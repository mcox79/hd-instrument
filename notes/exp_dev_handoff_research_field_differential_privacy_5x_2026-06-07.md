# exp_dev hand-off -- research: differential privacy field 5x deep drill

Filed-by: research sub-agent
Trigger: notes/research_drill_field_differential_privacy_5x_2026-06-07.md
Date: 2026-06-07

## Pause state block
This file is written unconditionally. exp_dev MUST check data/orchestrator_paused.flag before dispatching to queue. If paused, hold this handoff until resume.

## Per [[feedback-no-experiment-design-in-prompts]]
This file provides TASK + WHY + CONTRACT + AUTONOMY pointers only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA. No inline experiment design below.

---

## Anchor candidates (rank-ordered)

### Rank 1: RDP accountant integration + T-round epsilon verification
- Anchor pointer: Wire dp_accounting (Google library, pip install dp_accounting) Gaussian accountant into substrate write path; run T in {5, 10, 20, 50, 100} composition steps at sigma=4.8 (epsilon=1.0 single round); compare RDP, basic composition, and advanced composition epsilon_total values
- Substrate-product reading: The core claim of the 5x drill is that RDP is ~9x tighter than basic composition at T=20. If confirmed, the product can certify "epsilon <= 8.0 after 20 rounds" vs "epsilon = 20 under basic composition." This is the accounting primitive that enables the "DP-by-construction" product pitch. Cheap: pure Python, no GPU, no substrate writes needed -- just the accountant math.
- Tier hint: CPU probe, laptop, ~5 min; pip install dp_accounting required
- Why-now: Lowest-cost highest-impact anchor in this batch. Direct prerequisite for any customer-facing privacy certificate claim.

### Rank 2: DP write utility curve -- epsilon vs retrieval accuracy at N=4096
- Anchor pointer: Gaussian mechanism applied to substrate write vectors at N=4096; vary epsilon in {0.5, 1.0, 2.0, 4.0, 8.0}; k=3 parties; measure fraction of M=100 written patterns retrievable (cosine_sim > alpha_c) after noisy writes
- Substrate-product reading: Closes the most important empirical unknown from both the 2x federated drill and this 5x drill. The alpha_c capacity formula predicts sigma_max=8.73 at N=4096 vs sigma_DP=4.8 at epsilon=1.0, giving gap factor 1.8x. If retrieval accuracy > 0.85 at epsilon=1.0, N=4096 is confirmed viable and the federated deployment architecture is sound.
- Tier hint: CPU probe (numpy simulation, no GPU needed); ~10 min wall time
- Why-now: Confirms or refutes the key N=4096 rehabilitation from the 5x drill; required before any federated product claims at N=4096.

### Rank 3: Per-instance DP sparse vector utility gain
- Anchor pointer: Generate write vectors with varying sparsity w/N in {0.05, 0.10, 0.20, 0.50, 1.0}; apply per-instance Gaussian noise calibrated to each vector's actual L2 norm rather than worst-case sensitivity; measure M_max (max retrievable patterns) vs worst-case noise at the same epsilon=1.0
- Substrate-product reading: If M_max increases by >= 3x for sparse vectors (w/N <= 0.1), the healthcare/finance sparse-record use case is viable at N=1024. This is the rehabilitation path for the N=1024 hard-fail from the 2x drill. Expected gain: 3-10x M_max improvement; HARD-FAIL if improvement < 2x.
- Tier hint: CPU probe; ~10 min wall time; requires per-vector sensitivity computation
- Why-now: The sparsity angle is the cheapest path to N=1024 viability. If it works, avoids the N=4096 requirement and reduces compute cost for edge deployments.

### Rank 4: Shuffle DP amplification measurement
- Anchor pointer: Simulate k=20 client histogram submissions under local DP with epsilon_local=2.0; apply simulated random permutation shuffle; measure effective central epsilon via hypothesis testing (distinguishability test between shuffled and direct-submission distributions)
- Substrate-product reading: The theory predicts epsilon_central ~ 0.44 after shuffling 20 clients with epsilon_local=2.0. If confirmed, the shuffle model eliminates the "trust the aggregator" objection at near-central-DP utility. Relevant for maximum-security customer segments (financial services, government). HARD-PASS: epsilon_central <= 0.60; HARD-FAIL: epsilon_central > 1.0 (no amplification).
- Tier hint: CPU probe; ~15 min wall time; statistical test requires careful delta calibration
- Why-now: Lower priority than Ranks 1-3; needed only if customer objections to trusted aggregator emerge. Queue after Rank 2 confirms.

### Rank 5: Membership inference AUROC baseline
- Anchor pointer: Build a substrate W at N=2048, M=300 stored patterns; adversary tests 600 probes (300 in-set, 300 out-of-set) via cosine similarity threshold; measure AUROC with and without DP output perturbation at epsilon=2.0
- Substrate-product reading: Expected AUROC > 0.90 without DP (confirms the oracle leakage concern from the 2x drill) and < 0.65 with DP at epsilon=2.0 (confirms DP output perturbation protects against membership inference). Required for regulatory/auditor responses: "our system is protected against membership inference attacks."
- Tier hint: CPU probe; ~10 min wall time
- Why-now: Lowest priority of the batch; not blocking any product claims. Queue last.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_field_differential_privacy_5x_2026-06-07.md
- Prior federated 2x drill: d:/AI/hd-instrument/notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
- Prior federated 2x handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_federated_privacy_substrate_2x_2026-06-07.md
- Streaming algorithms 5x drill: d:/AI/hd-instrument/notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md
- VSA field 5x drill: d:/AI/hd-instrument/notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev owns: anchor names, queue assignment (overnight_queue vs remote_cpu_queue), threshold formulas, sweep grids, ETA estimates, pre-reg envelope bands.

Research note owns: which capabilities are claimed, what HARD-PASS and HARD-FAIL thresholds are (at the conceptual level), which product implications are asserted, ranked priority order.

Conflicts: if exp_dev judges a proposed anchor infeasible (e.g., dp_accounting library not available on runner), exp_dev files a routing note back to orchestrator before skipping -- does NOT silently skip.

## Autonomy declaration

exp_dev may adjust N, M, sigma, T, epsilon, k, and w/N sweep grids freely within the conceptual framing above. exp_dev may reorder Ranks 2-5 based on queue state. exp_dev may batch Ranks 1+2+3 into a single runner cell if wall time allows. exp_dev does NOT redesign the core mechanism (e.g., switching from Gaussian to Laplace mechanism) without escalating to orchestrator.
