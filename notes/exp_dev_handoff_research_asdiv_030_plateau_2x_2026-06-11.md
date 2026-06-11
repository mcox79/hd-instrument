# exp_dev hand-off: research ASDiv 0.30 plateau 2x DEEP (2026-06-11)

**Filed-by.** research sub-agent (opus), 2026-06-11.

**Trigger.** 2x DEEP research drill on ASDiv 0.30 / 0.309 plateau.
Diagnosis: cascade v1 + v2 are near their own architectural ceiling
(1-op-only oracle ceiling = 0.404). Path past 0.40 requires three
structural moves: class-dispatch pre-stage (covers 8 procedural
sub-classes), joint 1-op + 2-op scoring (current fallback rarely
fires), learned operand-selector (last-pair heuristic costs 24% on
1-op subset).

**Pause state.** Check `data/orchestrator_paused.flag` at dispatch. If
present, hold this hand-off. Per [[feedback-no-experiment-design-in-prompts]]
the anchors below are pointers; exp_dev owns the experiment design.

**Source research note.**
- d:/AI/hd-instrument/notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md

---

## Anchor candidates (rank-ordered)

### Anchor 1: ASDiv class-dispatch pre-stage (RANK-1; highest priority)
- Pointer: source research note section (c) Prediction P2; section
  "Concrete substrate-native paths" RANK-1; class-by-class subset
  table.
- Substrate-product reading: regex on the question stem dispatches the
  RATIO / GCD / LCM / MEAN / AREA / PERIM / COMPARE / YESNO subset
  (~243 items = 10.5% of ASDiv corpus) to a Python builtin
  (math.gcd, math.lcm, statistics.mean, ratio reduction, a*b, 2*(a+b),
  entity-name, Yes/No). The remaining items fall through to the
  existing v2 cascade. This is the cheapest highest-precision
  intervention and is independent of the cascade.
- Tier hint: Tier-A. Cheap. ~30 min CPU build. Isolated lift expected
  >= +0.07 absolute on full ASDiv.
- HARD-PASS / HARD-FAIL: source note Prediction P2
  (HARD-PASS full-ASDiv accuracy >= 0.37; HARD-FAIL < 0.34).
- Why now: highest single isolated lift; independent of cascade; lowest
  build cost; preserves full audit trace; the procedural classes are
  currently solved at near-zero by the arithmetic cascade so this is
  pure additive lift.

### Anchor 2: Cascade v3 joint 1-op + 2-op scoring (RANK-2)
- Pointer: source note Prediction P1; section "Concrete substrate-native
  paths" RANK-2; section (d) `2-op fallback fires rarely because 1-op
  produces a plausible candidate first`.
- Substrate-product reading: instead of v2's `if 1-op produces nothing,
  try 2-op`, score both branches jointly using the discriminative head's
  margin + verifier score, pick the higher-margin branch. Covers the
  22.4% subset (516 items) that v2 silently mis-solves as 1-op.
- Tier hint: Tier-A. ~30 min CPU build (re-order existing v2 logic).
- HARD-PASS / HARD-FAIL: HARD-PASS full-ASDiv accuracy with joint scoring
  >= 0.34 (lifts v2 by 0.03+); HARD-FAIL < 0.31. Conditional on
  Anchor 1 having shipped first (so isolated effect is measurable).
- Why now: zero-cost re-ordering of v2's existing branches; the 2-op
  fallback in v2 is currently nearly dead code.

### Anchor 3: Learned operand-selector (RANK-3)
- Pointer: source note Prediction P3; section "Concrete substrate-native
  paths" RANK-3; supporting computation (perfect-op + last-pair
  heuristic = 71% of 1-op subset, so operand selection is a real
  remaining lever).
- Substrate-product reading: substrate perceptron over per-pair features
  (numeric magnitude, surface distance to question token, position of
  "more"/"less"/"each"/"per" cues relative to each number, recency from
  question). Replaces the last-pair heuristic in cascade.
- Tier hint: Tier-A. ~2 hr CPU build + train. Per-pair training data is
  derivable from answer-consistency over the existing labeled subset.
- HARD-PASS / HARD-FAIL: HARD-PASS full-ASDiv >= 0.36 with operand-
  selector stacked on Anchor 1 + Anchor 2; HARD-FAIL < 0.32.
- Why now: attacks the 1-op subset directly; the largest single
  remaining lever inside the arithmetic regime that the cascade owns.

### Anchor 4: Discriminative re-ranker (RANK-4)
- Pointer: source note Prediction P4; section "Concrete substrate-native
  paths" RANK-4.
- Substrate-product reading: substrate bundle-similarity head over
  (problem-bundle, candidate-answer-bundle-with-unit-token); trained on
  gold positives + negatives from nearby wrong reductions. Replaces
  the v2 `_plaus` range filter with a learned discriminative re-ranker.
- Tier hint: Tier-A. ~3 hr CPU build + train. Synthetic negatives are
  cheap (all-pairs sweep produces wrong candidates).
- HARD-PASS / HARD-FAIL: HARD-PASS +0.03 over Anchor 1 + 2 + 3 stack;
  HARD-FAIL < 0.01 lift.
- Why now: closes the remaining tie-breaking failures the operand-
  selector leaves; uses orthogonal signal (unit string match).

### Anchor 5: Dep-parse-feature operand-selector extension (RANK-5)
- Pointer: source note Prediction P5; section "Concrete substrate-native
  paths" RANK-5.
- Substrate-product reading: PP-381 hashed-UAS=0.787 dep-parser (now
  available); add features "subject-of-question", "object-of-question",
  "head-noun-modifying-each-number" to Anchor-3 operand-selector.
- Tier hint: Tier-B. ~2 hr CPU build. Gated on Anchor 3 HARD-PASS.
- HARD-PASS / HARD-FAIL: HARD-PASS +0.02 above Anchor 3 alone;
  HARD-FAIL within noise (< 0.005).
- Why now: dep-parse is sitting idle in PP-381; cheap to integrate;
  modest expected lift; explicit syntactic role signal for
  comprehension-heavy items.

### Anchor 6: Unified structured perceptron over (class, op, operand)
- Pointer: source note RANK-6.
- Substrate-product reading: Collins-2002 structured perceptron over
  the joint label space (problem_class, op_seq, operand_index_seq).
  Substrate bundle similarity = emission feature; Viterbi inference.
- Tier hint: Tier-B. ~1 day CPU build. Long-term unified replacement
  for Anchors 1-4.
- HARD-PASS / HARD-FAIL: HARD-PASS replaces stacked 1+2+3+4 with a
  single coherent model and beats it by >= 0.03; HARD-FAIL < same as
  stacked.
- Why now: only after stacked Anchors 1-4 land and the ceiling is
  measured. Hold until 1-4 verdicts.

### Anchor 7: Diagnostic T-CEILING measurement (instrument-only)
- Pointer: source note section (b) Cheap decisive test T-CEILING.
- Substrate-product reading: NO new training. Compute upper bound of
  current v2 architecture by ablating only operand-selector to oracle,
  keeping v2 op-classifier. Verifies P1 (ceiling diagnosis).
- Tier hint: Tier-A diagnostic. ~5 min CPU. Should run FIRST to
  validate the diagnosis.
- HARD-PASS / HARD-FAIL: HARD-PASS oracle-operand v2 accuracy in
  [0.35, 0.42]; HARD-FAIL > 0.45 (would invalidate P1) or < 0.30
  (would mean v2 op-classifier is also broken).
- Why now: ~5 min validation of the 2x diagnosis before committing
  exp_dev cycles to Anchors 1-5. If T-CEILING reads > 0.45 the whole
  prioritization changes.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md
  (this 2x drill)
- d:/AI/hd-instrument/notes/research_drill_asdiv_mixed_adversarial_2x_2026-06-11.md
  (prior cascade-recommendation drill)
- d:/AI/hd-instrument/notes/exp_dev_to_research_RESCUES_DONE_ASDIV_CASCADE_2026-06-11.md
  (cascade v1 = 0.300 MIDDLE delivery)
- d:/AI/hd-instrument/experiments/exp_asdiv_cascade_cpu_v1.py
- d:/AI/hd-instrument/experiments/exp_asdiv_cascade_v2_cpu_v1.py
  (existing cascade scaffolds to extend, not rebuild)
- d:/AI/hd-instrument/experiments/data/asdiv_validation.json
  (bundled ASDiv corpus, n=2305, formula field present)
- d:/AI/hd-instrument/experiments/data/ud_english_ewt/
  (UD-English-EWT bundle from RESCUE-1; available for dep-parse
  features in Anchor 5)
- d:/AI/hd-instrument/data/exp_asdiv_cascade_cpu_v1/metrics.json
  (cascade v1 = 0.300 MIDDLE_BAND verdict)

---

## Contract section

- exp_dev owns experiment design; this hand-off lists pointers only.
- exp_dev runs Anchor 7 (T-CEILING diagnostic) FIRST to validate P1
  before committing cycles to Anchors 1-5.
- exp_dev ranks Anchors 1, 2, 3 as the immediate exp_dev-actionable
  batch (parallel-shippable: A1 isolated, A2 v2 re-order, A3 new
  perceptron).
- exp_dev defers Anchors 4, 5, 6 until verdicts on 1-3.
- All anchors are CPU-only; no GPU required.
- All anchors use bundled corpus already in repo; no network at
  runtime.
- Multi-seed (n>=5) at the HARD-PASS boundary per smoke-test
  methodology memory.

---

## Autonomy declaration

This hand-off lists POINTERS to the source research note and the
existing experiment scaffolds. It does NOT pre-design the experiments.
exp_dev autonomy:
- exp_dev decides feature set, training recipe, hyperparameters per
  anchor.
- exp_dev decides shipping order (recommended: A7 -> A1 -> A2 -> A3 in
  series; A4 -> A5 conditional on A3 verdict).
- exp_dev decides whether to stack interventions or run them
  independently for cleaner ablation.
- exp_dev decides multi-seed n and HP boundary policy.
- exp_dev decides whether RANK-6 (unified structured perceptron) is
  worth a 1-day cell after stacked Anchors 1-4 verdict.

end of hand-off.
