# exp_dev hand-off -- research: Friston FEP substrate framework 2x drill

**Filed-by:** research sub-agent
**Date:** 2026-06-04
**Trigger:** d:/AI/hd-instrument/notes/research_drill_friston_fep_substrate_framework_2x_2026-06-04.md
**Pause state:** check data/orchestrator_paused.flag before queueing

Per [[feedback-no-experiment-design-in-prompts]]: this file hands ANCHOR CANDIDATES + WHY-NOW +
CONTEXT POINTERS to exp_dev. exp_dev designs sweep grids, threshold formulas, and queue entries
autonomously.

---

## Anchor candidates (rank-ordered)

**Rank 1 -- FEP precision-weighted update vs BCM baseline BPC comparison**
- Anchor pointer: Implement precision-weighted update rule Delta_W^(l) = Pi^(l) * epsilon^(l) *
  sigma^(l-1)^T where Pi is initialized to identity and updated via rank-1 subtraction after each
  retrieval: Pi <- Pi - alpha * sigma sigma^T. Compare BPC on held-out patterns against BCM+three-
  factor baseline at same N, M, training steps.
- Substrate-product reading: if FEP-class BPC < BCM BPC by > 0.30 nats: Constraint 2 dissolution
  yields measurable training quality improvement; proceed to rung-2 scale. If BPC difference in
  [-0.10, +0.30]: architectures are equivalent at this scale; theoretical dissolution is valid but
  no empirical advantage yet. If FEP worse by > 0.10 nats: precision adaptation unstable at discrete
  boundary; temperature annealing required.
- Tier hint: CPU smoke, N=512, M=64, K=1000 steps, ~20 min wall; no GPU required for this rung.
- Why-now: Spisak-Friston 2025 provides the direct algebraic derivation that VFE minimization over
  bipolar-state networks yields this exact update rule with anti-Hebbian term. The cheap test
  immediately determines whether Constraint 2 dissolution is empirically meaningful, not just
  theoretically satisfying.

**Rank 2 -- Overlap matrix orthogonalization probe**
- Anchor pointer: After K training steps under FEP-class rule, compute the M x M overlap matrix
  O_ab = |xi_a . xi_b| / N for all stored pattern pairs. Compare mean off-diagonal O_off_diag
  between FEP-class and BCM baseline. HP band: O_off_diag < 0.15 for FEP-class.
- Substrate-product reading: self-orthogonalization is the core claim of Spisak-Friston 2025 and
  is the mechanism by which FEP's complexity term (||W||_F^2 Gaussian prior) prevents pattern
  interference. Confirming orthogonalization directly validates the precision-as-repulsion mapping.
- Tier hint: CPU quick probe, same run as Rank 1 (zero marginal cost -- compute O_ab as a logged
  metric during the BPC comparison run).
- Why-now: piggybacks on Rank 1 at zero additional compute cost; provides a second axis of
  falsification for the FEP reframing.

**Rank 3 -- Precision matrix eigenvalue distribution vs Parisi q(x)**
- Anchor pointer: After convergence, compute eigenvalue spectrum of Pi_final. Compare to
  Parisi P(q) prediction for M/N=0.125 (M=64, N=512) from replica theory. If eigenvalue
  distribution matches Marchenko-Pastur bulk with Parisi peak structure: spin-glass / free-probability
  adjacency is confirmed.
- Substrate-product reading: validates the spin-glass -> FEP -> free-probability adjacency chain
  identified in this drill. Tier-1 field adjacency (spin-glass 83% yield + free-probability 100%
  yield). Opens cavity-method precision matrix derivation as next research direction.
- Tier hint: CPU quick probe, ~5 min additional analysis after Rank 1 run; numpy eigenvalue
  computation on 512x512 matrix.
- Why-now: cross-validates three independent Tier-1 research fields simultaneously. High information
  per compute-minute ratio.

---

## Context pointers

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_friston_fep_substrate_framework_2x_2026-06-04.md
- Prior META 3x drill: d:/AI/hd-instrument/notes/research_drill_substrate_as_training_mechanism_3x_meta_2026-06-04.md
- Prior handoff (training mechanism constraints): d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_training_mechanism_3x_meta_2026-06-04.md
- Spisak-Friston 2025 key paper: https://arxiv.org/abs/2505.22749
- Spin-glass field advisor entry: notes/research_meta_map_and_adjacencies_*.md rows for spin-glass E3

---

## Contract

- HARD-PASS: FEP-class BPC < BCM BPC - 0.30 nats AND O_off_diag < 0.15
- MIDDLE-BAND: BPC difference in [-0.10, +0.30] nats
- HARD-FAIL: FEP-class BPC > BCM BPC + 0.10 nats

## Autonomy declaration

exp_dev owns: anchor naming, exact sweep grids (alpha, eta, Pi init), timeout formula, queue choice.
exp_dev does NOT modify cap_map -- research note flags no cap_map row changes pending.
Constraint 2 dissolution is theoretical (algebraic); empirical BPC improvement is separate question.
