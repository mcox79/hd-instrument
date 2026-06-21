# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): 2 D1 saturation-suspect can-fail re-run pre-regs (per CERT INTEGRITY AUDIT routing). Batched. Brief.

**Date:** 2026-06-21T04:50:00Z (true `date -u`)  **Re:** Skunkworks's CERT INTEGRITY AUDIT D1 routing: 2 saturation suspects need can-fail re-runs to determine genuine-PASS vs reframe-MM.

---

## Cell 1: `exp_planted_csp_viability_can_fail_at_harder_alpha_v1_cpu_v1.py`

### What it does
Tests planted_csp_viability at HARDER alpha values where saturation suspect (D1) fired. Original cell tested alpha=0.02 (easy regime); D1 flags possible saturation @ planted-solution-trivially-found. Re-run sweeps alpha ∈ {0.02 (control), 0.05, 0.10, 0.15, 0.20} to locate can-fail (recall drops below 0.95).

### CAN-fail discriminating regime
- **HARD_PASS:** can-fail LOCATED at some α ≤ 0.20 (genuine envelope; saturation cleared)
- **HARD_FAIL:** recall stays ≥0.95 at α=0.20 (still saturated; reframe to MM "viability at α≤0.20 LOWER-BOUND not genuine envelope")
- 3 seeds; cv ≤ 0.05

### Composes_with
- `T3/EXP_planted_csp_viability_v1` (original; the saturation-suspect being re-tested)
- CSP first-ship CERT 590 (related substrate-product chain)

### Tier
- IF can-fail located: original CHAIN-GRADE stands (saturation false alarm; envelope verified)
- IF still saturated: reframe to MM with LOWER-BOUND annotation (cliff-is-MEASUREMENT discipline; per a3f473dd precedent)

---

## Cell 2: `exp_pp49_hrc_depth_sweep_can_fail_v1_cpu_v1.py`

### What it does
Tests pp49_hrc at DEPTH SWEEP where saturation suspect (D1) fired. Original cell tested single-depth (D1 flag: depth=8 PASS may be single-data-point saturated). Re-run sweeps depth ∈ {6, 8 (control), 10, 12} to verify the depth=8 PASS holds and locate can-fail (cliff onset).

### CAN-fail discriminating regime
- **HARD_PASS:** depth=8 PASS confirmed + can-fail LOCATED at depth ≤ 12 (genuine envelope; cliff onset measured)
- **HARD_FAIL:** depth=8 fails on re-test (original was lucky single-seed) OR no cliff up to depth=12 (saturated; reframe MM)
- 3 seeds; cv ≤ 0.05

### Composes_with
- `T3/EXP_pp49_hrc_v1` (original; the saturation-suspect being re-tested)
- pp48_nkt cluster (related depth-cliff family)

### Tier
- IF depth=8 PASS confirmed + cliff located: original CHAIN-GRADE stands (saturation false alarm; envelope verified)
- IF depth=8 fails: HONEST DEMOTE (single-seed was lucky; reframe to MM or RESEARCH_FINDING)
- IF still saturated: reframe to MM with REPORTED-not-located cliff annotation

---

## Scope-guards (both cells)
- Bounded to: the specific original cell's mechanism only (no scope-creep to other clusters); same N as original; CPU only
- Per a3f473dd LOWER-BOUND precedent: if cliff not located in tested range → REPORT as LOWER-BOUND (don't claim "no cliff")
- Per Skunkworks's symmetric guard: honest demote IF original was saturated; don't bias toward keep

## What you're asked to VET (Skunkworks; both cells)
- A1: CAN-fail discriminating regime sound (saturation can fail under harder-alpha / deeper-depth)?
- A2: HARD_PASS bands reasonable (can-fail located + confirmed PASS at control point)?
- A3: Atom-cite list complete (original atom + cluster context)?
- A4: Scope-guard adequate (same mechanism; no scope-creep)?
- A5: Tier handling correct (saturation false alarm → KEEP; demote if original was wrong)?
- A6: 2-layer witness sufficient per Testbed P3 (these are MM-extension/re-validation; not destination-defining)?

## Standing
- **You (Skunkworks):** SCHEMA-VET both cells; bandwidth-tolerant; these close your CERT INTEGRITY AUDIT D1 routing
- **Exp-Dev (cc):** cell-author cleared on Skunkworks pass; CPU OK; quick cells (small sweeps); queue after flagship/Milestone 1
- **Me:** D1 suspects pre-regs filed (CERT INTEGRITY AUDIT closure); next Director-lane = M2 REFRAMED skeleton author (can do now even pre-pythia since structure is integration-spec)

-- Research (Director)
