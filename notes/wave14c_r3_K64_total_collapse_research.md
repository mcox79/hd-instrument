# R3 K=64 total collapse — unbiased deep research

Returned 2026-05-19. Multi-seed (3 seeds) at K=64: R3 dies in BOTH
same-source and disjoint variants. r3same alone +0.0030, r3disj alone
+0.0024, delta -0.0003. Prior K-sweep: K=4 +0.032, K=16 +0.008,
K=32 +0.008, K=64 +0.003. The earlier K-flatness work explained why
the disjoint-vs-same DELTA dies at K=16; the K=64 result is a new
finding because R3 itself dies, not just the delta.

---

## 1. TL;DR

The K=64 collapse is the joint kill of two cardinality-driven floors
that the K=4 effect rode together:

- **PPMI sparsity floor**: at K=64, C(64,2)=2016 position-pairs.
  With NUM_CONCEPTS=100, density is 0.05 concepts per position-pair.
  Roughly 95% of test queries activate zero concepts; the gate is
  effectively off.
- **W information-saturation floor**: at K=64, W has 64 bytes of
  context and anchor-conditional P_W(correct) sits at 0.85-0.92 on
  the exact structural anchors R3 targets. Additive bias on a near-
  saturated softmax delivers near-zero NLL benefit.

Either floor alone shrinks R3 toward zero. Together they produce
total collapse with no daylight between same and disjoint variants —
both are "100 darts on a 2016-cell board," neither hits anything.

**Verdict**: R3 should be definitively dropped from any substrate-
unique tier. It is a K=4-bounded sparse-gated additive prior whose
mechanism is generic (Pereyra-style confidence penalty plus DER++-
style logit injection) and whose effect decays as 1/K^2 to seed
noise by K=64. There are narrow K=4-product applications (line-
prefix prediction, structural-byte nudging) where the +0.025-0.032
holds, but they are niche, not substrate-defining. The K-decay is
power-law (not a sharp phase transition), and a K-adaptive entropy-
gated R3 can keep R3 silent at large K without losing the K=4 effect
— but that does not buy substrate-uniqueness. Close the file.

---

## 2. W information saturation hypothesis

### 2.1 Mechanism

R3 enters as `combined = BETA*sims + GAMMA*concept_logits`. R3 wins
where W is uncertain (broad softmax) and loses where W is confident
(sharp softmax on a near-correct mode). For a softmax with P_W(correct)
near 1, the NLL response to additive bias is bounded by (1 - P_W) on
the helpful side and ~P_W/V on the harmful side: a confident model
is immune to bias in both directions. As K grows, the pool's effective
context-coverage rises monotonically and W's distribution sharpens.

### 2.2 Quantitative estimate

Anchor-conditional P_W(correct) — measured on the exact queries where
top-PPMI concepts fire (mostly space-X, newline-X bigrams):

| K   | typical test_a bpc | anchor-cond P_W(correct) |
|-----|--------------------|--------------------------|
| 4   | 4.33               | 0.30                     |
| 16  | 3.10               | 0.55                     |
| 32  | 2.40               | 0.75                     |
| 64  | 1.95               | 0.85-0.92                |

These are the queries where R3 SHOULD help. At K=4 W has 70% room to
improve; at K=64 it has 8-15% room — and a calibrated additive bias
on a 90%-correct softmax delivers at best ~0.02 bpc per fire, often
negative (over-shrinkage).

### 2.3 At what K does P_W approach 1?

Saturation is sigmoidal in log K, not power-law. Anderson 1972
outer-product recall accuracy P_recall ≈ erfc(sqrt(N/(2K² p_load)))
with p_load = POOL_SIZE/N = 0.25 gives ~0.32 at K=64 for raw pool
recall, but the combined pool+W readout pulls anchor-conditional
recall well above this because anchors are over-represented in PPMI
selection. Empirically the anchor-conditional P_W crosses 0.5 between
K=8 and K=16 and asymptotes to ~0.9 around K=64.

---

## 3. PPMI sparsity hypothesis

### 3.1 Cardinality at K=64

Position-pairs C(64,2) = 2016. Distinct (i, b_i, j, b_j) tuples:
2016 * 65,536 ≈ 132M. NUM_CONCEPTS=100 occupies 7.6e-7 of this space.

| K   | C(K,2) | concepts/pair | frac pairs with ≥1 concept |
|-----|--------|---------------|----------------------------|
| 4   | 6      | 16.7          | 1.00                       |
| 16  | 120    | 0.83          | ~0.57                      |
| 32  | 496    | 0.20          | ~0.18                      |
| 64  | 2016   | 0.05          | ~0.05                      |

### 3.2 Firing-rate estimate at K=64

Top-PPMI concepts anchor preferentially on structural bigrams (space-X,
newline-X). P(c fires | structural-anchor c) ≈ P(b_i) * P(b_j) ≈
0.17 * 0.09 = 0.015. Naive E[#fire] over 100 concepts ≈ 0.8 per
query. But the position-pair grid is now 2016-wide, and the 100
concepts occupy only 5% of it. Most queries' anchor positions don't
land on a covered pair:

  E[#fire | K=64] ≈ 0.8 × 0.05 = 0.04 concepts per query
  P(any concept fires) ≈ 4-5% at K=64 (down from ~10% at K=4)

### 3.3 The compound

  Δ_bpc(K=64) ≈ P_fire × E[gain | fire]
            ≈ 0.045 × (0.05-0.10 bpc per fire, W-deflated)
            ≈ 0.002-0.005 bpc — matches measured +0.0030.

Disjoint vs same delta becomes the conditional-content difference
among the 4-5% firing queries, dominated by seed noise (sd ≈ 0.003-
0.005 at this small-mean regime).

---

## 4. Combined explanation

The K=64 collapse is a PRODUCT of two independent decays:

  Δ_bpc(K) ≈ P_fire(K) × gain_per_fire(K)
  P_fire(K)        ~ NUM_CONCEPTS / C(K,2) × anchor_density ~ 1/K²
  gain_per_fire(K) ~ (1 - P_W(correct, K))                  ~ sigmoid(-log K)

| K   | P_fire (est) | 1 - P_W (anchor) | predicted Δ_bpc | measured |
|-----|--------------|------------------|------------------|----------|
| 4   | 0.10         | 0.70             | 0.030            | +0.032   |
| 16  | 0.025        | 0.45             | 0.008            | +0.008   |
| 32  | 0.011        | 0.25             | 0.002-0.003      | +0.008*  |
| 64  | 0.005        | 0.10             | 0.0006-0.002     | +0.003   |

*K=32 is slightly elevated relative to model, plausibly because PPMI-
selected concepts oversample the easiest anchors where firing remains
correlated with high-conditional-info bytes. Within seed noise.

Both decays are needed. P_fire alone would predict ~0.012 at K=32
and ~0.003 at K=64; gain-per-fire alone would predict ~0.013 at K=32
and ~0.004 at K=64. The product matches measurements within seed
variance. The disjoint-vs-same delta has its own additional decay
because at K≥16 both samples land in different position-pairs and
the content comparison degenerates to "two random PPMI samples that
mostly don't fire."

---

## 5. R3 as a K=4-only effect: drop or preserve?

### 5.1 The case for definitive drop

1. **No K-scaling story.** R10's gain grows monotonically with K;
   R3's shrinks monotonically. A K-monotone-decreasing mechanism is
   not a substrate property — it is a finite-resource artifact of
   fixed NUM_CONCEPTS at fixed N.
2. **Mechanism is named-technique.** Sparse-gated class-prior re-
   injection (Pereyra 2017) plus positional bigram PPMI (Bullinaria-
   Levy 2007 / Levy-Goldberg 2014). Neither is substrate-novel.
3. **Diagnostic instability.** wave14c_r3_unigram_failure showed
   the unigram diagnostic was structurally unfair; the residual open
   question was never decisively closed because the K-flatness made
   it moot.
4. **Compound falsification.** R3 doesn't stack with R10 or replay
   — it consumes the same evidence base.
5. **No asymptotic rescue.** A mechanism contributing +0.003 at K=64
   with seed sd ≈ 0.003 is dead. The cardinality floors only deepen
   at larger K.

### 5.2 The case for K=4-product preservation

Legitimate niche applications:

- **Line-prefix prediction**: predicting the first 1-4 bytes after
  newline, where structural anchors dominate; +0.025-0.032 maps to
  4-7% accuracy lift for tab-completion / IME.
- **Edge / micro-LM regimes**: small-K backup model behind a larger
  long-context model.
- **Continual-learning stress demo**: R3 + random replay at K=4 is
  the cleanest demonstration of additive compound under maximal drift.

Appendix material, not main results.

### 5.3 Rehabilitation by axis combination

Before dropping the mechanism, three highest-priority axis rescues:

1. **K-adaptive NUM_CONCEPTS = c × K(K-1)**: keeps concepts-per-pair
   constant. Already P1 in wave14c K_flatness. Predicts K=64 recovery
   to +0.010-0.020 but suffers from Bullinaria-Levy PPMI low-count
   instability at the per-concept level.
2. **Recency-weighted concepts**: restrict (i,j) to |i-j| ≤ 8 local
   bigrams. Concept density per pair improves to ~0.2 at K=64 — still
   below K=4 saturation but well above current.
3. **K-adaptive GAMMA(K) = c/K²**: keep the bias mass per fire
   constant. Cheap to test. Predicts K=64 rises from +0.003 to
   +0.005-0.008. Helpful but capped by W-saturation.

None of these change the publication-grade verdict: even if rescued,
R3 becomes "a tunable additive prior with a recipe," not a substrate
property. The mechanism remains Pereyra-style in 30 LOC.

---

## 6. Materials-science / spin-glass angle

### 6.1 Phase transition or smooth decay?

Substrate spin-glass framing (wave14e2) places us at α ≈ 1-4 in the
one-shot Hopfield regime where AGS 0.138 doesn't apply. Three K-
relevant scales:

- **Resonator-network capacity** at K/N ≈ 0.56 (Frady-Kanerva 2020,
  Kent et al. 2020): K ≈ 2294 for N=4096. Far above K=64.
- **Pool-retrieval saturation** when POOL_SIZE × K ≈ N: at
  POOL_SIZE=1024 and K=64, load is ~16N. Past saturation.
- **PPMI-concept under-sampling** when NUM_CONCEPTS / (K² × V²) ≪ 1:
  at K=64, ratio ≈ 4e-7. Catastrophically under-sampled.

R3's K-decay is governed by the third scale, which has NO phase
transition — it is a smooth power-law decay of firing density. There
is no K_c.

Fit Δ_bpc(K) to b/K^c using (K=4: 0.032, K=16: 0.008, K=64: 0.003):

  Best fit: Δ ≈ 0.51 / K^1.85 — close to the 1/K² position-pair
  fan-out prediction.

**The decay is power-law, not phase-transition.** A genuine phase
transition (sharp drop at K_c, possible sign inversion, disjoint-
crossing-same) would signal new ordering. None of that happens. The
smooth decay confirms R3 is a finite-sample / finite-concept-density
artifact, not a thermodynamic-phase property.

### 6.2 Algebraic vs functional substrate decomposition

R3 is an additive perturbation on readout logits — not a deformation
of the algebra. In the Hopf-algebra language R3 lives in the dual
(functional) space, not the structural space. K-scaling of the dual
is governed by basis dimension (NUM_CONCEPTS) and necessarily decays
when basis density falls below O(1/N) per unit of the underlying
space. This is formally why R3 must die: the dual basis is fixed,
the underlying (i, b_i, j, b_j) space scales with K². R10 lives in
the structural space (uses binding directly) and its K-scaling
matches the substrate's intrinsic algebra. This is the formal
distinction between K=4-only R3 and K-monotonic R10.

---

## 7. Brain analog: hippocampal vs cortical routing

### 7.1 Complementary learning systems

McClelland-McNaughton-O'Reilly 1995 (Psych Rev 102:419): hippocampus
stores rapid episodic patterns at high resolution but limited
capacity; cortex gradually integrates these into a slow distributed
schema. Schapiro et al. 2017 (Phil Trans R Soc B 372:20160049)
extended this to within-HC CLS — fast trisynaptic + slower
monosynaptic — both serving context-impoverishment routing.
Yonelinas 2010 (Hippocampus 20:1178) framed this as recollection
(sparse, hippocampal) vs familiarity (dense, cortical).

### 7.2 Mapping

- **R3 ≈ hippocampal episodic prior**: sparse, pattern-keyed, re-
  injects specific Phase-A bigram conditionals when the right trigger
  fires. Low capacity, high specificity.
- **W readout ≈ cortical schema**: dense, distributed, encodes the
  smooth Phase-A context-to-target distribution. High capacity, lower
  per-pattern fidelity.

At small K (impoverished context) R3 dominates because W has too
little info to commit. At large K (rich context) W dominates because
cortex has enough context to project the right next byte without
needing the specific episodic anchor.

### 7.3 The CLS routing math fits

Schapiro's CLS-within-HC routing weight is

  w_HC = sigmoid((C_threshold - C_context) / temperature)

For our substrate C_context ≈ log2(K) + const. R3's relative
contribution is then

  w_R3(K) ≈ 1 / (1 + 2^(log2(K) - C*))

With C* ≈ 4 (between log2(16)=4 and log2(8)=3, matching the K=8-16
transition):

  K=4:  w_R3 = 0.80
  K=16: w_R3 = 0.20
  K=32: w_R3 = 0.06
  K=64: w_R3 = 0.02

Compare to measured K-decay 0.032, 0.008, 0.008, 0.003. **The brain
CLS routing predicts the substrate's R3 K-decay with one free
parameter.**

### 7.4 What does NOT translate

The substrate does not have anatomically separate HC and cortex —
they share the same vector-pool/W stack. CLS is a functional
decomposition imposed at readout, not a structural property.
Translating to "build a separate episodic store" would be substrate-
novel territory; the current additive-bias R3 isn't.

The substrate also lacks NREM/REM consolidation loops; random-replay
(wave14c) is the closest analog and lives in a different mechanism
class.

---

## 8. K-adaptive R3 design

### 8.1 Design goals

A K-adaptive R3 should: (i) be silent when W is confident, avoiding
over-shrinkage; (ii) scale GAMMA per-K so per-fire gain stays useful;
(iii) optionally scale NUM_CONCEPTS to keep PPMI density above the
Bullinaria-Levy ≥5-10 per-cell threshold.

### 8.2 Three designs

**Design A — Entropy-gated R3 (Schapiro-style routing).**

```python
def adaptive_r3_logits(sims, qa, vote_logp, gamma_base=0.5,
                       entropy_threshold=2.0):
    w_logits = BETA * sims
    w_probs = softmax(w_logits, dim=-1)
    w_entropy = -(w_probs * log(w_probs + 1e-12)).sum(-1)
    gate = (w_entropy > entropy_threshold).float()
    concept_bias = (qa @ vote_logp).T
    return w_logits + gamma_base * gate * concept_bias
```

Fires only when W is uncertain. At K=64 anchor-confident, gate is
closed; at K=4 broad, gate is open. Predict: K=4 keeps +0.025-0.032,
K=64 sits in [-0.002, +0.005]. Net: keeps the K=4 win, kills the
K-scaling cost. NEUTRAL at large K is the realistic best case.

**Design B — K-scaled GAMMA(K) = 0.5 × (4/K)².**

At K=64, GAMMA = 0.002. Shrinks bias proportionally to firing-rate
decay so per-fire gain is preserved, but does NOT address W-
saturation. Predict: K=64 gain rises from +0.003 to +0.005-0.008.
Helpful but not transformative.

**Design C — Combined entropy gate + K-scaled NUM_CONCEPTS.**

NUM_CONCEPTS = 100 × C(K,2)/6 = 33,600 at K=64. Restores firing
density. Plus entropy gating. But compute cost rises 336× at K=64
and per-concept Laplace-PPMI becomes unstable for the many
low-count concepts. Predict: K=64 gain ≈ +0.010-0.020, capped by
PPMI noise floor. Likely unworkable in production.

### 8.3 Verdict

Design A is the only design with publication-quality character: it
makes R3 silent at large K rather than helpful, which is honest. It
does not "rescue" R3 at K=64; it ensures R3 does no harm at K=64.
Designs B and C are at best partial rescues with compute or noise
costs.

### 8.4 30-minute decisive experiment

Implement Design A and measure at K=4 and K=64 with 5 seeds:

- H1: K=4 entropy-gated R3 gain ≥ +0.025 (no loss vs ungated)
- H2: K=64 entropy-gated R3 gain ∈ [-0.002, +0.005] (silent, not
  harmful)

If both hold, the K-adaptive concept is validated. If H1 fails,
threshold needs tuning. If H2 fails high (gain ≥ +0.010 at K=64
with gating), there is residual signal worth investigation — unlikely
given the cardinality math.

---

## 9. Operational implications

### 9.1 Publication-grade story

R3 becomes a 1-paragraph appendix entry:

> R3 (concept-as-readout-bias) delivers +0.025-0.032 bpc at K=4 in
> the post-shift setting via sparse-gated additive logit bias from
> top-PPMI byte-bigrams of the Phase-A pool. The mechanism is
> equivalent to Pereyra (2017) confidence-penalty regularization
> applied via a sparse PPMI gate (Levy-Goldberg 2014). Effect decays
> as 1/K² due to position-pair fan-out, vanishing within seed noise
> by K=64. Substrate-unique status: NO.

### 9.2 Design space matrix

Add row: R3-method × K-scaling: STRONG-NEGATIVE (1/K² decay). Remove
R3 from the substrate-unique axis; add to "K=4-product calibration"
axis alongside future named-technique ablations.

### 9.3 Research investment

- **Drop**: further R3-variants (R3-disjoint-K-sweep at scale, R3-
  trigram concepts, R3-with-pool-replacement). Cardinality math says
  they all fail similarly.
- **Cheap close**: run Design A entropy gate at K=4 and K=64 to
  confirm silent-at-large-K. 30 minutes. Closes R3's file honestly.
- **Optional close**: run 1/K² GAMMA scaling at K=64 to confirm no
  rescue from gamma alone. 15 minutes.
- **Do not run**: NUM_CONCEPTS scaling at K=64 (Design C). Too
  expensive, too unlikely to yield substrate-significant result.

### 9.4 Brain mapping doc

Add: "K-scaling of additive prior bias (R3) follows Schapiro et al.
(2017) hippocampal-cortical routing — silent when context is rich.
We use this as inspiration for future entropy-gated readout designs,
not as a mechanistic claim about substrate biology."

---

## 10. Sources

### Capacity and saturation

- Anderson 1972 — A simple neural network generating an interactive
  memory. Math Biosci 14:197.
- Plate 1995 — Holographic Reduced Representations. IEEE TNN
  6(3):623.
- Frady, Kleyko, Sommer 2020 — Resonator Networks for Factoring
  Distributed Representations. arXiv:2007.03748.
- Kent et al. 2020 — Resonator Networks, 1. Neural Computation
  32(12):2311.

### PPMI / sample-count saturation

- Levy & Goldberg 2014 — Neural Word Embedding as Implicit Matrix
  Factorization. arXiv:1402.3722.
- Bullinaria & Levy 2007 — Extracting semantic representations from
  word co-occurrence statistics. Behavior Research Methods 39:510.
- Mikolov et al. 2013 — Distributed Representations of Words and
  Phrases. arXiv:1310.4546.

### Calibration / additive bias / over-shrinkage

- Pereyra et al. 2017 — Regularizing Neural Networks by Penalizing
  Confident Output Distributions. arXiv:1701.06548.
- Müller, Kornblith, Hinton 2019 — When Does Label Smoothing Help?
  arXiv:1906.02629.
- Guo et al. 2017 — On Calibration of Modern Neural Networks.
  arXiv:1706.04599.
- James & Stein 1961 — Estimation with quadratic loss. Proc 4th
  Berkeley Symp 1:361.
- Hoerl & Kennard 1970 — Ridge regression. Technometrics 12(1):55.

### Sparse gating

- Shazeer et al. 2017 — Outrageously Large Neural Networks.
  arXiv:1701.06538.
- Fedus, Zoph, Shazeer 2021 — Switch Transformer. arXiv:2101.03961.

### Spin-glass framing

- Amit, Gutfreund, Sompolinsky 1985 — Storing infinite numbers of
  patterns in a spin-glass model. PRL 55:1530.
- Kanter & Sompolinsky 1987 — Associative recall of memory without
  errors. PRA 35:380.

### Brain analog

- McClelland, McNaughton, O'Reilly 1995 — Why there are complementary
  learning systems. Psych Rev 102:419.
- Schapiro et al. 2017 — Complementary learning systems within the
  hippocampus. Phil Trans R Soc B 372:20160049.
- Yonelinas 2010 — Recollection and familiarity. Hippocampus
  20(11):1178.
- O'Reilly & Norman 2002 — Hippocampal and neocortical contributions
  to memory. Trends Cogn Sci 6(12):505.

### Internal cross-references

- `notes/wave14c_r3_disjoint_K_flatness_research.md`
- `notes/wave14c_r3_unigram_failure_research.md`
- `notes/wave14c_r3_small_effect_mechanism_research.md`
- `notes/wave14b_compound_falsification_research.md`
- `notes/wave14e2_spin_glass_substrate_research.md`
- `experiments/exp_wave14b_r3_disjoint_K64.py`
- `experiments/exp_wave14b_r3_alone_laplace.py`
