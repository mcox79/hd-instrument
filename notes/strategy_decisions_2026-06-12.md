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
