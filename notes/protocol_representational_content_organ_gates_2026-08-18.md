# PROTOCOL -- HOW TO PROVE A STORE HOLDS "COULD REPLACE" AND NOT JUST "APPEARS NEAR"
## plus an audit of what 2026-08-17's experiments actually bought us

**Written 2026-08-18 by the Director as research drill 2 of the three named in
`notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` section 6.7 ("what experimental protocol does this
class of problem actually demand"). No cell was authored, no experiment run, nobody dispatched.
Every number below was read off disk; the enumeration method is stated in section 1.**

---

## 0. THE WHOLE THING IN PLAIN LANGUAGE, BEFORE ANY DETAIL

We spent 2026-08-17 asking a machine, sixteen times, **"does this change help?"** Sixteen times it
said "barely, or no". Then twice we asked a different question -- **"which part of this machine is
losing the signal?"** -- and both times we learned something that changed the plan.

**The audit says: of the eleven experiments the owner counted, FOUR changed what we did next and
SEVEN did not.** (A filesystem sweep finds five MORE full runs the same day that the "eleven"
framing missed; none of those five changed anything either, and five of them were never even
committed to git. So the true yield is more like **4 of 16**.)

The reason is not that the seven were sloppy. They were beautifully controlled. The reason is
structural, and it is this:

> **An experiment that can come back "no" tells you nothing when you already expect "no".**
> All year our system has scored 0.02-0.06 on a task where a machine that ignores the question
> entirely scores 0.139. Every "does this help?" test therefore has one likely answer, and that
> answer names no next step. A ladder cannot come back "no". It comes back with a RANKING of the
> machine's own parts, and the top of that ranking is a thing to go and fix.

The second reason is arithmetic. Our accuracy differences (0.002 to 0.04) are the same size as the
noise in the measurement (about 0.026 at our usual sample size). **We were measuring with a ruler
whose smallest tick is bigger than the things we were measuring.** A ladder fixes that too, because
it measures the DIFFERENCE between two rungs on the SAME items -- and a paired difference has about
a third of the noise of the two levels it is made from.

The third reason is that our real question is not an accuracy question at all. Our real question is
**"has the store recorded which words could replace each other, or only which words sit near each
other?"** That is a question about CONTENT. Accuracy is a terrible instrument for it -- it looks at
one word (the winner) per item and throws away everything else. The fields that ask content
questions for a living -- brain imaging, and the people who take apart language models -- long ago
stopped using end-task accuracy for it, for exactly our reason.

**What this note proposes we adopt tomorrow:**

1. **A named, ordered protocol for taking one organ apart -- OGL-1, nine gates numbered 0 to 8**
   (section 7). A subagent can follow it without judgement calls. It ends either with a named broken
   step or with a written statement that the organ is not where the problem is.
2. **A new primary measurement to replace end-task accuracy** (section 8): the **DISSOCIATION
   SCORE**. Build two small sets of word pairs -- ones that CAN replace each other but never appear
   together, and ones that always appear together but cannot replace each other -- and ask which
   set our store scores higher. **A store that holds substitutability puts the first set on top. A
   store that holds co-occurrence puts the second on top. The SIGN of that one number is the answer
   to our central question**, and its size is the size of our defect. It needs no new data: we
   already have WordNet and the corpus co-occurrence index. It also has a property nothing else we
   own has -- **our four floors sit at chance on it by construction**, so for the first time the bar
   would measure us rather than measuring the pool.
3. **A before-you-run test for whether an experiment can possibly produce an answer** (section 9.1).
   Three of our six retractions were "we read a fog as a result". The test is one line, it is run
   BEFORE the experiment, and applied retrospectively it would have stopped five of the seven
   no-decision runs.
4. **Two new corrections found while doing this audit** (sections 4.5 and 5), one of which affects a
   headline currently in the plan and one of which is five uncommitted experiment results.

**What this note refuses to do:** weaken any gate. Where a gate is currently out of reach I say so
and say what would put it in reach (section 8). Widening a band is not a result.

---

## 1. HOW I ENUMERATED (state the method, per the absence-claim discipline)

Three independent enumerations, because "I looked and didn't find it" is not evidence:

1. **Git, by content not by name.** `git log --since="2026-08-16 12:00" --until="2026-08-19"
   --name-only` over the repo, then kept every commit whose file list contains a path matching
   `data/exp_*/metrics.json`. This is a SHAPE query, not a keyword query, so it cannot be defeated
   by naming drift. It yields **eleven** experiment cells landed 2026-08-17 between 10:41 and 14:03
   local, then three ladder/rescore cells later that evening. The eleven match the owner's count
   exactly.
2. **The filesystem, independently.** `os.walk`-equivalent glob over `data/exp_*/metrics.json`
   filtered on mtime date == 2026-08-17 UTC. 103 files, of which 62 are one bulk-touch block at
   21:44 UTC (a checkout, not landings) and the rest split into `_smoke` / `_REDUCED` / `_selftest`
   companions and real runs. **This finds five full runs that the git enumeration does not.**
3. **Tracking status of the difference.** `git ls-files --error-unmatch` on each of those five.
   **All five are UNTRACKED.** See section 4.5 -- this is a finding, not a footnote.

Then, for each cell, `metrics.json` was opened with python and its `verdict`, `verdict_msg`,
`STOP_IF_VERDICT` and decisive-margin blocks read directly. **No verdict string was trusted where
per-arm numbers were available** (that discipline exists because verdict strings are where four of
this project's corrections lived).

Retractions were enumerated from `notes/STATUS_LESSONS.md` sections titled `CORRECTIONS TO PRIOR
CLAIMS` dated 2026-08-17, plus the two that live only in `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`
sections 6.1 and 6.6.

`director_kb_query.py` and `substrate_query.sh` were NOT used, per instruction (stale).

---

## 2. HALF 1, PART A -- THE AUDIT TABLE

Read the "changed what we did next?" column strictly. The test applied is: **would a different
result have produced a different next action, and is that next action traceable on disk?** Evidence
for a YES is a plan-of-record edit, an organ status change, or a directly-descended follow-on cell.
Citation in a document is NOT evidence of a decision -- all sixteen are cited somewhere.

### The eleven the owner counted

| # | cell | the question it asked | what it varied | headline measured | changed next action? |
|---|---|---|---|---|---|
| 1 | `exp_readout_ceiling_diagnosis_v1` | is the answer even in the pool, where does it rank, what wins instead | **nothing -- a decomposition** | exact-key hit@1 0.04807 vs random-ranking 0.01009; median gold rank 37 of 5491; 0 of 29 arms CI-separated above floor 0.13896 | **YES** -- moved the diagnosis from comparator to write rule; the next four cells were all write-rule cells |
| 2 | `exp_readout_second_order_v1` | does a successor/second-order read-out clear the floor | the read-out representation | 0 arms above floor, 0 above incumbent. **But its census arm:** winner co-occurrence 0.0809 vs best-gold 0.01908 vs random anchor 0.00043 (ratio 4.24); 79.3% of winners have no close WordNet relation | **YES, but only via the census bolted onto it.** The intervention itself changed nothing |
| 3 | `exp_cue_information_audit_v1` | is the answer in the partial cue at all; does compression destroy it | compressed vs uncompressed cue | U0 vs C0 addressing **+0.0138 [+0.0083,+0.0195] ABOVE**; hit@1 unchanged | **NO (local only)** -- spawned two sibling cells, but Organ D ends CLOSED and no direction changed |
| 4 | `exp_verb_target_space_n222_v1` | can the 12-dim space order verb pairs once the sample is big enough | **the sample size, not the system** | rho 0.2607 [0.1282,0.3841]; margin over strongest floor **+0.1452 [-0.0496,+0.3379] NOT_SEPARATED**; permutation p=0.001 | **YES** -- closed correction C33, retired the n=86 number, licensed a verb-channel build |
| 5 | `exp_sparse_address_regime_switch_uncompressed_v1` | does sparse-key/dense-value help addressing | store regime | T1 vs A0 **-0.0145 BELOW**; T2 vs A0 +0.0037 NOT_SEPARATED | **NO** |
| 6 | `exp_cue_compression_property_diagnosis_v1` | WHICH property of the count cue does projection destroy | three property-isolating encoders | B1_BINARIZED_RAW **+0.0383 [+0.0293,+0.0476] ABOVE** C0, recovering 2.837x the gap | **NO (local only)** -- caused cell 8 fourteen minutes later; that cell then closed the lane |
| 7 | `exp_readout_writerule_paradigmatic_v1` | does a second-order WRITE rule clear the read-out floor | the write payload | W0 0.0223 -> W1 0.0298 (**+0.0075 ABOVE**), floor 0.13896; frequency-matched control NOT_SEPARATED | **NO** -- the only intervention in forty that moved read-out, and it still changed no plan |
| 8 | `exp_cue_binarised_readout_transfer_v1` | does the addressing gain transfer to hit@1 | nothing new -- a transfer test | addressing 0.0711 -> 0.1094; hit@1 **+0.0026 [-0.0026,+0.0078] NOT_SEPARATED** | **YES** -- "addressing and read-out are separately capped" put cue engineering on the not-doing list |
| 9 | `exp_readout_writerule_binary_profile_v1` | does binarising the STORE row transfer like binarising the cue did | store binarisation | D 0.0295 ties B 0.0298, **NOT_SEPARATED** | **NO** |
| 10 | `exp_readout_writerule_selection_axis_v1` | is SELECTION (not payload) the axis | shortlist size k = 10/30/100 | all three **NOT_SEPARATED** from P0 | **NO** -- and cell 11 pursued selection anyway 36 minutes later, which is the proof it changed nothing |
| 11 | `exp_readout_shortlist_verifier_v1` | does propose-and-reject beat the proposer | verifier architecture | shortlist oracle @k50 **0.37581**; REAL_WIN_ARMS = **[]** | **NO** -- produced the "answer is in the top 50 for 37.6% of items, our chooser takes it 11% of the time" restatement, which named no step |

### The five the "eleven" framing missed (found by the filesystem sweep; ALL UNTRACKED IN GIT)

| cell | question | headline | changed next action? |
|---|---|---|---|
| `exp_cue_regime_one_variable_v1` | how much of the cue must be the item's own key before a non-informative filler separates | `lambda_star = 0.60` -- BRIDGE_CUE_CARRIES_IDENTITY_NO | **NO** |
| `exp_cue_regime_one_variable_retrieval_v1` | same, retrieval side | `lambda_star = 0.05`; exact-key read-out still BELOW floor | **NO** |
| `exp_verb_event_salient_channel_v1` | does an affect channel lift verb similarity | A0 0.2696 -> A1 0.3705, both spoiler controls fired helpfully | **YES** (it is the one live positive; superseded by the rescore) |
| `exp_readout_independent_verifier_signals_v1` | do independent rejector signals lift the shortlist | REAL_WIN_ARMS=[]; **RULE12 orthographic/length leakage FAILED on 3 arms** | **NO** |
| `exp_readout_iterative_rejection_feedback_v1` | does iterating the reject step help | I2 0.03013 vs I0 0.04093; beats floor NO, beats null NO, ties one-shot NO | **NO** |

---

## 3. HALF 1, PART B -- THE DECISION YIELD, STATED BLUNTLY

**FOUR of the eleven changed what we did next. SEVEN did not.** Counting the five the framing
missed: **five of sixteen**, and one of those five was the verb channel, whose value was only
realised when it was RE-RUN the next day on a matched population.

That is the headline. Three further facts make it sharper, and each is uncomfortable:

**(a) Of the four that produced a decision, only ONE was a "does this change help?" experiment --
and its decision was a NEGATIVE.** Cell 8 closed a lane by showing a real gain did not transfer.
The other three were structurally something else entirely:
- Cell 1 varied **nothing**. It decomposed a fixed system into "is the answer present / where does
  it rank / what wins instead". That is a ladder with the rungs called stages.
- Cell 2's decision came from a **census bolted onto the side of the experiment**, not from the arm
  under test. The arm lost. The census (what kind of word wins, and does it co-occur) is the fact
  that has framed every day since.
- Cell 4 varied the **sample size**, not the system. It was an instrument re-measurement.

**So: eleven experiments, ten of which tested an intervention, and the interventions produced ONE
decision between them -- a negative transfer result.** Every other decision that day came from
decomposing, censusing, or re-measuring the ruler.

**(b) The seven that produced nothing were not cheap.** They carried floors, known-answer arms,
null arms, frequency-matched controls, orthographic-leakage checks, tie conventions both ways, and
paired bootstraps. **Rigour was never the missing ingredient.** We were rigorously measuring
quantities that could not distinguish anything.

**(c) The two ladders, run in the last four hours of the day, produced more direction than the
preceding eleven combined** -- and that is not rhetoric, it is countable: the pipeline ladder
relocated the ceiling upstream of the entire read pipeline and corrected the Director's stage model
from nine stages to five; the write-rule ladder localised the relation-destroying step, corrected
the write model from five steps to four, produced the first per-step composition series, and threw
up a decisive arm showing that a single sentence carries enough to clear a floor we have never
cleared.

---

## 4. HALF 1, PART C -- WHAT ACTUALLY MAKES A LADDER ACTIONABLE

"They were ladders" is the observation. Here is the mechanism, in six parts. The first three are
the load-bearing ones.

### 4.1 A ladder has NO NULL OUTCOME. This is the whole thing.

An A/B test has a two-element outcome space: {the change helped, the change did not help}. In our
regime the second outcome has a prior around 0.9 and, critically, **it names no next action.**
"Binarising the store row does not help" tells you what not to do; it does not tell you what to do.
Seven of our eleven landed there.

A ladder over k steps has an outcome space of k! orderings, and **every single one of them names a
step.** The deliverable is not "did it work" but "which part loses the most", and there is no
arrangement of the data that fails to answer that. The worst case -- all steps equal -- is itself a
strong, actionable finding ("the loss is distributed; stop hunting for one bad step"), which is
precisely what the pipeline ladder returned and precisely why it redirected the programme.

**Operational rule that falls straight out:** before authorising any experiment, write down its
outcome space and check that EVERY element of it names a next action. If any element does not, the
experiment is a coin-flip with extra steps.

### 4.2 A ladder measures a DIFFERENCE against zero, not a LEVEL against a floor. That is a real, arithmetic change in what can be detected.

This is the part that is easy to miss and it is the reason the same day produced eleven
NOT_SEPARATEDs and then four clean separations in a row.

Our accuracy levels live at 0.02-0.06. The binding floor is 0.139. **Every arm is BELOW the floor,
so "margin over floor" is negative for all of them and carries no discriminating information at
all** -- it is the same verdict for a good arm and a terrible one. Meanwhile the analytic null
half-width at our usual n=3994 is **0.02603** (read from the ladder's own POWER block), which is
larger than most of the effects we were reporting.

A ladder compares adjacent rungs **on the identical items with the identical scorer**, so the
comparison is PAIRED. Item difficulty -- which is nearly all of the variance -- cancels. Measured,
from `data/exp_writerule_step_ladder_v1/metrics.json`:

| step | drop | CI half-width | ratio |
|---|---|---|---|
| ACCUMULATE | -0.0263 | 0.0078 | 3.4x |
| CODE_PROJECT | +0.0123 | 0.0064 | 1.9x |
| NORMALISE | +0.0016 | 0.0068 | 0.24x |
| FILTER | +0.0009 | 0.0024 | 0.38x |

**The paired half-width is 0.0024-0.0078 where the unpaired one is 0.026 -- between three and ten
times tighter.** A 0.0263 effect is invisible as a level and is a 3.4-sigma result as a paired
drop. **The eleven experiments were not measuring smaller effects than the ladders. They were
measuring the same size of effect with a ruler three to ten times coarser.**

### 4.3 The oracle rung converts an unknown ceiling into a spending budget, and a budget stops work.

Replace everything downstream of a step with a perfect oracle and the accuracy you read is **the
information still recoverable at that point**. Do it at every step and the drops sum to a total.

The pipeline ladder's total loss across every processing stage is **~0.038**. Our gap to the floor
is **~0.079**. Therefore: **even if we deleted every defect in the entire pipeline we would still
fail.** That single sentence retires an unbounded class of future work -- every "better comparator",
"better shortlist", "better cue" experiment now has a KNOWN MAXIMUM PAYOFF smaller than the gap.

**No A/B can produce that.** An A/B tells you what one intervention bought. Only an oracle tells
you what ALL possible interventions at that point could ever buy. **The pipeline ladder's real
output was not a number; it was permission to stop.**

### 4.4 A ladder carries a self-check that can fail independently of the hypothesis.

Signal cannot rise as you go down a ladder -- no step creates information. If it rises, **the
ladder is leaking**, and you have found a bug rather than a result. An A/B has no analogous
internal contradiction: it cannot tell you it is broken, because any number is a legal answer.

Both ladders' single most valuable outputs were of this type, and none of them was the thing being
tested:
- The read side has **five** stages, not the nine in the Director's head ("make a context vector",
  "project it" and "superpose it" are one physical event; "find the address" and "compare
  candidates" are one cosine).
- The write side has **four** live steps, not five (superposition is the same event as coding).
- **`sign()` normalise has been OFF BY DEFAULT since 2026-08-14** -- so every headline in the arc,
  including 79.3% and 4.24x, was measured with quantisation not firing. Nobody knew.
- Organ F's ladder found a **real evaluation leak** before it contaminated anything: the held-out
  sentence sits inside the first-90 window, so reading deeper pulls the answer into the store.

**Two of two ladders found the Director's model of the machine wrong about its joints. An A/B never
asks what the joints are, so it cannot find that class of error -- it can only inherit it.**

### 4.5 What made the two ladders actionable is NOT that ladders are safe. Two defects, one of them new.

Ladders concentrate risk into a CONVENTION and a REFERENCE. Both bit us, and the second one is a
finding of this drill:

**(i) The convention.** The write-rule ladder's prose read its own `drop_point` field backwards and
announced "ONE STEP DOMINATES -- ACCUMULATE, 64% of drop mass". It was a **sign error**: -0.0263
means downstream is HIGHER, so accumulation is the biggest positive contributor, not the biggest
destroyer. The fix landed the same night (an explicit `direction_of_step_a_to_b` GAIN/LOSS/FLAT
field on every row, verified present on disk) and it is the right kind of fix -- a machine-readable
field, not more care.

**(ii) The reference. NEW FINDING, and it affects a headline currently in the plan.**
Section 6.3 of `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` states that across the ACCUMULATE step "the
share of top-1 winners that have EVER co-occurred with the query jumps 66.0% -> 94.4%", and reads
that as "unweighted summation is the operation that converts our store into a record of adjacency".

Read off `data/exp_writerule_step_ladder_v1/metrics.json`,
`report.WINNER_COMPOSITION_PER_RUNG`, the same step:

| rung | winner co-occurrence share | **best-gold co-occurrence share** | winner/gold ratio of means |
|---|---|---|---|
| R2_FILTERED_SINGLE_OCC | 0.6600 | **0.2386** | 3.967 |
| R3_FILTERED_FULL_ACCUM | 0.9443 | **0.6029** | 3.822 |

**The gold's own co-occurrence share rises by 36 points across the same step that the winner's rises
by 28.** And the ratio of means, the only within-rung contrast available, moves 3.967 -> 3.822 --
i.e. slightly the WRONG way for the claim.

The mechanism, confirmed by reading `experiments/exp_writerule_step_ladder_v1.py` lines 341-380 and
its call site at 826-860: the co-occurrence index `where` and the probe index are FIXED across
rungs (so this is not a measurement-window artifact), but `BEST_GOLD_SYNONYM` is
**`argmax` over the gold candidates under the RUNG'S OWN similarity matrix**. The reference therefore
MOVES WITH THE ARM. And the parent cell's fixed reference -- `RANDOM_ELIGIBLE_ANCHOR`, which read
0.00043 in `exp_readout_second_order_v1` -- was **dropped** when the census was ported into the
ladder.

**Consequence, stated carefully so it is not over-read.** The 66.0 -> 94.4 series is a real
measurement and it is not wrong. But **it has no rung-invariant reference**, so on its own it cannot
separate "this step biased the winners toward collocates" from "at this rung everything the system
touches, including the golds it does rank, co-occurs more". The claim in section 6.3 is
**UNCONTROLLED, not refuted.** The fix is one line of code and it is in the protocol below as GATE 4:
**a composition series must carry a reference that does not move with the rung** -- the random
eligible anchor, or the full gold set unweighted, or both. Until it is re-run, quote the composition
series as a description of the winners and not as attribution to the step.

*(This is also a small vindication of the ladder method: it is the ladder's own per-rung table that
made the defect visible. A single-arm census would have shown 94.4% with nothing to compare it to.)*

### 4.6 A ladder forces enumeration from live code, and the enumeration is itself a deliverable.

Both ladders' step lists came from reading the running code. Both corrected the Director. The
pipeline ladder even records its method in `STAGE_ENUMERATION.method` ("read
`hdlab/grounding_acquisition_loop.py`, ... and the runtime-verified encoder identity"). **An
experiment that begins by writing down the machine's actual parts cannot reason about joints the
machine does not have. An A/B begins by writing down a hypothesis, and inherits whatever model the
hypothesis came from.**

---

## 5. HALF 1, PART D -- THE RETRACTIONS, CLASSIFIED

Enumerated from `notes/STATUS_LESSONS.md` (`CORRECTIONS TO PRIOR CLAIMS`, entries dated 2026-08-17)
plus the two that live only in the plan. **The owner counted four; the disk carries six.** I list
six and mark which four are the ones most likely meant.

| # | the claim that was withdrawn | fault type | preventable by |
|---|---|---|---|
| **C32** | "0 of 7,769 banked cells meet the bar" -> **1 of 7,789**, and the survivor is itself rejected | **STALE TOOL OUTPUT QUOTED AS A FACT ABOUT THE WORLD.** The count predated wiring the constant floor in AND predated allowlist-based arm selection. "0 of N" was never a statement about the corpus; it was a statement about the checker. | **PROCESS** |
| **C33** | "our instrument cannot resolve verbs even when handed the answer" -> SUSPENDED, then MEASURED at n=222 | **UNDERPOWERED NULL READ AS A CAPABILITY STATEMENT.** At n=86 the floor it had to clear (0.1776) equalled the null distribution's own width (1.645/sqrt(85) = 0.1784). No arm of any quality separates there. | **PROCESS** |
| **C34** | "the constant/prototype floor is the binding one" -> FALSE in general (it is the WEAKEST member on two other populations, -0.1959 and -0.2253) | **A NUMBER CARRIED ACROSS SCORERS.** A floor's strength is a property of the SCORER, not of the floor: a constant ranking is strong on hit@1 (it wins whenever the gold is popular) and anti-correlated on a pair-correlation instrument. | **PROCESS** |
| **C35** | "the binding-operator choice is empirically null across two cells and six operators" -> part-wrong in three places | **A COARSE GRID'S QUANTISATION READ AS A MEASURED EQUALITY**, compounded by trusting a verdict string over the per-point data underneath it. `M_per_bank` was swept over three values; all three operators landing on the middle bucket means they landed in the same bin, not that they are equal. At the identical grid point FHRR reads 0.8000 against Hadamard 0.2889. | **PROCESS** |
| **plan 6.1** | "ONE STEP DOMINATES -- ACCUMULATE, 64% of total drop mass" -> **it is a GAIN of +0.0263, not a loss** | **SIGN / DIRECTION CONVENTION.** The cell's own prose read its `drop_point` field backwards. Two ladders difference the identical quantity and reproduce bit-for-bit; only the prose was inverted. | **PROCESS** |
| **plan 6.6** | "depth is still climbing, +0.0503 [+0.0139,+0.0861] at 128 sentences" -> **an ORACLE-CUE number quoted at the operating point**; on the real partial cue every step is NOT_SEPARATED or BELOW | **REGIME CROSSING.** An exact-key/oracle measurement quoted as an operating-point lever. The project already had a standing rule against exactly this (standing discipline 12) and the Director broke it twice in one relay. | **PROCESS** |

**The four the owner most likely means** are C32, the sign error, the oracle-cue retraction, and one
of C33/C35 -- the description "an oracle-cue figure quoted as an operating-point lever TWICE, and a
sign error that inverted a headline" matches rows 5 and 6 exactly.

### The classification that matters: how many are preventable by PROCESS?

**All six.** Not one is a "should have been more careful" fault. That is a strong and slightly
surprising result, and it is good news, because a care-preventable fault will recur forever and a
process-preventable fault gets a mechanism. Here is the mechanism for each, and three of the six
already have theirs:

| fault | mechanism | status |
|---|---|---|
| stale tool output (C32) | every scan output carries the tool's commit hash and the timestamp of the last change to any file it depends on; a report older than its dependencies is refused, not quoted | **NOT BUILT** -- proposed as GATE 1c below |
| underpowered null (C33) | **pre-flight margin power check** -- see section 7.3. Compute the MARGIN's null half-width at the planned n BEFORE running; if it exceeds the action threshold, do not run | **NOT BUILT** -- this is the single highest-value mechanism in this note |
| number carried across scorers (C34) | `floor_battery.py` already recomputes all four floors on the caller's population; what is missing is a REFUSAL -- a floor value loaded from anywhere but the current population should raise | **HALF BUILT** (`tools/floor_battery.py` exists; the refusal does not) |
| coarse grid read as equality (C35) | any sweep must report its **grid resolution** beside its verdict, and a verdict of "invariant" is refused when the claimed effect is smaller than one grid step | **NOT BUILT** -- GATE 3d below |
| sign inversion (plan 6.1) | machine-readable `direction_of_step_a_to_b` on every drop row, and prose generated from the field rather than written beside it | **BUILT 2026-08-17**, verified present on disk |
| regime crossing (plan 6.6) | every reported number carries a `cue_regime` tag (`ORACLE_EXACT_KEY` / `REAL_PARTIAL_CUE`), and a cross-regime comparison is refused | **NOT BUILT** -- GATE 1d below |

**And one fault class the six do not cover, found by this drill: FIVE FULL EXPERIMENT RUNS FROM
2026-08-17 WERE NEVER COMMITTED TO GIT** (`exp_cue_regime_one_variable_v1`,
`exp_cue_regime_one_variable_retrieval_v1`, `exp_readout_independent_verifier_signals_v1`,
`exp_readout_iterative_rejection_feedback_v1`, `exp_verb_event_salient_channel_v1` -- all confirmed
UNTRACKED by `git ls-files --error-unmatch`). Two of them carry results the plan cites. One of them
(`exp_readout_independent_verifier_signals_v1`) records **RULE12 orthographic/length leakage
FAILURES on three arms**, which is a safety-relevant negative sitting outside version control.
**A result that is not committed is a result that the next compaction deletes.** Mechanism: the
landing check should assert tracked-ness, not just existence. This costs nothing and it is the
cheapest item in this note.

---

## 6. HALF 2, PART A -- HOW THE RELEVANT FIELDS ESTABLISH REPRESENTATIONAL CONTENT

Our question -- **does this store encode "could replace" (substitutability) or "appears near"
(co-occurrence)?** -- is not an accuracy question. It is a question about what a representation
CONTAINS. Four communities ask that question professionally. Each has a standard method, each has a
known failure mode, and the failure modes are the useful part.

Calibration statement, applied throughout: **MEASURED** = someone ran it and reported numbers;
**MODELLED** = derived analytically or in simulation; **MERELY POPULAR** = widely used, thinly
validated. Literature-scan probability estimates below are deflated by 0.15-0.25 per standing rule,
and no novel-synthesis estimate exceeds 0.50.

### 6.1 Representational similarity analysis (RSA) -- comparing similarity structures, not items

**The method.** Instead of decoding a label from a representation, you compute the representation's
own matrix of pairwise dissimilarities (an RDM) over a fixed set of items, do the same for a
HYPOTHESIS (e.g. "these two words are substitutable"), and correlate the two matrices. Introduced
in neuroscience by Kriegeskorte and colleagues; it is now the default way of asking "does this
system's geometry look like that one's".

**Why it fits us better than accuracy.** Accuracy reads one point (the argmax). An RDM over n items
uses n(n-1)/2 cells. For a 5,000-item pool that is over twelve million pairwise comparisons instead
of 5,000 argmaxes. **The power difference is not marginal; it is orders of magnitude** -- and power
is exactly what our eleven experiments lacked.

**What it controls for, when done properly (MEASURED practice):**
- a **noise ceiling** -- the highest correlation any model could achieve given the reliability of
  the hypothesis itself. Computed by leave-one-out over annotators/subjects: compare each held-out
  RDM to the average of the rest (lower bound) and to the average of all (upper bound). **We already
  do the analogous thing** -- the verb rescore quotes A1 at "~61% of achievable" against SimVerb's
  own inter-annotator agreement of 0.6121. That is a noise ceiling under another name.
- **cross-validated / unbiased distance estimators**, because a naive squared distance is biased
  upward by noise (the crossnobis / whitened-unbiased-distance family).
- **inference that generalises to new ITEMS, not just new subjects** -- a two-factor bootstrap.
  Schuett et al., *Statistical inference on representational geometries* (eLife 2023) is the current
  reference; it also reports that older fixed-model inference can be "severely suboptimal in terms
  of statistical power".

**Its known failure modes, and they land directly on us:**
- **The mimic effect.** Confounds in the stimulus set can produce high RSA scores between systems
  that are provably dissimilar. Because RSA is a second-order statistic -- a similarity of
  similarities -- **it is ambiguous which stimulus features drove the geometry.** Two systems
  operating on entirely different features can have highly correlated RDMs.
- **The modulation effect.** The score depends on which stimuli you happened to test with.
- **Hierarchically structured datasets make second-order confounds not merely possible but
  plausible.** (These three from the Dujmovic/Bowers-line critique, *Obstacles to inferring
  mechanistic similarity using RSA*, bioRxiv 2022.)
- **Correlated candidate models are the hard case.** Variance partitioning can split two hypotheses
  into unique-A, unique-B and shared, but where the two hypotheses are themselves correlated, "less
  overlap" and "stronger suppression" are not distinguishable. **Substitutability and co-occurrence
  ARE correlated in text** -- synonyms do sometimes co-occur -- so this caveat is ours.

**Verdict: adopt the instrument, do NOT adopt it as the primary.** RSA gives the power we need and a
noise ceiling we already understand. But its central weakness -- you cannot tell which feature drove
the geometry -- is *precisely our open question*. Using RSA alone to settle "substitutability vs
co-occurrence" would be using the tool at the exact point the literature says it is ambiguous.
P(a partial-correlation RSA alone cleanly separates our two relations) **~0.25**.

### 6.2 Diagnostic probing, and the probe-strength confound

**The problem, stated exactly.** Train a classifier to read property P out of a representation. High
accuracy gets read as "P is encoded". But a strong enough probe can learn P from almost anything --
**above-chance probing accuracy has been demonstrated for properties that are linguistically
meaningless noise.** So "the information is present" is not well-defined without saying how hard the
probe was allowed to work.

**The accepted control: CONTROL TASKS and SELECTIVITY** (Hewitt & Liang, *Designing and Interpreting
Probes with Control Tasks*, EMNLP 2019). Build a control task by assigning each word type a RANDOM
output. By construction that task can only be learned by the probe memorising -- the representation
cannot help. Then:

> **selectivity = (accuracy on the real task) - (accuracy on the control task)**

A trustworthy probe has high real accuracy AND low control accuracy. **MEASURED findings:** popular
probe designs turn out to have high control-task accuracy and hence low selectivity; linear probes
tend to be selective, non-linear ones tend not to be; dropout does not fix it, other regularisation
does.

**Why this matters to us more than it looks.** We do not train probes -- but we do the same thing in
different clothes every time we add a channel. A channel that "helps" may help because the channel
is expressive, not because the representation contains the relation. **Our four-floor bar is already
a selectivity construct** (a floor is a policy that could produce the answer without understanding;
the margin over it is selectivity by another name). The piece we lack is the random-label control
specifically: **a channel run against a SCRAMBLED version of the very relation it claims to encode.**

**And the owner has independently arrived at the same control.** Plan section 6.8, on the word-onset
channel: *"only applicable to some words"*, therefore *"a genuine morphological channel helps on
`unhelpful`/`unhealthy` and does NOTHING on words whose opening letters carry no morpheme; a
LETTER-MATCHING channel helps on BOTH equally. A uniform gain across both strata is a FAILURE."*
**That is selectivity, invented from first principles and stated in plain English.** It is the
strongest argument in this note for formalising the concept: our owner already reasons this way and
our protocol does not yet require it.

### 6.3 What is ENCODED versus what is USED -- causal intervention

**The distinction.** Probing (and RSA) show information can be EXTRACTED. Neither shows the system
USES it. The standard modern move is to intervene: remove or alter the feature and see whether
behaviour moves.

**Amnesic probing** (Elazar, Ravfogel et al., TACL 2021) removes all information linearly predictive
of a target property (iterative nullspace projection, INLP) and measures the effect on downstream
behaviour. **Known weakness, MEASURED:** INLP damages more than the target -- it introduces
collateral random modification -- so later work replaces it with mean projection or LEACE (Findings
of ACL 2025) to make the intervention surgical.

**How this maps onto us, and it maps cleanly.** Our oracle rungs already ARE causal interventions of
the strongest possible kind: replace a stage with a perfect version and see whether behaviour moves.
**We are, without having named it, doing the thing the interpretability field regards as the gold
standard, and doing it in a stronger form than they can** -- they must approximate a perfect feature
by projection; we can literally substitute the true answer. The gap is that we do it for STAGES and
never for CONTENT. We have never run "delete the co-occurrence signal from the store and watch what
happens to the winners", which is the exact analogue of amnesic probing and is a designable cell.

**And the encoded/used split is already the programme's most important result, unlabelled.** The
write-rule ladder's decisive arm: `BEST_SINGLE_ORACLE` reads **0.3033** (one well-chosen occurrence
of the target), `SUM_ALL` reads **0.0100**, `RANDOM_SINGLE` reads **0.0367**. The information IS
ENCODED in individual sentences and IS NOT USED by our averaging. **That is an encoded-vs-used
finding, not an accuracy finding, and it is the strongest thing we own.** (It is a CEILING
DIAGNOSTIC -- it consults the answer when choosing the occurrence -- and must never be quoted as a
capability.)

### 6.4 Distributional semantics' own literature on syntagmatic vs paradigmatic -- our exact failure, already named

The closest match to our problem, and the field named it decades ago. The terms are Saussure's; the
vector-space treatment is Sahlgren's *The Word-Space Model* (2006).

- **Syntagmatic** = words that occur TOGETHER (first-order co-occurrence): `bread`-`knife`,
  `absence`-`presence`. **Our store.**
- **Paradigmatic** = words that occur in the SAME KIND OF COMPANY, i.e. can substitute (second-order
  co-occurrence -- similar NEIGHBOURS, not shared occurrence). **Our task.**

**What the field MEASURED about how to get from one to the other:**
- **Context window size is the primary lever.** Narrow windows (adjacency) yield collocations; wide
  windows (roughly +/-10 words) yield paradigmatic relations -- synonymy, antonymy, hyponymy,
  meronymy. Repeatedly replicated as a parameter finding.
- **Second-order CONSTRUCTION is the structural lever.** You do not compare targets directly; you
  compare their CONTEXT PROFILES. SOC-PMI (Islam & Inkpen, LREC 2006) makes this explicit: score two
  words by the PMI-weighted overlap of their NEIGHBOUR SETS, never by their direct co-occurrence.
  There is a MEASURED note that plain PPMI is sensitive to first-order overlap and **not at all to
  second-order overlap** -- the weighting alone does not convert the relation; the construction does.
- **PPMI weighting suppresses frequency-driven collocates.** A word that co-occurs with everything
  has low association with anything. Directly on target for our finding that the winners are
  collocates co-occurring 4.24x more than the right answer.
- **The benchmark community built a dataset specifically to break this confound.** SimLex-999 (Hill,
  Reichart & Korhonen) exists because WordSim-353 and MEN conflate similarity with association --
  `clothes`-`closet` rates high on relatedness while being ontologically dissimilar. **The
  recognised fix for "my scores are driven by association, not similarity" is to build a stimulus
  set that DISSOCIATES them.** That is the move I recommend we copy, and it is section 8.3.

**Honest caveat we must carry, because it deflates the obvious next step.** We have ALREADY run a
second-order write rule (`exp_readout_writerule_paradigmatic_v1`, +0.0075) and a second-order
read-out (`exp_readout_second_order_v1`, lost outright). **"Just go second-order" is already measured
here and it is not the answer.** What we have NOT done: vary the WINDOW (we build from a sentence,
which is narrow by this literature's standard), and apply ASSOCIATION WEIGHTING inside the write rule
-- our accumulation is an UNWEIGHTED sum, the one construction this literature says will be dominated
by frequent collocates. P(a PPMI-weighted or window-widened write rule produces a CI-separated
composition shift) **~0.45**; P(it clears the binding floor on hit@1) **~0.15**. Those two must never
be conflated, and section 8 explains why the first is the one to gate on.

### 6.5 Effect sizes and power for this class

- **RSA correlations are routinely SMALL in absolute terms and that is normal.** Reported ranges in
  the model-comparison literature run roughly 0.10-0.43 with means near 0.26; ERP-based RSA
  correlations are often below 0.10 and still treated as real, because the noise ceiling is itself
  low. **The field reports the number AS A FRACTION OF THE NOISE CEILING, not raw.** Our verb result
  is already reported that way (A1 at ~61% of the 0.6121 ceiling). That is the right habit and it
  should become mandatory.
- **Power comes from the number of PAIRS, not the number of ITEMS.** A 50x50 RDM has 1,225 cells in
  its lower triangle. This is why that field reports 0.15 correlations confidently while we cannot
  report a 0.02 accuracy difference confidently: our instrument throws the pairs away.
- **Paired designs are the standard in NLP evaluation**, for the variance-cancelling reason above
  (paired bootstrap, typically 10,000 resamples; Koehn 2004 is the usual citation). We already do
  10,000-draw paired bootstraps -- good. **The gap is that we pair ACROSS ARMS while scoring with an
  instrument that has no pairs WITHIN an item.**
- **Minimum detectable effect (MDE) is the standard planning quantity and we have never computed
  one.** At 80% power, alpha 0.05, unpaired: n ~= 2*(1.96+0.84)^2*p(1-p)/delta^2. At our p ~= 0.05
  and n = 3,994 per arm the unpaired MDE is about **0.019** -- LARGER than eight of the eleven
  effects reported that day. Paired, at the between-rung correlation our ladders actually show, the
  MDE falls to roughly **0.005**. **Switching from unpaired levels to paired differences buys about
  a factor of four in detectable effect and costs nothing.** (MODELLED, from the standard formula;
  the paired figure is consistent with the 0.0024-0.0078 half-widths measured in the ladder.)

### 6.6 What to take and what to leave

| from | TAKE | LEAVE |
|---|---|---|
| RSA | the pair-level instrument (power); the noise ceiling as denominator; variance partitioning as a SECONDARY | RSA-correlation-alone as a content claim -- the mimic effect is exactly our ambiguity |
| probing | **selectivity: a channel must FAIL where it should**; the scrambled-relation control | trained probes themselves -- they would import a learned component into a glass-box substrate |
| causal intervention | we already own the strongest version (oracle rungs); extend it from STAGES to CONTENT | INLP/LEACE machinery -- overkill for a linear store we can edit directly |
| syntagmatic/paradigmatic | **the dissociating stimulus set** (the SimLex move); window size as a swept parameter; association weighting inside the write rule | "second-order fixes it" -- already measured here at +0.0075 |
| power | MDE computed BEFORE the run, on the MARGIN and not on the arm | nothing |

---

## 7. THE PROTOCOL -- **OGL-1, THE ORGAN GATE LADDER**

**Scope: ONE organ. Nothing else is touched until every gate has a verdict.** Nine gates, numbered
0 to 8, in order. Each gate states WHAT TO MEASURE, WHAT CONTROL TRAVELS WITH IT, WHAT MAKES IT PASS
OR FAIL, and WHAT TO DO ON EACH OUTCOME. A subagent can execute this without judgement calls.

**Three rules that hold at every gate:**
- **ONE population, ONE scorer, ONE gold, ONE cue regime, across every rung and every arm.** A
  number that cannot be produced on the common population is reported UNMEASURABLE. It is never
  imported.
- **Every margin is reported with its CI half-width and the null p95 at that n, beside it.** A width
  is not an effect.
- **NOT_SEPARATED is not a result.** It is either FAIL (the design was powered and the effect is
  absent) or UNMEASURED (the design was not powered). Gate 0 decides which, in advance.

### GATE 0 -- PRE-FLIGHT POWER. *Run before writing any experiment code.*

**Measure:** (a) **A, the action threshold** -- the smallest effect that would change what we do
next. Written down as a number, in the scorer's units, before anything else. Not the effect you
hope for: the effect below which you would take the same action anyway. (b) **MDE_margin** -- the
half-width of the MARGIN's null at the planned n, obtained by drawing two arms from the same item
set under the null (permutation), forming the margin, and paired-bootstrapping it.

**Control:** MDE must be computed **on the MARGIN, not on either arm.** The margin's interval is
wider than either endpoint's because both are estimated. *This is how C33 happened: at n=222 the arm
half-width was 0.128 and looked adequate, while the margin half-width was 0.194 and was not.*

**PASS:** `MDE_margin < A`. **FAIL:** `MDE_margin >= A`.

**On FAIL, the three legal responses and no others:** (1) raise n until it passes; (2) change the
SCORER to one with a smaller MDE -- an item-level argmax throws away pairs, a pair-level instrument
keeps them, and that is usually worth a factor of ten; (3) do not run the experiment. **Widening the
band is not on the list.** Record `A`, `MDE_margin` and the choice in the pre-registration.

**Why this gate is first:** three of our six retractions were an underpowered design read as a
capability statement. This is the only gate that prevents that class, and it costs minutes.

### GATE 1 -- ENUMERATE THE STEPS FROM LIVE CODE

**Measure:** the ordered list of steps that PHYSICALLY happen when the organ runs, each with the
`file.py::function` that implements it. Runtime evidence, not grep -- lazy imports inside function
bodies are invisible to static search, and comments read as imports. Record the method string in
`metrics.json` (the pipeline ladder's `STAGE_ENUMERATION.method` is the model).

**Control:** diff the list against the Director's written sketch. **Record the diff explicitly.**

**PASS:** every step has a named implementing function. **FAIL:** a step with no implementing
function is not a step -- delete it and re-diff.

**On either outcome, the diff is a deliverable.** Two of two ladders found the sketch wrong (read
side 9 -> 5, write side 5 -> 4). **Expect to be wrong; the correction is a result.**

### GATE 2 -- INSTRUMENT LICENCE. *Four sub-gates. Nothing below is interpretable until all four pass.*

- **2a KNOWN-ANSWER arm.** Hand the system the answer. It must read at the instrument's declared
  maximum (our exact-key arms read 1.0). **FAIL -> the instrument is broken; stop, fix, restart.**
- **2b NULL arm.** Permute the cue or the labels. Must read at chance. **FAIL -> leakage; stop.**
- **2c PROVENANCE.** Every input asset carries the commit hash of the tool that produced it and a
  timestamp not older than any file it depends on. **A report older than its dependencies is
  REFUSED, not quoted.** *(This is the C32 mechanism: "0 of 7,769" was a statement about a stale
  checker, not about the corpus.)*
- **2d REGIME TAG.** Every number the cell will emit is tagged `ORACLE_EXACT_KEY` or
  `REAL_PARTIAL_CUE`. A comparison across tags is refused by the code, not by the reader. *(This is
  the mechanism for the depth retraction: an oracle-cue figure was relayed as an operating-point
  lever, twice.)*

### GATE 3 -- FLOORS AND WIDTHS, ON THIS POPULATION AND NO OTHER

**Measure:** all four floors -- orthographic, frequency-hardened, scramble/permutation, and
constant/prototype -- via `tools/floor_battery.py`, on this exact population, in **both tie
conventions**. Report the binding floor (the max), its value, its CI, and the null p95 at this n.

**Control:** `floor_battery.pool_admits_a_winning_constant` on the candidate pool, and
`oracle_constant_scores` reported as a CEILING OF THE CONSTANT FAMILY, always labelled ORACLE.

**PASS:** four floors computed here, none imported. **FAIL:** any floor value loaded from another
population -> stop. *(C34: a floor's strength is a property of the SCORER. The constant floor is the
strongest member on hit@1 at 0.1390 and the WEAKEST member on a pair-correlation instrument at
-0.1959. Never carry 0.1382, 0.2070 or -0.1959 anywhere.)*

### GATE 4 -- THE ORACLE LADDER. *This is the measuring instrument, not a test of a hypothesis.*

**Measure, one rung per step, everything downstream replaced by a perfect oracle:**
- **SIGNAL** -- oracle-downstream accuracy at that rung.
- **SEPARATION** -- the correct item against the competing field, in units of that field's own
  spread. *A step can preserve the signal and collapse the separation. Those are different failures
  needing different fixes, and reporting accuracy alone hides the distinction.*
- **RANK** -- where the correct answer sits in the full ordering, against random-ranking expectation
  on the same population.

**Then:**
- **4a RANKED DROP TABLE**, with a **PAIRED CI on each DROP** (not on the endpoints), and an explicit
  machine-written `direction_of_step_a_to_b` = GAIN / LOSS / FLAT on every row. **Prose is generated
  from that field, never written beside it.** *(The sign-error mechanism, already built.)*
- **4b GRID RESOLUTION disclosure.** If a rung is a swept parameter, report the grid spacing. **A
  verdict of "no difference" is REFUSED when the claimed effect is smaller than one grid step.**
  *(C35: three operators landing in the same bucket of a three-bucket sweep was reported as
  "invariant"; at the identical grid point FHRR reads 0.8000 against Hadamard 0.2889.)*
- **4c MONOTONICITY ASSERTION.** Signal cannot rise going down the ladder; no step creates
  information. **If it rises, the ladder has a leak. Report the leak, not the ladder.** This matters
  more than any number the ladder produces -- Organ F's ladder caught a real held-out evaluation leak
  this way before it contaminated anything.

**PASS:** monotone, every drop paired-CI'd, a ranking produced. **FAIL (leak):** the leak is the
result; fix and re-run. **The ranking is the deliverable and there is no null outcome.**

### GATE 5 -- THE CONTENT GATE. *The new primary. Full definition in section 8.*

**Measure, at EVERY rung, on the SAME paired probe items:**
- the **DISSOCIATION SCORE** (section 8) -- does this rung rank substitutes-that-never-co-occur above
  collocates-that-cannot-substitute?
- the **WINNER COMPOSITION** -- fraction of top-1 winners with a close WordNet relation, and their
  co-occurrence share.

**Controls -- all three mandatory, and the first is the one we just found missing:**
1. **A RUNG-INVARIANT REFERENCE.** The random eligible anchor (fixed, read 0.00043 in
   `exp_readout_second_order_v1`) AND the FULL gold set unweighted. **Never the argmax-gold, which is
   selected by the rung's own scorer and therefore moves with the arm** -- section 4.5.
2. **A pure co-occurrence-count system**, scored identically. This pins what "maximally syntagmatic"
   looks like on this population, so the scale has a known worst end.
3. **A WordNet-derived system**, scored identically, labelled ORACLE. This pins the best end.

**PASS at a step:** the dissociation score moves CI-separated across that step, with the invariant
reference flat. **FAIL:** flat, or moves only in the same direction as the reference.

**Actions, and this is the gate that changes what we build:**
- **Content moves, accuracy flat -> THIS IS THE BUILD TARGET.** Accuracy is pinned to the floor in
  our regime and cannot see it.
- **Accuracy moves, content flat -> NOT a relation fix.** Record as an efficiency or capacity change
  and do not build a programme on it.
- **Both flat -> the step does not touch the relation.** Remove it from the organ's candidate list.

### GATE 6 -- SELECTIVITY. *Does the effect FAIL where it should?*

**Measure:** define, from the mechanism's OWN theory, the stratum where it CANNOT apply. Re-run the
winning arm there.

**Control:** the two strata must be matched on frequency and length, and the comparison between them
must be CI-separated, not just individually banded.

**PASS:** gain on the applicable stratum, NOT_SEPARATED on the inapplicable one, and the two
CI-separated from each other. **FAIL:** a uniform gain across both.

**A uniform gain is a FAILURE under standing rule 12, not a win** -- it means something generic
(capacity, expressivity, spelling overlap) produced it. The owner's morphology example is the
template: `un-` and `con-` carry meaning, `str-` does not, and a real morphological channel must be
silent on the second group. **Any channel that fires on every item is, by construction, not the
channel it claims to be.**

### GATE 7 -- CAUSAL. *Encoded is not the same as used.*

**Measure:** for the step Gate 5 named, ABLATE the content it is accused of carrying -- zero or
whiten the co-occurrence component, or substitute the best-single-occurrence oracle -- and re-read
behaviour.

**Control:** a **matched-magnitude RANDOM ablation.** Remove an equal amount of variance from a
random direction. *(This is the LEACE lesson: INLP's collateral damage means an intervention that
damages more than its target proves nothing.)*

**PASS:** behaviour moves for the targeted ablation and NOT for the matched-random one, CI-separated
from each other. **FAIL:** both move equally -> the intervention is not surgical and the claim is
unsupported.

### GATE 8 -- BUDGET. *Run this before authorising any build.*

**Measure:** `total_measured_loss` = sum of the ladder's step losses. `gap` = binding floor minus the
best rung's signal. `budget_remaining = gap - total_measured_loss`.

**Branch, and both branches are decisions:**
- **`total_measured_loss < gap` -> THE CEILING IS UPSTREAM OF THIS ORGAN.** Say so, stop working on
  the organ, and name the upstream organ. *(This is exactly what the pipeline ladder returned: total
  loss ~0.038 against a gap of ~0.079. It retired an unbounded class of downstream work.)*
- **`total_measured_loss >= gap` -> the ceiling is inside.** The top-ranked step is the build target.

**EXIT -- WIRE OR SHELVE.** On a PASS chain, promote to `hdlab/`, register in
`data/capability_registry.jsonl`, add the runtime witness. On a FAIL chain, write the revival
criterion in **BRAIN terms, never performance terms** ("revive when a CA3-style separation stage
exists", not "revive if accuracy improves").

---

## 8. THE MEASUREMENT THAT SHOULD REPLACE END-TASK ACCURACY

### 8.1 Why end-task accuracy has to go as the primary

Not because it is wrong -- because on this problem it is **blind, coarse and slow**, all three
measurable:

- **Blind.** It reads the argmax and discards the rest of the ordering. Our best diagnostic fact --
  that the gold sits at median rank 37 of 5,491 and inside the top 100 for 68.6% of items -- is
  invisible to it.
- **Coarse.** Unpaired MDE at our n and p is about 0.019; eight of the eleven effects that day were
  smaller than that. **The ruler's smallest tick was bigger than the things being measured.**
- **Slow to decide.** Every arm sits BELOW the binding floor of 0.139, so "margin over floor" returns
  the same verdict for a good arm and a hopeless one. **A measurement that returns the same value
  over the whole range you actually occupy is not a measurement.**

### 8.2 Is WINNER COMPOSITION the right primary? Partly. It is the right CONFIRMATION, not the right PRIMARY.

**What is right about it, and it is a lot.** It reads the RELATION directly rather than through a
proxy, and its effects are an order of magnitude larger than accuracy's. Across the ACCUMULATE step:
accuracy moves 0.0263 against a half-width of 0.0078 (3.4 sigma); the winner co-occurrence share
moves 0.284 against a binomial half-width near 0.035 at n=700 (about 8 sigma). **It caught a step
that accuracy alone could not see. That is exactly the property we need.**

**Three reasons it should not be the PRIMARY:**
1. **As run, it has no rung-invariant reference** (section 4.5). Its published headline moves 28
   points while its own reference moves 36 in the same direction. That is fixable in one line, and
   it must be fixed, but it means the measure as it stands cannot attribute a change to a step.
2. **It is still an argmax measure.** It reads only the winner, so it inherits accuracy's blindness
   -- and it is capped at the probe size (n=700 in the ladder) rather than the population size, which
   throws away most of the available power.
3. **It is DESCRIPTIVE, not CONTRASTIVE.** "94% of winners co-occur" is a fact about winners; it is
   not, by itself, an answer to "does the store encode substitutability rather than co-occurrence",
   because a store that encoded substitutability perfectly would still have SOME co-occurring
   winners (synonyms do co-occur).

### 8.3 THE RECOMMENDED PRIMARY: **THE DISSOCIATION SCORE**

**The idea in one sentence:** build two small sets of word pairs chosen so that the two relations
point in OPPOSITE directions, and ask which set the store scores higher. **The sign of the answer is
the answer to our central question.**

**Construction** (no new data required -- WordNet and our own corpus co-occurrence index are enough):
- **Cell P (paradigmatic, not syntagmatic):** pairs with a close WordNet relation whose corpus
  co-occurrence is **zero, or in the bottom decile**. Substitutable words that never appear together.
- **Cell S (syntagmatic, not paradigmatic):** pairs in the **top decile of corpus co-occurrence**
  with **no close WordNet relation**. Words that always appear together and cannot replace each
  other. `absence`->`presence` and `abnormality`->`chromosomal`, from our own winner census, are
  exactly this shape.
- **Match the two cells on** unigram frequency, word length, and part of speech, so no floor can
  separate them. Report the match quality.

**The score:** the store's own similarity for every pair in both cells; the headline is the
**rank-separation (AUC) of Cell P over Cell S**, with a paired bootstrap CI.

- **AUC > 0.5, CI-separated: the store encodes substitutability.**
- **AUC < 0.5, CI-separated: the store encodes co-occurrence.** *(This is where I expect us to land.
  P ~0.75 that our incumbent store scores CI-separated BELOW 0.5. If it does not, the syntagmatic
  diagnosis that has driven the last two days is weaker than we think, and that is worth knowing on
  its own.)*
- **NOT_SEPARATED: the store encodes neither, which is a third and distinct diagnosis** we currently
  cannot state at all.

**Its controls, and they pin the whole scale:**
- **A pure co-occurrence-count system** scored identically -> defines the bottom of the scale.
- **A WordNet-derived system** scored identically, labelled ORACLE -> defines the top.
- **The four floors** recomputed on this pair set -> by construction none of them can separate the
  two cells, because the cells are frequency- and length-matched. **If a floor DOES separate them,
  the stimulus set is broken and must be rebuilt.** That check is the analogue of Hewitt & Liang's
  control task, and it is cheap.
- **A scrambled-relation arm** (WordNet labels permuted across pairs) -> must read AUC 0.5.

**Why it beats both accuracy and raw composition, point by point:**

| property | end-task accuracy | winner composition | **dissociation score** |
|---|---|---|---|
| answers "X or Y?" directly | no -- proxy | partly -- descriptive | **yes -- it is literally the quantity** |
| uses the whole ordering | no (argmax) | no (argmax) | **yes (all pairs)** |
| has a rung-invariant reference | n/a | **no, as run** | **yes, by construction** |
| can move while accuracy is floor-pinned | n/a | yes | **yes** |
| effect size available | ~0.02 | ~0.28 | **AUC gaps of 0.2-0.4 are the expected scale** |
| confounded by frequency | yes | yes | **no -- matched by construction** |
| a floor can fake it | **yes (constant floor 0.139)** | partly | **no -- matched cells defeat constant, frequency and orthographic floors simultaneously** |

**That last row is the strongest argument and it deserves saying plainly.** The reason we can never
clear the binding floor is that a machine which always answers the same popular word scores 0.139 on
our pool. **On a matched two-cell design, that machine scores AUC 0.5 by construction** -- it cannot
prefer Cell P over Cell S because the cells are matched on everything it uses. **The dissociation
score is an instrument on which our floors are automatically at chance, which is what a floor is
supposed to be.** We have been fighting a floor that is strong for a reason unrelated to our
question.

**And it is brain-framed rather than tool-framed.** The claim under test is that neocortex extracts
cross-episode REGULARITIES while hippocampus keeps the EPISODE -- adjacency is episodic,
substitutability is the regularity. **Cell S is the episodic content; Cell P is the regularity.** A
cortical write rule must rank P over S. That is the organ's own metric, in the brain's terms, and it
is measurable tomorrow.

### 8.4 The full primary/secondary stack, as it should appear in every cell

1. **PRIMARY: dissociation score (AUC of Cell P over Cell S)**, per rung, with its four controls.
2. **CONFIRMATORY: winner composition, with a rung-invariant reference.** Behavioural -- what
   actually wins. Primary and confirmatory must move TOGETHER; if the geometry moves and the winners
   do not, the information is encoded and not used, and that is a Gate 7 question.
3. **SECONDARY: RSA partial correlation / variance partition** -- unique-paradigmatic,
   unique-syntagmatic, shared -- **reporting the correlation between the two hypothesis matrices on
   our own population**, so the reader knows how hard the separation was. Secondary, not primary,
   because of the mimic effect.
4. **REPORTED, NEVER GATED ON: end-task hit@1**, with its four floors. It stays because it is the
   thing we ultimately want. It stops being the thing we steer by.

---

## 9. THE STOPPING RULES

### 9.1 Telling an underpowered null from a real one -- BEFORE the run, not after

**The test, in one line:**

> **Compute the half-width of the MARGIN's null at the planned n. If it is larger than the smallest
> effect that would change what you do next, the experiment cannot produce an answer. Do not run it.**

That is Gate 0. Three details make it work rather than merely sound good:

**(a) Power the MARGIN, never the ARM.** The margin's interval is wider than either endpoint's,
because both endpoints are estimated. **MEASURED, from `exp_verb_target_space_n222_v1`:** the arm's
bootstrap half-width was **0.128**, which looks adequate against a required margin of 0.145; the
MARGIN's interval was [-0.0496, +0.3379], half-width **0.194**, which is not. **The design looked
powered and was not, and the difference between those two numbers is the entire retraction.**

**(b) The "floor equals the null width" check is necessary but NOT sufficient -- do not stop there.**
The identity `scramble_p95 ~= 1.645/sqrt(n-1)` is what exposed C33: at n=86 the floor was 0.1776
against a predicted 0.1784. **But the same ratio holds at n=222** (measured 0.1152 against predicted
0.1107, ratio 1.04) and that design still failed. **The ratio being near 1.0 is normal and is not
the diagnostic.** The diagnostic is the ABSOLUTE size of the margin's half-width against `A`. Anyone
using the ratio alone will mis-license the next verb-scale design exactly as we did.

**(c) Write `A` down first, in the scorer's own units, and justify it as an ACTION.** Not "we hope
for +0.05" but "below +0.03 we would build the same thing anyway, so +0.03 is A". If you cannot name
an action that turns on the number, the experiment has no decision to produce and Gate 0 fails for a
different reason.

**Retrospective check that this test would have worked:** applied to the eleven, Gate 0 fails
immediately for cells 5, 7, 8, 9, 10 -- all reported effects at or below the unpaired MDE of ~0.019
on the same scorer and n. **Five of the seven no-decision experiments would not have been run.**
Cells 3 and 6 pass Gate 0 (+0.0138 and +0.0383 are above MDE) and both produced real, reproducible
measurements -- they fail a different gate, Gate 8, because their effects were smaller than the
budget they were spending against.

### 9.2 When an ORGAN is finished

**All four must hold. Any one missing means it is not finished.**
1. **Every enumerated step has a verdict that is PASS or FAIL -- never NOT_SEPARATED.** A
   NOT_SEPARATED whose Gate 0 was not satisfied is UNMEASURED, and an organ with an unmeasured step
   is not finished. Say "unmeasured", never "saturated" and never "no effect".
2. **Gate 8 has produced a budget number.**
3. **RECONCILIATION: the sum of the measured step losses agrees with the organ's total loss to
   within the CI.** If it does not, a step is missing from the enumeration -- go back to Gate 1.
   *This is a genuine self-check and we have never run it; the two ladders happened to reconcile
   bit-for-bit, which is why the sign error was catchable.*
4. **Gate 5 has named at least one step where the CONTENT moves, or has established that NO step
   does.** Both are finished states. The second one is the more valuable and the more likely.

### 9.3 When a DIRECTION is dead

**Any one of these three, and only these three:**
1. **The oracle rung that deletes the step ENTIRELY still fails to clear the binding floor.** The
   step is not the ceiling. No implementation of it can be.
2. **Content is flat at every rung, with Gate 0 satisfied at every rung.** The organ does not touch
   the relation. *(Organ F's deep ladder is exactly this: no-relation rate 0.8235 and winner
   co-occurrence 0.00215 CONSTANT across D=1..768. Depth changes neither the score nor the kind of
   word that wins. That is a properly dead direction, and it is dead on CONTENT evidence, not on
   accuracy evidence -- which is the best available demonstration that the content gate is the right
   primary.)*
3. **The step's own ceiling diagnostic -- the best achievable choice within the step, consulting the
   answer -- reads BELOW the binding floor.** If cheating cannot clear it, honesty cannot.

**Explicitly NOT dead:** an arm returning NOT_SEPARATED at an n where Gate 0 failed. That is
unmeasured. **And per the standing rule: before any direction is called exhausted, write down what
was actually tested and what the stronger, more brain-faithful version would be, then test THAT.**

### 9.4 The anti-rule

**Adjusting a band is not a result.** If a gate cannot be met at the available n or with the
available instrument, the output is:

> "UNMEASURABLE at n = X with scorer S. It becomes measurable at n = Y, or with scorer T. Here is
> the cost of each."

Never a widened band, never a softened threshold, never a floor dropped from the battery.

---

## 10. WHAT THIS PROTOCOL REUSES RATHER THAN REINVENTS

Everything in the left column already exists in this repo and is load-bearing for OGL-1. Nothing
here should be rebuilt.

| existing mechanism | what OGL-1 uses it for | change needed |
|---|---|---|
| `tools/floor_battery.py` | Gate 3 entirely -- the four floor roles, both tie conventions, `pool_admits_a_winning_constant`, and `oracle_constant_scores` correctly labelled ORACLE | **add a REFUSAL** when a floor value is loaded from a different population (the C34 mechanism) |
| `tools/exp_checkpoint.py` | Gates 4 and 5 -- per-rung, per-arm resumability. The write-rule ladder already checkpoints its composition units, which is why it could be corrected and re-run cheaply | none |
| **the four-floor bar** (`tools/c3_gate.py`, `tools/verdict_bar_check.py`) | Gate 3's PASS predicate as an EXECUTABLE function rather than prose, plus the mandatory zero-meaning string control | none -- but note `verdict_bar_check.py` has false-passed four times and is a REPORT, never an enforcement action |
| **the ladder pattern** (`exp_pipeline_stage_oracle_ladder_v1`, `exp_writerule_step_ladder_v1`) | Gate 4 wholesale: oracle rungs, ranked drop table, paired CIs on drops, `direction_of_step_a_to_b`, monotonicity assertion, `STAGE_ENUMERATION.method` | **add the grid-resolution disclosure (4b)** |
| **pre-registered stop-ifs** | the branch actions at every gate. Note the standing defect: the write-rule ladder's coded stop-if string and its written conclusion disagreed, and the author disowned the string | **stop-if strings must be GENERATED from the gate predicates, not written alongside them** |
| **the composition instrument** (`wordnet_relation_composition`, `syntagmatic_jaccard_composition` in `exp_writerule_step_ladder_v1.py`, ported from `exp_readout_second_order_v1`'s C1/C2) | Gate 5's confirmatory half | **restore the rung-invariant `RANDOM_ELIGIBLE_ANCHOR` reference that was dropped in the port, and stop using argmax-gold as the reference** (section 4.5) |
| **the leak-safe profile pool** built for Organ F's ladder | any depth or accumulation work | none -- but it is MANDATORY, not optional |
| **paired bootstrap at 10,000 draws** | every CI in the protocol | none |
| `data/capability_registry.jsonl` + `capability_registry_audit.py` | the WIRE-OR-SHELVE exit | none |

**Two things to build, and they are small:**
- **The dissociating pair set** (section 8.3). WordNet plus the existing corpus co-occurrence index
  (`where` in the ladder). Frequency/length/POS matching. A few hundred lines, reusable forever.
- **The Gate 0 pre-flight MDE function.** Takes an item set and a scorer, returns the margin's null
  half-width. Perhaps fifty lines. **This is the highest value-per-line item in this note.**

---

## 11. THE GATES THAT ARE CURRENTLY OUT OF REACH -- AND WHAT WOULD PUT THEM IN REACH

**No gate below is weakened. Each is stated as unachievable-for-now with the specific thing that
would change that.**

### 11.1 "hit@1 CI-separated above the binding floor of 0.139" is not reachable on the current path, and the reason is instructive

The constant/prototype floor reads **0.1390** on a pool where chance is **0.0101** -- 13.8x chance
from a policy that ignores the query entirely. Our systems read 0.02-0.06. **We are not merely below
the floor; we are below a machine that does not look at the question.**

**This floor is legitimate and must not be removed.** It is strong because our generous gold sets
concentrate on popular anchors, so "always answer the most prototypical word" is a genuinely good
no-understanding policy on this instrument.

**What makes it achievable is not a different bar. It is this:** our failure mode is exactly
ORTHOGONAL to what the floor exploits. The floor wins by picking POPULAR words; our store wins by
picking RARE COLLOCATES (winners co-occur 4.24x more than the right answer; 79.3% have no close
WordNet relation). **A write rule whose winners are relation-bearing would clear this floor almost
incidentally, because the floor's advantage is popularity and a relation-bearing winner is right
regardless of popularity.** So the gate is unachievable **until the write rule changes**, and it is
the correct gate to hold on this instrument. **Do not touch it.**

**Secondary note, and it is a real repair item rather than a weakening:**
`floor_battery.matched_candidate_sets` -- the machinery whose whole purpose is to build a pool on
which no constant can beat chance -- **FAILED its own oracle check in four banked cells** (fitted
oracle constant 0.7262 / 0.7313 / 0.7323 / 0.7354 against chance 0.0625). Until that is repaired we
cannot even DECOMPOSE how much of the floor is popularity. **Repairing it is instrument maintenance,
not gate adjustment, and it is worth doing.**

### 11.2 Verb-space separation at SimVerb scale is not reachable and will not become reachable by adding items

At n=222, the margin over the strongest floor is +0.1452 with a half-width of 0.194. To separate you
need a half-width below 0.145, which means roughly **n >= 400 verb pairs on a benchmark that has
222.** **More items do not exist on this ruler.**

**What would make it achievable, in order of preference:** (1) a **pair-level instrument** rather
than a per-item correlation -- the same 222 pairs yield 24,531 pairwise orderings, which is the RSA
move and buys the power without new data; (2) a **stronger channel** so the effect grows rather than
the noise shrinking -- the affect channel already moved rho from 0.2711 to 0.3705, and the missing
"picture" and "social" halves of the owner's Q6 are unbuilt; (3) a different benchmark, which
imports a new population and all the hazards of crossing one.
**Never: relaxing the floor set from four to three.**

### 11.3 The dissociation score's own hard case, stated so nobody is surprised by it

Substitutability and co-occurrence are **correlated in text**, so Cell P (substitutable, never
co-occurring) may be small and unrepresentative -- it selects for synonym pairs that the corpus
happens to keep apart, which may be a peculiar subset. **Mitigations, all mandatory:** report Cell P's
size and its frequency profile against the full gold; report the correlation between the two relations
on the full population so the reader knows how much the cells are outliers; and run the score at
several decile cut-offs (top/bottom 10%, 20%, 30%) so the result cannot be an artifact of one
threshold. P(the dissociation score gives a CI-separated, threshold-stable answer on our incumbent
store) **~0.50** -- capped at the novel-synthesis ceiling per standing calibration, and honestly, I
think it is near that cap rather than below it because the predicted effect is large and the
construction is simple.

---

## 12. HONEST LIMITS OF THIS NOTE

- **The protocol is UNTESTED.** It is assembled from methods that are measured elsewhere and from
  two ladders that worked here. That it will raise our decision yield is a **hypothesis pending VET**,
  not a result. The falsifiable form: *if OGL-1 is applied to Organ A and produces fewer than two
  decisions in its first pass, the protocol is not the fix and the problem is elsewhere.*
- **The decision-yield count is a judgement call at the margins.** I stated the criterion (section 2
  preamble) and applied it uniformly; a reasonable person could move cells 3, 6 and 11 into the YES
  column and get 7 of 11. **They cannot get 11 of 11, and that is the point.**
- **Section 4.5's composition-reference finding is a defect in a CONTROL, not a refutation of the
  claim.** The claim in plan section 6.3 may well be true. It is currently uncontrolled, and the fix
  is one line.
- **Prior work is the foundation here, not a resource to be raided.** RSA and the noise ceiling are
  Kriegeskorte and colleagues'; the inference machinery is Schuett, Kriegeskorte, Diedrichsen and
  co-authors; the mimic/modulation critique is the Dujmovic/Bowers line and it is the more useful
  half; control tasks and selectivity are Hewitt and Liang's; amnesic probing is Elazar, Ravfogel
  and co-authors' with the LEACE refinement from later work; the syntagmatic/paradigmatic
  vector-space treatment is Sahlgren's and the terms are Saussure's; SOC-PMI is Islam and Inkpen's;
  SimLex-999 and the similarity-versus-association argument are Hill, Reichart and Korhonen's; the
  paired bootstrap in NLP evaluation is Koehn's. **We are building on their work and should say so
  in any writeup that uses it.**
- **What I did NOT do:** author or run anything; touch `experiments/`, `hdlab/` or
  `data/foundation/`; edit the plan or any cortical/write-rule-mathematics note (a sibling drill is
  in flight there).

**Sources consulted (web):**
[Obstacles to inferring mechanistic similarity using RSA](https://www.biorxiv.org/content/10.1101/2022.04.05.487135v4) *
[Statistical inference on representational geometries](https://elifesciences.org/articles/82566) *
[Designing and Interpreting Probes with Control Tasks](https://aclanthology.org/D19-1275/) *
[Probing Classifiers: Promises, Shortcomings, and Advances](https://direct.mit.edu/coli/article/48/1/207/107571/Probing-Classifiers-Promises-Shortcomings-and) *
[Amnesic Probing: Behavioral Explanation with Amnesic Counterfactuals](https://aclanthology.org/2021.tacl-1.10/) *
[Improving Causal Interventions in Amnesic Probing with Mean Projection or LEACE](https://aclanthology.org/2025.findings-acl.674/) *
[The Word-Space Model (Sahlgren)](https://www.semanticscholar.org/paper/The-Word-Space-Model-:-Using-distributional-to-and-Sahlgren/1521ddb27860cc8834f8a82e62665bf983c8ad2c) *
[Second order co-occurrence PMI for semantic similarity](https://www.cs.brandeis.edu/~marc/misc/proceedings/lrec-2006/pdf/242_pdf.pdf) *
[Multi-SimLex / the similarity-vs-relatedness argument](https://direct.mit.edu/coli/article/46/4/847/97326/Multi-SimLex-A-Large-Scale-Evaluation-of) *
[Feature-reweighted RSA](https://www.sciencedirect.com/science/article/pii/S105381192200413X) *
[Guide to RSA (noise ceiling practice)](https://academic.oup.com/scan/article/14/11/1243/5693905) *
[Variance partitioning](https://www.diedrichsenlab.org/BrainDataScience/variance_partitioning/index.htm) *
[Paired bootstrap significance testing in NLP](https://people.cs.umass.edu/~brenocon/inlp2015/16-sigtests.pdf)

---

## 13. THE FIVE THINGS TO DO TOMORROW, IN ORDER

1. **Commit the five untracked 2026-08-17 landings.** Five minutes. One of them holds an unrecorded
   orthographic-leakage failure.
2. **Write the Gate 0 pre-flight MDE function** (~50 lines) and make it a required field in every
   pre-registration: `A`, `MDE_margin`, and PASS/FAIL.
3. **Build the dissociating pair set** (Cell P and Cell S, frequency/length/POS matched) and run the
   four control systems through it. **This alone answers "does our store encode substitutability or
   co-occurrence?" as a single signed number with a confidence interval, for the first time.**
4. **Fix the composition instrument's reference** (restore `RANDOM_ELIGIBLE_ANCHOR`, drop
   argmax-gold as a baseline) and re-run the write-rule ladder's Gate 5 half. Until then, section
   6.3's "66.0% -> 94.4%" is uncontrolled.
5. **Then, and only then, run OGL-1 on ORGAN A** -- FILTER / CODE / ACCUMULATE / NORMALISE, gate by
   gate, per the owner's ruling.
