# exp_dev hand-off -- research: Pattern B production stack compatibility (3x drill)

Filed-by: research sub-agent (Sonnet)
Trigger: notes/research_drill_pattern_b_production_stack_compat_3x_2026-06-07.md
Date: 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates
and context pointers only. exp_dev designs the experiment scripts autonomously.

---

## Pause state block

Not currently paused. All 5 anchors below are CPU-only, < 30 min total wall time.
Can run in parallel as a batch. No cloud dispatch needed.

---

## Anchor candidates (rank-ordered)

### Rank 1: pattern_b_bundle_manifold_dim_TwoNN

Why now: d=30 PCA truncation is the ONE hard incompatibility between Pattern A and Pattern B
production stacks. This test resolves it in < 5 min CPU. If d_hat <= 50, the adaptation is
a config change. If d_hat >= 150, the adaptation requires a full PCA sweep. Either result
changes the engineering estimate and directly informs v1.1 scope.

Anchor pointer: Test 1 from research drill Section "3-5 cheap decisive tests".
Substrate-product reading: generate 1000 bundles from 20 random role vectors + bge-small
  fillers at N=4096; run TwoNN estimator; report d_hat.
Tier hint: CPU laptop, < 5 min. numpy + sklearn (or manual 2-NN estimator).
Hard-pass: d_hat <= 50 (d=30 needs only minor bump; PCA transfers with small adaptation)
Hard-fail: d_hat >= 300 (PCA truncation too expensive; must redesign compression for Pattern B)

### Rank 2: pattern_b_partial_bundle_retrieval_smoke

Why now: Partial-bundle retrieval (e.g., "find all facts where subject=X") is the KEY new
capability that differentiates Pattern B from Pattern A. If partial queries don't work at
the production N=2048-4096, Pattern B reduces to a slower Pattern A with more overhead.
This test is the go/no-go for the compositional retrieval mode.

Anchor pointer: Test 2 from research drill.
Substrate-product reading: store 20 bundles at N=2048; query with 2/3-bundle (subject+relation
  known, object unknown); measure cosine of retrieved vs target bundle.
Tier hint: CPU laptop, < 10 min.
Hard-pass: 2/3-bundle query cosine >= 0.75 for >= 18/20 queries.
Hard-fail: 2/3-bundle query cosine < 0.60 for any query type.

### Rank 3: pattern_b_role_sharing_cosine_audit

Why now: Modern Hopfield capacity degradation for Pattern B depends on pairwise cosine between
role-sharing bundles. The research drill predicts rho_max = 0.15-0.35 for typical role overlap.
If rho_max < 0.20, modern Hopfield loses only a minor fraction of its capacity. If rho_max > 0.35,
capacity degrades ~0.42x and must be measured directly rather than inferred.

Anchor pointer: Test 3 from research drill.
Substrate-product reading: 100 bundles from 20-vector role vocabulary; all-pairs cosine;
  report mean/95th-pct/max for pairs sharing 0, 1, 2 role slots.
Tier hint: CPU laptop, < 5 min.
Hard-pass: max cosine < 0.20 for any role-sharing category.
Hard-fail: 50th-pct cosine > 0.25 for 1-role-sharing pairs.

### Rank 4: pattern_b_whitening_eigenvalue_ratio

Why now: PCA whitening adaptation for Pattern B requires computing a new whitening basis on
bundles. This test checks whether whitening is even useful (eigenvalue ratio > 5) or whether
the bundle distribution is already near-uniform (ratio < 2, skip whitening). Answers the
question in < 5 min, removing a step from the adaptation roadmap if not needed.

Anchor pointer: Test 4 from research drill.
Substrate-product reading: sample covariance of 500 bundles; eigenvalue spread (max/min).
Tier hint: CPU laptop, < 5 min.
Hard-pass: eigenvalue ratio > 5 (whitening needed; compute Pattern B basis separately)
Hard-fail: eigenvalue ratio < 2 (whitening neutral for Pattern B; skip adaptation step)

### Rank 5: pattern_b_W_column_energy_variance

Why now: 4-bit quantization of W is expected to transfer, but the energy distribution of W
contributions from bundles vs single embeddings has not been measured. If bundles produce
structured sparse W columns, quantization error is amplified in a structured way. This test
checks whether the assumption is safe.

Anchor pointer: Test 5 from research drill.
Substrate-product reading: store 50 bundles in W at N=4096; measure column-wise energy CV;
  compare to 50 Llama embeddings in the same W.
Tier hint: CPU laptop, < 10 min.
Hard-pass: bundle CV / embedding CV < 2.0
Hard-fail: bundle CV / embedding CV > 5.0

---

## Context pointers

Research note (this drill): d:/AI/hd-instrument/notes/research_drill_pattern_b_production_stack_compat_3x_2026-06-07.md
Prior Pattern B feasibility note: d:/AI/hd-instrument/notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
Prior exp_dev handoff (SRL pre-test + capacity): d:/AI/hd-instrument/notes/exp_dev_handoff_research_pattern_b_compositional_storage_3x_2026-06-07.md
Pattern A production stack: cycle 143/148 (pseudoinverse), cycle 149 (H=2 BFT), cycle 155 (4-bit quant + sparse-W fail), cycle 157 (d=30 KEY-job)

---

## Contract section

The research drill establishes:
- 7/8 Pattern A elements transfer to Pattern B (clean or minor adaptation)
- d=30 PCA truncation is the one hard incompatibility (bundle manifold ~100-300 dim)
- Engineering estimate: 3 days for Pattern B overlay on Pattern A stack (excl. SRL)
- The 5 anchors above resolve all remaining uncertainty in < 30 min total CPU time
- All 5 can run in parallel or as a single batch; no ordering dependencies

## Autonomy declaration

exp_dev designs all 5 experiment scripts without further research or orchestrator input.
Script complexity is low (50-100 lines each; numpy + sklearn). No model downloads needed
beyond bge-small (already on runner). Dispatch as a single CPU batch.
