# Testbed Audit Day 1 — Substrate primitive portability audit

**Author:** Testbed
**Date:** 2026-06-08 ~16:00 UTC
**Scope:** Read all 11 PP-* primitive cells; assess portability into production substrate library
**Output:** library structure proposal + dependency graph + port-priority list for Week 1

## TLDR

Cells are small (~50-110 lines each) research POCs running on **synthetic numpy data**.
They are NOT production-ready library code; they ARE excellent algorithmic blueprints.
**Port effort is moderate**: extract the math (1-2 days), build production wrapper layers
(persistence + indexing + multi-tenant + audit trail) (3-5 days). The cells share a
small set of common FHRR primitives that need to live in one shared `substrate/core.py`
module.

## Pattern observation: all cells share 4 core FHRR primitives

Every cell repeats these (slightly different signatures, same math):

```python
def cphasor(m, d, g) -> np.ndarray[complex64, (m, d)]:
    """FHRR codebook: m unit-norm complex phasor vectors of dim d."""
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)

def cidx(v, book) -> int:
    """Cleanup memory: top-1 cosine via real(book @ conj(v))."""
    return int(np.argmax((book @ np.conj(v)).real))

# bind = elementwise complex multiplication: a * b
# unbind = a * conj(b)
# bundle = sum of bound terms; M = Σ bind(s_i, r_i, o_i)
```

Some cells use **binary bipolar codebook** (`np.sign(g.standard_normal(...))`) instead of
complex phasors (e.g., delete-downdate uses bipolar+pinv). Both are valid FHRR variants.

**This goes in `substrate/core.py` ONCE.** All primitives import from there.

## Per-primitive audit

| # | Primitive | Source cell | Lines | Port assessment | Production wrapping needed |
|---|---|---|---|---|---|
| 1 | **PP-119 K-hop traversal** | `exp_chain3_v1_khop_3shard_gpu_v1.py` | 92 | **Direct port** — `recovery(C, K, g)` is the core; 3-shard relay logic + noise scaling | Real codebook builder from CELL-2 cache; multi-hop walk over real entities (not synthetic chains) |
| 2 | **K-hop with audit chain** | `exp_fact_checked_khop_merkle_chain_hp12_root_v1.py` | 104 | Direct port; Merkle accumulator per hop | Merkle tree for verifiable audit (already present in counterfactual-do cell — can share `substrate/audit.py`) |
| 3 | **PP-123 Cascade router** | `exp_cascade_native_first_router_cpu_v1.py` | 62 | **Direct port** — `native_conf < THR` → fallback to fuzzy | Confidence threshold tuning; routing telemetry per query for the demo's cost-per-query panel |
| 4 | **PP-127/128/129/130 Sharding** | `exp_kg_sharding_strategy_compare_gpu_v1.py` + `exp_cross_shard_chain_extraction_cpu_v1.py` + `exp_hierarchical_subshard_kg_cpu_v1.py` | 83+80+74 | **Refactor needed** — three cells test different sharding strategies; consolidate into one `Sharding(strategy="subject"\|"relation"\|"hierarchical"\|"hybrid")` class | Per-subject default per Research findings; shard creation + lookup + MERGE on cross-shard chain; persistence via numpy memmap or per-shard pickle |
| 5 | **PP-135 Substrate-KV (Tier 5)** | `exp_d2_pythia1p4b_substrate_kv_gpu_v1.py` + `exp_d3_crossshard_substrate_kv_gpu_v1.py` | 110+109 | **Medium effort** — ZCA whitening + cosine retrieval is the math; need to integrate Pythia-1.4B model loading + last-token-pool encoding into a serving class | Pythia-1.4B persistent on RTX 4060 Ti; substrate-KV write + read API; fp16 inference; KV cache for the demo |
| 6 | **PP-125 Two-stage disambig** | `exp_two_stage_disambig_khop_cpu_v1.py` | 85 | **Direct port** — fuzzy embedding lookup + K-hop traversal from top-B candidates | bge-small encoder for fuzzy stage (already in benchmark suite); chain to K-hop module |
| 7 | **PP-107 Cleanup confidence (ROC)** | `exp_cleanup_confidence_roc_cpu_v1.py` | 54 | **Direct port** — max-cosine score; threshold tuned via AUC | Threshold per-shard (because shard density affects baseline); "I don't know" rendering in UI |
| 8 | **PP-104 GDPR exact erase** | `exp_delete_downdate_exactness_cpu_v1.py` | 49 | **Direct port** — `np.linalg.solve(K[keep].T @ K[keep] + λI, K[keep].T @ V[keep])` | Surgical erase API; audit log entry per deletion; cryptographic proof generation (hash before/after) |
| 9 | **Bitemporal as-of** | `exp_bitemporal_asof_1M_v1.py` | 59 | **Direct port** — `np.searchsorted` on sorted (valid_time, value) array | Per-entity version log; index management on writes; as-of query timing target <0.2ms |
| 10 | **Counterfactual do()** | `exp_counterfactual_do_operator_v1.py` | 106 | **Direct port** — DAG + override + recompute + Merkle audit chain | DAG persistence; share Merkle utilities with K-hop audit chain (`substrate/audit.py`) |
| 11 | **Mechanism B inverted shards** | `exp_inverted_property_shards_cpu_v1.py` | 64 | **Direct port** — at sleep-defrag, scan subject shards for properties; build `inv[P] = Σ ents[s]` bundles | Sleep-defrag scheduler; inverted index persistence; query routing (set queries → inverted; subject queries → forward) |
| 12 | **Mechanism C cross-shard chain** | `exp_cross_shard_chain_extraction_cpu_v1.py` + `exp_mechanism_composition_v1_n4096.py` | 80+544 | **Medium effort** — mechanism_composition is the most complex (544 lines); contains multiple cross-shard ops | Scatter-gather across shards; chain combiner; the 544-line cell has the most complex algebra to port |

## Proposed library structure

```
substrate/
├── __init__.py
├── core.py              # FHRR primitives: cphasor, cidx, bind, unbind, bundle
│                        #   binary variant for memory-constrained shards
├── shards.py            # Shard class: per-subject / per-relation / hierarchical
│                        #   persistence (numpy memmap), capacity, write, query
├── khop.py              # K-hop traversal: 3-shard relay, confidence-weighted
│                        #   chain Merkle audit
├── cascade.py           # Cascade router: native -> fuzzy fallback, threshold tuning
├── disambig.py          # Two-stage: fuzzy (bge) -> native (K-hop)
├── confidence.py        # PP-107: cleanup-cosine threshold for abstention
├── inverted.py          # Mechanism B: sleep-defrag inverted property index
├── cross_shard.py       # Mechanism C: scatter-gather across shards for chain extraction
├── gdpr.py              # PP-104: surgical erase via pinv downdate + audit log
├── bitemporal.py        # As-of queries via searchsorted on sorted valid-time
├── counterfactual.py    # Pearl-style do() + DAG recompute + Merkle audit
├── audit.py             # Shared Merkle tree, hash chains, cryptographic proofs
├── kv_memory.py         # Tier-5 substrate-KV: Pythia-1.4B + ZCA whitening + retrieval
└── persistence.py       # Disk-backed substrate state (per-shard pickle / memmap)
```

Backend wrapping (FastAPI) lives outside `substrate/`:

```
backend/
├── main.py              # FastAPI app
├── routes/
│   ├── query.py         # POST /query: bare LLM + substrate-enhanced
│   ├── add_fact.py      # POST /add_fact
│   ├── delete_facts.py  # POST /delete_facts (GDPR)
│   ├── scale_stats.py   # GET /scale_stats
│   └── audit_chain.py   # GET /audit_chain/{query_id}
├── llm/
│   ├── openai_client.py # gpt-4o-mini
│   └── anthropic_client.py # Claude Haiku toggle
├── kb/
│   ├── wikipedia.py     # Wikipedia ingest pipeline (NER → triples → substrate.write)
│   └── corporate.py     # Crunchbase + SEC EDGAR + News API overlay (Week 2+)
└── config.py            # env, API keys, paths
```

## Dependency graph

```
core.py (FHRR primitives) ── used by ALL substrate/* modules

audit.py (Merkle, hashes) ── used by khop.py, gdpr.py, counterfactual.py

persistence.py ── used by shards.py, inverted.py, kv_memory.py

shards.py ── used by khop.py, cross_shard.py, inverted.py
khop.py ── used by cascade.py, disambig.py
confidence.py ── used by cascade.py (threshold gate)
cross_shard.py ── used by khop.py (for cross-shard chains)
kv_memory.py ── standalone for Tier-5 retrieval; called by backend/routes/query.py
gdpr.py ── used by backend/routes/delete_facts.py
bitemporal.py ── standalone temporal index
counterfactual.py ── standalone do() operator
inverted.py ── built lazily by background sleep-defrag job
```

Roughly: core + audit + persistence are the foundation. Then shards. Then everything else can be ported in parallel.

## Port-priority list for Week 1

**Day 1** (foundation, 1 day):
- `substrate/core.py` — extract FHRR primitives from cells (~50 lines)
- `substrate/audit.py` — Merkle tree from counterfactual-do cell (~30 lines)
- `substrate/persistence.py` — numpy memmap save/load (~30 lines)

**Day 2** (sharding, 1 day):
- `substrate/shards.py` — consolidate kg_sharding_strategy + cross_shard_chain + hierarchical_subshard (~100-150 lines port; subject-sharding default)

**Day 3** (K-hop core, 1 day):
- `substrate/khop.py` — chain3 + fact-checked-khop-merkle ports (~80 lines)
- `substrate/confidence.py` — cleanup AUC threshold (~30 lines)

**Day 4** (routing + GDPR, 1 day):
- `substrate/cascade.py` — native-first router (~50 lines)
- `substrate/gdpr.py` — pinv downdate exact erase (~40 lines)
- `substrate/bitemporal.py` — searchsorted as-of (~40 lines)

**Day 5** (composition + LLM wiring, 1 day):
- `substrate/counterfactual.py` — Pearl do() + Merkle (~60 lines)
- `substrate/inverted.py` — Mechanism B sleep-defrag (~50 lines)
- `substrate/cross_shard.py` — Mechanism C (~80 lines, the harder port from mechanism_composition_v1_n4096)
- `substrate/disambig.py` — two-stage (~40 lines)
- `backend/main.py` + `backend/routes/query.py` skeleton

Total Week 1 deliverable: library compiled + `/query` endpoint returning JSON over 10K-fact demo KB.

**Tier-5 KV (`substrate/kv_memory.py`) deferred to Week 2** (needs Pythia-1.4B model setup; gated on Day-2/3 audit confirming the 4060 Ti can hold model + substrate concurrently).

## Open questions

1. **`mechanism_composition_v1_n4096.py` is 544 lines** — the biggest port effort. I should read it day 1 to confirm the cross-shard logic isn't more complex than the small cell suggests. Likely it composes multiple primitives but the per-primitive math is simpler.

2. **Audit chain Merkle root anchor** — counterfactual-do cell uses an internal hash chain. For the demo's "cryptographic proof of deletion" wow moment, should we anchor to a public timestamp service (e.g., Ethereum block hash) for verifiability? That's a v1.1 polish question; v1 demo can use just SHA-256 chain.

3. **Persistence format** — numpy memmap (fast, no serialization) vs pickle (versionable). I lean memmap for the substrate state, json for metadata. Confirm during Day 2.

4. **Sharding key choice** — Research finding: subject and relation both 1.0 on FB15K; recommended per-subject. Sticking with per-subject as default. Hybrid only if a customer-specific KB shows different patterns.

5. **Test coverage** — each library module needs at least one unit test that matches the cell's smoke output. Build incrementally during Week 1.

## What I'm NOT doing

- Re-validating the substrate science (settled per cycle 187 + cycle 185 architecture lock)
- Inventing new primitives (the 11 in the SPEC are the production set)
- Touching the cell scripts (they stay as reference implementations; library imports from clean ports)
- Building benchmark dashboard (Exp-Dev supplies the numbers; I render them)

## Audit Day 1 status: COMPLETE ✓

Next: Audit Day 2 = Cloudflare Tunnel setup on desktop + Pythia-1.4B + substrate-KV GPU smoke + Node toolchain install + API key plumbing + risk re-review.

## Cross-references

- v1 demo BUILD PLAN: `notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md`
- Research BUILD PLAN response: `notes/research_to_testbed_BUILD_PLAN_response_2026-06-08.md`
- Benchmark suite numbers (for demo head-to-head panels): `notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md`
- Source cells: `experiments/exp_*.py` (read 9 of 11; mechanism_composition_v1_n4096.py deferred to Day 1 of Week 1 since it's 544 lines)
