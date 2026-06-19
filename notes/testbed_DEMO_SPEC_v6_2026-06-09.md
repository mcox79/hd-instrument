# Demo SPEC v6: substrate-around-LLM, two-stage story

**Author:** Testbed  **Date:** 2026-06-09 evening
**Supersedes:** Demo SPEC v5 (cycle-187 framing); incorporates Research's STRATEGIC_REFRAME (substrate-around-LLM) + PATH_3_PARALLEL_DECISION + V2_DEMO_RESULTS_HANDOFF (Exp-Dev) + cycle 211 RECOVERY (PP-229..PP-238)

## North star

Goal: a deployed system that EMPIRICALLY exceeds LLMs of relative size in clear measurable ways. Substrate IS the AI; LLM is a vendor-swappable language tool called when needed.

## v1 today vs v2 production: two-stage demo positioning

### v1 today (live as of 2026-06-09)

What works empirically right now:

- **Substrate at 1M+ facts**: Wikipedia 184K + ConceptNet 458K + arXiv 234K + PubMed 99K = 976K facts pre-encoded via bge-large + pre-fit substrate state. /converse confidence 0.68, latency 327ms, audit chain Merkle-verified per response.
- **Wikidata 50M ingest in flight**: REC-3 semantic-property filter; ~137K triples landed; ETA ~95 hr at 25 facts/sec.
- **PP-228 audit chain reproducible**: every /converse response carries a Merkle hash chain that lets any auditor verify the substrate sources used.
- **Cycle 211 categorical wins now visible**:
  - PP-229 GDPR exact erasure 0 / 0 false-retentions/losses at 0.058 ms
  - PP-230 multi-tenant T=50 isolation cross-leak 0.001
  - PP-231 5-of-6 substrate primitives composing without interference
  - PP-237 + PP-238 FB15K-237 first public benchmark win (Hits@1 = 0.956, MRR = 0.974)
- **Verticals shipped**: /demo/legal /demo/healthcare /demo/finance /demo/fda with regulatory-aligned capability claims.

What the v1 demo claim is:
- "Substrate IS the LLM's persistent, swappable, audit-grade knowledge layer; substrate-direct queries answer in sub-ms with cryptographic provenance."
- "Public-benchmarkable: substrate-native FB15K-237 Hits@1 = 0.956 / MRR = 0.974 without KGE training."

### v2 production (target: 1-2 weeks post Stage A + Stage B substrate-library re-encode)

What lands in v2:

- **Stage A: Wikidata 50M filtered semantic facts** ingested + loaded → substrate at ~11M facts.
- **Stage B: FHRR-native substrate library** (REC-1..REC-6 wired): per-predicate sharded codebook + 1-bit quantization → 20-50x storage savings at the same recall.
- **Stage C: facts.jsonl → FHRR re-encode** for Wikidata + (optional) other sources; PP-225 + PP-226 acceptance gates verify.
- **B1 PP-225 linear projection head wired into /converse**: substrate-retrieved facts project into LLM logit space at heldout-recall 1.000 (per cycle 207 fp32 lock at Pythia-1.4B / Qwen-1.5B).
- **B2 Path A every-layer Flamingo toggle**: backend exposes substrate-on vs substrate-off mode; 28% perplexity improvement empirically visible on demo.
- **B3 HYBRID composed model**: Path A + PP-225 in one frozen model (PP-227 lm_ratio = 0.797 / fact_recall = 1.000 at 10K KB; cycle 207 scaleup).

What the v2 demo claim becomes:
- "Substrate IMPROVES the LLM (28% perplexity reduction; Path A every-layer Flamingo) AND SUPPLIES its knowledge (heldout-recall 1.000 across KBs from 1K to 50K facts) AT THE SAME TIME, in one frozen model."
- "Substrate at 11M facts in <10 GB of state; categorical compliance moats (GDPR Art.17 exact erasure; multi-tenant T=50 isolation; reproducible Merkle audit per response)."

## v1 demo surface (live)

| URL | What | Empirical anchor |
|---|---|---|
| `/` | Landing widget / Tier-5a ask-the-substrate input box | bge-large + Qwen-1.5B-Instruct |
| `/chat` | Substrate-first chat (substrate intent → substrate retrieval → optional LLM) | PP-187/195/198 cascade |
| `/converse` | Programmatic substrate cascade (intent-route → substrate-direct OR substrate-augmented LLM) | PP-225-ready |
| `/playground` | Interactive primitives (AND / NOT / COUNT / counterfactual) | PP-* primitive proofs |
| `/benchmark` | Static benchmark response gallery | curated benchmark_responses.json |
| `/benchmark/fb15k-237` | FB15K-237 first public benchmark win (PP-237/238) | cap_map v545 commit 2aed0634 |
| `/demo` | Decisive test (substrate vs bare-LLM side-by-side) | PP-228 audit chain |
| `/demo/legal` | PACER substrate (PP-208 99.9% docket recall; PP-229 erasure; PP-237 multi-hop) | cycle 200 + cycle 211 |
| `/demo/healthcare` | DDI substrate (PP-209 100% DDI accuracy; PP-186 HIPAA PII; PP-229 erasure; PP-230 T=50 isolation) | cycle 200 + cycle 211 |
| `/demo/finance` | SEC 10-K substrate (PP-211 100% extraction; PP-237/238 multi-hop benchmark) | cycle 200 + cycle 211 |
| `/demo/fda` | FDA audit substrate (PP-210 100% audit; PP-229 21 CFR Part 11; PP-231 composite preservation) | cycle 200 + cycle 211 |

## v2 demo surface (planned)

Additions when Stage A + B1/B2/B3 land:

| URL | What | Anchor |
|---|---|---|
| `/converse?mode=substrate_only` | Substrate-only mode (no LLM call) | PP-187 templated |
| `/converse?mode=substrate_with_pp225` | PP-225 projection mode | PP-225 cycle 207 fp32 |
| `/converse?mode=substrate_with_patha` | Path A Flamingo toggle | PP-227 every-layer |
| `/converse?mode=hybrid` | HYBRID composed model | PP-227 hybrid 10K |
| `/demo/wikidata` | Wikidata 11M substrate explorer | Stage A + Stage C completion |
| `/benchmark/path-a-perplexity` | Path A 28% perplexity claim live | PP-227 every-layer 3-seed |

## Strategic anchors (NORTH_STAR_FUNCTIONAL_SYSTEM_BEATS_LLMS)

Three substantive empirical claims visible in v2 demo:

1. **Substrate IS the LLM's persistent knowledge.** PP-225 projection head heldout=1.000; substrate KB swappable with no LLM retraining.
2. **Substrate IMPROVES LLM perplexity.** PATH A every-layer Flamingo 28% perplexity reduction on Pythia-160M; cross-family on Pythia-1.4B + Qwen-3B 4-bit.
3. **Substrate provides cryptographic compliance.** PP-228 audit chain per response; PP-229 GDPR exact erasure; PP-230 multi-tenant isolation; reproducible bit-exactly.

Plus the categorical compliance moats:
- GDPR Article 17 right-to-erasure (algebraic, not logging-suppress)
- EU AI Act Article 12 audit trail (Merkle-verified)
- SOC 2 CC6.1 tenant isolation (algebraic per-tenant W)
- 21 CFR Part 11 data integrity (reproducible retrieval)
- HIPAA 164.312 access control (per-tenant + per-fact)

## Release sequencing

### Tonight done
- [x] A1 verticals (4 pages anchored on cycle-200 vertical proofs)
- [x] Cycle-211 capability updates in verticals (PP-229/230/231/237/238)
- [x] /benchmark/fb15k-237 page (substrate numbers only; KGE baselines deferred until citation-grade)
- [x] E2 batch_size 128→256 (for future Stage A runs)
- [x] Faulthandler at backend startup (auto-diagnose future segfaults)
- [x] Demo SPEC v6 (this doc)

### Tomorrow (per Research priority ranking)
- [ ] B1 PP-225 projection head wiring (blocked on Exp-Dev checkpoint; request filed)
- [ ] B4 incremental: hero-card update on landing widget to surface cycle 211 wins (small)

### Day 2-3
- [ ] B2 Path A toggle (substrate-on vs substrate-off perplexity demo)
- [ ] B3 HYBRID composed backend (Path A + PP-225 in one frozen model)

### Day 4
- [ ] Stage A completes → re-prefit + load Wikidata into backend
- [ ] Stage C re-encode through FHRR substrate library
- [ ] Build SQLite label cache
- [ ] File `exp_dev_handoff_research_stage_c_verify` for PP-225 + PP-226 acceptance gates

### Day 5+
- [ ] C2 Wikipedia-loaded-twice dedup cleanup (cosmetic; user-noticeable)
- [ ] E1 bge-large GPU offload (coordinate with Exp-Dev's GPU lane)
- [ ] D1-D3 new ingest sources (Wikipedia 1M / Common Crawl / PubMed 30M)

## What v2.0 demo looks like end-to-end

```
User: "What's the structure of caffeine?"
  Intent: lookup_factual
  Substrate-direct: PP-187 templated; 23 ms
  Audit: Merkle hash; PP-228 reproduces
  Response: returns molecular structure facts; LLM not invoked

User: "Compare to theobromine"
  Intent: comparison_factual
  Substrate-with-pp225: retrieve both facts; project into Qwen logits
  PP-225 head: heldout=1.000 (cycle 207 fp32 lock)
  Latency: 320 ms (Qwen generation; substrate retrieval <1ms)
  Audit: Merkle chain reproduces

User: <toggle "substrate-on" off>
  /converse?mode=substrate_off
  Demonstrates 28% perplexity hit on identical query
  Path A claim visible empirically

User: "Forget that I asked about caffeine"
  Substrate: PP-229 GDPR exact erasure
  Latency: 0.058 ms
  Audit: deletion-certificate; bit-exact retrievability check
  Response: confirms erasure; physics-grade-not-policy-grade
```

Vertical landing pages map this to 4 regulated industries:
- Legal: PACER docket recall + Loper Bright ruling lookups + sealed-record erasure
- Healthcare: DDI lookups + paroxetine pregnancy contraindication + retracted-record erasure
- Finance: SEC 10-K revenue extraction + multi-hop cross-company segment aggregation
- FDA: trial protocol lookups + AE listing + 21 CFR Part 11 reproducibility

## Why this matters (one paragraph)

Substrate is not a vector DB. Substrate is the AI's knowledge layer with three categorical properties that change what a "knowledge layer" means: deterministic retrieval at substrate-grade scale (FB15K-237 0.956 Hits@1); algebraic compliance primitives (GDPR exact erasure; multi-tenant isolation; reproducible Merkle audit); composable with the LLM (Path A 28% perplexity; PP-225 heldout 1.000). Each property is empirically grounded in a numbered PP-* row in cap_map, and each shows up in the v1 demo today (verticals + benchmark page + /converse) or the v2 demo over the next 4 days (PP-225 wire-up + Path A toggle + HYBRID).

## Cross-references
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- V2 demo results handoff: notes/exp_dev_to_testbed_V2_DEMO_RESULTS_HANDOFF_2026-06-09.md
- Path 3 parallel decision: notes/research_to_testbed_PATH_3_PARALLEL_DECISION_2026-06-09.md
- Priority ranking: notes/research_to_testbed_PRIORITY_RANKING_2026-06-09.md
- Cycle 207: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- Cycle 211 RECOVERY: notes/orchestrator_to_research_VERDICT_HANDLER_HAIKU_BUG_2026-06-09.md
- KILL_LOAD_PROFILE_PREFIT: notes/research_to_testbed_KILL_LOAD_PROFILE_PREFIT_2026-06-09.md
- BACKEND_GREENLIGHT_AND_MONITOR: notes/research_to_testbed_BACKEND_GREENLIGHT_AND_MONITOR_2026-06-09.md
- Demo SPEC v5 (superseded): notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md
