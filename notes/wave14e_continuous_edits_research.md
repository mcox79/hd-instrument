# Wave 14e — Continuous (interpolated) edits in BSC bipolar atom space

Date: 2026-05-19
Framing rule: not "is HDC better than X?", but "what does *continuous editing*
require of a substrate, and which math gives it cleanest?" The contribution is
the mapping, not the advocacy.

---

## 1. TL;DR (best continuous-edit method)

The cleanest continuous edit in BSC bipolar space is **per-coordinate
Bernoulli mixing of A and B** (equivalently: linear interpolation of the
pre-sign gaussian codes with sign() applied at inference). Concretely:

```
  mask_i ~ Bernoulli(alpha) independent across i
  a_alpha = mask * B + (1-mask) * A             # one sample, in {-1,+1}^N
  OR
  g_alpha = (1-alpha) * g_A + alpha * g_B       # in R^N, the soft state
  a_alpha_hard = sign(g_alpha)                  # for BSC inference
  a_alpha_soft = tanh(gamma * g_alpha)          # for gradient-friendly use
```

Sections 3-5 show these two routes are equivalent in expectation, and Section
4 shows the naive `sign(alpha*A + (1-alpha)*B)` route FAILS — it is a step
function at alpha=0.5, not continuous.

**FHRR is the strictly cleaner substrate for continuous editing** (continuous
by construction; geodesic interpolation = circular mean of phases) at the cost
of ~8x memory and ~2-4x bind throughput vs BSC at N=4096. Recommendation: stay
BSC at inference, edit via probabilistic mixing or soft latent; switch to FHRR
only if editing becomes a top-3 product pillar.

**Minimal test**: encode "A bound to B", edit B toward C with alpha in {0,
.25, .5, .75, 1}, measure P(target=B) vs P(target=C). Pass if P moves
monotonically and strictly between endpoints at alpha=.5. Probabilistic and
soft-latent both pass; deterministic blend fails.

**Brain mapping**: graded synaptic weights with bounded plasticity (BCM,
soft-bound STDP) plus stochastic vesicle release are precisely soft-bipolar +
Bernoulli mixing. Discrete swap is biologically alien; graded edit is the
plasticity-correct primitive.

---

## 2. FHRR vs BSC for editing

### 2.1 Carriers side-by-side

| Carrier | Atom space | Per-dim cost | Binding | Continuous? |
|---|---|---|---|---|
| BSC | {-1,+1}^N | 1 bit | elementwise * | NO — discrete cube |
| HRR | R^N gaussian | 32 bits | circular conv | YES — Euclidean ball |
| FHRR | (S^1)^N unit modulus | 64 bits complex | complex mul | YES — N-torus |

FHRR (Plate 2003) is the canonical continuous VSA. Editing A toward B is
slerp on each circle factor:

```
  phi_alpha[i] = atan2( (1-alpha) sin(phi_A[i]) + alpha sin(phi_B[i]),
                        (1-alpha) cos(phi_A[i]) + alpha cos(phi_B[i]) )
  atom_alpha[i] = exp(i * phi_alpha[i])
```

Smooth, unit-modulus, recovers A at 0 and B at 1.

### 2.2 Capacity

- BSC at N=4096: k ~ 0.04 N ~ 160 atoms recoverable from a majority-bundled
  sum (Schlegel 2021 Table 2; Kanerva 2009). Bound ~ N/(4 ln M).
- FHRR at N=4096: same scaling N/(4 ln M), constant slightly better (circular
  gaussian noise rather than binomial). Plate 1995 ch. 6.

Verdict: capacity is a wash. Reports of "FHRR has higher capacity" often
conflate carrier with cleanup strategy.

### 2.3 Speed

- BSC bind: 1 XOR or sign-flip per dim.
- FHRR bind: 1 complex multiply = 4 muls + 2 adds per dim.

Wall-clock at N=4096 on GPU: FHRR is bandwidth-bound, so ~2-4x BSC for
bind/bundle, equal for similarity (dot product either way). Memory cost is
8x. Important when atom pool is tens of thousands.

### 2.4 Editing in each substrate

- **BSC**: requires relaxation (Section 3), blending (Section 4), or
  probabilistic mixing (Section 5). Atom cannot smoothly move without leaving
  the cube.
- **FHRR**: continuous by construction. Slerp, circular mean, weighted phase
  combination are all geometrically meaningful. *Continuous editing is the
  FHRR home turf.*

### 2.5 Recommendation table

| Need | Choose |
|---|---|
| Max throughput at small N, fixed-arity atoms | BSC |
| Continuous editing as first-class op | **FHRR** |
| Differentiable training in atom space | FHRR or soft-BSC |
| Compact storage of large atom pool | BSC |
| Audit/decompose a bundle exactly | BSC popcount, FHRR Re(<,>): tie |
| Sequential edits with rollback | BSC marginal — discrete waypoints |

---

## 3. Soft bipolar relaxation: tanh(gamma * x)

### 3.1 The map

BSC atoms are `a = sign(g)`, `g ~ N(0, I_N)`. The soft relaxation keeps `g` and
applies `tanh(gamma * g)` instead. At gamma -> inf, recovers BSC; at finite
gamma, interior of the cube and differentiable. This is the **straight-through
estimator** (Bengio 2013) and equivalently the **mean-field Ising** approx
(`<sigma> = tanh(beta h)`).

### 3.2 Effect on substrate operations

- Cross-similarity of two independent soft atoms: `E[tanh(g) tanh(h)] = 0`,
  same as BSC.
- Self-norm: `E[tanh^2(gamma g)]` shrinks at small gamma, asymptotes to 1.
  Orientations preserved; magnitudes shrink. This cancels in cosine.
- Bundling: K-atom sum has variance K * E[tanh^2(gamma g)] per coord; SNR of
  unbinding scales the same.
- Binding: elementwise mul still works in [-1,1]^N; bind-unbind not exact at
  finite gamma but ~exact when |a_i| ~ 1.

### 3.3 Training and inference

- Training: yes, gradients flow through tanh. BinaryConnect (Courbariaux 2015),
  HD-Glove (Yerxa 2024) train this way and binarise at deploy.
- Inference: yes, but resonator-network (Frady-Sommer 2020) contractivity is
  lost at small gamma. Practically: gamma >= ~3 keeps resonator convergent.

### 3.4 Gamma schedule

Anneal: small gamma early for gradient flow, gamma -> inf at deploy. Same
recipe as Gumbel-softmax (Maddison 2017, Jang 2017). For *editing alone* (no
training), hold gamma at deploy level (~10-20 at N=4096) and only relax for
the edit:

```
  edit_step(bundle, A, B, alpha):
      g_alpha = (1-alpha) * g_A + alpha * g_B
      a_alpha = sign(g_alpha)               # for BSC inference
      return rebind(bundle, A -> a_alpha)
```

### 3.5 Brain analog

`tanh(gamma * .)` is the sigmoidal f-I curve of a rate-coded neuron. Soft-to-
hard transition is the rate-vs-spike representation tradeoff.

---

## 4. Atom blending: sign(alpha * A + (1-alpha) * B)

### 4.1 The geometry

`a_alpha = sign(alpha * A + (1-alpha) * B)` is coordinate-wise majority vote.
For independent random A, B in {-1,+1}^N:

- Coordinates where A_i = B_i: fixed under blending.
- Coordinates where A_i != B_i: `a_alpha,i = B_i` for alpha < 0.5,
  `= A_i` for alpha > 0.5, degenerate at 0.5.

Therefore `a_alpha = B` exactly for alpha in [0, 0.5) and `= A` exactly for
(0.5, 1]. **Step function — NOT continuous.** Section 6 test would FAIL.

### 4.2 The fix: noisy blending

Add per-coordinate noise before sign:

```
  a_alpha,i = sign( alpha * A_i + (1-alpha) * B_i + eps_i ),  eps_i ~ N(0,sigma^2)
```

Now `P(a_alpha,i = A_i | A_i != B_i) = Phi((alpha-0.5)*2/sigma)`, continuous in
alpha. This is equivalent to Bernoulli mixing (Section 5) with mixing
probability Phi(.).

**Central trap**: deterministic sign-of-convex-combination is a discrete jump.
Continuous editing requires *either* stochasticity *or* a soft latent.

---

## 5. Probabilistic editing: Bernoulli mixing

### 5.1 Setup

```
  mask_i ~ Bernoulli(alpha) iid
  a_alpha = mask * B + (1 - mask) * A    # one BSC sample
```

This is the **Hamming-space barycentric interpolation**: at alpha=0.5, the
expected Hamming distance from A is N/2 * P(A_i != B_i) ~ N/4 (random A, B).

### 5.2 Properties

- `E[similarity(a_alpha, X)] = (1-alpha) * sim(A,X) + alpha * sim(B,X)` —
  **linear in alpha**, for any X. So downstream readout that is linear in
  similarity (ridge cleanup, near-linear softmax) gives linear-in-alpha
  predictions. Exactly the property we want.
- `E[d_H(a_alpha, A)] = alpha * d_H(A, B)` — linear.
- Variance: O(sqrt(N)) per coord total in d_H; bundle response variance
  O(1/sqrt(N)). Negligible at N=4096.
- Realisability: one mask draw = one concrete BSC atom. Can freeze for
  reproducibility or resample for ensemble averaging.

### 5.3 The right math

Probabilistic editing is a **convex combination in the simplex of
distributions over BSC atoms**, projected to a sample. Track the mean:

```
  mu_i = E[a_i] = 2*P(a_i = +1) - 1,  mu in [-1,+1]^N
  mu_alpha = (1-alpha) * mu_A + alpha * mu_B
```

Similarity uses `mu` directly (it is the expected cosine). Realise to hard BSC
when needed via mask sample or `sign(mu)`.

**Soft-bipolar = mean of Bernoulli mixture.** Section 3 and Section 5 are the
same object derived from two directions: `mu_i = tanh(gamma * g_i)` for an
implicit gamma identified by the inverse-tanh of the desired mean.

### 5.4 Why prefer the probabilistic framing

1. Literal convex combination in a meaningful space (probability simplex);
   measure-theoretic interpolation (Wasserstein on Hamming cube) applies.
2. Substrate stays interpretable: a "fact" is still a BSC atom or a
   distribution over BSC atoms.
3. Maps cleanly onto stochastic synapses: graded vesicle release probability
   (Maass-Zador 1999) is per-coord Bernoulli.

---

## 6. Minimal viable test

### 6.1 Protocol

```
N=4096, R=64 seeds, alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
A, B, C iid random BSC.
Encode: bundle = bind(A, B) + (filler bindings)
Edit B -> B_alpha by Method M:
  Method P (Bernoulli):   B_alpha = mask*C + (1-mask)*B, mask ~ Bern(alpha)
  Method S (soft latent): B_alpha = sign((1-alpha)*g_B + alpha*g_C)
  Method D (det. blend):  B_alpha = sign((1-alpha)*B + alpha*C)
Apply: bundle' = bundle - bind(A,B) + bind(A,B_alpha)
Decode: y = unbind(bundle', A)
Compute: P(target=B), P(target=C) via softmax over {B,C} at temperature beta.
Average over R seeds.
```

### 6.2 Pass criterion

P(target=B) and P(target=C) monotonic in alpha, crossing near alpha=0.5,
strictly between endpoints at alpha=0.5.

### 6.3 Expected outcomes

- Method P: PASS. Linear interpolation of expected similarity.
- Method S: PASS. Equivalent to Method P after one mask realisation in
  expectation.
- Method D: FAIL. Step function at 0.5 (Section 4.1).

### 6.4 Cost

~10 min GPU at N=4096, R=64, 100 fact bundles. Implement as
`experiments/exp_wave14e_continuous_edit_pilot.py`.

### 6.5 Diagnostics

- Hamming d_H(B_alpha, B), d_H(B_alpha, C) per alpha. Method P: ~ alpha*d_H(B,C)
  and (1-alpha)*d_H(B,C). Method D: 0 or large jumps.
- Slope of P(target=C) vs alpha. Method P: matches analytic
  `2*alpha*d_H(B,C)/N - d_H(B,C)/N`.
- Variance across mask draws at alpha=0.5: O(1/sqrt(N)) in readout.

---

## 7. Interpolation theory

### 7.1 Hamming-space geodesic

Hamming geodesic on {-1,+1}^N: path of d_H(A,B)+1 vertices obtained by
flipping disagreement coords in some order. Natural continuous param:
probabilistically flip with prob alpha. Exactly the Bernoulli edit of Sec 5.
E[d_H] linear in alpha. Frechet mean on Hamming cube.

### 7.2 Barycentric

Barycentric `sum_k beta_k A_k` is interior to the cube. Must project (sign())
or sample (Bernoulli). Both routes give Sec 5.

### 7.3 Slerp on the torus

T^N = (S^1)^N is Riemannian-flat. Geodesic between phi_A, phi_B is per-circle
slerp; length = sum_i d_circle(phi_A,i, phi_B,i). Cleanest atom-interpolation
math of any VSA. FHRR's home.

### 7.4 If you must stay in the cube

Only continuous variant: random walk on the geodesic, Markov-chain
parameterised. Operationally identical to Bernoulli mixing. No other choice
respects cube geometry.

### 7.5 Verdict

| Method | Closed form | Smooth in alpha | In-cube | Differentiable |
|---|---|---|---|---|
| Bernoulli (Sec 5) | yes | in expectation | yes | no (needs surrogate) |
| FHRR slerp (Sec 2) | yes | yes | yes | yes |
| Soft-bipolar tanh (Sec 3) | yes | yes | interior only | yes |
| Det. blend (Sec 4) | yes | NO step at .5 | yes | no |

Cleanest BSC option: Bernoulli (= soft-bipolar in expectation). Cleanest
across VSAs: FHRR slerp.

---

## 8. Product implications

Smooth editing unlocks capabilities the current discrete-swap substrate lacks:

1. **Gradient-style updates without binary commits.** Hold partial edit
   (alpha=0.3), refine from feedback. Online-SGD analog on a frozen substrate.
2. **Mistake correction.** Edit toward B with alpha=1, regress on held-out
   probe, roll back to alpha=0.5. Discrete edits have only 0 or 1.
3. **A/B testing.** Two users see alpha=0.2 and 0.8 of the same edit; pick
   better setting from telemetry. Discrete supports only (A,B) and (B,A).
4. **Audit-trail granularity.** "Edit applied at strength 0.4" richer than
   binary for legal/regulatory inspection (cf. wave14d targeted-erasure).
5. **Soft delete.** alpha drifting from 0 to 1 over time = the substrate
   analog of forgetting (Section 9). Plasticity-correct.

Tradeoff: keep the soft state (or alpha, or mask) somewhere — ~N extra floats
per edited atom. Not an obstacle at our scales.

---

## 9. Brain analog: synaptic plasticity

### 9.1 Mismatch with discrete swaps

Discrete byte-atom swap = all-or-none learning. Biologically alien: synaptic
weights in cortex are graded, with LTP/LTD modifying weights ~10-50% per
stimulus train (Bi-Poo 1998 STDP; Markram 1997; Bliss-Lomo 1973 LTP).

### 9.2 Math of synaptic plasticity

```
  dw/dt = eta * f(pre, post, w) - lambda * w
```

with `f` = Hebb (`pre*post`), STDP (`pre(t)*post(t+delta)`), or BCM
(`post*(post-theta)*pre`). Plus soft-bound homeostasis (Gerstner 2002):
`dw/dt = eta * f * (w_max - w) - lambda * (w - w_min)`. **Structurally
identical to soft-bipolar tanh saturation.**

Stochastic synapses (vesicle release prob p) = per-coord Bernoulli (Sec 5).
Maass-Zador 1999: stochastic synapses with graded release prob ~ deterministic
synapses with weight = expected release.

### 9.3 Mapping table

| Substrate | Brain |
|---|---|
| BSC atom ±1 | thresholded synapse state |
| Soft atom tanh(gamma*g) | graded synaptic weight |
| Bernoulli mixing | stochastic vesicle release |
| alpha | learning rate * coincidence |
| Edit rollback at alpha=0.5 | LTD reversing partial LTP |
| Anneal gamma -> inf | maturation / consolidation |

The substrate's edit primitive *should* be plasticity-like (graded, bounded,
reversible), not engineering-like (swap-in/swap-out). Soft-bipolar + Bernoulli
is the neuromodulator-free version of LTP/LTD.

### 9.4 Neuromodulators as alpha schedulers

In cortex, dopamine/acetylcholine gate plasticity by setting effective
learning rate. Substrate analog: context-conditioned alpha. Same edit applied
at alpha=0.2 in one context, alpha=0.8 in another — how the brain handles
reversal learning. Out of scope for 14e; natural next step.

---

## 10. Sources

- **Plate 1995, 2003** — HRR/FHRR canonical references.
- **Kanerva 2009** — "Hyperdimensional Computing: An Introduction" (Cognitive
  Computation). BSC capacity and bundling theory.
- **Schlegel et al. 2021** — "A comparison of vector symbolic architectures"
  (AI Review). Capacity tables BSC/FHRR/HRR.
- **Frady & Sommer 2020** — Resonator networks; convergence depends on
  contractive binding (matters for soft-bipolar at small gamma).
- **Bengio 2013** — Straight-through estimator for stochastic neurons.
- **Courbariaux 2015 (BinaryConnect); Hubara 2016 (BNN)** — soft-to-hard
  sigmoid relaxation for training binary nets.
- **Maddison 2017, Jang 2017** — Concrete / Gumbel-softmax: continuous
  relaxation of categorical with annealing.
- **Bi & Poo 1998** — STDP in hippocampal cultures (continuous weight change).
- **Markram 1997** — STDP windowing.
- **Gerstner & Kistler 2002** — Spiking Neuron Models (soft-bound plasticity).
- **Bienenstock-Cooper-Munro 1982** — BCM rule (bounded plasticity).
- **Maass & Zador 1999** — Stochastic synapses ~ graded weights.
- **Yerxa et al. 2024** — HD-Glove: gradient-trained HD atoms, binarised at
  deploy. Soft-bipolar validation.
- **Hase 2023** — "But Is It Really In Rome?" (motivates continuous edits).
- **Meng 2022 (ROME/MEMIT)** — discrete edit failure modes.

---

## 11. Recommended next steps

1. `experiments/exp_wave14e_continuous_edit_pilot.py` with Methods P, S, D
   from Sec 6. ~30 min coding + ~10 min GPU.
2. If Method P passes: add `hdlab/edit.py` with `probabilistic_edit(atom_A,
   atom_B, alpha, generator) -> atom`. One screen of code.
3. For differentiable edit-search later: add `soft_atom(g, gamma)`; route
   inference through `tanh(gamma*g)` with gamma scheduled by config.
4. Park FHRR-substrate switch as a Wave 15 decision: right long-run carrier
   *if* continuous editing becomes a product pillar, not before.
5. Frame product page in plasticity language ("graded edits", "soft
   consolidation", "soft delete by decay"), not engineering language
   ("alpha-blend"). Durable framing per brain-inspired feedback.
