# Exp-Dev OVERNIGHT SUMMARY (for user, 2026-06-04 ~23:00 -> 2026-06-05 ~03:00)

## HARD_PASS landed overnight (the substrate cognitive-core narrative is now empirically anchored)
1. **Tier-6 Phase D CPU FULL** -- substrate-intrinsic LLM training: BPC<=1.20x baseline AND >=2x speedup AND
   audit-during-training operational. (GPU was MIDDLE = hardware artifact; CPU is the real speedup wedge.)
2. **Tier-4 substrate-attention IN Pythia-160M** -- training-stable (ppl 1.06x, grad<1, no entropy collapse). Bridge-D anchor.
3. **audit-core-v2 on REAL Pythia residuals** -- deletion-cert 0.98 + drift 11x. HIPAA/GDPR product wedge.
   KEY INSIGHT: real (correlated) activations must be DECORRELATED (PCA-whiten) before storage for clean deletion
   (v1 raw got C2=0.50; whitening rescued it to 0.98).
4. **CCC-AGGRESSIVE** -- VSA reasoning (analogical 1.0, counterfactual 0.94, cross-domain 1.0, recall 1.0).
5. **CCC-2 substrate-only structured QA** -- multi-relation KG traversal, exact-match >=70% @ K=3 (PATH-B ceiling).
6. **NEW EXP 3 resonator/cleanup-augmented depth** -- 6x depth boost (drill predicted 2.7x).
7. **NEW EXP 5 hierarchical-D saturation** -- capacity scales linearly to D>=20.
8. **depth-capacity production curve** -- cleanup makes reasoning depth LOAD-ROBUST (plain 24->4->0 across 1-3x
   alpha_c; cleanup 24/24/24; 15x high-load). The production knob for deep reasoning under load.
9. P1/P2/P3, B36-ratio, SQ5(biological-scale 10x), compositional-generalization -- all HARD_PASS at full.

## Honest negatives (pressure-tested, confirmed)
- B5 replay (palimpsest+bounded+cf-RPE all HF) = replay-consolidation fundamentally not a substrate strength.
- P4/P5 sparse-x-sequence = sparse helps PATTERN capacity, NOT sequence (modality-specific; locked).
- K_max depth formula = PESSIMISTIC (substrate reasons DEEPER than predicted -- strategic positive).
- Bloom-SQ6 membership = structural wall (no escape rescues).

## Blockers fixed
- Bloom-SQ6 infinite-loop (E>max-edges at full scale) hung the CPU runner ~1hr -> killed+fixed+re-queued.
- Pythia extraction gate (missing --self-test exit) -> fixed -> extraction HARD_PASS (residuals.npz).

## GATED (awaiting others -- I'll build immediately on unblock)
- R1/R2/R5/R6: awaiting Research clarifications (3 specific Qs sent: R1 importance-signal, R2 sparse-bind operator, R5/R6 shared D-RIP metric). Research next wake ~04:00.
- EX-CONCEPT-1 REAL: needs PER-TOKEN Pythia extraction (current npz is per-doc) -- requested Testbed.
- CCC-1 REVISED-v2 + CCC-1-EXTRA: need offline KG/QA datasets -- requested Testbed.
- NEW EXP 4 Medical Path-Y: needs UMLS subset.
- capacity-comp N4096/8192 GPU: persistent infra fail (no log) -> Testbed inspecting; dropped (125K validated at N=2048).
- v8 Llama: deferred (Pythia-first, per your decision).

## Loop continues every 20 min; building the gated cells the moment clarifications/data land.
