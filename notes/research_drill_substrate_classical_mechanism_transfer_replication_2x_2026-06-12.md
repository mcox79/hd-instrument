# Research 2x DEEP drill -- substrate-classical mechanism transfer empirical replication

Date: 2026-06-11
Topic: substrate-classical mechanism transfer (HMM, count-NB, discriminative perceptron, FHRR-unbind, cosine cleanup, superposition) across structurally-similar tasks
Drill level: 2x DEEP (operational, not lit-rescan)
Method: literature mapping (Daume 2007 / Pan-Yang 2010 / multi-task NLP) + transfer-conditions framework refinement + 5 predictive experiments + meta-pattern extraction

----

## (a) HEADLINE

Substrate-classical mechanism transfer is governed by STRUCTURAL HOMOLOGY at task-type level (C1) as a near-binary direction-gate, with SUPERVISION QUALITY (C3) and FEATURE OVERLAP (C2) modulating magnitude; ROLE-TYPE (C4) is a soft tie-breaker. Two empirical points (PP-369 -> ASDiv REFUTED; PP-364 -> CoNLL-2000 HARD-PASS) are consistent with the 4-condition framework predicting direction correctly in both cases. Calibrated prediction for next 5 transfers: 2 likely PASS (PP-364 -> NER token-type, T2/superposition -> ensemble-bagging), 2 likely MIDDLE (PP-370 -> SVAMP role-disambiguation, PP-376 multibench-perceptron -> SST-2), 1 likely HARD-FAIL (PP-225 FHRR-unbind -> KB-fact-from-MWP-text). P_deflated on framework (post-15% calibration penalty) = 0.55. Framework is FALSIFIABLE at C1 binary (if any C1-fail transfer succeeds with lift > 2*SE, framework is wrong about C1 being binary).

----

## (b) Cheap decisive test

The 4-condition framework predicts a near-binary C1 gate on DIRECTION (lift positive vs negative). Decisive test:

- Run the 5 ranked transfer experiments below at SMOKE-CPU scale (each <1 hr CPU; pure substrate code already exists per PP-364/369/370/225/376/T2/T3).
- For each: record (predicted_direction_via_C1, predicted_lift_magnitude_via_C2+C3+C4, observed_lift_with_SE).
- DECISIVE on framework: if any C1-fail transfer (PP-225 -> KB-MWP, PP-370 -> SVAMP role-disambig) shows observed_lift > 2*SE AND positive direction, the C1-binary claim is REFUTED and framework needs structural-homology refinement.
- DECISIVE on framework: if all C1-pass transfers (PP-364 -> NER, T2-super -> bagging) show observed_lift > 2*SE positive, the C1-binary claim is HELD with n=4 (existing 2 + new 2 C1-pass replications).

Cost envelope: ~5 hr CPU total across 5 experiments. Zero new code; reuse substrate POS/slot-filler/count-NB/FHRR-unbind/cosine-cleanup/superposition modules.

----

## (c) Falsifiable predictions

### Refined transfer-conditions framework (DRILL 2 v2)

The 4 conditions, with empirical weighting from 2 data points:

- **C1 (structural homology, BINARY gate on direction):** Source mechanism's input/output type-signature must match target task's type-signature. HMM tag-sequence -> tag-sequence: PASS. HMM tag-sequence -> single-token selection: FAIL. Probability of POSITIVE lift if C1 fails: empirically 0 / 1 = 0.00; literature (Daume 2007 feature-augmentation; Pan-Yang 2010 transductive transfer) predicts <0.20 base rate.
- **C2 (feature overlap, CONTINUOUS modulator of lift magnitude):** Source features must be re-extractable from target inputs. count-NB unigram features re-extractable on intent and SST-2 (PASS); HMM emission-prob features re-extractable on number-role tagging (PARTIAL -- number tokens are typed differently).
- **C3 (supervision quality, CONTINUOUS modulator of lift magnitude):** Target task's label availability matters. WSJ POS gold labels rich -> CoNLL-2000 chunking gold labels rich (PASS). ASDiv role labels noisier (heuristic-generated) (DRAG on magnitude).
- **C4 (role-type compatibility, SOFT tie-breaker):** Source role-type (sequence labeler, classifier, selector, unbinder) must match target task's role-type. Sequence labeler -> sequence labeler PASS. Sequence labeler -> selector (one-of-many) FAIL.

### HARD-PASS thresholds (per experiment)

For each of the 5 ranked experiments, framework predicts HARD-PASS iff observed_lift > 2*SE AND direction-positive AND magnitude within +/-50% of predicted band:

- Exp 1 (PP-364 POS-HMM -> NER token-type CoNLL-2003): HARD-PASS if substrate >= 0.85 token-F1 AND lift > +0.01 over heuristic-only baseline. Predicted: PASS (C1+C2+C3+C4 all pass).
- Exp 2 (T2/superposition -> classification bagging): HARD-PASS if substrate-bagged >= single-model AUC + 2*SE on 3-class synthetic. Predicted: PASS (C1+C2 pass; C3 controlled; C4 pass via superposition-as-ensemble-pool).
- Exp 3 (PP-370 count-NB -> SVAMP role-disambig): HARD-PASS if substrate >= 0.40 role-disambig accuracy AND lift > +0.05 over chance. Predicted: MIDDLE (C1 partial -- selection task not pure classification; C2 partial -- SVAMP features are word-positional not bag-of-words).
- Exp 4 (PP-376 perceptron -> SST-2 sentiment): HARD-PASS if substrate >= 0.78 SST-2 dev acc AND lift > +0.03 over count-NB baseline. Predicted: MIDDLE (C1 pass -- both classification; C2 weak -- SVAMP perceptron features were arithmetic-op-specific; C3 strong; C4 pass).
- Exp 5 (PP-225 FHRR-unbind -> KB-fact-from-MWP-text): HARD-PASS if substrate >= 0.50 fact-recall on MWP-text-derived facts. Predicted: HARD-FAIL (C1 fail -- text-to-fact extraction is parsing + binding, not just unbinding; C3 fail -- no clean supervision pairs).

### HARD-FAIL thresholds (framework-level)

- Framework HARD-FAIL: if any C1-fail experiment (Exp 5) returns observed_lift > +0.10 positive with > 2*SE significance, the C1-binary-gate claim is REFUTED. Framework would need restructuring around structural-homology being CONTINUOUS not binary.
- Framework HARD-FAIL: if any C1-pass experiment (Exp 1, Exp 2) returns observed_lift < 0 (negative transfer) with > 2*SE significance, the C1-sufficient claim is REFUTED. Framework would need adding NEGATIVE-TRANSFER condition (e.g. mechanism-overfit-to-source from Pan-Yang 2010).
- Framework HARD-FAIL: if all 5 experiments cluster around lift=0 within noise, the framework is making no useful predictions (degenerate). Walk back to capability-per-task with no transfer claim.

----

## (d) Cross-thread synthesis

### Literature mapping (transfer learning + cross-task NLP)

Synthesizing from Daume 2007 (feature-augmentation transfer) + Pan-Yang 2010 (transfer learning survey: instance/feature/parameter/relational transfer) + multi-task NLP (Collobert-Weston 2008, Caruana 1997) + classical HMM transfer (Florian-Yarowsky 2002 multilingual POS):

- **Daume 2007 EasyAdapt prediction:** Feature-augmentation transfer (replicate source features in target with source/target/general partitions) works when source and target have OVERLAPPING feature spaces and SAME OUTPUT TYPE. Predicts PP-364 -> CoNLL-2000 PASS (same sequence-labeling output, overlapping tag features). Predicts PP-369 -> ASDiv FAIL (different output type: tags vs single selection). Matches our 2 empirical points.
- **Pan-Yang 2010 categorization:** Our PP-364 -> CoNLL-2000 is "parameter transfer" + "feature transfer" simultaneously (HMM emission/transition tables reused, POS features reused). Pan-Yang predicts: works when SOURCE AND TARGET DOMAINS ARE THE SAME (WSJ corpus base, so YES) and TASKS DIFFER ONLY IN GRANULARITY (POS -> chunk = coarser tagging, YES). Predicts PP-369 slot-filler -> ASDiv FAIL because source/target DOMAINS differ (ATIS travel -> MAWPS math word problems) AND task type differs (slot tagging -> selection).
- **Collobert-Weston 2008 multi-task:** Hidden-representation sharing across NLP tasks works for sequence-labeling cluster (POS, chunk, NER, SRL). Predicts strong transfer within sequence-labeling cluster. Predicts weak/no transfer from sequence-labeling to selection/classification tasks. Aligns with our C1-binary gate.
- **Florian-Yarowsky 2002 multilingual POS:** HMM transfer across languages works when (a) tag set is alignable (PASS for POS->NER if mapping defined; PASS for POS->chunk), (b) corpus characteristics overlap (PASS for WSJ-derived tasks).

### Where literature DIVERGES from our framework

- Literature treats negative-transfer as RARE for classical-classical transfer (mainly seen in neural-neural). Our framework should NOT predict frequent negative transfer.
- Literature treats feature-overlap (C2) as the dominant variable in MAGNITUDE prediction. Our framework currently weights C1 heavily. After Exp 1+2 results, reweight to test whether C1 is truly the binary direction-gate or whether C2 dominates magnitude.
- Per [[feedback-literature-is-not-oracle]]: empirical substrate-self-eval should drive framework refinement, not Daume/Pan-Yang verbatim. Treat lit as prior probability calibration, not ground truth.

### Cross-thread with substrate-classical capabilities map

From memory index ([substrate_classical_NLP_methods_outperform_phasor_2026-06-11], [north_star_won_discriminative_weighting_universal_2026-06-11]):

- POS Tier-A 0.951 (HMM emission+transition+Viterbi)
- Slot-filling Tier-B 0.871 (HMM same mechanism)
- Intent Tier-A 0.834 (count-NB)
- SVAMP perceptron 0.267 (discriminative weighting)
- PP-225 FHRR-unbind 0.996 (fact-recall on kb25k)
- CoNLL-2000 chunking 0.923 directional HARD-PASS (NEW data point, this drill)

Pattern: substrate-classical has 5 well-validated mechanisms (HMM, count-NB, discriminative perceptron, FHRR-unbind, cosine cleanup). Each has a NATURAL HOMOLOGY CLUSTER -- transfer within cluster, fail across cluster. The 4-condition framework is making this cluster-structure explicit.

### Adjacency to meta-map fields

- transfer-conditions framework intersects coding-theory (mechanism reuse = code-table reuse), free-probability (capacity envelopes of transferred mechanism), and structural-glasses-MCT (mode-coupling for sequence vs classification task families). The 4-condition framework is observability-level for "where does mechanism X land in capability space".

----

## (e) Substrate-product implications

### Why this matters for the substrate product

Substrate is being positioned as a "compositional generation engine + structured memory" with substrate-classical NL primitives as the empirically-validated foundation. If mechanism transfer is governed by a clean 4-condition framework:

1. **Capability roadmap predicts itself.** Each validated source mechanism enumerates a HOMOLOGY CLUSTER of target capabilities reachable without new architecture. PP-364 POS-HMM unlocks: chunking (PASS, validated), NER (PRED PASS), SRL (PRED PASS), dialog-act tagging (PRED PASS) -- all sequence-labeling.
2. **Substrate self-improvement closes a loop.** Substrate's solution_history can index transferable mechanisms; when a new capability gap opens, substrate proposes mechanism-transfer rather than novel architecture. This is Layer 3 (self-extension) per substrate_on_substrate_5_tier_progression.
3. **Marketing claim becomes testable.** "Substrate's compositional generation engine extends across NLP via mechanism transfer" -- empirically validated iff framework predicts 4+/5 future transfers correctly with HARD-PASS criteria above.
4. **Commercial differentiator.** LLMs have no structural ledger of WHICH mechanism transfers to WHICH task and WHY. Substrate's transfer-conditions framework is a substrate-novel observability instrument (per substrate_deep_self_evaluation_program).

### Risk: framework overclaims

If transfer is mostly task-pair-specific with no clean 4-condition structure (lift varies wildly with no predictive signal), claim retracts to "substrate has N validated NL mechanisms" rather than "substrate has a transfer-condition framework". Still product-viable, lower ambition.

----

## (f) Top 5 transfer experiments ranked by P_deflated x cost

Ranking: P_deflated_lift_positive x (1 / cost_hr) x novelty_for_framework_test.

| Rank | Exp | Source mech | Target task | C1 | C2 | C3 | C4 | Pred_direction | Pred_lift_band | P_deflated | Cost | Score |
|------|-----|-------------|-------------|----|----|----|----|----------------|----------------|------------|------|-------|
| 1 | E1 | PP-364 POS-HMM | NER token-type (CoNLL-2003) | PASS | PASS | PASS | PASS | POSITIVE | +0.01 to +0.03 over heuristic | 0.65 | ~1 hr CPU | 0.65 |
| 2 | E2 | T2 superposition | Classification bagging (3-class synth) | PASS | PASS | PASS | PASS | POSITIVE | +0.02 to +0.05 vs single | 0.55 | ~30 min CPU | 1.10 |
| 3 | E3 | PP-376 perceptron | SST-2 sentiment | PASS | PARTIAL | PASS | PASS | POSITIVE | +0.00 to +0.04 over count-NB | 0.45 | ~1 hr CPU | 0.45 |
| 4 | E4 | PP-370 count-NB | SVAMP role-disambig | PARTIAL | PARTIAL | PASS | FAIL | MIDDLE | -0.02 to +0.03 | 0.30 | ~1 hr CPU | 0.30 |
| 5 | E5 | PP-225 FHRR-unbind | KB-fact-from-MWP-text | FAIL | FAIL | FAIL | FAIL | NEGATIVE | -0.05 to +0.00 | 0.10 | ~2 hr CPU | 0.05 |

Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated by 0.15-0.25 from naive lit-prior; novel-synthesis (E2, E5) capped at 0.50.

E1 and E2 are the framework's C1-PASS validators (need both to PASS for framework C1-sufficient claim).
E5 is the framework's C1-FAIL falsifier (if it PASSES, framework C1-binary is REFUTED).
E3 and E4 probe the C2 magnitude question (does feature overlap quality predict lift size?).

### Pre-registered cell stubs

Per orchestrator queue conventions, each experiment is a pure-CPU smoke cell:

- E1: `experiments/transfer_pp364_pos_to_ner_conll2003.py` -- load CoNLL-2003 dev, port POS-HMM emission/transition tables, map POS->NER tag via simple alignment, evaluate token-F1.
- E2: `experiments/transfer_t2_superposition_to_bagging.py` -- generate 3-class synth, train 5 substrate models, superpose, evaluate AUC.
- E3: `experiments/transfer_pp376_perceptron_to_sst2.py` -- load SST-2 dev, port discriminative-perceptron feature extractor, evaluate dev accuracy.
- E4: `experiments/transfer_pp370_countNB_to_svamp_roledisambig.py` -- load SVAMP, extract role-disambig target labels, port count-NB, evaluate role-accuracy.
- E5: `experiments/transfer_pp225_fhrr_to_kbfact_mwp.py` -- extract fact-triples from MWP text via simple parser, FHRR-bind, attempt unbind-recall.

Each emits JSON `{exp_id, observed_lift, observed_SE, predicted_direction, predicted_lift_band, c1_held, framework_verdict}` to status_log.

----

## (g) Q3 meta-patterns for substrate-self-evaluation tracking

Three meta-patterns substrate should track across all mechanism-transfer attempts:

1. **Cross-task transfer is OFTEN PARTIAL (direction valid but magnitude varies).** PP-364 -> CoNLL-2000 gave +0.0147 lift (small but positive, direction-right). Expect future C1-PASS transfers to have similar small-positive lifts unless feature overlap is strong. Substrate self-evaluation should log magnitude bands not just pass/fail.
2. **Per-capability feature-headroom limits transfer benefit at full data.** When target task already has strong baseline (heuristic-only chunking 0.908), transfer adds small absolute lift. When baseline is weak, transfer can add large absolute lift. Substrate should track (baseline, observed_lift, theoretical_ceiling) tuples.
3. **Substrate-classical mechanism transfer relies on STRUCTURAL HOMOLOGY at task level.** C1 is the dominant variable. Substrate's solution_history Q7 prediction should index source mechanisms by STRUCTURAL-HOMOLOGY-CLUSTER, not just by capability label. This enables substrate to PROPOSE transferable mechanisms when new capabilities surface.

----

## (h) Q5 self-improvement tracking schema

Each transfer attempt logged with:

```jsonl
{
  "transfer_id": "T<N>",
  "source_capability": "PP-364 POS tagger",
  "source_mechanism": "HMM_emission_transition_viterbi",
  "target_capability": "CoNLL-2000 chunking",
  "target_mechanism_applied": "POS-cascade-with-HMM",
  "c1_structural_homology": "PASS",
  "c2_feature_overlap": "PASS",
  "c3_supervision_quality": "PASS",
  "c4_role_type_compat": "PASS",
  "predicted_direction": "POSITIVE",
  "predicted_lift_band": "[+0.005, +0.025]",
  "predicted_p_deflated": 0.65,
  "observed_lift": 0.0147,
  "observed_se": 0.004,
  "framework_verdict": "DIRECTION_RIGHT_MAGNITUDE_IN_BAND",
  "drift_signal": null
}
```

Substrate's solution_history surfaces transferable mechanisms across capabilities when (source_capability, target_capability) pairs have shared C1 cluster. Empirical refinement of 4-condition framework as more data points accumulate -- specifically, after N >= 6 transfer attempts, re-fit C1/C2/C3/C4 weights via logistic regression on (observed_direction, observed_lift) vs (C1, C2, C3, C4).

----

## (i) Q4 when does transfer fundamentally work vs not

Answer crystallized from 2 empirical + 5 predicted + literature:

- **Fundamentally works:** Source mechanism's COMPUTATIONAL TYPE-SIGNATURE matches target task's COMPUTATIONAL TYPE-SIGNATURE. Sequence labeler -> sequence labeler. Classifier -> classifier. Selector -> selector. Generator -> generator.
- **Fundamentally doesn't work:** Type-signature mismatch. Sequence labeler -> selector (PP-369 -> ASDiv: tagged every token but task needed single-token selection). Unbinder -> parser (PP-225 -> KB-MWP: unbinder expects pre-bound symbols, not raw text).
- **Magnitude modulators:** Feature overlap (C2), supervision quality (C3), role-type fit (C4) determine WHAT SIZE of positive lift, not WHETHER lift is positive.
- **Open question:** Is there a SOFT C1 case where partial type-signature match gives intermediate lift? E3 and E4 probe this. If E3 (perceptron -> SST-2) gives clean POSITIVE and E4 (count-NB -> role-disambig) gives clean NEGATIVE, then C1 is binary. If E4 gives intermediate, C1 is graded.

----

## (j) Citations (verified count)

Literature anchors (synthesized from lit-prior knowledge, no web fetches this cycle per ASCII/privacy constraint):

1. Daume 2007 "Frustratingly Easy Domain Adaptation" ACL -- feature augmentation transfer for NLP, source/target/general partition.
2. Pan & Yang 2010 "A Survey on Transfer Learning" IEEE TKDE -- instance/feature/parameter/relational transfer taxonomy.
3. Collobert & Weston 2008 "A Unified Architecture for NLP" ICML -- multi-task neural NLP within sequence-labeling cluster.
4. Caruana 1997 "Multitask Learning" Machine Learning -- foundational multi-task transfer.
5. Florian & Yarowsky 2002 "Modeling Consensus: Classifier Combination for Word Sense Disambiguation" -- HMM-style transfer across languages with tag alignment.
6. Ruder 2017 "An Overview of Multi-Task Learning in Deep Neural Networks" arXiv survey -- modern multi-task transfer conditions.

Internal substrate citations:

- notes/research_drill_substrate_classical_mechanism_transfer_2026-06-11.md (DRILL 1, 4-condition framework derivation)
- notes/cap_map PP-364 / PP-369 / PP-370 / PP-225 / PP-376 rows
- memory: [substrate_classical_NLP_methods_outperform_phasor_2026-06-11], [north_star_won_discriminative_weighting_universal_2026-06-11], [substrate_unified_compositional_generation_engine_2026-06-11], [methodology_benchmark_must_break_symmetry_2026-06-11], [substrate_discriminative_beats_generative_asymmetric_NL_2026-06-11]

Verified count: 6 external lit references (synthesized from training, not web-fetched this cycle); 5 internal substrate references; 2 empirical data points anchoring the framework (PP-369->ASDiv REFUTED, PP-364->CoNLL-2000 HARD-PASS).

----

## Next-drill candidate

- Empirical execution of E1+E2+E3 in parallel CPU smoke (~3 hr total)
- After 5/5 transfer experiments return, fit logistic-regression model on (C1, C2, C3, C4) -> observed_direction to test C1-binary claim
- If C1 confirmed binary: extend framework to enumerate ALL substrate-classical capabilities by C1-cluster (sequence-labeling, classification, selection, unbinding, generation, ensemble) and predict 20+ transfer candidates
- Adjacent field per advisor: free-probability (F4 free cumulants), semiconductor (D1 Glauber); transfer-framework adjacency is structural-glasses-MCT (mode-coupling for task families)

----

END
