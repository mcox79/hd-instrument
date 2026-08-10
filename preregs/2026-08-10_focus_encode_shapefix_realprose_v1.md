# Pre-reg: exp_focus_encode_shapefix_realprose_v1 (E3b aggregation-shape-fix gate)

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- cheap local cell).
Dispatched by Director/hdi_research with task-shape + the E3 diagnosis as pointers (exp_dev owns: exact
shape-fix parameters, bands, arm set, verdict logic).

Prior-work check (mandatory, 2026-07-01 USER-locked): `bash tools/substrate_query.sh "chunked focus
capacity-limited aggregation Cowan bounded working memory role structure scramble collapse event bundle
discrimination tense low-entropy dominance"` -> top hit cosine=0.3076, entity=
`notes/multi_sentence_situation_model_plan_2026-07-24.md::chunk020` -- this is the ORIGIN design note for
`hdlab/situation_focus.py` itself (the module this cell is asked to wire in), not a competing/duplicate
prior-art hit. Second/third hits (cosine 0.294-0.297) are the same lineage (the original
`exp_situation_model_event_bundle_focus_v1` PARTIAL landing that built `EventBundleCodec` +
`FlatFocus`/`ChunkedFocus`). No unrelated prior cell already ran this exact shape-fix-vs-scramble
diagnostic on real prose -- this is the direct, non-duplicative NEXT cell in the E3 lineage, not a
rediscovery.

## Question

E3 (`exp_focus_encode_grounded_event_discrimination_realprose_v1`, HARD_FAIL, gap_grounded=0.0542 vs
gap_bow=0.1452, scramble=0.0551 NOT collapsing i.e. scramble > grounded gap) diagnosed the cause as an
AGGREGATION-SHAPE problem, not a grounding problem: the flat multi-event bundle-SUM lets low-entropy
TENSE (SIMPLE_PAST = 60% of 994 events) dominate the accumulated bundle and swamp the PRED/AGENT/PATIENT
signal, so matched and wrong-pair cosines both land in a uniformly-high ~0.57-0.68 band with almost no
separation. Does FIXING THE AGGREGATION SHAPE -- (a) excluding the low-entropy TENSE role from the
bundle, or (b) replacing the flat bundle-SUM with Cowan-bounded CAPACITY-LIMITED chunked aggregation
(`hdlab.situation_focus.ChunkedFocus`) -- recover discriminative power, and (critically) does the
role-SCRAMBLE control NOW COLLAPSE under either fix (proof the structure, not just vocabulary
co-occurrence, is carrying the signal)?

## Design

REUSE, not re-ground: this cell imports `build_instance_role_events`, `build_grounded_codec`,
`select_sample`, `matched_wrong_gap`, `cosine`, `encode_instance_bow`, `encode_instance_structured` and
the constants `CORPUS_PATH, N_DIM=8192, SEED=7, HYPERNYM_DEPTH=3, DECAY=0.7, N_SCENARIOS_FULL=15,
MAX_PER_SCENARIO_FULL=4, N_SCENARIOS_SMOKE=5, MAX_PER_SCENARIO_SMOKE=3, NONE_FILLER` DIRECTLY from
`experiments.exp_focus_encode_grounded_event_discrimination_realprose_v1` (the E3 module) rather than
re-implementing the extraction/grounding pipeline. Same corpus, same deterministic `select_sample`
(`sorted()`, no `hash()`), same tiered WordNet/lexical-similarity grounding code -> the resulting 60
instances / 15 scenarios and the grounded symbol codebook are BIT-IDENTICAL to E3's, not merely similar.
A runtime positive-control check (see Gates) confirms this empirically by reproducing E3's BOW and
FLAT_GROUNDED (== E3's GROUNDED_STRUCTURED) gaps within tight tolerance before trusting the shape-fixed
arms.

Six arms per instance, all measured on the SAME extracted role_events + content_words (all vectors
bipolar {-1,+1} float32, `n_dim=8192`):

  - **BOW** (reference 0.1452): `encode_instance_bow(content_words, codec_ungrounded)` -- unchanged from
    E3, re-measured here as the positive-control anchor.
  - **FLAT_GROUNDED** (reference 0.0542): `encode_instance_structured(role_events, codec_grounded,
    scrambled=False)` -- E3's GROUNDED_STRUCTURED arm, re-measured bit-identically (second positive
    control).
  - **GROUNDED_DROP_TENSE** (shape-fix A): identical flat bundle-SUM aggregation, but each event is
    encoded from a 3-role subset `{PRED, AGENT, PATIENT}` only -- `codec_grounded.encode_event(rf_sub)`
    for `rf_sub = {k: rf[k] for k in ("PRED","AGENT","PATIENT")}` -- summed + quantized across the
    narrative's events, TENSE excluded entirely from the bundle. Uses the SAME role keys 0/1/2 (PRED/
    AGENT/PATIENT) as FLAT_GROUNDED (role key 3 = TENSE simply never touched), so this isolates
    "TENSE-exclusion" as the ONE variable vs FLAT_GROUNDED.
  - **GROUNDED_DROP_TENSE_SCRAMBLE**: same 3-role pipeline, but `codec_grounded.encode_scrambled_event
    (rf_sub, perm=[1,2,0])` -- a derangement over the 3 active role keys (PRED->AGENT's key, AGENT->
    PATIENT's key, PATIENT->PRED's key). Role<->filler binding destroyed within the surviving 3-role
    subset.
  - **GROUNDED_CHUNKEDFOCUS** (shape-fix B): identical per-event encoding to FLAT_GROUNDED (all 4 roles,
    `codec_grounded.encode_event(rf)`), but the AGGREGATION OPERATOR changes: each event vector is
    `push()`-ed in narrative order into a real `hdlab.situation_focus.ChunkedFocus(codec_grounded,
    capacity=4, fanout=2, seed=7)` (Cowan ~4-chunk bounded focus, module default), and the instance
    representation is `cf.focus_vec()` -- a bounded <=4-term superposition where the most recent ~4
    events/chunks are addressed at fixed slot keys and older events are recursively compressed into
    nested chunks (graceful degradation, not truncation). This isolates "capacity-bounded aggregation"
    as the ONE variable vs FLAT_GROUNDED (same per-event encoding, same codec, same events, same order).
  - **GROUNDED_CHUNKEDFOCUS_SCRAMBLE**: same chunked-aggregation pipeline, but each pushed event vector
    is `codec_grounded.encode_scrambled_event(rf, perm=[1,2,3,0])` -- E3's own 4-role derangement,
    applied at the per-event binding level before chunking (role structure destroyed at the finest
    grain, chunking/capacity-bounding left intact).

Discriminator: identical metric to E3 -- matched-pair (same-scenario) mean cosine minus wrong-pair
(different-scenario) mean cosine, over ALL pairwise instance comparisons in the sample (not a
sub-sample; ~1770 pairs at N=60).

Two shape-fixes are DELIBERATELY orthogonal (drop-TENSE changes per-event content only, keeps flat-sum
aggregation; ChunkedFocus changes the aggregation operator only, keeps full 4-role per-event content) so
a positive result on one and not the other is diagnostic of WHICH kind of shape-fix the flat bundle-SUM
needed.

## Compute architecture

Sequential-CPU. Justification: E3 (same corpus, same N=60, same tokenizer/grounding cost, a superset of
this cell's per-instance work) landed at `elapsed_s=4.705` FULL. This cell adds 4 extra arms per instance
(2 shape-fix + 2 scramble) at the same O(events) cost per instance -- still comfortably under 10s total,
no GPU benefit at this N. Storage strategy: no persistent storage (diagnostic-gate measurement cell).

## Bands (per task contract, USER/Director-specified; NOT re-derived)

Per-arm evaluation (`GROUNDED_DROP_TENSE` and `GROUNDED_CHUNKEDFOCUS`, each against its OWN scramble):
  - `reaches_bow_parity = gap_arm >= gap_bow` (gap_bow = THIS RUN's re-measured BOW gap, not a frozen
    constant -- literal reading of "reaches gap >= BoW").
  - `scramble_collapses = gap_arm > 0 AND gap_scramble_arm < 0.5 * gap_arm`.
  - arm tier: `HARD_PASS` if both hold; `MIDDLE_BAND` if exactly one holds; `HARD_FAIL` if neither holds.

Overall cell verdict = the BEST tier reached by either shape-fixed arm (`HARD_PASS` > `MIDDLE_BAND` >
`HARD_FAIL`); `best_arm` = the arm achieving that tier (tie-break: higher `gap_arm`).

  - **HARD-PASS**: at least one shape-fixed arm reaches BoW-parity AND its own scramble collapses
    (< 0.5x its gap).
  - **HARD-FAIL**: NEITHER shape-fixed arm reaches BoW-parity AND NEITHER arm's scramble collapses (i.e.
    both arms individually HARD_FAIL) -- the deep finding that the flat-bipolar-bundle role-structure
    shape is fundamentally wrong for this discrimination task, reported plainly, no epicycles.
  - **MIDDLE_BAND**: at least one arm reaches BoW-parity but its scramble does not collapse, OR at least
    one arm's scramble collapses but its gap stays below BoW-parity (and neither arm HARD_PASSes).

HP_SCOPE: bands apply to `GROUNDED_DROP_TENSE` / `GROUNDED_CHUNKEDFOCUS` only (+ their own SCRAMBLE
controls). `BOW` / `FLAT_GROUNDED` are RE-MEASURED reference/positive-control arms, not independently
gated (matches E3's HP_SCOPE convention).

## Gate D positive control (reproduce E3 as a REGIME-IDENTICAL reproduction, not a regime-extension)

```yaml
positive_control_arms:
  - arm: BOW_REPRODUCE
    cited_prior_atom: data/exp_focus_encode_grounded_event_discrimination_realprose_v1/metrics.json:gap_bow.gap
    cited_prior_metric: 0.14524914466660693   # MEASURED@data/exp_focus_encode_grounded_event_discrimination_realprose_v1/metrics.json:gap_bow.gap
    test_regime: IDENTICAL (same corpus, same select_sample code, same extraction code, imported not re-implemented)
    tolerance: 0.005
    if_outside_tolerance: HARD_FAIL_POSITIVE_CONTROL_REPRODUCTION_MISMATCH (downstream shape-fix arms untrustworthy -- reuse premise broke)
  - arm: FLAT_GROUNDED_REPRODUCE
    cited_prior_atom: data/exp_focus_encode_grounded_event_discrimination_realprose_v1/metrics.json:gap_grounded_structured.gap
    cited_prior_metric: 0.05424204209720129   # MEASURED@data/exp_focus_encode_grounded_event_discrimination_realprose_v1/metrics.json:gap_grounded_structured.gap
    test_regime: IDENTICAL
    tolerance: 0.005
    if_outside_tolerance: HARD_FAIL_POSITIVE_CONTROL_REPRODUCTION_MISMATCH
```

Both reference numbers are loaded LIVE from the E3 metrics.json at runtime (not hardcoded copies) so a
stale/regenerated E3 file cannot silently drift out of sync with the check. Applied at `--full` only
(the `--smoke` regime N differs from E3's FULL N so gap magnitudes are not expected to match at smoke
scale; smoke instead checks `baseline_in_band` per META_RULE_AG -- BOW/FLAT_GROUNDED gaps non-degenerate,
non-NaN, roughly consistent in sign/direction with FULL).

## Self-test / discriminator-fires gates

- Real-code-path: self-test constructs a REAL `hdlab.situation_focus.ChunkedFocus` (push + focus_vec),
  a REAL `hdlab.event_bundle.EventBundleCodec` (via the imported `build_grounded_codec`), and runs the
  full 6-arm pipeline on a tiny synthetic 4-instance/2-scenario corpus (not a toy-only branch).
- Reproduction-of-mechanism check: on the tiny synthetic corpus, this cell's own flat-aggregation helper
  (all 4 roles, unscrambled) must be BIT-IDENTICAL to E3's own `encode_instance_structured` on the same
  role_events (proves "reuses the SAME grounded fillers" at the mechanism level, not just "similar").
- `GROUNDED_DROP_TENSE` must differ from `FLAT_GROUNDED` on the tiny corpus whenever TENSE actually
  varies across events (sanity: dropping TENSE must change SOMETHING).
- `ChunkedFocus` active buffer must stay `<= capacity` after >capacity pushes on the tiny corpus (bounded
  behavior fires, not just "runs").
- `arms_differ_verified` (META_RULE_AF): all 6 arms pairwise hash-differ on the tiny synthetic corpus.
- `cardinality_ok` on the tiny corpus.
- `substrate_signature` check (§15 F.2): `ChunkedFocus.__init__` kwargs `{codec, capacity, fanout, seed}`
  bound against the live signature.
- `real_code_path` check (§15 F.1): declares `["EventBundleCodec", "ChunkedFocus", "build_grounded_codec",
  "select_sample"]` as FULL entrypoints; self-test exercises all four.

## Schema-vet fields

- `cardinality_ok`: EXPECTED_N_UNITS = len(sample) instances (pass-1 extraction, checkpointed).
- `arms_differ_verified`: bool, hash-differ across all 6 arms on real instance vectors (not just tiny
  synthetic corpus).
- `final_metrics_atomicity`: "tmp_replace".
- `except SystemExit: raise` before `except Exception` (no `BaseException`, no bare `except:`).
- `crlb_n/a`: "cosine-gap discrimination measurement on real narrative text; bands are drawn from THIS
  RUN's own re-measured BoW gap (self-referential threshold per task contract), not a synthetic capacity
  envelope -- no CRLB applies".
- `calibration_check`: "adaptive_with_discriminator_gate" -- `HYPERNYM_DEPTH=3`/`DECAY=0.7` inherited
  unchanged from E3 (not re-tuned; grounding is explicitly NOT the variable under test here).
  `CAPACITY=4`/`FANOUT=2` are the `hdlab.situation_focus.ChunkedFocus` module defaults (Cowan 2001
  citation baked into the module docstring), chosen before running, not tuned post-hoc against the gap
  numbers.
- `deterministic_seeding`: true (all randomness inherited from E3's `hashlib`-seeded/`sorted()` code
  path; no new `hash()`/`list(set())` introduced).
- `cell_chunked`: false (single instance-sample run); pass-1 extraction IS checkpointed via
  `tools/exp_checkpoint.py` (same pattern as E3).
- `progress_logging`: "print_flush_true" (declared for template parity; wall time is seconds).

## Report contract

All 6 arm gaps (BOW / FLAT_GROUNDED / GROUNDED_DROP_TENSE / GROUNDED_DROP_TENSE_SCRAMBLE /
GROUNDED_CHUNKEDFOCUS / GROUNDED_CHUNKEDFOCUS_SCRAMBLE), the scramble-collapse verdict per shape-fixed
arm, the positive-control reproduction check result, 2-3 concrete example passages with role_events, and
the overall verdict per the bands above. Per the Director's caveat: this is a BoW-favorable task (topic
content-words alone discriminate scenarios), so the PRIMARY diagnostic signal is whether SCRAMBLE
collapses under either shape-fix, not whether BoW-parity is beaten by a wide margin -- report both but do
not over-index on beating BoW.
