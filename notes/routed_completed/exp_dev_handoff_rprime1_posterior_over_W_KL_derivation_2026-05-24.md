---
SOURCE: research
RECIPIENT: exp_dev
TOPIC: R-PRIME-1 PAC-Bayes posterior-over-W KL derivation (closed form + substrate-computable approximation)
TRIGGER: R-PRIME-3 HARD-FAIL (input-data KL was the wrong quantity); R-PRIME-1 v2 HARD_FAIL (identity-covariance Gaussian over W is structurally vacuous, KL=N^2/2 regardless of update -- see exp_dev_to_strategy_rprime1_pac_bayes_reframe_2026-05-24.md)
CYCLE: research drill 2026-05-24
PRIOR ATTEMPTS RULED OUT (do not re-derive these):
  - Identity-covariance Gaussian posterior over vec(W) -> vacuous (KL = N^2/2 per task)
  - Input-data KL between corpora -> tested as R-PRIME-3, HARD-FAIL
COMPANION: pairs with exp_dev_handoff_rprime3_task_pair_geometry_2026-05-24.md
DISCIPLINE:
  - per [[feedback-strategy-spec-formula-selftests]]: 4 (input -> expected output) self-test pairs provided below
  - per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS/HARD-FAIL/MIDDLE bands pre-registered
  - per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis P capped at 0.50
  - per [[feedback-no-experiment-design-in-prompts]]: this handoff specifies the FORMULA and SELF-TESTS only; exp_dev decides N, M, seeds, queue, ETA, regime grid
LIT-SCAN CALIBRATION:
  P(formula matches Bet B retention within +/-3pp across 3+ regimes) before deflation: 0.55
  After lit-scan calibration penalty (uncharted regime, novel synthesis): 0.40
  Rationale: Laplace-Fisher posterior PAC-Bayes is a well-established route (Khan 2019, Daxberger 2021, Dziugaite-Roy 2017); the synthesis with Hebbian-outer-product likelihood is the load-bearing novel step
---

# R-PRIME-1: closed-form PAC-Bayes posterior-over-W KL term for Bet B retention

## TL;DR (one-paragraph)

The posterior-over-W KL term that actually predicts Bet B retention is **not** the identity-covariance Gaussian KL (vacuous: N^2/2) and **not** input-data KL (R-PRIME-3 HARD-FAIL). It is the **Laplace/Fisher-posterior KL** between the Phase-A and Phase-B trained-weight posteriors:

```
KL(q_B || q_A) = (1/2) * [ tr(F_A^{-1} F_B) - rank(F_A) + log(det(F_A)/det(F_B))
                            + (W_B - W_A)^T F_A (W_B - W_A) ]
```

When the Fisher F is well-approximated by its diagonal (the standard practical Laplace assumption — Daxberger 2021), this reduces to the substrate-computable expression

```
KL(q_B || q_A)  ~=  (1/2) * sum_i [ f_{A,i} * (w_{B,i} - w_{A,i})^2 + (f_{B,i}/f_{A,i}) - 1 - log(f_{B,i}/f_{A,i}) ]
```

where f_{A,i}, f_{B,i} are the per-parameter Fisher diagonals at the end of Phase A and Phase B respectively, and w_{A,i}, w_{B,i} are the corresponding W-matrix entries. The PAC-Bayes generalization-floor formula then reads

```
retention(t) >= 1 - sqrt( KL(q_t || q_{t-1}) / (2 * M_t) )
```

with M_t = effective sample count during Phase t (NOT M_total).

The crucial difference from the v2 attempt: replacing the identity covariance sigma^2 I with the **Fisher metric F_A** (the local geometry of the Phase-A likelihood) makes the bound non-vacuous because Hebbian outer-product updates lie in the low-curvature directions of F_A and hence contribute small (W_B - W_A)^T F_A (W_B - W_A), not large ||W_B - W_A||_F^2 / sigma^2 = N^2/2.

---

## (a) Derivation

### Lineage

The derivation is the standard "online PAC-Bayes via Laplace posterior" route, anchored in:

- **McAllester 1999** -- original Gibbs-classifier PAC-Bayes bound: retention >= 1 - sqrt((KL + ln(2 sqrt(M) / delta)) / (2 M))
- **Catoni 2007** -- tighter empirical-Bernstein form (we use the McAllester form for closed-form tractability)
- **Dziugaite & Roy 2017** -- "Computing nonvacuous generalization bounds for deep nets" -- demonstrates that the choice of posterior covariance is the load-bearing decision; identity covariance is generically vacuous
- **Khan, Nielsen et al 2018** -- Vadam / variational online learning: posterior covariance = Fisher^{-1} gives the meaningful PAC-Bayes bound for sequential-task training
- **Daxberger et al 2021** -- "Laplace Redux" -- practical recipes for diagonal-Fisher Laplace approximations
- **Bonnabel 2013 / Amari 1998** -- natural gradient: the Fisher is the *correct* metric on the weight manifold; KL between two posteriors at nearby parameter values is a Fisher-metric quadratic form, NOT a Euclidean one

### Step 1: posterior model

Assume each phase's training produces an approximately Gaussian posterior over W via Laplace approximation:

```
q_A(W) ~= N(W_A, F_A^{-1})       (posterior after Phase A)
q_B(W) ~= N(W_B, F_B^{-1})       (posterior after Phase B)
```

where W_A, W_B are the Hebbian-trained MAP weights and F_A, F_B are the empirical Fisher information matrices evaluated at W_A, W_B respectively under the substrate's per-batch retrieval log-likelihood.

### Step 2: Gaussian KL closed form

The KL divergence between two multivariate Gaussians N(mu_1, Sigma_1) and N(mu_2, Sigma_2) is the textbook formula:

```
KL(N1 || N2) = (1/2) * [ tr(Sigma_2^{-1} Sigma_1) - d + log(det(Sigma_2)/det(Sigma_1))
                          + (mu_2 - mu_1)^T Sigma_2^{-1} (mu_2 - mu_1) ]
```

Substituting q_B as N1 and q_A as N2 (we measure how far the Phase-B posterior has drifted from the Phase-A posterior, which is the "reference" for retention of task A):

```
KL(q_B || q_A) = (1/2) * [ tr(F_A * F_B^{-1}) - d + log(det(F_A^{-1})/det(F_B^{-1}))
                            + (W_A - W_B)^T F_A (W_A - W_B) ]
```

where d = rank(F_A). Reordering log terms:

```
KL(q_B || q_A) = (1/2) * [ tr(F_A * F_B^{-1}) - d + log(det(F_B)/det(F_A))
                            + (Delta_W)^T F_A (Delta_W) ]                          (*)
```

with Delta_W = W_B - W_A.

### Step 3: why this is the right object (vs v2 identity)

The v2 attempt assumed Sigma = sigma^2 I with sigma calibrated to ||Delta_W||_F / N. That choice gives

```
KL_v2 = ||Delta_W||_F^2 / (2 sigma^2) = N^2 / 2   (constant!)
```

regardless of the actual update direction. The pathology is that identity covariance assigns equal a-priori uncertainty to ALL N^2 W-entries, including the (N^2 - rank(W)) directions in which Hebbian outer-product updates never move. The bound then "pays" for KL in directions the substrate never visits.

The Fisher metric F_A *concentrates* on the directions that actually affect the Phase-A likelihood. For a Hebbian outer-product memory storing M_A patterns, rank(F_A) is at most M_A * d_key (where d_key is the key embedding dim), and the Fisher's nonzero eigenvalues are aligned with the stored-pattern subspace. Updates Delta_W that lie outside this subspace contribute zero to the Fisher quadratic form -- correctly, because they don't perturb the Phase-A likelihood.

### Step 4: substrate-computable approximation (diagonal Fisher)

The full Fisher F_A is N^2-by-N^2 -- infeasible to store. The standard Laplace-Redux practice (Daxberger 2021 sec 4.1) is the **diagonal-Fisher approximation**: F_A ~= diag(f_{A,1}, ..., f_{A,N^2}), where

```
f_{A,i} = (1/B_A) * sum_{b in BatchA} (d log p(y_b | x_b, W) / d w_i)^2 |_{W = W_A}
```

is the i-th diagonal of the empirical Fisher computed at W_A over Phase-A batches B_A. Under the diagonal approximation, (*) becomes the substrate-computable expression:

```
KL_diag(q_B || q_A) = (1/2) * sum_i [ (f_{A,i} / f_{B,i})
                                       - 1
                                       + log(f_{B,i} / f_{A,i})
                                       + f_{A,i} * (Delta_w_i)^2 ]                 (**)
```

with i ranging over all N^2 W-entries. (Self-test #2 below verifies the algebraic simplification.)

### Step 5: rank-reduction shortcut (Hebbian-specific)

For the Bet B Hebbian outer-product memory, the Phase-A likelihood gradient w.r.t. W has a rank-M_A structure: every per-batch gradient is a rank-1 outer product (key_b * value_b^T - reconstruction_error_b * key_b^T). Therefore most diagonals f_{A,i} are ~zero in the absence of regularization. Practically, exp_dev should either:

  (i) Add a small ridge: F_A_ridge = F_A + lambda * I with lambda = 1/N (regularizes the log-det and the inverse), or
  (ii) Restrict the sum in (**) to entries where max(f_{A,i}, f_{B,i}) > eps * max_j(f_{A,j} or f_{B,j}), with eps = 1e-6.

Both give numerically stable bounds; option (i) preserves the closed-form, option (ii) is faster.

### Step 6: PAC-Bayes floor formula (unchanged from R-PRIME-1 spec)

Per McAllester 1999, the posterior-Gibbs generalization bound gives

```
retention_t  >=  1 - sqrt( (KL_acc + ln(2 sqrt(M_acc) / delta)) / (2 * M_acc) )
```

For the operating regime here (delta = 0.05, M_acc = O(thousand)), the ln term is O(5) and small relative to KL_acc when KL_acc >> 1. Simplification used in v2 (also used here):

```
retention_t  >=  max(0, 1 - sqrt( KL_acc / (2 * M_acc) ))                            (***)
```

with KL_acc = sum over phase transitions of KL_diag (eq (**) above) and M_acc = effective number of items the substrate has been trained on (post Phase B, M_acc = M_A + M_B).

---

## (b) Substrate-observable inputs needed

To compute KL_diag(q_B || q_A) for a single Bet B run, exp_dev needs:

| Artifact | Source | Extraction |
|---|---|---|
| **W_A** (Phase-A trained W) | Bet B run's checkpoint at end of Phase A | torch.save on `model.W` after Phase A; if not currently saved, exp_dev adds `torch.save(W.cpu(), out_dir / "W_phaseA.pt")` to `exp_wave14d_betB_kovacs_v1.py` after the Phase A loop completes |
| **W_B** (Phase-B trained W) | Bet B run's checkpoint at end of Phase B | same pattern: `torch.save(W.cpu(), out_dir / "W_phaseB.pt")` |
| **f_{A,i}** (Phase-A diagonal Fisher) | Re-compute on Phase-A batches at W_A | one forward+backward pass per Phase-A batch at frozen W_A; accumulate `(grad ** 2)` element-wise; normalize by batch count |
| **f_{B,i}** (Phase-B diagonal Fisher) | Re-compute on Phase-B batches at W_B | same recipe with Phase-B batches at frozen W_B |
| **M_A, M_B** (sample counts) | From the run's config | already in `metrics.json` -> `config["bytes_per_corpus"]` divided by sequence length, or equivalently `M_per_task` for the Hebbian-outer-product runs |
| **lambda** (ridge regularization) | exp_dev chooses; recommend lambda = 1/N | applied as F_diag + lambda before any inversion/log-det |
| **eps** (effective-rank cutoff) | exp_dev chooses; recommend eps = 1e-6 | only used in option (ii) above |

### Estimated extraction cost

- W_A, W_B: ~30MB each at N=4096; cheap to dump
- Diagonal Fisher: 1 epoch's worth of forward+backward at frozen weights; for Phase A with 5000 bytes (smoke) ~0.5s on GPU, for FULL ~ 10-30s on GPU
- Total added compute per Bet B run: < 1 minute on overnight_queue GPU

### Code skeleton (Python; exp_dev integrates)

```python
def compute_diagonal_fisher(model, batches, W_anchor):
    """Empirical-Fisher diagonal at W_anchor over batches."""
    model.W.data.copy_(W_anchor)
    fisher_diag = torch.zeros_like(W_anchor)
    n_b = 0
    for x, y in batches:
        model.W.grad = None
        loss = -model.log_likelihood(x, y)   # negative log-lik per batch
        loss.backward()
        fisher_diag += model.W.grad.detach() ** 2
        n_b += 1
    return fisher_diag / max(n_b, 1)

def kl_diag_laplace(W_A, W_B, fisher_A, fisher_B, ridge=None):
    """Diagonal-Laplace PAC-Bayes posterior KL, eq (**) above."""
    if ridge is None:
        ridge = 1.0 / W_A.shape[0]
    fA = fisher_A + ridge
    fB = fisher_B + ridge
    delta = W_B - W_A
    term_quadratic = (fA * delta * delta).sum()
    term_trace     = (fA / fB).sum()
    term_logdet    = (torch.log(fB) - torch.log(fA)).sum()
    d              = fA.numel()
    return 0.5 * (term_trace - d + term_logdet + term_quadratic)

def pac_bayes_floor(kl_total, m_total):
    if m_total <= 0:
        return 0.0
    return max(0.0, 1.0 - math.sqrt(kl_total / (2.0 * m_total)))
```

---

## (c) Self-test pairs (per [[feedback-strategy-spec-formula-selftests]])

**REQUIRED**: exp_dev MUST run these self-tests BEFORE shipping the FULL experiment; if any self-test fails, the formula is implemented wrong, NOT the substrate is failing.

### Self-test 1: trivial (Phase A == Phase B -> KL = 0)

| Input | Expected output |
|---|---|
| W_A = identity_N, W_B = identity_N (identical) | KL_diag = 0 exactly |
| fisher_A = ones(N,N), fisher_B = ones(N,N), ridge = 0 | (term_trace = N^2, term_logdet = 0, d = N^2, term_quadratic = 0) -> KL = 0.5 * (N^2 - N^2 + 0 + 0) = 0 |

**Pass criterion**: |KL_diag| < 1e-9 for N in {16, 64, 256}.

### Self-test 2: diagonal scaling (algebraic check on simplification)

For 1-D case (single scalar parameter): W_A = 0, W_B = 1, fisher_A = 4, fisher_B = 1, ridge = 0.

Plugging into eq (**):
- term_trace = fA / fB = 4
- d = 1
- term_logdet = log(fB) - log(fA) = log(1) - log(4) = -log 4
- term_quadratic = fA * (Delta_W)^2 = 4 * 1 = 4

KL_diag = 0.5 * (4 - 1 + (-log 4) + 4) = 0.5 * (7 - log 4) = 0.5 * (7 - 1.3863) = **2.8069** (to 4 decimal places).

**Pass criterion**: |computed - 2.8069| < 1e-4.

### Self-test 3: asymmetric case (distinguishes from naive ||W_A - W_B||^2)

Setup that defeats the naive Euclidean distance metric:
- N = 4 (so W is 4x4 = 16 entries)
- W_A = zeros(4,4)
- W_B = W_A with W_B[0,0] = 1.0, all other entries 0 (single-entry perturbation)
- fisher_A: diagonal with f_{A,0} = 100.0 (high curvature at entry [0,0]) and f_{A,i} = 0.01 elsewhere
- fisher_B = fisher_A (Phase B Fisher equals Phase A Fisher; same curvature)
- ridge = 0

Naive Euclidean: ||W_B - W_A||_F^2 = 1.0
Correct Fisher-metric quadratic: Delta^T F_A Delta = 100.0 * 1 + 0 = 100.0

Plugging into eq (**):
- term_trace = sum(fA/fB) = 16 (since fA=fB elementwise)
- d = 16
- term_logdet = 0 (since fA=fB elementwise -> log(1) = 0 per entry)
- term_quadratic = 100.0 (from the single high-Fisher direction)

KL_diag = 0.5 * (16 - 16 + 0 + 100) = **50.0**.

Compare: a naive Euclidean PAC-Bayes with sigma^2 = 1 would give 0.5 * 1.0 = 0.5 (200x smaller). This self-test confirms the formula correctly *up-weights* updates in high-Fisher (high-curvature) directions, which is the load-bearing property for retention prediction.

**Pass criterion**: |computed - 50.0| < 1e-4.

### Self-test 4: monotonicity in ||Delta_W|| within a fixed Fisher (sanity)

Setup: N = 4, fisher_A = fisher_B = ones(4,4), ridge = 0.
Sweep alpha in {0.1, 0.5, 1.0, 2.0, 5.0}; W_A = zeros, W_B = alpha * randn(4,4) with fixed seed.

Expected: KL_diag(alpha) = 0.5 * alpha^2 * ||randn||_F^2 (since term_trace = d = 16 cancel, term_logdet = 0, only term_quadratic survives).

For seed=0 with numpy `default_rng(0).standard_normal((4,4))`, ||randn||_F^2 = 13.498337 (verified). Expected KL values: alpha=0.1 -> 0.067492; alpha=0.5 -> 1.687292; alpha=1.0 -> 6.749169; alpha=2.0 -> 26.996675; alpha=5.0 -> 168.729216. exp_dev: if using a different library/seed, regenerate the prefactor; the *form* (KL = 0.5 * alpha^2 * ||randn||_F^2) is the load-bearing invariant.

**Pass criterion**: For each alpha, |KL_diag(alpha) - 0.5 * alpha^2 * ||randn||_F^2| / KL_diag(alpha) < 1e-6. (Relative error since absolute scales with alpha.)

---

## (d) Approximation regime caveats

| Caveat | Threshold / regime | Mitigation |
|---|---|---|
| **Gaussian posterior** is a Laplace approximation -- valid only when the log-posterior is approximately quadratic around the MAP | Valid for small Phase-B updates; **breaks down when ||Delta_W||_F / ||W_A||_F > ~0.5** (substrate has moved out of the local Laplace basin) | exp_dev: report ||Delta_W||_F / ||W_A||_F alongside KL_diag; flag any regime where this ratio exceeds 0.5 as "Laplace assumption suspect" |
| **Diagonal-Fisher approximation** ignores off-diagonal Fisher correlations; underestimates KL when updates are aligned with off-diagonal Fisher structure | Generally tightens (under-bounds) the true KL; the PAC-Bayes floor remains valid but may be loose | If exp_dev sees PAC-Bayes floor systematically *exceeding* measured retention, the diagonal approximation may be too loose -- upgrade to KFAC (Martens & Grosse 2015) block-diagonal Fisher |
| **Empirical Fisher vs true (model) Fisher** -- we use the gradient-squared empirical estimator, not the model-Hessian | Empirical Fisher = true Fisher only at the MAP optimum; deviates when training hasn't converged | exp_dev: ensure Phase-A loss has plateaued before snapshotting W_A; rule of thumb: last 100 steps have |delta_loss| / loss < 0.01 |
| **Rank degeneracy in Hebbian-outer-product W** -- raw F_A is rank-deficient, log(det) goes to -infinity | Forces use of ridge regularizer | Recommended ridge = 1/N (gives proper proper-prior interpretation: posterior is over the affine subspace tangent to the stored-pattern manifold, with isotropic prior of variance N in the null space) |
| **Codebook-dimensionality scaling** -- as N grows, the diagonal-Fisher sum is dominated by O(M) nonzero entries (rank-M structure of Hebbian Fisher); KL_diag scales as O(M), NOT O(N^2) | The bound becomes *tighter* (more informative) for higher-dim substrates -- opposite of v2 pathology where bound was vacuous at all N | exp_dev: verify in the smoke run that KL_diag does NOT scale with N when M is held fixed; this is the key sanity check that distinguishes the Laplace-Fisher route from the v2 identity-covariance route |
| **M_acc choice** -- effective sample count is ambiguous when Phase A and Phase B have different token counts | Use M_A + M_B (post-Phase-B accumulated count); document choice in prereg | If retention metric is per-token-of-Phase-A, use M_A only; if per-token-of-aggregate, use M_A + M_B |
| **PAC-Bayes lineage choice (McAllester vs Catoni)** -- Catoni's bound is tighter when KL is moderate; McAllester is the closed-form-friendly default | At KL > 10 the two bounds agree to <5%; at KL < 1 Catoni can be 10-30% tighter | Use McAllester for the falsifiable prereg; report Catoni as a secondary cross-check (Catoni is implementable with the same KL_diag input -- only the bound-formula step changes) |
| **Confidence delta in McAllester** -- standard is delta=0.05; the ln term shifts the bound by ~ln(2 sqrt(M)/0.05) ~= 5 for M~1000 | Affects the bound by <1pp when KL > 20; negligible for retention-floor prediction | exp_dev: use delta = 0.05; document in prereg |
| **Phase-B Fisher F_B evaluation point** -- KL is asymmetric; should F_B be evaluated at W_B (post-Phase-B) or at W_A (pre-Phase-B)? | Standard online-Bayesian convention: F_B at W_B (the new MAP); but for Bet B retention prediction the relevant quantity is **forgetting of Phase A**, which uses F_A (Phase-A curvature) for the quadratic term and F_B (post-update curvature) only in the trace and log-det terms | Implementation: F_A at W_A, F_B at W_B. This is what eq (**) above does. |

---

## Pre-registered HARD-PASS / HARD-FAIL / MIDDLE bands for the eventual FULL experiment

Per [[feedback-envelope-expansion-fail-bands]] -- exp_dev's prereg file MUST cite these bands BEFORE the FULL ship:

- **HARD-PASS**: KL_diag-based PAC-Bayes floor matches measured retention within +/-3pp (absolute) on >= 3 of 5 norm regimes (norm in {0.5, 1.0, 2.0, 4.0, 8.0}, same as v2's regime grid) AND Pearson r(predicted, measured) >= 0.80 across all 5 regimes. -> **R-PRIME-1 promoted 🔬 -> 🟡 PARTIAL; PAC-Bayes Laplace-Fisher floor is binding mechanism for Bet B retention.**
- **HARD-FAIL**: max absolute error |measured - predicted| > 0.25 on every regime AND Pearson r < 0.20. -> **PAC-Bayes posterior-over-W KL formulation REJECTED. exp_dev rehab paths: (a) replace diagonal-Fisher with KFAC, (b) shift to function-space KL (Rescue #1 from exp_dev_to_strategy memo), (c) try empirical Bernstein PAC-Bayes (Rescue #3).**
- **MIDDLE**: anything between -- report bands, run one rehab attempt before closure.

These bands are TIGHTER than v2's +/-20% / r >= 0.60 because (i) the v183 PAC-Bayes floor already matched within 1pp on the limited regimes tested, raising the bar for what counts as confirmation, and (ii) the Laplace-Fisher derivation is principled (not heuristic) so loose tracking would not be a satisfactory promotion.

---

## What exp_dev decides (per [[feedback-no-experiment-design-in-prompts]])

- N, M, n_tasks, seeds, queue placement, ETA, ridge value, eps cutoff
- Whether to snapshot W matrices in the Bet B base script (likely yes -- adds ~60MB per run but enables this and other downstream analyses)
- Whether to compute KL via option (i) ridge-regularized or option (ii) effective-rank-truncated
- Smoke configuration: at minimum N=512, M=40, 2 tasks, 1 seed -- enough to verify the 4 self-tests pass on real artifacts
- Whether to ship as a re-run of v2 (overwriting wave14_rprime1_pac_bayes naming) or as a v3 with new name (recommend: v3 to preserve v2's negative result as scientific record)

## Companion items for cap_map update (Strategy will handle on verdict)

- substrate_capability_map.md R-PRIME-1 row currently 🔬 (hypothesis), pending FULL outcome
- If HARD-PASS: promote 🔬 -> 🟡 with note "PAC-Bayes Laplace-Fisher floor matches retention within 3pp; binding mechanism for Bet B retention; rules out function-space-KL-only narratives (Rescue #1 demoted)"
- If HARD-FAIL: keep 🔬 with note "PAC-Bayes posterior-over-W KL REJECTED via diagonal-Fisher Laplace; rescue paths: KFAC, function-space KL, empirical Bernstein"
- Either outcome: update cap_map "PAC-Bayes / information-theoretic floor" capability row with the new evidence

## Filing trail

- Companion to: exp_dev_handoff_rprime3_task_pair_geometry_2026-05-24.md (Bet B retention mechanism work; R-PRIME-3 already shipped)
- Resolves: exp_dev_to_strategy_rprime1_pac_bayes_reframe_2026-05-24.md (Rescue #1 function-space KL was the previously-leading direction; this handoff supersedes by showing the *weight-space* KL is also rescuable via Fisher metric, not abandoned as the strategy memo implied)
- Anchor for: any future PAC-Bayes work on Bet A or Bet C (the formula is substrate-agnostic; only the Fisher computation changes)

---

**End of handoff. exp_dev: read this, run the 4 self-tests on a 1-second toy implementation BEFORE adding W-snapshot logic to the Bet B script, ship smoke, then FULL.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
