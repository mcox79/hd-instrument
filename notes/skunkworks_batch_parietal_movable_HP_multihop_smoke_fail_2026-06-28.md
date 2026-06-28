# skunkworks batch landed-VET: parietal MOVABLE smoke HP + multihop smoke_v3 GATE_FAIL

**Date:** 2026-06-28
**Auditor:** skunkworks (Agent Teams sub-agent)
**Cell-author commit at audit time:** fade4410

## Landing 1: parietal MOVABLE-rebind phase diagram v1

**Ruling:** SMOKE_HARD_PASS confirmed. CERT delta = 0 (NOT chain-grade).

### Critical correction to landing narrative

The user-facing landing brief claimed "FULL 3-seed all HARD_PASS at 13:36-13:37 PDT". Verify-OFF-DATA inspection:

- `data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7/metrics.json`
- `data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_13/metrics.json`
- `data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_19/metrics.json`

All three contain `run_mode="self_test"`, `elapsed_s=0.0`, NO `phase_map` field. They are 1-point self-test stubs (eval_one_point at g=4,n_obj=3,mf=0.5,n_scenes=3). The `ts_iso` is 16:36-16:37Z = **12:36-12:37 EDT**, not 13:36-13:37 PDT. Per-file stat mtime confirms 12:36-12:37 EDT. The cell at `experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_*.py` accepts `--self-test`, `--smoke`, or no flag (full). These were dispatched with `--self-test`.

The FULL 56-point 3-seed phase sweep DID NOT RUN. The only real-data file is `data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7_smoke/metrics.json`.

This is a Fix #28 / BIAS-Q / verify-the-referent violation in the landing framing.

### Verify-OFF-DATA smoke recompute

Per `experiments/_parietal_phase_diagram_v1_base.smoke_verdict`:

| corner          | sub   | rand  | static | lift_static |
|-----------------|-------|-------|--------|-------------|
| g=8  n=8  mf=0.5 | 1.000 | 0.000 | 0.000  | 1.000       |
| g=16 n=20 mf=0.5 | 1.000 | 0.050 | 0.000  | 1.000       |
| g=32 n=200 mf=0.5| 0.250 | 0.000 | 0.000  | 0.250 (CLIFF)|
| g=4  n=8  mf=0.0 | 1.000 | 0.300 | 1.000  | 0.000 (no-rebind sanity)|

n_sat=3, n_fail=1, n_strong=3, AM_breach=[], arms_distinct=True. SMOKE_HARD_PASS recomputed.

### Pre-reg vs cell drift

- Pre-reg n_objs={3,8,20,50}; cell n_objs={8,20,50,100,200}. Cell-author rationale (META_RULE_AN pattern): Plate analytic cap underestimates substrate by ~2x at N=1024.
- Pre-reg smoke includes mf=0.8; cell smoke all mf=0.5.
- Pre-reg FULL=64; cell FULL=56 after `n_obj<=n_pos` filter.

Severity: MEDIUM. Sweep extensions have rationale; smoke mf-drop is unannotated; total points decreased without documentation.

### Cliff localization

Substrate jumps from 1.000 to 0.250 between (g=16,n=20,mf=0.5) and (g=32,n=200,mf=0.5). Smoke does not bracket the cliff tightly; FULL 56-pt sweep needed for chain-grade promotion.

### Chain-grade promotion gate

Re-dispatch seed_7/13/19 WITHOUT `--self-test` flag. Verify landed metrics.json has `run_mode='full'` and `len(phase_map)==56`. Require cross-seed cv<0.15 on cliff location and narrowed cliff bracket (e.g., n_obj in {50,100,150,200} at g=32).

### Atom

- `math::T3/EXP_parietal_movable_rebind_phase_diagram_v1_SMOKE_HARD_PASS_cliff_g32_n200_mf05_FULL_NOT_RUN_2026-06-28`
- sha256(first 16): `80b0cbbd998bd907`
- cert_status: `smoke_hard_pass_full_not_run`; cert_class: `mechanism_characterization`

---

## Landing 2: multihop phase diagram depth*V_C*N_chains v1 smoke_v3

**Ruling:** SMOKE_GATE_FAIL confirmed. CERT delta = 0. Failure mode: **(b) test-design issue** (NOT substrate failure, NOT cell mechanism bug; secondary gpu_util silent-except).

### Verify-OFF-DATA gate decomposition

Source: `data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json`.

| Gate                       | Status | Notes                                                        |
|----------------------------|--------|--------------------------------------------------------------|
| cardinality_ok             | PASS   | 4/4 corners observed                                         |
| arm_discrim_fires (>=2)    | PASS   | 4/4 corners have sub-rand > 0.20                             |
| saturation_observed        | PASS   | corner3 1.000, corner4 0.990 saturated=True                  |
| arms_differ_all            | PASS   | 4 distinct SHA-256 pairs                                     |
| cross_cell_rail            | PASS   | corner2 (15,200,200) top1=0.820 in pre-reg [0.75,0.86]; reproduces v1 anchor 0.808 |
| regime_fail_observed       | FAIL   | no corner < 0.10                                              |
| sat_corner_ok (>=0.95)     | FAIL   | corner1 (5,200,50) top1=0.940; 0.01 short = stochastic noise (n_chains=50; binomial std ~0.034) |
| fail_corner_ok (<0.10)     | FAIL   | corner4 (15,16000,200) top1=0.990 vs predicted 0.000          |
| gpu_util_ok (>=50%)        | FAIL   | n_samples=0; mean=0.0; gpu_avail=True; silent-except bug      |

### Root cause: test-design flaw

The SUBSTRATE arm uses partition-routed oracle cleanup with `N_PARTITIONS=20`. At nominal V_C=16000, this gives `part_size=800`. The per-step cleanup search size is the partition size, NOT the nominal V_C.

The `top1_pred` cone-formula extrapolation (anchored on v1 0.808 at V_C=200, N_chains=200; scaled by `V_C*N_chains` ratio) implicitly assumed full-V_C per-step search. The "fail corner" at (15,16000,200) was supposed to be a regime-fail null check (top1_pred=0.0), but substrate actually achieves 0.99 because the effective V_C is held nearly constant.

**Substrate did its job; the pre-reg's predictive bands were derived from a model that didn't account for partition-routing.**

### Secondary issues

1. `sample_gpu_util()` wraps `torch.cuda.utilization(0)` in `try/except Exception` which silently returns 0.0 without appending to `_GPU_UTIL_SAMPLES`. Typical cause: NVML/pynvml not initialized. **META_RULE_J (no-silent-except) violation.** The cell never knows whether GPU is being used.
2. sat_corner top1=0.940 vs threshold 0.95 is within stochastic noise; not a real failure.

### Failure mode classification

- (a) Cell-bug for substrate mechanism? **NO.** Substrate over-performs at fail-corner; mechanism is healthy.
- (b) Test-design issue? **YES, primary.** Pre-reg bands derived from wrong model.
- (c) Genuine substrate failure? **NO.**
- Secondary: gpu_util silent-except is a cell hygiene bug (META_RULE_J violation).

### Remediation

For research to re-spec the pre-reg:
- (i) sweep `N_PARTITIONS` axis holding `part_size` ~constant — this tests the actual per-step difficulty
- (ii) recompute `top1_pred` per-corner using `effective_V_C = V_C / N_PARTITIONS` with anchor at part_size=200 (or wherever v1 effectively was)
- (iii) drop the high-V_C regime-fail null since partition-oracle makes that regime not actually fail at this configuration

For cell-author:
- fix `sample_gpu_util` silent-except: log exceptions to a separate counter so the gate distinguishes "sampled 0" from "never sampled"

Then re-dispatch smoke_v4 with corrected bands.

### Atom

- `math::T3/EXP_substrate_multihop_phase_diagram_depth_VC_NChains_v1_SMOKE_v3_GATE_FAIL_test_design_2026-06-28`
- sha256(first 16): `0bfdac9e73a27ed5`
- cert_status: `smoke_gate_fail`; cert_class: `mechanism_characterization`

---

## CERT delta summary

- Pre-batch: math/atoms.jsonl=28649, cert_ledger=879
- Post-batch: math/atoms.jsonl=28651 (+2), cert_ledger=881 (+2)
- CERT count delta: **+0** (parietal smoke-HP not chain-grade; multihop SMOKE_GATE_FAIL not chain-grade)

## A5 protocol confirmation

Atomic write (tmp + os.replace + fsync) + verify-load + pre/post line-count delta + tail JSON parse + round-trip ID match. All 4 appends passed.
