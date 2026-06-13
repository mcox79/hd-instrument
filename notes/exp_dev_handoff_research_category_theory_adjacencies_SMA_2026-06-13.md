# exp_dev hand-off -- research: category-theory adjacencies for SHARES_MATH (Cell SMA-2 / SMA-3)

Filed-by: research sub-agent (2026-06-13)
Trigger: notes/research_DRILL_category_theory_adjacencies_for_substrate_symbolic_prover_SHARES_MATH_architecture_2026-06-13.md
Pause state: check data/orchestrator_paused.flag before acting. Also GATED on Cell SMA-1 outcome -- do not ship SMA-2/SMA-3 until SMA-1 returns HARD-PASS verdict on SHARES_MATH-aware L6-PROOF traversal.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor:
1. verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.
2. verify Cell SMA-1 has returned a verdict. If SMA-1 has not run or returned PARTIAL/FAIL, file as STANDING -- do NOT ship SMA-2/SMA-3 until SMA-1 HARD-PASSES. Per research note, axiomatizing a SHARES_MATH that doesn't lift proof depth has no value.

---

## Why this hand-off exists

Substrate has DEPLOYED coalgebraic bisimulation as SHARES_MATH at production scale (332 edges, 12 archetypes, 61 atoms). The natural categorical adjacencies (per research drill 2026-06-13) split into LOAD-BEARING (predicate-lifting axiomatization; Lawvere-quantale enriched non-expansiveness) and SPECULATIVE (categorical type theory; e-graph-as-pushout). Two cheap CPU cells can EMPIRICALLY decide whether the load-bearing adjacencies hold, opening 2 NEW substrate-product capability-gap claims over LLMs.

These cells COMPOSE on top of CELL SMA-1 (which tests whether SHARES_MATH-aware traversal lifts proof depth 1.5-3x in L6-PROOF). If SMA-1 confirms the operational value, SMA-2/SMA-3 axiomatize WHY that value exists and what its categorical structure is.

---

## Anchor Candidates (rank-ordered by cost and load-bearingness)

### A. CELL SMA-2 -- Predicate-lifting axiomatization of SHARES_MATH

Anchor pointer: SMA-2-PREDICATE-LIFTING (new; not yet queued)
Substrate-product reading: Tests whether substrate's 12-archetype SHARES_MATH partition has a NATURAL modal-logic axiomatization in <= 8 predicate-lifting axioms. If yes, substrate has a sound class-transfer mechanism (proof of property P about atom A transfers to atom B if A SHARES_MATH B), opening a NEW capability-gap claim "substrate's class machinery is axiomatized in <= 8 modal axioms; LLMs have 0 axioms for their implicit semantic equivalence".
Tier hint: CPU laptop; ~30-60 min wall time; no GPU; existing SHARES_MATH 332-edge corpus is ground truth
Why-now: Highest-value LOAD-BEARING adjacency. If SMA-1 HARD-PASSES on traversal, SMA-2 explains why. If SMA-2 also HARD-PASSES, substrate gains an audit-robust soundness argument for class-transfer that no LLM can match.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS: predicate-lifting axiomatization recovers 12/12 archetypes (0 cross-archetype false merges) AND axiom-count <= 8
    -> SHARES_MATH has natural modal axiomatization; load-bearing for class transfer
  HARD-FAIL: <= 9/12 archetypes recoverable OR axiom-count >= 14
    -> SHARES_MATH has no natural axiomatization; predicate-lifting is post-hoc not load-bearing
  MID-BAND: 10-11 archetypes + axiom-count 9-13
    -> Filed as candidate-but-not-load-bearing; do not extend

Setup: existing 61-atom 332-edge SHARES_MATH relation as ground truth; define candidate predicate liftings over the SHARES_MATH coalgebra functor F; check Hennessy-Milner duality on the partition; minimize axiom count via standard modal-logic compression.

### B. CELL SMA-3 -- Lawvere-quantale enriched non-expansiveness test

Anchor pointer: SMA-3-LAWVERE-NONEXPANSIVE (new; not yet queued)
Substrate-product reading: Tests whether substrate's 7 capability-class operators are NON-EXPANSIVE in a [0,1]-enriched (Lawvere quantale) SHARES_MATH distance. If yes, substrate is a generalized metric space in the Lawvere sense -- a STRUCTURAL property no LLM has been shown to satisfy.
Tier hint: CPU laptop; ~1 hr wall time; no GPU; existing 61-atom corpus
Why-now: Second-highest LOAD-BEARING adjacency. Compounds with SMA-2 -- if both pass, substrate gains 2 NEW capability-gap claims simultaneously. Closest published analog is Wild & Schroeder Kantorovich-functor framework (2022); substrate would be among the first deployed cognitive-substrate instance.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS: >= 6/7 substrate capability-class operators non-expansive over d AND max-stretch <= 1.0
    -> substrate IS a Lawvere-quantale-enriched category in a natural sense
  HARD-FAIL: <= 4/7 operators non-expansive OR max-stretch > 1.5
    -> substrate is NOT enriched in any natural sense; INV-3 continuous extension stays heuristic
  MID-BAND: 5/7 operators non-expansive AND max-stretch in [1.0, 1.5]
    -> Partial enrichment; document operators that fail and investigate

Setup: define d: A x B -> [0,1] s.t. d(A,B) = 0 iff same archetype, d(A,B) = 1 iff unrelated, interpolate in (0,1) for SHARES_MATH-cluster-radius<=k; check 7 substrate operators (fhrr_bind, partition_routing, codebook_cleanup, dijkstra, astar, name_vec_compose, l6_proof_chain) for non-expansiveness.

### C. (DEFER) CELL SMA-4 -- e-graph DPO rewriting for SHARES_MATH normalization

Anchor pointer: SMA-4-EGRAPH-DPO (NOT YET FILE)
Substrate-product reading: SPECULATIVE per research note; pre-test required first (measure star vs dense-clique pattern in 332 edges). Only file if pre-test shows >= 50pct dense-clique pattern (room for normalization). Otherwise the 332 edges are at-or-near saturated canonical form already.
Tier hint: DEFER -- file pre-test only (~20 min CPU)
Why-now: NOT NOW. Pre-test gates the actual cell.

### D. (DEFER) CELL SMA-5 -- Fibrational categorical type theory for CHTV-1

Anchor pointer: SMA-5-FIBRATIONAL-TYPE-THEORY (NOT YET FILE)
Substrate-product reading: SPECULATIVE per research note; GATED on Pi/Sigma corpus authoring (~50-80 atoms) which is itself gated on BATCH 18+ authoring decisions.
Tier hint: DEFER until Pi/Sigma corpus exists
Why-now: NOT NOW. Pre-condition not met.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_DRILL_category_theory_adjacencies_for_substrate_symbolic_prover_SHARES_MATH_architecture_2026-06-13.md (this drill)
- Memory: substrate_CHTV1_substrate_as_verifier_HARD_PASS_1p0_precision_LLM_categorical_gap_checkable_ground_truth_2026-06-12.md
- Memory: substrate_L6_PROOF_FINDER_HARD_PASS_20_20_SOUND_axiom_terminating_38pct_genuine_T1_62pct_authoring_gap_USER_goal_deduction_closed_2026-06-13.md
- Memory: substrate_CELL_KP_knowledge_promotion_operator_P1_P4_HARD_PASS_2_of_5_paths_multi_mechanism_validated_2026-06-13.md
- Memory: substrate_mathematical_primitive_shares_math_architectural_insight_2026-06-12.md
- Memory: substrate_CH_P6_LLM_soundness_gap_capstone_HARD_PASS_substrate_0_false_accepts_vs_Qwen_3_of_12_hallucinated_PROVER_NARRATIVE_COMPLETE_2026-06-13.md

---

## Contract section

- Cells SMA-2 and SMA-3 ship ONLY IF Cell SMA-1 HARD-PASSES first. Do NOT ship if SMA-1 returns PARTIAL/FAIL.
- Cell SMA-4 (e-graph) requires PRE-TEST first (star vs dense-clique pattern measurement).
- Cell SMA-5 (fibrational type theory) is DEFERRED until Pi/Sigma corpus exists (>=50 atoms).
- All cells are CPU-only laptop smoke (no GPU needed); avoid blocking GPU queue.
- Pre-reg bands above are RESEARCH RECOMMENDATIONS; exp_dev validates and may refine.

## Autonomy declaration

exp_dev has full autonomy to:
- refine the pre-reg bands per smoke-data calibration
- choose substrate-existing 7-operator list (the 7 named are research recommendations; exp_dev may substitute equivalent capability-class operators)
- decide queue priority and ordering of SMA-2 vs SMA-3 (research recommends SMA-2 first for cost reasons but order is exp_dev's call)
- file SMA-4 pre-test independently if SMA-1 has not yet returned
- decline to ship if substrate state has materially changed since this hand-off was filed
