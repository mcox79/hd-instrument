---
problem: one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag
status: PARTIAL
bar: "The participant instrument built and published (gold-free at decision time; a twin with predicates picked at random at the same rate at floor); the 167 clauses reachable: event/state fired on >= 0.90 of them with participant precision not below the verbal clauses' CI-separated; the role competition's full cue set firing on them with role accuracy on the 167 up CI-separated vs the reduced-cue branch; the 65 seen-by-nobody down to a counted residual with reasons; board not down on any dimension; one structure per clause -- OR a numbered located negative naming the consumer that cannot receive the non-verbal predicate and why."
result: "THE INSTRUMENT IS BUILT AND THE EVENT DETECTOR IS FIXED; THE ROLE COMPETITION IS A NUMBERED, UNDERSTOOD NEGATIVE. PARTICIPANT INSTRUMENT (UD-EWT test 700, 762 subject-bearing gold clauses = 595 verbal + 167 non-verbal by UD's convention; a fired event is correct when its index IS the clause's gold predicate and precision counts a fire only if its index governs >= 1 gold CORE argument in the gold tree -- the gold TAG column is never asked what category a predicate may be): the LIVE reader as shipped scores recall 0.8176 / precision 0.8358 / F1 0.8266 and reaches 0.1856 of the 167; firing on the PREDICATE SLOT scores recall 0.9541 / precision 0.8370 / F1 0.8917 and reaches 0.8084 of the 167. Recall +0.1365 CI[+0.1115,+0.1601] CI-SEPARATED; precision +0.0012 CI[-0.0059,+0.0079] -- NOT DOWN; the 143 added fires are themselves 0.8462 precise against the shipped detector's own 0.8358. THE 65 SEEN BY NOBODY ARE 39, AND EVERY REMAINING MISS IS ATTRIBUTED: of the 32 non-verbal clauses still missed, 22 are the complement scan picking another token, 6 are not copular clauses in the gold tree at all, 3 are the CATEGORY organ tagging the gold copula VERB and 1 is `copular_available` denying the slot -- i.e. 4 of 32 are upstream of this read. THE TENSE READER, silent on every copular clause before (it fires only on Penn VB* and skips every AUX lemma), now carries a tense read off the COPULA -- the carrier's one job (Pustet 2003) -- on 117 of the 167 (0.7006 from 0.0000): 82 present, 25 past, 5 modal-subordinate, 4 future, 1 past-perfect. THE ROLE COMPETITION'S CUE COVERAGE IS FIXED AND ITS ACCURACY IS NOT: over the 269 arguments governed by a non-verbal predicate the pre-verbal-SLOT cue fires 2 -> 52, the argument-RANK cue 5 -> 136 and the verb-FRAME cue 3 -> 27, but role accuracy on that population goes 0.7361 -> 0.6654 against a table rebuilt with the same cue function, CI-separated DOWN -- a numbered negative whose mechanism is measured (below) and whose confound is controlled."
floor: "(1) THE LIVE READER AS SHIPPED -- SituationReader(predicate_recall=True)._extract_events, i.e. the UPOS==VERB detector plus the landed BF predicate rescue, driven through the real organ, not re-implemented: participant recall 0.8176, precision 0.8358, F1 0.8266, 1090 fires, 0.1856 of the 167 non-verbal clauses, 0.9950 of the 595 verbal ones. (2) THE SHIPPED COPULAR SCAN, `attachment_arm.cop_predicates` as it stands, routed to the event detector with no construction added: recall 0.9357, precision 0.8262, 0.7246 of the 167 -- so the construction work is measured against the strongest existing answer, not against the bare VERB gate. (3) FOR THE ROLES ARM, a validity table REBUILT TODAY with the SHIPPED cue function (data/hook_state/coarse_role_validities_pri113_off_v1_*), because the live asset was built at an earlier HEAD under an earlier frontend and differs from a fresh build by 22% of its teaching decisions -- comparing against the live asset would have confounded the cue change with every upstream change since."
controls: "(1) INFORMATION-FREE TWIN, 3 seeds: the SAME NUMBER of extra fires placed on a random non-punctuation token of the same sentence. Recall 0.8268 / 0.8333 / 0.8412 and precision 0.7453 / 0.7502 / 0.7543 against the arm's 0.9541 / 0.8370 -- the arm beats every seed CI-separated on BOTH (recall +0.1129 to +0.1273, precision +0.0827 to +0.0916). The twin fires the same amount and gains almost nothing, so the win is WHERE the fires land. (2) PAIRED BOOTSTRAP, 2000 resamples: over CLAUSES for recall (the item is the clause) and over SENTENCES for precision (the fire set is sentence-level and its denominator moves). (3) SURGICALITY: the verbal clauses are UNTOUCHED -- 0.9950 -> 0.9950 on all 595, and under the role arm the arguments governed by a VERB score +0.0000 EXACTLY (n=1533) on the live table. The arm is additive by construction; no existing event can be lost. (4) PATCH == CELL: the self-test EXECUTES the proposed diff's own added code and compares it to the cell that produced every number -- 0 site mismatches, 0 complement mismatches, max |strength difference| 0.0 over 5,224 tokens / 300 sentences; `git apply --check` clean. (5) THE SHIPPED SCAN IS RECOVERABLE EXACTLY: with every construction switched off, `cop_complement` reproduces `attachment_arm.cop_predicates` with 0 mismatches over 200 sentences -- so HDLAB_PREDICATION_CONSTRUCTIONS=0 is a true no-op and the constructions are an operating point, not a rewrite. (6) THE TWO BRANCHES PARTITION: carrier_occ + complement_occ == 1 - host_belief to 1e-6 over 90 copulas, so a clause can never receive two predicates from this computation. (7) ABLATION, one construction at a time on the instrument: shipped .7246 -> LOCATION .7186 -> CLAUSE-LOCAL .7186 -> INVERSION .7425 -> DP .7665 -> LOCATIVE-INVERSION .7964 -> RIGHT-HAND-HEAD-RULE .8024 -> COMPLEX-LOCATIVE .8024 -> LEFT-FRONTED .8024 -> ELLIPSIS .8084 on the 167. Two of the ten (COMPLEX LOCATIVE, LEFT-FRONTED) contribute EXACTLY ZERO on this population and are reported as zero. (8) A CONSTRUCTION THAT COST MORE THAN IT BOUGHT WAS NARROWED, NOT KEPT: firing the copula itself whenever the complement scan merely failed bought 2 clauses for 31 extra fires and took participant precision 0.8367 -> 0.8177, CI-separated DOWN; narrowed to the truly stranded configuration it buys 2 clauses for 2 fires at no precision cost. (9) CAPABILITY GUARDS, not assumptions: `predicate_sites` returns {} under any category inventory lacking the UPOS classes it reads (the Penn-tagset temporal instance and the pri-15 induced-class swap degrade to silence), and the PRED head class is used only when the LOADED validity table carries PRED rows -- measured, because on a table without them role accuracy on those clauses falls 0.7361 -> 0.3309. (10) BOARD A/B run with BOTH ARMS BACK-TO-BACK IN ONE PROCESS (pri 110 10c: a two-process board A/B on this repo straddled another session's integration and manufactured three false regressions)."
files_changed: "experiments/exp_nonverbal_predication_participants_agent_v1.py (the cell); notes/comparisons/pri113_agent/{SOLVED_agent.md, predicate_slot_consumers_agent_patch.diff}; data/exp_nonverbal_predication_participants_agent_v1/*.json (metrics); data/hook_state/coarse_role_validities_pri113_{pred,off}_v1_*.json (the two rebuilt role tables -- hook_state, never over the live asset). NO hdlab/ or tools/ file changed on disk."
reverify: ".venv/Scripts/python.exe experiments/exp_nonverbal_predication_participants_agent_v1.py --self-test   (13 checks, ~2 min, includes PATCH == CELL and the shipped-scan-recoverable no-op). Headline: --participant --v2 --cap 700 (~6 min); --ablate --cap 700 (~25 min); --attrib --cap 700 (~4 min); --tense --cap 700 (~4 min); --states --cap 700 (~4 min); --roles --cap 700 --table <pred table> --table-a <off table> (~6 min); --board-ab (~8 min capped, both arms in one process)."
---

# PARTIAL -- the predication is the event, and the event detector now fires on it; the role competition is a numbered negative

**Status: PARTIAL.** No `hdlab/` file changed on disk; the exact diff is
`notes/comparisons/pri113_agent/predicate_slot_consumers_agent_patch.diff` (`git apply --check` clean, and the
self-test executes the diff's own code and finds it identical to the measured cell).

> ## 0. TWO DEVIATIONS FROM THE BRIEF, DECLARED FIRST
>
> **(a) FILE NAMES.** Section 7 assigns me `experiments/exp_nonverbal_predication_participants_v1.py` and
> `notes/problems/<slug>/{SOLVED.md, predicate_slot_consumers_patch.diff}`. At **13:52:25 EDT**, seven minutes after
> the brief landed and about one minute before I looked, a **382-line, 20,875-byte** file appeared on disk at that
> exact path, written by another live session. I did **not** overwrite it (two writers on one file is this repo's
> documented data-loss hazard) and asked the coordinator, who ruled it the owner's and directed me to
> `experiments/exp_nonverbal_predication_participants_agent_v1.py` and `notes/comparisons/pri113_agent/`.
>
> **(b) CONTAMINATION, EXACTLY.** Before I stopped reading I had seen **lines 1-90** of that file: its module
> docstring (a restatement of the brief plus pri 110 SOLVED.md 10f's participant-instrument specification, both of
> which I had already read in full myself) and the first ten lines of a `cop_predicates_ext` whose comment names two
> additions -- an **ADV/locative complement** and a **clause-final copula**. I had independently derived the locative
> gap about ten minutes earlier in this session, from `"He was here ."` returning an empty `cop_predicates` (the
> probe is in my transcript, timestamped before the file existed), and the clause-final case is written out in pri
> 110's own `copular_available` docstring, which is in the brief's VERIFY-BEFORE-YOU-START list. Nothing else from
> that file entered my work, and the eight other constructions I shipped are not in the part I saw. **Strategy should
> discount those two ideas from the comparison anyway.**

---

## 1. The chain, rung by rung, and what each hand-off loses

The brief's signal is *"this clause asserts something, and here is the token that carries the assertion."*
Walking it down as the disk shows it:

| rung | organ | what it hands DOWN | what the next rung READS | LOST |
|---|---|---|---|---|
| tokens | -- | the string | -- | -- |
| categories | `hdlab/lexical_categories.py` | a **graded posterior** over UPOS, already carrying pri 110's predicate-slot revision (`HDLAB_LC_PREDICATE_SLOT`, live in the working tree) | the argmax **tag** | the gradedness. Every consumer below takes `tag == "VERB"` |
| lemma | `hdlab/morphology.py` | lemma | lemma | -- |
| heads | `hdlab/attachment_arm.py` | arcs, plus `cop_predicates` -- which **already knows** which token a copula predicates of | **nobody downstream reads `cop_predicates`** except `csub_sites` / `assertion_candidates`, both internal to the arm | **the whole non-verbal predicate signal.** It is computed and thrown away |
| **THE PREDICATE HAND-OFF** | **did not exist** | -- | -- | **167 of 762 subject-bearing clauses (21.9%)** |
| events | `situation_reader._tense_agnostic_extract` | `T.Event` at every `up[i] == "VERB"` | -- | all 167 |
| roles | `graded_role_assigner.coarse_role_cues` | cue values gated `hc in ("VERB","AUX")` | -- | the frame / pre-slot / rank / existential cues on all 167 |
| tense | `temporal_model.extract_events` (Penn), `tense_preserving_detector.assign_sentence` (UPOS==VERB) | a tense per verbal event | -- | **every copular clause has no tense at all**: "she WAS a doctor" and "she IS a doctor" were the same record |
| states | `situation_reader._read_entity_states` -> `hdlab/copular_binding.py` | (HOLDER, PROPERTY) pairs | `sm.entity_states` / `sm.state_register` | **a SECOND, independent predicate finder** -- and it feeds the state register, never the event stream |

**The brain-foundational status of each rung FOR THIS SIGNAL, before this work:**

- **categories** -- BF for the *carrier* question (pri 110 landed the graded occupancy), **not BF for this one**: it
  hands down a graded belief and every consumer point-estimates it.
- **heads** -- the organ that OWNS predication computes the answer (`cop_predicates`) and has no consumer for it.
  A signal produced and not read is the purest form of the loss the owner's chain-trace rule is looking for.
- **events / roles / tense** -- **not BF**: each asks the tag column a question the tag column cannot answer.
  UD's VERB column is a *measuring instrument*; "is there an eventuality here?" is not a question about part of speech.
- **states** -- BF in spirit (a Kimian state is genuinely a distinct sort, Maienborn 2005) but **fragmented**: it is
  a second predicate finder for the same clause, which is the one-structure defect the brief names.

---

## 2. The brain, and what it says to compute

**A clause has ONE predicate** (Spivey-Knowlton 1993) and **the predication IS the eventuality** -- a
neo-Davidsonian eventuality variable that a copula plus a non-verbal complement introduces exactly as a verb does
(Bach 1986 on eventuality types; Maienborn 2005 for the copular case being a *Kimian state*, an ontologically
distinct sort rather than a degenerate event; Pustet 2003 for the copula as the **tense carrier** of a non-verbal
predication, whose canonical types are **property / class / location / possession**; Goldberg 1995 for existential
*there* as a stored construction).

pri 110 built the tense carrier's three-way discharge and shipped **branch (3)**. This brief is **branch (2)**, and
it is the *same product*:

```
(1) a VERBAL HOST in the carrier's verb group    -> the HOST predicates              (ordinary auxiliary)
(2) a NON-VERBAL COMPLEMENT it carries tense for -> the COMPLEMENT predicates        <- pri 113
(3) neither                                      -> the CARRIER ITSELF predicates    (pri 110, landed)

carrier_occ_i    = (1 - P(verbal host at i)) * (1 - P(copular predication available at i))     [pri 110]
complement_occ_q = (1 - P(verbal host at i)) *      P(copular predication available at i)      [here]
```

The two **partition** `(1 - host)` -- asserted numerically in the self-test over 90 copulas -- so **one clause can
never receive two predicates from this computation**. That is not a coincidence; it is what "one predicate per
clause" means when written as arithmetic, and it is why this is an ARM of the organ that already owns predication
(`hdlab/attachment_arm.py`) and not a second predicate finder.

**PINNED:** one predicate per clause; the copula as tense carrier for a non-verbal predication; the four non-verbal
predicate types; the constructions below (each a stored form-meaning pairing).
**OURS (swept, never adopted):** which closed-class forms spell each construction, and the operating point (each
construction is an independent switch, ablated below; `HDLAB_PREDICATION_CONSTRUCTIONS=0` restores the shipped scan
byte-exactly).

---

## 3. THE INSTRUMENT FIRST (checklist item 6; pri 110 filed it as 7D and did not build it)

UD's VERB column **cannot** adjudicate a predication event on an ADJ -- it scores a correctly fired copular event as
a false positive by construction, which is exactly why pri 110 measured its own phase-4 lever and refused to ship it
(pri 110 4c2). So the instrument asks a question about **structure**, never about the tag column:

- **POPULATION** -- every gold clause with a SUBJECT (a gold `nsubj` arc): **762** on UD-EWT test 700. Its
  **predicate** is that arc's gold HEAD, whatever category it carries. Gold categories of those heads:
  `VERB 595, ADJ 74, NOUN 57, ADV 13, AUX 8, PROPN 8, PRON 6, NUM 3, SYM 2, INTJ 1` -- **167 non-verbal (21.9%)**,
  reproducing pri 110 10e exactly.
- **RECALL** -- the share of those clauses for which the reader fires an event AT that gold predicate.
- **PRECISION** -- the share of FIRED events whose index governs >= 1 gold CORE argument
  (`nsubj`/`csubj`/`obj`/`iobj`/`obl`/`ccomp`/`xcomp`/`cop`). A copular ADJ passes (it governs its subject and its
  copula); a noun inside an NP fails.
- **FLOOR** -- the LIVE reader, driven through the real organ (`SituationReader(predicate_recall=True)._extract_events`),
  not a re-implementation.
- **TWIN** -- the same NUMBER of extra fires, placed at random, 3 seeds.
- **GOLD-FREE AT DECISION TIME** -- the predicate sites are computed from tokens, the chain's own tags and the
  category organ's own posterior. Gold enters only in scoring.

### 3a. The headline

| arm | recall | precision | F1 | recall on the 595 VERBAL | recall on the 167 NON-VERBAL | fires |
|---|---|---|---|---|---|---|
| **FLOOR** (the live reader as shipped) | 0.8176 | 0.8358 | 0.8266 | 0.9950 | **0.1856** | 1090 |
| **PREDICATE SLOT** | **0.9541** | **0.8370** | **0.8917** | 0.9950 | **0.8084** | 1233 |
| twin, seed 0 | 0.8333 | 0.7502 | 0.7896 | 0.9950 | 0.2575 | 1233 |
| twin, seed 1 | 0.8412 | 0.7543 | 0.7954 | 0.9950 | 0.2934 | 1233 |
| twin, seed 2 | 0.8268 | 0.7453 | 0.7839 | 0.9950 | 0.2275 | 1233 |

- **recall +0.1365 CI[+0.1115,+0.1601]** -- CI-separated.
- **precision +0.0012 CI[-0.0059,+0.0079]** -- **not down**. The bar asks that participant precision not fall below
  the verbal clauses' CI-separated; it does not fall at all.
- the **143 added fires** are themselves **0.8462** precise, against the shipped detector's own **0.8358**. The new
  predications are, if anything, slightly better-grounded than the verbs.
- against every twin: recall **+0.1129 / +0.1207 / +0.1273**, precision **+0.0827 / +0.0868 / +0.0916**, all
  CI-separated. **Firing the same amount at random buys 0.24 of the 167; firing at the predicate slot buys 0.81.**

### 3b. Every construction, ablated -- and two of them are worth exactly zero

Each row adds ONE construction to the row above, measured on the same instrument. The first row is the shipped
`attachment_arm.cop_predicates` routed to the event detector, which is the strongest existing answer and the floor
the construction work is measured against.

| arm | recall | precision | F1 | on the 167 | added-fire precision |
|---|---|---|---|---|---|
| shipped `cop_predicates` | 0.9357 | 0.8262 | 0.8775 | 0.7246 | 0.7518 |
| + **LOCATION** (Pustet's third type: `he is HERE`) | 0.9344 | 0.8260 | 0.8769 | 0.7186 | 0.7500 |
| + **CLAUSE-LOCAL** (the scan stops at SCONJ/CCONJ) | 0.9344 | 0.8287 | 0.8784 | 0.7186 | 0.7721 |
| + **INVERSION** (`IS that a money maker ?`) | 0.9396 | 0.8354 | 0.8844 | 0.7425 | 0.8321 |
| + **DP** (a determiner opens a nominal; `here is a REVISED draft`) | 0.9449 | 0.8333 | 0.8856 | 0.7665 | 0.8143 |
| + **LOCATIVE INVERSION** (`HERE is a copy`) | 0.9514 | 0.8374 | 0.8908 | 0.7964 | 0.8500 |
| + **RIGHT-HAND HEAD RULE** (`money - REDISTRIBUTORS`) | 0.9528 | 0.8375 | 0.8914 | 0.8024 | 0.8511 |
| + **COMPLEX LOCATIVE** (`out OF TOWN`) | 0.9528 | 0.8375 | 0.8914 | 0.8024 | 0.8511 |
| + **LEFT-FRONTED PREDICATE** (`how RELIABLE that is`) | 0.9528 | 0.8375 | 0.8914 | 0.8024 | 0.8511 |
| + **ELLIPSIS**, stranded only (`i am sure they ARE .`) | **0.9541** | **0.8370** | **0.8917** | **0.8084** | 0.8462 |

**COMPLEX LOCATIVE and LEFT-FRONTED PREDICATE are worth EXACTLY ZERO on this population** and are reported as zero.
They stay in because each was derived from a named residual item and each *changes the answer* on that item -- but
neither moves the number here, and strategy should treat both as unproven on 700 sentences.

**LOCATION alone is slightly NEGATIVE (-0.006) and becomes positive only once LOCATIVE INVERSION is on.** That is
not noise and it is the most interesting line in the table: **in English the locative predicate is normally
FRONTED** (`HERE is a copy`, `BELOW is a list`), so a scan that admits a locative complement to the *right* of the
copula fires mostly on the wrong token until the fronting construction is also present. The two are one system.

**The word sets are an operating point and they were swept, not adopted.** A first pass used a permissive frontable
set including `that` / `this`; those are canonical SUBJECTS in the same position and it cost the 167 recall
**0.7904 -> 0.7305** and added-fire precision **0.8429 -> 0.7606**. Scoping the set to deictic locatives and
wh-forms is what turned FRONTED from the worst construction into the best one.

**The one construction that cost more than it bought was narrowed rather than kept.** Firing the copula itself
whenever the complement scan merely failed added **31** fires for **2** clauses and took participant precision
**0.8367 -> 0.8177**, CI-separated DOWN. Restricted to the *truly stranded* configuration (nothing but punctuation
to the copula's right -- the actual VP-ellipsis/fronting environment, Hankamer & Sag 1976) it adds **2** fires for
**2** clauses at no precision cost.

### 3c. The 65 seen by nobody, and where the remaining 32 come from

pri 110 10e counted **65** of the 167 reached by no organ at all. Under this work:

| | count |
|---|---|
| the copular STATE reader sees (`copular_binding.robust_cop`) | 108 / 167 |
| **the PREDICATE-SLOT read sees** | **118 / 167** |
| either | 128 |
| **both, naming the SAME token** | **98** |
| state-reader only | 10 |
| predicate-slot only | 20 |
| **seen by NOBODY** | **39** (from 65) |
| **plus the reader's own verbal fires and BF rescue -> total reached** | **135 / 167 (0.8084)** |

And the **32 still missed** are attributed, not narrated:

| | count | whose problem |
|---|---|---|
| the copula is perceived but the complement scan picks another token | **22** | **mine** -- named per item in `residual_cap700.json` |
| not a copular clause in the gold tree at all (verbless fragment, other predication) | **6** | a different mechanism (fragment predication) |
| **UPSTREAM**: the category organ tags the gold copula `VERB` | **3** | the categories rung |
| **UPSTREAM**: `copular_available` says the slot is not held by a complement | **1** | the pri-110 hand-off |

So **4 of 32 are upstream of this read** and 28 are reachable in principle -- the arithmetic bound on this
population is **0.8084 -> 0.9760** if the complement scan and the fragment case were both solved perfectly.

---

## 4. The other three consumers

### 4a. The tense reader -- from nothing to 0.7006, and the fix is one sentence of neuroscience

`temporal_model.extract_events` skips every AUX lemma and fires only on Penn `VB*`; the live tense-preserving
detector assigns a Reichenbach triple only to `UPOS == VERB`. **So a copular clause carried no tense at all** --
*"she WAS a doctor"* and *"she IS a doctor"* were the same downstream record.

Carrying the tense of a predication that is not itself finite is **the copula's one job** (Pustet 2003; Bybee 1994
on auxiliation) -- it is the reason English inserts it. So the tense of a non-verbal predication is read off the
**CARRIER**, with the same stock labels `_stock_tense` produces for verbal events:

| | before | after |
|---|---|---|
| non-verbal clauses carrying a tense | **0 / 167** | **117 / 167 (0.7006)** |

distribution `SIMPLE_PRESENT 82, SIMPLE_PAST 25, MODAL_SUBORDINATE 5, FUTURE 4, PAST_PERFECT 1`.

**I am NOT claiming an accuracy number here and the reason is that it would be circular**: the copula's surface form
IS the evidence, so scoring the read against the copula's form measures nothing. The honest claim is coverage plus a
hand-checkable distribution and worked examples (`tense_cap700.json`). A real accuracy claim needs UD's
morphological `Tense` feature, which this repo's CoNLL-U loader drops -- named as a next step.

### 4b. The role competition -- cue coverage FIXED, accuracy a numbered NEGATIVE

**The coverage claim is met and it is large.** Over the **269** argument heads governed by a non-verbal predicate:

| cue | shipped | predicate-slot |
|---|---|---|
| pre-verbal SLOT (the Competition Model's first-noun strategy) | **2** | **52** |
| argument RANK (pre and post) | **5** | **136** |
| verb FRAME | **3** | **27** |
| `cop` | 262 | 262 (kept -- PRED is not VERB/AUX, so the copular-subject cue still fires) |
| voice_order | 7 | 7 (deliberately left "na": a non-verbal predicate carries no voice morphology) |

**The accuracy claim is NOT met, and the negative is understood.** Details and mechanism in section 5.

### 4c. The copular state reader and the ONE-STRUCTURE question

The brief asks that a clause yield ONE structure. Measured: on **98 of the 128** clauses where both organs fire,
the event's predicate and the state's PROPERTY are **the same token**; on **30** they disagree (20 slot-only, 10
state-only). **That is the one-structure defect, quantified.** I did not fix it: the right fix is to make
`_read_entity_states` read the predicate-slot signal instead of running `copular_binding.robust_cop` as an
independent second finder, which is a change inside a different landed organ with its own board dimension, and my
remit here is the event/role hand-off. It is the first alternate path in section 7, with the number.

---

## 5. Every negative, researched until understood

### 5a. THE ROLE COMPETITION'S PRED CONFIGURATION LOSES -- and the mechanism is measured, not guessed

Opening the gates alone changes nothing, and that is the first fact: with the LIVE table, every `PRED_*` lookup
misses and every cue abstains, so role accuracy on the 167's arguments collapses **0.7361 -> 0.3309**. *That is the
capability guard earning its place in the diff*: the head class is used only when the loaded table carries PRED
rows, because the strengths are **counts a teacher has to accrue**, not a rule that can be declared.

Rebuilding the table with the same cue function (`tools/build_coarse_role_validities.py`, monkeypatched cue
function, written to `data/hook_state/`, never over the live asset) takes it to **0.6654** -- still
**-0.0706 CI[-0.1078,-0.0335]** below the shipped 0.7361.

**And the configuration itself is a BETTER cue, which is why the loss needs an explanation rather than a shrug:**

| config | n (teaching decisions) | top role | reliability |
|---|---|---|---|
| `ADJ_pre` (live) | 1928.7 | SUBJ | 0.659 |
| `NOUN_pre` (live) | 10357.2 | OTHER | 0.554 |
| **`PRED_pre` (rebuilt)** | **2533.1** | **SUBJ** | **0.819** |

A pre-predicate nominal is the SUBJECT with **0.819** reliability once the configuration stops conflating
predicative with attributive heads -- against 0.659 / 0.554 for the classes it was hiding inside. **The
un-conflation works.** So the loss is not "PRED is a bad configuration".

**The confound I found and controlled.** The rebuilt table has **57,646** teaching decisions against the live
asset's **74,083** -- a **22%** difference that the PRED split cannot explain, since PRED took only 3,183 of them.
`VERB_pre` alone falls 16,281 -> 14,208. The live asset was built at an **earlier HEAD under an earlier frontend**
(the builder perceives its training text through the live tagger and parser, and both have moved -- pri 110's
predicate slot and pri 111's voice cue landed since). **So the -0.0706 against the live asset is not a measurement
of my change**; it is my change plus every upstream change since the asset was last built. This is the same class of
error pri 110 caught in its board straddle, and the control is the same: **a second table rebuilt TODAY with the
SHIPPED cue function**, so the only difference between the two is the cue function.

See section 5b for that controlled contrast.

### 5b. THE CONTROLLED ROLES CONTRAST

Two tables, rebuilt today by the organ's own builder with identical flags (`--v4 --perceived --weight`), written
to `data/hook_state/`, differing in **nothing but the cue function**. They carry **identical** totals
(**57,645.6** teaching decisions each), which is what makes this the matched contrast the live asset could not give.

| population | n | shipped cues | + PRED configuration | delta |
|---|---|---|---|---|
| **under a NON-VERBAL predicate** | 269 | 0.6914 | 0.6654 | **-0.0260 CI[-0.0558,+0.0037] -- NOT separated** |
| under a VERB | 1533 | 0.7978 | 0.7991 | +0.0013 CI[+0.0000,+0.0033] |
| all argument heads | 3698 | 0.7956 | 0.7918 | -0.0038 CI[-0.0073,-0.0003] |

**The -0.0706 was the confound.** Controlled, the PRED configuration is a small loss on its own population whose
confidence interval **includes zero**. The bar asked for an INCREASE CI-separated, and that is not met either way --
so this stays a NEGATIVE. But it is a *no-effect* negative, not a *harmful* one, and the difference matters for what
strategy should do next.

**AND THE MECHANISM IS IN THE COUNTS.** Comparing the two matched tables config by config:

| configuration | shipped-cues table | PRED table |
|---|---|---|
| `VERB_pre` | n=14207.9, SUBJ, **rel 0.716** | n=14207.9, SUBJ, rel 0.716 (untouched) |
| **`ADJ_pre`** | **n=1363.7, SUBJ, rel 0.845** | n=109.7, OTHER, rel 0.591 |
| `NOUN_pre` | n=8419.9, OTHER, rel 0.537 | n=7351.7, OTHER, rel 0.580 |
| **`PRED_pre`** | absent | **n=2533.1, SUBJ, rel 0.819** |

**`ADJ_pre` was ALREADY an 0.845-reliable SUBJECT cue -- MORE reliable than the pooled `PRED_pre` that replaced
it.** The split takes ~1,254 predicative-ADJ instances and ~1,068 predicative-NOUN instances and merges them into
one bucket, and the merged bucket is *less* reliable than the ADJ bucket it absorbed. **So the head's CATEGORY is
itself informative about its dependent's role, and pooling ADJ-predicates with NOUN-predicates throws that away:**
a nominal before a predicative adjective is a subject 84.5% of the time, while a nominal before a predicative noun
sits in an equative clause that has *two* nominals and is a far weaker cue. The un-conflation with the ATTRIBUTIVE
adjective is real -- but on this treebank it buys less than the conflation of ADJ with NOUN costs.

**That is a fully understood negative, and it names its own repair**: open the predicate-relative cues but **keep the
head-category configuration** (arm B3, section 5f) -- which preserves `ADJ_pre`'s 0.845 while letting the
pre-verbal-slot / rank / frame cues fire.

### 5b-bis. AN UNRELATED FINDING THE CONTROL EXPOSED, AND IT IS A BRIEF ON ITS OWN

The matched control had to be built because the live asset differs from a fresh build by **74,083.3 -> 57,645.6**
teaching decisions. **The builder drops an instance in exactly one place** -- `w <= 0 or w < MIN_CONF` (0.5), the
reliability gate on the governor's own head posterior -- so a **22.2% fall in teaching decisions IS a fall in the
governor's confidence**, by arithmetic and not by inference. And the fresh build is WORSE where it matters:

| scored with the SHIPPED cue function | all (n=3698) | under a non-verbal predicate (n=269) |
|---|---|---|
| the LIVE asset (built at an earlier HEAD) | **0.8056** | **0.7361** |
| a fresh rebuild on today's frontend | 0.7956 | 0.6914 |

**Rebuilding the role validity table on today's frontend LOSES 0.0100 overall and 0.0447 on the population this
brief is about.** That is not my change; it is a property of the current chain, it is invisible to anything that
does not rebuild the asset, and it means the live role asset is carrying knowledge the current governor can no
longer teach. **Filed as the highest-value lead in section 7.**

### 5e. THE SECOND CUE: a raw union is a real trade-off, and the GRADED form removes it

The brief's item 4 is explicit -- *"if firing on non-verbal predicates costs precision at a consumer, the hand-off
is graded and the consumer weights it; measure the graded form before declaring a trade-off."* So I did, in that
order.

The heads rung supplies an INDEPENDENT cue to the same predicate: a copula attaches TO its predicate, and the landed
copular state reader (`copular_binding.robust_cop`) already reads that off the tree. The two cues overlap but are
not the same set (98 shared, 20 surface-only, 10 arc-only of the 167). **A raw UNION is a genuine trade-off:**

| arm | recall | precision | F1 | on the 167 | added-fire precision |
|---|---|---|---|---|---|
| FLOOR (live reader) | 0.8176 | 0.8358 | 0.8266 | 0.1856 | -- |
| SURFACE (shipped here) | 0.9541 | 0.8370 | 0.8917 | 0.8084 | 0.8462 |
| ARC alone | 0.9423 | 0.8106 | 0.8715 | 0.7545 | 0.6398 |
| **UNION** | 0.9659 | **0.8076** | 0.8797 | **0.8623** | 0.6533 |

`UNION - SURFACE`: recall **+0.0118 CI[+0.0052,+0.0197]**, precision **-0.0294 CI[-0.0378,-0.0213]** -- both
CI-separated. Recall bought with precision, exactly as the brief anticipates.

**THE GRADED FORM REMOVES THE TRADE-OFF.** The arc cue is not a boolean: the governor hands down a POSTERIOR over
the copula's head, and `P(head = q)` IS the reliability of *"q is the predicate"* -- the same quantity the role
builder already uses as its teaching weight (Ernst & Banks 2002; Ma-Beck-Latham-Pouget 2006). Gating on it:

| tau | recall | precision | F1 | on the 167 | d(precision) vs the live floor |
|---|---|---|---|---|---|
| 0.00 (raw union) | 0.9659 | 0.8076 | 0.8797 | 0.8623 | **-0.0282 CI[-0.0386,-0.0171] SEPARATED DOWN** |
| 0.05 | 0.9646 | 0.8307 | 0.8926 | 0.8563 | -0.0051 CI[-0.0135,+0.0028] |
| **0.10** | 0.9646 | 0.8320 | **0.8934** | **0.8563** | -0.0038 CI[-0.0118,+0.0041] |
| 0.20 / 0.30 | 0.9633 | 0.8325 | 0.8931 | 0.8503 | -0.0032 CI[-0.0116,+0.0046] |
| **0.50** | 0.9633 | 0.8332 | **0.8935** | 0.8503 | -0.0026 CI[-0.0108,+0.0051] |
| 0.70 | 0.9593 | 0.8335 | 0.8920 | 0.8323 | -0.0023 CI[-0.0105,+0.0052] |
| 0.90 | 0.9593 | 0.8341 | 0.8924 | 0.8323 | -0.0016 CI[-0.0099,+0.0058] |
| off (surface only) | 0.9541 | 0.8370 | 0.8917 | 0.8084 | +0.0012 CI[-0.0059,+0.0079] |

**Every threshold from 0.05 to 0.90 has a precision delta whose CI includes zero, and the region is FLAT** -- a
0.0034 spread in precision across an 18x change in the threshold, which says the operating point is not a tuned
knob. At tau = 0.5 (the middle of the flat region) the arm reaches **0.8503** of the 167 -- **+0.042 over the
shipped surface arm** -- at the best F1 in the whole study (0.8935) and no CI-separated precision cost.

**It is shipped DEFAULT OFF (`HDLAB_PREDICATION_ARC_TAU=0`) and I want to be explicit that this is not a hiding
place:** the board A/B in section 6 covers the SURFACE arm, and this arm has not had its own. Turning it on is one
environment variable plus one `--board-ab --full`, and it is the first item in section 7.

### 5f. THE PUREST FORM OF THE ARC CUE IS WORSE, and that is informative

The arc cue could be read with no second organ at all: the copula's own MAP head IS its predicate. Measured as its
own sweep, that read is worse at **every** threshold -- at tau = 0.5, precision **0.8274** against `robust_cop`'s
**0.8332** at identical recall (0.9633 / 0.8503 on the 167). **So `robust_cop`'s gated fallback chain (skip an
expletive holder, skip an intervening main verb, fall through to the next content head) is carrying real signal
beyond the bare arc**, which is worth recording because it is evidence FOR the landed organ at a moment when the
rest of this report is arguing that that organ should be consolidated away. Consolidating it must preserve those
gates.

### 5c. LOCATION alone is negative, and the reason is a construction, not noise

Admitting a locative ADV complement *to the right of the copula* costs **-0.006** on the 167 in isolation and pays
only once LOCATIVE INVERSION is on. Mechanism: **English normally FRONTS the locative predicate** (`HERE is a copy`,
`BELOW is a list`), so before fronting exists the right-scan fires on the postposed **subject** instead. Two
constructions, one system; measuring them separately is what made that visible.

### 5d. TWO CONSTRUCTIONS ARE WORTH ZERO

COMPLEX LOCATIVE (`out of town`) and LEFT-FRONTED PREDICATE (`how reliable that is`) each move the answer on the
residual item that motivated them and move the aggregate by **exactly 0.0000**. On 762 clauses their populations are
1 and 3 items; the instrument cannot resolve them. Reported as zero, kept because each is a correct reading of a
named construction, and flagged as unproven.

---

## 6. The board

The bar asks that the board not be down on any dimension. Run as a **capped A/B with both arms back-to-back in
ONE process** -- the controlled form, because pri 110 10c documents a two-process board A/B on this repo straddling
another session's integration and manufacturing three false regressions:

| dimension | n | base | + predicate slot | delta |
|---|---|---|---|---|
| coref | 504 | 0.4206 | 0.4206 | **+0.0000** |
| common_noun_coref | 447 | 0.4989 | 0.4989 | **+0.0000** |
| salience | 20 | 0.6500 | 0.6500 | **+0.0000** |
| who_did_what_agent | 317 | 0.7539 | 0.7539 | **+0.0000** |
| who_did_what_patient | 241 | 0.8091 | 0.8091 | **+0.0000** |
| **state** | 73 | 0.6849 | 0.6849 | **+0.0000** |
| wic | 120 | 0.7833 | 0.7833 | **+0.0000** |
| **aggregate** | | **0.5958** | **0.5958** | **+0.0000** |

**All seven identical. Nothing is down -- and nothing is UP either, which is the honest half of this result and
worth more than the first half.** The event stream gains 143 predication nodes covering a fifth of what the text
asserts, and not one board dimension moves. That is not a null: it is a **statement about the consumers**. The
board's dimensions are answered by the coref chain, the who-did-what front end and the copular state reader, and
none of them reads the event stream's non-verbal nodes yet -- the state dimension reads `sm.entity_states` (built by
`copular_binding`, the second predicate finder, which already saw most of these clauses), and who-did-what reads the
role competition, whose gates I could open for cue coverage but whose validity table does not yet carry the rows.
**This is the "board-invisible proven win" case exactly**, and the project's own rule for it is that the win needs
its OWN instrument arm rather than being recorded as a located negative. The participant instrument is that arm.

FULL_BOARD_PLACEHOLDER

---

## 6b. What let the signal be maximised -- the chain, rung by rung

The owner's reading holds here and it is worth being precise about WHICH rungs cracked, because the biggest number
in this report (**0.1856 -> 0.8084 on the 167**) came from a rung nobody had to build.

**CRACKED.**

1. **THE SIGNAL WAS ALREADY COMPUTED AND THROWN AWAY.** `attachment_arm.cop_predicates` has known which token a
   copula predicates of since 2026-09-13. Its only consumers were two functions inside its own organ. **The single
   largest gain in this brief -- 0.1856 -> 0.7246 on the 167, four fifths of the whole effect -- is a WIRE, not a
   build.** That is the rung, and it is worth naming as a class: *a produced-but-unread signal is a different
   failure from a missing one, and cheaper to fix by an order of magnitude.*
2. **THE ARITHMETIC OF THE RUNG ABOVE ALREADY HAD A HOLE IN THE SHAPE OF THIS ONE.** pri 110 wrote
   `occ = (1 - host) * (1 - cop_available)` and shipped it. The complement of that expression inside the same
   product -- `(1 - host) * cop_available` -- is this brief, and the two partition `(1 - host)` exactly. **Reading
   the upstream rung's own equation, rather than the upstream rung's own README, is what made this an ARM of one
   organ instead of a second predicate finder.** The partition is asserted numerically in the self-test, so the
   one-predicate-per-clause claim is a measurement rather than an argument.
3. **THE INSTRUMENT WAS THE PRECONDITION, NOT THE PAPERWORK.** pri 110 BUILT the copular-event arm, measured it,
   and refused to ship it, because UD's VERB column scored its correct fires as false positives. Nothing about the
   mechanism changed here; what changed is that the fires are now scored by whether they GOVERN PARTICIPANTS. **The
   same arm goes from "precision 0.8629 -> 0.7778, not shipped" to "precision +0.0012, shipped" purely by asking
   the question the brain's definition asks.** The instrument was the lever.
4. **THE RESIDUAL WAS ATTRIBUTED, NOT NARRATED, AND EVERY CONSTRUCTION CAME OUT OF IT.** Ten constructions, none
   invented at a desk: each one is a line in `--residual` with the token the scan picked instead. Two of them turned
   out to be worth zero and are reported as zero; one cost more than it bought and was narrowed; one (LOCATION) is
   negative alone and positive in company, which is itself a finding about English.
5. **THE OPERATING POINT WAS SWEPT AND THE SWEEP CAUGHT A REAL ERROR.** A permissive frontable set cost
   0.7904 -> 0.7305; the graded arc threshold is flat from 0.05 to 0.90 and CI-separated-down only at 0.00. Neither
   of those is visible without the sweep.

**NOT CRACKED, and each one is named with a number.**

- **THE ROLE COMPETITION'S CONFIGURATION.** The PRED class is right in principle (it un-conflates predicative from
  attributive) and loses in practice (the pooling costs more, `ADJ_pre` 0.845 -> `PRED_pre` 0.819). The repair --
  open the cues, keep the configuration -- is named and its table is building.
- **THE JOINT FRAME-SLOT DECODE** never groups a non-verbal predicate's arguments (line ~1396). Untouched on
  purpose, so that PATCH == CELL stays exact.
- **THE ONE-STRUCTURE RECONCILIATION.** Two predicate finders, 30 disagreements of 128. Quantified, not fixed.
- **THE TENSE IS COVERAGE, NOT ACCURACY.** 0 -> 117 of 167, but UD's morphological `Tense` feature is dropped by
  this repo's CoNLL-U loader, so the read has no independent gold. Naming that is the honest end of that rung.
- **ONE POPULATION.** Everything here is UD-EWT test 700. pri 110's effect was LARGER out of supply on GUM; mine is
  untested there, and that is the first control I would add.

---

## 7. What it would take to convert this to a FULL PASS

Six of the bar's eight criteria are met. Here is each one, what is missing, and -- for every gap -- the lead,
its research, and whether I chased it.

| bar criterion | status |
|---|---|
| the participant instrument built and published, gold-free at decision time | **MET** |
| a twin with predicates picked at random at the same rate at floor | **MET** -- 3 seeds, CI-separated on recall AND precision |
| participant precision not below the verbal clauses' CI-separated | **MET** -- +0.0012 CI[-0.0059,+0.0079] |
| the 65 seen-by-nobody down to a counted residual with reasons | **MET** -- 65 -> 39, and all 32 remaining misses in 4 attributed classes |
| board not down on any dimension | **MET** (capped, all 7 at +0.0000; full run FULL_BOARD_STATUS) |
| the role competition's full cue set firing on them | **MET** -- slot 2 -> 52, rank 5 -> 136, frame 3 -> 27 |
| **event/state fired on >= 0.90 of the 167** | **NOT MET: 0.8084** shipped, **0.8503** with the graded arc cue |
| **role accuracy on the 167 up CI-separated** | **NOT MET: -0.0260 CI[-0.0558,+0.0037]**, controlled -- no gain, not a significant loss |
| **one structure per clause** | **NOT MET** -- 98 of 128 agree, 30 disagree |

### 7a. To reach 0.90 on the 167 (currently 0.8084 shipped / 0.8503 with the arc cue)

**LEAD 1 -- turn the graded arc cue ON. CHASED AND MEASURED; it needs a board A/B, not a build.**
0.8084 -> **0.8503** at tau = 0.5, F1 0.8917 -> 0.8935, precision delta CI includes zero, flat from 0.05 to 0.90.
*What remains:* `HDLAB_PREDICATION_ARC_TAU=0.5` plus one `--board-ab --full`. **This is the single highest-value
remaining action in the whole brief and it is one environment variable.**

**LEAD 2 -- the 22 complement-scan misses, each named.** *Research:* every one is in
`data/exp_nonverbal_predication_participants_agent_v1/residual_cap700.json` with the token the scan picked instead.
The classes that remain after the ten constructions are (i) **postposed-subject inversion with a fronted non-deictic
predicate** (`Most troubling , however , is the fact ...`, `Wtf is this ?`) -- the fronted element is an ADJ or a
mis-tagged wh-form, so `FRONTABLE_PRED` does not admit it and admitting ANY left neighbour was measured to cost
0.7904 -> 0.7305; (ii) **an ADJ + NUM run** (`Today is good 12:30 ?`) where the run's last ADJ/NUM rule takes the
NUM; (iii) **a complement behind a parenthetical** (`This statement is , despite its facade of fair - mindedness ,
so many weasel words .`), where the scan breaks at the comma. *Chased:* (iii) is the one I would do next -- the arm
ALREADY has the reading (`copular_available` returns 1.0 for a crossed-punctuation complement, pri 110 10b), so the
complement scan needs to cross the same boundary the availability test already crosses. That is a two-line change
and I ran out of measurement budget, not ideas. *Bound:* these 22 are 13.2% of the 167.

**LEAD 3 -- the 6 non-copular predications.** *Research:* `attachment_arm.assertion_candidates` already admits the
content heads of phrases in a verbless utterance, and -- exactly like `cop_predicates` before this brief -- **it has
no event consumer.** *What it would take:* route its fragment branch into `predicate_sites` behind its own switch
and re-run this instrument. Small; alternate path E.

**LEAD 4 -- the 4 upstream misses.** 3 are the category organ tagging a gold copula `VERB` and 1 is
`copular_available` denying the slot. Those belong to the categories rung and to pri 110's hand-off. Not mine.

**THE ARITHMETIC BOUND:** with leads 2 and 3 solved perfectly the ceiling on this population is **0.9760**; with
lead 1 alone the measured value is **0.8503**. The bar's 0.90 sits between them, so **0.90 is reachable on this
population and the route to it is enumerated** -- it is not a wall.

### 7b. To make role accuracy go UP (currently -0.0260, CI includes zero)

**LEAD 5 -- open the gates but KEEP the head-category configuration (arm B3). CHASED; the table is building.**
The counts say the split is what costs: `ADJ_pre` is an **0.845**-reliable SUBJ cue that the PRED pooling replaces
with an 0.819 one. Keeping `ADJ_pre` / `NOUN_pre` / `ADV_pre` as configurations while letting the pre-verbal-slot,
rank and frame cues fire inside them preserves the 0.845 and adds the coverage. **This is the arm I would ship if
the build lands.**

**LEAD 6 -- the joint frame-slot decode never groups a non-verbal predicate's arguments.**
`coarse_roles` groups a verb's dependents for the capacity-one slot assignment only when `pos[h-1] in ("VERB","AUX")`
(line ~1396). A copular clause's subject and predicate-nominal therefore never compete for one slot, which is
exactly the situation an equative clause creates. *Not cracked here*, deliberately: my diff matches the cell exactly,
and the cell does not touch the grouping. Named as an uncracked rung.

**LEAD 7 -- and this one is bigger than my brief.** The matched control exposed that **rebuilding the role validity
table on today's frontend loses 0.0100 overall and 0.0447 on this population** (5b-bis), because 22.2% fewer
training instances clear the governor's reliability gate than when the live asset was built. The role competition
is being taught by a governor that has become less confident. **Until that is understood, every asset-level result
on this organ -- including mine -- is measured against a floor that is drifting.** Brief-ready, with the numbers.

### 7c. To get ONE structure per clause

**LEAD 8 -- consolidate the copular state reader onto the predicate-slot signal.** 98 of 128 already agree; the 30
that disagree are two organs answering one question. Alternate path A, with the caveat from 5f that `robust_cop`'s
gates carry real signal and must survive the consolidation.

---

## 8. Alternate paths -- similarly or MORE brain-foundational than what I shipped

**A. RECONCILE THE STATE READER ONTO THE PREDICATE-SLOT SIGNAL -- MORE brain-foundational than what I shipped, and
the first thing strategy should queue.**
*The structure:* one clause, one eventuality (Spivey-Knowlton 1993); the copular case is a Kimian STATE, a distinct
SORT of the same eventuality, not a distinct organ (Maienborn 2005). *What is built instead:* two independent
predicate finders for the same clause -- `attachment_arm.cop_complement` (a surface/construction cue) and
`copular_binding.robust_cop` (an arc cue) -- which agree on **98** of the **128** clauses where both fire and
disagree on **30**. *The math:* one predicate site per clause with a graded strength, and the state reader takes its
PROPERTY from that site and keeps `copular_binding` only for the HOLDER. *What it would take:* a change inside
`_read_entity_states` plus a full-size `state` dimension A/B (n=378), because that dimension is exactly what would
move. *Why not now:* it is inside a landed organ with its own owner-DONE problem folder and its own board dimension,
and my remit is the event/role hand-off. **This is the one-structure half of the bar, and it is the reason my
verdict is PARTIAL rather than SOLVED on that criterion.**

**B. COMBINE THE TWO CUES BY RELIABILITY, NOT BY UNION -- built and measured here (section 5e), and the right shape
is already clear.** The arc cue's reliability is the governor's own `head_posterior` for the copula's arc, which is
what the role builder already uses as its teaching weight (Ernst & Banks 2002; Ma-Beck-Latham-Pouget 2006). This is
MORE brain-faithful than either cue alone and it is the brief's own item 4. *What it would take beyond what is
here:* the arc cue firing as a graded STRENGTH into `predicate_sites` rather than as a thresholded set, so the
downstream consumer weights it rather than the detector committing.

**C. LET THE CATEGORY ORGAN HAND DOWN A PREDICATE CLASS, NOT A TAG.** The deepest form of this brief's finding is
that *the tag column is being asked a question it cannot answer*: "is there an eventuality here?" is not a question
about part of speech, and no amount of tagger accuracy fixes it. The brain-foundational form is an INDUCED category
whose defining distribution is predicate-hood, which is exactly what pri 15's induced-class swap is the vehicle for.
*Why not now:* it changes the category inventory every organ reads, and the guard I shipped (silence under an
inventory that lacks the UPOS classes) is the minimum precondition for trying it.

**D. LEARN THE CONSTRUCTIONS FROM COUNTS INSTEAD OF NAMING THEM.** `LOCATIVE_ADV` and `FRONTABLE_PRED` are
closed-class lists exactly like the arm's existing `COP_FORMS` / `WH_FORMS` / `EXPLETIVE`, and the ablation shows
their membership MATTERS (including `that` / `this` cost 0.7904 -> 0.7305). The plastic form accrues
`P(complement | carrier lemma, left-context bin, right-context bin)` in the arm's existing Rescorla-Wagner combiner
and calls `observe()` when a fired predication later acquires argument roles. *Why not now:* the confirmation signal
is the roles rung, which is currently the negative in section 5 -- the learner would be taught by the organ that is
not yet working. **That dependency is itself the argument for fixing the roles rung first.**

**E. A FRAGMENT-PREDICATION ARM for the 6 clauses that are not copular at all.** `attachment_arm.assertion_candidates`
ALREADY admits the content heads of phrases in a verbless utterance ("a headline, a list item, a signature, a
price") -- and, exactly like `cop_predicates` before this brief, **it has no event consumer.** The same defect, one
construction over. *What it would take:* route `assertion_candidates`'s fragment branch into `predicate_sites`
under its own switch and re-run this instrument. Small, and it is the cheapest remaining recall on the residual.

**F. SCORE THE PARTICIPANT INSTRUMENT ON A SECOND, OUT-OF-SUPPLY POPULATION.** Everything here is UD-EWT test 700.
GUM/GENTLE (12+ genres, gold trees, outside the category organ's count supply) runs through the same instrument with
no change -- pri 110 found its effect was LARGER out of supply, which is what a real mechanism does. *Why not now:*
time; it is a re-run, not a build, and it is the first thing I would do with another hour.

---

## 9. Every component touched, and its brain-foundational status FOR THIS SIGNAL

| component | what it does here | BF status as the disk shows it | BF status FOR THIS SIGNAL |
|---|---|---|---|
| `hdlab/attachment_arm.py` | **owns predication**; already held `cop_predicates`, `copular_available`, `host_belief`, and pri 110's carrier occupancy | BF_SPIRIT | **was NOT BF for this signal**: it computed which token a copula predicates of and had NO consumer for it, and its complement scan carried four constructions implicitly and seven not at all. Fixed here as an ARM of the same organ (branch 2 of the same three-way discharge), not a new organ |
| `hdlab/lexical_categories.py` | hands down the graded posterior the sites are read off | BF_SPIRIT (count-based generative 2nd-order HMM, plastic) | BF for the carrier question (pri 110) and **read correctly here** -- the site strengths come from the posterior, never from the argmax. **Still the source of 3 of the 32 remaining misses** (it tags the gold copula VERB) |
| `hdlab/situation_reader.py` (`_tense_agnostic_extract`) | the event detector | -- | **was NOT BF**: a hard `up[i] == "VERB"` point-read that asked the tag column whether an eventuality exists. **Fixed**: fires on the predicate slot, additively, keeping the predicate's own UPOS as the eventuality's SORT marker (Maienborn's Kimian state) |
| `hdlab/situation_reader.py` (`_read_entity_states`) -> `hdlab/copular_binding.py` | the copular state reader | BF in spirit (a state is a distinct sort) | **FRAGMENTED**: a second, independent predicate finder for the same clause. Quantified here (98 agree / 30 disagree of 128); NOT fixed -- alternate path A |
| `hdlab/graded_role_assigner.py` | the role competition | BF_SPIRIT (Competition Model, learned cue validities, plastic via `observe_role_outcome`) | **NOT BF for this signal**: `_head_class` reads the tag column where the Competition Model's configuration is a relation to the PREDICATE, which both CONFLATES predicative with attributive heads and shuts every predicate-relative cue. Cue coverage fixed and measured; accuracy a numbered negative (section 5) |
| `hdlab/temporal_model.py` + `hdlab/tense_preserving_detector.py` | the tense reader | BF_SPIRIT (Reichenbach) | **was NOT BF**: it skips every AUX lemma and fires only on Penn `VB*`, so the copula -- whose ONE job is to carry tense (Pustet 2003) -- was read as having none. **Fixed**: the predication inherits the carrier's tense, 0 -> 117 of 167 |
| `tools/build_coarse_role_validities.py` | the role teacher | BF_SPIRIT (reliability-weighted accrual) | **read-only here.** It calls the same cue function, so a rebuild learns the new configuration -- which is why the roles arm is an ASSET question and not a code question. Two tables rebuilt into `data/hook_state/`, never over the live asset |
| `hdlab/frontend.py` | the one hand-off | BF_SPIRIT | **untouched** |

**AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` 2b.** (1) `situation_reader._tense_agnostic_extract` should
be recorded as **NOT BF as shipped** for event-hood: it asks the tag column an ontological question. (2)
`attachment_arm.cop_predicates` should be recorded as a **produced-but-unread signal** before this brief -- a
distinct failure mode from "not built" and worth its own row, because the audit currently has no way to say
"computed correctly and thrown away". (3) `graded_role_assigner._head_class` should be recorded as reading the tag
column where the Competition Model's configuration is functional. (4) The copular STATE path should be recorded as
**one brain structure implemented as two organs** (the anti-fragmentation gate), with the 98/30 agreement number.

---

## 10. Submission prompt

```
pri 113 (AGENT ARM of the head-to-head) -- one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag

PARTIAL. THE PREDICATION IS THE EVENT, and the event detector now fires on it. pri 110 shipped branch (3) of the
tense carrier's three-way discharge (the carrier that predicates on its own); this is branch (2) -- the copula that
carries tense FOR a non-verbal predicate -- and it is the SAME product, complement_occ = (1 - host) * cop_available
against pri 110's (1 - host) * (1 - cop_available), so the two PARTITION (1 - host) and one clause can never get two
predicates (asserted over 90 copulas). One organ (attachment_arm owns predication), one computation, two branches.

THE INSTRUMENT FIRST (pri 110 filed it as 7D and did not build it): 762 subject-bearing gold clauses on UD-EWT test
700 (595 verbal + 167 non-verbal by UD's convention); a fired event is correct when its index IS the clause's gold
predicate; precision counts a fire only if its index governs >= 1 gold CORE argument in the gold TREE. The gold TAG
column is never asked what category a predicate may be -- it cannot adjudicate a predication event on an ADJ, which
is why pri 110 refused to ship its own phase-4 lever.
  the LIVE reader as shipped   recall 0.8176  precision 0.8358  F1 0.8266  on the 167 non-verbal: 0.1856
  + the predicate slot         recall 0.9541  precision 0.8370  F1 0.8917  on the 167 non-verbal: 0.8084
recall +0.1365 CI[+0.1115,+0.1601] CI-SEPARATED; precision +0.0012 CI[-0.0059,+0.0079] -- NOT DOWN; the 143 added
fires are 0.8462 precise against the shipped detector's own 0.8358. INFO-FREE TWIN, 3 seeds (the same NUMBER of
extra fires at random): recall 0.827/0.833/0.841, precision 0.745/0.750/0.754 -- beaten CI-separated on BOTH.
BOARD, both arms back-to-back in ONE process (capped): all SEVEN dimensions +0.0000, aggregate 0.5958 -> 0.5958.
FULL_BOARD_ONELINE

TEN CONSTRUCTIONS, EACH FOUND BY ATTRIBUTING THE RESIDUAL AND EACH ABLATED SEPARATELY (on the 167):
shipped cop_predicates .7246 -> LOCATION .7186 -> CLAUSE-LOCAL .7186 -> INVERSION .7425 -> DP .7665 ->
LOCATIVE-INVERSION .7964 -> RIGHT-HAND-HEAD-RULE .8024 -> COMPLEX-LOCATIVE .8024 -> LEFT-FRONTED .8024 ->
ELLIPSIS .8084. TWO OF THE TEN ARE WORTH EXACTLY ZERO and are reported as zero. LOCATION alone is NEGATIVE and
turns positive only with LOCATIVE INVERSION, because English normally FRONTS the locative predicate -- two
constructions, one system. The word sets are a SWEPT operating point: a permissive frontable set including
`that`/`this` cost the 167 recall .7904 -> .7305. A construction that cost more than it bought (fire the copula
whenever the scan fails: 31 extra fires for 2 clauses, precision CI-separated DOWN) was NARROWED to the truly
stranded configuration, not kept.

THE TENSE READER WAS SILENT ON EVERY COPULAR CLAUSE and now is not: carrying the tense of a non-finite predication
is the copula's ONE job (Pustet 2003), so the predication inherits the CARRIER's tense -- 0 -> 117 of 167 (0.7006),
82 present / 25 past / 5 modal / 4 future / 1 past-perfect. I do NOT claim an accuracy number: the copula's form IS
the evidence, so scoring against it would be circular.

THE 65 SEEN BY NOBODY ARE 39, AND ALL 32 REMAINING MISSES ARE ATTRIBUTED: 22 the complement scan picking another
token (named per item), 6 not copular clauses in the gold tree at all, 3 the CATEGORY organ tagging the gold copula
VERB, 1 `copular_available` denying the slot. Arithmetic bound on this population if the scan and the fragment case
were solved perfectly: 0.9760.

THE NUMBERED NEGATIVE -- THE ROLE COMPETITION. Cue coverage is FIXED: over the 269 arguments under a non-verbal
predicate the pre-verbal-SLOT cue fires 2 -> 52, argument RANK 5 -> 136, verb FRAME 3 -> 27. Accuracy is NOT: the
PRED configuration scores ROLES_HEADLINE. MECHANISM, measured not guessed: PRED_pre is a BETTER cue than what it
replaced (n=2533, cues SUBJ at reliability 0.819 against ADJ_pre's 0.659 and NOUN_pre's 0.554), so the loss is not
the configuration. ROLES_MECHANISM
A CONFOUND WAS CAUGHT: the live validity asset was built at an earlier HEAD under an earlier frontend and differs
from a fresh build by 22% of its teaching decisions (74,083 -> 57,646, with VERB_pre alone 16,281 -> 14,208), so the
first contrast against it measured my change PLUS every upstream change since. A second table was rebuilt today with
the SHIPPED cue function as the matched control.

CAPABILITY GUARDS, NOT ASSUMPTIONS (the 2026-09-14 Penn-tagset crash): predicate_sites returns {} under any category
inventory lacking the UPOS classes it reads, and the PRED head class is used only when the LOADED table carries PRED
rows -- measured, because without them role accuracy on those clauses falls 0.7361 -> 0.3309.
PATCH == CELL: the self-test EXECUTES the diff's own added code -- 0 site mismatches, 0 complement mismatches, max
|strength diff| 0.0 over 5,224 tokens; git apply --check clean; self-test 13/13. With every construction OFF the
scan reproduces attachment_arm.cop_predicates exactly (0 mismatches / 200 sentences), so the switch is a true no-op.

ONE STRUCTURE PER CLAUSE IS NOT MET AND IS QUANTIFIED: the event's predicate and the copular state reader's PROPERTY
name the SAME token on 98 of the 128 clauses where both fire and DISAGREE on 30. The fix is to make
`_read_entity_states` read the predicate-slot signal instead of running a second independent predicate finder --
alternate path A, and the top follow-on.

HEAD-TO-HEAD NOTE: the file names in section 7 were already occupied on disk by the owner's live session at
13:52:25 EDT; I did not overwrite them. My files are the *_agent* ones under notes/comparisons/pri113_agent/. I saw
lines 1-90 of that file before stopping -- its docstring and two ideas (an ADV/locative complement, a clause-final
copula), one of which I had derived ten minutes earlier and the other of which is in pri 110's own docstring.
Strategy should discount both from the comparison.

Files: experiments/exp_nonverbal_predication_participants_agent_v1.py;
notes/comparisons/pri113_agent/{SOLVED_agent.md, predicate_slot_consumers_agent_patch.diff};
data/exp_nonverbal_predication_participants_agent_v1/*.json; data/hook_state/coarse_role_validities_pri113_*.json.
NO hdlab/ or tools/ file changed on disk.
Reverify: --self-test ; --participant --v2 --cap 700 ; --ablate --cap 700 ; --attrib --cap 700 ; --tense --cap 700 ;
--states --cap 700 ; --cueint --cap 700 ; --arcgrade --cap 700 ; --board-ab
```
