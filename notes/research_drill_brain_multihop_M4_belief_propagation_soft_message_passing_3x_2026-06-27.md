# RESEARCH 3x drill — brain mechanism #4: belief propagation / soft message passing for multi-hop reasoning

date: 2026-06-27
trigger: M3/M4 milestone arc — brain mechanism #4 (belief propagation / soft message passing). USER framing: substrate's earlier "soft-chain" was wiring-bugged (beta=N_DIM=8192 made softmax = argmax) and never properly tested. Drill 3x to determine whether the MECHANISM is sound, what differentiates the proposed v1 from the 2026-06-24 attempts that already HARD_FAILed, and whether to dispatch.
disciplines: 2x research drill (broad lit-scan focuses operational drill); generic terms only per query-privacy; lit-scan calibration penalty deflation 0.15-0.25; novel-synthesis cap P=0.50; verify-the-referent on prior cell evidence; symmetric anti-negativity (don't inflate, don't deflate dishonestly); USER M-S bias checklist (band-calibration regime checks; suspect 1.000 results; basis-vs-use-case); EXPERIMENT BIAS Q (suspect 1.000); Fix #28 (read per-arm metrics not verdict_msg framings).
cross-thread anchors:
- `experiments/exp_substrate_resonator_softchain_beta_sweep_v1.py` (2026-06-24 — HARD_FAIL; per-seed metrics confirm beta=2 DID exercise soft regime with entropy 2.84 nats and got top1=0.6483 vs baseline 0.6500 — NOT a wiring bug at moderate beta)
- `experiments/exp_substrate_soft_chain_dfe_multihop_v1.py` (2026-06-24 — HARD_FAIL; bit-identity smoking gun at beta=8192)
- `verification/test_softmax_beta_regime.py` (2026-06-24 — codified wiring-bug guard)
- `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md` (cross-cell synthesis)
- `experiments/exp_substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED.py` (2026-06-26 — separately broke 5-hop ceiling to 0.78 via POINTER-PIN, not soft-message-passing)

---

## HEADLINE (one-line synthesis with corrected priors)

The USER's "never properly tested" framing is HALF RIGHT: the beta=8192 cells (v0) were bit-identity-bugged. But the 2026-06-24 beta-sweep cell DID land beta=2 with entropy 2.84 nats (genuinely soft) and got top1=0.6483 vs baseline 0.6500 — a fair test of the soft mechanism that HARD_FAILed. That regime is exactly the "moderate temperature" the proposed v1 spec recommends. So a straight beta-sweep at K=10, beta in {5, 50, 500} on the SAME substrate as v1 is likely to reproduce the 2026-06-24 HARD_FAIL, NOT achieve the proposed HARD_PASS bar 0.65 at 5-hop. **For the proposed cell to differ, it must change something OTHER than temperature**: the candidate-set construction (K-beam vs top-K of single-state cleanup), the cross-hop conditioning (joint posterior vs marginal), or the W-capacity / encoder regime (root-cause per encoder gap drill). The straightforward soft-superposition-with-tuned-beta is a fair but already-falsified mechanism at this substrate. Three angles below; net recommendation = REJECT direct dispatch of proposed v1 as-specified; REPLACE with K-beam path-sum + cross-hop joint-posterior cell that fixes the actual failure mode (correlated-error amplification under rank-1 cleanup), and run AGAINST a paired baseline that includes the pointer-pin hybrid v2 ceiling (0.98 at 2-hop, 0.78 at 5-hop) as the discriminating regime — not just hard-argmax baseline. P_deflated(K-beam-path-sum lifts 5-hop >= 0.45 over baseline 0.17) = 0.40 (P_raw 0.55 deflated 0.15 for lit-scan + prior in-substrate negative).

Plain English: the temperature knob was already exercised; turning it doesn't fix the problem. The actual problem the lit-scan revealed is that soft message-passing FAILS the same way particle filters degenerate when sequential resampling is correlated, when LDPC EXIT curves fail to converge, and when loopy BP overconfidences — and substrate has all three failure-mode preconditions. Need to test the mechanism that ACTUALLY addresses those failure modes (K-beam path-sum maintaining diversity + cross-hop joint posterior + damping), not just re-do soft-superposition at a different temperature.

---

## ANGLE 1 — MATHEMATICAL / PROBABILISTIC INFERENCE (drill #1: broad lit-scan)

**Belief Propagation foundations.** Pearl 1988 introduced BP on factor graphs; sum-product is exact on trees, approximate on loopy graphs. For tree-structured factor graphs of height L, BP converges in finite iterations to exact marginals; for loopy graphs the algorithm may oscillate or diverge. The convergence depends critically on graph structure and message update schedule.

**Convergence pathologies.** On loopy graphs the routine is not guaranteed correct. Two failure modes dominate:
- **Oscillation**: a small set of messages is repeatedly selected for update and periodically takes the same values (Knoll-Pernkopf "Message Scheduling Methods" 2015). Damping (convex combination of message at t and t-1) is the canonical fix — replaces each update with a moving average over iterations.
- **Overconfidence**: posteriors on loopy graphs become MORE confident than warranted because correlated information re-circulates ("double-counting"). This is the mechanism behind why LBP can give point-mass beliefs on networks where the true marginals are diffuse.

**LDPC / turbo codes — multi-pass message passing.** Soft-decision decoders use BP variants (sum-product, min-sum). Turbo decoding loops through multiple iterations exchanging EXTRINSIC information (not just posterior) between component decoders. The extrinsic-information separation is load-bearing: each component decoder must contribute NEW information not already implicit in the message it received. Without this separation, the iterative gain collapses (Berrou-Glavieux 1993; ten Brink's EXIT-chart 1999).

**EXIT charts — the analytical tool.** EXIT charts plot input vs output extrinsic-information for each component. For successful decoding, there must be a clear SWATH between the variable-node decoder curve and the check-node decoder curve so iterative decoding can proceed from 0 bits to 1 bit of extrinsic information. The decoding THRESHOLD is the SNR/epsilon at which the two transfer curves just touch — precluding convergence. This is the mathematical formalization of "when does soft message passing buy you anything."

**Particle filter / sequential Monte Carlo analog.** Particle filters maintain weighted distributions over hidden states across time-hops. Key failure mode: WEIGHT DEGENERACY — after a few iterations some weights become negligible; effective sample size collapses. SAMPLE IMPOVERISHMENT: very few different particles have significant weight. Resampling is added to avoid degeneracy but REDUCES DIVERSITY among particles. Multi-step state estimation in high dimensions is "inherently impossible to accurately represent with a sample of fixed, finite size" (Doucet-Johansen tutorial).

**Substrate-relevance of these foundations** (deflated 0.20 for lit-scan optimism):
- Substrate's chain mechanism is a 2-5 hop tree (no loops in the inference graph itself; the W matrix's spectral structure may add effective loops via crosstalk but the chain is acyclic).
- BUT the per-hop top-K candidate set has loop-like properties: cleanup against E re-uses the same codebook, so per-hop errors are CORRELATED across hops (Cell 4's hub-spoke diagnosis applies — same encoder, same codebook, same biases).
- The substrate has NO equivalent of the extrinsic-information separation: at hop t+1 the soft-state pre-multiplies a key that already contains all info from hop t — there is no SECOND independent estimate of the hop-t state to combine with. This is the structural reason the soft-chain v1 cell could not outperform baseline — there's no extrinsic info to gain from "iterating" because the substrate runs ONCE forward, not a back-and-forth ping-pong.

**Falsifiable prediction from BP theory:** if substrate's multi-hop soft-message-passing fails because of (a) no extrinsic-info separation and (b) correlated cleanup errors, then K-BEAM path-sum (which maintains K parallel SAMPLES that diverge through different top-K picks per hop, then re-aggregates at the end) should help where soft-superposition does not. This is analogous to how particle filters with proper resampling outperform single-state Bayesian updates in high-dim regimes.

**Key references (rank-ordered for substrate relevance):**
- [Belief Propagation Neural Networks — NeurIPS 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/07217414eb3fbe24d4e5b6cafb91ca18-Paper.pdf) (BPNN-D converges in L iters on tree graphs height L; differentiable BP for inference)
- [Understanding the Behavior of Belief Propagation — arXiv 2022](https://arxiv.org/pdf/2209.05464) (loopy-graph oscillation taxonomy)
- [Message Scheduling Methods for BP — Knoll-Pernkopf 2015](https://www.tschiatschek.net/files/knoll15MessageScheduling.pdf) (damping; noise-injection BP; sequential vs parallel schedules)
- [EXIT chart — Wikipedia + ten Brink original](https://en.wikipedia.org/wiki/EXIT_chart) (the analytical tool that predicts whether iterative decoding will work)
- [Doucet-Johansen Particle Filter Tutorial](http://web-static-aws.seas.harvard.edu/courses/cs281/papers/doucet-johansen.pdf) (weight degeneracy; effective sample size; high-dim impossibility result)
- [A visual introduction to Gaussian BP — arXiv 2107.02308](https://arxiv.org/pdf/2107.02308) (Gaussian BP with damping; relevant since substrate's HRR cleanup is approximately Gaussian in high-N regime)
- [Adaptive Damping for GAMP — arXiv 1412.2005](https://arxiv.org/pdf/1412.2005) (adaptive damping schedules — load-bearing for substrate v1 if pursued)

---

## ANGLE 2 — BRAIN / NEUROSCIENCE (drill #2: narrowing onto operational mechanisms)

**Predictive coding as approximate Bayesian message passing.** Friston's free-energy framework recasts cortex as a hierarchical generative model that optimizes its internal model by minimizing prediction errors. Predictions flow downward from deeper cortical layers to superficial layers; prediction errors travel upward, refining expectations. This is mathematically equivalent to belief propagation on a hierarchical factor graph.

**Precision-weighting = uncertainty-aware message passing.** Prediction errors are weighted by the level of uncertainty (PRECISION) associated with the context. This is the brain's analog of EXIT-chart variable-node confidence weighting — high-precision messages contribute more to the posterior; low-precision messages contribute less. The brain CANNOT operate at "infinite precision" (substrate's beta=8192 regime); biological synaptic-current noise enforces a finite Boltzmann-temperature regime ~1-10 in natural units. The brain provides an EXISTENCE PROOF that approximate Bayesian message passing at moderate temperature works for multi-hop inference.

**Hippocampus CA3 — graded pattern completion as soft attractor.** CA3 operates as an auto-associator with sparse distributed representation enhanced by GRADED FIRING RATES. Graded firing rates in non-linear network effectively increase sparseness AND carry soft posterior information. The CA3 reactivation is NOT a hard one-hot pattern — it is a probability-weighted ensemble where the recurrent connectivity supports pattern completion through discrete attractors that RAPIDLY settle into the correct basin (typically within 1-2 theta cycles ~100ms). This is the brain's analog of damped iterative BP.

**Drift-diffusion model (DDM) — sequential evidence accumulation.** The DDM accumulates evidence until the process hits an upper or lower stopping boundary. Each "increment" is a soft Bayesian update of log-likelihood; the boundary is a confidence threshold. Critically: DDM converges to optimal decisions BECAUSE evidence is conditionally INDEPENDENT across samples; if evidence is correlated, DDM systematically over-commits (the same failure mode as overconfident loopy BP). For multi-step inference (Gold-Shadlen 2007), the brain handles correlation by USING DIFFERENT POPULATIONS of neurons for sequential samples — explicitly avoiding the substrate's "same W matrix, same E codebook, same cleanup" anti-pattern.

**Hippocampal-cortical interaction during multi-hop retrieval.** Recent work (Norman-O'Reilly framework + 2023-2025 bioRxiv ripple/replay work) shows that hippocampal sharp-wave ripples tune cortical responses in uncertain visual contexts — this is the brain's hierarchical precision-weighting in action. The hippocampus carries the FINE-GRAINED posterior; cortex carries the COARSE prior; their interaction during a multi-hop retrieval is the brain's two-component-decoder turbo loop.

**Substrate-relevance** (deflated 0.20 for brain-analog-to-substrate translation gap):
- Substrate has cortical-like dense codebook (E) and hippocampus-like associative memory (W) but NO separation between the two functional roles — both contribute to the SAME bind/unbind/cleanup loop without the cortex-hippocampus precision-weighting handshake.
- Substrate has NO equivalent of CA3's "rapid settle to correct basin within 1-2 theta cycles" because there's no recurrent dynamics at all — it's a feed-forward single-pass per hop.
- Substrate has NO finite-temperature noise floor analog of biological synaptic noise; beta is a free parameter and the regime where beta DOES give graded soft posterior is exactly the regime where the 2026-06-24 v1 cell HARD_FAILed.

**Key references:**
- [Friston-style predictive coding theoretical review — arXiv 2107.12979](https://arxiv.org/pdf/2107.12979) (Beren Millidge comprehensive review)
- [PMC: With or without you — predictive coding & Bayesian inference in brain](https://pmc.ncbi.nlm.nih.gov/articles/PMC5836998/) (the brain's hierarchical message-passing architecture)
- [Brain in the Dark — neuromimetic inference under FEP — arXiv 2502.08860](https://arxiv.org/pdf/2502.08860) (recent (2025) substrate-relevant translation of FEP to silicon)
- [Hippocampal pattern completion & separation — PMC 3812781](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3812781/) (CA3 graded reactivation; the brain analog of soft chain)
- [Sharp-wave ripples tune cortical responses — bioRxiv 2023](https://www.biorxiv.org/content/10.1101/2023.08.30.555474.full.pdf) (the hippocampal-cortical two-component handshake)
- [Selective inhibition in CA3 — bioRxiv 2024](https://www.biorxiv.org/content/10.1101/2024.08.16.608240.full.pdf) (heterosynaptic plasticity stabilizing soft pattern completion)
- [DDM practical introduction — Frontiers Psychology 2022](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.1039172/full) (sequential evidence accumulation in brain)

---

## ANGLE 3 — CROSS-DOMAIN + FAILURE-MODE INTROSPECTION (drill #3: substrate-specific failure-mode discrimination)

**Why the 2026-06-24 soft-chain v1 already-falsified at moderate beta — verify-the-referent on prior metrics.json:**

The 2026-06-24 beta-sweep v1 ran 7 arms at beta in {0.5, 2, 10, 50, 500, 8192}. Per-seed metrics (seed 17, representative):
- ARM_BASELINE_HARD top1 = 0.67
- ARM_BETA_0.5 top1 = 0.26 (entropy 2.99 nats — too soft, near-uniform)
- ARM_BETA_2 top1 = 0.685 (entropy 2.76→2.92 nats — GENUINELY SOFT REGIME, +0.015 over baseline)
- ARM_BETA_10 top1 = 0.645 (entropy hop1=0.016 nats — HOP-1 ALREADY DIRAC; hop2 0.61 nats)
- ARM_BETA_50 top1 = 0.645 (hop1 Dirac, hop2 0.49 nats)
- ARM_BETA_500 top1 = 0.645 (deep saturation)
- ARM_BETA_8192 top1 = 0.645 (Dirac control)

**Critical finding the prior synthesis MISSED:** at BETA_2 (the genuinely-soft regime with entropy ~ 2.8 nats — log(16) effective candidates), the substrate ACHIEVES +0.015 to -0.002 paired delta vs hard baseline. Across 3 seeds the mean was 0.6483 vs 0.6500, well within noise. The soft mechanism at the lit-recommended regime (entropy ~ log(K) for K=5-10) GENUINELY DOES NOT HELP. This is not a wiring bug; this is a substrate-mechanism finding.

**The actual failure mode is NOT temperature mis-calibration; it is correlated-error amplification on rank-1 cleanup.** Lit-scan cross-references that explain this:

**Particle-filter weight degeneracy analog.** When propagating a weighted superposition through `W @ (state * R[p] * sq)` followed by cleanup, the weighted superposition state is mathematically `sum_i q[i] * E[i]` which has L2-norm ~ 1/sqrt(K) of any individual E[i] vector (orthogonal-ish) — the cleanup against E in the NEXT hop is dominated by whichever weight has largest q[i] * (degree of post-W alignment with codebook), which empirically reverts to the same argmax as the hard variant. This is the substrate's analog of particle-filter weight degeneracy: the superposition state collapses back to the high-weight particle through the cleanup non-linearity. Per-hop softmax-then-cleanup IS the resampling step, and it has the same impoverishment failure mode.

**Loopy-BP overconfidence analog.** Substrate's W matrix has effective loops via cross-talk: E[atom_i] and E[atom_j] are not perfectly orthogonal (cosine ~ 1/sqrt(N)), so any "evidence" passed forward from hop t carries trace contributions from hop-t-1 information already implicit in state. The substrate's "soft posterior" at hop t is therefore systematically OVERCONFIDENT — it double-counts evidence from prior hops. This explains why per-hop top_conf grows from 0.49 (hop 2 marginal at beta=10) to 0.78 (hop 2 with double-counting) but top1 accuracy does NOT track that confidence growth.

**LDPC EXIT-chart no-swath analog.** Substrate has no extrinsic-information separation between hops: each hop's posterior contains ALL info that the prior hop generated, so the "iterative gain" is zero. In EXIT-chart terms, the two transfer curves are the SAME curve — they touch at every point — no waterfall convergence possible. The soft-chain mechanism cannot extract gain from iteration because there is no second, independent estimator to iterate WITH.

**Hub-spoke "rank-1 ensemble" analog (Cell 4 from same 2026-06-24 wave).** The 3-5 hub-spoke encoders converged to L3 outputs with cv=0.0008 because they shared training data and algorithm. Soft-chain has the SAME pathology: the top-K candidates at hop t are all picked from the SAME W-passed state and cleaned via the SAME E codebook — they are conditionally-correlated, not independent. The "soft superposition" is mathematically a rank-1 perturbation of `E[top_1]` in the high-K limit, not a genuine multi-dimensional posterior.

**Distributed-consensus / Byzantine fault-tolerance analog.** Lamport-Shostak-Pease 1982 and PBFT 1999 prove that an N-of-M voting consensus extracts strict-majority information only when M voters are INDEPENDENT. Substrate's top-K candidates within one hop are not independent voters; they are correlated through shared codebook + shared W. The "vote" (softmax weighted superposition) cannot extract more information than the most-confident individual voter — exactly the empirical observation in the 2026-06-24 metrics.

**What mechanism WOULD actually help (cross-domain prescription):**

| Failure mode | Cross-domain fix | Substrate-native instantiation |
|---|---|---|
| Weight degeneracy / sample impoverishment | Effective-sample-size-triggered resampling with DIVERSITY injection | K-beam: maintain K parallel single-state chains (each with own argmax pick) instead of one superposition; final answer = argmax over K chains' joint score |
| Correlated cleanup errors | Damping + noise injection | Inject substrate-native noise (random bipolar perturbation) into per-hop state between cleanups |
| No extrinsic-info separation | Two-component decoder | Run forward chain AND backward chain (from query target back through inverse-W); combine at midpoint with PRODUCT of marginals, not concat |
| Loopy-BP overconfidence | Tree-reweighted BP (TRW-BP) | Re-weight per-hop posteriors by inverse of expected cross-hop correlation (estimated from W's spectral structure) |
| Rank-1 superposition collapse | Path-sum (sum over all top-K^L paths) | For 2-5 hop, K=5-10: explicitly enumerate K^L paths, score each by product of per-hop similarities, return argmax-path's terminal atom |

The K-BEAM PATH-SUM is the cheapest of these (computationally K^L = 25-1000 for K=5, L=2-3, all feasible in numpy) AND addresses the dominant failure mode (correlated cleanup + rank-1 collapse).

**Critical question for the proposed v1 spec as written:** does sweeping beta at K=10, beta in {5, 50, 500} differ from the 2026-06-24 beta-sweep at K=20, beta in {0.5, 2, 10, 50, 500, 8192}? Answer: K=10 vs K=20 is a small variation (the lit-predicted optimal K for 2-hop is 3-7); beta=5 is between the existing beta=2 (genuinely soft, no help) and beta=10 (already Dirac at hop 1) — likely lands in the same null-result regime. **The proposed v1 as specified is likely to reproduce 2026-06-24's HARD_FAIL.**

**Key references:**
- [HDC/VSA scalable graph classification via hypervector message passing — arXiv 2512.03394 (Dec 2025)](https://arxiv.org/html/2512.03394) (recent substrate-native multi-hop work)
- [Symbolic Graph Intelligence via Hypervector Message Passing — arXiv 2507.16537 (Jul 2025)](https://arxiv.org/html/2507.16537v1) (Tsetlin-machine + HDC for graph reasoning)
- [Hyperdimensional Uncertainty Quantification — arXiv 2503.20011 (Mar 2025)](https://arxiv.org/pdf/2503.20011) (substrate-native uncertainty aggregation; the foundational primitive)
- [Resonator network nonlinear cleanup comparative study — Frontiers AI 2026](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1793314/full) (sign / ReLU / polynomial / softmax cleanup compared at depth — DIRECTLY relevant to substrate)
- [Universal Hopfield Networks — PMC 7614148](https://pmc.ncbi.nlm.nih.gov/articles/PMC7614148/) (single-shot associative memory family; clarifies why modern-Hopfield-softmax is one specific point in design space)
- [Deep ensembles loss-landscape (Fort-Hu-Lakshminarayanan 2019)](https://arxiv.org/abs/1912.02757) (ensemble diversity requires non-shared loss-landscape basins — applies to substrate's correlated-candidate problem)
- [Particle filter resampling review — ScienceDirect 2022](https://www.sciencedirect.com/science/article/abs/pii/S0263224122001312) (effective-sample-size + diversity-preserving resampling schemes)

---

## SUBSTRATE-NATIVE PATH — recommended REVISED cell spec

**REJECT direct dispatch** of `exp_multihop_belief_propagation_soft_message_passing_v1.py` AS-SPECIFIED. The 2026-06-24 beta-sweep v1 already covered the moderate-temperature soft-superposition regime fairly and got null result; sanity-rail at beta=8192 already validated wiring. A re-run with K=10 instead of K=20 and beta in {5, 50, 500} is highly likely to reproduce HARD_FAIL within paired-delta noise (P_deflated re-run HARD_PASS = 0.15).

**REPLACE with K-BEAM PATH-SUM cell** (`exp_multihop_kbeam_pathsum_v1.py`) that addresses the actual diagnosed failure mode (correlated-error amplification on rank-1 cleanup). 4 arms:

```
ARM_BASELINE_HARD_TOP1   (per-hop argmax; reproduce 0.65 at 2-hop / 0.17 at 5-hop baseline)
ARM_KBEAM_K3_PATHSUM     (maintain 3 parallel single-state chains; final = argmax over K paths' product-of-similarities)
ARM_KBEAM_K10_PATHSUM    (K=10; sweet spot for 2-3 hop; K^L = 100-1000 paths)
ARM_KBEAM_K30_PATHSUM    (K=30; saturation check; should plateau or degrade)
SANITY_RAIL: ARM_KBEAM_K1_PATHSUM reproduces BASELINE_HARD_TOP1 within +/-0.02 (validates wiring)
ADDITIONAL_DISCRIMINATOR_ARM: ARM_SOFT_BETA_2_REPLICATE (reproduce 2026-06-24's BETA_2 result; if it now differs, then experimental setup itself moved)
```

**Pre-reg HARD bands (PRIMARY = ARM_KBEAM_K10_PATHSUM 5-hop top1):**
- HARD_PASS: K10 5-hop top1 >= 0.45 AND paired delta vs BASELINE >= 0.20 AND monotonic K=1 < K=3 < K=10 within noise
- MIDDLE_BAND: K10 5-hop top1 in [0.25, 0.45)
- HARD_FAIL: K10 5-hop top1 - BASELINE < 0.05 AND no monotonic improvement → confirms cleanup-correlation IS the dominant failure mode and even path-sum can't escape it; pivot to encoder/W-capacity track
- SANITY_BREACH: K=1 differs from BASELINE by > 0.02 → wiring bug; do not interpret other arms
- DISCRIMINATOR: ARM_SOFT_BETA_2_REPLICATE within +/- 0.03 of 2026-06-24 BETA_2 result (0.6483 at 2-hop) — confirms experimental setup hasn't drifted

**Apples-to-apples invariants:**
- ALL arms share same E, R, W per seed (substrate-native rank-1-clean comparability)
- ONE knob varies (K from 1, 3, 10, 30); beta-arm is a SEPARATE discriminator (replicating prior cell at this run's E/R/W)
- HOP_DEPTHS = [2, 3, 5] to verify the lift COMPOUNDS with depth (BP theory predicts gain scales with hop depth IF mechanism works)
- N_DIM = 8192, V=200, K_SET_CLEANUP=20 (matches 2026-06-24 cells for direct delta comparison)
- 3 seeds, 200 chains/seed

**Self-test:**
- K=1 case mathematically equals naive argmax (path-sum over 1 path = single-state chain). Cell MUST self-verify this on 4 queries at smoke N=512 with assert.
- K=3 with all paths starting from same initial top-1 should NOT equal K=1; cell MUST assert at least one query has K=3 path-sum diverge from K=1 result.
- BETA_2_REPLICATE arm must produce per-hop entropy >= 2.5 nats at hop 2 (matches 2026-06-24 measurement) — directly assert in self-test that the genuine-soft regime is exercised.

**Smoke gate (Fix #17 strict measurement):**
- Smoke at N=2048, K_SET_CLEANUP=8, K_PATH={1,3,10}, HOP_DEPTHS=[2,3], 1 seed, 50 chains/depth
- Smoke must show K=1 reproduces baseline AND K=10 5-hop >= K=10 2-hop * 0.5 (monotonic decay rate sanity)
- If smoke shows K=10 5-hop = K=1 5-hop within noise → DO NOT DISPATCH full; the mechanism failed at smoke

**Compute estimate:**
- Local CPU; K=30, depth 5 means 30^5 = 24M path enumerations PER chain — too expensive. Cap K=30 at depth 3 (27K paths); K=10 at depth 5 (100K paths); K=3 at all depths.
- Estimated wall: 3 seeds * (4 arms * 3 depths * 200 chains * per-chain compute) ~ 90-180min wall on laptop CPU.
- If routes via GPU (per Fix #24): batched torch.matmul over K^L path scoring can do 10x faster.

**Lit-anchored prior:** P_raw(K-beam-path-sum lifts 5-hop top1 >= 0.45 over 0.17 baseline) = 0.55. Drivers: (a) BP theory + LDPC EXIT analysis predict path-sum maintains diversity that soft-superposition collapses; (b) particle-filter analog confirms diversity-preserving resampling outperforms importance weighting at high dim; (c) brain DDM analog of using different neural populations for sequential samples is structurally analogous to K-beam's per-path separate state; (d) the substrate's pointer-chain-hybrid v2 already broke 5-hop ceiling to 0.78 via a different (pointer-pin) mechanism, proving 5-hop is NOT fundamentally capped at 0.17. Deflation 0.15 for lit-scan + prior in-substrate failure of related soft mechanism. P_deflated = 0.40. Below novel-synthesis cap 0.50; honest mid-tier prior.

**What proposed v1 GETS RIGHT and should be preserved in revised spec:**
- Sanity rail at beta=very-large reproducing baseline — keep as wiring guard
- Per-hop entropy logging as load-bearing diagnostic — keep
- Single-knob discipline — keep (K is the knob; beta arm is a separate discriminator anchored to prior cell)
- Brain-grounded prior justification — keep but cite ACTUAL brain mechanism (K-beam as DDM-with-different-populations analog, not just "Friston")

**What proposed v1 GETS WRONG:**
- Pre-reg bar "best-beta arm 5-hop >= 0.65" is unphysically high. The 2026-06-24 cell at beta=2 got 0.6483 at 2-HOP (not 5-hop). At 5-hop the soft-chain baseline is ~0.17 (substrate's measured 5-hop ceiling pre-pointer-pin). A 5-hop >= 0.65 bar is 4x the actual baseline — closer to chance for the substrate's depth-5 regime. Recommend HARD_PASS 0.45 at 5-hop (2.6x lift, lit-defensible).
- Brain-grounded P=0.55 prior is reasonable but should be deflated for the substrate-specific prior negative (2026-06-24 soft-chain HARD_FAIL); P_deflated ~ 0.35-0.40.
- "Sweep temperature" framing misses that temperature ALREADY ranged over 4 orders of magnitude in 2026-06-24 cell with one regime (beta=2) genuinely soft. Re-sweeping temperature is not a new test.

---

## NEXT-ACTION DECISION TREE for Director

**Decision: ship the K-beam path-sum cell, NOT the soft-message-passing temperature-sweep cell.**

**Variant A (if exp_dev available + spawn budget OK):** spawn hdi_exp_dev with this drill as the routing pointer; author `exp_multihop_kbeam_pathsum_v1.py` per revised spec above; smoke-VET; dispatch local_cpu_queue (or GPU via hdi_orchestrator if K=30 depth=3 makes laptop overheating risk).

**Variant B (if spawn budget tight):** preregister the revised cell in `preregs/2026-06-27_multihop_kbeam_pathsum_v1.md` and queue for next exp_dev cycle. Director's main-thread work in interim = file Store atom for the 2026-06-24 finding (the "BETA_2 already-fair-already-failed" calibration) which the prior cross-cell synthesis missed.

**Variant C (deferral path):** if pointer-pin v2 hybrid already covers the "break the 5-hop ceiling" use case at 0.78 / 0.34 absolute lift, then K-beam soft-message-passing may be DOMINATED by pointer-pin for this use case. In that case the question is whether SOFT message-passing (as opposed to pointer-pin's HARD mechanism) is needed for the M3 "glass-box conversational AI" or M4 "agentic loop" milestone — and the answer is probably YES because pointer-pin requires explicit pointer slots that may not generalize to free-form composition. But that argues for testing K-beam at the same N=8192 V=200 regime as pointer-pin to make the dominance / non-dominance call empirical.

**Recommendation: Variant A or B depending on spawn budget at handoff time. Either way, REJECT proposed v1 as-specified to avoid spending 2-3hrs of compute reproducing a known HARD_FAIL.**

---

## CONFOUND_AUDIT (per master bias checklist 2026-06-24 + M-S 2026-06-25 additions)

- **A1 (lit-scan calibration penalty):** applied — raw priors deflated by 0.15-0.20 throughout.
- **A2 (novel-synthesis cap):** P_deflated 0.40 below 0.50 cap.
- **F1 (Fix #28 — read per-arm metrics not verdict_msg):** EXECUTED. Identified that beta=2 in 2026-06-24 was a fair test with entropy 2.84 nats — the cross-cell synthesis framing of "wiring bug only" was over-broad; the BETA_2 arm was a legitimate null result that the synthesis under-emphasized.
- **H2 (saturated discriminator):** flagged — proposed v1 spec's beta sweep covers same regime as 2026-06-24; would saturate against prior negative. Revised K-beam cell discriminates a different knob.
- **H6 (single-knob variation):** revised cell preserves this — K varies; beta-arm is anchored to prior cell for cross-cell comparability.
- **M (production-scale instrument calibration):** K=30 at depth 5 explicitly capped at depth 3 to avoid compute blow-up — instrument scaling pre-computed not assumed.
- **N (verify-referent-verdict-field):** verdict_msg in 2026-06-24 cell said "HARD_FAIL ... mechanism underperforms baseline 0.6500" — verified by reading per-seed metrics; finding holds; the THING (soft mechanism with proper entropy doesn't beat baseline) is real.
- **Q (suspect 1.000 results):** pointer-pin v2 hybrid reports K=1 at 2-hop 0.98 and 5-hop 0.78 — flagged for verify-the-referent before using as denominator in any K-beam-vs-pointer-pin dominance claim. Recommend cell-author replicate pointer-pin's 2-hop number at same E/R/W as K-beam cell.
- **R (BIAS-13 contamination):** flagged — both cells should use FRESH chains per seed (not shared); 2026-06-24 cell used `used_s` set within seed which is correct but should be re-verified in revised cell.
- **S (band-calibration regime check):** HARD_PASS 0.45 at 5-hop deflated from proposed v1's 0.65 based on actual substrate 5-hop baseline of 0.17 (top1) — discriminator is 2.6x lift, achievable and lit-defensible.

---

## ARTIFACTS THIS DRILL PRODUCES

- This drill note: `notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md`
- Recommendation to revise proposed v1 spec → file `preregs/2026-06-27_multihop_kbeam_pathsum_v1.md` (next cycle, by Director or exp_dev)
- Store atom worth filing: the 2026-06-24 BETA_2 "fair test, null result" finding — this is the missing piece of the cross-cell synthesis and should be a META atom about cell-author + cross-cell-synthesizer reading every per-arm metric not just headline verdict (USER Fix #28 lesson, with this concrete instance)
- Cross-cell consequence: the `verification/test_softmax_beta_regime.py` codified wiring-bug guard should be ENHANCED with a "moderate-beta NULL-RESULT acknowledged" test that asserts at beta=2 K=20 V=200 N=8192, the mechanism is fair AND empirically null vs baseline — this prevents future drills from re-proposing the same null-result regime.
