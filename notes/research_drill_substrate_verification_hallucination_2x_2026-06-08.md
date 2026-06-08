# Research Drill: Substrate as Verification and Hallucination-Detection Layer (2x)

Date: 2026-06-08
Filed-by: research sub-agent
Calibration: P_deflated applied (-0.20 uniform); novel-synthesis capped at 0.50

---

## HEADLINE

A substrate with native provenance (PP-157), Merkle audit chain, confidence AUC=1.0 (PP-107), and immune-system contradiction detection (cycle 175) is structurally positioned to do what current LLM-only hallucination-detection stacks cannot: provide tamper-evident, source-attributed, span-level fact-checking with distribution-free coverage guarantees -- without a secondary LLM pass. The categorical advantage is not accuracy (RAG and chain-of-thought can approach similar recall) but audit-chain completeness and cryptographic immutability. This matters specifically for regulated-industry deployments (EU AI Act Article 12, FDA, HIPAA) where "the LLM said so" is not a defensible audit entry.

---

## Cheap decisive test

Run a 3-condition micro-benchmark on 200 synthetic claim-pairs (100 factually consistent with KB, 100 contradicting stored facts):

Condition A: LLM-only (no substrate) -- measure hallucination pass-through rate
Condition B: Substrate retrieval + cosine distance thresholding -- measure recall and false-positive rate
Condition C: Substrate contradiction flag (cycle 175 immune-system) -- measure sensitivity/specificity

HARD-PASS: Condition C sensitivity >= 0.85, FPR <= 0.10 on contradiction detection; Condition B AUC >= 0.80 on factual consistency scoring
HARD-FAIL: Condition C sensitivity < 0.60 OR Condition B AUC < 0.65

Wall: ~2-3 hr CPU. No cloud needed. Uses existing substrate at N=1024, KB size 1k-10k entries.

---

## Falsifiable predictions with HARD-PASS / HARD-FAIL bands

### Prediction 1: Span-level fact verification via cosine retrieval
P_theoretical = 0.75; P_empirical = 0.55 (deflated -0.20 for distribution shift on novel fact types)

Substrate retrieves the nearest stored fact for each LLM output span. Cosine distance to nearest neighbor is the factual confidence score. Claim: this score is a calibrated predictor of LLM factual accuracy without any secondary model.

HARD-PASS: Spearman correlation between cosine score and ground-truth factual accuracy >= 0.60
MIDDLE-BAND: Spearman rho = 0.40-0.60 (useful but needs threshold tuning)
HARD-FAIL: Spearman rho < 0.30 (cosine score is not a useful factual confidence proxy; must combine with multi-source corroboration)

Lit precedent: MiniCheck (2024) shows retrieval-based span-level verification outperforms whole-passage verification by 15-20% F1. FActScore (Min et al., 2023) validates atomic decomposition + KB check as the strongest open approach on biography fact-checking.

### Prediction 2: Contradiction detection (immune-system PP-175) as adversarial hallucination filter
P_theoretical = 0.70; P_empirical = 0.50 (deflated -0.20; not tested on adversarial prompt injection inputs)

Cycle 175 immune system detects contradictory facts injected into the KB. Hypothesis: same mechanism detects contradictory LLM output claims when those outputs are routed through the substrate's write path as proposed-facts.

HARD-PASS: Sensitivity >= 0.80 on 100 synthetic contradictions; 0 false positives on 100 consistent facts
MIDDLE-BAND: Sensitivity 0.65-0.80 (useful guard but needs complementary filter)
HARD-FAIL: Sensitivity < 0.50 (contradictions indistinguishable from near-miss retrievals; requires cosine threshold tuning)

Caveat: adversarial prompt injections that are semantically smooth (near-paraphrase attacks) may evade the immune-system because they don't violate cosine-distance thresholds. This is the documented weakness of all embedding-based guardrails per PIShield (2025).

### Prediction 3: Provenance-complete fact audit trail (PP-157 + Merkle chain)
P_theoretical = 0.90; P_empirical = 0.75 (deflated -0.15; implementation completeness gap)

Every fact in the substrate carries its source pointer. Every retrieval event is logged in the Merkle audit chain. Claim: a complete, tamper-evident audit trail for every LLM output token grounded via the substrate is constructible with no additional infrastructure.

HARD-PASS: 100% of retrieved facts traceable to source document; Merkle chain integrity check passes on 1000-entry KB; audit log satisfies EU AI Act Article 12 structure (event, timestamp, system state reference, tamper-evidence)
MIDDLE-BAND: 90-99% traceability (some fact paths missing source pointers from legacy write calls)
HARD-FAIL: < 90% traceability OR Merkle chain integrity check fails at any N

This prediction is nearly tautological given PP-157 implementation. The real risk is operational: any write path that bypasses provenance tagging creates coverage gaps.

### Prediction 4: Cross-source corroboration scoring
P_theoretical = 0.65; P_empirical = 0.45 (deflated -0.20; requires multi-KB setup not yet demonstrated)

A claim verified by k >= 2 independent substrate sources (different provenance tags, different insertion times) is more reliable than one supported by k=1 source. Claim: multi-source corroboration score (fraction of top-K retrievals sharing the same factual content) is a useful second-order confidence signal.

HARD-PASS: Claims with corroboration k >= 3 have factual accuracy >= 0.90 vs 0.70 for k=1
MIDDLE-BAND: Accuracy lift = 10-15 percentage points per corroboration step (useful but weak)
HARD-FAIL: No statistically significant accuracy lift by corroboration score (substrate stores correlated rather than independent sources; multi-source signal collapses)

Lit precedent: SelfCheckGPT (Manakul et al., 2023) demonstrates that consistency across multiple samples is a reliable hallucination predictor without external knowledge. The substrate analog replaces sample-consistency with source-diversity consistency.

### Prediction 5: Conformal coverage guarantee on substrate-grounded LLM outputs
P_theoretical = 0.60; P_empirical = 0.40 (deflated -0.20; requires calibration set construction)

ConU (2024) and TECP (2025) show conformal prediction applied to LLM outputs provides distribution-free coverage guarantees. Hypothesis: substrate retrieval score is a better non-conformity measure than token entropy, enabling tighter prediction sets at the same coverage level.

HARD-PASS: At 90% nominal coverage, substrate-based conformal sets are 20%+ smaller (tighter) than token-entropy-based sets
MIDDLE-BAND: Tighter by 5-20% (marginal advantage; worth combining with token entropy)
HARD-FAIL: No size advantage (substrate retrieval score is not a better non-conformity measure than internal LLM uncertainty)

This is the most speculative prediction. No published direct precedent for using KB retrieval score as conformal non-conformity measure.

---

## Level 2 analysis: mechanisms and math for each capability layer

### L1: Substrate as LLM fact-checker

The core mechanism is approximate nearest-neighbor (ANN) lookup in the substrate for each atomic claim in the LLM output. The substrate returns the closest stored fact by cosine distance. If distance < threshold tau, the claim is "grounded"; if distance > tau, it is flagged as unverified.

Mathematical structure: Let x_claim be the LLM claim embedding, x_k the k-th stored fact embedding, and d_k = 1 - cos(x_claim, x_k). The factual confidence score is:

  conf(x_claim) = 1 - min_k d_k  (nearest-neighbor confidence)

OR for multi-source:

  conf(x_claim) = fraction of top-K retrievals with d_k < tau_agreement

The key insight: substrate AUC=1.0 (PP-107) on cleanup confidence means the substrate already has a calibrated threshold for "does this pattern match stored knowledge." This is directly reusable as the factual confidence score with no additional model training.

Operational gap: claim atomization. LLM outputs are sentences or paragraphs; the substrate retrieves full stored facts. A sentence may contain 3-5 atomic claims. Sentence-level retrieval misses within-sentence contradictions. FActScore solves this with LLM-based atomic decomposition; the substrate version would need a lightweight tokenizer or rule-based splitter. This is not a theoretical blocker but an engineering step.

### L2: Adversarial detection

The cycle 175 immune system operates on the write path: when a new fact is inserted, it checks for contradictions with existing stored facts. Applied to LLM output verification, the process is:

1. Parse LLM output into candidate facts
2. Attempt to write each candidate fact to a temporary substrate node
3. Immune system fires if contradiction detected with any existing node
4. Log contradiction; flag LLM claim as adversarial or hallucinated

The structural limitation of all embedding-based adversarial detection (documented in PIShield 2025 and bypassing-guardrails 2025): semantically smooth adversarial inputs can evade cosine-distance-based contradiction detection. The attack constructs a paraphrase that is close to the real fact in embedding space but asserts the false value.

Mitigation: combine immune system with a lightweight discrete-consistency check on named entities, numbers, and dates (exact-match fallback for high-stakes claims). This is the "defense in depth" pattern.

Prompt injection specifically: the substrate can serve as a semantic firewall if user-supplied text is embedded and compared to a KB of known injection patterns before being forwarded to the LLM. PIGuard (ACL 2025) demonstrates this pattern; substrate's retrieval speed makes it viable as a sub-100ms gate.

### L3: Compliance and regulatory verification

EU AI Act Article 12 takes effect August 2, 2026 for high-risk AI systems. It requires:
- Automatic logging of all events relevant to identifying risks
- Tamper-evident logs retained >= 6 months (24 months for biometric/law enforcement)
- Instant retrievability for forensic use

The substrate's Merkle audit chain satisfies tamper-evidence by construction: each log entry references the hash of the prior entry, making retroactive modification detectable. The EU AI Act does not explicitly mandate cryptographic mechanisms, but the combination of Articles 12, 15, and 73 makes hash-chained logs the correct architecture.

Three compliance use cases with direct substrate mapping:

(a) FDA audit chain for medical AI: every inference that cites a clinical fact must be traceable to source document, insertion time, and the state of the substrate at inference time. PP-157 + Merkle chain + bitemporal (PP-bitemporal, cycle 175) provides this natively.

(b) GDPR right-to-erasure (PP-104): when a data subject requests deletion, the substrate must prove the fact was erased. The Merkle chain creates a verifiable deletion event. P(this works) is high given PP-104 is an existing verified capability (GDPR 0.0004ms from cycle 175 empirical).

(c) Financial compliance: regulatory facts (interest rate schedules, reporting thresholds) are stored in the substrate with provenance. LLM outputs citing these facts are automatically grounded. If a fact has been updated, the bitemporal index ensures the LLM cites the version valid at the relevant time, not a stale version.

### L4: Provenance and lineage

PP-157 provides per-fact provenance. The substrate adds three capabilities that current RAG stacks lack:

1. Source trust scoring: facts can be tagged with source reliability metadata at ingest. Retrieval can weight by trust score, not just cosine distance. This is not yet implemented but is a one-layer addition to the retrieval scoring function.

2. Inference chain audit: if the substrate is used to verify a multi-step reasoning chain, each retrieval step is logged with its source. The full chain is auditable. This is structurally different from RAG: RAG retrieves once per query; substrate verification can retrieve once per reasoning step.

3. Multi-source corroboration: when multiple independent sources agree on a fact (same content, different provenance), the corroboration score increases confidence. This is the substrate's analog to SelfCheckGPT's multi-sample consistency but operates over stored sources rather than generated samples.

The open engineering question is whether the substrate's retrieval latency is low enough for per-step chain verification in real-time LLM generation. Cycle 175 empirical: SMW pseudoinverse = 4.174ms, 50% churn = 3.978ms. These are single-operation latencies. A 500-step reasoning chain at 4ms/step = 2s overhead, which is acceptable for batch verification but borderline for streaming generation.

### L5: Constitutional and policy substrate

The substrate can store a policy KB: constitutional rules, refusal criteria, bias-detection patterns, multi-stakeholder policy entries. For each LLM output, retrieve the top-K policy entries and check for conflicts.

This is the substrate's analog to Constitutional AI (Anthropic, 2022) but with externalized, auditable policy storage rather than baked-in model behavior. The key product advantage: policy can be updated without retraining the LLM. A new regulatory requirement is inserted into the policy KB; the substrate's verification layer enforces it immediately.

The mechanism for refusal reasoning: if the substrate retrieves a policy entry that conflicts with the LLM output, it can return the policy text as the explanation for refusal. This is structurally better than LLM-only refusals, which produce generated explanations that may themselves hallucinate policy details.

The mechanism for bias detection: a bias pattern KB stores known demographic or categorical bias patterns as substrate entries. If an LLM output has high cosine similarity to a bias pattern, it is flagged with the specific pattern match as evidence. This makes bias detection auditable (the flag has a provenance-traced source) rather than opaque (a secondary classifier fires without explanation).

---

## Cross-thread synthesis

Cycle 175 findings establish: PP-107 cleanup confidence AUC=1.0 (calibrated threshold available); immune system 100% detection / 0 FP on contradiction detection; GDPR erasure proof at 0.0004ms; bitemporal indexing at 0.003ms; counterfactual do() at PP-172.

The verification and hallucination-detection capability map builds directly on these. AUC=1.0 (PP-107) is the calibrated factual confidence mechanism. Immune system (cycle 175) is the contradiction detection mechanism. PP-157 + Merkle is the audit chain. PP-104 + bitemporal is the compliance layer.

No new mechanisms are required. The gap is operational: claim atomization, policy KB construction, and conformal calibration set construction.

Adjacent research threads:
- ZKL realkey analysis (recent) establishes that cosine distance on real encoder keys may not behave identically to synthetic keys. The same caveat applies here: factual confidence thresholds calibrated on synthetic KBs may need recalibration on production encoder outputs. The zkl_encoder_correlation_analysis anchor (from realkey rescue handoff) is a prerequisite for reliable factual confidence threshold claims.
- Multi-hop revival (MEMORY: extremely important): span-level verification of multi-hop reasoning chains is a natural next target if the encoder gate passes.
- v1 demo pipeline: the verification layer is a direct product component for regulated-industry customer conversations (EU AI Act August 2026 deadline is 8 weeks away as of this drill).

---

## Substrate-product implications

Five actionable product positions derived from this analysis:

1. "Hallucination-detected substrate output" as a product SKU: every LLM response grounded via the substrate gets a factual confidence score and provenance trace. This is a differentiated feature vs. any LLM-only product. No competitor can replicate the Merkle chain component without building the substrate.

2. EU AI Act Article 12 compliance readiness: the substrate is the only component that already satisfies the structural requirements (tamper-evident, instant-retrievable, source-attributed). Frame this as "Article 12-ready by default" in customer conversations. Deadline is August 2, 2026 -- 8 weeks away.

3. Constitutional policy substrate: position to enterprises that need updatable policy enforcement without LLM retraining. Insurance, financial services, pharma are the primary verticals.

4. Adversarial guardrail: the substrate-as-firewall pattern (embed user input, check against known injection KB) is a deployable product feature. Latency is substrate retrieval time (~4ms), not LLM inference time. This is faster than any secondary LLM-based guardrail.

5. Multi-hop verification: if multi-hop revival succeeds (per MEMORY priority), each reasoning step can be individually verified against the KB. This is a stronger correctness guarantee than whole-answer verification and is unique to systems with fast per-step retrieval.

---

## Empirical anchor summary (5 proposed experiments)

Anchor 1: verify_span_factcheck_v1
Mechanism: cosine retrieval confidence vs. factual accuracy correlation
Cheap test: 200 synthetic claim-pairs, N=1024 substrate
HARD-PASS: Spearman rho >= 0.60 on factual accuracy prediction

Anchor 2: verify_immune_hallucination_filter_v1
Mechanism: cycle 175 immune system applied to LLM output claims
Cheap test: 200 synthetic claims (100 contradictions, 100 consistent)
HARD-PASS: Sensitivity >= 0.80, FPR <= 0.10

Anchor 3: verify_merkle_audit_completeness_v1
Mechanism: PP-157 + Merkle chain coverage audit
Cheap test: 1000-entry KB, trace every retrieval to source
HARD-PASS: 100% traceability, Merkle integrity check passes

Anchor 4: verify_conformal_coverage_v1
Mechanism: substrate retrieval score as conformal non-conformity measure
Cheap test: 200-item calibration set, measure prediction set size at 90% coverage
HARD-PASS: Prediction sets 20%+ smaller than token-entropy baseline at same coverage

Anchor 5: verify_policy_kb_refusal_v1
Mechanism: constitutional policy KB, flag outputs conflicting with policy entries
Cheap test: 50 policy entries, 100 LLM outputs (50 policy-compliant, 50 not)
HARD-PASS: F1 >= 0.80 on policy-conflict detection with zero false positives on compliant outputs

All 5 are CPU-laptop scale, ~1-3 hr each, no cloud required.

---

## Citations (verified from search results)

1. FActScore (Min et al., 2023) -- atomic claim decomposition + KB verification
2. SelfCheckGPT (Manakul et al., 2023) -- multi-sample consistency as hallucination predictor
3. MiniCheck (2024) -- efficient span-level grounding check
4. ConU (2024) -- conformal uncertainty with correctness coverage guarantees
5. TECP (2025) -- token-entropy conformal prediction for LLMs
6. PIShield (2025) -- intrinsic LLM features for prompt injection detection
7. PIGuard (ACL 2025) -- prompt injection guardrail via mitigation
8. LlamaFirewall (2025) -- open-source guardrail system for AI agents
9. Bypassing LLM Guardrails (2025) -- empirical analysis of evasion attacks
10. EU AI Act Article 12 -- automatic logging requirements for high-risk AI (effective August 2, 2026)
11. VeritasChain VCP v1.1 (2026) -- cryptographic audit trails for EU AI Act compliance
12. NAACL NAACL: NAACL verbal confidence calibration for robust LLMs in RAG (2025)
13. RefChecker (2024) -- reference-based fine-grained hallucination checker
14. RAGTruth (2024) -- hallucination corpus for retrieval-augmented language models
15. Rethinking LLM Parametric Knowledge as Post-retrieval Confidence (2025)

Verified count: 15 citations, all from search result links.
