---
owner_verdict: DONE
---

SOLVED (pending your verdict) — build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension (opus 4.8 solver)

Write-up: notes/problems/build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension/
  {SOLVED.md, research_goal_hierarchy_plot_structure_mechanism_2026-09-04.md,
   research_prior_multihop_supercharge_implications_2026-09-04.md}
Reverify (re-runs NO landed cell): .venv/Scripts/python.exe verification/test_goal_hierarchy_graph.py   # 8/8

WHAT SHIPS: a glass-box GOAL->SUBGOAL HIERARCHY GRAPH composing the landed flat goal register
(hdlab.goal_register) with the reader's causal network — subgoal-action -> superordinate-purpose MOTIVATION
edges chained across sentences on the shared head lemma, CONNECTIVITY salience (Trabasso & van den Broek
1985, not depth/recency), open-superordinate reinstatement (Suh & Trabasso 1993). Glass-box, NO LLM, zero
tuned params. Brain mechanism validated by a 7-question research drill (all choices PINNED).

RESULT (30-item authored plot-structure battery; hand-set gold, flat register + shuffled-edges twin carry
the epistemic weight; structural graph reconstruction 1.000): THREE QA arms, each CI-separated over the
ACTUAL landed flat-register floor with the info-free twin LOSING —
- goal-why CHAIN / superordinate (n=88): graph 1.000 vs flat.why (immediate purpose only) 0.682,
  +0.318 CI[0.227,0.421]; twin p95 0.296.
- SUPERORDINATE reinstatement over distance (n=15): 1.000 vs flat.wants (recency) 0.067, +0.933 CI[0.80,1.0];
  twin p95 0.467. DISTANCE-invariant (graph 1.0 for K=0..5 distractors; recency floor collapses to 0 at K=1).
- CONNECTIVITY salience (n=15): 1.000 vs recency 0.000; twin p95 0.333.

CONSUMER IMPACT (owner ask; live SituationReader on 12 LitBank docs): the graph is a pure ADD (sets
sm.goal_graph + NEW callables, never touches sm.wants/why/achieved) -> existing board answers BYTE-IDENTICAL
169/169, 0 regression on ALL dimensions. Instrument gap: only 6/149 (4%) of the live board's goal-why
questions are multi-hop, and the board gold is depth-1, so the benefit is invisible until a plot-structure
QA arm is added (same shape as the parser problem's agent-only events QA). Scored benefit is the battery above.

MULTI-HOP PRIOR-WORK RECONCILIATION (owner: "we can DEFINITELY do multihop / found ways to supercharge it"):
multi-hop reasoning IS proven here — on CLEAN symbolic substrates (certified hdlab/multi_hop.py K=2; 50 hops
when relations don't repeat), supercharged by candidate-set restriction (community-routing, gated re-query
+0.383, meet-in-the-middle); precision ceiling = cone-collapse, closed by restriction not scaling. No prior
multi-hop runs over the reader's own extraction — the limiter is EXTRACTION/COVERAGE, not the reasoning. The
goal graph's structural walk sits in the proven-clean regime (no per-hop decay); the real lever is EDGE
COVERAGE, not deeper search (confirmed: causal enablement edges rescue isolated goals 0.080->0.066).

LOCATED NEGATIVE — CRACKED + OPTIMIZED (my first "out of scope" was over-stated): the marker-less
action->goal link is a graded MEANS-END lookup over ATOMIC (xIntent/xWant in the CSKG), the SAME mechanism as
the landed 0.700 discourse-fact bridge. Three ascending-fidelity versions measured vs recency 0.0 + shuffled-
index twin p95 0.25: binary 0.375 -> frequency counts 0.688 -> PPMI+SVD 0.938 (+0.25, the optimization). The
SVD also GENERALIZES to unseen verb pairs (held-out AUC 0.68) and a reliability GATE abstains on 4/5 no-signal
items (no-harm). PoC (n=16 authored); the honest bound is ATOMIC verb coverage (softened by SVD generalization).

files: experiments/{goal_hierarchy_graph, exp_goal_hierarchy_qa_v1, exp_goal_hierarchy_consumer_impact_v1,
exp_goal_hierarchy_markerless_bridge_v1}.py + verification/test_goal_hierarchy_graph.py (8/8) +
data/{exp_goal_hierarchy_qa_v1,_consumer_impact_v1,_markerless_bridge_v1}/metrics.json. NO hdlab written
(Q111 — additive default-on diff in SOLVED §5). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT §2b (goal-hierarchy
graph, PINNED connectivity salience + motivation edges + reinstatement). Ledger malformed/incomplete: 0.

NEXT STEPS (optimization roadmap; §0 done this session): 1) land the additive Q111 wire + a goal_hierarchy
board arm (else the benefit is invisible). 2) THE biggest remaining win — validate the PPMI+SVD means-end
bridge on REAL narrative with a coverage curve, wired as a reliability-GATED edge type (reuse
exp_discfact_store_bridging_graded + hdlab/graded_competition + hdlab/reasoner.py); problem-sized. 3) fidelity:
connectivity+chain-membership salience, faithful two-hop enablement, backoff edge types for verbs ATOMIC
misses. 4) register-native parser for real-narrative chain density.

KEY REALIZATIONS: (a) the flat register COLLAPSES the hierarchy (every "to G" stored as "goal=G"), so its
clean blind spots are multi-hop why + reinstatement-with-a-distractor — tracing that by hand located the
can-fail discriminators. (b) an info-free twin must randomize WHICH node is the root (rewire edges to random
nodes), not just permute endpoints, and the tiebreak must be gold-neutral — else the control proves nothing.
(c) the owner's "definitely do multihop" is right: multi-hop is proven on clean substrates and the located
negative was over-stated — copying the proven PPMI+SVD bridge lifted the marker-less link 0.69->0.94 and made
it generalize. The lesson across the whole lineage: the reasoning step works; extraction/coverage is the limiter.
