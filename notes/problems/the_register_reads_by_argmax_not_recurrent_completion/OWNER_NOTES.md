---
owner_verdict: DONE
---

the_register_reads_by_argmax_not_recurrent_completion — SOLVED
All 5 bar items met, plus 3 deepening drills. Six cells + one scaffold-free witness (13/13), problem_ledger --check clean.

The mechanism (brain-foundational, corrected by the drill): the register's capacity cliff is largely an argmax-readout artifact. The brain reads a superposition by theta-gamma serial decode-and-suppress (Lisman & Idiart 1995 — decode strongest, inhibition-of-return, decode next from the residual), not CA3 attractor completion. Copying that operation on the linear superposition recovers the overloaded register ~4× at fixed D.

What the numbers say:

Recovery (synthetic, D=256): argmax 0.51 → serial 1.00 at M=64 (+0.454 CI-sep); window M∈[16,64].
It's the right completion: the Hopfield attractor control ties argmax (no manifold on separated codes) → the gain is known-key crosstalk cancellation, not generic "completion." Twin loses; the per-component bundle renorm breaks serial (must read the linear sum).
Lever separation (bar 3): readout (2×) and p2's sparse store (8×) are distinct and compose to 12–16× at fixed D.
The reconciliation (bar 4, the meat): attractor completion hurts ranking (hub bias, +0.587 CI-sep), and both halves of the falsifiable prediction hold (scales with settling depth and cue degradation). A CA1-comparator exact-match gate routes by query structure — completes for recall, degrades to graded for rank — and beats both blanket policies (0.947 vs 0.77/0.64).
Real load (bar 2): honestly inert on the bulk (no false current-task win), recovers the real book-scale tail — 91 LitBank entities with ≥64 events: argmax 0.959 → serial 1.000 (+0.041 CI-sep), twin near-chance.
Three drills beyond the bar (your pushes):

Component fidelity → found & measured the non-brain-faithful bundle renorm that breaks the readout.
Correlated fillers (reversed my own prediction): serial is correlation-invariant (keyed on orthogonal keys); argmax collapses 0.76→0.14 → the lever is more valuable on real correlated verbs, so exp4's +0.041 is likely an under-estimate.
The divergence wall, drilled with a graded/stochastic resonator: true capacity bound, not a hard-commit artifact — the brain-faithful fix is the store (distribute load), exactly exp2.
Handoff: SOLVED.md carries the proposed additive hdlab diff (decode_serial + decode_gated on AccumulateRegister, no storage change), the AUDIT UPDATE, and 4 flagged adjacencies (strongest: the bundle-renorm fidelity gap — a clean focused-solver brief). Nothing landed in hdlab/ (Q111). Reverify: verification/test_register_completion_readout.py.
