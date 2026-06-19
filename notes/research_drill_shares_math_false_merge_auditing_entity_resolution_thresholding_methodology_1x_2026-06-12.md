# Research drill: SHARES_MATH false-merge auditing via entity-resolution thresholding methodology

Date: 2026-06-12
Drill type: 1x scoped literature scan (4-6 generic queries)
Topic: pre-commit auditing methodology + confidence threshold tuning + false-positive rate measurement for SHARES_MATH edge population in capability knowledge graph
Scope: STRONG on standard entity-resolution / record-linkage thresholding; MODERATE on knowledge-graph edge proposal validation; SPECULATIVE on transfer to math-primitive equivalence (substrate-novel application of standard ER).

## Drill spec

A SHARES_MATH edge is proposed between two capability nodes when shared_primitive_strength (cosine similarity over the math_primitive vector field) exceeds a threshold tau. Failure mode is FALSE MERGES: assigning SHARES_MATH between capabilities that do NOT share underlying math (e.g. two capabilities with similar surface vocabulary but distinct binding/unbinding operators). Drill asks how the standard record-linkage / entity-resolution literature tunes tau, audits false-merges, and gates production deployment.

## Findings (compact)

1. Fellegi-Sunter record-linkage framework (1969) is the foundational methodology: pairwise similarity scores partition into three regions by two thresholds (tau_lo, tau_hi). Pairs above tau_hi: auto-MATCH. Pairs below tau_lo: auto-NON-MATCH. Pairs in [tau_lo, tau_hi]: REVIEW REGION requiring human adjudication. The two-threshold design is the dominant pattern in modern ER systems (Magellan, Dedupe.io, ZeroER).

2. Precision-recall tradeoff at varying tau is the standard calibration curve. Gold-standard sample of N hand-annotated pairs (typically N=50-500) gives empirical P(MATCH | similarity) and FPR/FNR estimates. Choosing tau where precision >= 0.90 is the dominant heuristic for high-stakes merges (master data management literature); precision >= 0.95 for medical / financial record linkage where false merge cost is catastrophic.

3. Crowdsourcing / multi-annotator adjudication: review-region pairs labeled by 2-3 independent annotators with Cohen's kappa >= 0.80 inter-annotator agreement gate. Pairs without consensus: explicit DEFER label, not auto-decided. (Wang-Kraska-Madden CrowdER 2012; Vesdapunt-Bellare-Dalvi 2014.)

4. Active learning for ER (Sarawagi-Bhamidipaty 2002; Bellare-Iyer-Rastogi 2012): instead of uniform random sample, prioritize annotation of pairs near the decision boundary tau where the model is most uncertain. Reduces gold-standard cost 5-10x for same precision target. Uncertainty = absolute distance from tau, or model-disagreement (ensemble of similarity scorers).

5. Calibration via isotonic regression / Platt scaling: raw similarity scores are not probabilities. Mapping similarity -> P(MATCH) via isotonic regression on gold-standard sample gives well-calibrated probabilities, then threshold on probability rather than raw similarity (Niculescu-Mizil-Caruana 2005).

6. False-merge audit pipeline (Stonebraker-Bruckner-Ilyas Tamr 2013; Konda et al. Magellan 2016): three layers — (a) blocking (reduce candidate pairs from O(n^2) to O(n)); (b) matching (similarity threshold proposes MATCH); (c) clustering / merging (transitive closure can compound errors; explicit conflict-resolution pass required before commit). Production systems gate edge insertion behind explicit precision floor measured on rolling gold sample.

7. Knowledge-graph edge proposal validation (Galarraga et al. AMIE 2013; Lao-Cohen 2010): rule-mined edges audited by hold-out triple completion. Edge-type-specific precision floors. False-positive systematic-class analysis: cluster false-merges by feature signature to identify mechanism (e.g. surface-vocabulary overlap without operator equivalence).

8. Schema matching (Rahm-Bernstein 2001; COMA++ 2005): when matching schema elements (close analog to capability nodes), composite similarity (name + structure + instance) outperforms single-similarity. Threshold tuning per match-type. Hand-curated thesaurus + structural constraints reduce false-positives 30-50% vs name-only matching.

## Synthesis: entity-resolution methodology applied to SHARES_MATH

The standard ER pipeline maps directly onto SHARES_MATH auditing:

1. **Blocking**: candidate pairs are the cross-product of capability nodes restricted to those with non-empty math_primitive vectors. With ~32 collision atoms + extension pairs, O(n^2) is tractable (no blocking needed at current scale).

2. **Similarity**: shared_primitive_strength = cosine over math_primitive vector field is the matching score.

3. **Two-threshold Fellegi-Sunter design**:
   - tau_hi (auto-MATCH): high precision (>= 0.90) region. SHARES_MATH edge committed.
   - tau_lo (auto-NON-MATCH): pairs below tau_lo not even proposed.
   - REVIEW region [tau_lo, tau_hi]: explicit DEFER state requiring human (Research) adjudication.

4. **Gold-standard sample**: hand-annotate 20-50 pairs spanning the similarity range as MATCH / NON-MATCH / AMBIGUOUS. Compute precision-recall curve. Choose tau_hi where precision >= 0.85 (substrate-quality-first conservative floor; below the 0.90 master-data-management standard because substrate is in low-data regime and small absolute gold sample limits precision estimate confidence — wider margin compensates).

5. **Calibration**: isotonic regression on gold sample maps cosine -> P(MATCH | cosine). Threshold on calibrated probability, not raw cosine. Probability is the substrate-correct semantics for what shared_primitive_strength claims.

6. **False-merge systematic-class analysis**: review MATCH region; classify each false-merge by its feature signature. Anticipated classes:
   - Same vsa_family (e.g. both FHRR) but distinct binding operator -> false merge via shared infrastructure not shared math.
   - Same input modality (both structured prediction) but distinct decoder math -> shared upstream not shared core.
   - Surface-vocabulary collision in primitive names without operator equivalence.

   Each class triggers a feature-engineering response: add an explicit feature axis (operator_signature, decoder_signature) so future SHARES_MATH proposals separate these classes.

7. **Active-learning loop**: subsequent gold-annotation rounds prioritize pairs nearest tau_hi where shared_primitive_strength is closest to the threshold. 5-10x annotation efficiency vs uniform random.

8. **Hold-out monitoring**: 20% of pairs reserved as hold-out test. Post-deployment precision measured on hold-out at each commit; regression triggers re-calibration.

## Pre-registered audit protocol for SHARES_MATH on 32 collision atoms + extension pairs

**Protocol PRE-REG (v1)**:

1. **Compute** shared_primitive_strength for all C(32, 2) = 496 pairs in collision set + extension pairs. Output triple (cap_a, cap_b, cosine).

2. **Sample for gold annotation**: stratified by cosine decile, 30 pairs total (3 per decile). Research hand-annotates as MATCH / NON-MATCH / AMBIGUOUS with one-sentence rationale citing the specific shared primitive (or its absence).

3. **Calibrate**: isotonic regression on 30 gold pairs -> P(MATCH | cosine) function. Pre-register isotonic monotonicity sanity check.

4. **Set tau_hi** = smallest cosine such that calibrated P(MATCH) >= 0.85 on gold sample. Set tau_lo = largest cosine such that calibrated P(MATCH) <= 0.20. REVIEW region between.

5. **Pre-commit audit**: for each proposed SHARES_MATH edge, log (cap_a, cap_b, cosine, calibrated_P, decision_region). Edges in REVIEW region NEVER auto-commit; explicit Research adjudication required.

6. **Systematic-class log**: every false-merge identified during gold annotation appended to false_merge_classes.jsonl with feature signature. After 5 false-merges in a single class, add explicit feature axis to math_primitive vector and re-calibrate.

7. **Hold-out test set**: 10 pairs reserved (not used for calibration). Post-commit precision measured on hold-out; precision_holdout < 0.80 triggers HARD_FAIL and rollback of edges committed since last calibration.

8. **HARD-PASS criterion (v1 deployment)**: precision_holdout >= 0.85 on N >= 10 hold-out pairs AND zero systematic-class with >= 3 instances.

9. **HARD-FAIL criterion**: precision_holdout < 0.70 OR any systematic-class >= 5 instances without feature-axis remediation.

## Substrate-product implications

Substrate-quality-first prefers conservative threshold (high precision, lower recall) over aggressive (high recall, low precision). False-merges propagate via transitive closure and corrupt downstream capability-equivalence claims, which are load-bearing for substrate-product positioning as a self-knowing system. A missed SHARES_MATH edge is recoverable (next drill catches it); a false SHARES_MATH edge poisons the structural ledger and undermines metacognition claims. Per meta::RULE_authoring_substrate_queries_first (4th appearance candidate), pre-commit audit gates structural writes the same way the 7 invariants gate Testbed writes.

The Fellegi-Sunter REVIEW region is the structural enforcement of "substrate writes done EITHER by us OR by substrate itself" (memory rule 8): cosine-and-calibrated-probability is the substrate's voice; Research adjudication in the REVIEW region is our voice. The two voices compose; neither alone commits.

## Honest scope

- STRONG (literature-grounded): Fellegi-Sunter two-threshold design, precision-recall calibration, gold-standard sample, isotonic calibration, active learning for ER, systematic false-positive class analysis. These are 30-50 year established methodologies with broad cross-domain validation.
- MODERATE (literature-grounded, transfer claim): applying ER methodology to math-primitive equivalence in a capability knowledge graph. Schema matching (Rahm-Bernstein) is the closest precedent; transfer is conceptually clean but no published direct precedent for math-primitive equivalence specifically.
- SPECULATIVE: specific tau_hi numeric (0.85 calibrated probability) is a substrate-quality-first heuristic, not a literature value. Hold-out precision floor 0.80 is conservative compared to 0.90 master-data-management standard, justified by small gold sample. Both tunable post-first-audit.

## Citations (verified count: 9)

1. Fellegi & Sunter (1969) "A Theory for Record Linkage" JASA — foundational two-threshold framework.
2. Sarawagi & Bhamidipaty (2002) "Interactive Deduplication using Active Learning" KDD — active learning for ER.
3. Niculescu-Mizil & Caruana (2005) "Predicting Good Probabilities With Supervised Learning" ICML — isotonic / Platt calibration.
4. Wang, Kraska, Madden (2012) "CrowdER: Crowdsourcing Entity Resolution" VLDB — multi-annotator adjudication.
5. Bellare, Iyer, Rastogi (2012) "Active Sampling for Entity Matching" KDD — uncertainty sampling near decision boundary.
6. Konda et al. (2016) "Magellan: Toward Building Entity Matching Management Systems" VLDB — production ER pipeline.
7. Galarraga, Teflioudi, Hose, Suchanek (2013) "AMIE: Association Rule Mining Under Incomplete Evidence" WWW — KG edge precision auditing.
8. Rahm & Bernstein (2001) "A Survey of Approaches to Automatic Schema Matching" VLDB Journal — composite similarity, threshold tuning per match-type.
9. Stonebraker, Bruckner, Ilyas et al. (2013) "Data Curation at Scale: The Data Tamer System" CIDR — production false-merge audit pipeline.
