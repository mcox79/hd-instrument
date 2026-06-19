# exp_dev hand-off: Field-A reservoir-computing Lyapunov spectrum

**Filed:** 2026-05-24 by orchestrator (v192 paired commit, Ship 2).
**Status:** READY for exp_dev pickup. Pre-reg + script + queue entry owned by exp_dev.

---

## WHAT

Measure the substrate's Lyapunov spectrum at the operating point used for Bet B retention runs. Compare to reservoir-computing edge-of-chaos signatures (largest Lyapunov exponent λ_1 ~ 0 at edge of chaos; spectrum tails follow predictable decay in reservoir-computing literature).

## WHY

The 5-new-fields delivery at `notes/research_R_PRIME_directions_2026-05-24.md` flags **Field-A (reservoir computing)** as the highest-leverage adjacent framework. Substrate dynamics look like an echo-state reservoir with HD readout; Lyapunov spectrum + memory-capacity curves are mature literature with closed-form predictions.

If sub-substrate matches reservoir-computing edge-of-chaos signatures (λ_1 near 0; spectrum decay matching Jaeger-style echo-state predictions), this opens the echo-state mapping — large algorithmic payoff including:
- Memory-capacity closed-form from reservoir-computing theory
- O(N log N) algorithmic accelerators via reservoir-state recurrence
- Connection to broader dynamical-systems framework

If substrate is firmly chaotic (λ_1 >> 0) or firmly contractive (λ_1 << 0), Field-A is ruled out and we save a Week-2 drill.

Per [[feedback-periodic-scope-expansion]] this is the cross-framework cadence drill of the cycle (~once per 24-48h dispatch on a framework different from current AI-memory framing).

## CONTEXT POINTERS

- `notes/research_R_PRIME_directions_2026-05-24.md` — Field-A reservoir-computing spec
- `notes/substrate_capability_map.md` v192 block — current Bet B retention operating points
- Existing exp_a4_hebbian (data/exp_a4_hebbian) — Hebbian-update dynamics on substrate may already produce Lyapunov-relevant trajectories
- Literature anchors: Jaeger 2001 echo-state networks; Maass 2002 liquid state machines; Boedecker et al 2012 edge-of-chaos reservoirs
- Lyapunov spectrum estimation: Benettin et al 1980 standard method; QR-decomposition variant for high-dim systems

## CONTRACT (deliverable shape)

- exp_dev decides: which substrate operating point(s) to probe (e.g., Bet B retention runs at retA=0.954 vs retA=0.600 vs retA=0.74).
- exp_dev decides: Lyapunov spectrum estimation method (Benettin / QR / Jacobian-trace ratio).
- exp_dev decides: how many exponents to estimate (top-k or full spectrum).
- exp_dev decides: HARD-PASS / HARD-FAIL / MIDDLE bands. Suggested SHAPE (exp_dev refines):
  - HARD-PASS: λ_1 within +/-0.05 of 0 at the operating point; spectrum decay matches reservoir-computing power-law within 15%.
  - HARD-FAIL: |λ_1| > 0.2 (firmly chaotic or firmly contractive).
  - MIDDLE: between.
- Pre-reg file in `notes/preregs/` ahead of FULL run.
- Smoke first.
- CPU-suitable (matrix-spectrum diagnostic; not training-heavy).

## AUTONOMY DECLARATION

You decide all design parameters: operating point(s), estimation method, exponent count, threshold bands, queue placement, ETA. Do NOT ship parameter grids designed in this hand-off.

## DISCIPLINE CITATIONS

- per [[feedback-no-experiment-design-in-prompts]] — this hand-off names task SHAPE, not parameters
- per [[feedback-periodic-scope-expansion]] — Field-A is the cross-framework drill of the cycle
- per [[feedback-dont-dismiss-adjacent-methods]] — reservoir-computing is mathematically adjacent (echo-state + HD-readout); dispatch rather than pre-judge
- per [[feedback-lit-scan-calibration-penalty]] — substrate is in uncharted regime for reservoir-computing; deflate P estimates by 0.15-0.25 in pre-reg
- per [[feedback-no-smoke]] — honest reread of label=msg=data after FULL; pre-reg the threshold bands explicitly

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
