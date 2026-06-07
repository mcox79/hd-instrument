# exp_dev hand-off -- research: Llama privacy mechanism reopening (3x)

Filed-by: research sub-agent
Trigger: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY +
CONTRACT + AUTONOMY. Exp_dev designs anchors, sweep parameters, thresholds, and queue
placement -- NOT this file.

---

## WHY NOW

The eigenspectrum diagnostic (cycle 154/155) proved that SRHT leaves Llama's participation
ratio unchanged (12.733 -> 12.733). This mathematically rules out the dimension-
concentration hypothesis: orthogonal transforms preserve all inner products and cannot
disrupt manifold-local cosine similarity. The new leading hypothesis is manifold
confinement: Llama L15 embeddings may live on a ~20-50 dimensional manifold within
the 2048-dimensional ambient space. If confirmed, a PCA bottleneck projection (compress
below manifold dim) is the substrate-internal fix that disrupts the leak signal. Two
cheap diagnostics (2 hours CPU each) will determine which mitigation path to pursue.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- Manifold dimensionality diagnostic (laptop CPU, ~2 hours)
Pointer: research note Section 5, Priority 1 diagnostic
Substrate-product reading: Run PCA explained-variance curve and TwoNN intrinsic
dimensionality estimator on the production KB embedding matrix (shape N_stored x 2048).
Record k_90 (number of PCA components needed for 90% explained variance). If k_90 < 100,
manifold confinement is confirmed and the bottleneck PCA mitigation should run immediately.
If k_90 > 300, pivot to Gram structure diagnostic.
Tier hint: laptop CPU; numpy + scikit-learn only; no GPU needed; ~2 hours wall
Why now: this is the cheapest screen that determines which privacy fix path has the
correct mechanism. Without it, we are guessing at which of five hypotheses is active.

### Anchor 2 -- Member vs nonmember cosine distribution diagnostic (laptop CPU, ~2 hours)
Pointer: research note Section 5, Priority 2 diagnostic
Substrate-product reading: Collect 200 member query embeddings and 200 non-member query
embeddings. For each, compute cosine to nearest stored vector. Run KS test between the
two distributions. If KS p < 0.001, the leak is in pairwise Gram structure and rank
randomization (Mallows shuffle, Path B) is the direct mitigation. Test can run in
parallel with Anchor 1 on the same harness instance.
Tier hint: laptop CPU; same harness as Anchor 1; ~2 hours wall
Why now: directly measures the mechanism the attacker is exploiting. Result determines
whether Path B (rank randomization) is worth pursuing.

### Anchor 3 -- PCA bottleneck projection ZKL test (laptop CPU, ~2 hours, conditional)
Pointer: research note Section 5, Priority 1, bottleneck pre-test
Substrate-product reading: If Anchor 1 confirms k_90 < 100, run PCA projection to
k_bottleneck = 20 (below k_90), reconstruct to 2048 via pseudoinverse, measure ZKL(50)
and top-1 recall. This is the direct test of whether manifold disruption achieves
the ZKL < 0.12 target while preserving recall >= 0.85.
Tier hint: laptop CPU; conditional on Anchor 1 result; ~2 hours wall
Why now: if Anchor 1 confirms manifold confinement, this is the immediate mitigation
test. It is a 30-line change to the inference path.

### Anchor 4 -- Layer sweep ZKL profile (laptop CPU, ~2-3 hours)
Pointer: research note Section 5, Priority 3 diagnostic
Substrate-product reading: Extract embeddings at layers {5, 8, 10, 12, 15, 20} for
same stored facts. Measure ZKL(50) and top-1 recall at each layer. Identify the
"privacy frontier" layer -- lowest ZKL while recall >= 0.85. This test costs nothing
to implement if the fix works (just change the extraction layer config index). A
layer sweep revealing ZKL < 0.14 at an earlier layer would be the zero-cost fix.
Tier hint: laptop CPU; HuggingFace model already loaded; ~3 hours wall
Why now: cheapest possible fix if it works -- zero architecture change, just config.

---

## CONTEXT POINTERS

Research note (this drill): d:/AI/hd-instrument/notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
Prior privacy mechanism drill: d:/AI/hd-instrument/notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
SRHT empirical results: notes/exp_dev_to_research_URGENT_srht_hurts_llama_2026-06-07.md
Federated privacy handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_federated_privacy_substrate_2x_2026-06-07.md
Cycle 154/155 eigenspectrum result: data/exp_<anchor>/metrics.json (check orchestrator for exact anchor names)

---

## CONTRACT

- Exp_dev designs ALL anchor parameters, sweep grids, threshold formulas, queue placement
- Exp_dev verifies formula self-tests before coding
- Exp_dev checks queue.json for name collisions before shipping
- ASCII-only in print()/verdict_msg (per [[feedback-ascii-only-in-scripts]])
- Progress logging for any run > 5 min wall
- All four anchors are laptop CPU -- do NOT route to GPU runner
- Anchors 1 and 2 can run in parallel (different passes over the embedding matrix)
- Anchor 3 is conditional on Anchor 1 result (k_90 < 100 required)
- Anchor 4 is independent and can run any time the Llama harness is available

## AUTONOMY DECLARATION

Exp_dev has full autonomy to:
- Choose specific PCA implementation (sklearn or torch SVD)
- Choose intrinsic dimensionality estimator (TwoNN or MLE are both fine)
- Choose the specific k_bottleneck values to sweep (20, 50, 100 are suggested but not required)
- Choose the non-member query set source
- Determine the exact number of queries (200 is suggested; adjust based on available eval set)
- Add additional layer sweep points beyond {5, 8, 10, 12, 15, 20}
- Combine anchors into a single script if it reduces overhead
- Pre-register hard-fail thresholds per their own analysis of the mechanism
