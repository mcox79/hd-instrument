# PRE-REG: substrate_hub_spoke_E1_v3_MRC_calibrated_routing

**Date:** 2026-06-25
**Cell:** `experiments/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.py`
**Lane:** 1 (substrate-native)
**Routing:** GPU overnight_queue (via hdi_orchestrator handoff; exp_dev push is harness-denied)

## What it tests

v2 RESCUE of MIDDLE_BAND `substrate_hub_spoke_E1_v2_diverse_algorithm`. v2 landed
MIDDLE_BAND READOUT_DEGENERATE because (a) SoftHebb spoke produced `spoke_recon_err = NaN`
across all seeds, (b) cf-RPE gates collapsed to [0.96, 0.03, 0.01] -- the broken NaN spoke
won routing, (c) `sign(sum_spokes)` bundle of K=3 orthogonal spokes loses 0.5*log(K) bits
mutual information (signal-processing maximal-ratio-combining theorem; brain ATL hub-spoke
analog is MRC weighted sum NOT sign-of-sum).

Per drill `notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md` DRILL A
(info-theory + MRC math) + DRILL B (brain ATL hub-spoke) + DRILL C (MRC + turbo-decoder)
+ DRILL E (NaN propagation), v3 applies THREE FIXES:

1. **FIX 1 -- Per-spoke health check at construction.** Each spoke's codebook is
   validated for NaN/Inf + recon_err in finite sane range + non-zero row norms. If
   any spoke is broken, `build_arm_encoder` raises `RuntimeError("FIX_1_BROKEN_SPOKE: ...")`
   and the arm is recorded as `compute_failed` with the explicit cause (NOT silently
   bundled into the hub).
2. **FIX 2 -- MRC-weighted bundle.** Replace `sign(sum_spokes)` with
   `hub = sign( sum_i softmax(gate_logits / T_gate)_i * spoke_i )` where T_gate is
   swept over `{0.1, 0.5, 1.0, 2.0}` and the T producing gate-entropy in `[0.5, 1.5]`
   wins. This is the optimal soft-combiner for K independent observation channels
   (Brennan 1959; turbo decoding literature).
3. **FIX 3 -- Gate training on real task signal.** Train gate logits against the
   next-token-prediction loss gradient using REINFORCE-style advantage on per-spoke
   `cos(spoke[i], spoke[j])` for bigram (i, j). ZERO LLM at inference (substrate-native;
   substrate's own per-spoke cosine IS the task signal).

## Arms (4)

1. `ARM_BASELINE_PATH_C_SINGLE` -- control + sanity rail (reproduces v2 baseline 7.667)
2. `ARM_HUB_3SPOKE_MRC` -- 3-spoke MRC bundle + cf-RPE LR-trained gates (PRIMARY load-bearing)
3. `ARM_HUB_3SPOKE_MRC_PLUS_FPE` -- arm 2 + S4 FPE (4-spoke MRC)
4. `ARM_HUB_5SPOKE_MRC_ABLATION` -- same spokes as arm 2 but sign-sum (NO MRC) -- ABLATION
   to isolate whether MRC is load-bearing vs (health-check + gate-training)

## DISCRIMINATOR

- `ARM_HUB_3SPOKE_MRC` PASS + `ARM_HUB_5SPOKE_MRC_ABLATION` FAIL -> MRC is load-bearing fix
- Both PASS -> health-check + gate-training are load-bearing (MRC unnecessary)
- Neither pass -> architecture refuted; pivot per drill recommendations

## HARD bands

- `HARD_PASS_CHAIN_GRADE`: best_hub bpc <= 6.95 AND diversity_cv >= 0.05 AND
  no broken spokes AND gate_entropy in [0.5, 1.5] AND CV(seeds) <= 0.03
- `HARD_PASS`: best_hub bpc <= 7.50 AND beats single-spoke baseline by >= 0.10 BPC
  AND no broken spokes
- `HARD_FAIL`: best_hub bpc >= 7.70 (all arms at unigram floor) OR any spoke produces NaN/Inf
- `SANITY_RAIL`: ARM_BASELINE_PATH_C_SINGLE bpc within +/-0.02 of v2 7.667

## Per-arm sanity

Baseline must reproduce v2 baseline 7.667 within +/-0.02.

## Production config

- N_DIM = 8192
- V = 4000 (text8)
- N_TRAIN = 100_000
- N_HELD = 20_000
- SEEDS = [7, 17, 23] (3 seeds)
- sparse-bipolar f = 0.02
- T_GATE_GRID = [0.1, 0.5, 1.0, 2.0]
- Timeout: 7200s (overnight_queue GPU)

## Self-test evidence

`.venv/Scripts/python.exe experiments/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.py --self-test`
returns PASS on T1-T16 including:

- T11 FIX1 spoke_health (NaN/Inf detection + recon_err sanity)
- T12 FIX2 MRC bundle (T_gate sharpens/flattens; gate softmax sums to 1)
- T13 FIX3 task-signal gate_logits (finite + no NaN)
- T14 gate_entropy (uniform = log(3), peaked < 0.2)
- T15 v3 verdict bands: CHAIN_GRADE / HARD_PASS / HARD_FAIL_BROKEN_SPOKE /
  HARD_FAIL_ALL_AT_UNIGRAM / SANITY_RAIL_MISS / DISCRIMINATOR (MRC_LOAD_BEARING etc.)
- T16 llm=0

## Cites

- `notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md` (drill that
  identified the THREE causes + recommended the three fixes)
- `experiments/exp_substrate_hub_spoke_E1_v2_diverse_algorithm.py` (v2 base; MIDDLE_BAND)
- `data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json` (v2 evidence)
- `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md` (synthesis priors)
- USER 2026-06-23 Path C substrate-owned encoder
- USER 2026-06-22 Fix #24 GPU must use GPU

## Honest scope

- Tests 3 fixes (health-check + MRC + task-signal gates) on the v2 hub-spoke design.
- Does NOT test K>4 spokes or other gate-training schemes (decision-level fusion,
  product-of-experts).
- ABLATION arm uses SAME 3 spokes as PRIMARY but sign-sum bundle -- isolates MRC
  contribution from the other two fixes.
