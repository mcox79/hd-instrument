# Research: Cap 2 self-monitoring confidence rehab (post v160 STRUCTURAL CLOSURE)

**Date**: 2026-05-23 (Research cycle response to Strategy v160 closure routing file)
**Trigger**: `wave14_cap2_confidence_margin_probe_v1` FULL = `CAP2_MARGIN_KILL` + prior v153 `CRITICAL_NO_CORRELATION`. Two independent metric framings of Cap 2 (tau, margin) both HARD-FAIL.
**Routing file**: `notes/strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md`
**Anchors**: [[feedback-rehabilitation-after-rejection]] [[feedback-lit-scan-calibration-penalty]] [[feedback-dont-overextend-theorems]] [[feedback-dont-dismiss-adjacent-methods]] [[feedback-no-smoke]] [[feedback-no-papers-product-only]] [[feedback-query-privacy-decomposition]]

---

## (a) HEADLINE

**Top pick: Rescue 5 (Gap C subsumption) — but with a hard caveat.** If the original Cap 2 product spec is *hardware-side abstain pre-readout*, Gap C does NOT cover it and Rescue 1 (endpoint-id + PLCP-style conditional conformal) becomes the live experimental path. **Recommend executing Rescue 5 audit FIRST (2 hours strategy work, zero experiment cost), THEN Rescue 1 if and only if Gap C audit reveals a residual gap.**

Calibrated rescue ranking (deflated per [[feedback-lit-scan-calibration-penalty]]; uncharted regime penalty 0.15-0.25; novel-synthesis cap 0.50):

| # | Rescue | Raw P | Deflated P | Cost | Verdict |
|---|---|---|---|---|---|
| 5 | Re-axiomatize as Gap C subsumption | 0.70 | **0.55** (cap held above 0.50 because the lit-mechanism — downstream conformal — is published and Gap C is FULL-validated; this is not novel synthesis but established practice) | 2 h audit | **DO FIRST** |
| 1 | Endpoint-ID + conditional conformal (PLCP-anchored) | 0.55 | **0.35** | ~10 min CPU + ~150 LOC | DO SECOND if Rescue 5 surfaces a gap |
| 2 | VAMP-on-chain posterior variance | 0.40 | **0.20** | ~15 min CPU + ~80 LOC | Hold |
| 3 | chi_4 dynamic susceptibility per-query | 0.35 | **0.15** | ~20 min CPU + ~100 LOC | Hold — per-query single-trajectory chi_4 is methodologically fraught |
| 4 | Kovacs hysteresis per-query | 0.30 | **0.12** | ~25 min CPU + ~120 LOC | Hold — Kovacs is intrinsically ensemble; per-query estimation expensive AND noisy |
| 6 (NEW) | Trust-Score / kNN-density confidence in endpoint-id basin | 0.50 | **0.30** | ~10 min CPU + ~100 LOC | Optional add-on combined with Rescue 1 |

The 6th rescue surfaced from lit: **Jiang et al. Trust Scores** (a published method for distribution-free classification confidence using kNN density to nearest-class point, which is *exactly* the natural extension of the 28-element endpoint partition: per-query confidence = density-of-nearest-correct-endpoint / density-of-nearest-other-endpoint). Strategy didn't sketch this — it slots in as a strict refinement of Rescue 1.

---

## (b) Cheap decisive test (Rescue 5, before any experiment)

**Audit protocol** (2 h, no compute):

1. Pull the original Cap 2 product-spec text from `notes/substrate_capability_map.md` and any locked spec docs (cycle 100-153 narrative).
2. Identify the answer to: **"Does the customer-facing self-monitoring claim require a hardware/substrate-side abstain decision BEFORE readout, or is a downstream calibrated-confidence wrapper sufficient?"**
3. Pull Gap C cycle 173 v153 `CONFORMAL_COVERED` FULL verdict scope: ECE, coverage, abstain semantics, per-query granularity.
4. Side-by-side: Does Gap C's deliverable cover Cap 2's promise?

**Decision rule**:
- If YES (Gap C covers): Cap 2 closure becomes **FINAL** (bare ❌, not PROVISIONAL). Portfolio honestly drops 12 → 11. No experiments. **THIS IS THE LIKELY OUTCOME** based on the v158 Cap 1 precedent — Strategy already foresaw it.
- If NO (Gap C misses substrate-intrinsic pre-readout abstain): Route to Rescue 1 (endpoint-id) as the live experiment.

**Why this is decisive**: It is a documentation audit, not a measurement. Either the spec covers it or it doesn't. No statistical inference required.

---

## (b') Cheap decisive test (Rescue 1, conditional on Rescue 5 surfacing a gap)

**Experimental protocol** (~10 min CPU, ~150 LOC):

1. Reuse cycle 137 + v149/v153 endpoint-detection code to tag each of the existing FULL retrieval traces (the same trace set used in v153 and v160) with its 1-of-28 endpoint cluster.
2. Compute `p(correct | endpoint_k)` empirically on a held-out calibration split (50/50).
3. Wrap with **conformal prediction**, specifically a Mondrian / class-conditional conformal scheme using endpoint-id as the partition (this maps directly onto PLCP — Partition Learning Conformal Prediction; the substrate's 28-element partition IS the partition variable).
4. Score on the test split.

**Optional Rescue 6 augment**: add Trust-Score-style kNN-density signal *within* each endpoint basin (density-to-nearest-correct vs density-to-nearest-other) and check if it composes additively in AUC.

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL

### Rescue 5 (Gap C subsumption audit)

- **HARD PASS**: Gap C's documented scope explicitly covers (i) per-query confidence value, (ii) abstain decision, (iii) ECE <= 0.10 calibration, (iv) post-readout deployment context. → Cap 2 closure is FINAL.
- **HARD FAIL**: Gap C documentation is silent on or explicitly excludes any of: (i) pre-readout substrate-side abstain, (ii) per-query (not just per-batch) confidence, (iii) substrate-internal calibration source. → Rescue 1 escalates.

### Rescue 1 (endpoint-id + conditional conformal)

- **HARD PASS** (all three required):
  - ROC AUC(correct vs incorrect | endpoint partition) >= 0.65 in at least 3/4 noise strata (p in {0, 0.05, 0.10, 0.20}), 200 queries per stratum × 3 seeds.
  - ECE <= 0.10 after Mondrian/PLCP conformal wrap.
  - **Substrate-novel contribution check**: ablation control (replace substrate with random classifier → recompute pipeline). Endpoint-id AUC must beat random-classifier-baseline by >= 0.10 AUC. If endpoint-id AUC == random-baseline AUC, the signal is data-side, not substrate-side, and Cap 2 still closes.
- **HARD FAIL** (any one triggers closure):
  - ROC AUC < 0.55 in 3/4 strata (no signal).
  - ECE > 0.15 after conformal wrap (uncalibratable).
  - Substrate-ablation check fails (the substrate adds no information over a random classifier on the same partition).

### Rescue 2 (VAMP posterior variance) — IF escalated

- **HARD PASS**: `corr(-log sigma^2, correct)` >= 0.40 in 2/4 strata AND Cohen's d >= 0.5 AND ECE <= 0.10 post-conformal.
- **HARD FAIL**: `corr` < 0.20 in all strata (mirrors the v160 margin failure) OR Cohen's d < 0.2 (variance distributions overlap).

### Rescue 3 (chi_4 per-query) — IF escalated

- **HARD PASS**: per-query chi_4 estimate (5-ref-batch) yields `corr(-peak_chi_4, correct)` >= 0.35 (deflated from sketch's 0.40 because lit says single-trajectory chi_4 is statistically marginal) in 2/4 strata; Cohen's d >= 0.4.
- **HARD FAIL**: per-query chi_4 estimator variance dominates inter-query signal (Cohen's d < 0.2) — the predicted failure mode per lit.

### Rescue 4 (Kovacs per-query) — IF escalated

- **HARD PASS**: per-query Kovacs hump amplitude (single perturbation pulse) yields `corr(-A_Kovacs, correct)` >= 0.35 in 2/4 strata; Cohen's d >= 0.4.
- **HARD FAIL**: single-pulse Kovacs amplitude variance dominates inter-query signal — the predicted failure mode per lit (Kovacs is intrinsically a probability-distribution quantity).

### Rescue 6 (Trust Score / kNN-density on endpoint basin)

- **HARD PASS** (compositional with Rescue 1): adding Trust-Score signal lifts AUC by >= 0.05 over endpoint-id-alone AND maintains ECE <= 0.10.
- **HARD FAIL**: Trust-Score signal correlates >0.9 with endpoint-id (redundant) OR adds < 0.02 AUC (no new information).

---

## (d) Cross-thread synthesis

### Why Rescue 5 ranks highest despite "doing nothing"

1. **v158 Cap 1 precedent is directly analogous**. Cap 1's clean-only Crooks-FT framing was re-axiomatized to a tiered Sagawa-Ueda SLA — same capability, different formal envelope, no substrate change. The v160 closure-then-subsumption move is literally the same template applied to Cap 2: when the substrate-intrinsic measurement fails, ask whether a downstream calibrator (Gap C, FULL-validated cycle 173) already delivers the customer-facing capability.
2. **Lit confirms downstream conformal is the modern best practice**. Conformal prediction provides distribution-free finite-sample frequentist coverage without requiring the underlying model to be well-specified — Gap C already delivers this; trying to bolt substrate-intrinsic confidence ON TOP is a category error if the downstream wrapper suffices.
3. **Zero compute cost**. Audit is documentation work. If it lands, the portfolio update is honest (12 → 11) and the closure is FINAL, freeing CPU/GPU for Cap 6/Bet Y/Bet Z queues.

### Why Rescue 1 ranks second

1. **Substrate-novel structural finding survives FULL**. The 28-element endpoint partition is a v149/v152/v153 FULL-validated structural fact (cycle 152 PQ_DISCRETE_OTHER 15 peaks; cycle 150 ORDER_PARAM_SUB_REGION_STABLE). Margin and tau collapse trajectory information to scalars; endpoint-id preserves it. This is *exactly* the [[feedback-dont-dismiss-adjacent-methods]] case — Strategy correctly identified it.
2. **Modern lit anchor exists**. **Partition Learning Conformal Prediction (PLCP)** is a published 2024 method for using learned partitions as the conditioning variable in conformal prediction — the 28-element substrate endpoint partition IS the partition variable. The mapping is clean. Cited: PLCP — arxiv 2404.17487.
3. **Cheap and decisive**. Reuses existing FULL trace data + existing endpoint-detection code. ~10 min CPU.
4. **Built-in substrate-novelty audit**. The ablation control (random-classifier-on-same-partition baseline) directly answers the question "does substrate add info over data-only signal?" — if not, we kill it cleanly.

### Why Rescue 2-4 deflate hardest

- **Rescue 2 (VAMP variance)**: Lit confirms VAMP/AMP posterior variance is calibrated for Gaussian noise; substrate's bit-flip noise is non-Gaussian. "Sharp theoretical results on uncertainty quantification in high-dimensional models where posterior distributions are not Gaussian are consequently scarce." The empirical re-scaling that would be needed defeats the "native Bayesian quantity" appeal. P deflated 0.20.
- **Rescue 3 (per-query chi_4)**: Chi_4 is fundamentally a BATCH / ensemble variance. Lit (Brownian beads paper, arxiv 1904.01865; supercooled lit) explicitly notes that single-trajectory chi_4 estimates are "not always statistically meaningful." The predicted failure mode (per-query noise dominates inter-query signal) is the typical outcome in this literature. P deflated 0.15.
- **Rescue 4 (per-query Kovacs)**: Kovacs hump is INTRINSICALLY a probability-distribution quantity ("its description requires to deal not only with averages but with a full probability distribution of domain sizes or relaxation times"). Single-pulse single-query estimation has the same problem as Rescue 3, worse, because it requires perturbation calibration too. P deflated 0.12.

### Why Rescue 6 (NEW) is worth flagging

**Trust Scores** (Jiang et al, NeurIPS 2018; surfaced via the PLCP search) provide a published distribution-free classification confidence score = ratio of distance-to-nearest-class point vs distance-to-nearest-other-class point. The endpoint-id partition gives a natural "nearest-correct-endpoint" definition. This is the cleanest published refinement of Rescue 1 — strict composition: Rescue 1 gives the partition; Rescue 6 gives a within-partition confidence score. Cited in lit as "Conformal Prediction Sets with Improved Conditional Coverage using Trust Scores" — arxiv 2501.10139.

### Calibration penalty audit

Per [[feedback-lit-scan-calibration-penalty]], all P estimates above are deflated. Notably:
- Rescue 5 is NOT subject to the novel-synthesis cap because it uses two published mechanisms (Gap C conformal, FULL-validated; Sagawa-Ueda axiomatization, validated v158) — not a novel synthesis. P=0.55 is justified above the 0.50 cap.
- Rescues 1, 6 are novel-synthesis (substrate-novel 28-element partition × published PLCP/Trust Score conformal) — capped at 0.50, then deflated by lit-uncharted penalty to 0.35 / 0.30.
- Rescues 2-4 are deflated hardest (0.20 / 0.15 / 0.12) because lit explicitly predicts the dominant failure mode for each.

---

## (e) Substrate-product implications

### If Rescue 5 lands (likely outcome)

**Cap 2 returns to portfolio: NO. Closure becomes FINAL.**

- Portfolio honestly updates 12 → 11 demonstrated capabilities. This is NOT a regression — it is acknowledging that Cap 2 was never an independent axis from Gap C.
- Customer-facing self-monitoring claim still works, delivered by Gap C conformal wrapper.
- Product story: "calibrated abstain decision via downstream conformal prediction on substrate readout." Cleaner story, fewer moving parts.
- Frees CPU/GPU queue for higher-leverage probes (Cap 6, Bet Y, Bet Z).
- Aligns with [[feedback-no-smoke]] and [[feedback-no-papers-product-only]]: honest accounting, product-relevant.

### If Rescue 5 surfaces a gap → Rescue 1 lands

**Cap 2 returns to portfolio: YES, but in REFINED form.**

- New form: "per-query confidence via endpoint-id-conditioned conformal calibration (Mondrian/PLCP-anchored)."
- Substrate-novel contribution: the 28-element endpoint partition is the partition variable, validated by lit-anchored PLCP framework.
- Audit-ready: built-in ablation against random-classifier-on-same-partition baseline ensures substrate contribution is genuine.
- AI memory subsystem mapping: per-query confidence enables fine-grained provenance + abstain at the memory-retrieval interface (one of the 4 capability classes per [[project-ai-memory-subsystem-direction]]).
- Customer story: "substrate-internal trajectory landmarks provide per-query confidence beyond what downstream calibration alone can deliver."

### If Rescue 5 surfaces a gap AND Rescue 1 fails

**Cap 2 returns to portfolio: NO. Closure becomes FINAL with detailed scope.**

- Rescues 2-4 not worth pursuing given their deflated P (< 0.20). Their failure mode is predicted by lit.
- Honest scope of closure: "substrate does not carry per-query confidence signal in margin, tau, endpoint-id, OR (predicted) VAMP-variance/chi_4/Kovacs framings." Closes the broad axis.
- Triggers a portfolio-level review: are there other capabilities the substrate IS uniquely positioned to deliver vs downstream calibrators? Cross-application probe per [[feedback-strategy-shore-up-capabilities]].

### Materials/spin-glass framing (per [[feedback-materials-science-probe]])

The 28-element endpoint partition is the substrate's equivalent of a metastable basin landscape in a spin glass. Per-query "which basin did we land in" is a *trajectory* observable, not a local-step observable — and the v150 RS-cert anchor confirms the substrate has the right glass-class structure. Rescue 1 is the spin-glass-native confidence framing; Rescues 3-4 (chi_4, Kovacs) are also spin-glass-native but suffer the per-query estimation problem. This is consistent with the Ising-spin / BSC mapping: per-spin-config landing basin is well-defined; per-spin-config dynamical heterogeneity is intrinsically noisy.

---

## (f) Verified citations

1. **Partition Learning Conformal Prediction (PLCP)** — arxiv 2404.17487. "Conformal Prediction with Learned Features." Establishes that learned partitions improve conditional coverage of conformal prediction. *Direct anchor for Rescue 1.*
2. **Trust Scores** — arxiv 2501.10139. "Conformal Prediction Sets with Improved Conditional Coverage using Trust Scores." Distribution-free per-instance confidence via kNN density ratios. *Direct anchor for Rescue 6 (NEW).*
3. **Conformal Bayesian Computation** — arxiv 2106.06137. Establishes that downstream conformal wrappers calibrate misspecified Bayesian posteriors. *Anchor for Rescue 5 (Gap C subsumption).*
4. **Theoretical characterization of uncertainty in high-dimensional linear classification** — arxiv 2202.03295 / IOPscience 10.1088/2632-2153/acd749. VAMP posterior marginal calibration is Gaussian-prior-dependent; high-dim non-Gaussian is open. *Predicts Rescue 2 failure mode.*
5. **Dynamical susceptibility of glass-formers** — arxiv cond-mat/0412158. chi_4 is intrinsically a batch / four-point quantity; defines via space-integrated four-point correlator. *Predicts Rescue 3 failure mode.*
6. **Concentrated suspensions of Brownian beads** — arxiv 1904.01865. Single-particle-trajectory chi_4 estimates are statistically marginal at small sample. *Predicts Rescue 3 failure mode at per-query granularity.*
7. **The Kovacs effect in model glasses** — arxiv cond-mat/0306089. Kovacs hump "requires the full probability distribution (of domain sizes or relaxation times)" not just averages — intrinsically ensemble. *Predicts Rescue 4 failure mode at per-query granularity.*
8. **Strain-driven Kovacs-like memory effect in glasses** — Nat. Commun. s41467-023-44187-x. Kovacs hump amplitude depends on full pre-perturbation state distribution. *Reinforces Rescue 4 cost analysis.*

All 8 sources verified via WebSearch returns; primary anchors (1, 2, 3) are the load-bearing citations for the recommended top picks (Rescues 5, 1, 6).

---

## Final recommendation to Strategy

**Execute Rescue 5 (Gap C subsumption audit) FIRST.** Zero compute. 2 h documentation work. Likely outcome: Cap 2 closure becomes FINAL, portfolio updates to 11 cleanly.

**IF and ONLY IF Rescue 5 audit surfaces a gap** (Gap C does not cover Cap 2's full product spec), escalate to **Rescue 1 (endpoint-id + Mondrian/PLCP conformal) + Rescue 6 (Trust Score composition)**. Expected combined deflated P ~ 0.35-0.40, ~10 min CPU, decisive in one cycle.

**Do NOT pursue Rescues 2, 3, 4** unless the cap_map review later flags a specific substrate-physics framing requirement (cross-application probe), because lit explicitly predicts their per-query failure modes.

Sequencing keeps queue depth >= 1 (no compute blocked on this decision) and follows [[feedback-dont-overextend-theorems]] — closing only the scope the data refutes, opening one new axis (endpoint-id + conformal) with explicit hard-fail bounds.
