# Pre-reg: grounded-ingest-at-scale Phase-0 go/no-go -- exact-ID join hit-rate on the sparse tail

**Filed by:** exp_dev | **Date:** 2026-07-14 | **Cell:** `experiments/exp_grounded_ingest_tail_join_v1.py`
**Spec source:** `notes/research_grounded_ingest_at_scale_2026-07-14.md` ("Cheap decisive test" + "First buildable step")

## What this measures

A DATA-JOIN MEASUREMENT, not a training run. Determines whether external bulk
MEASURED data (Wikidata quantity-typed claims) can reach the substrate's
sparse-tail (support<=1) entities via EXACT-ID join only (no fuzzy match, no
embedding match, no LLM). This converts "grounded ingest fixes the sparse
tail" from an aspiration into a measured go/no-go number.

## Entity ID namespace (determined FIRST, per task mandate)

`hdlab/kg_traversal.py::KGStore` holds only integer-indexed codebooks; the
actual string entity-ID namespace lives in
`data/substrate_index/concept/relations.jsonl` (`src_id`/`tgt_id` fields), the
189,654-edge CSKG-derived graph cited in the drill note ("~190k relations,
71k SYNONYM, 62k IS_A"). MEASURED@this-session (direct file scan):

- Prefix composition of all 141,511 entities: CN_ 133,305 (94.2%, ConceptNet
  lemma, e.g. `CN_earldom`), WN_ 6,310 (4.5%, WordNet synset id, e.g.
  `WN_rectangle.n.01`), FN_ 1,198 (0.85%, FrameNet frame name), plus a small
  tail of non-lexical provenance/admin refs (SLASH_OTHER 622, EXP 22, CAP 21,
  LEX 18, RETRIEVAL 4, OTHER 9, unified 1, FINDING 1 -- e.g.
  `RF/research_drill_rmt_beyond_free_probability_2x_2026_06_11`, clearly not
  concept nouns, a data-quality artifact from cross-corpus relation merging).
- **`metadata` field is `{}` (empty) on every relations.jsonl row** (matches
  drill note's "metadata EMPTY on 100%") -- CONFIRMS the task's anticipated
  infeasibility: **there is no persisted external-ID crosswalk field (no
  Wikidata QID, no CAS, no InChIKey) on any CSKG node.** A true foreign-key
  ID-join is infeasible by construction.
- **Operationalization used instead (still "exact match", not fuzzy):**
  Wikidata's own canonical exact-ID mechanism is the enwiki-sitelink <-> QID
  binding (this is literally what OpenRefine+Wikidata reconciliation's exact
  mode uses, cited in the drill note's citation list). We normalize each
  CN_/WN_/FN_ id to a candidate enwiki page TITLE via a deterministic,
  documented rule (strip prefix; for WN_ additionally strip the WordNet
  sense suffix `\.[a-z]\.\d+$`; underscores -> spaces; capitalize first
  character only) and query `action=wbgetentities&sites=enwiki&titles=<title>`.
  This is an EXACT title-string lookup (the API returns `missing` with zero
  fuzzy fallback) -- no substring search, no `wbsearchentities`, no embedding.
  This is the fair, disclosed operationalization of "exact-ID join" given the
  namespace reality; flagged here rather than silently forcing a fuzzy match.

## Sparse-tail sampling (MEASURED@this-session)

- Population: entities with `prefix in {CN,WN,FN}` (lexical/concept types
  only -- the 400 non-lexical provenance-artifact entities at support<=1 are
  EXCLUDED and reported, not silently dropped) AND `degree(support) <= 1` in
  `concept/relations.jsonl`. Pool size: 83,138 (of 141,511 total entities;
  59% of ALL entities in this graph are support<=1).
- **Scoping note (HYPOTHESIZED->clarified during authoring):** "support=0"
  entities as such do not exist as addressable nodes in this specific graph
  file (a relations.jsonl edge-list only contains entities that appear in
  >=1 edge). The drill note's "cold=0-support" framing refers to the
  substrate's bottleneck in general; for THIS measurable graph slice the
  sparse tail is operationalized as **support==1** (the well-defined,
  measurable majority: 83,538 of 83,538+support-0-elsewhere). This is
  disclosed, not hidden -- see "Crossing-threshold metric caveat" below for
  the consequence.
- Sample: 500 entities, deterministic via `sha256('SEED42_LEXICAL_TAIL::' +
  entity_id)` ascending sort, first 500. Composition: CN_ 476, WN_ 21, FN_ 3.
- Source file provenance pinned: `data/substrate_index/concept/relations.jsonl`
  sha256 `d88acf2055fd986d67ea26eb79481bdf172f3284207e26f4679795fb73790e6d`,
  18,304,525 bytes, mtime 1781907852.0.

## Cached snapshot (why this cell is network-free at remote-dispatch time)

None of the ~110 experiment cells in this repo make live HTTP calls at
runtime (grepped `requests\.|urllib.request` across `experiments/*.py`: zero
hits) -- live network dependency inside an unattended remote-queued cell is
an untested pattern and a `SCRIPT_PRECONDITION_VIOLATION` risk (remote
firewall/rate-limit/DNS could differ from the authoring environment). The
500-entity join was performed ONCE, interactively, with an internet-capable
Bash session, with retries and a scramble-control sanity check (below), and
the full result is committed at
`data/exp_grounded_ingest_tail_join_v1/wikidata_tail_join_snapshot_500.json`
(full provenance block: fetch method, endpoint, per-entity title/QID/claim
result, scramble-control repeats). The CELL recomputes the tail sample
IDENTICALLY from the committed `concept/relations.jsonl` (present in the
repo on any checkout, local or remote) and cross-validates entity-for-entity
identity against the cached snapshot before trusting it (a mismatch is a
HARD_FAIL, not a silent pass-through) -- this is a deterministic, remote-safe
reproduction of a real, already-measured join, not a live network call.

## MEASURED result (this session, direct join, not simulated)

- **Join hit-rate: 9/500 = 1.80%** MEASURED@`data/exp_grounded_ingest_tail_join_v1/wikidata_tail_join_snapshot_500.json:results`
  (hit = exact enwiki-title match to a live QID AND that QID carries >=1
  claim with `mainsnak.datatype == "quantity"`, e.g. P2067 mass, P2046 area,
  P1082 population -- genuine numeric-literal claims, not identifier claims).
- Missing (no exact title match at all): 377/500 = 75.4%.
- Found title, zero quantity-typed claims: 114/500 = 22.8%.
- The 9 hits are plausible and non-spurious on manual inspection (Reims,
  Assam, Taipei -> population/area; silicon dioxide, potassium cyanide,
  cephaloridine -> mass/density -- concrete nouns exactly matching the
  drill's "concrete/basic-level anchors ground first" prediction).
- **Scramble/wrong-ID negative control (Gate F.4 style, required by task):**
  3 repeats x 15 character-scrambled titles derived from real tail lemmas
  (same length/alphabet, near-certain non-words) queried through the
  identical pipeline: **0/45 hits across all 3 repeats (0.0%)**, robustly
  below the 5% HARD-FAIL floor with margin. Confirms the exact-match method
  has real discriminating power (majority of genuine queries already miss;
  gibberish queries miss universally) and is not spuriously matching
  anything thrown at it.

## Falsifiable predictions (PRE-REGISTERED bands, per drill note verbatim)

- **HARD-PASS:** join hit-rate >= 15% AND (of hits) >= 50% cross from
  support<=1 to support>=2 by gaining the literal edge.
- **HARD-FAIL:** join hit-rate < 5%.
- **MIDDLE-BAND (5-15%):** partial coverage -- proceed but scope first
  production ingest to the sub-domains that DID hit, not a general claim.
- **Middle-band handling (exp_dev's call, per task autonomy declaration):**
  if MIDDLE-BAND lands, do NOT auto-dispatch Phase 1-3 of the drill's build
  plan; file a routing note back to research/director recommending scoped
  sub-domain ingest (e.g. "materials/chemistry/geography nouns only") rather
  than treating it as license for the general literal-fusion pipeline.

## Crossing-threshold metric caveat (honest disclosure, META_RULE_AC)

Because the operational tail is scoped to support==1 (see Scoping note
above), for EVERY hit entity, adding exactly 1 grounded literal-edge moves
support 1 -> 2, which trivially satisfies ">= 2-support" by construction.
The "% of hits that cross the threshold" metric is therefore analytically
==100% for this scoping and does NOT independently discriminate anything --
it is reported for completeness (drill note asked for it explicitly) but
flagged HERE as a degenerate corollary of the support==1 scoping, not a
second genuine signal. The one genuinely informative number in this cell is
the join **hit-rate**. A future cell targeting genuine 0-support entities
(which would require a different entity-enumeration source than this
edge-list-only graph file) is the right vehicle for a non-degenerate
crossing-threshold measurement.

## Functional requirements (Gate E)

| Requirement | Primitive/method used |
|---|---|
| Sample real current sparse-tail entities | direct degree scan of `concept/relations.jsonl` |
| Determine actual joinable ID namespace | prefix audit (CN/WN/FN vs provenance artifacts) BEFORE designing the join |
| Exact-ID join, no fuzzy/embedding | Wikidata `wbgetentities&sites=enwiki&titles=` exact title lookup |
| Prove the join mechanism discriminates | scramble/gibberish-title negative control, 3 repeats |
| Remote-safe reproducibility | cached snapshot + entity-identity cross-validation at cell runtime |

## Gate declarations (SCHEMA-VET checklist)

- `sweep_alignment_verdict: N/A` -- no swept parameter axis; single-shot join
  measurement over a fixed 500-entity sample.
- `discriminating_fraction: N/A` -- not a parameter sweep.
- `composition_edges: N/A` -- no primitive-to-primitive composition; this
  cell does not construct or call any substrate object (no `KGStore`, no fit
  module, no embedding). It is a pure external-data-join measurement.
- `positive_control_arms: N/A` -- no prior chain-grade primitive is being
  invoked or reproduced; this is a new data-plumbing measurement opening a
  new field (per the drill note's own framing), not a composition of
  existing substrate mechanisms.
- `functional_requirements`: see table above (Gate E satisfied).
- `real_code_path_exercised: N/A (declared None, justified)` -- no substrate
  entrypoint (KGStore/fit fn) is invoked by this cell; Gate F.1
  (`assert_real_code_path_exercised`) is passed `None` deliberately (MISSING
  path -> warns, never blocks) with this explicit rationale on record.
- `substrate_signature_checked: N/A (declared None, justified)` -- same
  rationale; no substrate callable is invoked.
- `guard_baseline_validated: [scramble_control]` -- Gate F.4-style guard
  implemented via `assert_negative_control_fails_with_margin` in self-test:
  `control_scores=[0.0,0.0,0.0]` (3 scramble repeats), `headline_threshold=0.05`
  (the HARD-FAIL floor), `margin=0.02`, `n_repeats_min=3`. Must robustly pass
  (scramble stays well under threshold-margin) or self-test fails loud.
- `arms_differ_verified: N/A` -- no parallel arms produce tensors to compare;
  the single measurement IS the arm. Exempted with rationale.
- `cardinality_ok: true` -- `EXPECTED_N_UNITS = 500` (tail sample size);
  verdict logic asserts `len(per_entity_results) == 500` exactly, else
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `cell_chunked: false` -- single-shot, no seed axis (deterministic join over
  a fixed sample; nothing to chunk).
- `start_marker_written: true`, `crash_diagnostic_present: true`,
  `heartbeat_present: false (timeout_s < 1800, not mandatory; job completes
  in seconds since it is pure local IO + dict ops, no network at cell
  runtime)`, `defensive_error_checking: "passed_all_4_patterns"`.
- `final_metrics_atomicity: "tmp_replace"`.
- `progress_logging: "print_flush_true"` (declared even though not mandatory
  at this timeout, for consistency).
- `crlb_n/a: "no quantitative noise-floor/argmax discriminator; this is a
  binary exact-match join measurement, not a capacity/noise regime"`.
- `calibration_check: "default_ok_for_this_regime"` -- thresholds (15%/5%)
  are taken verbatim from the pre-registered drill note, not tuned post-hoc.
- `baseline_in_band: N/A` -- no baseline arm in the usual sense; the scramble
  control plays that role and is explicitly required to be near-zero (NOT
  in a 0.05-0.95 "band"), which is the correct expectation for a must-fail
  guard, not a baseline-in-band arm.

## Compute architecture

- Class: **(b) sequential-CPU with justification.** This is a pure
  dict/JSON-scan measurement over 500 entities plus a 189,654-line jsonl
  degree scan (a few seconds of I/O-bound work). No matmul, no GPU
  primitive, no batching opportunity -- wall time well under 10s.
- Storage strategy: **no_storage / no_composition** -- this cell measures an
  external-data join; it does not write to the substrate's KGStore or
  atoms.jsonl, and performs no chained/composed retrieval.

## Dispatch

- Target queue: `remote_cpu_queue` (per task instruction: "remote_cpu"; also
  matches CLAUDE.md/MEMORY.md discipline that experiment execution routes
  off the laptop). No GPU need (pure CPU/IO), no cloud-GPU justification.
- Timeout: 300s (generous margin over the <10s local-measured smoke time;
  this is not a scaling cell so no N-dependent timeout formula applies --
  fixed 500-entity sample both at smoke and full).
- `run_mode` defaults to `full` in this cell (per RUN_MODE VERIFICATION
  discipline: no separate smoke/full split needed since the full run IS the
  cheap 500-entity join reproduction; `--self-test` is the explicit opt-in
  for the reduced self-check path, not the default).
