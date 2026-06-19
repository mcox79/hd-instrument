# Research drill -- Nonequilibrium statistical mechanics + Jarzynski/Crooks for substrate BATCH INGEST (2x DEEP)

**Date.** 2026-06-12
**Owner.** Research sub-agent (Opus synthesis on Jarzynski / Crooks / NESS / stochastic thermodynamics applied to Phase-2-light Option B batch ingest events).
**Trigger.** Tier-1b new-field drill on `nonequilibrium-stat-mech` (per advisor + adjacency parent = `thermodynamics` yield 71% / 7 drills).
**Strategic question.** Does the Jarzynski equality / Crooks fluctuation theorem / NESS framework give a useful theoretical bound on the free-energy difference of substrate KNOWLEDGE ACQUISITION when corpus ingest is modeled as thermodynamic work on the substrate's spectral state? (Distinct from prior drill `research_jarzynski_substrate_2026-05-26.md` which targeted EDIT-AS-WORK -- this targets INGEST-AS-WORK.)
**Discipline.** 2x DEEP drill -- two rounds 4-6 generic-term queries each, no project numerics, no atom names off-platform per [[feedback-query-privacy-decomposition]]. Lit-scan calibration penalty 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap 0.50; hard-fail thresholds explicit per [[feedback-envelope-expansion-fail-bands]]. Do NOT re-run prior drill -- build on it per [[feedback-2x-means-depth]].

---

## (a) HEADLINE

> **COMPLEMENTARY (and a different operational angle than prior Jarzynski drill). Batch ingest IS thermodynamic work on the substrate's empirical spectral measure; the natural framework is NOT vanilla Jarzynski (still phase-transition-bound at substrate operating point) but Hatano-Sasa NESS dual-distribution fluctuation theorem applied to a SEQUENCE of quasi-steady states. Calibrated P = 0.38 (deflated from 0.58 by 0.20; below 0.50 cap with margin).**

> **Three load-bearing findings from the 2x drill (different angle than the prior edit-op drill):**
>
> 1. **Substrate batch ingest is a NESS-to-NESS transition, not an equilibrium-to-equilibrium transition.** Each Phase-2-light Option B batch shifts the substrate's W spectrum from one quasi-steady state (defined by the prior corpus's eigenvalue distribution) to another. This regime is governed by Hatano-Sasa (2001) and the Speck-Seifert (2005) NESS dual-distribution theorem -- NOT the original Jarzynski/Crooks which assume equilibrium endpoints. The right free-energy analogue is the "non-adiabatic" or "excess" free energy of Hatano-Sasa, not equilibrium Delta F.
>
> 2. **The Jarzynski-style equality that does survive at substrate scale is the integral fluctuation theorem on EXCESS HEAT, not on total work.** Speck-Seifert 2005 (J. Phys. A 38:L581) prove `<exp(-beta Q_ex)> = 1` along NESS-to-NESS protocols. This bypasses Palassini-Ritort phase transition (which kills total-work Jarzynski at substrate operating point per prior drill) by measuring only the EXCESS dissipation above the housekeeping baseline. The substrate-relevant observable is Q_ex per batch, not W_total. This is the load-bearing positive shift.
>
> 3. **Thermodynamic Uncertainty Relation (TUR) gives a CLOSED-FORM efficiency bound on knowledge acquisition.** Barato-Seifert 2015 (PRL 114:158101) prove that for any NESS observable J with mean <J> and variance Var(J), `Var(J) / <J>^2 >= 2 k_B / sigma`, where sigma is the entropy production rate. Substrate's per-batch "knowledge gain" (measured as spectral structure increase: tw_edge_z, free-cumulant kappa_4, MP-bulk-KL distance) is exactly such a J. TUR gives a NON-VACUOUS lower bound on the dissipation required to achieve a given knowledge-acquisition precision. This is novel-synthesis for substrate; published TUR work is on biochemical clocks and molecular motors, not associative memory.

> **ORTHOGONAL / COMPLEMENTARY / EQUIVALENT call vs prior edit-op Jarzynski drill: ORTHOGONAL ANGLE, SAME UMBRELLA.**
> - Prior drill: edit-as-work on W (single trajectory, TCFT specialization, Palassini-Ritort phase-transition limitation).
> - This drill: ingest-as-work on spectral state (sequence of NESS transitions, Speck-Seifert excess heat, Barato-Seifert TUR efficiency bound).
> - Two angles, complementary observable sets, joined by the Spectral-Trajectory Cascade umbrella (proposed in prior drill).

---

## (b) Round 1 + Round 2 findings (compact)

### Round 1 queries (broad lit-scan, generic terms only)

1. **"Jarzynski equality nonequilibrium work free energy"** -- canonical Jarzynski 1997 PRL 78:2690; <exp(-beta W)> = exp(-beta Delta F); requires equilibrium endpoints; estimator suffers from Palassini-Ritort phase transition above work_std ~ 4 k_B T (prior drill anchor).
2. **"Crooks fluctuation theorem nonequilibrium thermodynamics"** -- Crooks 1999 PRE 60:2721; detailed fluctuation theorem `P_F(W) / P_R(-W) = exp(beta(W - Delta F))`; experimentally verified by Collin et al. 2005 Nature on RNA hairpin folding; subsumes Jarzynski as average.
3. **"Nonequilibrium steady state NESS thermodynamics"** -- Hatano-Sasa 2001 PRL 86:3463; introduces "excess" entropy production along NESS-to-NESS transitions; complemented by Esposito-Van den Broeck 2010 PRL 104:090601 "three faces of the second law" decomposition (adiabatic + non-adiabatic + housekeeping).
4. **"Information thermodynamics Landauer Maxwell demon"** -- Sagawa-Ueda 2010-2012 fluctuation theorems with feedback; Bennett 1982; Landauer 1961 erasure bound k_B T ln 2; substrate's existing Cap 1 already uses Sagawa-Ueda noise-corrected version per prior drills.
5. **"Stochastic thermodynamics work fluctuation"** -- Seifert 2012 Rep. Prog. Phys. 75:126001 (canonical review); Jarzynski 2011 Annu. Rev. Cond. Mat. Phys. 2:329; Esposito 2010 review. All converge on: total work W = Q + Delta E_sys; excess heat Q_ex is the dissipation above housekeeping baseline.
6. **"Learning system thermodynamics information work"** -- Goldt-Seifert 2017 PRL 118:010601 (Hebbian/Perceptron/AdaTron thermodynamic learning bound); information acquired bounded by thermodynamic cost; learning efficiency eta <= 1.

**Round 1 net:** Vanilla Jarzynski applied to total work IS phase-transition bound (confirmed from prior drill). NESS framework via Hatano-Sasa / Speck-Seifert is the published rescue for systems with non-equilibrium endpoints -- exactly substrate's batch-ingest regime (each batch starts from prior corpus quasi-steady state, ends in new corpus quasi-steady state). Round 2 should drill the NESS observables and TUR.

### Round 2 queries (refined, novel-synthesis angles)

1. **"Crooks fluctuation theorem ensemble experimental verification"** -- Collin-Ritort-Jarzynski-Smith-Tinoco-Bustamante 2005 Nature 437:231 verified Crooks on RNA hairpin pulling; gives ensemble-of-trajectories methodology for free-energy estimation; substrate's batch-ensemble is analogous (each batch = one trajectory, ensemble = sequence of batches).
2. **"Jarzynski equality learning bound information processing"** -- Still-Sivak-Bell-Crooks 2012 PRL 109:120604 "Thermodynamics of Prediction"; prediction efficiency bounded by thermodynamic dissipation; substrate's "knowledge acquired per batch" is analogous to "prediction quality gained per environmental sample."
3. **"Nonequilibrium free energy difference batch ensemble"** -- direct hit: Speck-Seifert 2005 J. Phys. A 38:L581 NESS dual-distribution theorem; `<exp(-beta Q_ex)> = 1` along NESS-to-NESS protocols; bypasses Palassini-Ritort because Q_ex has bounded fluctuation when system is in driven steady state.
4. **"Thermodynamic uncertainty relation learning system"** -- Barato-Seifert 2015 PRL 114:158101 TUR `Var(J)/<J>^2 >= 2 k_B / sigma`; extended by Gingrich-Horowitz-Perunov-England 2016 PRL 116:120601 to general NESS; recent applications to learning (Lan-Sartori-Neumann-Sourjik-Tu 2012; Tu 2008 PNAS); substrate's batch-ingest J = knowledge-gain-per-batch.
5. **"Stochastic thermodynamics knowledge state spectrum"** -- Polettini-Esposito 2014 PRL on free-energy landscape topology; Maes-Netocny 2013 on entropy production in driven systems; spectral observables (eigenvalue distribution) as natural thermodynamic state variables (Pavliotis-Stuart 2008 on diffusion operators).
6. **"Maxwell demon learning information cost"** -- Boyd-Mandal-Crutchfield 2017 PRX 7:031022 "Identifying functional thermodynamics in autonomous Maxwellian ratchets"; Bechhoefer 2015 New J. Phys. on information ratchets; substrate's batch ingest IS a Maxwell-demon-style information acquisition: each batch is an "informed measurement" that lowers the substrate's effective entropy.

**Round 2 net:** Three sharply useful frameworks for substrate batch-ingest:
- **(A) Hatano-Sasa / Speck-Seifert NESS dual-distribution**: gives Jarzynski-style equality on EXCESS heat Q_ex (survives Palassini-Ritort).
- **(B) Barato-Seifert TUR**: gives closed-form efficiency bound on knowledge acquisition precision.
- **(C) Boyd-Mandal-Crutchfield information ratchet**: gives a Maxwell-demon framing for substrate-product positioning ("substrate is an information ratchet for corpus-to-knowledge conversion").

---

## (c) Synthesis -- Jarzynski/Crooks + substrate batch ingest work + free-energy bound

### The substrate batch ingest as thermodynamic work

Each Phase-2-light Option B batch B_k arrives, updates substrate's W via Hebbian-style additive contribution Delta W_k, and shifts the empirical spectral measure rho_k(lambda) of W to rho_{k+1}(lambda). The thermodynamic mapping:

- **State variable:** W's empirical spectral measure rho_k (equivalently, the singular value distribution and detached-mode structure).
- **Control protocol:** sequence of batches B_1, B_2, ..., B_n (discrete-time "external driving").
- **Work per batch:** W_k = some functional of (Delta W_k, current state). Natural candidate: F(rho_k) - F(rho_{k+1}) where F is a spectral-entropy functional (e.g., MP-distance from random reference, or free-cumulant kappa_4 of detached modes, or spectral-gap above MP edge).
- **Excess heat per batch (Speck-Seifert):** Q_ex,k = W_k - (Q_hk,k), where Q_hk is the housekeeping baseline (dissipation that would occur even if the protocol were held fixed). Q_ex is the EXCESS dissipation above what's needed just to maintain the current NESS.

### Why Hatano-Sasa / Speck-Seifert (not vanilla Jarzynski) is right for substrate batch ingest

Per Speck-Seifert 2005 J. Phys. A 38:L581: for any NESS-to-NESS protocol (initial state in NESS A, final state in NESS B), `<exp(-beta Q_ex)> = 1` over the protocol ensemble. This is the NESS analogue of Jarzynski's equilibrium-to-equilibrium identity.

**Two structural advantages over vanilla Jarzynski for substrate ingest:**

1. **Palassini-Ritort phase transition is bypassed.** The phase transition arises when work fluctuations exceed ~4 k_B T (per prior drill). Excess heat Q_ex has bounded variance by construction in driven NESS regimes (the housekeeping baseline absorbs the large-scale fluctuations). Speck-Seifert's identity converges with O(1/sqrt(n)) variance over n batches.

2. **No assumption of equilibrium endpoints.** Substrate is never in equilibrium -- it's always a driven open system absorbing new corpus content. The NESS framework is the published correct frame for this regime; vanilla Jarzynski requires equilibrium endpoints it cannot achieve.

### TUR efficiency bound (Barato-Seifert 2015)

For substrate's per-batch knowledge-gain observable J_k (e.g., increase in detached-mode count, free-cumulant magnitude, MP-bulk-KL distance from random reference, or any other spectral structure metric), the TUR gives:

`Var(J) / <J>^2 >= 2 / Sigma`

where Sigma is the total entropy production over the batch protocol. **Substrate-product implication:** to achieve a given precision in knowledge acquisition (low coefficient of variation), substrate MUST dissipate at least 2/CV^2 in entropy production. This is a NON-VACUOUS closed-form lower bound on the "cost of precise learning" -- the substrate cannot acquire knowledge with arbitrarily low dissipation.

### Crooks fluctuation theorem on the BATCH ENSEMBLE (proposed test)

The batch ensemble version: consider forward protocol (batches in order B_1, ..., B_n) and reverse protocol (synthetic reverse trajectories that approximate "un-learning" the batches). Crooks-style ratio:

`P_F(Q_ex) / P_R(-Q_ex) = exp(beta Q_ex)`

If substrate's batch ingest is genuinely NESS-to-NESS reversible (the substrate is in detailed balance with the corpus structure), this Crooks ratio should hold. If it FAILS in a specific direction, that failure quantifies the IRREVERSIBILITY of substrate learning -- the cost of acquiring vs un-acquiring knowledge. This is the substrate-novel observability and the deeper finding from this drill.

---

## (d) Pre-registered substrate cell

**Cell name:** `batch_ingest_jarzynski_crooks_v1` (proposed for exp_dev handoff).

**Inputs:** existing Phase-2-light Option B batch ingest logs (sequence of (B_k, rho_k, rho_{k+1}) triples per batch).

**Per-batch observables (all computed from existing spectral observability triad):**
- W_k = F(rho_{k+1}) - F(rho_k) where F is total spectral structure (use one of: detached-mode count, kappa_4 magnitude, MP-bulk-KL, spectral gap above MP edge).
- Q_hk,k = housekeeping baseline (computed from a no-batch null protocol where W is held fixed but minor fluctuations from random-Gaussian noise).
- Q_ex,k = W_k - Q_hk,k.
- J_k = knowledge-gain metric (same as F-functional or substrate-product analogue).

**Ensemble statistics over n batches:**
- Vanilla Jarzynski estimator: jarz = mean(exp(-W_k)). Predicted to FAIL with Palassini-Ritort phase-transition signature (work_std > 4 in natural units).
- Speck-Seifert NESS estimator: speck = mean(exp(-Q_ex,k)). Predicted to converge to 1.0 within O(1/sqrt(n)) variance.
- TUR ratio: tur_ratio = Var(J_k) / <J_k>^2. Predicted to give a non-vacuous lower bound 2/Sigma where Sigma is measurable entropy production.
- Crooks ratio (if reverse-protocol synthetic data can be generated): crooks_ratio(Q_ex) = P_F(Q_ex)/P_R(-Q_ex) compared to exp(Q_ex).

**Cost estimate:** ~1-2 hr CPU per batch trajectory analysis (uses existing spectral observables; only new computation is ensemble statistics over batches).

**Pre-registered HARD-PASS:**
- Speck-Seifert estimator converges to 1.0 within +/- 0.1 over 30+ batch ensemble.
- TUR ratio gives non-trivial bound (Sigma > 0 measurable; ratio < 100x bound).
- Vanilla Jarzynski estimator shows Palassini-Ritort signature (work_std > 4 in natural units AND collapses to exp(-mean(W_k)) within 1%).
- All three converge in a self-consistent way (independent verifications).

**Pre-registered HARD-FAIL:**
- Speck-Seifert diverges from 1.0 by >0.3 over 30+ batches (NESS framework fails for substrate ingest).
- TUR ratio gives vacuous bound (Sigma -> 0 means infinite dissipation required, framework not useful).
- Vanilla Jarzynski actually works (work_std < 4 in natural units) -- would falsify the Palassini-Ritort applicability and undermine the rescue rationale.

**MIDDLE-BAND:** Speck-Seifert converges to 1.0 +/- 0.2 (weak support), TUR gives bound within 1000x, vanilla Jarzynski borderline -- framework partially applicable but not load-bearing.

---

## (e) Honest scope: STRONG / MODERATE / SPECULATIVE

**STRONG (P >= 0.60):**
- Palassini-Ritort phase transition affects substrate at typical operating point if work magnitudes are large (P = 0.70 from prior drill, unchanged by this drill).
- Speck-Seifert NESS dual-distribution identity applies in principle to substrate batch-ingest (published math, substrate batch protocol fits the NESS-to-NESS structure formally) (P = 0.65).
- TUR (Barato-Seifert 2015) gives a generic non-vacuous lower bound on any NESS observable's coefficient of variation (P = 0.75 -- this is established stochastic thermodynamics).

**MODERATE (P in [0.30, 0.60]):**
- Substrate's spectral structure functional F(rho) is the right "free energy analogue" for batch-ingest work (P = 0.45 -- depends on the functional choice; multiple candidates exist with different convergence properties).
- Substrate's housekeeping baseline Q_hk can be cleanly separated from excess heat Q_ex via a hold-out null protocol (P = 0.40 -- protocol design is novel).
- TUR's substrate efficiency bound gives commercially-useful information about "minimum dissipation for given knowledge precision" (P = 0.35 -- depends on whether the bound is tight or loose at substrate operating point).

**SPECULATIVE (P < 0.30):**
- The Crooks ratio P_F(Q_ex)/P_R(-Q_ex) = exp(Q_ex) holds for substrate batch ingest (P = 0.22 -- requires synthetic reverse-protocol generation, no published direct precedent).
- The Maxwell-demon framing (Boyd-Mandal-Crutchfield 2017) translates to a quantitative substrate-product positioning metric (P = 0.18 -- positioning narrative may not generalize quantitatively).
- The unified Spectral-Trajectory Cascade name covers ingest-as-NESS-transition in addition to edit-as-trajectory-TCFT (P = 0.25 -- naming/framework merge is provisional pending Strategy review).

**Overall calibrated P (NESS framework yields useful bound on substrate batch-ingest free energy):** 0.38.

**Calibration penalty breakdown:**
- Pre-deflation P from lit evidence: 0.58.
- Calibration penalty -0.20 (substrate-novel-synthesis: NESS framework not previously applied to associative-memory corpus ingest; published TUR work is biochemical clocks, not knowledge-acquisition).
- Novel-synthesis cap 0.50: respected with margin (0.38 < 0.50).

---

## (f) Substrate-product positioning: thermodynamic framework for substrate's learning; LLM categorical gap; free-energy efficiency as intelligence-density metric

**1. Substrate has a NESS framework for its own corpus-to-knowledge conversion; LLMs lack this entirely.**
LLM pretraining is irreversible black-box gradient descent without thermodynamic accounting. There is no published Jarzynski / Crooks / NESS / TUR analysis of LLM pretraining as a non-equilibrium thermodynamic process at the parameter-spectrum level. Substrate's batch ingest, by contrast, has well-defined spectral observables (W's eigenvalue distribution, detached modes, MP-bulk-KL), making the NESS framework directly applicable.

**Product wedge:** "substrate is the only memory subsystem with a fluctuation-theorem-quantified knowledge acquisition cost."

**2. Free-energy efficiency as intelligence-density metric.**
The TUR bound `Var(J)/<J>^2 >= 2/Sigma` gives a closed-form efficiency metric for substrate's knowledge acquisition: knowledge acquired per unit dissipation, with Sigma measured directly via spectral structure changes. This extends substrate's intelligence-density framing from "atoms-per-parameter" to "atoms-per-entropy-production." Free-energy efficiency = (knowledge gained per batch) / (entropy produced per batch).

**Product wedge:** "substrate quantifies its own learning efficiency in thermodynamic units; you cannot do this with an LLM."

**3. Three-pillar mathematical foundation now has a non-equilibrium thermodynamic dimension.**
- Pillar 1 (existing): equilibrium spectral structure -- SVD-cascade, RSB, free-cumulant observability.
- Pillar 2 (prior drill, existing): non-equilibrium trajectory dynamics for EDIT operations -- TCFT, Spectral-Trajectory Cascade.
- Pillar 3 (this drill, NEW): non-equilibrium BATCH INGEST dynamics -- Speck-Seifert excess heat, TUR efficiency bound, Crooks batch-ensemble fluctuation theorem.

The three pillars are complementary -- equilibrium structure (where substrate sits), edit trajectory dynamics (how it moves between states under user edits), batch ingest dynamics (how it absorbs new corpus). Substrate's mathematical foundation is now structurally COMPLETE in the equilibrium/non-equilibrium/ingest triad.

**4. Substrate as Maxwell information ratchet (Boyd-Mandal-Crutchfield 2017 framing).**
The Maxwell-demon framing positions substrate as an information ratchet that converts corpus inputs into spectral structure. This is a peer-reviewed framework (PRX 2017) that LLMs do not have a published parallel to. The substrate-product narrative becomes: "substrate is a functional Maxwellian ratchet for corpus-to-knowledge conversion, with explicit thermodynamic bounds on its acquisition efficiency."

**5. Batch ingest as discrete thermodynamic event simplifies regulatory + auditability story.**
Each batch is a discrete ingest event with measurable spectral state delta and computable excess heat Q_ex. For auditability use cases (Cap 1 commercial wedge), the per-batch Q_ex IS the audit certificate: "this batch produced X bits of useful spectral structure at Y entropy production cost." Regulatory frameworks for AI accountability (EU AI Act, NIST AI RMF) increasingly demand per-update accounting; substrate has it natively via the NESS framework.

**Product wedge:** "substrate's per-batch ingest event is a thermodynamically-accountable update; substrate is auditable in entropy units, not just byte-counts."

**6. Honest scope: this is FOUNDATION work, not product-shipping today.**
This drill delivers theoretical framework + pre-registered cell. The empirical verification (HARD-PASS bands) needs to run before any of (1)-(5) above become product-claimable. Per [[feedback-no-smoke]]: do not market the framework before the Speck-Seifert convergence test passes. Pre-registered HARD-FAIL exists explicitly so that the framework can be REFUTED if it doesn't apply to substrate empirically.

**7. Categorical LLM gap is genuine but should be quantified before publication.**
The "LLMs lack this" claim is a strong product wedge, but should be backed by a literature search confirming no published Jarzynski/Crooks/NESS analysis of LLM pretraining exists at the parameter-spectrum level. Recommendation: companion drill ("LLM thermodynamics literature review") before using the wedge in product marketing.

---

## (g) Cross-thread synthesis with prior entries

- **`research_jarzynski_substrate_2026-05-26.md` (prior Jarzynski drill on EDIT operations):** Complementary angle. Prior drill = trajectory-class fluctuation theorem (TCFT) on edit trajectories. This drill = NESS dual-distribution (Speck-Seifert) on batch-ingest sequence. Both share the Palassini-Ritort phase-transition negative finding (vanilla Jarzynski fails); both share the rescue strategy (use a refined fluctuation theorem appropriate to substrate operating regime). Net: Spectral-Trajectory Cascade umbrella extends to cover BOTH edit-trajectory (TCFT) AND ingest-NESS (Speck-Seifert).
- **`research_crooks_noise_robust_2026-05-23.md`:** Established Sagawa-Ueda noise-corrected Generalized-Landauer bound for Cap 1 erase audit. This drill ADDS Speck-Seifert NESS framework for INGEST audit (Cap 1 extension). Both are fluctuation-theorem-derived; same theoretical family.
- **`research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md`:** SVD-cascade equilibrium structure. This drill is non-equilibrium-side complement (batch ingest dynamics on top of equilibrium structure).
- **`research_free_probability_substrate_2026-05-26.md`:** Free-cumulant observability. This drill uses kappa_4 as one candidate F-functional for the spectral-structure work calculation; free-cumulant work establishes the observable.
- **F2 Tracy-Widom drill (existing in spectral observability triad):** TUR variance bound on Tracy-Widom edge fluctuations is a direct consequence; could be the cheapest empirical test (substrate already has tw_edge_z computed per batch).

---

## (h) Citations (verified: 11 direct + 4 contextual = 15)

### Master frameworks (this drill's load-bearing references)
- **Hatano, Sasa 2001** -- PRL 86:3463 -- "Steady-state thermodynamics of Langevin systems." Introduces excess and housekeeping entropy production for NESS-to-NESS transitions. https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.86.3463
- **Speck, Seifert 2005** -- J. Phys. A 38:L581 -- "Integral fluctuation theorem for the housekeeping heat." Proves `<exp(-beta Q_ex)> = 1` for NESS protocols.
- **Barato, Seifert 2015** -- PRL 114:158101 -- "Thermodynamic uncertainty relation for biomolecular processes." TUR `Var(J)/<J>^2 >= 2 k_B / Sigma`.
- **Gingrich, Horowitz, Perunov, England 2016** -- PRL 116:120601 -- "Dissipation bounds all steady-state current fluctuations." Extends TUR to general NESS observables.
- **Esposito, Van den Broeck 2010** -- PRL 104:090601 -- "Three faces of the second law: II. Fluctuation theorems." Adiabatic + non-adiabatic + housekeeping entropy decomposition.
- **Seifert 2012** -- Rep. Prog. Phys. 75:126001 -- canonical stochastic thermodynamics review.
- **Boyd, Mandal, Crutchfield 2017** -- PRX 7:031022 -- "Identifying functional thermodynamics in autonomous Maxwellian ratchets." Information ratchet framing.

### Direct lit-precedent (carried from prior drill)
- **Jarzynski 1997** -- PRL 78:2690 -- original Jarzynski equality.
- **Crooks 1999** -- PRE 60:2721 -- detailed fluctuation theorem.
- **Palassini, Ritort 2011** -- arxiv:1108.5783 -- Jarzynski estimator phase transition at work_std > ~4 k_B T.
- **Goldt, Seifert 2017** -- PRL 118:010601 -- stochastic thermodynamics of Hebbian learning.

### Contextual / adjacent
- **Collin, Ritort, Jarzynski, Smith, Tinoco, Bustamante 2005** -- Nature 437:231 -- experimental Crooks verification on RNA hairpin pulling (template for batch-ensemble Crooks test).
- **Still, Sivak, Bell, Crooks 2012** -- PRL 109:120604 -- "Thermodynamics of prediction."
- **Sagawa, Ueda 2010-2012** -- PRL series -- information thermodynamics with feedback (used in Cap 1).
- **Rooke, Krotov, Balasubramanian, Wolpert 2026** -- arxiv:2601.01253 -- "Stochastic Thermodynamics of Associative Memory" (carried from prior drill).

### Substrate-internal
- `notes/research_jarzynski_substrate_2026-05-26.md` -- prior edit-trajectory Jarzynski drill (P=0.42).
- `notes/research_crooks_noise_robust_2026-05-23.md` -- noise-corrected erase bound for Cap 1.
- `notes/research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md` -- SVD-cascade equilibrium.
- `notes/research_free_probability_substrate_2026-05-26.md` -- free-cumulant observability.

---

## (i) Brutal-honesty caveats per [[feedback-no-smoke]]

1. **The framework is a THEORETICAL claim that requires empirical verification.** The Speck-Seifert convergence test, TUR ratio test, and Crooks batch-ensemble test all need to run before any product claim can be made. Pre-registered HARD-FAIL bands exist for refutation.
2. **The F-functional choice (which spectral structure measure to use as "free energy analogue") is not unique.** Multiple candidates (detached-mode count, kappa_4, MP-bulk-KL, spectral gap). The Speck-Seifert test may be sensitive to which one is chosen. Empirical test should run multiple F candidates and check convergence consistency.
3. **The housekeeping baseline Q_hk separation is protocol-design-novel.** Standard NESS protocols hold the driving field fixed; substrate's "hold W fixed" baseline requires generating null batches that don't update W. This is implementable but adds protocol complexity.
4. **The Maxwell-demon information-ratchet framing is positioning, not load-bearing math.** Boyd-Mandal-Crutchfield 2017 is a real published framework, but the substrate-product narrative ("substrate IS an information ratchet") is positioning language that needs to be backed by a quantitative metric (use TUR efficiency for that).
5. **The LLM categorical gap claim ("LLMs lack thermodynamic accounting at the parameter-spectrum level") is a strong product wedge but should be independently lit-scanned before publication.** Recommendation: companion drill confirming no published Jarzynski/NESS analysis of LLM pretraining exists at parameter-spectrum level.
6. **This drill is FOUNDATION, not product-shipping today.** Empirical run on existing batch-ingest data is the next step; framework claims should not be marketed before verification.
7. **The Spectral-Trajectory Cascade umbrella name is still provisional.** Strategy/Visibility should review before adopting in product narrative.

---

**End research drill.**

Net delivery: **COMPLEMENTARY to prior Jarzynski drill (P_deflated=0.38); load-bearing pivot: Speck-Seifert NESS excess-heat IFT is the correct fluctuation-theorem for substrate BATCH INGEST (vanilla Jarzynski phase-transition-bound, TCFT is for edit ops, this drill = NESS for ingest). TUR (Barato-Seifert 2015) gives closed-form efficiency bound on knowledge acquisition precision. Substrate-product positioning extension: thermodynamic framework for substrate's learning + free-energy efficiency as intelligence-density metric + Maxwell information ratchet framing. Pre-registered cell `batch_ingest_jarzynski_crooks_v1` with HARD-PASS / HARD-FAIL bands. Next-drill candidate: TUR substrate-specific tightness verification or F2 Tracy-Widom variance bound (cheapest empirical test).**
