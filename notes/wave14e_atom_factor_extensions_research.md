# Wave 14e - Adding atom factors to BSC bundles: polarity and temporal

Unbiased math research, 2026-05-19. Question: how do we add a polarity
(truth-conditional) factor and a temporal (time-stamped) factor to the
existing two-factor BSC binding (byte_atom x pos_atom) at N=4096, without
collapsing the capacity-cliff behavior the substrate currently exhibits?

## 1. TL;DR

**Polarity.** Signed scalar epsilon in {-1, +1} multiplying the bound
term: `signed_term = eps * (byte_atom * pos_atom)`. BSC-native
realisation of Kanerva 2009 involutive negation; exact
(eps * eps = 1), zero N overhead, commutes with binding. Does NOT
consume an atom factor. A learned negation atom `n` with `n * n = 1`
is mathematically identical because in BSC every element is self-
inverse -- a global sign is a degenerate negation atom.

**Temporal.** Continuous-time fractional-power encoding `T(t) = g^t`
(Plate 1995, Frady-Kanerva 2018, Frady-Sommer 2021 arxiv:2104.10125).
For BSC: `T(t)[k] = sign(cos(2*pi * phi_k * t + theta_k))` with phi_k
random per-coordinate frequencies (Komer 2019 spatial semantic
pointers). Smooth temporal similarity decay, exact algebraic
composition up to BSC quantisation, tunable bandwidth.

**Capacity.** Frady-Sommer BSC recovery requires `N >> 2*(2B-1)*log V`
where B = summed terms. Polarity absorbs into per-term sign (zero
new B). One timestamp per term also adds zero B. Cleanup dictionary
grows to `256 * 4 * 2 * T_bins`; at T=64 this is 130k -- ~5ms on a
4090. Cliff stays at the current B~200 boundary.

**Minimal tests** (Section 6): polarity test predicted >99% accuracy;
temporal >95%; joint four-factor 85-95% with byte-recovery as the
bottleneck. Section 7 gives the explicit noise floor at B=50.

## 2. Polarity (negation) in HDC: the literature

### 2.1 Plate 1995 HRR: inverse is NOT negation

Plate (1995) defines an approximate inverse `x*` for HRR via circular
correlation: `x* := (x[0], x[N-1], x[N-2], ...)`, satisfying
`x conv x* ~ delta_0`. So `x*` is an *inverse* (undo binding), not a
*negation* (logical NOT). Plate explicitly separates them; HRR has no
clean negation primitive and falls back to a symbolic `not` role atom.

### 2.2 Kanerva 2009 BSC: built-in involution

BSC binding is elementwise XOR (equivalently +/-1 multiplication).
**Every BSC vector is self-inverse**: `x * x = 1`. So a "negation atom"
`n` with `n * n = 1` is *every* vector. Cleanest realisation: global-
sign scalar `eps`, because flipping signs gives the semantic complement
at cosine = -1. **BSC has a built-in involution HRR lacks** -- the
algebraic asymmetry that makes BSC the natural substrate for negation.

### 2.3 Gayler 2003 MAP: sign-flip as unary operator

Gayler treats negation as a unary operator distinct from binding:
`NOT(x) := -x`. Properties:
- `NOT(NOT(x)) = x` (involution)
- `NOT(x * y) = NOT(x) * y = x * NOT(y)` (distributes over binding)
- pre-threshold bundle linear: `sum(NOT(x_i)) = -sum(x_i)`, so
  negation moves cleanly through the pre-threshold accumulator.

This is the formal justification for our design.

### 2.4 Rejected alternative: complement coding (Carpenter 1991)

ART represents x by the pair (x, 1-x). Makes set operations linear but
costs 2x N. Rejected: scalar-sign already gives perfect involution at
zero N cost; complement coding is only needed for subset semantics,
not our use case.

## 3. The signed-bundle approach: polarity math

### 3.1 Encoding

For each fact f_i = (byte_i, pos_i, polarity_i) with
polarity_i in {-1, +1}:

```
term_i = polarity_i * (byte_atom[byte_i] * pos_atom[pos_i])
bundle = sign( sum_i term_i )                     # BSC majority vote
```

### 3.2 Decoding by query "is X at position p"

```
v = bundle * pos_atom[p] * byte_atom[X]           # the test atom
score = mean(v)                                   # in [-1, +1]
```

Predictions:
- If (X, p, +1) is in the bundle: `score -> +1/B` (positive)
- If (X, p, -1) is in the bundle: `score -> -1/B` (negative)
- If (X, p) is not in the bundle: `score -> 0` (centered, std ~ 1/sqrt(N))

So the sign of `score` distinguishes assertion from negation; the
magnitude distinguishes present from absent. **Three-way decision**: a
threshold on `|score|` gates presence; the sign on `score` gates
polarity. This is the entire decoder.

### 3.3 Capacity preservation

Frady-Sommer 2021 bound for B summed terms in BSC:
```
SNR_decode = sqrt(N / (2B - 1))
P_error <= (M-1) * Phi(-SNR_decode)
```

The signed sum doesn't change B (each fact is still one term in the
sum; the sign is absorbed into the term). So **adding polarity does
NOT shift the capacity cliff**. At N=4096 and B=50:
- SNR = sqrt(4096/99) ~ 6.4 sigma
- P_error_byte ~ 255 * Phi(-6.4) ~ 2 * 10^{-8}
- P_error_polarity ~ 1 * Phi(-6.4) ~ 8 * 10^{-11}

Polarity decoding is more reliable than byte decoding because it's a
binary decision (M=2) vs 256-way. The cliff is set by byte decoding.

### 3.4 What can break this

- **Asymmetric polarity prior**: if 90% of facts are assertions, then
  the bundled mean has a positive drift that biases all `score`s up.
  Fix: center the bundle by subtracting the empirical mean before
  decoding. Cheap, exact.
- **Same (byte, pos) asserted AND negated**: this is a logical
  contradiction. The two signed terms cancel: `(+1)*x + (-1)*x = 0`.
  This is theoretically correct -- the substrate represents the
  contradiction as "no information about this fact" -- but if the user
  expects "the latest fact wins", we need a temporal factor (Section
  4) to disambiguate.

## 4. Temporal binding in VSA: the literature

### 4.1 Eliasmith SPA: time as slow position

Eliasmith (2013) encodes time in the Semantic Pointer Architecture as
a slow-changing position atom (Legendre delay network, Voelker-
Eliasmith 2019). Gives smooth time, but the integrator drifts, so
horizons are short (~1 sec of neural time).

### 4.2 Plate 1995 / Frady-Kanerva 2018: fractional-power binding

Define `g^t := IFFT(FFT(g)^t)` (HRR/FHRR), or `exp(i*2*pi*phi*t)`
per-coordinate (FHRR), where phi is the per-coordinate phase angle of
generator g. Properties:
- `g^t1 * g^t2 = g^{t1+t2}` (exact group structure)
- `g^0` = identity (all-ones for BSC)
- `<g^t1, g^t2>` is a sinc-like function of (t1-t2)
- bandwidth tunable via the phi distribution

This is the canonical HDC realisation of continuous time.

### 4.3 Komer 2019 spatial semantic pointers

Extends fractional binding to N-D continuous variables: per axis k,
random phase phi_k; encoding `T_k(t) = exp(i*2*pi*phi_k*t)`. Similarity
kernel width controlled by `var(phi_k)`.

### 4.4 Frady-Sommer 2021 (arxiv:2104.10125)

Generalises: any `f(t) = exp(i*Phi*t)` with random Phi gives a positive-
definite kernel `K(t1, t2)` whose shape is the Fourier transform of
the Phi distribution. Phi ~ Normal -> Gaussian kernel; uniform -> sinc.
This is the rigorous foundation.

### 4.5 BSC realisation

For BSC (+/-1), the fractional encoding becomes:
```
T(t)[k] = sign( cos(2 * pi * phi_k * t + theta_k) )         (per coordinate)
```
with phi_k drawn from a chosen frequency distribution and theta_k from
uniform[0, 2*pi]. Properties:
- `T(t)` is +/-1 valued (BSC-compatible)
- `T(t) * T(s)` is NOT exactly `T(t+s)` (BSC sign loses information)
  but the similarity `<T(t), T(s)>` is well-approximated by
  `(2/pi) * arcsin( cos(2*pi * phi_avg * (t-s)) )` (a low-distortion
  warping of the FHRR sinusoidal similarity, Van Vleck 1966 arcsine
  law for sign-quantised Gaussians)
- For small (t-s) the similarity falls off smoothly; for large (t-s)
  it oscillates around zero with envelope decay set by bandwidth.

### 4.6 Math constraints for stable temporal binding

`f(t) -> {-1, +1}^N` must satisfy:

1. **Boundedness**: f(t)[k] in {-1, +1}. (BSC.)
2. **Stationarity**: E[f(t)[k] * f(s)[k]] depends only on (t-s).
3. **Decorrelation at infinity**: `<f(t), f(s)> -> 0` as |t-s| -> inf,
   requires broadband phi_k spectrum.
4. **Smoothness**: `<f(t), f(t+dt)> > 1 - O(dt)` for small dt,
   requires bounded phi_k spectrum (Nyquist).
5. **Binding commutativity**: holds because BSC binding is abelian.

Joint 3+4: pick `phi_k ~ Uniform[-W, W]`; similarity is
`sinc(2*W*dt)` (FHRR) or `(2/pi)*arcsin(sinc(2*W*dt))` (BSC). Choose
W so expected event spacing equals 1 / (2W).

## 5. Capacity cost of additional factors

### 5.1 Frady-Sommer scaling

BSC recovery requires `N >> 2 * (2B - 1) * log(V)` (Frady-Sommer 2021
eq. 12). Cleanup-dictionary size is `V_total = prod_k V_k`, but only
the **summed term count B** appears in the capacity exponent. A new
factor that does NOT change B is free.

### 5.2 Cost accounting

- byte: V=256, pos: V=4, polarity: V=2 (absorbed into per-term sign,
  zero B), time: V=T_bins (one timestamp per fact, zero B).

B is unchanged by polarity OR single-timestamp time. **Capacity cliff
unchanged.** Cleanup-dictionary at T=64: 256*4*2*64 = 131k -- ~5ms on
a 4090.

### 5.3 Cliff triggers

Cliff IS triggered when bundling across many time bins (B = K_facts).
For the minimal test (50 events at 10 time bins):
- B = 50, SNR = sqrt(4096/99) ~ 6.4 sigma
- Cleanup = 256*4*2*10 = 20480
- Per-query error ~ 20479 * Phi(-6.4) ~ 1.6e-6

Substrate has massive headroom.

### 5.4 The practical limit

At N=4096, the capacity-cliff for byte recovery is at B ~ 355 (from
exp_scaling_bsc.md). With four factors and a 256*4*2*T cleanup
dictionary, the byte recovery sets the floor. **Practical limit:
B <= 200 four-factor facts in one bundle, with T_bins up to ~256 and
arbitrary polarity.** Beyond B=200 the SNR drops below ~4.5 sigma and
the union bound over 256 byte candidates starts to bite.

## 6. The minimal viable tests

### 6.1 Polarity test

Setup:
- N=4096, BSC, K=4 positions.
- Bundle 100 facts: 50 with polarity=+1 and 50 with polarity=-1.
  Byte and position chosen uniformly random WITHOUT collision (so no
  same-byte/same-position contradictions).
- Decode 100 queries: for each fact, ask "is byte_i at pos_i, and
  what polarity?"
- Score: cosine `(bundle * pos_atom[i] * byte_atom[i]).mean()`.
- Predict polarity from sign of score; predict presence from |score|
  > threshold.

Pass criterion: >90% polarity-accuracy on present facts; >95% absent-
fact rejection. **Predicted: 99.5-100% polarity, 99.9% rejection** at
N=4096, B=100. The pass bar is 10x looser than predicted; this test
is safe.

Falsification mode: if polarity accuracy drops below 80%, the
prediction is wrong and the sign-of-mean decoder is inadequate. Likely
cause would be polarity-prior bias; fix by centering the bundle.

### 6.2 Temporal test

Setup:
- N=4096, BSC, K=4 positions.
- Generate temporal atoms via 4.5: phi_k ~ Uniform[-1, +1], 10 time
  bins t in {0, 1, ..., 9}.
- Bundle 50 (event, time) facts: each event has random byte, position,
  and time-bin assignment.
- Decode queries: "what byte was at position p at time t?" via
  `query = bundle * pos_atom[p] * T(t).conj_or_T(-t)`, then cosine
  with byte atoms.

Pass criterion: top-1 byte recovery accuracy >90% on the cued (pos, t)
pair. **Predicted: 95-99% top-1** at B=50.

Falsification mode: if accuracy drops below 70%, the temporal kernel
bandwidth is wrong (W too large -> times are over-orthogonal and
noise dominates; W too small -> adjacent times alias). Re-tune W and
re-run.

### 6.3 Joint test (composition)

Setup as 6.2 but each fact also has polarity in {-1, +1}. Decode:
- byte (top-1 against 256)
- polarity (sign of cosine)
- time (top-1 against 10 bins, by sweeping the t in the query)

Pass criterion: joint top-1 accuracy (byte AND polarity AND time all
correct) >80%. **Predicted: 85-95%**, dominated by byte-recovery
errors which propagate.

## 7. The composition question and the noise floor

### 7.1 Decoding scales additively in noise variance

For a four-factor bundle with B terms, the decoded vector is:
```
v = b * pos_q * byte_q * T(t_q)
  = polarity_q + sum_{i != q} polarity_i * cross_atom_noise_i
```
The noise is a sum of (B-1) random +/-1 terms (after binding all four
factors). The variance is (B-1) per coordinate; the per-coordinate
sign-mean is `polarity_q + N(0, (B-1)/N)`.

So the mean-cosine signal is `1/B` (signal) vs `sqrt((B-1)/N)` (noise
std). **Noise floor**:
```
SNR_db = 20 * log10( (1/B) / sqrt((B-1)/N) )
       = 20 * log10( sqrt(N) / (B * sqrt(B-1)) )
```
For N=4096, B=50: SNR = 20*log10(64 / (50 * 7)) = 20*log10(0.183) =
-15 dB. **That's negative SNR per coordinate**, but the bundle has N
coordinates so the cosine averages over all of them. The effective
SNR after the mean is `sqrt(N) * (1/B) / sqrt(B-1) = 64/350 ~ 0.18`,
giving a cosine of about 0.018 -- well above the chance level of
1/sqrt(N) = 0.0156.

This is the **substrate's noise floor**: at B=50, the cosine for a
correct hit is ~0.018; the cosine for a wrong-byte hit is ~0.016;
the margin is ~0.002. Top-1 recovery still works because we pick the
max over 256 candidates and the max-of-many-Gaussians beats the
margin by sqrt(2*log(256)) ~ 3.3.

### 7.2 The four-factor multiplier

Each additional factor in the binding chain does NOT raise the noise
variance (binding is a unitary operation in expectation). It DOES
raise the cleanup-dictionary size linearly per factor. So the noise
floor is set by B alone; the union-bound prefactor is set by the
product of vocabularies.

**Conclusion**: composition works as long as B stays under ~200 at
N=4096. The four factors do not compound noise; they compound
look-up cost (which is cheap).

### 7.3 What would break composition

- **Non-independent atoms across factors**: if `byte_atom * pos_atom`
  happens to align with `polarity * T(t)`, the cross-term variance
  rises. Mitigation: draw all atom families from independent seeds.
- **Temporal kernel leakage**: if `T(t)` and `T(t+1)` overlap by
  cosine 0.5, then "wrong by one time bin" errors will dominate.
  Mitigation: pick W so that adjacent-time-bin cosine is <0.1.

## 8. Brain analog: episodic memory math

Eichenbaum (2014) describes hippocampal time cells parallel to place
cells; with content-selective lateral entorhinal cells the brain has
at least three orthogonal axes per memory: **where, when, what**.

### 8.1 Multiplicative mapping

The cognitive-map model (Howard-Eichenbaum 2015) gives episodic traces
as `trace = where * when * what * valence`. Valence (positive vs
negative affect, mediated by amygdala-hippocampus coupling) behaves
like polarity. Time cells provide a continuous-time embedding; Howard-
Hasselmo 2015 propose a Laplace-transform time code, which IS the
Frady-Sommer 2021 kernel structure.

### 8.2 Match to BSC

Each axis is a population of cells whose joint activity is an HDC
atom. Binding = conjunctive coding (cells firing only when both
presynaptic populations are active = AND = +/-1 elementwise
multiplication when activity is binary). Polarity = valence
populations (Janak-Tye 2015); a single valence-neuron flip inverts the
emotional sign of the memory -- mathematically our scalar epsilon.
Temporal axis = time-cell sequences (MacDonald 2011) = band-limited
continuous embedding = fractional binding with phi_k realised by
individual time cells' preferred lag.

### 8.3 Why multiplicative is forced

Population codes have fixed size and cannot grow per memory, so
concatenation is impossible. Tensor-product binding (Smolensky 1990,
Plate 1995) is the only known mechanism that produces a bound trace
the same size as each constituent. **Same mathematical constraint
that drives our BSC choice.** Brain and substrate converge on the
same algebra.

## 9. Sources

- Plate, T.A. (1995). "Holographic Reduced Representations." IEEE
  Trans. Neural Networks 6(3):623-641.
- Kanerva, P. (2009). "Hyperdimensional computing: An introduction
  to computing in distributed representation with high-dimensional
  random vectors." Cognitive Computation 1(2):139-159.
- Gayler, R. (2003). "Vector Symbolic Architectures answer
  Jackendoff's challenges for cognitive neuroscience."
  arXiv:cs/0412059.
- Carpenter, G.A., Grossberg, S., Rosen, D. (1991). "Fuzzy ART: An
  adaptive resonance algorithm for rapid, stable classification of
  analog patterns." Neural Networks 4(6):759-771. (Complement coding.)
- Smolensky, P. (1990). "Tensor product variable binding and the
  representation of symbolic structures in connectionist systems."
  Artificial Intelligence 46(1-2):159-216.
- Eliasmith, C. (2013). "How to Build a Brain." Oxford UP.
- Voelker, A.R., Eliasmith, C. (2018). "Improving spiking dynamical
  networks: Accurate delays, higher-order synapses, and time cells."
  Neural Computation 30(3):569-609.
- Frady, E.P., Kanerva, P. (2018). "A theory of sequence indexing and
  working memory in recurrent neural networks." Neural Computation
  30(6):1449-1513.
- Komer, B. (2019). "Biologically Inspired Spatial Representation."
  Univ. of Waterloo PhD thesis. (Spatial semantic pointers.)
- Frady, E.P., Kleyko, D., Kymn, C.J., Olshausen, B.A., Sommer, F.T.
  (2021). "Computing on Functions Using Randomized Vector
  Representations." arXiv:2104.10125.
- Frady, E.P., Sommer, F.T. (2019). "Robust computation with rhythmic
  spike patterns." PNAS 116(36):18050-18059.
- Vaswani, A. et al. (2017). "Attention Is All You Need." NeurIPS.
  (Sinusoidal positional encoding; the FHRR-equivalent kernel.)
- Van Vleck, J.H., Middleton, D. (1966). "The spectrum of clipped
  noise." Proc. IEEE 54(1):2-19. (Arcsine law for sign-quantised
  Gaussians; calibrates BSC vs FHRR similarity.)
- Eichenbaum, H. (2014). "Time cells in the hippocampus: a new
  dimension for mapping memories." Nature Reviews Neuroscience
  15(11):732-744.
- MacDonald, C.J., Lepage, K.Q., Eden, U.T., Eichenbaum, H. (2011).
  "Hippocampal 'time cells' bridge the gap in memory for discontiguous
  events." Neuron 71(4):737-749.
- Howard, M.W., Eichenbaum, H. (2015). "Time and space in the
  hippocampus." Brain Research 1621:345-354.
- Howard, M.W., Hasselmo, M.E., et al. (2015). "A unified mathematical
  framework for coding time, space, and sequences in the hippocampal
  region." J. Neuroscience 35(4):1707-1721. (Laplace-transform time
  code.)
- Janak, P.H., Tye, K.M. (2015). "From circuits to behaviour in the
  amygdala." Nature 517(7534):284-292. (Valence populations.)
- Internal: hd-instrument/notes/exp_scaling_bsc.md (BSC scaling
  exponent alpha = 1.004, k_50% = N/12.2).
- Internal: hd-instrument/notes/wave14b_bundle_noise_theory.md
  (Frady-Sommer noise theory calibration for our N=4096 substrate).
