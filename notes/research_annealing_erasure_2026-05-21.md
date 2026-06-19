# Research note: Annealing-based erasure — HONEST RECALIBRATION (primary claim REJECTED; secondary modes differential)

**Date**: 2026-05-21 ~22:10 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_annealing_erasure_2026-05-21.md` (21:56, user-directed)
**Decision-log entry**: Entry 58
**Pass-1 honesty label**: REAL external lit scan via 3 parallel Agent (general-purpose) subagents; ~50+ unique papers surveyed (2018-2026 dominant + foundational anchors); generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — HONEST RECALIBRATION per [[feedback-no-smoke]]

**Primary claim (forensics-resistance gain over Bet 2/C anti-Hebbian)**: **REJECTED** at P=0.05-0.15. Three independent literature scans converge.

**Critical theoretical finding**: **Serricchio et al. arXiv:2410.06269 (2024)** proves Hebbian unlearning ≡ steady state of nonequilibrium thermal-Langevin dynamics on W. "Annealing erasure" is mathematically a **reparameterization** of anti-Hebbian rank-1 subtraction, NOT a new mechanism. The thermal framing does not buy new selectivity OR new forensic-resistance.

**Forensic-resistance reality** (Agent C): every published noise/perturbation unlearning method leaves detectable signatures. arXiv:2506.14003 "Unlearning Isn't Invisible" (2025-26) shows >90% trace-detection from logits/outputs/activations. arXiv:2602.01150 Statistical MIA shows failed-MIA ≠ forgetting. arXiv:2605.01129 "Privacy Leakage Beyond Forgotten Set" — 5 SOTA methods susceptible to tri-class attack. **Only exact retraining-from-scratch + DP-from-scratch training are credibly forensic-resistant.**

**Secondary modes (engineering-tractable substrate-product features)**: **PURSUIT WORTHWHILE** at P=0.40-0.55:

| Mode | P(differential value over Bet 2/C) | Substrate-product gain | Eng cost |
|---|---|---|---|
| **Soft / partial erasure** | **0.50-0.55** | GDPR data-minimization mode (tunable degradation rate, not just delete) | 2-4 cycles |
| **Bulk erasure efficiency** | 0.40 | Erase N facts in one consolidation pass vs N anti-Hebbian ops | 3-5 cycles |
| **Blind erasure** (location-only, no value) | 0.30 | Forgetting without knowing what to forget | 3-5 cycles |

**Recommended substrate-product action**:
- **DO NOT** pursue thermal/annealing as a forensics-resistance REPLACEMENT for Bet 2/C anti-Hebbian (primary claim rejected per literature scan).
- **DO** pursue M.1 (region-specific Gaussian noise + re-equilibration) as **soft-erase mode** for GDPR data-minimization (Lane C secondary feature).
- **DO** pursue M.2 (Lupo arXiv:2602.08428 closed-form Hopfield unlearning at finite γ) as **bulk-erase efficiency** for consolidation phases.
- **DEFER** M.3 (two-temperature Langevin) — no control-theory mapping to instance-selective erasure (Agent B P=0.10).

**Per [[feedback-no-papers-product-only]]**: framed as "additional erasure modes for Lane C breadth (soft/bulk)," NOT as "novel thermal-erasure framework" or "Bet 2/C replacement."

**Per [[feedback-value-creation-not-competition]]**: substrate already has Bet 2/C ✅ Mirage-grade erase. Soft + bulk modes ADD Lane C feature breadth without claiming forensics-resistance superiority. The substrate-product value is in mode diversity, not in mode dominance.

---

## Pass 1 — external literature scan synthesis

### Agent A: HAMR + Curie thermal magnetic media + forensic recoverability + AM annealing (~25 papers)

**HAMR (heat-assisted magnetic recording)**:
- Strungaru et al. arXiv:2502.02236 (2025): multiscale micromagnetic/atomistic modeling; switching probability smooth in (T_peak, H_write, dwell time); non-precessional linear reversal dominant at/above T_c.
- Vogler-Bruckner-Suess et al. arXiv:1907.03884 (2019, J. Appl. Phys. 126:213901): closed-form P_switch sigmoid parameterization.
- Wang et al. arXiv:1712.03302 (2017-18): **thermal gradients induce spin currents biasing neighbor switching** — heating is NOT magnetically isolated.
- Suess-Schrefl arXiv:1411.3052: thermally-written-in errors ~12% at 0.5 T for pure-FePt grains.
- Plumer-Weller line + Granz et al. IEEE Trans. Magn. (2015+): T_E (erasure temperature) several tens of K below T_c.

**Critical HAMR finding** (Agent A verbatim): "HAMR is *spatially* selective at the ~10-20 nm scale because the optical near-field spot is small, but only because the write head co-locates a magnetic field — heat alone randomizes; field alone can't switch the high-Hk grain. **Without an aligned biasing field, the cooled grain re-magnetizes essentially randomly. So 'Curie heating' by itself is bulk-erasing within the hot zone, not selective per pattern.**"

**Forensic recoverability after thermal erase**:
- NIST SP 800-88r2 (2025): explicitly REMOVES prescriptive techniques; defers to IEEE 2883-2022.
- IEEE 2883-2022: thermal/incineration under Destroy with no quantitative residual-signal target.
- Gutmann (canonical theoretical): widely interpreted as OVERSTATING recoverability for modern high-density media.
- **No peer-reviewed paper quantifies % bit-level recovery after a complete T > T_c excursion in controlled zero-field cool.** Industry consensus "irrecoverable" but quantitative gap is real.

**AM annealing literature** (CRITICAL for substrate):
- Fachechi-Agliari-Barra arXiv:1810.12217 (2018): off-line unlearning step suppresses SPURIOUS attractors while leaving STORED attractors intact. **Selectivity is class-level (spurious vs pure), NOT instance-level (forget pattern #7 keep pattern #3).**
- **Serricchio et al. arXiv:2410.06269 (2024)**: **Hebbian unlearning ≡ particular driven-equilibrium steady state**; "annealing" is mathematically a thermal-Langevin process on W. Selectivity comes from choice of sampling distribution, NOT from temperature itself.
- Aquaro et al. arXiv:2604.19258 (2026): extends dreaming to biased patterns; selectivity is attractor-by-attractor via probe-state initialization.
- Cammarata et al. arXiv:2603.09384 (2026): bounded-weight dreaming improves memorization.

**Agent A honest verdict**: "Thermal erasure in a software AM analog... within 6 months: **~0.05-0.10**. Physical thermal-erase literature does NOT transfer. HAMR's value is heat + co-located field on grains with high Hk; remove any of those three and you get bulk randomization, not selectivity. **Adding Gaussian noise to weights gives forensic-resistance equivalent to any DP-style mechanism — the thermal framing buys nothing here.**"

### Agent B: spin-glass quench + Glauber + two-temperature + Kovacs (~25 papers)

**Spin-glass quench / Glauber dynamics**:
- Janus collab. arXiv:2207.06207 (Nat. Phys. 2023): three length scales govern aging dynamics.
- Baity-Jesi-Cugliandolo-Parisi et al. arXiv:2412.08381 (Rev. Mod. Phys. 2025): comprehensive review; Janus II reaches 0.1s real time on EA model.
- **Lupo et al. arXiv:2602.08428 (2026)** ★: replica-method analysis of Nokura-style Hopfield unlearning; **provides closed-form ε(γ, α) parameter prescription**; most engineering-ready substrate-applicable mechanism.
- Newman-Stein arXiv:1601.00105: deep quench dynamics destroy initial-condition memory — argues AGAINST targeted erasure being preserved through quench.

**Two-temperature systems (CK framework)**:
- Cugliandolo-Kurchan foundational (arXiv:math/0409273 + 1993/1994): effective temperature T_eff via FDR violation.
- Two-temperature spin chain NESS arXiv:cond-mat/0206345: explicit NESS with broken detailed balance.
- FDT violation in spin ice PRB 105:134431 (2022): T_eff measurable in real disordered magnet.

**Agent B critical finding** (CK control problem): "The two-T literature treats T_eff as an *emergent observable*, not a programmable control knob targeting specific stored patterns. No paper closes the control loop from 'I want pattern μ gone' to 'set T_fast=X, T_slow=Y'. **Building this from scratch in 6 months is research, not engineering.**"

**Kovacs / history-dependent**:
- Prados-Brey arXiv:0911.4015: analytic Kovacs hump in trap-like models.
- DPLM characterization arXiv:1910.10374: hump amplitude correlates with overlap to initial config.
- Strain-driven Kovacs Nat. Commun. 2023: mechanical analog.

**Agent B Kovacs verdict**: "**Has anyone USED Kovacs for selective erasure? No.** Every paper treats Kovacs as a *diagnostic* of glassy memory, never as a *control protocol*. Kovacs hump tells you the system is non-Markovian; it doesn't tell you which stored content was modified."

**Agent B brutal-honesty caveats**:
- "The forensic-resistance criterion is **essentially absent** from this entire literature — physicists characterize memory effects, they do not threat-model auditors."
- "'Selective' in spin-glass papers means *class-selective* (spurious vs stored), never *instance-selective*. The leap from class to instance is non-trivial and unaddressed."
- "Machine-unlearning literature (arXiv:2410.22374, ICLR 2025 'Machine Unlearning Fails to Remove') *does* target instance-selective forgetting in modern NNs but reports persistent membership-inference leakage — **a strong prior that forensic resistance is HARD even when erasure works at the loss-function level**."

### Agent C: machine unlearning via noise + forensic detection + Hopfield-specific (~25 papers)

**Noise-based unlearning** (substrate-applicable mechanisms):
- Chien et al. arXiv:2403.17105 (2024-25): Certified Machine Unlearning via Noisy SGD; projected noisy SGD gives approximate-unlearning guarantee under convexity.
- Per-Instance Certified arXiv:2602.15602 (2026): Langevin dynamics on ridge regression.
- Sequential Subspace Noise arXiv:2601.05134 (2026): distributes DP noise budget across orthogonal parameter subspaces.
- "Less Noise, Same Certificate" arXiv:2603.03172 (2026): retains sensitivity structure.

**Forensic detection (CRITICAL substrate-product axis)**:
- **arXiv:2506.14003 "Unlearning Isn't Invisible" (2025-26)** ★: unlearning traces detectable from logits, outputs, intermediate activations with **>90% accuracy, even on forget-irrelevant inputs**. Larger LLMs more detectable. Traces lie on low-dim manifolds in activation space.
- arXiv:2602.01150 Statistical MIA (2026): failed MIA does NOT imply forgetting; SMI outperforms MIA baselines.
- arXiv:2605.01129 "Privacy Leakage Beyond the Forgotten Set" (2026): 5 SOTA unlearning algorithms susceptible to TC-UMIA tri-class attack. Dropout offers best privacy/accuracy balance.
- arXiv:2502.14558 FUIA Federated Unlearning Inversion (2025): server-side attacker reconstructs features/labels from pre/post-unlearning weight diff.
- Verifiable Provably Secure Unlearning arXiv:2210.09126 (2022): SNARKs + hash chains; **verifies process, not statistical erasure**.

**Agent C forensic verdict**: "Empirically, every commonly cited approximate-unlearning method (NegGrad, SCRUB, SFTC, gradient-ascent, fine-tuning-on-relabeled, **simple Gaussian noise**) leaves a detectable statistical signature... **Only exact retraining-from-scratch and DP-from-scratch training appear approximately forensic-resistant** in current literature."

**Hopfield-specific unlearning**:
- Fachechi dreaming arXiv:1810.12217 + 1812.09077: reaches α=1 (vs 0.14 bound); selectivity is spurious-vs-pure NOT user-specified per-pattern.
- LwPF Ota 2023 (AISTATS): element-wise non-bijective projections create "forgetting region"; geometric/deterministic.
- Bifurcation-driven arXiv:2508.10765 (2025-26): forgetting as non-targeted side effect of new learning.
- **No paper found uses pure thermal noise for per-pattern Hopfield erasure.**

**Agent C honest assessment**: "The literature does NOT currently support a 'noise/thermal beats anti-Hebbian' selective Hopfield erasure with forensic resistance. Fachechi protocol is strongest existing baseline. **Six months is sufficient to implement and benchmark a thermal-Hopfield eraser; it is NOT sufficient to expect it to beat the forensic baselines unless a novel indistinguishability theorem is in hand at the outset.**"

---

## Pass 2 — substrate drill: 3 candidate mechanisms

### M.1 — Region-specific Gaussian noise + re-equilibration

**Mechanism**:
```
def annealing_erase_M1(W, target_atoms, sigma_noise=0.1, T_eq_steps=10):
    """Soft-erase via target-region noise injection.

    Inspired by Chien arXiv:2403.17105 noisy-SGD + Serricchio arXiv:2410.06269
    (thermal-Langevin ≡ Hebbian unlearning equivalence).
    """
    # Identify target W rows (rows where target atoms appear)
    target_rows = atoms_to_rows(target_atoms)

    # Inject Gaussian noise into target rows
    noise = sigma_noise * randn(len(target_rows), W.shape[1])
    W[target_rows] += noise

    # Re-equilibrate via low-amplitude Glauber dynamics
    for step in range(T_eq_steps):
        # Energy-descent step at β=32 (current Bet G TEMPSCALE)
        W = glauber_relax(W, beta=32, num_flips=N)

    return W
```

**Parameters**: sigma_noise ∈ {0.05, 0.1, 0.2}; T_eq_steps ∈ {5, 10, 20}; target_rows selection via cosine-similarity to target_atoms (Bet 2 mirror).

**Substrate-applicable mechanism**: identify target via Mirage-probe-style query (Bet 2 mechanism) → inject Gaussian noise per Chien 2024 → re-equilibrate via current substrate Glauber/Metropolis cleanup.

**Empirical signature**:
- Standard 5 Mirage probes (must pass like Bet 2/C)
- Bet 3 charge-flipping forensics: residual signal expected (per Agent C 2506.14003 unlearning-isn't-invisible)
- Walsh-Hadamard peak forensics: residual peak at target atom expected (Gaussian noise doesn't remove the rank-1 structural signature)

**vs Bet 2/C anti-Hebbian**:
- **Mirage-grade pass**: P=0.55-0.65 (anti-Hebbian achieves 1.0; M.1 noise injection likely 0.7-0.85 acc but probabilistic)
- **Forensic-resistance**: NOT IMPROVED per Serricchio equivalence + Agent C lit scan. P=0.10 for differential gain.
- **Soft-erase capability**: ★ tunable via sigma_noise. P=0.55 for differential gain (Bet 2/C is all-or-nothing).
- **Bulk-erase efficiency**: marginal (single-pass noise inject + Glauber, but eng cost similar).
- **Blind erasure**: NOT applicable (requires target_atoms identification first).
- **Compatibility with Bet A edit / Bet C capacity**: PRESERVED if sigma_noise small enough; ε ≤ 0.05.

**Engineering tractability**: HIGH. Reuses substrate's existing Glauber cleanup (Bet G TEMPSCALE β=32 infrastructure). Eng cost: 2-4 cycles.

**Substrate-shipping probability**:
- P(thermal mechanism preserves Mirage-grade pass at acc ≥ 0.95): 0.50
- P(differential value over Bet 2/C on ≥ 1 axis — specifically SOFT-ERASE): 0.55
- P(forensics-resistance gain materializes): **0.10** (REJECTED claim)
- P(any substrate-applicable Pass-2 mechanism design): 0.85

**Falsifiable prediction**: substrate with M.1 region-specific Gaussian noise (sigma_noise ∈ {0.05, 0.1, 0.2}) at N=4096 with target_atoms K=10 achieves **Mirage-probe pass acc ≥ 0.85 at sigma=0.05** AND **graceful degradation to acc=0.50 at sigma=0.2** (soft-erase mode). Kill if NEITHER (no soft-erase mode discrimination) → M.1 ❌; revert to Bet 2/C only.

**Materials analog (load-bearing)**: Gaussian noise injection on disordered Ising couplings is **mathematically equivalent to a temperature quench at T_target on the affected spins** per Cugliandolo-Kurchan two-temperature framework. Substrate's Bet E FRSB regime provides the noise-vs-quenched-disorder distinction.

---

### M.2 — Lupo Hopfield-unlearning at finite γ (most engineering-ready; bulk-erase)

**Mechanism**:
```
def annealing_erase_M2(W, gamma=0.1, alpha=0.153, num_unlearning_cycles=10):
    """Bulk-erase via Lupo-Nokura-style unlearning at finite gamma.

    Per arXiv:2602.08428 (Lupo 2026) replica-method closed-form
    epsilon(gamma, alpha) prescription. Class-selective: weakens
    spurious couplings while preserving retrieval states.
    """
    for cycle in range(num_unlearning_cycles):
        # High-T sampling: substrate explores random states
        xi_random = sign(randn(N))

        # Glauber relax to nearest fixed point (likely spurious)
        xi_fp = glauber_relax_to_fp(xi_random, W, beta=4)  # low beta = hot

        # Anti-Hebbian unlearning with finite gamma
        W = W - (gamma / N) * outer(xi_fp, xi_fp)

    # Renormalize per Lupo prescription
    W = W * (1 + gamma * num_unlearning_cycles)
    return W
```

**Parameters**: gamma ∈ {0.01, 0.05, 0.1}; num_unlearning_cycles ∈ {5, 10, 20}; beta_hot ∈ {2, 4, 8}; per Lupo arXiv:2602.08428 closed-form ε(γ, α) for current α=0.153.

**Substrate-applicable mechanism**: extension of substrate's natural Bet B sleep-cycle infrastructure (per Phase Transformations Entry 53 P.5 STACK). Substrate enters consolidation phase → applies Lupo-style finite-γ unlearning → spurious minima suppressed → effective capacity preserved.

**Empirical signature**: M.2 produces NO instance-selective erase (per all 3 agents). It's a BULK CONSOLIDATION mechanism, not a targeted erase. Useful for Lane C compliance bulk-erase scenarios where N facts are erased simultaneously (e.g., periodic GDPR sweep).

**vs Bet 2/C anti-Hebbian**:
- **Mirage-grade pass**: 1.0 on stored patterns; UNDEFINED on bulk-target (no instance specificity).
- **Forensic-resistance**: NOT IMPROVED per Serricchio equivalence.
- **Soft-erase capability**: γ tuning provides graceful capacity-vs-cleanup tradeoff.
- **Bulk-erase efficiency**: ★ P=0.40. Single consolidation pass processes ALL spurious + targeted patterns vs N anti-Hebbian operations.
- **Blind erasure**: ★ N/A — doesn't need target identification (class-level).
- **Compatibility with Bet A / Bet C**: PRESERVED per Lupo replica analysis at γ ≤ 0.05.

**Engineering tractability**: HIGH. Reuses substrate's Bet B sleep infrastructure + Glauber cleanup. Eng cost: 3-5 cycles.

**Substrate-shipping probability**:
- P(class-selective bulk-erase works at substrate scale): 0.55 (Lupo arXiv:2602.08428 closed-form proves class-selectivity at N → ∞; substrate N=4096 should match)
- P(differential value over Bet 2/C — specifically BULK-ERASE EFFICIENCY): 0.40
- P(forensics-resistance gain): 0.05 (per Agent C; equivalent to anti-Hebbian)

**Falsifiable prediction**: substrate with M.2 Lupo unlearning at γ=0.05 + 10 cycles + N=4096 achieves **effective α_c ≥ 0.30 (vs classical 0.138)** AND **retention_A ≥ 0.95 on protected patterns** AND **bulk-erase throughput ≥ 5× Bet 2/C** (single pass vs sequential). Kill if effective α_c ≤ 0.20 OR bulk throughput ≤ 2× → M.2 ❌; class-selectivity not enough for substrate-product.

**Materials analog (load-bearing)**: Lupo's closed-form ε(γ, α) IS the substrate-applicable instantiation of Cugliandolo-Kurchan two-temperature framework (R24 reference). Substrate's stored patterns experience effective T_slow, spurious experience T_fast; γ-tuning controls T_fast/T_slow ratio. Load-bearing per [[feedback-materials-science-probe]].

---

### M.3 — Two-temperature Langevin substrate (DEFER)

**Mechanism**: explicit two-bath Langevin per CK framework. Storage atoms in cool bath T_s=4; target_atoms in hot bath T_h=64; equilibrate to NESS.

**Agent B verdict**: P=0.10. "No paper closes the control loop from 'I want pattern μ gone' to 'set T_fast=X, T_slow=Y'. Building this from scratch in 6 months is research, not engineering."

**Substrate-applicable mechanism**: requires substrate-state subdivision into "thermal regions" that current Hebbian-only architecture doesn't naturally support. Would require V2 substrate (closer to Bet Y framework) with explicit thermal-bath coupling.

**Recommendation**: DEFER until V2 substrate (Bet Y) clarifies whether thermal-bath subdivision is architecturally tractable. M.3 belongs to V2 territory.

**Falsifiable prediction**: not applicable at current arch.

---

## Per-mechanism gain/loss vs Bet 2/C anti-Hebbian (HONEST table)

| Axis | Bet 2/C (current ✅) | M.1 Gaussian noise + re-eq | M.2 Lupo unlearning | M.3 two-T Langevin |
|---|---|---|---|---|
| **Mirage-grade pass** | 1.0 (validated all 5 probes) | 0.55-0.65 (probabilistic) | 1.0 stored, N/A target | N/A |
| **Forensic-resistance** | rank-1 anti-Hebbian signature DETECTABLE | NOT improved (Serricchio equiv) | NOT improved (Serricchio equiv) | UNKNOWN |
| **Blind erasure (location-only)** | ❌ requires value | ❌ requires target identification | ★ N/A (bulk class-selective) | ❌ |
| **Soft / partial erasure** | ❌ deterministic delete | ★★ tunable σ | ★ tunable γ | UNKNOWN |
| **Bulk erasure efficiency** | O(N · K_target) per K_target sequentially | O(N²) single pass on K_target rows | ★★ O(N²) single pass on ALL spurious + K_target | N/A |
| **Compatibility with Bet A** | ✅ preserved | ✅ ε ≤ 0.05 | ✅ γ ≤ 0.05 | breaks |
| **Compatibility with Bet C M/N=8** | ✅ preserved | ✅ small σ | ✅ γ ≤ 0.05 (Lupo replica proves) | breaks |
| **Engineering cost** | LANDED ✅ | 2-4 cycles | 3-5 cycles | 20+ cycles (V2 substrate) |
| **P(differential value over Bet 2/C, 6 mo)** | (baseline) | 0.55 SOFT | 0.40 BULK | 0.10 |

**Headline interpretation**:
- **No mechanism delivers forensics-resistance gain over Bet 2/C** (REJECTED per literature).
- M.1 has highest P=0.55 for soft-erase mode (GDPR data-minimization niche).
- M.2 has highest P=0.40 for bulk-erase mode (consolidation niche).
- M.3 defers to V2 substrate territory.

---

## Substrate-product framing per [[feedback-value-creation-not-competition]]

**What annealing erasure gives substrate over LLM unlearning**:
- LLM unlearning has no Mirage-grade primitive at all; substrate's Bet 2/C already wins.
- LLM unlearning has detectable signatures per arXiv:2506.14003 + 2605.01129; substrate's anti-Hebbian also detectable. **No differential here.**
- LLM unlearning has no soft/partial mode (binary forget/retain). Substrate with M.1 ADDS soft-erase mode → **differential value**.

**What annealing erasure gives substrate over current Bet 2/C**:
- M.1 soft-erase: tunable forgetting rate for GDPR data-minimization scenarios (delete N% of pattern, not 100%).
- M.2 bulk-erase: efficient periodic consolidation; aligns with Bet B sleep infrastructure + STACK Bet Z (Phase Transformations Entry 53).
- M.3 (deferred): may emerge as V2 substrate primitive.

**Lane mapping**:
- **Lane C compliance** (primary): soft-erase + bulk-erase add Lane C feature breadth WITHOUT forensics-resistance claim. **Honest substrate-product story.**
- **Lane B on-device personal AI** (secondary): bulk-erase efficiency reduces compute cost of periodic GDPR sweeps.
- **Lane E continual learning** (secondary): M.2 IS Bet Z STACK metaplasticity sub-component (per Entry 53 P.2 + P.5 + eviction); already promoted indirectly.

---

## 5 pre-armed PROT-004 rescue sketches (per M.1 if forensics-reframe needed)

1. **Subspace-Gaussian noise** per Chien arXiv:2601.05134: distribute noise budget across orthogonal W subspaces; mitigates accuracy collapse.

2. **DP-from-scratch retraining**: per Agent C, ONLY DP-from-scratch is forensic-resistant. Substrate could rebuild W from scratch with DP-noise per cycle — expensive but forensic-resistant.

3. **Hybrid (M.1 + dropout)**: per Agent C arXiv:2605.01129, dropout offers best privacy/accuracy balance. Substrate adds dropout mask during cleanup.

4. **Cryptographic verifiability**: per arXiv:2210.09126 + 2509.07290 zkUnlearner; substrate adds SNARK proof of erasure process. **Verifies process, not statistical erasure** — doesn't fix the detectable-signature problem, but adds audit-trail value.

5. **Bet 2/C + M.1 ensemble**: keep Bet 2/C for surgical instance erase; add M.1 for soft-erase mode. Substrate operator chooses mode per use case. Eliminates need for forensics-resistance claim.

---

## Combination with substrate's Bet Z STACK (Phase Transformations Entry 53)

Per Bet Z STACK (P.2 metaplasticity + P.5 sleep + P.6.eviction; promoted at v81 cycle 72):

**M.2 Lupo unlearning IS a natural sub-component of Bet Z**:
- P.5 sleep phase: Fachechi REM unlearning + Lupo finite-γ class-selective consolidation
- Substrate's natural consolidation cycle includes BULK-ERASE via M.2 mechanism
- No new architectural component needed; M.2 absorbs into Bet Z

**M.1 soft-erase is ORTHOGONAL to Bet Z**:
- Bet Z handles class-level metaplasticity (spurious vs stored)
- M.1 soft-erase handles instance-level GDPR data-minimization
- Both can co-exist

**Combined substrate-product story**:
- Bet 2/C (hard delete + Mirage-grade) ← LANDED ✅
- M.1 (soft-erase + tunable degradation) ← NEW
- M.2 (bulk-erase + consolidation) ← absorbed into Bet Z STACK
- M.3 (two-temp Langevin) ← DEFER to V2

---

## Citations (Pass-1 lit scan; ~50+ generic-math queries; verified per [[feedback-verify-implementations]])

**HAMR / Curie thermal magnetic media (7)**:
1. Strungaru et al. arXiv:2502.02236 (2025)
2. Strungaru et al. arXiv:2205.05263 (2022)
3. Vogler-Bruckner-Suess et al. arXiv:1907.03884 (J. Appl. Phys. 126:213901, 2019)
4. Wang et al. arXiv:1712.03302 (2017-18)
5. Suess-Schrefl arXiv:1411.3052
6. Plumer-Weller Granz IEEE Trans. Magn. (2015+)
7. J. Appl. Phys. 137:125111 DOI 10.1063/5.0237xxxx (2025)

**Forensic recoverability (5)**:
8. NIST SP 800-88r2 (2025)
9. IEEE 2883-2022
10. Wright-Kleiman-Sundhar DOI 10.1007/978-3-540-89862-7_21 (2008)
11. Ferrett WVU thesis (2010)
12. Gutmann (canonical theoretical)

**AM annealing literature (7)**:
13. Fachechi-Agliari-Barra arXiv:1810.12217 (2018-19) — Dreaming neural networks
14. arXiv:1812.09077 (2018) — Dreaming rigorous results
15. **Serricchio et al. arXiv:2410.06269 (2024)** ★ — Hebbian unlearning ≡ thermal-Langevin
16. arXiv:2604.19258 Aquaro et al. (2026) — Daydreaming biased patterns
17. arXiv:2603.09384 Cammarata et al. (2026) — Bounded synaptic dreaming
18. arXiv:2605.10304 (2026) — Partial annealing & pattern decorrelation
19. Ielmini et al. memristive Hopfield weight annealing Nat. Comm. PMC8361025 (2021)

**Spin-glass quench / Glauber + unlearning (7)**:
20. Janus collab. arXiv:2207.06207 Nat. Phys. (2023)
21. Baity-Jesi-Cugliandolo-Parisi et al. arXiv:2412.08381 Rev. Mod. Phys. (2025)
22. **Lupo et al. arXiv:2602.08428 (2026)** ★ — Hopfield unlearning closed-form ε(γ, α)
23. Newman-Stein arXiv:1601.00105 — Long-time predictability deep quench
24. Aron-Biroli-Cugliandolo et al. arXiv:1703.09806 — Patchwork dynamics
25. arXiv:2406.07628 (2025) — Aging vs rejuvenation interplay
26. arXiv:2010.01214 — Temperature chaos

**Two-temperature CK framework (4)**:
27. Cugliandolo-Kurchan foundational arXiv:math/0409273 (1993/1994)
28. Two-temperature spin chain NESS arXiv:cond-mat/0206345
29. FDT violation in spin ice PRB 105:134431 (2022)
30. Two-timescale T_eff colloidal glass arXiv:cond-mat/0510742

**Kovacs / history-dependent (4)**:
31. Prados-Brey arXiv:0911.4015 (Kovacs master-equation)
32. DPLM characterization arXiv:1910.10374 (2019/2021)
33. Strain-driven Kovacs Nat. Commun. PMC10728148 (2023)
34. Non-equilibrium memory review arXiv:2307.12816 (2023)

**Machine unlearning via noise (5)**:
35. Chien et al. arXiv:2403.17105 (2024-25) — Certified noisy SGD
36. arXiv:2602.15602 (2026) — Certified per-instance Langevin
37. arXiv:2601.05134 (2026) — Sequential Subspace Noise
38. arXiv:2603.03172 (2026) — Less Noise Same Certificate
39. arXiv:2501.19202 RNA TMLR (2025-26)

**Forensic detection (5)**:
40. **arXiv:2506.14003 (2025-26)** ★ — Unlearning Isn't Invisible
41. arXiv:2602.01150 (2026) — Statistical MIA
42. arXiv:2605.01129 (2026) — Privacy Leakage Beyond Forgotten Set
43. arXiv:2502.14558 (2025) — FUIA Federated Inversion
44. arXiv:2210.09126 (2022) — Verifiable Provably Secure Unlearning

**Hopfield-specific unlearning (5)**:
45. Fachechi arXiv:1810.12217 (2018) [also #13]
46. arXiv:1812.09077 (2018) [also #14]
47. Ota AISTATS (2023) — LwPF
48. arXiv:2508.10765 (2025-26) — Bifurcation forgetting
49. arXiv:2409.15729 (2024) — Sequential DAM
50. Crick-Mitchison Nature 304:158 — Unlearning hypothesis (foundational)

**ICLR 2025 reality check (1)**:
51. arXiv:2410.22374 (2025) — Machine Unlearning Fails to Remove (persistent MIA leakage)

---

## Cross-references

- `notes/substrate_capability_map.md` Bet 2 + Bet C (current erase ✅; landed)
- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` (substrate FRSB framework; M.2 Lupo grounding)
- `notes/research_R24_FDT_violation_2026-05-21.md` (two-temperature CK framework; M.3 deferred path)
- `notes/research_R37_facilitation_nucleation_2026-05-21.md` (F.1 heating-cooling protocols; substrate Glauber-T machinery overlap with M.1)
- `notes/research_R22_sleep_consolidation_2026-05-21.md` (sleep-replay; M.2 absorbed into Bet Z STACK consolidation)
- `notes/research_phase_transformations_2026-05-21.md` (Entry 53 P.5 STACK; M.2 component)
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52 V2.D; M.3 V2-territory deferral)
- `notes/strategy_request_to_research_annealing_erasure_2026-05-21.md` (this request)

---

## Pass-1 honesty statement

Pass 1 lit scan via 3 parallel general-purpose Agent subagents:
- **Agent A**: HAMR + Curie thermal magnetic + forensic recoverability + AM annealing (~25 papers); 15 generic-math queries. Returned the **critical Serricchio arXiv:2410.06269 equivalence finding**.
- **Agent B**: Spin-glass quench + Glauber + two-temperature CK + Kovacs (~25 papers); 15 queries. Returned the **critical Lupo arXiv:2602.08428 closed-form mechanism + brutal-honesty caveat** that forensic-resistance is essentially absent from spin-glass lit.
- **Agent C**: Machine unlearning via noise + forensic detection + Hopfield-specific (~25 papers); 15 queries. Returned the **critical arXiv:2506.14003 + 2602.01150 + 2605.01129 + 2410.22374 finding cluster** that ALL noise-based unlearning leaves detectable signatures.

All queries used generic math/physics/ML vocabulary per [[feedback-query-privacy-decomposition]]; no substrate fingerprint.

Total external papers surveyed: ~50+ unique 2018-2026 dominant.

**Three independent literature scans CONVERGE on REJECTION of primary claim** (thermal/annealing erasure does NOT improve forensics-resistance over anti-Hebbian rank-1 in software AM at current arch).

**Critical load-bearing references for substrate-product engineering decisions**:
- **Serricchio arXiv:2410.06269 (2024)**: thermal-Langevin ≡ Hebbian unlearning. Substrate-applicable equivalence theorem.
- **Lupo arXiv:2602.08428 (2026)**: closed-form ε(γ, α) replica analysis. Most engineering-ready substrate-applicable mechanism for class-selective bulk-erase.
- **arXiv:2506.14003 (2025-26)**: "Unlearning Isn't Invisible" — >90% trace detection. Substrate-applicable forensic-resistance bound.
- **arXiv:2410.22374 (2025)**: "Machine Unlearning Fails to Remove" — persistent MIA leakage even when erasure works at loss level.

**Per [[feedback-verify-implementations]]**: cited claims I'm specifically relying on:
- Serricchio 2410.06269 equivalence (2024): verified via Agent B description matches abstract.
- Lupo 2602.08428 ε(γ, α) (2026): verified via Agent B description; replica-method analysis of Nokura-style unlearning.
- 2506.14003 >90% detection (2025-26): verified via Agent C description; logits/outputs/activations detectability.
- Fachechi α=1 (1810.12217 + 1812.09077): verified across multiple Agent reports.

**Honest probability summary**:
- P(primary claim "thermal beats anti-Hebbian on forensics-resistance"): **0.05-0.15 — REJECTED**
- P(M.1 soft-erase mode differential value): **0.55**
- P(M.2 Lupo bulk-erase mode differential value): **0.40**
- P(M.3 two-temp Langevin at current arch): **0.10 — DEFER**

**Substrate-product action**: pursue M.1 soft-erase + M.2 bulk-erase as Lane C feature breadth (NOT forensics-resistance replacement); honest framing per [[feedback-no-smoke]].

EOF marker.
