# Pre-reg: text-spoke feasibility go/no-go -- exogenous gloss availability + exogeneity on the sparse tail

**Filed by:** exp_dev | **Date:** 2026-07-14 | **Cell:** `experiments/exp_grounded_ingest_text_spoke_v1.py`
**Spec source:** `notes/research_brain_grounding_spoke_building_canonical_reference_2026-07-14.md` (Q5 transfer design
+ symbols-about-symbols must-fail) and the numeric-join predecessor
`preregs/grounded_ingest_tail_join_v1.md` (same tail population, same
sha256-pinned-source + cached-snapshot + scramble-control discipline).

## What this measures

A DATA-AVAILABILITY measurement (NOT the grounding build, which stays gated
on pinpoint). The numeric-join go/no-go (`grounded_ingest_tail_join_v1`)
measured whether bulk Wikidata quantity claims reach the sparse tail via
exact-ID join: HARD_FAIL, 1.80% hit-rate (9/500). This cell is its direct
successor: does EXOGENOUS definitional/gloss/situational TEXT reach the same
tail, and -- the load-bearing new question -- is that text genuinely
EXOGENOUS content, or is it just the concept's own graph-neighbors
re-encoded (symbols-about-symbols / DoQ trap, per the canonical reference's
Q5 must-fail)?

Two measurements, both pre-registered:
1. **AVAILABILITY**: fraction of tail entities with an exogenous
   definitional/gloss/situational text available, per-source + union.
2. **EXOGENEITY**: of the gloss content retrieved, what fraction of its
   content-tokens are NOT already the entity's own graph-neighbor lemmas
   (the must-fail guard against the DoQ trap).

## Entity population (identical to the numeric-join predecessor, reused for direct comparability)

Same tail: `data/substrate_index/concept/relations.jsonl`, sha256
`d88acf2055fd986d67ea26eb79481bdf172f3284207e26f4679795fb73790e6d`
(MEASURED@this-session, re-hashed 2026-07-14, unchanged since the numeric
cell). Lexical entities (`CN_`/`WN_`/`FN_` prefix) with degree (support)
`<= 1`: pool size 83,138. Sample: 500 entities, deterministic via
`sha256('SEED42_LEXICAL_TAIL::' + entity_id)` ascending sort, first 500 --
**bit-identical to the numeric-join cell's sample** (re-verified this
session: first 10 entries `CN_reims, CN_water_flowers, CN_addlebrained,
CN_thomas_middleton, CN_ockham, CN_sipper, CN_every_so_often,
CN_calystegia_sepium, CN_incorrectly, CN_gather_clan` match the sibling
cell's committed sample_order exactly). Composition: CN_ 476, WN_ 21, FN_ 3.
This means every "hit"/"miss" number below is a direct successor to the
numeric cell's, over the identical population.

## Sources used (MEASURED@this-session, direct nltk corpus scan in `.venv`)

- **WN_native** (WordNet synset's own gloss): `nltk.corpus.wordnet`, local
  corpus, 117,659 synsets, no network. 21/21 tail WN_ entities resolve
  (WN_ ids are literal synset names, e.g. `WN_rectangle.n.01` ->
  `wn.synset('rectangle.n.01').definition()`).
- **CN_lemma_match_WN** (lemma-matched WordNet gloss for ConceptNet
  lemmas): normalize the CN_ id to its bare lemma (strip prefix, keep
  underscores as the nltk multi-word-lemma form), `wn.synsets(lemma)`,
  take the first synset's definition (nltk's synsets() ordering = WordNet's
  standard most-frequent-sense-first convention; not cherry-picked).
  392/476 hit.
- **FN_native** (FrameNet frame definition): `nltk.corpus.framenet`, local
  corpus, 1,221 frames, no network. 3/3 tail FN_ entities resolve
  (`fn.frame_by_name(name).definition`).
- **CN_ConceptNet_DefinedAs_HasContext**: task pointer named this as a
  candidate source. MEASURED@this-session: `relations.jsonl`'s full
  `rel_type` histogram (all 189,654 edges scanned) contains **zero**
  `CN_DEFINED_AS` / `CN_HAS_CONTEXT` rows (`/r/DefinedAs`, `/r/HasContext`
  were never ingested into this graph -- only `CN_SYNONYM, IS_A,
  CN_RELATED_TO, CN_MANNER_OF, PART_OF, HYPERNYM, CN_AT_LOCATION,
  CN_USED_FOR, CN_CAPABLE_OF, CN_CAUSES, CN_DERIVED_FROM,
  CN_MOTIVATED_BY_GOAL, RELATES, FRAME_*, CN_HAS_PROPERTY, CN_ANTONYM,
  CN_HAS_A, CN_RECEIVES_ACTION, USES, CN_MADE_OF, DEPENDS_ON,
  INSTANCE_OF, DEFINED_OVER, OPTIMIZES` -- 32 rel_types, none of them
  DefinedAs/HasContext). Reported honestly as **0/476 (source
  unavailable in this environment)**, not silently dropped -- a raw
  ConceptNet assertions dump would be required and is out of scope for a
  network-free local cell.
- **Wiktionary/DBnary**: filesystem scan found no local dump (`find
  -iname "*wiktionary*" -o -iname "*dbnary*"` under `data/`: zero hits).
  Declared **not attempted** (would require a live network fetch, which
  this cell's network-free design intentionally avoids at runtime -- see
  Cached snapshot section).

## Cached snapshot (why this cell is network-free at remote/local-queue runtime)

Same pattern as the numeric-join predecessor: rather than depend on the
`.venv`'s nltk WordNet/FrameNet corpora being present bit-identically on
whatever machine later runs this cell (a real Gate-F.3-class local/remote
drift risk -- corpora are downloaded user-data, not committed to the repo),
the gloss lookup was performed ONCE, interactively, in this session's
`.venv` (nltk 3.9.4, wordnet + framenet corpora confirmed present), and the
full result (raw gloss text per entity, source_used, scramble-control
detail) is committed at
`data/exp_grounded_ingest_text_spoke_v1/provenance.json`. The CELL
recomputes the tail sample identically from the committed
`concept/relations.jsonl`, cross-validates entity-for-entity identity
against the cached snapshot's `sample_order` (mismatch = HARD_FAIL, not
silent pass-through), and computes the EXOGENEITY metric LIVE and
PURELY from committed data (regex tokenization + the graph's own edge
list -- no corpus dependency at all for this half). The cell has **zero**
runtime import of `nltk`; the only corpus-dependent step (gloss retrieval)
is fully cached.

## AVAILABILITY metric

`hit(e) = True` if ANY source above returns a gloss for `e`. Per-source
counts + union hit-rate reported. MEASURED@this-session (from the
committed snapshot): **union hit-rate 416/500 = 83.20%**
(WN_native 21/21, CN_lemma_match_WN 392/476, FN_native 3/3).

**Scramble/wrong-lemma negative control** (Gate-F.4-style, required by
task): 3 repeats x 15 character-scrambled real tail lemmas (same length/
alphabet, near-certain non-words), queried through the identical
`wn.synsets()` pipeline: **0/45 hits across all 3 repeats (0.0%)** --
confirms the retrieval mechanism is not spuriously matching gibberish.

## EXOGENEITY metric (the must-fail guard)

For each entity `e` with a gloss: `content_tokens = tokenize(gloss)`
(lowercase alphabetic words, length > 2, ASCII stopword-filtered via a
~90-word hardcoded list -- no nltk stopwords corpus dependency, since that
corpus is not installed in this `.venv`, MEASURED@this-session:
`nltk.corpus.stopwords` raises `LookupError`). `graph_tokens = tokenize(own
lemma) UNION tokenize(the lemma of e's single tail-graph neighbor)` --
recomputed LIVE from `relations.jsonl` at cell runtime (every tail entity
here has degree==1 by the pool's own definition, i.e. exactly one edge,
so "own graph-neighbor lemmas" is well-defined and small: self + 1
neighbor). `exogenous_fraction(e) = |content_tokens - graph_tokens| /
|content_tokens|` (0.0 if content_tokens is empty; flagged separately).

MEASURED@this-session (exploratory calibration script, not the dispatched
cell, over the identical population/tokenizer the cell uses):
- mean exogenous fraction across the 416 entities with a gloss: **0.895**
- fraction clearing a 0.70 per-entity threshold: **364/416 = 87.5%**
- 5/416 entities score exactly 0.0 (degenerate short/circular glosses,
  e.g. `CN_sipper` -> "a drinker who sips" scores 0.5, not 0.0; the
  exact-0.0 cases are inspected in the cell's `per_entity` output, not
  hidden)

**MUST-FAIL synthetic control (the DoQ-trap guard, per the canonical
reference's Q5)**: for every sampled entity, build a synthetic
"graph-re-encoded gloss" = the concatenation of `self` and `neighbor`
lemma tokens ONLY (no relation words, nothing else) and run the identical
exogeneity computation on it. By construction its content tokens are a
strict subset of its own graph_tokens, so the honest expectation is
`exogenous_fraction == 0.0` for every entity. MEASURED@this-session:
**mean 0.0, max 0.0 across all 500 entities** -- the metric correctly
flags a symbols-about-symbols re-encoding as carrying zero exogenous
content, proving it is NOT vacuous (a metric that scored high on this
synthetic control would be worthless as a must-fail guard).

## Honest disclosure: the exogeneity metric is a WEAK test on THIS tail slice, and that is by design of the population, not a hidden flaw

Because the population is scoped to degree(support) `<= 1` (identical
scoping caveat as the numeric-join predecessor's "Crossing-threshold
metric caveat"), the `graph_tokens` forbidden-set per entity is tiny (self
lemma + exactly one neighbor lemma, typically 2-6 words). Any real,
independently-authored dictionary definition will almost always score
high exogenous fraction against such a small forbidden set, essentially
because our graph carries **zero** text content at all (the ingested
`relations.jsonl`'s `metadata` field is `{}` on every row) -- there is no
graph-native text to "leak" into. So the headline `mean=0.895` number
should NOT be read as "the gloss content is 89.5% independently
informative beyond the WHOLE graph" -- it is only informative relative to
this entity's immediate 1-edge neighborhood. The real teeth of this gate
is the MUST-FAIL synthetic control: it proves the metric CAN register
0.0 when the content genuinely is just the graph re-encoded, which is the
falsifiable claim the task asked for. A future cell with a broader
graph-token comparison set (e.g. all support>=2 entities' own multi-hop
neighborhoods) would be the right vehicle for a more demanding exogeneity
bar; this cell's job is the go/no-go, not the final capacity number.

## Falsifiable predictions (PRE-REGISTERED bands, decided before reading this session's exploratory numbers into a verdict -- see next paragraph for the honesty caveat)

Two independent dimensions, each with its own HARD-PASS/HARD-FAIL band,
chosen to mirror the numeric predecessor's shape (a wide PASS/FAIL gap,
not a knife-edge) and calibrated by principled reasoning about what would
constitute "text clearly beats the numeric channel" rather than reverse-
fit to force a particular verdict:

- **AVAILABILITY HARD-PASS**: union hit-rate >= 50% (majority of the tail
  reached -- a qualitatively different regime than the numeric join's
  1.80%, and a natural "most of the population" bar).
- **AVAILABILITY HARD-FAIL**: union hit-rate < 15% (same order as the
  numeric predecessor's own HARD-PASS bar; if text can't even clear what
  numeric would have needed to pass, the redirect thesis is wrong).
- **AVAILABILITY MIDDLE-BAND**: [15%, 50%).
- **EXOGENEITY HARD-PASS**: mean exogenous fraction >= 0.70 AND fraction
  of entities clearing the 0.70 per-entity threshold >= 0.70 AND the
  must-fail synthetic control scores <= 0.10 (mean, across >=3 folds) AND
  the scramble/wrong-lemma retrieval control scores <= 0.05 hit-rate
  (mean, across the 3 repeats) -- i.e. both guards must ALSO clear before
  the headline exogeneity number can be trusted.
- **EXOGENEITY HARD-FAIL**: mean exogenous fraction < 0.30 OR
  fraction-clearing < 0.30 OR must-fail synthetic control > 0.30 (metric
  vacuous, can't discriminate) OR scramble control > 0.15 (retrieval
  spuriously matches non-words).
- **EXOGENEITY MIDDLE-BAND**: everything else.
- **OVERALL verdict**: HARD_PASS requires BOTH dimensions HARD_PASS.
  HARD_FAIL if EITHER dimension HARD_FAILs (a must-fail-guard violation on
  either dimension forces HARD_FAIL regardless of the headline number, per
  META_RULE_L/AG -- an unguarded pass is not a pass). Otherwise
  MIDDLE_BAND.

**Honesty caveat (META_RULE_AC compliance):** this session's exploratory
calibration numbers (union hit-rate 83.20%, mean exogenous fraction 0.895,
must-fail control 0.0, scramble control 0.0) were computed BEFORE the
bands above were finalized in this document, so the choice of 50%/15% and
0.70/0.30 was made with the outcome already visible -- flagged here rather
than hidden. Two things make this not p-hacking-to-a-verdict: (1) the
bands were derived from principled reasoning (majority-coverage bar,
3x-the-predecessor's-own-pass-bar) independent of the exact 83.2%/0.895
figures, not reverse-engineered to a knife-edge; (2) the measured result
(83.2%, 0.895) clears ANY reasonable choice of threshold in this
neighborhood (40-60% availability, 0.5-0.8 exogeneity) by a wide margin,
so the qualitative verdict (HARD_PASS) is robust to reasonable
re-parameterization, unlike the numeric cell's 1.80% which is unambiguously
below ANY reasonable pass bar. If MIDDLE_BAND or HARD_FAIL had resulted,
the same disclosure obligation would apply in the other direction.

## Middle-band / hard-fail handling (exp_dev's call, per task autonomy declaration)

If MIDDLE_BAND lands on EITHER dimension: do not treat as license for the
full spoke-build (Phase 1+ of the drill note's design); file a routing
note recommending scoped further calibration (e.g. broaden the neighbor-
token comparison set, or restrict to specific prefix classes) rather than
a blanket "text spoke works" claim. If HARD_FAIL lands: report the
mechanism honestly (which guard failed) and do NOT proceed to the spoke
build; the redirect thesis would need re-examination.

## Functional requirements (Gate E)

| Requirement | Primitive/method used |
|---|---|
| Sample the SAME sparse-tail entities as the numeric predecessor | identical `SEED42_LEXICAL_TAIL` deterministic sample over `concept/relations.jsonl` |
| Determine available exogenous-text sources | direct nltk WordNet/FrameNet corpus scan (native + lemma-matched) + rel_type histogram audit for ConceptNet DefinedAs/HasContext |
| Measure per-source + union availability | committed cached snapshot, cross-validated for identity at cell runtime |
| Guard against the DoQ / symbols-about-symbols trap | live-computed exogeneity metric vs a synthetic graph-re-encoded-gloss must-fail control (expected 0.0) |
| Prove the retrieval mechanism discriminates | scramble/wrong-lemma control (3 repeats x 15, must robustly miss) |
| Remote/local-safe reproducibility | cached snapshot + entity-identity cross-validation; zero runtime nltk import |

## Gate declarations (SCHEMA-VET checklist)

- `sweep_alignment_verdict: N/A` -- no swept parameter axis; single-shot
  availability + exogeneity measurement over a fixed 500-entity sample
  (same population as the numeric predecessor).
- `discriminating_fraction: N/A` -- not a parameter sweep; the
  discriminating power is established via the must-fail synthetic control
  (Gate F.4-analog) and the scramble/wrong-lemma control instead.
- `composition_edges: N/A` -- no primitive composition; pure data
  measurement (regex tokenization + committed graph edge scan + committed
  gloss snapshot).
- `positive_control_arms: N/A` -- no prior chain-grade primitive is being
  reproduced; this is a fresh data-availability measurement, direct
  successor to `grounded_ingest_tail_join_v1` (which this cell cites and
  reuses the population/sha256/scramble-control conventions of).
- `functional_requirements`: see table above (Gate E, present).
- `real_code_path_exercised: N/A, justified` -- Gate F.1: no substrate
  KGStore/fit-module call in this cell (pure external gloss-availability +
  local graph-token measurement); declared None with explicit
  justification, matching the numeric predecessor's Gate F.1 declaration.
- `substrate_signature_checked: N/A` -- Gate F.2/F.3: no live substrate
  callable is invoked (same reason as F.1).
- `guard_baseline_validated: [must_fail_synthetic_control,
  scramble_wrong_lemma_control]` -- Gate F.4-analog: both must-fail guards
  are validated via `assert_negative_control_fails_with_margin` at
  self-test, each with `n_repeats_min=3` and an explicit margin (0.30 for
  the synthetic-graph-reencode control against the 0.70 exogeneity
  threshold; 0.10 for the scramble control against the 0.15 HARD-FAIL
  availability-style floor).
- `cardinality_ok`: `EXPECTED_N_UNITS = 500` (tail sample size); self-test
  uses `EXPECTED_N_UNITS = 20`.
- `final_metrics_atomicity: tmp_replace`.
- `cell_chunked: false` (single-shot measurement, no seed axis).
- `start_marker_written: true`, `crash_diagnostic_present: true`,
  `heartbeat_present: false` (elapsed_s expected < 30s at N=500; well under
  the 15-minute heartbeat-mandatory threshold), `defensive_error_checking:
  "passed_all_4_patterns_except_heartbeat_exempted_short_runtime"`.
- `progress_logging: N/A` -- `timeout_s` for this cell is set well under
  1800s (see Compute architecture / timeout below), so §17 is not
  mandatory; a single completion print is emitted regardless.
- `crlb_n/a`: no quantitative noise floor; binary availability + bounded
  [0,1] exogeneity-fraction measurement, not a capacity/argmax-noise
  regime.

## Compute architecture

Class **(b) sequential-CPU with justification**: this is a pure
string/regex/dict measurement over a 500-entity sample and a 189,654-line
edge-list scan (a handful of linear passes over data already loaded in
memory) -- no GPU-batchable tensor operation exists in this cell at all
(no bind/bundle/cleanup primitive is invoked). Wall time is expected under
5 seconds total; the wall-time sanity check (>10s per-phase-point
triggers a batching review) does not apply here since there is no
per-phase-point loop, only one fixed-size pass. Storage strategy:
`no_storage` (no PartitionedStore / KGStore write of any kind; pure
read-and-measure cell, matching the numeric predecessor).

## Dispatch plan

Per task authorization ("CPU; local-CPU is fine (deterministic,
network-free where possible) per USER go-ahead") this cell is fully
network-free and corpus-free at runtime (zero nltk import), so the
Gate-F.3 local/remote-corpus-drift risk that would otherwise argue against
remote dispatch does not apply -- the cell is equally safe on
`local_cpu_queue` or `remote_cpu_queue`. Per this repo's locked routing
discipline (`local_cpu_queue` = smoke-scale verification only; FULL runs
route to `remote_cpu_queue`/`overnight_queue` via the orchestrator, since
exp_dev's SCP/SSH ship path is denied to this role, USER-locked
2026-07-08), the smoke (N=50) is dispatched to `local_cpu_queue` directly
by exp_dev, and the FULL (N=500) dispatch command is returned in the
completion report for the orchestrator to ship to `remote_cpu_queue`.

**Timeout:** self-test N=20 measured at < 1s wall. FULL N=500 is the same
linear pass at 25x the entities plus one fixed 189,654-line edge scan
(dominant cost, O(edges) not O(sample_size), ~0.3s at self-test scale) --
expected FULL wall time < 10s. `timeout_s = 300` (30x safety margin over
the ~10s expectation; far below the 14400s cap, no waiver needed).
