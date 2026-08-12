# Definitional TERM-BOUNDARY repair (v5) -- measurement + fix, 2026-08-12

Author: exp_dev. Pre-reg: `preregs/2026-08-12_definitional_term_boundary_v5.md` (committed
BEFORE the run, 486552a54). Cell: `experiments/exp_definitional_grounding_v5.py` (79a230f40).
Module fix: `hdlab/definitional_extraction.py` (e01db310b).
**WIRE STATUS: VET_PENDING.** Nothing here is promoted without the director's hand-score.

Prior-work check (mandated substrate-KB concept-query, "definitional extraction term boundary
glossary genus hypernym"): top hits at cosine >0.30 are `dictionary_definition` (0.3389),
`dictionary definition` (0.3389), `extraction` (0.3174), `hdlab/definitional_extraction.py`
(0.3164, sourced from this arc's own v3 note), `glossary` (0.3066). The only arc hit is this
module's own predecessor -- a CONTINUATION, not a rediscovery. No prior cell attacked term
boundaries.

---

## 1. The director's diagnosis, verified independently

I did not inherit it. I read the code, read the raw corpus, and measured.

**CONFIRMED, and the 50-row sample UNDER-stated it.** The director saw 8/22 NOISE rows as
glossary-boundary corruption. Corpus-wide, **four of every five glossary facts carried a term
that is not a real term of the source textbook.**

### Operational definition of CORRUPTED (as instructed, stated explicitly)

A fact's stored `subject` is CORRUPTED iff EITHER test fires:

- **T1 BOUNDARY-CROSSING TERM.** The subject is multiword; locate its tokens as an in-order
  MINIMAL window in its source sentence (closed-class tokens that `build_term` drops may be
  skipped); CORRUPT iff the raw text of that window contains a character that cannot occur
  inside one term (`. , ; : ( ) [ ] " ! ?`) or an interior token that cannot occur inside one
  term (`and or but nor` / finite verb / complementizer / preposition).
- **T2 GLOSSARY-KEY MISMATCH.** `pattern == GLOSSARY_COLON` and `segment == bio_new` and the
  normalized subject is NOT one of the **926 ground-truth glossary keys** recovered from the
  LINE STRUCTURE of `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt`.
  This is GROUND TRUTH, not a heuristic -- the true keys are on disk (line 8715 is literally
  `equilibrium: the steady state of a system ...`); only the loader destroyed them.

Implemented as `audit_corruption()` / `term_crosses_boundary()` / `true_glossary_keys()` in the
v5 cell; calibrated in `_selftest_corruption_detector()` (must fire on the three director-named
merges, must NOT fire on the F1 gains).

### Measured over ALL 1956 v4 facts

| quantity | value |
|---|---|
| T1 boundary-crossing terms | 22 |
| T2 glossary-key mismatches | **292 of 363 glossary facts = 80.4%** |
| **CORRUPT (T1 or T2)** | **314 / 1956 = 16.1%** |

**LOWER BOUND.** T2 cannot fire when a corrupted term coincides with some *other* valid
glossary key -- confirmed instance `population -> allele`, harvested from an entry whose true
term is `migration`. T1 cannot fire on a same-clause merge with no punctuation.
Director's sample rate 11/50 = 22%; corpus-wide lower bound 16.1% is consistent at se ~5.8pp.

---

## 2. Root cause -- three bugs, two of them mine

1. **`_GLOSSARY_ENTRY` absorbed LEFTWARD.** The split regex allowed the entry term to be up to
   FOUR words, and regex alternation takes the LEFTMOST viable start, so the term ate up to
   three words of the PREVIOUS entry's definiens:
   `"...interactions with their abiotic environment equilibrium: the steady state..."`
   -> term `abiotic environment equilibrium` (true term: `equilibrium`).
2. **`_expand_proper_name` walked the TOKEN list, which drops punctuation**, so a name merged
   across a comma or period: `"Like DNA, RNA is a polymer"` -> `DNA RNA`.
3. **NOT A PARSER BUG AT ALL:** `exp_reading_grounding_loop_cycle2_v1.load_biology_sentences`
   does `" ".join(kept)`, destroying the one-entry-per-line structure the cleaned OpenStax file
   actually has. Joined: 11332 sentences, 50 of them >1000 chars, max 4776. Per line: 12559
   sentences, **0** >1000 chars, max 591. The parser never had a chance.

---

## 3. The fixes

| id | where | fix |
|---|---|---|
| **F7** | `hdlab/definitional_extraction.py` | proper-name expansion requires a spaces-only gap between adjacent tokens, in BOTH directions (`_gap_is_clean`). |
| **F8** | `hdlab/definitional_extraction.py` | the glossary split point is the LAST token before the colon. Inside a run-on block the true left edge is UNRECOVERABLE, so the term is deliberately UNDER-SPECIFIC (`web` for `detrital food web`) rather than a DIFFERENT CONCEPT. Under-specific beats corrupt. |
| **F9** | v5 cell only (`load_biology_sentences_lineaware`) | sentence-split PER LINE. This RECOVERS the true multiword terms: a line-aware entry is its own sentence, so `_RE_COLON` (anchored at `^`) reads the full correct term. Touches no file owned by another agent; verified byte-equivalent splitting recipe. |

F9 is a SECOND VARIABLE and was declared as such before the run, which is why the cell reports
both arms.

---

## 4. Results (MEASURED@`data/exp_definitional_grounding_v5/metrics.json`)

`verdict: STRUCTURAL_PASS_PENDING_B3` -- **all machine checks pass.** elapsed 17.5s, run_mode full.

### Corruption

| arm | facts | T1 | T2 (of glossary) | corruption |
|---|---|---|---|---|
| v4 BEFORE | 1956 | 22 | 292/363 (80.4%) | **16.1%** |
| v5 PARSER_ONLY (F7+F8, v4 loader) | 2105 | 8 | 157/514 (30.5%) | **7.8%** |
| v5 CANONICAL (F7+F8+F9) | 2092 | 8 | 12/506 (2.4%) | **1.0%** |

Attribution is clean: the parser fix alone halves corruption (16.1 -> 7.8) but cannot recover
the true multiword terms; the loader fix takes it the rest of the way (7.8 -> 1.0). Pre-reg
vacuity guard (<= 4%) is SATISFIED, so the discriminator fired and the hand-score is readable.

### Composition

2092 facts (v4 1956, +136). 1601 pairs kept from v4, 491 new, 355 dropped -- i.e. 17% of the
set changed, far less churn than v4's 44%. PROPER 329 / COMMON 1763; 615 multiword subjects.
GLOSSARY_COLON rises 373 -> 519 (the line-aware loader exposes entries the run-on had swallowed).

### F1 regression status -- ALL EIGHT HOLD

`Chon -> counsellor`, `Naeem -> campaigner`, `Olkin -> scientist`, `Rajagopalan -> student`,
`Shanhui Fan -> expert`, `Currie Technologies -> seller`, `Piraeus -> port`, `Drosophila -> fly`
all survive; `fan -> expert` and `technology -> seller` stay absent. Each is ALSO a named
regression test in `hdlab.definitional_extraction._self_test`, so the fix cannot be undone
silently. All 4 v4 control rows survive; all 19 fault rows are gone.

### Multi-sense yield -- BOTH indexes, both UP

(`n_multi_sense_words` / `senses_with_gt1_source_sentence` / `words_with_ALL_senses_gt1`)

| index | v4 | v5 |
|---|---|---|
| `subject` (full TERM) | 197 / 51 / 2 | **288 / 96 / 3** |
| `subject_head_lemma` | 333 / 88 / 2 | **379 / 145 / 4** |

Pre-reg said the sign was unknown; it is UP on both. Note the v4 head-lemma triple I recompute
here is 333/88/2, not the 333/135/7 quoted in the hand-score note -- the `n_multi_sense_words`
agrees but the sentence counts differ, because I count `source_sentences` per stored ROW
(keyed `(term, object)`) rather than re-merging sentences across rows sharing a head lemma.
v4 and v5 are computed identically here, so the delta is apples-to-apples.

---

## 5. Out-of-scope fault classes -- REPORTED, NOT REPAIRED

**INVERTED HYPERNYMY: my fix does NOT touch it, plainly stated.** It is not a parse bug. It is
not knowing which side of a definitional sentence carries the genus, and no surface cue in the
sentence supplies that. WordNet-based auto-count (object's hypernym path passes THROUGH the
subject while the reverse does not): **v4 24 (1.2%) -> v5 25 (1.2%) -- unchanged, as predicted.**
Examples in v5: `cell -> axon`, `allele -> dominant`, `aqueous solution -> solvent`,
`age structure -> proportion`. All three director-cited instances (`bacteria -> fixation`,
`cell -> lymphocyte`, `pellucida -> event`) are still PRESENT.

**ADJECTIVAL / LIST HEADS: also untouched, and my automatic probe is NOT a valid measurement
of it.** The probe (object has no WordNet noun sense) returns **0 in both v4 and v5** -- because
`definiens_head` already gates on `is_nominal_lemma`, so the surviving instances are words that
DO have a noun sense but are functioning adjectivally or as the first item of a coordinate list.
`Margaret Thatcher -> best`, `dominant phase -> short`, `quadrat -> wood` are all still PRESENT
in v5. Treat the 0 as "detector blind", not as "class eliminated".

**ROLE-NOT-MEANING:** `predecessor -> warner` and `Lodge -> scene` both still PRESENT.

Judgement on scope: all three are DEFINIENS-side or semantic faults. Repairing them in the same
pass would have confounded attribution of the term-boundary result, which is the one question
this pass was asked. `quadrat -> wood` in particular looks cheaply fixable (take the head after
the coordinator in "a wood, plastic, or metal square"), and is the obvious next parser candidate
IF the hand-score says parser work is still worth doing at all -- see s.6.

---

## 6. Standing read if the hand-score lands flat

Deliberately written BEFORE the score exists, so it cannot be retrofitted.

38% -> 40% -> ? . If v5 also lands at or below 42%, the pre-registered falsifier fires: the
corruption was an obvious-looking but NON-BINDING fault. In that case my read is that
**surface-pattern definitional extraction has reached its ceiling near 40%**, and the reason is
structural, not a residue of bugs:

- The three fault classes that survive are all cases where the SURFACE IS AMBIGUOUS and the
  correct answer requires knowing what the words mean. Inverted hypernymy is the clearest: "a
  lymphocyte is a type of white blood cell" and a sentence pairing `cell` with `lymphocyte` are
  surface-indistinguishable without already knowing which is the broader category. A regex
  cannot acquire that; only an existing taxonomy or an existing grounded concept can supply it.
- Every fix so far has been of the form "this surface cue was read wrongly". Those are now
  largely exhausted: corruption is at 1.0%, adjectival heads are gated, negation/partitive/
  list/enumeration are gated. The remaining errors are not misreadings of the surface -- they
  are correct readings of a surface that does not determine the answer.
- That is a route-classification result, not a dead end: per the error-routing rule this is a
  **missing-COMPONENT** fault (the extractor has no notion of which term is superordinate),
  not a used-ability-wrong fault. The brain-faithful next move is to give the definitional
  path a genus/species decision that reads from the FOUNDATION being built (is one of these
  two already grounded as a broader category?), i.e. couple definitional extraction to the
  grounded frontier rather than continuing to sharpen the regex. That also lines up with the
  gap==grounding framing.

If instead v5 lands >= 47%, the term boundary WAS binding, and the same reasoning says the next
parser fix worth doing is the coordinate-list head (`quadrat -> wood`), which is small and
localized.

---

## Artifacts

- facts: `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` (2092)
- metrics: `data/exp_definitional_grounding_v5/metrics.json`
- **UNSCORED sample for the director:**
  `data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json`
  (n=50, seed 42, sampling bit-identical to v2/v3/v4 and asserted in the cell self-test,
  identical field schema, `scored: false`)
