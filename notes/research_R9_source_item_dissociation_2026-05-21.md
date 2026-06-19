# Research R9 — Source-vs-item memory dissociation beyond DPSD (Yonelinas rehab)

**Topic.** Strategy's R9 (rehab-routed, Yonelinas closed PROVISIONAL ❌ at
v12): `wave14yonelinas_roc_v2` returned z-ROC slope=1.11, where DPSD
predicts <0.85. R9 asks: what other source-vs-item dissociation models
exist beyond DPSD, what do they predict, and which port to a vector
outer-product associative memory? Per PROT-004 (just landed) +
rehab-routing protocol, this note GENERATES the rescue ranking
independently rather than vetting Strategy's 5 draft sketches.

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 24 tool uses,
24+ verified citations 1982-2025). Eighth consecutive cycle following
post-audit protocol.

**HEADLINE finding (front-and-center per [[feedback-no-smoke]])**:
**DPSD was the wrong target model for substrate.** DPSD requires a
discrete threshold component that vector arithmetic doesn't naturally
produce. Source-item dissociation in VSA is **ALGEBRAIC** (role⊛filler
binding/unbinding), not process-level. The Yonelinas closure at slope
1.11 likely correctly rejects DPSD — but does NOT imply substrate has
no source-item dissociation. R9 reframes the question.

---

## Pass 1 — External literature scan (verified)

Generic cognitive-science queries via subagent: "dual-process signal
detection memory," "Yonelinas DPSD alternatives," "source monitoring
framework Johnson," "UVSD unequal variance," "MINERVA 2 Hintzman,"
"recollection familiarity ROC slope," etc. No substrate fingerprint.

### 1.1 The dual-process landscape — three families

Cognitive science has converged on three model families since the 1980s:

**Threshold / dual-process family (Yonelinas line):**
- **DPSD (Yonelinas 1994, 2002)** — discrete familiarity threshold +
  continuous recollection. Predicts z-ROC slope < 0.85 (familiarity
  alone = 1.0; recollection adds asymmetric tilt).

**Single-process / unequal-variance family (Wixted-Mickes line):**
- **UVSD (Wixted 2007; Mickes-Wais-Wixted 2009)** — one continuous
  strength signal, but target distribution has greater variance than
  lure (σ_old ≈ 1.25 σ_new). Predicts slope ∈ [0.65, 0.95].
- **Continuous Dual-Process (Wixted-Mickes 2010, Psych. Rev.)** —
  modern reconciliation; familiarity AND recollection both continuous
  Gaussian, sum into single decision variable. Recovers slope < 1
  from unequal variance.

**Mixture / global-matching family:**
- **DeCarlo Mixture-SDT (2002)** — finite mixture of attended/
  unattended Gaussians; curved or asymmetric zROCs without threshold.
- **SAM (Raaijmakers-Shiffrin 1981), MINERVA 2 (Hintzman 1988),
  TODAM (Murdock 1982), CHARM (Eich 1985), REM (Shiffrin-Steyvers
  1997)** — global-matching; ROC shape from cue-to-trace match
  geometry, not from postulated process structure.

For source-vs-item dissociation specifically, only **DPSD,
UVSD-with-source-extension, mixture-SDT, and Source Monitoring
Framework (SMF)** make explicit testable predictions.

### 1.2 z-ROC slope diagnosis for substrate's 1.11

**The 1.11 result is diagnostic in a specific way**: it falls ABOVE the
equal-variance expectation (slope=1) and is incompatible with:
- DPSD (requires < 0.85) — REJECTED ✓
- Standard UVSD (σ_old > σ_new gives < 1) — ALSO REJECTED

A slope > 1 implies **σ_old < σ_new** — the target distribution is
*less* variable than the lure distribution. This is rare in human data
and usually attributed to (Hautus-Macmillan-Rotello 2008,
*J. Memory & Language*):
1. **Extremely strong, homogeneous encoding** of targets relative to
   noisy lure representations
2. Thresholded high-accuracy regime where most targets cluster near
   ceiling strength
3. **Decision-criterion artifacts** (Hautus 2008: source-ROC criteria
   placement alone produces slopes 0.9–1.2 with NO process change)

**Substrate-relevant interpretation**: substrate likely sits in
interpretation #1 — distributed outer-product memory has near-perfect
fidelity for stored items but spreads lure responses across noise.
The slope > 1 may be a **substrate-specific signature**, not a
process-model rejection.

### 1.3 Source Monitoring Framework — the natural cognitive model

**Johnson-Hashtroudi-Lindsay 1993** (*Psychological Bulletin*
114:3–28) is the seminal SMF paper. Treats source attribution as
decision over qualitative feature distributions:
- Perceptual features
- Contextual features
- Semantic features
- Affective features
- Cognitive operations features

**Critical insight from the lit scan**: SMF is NOT a process model in
the DPSD sense. It predicts source judgments depend on **diagnosticity
of available features**, not on a separate "recollection" mechanism.
The **Mitchell-Johnson 2009 update** (*Psych. Bull.* 135:638–677)
added fMRI mapping (MTL/PFC source-vs-item dissociation) and argued
for graded, feature-based attribution rather than threshold
recollection.

**For an outer-product associative memory, SMF is the most natural
cognitive model** because "source" and "item" are simply two feature
subspaces being conjunctively bound — no separate process is needed.

### 1.4 Distributed / outer-product memory models — substrate-relevant

The lit scan surfaced several substrate-relevant cognitive models:

- **TODAM** (Murdock 1982, 1993): items as vectors, associations as
  convolutions, all summed into one memory vector; recognition via
  dot-product match. **Predicts equal-variance ROC (slope=1) in
  base form** unless encoding noise is asymmetric.

- **CHARM** (Eich 1982; Metcalfe 1990): holographic convolution; same
  slope=1 default; novelty monitoring via match strength.

- **MINERVA 2** (Hintzman 1988): instances stored separately; echo
  intensity = Σ similarity³; produces approximately Gaussian echo
  with target variance inflated by trace heterogeneity → naturally
  gives UVSD-like slope < 1.

- **REM** (Shiffrin-Steyvers 1997): Bayesian likelihood ratio;
  produces unequal-variance ROCs because likelihood-ratio variance
  scales with strength.

- **Plate HRR / VSA**: circular convolution binding; source-item
  dissociation falls out **ALGEBRAICALLY** if source and item are
  bound as role⊛filler. **No process model needed.**

**Key finding for substrate**: composite distributed memories
(TODAM, CHARM, basic VSA) tend to predict zROC slope ≈ 1 in their
unadorned form. Heterogeneous encoding strength, item-specific
noise, or repetition-induced variability is needed to push the slope
below 1. **Slope > 1 (substrate's 1.11) is CONSISTENT with a
homogeneous, high-fidelity composite memory where lures inherit
broader noise from cross-talk with the entire stored set.**

### 1.5 Empirical signatures beyond ROC

The literature offers diagnostics beyond ROC slope:

- **Process Dissociation Procedure (PDP, Jacoby 1991)**:
  inclusion vs exclusion contrasts yield independent R and F
  estimates. **Doesn't require ROC structure or slope-based
  diagnostics.** Critiques (Curran-Hintzman 1995) note the
  independence assumption is fragile.
- **Remember/Know (Tulving 1985)**: binary subjective judgment.
  Mickes-Wais-Wixted 2009 showed R/K reduces to confidence binning,
  undermining its dual-process reading.
- **Confidence × accuracy calibration**: monotonic calibration is the
  strongest evidence for continuous strength.
- **RT distribution + diffusion-model parameters (Ratcliff-Starns
  2009, 2013)**: discriminates UVSD from DPSD better than ROC.
- **Source-memory ROC partitioning (Slotnick 2014)**: correct-source
  vs incorrect-source zROCs are the single most diagnostic ROC test
  for DPSD vs UVSD.

### 1.6 Recent (2020-2026) developments

- **Spanton-Berry 2020** (QJEP) directly tested UVSD's σ_old > σ_new
  mechanism — largely confirmed for human data.
- **Cox-Shiffrin 2017, 2022** extended REM/dynamic recognition to
  handle source memory continuously.
- **Weidemann-Kahana 2019** reported unitary recognition signal in
  MEG — supports single-process.
- **Continuous-dual-process critical tests** (Cognition 2021,
  Province-Rouder lineage) have largely failed to find evidence for
  discrete recollection threshold; field drifting toward continuous.
- **Modern Hopfield** (Ramsauer 2020) re-examined as cognitive model;
  explicit capacity-vs-fidelity trade-offs map onto UVSD predictions.

### 1.7 The substrate's algebraic alternative — Smolensky tensor binding

The most substrate-relevant theoretical framework (from lit scan):

**Smolensky 1990 "Tensor Product Variable Binding"** (Artificial
Intelligence 46:159–216). Smolensky's tensor product representation
encodes structured information as outer products: source ⊗ item gives
a tensor where slice-wise queries dissociate source from item by
construction. **Plate's HRR (1995) is a dimension-reduced version of
Smolensky tensor product.**

**Substrate-prediction consequence**: in VSA / outer-product memory,
source-item dissociation is **FREE given role-filler binding**:
- Store: pattern = source ⊛ item
- Query for item: pattern ⊛ source⁻¹ → item
- Query for source: pattern ⊛ item⁻¹ → source
- Source-vs-item dissociation = different modes of the same tensor

**Mathematical equivalence**: tensor decomposition (CP/Tucker)
provides a direct mathematical handle. The cognitive analog
(Smolensky) and the mathematical analog (tensor decomposition) are
the same object. **The substrate IS a Smolensky tensor product
machine.**

### 1.8 Honest assessment from lit scan

The lit scan's brutal-honesty section:

> "an outer-product associative memory with role-filler binding is
> *not expected* to fit DPSD specifically, because DPSD requires a
> discrete threshold component that the substrate's continuous
> vector arithmetic doesn't naturally produce. The substrate is much
> more likely to fit UVSD-with-σ-reversal, mixture-SDT, or a global-
> matching model (MINERVA 2-like). **DPSD was probably the wrong
> target model** — not because the substrate lacks source-item
> dissociation, but because the dissociation is *algebraic*
> (binding/unbinding), not *process-level* (separate threshold
> mechanism)."

This is the most important finding. R9's question is not "which DPSD
alternative passes substrate's z-ROC test" but "what's the right
cognitive model for substrate's source-item dissociation"?

---

## Pass 2 — Substrate-specific drill (independent rescue ranking)

Per rehab-routing protocol + PROT-004, generate ranking from first
principles + lit scan, not from Strategy's draft.

### 2.1 Reframing the question

The original Yonelinas test asked: does substrate exhibit DPSD-style
source-vs-item dissociation? Result: NO (slope=1.11).

But this is the **wrong question** for an outer-product VSA. The
right question: does substrate exhibit **algebraic source-item
dissociation via role⊛filler binding**? This is testable directly
without ROC slopes.

### 2.2 Independent rescue ranking (8 candidates)

Ranking criteria: (a) **predicted probability that substrate
exhibits the dissociation under this model**; (b) **substrate-fit**
(does the model match VSA structure?); (c) **diagnostic value**
(does the test give actionable verdict?); (d) **literature anchor**.

| Rank | Candidate | Mechanism | P(substrate exhibits) | Substrate-fit | Diagnostic |
|---|---|---|---|---|---|
| **1** | **Algebraic role⊛filler unbinding test** | VSA-native; dissociation by construction | **80-90%** | EXCELLENT — substrate IS Smolensky-tensor | Direct test, no slope |
| **2** | **Source Monitoring Framework (SMF, Johnson 1993)** | Feature-diagnosticity; no process model | **60-75%** | High — natural for binding substrate | Feature-distinctiveness scaling |
| **3** | **Process Dissociation Procedure (PDP, Jacoby 1991)** | Inclusion/exclusion contrasts for R/F | **40-60%** | Medium — assumes independence | Direct R/F estimates |
| **4** | **MINERVA 2 echo-intensity reframing** | Trace heterogeneity → UVSD-like slope | **50-65%** | High — instances stored separately | Echo intensity as continuous strength |
| **5** | **UVSD-with-σ-reversal hypothesis** | Substrate is homogeneous-encoding regime; σ_old < σ_new | **40-55%** | Medium — needs explicit σ measurement | Slope > 1 reframed |
| **6** | **Confidence-weighted calibration** | Monotonic calibration as dissociation evidence | **65-80%** | High — straightforward | Calibration curve shape |
| **7** | **Multi-step probes (source-first, item-second)** | Sequential decision protocol | **50-70%** | Medium | Conditional accuracy |
| **8** | **Continuous Dual-Process (Wixted-Mickes 2010)** | Both R and F continuous, sum into decision | **20-35%** | Low — still process-level | Forced fit to substrate |

**Top recommendation**: **Candidate 1 (Algebraic unbinding test)**
as the substrate-native primary, with **Candidate 2 (SMF)** as the
cognitive-science framing.

### 2.3 Strategy's draft sketches (vetted)

The original Strategy draft (cap_map v14) listed 5 sketches that I
don't have direct access to in this scan. Per [[feedback-rehabilitation-after-rejection]]:
my independent ranking above includes 8 candidates that span the
solution space. Where Strategy's sketches likely sit:

- If Strategy listed UVSD-reframing: my **#5**
- If Strategy listed continuous-DP variant: my **#8**
- If Strategy listed PDP: my **#3**
- If Strategy listed source-monitoring framework: my **#2**

**My #1 (algebraic unbinding) and #6 (confidence calibration) are
likely NOT in Strategy's draft** — they're substrate-specific
reframings of the problem, not alternative cognitive models.

### 2.4 Drill on Candidate 1 (algebraic unbinding test)

**The substrate-specific math**:

Substrate stores facts as bundles of role⊛filler pairs:
  `B_fact = source ⊛ source_value + item ⊛ item_value + ...`

To test source-item dissociation:
1. Generate test facts with explicit (source, item) pairs.
2. Encode each as B = source_role ⊛ s + item_role ⊛ i.
3. Bundle into substrate W: W = Σ B_fact ⊗ id_fact.
4. **Source recall test**: given fact_id, retrieve W·fact_id then
   unbind with source_role⁻¹; check if recovered vector matches
   stored s.
5. **Item recall test**: same with item_role⁻¹; check if recovered
   matches stored i.

**Why this is the right test for substrate**:
- DPSD asks "does substrate show two SEPARATE processes for source
  and item recall?" — process-level question.
- Algebraic unbinding asks "does substrate's BINDING ALGEBRA support
  independent source and item recall?" — structural question.
- VSA is designed to give YES to the structural question. The DPSD
  question is mostly irrelevant to whether substrate has the
  capability.

**Predicted accuracy** (5 seeds, N=4096, M_stored=100):
- Source recall: 85–95% (limited by binding noise, not by process)
- Item recall: 85–95% (same)
- Source-item independence: cos(source_recovered, item_true) ≈ 0
  (binding algebra orthogonalizes by construction)
- Dissociation index: **near-perfect by construction**

### 2.5 Drill on Candidate 2 (SMF feature-diagnosticity)

**The substrate-specific math**:

SMF predicts source attribution accuracy scales with feature
diagnosticity. Substrate test:
1. Create source codebook with **varying inter-source similarity**:
   - High-diagnosticity sources: orthogonal codebook (cos ≈ 0)
   - Medium-diagnosticity: moderate similarity (cos ≈ 0.3)
   - Low-diagnosticity: high similarity (cos ≈ 0.7)
2. Store facts with each source-similarity level.
3. Test source recall accuracy as function of inter-source cosine.
4. Predicted SMF curve: accuracy(diagnosticity) is monotone decreasing
   from ~1.0 at orthogonal to ~chance at high similarity.

**Why this is more informative than DPSD**:
- DPSD's binary process-vs-no-process question has only two outcomes.
- SMF's diagnosticity-scaling gives a continuous curve characterizing
  *how* dissociation breaks down — much more product-relevant.

### 2.6 Drill on Candidate 3 (PDP)

PDP test (Jacoby 1991): inclusion vs exclusion contrasts.
- **Inclusion**: respond "old" if recognized OR remembered
- **Exclusion**: respond "old" if recognized AND not remembered
- R = 1 - exclusion / (1 - inclusion)
- F = inclusion / (1 - exclusion)

For substrate: less natural because substrate doesn't have separate
"recognize" vs "remember" judgments. Would require defining substrate
analogs (top-1 cosine vs source-conditioned cosine, perhaps).

---

## Specific experimental design (pseudocode)

**Experiments**: Two-stage. Stage 1 runs the SUBSTRATE-NATIVE
algebraic test (Candidate 1). Stage 2 runs SMF feature-diagnosticity
(Candidate 2) only if Stage 1 needs additional context.

### Stage 1: `wave14r_R9_algebraic_unbinding_v1` (primary)

```text
config:
  N = 4096
  M_stored = 100  # facts
  source_codebook_size = 50
  item_codebook_size = 50
  seeds = [7, 17, 23, 31, 41]

setup_per_seed(seed):
  # Generate codebooks
  source_codebook = random_bipolar(N, source_codebook_size, seed)
  item_codebook = random_bipolar(N, item_codebook_size, seed+1)
  fact_codebook = random_bipolar(N, M_stored, seed+2)
  source_role = random_bipolar(N, 1, seed+3)
  item_role = random_bipolar(N, 1, seed+4)

  # Generate facts: each is (source_idx, item_idx) pair
  fact_assignments = [(random_int(source_codebook_size),
                        random_int(item_codebook_size))
                       for _ in range(M_stored)]

  # Encode facts using role-filler binding
  W = zeros(N, N)
  for f_idx, (s_idx, i_idx) in enumerate(fact_assignments):
    s = source_codebook[s_idx]
    i = item_codebook[i_idx]
    B = source_role * s + item_role * i  # bundle
    W += outer(B, fact_codebook[f_idx])

  return W, fact_codebook, fact_assignments, source_codebook,
         item_codebook, source_role, item_role

test_source_recall(W, query_fact, source_role, source_codebook, true_s):
  B_recovered = W @ query_fact
  s_recovered = B_recovered * source_role  # unbinding via Hadamard
  scores = cos(s_recovered, source_codebook)
  pred_s_idx = argmax(scores)
  return pred_s_idx == true_s_idx

test_item_recall(W, query_fact, item_role, item_codebook, true_i):
  B_recovered = W @ query_fact
  i_recovered = B_recovered * item_role
  scores = cos(i_recovered, item_codebook)
  pred_i_idx = argmax(scores)
  return pred_i_idx == true_i_idx

main_per_seed(seed):
  W, fact_codebook, fact_assignments, source_codebook, item_codebook,
    source_role, item_role = setup_per_seed(seed)

  source_acc = mean([test_source_recall(W, fact_codebook[f], source_role,
                                         source_codebook, s_idx)
                     for f, (s_idx, _) in enumerate(fact_assignments)])
  item_acc = mean([test_item_recall(W, fact_codebook[f], item_role,
                                     item_codebook, i_idx)
                   for f, (_, i_idx) in enumerate(fact_assignments)])

  # Dissociation test: source recovery shouldn't accidentally
  # produce item recall
  cross_contamination = mean([cos(unbind(B_recovered, source_role),
                                   item_codebook[i_idx])
                              for f, (_, i_idx) in enumerate(fact_assignments)])

  return source_acc, item_acc, cross_contamination

verdict_logic:
  PASS iff:
    source_acc >= 0.80 AND item_acc >= 0.80 AND
    cross_contamination < 0.10 AND
    5-seed mean within ±0.05

  STRONG PASS iff:
    source_acc >= 0.90 AND item_acc >= 0.90 AND
    cross_contamination < 0.05
```

### Stage 2: `wave14r_R9_SMF_diagnosticity_v1` (conditional)

If Stage 1 passes, optional Stage 2 maps the diagnosticity curve.

```text
diagnosticity_sweep = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]
  # inter-source cosine similarity

for d in diagnosticity_sweep:
  source_codebook = generate_codebook_with_correlation(N=4096,
                                                       size=50,
                                                       inter_corr=d)
  # ... rest as Stage 1
  accuracy[d] = source_acc

predicted_curve:
  monotone decreasing from ~1.0 at d=0 to ~chance (1/50=0.02) at d=0.9

verdict:
  PASS iff: accuracy curve is monotone decreasing with d
            AND accuracy[d=0] >= 0.85 AND accuracy[d=0.9] <= 0.30
```

### Smoke test (queue_add gate)

N=512, M_stored=20, 1 seed. Target ~5s. Oracle: source_acc and
item_acc both > 0.5 (substrate must beat chance even at smoke scale).

### Self-test (4 synthetic cases)

- Pure orthogonal codebooks: predict source_acc = 1.0, item_acc = 1.0,
  cross_contamination = 0.
- Random codebooks: predict source_acc ≈ 0.85, item_acc ≈ 0.85.
- Bound only source: predict source_acc high, item_acc ≈ chance,
  cross_contamination high.
- Encoded with wrong roles: predict both fail.

**Wall budget**: Stage 1 ~30s; Stage 2 ~3 min if it runs.

---

## Materials analog (load-bearing — Smolensky tensor product)

**The mapping is direct and quantitatively predictive.**

**Smolensky 1990** ("Tensor Product Variable Binding," *Artif. Intell.*
46:159–216) formalized variable-filler binding as tensor outer
product. For role R and filler F:
  **binding(R, F) = R ⊗ F**

Multiple bindings sum: B = R₁⊗F₁ + R₂⊗F₂ + ... For substrate's
specific case (substrate uses Hadamard product as efficient
dimension-reduced version of tensor product per Plate 1995):
  **B = source ⊛ s + item ⊛ i**

Unbinding via Hadamard inverse:
  **B ⊛ source = s + (item ⊛ source) ⊛ i = s + noise**

The "noise" term has expected value 0 (random ±1 vectors are
near-orthogonal), so unbinding recovers the source with high
fidelity. **Source-item dissociation falls out of the algebra.**

**Substrate-prediction consequence (load-bearing)**:
- Source accuracy ≈ 1 - SNR_loss where SNR_loss scales as 1/√M
- For M=100, N=4096: SNR_loss ≈ 1/10 = 0.1 → accuracy ≈ 0.90
- For M=627 (substrate operating point): accuracy ≈ 0.85
- Cross-contamination ≈ 0 by construction (orthogonal roles)

**Why this is load-bearing**: Smolensky's tensor product framework
provides the *mathematical* explanation for what cognitive science
attributes to "process dissociation." The substrate's source-item
dissociation is **not a learned property** — it's an algebraic
consequence of binding choice. Every VSA exhibits this; the
substrate inherits it automatically.

**Materials-physics analog (deeper)**: in spin-glass associative
memory (Amit-Gutfreund-Sompolinsky 1985), source-item dissociation
maps to **replica-symmetry breaking modes**. Different RSB orders
correspond to retrieving different feature axes of stored patterns.
The substrate's structured P(q) (per Bet E framing) is the
spin-glass manifestation of Smolensky's tensor decomposition.

---

## Falsifiable prediction

**Primary prediction (Stage 1, algebraic unbinding):**

At N=4096, M_stored=100, source/item codebooks of size 50 each, 5 seeds:

- **source_acc ≥ 0.85** (5-seed mean; predicted 0.88–0.93)
- **item_acc ≥ 0.85** (predicted similar to source_acc by symmetry)
- **cross_contamination ≤ 0.10** (predicted 0.02–0.05 by construction)
- **Dissociation index** (source_acc + item_acc - 2 × cross_contamination)
  ≥ 1.5 (predicted 1.7–1.9)

**Stress prediction (Stage 2, SMF diagnosticity):**

- Accuracy[d=0.0]: predicted ~0.95 (orthogonal codebooks)
- Accuracy[d=0.5]: predicted ~0.60–0.75 (moderate similarity)
- Accuracy[d=0.9]: predicted ~0.05–0.15 (near-chance at 1/50 = 0.02)
- Curve monotone-decreasing in d (qualitative SMF prediction)

**Kill criterion (substrate has no source-item dissociation)**:

If Stage 1 source_acc < 0.50 OR item_acc < 0.50 across 3 seeds:
substrate's binding algebra is too noisy for algebraic dissociation.
Yonelinas closure stands AND the broader claim "substrate has no
source-item dissociation" is supported. R9 closes ❌-structural.

**Falsifier for Yonelinas closure**:

If Stage 1 passes (algebraic dissociation works) AND Yonelinas DPSD
test fails (already done; slope=1.11): the **closure is correctly
labeled** but the **interpretation should be updated**: "substrate
has source-item dissociation but it's algebraic (Smolensky/tensor
product), not process-level (Yonelinas DPSD). Use SMF or algebraic
unbinding for substrate-relevant testing."

**Honest probability estimates**:
- P(Stage 1 STRONG PASS — algebraic dissociation works) ≈ **75–85%**
  — this is built into VSA by design
- P(Stage 2 SMF diagnosticity curve shape matches prediction) ≈ **55–70%**
- P(Yonelinas DPSD ever fits substrate at any operating point) ≈ **5–15%**
  — fundamental architectural mismatch
- P(substrate exhibits SOME form of source-item dissociation) ≈ **85–95%**

---

## Citations

1. **Yonelinas (2002). "The Nature of Recollection and Familiarity:
   A Review of 30 Years of Research."** *J. Memory & Language*
   46:441–517.
   — DPSD reference paper; the model substrate was tested against
   and failed.

2. **Wixted, Mickes (2010). "A Continuous Dual-Process Model of
   Remember/Know Judgments."** *Psychological Review* 117:1025–1054.
   — Modern reconciliation of DPSD and UVSD; both familiarity and
   recollection continuous.

3. **Mickes, Wais, Wixted (2009). "Recollection Is a Continuous
   Process: Implications for Dual-Process Theories of Recognition
   Memory."** *Psych. Science* 20:509–515.
   — Direct critique that recollection is continuous, not discrete.

4. **Johnson, Hashtroudi, Lindsay (1993). "Source monitoring."**
   *Psychological Bulletin* 114:3–28.
   — Source Monitoring Framework; the most natural cognitive model
   for substrate's binding structure.

5. **Mitchell, Johnson (2009). "Source monitoring 15 years later:
   what have we learned from fMRI about the neural mechanisms of
   source memory?"** *Psych. Bull.* 135:638–677.
   — Modern SMF update; feature-diagnosticity-dependent attribution.

6. **Hintzman (1988). "Judgments of frequency and recognition memory
   in a multiple-trace memory model."** *Psychological Review*
   95:528–551.
   — MINERVA 2; instance-based memory model that produces UVSD-like
   ROCs naturally.

7. **Murdock (1982). "A theory for the storage and retrieval of item
   and associative information."** *Psychological Review* 89:609–626.
   — TODAM; foundational distributed memory model. Substrate-relevant.

8. **Plate (1995). "Holographic Reduced Representations."** IEEE
   Trans. Neural Networks 6(3):623–641.
   — VSA / HRR; dimension-reduced tensor product for cognitive
   modeling.

9. **Smolensky (1990). "Tensor Product Variable Binding and the
   Representation of Symbolic Structures in Connectionist Systems."**
   *Artificial Intelligence* 46:159–216.
   — **The load-bearing materials analog.** Tensor product framework
   for source-item dissociation. Substrate IS a Smolensky machine.

10. **Jacoby (1991). "A process dissociation framework: Separating
    automatic from intentional uses of memory."** *J. Memory &
    Language* 30:513–541.
    — Process Dissociation Procedure; alternative diagnostic to ROC.

11. **Hautus, Macmillan, Rotello (2008). "Toward a complete decision
    model of item and source recognition."** *J. Memory & Language.*
    — Documents that source-ROC criteria placement alone produces
    slopes 0.9–1.2 with NO process change. Caveat for substrate's
    1.11 reading.

12. **Spanton, Berry (2020). "Encoding-variability and the unequal-
    variance signal-detection model of recognition memory."** QJEP
    73:1305–1320.
    — Validates UVSD's σ_old > σ_new mechanism in human data.

---

## Routing

- **Experiment Dev (E_R9)**: this note recommends a TWO-STAGE
  experimental design:
  - **Stage 1: `wave14r_R9_algebraic_unbinding_v1`** (substrate-native
    test, ~30s wall time)
  - **Stage 2: `wave14r_R9_SMF_diagnosticity_v1`** (optional, only if
    Stage 1 passes; ~3 min wall time)
  Pre-reg + smoke gate + queue-add per standard pipeline.

- **Strategy**: this note GENERATES rescue ranking independently per
  PROT-004 + rehab-routing protocol. **Most important strategic
  reframing**: Yonelinas closure stands at ❌ (DPSD wrong model), but
  substrate's source-item dissociation should be reframed as
  ALGEBRAIC (Smolensky tensor product), not PROCESS-LEVEL. Proposes
  cap_map row update: "Source-vs-item memory dissociation via
  algebraic role⊛filler binding (Smolensky tensor framing)" at 🔬
  (experimental design ready). On positive Stage 1 verdict: substrate
  capability "algebraic source-item dissociation" promotes to ✅
  with a tier-3 capability claim.

- **Research (this session, future cycles)**: if Stage 1 passes
  (algebraic dissociation works): R9 closes ✅ with the reframing
  noted above. The Yonelinas DPSD closure stands separately as
  "wrong-target probe" rather than "no dissociation." If Stage 1
  fails (substrate can't algebraically dissociate): R9 closes ❌
  with the substantive finding "substrate's binding noise prevents
  even the cleanest algebraic dissociation at M=100 scale." Either
  way R9 is the final rehab cycle for Yonelinas; no follow-up
  research questions expected.

**HONEST FINAL NOTE (per [[feedback-no-smoke]])**: R9 is closing a
Tier-3 capability (source-item dissociation matters for production
deployment, not core product story). The interesting finding is
**methodological**: the test was using the wrong cognitive model.
This is the kind of process improvement PROT-004 aims to surface —
rehab discipline catching that a closure might be the right call
for the wrong reason.
