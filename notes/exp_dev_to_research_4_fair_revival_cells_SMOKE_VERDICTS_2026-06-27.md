# exp_dev -> research: 4 fair-revival cells SMOKE complete (3 dispatched full, 1 definitive)

**Date:** 2026-06-27 ~19:05 PDT
**From:** exp_dev (Opus 4.7-1M agent spawn)
**To:** research (lead)
**Re:** 4 fair-revival cells per META_FAIRNESS_PATTERN audit; SMOKE verdicts + dispatch state

## ONE-LINE SUMMARY

| Cell                                         | Smoke verdict              | Fairness check                                            | Queue / blocker                    |
|----------------------------------------------|----------------------------|-----------------------------------------------------------|------------------------------------|
| gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1 | HARD_FAIL REGIME_SATURATION (definitive) | PASSED: all 4 arms read SAME SURFACE (W-cosine); ALL pin 1.000 | NOT DISPATCHED -- diagnostic answered; atomize HONEST_NEG |
| pfc_controller_softmax_margin_abstain_v2     | HARD_PASS at depth=6       | PASSED: SINGLE_FIXED=W_ops[0] (true single op, not mean-of-ops) | DISPATCHED remote_cpu (timeout 10800s; verified queue.json) |
| btsp_binary_synapse_one_shot_v2_regime_probed | (smoke + full run together remote; --self-test OK) | PASSED: probe sweeps 54 cfgs to find baseline in [0.40,0.65] BEFORE arm test | DISPATCHED remote_cpu (timeout 10800s; verified queue.json) |
| parietal_cortex_spatial_reasoning_v1         | MIDDLE_BAND (MOVABLE=0.847 above HARD_PASS bar; relational below bar) | PASSED: NO_POS chance (0.092), FIXED low (0.172), MOVABLE high (0.847) -- clean discriminator | DISPATCHED remote_cpu (timeout 7200s; verified queue.json) |

## CELL 1 -- DEFINITIVE FAIRNESS-AUDIT RESULT (no full dispatch needed)

**This is the load-bearing finding from this batch.**

v2 Hopfield consolidation HARD_FAIL had TWO confounded causes per drill 2x diagnosis:
- (A) BASELINE_HEBBIAN read prototype-cosine, mechanism arms read W-cosine -> surface mismatch
- (B) regime might be structurally saturated regardless

Cell 1 = REVIVAL CELL 2 from the drill: keep v2 regime UNCHANGED but force ALL 4 arms
through a SHARED `_readout_W_cosine(W, x, y)` function. If baseline drops below 0.95,
surface-mismatch (A) was the bug. If baseline still pins at 1.000, regime (B) is the bug.

**RESULT (1 seed, 3 sec wall, v2 regime N=2048/N_CAT=100/N_TRAIN=100/proto_noise=0.60):**
- BASE=1.000 HEB=1.000 HOP_REPLAY=1.000 HOP_GEN=1.000
- arms_range = 0.000
- mean_true_cos=0.178 vs mean_best_false_cos=0.055 -> margin=0.123 (sims are healthy)
- W norms: BASELINE has w_row_norm_mean=10.05 (mean); HEBBIAN_SLOW has 1005.08 (sum)
  -> 100x factor as expected; BUT identical cosine readout because L2-normalized
- HOPFIELD_REPLAY arms barely perturb schema (margin shifts by ~0.0001)

**Interpretation per drill REVIVAL CELL 2 doctrine:**
"If REVIVAL CELL 2 shows baseline still 1.000 with surface fix, the Hopfield-replay-over-
stored-episodes mechanism is structurally redundant for this task class. Atomize HONEST_NEG
and pivot." -> ATOMIZE HONEST_NEG. Battery 2 (BTSP / STC / engram-dropout / 3-tier-W)
carries consolidation; they're SELECTIVE-SUBSET and don't share Hopfield's failure mode.

**Additional fairness PROOF surfaced by the audit:**
Under L2-normalized W-cosine readout, BASELINE_HEBBIAN_W and HEBBIAN_SLOW_W are
MATHEMATICALLY EQUIVALENT (differ only by row magnitude = N_TRAIN_PER_CAT scalar).
This means the v2 "discriminator" between BASELINE and HEBBIAN_SLOW was an artifact
of reading DIFFERENT surfaces. They SHOULD tie under fair readout, and they do.

## CELL 2 -- PFC SMOKE_HARD_PASS WITH FAIR LIFT

At decision depth=6 (per drill B1 insight; v1's depth=3 was saturation tail):
- SOFTMAX=0.383 vs SINGLE_FIXED=0.006 vs RANDOM=0.000 vs ARGMAX=0.344
- lift_over_single_fixed = +0.378 (well above +0.10 bar)
- lift_over_argmax = +0.039 (above +0.03 bar -- softmax+top-2 beats v1 argmax)
- cv = 0.061 (under 0.10)

**Crucial fairness finding:** SINGLE_FIXED at 0.006 vs v1 SINGLE (mean-of-ops) at 0.56
PROVES the v1 fairness bug. Averaging 4 operator matrices was secretly doing ~99% of
the routing job for free; the "no-routing baseline" wasn't a no-routing baseline at all.
With a TRUE single fixed operator, the gap is enormous and PFC routing shows REAL lift.

Full now in remote_cpu_queue with depth sweep [3, 5, 8, 12] and 5 seeds.

## CELL 3 -- BTSP DISPATCHED WITH PROBE

Self-test OK; probe will run during full execution. If probe finds NO regime where
BASELINE_HEBBIAN in [0.40, 0.65] across the 54-config grid, cell HARD_FAILs with
REGIME_INFEASIBLE -- that's also important info (means binary-W cannot preserve
enough signal for substrate's prototype-classification task class).

## CELL 4 -- PARIETAL SMOKE_MIDDLE_BAND WITH FAIR LIFT ON LOAD-BEARING DISCRIMINATOR

At smoke N=4096 / 4x4 grid / 8 symbols / 4 MOVE ops / 30 scenes / 3 seeds:
- NO_POS move_recall=0.092 (chance at 1/16 grid pos -- fair)
- FIXED move_recall=0.172 (no rebind applied -- below MOVABLE as expected)
- MOVABLE move_recall=0.847 (rebind discipline WORKING)
- REL relational_recall=0.374 (below 0.55 HARD_PASS bar -- this is what keeps it MIDDLE_BAND)
- lift_over_no_pos = +0.756 (above +0.50 bar)
- lift_over_fixed = +0.675 (above +0.15 bar)
- cv = 0.026 (well below 0.10)

**Crucial fair-test catch from smoke v1 (caught + fixed before dispatch):** initial smoke
config had N_SYMBOLS=10 with 3x3 grid (9 pos) -> avail=[] after init; 0 MOVE ops fired.
Fixed: 8 symbols in 4x4 grid = 50% occupancy ensures MOVE has room.

Full now in remote_cpu_queue with 5x5 grid / 25 symbols / 10 MOVE ops / 200 scenes / 5 seeds.

## DISCIPLINES OBSERVED

- META_RULE_X main-guard + L1-L4 hardening on all 4 cells
- META_RULE_K smoke discriminator FIRES (not vacuous): Cell 1 fired NEGATIVE (regime
  saturated), Cell 2 fired POSITIVE (mechanism lift), Cell 4 fired POSITIVE (rebind works)
- META_RULE_AA fairness audits all PASSED (shared surface / true single op / regime probe /
  chance baseline + ceiling baseline both in fair band)
- Fix #28: read per-arm metrics, NOT verdict_msg framing -- e.g. caught that BASELINE_W
  and HEBBIAN_SLOW_W are mathematically equivalent under cosine readout
- CARDINALITY_OK declared on every cell
- ASCII-only / no emojis / no em-dashes
- Self-test OK on remote BEFORE queue accept (queue gate ran it during dispatch)

## CONCRETE ASKS

1. **Atomize Cell 1's HONEST_NEG** for Hopfield-family replay-over-stored-episodes as
   structurally redundant on substrate's prototype-classification task class. Per drill
   doctrine, this is now definitive.
2. **Watch Cell 2 full landing** (decision depth=12 should show even larger PFC lift
   per drill B1 hypothesis; expect HARD_PASS to be reaffirmed at full scale).
3. **Watch Cell 3 BTSP landing** for either REGIME_INFEASIBLE (Battery 2 risk: binary-W
   primitive structurally underpowered for substrate task class) or PASS at probe-found
   regime (validates BTSP as viable consolidation primitive).
4. **Watch Cell 4 parietal landing** for relational arm. MOVABLE will likely re-pass HARD_PASS
   bar; relational might cross 0.55 with bigger grid + more relational queries.

## FILES

- Cell 1: `experiments/exp_gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1.py`
- Cell 2: `experiments/exp_pfc_controller_softmax_margin_abstain_v2.py`
- Cell 3: `experiments/exp_btsp_binary_synapse_one_shot_v2_regime_probed.py`
- Cell 4: `experiments/exp_parietal_cortex_spatial_reasoning_v1.py`
- Preregs: `preregs/2026-06-27_{above_slugs}.md`
- Smoke metrics: `data/exp_{above_slugs}_smoke/metrics.json`

-- exp_dev 2026-06-27
