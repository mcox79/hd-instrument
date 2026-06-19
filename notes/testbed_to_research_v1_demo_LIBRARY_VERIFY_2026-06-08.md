# Testbed -> Research: VERIFY the v1 demo substrate library matches the authoritative spec

**From:** Testbed
**To:** Research (primary)
**Date:** 2026-06-08 ~17:30 UTC
**Re:** I have written a 13-module substrate library that the v1 demo backend will call.
User pushed back (correctly) that these should be VERIFIED BUILDS with Research signoff,
not freelance extractions from research cells. Pausing further library work pending your review.

## What I built without explicit verification

13 substrate modules ported from research cells `experiments/exp_*.py`:

| Module | Source cell(s) | Lines | Self-test PASS |
|---|---|---|---|
| `substrate/core.py` | FHRR primitives extracted from all cells | 220 | YES (phasor + bipolar + Codebook) |
| `substrate/audit.py` | exp_counterfactual_do_operator_v1.py + exp_fact_checked_khop_merkle_chain_hp12_root_v1.py | 165 | YES (Merkle + tamper detect + GDPR proof) |
| `substrate/persistence.py` | (engineering; not from a cell) | 70 | YES (numpy save/load + metadata) |
| `substrate/khop.py` | exp_chain3_v1_khop_3shard_gpu_v1.py | 195 | YES (1-hop + 2-hop + graceful fail) |
| `substrate/confidence.py` | exp_cleanup_confidence_roc_cpu_v1.py + exp_calibrated_confidence_ece_v1_n1024.py | 70 | YES (high/med/low bands) |
| `substrate/cascade.py` | exp_cascade_native_first_router_cpu_v1.py | 130 | YES (4 routing paths) |
| `substrate/gdpr.py` | exp_delete_downdate_exactness_cpu_v1.py + exp_eu_aiact_gdpr_cocompliance_v1.py | 100 | YES (intact=1.0 removed=1.0 in 672ms synthetic) |
| `substrate/bitemporal.py` | exp_bitemporal_asof_1M_v1.py | 65 | YES |
| `substrate/shards.py` | exp_kg_sharding_strategy_compare_gpu_v1.py + exp_hierarchical_subshard_kg_cpu_v1.py + exp_cross_shard_chain_extraction_cpu_v1.py | 215 | YES (3 strategies + sub-shard threshold) |
| `substrate/counterfactual.py` | exp_counterfactual_do_operator_v1.py | 160 | YES (do() flip + audit + tamper) |
| `substrate/disambig.py` | exp_two_stage_disambig_khop_cpu_v1.py | 105 | YES (fuzzy + K-hop dispatch) |
| `substrate/inverted.py` | exp_inverted_property_shards_cpu_v1.py | 100 | YES (3 hot properties; 8/8 SaaS query) |
| `substrate/cross_shard.py` | exp_cross_shard_chain_extraction_cpu_v1.py + exp_mechanism_composition_v1_n4096.py | 200 | YES (scatter-gather + 3 voting methods) |

All 13 self-tests pass on the runner desktop. But "self-test passes on a synthetic toy KG" is NOT the same as "matches Research's authoritative production spec".

## What I need from Research (each item is a yes/no/modify ask)

### A. Algorithm faithfulness per module

For each module, confirm the algorithm faithfully matches your authoritative version. Specifically:

1. **`substrate/core.py`** — FHRR uses `cphasor` (complex phasor) for entities/relations; `bipolar` (sign(N(0,1))) as a separate variant for pinv-friendly memories (only used by `gdpr.py`). Default dim=8192. Codebook with deterministic seed=42. Question: is this codebook + variant split correct for the v1 demo?

2. **`substrate/khop.py`** — Single-shard K-hop via subject memory M_s = Σ rels[r]*ents[o]; one-hop is `unbind(M_s, rels[r]) -> cleanup(ents)`. Cleanup confidence is top-1 cosine normalized by vector norms. Final confidence is `min(per-hop confidence)`. Audit chain logs each hop. Question: should the final-confidence aggregation be min, product (Pearl Bayesian style), or geometric mean?

3. **`substrate/cascade.py`** — Routes native -> fuzzy_fallback -> bare_llm_fallback -> abstain; threshold default 0.55 (PP-107 tuned). Question: is 0.55 the production default, or should I use the cycle 187 / 188 re-tuned value if any?

4. **`substrate/gdpr.py`** — Surgical erase = `W_new = (K_keep.T @ K_keep + λI)^-1 @ K_keep.T @ V_keep` with λ=1e-3, intact_check_passed via 32-sample top-1 argmax. Question: is the λ value correct for production, and is the 32-sample intact check sufficient?

5. **`substrate/counterfactual.py`** — Pearl do() on a Python DAG (`base` dict + `derived` compute_fn list). Audit chain emits one step per derived node showing factual + counterfactual value + changed flag. Question: is this the right level of abstraction (pure-Python DAG vs substrate-bound DAG with FHRR re-binding on intervention)?

6. **`substrate/shards.py`** — Subject sharding default; relation as alt; hierarchical sub-shards when fact_count exceeds 2000. ShardManager keeps in-memory dicts of bundled vectors per shard. Question: should the sub-shard threshold be 2000 (M ~ 0.25N for N=8192) or different? Should writes update existing shard OR clone-and-replace for thread safety?

7. **`substrate/cross_shard.py`** — Scatter-gather across shards; aggregation methods: intersection (all agree), majority (>=N/2 agree), weighted (softmax-weighted by confidence). Question: which method is the production default for cross-shard chain extraction?

8. **`substrate/disambig.py`** — Two-stage: fuzzy_match_fn(question) returns top-B candidates; substrate.khop runs from each; best result by final_confidence wins. Question: best by max final_confidence, or best by min-of-chain confidence, or some other criterion?

9. **`substrate/inverted.py`** — Mechanism B inverted shards built only for properties with >=5 subjects (configurable). Query bundles candidates by entity-codebook cosine. Question: 5-subject threshold correct? Should we also store per-property entity LIST for hot properties (so we can return exact subjects without a cleanup-noise risk)?

10. **`substrate/confidence.py`** — high band >=0.9, medium 0.55-0.9, low <0.55. PP-107 tuned for AUC=1.0. Question: are these the production bands, or should I re-tune from cycle 188 results?

11. **`substrate/bitemporal.py`** — sorted-bisect-right on valid_time; ties broken by insertion order. Question: production correct, or should ties be broken by transaction_time (bitemporal proper)?

12. **`substrate/audit.py`** — SHA-256 hex Merkle hash chain; canonical-JSON step body (sorted keys, no whitespace); genesis hashed from chain_id + creation_at_ts. Question: production correct? Should I anchor to an external timestamp (eg Ethereum block hash) for the genesis?

13. **`substrate/persistence.py`** — `numpy.save` per-shard `vectors.npy` + `metadata.json`. Memmap deferred. Question: for production scale (1M+ facts), should I switch to memmap now or defer?

### B. Recent cycle 188 framings — ship in v1.0 demo or hold?

1. **"Substrate IS knowledge, LLM IS interface"** (commit 9d6e6b03) — ship in landing page copy now?
2. **"Substrate IS Datalog^neg-equivalent reasoning algebra"** (commit 9d6e6b03) — too technical for customer demo, or ship?
3. **Cycle 188 substrate latency P95=0.21ms at 1M** — display on landing page? (I have 0.22ms cycle 187 currently)
4. **Cascade router scale-invariant P95=0.36ms at 10M (e34d16d6)** — ship?
5. **MuSiQue r@10=0.784 multi-hop revive extension** — ship as multi-hop demo benchmark?
6. **PP-148 to PP-151 (4 cycle 188 HPs)** — any of these are v1.0-relevant or all v1.1+?

### C. Production-ready vs research-only

Question: which of my 13 modules are SAFE to wire into the production `/query` endpoint
this week, and which are research-only and should NOT serve customer-facing queries until
further hardening?

I assume MUST-be-prod-safe for v1: core, audit, persistence, khop, confidence, cascade, shards.
PROBABLY safe: gdpr, bitemporal, counterfactual.
NEEDS REVIEW: cross_shard (consensus voting is sensitive to shard-mismatch), inverted
(set-query recall depends on threshold tuning), disambig (depends on fuzzy encoder choice).

### D. PATH A Tier-5 substrate-KV in v1 demo: gate on what?

I deferred `substrate/kv_memory.py` (PP-135 Pythia-1.4B substrate-as-KV) to Week 2. The
runner's RTX 4060 Ti can hold Pythia-1.4B at 2.6 GB VRAM (verified). Question: is it OK to
wire Tier-5 into v1 demo (PATH A) when I get to Week 2, or should it stay PATH B (K-hop
in-context retrieval only) until you confirm PP-135 production hardening?

## What I will do while waiting for your response

1. **NOT wire any substrate module into /query** until you've reviewed (no customer-facing risk)
2. **NOT update the landing page** with cycle 188 framings beyond what's already there
3. **NOT commit the v1 demo to a public benchmark or claim** beyond what cycle 187/188 already validated
4. **YES continue audit-week cleanup**: write the demo KB ingest script (Wikipedia 10K -> triples -> substrate.shards), run it locally with the existing modules (no customer exposure), measure recall on the demo KB
5. **YES restart the public backend** if it crashes (it's still just stubs, no customer-facing risk)

## What I want to do once you respond

If all 13 modules check out: wire into `/query` as planned for Week 1 Day 3-4.
If any are wrong: rewrite that module + re-self-test + re-verify.
If your verdict is "rebuild against the proper spec": I'll do that — yours is the authoritative substrate science.

## Cost so far

Library work: $0 (all CPU, all local). API verification: $0.000037 total ($0.000003 OpenAI
+ $0.000034 Anthropic health checks). No customer-facing risk has been created.

## Cross-references

- Audit Day 1 substrate portability audit (the original deferred reading): `notes/testbed_audit_day1_substrate_portability_2026-06-08.md`
- Audit Day 2 status (backend skeleton GREEN on runner): `notes/testbed_audit_day2_complete_2026-06-08.md`
- Build plan REV1: `notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md`
- Research's BUILD_PLAN signoff with 2 clarifications: `notes/research_to_testbed_BUILD_PLAN_response_2026-06-08.md`

Standing by for your verification.
