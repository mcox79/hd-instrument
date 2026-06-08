# exp_dev hand-off -- research: substrate verification and hallucination detection 2x

Filed-by: research sub-agent
Date: 2026-06-08
Trigger: notes/research_drill_substrate_verification_hallucination_2x_2026-06-08.md
Urgency: HIGH -- EU AI Act Article 12 deadline is August 2, 2026 (~8 weeks); verification layer is a customer-facing product claim candidate

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: verify_span_factcheck_v1

Anchor pointer: Research note Section "Prediction 1" + "L1: Substrate as LLM fact-checker"
Substrate-product reading: Measures whether cosine retrieval confidence (1 - min cosine distance to KB) correlates with factual accuracy of LLM output claims. If Spearman rho >= 0.60, the substrate confidence score is a directly usable factual accuracy predictor. PP-107 cleanup confidence AUC=1.0 implies the threshold infrastructure already exists.
Tier hint: CPU laptop, ~1-2 hr. CHEAPEST. Gates downstream conformal prediction anchor.
Why-now: This is the single cheapest proof point for the "hallucination-detected substrate output" product position. A 1-2 hr run produces a customer-presentable number. Must run before any conformal calibration work.

Pre-reg bands:
  HARD-PASS: Spearman rho >= 0.60 between cosine confidence and factual accuracy on 200 synthetic claim-pairs
  MIDDLE-BAND: rho = 0.40-0.60 (useful signal; combine with multi-source corroboration)
  HARD-FAIL: rho < 0.30 (cosine confidence not useful as standalone factual predictor)

### Anchor 2: verify_immune_hallucination_filter_v1

Anchor pointer: Research note Section "Prediction 2" + "L2: Adversarial detection"
Substrate-product reading: Applies cycle 175 immune system to LLM output claims treated as proposed-facts. Measures sensitivity and false-positive rate on 200 synthetic claims (100 contradictions, 100 consistent). If sensitivity >= 0.80 and FPR <= 0.10, the immune system is a deployable hallucination guard with a provenance-complete audit trail.
Tier hint: CPU laptop, ~1-2 hr. Can run in parallel with Anchor 1.
Why-now: The immune system is already implemented. This is a measurement run, not engineering work. If it passes, it becomes an immediate product claim.

Pre-reg bands:
  HARD-PASS: Sensitivity >= 0.80, FPR <= 0.10 on contradiction detection
  MIDDLE-BAND: Sensitivity 0.65-0.80 (useful guard; needs threshold tuning or complementary discrete check)
  HARD-FAIL: Sensitivity < 0.50 (immune system not suitable as primary hallucination filter; re-route to cosine-threshold-only approach)

### Anchor 3: verify_merkle_audit_completeness_v1

Anchor pointer: Research note Section "Prediction 3" + "L3: Compliance / regulatory"
Substrate-product reading: Runs a completeness audit on PP-157 provenance + Merkle chain for a 1000-entry KB. Measures traceability rate and Merkle integrity. If 100% traceability and integrity check pass, the substrate can be presented as EU AI Act Article 12-ready. GDPR erasure already empirically validated at 0.0004ms (cycle 175).
Tier hint: CPU laptop, ~1 hr. Near-certain PASS given PP-157 is a verified capability. Run for documentation, not discovery.
Why-now: EU AI Act Article 12 takes effect August 2, 2026. An empirically validated audit completeness result is a direct sales enablement artifact for regulated-industry customers.

Pre-reg bands:
  HARD-PASS: 100% traceability, Merkle integrity check passes on 1000-entry KB
  MIDDLE-BAND: 90-99% traceability (operational gap in write path bypassing provenance tagging)
  HARD-FAIL: < 90% traceability OR Merkle chain integrity failure (PP-157 implementation has coverage gaps)

### Anchor 4: verify_policy_kb_refusal_v1

Anchor pointer: Research note Section "L5: Constitutional / policy substrate"
Substrate-product reading: Builds a 50-entry policy KB, generates 100 LLM outputs (50 policy-compliant, 50 policy-violating), and measures F1 for policy-conflict detection via substrate retrieval. If F1 >= 0.80 with zero false positives on compliant outputs, the substrate is a viable constitutional policy enforcement layer. Key advantage over LLM-only: policy updates at KB-write time, not LLM retraining time.
Tier hint: CPU laptop, ~2-3 hr including KB construction.
Why-now: Constitutional policy substrate is directly addressable to insurance, financial services, and pharma customers who need audit-traceable policy enforcement without LLM retraining costs.

Pre-reg bands:
  HARD-PASS: F1 >= 0.80 on policy-conflict detection; 0 false positives on compliant outputs
  MIDDLE-BAND: F1 = 0.65-0.80 (useful but needs threshold tuning per policy domain)
  HARD-FAIL: F1 < 0.50 (policy entry embeddings too close to compliant outputs; requires domain-specific encoder tuning)

### Anchor 5: verify_conformal_coverage_v1

Anchor pointer: Research note Section "Prediction 5" + "L5: Conformal coverage"
Substrate-product reading: Uses substrate retrieval score as conformal non-conformity measure on a 200-item calibration set. Measures prediction set size at 90% nominal coverage and compares to token-entropy baseline. This is the most speculative anchor; no published direct precedent.
Tier hint: CPU laptop, ~3-4 hr including calibration set construction. Lower priority than Anchors 1-3.
Why-now: If prediction sets are meaningfully smaller than token-entropy baseline, this is a publishable-quality product claim (provable coverage guarantee tighter than LLM internal uncertainty). File as a follow-on after Anchor 1 validates the cosine confidence signal.

Pre-reg bands:
  HARD-PASS: Substrate-based conformal prediction sets 20%+ smaller than token-entropy sets at 90% coverage
  MIDDLE-BAND: 5-20% smaller (marginal advantage; combine with token entropy as ensemble)
  HARD-FAIL: No size advantage (substrate retrieval score not a better non-conformity measure)

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_verification_hallucination_2x_2026-06-08.md
- Cycle 175 empirical results context: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- ZKL realkey rescue handoff (encoder correlation prerequisite): d:/AI/hd-instrument/notes/exp_dev_handoff_research_zkl_realkey_rescue_3x_2026-06-07.md
- Production architecture memory: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- v1 demo brief: d:/AI/hd-instrument/notes/testbed_post_compaction_brief_2026-06-08_v1_demo_audit_week.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: Anchor 1 (verify_span_factcheck_v1) MUST run before Anchor 5 (verify_conformal_coverage_v1). Anchor 1 validates the cosine confidence signal that Anchor 5 builds on.

PARALLEL: Anchors 1, 2, and 3 can run in parallel if queue depth permits. All are CPU-only.

PREREQUISITE NOTE: Anchors 1 and 2 may benefit from running after zkl_encoder_correlation_analysis_v1 (from ZKL realkey rescue handoff) confirms that real-key cosine distances behave as expected. If that anchor has not yet run, treat its result as a prerequisite for threshold-setting.

GATING: If Anchor 2 returns HARD-FAIL (immune system sensitivity < 0.50), re-route hallucination detection to cosine-threshold-only (Anchor 1 path) and do not pursue immune-system-based adversarial detection.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing KB construction method, claim generation method, and parameter values
- Choosing local CPU vs remote CPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Writing experiment scripts per feedback_metrics_required_fields_write_metrics.md convention

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Making customer-facing claim revisions from verification results (orchestrator owns after verdicts are in)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
- Interpreting EU AI Act compliance status (orchestrator + user decision from empirical results)
