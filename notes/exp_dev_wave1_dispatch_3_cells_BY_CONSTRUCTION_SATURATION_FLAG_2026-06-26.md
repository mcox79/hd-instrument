# exp_dev Wave 1 dispatch -- 3 cells + by-construction-saturation flag for landed-VET

**Filed-by:** exp_dev (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER-greenlit Wave 1 per `notes/exp_dev_handoff_research_first_wave_7_compositional_understanding_USER_GREENLIT_2026-06-26.md`

## Dispatch summary

3 cells authored, smoke-gated, dispatched to local_cpu_queue:

| Anchor | Status | Timeout | Prereg |
|---|---|---|---|
| cortex_E_tensor_separate_importance_v1 | running | 4500s | preregs/2026-06-26_cortex_E_tensor_separate_importance_v1.md |
| topk_composition_refuse_gate_v1 | pending | 1200s | preregs/2026-06-26_topk_composition_refuse_gate_v1.md |
| pc_cleanup_attractor_v1 | pending | 7200s | preregs/2026-06-26_pc_cleanup_attractor_v1.md |

New primitive: `hdlab/excitability.py` (per-atom E[i] tracker; CREB analog).

All smoke gates produced valid metrics.json; all --self-tests passed on .venv (Py3.11). All cells substrate-only-decode (n_llm==0; structural; no LLM imports). All cells ARM_BASELINE + RANDOM-control rail per handoff.

## BY-CONSTRUCTION-SATURATION FLAGS (META atom; honest verdict trail)

**Flag 1 -- ANCHOR 1 cortex_E_tensor (CONFIRMED IN-FLIGHT):** Live log at seed 7 + 17 confirms: ARM_E_GATED arm has `n_downscaled=0` (the E-distribution doesn't drift below E_THRESHOLD=0.30 within the retrieval cycle), ARM_RANDOM downscales 40% of atoms but the substrate cleanup margin is so strong that recall_old still hits 1.000 (no degradation). Predicted verdict: **HARD_FAIL** via the discriminator gate: `|E_GATED.rec_old - RANDOM.rec_old| < 0.03` (both are 1.000, diff=0) triggers HF c3. That IS the honest verdict: the substrate at this alpha=0.244 + downscale_scale=0.20 + downscale_frac=0.40 regime fends off both gates perfectly so the E-mechanism is not testable. Research follow-up: raise alpha (e.g. M_OLD=600 to push past Hopfield capacity) AND/OR raise E_THRESHOLD to ~0.55 AND/OR add slow_decay() with decay=0.95 between retrieval-pass batches so unused atoms actually drift down. The HARD_FAIL is mechanism-not-discriminator, NOT mechanism-rejected.

**Flag 2 -- ANCHOR 6 pc_cleanup_attractor:** Pre-dispatch probe at near-full config showed vanilla cleanup is at recall=1.0 even at alpha_eff=1.07 (3.5x Hopfield capacity) and HOP_NOISE_P_FLIP=0.15. The substrate's per-hop cleanup margin is too strong; PC's top-K bundle has no headroom to demonstrate value. Cell will likely land HARD_PASS-by-tie (both VAN and PC at 1.0) which Skunkworks should downgrade to MEASURED_MECHANISM. Honest finding: at this substrate-cleanup margin, PC's top-K bundle is neutral; need higher-difficulty regime (e.g. HOP_NOISE_P_FLIP>=0.40 OR much higher alpha_eff) to detect PC value. Cell will produce per-arm metrics Research can use to design the follow-up regime.

**Flag 3 -- ANCHOR 3 topk_composition_refuse_gate:** smoke produced HARD_PASS with 3 ambiguous queries / 120 (P_FLIP=0.35 in smoke). At FULL the production P_FLIP=0.18 is gentler -- ambiguous_frac may be very low, producing degenerate HARD_PASS (DISJ never exercised). If amb_frac < 0.05 at full, downgrade to MEASURED_MECHANISM and recommend Research raise P_FLIP_FULL.

## Per-mechanism honesty (per Fix #28)

These are NOT proposals for Skunkworks to tier UP -- they're cell-author flags that the SMOKE-mode + production-mode discriminator-regime may be too gentle. Verdict-text-only interpretation (correctness numbers PASS the bands) will hide the mechanism-didn't-fire reality. Need to READ metrics.json per-arm (especially n_downscaled, n_disjuncted, ambiguous_frac) to make honest tier calls.

## Pivot frame honored

All 3 cells are COMPOSITIONAL-UNDERSTANDING tests per USER 2026-06-26 standing lock. Zero text8 / BPC / language-prediction evals. All use bipolar HD atoms + Hebbian outer-product substrate primitives + substrate-native cleanup. No LLM forward calls. No tokenizer-vocab evals.

## Wave 2/3 NOT dispatched

Per handoff dispatch-ordering, Waves 2 (ANCHOR 2 typed-multibank + ANCHOR 4 SOLAR_LARS; remote_cpu_queue, route via Orchestrator per Fix #24) and Wave 3 (ANCHOR 5 emergent-slot-discovery + ANCHOR 7 holographic_chunk_pack; local_cpu_queue) are NOT touched. Wave 1 verdicts should inform Wave 2 (especially ANCHOR 2 typed-routing rail used by ANCHOR 5).

-- exp_dev (Opus 4.7-1M)
