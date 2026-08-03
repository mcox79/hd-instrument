# The foundational grounded-knowledge layer — program design

Status: DESIGN (no cells authored/dispatched from this doc). Author: Director. Date: 2026-08-03.
Branch: `dataprep/mcguffey-graded-corpus`, all local, NO push.

## 0. The diagnosis this program answers

Tonight's ~8 corrections (cheap-distributional -> mean-pool -> scorer-bug -> wrong-grain ->
wrong-success-criterion -> context-stripped -> bundle-vs-bind -> situated-structure) are one
failure: we tried to make the substrate infer goal/affective/social *meaning* (revenge, anger,
care, punishment-vs-discipline) purely from text statistics, with no grounded referent for those
words to land on. USER: "there needs to be a foundational knowledge that all other knowledge can
build upon ... You can't learn revenge and anger from a book." The existing comprehension stack
(coref B3~0.87, `situation_model_accumulate`/`situation_model_multibank`, `CausalLinkRegister`
0.9722 GIVEN links, Trabasso goal->causal in `hdlab/action_selection.py`,
`hdlab/self_improving_loop.py`) is VERIFIED but presupposes GIVEN structured relations (goals,
satisfy/thwart, agent/patient roles) — it never had to ground what a goal, a blocked goal, or
anger actually *are*. This program builds that ground, once, non-textually, so reading can then
map words onto it instead of trying to originate it from word co-occurrence.

KB-check (bash tools/substrate_query.sh, tau 0.15, k5, v2 schema, 2026-08-03): no existing
grounding-simulation or emotion-appraisal prior art in the substrate. Top hits are dictionary-level
concept-node entries (`appraisal`, `false belief`, `retaliation`, `simulation` — WordNet/definitional,
not a grounding mechanism) plus the ALREADY-BANKED `theory_of_mind_sally_anne_nested_hrr_v1`
cell (HARD_PASS, `preregs/2026-06-27_theory_of_mind_sally_anne_nested_hrr_v1.md`,
`data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json`) and a language/world-model
framing note (`notes/drill_language_world_model_framing.md`) that already carries the Spelke
core-knowledge citations verbatim (Spelke & Kinzler 2007 *Developmental Science*; Spelke 2000
*American Psychologist*; Revencu 2023 *Mind & Language* review of Spelke's *What Babies Know*).
**This program is genuinely new** (no grounding-simulation exists) but **builds on, does not
duplicate**: the Sally-Anne ToM organ (cite, extend to appraisal-driven false-belief, don't
re-derive) and the Spelke citation chain already vetted in `drill_language_world_model_framing.md`.

---

## 1. What the ~6yo grounded foundation IS (developmental science, prioritized)

Lead with the biology. By the time a child starts reading connected narrative (~5-7yo, matching
the McGuffey grade band we curriculum-tuned to), the following pre-literate systems are already
in place, in this developmental order. This is the inventory to ground — not everything a 6yo
knows, but the *load-bearing* primitives narrative comprehension actually calls on.

### 1a. Spelke core knowledge (pre-linguistic, infancy, shared with primates)
Spelke & Kinzler 2007 (*Dev. Sci.* 10:89-96); Spelke 2000 (*Am. Psychologist*). Five systems,
each with its own signature (violation-of-expectation looking-time paradigms):
- **Objects**: cohesion, continuity, contact — persist, move on connected paths, don't teleport.
- **Agents**: goal-directed, *not* bound by contact/cohesion mechanics — this is the one that
  matters most for narrative. Even 3-6-month-olds and non-human primates parse self-propelled,
  goal-directed motion as categorically different from object motion (Premack & Premack 1997,
  chasing/helping displays with animated shapes; Woodward 1998, infants habituate to an actor's
  *goal-object*, not the literal trajectory — reach for A over B still reads as "wants A" after
  the actor's arm position changes).
- **Number**: approximate magnitude (less load-bearing for narrative than the other four).
- **Space/geometry**: allocentric layout.
- **Social partners** (likely 5th system, Spelke's tentative extension): conspecific
  recognition, in-group/out-group — feeds harm/help/fairness below.

### 1b. Agency and goal-directedness (extends 1a, ~6-12mo)
Woodward's goal-encoding studies establish that infants represent *actions as directed at
outcomes*, not as raw kinematics, before they have language for "goal" or "want." This is the
single most load-bearing primitive for narrative: every Trabasso goal-plan-action story
structure and the substrate's existing Trabasso goal->causal organ presupposes an entity that
HAS a goal. Grounding "goal" is grounding *directedness-toward-an-outcome-with-preference*, not a
symbol.

### 1c. Intuitive social evaluation — helper/hinderer (~6-10mo, Hamlin, Wynn & Bloom 2007, *Nature*)
Infants prefer an agent that HELPED a goal-seeking shape reach its goal over one that HINDERED
it, before any language. This is the earliest evidence of a valenced appraisal of *another
agent's causal relation to a third party's goal* — i.e., the germ of harm/help moral evaluation,
prior to and independent of any narrative or verbal instruction. Load-bearing because it shows
the valence (good-agent/bad-agent) is bound to *goal-outcome causal role*, not to any lexical
item.

### 1d. Appraisal-theory emotion (goal-relevant event evaluation, NOT word definitions)
Lazarus (1991, *Emotion and Adaptation*) and Scherer's Component Process Model: emotions are not
categories to be defined, they are the OUTPUT of an appraisal of an event against an agent's
goals/concerns along a small set of dimensions (goal relevance, goal congruence/incongruence,
agency/causal attribution — self/other/circumstance, coping potential). The mapping that matters
for narrative comprehension:
- **Joy** = goal achieved (congruent outcome).
- **Sadness** = goal-relevant loss, no agent to blame / low coping potential.
- **Anger** = goal BLOCKED, causal attribution to an AGENT (not accident/circumstance), coping
  potential = can act against the blocker. This is the direct ground for "revenge": anger with
  a *retaliation* action-tendency directed at the identified blocking agent.
- **Fear** = anticipated threat to a goal/to safety, agency uncertain, low coping potential
  (flee/avoid tendency).
This is the crux the USER named: "anger" and "revenge" are not word-meanings to be learned from
a dictionary or from co-occurrence — they are LABELS FOR AN APPRAISAL OUTCOME (a computation over
goal-state + causal attribution + coping potential). A system that has never computed that
appraisal has nothing for the words to refer to.

### 1e. Theory of mind, developmental sequence (Wellman, Cross & Watson 2001 meta-analysis,
*Child Development*, ~178 studies)
- **Desire psychology** (~2yo): others act to satisfy wants, wants can differ from mine.
- **Belief-desire psychology** (~3-4yo): action follows from BOTH belief and desire.
- **False-belief understanding** (~4-5yo, the classic Sally-Anne benchmark, Wimmer & Perner
  1983; Baron-Cohen, Leslie & Frith 1985 autism dissociation): the agent's belief can be FALSE,
  and behavior follows the (false) belief, not reality. **Already built and HARD_PASS in this
  substrate**: `theory_of_mind_sally_anne_nested_hrr_v1` (see KB-check above) — cite and extend,
  do not re-derive the nested-belief representation.

### 1f. Intentional vs. physical/accidental causality (Piaget's developmental precursor;
Shultz 1980 attribution-of-responsibility studies)
6yos already differentiate "he knocked it over on purpose" from "he tripped and knocked it
over" — intentional causality carries moral/appraisal weight (feeds 1c/1d blame attribution),
physical causality does not. This is the gate on whether "anger" fires at all: appraisal-theory
anger requires attribution to an AGENT's intentional action, not an accident.

### Prioritized load-bearing inventory for THIS program (what narrative comprehension of
goal/affect/social content actually calls on, in build order):
1. **Agent vs. object** distinction + **goal-directedness** (1a/1b) — prerequisite for everything
   below; largely already implicit in the existing role-extraction/situation-model stack (agent
   slot exists) but never grounded as *goal-directed-toward-a-preferred-outcome*.
2. **Self/other + valenced target** (1c) — already partially present as coref/binding
   (2026-08-03 situated-structure reframe: agent->TARGET(self/other)->action). Needs the
   VALENCE dimension added (help vs. harm toward the target).
3. **Goal-outcome appraisal -> emotion** (1d) — THE genuinely missing primitive. Anger/fear/
   joy/sadness as a small computed function of (goal state, causal attribution, coping
   potential), not four separate word-meanings.
4. **Intentional vs. accidental causal attribution** (1f) — gates whether appraisal-anger fires;
   composes with the already-verified `CausalLinkRegister` (0.9722) which currently treats all
   causal links uniformly and has no intentional/accidental distinction.
5. **Belief-desire + false-belief** (1e) — already built (Sally-Anne HARD_PASS); needs to be
   WIRED to feed the appraisal (a false belief about a threat still produces real fear; the
   appraisal runs over the AGENT'S REPRESENTED state, not ground truth — this is the standard
   ToM-appraisal integration in the developmental literature, e.g. Wellman's belief-desire
   reasoning about others' emotions, ~preschool).

---

## 2. How to ground it brain-faithfully, no borrow, not from text

The crux constraint: an LLM/embedding-borrow is forbidden (it would just be re-importing text
statistics under a different name), and grounding FROM TEXT is exactly the thing that failed
tonight (you cannot get "anger" from co-occurrence of the word "anger"). The developmental
answer is that a 6yo did not get these primitives from books either — pre-literate children get
1a-1c from PERCEPTUAL/INTERACTIVE EXPERIENCE (the habituation/looking-time paradigms above are
literally infants *watching events happen*), and get 1d (appraisal) from living through or
witnessing goal-relevant events with real stakes, well before literacy. The substrate's analog of
"perceptual/interactive experience" is a SIMULATED WORLD it can compute over directly — not a
described one.

### 2a. The supply-vs-earn split

**SUPPLY BY HAND** (innate/near-innate core knowledge — developmental evidence places these too
early, too fast, and too cross-species-general to be plausibly LEARNED from any modest amount of
experience; this matches the "build-primitive-by-hand" error-routing rule
[[feedback route errors: missing-PRIMITIVE -> BUILD]] and is consistent with "capability dev is
goal, cert-grade is instrument" — bootstrapping a primitive by hand is a legitimate build step,
not a shortcut around earning):
- The **agent/object distinction** and the representational slot for **goal** (an agent has an
  outcome it is directed toward, with a preference ordering) — Spelke-core, present at 3-6mo,
  not learned from any experience corpus a substrate could run.
- The **appraisal DIMENSIONS** themselves (goal-relevance, congruence, causal-attribution-to-agent,
  coping-potential) as a fixed small computational schema (Scherer's Component Process Model is
  explicitly a SEQUENCE OF CHECKS, not a learned classifier) — the *architecture* of appraisal is
  supplied, the same way object-permanence's continuity/cohesion checks are supplied.
- The **self/other distinction** and a **valence primitive** (help/harm as a signed scalar on an
  action's effect on another agent's goal-state) — already partially present via the 2026-08-03
  situated-structure reframe (bind agent->target->action); this program adds the valence slot.
- The **false-belief/nested-belief machinery** — already built (Sally-Anne organ), reuse as-is.

**EARN VIA A MINIMAL GROUNDING SIMULATION** (the genuinely experiential, error-driven part —
this is where "you can't learn it from a book" gets its buildable answer):
- The MAPPING from (goal-blocked, agent-caused, high coping-potential) -> retaliation-toward-
  the-blocker is NOT supplied as a hand rule. It is EARNED by having the substrate accumulate
  many simulated episodes, each with a concrete outcome (did retaliating vs. not-retaliating
  reduce/resolve the blocked-goal state), and let error-driven update shape the appraisal ->
  action-tendency mapping the way associative/reinforcement learning shapes a young child's
  emerging anger-regulation and social-retaliation scripts (this is NOT claiming children learn
  anger by trial-and-error alone — appraisal itself is early/fast per 1d — but the ACTION-
  TENDENCY -> BEHAVIOR coupling, and generalization across novel blockers/goals, is exactly the
  kind of statistical regularity that experience-driven learning is well-evidenced for,
  e.g. instrumental learning literature on approach/avoidance shaping).
- Also earned: generalization of the VALENCE label (this specific action, toward this target,
  in this goal-context, is HELP or HARM) across novel agents/goals — the substrate should not
  memorize "shape A is bad" (that was the infant study's OWN result — infants generalize
  helper/hinderer valence across novel actors), it should earn a transferable function of
  (goal-state, causal-role) -> valence.

This split mirrors exactly how the literature frames it: appraisal STRUCTURE is early/fast/
core-knowledge-like (supply), the mapping from repeated appraised-experience to differentiated
emotional/social RESPONSES and their generalization is where experience does real work (earn).
It is also the direct FHRR analog of pre-literate experiential learning: a toddler is not
reading about blocked goals, they are living through hundreds of them (toy taken away, blocked
by furniture, blocked by a sibling) and the appraisal->response mapping tunes over that
experience — the simulation is the substrate's substitute for that embodied experience stream,
not a textual substitute for it.

### 2b. Minimal grounding-simulation spec (first buildable artifact)

**World**: a small set of AGENTS (2-4 per episode, held-out identities across train/eval — no
agent-specific memorization allowed) each carrying:
- a **goal state**: (target-outcome, currently-satisfied: bool)
- a **position/possession state** in a tiny discrete world (who holds what resource, in what
  location) — this is the minimal "object" substrate the goal is defined over (e.g. goal =
  possess resource X, goal = occupy location Y).

**Actions** (small closed set, each agent picks one per timestep):
- `pursue(goal)` — act toward own goal.
- `block(other, other's goal)` — act to prevent another agent's goal (take their resource,
  occupy their target location).
- `help(other, other's goal)` — act to advance another agent's goal.
- `retaliate(blocker)` — act against a specific other agent who has PREVIOUSLY blocked own goal.
- `withdraw` — disengage (the "no retaliation" comparison arm).

**Episode structure**: multi-timestep sequences where agent A's goal gets blocked by agent B
(explicit causal event: B's action -> A's goal-state flips satisfied:true->false, or
prevents reaching true), across many (goal, blocker-identity, world-configuration) combinations.
Held-out slices: novel blocker identities, novel goal-types, novel world configurations — the
can-fail test below requires generalization, not memorization of specific (agent,goal) pairs.

**Appraisal computation** (SUPPLIED architecture, per 2a): after each event, compute the fixed
dimension-vector (goal-relevance: does this event touch MY goal; congruence: did it help or hurt;
causal-attribution: was there an identifiable AGENT cause vs. accidental/environmental;
coping-potential: do I have an available action that could address the blocker). This is a
deterministic function of the world-state + action-log, NOT a learned component — it is the
architecture, same status as the object-permanence continuity check.

**What is EARNED** (the actual learning target, glass-box/error-driven, FHRR-native): given the
appraisal-vector for an episode's outcome, learn the ACTION-TENDENCY mapping
(appraisal-vector -> preferred next action among {pursue, retaliate, withdraw, help}), trained
against episode-level reward = own-goal eventually achieved (does retaliating against the
specific blocker who caused the block actually restore goal-progress, vs. an untargeted or
misdirected response). This is where "blocked-goal + agent-cause + high coping-potential ->
retaliate-toward-the-blocker" gets EARNED rather than hand-coded: the substrate has to discover,
from simulated consequence, that retaliation targeted at the causal agent (not a bystander, not
withdrawal) is differentially reinforced when coping-potential is high, mirroring the Hamlin-
style result that valence tracks causal role, not surface identity.

**Held-out generalization requirement** (glass-box, error-driven, no borrow — everything above
is world-state, integer/discrete actions, and a small appraisal-dimension vector, no text, no
pretrained anything).

### 2c. The fair can-fail test

Pre-registration-shape (for the eventual cell, not authored here):
- **Discriminator**: on HELD-OUT (agent-identity, goal-type, world-config) triples never seen in
  training, does the earned action-tendency mapping correctly select `retaliate(blocker)` over
  {pursue, withdraw, help, retaliate(wrong-agent)} when appraisal = (goal-blocked, agent-caused,
  high-coping-potential), at a rate that beats:
  - a RANDOM-action floor,
  - a MEMORIZED-lookup floor trained on training agents but evaluated on held-out ones (must
    generalize, not memorize identity),
  - a NO-APPRAISAL floor (action-tendency conditioned only on raw event features, not on the
    supplied appraisal dimensions) — this isolates whether the appraisal STRUCTURE (supplied)
    is actually doing work vs. the earned mapping alone could do it from raw features (if the
    no-appraisal floor matches, the appraisal architecture is vacuous and the split in 2a is
    wrong).
- **Envelope-fail bands**: PASS = beats all three floors with margin, generalizes across >=2
  held-out slices (identity AND goal-type). PARTIAL = beats random/memorized but not
  no-appraisal (appraisal structure not adding value — informative negative, would mean the
  earning can be done directly on raw features and 2a's supply list should shrink). FAIL =
  doesn't beat random on held-out (simulation too easy/hard-coded-shortcut-prone, or the
  action-tendency mapping isn't learnable from this signal — needs redesign, not abandonment,
  per "flat result = broken experiment not a ceiling").
- **Brain-fidelity gate**: does this fail the same way a Hamlin-study infant or a preschool
  false-belief-emotion task would fail (misattribution to wrong agent, misjudging coping
  potential) vs. an architecture-specific failure (can't hold appraisal dimensions in the
  representation at all)? If FAIL, diagnose against this gate before concluding.

---

## 3. How reading builds on the grounded foundation

Once (a) the supplied core-knowledge primitives (agent/goal/self-other/valence/appraisal-
architecture/false-belief-machinery) and (b) the earned appraisal-outcome -> action-tendency
mapping exist, **text stops being asked to originate meaning and starts being asked to MAP onto
an already-grounded structure** — exactly the role text plays for a literate 6yo (they don't
learn what anger IS from "she was angry," they recognize the word as a LABEL for an appraisal
state they can already compute).

Concretely, the existing organs become CONSUMERS of the grounded layer instead of operating on
ungrounded symbols:
- **Role extraction / coref / situation_model_accumulate** (already built, WIRED, B3~0.87):
  unchanged — still tracks WHO across the discourse. This is the "who" that fills the agent slot
  in the grounded appraisal computation.
- **Situated-structure (agent->target->action->valence)**, the 2026-08-03 in-flight reframe
  (test a7a370e2): becomes the PARSER OUTPUT format that FEEDS the grounded appraisal function
  from 2b directly — instead of hand-defining "REVENGE=harm-toward-other-after-being-harmed" as a
  text-side category, the situated-structure parse produces (agent, target, action, goal-context)
  and the SAME appraisal-then-earned-action-tendency function from the simulation scores it. A
  sentence like "she wanted to punish him" maps to (agent=she, target=him, action~=harm,
  goal-context=he blocked her earlier goal) -> the grounded function classifies it as the
  retaliation-appraisal region, which is what "punish"/"revenge" DENOTE — the near-synonym
  disambiguation (REVENGE_PUNISH vs SELF_DISCIPLINE) that blocked the frontier tonight resolves
  because "punish" applied to (agent=self, target=self) is definitionally outside the
  retaliation region (no other-directed target) while (agent=she, target=him,
  prior-blocked-goal-by-him) is inside it — the grounding supplies the discriminating structure
  that lexical/distributional methods could not.
- **`CausalLinkRegister`** (0.9722 GIVEN links): gains the intentional-vs-accidental attribution
  dimension (1f) as an additional edge-label, feeding directly into the appraisal
  causal-attribution dimension — currently the organ is causally uniform (any cause is a cause);
  this program adds the distinction appraisal needs.
- **Trabasso goal->causal** (`hdlab/action_selection.py`): the goal-plan-action chain the organ
  already tracks becomes the goal-STATE input to appraisal (satisfied/blocked), not a bare
  causal edge.
- **Sally-Anne ToM organ**: reused as-is for belief-desire input to appraisal (appraisal runs
  over the agent's REPRESENTED goal/belief state, not ground truth — standard in the ToM-
  emotion-understanding literature and already representable given the HARD_PASS nested-belief
  organ).
- **`self_improving_loop`**: extends naturally — flagged low-confidence appraisal
  classifications (e.g. ambiguous target, ambiguous causal attribution) become the metacognitive
  flag signal, same architecture as the existing coref-margin flag.

This is a two-stage architecture: **FOUNDATION (2b, non-textual, built once)** produces a
grounded appraisal-and-action-tendency function; **READING (existing comprehension stack)**
extracts situated structure from text and queries that function. Text never has to bootstrap the
concept of anger from scratch again — it only has to extract who/what/whom, which the coref and
situated-structure machinery already does at a validated level.

---

## 4. Lock-compatibility

- **Supply-by-hand primitives**: explicitly authorized by the "route errors by flavor" rule
  (missing-PRIMITIVE -> BUILD) and consistent with "brain-foundational" (the developmental
  evidence places these primitives as innate/near-innate, not learned — supplying them IS the
  brain-faithful choice, not a shortcut around one).
- **Earn-via-simulation**: glass-box, error-driven, FHRR-native, no borrowed embeddings, no LLM
  at any point (world-state is small discrete structure, not text) — fully compliant with
  "no borrowed embeddings ever," "no bolt-on reader/parser" (there is no reader here — the
  simulation is not text), and "meaning = assignment."
- **Not-from-text**: the grounding step operates entirely over simulated world-state/actions;
  text only enters at the READING stage (section 3), consuming an already-grounded function —
  directly answers the USER's "you can't learn revenge and anger from a book."
- **Comprehension = growing library of construction-competencies**: this program adds
  "appraisal-grounded goal/affect/social competency" as one MORE competency in the library
  (alongside coref, causal, ToM), not a replacement objective — composes rather than collapses
  the existing stack.

## 5. Scope-note update (honest correction to a prior framing)

The 2026-07-14 "grounding = optional" framing is SUPERSEDED for this competency class: grounding
is NECESSARY (not optional) specifically for goal/affect/social-valence comprehension — the
2026-08-03 empirical arc (word-level distributional exhausted, event-predictor closed,
construction-integration MIDDLE_BAND, near-synonym goal disambiguation impossible without
content meaning) is the evidence for this correction, not an assumption. Grounding remains
optional/orthogonal for competencies that don't route through appraisal (e.g. pure entity
tracking, adjacency-causal inference) — this is a scoped correction, not a blanket reversal.

## 6. What's new vs. what's reused (summary)

| Component | Status |
|---|---|
| Spelke core-knowledge citations | REUSED (already in `notes/drill_language_world_model_framing.md`, verbatim, disk-verified) |
| Sally-Anne false-belief ToM organ | REUSED AS-IS (HARD_PASS, `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json`) |
| Situated-structure agent->target->action->valence parse | REUSED, in-flight test a7a370e2 becomes the reading-side FEEDER into the grounded function |
| Coref / situation_model_accumulate / CausalLinkRegister / Trabasso goal->causal | REUSED AS-IS, become CONSUMERS of the grounded appraisal function |
| Appraisal-dimension architecture (goal-relevance/congruence/causal-attribution/coping-potential) | NEW — supplied by hand per Scherer CPM |
| Minimal grounding-simulation (agents/goals/block/retaliate/help/withdraw, held-out generalization) | NEW — first buildable artifact, spec in section 2b |
| Earned appraisal-outcome -> action-tendency mapping | NEW — the genuinely-earned, error-driven, glass-box learning target |
| Intentional-vs-accidental causal attribution label on CausalLinkRegister edges | NEW (small extension) |

## 7. Recommended next step (not authorized by this doc)

Design research is complete. The next step is a pre-reg for the 2b simulation cell (small,
CPU-cheap, discrete-world, no text) with the 2c can-fail bands — that is an exp_dev-shaped
build, not a design task, and is intentionally NOT dispatched from this doc per the task
constraint (design research only, no cell authoring). Flagging it as the concrete next action
for the USER/next cycle: build the minimal grounding simulation (2b), verify the three-floor
can-fail (2c) on held-out agents/goals, and if PASS, wire it as the appraisal-function consumer
for the in-flight situated-structure test (a7a370e2).
