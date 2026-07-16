# Pre-reg: curriculum_order_ingest_schema_fit_v1

**Date:** 2026-07-16. **Author:** exp_dev. **Cell:** `experiments/exp_curriculum_order_ingest_schema_fit_v1.py`.
**Compute:** local numpy, no queue/GPU/atoms/push. Sequential-CPU justified: wall < 10s total; the cell IS the
gate/ingest mechanism being validated (bit-exact numpy reference). Runs to completion in foreground.

## Question

Does INGESTION ORDER matter for foundation-building? Does CURRICULUM/prerequisite order (foundational/core/
high-connectivity facts first) beat ARBITRARY order at building a quality foundation, and does curriculum order
RESCUE the schema-fit signal (handicapped when advanced facts arrive before their scaffold)? USER: "learn quantum
mechanics before addition -> very different experience." Abstraction is scaffolded; schema-fit is RELATIVE to what
is already in the foundation, so ORDER determines what it can see.

## Construction (glass-box numpy; reuses additive_map + reachability_audit CORE ideas)

- Foundation = additive-map coordinate space: entities are coordinates X in R^k, relations are displacements,
  readout = closed-form Euclidean distance, compose = degree-invariant arithmetic MEAN of per-edge tail estimates
  (reuses `hdlab/additive_map.py`'s core; numpy re-impl since additive_map is torch/CSKG-coupled and this is a
  directional-gate cell -> proportional method per COMPUTE-PROPORTIONALITY discipline).
- GENUINE prerequisite DAG: a concept forest where a deep node's true coord x_true = x_true(parent) + delta. Prereqs
  are REAL: a deep fact ingested before its ancestors has genuinely no admitted anchor to place on.
- schema_fit(X) = fraction of X's up-to-`ref_levels` nearest-ancestor refs currently ADMITTED in the foundation
  (reuses `hdlab/reachability_audit.py`'s prerequisite-reachability idea). Root/axiom nodes ground on an
  always-present INNATE anchor set (core-knowledge priors) -> schema_fit = 1.
- FIXED gate: admit iff schema_fit >= tau. `tau = 0.50` set ONCE, principled (majority-of-prerequisites present),
  applied IDENTICALLY to all 3 orders and BOTH regimes (anti-rig). Rejected fact NOT re-queued (single-pass) -> that
  is exactly why order can matter.
- Placement on admit = degree-invariant MEAN over present refs of (foundation[ref] + observed noisy displacement).
  More prereqs present -> average of more estimates -> more accurate placement; errors PROPAGATE (a ref placed under
  a thin scaffold is noisy -> children inherit error).
- Same facts + same per-seed noisy displacements reused across all 3 orders (fairness).

## Orders x Regimes

- Orders: CURRICULUM (topological, shallow-first), ARBITRARY (random perm), REVERSE (deep-first).
- HIERARCHICAL (positive control): deep prerequisite forest (3 roots x depth-5 binary = 189 nodes). Order should
  PROVABLY matter.
- FLAT (null guard): every fact grounds directly on the always-present innate anchors (no prerequisites) ->
  schema_fit = 1 for all facts in ALL orders -> order should NOT matter. Confirms the effect is prerequisite-
  structure-driven, not a spurious gate artifact.

## Metrics (per regime x order, mean over 8 seeds)

- `admit_rate` = fraction of TRUE facts admitted (all facts are true).
- `premature_rejection` = fraction of non-axiom TRUE facts rejected (would admit under curriculum).
- `foundation_quality` = held-out relational retrieval accuracy (sibling-retrieval; edges NOT used during
  ingestion; noiseless query oracle so accuracy reflects FOUNDATION placement error + coverage).
- `mean_placement_error` = mean ||x_foundation - x_true|| over admitted nodes.

## PRE-REG BANDS

- **HARD-PASS** = HIERARCHICAL: `(curriculum_quality - reverse_quality) >= 0.25` AND curriculum rescues schema-fit
  vs arbitrary `(arbitrary_premature - curriculum_premature) >= 0.20`; AND NULL guard holds: FLAT quality spread
  across orders `<= 0.05` AND FLAT premature `<= 0.02` all orders.
- **HARD-FAIL** = HIERARCHICAL quality spread across orders `<= 0.05` (gate handles any order equally -> order
  doesn't matter here).
- **MIDDLE** = otherwise.

## Discriminator-fires gate (smoke)

- HIERARCHICAL reverse `premature_rejection >= 0.30` (reverse must actually mis-reject scaffold-less deep facts).
- FLAT spread `<= 0.05` and FLAT premature `<= 0.02` (null MUST hold; if flat shows an order effect the mechanism is
  spurious/buggy -> `BLOCK_NULL_GUARD_FAILED_SPURIOUS_ORDER_EFFECT`).

## Anti-rig / feasibility

- `tau` fixed at 0.50, NOT tuned to make curriculum win. tau-robustness sweep {0.34, 0.50, 0.67} reported.
- Both endpoints measurable: curriculum quality high, reverse quality low, arbitrary intermediate at shallow depth
  -> not a vacuous/saturated single-arm test. Depth-sweep {2,3,4,5} reports arbitrary transitioning smoothly from
  intermediate to collapsed (order-sensitivity is a smooth function of the structural depth knob).
- Determinism: numpy `default_rng` fixed int seeds; NO `hash()`-derived seeds; `sorted()` for all set ops
  (META_RULE F.5 compliant). Atomic tmp+os.replace metrics write (META_RULE_AH). `except Exception` only, SystemExit
  re-raised (no BaseException). Arms-must-differ asserted (curriculum vs reverse admit sets differ in hierarchical;
  identical in flat by design).

## Honest scope note

The hierarchical order effect is partly BY-CONSTRUCTION: a genuine deep prerequisite DAG + a scaffold-requiring
single-pass gate necessarily makes reverse/arbitrary order fail. The load-bearing SCIENTIFIC content is (1) the NULL
guard proving the effect is prerequisite-structure-specific not a universal gate artifact, (2) the magnitude/rescue
quantification, and (3) the depth-sweep showing the smooth gradient. Confirms `research_developmental_...
curriculum_order` note Prediction 1 (P=0.28) in the constructed regime; identifies the FIX = curriculum-ordered
ingest OR provisional-hold-for-bootstrapping (re-queue rejected premature facts).
