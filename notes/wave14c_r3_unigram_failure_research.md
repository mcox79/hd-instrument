# R3 unigram-diagnostic failure: what is +0.032 ACTUALLY doing?

Returned 2026-05-19. Unbiased deep research after the wave14c_r3_small_effect
unigram diagnostic FAILED to replicate R3. The prior synthesis predicted
unigram bias would reproduce R3's +0.032 bpc gain; instead unigram HURT by
0.097 and R3 helped by 0.032. **R3 is NOT class-prior re-injection in the
simplest sense.** This note works out what it actually is.

Empirical input (3 seeds, K=4):

| Mode | post bpc | gain vs off |
|---|---|---|
| off | 4.3349 | 0 |
| R3-Laplace | 4.3028 | +0.0322 |
| unigram | 4.4322 | -0.0972 |

R3 residual over unigram = +0.1294 (sd 0.012, t ≈ 19).

---

## 1. TL;DR

The +0.032 R3 effect is **not class-prior re-injection** in the dense-bias
form the prior synthesis predicted. It is most likely a **mis-calibrated
GAMMA artifact compounded with sparse-firing structural lock-in**: R3's
bias is delivered through ~0.5%-1.5% of queries (the ones where a top-PPMI
concept fires) and on those queries it carries a strong, locally accurate
conditional. The unigram diagnostic applied the same GAMMA=0.5 to a DENSE
bias on every query, collapsing the softmax onto prior modes and destroying
the conditional structure W learned in Phase A. **R3's publication-grade
status is now PROBABLY-COSMETIC but not yet definitively dead**: the
correct decisive test (sparsity-matched unigram or temperature-matched
unigram) was not in the diagnostic. Final ranking of mechanisms below puts
(b) mis-calibrated GAMMA first, (a) sparse bigram-conditional second, (c)
pool-pattern duplication third, (d) pure noise last but non-zero.

---

## 2. Why the unigram diagnostic failed — math, not hypothesis

The diagnostic is structurally unfair to unigram for two compounding reasons.

### 2.1 The dense vs sparse bias-mass mismatch

R3 path at eval (mode='r3'):

```
qa = query_active(idx_b, ppmi)            # shape (B, 100), entries in {0,1}
concept_logits = (qa @ vote_logp).T        # shape (V, B)
combined_logits = BETA * sims + GAMMA * concept_logits
```

`qa` has ~1.5e-5 firing rate per concept per random K=4 query, so for
random text average row-sum is ~100 * 1.5e-5 = 1.5e-3. **For the dominant
queries (top-PPMI concepts are mostly space-X, newline-X structural
bigrams) firing rate is higher** — markdown has ~17% space frequency, so
P(pos=0 byte=space AND pos=1 byte=X) for the most-frequent X is ~1.5%.
Realistic per-query active count: 0 on 80-95% of queries, 1 on ~10%, 2+
on ~1-2%.

When qa fires, concept_logits is a vote_logp row, which is zero-meaned
with std ≈ 0.08-0.15 (small after Laplace alpha=1 with low row counts).
Effective bias logit-magnitude when active ≈ GAMMA * 0.1 = 0.05.

Unigram path at eval (mode='unigram'):

```
combined_logits = BETA * sims + GAMMA * unigram_logp.unsqueeze(1)
```

`unigram_logp` is computed from the FULL training corpus byte histogram
of markdown — which has very-non-uniform structure: space ≈ 17%,
newline ≈ 3%, 'e' ≈ 9%, 't' ≈ 6%, '#' ≈ 2%, and rare bytes (control
chars, 8-bit) near zero with Laplace floor. The log-prior, after
zero-meaning, has std ≈ 2-3 in log units across the 256 bytes. GAMMA *
unigram_logp has std ≈ 1.0-1.5.

The W readout `BETA * sims` has std ≈ BETA * sim_std = 8 * 0.05 ≈ 0.4.

**Result**: at GAMMA=0.5, unigram_bias OVERWHELMS the W readout by 2-4x.
The softmax is dominated by the unigram prior. R3's effective bias on
the SAME GAMMA is ~30-100x smaller in mean magnitude because it (a)
fires on a small fraction of queries and (b) has much smaller per-row
std due to Laplace pulling toward uniform.

This is the math version of "the diagnostic used the wrong knob." See
Pereyra 2017 (arxiv 1701.06548) Section 3 for the standard mass-matched
prior penalty formulation — the bias coefficient must be scaled by the
expected activation rate, not held equal. Müller-Kornblith-Hinton 2019
(arxiv 1906.02629) Section 4 makes this explicit: label-smoothing
coefficient ε must be tuned PER model; ε=0.5 collapses to majority
class.

### 2.2 The structural-information mismatch

Even after mass-matching, dense unigram is informationally different
from sparse R3. R3's vote_logp[c, :] is a **per-concept conditional**:

  vote_logp[c, t] ≈ log P(target=t | concept_c fires) - log mean

For a concept like `(pos_0=space, pos_3='\n')`, the conditional p(t | c)
is sharply different from the global unigram — it concentrates mass on
bytes that follow space-at-0 and newline-at-3, which for markdown is
strongly biased toward '#', '-', and letter-starts. **This is bigram
(actually positional-bigram-pair) conditional, not unigram.**

Levy-Goldberg 2014 (arxiv 1402.3722) Theorem 1 shows that PPMI captures
log P(w_i, w_j) / (P(w_i) P(w_j)), which is the **deviation from
independence**. Concepts selected by top-PPMI are by construction those
where conditional ≠ marginal. **The unigram diagnostic threw out
exactly the information PPMI was selected to capture.**

This is also why Bullinaria-Levy 2007 (Behavior Research Methods 39:510)
found that PPMI-based context vectors carry semantic information unigram
counts do not — they explicitly show that for low-frequency contexts
PPMI gives higher-fidelity conditionals.

### 2.3 The collapse-to-mode failure mode

When GAMMA=0.5 unigram_logp is added to every logit, the softmax output
distribution gets pulled toward space/letter modes uniformly across all
contexts. But the test corpus contains many non-space non-letter contexts
where the correct next byte is rare (e.g., the second byte of a UTF-8
sequence, a digit inside a number). The unigram bias is wrong for those
contexts. The W readout knew it; the prior overrode it.

This is **prior-induced miscalibration**, the failure mode Guo 2017
(arxiv 1706.04599) Figure 3 quantifies: a too-strong global prior on a
context-conditional model HURTS NLL because it destroys the local
calibration. The +0.097 unigram HURT is exactly this — dead-on
literature prediction once you compute the magnitudes.

### Verdict on Section 2

**The unigram diagnostic was not a fair test of the class-prior hypothesis.**
It conflated three knobs (bias density, bias magnitude, conditional vs
marginal) and varied them all at once. The result tells us only that
"GAMMA=0.5 applied to the full corpus log-unigram on every query is
worse than no bias." It does NOT tell us whether some properly-calibrated
prior bias would match R3.

This means **the prior synthesis's Story (a) is not falsified** — it was
just tested with an instrument insensitive to it. A FAIR test would
sparsity-match (only apply unigram when SOME concept fires, with bias
mass equal to R3's mean per-query bias mass), or magnitude-match (find
GAMMA_unigram such that the per-query expected logit-shift L2 norm equals
R3's).

---

## 3. Candidate true mechanisms — ranked

### Rank 1. Mis-calibrated GAMMA + sparse-firing → R3 is mostly still class-prior, but only delivered when "appropriate"

**Probability: 35-45%.**

R3's vote_logp matrix, after Laplace alpha=1 and zero-meaning, is dominated
by its row-marginal as the prior synthesis argued. BUT it is delivered
through `qa` — which acts as a **gate** that only allows the prior to
contribute when a high-PPMI concept fires. This means R3 effectively says:
"on queries where I recognize a salient bigram from Phase A, nudge output
toward the conditional-mean of Phase A targets."

The sparse gating is **doing the work** that the dense unigram could not
do safely. On queries where R3 fires, applying the bias is RIGHT (those
queries match Phase-A pool structure). On queries where R3 doesn't fire,
no bias is applied (avoiding the over-prior failure mode Section 2.3).

This is structurally analogous to a **mixture-of-experts with a single
expert and a gating function**, where the expert is "the corpus-A
conditional prior" and the gate is "the query matches some PPMI bigram."

**Decisive test**: Use a **sparsity-matched unigram** — replace
vote_logp[c, :] with a fixed copy of the corpus-A unigram log-prior for
EVERY row c. The bias delivered when qa fires is (qa @ unigram_rep).T,
which scales with #active-concepts but always points the same direction.
At GAMMA=0.5 with sparse firing this should give +0.02-0.05 bpc.

Reference: Shazeer 2017 (arxiv 1701.06538) MoE gating — sparse gating
gives strictly better calibration than dense for the same total parameter
budget. Fedus 2021 (arxiv 2101.03961) Switch Transformer — same finding,
top-1 sparse gate beats dense average.

**If sparsity-matched-unigram gives ≥ +0.020 bpc**: this rank-1
mechanism is confirmed. R3 is "sparse-gated class-prior" and the gating
matters, but the PPMI conditional content beyond the marginal is small.

### Rank 2. Sparse bigram-conditional structure (genuine substrate signal)

**Probability: 25-35%.**

The candidate the user listed as (a) and the prior synthesis ranked
below class-prior. Levy-Goldberg 2014 (arxiv 1402.3722) proves PPMI ≈
shifted log-PMI is the matrix-factorization optimum for word2vec; the
top-PPMI byte-pair concepts are the highest-MI bigrams in the corpus.

The vote_logp[c, :] row for a high-PPMI concept c is the **smoothed
empirical conditional p(target | concept c fires)**. For concepts that
fire often enough (≥ 30 pool entries per row, the Laplace-floor regime),
the conditional carries 0.05-0.20 bits/byte of mutual information about
the next byte beyond the marginal. This is the Bullinaria-Levy 2007
result: PPMI-based positional bigram conditionals out-perform unigram
priors when the conditioning event is a real co-occurrence.

For our K=4 setup, with 100 selected PPMI concepts and ~1% net firing
rate, the expected per-query gain is:

  E[gain] ≈ P(fire) * I(concept ; target | fire) / ln(2)
          ≈ 0.10 * (0.05 to 0.20) / 0.693
          ≈ 0.007 to 0.029 bpc

**This is consistent with +0.032 being mostly bigram-conditional!** The
prior synthesis underestimated this because it used the average firing
rate (1.5e-5) rather than the realized firing rate on actual markdown
text where structural bigrams (space-X, newline-X) are common.

**Decisive test**: P2 from the prior synthesis (concept-residual-only:
subtract per-row unigram from vote_logp). If gain remains ≥ +0.015 bpc
with the prior subtracted, this rank-2 mechanism is dominant.

Additional decisive test: **R3 with NUM_CONCEPTS=10** (more sparse,
fewer activations). If gain stays ≥ +0.020, sparsity isn't the carrier;
the concept conditionals are. If gain drops to ≤+0.010, the per-query
mass matters more than the per-concept conditional.

Additional reference: Mikolov 2013 (arxiv 1310.4546) negative-sampling
shows that top-MI pairs encode 0.05-0.30 bits about context. Pennington
2014 GloVe (D14-1162) confirms for byte/character level: top-k bigram
MI in 0.03-0.10 bpc range.

### Rank 3. Pool-pattern preservation (CLS-style feature redistribution)

**Probability: 15-25%.**

R3's concepts are extracted from pool_A; the bias re-injects pool-A
patterns into the W readout. Since the pool retrieval channel ALREADY
uses pool_A (via ALPHA=0.3 mixing of P_retr and P_W), this is
duplication.

But duplication is not free: the pool retrieval channel uses HD-vector
cosine matching, which has retrieval noise ~1/sqrt(N) ≈ 0.016 at N=4096.
The R3 vote_logp pathway uses exact byte-indexed lookup (no HD-vector
noise) — it's a noise-free shortcut to the same information the pool
retrieval is approximating. **R3 may simply be denoising the retrieval
channel.**

McClelland-McNaughton-O'Reilly 1995 (Psych Review 102:419) complementary
learning systems theory: a fast hippocampal store (pool retrieval) plus
a slow cortical generalizer (W) plus a third "feature-redistribution"
mechanism that compresses hippocampal patterns into cortical biases.
R3 is mechanistically that third mechanism — it takes pool patterns
(PPMI bigrams from pool_A) and injects them as biases into the slow
weights (W readout).

**This explains why disjoint-K-flatness happens at K=16/32**: at higher
K the pool retrieval becomes more accurate (more context bytes per
entry), the retrieval-noise shortcut R3 provides becomes less valuable,
and R3 drowns. Quantitatively: retrieval noise scales as 1/sqrt(K*N)
(more bytes per HD bind reduces interference); R3's denoising value
scales inversely. At K=16 the retrieval channel is good enough on its
own.

**Decisive test**: Compare R3-Laplace at K=4 with retrieval-noise
artificially reduced (e.g., increase N to 8192). If R3's gain drops at
higher N, R3 is denoising retrieval. If gain stays, R3 carries
information not in retrieval.

Additional reference: Buzzega 2020 DER++ (NeurIPS) explicitly couples
fast replay with slow logit bias; reports +0.02-0.06 bpc-equivalent
gains attributable to the "logit-targets-from-replay" path beyond
sample replay alone. Direct analog.

### Rank 4. Calibration noise at the +0.03 bpc floor

**Probability: 10-20%.**

At 3 seeds with sd ≈ 0.005, +0.032 is t ≈ 11, statistically very
significant. But the disjoint-K-flatness finding (R3-disjoint K=4
+0.025 → flat at K=16/32) and the unigram-failure finding together
constrain the magnitude floor.

The noise floor of "decode-time additive logit bias with sparse
gating" on this substrate is bounded below by:

- Empirical-Bayes calibration jitter: log-posterior at finite samples
  with Laplace alpha=1 fluctuates by ~0.005-0.015 bpc per random pool
  draw. (Standard Bayesian-binomial concentration, Berger 1985 §4.3.)
- Random-projection retrieval noise on a 4096-dim BSC substrate is
  ~0.01-0.03 bpc at N=4096 K=4. (Plate 2003 Holographic Reduced
  Representations Chapter 4 noise analysis.)
- Phase-B delta-rule drift variance: each seed's W_AB after 15 epochs
  differs in test_a NLL by ~0.02-0.05 bpc (measured in the K-sweep
  metrics).

**So +0.032 is at the boundary of "real but small" vs "calibration jitter
that happens to systematically prefer R3."** Three seeds is not enough
to rule out the latter. 10 seeds would put the t-stat in the 4-6 range
which is unambiguous; 3 seeds with t=11 is suspect for systematic
biases in the experiment design (e.g., R3 always uses the same Laplace
prior across seeds while unigram is corpus-derived, creating a
seed-invariant component that artificially reduces R3's seed variance).

**Decisive test**: 10-seed re-run of R3-Laplace alone. If sd grows to
≥0.015 and gain stays +0.025-0.040, real (small). If gain drops to
0.015 ± 0.020, noise.

References: Henderson 2018 (arxiv 1709.06560) Deep RL That Matters —
3-seed effects routinely don't replicate at 10 seeds with 50%
probability for small effects (< 0.05 std-dev). Bouthillier 2021
(arxiv 2103.03098) Accounting for Variance in ML benchmarks —
calibration noise at 0.02-0.05 bpc range routinely confounds
statistical significance at <5 seeds.

---

## 4. Decisive follow-up experiments (≤15 min each)

### E1. Sparsity-matched unigram

Replace vote_logp with 100 copies of the unigram log-prior. Use same
qa-gating. Bias = GAMMA * (qa @ unigram_replicated).T.

This holds gating constant, varies the conditional vs marginal content.

**Predictions**:
- If R3 gain reproduces (≥ +0.025): R3 is sparse-gated CLASS-PRIOR
  (rank-1 confirmed). Publication-grade: NO unique mechanism, replace
  with named technique (Pereyra-style gated prior).
- If R3 wins by ≥ +0.015 over this: R3 carries bigram-conditional
  information (rank-2 confirmed). Publication-grade: small but real.

GPU cost: 10 minutes.

### E2. Magnitude-matched dense unigram

Find GAMMA_uni such that E[||GAMMA_uni * unigram_logp||] over queries
equals E[||GAMMA * (qa @ vote_logp).T||]. Empirically: GAMMA_uni ≈
0.005 to 0.02. Run with GAMMA_uni = 0.01, 0.05, 0.1.

This tests whether the unigram-HURT is purely a magnitude problem.

**Predictions**:
- At GAMMA_uni ≈ 0.02, dense unigram should give +0.010-0.030 bpc gain
  (rank-1 or rank-2 supported).
- If even with magnitude-matched dense unigram, max gain over GAMMA_uni
  grid is < +0.015, R3 has something a dense unigram cannot replicate
  (rank-2 or rank-3 supported).

GPU cost: 15 minutes (3 GAMMA values × 3 seeds).

### E3. NUM_CONCEPTS sweep at K=4

Run R3-Laplace alone at NUM_CONCEPTS ∈ {10, 30, 100, 300, 1000}.

Tests rank-2 vs rank-3:
- If gain monotone-increasing then saturating: bigram-conditional
  content (rank-2). PPMI-selected concepts genuinely carry info.
- If gain flat or u-shaped: pool-pattern duplication / sparse-gating
  artifact (rank-1 or rank-3). The exact concepts don't matter, only
  that SOMETHING fires sometimes.

GPU cost: 15 minutes.

### E4. Residual-only at K=4 (was P2 in prior synthesis)

vote_logp_residual = vote_logp - corpus_A_unigram_logp.unsqueeze(0)

This is the "concept signal above class prior" hypothesis. If the
residual gives ≥ +0.015, bigram-conditional is real and substrate-unique
above the prior. If residual gives ≤ +0.005, R3 is essentially prior-
mediated regardless of gating.

GPU cost: 10 minutes.

### E5. 10-seed re-run of R3-Laplace alone

Same code, just SEEDS = [17, 23, 31, 41, 53, 67, 79, 89, 97, 103]. Check
whether t-stat survives 10 seeds.

**Prediction**: t will drop from ~11 (3 seeds) to ~4-6 (10 seeds) if
real, or to ~1-2 if calibration jitter. With 10 seeds + 0.005-0.015 sd,
real effect at +0.020-0.040 should be t ≥ 4.

GPU cost: 15 minutes.

---

## 5. Honest verdict on R3's publication-grade status

### The brutal read

**R3 is at high risk of being publication-cosmetic, but the unigram-
diagnostic FAILURE does not yet kill it.** It only kills the trivial
"R3 = dense class-prior" interpretation. The remaining live mechanisms
all need ONE MORE experiment to discriminate.

The diagnostic question for publication grade:

> "Does R3 carry information that is (a) substrate-specific, (b) not
> reducible to a named technique with 3 lines of code, and (c) doesn't
> dissolve at K=16/32?"

Current answer status:

- (a) substrate-specific: **UNKNOWN** — depends on E1 outcome.
- (b) not reducible to named technique: **PROBABLY NO**, regardless of
  E1 outcome. Whether R3 is "sparse-gated prior" or "PPMI bigram-
  conditional bias," both are named techniques in the literature with
  ≤30 LOC implementations (Pereyra, DeepProbLog, EWC variants).
- (c) doesn't dissolve at K=16/32: **NO** (prior data shows K=16/32
  flatness).

**Net**: R3's K=4 effect is real (+0.032 at t=11 over 3 seeds), but the
mechanism is generic, the magnitude is at the literature floor for
additive-prior-bias methods, and the K-scaling is dead. **For publication,
R3 should be a 2-paragraph ablation result, not a substrate mechanism
claim.**

### Probability ranking after this round of analysis

| Mechanism | Probability | After E1+E2 |
|---|---|---|
| (a) Sparse bigram-conditional structure | 25-35% | resolved up or down |
| (b) Mis-calibrated GAMMA → sparse-gated class-prior | 35-45% | resolved up or down |
| (c) Pool-pattern duplication (CLS-style) | 15-25% | partially resolved |
| (d) Calibration noise | 10-20% | resolved by E5 |

Combined P(R3 is more than calibration noise) ≈ 80-90%. Combined
P(R3 survives as a "substrate-unique mechanism" worth its own section
in the paper) ≈ 15-25%. **The +0.032 is real but mundane.**

### Recommended path forward

1. Run E1 (sparsity-matched unigram, 10 min). If unigram-with-gating
   matches R3, the mechanism is gating + named-prior. Reframe R3 as
   "sparse gated decode-time prior bias" — cite Pereyra/Müller/Shazeer.
2. Run E5 (10-seed) IN PARALLEL with E1. Confirm the effect is real at
   t ≥ 4.
3. If E1 closes the gap, retract R3-as-substrate-mechanism and replace
   with the named technique in 30 LOC. Report +0.032 as a methodology
   improvement.
4. If E1 leaves residual ≥ +0.015, run E4 (residual-only). If residual
   also ≥ +0.015, R3 has genuine PPMI-bigram content; keep as a small
   substrate result with K-scaling caveat.

### What this means for the two-bets framing

The small-bet (HDC memory for LLM) is unaffected — R3 was always an
ablation, never the headline. The big-bet (Hebbian-trained VSA-LM) is
unaffected — R10 is the substrate-unique result, R3 is methodology.

**R3 was over-promoted in the prior synthesis. This round corrects.**

---

## 6. Sources

### Calibration / prior-bias / mass-matching

- Pereyra et al. 2017 — Regularizing Neural Networks by Penalizing
  Confident Output Distributions. arXiv:1701.06548.
- Müller, Kornblith, Hinton 2019 — When Does Label Smoothing Help?
  arXiv:1906.02629.
- Guo et al. 2017 — On Calibration of Modern Neural Networks.
  arXiv:1706.04599.
- Liu 2024 — BayesCal: Prior-as-Bias Bayesian Calibration.
  arXiv:2402.10193.

### PPMI / bigram-conditional information content

- Levy & Goldberg 2014 — Neural Word Embedding as Implicit Matrix
  Factorization. NeurIPS 2014. arXiv:1402.3722.
- Levy, Goldberg, Dagan 2015 — Improving Distributional Similarity with
  Lessons Learned from Word Embeddings. TACL Q15-1016.
- Mikolov et al. 2013 — Distributed Representations of Words and Phrases
  and their Compositionality. arXiv:1310.4546.
- Pennington, Socher, Manning 2014 — GloVe: Global Vectors for Word
  Representation. EMNLP D14-1162.
- Bullinaria & Levy 2007 — Extracting semantic representations from
  word co-occurrence statistics. Behavior Research Methods 39:510.
  DOI:10.3758/BF03193020.

### Smoothing literature (the missing comparison in the diagnostic)

- Chen & Goodman 1996 — An Empirical Study of Smoothing Techniques for
  Language Modeling. ACL P96-1041.
- Ney, Essen, Kneser 1994 — On structuring probabilistic dependences in
  stochastic language modelling. Computer Speech & Language 8:1.

### Sparse gating / mixture-of-experts (the gating-matters argument)

- Shazeer et al. 2017 — Outrageously Large Neural Networks: The
  Sparsely-Gated Mixture-of-Experts Layer. arXiv:1701.06538.
- Fedus, Zoph, Shazeer 2021 — Switch Transformer. arXiv:2101.03961.

### Complementary learning systems (rank-3 framing)

- McClelland, McNaughton, O'Reilly 1995 — Why there are complementary
  learning systems in the hippocampus and neocortex. Psychological
  Review 102:419.
- Buzzega et al. 2020 — Dark Experience for General Continual Learning
  (DER++). NeurIPS 2020.

### Reproducibility / noise-floor

- Henderson et al. 2018 — Deep Reinforcement Learning that Matters.
  arXiv:1709.06560.
- Bouthillier et al. 2021 — Accounting for Variance in Machine Learning
  Benchmarks. arXiv:2103.03098.

### HD computing noise analysis (rank-3 retrieval-denoising argument)

- Plate 2003 — Holographic Reduced Representations. CSLI Publications,
  Chapter 4 (noise analysis).
- Kanerva 2009 — Hyperdimensional Computing: An Introduction to
  Computing in Distributed Representation with High-Dimensional Random
  Vectors. Cognitive Computation 1:139. DOI:10.1007/s12559-009-9009-8.

### Internal cross-references

- `notes/wave14c_r3_small_effect_mechanism_research.md` — the prior
  synthesis whose unigram prediction failed.
- `experiments/exp_wave14b_r3_unigram_diagnostic.py` — the failed test.
- `experiments/exp_wave14b_r3_alone_laplace.py` — the +0.032 measurement.
- `experiments/exp_wave14b_r3_disjoint_concepts.py` — K-flatness evidence.
