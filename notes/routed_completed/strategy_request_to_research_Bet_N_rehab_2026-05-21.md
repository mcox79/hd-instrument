# Strategy → Research: Bet N (soft cleanup) rehab routing per PROT-004

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~15:42 EDT
**Topic**: Bet N KILLED cycle 43 — rehab discipline missed under verdict-batch pressure; routing now

## Context

`wave14r_multihop_soft_cleanup_v1` full mode KILLED 15:30:01 with
acc_50hop=0.160 across all τ ∈ {0.5, 1.0, 2.0, 4.0}, below FHRR's 0.22
floor at every τ. Closure scope: cleanup-amplification axis at current
Plate-HRR substrate.

Strategy did not file rehab routing immediately due to verdict-batch
pressure (3 verdicts + R17 integration in 8 minutes). User catch
("you have all negative results researched right") triggered this
routing.

## Per PROT-004: 5 axis-combination rescue sketches (DRAFT — Research vets in 2x deep pass)

Strategy DRAFT sketches; Research expected to GENERATE the rescue list
during Pass 2, not vet a Strategy-drafted one. Sketches below are
starting points only per [[feedback-unbiased-research]].

### Sketch 1 — Top-k weighted propagation (k > 1, not just softmax over all atoms)
Soft cleanup used softmax over all N atoms. Alternative: explicit top-k
selection with weighted propagation (k ∈ {2, 4, 8}). Reduces noise
amplification from low-overlap atoms while preserving the cleanup-
amplification mechanism Wu-Zhou 2024 polylog identified in R16.

### Sketch 2 — Iterative cleanup with damping (substrate Newton-style)
Replace single-pass softmax with iterative refinement: cleanup_t+1 =
α·cleanup(query_t) + (1-α)·query_t. Variable α schedules. Substrate-
physics analog: thermal annealing trajectories in spin-glass landscape
(per R23 FRSB regime).

### Sketch 3 — Heavy-tailed (Cauchy/Lorentzian) cleanup distribution
Softmax is Gaussian-like; substrate atoms in BSC might benefit from
heavier-tailed cleanup that preserves dispersion. Cauchy-style cleanup
distribution. Connects to R18 (RFOT) mathematical-glass-without-caging
caveat — if substrate has only mathematical (not physical) glass
character, heavier tails might restore the genuine-caging-like behavior.

### Sketch 4 — Sparse cleanup (L1-regularized atomic selection)
Force cleanup output to be sparse (≤ K_sparse atoms) via thresholding
or top-1 with confidence-gated abstention. Substrate-physics anchor:
sparse spike-and-slab models for high-d signal recovery.

### Sketch 5 — Annealed-β with bundle-state feedback
Adaptive-β (R8 #6) failed at fixed schedules. Alternative: β controlled
by current bundle norm or overlap variance — feed back from substrate
state. Like Marchenko-Pastur eigenvalue-distribution-aware temperature.

## What Research should produce

Per [[feedback-unbiased-research]] + [[project-research-playbook]] item 9:

1. **Pass 1 (external lit-scan, broad)**: cleanup operators in
   high-dimensional associative memory; cleanup amplification beyond
   simple argmax; non-equilibrium dynamics in error-correcting codes;
   iterative-cleanup theory.
2. **Pass 2 (substrate drill)**: which mechanisms survive the 4-axis
   closure (binding, cleanup, storage-redundancy, symptom-mitigation)
   at current-arch and ALSO at substrate-physics-load-bearing analog?
3. **Output format**: research note enumerating actual mechanisms with
   substrate-compatible variants; explicit probability estimates per
   [[feedback-no-smoke]]; honest-negative tagging if family fully closes.

## Sequencing recommendation

R33 quantum-repeater is HIGHER priority than this rehab. R33 is the
only poly-vs-exp candidate and has not yet been routed. Bet N rehab
is rehab discipline (closing a closure with PROT-004) — important but
not the highest-leverage Research bandwidth.

Suggested order: R33 first, then this Bet N rehab + Bet O rehab in
parallel pass.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
