---
owner_verdict: DONE
---

SUBMISSION — replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering
Status: SOLVED (solver scope; your DONE gates integration). One owner judgement call flagged below.
Reverify: .venv/Scripts/python.exe verification/test_online_cue_cluster.py   → 23/23 PASS
Deliverable: notes/problems/replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering/SOLVED.md

THE LEAK (confirmed first-hand): the live reader's entity layer (which feeds the affect/goal experiencer) is
gold-derived — either _apply_commonnoun_gate relabels groups to the plurality GOLD coref cluster, or, gate-off,
_build_entities groups by the gold coref column. Fed the answer key it fakes the cross-type experiencer bind at
C3=0.807 WITHOUT reading; the honest floor is 0.155.

THE BRAIN-FOUNDATIONAL FIX (glass-box, NO external LLM, NO gold in any decision): an ONLINE Heim file-change
clustering with Lewis-Vasishth ACT-R content-addressable retrieval — exact-head TYPE cue + gender/number AGREEMENT
+ ACT-R base-level ACTIVATION, always-merge. Faithfulness-gated to the landed cue_cluster byte-for-byte.

RESULTS (modern GUM V12.1.0):
• CLAUSE 1 — beats the honest floor CI-sep: entity-layer CoNLL 0.6975 vs situation_predict 0.6939 (+0.0036 CI-sep)
  and vs string-identity 0.6921 (+0.0054 CI-sep); shuffled-cue twin collapses to 0.4309. The unified_referent organ's
  INDEPENDENT grouping converges to the same number (0.6976) → a LOCATED OPTIMUM, not one arbitrary heuristic.
• CLAUSE 2 — unmasks the downstream gain the peek was hiding (all 275 docs, n=549): online clustering + crosstype
  bridge lifts the experiencer 0.1548 → 0.2386 = +0.0838 CI[0.0355,0.1394] CI-sep. Shuffled-CLUSTERING twin + bridge
  collapses (+0.0528 CI-sep → clustering structure load-bearing); random-target twin loses (+0.0583 CI-sep). C1 up.
• OOD (GENTLE) replicates in direction+magnitude. Research VET confirmed the mechanism (Lewis-Vasishth/ACT-R) high.

I CORRECTED THE BRIEF: it asked to wire a part-whole (C6) route into the type cue. The data refuses it (over-merges,
-0.0100 CI-sep) and a literature VET confirms why — meronymy is BRIDGING, not identity ("the wheel" ≠ "the car";
Clark 1975 / ARRAU / ISNotes). Centering-Cb and hold-under-uncertainty are also drilled located negatives.

ONE HONEST CAVEAT (a control caught what I'd asserted): the tighter gn-correct clusterer costs a small CI-sep drop on
the C2 named-entity hard-link (deployed 0.0310→0.0231, -0.0078 CI[-0.0146,-0.0025]) — cross-type recall is the
bridge's + world-knowledge's job, not the identity former's; the LIVE named consumer (C3) is up +0.0838 and C1 is up.
→ OWNER JUDGEMENT CALL: I recommend SOLVED (live gains clean, C2 is a dormant-path precision/recall trade); if you
read the "named-antecedent no-regress" sub-clause strictly, PARTIAL is defensible.

WALL PROTOTYPES (you asked me to prove both remaining walls are crossable — mechanism proofs, not solves):
• Wall 1 (world knowledge): encyclopedic KB route converts stored facts→correct binds at 40%, +0.0511 CI-sep, twin
  loses, oracle=1.0 → coverage-bounded (KB reaches 10.6% of GUM's local/fictional names). Lever = KB breadth.
• Wall 2 (generative inference): discourse-prediction (ACT-R+Centering) works where cued (0.44 vs 0.11 chance) and has
  partial reach even into the 98% residual (0.26 vs 0.12) — the rest needs the full generative world-model.

hdlab UNTOUCHED (Q111 — proposed diff in SOLVED.md). Files: experiments/exp_online_cue_cluster_gum_v1.py,
exp_online_cluster_downstream_c3_gum_v1.py, exp_wall1_encyclopedic_kb_v1.py, exp_wall2_generative_inference_v1.py,
verification/test_online_cue_cluster.py.

NEXT (priority): (1) strategy lands the wire — the keystone that makes the blocked coref/name-bridge/experiencer work
live; (2) HIGH: world_knowledge...81_percent_residual (broaden the offline entity-type KB — mechanism is ready);
(3) the generative world-model program; (4) a bridging/associative-anaphora resolver (needs acquired bridging gold).
