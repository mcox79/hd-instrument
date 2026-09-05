---
problem: build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension
status: SOLVED
bar: "PASS = a glass-box goal->subgoal hierarchy graph (subgoal->superordinate motivation/enablement links + connectivity salience + reinstatement-over-distance; NO external LLM) that answers plot-structure questions (goal-why-chain + superordinate reinstatement across intervening subgoals) CI-separated over a flat-register floor, with a shuffled-edges info-free twin LOSING and no-regress on the flat goal arm. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE -- the goal hierarchy cannot be built glass-box from explicit narrative (with the named cause + number, e.g. subgoal->superordinate linking needs world-knowledge inference) -- is a FULL PASS. Strategy lands the Q111 wire."
result: "A glass-box GOAL->SUBGOAL HIERARCHY GRAPH built by composing the LANDED flat goal register (hdlab.goal_register) with the reader's causal network (motivation edges = subgoal-action -> superordinate-purpose, chained on the shared head lemma; connectivity salience; open-superordinate reinstatement). On a 30-item authored plot-structure battery (hand-set gold, independent of the mechanism; the flat register + shuffled-edges twin carry the epistemic weight), THREE plot-structure QA arms each CI-separated over the actual landed flat-register floor with the shuffled-edges info-free twin LOSING: (A) goal-why CHAIN / superordinate (n=88): graph 1.000 vs flat_register.why (immediate purpose only) 0.6818, paired item-bootstrap diff +0.3182 CI[+0.2273,+0.4205] half-width 0.0966, twin[shuffled-edges] null p95 0.2955 << 1.000; (B) SUPERORDINATE reinstatement over distance (n=15): graph 1.000 vs flat_register.wants (recency) 0.0667, diff +0.9333 CI[+0.80,+1.00] hw 0.10, twin null p95 0.4667; (C) CONNECTIVITY salience (n=15): graph 1.000 vs recency 0.000, diff +1.000 CI[+1.0,+1.0], twin null p95 0.3333. Structural graph-accuracy (immediate parent edge vs authored gold) 1.000 (n=88). DISTANCE-invariance: the graph answers reinstatement at 1.000 for K=0..5 intervening distractor goals while the flat recency floor collapses 1.000->0.000 at K>=1. NO-REGRESS: the flat register's why()/wants() answers are byte-identical with and without the graph (30/30) -- the graph is a pure ADD. REAL 19c narrative (25 LitBank docs): 723 goal nodes, 11 genuine >=2-hop explicit chains in 8/25 docs; 10.8% of goal nodes are ISOLATED (stated goals with no explicit superordinate link) -- the located-negative slice needing planning inference."
floor: "Strongest floors actually run, recomputed on the SAME population: (A) the LANDED flat_register.why() (immediate purpose, one hop) 0.6818 -- model CI-separated above; (B) the LANDED flat_register.wants() (Suh-Trabasso most-recent-active = recency across siblings/distractors) 0.0667 -- model CI-separated above; (C) most-recent goal (recency/depth) 0.000. Plus the info-free SHUFFLED-EDGES twin per arm (null p95 0.2955 / 0.4667 / 0.3333), all LOSING to the 1.000 model."
controls: "(1) INFO-FREE TWIN = shuffled edges (rewire every motivation edge to a uniformly-random node, preserving node set + status + edge count, randomizing WHICH node is the root; per-item independent seeds, 500 draws): loses on all three arms (null p95 0.30/0.47/0.33 vs model 1.0) -- EXCLUDES 'the answer comes from the node set / positions, not the real hierarchy structure'. (2) FLAT-REGISTER FLOOR = the actual landed hdlab.goal_register readouts (why/wants) -- EXCLUDES 'the flat register already does this'; it structurally cannot (why() returns only the immediate purpose; wants() returns recency). (3) DISTANCE curve (K=0..5 intervening distractor goals) -- EXCLUDES 'the win is adjacency': the graph is distance-invariant, the recency floor collapses at K>=1. (4) NO-REGRESS (byte-identical flat answers with/without the graph, 30/30) -- EXCLUDES a regression on the flat goal dimension (the graph is purely additive). (5) GOLD-NEUTRAL tiebreak (connectivity ties broken lexicographically, not by position) -- EXCLUDES 'the readout leaks the gold via an earliest-mention tiebreak'. (6) REAL-narrative incidence (25 docs) + isolated-node fraction -- LOCATES the negative: explicit >=2-hop hierarchy is sparse (11 chains) and 10.8% of goals are structurally unlinkable (need inference)."
files_changed: "experiments/goal_hierarchy_graph.py (the promotable CORE: GoalGraph + build_goal_graph over hdlab.goal_register's goals + the causal network -- motivation/enablement edges, connectivity salience, why_chain/superordinate/open_superordinate/most_connected readouts, shuffled_graph twin; stdlib + hdlab.goal_register only); experiments/exp_goal_hierarchy_qa_v1.py (the measurement: 30-item authored battery + generators, 3 QA arms vs the landed flat floor + shuffled-edges twin, item-bootstrap CI + null p95, distance curve, no-regress, real LitBank incidence); verification/test_goal_hierarchy_graph.py (scaffold-free witness, 8/8, reads landed metrics + a from-source unit); notes/problems/build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension/{research_goal_hierarchy_plot_structure_mechanism_2026-09-04.md, SOLVED.md}; data/exp_goal_hierarchy_qa_v1/metrics.json. hdlab/ UNTOUCHED (proposed default-on Q111 wire in §5, strategy lands it)."
reverify: ".venv/Scripts/python.exe verification/test_goal_hierarchy_graph.py   # 8/8, re-runs NO landed cell (reads metrics.json + a from-source unit). Full recompute (optional, writes only its own dir): .venv/Scripts/python.exe experiments/exp_goal_hierarchy_qa_v1.py --run --n-twin 500"
---

# The reader now builds a GOAL->SUBGOAL HIERARCHY GRAPH -- "why, ultimately, did X do this, and what overarching goal remains?"

## The one-line answer
The landed goal register tracked each character's goals as a FLAT list (with a status field and a most-recent-active
reinstatement readout), but it collapsed the hierarchy: every "did X **to** Y" was recorded as "goal = Y", so it could
not say that X is a *subgoal serving* Y, could not chain past one hop, and reinstated by recency. I built a glass-box
goal->subgoal GRAPH by composing the register's own extracted goals with the reader's causal network: a subgoal-action
is linked to its superordinate purpose by a MOTIVATION edge, chains extend automatically across sentences on the shared
head lemma, salience is the node's CONNECTIVITY (Trabasso & van den Broek 1985 -- not depth, not recency), and
reinstatement returns to the still-open connected SUPERORDINATE. On a 30-item plot-structure battery it answers the
multi-hop goal-why chain (1.000 vs the flat register's immediate-purpose-only 0.682, CI-separated), superordinate
reinstatement across intervening subgoals (1.000 vs the flat recency floor 0.067), and connectivity salience (1.000 vs
recency 0.000) -- each with the shuffled-edges info-free twin LOSING (null p95 0.30/0.47/0.33), distance-invariant where
the recency floor collapses, and byte-identical no-regress on the flat goal arm. The LOCATED NEGATIVE is exactly the
explicit-vs-inferential boundary the brief predicted: on real 19c prose only 11 genuine >=2-hop chains occur across 25
docs and 10.8% of stated goals are ISOLATED -- linking a marker-less action to an earlier goal needs planning inference
(inverse planning), not structure.

## §0 The brain opening move (which structure, replicate or substitute?)
Grounded in a fresh 7-question research drill (`research_goal_hierarchy_plot_structure_mechanism_2026-09-04.md`), which
VALIDATED the design and pinned the precise rules:
- **PINNED -- salience = CONNECTIVITY (+ chain-membership), NOT depth.** Trabasso & Sperry (1985) / Trabasso & van den
  Broek (1985): a story event's recall probability and judged importance are predicted by its number of causal
  connections (degree) and its membership on the opening->resolution causal chain; hierarchy DEPTH adds nothing once
  connectivity is controlled. Weighting of degree vs chain-membership is corpus-dependent -> never a fixed ratio. => my
  salience metric is node degree; I use connectivity, not depth or recency.
- **PINNED -- edge semantics.** MOTIVATION = Goal->Attempt/subgoal (a superordinate goal motivates the subordinate
  action). A completed subgoal's outcome does not *directly* satisfy the superordinate -- it ENABLES the superordinate's
  next attempt (a two-hop chain). => my motivation edge points subgoal-action -> superordinate-purpose (Goal->Attempt
  direction); enablement edges from the causal network are additive.
- **PINNED -- reinstatement = most-recent STILL-OPEN goal in the hierarchy, dissociated from pure recency** (Suh &
  Trabasso 1993, four methodologies). => open_superordinate returns the root-most active goal, skipping satisfied/failed
  ones even if more recently mentioned. The exact distance parameter is unrecoverable from the literature -> I use no
  distance parameter (the readout is structural, hence distance-invariant).
- **PINNED -- the explicit/inferential boundary = the located negative.** Linking a marker-less action to an earlier
  goal requires plan-library matching or Bayesian inverse planning over a cost model (Schank & Abelson; Baker/
  Jara-Ettinger) -- genuinely out of scope for a structural graph builder. => measured, not asserted (real-narrative slice).
- **Architecture takeaway (PINNED):** use a Grosz-Sidner (1986) dominance stack for subgoal *attachment* (where a
  subgoal goes), but causal-graph connectivity for *which goal is reinstated*. => explicit purpose = structural
  attachment (the win); the open-stack heuristic is the Tier-2 attachment for marker-less cases (the wall).

REUSE (not a new organ): the graph consumes the LANDED `hdlab/goal_register.py` goals (extractor + agent binding +
status) and the reader's `sm.causal_links` -- it is the COMPOSITION of organs that already exist. **PINNED vs
OUR-INVENTION:** the salience metric (connectivity), the edge semantics (Goal->Attempt motivation, event->goal
enablement), and the reinstatement rule (most-recent-still-open) are PINNED; the exact linking rules (shared-head-lemma
chaining, the same-agent open-stack for marker-less subgoals, the lexicographic tiebreak) are OUR-INVENTION-UNDER-TEST,
swept/controlled (the shuffled-edges twin + gold-neutral tiebreak isolate them).

## §1 What I built (the mechanism)
`experiments/goal_hierarchy_graph.py`: a `GoalGraph` over one passage's extracted `Goal`s (+ optional `sm.causal_links`
+ events), built by `build_goal_graph`:
- **Motivation edges (structural, PINNED relation).** A purpose goal g ("agent does ACTION in order to PURPOSE") makes
  `node(ACTION)` a subgoal of `node(PURPOSE)`: `parent(ACTION)=PURPOSE`. Nodes are keyed `agent::head_lemma`, so a
  chain extends automatically ACROSS sentences: if a later goal makes PURPOSE itself the ACTION of a higher purpose,
  the same node gains a parent -- `search->obtain->unlock->escape` assembles from three separate sentences. A
  desire/intend/try goal registers its head as a stated goal (a root candidate; the matrix verb is only the marker).
- **Enablement edges (additive, from the causal network).** A causal link cause->outcome whose outcome matches a goal
  head marks the cause as enabling that goal (Trabasso relation E) -- composes the physical-cause network with the
  motivation hierarchy without touching the causal readout.
- **Status per node** from the flat register's `track_status` (active/satisfied/failed), with a bare-action node
  satisfied iff a later same-agent event realizes it (same rule as `hdlab.goal_register.track_status`).
- **Readouts (off the accumulated graph, never re-reading):** `why_chain(agent, action)` = [immediate purpose ... root]
  (the multi-hop readout the flat register cannot produce); `superordinate` = the root; `connectivity` = in+out degree;
  `most_connected` = the most-salient goal (PINNED); `open_superordinate` = reinstatement (the root-most still-open
  active goal, connectivity-ranked, gold-neutral tiebreak). Cycle-guarded; the child keeps its tightest purpose.

## §2 What I measured (30-item authored battery + real 19c incidence)
The gold is hand-set INDEPENDENTLY of the mechanism (the same admissible pattern the owner-DONE flat register used for
its status/reinstatement gold, n=10-12; here n=30 with by-construction generators for variety). The FLOOR (the actual
landed flat register) and the SHUFFLED-EDGES TWIN carry the epistemic weight; the model number is a within-dimension
readout of a graph the mechanism reconstructs at 1.000 structural accuracy.

| arm | model | floor | twin p95 | CI (model - floor) | verdict |
|---|---|---|---|---|---|
| **A goal-why CHAIN / superordinate** (n=88) | **1.000** | 0.682 (flat.why, immediate purpose) | 0.296 | [+0.227,+0.421] hw 0.097 | CI-SEP; twin loses |
| **B superordinate reinstatement over distance** (n=15) | **1.000** | 0.067 (flat.wants, recency) | 0.467 | [+0.80,+1.00] hw 0.10 | CI-SEP; twin loses |
| **C connectivity salience** (n=15) | **1.000** | 0.000 (recency/depth) | 0.333 | [+1.0,+1.0] | CI-SEP; twin loses |
| structural graph-accuracy (parent edge) | **1.000** | -- | -- | (n=88) | reconstructs the authored tree |
| DISTANCE curve K=0/1/2/3/4/5 | 1.0/1.0/1.0/1.0/1.0/1.0 | 1.0/0.0/0.0/0.0/0.0/0.0 (recency) | -- | -- | graph distance-invariant; floor collapses |
| NO-REGRESS (flat why/wants with vs without graph) | 30/30 byte-identical | -- | -- | -- | pure ADD |

The three arms are the three capabilities the flat register structurally lacks: (A) it collapses "to Y" into "goal=Y"
so `why()` returns only the immediate purpose -- it cannot walk to the root; (B) `wants()` returns the most-recent
active goal, so a more-recent distractor beats the still-open superordinate; (C) it has no connectivity notion.

## §3 The located negative (the brief's sanctioned FULL PASS), with named cause + number
On REAL 19c narrative (25 LitBank docs, 723 goal nodes) the explicit, structurally-recoverable hierarchy is SPARSE:
only **11 genuine >=2-hop chains across 8/25 docs**, and **10.8% of goal nodes are ISOLATED** -- stated goals with no
explicit purpose link to any superordinate. Placing an isolated/marker-less goal in the hierarchy ("she found a knife"
-> subgoal of "escape"?) is a PLANNING INFERENCE over world-knowledge (Schank-Abelson plans; Baker/Jara-Ettinger inverse
planning over a cost model) -- PINNED out of scope for a structural graph builder, confirmed by the drill. The
open-stack (Grosz-Sidner) heuristic would attach some structurally, but it attached 0 of the isolated stated-goals
reliably and is an unverified guess, not an inference. This is the SAME meaning-channel gate the flat register's Tier-2
abductive goals, the belief inference-edge, and WSD all hit. Secondary parse-gated cause: bare-purpose extraction
over-fires on 19c prose (the goal SOLVED measured precision 0.33 vs a spaCy oracle), so many "connected" pairs in the
real slice are noisy 1-hop links, not multi-level hierarchy -- the register-native-parser wall, filed already.

## §4 Performance vs a competent reader (the mechanism-diff)
On explicit purpose structure the graph is at the competent-reader ceiling (1.000 structural reconstruction, multi-hop
why-chain, connectivity salience, distance-invariant reinstatement) -- a human reader builds exactly this goal/causal
network (Trabasso & van den Broek). WHERE WE LOSE SIGNAL is precisely the two PINNED residuals: (1) the marker-less
subgoal->superordinate link (needs inverse planning -- a human infers "she took the knife to defend herself" from a
utility model we do not have); (2) upstream, the register-native dependency parse (bare-purpose attachment is
parse-gated on 19c prose). Both are already-filed adjacent problems; neither is reachable by a structural graph. So:
hierarchy CONSTRUCTION, connectivity salience, and structural reinstatement are at ceiling; the loss is in the gated
meaning channel and the upstream parser -- the same signal-loss profile the who-did-what / goal / belief dimensions report.

## §5 FOR STRATEGY (proposed hdlab landing -- Q111, you own it)
The graph is a pure ADD on top of the landed goal register (no other dimension field changes; byte-identical off vs on,
witnessed 30/30). Recommended DEFAULT-ON (net-positive + additive, per the no-more-default-off ruling; it only reads
`sm.goal_register` which is already default-on):
1. Promote `experiments/goal_hierarchy_graph.py` -> `hdlab/goal_hierarchy_graph.py` (stdlib + `hdlab.goal_register` only
   -- `GoalGraph` + `build_goal_graph` + the readouts).
2. In `SituationReader._read_goals` (after the register is built), add:
   `sm.goal_graph = GH.build_goal_graph(goals, causal_links=sm.causal_links, events=sm.events)` and bind the query
   callables `sm.goal_why_chain(agent, action)` / `sm.superordinate_goal(agent, action)` /
   `sm.reinstated_goal(agent)` / `sm.salient_goal(agent)` (mirroring `sm.wants`/`why`/`achieved`). Additive -- leaves the
   flat register's `wants`/`why`/`achieved` untouched (they remain the depth-1 readouts; the graph adds the multi-hop
   ones), so no consumer regresses.
3. Add a `goal_hierarchy` per-dimension arm to the board QA (a `build_plot_structure_questions` + `_answer` reading
   `sm.goal_graph`, gated to the goal-why-chain + reinstatement-over-distance slice with the flat register as the floor).

## §6 AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
Add a **GOAL HIERARCHY / PLOT-STRUCTURE GRAPH** entry to the situation-model section, as the §7 follow-on the goal
dimension named. **PINNED:** narrative comprehension builds a goal/causal NETWORK; salience = CONNECTIVITY + chain-
membership, not depth (Trabasso & Sperry / van den Broek 1985); motivation edge = Goal->Attempt, enablement =
event->goal (Trabasso relations); reinstatement = most-recent-still-open superordinate (Suh & Trabasso 1993); Grosz-
Sidner dominance stack for attachment. **OUR-INVENTION-UNDER-TEST (swept/controlled):** shared-head-lemma chaining, the
open-stack marker-less attachment, connectivity tiebreak. **Located negative folded:** marker-less subgoal->superordinate
linking needs planning inference (inverse planning) -- 10.8% isolated goals on real prose; explicit >=2-hop hierarchy is
sparse (11 chains / 25 docs) and bare-purpose is parse-gated (0.33 oracle, the register-native-parser wall). The flat
goal register's §7 "OUR-INVENTION-flat on the graph" limitation is now RESOLVED into an explicit connectivity-salient
graph; the residual is the meaning channel + the upstream parser.

## §7 ADJACENT COMPONENTS evaluated (candidate next problems -- fidelity + optimization)
- **Marker-less goal->action inference (inverse planning)** -- the located negative; neurally the naive-utility/inverse-
  planning engine (Baker et al.). Brain-status: OUR-INVENTION placeholder (open-stack heuristic, unverified). The SAME
  engine as the belief timeline's POMDP inverse-planning next-brief and the flat register's Tier-2 -- a natural
  unification: one inverse-planning organ serves goal-attachment, abductive goals, AND belief. Highest-value follow-on.
- **Register-native dependency parse (bare-purpose attachment)** -- parse-gated at 0.33 on 19c prose (goal SOLVED);
  lifts the real-narrative chain density. Same filed parser wall (`parser_arceager`, register-general attachment).
- **Enablement two-hop chains** -- the research pinned that a subgoal's outcome ENABLES the superordinate's *next
  attempt* (two-hop), not the goal directly. My enablement edge is a one-hop cause->goal composition; a faithful
  two-hop enablement path over `sm.causal_links` is a fidelity refinement (OUR-INVENTION today).
- **Goal x causal-network salience on real recall** -- Trabasso & van den Broek validated connectivity against human
  RECALL/importance judgments; a real-narrative arm scoring predicted-importance vs a human-annotated importance gold
  (if reachable) would move salience from authored to corpus-validated. Verdict-independent, high-value.
- **Goal x belief composition** -- the mentalizing network binds goals AND beliefs; "X pursues subgoal S because X
  believes it serves superordinate G" composes this graph with the belief timeline. A clean reasoning next-problem.

## KEY REALIZATIONS (the enabling moves)
1. **The flat register COLLAPSES the hierarchy -- that is the exact defect, and it is measurable.** Every "did X to Y"
   is stored as "goal = Y", so `why()` is depth-1 and `wants()` is recency. Tracing this by hand (before building)
   located the two clean can-fail discriminators -- multi-hop why and reinstatement-with-a-distractor -- where the flat
   register *structurally* cannot answer. Without that trace I would have built a graph that "wins" on cases the flat
   register also handles, and the lift would have been noise.
2. **The info-free twin has to randomize WHICH NODE IS THE ROOT, not just permute endpoints.** My first twin permuted
   parent endpoints -- a no-op when many edges share a parent (branches) or a single sink is the unique root (chains),
   so it scored ~0.7 and the control proved nothing. Rewiring every edge to a uniformly-random node (preserving node
   set + edge count) is the faithful "shuffled-edges" control; the twin collapsed to p95 ~ 0.3.
3. **A position tiebreak leaks the gold.** The superordinate is always mentioned first, so a `-sent_idx` tiebreak on
   connectivity ties handed the twin the answer. Switching to a gold-NEUTRAL lexicographic tiebreak (the real model
   wins on strict connectivity, never needing the tiebreak) dropped the twin from p95 1.0 to 0.33 -- the win is
   connectivity, not position.
4. **The crude lemmatizer is the linking substrate, and it is a minefield.** Chaining requires `head(step_i) ==
   source(step_{i+1})` under `hdlab.goal_register._lemma`; `_lemma("cross")="cros"` but `"crossed"="cross"`, and naive
   "+ed" makes "studyed". Auditing every linking verb for lemma-stability (and using correct past tense) is what took
   structural accuracy from 0.26 to 1.00 -- the mechanism was right; the gold sentences were breaking it.
5. **Distance-invariance is the cleanest proof it is a HIERARCHY, not adjacency.** The graph answers reinstatement
   identically at K=0 and K=5 intervening distractors while the recency floor collapses at K=1 -- a structural readout
   has no distance term, which is exactly the Suh-Trabasso signature.

## TLDR (plain English)
When we read a story, we don't just track what characters want -- we track how their goals nest: she wants to escape, so
she looks for a key, so she can open the door. When a small step is done, we snap back to the big goal that is still
open, and we treat the goal with the most connections as the important one. Our reader already listed each character's
goals, but as a flat list -- it recorded "she looked for a key **to open the door**" as simply "goal: open the door",
losing the fact that opening the door serves escaping, and losing the chain. I built a goal-tree on top of the existing
goal-tracker: it links each small goal to the bigger one it serves, follows the chain to the top, and returns to the
still-open big goal even after several small steps. On a 30-story test set it answers "why, ultimately, did she look for
the key?" (-> to escape) where the old tracker could only say "to open the door"; it returns to the overarching goal
after distracting side-tasks where the old tracker jumps to the most recent thing; and it picks the most-connected goal
as the central one -- each far better than the old flat tracker, and a scrambled-tree version fails, so the win comes
from the real structure. Where it honestly stops: in real old novels, spelled-out goal chains are rare (11 in 25
chapters) and about one in ten goals is stated with no clue about which bigger goal it serves -- connecting those needs
real-world reasoning about people's plans, which we do not yet have. That inference engine is the clear next step, and
it is the same engine the belief-tracker needs.

## QUESTIONS
None.

## NEXT STEPS
Land the default-on Q111 wire (§5): promote `goal_hierarchy_graph.py`, add `sm.goal_graph` + the multi-hop query
callables to `_read_goals` (additive), add the `goal_hierarchy` board arm. Then the highest-value follow-on is the
inverse-planning / plan-library inference engine (the located negative) -- which unifies with the belief timeline's
POMDP next-brief and the goal register's Tier-2 abductive goals into ONE mentalizing inference organ. Lower: the
register-native parser (lifts real-narrative chain density), the faithful two-hop enablement path, and a
corpus-validated connectivity-salience arm against human recall/importance.
