# Director hand-score: v6.1 predicate recovery sample (2026-08-13)

**Scorer:** Director, single judge, scored BLIND (the sample ships `scored: false`, `note:
"UNSCORED AND UNBANKED ... the v6 hand-score (35/7/8) is NOT carried over"`, no pre-assigned
buckets). Sample: `data/exp_definitional_predicate_v61/predicate_audit_sample.json` (n=50,
seed 42, arm `DEF_V61_PREDICATE`, arm n=228). Relations in arm: ENABLING_CONDITION 70,
ENABLING_CONDITION_AGENT 52, PROCESS_ACTION 49, PROCESS_PATIENT 42,
ENABLING_CONDITION_PATIENT 15.

## SCOPE -- READ BEFORE THE NUMBER

New relation types (PROCESS_ACTION / PROCESS_PATIENT / ENABLING_CONDITION /
ENABLING_CONDITION_AGENT / ENABLING_CONDITION_PATIENT) over textbook corpora. This is
**NOT comparable to the v5 64% figure** (`director_handscore_b3_v5_termboundary_2026-08-12.md`,
GROUNDED_MEANING genus facts) and **NOT comparable to the read-out hand-scores**. Cross-scoring
against v5's 64% is already flagged as an error in `notes/STATUS.md` DO-NOT-REDO.

It licenses only: **"predicate/condition recovery yields a correct fact ~80% of the time on this
corpus, single judge."**
It licenses **NO** claim about the substrate LEARNING anything -- this is a hand-written parser
SUPPLYING facts. Facts remain **UNBANKED** in `data/exp_definitional_predicate_v61/`; growth is
PAUSED and `data/foundation/**` is untouched.

## RESULT

| bucket | n | share |
|---|---|---|
| MEANINGFUL | 40/50 | **80%** |
| RELATED | 2/50 | 4% |
| NOISE | 8/50 | 16% |

- **MEANINGFUL (40):** 01,02,03,04,05,06,07,09,10,11,12,13,14,15,17,18,21,22,23,24,25,28,29,30,
  31,35,36,37,38,39,40,41,42,43,44,45,47,48,49,50
- **RELATED (2):** 26,33
- **NOISE (8):** 08,16,19,20,27,32,34,46

## COMPARISON TO v6 -- NOT A PAIRED DELTA

v6 scored 35/7/8 = 70/14/16 on **its own** n=50 sample; v6.1 scores 40/2/8 = 80/4/16 on **its
own** n=50 sample. **These are DIFFERENT samples drawn from different fact populations (v6 arm
n=250, v6.1 arm n=228), not a paired re-score of identical rows.** Same scorer, same rubric,
same seed convention (42), same corpus. Report as "quality of v6 output vs quality of v6.1
output", never as a per-row delta.

Honest summary: MEANINGFUL rose 70 -> 80 with RELATED collapsing 14 -> 4 -- partials converted
into genuine hits. **NOISE was UNCHANGED at 16%.** The fixes converted borderline rows; they did
**not** reduce the error floor.

Machine-side, all 13 tracked defect rows are resolved:
`defect_recheck.json` reports `n_still_reproducing_the_v6_fact = 0`. 178 refusals over 175
sentences (`refusals.jsonl`): NO_VERB_IN_OWN_CLAUSE 86, term-boundary 79
(TERM_ANAPHORIC_SUBJECT 44, TERM_NOT_NOMINAL 29, D1_BARE_CATEGORY_HEAD 4, TERM_EMPTY_CUT 2),
argument-selection 8 (D3_PATIENT_OBLIQUE 3, D3_PATIENT_PURPOSE_ONLY 3, D3_PATIENT_NO_NOMINAL 2),
negation 4 (D2_NEGATION_IN_SCOPE), non-definition 1 (D4_NON_DEFINITIONAL_CONTEXT).

Term-boundary logic is **CENTRALIZED**, not duplicated per pattern: `build_term_explain()`
(`hdlab/definitional_extraction.py:533`) called via `_term()`
(`hdlab/definitional_predicate_v61.py:261`) from all three VP patterns.

## WHAT WORKED

v6.1-sample row indices:

- **[28]** `lactation --PROCESS_ACTION--> synthesize` -- v6 banked `nipple` from a trailing
  adjunct.

v6-sheet row indices (from `defect_recheck.json`, the exact source sentences the v6 hand-score
flagged):

- **[44]/[45]** `termination of signal` vs `termination of translation` are now **distinct
  terms**; v6 collapsed both to the string `termination`, making them indistinguishable in the
  store.
- **[41]** `second-degree` recovered to `incomplete block`
  (`(incomplete block, ENABLING_CONDITION, reach)`).
- **[07]** the bystander-effect **inverted** fact is now REFUSED (`D2_NEGATION_IN_SCOPE`) instead
  of banked as `(bystander effect, PROCESS_ACTION, volunteer)`.
- **[13][16]** bad patients REFUSED rather than guessed (`D3_PATIENT_NO_NOMINAL`,
  `D3_PATIENT_OBLIQUE`); each still emits its correct action fact (`become`, `travel`).

## TWO NEW NAMED DEFECT CLASSES (ranked -- next build target)

### 1. SLOT TYPE NOT ENFORCED -- HIGHEST LEVER

An ACTION slot may hold a non-verb and a PATIENT/AGENT slot a non-noun. Nothing checks.

- **[08]** `cellular respiration --PROCESS_PATIENT--> convert` -- a **verb in a noun slot**
  ("...the chemical energy stored in sugars **is converted** into ATP").
- **[32]** `osmotic regulation --PROCESS_ACTION--> salt` -- a **noun in a verb slot**; should be
  "keep" ("...the mineral salts and water **are kept** in balance").
- **[34]** `photosynthesis --PROCESS_ACTION--> like` -- a **PREPOSITION**, taken from
  "organisms **like** plants".

A per-slot type check kills all three outright.

### 2. TERM EXTRACTOR NOW OVER-TAKES

The v5/v6.1 boundary work fixed under-taking and overshot in the other direction:

- **[20]** `pathway's` -- a bare **possessive fragment** ("the **pathway's** end product").
- **[27]** `interesting example of ecosystem dynamics` -- a **discourse phrase**, not a concept
  ("In 1993, an interesting example of ecosystem dynamics occurred when...").
- **[46]** `tragic irish potato famine` -- **evaluative adjective** baked into the term.

### 3. MINOR: WRONG VERB CHOSEN INSIDE THE CLAUSE

- **[19]** `feedback inhibition --ENABLING_CONDITION--> end` -- took "end" from the **noun**
  "end product" instead of the predicate "**inhibits**".
- **[46]** took "grow" from a **reduced relative** ("the single variety **grown** in Ireland")
  instead of the main verb "became".

### 4. MINOR: PATIENT DRAWN FROM THE WRONG CLAUSE

- **[16]** `elaborative rehearsal --PROCESS_PATIENT--> try` -- from "new information **you are
  trying to learn**", not the main clause.

**Six of the eight noise rows ([08],[20],[27],[32],[34],[46]) fall to defect classes 1 and 2.**

## LIMITS

Single judge. Borderline calls:

- **[26]** `injury --ENABLING_CONDITION_PATIENT--> knee` -- term **truncated** from the
  definiendum surface "Injury to the posterior cruciate ligament".
- **[33]** `osmotic regulation --PROCESS_PATIENT--> balance` -- **oblique** ("kept **in
  balance**"), but topically central.
- **[11]** `head` (from "the myosin **head** attaches to the actin") and **[17]** `response`
  (from "the immune **response** first develops...") are truncated but judged **correct in
  context**.
