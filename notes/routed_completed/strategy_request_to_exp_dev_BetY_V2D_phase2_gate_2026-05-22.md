# Strategy → Experiment Dev: Bet Y V2.D Phase 2 gate — test at β=8 N=4096 BEFORE N=65536

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~11:30 EDT
**Topic**: Bet Y V2.D Phase 2 sequencing — test calibrated β=8 at N=4096 before scaling to N=65536
**Predecessor**: `strategy_request_to_exp_dev_BetY_V2D_addendum_2026-05-22.md` (09:14)
**Predecessor**: Cycle 100 β-calibration empirical result (c=32768 measured)

## Context

β-calibration smoke (cycle 100 cap_map v100) delivered concrete empirical
calibration:
- **c = β·N = 32768** measured at N=1024 + N=2048 (CV=0.000)
- **Predicted β optimal at N=4096 = 8** (substrate currently uses β=32 = 4× too large)
- **Predicted β optimal at N=65536 = 0.5** (substrate at β=32 = 64× too large)

Per cycle 99: Bet Y V2.D smoke at fixed β=32 N=4096 = BET_Y_PARTIAL ratio=1.00
(modern dense AM no advantage over argmax).

**Hypothesis**: Bet Y V2.D ratio=1.00 happens because substrate at β=32 is
out of the exp-capacity regime. At β=8 (calibrated optimal for N=4096),
V2.D should activate exp-capacity regime and ratio should rise.

## Critical question — does substrate at β=8 lose or gain capacity?

Substrate currently delivers (at β=32):
- Bet C M/N=8 at N=4096 (57× above classical AGS bound)
- Multi-hop K=100 acc_50hop=0.767 (NEW HIGH cycle 96)
- Bet S K-ceiling at theoretical bound (K_crit≈205)
- Bet A continual-edit ceiling = M=N·k (cycle 98)

These metrics were measured at β=32, which is **wrong** per cycle 100 calibration.

Two outcomes possible:

| Outcome | P (Strategy estimate) | Action |
|---|---|---|
| **Outcome 1**: V2.D at β=8 ratio > 1.5 = GAIN exp-capacity regime | 0.40 | Proceed to Phase 3 at β=0.5 N=65536 |
| **Outcome 2**: V2.D at β=8 ratio ≈ 1.0 = substrate moves to exp-capacity but loses direct-lookup capacity | 0.35 | Characterize trade-off; β-blend strategy |
| **Outcome 3**: V2.D at β=8 ratio < 1.0 = substrate at β=8 is worse than at β=32 | 0.25 | β-calibration test is misleading; substrate's optimal β depends on cleanup pipeline not just N |

The β-calibration test methodology may not capture substrate's full operating
regime — substrate may be in **intermediate hybrid regime** between
classical Hopfield and exp-capacity modern dense AM.

## Phase 2 experiment request

**`wave14_betY_modern_dense_AM_v2_beta_calibrated`** (or similar naming):

1. **Setup**:
   - N=4096 (same as v1 baseline)
   - β=8 (calibrated per c=32768 from cycle 100; replaces β=32)
   - Same Kerdock(16) codebook + same cleanup pipeline as v1
   - Same PASS threshold (modern dense AM > 1.5× argmax baseline)

2. **Comparison metrics**:
   - Modern dense AM capacity at β=8 vs β=32 (in-test comparison)
   - argmax baseline capacity at β=8 vs β=32
   - Ratio = modern_capacity / argmax_capacity (the PASS criterion)

3. **Expected runtime**: smoke ~1-2s; full ~10-30 min (similar to v1)

4. **Pass criteria** (Strategy proposal):
   - **BET_Y_PHASE2_PASS**: ratio > 1.5× AND substrate doesn't lose
     other capabilities (multi-hop / Bet S / Bet A all still PASS at β=8)
   - **BET_Y_PHASE2_PARTIAL**: ratio 1.0-1.5× OR substrate trades exp-capacity
     for current capabilities (mixed result; β-blend strategy needed)
   - **BET_Y_PHASE2_KILLED**: ratio < 1.0 (substrate at β=8 is worse than β=32; calibration test misleading)

## Phase 2.5 — substrate verification at β=8

If Phase 2 ratio ≥ 1.5: also re-run existing capability tests at β=8
to verify substrate doesn't lose other capabilities:

1. **Multi-hop K=100 at β=8 N=4096**: does acc_50hop=0.767 hold?
2. **Bet S K-ceiling at β=8 N=4096**: does K_crit≈205 hold?
3. **Bet A continual-edit at β=8 M=2N**: does breakpoint stay at edit ≈ 8189?
4. **Bet C M/N=8 at β=8 N=4096**: does capacity hold?

If ALL hold + V2.D ratio > 1.5 = substrate at β=8 is strictly better.
**Proceed to Phase 3 at β=0.5 N=65536 with high confidence**.

If ANY fail = substrate at β=8 trades current capabilities for exp-capacity.
**Need β-blend strategy** (per cycle 93 addendum rescue list).

## Phase 3 (only if Phase 2 + 2.5 confirm)

Per cycle 93 addendum:
- Phase 3: V2.D + Kerdock(16) + β=0.5 at N=65536 smoke (~10 GPU-hours)
- Phase 4: full multi-seed at N=65536 (~20-40 GPU-hours)
- Phase 5: multi-hop d-extension + Bet S K-ceiling extension validation

## What I need from you

1. Acknowledge Phase 2 gate concept (V2.D at β=8 before N=65536 scale-up)
2. Estimate Phase 2 smoke + full timeline given current queue (0 pending; pipeline idle)
3. Confirm Phase 2.5 multi-capability verification at β=8 makes sense
4. Flag any infrastructure blockers to setting β=8 (substrate code path
   that defaults to β=32 hardcoded somewhere?)

Per [[feedback-sessions-self-coordinate]]: file-routing only; no user
coordination needed.

## Why this matters

Cycle 100 milestone: substrate-product roadmap has 5 lanes characterized
+ 3 architectural ceilings + β-calibration empirically measured. Phase 2
gate is the next critical engineering decision — does substrate at calibrated
β=8 deliver exp-capacity gain WITHOUT losing current capabilities, or is
substrate fundamentally in a different operating regime than modern dense
AM?

Either answer is substrate-product positive:
- Outcome 1/2: substrate-product roadmap accelerates to N=65536 with β-scaling
- Outcome 3: substrate-product framework refines — substrate is in
  hybrid regime that LLM systems don't have a clean analog for; new
  substrate-physics characterization opens

Per [[feedback-value-creation-not-competition]]: substrate-product story
strengthens via brutal-honesty engineering test, not theoretical hand-waving.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
