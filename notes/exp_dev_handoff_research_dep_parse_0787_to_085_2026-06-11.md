# exp_dev hand-off -- research: dep-parser 0.787 -> 0.85+ substrate-only path

Filed-by: research (2x DEEP drill, 2026-06-11)
Trigger: Research note notes/research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHOR CANDIDATES and POINTERS only.
exp_dev designs the cells and ships per the standard envelope/smoke/queue protocol.

## Anchor candidates (rank-ordered)

### A1 (TOP) -- four-cell decisive sweep: decode x parts ladder
  - Anchor pointer: notes/research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md (section "Cheap decisive test")
  - Substrate-product reading: dep-parse 0.85 substrate-only is the v1-product unlock for structured information
    extraction without LLM dependency.  Composes on PP-379 POS (0.9499) to give substrate-only structured-NLP stack.
  - Tier hint: B if any cell HARD_PASS; A on n=5 multi-seed at HP boundaries (S2 or S3)
  - Why-now: substrate arc-scorer already validated at 0.694; perceptron lever already validated at POS 0.95; this
    is composition of two validated levers, NOT novel substrate primitive.  Cheap CPU < 1 hour.

### A2 -- 3rd-order parts only (Koo-Collins 2010)
  - Anchor pointer: same note, sections "Lever B" and "P-3"
  - Substrate-product reading: pushes substrate beyond what feature-engineered MSTParser achieved historically
  - Tier hint: B; A on multi-seed
  - Why-now: cleanest single-mechanism test; isolates whether higher-order parts alone clear 0.85

### A3 -- POS-tag + char prefix/suffix bundles as input features (Lever D)
  - Anchor pointer: same note, section "Lever D"
  - Substrate-product reading: addresses 8.5% OOV (dominant residual error) without architecture change
  - Tier hint: C if measured incrementally on top of best A1 config; B if it independently lifts S0
  - Why-now: lowest-cost lever; reuses existing PP-379 outputs as features

### A4 (HOLD) -- joint POS+parse structured prediction (Lever F)
  - Anchor pointer: same note, section "Cascade vs joint"
  - Substrate-product reading: theoretical interest; small product lift expected
  - Tier hint: D candidate; only run if A1 plateaus in 0.83-0.84 band
  - Why-now: hold until A1 verdict

## Context pointers (paths, not summaries)

  - notes/research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md  (this drill)
  - notes/exp_dev_to_research_DISCRIMINATIVE_WEIGHTING_UNIVERSAL_2026-06-11.md  (universal-lever precedent)
  - memory/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md       (substrate-classical framing)
  - memory/substrate_only_NL_pos_tagger_validated_2026-06-11.md                  (POS 0.9499 precedent)
  - memory/drill_pattern_temporal_contextual_not_structural_2026-06-11.md        (drill-pattern reliability prior)
  - memory/feedback_dont_parrot_drill_defeatism_2026-06-11.md                    (substrate-only path exhaustion)

## Contract

  - exp_dev owns cell design, smoke gate, queue ship, and post-ship REMOTE VERIFY.
  - HARD-PASS / HARD-FAIL thresholds are pre-registered in the source research note (P-1 through P-6).
  - Multi-seed n=5 required at HP boundaries for any Tier-A promotion claim.
  - LIFT verification per [[feedback-method-overclaim-lift-validation]]: report lift > 2 x SE relative to S0,
    NOT just absolute UAS threshold.
  - Bundled UD-English-EWT (per RESCUE-1).  No external data fetch.

## Autonomy declaration

exp_dev decides: cell name, smoke-vs-full ordering, queue selection (home CPU vs cpu_runner_local vs GPU --
A1/A2/A3 are all CPU-class), seed schedule, whether to fold A2/A3 into A1's sweep, whether to lock S3 in A1
includes all 3rd-order parts or only sibling+grandchild.

Research stays available for re-drill if S3 surprises (plateau below 0.82 with no obvious feature-coverage cause).
