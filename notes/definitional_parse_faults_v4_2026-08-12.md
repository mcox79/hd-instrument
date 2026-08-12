# Definitional parse faults v4 -- 2026-08-12 (exp_dev, incremental)

Task: fix the PARSE faults the director's per-row hand-score named, and in doing so produce a
cleaner MULTI-SENSE set (621/723 senses currently have one source sentence, which is what leaves
the sense-selection eval underpowered). Written incrementally; committed after each step.

Source of the fault list: `notes/director_handscore_b3_def_vs_control_2026-08-12.md` (19
MEANINGFUL / 9 RELATED / 22 NOISE out of 50). Every claim below was re-verified on disk; nothing
is inherited.

## 0. Prior-work check (MANDATORY concept-query)

`bash tools/substrate_query.sh "definitional parse fault proper noun collision appositive list
subject truncation multiword term polarity inversion"` -> confidence 0.3457. Top hits are WordNet
/ Gene-Ontology lexical entities (`a multidimensional proposition` 0.3457, `faulty position`
0.3057, `collision` 0.3037), **no arc cell at cosine > 0.30**. Prior-work check: NONE. This is
parse-repair on an artefact built 8 hours ago; genuinely novel, not a rediscovery.

## 1. FAULT MECHANISMS -- each CONFIRMED on the actual row before any fix

Every one reproduces. `dfd` = stored `definiendum_surface`, `dfs` = `definiens_surface`.

| # | fact | mechanism, read off the row |
|---|---|---|
| 1 | `fan -> expert` | dfd=`Fan` from "said Shanhui Fan, an expert in..." -- a SURNAME whose lowercase form is the common noun `fan`. Name is truncated (preceding token `Shanhui` also capitalised). |
| 1 | `technology -> seller` | dfd=`Technologies` from "CEO of Currie Technologies, the number one seller..." -- head token of a multi-token ORG name, lowercased onto the common noun. |
| 2 | `kidney -> ureter` | "comprised of the paired kidneys, the ureter, urinary bladder and urethra". Both existing list-guards miss it: the tail after the closing comma does not start with `and`, and the definiendum is not preceded by `, the`. |
| 2 | `system -> locomotion` | CALLED pattern; dfs captured as `and locomotion` -- the LAST ITEM of "for gas exchange, nutrient circulation, and locomotion called the water vascular system". |
| 3 | `bubble -> region` | dfd=`transcription bubble`; only the head lemma `bubble` is stored as subject. Same for `Age structure`->`structure`, `bottleneck effect`->`effect`, `latent unit factor`->`factor`, `water vascular system`->`system`. |
| 4 | `structure -> function` | CALLED; dfs=`These unused structures without function`. `without` is ABSENT from `_NP_BOUNDARY` in `hdlab/definitional_extraction.py:118`, so the head walk crosses the negation and lands on `function`. |
| 5 | `dialysis -> medical` | dfs=`a medical process of removing wastes...`. `process` is listed in `_NON_HEAD` (line 68), so it is excluded from `strong`, and the ADJECTIVE `medical` survives as the last "strong" token. There is NO part-of-speech test on the head. |
| 5 | `kidney -> pair` | dfs=`a pair of bean-shaped structures...`. `pair` is a MEASURE/partitive head; the content sits in the of-complement (`structures`). |
| 5 | `cancer -> collective` | NOT the head rule -- a GLOSSARY RUN-ON. dfd is literally `and are surrounded by new nuclear envelopes Cancer`: the OpenStax glossary block has no sentence boundaries, so one "sentence" contains many `term: definition` entries. Same cause as `effect -> magnification`, whose dfs runs into the next entry (`... catastrophes founder effect: a magnification ...`). **This is a 6th fault class the director's list did not name; found by verifying the 5th.** |

## 2. FREQUENCY ACROSS ALL 1751 FACTS (not the 50-row sample)

Tool: `tools/measure_definitional_parse_faults_v1.py` (READ-ONLY; touches nothing under
`data/foundation/`). MEASURED@`data/analysis_definitional_parse_faults_v1/metrics.json`.

| class | rows flagged | % of 1751 | breakdown |
|---|---|---|---|
| F1 proper-noun handling | **319** | 18.2% | 223 collide with a common noun (127 of those ALSO name-truncated), 96 name-truncated only. Plus **49 CLEAN proper nouns** (`piraeus->port`, `omikron->game`) counted separately and NOT a fault. |
| F2 list read as appositive/definiens | **78** | 4.5% | 35 coordinate tail, 21 enumeration trigger + bare NP, 22 definiens starts with a coordinator |
| F3 subject truncation | **588** | 33.6% | 469 genuine multiword terms, 119 run-on definienda (>4 content tokens or containing a finite verb) |
| F4 polarity inversion | **2** | 0.1% | negation scoping directly over the object |
| F5 bad definiens head | **168** | 9.6% | 124 head is not a WordNet noun (adjective/verb), 38 measure-head + indefinite of-complement, 6 other measure-head |
| F6 glossary run-on | **53** | 3.0% | a second `term:` entry inside the same "sentence" |
| **any flag** | **992** | **56.7%** | |

**Detector honesty (stated, not hidden).** These are FAULT-SUSPICION counts: a flag means the
named parse mechanism fired, not that the fact is wrong. I spot-checked every class and TIGHTENED
two detectors after finding false positives, before reporting any number:
- F2 first read 209 rows; loose "coordinator in the tail" flagged `aorta -> artery` (the tail
  "taking oxygenated blood to..." is a participial adjunct) and `china -> importer` (a coordinated
  CLAUSE). After requiring a short bare-NP definiens + no verb before the coordinator + no clause
  after it: 78. Residual false positives remain visible (`diploid -> configuration`), so 78 is an
  UPPER bound.
- F4 first read 7; "any negation before the object" flagged `mesophyll -> layer`, where the object
  sits in the POSITIVE branch of "not on the surface layers, but rather in a middle layer". After
  requiring an exclusion cue scoping within 2 tokens: **2**. Polarity inversion is RARE -- the
  director's 1/50 sample rate overstated it ~5x, and it is the least valuable class to fix.
Conversely F3's 588 is a LOWER bound on the affected population in one sense (it counts only rows
whose stored surface is multiword) and an over-count of "faults" in another (`Migratory Bird Act`
-> `act` is arguably fine). F1's 319 includes rows the director scored MEANINGFUL
(`kebede -> entrepreneur`, `abdullah -> minister`) -- those are name-TRUNCATION, not collisions,
and the fix improves them rather than dropping them.

**Ranking by frequency x scoring-weight: F3 (33.6%) and F1 (18.2%) dominate; F5 (9.6%) is the
cheapest real precision win; F4 (0.1%) is nearly a non-issue.**

## 3. MULTI-SENSE YIELD -- BEFORE (independently recomputed, matches the inherited numbers)

MEASURED@`data/analysis_definitional_parse_faults_v1/metrics.json:multisense_yield_BEFORE`:

| quantity | value |
|---|---|
| facts / distinct subjects | 1751 / 1316 |
| multi-sense words (>1 distinct object) | **288** |
| facts belonging to a multi-sense word | 723 |
| **senses with >1 source sentence** | **102** (dist 1->621, 2->78, 3->24) |
| multi-sense words with ANY sense >1 sentence | 83 |
| **multi-sense words with EVERY sense >1 sentence** (the leave-one-sentence-out population) | **7** |

This reproduces `notes/context_conditioned_sense_selection_2026-08-12.md` exactly (288 / 723 /
621 / 7), so the two measurements are independent and agree.
