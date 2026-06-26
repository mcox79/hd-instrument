# exp_dev -> orchestrator: dispatch ask MH_REVIVAL ANCHOR 1 to remote_cpu_queue

## TL;DR
- Cell: `experiments/exp_mh_revival_feature_regime_diagnostic_v1.py`
- Prereg: `preregs/2026-06-26_mh_revival_feature_regime_diagnostic_v1.md`
- Anchor: `mh_revival_feature_regime_diagnostic_v1`
- Queue: **remote_cpu_queue** (USER directive 2026-06-26; 1 CPU-hr cheapest test)
- Timeout: **3600s** (1h budget; ~10-30s expected wall)
- Commit: `7db1b4a6`
- Push: harness-DENIED to exp_dev -> Orchestrator must push origin/main + SCP+SSH dispatch

## Dispatch command for Orchestrator
```
bash tools/orchestrator/queue_add.sh remote_cpu_queue \
    mh_revival_feature_regime_diagnostic_v1 \
    experiments/exp_mh_revival_feature_regime_diagnostic_v1.py \
    preregs/2026-06-26_mh_revival_feature_regime_diagnostic_v1.md \
    3600
```

## Source thread
- Research drill: `notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md`
- Handoff: `notes/exp_dev_handoff_research_modern_hopfield_revival_slow_built_basins_2026-06-26.md` (ANCHOR 1)
- USER reframe: prior Modern Hopfield prototype cell HARD_FAIL was REGIME error (softmax/WTA wrong
  for 20-instance weak-basin substrate); test feature-matching regime (n=2 polynomial; cooperative
  aggregation across instances) on the SAME substrate state.

## What this cell does in one sentence
Tests whether the SAME Modern Hopfield architecture with `n=2` (Krotov feature-matching regime;
many basins cooperate) outperforms `n=20`/softmax (prototype regime; one basin dominates) on the
SAME substrate state that just produced MH_PROTO=0.22 in the prior gap3 cell.

## Pre-reg bands (LOCKED via module-init assert)
- **HARD_PASS_REGIME_CONFIRMED**: ARM_HOPFIELD_N2 >= 0.50 AND lift >= +0.15 over
  ARM_HOPFIELD_N20_SOFTMAX. Substrate-product win without architecture change.
- **HARD_FAIL_MECHANISM_CLASS_DEAD**: ARM_HOPFIELD_N2 within 0.05 of softmax control
  (regime not the issue; pivot to slow-build STC ANCHOR 2).
- **MIDDLE_BAND [0.35, 0.50)** : partial regime lift.
- **MIDDLE_BAND_FLOOR_MET_INSUFFICIENT_LIFT**: N2 above floor but lift <+0.15.
- **HARD_FAIL_HARNESS_CONFOUND**: HRR_BUNDLE_PROTOTYPE drifts >0.03 from Cell 1 ref
  (0.4733 full / 0.58 smoke seed=11) -> methodology mismatch; abort interpretation.

## 6 arms
- ARM_BASELINE_NO_SCHEMA (Cell 1 sanity rail)
- ARM_HRR_BUNDLE_PROTOTYPE (Cell 1 cross-cell rail; privileged cat_vec; upper-bound)
- ARM_HOPFIELD_N2 (PRIMARY hypothesis; feature-matching cooperative aggregation)
- ARM_HOPFIELD_N4 (intermediate polynomial regime)
- ARM_HOPFIELD_N10 (approaching prototype regime)
- ARM_HOPFIELD_N20_SOFTMAX (prior MH failure-regime control rail)

## Pre-dispatch checklist (verified before commit)
- [x] Self-test PASS (6/6 formula tests; T1 HRR roundtrip cos=1.000, T2 Hopfield n=2 high-signal
  recovery acc=1.000, T3 polynomial-score consistency, T4 bands LOCKED, T5 cross-cell rail
  encoded 0.4733, T6 6-arm discriminator spread 0.060 non-degenerate)
- [x] Smoke PASS valid metrics; seed=11 N=8192 wall=0.69s:
  BASELINE=0.42 HRR_BUNDLE=0.58 N2=0.58 N4=0.50 N10=0.40 N20_SOFTMAX=0.48
- [x] Cross-cell rail PERFECT on smoke: HRR_BUNDLE=0.58 == Cell 1 seed=11 ref 0.58 exactly
- [x] Verdict logic exercises all 4 paths (HP / HF_dead / HF_confound / MB variants)
- [x] zero_llm_calls_at_inference=True; n_llm_calls=0; ENCODER_PROVENANCE=SUBSTRATE_NATIVE
- [x] Per-seed checkpoint via experiments/_seed_checkpoint
- [x] PROT-018 N/A (no _n<N> suffix)
- [x] PROT-019 N/A (timeout=3600s < 4h floor; cell wall ~10-30s; budget 100x safety)
- [x] PROT-020 N/A (queue=remote_cpu_queue, not GPU; numpy is fine)
- [x] PROT-021 N/A (timeout=3600s < 14400s threshold; cell wall<<<floor; but checkpoint imported anyway)
- [x] Fix #26 predispatch_check.py: PROCEED (0 prior landings, 0 atoms)
- [x] ASCII only
- [x] Commit path-scoped (cell + prereg only; NEVER `git add -A`)

## Honest smoke reading (Fix #28; do NOT over-claim)
Smoke verdict was `MIDDLE_BAND_FLOOR_MET_INSUFFICIENT_LIFT`:
- N2=0.58 hits floor 0.50 - regime hypothesis DIRECTIONALLY confirmed (vs prior MH_PROTO=0.22 on
  the same seed=11 in prior gap3 cell -- 2.6x lift).
- BUT smoke lift over softmax control is +0.10 < +0.15 pre-reg threshold.
- Full 3-seed mean (seeds 11,13,19) decides chain-grade-ness.
- N-sweep monotone at smoke: N2(0.58) > N4(0.50) > N10(0.40), regime gradient measurable.
- Caveat: N20_SOFTMAX=0.48 in THIS cell is much better than prior gap3 MH_PROTO=0.22 because the
  mechanism is FEATURE-MATCHING aggregation over instances (this cell) vs
  PROTOTYPE-FORMATION-then-bundle (prior cell). Both regime AND mechanism differ. The honest
  framing on the lift is "feature-matching N2 vs feature-matching softmax", not "vs prior cell".

## Compute budget rationale
~10-30s per seed FULL (vectorized matmul over (K_total=100, D=8192)); 3 seeds -> ~30-90s wall;
timeout=3600s gives 40-120x safety. Per USER directive "1 CPU-hr cheapest test".

## Routing note (USER directive)
remote_cpu_queue NOT local NOT GPU. Cell is numpy-only matmul; no benefit from GPU at this regime;
remote CPU is the cheapest dispatch path.

## Atomization on HARD_PASS
- atom: modern_hopfield_feature_regime_substrate_n2_outperforms_prototype
- hdlab update: hdlab/iterative_attractor.py n-parametric variant
- substrate-product win: regime fix without new architecture

## Next routing on land (regardless of verdict)
- Skunkworks landed-VET (per cert observability discipline)
- If HARD_PASS: atomize + Director ratify + ship
- If HARD_FAIL_MECHANISM_CLASS_DEAD: pivot to STC ANCHOR 2 (slow-build write-side; 6-10 CPU-hr)
- If MIDDLE_BAND: queue follow-up beta-sweep or full STC build

-- exp_dev (per ANCHOR 1 dispatch ask 2026-06-26)
