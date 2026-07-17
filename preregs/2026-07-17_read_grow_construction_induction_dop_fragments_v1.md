# Pre-registration: read_grow_construction_induction_dop_fragments_v1

Minimal FEASIBILITY PROBE of Prediction 2 from
`notes/research_how_brain_does_broad_construction_parsing_synthesis_2026-07-17.md`: can the substrate GROW a
glass-box, non-neural construction inventory from a reading corpus (variable-grain POS+deprel form-meaning
fragments, induced by frequency counting, scored/selected by a -log P surprisal cutoff -- the SAME scoring
form as `exp_codex_unexpectedness_incremental_value_v1`'s ingest-gate primitive) that covers held-out
construction instances the existing hand-rule toy grammar (Rung 5's `analyze_sentence`, imported unmodified)
kept missing, WITHOUT per-construction hand-authoring, WITH genuine held-out generalization (not memorization)?

Full design rationale, scope decisions, and the pre-design probe numbers are in the cell's own module
docstring: `experiments/exp_read_grow_construction_induction_dop_fragments_v1.py`. This file states the
bands and gates for SCHEMA-VET / SKUNKWORKS audit in one place.

## Corpus + method

- Corpus: `data/corpora/ud_english_ewt/en_ewt-ud-test.conllu` (already committed, CC BY-SA 4.0), loaded via
  Rung 5's `load_qualifying_sentences` (unmodified import) -- 846 qualifying declarative 5-25-token sentences.
- HAND-RULE baseline arm: Rung 5's `analyze_sentence` (unmodified import), classifying each sentence into one
  of 6 buckets; `other_unhandled` = the TAIL this probe targets.
- GROWN arm: POS+deprel shape fragments at 2 grains (depth-1 token+children; depth-2 additionally each
  qualifying child's own children), extracted from the GOLD UD dependency tree (pure recursive descent, no
  learned model). A shape enters the induced inventory once its pooled frequency count clears an entrenchment
  threshold MIN_COUNT=2. Selection criterion restated as a surprisal cutoff `-log(MIN_COUNT/total)`, reported
  per induction size.
- Split: deterministic sha256-digest split of `sent_id` (70% induction / 30% held-out), 3 independent salts
  (seedA/seedB/seedC). Zero sentence-id overlap asserted (SPLIT_IDENTITY check).
- Growth curve: nominal induction-pool sizes swept at [50, 150, 300, full] (actual sizes = min(nominal,
  pool_size); "full" = the whole induction pool for that split, ~580-630 sentences).
- Must-fail control: SCRAMBLE arm -- deterministically-seeded per-sentence permutation of deprel labels
  (preserves per-sentence label multiset, destroys true form-meaning association), same induction+coverage
  pipeline, computed at full induction size.

## Compute architecture

- Class: (b) sequential-CPU with justification. Pure Python dict/Counter/tuple manipulation over pre-parsed
  CoNLL-U token lists (no torch, no GPU, no numpy on the hot path -- Rung 5's transitive import chain pulls in
  numpy/nltk but this cell's own algorithm never calls them). Wall time for the full 3-seed x 4-sweep-point run
  is ~1s (MEASURED@smoke, `elapsed_s`); GPU batching would add overhead, not remove it, at this scale.
- Storage strategy: no_storage (no FoundationStore/KGStore touched; pure in-memory counting).

## Bands (pre-registered; see cell docstring BANDS section for full detail)

Per-seed-salt gates (GROWN arm only; HAND_RULE and SCRAMBLE are reference/control arms, HP_SCOPE excludes them):

- `seed_passes_hard` := `tail_root_coverage_at_full_induction >= 0.15` AND
  `(tail_root_coverage_at_full_induction - scramble_coverage_at_full) >= 0.10` AND growth curve
  monotonic-enough (`last - first >= 0.10`; no single consecutive drop `> 0.02`) AND `split_overlap == 0`.
- `seed_fails_hard` := `split_overlap > 0` OR margin `< 0.03` OR `growth_curve[-1] - growth_curve[0] <= 0.0` OR
  `tail_root_coverage_at_full_induction == 0.0`.

Cell-level tiers:

- **HARD_PASS**: `split_overlap == 0` for all 3 seeds AND all 3 seeds `seed_passes_hard` AND
  `arms_differ_verified` (META_RULE_AF) true for all seeds.
- **HARD_FAIL**: any seed `split_overlap > 0` (integrity breach overrides everything) OR
  `arms_differ_verified` false for any seed OR `>= 2/3` seeds `seed_fails_hard` OR cardinality breach
  (`actual_n_units != expected_n_units = n_seed_salts * 4`).
- **MIDDLE_BAND**: otherwise (mixed signal across seeds).

Honest guard: HARD_PASS on this cell means "grow-from-reading shows real, scramble-beating, growing signal on
a minimal probe -- worth scaling." It does NOT mean "the parser is solved." HARD_FAIL/MIDDLE_BAND localizes
what additional machinery (richer fragment grain, real lexicalization, larger corpus) this minimal form lacks.

## SCHEMA-VET checklist

```yaml
cardinality_ok: true  # EXPECTED_N_UNITS = n_seed_salts * 4 sweep sizes (smoke: 1*4=4; full: 3*4=12); verdict
                       # logic counts actual_n_units and HARD_FAILs on mismatch (META_RULE_H)
arms_differ_verified: true  # real vs scrambled induced-inventory hash differ (META_RULE_AF), checked per seed
final_metrics_atomicity: tmp_replace  # META_RULE_AH
crlb_n/a: "no quantitative noise floor formula for discrete construction-coverage counting; validated instead
  via scramble must-fail control + 3-independent-split robustness (functionally the same role as a CRLB floor)"
baseline_in_band: true  # HAND_RULE arm coverage on full held-out (0.36-0.43 measured pre-design) is within
  # [0.05, 0.95]; SCRAMBLE is an intentional floor-control, exempt by design (it is SUPPOSED to sit near floor)
discriminator_survives_scale: "Option A -- smoke uses the SAME full sweep (including the full-induction-pool
  point) as FULL; whole-corpus wall time < 2s, no scale-dependent saturation risk"
hard_pass_strictly_above_floor: true  # 0.15 floor vs pre-design-measured 0.28-0.36 (wide margin, not
  # floor-hugging)
hp_scope:
  GROWN: [tail_root_coverage_at_full_induction, growth_curve_slope, scramble_margin]
  HAND_RULE: []  # reference/control arm, reported not gated
  SCRAMBLE: []   # reference/control arm (must-fail floor), reported not gated
sweep_alignment_verdict: ALIGNED  # gate A -- nominal induction size (50/150/300/full) tracks actual size used
discriminating_fraction: 0.75  # gate B -- 3/4 sweep points per seed land in [0.05, 0.40] (not saturated/floor)
composition_edges: [{from: parse_conllu, to: fragment_extractor, verdict: SHAPE_MATCH},
                     {from: fragment_extractor, to: coverage_counter, verdict: SHAPE_MATCH}]  # gate C
positive_control_arms:
  - arm: HAND_RULE_REPRODUCE_AT_SAME_REGIME
    primitive: analyze_sentence (Rung 5, imported unmodified)
    cited_prior_metric: 0.599  # MEASURED@this-cell's own adhoc pre-design probe, n=846 full qualifying pool
    cited_prior_regime: {corpus: ud_ewt_test, filter: load_qualifying_sentences}
    test_regime: {corpus: ud_ewt_test, filter: load_qualifying_sentences}  # IDENTICAL (direct import, not
      # a reimplementation)
    tolerance: 0.05
    regime_extension_audit: SHAPE_MATCH  # same code object, same regime -- no drift possible
functional_requirements:  # gate E
  - requirement: "grow constructions from reading, no per-construction hand-authoring"
    mechanism: "frequency-counted POS+deprel fragment induction (new here; CITED@Bod-DOP + analogy to the
      existing ingest-gate unexpectedness primitive)"
  - requirement: "score/select fragments via surprisal"
    mechanism: "-log P over the induced frequency table (same scoring FORM as
      exp_codex_unexpectedness_incremental_value_v1's unexpectedness_pe)"
  - requirement: "measure held-out generalization, not memorization"
    mechanism: "disjoint sha256-digest sentence split (SPLIT_IDENTITY assert) + scramble must-fail control"
real_code_path_exercised: []  # gate F.1 -- N/A, no KGStore/FoundationStore/substrate-fit objects touched
substrate_signature_checked: []  # gate F.2/F.3 -- N/A, same reason
guard_baseline_validated: []  # gate F.4 -- N/A, no control-beats-POP-style guard in this cell
deterministic_seeding: true  # gate F.5 -- all splits/scrambles derive from hashlib.sha256 digests of stable
  # string keys; never Python's salted hash() nor list(set(...)) ordering
cell_chunked: false  # exemption: total wall time for ALL 3 seeds pooled is ~1s (pure Python dict counting over
  # 846 pre-parsed sentences); chunking overhead is disproportionate to trivial compute (spirit of the rule is
  # protecting expensive/long-running work from partial loss, not gating sub-second cells)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true  # single heartbeat tick at run end (compute is sub-second; no mid-run cadence needed)
defensive_error_checking: passed_all_4_patterns
progress_logging: "n/a (timeout_s << 1800; cell completes in ~1-8s wall)"
calibration_check: "default_ok_for_this_regime"  # MIN_COUNT=2 entrenchment threshold; evidenced by pre-design
  # probe (non-vacuous, non-saturated coverage) + non-gating min_count_sensitivity diagnostic (MIN_COUNT in
  # {1,2,3}) reported in metrics.json per seed
```

## Compute / dispatch

- Smoke: seedA only, same full sweep (Option A). MEASURED@smoke: HARD_PASS, elapsed_s=1.06, growth=[0.048,
  0.153, 0.202, 0.355], scramble_at_full=0.016, margin=0.339.
- Full: all 3 seed-salts (seedA/seedB/seedC), expected_n_units=12.
- Timeout: 120s (measured full-corpus wall for 1 seed x 4 sweep points ~1s internal / ~8s process-including
  startup; 3 seeds well under 30s total; 120s gives a wide safety margin, no scaling risk since compute is
  O(n_sentences) pure-Python counting, not a matrix op).
- Route: `local_cpu_queue` (no SCP, no push, no atomize -- per this task's explicit routing; local compute
  re-authorized for FULL runs per MEMORY.md 2026-07-15 note).
- Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before queue_add.
