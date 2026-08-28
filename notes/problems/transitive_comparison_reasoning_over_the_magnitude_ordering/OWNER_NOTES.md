---
owner_verdict: DONE
---

SOLVED: transitive_comparison_reasoning_over_the_magnitude_ordering (SOLVER, opus 4.8)

The first reasoning operation is built and validated. The reader now takes pairwise comparisons ("A>B, B>C"), integrates them into one magnitude ordering, and answers the un-stated pair ("A vs C") it was never told.

Mechanism (brain-foundational): delta-rule / value-transfer settling (Frank-Rudy-O'Reilly 2003; hippocampal relational integration, Dusek/Eichenbaum) → bounded FHRR magnitude-line register (item_key ⊗ FPE(position), parietal ATOM) → native FPE read-out. Copies the computation, sweeps the parameters. Not a symbolic sort.

Bar — all 4 items met (witness verification/test_transitive_ordering_reasoning.py = 12/12 PASS; problem_ledger --check clean):

Un-stated pairs 1.000 vs the association floor 0.500 (+0.500 CI-sep) on the association-matched internal pairs (the Dusek/Eichenbaum control); twin loses; stated-only at chance.
Symbolic-distance effect (Weber confidence 1.29→4.01; accuracy far-beats-near d2:0.68→d8:0.92 under noise) + end-anchor effect — both classic human signatures, both emergent.
Substrate-native + grounded on real words via the landed p1 ruler (recovers human concreteness order 1.000 vs 0.673, +0.327 CI-sep).
Proposed default-off hdlab/transitive_ordering.py diff in SOLVED.md.
Strongest brain-foundational result: on the same premises, serial chaining and the magnitude line reach identical overall accuracy (0.74) but opposite distance-effect direction — chaining −0.98 (far harder), magnitude +0.91 (far easier). The human positive distance effect forces the magnitude-line choice and rules out chaining (Eichenbaum, measured on-substrate). The mechanism isn't asserted from the brief; a measured human signature selects it.

Honest boundaries: integration ties direct-reading on a grounded 1-D axis (two-systems regime — reasoning is for novel/text-defined orderings, exp4 proves that regime); the front-end (p1 reading close comparisons at ~60%) is the grounded bottleneck, flagged as the top adjacency.

6 experiments + witness. Full writeup, KEY REALIZATIONS, AUDIT UPDATE, proposed hdlab diff, and adjacency map in notes/problems/transitive_comparison_reasoning_over_the_magnitude_ordering/SOLVED.md.

Reverify: .venv/Scripts/python.exe verification/test_transitive_ordering_reasoning.py
