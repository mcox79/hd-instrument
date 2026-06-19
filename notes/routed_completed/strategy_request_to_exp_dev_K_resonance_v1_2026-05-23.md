# Strategy → Experiment Dev: K=1000 anomaly + K-resonance structure investigation

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~06:50 EDT
**Topic**: K=1000 FIXED POINTS anomaly from cycle 159 — investigate K-resonance structure
**cap_map state**: v143 (commit `c30d48f`)
**Trigger**: User signal "exp dev needs strategy guidance"; cycle 159 PERIOD_K_SCALES FULL revealed K=1000 anomaly (period 1 FIXED POINTS not cycles)

## Context

Cycle 159 limit cycle K-sweep FULL revealed substrate-novel **K-RESONANCE structure**:
- K=100: period 3 (cycle)
- K=500: period 12 (cycle)
- **K=1000: period 1 (FIXED POINTS — anomaly)**
- K=5000: period 42 (cycle)

K=1000 produces qualitatively different substrate behavior — codewords map
to themselves under W^L rather than entering cycles. This is a substrate-novel
finding worth characterizing.

## PRIORITY 1 — K=1000 anomaly boundary

**`wave14_K_resonance_fine_sweep_v1`** (~10 GPU-min):

Fine K-sweep around K=1000 to find anomaly boundary:
- K ∈ {800, 900, 950, 1000, 1050, 1100, 1200, 1500, 2000}
- Measure median cycle period at each K
- Find boundary of fixed-point region

**Verdict criteria**:
- K_RESONANCE_NARROW: only K=1000 (or single K) shows period 1
- K_RESONANCE_BAND: range of K values show period 1 (e.g., K=950-1050)
- K_RESONANCE_BROAD: many K values show period 1

## PRIORITY 2 — Other K resonances?

**`wave14_K_resonance_full_sweep_v1`** (~20 GPU-min):

Wide K-sweep to find OTHER K-resonance points:
- K ∈ {64, 128, 256, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 8000, 10000}
- Measure median cycle period at each K
- Identify all K values producing period 1 (or period close to 1)

**Verdict criteria**:
- K_RESONANCE_MULTIPLE: multiple K values show period 1 (substrate has multiple resonances)
- K_RESONANCE_SINGULAR: only K=1000 (or single K) is anomalous
- K_RESONANCE_PATTERN: structured pattern (e.g., powers of 2, prime K values)

## PRIORITY 3 — K=1000 substrate-product implications

**`wave14_demo_1_K1000_smoother_v1`** (~10 GPU-min):

If substrate has FIXED POINTS at K=1000, does Demo 1 work differently at K=1000?
- Run Lane D E2E pipeline at N=65536 K=1000 with backward-smoother readout
- Compare composed_acc vs cycle 139 K=5000 baseline (acc=1.000)

**Verdict criteria**:
- DEMO_1_K1000_PASS: composed_acc ≥ 0.95 (same as cycle 139 K=5000)
- DEMO_1_K1000_BETTER: composed_acc > 0.95 with smoother performance
- DEMO_1_K1000_DEGRADED: composed_acc < 0.95 (fixed-point structure affects Demo 1)

## PRIORITY 4 — Forward retrieval at K=1000

**`wave14_forward_argmax_K1000_v1`** (~10 GPU-min):

If substrate has fixed points at K=1000, does forward argmax retrieval work
DIFFERENTLY at K=1000?
- Run forward argmax retrieval at N=65536 K=1000 multi-hop chain
- Compare acc_50hop vs cycle 121 K=100 baseline (acc_50hop=0.217)

**Verdict criteria**:
- FORWARD_K1000_RESCUED: acc_50hop ≥ 0.50 (fixed-points enable forward retrieval)
- FORWARD_K1000_BOUNDED: acc_50hop 0.20-0.50 (some improvement)
- FORWARD_K1000_SAME: acc_50hop similar to K=100 (no improvement)

## Pending pickup (re-emphasize)

- HEAVY_VALIDATED FULL (cycle 143 P4)
- Retraction Phase 1 FULL (cycle 138)
- Bet A continual-edit FULL (cycle 136)
- extreme_stress FULL (cycle 128 + cycle 156 routing)
- Cycle 156 batch (Demo 2 5-seed, N=524K, head-to-head VAMP/smoother, cross-task 5-seed)

## Total queue suggested

4 K-resonance priorities + pending pickups; smoke + FULL = 8-12 runs;
~2-4 GPU-hours total.

Recommended priority ordering:
1. PRIORITY 1 K=1000 anomaly boundary (cheapest; finest resolution near K=1000)
2. PRIORITY 4 Forward retrieval at K=1000 (substrate-product implication)
3. PRIORITY 2 K=1000 wider sweep (find other resonances)
4. PRIORITY 3 Demo 1 at K=1000 (substrate-product capability)
5. Pending pickups

## Substrate-physics implication

If K=1000 anomaly extends to other K values (K_RESONANCE_MULTIPLE), substrate
has structured K-resonance pattern — likely connected to Kerdock 4-coset
codebook algebraic structure. This would be a substrate-novel finding
distinguishing substrate from generic classical-Hopfield-class.

If K=1000 is unique (K_RESONANCE_SINGULAR), substrate has specific K=1000
algebraic alignment but the resonance isn't generic.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 60-120 min.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
