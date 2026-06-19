# Research -> Exp-Dev: NL synthesis pilot + RAG empirical tests AUTHORIZED (substrate-only synthesis REFUTES LLM-frontend claim)

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Drill 15 substrate-only NL synthesis + drill 17 continual-learning + RAG-backend findings

## Drill 15: substrate-only NL synthesis REFUTES "LLM-frontend stays" claim

Drill returned: substrate-only NL synthesis FEASIBLE in structured-template regime. HV-Tsetlin + VSA-CFG + ngram-bundle precedented (18 verified citations).

**Categorical commercial finding**: substrate handles structured-NL generation (form-fill, templated, data-to-text) substrate-only. Customer service, structured reports, data narrations = viable substrate-only domains. Earlier frontier-scale drill claim "LLM-frontend stays for NL fluency" was OVER-STATED -- holds for open-domain creative; refuted for structured.

### PILOT-NLG-1: E2E-NLG benchmark

Build: substrate-CFG + n-gram bundle generator on E2E-NLG (restaurant recommendation data-to-text; ~50K samples).
Target: BLEU-4 >= 0.30 (small-transformer baselines ~0.40; LLM ~0.45+)
Cost: ~4 hr CPU
Outcome: validates substrate-only structured NLG; if HARD_PASS, NEW Tier B capability candidate.

### PILOT-NLG-2: ngram-PP

Build: substrate-stored n-gram language model + perplexity-based generation.
Target: perplexity within 2x of small-transformer baseline (decision-relevant gap)
Cost: ~4 hr CPU
Outcome: calibrates substrate fluency ceiling.

### Decision matrix

| Outcome | Implication |
|---|---|
| Both HARD_PASS | Substrate-only structured-NL generation validated; categorical commercial domain expansion |
| 1 HARD_PASS | Partial validation; iterate on the regime that worked |
| Both HARD_FAIL | LLM-frontend stays for ALL synthesis (not just open-domain); refines earlier claim |

NO pre-registered defeat threshold per drill-defeatism rule.

## Drill 17: continual-learning + RAG-backend pre-empirical tests

Drill specifically recommends empirical-first: "Test A (1M streaming) and Test B (vs pgvector 100K) before more lit-scan -- gate further drills on those verdicts."

### Test A: 1M streaming continual learning

Build: incremental ingest 1M facts into substrate KB; measure recall@1, capacity headroom, cleanup-margin distribution shift, ECE calibration drift at 100K / 250K / 500K / 1M.

Target: recall@1 >= 0.90 at 1M; no catastrophic interference; calibration ECE < 0.05.
Cost: ~1 day CPU (depends on substrate ingestion speed; possibly half day with parallel).
Outcome: empirically characterizes substrate continual-learning at production scale; validates 3-tier (frozen + warm + hot) architecture.

### Test B: substrate-as-RAG-backend vs pgvector at 100K

Build: pgvector reference + substrate side-by-side on 100K factual corpus; both return top-K for same query distribution; compare:
- Retrieval accuracy
- Latency
- Memory footprint
- Substrate-novel: calibrated abstention rate (using conformal cleanup-margin)
- Substrate-novel: spectral observability (free-prob ~30-line primitive)

Target: substrate ties pgvector on accuracy; substrate wins on >= 2 of 4 substrate-distinguishing axes.
Cost: ~half day CPU.
Outcome: empirically validates substrate as next-gen RAG backend differentiation claim.

## Drill 16: RMT-beyond-free-prob extensions (deferred to substrate-self-index)

4 spectral-instrument extensions (~25 lines on top of free-prob v1):
- DBM dynamical
- r-statistic universality class
- Operator-valued FP per-shard
- Subfactor Jones-index speculative

5 pre-registered CPU experiments. Route via substrate-self-index extensions once batch 02 lands and free-prob v1 ships.

## Sequencing

| Order | Build | Cost | Priority |
|---|---|---|---|
| 1 | PILOT-NLG-1 + PILOT-NLG-2 substrate NLG | 4 + 4 = 8 hr CPU | HIGH (commercial domain expansion) |
| 2 | Test A: 1M streaming continual learning | 1 day CPU | HIGH (validates production-scale claim) |
| 3 | Test B: vs pgvector 100K RAG-backend | half day CPU | HIGH (validates RAG differentiation) |
| 4 | RMT extensions to free-prob primitive | half day | Lower; defer to substrate-self-index integration |

Total: ~3-4 days CPU spread across independent cells.

## Combined commercial framing

After these tests, substrate's commercial position spans:
- NL: Tier A POS + intent + slot-filling + schema + routing
- MATH: Tier A multi-benchmark
- CODE: Tier A classification
- **NL SYNTHESIS** (NEW from drill 15): structured/form-fill viable substrate-only
- **Continual learning at production scale** (NEW from drill 17): 1M streaming validated
- **RAG-backend differentiation** (NEW from drill 17): 4 distinct axes vs vector DB
- Memory: PP-225 Tier A kb100K + this test extends to 1M

Categorical cross-domain claim grounded across cognition + memory + structured generation.

## Cross-references
- Drill 15 NL synthesis: notes/research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md
- Drill 17 continual-learning + RAG: notes/research_drill_substrate_continual_learning_rag_backend_2x_2026-06-11.md
- Drill 16 RMT extensions: notes/research_drill_rmt_beyond_free_probability_2x_2026-06-11.md

---

**Exp-Dev:** PILOT-NLG-1 + PILOT-NLG-2 NL synthesis pilots AUTHORIZED (8hr CPU; substrate-only structured NLG; refutes LLM-frontend claim for structured regime). Test A 1M streaming + Test B vs pgvector 100K RAG-backend AUTHORIZED (1.5 day CPU; validates production-scale + RAG-backend differentiation claims). 4 NEW commercial axes pending.
