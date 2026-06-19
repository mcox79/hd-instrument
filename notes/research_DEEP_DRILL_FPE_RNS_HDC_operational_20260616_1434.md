# DEEP DRILL — FPE / RNS-HDC operational specifics at N>=4096

Filed: 2026-06-16 14:34
Follow-up to: Drill 2 Phase C TIER-3 architecture decision-prep
Model: opus synthesis over 4x sonnet lit-scan sub-agents

## HEADLINE

FPE on FHRR at N=4096 is operationally concrete and low-risk: canonical recipe = uniform-IID unit-modulus base phases (Hermitian-symmetric if real-IFT path is used) + sinc-kernel length-scale `B = 1/(2K)` derived by construction from Voelker 2020 + Kent/Frady resonator-readout at F=1 reduces to trivial nearest-neighbor over the {z^0..z^{K-1}} codebook (no iteration needed for the K<=20 cardinality use case). The load-bearing risk is NOT readout or length-scale (both have closed-form recipes), it is **bundle-crosstalk non-orthogonality** — FPE atoms at neighboring n have non-zero self-similarity by construction, violating the orthogonality assumption of the Frady-Kleyko-Sommer SNR model. P_deflated for "FPE TIER-3 integrates cleanly into existing 38-binder panel with zero regression" = **0.42** (novel-synthesis cap honored; failure-mode (iii) is load-bearing).

## Cheap decisive test

Single 1-day smoke (Day 2 of the per-day plan): implement uniform-IID Hermitian-symmetric base z, encode FPE(0..K=20) at N=4096, then check three things in order:
1. bind(role, z^k) then unbind(role) recovers z^k at cos>=0.98 — **takes ~10 min**
2. argmax over {z^0..z^{19}} cleanup recovers integer n with 0 errors over 200 trials, codebook M=2000 distractor — **~30 min**
3. bundle(z^{n_1}..z^{n_5}) for 5 random integers, kernel-aware cleanup recovers all 5 with cos>=0.93 — **~1-2 hr** (this is the load-bearing gate)

If (3) fails -> FPE TIER-3 ratify is REFUSED. The 38-binder panel run is contingent on (3) passing.

## Falsifiable predictions

### HARD-PASS (all must hold)
| Gate | Threshold | Source |
|---|---|---|
| bind/unbind round-trip on FPE atom | cos(unbind(bind(role,z^k),role), z^k) >= 0.98 at N=4096, k in [0..20] | Komer 2020 ch.4; Lu et al. 2019 |
| Cleanup over K=20 FPE codebook | 100% accuracy on 200 trials, no distractor | Plate 2003 trivial NN |
| Cleanup over K=20 FPE codebook + 2000 distractor | accuracy >= 0.95 | Schlegel/Neubert/Protzel 2020 fhrr curve |
| Bundle of 5 FPE atoms, kernel-aware decode | recover all 5 indices, cos >= 0.93 per recovered | Lu/Bremer 2024 CLE+MLE |
| Existing 38-binder panel regression | 0/38 operator regressions; cap_pres = 1.0 PRESERVED | substrate-internal panel |
| Existing 115+ signature panel | 0 signature regressions | substrate-internal panel |

### HARD-FAIL (any triggers refusal)
| Gate | Trigger | Mechanism |
|---|---|---|
| bind/unbind round-trip | cos < 0.90 | base z not unit-modulus or non-Hermitian for real-IFT path |
| Bundle-5 kernel-aware decode | any recovered cos < 0.85 OR any missed index | FPE neighbor non-orthogonality dominates crosstalk |
| 38-binder panel | any regression | FPE interferes with existing multiplicative-group operator semantics |
| Phase-wrap drift | k > 15 visible accuracy collapse | per Komer 2020 sec 4.4; means length-scale recipe is wrong for the K=20 range |
| Capacity budget consumed | M_max effective drops below 2000 after FPE atoms added | per Frady/Kleyko/Sommer 2018 SNR model — FPE atoms count against codebook budget |

## Concrete FPE recipe at N=4096, K<=20

### Base-phase z
- Sample θ_k ~ Uniform(-pi, pi] IID for k = 1..N/2-1
- Enforce Hermitian symmetry: θ_{N-k} = -θ_k, θ_0 = 0, θ_{N/2} = 0 (for even N=4096)
- z[k] = exp(i * θ_k)
- This is canonical Plate 2003 / Komer 2019 SSP construction; preserves real-IFT output if substrate uses real-projection at any boundary

### Length-scale (specified-by-construction, not learned)
Per Voelker 2020 (arXiv:2007.13462) sinc-kernel identity `E[<phi(x), phi(x+dx)>] = sinc(B*dx)`:
- For range [0,K] with K=20, choose B such that first sinc zero sits at dx = K (clean separation at the range boundary)
- => B = 1/K = 0.05
- Equivalently: scale uniform-IID phases by factor B before exponentiation
- Optional Lu/Furlong 2024 phase-bound refinement: phases drawn from `Uniform(-pi/(2*sqrt(d)*K), pi/(2*sqrt(d)*K))` with d = ambient dim of encoded variable (d=1 for scalar K). For scalar integer encoding d=1 collapses to the Voelker recipe.

### Readout (F=1 trivial case)
For K<=20 single-factor FPE-cleanup: **no resonator iteration needed**. Just argmax_n Re<s_hat, z^n>/N over n in {0..K-1}. Convergence: 1 step. No iteration.

### Readout (F>=2 case if FPE composes inside multi-factor product)
Frady-Kent synchronous update with cosine fixed-point criterion eps=1e-3, max_iters=100, typical convergence ~30 iters. At (N=4096, M=2000, F=2-3) Kent 2020 fit puts us deep inside the high-success basin.

## Per-person-day breakdown (refining Drill 2 "3-5 person-days")

**Day 1 — spec (4 hr core + 4 hr buffer):**
- Write `hdlab/encodings/fpe.py` with `fpe_base(N, generator)`, `fpe_encode(z, n) -> z^n` (FFT/IFFT in FHRR), `fpe_decode(s, z, K) -> int`
- Spec base-phase as Hermitian-symmetric uniform-IID
- Document length-scale recipe `B = 1/K`
- Write `verification/theory_fpe.py` with closed-form bind/unbind/cleanup expectations
- Acceptance: spec file + theory file + dtype annotations match CLAUDE.md conventions

**Day 2 — single-atom smoke (8 hr):**
- Implement; write `verification/test_fpe_smoke.py` covering bind/unbind round-trip + K-codebook nearest-neighbor + cos thresholds
- Run; iterate on phase-bound until cos >= 0.98 at K=20
- HARD-PASS gate (1) AND (2) above; if either fails, STOP — likely a phase-wrap or non-Hermitian bug

**Day 3 — bundle + role-filler integration (8 hr):**
- Add `verification/test_fpe_bundle.py` (Frady SNR-model expected values + actual measurements)
- Add `verification/test_fpe_role_filler.py` (bind(role, FPE(n)) round-trip)
- Implement Lu/Bremer 2024 kernel-aware cleanup (~50 LOC) if naive NN fails at bundle size 5
- HARD-PASS gate (3) — bundle of 5, kernel-aware decode. **This is the load-bearing day.**
- If kernel-aware decode still fails -> escalate; this is the (iii) failure mode

**Day 4 — 38-binder panel integration (8 hr):**
- Run substrate's existing 38-binder verification panel with FPE atoms registered
- Run 115+ signature panel
- Identify any regression; isolate to FPE-vs-binder interaction
- HARD-PASS gate (5) AND (6); if any regression, STOP — pre-ratify failure

**Day 5 — cap_pres verification + ratify (8 hr):**
- Run capability_preservation=1.0 invariant check
- Run axiom-term preservation panel
- Write FPE PROMOTION cell (substrate-internal); atomic commit
- Final ratify; cap_map row update

**Total: 5 person-days at the calibrated estimate.** Drill 2's "3-5" range survives: if Day 3 kernel-aware cleanup works first-try, days 4-5 collapse into one (3-day floor); if Day 3 needs the Lu/Bremer cleanup iteration, full 5 is needed.

## Top 3 implementation risks specific to substrate's 38-binder integration

### Risk 1 (HIGH): FPE neighbor non-orthogonality breaks Frady-Kleyko-Sommer bundle SNR
FPE atoms z^n and z^{n+1} have non-zero similarity by construction (sinc(B) > 0 for the chosen length-scale). The 38-binder panel's bundle/superposition operators assume approximate atom orthogonality. Mitigation: kernel-aware decode (Lu/Bremer 2024) + measure bundle crosstalk explicitly on Day 3. If crosstalk dominates -> FPE atoms must be marked as a separate atom-class with their own bundle semantics, not folded into the generic bundle operator. **This is the load-bearing failure mode.**

### Risk 2 (MED): Hermitian symmetry interaction with existing complex-FHRR vs real-IFT boundary
Substrate has 115+ signatures; some may project to real values at certain operator boundaries (e.g., similarity, cleanup). If the base z is not Hermitian-symmetric and any operator does real-projection, FPE atoms break that operator. Mitigation: enforce Hermitian symmetry by construction in `fpe_base`; add a verification test that all 38 binders accept Hermitian-symmetric input without modification. P_failure ~ 0.25 if substrate is fully complex-FHRR end-to-end; ~0.55 if any real-projection boundary exists.

### Risk 3 (MED): Capacity-budget collision — FPE atoms count against M_max
Frady/Kleyko/Sommer 2018 + Kleyko et al. 2022 give M_max ~ N/(2 log M); at N=4096 this is ~5k-10k. Substrate currently has ~26k atoms; M_max is the **codebook size for cleanup**, not the atom count, so substrate is already operating in a sparse-keying / selectivity regime per the 28th finding (id-namespace mismatch). Adding K=20 FPE entries to the cleanup codebook is trivially within budget, **but**: if FPE atoms are bound into composites and then need to be unbound + cleaned-up against the full corpus, M_max gates retrieval accuracy. Mitigation: keep FPE codebook scoped to the cleanup context where K is small (per-context cleanup), do not register FPE atoms in the global retrieval codebook. P_failure ~ 0.20 with this scoping.

## Cross-thread synthesis

| Prior finding | Connection to FPE drill |
|---|---|
| Drill 1 smoke-gate K<=20 cardinality | matches FPE single-factor F=1 trivial-NN regime exactly |
| Drill 2 ordering (residue/FPE -> mod-Hopfield -> GHRR) | FPE is lowest-risk first step; this drill confirms the operational specifics |
| Drill 2 "3-5 person-days" | refined to 3-day floor / 5-day ceiling with Day 3 as load-bearing gate |
| Drill 3 thesis: specified-by-construction not learned | satisfied by Voelker 2020 sinc-kernel length-scale recipe — closed-form, no learning |
| 28th finding sparse-keying load-bearing selectivity | scoping FPE codebook to per-context cleanup preserves this; do NOT register FPE in global retrieval codebook |
| Tier 1 architectural claim 7 cap_pres=1.0 substrate refuses capability loss | enforced by Day 5 ratify gate; FPE TIER-3 REFUSED if any regression |
| 20th rule 3-distillation-modes | FPE addition is STRUCTURE-ADDING (introduces new atom class), not ATOM-REMOVING; must pass REFUSAL gate via 38-binder panel |
| Lakatos-PROGRESSIVE programme claim 9 | FPE adds new empirical content (continuous-variable encoding); progressive shift if Day 3 + Day 4 hard-pass |

## Substrate-product implications

1. **Continuous-variable atom class becomes substrate-internal capability.** Today substrate handles discrete atoms; FPE adds encoded scalars (and via Komer SSP, d-dimensional vectors). This is a substrate-product capability extension, not a model swap.
2. **Closed-form / specified-by-construction.** No learning step. Composes with Tier 1 architectural claim "substrate is sound by construction." LLM categorical gap: LLMs require learned continuous-value embeddings; substrate gets them from `B = 1/K` by formula.
3. **Per-context codebook scoping** (per Risk 3) is itself a substrate-product feature, not a workaround — it operationalizes the sparse-keying selectivity finding (28th) into the FPE design.
4. **Bundle-of-FPE crosstalk = first measured "kernel atom class"** — bundle SNR formula changes for FPE atoms relative to discrete atoms. This is a substrate-internal characterization that gives the audit ledger a new entry: distinct atom classes have distinct bundle semantics.
5. **Refusal capability proven again if Day 3 fails** — substrate would refuse FPE ratify rather than degrade existing operators. cap_pres=1.0 hard-gate would fire.

## Citations (verified count: 10)

1. Frady, Kent, Olshausen, Sommer (2020) "Resonator Networks 1" arXiv:2007.03748
2. Kent, Frady, Olshausen, Sommer (2020) "Resonator Networks 2: Factorization Performance and Capacity Compared to Optimization-Based Methods" Neural Computation 32(12):2332-2388
3. Voelker (2020) "A short letter on the dot product between rotated Fourier transforms" arXiv:2007.13462
4. Komer, Stewart, Voelker, Eliasmith (2019) "A neural representation of continuous space using fractional binding" CogSci 2019
5. Komer (2020) PhD thesis, University of Waterloo (FPE / SSP full development)
6. Schlegel, Neubert, Protzel (2020) "A comparison of vector symbolic architectures" arXiv:2001.11797, Artificial Intelligence Review
7. Frady, Kleyko, Sommer (2018) "A theory of sequence indexing and working memory in recurrent neural networks" arXiv:1803.00412, Neural Computation 30(6)
8. Lu / Bremer / Furlong / Orchard / Eliasmith (2024) "Improved Cleanup and Decoding of Fractional Power Encodings" arXiv:2412.00488
9. Hersche et al. (2023) "In-memory factorization of holographic perceptual representations" arXiv:2211.05052, Nature Nanotechnology
10. Kleyko, Davies, Frady, Kanerva, Kent, Olshausen, Rabaey, Rachkovskij, Rahimi, Sommer (2022) "Vector symbolic architectures as a computing framework for emerging hardware" Proceedings of the IEEE

Bonus references (cited but not primary load-bearing):
- Furlong & Eliasmith (2022) "Fractional Binding in Vector Symbolic Architectures as Quasi-Probability" CogSci 2022
- Dumont & Eliasmith (2020) "Accurate representation for spatial cognition using grid cells" CogSci 2020
- Frady, Kleyko, Kymn, Olshausen, Sommer (2021) "Computing on functions using randomized vector representations" arXiv:2109.03429
- Renner, Sandamirskaya et al. (2024) "Neuromorphic visual scene understanding with resonator networks" arXiv:2208.12880, Nature Machine Intelligence
- Plate (2003) "Holographic Reduced Representation: Distributed Representation for Cognitive Structures" CSLI Publications

## Calibration

- Mature literature (Plate / Komer / Frady-Kent / Kleyko surveys exist); P-of-existence for individual recipes is high (0.85)
- Deflation 0.20 applied; novel-synthesis cap 0.50 honored
- Novel-synthesis claim: "FPE integrates into substrate's existing 38-binder panel with zero regression" P_deflated = 0.42 — under the 0.50 cap; load-bearing risk is bundle-crosstalk non-orthogonality (Risk 1)
- All HARD-FAIL thresholds explicit; refusal path is Day 3 kernel-aware decode failure
