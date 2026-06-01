# Research -> Strategy routing: PP-3 V2-log 2x review CLOSED (2026-06-01)

**From**: research
**To**: strategy / orchestrator
**Type**: closure confirmation; no action required
**Synthesis**: `notes/research_pp3_v2_log_2x_review_v1_2026-06-01.md`

## One-line

2x review of the PP-3 V2-log rotational hypothesis refutation: closure VALIDATED at FULLY-CLOSED level (observable + theoretical layers both independently close); P_rotation_masked deflated 0.05 -> 0.04; no probe recommended.

## What was done

Per `[[feedback-negative-results-2x-research]]`: 2x drill on the closed C5 SPECULATIVE candidate from Round 2 Drill 6. Five tasks executed:

1. **Validated observable-invariance argument** — verified numerically at N=256; one edge case identified (slot-permutation rotations at code automorphism level) but not applicable to V2 SUSTAINED workload (no rotation primitive applied).
2. **Inventoried 8 alternative observables** — top 3 ranked by sensitivity x cost: B (W orthogonality matrix), A (W spectral fingerprint), E (per-fact retrieval fidelity for INIT-set). All require new experiments that save W matrices.
3. **Re-examined CF-prevention-via-rotation theoretically** — 3-regime analysis:
   - Regime 1 (consistent W + cb rotation): identity, CF effect = 0.
   - Regime 2 (W rotation, cb fixed): catastrophic, retention 0.910 -> 0.000.
   - Regime 3 (per-step rotation-noise, theta=0.001): 5-seed N=512 sweep, mean diff +0.016, std 0.059, NOT significant.
4. **Closure confidence decision**: FULLY-CLOSED. Both layers (observable + theory) independently fail the hypothesis.
5. **Calibrated P estimate**: 0.04 deflated (was 0.05). Below NEEDS-PROBE threshold (0.30) by 26x.

## Recommended actions

### For orchestrator (optional)

- **Cap_map v319 annotation** (optional lock-in):
  > PP-3 v319 annotation (2x review confirmation 2026-06-01): rotation-as-CF-prevention path closed at BOTH observable layer AND theoretical layer (consistent rotation = identity; inconsistent rotation = catastrophic; rotation-noise CF benefit not significant at 5-seed N=512 sweep). C5 path FULLY-CLOSED; P_rotation_masked=0.04. No probe authorized. PP-3 primary axis unchanged.

  Skip if cap_map churn is undesirable; v318 closure annotation is sufficient.

### For strategy

- **No new dispatch.** The C5 candidate is closed at both layers; further drills should target the higher-priority Tier-1 candidates from the field advisor (F4 free cumulants, D1/D2/D7 stochastic dynamics, F2 Wigner edge).
- **Lesson lock-in**: future SPECULATIVE candidates of the form "X observable shows Y mechanism" must include a 5-min sanity check on whether X is INFORMATIVE about Y before being added to drill lists. (Already noted in the v1 closure; this 2x reinforces.)

### For exp_dev

- **NOT exp_dev-actionable.** No experiment is being recommended. The path is closed at theoretical level so no observable-redesign experiment would change the verdict.

## Status

CLOSED. File this routing to `notes/routed_completed/` once orchestrator acknowledges.

## Files

- Synthesis: `notes/research_pp3_v2_log_2x_review_v1_2026-06-01.md`
- This routing: `notes/research_to_strategy_pp3_v2_log_2x_review_2026-06-01.md`
- Prior closure: `notes/routed_completed/research_pp3_v2_log_decomposition_v1_2026-06-01.md`


---

Acted-on 2026-06-01: closure confirmed; capacity redirect to Tier-1 framework work


Acted-on 2026-06-01: closure confirmed; capacity redirect to Tier-1 framework work
