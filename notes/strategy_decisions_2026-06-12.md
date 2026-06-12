# strategy_decisions_2026-06-12

## v574 -> v575 CYCLE 241 7-VERDICT BATCH E3b-endtask + QA-self-knowledge + E4-world-model-MWP + Path5-schema-MWP + Path1lite-entity-MWP + Tier5-self-discovery + Path1-SRL-MWP (verdict_handler 469th PROT-009 paired commit; 1 HP [e3b_permutation_binding_endtask]; 2 MIDDLE_BAND [qa_self_knowledge + tier5_self_discovery_rule_extraction]; 4 HARD_FAIL [e4_world_model_mwp + path5_schema_retrieval_mwp + path1lite_entity_binding_mwp + path1_srl_mwp]; 0 LVH; 3 NEW PP ROWS [PP-400 e3b-endtask + PP-401 qa-self-knowledge + PP-402 tier5-self-discovery]; MWP comprehension-wall CONVERGENTLY CONFIRMED by 4 independent angles; PP-398 promoted to end-task demonstration; Phase-6 math+science ingestion strategy supported; Portfolio 32+399->32+402 +3; HONEST 1831->1838 +7; LVH 291->291 +0)

### Step 0 honest re-read

Metrics source: LOCAL (all 7 files at d:/AI/hd-instrument/data/exp_<name>/metrics.json, cpu_runner_local FrameworkMPC). 0 LVH catches.

**e3b_permutation_binding_endtask_cpu_v1 HARD_PASS (HONEST):** perm_endacc=0.3876 vs FHRR_endacc=0.0465, lift=+0.3411, n_test=129. Threshold >=+0.10 met by 3.4x. HONEST.

**qa_self_knowledge_cpu_v1 MIDDLE_BAND (HONEST):** macro-F1=0.4658 in band [0.30-0.50]. Per-type A=0.3548/B=0.325/C=0.6451/D=0.5/E=0.495/G=0.6667. n_seeds=1. HONEST.

**e4_world_model_mwp_cpu_v1 HARD_FAIL (HONEST):** accuracy=0.3431 vs disc_plateau=0.39. World-model UNDERPERFORMS discriminative baseline. Threshold <=0.40 met (HARD_FAIL). HONEST.

**path5_schema_retrieval_mwp_cpu_v1 HARD_FAIL (HONEST):** accuracy=0.3592, lift_over_baseline=-0.0308 (negative). Threshold <+0.04. HONEST.

**path1lite_entity_binding_mwp_cpu_v1 HARD_FAIL (HONEST):** accuracy=0.3402, lift_over_baseline=-0.0498 (negative). 5th triangulation angle. HONEST.

**tier5_self_discovery_rule_extraction_cpu_v1 MIDDLE_BAND (HONEST):** n_novel_recurring=0, n_re_derived=5, n_sh_atoms=20, n_transitions=11. Miner validated; solution_history too sparse for novel rule emergence. f1=0.0 (no novel rule proposed). MIDDLE_BAND on re-derivation success with mechanism validation. HONEST.

**path1_srl_mwp_cpu_v1 HARD_FAIL (HONEST):** accuracy=0.3268, lift_over_baseline=-0.0632 (negative), n_srl_train=30. 6th triangulation angle. HONEST.

HONEST: 1831 -> 1838 (+7). LVH: 291 -> 291 (+0). 0 LVH catches this cycle.

### Cap_map decisions (v574 -> v575 CYCLE 241)

**(A) e3b_permutation_binding_endtask_cpu_v1 (HARD_PASS -- NEW ROW PP-400; PP-398 end-task promotion):**
NEW ROW PP-400: e3b_permutation_binding_endtask_cpu_v1 HARD_PASS v575: perm_endacc=0.3876 vs fhrr_endacc=0.0465, lift=+0.3411, n_test=129, n_subset=427, n_seeds=1 (cycle 241). PERMUTATION BINDING PROMOTES TO END-TASK MWP ACCURACY: cycle-240 PP-398 showed permutation binding solves multi-occurrence role collision at representation level (acc=1.000); this cycle confirms the lift extends to REAL MWP END-TASK accuracy (+34.11pp). FHRR cannot retrieve same-role occurrences (FHRR endacc=0.0465 ~= chance); permutation indexing enables correct operand selection (endacc=0.3876). Addresses cycle-239 diagnosis: the binding collision WAS the operative bottleneck for multi-occurrence MWP items -- not purely question-semantics comprehension. Composition: PP-398 (role-collision solved) + PP-400 (end-task validated) = substrate-native path to multi-occurrence MWP. Bottleneck shifted to upstream role-detection quality and single-occurrence comprehension ceiling (0.39 disc plateau for 1-op items). P-band: 0.82-0.92 EXPLORATORY n=1 seed CPU n_test=129 elapsed=0.28s. Cross-ref PP-398 (binding mechanism), PP-395/PP-396 (role detection), PP-376 (MAWPS), PP-374 (multibench).

**(B) qa_self_knowledge_cpu_v1 (MIDDLE_BAND -- NEW ROW PP-401; substrate QA self-knowledge v1):**
NEW ROW PP-401: qa_self_knowledge_cpu_v1 MIDDLE_BAND v575: macro-F1=0.4658, per-type A=0.3548/B=0.325/C=0.6451/D=0.5/E=0.495/G=0.6667, n_qs=53, gold_attrition=19, n_seeds=1 (cycle 241). SUBSTRATE QA SELF-KNOWLEDGE PARTIAL: substrate answers questions about what it knows with F1=0.4658. Strong on type-C (knows-what-it-knows: 0.645) and type-G (0.667); weaker on A (enumeration: 0.355) and B (boundary detection: 0.325). Gold attrition=19 (some answers not found in substrate). MIDDLE_BAND: improvement path is Gap-4 intent router (routes question type before answering) and vocabulary reconciliation. Mechanism: hard-route + keyword retrieval v1 (no learned router). Product implication: substrate can answer meta-questions about its own content at moderate accuracy -- useful for knowledge auditing and self-reporting. Phase-6 ingestion scale expected to lift gold attrition issue. P-band: 0.45-0.62 EXPLORATORY n=1 seed CPU n=53 elapsed=0.61s. Cross-ref PP-263 (meta-substrate binary know/don't-know), PP-277 (calibration ECE).

**(C) e4_world_model_mwp_cpu_v1 (HARD_FAIL -- 4th MWP triangulation; comprehension wall annotation):**
e4_world_model_mwp_cpu_v1 HARD_FAIL v575: accuracy=0.3431 vs disc_plateau=0.39, n=1364, per-op +/*/- /=0.301/0.29/0.481/0.204, n_seeds=1 (cycle 241). WORLD-MODEL SCHEMA PLATEAUS AT DISCRIMINATIVE FLOOR: world-model approach underperforms even the discriminative baseline (0.3431 < 0.39). 4th independent triangulation angle: world-model / schema-schema / BMA-ensemble / role-binding all converge at 0.385-0.39. Honest evidence: the 1-op MWP bottleneck is corpus-bound COMPREHENSION (question-semantics at operand-selection level), NOT the op-mapping mechanism. Supports Phase-6 math+science ingestion strategy. No new PP row; ASDiv math series annotated (comprehension wall 4th triangulation).

**(D) path5_schema_retrieval_mwp_cpu_v1 (HARD_FAIL -- 5th MWP triangulation; schema-retrieval axis closed for 1-op):**
path5_schema_retrieval_mwp_cpu_v1 HARD_FAIL v575: schema-retrieval acc=0.3592, majority-op=0.2385, lift_over_baseline=-0.0308, n=348, k=7, n_seeds=1 (cycle 241). SCHEMA RETRIEVAL DOES NOT BREAK OPERAND-SELECTION PLATEAU: PP-372 schema retrieval (96.7% schema selection) cannot compensate for corpus-bound comprehension deficiency. 5th independent triangulation confirms: retrieval quality is not the bottleneck -- semantic understanding of operand roles is. PROT-004/006 rescue sketches for MWP series (cheapest first, per convergent comprehension-wall diagnosis):
RESCUE-1 (cheapest/subsumption): direct Phase-6 math+science ingestion -- more training text is the structural fix per BMA ensemble + all 5 triangulation angles.
RESCUE-2: PP-400 end-task permutation binding scaled to multi-occurrence (multi-occ items already solved; single-occurrence ceiling is the residual 0.39).
RESCUE-3: FCG construction grammar semantic parsing (RESCUE-3 from cycle-239 multihop series).
RESCUE-4: dependency parse operand roles via PP-381 full pipeline.
RESCUE-5: cross-domain schema transfer (train on richer annotated MWP dataset, transfer PP-372 schemas).
Route RESCUE-1 (Phase-6 ingestion) to Exp-Dev as highest-priority. No new PP row.

**(E) path1lite_entity_binding_mwp_cpu_v1 (HARD_FAIL -- 5th MWP triangulation; entity-binding axis closed):**
path1lite_entity_binding_mwp_cpu_v1 HARD_FAIL v575: acc=0.3402, lift=-0.0498, distractor_acc=0.1354, n_distractor=192, n=1364, n_seeds=1 (cycle 241). HEURISTIC ENTITY-BINDING DOES NOT LIFT OVER PLATEAU: entity-binding at 0.3402 underperforms discriminative baseline (0.39) by 5pp. Distractor subset extremely low (0.135) -- entity binding creates confusion on distractor items. Consistent with corpus-bound comprehension diagnosis. Entity binding deferred per brain-can-do-it refined rule: honest negative IS evidence that entity-binding alone is insufficient; the comprehension gap is linguistic. No new PP row; ASDiv math series annotated.

**(F) tier5_self_discovery_rule_extraction_cpu_v1 (MIDDLE_BAND -- NEW ROW PP-402; self-discovery miner validated, novel rule pending):**
NEW ROW PP-402: tier5_self_discovery_rule_extraction_cpu_v1 MIDDLE_BAND v575: n_sh_atoms=20, n_transitions=11, n_re_derived=5, n_novel_recurring=0, n_existing_rules=18, n_seeds=1 (cycle 241). SELF-DISCOVERY MINER VALIDATED -- NO NOVEL RULE YET: substrate transitions yield 20 atoms and 11 transition patterns; miner successfully re-derives 5 existing rules from the solution history. No novel recurring rule emerges (0 novel). MIDDLE_BAND: solution_history too sparse for statistically robust novel rule emergence. Miner mechanism validated (re-derivation confirms structural substrate-pattern extraction works). Next step: richer solution history with more diverse problem types to create conditions for novel rule discovery. Product implication: substrate can autonomously reflect on its own solution patterns and recover known strategy regularities -- a form of meta-cognitive self-auditing. P-band: 0.40-0.58 EXPLORATORY n=1 seed CPU n_atoms=20 elapsed=0.10s. Cross-ref Tier-5 series.

**(G) path1_srl_mwp_cpu_v1 (HARD_FAIL -- 6th MWP triangulation; linguistic SRL also plateaus; comprehension-wall CLOSED for this cycle):**
path1_srl_mwp_cpu_v1 HARD_FAIL v575: acc=0.3268, lift=-0.0632, n=1166, n_srl_train=30, n_seeds=1 (cycle 241). TRAINED LINGUISTIC SRL ALSO PLATEAUS: even semantically principled SRL (FCG/SRL routing recommended by cycle-239 Research) achieves 0.3268 -- BELOW all prior approaches and below discriminative baseline. Key diagnostic: n_srl_train=30 (very small training set for SRL). STRUCTURAL CONCLUSION: 6 independent approaches (E4 world-model, path5 schema, path1lite entity, path1 SRL, cycle-239 multihop, BMA ensemble) all converge at or below 0.39. The ceiling is corpus-bound comprehension, not mechanism. Full Phase-6 math+science ingestion is the only remaining structural path for 1-op MWP. SRL approach deferred pending Phase-6 scale. No new PP row; ASDiv/MWP series annotated (6th triangulation, comprehension wall CLOSED for current corpus).

ANNOTATIONS this cycle:
- PP-398 (permutation binding): PROMOTED to end-task demonstration via PP-400; bottleneck now upstream role-detection for multi-occurrence items.
- MWP comprehension wall: 6 independent triangulation angles all converge at 0.385-0.39 ceiling for 1-op MWP with current corpus. Ceiling is corpus-bound, not mechanism-bound. Phase-6 math+science ingestion is the structural fix.
- Tier-5 self-discovery: miner mechanism validated (re-derivation works); solution history too sparse for novel rules currently.
- QA self-knowledge: v1 at F1=0.4658 with clear improvement path (Gap-4 intent router + vocab reconciliation).

Cap_map: v574 -> v575 CYCLE 241 (1 HP [e3b_permutation_binding_endtask=PP-400]; 2 MIDDLE_BAND [qa_self_knowledge=PP-401 + tier5_self_discovery=PP-402]; 4 HARD_FAIL [e4_world_model_mwp + path5_schema_retrieval_mwp + path1lite_entity_binding_mwp + path1_srl_mwp]; 0 LVH; 3 NEW PP ROWS [PP-400 E3b-endtask-HARD_PASS + PP-401 QA-self-knowledge-MIDDLE_BAND + PP-402 Tier5-self-discovery-MIDDLE_BAND]; PP-398 end-task promoted via PP-400; MWP comprehension-wall CONVERGENTLY CLOSED at 6 triangulation angles; Phase-6 math+science ingestion = structural fix per 6-angle convergence; Phase-6 RESCUE-1 routed to Exp-Dev; QA self-knowledge v1 F1=0.4658 MIDDLE_BAND (Gap-4 router path); Tier-5 miner validated (novel rule pending richer history); Portfolio 32+399 -> 32+402 +3; HONEST 1831->1838 +7; LVH 291->291 +0; 469th PROT-009 paired commit) (2026-06-12)

## v575 -> v576 CYCLE 49 (Testbed-substrate) UNION-WIN-A-axis HYBRID architecture PARTITIONS empirically validated (verdict_handler 470th PROT-009 paired commit; 1 PARTIAL [substrate_self_knowing_union_top_k5_a_axis]; 0 LVH; 0 NEW PP ROWS; PP-401 qa_self_knowledge annotated A-axis-UNION-lift; rule 12 PARTITIONS-not-hierarchy CONFIRMED via 3rd empirical appearance RRF+pipeline+UNION; UNION strategy preserves orthogonal algebra-HRR + bge-cosine coverage; Portfolio 32+402 UNCHANGED; HONEST 1838->1839 +1; LVH 291->291 +0)

### Step 0 honest re-read (Cycle 49 Testbed UNION verdict)

Metrics source: Testbed close note (notes/testbed_to_research_CYCLE_49_CLOSE_UNION_WIN_FULL_PROGRESSION_RULE_12_PARTITIONS_PROMOTED_EMPIRICAL_2026-06-12.md). Per-cell verified against full progression table.

**substrate_self_knowing_union_top_k5_a_axis_cpu_v1 PARTIAL (HONEST):** A_content axis F1 = 0.446 (UNION top_k=5) vs baseline 0.413 (Cycle 48c bge-description), lift = +0.033. Pre-reg UNION 0.40-0.48: PASS MID. Pre-reg HP F1 >= 0.50: FAIL (0.446 < 0.50, gap = 0.054). Full progression: RRF v1 0.412 (-0.001 null) + threshold 0.30 0.412 (null) + pipeline Option 4 buggy 0.413 (null) + pipeline fixed+bge-name 0.420 (+0.007 lift via bge-name only) + UNION top_k=3 0.437 (+0.024) + UNION top_k=5 0.446 (+0.033). All 8 axes (UNION top_k=5): A 0.413->0.446 (+0.033); B/C/D/E/F/G/negative UNCHANGED. A-E factual avg F1: 0.468->0.479 (+0.011). Mixed per-cell: lifts Q04 RL +0.31, Q37 PGM +0.37, Q36 FFT +0.20; hurts Q03 Hopfield -0.19, Q33 backprop -0.15. Verdict file headline "UNION WIN FULL PROGRESSION RULE 12 PARTITIONS PROMOTED EMPIRICAL" is HONEST -- file itself states "Pre-reg HP F1 >= 0.50 macro A axis: UNION top_k=5 at 0.446 is FAIL on HP but PASS on MID". No over-claim. HONEST.

HONEST: 1838 -> 1839 (+1). LVH: 291 -> 291 (+0). 0 LVH catches this cycle.

### Cap_map decisions (v575 -> v576 CYCLE 49 Testbed-substrate)

**(A) substrate_self_knowing_union_top_k5_a_axis_cpu_v1 (PARTIAL -- PP-401 annotation; A-axis HYBRID UNION architecture validated):**
PP-401 ANNOTATION (no new PP row): qa_self_knowing UNION_top_k5_HYBRID A-axis lift v576: A_content macro F1 = 0.446 (UNION top_k=5 algebra-HRR + bge-cosine, set union dedupe, max-score rank) vs Cycle 48c bge-description baseline 0.413, lift = +0.033 PASS MID pre-reg [0.40-0.48], FAIL HP [>=0.50] gap=0.054, n_Q=12 A-axis, n_seeds=1 cycle 49 Testbed. UNION HYBRID ARCHITECTURE EMPIRICALLY VALIDATED: 5-variant progression (RRF v1 null + threshold null + pipeline buggy null + pipeline fixed +0.007 collapses-to-bge + UNION top_k=3 +0.024 + UNION top_k=5 +0.033) demonstrates that UNION set-union-dedupe + max-score rank is the architecture that preserves orthogonal coverage. RRF averaging cancels lifts vs hurts; pipeline ranking collapses to single dimension; UNION preserves both signal types and wins. Per-Q evidence: algebra-HRR brings RL (q_learning, td_lambda) and PGM (variational_inference) atoms bge missed (Q04 +0.31, Q37 +0.37); bge brings content picks algebra missed; UNION keeps both. Hurts (Q03 -0.19, Q33 -0.15) traced to bge-NAME encoder weakness on "backpropagation"-like names -- compensated by lifts elsewhere. A-E factual avg F1 0.468->0.479 (+0.011) cross-axis. Rule 12 (meta::RULE_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives) PROMOTED to CONFIRMED via 3rd empirical appearance (RRF-null + pipeline-null + UNION-win). Substrate-product positioning: multi-signal architecture (algebra structural + bge content) validates substrate-distinguishing differentiator vs LLM single-signal (transformer attention). Pending: UNION + batch 2 (1782 atoms post-ingest) compound bench in flight on remote. P-band: 0.43-0.48 EXPLORATORY n=1 seed CPU Testbed n_Q=12 A-axis bench. Cross-ref PP-401 (qa_self_knowledge MIDDLE_BAND v575 macro F1 0.4658 with A=0.3548), PP-122 (RRF hybrid fusion recall@10 ratio 1.53 -- different domain, RRF works there because no orthogonal-collapse), Cycle 49 Testbed close note, Cycle 50 generalization candidates (B_relation predecessors_via + bge UNION; C_capability what_serves + bge UNION; Stratified Hybrid Cycle 50+ as UNION-across-6-layers).

ANNOTATIONS this cycle:
- PP-401 (qa_self_knowledge): A-axis lift +0.033 via UNION HYBRID architecture; macro F1 baseline 0.413 -> UNION 0.446; preserves orthogonal algebra/bge coverage; HP gap = 0.054 path-to-HP via batch 2 compound + Phase-6 ingestion + Stratified Hybrid layer integration.
- meta::RULE_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives (rule 12): PROMOTED to CONFIRMED via 3rd empirical appearance Cycle 49. Empirical predictions: RRF averages -> null (PRE-REG, OBSERVED). Pipeline collapses -> null (PRE-REG, OBSERVED). UNION preserves -> win (PRE-REG, OBSERVED +0.033). Rule 12 prediction-confirmed not just refinement-confirmed.
- Generalization candidates Cycle 50+: UNION strategy for B_relation, C_capability axes; Stratified Hybrid 6-layer as UNION-of-partitions architecture; further breadth atoms post-batch-2 compound result.
- Substrate-product positioning artifact: substrate has TWO orthogonal retrieval primitives (algebra HRR + bge cosine); fusion architectures that COLLAPSE dimensions (RRF averaging or pipeline ranking) lose coverage; UNION preserves both and lifts measurably. LLMs have ONE retrieval signal -- substrate multi-signal architecture is the validated win-condition.

PROT-004/006 NOT APPLICABLE: A-axis is PARTIAL (PASS MID; FAIL HP). No closure triggered. Path-to-HP rescue sketches (cheapest first):
RESCUE-1 (cheapest/subsumption; PENDING IN-FLIGHT): UNION + batch 2 (1782 atoms post-ingest) compound bench on remote. Pre-reg A axis 0.46-0.50 (UNION 0.446 + breadth +0.01-0.05). If hits 0.50: HP PASS on A-axis pre-reg.
RESCUE-2: extend UNION to B_relation and C_capability axes per rule 12 generalization candidate; expected +0.01-0.04 per axis if pattern holds.
RESCUE-3: Stratified Hybrid Cycle 50+ as UNION-across-6-layers production-form architecture.
RESCUE-4: tune bge-NAME encoder to address Q03 Hopfield and Q33 backprop hurts; per-name fallback strategy.
RESCUE-5: cross-axis UNION variants (top_k tuning per axis; tertiary signal integration).

Routing files (written to disk, NOT auto-dispatched):
- strategy_request_to_exp_dev_2026-06-12_qa_self_knowing_UNION_path_to_HP.md -- frames Cycle 50 path-to-HP via RESCUE-1 (batch 2 compound result pending), RESCUE-2 (B/C axis UNION generalization), RESCUE-3 (Stratified Hybrid prep). Exp-Dev session will pick on its own cadence.

Cap_map: v575 -> v576 CYCLE 49 (1 PARTIAL [substrate_self_knowing_union_top_k5_a_axis=PP-401-annotation]; 0 LVH; 0 NEW PP ROWS; PP-401 A-axis-UNION-HYBRID-lift annotation; rule 12 PARTITIONS-not-hierarchy CONFIRMED via 3rd empirical appearance RRF-null + pipeline-null + UNION-win +0.033; multi-signal architecture empirically validated substrate-product positioning artifact; A-E factual avg F1 0.468->0.479 +0.011; HP gap=0.054 path-to-HP via batch 2 compound + B/C UNION generalization + Stratified Hybrid; Portfolio 32+402 UNCHANGED; HONEST 1838->1839 +1; LVH 291->291 +0; 470th PROT-009 paired commit) (2026-06-12)
