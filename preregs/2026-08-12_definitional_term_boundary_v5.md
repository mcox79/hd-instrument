# PRE-REG -- definitional TERM-BOUNDARY repair (v5), 2026-08-12

Registered BEFORE the v5 build is run and BEFORE any v5 fact or sample row is looked at.
Author: exp_dev. WIRE STATUS: **VET_PENDING** -- nothing here is promoted without the
director's hand-score.

Predecessors:
- v3 DEF, 1751 facts, director hand-score 38 / 18 / 44
  (`notes/director_handscore_b3_def_vs_control_2026-08-12.md`)
- v4 DEF parse-fix, 1956 facts, director hand-score **40 / 16 / 44 = MIDDLE_BAND**
  (`notes/director_handscore_b3_v4_parsefix_2026-08-12.md`)

## Honest constraint, stated up front

Two consecutive quality passes have moved 38% -> 40%. That is FLAT. This pre-reg is written
with the explicit expectation that a third flat result is a real possibility and is a MORE
useful answer than another marginal number. The falsifier below is written so that a flat
result cannot be spun as partial success.

## Prior-work check (substrate-KB concept-query, mandated)

`bash tools/substrate_query.sh "definitional extraction term boundary glossary genus hypernym"`
-> top hits at cosine >0.30: `dictionary_definition` (0.3389, WordNet lexicon entry),
`dictionary definition` (0.3389, atoms), `extraction` (0.3174), **`hdlab/definitional_extraction.py`
(0.3164, sourced from `notes/definitional_grounding_v3_2026-08-12.md`)**, `glossary` (0.3066).
The only ARC hit is this module's own v3 note -- i.e. this is a CONTINUATION of the same arc,
not a rediscovery of separate prior work. No prior cell has attacked term boundaries.

## Question

The v4 hand-score identified corrupted multiword terms as the new dominant fault. Is that
fault (a) as frequent as the 8/22-in-50 sample suggested, and (b) the binding constraint on
DEF fact quality?

## MEASURED corruption rate in v4 (done BEFORE any fix, as instructed)

**Operational definition. A v4 fact's stored `subject` is CORRUPTED iff EITHER test fires:**

- **T1 BOUNDARY-CROSSING TERM.** The subject is multiword; locate its tokens as an in-order
  minimal window in its source sentence (closed-class tokens that `build_term` drops may be
  skipped); CORRUPT iff the raw text of that window contains a character that cannot occur
  inside one term (`. , ; : ( ) [ ] " ! ?`) or an interior token that cannot occur inside one
  term (`and or but nor` / a finite verb / a complementizer / a preposition).
- **T2 GLOSSARY-KEY MISMATCH.** `pattern == GLOSSARY_COLON` and `segment == bio_new` and the
  normalized subject is NOT one of the 926 ground-truth glossary keys recovered from the LINE
  STRUCTURE of `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt`
  (lines of the form `<term>: <definition>` with a definition longer than 15 chars). This is
  GROUND TRUTH, not a heuristic: the true glossary keys exist on disk and were destroyed only
  by the corpus loader's `" ".join(lines)`.

**Result, over ALL 1956 v4 facts** (MEASURED@`/tmp` prototype, reproduced by
`audit_corruption()` in `experiments/exp_definitional_grounding_v5.py`):

| quantity | value |
|---|---|
| T1 boundary-crossing terms | 22 |
| T2 glossary-key mismatches | **292 of 363 glossary facts = 80.4%** |
| **CORRUPT (T1 or T2)** | **314 / 1956 = 16.1%** |

**This is a LOWER BOUND.** T2 cannot fire when a corrupted term happens to coincide with some
other valid glossary key (confirmed instance: `population -> allele`, harvested from an entry
whose true term is `migration`). T1 cannot fire on a same-clause merge with no punctuation.

The director's sample rate was 11/50 = 22% (8 glossary + 3 non-glossary); the corpus-wide
lower bound of 16.1% is consistent with it at se ~5.8pp. **The diagnosis is CONFIRMED, and the
sample UNDER-stated how bad the glossary path is: four of every five glossary facts carry a
term that is not a real term of the source textbook.**

## Root cause (two bugs, both verified by reading the code and the corpus)

1. **`_GLOSSARY_ENTRY` absorbed leftward.** The split regex allowed the entry term to be up to
   FOUR words and regex alternation picks the LEFTMOST viable start, so the term ate up to three
   words of the PREVIOUS entry's definiens:
   `"...interactions with their abiotic environment equilibrium: the steady state..."`
   -> term `abiotic environment equilibrium` (true term: `equilibrium`).
2. **`_expand_proper_name` walked the TOKEN list, which drops punctuation**, so a name merged
   across a comma or a period: `"Like DNA, RNA is a polymer"` -> `DNA RNA`.

And one UPSTREAM cause that is not a parser bug at all:

3. **`load_biology_sentences` does `" ".join(kept)`**, destroying the one-entry-per-line
   structure that the cleaned OpenStax file actually has (line 8715 is exactly
   `equilibrium: the steady state of a system ...`). Joined, the glossary becomes 50 run-on
   pseudo-sentences up to 4776 chars. Per-line it is 0 such blocks.

## Fixes (declared before implementation)

| id | where | fix |
|---|---|---|
| **F7** | `hdlab/definitional_extraction.py` (committed e01db310b) | proper-name expansion requires a spaces-only gap between adjacent tokens, in BOTH directions. Kills `DNA RNA`, `Wembley Stadium Bowie`, `Mars Bas Lansdorp`, `Norway Germany`, `December Mikhail Kalashnikov`, ... |
| **F8** | `hdlab/definitional_extraction.py` (committed e01db310b) | the glossary split point is the LAST token before the colon. Inside a run-on block the true left edge of a term is UNRECOVERABLE, so the term is deliberately UNDER-SPECIFIC (`web` for `detrital food web`) rather than a DIFFERENT CONCEPT. Under-specific beats corrupt. |
| **F9** | `experiments/exp_definitional_grounding_v5.py` (this cell only) | `load_biology_sentences_lineaware`: sentence-split PER LINE instead of over the joined text. This RECOVERS the true multiword glossary terms, because a line-aware entry is its own sentence and `_RE_COLON` (anchored at `^`) reads the full correct term. |

**F9 IS A SECOND VARIABLE AND IS DECLARED AS SUCH.** It changes the corpus for the `bio_new`
segment (11332 -> 12559 sentences; max sentence length 4776 -> 591 chars; run-on blocks
>1000 chars 50 -> 0). It touches NO file owned by another agent -- the v5 cell defines its own
loader and does not call `load_biology_sentences`. To keep attribution honest the cell reports
the corruption rate for BOTH configurations:
- `ARM_PARSER_ONLY` = F7+F8, v4's loader (isolates the parser fix)
- `ARM_CANONICAL` = F7+F8+F9 (the shipped set; the one that is sampled and hand-scored)

## Deliberately NOT fixed (judged OUT OF SCOPE; reported, not repaired)

- **INVERTED HYPERNYMY** (`bacteria -> fixation`, `cell -> lymphocyte`, `pellucida -> event`).
  **Stated plainly: this fix does NOT touch inverted hypernymy.** It is not a parse bug. It is
  not knowing which side of a definitional sentence carries the genus, which is a SEMANTIC
  judgement that no surface cue in the sentence supplies. Auto-reported as a count via WordNet
  (`INVERTED` iff `object` has a hypernym path THROUGH `subject`, i.e. the stored direction is
  the reverse of WordNet's).
- **ADJECTIVAL / LIST HEADS** (`Margaret Thatcher -> best`, `dominant phase -> short`,
  `quadrat -> wood`). These are DEFINIENS-side faults; fixing them in the same pass would
  confound attribution of the term-boundary result. Auto-reported as a count.
- **ROLE-NOT-MEANING** (`predecessor -> warner`, `Lodge -> scene`). Semantic, same reasoning.

## Compute architecture

Class **(b) sequential-CPU with justification**: regex + WordNet lookups over ~34k sentences;
v4's identical pipeline ran FULL in ~40s. No matmul, no seeds, no sweep, no GPU speedup
available. Storage strategy `no_composition` (facts sharded into HDFactStore as in v3/v4).
Runs FOREGROUND to completion in one call. `progress_logging`: n/a (`timeout_s` << 1800).

## PRE-REGISTERED BANDS

### (a) FACT QUALITY -- NOT auto-scored, NOT claimed by this agent

A fresh 50-row sample is written **UNSCORED** to
`data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json`, seed=42, sampling procedure
bit-identical to v2/v3/v4 (asserted in the cell self-test), identical field schema, for the
DIRECTOR to hand-score on the same MEANINGFUL / RELATED / NOISE rubric.

| band | condition (MEANINGFUL rate on the director's hand-score) |
|---|---|
| HARD_PASS | **>= 52%** AND >= 900 facts |
| PASS | **>= 47%** AND >= 900 facts |
| MIDDLE_BAND | 42 - 47% |
| **FAIL** | **<= 42%** -- inside one se of v4's 40%; the term-boundary theory was WRONG |
| **FAIL (yield)** | fact count < 900 whatever the rate |

**Basis for the edges, all HYPOTHESIZED@this prereg.** 16.1% of the v4 set is machine-certified
corrupt and every such row is NOISE by construction. In the director's own 50-row sample 11 rows
were corruption and all 11 were NOISE; the other 39 rows carry all 20 MEANINGFUL, i.e. the
CLEAN subset of v4 already scores 20/39 = 51%. So: if the fix merely DELETED corrupt rows the
rate would land near 51%; it instead REPLACES them with the corrected rows
(`equilibrium -> state`, `biome -> community`), which are real textbook glossary definitions and
should score at or above the clean base rate. 52% is that reasoning discounted for fixes that
misfire and for the F8 under-specificity cost. 47% (PASS) is the point at which the fix has
clearly bought more than sampling noise. 42% (FAIL) is v4's 40% plus a fraction of one se.

### (b) THE FALSIFIER -- what result means the term-boundary theory was WRONG

**If the machine-measured corruption rate falls to <= 4% AND the director's hand-score is
<= 42%, the term-boundary theory is REFUTED.** In that case the corrupted terms were an
obvious-looking but NON-BINDING fault: removing them did not buy quality, so what caps DEF
quality is the residual semantic classes (inverted hypernymy, adjectival/list heads,
role-not-meaning) plus the shallowness of surface-pattern extraction itself. That outcome will
be reported as **"surface-pattern definitional extraction has reached its ceiling at ~40%"**,
with the three consecutive flat results (38 -> 40 -> flat) as the evidence, and NOT as a
partial win.

**Vacuity guard (META_RULE_K, discriminator-fires).** If the measured corruption rate does NOT
fall below 4%, the cell emits `HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE` and the hand-score is
MEANINGLESS for this question -- the fix did not do what it claims, and no quality band may be
read off it either way.

### (c) MULTI-SENSE YIELD -- auto-reported (counts, not judgements), on BOTH keys

Reported as the triple (`n_multi_sense_words`, `n_senses_with_gt1_source_sentence`,
`n_multi_sense_words_with_ALL_senses_gt1_sentence`) on BOTH indexes.

| index | v4 MEASURED | v5 |
|---|---|---|
| `subject` (full TERM) | 197 / 51 / 2 (MEASURED@`data/exp_definitional_grounding_v4/metrics.json:multisense_yield_AFTER_v4`) | auto-reported |
| `subject_head_lemma` | 333 / 135 / 7 (MEASURED@`notes/director_handscore_b3_v4_parsefix_2026-08-12.md` lineage; recomputed here from the v4 file) | auto-reported |

**PRE-DECLARED EXPECTATION so it cannot be spun after the fact:** F9 RAISES specificity
(`equilibrium` becomes a correct standalone term rather than a merged one) which SPLITS term
keys and should push the TERM-index yield DOWN or flat; F8 in the parser-only arm pushes it UP
by collapsing run-on terms onto their head. **I do not know the sign of the net on either
index.** No band is attached to yield. If yield falls while quality rises, that is a REAL
TENSION between fact quality and sense-eval power and will be reported as such, not averaged
away.

## FAILURE CONDITIONS (machine-checked by the cell)

- `HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE` -- corruption rate in `ARM_CANONICAL` > 4%.
- `HARD_FAIL_YIELD_COLLAPSE` -- fewer than 900 facts.
- `HARD_FAIL_SAMPLING_DRIFT` -- seed-42 sampling not bit-identical to v2/v3/v4
  (self-test asserts on a 634-length synthetic list).
- `HARD_FAIL_F1_REGRESSION` -- ANY of the 8 director-confirmed F1 proper-noun gains is lost:
  `Chon -> counsellor`, `Naeem -> campaigner`, `Olkin -> scientist`, `Rajagopalan -> student`,
  `Shanhui Fan -> expert`, `Currie Technologies -> seller`, `Piraeus -> port`,
  `Drosophila -> fly`. Also `fan -> expert` and `technology -> seller` must stay ABSENT.
  Each is ALSO a named regression test in `hdlab.definitional_extraction._self_test`.
- `HARD_FAIL_CONTROL_ROWS` -- any v4 control row lost (`aorta -> artery`,
  `cholesterol -> lipid`, `arthropoda -> phylum`, `arteriole -> vessel`).
- `HARD_FAIL_REGRESSION` -- any v4 fault row returns (`fan -> expert`, `technology -> seller`,
  `kidney -> ureter`, `system -> locomotion`, `structure -> function`, `dialysis -> medical`,
  `kidney -> pair`, `bubble -> region`, `effect -> magnification`) or any of the 3 director-cited
  v4 term merges returns (`DNA RNA -> polymer`, `Mars Bas Lansdorp -> founder`,
  `Wembley Stadium Bowie -> performer`) or any of the 8 director-cited glossary corruptions
  returns.

## Discipline fields

- `arms_differ_verified`: v4 / ARM_PARSER_ONLY / ARM_CANONICAL fact sets are sha256-compared;
  any two identical = the fix did not fire = BLOCK.
- `final_metrics_atomicity`: `tmp_replace`.
- `crlb_n/a`: deterministic symbolic extraction; no estimator noise floor. The relevant
  feasibility bound is BINOMIAL and is where the band edges above are placed (se at n=50 and
  p~0.45 is 7.0pp, which is why FAIL is set at 42% and PASS at 47%).
- `baseline_in_band`: v4 = 0.40 MEANINGFUL, inside (0.05, 0.95).
- `calibration_check`: `default_ok_for_this_regime` -- PMI floor, closed-class gate and n_dim
  carried over UNCHANGED from v3/v4; the PMI control pairs are asserted to survive or the cell
  halts.
- `cell_chunked`: false (single deterministic pass, no seed axis).
- `defensive_error_checking`: start marker + crash metrics + `except SystemExit: raise` before
  `except Exception`; no bare except; heartbeat n/a (~60s run).
- `deterministic_seeding`: true -- fixed integer seed 42, `sorted(set(...))` only.
- `real_code_path_exercised`: `extract_definitions`, `build_term`, `split_glossary_entries`,
  `HDFactStore`, `build_profile`, `load_biology_sentences_lineaware`.
