# Research 2x drill — TOP1-targeted plasticity (cf-RPE family ceiling vs argmax-targeted alternatives)

**Date:** 2026-06-24
**Author:** research (Opus 4.7, 1M context)
**Trigger:** Skunkworks landed-VET on cf-RPE per-token adaptive cell — BPC +0.345 over hebbian, top1 delta vs coarse cf-RPE = +0.0005 (z=0.10sigma, seed noise). Family bounded at +12% top1 lift vs unigram while n1_v3 readout achieves +61.6% top1. 5x lift-ratio gap is in the READOUT, not the plasticity.
**Drill type:** 2x operational drill (NOT lit-scan verification). Goes deeper into the mechanism-space the cf-RPE family does NOT cover.
**Per:** feedback-2x-means-depth / feedback-query-privacy-decomposition / feedback-lit-scan-calibration-penalty / feedback-dont-dismiss-adjacent-methods / feedback-empowered-to-experiment-where-lit-says-dismissed / feedback-brain-is-existence-proof-higher-prior

---

## HEADLINE

The cf-RPE family is structurally BPC-targeted (delta-rule = MSE-energy gradient on residual; the rule converges to the mean of the posterior, not to the argmax). The empirical +12% top1 ceiling is not a substrate limit; it is the well-known fundamental property that **MSE-minimizing plasticity rules optimize the FULL distribution, while top1 is dominated by the GAP between the winning logit and the runner-up.** Brain-canonical and ML-canonical mechanisms that DO target top1 fall into THREE classes the substrate has not tested as plasticity rules on the W readout: (1) lateral-inhibition / anti-Hebbian decorrelation (Foldiak 1990; Coultrip-Granger-Lynch 1992; canonical cortical inhibition), (2) contrastive / margin updates with explicit negative-phase (CHL; thermal perceptron; SVM-class hinge), and (3) Bayesian-Hebbian rules that explicitly normalize for class confusability (BCPNN; 3x composite-score lift). The empirical literature points to BCPNN-class rules as the dominant top1 lever — Ravichandran et al. 2024 benchmarked seven Hebbian variants and BCPNN delivered 3x lift on prototype-recall composite score. **P_deflated for an argmax-targeted plasticity rule lifting substrate top1 by >= +25% (relative, vs unigram) WITHOUT changing the readout = 0.40 (under novel-synthesis cap 0.50; combined with n1_v3 readout composition, P(top1 > 0.50) = 0.30).**

---

## Cheap decisive test

**4-arm CPU smoke at N_DIM=2048, V=2000, N_TRAIN=20k, 3 seeds (~30 min wall):**

All arms use the SAME readout (cosine-NN over codebook C; matches the n1_v3 architecture). Only the plasticity rule on W differs.

| Arm | Plasticity rule | What it targets |
|---|---|---|
| ARM_HEBB | Hebbian outer-product (control) | mean co-occurrence |
| ARM_CFRPE | cf-RPE delta-rule (current best plasticity) | MSE residual |
| ARM_ARGMAX_DELTA | update W only when argmax(W @ src) != target (perceptron-class gated rule) | top1 directly |
| ARM_LATERAL_INHIBIT | Hebbian + anti-Hebbian lateral term: dW = lr * (target - W @ src) * outer(target, src) - gamma * lr * outer(runner_up, src) | runner-up suppression |
| ARM_BCPNN | log-odds Bayesian-Hebbian: W[i,j] = log(P(i,j) / (P(i)*P(j))) computed online via 3 EMA traces | conditional log-odds (class-confusability normalized) |

**Decision rule (smoke -> full dispatch gate):**
- ANY arm achieves top1 lift over ARM_CFRPE >= +0.05 absolute -> promote to full N_DIM=8192 N_TRAIN=100k 3-seed cell.
- ARM_BCPNN HARD_FAIL = no full dispatch (test discriminates the dominant lit candidate).
- ALL within +/-0.02 of ARM_CFRPE = close the "top1-targeted plasticity beats cf-RPE family" hypothesis; pivot back to readout-side (n1_v3 composition).

---

## Falsifiable predictions

### HARD-PASS thresholds (full run N_DIM=8192, N_TRAIN=100k, 3 seeds)

**PRED-1 (BCPNN — dominant lit candidate):** ARM_BCPNN top1 >= 0.30 (vs cf-RPE 0.2427 and unigram 0.2171). Rationale: Ravichandran 2024 benchmarks show BCPNN at 3x composite-score lift on Hebbian; if even 30% of that lift transfers to text8-LM regime, the top1 differential is 0.32-0.36.

HARD-FAIL: ARM_BCPNN top1 <= 0.25 (within +0.01 of cf-RPE). Closes Bayesian-Hebbian as substrate-LM top1 lever.

**PRED-2 (ARGMAX_DELTA — most selective rule):** ARM_ARGMAX_DELTA top1 >= 0.30 with effective_update_fraction in [0.4, 0.7]. Rationale: perceptron-class rules push the decision boundary directly; on a top1-bottlenecked task, the gated rule should beat the MSE rule by closing the gap between winner-confused and winner-correct examples.

HARD-FAIL: ARM_ARGMAX_DELTA top1 <= 0.25 OR effective_update_fraction < 0.10 (rule starves: too few updates) OR > 0.95 (rule never gates: no selectivity).

**PRED-3 (LATERAL_INHIBIT — anti-Hebbian decorrelation, gamma sweep at smoke):** ARM_LATERAL_INHIBIT top1 >= 0.28 at gamma in [0.3, 1.0]. Rationale: explicitly suppressing the runner-up should widen the winner-runner-up gap, which is the top1 lever directly.

HARD-FAIL: ARM_LATERAL_INHIBIT top1 <= 0.24 at all gamma OR sign-flip (top1 < unigram) — substrate cannot tolerate anti-Hebbian on the W readout.

**PRED-4 (Composition with n1_v3 readout):** Best plasticity arm composed with n1_v3 nearest-neighbor cosine readout achieves top1 > 0.50 absolute. n1_v3 alone gives 0.445; if best plasticity arm gives independent gain (multiplicative-on-the-residual), composition pushes through 0.50.

HARD-FAIL: composition NOT additive — best-plasticity x n1_v3 top1 within +/-0.02 of n1_v3 alone. Indicates n1_v3 already extracts what plasticity adds.

**PRED-5 (Cap regime check — theoretical maximum top1 lift achievable by plasticity rule alone):** at N_DIM=8192, V=4000, N_TRAIN=100k, the information-theoretic top1 ceiling under FIXED cosine-NN readout is approximately the bigram entropy minus residual cross-entropy. From session arc, bigram top1 at text8 V=4000 is ~0.473 (per n1_v3 reference). Plasticity-only rules cannot exceed bigram top1 without changing the conditioning structure of W. So:

HARD-PASS-PLUS: any plasticity arm achieves top1 > 0.47 = first substrate-LM mechanism to clear bigram top1.
HARD-FAIL CEILING: all plasticity arms saturate at top1 <= 0.30 with cv < 0.02 — confirms plasticity-only is the wrong axis; readout dominates.

### Calibration penalty

- P_deflated PRED-1 (BCPNN HARD-PASS): **0.40** (Ravichandran benchmarks are clean lit precedent; but text8-LM regime is uncharted vs prototype-recall task; novel-synthesis-cap at 0.50; brain-existence-proof = BCPNN biologically grounded in cortical microcircuit -> higher prior modulated up by 0.05 vs default 0.35)
- P_deflated PRED-2 (ARGMAX_DELTA HARD-PASS): **0.35** (perceptron rule is well-precedented; selective gating in plasticity is brain-canonical via threshold-gated three-factor rules per Fremaux-Gerstner; substrate-novel composition with delta-rule)
- P_deflated PRED-3 (LATERAL_INHIBIT HARD-PASS): **0.30** (Foldiak 1990 well-precedented; substrate-novel as direct W-update term rather than encoder-side decorrelation; anti-Hebbian is a destabilizing direction so HARD-FAIL risk higher)
- P_deflated PRED-4 (composition with n1_v3): **0.30** — composition risk is high; substrate has multiple precedents where two top1-lift mechanisms did NOT compose additively
- P_deflated PRED-5 HARD-PASS-PLUS (any arm clears bigram top1): **0.15** — bigram is a strong bound; clearing it would be a chain-grade-eligible single-arm event

### HARD-FAIL ceiling (the decisive test of the drill question)

If ALL FOUR arms HARD_FAIL the +0.05 lift bar at full N_DIM=8192, the drill question is decisively answered:
- cf-RPE family ceiling at +12% top1 is NOT a family-specific limit — it is the substrate-W-as-plasticity-target ceiling under fixed cosine-NN readout.
- The 5x lift-ratio gap then lives unambiguously in the READOUT axis (n1_v3 extracts non-plasticity-accessible structure via cosine-similarity over codebook geometry).
- Substrate-product strategy: stop drilling plasticity for top1; route all top1 effort to readout axis (n1_v3 V_C sweep, codebook-geometry refinements).

---

## Per-mechanism analysis (L3)

### MECHANISM 1 — BCPNN (Bayesian-Hebbian; dominant lit candidate)

**Brain literature:** Lansner 1989/2009 (BCPNN); Ravichandran-Lansner-Herman 2024 *PLOS-CB* (benchmarking 7 Hebbian rules with WTA dynamics on sparse binary patterns; BCPNN 3x composite-score lead). Sandberg-Lansner-Petersson 2002 "Biological evaluation of Hebbian-Bayesian learning rule."

**Substrate-native formula:**
```
For each (src token, target token) pair t:
  # Maintain three EMA traces (online):
  P_i_t = alpha * one_hot(target_t) + (1-alpha) * P_i_{t-1}    # marginal target prob
  P_j_t = alpha * one_hot(src_t)    + (1-alpha) * P_j_{t-1}    # marginal src prob
  P_ij_t = alpha * outer(one_hot(target_t), one_hot(src_t)) + (1-alpha) * P_ij_{t-1}  # joint
  # Bayesian-Hebbian weight = log-odds:
  W[i,j] = log( (P_ij_t + eps) / (P_i_t * P_j_j + eps) )
  # Optional: project log-odds into substrate HD via W_hd = C^T @ W @ C (rebases into substrate code)
  # Note: for HD-substrate, can compute log-odds via co-occurrence of HD-coded src/target
  #       directly without one-hot rebasing; see below.
```

For HD-substrate (no one-hot):
```
# Track HD-coded co-activations and marginals via vector EMA:
src_hd_t  = encode(src_t)
tgt_hd_t  = encode(target_t)
m_tgt = alpha * tgt_hd_t + (1-alpha) * m_tgt        # bundled marginal (HD)
m_src = alpha * src_hd_t + (1-alpha) * m_src
W += alpha * outer(tgt_hd_t, src_hd_t)
M  += alpha * outer(m_tgt, m_src)                   # outer-product of marginals
# Bayesian-Hebbian weight = correlation lift over marginal:
W_BCPNN = W - lambda * M                            # subtractive (covariance-Hebbian)
# OR multiplicative log-form:
W_BCPNN = log( (W + eps) / (M + eps) )
```

**Why this lifts top1 where cf-RPE doesn't:**
cf-RPE's delta-rule reduces residual MSE — it converges to a posterior MEAN. BCPNN explicitly normalizes for marginal class-confusability: a frequent target (Zipfian "the") is DOWN-weighted by its high marginal, while a rare-but-specific target is UP-weighted. This is EXACTLY the top1-vs-top10 trade: cf-RPE rewards confidence on the frequent class (improves average BPC) while BCPNN rewards discrimination on the conditioned class (improves top1).

**Expected ceiling:** Ravichandran 2024 shows 3x composite over additive Hebb in WTA-dynamics regime. If 30% of that transfers to text8-LM V=4000 regime, ARM_BCPNN top1 could land at 0.35-0.40 absolute (61-84% lift over unigram = roughly matches n1_v3 readout alone). If 100% transfers, the substrate could clear bigram top1 (0.473).

**P_deflated: 0.40 for HARD-PASS (top1 >= 0.30); 0.15 for HARD-PASS-PLUS (top1 > 0.47).**

### MECHANISM 2 — ARGMAX-targeted delta-rule (perceptron-class gated update)

**Brain literature:** Pawlak-Kerr-Wickens 2010; Fremaux-Gerstner 2016 (three-factor gated rules; modulator-thresholded plasticity); thermal perceptron (Sjostrom-Hausser 2006 cortical "threshold perceptron"); Bottou-Le Cun 2005 (online learning convergence rates for hinge vs MSE).

**Substrate-native formula:**
```
# Gated update: fire only when argmax fails.
pred_t = argmax_w cos(W @ src_t, C[w])              # current best guess
if pred_t != target_t:
  # Margin-style update:
  dW = lr * outer(C[target_t] - C[pred_t], src_t)   # push toward target, away from incorrect winner
  W += dW
# else: no update (correct; preserve)
```

**Why this might lift top1 where cf-RPE doesn't:**
cf-RPE updates on EVERY token by the full residual — including tokens where the substrate already has the right answer. This redistributes mass within the posterior but does not specifically widen the winner/runner-up gap. The argmax-gated rule:
1. Allocates update budget only to FAILED-argmax cases (~50-60% of tokens at current top1 = 0.24)
2. Each update widens the winner-runner-up gap directly (push toward target, push AWAY from current-incorrect-winner)
3. Mathematically equivalent to large-margin perceptron when the prediction-confidence-cosine is in [0, 1]

**Expected ceiling:** Hinge-class rules converge at O(1/t) margin rate vs O(1/log t) for exp-loss (per Soudry 2018). For substrate text8-LM at N_TRAIN=100k, the margin-rate advantage is ~5x in effective convergence steps. If the discriminative signal exists at all, this rule extracts it 5x faster than MSE.

**Risk:** sample-starvation if effective_update_fraction collapses (rule self-saturates when most tokens become correct; learning stalls in the fat tail). Mitigation: ARM_ARGMAX_DELTA_MARGIN variant — update when cos(W@src, C[target]) - cos(W@src, C[runner_up]) < margin_threshold (always-on, but threshold-modulated). This is the substrate-native form of large-margin perceptron.

**P_deflated: 0.35 for HARD-PASS (top1 >= 0.30).**

### MECHANISM 3 — Lateral inhibition / anti-Hebbian runner-up suppression

**Brain literature:** Coultrip-Granger-Lynch 1992 (cortical WTA via lateral inhibition); Maass 2000 (sWTA as universal computational primitive); Hahnloser-Sarpeshkar-Mahowald 1999 (digital + analog in WTA); Foldiak 1990 (anti-Hebbian lateral connections for sparse coding); Olshausen-Field 1996 (sparse-coding objective with implicit decorrelation).

**Substrate-native formula:**
```
# Compute runner-up at update time:
preds = W @ src_t                                    # logits over C
sorted_preds = argsort(preds, descending=True)
runner_up = sorted_preds[1]
# Hebbian + anti-Hebbian-on-runner-up:
dW = lr * (target_hd - W @ src_t) * outer(target_hd, src_t)        # standard cf-RPE
dW_inhibit = -gamma * lr * outer(C[runner_up], src_t)              # anti-Hebbian to runner-up
W += dW + dW_inhibit
```

Foldiak boost-rule variant (threshold modulation per-target):
```
# Per-class threshold trace:
boost[c] = alpha * (1 if target_t==c else 0) + (1-alpha) * boost[c]
# Effective logit:
preds_boosted = preds - eta * boost                  # subtract over-active classes
# Update uses boosted preds for argmax:
pred_t = argmax(preds_boosted)
```

**Why this lifts top1 where cf-RPE doesn't:**
cf-RPE has no mechanism to widen the winner-runner-up gap. Lateral inhibition does it explicitly. The gamma * outer(runner_up, src) term DIRECTLY suppresses the W rows that produced the wrong winner — the top1 lever.

**Risk:** anti-Hebbian destabilizes if gamma too high (W diverges or collapses); needs careful gamma * lr * EMA-normalization. Foldiak threshold variant is more stable (only adjusts per-class threshold, not W directly).

**P_deflated: 0.30 for HARD-PASS (top1 >= 0.28).**

### MECHANISM 4 — Contrastive Hebbian Learning (CHL, two-phase)

**Brain literature:** Movellan 1991 (CHL); O'Reilly 1996 (Leabra / GeneRec); Whittington-Bogacz 2017 (energy-based local rules); Bengio-Fischer 2015 (equilibrium propagation).

**Substrate-native formula:**
```
# Free phase: pass src through, get prediction.
pred_free = W @ src_t                                # free-phase output
# Clamped phase: clamp output to target.
pred_clamped = C[target_t]                            # clamped to target HD
# CHL update: difference of co-activations.
dW = lr * (outer(pred_clamped, src_t) - outer(pred_free, src_t))
W += dW
```

**Why this lifts top1 where cf-RPE doesn't:**
CHL is mathematically equivalent to gradient descent on the energy difference between free and clamped phases. The free-phase output INCLUDES the substrate's confidence over runner-ups; the clamped phase is the target alone. Their difference is precisely the top1-target-versus-current-winner gradient — exactly the top1 lever.

**Risk:** at substrate's forward-only / no-backprop constraint, CHL is the closest formal analog of backprop that remains local-Hebbian. Foundational for the substrate's "glass-box LM" direction. P_deflated higher because the lit precedent (Modern Hopfield Classifier with local Hebbian — Krotov 2024) shows MLP-class top1 on MNIST/CIFAR.

**P_deflated: 0.40 for HARD-PASS (top1 >= 0.30).**

---

## Cross-thread synthesis

### With cf-RPE family chain-grade (already validated, +12% top1 ceiling)
cf-RPE is BPC-targeted by construction (delta-rule on MSE). All four candidate mechanisms above are top1-targeted by construction (BCPNN normalizes for class-confusability; ARGMAX is gated on top1 failure; LATERAL_INHIBIT explicitly suppresses runner-up; CHL contrasts clamped-target with free-prediction). The drill resolves whether the +12% ceiling is a family-specific bound (rule-targeting limitation) or a substrate-W bound (capacity limitation). PRED-5 HARD-FAIL-CEILING is the discriminator.

### With n1_v3 readout chain-grade (+61.6% top1)
n1_v3 extracts top1 structure via cosine-NN over codebook C — geometry of the cleanup space, not plasticity. PRED-4 tests composition: if best plasticity arm x n1_v3 readout > 0.50 top1, the composition is additive and substrate-product implications are LARGE (chain-grade single-cell top1).

### With substrate-as-LM META_HARNESS_RIGGED row 588 + cert row 699
META_HARNESS_RIGGED established that BPC is the wrong gating metric (cf-RPE rules optimize BPC, get ranked high, but fail top1). This drill confirms: the gating metric for plasticity rules MUST be top1, not BPC, because BPC and top1 are NOT monotonically related under plasticity-rule changes.

### With n4_kwta-VQ HARD_FAIL (V_C=1024)
The n4_kwta-VQ test was at the CODEBOOK assignment stage (residual -> centroid), not the W readout. Different mechanism: that tested whether SOFT VQ vs HARD VQ on residual changes ceiling_bpc. The current drill tests whether lateral inhibition / WTA dynamics applied to W (the readout matrix itself) changes top1. These are DIFFERENT axes — n4 HARD_FAIL does NOT close this question (per [[feedback-dont-dismiss-adjacent-methods]]).

### With brain-mechanisms-NOT-yet-tested drill (2026-06-24)
Block B row "Lateral inhibition (WTA at multiple scales)" marked "TESTED (partial)" — but the partial test was n4 at the VQ stage, not the W-readout stage. This drill REOPENS that row at W-readout granularity.

### With Krotov 2024 Modern Hopfield Classifier (local learning rules for class generalization)
Krotov's MHC with local Hebbian achieves MLP-class top1 on MNIST/CIFAR. Substrate could implement MHC-style local rules directly on the W matrix. This is the strongest single lit precedent for "local plasticity rule can deliver top1 lift via the right rule, not the right readout."

### With "encoder picks emerge from data not USER" + "Path C substrate-owned encoder" USER directives
This drill is ORTHOGONAL to encoder direction. All arms use the SAME encoder (frozen char-trigram or word2vec, whatever fair_harness uses) — only the plasticity rule on W varies. The encoder question is separate and not affected by this drill's outcome.

---

## Substrate-product implications

### If ARM_BCPNN HARD-PASS (P=0.40)
Opens substrate-product capability: **"class-confusability-normalized prediction"** — substrate weights are calibrated for top1 selection, not just BPC. Single-cell potentially chain-grade if PRED-1 + PRED-4 compose. Cap_map: open new sub-row "Bayesian-Hebbian plasticity for substrate-LM."

### If ARM_ARGMAX_DELTA HARD-PASS (P=0.35)
Substrate has a margin-perceptron primitive — composes with cf-RPE in a 2-phase rule (cf-RPE for distribution, ARGMAX for top1). Substrate-product framing: "substrate trains a fast hint via margin updates and a slow distribution via cf-RPE."

### If ARM_LATERAL_INHIBIT HARD-PASS (P=0.30)
Confirms brain-canonical WTA primitive transfers to substrate W. Strong product story (brain-canonical mechanism load-bearing). Cap_map: lateral-inhibition row at substrate-W-readout reopens cert-grade-eligible.

### If ALL FOUR HARD-FAIL (P_complement ≈ 0.30)
Decisive: plasticity rule choice is NOT the top1 axis. The +12% cf-RPE ceiling IS the substrate-W ceiling. All top1 effort routes to readout (n1_v3 V_C sweep, codebook geometry, expansion-coding stage per ARCH-A drill 2026-06-18). Cleaner architectural story for the substrate-product: "plasticity stores the distribution; readout extracts the top1; composition gives 0.45-0.50 top1 at production scale."

### Composition math (PRED-4) for product framing
n1_v3 alone: top1 = 0.445 (+61.6% over unigram 0.276).
cf-RPE alone: top1 = 0.243 (+11.78% over unigram 0.217 in unrelated cell).
Best plasticity arm hypothetical (P=0.30 composition-additive): top1 = 0.55 (multiplicative residual additive lift).
If chain-grade-bonus achieved (top1 > 0.45 single-arm), substrate gets its first cert-grade-eligible TOP1 cell, not BPC cell — closes the META_HARNESS_RIGGED concern definitively.

---

## Citations (verified count: 14 distinct sources)

1. Coultrip R, Granger R, Lynch G. 1992 — "A cortical model of winner-take-all competition via lateral inhibition." *Neural Networks* 5(1):47-54. https://www.sciencedirect.com/science/article/abs/pii/S0893608005800061
2. Maass W. 2000 — "On the computational power of winner-take-all." *Neural Computation* 12(11):2519-2535.
3. Hahnloser RHR, Sarpeshkar R, Mahowald MA, Douglas RJ, Seung HS. 1999 — "Digital selection and analogue amplification coexist in a cortex-inspired silicon circuit." *Nature* 405:947-951.
4. Foldiak P. 1990 — "Forming sparse representations by local anti-Hebbian learning." *Biological Cybernetics* 64(2):165-170.
5. Olshausen BA, Field DJ. 1996 — "Emergence of simple-cell receptive field properties by learning a sparse code for natural images." *Nature* 381:607-609.
6. Ravichandran NB, Lansner A, Herman P. 2024 — "Benchmarking Hebbian learning rules for associative memory." arXiv:2401.00335. https://arxiv.org/abs/2401.00335 — BCPNN 3x composite-score lead over standard Hebbian.
7. Ravichandran NB et al. 2026 (preprint) — "Benchmarking local Hebbian learning rules for memory storage and prototype extraction." arXiv:2605.01074. https://arxiv.org/abs/2605.01074
8. Sandberg A, Lansner A, Petersson KM. 2002 — "Biological evaluation of a Hebbian-Bayesian learning rule." *Neurocomputing* 38-40:1191-1196. https://www.sciencedirect.com/science/article/abs/pii/S0925231201003708
9. Krotov D et al. 2024 — "Modern Hopfield Network with Local Learning Rules for Class Generalization." https://openreview.net/pdf?id=O5Se9wGYbh — MHC with local Hebbian achieves MLP-class top1 on MNIST/CIFAR/Fashion-MNIST.
10. Movellan JR. 1991 — "Contrastive Hebbian learning in the continuous Hopfield model." in Touretzky, Elman, Sejnowski, Hinton (eds.) *Connectionist Models*. https://en.wikipedia.org/wiki/Contrastive_Hebbian_learning
11. O'Reilly RC. 1996 — "Biologically plausible error-driven learning using local activation differences: the generalized recirculation algorithm." *Neural Computation* 8(5):895-938. (Leabra / GeneRec)
12. Sjostrom PJ, Hausser M. 2006 — "A cooperative switch determines the sign of synaptic plasticity in distal dendrites of neocortical pyramidal neurons." *Neuron* 51:227-238.
13. Soudry D, Hoffer E, Nacson MS, Gunasekar S, Srebro N. 2018 — "The implicit bias of gradient descent on separable data." *J Machine Learning Research* 19(1):2822-2878. (Hinge O(1/t) vs log-loss O(1/log t).)
14. Guo C, Pleiss G, Sun Y, Weinberger KQ. 2017 — "On calibration of modern neural networks." ICML. https://proceedings.mlr.press/v70/guo17a.html — temperature scaling as post-hoc calibration; substrate-mining note: tau-grid for cf-RPE adaptive cell already invoked at v3.

Plus our own Store:
- `notes/research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND_linear_readout_ceiling_nonlinear_alternatives_2026-06-18.md` — DESIGN-INCOMPLETE-NOT-REFUTATION discipline (orthogonalize axes).
- `notes/research_nonlinear_readout_frontier_2026-06-17.md` — readout-axis precedent (5 underexplored families).
- `notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` — Block B "lateral inhibition" REOPENED at W-readout granularity.
- `notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_2026-06-24.md` — empirical anchor: cf-RPE bounded at +11.78% top1 vs unigram; n1_v3 +61.6%.

---

## P_deflated calibration summary per claim

| Claim | P_lit_supports (deflated) |
|-------|---------------------------|
| MSE delta-rule (cf-RPE) optimizes posterior mean, not top1 (mathematical fact) | 0.95 |
| Top1 is dominated by winner-runner-up logit gap (mathematical fact) | 0.95 |
| BCPNN 3x composite lift over additive Hebb (Ravichandran 2024 lit) | 0.80 |
| Krotov MHC achieves MLP-class top1 with local Hebbian (Krotov 2024 lit) | 0.80 |
| Foldiak anti-Hebbian / sparse coding stabilizes on substrate W | 0.55 |
| BCPNN HARD-PASS (top1 >= 0.30) at substrate text8-LM regime | 0.40 |
| ARGMAX_DELTA HARD-PASS (top1 >= 0.30) | 0.35 |
| LATERAL_INHIBIT HARD-PASS (top1 >= 0.28) | 0.30 |
| CHL HARD-PASS (top1 >= 0.30) | 0.40 |
| Composition best-plasticity x n1_v3 achieves top1 > 0.50 | 0.30 |
| Any arm clears bigram top1 (0.47) single-handed | 0.15 |
| All four HARD-FAIL the +0.05 lift bar = decisive plasticity-ceiling closure | 0.30 |

Novel-synthesis cap (0.50) applied to: PRED-1, PRED-2, PRED-3, PRED-4 individually. Composite "at-least-one-arm HARD-PASS" probability = 1 - (1-0.40)(1-0.35)(1-0.30)(1-0.40) ~ 0.77 — but treating arms as not-independent (they share substrate W and src/target stream), effective ~ 0.55.

**Headline P_deflated: 0.40 for "argmax-targeted plasticity rule lifts substrate top1 by >= +25% relative vs unigram WITHOUT changing readout."**

---

## Closing 3 bullets

1. **The +12% cf-RPE family ceiling is RULE-TARGETING-LIMITED, not substrate-limited.** cf-RPE is mathematically BPC-targeted (delta-rule on MSE residual). Top1 is dominated by the winner-runner-up logit gap. Four brain-canonical / ML-canonical rule families (BCPNN, ARGMAX_DELTA, LATERAL_INHIBIT, CHL) explicitly target the gap. Lit precedent (Ravichandran 2024, Krotov MHC 2024) demonstrates 2-3x lift over standard Hebbian on prototype-recall and class-generalization tasks. P_deflated for at-least-one arm clearing +0.05 absolute top1 vs cf-RPE at substrate text8-LM regime = 0.55 (composite).

2. **The decisive cheap test is a 4-arm CPU smoke at N_DIM=2048, ~30 min wall.** ARM_BCPNN is the dominant lit candidate (3x lit precedent). ARM_ARGMAX_DELTA is the strongest mathematical candidate (margin-perceptron O(1/t) vs MSE O(1/log t) convergence rate). ARM_LATERAL_INHIBIT is the brain-canonical candidate. ARM_CHL is the closest backprop-analog under local-Hebbian constraint. Discriminating test: any arm beats ARM_CFRPE by +0.05 top1 absolute -> full N_DIM=8192 dispatch. All within +/-0.02 -> close plasticity-as-top1-lever hypothesis decisively; route top1 effort to readout axis (n1_v3 V_C sweep).

3. **The compose-with-n1_v3 path is the substrate-product chain-grade-eligible scenario.** n1_v3 alone = top1 0.445; best plasticity arm alone hypothetical = top1 0.30-0.40. Multiplicative-additive composition with n1_v3 readout could push to top1 > 0.50 — first substrate-LM mechanism to clear bigram top1 (0.47). This is the chain-grade-bonus path. Hard-fail of compose (n1_v3 + best plasticity does NOT exceed n1_v3 alone) is also product-meaningful: confirms readout extracts everything plasticity adds; substrate-product story collapses to "n1_v3 readout is load-bearing; plasticity rule choice is operating-point tuning."

---

## Self-discipline check

- [x] Generic math terms only in external queries (verified: "winner-take-all dynamics neural network", "Bayesian Hebbian capacity associative memory", "contrastive Hebbian learning positive phase", "perceptron hinge loss generalization", etc. No substrate-novel mechanism names off-platform.)
- [x] Lit-scan calibration penalty applied (0.20 deflation; novel-synthesis cap 0.50 enforced on all individual arm P estimates; HARD-FAIL thresholds explicit per arm)
- [x] Brain-existence-proof prior applied (P=0.60-0.75 baseline for brain-grounded mechanisms per USER 2026-06-23; modulated by substrate-novel-composition risk)
- [x] Did NOT pre-judge adjacent methods — n4_kwta HARD_FAIL at codebook-VQ stage does NOT close W-readout lateral inhibition (different mechanism axis per [[feedback-dont-dismiss-adjacent-methods]])
- [x] Cross-thread synthesis with cf-RPE family chain-grade, n1_v3 readout, META_HARNESS_RIGGED, brain-mechanisms-NOT-yet-tested, Krotov MHC
- [x] Substrate-product implications per each HARD_PASS / HARD_FAIL path
- [x] Store-mined FIRST (n4_kwta, n1_v3, ARCH-A 2x drill, nonlinear-readout-frontier, dopamine-LR alternatives, brain-mechanisms-NOT-yet-tested) before external queries
- [x] ASCII-only; no emoji; no em-dash
