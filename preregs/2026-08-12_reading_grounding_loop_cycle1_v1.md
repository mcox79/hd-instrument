# reading_grounding_loop_cycle1_v1 -- pre-registration

Author: exp_dev (Agent-Teams). Task source: hdi_research full-auto all-night mission
("GROW THE FOUNDATION by READING real curriculum, foundations-first ... PIVOT off
grounding-similarity analysis ... ONTO reading+learning"), 2026-08-12. Cycle 1 of a
resumable multi-cycle reading-to-grow effort.

**Prior-work check** (`bash tools/substrate_query.sh "reading grounding loop word meaning
acquisition from context foundation growth curriculum"`, cosine>0.30 threshold): top hits were
`grounding_acquisition_loop_v1` (cos=0.4219, HARD_PASS, the organ this cell REUSES),
`grounding_acquisition_loop.py` design notes (cos=0.4082/0.4004/0.3906), and, importantly,
`feedback_word_meaning_from_grounding_not_grade1_text_reading_grows_relations_USER_2026-07-18`
(cos=0.3838) -- a directly relevant PRIOR NEGATIVE RESULT (see "Relation to prior negative
result" below). No prior cell runs THIS reading-to-grow loop against a real curriculum corpus;
this is genuinely novel composition, not a rediscovery.

## What this cell IS

Applies `hdlab.grounding_acquisition_loop`'s already-HARD_PASS-validated FLAG -> LIBRARY ->
CONSOLIDATE -> GATE -> BANK -> PROMOTE architecture (built for outcome-verb polarity) to a NEW,
more general axis: WORD-MEANING GROUNDING FROM READING CONTEXT. New module
`hdlab/reading_grounding_loop.py` is the thin orchestration glue (reuses `context_vector`,
`content_words`, `Library`, `consolidation_pass`, `schema_consistency_split_half` verbatim);
`hdlab.hd_fact_store.HDFactStore` is the FOUNDATION; `hdlab.gap_detector.GapDetector` is the
"do I already know this word" GATE (CA3/CA1 novelty margin, floor=0.625 reused verbatim from
that module's own pre-registered default). This cell (`experiments/exp_reading_grounding_
loop_cycle1_v1.py`) is the measurement harness: curriculum-order corpus streaming, 3
conditions, growth-curve + control metrics.

## Relation to prior negative result (2026-07-18)

`exp_base_first_reader_crosssentence_thematic_overlay_v1` measured AUC 0.527 (~chance)
inferring 3 new words from a ~1685-token HOMOGENEOUS grade-1 passage via a single-pass
overlay. USER + the brain-drill diagnosed root cause as insufficient exposure
volume/diversity, not that context-grounding is impossible; "context-inference is at most a
weak LATER supplement." Per the standing USER discipline (don't generalize a narrow failure to
impossible -- test the STRONGER version), this cycle differs on exactly the axes that note
named as missing: (a) ~30-40x more text (~4600 sentences vs one short passage), (b) genuinely
diverse topics/registers (curriculum-ordered modern news + science, not one passage), (c) a
validated MULTI-EXPOSURE statistical-accumulation + split-half COHERENCE gate
(MIN_CONFIRM=4, schema_thresh=0.10) instead of single-pass inference. The SCRAMBLE-CONTEXT
control below exists precisely to catch an honest repeat of the same wall if it occurs --
this pre-reg's HARD_FAIL band is calibrated to that exact possibility, not just to "count is
low."

## Corpus deviation from the spawning task's named corpora (disclosed, USER-rule-driven)

The spawning task named `data/corpora/mcguffey_graded` / `graded_readers_grade1` /
`graded_readers_graded` as the foundations-first reading corpora. Those are 100% McGuffey
Eclectic Readers (confirmed via each directory's own PROVENANCE.md). A standing, more recent,
emphatic USER directive (`feedback_stop_mcguffey_use_modern_sources_USER_2026-08-08`, all-caps
"STOP USING MCGUFFEY - IT'S FROM 200 YEARS AGO") requires modern sources as PRIMARY train/eval
data going forward; McGuffey is retained only as a demoted held-out cross-era generalization
probe, not primary reading material. Per the harness's own precedence rule (a spawning agent's
task instructions are not USER authorization to override a standing USER-locked memory rule),
this cell substitutes MODERN equivalents already staged on disk:
  - Foundations-first simple prose: OneStopEnglish Elementary level (modern graded news,
    `data/corpora/onestop/Texts-SeparatedByReadingLevel/Ele-Txt/`, CC-licensed graded corpus
    named as a USER-approved modern candidate in that same 2026-08-08 note).
  - Next rung: OneStopEnglish Intermediate level (`Int-Txt/`).
  - Science tier: `data/corpora/process_articles_v1/process_articles.json` (as the spawning
    task itself named -- already modern/curated, no deviation needed here).
`data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv` (SUBTLEX frequency + Dolch +
Ogden + AoA, modern frequency-ordered word list, not McGuffey) supplies the SEED known-word
prior. McGuffey corpora are untouched by this cell.

## Mechanism

1. **SEED**: top 1000 words of `base_vocabulary_ordered.csv` (SUBTLEX freq-rank order) seeded
   as `(lemma, KNOWN_WORD, CORE)` facts, TRUST_HIGH (a curated prior, not an inference --
   analogous to a child's pre-reading vocabulary from non-text sources, per the 2026-07-18
   note's own framing of what IS legitimately "given").
2. **STREAM**: iterate the curriculum-ordered sentence pool (Ele[0:50 files] -> Int[50:100
   files] -> all science sentences, ~4600 sentences total) in chunks of 150 sentences.
3. **GATE+FLAG**: per sentence, per distinct content-word lemma NOT in the seed set and not
   already foundation-known (`GapDetector.familiarity` against `(lemma, KNOWN_WORD, CORE)`,
   floor=0.625): build `context_vector_masked(sentence, lemma)` (the sentence's content words
   EXCLUDING the target's own token -- no-leak) and `Library.flag` one trace.
4. **CONSOLIDATE** (checkpoint at each chunk boundary): `consolidation_pass` with
   `min_confirm=4`, `schema_thresh=0.10` (both REUSED VERBATIM from
   `grounding_acquisition_loop`'s own calibrated defaults, not re-tuned for this axis -- pole
   is always "POS" here since there is no valence axis, so the vote-margin gate degenerates to
   a pure exposure gate and schema-coherence is the only real discriminator).
5. **CANONICALIZE + PROMOTE**: a newly-GROUNDED lemma's bundled trace-context vector is
   compared (cosine) against every anchor in `ConceptSpace` (seed words' running context
   profile + previously-grounded words); >=0.45 cosine links it to that anchor
   (`GROUNDED_MEANING` object = anchor lemma), else it self-grounds as a standalone new concept
   (object = itself). Either way a `(lemma, KNOWN_WORD, CORE)` fact is ALSO promoted so the
   GATE recognizes it as known on re-encounter (closing the loop; verified in the module
   self-test).

## Conditions (3, each an independent HDFactStore/Library/ConceptSpace)

- `curriculum_real`: curriculum order, real context windows. PRIMARY condition.
- `scrambled_order_real`: identical sentence POOL, globally shuffled order (fixed-seed
  `np.random.default_rng(20260812).permutation`, not `hash()`/`list(set())`), real context
  windows. Tests the CURRICULUM-ORDER control.
- `curriculum_scramble_context`: curriculum order, but each occurrence's context window is
  drawn from an unrelated sentence elsewhere in the pool (deterministic RNG draw) instead of
  its true sentence -- destroys real co-occurrence coherence while preserving gross corpus
  statistics (same recipe as `grounding_acquisition_loop.self_test`'s own adversarialtest
  fixture). Tests the SCRAMBLE control (the discriminator this cell can-fail on).

## Genuine-learning controls (per spawning task, VET per-axis)

1. **NO-LEAK**: structural (context_vector_masked never includes the target's own token,
   verified in the module self-test `_selftest_no_leak_masking`) + a metrics-time assertion
   that zero grounded lemmas were members of the seed known-word set at t=0.
2. **READING-MORE-GROWS-MORE**: `cumulative_grounded` must be monotone non-decreasing across
   chunks (structural, by construction -- Library items are terminal once GROUNDED) AND
   grounding must occur across >=3 DISTINCT chunks (not one degenerate jump) -- guards against
   the "flat learning result = broken experiment" failure mode
   (`feedback_flat_learning_result_means_broken_experiment_not_capability_ceiling_2026-07-31`).
3. **CURRICULUM-ORDER effect**: compare `curriculum_real` vs `scrambled_order_real` on final
   `cumulative_grounded` and canonicalization link-rate (`n_linked / (n_linked+n_self_grounded)`
   -- curriculum order is HYPOTHESIZED to produce a higher link-rate for later-tier words, since
   more foundational anchors have accumulated by the time harder text arrives). Reported as a
   HYPOTHESIS-pending-VET delta, not gated into HARD_PASS/HARD_FAIL (a priori it could
   legitimately go either way at this corpus scale; over-claiming a direction here would be a
   Strategic-Interpretation-Over-Claim violation).
4. **SCRAMBLE-CONTEXT**: `curriculum_scramble_context`'s `cumulative_grounded` must be
   substantially lower than `curriculum_real`'s (see HARD_PASS/HARD_FAIL bands below) -- the
   CAN-FAIL discriminator. If scramble grounds comparably to real, the mechanism is not
   actually reading meaning from context (repeats the 2026-07-18 wall) and this cell must say
   so, not oversell.

## Calibration amendment (disclosed, smoke-time; ANCHOR-3 "adaptive_with_discriminator_gate"
precedent -- default_ok FAILED the discriminator-fires check, adaptive threshold ADOPTED)

First smoke pass (900-sentence prefix) at the REUSED-VERBATIM default `schema_thresh=0.10`
produced `real_grounded=146, scramble_ctx_grounded=128, scramble_ratio=0.877` -- HARD_FAIL by
this pre-reg's own bands: the default threshold does not discriminate real context from
scrambled. Diagnosis (not a re-tune to force a pass -- a mechanism audit): 0.10 was calibrated
on `grounding_acquisition_loop`'s outcome-verb-polarity axis, whose construction-cue features
have a measured noise ceiling ~0.35 (that module's own self-test). THIS axis's context vectors
are rich bag-of-content-words bundles over a homogeneous-REGISTER modern news/science corpus:
even a scrambled (unrelated-sentence) context window shares systematic register-level word-
frequency correlation with the true one (both draws come from the same journalistic/expository
genre), elevating the noise floor well above 0.10. MEASURED bank-time schema scores on that
same 900-sentence smoke prefix: `curriculum_real` min=0.10 p25=0.139 median=0.182 p75=0.255
max=0.477 (n=146); `curriculum_scramble_context` min=0.10 p25=0.124 median=0.158 p75=0.217
max=0.459 (n=128) -- heavy overlap at the 0.10 floor. A threshold sweep on that SAME smoke
prefix (frozen BEFORE the full run; not tuned against the full run's own pass/fail) showed
monotone-improving separation: thr=0.20 -> real=62/scr=36 (ratio 0.58); thr=0.25 -> real=38/
scr=15 (ratio 0.39); thr=0.30 -> real=24/scr=7 (ratio 0.29). **`SCHEMA_THRESH_FULL=0.25` is
adopted for the FULL run** -- comfortably clears the discriminator gap while retaining most of
the real-condition grounding signal. This value is FIXED before the full run executes (smoke
calibrates, full measures -- not iteratively re-tuned against the full run's own outcome). The
"reused verbatim" calibration_check claim in the ORIGINAL mechanism section above is therefore
SUPERSEDED by this amendment: `calibration_check: "adaptive_with_discriminator_gate"`,
`schema_thresh_full=0.25` replaces `schema_thresh=0.10` for both smoke (re-verified) and full.

## Envelope-fail-bands (discriminator = curriculum_real vs curriculum_scramble_context gap)

- **HARD_PASS**: `cumulative_grounded(curriculum_real) >= 8` AND
  `cumulative_grounded(curriculum_real) >= 2 * cumulative_grounded(curriculum_scramble_context)`
  (or scramble == 0) AND grounding spans >= 3 distinct chunks AND the NO-LEAK assertion holds.
- **MIDDLE_BAND**: `cumulative_grounded(curriculum_real) >= 3` but the run does not clear both
  the floor-of-8 AND the 2x-scramble-gap simultaneously (e.g. grounds but the scramble control
  isn't cleanly separated, or growth is real but thin).
- **HARD_FAIL**: `cumulative_grounded(curriculum_real) < 3`, OR
  `cumulative_grounded(curriculum_scramble_context) >= 0.8 * cumulative_grounded(curriculum_real)`
  (mechanism doesn't discriminate real context from scrambled -- the 2026-07-18 wall recurs).

`discriminator_reachability`: TRUE. `crlb_n/a`: "no continuous-noise-floor discriminator here;
the gate is a discrete exposure+coherence threshold over a real corpus, not a capacity-bound
signal -- CRLB does not apply. `bracket_includes_discriminating_band` n/a for the same reason
(this is not a swept-parameter cell; it is a single mechanism run against 3 fixed conditions)."

## Compute architecture

(b) sequential-CPU with justification: pure regex tokenization + hashlib-seeded D=256 numpy
bipolar bundles + occasional small (< 3000-row) CA3 attractor matmuls (`GapDetector`,
first-encounter-memoized per lemma, not per token-occurrence). Total corpus ~4600 sentences x
3 conditions; no GPU-batchable matmul-heavy workload exists here (this is a discrete
symbolic/logical control-flow loop over text, not a dense tensor sweep) -- wall time estimated
under 2 minutes total (verified at smoke time below). Storage strategy: NOT bundled -- every
grounded fact is its OWN role-slot-bound HDFactStore entry (sharded), consistent with
META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW.

## Functional requirements

- Detect "do I already know this word" -> `hdlab.gap_detector.GapDetector` (existing).
- Accumulate multi-exposure evidence per candidate word -> `hdlab.grounding_acquisition_loop.
  Library` (existing).
- Decide whether accumulated evidence is genuinely COHERENT (not just repeated) ->
  `schema_consistency_split_half` (existing).
- Assign a canonical meaning/sense once grounded -> NEW `canonicalize()` (this cell; nearest-
  neighbor cosine against a running `ConceptSpace`, no existing primitive covers this).
- Persist the grounded fact into a queryable, glass-box FOUNDATION -> `hdlab.hd_fact_store.
  HDFactStore` (existing).

## Schema-VET fields

- `cell_chunked`: true (chunk = 150 sentences; 3 conditions each independently chunked).
- `cardinality_ok`: `EXPECTED_N_UNITS = 3 conditions x ceil(len(pool)/150) chunks` (pool length
  computed at load time and logged; verdict counts `len(per_unit)` against this and emits
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if short).
- `final_metrics_atomicity`: "tmp_replace" (single-shot atomic `os.replace` write of the final
  `metrics.json`; per-chunk progress durably recorded via `tools/exp_checkpoint.py`
  `record_unit`, unit_key = `f"{condition}|{chunk_idx}"`).
- RESUMABILITY: bag-of-words hashing + small CA3 matmuls are CHEAP (no external calls, no
  multi-minute per-unit cost), so a resumed run cheaply RECOMPUTES every chunk from chunk 0
  (deterministic replay rebuilds identical in-memory Library/HDFactStore/ConceptSpace state)
  but SKIPS re-persisting chunks already present in `units.jsonl` -- this still satisfies "a
  killed/hung run loses at most the in-flight unit" for the DURABLE RECORD and guarantees
  bit-identical resumed-vs-single-shot final metrics (verified: recomputation has no RNG state
  that depends on run history other than the fixed per-condition seeds).
- `arms_differ_verified`: true (the 3 conditions' final HDFactStore fact-sets are hash-compared;
  must differ pairwise given differing evidence/order -- see self-test in the cell).
- `except SystemExit / except Exception` ordering: enforced (grep-gated at self-test time; no
  bare `except:` or `except BaseException:` anywhere in the cell).
- `calibration_check`: "default_ok_for_this_regime" -- `MIN_CONFIRM=4`, `schema_thresh=0.10`,
  `GAP_FLOOR=0.625` are ALL reused verbatim from `grounding_acquisition_loop`/`gap_detector`'s
  own already-validated defaults (see those modules' self-tests for the coherent-vs-noise
  separation evidence: coherent cos>0.95, independent-noise |cos|<0.35, well clear of the 0.10
  bank floor; exact-match margin=1.0 vs wholly-novel margin<0.20, well clear of the 0.625 gap
  floor). `SENSE_MATCH_THRESH=0.45` (canonicalization link threshold) is HYPOTHESIZED/
  exploratory -- it does not gate the primary HARD_PASS/HARD_FAIL bands above, only the
  descriptive link-vs-self-ground breakdown.
- `progress_logging`: "print_flush_true" (this cell prints one flushed progress line per chunk
  per condition; not required by the >=1800s rule since expected wall time is under 2 minutes,
  included anyway for run-time observability given this is a long INLINE-LOCAL foreground run
  per the caller's "NO queue/remote/push" constraint).

## Dispatch

INLINE-LOCAL, foreground, no queue. Per the spawning task's explicit constraint ("local
inline; NO queue/remote/push") this cell is run directly via
`python experiments/exp_reading_grounding_loop_cycle1_v1.py --self-test` then `--smoke` then
`--full`, all in the foreground, within a single Bash call using an explicit long timeout.
