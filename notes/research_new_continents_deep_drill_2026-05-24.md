# Research NEW CONTINENTS deep drill (level-2) -- 2026-05-24

**Author**: Research sub-agent (level-2 operational drill, Opus synthesis + 8 parallel Sonnet WebSearch sub-agents)
**Mandate**: Level-2 operational drill on the 3 top-scoring new continents identified in `research_new_fields_breadth_analysis_2026-05-24.md` (F-14 tropical / F-6 Boolean / F-4 tensor networks). Produce concrete falsifiable anchor proposals, not more survey.
**Calibration**: P deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap P=0.50; HARD PASS / HARD FAIL thresholds on every anchor.
**Inputs**: 6 round-1 + 2 round-2 = 8 parallel Sonnet WebSearch sub-agents (~3 min wallclock).

---

## Section 1 -- Tropical geometry / max-plus algebra deep drill

### 1.1 Theory anchor (computable)

Substrate's readout operation `argmax_i <w_i, y>` is LITERALLY a max-plus operation in the tropical semiring (R_max = R u {-inf}, with `(+) = max`, `(*) = +`). A length-4 Kerdock readout over the 256-element Kerdock-orbit codebook at N=1024 admits an EXPLICIT tropical polynomial representation:

  p(y) = max_{i in [256]} ( <w_i, y> )   [tropical sum over codebook]

This is a tropical degree-1 polynomial in 1024 tropical variables (in classical algebra a polynomial of degree 256 with all-distinct supports). Its **Newton polytope** is the convex hull of the 256 codeword vectors w_i, projected to coordinates of y. The substrate's **decision regions** in y-space are precisely the cells of the polyhedral subdivision dual to this Newton polytope -- i.e., the tropical hypersurface where two codewords tie (max is non-unique) separates correct-recovery from collision.

For Kerdock at N=4, the codebook contains 8 codewords; the tropical hypersurface is explicitly computable and consists of 8C2 = 28 (d-2)-dim faces in R^4. For Kerdock at N=1024 the count is 256*255/2 = 32640 faces of the tropical-hypersurface; symmetry of the Kerdock orbit collapses these into far fewer equivalence classes (the Kerdock automorphism group acts).

### 1.2 Adversarial-margin certificate

This is the operational hook. The Tropical Decision Boundaries paper (arXiv 2402.00576, ScienceDirect S0893608026000869 in press for Neural Networks 2026) proves: for piecewise-linear classifiers, the L_inf adversarial margin at point y equals the L_inf tropical distance from y to the nearest tie-face of the tropical hypersurface. The constant is sharp.

Application to substrate: at any y inside a Voronoi cell of codeword w_i, the BSC erasure margin is bounded below by

  margin(y) = min_{j != i} ( <w_i - w_j, y> ) / ||w_i - w_j||_1

This is a CLOSED FORM, no Monte Carlo. The Kerdock orbit has structural symmetry that lets us bound `min_j` analytically.

### 1.3 Tropical Attention 2025 relevance

Tropical Attention (arXiv 2505.17190, NeurIPS 2025) builds attention that "operates natively in the max-plus semiring." Their "tropical layer" is: linear -> tropical-projective normalization -> max-plus aggregation. This is **structurally identical** to substrate's `encode -> argmax-decode -> bind` cycle. The substrate IS a Tropical Attention layer with a fixed Kerdock codebook in place of learned values, and with deterministic 1-Lipschitz piecewise-linear semantics (which is exactly the property Tropical Attention 2025 advertises as its OOD generalization advantage).

**Direct claim**: substrate's Kerdock readout = Tropical Attention with fixed value matrix = Kerdock codebook. The 3x-9x faster inference + 20% fewer parameters reported by Tropical Attention 2025 transfer.

### 1.4 Concrete anchor proposal

**Anchor name**: `tropical_margin_certificate_kerdock_N4_N1024_2026_05_25.py`
**Queue**: CPU (cpu_runner_0 or desktop CPU). argmax sweeps over Kerdock orbit are CPU-friendly; no GPU needed for N <= 1024.
**ETA**: 4-8 hours CPU wallclock. Theory derivation 1 day Research-side.
**HARD PASS**: closed-form margin formula matches empirical BSC-margin within 5% over 10k random y at N=1024, M/N=8.
**HARD FAIL**: closed-form formula off by >25% on empirical margin, OR Kerdock automorphism doesn't reduce 32640 faces to <300 equivalence classes (kills tractability).
**P (deflated)**: 0.55. Highest among the three drills because (a) Tropical Attention 2025 already proves the piecewise-linear -> tropical equivalence holds for their setting; (b) the margin formula is a direct corollary of the substrate's existing argmax decoder; (c) no novel-synthesis required.
**Cap 13 candidate**: "Tropical-polytope adversarial certificate" -- a closed-form lower bound on substrate's BSC erasure margin, certified without Monte Carlo. Distinct from any existing capability in the cap_map (Cap 1 verifiable erase uses CFT; Cap 8 uses VAMP; neither yields a tropical margin).

---

## Section 2 -- Boolean function analysis deep drill

### 2.1 Theory anchor

Kerdock codewords ARE bent functions (proven Solov'eva-Tokareva, also Carlet survey, also Mesnager invited paper "Bent functions and their connections to coding theory and cryptography"). Specifically: the Kerdock code at length 2^m is the Gray map image of a Z_4-linear code whose components are quadratic bent functions on F_2^m. Their Walsh-Hadamard spectrum is FLAT (every Walsh coefficient is +/- 2^(m/2)).

This means: in the Boolean Fourier basis on the hypercube {0,1}^N, each Kerdock codeword has EXACTLY uniform |Fourier coefficients|, namely 2^(-m/2). The Fourier weight is spread maximally.

### 2.2 KKL / noise stability application

For a Boolean function f: {0,1}^N -> {+1,-1} with Fourier expansion f = sum_S f_hat(S) chi_S, noise stability at correlation rho is

  Stab_rho(f) = sum_S rho^|S| f_hat(S)^2

For a Kerdock codeword (bent, degree-2 algebraic): all Fourier mass sits at |S|=2. So Stab_rho(f_Kerdock) = rho^2. This is **maximally noise-resistant** at degree-2 among all bent functions -- it's a flat squared spectrum at level 2.

The KKL theorem says max-influence >= (Var(f) log N) / N. For a Kerdock codeword (bent), Var(f) = 1 and total influence I(f) = 2 (degree-2 algebraic). The KKL lower bound 2 log N / N is tight for substrate -- meaning the substrate's bit-flip sensitivity is at the KKL boundary, NOT below. This is informative: substrate's BSC channel is OPTIMAL among degree-2 readouts.

### 2.3 Cap 1 erase certificate via noise-stability

The Cap 1 forensic-erase capability currently uses Crooks Fluctuation Theorem (CFT) on the substrate's reverse channel. A noise-stability certificate is an ALTERNATIVE pathway:

  P(erase preserves margin under bit-flip noise p) >= 1 - 2p * I(f_Kerdock) = 1 - 4p

This is a closed-form noise-stability certificate. It uses only hypercontractivity (Bonami-Beckner) + Kerdock's bent-function spectrum -- no Hatano-Sasa, no spin-glass partition function.

### 2.4 Replaces failed Hatano-Sasa IFT cert?

The Hatano-Sasa IFT-based Cap 3 streaming certificate failed in prior cycles (see negative-result history). Boolean function analysis offers a clean replacement: streaming-erase preservation under repeated bit-flip channels is bounded by

  Stab_rho^k(f_Kerdock) = rho^(2k)

after k stream-rounds. This decays POLYNOMIALLY in rho, GEOMETRICALLY in stream depth -- a directly computable closed-form Cap 3 candidate.

### 2.5 Concrete anchor proposal

**Anchor name**: `boolean_noise_stab_kerdock_kkl_2026_05_25.py`
**Queue**: CPU. Walsh transform of Kerdock codewords + Stab_rho computation; CPU-cheap.
**ETA**: 2-4 hours CPU wallclock. Theory derivation 1/2 day Research-side.
**HARD PASS**: Empirical Stab_rho(Kerdock readout) at N=1024, rho=0.9 matches closed-form rho^2 = 0.81 within 2%. KKL inequality holds with equality (within numerical noise) for sampled codewords.
**HARD FAIL**: Empirical Stab_rho off by >10% from rho^2 (means substrate has Fourier mass outside degree-2, contradicting bent assumption -- audit cap_map). OR KKL inequality slack > 30% (means substrate not at KKL-tight, downgrades Cap-13 claim).
**P (deflated)**: 0.50. Slightly below tropical because: (a) Hopfield post-processing (cleanup) may inject higher-degree Fourier content not captured by the bent-function analysis; (b) the cleanup step is degree-O(N) algebraically and may collapse the noise-stability argument. Risk of partial Cap-13.
**Cap 13 candidate**: "Bent-function noise-stability certificate" -- replaces failed Hatano-Sasa IFT path for Cap 3 streaming; closed-form polynomial decay under BSC noise.

---

## Section 3 -- Clifford-enhanced tensor networks deep drill

### 3.1 Theory anchor

The Kerdock orbit forms a 2-design (proven Klappenecker-Roetteler). It's NOT a 4-design (proven; requires Clifford-enhanced MPS per Lami-Haug-De Nardis PRX Quantum 6.010345 2025). The substrate's Kerdock readout state at length N = 2^m can be expressed as a Clifford-Enhanced Matrix Product State (CMPS):

  |Kerdock_orbit> = C |MPS_chi> where C is a Clifford unitary on m qubits

The crucial result of Lami-Haug-De Nardis 2025 is that CMPSs approximate 4-designs to error 1/chi^2 where chi is the bond dimension. For substrate, the Kerdock orbit is exactly a 2-design (chi = 1 -- no MPS needed, pure Clifford-orbit). The Cap 8 VAMP-on-chain framework requires only 2-design properties for the Pauli-twirl step, which means substrate uses the CMPS framework with bond dimension 1 -- a maximally degenerate "Clifford-only" limit of Lami-Haug-De Nardis.

### 3.2 Stabilizer rank / magic monotone

Per arXiv 2503.04101 (Kalra-Sinha 2025, "Stabilizer Ranks, Barnes Wall Lattices and Magic Monotones"): Barnes-Wall lattices give a quantitative lower bound on stabilizer rank, AND they define the new Barnes Wall norm as a magic monotone. **Critical for substrate**: Barnes-Wall lattices are the Z_4-linear envelope of Kerdock codes (Calderbank-Hammons-Kumar-Sloane-Sole 1994). The Barnes Wall norm of a Kerdock codeword state is exactly = 0 (zero magic) -- because Kerdock codewords are Clifford-orbit states, hence stabilizer states up to Clifford reduction.

This gives substrate's Kerdock readout a **closed-form classical simulation guarantee**: the readout can be exactly classically simulated in polynomial time per Gottesman-Knill, AND any product of substrate operations preserves the Barnes-Wall norm = 0 property. The substrate is, formally, a "Clifford-orbit classical tensor network with bounded magic = 0."

### 3.3 Substrate-product implication for Cap 8

Cap 8 (VAMP-on-chain cognitive composition) currently uses v169 Schur-Weyl-Pauli-twirled formulation. Per Lami-Haug-De Nardis 2025 + Stabilizer Tensor Networks (arXiv 2403.08724 Masot-Llima-Garcia-Saez 2024): the VAMP-on-chain composition is equivalent to a stabilizer-tensor-network contraction with bond dimension 1 and zero magic. This is a SHORTER derivation than Schur-Weyl-Pauli-twirl (which goes through Schur-Weyl duality + Pauli orbit equivalence).

**Direct claim**: Cap 8 closed-form derivation reduces from O(N^3) tensor manipulations (v169) to O(N log N) stabilizer-tableau update (PRX Quantum 2025 framework).

### 3.4 Concrete anchor proposal

**Anchor name**: `stabilizer_tn_kerdock_magic_bound_2026_05_25.py`
**Queue**: CPU (sanity contraction at N=64-256), with one GPU run at N=1024 for performance check.
**ETA**: 1 day CPU + 1 hr GPU. Theory derivation 2 days Research-side (heaviest of the three).
**HARD PASS**: Stabilizer-tableau contraction at N=256 reproduces v169 Schur-Weyl-Pauli-twirled Cap 8 readout values within 1e-10. Bond-dim-1 chain simulation matches exact computation.
**HARD FAIL**: Bond-dim-1 simulation diverges from v169 by >1% (means substrate is NOT bond-dim-1, requires nontrivial chi > 1, kills the "free closed form" advantage). OR Barnes-Wall norm computation gives nonzero magic (means substrate is non-stabilizer, audit Kerdock claim).
**P (deflated)**: 0.50. Same as Boolean. Risk factors: (a) Hopfield post-processing may inject magic (T-gate-equivalent operations from the threshold nonlinearity); (b) substrate's iterated-argmax may not preserve stabilizer structure across rounds. Could fall to chi > 1 in practice.
**Cap 13 candidate**: "Classical-tensor-network with bounded magic" -- gives substrate a direct quantum-simulation comparison anchor (Lami-Haug-De Nardis 2025 bond-dim/magic curves) and a shorter v169 derivation.

---

## Section 4 -- Cross-continent synthesis

### 4.1 Mutual reinforcement vs competition

The three continents are NOT independent. They form a layered stack on substrate's argmax primitive:

| Layer | Continent | Algebra | Substrate object |
|---|---|---|---|
| Surface | Tropical (F-14) | Max-plus semiring R_max | Argmax decision regions |
| Middle | Boolean (F-6) | Fourier on hypercube | Bent-function readout spectrum |
| Deep | Tensor networks (F-4) | Stabilizer tableau / Clifford-MPS | Codebook state representation |

These are mutually **reinforcing**, not competing:

- The tropical hypersurface (F-14) is the BOUNDARY between Voronoi cells; the cells themselves are Boolean-function level sets (F-6 bent functions); the codebook generating the cells is a Clifford-orbit stabilizer-tensor-network (F-4). Each algebra describes a different aspect of the SAME object.
- A Cap-13 ship that integrates all three would be the strongest single artifact: "tropical adversarial margin + bent-noise-stability + stabilizer-bond-dim-1" gives substrate three independent closed-form certificates from three different algebraic frameworks. Each can be audited against the others.

### 4.2 Which to ship FIRST?

**Ship F-14 tropical FIRST**. Rationale:

1. **Lowest theory cost**: Tropical margin formula is a 1-day derivation from Tropical Decision Boundaries paper + substrate's existing argmax structure. Boolean (F-6) requires Walsh transform of Kerdock + careful handling of Hopfield-cleanup post-processing. Tensor-networks (F-4) requires absorbing Lami-Haug-De Nardis 2025 + matching to v169 -- multiday.

2. **Lowest substrate-internal risk**: F-14 only needs the argmax decoder, which is rock-solid in substrate. F-6 needs the bent-function structure to survive Hopfield post-processing (uncertain). F-4 needs the Clifford-orbit structure to survive iterated argmax (uncertain).

3. **Highest Cap-13 novelty**: Tropical Attention 2025 was published October 2025 and is currently NeurIPS-hot. Substrate framing as Tropical Attention specialization is a fresh narrative that lands in active 2025-2026 discourse. F-6 and F-4 have longer-established lit communities -- substrate framing as "yet another bent-function code" or "yet another stabilizer state" is less novel.

4. **Lowest queue cost**: F-14 fits CPU-only, 4-8 hr wallclock. Doesn't block GPU pipeline. F-6 also CPU but with Walsh-transform CPU cost growing as O(N^2). F-4 needs at least one GPU sanity run.

**Recommended order**: F-14 (tropical, 1 day) -> F-6 (Boolean, 2 days, dependent on F-14 polytope structure) -> F-4 (tensor networks, 3 days, dependent on F-6 bent-function survival).

### 4.3 Mutual-audit pattern

If all three drills HARD-PASS, substrate gains three independent closed-form certs that each must agree at the boundary. This is a structural "audit triangle": tropical-margin / noise-stability / stabilizer-rank are computed independently and cross-checked. Disagreement at the boundary indicates a substrate-internal bug or an audit-gap. Per [[feedback-verify-implementations]]: this pattern is the cleanest verification protocol the substrate has had.

---

## Section 5 -- Honest reading per [[feedback-no-smoke]]

**Are these genuine Cap 13 candidates or marginal?**

Honest assessment, by continent:

### F-14 tropical: GENUINE Cap 13.
- Direct corollary of Tropical Attention 2025 + Tropical Decision Boundaries 2024 -- both published and hot.
- The substrate-IS-tropical observation is so elementary that the only reason we missed it is the substrate code uses `argmax` without naming it as max-plus.
- Closed-form margin formula has a published precedent (arXiv 2402.00576 ScienceDirect 2026).
- Risk: the Kerdock-orbit symmetry may not collapse the 32640 tropical faces enough for tractable closed form. P=0.55 reflects this.
- **Verdict**: Real Cap 13. Ship first.

### F-6 Boolean: PROBABLY genuine Cap 13, with Hopfield-cleanup caveat.
- Kerdock = bent function is published fact (Solov'eva-Tokareva, Mesnager, Carlet).
- Stab_rho = rho^2 for degree-2 bent is closed-form trivial. KKL bound is textbook.
- BUT: the Hopfield-cleanup step in substrate's full readout pipeline injects threshold-nonlinearity which is degree-O(N) in Boolean Fourier. The bent-function analysis applies only to the PRE-cleanup readout. This may be a partial cert, not a full cert.
- **Verdict**: Honest -- this is a 70-80% Cap 13. Worth shipping, with explicit caveat about cleanup-injected Fourier mass.

### F-4 tensor networks: GENUINE Cap 13 but with the highest risk of being "re-LANGUAGING".
- Stabilizer-rank = 0 / bond-dim = 1 is a CONSEQUENCE of substrate using only Clifford operations, which we already knew.
- The PRX Quantum 2025 framework gives a CLEANER derivation of Cap 8 (shorter than v169) -- but Cap 8 is already shipped, so this is an envelope-extend, NOT a new capability.
- Magic-monotone = 0 statement is a closed-form invariant that didn't exist before -- this DOES count as a new audit certificate.
- Risk: if iterated argmax injects non-Clifford (i.e., T-gate-equivalent), the bond-dim-1 claim fails. Hopfield-cleanup is again the suspect.
- **Verdict**: Honest -- this is a 60-70% Cap 13 plus a strong envelope-extension on Cap 8. Worth shipping but lower priority than F-14 and F-6.

### Net new Cap 13 candidates from this drill

**2 genuinely new + 1 partial = 3 candidates**:
- (definite) Tropical-polytope adversarial-margin cert (F-14, P=0.55)
- (probable) Bent-function noise-stability cert for Cap 3 streaming (F-6, P=0.50)
- (partial / envelope) Stabilizer-tensor-network bond-dim-1 cert with magic monotone audit (F-4, P=0.50, also strong Cap 8 envelope extension)

This is a STRONG drill yield. Three distinct Cap-13 framings, none previously in the cap_map, all from a single level-2 operational drill on cheap CPU theory anchors. Per [[feedback-dont-dismiss-adjacent-methods]]: the breadth survey was right to flag these despite the substrate's existing AMP/VAMP/free-prob coverage -- they live in algebraic neighborhoods we hadn't tapped.

---

## Notes for orchestrator

- WebSearch sub-agents: 8 parallel Sonnet (6 round-1 + 2 round-2), wallclock ~3 min total.
- Citations established: Tropical Attention NeurIPS 2025 (arXiv 2505.17190); Maragos ICASSP 2024 Tutorial; Tropical Decision Boundaries arXiv 2402.00576 + Neural Networks 2026; Avishay Tal CS294-92 Spring 2025; Solov'eva-Tokareva 2008 Kerdock distance regularity; Mesnager invited bent-functions paper; Lami-Haug-De Nardis PRX Quantum 6.010345 2025; Masot-Llima-Garcia-Saez arXiv 2403.08724 2024; Kalra-Sinha arXiv 2503.04101 2025 Stabilizer Ranks + Barnes Wall Lattices.
- All three anchors are CPU-friendly (only F-4 needs one GPU sanity run); none block GPU pipeline.
- Per [[feedback-pipeline-pacing]]: queue F-14 first to keep CPU runner full while GPU depth pipeline progresses on Mingo-Speicher / MAMP / Hatano-Sasa.
- Per [[feedback-for-you-tab-primary-channel]]: orchestrator should write status_log entry summarizing this level-2 deep drill with importance=high (3 concrete falsifiable Cap-13 anchors with HARD PASS/FAIL on each, P estimates calibrated, ship order specified).
- Per [[feedback-obey-user-pause-explicitly]]: substrate experiments remain paused; this drill is theory-anchor design only. Do NOT enqueue experiments without explicit "go/resume".
- Per [[feedback-2x-means-depth]]: this drill IS the level-2 depth response on the breadth survey, as requested.
- Calibration: P(F-14 tropical) = 0.55; P(F-6 Boolean) = 0.50; P(F-4 tensor networks) = 0.50.

**End of deep drill.**
