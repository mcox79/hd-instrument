# exp_dev hand-off -- research: federated privacy knowledge accumulation (level-2 drill)

Filed-by: research sub-agent
Trigger: notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
Date: 2026-06-07

## Pause state block
This file is written unconditionally. exp_dev MUST check data/orchestrator_paused.flag before dispatching to queue. If paused, hold this handoff until resume.

## Per [[feedback-no-experiment-design-in-prompts]]
This file provides TASK + WHY + CONTRACT + AUTONOMY pointers only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA. No inline experiment design below.

---

## Anchor candidates (rank-ordered)

### Rank 1: Cell A -- DP substrate write utility curve
- Anchor pointer: Differential privacy noise injection at write time; vary epsilon; measure retrieval accuracy
- Substrate-product reading: Determines minimum N and epsilon for viable federated healthcare/finance deployment; the sigma_max vs sigma_DP gap formula predicts HARD FAIL at N=1024/epsilon=1.0 and PASS at N=4096/epsilon=2.0; needs empirical confirmation
- Tier hint: CPU probe (numpy simulation, no GPU needed); laptop or remote CPU
- Why-now: Closes the most critical unknown in the federated privacy thesis -- is the DP capacity formula correct at the alpha_c boundary? Direct precondition for any product claim on healthcare consortium deployments

### Rank 2: Cell B -- Secret-shared substrate correctness
- Anchor pointer: Additive (k=3) secret sharing on substrate weight matrix W; verify retrieval correctness after reconstruction
- Substrate-product reading: Confirms the key algebraic compatibility claim: pseudoinverse write + additive sharing = correct aggregate substrate. This is the "algebraically native" claim in the research note. Should be ~1.0 correctness minus float rounding; any degradation indicates implementation error
- Tier hint: CPU probe; laptop or remote CPU; ~5 min wall time
- Why-now: Lowest-cost highest-confidence anchor in the batch; binary pass/fail with no ambiguity; prerequisite correctness test for all Pattern C deployments

### Rank 3: Cell D -- Federated aggregate cross-party retrieval
- Anchor pointer: 3-party simulation: local writes, simulated secure aggregation sum, central DP noise, test cross-party retrieval accuracy
- Substrate-product reading: Validates the core federation value proposition -- can party A's patterns be retrieved by party B after aggregation without revealing local data? If cross-party accuracy > 0.80 at epsilon=2.0, the healthcare consortium product story is empirically supported
- Tier hint: CPU probe; laptop or remote CPU; ~15 min wall time
- Why-now: The most commercially important cell; directly validates the $30B healthcare market entry claim

### Rank 4: Cell E -- Membership inference oracle test
- Anchor pointer: AUROC measurement of cosine-similarity membership inference on substrate, with and without DP output perturbation
- Substrate-product reading: Quantifies Failure 5 severity; if AUROC > 0.90 without DP (expected, validating oracle leakage concern) and DP at epsilon=2.0 reduces AUROC < 0.65, this provides the empirical basis for the "DP-protected retrieval oracle" product claim
- Tier hint: CPU probe; laptop or remote CPU; ~10 min wall time
- Why-now: Required for honest privacy certification claims; regulators will ask about membership inference

### Rank 5: Cell C -- BFV homomorphic write latency benchmark
- Anchor pointer: Microsoft SEAL or OpenFHE; N=256; k=2 parties; measure HE write/read latency vs plaintext
- Substrate-product reading: Determines whether Pattern D (HE write aggregation) is in the "acceptable for batch offline" regime or "too slow for any use case" regime; 100-1000x overhead is the expected range; > 5000x is HARD FAIL for production use
- Tier hint: CPU probe; requires SEAL/OpenFHE Python bindings; ~30 min wall time including setup
- Why-now: Lower priority than A-D; only needed if A+B+D pass and HE path is being seriously considered

---

## Context pointers (file paths, not summaries)
- Research note: d:/AI/hd-instrument/notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
- Prior unlearning note: d:/AI/hd-instrument/notes/research_drill_federated_unlearning_2026-06-02.md
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check for current federated/privacy rows before dispatch)
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl
- Queue: d:/AI/hd-instrument/data/overnight_queue/queue.json

---

## Contract section
exp_dev is autonomous on: anchor naming, sweep parameter choices, threshold formula derivation, queue assignment, ETA estimation, pre-registration format.
exp_dev is NOT autonomous on: deciding whether to override the pause flag, committing to cap_map changes, dispatching cloud runs > $10 without orchestrator authorization.

## Autonomy declaration
This handoff is structural. exp_dev picks up on emergency-refill cycle scan (notes/exp_dev_handoff_*.md sorted by mtime). No orchestrator prompt needed to activate.
