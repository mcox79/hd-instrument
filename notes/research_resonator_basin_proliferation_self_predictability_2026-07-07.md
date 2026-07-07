# RESEARCH — 2x negative-revival drill: mechanism + self-predictability of the resonator's
# K-dependent convergence-basin collapse (candidate 4th self-margin family)

**Date:** 2026-07-07
**Author:** research (Sonnet 5, fresh spawn)
**Trigger:** USER-triggered 2x negative-revival on `research_self_margin_taxonomy_held_out_validation_
resonator_2026-07-06.md`, which HARD-FAILED the 3-family self-margin taxonomy against
`exp_resonator_capacity_gpu_v1` (K2=1.0, K3=0.7, K4=0.142, N=4096, M=30) and diagnosed — but did not
derive — a 4th mechanism: **convergence-basin proliferation** in the resonator's recurrent
alternating-projection decode. This drill goes deeper: (1) pins down the mechanism against real
theory, (2) attempts an actual basin-counting derivation to see if it is self-predictable, (3) renders
an honest envelope-push verdict.

**Method:** field advisor run (confirms `dynamics` field closed at 0% yield, "Arnold tongue REFUTED" —
explicitly a DIFFERENT phenomenon from what's investigated here, see (d)); 3 parallel Sonnet lit-scan
sub-agents (generic math terms only, per query-privacy); substrate history scour
(`wave14b_noise_resonator_failure_research.md`, 2026-05-19; `research_K_resonance_2026-05-23.md`;
`substrate_capability_map.md` row 51); own off-disk derivation + numeric verification (CPU, numpy,
zero new trials of the actual GPU resonator — verifying my own hand-algebra, not re-running the
capability under test).

---

## (a) HEADLINE

**Mechanism: CONFIRMED as convergence-basin proliferation (spurious joint fixed points), cross-validated
by 3 independent literature searches AND by this substrate's own 2026-05-19 history, which already
correctly identified the exact right paper family for this phenomenon two months before this cell was
even built.** All three lit-scan sub-agents, searching independently (resonator-capacity theory;
Hopfield/AGS spurious-mixture-state theory; general multistability/K-SAT-clustering theory), converge on
the SAME two-part answer: (1) the qualitative mechanism — coupled iterative joint search accumulates
spurious stable fixed points combinatorially faster than any single-shot SNR argument predicts — is
real, well-established, and cited across 4 independent sub-literatures; (2) **no ready-made closed-form
formula exists anywhere in the literature that predicts joint-success-probability as an explicit
function of a small factor-count K (2,3,4)** — the founding resonator-network papers (Frady, Kent,
Olshausen, Sommer, Neural Computation 2020) say so IN PRINT ("our attempts to analytically derive this
result were stymied"), and every successor (Hersche et al. 2023, Karunaratne/Langenegger et al. 2024)
remains simulation/empirical-fit only.

**Self-predictability (the revival question): NO, not this cycle — but this is an EFFORT/SCOPING
boundary, not a FUNDAMENTAL one.** I attempted my own basin-counting derivation (below) and got real,
verifiable partial traction (a previously-unnoticed initialization bias, confirmed to machine precision;
a combinatorial-count sanity check that is honestly reported as failing by ~10x, which is itself
diagnostic, not a dead end) but did NOT complete a working K-explicit closed form this cycle. **No 4th
CG-tier self-margin family is minted today.** Unlike control's autonomous-decomposition row (8b in the
frontier map, which resists closed form for a *structural* reason — dependence on a learned function's
out-of-distribution generalization, not derivable from first principles even in theory), this mechanism
is, in principle, a well-posed annealed/first-moment counting problem (the same machinery that gives
Amit-Gutfreund-Sompolinsky's `3^p` spurious-mixture-state count, Bray-Moore/Kac-Rice TAP complexity, and
K-SAT solution-clustering counts) that has simply not been completed for this substrate's specific
update rule. That is a real, scoped, tractable-in-principle follow-up research project — not a
memorialized dead end.

**Envelope-push verdict: the honest verdict is "single-shot/chain-composed decode is self-predictable
(3-family taxonomy holds, unchanged); recurrent-search decode is NOT YET self-predictable, pending a
genuinely new (not-yet-built) annealed basin-counting derivation."** This does NOT open a fresh CG_META
attempt today. It DOES open two concrete, well-scoped, differently-timescaled follow-ups: (i) a cheap,
near-term EMPIRICAL rescue attempt — apply this substrate's OWN already-validated ACF (Asymmetric
Codebook Factorizer) technique, proven to extend resonator capacity on the *codebook-size* axis
(cap_map row 51, "Resonator decomposition with ACF rescue," validated 50x+ gain), to the untested
*factor-count* axis (this cell's K=2,3,4) — and (ii) a longer-horizon THEORY project — complete the
annealed basin-counting derivation sketched below, which literature says is original work, not
retrieval.

---

## (b) Cheap decisive test (executed this drill, zero new trials of the actual resonator)

Two off-disk numeric checks, run live this cycle on CPU (`.venv/Scripts/python.exe`, numpy) to verify my
own hand-derivation against the resonator's exact code (`experiments/exp_resonator_capacity_gpu_v1.py`),
not against the GPU capability itself:

**Check 1 — the "flat start" is not actually uninformative (a previously-unstated fact about the
mechanism).** The resonator initializes each factor's estimate as `est[k] = mean(books[k])`, normalized.
Because the TRUE codeword is literally one of the `M` vectors being averaged, this initialization has a
deterministic coherent bias toward the true codeword baked in, even before any iteration:

```
predicted signal term   N/M              = 136.53
predicted noise std     sqrt((M-1)N/2)/M = 8.12
predicted z_init = signal/noise          = 16.81   (== sqrt(2N/(M-1)))

EMPIRICAL (400 fresh random books, CPU verification of the algebra only):
  mean dot(book_true, mean_vec).real     = 137.17   (predicted 136.53)
  std  dot(...)                          = 8.09     (predicted 8.12)
  empirical z (mean/std)                 = 16.95    (predicted 16.81)
```

The hand-derivation matches to within 1%. This REFINES (does not overturn) last cycle's honest
diagnosis: the collapse is not from a fundamentally blind start — each factor, decoded IN ISOLATION at
iteration 0, already carries a real (z~17) signal. The catastrophic K-dependent collapse must therefore
come from how the MULTIPLICATIVE COUPLING across K factors erodes this per-factor initial signal through
the `others = product_{j != k} est[j]` unbinding step and its feedback over up to 60 iterations — exactly
the "coupled recurrent dynamics," not "no signal at all," framing.

**Check 2 — naive constant-capture-probability annealed count: HARD-FAILS, informatively.** The simplest
possible first-moment model (AGS-style): if the probability any ONE specific wrong joint configuration
becomes a captured spurious fixed point were roughly constant in K, total spurious-capture probability
would track the raw count of wrong configurations, `M^K - 1`:

```
M^K - 1 at K=2: 899   K=3: 26999   K=4: 809999
raw wrong-config count GROWTH ratio, K3->K4: 30.0x   (== M, exactly, as expected)

observed (1 - success): K2=0.000 (saturated)  K3=0.300  K4=0.858
observed FAILURE-RATE growth ratio, K3->K4:    2.86x
```

The naive model predicts ~30x more failure at K4 than K3; the substrate shows only 2.86x more — a ~10x
mismatch. **This is itself a genuine, informative finding, not noise**: it means the per-configuration
capture probability is NOT constant in K — it must itself be SHRINKING as K grows (each additional
coupled factor makes any SPECIFIC wrong joint configuration progressively harder to lock onto
self-consistently, partially offsetting the exploding number of wrong configurations available). This
is exactly the residual term a real annealed-counting derivation would need to solve for, and is
reported here as partial progress + an honest wall, not force-fit into an answer.

**Falsifiable status of these two checks:** Check 1 is confirmatory (HARD-PASS on its own narrow claim —
predicted vs. measured z_init within 1%). Check 2 is a diagnostic HARD-FAIL of the simplest possible
rescue model, which is valuable precisely because it rules out the laziest closed form and localizes
where the real derivation effort must go (K-dependence of per-configuration stability, not just K-dependence
of configuration count).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL) — for the two concrete follow-ups, not yet run

**Follow-up 1 (empirical, near-term, cheap) — ACF-rescue transfer to the factor-count axis.**
`experiments/exp_wave14b_acf_resonator.py` (and siblings `..._acf_K_dependent.py`,
`..._acf_K_dependent_extended.py`) already validated ACF (bit-flip mask on a SEPARATE reconstruction
codebook + hard-threshold activation, Karunaratne/Langenegger et al. 2024) on the *codebook-size* axis
of this exact same resonator-network capacity surface, at FIXED factor-count `F=2` (cap_map row 51,
validated, 50x+ capacity gain). `exp_resonator_capacity_gpu_v1` is the ORTHOGONAL axis of the same
Frady-Sommer capacity surface (factor-count K=2,3,4 at fixed codebook size M=30) and has NEVER been
tested with ACF — it is a naive resonator, no noise/asymmetry rescue at all. Concrete, scoped,
well-precedented test: adapt the ACF template to sweep K in {3,4,5,6} at fixed M, N.
- **HARD-PASS:** ACF-rescued K4 success >= 0.75 (MIDDLE-band-or-better on the ORIGINAL cell's own
  pre-registered bands) AND K4/K3 ratio improves by >= 1.5x over the naive baseline's 0.142/0.7=0.203
  ratio.
- **HARD-FAIL:** ACF-rescued K4 success stays < 0.30 (no material rescue) OR the K4/K3 ratio is
  unchanged (<= 1.2x the naive baseline ratio) — meaning the factor-count axis's basin proliferation is
  NOT the same failure mode ACF fixes on the codebook-size axis (a real, informative negative: the two
  axes would then be mechanistically distinct despite both being "resonator capacity cliffs").

**Follow-up 2 (theory, longer-horizon) — complete the annealed basin-counting derivation.**
Sketch of the 4th-family mathematical object (NOT yet derived, scoped for a future cycle): a
"complexity"-style function, analogous to AGS's spurious-mixture-state count and Bray-Moore/Kac-Rice TAP
complexity, `Sigma(K) = log[ sum over the M^K - 1 wrong joint configurations of P(configuration is a
locally-stable fixed point of the update AND is reached from the mean-of-codebook initial condition
within MAXIT iterations) ]`, with the per-configuration capture probability itself expanded via the
`2^(K-1)`-term crosstalk decomposition partially sketched in (b) (coherent term `prod_j m_j` vs. `2^(K-1)-1`
independent-random-phase cross terms). This is a real, well-posed, historically-precedented mathematical
program (same family as AGS/TAP/K-SAT annealed counting) — literature confidently says it does not exist
yet; it does NOT say it is impossible.
- **HARD-PASS (promotes to CG_META 4th family):** a completed derivation reproduces K3=0.7 and K4=0.142
  (or a fresh K=5/K=6 held-out point) within the SAME `<=1.5x` per-cell / `[0.80,1.25]` aggregate bands
  used for the other 3 families, with the classification not revised after seeing the fit.
- **HARD-FAIL (stays ACCEPT-boundary, same as today):** no closed form is found that clears those bands,
  or any fit found requires more free parameters than data points (over-fit, not a real law).

---

## (d) Cross-thread synthesis

- **Directly resolves, and sharpens, the open question left by
  `research_self_margin_taxonomy_held_out_validation_resonator_2026-07-06.md`**: that note diagnosed
  "convergence-basin phenomenon... closer to multi-basin/spin-glass mean-field dynamics" but explicitly
  declined to pursue a derivation ("I am NOT claiming this diagnosis IS a new closed form"). This drill
  took the next step and confirms, via 3 independent literature searches, that the diagnosis was
  correctly aimed (AGS mixture-state counting, TAP/Kac-Rice complexity, K-SAT clustering ARE the right
  reference class) but that completing it is original theoretical work, consistent with — not
  contradicting — last cycle's restraint.
- **Confirms and sharpens the substrate's own `dynamics` field closure.** The field-advisor flags
  `dynamics` as 0%-yield, "Arnold tongue REFUTED" (from `research_K_resonance_2026-05-23.md`, which
  investigated period-1 fixed points at K=1000 in a DIFFERENT capability — an N=65536 iterated-argmax-W^L
  map — via eigenvalue-commensurability/mode-locking theory, and found no clean K-boundary fit). Lit-scan
  sub-agent 3 this cycle explicitly confirmed, with citations, that Arnold tongues (frequency-locking
  regions for periodically-forced/coupled OSCILLATORS, parametrized by rotation number, bounded by
  saddle-node bifurcations of periodic orbits) are a DIFFERENT mathematical object from basin/attractor
  multiplicity in an autonomous discrete-time alternating-projection search (bounded instead by
  saddle-node/pitchfork creation of new FIXED-POINT basins, no forcing frequency involved). **The
  `dynamics` field's 0%-yield closure is specifically about mode-locking claims and does NOT preclude
  basin-counting/multistability theory being live and useful here** — exactly the
  don't-dismiss-adjacent-methods discipline the role contract flags as the dominant failure mode.
- **Reconciles with, and meaningfully extends, this substrate's own 2026-05-19 history.**
  `wave14b_noise_resonator_failure_research.md` already independently identified Frady-Kent Resonator
  Networks (arXiv:1906.11684 / Neural Computation 32(12):2332) and Karunaratne-Langenegger et al. 2024
  (arXiv:2412.00354, "On the Role of Noise in Factorizers") as the exact right literature for resonator
  capacity cliffs, TWO MONTHS before `exp_resonator_capacity_gpu_v1` was built — and validated ACF on the
  codebook-size axis of the SAME capacity surface (cap_map row 51). This drill's independent 2026-07-07
  lit-scan (3 fresh Sonnet sub-agents, no prompt-priming with the prior note's citations) converged on
  the IDENTICAL paper family from scratch, which is itself a strong cross-validation signal that this is
  genuinely the right reference class, not a coincidence of query framing.
- **Does not reopen any of the 3 closed RESISTOR rows** (encoder power-law spectrum, generalization
  entropy ceiling, control-autonomous-decomposition `O(T^2)` compounding) from the self-margin frontier
  map — this drill adds a 4th INSTANCE of "collapse mechanism outside the order-statistic/collision/
  chain trio," independently arrived at, that is qualitatively DIFFERENT from all 3: unlike those three,
  it is not (yet) proven to resist closed form in principle — it is an open, tractable-in-principle
  research program, honestly incomplete rather than honestly closed.

---

## (e) Substrate-product implications

- **No product claim changes today.** The 3-family self-margin taxonomy's product claim ("the substrate
  knows, in closed form, where 4-5 of its core capabilities will collapse") is unaffected — it never
  included resonator-style recurrent-search decode, and still doesn't. No overclaim, no walk-back needed.
- **A concrete, low-risk, well-precedented experimental opportunity is newly visible and directly
  actionable:** applying this substrate's OWN already-validated ACF rescue (cap_map row 51, 50x+ gain on
  the codebook-size axis) to the untested factor-count axis (`exp_resonator_capacity_gpu_v1`'s K=2,3,4
  cliff) is NOT speculative theory — it is re-applying a proven-on-this-substrate technique to an
  adjacent, previously-untried axis of the identical published capacity surface (Frady-Sommer 2020;
  Karunaratne-Langenegger 2024 explicitly study BOTH axes, factor-count F and codebook-size D, and this
  substrate has only ever tested the ACF rescue at fixed F=2). Template file: 
  `experiments/exp_wave14b_acf_resonator.py` (and `_acf_K_dependent.py`,
  `_acf_K_dependent_extended.py` for the sweep-harness pattern). If it lands, the product gains "K-way
  concept factorization survives past the naive capacity cliff" as a reusable capability claim,
  analogous to the already-validated "pool retrieval survives past naive capacity cliff via ACF" claim.
  If it HARD-FAILs per the bands in (c), that is ALSO valuable: it would show the two axes of the same
  named capacity surface are mechanistically distinct despite superficial similarity, a genuine and
  reportable negative.
- **A real, scoped, non-urgent theory-building opportunity exists** (the annealed basin-counting
  derivation, (c) Follow-up 2) but should NOT be prioritized over the cheap empirical ACF-transfer test —
  the empirical route is faster, cheaper, already-precedented-on-this-substrate, and would itself supply
  the richer per-trial data (recurring-wrong-idxs signature, per (c)'s proposed mechanism-signature test)
  that the theory route currently lacks (today's `metrics.json` only stores aggregate success rate per K,
  not per-trial converged indices — a real, fixable, cheap instrumentation gap for any follow-up cell:
  log `idxs` per trial to enable the "do specific wrong joint labelings recur across trials" smoking-gun
  test for genuine spurious ATTRACTORS vs. pure noise).

---

## (f) Citations (verified count)

**Lit-scan sub-agent 1 (resonator-network capacity theory), 5 sources, all fetched/verified via
WebSearch/WebFetch:**
1. Frady, Kent, Olshausen, Sommer, "Resonator networks for factoring distributed representations of data
   structures," Neural Computation 32(12):2311-2331 (2020), arXiv:2007.03748.
2. Frady, Kent, Olshausen, Sommer, "Resonator Networks, 2: Factorization Performance and Capacity
   Compared to Optimization-Based Methods," Neural Computation 32(12):2332-2388 (2020),
   arXiv:1906.11684. Full text fetched: sec 6.2 explicitly states the N^2 capacity scaling is fit from
   simulation, not derived, and that analytical derivation "stymied" the authors.
3. Hersche, Terzić, Karunaratne, Langenegger, Pouget, Cherubini, Benini, Sebastian, Rahimi, "Factorizers
   for Distributed Sparse Block Codes," arXiv:2303.13957 / DOI 10.3233/NAI-240713. Sec IV-F/G:
   qualitative spurious-fixed-point description; one closed form (Eq. 11) is for a degenerate
   random-sampler toy variant only, not the real alternating-projection dynamics.
4. "On the Role of Noise in Factorizers for Disentangling Distributed Representations,"
   arXiv:2412.00354 (OpenReview VYryqVqQEF). Measured F=2..4 capacity-vs-noise curves; no derived
   K-explicit equation.
5. "In-memory factorization of holographic perceptual representations," Nature Nanotechnology (2023);
   github.com/IBM/in-memory-factorizer (context only).

**Lit-scan sub-agent 2 (Hopfield/AGS spurious-attractor + basin-counting theory), 10 sources:**
6. Amit, Gutfreund, Sompolinsky, "Spin-glass models of neural networks," Phys. Rev. A 32:1007 (1985).
7. Amit, Gutfreund, Sompolinsky, "Storing infinite numbers of patterns in a spin-glass model of neural
   networks," Phys. Rev. Lett. 55:1530 (1985).
8. Amit, Gutfreund, Sompolinsky, "Statistical mechanics of neural networks near saturation," Ann. Phys.
   173:30 (1987).
9. Ramsauer et al., "Hopfield Networks is All You Need," arXiv:2008.02217 (2020).
10. Krotov & Hopfield, dense associative memory (2016); Demircigil et al. (2017) — exponential-capacity
    interaction-order results (context, via arXiv:2504.04879 "Mixed memories in Hopfield networks").
11. "Legendre structure of TAP complexity," arXiv:2604.20660 (2026) — modern Kac-Rice/TAP-complexity
    framing.
12. Parisi & Potters, "On the number of metastable states in spin glasses."
13. Mezard, Mora, Zecchina, PRL 94:197205 (2005) — K-SAT clustering.
14. Krzakala, Montanari, Ricci-Tersenghi, Semerjian, Zdeborova, PNAS (2007) — K-SAT gap.
15. Montanari & Semerjian, "Clusters of solutions and RSB in random k-SAT," J. Stat. Mech. (2008),
    iopscience P04004.

**Lit-scan sub-agent 3 (general multistability + Arnold-tongue-vs-basin-counting distinction), 8 sources:**
16. Richardson & Urbanke, density evolution / fixed points of density evolution (via Projecteuclid).
17. "Fixed Points of Belief Propagation via Bethe Free Energy," arXiv:1605.06451 — O(log N) BP
    fixed-point count.
18. "From synchronization to multistability in two coupled quadratic maps," arXiv:nlin/0005053.
19. "Transients vs. network interactions" (up to 84 coexisting attractors, N=10 coupled maps),
    arXiv:2411.14132.
20. Arnold tongue definition/summary (Grokipedia) + PubMed mode-locking in integrate-and-fire
    oscillators — confirms Arnold tongues are a saddle-node-of-periodic-orbits, rotation-number
    phenomenon, distinct from fixed-point-basin multiplicity.
21. Coupled-map-lattice stability, Eur. Phys. J. B (2005).
22. CP-ALS local convergence theory, arXiv:2505.14037 (2025).
23. Phase retrieval via alternating minimization, arXiv:1306.0160.

**Internal/substrate sources (on-disk, verified this drill):**
24. `experiments/exp_resonator_capacity_gpu_v1.py` (full script re-read; mechanism, initialization, and
    iteration structure derived directly from code for the z_init and combinatorial-count checks).
25. `data/exp_resonator_capacity_gpu_v1/metrics.json` (K2=1.0, K3=0.7, K4=0.1417, confirms only
    aggregate success rate is logged, not per-trial idxs — an instrumentation gap noted in (e)).
26. `notes/wave14b_noise_resonator_failure_research.md` (2026-05-19) — substrate's own prior,
    independent identification of the same paper family + validated ACF mechanism.
27. `notes/research_K_resonance_2026-05-23.md` — the `dynamics`/Arnold-tongue field's own closure
    record, cross-checked and confirmed distinct from this drill's phenomenon.
28. `notes/substrate_capability_map.md` row 51 ("Resonator decomposition with ACF rescue") — validated
    codebook-size-axis capacity extension.
29. `experiments/exp_wave14b_acf_resonator.py` (+ `_acf_K_dependent.py`, `_acf_K_dependent_extended.py`)
    — read to confirm ACF was only ever run at fixed F=2, never swept over factor count.
30. `notes/research_capability_self_margin_frontier_map_2026-07-06.md` — cross-referenced for the
    honesty-gate framing (why row 8b resists vs. why this mechanism does not, structurally).
31. `tools/orchestrator/research_field_advisor.py` run this cycle (context: confirms `dynamics` field
    closure and its scope).
32. Live off-disk numeric verification this cycle (`.venv/Scripts/python.exe`, numpy): z_init
    hand-derivation vs. 400-trial CPU check; M^K combinatorial count vs. observed failure-rate ratios.

**Total: 23 external literature sources (all fetched/verified via WebSearch/WebFetch by 3 independent
Sonnet sub-agents) + 9 internal on-disk sources + 1 live off-disk numeric verification = 32 verified
sources/checks. No new GPU/CPU trials of the resonator capability itself.**

## P_deflated (calibration penalty applied, two separate claims)

**Claim 1 (mechanism classification — convergence-basin proliferation, matching AGS/TAP/K-SAT annealed-
counting family, NOT order-statistic/product-law-chain):** raw confidence 0.80-0.85 (three independent
lit-scans converge; substrate's own independent 2026-05-19 history converges; own z_init and
combinatorial-count checks are directionally consistent). This is a novel synthesis (no single source
states this exact mapping for THIS problem) — per the mandatory novel-synthesis cap, **P_deflated =
0.50** (capped, not raw).

**Claim 2 (no ready-made or newly-derived closed-form self-margin exists yet for this mechanism — the
honest negative/ACCEPT-boundary-for-now finding):** raw confidence 0.85 (3 independent lit-scans
converge on "not in literature"; my own derivation attempt independently hit the same wall, i.e. 4
independent lines of evidence, not 1). Deflated per calibration discipline to **P_deflated = 0.65** —
residual uncertainty is whether a more determined multi-day derivation effort (fully expanding the
`2^(K-1)`-term crosstalk decomposition through the finite-iteration capture dynamics) could close the
gap; this residual does not change today's ACCEPT-boundary-for-now verdict, exactly as the prior note's
own residual-uncertainty caveat did not change ITS verdict.
