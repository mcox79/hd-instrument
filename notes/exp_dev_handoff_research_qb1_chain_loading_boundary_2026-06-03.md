# exp_dev hand-off -- research: QB1 heteroassociative chain loading boundary

Filed-by: research sub-agent
Trigger: notes/research_drill_qb1_chain_loading_boundary_2026-06-03.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. Anchor names, sweep grids, threshold formulas, HF/HP numerical bounds, and queue choice are for exp_dev to decide.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority)
Pointer: QB1 chain loading boundary alpha-sweep
Substrate-product reading: Establish the exact α_collapse as a function of chain depth L for the current substrate configuration. The theoretical prediction from DCS 1998 + finite-chain correction (PhysRevE 2007) places the boundary at α_eff(L=300-400) ≈ 0.22–0.24. A sweep over α × L confirms the operating envelope and produces the engineering curve for the product spec ("use α < X for depth > Y").
Tier hint: this is a cheap CPU sweep (no GPU needed — smoke-class, design-space mapping).
Why-now: Q-B1 chain depth-300 and depth-400 HARD_FAILs at α ≈ 0.229+ are unresolved. The operating envelope for chain retrieval is the product spec. This is the highest-leverage cheap test available.

### Anchor 2 (secondary)
Pointer: QB1 chain k_decay exponent vs (alpha_c - alpha)
Substrate-product reading: Fit the depth-decay rate k_decay as a function of (α - α_c_eff). DCS predicts k_decay ~ 1/(α_c - α). If the exponent is confirmed, it validates the DCS model class and provides a calibration formula for the product.
Tier hint: CPU, requires anchor 1 data to fit.
Why-now: Only needed once anchor 1 sweep data is in hand. Can be batched with anchor 1 analysis.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_qb1_chain_loading_boundary_2026-06-03.md
- DCS 1998 reference: cond-mat/9805073 (α_c ≈ 0.269, sequence network capacity)
- PhysRevE 2007: 10.1103/PhysRevE.75.011910 (chain-length-dependent L_c)
- Long Sequence Hopfield Memory: arXiv:2306.04532 (NeurIPS 2023)
- Transient dynamics: arXiv:2506.05303 (Clark 2025, Phys Rev E)
- Non-reciprocal Hopfield: arXiv:2501.00983 (SciPost 2025)

---

## Contract

exp_dev designs and queues the cheapest decisive test per the research note's "Cheap decisive test" section. The test must pre-register HARD-PASS / HARD-FAIL bands before shipping. Queue on CPU runner (laptop or remote CPU) unless the sweep proves too large for <60s wall per cell.

## Autonomy declaration

exp_dev decides: anchor naming, sweep grid granularity, which runner, timeout formula, pre-reg threshold values, whether to batch anchors 1+2 into one run. Orchestrator does not specify these.
