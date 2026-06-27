# exp_dev hand-off — research: CORTEX Wave 1.6 (E-tensor fairness re-test + 4x alternatives in parallel)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** Cortex E-tensor harder-regime smoke 2026-06-26 18:43 HARD_FAIL. USER 2026-06-26 audit: "verify this test was fair. were the used atoms tagged enough? How many iterations before pruning?" — caught two specific fairness concerns. Also USER green-lit dispatching the other cortex 4x anchors in parallel.

**Source HARD_FAIL evidence:** `data/exp_cortex_E_tensor_HARDER_REGIME_v1_smoke/metrics.json`:
- E_GATED rec_old=0.500 (preserves 50% of old)
- RANDOM rec_old=0.717 (random pruning preserves MORE than E-gated)
- BASELINE_mag rec_old=0.800 (magnitude-based preserves MOST)
- gap_E_vs_RND = -0.217 (E_GATED worse than random by 21.7pp)
- cor(E, |W|) = 0.760 (E heavily correlated with magnitude — not independent signal)

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off and DO NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchor pointers only.

## Pivot frame (mandatory)

USER 2026-06-26 pivot in force: substrate has NO language understanding; compositional understanding track (Stage 3); text8 / BPC / bigram-gap NOT relevant evals. These cells exercise cortex content-extraction mechanisms; eval is RECALL on old + recent atoms + capacity-bounded over many continual-ingest cycles.

## Anchor candidates

### ANCHOR 1 (RE-TEST with USER-identified fairness fixes): cortex_E_tensor_RETEST_fairness_v2

- **Anchor pointer:** new cell extending `experiments/exp_cortex_E_tensor_HARDER_REGIME_v1.py` + modified `hdlab/excitability.py`
- **USER-identified fairness concerns to fix:**
  - **Fix A: explicit retrieval pattern during consolidation phase.** Current test may not retrieve old atoms during cycles → E score stays at initial value → E-gated pruning prunes them all → looks like mechanism failure but is test-design artifact. Fix: structured retrieval schedule where some old atoms get N retrievals over cycles, some get 0; pre-reg requires E_GATED preserves retrieved-old atoms ≥ 90% AND prunes unretrieved-old atoms with the same rate as RANDOM. Tests whether E ACTUALLY differentiates retrieved vs unretrieved.
  - **Fix B: decouple EWMA bump from cosine magnitude.** cor(E, |W|) = 0.76 in v1 smoke. Suspicion: EWMA update is scaled by cosine match score, which is proportional to |W|. Then E just tracks |W|, carrying no new info. Fix: bump E by CONSTANT amount per retrieval hit (e.g. +1.0 per hit, regardless of cosine score); decay E by constant rate per cycle. Pre-reg requires final cor(E, |W|) < 0.3 (E independent of magnitude). If still > 0.5, the EWMA design is fundamentally wrong-shaped and we need a different importance signal.
- **Tier hint:** MIDDLE_BAND expected; chain-grade-eligible IF Fix A passes (E differentiates retrieved/unretrieved old atoms) AND Fix B passes (cor(E,|W|) < 0.3) AND ARM_E_GATED preserves retrieved-old > 90% AND prunes unretrieved-old similarly to RANDOM.
- **Pre-reg HARD_FAIL bands:** E still indistinguishable from RANDOM on retrieved-old atoms — mechanism truly refuted (route to research for alternative selectivity signals).
- **Arms (4 mandatory):**
  - ARM_BASELINE_NO_DOWNSCALE (rail; same as v1)
  - ARM_E_GATED_RETEST (Fix A + Fix B applied)
  - ARM_RANDOM_GATED (control; same as v1)
  - ARM_BASELINE_MAG_GATED (control; rules out "magnitude is the right signal after all")
- **Cost:** ~3-5 hr local_cpu (3 seeds)
- **Queue:** remote_cpu_queue (route via hdi_orchestrator; per USER 2026-06-26 routing-correction — remote queues have been idle)
- **Dependency:** spawn budget freedom (currently at cap; serialize after one of Wave 1.5 / language ingest / bio ingest lands)

### ANCHOR 2: cortex_ultrametric_clustering_coarse_grain_v1

- **Anchor pointer:** see `notes/exp_dev_handoff_research_cortex_4x_selective_abstraction_drill_2026-06-26.md` ANCHOR 2 (full spec already there); compose on chain-grade SEMANTIC concept learner (`data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1/metrics.json`)
- **Substrate-product reading:** different mechanism class — semantic clustering replaces per-atom selectivity. Collapse high-cosine atom clusters into representative + residual codes. Different failure mode from E-tensor entirely.
- **Why dispatch now:** orthogonal to E-tensor; not contingent on E-tensor fix; tests whether the cortex content-extraction problem can be solved at CLUSTER level instead of ATOM level.
- **Cost:** ~4-6 hr local_cpu
- **Dependency:** spawn budget; can dispatch in parallel with ANCHOR 1

### ANCHOR 3: cortex_SOC_critical_write_rate_avalanche_v1

- **Anchor pointer:** see `notes/exp_dev_handoff_research_cortex_4x_selective_abstraction_drill_2026-06-26.md` ANCHOR 3
- **Substrate-product reading:** Bak-Tang-Wiesenfeld self-organized-criticality frame; heterosynaptic depression on saturated atoms; emergent capacity management instead of explicit gating. Tests "homeostasis is EMERGENT not enforced."
- **Why dispatch now:** different mechanism class; tests UNIFIED theoretical frame (substrate IS a sandpile, just needs to find criticality).
- **Cost:** ~4-6 hr local_cpu
- **Dependency:** spawn budget

### ANCHOR 4: cortex_MDL_dictionary_turnover_v1

- **Anchor pointer:** see `notes/exp_dev_handoff_research_cortex_4x_selective_abstraction_drill_2026-06-26.md` ANCHOR 4
- **Substrate-product reading:** information-theoretic per-atom MDL bits-saved metric; turnover via replacement (random or bound-composition); explicit capacity management vs gated downscale.
- **Why dispatch now:** complementary to ANCHORS 1-3; tests if turnover-by-replacement works where gated-downscale didn't.
- **Cost:** ~4-6 hr local_cpu
- **Dependency:** ANCHORS 1-3 (run after to compare; or in parallel if spawn budget allows)

## Recommended dispatch sequence

When spawn budget frees (one of the current 3 in-flight agents lands):

**Wave 1.6a (parallel; serialize as budget allows):**
1. ANCHOR 1 (E-tensor re-test with fairness fixes) — load-bearing for "is E-tensor mechanism viable at all"
2. ANCHOR 2 (ultrametric clustering) — orthogonal mechanism class
3. ANCHOR 3 (SOC criticality) — orthogonal mechanism class

**Wave 1.6b (after 1.6a verdicts):**
4. ANCHOR 4 (MDL turnover) — informed by which of ANCHORS 1-3 showed signal

## Context pointers

- USER fairness audit: this conversation 2026-06-26 (turn before this handoff was filed)
- v1 HARD_FAIL evidence: `data/exp_cortex_E_tensor_HARDER_REGIME_v1_smoke/metrics.json`
- Cortex 4x cross-discipline drill (anchors 2-4 specs): `notes/exp_dev_handoff_research_cortex_4x_selective_abstraction_drill_2026-06-26.md` + `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md`
- USER pivot: `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- TWO_TIER + NREM replay chain-grade primitives that compose with cortex mechanisms

## Contract

- ANCHOR 1: USER-identified fairness fixes load-bearing. If Fix A test passes but Fix B fails (cor still > 0.5), don't claim mechanism win — file as MEASURED_MECHANISM only.
- ANCHORS 2-4: pre-reg bands per cortex 4x drill handoff are load-bearing; bake into prereg verbatim.
- ARM_BASELINE_MAG_GATED in ANCHOR 1 is NEW — tests whether magnitude was the right signal all along.
- All cells: substrate-only-decode gate (n_llm==0); per-seed cv<=0.05 for chain-grade; default tier MIDDLE per Fix #28.

## Autonomy declaration

exp_dev owns cell authoring + smoke + dispatch. Does NOT own: relaxing Fix A or Fix B (USER-identified fairness); reaching for language-prediction evals; bypassing the dependency-on-spawn-budget gate (serialize, don't exceed Fix #14 cap of 3 in flight).

---

-- Research (Opus 4.7-1M)
