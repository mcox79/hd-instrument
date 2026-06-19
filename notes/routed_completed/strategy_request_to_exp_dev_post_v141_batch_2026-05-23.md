# Strategy → Experiment Dev: Post-v141 substantive batch — limit cycle deeper + Demo 2 5-seed + N=524K stress + VAMP vs smoother head-to-head

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~06:35 EDT
**Topic**: Pipeline resumed (limit_cycle_N_sweep_v1.py created 06:29); user signal "exp dev needs strategy guidance for queue"
**cap_map state**: v141 (commit `7541f4b`)
**Trigger**: Exp Dev session resumed; new substantive directions warranted given LIMIT_CYCLE substrate-physics POSITIVE characterization at FULL + comprehensive substrate-product validation at FULL

## Context

Cycle 145 v141 commit captured 10 FULL verdicts smoke→FULL CONSISTENT batch:
LIMIT_CYCLE_DETECTED at FULL + Demo 1 5-seed FULL + N=262K FULL + 7 overnight
ON_ENVELOPE FULL.

Exp Dev resumed at 06:29 with new `exp_wave14_limit_cycle_N_sweep_v1.py`
(self-directed initiative on limit cycle N-scaling). Pipeline waking up.

**NEW substantive directions** beyond pending pickups:
1. Limit cycle deeper characterization (period distribution, K-dependence)
2. Demo 2 5-seed hardening (match Demo 1)
3. N=524K stress test (8× beyond V2.D)
4. VAMP-on-chain vs backward-smoother head-to-head FULL comparison
5. Cross-task + multi-target multi-seed hardening

## Pending pickup (re-emphasize)

- HEAVY_VALIDATED FULL (cycle 143 Priority 4; smoke 10× forward-vs-backward dichotomy)
- Retraction Phase 1 FULL (cycle 138 `f919da8`; smoke 0/3 REFUTES)
- Bet A continual-edit FULL (cycle 136 `d6caeba`; smoke KILLED at 100 edits)
- extreme_stress FULL (cycle 128 `c1acdbd`; long-overdue)

## PRIORITY 1 — Limit cycle deeper characterization (extends self-initiated)

Exp Dev queued `exp_wave14_limit_cycle_N_sweep_v1.py` on own initiative.
Extending with deeper characterization:

**`wave14_limit_cycle_period_distribution_v1`** (~10 GPU-min):

Histogram of cycle periods at N=65536 K=100 across all 100 codewords.
- Compute period for each codeword (cycle 144 showed 100% have cycles)
- Histogram: how many at period 1, 2, ..., 100, >100?
- Identify modal period

**Verdict criteria**:
- PERIOD_DIST_TIGHT: stdev/mean < 0.5 (periods cluster)
- PERIOD_DIST_BROAD: stdev/mean ∈ [0.5, 1.5]
- PERIOD_DIST_BIMODAL: bimodal distribution

**`wave14_limit_cycle_K_sweep_v1`** (~10 GPU-min):

Cycle period statistics at K ∈ {50, 100, 200, 500} at N=65536.

**Verdict criteria**:
- CYCLE_K_INVARIANT: cycle period statistics K-independent
- CYCLE_K_GROWS: cycle period scales with K
- CYCLE_K_SHRINKS: cycle period decreases with K

## PRIORITY 2 — Demo 2 5-seed hardening (match Demo 1 discipline)

`wave14_demo_2_lane_C_multihop_5seed_v1` (~30-60 GPU-min):

Demo 2 (Lane C compliance + multi-hop chain composition) is at single-seed
FULL (cycle 139). Demo 1 has 5-seed FULL (cycle 145). Match Demo 2 to
Research playbook 5-seed discipline.

**Verdict criteria**:
- DEMO_2_5SEED_PASS: mean ≥ 0.95, stdev < 0.05 across 5 seeds (both Lane C + multi-hop)
- DEMO_2_5SEED_PARTIAL: mean 0.50-0.95
- DEMO_2_5SEED_KILLED: mean < 0.50

## PRIORITY 3 — N=524288 stress test (8× beyond V2.D)

`wave14_substrate_N524288_v1` (~30-60 GPU-min):

Cycle 145 N=262K at FULL (4× beyond V2.D). Push 1 more doubling:
backward-smoother readout at N=524288 multi-hop chain composition.

**Verdict criteria**:
- N524K_SCALES: smoother@N=524288 acc ≥ 0.50
- N524K_PARTIAL: acc 0.30-0.50
- N524K_KILLED: acc < 0.30

## PRIORITY 4 — VAMP-on-chain vs backward-smoother head-to-head FULL

`wave14_vamp_vs_smoother_head_to_head_v1` (~30-60 GPU-min):

Direct comparison of TWO substrate-novel readout primitives at FULL:
- VAMP-on-chain (forward-backward EP) — cycle 127 PROVEN at FULL
- backward-smoother-only — cycle 139 + cycle 145 PROVEN at FULL

Compare on identical test grid (K, d, noise, N) at FULL:
- Accuracy parity?
- Compute cost difference?
- Edge case behavior?

**Verdict criteria**:
- HEADTOHEAD_EQUIVALENT: both ≥ 0.95 across grid (substrate-product equivalent)
- HEADTOHEAD_SMOOTHER_BETTER: smoother > VAMP at edge cases (preferred primitive)
- HEADTOHEAD_VAMP_BETTER: VAMP > smoother at edge cases
- HEADTOHEAD_CONFIG_SPLIT: each primitive better in different regimes

## PRIORITY 5 — Cross-task + multi-target 5-seed hardening

`wave14_crosstask_5seed_v1` + `wave14_multitarget_5seed_v1` (~30-60 GPU-min each):

Cycle 139 cross-task + multi-target at FULL but single-seed. Match
Research playbook 5-seed discipline.

**Verdict criteria**:
- CROSSTASK_5SEED_PASS: mean ≥ 0.50 (relaxed; multi-task may have variance)
- MULTITARG_5SEED_PASS: top-1 mean ≥ 0.95

## Total queue suggested

5 priorities × ~1-3 experiments each + pending pickups = ~10-15 experiments;
smoke + FULL = 20-30 runs; ~6-15 GPU-hours total.

Recommended priority ordering:
1. **PENDING PICKUP**: HEAVY_VALIDATED FULL (highest-leverage per META cycle 75)
2. **PENDING PICKUP**: Retraction Phase 1 FULL (substrate-physics gate; smoke REFUTED)
3. PRIORITY 1 limit cycle deeper (extends Exp Dev self-initiative; cheapest)
4. PRIORITY 4 VAMP vs smoother head-to-head (substrate-product primitive comparison)
5. PRIORITY 2 Demo 2 5-seed (substrate-product hardening)
6. PRIORITY 3 N=524K stress (substrate-product scope expansion)
7. PRIORITY 5 cross-task + multi-target 5-seed (substrate-product variance)
8. **PENDING PICKUP**: Bet A continual-edit FULL + extreme_stress FULL

## Substrate-product implication

**v141 → v142 expansion targets**:
- Two readout primitives head-to-head characterization
- Demo 2 hardened to 5-seed (match Demo 1 discipline)
- Substrate scope to N=524K (8× beyond V2.D)
- Limit cycle period distribution characterized
- Cross-task + multi-target variance estimated

## Per [[feedback-no-papers-product-only]]

All priorities substrate-product oriented:
- P1: substrate-physics characterization (extends LIMIT_CYCLE finding)
- P2/P3/P4/P5: substrate-product hardening + scope expansion + primitive comparison

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 60-120 min per recent Exp Dev pickup pattern.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
