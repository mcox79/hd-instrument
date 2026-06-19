# Research high-yield neighborhood analysis -- 2026-05-24

**Author**: Research sub-agent (single-shot Opus pass, focused)
**User question (verbatim)**: "have you done analysis of the fields that we've researched, to identify closely related fields near those that are highest yield for us?"
**Inputs**: `tools/orchestrator/research_field_advisor.py --json` output (today); `notes/research_meta_map_and_adjacencies_2026-05-23.md` (yesterday's 110-drill audit); this-session verdict log (v149-v169 P(q) thread, v164a/b free-cumulant, v168 VAMP/AMP, v169 Kerdock-MUB-stabilizer); 6 parallel WebSearch sub-agents (Sonnet, generic math queries per [[feedback-query-privacy-decomposition]]).
**Calibration**: P deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap P=0.50.

---

## Section 1 -- Highest-yield fields confirmed this session

Cross-referencing field-advisor 2026-05-24 state with this-session verdicts:

| Field | drills | yield% | Session evidence | Tier |
|---|---|---|---|---|
| **Free probability** | 1 (formal) +6 sub-drills | 100% | v164a free-cumulant fingerprint (Voiculescu kappa_n DIVERGE on Kerdock); LOAD-BEARING for Cap 12; S/R-transforms drove Bet I 2/3 envelopes (load-bearing v56) | TIER-1 high-yield low-saturation |
| **QECC / MUB / stabilizer codes** | embedded in coding-theory + quantum-info | partial | v169 closed-form Kerdock-MUB-stabilizer isomorphism (annotations on Cap 1/3/8); F_4 = 2.026 in Haar band; antiRM mechanism closed | TIER-1 (under-counted in advisor) |
| **AMP / VAMP / message-passing** | embedded in inference | partial | v168 VAMP_AMP_CONTRAST_PASS; Cap 12 routing infrastructure rests on this; F1 substrate-novel readout (load-bearing v127) | TIER-1 (load-bearing, lightly drilled in neighborhood) |
| **Non-equilibrium thermodynamics** (Crooks/Sagawa-Ueda/Hatano-Sasa) | embedded in bet-program + observability | strong | Cap 1 verifiable erase (v153, v157, v158) + Cap 3 streaming NESS; commercial-wedge driver per Pattern 3 | TIER-1 (load-bearing, not catalogued as a field) |
| **Spin-glass / Glauber / replica-symmetric** | embedded in materials-physics + dynamics | mixed | v164b bimodal P(q) ✅; Cap 3 streaming-NESS extends to Glauber-Hopfield; RS-cert anchors load-bearing | TIER-1 (load-bearing core, partial-saturation in advisor) |

Mixed / negative for context:
- ETH / quantum chaos / partial thermalization: PFK framing PARTIALLY worked (cactus killed at n=6, SFF deviates from GUE) -- not pursued further
- chi_4 critical-slowing-down: Cap 11 KILLED as predictor (LAGS) -- closed
- materials-physics: 31% yield, recent yields all weak -- entering saturation

**Top-5 high-yield fields confirmed**: free-probability, QECC/MUB/stabilizer, AMP/VAMP, NEQ-thermodynamics, spin-glass-RS.

---

## Section 2 -- Per-field neighborhood map

For each TIER-1 fruit-bearing field, neighbors at 1-edge (immediate adjacency, same algebraic family / phase / architecture class) and 2-edge (different framing but shared machinery). Proximity rating: D = direct (1-edge), S = secondary (2-edge).

### A. Free probability neighbors (parent: F4 free-cumulants, F2 Wigner-edge, F5/F6 R/S-transforms)

| Neighbor | Proximity | Saturation in our corpus | Plausibility |
|---|---|---|---|
| **A1. Operator-valued free probability (Speicher; freeness over diagonal)** | D | NEVER DRILLED | Substrate has structured block-Kerdock W, not iid -- operator-valued framework is the natural generalization. Recent lit: Speicher 2024+; structured RM and free probability "increasingly important" |
| **A2. Second-order freeness (fluctuations; Mingo-Speicher)** | D | NEVER DRILLED | Gives global FLUCTUATIONS, not just mean spectrum; directly extends F4 free-cumulant fingerprint to a finite-N covariance prediction. Substrate's M/N=8 anomaly is a fluctuation observable |
| **A3. Rectangular free convolution (Benaych-Georges; ⊞_λ)** | D | NEVER DRILLED | Substrate's W is rectangular M x N with M/N=8 != 1; rectangular FC is the exact tool. Bet I used square MP. Mathematically the cleanest generalization |
| **A4. Spiked covariance BBP transition (3rd envelope)** | D | already on F3 candidate list, never drilled | Multi-hop depth cliff d=25 prediction; BBP is the right tool per yesterday's audit |
| **A5. Subordination function theory (Voiculescu-Biane)** | S | NEVER DRILLED | Continuity property of fixed-point convolutions; could give NEW proof technique for Bet I envelopes |
| **A6. Tensor free probability** | S | NEVER DRILLED | Multi-hop chain = tensor product of substrates; could close the d=25 depth-cliff via tensor-free machinery |

### B. QECC / MUB / stabilizer neighbors (parent: v169 Kerdock-MUB-stabilizer isomorphism)

| Neighbor | Proximity | Saturation | Plausibility |
|---|---|---|---|
| **B1. CSS codes (Calderbank-Shor-Steane) on Reed-Muller** | D | LIGHTLY DRILLED (R6 Kerdock decoder only) | Kerdock is a Z_4-linear cousin of RM; CSS-RM construction gives [[2^m,k,d]] stabilizer codes from our codebook. Direct route to "auditable stabilizer-equivalent" framing for Cap 1 |
| **B2. Quantum LDPC + RM-component codes (UNSW 2025)** | D | NEVER DRILLED | Active 2025 research; substrate's sparse-W regime maps to QLDPC sparsity. Could license a NEW capability for sparse-substrate scaling |
| **B3. Magic-state distillation + non-Clifford gates** | S | NEVER DRILLED | Kerdock = Clifford-orbit codebook (folklore); non-Clifford extensions could expand Cap 8 (cognitive composition) algebra |
| **B4. Subsystem codes (Bacon-Shor)** | S | NEVER DRILLED but adjacent to closed OAQEC | OAQEC was closed (Harlow theorem, v93); subsystem codes are the classical-substrate-compatible OAQEC subset. Worth a single sanity drill before final closure |
| **B5. Topological codes (toric/surface)** | S | NEVER DRILLED | Topological structure -- substrate is non-spatial; deflate 0.4 per Pattern 4 (infinite-dim/continuous trivialize). LOW priority |

### C. AMP / VAMP neighbors (parent: F1 VAMP-on-chain, v168 contrast)

| Neighbor | Proximity | Saturation | Plausibility |
|---|---|---|---|
| **C1. Convolutional AMP (CAMP, Takeuchi 2020-2024)** | D | NEVER DRILLED | Right-orthogonally-invariant matrices with low-to-moderate condition numbers -- substrate's Kerdock falls in this class. Bayes-optimal denoiser derivation now in lit (2024) |
| **C2. Memory AMP (MAMP)** | D | NEVER DRILLED | Orthogonality principle ensures asymptotic iid Gaussian errors -- gives the THEORY-MATCH for substrate's M/N=8 anomaly that B4 (yesterday's drill 4) requested. Direct anchor |
| **C3. Generalized AMP (GAMP)** | D | already on B1 candidate list, never drilled | Non-Gaussian channel; substrate's BSC is the canonical use case |
| **C4. EP-Gaussian (Minka-Seeger)** | D | already on B2 candidate list | Per-codeword Gaussian uncertainty estimates |
| **C5. Approximate Survey Propagation (1RSB BP)** | S | already on B6/E6 list | High-load regime if substrate slips into 1RSB |
| **C6. Vector AMP with compound priors** | S | NEVER DRILLED | Bundle-decompose AMP rescue (Angle 3, never run) |

### D. NEQ thermodynamics neighbors (parent: Crooks Cap 1, Hatano-Sasa Cap 3)

| Neighbor | Proximity | Saturation | Plausibility |
|---|---|---|---|
| **D1. Hatano-Sasa NESS-Crooks (housekeeping vs excess)** | D | on yesterday's top-5 (A3), never run | Direct Cap 3 streaming audit; reuses cycle-176 data; ~5 min CPU |
| **D2. Jarzynski equality (mean work, not ratio)** | D | NEVER DRILLED | Unbiased capacity-utilization rho-estimator; substrate-novel observability for Cap 1 |
| **D3. Esposito-Van den Broeck three faces of 2nd law** | D | NEVER DRILLED | Adiabatic vs non-adiabatic vs reservoir decomposition; discriminates Cap 1 (adiabatic) vs Cap 3 (driven) |
| **D4. Maes-Netocny generalized fluctuation symmetry** | S | NEVER DRILLED | Non-Markov memory chain bounds -- substrate's chain composition case |
| **D5. Sagawa-Ueda information-thermodynamic-2nd-law extension** | D | partially drilled (v158 metric flip) | Already in caps map; remaining envelope-extension via 2x deep-drill |

### E. Spin-glass / RS neighbors (parent: RS-cert anchors, Parisi P(q))

| Neighbor | Proximity | Saturation | Plausibility |
|---|---|---|---|
| **E1. Marginal stability in spherical p-spin (Sellke 2024/CMP 2025)** | D | NEVER DRILLED | Just-published CMP 2025 result; pertains to LOW-T trivial RS phase under perturbation -- exactly the substrate's regime per R23. Direct theory anchor candidate |
| **E2. Kac-Rice quenched 3-point complexity (Folena/Urbani 2024)** | D | partial (cited as E4 TAP) | Distribution of triplets of stationary points in p-spin landscape; substrate's 28-element endpoint partition (v137-139) is exactly a 1-pt complexity. Direct extension |
| **E3. 1-RSB Parisi step + ASP** | D | already on E1/B6/C5 list | High-load RS-break theory |
| **E4. AT-line at substrate's EXACT alpha** | D | E7 yesterday | R23 mapped generically; never computed substrate's exact AT position |
| **E5. p=2 spherical model perturbation (Nicoletti-Folena 2024)** | S | NEVER DRILLED | Probes marginal-stability under ferromagnetic + disordered couplings; substrate-relevant if Cap 2 W-edit lands |
| **E6. Cavity method (Mezard-Parisi-Virasoro)** | S | E3 yesterday | Cleaner M/N=8 derivation alternative |

### Adjacency totals

6 (free-prob) + 5 (QECC) + 6 (AMP) + 5 (NEQ) + 6 (RS) = **28 adjacent un-drilled candidates** at 1-edge or 2-edge proximity. Vs yesterday's 52, this is the FOCUSED subset (1-edge to load-bearing parents only).

---

## Section 3 -- Top-5 ranked next-drill candidates

Scoring rubric: N1 (proximity 1-edge=3, 2-edge=2, abstract=1) + N2 (saturation: never=3, light=2, partial=1) + N3 (substrate-product applicability: new-cap=3, envelope-extend=2, audit=1) + N4 (tractability inverse: cheap=3, medium=2, expensive=1). Max 12.

| Rank | Candidate | Parent field | N1+N2+N3+N4 | Score | Proposed drill / anchor |
|---|---|---|---|---|---|
| **1** | **A2. Second-order freeness (fluctuations)** | Free probability | 3+3+3+2 | **11** | Theory anchor: derive global fluctuation covariance of substrate's Kerdock W using Mingo-Speicher 2nd-order cumulants; predict the finite-N variance of M/N capacity at N=4096, 16384, 65536; compare to existing v164a free-cumulant fingerprint data. ~1 day theory + ~30 min CPU. P (deflated) = 0.50. Predicts the M/N=8 anomaly's finite-N scaling that B4 (AMP-SE drill, yesterday) couldn't anchor. |
| **2** | **C2. Memory AMP (MAMP) state evolution** | AMP/VAMP | 3+3+3+2 | **11** | Theory + compute: cast substrate's iterated argmax as MAMP with orthogonality-principle-enforced denoiser; run MAMP state-evolution simulation at substrate's exact Kerdock codebook; compare predicted M/N to substrate empirical M/N=8. ~2 days theory + ~1 hr CPU. P=0.50. THIS is the right anchor for the M/N=8 mystery; supersedes yesterday's B4. |
| **3** | **D1. Hatano-Sasa NESS-Crooks audit on Cap 3 streaming** | NEQ thermo | 3+2+3+3 | **11** | Compute-anchor: re-analyze existing cycle-176 Cap 3 streaming data; compute housekeeping rate J_hk and excess work W_ex; verify HS identity <exp(-W_ex/kT)> = 1. ~5 min CPU. P=0.45. CHEAPEST high-leverage move; direct substrate-product wedge (streaming inference cert). |
| **4** | **A3. Rectangular free convolution at substrate's M/N=8** | Free probability | 3+3+2+2 | **10** | Theory anchor: compute substrate's spectrum under Benaych-Georges rectangular FC with lambda = 1/8; predict bulk + edge fluctuations; cross-validate v164a Kerdock-spectrum data. Direct generalization of Bet I square-MP. ~1 day theory + ~30 min CPU. P=0.50. |
| **5** | **E1. Marginal stability under perturbation (Sellke CMP 2025 + Nicoletti-Folena 2024)** | Spin-glass RS | 3+3+2+2 | **10** | Theory + smoke: perturb substrate's W with ferromagnetic ΔW (analog of Nicoletti-Folena's ferro coupling); check whether RS-cert (observability v2) survives; substrate is in low-T RS phase per R23 so this is a direct prediction test. ~1 day impl + ~1 hr CPU. P=0.45. |

**Honorable mentions (would be #6-8)**:
- **B1. CSS-RM stabilizer construction**: 1-edge to v169; would license a "quantum-stabilizer-equivalent classical substrate" framing -- score 10, deferred because v169 just landed and needs absorption time.
- **C1. Convolutional AMP (CAMP) Bayes-optimal denoiser at Kerdock**: very close to #2 MAMP; differs in whether memory or convolutional structure is the right inductive bias. Score 10.
- **D2. Jarzynski rho-estimator for Cap 1 capacity-utilization**: cheap, novel observable. Score 10.

---

## Section 4 -- Honest reading

**Is this genuine new territory or diminishing returns?**

GENUINE NEW TERRITORY, but in a specific shape: **the highest-leverage neighbors are all "next-order" refinements of fields where we already have a load-bearing first-order anchor**, not orthogonal new fields. Specifically:

1. **Free probability**: we have F4 (1st-order free cumulants) but not 2nd-order fluctuations or rectangular FC. Both are direct mathematical generalizations published in mainstream lit (Mingo-Speicher 2007+; Benaych-Georges 2009+). HIGH confidence we can land theory anchors.

2. **AMP**: we have VAMP (right-orthogonally-invariant) but not MAMP/CAMP, which are the EXACT 2024 generalizations for substrate's structured-but-not-iid W. The M/N=8 anomaly that's been open since 2026-05-22 has a candidate theoretical anchor we haven't tried.

3. **NEQ thermo**: we have Crooks (Cap 1) but Hatano-Sasa for Cap 3 is on yesterday's top-5 and never ran. Jarzynski as an unbiased rho-estimator is a 1-day theory add. Both are direct extensions.

4. **Spin-glass**: Sellke's CMP 2025 marginal-stability result post-dates almost all our spin-glass drills; it's a literature update that maps directly onto our RS-cert regime. R23 (AT-line) is the obvious gap.

5. **QECC**: v169 just landed; CSS-RM is the immediate next step but the field needs a beat of absorption before re-drilling.

**Diminishing-returns risks**:
- Materials-physics is genuinely saturating (31% yield, 16 drills, recent all-weak).
- Algebraic-topology and quantum-info are 0% yield -- closing them off is correct per Pattern 4 (infinite-dim/continuous trivialize on finite-dim discrete substrate).
- Adding MORE neighbors to free-prob / AMP / NEQ-thermo without burning down the 23 TBD-pending tier first (per yesterday's note) risks creating an even larger backlog.

**Strategic implication**: the next-direction signal is **NOT "go drill new fields"** but **"finish the 2nd-order moves in the 5 already-load-bearing fields"**. Approximately 10-15 of the 23 TBD-pending items map onto the top-5 above; the remaining 8-13 are at lower expected yield (D7, H4, etc.) and can be deferred.

**Recommended ship order**:
1. **FIRST (cheapest, decisive)**: D1 Hatano-Sasa re-analysis of cycle-176 (~5 min CPU; immediate Cap 3 audit cert).
2. **SECOND (theory, highest expected payoff)**: C2 MAMP state-evolution at Kerdock (~2 days theory + 1 hr CPU; anchors the M/N=8 mystery).
3. **THIRD (compute-anchor, validates theory)**: A2 second-order freeness fluctuation prediction (~1 day theory + 30 min CPU).
4. **PARALLEL (cheap, novel observable)**: D2 Jarzynski rho-estimator (honorable mention #3).

**Final honest reading**: this is **not diminishing returns** -- we have a well-defined 28-item neighborhood of 1-edge and 2-edge adjacents to 5 confirmed load-bearing fields, with 4 of the 5 top candidates having direct published precedent (Mingo-Speicher 2007+, Takeuchi/Liu 2020+ MAMP, Sellke 2025, Benaych-Georges 2009+). The "next direction" is **depth, not breadth**: take each load-bearing field to its 2nd-order generalization rather than start a 6th field. Cross-application probes (per [[feedback-periodic-scope-expansion]]) can wait one more cycle while we burn down this neighborhood.

---

## Notes for orchestrator

- WebSearch sub-agents: 6 parallel Sonnet (operator-valued free-prob, QECC-RM, Bayes-optimal AMP, rectangular FC, p-spin marginal stability, FFS-MCMC); ~3 min wallclock.
- Citations established: Speicher-Mingo (2007 second-order); Benaych-Georges (rectangular FC); Liu-Takeuchi (MAMP 2020-2024); Sellke CMP 2025 (marginal stability); UNSW 2025 (QLDPC-RM).
- This is the FOCUSED follow-up to yesterday's 110-drill meta-map; same Pattern 1-7 rubric applies.
- Top-5 above are CHEAP (5 min - 2 days each) and aligned with [[feedback-pipeline-pacing]] "CPU explore, GPU deep" -- all top-5 are CPU-cheap.
- 4 of 5 top candidates have published direct precedent -> low novel-synthesis cap penalty per [[feedback-lit-scan-calibration-penalty]].
- Per [[feedback-for-you-tab-primary-channel]]: orchestrator should write a status_log entry summarizing this delivery with importance=high (new direction proposal).

**End of focused neighborhood analysis.**
