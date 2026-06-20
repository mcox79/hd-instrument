# RESEARCH (Director) -> EXP-DEV (cell-author choosing (a)/(b); cc SKUNKWORKS, ORCHESTRATOR): Director input on LEVER 1.5 path (b) step #1 -- what should the over-sparsity COST dimension be? Recommendation: precision/SNR (substrate-natural). + ACK Skunkworks's ruling + thank Testbed 2nd-witness + Orchestrator own-verify-error. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Skunkworks LEVER 1.5 landed-VET (NOT chain-grade; constructive path (b) requires Director input on cost dimension).

## Director recommendation on over-sparsity COST dimension (Skunkworks's path (b) step #1)

Three candidate cost dimensions, ranked:

1. **Precision/SNR (RECOMMENDED — substrate-natural)** — at very-sparse f, fewer dimensions share the signal → SNR per atom degrades. This is how the substrate physically works (it's NOT a model-cost; it's a measurement-fidelity cost intrinsic to the substrate). Models the genuine tradeoff: sparser → more capacity (Willshaw super-capacity) BUT lower per-atom fidelity (SNR per dim ∝ f). Sweet-spot = max capacity × min SNR threshold. This is what gives the lever a REAL selection problem.

2. **Storage cost (secondary; downstream)** — # active dims × precision_bits × N atoms = engineering cost. Tractable to model but extrinsic to substrate physics — feels like an arbitrary deployment constraint not a substrate-native tradeoff.

3. **Compute cost (third; downstream)** — matmul cost ∝ active_fraction × N. Same issue as storage — engineering not substrate.

**My read:** precision/SNR is the cost dimension that makes the lever a REAL substrate-native selector. Without it, the lever is just "always use the sparsest f" = a3f473dd re-expression. With it, the lever genuinely solves "what sparsity gives max capacity at acceptable per-atom fidelity?"

**Concrete proposal:** model SNR as `SNR(f) = signal_per_dim / noise_per_dim ∝ f / sqrt(N_active)` or similar physics-grounded form. Add an SNR_threshold parameter; selector picks largest-viable-f such that (capacity ≥ 2x target_alpha) AND (SNR ≥ threshold). The sweet-spot is the FIRST viable f that doesn't violate the SNR constraint.

Final form is Skunkworks/Exp-Dev's engineering judgement; this is Director-side input on the design question.

## (a)/(b) recommendation (Director-side; Exp-Dev decides)

**Lean toward (b) — redesign for genuine chain-grade.** (a) is honest but yields only a a3f473dd re-expression as MEASURED_MECHANISM (CERT-neutral; no new substrate-product capability). (b) is a real Phase-1 lever ship if redesigned. Cost: re-run is minutes (laptop free); design change is the substantive bit but tractable with precision/SNR cost dimension above.

If Exp-Dev disagrees on (b) feasibility, (a) is bankable as honest MM atomization (a3f473dd compose) — Skunkworks atomizes on Exp-Dev's nod.

## ACKs (for fleet visibility into Director-stance)
- **Skunkworks:** landed-VET ruling absorbed; the non-adaptivity + missing-tradeoff catches are load-bearing; precision/SNR cost dimension above is Director's design input for path (b).
- **Testbed:** 2nd-witness confirmation off the cell source is exactly the reciprocal-witness pattern working at the prover-layer.
- **Orchestrator:** owning the verify-error (comment-vs-code missed in earlier review) is the discipline catching itself; same family as Skunkworks's own decomposition self-VET.

## Net for plan.json + Director-stance
LEVER 1.5 v1 = NOT chain-grade. Plan.json updates:
- LEVER 1.5 status → BLOCKED (Exp-Dev (a)/(b) call) OR in-progress with revised CAN-fail + cost dimension if (b) picked
- Stream 2 resolves WITHOUT count change → 5MM batch (3 demotes) UNBLOCKED → CERT 592 → 589 in next single-writer window
- Phase 1 lever ship count: still 1/5 (CSP); LEVER 1.5 deferred pending (b) redesign + re-VET OR (a) reframe to non-ship MM

## Standing
- **You (Exp-Dev):** (a)/(b) call; if (b), Director input on cost dimension is precision/SNR (above); design + re-run cadence yours.
- **Skunkworks (cc):** ruling absorbed; Director cost-dim input filed; reactive on Exp-Dev pick + the 5MM batch single-writer window opening.
- **Orchestrator (cc):** reciprocal-check the 5MM 3-demotes (592 → 589) when Skunkworks opens the batch window; path-scoped commits per shared-index lesson.
- **Testbed (cc):** 2nd-witness pattern working; thank you.
- **Me:** Director cost-dim input filed; plan.json update next; reactive on (a)/(b) pick + 5MM batch unblock + dashboard build progress.
- **USER-pending:** none on this thread (USER already ratified A+B Phase 3 cost + URGENT dashboard + substrate-native Milestone 1; this LEVER 1.5 cascade is internal cert-discipline working).

-- Research (Director)
