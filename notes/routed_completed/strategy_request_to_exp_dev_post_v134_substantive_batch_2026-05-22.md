# Strategy → Experiment Dev: Post-v134 substantive batch — concrete new directions

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~21:35 EDT
**Topic**: Pipeline empty + user signal "needs more strategy guidance not longer experiments"
**cap_map state**: v134 (commit `bce4958`)
**Trigger**: User pushback "exp dev needs more strategy guidance queue is empty and it's thinking it just needs to make longer experiments"

## Context

Cycle 134-135 delivered substantial substrate-physics + substrate-product gains:
- Cluster-trapping framework P=[0.55, 0.70] 8/8 constraint score (HIGHEST across 4 attempts)
- TWO substrate-novel readout primitives validated (VAMP-on-chain + backward-smoother-only)
- Backward-smoother-only ENVELOPE 2.5×-3×-4× wider than VAMP-on-chain
- Substrate-physics characterization: "forward-lossy + reverse-invertible"

But pipeline drained to queue=0 + current=None. NEW substantive directions
needed — not just longer experiments.

## Pending items from prior routings (verify pickup status first)

- `40f9e1f` cluster census Phase 1 (cycle 134) — appears not picked up; CRITICAL
- `c1acdbd` extreme_stress FULL (cycle 128) — still pending; long-overdue
- Bet A continual-edit FULL (smoke KILL cycle 132)
- Backward-smoother-only extreme_K FULL + MEGA FULL (cycle 135 smokes)

## PRIORITY 1 — Cluster census Phase 1 (FINAL substrate-physics gate)

Re-emphasize cycle 134 routing `40f9e1f`. Substrate-physics characterization
GATED on cluster census verdict (cluster-trapping P=[0.55, 0.70] candidate).
Cheap discriminator (~5-15 GPU-min) for the substrate-physics WHY question
after 4 attempts.

Most decisive single test from Research cycle 134 ADDENDUM:

**`wave14_cluster_census_init_compare_N65536_v1`** (~10-15 GPU-min):

Compare cluster membership across 5 init methods (forward_argmax / forward_soft
/ forward_resonator / backward_warmstart_argmax / backward_warmstart_resonator).

Predicted: forward methods concentrate on ~5-codeword cluster; backward methods
concentrate on true codeword. Verdict CLUSTER_TRAPPING_CONFIRMED if unique
codewords < 10 + top5_share > 0.9 for forward; true_codeword_share > 0.8 for
backward.

## PRIORITY 2 — Substrate-product hardening: Lane D E2E with backward-smoother-only

Backward-smoother-only has 2.5×-3×-4× WIDER envelope than VAMP-on-chain.
Substrate-product Demo 1 capstone should re-demonstrate end-to-end with
backward-smoother-only readout — substantively wider capability envelope.

**`wave14_lane_D_end_to_end_N65536_smoother_v1`** (~10-15 GPU-min):

Extend cycle 130 `wave14_lane_D_end_to_end_N65536_vamp_v1` (composed_acc=1.000)
to use **backward-smoother-only** readout at the multi-hop stage instead of
VAMP-on-chain. Demo 1 substrate-product story strengthens if E2E composed_acc
remains 1.000 with simpler primitive.

**Pass criteria**:
- LANE_D_E2E_SMOOTHER_PASS: composed_acc ≥ 0.50 at N=65536 with backward-smoother-only
- LANE_D_E2E_SMOOTHER_PARTIAL: composed_acc 0.30-0.50
- LANE_D_E2E_SMOOTHER_KILLED: composed_acc < 0.30

## PRIORITY 3 — Backward-smoother-only FULL completion

Cycle 135 smoke evidence STRONG (K=20K + MEGA broad envelope) but per
[[feedback-no-smoke]] + 15-anchor smoke→FULL precedent, FULL required for
substrate-product positioning.

**`wave14_chain_smoother_extreme_K_v1`** FULL (~30-60 GPU-min): K=10K + K=20K
at N=65536; confirms K=20K ceiling claim at FULL.

**`wave14_chain_smoother_mega_characterization_v1`** FULL (~30-60 GPU-min):
Broad joint envelope (3+ axis sweep) confirms substrate-product positioning
across operating space.

## PRIORITY 4 — Bet A continual-edit FULL (substrate-product completeness)

Cycle 132 smoke KILLED at N=65536 (edit_acc=1.0 but kept_acc=0.020 at 100
edits; 0 at 1000). Per cycle 102 smoke-not-predictive 15-anchor precedent,
FULL could improve OR degrade.

**`wave14_betA_continual_edit_N65536_v1`** FULL (~60-120 GPU-min):

Substrate-product implication:
- If FULL CONFIRMS smoke KILL: substrate-product positioning at N=65536 has
  NO continual-edit capability (cycle 98 architectural ceiling fails); Demo 1
  capstone still holds but continual-edit axis closed
- If FULL OVERTURNS smoke KILL: substrate-product story gains continual-edit
  axis at N=65536

## PRIORITY 5 — Demo 2 capstone (Lane C compliance + chain composition integration)

Cycle 121 Lane C compliance FULL PASS unlocked Demo 2 (browser extension
forensic-erase). But no end-to-end Demo 2 capstone demonstration exists yet.

**`wave14_demo_2_lane_C_multihop_N65536_v1`** (~30-60 GPU-min):

Integrates Lane C compliance (verifiable erase) with multi-hop chain composition
via backward-smoother-only readout at N=65536. Demonstrates substrate-product
forensic-erase + deep-chain compose end-to-end.

**Pass criteria**:
- DEMO_2_CAPSTONE_PASS: Lane C compliance probes ALL pass AND multi-hop
  acc_50hop ≥ 0.50 with backward-smoother-only readout
- DEMO_2_CAPSTONE_PARTIAL: one of Lane C OR multi-hop falls short
- DEMO_2_CAPSTONE_KILLED: both axes fail

Substrate-product implication: Demo 2 capstone DEMONSTRATED end-to-end
strengthens substrate-product positioning for Lane C wedge ($5-50M ARR per
cycle 121).

## PRIORITY 6 — Substrate-physics: W endpoint injection diagnostic

Directly tests the "(codeword → endpoint after L hops) map is INJECTIVE for
substrate W" claim that explains SMOOTHER_ONLY_WORKS.

**`wave14_W_endpoint_injection_diagnostic_v1`** (~10 GPU-min):

For all K=100 codewords at N=65536, run L-hop forward chain and record
endpoint. Verify endpoints are distinct (injective map) vs collapsed (cluster
trapping at the endpoint level).

**Pass criteria**:
- ENDPOINT_INJECTIVE: all K endpoints distinct; substrate forward map
  injective despite cluster trapping in argmax basin
- ENDPOINT_COLLAPSED: endpoints collapse into <K distinct states; cluster
  trapping happens at endpoint level (would contradict SMOOTHER_ONLY_WORKS)
- ENDPOINT_PARTIAL: K' < K distinct endpoints; structured collapse

Substantive substrate-physics gain: validates or refines reverse-invertibility
characterization.

## Total queue suggested

6 priorities; 11 experiments smoke + FULL = 22 runs; ~6-12 GPU-hours total.

Recommended priority ordering:
1. PRIORITY 1 cluster census (FINAL substrate-physics gate)
2. PRIORITY 4 Bet A FULL (substrate-product completeness)
3. PRIORITY 2 Lane D E2E with backward-smoother-only
4. PRIORITY 6 W endpoint injection diagnostic (cheap)
5. PRIORITY 3 backward-smoother-only extreme_K + MEGA FULL
6. PRIORITY 5 Demo 2 capstone

## Per [[feedback-two-experiments-per-cycle]]

Queue-depth ≥1 invariant — file all 6 priorities to maintain pipeline continuity.

## Per [[feedback-no-papers-product-only]]

All 6 priorities substrate-product oriented:
- P1+P6: substrate-physics characterization (feeds positioning narrative)
- P2+P3: substrate-product Demo 1 hardening with wider-envelope primitive
- P4: substrate-product completeness on continual-edit axis
- P5: substrate-product Demo 2 capstone demonstration

## What I need from you

1. Verify cycle 134 routing `40f9e1f` (cluster census) pickup status
2. Verify cycle 128 routing `c1acdbd` extreme_stress FULL status
3. Queue 6 priority experiments per ordering (or your preferred order)
4. Flag infrastructure issues (cluster census needs init-method comparison code;
   Lane D E2E needs backward-smoother-only readout integration into Lane D
   pipeline; Demo 2 capstone needs Lane C compliance + multi-hop integration)

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 60-120 min for substantive priorities.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
