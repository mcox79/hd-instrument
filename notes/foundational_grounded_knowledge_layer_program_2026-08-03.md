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
grounding-SIMULATION or dynamic-appraisal-earning prior art. BUT — and this is the load-bearing
correction to the first draft of this doc — we have already done SUBSTANTIAL STATIC grounding
work that this program must build on, not reinvent. See section 1.5 for the disk-verified
inventory. The one-line version: the SUPPLIED grounded core the developmental science calls for
(section 2a) is already largely ON DISK (Binder experiential features incl. emotion/drive/social;
animacy/agency lexicon; verb-affectedness/who-is-affected), and the EXTENSION mechanism (grounded
seed + transfer) is already the vetted theory (Harnad/Cangelosi). The genuinely-new part shrinks
to the DYNAMIC structure static grounding cannot give: the blocked-goal -> anger -> retaliate-
toward-the-blocker temporal/causal mapping, which is what the minimal experiential simulation
earns. This program therefore = REUSE the static grounded core + Harnad transfer + Sally-Anne ToM
+ Spelke citations, BUILD the dynamic experiential layer (2b), and MAKE THE FOUNDATION LIVING —
a self-extending grounded STORE (3.5, USER first-class requirement) whose write-back qualification
gate REUSES the already-certified `self_improving_loop` consolidation + false-consolidation
detection, so the foundation is the self-improving reader whose improving target is its OWN
grounded knowledge.

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

## 1.5 Prior grounding work already done — disk-verified inventory + reuse plan

Every item below was DISK-VERIFIED (2026-08-03) before being cited. This is the correction that
turns "design from scratch" into "build on what exists." Credit to the prior arcs (2026-07-10
through 2026-08-02).

**(A) BINDER brain-based experiential semantics — THE supplied grounded DIMENSION SPACE for the
affective/agentive layer. VERIFIED ON DISK: `data/corpora/binder/binder2016_ratings.csv`, 535
rated concepts × 85 columns (65 experiential attributes + metadata)** (Binder et al. 2016;
attributes chosen for KNOWN NEURAL CORRELATES). Confirmed the emotion/drive/social/agency
DIMENSIONS are present as COLUMNS and are exactly the right grounding type for this program:
`Angry, Fearful, Happy, Sad, Disgusted, Surprised, Benefit, Harm, Pleasant, Unpleasant, Social,
Human, Self, Communication, Cognition, Caused, Consequential, Drive, Needs, Arousal`.
**CORRECTED REUSE CLAIM (disk-verified 2026-08-03, correcting the prior draft):** the load-bearing
abstract emotion/social CONCEPTS are NOT rated ROWS and CANNOT be looked up. Verified: rows FOUND
= `angry, happy, joy, love, awe, animosity, apology`; rows ABSENT = `anger, fear, afraid, sad,
sadness, hate, hatred, REVENGE, PUNISH, HURT, HARM, HELP, kind, cruel`. The rated rows are
dominated by CONCRETE nouns (`accordion, alligator, ambulance, apricot, asparagus, axe, banana`) —
Binder's 2016 set is a mostly-concrete-vocabulary norming study, NOT an emotion-lexicon. Therefore:
**Binder supplies the affect/agency DIMENSIONS (the grounded feature axes), and grounding the
abstract concepts the foundation needs — anger, fear, revenge, harm, help — happens via
GROUNDING-TRANSFER / COMPOSITION over those dimensions (1.5-B), NOT by table lookup.** This is not
a limitation to apologize for — it is exactly on-theory (Harnad: a small directly-grounded base +
transfer), and it is the RIGHT architecture: "revenge" SHOULD be a composed structure
(Harm-dimension toward-other after-being-harmed-by-that-other), not a memorized rating vector.
The Binder rows that DO exist (concrete objects + a handful of affect adjectives) seed the
directly-grounded base; the abstract affect concepts compose over it. This is Barsalou/
grounded-cognition operationalized (meaning = which brain systems a concept engages), and it is
LOCK-CLEAN: human RATINGS are grounded axioms/data, NOT a borrowed distributional encoder — same
status as supplying a dictionary. Prior MEASURED outcome (atom 29571, commit cc0045e42, per the
coordinator; the on-disk cell I verified is `data/exp_wave14_binder_ratio_v1/metrics.json` =
BINDER_RS_CONFIRMED, a representational-saturation/self-averaging result, a separate use): direct-
supply CAPPED for ABSTRACT SCIENCE reasoning-ties (~5% vocab coverage; science terms are
definitional/propositional = WRONG grounding TYPE for Binder's experiential axes). **The key
insight this program acts on: that cap was for SCIENCE, not for EMOTION/AFFECT/AGENCY. Binder's
Emotion/Drive/Social/Benefit/Harm/Self/Human attributes are EXACTLY the right grounding type for
anger/fear/joy/care/revenge/self-other.** REUSE: Binder emotion/drive/social/benefit/harm/self
attributes = the SUPPLIED grounded feature-vectors for affective/social concepts, replacing the
"supply a valence primitive by hand" placeholder in the first draft (2a). (Optional sourcing: the
786-concept AI-extended set, arXiv 2505.10718, if obtainable — extends coverage the same lock-
clean way; NOT required for the first build.)

**(B) SYMBOL-GROUNDING THEORY = the extension mechanism. VERIFIED: `notes/research_word_grounding_
lexicon_structure_content_unification_2026-07-16.md`** (+ `notes/exp_dev_handoff_research_word_
grounding_lexicon_2026-07-16.md`). Harnad (1990): a small directly-grounded base (iconic +
categorical) + GROUNDING TRANSFER supports a much larger abstract vocabulary via linguistic
composition, with NO further sensorimotor experience. Cangelosi & Riga (2006): simulated-agent
grounding transfer. The note explicitly frames this as "small measured/relational foundation
grounds the rest via composition" and pairs it with role-filler binding (TPR/HRR/SPA) as the
published mechanism uniting compositional STRUCTURE with grounded CONTENT. REUSE: this is the
supply-a-small-grounded-core-then-transfer architecture for section 2a — the Binder-rated concepts
are the directly-grounded base; abstract goal/affect words the corpus introduces that AREN'T Binder-
rated get grounded by COMPOSITION over the base + situated structure, not by new experience. This
IS the "supply grounded core primitives + earn/transfer the extension" theory, already vetted.

**(C) AGENCY / core-knowledge lexicon — ALREADY BUILT. VERIFIED: `hdlab/animacy_lexicon.py`**
(2026-08-02, glass-box WordNet lookup word/lemma -> {animacy, category, agent_capable}, with a
scrambled-lexicon can-fail control, and documented WordNet failure-mode guards). REUSE AS-IS: this
IS the Spelke agent-vs-object core-knowledge distinction (1a/1b), already grounded and glass-box —
it supplies the `agent_capable` signal that fills the agent slot the appraisal computation runs
over. No need to build agent/object grounding; it exists.

**(D) VERB-AFFECTEDNESS "who is affected" lexicon — ALREADY BUILT (credit; number per coordinator/
atom 2026-07-21, not re-measured here).** 328 verbs, Levin/VerbNet/Dowty/Beavers/Tsunoda;
reported to lift McGuffey semantic 0.529 -> 0.912 (with a definitional-agreement-ceiling caveat —
the lift is partly agreement-with-a-definitional-standard, treat as a strong tool not a pure
capability win). Related on-disk artifacts confirmed present (`notes/research_brain_patienthood_
affectedness_grounding_2026-07-20.md`, `notes/research_cheapest_glassbox_grounding_for_perinstance_
affectedness_2026-07-20.md`). REUSE: this grounds the HARM/HELP causal-role dimension (1c/1f) —
who is affected by an action, and how — which feeds directly into the appraisal congruence +
target-valence dimensions. The situated-structure parse (agent->target->action) gets its
target-AFFECTEDNESS from this lexicon rather than a hand rule.

**(E) Prior grounding-scoping / convergence work (context, cited not duplicated):**
`notes/convergence_architecture_grounding_is_the_verifier_2026-07-10.md`,
`notes/exp_dev_handoff_research_math_social_abstract_grounding_core_expansion_2026-07-10.md`,
`notes/drill_grounding_scoping_is_it_subsumed_by_foundation_hub_or_separate_2026-07-15.md`,
`notes/grounding_work_lookback_synthesis_2026-07-26.md`. These establish the "grounding is the
verifier" + "abstract concepts ground by relay from anchors" framing this program inherits.

**(F) Sally-Anne false-belief ToM organ — HARD_PASS, REUSE AS-IS** (`data/exp_theory_of_mind_
sally_anne_nested_hrr_v1/metrics.json`; `preregs/2026-06-27_...`). Cite, extend to feed appraisal
(appraisal runs over the agent's REPRESENTED state), do not re-derive nested-belief representation.

**(G) Spelke core-knowledge citation chain — REUSE** (already verbatim in `notes/drill_language_
world_model_framing.md`: Spelke & Kinzler 2007 *Dev. Sci.*; Spelke 2000 *Am. Psychologist*;
Revencu 2023 *Mind & Language*). Section 1's science leads with these; not re-sourced.

**What this leaves as GENUINELY NEW** (the only thing the simulation must build): the DYNAMIC
appraisal-outcome -> action-tendency mapping over TIME (blocked-goal-event -> anger-appraisal ->
retaliate-toward-the-identified-blocker), and its generalization to held-out agents/goals. Static
grounding (A-D) gives the FEATURES (what anger/harm/help/self-other/agent ARE, as grounded vectors);
it does NOT give the DYNAMICS (that a goal-block BY an agent PRODUCES anger which MOTIVATES targeted
retaliation over subsequent timesteps). That temporal-causal structure is not in any lexicon or
rating table — it is exactly the pre-literate experiential regularity a child acquires by living
through goal-blocking episodes, and it is what section 2b's minimal simulation earns.

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

**SUPPLY (mostly ALREADY ON DISK — see 1.5; supply-by-hand only where nothing exists yet)** —
innate/near-innate core knowledge, developmentally too early/fast/cross-species-general to be
learned from a modest experience corpus; supplying it is the brain-faithful choice per the
"route errors: missing-PRIMITIVE -> BUILD" rule, NOT a shortcut around earning:
- The **agent/object distinction** and **agent-capable** signal — REUSE `hdlab/animacy_lexicon.py`
  (1.5-C), already built and glass-box. Not re-supplied.
- The **grounded emotion/social/self-other/harm-benefit DIMENSIONS** (the axes along which
  anger/fear/joy/care/self/other/harm/help are DEFINED) — REUSE the Binder emotion/drive/social/
  benefit/harm/self ATTRIBUTE COLUMNS (1.5-A), brain-derived, lock-clean. This REPLACES the first
  draft's "supply a valence primitive by hand": Binder's `Harm`/`Benefit`/`Pleasant`/`Unpleasant`/
  `Angry`/`Fearful` axes ARE the grounded valence-space, brain-derived, not invented. NOTE (per the
  corrected 1.5-A): abstract concepts like `anger`/`revenge`/`harm`/`help` are NOT Binder rows and
  are grounded by COMPOSITION over these dimensions (next bullet), not by lookup.
- The **who-is-affected / causal-role affectedness** (harm/help TOWARD a target) — REUSE the
  verb-affectedness lexicon (1.5-D). Not re-supplied.
- The **appraisal DIMENSIONS as a computational schema** (goal-relevance, congruence, causal-
  attribution-to-agent, coping-potential) — SUPPLY BY HAND (genuinely not on disk): a fixed small
  sequence-of-checks per Scherer's Component Process Model (explicitly a check-sequence, not a
  learned classifier), the same status as object-permanence's continuity/cohesion checks. This
  schema READS its inputs from the reused grounded features above (Binder valence, animacy agent-
  capability, verb-affectedness target-role) rather than from hand-invented scalars.
- The **goal representational slot** (an agent directed at an outcome with a preference) — SUPPLY
  minimally as the simulation's state type (2b); the Trabasso goal->causal organ already consumes
  goal states, so this is a slot, not a new grounding.
- The **false-belief/nested-belief machinery** — REUSE the Sally-Anne organ (1.5-F), as-is.

**EXTENSION beyond the directly-grounded base** — REUSE the Harnad/Cangelosi grounding-transfer
mechanism (1.5-B): affective/goal words the corpus introduces that are NOT Binder-rated get
grounded by COMPOSITION over the Binder base + situated structure (e.g. "revenge" is not a Binder
row, but composes as harm-valence [Binder Harm] toward-other [self/other from binding] after-being-
harmed-by-that-other [the dynamic mapping earned in 2b]). No new sensorimotor/experiential data
needed for the extension — that is the whole point of grounding transfer.

**EARN VIA A MINIMAL GROUNDING SIMULATION** (the ONLY genuinely-new build — the dynamic/temporal
structure that no lexicon or rating table contains, per 1.5's "what's genuinely new"; this is
where "you can't learn it from a book" gets its buildable answer):
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

**Appraisal computation** (SUPPLIED architecture, per 2a; reads REUSED grounded features): after
each event, compute the fixed dimension-vector (goal-relevance: does this event touch MY goal;
congruence: did it help or hurt — sourced from Binder Harm/Benefit valence [1.5-A] + verb-
affectedness target-role [1.5-D]; causal-attribution: was there an identifiable AGENT cause
[animacy_lexicon agent_capable, 1.5-C] vs. accidental/environmental; coping-potential: do I have
an available action that could address the blocker). This is a deterministic function of world-
state + action-log + the reused grounded lexicons, NOT a learned component — same status as the
object-permanence continuity check. Note it consumes the STATIC grounded core rather than
re-inventing valence/agency inline.

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

## 3.5 The grounded foundation is a LIVING, SELF-EXTENDING STORE (first-class architecture, USER)

The foundation is NOT a static supplied table that is built once and frozen. It is a living store
that ADDS to its own grounded knowledge whenever it grounds something NEW that QUALIFIES — i.e.
the foundation IS the self-improving reader, and its improving target is its OWN grounded
knowledge. All three pieces already exist in-project; this is composition, not invention.

### Architecture (compose 3 existing pieces)
1. **Supplied grounded CORE** = the Binder affect/agency DIMENSION space (1.5-A) + the reused
   core primitives (animacy/agency 1.5-C, verb-affectedness 1.5-D) + the appraisal schema (2a) +
   the earned dynamic mapping (2b). This is the seed the store starts from.
2. **`hdlab/self_improving_loop.py` consolidation = THE QUALIFICATION GATE.** The already-built,
   already-certified coherence-gated keep/revert controller (3 cycles, 4 fix-levers, 2 falsified;
   atoms 29613-29625) is repurposed: instead of gating a coref fix, it gates a WRITE-BACK to the
   grounded store. Its consolidation ledger + FALSE-CONSOLIDATION detection
   ([[feedback_verify_self_improving_loop_via_consolidation_observability_false_consolidation_USER_2026-08-02]])
   is exactly the mechanism that must guard the store from poison.
3. **Harnad grounding-TRANSFER (1.5-B) = the GROWTH OPERATOR.** New concepts become grounded by
   composition over already-grounded primitives; the store records the composition (provenance),
   not a distributional guess.

### What QUALIFIES to be written into the store (the gate — guard HARD; false-consolidation here
poisons the foundation itself, which is worse than a transient reading error)
- **(a) GROUNDING-TRANSFER**: composable from ALREADY-grounded primitives (inherits grounding, no
  new experience needed) — e.g. "revenge" = Harm-toward-other-after-being-harmed-by-that-other,
  every term of which is already grounded. WRITE (with the composition recorded as provenance).
- **(b) EXPERIENTIAL**: grounded via the 2b simulation (the earned dynamic mapping). WRITE.
- **(c) VERIFIED-RELATIONAL**: earned by error-driven differentiation over VERIFIED relations,
  past a confidence/coherence gate. WRITE.
- **NOT written**: distributional guesses (the exact failure mode of tonight's arc); low-confidence
  entries below the coherence gate; anything the false-consolidation ledger flags as inconsistent
  with the existing grounded store. REFUSE.

### The grounded-store data structure (glass-box, inspectable, append-only-with-provenance)
Each entry (one JSONL record per grounded concept, mirroring the substrate's existing
append-only-with-provenance store convention):
```
{ concept, grounding_TYPE: {supplied_core | transfer | experiential | verified_relational},
  grounding_VALUE: <dimension-vector for core, OR composition-expression for transfer,
                    OR earned-mapping-ref for experiential>,
  provenance: <source primitives + composition, OR simulation-episode-refs, OR relation-refs>,
  confidence, consolidation_cycle, coherence_at_write, superseded_by }
```
Append-only (never overwrite; supersede-with-provenance, matching the store-write discipline);
every entry is a small READABLE record (glass-box — no hidden embedding is ever written; the
grounding VALUE for a composed concept is a symbolic composition expression, not an opaque vector).
Inspectable: any concept's grounding can be traced back through its provenance chain to supplied
core primitives (the transfer closure) or to simulation episodes / verified relations.

### The write-back gate (mechanism)
On a candidate new grounding: (1) classify its TYPE (a/b/c above); (2) compute coherence of the
candidate against the existing store via the self_improving_loop coherence check; (3) run
false-consolidation detection (does adding this entry make the store internally inconsistent, or
contradict a higher-confidence existing grounding?); (4) KEEP (write, record consolidation_cycle
+ coherence_at_write) or REVERT (refuse, log to the false-consolidation ledger with reason). This
is the SAME keep/revert controller already certified, pointed at the store instead of at a reading
fix.

### Can-fail (the headline safety metric = FALSE-CONSOLIDATION RATE)
Pre-registration-shape: feed the store a stream of candidate groundings, a KNOWN fraction of which
are CORRECT (valid transfer compositions / valid experiential groundings) and a KNOWN fraction
INCORRECT (distributional guesses, contradictory compositions, low-confidence noise) — held-out,
adversarially constructed.
- **Discriminator**: does the store GROW with the correct groundings (write-acceptance rate on
  correct candidates high) while REFUSING the incorrect ones (false-consolidation rate = fraction
  of INCORRECT candidates wrongly written — LOW)?
- **Envelope-fail bands**: PASS = high correct-acceptance AND false-consolidation rate below a
  pre-set safety threshold, with the ledger correctly logging every refusal reason. PARTIAL =
  refuses incorrect but also refuses too many correct (over-conservative gate — informative, tune
  the coherence threshold). FAIL = false-consolidation rate not below the random/ungated floor
  (the gate isn't discriminating — the store would self-poison; block the whole living-store
  feature until fixed, because a poisoned foundation corrupts all downstream reading).
- **Brain-fidelity note**: consolidation-gated write-back is the memory-systems analog of
  systems consolidation (hippocampal->neocortical), where only coherent, schema-consistent
  memories get consolidated and schema-INconsistent ones are gated/flagged — the false-
  consolidation gate is the substrate's version of that schema-consistency check.

This makes the foundation self-extending WITHOUT reintroducing the distributional-guessing failure
the whole program exists to fix: the store only grows by grounded, provenance-carrying, coherence-
gated additions, and its safety is a measured, headline metric.

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
- **Living self-extending store (3.5)**: lock-clean because every write is (a) transfer-composed
  from grounded primitives, (b) experiential from the simulation, or (c) verified-relational past
  a coherence gate — NEVER a distributional guess or a borrowed vector; the store holds symbolic
  composition expressions + provenance, no hidden embeddings; the write-back gate REUSES the
  already-certified self_improving_loop consolidation controller. Directly honors the USER
  false-consolidation-observability directive.

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
| **Binder experiential DIMENSIONS** (emotion/drive/social/harm/benefit/self as COLUMNS) `data/corpora/binder/binder2016_ratings.csv` (535 rows × 85 cols, disk-verified) | **REUSED as the grounded DIMENSION SPACE** — right grounding TYPE for affect (unlike the capped science-tie use). Abstract concepts (anger/revenge/harm/help) are NOT rows → grounded by COMPOSITION over the dimensions, not lookup |
| **animacy_lexicon.py** (agent/object, agent_capable) | **REUSED AS-IS** — Spelke agent-vs-object core knowledge, already glass-box |
| **Verb-affectedness lexicon** (328 verbs, who-is-affected) | **REUSED** — harm/help causal-role + target-affectedness grounding |
| **Harnad/Cangelosi grounding-transfer** (`notes/research_word_grounding_lexicon_..._2026-07-16.md`) | **REUSED** — the extension mechanism: grounded base + composition, no new experience |
| Spelke core-knowledge citations | REUSED (`notes/drill_language_world_model_framing.md`, verbatim, disk-verified) |
| Sally-Anne false-belief ToM organ | REUSED AS-IS (HARD_PASS, `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json`) |
| Situated-structure agent->target->action->valence parse | REUSED, in-flight test a7a370e2 becomes the reading-side FEEDER into the grounded function |
| Coref / situation_model_accumulate / CausalLinkRegister / Trabasso goal->causal | REUSED AS-IS, become CONSUMERS of the grounded appraisal function |
| Appraisal-dimension SCHEMA (goal-relevance/congruence/causal-attribution/coping-potential, reading the reused grounded features) | NEW (small) — supplied by hand per Scherer CPM; a check-sequence over reused lexicons, not new grounding |
| **Minimal grounding-simulation + earned DYNAMIC appraisal-outcome -> action-tendency mapping** (blocked-goal->anger->retaliate over time, held-out generalization) | **NEW — the ONLY substantial new build**; the temporal-causal structure no lexicon contains; first buildable artifact, spec in 2b |
| Intentional-vs-accidental causal attribution label on CausalLinkRegister edges | NEW (small extension) |
| **Living self-extending grounded STORE** (append-only-with-provenance, glass-box) | **NEW STRUCTURE, REUSED GATE** — data structure is new; the qualification gate = `hdlab/self_improving_loop.py` consolidation + false-consolidation detection REUSED (3.5); growth operator = Harnad transfer REUSED |
| `hdlab/self_improving_loop.py` consolidation / false-consolidation ledger | REUSED as the store WRITE-BACK gate (was: reading-fix keep/revert controller) |

## 7. Recommended next step (not authorized by this doc)

Design research is complete, and the revision confirms the buildable surface is SMALL because the
static grounded core already exists (1.5). The next step is a pre-reg for the 2b simulation cell
— which now only has to earn the DYNAMIC mapping, reading grounded features from the reused
Binder/animacy/affectedness lexicons rather than inventing them (small,
CPU-cheap, discrete-world, no text) with the 2c can-fail bands — that is an exp_dev-shaped
build, not a design task, and is intentionally NOT dispatched from this doc per the task
constraint (design research only, no cell authoring). Flagging it as the concrete next action
for the USER/next cycle: build the minimal grounding simulation (2b), verify the three-floor
can-fail (2c) on held-out agents/goals, and if PASS, wire it as the appraisal-function consumer
for the in-flight situated-structure test (a7a370e2).
