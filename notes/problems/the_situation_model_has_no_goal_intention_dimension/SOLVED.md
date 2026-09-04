---
problem: the_situation_model_has_no_goal_intention_dimension
status: SOLVED
bar: "PASS = a glass-box GOAL/INTENTION dimension (a per-agent goal register populated from explicit purpose/desire/intention constructions + an abductive goal-inference rule over the reader's event stream; NO external LLM) whose `goal` QA answers on real narrative (a `goal` per_dimension row) score CI-separated over the strongest trivial floor (most-recent-action / physical-cause), with a shuffled-goal-agent info-free twin LOSING CI-separated and NO regression on the other dimensions (additive). Report CI half-width + null p95; recompute the floor on the item's own population. A rigorous located NEGATIVE — goals are not recoverable glass-box on natural text beyond the explicit-purpose slice, with the named cause + number (e.g. abductive goal inference needs the meaning/world-knowledge channel) — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed) + adds the `goal` board arm."
result: "A glass-box per-agent GOAL REGISTER over the reader's OWN extraction (frontend POS tagger + coref; NO spaCy on the inference path, NO LLM), on 100 real LitBank narrative docs. TWO goal-QA question types, each CI-separated over its strongest trivial floor with the info-free twin LOSING. (A) 'What is X trying to do?' on the RELIABLE explicit-construction slice (desire/intend/try + in-order-to, n=234 with the upstream lexicalist parser + passive-agent guard, up from 0.531 at n=243 with the heuristic): model 0.6068 vs most-recent-action floor 0.1368 (paired doc-cluster bootstrap diff CI-separated) AND vs shuffled-agent twin 0.0171 (CI-separated); whole-WANT twin null p95 0.0165 << model 0.6369. (B) 'Why did X do ACTION?' goal-why (n=1372): goal register 0.9796 vs the PHYSICAL-CAUSE dimension 0.0408 (diff CI [+0.9239,+0.9533], half-width 0.0147) -- and the CONVERSE (n=461 physical because/so questions): the causal dimension 0.8503 vs the goal register 0.0108, so goal-why and physical-cause are DISJOINT, complementary dimensions (Malle reason-vs-cause). Extraction faithfulness vs a spaCy ORACLE (reference-only, 25 docs): explicit-slice goal-head precision 0.85 (recall 1.0) vs bare-purpose 0.33. PINNED status field on authored gold (n=12): track_status 1.000 (satisfied 5/5, active 4/4, failed 3/3) vs a no-status floor 0.333. PINNED reinstatement (Suh & Trabasso 1993, authored n=10): after a subgoal is satisfied, status-gated wants() reinstates the older superordinate goal at 1.000 vs a status-blind RECENCY floor 0.000 (returns the satisfied subgoal every time), status-shuffle info-free twin null p95 0.800 < 1.000."
floor: "Strongest floors actually run, recomputed on each item's own population: (A) MOST-RECENT-ACTION (X's most recent event predicate) 0.2016 on the explicit slice / 0.141 whole-WANT -- model CI-separated above; also the SHUFFLED-AGENT info-free twin 0.0288 / 0.011 (null p95 0.0165). (B) the PHYSICAL-CAUSE dimension (sm.causal_links) + adjacency 0.0408 -- model CI-separated above; the converse floor (causal dim on physical questions) 0.8503 vs goal register 0.0108 proves disjointness. (Status) no-status 'always-active' floor 0.333 vs 1.000."
controls: "(1) INFO-FREE TWIN = shuffled goal->agent binding (derangement, 200 seeds): whole-WANT null p95 0.0165, LOSES CI-separated (model 0.637 > 0.0165) -- excludes 'the register works from a non-informative binding'. (2) POSITIVE CONTROL (multi-agent passages, n=1453): model-right & agent-blind-floor-wrong = 827 vs the reverse = 4 -- earns 'binds the goal to the RIGHT agent', not the salient/nearest one. (3) COMPLEMENTARITY / disjointness (n=461): on physical because/so questions the causal dim answers (0.850) and the goal register does NOT (0.011), the converse of arm B -- excludes 'goal-why is just physical causation relabelled'. (4) spaCy ORACLE extraction (reference-only, never on the inference path): explicit-slice precision 0.85 validates the gold is REAL not circular; bare-purpose 0.33 LOCATES the parse-gated negative. (5) STATUS field on authored gold across all three states (satisfied/active/failed), floor 0.333 -- excludes 'a static extractor with no tracking'. (5b) REINSTATEMENT (Suh & Trabasso, authored n=10): status-gated wants() 1.000 vs the status-blind RECENCY floor 0.000 vs the status-shuffle twin null p95 0.800 -- excludes 'a recency reader (most recent goal) is enough' and proves the PINNED superordinate-reinstatement mechanism, not just an assertion. (6) ADDITIVE: the goal read is a pure addition (new sm.goal_register + query callables) touching no other dimension field -- the other dimensions are byte-identical, mirroring _read_belief/_read_world_state."
files_changed: "experiments/goal_register.py (the promotable CORE: glass-box explicit purpose/desire/intention extractor + per-agent GoalRegister + track_status status field + the lexicalist subcat-frame/extraposition filter, POS from the frontend tagger, NO spaCy/LLM); experiments/verb_subcat_frames.py (UPSTREAM brain-foundational component: per-verb infinitive-complement SUBCATEGORIZATION FRAME derived from UD-EWT gold + extraposition-predicate set); data/verb_subcat_frames_v1/verb_subcat_frames_ud_ewt.json (the frame asset -- solver-owned static offline foundation; strategy ships it to data/frontend_assets/ at landing); experiments/exp_goal_register_qa_v1.py (the measurement: WANT + goal-why + complementarity + positive control + spaCy-oracle faithfulness A/B + authored status + reinstatement + the passive-agent guard, doc-cluster bootstrap CI + twin null p95); verification/test_goal_register.py (scaffold-free witness, 11/11 PASS, reads landed metrics + a from-source unit); notes/problems/the_situation_model_has_no_goal_intention_dimension/{research_goal_intention_brain_mechanism_2026-09-04.md, research_infinitive_attachment_brain_mechanism_2026-09-04.md, SOLVED.md, OWNER_NOTES.md}; data/exp_goal_register_qa_v1/metrics.json. hdlab/ UNTOUCHED (proposed default-off track_goals wire below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_goal_register.py   # 11/11, re-runs NO landed cell (reads metrics.json + a from-source unit). Rebuild the upstream frame asset (optional): .venv/Scripts/python.exe experiments/verb_subcat_frames.py --build . Full recompute (optional, ~10 min): .venv/Scripts/python.exe experiments/exp_goal_register_qa_v1.py --run --oracle-docs 12"
---

## INTEGRATED_BY_STRATEGY (2026-09-04) — EXCELLENT (a full-chain upgrade)
Reverified first-hand: `verification/test_goal_register.py` **11/11** + a new pure-hdlab landing witness `verification/test_goal_register_landing_organ.py` **6/6** (existing dims byte-identical track_goals off vs on across 3 docs → purely additive). Live goal-arm CI-separated (WANT-explicit 0.58 over floor 0.28 + twin 0.0; WHY 0.97 vs physical-cause 0.03).
- **WIRE LANDED (Q111), DEFAULT-ON** (no-default-off: additive + net-positive, mirrors the sibling situation-model dims): promoted `hdlab/goal_register.py` (stdlib+hdlab only — extractor + GoalRegister + track_status + the ported `make_canonicalizer`/`passive_agent_guard`/`_named_clusters`/`_norm`/`_PRONOUNS`, NO experiments dep) + `track_goals` flag (default TRUE) + `_read_goals` (mirrors `_read_belief`; sets `sm.goal_register` + `sm.wants`/`why`/`achieved`). Board `goal` arm registered in `exp_situation_model_qa_v1.py` (DIMENSIONS += 'goal', with_goal=True). +~0.24s/read.
- **THE FULL-CHAIN UPGRADE (owner "this solution is also a full chain upgrade"):** landed the upstream general parse-fidelity primitive `hdlab/verb_subcat_frames.py` + shipped `data/frontend_assets/verb_subcat_frames_ud_ewt.json` (lexicalist complement-vs-adjunct + extraposition; a GENERAL primitive usable beyond goals) + the passive-agent guard (PRO→matrix agent). Zero regression (the frame gates ONLY the bare-purpose branch).
- **§2b folded.** The reader now has ALL FIVE Zwaan-Radvansky dimensions.
- **ONE non-material deviation:** the reader's `sents` are lowercased (its convention) vs the experiment's original-case; A/B 30/31 explicit goals identical (0.968), the live arm independently CI-separated.
- **LOCATED NEGATIVE (a full pass):** bare-purpose adjuncts parse-gated (0.34 vs oracle → register-native parser); Tier-2 abductive goals → the meaning channel (P9). §7 follow-ons noted; the general subcat primitive is available to wire into broader infinitive-attachment (a chain lever beyond goals).

# The reader now has a GOAL/INTENTION dimension -- "what is X trying to do, and why did X act?"

## The one-line answer
The reader tracked who/what/when/where, physical causation, belief, state and possession -- but had NO
representation of what any agent is TRYING to achieve (the missing 5th Zwaan-Radvansky event-indexing
dimension, intentionality). I built a glass-box per-agent GOAL REGISTER: it extracts each agent's goals
from the reliable explicit purpose/desire/intention constructions (Levin desiderative/intention/try verbs
+ the "in order to"/"so as to" purpose class), binds them to the resolved agent, and carries a status
field (active/satisfied/failed). On 100 LitBank docs it answers "what is X trying to do" CI-separated over
a most-recent-action floor (0.607 vs 0.137 on the reliable slice, with the upstream lexicalist parser +
passive-agent guard; 0.531 with the heuristic) with a shuffled-agent twin LOSING (null
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
The `GoalRegister` answers off the accumulated register (never re-reading): `wants(agent)` (the current
goal via Suh-Trabasso REINSTATEMENT = the most-recent ACTIVE goal -- a satisfied subgoal deactivates and the
older still-open superordinate goal is reinstated), `why(action, agent)` (the goal-purpose behind an
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
| **reinstatement authored** (n=10) | **1.000** | 0.000 (recency, status-blind) | 0.800 (null p95) | -- | Suh-Trabasso superordinate reinstatement |
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
0. Promote the UPSTREAM component `experiments/verb_subcat_frames.py` -> `hdlab/verb_subcat_frames.py` +
   ship `data/frontend_assets/verb_subcat_frames_ud_ewt.json` (the lexicalist subcat-frame asset). It is a
   general parse-fidelity primitive (complement-vs-adjunct + extraposition) usable beyond goals.
1. Promote `experiments/goal_register.py` -> `hdlab/goal_register.py` (spaCy-free core: extractor +
   lexicalist subcat filter + GoalRegister + track_status), consuming the frame asset.
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
- **Goal HIERARCHY (superordinate/subordinate graph)** -- reinstatement itself is now MEASURED (status-gated
  wants() reinstates the superordinate at 1.000 vs a status-blind recency floor 0.000, Suh & Trabasso), but
  only via a FLAT status-gated register; an explicit goal->subgoal GRAPH with connectivity-based salience
  (Trabasso & van den Broek 1986: salience from connectivity, not hierarchy depth) and reinstatement over a
  distance of intervening material is the richer follow-on. OUR-INVENTION-flat on the graph today.
- **Thwart-by-outcome status** -- "tried to X but Y stopped him" needs the outcome/meaning channel; only
  explicit-negation failure is covered. Adjacent to the meaning channel.
- **Goal x belief composition** -- the mentalizing network binds goals AND beliefs; "X wants Y because X
  believes Z" composes this register with the belief timeline. A clean next reasoning problem.

## §8 UPSTREAM brain-foundational component -- the lexicalist SUBCATEGORIZATION-FRAME parser (owner directive 2026-09-04: "prototype an upstream brain foundational component... make it EXCEL and EXCEED... EVERY component brain foundational")
The parse-gated bare-purpose wall is an UPSTREAM parse problem. I prototyped the upstream fix as the
BRAIN'S ACTUAL mechanism (verified by two research drills, not cited after the fact):
`research_infinitive_attachment_brain_mechanism_2026-09-04.md`.
- **What the brain does (PINNED, ~0.85):** infinitive attachment (complement vs adjunct) is resolved by
  LEXICALIST CONSTRAINT-BASED parsing -- the verb's stored, frequency-weighted SUBCATEGORIZATION FRAME
  (MacDonald/Pearlmutter/Seidenberg 1994; Trueswell 1996; Garnsey 1997; Vosse-Kempen 2000 unification;
  Hagoort MUC + Snijders 2009 fMRI). For the CLEAR case (a verb lacks the infinitival-complement frame) the
  faithful mechanism is CONSTRAINT-SATISFACTION / FILTERING (the complement candidate is never licensed ->
  the adjunct reading wins by exclusion), which is exactly what I implemented. Pickering/Traxler/Crocker
  2000 shows a SOFT bias (not hard argmax) is right -- we keep the graded `p_complement` and threshold it.
- **What I built (3 upstream components, all glass-box, NO spaCy at inference):**
  1. `experiments/verb_subcat_frames.py` -- a per-verb infinitive-complement frame P(complement) DERIVED
     from the UD-EWT GOLD treebank (a static, offline-built FOUNDATION asset -- owner 2026-08-16; NOT the
     LitBank test set -> no leakage). Brain-faithful: the frame IS the lexical knowledge; the "be going to"
     FUTURE is excluded from go's frame (a grammaticalized auxiliary, not motion-go subcategorizing). Result:
     want/begin/try/seem = complement-takers (P>=0.92); go/come/stand = adjunct-hosts -- the correct split.
  2. EXTRAPOSITION detection (expletive-it + copula + an extraposition predicate; predicate set corpus-
     derived) -- "it would be wonderful to meet a Megalosaurus" is an extraposed subject, not a purpose
     adjunct (Li et al. 2009 JAIR; CGEL).
  3. PASSIVE-AGENT GUARD (Lane 4 / McCourt et al. 2015): PRO binds to the matrix AGENT -- the subject in
     ACTIVES but the IMPLICIT agent in PASSIVES ("the ship was sunk to collect the insurance" -> not "ship").
     The guard reuses the reader's VOICE-AWARE role extraction, never binding the patient.
- **Measured effect (100 docs; A/B vs the hardcoded heuristic, spaCy-oracle reference on 12 docs):** the fix
  DECISIVELY corrects the targeted cases (the smoke: "to meet a Megalosaurus" and "began to rain" dropped;
  "went to buy"/"rushed to watch" kept), removes ~120 net over-fires (bare-purpose 1211->1091), lifts
  extraction ALL-precision 0.396->0.403 (bare 0.340->0.344), and -- the downstream payoff -- **lifts the
  WANT-explicit goal-QA accuracy 0.531->0.607** (partly by not mis-binding passive-subject cases), with NO
  regression on any arm (WHY 0.966, positive control 816-vs-3, reinstatement 1.0, status 1.0).
- **ZERO REGRESSION on the other consumers (A/B, subcat OFF vs ON, all 100 docs):** the frame gates ONLY
  the bare-purpose branch, so the EXPLICIT consumer is BYTE-IDENTICAL -- WANT-explicit OFF 0.6068 == ON
  0.6068 (n=234 both); the bare slice is the only thing that changes (removes 116 over-fires, acc +0.001);
  WHY / positive-control / status / reinstatement show no capability regression (small n drops = fewer bare
  questions, not worse accuracy). Proven from source in the witness (W10, extract_goals off==on on the
  explicit kinds) and additive-by-construction on the OTHER reader dimensions (coref/events/temporal/causal
  /belief/state) -- my work modifies no file they read (the frame asset even lives in a solver-owned dir).
- **HONEST magnitude + the deeper wall:** the aggregate bare-purpose EXTRACTION precision lift is MODEST
  (+0.003) because the DOMINANT bare-purpose residual is not complement-vs-adjunct CLASSIFICATION (which the
  frame now handles brain-foundationally) but ATTACHMENT -- which "to VP" attaches to which verb, vs a
  relative-clause / noun-complement infinitive. Attachment needs the full DEPENDENCY PARSE. The reader's
  arc parser is documented 19c-NEGATIVE (a bad fit for this corpus), so the residual is a REGISTER-NATIVE
  PARSER (filed `parser_arceager` / a 19c-native parser), NOT reachable by the off-the-shelf parser -- and
  the brain-faithful attachment is itself lexicalist+incremental (Construal high-attachment), so the frame
  is the right primitive and the parser is the composition target. This is the refined located negative:
  the explicit slice is at the competent-reader ceiling (precision 0.857 == the oracle); the bare tail is
  attachment-parse-gated.

## §9 FULL BRAIN-FOUNDATIONAL AUDIT -- every computational step (owner directive 2026-09-04: "ENSURE that EVERYTHING is as close to brain foundational as possible; every calculation, averaging step")
Grounded in the two upstream research drills (`research_infinitive_attachment_brain_mechanism_2026-09-04.md`,
`research_goal_intention_brain_mechanism_2026-09-04.md`). Each MECHANISM step is PINNED (named brain
structure/computation, copied) or OUR-INVENTION-UNDER-TEST (flagged, swept). MEASUREMENT steps are
labelled HYGIENE -- they are how we MEASURE, deliberately NOT a brain claim (the mission is the mechanism;
measurement is hygiene). NO step is a convenient off-the-shelf substitute for a brain operation.

| # | step (operation) | brain status | note |
|---|---|---|---|
| 1 | goal-cue detection (Levin desiderative/intend/try verbs; in-order-to; bare-to) | **PINNED** | reliable anchor = Levin classes + PropBank ARGM-PRP; the cue LISTS are OUR-INVENTION-swept |
| 2 | subcat filter: complement-taker vs adjunct-host | **PINNED** | lexicalist constraint-satisfaction / FILTERING (MacDonald-Seidenberg 1994; Vosse-Kempen 2000); the brain-faithful mechanism for the clear case |
| 3 | P(complement)=xcomp/(xcomp+advcl) frequency ratio | **PINNED** | the brain stores FREQUENCY-WEIGHTED subcat frames (Trueswell 1996; Garnsey 1997) -- this "averaging" IS lexical experience, not a convenience average; graded (Pickering 2000: soft not argmax) |
| 4 | is_complement_taker threshold (tau=0.5) | OUR-INVENTION | a binary decision on the graded frame; tau SWEPT, not adopted |
| 5 | extraposition detection (expletive-it + copula + predicate) | **PINNED** | surface cue for extraposed subject (Li et al. 2009 JAIR; CGEL); predicate set corpus-DERIVED, not hand-listed |
| 6 | attachment (nearest preceding finite verb) | PINNED-ish / OUR-INVENTION | the brain attaches a purpose clause HIGH to the matrix event (Construal; A'ingae "TP adjunct"); nearest-finite-verb = the matrix verb in the dominant case; high-attachment refinement filed |
| 7 | **agent binding: PRO -> matrix AGENT (passive guard)** | **PINNED** | Lane 4 / McCourt et al. 2015: subject in actives, IMPLICIT agent in passives; the passive guard reuses the reader's VOICE-AWARE role extraction, never binds the patient |
| 8 | canonicalize (surface -> entity via coref) | **PINNED (reuse)** | reuses the reader's coref/entity model; pronoun-resolution pick is OUR-INVENTION |
| 9 | status field (active/satisfied/failed) | **PINNED** | Lutz & Radvansky 1997 (failed>completed>neutral); the satisfied-match / negation rules are OUR-INVENTION |
| 10 | reinstatement: wants()=most-recent ACTIVE goal | **PINNED** | Suh & Trabasso 1993 (last-unsatisfied-superordinate); recency is a real factor |
| 11 | why()/goals_of() readout | PINNED (order) / OUR-INVENTION (match) | reinstatement order PINNED; the head-match is OUR-INVENTION |
| M1 | doc-cluster bootstrap CI, null p95 | **HYGIENE** | resampling MEAN over docs -- statistical measurement, not a brain averaging step |
| M2 | floors (most-recent-action / physical-cause / adjacency), info-free twin, spaCy oracle | **HYGIENE** | baselines / controls / reference validation -- deliberately trivial, not brain claims |
| M3 | _match_goal (lemma equality), _match_overlap | **HYGIENE** | scoring predicate |

**Averaging audit (the owner's specific ask):** the ONLY averaging inside the MECHANISM is the subcat-frame
frequency ratio (#3), which is brain-faithful (lexical frames ARE frequency-weighted, PINNED). There is NO
FHRR bundling / vector averaging / consolidation-style mean in the goal pipeline (the register SELECTS, it
does not superpose) -- so this dimension does not carry the project's documented "averaging machine" hazard.
Every other mean is the bootstrap over documents (#M1), which is measurement hygiene and correctly not a
brain claim. **Conclusion: every mechanism step is PINNED or OUR-INVENTION-flagged-and-swept; no convenient
substitute for a brain operation remains.** The two labelled residuals to the ideal are the high-attachment
graph (#6, filed as the goal-hierarchy next-problem) and Tier-2 abductive inference (the meaning channel).

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
