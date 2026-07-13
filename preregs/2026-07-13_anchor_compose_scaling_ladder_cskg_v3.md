# Pre-registration: ANCHOR_COMPOSE scaling ladder (CSKG held-out-ENTITY; support_frac x k_core x N)

- **Cell:** `experiments/exp_anchor_compose_scaling_ladder_cskg_v3.py`
- **Anchor name:** `anchor_compose_scaling_ladder_cskg_v3`
- **Metrics path:** `data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json`
- **Filed:** 2026-07-13 (exp_dev). **Follow-up (B)** to the VET-CONFIRMED CHAIN_GRADE cell
  `anchor_compose_inductive_entity_cskg_v1` (commit 06c50feac). Answers the USER's standing question -- "does the win
  hold at bigger N / would it just work at scale?" Routes to `overnight_queue` (GPU).

## Question / prediction
The map-builder drill predicts capacity tracks LOCAL support-degree (VSA SNR ~ 5 log(D/d) = CA3 capacity), NOT global
N. So the win should HOLD as N grows IF per-entity support-degree is preserved, and DEGRADE GRACEFULLY as
support_frac / k_core shrink (fewer anchors per held entity). This cell sweeps those levers and reports the
win-vs-support-degree curve at each rung. Support-degree is the LOAD-BEARING stratifier (per the VET's correction:
global-degree stratification is VACUOUS here because held entities have train-degree 0).

## Ladder rungs (pre-registered; each OVERRIDES base k_core + support_frac; 2 seeds [7,13]/rung)
| rung | k_core | support_frac | tests |
|---|---|---|---|
| r0_base | 12 | 0.50 | reproduce confirmed v1 (POSITIVE CONTROL / ladder anchor) |
| r1_halfsupport | 12 | 0.25 | HALVED support per entity -- does the win survive fewer anchors? |
| r2_sparsecore_bigN | 8 | 0.50 | LOWER k-core threshold -> LARGER N + lower per-node degree ("bigger N") |

k-core note: a lower k_core admits MORE nodes (larger induced N) at lower per-node degree, so r2 is the "bigger N /
sparser core" test. Each rung runs the FULL confirmed 7-arm machinery + the confirmed ceiling-aware verdict; ckpt +
partials are isolated in per-rung subdirs so identical seeds across rungs do NOT collide on FitCheckpoint tags.

## Pre-registered bands (primary metric = FILTERED MRR; picked BEFORE the run)
- **Per-rung**: each rung gets the CONFIRMED per-rung verdict (HARD_PASS / MIDDLE / HARD_FAIL / INCONCLUSIVE) from
  `aggregate_and_verdict` with its OWN in-run oracle headroom H (ceiling-relative, so a rung with a lower ceiling is
  scored fairly against its own ceiling).
- **Base reproduction (Gate D, required to anchor the ladder)**: r0_base must be `HARD_PASS` AND
  `anchor_margin >= 0.50 * 0.127727` (>= 50% of the confirmed v1 margin). If not, overall =
  `SCALING_INCONCLUSIVE_BASE_DID_NOT_REPRODUCE` (the ladder cannot be interpreted).
- **Retention** `= rung_anchor_margin / base_anchor_margin`; a non-base rung is classified:
  - **HOLDS**: retention >= 0.40 (the halved-support / bigger-N lever retained >= 40% of the win).
  - **GRACEFUL_DEGRADE**: 0.15 <= retention < 0.40.
  - **COLLAPSE**: retention < 0.15 (the win did NOT scale).
- **Overall verdict**:
  - `SCALING_HOLDS`: base reproduced AND every non-base rung HOLDS. (**HARD-PASS** of the scaling question.)
  - `SCALING_GRACEFUL_DEGRADE`: base reproduced AND all non-base rungs at least GRACEFUL (>= 0.15). This is the
    PREDICTED outcome (support_frac 0.5->0.25 halves support-degree -> expected partial drop; r2 lower degree ->
    expected partial drop; the win-vs-support-degree curve should still show ANCHOR mrr rising with support degree).
  - `SCALING_COLLAPSE_SOME_RUNG` (**HARD-FAIL** of the scaling question): base reproduced but some rung COLLAPSES
    (retention < 0.15) -> the win does NOT survive that lever; localize via the per-rung support-degree curve.
- **Load-bearing report**: `scaling_summary.rungs[*].anchor_mrr_by_support_degree` -- the ANCHOR MRR per
  support-degree bin {cold, d1, d2_3, d4_7, d8plus} at EACH rung. The confirmed v1 curve (cold 0.00004, d1 0.0038,
  d2_3 0.075, d4_7 0.171, d8+ 0.115) rises with support degree; the prediction is this SHAPE holds at every rung
  (win tracks local degree), so retention is governed by how each lever reshapes the support-degree DISTRIBUTION.

## Self-test (MEASURED, local .venv, single-thread CPU, 8.0s) -- PASS
Shared mechanism self-test with the confirmed cell (the rung sweep changes only k_core/support_frac, not the
mechanism). MEASURED@data/exp_anchor_compose_scaling_ladder_cskg_v3_selftest/metrics.json:mechanism_selftest:
anchor_margin=0.39129, scramble_margin=0.26872, oracle_fires=True, validity_preflight_ok=True, verdict=SELFTEST_PASS.
The rung-aggregation + support-curve + scaling-classification logic was unit-tested off-line on synthetic rung
results (4 cases: SCALING_GRACEFUL_DEGRADE / INCONCLUSIVE_BASE / COLLAPSE_SOME_RUNG / SCALING_HOLDS all classify
correctly; retention math + support-degree-curve extraction verified). The rung sweep is validated PER-RUNG at FULL
by each rung's own oracle-relative gate (no rung is trusted unless its ORACLE fires).

## SCHEMA-VET / cell-template fields
- `arms_differ_verified: true` (7 arms per rung; >=5 distinct sigs asserted per (rung, seed)).
- `final_metrics_atomicity: tmp_replace`; `except SystemExit: raise` before `except Exception`; grep-clean. VERIFIED.
- `cardinality_ok: true` -- `EXPECTED_N_UNITS = n_rungs * n_seeds = 3 * 2 = 6`; every (rung,seed) asserted (all-7-arms
  + >=5 sigs); shortfall -> `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `sweep_alignment_verdict: ALIGNED` -- the swept params (support_frac, k_core) are EXACTLY the levers the mechanism
  experiences: support_frac controls per-entity support-degree directly; k_core controls the arena N + degree
  distribution the anchor bundle draws from. No nominal-vs-effective mismatch (Gate A).
- `discriminating_fraction`: the ladder is designed so >=1 rung lands in each band region; the base rung reproduces
  HARD_PASS (MEASURED confirmed) and the shrink-levers are predicted to move retention into [0.15, 1.0].
- `positive_control_arms`: ORACLE_ADDITIVE fires per rung; r0_base reproduces the confirmed ANCHOR margin (Gate D).
- `crlb / info-ceiling`: per-rung ceiling-relative bands (each rung's own H); `discriminator_reachability: true`.
- `cell_chunked: false` (per-rung per-seed FitCheckpoint ckpt_every=20 in isolated per-rung subdirs, outage-resumable).
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true` (heartbeat tags per rung+seed);
  `per_unit_failure_class: true` (per rung+seed failure_class).
- `progress_logging: print_flush_true` (line-buffered stdout; per-rung + per-seed flush prints; timeout_s >= 1800).
- `calibration_check: adaptive_with_discriminator_gate` (RUNG_HOLD_FRAC=0.40 / RUNG_COLLAPSE_FRAC=0.15 /
  BASE_REPRO_FRAC=0.50 pre-registered, NOT tuned on real data).

## Compute architecture
class (c) MIXED (identical to confirmed v1, looped over rungs). SHARDED storage. device=auto (cuda on GPU host).
Each (rung, seed) is fit-checkpointed in a per-rung subdir; a timeout/outage resumes the in-progress fit.

## Run profiles
- **self_test** (LOCAL .venv gate, PASSED 8.0s): base rung only, k=12, ep=350, 1 seed, planted arena.
- **memsmoke** (GPU one-shot `--memsmoke`): base rung only, FULL footprint, ep=25, 2 seeds -> no-OOM check.
- **full** (REMOTE GPU): 3 rungs x 2 seeds [7,13], k=24, ep=500, n_neg=128, neg_chunk=16, ckpt_every=20,
  n_heldout_eval=3000. Est ~2.2h/rung (r2 larger-N slower) -> ~7h total; timeout 36000s (10h) with ckpt resume.

## Numbers provenance
- confirmed v1 anchor margin 0.127727, support-degree curve (cold/d1/d2_3/d4_7/d8+):
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates + per_seed[0].localization.
- self-test anchor_margin 0.39129: MEASURED@data/exp_anchor_compose_scaling_ladder_cskg_v3_selftest/metrics.json.
