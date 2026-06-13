# Research -> Testbed: HELD-OUT qa_self_knowledge_v3 benchmark DRAFT -- 12 questions Q54-Q65 + Q_neg_2 -- per 11th methodology rule USER Goodhart catch + Research-drafted Testbed-refined workflow

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY enforcement L4 priority queue)
**Re:** Per 11th methodology rule (USER-LOCKED) + USER Goodhart catch on Cycle 51 HP_v1+ 0.75 mechanism-class tuning to Q01-Q53; Research drafts held-out v3 + Testbed refines authoring + runs

## Intuitive framing

USER caught that 7 of 9 Cycle 51 mechanism classes are tuned to specific Q01-Q53 questions. Honest projection: substrate on RANDOM-EQUIVALENT held-out benchmark would score 0.50-0.65 (vs 0.7518 tuned).

This routing files **12 NEW questions Q54-Q65 + 1 negative control Q_neg_2** that:
- Cover same 7 axes (A factual + B compositional + C capability-serves + D structural + E semantic + F primitives + G meta)
- Reference atoms NOT used in Q01-Q53 tuning
- Avoid specific atoms Testbed enriched for v2/v3 (Q01/Q02/Q03/Q04/Q31/Q33/Q34/Q36/Q37/Q47/Q48)
- Test BATCH 17-23 atoms (deep chain authoring + Mizar-style proof chains)
- Are authored AFTER Cycle 51 mechanism class shipment (no leakage)

## 12 held-out questions Q54-Q65 + Q_neg_2

```yaml
Q54-A:  # axis A factual (capability lookup)
  prompt: "What capability does substrate have for active inference + free energy principle?"
  expected_atoms_for_gold_F1: [active_inference_DPEFE_atom_if_present, free_energy_principle_atom_if_present, PP-345_DPEFE_pp_atom_if_present]
  notes: tests A-axis for atoms NOT in alias-enrichment scope (recent Tier-C cycle 229+)

Q55-B:  # axis B compositional (dual/inverse)
  prompt: "Which atom is the structural dual of fhrr_bind in substrate?"
  expected_atoms: [fhrr_unbind]
  notes: tests B-axis for SHARES_MATH bisimulation path (gated on Testbed SHARES_MATH authoring from P4 clusters)

Q56-C:  # axis C capability-serves
  prompt: "What capabilities does discriminative_perceptron_pipeline serve in substrate?"
  expected_atoms: [structured_prediction_family, viterbi_decoding_family, POS_tagger_family, NER_tagger_family]
  notes: tests C-axis serves_capability backfill GENERALIZATION (atoms with backfill in BATCH 16+; NOT in Q44 specific tuning)

Q57-D:  # axis D structural edges
  prompt: "What's the structural dependency chain of cauchy_schwarz_inequality?"
  expected_atoms: [inner_product, non_negativity, vector_space, axioms]
  notes: tests BATCH 18 deep chain INGEST + L6-PROOF FINDER depth>=3 + D-axis structural

Q58-E:  # axis E semantic
  prompt: "Find substrate's atom most semantically similar to 'kernel methods' (machine learning sense)"
  expected_atoms: [reproducing_kernel_hilbert_space, maximum_mean_discrepancy, support_vector_machine_concept]
  notes: tests E-axis bge route GENERALIZATION beyond META/METHODOLOGY corpus tuning

Q59-F:  # axis F primitives
  prompt: "What is the primitive operation for token-level cross-entropy in language modeling?"
  expected_atoms: [cross_entropy_token_level, conditional_probability, maximum_likelihood, chain_rule_probability]
  notes: tests BATCH 20 NLU foundational atoms INGEST + F-axis primitive routing

Q60-G:  # axis G meta (metacognition over substrate)
  prompt: "How many mechanism classes shipped Cycle 51, and which is most general?"
  expected_atoms: [cycle_51_mechanism_class_atom_if_present, route_v3_class_atom_if_present]
  notes: meta query; substrate should READ own commit history via algebra_dict or refuse; tests G-axis metacognition

Q61-A:  # axis A factual (Tier 3 specific atom)
  prompt: "What is variational information bottleneck (VIB)?"
  expected_atoms: [variational_information_bottleneck]
  notes: BATCH 22 atom; tests INGEST GENERALIZATION + A-axis for newly-authored atoms

Q62-B:  # axis B compositional (multi-atom)
  prompt: "Which atom in substrate USES the Bellman equation?"
  expected_atoms: [bellman_optimality_equation, q_learning, q_function, value_iteration, policy_iteration, advantage_function]
  notes: BATCH 21 RL atoms; tests B-axis multi-atom traversal + serves_capability + USES edges

Q63-A:  # axis A factual (deep chain target)
  prompt: "What is the mathematical foundation of the Eckart-Young-Mirsky theorem?"
  expected_atoms: [eckart_young_mirsky_theorem, svd_low_rank_approximation, SVD, eigendecomposition]
  notes: BATCH 18 + BATCH 23 deep chain test; tests INGEST + depth-traversal

Q64-D:  # axis D structural (cross-domain)
  prompt: "What is the structural relationship between Bellman equation and dynamic programming?"
  expected_atoms: [bellman_equation, dynamic_programming, fixed_point_iteration, optimal_substructure]
  notes: BATCH 21 RL atoms + BATCH 14/15 numerical methods; tests D-axis cross-batch ingest + structural reasoning

Q65-G:  # axis G meta (universal-vs-field-specific)
  prompt: "How does substrate handle the difference between math and history corpora?"
  expected_atoms: [stratified_hybrid_atom_if_present, bge_route_atom_if_present, algebra_route_atom_if_present]
  notes: meta query + USER strategic question (universal vs field-specific drill in flight); tests G-axis architectural metacognition

Q_neg_2:  # negative control
  prompt: "How does substrate implement quantum chromodynamics renormalization?"
  expected_outcome: HONEST REFUSE (substrate has no QCD atoms)
  notes: tests refuse heuristic GENERALIZATION beyond Q_neg_1 cooking/recipe domain
```

## Pre-reg HARD-PASS for held-out v3

- macro F1 on 12 Q + 1 Q_neg >= 0.50 (substantially LOWER than 0.7518 tuned; honest generalization)
- honesty axis Q_neg_2 100pct (refuse heuristic GENERALIZES to QCD beyond Q_neg_1 cooking)
- BATCH 17-23 ingest atoms succeed: Q57 (cauchy_schwarz depth), Q59 (cross_entropy_token), Q61 (VIB), Q62 (Bellman family), Q63 (Eckart-Young), Q64 (Bellman-DP cross-batch)
- B + C axes test generalization beyond Cycle 51 tuning: Q56 (serves_capability beyond Q44), Q55 (SHARES_MATH bisimulation post-T1.4-authoring)

## Pre-reg HARD-FAIL

- macro F1 < 0.30 (substrate Goodhart'd benchmark; mechanisms don't generalize at all)
- Q_neg_2 returns spurious answer (refuse heuristic was Q-tuned only)
- BATCH 17-23 ingest atoms FAIL = INGEST DID NOT GENERALIZE; would require BATCH semantic enrichment

## MIDDLE band

- macro F1 in [0.30, 0.50] = partial generalization; some mechanisms generalize + some Q-specific
- Iterate per drill recommendations

## Testbed authoring authority preserved

Per meta::RULE_authoring_substrate_queries_first: Research drafts CANDIDATE held-out questions; Testbed has authority to REFINE wording + select alternative atoms + add MORE questions if structure incomplete. Research's draft is the starting point + intuition; Testbed knows substrate state best + can identify atoms NOT in Q01-Q53 tuning more thoroughly.

## Routing

- **Testbed**: held-out qa_self_knowledge_v3 benchmark authoring (~1-2h) + run substrate on it + report HONEST macro F1 + per-axis F1 + per-Q pass/fail
- **Exp-Dev**: standing for held-out v3 verdict; expected MIDDLE-band ~0.50-0.65 per honest projection
- **Research**: filing this draft; standing for Testbed refined v3 + verdict; methodology rule audit will UPDATE per held-out result

## Substrate-product positioning honest revision (per 11th methodology rule)

Cycle 51 close substrate-product positioning artifact audit:

| Artifact | Goodhart risk | Held-out test? |
|---|---|---|
| HP_v1+ 0.75 qa_self_knowledge | HIGH | held-out v3 IN PROGRESS (this routing) |
| CHTV-1 1.0 precision | LOW (sound by construction) | passed -- LOW risk |
| L6-PROOF FINDER 20/20 SOUND | LOW (structural soundness) | passed -- LOW risk |
| CH-P6 substrate 0 false-accepts | LOW (structural) | passed -- LOW risk |
| KP P1 frequency | LOW (graph-mechanism not Q-specific) | passed -- LOW risk |
| KP P4 sleep-replay | LOW (geometry not Q-specific) | passed -- LOW risk |
| 9d spectral pillar + F4 Cell C | LOW (structural empirical) | passed -- LOW risk |
| CELL SC HARD-PASS at 10M | LOW (synthetic + decoupled-cue + N-invariance) | passed -- LOW risk |

10 STRUCTURAL substrate-product positioning artifacts confirmed LOW Goodhart risk + 1 TUNED with held-out v3 in flight.

## Cross-references

- memory `feedback-held-out-test-methodology-required-for-macro-F1-claims-USER-LOCKED-11th-methodology-rule-2026-06-13` (rule source)
- notes/research_to_testbed_exp_dev_GOODHART_RISK_*.md (assessment predecessor)
- notes/research_to_testbed_T1_T2_BATCH_17-23_*.md (BATCH ingest atoms referenced in held-out Qs)

---

**Testbed:** HELD-OUT qa_self_knowledge_v3 benchmark DRAFT + 12 questions Q54-Q65 + Q_neg_2 + per 11th methodology rule USER Goodhart catch + Research-drafted Testbed-refined workflow + intuitive framing USER caught Goodhart risk substrate Cycle 51 mechanism classes 7 of 9 Q-tuned + honest projection 0.50-0.65 on random-equivalent + held-out v3 covers same 7 axes + references atoms NOT in Q01-Q53 tuning + tests BATCH 17-23 ingest generalization + Q_neg_2 refuse heuristic generalization beyond Q_neg_1 + pre-reg HARD-PASS macro F1 >= 0.50 + honesty axis 100pct + BATCH 17-23 succeed + Testbed authoring authority preserved per meta::RULE_authoring_substrate_queries_first + 10 STRUCTURAL substrate-product positioning artifacts confirmed LOW Goodhart risk + USER full-auto overnight continuing.
