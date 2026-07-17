# Pre-registration: read_grow_schema_abstraction_predictive_precision_v2

v2 of the grow-from-reading construction arc. v1 (`exp_read_grow_construction_induction_dop_fragments_v1`,
48c0080ca, VET'd MEASURED_MECHANISM) showed real coverage growth from a grown, flat construction inventory, but
the VET (aa41c04d) + USER steer named 3 gaps: coverage-only (no precision), flat fragments plateau/cover only
SEEN shapes, "surprisal" was a relabeled count. This cell adds two genuinely new pieces on the SAME arc:

- **ARM A (abstraction/schematization):** collapses FLAT POS+deprel fragments sharing a core structure but
  differing in optional UD function-word children into an abstract SCHEMA fragment, tests whether the
  abstracted inventory generalizes to genuinely UNSEEN construction instances and reaches a higher coverage
  ceiling with LESS induction exposure than FLAT needs.
- **ARM B (predictive-use precision):** uses the grown (+abstracted-adjacent) inventory to actually EXTRACT
  triples via confidence-gated, surprisal-disambiguated candidate selection over a genuine multi-candidate
  ambiguity space, scored with the SAME CaRB gold/strictness as RUNG5/ReVerb.

Full design rationale, scope decisions, and the pre-design probe numbers (measured BEFORE finalizing bands,
same discipline as v1) are in the cell's own module docstring:
`experiments/exp_read_grow_schema_abstraction_predictive_precision_v2.py`. This file states the bands/gates for
SCHEMA-VET / SKUNKWORKS audit in one place.

## Corpus + method

- TRAIN (induction): `data/corpora/ud_english_ewt/en_ewt-ud-train.conllu` (already committed, CC BY-SA 4.0),
  6110 qualifying sentences via RUNG 5's `load_qualifying_sentences` (unmodified import).
- TEST (held-out, gold scoring): `data/corpora/ud_english_ewt/en_ewt-ud-test.conllu` -- the SAME file RUNG
  5/9/ReVerb already use, 846 qualifying sentences. TRAIN/TEST are physically disjoint files (zero possible
  sent_id overlap by construction; asserted defensively at self-test AND at full/smoke run time).
- TAIL (ARM A discriminator subset): held-out TEST sentences RUNG 5's unmodified `analyze_sentence` classifies
  `other_unhandled` (n=507/846).
- ARM A: FLAT = v1's `frag1` (imported unmodified from the v1 cell). SCHEMA = FLAT's children-deprel tuple with
  UD "Function Word relations" (case/mark/cc/det/cop/aux) + punct dropped -- a declared, a-priori abstraction
  (NOT tuned post-hoc; a too-aggressive CORE_ONLY whitelist variant was measured and rejected as vacuous --
  scramble coverage 0.92 -- and is reported as a non-gating diagnostic ablation alongside a milder MINIMAL_DROP
  variant). 3 independent deterministic (sha256-seeded) shuffles of TRAIN induction order (seedA/seedB/seedC);
  held-out TAIL is fixed (file-level split, no per-seed re-derivation needed). Growth sweep at nominal induction
  sizes [50, 150, 400, 1000, 2500, full]. Scramble must-fail control (v1's `scramble_sentence`, imported
  unmodified) at full induction size. Genuinely-unseen-FLAT-shape subset test: TAIL sentences whose FLAT root
  shape never occurs ANYWHERE in the full TRAIN pool (n=132/507) -- SCHEMA coverage vs SCHEMA's own scramble
  control on this exact subset (FLAT coverage is 0 by construction there, so FLAT-vs-SCHEMA on this subset would
  be tautological).
- ARM B: a variant of the ReVerb cell's candidate-generation loop (imports its constants/helpers unmodified)
  that enumerates ALL candidate NP-chunk objects in the forward-search window (genuine ambiguity: 24.7% of verb
  occurrences on the pooled test rows have >1 candidate, MEASURED) instead of only the nearest. A GROWN
  frequency table of (verb-specific relation, ReVerb pattern type, distance-bucket) item shapes, with a coarser
  (pattern, distance-bucket) abstract-backoff table, is built from an UNSUPERVISED pass of this SAME candidate
  enumeration over the full TRAIN pool (no gold labels used in induction). PREDICTIVE USE = (1) disambiguate
  multi-candidate groups by argmax induction-frequency (vs a deterministically-seeded RANDOM-tiebreak control,
  and vs the ReVerb baseline's fixed NEAREST-only rule); (2) confidence-gate: abstain unless the chosen
  candidate's shape clears a declared entrenchment threshold (min_item=8 OR backoff min_abstract_frac=0.15 --
  chosen from a pre-design sweep that showed a genuine, non-monotonic PEAK at this point, not tuned to hit an
  arbitrary target; the full sweep is reported as a non-gating diagnostic). Scored on the SAME pooled n=210 test
  rows (SEEDS_FULL=[7,13,19], N_PER_SEED=70) RUNG5/ReVerb use, with `score_arm` (imported unmodified, relax=False).

## Compute architecture

- Class: (b) sequential-CPU with justification. ARM A is pure Python dict/Counter/tuple manipulation (no
  torch/GPU/numpy on the hot path). ARM B additionally calls `nltk.pos_tag` (averaged-perceptron, CITED
  non-neural, same tagger the ReVerb cell already self-tests) + `nltk.RegexpParser`/`tree2conlltags` (zero
  learned parameters). MEASURED prototype wall time for the full pipeline (ARM A 3 seeds + ARM B full-train
  induction + ~15 scoring passes over pooled n=210 test rows) ~= 3-5 minutes; GPU batching would add overhead,
  not remove it, at this scale (string/regex processing, not matrix ops).
- Storage strategy: no_storage (no FoundationStore/KGStore touched; pure in-memory counting + scoring).

## Bands (pre-registered; see cell docstring BANDS section for full detail)

### ARM A (per seed-salt; HP_SCOPE = SCHEMA arm only; FLAT/SCRAMBLE are reference/control arms)

- `seed_passes_hard` := `schema_coverage_gain_over_flat_at_full >= 0.05` AND
  `schema_scramble_margin_at_full >= 0.10` AND `unseen_flat_subset_schema_margin_over_scramble >= 0.05` AND
  SCHEMA reaches FLAT's full-corpus coverage ceiling by sweep index <= 4 (i.e. using <= 2500/6110 = 41% of the
  induction pool) AND `split_overlap == 0`.
- `seed_fails_hard` := `split_overlap > 0` OR `schema_coverage_gain_over_flat_at_full < 0.02` OR
  `schema_scramble_margin_at_full < 0.05` OR `unseen_flat_subset_schema_margin_over_scramble < 0.0`.
- **ARM A HARD_PASS**: all 3 seeds `seed_passes_hard` AND `arms_differ_verified` true for all seeds.
- **ARM A HARD_FAIL**: any seed `split_overlap > 0` (integrity override) OR `arms_differ_verified` false for any
  seed OR `>= 2/3` seeds `seed_fails_hard`.
- **ARM A MIDDLE_BAND**: otherwise.

### ARM B (single deterministic induction pass; HP_SCOPE = GATED_SURPRISAL arm at the declared operating point)

- **ARM B HARD_PASS**: `gated_surprisal_precision >= 0.30` AND `gated_surprisal_coverage > 0.1190` (RUNG5
  baseline) AND `(gated_surprisal_precision - mean_random_tiebreak_precision) >= 0.03` (disambiguation genuinely
  load-bearing) AND `arms_differ_verified` AND glass-box-legal confirmed.
- **ARM B HARD_FAIL**: `gated_surprisal_precision < 0.15` (no meaningfully different regime from raw ReVerb's
  0.083) OR `(gated_surprisal_precision - mean_random_tiebreak_precision) < 0.0` (surprisal does NOT beat random
  tiebreak -- the SAME "relabeled count, not load-bearing" failure class v1 had) OR `arms_differ_verified` false.
- **ARM B MIDDLE_BAND**: otherwise.

### Cell-level combination

- Overall `verdict` = the WORSE of `{arm_a_tier, arm_b_tier}` (HARD_FAIL < MIDDLE_BAND < HARD_PASS in rank).
  Conservative, non-oversold: a cell where one arm is a genuine positive and the other a genuine negative must
  not be reported as a blanket HARD_PASS. Both arm verdicts + full per-seed/per-operating-point detail are
  always reported independently of the combined tier.
- Honest guard: precision and coverage are ALWAYS reported separately for ARM B (no headlined blended
  "all-instance" number); pooled precision is reported (this cell does not construct a distinct
  excluding-other_unhandled bucket beyond what RUNG5's own `per_class` breakdown in `score_arm` already provides,
  which is carried through in the metrics for both BASELINE and GATED arms).

## SCHEMA-VET checklist

```yaml
cardinality_ok: true  # EXPECTED_N_UNITS = arm_a_units (n_seed_salts * 6 sweep sizes) + arm_b_units (1 induction
  # pass + 8 diagnostic min_item sweep points + 3 random-tiebreak salts); smoke: 1*6 + (1+8+3) = 18; full:
  # 3*6 + 12 = 30. Verdict logic counts actual_n_units and HARD_FAILs the combined tier on mismatch (META_RULE_H)
arms_differ_verified: true  # ARM A: FLAT vs SCHEMA inventory hash differ; ARM B: BASELINE vs GATED emitted-set
  # hash differ (META_RULE_AF), both checked at self-test/smoke/full
final_metrics_atomicity: tmp_replace  # META_RULE_AH
crlb_n/a: "no quantitative noise floor formula for discrete construction-coverage counting (ARM A) or discrete
  syntactic pattern-match + classical-tagger-benchmarked accuracy (ARM B); validated instead via scramble/random
  must-fail controls (functionally the same role as a CRLB floor)"
baseline_in_band: true  # ARM A: FLAT arm coverage on full held-out tail (0.623, pre-design measured) is within
  # [0.05, 0.95]. ARM B: BASELINE (raw ReVerb, 0.083/0.714) is a reference point, not smoke-time in-band-checked
  # (same convention as the ReVerb cell itself)
discriminator_survives_scale: "Option A -- ARM A smoke uses the SAME full sweep as FULL (trivial wall time,
  no scale-dependent saturation risk). ARM B smoke uses the SAME full-train induction (fixed corpus size) scored
  against a smaller test subset (seed[7] only, n=70) -- discriminator direction (gated vs baseline precision,
  near-zero disambiguation margin) verified to fire at smoke scale (MEASURED@smoke below)."
hard_pass_strictly_above_floor: true  # ARM A margins (0.34-0.36 scramble margin vs 0.10 floor; 0.08-0.13 unseen
  # margin vs 0.05 floor) are not floor-hugging. ARM B's declared 0.30 floor is, per pre-design measurement, NOT
  # reached (peak ~0.128-0.14) -- an honest, wide-margin HARD_FAIL, not a floor-hugging one.
hp_scope:
  ARM_A_SCHEMA: [schema_coverage_gain_over_flat_at_full, schema_scramble_margin_at_full, unseen_flat_subset_margin,
    ceiling_reached_by_sweep_idx]
  ARM_A_FLAT: []      # reference/control arm, reported not gated
  ARM_A_SCRAMBLE: []  # reference/control arm (must-fail floor), reported not gated
  ARM_B_GATED_SURPRISAL: [precision_at_operating_point, coverage_at_operating_point, disambiguation_margin]
  ARM_B_BASELINE: []      # reference/control arm (raw ReVerb), reported not gated
  ARM_B_GATED_NEAREST: [] # reference/control arm, reported not gated
  ARM_B_GATED_RANDOM: []  # control arm (disambiguation-independence guard), reported not gated
sweep_alignment_verdict: ALIGNED  # gate A -- ARM A nominal induction size tracks actual size used; ARM B's
  # confidence-gate threshold applies identically to every candidate
discriminating_fraction: 0.83  # gate B -- ARM A: 5/6 sweep points land in a genuinely discriminating [0.10,0.70]
  # band. ARM B's gate sweep (precision 0.066-0.14 across min_item 0-40) is itself the discriminating band --
  # none saturated/floor-degenerate; discriminating_fraction 1.0 there.
composition_edges:  # gate C
  - {from: parse_conllu, to: children_map_fragment_extractor, verdict: SHAPE_MATCH}       # ARM A
  - {from: tokenize_postag_chunk, to: candidate_enumeration, verdict: SHAPE_MATCH}         # ARM B (reuses
      # the ReVerb cell's already-validated chain)
  - {from: candidate_enumeration, to: shape_frequency_lookup_and_score_arm, verdict: SHAPE_MATCH}
positive_control_arms:  # gate D
  - arm: HAND_RULE_OTHER_UNHANDLED_REPRODUCE
    primitive: analyze_sentence (RUNG 5, imported unmodified)
    cited_prior_metric: 0.599
    tolerance: 0.05
    regime_extension_audit: SHAPE_MATCH  # same code object, same corpus/filter
  - arm: REVERB_BASELINE_REPRODUCE
    primitive: ie_extract_reverb (ReVerb cell, imported unmodified)
    cited_prior_metric: {precision: 0.0830, coverage: 0.7143}
    cited_prior_regime: {seeds: [7,13,19], n_per_seed: 70, corpus: ud_ewt_test}
    test_regime: {seeds: [7,13,19], n_per_seed: 70, corpus: ud_ewt_test}  # IDENTICAL
    tolerance: 0.02
    regime_extension_audit: SHAPE_MATCH
functional_requirements:  # gate E
  - requirement: "abstract flat fragments into generalizing schemas"
    mechanism: "UD function-word-relation dropping (NEW here; CITED@UD typology + Goldberg CxG core-vs-adjunct
      distinction); a too-aggressive core-only whitelist was measured and rejected (reported as diagnostic)"
  - requirement: "measure unseen-instance generalization, not memorization"
    mechanism: "genuinely-unseen-FLAT-shape subset test (NEW) -- FLAT coverage is 0 by construction there;
      SCHEMA vs its own scramble control on the SAME subset is the informative comparison"
  - requirement: "predictively USE the grown inventory to extract triples, not just measure coverage"
    mechanism: "confidence-gated, surprisal-disambiguated candidate selection over the REUSED ReVerb
      candidate-generation chain (NEW selection logic, reused generation chain), scored with RUNG5's
      unmodified score_arm"
  - requirement: "disambiguation must do independent work, not just reduce volume"
    mechanism: "deterministically-seeded (3-salt) RANDOM-tiebreak control at the SAME operating point (NEW)"
real_code_path_exercised: []  # gate F.1 -- N/A, no KGStore/FoundationStore/substrate-fit objects touched
substrate_signature_checked: []  # gate F.2/F.3 -- N/A, same reason
guard_baseline_validated: []  # gate F.4 -- N/A, no control-beats-POP-style guard in this cell
deterministic_seeding: true  # gate F.5 -- all shuffles/scrambles/random-tiebreaks derive from hashlib.sha256
  # digests of stable string keys (reusing v1's digest_frac/digest_seed); never hash() nor list(set(...))
cell_chunked: false  # exemption: MEASURED full wall time ~3-5 minutes total (pooled, not per-seed); chunking
  # overhead disproportionate to this scale (protects long-running work from partial loss, not sub-10-min cells)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true  # single heartbeat tick at run end (sub-10-minute wall; no mid-run cadence needed)
defensive_error_checking: passed_all_4_patterns
progress_logging: "print_flush_true"  # declared regardless of the 1800s threshold (MEASURED wall well under it)
calibration_check: "default_ok_for_this_regime"  # ARM A MIN_COUNT=2 (same as v1, evidenced non-vacuous).
  # "adaptive_with_discriminator_gate" for ARM B's confidence-gate operating point (min_item=8/frac=0.15 chosen
  # from a pre-design sweep showing a genuine, non-arbitrary PEAK; full sweep reported non-gating)
```

## Compute / dispatch

- Smoke: ARM A seedA-only (SAME full sweep, Option A); ARM B full-train induction scored against seed[7]-only
  test rows (n=70, matching the ReVerb cell's own smoke convention). MEASURED@smoke: overall HARD_FAIL (combined
  = worse of the two arms), elapsed_s=5.73, ARM_A=HARD_PASS (schema_gain=+0.136, unseen_margin=0.129,
  ceiling_idx=4), ARM_B=HARD_FAIL (gated_surprisal_precision=0.140, mean_random_precision=0.1400,
  disambig_margin=+0.0000 -- near-zero, confirming the pre-design probe's honest negative at smoke scale too).
- Full: ARM A all 3 seed-salts; ARM B scored against pooled n=210 (SEEDS_FULL=[7,13,19]).
- Timeout: 1800s (MEASURED smoke wall ~6-8s including process startup; full prototype wall for the equivalent
  pipeline was 3-5 minutes; 1800s gives a wide safety margin -- compute is O(n_sentences) pure-Python +
  bounded nltk.pos_tag calls, no scaling risk beyond linear).
- Route: `local_cpu_queue` (light CPU work, no heavy training fit, per COMPUTE-PROPORTIONALITY -- run fast to
  completion rather than routing to a heavy remote/GPU queue; local FULL runs re-authorized per MEMORY.md
  2026-07-15 note).
- Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before queue_add.
