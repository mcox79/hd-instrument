---
problem: the_situation_model_has_no_goal_intention_dimension
status: SOLVED
bar: "PASS = a glass-box GOAL/INTENTION dimension (a per-agent goal register populated from explicit purpose/desire/intention constructions + an abductive goal-inference rule over the reader's event stream; NO external LLM) whose `goal` QA answers on real narrative (a `goal` per_dimension row) score CI-separated over the strongest trivial floor (most-recent-action / physical-cause), with a shuffled-goal-agent info-free twin LOSING CI-separated and NO regression on the other dimensions (additive). Report CI half-width + null p95; recompute the floor on the item's own population. A rigorous located NEGATIVE — goals are not recoverable glass-box on natural text beyond the explicit-purpose slice, with the named cause + number (e.g. abductive goal inference needs the meaning/world-knowledge channel) — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed) + adds the `goal` board arm."
result: "A glass-box per-agent GOAL REGISTER over the reader's OWN extraction (frontend POS tagger + coref; NO spaCy on the inference path, NO LLM), on 100 real LitBank narrative docs. TWO goal-QA question types, each CI-separated over its strongest trivial floor with the info-free twin LOSING. (A) 'What is X trying to do?' on the RELIABLE explicit-construction slice (desire/intend/try + in-order-to, n=243): model 0.5309 vs most-recent-action floor 0.2016 (paired doc-cluster bootstrap diff CI [+0.2332,+0.4292], half-width 0.098) AND vs shuffled-agent twin 0.0288 (CI [+0.436,+0.5714]); whole-WANT twin null p95 0.0165 << model 0.6369. (B) 'Why did X do ACTION?' goal-why (n=1372): goal register 0.9796 vs the PHYSICAL-CAUSE dimension 0.0408 (diff CI [+0.9239,+0.9533], half-width 0.0147) -- and the CONVERSE (n=461 physical because/so questions): the causal dimension 0.8503 vs the goal register 0.0108, so goal-why and physical-cause are DISJOINT, complementary dimensions (Malle reason-vs-cause). Extraction faithfulness vs a spaCy ORACLE (reference-only, 25 docs): explicit-slice goal-head precision 0.85 (recall 1.0) vs bare-purpose 0.33. PINNED status field on authored gold (n=12): track_status 1.000 (satisfied 5/5, active 4/4, failed 3/3) vs a no-status floor 0.333."
floor: "Strongest floors actually run, recomputed on each item's own population: (A) MOST-RECENT-ACTION (X's most recent event predicate) 0.2016 on the explicit slice / 0.141 whole-WANT -- model CI-separated above; also the SHUFFLED-AGENT info-free twin 0.0288 / 0.011 (null p95 0.0165). (B) the PHYSICAL-CAUSE dimension (sm.causal_links) + adjacency 0.0408 -- model CI-separated above; the converse floor (causal dim on physical questions) 0.8503 vs goal register 0.0108 proves disjointness. (Status) no-status 'always-active' floor 0.333 vs 1.000."
controls: "(1) INFO-FREE TWIN = shuffled goal->agent binding (derangement, 200 seeds): whole-WANT null p95 0.0165, LOSES CI-separated (model 0.637 > 0.0165) -- excludes 'the register works from a non-informative binding'. (2) POSITIVE CONTROL (multi-agent passages, n=1453): model-right & agent-blind-floor-wrong = 827 vs the reverse = 4 -- earns 'binds the goal to the RIGHT agent', not the salient/nearest one. (3) COMPLEMENTARITY / disjointness (n=461): on physical because/so questions the causal dim answers (0.850) and the goal register does NOT (0.011), the converse of arm B -- excludes 'goal-why is just physical causation relabelled'. (4) spaCy ORACLE extraction (reference-only, never on the inference path): explicit-slice precision 0.85 validates the gold is REAL not circular; bare-purpose 0.33 LOCATES the parse-gated negative. (5) STATUS field on authored gold across all three states (satisfied/active/failed), floor 0.333 -- excludes 'a static extractor with no tracking'. (6) ADDITIVE: the goal read is a pure addition (new sm.goal_register + query callables) touching no other dimension field -- the other dimensions are byte-identical, mirroring _read_belief/_read_world_state."
files_changed: "experiments/goal_register.py (the promotable CORE: glass-box explicit purpose/desire/intention extractor + per-agent GoalRegister + track_status status field, POS from the frontend tagger, NO spaCy/LLM); experiments/exp_goal_register_qa_v1.py (the measurement: WANT + goal-why + complementarity + positive control + spaCy-oracle faithfulness + authored status, doc-cluster bootstrap CI + twin null p95); verification/test_goal_register.py (scaffold-free witness, 8/8 PASS, reads landed metrics + a from-source unit); notes/problems/the_situation_model_has_no_goal_intention_dimension/{research_goal_intention_brain_mechanism_2026-09-04.md, SOLVED.md, OWNER_NOTES.md}; data/exp_goal_register_qa_v1/metrics.json. hdlab/ UNTOUCHED (proposed default-off track_goals wire below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_goal_register.py   # 8/8, re-runs NO landed cell (reads metrics.json + a constructed from-source unit). Full recompute (optional, ~7 min): .venv/Scripts/python.exe experiments/exp_goal_register_qa_v1.py --run --oracle-docs 25"
---

# The reader now has a GOAL/INTENTION dimension -- "what is X trying to do, and why did X act?"

## The one-line answer
The reader tracked who/what/when/where, physical causation, belief, state and possession -- but had NO
representation of what any agent is TRYING to achieve (the missing 5th Zwaan-Radvansky event-indexing
dimension, intentionality). I built a glass-box per-agent GOAL REGISTER: it extracts each agent's goals
from the reliable explicit purpose/desire/intention constructions (Levin desiderative/intention/try verbs
+ the "in order to"/"so as to" purpose class), binds them to the resolved agent, and carries a status
field (active/satisfied/failed). On 100 LitBank docs it answers "what is X trying to do" CI-separated over
a most-recent-action floor (0.531 vs 0.202 on the reliable slice) with a shuffled-agent twin LOSING (null
p95 0.0165), answers goal-based "why" where the physical-cause dimension cannot (0.98 vs 0.04) AND vice
versa (the two dimensions are DISJOINT), binds the right agent (827 vs 4), and recovers goal status (1.000
vs 0.333). The LOCATED NEGATIVE is exactly the explicit-vs-inferred split the brief predicted: bare-purpose
adjuncts are PARSE-gated (precision 0.33 vs a spaCy oracle) and unstated/abductive goals (Tier-2 "why this
action over the alternatives") need the world-knowledge/meaning channel we do not have.

## §0 The brain opening move (which structure, replicate or substitute?)
Grounded in the 5-lane research drill (`research_goal_intention_brain_mechanism_2026-09-04.md`):
- **PINNED:** goal/intention is a distinct **dmPFC-anchored** mentalizing computation (Spunt/Lieberman
  "Why > How", 4 studies), separate from belief (TPJ) though sharing mentalizing infrastructure, and
  **DECISIVELY separate from physical causation** (Malle 1999/2004 reason-vs-cause: the generic cause
  categories give null effects, reason categories d=0.4-0.7 on the same data; the "in order to / so that"
  family is reason-specific). => a SEPARATE register from belief and from the causal dimension. **Desire is
  FOLDED into the goal/intention register** (weakest-evidenced for its own register).
- **PINNED:** narrative goal structure carries a STATUS field (active/satisfied/failed), satisfaction =
  graded decay not deletion (Lutz & Radvansky 1997: failed > completed > neutral), reinstatement = the
  last-unsatisfied-superordinate goal has priority (Suh & Trabasso 1993, four methodologies).
- **PINNED tiering (the decisive lane):** Tier-0 "what the action TARGETED" (Woodward agent->object
  binding) is structurally recoverable; **Tier-2 "why THIS action over the alternatives" (Baker/
  Jara-Ettinger inverse planning) REQUIRES the world-knowledge channel -- the located negative** (text has
  no perceptual analog to the path-length/effort cost that makes vision-domain goal inference structural).
- **PINNED anchor:** the reliable non-circular gold is the "in order to"/"so as to" purpose class + the
  Levin desiderative/intention verb classes (PropBank tags ARGM-PRP distinct from ARGM-CAU at corpus scale).
- **OUR-INVENTION-UNDER-TEST (swept, not adopted):** the exact cue set, the subject-attachment rule, the
  goal-span extent, the satisfaction-match rule, the register data structure.

REUSE (not a new organ): the register consumes the reader's EXISTING entity/coref stream (agent binding)
and event stream (status tracking), and mirrors the belief/world-state register+readout pattern exactly.
NOTE the disambiguation that motivated the whole build: the reader already collects a thematic-role "goal"
(`wired_extra_roles`, the DESTINATION argument of a motion verb -- "to the market"); that is DISJOINT from
the intentional goal (what the agent WANTS). This dimension builds the intentional one.

## §1 What I built (the mechanism)
`experiments/goal_register.py`: a glass-box extractor over (tokens, UPOS from the frontend tagger) that
emits `Goal(agent, goal_head, goal_text, kind, source_verb, sent_idx, negated, status)` for three
construction families, then binds each goal's surface subject to a canonical entity via the reader's
coref, then tracks status against the event stream:
- **desire/intend/try matrix verb + infinitival complement** (kind = desire/intend/try): reliable, the
  matrix verb is the unambiguous marker.
- **explicit purpose markers** "in order to"/"so as to" (kind = purpose_marked): the "because"-analog for
  purpose.
- **bare "to VINF" purpose adjunct** attached to the nearest preceding finite action verb, FILTERED by the
  "in order to" substitution test (a raising/aspectual/desire governor adjacent to "to" is rejected --
  "began to rain", "seemed to know") (kind = purpose_bare): the Tier-2-with-filter slice.
The `GoalRegister` answers off the accumulated register (never re-reading): `wants(agent)` (the current =
most-recent unsatisfied goal, reinstatement order), `why(action, agent)` (the goal-purpose behind an
action, distinct from a physical cause), `achieved(agent, goal)` (status). `track_status` sets
active/satisfied/failed from the event stream (satisfied = a later same-agent event realizes the goal head;
failed = explicit negation).

## §2 What I measured (100 LitBank docs; real-corpus incidence)
Incidence (`metrics.json` slice_counts): 243 explicit constructions (desire 108 / intend 55 / try 67 /
in-order-to 13) + 1211 bare-purpose candidates across 100 docs -- a REAL-corpus population (unlike the
belief timeline, which had to author its gold).

| arm | model | floor | twin | CI (model - floor) | verdict |
|---|---|---|---|---|---|
| **WANT explicit** (n=243) | **0.531** | 0.202 (most-recent-action) | 0.029 (shuffled agent) | [+0.233,+0.429] | CI-SEP over both |
| WANT all (n=1454) | 0.637 | 0.141 | 0.011 (null p95 0.0165) | [+0.447,+0.543] | CI-SEP; twin loses |
| **WHY goal-why** (n=1372) | **0.980** | 0.041 (physical-cause dim) | -- | [+0.924,+0.953] | CI-SEP; goals != cause |
| complementarity (n=461 physical q) | 0.011 (goal reg) | **0.850** (causal dim) | -- | -- | DISJOINT (converse) |
| positive control (n=1453) | 827 right/floor-wrong | 4 reverse | -- | -- | binds the agent |
| status authored (n=12) | **1.000** | 0.333 (no-status) | -- | -- | active/satisfied/failed |
| oracle extraction (25 docs) | explicit prec **0.85** | bare-purpose prec **0.33** | -- | -- | explicit reliable / bare parse-gated |

## §3 The located negative (the brief's sanctioned FULL PASS), with named cause + number
Two disjoint failure modes, both PINNED by the research drill:
1. **Bare-purpose adjuncts are PARSE-gated.** On real 19c literary prose the glass-box register (POS
   tagger, no dependency parse) mis-attaches many "to VINF" -- extraposed subjects ("it would not be
   wonderful to meet a Megalosaurus" mis-read as "waters retired to meet"), complements, relatives -- so
   bare-purpose goal-head precision is **0.33 vs the spaCy oracle** (vs 0.85 on the explicit slice). The
   attachment + purpose-vs-extraposition distinction genuinely NEEDS a real dependency parse -- the SAME
   parser wall the relcl/causal dimensions hit (filed: `parser_arceager`, `the_relcl_parser_is_too_weak`).
2. **Unstated / abductive goals (Tier-2) need the meaning channel.** "He picked up the knife" -> goal =
   "to cut" / "to attack" is inference over world-knowledge of typical costs/utilities; text has no
   perceptual analog to the path-length/effort signal that makes vision-domain teleology structural
   (Graesser/Trabasso, Sanford/Garrod, Bower/Black/Turner all unanimous). This is the SAME meaning-channel
   gate the belief inference-edge, WSD, and consolidation drills hit. Also parse/outcome-gated:
   thwart-by-OUTCOME ("tried to X but Y stopped him") is not covered by the status field (needs the outcome
   channel); explicit-negation failure IS.

## §4 Performance vs a competent reader (the mechanism-diff)
On the RELIABLE explicit slice the glass-box register matches a spaCy oracle at precision 0.85 / recall
1.0 -- it finds every desire/intend/try goal the competent parser does. Where we differ is exactly the
Tier-2/parse tail above: the competent parser correctly rejects the bare-purpose mis-attachments (its
dependency parse resolves the attachment), and neither the parser nor we can do open-ended abductive goal
inference without a utility/world model. So: role-BINDING and explicit-construction extraction are at the
competent-reader ceiling; the loss is upstream (register-native parse) and in the gated meaning channel --
the same signal-loss profile the who-did-what / belief dimensions report.

## KEY REALIZATIONS (the enabling moves)
1. **The reader's existing "goal" is the WRONG goal.** `wired_extra_roles` already carries a thematic-role
   "goal" -- but that is the DESTINATION argument of a motion verb ("to the market"), not the intentional
   goal (what the agent WANTS). Disambiguating these was the whole unlock; they are disjoint construction
   classes, exactly as the brief warned.
2. **Goal-why vs physical-cause is the non-circular test.** The gold (purpose) and the physical-cause floor
   (because/so) are DISJOINT construction classes, so "the register produces a purpose where the causal
   dimension produces a cause" is a genuine, non-circular capability -- and the CONVERSE (cause dim wins on
   physical questions, register ~0) proves complementarity, not superiority. This is the Malle reason-vs-
   cause signature made measurable.
3. **The explicit-vs-inferred split falls out of the spaCy-oracle precision by slice.** explicit 0.85 /
   bare-purpose 0.33 IS the located negative -- the reliable anchor and the parse-gated tail, separated by
   a number, not asserted.
4. **The floor/twin carry the epistemic weight, not the model number.** Like the belief timeline: gold
   built from the same grammar the register reads means the model number is a within-dimension readout; the
   most-recent-action floor (0.20), the shuffled-agent twin (0.03), the physical-cause floor (0.04), and
   the spaCy oracle are the independent methods that make it a result.

## §5 FOR STRATEGY (proposed hdlab landing -- Q111, default-off, you own it)
Mirror `_read_belief` / `_read_world_state` exactly (additive, lazy, default-off):
1. Promote `experiments/goal_register.py` -> `hdlab/goal_register.py` (spaCy-free core: extractor +
   GoalRegister + track_status).
2. Add a default-off `track_goals` flag to `SituationReader`; in `read()`, `if self.track_goals:
   self._read_goals(sm, sents)` (runs after coref+events so agents/status bind to the final stream).
   `_read_goals` sets `sm.goal_register` and binds `sm.wants(agent)` / `sm.why(action, agent)` /
   `sm.achieved(agent, goal)` query callables. Additive -- no other dimension field changes (byte-identical
   off vs on, witnessed structurally).
3. Add a `goal` per_dimension row to `experiments/exp_situation_model_qa_v1.py` (a `build_goal_questions`
   + `_answer_goal` reading `sm.goal_register`, the SAME router), gated to the explicit slice + the
   goal-why vs physical-cause floor. The `goal` board arm.

## §6 AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
Add a **GOAL/INTENTION dimension** entry to the situation-model section: **PINNED** -- distinct dmPFC
mentalizing computation (Spunt/Lieberman Why>How), separate from belief (TPJ; desire FOLDED in, not a
third register) and DISJOINT from physical causation (Malle reason-vs-cause, measured complementarity);
STATUS field active/satisfied/failed with graded decay (Lutz & Radvansky); reinstatement = last-unsatisfied
-superordinate (Suh & Trabasso). **OUR-INVENTION-UNDER-TEST:** cue set / subject-attachment / goal-span /
status-match / register structure (swept). **Located negative folded:** bare-purpose adjunct extraction is
parse-gated (0.33 vs oracle) and Tier-2 abductive "why this over that" needs the meaning channel -- the
explicit-vs-inferred split. This is the 5th and last classic Zwaan-Radvansky dimension; the reader now has
all five (time/space/causation/protagonist+belief/INTENTIONALITY).

## §7 ADJACENT COMPONENTS evaluated (candidate next problems -- fidelity + optimization)
- **Register-native dependency parse (the bare-purpose ceiling)** -- OUR-INVENTION placeholder (POS-only
  attachment). A real parse would lift bare-purpose from 0.33 toward the explicit 0.85; it is the same
  filed parser wall (`parser_arceager`, filler-gap). Leverage: the largest single lift for the goal
  dimension. High-value follow-on.
- **The meaning/world-knowledge channel (Tier-2 abductive goals)** -- the located-negative gate, shared
  with the belief-inference edge / WSD / consolidation drills. Neurally the naive-utility-calculus /
  inverse-planning engine (Baker et al.); the belief timeline's POMDP inverse-planning next-brief is the
  SAME engine viewed from desire rather than belief -- a natural unification.
- **Goal HIERARCHY (superordinate/subordinate, reinstatement over distance)** -- PINNED (Suh & Trabasso)
  but only the flat register + reinstatement-by-recency is built; a goal->subgoal graph with connectivity-
  based salience (Trabasso & van den Broek 1986) is the richer follow-on. OUR-INVENTION-flat today.
- **Thwart-by-outcome status** -- "tried to X but Y stopped him" needs the outcome/meaning channel; only
  explicit-negation failure is covered. Adjacent to the meaning channel.
- **Goal x belief composition** -- the mentalizing network binds goals AND beliefs; "X wants Y because X
  believes Z" composes this register with the belief timeline. A clean next reasoning problem.

## TLDR (plain English)
When we read a story, most of what we understand is what people are TRYING to do -- she went to the market
to buy bread, he lied because he wanted to protect her. Our reader could say what happened, who did it,
when, where, what physically caused what, and what characters believed -- but it had no idea what anyone
WANTED. I gave it a goal-tracker: it reads each character's goals from the plain "wanted to / tried to / in
order to" phrasings, ties each goal to the right character, and tracks whether the goal was reached. On 100
real story chapters it answers "what is she trying to do" far better than just naming her last action, and
answers "why did he do that" with the GOAL (to buy bread) where the physical-cause tracker draws a blank --
and, tellingly, the physical-cause tracker wins on physical "why" questions where the goal-tracker draws a
blank, so the two are genuinely different tools that each cover what the other can't, exactly as the
psychology says. It also correctly says whether a goal was reached, abandoned, or still open on clean
examples. Where it honestly falls short: goals that are only IMPLIED (never said out loud) need real-world
knowledge we do not yet have, and the messier "did-something-in-order-to" phrasings on old literary prose
need a better grammar parser than the lightweight one it uses -- both measured, both named. This is the
fifth and last of the classic story-understanding dimensions; the reader now has all five.

## QUESTIONS
None.

## NEXT STEPS
Land the default-off `track_goals` wire + the `goal` board arm (§5, Q111). Then the highest-value follow-on
is the register-native dependency parse (lifts the bare-purpose slice, the filed parser wall); the Tier-2
abductive-goal engine is the meaning-channel successor (unifies with the belief timeline's inverse-planning
next-brief); goal x belief composition is the clean next reasoning problem.
