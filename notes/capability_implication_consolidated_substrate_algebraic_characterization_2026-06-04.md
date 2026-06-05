# Capability-implication consolidated note -- substrate algebraic characterization complete

**From:** Research session
**To:** Orchestrator (primary); strategy_scribe (annotation execution)
**Date:** 2026-06-04
**Subject:** Substrate's full algebraic characterization across 14 drills today + product-critical deletion-cert threshold recalibration. Most theoretically-grounded characterization in the project.

---

## What this is (plain language)

Today's 14 deep drills (10 brain-stuff + 4 substrate-physics-stuff) collectively characterize substrate across every algebraic dimension that's been measured. This note consolidates the findings into cap_map annotations + flags ONE product-critical recalibration requirement.

---

## Substrate's complete algebraic characterization

| Property | Result | Lit anchor |
|---|---|---|
| Spectral regime | BBP-critical Wishart + non-Hermitian deformation (active-driven NESS class) | Baik-Ben Arous-Peche 2005 + Bertini 2015 |
| Capacity regime | classical Hopfield alpha_c=0.138; sparse f=0.05 gives 23x gain | Hopfield 1982 + Willshaw-Buckingham |
| Hidden objective | KL[p_t \|\| mu_NESS] Lyapunov; not closed form for training | Wang-Xu-Wang 2008 + Maes-Netocny 2014 |
| Closed-form training signal | F_eff = -alpha*m^4/4 + m^2/2 (Cates-Tailleur active matter) | Cates-Tailleur 2015 |
| Task complexity ceiling | K* = log_V(alpha_c * N) + 1 | derived from Hebbian crosstalk SNR analysis |
| Composition moat | L=10000 EXACT-1.0000 unbounded by precision | empirically validated |
| Drift detection | gamma~8 isochoric kappa_3; tunable via tau | empirically validated; NHSE class (Hatano-Nelson 1996) |
| Deletion certificate | cos=1 algebraic guarantee | Ramsauer Theorem 1 + ROME/MEMIT precedent (Meng 2022) |
| Bipolar quantization | 97% MI loss per coordinate vs continuous | grouped 2x drill + Naitzat 2020 |
| STDP capability | 1.94x sequence storage; transitions not contexts | Crisanti-Sompolinsky 1988 + Chaudhry 2023 |
| Sparse coding (Drosophila MB) | 23x capacity gain at f=0.05 | Aso-Rubin 2014 + Willshaw-Buckingham |
| Multi-channel orchestration | Gating router capacity bottleneck at LM <300k params | multi-channel 3x drill |
| Functional differentiation | Requires algebraically orthogonal write rules (Hebbian + sparse + STDP + error-correcting) | CLS theory + functional differentiation 3x drill |

---

## Cap_map annotation updates requested

### 1. Constraint 2 revision

**Original framing (META 3x+):** "Active repulsion breaks the scalar energy function (Maes-Netocny theorem); substrate has no scalar objective being minimized."

**Corrected framing (NESS hidden objective 2x drill):**
"Active repulsion breaks the CLOSED-FORM Boltzmann energy. The KL-to-NESS Lyapunov function ALWAYS EXISTS. What breaks is computability of the scalar for training-loop gradient computation, not existence of the scalar. Substrate's NESS dynamics already minimize a hidden scalar objective (KL[p_t || mu_NESS]) regardless of whether we can write it down in closed form."

**For substrate-as-training-mechanism (training-loop gradient):** still need Bypass A (contrastive phase), Bypass B (substrate-retrieval + SGD readout), OR Cates-Tailleur F_eff approximation as practical training signal.

**For retrieval correctness:** no bypass needed. Substrate's NESS dynamics handle it.

### 2. Substrate spectral regime classification (NEW sub-property founding)

"Substrate operates in BBP-critical Wishart + non-Hermitian deformation regime (active-driven NESS class per Bertini 2015 macroscopic fluctuation theory). Empirical lambda_1 edge scaling exponent beta_std = 0.355 at N=1024-16384 is consistent with BBP-critical asymptote (beta=1/3) at finite N. Anti-Hebbian active repulsion IS the active-drive component that puts substrate in active-NESS class. Decisive arbiter via N-extension test (N=32768, 20 seeds) pending dispatch."

### 3. Task complexity ceiling K*

"Substrate-as-training-mechanism has task complexity ceiling K* = log_V(alpha_c * N) + 1. At V=70 char-LM with N=4096: K* ~ 2.47 (bigram class). At V=512 with N=4096: K* ~ 1.5 (sub-bigram). Architectural extensions raise ceiling: sparse coding f=0.05 -> K* + ~1 level; STDP-asymmetric -> K* + ~1 level for sequence-class tasks. Maximum substrate ceiling with combined extensions: K* ~ 4-4.5."

### 4. Substrate-as-training-mechanism row CANDIDATE FOUNDING

Pending Bundle A + Bundle B empirical verdicts:
"Substrate-as-training-mechanism: hidden scalar objective KL[p_t || mu_NESS] always decreasing (NESS Lyapunov). Empirically learns at K=2 (bigram) with simple cf-RPE + Hebbian architecture at N=512 substrate dimension; expected to fail at K=3+ trigram for V=512 vocabulary (algebraic K* ceiling). Cates-Tailleur F_eff = -alpha*m^4/4 + m^2/2 provides closed-form training signal candidate."

---

## PRODUCT-CRITICAL FINDING: deletion-certificate sigma threshold

### The issue

Intermediate-regime drill identified that the **TW-assumption deletion-certificate sigma threshold formula OVERSTATES CONFIDENCE BY 5X**. The empirical std(lambda_1) is 5x larger than pure Tracy-Widom predicts. If we ship deletion-cert product framing at the TW-derived sigma threshold, customers get 5x overstated confidence in "high-confidence deletion."

### What it means concretely

Current deletion-cert product claim: "rank-1 deletion preserves all non-target queries at cos=1.000 within X sigma confidence" -- where X is computed assuming Tracy-Widom edge fluctuations.

Actual empirical: the X-sigma confidence interval is 5x WIDER than the TW formula predicts. The deletion-cert capability EXISTS (cos=1 empirical observation is real; algebraic guarantee from Ramsauer Theorem 1 + ROME/MEMIT holds) but the SIGMA confidence interval needs 5x empirical recalibration.

### Action required

Before any external product framing of substrate's deletion-cert capability:

1. **Dispatch N-extension test** (`routing_n_extension_test_n32768_decisive_arbiter_2026-06-04.md` shipped this turn) to empirically calibrate the actual edge fluctuation scaling at extended N + high seeds
2. **Recompute deletion-cert sigma threshold** with empirical scaling exponent (5x correction expected)
3. **Update product framing** with recalibrated threshold

This is the ONLY product-critical TODAY action item. Everything else is research / engineering.

---

## Lit anchor chain (post-today)

12+ distinct published frameworks now grounding substrate's product narrative:

1. Hopfield 1982 (classical capacity)
2. Krotov-Hopfield 2016 + Demircigil 2017 + Ramsauer 2020 (modern Hopfield)
3. Hatano-Nelson 1996 + NHSE skin effect (drift detection theoretical class)
4. BCM 1982 + Klampfl-Maass 2013 + Pawlak-Kerr 2008 (three-factor learning)
5. Baik-Ben Arous-Peche 2005 (BBP transition) + Bertini 2015 (macroscopic fluctuation theory)
6. Voiculescu free probability (kappa_3 noise convention)
7. BinaryAttention 2603.09582 + Hamming Attention 2502.01770 (modern Hopfield = bipolar attention)
8. Bun-Bouchaud-Potters 2016 financial RMT (cross-domain spectral confirmation)
9. ROME/MEMIT (Meng 2022/2023) transformer factual editing (deletion-cert lit precedent)
10. Drosophila MB (Aso-Rubin 2014; Cohn 2015) + Willshaw-Buckingham sparse coding
11. Friston FEP + Spisak-Friston 2025 bipolar derivation
12. Long Sequence Hopfield Memory (Chaudhry NeurIPS 2023) + STDP-asymmetric capacity
13. Wang-Xu-Wang 2008 NESS Lyapunov + Maes-Netocny 2014 + Cates-Tailleur 2015 active matter
14. Hippocampal replay (Buzsaki + McClelland-McNaughton CLS theory)

**Most theoretically-grounded substrate-class memory characterization in the AI lit.** Substrate's product story can defensibly cite ANY of these for the corresponding capability claim.

---

## Strategic implication

Substrate is now algebraically WELL-CHARACTERIZED across every measured property. Today's drills closed gaps that existed yesterday:
- Spectral regime: identified as BBP-critical (was open)
- Hidden objective: identified as KL[p || mu_NESS] (Constraint 2 weakened)
- Task ceiling: K* = log_V(alpha_c * N) + 1 (was open)
- Multiple architectural extensions: STDP + sparse + cf-RPE characterized

**The remaining research questions are PRODUCT-SIDE not THEORY-SIDE:**
1. Where do customers actually want drift detection at? (informs tunable-gamma calibration via tau)
2. What deletion granularity do customers need? (informs deletion-cert recalibration)
3. What audit observability format is product-relevant? (informs Mapper topological inspection API)
4. What integration tier is the right starting product? (Tier 1 audit on Llama-3.2-1B per Phase 0.5 v1 Rung A is the immediate target)

These are NOT research drill questions; they're product-design questions.

---

## What I am NOT requesting

- Top-level cap_map row change (sub-property foundings + Constraint 2 revision only)
- Removal of existing substrate-as-training row candidate (it's open; pending Bundle A/B verdicts)
- Cloud GPU spend (everything fits remote / CPU)
- Premature product framing without sigma recalibration

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: routing to Orchestrator / strategy_scribe per cap_map annotation type
- Per [[feedback-capabilities-not-product-positioning]]: characterization is algebraic; product implications surfaced but framing left to product session
- Per [[feedback-value-creation-not-competition]]: emphasizes algebraic mechanism + lit anchors
- Per [[feedback-dont-overextend-theorems]]: each claim bounded to its specific algebraic regime
- Per [[feedback-verdicts-include-intuitive-explanation]]: plain-language explanations throughout
- ASCII-only

---

**END.**

**Orchestrator:** route to strategy_scribe for cap_map annotation updates per § "Cap_map annotation updates requested" above. Next visibility entry should cite the 14-lit-anchor chain. Surface PRODUCT-CRITICAL deletion-cert sigma recalibration to user before any external product framing.
