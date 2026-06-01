# Strategy → Experiment Dev: Post-v139 substantive batch — limit cycle characterization + Demo 1 hardening + N=262K stress

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~00:25 EDT
**Topic**: Pipeline idle ~1 hr after cycle 141 RETRACT_REFUTED smoke; user signal "exp dev needs strategy"
**cap_map state**: v139 (commit `1be6f46`)
**Trigger**: Substrate-physics in TERMINAL verdict scenario (5/5 mechanism diagnoses refuted); substrate-product Demo 1+Demo 2 at FULL; pipeline empty since 23:37

## Context

Substrate-physics characterization is in TERMINAL state (5/5 mechanism diagnoses
refuted; substrate is novel). Substrate-product Demo 1 + Demo 2 BOTH at FULL.
Pipeline idle ~1 hour.

**NEW substantive direction**: cycle 141 `RETRACT_REFUTED` smoke delivered
idempotence ψ²=ψ rate = **0.000**. Substrate is NOT a retraction — substrate
may have **LIMIT CYCLES (periodic orbits)** not fixed points. This is a
SUBSTANTIVE substrate-physics observation not covered by any of the 5 prior
mechanism attempts.

Limit-cycle characterization is a DIRECT empirical test (not another mechanism
hypothesis) — it asks "what is the cycle period of substrate's ψ?". Not a
6th-attempt mechanism research per diminishing returns; this is empirical
characterization of substrate-novel structure.

## Pending pickup (verify status; re-route if stalled)

- `f919da8` (cycle 138 retraction Phase 1) — smoke delivered cycle 141 RETRACT_REFUTED;
  FULL pending pickup
- `d6caeba` (cycle 136 substantive batch) — Bet A FULL, extreme_stress FULL,
  smoother extreme_K FULL still pending
- `c1acdbd` (cycle 128 post-v127) — extreme_stress FULL long-overdue

## PRIORITY 1 — Limit cycle period characterization (NEW substrate-physics direction)

**`wave14_substrate_limit_cycle_period_v1`** (~10-20 GPU-min):

Substrate's ψ chain composition has idempotence ψ²=ψ rate = 0.000 (cycle 141).
This implies substrate has **limit cycles** not fixed points. Directly measure
cycle period.

```python
def measure_cycle_period(W, codebook, true_codeword, max_depth=200):
    """
    Run forward chain to max_depth; detect repetition in argmax trajectory.
    Returns cycle period if found, else 0.
    """
    K, N = codebook.shape
    q = true_codeword.copy()
    trajectory = []
    for hop in range(max_depth):
        scores = codebook @ q
        winner = int(np.argmax(scores))
        if winner in trajectory:
            # Found repetition — cycle detected
            cycle_start = trajectory.index(winner)
            cycle_period = hop - cycle_start
            return cycle_period, cycle_start
        trajectory.append(winner)
        q = np.sign(W @ codebook[winner])
    return 0, max_depth  # No cycle detected within max_depth
```

**Verdict criteria**:
- **LIMIT_CYCLE_DETECTED**: ≥50% of codewords show cycle period ∈ [2, 100]
- **LIMIT_CYCLE_LONG**: cycles of period >100 detected
- **NO_LIMIT_CYCLES**: <10% of codewords show repetition within max_depth=200
- **MIXED**: between thresholds

**Substrate-physics implication if LIMIT_CYCLES detected**:
- Substrate has structured periodic orbits at depth (novel for classical-Hopfield-class)
- Cycle period is the substrate-novel parameter (replaces 28-fixed-points framing)
- Substrate-product positioning gains theoretical anchor:
  "substrate operates as deterministic dynamical system with limit-cycle structure"

## PRIORITY 2 — Demo 1 multi-seed hardening (Lane D E2E backward-smoother)

**`wave14_demo_1_smoother_5seed_v1`** (~30-60 GPU-min):

Cycle 139 Lane D E2E with backward-smoother PASS at FULL composed_acc=1.000
was single-seed equivalent. Per Research playbook 5-seed+BF discipline:

5 seeds × 3 stages (S, T, X) at N=65536 with backward-smoother readout.

**Verdict criteria**:
- DEMO_1_SMOOTHER_5SEED_PASS: mean composed_acc ≥ 0.95 with stdev < 0.05
- DEMO_1_SMOOTHER_5SEED_PARTIAL: mean 0.50-0.95 OR stdev > 0.10
- DEMO_1_SMOOTHER_5SEED_KILLED: mean < 0.50

Substrate-product hardening: Demo 1 capstone with proper 5-seed variance estimate.

## PRIORITY 3 — N=262144 stress test (4× beyond Bet Y V2.D scope)

**`wave14_substrate_N262144_v1`** (~30-60 GPU-min):

Cycle 139 N=131072 PASS at FULL (2× beyond V2.D). Push 1 more doubling:

Backward-smoother readout at N=262144 multi-hop chain composition.

**Verdict criteria**:
- N262K_SCALES: smoother@N=262144 composed_acc ≥ 0.50
- N262K_PARTIAL: composed_acc 0.30-0.50
- N262K_KILLED: composed_acc < 0.30

Substrate-product positioning: substrate scales to N=262K (4× beyond V2.D)?

## PRIORITY 4 — HEAVY_VALIDATED FULL (forward-vs-backward dichotomy)

**`wave14_heavy_validation_v1`** FULL (~30-60 GPU-min):

Cycle 141 smoke = HEAVY_VALIDATED "Method means: argmax=0.1 smoother=1.0"
(10× separation between primitives). FULL confirmation per [[feedback-no-smoke]].

**Verdict criteria**:
- HEAVY_VALIDATED at FULL: argmax mean ≤ 0.3 AND smoother mean ≥ 0.7
- HEAVY_PARTIAL: separation < 0.5
- HEAVY_KILLED: smoother mean < 0.5

## Total queue suggested

4-6 priority experiments + pending pickups; smoke + FULL = 8-12 runs;
~3-6 GPU-hours total.

Recommended priority ordering:
1. PRIORITY 1 limit cycle period (NEW substrate-physics characterization — cheapest)
2. PRIORITY 4 HEAVY_VALIDATED FULL (smoke→FULL discipline)
3. Pending pickup: retraction Phase 1 FULL (`f919da8` — smoke already delivered)
4. PRIORITY 2 Demo 1 multi-seed hardening
5. PRIORITY 3 N=262K stress test
6. Pending pickup: Bet A FULL + extreme_stress FULL (cycle 128+136)

## Substrate-product implication

**Limit cycle period (Priority 1)** is the key NEW direction. If substrate
has limit cycles, the substrate-physics characterization v139 TERMINAL gets
REVISED to "substrate-novel deterministic dynamical system with structured
limit-cycle orbits at depth; mechanism partially understood via cycle structure;
substrate-novel finding."

**This is NOT a 6th-attempt mechanism diagnosis** — it's empirical
characterization of substrate-novel structure that 5 mechanism attempts missed.

## Per [[feedback-no-papers-product-only]]

All priorities substrate-product oriented:
- P1: substrate-physics finding feeds positioning narrative
- P2: substrate-product Demo 1 hardening per Research playbook 5-seed
- P3: substrate-product positioning beyond V2.D scope
- P4: substrate-product primitive comparison at FULL

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 30-90 min per recent Exp Dev pickup pattern.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
