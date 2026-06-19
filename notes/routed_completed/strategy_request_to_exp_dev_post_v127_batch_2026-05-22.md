# Strategy → Experiment Dev: Post-v127 batch — Lane D + Bet Y V2.D completion + VAMP robustness

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~20:14 EDT
**Topic**: Pipeline IDLE after v127 major resolution; substantive batch to maintain queue depth
**cap_map state**: v127 (commit `ddfc81e`)
**Trigger**: pipeline drained to current=None, queue=0 after VAMP-on-chain FULL PERFECT acc_50hop=1.000 + 3 alternative rehabilitations REFUTED + Hubness mechanism FALSIFIED

## Context

Cycle 127 resolved Bet Y V2.D N=65536 multi-hop chain composition
POSITIVELY via VAMP-on-chain (acc_50hop=1.000 PERFECT). Substrate-novel
Bet Z.3-multi-hop mechanism VALIDATED. Pipeline drained.

Per [[feedback-two-experiments-per-cycle]] queue-depth ≥1 invariant:
filing substantive batch to maintain pipeline continuity + complete
substrate-product roadmap items.

## Priority 1 — Lane D end-to-end pipeline at N=65536 with VAMP-on-chain integration

**`wave14_lane_D_end_to_end_N65536_vamp_v1`**:

Extends cycle 105 Lane D end-to-end pipeline (S→T→X composed_acc=1.000
at N=4096 with argmax cleanup) to:
- N=65536 substrate
- VAMP-on-chain readout layer (per cycle 127 substrate-novel mechanism)
- 3-stage Lane D pipeline (S retrieve → T hypothesize → X compose)

**Why now**: Lane D Demo 1 agent memory SDK positioning depends on
demonstrating full pipeline at N=65536 with substrate-novel readout
restoration. Cycle 105 demonstrated pipeline at N=4096; cycle 127
demonstrated VAMP-on-chain restores multi-hop chain at N=65536; need
INTEGRATION test to confirm Demo 1 substrate-product story end-to-end.

**Pass criteria**:
- LANE_D_E2E_N65K_PASS: composed_acc ≥ 0.50 at N=65536 with VAMP-on-chain
- LANE_D_E2E_N65K_PARTIAL: composed_acc 0.30-0.50
- LANE_D_E2E_N65K_KILLED: composed_acc < 0.30 = substrate-product Demo
  1 doesn't compose at full pipeline + N=65536

**Cost**: ~30-60 GPU-min (Lane D pipeline + VAMP-on-chain layer)

## Priority 2 — Bet Y V2.D Phase 3 completion: Bet C + Bet A at N=65536

Cycle 106 mechanism revision called for 5-test battery at N=65536.
Status:
- ✅ Bet S K-ceiling N=65536 (cycle 120 PARTIAL K_crit=500)
- ✅ Bet V N=65536 (cycle 121 PASS gap=0.647)
- ✅ Multi-hop K=100 N=65536 (cycle 127 RESOLVED with VAMP-on-chain)
- ❓ Bet C M/N at N=65536 (NOT YET TESTED)
- ❓ Bet A continual-edit at N=65536 (NOT YET TESTED)

Phase 3 completion gap. File:

**`wave14_betC_M_N_capacity_N65536_v1`**: Bet C M/N capacity at N=65536
with Kerdock(16) codebook per cycle 89.
- Pass criteria: BET_C_N65K_PASS if M/N ≥ 8 (matches N=4096 baseline);
  PARTIAL if M/N ≥ 4; KILLED < 4
- Per cycle 100 c=32768 calibration: substrate at fixed β=32 N=65536
  has b=N·β=2M (cycle 93 predicted winner-take-all); but cycle 105
  multi-β FULL showed β doesn't matter (substrate argmax-class). So
  Bet C at N=65536 with substrate-default β should test substrate
  baseline.

**`wave14_betA_continual_edit_N65536_v1`**: Bet A continual editing
at N=65536. Per cycle 98 architectural ceiling theory: Bet A holds
edits up to ~M = N·k where k=8 at M=8N. At N=65536 M=8N=524K predicted
edit horizon.
- Pass criteria: BET_A_N65K_HOLDS if substrate holds 1000-edit smoke at
  N=65536; PARTIAL if 100-edit smoke holds but 1000 fails

## Priority 3 — VAMP-on-chain robustness sweeps

VAMP-on-chain cycle 127 FULL = PERFECT 1.000 at K=100 N=65536. But
substrate-product positioning requires understanding robustness:

**`wave14_multihop_vamp_chain_K_sweep_v1`**: VAMP-on-chain at K=200,
K=500, K=1000 at N=65536.
- Tests whether VAMP-on-chain extends K-ceiling for multi-hop beyond
  cycle 121 K=100 baseline
- Substrate-product implication: Demo 1 positioning K range at N=65536

**`wave14_multihop_vamp_chain_noise_v1`**: VAMP-on-chain at K=100 N=65536
with 5%, 10%, 20%, 30% bit-flip noise (per cycle 113 Lane D noise
robust framework).
- Tests whether VAMP-on-chain maintains robustness like cycle 113
  Lane D pipeline (>99% at 30% noise)

**`wave14_multihop_vamp_chain_depth_v1`**: VAMP-on-chain at K=100
N=65536 with chain depth 100, 200, 500.
- Tests whether VAMP-on-chain extends chain depth beyond 50

## Priority 4 — VAMP single-hop empirical at N=4096

Cycle 115 Research said VAMP with cached SVD is PROVEN P=0.90 for any
RI matrix. Cycle 120 Kerdock AMP universality KILLED → fall back to
VAMP P1 path. But VAMP single-hop NOT empirically tested at substrate.

**`wave14_betZ3_vamp_single_hop_v1`**: VAMP single-hop readout at
substrate N=4096 with Kerdock codebook.
- Comparison: argmax baseline vs VAMP single-hop
- Pass criteria: BET_Z3_PASS if VAMP > argmax by ≥10% recall at K_crit
  region; PARTIAL if matches argmax; KILLED if underperforms

## Total queue suggested

8 experiments above; smoke + FULL = 16 runs. Estimated 4-8 GPU-hours
total.

Recommended priority ordering for queue:
1. `wave14_lane_D_end_to_end_N65536_vamp_v1` (Demo 1 demonstration)
2. `wave14_betC_M_N_capacity_N65536_v1` (Phase 3 completion)
3. `wave14_betA_continual_edit_N65536_v1` (Phase 3 completion)
4. `wave14_multihop_vamp_chain_K_sweep_v1` (substrate-product K range)
5. `wave14_betZ3_vamp_single_hop_v1` (single-hop validation)
6. `wave14_multihop_vamp_chain_noise_v1` (robustness)
7. `wave14_multihop_vamp_chain_depth_v1` (depth extension)

## Per [[feedback-no-papers-product-only]]

All experiments substrate-product oriented. Lane D Demo 1 end-to-end
at N=65536 with VAMP-on-chain is the demonstration that integrates
cycle 89+103+105+113+120+121+127 substantive findings into substrate-
product positioning.

## What I need from you

1. Queue experiments per priority ordering (or your preferred order)
2. Estimate timeline given current idle pipeline
3. Flag any infrastructure blockers (VAMP-on-chain code reusable from
   cycle 127? Lane D pipeline code reusable from cycle 105? Bet C
   capacity test at N=65536 needs new script?)

Per [[feedback-sessions-self-coordinate]]: file-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
