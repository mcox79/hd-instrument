# exp_dev hand-off -- research: Modern Hopfield Networks / Energy-Based Memory 5x Deep Drill

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_field_modern_hopfield_5x_2026-06-07.md
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

Modern Hopfield network field lit-scan completed 2026-06-07. Core findings:

1. Lucibello-Mezard 2024 (PhysRevLett) provides exact capacity threshold: P_max = 2^(alpha_c * N)
   with alpha_c ~ 0.693 for bipolar patterns. At N=4096, P_max ~ 2^2836. Substrate at
   P=10^6 = 2^20 operates at 0.7% of theoretical capacity ceiling.

2. NeurIPS 2024 spherical-code result: substrate's PCA whitening IS the spherical code
   optimality condition. Whitening spreads stored patterns optimally on the unit sphere.
   This is why whitening universally improves recall.

3. Ramsauer 2020: substrate's retrieval formula (softmax(beta * Xi^T q) * Xi) is exactly
   transformer self-attention. Substrate is a persistent-memory analog of transformer KV-attention.

4. Sparse Hopfield (arXiv 2402.13725, Hu et al. 2023): replacing softmax with sparsemax
   (top-k) yields TIGHTER retrieval error bounds than dense and reduces compute by O(P/k).

5. Synaptic noise study (PhysRevE 2025): capacity scaling N^(n-1) survives quantization
   noise; prefactor reduced but not structurally broken.

These findings are actionable as 4 near-term experiments (all CPU or existing GPU).

---

## Anchor Candidates (rank-ordered by P_actionable x cost x urgency)

### 1. HOPFIELD-PHASE-MAP -- Phase-Transition Operating Point Sweep (HIGHEST PRIORITY)

Anchor pointer: HOPFIELD-PHASE-MAP (new; not yet queued)
Substrate-product reading: Maps recall@1 across a grid of (N, P) combinations. Identifies
  the empirical cliff location and compares to Lucibello-Mezard prediction P_cliff = 2^(alpha_c * N).
  If cliff matches theory, the customer-facing safety margin claim ("substrate at <1% of
  capacity ceiling") becomes auditable and specific. If cliff is below prediction, the
  theoretical backing needs recalibration.
Tier hint: CPU or existing GPU runner; no cloud needed; ~2-4 hours wall
Why-now: The safety margin claim is the strongest single quantitative customer pitch
  upgrade from this research drill. One experiment makes it auditable.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: Empirical cliff at P > 2^(0.5 * N) for all N in [1024, 4096, 16384]
             AND current operating point (N=4096, P=10^6) has recall@1 >= 0.98
  HARD-FAIL: Cliff at P < 2^(0.3 * N) at any N >= 4096
             OR recall@1 < 0.90 at current operating point (N=4096, P=10^6, noise=15%)
  MID-BAND:  Cliff at 2^(0.3*N) < P < 2^(0.5*N); safety margin confirmed but smaller
             than Lucibello-Mezard predicts

Sweep grid: N in [1024, 2048, 4096, 8192]; P in [10^3, 10^4, 10^5, 10^6]; noise = 15%.
Measure: recall@1 at each (N, P) grid point. Stop increasing P when recall@1 < 0.90.
Use existing substrate code; no new implementation required.

### 2. HOPFIELD-SPARSE-K -- Sparse Retrieval (sparsemax top-k) Eval

Anchor pointer: HOPFIELD-SPARSE-K (new; not yet queued)
Substrate-product reading: Replaces softmax cleanup with top-k sparsemax at k in [5, 10, 20, 50].
  Tests whether sparse Hopfield error bounds (Hu et al. 2023) hold in practice: recall@10
  should be maintained or improved at k >= 20 while compute cost drops by O(P/k).
  If recall@10 >= 0.95 at k=20, sparse retrieval is viable for edge deployment.
Tier hint: CPU laptop or remote CPU; ~1-2 hours wall; no cloud
Why-now: Edge deployment moat is a near-term product priority. Sparse retrieval is the
  key enabling mechanism. This pre-test gates the engineering investment.

Pre-reg bands:
  HARD-PASS: recall@10 >= 0.95 at k=20 AND recall@10 >= 0.92 at k=10
             (sparse retrieval viable; proceed to edge deployment engineering)
  HARD-FAIL: recall@10 < 0.80 at k=50 (dense retrieval required; sparse not viable)
  MID-BAND:  recall@10 in [0.80, 0.95] at k=20 (viable but with tradeoff; widen k sweep)

Sweep: k in [5, 10, 20, 50, 100]; N=4096; P=10^6; noise=15%.
Mechanism: for each query, compute all P dot-products, then zero-out all but top-k
  before softmax normalization. Compare recall@10 vs dense baseline.

### 3. HOPFIELD-BETA-SWEEP -- Finite-Beta Soft Retrieval + Uncertainty Output

Anchor pointer: HOPFIELD-BETA-SWEEP (new; not yet queued)
Substrate-product reading: Tests whether finite-beta retrieval (replacing hard argmax with
  softmax at beta in [0.5, 50]) enables calibrated uncertainty output. At finite beta,
  retrieval output is a posterior over stored patterns. Entropy of this distribution should
  predict retrieval difficulty (hard queries = high entropy; easy queries = low entropy).
  If entropy-recall correlation holds (r >= 0.60), this is a deployable uncertainty signal.
Tier hint: CPU; ~1-2 hours wall; no cloud
Why-now: Enterprise customers (medical, legal, compliance) need calibrated confidence on
  retrieved facts. This is the cheapest path to an uncertainty quantification feature.

Pre-reg bands:
  HARD-PASS: recall@1 >= 0.95 at some beta in [5, 50] AND Pearson r(entropy, 1-recall)
             >= 0.60 on held-out query set (uncertainty is informative)
  HARD-FAIL: No beta achieves recall@1 >= 0.90 OR r(entropy, 1-recall) < 0.30 (entropy
             is uninformative; uncertainty output not viable without calibration training)
  MID-BAND:  recall@1 >= 0.90 at best beta but r < 0.60 (recall viable; uncertainty
             output requires calibration post-processing)

Sweep: beta in [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]; N=4096; P=10^5 (smaller P
  for faster sweep; scale-up sweep after if HARD-PASS at P=10^5).

### 4. HOPFIELD-QUANT -- Quantization Noise Tolerance (int8 / int4 storage)

Anchor pointer: HOPFIELD-QUANT (new; not yet queued)
Substrate-product reading: Tests whether stored pattern matrix Xi can be quantized to
  int8 or int4 without meaningful recall degradation. Bhattacharjee-Martin 2025 predicts
  capacity prefactor reduces with noise but N^(n-1) scaling holds. At int8 (4-bit
  effective noise), recall should remain above 0.93 if the whitening ensures patterns
  are near the center of the quantization range.
Tier hint: CPU laptop; ~1 hour wall; no cloud
Why-now: 4x memory reduction (float32 -> int8) directly reduces VRAM cost. This is a
  pure engineering win if recall holds. Pre-test before investing in quantized storage path.

Pre-reg bands:
  HARD-PASS: recall@10 >= 0.93 at int8 quantization AND >= 0.85 at int4 quantization
             (quantized storage viable; proceed to engineering)
  HARD-FAIL: recall@10 < 0.80 at int8 quantization (quantization breaks retrieval;
             float32 storage required)
  MID-BAND:  recall@10 in [0.80, 0.93] at int8; borderline viable; test with larger N

Mechanism: quantize Xi to int8/int4 at storage time using uniform symmetric quantization.
  Run standard recall@10 evaluation at N=4096, P=10^5, noise=15%.

---

## Dispatch priority and prerequisites

Independent (can run in parallel): HOPFIELD-PHASE-MAP and HOPFIELD-SPARSE-K and HOPFIELD-QUANT
  (no prerequisites; all CPU; all use existing code with small modifications)

Prerequisite chain: HOPFIELD-BETA-SWEEP should run after HOPFIELD-PHASE-MAP confirms
  operating point stability (to set correct N and P for the beta sweep).

All 4 are CPU-only, estimated total wall time <= 8 hours, no cloud dispatch needed.

---

## Strategic escalation gates

HOPFIELD-PHASE-MAP HARD-PASS: write a strategy note confirming the safety margin claim
  is auditable; orchestrator should add this to customer pitch materials and cap_map.

HOPFIELD-SPARSE-K HARD-PASS: escalate to orchestrator; triggers edge deployment
  engineering authorization (2-3 week implementation of sparse retrieval module).

HOPFIELD-BETA-SWEEP HARD-PASS with r >= 0.60: escalate to orchestrator; triggers
  uncertainty quantification feature design for enterprise tier.

Any HARD-FAIL: write a brief verdict note explaining which theoretical prediction failed;
  do NOT immediately propose a rescue without referencing the research note for alternatives.

---

## Context pointers

- Research note (full analysis with all 13 sections + 16 citations):
  d:/AI/hd-instrument/notes/research_drill_field_modern_hopfield_5x_2026-06-07.md
- Substrate capability map (Hopfield capacity rows):
  d:/AI/hd-instrument/data/substrate_capability_map.md
- Prior VSA/HRR drill (complementary field, dual framework):
  d:/AI/hd-instrument/notes/ (search: research_drill_field_vsa_hrr_*)
- Cycle 155 capacity confirmation:
  d:/AI/hd-instrument/data/ (search: exp_*/metrics.json for cycle 155 HP anchor)
- Cycle 171 1M-fact recall validation:
  d:/AI/hd-instrument/data/ (search: exp_*/metrics.json for cycle 171 anchor)

---

## Contract section

This hand-off is research-to-experiment. The 4 anchor specs are provided as pre-reg
recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs from
  cycle 171 recall@10 baseline)
- Implementing the minimal code changes needed (sparsemax, beta sweep, quantization noise
  injection -- all are small modifications to existing recall evaluation harness)
- Assigning to correct queue (all are CPU tier; HOPFIELD-QUANT and HOPFIELD-SPARSE-K
  could run on remote CPU runner for speed)
- Writing verdict notes per standard protocol
- Escalating any HARD-PASS that triggers a product-tier or customer-pitch change to
  orchestrator before acting on it

## Autonomy declaration

Exp_dev may dispatch all 4 anchors without orchestrator approval (all are CPU pre-tests,
low cost, no cloud). Any result that would change the customer pitch wording, upgrade
a cap_map row, or trigger edge-deployment engineering authorization MUST be escalated
to orchestrator before downstream action.
