# Pre-reg: lexicon_coverage_audit_barrier2_v1

Date: 2026-07-17. Filed by: exp_dev (re-run of a cell that STALLED on 2026-07-17 due to
filesystem contention from a duplicate CPU-runner process, now cleaned up; re-authored
fork-independent of the Rung 5-9 real-prose reading arc per Director's explicit instruction).

## Trigger

Research's ranked-barriers synthesis (`notes/research_glassbox_realprose_reading_barriers_5x_drill_synthesis_2026-07-17.md`)
and lexicon-richness drill (`notes/research_lexicon_richness_subcategorization_barrier_real_prose_parsing_2026-07-17.md`)
name barrier #2 = LEXICON-MEANING-ATTACHMENT (subcat frames + selectional preferences), claimed DISTINCT from
barrier #5 = foundation/world-knowledge SIZE. Drill 4's section (b) part 1 specifies a coverage-audit as the
cheapest decisive first test of that claim (Prediction 2 in the drill note). This cell IS that audit.

## Question

1. What fraction of real-prose verb tokens/types fall inside existing free symbolic subcat/selectional
   resource coverage (VerbNet primary; PropBank + FrameNet cross-check)?
2. For covered verbs, at what granularity do argument-selectional needs resolve: TYPE-level (the verb's own
   subcat/selectional frame -- including catalogued sense-variants and idiom/MWE entries -- suffices, no
   world-fact about the specific referents needed) vs INSTANCE-level (correct interpretation needs a specific
   world/discourse fact about the particular entities named, beyond any general lexicon entry)?
3. Does this support or refute "lexicon-richness is distinct from foundation-size" (Prediction 2)?

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)

`bash tools/substrate_query.sh "VerbNet FrameNet PropBank subcategorization selectional coverage lexicon
barrier real prose verb tokens"` -- top hit cosine=0.2832 (a T3-deeper-ingest hypernym-recall note, unrelated
mechanism), all 5 hits below the cosine>0.30 rediscovery threshold. Verdict: NOVEL, not a rediscovery of a
landed cell. (Same discipline as hdi_research; not skipped on the assumption Director already checked.)

## Resources (sourcing declaration)

VerbNet (3621 lemmas / 429 classids), PropBank (3319 lemmas / 4659 rolesets), FrameNet (3318 verb-LU lemmas /
13572 total LUs), all via `nltk.corpus` readers. VerbNet + FrameNet were ALREADY present in the local
`nltk_data` cache (no download needed this session); PropBank was fetched ONE TIME this session via
`nltk.download('propbank')` (public, free, Apache/CC-style academic-use license per standard NLTK data
distribution terms -- same class of resource as the FrameNet ingest already landed in this repo,
`tools/substrate_framenet_ingest_v1.py`). **This is a one-time environment-setup action, not a cell runtime
action** -- the cell itself performs NO network access at self-test/smoke/full time; it only reads the local
`nltk_data` cache (same convention as the already-committed `data/corpora/ud_english_ewt/` corpus fetch). If
`nltk_data/corpora/{verbnet,propbank,framenet_v17}` is ever absent on a runner, the cell fails LOUD with a
clear one-time-setup instruction (no silent auto-download at run time).

Real-prose slice: SAME corpus as Rung 5-9 (`data/corpora/ud_english_ewt/en_ewt-ud-test.conllu`, CC BY-SA 4.0,
already committed), reused per Director's pointer -- but this cell's own CoNLL-U parser and lemma/coverage
logic is a **fresh, independent implementation** (does not import from any `exp_read_grow_*` module), per the
explicit "fork-independent, no parser adoption" instruction. This decouples the two measurements: this audit
does not depend on the Rung-9 parser's correctness, and vice versa.

## Method

1. Parse the corpus (independent minimal CoNLL-U reader: form/lemma/UPOS/head/deprel columns only).
2. Extract every UPOS=='VERB' token (AUX tokens -- copulas/modals as a separate UD tag -- excluded by design;
   main predicates only). Use UD's own GOLD lemma column (field 3) -- no re-lemmatization.
3. For each verb token, look up VerbNet-lemma / PropBank-lemma / FrameNet-verb-LU-lemma membership
   (`vn`, `pb`, `fn` booleans). Coverage = fraction of tokens/types with `vn or pb` (PRIMARY, per Prediction
   2's own wording "VerbNet-class + PropBank-roleset"); FrameNet reported as a secondary cross-check
   (`vn or pb or fn`, and `fn` alone).
4. Deterministic sample: from tokens where `vn or pb` (the covered population), draw N=120 via
   `random.Random(7).sample()` over a list PRE-SORTED by `(sent_id, tok_id)` (never `hash()`-seeded, never
   `list(set(...))` -- per META_RULE F.5 / PROT-023), then re-sort the drawn sample by `(sent_id, tok_id)` for
   deterministic output order.
5. HAND-AUDIT (not automated -- this is the explicitly-required manual step): for each of the 120 sampled
   verb tokens, in its full sentence context, judge:
   - `type_level` if the verb's own subcat frame -- including a catalogued sense-variant (e.g. "have"
     TYPE-disambiguated by complement-type into possessive vs modal "have to") or a catalogued idiom/MWE
     entry (e.g. "take place", "get in touch with") -- suffices to correctly resolve the argument structure,
     with NO need for a specific fact about the particular named entities.
   - `instance_level` if correct interpretation genuinely requires a specific world/discourse/pragmatic fact
     about the particular referents (e.g. a metonymic or narrative-specific reading that a fixed lexicon entry
     cannot supply).
   Three `type_level` subclasses are reported for transparency (not gating): `trivial_compositional` (plain
   selectional fit), `frame_disambiguated_sense` (multiple senses/constructions exist but the SUBCAT FRAME's
   complement type alone disambiguates), `idiom_or_mwe_lexicon_entry` (non-compositional but still a
   general, referent-independent lexical entry). **Scoping decision, stated explicitly:** this judgment is
   about VERB-ARGUMENT SELECTIONAL resolution specifically, not pronoun/coreference resolution (which entity
   a pronoun refers to is a separate, already-identified barrier -- discourse/working-memory tracking -- and
   is NOT counted as "instance-level" for this measurement; only the verb's OWN selectional/sense resolution
   is judged). This scoping avoids conflating two distinct barriers.
   Hand-judgments are recorded once, committed as a static data file
   (`data/exp_lexicon_coverage_audit_barrier2_v1/hand_judgments_v1.json`), and the cell CROSS-VALIDATES at
   every run that a live re-derivation of the sample (same seed, same corpus, same coverage sets) produces the
   IDENTICAL `(sent_id, tok_id)` key set as the judgments file -- a staleness/drift guard (`STALE_JUDGMENTS`
   hard-halt on mismatch), not a silent re-sample.
6. Compute fractions + apply pre-registered bands (below); write metrics.

## Bands (pre-registered BEFORE this run, adopting Research's own Prediction-2 thresholds verbatim)

- **HARD-PASS:** `coverage_union_vn_pb_token_frac >= 0.90` AND `type_level_frac_of_audited_sample >= 0.80`.
- **HARD-FAIL:** `coverage_union_vn_pb_token_frac < 0.60` OR `type_level_frac_of_audited_sample < 0.50`.
- **MIDDLE_BAND:** otherwise.
- META_RULE_L floor-hugging check: report `margin_above_hard_pass_floor` for both metrics; if either margin
  is < 5% of its own [floor, 1.0] band width, demote HARD_PASS to MIDDLE_BAND (floor-hugging, not clearly
  above). This is a genuine measurement, not a comparative discriminator with a saturating baseline -- so
  META_RULE_AG (baseline-in-band) is N/A by design (`baseline_in_band: "n/a_no_baseline_arm_single_
  measurement_audit"`).

## Honest limitations (declared up front, not discovered post-hoc)

- Single-rater hand-audit (this cell's author, no second annotator) -- no inter-rater reliability measured.
  Flagged as CLAIM (VET-pending), per standing discipline, not a certified capability result.
- UD-EWT register is informal/transactional web text (blogs, emails, Q&A, reviews, newsgroups) -- likely
  UNDER-represents metaphor/instance-dependent language relative to literary/narrative prose; the honest
  ceiling this measures is for THIS register, not "real prose" universally. Flagged as a caveat carried
  forward, not claimed closed.
- n=120 is a defensible but modest sample for a proportion this close to 1.0 (approx +/-1-2pp binomial SE at
  the observed rate; Wilson interval recommended over Wald given the extreme proportion).
- The `idiom_or_mwe_lexicon_entry` and `frame_disambiguated_sense` type-level subclasses (29/118 of the
  type-level count) rest on the judgment call that non-compositional/multi-sense verb readings are still
  LEXICON-resolvable (a richer VerbNet/FrameNet/PropBank entry) rather than requiring INSTANCE/world-fact --
  this is a substantive interpretive choice, reported with a full subclass breakdown so a reader can
  recompute the headline fraction under a stricter alternative reading if desired.

## Compute architecture

Class: (b) sequential-CPU, justified -- pure CoNLL-U string/dict processing + in-memory `nltk.corpus` lemma-set
lookups over ~2600 verb tokens / 2077 sentences; no torch, no GPU-batchable primitive, no VSA store. Storage
strategy: `no_storage` (pure external-lexicon coverage measurement, no HD substrate object touched).

## Functional requirements (Gate E)

- "Measure symbolic-resource coverage of real-prose verbs" -> addressed by off-the-shelf `nltk.corpus.verbnet
  / propbank / framenet` readers (existing, not a substrate chain-grade primitive; a pure external-lexicon
  lookup).
- "Judge type-vs-instance selectional granularity" -> addressed by a NEW, explicitly-declared hand-audit
  rubric (this cell), not a composition of a prior chain-grade primitive.

## SCHEMA-VET / cell-template declarations

- `arms_differ_exempted: [("n/a", "no_comparative_arms")]` -- single-measurement audit cell, not a
  discriminator across arms; META_RULE_AF is N/A by design.
- `final_metrics_atomicity: "tmp_replace"`.
- `except SystemExit / KeyboardInterrupt: raise` BEFORE `except Exception` (crash -> `CELL_CRASHED` metrics).
- `crlb_n/a`: no quantitative noise floor in the CRLB sense; the closest analog (binomial SE on the audited
  proportion) is reported informally in metrics, not gated.
- `baseline_in_band: "n/a_no_baseline_arm_single_measurement_audit"`.
- `discriminator survives scale: n/a` -- no scale axis; deterministic whole-corpus count (same class as
  Rung 5-9's own audit-type cells).
- `cardinality_ok: "n/a_no_sweep_axis"` (one full-corpus measurement, not a K/N/V sweep).
- `calibration_check: "n/a_bands_are_verbatim_prereg_thresholds_not_tuned"`.
- `cell_chunked: false` (single deterministic run, no seed loop).
- `start_marker_written: true`, `crash_diagnostic_present: true`.
- `heartbeat_present: false` -- wall time measured <10s (whole-corpus parse + nltk lookups), well under the
  60s/15min heartbeat-relevance threshold.
- `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "not_applicable_timeout_below_1800s"` (timeout set to 300s, generous vs. measured <10s
  wall time).
- Gate F (`real_code_path_and_signature_preflight`): `real_code_path_exercised: [parse_conllu (real corpus
  file, self-test slice), nltk.corpus.verbnet/propbank/framenet (real resource lookups, self-test)]`.
  `substrate_signature_checked: "n/a_no_substrate_object_calls_this_is_a_pure_external_lexicon_measurement"`
  (this cell never constructs a KGStore / hdlab substrate object). `guard_baseline_validated: "n/a_no_control_
  beats_baseline_guard"`. `deterministic_seeding: true` (fixed int seed 7, `sorted(...)` never `list(set())`,
  no `hash()`-derived ordering).
- Glass-box / no-LLM: static source-scan (no `torch/spacy/transformers/stanza` imports) + a runtime
  `sys.modules` transitive-closure check after `nltk` use, both asserted at self-test (same pattern as
  Rung 5-9).

## Dispatch

`local_cpu_queue` (measurement only, pause flag re-checked absent immediately before dispatch). Timeout 300s
(measured full wall time <10s; generous margin). No push, no remote persist, no atomization requested by this
cell (a status_log entry records the run; landed-VET/atomize decision is Director's downstream call).
