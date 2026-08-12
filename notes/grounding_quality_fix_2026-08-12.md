# Grounding quality fix -- tautology refusal, filler refusal, provenance (2026-08-12)

Author: exp_dev. Branch `dataprep/mcguffey-graded-corpus`.
Status: PRE-REGISTERED (this section written BEFORE any fix was implemented or run).

Evidence being corrected: `notes/foundation_grounding_sample_2026-08-12.md`
(store `data/foundation/reading_grounding_v1/`, 7966 facts, 3544 GROUNDED_MEANING).
That store is EVIDENCE and is never overwritten or mutated by this work.

## 0. Prior-work check (substrate-KB concept-query)

`bash tools/substrate_query.sh "grounding tautology self-grounded refusal closed class filler
provenance source sentence"` -- see section 6 for the measured result. This is a CORRECTION of a
named defect in a specific landed artifact, not a new arc.

## 1. What is being changed (design + justification)

### 1a. TAUTOLOGY REFUSAL
Today `hdlab/reading_grounding_loop.py::checkpoint()` writes
`(lemma, GROUNDED_MEANING, canon_obj)` unconditionally, where `canon_obj` comes from
`canonicalize()`. `canonicalize()` returns `new_lemma` ITSELF when no anchor in `ConceptSpace`
clears `SENSE_MATCH_THRESH=0.45`. That "self-grounded" return value is the function's explicit
NO-MATCH signal -- it means *the loop failed to find any meaning for this word*. Recording it as
`GROUNDED_MEANING` converts a failure into an asserted fact `(X, GROUNDED_MEANING, X)`, which
asserts nothing. 2328/3544 = 65.7% of the store is this.

DECISION: a no-anchor outcome is refused at the GATE, before banking, and the concept stays
UNGROUNDED. Concretely the refusal is implemented as `consolidation_pass`'s existing
`mdl_gate_fn` hook (an extension point that module already exposes; no edit to
`grounding_acquisition_loop.py`). A False verdict there is treated exactly like a schema-check
failure: the item does NOT bank, `patience` increments, and the item stays PENDING and keeps
accumulating exposures for up to `PATIENCE_MAX=3` further passes before ESCALATING.

WHY THIS AND NOT "write it with a different relation": the requirement is that the concept is not
COUNTED as grounded. Foundation size is measured as distinct subjects with a live
`GROUNDED_MEANING` fact (`grounded_lemmas_in_store`), and the gap gate is
`GapDetector.familiarity(lemma, KNOWN_WORD, CORE)`. Refusing at the gate means BOTH the
`GROUNDED_MEANING` fact AND the `KNOWN_WORD` fact are withheld, so:
  * the concept is not counted as grounded, AND
  * `is_gap(lemma)` stays TRUE -- the gap machinery still sees it as a gap, which is exactly the
    information the gap loop needs and must not lose.
Nothing is silently dropped: every refusal is recorded with its reason, exposure count, best
cosine and pass index in a `refusals` ledger persisted next to the store
(`grounding_refusals.jsonl`), so a refused word is auditable and re-readable, not invisible.

RETRY, NOT PERMANENT DISCARD: because refusal costs patience rather than terminating the item,
a word whose context was too thin at pass N can still ground at pass N+1/N+2 once more exposures
and more anchors exist. After `PATIENCE_MAX` it ESCALATES ("inconclusive so far", per
`foundation_persistence`'s own documented semantics), which is still an ungrounded, gap-visible
state.

### 1b. NO GROUNDING TO FILLER (closed-class exclusion for TARGETS)
CRITERION (stated before measuring, deliberately NOT a blacklist of the audit's specific
offenders): a lemma is CLOSED-CLASS, and therefore ineligible to be the OBJECT of a
`GROUNDED_MEANING` fact, iff EITHER
  (i) its majority UPOS tag in the Universal Dependencies English EWT treebank
      (`data/corpora/ud_english_ewt/en_ewt-ud-train.conllu`, already in-repo, CC BY-SA) is one of
      UD's own FUNCTIONAL (closed) classes: ADP, AUX, CCONJ, DET, NUM, PART, PRON, SCONJ, PUNCT,
      SYM, X -- UD's open/closed split is a published, language-general standard
      (universaldependencies.org/u/pos/); OR
  (ii) it appears in spaCy's English default stop-word list
      (`spacy.lang.en.stop_words.STOP_WORDS`, 326 entries) -- a curated FUNCTION/DISCOURSE-word
      list. It is preferred over sklearn's `ENGLISH_STOP_WORDS` on documented grounds, not on
      outcome grounds: sklearn's own documentation flags that list as having known issues and not
      being a good general-purpose stop list, and it additionally excludes plainly lexical items
      (`thin`, `describe`, `system`).
Membership is tested against BOTH the surface form and its `lemma_verb` normalization, because the
loop stores suffix-stripped lemmas.

The same criterion also disqualifies a closed-class SUBJECT from grounding (a function word has no
lexical meaning to ground), measured and reported separately.

HONEST LIMITATION, STATED IN ADVANCE: this criterion catches `also`, `more`, `most` (spaCy),
`say` (spaCy), and `like` (UD majority tag = ADP). It does NOT catch `people` (UD majority NOUN,
in no stop list) -- `people` is a genuine open-class noun. Adding it would be exactly the
overfitting-to-the-audit the task forbids, so it is left permitted and this is disclosed rather
than patched.

IMPLEMENTATION: `canonicalize()` gains an `eligible` predicate and SKIPS ineligible anchors while
scanning, so a word whose nearest anchor is a function word can still link to its best ELIGIBLE
anchor instead of being dropped -- exclusion narrows the candidate pool, it does not veto the word.

### 1c. PROVENANCE
Today a grounded fact's evidence is structurally unrecoverable: `Trace.context_vec` is a bundled
bag-of-words vector, never text, and `foundation_persistence` persists traces only for PENDING
items. For every `GROUNDED_MEANING` fact written, the fix persists a provenance row keyed by the
store `fid`: subject, object, relation, segment/source tag, corpus tier, exposure count, best
cosine, schema score, and the LIST OF SOURCE SENTENCES (verbatim text, with episode_id and
pass_idx) that produced each accumulated trace. Written to `grounding_provenance.jsonl` in the
foundation directory; PENDING-item evidence is persisted alongside the pending library so
cross-segment (cross-process) grounding keeps its sentences.

BACKWARD COMPATIBILITY: all new files are OPTIONAL on load (`os.path.exists` guards, `.get()`
manifest reads). `load_foundation('data/foundation/reading_grounding_v1')` must keep working
unchanged -- that is an explicit FAIL condition below.

## 2. PRE-REGISTERED BANDS (written before running; expected direction stated)

Re-run scope: the SAME corpus segments as the original run -- `bootstrap`, `ele_cont`, `int_cont`,
`adv_new`, `bio_new` -- at the SAME full sentence counts (4640 / 4623 / 4952 / 7408 / 4500), into
NEW directories `data/foundation/reading_grounding_v2_qualityfix/` and
`data/exp_reading_grounding_loop_cycle3_groundingfix_v1/`. The v1 store is read-only evidence.

| # | Band | BEFORE (v1, measured) | Expected direction | PASS | FAIL |
|---|---|---|---|---|---|
| B1 | tautology rate among newly written GROUNDED_MEANING facts | 0.657 (2328/3544) | -> ~0 | == 0.000 | > 0.000 |
| B2 | share of new groundings whose OBJECT is closed-class (criterion 1b) | to be measured on v1 | -> ~0 | == 0.000 | > 0.000 |
| B3 | fresh random 50-pair audit of NEW facts, bucketed MEANINGFUL / RELATED / NOISE by the SAME rubric | mixed baseline 4% / 6% / 90%; cross-grounded baseline 35% / 25% / 40% | MEANINGFUL up, NOISE down | MEANINGFUL >= 35% AND NOISE <= 40% (matches or beats the cross-only baseline) | MEANINGFUL < 15% OR NOISE > 60% |
| B4 | total concepts reaching grounded status | 3544 | DROP SHARPLY | 300 <= n <= 1400 | n == 0 (over-refusal killed the loop) or n >= 3000 (refusal never bit) |
| B5 | provenance coverage of new GROUNDED_MEANING facts (source sentences recoverable) | 0.000 | -> 1.0 | == 1.000 | < 1.000 |
| B6 | backward compatibility: `load_foundation('data/foundation/reading_grounding_v1')` under the new code | loads | unchanged | loads, same fact count 7966 | raises, or count changes |

B4 IS A CORRECTION, NOT A REGRESSION, AND IS REPORTED AS SUCH. The v1 count of 3544 was inflated
by 2328 tautologies that assert nothing plus an unmeasured number of function-word objects. A
large drop is the EXPECTED CONSEQUENCE of no longer counting non-groundings as groundings. The
honest number will be reported plainly whatever it is; it is not a target to be tuned toward.

MIDDLE_BAND for B3: MEANINGFUL in [15%, 35%) -- better than the 4% mixed baseline (which is the
composition the store actually had) but not matching the 35% cross-only subset.

### 2a. WHAT WOULD MEAN THE FIX FAILED (declared before running)
1. ANY tautology `(X, GROUNDED_MEANING, X)` in the new store (B1 > 0).
2. ANY closed-class object under criterion 1b (B2 > 0).
3. Zero concepts grounded (B4 == 0): the refusal is not a filter, it is a kill switch.
4. B4 >= 3000: refusal did not actually bite; the tautologies were merely relabelled.
5. MEANINGFUL rate < 15% in the fresh 50-pair audit: the facts that survive refusal are no better
   than the pile that was thrown away -- i.e. removing tautologies did not improve the store's
   actual semantic content, only its size. This is the band most likely to fail and the one that
   matters; it is stated in advance so a null here is reported, not explained away.
6. Any new GROUNDED_MEANING fact without recoverable source sentences (B5 < 1.0).
7. The existing v1 store fails to load under the new code (B6).

### 2b. ANTI-TUNING COMMITMENT
`SENSE_MATCH_THRESH` (0.45), `MIN_CONFIRM` (4), `SCHEMA_THRESH_FULL`, `PATIENCE_MAX` (3) and the
closed-class criterion are FROZEN at their pre-registered values above. They will NOT be adjusted
after seeing B3. If B3 lands MIDDLE or FAIL that is the reported result. The B3 bucketing rubric
is the one already used in `notes/foundation_grounding_sample_2026-08-12.md`, restated verbatim
here before any new sample is drawn:
  * MEANINGFUL -- the object states or defines something about what the subject means
    (definitional, taxonomic, part-whole, or a textbook-correct technical collocation).
  * RELATED -- a real topical/associative link, but not defining.
  * NOISE -- no real semantic link, a proper-name/coincidence pairing, a function word, or a
    tautology.
Sampling: `random.seed(42); random.sample(range(len(gm_facts)), 50)` over the new store's
GROUNDED_MEANING facts in fid order -- the same procedure and seed as the prior audit.

---
## 3. IMPLEMENTATION LOG (appended as work proceeds)
</content>

### 3.1 Implementation landed (all self-tests green before any re-run)
- NEW `hdlab/closed_class_lexicon.py` -- 1703 entries. `python -m hdlab.closed_class_lexicon` PASS.
  Self-tests assert the criterion catches `like` via UD-majority-ADP and `also`/`more`/`most`/`say`
  via the spaCy function-word list, keeps every MEANINGFUL object the prior audit found, and
  asserts the DISCLOSED LIMITATION (`people` still eligible) so it cannot silently become a
  hand-patch later.
- `hdlab/reading_grounding_loop.py` -- `canonicalize(eligible=...)` skips ineligible anchors during
  the scan (narrows the pool, does not veto the word); `_make_grounding_gate` wired through
  `consolidation_pass`'s EXISTING `mdl_gate_fn` hook (no edit to `grounding_acquisition_loop.py`);
  provenance + refusal ledgers on `ReadingLoopState`. 8/8 self-tests PASS (3 new).
- `hdlab/foundation_persistence.py` -- FORMAT_VERSION 2, three OPTIONAL sidecars. 7/7 self-tests
  PASS (2 new, one of which deletes the sidecars to exercise the real v1-shape load path).

### 3.2 BEFORE numbers, measured off the v1 evidence store under the NEW code
`data/foundation/reading_grounding_v1` (untouched; opened read-only)
- B6 backward compat: LOADS, 7966 facts, 3544 GROUNDED_MEANING (all live) -- unchanged. PASS.
- B1 tautology rate BEFORE = 0.6569 (2328/3544)
- B2 closed-class OBJECT share BEFORE = 0.0401 (142/3544); among CROSS-grounded only = 0.0979
  (119/1216). Closed-class SUBJECT share BEFORE = 0.0102 (36/3544).
- B4 grounded concepts BEFORE = 3544
- B5 provenance coverage BEFORE = 0.0000 (0 provenance rows persisted)
