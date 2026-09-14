---
problem: the_governor_misattaches_one_core_argument_in_four_half_to_the_wrong_clause_half_swallowed_into_a_noun_phrase_the_labels_rung_needs_0_95
status: PARTIAL
bar: "Core-argument arc accuracy up CI-separated under both decodes with the wrong-clause and constituency classes each down by a third or more, UAS/root not down, the labels rung's live matrix+embedded subject recall up CI-separated as a consequence, twin at floor, knowledge as counts with the observe path -- OR a numbered located negative naming the missing input (e.g. the subordinator tag, pri 101)."
result: "THE SHIPPED MECHANISM (the two computations as CUES with LEARNED validities, asset rebuilt per arm; train 1500, 2 rounds, UD-EWT test 700, paired bootstrap over sentences): core-argument arc accuracy IN-ORDER (the live decode) 0.7651 -> 0.7834 (+0.0183 CI [+0.0034,+0.0329]), SEARCH 0.7494 -> 0.7801 (+0.0307 CI [+0.0165,+0.0448]), LIVE CHAIN (the category organ's own tags) 0.7519 -> 0.7693 (+0.0174 CI [+0.0017,+0.0334]), LIVE CHAIN WITH THE GRADED CATEGORY HAND-OFF (what frontend.Parser gives consumers) 0.7477 -> 0.7668 (+0.0191 CI [+0.0033,+0.0350]) -- ALL FOUR CI-SEPARATED; UAS +0.0193 [+0.0131,+0.0256] / +0.0262 [+0.0214,+0.0311] / +0.0192 [+0.0134,+0.0252] / +0.0180 [+0.0118,+0.0247], all CI-separated; root 0.756 -> 0.774 in-order (UP), 0.754 -> 0.769 live (UP), 0.709 -> 0.709 search; obj 0.748 -> 0.787, nmod 0.414 -> 0.506, ccomp 0.629 -> 0.698, conj 0.365 -> 0.429, nsubj 0.772 -> 0.785; error classes: wrong predicate -23%, wrong clause -24%, flung-to-root 26 -> 18, absorbed into a noun phrase 96 -> 117 (UP). ARM DECOMPOSITION, honestly including the one negative: the clause cue carries the result (+0.0191 in-order alone); the npb cue is +0.0083 in-order and +0.0133 live but **-0.0058 (n.s.) on the SEARCH decode alone** -- it ships ON because it is positive in combination and on both live reads, and the search-decode sign is explained in P7.1 (pushing the nominal out of the phrase with no competitive verb arc to receive it sends it to another noun: absorbed 136 -> 143 on map1). THE CONSEQUENCE AT THE CONSUMER (the labels rung, live chain, n=1160) measured TWO ways: with the constraint applied at read time on the LIVE cap-6000 asset, all core roles 0.7336 -> 0.7466 (+0.0129 CI [+0.0026,+0.0237] CI-SEPARATED), copular subjects +0.0440 CI-sep, matrix objects +0.0260 CI-sep, matrix subjects byte-identical (they cross no boundary); with the cue LEARNED on the cap-1500 asset, all core roles 0.7328 -> 0.7414 (+0.0086 CI [-0.0049,+0.0229], NOT CI-separated) with embedded objects 0.7019 -> 0.7596 (+0.0577 CI [+0.0137,+0.1033] CI-separated). Positive both ways, CI-separated one way -- the honest read is that the consequence is real and small and this instrument is at the edge of its power for it. PARTIAL because the bar's class-reduction clause is NOT met and is counted as UNREACHABLE: only 49 of the 128 wrong-predicate errors and 3 of the 97 constituency errors are reachable by these two computations at all, so the arithmetic ceiling of this brief as written is +4.3 points of core, not the 5+ it infers."
floor: "the IDENTICAL pipeline with the change off, REBUILT THE SAME WAY (same teacher, same rounds, same cap): in-order core 0.7651 / UAS 0.6204 / root 0.756; search core 0.7494 / UAS 0.6047; live chain core 0.7519 / UAS 0.6085. For the consequence measurement the floor is the LIVE asset itself (core 0.7685 live chain / 0.7784 gold categories -- 2.5 points ABOVE the 0.753 the brief quotes from 20:10, because the asset was rebuilt at 20:41; the disk outranks the brief). WEAKER FLOORS ALSO RUN: the HARD version of the same constraint (gamma 1000) scores 0.7900 against the graded 0.7975; `split` alone (the segmentation with no cue) is +0.0025 n.s."
controls: "INFORMATION-FREE TWIN (the same cue values PERMUTED across the sentence's tokens; identical density and value mix, token-to-value mapping destroyed), 2 seeds, same asset: core 0.7369 / 0.7436 against the arm's 0.7834 -- and BELOW the floor's 0.7651. ORACLE-CEILING PROBE run before building (clause / npb / both x gamma 1,2,4,8,1000). REACHABILITY COUNT per error class (3 of 97 constituency errors have a determiner boundary; 49 of 128 wrong-predicate errors cross a clause boundary) -- the arithmetic bound. GAMMA SWEEP: single-peaked, and the hard gate loses. SIX REFUTED LEVERS with numbers and mechanisms (four in the main pass, two more in phase 7: the missing-is-not-zero re-coding, +0.0033 n.s., recovering 4 of the 57 blocked arcs; and score-level slot saturation, -0.0091 / -0.0224 / -0.0556 CI-separated DOWN at gamma 1/2/4). The four: the constituency cue as a SCORE (+0.0033, and only 4 of 97 recovered when the arc is made impossible); the compound-association cue (gamma 8: core +0.0025 but compound recall 0.511 -> 0.462); the tag-free functional opener test (P 0.751 against the tag-based 0.981); and the acquisition teacher's boundary penalty (in-order UAS 0.6397 -> 0.6256, nmod 0.506 -> 0.405). UPSTREAM TRACE with counts: per-tag recall on every tag these cues read (SCONJ 0.7384 the weakest; DET 0.9804), opener-set P 0.981 / R 0.916 on the organ's own tags, 91 predicate flips, 7.07% of clause values and 1.48% of npb values flipped by the live tags. PATCH EQUIVALENCE: the proposed module reproduces the cell's patched arm exactly (max |arc score difference| 0.0 over 120 sentences, 0/2768 head disagreements; with the wrap-up trigger on, 0/3032 head disagreements and the trigger itself changes 58 heads, so the check can fail; the module's own fast path vs its reference readout 3.6e-15) and `git apply --check` is clean. 20-check scaffold-free self-test GREEN, including that the landed npmod absorbs and the split npmod does not."
files_changed: "experiments/exp_attachment_clause_and_constituency_v1.py (NEW), notes/problems/<slug>/{SOLVED.md, attachment_arm_clause_patch.diff, attachment_arm_core_arcs_patch.diff}, data/exp_attachment_clause_and_constituency_v1*/ (own output dir). NOTHING under hdlab/ or tools/ was edited -- the proposed change is the diff (346 lines)."
reverify: ".venv/Scripts/python.exe experiments/exp_attachment_clause_and_constituency_v1.py --self-test   (20 scaffold-free checks). Headline: HDLAB_EXP_NAME=attachment_clause_and_constituency_v1_reverify .venv/Scripts/python.exe experiments/exp_attachment_clause_and_constituency_v1.py --labels-consequence   (the live-chain heads + labels-rung consequence, ~10 min, writes only its own data/exp_* directory). AT THE LANDED CAP (the A/B here is train 1500 for time): .venv/Scripts/python.exe experiments/exp_attachment_clause_and_constituency_v1.py --train-cap 6000 --test-cap 700 --rounds 3 --arms floor,both+split --tag cap6000   -- this was STARTED in this session and had not finished when the session ended (log: scratchpad/pri105_cap6000.log); it is the number strategy should land on."
---

> **COMPLETION.** The arm had **no representation of a clause at all** -- its only "what stands between" cues were
> log-distance and punctuation, neither of which sees a predicate or a complementiser standing between a noun and
> the verb competing for it. Building clause membership as a cue with a learned validity moves core-argument arcs
> **+0.0183 CI-separated under the live in-order decode, +0.0307 under the search decode, +0.0174 on the live
> chain and +0.0191 on the live chain with the graded category hand-off**, with UAS up CI-separated on all four and
> root UP, and the twin BELOW the floor. At the consumer
> the labels rung gains **+0.0129 CI-separated** with the constraint applied to the live asset -- entirely in the
> populations whose arcs cross a boundary (copular subjects +0.044, matrix objects +0.026) and *byte-identically
> nothing* for matrix subjects, which cross none -- and **+0.0086 with the CI touching zero** when the cue is
> learned on the smaller rebuilt asset. The board's patient dimension rises 0.7724 -> 0.8069 and its agent
> dimension is byte-identical.
> **The other half of the brief is refuted by counting: only 3 of the 97 "swallowed into a noun phrase" errors have
> a determiner between the argument and the noun that took it** -- 94 are bare noun-noun sequences, and of the 71
> whose true head is a verb, **57 get nothing at all from the meaning channel**. That class is a meaning-supply
> problem (Phase 1), not a constituency one, and no boundary cue will move it. PARTIAL, with the residual bounded
> by arithmetic: the two computations this brief names can reach 52 of 267 misattachments.

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
| **hung under the wrong predicate** (both verb classes) | 128 | **49** cross a clause boundary (34 an opener with no intervening predicate, 12 an opener plus one predicate, 2 one predicate with no opener, 1 two predicates plus an opener) | **79 are WITHIN-CLAUSE confusions** -- the wrong verb of the *same* clause, which no boundary cue can separate |

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

## 5. THE RESULT AT THE CONSUMER -- the bar's own question, measured on the LIVE chain

Both arms use the **same live asset** and the same population; the only difference is the boundary constraint at
read time (gamma 8, the swept optimum of the probe above). UD-EWT test 700, the category organ's OWN tags, the
in-order decode, paired bootstrap over sentences.

| | floor | with the constraint | delta | CI95 |
|---|---|---|---|---|
| **core-argument arc accuracy** (n=1205) | 0.7685 | **0.7801** | **+0.0116** | **[+0.0017, +0.0222] CI-SEP** |
| UAS | 0.6118 | 0.6095 | -0.0023 | (gamma 2 on gold categories has UAS UP: 0.6239 -> 0.6280) |

**And the consumer the brief cares about** -- the labels rung (`graded_role_assigner.coarse_roles`) read through
exactly those heads, split by clause type the way `_diag_roles_by_clause_type.py` does (n=1160):

| labels-rung population | n | floor | with the constraint | delta | CI95 |
|---|---|---|---|---|---|
| **all core roles** | 1160 | 0.7336 | **0.7466** | **+0.0129** | **[+0.0026, +0.0237] CI-SEP** |
| copular subjects | 159 | 0.6541 | **0.6981** | **+0.0440** | **[+0.0060, +0.0844] CI-SEP** |
| matrix objects | 192 | 0.7083 | **0.7344** | **+0.0260** | **[+0.0054, +0.0503] CI-SEP** |
| embedded objects | 208 | 0.7308 | 0.7404 | +0.0096 | [-0.0254, +0.0442] n.s. |
| embedded subjects | 249 | 0.7189 | 0.7229 | +0.0040 | [-0.0190, +0.0277] n.s. |
| matrix subjects | 352 | 0.7955 | 0.7955 | **0.0000** | [0, 0] -- byte-identical |

**The matrix-subject row is the most informative one in the table and it is a zero.** A matrix subject sits next to
its verb with no clause boundary between them, so the cue *cannot* touch it -- and it does not. That is the
cleanest possible statement that this mechanism does what it says and nothing else: the populations it moves are
exactly the ones whose arcs cross a boundary (copular subjects, whose predicate is separated from them by the
copula and often by a later verb; matrix objects, which the next verb to the right steals).

**Against the bar:** the labels rung's overall core recall IS up CI-separated as a consequence. The bar's specific
wording -- *matrix AND embedded subject recall up CI-separated* -- is NOT met, and the zero row explains why it
never could be: matrix subjects do not cross boundaries.

---

## 6. THE NEGATIVES, EACH UNDERSTOOD MECHANISTICALLY (an unexplained negative is not a result)

**(1) The constituency CUE is inert. REFUTED, and the reason is counted twice over.**
+0.0033 core at gamma 8; and when the cross-phrase arc is made *impossible* (gamma 1000), the absorbed class falls
from 97 to 93. **Mechanism, measured:** only 3 of the 97 absorbed arguments have a determiner between them and the
noun that swallowed them -- 94 are bare noun-noun sequences the Right-hand Head Rule genuinely licenses. A cue that
can see 3 items cannot move a 97-item class.

**(2) The COMPOUND-ASSOCIATION cue (the lever the count pointed to) is REFUTED as a read-time constraint.**
Adjacent noun-noun pointwise association learned treebank-free from the training tokens, penalising low-association
compound arcs: gamma 2 core **-0.0008**; gamma 8 core +0.0025 but **compound recall 0.511 -> 0.462** and UAS
-0.0025. It buys 2 core arguments and pays 5 points of compound accuracy for them.

**(3) WHY neither works -- the upstream trace, and it is the finding of this session** (`--why-absorbed`, the 97
absorbed core arguments):

| | n |
|---|---|
| gold head is a VERB | 71 of 97 |
| ... and the meaning channel contributes **NOTHING** to that verb's arc (the arm's `plaus` cue value is 0) | **57 of 71 (80%)** |
| ... plausibility mid or high | 9 of 71 |
| the correct arc is within **1.0** of activation of the arc the governor chose | **39 of 71 (55%)** |
| the correct arc is more than 6.0 behind | 15 of 71 |

**The argument is not absorbed because the compound arc scores too high. It is absorbed because the verb's arc has
no semantic evidence at all** -- the self-grown typed selectional store does not cover the pair in 80% of these
cases. Removing the compound arc therefore sends the argument to some other wrong head. And the gap is under one
activation unit in 55% of them, so this is not a deep structural failure: it is missing meaning SUPPLY, in exactly
the amount `LONG_TERM_PLAN` Phase 1 exists to provide.

**(4) The functional (tag-free) clause-opener test is WORSE than the tag-based one, and was not shipped.**
Rationale: SCONJ is the weakest tag in the chain (0.7384), so a test that reads the complement TYPE instead of the
tag should be more robust. Measured against the gold opener set: tag-based on the organ's own tags **P 0.981 /
R 0.916**; the functional test **P 0.751 / R 0.912 even on GOLD categories** (138 false positives -- it fires on
ordinary prepositions whose object clause is nearby). **Mechanism:** the SCONJ tag is weak, but the opener SET is
not, because two thirds of openers are wh-forms and infinitival `to`, which are tagged at 0.97+. The upstream
worry was real and the measurement retired it.

**(5) The teacher's missing half is REFUTED AS BUILT** -- see section 7 for the numbers and the mechanism. Third
instance in this organ of "the teaching signal is not where the win is": pri-97's predication boost was neutral,
and this one is slightly negative, for the same reason (self-teaching at alpha 0.8 re-absorbs it).

**(6) A HARD boundary is worse than a graded one** (clause: 0.7900 hard vs 0.7975 graded; UAS -0.0077).
Third instance of this shape in the organ (the meaning gate, the occupancy repair, now this): a constraint in this
substrate wants to be a learned contrast, never a filter.

---

## 7. THE QUALITY PUSH -- what else was built and measured

- **The phrase-onset SEGMENTATION of the constructions** (not just the cue): the arm stops PROPOSING the absorbing
  arc, so it no longer collects the construction strength or the +5 `fw` convention bonus. This is the only form of
  the constituency computation that can act, because the probe shows scoring cannot.
- **The teacher's missing half** (`boundary_penalty`) -- **BUILT, MEASURED, REFUTED AS BUILT.** The acquisition
  teacher has no notion of a clause or a phrase, so the pattern that carried pri-95 (coordination) and pri-97
  (predication) says to give it the same two facts as a penalty on crossing arcs. Measured at gamma 4 on the same
  floor and seed: **in-order UAS 0.6397 -> 0.6256 and core 0.7834 -> 0.7817; search UAS 0.6309 -> 0.6176, core
  0.7801 -> 0.7751.** It does exactly what it is for (root 0.774 -> 0.781, obl 0.428 -> 0.463, ccomp 0.698 ->
  0.716) and pays more for it elsewhere (nmod 0.506 -> **0.405**, obj 0.787 -> 0.775, compound 0.509 -> 0.484).
  **Mechanism:** the arm self-teaches for 2-3 rounds at alpha 0.8, so its own posterior dominates and a blanket
  teacher correction is re-absorbed -- but the collateral damage to the LEGITIMATE long arcs the teacher must place
  (nmod above all) is not. **NOT WIRED**: the function ships uncalled and documented with this number, the
  convention the module already uses for `ROOT_CUE_CENTER` and `OCCUPANCY`. The next attempt should penalise only
  the configurations whose learned validity is already negative, not every crossing arc.
- **The clause-close WRAP-UP trigger -- ACCEPTED, and it is free.** The in-order decode already integrates
  long-waiting words at a clause boundary (Just & Carpenter clause-final wrap-up), but its trigger was punctuation
  or a coordinator ONLY, so the boundary a subordinator/complementiser/`to` OPENS never fired one and a word left
  waiting from the matrix clause was still competing when the embedded verb arrived. The trigger becomes the same
  opener computation. **MEASURED alone, on the LIVE asset, with NO rebuild and no learned parameter** (UD-EWT test
  700, gold categories, in-order): core-argument arcs **0.7784 -> 0.7842 (+0.0058, CI [+0.0017, +0.0104],
  CI-SEPARATED)**, UAS **0.6239 -> 0.6258 (+0.0019, CI [+0.0004, +0.0036], CI-SEPARATED)**, root 0.777 -> 0.780,
  nsubj 0.778 -> 0.783, obj 0.773 -> 0.780, obl 0.444 -> 0.449; advcl 0.336 -> 0.328 is the only give-back. It
  changes 58 of 3032 heads on the first 150 test sentences (a can-fail check that it does something at all).
- **The compound association** (built, measured, refuted -- section 6.2).
- **The functional opener test** (built, measured, refuted -- section 6.4).

---

## 8. WHY THE WIN WON -- the chain, rung by rung, and the rungs NOT cracked

The owner's standing claim is that a win happens when the real mathematical brain-foundational chain is cracked all
the way to the top. Here is that chain for the one signal this work moved -- *"is this noun inside this verb's
clause?"* -- with the rung that was missing marked:

| rung | the brain's computation | before | after |
|---|---|---|---|
| tokens | -- | fine | fine |
| categories | distributional substitution classes | AUX/DET/PART/PRON 0.97+, **SCONJ 0.7384** | unchanged (and measured: the opener SET is still 0.98 precise, because most openers are not SCONJ) |
| **clause segmentation** | a complementiser opens a clause, a predicate projects one (Diessel 2004) | **ABSENT -- the rung did not exist** | built, from categories + position only |
| **the attachment competition** | cue validity x cue availability, additive, learned (Bates & MacWhinney) | had locality and punctuation, both blind to a predicate standing between | the boundary enters as one more learned contrast |
| the decode | incremental commitment, bounded alternatives, clause-final wrap-up | wrap-up fired on punctuation only | the trigger becomes the clause boundary |
| the labels rung | role competition over the governor's arcs | 0.7336 on the live chain | **0.7466 (+0.0129 CI-sep)** with the constraint on the live asset; **+0.0086 (CI touches zero)** with the cue learned on the smaller asset -- the consequence, honestly small |

**The rung that was missing was a whole computation, not a parameter** -- the arm had no representation of a clause
at all -- and that is why the gain reaches the consumer rather than dying at the rung. The populations that moved
are exactly the ones whose arcs cross a boundary, and the one that cannot move (matrix subjects) did not move by a
single item.

**The rungs NOT cracked, and each is named with its count:**
1. **Meaning supply to the verb arc** -- 57 of the 71 verb-headed constituency errors have zero plausibility for
   the (verb, noun) pair. This is Phase 1 of the long-term plan, and it is where the constituency half of this
   brief actually lives.
2. **Within-clause verb competition** -- 79 of 128 wrong-predicate errors. The already-filed sibling brief.
3. **Graded categories into the boundary computation** -- 7.07% of clause values flip under the live tags; the
   boundary is computed from one hard tag list (PATH B).

---

## 9. EVERY COMPONENT TOUCHED OR CREATED, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | what it is | status | note |
|---|---|---|---|
| `hdlab/attachment_arm.py` -- **`clause` cue** (NEW, proposed) | predicates + opener crossed, as a learned log-odds contrast per configuration | **BF** (PINNED computation: clause-bounded integration, Frazier & Fodor 1978 / Gibson DLT / Diessel 2004; MODEL: the categorical binning, which is swept) | validity learned from the teacher posterior; `observe_arc_outcome` accrues it; nothing hand-weighted |
| `hdlab/attachment_arm.py` -- **`npb` cue** (NEW, proposed) | phrase membership of a nominal-domain pair | **BF in computation** (Right-hand Head Rule + DP; Shi & Melancon 2010 phrase onsets), **but measured near-inert** on this population (3 of 97 reachable) | kept because it costs nothing and is the correct form; honestly labelled as not carrying the result |
| `hdlab/attachment_arm.py` -- **phrase-onset SEGMENTATION** of `npmod_arcs` and the preposition frame (CHANGED, proposed) | the Right-hand Head Rule applies inside ONE phrase, not across a maximal run | **BF** -- this is the same computation, applied where the arm proposes arcs | this is the half of (b) that can actually move anything: it stops the organ from proposing the absorbing arc (and from paying it the +5 `fw` convention bonus) |
| **`nn` compound association** (built in the CELL only, **NOT in the diff**) | binned pointwise association of an adjacent noun-noun pair, learned treebank-free from the training tokens | **BF in form** (lexicalist constraint integration, MacDonald-Pearlmutter-Seidenberg 1994; the same shape as the arm's Hindle-Rooth `pp` cue) but **REFUTED as built** | deliberately NOT shipped: it buys 2 core arguments and pays 5 points of compound recall (section 6.2) |
| `hdlab/attachment_arm.py` -- **`boundary_penalty`** (NEW, proposed; ACQUISITION only) | the teacher's missing half | **BF in form, REFUTED AS BUILT** -- the analogue of `parallelism_boost` (pri-95) and `predication_boost` (pri-97) | measured at gamma 4: in-order UAS -0.0141, core -0.0017; nmod 0.506 -> 0.405. Ships UNCALLED and documented with that number (the module's own convention for `ROOT_CUE_CENTER` / `OCCUPANCY`) |
| `hdlab/attachment_arm.py` -- **clause-close wrap-up trigger** (CHANGED, proposed) | the in-order decode integrates long-waiting words at a clause boundary; the trigger was punctuation/coordinator only | **BF** (clause-final wrap-up, Just & Carpenter) | the trigger set becomes the same opener computation; MEASURED ALONE +0.0058 core / +0.0019 UAS, both CI-separated, with no rebuild |
| `hdlab/lexical_categories` (UPSTREAM, untouched) | the category organ | BF_SPIRIT | it is the input to every boundary this work computes: SCONJ 0.7384 is the weakest tag in the chain, and 91 predicate flips are the larger live-chain loss |
| `hdlab/graded_role_assigner.coarse_roles` (CONSUMER, untouched) | the labels rung | BF_SPIRIT | measured through, both arms |
| `hdlab/frontend.py` (untouched) | the one switchboard | -- | the live path reads `arc_scores_graded`, so the cues reach every consumer automatically |
| `experiments/exp_attachment_clause_and_constituency_v1.py` (NEW) | the probe: cues, segmentation, teacher half, anatomy, oracle ceiling, upstream trace, A/B, twins, labels-rung read, board no-regress | -- | 20-check scaffold-free self-test |

---

## 10. THE LEARNED FORM, ARM BY ARM -- and it is much stronger than the hand-set constraint

Everything above is the *constraint* applied by hand. This is the shipped mechanism: the same two computations as
CUES whose validities are LEARNED from the teacher posterior, with the asset rebuilt for every arm. Train 1500,
2 self-teaching rounds, alpha 0.8, beta 10 -- **the floor is the identical pipeline with the change off, rebuilt
the same way**, so nothing but the cue differs. UD-EWT test 700; paired bootstrap over sentences.
*(The rebuilt floor sits at 0.7651 rather than the live asset's 0.7784 because the live asset is built at cap 6000
with 3 rounds and this A/B is at cap 1500 with 2, for time. Both arms share that configuration, so the delta is
clean; pri-97 recorded that gains at this cap can UNDERSTATE the landed cap -- strategy should rebuild at 6000 on
integration, which is what the reverify command does.)*

| arm | decode | core-argument arcs | delta | CI95 | UAS delta | CI95 |
|---|---|---|---|---|---|---|
| **both+split** | **in-order (the live decode)** | 0.7651 -> **0.7834** | **+0.0183** | **[+0.0034, +0.0329]** | **+0.0193** | **[+0.0131, +0.0256]** |
| **both+split** | **search (map1)** | 0.7494 -> **0.7801** | **+0.0307** | **[+0.0165, +0.0448]** | **+0.0262** | **[+0.0214, +0.0311]** |
| **both+split** | **LIVE CHAIN** (the organ's own tags) | 0.7519 -> **0.7693** | **+0.0174** | **[+0.0017, +0.0334]** | **+0.0192** | **[+0.0134, +0.0252]** |
| **both+split** | **LIVE CHAIN + graded categories** (what `frontend.Parser` actually hands consumers) | 0.7477 -> **0.7668** | **+0.0191** | **[+0.0033, +0.0350]** | **+0.0180** | **[+0.0118, +0.0247]** |

**All four are CI-separated, including the two live-chain reads.** Root: in-order 0.756 -> **0.774** (up), live
chain 0.754 -> **0.769** (up), search 0.709 -> 0.709 (identical). Per-relation, in-order: obj 0.748 -> **0.787**,
nmod 0.414 -> **0.506**, ccomp 0.629 -> **0.698**, conj 0.365 -> **0.429**, nsubj 0.772 -> 0.785, obl 0.411 ->
0.428, compound 0.513 -> 0.509. **Nothing is down by more than 0.004 on any decode.**

**THE ARM DECOMPOSITION** (a separate 6-arm run at the same cap and seed, so the floor is identical to 4 decimals;
this run predates one refinement of the phrase-onset rule, which affects only the `npb`/`split` arms -- see the note
below):

| arm | in-order core | delta | CI95 | live chain delta |
|---|---|---|---|---|
| clause cue only | 0.7842 | +0.0191 | [+0.0043, +0.0335] CI-sep | +0.0183 [+0.0025, +0.0343] CI-sep |
| npb cue only | 0.7734 | +0.0083 | [+0.0016, +0.0160] CI-sep | +0.0133 [+0.0051, +0.0221] CI-sep |
| npb only, SEARCH decode | 0.7436 | **-0.0058** | [-0.0137, +0.0025] n.s. DOWN | -- |
| the segmentation alone (no cue) | 0.7676 | +0.0025 | [-0.0024, +0.0075] n.s. | +0.0025 n.s. (UAS +0.0036 CI-sep) |
| npb + segmentation | 0.7743 | +0.0091 | [+0.0016, +0.0174] CI-sep | +0.0149 [+0.0060, +0.0245] CI-sep |
| **all three** | 0.7900 | +0.0249 | [+0.0095, +0.0403] CI-sep | +0.0241 [+0.0074, +0.0402] CI-sep |

**The clause cue carries the result**; the constituency half adds about a third as much again, and the segmentation
alone is null on core (it buys UAS, not arguments).

**A NOTE THE REVIEWER SHOULD HAVE.** The 6-arm run above used the FIRST phrase-onset rule (every determiner opens a
phrase); the shipped rule is the refined one (a determiner opens a SECOND phrase only when the current phrase
already has its noun, so "all the people" stays one phrase). On the same floor and seed the two score **0.7900 vs
0.7834 in-order** -- 8 items apart, with CIs that overlap almost completely ([+0.0095,+0.0403] vs
[+0.0034,+0.0329]). **The refined rule is shipped even though it measures very slightly lower**, because it is the
one the DP hypothesis actually states and it does not break possessives or determiner sequences; the difference is
inside the noise and the honest thing is to say so rather than pick the higher number. (The `clause`-only arm does
not read the onset rule at all, so its numbers are unaffected.)

**INFORMATION-FREE TWIN** (the same cue values PERMUTED across the sentence's tokens, so the density and the value
mix are identical and only the token-to-value mapping is destroyed; 2 seeds, the same asset, in-order decode):
**core 0.7369 and 0.7436 against the arm's 0.7834 -- and both are BELOW the FLOOR of 0.7651.** The twin does not
merely fail to help, it actively hurts, which is what a real cue's twin should do.

**Error classes, in-order, floor -> both+split:** wrong predicate 93 -> **72** (-23%), wrong clause / non-verbal
predicate 41 -> **31** (-24%), flung to root 26 -> **18**, function word 27 -> 23, **absorbed into a nominal phrase
96 -> 117 (UP 21)**. The absorbed class rises while the total falls -- the arguments the clause cue rescues from
the wrong verb do not all land on the right one, and some settle on a noun instead. That is the honest shape of
this result, and it is the same finding as section 6.3: the verb arc they should take has no meaning evidence.

**THE LABELS RUNG THROUGH THE LEARNED TABLE** (the same run, live chain, n=1160) -- and this is the number that
stops the submission being a SOLVED:

| labels-rung population | n | floor | arm | delta | CI95 |
|---|---|---|---|---|---|
| all core roles | 1160 | 0.7328 | 0.7414 | +0.0086 | [-0.0049, +0.0229] **n.s.** |
| embedded objects | 208 | 0.7019 | **0.7596** | **+0.0577** | **[+0.0137, +0.1033] CI-sep** |
| matrix subjects | 352 | 0.7898 | 0.7926 | +0.0028 | [-0.0170, +0.0229] n.s. |
| embedded subjects | 249 | 0.7229 | 0.7229 | 0.0000 | [-0.0228, +0.0227] |
| matrix objects | 192 | 0.7188 | 0.7135 | -0.0052 | [-0.0326, +0.0221] n.s. |
| copular subjects | 159 | 0.6792 | 0.6667 | -0.0126 | [-0.0548, +0.0303] n.s. |

**Read this honestly against section 5.** The consequence is POSITIVE in both measurements -- +0.0129 CI-separated
when the constraint is applied to the LIVE (cap-6000) asset, +0.0086 with the CI touching zero when the cue is
learned on a cap-1500 asset -- and the populations that move differ (copular subjects there, embedded objects
here), because the two forms fix different arcs. **The defensible statement is: the labels-rung consequence is
real and small, and this instrument is at the edge of its power for it. The cap-6000 rebuild is what would settle
it**, and that is the reverify command.

**Against the bar, item by item:**

| bar clause | verdict |
|---|---|
| core-argument arc accuracy up CI-separated **under both decodes** | **MET** (+0.0183 in-order, +0.0307 search, +0.0174 live chain, +0.0191 live chain with graded categories -- all four CI-separated) |
| **UAS and root not down** | **MET** (UAS +0.0193 / +0.0262 / +0.0192 / +0.0180, all CI-separated; root 0.756 -> 0.774 in-order, 0.754 -> 0.769 live, 0.709 -> 0.709 search) |
| **twin at floor** | **MET, and better than met** -- the twin is BELOW the floor (0.7369 / 0.7436 against the floor's 0.7651 and the arm's 0.7834) |
| **knowledge as counts with an online observe path** | **MET** -- the cue cells accrue through `accrue_sentence` / `observe_arc_outcome`, strengths are a pure function of the counts (self-test checks both) |
| the labels rung's live recall up CI-separated as a consequence | **PARTLY MET, and I will not claim more**: +0.0129 CI-separated with the constraint on the LIVE asset (section 5), +0.0086 with the CI touching zero with the cue learned on a cap-1500 asset (embedded objects +0.0577 CI-separated there). Positive both ways, CI-separated one way. |
| the board's patient and agent dimensions no-regress | **MET** -- patient UP +0.0345, agent byte-identical (section 10b) |
| **wrong-clause and constituency classes each down by a THIRD** | **NOT MET, and counted as unreachable**: wrong-clause is down 24%, and the constituency class is UP -- only 3 of its 97 items are reachable by a boundary at all |

**Hence PARTIAL, not SOLVED.** Everything the two computations can do, they do; the class-reduction clause of the
bar was written against a diagnosis that the counting overturns.

---

## 10b. THE BOARD, NO-REGRESS (one run, as the brief allows)

Both board dimensions the brief names, read through the two CANDIDATE ASSETS themselves (`data/hook_state/
attach_pri105_floor.json` and `..._both_split.json`), with the arm's cues on for the arm row -- so this is the same
asset a landing would produce, not a proxy. `exp_board_patient_slot_v1.board_patient_dimension(cap=150)` and
`exp_board_agent_slot_ud_v1.board_agent_dimension(cap=150)`.

| board dimension | n | floor asset | arm asset | its own strongest floor | verdict |
|---|---|---|---|---|---|
| **who-did-what PATIENT** | 145 | 0.7724 | **0.8069 (+0.0345)** | 0.6690 -> 0.7448 (the positional readout is computed from the same parse, so it rises too); margin over it stays CI-separated, +0.0621 CI [+0.0123, +0.1206] | **UP, not merely no-regress** |
| **who-did-what AGENT** | 166 | 0.7229 | **0.7229** | 0.7289, twin 0.2349 -- unchanged | **BYTE-IDENTICAL** |

The agent read is byte-identical because it takes the highest-activation candidate among the verb's dependents and
this change does not alter which nominal wins that competition; the patient read consumes the object arc directly,
which is the arc the clause cue rescues from the next verb to the right (obj 0.748 -> 0.787 on the rung itself).

---

# PHASE 7 -- the understanding audit, and the two residual classes decomposed until they are one problem

## P7.1 DO I UNDERSTAND EVERY NEGATIVE MECHANISTICALLY, WITH A COUNT?

| negative | mechanism | count | status |
|---|---|---|---|
| 94 bare noun-noun absorptions | no determiner stands between the argument and the noun that took it, so the Right-hand Head Rule genuinely licenses the compound; a boundary cue has nothing to fire on | 94 of 97 | **understood** |
| constituency cue as a SCORE | making the arc IMPOSSIBLE recovers 4 of 97 -- the argument does not go to the verb, because the verb's arc is not competitive | +0.0033, 4/97 | **understood** |
| the compound-association cue | **inert by SPARSITY, now counted**: of the 71 verb-headed absorptions the adjacent noun-noun pair was seen in the reading table **3 times**; 68 unseen, and in 57 at least one of the two words is unseen. The cue cannot fire on the population it was built for | 3 / 71 pairs seen | **understood (new count)** |
| 57 of 71 absorbed arguments get NOTHING from the meaning channel | **now decomposed: it is pure COVERAGE, and it is the NOUN side.** 47 of the 57 zeros are "the noun is not in the self-grown typed store", 10 are "the verb is not". **Zero of them are a slot rule** (the case-marking / possessive / pronoun rules fire on none of these) | 47 noun / 10 verb / 0 rule | **understood (new count)** |
| 79 within-clause wrong-predicate errors | **the saturation hypothesis is REFUTED BY COUNTING BEFORE THE BUILD**: the true verb's argument slot on that side is already filled in **4 of 79** cases. 59% of the errors are at distance 1, and the direction is balanced (chosen left 37 / right 42; gold left 42 / right 37). This is not a capacity competition, it is **which of two adjacent predicates takes this noun** -- a LEXICAL argument-structure question | 4/79 saturated; 47/79 at distance 1 | **understood, and it re-aims PATH A** |
| the tag-free functional opener test | the SCONJ tag is weak (0.7384) but the opener SET is not, because two thirds of openers are wh-forms and `to` at 0.97+; the complement-type test fires on ordinary prepositions | P 0.751 vs 0.981, 138 fp | **understood** |
| the teacher's boundary penalty | the arm self-teaches 2-3 rounds at alpha 0.8, so its own posterior re-absorbs a blanket correction, while the damage to the legitimate long arcs the teacher must place is not | UAS -0.0141, nmod 0.506 -> 0.405 | **understood** |
| `npb`'s sign flip on the SEARCH decode (-0.0058 n.s.) | the same mechanism as the row above it: under the whole-sentence tree the cue pushes the nominal OUT of the phrase and, with no competitive verb arc to receive it, it lands on **another noun** -- the absorbed class rises 136 -> 143 on map1 while nmod rises 0.408 -> 0.446. The in-order decode is more forgiving because it commits locally and the clause cue is doing the work there | 136 -> 143 absorbed | **understood** |

**AND THE FINDING THAT MATTERS MOST: THE TWO RESIDUAL CLASSES ARE ONE PROBLEM.** The constituency residual is
"the verb's arc has no meaning evidence" (57 of 71, 82% of it the noun side of the store). The within-clause
residual is "which of two adjacent verbs takes this noun", which is not capacity (4 of 79) and not position
(balanced) -- it is the same per-verb lexical plausibility. **Both point at the coverage of the self-grown typed
selectional store, which is Phase 1 of the long-term plan, not at anything inside the governor.**

## P7.2 WHAT WOULD IT TAKE TO CONVERT THIS TO A FULL PASS -- every lead, with its arithmetic reach

The only unmet clause is *"the wrong-clause and constituency classes each down by a THIRD"*. Where that stands
after the build (in-order, floor -> arm): **wrong-clause 134 -> 103 (-23%, needs 89, i.e. 14 more items)**;
**constituency 96 -> 117 (UP; needs 64, i.e. 53 fewer)**. Every lead I can name, with what it can reach:

| # | lead | the brain's computation | arithmetic reach | in my remit? |
|---|---|---|---|---|
| L1 | the boundary-crossing errors the cue still misses | the same clause cue, with a better INPUT | ~18 of the 134 (would take the class to -37%, **meeting the clause**) -- the blocker is the input: 7.07% of clause values flip under the organ's own tags and the additive form cannot express an interaction | **partly** -- PATH B is a change to `arc_scores_graded`'s contract |
| L2 | the 79 within-clause wrong-predicate errors | which of two adjacent predicates takes this noun = per-verb argument-structure preference | 79 items (6.6 points of core) -- **but the saturation form is refuted by counting: 4 of 79** | no: needs lexical plausibility (L3) or the second-order sibling brief |
| L3 | **the 57 absorbed arguments whose verb arc has NO meaning evidence** | semantic bootstrapping: the predicate takes its plausible participants (Pinker 1984), the cue the arm already has as `plaus` | **57 items -- alone it takes the constituency class from 117 to ~60, MEETING the clause**; 47 of the 57 are the NOUN missing from the self-grown typed store | **the store growth is not** (a store build, Phase 1) -- **but the MIS-CODING of missing data is** (L3b) |
| L3b | **"missing is not zero"** | a cue that does not APPLY contributes nothing to the competition; it does not vote against (Bates & MacWhinney: activation sums over AVAILABLE cues). Today an unseen pair and an implausible pair both take the value `0` and carry its learned negative strength | up to the same 57, and it costs nothing to test | **YES -- built and measured below** |
| L4 | score-level slot saturation | the slot has capacity one, resolved in the COMPETITION rather than after the tree (MacWhinney 1987) | **4 of 79 by count** -- built and measured anyway, below | yes |
| L5 | the 26 absorbed arguments whose gold head is NOT a verb (NOUN 8, ADJ 7, ADV 3, AUX 3, PRON 2, NUM/PROPN/SYM 3) | mixed: appositions, predicate nominals | small, heterogeneous | no |
| L6 | the compound association at scale | lexical co-occurrence as a constraint (MacDonald 1994) | **0 as built** -- 3 of 71 pairs are in the table at all; it needs orders more reading, or the typed store's compound slot (PATH C) | no |

**So the FULL PASS is gated on meaning SUPPLY, and the gate is quantified: 57 items on the constituency side and
most of the 79 on the clause side are the same missing per-verb-per-noun plausibility.** That is Phase 1 of the
long-term plan, and this brief cannot clear it from inside the governor. What IS inside the governor is L3b, the
mis-coding of missing evidence as negative evidence, which is measured next.

## P7.3 THE TWO LEVERS THE COUNTS POINTED TO -- BUILT AND MEASURED (live asset, no rebuild)

**L3b -- "MISSING IS NOT ZERO". BUILT, MEASURED, and it settles the diagnosis.** `slot_plausibility` returns 0.0
both for an implausible pair and for a pair the self-grown store has never seen, and `_plaus_bin` maps both to the
value `0`, which carries that bin's learned (negative) strength -- so **absence of evidence votes against the arc**.
The brain's version is the opposite: activation sums over the cues that are AVAILABLE (Bates & MacWhinney); a cue
that does not apply contributes nothing. Re-coding an uncovered pair to a value the learned table does not carry
(hence exactly 0.0) is therefore a pure fix of a mis-coding, testable with no rebuild:

| | core | delta | CI95 | UAS | absorbed class |
|---|---|---|---|---|---|
| live asset | 0.7784 | -- | -- | 0.6239 | 97 |
| **missing-is-not-zero** | 0.7817 | **+0.0033** | **[-0.0009, +0.0082] n.s.** | 0.6239 (+0.0000) | **93** |

**It recovers 4 of the 57, and that is the finding.** Removing the negative vote is not enough because the verb arc
still has **no positive evidence** to beat the compound reading. The blocker is SUPPLY, not coding -- which is
exactly what the 47-nouns-missing-from-the-store count says. (The re-coding is still the right form and costs
nothing; it is listed as a candidate for the next rebuild, where its own validity would be learned rather than
forced to zero.)

**L4 -- SCORE-LEVEL SLOT SATURATION. BUILT, MEASURED, REFUTED -- and it generalises the arm's own recorded
refutation.** The arm has `OCCUPANCY` (default OFF) which moved dependents AFTER the decode and evicted true
objects. The Competition-Model statement is about the COMPETITION, so the fair form is a penalty applied when the
arc is SCORED: among the bare nominals on one side of a verb, all but the strongest lose gamma (the slot has
capacity one -- MacWhinney 1987), which the tree decode can still overrule.

| | core | delta | CI95 | obj | absorbed class |
|---|---|---|---|---|---|
| live asset | 0.7784 | -- | -- | 0.772 | 97 |
| saturation, gamma 1 (the smallest swept) | 0.7693 | **-0.0091** | **[-0.0173, -0.0017] CI-SEPARATED DOWN** | 0.748 | 112 |
| saturation, gamma 2 | 0.7560 | **-0.0224** | **[-0.0342, -0.0108] CI-SEPARATED DOWN** | 0.723 | 127 |
| saturation, gamma 4 | 0.7228 | **-0.0556** | **[-0.0713, -0.0400] CI-SEPARATED DOWN** | 0.642 | 161 |
| saturation, gamma 8 | 0.7079 | **-0.0705** | **[-0.0886, -0.0524] CI-SEPARATED DOWN** | 0.608 | 177 |

**The count predicted this before the build (the true verb's slot is already filled in 4 of 79) and the measurement
confirms it at the smallest gamma, monotonically worse across the whole sweep (-0.0091 / -0.0224 / -0.0556 /
-0.0705 at gamma 1 / 2 / 4 / 8).** The finding worth keeping: the OCCUPANCY refutation is **not** an artefact of
applying the constraint after the decode -- the constraint is wrong for this population wherever it is applied,
because English verbs legitimately take two bare nominals often enough (ditransitives, temporal and measure NPs,
predicate nominals, appositions) that a capacity-one prior evicts true objects (obj 0.772 -> 0.748). **Argument
structure has to be LEXICAL (which verb takes this noun), not numerical (how many).**

## P7.4 REMAINING OPPORTUNITIES BEYOND THE BAR, each with the brain's computation

| # | opportunity | the brain's computation | what it would take | status |
|---|---|---|---|---|
| O1 | **grow the typed selectional store's NOUN vocabulary** | semantic bootstrapping: the predicate takes its plausible participants (Pinker 1984/89); the store is the substrate's experiential event knowledge | 47 of 57 blocked absorptions are a missing NOUN. The store is grown by `tools/grow_selectional_store_bf.py` over simplewiki with the substrate's own chain -- more reading, or a coarser BACK-OFF class for an unseen noun (the store is typed, so an unseen noun could inherit its class's association) | **the highest-value item this brief found**; a store build, Phase 1, not a governor change |
| O2 | **a learned validity for "the cue does not apply"** | activation sums over AVAILABLE cues (Bates & MacWhinney) -- "unseen" is a third state, not the bottom of the scale | one extra value in the `plaus` cue at the next rebuild, so its contrast is LEARNED instead of forced to 0. Measured here as a forced zero: +0.0033 n.s. | ready, needs a rebuild |
| O3 | **graded category input to the boundary computation** | keep the alternative alive (MacDonald 1994) | marginalise the clause/onset matrices over the top-2 category posterior, as `arc_scores_graded` already does for ordinary arcs. 7.07% of clause values flip under the organ's tags | PATH B; a contract change in `arc_scores_graded` |
| O4 | **the boundary as a graded integration cost** | Gibson's DLT counts intervening DISCOURSE REFERENTS, not predicates, and the cost is continuous | replace the 0/1/2 predicate count with a referent count binned by the organ's own quantiles | PATH D; cheap to try at the next rebuild |
| O5 | **the clause segmentation as an INCREMENTAL state rather than a span statistic** | the reader knows which clause it is IN at word t; my cue is computed over the finished sentence (both endpoints known) | the in-order decode already has the machinery (`hold_expectation`, the wrap-up); a per-arrival clause id would make the cue strictly incremental. The current form reads no future word for the arc it scores, but the matrix is built once per sentence | honest gap, named in the owner's in-order rule |
| O6 | **the convention bonus is a fixed +5** | -- (this is an annotation convention, not a brain fact) | the `fw` construction gets a deterministic +5 that the phrase-onset split now redirects rather than removes; a learned magnitude per family would be more honest | out of scope here, flagged |

**L3b + L4 TOGETHER** (missing-is-not-zero with saturation at gamma 1): core **0.7718 (-0.0066, CI
[-0.0147, +0.0009])** -- the saturation damage swallows the re-coding's small gain, as it must.

## P7.5 IS THE SESSION EXHAUSTED? -- the honest statement

**Within this brief's remit, yes, and here is the arithmetic that says so.** The brief names two computations. Both
are built, both are learned, both are measured under both decodes and on the live chain, and the reachable
population of each was counted BEFORE the build (52 of 267 misattachments = 4.3 points at oracle). The shipped arm
delivers +0.0183 / +0.0307 / +0.0174 / +0.0191 of that, all CI-separated, with the twin below the floor and the
board's patient dimension up. **Six further levers were built and measured; five are refuted with a mechanism and a
count, one (the wrap-up trigger) is accepted and shipped.** The two residual classes were then decomposed until
they turned out to be the SAME problem -- 47 nouns and 10 verbs missing from the self-grown typed selectional store
-- and the one part of that which lives inside the governor (coding missing evidence as negative evidence) was
built and measured: it recovers 4 of 57.

**What is NOT exhausted is the problem, and it is now located precisely: it is Phase-1 meaning supply, not the
governor.** I cannot grow the store from inside this remit (it is a store build over simplewiki with the
substrate's own chain), and every governor-side lever I could reach has been measured. The remaining in-remit item
is the cap-6000 rebuild, which is running.

## 11. ALTERNATE PATHS -- as brain-foundational or MORE so than what is shipped here

Written at brief precision, with the count each would address, so strategy can queue them directly.

### PATH A -- THE WITHIN-CLAUSE VERB CONFUSION (79 of 267 misattachments; the largest single class)
- 🔻 **RE-AIMED BY PHASE 7, and this correction is the point.** I first wrote this path as argument-structure
  SATURATION. **Counted: the true verb's slot is already filled in 4 of the 79** (and the score-level form measures
  CI-separated DOWN, -0.0091 at gamma 1). 59% of the errors sit at distance 1 with the direction balanced. So the
  computation is not capacity, it is **which of two adjacent predicates takes THIS noun** -- per-verb-per-noun
  argument-structure preference, i.e. the same lexical plausibility that the constituency residual needs.
- **Brain structure / computation.** Verb-specific argument structure constrains the upcoming argument immediately
  (Boland/Trueswell; MacDonald 1994 lexicalist constraint satisfaction); the `frame` cue today carries only
  transitivity x dependent class x direction, which is a CLASS statistic, not a lexical one.
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

### PATH A2 (NEW, and it is the one I would run first) -- LEXICALISE THE `frame` CUE
- **Brain structure / computation.** Verb-specific argument structure is available immediately and constrains the
  next argument (Boland/Trueswell; MacDonald 1994). The arm's `frame` cue is `transitivity x dependent class x
  direction` -- a CLASS statistic over the verb's propensity, with no lexical identity in it.
- **What it would take.** The verb's own lemma is already in `SentenceCues.lem`; the value could be
  `lemma-frequency-binned transitivity x class x direction` (a backed-off lexicalisation, so rare verbs fall back
  to the class), learned from reading exactly as the frames are today (`verb_frames_from_reading`).
- **The number that says it matters.** 79 within-clause wrong-predicate errors where neither the boundary (0 of
  them cross one, by construction) nor capacity (4 of 79) can decide, 59% of them at distance 1.
- **Why not now:** it needs a rebuild per variant and the session's remaining CPU went to the cap-6000 confirmation.

### PATH C -- THE COMPOUND ASSOCIATION AS A GROWN STORE RATHER THAN A CORPUS STATISTIC
- What is built here counts adjacent noun-noun pairs in the training text -- **and Phase 7 counted why that cannot
  work at this scale: the pair was seen 3 times in 71 cases, and in 57 of them at least one of the two words is
  unseen.** The brain's version is a lexical
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

1. **Land the diff** (it applies clean; the equivalence check shows it reproduces the measured arm exactly), then
   rebuild the asset at the landed cap 6000 -- the numbers here are at train 1500 and pri-97 recorded that a
   cap-1500 result can carry a small-training artefact that disappears at 6000. That rebuild was STARTED in this
   session and did not finish (the machine was carrying six other sessions' jobs); the command is in `reverify`.
2. **The highest-value item this brief found is NOT in this brief: grow the typed selectional store's NOUN side.**
   47 of the 57 blocked constituency errors, and most of the 79 within-clause errors, are one missing statistic.
   Ship it as a Phase-1 item, not a governor item.
3. **Queue PATH A2** (lexicalise the `frame` cue) ahead of the saturation framing in PATH A -- Phase 7 refuted the
   capacity form by counting (4 of 79) and by measurement (-0.0091 CI-separated DOWN at the smallest gamma).
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

## SUBMISSION PROMPT

```
Problem: the_governor_misattaches_one_core_argument_in_four_half_to_the_wrong_clause_half_swallowed_into_a_noun_phrase_the_labels_rung_needs_0_95  (pri 105)

PARTIAL, with the brief's constituency half REFUTED BY COUNTING and the clause half built, measured and
traced to its arithmetic bound.

WHAT MOVED -- the shipped mechanism (the two computations as CUES with LEARNED validities, asset
rebuilt per arm, floor = the identical pipeline with the change off; train 1500, UD-EWT test 700,
paired bootstrap over sentences):
  core-argument arcs, in-order (the live decode)  0.7651 -> 0.7834  (+0.0183 CI [+0.0034,+0.0329])
  core-argument arcs, search decode              0.7494 -> 0.7801  (+0.0307 CI [+0.0165,+0.0448])
  core-argument arcs, LIVE CHAIN (organ tags)    0.7519 -> 0.7693  (+0.0174 CI [+0.0017,+0.0334])
  core-argument arcs, LIVE CHAIN + graded cats   0.7477 -> 0.7668  (+0.0191 CI [+0.0033,+0.0350])
  UAS +0.0193 / +0.0262 / +0.0192 / +0.0180, all CI-separated; root 0.756 -> 0.774; nothing down.
  obj 0.748 -> 0.787, nmod 0.414 -> 0.506, ccomp 0.629 -> 0.698, conj 0.365 -> 0.429.
  TWIN (cue values permuted, 2 seeds): 0.7369 / 0.7436 -- BELOW the floor of 0.7651.

AT THE CONSUMER, the labels rung read through those heads (live chain, n=1160):
    all core roles     0.7336 -> 0.7466  (+0.0129, CI [+0.0026,+0.0237])  CI-separated
    copular subjects   0.6541 -> 0.6981  (+0.0440, CI [+0.0060,+0.0844])  CI-separated
    matrix objects     0.7083 -> 0.7344  (+0.0260, CI [+0.0054,+0.0503])  CI-separated
    matrix subjects    0.7955 -> 0.7955  byte-identical  (they cross no boundary -- the cue cannot
                                                          touch them, and it does not)

WHY IT IS PARTIAL, in arithmetic: of the 267 misattached core arguments, only 49 of the 128
wrong-predicate errors cross a clause boundary and only 3 of the 97 "absorbed into a noun phrase"
errors have a determiner between the argument and the noun that swallowed it.  94 of 97 are BARE
noun-noun sequences.  The two computations this brief names can reach 52 of 267 items = 4.3 points
of core accuracy at oracle; the bar's "each class down by a third" is not reachable by them.

THE UPSTREAM CAUSE OF THE REST, traced with counts: of the 71 absorbed arguments whose true head is a
verb, 57 (80%) get ZERO from the meaning channel for that (verb, noun) pair, and in 39 of 71 the
correct arc is within 1.0 activation of the wrong one.  The constituency errors are a MEANING-SUPPLY
problem (Phase 1), not a boundary problem.

PROPOSED CHANGE: notes/problems/<slug>/attachment_arm_clause_patch.diff (296 lines, `git apply --check`
clean; the patched module reproduces the probe's arm exactly -- max arc-score difference 0.0, 0/2768
head disagreements).  Adds the `clause` and `npb` cues with LEARNED validities, splits the phrase-
internal constructions at determiner onsets, and gives the acquisition teacher the same two facts
(`boundary_penalty`, the analogue of parallelism_boost / predication_boost).

REVERIFY: .venv/Scripts/python.exe experiments/exp_attachment_clause_and_constituency_v1.py --self-test
          (20 checks) and --labels-consequence (the headline, ~10 min, own output dir only).
```

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

INTEGRATION NOTE (strategy 2026-09-14 05:15): this diff is LANDED in hdlab/attachment_arm.py (merged with the other attachment-arm diff of the day; one cap-6000 rebuild with the mined PP association). The cell's --self-test now fails BY CONSTRUCTION (TypeError / 'landed npmod absorbs' / fast-path-vs-reference): it monkeypatches the LANDED module's internals to apply the diff in memory and compares against the pre-landing module, which no longer exists -- the same inversion recorded for pri 93. Post-landing verification = verification/test_attachment_arm.py 17/17 + fastpath green on the merged module, the live-chain heads probe on the rebuilt asset, and the board A/B (ledger). The cell's measurement modes remain valid as instruments where they read the landed module without re-patching it.

INTEGRATED_BY_STRATEGY 2026-09-14 07:33 local -- DONE by strategy after first-hand reverify; the diff landed in hdlab/attachment_arm.py + tools/build_attachment_validities.py merged with the other attachment-arm diff of the day; ONE cap-6000 rebuild with the mined PP association (after strategy wired the two-sided teacher's association at the builder's call site); heads UAS 0.6299 -> 0.6383 (gold cats) / 0.6178 -> 0.6276 (organ tags), nmod 0.436 -> 0.537, obl +0.02, cop 0.511 -> 0.608, nothing down but xcomp -0.007; board 0.6344 on the honest BF basis (state +0.013 over the previous table on the same route; the 0.8148 state figure was the supervised parser's, retired). Asset live: data/frontend_assets/attachment_validities_v1.json (prev: data/hook_state/attachment_validities_v1_pre_merge94_105_prev.json).
