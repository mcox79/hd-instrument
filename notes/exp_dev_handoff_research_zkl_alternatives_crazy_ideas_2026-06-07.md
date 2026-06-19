# exp_dev hand-off -- research: ZKL alternatives and crazy ideas

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_zkl_alternatives_crazy_ideas_3x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Linear mitigations on the shared Llama-3.2-1B L15 encoder are empirically bounded at
ZKL(50) ~0.22. Five pre-reg pre-tests (T1-T5) are designed to determine whether any
nonlinear mitigation path can reach ZKL <= 0.10. The tests are ordered by prerequisite:
T1 and T2 are independent; T5 requires T1 and T2 to pass or mid-band first.

All tests are CPU-only, estimated 20-60 min wall time each. No cloud dispatch needed for
pre-tests. If T5 HARD-PASS is achieved, a follow-up production-scale anchor should be
queued (GPU, Llama full-scale, 500-fact probe + larger N).

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. T1 -- INLP linearity check (HIGHEST PRIORITY)

Anchor pointer: ZKL-INLP-T1 (new; not yet queued)
Substrate-product reading: Determines whether the membership-inference signal in Llama L15
  embeddings is linearly accessible. If yes, INLP nullspace projection is the cheapest
  path to ZKL improvement. If no (nonlinear manifold), INLP is blocked and the
  combination path cannot achieve ZKL <= 0.10 without encoder modification.
Tier hint: CPU laptop; ~20-30 min wall; uses existing embedding diagnostic data
Why-now: Gate for all downstream shared-encoder paths. Cheapest pre-test; runs first.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: AUROC <= 0.52 after <= 5 INLP iterations AND cosine recall@10 >= 0.80
  HARD-FAIL: AUROC >= 0.60 after 10 INLP iterations (signal nonlinear, path blocked)
             OR recall@10 < 0.65 at AUROC <= 0.55 (utility-privacy tradeoff too tight)
  MID-BAND: AUROC <= 0.55 after 5-10 iterations with recall@10 in [0.65, 0.80]

Inputs required: Llama L15 member/non-member cosine score data (from existing privacy
  harness; the 500-fact probe set). No new embedding runs needed for this pre-test.
  If existing data is insufficient, generate 200 member/non-member query pairs from
  the privacy harness probe set.

### 2. T2 -- Stochastic top-k (exponential mechanism) epsilon sweep (INDEPENDENT OF T1)

Anchor pointer: ZKL-STOCHK-T2 (new; not yet queued)
Substrate-product reading: Maps the utility-privacy tradeoff for the exponential
  mechanism at retrieval output. Determines whether calibrated stochastic sampling of
  top-k results can contribute ZKL reduction as a compound layer alongside INLP.
Tier hint: CPU laptop; ~30-45 min wall; uses 500-fact probe set
Why-now: Independent of T1; can run in parallel. If T2 fails, the combination path
  (T5) is unlikely to reach 0.10.

Pre-reg bands:
  HARD-PASS: Some epsilon in [0.3, 2.0] achieves ZKL(50) <= 0.15 AND recall@10 >= 0.80
  HARD-FAIL: No epsilon achieves ZKL(50) <= 0.15 without recall@10 < 0.70
  MID-BAND: ZKL(50) in [0.15, 0.18] at recall@10 >= 0.80 at some epsilon

Sweep: epsilon in [0.3, 0.5, 1.0, 2.0, 5.0]; report ZKL(50) and recall@10 at each.
Mechanism: exponential mechanism p(doc_i) proportional to exp(epsilon * score_i / 2).
  Sample 1 result per query rather than taking argmax. Repeat 50 times per query for
  ZKL(50) estimate.

### 3. T3 -- VIB sigma sweep (degenerate bottleneck, no training)

Anchor pointer: ZKL-VIB-T3 (new; not yet queued)
Substrate-product reading: Maps the utility-privacy tradeoff for additive Gaussian noise
  in the embedding space. This is a proxy for the full VIB learning outcome: if additive
  noise cannot find a viable operating point, trained VIB will not either.
Tier hint: CPU laptop; ~20-30 min wall; uses 500-fact probe set
Why-now: Independent of T1 and T2. If T3 shows a viable sigma operating point, VIB
  (Candidate 1B) is worth the 2-3 week engineering investment.

Pre-reg bands:
  HARD-PASS: Some sigma in [0.01, 0.60] achieves ZKL(50) <= 0.12 AND recall@10 >= 0.80
  HARD-FAIL: No sigma achieves ZKL(50) < 0.16 without recall@10 < 0.70
  MID-BAND: ZKL(50) in [0.12, 0.16] at recall@10 >= 0.80 at best sigma

Sweep: sigma in [0.01, 0.05, 0.10, 0.20, 0.30, 0.60]; add N(0, sigma^2 * I) to
  Llama L15 embeddings before storage and query. Measure ZKL(50) and recall@10.

### 4. T4 -- Adversarial GRL pre-test on Pythia-160M

Anchor pointer: ZKL-GRL-T4 (new; not yet queued)
Substrate-product reading: Tests whether gradient reversal layer (GRL) adversarial
  fine-tuning suppresses ZKL on a small proxy encoder (Pythia-160M). If ZKL drops on
  Pythia, GRL is credible at Llama scale (3-5 week investment justified). If ZKL is
  unchanged on Pythia, the utility-leakage entanglement is structural and GRL will fail
  at all scales.
Tier hint: CPU laptop; ~30-60 min wall for 200 GRL gradient steps on Pythia-160M
Why-now: Blocks 3-5 week Llama-scale GRL training. Cheapest gate for the most
  expensive engineering path.

Pre-reg bands:
  HARD-PASS: ZKL(50) drops >= 0.08 from Pythia baseline after GRL, AND recall@10 >= 0.75
  HARD-FAIL: ZKL(50) unchanged or increases after GRL, OR recall@10 < 0.60
  MID-BAND: ZKL drops >= 0.04 at recall@10 >= 0.75 (marginal; needs Llama-scale test)

Inputs required: Pythia-160M checkpoint (HuggingFace); member/non-member pair dataset
  from privacy harness. GRL implementation: 2-layer MLP classifier head + gradient
  reversal at encoder output. Loss = L_retrieval - lambda * L_member_classifier.
  Sweep lambda in [0.1, 0.5, 1.0] and report best result.

### 5. T5 -- Combination test (INLP + stochastic top-k)

Anchor pointer: ZKL-COMBO-T5 (new; not yet queued)
Substrate-product reading: The primary shared-encoder HIPAA-absolute gate. If this passes,
  the combination of INLP nullspace projection and stochastic top-k achieves ZKL <= 0.10
  at recall >= 0.78 on the shared encoder without per-customer cost. This would upgrade
  the shared-encoder tier from "qualified" to "HIPAA-absolute" and eliminate the
  premium-tier-only constraint for HIPAA compliance.
Tier hint: CPU laptop; ~30-45 min wall
Why-now: Prerequisite: T1 HARD-PASS and T2 HARD-PASS or MID-BAND.
         Do NOT dispatch T5 if T1 HARD-FAILs.

Pre-reg bands:
  HARD-PASS: ZKL(50) <= 0.10 AND recall@10 >= 0.78 (HIPAA-absolute shared encoder)
  HARD-FAIL: ZKL(50) >= 0.14 OR recall@10 < 0.70 (qualified posture is structural ceiling)
  MID-BAND: ZKL(50) in [0.10, 0.14] with recall@10 >= 0.78 (widen INLP sweep before
            declaring ceiling; do not immediately declare hard fail)

Setup: Apply INLP nullspace projection with best k from T1 to Llama L15 embeddings.
  Apply exponential mechanism with best epsilon from T2 at query time. Measure ZKL(50)
  and recall@10 on 500-fact probe set.

If T5 HARD-PASS: write strategy note recommending shared-encoder tier upgrade and
  queue a production-scale validation anchor (GPU, BGE-large encoder, N=10000+ facts).

---

## Strategic context for exp_dev

The qualified posture (ZKL ~0.22) is locked until T5 passes. Do not reframe the
shared-encoder as HIPAA-absolute based on T1 or T2 alone. Only T5 HARD-PASS with both
ZKL <= 0.10 AND recall >= 0.78 justifies the upgrade.

Test dispatch priority: T1 and T2 in parallel (independent); T3 in parallel or after;
T4 after T1/T2 results are known; T5 only if T1 HARD-PASS and T2 pass/mid-band.

If T1 HARD-FAIL: the linear signal is not suppressible without encoder modification.
  The path to shared-encoder ZKL <= 0.10 requires GRL (T4 scale-up) or VIB (T3-guided).
  Path D premium tier is the structural ceiling until GRL/VIB is implemented and tested.

If T5 HARD-FAIL after T1+T2 pass: the combination provides no meaningful additive
  benefit. Qualified posture + Path D is confirmed as structural ceiling. Do not invest
  further in shared-encoder ZKL reduction without new mechanism discovery.

---

## Context pointers

- Research note (full analysis):
  d:/AI/hd-instrument/notes/research_drill_zkl_alternatives_crazy_ideas_3x_2026-06-07.md
- Prior privacy mechanism analysis:
  d:/AI/hd-instrument/notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
- Prior Llama privacy reopening:
  d:/AI/hd-instrument/notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Substrate cap_map (privacy rows):
  d:/AI/hd-instrument/data/substrate_capability_map.md
- Privacy harness data (member/non-member probe set):
  Look in data/exp_*/metrics.json for ZKL privacy harness runs; use the 500-fact probe set.

---

## Contract section

This hand-off is research-to-experiment. The 5 pre-test specs (T1-T5) are provided as
pre-reg recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs)
- Implementing the test scripts (INLP, exponential mechanism, VIB noise, GRL stub)
- Assigning to correct queue (all T1-T5 are CPU laptop tier)
- Writing verdict notes for each test per standard protocol
- Escalating T5 HARD-PASS to orchestrator for cap_map update and tier decision

## Autonomy declaration

Exp_dev may dispatch T1, T2, T3, T4 independently without orchestrator approval (all
are CPU pre-tests, low cost, low risk). T5 requires T1 HARD-PASS first. A T5 HARD-PASS
that would trigger a shared-encoder tier upgrade MUST be escalated to orchestrator before
any product-tier or compliance documentation is changed.
