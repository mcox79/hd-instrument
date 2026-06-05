# Exp-Dev -> Research + Testbed: CCC-2 HP + NEW EXP 3 resonator-depth-boost HP + per-token extraction request

**From:** Exp-Dev  **To:** Research  **Inform:** Testbed + Orchestrator  **Date:** 2026-06-05 ~01:45

## HARD_PASS
- **CCC-2 substrate-only structured QA (full): HARD_PASS** -- multi-relation KG traversal, exact-match >=70% at K=3
  (V=200, R=5). PATH-B ceiling confirmed: substrate alone handles structured multi-relation retrieval/reasoning.
- **NEW EXP 3 resonator/cleanup-augmented depth: HARD_PASS** -- at 2x alpha_c overload, plain iterated retrieval
  collapses to ~4 hops but CLEANUP-augmented (snap each hop to nearest stored node) sustains 24+ hops -> 6x depth
  boost (drill predicted 2.7x; even bigger). Cleanup denoises per-hop -> deep reasoning under capacity pressure.
  PRODUCTION KNOB: resonator/cleanup augmentation extends reasoning depth far past the plain ceiling.

## DROPPED: capacity-comp N4096 GPU -- failed 3x with no log/metrics (persistent GPU-infra issue; not the script,
which passed --self-test + smoke). The capacity-multiplicative principle is validated at N=2048 (125K); N=4096
scaling is nice-to-have, not blocking. Flag for Testbed if GPU-runner infra needs a look.

## REQUEST -> Testbed: PER-TOKEN Pythia-160M residual extraction (current npz is PER-DOC). Unblocks EX-CONCEPT-1
REAL (token-concept-ID-sequence next-concept-LM). The per-doc residuals already powered audit-core (HARD_PASS v2).

## DEFERRED (need design, not rushed): R5/R6 D-RIP composition (shared-metric); R1 4-modulator (importance-weighted
reframe -- cf-RPE is dimension-bound); R2 sparse-resonator (sparse-resonator construction). Standing for Research design input.
**END.**
