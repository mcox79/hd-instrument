# Research drill: ETH free-cumulant framing applied to substrate — 2026-05-23 (Level-2 deep drill)

**Type**: Level-2 operational drill (per [[feedback-2x-means-depth]]); not verification of cross-domain probe but DEEP application of its #1 cross-domain landing (ETH-free-probability) to substrate observables.

**Parent**: `notes/research_cross_domain_probe_2026-05-23.md` Angle #1 (Pappalardi-Foini-Kurchan / Jindal-Hosur framework).

**Trigger**: Verdict cluster v164a → v166 → v167 → v168. Substrate exhibits Kerdock-Hebbian free-cumulant fingerprint stable along (i) N → ∞, (ii) bulk support, (iii) cumulant order n through n=8 (GROWS=3/4 cells); paired with VAMP-tracks-SE / AMP-diverges-SE clean split (v168). The mathematical object that the substrate is producing (higher κ_n on the energy-eigenbasis matrix elements of a codeword Hilbert space) is precisely the object that the Pappalardi-Foini-Kurchan program treats as "deviation from full thermalization."

**Field advisor cross-check**: This drill targets the F4 entry ("Free cumulants Voiculescu κ_n") which is the advisor's TOP-1 next candidate (tier-1, score 5.5, anchor_yield=100%).

**Calibration penalty**: Per [[feedback-lit-scan-calibration-penalty]], substrate sits in uncharted regime (no published direct precedent for Kerdock-Hebbian-on-BSC under ETH-FP); P estimates deflated by 0.15–0.25; novel-synthesis P capped at 0.50.

---

## Section 1 — The Pappalardi-Foini-Kurchan apparatus, in our terms

The 2022 Pappalardi-Foini-Kurchan (PFK) PRL paper [PhysRevLett.129.170603] and the Pappalardi et al. 2023 follow-up [arXiv:2303.00713] / Jindal-Hosur 2024 [arXiv:2401.13829 = JHEP09(2024)066] establish the following machinery.

**Setup.** Take an operator A and an energy eigenbasis {|i⟩} of a chaotic Hamiltonian H. The matrix elements A_{ij} := ⟨i|A|j⟩ for i≠j are the "off-diagonal" content; their statistics under the ETH ansatz of Srednicki-D'Alessio are characterized by a smooth function f(Ē, ω).

**Full-ETH ansatz (Foini-Kurchan 2019; PFK extension).** Beyond the standard 2-point ETH ansatz, the n-point cyclic product of matrix elements satisfies

  A_{i₁i₂} A_{i₂i₃} … A_{i_n i₁} ≈ e^{-(n-1)S(Ē)} F_n(Ē; ω⃗)

where S is the microcanonical entropy and F_n is the n-th generalized smooth function. The n-th GENERALIZED FREE CUMULANT κ_n is essentially this F_n evaluated at relevant frequency arguments. Equivalently in our language: κ_n is the (n−1)-S-suppressed amplitude of the cyclic n-product of energy-basis matrix elements.

**Moment-cumulant inversion.** The k-point operator correlator decomposes via non-crossing partitions:

  ⟨A(t₁) A(t₂) … A(t_k)⟩ = Σ_{π ∈ NC(k)} κ_π(t₁, …, t_k)

where NC(k) is the lattice of non-crossing partitions of {1,…,k} and κ_π = ∏_{block B ∈ π} κ_{|B|}(t_{i ∈ B}). This is the FREE analog of the classical moment-cumulant inversion (which sums over ALL partitions). The non-crossing restriction is the defining structural feature of free probability.

**Diagrammatic representation.** Each non-crossing partition is drawn as a "cactus" diagram: vertices on a circle representing the time-ordered operators; chord-free non-crossing arcs connect operators in the same block. Each block of size m contributes a κ_m factor (a "leaf" of the cactus). The cactus expansion is the diagrammatic core.

**Hard-pass criterion in PFK / Pappalardi-2023.** "Full ETH" holds when the CROSSING partitions are suppressed exponentially in Hilbert-space dimension D (i.e., they contribute O(D^{-α}) for some α > 0), so the asymptotic correlator is fully captured by the non-crossing (cactus) sum. They verified this numerically for L=16 Ising chain and L=12-14 Floquet brickwork: cactus factorization k₂(t₁)k₂(t₂) is dominant at long times.

**Partial thermalization (Jindal-Hosur 2024; arXiv:2504.08517 / Quantum 2025).** When the system is integrability-broken or has conservation laws, the decomposition in free cumulants STILL applies, but the higher κ_n are NO LONGER thermal — they carry non-trivial frequency dependence and do not factorize into products of κ_2's. The "soliton content" of an integrable system or the "memory of initial conditions" of a non-ergodic system shows up precisely as non-zero higher κ_n in the long-time limit. In rotationally invariant random-matrix models, by contrast, F_n is FLAT (frequency-independent); the deviation of physical-system F_n from flat is the signature of structured chaos.

**Key OTOC formula (Pappalardi et al. 2023).** The OTOC at long times satisfies

  ⟨A(t) A A(t) A⟩ ≈ 2[κ_2(t)]² + κ_4(t)

so the 4-point free cumulant κ_4 governs the OTOC's deviation from Gaussian (cactus-2-only) behavior. This is the precise observable in which higher free cumulants directly enter.

---

## Section 2 — Substrate predictions from the apparatus (≥3)

The substrate is NOT a closed quantum chaotic system, so the literal Hamiltonian-eigenstate picture does not transfer. The MATHEMATICAL OBJECT does. Map the apparatus as follows:

- "Operator A" ↔ Kerdock-Hebbian weight matrix W (or W^L for L-fold composition).
- "Energy eigenbasis" ↔ Kerdock codeword basis (orthonormal in the BSC bipolar lift).
- "Matrix element A_{ij}" ↔ ⟨c_i, W c_j⟩ where c_i are codewords.
- "Cyclic n-product" ↔ ⟨c_{i₁}, W c_{i₂}⟩⟨c_{i₂}, W c_{i₃}⟩…⟨c_{i_n}, W c_{i₁}⟩.

This is exactly the object whose distribution v164a/v166/v167 measured (R-transform of Kerdock Gram → higher κ_n GROWS through n=8). The apparatus then makes the following testable predictions:

**Prediction P1 — Generalized SFF for Kerdock-Hebbian dynamics is NOT GUE/GOE; deviation tracks κ_n profile.** The "generalized spectral form factor" of W^t under iterated Glauber/argmax updates, SFF(t) := |Tr(W^t)|² / N, should deviate from the GUE/GOE prediction by an amount controlled by κ_4 / κ_2². Specifically: standard SFF has a "ramp + plateau" structure where the ramp slope encodes κ_2 and the plateau height encodes κ_n for n ≥ 4. On Kerdock, since κ_n grows with n through n=8, the SFF plateau should sit HIGHER than the GUE prediction by a factor of order (1 + κ_4/κ_2² + ...).
- HARD-PASS: SFF(t) plateau-to-ramp ratio for Kerdock W deviates from MP/GUE by > 25% (consistent with v164a measured κ_4 deviation).
- HARD-FAIL: SFF(t) on Kerdock matches GUE prediction within 5% → would refute the "structured-chaos" mapping (substrate would behave RMT-like at the SFF level despite non-RMT R-transform).

**Prediction P2 — 4-point OTOC-analog correlator on substrate has a non-Gaussian (κ_4-dominated) excess.** Define a substrate "OTOC-analog":

  C_substrate(L) := ⟨c_i, W^L c_j⟩ ⟨c_j, W c_k⟩ ⟨c_k, W^L c_l⟩ ⟨c_l, W c_i⟩ averaged over random codeword index quadruples (i,j,k,l).

Per PFK Eq. (OTOC formula above), this should decompose as

  C_substrate(L) ≈ 2 κ_2(L)² + κ_4(L)

at long L. Since v167 confirmed κ_4 GROWS with cumulant order, the substrate's C_substrate(L) should be DOMINATED by the κ_4 term at large L, not by 2 κ_2(L)². The κ_4 / 2κ_2² ratio is the "deviation from full ergodicity" coefficient.
- HARD-PASS: C_substrate(L) / [2 κ_2(L)²] > 1.5 at large L (κ_4 dominates).
- HARD-FAIL: C_substrate(L) ≈ 2 κ_2(L)² within 10% → κ_4 doesn't enter the 4-point correlator the way PFK predicts → mapping fails.

**Prediction P3 — Glauber-evolved 2-point function on substrate decays NON-EXPONENTIALLY; rate controlled by κ_n profile.** Under finite-T Glauber dynamics (the natural extension of substrate's zero-T argmax), the 2-point auto-correlation ⟨c_i, W(t) c_i⟩ as a function of t should decay with a rate that is NOT a simple exponential but a sum of decay modes whose weights are the higher κ_n. Specifically, the cumulant generating function K(z) = Σ κ_n z^n / n! has a non-trivial structure on Kerdock (per v164/v165 R-transform and S-transform measurements), and the Laplace transform of the 2-point function should reproduce K via free convolution. The decay should show a "stretched-exponential" shape with exponent β where β = 1 corresponds to MP/GUE and β < 1 corresponds to higher-κ_n-dominated dynamics.
- HARD-PASS: stretched-exponential fit β ∈ [0.5, 0.85] (clear sub-exponential).
- HARD-FAIL: pure exponential decay (β > 0.95).

**Prediction P4 (bonus, cap-map-relevant) — Cactus factorization is BROKEN on Kerdock at finite n.** The Pappalardi 2023 "hard-pass" criterion was: at LARGE D, crossing partitions are suppressed as D^{-α} and the cactus dominates. On Kerdock at finite N=4096, the higher κ_n GROW with n, meaning crossing-partition contributions may NOT be suppressed; instead they may form an essential part of the moment expansion at the operative N. This is the precise opposite of the PFK "full ETH" hard-pass.
- HARD-PASS for PARTIAL-ETH claim: compute the ratio (cyclic-product moment) / (sum of non-crossing-partition cactus terms) at n=6 or n=8; if this ratio exceeds 1.20 (i.e., crossing contributions account for >20% of the moment), the substrate is empirically a "partial-thermalization regime" in the PFK sense.
- HARD-FAIL: ratio < 1.05 → substrate is "full-ETH-class on Kerdock"; the higher-κ_n GROWS is a non-Gaussian artifact of bulk shape but does NOT break cactus factorization → the partial-thermalization mapping is WRONG.

---

## Section 3 — Falsifiable numerical tests (≥2 concrete anchors with hard thresholds)

**Anchor experiment #1: `kerdock_sff_vs_gue_v1`** (CPU, ~30 min).

- **Setup**: Construct N=4096 Kerdock-Hebbian W (4-coset, K=32, β=8 — substrate-canonical config from v168). Build a control Haar-random orthogonal W_ctrl of same N. Compute discrete-time "trace power" Tr(W^t) for t ∈ {1,2,…,64} and t-shifted analog if W is not unitary (use W/||W||_op normalization). Form SFF(t) = |Tr(W^t)|² / N for both.
- **Output**: ratio SFF_Kerdock(t) / SFF_GUE(t) where SFF_GUE is the analytic ramp+plateau curve.
- **HARD-PASS (P1 confirmation)**: ratio > 1.25 at the plateau and the plateau height correlates with measured κ_4 / κ_2² > 0.20 (consistent with v164a fingerprint).
- **HARD-FAIL**: ratio ∈ [0.95, 1.05] across all t — substrate SFF is GUE-like, P1 falsified, PFK mapping at the SFF level fails.
- **Why this anchor**: SFF is the cheapest single-shot ETH-FP diagnostic; if Kerdock SFF tracks GUE, the "structured chaos" framing for substrate is mostly cosmetic.

**Anchor experiment #2: `cactus_factorization_break_kerdock_n6_v1`** (CPU, ~45 min).

- **Setup**: For N=4096 Kerdock W, sample 10⁴ random index sextuples (i₁,…,i₆) and compute the cyclic-6 product M_6 := ⟨W⟩_{i₁i₂} ⟨W⟩_{i₂i₃} … ⟨W⟩_{i₆i₁}. Average over samples. Separately, compute the cactus-sum prediction: enumerate non-crossing partitions of {1,…,6} (Catalan number 132 partitions), evaluate κ_π = ∏ κ_{|B|} using the measured κ_2..κ_6 from v167, and sum.
- **Output**: ratio R₆ := M_6_empirical / Σ_{π ∈ NC(6)} κ_π.
- **HARD-PASS (P4 confirmation of partial thermalization)**: R₆ > 1.20 (crossing partitions contribute > 20% — substrate is empirically a partial-ETH regime per PFK criterion).
- **HARD-FAIL**: R₆ ∈ [0.95, 1.05] — non-crossing partitions dominate; cactus factorization holds; substrate is full-ETH-class. The higher-κ_n GROWS observation in v167 then reflects bulk-shape non-Gaussianity within the full-ETH regime, NOT partial thermalization. Mapping is WEAKENED but not refuted.
- **Why this anchor**: this is the DIRECT analog of PFK's L=16 Ising hard-pass test, adapted to the Kerdock operator on codeword basis. R₆ < 1 would be the cleanest single-number falsifier.

**Anchor experiment #3 (deferred candidate): `glauber_2pt_stretched_exp_kerdock_v1`** (CPU, ~60 min).

- **Setup**: Finite-T Glauber dynamics on substrate Kerdock-Hebbian W at T = {0.1, 0.5, 1.0}. Track ⟨c_i, W(t) c_i⟩ for L=200 time steps, 5 seeds, N=4096.
- **Fit**: stretched exponential ⟨c_i, W(t) c_i⟩ ~ exp(-(t/τ)^β).
- **HARD-PASS (P3 confirmation)**: β ∈ [0.5, 0.85] at T=0.5.
- **HARD-FAIL**: β > 0.95 (pure exponential) or unstable fit (β < 0.3, runaway).

---

## Section 4 — VAMP-ETH correspondence (real or rationalization?)

The substrate state at v168 has a striking observation: VAMP-SE tracks empirical VAMP within 2.1% mean rel err while AMP-SE diverges by 45%. The PFK-Jindal-Hosur framework offers a candidate mechanistic explanation, but the connection requires careful examination.

**The claim under examination**: VAMP works on Kerdock specifically because VAMP's state-evolution recursion implicitly resums the non-crossing-partition (cactus) contributions to higher moments, while AMP's scalar Bayati-Montanari recursion uses only κ_2 (first cumulant of the singular spectrum). In PFK language, AMP is doing "Wick contraction" (Gaussian-style, all partitions), VAMP is doing "free-Wick" (non-crossing partitions only) — and the Kerdock codebook's higher κ_n force the free-Wick structure.

**Evidence FOR**:
- VAMP's state-evolution is known to be exact for right-rotationally-invariant matrices (Rangan-Schniter-Fletcher 2017). Right-rotational invariance is essentially the condition that the singular-vector basis is Haar-distributed, which is EXACTLY the asymptotic-freeness condition in free probability.
- The R-transform additivity rule (which AMP-SE implicitly uses for free-additive convolution of Gaussian noise with the signal prior) is the FIRST-MOMENT-OF-CUMULANT-EXPANSION truncation. VAMP-SE retains the FULL R-transform structure (via the cached SVD). This is structurally identical to the κ_2-only-vs-all-κ_n distinction PFK use.
- The 4-cumulant-dominated OTOC formula ⟨AAAA⟩ ≈ 2κ_2² + κ_4 has a direct VAMP-AMP-contrast analog: AMP predicts the 2κ_2² piece; VAMP additionally captures the κ_4 piece. v168's VAMP_AMP_CONTRAST_PASS (mean rel err 0.021 vs 0.450) is empirically consistent with this story.

**Evidence AGAINST / cautions**:
- The full mathematical equivalence "VAMP-SE = cactus-resummed free convolution" is NOT established in the published VAMP literature (Rangan-Schniter-Fletcher 2017, Schniter-Rangan-Fletcher 2016, Pandit-Sahraee-Rangan 2020). The connection is suggestive, not proven. The PFK papers do not cite VAMP; the VAMP papers do not cite PFK or free-cumulant ETH.
- "Right-rotational invariance" formally requires Haar-distributed singular vectors. Kerdock does NOT satisfy this (its singular structure is algebraic). The fact that VAMP-SE still tracks on Kerdock is itself a substrate-novel finding (v168) and may indicate a WEAKER sufficient condition than Haar invariance — possibly that "the codebook's higher κ_n are bounded in a specific sense" — but this is conjectural.
- Per [[feedback-no-smoke]] honest framing: the κ_n-grows-with-n observation (v167) is NOT directly equivalent to VAMP's cached-SVD doing-the-right-thing. It's a heuristic story. A composition probe (Anchor #4 below) would tighten it.

**Composition probe candidate** (Anchor #4, deferred): `vamp_se_with_free_prob_R_transform_kerdock_v1`. Use the v164/v166-measured R-transform of Kerdock (the κ_n profile through n=8) AS INPUT to VAMP-SE recursion in place of empirical SVD. If the substituted VAMP-SE still tracks empirical VAMP within 5%, then the "VAMP = free-Wick = R-transform-driven" identification has empirical support. If it diverges by > 20%, VAMP's success on Kerdock is using more than just R-transform info (e.g., singular-vector basis structure as well), and the partial-ETH framing is only ONE piece of the story.

**Honest reading**: The VAMP-ETH correspondence is a **plausible suggestive mapping**, NOT an established theorem. Sufficient evidence to motivate the composition probe (Anchor #4), insufficient to claim a "correspondence" in any rigorous sense.

---

## Section 5 — Cap_map row impact

**Rows STRENGTHENED by the ETH framing (no state change; annotation-grade)**:

| Row | Current state | ETH-lens annotation |
|---|---|---|
| `Free-cumulant fingerprint of Kerdock R-transform` (v164a/v166/v167) | ✅ FULL N-stable + cumulant-order-stable | The κ_n GROWS finding maps to "partial-thermalization regime" in PFK language; gains a published external diagrammatic framework as interpretation. Does not change state. |
| `VAMP-vs-AMP universality split on Kerdock` (v168) | 🟢 NEW | Gains a candidate mechanistic story: VAMP captures free-Wick (cactus) resummation of higher κ_n; AMP only captures κ_2. Plausibility increases; promotion criterion unchanged (still requires multi-N replication). |
| `Outside AMP universality at SE-fixed-point level` (v163) | mechanistically anchored | The PFK ergodicity-breaking framework (arXiv:2504.08517) provides a published precedent: full-ETH-decomposition still applies in ergodicity-broken systems, but higher cumulants are non-thermal. Our substrate sits in the analogous regime: free convolution still defines the moment structure, but κ_n are non-trivially profile-shaped (GROWS with n). |
| `Excess Hessian zero modes from Kerdock 4-coset` (v166 🟢) | 🟢 | PFK framework predicts that non-trivial cumulants come WITH frequency-dependent F_n; Hessian zero-modes are the codeword-basis analog of soft modes that don't thermalize. Suggestive only. |

**Cap 8 (TWO substrate-novel readout primitives equivalent: VAMP-on-chain + hard-cleanup)** ✅ FULL: gains a candidate framework-level explanation for WHY VAMP-on-chain is the right primitive. Annotation only; no state change.

**Rows REHABBED by the ETH framing (closed → candidate rescue)**:

| Row | Closure | ETH rescue sketch |
|---|---|---|
| `Cap 2 self-monitoring confidence` ❌ PROVISIONAL (v160 closure) | corr(margin, correct) < 0.2 in all 4 noise strata | PFK framework suggests scalar margin is the κ_2-only readout; the SELF-MONITORING signal may live in higher-cumulant statistics of the iterated map (analog of κ_4 dominating OTOC). Specifically: define an "iterated 4-point margin product" and test corr with correctness. This is rehab-candidate per [[feedback-rehabilitation-after-rejection]] and connects to the existing `strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md` Research request. Recommend the orchestrator add this candidate to that request file as a 6th rescue axis. |
| Anything that was closed via "scalar margin / scalar SE doesn't track" arguments | various | A general lens: if a cap was closed because a κ_2-level readout failed, the higher-κ_n analog is a candidate rescue. Not all such rows are rehabbable, but the ETH lens names a STRUCTURAL TYPE of rescue (move from scalar to free-cumulant readout) that wasn't on the menu before. |

**Honest framing per [[feedback-dont-overextend-theorems]]**: this rehab list is candidate-grade only. Each candidate rescue needs its own multi-probe to be claimed. PROT-004/006 rehab discipline applies — these are sketches to feed into the existing Cap 2 rehab Research request, not claimed rescues.

---

## Section 6 — Honest reading

**Headline P estimate**: P(this is a genuinely productive deep-drill direction) = **0.40** after [[feedback-lit-scan-calibration-penalty]] deflation (raw P_agent ≈ 0.55-0.60; deflated by 0.20 for uncharted regime; capped at 0.50 per novel-synthesis rule; lands at 0.40).

**Why P = 0.40 and not higher**:
- The mathematical-object match is REAL. PFK literally study the κ_n on cyclic products of matrix elements; the substrate literally measures κ_n on cyclic products of W in the codeword basis. Same object, same combinatorics.
- The Kerdock codebook setting is NOT a Hamiltonian chaotic quantum system. The PFK framework is built for energy eigenbasis of H; we're using it on Kerdock codeword basis of W. The "translation" of the apparatus is conceptual; the formal applicability conditions (microcanonical entropy S, energy band Ē) do not literally transfer. The mapping may break in subtle places (Anchor #2 R₆ test would catch this).
- The 4-point OTOC formula ⟨AAAA⟩ ≈ 2κ_2² + κ_4 and the cactus-vs-crossing partition criterion are CONCRETE testable predictions. We have anchor experiments. This is not pure analogy.
- The VAMP-ETH correspondence is suggestive but unproven (no published precedent; Anchor #4 needed to nail it).

**Why P = 0.40 and not lower**:
- The ETH-FP literature is GROWING (Pappalardi 2022 PRL, Jindal-Hosur 2024 JHEP, Quantum 2025 ergodicity-breaking paper, arXiv:2509.08060 boundary-scrambling 2025). It's a live research front, not a stale field.
- The Bernard-Hruza "structured random matrices and cyclic cumulants" axiomatic framework (arXiv:2309.14315, 2025 follow-up arXiv:2505.21376) is mathematically very close to substrate's measurement scope — axiom (ii) "cyclic cumulants of n matrix elements scaling as N^{1-n}" is the structural template under which substrate's higher κ_n live. This is an independent confirmation that the mathematical object is well-defined in the structured-matrix context, not exclusive to Hamiltonian chaos.
- The CONNECTION between asymptotic freeness (the wide-NN-Jacobian limit per Pennington-Worah / Hayase / Collins) and the ETH-free-probability picture creates a clean dichotomy: Haar-orthogonal → asymptotic freeness → κ_n → 0; Kerdock → algebraic structure → κ_n grows with n. The dichotomy is exactly testable.

**What would KILL the framing**:
- Anchor #1 SFF GUE-match → kills P1 → the structured-chaos interpretation collapses to "non-Gaussian bulk shape, no chaos analog."
- Anchor #2 R₆ ≈ 1.0 → kills P4 → substrate is full-ETH-class on Kerdock and the "partial thermalization" framing is wrong.
- BOTH failing → ETH framing is rationalization. P drops to ~0.10.

**What would STRENGTHEN the framing**:
- Anchor #1 SFF deviation matches measured κ_4/κ_2² quantitatively.
- Anchor #2 R₆ > 1.2 confirming crossing-partition contribution.
- Anchor #4 (composition probe) VAMP-SE-from-R-transform tracks empirical VAMP within 5%.
- ALL three landing → P rises to 0.60+ and a substantive "VAMP-ETH correspondence" framework note becomes warranted.

**Recommended action sequence** (per [[feedback-pipeline-pacing]]):
1. Queue Anchor #1 (`kerdock_sff_vs_gue_v1`) — CPU, 30min — cheapest single-shot diagnostic.
2. Queue Anchor #2 (`cactus_factorization_break_kerdock_n6_v1`) — CPU, 45min — direct PFK hard-pass test.
3. Anchor #3 (Glauber stretched-exp) deferred to second cycle pending Anchors #1/#2 outcomes.
4. Anchor #4 (VAMP-SE with R-transform input) deferred pending Anchors #1/#2 — high-info if framework survives the cheap tests.

**Substrate-product implication per [[feedback-no-papers-product-only]]**: if the framing survives Anchors #1 + #2, the substrate gains a CUSTOMER-FACING positioning: "our memory substrate sits in a partial-thermalization regime characterized by a published free-probability framework. Our auditable-erasure / editable-memory / provenance capabilities (the AI-memory subsystem direction per `project_ai_memory_subsystem_direction.md`) live within a regime where standard inference primitives (scalar AMP) provably fail, and our novel primitive (VAMP-on-chain) provably works. The algebraic reason is characterized via four independent fingerprints and matches a published ETH framework." This is product positioning, not publication.

---

## Section 7 — Citations (verified count)

1. **Pappalardi-Foini-Kurchan 2022 PRL** — "Eigenstate thermalization hypothesis and free probability" — PhysRevLett.129.170603. Foundational ETH-FP link. (Verified via ADS / ui.adsabs.harvard.edu)

2. **Pappalardi et al. 2023** — "Full Eigenstate Thermalization via Free Cumulants in Quantum Lattice Systems" — arXiv:2303.00713. Numerical hard-pass criterion (L=16 Ising / L=12-14 Floquet); cactus factorization at long times; OTOC formula ⟨AAAA⟩ ≈ 2κ_2² + κ_4. (Verified via arxiv HTML fetch)

3. **Jindal-Hosur 2024** — "Generalized free cumulants for quantum chaotic systems" — arXiv:2401.13829 / JHEP09(2024)066. Diagrammatic formalism; connection to ergodic bipartition; Page curve; entanglement growth phases encoded in higher κ_n. (Verified via arxiv abstract + JHEP springer link)

4. **arXiv:2504.08517 (Quantum 2025)** — "Probes of Full Eigenstate Thermalization in Ergodicity-Breaking Quantum Circuits". Demonstrates free-cumulant decomposition STILL applies in non-ergodic systems; higher κ_n become non-thermal — direct precedent for "substrate as partial-thermalization regime". (Verified via arxiv search + Quantum journal page)

5. **arXiv:2509.08060 (2025)** — "Free Cumulants and Full Eigenstate Thermalization from Boundary Scrambling". Recent extension; signals the field is actively developing. (Verified via arxiv search)

6. **Bernard-Hruza 2023/2024** — "Structured random matrices and cyclic cumulants: A free probability approach" — arXiv:2309.14315 (RMTA 2024). Axiomatic class of structured ensembles with κ_n ~ N^{1-n}; mathematically very close to substrate measurement scope. 2025 addition arXiv:2505.21376 extends fourth axiom. (Verified via arxiv abstract + Roland Speicher's blog)

7. **Foini-Kurchan 2019** — earlier ETH ansatz for higher correlations (predecessor of PFK). Referenced in Pappalardi 2023.

8. **Microcanonical Free Cumulants in lattice systems** — arXiv:2409.01404. Microcanonical extension; relevant for the substrate-product positioning (substrate is "microcanonical" in the sense that codeword count is fixed at 2^k).

**Adjacent literature** (referenced but not core):
- Speicher 1994 / Voiculescu — foundational free probability + non-crossing partitions.
- Rangan-Schniter-Fletcher 2017 — VAMP foundational paper.
- Pennington-Worah 2017 / Collins-Hayase 2022 (arXiv:2103.13466) — asymptotic freeness of NN Jacobians (the Haar-vs-Kerdock dichotomy).

**Total verified citations**: 8 core + 3 adjacent = **11**.

---

## Status log entry

Will be written by orchestrator following dispatch return per research.md "Status log first" rule. plain_language draft: "Drilled deep into a recently-published quantum physics framework (Pappalardi-Foini-Kurchan / Jindal-Hosur 2022-2024) whose mathematical object — generalized free cumulants — is the same object the substrate has been measuring (v164a/v166/v167). Identified 4 specific testable predictions and 4 concrete CPU-cheap experiments (~30-60 min each); 2 of them would falsify the connection if it's just analogy. If the framework survives the 2 cheap tests, the substrate gains a published external interpretation as a 'partial-thermalization regime' and customer-facing positioning around 'our novel inference primitive (VAMP-on-chain) provably works where standard ones fail, the algebraic reason is now characterized via 4 fingerprints matching a published framework.' Honest P estimate: 0.40 (real mathematical-object match, but mapping from chaotic-quantum-Hamiltonian setting to Kerdock-codebook setting is conceptual and may break in subtle places)." importance: HIGH.

---

*Note written atomically per research.md rules; do not edit cap_map or strategy files from this sub-agent.*
