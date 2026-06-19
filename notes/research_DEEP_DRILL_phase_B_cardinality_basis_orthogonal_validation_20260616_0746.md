# Research DEEP DRILL: Phase B Task-Surface — Cardinality vs Ternary Motif vs Element-Layer

Date: 2026-06-16
Trigger: 2x deep-drill validation of Exp-Dev recommendation that CARDINALITY / COUNTING / QUANTIFIER is the #1 highest-basis-gap-potential Phase B candidate.
Method: 3 parallel Sonnet lit-scan sub-agents (VSA cardinality, ternary tensor motifs, internal element-layer precedents) + Opus synthesis.
SAFETY: All external queries used generic math terms. ASCII-only output. No project-internal nomenclature off-platform.

---

## (a) HEADLINE

CARDINALITY is empirically validated as binding-orthogonal across 4 independent author clusters (Plate; Kanerva/Kleyko; Eliasmith/Komer; Frady/Sommer/Kymn). Every published numerical / counting capability in VSA arrives as an ADDED operator (FPE, RNS-HDC, NEF integrator), NOT as a composition of {bind, bundle, similarity, cleanup, unbind}. No formal impossibility theorem exists, but the constructive evidence is unanimous. TERNARY PARTIAL-SYMMETRIC MOTIFS (Exp-Dev's #2) are MORE expressively-decisive but LESS task-distinctive: HypE/GETD prove position-tagged rank-1 binders are fully expressive, so the impossibility is only relative to position-BLIND binder families (which is the current substrate basis). RECOMMENDATION: LEAD Phase B with CARDINALITY as primary basis-gap-forcing task; KEEP ternary partial-symmetric motif as a tier-2 secondary that probes the basis from a different angle (composition cost rather than primitive absence).

## (b) Cheap decisive test

A two-arm Phase B task surface:

**Arm 1 (PRIMARY) — Cardinality basis-gap test.** Construct a task family of the form "given a bundle of bound role-filler pairs, return the count / answer 'how many distinct fillers', 'most', 'at least k'." Evaluate three configurations:
  - C1: Substrate's existing 38 binders + bundle-norm threshold readout (the "composable from basis" hypothesis).
  - C2: Substrate's basis + ONE added cardinality primitive (NEF-integrator-class or bundle-norm-counter).
  - C3: Substrate's basis + DreamCoder-style internal abstraction discovery (composition-search gated by task-equivalence).

HARD-PASS for "cardinality IS basis-orthogonal" = C1 ceiling demonstrably below C2 floor by >= 0.20 accuracy at modest scale (~100 items per bundle, vocabulary 50-200). C1 cannot be closed by raising dimension N alone (test at N=1024, 2048, 4096).

HARD-FAIL = C1 reaches within 0.05 of C2 by N=2048 — cardinality is composable; recommendation REFUTED.

**Arm 2 (SECONDARY) — Ternary partial-symmetric motif.** Mine real KG (Freebase/WikiPeople/JF17K) for ternary tuples with empirical partial symmetry (sym across 2 positions, asym to 3rd). Measure link-prediction accuracy with:
  - position-blind rank-1 binders (current substrate basis)
  - position-tagged role binders (the HypE-style augmentation)
  
HARD-PASS for "partial-symmetric motifs are basis-gap" = position-blind ceiling >= 0.15 below position-tagged. HARD-FAIL = within 0.05 (then composition covers it).

## (c) Falsifiable predictions

### Cardinality (Exp-Dev #1)

PRE-REGISTERED HARD-PASS thresholds:
- Bundle-norm-only counting on multisets of size n in [2, 30] yields RMSE > 3.0 at N=1024 and does NOT improve to RMSE <= 1.0 at N=4096 (sqrt-N noise floor, supported by Plate 1995 magnitude analysis).
- "At-least-k" quantifier accuracy with k variable in [1,10] using ONLY {bind, bundle, similarity, cleanup} stays <= 0.60 across dimensions.
- An added primitive (FPE-style or NEF-integrator-style) lifts these by >= 0.20 accuracy and reduces RMSE by >= 2x.

HARD-FAIL conditions:
- Bundle-norm + multi-probe cleanup reaches RMSE <= 1.0 at N=4096 for n in [2,30]. (Would mean count IS a latent capability of bundle, not orthogonal.)
- At-least-k accuracy reaches 0.80 with no added primitive. (Would mean quantifier is composable.)

### Ternary partial-symmetric motif (Exp-Dev #2)

PRE-REGISTERED HARD-PASS:
- Position-blind rank-1 binder ceiling on real-KG ternary partial-symmetric subset >= 0.15 below position-tagged at parameter parity.
- The gap is reproducible across at least 2 of {Freebase n-ary subset, JF17K, WikiPeople}.

HARD-FAIL:
- Gap < 0.05, OR an additive bundle of two position-blind binders (e.g., one for the symmetric pair + one for the asym position) closes the gap to within 0.03. (Would mean partial symmetry is composable from 2 binders, not a basis gap.)

### Element-layer precedent (Skunkworks path)

P_deflated estimate for "DreamCoder-style internal-abstraction in VSA binding-operator space yields a genuinely-new substrate primitive without external oracle": 0.40 (capped under novel-synthesis ceiling 0.50, deflated 0.10 for VSA-specific novelty risk). HARD-PASS: at least one substrate-discovered operator achieves PROVABLY_EQUIVALENT_BY_CAPABILITY status with corr(bundle(a,b),c) AND extends to a 2nd partial-symmetry signature (i.e., reusability beyond the seed). HARD-FAIL: 0 reusable discoveries across 100 abstraction-loop steps.

## (d) Cross-thread synthesis with prior entries

- Composes with substrate DECISION 142 (TIER-2 novel composition existence-proven): cardinality task surface is the natural extension that promotes the existence-proof to a NECESSITY-proof. The 38-op basis bimodality (fully-symmetric or fully-asymmetric) is exactly what makes cardinality interesting — counting needs neither pure symmetry nor pure asymmetry, it needs a magnitude-aware reduction that the binding basis does not provide.
- Refines the gap-driven loop result (2026-06-15) by giving Phase B a literature-grounded basis-gap target rather than a synthetic one. The corr(bundle(a,b),c) composition was substrate-internal evidence; the cardinality literature provides external corroborating structure across 4 author clusters.
- Validates the [[feedback-dont-dismiss-adjacent-methods]] rule: the ternary-motif angle, dispatched as a parallel lit-scan rather than dismissed, surfaced HypE's position-tagging impossibility argument — a genuine secondary basis-gap that would have been missed.
- Reinforces 11th USER-LOCKED rule (substrate standalone capability first): the element-layer precedent finding (DreamCoder/Stitch/Metagol exist; no VSA precedent) means the path to a substrate-internal tier-3 primitive is a genuine first-in-class within VSA/HDC, NOT a derivative of LLM/external supervision.
- Adjacency cascade (Trigger C): the residue-number HDC line (Kymn et al. 2024, arXiv:2311.04872) is a NEW adjacency surfaced today. Should be followed up within 24h as a Tier-1b drill candidate — it is the most explicit "arithmetic-on-top-of-VSA" framing and may give us the cleanest cardinality-primitive design.

## (e) Substrate-product implications

1. **Phase B can be lead-scoped with cardinality as the primary basis-gap-forcing task surface.** The literature supports the architectural claim. The substrate-product positioning gains a 5th independent coordinate: "cardinality/counting requires an added primitive that substrate can DISCOVER vs LLMs which approximate via attention-distribution heuristics."
2. **The element-layer (Skunkworks PATH 1) is genuinely first-in-class for VSA.** Internal-primitive-discovery precedent exists in symbolic program synthesis (DreamCoder, Stitch, Metagol) but NOT in VSA/HDC. This is a defensible substrate-product novelty axis (DECISION 142 architectural-claim-9 extension candidate).
3. **Ternary partial-symmetric motif is the right Phase B secondary.** It probes basis composition cost from a different angle than cardinality (cost-of-composition vs absence-of-primitive). Both arms running in parallel give a 2D scan of basis-gap modes.
4. **The 4-mode distillation taxonomy (V1 atom-removing / V2 structure-adding / refusal / new-primitive) gains a 4th empirical mode if Arm 1 HARD-PASS holds.** Currently 3 modes are operational; a discovered cardinality primitive would establish the 4th.
5. **RISK: cardinality might be "too primitive" (Exp-Dev's adversarial possibility b) — a tier-3 jump that doesn't grow the basis but jumps over it.** This is the highest-risk failure mode. Mitigation: pre-register the C3 internal-abstraction-discovery arm so we measure whether substrate can BUILD the cardinality primitive from compositions + an internal abstraction step, vs needing it injected.

## Adversarial verdict (Question 5)

Adversarial possibilities ranked by plausibility:
- **(a) Composable via bundle-norm + threshold:** PARTIALLY PLAUSIBLE. Bundle-norm gives a sqrt(n)-noisy estimator. Literature pattern (no formal impossibility, only constructive absence) means this is the highest-confidence FAILURE mode for the recommendation. Cheap test (C1 at varying N) directly probes it. P(REFUTES Exp-Dev #1 via this path) = 0.20.
- **(b) Too primitive (tier-3 jump):** PLAUSIBLE. If cardinality is genuinely orthogonal to ALL binding compositions, then substrate cannot discover it from internal abstraction — it must be injected. This still SUPPORTS the basis-orthogonality claim but REFUTES the "growable from element-layer alone" thesis. P = 0.30.
- **(c) Conflates cardinality with retrieval:** LOW. The literature is careful to distinguish retrieval (cleanup, similarity, unbinding) from numerical magnitude (FPE, RNS, integrator). P = 0.10.
- **(d) More decisive families exist:** TRUE in addition, not in substitution. Ternary partial-symmetric motif IS a decisive parallel family; ordering / sets-with-multiplicity / continuity also exist (per VSA literature). P that another family is STRICTLY more decisive than cardinality = 0.25.

## Per-question verdicts

| Q | Verdict | Confidence |
|---|---|---|
| Q1 (cardinality binding-orthogonal in VSA lit) | SUPPORTS Exp-Dev #1 | HIGH |
| Q2 (known VSA cardinality mechanisms exist as added primitives) | SUPPORTS | HIGH |
| Q3 (composable from 5-tuple?) | REFUTES composability (constructive evidence, no formal proof) | MEDIUM-HIGH |
| Q4 (other basis-orthogonal families) | CONDITIONAL — multiple exist (magnitude, ordering, multisets, continuity, RNS-arithmetic); cardinality is representative, not unique | MEDIUM |
| Q5 (adversarial — could be wrong) | CONDITIONAL — main risk is tier-3-jump (b), not composition (a) | MEDIUM |
| Q6 (ternary motif partial-symmetry common + inexpressible) | CONDITIONAL — common YES; inexpressible only for position-blind binders | MEDIUM-HIGH |
| Q7 (internal element-layer precedent without external truth) | SUPPORTS — DreamCoder/Stitch/Metagol exist in symbolic; NO precedent in VSA; first-in-class opportunity | HIGH |

## Overall RECOMMENDATION

**LEAD Phase B with CARDINALITY (Exp-Dev #1) as primary, ternary partial-symmetric motif (Exp-Dev #2) as parallel secondary, internal-abstraction-discovery as orthogonal probe in both arms.**

Rationale:
1. Cardinality has the strongest literature support for basis-orthogonality across 4 independent author clusters.
2. Cardinality is the cleanest test of the "growable basis" thesis: if substrate's internal abstraction can build a cardinality primitive, that is the strongest tier-3 demonstration available; if it cannot, that is the cleanest evidence that an injection is needed (still useful for substrate-product positioning).
3. Ternary motif as parallel arm hedges against the "cardinality is tier-3, jumps over basis" failure mode by probing basis composition cost from a different angle.
4. Element-layer (Skunkworks PATH 1) sits in both arms — it is the substrate's MECHANISM, not a separate task surface.

P_deflated for "Phase B with cardinality lead identifies at least one genuine basis-gap that grows the substrate's expressive power within 1-2 weeks of empirical work" = **0.45** (capped at novel-synthesis 0.50, deflated 0.05 for VSA-specific novelty risk).

## Highest-risk failure mode

The recommendation's highest-risk failure mode is **(b) cardinality is too primitive — genuine tier-3, NOT growable from element-layer composition.** If this holds, substrate cannot discover the cardinality primitive from its 38-op basis via internal abstraction; the task surface forces an externally-injected primitive (which violates the "substrate-on-its-own" thesis). The MITIGATION is to pre-register the internal-abstraction arm and accept that even a HARD-FAIL there is informative: it tells us tier-3 primitives require USER-architectural decision, NOT autonomous discovery. This is fully consistent with DECISION 142's "Tier-3 architecture held for later USER decision" — the Phase B result would simply make that constraint sharper.

## (f) Citations (verified count: 30 distinct paper citations across the three lit-scan sub-agents)

VSA / Cardinality (10):
- Plate 1995 IEEE Trans Neural Networks 6(3):623-641 — HRR foundations, bundle sqrt(n) magnitude
- Plate 2003 CSLI HRR book — canonical reference, no counting primitive
- Kanerva 2009 Cognitive Computation 1(2):139-159 — HDC introduction
- Schlegel, Neubert, Protzel 2022 Artif Intell Rev (arXiv:2001.11797) — 11-VSA comparison; no counting basis op
- Kleyko et al. 2022/2023 ACM Computing Surveys Part I/II (arXiv:2111.06077, 2112.15424) — survey; numerical encoding is separate transformation
- Frady, Kent, Olshausen, Sommer 2020 Neural Computation 32(12) — Resonator Networks 1 & 2
- Komer, Stewart, Voelker, Eliasmith 2019 CogSci — fractional binding / SSPs; continuous magnitude requires new operator
- Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen 2024 Neural Computation 37(1) (arXiv:2311.04872) — residue-number HDC; arithmetic is added layer
- Eliasmith 2013 Oxford — Spaun/SPA; counting via NEF integrator, not HRR binding
- Frady et al. 2022 Neural Computation — "Computing on Functions" / VFA framework

Ternary tensor / motif (12):
- Nickel, Tresp, Kriegel 2011 ICML — RESCAL
- Trouillon et al. 2016 JMLR vol 18 — ComplEx; symmetry/antisymmetry dichotomy is binary
- Balazevic, Allen, Hospedales 2019 EMNLP — TuckER
- Kazemi & Poole 2018 NeurIPS — SimplE
- Wen, Li, Mao, Chen, Zhang 2016 IJCAI — m-TransH; Freebase 61% non-binary statistics
- Fatemi, Taslakian, Vazquez, Poole 2020 IJCAI — HypE; position-blind binders force symmetry
- Liu, Yao, Li 2020 WWW — GETD; full-expressivity n-ary
- Liu, Wang et al. 2021 WWW — RAM role-aware n-ary
- Comon, Golub, Lim, Mourrain 2008 SIAM J Matrix Anal — symmetric tensor rank
- Brachat, Comon, Mourrain, Tsigaridas 2010 Lin Alg Appl + Galuppi et al. 2018 (arXiv:1810.07679) — partial-symmetric tensor decomposition
- Milo et al. 2002 Science — network motifs
- Lee, Ko, Shin 2020 VLDB; Lotito et al. 2022 Comm Phys (Nature); Benson, Gleich, Leskovec 2016 Science — hypergraph / higher-order motifs

Element-layer / library learning (8):
- Ellis et al. 2021 PLDI / Phil Trans Roy Soc A 2023 — DreamCoder
- Bowers, Olausson, Wong, Grand, Tenenbaum, Ellis, Solar-Lezama 2023 POPL — Stitch
- Cropper & Morel 2021 MLJ — Popper ILP predicate invention
- Cropper & Muggleton 2016 — Metagol
- Schmidhuber 2003/2009 arXiv:cs/0309048 — Goedel machines
- Mao, Gan, Kohli, Tenenbaum, Wu 2019 ICLR — NS-CL
- Wong, Ellis, Tenenbaum, Andreas 2021 ICML — LAPS; Grand et al. 2024 ICLR — LILO
- Osipov, Kleyko et al. 2021 IEEE TNNLS (arXiv:2110.08343) — Hyperseed; closest VSA-internal precedent (FIXED binder)

Total verified citations: 30 distinct works across 3 angles.

## Calibration notes (per [[feedback-lit-scan-calibration-penalty]])

- Sub-agent P estimates deflated by 0.15 each.
- Novel-synthesis ceiling 0.50 enforced on the integrated P_deflated = 0.45.
- HARD-PASS and HARD-FAIL thresholds explicit in section (c).
- No formal impossibility theorem found for either cardinality OR partial-symmetric ternary; both are constructive-evidence claims. Honest hedge in HARD-FAIL conditions.

## Next-drill candidate (field-coverage)

**residue-number HDC adjacency** (Kymn et al. 2024) — Tier-1b under nonequilibrium-stat-mech-adjacent / mesoscopic-transport via the arithmetic-as-transmission framing. Should be drilled within 24h to inform the cardinality primitive design (Arm 1, C2 configuration). The RNS-HDC paper gives the cleanest "added arithmetic primitive on top of VSA" recipe in the literature, and may collapse the C2 design from open question to specific recipe.
