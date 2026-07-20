# Research: VSA superposition capacity-cliff reconciliation (the 6x miss) + genuine-decoupling criteria (chain-grade drill)

Filed by: research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents: VSA/HDC exact
capacity theory; sparse/correlated-key + random-matrix corrections; multiplexing/decoupling
theory; brain theta-gamma + hippocampal cross-check).
Date: 2026-07-17.
Trigger: a VSA/HDC associative-memory phase-diagram experiment landed MEASURED_MECHANISM (mixed).
Two weaknesses block CHAIN_GRADE: (1) the naive capacity-cliff formula K_cliff ~ N/(4 ln V) was
measured ~6x off (measured 0.5-recall crossing at much higher K than predicted); (2) a
two-subsystem "shared buffer, zero interference" decoupling claim needs a genuine-contention test,
not an easy-operating-point demonstration.

---

## HEADLINE

**Both weaknesses have a documented, citation-grade fix path, and — the key calibration point —
the DIRECTION of the 6x miss is exactly what the literature predicts, not a sign of a new or
exotic mechanism.**

**Weakness 1 (the capacity miss).** The naive `N/(4 ln V)` formula is a doubly-lossy shorthand of
Plate's own exact derivation, and Plate's own formula never used raw codebook cardinality V in the
first place — it used **m, the number of candidate vectors actually compared at cleanup time**
(what your experiment should call `V_eff`). Two independent, separately-documented effects both
push in the direction of your miss (naive formula predicts too LOW a capacity, i.e. cliff should
sit at HIGHER K than the naive formula says — matching what you measured):

1. **V_eff (cleanup comparison-set size) is very likely smaller than raw codebook V** in most
   real harnesses. Plugging full V into `N/(4 ln V)` systematically underpredicts capacity when
   the actual cleanup step only ever compares against a subset (m in Plate's notation, D in
   Frady/Kleyko/Sommer's notation). This is confirmed structurally in **every** capacity paper
   surveyed (Plate 1995; Frady, Kleyko & Sommer 2018; Gallant & Okaywe 2013; Thomas, Dasgupta &
   Rosing 2021) — the union-bound / crosstalk term is always over the compared candidate set, not
   an abstractly larger vocabulary.
2. **Frady, Kleyko & Sommer (Neural Computation, 2018)** report a *directly citable, already-known*
   result of the same character: the classical "high-fidelity" asymptotic-style approximations
   (the Plate/Gallant-Okaywe style formulas) **underestimate true capacity by about 4x** relative
   to the exact numerically-evaluated integral. This is documented independently of the V_eff
   issue — it comes from the accuracy-criterion / tail-bound approximation itself being loose.

Compounding (1) x (2) plausibly reaches ~6x without invoking any new mechanism. This is
falsifiable and cheap to check: re-derive `K_cliff` with the corrected formula (exact-integral or
Chang-bound sensitivity, with V_eff substituted for V) and see whether the residual gap collapses
to ~20% (see Cheap decisive test below).

**Weakness 2 (decoupling).** The literature gives a crisp, *named* distinction between GENUINE
(architectural) decoupling and VACUOUS (operating-point) decoupling:

- **Genuine decoupling** requires (a) an interference metric that is provably **zero, not merely
  small**, up to a combinatorially/geometrically fixed contention threshold (orthogonal-subspace
  dimension, mutual coherence mu=0, or a Restricted-Isometry-Property-style bounded per-access
  footprint), and (b) that threshold — and the per-access footprint — must **not grow** with the
  number of independent subsystems sharing the substrate.
- **Vacuous decoupling** looks identical at a single low-load operating point but is secretly a
  smoothly-increasing-interference curve underneath. CDMA overload, HRR/VSA superposition
  crosstalk, correlated-Hopfield capacity degradation, and holographic dynamic-range crosstalk are
  ALL documented examples of this "soft" regime — none of them has a hard interference-free
  ceiling; they degrade continuously from K=0.

**The dedicated test:** sweep shared-buffer load *past* the tested operating point and look for a
KNEE — flat-zero interference, then a sharp onset — at a location **predicted in advance** by a
closed-form threshold (not curve-fit after the fact). See Part B of the experiment design below.

**Biology cross-check (important calibration for how to frame a positive result).** The brain's
own theta-gamma multiplexing (Lisman & Idiart 1995; Lisman & Jensen 2013) is explicitly **NOT**
described in the literature as exact/orthogonal multiplexing. It is graceful: capacity is
~4-7 items, set by the number of gamma cycles nested in one theta cycle, and interference/precision
trades off smoothly with load — the same "soft" regime as the vacuous-decoupling examples above.
**If this substrate's phase-point-per-subsystem decoupling is genuinely hard-zero (provable, with
a closed-form threshold), that is a substrate-native mechanism that goes BEYOND what the brain
does in this specific respect** (exact/orthogonal addressing vs. the brain's statistical,
graceful multiplexing) — consistent with the "Frontier 2 / substrate-native affordances can beat
the brain" framing already active in this project. **If it turns out to be graceful/soft instead,
that is brain-parity, not a wall** — report it as parity, not as a failure to hit an exotic bar.

P_deflated = 0.45 for "the capacity-formula fix explains the 6x" (the underlying formulas are
directly cited from four independent sources; the specific claim that THIS substrate's 6x
decomposes as V_eff-effect x asymptotic-looseness is my own synthesis, not itself a cited result —
capped below the novel-synthesis ceiling per calibration policy).

P_deflated = 0.35 for "the measured decoupling is genuine" (the test design and the
orthogonality/RIP mechanism are citation-grade solid; whether THIS substrate's specific mechanism
actually satisfies the zero-interference condition is an open empirical question this drill did
not verify — it must be checked structurally then contention-tested, per Part B).

---

## (a) The corrected capacity theory — what quantity to compare, why the naive formula fails

**Plate (1994 PhD thesis; 1995 IEEE Trans. Neural Networks, "Holographic Reduced
Representations") — direct citation.** His own non-asymptotic bounds, in his notation (n =
dimension, m = number of *candidate vectors compared at cleanup*, q = target probability of >=1
decode error, k = number of items bundled):

- Bind-then-bundle (paired-associate) memory: `k > n / (16 ln(m^2/q)) - 2`
- Plain bundling (no binding): `k > n / (8 ln(m/q)) - 1`

Both are already non-asymptotic (finite-n, finite-m, explicit accuracy target q) — the familiar
`N/(4 ln V)` is a *further* simplification of these that (i) drops the additive offset
(`-2`/`-1`), (ii) folds the accuracy criterion q into a single fixed constant instead of leaving it
a free parameter, and (iii) — most importantly for this drill — silently assumes m (candidates
actually compared) equals the full codebook V. Plate's own derivation never treats V as a distinct
quantity from m; the crosstalk/union-bound term is built around the comparison set from the start.

**Frady, Kleyko & Sommer (Neural Computation, 2018), "A Theory of Sequence Indexing and Working
Memory in Recurrent Neural Networks" — direct citation.** They give the exact (not asymptotic)
recall-accuracy integral:

```
p_corr(s) = INTEGRAL over h of  N(h; 0, 1) * [Phi(h + s)]^(D-1)  dh
```

with **universal sensitivity** `s = sqrt(N / M)` (N = dimension, M = number bundled — this
relationship holds across HDC/HRR/FHRR/MBAT codings, a documented universality result) and **D =
the comparison-set size at cleanup** (their D plays exactly Plate's m role — again, NOT
necessarily the raw vocabulary). High-fidelity closed forms for the threshold sensitivity:

- Chernoff-Rubin bound: `s^2 = 4 [ ln(D-1) - ln(2*epsilon) ]`
- Tighter Chang bound (their recommended form, beta ~= 1.08):
  `s^2 = (4/beta) [ ln(D-1) - ln(2*epsilon) + ln( sqrt(2e/pi) * sqrt(beta-1) / beta ) ]`

**They explicitly state that the classical high-fidelity approximations (Plate-/Gallant-Okaywe-
style) underestimate true achievable capacity, and that the true maximum capacity — found by
numerically evaluating the exact integral rather than using the asymptotic bound — is
approximately 4x larger than what the classical approximations predict.** This is a *documented*
discrepancy in the same direction as your 6x miss (naive formula predicts too little capacity),
though not identical in magnitude — treat "4x + V_eff-effect approx-compounds-to-6x" as **my own
synthesis (extrapolation, not itself cited)**.

**Gallant & Okaywe (Neural Computation, 2013), MBAT — direct citation.** Same structural
derivation (`p = 1 - N*S*T(sqrt(D/(2S-1)))`, S = bundled count, N = comparison-set size, T =
Gaussian tail); their own simulations (their Table 2) show the required dimension for "90% of
top-S items correct" vs. "98% completely-error-free" differs by ~2.5x for the same S — a second,
independent, DOCUMENTED demonstration that the choice of accuracy criterion alone can move the
apparent cliff location by a large factor, fully separate from the V_eff issue.

**Thomas, Dasgupta & Rosing (JAIR, 2021), "A Theoretical Perspective on Hyperdimensional
Computing" — direct citation.** A more rigorous (sub-Gaussian concentration, not CLT-heuristic)
non-asymptotic incoherence framework: exact guarantee `mu < 1/(2s)` for perfect decoding of a
size-s subset (mu = mutual coherence), and a probabilistic version needing `d = O(s ln m)` — same
log-linear scaling family, m again explicitly the alphabet/comparison-set size.

**Reconstructed corrected formula (my synthesis, moderate confidence — not itself a citation):**
replace `K ~ N/(4 ln V)` with the Frady-et-al exact-integral evaluation (or, if a closed form is
preferred, the Chang-bound sensitivity relation above), substituting **V_eff = the actual number
of candidate vectors compared at cleanup time in this experiment's harness** for V, and fixing an
explicit target accuracy q/epsilon rather than leaving it implicit. **What to measure to verify:**
log the exact V_eff used by the cleanup step in the existing harness (this is very likely already
recoverable from the code without a new experiment) and recompute the predicted cliff with the
Chang-bound formula; if V_eff < V by roughly the missing factor, and the exact-integral correction
supplies the rest, the 6x collapses without any new theory.

**Sparse / block-sparse / correlated-key corrections (sub-agent 2, relevant since the substrate
uses block-sparse + a decorrelation front-end):**

- **Löwe (Ann. Appl. Probab., 1998)** — direct citation: correlated (Markov-chain-generated)
  patterns can still be stored in a Hopfield-type memory, with capacity `M = N / (gamma * log N)`,
  where gamma degrades explicitly as a function of the correlation parameter — correlation does
  NOT give a clean `N_eff = N*(1-rho)` rescaling (I did not find that closed form anywhere in the
  literature; treat any such simple rescaling as this project's own approximation, not a citation).
- **Structured block-sparse recovery thresholds are a genuine, admitted literature gap** — recent
  papers (2024-2025, e.g. arXiv:2411.09868) explicitly flag that closed-form phase-transition
  curves analogous to Donoho-Tanner for block/group-sparse recovery remain underexplored. Do not
  claim a precise block-sparse cliff-shift formula from the literature; it would need to be
  measured on this substrate directly.
- **Resonator networks / factorizers (Frady, Kent, Olshausen & Sommer, Neural Computation 2020;
  Hersche et al., arXiv:2303.13957)** — direct citation: capacity there is explicitly expressed
  relative to the **per-factor comparison-set size** (their M, analogous to V_eff/D/m above), not
  the combinatorial total across factors — the same "compare against a bounded candidate set, not
  the full combinatorial space" principle recurs a fourth independent time in this literature.
- **Decorrelation/pattern-separation front-ends (Marr 1971; Treves & Rolls 1994) raise downstream
  associative capacity** by reducing pattern overlap before storage — directly analogous to what a
  decorrelation front-end should be doing for this substrate's block-sparse codebook; well
  established, high confidence, direct citation.

---

## (b) What makes decoupling GENUINE — contention threshold + mechanism

**General theory (sub-agent 3, direct citations):**

- **Multiple-access / CDMA theory (Verdu 1986/1990; Tse & Hanly, IEEE Trans. Info Theory, 1999)**
  — orthogonal spreading codes give **exactly zero** mutual interference up to a hard ceiling
  (number of users = processing gain = code length); beyond that ("overloaded" CDMA) even optimal
  receivers leave residual interference that cannot be removed. Below the ceiling: truly flat
  zero. Above it: a genuinely different regime, not a gradual one.
- **Compressed sensing mutual-coherence / RIP (Candes-Tao)** is the cleanest general mechanism:
  exact recovery is guaranteed when `mu < 1/(2k-1)`, where **k is the LOCAL sparsity of one
  access, not the size of the shared dictionary** — this is exactly the "bounded per-access
  crosstalk" property this project already names as a candidate mechanism. mu=0 (true
  orthogonality) gives the hard CDMA-style ceiling; small-but-nonzero mu still gives *provably
  exact* recovery as long as each individual access's footprint stays under the threshold,
  independent of how many OTHER independent subsystems share the substrate.
- **Broadcast-channel superposition coding (Cover, 1998)** and **holographic multiplexing
  (angle/wavelength/phase-code)** are the counter-examples: both are documented as inherently
  SOFT — degrading continuously with load (a convex rate region in the coding case; crosstalk
  scaling with the medium's fixed dynamic range, `efficiency ~ (M#/M)^2`, in the holographic case).
  Even orthogonal phase-code multiplexing in holography only IMPROVES the SNR constant, it does
  not remove the continuous crosstalk-with-load scaling.
- **Modern Hopfield / correlated-pattern associative memory** is also documented soft: capacity
  degrades continuously and then collapses sharply near a threshold (Amit-Gutfreund-Sompolinsky);
  well-separated patterns (Ramsauer et al. 2020 exponential-capacity result) reduce interference
  but via a *coherence-like separation condition*, not a hard zero.

**Diagnostic test (my synthesis of the above, moderate-high confidence):** genuine architectural
decoupling is distinguished from vacuous decoupling by plotting interference vs. shared load and
checking for a **flat-zero segment followed by a knee whose location is predictable in advance
from a closed-form combinatorial/geometric formula** (orthogonal-subspace dimension split, or the
RIP/coherence threshold given the codes actually in use) — NOT a smooth, monotonically increasing
curve from K=0 (which is what every "soft" example above looks like). The mechanism-level
diagnostic: check whether the actual keys/subspaces used by the two subsystems are analytically
orthogonal (mu=0 exactly) or merely small-in-expectation for the tested N — the former supports a
hard ceiling, the latter is a soft-regime operating-point result that WILL degrade under enough
load, no matter how clean it looks at the tested point.

---

## (c) Biology cross-check — theta-gamma multiplexing, hippocampal capacity, concurrent systems

**Hippocampal capacity / pattern separation (direct citation).** Marr (1971) proposed CA3 as an
autoassociative net fed by dentate gyrus (DG) pattern separation; Treves & Rolls (1994; Rolls
2013, *Front. Cell. Neurosci.*) give quantitative capacity estimates (tens of thousands of
patterns, strongly dependent on activity sparseness) — capacity rises because DG's very sparse
(2-6% active), decorrelated codes keep stored patterns near-orthogonal *before* CA3 storage. This
is the biological analogue of a decorrelation front-end raising downstream associative capacity —
directly relevant to weakness-1's sparse/decorrelation correction above (same mechanism, same
citation family as sub-agent 2's item 5).

**Theta-gamma phase coding as the brain's "phase diagram" (direct citation).** Lisman & Idiart
(*Science*, 1995) and Lisman & Jensen (*Neuron*, 2013, "The Theta-Gamma Neural Code") propose
that each of ~4-7 working-memory items is carried in one gamma sub-cycle nested within a slower
theta cycle; item capacity = number of gamma cycles that fit in one theta cycle (supported by
tACS studies: slowing theta increases capacity, speeding it decreases capacity — a direct,
mechanistic, testable relationship, not just a correlational number).

**Is this exact/orthogonal multiplexing or graceful multiplexing?** The literature explicitly
frames it as GRACEFUL, not exact — Lisman & Jensen describe gamma bursts as "gating access to and
limiting" interference, and behavioral/computational models of the scheme show capacity and
precision trading off smoothly with load (stable-limit-cycle attractors per item, not hard
channel isolation). **This is the same "soft" regime as CDMA overload / VSA superposition
crosstalk / holographic dynamic-range crosstalk** — moderate-confidence synthesis across sources,
not one paper's explicit claim, but consistent across everything found.

**Concurrent memory systems without interference (direct citation).** McClelland, McNaughton &
O'Reilly (*Psychological Review*, 1995, Complementary Learning Systems) is the canonical account:
the hippocampus (sparse, pattern-separated, fast-learning) and neocortex (slow, overlapping,
distributed) avoid catastrophic interference through *different learning rates and representational
overlap*, not shared-circuit multiplexing — replay-driven systems consolidation interleaves new
memories into cortex gradually offline. This is a structurally DIFFERENT decoupling mechanism from
theta-gamma phase multiplexing (separation by learning dynamics/representation, not by
time/phase-slot) — worth distinguishing in the substrate-product framing: the substrate's
phase-point-per-subsystem decoupling is the theta-gamma-style analogue (same-time, same-buffer,
different addressing), not the CLS-style analogue (different subsystems entirely).

**Bottom line for framing:** the brain's own concurrent-memory mechanisms are ALL graceful/soft
at the phase-multiplexing level (theta-gamma) and use an entirely different mechanism (learning-
rate/representational separation, not phase addressing) for true architectural independence (CLS).
Neither brain mechanism achieves a hard, RIP/orthogonality-style zero-interference ceiling of the
kind engineering multiplexing theory (CDMA, RIP) says is achievable in principle. **A substrate
that demonstrates a genuine hard-zero decoupling would be doing something the brain does not do**
— a legitimate substrate-native (Frontier-2) claim, but ONLY if Part B of the experiment design
below actually confirms the hard-zero/knee signature; absent that, report graceful/brain-parity.

---

## Cheap decisive test

**Part A (capacity-formula reconciliation) — near-zero new compute, reuses existing data.**
Before running anything new: (1) extract V_eff (the actual candidate-set size compared at cleanup
in the existing harness) from the code/config that produced the mismatched measurement — this is
very likely already recoverable without a new run; (2) recompute the predicted K_cliff using the
Frady-et-al Chang-bound formula (`s^2 = (4/beta)[ln(V_eff-1) - ln(2*epsilon) + ...]`, solved for K
via `s = sqrt(N/K)`) with V_eff substituted for the raw V used in the original naive prediction;
(3) compare the corrected prediction against the already-measured cliff. If this alone collapses
most of the 6x gap, the mechanism is confirmed essentially for free.

**Part B (decoupling genuineness) — one new dedicated cell, CPU-cheap.** See experiment design
below; reuses the existing two-subsystem/shared-buffer setup, just extends the load sweep and adds
a misplacement control.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Capacity-formula reconciliation:**
- **HARD-PASS:** using V_eff (not raw V) plus the exact-integral/Chang-bound formula, predicted
  K_cliff lands within +/-20% of measured, averaged across a grid of >= 8 (N, V, K) cells, AND the
  V_eff-corrected prediction reduces mean absolute relative error by >= 3x versus the naive
  `N/(4 ln V)` prediction. This confirms V_eff + exact-formula is the resolving mechanism, no new
  theory needed.
- **MIDDLE_BAND:** error reduced 1.5-3x but residual > 20% average — real partial explanation;
  something else (correlation structure in the actual codebook, finite-N corrections beyond the
  Chang bound) still needed.
- **HARD-FAIL:** corrected formula does not outperform the naive one by >= 1.5x error reduction —
  the 6x miss is NOT explained by V_eff/exact-vs-asymptotic and a substrate-specific mechanism
  (e.g. codebook correlation structure, block-sparse interaction effects) is actually responsible;
  pivot to measuring the codebook's own covariance/coherence structure directly.

**Decoupling genuineness:**
- **HARD-PASS:** interference (degradation in subsystem B's recall given increasing subsystem-A
  load, and vice versa) stays statistically indistinguishable from zero up to a threshold
  predicted IN ADVANCE from the closed-form orthogonality/RIP condition of the actual codes in
  use (within ~15% of predicted knee location), THEN rises sharply — AND a deliberately
  misaligned-addressing control (same nominal loads, non-orthogonal/overlapping keys) shows
  interference rising immediately/gradually from K=0 with no flat region. This confirms genuine,
  nameable architectural decoupling.
- **MIDDLE_BAND:** a flat-zero region exists, but the knee location is not well-predicted by the
  closed-form threshold (> 30% off) — decoupling is real but its mechanism is not yet fully
  characterized; needs more theory before a chain-grade mechanism claim.
- **HARD-FAIL:** interference rises smoothly from K=0 in the "genuine" condition too, statistically
  indistinguishable from the misplacement control — the original zero-interference result was a
  vacuous low-load operating-point artifact; must be walked back to "no interference observed in
  the tested regime," not "decoupled." This would also mean the substrate's multiplexing is in the
  brain's own graceful/soft regime (theta-gamma-like), which is not a failure per se — report as
  brain-parity, and re-scope the claim accordingly.

---

## Concrete dedicated experiment design (predict-then-verify grid + genuine-contention decoupling)

**Part A grid (capacity reconciliation, CPU-cheap, reuses existing bundle/cleanup primitives):**
- N in {512, 1024, 2048, 4096}; raw codebook V in {100, 1000, 10000}.
- Two cleanup conditions per (N, V) cell, to directly separate the V-vs-V_eff effect:
  1. `FULL_CODEBOOK` — cleanup compares against all V candidates (V_eff = V).
  2. `RESTRICTED_SET` — cleanup compares against a fixed smaller candidate subset, e.g.
     `V_eff = sqrt(V)` or a fixed size (e.g. 32), matching how a realistic query-time comparison
     set is likely to be constructed.
- For each of the 4x3x2 = 24 cells, sweep K finely near the predicted cliff (both naive and
  corrected predictions bracket the sweep range), measure the empirical 0.5-recall crossing.
- Compute and log, per cell: naive prediction (`N/(4 ln V)`), corrected prediction (Chang-bound
  with V_eff), and measured K_cliff. Report mean absolute relative error for each formula across
  the grid.

**Part B contention grid (decoupling genuineness, one new cell, CPU-cheap):**
- Reuse the existing two-subsystem/shared-buffer setup at its previously-tested phase-points.
- `GENUINE` condition: sweep (K_A, K_B) — the respective loads of subsystem A and B sharing the
  buffer — over a 2D grid extending well past the originally-tested point in both directions.
  Measure subsystem B's recall degradation as a function of K_A (holding K_B fixed at its tested
  value), and symmetrically A's degradation as a function of K_B.
- Before running: compute the theoretically-predicted contention threshold from the actual
  addressing mechanism in use (orthogonal-subspace dimension split if that's the mechanism;
  combined-sparsity/coherence bound if it's RIP-style bounded-access).
- `MISPLACEMENT_CONTROL` condition: repeat the identical (K_A, K_B) sweep, but with subsystem A
  and B's addressing deliberately misaligned (overlapping/non-orthogonal keys instead of the
  actual orthogonal/structured addressing) at the same nominal loads — this isolates whether the
  original zero-interference result came from the addressing mechanism itself, or merely from
  the loads being low in absolute terms.

---

## Cross-thread synthesis

- `notes/research_brain_N_sparse_capacity_cost_decoupling_2026-07-16.md` — yesterday's companion
  drill already established the textbook capacity math (Willshaw/Tsodyks-Feigel'man/Amari),
  confirmed this project's own block-sparse resonator primitive (`data/exp_substrate_sparse_
  resonator_blocklocal_K26_v1_n5000/metrics.json`, K4=1.00/K8=1.00 factor recall) as an
  already-proven, reusable building block, and flagged the "superposition catastrophe is a sharp
  cliff, not smooth degradation" shape independently. This drill's Part A grid should reuse that
  exact primitive as the decode path (resonator/factorizer, sub-N cost) rather than a brute-force
  argmax scan, per that note's "search-cost sanity check" discipline — otherwise a capacity win
  here would be confounded by an uncontrolled cost change.
- Same note's citation of **Löwe (1998)** on correlated-pattern Hopfield capacity and the
  **admitted literature gap on block-sparse phase transitions** (arXiv:2411.09868, this cycle)
  both bear directly on weakness-1's "sparse/correlated-key corrections" sub-question — treat any
  precise block-sparse cliff-shift number as something this substrate would need to MEASURE, not
  something available off-the-shelf from the literature.
- `notes/exp_dev_to_research_sparse_value_CLOSED_2026-06-08.md`,
  `notes/exp_dev_to_research_DIMSPARSE_result_2026-06-06.md` — prior HARD-FAIL closures on naive
  value-sparsification are unrelated to this drill's capacity-formula question but relevant to
  Part A grid design: if a sparse/block-sparse codebook variant is tested, the "pattern/key
  sparsity vs value sparsity" distinction from these notes must be respected in interpreting any
  cliff-location shift.
- `notes/research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md` —
  already raised theta-gamma-style chunking as an open menu item for bundling capacity; this
  drill's biology section (Lisman & Idiart / Lisman & Jensen, graceful not exact multiplexing) is
  the correct, citation-grounded characterization to use if that menu item is picked up next —
  do not frame theta-gamma as a hard-multiplexing precedent; it is a soft one.
- No prior note in this project's notes/ directory addresses the V-vs-V_eff (comparison-set vs
  codebook) distinction directly — this is a genuinely new angle for this drill, not a repeat of
  prior capacity-cliff work (which focused on M/N ratios and codebook-clustering effects, e.g.
  `notes/exp_dev_to_research_CELL_A_B_VERDICT_COMPOSITION_DECOMPOSITION_NO_CAPACITY_CLIFF_CEILING_IS_CLUSTERED_CODEBOOK_2026-06-12.md`,
  which is adjacent but orthogonal — that note is about codebook clustering shifting the cliff;
  this drill is about which SIZE quantity (V vs V_eff) belongs in the formula at all. Worth a
  follow-up cross-check between the two findings: codebook clustering could itself be reframed as
  an effective-V-reduction effect, which would unify both notes under one mechanism.

---

## Substrate-product implications

Framed as product roadmap, not publication. If Part A HARD-PASSes: the substrate gains a
**correctly-calibrated, predictive capacity formula** (not just a measured curve) — meaning future
capacity/cost tradeoffs (how much N is needed for a target K at a target V_eff) can be computed in
advance rather than empirically re-discovered per configuration change. That is a genuine
observability/predictability win, consistent with this project's "glass-box, computable, not
curve-fit" positioning. If Part A HARD-FAILs, it redirects effort productively: toward measuring
and correcting for the actual codebook's correlation/coherence structure, which is itself a
capability this substrate can expose (glass-box access to its own codebook statistics) that no
opaque LLM-style memory can offer.

If Part B HARD-PASSes with a hard-zero knee: the substrate can make a genuinely differentiated
product claim — **exact, provable multi-tenant memory isolation on a single shared substrate**,
something the brain itself does not achieve at the phase-multiplexing level (its own concurrent-
memory mechanisms are either graceful/soft, like theta-gamma, or achieved via an entirely separate
mechanism, like CLS's learning-rate/representation split, not shared-buffer phase addressing).
This is a legitimate substrate-native (beat-the-brain) capability claim, but must not be asserted
until Part B's misplacement control is actually run — an unverified "decoupled" claim that turns
out graceful-not-exact would be an overclaim this project's discipline explicitly guards against
(NO SMOKE; never frame a soft operating point as a hard ceiling).

---

## Citations (verified count)

**~30 distinct sources, live WebSearch-verified this cycle across 4 independent Sonnet lit-scan
sub-agents** (a few sources recur across sub-agents; counted once):

- **Capacity theory core:** Plate 1994 PhD thesis + 1995 IEEE Trans. Neural Networks
  ("Holographic Reduced Representations"); Frady, Kleyko & Sommer 2018 *Neural Computation* ("A
  Theory of Sequence Indexing and Working Memory in RNNs"); Gallant & Okaywe 2013 *Neural
  Computation* (MBAT); Thomas, Dasgupta & Rosing 2021 *JAIR* ("A Theoretical Perspective on
  Hyperdimensional Computing"); Kanerva Sparse Distributed Memory (background).
- **Sparse / correlated-key / random matrix:** Donoho-Tanner compressed-sensing phase transitions;
  Donoho, Johnstone & Montanari, arXiv:1111.1041 (PNAS, AMP phase-transition-denoiser link);
  Barron & Joseph (ISIT 2010/2011, sparse superposition codes); Rush, Greig & Venkataramanan 2017;
  Löwe 1998 *Ann. Appl. Probab.* (correlated-pattern Hopfield capacity); arXiv:2505.11948
  (spectral density of correlated hetero-associative memory); arXiv:2411.09868 (structured/block
  sparsity phase transitions, admitted open gap); Frady, Kent, Olshausen & Sommer 2020 *Neural
  Computation* (Resonator Networks 1 & 2); arXiv:2412.00354 (noise in factorizers); arXiv:
  2303.13957 (Hersche et al., Factorizers for Distributed Sparse Block Codes); Marr 1971; Treves
  & Rolls 1994/2013; Yassa & Stark 2011 *Trends Neurosci.* (DG pattern separation review).
- **Multiplexing / decoupling:** Verdu 1986/1990 (multiuser detection, near-far resistance); Tse
  & Hanly 1999 *IEEE Trans. Info Theory* (effective interference / effective bandwidth); Cover
  1998 (broadcast-channel superposition coding); holographic angle/wavelength/phase-code
  multiplexing crosstalk literature (ScienceDirect); Amit-Gutfreund-Sompolinsky Hopfield capacity;
  Ramsauer et al. 2020 (modern/exponential-capacity Hopfield); arXiv:2503.09518; Candes-Tao
  restricted isometry / mutual coherence.
- **Biology cross-check:** Lisman & Idiart 1995 *Science* ("Storage of 7 +/- 2 Short-Term
  Memories in Oscillatory Subcycles"); Lisman & Jensen 2013 *Neuron* ("The Theta-Gamma Neural
  Code"); McClelland, McNaughton & O'Reilly 1995 *Psychological Review* (Complementary Learning
  Systems); Cowan 2001 *Behav. Brain Sci.* ("The Magical Number 4"); Miller 1956 (magic number 7,
  historical reference); hippocampal-prefrontal theta-gamma coupling, *Nature Communications*
  2017.

**Calibration applied per [[feedback-lit-scan-calibration-penalty]]:** the underlying capacity
formulas (Plate/Frady-Kleyko-Sommer/Gallant-Okaywe/Thomas-Dasgupta-Rosing) are treated as HIGH
confidence (direct citations, cross-derived independently by 4 groups over 3 decades). Deflated to
P_deflated=0.45 (capacity fix) and 0.35 (decoupling genuineness) because: (1) the specific claim
that THIS substrate's 6x miss decomposes as V_eff-effect x asymptotic-looseness is this drill's own
synthesis, not a directly cited result — it must be verified against this substrate's actual V_eff
before being asserted as the explanation; (2) whether the measured decoupling satisfies the
RIP/orthogonality condition for a hard-zero ceiling is a genuinely open, unverified empirical
question — the mechanism theory is solid but its applicability to this specific substrate has not
been checked; (3) both estimates are capped below the 0.50 novel-synthesis ceiling per policy.

---

## Next-drill candidate

If Part A HARD-PASSes: drill `sparse-coding-compressed-sensing` (Tier-1b, already flagged adjacent
to free-probability/AMP-VAMP) specifically on the block-sparse phase-transition gap
(arXiv:2411.09868 flags this as unresolved in the literature) — this substrate's own Part-A grid
data would be a genuine, publishable-quality (product-framed: "first measured") contribution to a
literature-acknowledged open question.
If Part A HARD-FAILs: pivot to measuring the actual codebook's coherence/correlation structure
directly (a `network-science-graph-theory` / `free-probability` adjacent angle — codebook Gram
matrix eigenvalue tail, per the F2/F4 Tier-1 candidates already on the field advisor's list).
If Part B HARD-PASSes: `mesoscopic-transport` (Tier-1b, Landauer-Buttiker multi-terminal
formalism) is the next-adjacent field — multi-tenant shared-substrate capacity is structurally a
multi-terminal transport/conductance problem once a hard-zero threshold is confirmed.
