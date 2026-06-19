# Noise-resonator failure — research synthesis

Returned 2026-05-19. Unbiased diagnosis of why my "Langenegger 2024"
noise-injection rescue produced 13.3% recovery at K=2048 (where
baseline gives 100%).

## TL;DR

**I misunderstood the rescue.** Karunaratne-Langenegger et al. 2024
(arXiv:2412.00354) describes **three** variants:
- BRN (baseline): no noise, capacity ~10^5 at F=2
- **IMF** (In-Memory Factorizer): iterative additive Gaussian on
  similarity vector at sigma=0.008 CONSTANT, no annealing. **F>=3 winner.**
- **ACF** (Asymmetric Codebook Factorizer): bit-flip mask applied ONCE
  at initialization to reconstruction codebook only.
  **F=2 winner (50x capacity).**

I implemented IMF-style with FIVE bugs simultaneously:
1. Wrong variant (IMF instead of ACF for F=2)
2. Noise scale 12.5x too large (0.1 vs paper's 0.008)
3. Wrong activation (tanh instead of hard threshold)
4. Invented annealing the paper doesn't use (sigma is CONSTANT)
5. Wrong injection point (scores vs codebook bit-flip)

## Why K=2048 collapsed

At K/N=0.5 baseline gives 100% recovery (clean signal, distractor
margin ~1/sqrt(N) = 0.016). My sigma=0.1 noise is ~6x the inter-distractor
spacing. Drowning the signal entirely. Then `tanh(2*noise)` produces
random updates and the resonator never converges.

## ACF mechanism for F=2

- Build pos_atoms normally for the associative-search codebook A
- Build a separate **reconstruction codebook** `A_rc = A · BFM(r)` where
  BFM is a Bernoulli bit-flip mask with sparsity r in {0.005, 0.01, 0.1}
- In the resonator iteration:
  - Use A for the similarity scoring (`scores = A @ proj / N`)
  - Use A_rc for the reconstruction step (`e_new = A_rc^T @ activation(scores)`)
- Asymmetry permanently breaks codebook symmetry; spurious fixed points
  vanish

**Hard threshold activation** (not tanh): `f(alpha)[i] = alpha[i] if
alpha[i] > T else 0`. T tuned together with bit-flip sparsity r.

## Five rescues ranked

| Rank | Variant | Prediction |
|---|---|---|
| **(c)** | **ACF: init bit-flip on pos_atoms reconstruction path, hard-threshold activation, no annealing, no iter-noise** | Most likely to deliver 50x gain at F=2. Literal paper protocol. |
| (a) | Iterative additive noise at sigma=0.008 constant, keep tanh | Recovers baseline; will NOT show 50x (wrong variant for F=2) |
| (b) | Noise on post-sign estimates | Off-protocol, random walk, worse than (a) |
| (d) | Cosine/exp annealing at sigma=0.008 | Marginal; annealing isn't the mechanism |
| (e) | Multiplicative noise | No literature support |

## Honest bottom line

The K-cliff theory agent overstated by collapsing ACF and IMF into
"iterative noise injection." The 50x gain IS real for F=2 but only via
ACF (asymmetric codebook), not iterative noise. My implementation
tested neither cleanly.

Re-run as ACF before declaring noise-resonators dead. Until then, the
K-cliff result (cliff at K/N=0.55-0.56 for baseline F=2 resonator) is
real and matches Frady-Sommer published envelope. The 50x rescue is
not yet falsified — it just wasn't implemented.

## Sources

- [On the Role of Noise in Factorizers (arXiv:2412.00354)](https://arxiv.org/html/2412.00354v1)
- [Hersche-Langenegger Factorizers for sparse block codes 2025](https://journals.sagepub.com/doi/10.3233/NAI-240713)
- [Frady-Kent Resonator Networks 1 (2020)](https://rctn.org/bruno/papers/resonator1.pdf)
- [Resonator Networks paper (arXiv:1906.11684)](https://arxiv.org/abs/1906.11684)
