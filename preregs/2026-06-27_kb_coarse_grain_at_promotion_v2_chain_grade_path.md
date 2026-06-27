# Pre-reg: kb_coarse_grain_at_promotion_v2_chain_grade_path (ANCHOR 3 v2; CHAIN_GRADE candidate; 2026-06-27)

**Anchor:** `kb_coarse_grain_at_promotion_v2_chain_grade_path`
**Cell:** `experiments/exp_kb_coarse_grain_at_promotion_v2_chain_grade_path.py`
**Queue:** `remote_cpu_queue` (NO LOCAL per USER 2026-06-27)
**Tier hint:** CHAIN_GRADE candidate (v1 tiered PROVEN_BOUND due to (a) rec saturation at metric cap + (b) USER_DIRECTIVE separation vacuously satisfied with n_UD=0 in sample). v2 designed to break both saturations.
**Wave:** 3b promotion-path; routed remote via orchestrator.

## Source

v1 metrics: `data/exp_kb_coarse_grain_at_promotion_v1/metrics.json` -- FULL HARD_PASS but cert-owner tiered PROVEN_BOUND. Skunkworks RC paths:
- RC-1: mix USER_DIRECTIVE atoms into the sample so the load-bearing separation invariant is genuinely tested.
- RC-2: scale `n_atoms >= 10000` so the rec=1.000 cap genuinely breaks (small-N rec is by-construction saturated against the original W).

## Scope

Same mechanism + adaptive percentile threshold as v1. CHANGES:

1. **Mandatory USER_DIRECTIVE inclusion:** force-include at least `n_UD >= 10` atoms with `source_class='memory'`. Production KB has 939 memory atoms; sampling at least 10 is guaranteed. USER_DIRECTIVE atoms MUST NEVER be clustered with non-USER atoms; per-arm verification asserts `user_directive_mixing_violations == 0` (HARD_FAIL invariant).
2. **Scale n_atoms >= 10000 (full) / 600 (smoke -- matches v1 smoke).** At n=10k mixed-class sample, the cosine recall metric is well below saturation (random retrieval at n=10k = 1/10k = 0.0001; mechanism must climb above adaptive ceiling). ARM_ULTRA must measurably differentiate from ARM_RANDOM.
3. **Discriminator-must-survive-scale guard:** smoke runs both at smoke-N (600) AND at full-N preview arm (n=10000, single seed, ARM_ULTRA only) to verify baseline still discriminates at full scale before full dispatch acceptance.

## Arms (3 mandatory + 1 full-N preview at smoke)

### ARM_NO_COARSE_GRAIN_BASELINE
Same as v1; sanity rail. recall_unclustered = 1.0 by construction.

### ARM_COARSE_GRAIN_ULTRAMETRIC
Same primitive call. CHANGES vs v1:
- Sample forces n_UD >= 10 memory-class atoms mixed in.
- Cluster computation per-source-class (USER_DIRECTIVE strictly separated by construction).
- recall metrics computed against the FULL W (not collapsed W) so the saturation cap (which capped v1) lifts; recall metric = fraction of clustered atoms whose top-1 match in the collapsed KB has the same cluster_id as the query.
- At n=10k, the adaptive threshold operates on a 10k-row pairwise distance matrix (memory: ~400MB float32 if dense; chunked computation used).
- `user_directive_mixing_violations` asserted == 0.

### ARM_RANDOM_CLUSTER_COLLAPSE
Matched cluster sizes from ARM_ULTRA. CONTROL. recall_clustered for random must be measurably lower (gap >= 0.30 at n=10k; mechanism non-null).

### ARM_FULL_N_PREVIEW (smoke-only safety check; n=10000 single seed)
At smoke, run ARM_ULTRA ONCE at n_atoms=10000 with 1 seed to verify recall metrics do not saturate at full-N (the v1 failure mode). If preview rec_unclst >= 0.95 at n=10k, smoke FLAGS the cell as "may saturate at full" but does not block dispatch (the full-N PASS bar is set below the saturation cap).

## Success criteria (CHAIN_GRADE bar; HARDER than v1 INFRASTRUCTURE bar)

HARD_PASS requires ALL of:
- (a) `user_directive_retention == 1.0` (zero memory-class atoms clustered with non-memory; n_UD >= 10 verified present).
- (b) `recall_unclustered < 1.0` at n_atoms=10000 (cap-breaking evidence -- proves we are NOT at metric saturation).
- (c) `capacity_drop_fraction > 0.20` (mechanism does substantive compression; > v1's 0.212 floor).
- (d) `gap_vs_random > 0.30` (ULTRA - RANDOM recall_clustered; mechanism strongly non-null at scale).
- (e) `cv_recall_clustered < 0.05` across 3 seeds (seed-stable).

MIDDLE_BAND: any subset of (a)+(b)+(c)+(d) met but (e) fails (0.05 <= cv <= 0.10) OR gap in (0.15, 0.30].
HARD_FAIL: (a) violated, OR (b) rec_unclst still saturates at 1.0 at n=10k, OR cap_drop < 0.10, OR gap <= 0.05.

## Failure (REJECT)

- `user_directive_mixing_violations > 0` (load-bearing invariant violated).
- `n_UD_in_sample == 0` (test vacuously satisfied; v1 failure mode recurring).
- `recall_unclustered == 1.0` AND `recall_clustered == 1.0` at n=10k (still saturated; need larger N or harder discriminator).
- ARM_RANDOM recall_clustered >= ARM_ULTRA recall_clustered (mechanism null).

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `cardinality_ok`, `summary.arms[].n_user_directive_atoms`, `summary.arms[].user_directive_mixing_violations`, `summary.full_n_preview_recall_unclustered` (smoke only).

## cardinality_ok

`summary.cardinality_ok = (n_UD_in_sample >= 10) AND (n_atoms_full >= 10000) AND (n_seeds_full >= 3)`.

## Discipline gates

- Fix #26: pre-dispatch referent check (KB W matrix exists at load_default_kb path).
- META_RULE_H: cardinality_ok mandatory.
- META_RULE_J: USER_DIRECTIVE separation enforced as HARD_FAIL invariant (zero loss tolerance).
- META_RULE_K: discriminator-must-survive-scale via ARM_FULL_N_PREVIEW at smoke.
- META_RULE_L: real-data evidence (production KB, not synthetic).
- META_RULE_M: band-floor recall is MIDDLE_BAND; cap_drop > 0.20 AND gap > 0.30 required for HARD_PASS.

## Estimated cost

Smoke: ~30-90s (n=600 + n=10k preview single seed; pairwise dist ~400MB peak).
Full: ~5-15min (n=10000 x 3 seeds; pairwise dist memory ~400MB peak; cluster computation O(n^2) per seed).

## Routing

`remote_cpu_queue` on marsh@home (per USER 2026-06-27 NO LOCAL directive). Push + queue_add via orchestrator (push is harness-DENIED to exp_dev).
