# Research: does precedent exist for a leave-one-out counterfactual-necessity test over GOAL-SATISFACTION state (as opposed to physical state) to select a narrative's cause sentence? (2026-09-08)

Filed by: research (Opus), direct topic dispatch (not a routing file). Extends and specializes
`notes/research_context_conditioned_cause_selection_2026-09-08.md` (same day, earlier cycle), which
established the LOO/INUS/Trabasso convergence for PHYSICAL precondition state. This drill asks the
identical question for PSYCHOLOGICAL/goal state specifically, with emotional appraisal as a downstream
composition. Method: 3 parallel Sonnet lit-scan lanes (Trabasso+Zwaan; Graesser+OCC; counterfactual
philosophy-of-causation extended to psychological causation), synthesized here.

---

## HEADLINE

**Two separable questions, two different answers.** (A) Was Trabasso's counterfactual coding criterion
applied to goal-caused events historically? Yes — decisively, and it was the SAME test as for physical
events, not a different one. (B) Is there precedent for building a leave-one-out fold over a GOAL-STATE
fluent (goal-established / goal-satisfied / goal-thwarted) to computationally SELECT which prior sentence
caused a later one, the way the existing STRIPS-precondition fold already does for physical state? No —
all three lanes independently return this as an open gap, and one lane surfaces a genuine calibration
WARNING: the psychology-of-causal-judgment literature shows humans do NOT apply plain counterfactual
necessity uniformly to intentional/goal causation the way they do to physical causation — norm/abnormality-
based selection dominates instead. This is a stronger and more specific warning than a simple "no
precedent found," and should directly shape how the psychological LOO fold is built and calibrated.

---

## 1. Trabasso causal-network coding criterion — physical vs. goal-plan causation

**Trabasso & Sperry (1985, *JML* 24:595-611)** gives the canonical wording: causal links between ALL
pairs of story events were coded using "context-dependent, logical criteria of necessity, and
counterfactual tests of the form: If event A had not occurred, then, in the circumstances of the story,
event B would not have occurred." This was applied to whole folktales, not restricted to goal chains.

**Trabasso, van den Broek & Suh (1989, *Discourse Processes* 12:1-25)** is the decisive methodological
paper: "The counterfactual criterion of necessity... distinguished causal from noncausal relations and
yielded high strength ratings for **physical, motivational, psychological, and enabling relations, in
that order**." One uniform counterfactual test was run across all four causal-category types; the
categories differ in resulting judged STRENGTH (physical rated strongest, enabling weakest), not in the
verification LOGIC applied. Trabasso, Secco & van den Broek (1984) establishes Goal as a clause/node
category (within Setting-Event-Internal Response-Goal-Attempt-Outcome) that participates in the SAME
pairwise counterfactual test as any other clause — not a separately-coded relation type. Suh & Trabasso
(1993, *Discourse Processes* 16:3-34) confirms goal-based causal inferences are generated online during
reading consistent with this uniform-network account.

**Conclusion for item 1: the original Trabasso scheme did NOT treat goal-caused and physically-caused
events with different tests — it is documented, cited precedent for exactly ONE counterfactual-necessity
computation applied across both.** This is good news for the architecture: it means goal-state does not
need a bespoke verification LOGIC, only a bespoke STATE REPRESENTATION (a goal fluent instead of a
possession/open-closed fluent) to fold through the same kind of test.

## 2. Zwaan & Radvansky (1998) event-indexing model

Five situational dimensions confirmed: time, space, protagonist/entity, causation, and intentionality
(motivation) — Zwaan, Langston & Graesser (1995, *Psych Science*) is the precursor. Secondary sources
consistently describe intentionality as tracking a character's goals/plans as a dimension DISTINCT from
causation, but this lane could not retrieve verbatim defining text (primary PDFs unreadable), so treat as
paraphrase-level confidence. The closest operationalization of "goal-state as a trackable variable" found
is **Lutz & Radvansky (1997, *JML* 36:293-310)**, "The fate of completed goal information in narrative
comprehension," which tracks goal-completion status (completed vs. uncompleted) via reading-time/
recognition-priming — but this is a MEMORY-AVAILABILITY measure (does a completed goal stay activated in
working memory), not a counterfactual-necessity test for cause selection. No follow-up work found that
uses goal-state as the object of an LOO-style removal test.

## 3. Graesser, Singer & Trabasso (1994) inference taxonomy

Confirmed a 13-category QA-derived taxonomy including **causal antecedent** and **superordinate goal** as
SEPARATE, PARALLEL categories, not goal-as-subtype-of-causal-antecedent. Causal antecedent = general
bridging inference ("why"/"how" for events/states); superordinate goal = the why-inference specific to
intentional action. GST94's causal-antecedent notion is explicitly built on Trabasso & van den Broek
(1985)'s causal-network framework, and inherits the SAME counterfactual necessity criterion, applied
uniformly across physical, motivational, psychological, and enabling relation types (consistent with
finding 1). **No formal "goal satisfaction necessity" inference category distinct from physical causal
antecedent was found** — goal-directedness gets its own taxonomic slot for WHAT KIND of question it
answers, not a different verification MECHANISM.

## 4. OCC model + computational appraisal implementations

OCC prospect-based structure confirmed exactly as specified: hope/fear (unresolved prospect, pleased/
displeased), satisfaction/disappointment (desirable prospect confirmed/disconfirmed), relief/fears-
confirmed (undesirable prospect disconfirmed/confirmed). Computational systems surveyed:
- **Elliott's Affective Reasoner (1992)**: goals are simple desired-state flags; event-triggered valence
  classification. No counterfactual mechanism.
- **Gratch & Marsella's EMA (2004, *Cog Sys Research* 5(4))**: richer plan-graph goal representation;
  "causal attribution" traces credit/blame along the causal-interpretation graph — structurally CLOSER to
  necessity (an event only gets credit if on the dependency path) but this is graph traversal, not
  explicit leave-one-out simulation. True counterfactual-SIMULATION-based responsibility judgment appears
  only in the adjacent Mao & Gratch (2005) "Social Causality and Responsibility" line, downstream of core
  appraisal, not inside it.
- **WASABI (Becker-Asano & Wachsmuth)**: explicitly studies MISattribution of emotion to temporally-
  proximate (not necessarily necessary) causes — implies simple proximity/valence attribution, not
  necessity testing.
- **FLAME, ALMA, FAtiMA**: event-triggered appraisal against goal/standard state; no evidence of
  leave-one-out cause-selection in any of these.

**No OCC-family implementation found that runs a counterfactual/necessity test to select WHICH prior
event caused the appraised emotion** — all classify valence/type for the currently-processed event
against goal state. This directly confirms the emotional-appraisal-as-downstream-composition framing in
the task: appraisal systems in the literature assume the cause is already identified/current, they don't
solve cause-selection themselves — which is exactly consistent with treating appraisal as a layer that
sits ON TOP of a separately-computed goal-causation answer, not a layer that computes it.

## 5. Mackie/Halpern-Pearl extended to psychological causation — and a critical calibration flag

No formal INUS/Halpern-Pearl treatment isolating a GOAL fluent (goal-adopted / goal-satisfied) for
leave-one-out testing was found, in narrative comprehension, planning, or BDI-agent literature. Classical-
planning LANDMARKS (Hoffmann et al.; LAMA planner) are the closest formal analog — a landmark is a fact
that must hold in every valid plan, a genuine necessity test — but defined over generic STRIPS fluents,
never singled out for mental-state fluents specifically. A 2023/2026 BDI contrastive-explanation line was
directly checked and confirmed to NOT use Mackie/Halpern-Pearl counterfactual removal; goals are static
tree nodes there.

**The important finding is not just absence — it's a positive warning.** The psychology-of-causal-
judgment literature (Knobe & Fraser 2008; Hitchcock & Knobe 2009 "Norms and the Knobe Effect"; Henne,
O'Neill, Bello, Khemlani & De Brigard 2021, *Cognitive Science*; Samland & Waldmann 2016) shows people do
**NOT** apply plain counterfactual necessity uniformly to intentional/goal-caused outcomes — norm- and
abnormality-based selection dominates causal judgments about intentional agents instead. Gerstenberg's
Counterfactual Simulation Model extends counterfactual reasoning to intentional agents but adds a
"counterfactual robustness" adjustment (an action performed WITH the intention to produce an outcome is a
robust cause across many counterfactual branches, not just the single actual branch) — a refinement of
plain LOO, not a replacement, but a real complication a naive single-branch fold will not capture.

**Note on tension with finding 1:** Trabasso's finding (uniform test, different judged strengths) is a
narrative-comprehension/discourse-coding result from the 1980s; the Knobe-effect literature is a later
(2000s-2020s), separate psychology-of-causal-attribution tradition studying deliberate norm-violation
judgments (blame/responsibility), not story-coherence judgments. These may not be in tension — Trabasso
measured whether readers judge a causal LINK to exist; Knobe-effect work measures how readers select
AMONG multiple satisfying causes when assigning blame/responsibility. The system being designed here is
doing the former (which prior sentence caused this one), which is closer to Trabasso's setup than to the
Knobe blame-attribution setup — this reduces but does not eliminate the calibration concern.

---

## Cross-thread synthesis

This drill resolves the split the task poses: the VERIFICATION LOGIC (counterfactual/LOO-necessity) has
strong, explicit, cited precedent for goal-caused events — Trabasso's own coding scheme already ran it
uniformly across physical and psychological/motivational categories, so extending the existing
`WorldState.fold` LOO machinery (built for physical preconditions per
`notes/research_context_conditioned_cause_selection_2026-09-08.md`) to a goal-established/goal-satisfied/
goal-thwarted fluent is NOT introducing a new kind of test — it is reusing the exact test Trabasso already
validated for this category, just on a new state type. What is NOT precedented is the specific SOFTWARE
PATTERN of folding goal-state as a mutable, removable fluent through an LOO test — no computational
appraisal system (OCC family) or formal causation framework (Mackie/Halpern-Pearl) has been found doing
this. And there IS a genuine psychological-plausibility caveat (Knobe-effect norm-based selection) that a
plain LOO-necessity fold over goal state may, in edge cases (especially where blame/responsibility framing
creeps in), diverge from how humans actually select intentional causes — worth pre-registering as a
possible source of graded (not categorical) disagreement with human judgments, not a blocking objection.

## Substrate-product implications

This closes the historical-precedent gap the design's physical-state implementation already exploited:
the psychological analog is not a speculative extension, it's completing what Trabasso's own original
coding scheme already covered in principle (uniform test, both categories) but which the field never
built as a computational fold. Practically: implement a `GoalState` fluent (established / satisfied /
thwarted) parallel to `WorldState`'s possession/open-closed fluents, fold candidate-minus-one exactly as
the physical mechanism already does, and treat OCC-style emotional labeling as a pure downstream function
of the resulting (goal, cause-sentence, satisfied-or-thwarted) triple — never as an input to cause
selection itself, since no literature reviewed uses emotion/valence to select the cause rather than being
computed from it. The one design caution: expect a small, systematic disagreement class on norm-violating
or blame-laden goal outcomes, where a norm-abnormality cue (not implemented here) would better match human
judgment than pure necessity — flag this as a known non-blocking miss category rather than a bug if it
shows up in error analysis.

## Citations (verified count)

Verified this cycle across 3 lit-scan lanes (23+24+27 = 74 tool-uses, search/abstract/secondary-source
confirmed; primary PDFs largely unreadable — noted per-claim above where confidence is paraphrase-level):
Trabasso & Sperry 1985 (*JML* 24:595-611); Trabasso & van den Broek 1985 (*JML* 24:612-630); Trabasso,
Secco & van den Broek 1984; Trabasso, van den Broek & Suh 1989 (*Discourse Processes* 12:1-25); Suh &
Trabasso 1993 (*Discourse Processes* 16:3-34); Zwaan, Langston & Graesser 1995 (*Psych Science*); Zwaan &
Radvansky 1998 (*Psych Bulletin* 123(2):162-185); Lutz & Radvansky 1997 (*JML* 36:293-310); Graesser,
Singer & Trabasso 1994 (*Psych Review* 101(3):371-395); Ortony, Clore & Collins 1988 (*Cognitive
Structure of Emotions*, Cambridge UP); Steunebrink 2009 ("The OCC Model Revisited," KI09); Elliott 1992
(PhD diss., Northwestern ILS TR#32); Gratch & Marsella 2004 (*Cog Sys Research* 5(4):269-306); Mao &
Gratch 2005 ("Social Causality and Responsibility," IVA05); Becker-Asano & Wachsmuth 2008-2010 (WASABI);
Mackie 1965 (*Am Phil Q*) / 1974 (*Cement of the Universe*, Oxford); Halpern & Pearl 2005 (*BJPS*);
Halpern 2016 (*Actual Causality*, MIT Press); Knobe & Fraser 2008; Hitchcock & Knobe 2009; Henne, O'Neill,
Bello, Khemlani & De Brigard 2021 (*Cognitive Science*); Samland & Waldmann 2016 (*Cognition*);
Gerstenberg, Goodman, Lagnado & Tenenbaum 2021 (*Cognition*, counterfactual simulation model); Danks
2005+; Liu & Belle 2025 (arXiv:2501.06857, situation-calculus counterfactual cause); Hoffmann/Porteous/
Sebastia planning-landmarks literature; LAMA planner (Richter & Westphal); "Contrastive Explanations of
BDI Agents" 2023 Springer / 2026 arXiv:2602.13323; "Shadow-Loom" arXiv:2605.02475 (2026 preprint, weak
signal, non-peer-reviewed).

Total distinct sources: 27.

## Calibration

Per mandatory lit-scan calibration policy: finding 1 (Trabasso applied ONE uniform counterfactual test
across physical/motivational/psychological/enabling categories) is corroborated by two independent lanes
citing the same 1989 *Discourse Processes* paper's own summary language — P(literature characterized
accurately) ~0.70 pre-deflation, **deflated to 0.50** (top-of-band; both lanes worked from secondary-
source paraphrase of the 1989 paper, not machine-readable primary text — flagged explicitly by both
agents). Finding 5's negative result (no software precedent for goal-state LOO fold) is a stronger claim
(absence across three independently-searched literatures: narrative comprehension, planning/BDI,
philosophy of causation) — P(absence is real, not just under-searched) ~0.65, **deflated to 0.45**. The
Knobe-effect calibration warning itself (people don't use plain counterfactual necessity for intentional
causation) is well-established published psychology, not novel synthesis — P(accurately characterized)
~0.70, **deflated to 0.50**. The INTEGRATED claim of this note (goal-state LOO fold is precedented at the
verification-logic level via Trabasso, unprecedented at the software-pattern level, with a known
norm-based-selection divergence risk) is this drill's own synthesis bridging three literatures that do not
cite each other — **P_deflated capped at the mandatory novel-synthesis ceiling: 0.40**.
