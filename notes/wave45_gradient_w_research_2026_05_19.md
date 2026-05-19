# Wave 4.5 gradient W failure — research synthesis

Returned 2026-05-19. Unbiased deep research on the closed Wave 4.5 v3
negative (cross-entropy + Adam: +0.7 to +3.3 bpc worse than delta rule).

## Bottom line

**Gradient W is not "dead" but structurally disadvantaged on this
substrate.** The realistic upside ceiling is **matching delta rule,
not beating it by much.** The genuine win the literature points to
is a **curvature-aware delta rule** (Shampoo-block / EGOP / conjugate-
gradient inner step), not cross-entropy + Adam.

## What DeltaNet / Schlag-Irie actually do

**Neither paper backpropagates into the fast weight W.** W is
recurrent STATE, not a parameter:

- **DeltaNet (Yang 2024)**: explicitly frames the update as
  `S_t = S_{t-1} - beta_t (S_{t-1}k_t - v_t) k_t^T` =
  "optimizing online regression loss using single SGD step on
  L_t(S) = ||S k_t - v_t||^2". Gradients flow only through the
  slow projections W_k, W_v, W_q.

- **Schlag-Irie 2021**: "fast weight matrix W is not directly
  backpropagated. Instead, it's dynamically computed at each timestep
  through a differentiable update rule. Slow weights are what gradient
  descent trains."

**Why?** The delta-rule recurrence is already the right SGD step
for the local objective ||S·k - v||^2. Replacing the inner loop with
Adam re-parameterizes inner SGD as outer optimization — but Adam
can't see the recurrence structure and treats W as flat parameter.

2026 follow-ups (Preconditioned-DeltaNet, OSDN, MesaNet) confirm
the right move is **preconditioning the delta rule**, not replacing it.

## Liu/DePavia 2025 — preconditioner mismatch

Adam's diagonal preconditioner is **basis-sensitive**. For gradients
with outer-product / low-rank structure, Adam captures only diagonal
info and misses cross-coordinate correlation.

Our gradients are LITERALLY rank-1 outer products:
`dW = (softmax(W·ctx) - onehot) ⊗ ctx`

Adam's v_t (diagonal second moment) whitens this in the wrong basis.
The exploding-norm symptom at higher LR (||W||=669, 3316, 7619) is
the canonical signature of basis-mismatched preconditioning on
structured gradients.

LMS theory: for stability LR < 2/lambda_max(R) where R = E[ctx ctx^T].
With N=4096 and rich contexts, lambda_max ~ O(N); our lr=1e-2 and
3e-2 violate this. Delta rule survives because its effective LR is
normalized by ||k||^2 implicitly.

## Cross-entropy vs MSE objective gap (irreducible)

Cross-entropy on softmax(W·ctx · C^T) and MSE ||W·ctx - atom||^2 have
different minima except at the point where the model puts mass 1 on
the right atom.

Hebbian Descent (Melchior-Wiskott 2019): with linear activation,
Hebbian descent IS the delta rule = Widrow-Hoff = LMS. With softmax+CE,
they diverge.

Our 57-60% argmax-accuracy with bad bpc is textbook: gradient training
saturates the top guess (sharpens softmax) at the expense of the tail.
CE penalizes mildly, bpc penalizes harshly. **The +0.99 bpc gap is
partly objective-floor and partly preconditioner.**

## Five rescues ranked by literature support

| # | Rescue | Predicted delta vs delta-rule | Backing |
|---|---|---|---|
| 1 | Plain SGD, lr~1/lambda_max(R), no Adam | +0.05 to +0.20 (still worse) | Strong (Test-time-regression, LMS theory) |
| 2 | Codebook-projected dW + plain SGD | ~= delta rule within noise | Strong (collapses to delta rule mathematically) |
| 3 | **Block-Shampoo / EGOP preconditioner on W only** | **Possibly BETTER than delta** | **Strong** (Preconditioned-DeltaNet, OSDN, Liu 2502.01594) |
| 4 | Temperature-learned cosine softmax + Adam | Closes some calibration; won't close objective | Moderate |
| 5 | Decoupled-LR Adam (per-row LR scaled by 1/||row||^2) | +0.2 to +0.5 still worse | Weak |

**MSE-in-bundle-space (v3) is exhausted.** What's left:
- (a) MSE WITH per-sample LR normalization by ||ctx||^2 — turns MSE-Adam
      into delta rule by construction
- (b) MSE on post-cleanup vector, not raw bundle

## Recommended single 1h experiment

**Codebook-projected SGD on MSE, lr-normalized by ||ctx||^2** (rescue #2):
- If matches delta rule within noise: negative result fully explained
  by Adam + objective; gradient-W is closed
- If also fails: substrate has deeper architectural mismatch; abandon
  rehabilitation in favor of curvature-aware delta rule

## Sources

- [DeltaNet Yang 2024](https://arxiv.org/abs/2406.06484)
- [Schlag-Irie 2021 Linear Transformers as Fast Weight Programmers](https://arxiv.org/abs/2102.11174)
- [Liu/DePavia 2025 EGOP preconditioner](https://arxiv.org/abs/2502.01594)
- [Test-time regression unifying framework 2025](https://arxiv.org/pdf/2501.12352)
- [Preconditioned DeltaNet 2026](https://arxiv.org/html/2604.21100v1)
- [OSDN Online Preconditioning in Linear Attention](https://arxiv.org/html/2605.13473)
- [Melchior-Wiskott Hebbian Descent 2019](https://arxiv.org/abs/1905.10585)
- [Miconi Metalearning Hebbian Fast Weights 2018](https://arxiv.org/pdf/1807.05076)
- [Miconi Backprop of Hebbian Plasticity 2016](https://arxiv.org/pdf/1609.02228)
- [Hebbian and Gradient Plasticity in Transformers 2025](https://arxiv.org/pdf/2510.21908)
