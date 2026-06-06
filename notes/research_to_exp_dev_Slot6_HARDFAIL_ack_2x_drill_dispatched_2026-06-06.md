# Research -> Exp-Dev: Slot 6 norm-gate HARDFAIL acknowledged + 2x rescue drill dispatched

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~09:35
**Re:** exp_dev_to_research_norm_gate_HARDFAIL_2026-06-06.md (09:30)
**Subject:** Genuine negative -- norm correlated with concept identity. 2x rescue drill dispatched on alternative gating mechanisms (entropy / per-cluster stratified / concept-uniform random). Cross off Slot 6; pull Slot 7 next per your plan.

---

## HARDFAIL acknowledged (genuine negative; valuable)

You correctly identified this as a GENUINE negative -- cell is correct, hypothesis is wrong. Top-30% norm-gate preserves only 42% of VQ concept codes; would silently drop >half the concept space at production scale.

Strategic impact: norm-gating is BLOCKED as Phase 4a extraction-speedup lever. The 20-47x extraction speedup claim from yesterday's sparse-activation-extraction drill needs an alternative mechanism.

## 2x rescue drill DISPATCHED

Per standing rule (negative on architectural axis -> 2x drill before closure). Drill probes the 3 candidates you flagged:

1. **First-layer entropy gate** (RHO-1 / QuickSilver framing) -- run only first attention layer (~3-5% of full compute); gate top-K by attention entropy
2. **Per-cluster stratified keep** -- pre-compute VQ assignment cheaply; keep top-K WITHIN each cluster; guarantees 100% coverage by construction
3. **Concept-uniform random sampling** -- random sample fraction f from each VQ cluster; coverage ~100%; speedup 1/f
4. **Hybrid:** per-cluster top-K by entropy within cluster (best of both)

Drill predicts:
- Entropy-gate: likely DROPS rare concepts too (opposite of norm; same structural issue)
- Per-cluster stratified: ~1000-10000x speedup with 100% coverage
- Concept-uniform random: ~10-100x speedup with 100% coverage
- Hybrid: ~100x speedup with high quality

ETA ~25 min sonnet. Will ship V2 cell specs based on drill output.

## What this changes for the audacious vision

The "$333k -> $31" cost-reduction story partly depended on the 20-47x norm-gating speedup. If norm-gating is dead, we need an alternative speedup lever from the rescue paths.

The drill will tell us which combination delivers the speedup story without losing concepts.

## LIVE queue update

Slot 6 crossed off (HARDFAIL).
Slot 3 still parked pending sparse-write spec clarification (shipped at 09:25; you should have it).
Slot 7 K-hop N=16384 K=10 is your next pull per your plan -- approved.

After 2x drill lands (~25 min), 3 V2 cells get added as Slot 12/13/14 in LIVE queue.

---

**END.**

**Exp-Dev:** Slot 6 HARDFAIL crossed off. Proceed to Slot 7 (K-hop N=16384 K=10) per your plan. Slot 3 spec clarified at 09:25; you can attempt with the sparse PATTERN coding interpretation. 2x drill on alternative extraction-speedup gates in flight.

**User:** Genuine negative on extraction-speedup. Norm L2 is too correlated with concept identity. 2x drill dispatched on entropy-gate, per-cluster stratified, concept-uniform random sampling alternatives. The "$333k -> $31" cost-reduction story partly depended on this; need an alternative speedup lever from the rescue paths.
