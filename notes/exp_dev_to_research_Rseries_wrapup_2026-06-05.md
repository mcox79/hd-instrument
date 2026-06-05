# Exp-Dev -> Research: R-series wrap-up (R2 HP; R6 D-RIP super-additive REFUTED; R1/R5 deferred)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~03:45

## R2 sparse-resonator block-local: HARD_PASS (full, K=26). Block-local sum-bind enables high-K (dense caps ~7-9). VALIDATED.

## R6 B2-storage x sparse-resonator: HARD_FAIL -> D-RIP SUPER-ADDITIVE REFUTED for this pairing (registered, queued).
Tested both DG-expand-store (lossy roundtrip) AND direct sparse auto-assoc store. Both: K_max(res-alone)=8 ->
K_max(B2+resonator)=0. ROOT CAUSE: storing M composites in a shared auto-assoc W creates CROSSTALK that corrupts
the precise BLOCK structure the resonator needs (recall returns comp + crosstalk from other stored composites ->
block cleanup picks wrong codes). B2-storage and block-local-resonator-recovery are INCOMPATIBLE: storage degrades
the structure recovery requires. The D-RIP "orthogonal sparse-axis super-additive" prediction does NOT hold here --
storage and structured-recovery interfere rather than compose. (Consistent w/ the broader pattern: not all orthogonal
pairings super-add; some interfere -- like same-axis subsumption.) Honest negative; pressure-tested 2 storage variants.

## R1 4-modulator: DEFERRED-FINAL (cf-RPE error-gating already reinforces recurring-important via re-storage; no gap on recurrence tasks).
## R5 B2+B8: DEFERRED -- B8 is a logit-BRIDGE not a capacity primitive; its contribution to M_crit is undefined.
   To build R5 cleanly I need: what EXACTLY does B8 add to storage capacity? (B8's validated metric is r=sqrt(K/V)
   reconstruction-correlation, not M_crit.) If R5 is really "does the B8 logit-residual readout preserve r while B2
   raises M_crit" -> that's two independent metrics, not a composition. Please specify the single shared capacity claim.

## R-series outcome: R2 HP (high-K via block-local) + 3 honest negatives/deferrals. The composition taxonomy holds:
orthogonal-axis composition is multiplicative on CAPACITY (B2xB4=125K validated) but NOT on every pairing/metric --
storage x structured-recovery interferes (R6); error-axis modulators don't stack (R1); cross-space pairs need a shared metric (R5).
**END.**
