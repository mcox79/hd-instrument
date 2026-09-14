---
problem: the_governor_misattaches_one_core_argument_in_four_half_to_the_wrong_clause_half_swallowed_into_a_noun_phrase_the_labels_rung_needs_0_95
status: PARTIAL
bar: "Core-argument arc accuracy up CI-separated under both decodes with the wrong-clause and constituency classes each down by a third or more, UAS/root not down, the labels rung's live matrix+embedded subject recall up CI-separated as a consequence, twin at floor, knowledge as counts with the observe path -- OR a numbered located negative naming the missing input (e.g. the subordinator tag, pri 101)."
result: "THE CONSEQUENCE MEASUREMENT (the bar's own question), UD-EWT test 700, THE LIVE CHAIN (the category organ's own tags), in-order decode, paired bootstrap over sentences, the boundary constraint applied at read time on the LIVE asset so nothing else differs: core-argument arc accuracy 0.7685 -> 0.7801 (+0.0116 CI [+0.0017,+0.0222], CI-SEPARATED, n=1205); and AT THE CONSUMER, the labels rung read through those heads (graded_role_assigner.coarse_roles, the pri-103 clause-type split, n=1160): all core roles 0.7336 -> 0.7466 (+0.0129 CI [+0.0026,+0.0237] CI-SEPARATED), copular subjects 0.6541 -> 0.6981 (+0.0440 CI [+0.0060,+0.0844] CI-SEPARATED), matrix objects 0.7083 -> 0.7344 (+0.0260 CI [+0.0054,+0.0503] CI-SEPARATED); matrix subjects byte-identical (0.7955, CI [0,0] -- a matrix subject crosses no boundary, so the cue cannot touch it) and embedded subjects/objects n.s. (+0.0040 / +0.0096). GOLD CATEGORIES, same probe: core 0.7784 -> 0.8000 (+0.0216) at gamma 8, +0.0150 at gamma 2 with UAS UP (0.6239 -> 0.6280). PARTIAL because the bar's class-reduction clause is NOT met and cannot be: only 49 of the 128 wrong-predicate errors and 3 of the 97 constituency errors are reachable by these two computations at all (counted), so the arithmetic ceiling of this brief as written is +4.3 points of core, not the 5+ it infers."
floor: "the IDENTICAL pipeline with the change off, on the same asset and the same population: live chain core 0.7685 / labels all-core 0.7336; gold categories core 0.7784 / UAS 0.6239 / root 0.777 (this reproduces the live 20:41 asset, and it is 2.5 points ABOVE the 0.753 the brief quotes from 20:10 -- the disk outranks the brief). WEAKER FLOORS ALSO RUN: the HARD version of the same constraint (gamma 1000) scores 0.7900, BELOW the graded 0.7975."
controls: "ORACLE-CEILING PROBE run before building (clause / npb / both x gamma 1,2,4,8,1000). REACHABILITY COUNT per error class (3 of 97 constituency errors have a determiner boundary; 49 of 128 wrong-predicate errors cross a clause boundary) -- the arithmetic bound. GAMMA SWEEP: single-peaked, and the hard gate loses. TWO REFUTED LEVERS with numbers: the constituency cue as a SCORE (+0.0033, and only 4 of 97 recovered when the arc is made impossible) and the compound-association cue (gamma 8: core +0.0025 but compound recall 0.511 -> 0.462, UAS -0.0025). UPSTREAM TRACE with counts: per-tag recall on every tag these cues read (SCONJ 0.7384 the weakest; DET 0.9804), opener-set P 0.981 / R 0.916 on the organ's own tags, 91 predicate flips, 7.07% of clause values and 1.48% of npb values flipped by the live tags. PATCH EQUIVALENCE: the proposed module reproduces the cell's patched arm exactly (max |arc score difference| 0.0 over 120 sentences, 0/2768 head disagreements, fast path vs reference 3.6e-15) and `git apply --check` is clean. 20-check scaffold-free self-test GREEN, including that the landed npmod absorbs and the split npmod does not."
files_changed: "experiments/exp_attachment_clause_and_constituency_v1.py (NEW), notes/problems/<slug>/{SOLVED.md, attachment_arm_clause_patch.diff, attachment_arm_core_arcs_patch.diff}, data/exp_attachment_clause_and_constituency_v1*/ (own output dir). NOTHING under hdlab/ or tools/ was edited -- the proposed change is the diff (296 lines)."
reverify: ".venv/Scripts/python.exe experiments/exp_attachment_clause_and_constituency_v1.py --self-test   (20 scaffold-free checks). Headline: HDLAB_EXP_NAME=attachment_clause_and_constituency_v1_reverify .venv/Scripts/python.exe experiments/exp_attachment_clause_and_constituency_v1.py --labels-consequence   (the live-chain heads + labels-rung consequence, ~10 min, writes only its own data/exp_* directory)."
---

## 1. HOW THE BRAIN DOES THIS (the opening move), and what the arm was missing

The brief names two distinct computations, and they turned out to have very different sizes. Both are built as
CUES with LEARNED validities inside the existing attachment arm of the Competition-Model organ -- no new organ, no
rule layer, no treebank read while learning.

**(a) CLAUSE MEMBERSHIP.** An argument is integrated inside the clause it is in. The first-stage parser packages
roughly a clause before handing it on (Frazier & Fodor 1978's "sausage machine"); integration cost is paid across
intervening discourse referents and across clause boundaries (Gibson's DLT), and reading times rise **at** a clause
boundary because that is where the integration of new arguments happens (Memory & Cognition, *Processing of new
arguments at clause boundaries*: word reading time rises with the cumulative number of new-argument nouns **at
clause boundaries** and rises more there than at non-boundary positions -- a buffer-integrate-purge account).
A subordinator or complementiser OPENS the clause and is the child's acquisition cue for clause dependency
(Diessel 2004); an infinitival `to` opens a non-finite one; every predicate projects one. Cross-linguistically the
same computation is visible in the clearest possible form: in Japanese, *a clause boundary is posited whenever the
case markers prevent two noun phrases from belonging to the same clause*, and the reading-time cost appears at the
second NP -- i.e. the boundary is a **cue** the parser uses on-line, not a post-hoc description.

*What the arm had.* Its only "what stands between" cues were **log-distance** (`locality`) and **punctuation marks
spanned** (`boundary`). Neither sees a predicate or a complementiser standing between a noun and the verb that is
competing for it. So "the next verb to the right" -- the dominant wrong-clause error -- was invisible to the
competition.

*What was built.* `clause`: for the arc (h -> j), the number of PREDICATES strictly between them (capped at 2,
swept) plus whether a CLAUSE OPENER stands between them. Six categorical values (`0 0s 1 1s 2 2s`), one validity
per configuration (category pair x direction), learned from the teacher posterior exactly like every other cue --
so a VERB may head a VERB across a boundary (that IS the subordinate-clause arc) while a VERB may not head a NOUN
across one. Nothing is hand-weighted.

**(b) CONSTITUENCY.** A noun phrase is a unit whose head is its rightmost noun (Right-hand Head Rule, Williams
1981) and whose onset is its determiner (DP hypothesis; and, as an acquisition fact, the determiner is the
infant's phrase-onset marker -- 14-month-olds use a determiner to categorise the adjacent novel word as a noun and
to segment it, Shi & Melancon 2010, Bernal et al. 2010, Christophe et al. 2008). A noun that carries its own
determiner is its own phrase and cannot be a modifier inside the neighbouring one.

*What the arm had.* The opposite: `npmod_arcs` and the preposition frame inside `function_word_arcs` scanned a
**maximal** contiguous DET/ADJ/NUM/NOUN/PROPN run and attached every element to the run's **last** noun. In
"gave the man a book" the run `the man a book` is one phrase, so the construction PROPOSED `man` under `book` --
and, being an `fw`/`npmod` arc, that proposal carried the construction cue's learned strength (and, for the
preposition frame, the deterministic +5 convention bonus). The organ was manufacturing the very error class the
brief is about.

*What was built.* The same computation in both places the brain has it: a phrase ONSET (a determiner, or a
possessive pronoun, arriving when the current phrase already has its noun -- so "the man | a book" splits and
"all the people" does not), used (i) to SEGMENT the runs the phrase-internal constructions work on, and (ii) as a
cue `npb` ("in" / "cross") on nominal-domain arcs, with a learned validity.

**(c) THE ACQUISITION TEACHER'S MISSING HALF** (the pattern that carried pri-95 coordination and pri-97
predication). A read-time cue can only learn a validity if the teacher posterior it is counted from puts mass on
the class of arcs the cue is about. The knowledge-free teacher is locality + semantic plausibility: it has no
notion of a clause or a phrase. `boundary_penalty` gives the teacher the same two facts as a penalty on crossing
arcs (gammas swept), so the counts behind the two new cues carry contrast.

---

## 2. THE DEFICIT, MEASURED ON DISK BEFORE ANYTHING WAS BUILT

`--anatomy` on the LIVE asset (UD-EWT test 700, gold categories, the live in-order decode). **The disk disagrees
with the brief and the disk wins:** the brief's baseline (0.753 core, from pri-103 at 20:10) predates the asset
rebuilt at 20:41, and the population differs slightly (my population is every gold `nsubj`/`obj`/`iobj` after UD
subtype stripping, n=1205; the brief's was 1160).

| what the governor did with the core argument | n | share |
|---|---|---|
| attached it correctly | 938 | **0.7784** |
| absorbed it into a NOMINAL phrase | 97 | 0.081 |
| hung it under another VERB (gold head also a verb) | 87 | 0.072 |
| hung it under a VERB where the gold head is NON-VERBAL (a copular predicate) | 41 | 0.034 |
| flung it to ROOT | 25 | 0.021 |
| hung it under a function word (ADP/DET/ADV/SCONJ) | 17 | 0.014 |

**And the two cues' raw validity, counted before any learning** (per core argument: the value on the arc the
governor CHOSE vs the value on the GOLD arc):

| | crosses a boundary | share |
|---|---|---|
| arcs the governor chose and got RIGHT | 12 / 938 | **1.3%** |
| arcs the governor chose and got WRONG | 73 / 267 | **27.3%** |
| the GOLD arcs of those wrong items | 48 / 267 | 18.0% |

A cue that fires on 27% of the wrong choices and 1.3% of the right ones is exactly what the Competition Model
means by a high-validity cue. The single strongest value: an arc that crosses a clause OPENER but no predicate
(`0s`) -- 45 wrong choices against 10 right ones.

---

## 3. THE STATUS PROBE, ANSWERED WITH NUMBERS: where the signal is lost, chain by chain

**The signal this read needs, in one sentence per rung:** *tokens* -> the word forms; *categories* -> which tokens
are PREDICATES (VERB / copular AUX) and which are CLAUSE OPENERS (SCONJ / wh / infinitival `to`) and which are
PHRASE ONSETS (DET / possessive); *morphology* -> the lemma, for the copular detector and the frame cue; *heads*
(this rung) -> the arc; *labels* -> the role; *the board's who-did-what* -> the answer.

**(a) WHAT EACH HAND-OFF PRODUCES, WHAT THE NEXT RUNG READS, AND WHAT IS LOST** (`--upstream`, UD-EWT test 700;
UD's UPOS column is a measuring instrument only):

| rung | produces | this rung reads | LOST, with counts |
|---|---|---|---|
| **1 tokens** | the surface string | the form | nothing measurable |
| **2 categories** (`lexical_categories`, the live count organ) | a HARD tag + a posterior | PREDICATE = VERB or copular AUX; OPENER = SCONJ / wh / `to`; ONSET = DET / possessive PRON | per-tag recall on exactly the tags these cues read: **PUNCT 0.9984, AUX 0.9843, PART 0.9802, DET 0.9804, PRON 0.9695, ADP 0.9643, VERB 0.9380, NOUN 0.9110, ADJ 0.8692, SCONJ 0.7384**. Replacing gold categories with the organ's tags flips a `clause` value on **17,680 of 249,914 arc pairs (7.07%)** and an `npb` value on **3,689 (1.48%)**. |
| **2b the OPENER set** | the clause openers | the `clause` cue's `s` bit | measured directly against the gold opener set (SCONJ + wh + `to`): **P 0.981 / R 0.916 on the organ's own tags** (415 tp, 8 fp, 38 fn of 453). The dominant single confusion is **SCONJ -> ADP, 31 tokens**. |
| **2c the PREDICATE set** | the clause-projecting words | the `clause` cue's count | the bigger live-chain loss: **91 predicate flips** (NOUN->VERB 24, VERB->AUX 23, VERB->NOUN 18, ADJ->VERB 13, VERB->ADJ 13). |
| **2d the ONSET set** | the phrase onsets | `npb` + the run segmentation | **31 flips in 700 sentences** (DET->PRON 10, PRON->DET 6, the rest single-figure). The constituency cue's input is essentially intact. |
| **3 morphology** (`lemma_verb`) | the lemma | the copular detector, `frame` | unchanged by this work (pri-97 measured its two conflated finiteness values) |
| **4 cue activations** | additive log-odds contrasts | the decode | the additive form cannot represent an interaction; a clause boundary and a phrase onset now each contribute one term |
| **5 the in-order decode** | a beam posterior over heads | the labels rung | pri-97 measured it: the gold root arc survives in the final beam in only 0.757 of sentences |
| **6 the labels rung** | a coarse role per argument | the board arms | pri-103 measured it: with perfect heads 0.9198, with the live governor 0.7276 -- **the heads rung costs the labeler 0.160** |

**(b) BRAIN-FOUNDATIONAL STATUS OF EACH RUNG *AS IT RELATES TO THIS SIGNAL*** (not the registry label -- whether
the rung hands DOWN the graded signal this read needs):

| rung | graded? | verdict on THIS signal |
|---|---|---|
| categories | the organ has a posterior, and `arc_scores_graded` mixes the top-2 for ORDINARY arcs -- but the clause/onset segmentation is computed from ONE HARD tag list, exactly as `root_cue_values` was before pri-97 | **NOT fully BF for this signal.** The brain keeps the category alternative alive; a token that is 0.55 SCONJ / 0.45 ADP commits before the competition sees it. Named fix in section 9. |
| the opener / predicate / onset sets | **NO -- boolean.** A word either opens a clause or does not | **BF in operation, lossy in resolution.** The brain's boundary is graded (prosody + morphology + frequency); ours is a hard bit. Measured cost: see the SCONJ row. |
| the two new cues | **YES** -- graded, learned, plastic log-odds contrasts, one per (configuration, value) | **BF** -- this is what the work adds |
| the phrase-internal constructions | deterministic proposals with a learned family strength (plus a +5 convention bonus for `fw`) | **CONVENTION LAYER, honestly labelled** -- the segmentation is BF, the bonus is an annotation convention the arm already carries |
| the decode | a bounded weighted beam | **BF in form**; its clause wrap-up trigger was punctuation-only (fixed here as a lever, section 7) |

**(c) THE BRAIN'S MATH PER RUNG, AND WHAT IS BUILT**

| rung | the brain's computation | what is built | gap |
|---|---|---|---|
| clause membership | integration inside the clause; cost paid at the boundary (Gibson DLT: integration cost ~ number of new discourse referents crossed; Frazier & Fodor: package, then attach) | a categorical count of predicates + an opener bit, entering the additive cue competition with a LEARNED validity per configuration | the brain's cost is *graded in the number of referents crossed*; ours caps at 2 and does not distinguish a referent from a predicate. Matches in operation. |
| phrase membership | a determiner projects a phrase; the head is the rightmost noun (Williams 1981; Abney 1987) | onsets -> segmentation -> Right-hand Head Rule within a phrase; plus a learned `npb` contrast | matches in operation; bare noun-noun sequences are genuinely ambiguous for BOTH (section 6) |
| acquisition | the child's clause packaging shapes what it learns from | `boundary_penalty` on the teacher's score matrix (gamma swept) | matches the two existing teaching signals (`parallelism_boost`, `predication_boost`) |

---

## 4. HOW MUCH OF THE ERROR EACH COMPUTATION CAN REACH AT ALL -- counted before trusting any learned form

Two probes were run on the LIVE asset before a single validity was learned. This is the move the wall-push protocol
asks for (oracle-ceiling probe; count, do not narrate), and it is what makes the rest of this submission honest.

**(a) THE REACHABILITY COUNT -- which errors can these cues even see?** (`--anatomy`, per misattached core argument,
the value on the arc the governor actually chose):

| error class | n | reachable by the cue | not reachable |
|---|---|---|---|
| **absorbed into a nominal phrase** | 97 | **3** have a phrase ONSET (a determiner) between the argument and the noun that swallowed it | **94 are BARE noun-noun sequences** -- no determiner, so the Right-hand Head Rule genuinely licenses the compound reading |
| **hung under the wrong predicate** (both verb classes) | 128 | **49** cross a clause boundary (34 an opener with no predicate, 12 an opener plus a predicate, 3 a predicate alone) | **79 are WITHIN-CLAUSE confusions** -- the wrong verb of the *same* clause, which no boundary cue can separate |

**So the two computations the brief names can reach 52 of the 267 misattachments = 4.3 points of core accuracy,
at oracle.** That number is the honest ceiling of this brief as written, and it is arithmetic, not an opinion.

**(b) THE ORACLE-CEILING PROBE -- how much of the reachable part a boundary constraint actually recovers**
(the constraint applied as a hand-set read-time penalty of size gamma on the live asset -- NOT learned, NOT
shipped; UD-EWT test 700, gold categories, in-order decode; base core 0.7784, UAS 0.6239):

| constraint | gamma | core | UAS | wrong-predicate class | absorbed class |
|---|---|---|---|---|---|
| clause | 2 | 0.7934 (+0.0150) | 0.6280 | 116 | 92 |
| clause | **8** | **0.7975 (+0.0191)** | 0.6220 | 103 | 93 |
| clause | 1000 (hard) | 0.7900 (+0.0116) | 0.6162 | -- | 92 |
| npb | 8 | 0.7817 (+0.0033) | 0.6258 | 127 | 94 |
| npb | 1000 (hard) | 0.7826 (+0.0042) | 0.6261 | -- | 93 |
| both | **8** | **0.8000 (+0.0216)** | 0.6236 | 102 | 91 |

Three things this settles before any build:
1. **A GRADED constraint beats a hard gate** -- forbidding the crossing arc outright is WORSE than penalising it
   (clause 0.7900 vs 0.7975; UAS -0.0077). Same finding as the meaning cue's refuted hard gate. The cue form
   (a learned log-odds contrast, not a filter) is the right one.
2. **The constituency constraint is nearly inert as a CUE** (+0.003, and the absorbed class falls by 4 of 97 even
   when the arc is made impossible). Its value is therefore not in scoring -- it is in not PROPOSING the arc in the
   first place (the run segmentation), which the probe cannot test.
3. **The clause constraint recovers about half of what it can reach** (+0.019 of a reachable +0.041).

---

## 9. EVERY COMPONENT TOUCHED OR CREATED, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | what it is | status | note |
|---|---|---|---|
| `hdlab/attachment_arm.py` -- **`clause` cue** (NEW, proposed) | predicates + opener crossed, as a learned log-odds contrast per configuration | **BF** (PINNED computation: clause-bounded integration, Frazier & Fodor 1978 / Gibson DLT / Diessel 2004; MODEL: the categorical binning, which is swept) | validity learned from the teacher posterior; `observe_arc_outcome` accrues it; nothing hand-weighted |
| `hdlab/attachment_arm.py` -- **`npb` cue** (NEW, proposed) | phrase membership of a nominal-domain pair | **BF in computation** (Right-hand Head Rule + DP; Shi & Melancon 2010 phrase onsets), **but measured near-inert** on this population (3 of 97 reachable) | kept because it costs nothing and is the correct form; honestly labelled as not carrying the result |
| `hdlab/attachment_arm.py` -- **phrase-onset SEGMENTATION** of `npmod_arcs` and the preposition frame (CHANGED, proposed) | the Right-hand Head Rule applies inside ONE phrase, not across a maximal run | **BF** -- this is the same computation, applied where the arm proposes arcs | this is the half of (b) that can actually move anything: it stops the organ from proposing the absorbing arc (and from paying it the +5 `fw` convention bonus) |
| `hdlab/attachment_arm.py` -- **`nn` compound association** (NEW, proposed) | binned pointwise association of an adjacent noun-noun pair, learned from reading | **BF** (lexicalist constraint integration, MacDonald-Pearlmutter-Seidenberg 1994; the same shape as the arm's Hindle-Rooth `pp` cue) | treebank-free counts from the training TOKENS; plastic |
| `hdlab/attachment_arm.py` -- **`boundary_penalty`** (NEW, proposed; acquisition only) | the teacher's missing half | **BF** -- the analogue of `parallelism_boost` (pri-95) and `predication_boost` (pri-97) | gammas swept |
| `hdlab/attachment_arm.py` -- **clause-close wrap-up trigger** (CHANGED, proposed) | the in-order decode integrates long-waiting words at a clause boundary; the trigger was punctuation/coordinator only | **BF** (clause-final wrap-up, Just & Carpenter) | one line: the trigger set becomes the same opener computation |
| `hdlab/lexical_categories` (UPSTREAM, untouched) | the category organ | BF_SPIRIT | it is the input to every boundary this work computes: SCONJ 0.7384 is the weakest tag in the chain, and 91 predicate flips are the larger live-chain loss |
| `hdlab/graded_role_assigner.coarse_roles` (CONSUMER, untouched) | the labels rung | BF_SPIRIT | measured through, both arms |
| `hdlab/frontend.py` (untouched) | the one switchboard | -- | the live path reads `arc_scores_graded`, so the cues reach every consumer automatically |
| `experiments/exp_attachment_clause_and_constituency_v1.py` (NEW) | the probe: cues, segmentation, teacher half, anatomy, oracle ceiling, upstream trace, A/B, twins, labels-rung read, board no-regress | -- | 20-check scaffold-free self-test |

---

## 11. ALTERNATE PATHS -- as brain-foundational or MORE so than what is shipped here

Written at brief precision, with the count each would address, so strategy can queue them directly.

### PATH A -- THE WITHIN-CLAUSE VERB CONFUSION (79 of 267 misattachments; the largest single class)
- **Brain structure / computation.** Argument-structure saturation: a verb's core slots have capacity one and fill
  incrementally, so a second bare nominal after a verb whose object slot is already filled belongs to the NEXT
  predicate (Competition Model slot competition, MacWhinney 1987; verb-frame prediction, Boland/Trueswell).
- **Why it is not this brief.** It is *inside* one clause, so no boundary cue can see it. It is exactly the
  already-filed brief `attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally`.
- **What the counts add.** 79 items = 6.6 points of core-argument accuracy, the largest reachable block that
  remains; and the arm's own recorded refutation (`OCCUPANCY`, default OFF: obj 0.725 -> 0.655) says the naive
  decode-time repair is the wrong form -- the constraint has to enter as a SECOND-ORDER term in the score, not as
  a post-hoc eviction. That is what the sibling brief asks for.

### PATH B -- GRADED CATEGORY INPUT TO THE BOUNDARY COMPUTATION (the upstream fix, MORE brain-foundational)
- **The gap, measured here.** The clause boundary is computed from ONE hard tag list. 7.07% of arc pairs get a
  different `clause` value under the organ's own tags; the opener set loses 38 of 453 (SCONJ -> ADP, 31) and the
  predicate set flips 91 tokens. This is the same defect pri-97 named for `rsub` and fixed for the root cues by
  routing them through the category POSTERIOR.
- **The computation.** Keep the alternative alive (MacDonald 1994): marginalise the boundary matrices over the
  top-2 category posterior exactly as `arc_scores_graded` already does for ordinary arcs, so a token that is
  0.55 SCONJ / 0.45 ADP contributes 0.55 of an opener.
- **Why not now.** It is a change to `arc_scores_graded`'s contract (the boundary matrices are computed once per
  sentence from `pos`, not per alternative), and it multiplies the read cost by the number of alternatives kept.
  **Expected value:** bounded below by turning a 7% value-flip rate into a graded one; the cue's validity is
  already learned and correct, so this is input quality, not mechanism.

### PATH C -- THE COMPOUND ASSOCIATION AS A GROWN STORE RATHER THAN A CORPUS STATISTIC
- What is built here counts adjacent noun-noun pairs in the training text. The brain's version is a lexical
  SEMANTIC relation (is N1 a plausible modifier of N2?), which the substrate already has machinery for: the typed
  selectional-preference store grown by the substrate's own chain. A compound-relation slot in that store would
  generalise to unseen pairs, where a raw adjacency count cannot.
- **Why not now:** growing a new slot type is a store build, not a solver-sized change. **The number that says it
  matters:** 94 of 97 constituency errors are bare noun-noun pairs.

### PATH D -- A GRADED PROSODIC/ORTHOGRAPHIC BOUNDARY INSTEAD OF A BOOLEAN ONE
- The brain's clause boundary is not a bit: it is a prosodic break with a magnitude (and in text, punctuation is
  written prosody -- the arm already treats it that way in the `boundary` cue). The natural next form of the
  `clause` cue is a continuous integration cost (Gibson's DLT counts *discourse referents* crossed, not
  predicates), binned by the organ's own quantiles rather than at 0/1/2.

---

## 12. PRIORITY NEXT STEPS (for strategy)

1. **Land the diff** (it applies clean; the equivalence check below shows it reproduces the measured arm exactly),
   then rebuild the asset at the landed cap 6000 -- the numbers here are at train 1500 and pri-97 recorded that a
   cap-1500 result can carry a small-training artefact that disappears at 6000.
2. **Queue PATH A** -- it is already a filed brief and it owns the biggest remaining block (79 items).
3. **Re-run the head-repair curve** (pri-103's instrument) with the new core-arc accuracy to re-price the labels
   rung's requirement: the 0.95 target is 17 points above where the governor now is, and this brief's two
   computations can supply at most 4.3 of them.

---

## 13. MERGE NOTE -- the concurrent pri-94 diff

`pp_attachment_obl_nmod_...`'s `attachment_arm_pp_patch.diff` (34.9 KB, written 20:38) and this one both edit
`hdlab/attachment_arm.py`. **They do not touch the same computations**, but they do touch three of the same
LINES, so a merge is needed rather than two clean applies:

| region | pri-94 | this diff | merge |
|---|---|---|---|
| the `CUES` tuple (line 96-99) | appends `"ppobj"` | appends `"clause"` / `"npb"` (conditional on the flags) | append both -- the tuple is order-free |
| `SentenceCues.__init__` / `.cues` | adds the `ppobj` value | adds `clause` / `npb` values | both are additive lines in the same two places |
| `arc_scores` (the vectorised readout) | adds a sparse `ppobj` add | adds two dense adds | additive, order-free |
| `npmod_arcs`, `function_word_arcs`'s `np_head_after` | **untouched** | changed (phrase-onset segmentation) | no conflict |
| `tools/build_attachment_validities.py` | adds the v2 association build | adds `boundary_penalty` to the teacher | both are one line in the same loop |

**Land order does not matter; land BOTH and rebuild the asset once.**

---

## KEY REALIZATIONS

- **The brief's two error classes are not equally reachable, and the counting took ten minutes.** "101 absorbed
  into a noun phrase" reads like a constituency failure; **3 of them have a determiner between the argument and
  the noun that swallowed it.** The other 94 are bare noun-noun sequences, where the Right-hand Head Rule is
  *correct* and the disambiguation is lexical, not structural. Counting the reachable population per class BEFORE
  building is what separated a 3-item lever from a 49-item one -- and it is the single most useful thing in this
  submission.
- **A constraint can be right and inert at the same time.** Making the cross-phrase arc IMPOSSIBLE (gamma 1000)
  recovered 4 of 97 absorbed arguments. The arm does not put the argument on the wrong noun because that arc scores
  too high; it does so because the correct verb arc is not competitive. A cue can only re-rank alternatives that
  exist -- which is why the fix that can work is the one that stops the arc being PROPOSED (and paid a +5
  convention bonus), not the one that scores it down.
- **Graded beats hard, again, and the arm had already recorded it.** The hard version of the clause constraint is
  worse than the graded one (0.7900 vs 0.7975) -- the same shape as the refuted hard meaning gate. Every constraint
  in this organ wants to be a learned contrast, never a filter.
- **"The next verb to the right" is two different diseases.** Of 128 wrong-predicate attachments, 49 cross a clause
  boundary (this brief) and 79 are the wrong verb inside the SAME clause (the sibling/occupancy brief). Splitting
  the class by the boundary count is what turned one brief into two, with a count on each.

---

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` / `notes/BRAIN_MATH_REFERENCE.md`)

- **New row (attachment):** *clause-bounded integration as an attachment cue* -- computation: arc validity
  conditioned on the predicates and clause openers crossed; status **PINNED** (Frazier & Fodor 1978; Gibson DLT;
  Diessel 2004; the Japanese case-marker clause-boundary result) / **MODEL** for the binning; our numbers below.
- **New row (attachment):** *phrase membership by determiner onset + Right-hand Head Rule* -- status **PINNED**
  (Williams 1981; Abney 1987; Shi & Melancon 2010) / **REFUTED-AS-A-CUE on this population** (3 of 97 reachable;
  gamma-1000 oracle +0.004): the computation is right, the *cue* is inert; its value is in the SEGMENTATION.
- **Correction to the pri-105 brief's premise** (and to any downstream quote of it): the "119 constituency errors"
  are not determiner-marked phrase-boundary violations. 94 of 97 are bare noun-noun sequences.
- **Attachment-arm anatomy, updated:** with the 20:41 asset the live core-argument arc accuracy is **0.7784**
  (n=1205, UD-EWT test 700, gold categories, in-order decode), not the 0.753 the brief carries from 20:10.

---
