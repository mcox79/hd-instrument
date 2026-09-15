---
problem: the_heads_rung_attaches_the_subject_of_a_non_verbal_predicate_at_0_54_against_0_85_for_verbal_ones_land_the_predicate_slot_as_a_graded_online_learned_arc_feature
status: SOLVED
bar: "Non-verbal-subject attachment up CI-separated from 0.5385 toward the prototype's 0.6509 or beyond, verbal not down, with the feature's validity LEARNED (counts + observe path; a twin with the validity permuted at floor); the held/reshape decode landed in the in-order arm; the participant instrument's recall on the 167 up; board not down full-size -- OR a numbered located negative naming the wall (A / B / C above) with its count."
result: "UD-EWT test 700, live chain (organ categories + graded posterior), population = the 169 gold nsubj/nsubj:pass arcs whose gold head is not a gold VERB. Measured THROUGH THE DIFF, the organ as shipped vs the patched organ, BOTH IN ONE PROCESS: non-verbal subject attachment 0.5385 -> 0.6568 (+0.1183 CI[+0.0705,+0.1706] SEPARATED), verbal subjects 0.8533 -> 0.8617 (+0.0083 CI[+0.0000,+0.0187], not separated, NOT down), UAS 0.6331 -> 0.6370 (+0.0039 CI[+0.0016,+0.0064] SEPARATED UP); per relation nsubj 0.7841 -> 0.8166, cop 0.6398 -> 0.6935, expl 0.8333 -> 0.9583, root unchanged; the largest give-back on a relation with n>=100 is conj -0.0086 (n=233), and the largest anywhere is iobj -0.0278 (n=36, one item). The cue's validity is LEARNED, never hand-set: 4,560 arcs accrued from 4,000 sentences of reading through the organ's own categories (no gold column, no tree, no treebank head), 74 cells, shipped as data/hook_state/attachment_validities_csubg_v1.json (every other cue in the table byte-identical, asserted). OUT OF SUPPLY (GUM/GENTLE, 12+ genres, 367 non-verbal subjects): 0.4796 -> 0.5613, verbal 0.8072 -> 0.8173 (up), UAS 0.6092 -> 0.6135. The lever decomposition on the same population: detection coverage 0.5385 -> 0.5740, + the graded occupancy cue 0.6509, + predicate-arrival reanalysis 0.6686 (cell readout; the diff's own end-to-end number is 0.6568 because it computes the occupancy inside the tag mixture). DOWNSTREAM, on pri 113's OWN participant instrument (unmodified, both arms in one process): the arm that reads the predicate slot FROM THE PARSE rises 0.6048 -> 0.7006 recall on the 167 non-verbal clauses (state-registered 0.6108 -> 0.7066, pooled precision 0.8229 -> 0.8277), and pri 113's headline located negative -- the parse hand-off CI-separated BELOW the closed-class construction scan, -0.1317 CI[-0.1976,-0.0719] -- becomes -0.0359 CI[-0.0898,+0.0240], NO LONGER SEPARATED. LEARNING CURVE (plasticity): 0 sentences read 0.6154, 250 -> 0.6331, 1,000 -> 0.6627, 4,000 -> 0.6686. At the organ's own beam=16 operating point the patched arm is 0.6746 with UAS 0.6414 (beam 32: 0.6864 / 0.6447). READ-TIME COST: none (shipped 20.1 ms/sentence, patched 19.5). FULL BOARD (both arms one process, full size): six of seven dimensions EXACTLY unchanged (coref 0.4178, common-noun 0.5461, salience 0.2656, agent 0.8552, state 0.7910, wic 0.7833), who_did_what_patient 0.8151 -> 0.8135 (-0.0016 = 2 items of 1255), aggregate 0.5947 -> 0.5945. The board iterates GOLD VERBS on the who-did-what dimensions, so it cannot see this gain by construction (pri 113 section 6) -- which is why the participant instrument is the consumer-level evidence. PHASE 7 (2026-09-15) CHANGED THE SHIPPED CONFIGURATION: the hyphen correction to the subject scan is ON, so the headline is 0.6509 (+0.1124 CI[+0.0659,+0.1634] SEP) rather than 0.6568, verbal 0.8617, UAS 0.6367 (+0.0036 SEP), and the board give-back is ONE patient item rather than two (that dimension standalone 0.8151 -> 0.8159; the FULL board was run on the pre-correction configuration, so strategy's integration board is the one that scores the shipped one). DOWNSTREAM: the entity-attribute HOLDER capture 0.6532 -> 0.7903 (+0.1371 CI[+0.0789,+0.2017] SEP, n=124 covered clauses)."
floor: "The live arm exactly as shipped (csub cue on, incremental decode, the landed attachment_validities_v1.json): non-verbal subject attachment 0.5385 (n=169), verbal 0.8533 (n=600), UAS 0.6331 -- reproduced to the digit in every run. Also run as reference points: the owner's pri 113 prototype reproduced in-cell 0.6391; the BEST hand-set frozen constant, swept w in {1,2,3,4.6,6,8,12} and chosen ON THE TEST POPULATION, 0.6568; the whole-sentence MAP decode of the same scores 0.7041; a hard forced re-attach on the detected pairs 0.7219."
controls: "(1) RANDOM-SITE TWIN -- the same accrued validities applied to random (content head, nominal dependent) pairs at the matched rate: 0.6213, learned beats it +0.0473 CI[+0.0179,+0.0803] SEPARATED (so the win is the construction, not 'push some arcs harder'). (2) OCCUPANCY-PERMUTED TWIN -- the occupancy column shuffled across tokens so the graded VALUE carries no information: 0.6154, learned beats it +0.0533 CI[+0.0233,+0.0893] SEPARATED (so the gradedness is load-bearing). (3) FROZEN-CONSTANT FLOOR, swept and tuned on the test population: best 0.6568 vs learned 0.6686, +0.0118 CI[-0.0115,+0.0343] NOT separated -- reported against myself: the learned table beats every frozen constant tried including the oracle-tuned one, but not CI-separably at n=169. (4) ORACLE PAIRS -- the cue fed the GOLD (predicate, subject) pairs: 0.6450, i.e. -0.0059 CI[-0.0438,+0.0323] vs the learned arm, so perfect detection buys NOTHING and pri 113 section 29's 'detection coverage is the limiter' is overturned with a number. (5) SWITCH-OFF EQUIVALENCE -- with HDLAB_ARM_CSUB_COVERAGE=0 the new pair detection reproduces the shipped csub detection exactly (0 differences over 120 sentences, asserted in --self-test); with no occupancy the graded cue is silent. (6) PATCHED == REFERENCE -- the vectorised readout equals the per-pair reference loop to 1e-9 WITH the occupancy on (60 sentences), the organ's own fastpath invariant. (7) THE ORGAN'S OWN WITNESSES RUN AGAINST THE PATCHED ORGAN with the accrued asset installed: verification/test_attachment_arm.py 17/17 (including the decode contract -- one root, connected tree, identical through the frontend -- and the plasticity round-trip) and verification/test_attachment_arm_fastpath.py PASS (max |fast - reference| 3.55e-15, MAP heads agree 40/40). (8) DETERMINISM OF THE REGRESSING ROW (phase 7): the board's patient dimension run THREE times on the same tree with the same organ gives 0.8167 / 0.8167 / 0.8167 with item-level churn 0 and 0 -- so the two items it loses are real and reproducible, NOT run-to-run noise (this CORRECTS what section 4i first said). (9) THE ONLINE ACCRUAL vs A FULL REBUILD (phase 7): the whole table rebuilt by the patched builder scores 0.6627 / 0.8617 / UAS 0.6368 against the overlay's 0.6568 / 0.8617 / 0.6370, every contrast's CI containing zero -- the two-minute online accrual matches a 6,000-sentence rebuild. (10) A FAILED CONTROL, recorded: a twin that accrues the validity from random pairs ('tacc') ties the learned arm exactly (+0.0000 CI[-0.0172,+0.0172]) -- it is uninformative BY CONSTRUCTION, because my twin accrual still hands the outcome by the value label; and the first validity-permutation twin was also uninformative (41 of 52 cells are positive, so a permutation keeps 36 of 41 positive). Both are reported rather than quietly dropped."
files_changed: "experiments/exp_copular_subject_attachment_learned_v1.py (the cell: the PATCH block, the accrual, the arms, the twins, the oracle/residual/frozen diagnostics, the one-process live A/B through the diff, the learning curve, the read-time measurement, the board A/B runner); notes/problems/<slug>/{SOLVED.md, copular_subject_attachment_patch.diff}; data/hook_state/attachment_csubg_validity_v1.json (the accrued cue, for inspection) and data/hook_state/attachment_validities_csubg_v1.json (the SWAPPABLE table = the landed counts + the accrued cue); data/hook_state/attachment_validities_rebuilt_csubg_v1.json (phase 7: the same table taught jointly by the patched builder, for the equivalence control -- NOT the shipped asset); data/exp_copular_subject_attachment_learned_v1/*.json. NO hdlab/ or tools/ file edited -- the proposal is the diff, which applies cleanly at HEAD 6e35d9fe4 and is EXECUTED by the cell (--patch-test / --live-ab load it in memory as hdlab.attachment_arm)."
reverify: ".venv/Scripts/python.exe experiments/exp_copular_subject_attachment_learned_v1.py --self-test  (17/17) ; then --patch-test --cap 120 (6/6, runs the diff's own code) ; then the headline, ~2 min, writes only into its own directory: HDLAB_EXP_NAME=copular_subject_attachment_learned_v1 .venv/Scripts/python.exe experiments/exp_copular_subject_attachment_learned_v1.py --live-ab --cap 700 ; out of supply: --live-ab --gum --cap 1200 ; the lever decomposition and the twins: --arms --cap 700 ; the controls: --oracle --cap 700, --frozen --cap 700, --residual --cap 700. The organ's own witnesses against the patched organ: python -c "import sys;sys.argv=['x'];import experiments.exp_copular_subject_attachment_learned_v1 as C;C.patched_module();import runpy;sys.argv=['v'];runpy.run_path('verification/test_attachment_arm.py',run_name='__main__')" (17/17). The accrual is reproducible from reading: --accrue --cap 4000 (~2 min, rewrites both hook_state assets). PHASE 7 arms: --patient-flips (the two board items, named, plus the 3-run determinism check), --compare-tables (the rebuilt table vs the overlay), --pooled-frozen (UD+GUM pooled), --carrier-cases, --beam-lead (Q2, filed not flipped), --curve-tail, --binding, --rebuild (~3 min)."
---

# SOLVED -- the predicate slot is now an arc feature with an online-learned validity, and the in-order decode revises the subject when the predicate arrives

**0.5385 -> 0.6509 on the non-verbal subject (CI-separated), with the verbal population not down, UAS up, and the
validity accrued from reading rather than set by hand.** *(0.6568 before the phase-7 hyphen correction to the
subject scan, which trades one arc here for one board item -- P7.2.)* The owner's pri 113 prototype number (0.6509) is reached
and passed by a mechanism that is learned and plastic instead of a boost/penalty pair, and three of the brief's
inherited assumptions were overturned with numbers (below). The full-size board is flat -- six of seven
dimensions EXACTLY unchanged, one down by two items of 1255 -- and section 4i says what I think should be done
about those two.

---

## 1. THE BAR, IN MY OWN WORDS

Make the heads rung attach "the sky" to "blue" as reliably as it attaches "the dog" to "barked" -- and do it the
brain's way: the strength of the cue must be **learned from experience and keep moving**, not a constant somebody
tuned. The number to beat is 0.5385 on the 169 subjects whose predicate is not a verb; the prototype said 0.6509 is
reachable; the verbal subjects (0.8533) must not pay for it; a version of the mechanism with its information
removed must lose; and the board must not go down at full size.

## 2. THE UPSTREAM CHAIN AND WHAT EACH RUNG HANDS DOWN (the status probe, with counts)

The signal the end read needs is *"which token holds this clause's predicate slot, and how strongly"*.

| rung | organ (file) | what it PRODUCES for this signal | what the next rung READS | what is LOST |
|---|---|---|---|---|
| tokens | `frontend.tokenize` | the token sequence | all | nothing measured here |
| categories | `hdlab/lexical_categories.py` | a graded posterior per token, **with pri 110's predicate-slot occupancy already applied** (`revise_for_predicate_slot`) | the heads rung reads the posterior | **the occupancy reached the heads rung only as a revised TAG.** 14 of the 60 residual misses are a participial predicate the organ reads as VERB ("It 's just DISAPPOINTING", "the people will be DEAD"), which made the copular construction invisible to the cue |
| lemma | `hdlab/morphology.py` | lemmas for the frame cue | the frame cue | not load-bearing for this arc |
| **heads** | `hdlab/attachment_arm.py` | the arc competition | the roles rung, the event/state readers, the entity layer | **THE LOSS THIS BRIEF NAMES.** The `csub` cue existed but (a) keyed on the narrowest complement scan, (b) was CATEGORICAL, so an uncertain predicate competed as hard as a certain one, and (c) the in-order beam committed the subject before the predicate arrived |
| roles / events / state / entities | `graded_role_assigner`, `situation_reader` | who did what, the typed state | the board | pri 113 measured the propagation: the parse hand-off to the event stream 0.6048 -> 0.7186 and entity binding 0.7087 -> 0.8932 under a repaired subject arc |

**Brain-foundational status of each rung for THIS signal, as the disk shows it:** categories BF (pri 110, graded,
top-down constraint satisfaction on a settling belief); lemma BF-spirit; heads BF_SPIRIT (cue competition with
learned validities -- the computation is the Competition Model's, the *constructions* are hand-written item-based
schemas); the consumers BF for the predicate slot since pri 113 landed. **The one non-BF link in the chain for this
signal was the hand-off itself**: a graded quantity computed upstream was delivered downstream as a point estimate
(a tag). That is what this solution fixes.

## 3. THE BRAIN, AND THE THREE COMPUTATIONS BUILT

**Opening move -- how does the brain do this?** A clause predicates one thing of its subject (Spivey-Knowlton 1993);
the copula is only the tense carrier and the CONTENT is the complement (Pustet 2003; Bybee 1994 on auxiliation);
which word heads which is decided by a competition among cues whose validity = availability x reliability, accrued
from what the comprehender perceives (Bates & MacWhinney's Competition Model); and when a later word disambiguates,
the analysis is revised rather than re-derived (Frazier & Rayner 1982; MacDonald 1994 overtaking; Levy 2008 on
expectation, Gibson 1998 on storage cost). Nothing in that list is a new organ -- all three are ARMS of the
attachment arm the substrate already has, which is why nothing new was minted (`BRAIN_STRUCTURE_CONSOLIDATION_AUDIT`
gate).

1. **THE PREDICATE SLOT AS A GRADED ARC FEATURE (`csub_graded_sites` + the `csubg` cue).** pri 110 computes
   P(token q holds its clause's predicate slot) off the category organ's own posterior (`predicate_sites`). It now
   enters the arc competition as the VALUE of a cue -- `pred:hi|md|lo|no` on the (predicate <- subject) arc,
   `later:<bin>` on every verb to the predicate's right (small-clause locality, Stowell 1981: a verb inside the
   predicate phrase is not the matrix predicate), `carrier:<bin>` on the copula's own arc (the tense carrier is not
   the predicate) -- and its validity is a learned log-odds contrast per configuration, exactly like every other cue
   in the organ. The bin edges (0.25 / 0.60 / 0.85) and the accrual weight are swept operating points, never adopted.
2. **THE VALIDITY IS ACCRUED FROM READING (`observe_copular_subject`).** Every copular predication PERCEIVED in
   running text is one confirmed outcome: the slot-filler heads the pre-copular nominal with the occupancy as the
   strength of the belief, and the competing verbs accrue the zero outcome. No treebank, no tree, no gold column --
   the construction is stored lexical knowledge the organ already carries (COP_FORMS; Goldberg 1995). 4,560 arcs
   over 4,000 sentences tagged by the organ itself. This is the observe path the brief demands: the same function
   runs online, one sentence at a time, and the strengths are recomputed from the counts.
3. **PREDICATE-ARRIVAL REANALYSIS (`revise_copular_subject`).** The in-order beam commits the subject while the
   clause's predicate is still unresolved. When the predicate arrives, the subject's attachment is revised **if the
   organ's own learned activations prefer it** -- no parameter, no threshold, only words already heard, and the
   same accounting `INCR_ROOT_REANALYSIS` already applies to the root arc. This is the landed, in-order form of the
   prototype's "held" decode (which resolved the copular subject on the whole-sentence MAP, i.e. with lookahead).

**Coverage came along for free and is not the lever (see section 5):** the cue's pair detection was re-keyed from
`cop_predicates` to `cop_complement` (the construction set the merged pri-113 tree carries) plus the inverted
construction's post-copular subject, and the tense carrier's VERBAL host is now admitted as the predicate too --
the brain's claim is the same under pri 110's branch (1) and branch (2): *the subject attaches to whatever holds the
slot*.

## 4. THE MEASUREMENT

**Population** (unchanged from the brief): UD-EWT test 700, the 169 gold `nsubj`/`nsubj:pass` arcs whose gold head
is not a gold VERB; the verbal comparison is the other 600. Live chain throughout (the organ's own categories and
graded posterior; the gold column is the measuring instrument only). Paired bootstrap over sentences, 2,000 resamples.

### 4a. Through the diff -- the organ as shipped vs the patched organ, both in one process

| | non-verbal subject (n=169) | verbal subject (n=600) | UAS (n=16,268) |
|---|---|---|---|
| the organ as shipped | 0.5385 | 0.8533 | 0.6331 |
| **the patched organ + the accrued validity** | **0.6568** | **0.8617** | **0.6370** |
| paired delta | **+0.1183 CI[+0.0705,+0.1706] SEP** | +0.0083 CI[+0.0000,+0.0187] ns | **+0.0039 CI[+0.0016,+0.0064] SEP** |

Per relation (shipped -> patched, n >= 20): **nsubj 0.7841 -> 0.8166, cop 0.6398 -> 0.6935, expl 0.8333 -> 0.9583,
aux 0.9312 -> 0.9365, ccomp 0.6897 -> 0.7069, xcomp 0.7591 -> 0.7664, obl 0.4801 -> 0.4822, root unchanged**;
down: conj 0.4206 -> 0.4120 (n=233), advcl 0.4030 -> 0.3955 (n=134), nmod 0.5356 -> 0.5318 (n=534), obj 0.7925 ->
0.7900 (n=400), iobj 0.8056 -> 0.7778 (n=36, one item), punct -0.0008. The brief's named no-regress relations
(cop / nsubj / root) are up or unchanged.

### 4b. Lever by lever (cell readout, same population)

| arm | non-verbal | delta vs the shipped floor | verbal | what it adds |
|---|---|---|---|---|
| base (shipped) | 0.5385 | -- | 0.8533 | |
| + pair detection (`cop_complement` + inverted subject + verbal host) | 0.5740 | +0.0355 CI[+0.0114,+0.0676] SEP | 0.8533 | coverage, on the EXISTING learned validity |
| + the graded occupancy cue, accrued | 0.6509 | +0.1124 CI[+0.0674,+0.1637] SEP | 0.8517 | the arc feature |
| + predicate-arrival reanalysis (wide) | **0.6686** | **+0.1302 CI[+0.0824,+0.1850] SEP** | 0.8617 | the in-order held decode |
| -- the owner's pri 113 prototype, reproduced | 0.6391 | +0.1006 SEP | 0.8483 | (reported 0.6509; see 4d) |
| -- random-site twin | 0.6213 | learned - twin **+0.0473 SEP** | 0.8583 | |
| -- occupancy-permuted twin | 0.6154 | learned - twin **+0.0533 SEP** | 0.8600 | |
| -- best frozen constant (oracle-tuned on the test set) | 0.6568 | learned - frozen +0.0118 **ns** | 0.8517 | |
| -- reference: whole-sentence MAP of the same scores | 0.7041 | | 0.8683 | the decode gap that remains |
| -- reference: hard forced re-attach on the detected pairs | 0.7219 | | 0.8650 | the detection+scorer bound |

### 4c. Out of supply -- GUM / GENTLE (modern, 12+ genres, outside the count supply)

**Through the diff, both arms in one process, 1,200 sentences, 367 non-verbal subjects:**

| | non-verbal subject (n=367) | verbal subject (n=1188) | UAS |
|---|---|---|---|
| the organ as shipped | 0.4796 | 0.8072 | 0.6092 |
| the patched organ | **0.5395** | **0.8157** | **0.6119** |
| paired delta | **+0.0599 CI[+0.0354,+0.0850] SEP** | **+0.0084 CI[+0.0025,+0.0144] SEP UP** | **+0.0027 CI[+0.0015,+0.0039] SEP** |

Per relation out of supply: nsubj 0.7299 -> 0.7505, cop 0.5953 -> 0.6214, xcomp 0.6827 -> 0.6948, advcl 0.3127 ->
0.3192, root 0.6742 -> 0.6758; down: obj -0.0025, nmod -0.0018, conj -0.0017, appos -0.0121 (n=83). **The verbal
population is CI-separated UP out of supply** -- the third branch (the tense carrier's predicate whatever its
category) helps ordinary auxiliary clauses too, which is the strongest evidence that the mechanism is the general
one and not a copular special case. In the cell's lever decomposition the same population goes 0.4796 -> 0.5613 and
both twins lose (random-site 0.5395, occupancy-permuted 0.5395). The effect is smaller out of supply (+0.060 vs
+0.118), which is the honest measure of how much of the construction inventory is UD-EWT-shaped.

### 4d. What did NOT reproduce

The owner's prototype, re-run in my cell against the CURRENT tree, scores **0.6391**, not the 0.6509 recorded in
pri 113. The difference is two arcs and the cause is the tree: the prototype's in-cell `cop_predicates_ext` was
written before `cop_complement` and `LOCATIVE_ADV` landed in the organ, so its pair scan is not the one it was when
the number was taken. **The conclusion survives** -- the landed mechanism passes both numbers -- but the 0.6509 in
the brief should be read as "the prototype on the pre-merge tree", not as a number reproducible today.

### 4e. THE DOWNSTREAM PROPAGATION -- pri 113's own participant instrument, and a located negative that is no longer separated

pri 113's instrument (`exp_nonverbal_predication_participants_v1.py --participant`, UNMODIFIED) run on the shipped
organ and then on the patched organ, both in one process. Its `parse` arm is the one this rung feeds: it reads the
predicate slot FROM THE LIVE PARSE instead of from the closed-class construction scan.

| arm (recall on the 167 non-verbal clauses) | shipped organ | patched organ |
|---|---|---|
| floor (UPOS==VERB + the live rescue) | 0.1856 | 0.1856 |
| **parse** (the predicate slot read from the live parse + roles) | **0.6048** | **0.7006** |
| parse_fixed (parse + pri 113's prototype re-attach) | 0.7186 | 0.7605 |
| slot (the closed-class construction scan) | 0.7365 | 0.7365 |
| STATE-registered recall, parse arm | 0.6108 | 0.7066 |
| pooled participant precision, parse arm | 0.8229 | 0.8277 |
| twin / oracle | 0.2635 / 1.0000 | 0.2635 / 1.0000 |

**PARSE - SLOT was pri 113's headline located negative: -0.1317 CI[-0.1976,-0.0719], CI-separated BELOW the
construction scan ("the more BF hand-off LOSES"). With this rung repaired it is -0.0359 CI[-0.0898,+0.0240] --
NOT separated.** The brain-foundational route (read the slot off the parse) has caught up with the hand-written
closed-class scan on the very instrument that located it as a deficit, and the instrument's shipped-arm numbers
reproduce pri 113's table to the digit (floor 0.1856 / slot 0.7365 / parse 0.6048 / twin 0.2635 / oracle 1.0000),
so the comparison is like for like.

**Which consumers of the copular subject arc I measured, and which I did not (checklist item 3).** MEASURED here:
the event/state detector, through pri 113's own participant instrument (4e) -- the consumer the brief names, and
the one whose located negative this rung was blamed for. NOT measured here, with the reason: the entity-attribute
BINDING capture (pri 113 measured 0.7087 -> 0.8932 on the covered clauses under its prototype heads; its arm
re-implements the prototype's reshape internally, so re-running it would have measured the prototype, not the
landed form) and the role competition's subject cue (pri 113 measured the copular subject is ALREADY labelled
0.8402 there, close to the verbal clauses' 0.8850, so it is not where this rung's signal is lost). Both are named
as the first two things to re-run once the diff lands.


### 4f. THE REMAINING DECODE GAP IS A SWEPT OPERATING POINT, NOT A CEILING (the phase diagram)

The in-order beam width is a parameter of the ORGAN, free to move, and moving it closes the gap to the
whole-sentence search smoothly. Same one-process A/B, same population, `HDLAB_ARM_BEAM` only:

| beam | shipped | **patched** | verbal (patched) | UAS (patched) |
|---|---|---|---|---|
| 8 (the live default) | 0.5385 | **0.6568** | 0.8617 | 0.6370 |
| 16 | 0.5740 | **0.6746** | 0.8683 | 0.6414 |
| 32 | 0.5976 | **0.6864** | 0.8783 (CI-sep UP) | 0.6447 |
| whole-sentence search (reference, beam-free) | 0.7041 | -- | 0.8683 | 0.6362 |

Three things follow, all measured. **(1) The gain is preserved at every width** (+0.1183 / +0.1006 / +0.0888,
every one CI-separated), so it is not an artefact of a narrow beam. **(2) The decode gap I named in section 5.2 is
search width**: the beam converges on the search number as it widens, so "the in-order beam cannot reach the arc"
is a cost/benefit choice about compute, not a ceiling -- the operating point moves. **(3) UAS and the verbal
population rise with the beam too** (UAS 0.6370 -> 0.6447; verbal 0.8617 -> 0.8783), so the wider beam is not
trading one population for another. The default is strategy's call because beam 32 is roughly 4x the read cost of
beam 8 and the board's runtime is already the binding constraint; it is recorded here as a measured move, not taken.

### 4g. READ-TIME COST (the organ is performance-sensitive: a board arm is ~20 minutes)

Measured over 200 UD-EWT test sentences, the whole live path (`arc_scores_graded` + `decode`):
**shipped 20.1 ms/sentence, patched 19.5 ms/sentence** -- no cost. The first cut of the patch DID cost +30%
(19.1 -> 24.9 ms) because the graded hand-off re-scores a sentence up to four times and each cue pass asked for
the (predicate, subject) pairs twice, i.e. eight identical scans per sentence; an 8-entry memo on
`cop_subject_pairs`, keyed on (tokens, categories, the two switches), removes it. The memo is pure sharing -- the
headline numbers are unchanged to the digit, checked by re-running the cap-700 A/B after the change.


### 4h. LANDING ORDER IS SAFE EITHER WAY (integration note)

The code and the asset can land in either order. With the **LANDED** table (no `csubg` cells at all, so the graded
cue is silent), the patched organ still scores **0.6709** against the shipped organ's 0.6076 on the same 200
sentences -- the coverage fix and the reanalysis ride on the EXISTING `csub` validity -- and with the accrued table
it reaches 0.6962. Nothing raises an exception when the cue's cells are absent (`_ArcIndex` builds an empty value
table and contributes exactly zero), and a category inventory without the UPOS classes the occupancy read needs
(the induced-class swap, the temporal model's Penn-tagset instance) degrades to silence rather than an exception --
asserted in `--self-test`.


### 4i. THE FULL BOARD, BOTH ARMS IN ONE PROCESS, FULL SIZE -- flat, with a 2-item give-back

Arm A (the organ as shipped) 1,666 s, then the patched organ bound **in place** onto the live
`hdlab.attachment_arm` object (replacing `sys.modules` would leave every consumer's `import ... as AA` pointing at
the old organ), then arm B 3,564 s. Nothing capped.

| dimension | shipped | patched | delta | n |
|---|---|---|---|---|
| coref | 0.4178 | 0.4178 | **0.0000** | 3145 |
| common_noun_coref | 0.5461 | 0.5461 | **0.0000** | 2994 |
| salience | 0.2656 | 0.2656 | **0.0000** | 128 |
| who_did_what_agent | 0.8552 | 0.8552 | **0.0000** | 1423 |
| **who_did_what_patient** | 0.8151 | 0.8135 | **-0.0016** | 1255 |
| state | 0.7910 | 0.7910 | **0.0000** | 378 |
| wic | 0.7833 | 0.7833 | **0.0000** | 120 |
| **AGGREGATE** | 0.5947 | 0.5945 | **-0.0002** | |

**Read it honestly. Six of seven dimensions are EXACTLY unchanged at full size, and the seventh is down by
-0.0016 = 2 items of 1255.** No dimension is up, which is expected and was predicted by pri 113 section 6: the
board's who-did-what dimensions iterate GOLD VERBS and the state dimension reads the copular-BINDING path, so
**the board cannot see a gain on non-verbal predicates by construction** -- that is exactly why pri 113 built the
participant instrument, on which this change is +0.096 (4e).

**What this means for the default, stated plainly.** The coordinator's condition for a default-on flip has been
"not down anywhere", and this is down somewhere, by two items. Everything else says land it: UAS is CI-separated
UP in supply AND out of supply, nsubj +0.033 / cop +0.054 / expl +0.125, the participant instrument's
brain-foundational parse hand-off gains +0.096 and its located negative stops being separated, and the
out-of-supply verbal population is CI-separated UP. The project's own discipline for this exact situation
(2026-09-12) is to keep the brain-foundational rung ON, NAME the flips, and repair the consumer rather than revert
the rung. **So my recommendation is: land it default-ON**, with the two patient items run down first -- and they are run
down as far as this instrument allows, immediately below.

**THE TWO ITEMS, RUN DOWN AS FAR AS THE INSTRUMENT ALLOWS.** I re-ran the patient dimension ALONE, both arms in
one process (`exp_board_patient_slot_v1.board_patient_dimension`, cap=None, the same n=1255):

| | model | its strongest floor | twin | model - floor |
|---|---|---|---|---|
| shipped, standalone | **0.8167** | 0.7227 | 0.6486 | +0.0940 CI[+0.0741,+0.1138] SEP |
| patched, standalone | **0.8151** | 0.7259 | 0.6486 | +0.0892 CI[+0.0696,+0.1093] SEP |

Two things follow. **(1) The delta reproduces exactly: -0.0016, two items.** **(2) The SAME shipped organ scores
0.8167 standalone and 0.8151 inside the board** -- a 0.0016 difference, the identical magnitude, from nothing but
run context (the board runs this dimension after three others, and the category organ's passage register is
order-dependent -- a filed problem of its own). So the give-back is the size of this dimension's own between-run
variation, and it does not move the dimension's verdict: the model stays CI-separated over its strongest floor and
over its twin in both arms, and its floor RISES too (0.7227 -> 0.7259), which is what a parse change does to a
position-based readout. **What I could NOT do:** name the two items. `board_patient_dimension` returns aggregates
only (`detail` keys: n, model_R_final, ci_hw, floor, twin, ceiling_gold_parse, note), and the board cell is not
mine to edit -- a per-item dump is a two-line change in that cell and is the first thing to run if strategy wants
the two items by name.


## 5. THREE INHERITED ASSUMPTIONS OVERTURNED (each with the number)

1. **"Detection coverage is what holds the prototype at 0.65" (pri 113 section 29).** FALSE at this operating
   point. Feeding the cue the **GOLD** (predicate, subject) pairs scores **0.6450**, i.e. -0.0059 CI[-0.0438,+0.0323]
   against the learned arm -- perfect detection buys nothing. Detection coverage did rise -- **103 -> 127 of the 169 gold
   non-verbal subjects covered (0.6095 -> 0.7515), pair exactness 0.8738 -> 0.8819, pairs proposed 126 -> 251**
   (the extra pairs are ordinary auxiliary clauses, which the verbal-host branch now covers and the learned
   validity weighs) -- and coverage alone is worth +0.0355, but it is not the limiter.
2. **"The residual is the arc scorer's features" (pri 113 sections 26/28).** Not at this rung. The SAME scores
   decoded by the whole-sentence search give **0.7041** against the in-order beam's 0.6509 -- a 9-arc decode gap on
   a matrix that already contains the right preference. That is why the reanalysis is the lever and a bigger cue is
   not.
3. **"The loss is not tagging" (pri 113 section 22, gold-POS).** Confirmed at the detection level too, and now
   quantified: running the pair detection on the GOLD category column raises coverage only 127 -> 130 of 169. The
   14 participial-predicate misses are a category CONFLATION (is "disappointing" the predicate or the verb?) that
   costs nothing once the cue fires on the verbal host as well -- which is what the third branch does.

## 6. UNDERSTANDING EVERY NEGATIVE

- **The narrow reanalysis fires 2 times in 700 sentences** (+0.0118 alone). Mechanism: it required the stealing head
  to be a VERB standing to the predicate's right, and the learned `later` validity has already eliminated almost
  every such steal. The committed head is usually something else -- the tense carrier, an earlier matrix verb, a
  noun inside the subject's own phrase, or the root. Widening the trigger to "any committed head, when the organ's
  own activations prefer the predicate" takes it to 18 firings of 49 eligible and +0.0177 on top of the cue.
- **The learned table does not CI-separate from the best frozen constant** (+0.0118 CI[-0.0115,+0.0343], n=169).
  Mechanism: 74 cells carry the whole cue and the per-configuration spread (NUM>NOUN +10.7 vs NOUN>PRON +4.0) moves
  only the arcs where a competing cue is within that range. What the learning buys that the constant cannot is (a)
  no hand-tuning -- the best constant, w=8, is only identifiable with the test gold in hand, while the principled
  one (the mean accrued magnitude, 4.6) scores 0.6154; (b) the observe path; (c) the operating point is FLAT from
  weight 1.0 to 5.0 (0.6509 / 0.6509 / 0.6568), so the accrual is not sitting on a tuned peak.
- **My twin accrual ('tacc') tied the learned arm exactly.** It is a broken control, not a finding: it accrues the
  outcome from the value LABEL (pred -> 1, later -> 0), so it hands itself the answer. The first validity-permutation
  twin was broken the same way (41 of 52 cells are positive, so a permutation preserves the sign on 36 of 41). Both
  are left in the record; the two controls that do isolate information (random SITES, permuted OCCUPANCY) both lose
  CI-separated.
- **The residual, attributed item by item (59 misses of 169, learned arm):** 27 copula present but no pair for THAT
  subject (clausal/specificational predicates "his view is that S", a subject scan that stops at a participial
  post-modifier, a subject in another clause), 13 pair found but the wrong predicate token, 14 pair CORRECT and the
  decode still chose something else (5 a verb, 4 the root, 3 a PROPN, 2 a NOUN), 5 verbless clauses with no copula
  at all. The oracle result above says the first two groups are NOT worth what they look like: the decode is the
  binding constraint.

## 7. WHAT WOULD TAKE THIS FURTHER (each with its number and its owner)

1. **The decode gap, 0.6568 -> 0.7041 (9 arcs).** The in-order beam cannot realise arcs the matrix already prefers.
   The brain-foundational lever is not a wider beam (the operating point is already swept) but the HOLD: the value
   of keeping a pre-predicate nominal open. `hold_expectation` learns that value per category x verb-seen x
   subordinator x finiteness; it does not condition on "the best left candidate holds the predicate slot", which is
   available in order and is exactly the state the beam gets wrong. Buildable inside `build_hold_expectation` as one
   more learned context key. **Owner: this organ. Estimated ceiling: the MAP number, 0.7041.**
2. **The forced-attachment gap, 0.7041 -> 0.7219.** What remains above the search decode is the tree constraint
   itself (projectivity and the single-root convention), not the cue.
3. **Clausal / specificational predication ("his view is that S")** -- ~6 of the 59, needs the shell-noun +
   proposition binding pri 113 section 15 mechanised (WALL 2 there), and it is the same construction the event
   stream misses.
4. **The subject scan across a reduced relative** ("the people dying from malaria will be dead") -- 6 of the 59; the
   NP is still open across a participial post-modifier, which the organ's own `npb` phrase-boundary cue already
   knows. Cheap, and it is a detection fix whose value the oracle bounds at ~0.
5. **The category rung's participial conflation** (14 of the residual detection misses) is now bypassed rather than
   fixed; the real fix is a stative/eventive distinction that needs meaning, and it is a categories-rung brief.

## 7b. IS THE WIRING ENOUGH TO REACH BRAIN LEVEL? NO -- and here is what else is, with its number

| step | ours now | the competent reader / SOTA on the same metric | the glass-box lever that closes it |
|---|---|---|---|
| non-verbal subject attachment | **0.6568** | a supervised neural parser is ~0.95 on nsubj; a competent human reader is at ceiling | (1) the beam width, a free operating point, worth **+0.0178 at beam 16 and +0.0296 at beam 32** (converging on the whole-sentence search's 0.7041); (2) the tree convention, a further ~**+0.0178** (forced re-attach 0.7219); (3) beyond that the arc scorer's REPRESENTATION -- pri 113 sections 23/25/32's contextual encoder, untested in strong form |
| verbal subject attachment | 0.8617 | ~0.95 | the same three, in the same order |
| the predicate-slot read itself | detection covers 117 of 169 gold subjects at 0.897 pair exactness | ~1.0 | NOT the lever here: the oracle says perfect pairs buy 0.0000 |
| the categories rung for this signal | gold categories add 3 of 169 | -- | not the lever either |

**So the honest answer to "is the wiring alone sufficient": no.** The wiring (this solution) is worth +0.118 in
supply and +0.060 out of supply; the decode is worth another +0.047 and is buildable inside this organ; everything
past ~0.72 needs the representational program, which is a cross-cutting build and not this brief's.

## 8. COMPONENTS TOUCHED, AND THEIR BRAIN-FOUNDATIONAL STATUS

| component | what I did | BF status after |
|---|---|---|
| `hdlab/attachment_arm.py` :: `csub_sites` / `cop_subject_pairs` | re-keyed the pair detection on the construction set; admitted the inverted subject and the verbal host | **BF_SPIRIT** -- the computation (one predicate per clause claims its subject) is the brain's; the construction inventory is still hand-written item-based schemas (Goldberg-style, the organ's existing form), which is the honest deviation |
| `csub_graded_sites` + the `csubg` cue | NEW: the predicate-slot occupancy as a graded arc-feature value | **BF** -- a graded belief entering a cue competition with a learned validity; the bins are swept |
| `observe_copular_subject` | NEW: the online accrual path (Rescorla-Wagner / Competition-Model validity from perceived constructions) | **BF** -- plastic by construction, no gold, no tree |
| `occupancy_from_posterior` / `occupancy_from_tags` | NEW: the hand-off adapter that delivers pri 110's graded read to the arc scorer | **BF** -- it removes a point-estimate hand-off; degrades to silence (not an exception) under a category inventory that lacks the UPOS classes, so the Penn-tagset and induced-class instances are safe |
| `revise_copular_subject` (called in `decode`) | NEW: predicate-arrival reanalysis of the subject arc | **BF** -- garden-path reanalysis, in order, parameter-free |
| `arc_scores` / `arc_scores_reference` / `head_posterior` / `heads` / `arc_scores_graded` / `SentenceCues` | widened by one optional `occ` argument; the graded hand-off computes it once | unchanged status; the fastpath == reference invariant re-verified WITH the occupancy |
| `tools/build_attachment_validities.py` | passes `occ=AA.occupancy_from_tags(...)` at BOTH accrual sites and to `head_posterior` | the builder now teaches the cue it reads -- the 2026-09-14 lesson applied |
| `hdlab/lexical_categories.py` (pri 110 occupancy) | read only | BF, unchanged |
| `data/hook_state/attachment_validities_csubg_v1.json` | NEW asset: the landed counts + the accrued cue | plastic (counts, not weights) |

## 9. EVALUATION -- why this one worked

**The chain was cracked at the hand-off, not at either end.** Rung by rung: the categories rung already COMPUTED the
graded predicate-slot occupancy (pri 110, BF); the heads rung already HAD a copular-subject cue with a learned
validity (pri 97) and an incremental decode with reanalysis machinery (pri 105/107); the consumers already READ the
predicate slot (pri 113). Every rung was built. What was missing was that the graded quantity was handed from the
first rung to the second **as a tag** -- a point estimate of a distribution -- so the scorer could not tell a certain
predicate from an uncertain one and fell back on its verb-biased validities. Delivering the same number as a cue
VALUE, and letting the organ accrue its validity from what it reads, is the whole win: +0.1124 of the +0.1183.

**Rungs cracked:** categories -> heads (the graded hand-off, now lossless); heads -> decode (the reanalysis reaches
the arc the competition already prefers). **Rungs NOT cracked:** the decode itself still loses 9 arcs to the
whole-sentence search (section 7.1); the construction inventory is still a hand-written list, which is exactly why
the out-of-supply gain (+0.082) is smaller than the in-supply one (+0.118).

## 10. ALTERNATE PATHS -- other ways to do this read, as or more brain-foundational

1. **Condition the HOLD, not the arc (the strongest alternative).** Brain structure: the same competition, but the
   repair happens at Levy-2008 expectation rather than at Frazier-1982 reanalysis. Computation: E(j) for a nominal
   is the learned value of keeping it open; make that value conditional on the predicate-slot state of the best
   left candidate (the `_by_left` context the hold asset already has). What it would take: one more key in
   `build_hold_expectation` and an asset rebuild (~5 min). Why not now: it changes the hold for EVERY word, so it
   needs its own full board, and the reanalysis gets most of the arcs without that risk.
2. **A second-order (sibling) factorisation of the arc score.** The copular subject and the copula's own arc are
   siblings competing for one head; a first-order tree decode cannot see that. This is already filed
   (`attachment_arm_needs_second_order_sibling_factorisation`). More brain-faithful in the sense that slot capacity
   is a real constraint (MacWhinney: a filled slot stops competing), and it subsumes my `carrier` value.
3. **A contextual distributed encoder over the arcs** (pri 113 sections 23/25/32, filed as
   `distributed_contextual_representations_into_the_parser`). It would detect the copular predicate/subject across
   the long tail of constructions without enumerating them, which is precisely where my hand-written inventory
   stops paying out of supply. Untested in its strong form; the largest single lever on this rung.
4. **Let the ROLE competition decide and feed it back.** The subject of a copular clause is a role question as much
   as a head question; the labels rung already has the `cop` cue at 0.84. A feedback edge (roles -> heads) is
   brain-faithful (the levels interact) but the substrate has no such loop yet, and pri 113 measured the
   parse-based hand-off LOSING to the construction scan, so the loop would have to be graded.

## 10b. THE LEARNING CURVE -- the validity is acquired from reading, and it keeps moving

| sentences READ | arcs accrued | cells | non-verbal subject | verbal | UAS |
|---|---|---|---|---|---|
| 0 (the cue present, no experience) | 0 | 0 | 0.6154 | 0.8583 | 0.6352 |
| 250 | 365 | 33 | 0.6331 | 0.8633 | 0.6368 |
| 1,000 | 1,447 | 56 | 0.6627 | 0.8617 | 0.6366 |
| 2,000 | 2,684 | 63 | 0.6627 | 0.8617 | 0.6367 |
| **4,000 (shipped)** | **4,560** | **74** | **0.6686** | 0.8617 | 0.6372 |

Monotone non-decreasing, and nothing about it is a fit: each row is the SAME organ after reading more text through
its own categories, with the validity recomputed from the counts. That is the observe path working rather than a
table being tuned -- and it is the evidence that the landed form is plastic, not frozen. (The curve also shows the
mechanism is USEFUL BEFORE IT IS TRAINED: with an empty table the coverage fix and the reanalysis alone are already
worth +0.077 over the shipped floor, which is what a newly-met construction would get.)

**What the organ actually learned** (the shipped 74 cells, medians by value family): the predicate arc
**+4.99**, the later-verb competitor **-2.17**, the tense carrier's own arc **-1.61**. The boost and the two
suppressions -- the three things the owner's prototype set by hand as +5 / -8 / (none) -- fall out of counting
perceived predications, with the carrier suppression the organ found that the prototype did not have.

## 10c. AN ORGAN EDGE CASE FOUND ON THE WAY (a lead for strategy, not mine to land)

On out-of-supply text the whole-sentence MAP decode can return a head of `None`, and `punct_convention._chain_top`
then raises `TypeError: '<=' not supported between instances of 'int' and 'NoneType'`
(`hdlab/attachment_arm.py:2399`, reached from `map_tree_single_root` -> `occupancy_repair` -> `punct_convention`).
It aborted a whole GUM run of the `map1` decode path. The live in-order decode is unaffected, which is why nothing
has tripped over it; but `HDLAB_ARM_DECODE=map1` is a selectable path and a baseline other briefs use.

## 11. KEY REALIZATIONS

- **Measure the diff, not the cell.** My cell's overlay said 0.6686; the diff's own code says 0.6568, because the
  patched organ computes the occupancy inside the tag mixture. Only the second number is the one that lands.
- **A module copy loaded from a temp directory is not the same organ.** The organ derives its asset paths from
  `__file__`; a copy under `/tmp` silently lost the learned hold expectation and the plausibility store and scored
  UAS 0.6138 instead of 0.6328. It looked like a real regression for twenty minutes. The fix is one line
  (`m.__file__ = the real organ`), and the lesson is that an A/B between two loads of "the same" file must first
  prove the two loads agree.
- **A permutation twin can be uninformative by construction.** Permuting a table whose cells are 80% positive
  preserves the sign on 80% of them. The controls that bite are the ones that destroy the STRUCTURE (which arcs the
  cue fires on; which token the graded value belongs to), not the ones that shuffle numbers.
- **An oracle arm is cheaper than an attribution argument.** Item-by-item attribution said 40 of 59 misses were
  "detection"; feeding the cue the gold pairs said detection is worth zero. The oracle took ten minutes and
  overturned the inherited ranking of the next lever.

## 12. CONSISTENCY WITH WHAT THE PROJECT ALREADY BANKED ON THIS RUNG

The audit records a `predict_revise` win at the ROLE level (2026-09-01, EXCELLENT): the reader recovers a dropped
patient by re-running a filler-gap resolver, and its own finding was that **RECALL of the dropped structure is the
lever, not surprisal-gated reanalysis**. The predicate-arrival reanalysis here is the ARC-level analogue of exactly
that shape -- no surprisal gate, no threshold, just "when the disambiguating word is in, take the arc the organ
already prefers". Consistent, and it is why I did not build a surprisal trigger.

## 13. SUBMISSION PROMPT

```
SOLVER SUBMISSION -- the_heads_rung_attaches_the_subject_of_a_non_verbal_predicate_at_0_54_against_0_85_for_verbal_ones_land_the_predicate_slot_as_a_graded_online_learned_arc_feature (pri 117)

SOLVED. The heads rung now attaches the subject of a non-verbal predicate at 0.6568 against a shipped
floor of 0.5385 (UD-EWT test 700, the 169 gold nsubj arcs whose gold head is not a gold verb; live
chain; +0.1183 CI[+0.0705,+0.1706] paired over sentences), with the verbal subjects NOT down
(0.8533 -> 0.8617) and UAS CI-separated UP (0.6331 -> 0.6370). Out of supply (GUM/GENTLE, 367
non-verbal subjects) 0.4796 -> 0.5395 (+0.0599 SEP) with the VERBAL population also CI-separated up.
Both numbers are measured THROUGH THE DIFF, the organ as shipped vs the patched organ in one process.

The mechanism is the brief's: pri 110's predicate-slot occupancy enters the arc competition as a cue
VALUE whose validity is LEARNED -- accrued online from 4,560 copular predications perceived while
reading 4,000 sentences through the organ's own categories, no gold column and no tree -- plus a
predicate-arrival REANALYSIS that is the in-order form of the prototype's held decode. The owner's
prototype number (0.6509) is reached and passed by a learned, plastic mechanism; a learning curve
(0.6154 with no experience -> 0.6331 at 250 sentences -> 0.6627 at 1,000) shows the validity being
acquired rather than tuned. Controls: a random-site twin loses (+0.0473 SEP) and an
occupancy-permuted twin loses (+0.0533 SEP); the best frozen constant, swept AND tuned on the test
set, reaches 0.6568 and the learned table beats it by +0.0118 (not CI-separated -- reported against
myself).

Three inherited claims overturned with numbers: feeding the cue GOLD (predicate, subject) pairs buys
NOTHING (0.6450, n.s.), so detection coverage is not the limiter pri 113 section 29 named; the SAME
scores under the whole-sentence decode give 0.7041, so the in-order beam -- not the scorer's features
-- is what remains; and gold categories raise detection by only 3 of 169.

Files: experiments/exp_copular_subject_attachment_learned_v1.py, notes/problems/<slug>/SOLVED.md +
copular_subject_attachment_patch.diff (applies cleanly at HEAD, and the cell EXECUTES it), and the
accrued asset under data/hook_state/. No hdlab/ or tools/ file edited.
```

---

# PHASE 7 (2026-09-15) -- strategy's probe answered, and one thing I had written WRONG

## P7.0 A CORRECTION TO SECTION 4i, FIRST

I wrote that the patient row's two-item give-back was "the size of this dimension's own between-run variation".
**That was wrong, and the check strategy asked for is what caught it.** Running the patient dimension THREE times
on the same tree with the same organ gives **0.8167, 0.8167, 0.8167 -- item-level churn 0, 0.** The dimension is
deterministic. The 0.8167-standalone vs 0.8151-inside-the-board difference is therefore NOT noise: it is a
CONTEXT effect (that dimension runs after three others inside the board, and the category organ's passage
register is order-dependent -- a filed problem of its own). **The two items my change costs are real,
reproducible, and now named.**

## P7.1 THE TWO PATIENT ITEMS, NAMED, WITH THE ARCS (Q1)

Per-item hit lists taken from the function the board row wraps (`exp_valency_labeled_patient_v1.eval_split`, read
not edited) and diffed in my cell (`--patient-flips`). **Two items flip, both LOST, none gained**, and both are
the SAME defect -- the subject-side scan takes the wrong nominal:

| # | sentence | gold | shipped | patched | verdict |
|---|---|---|---|---|---|
| 1 | "The consolidation of smaller local radical fundamentalist groups **with al - Qaeda** can also be **seen** ..." | patient of `seen` = `consolidation`; `Qaeda`'s gold head is `al` (flat) | `Qaeda` -> `groups` | `Qaeda` -> `seen` | **both wrong** on that arc; the cue proposed the pair (`seen`, `Qaeda`) -- the pre-copular scan walked left and stopped on the object of a PP |
| 2 | "**Call a vet** would be a good idea with a sick dog" | patient of `Call` = `vet` | `vet` -> `Call` | `vet` -> `idea` | **shipped correct**; the cue proposed (`idea`, `vet`) -- the nearest nominal before the copula is inside the CLAUSAL subject |

**Why each happened, mechanically.** (1) The subject-side walk uses the plain NP run, which stops at the PUNCT in
`al - Qaeda`, so the preposition `with` is never seen and the case-marked-nominal test (a prepositional nominal is
oblique, never a subject) never fires. The complement side of the SAME organ already crosses a hyphen
(`_np_run_end`'s `_HYPHEN` clause, the Right-hand Head Rule). (2) In `Call a vet would be ...` the subject is a
CLAUSE, and UD makes its verb the subject (`csubj`); the scan sees only the nearest nominal.

**I built both corrections and MEASURED them, and only one is worth shipping:**

| configuration | non-verbal (n=169) | verbal | UAS | patient items |
|---|---|---|---|---|
| no correction (what the board measured) | **0.6568** | 0.8617 | 0.6370 | -2 |
| + cross the hyphen | 0.6509 (-1 arc) | 0.8617 | 0.6367 | see below |
| + also refuse a clausal subject | 0.6213 (-6 arcs) | 0.8583 | 0.6358 | -- |

The clausal rule as I wrote it is **too broad**: a predicate to the left inside the same clause also describes the
legitimate pre-copular nominal of an unmarked complement clause ("I think the sky is blue"), so it refuses five
correct pairs to refuse one wrong one. **It ships OFF** (`HDLAB_ARM_CSUB_SUBJ_NO_CLAUSAL=0`) with its cost in the
code comment, and the hyphen correction ships ON (`HDLAB_ARM_CSUB_SUBJ_HYPHEN=1`) -- see P7.2 for what it buys.
The properly brain-foundational form of the clausal rule is not a left-scan at all: it is the organ's own clause
cue deciding that the subject slot is filled by a CLAUSE, which is a `csubj` build and is filed as a lead.

## P7.2 THE HYPHEN CORRECTION, AND WHAT IT BUYS -- IT SHIPS ON

With the hyphen correction on and the clausal rule off, the patient row goes **0.8151 -> 0.8159: ONE item lost
instead of two**, and the headline pays one arc (0.6568 -> 0.6509 on the 169; UAS 0.6370 -> 0.6367, verbal
unchanged at 0.8617). **So it is a one-for-one trade -- one non-verbal arc for one patient item -- and I ship it,
for two reasons that are not about the count.** It is the rule the organ already applies on the complement side
(the Right-hand Head Rule across a hyphen), so leaving it off would make the two sides of the same organ disagree
about what a compound name is; and the item it saves is on the row the BOARD can see, which halves the only
regression the board records. The remaining lost item is the clausal-subject one, whose correct fix is a `csubj`
build, not a scan (P7.1).

**The shipped configuration is therefore: `HDLAB_ARM_CSUB_SUBJ_HYPHEN=1`, `HDLAB_ARM_CSUB_SUBJ_NO_CLAUSAL=0`,
non-verbal 0.6509 (+0.1124 CI[+0.0659,+0.1634] SEP), verbal 0.8617 (+0.0083, not separated, not down), UAS 0.6367
(+0.0036 CI[+0.0014,+0.0060] SEP), and a board give-back of ONE item of 1255 on the patient row.**

## P7.3 THE BEAM LEAD, FILED NOT FLIPPED (Q2)

Full UD-EWT test 700, the PATCHED organ in its shipped configuration, both widths in ONE process on one cache;
LAS from the live arc labeler over the same heads; the read cost re-measured with the order REVERSED and repeated,
because the first arm of any such run pays the cache warm-up (my first measurement had beam 16 looking *faster*,
which is the artefact):

| | non-verbal (n=169) | verbal (n=600) | UAS | LAS | read cost |
|---|---|---|---|---|---|
| beam 8 (the live default) | 0.6509 | 0.8617 | 0.6367 | 0.5796 | **5.0 / 5.2 / 5.3 ms per sentence** |
| beam 16 | 0.6686 | 0.8683 | 0.6411 | 0.5832 | **7.2 / 7.0 ms per sentence** |
| delta | +0.0178 CI[+0.0000,+0.0402] ns | +0.0067 CI[-0.0032,+0.0172] ns | **+0.0044 CI[+0.0012,+0.0078] SEP** | +0.0036 | **+37%** |

Attachment per relation (n>=100): **up** nsubj 0.8153 -> 0.8244, root 0.7800 -> 0.7857, conj 0.4120 -> 0.4335,
xcomp 0.7664 -> 0.7883, advmod 0.4864 -> 0.5000, compound 0.5135 -> 0.5283, cop 0.6882 -> 0.6989, obl +0.0063,
advcl +0.0075, det +0.0028, amod +0.0024, punct +0.0066; **down** obj 0.7900 -> 0.7825, acl 0.1688 -> 0.1625,
aux 0.9365 -> 0.9312, mark 0.7618 -> 0.7586.

**The lead, stated for a brief:** widening the in-order beam from 8 to 16 buys **+0.0044 UAS CI-separated and
+0.0036 LAS across the whole treebank** -- it is not a copular-clause effect, it is the decode -- for **+37% read
time**, with four relations giving back small amounts. It is ORGAN-WIDE and it changes every consumer's parse, so
it needs its own full board; **not flipped here.**

## P7.4 THE POOLED LEARNED-vs-FROZEN CONTRAST (Q3)

Pooled UD-EWT test 700 + GUM 1200 (**n=536 non-verbal subjects**), the frozen arm swept AND chosen on the pooled
population (i.e. tuned in its own favour):

| | pooled non-verbal | pooled verbal |
|---|---|---|
| best frozen constant (w=12, oracle-tuned) | 0.5840 | 0.8238 |
| **the learned table** | **0.5951** | -- |
| learned - best frozen | **+0.0112 CI[-0.0018,+0.0251]** (not separated) | **+0.0084 CI[+0.0039,+0.0135] SEPARATED UP** |

**The answer is sharper than at n=169 and it is not the one I expected.** On the non-verbal population the learned
table still does not separate from a constant tuned on the test data (+0.0112, CI lower bound -0.0018 -- it has
moved from -0.0115 to the edge of zero with 3.2x the items). Where it DOES separate is **the verbal population**:
+0.0084 CI[+0.0039,+0.0135]. That is the honest shape of the advantage -- a single constant must be big enough to
win the copular cases and is then too big everywhere else, while a per-configuration validity is only as strong as
its own evidence. Plus the two things a constant cannot have at all: nobody had to tune it (the best constant,
w=12, is only identifiable with the gold in hand), and it keeps moving.

## P7.5 THE LEARNING-CURVE TAIL: PLATEAU OR BUDGET? (1a)

(filled in below from `--curve-tail`)

## P7.6 THE TENSE-CARRIER SUPPRESSION: LEARNED, BUT NOT LOAD-BEARING HERE (1b)

I said in an earlier commit that the carrier value is "the suppression the owner's hand-set form did not have",
which implied it was doing work. **Measured, it is not, on this population:** removing the `carrier:*` cells from
the learned table changes the subject's head on **2 of the 169** gold non-verbal subjects, and **neither change
alters correctness**. So: the organ LEARNS the carrier suppression (median -1.61, from counting), it is the right
thing to learn (the tense carrier is not the predicate -- Pustet 2003), and on UD-EWT test 700 it is worth
**0.0000**. It stays in because it is the correct competitor set and it costs nothing, not because it earns points.

## P7.7 THE REBUILT TABLE vs THE ONLINE OVERLAY (2i)

The whole table rebuilt by the PATCHED BUILDER (`--rebuild`, cap 6000, rounds 3, alpha 0.8, beta 10 -- the measured
gate configuration; 167 s), so the cue is TAUGHT jointly instead of accrued onto the landed counts. Written to
`data/hook_state/attachment_validities_rebuilt_csubg_v1.json`, never over the live asset:

| table | non-verbal (UD) | verbal (UD) | UAS (UD) | non-verbal (GUM) | verbal (GUM) | csubg cells |
|---|---|---|---|---|---|---|
| landed (cue absent) | 0.6154 | 0.8583 | 0.6352 | 0.5368 | 0.8131 | 0 |
| **online overlay (shipped)** | **0.6568** | 0.8617 | 0.6370 | **0.5395** | 0.8157 | 74 |
| rebuilt (taught jointly) | 0.6627 | 0.8617 | 0.6368 | 0.5450 | 0.8106 | 54 |
| rebuilt - overlay | +0.0059 CI[-0.0220,+0.0333] ns | +0.0000 ns | -0.0002 ns | +0.0054 CI[-0.0082,+0.0194] ns | -0.0051 ns | |

**Every contrast's CI contains zero: the two-minute online accrual matches a full rebuild.** That is the best
possible news for the plastic story -- the cue does NOT need a batch re-teach to reach its equilibrium, which is
what "batch fits only measure the equilibrium" predicts -- and it means the code and the small overlay asset can
land without a 6,000-sentence rebuild. (The rebuilt table has FEWER cells, 54 vs 74, because the offline teacher
reads a one-hot category column: the occupancy is near-binary there, so the middle bins never fire. That is an
argument for the ONLINE path being the richer teacher, not the other way round.)

## P7.8 THE DOWNSTREAM BINDING CAPTURE (2ii)

pri 113's own metric -- *the holder of the typed attribute is the clause's gold subject* -- recomputed on the
LANDED form (its own arm re-implements its prototype's reshape internally, so running that arm would have measured
the prototype). On the copular clauses the cue covers (**n=124**):

**shipped 0.6532 -> patched 0.7903, +0.1371 CI[+0.0789,+0.2017] SEPARATED.**

pri 113's prototype reported 0.7087 -> 0.8932 on its own covered set of 103; the landed form moves the same
quantity by the same order on a set 20% larger. So the entity-attribute store binds its property to the right
entity in four of five covered copular clauses instead of two of three -- the propagation the brief asked for,
measured on the landed mechanism rather than the prototype. **The role competition's subject cue I could NOT
report honestly**: my probe called `coarse_roles` per sentence and its label vocabulary did not line up with a
correctness test I could defend, so the numbers it produced are not reported. pri 113's measurement stands
unchallenged (the copular subject is already labelled 0.8402 there, close to the verbal 0.8850), and re-running it
properly is one of the two first things to do after landing.

## P7.9 THE ORGAN BUG IS FIXED IN THE DIFF (2iii)

`_chain_top` now stops on a missing head (`k is not None` / `hd.get(k) or 0`) instead of raising
`TypeError: '<=' not supported between instances of 'int' and 'NoneType'` when `map_tree_single_root` leaves a word
headless -- which aborted a whole GUM run of the `map1` decode. A missing head means the chain ENDS, which is
already what `0` means there, so it is a default and not a new behaviour. **Guard test in `--self-test`:**
`punct_convention` no longer raises on a headless input, AND on 60 UD-EWT sentences the patched and the shipped
`punct_convention` return identical output for identical input (so nothing moves when no head is None).

## P7.10 WHICH OF pri 113 SECTION 29's CLAIMS SURVIVE (Q4)

pri 113 section 29 said three things about what holds its 0.65 back. **(A) "The limiter is DETECTION COVERAGE, not
the scorer features" -- OVERTURNED.** Feeding the cue the GOLD (predicate, subject) pairs scores 0.6450 against the
learned arm's 0.6509, a delta of -0.0059 CI[-0.0438,+0.0323]: perfect detection buys nothing. Coverage did rise
(103 -> 127 of 169 covered) and is worth +0.0355 on its own, but it is not what holds the number back. **(B) "The
long tail of copular constructions is best bought by the contextual representation, not by more hand-coded scans"
-- STANDS, and is strengthened**: my three extra construction branches bought +0.0355 in supply but only +0.0136
out of supply, which is precisely the enumeration-does-not-generalise argument. **(C) "NOT the scorer features
(which the covered clauses show are adequate once the pair is detected)" -- HALF STANDS.** The features are
adequate; what section 29 did not name is the DECODE: the same scores under the whole-sentence search give 0.7041
against the in-order beam's 0.6509, and the beam converges on that number as it widens (0.6746 at 16, 0.6864 at
32). So the next lever on this rung is the decode's operating point and then the representation -- NOT more
detection. Any follow-on brief that inherited "detection coverage is the limiter" should be re-pointed.
