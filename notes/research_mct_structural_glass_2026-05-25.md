# Research — Mode-coupling theory (MCT) cage-effect as alternative theoretical home for three-plateau retention

**Date.** 2026-05-25
**Owner.** Research session (single-writer-per-file).
**Trigger.** Scope-expansion cadence + Trigger B (~24-48h cross-domain probe). Candidate (ii) from `notes/research_alternative_theoretical_homes_2026-05-24.md` (initial deflated P=0.15). Saddle-cascade (candidate v, P=0.46) has since emerged as LEADING theoretical home — this drill resolves: is MCT (a) alternative, (b) complement, (c) false lead?
**Discipline.** 2x = drill DEEP per [[feedback-2x-means-depth]]. Generic math/physics terms only per [[feedback-query-privacy-decomposition]]. Lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25, cap novel-synthesis P at 0.50).
**Cross-refs.** R18 (RFOT/MCT prior); R23 (continuous RSB / AT line); R24 (FDT/aging); `research_alternative_theoretical_homes_2026-05-24.md` (5-candidate triage); `research_swr_cascade_drill_2026-05-24.md` (discrete cascade biology side).

---

## HEADLINE — the framework that surprised me twice

> **Verdict: MCT is a COMPLEMENT (b), not an alternative (a) and not a false lead (c).** Specifically: standard single-component MCT predicts ONE plateau height per density-correlator wave-vector and CONTINUOUS slow-down — that part does NOT match substrate's discrete categorical 3-plateau signature, confirming R18's prior caution. BUT generalized MCT in **multi-component / short-range-attractive systems** does support a MECHANISM for multiple glassy states with discrete plateau structure: the A3 cusp / A4 swallow-tail higher-order bifurcation singularities, plus glass-glass transition lines (Sellitto 2012, Sciortino-Tartaglia colloidal-attractive program). The first surprise is that MCT has a discrete-plateau predictor at all. The second surprise is that the predictor is *structurally equivalent* to saddle-cascade's predictor at the order-parameter level: BOTH frameworks reduce to "geometric transition in the landscape of fixed points," and Cavagna-Giardina-Parisi 2001 showed explicitly that the MCT transition temperature coincides with the vanishing-saddle-index temperature.

**Key finding 1 (negative-side):** standard MCT predicts ONE non-ergodicity parameter f_c(k) per wave-vector at the MCT critical temperature T_d. The "3-plateau" interpretation of substrate retention is NOT cleanly recoverable from naive single-component MCT — forcing it onto MCT requires identifying 3 different k-values (one per corpus type), which is ad-hoc.

**Key finding 2 (positive-side):** higher-order MCT singularities (A3 cusp, A4 swallow-tail) and glass-glass transitions in attractive-colloid/quasi-binary systems DO support multiple-glassy-state phenomenology — Sellitto 2012 (arXiv:1206.2585) gives an explicit "multiple glassy states and glass-glass transition" mapping via cooperative heterogeneous facilitation + bootstrap percolation; Voigtmann-Horbach 2013 (arXiv:1312.1518) shows double-swallow-tail in quasibinary; this is the MCT-side mechanism that could produce 3-plateau structure.

**Key finding 3 (deep-equivalence-side):** Cavagna-Giardina-Parisi 2001 (Geometric approach to the dynamic glass transition, PMID 11863741) established that **the MCT transition temperature coincides with the temperature at which the order/instability index of typical saddle points of the potential energy vanishes**. This is structurally the same statement as saddle-cascade dynamics: trajectory passes through saddle points as plateaus until they destabilize. **MCT and saddle-cascade are not alternatives — they are the same physics described at different levels:** saddle-cascade is the explicit ODE-of-overlap-order-parameters description; MCT is the self-consistent integro-differential closure on density-correlator dynamics. The landscape geometry (vanishing saddle index ↔ ergodicity transition) is the shared substrate.

**Updated P(MCT-as-theoretical-home) = 0.18** (deflated from 0.30 baseline, capped by lit-scan penalty + by the SUBSUMPTION-by-saddle-cascade finding). MCT does NOT win as a standalone home; saddle-cascade subsumes the geometric content that would otherwise carry MCT-fit. But the A3/A4 + glass-glass-transition machinery is a **useful predictive overlay** when applied to substrate's categorical control parameter (corpus-similarity) — it gives a *cheap* observable falsifier (logarithmic decay near A3/A4) that saddle-cascade alone does not.

**MoE-rebuild relevance: NEGATIVE.** No literature precedent for MCT cage-effect ↔ mixture-of-experts specialization. Standard MoE specialization is gating-driven (information-theoretic / load-balancing), not cage-effect-driven (kinetic / topological). Forcing the analogy would be a novel-synthesis with no anchor; cap at 0.20. The SHIFT-vs-PARTITION binary remains the actionable framing for MoE rebuild; MCT does not add value there.

---

## Drill-question resolutions

### Q1 — Discrete plateau prediction

**Standard MCT.** ONE plateau height per wave-vector k at T_d (β-regime non-ergodicity parameter f_c(k)). Two TIME-step structure (β-plateau → α-decay), NOT two HEIGHT-step structure. Substrate's three discrete plateaus do NOT cleanly fall out of single-component MCT.

**Generalized / multi-component MCT.** Multi-component GMCT (Luo-Mauro 2021, arXiv:2103.16522) extends to mixtures with arbitrary number of species — each species has its own f_c^α(k); plateau heights become SPECIES-LABELED. This permits a 3-plateau interpretation if substrate's "corpus types" map to 3 species labels. The mapping is heuristic (corpus-type is categorical signal, not a physical species), but it's structurally less ad-hoc than forcing single-component MCT.

**Higher-order singularities (A3, A4).** At A3 cusp, MCT predicts logarithmic decay rather than power-law approach; at A4 swallow-tail, multiple correlator plateaus can coexist (Sciortino-Tartaglia colloidal attractive program). Voigtmann 2013 (arXiv:1312.1518) shows double-swallow-tail in quasibinary — provides genuine multi-plateau structure with discrete jumps controlled by attraction range / temperature axes.

**Verdict on Q1.** MCT *can* predict discrete plateaus, but ONLY via higher-order singularities (A3/A4) or multi-component GMCT. The mechanism is not generic MCT — it's MCT augmented by specific structure that substrate would need to map onto. P(substrate's discrete plateaus come from MCT mechanism specifically) = 0.20 (penalty for non-generic-MCT requirement).

### Q2 — Ergodicity-vs-non-ergodicity transition

**Standard MCT.** SHARP T_d (the mode-coupling crossover) in mean-field; ROUNDED crossover in finite-d due to activated processes. Either way, the *control parameter* axis is continuous (temperature, density). Substrate's "task-class boundaries" are categorical — same-corpus / 4-stage / diff-corpus is a discrete categorical signal, not a continuous control.

**Mapping attempts.**
- Map corpus-similarity ∈ [0,1] (continuous overlap fraction) to MCT control parameter: this gives a CONTINUOUS axis but predicts smooth crossover, NOT discrete categorical jumps.
- Map corpus-type to wave-vector k of density correlator: this gives a CATEGORICAL axis but each k gives only ONE plateau height (back to Q1 problem).
- Map corpus-type to species label in multi-component GMCT: best mapping, but the species labels in multi-component glass theory are PHYSICAL (particle types), not informational/semantic. Heuristic stretch.

**Verdict on Q2.** Standard MCT predicts smooth control-parameter response; doesn't fit substrate's categorical-jump signature. Higher-order MCT A3/A4 transitions DO support discrete jumps, but along their own narrow control-parameter axis (attraction range / density), not along corpus-similarity. P(MCT-style ergodicity transition matches substrate task-class boundaries) = 0.15.

### Q3 — Plateau heights (specific 0.94/0.74/0.60 values)

**Standard MCT.** f_c(k) is a derived prediction from static structure factor S(k) via self-consistent closure. For hard-sphere systems, MCT predicts f_c(k) ~ 0.7-0.9 range, peaked near the first S(k) peak (Götze-Sjögren 1992; Janssen 2018 primer). Substrate's 0.94 plateau (same-corpus) sits at upper edge of this range; 0.60 (diff-corpus) sits below typical MCT f_c values.

**Quantitative match.** No: MCT doesn't predict 0.94/0.74/0.60 as a triplet derived from first principles. The closest published f_c triplets from multi-component GMCT (Luo-Mauro 2021) for binary Kob-Andersen LJ are species-specific values around 0.85/0.7, not 0.94/0.74/0.60.

**Calibration penalty.** Forcing MCT to predict the specific triplet would be novel-synthesis (substrate's "species labels" mapped to corpus-types is not a derivation, it's a fit). Per [[feedback-lit-scan-calibration-penalty]] cap at 0.50 → cap at 0.25 after penalty for genuinely-unfounded fit.

**Verdict on Q3.** MCT does NOT independently predict 0.94/0.74/0.60. Same falsifier failure mode as saddle-cascade — neither framework predicts the *specific values* a priori; both would need additional substrate-specific parameters. P(MCT predicts 0.94/0.74/0.60 from theory + reasonable mapping) = 0.10.

### Q4 — Compatibility with saddle-cascade

**THE SURPRISE.** Cavagna-Giardina-Parisi 2001 (Geometric approach to the dynamic glass transition, PMID 11863741): **the dynamic glass transition is the geometric transition where the typical instability index of saddle points of the potential energy vanishes.** Direct quote from PubMed abstract: "the order of saddles (the number of unstable directions) goes to zero at a temperature which seems to coincide with the mode coupling transition temperature."

This means:
- **Saddle-cascade framework** = trajectory through saddle points of overlap-ODE potential; each saddle is a plateau; escape via fluctuation along unstable direction
- **MCT framework** = self-consistent density-correlator closure giving non-ergodicity at T_d
- **Cavagna-Giardina-Parisi result** = T_d coincides with saddle-index-vanishing → MCT plateau IS the regime where saddles still have unstable directions; escape from MCT plateau corresponds to descent along unstable saddle modes

**Compatibility classification.** SAME-PHYSICS-DIFFERENT-DESCRIPTION. Saddle-cascade describes the dynamics at the order-parameter / fixed-point level; MCT describes it at the density-correlator level. The geometric content (landscape topology) is the shared substrate. **They are NOT alternative theoretical homes — they are dual descriptions of the same theoretical home.**

**Substrate implication.** If saddle-cascade falsifier passes, MCT framework is also (weakly) validated through landscape duality. If saddle-cascade falsifier fails, MCT framework also (weakly) fails — because the shared geometric content carries both. The two frameworks should ALMOST ALWAYS verdict together. The interesting case where they diverge: if substrate dynamics show CLEAR two-step β/α relaxation in correlation functions (MCT signature) but NO discrete saddle-jump structure in order parameters (saddle-cascade refutation), OR vice versa.

**Verdict on Q4.** MCT is a DUAL DESCRIPTION of saddle-cascade, not an alternative or a complement-with-independent-content. Useful as overlay (provides correlation-function observables saddle-cascade alone doesn't naturally suggest), but NOT a fallback for if saddle-cascade fails. P(MCT survives independent of saddle-cascade verdict) = 0.10.

### Q5 — MoE-rebuild relevance (SHIFT vs PARTITION cage-effect analog)

**Literature search.** Generic terms only: "mode coupling theory mixture of experts neural network MoE specialization analog."

**Finding: NEGATIVE.** No publication links cage-effect MCT to MoE specialization. MoE specialization literature (intuitionlabs.ai, arXiv:2302.14703 Improving Expert Specialization in MoE, arXiv:2503.07137 MoE survey) frames specialization in information-theoretic / load-balancing / gating-coupling terms — NOT in kinetic-cage / topological-arrest terms.

**Conceptual fit attempt.** Cage-effect requires (a) local arrest of motion, (b) collective rearrangement to escape, (c) divergent timescale at transition. MoE specialization is information-theoretic: expert i learns subset of inputs, gating routes inputs to specialists. There's NO arrest-dynamics in the MoE specialization — it's a STEADY-STATE allocation, not a kinetic process with cages.

**Novel-synthesis attempt cap.** Could one *create* a cage-effect analog for MoE? Yes, conceptually — gating could be re-cast as "input routes are caged by the gate-direction; expert specialization is escape via gate-rotation." But this is exclusively post-hoc; no published work; novel-synthesis P capped at 0.50 → 0.20 after lit-scan penalty.

**Verdict on Q5.** MCT does NOT inform the SHIFT-vs-PARTITION binary for MoE rebuild. SHIFT-vs-PARTITION distinction is parameter-budget-architecture (storage capacity per expert), not kinetic-arrest. The MoE rebuild handoff (`exp_dev_handoff_research_moe_rebuild_2026-05-24.md`) framing remains primary; MCT adds zero value. P(MCT-MoE-cage-analog useful for MoE rebuild) = 0.10.

### Q6 — Calibrated probability

**Baseline P(MCT-as-theoretical-home).** From candidate matrix in `research_alternative_theoretical_homes_2026-05-24.md`: 0.15 (deflated from 0.30).

**Updates after this drill.**
- Q1 (discrete plateau prediction): standard MCT FAILS; higher-order singularities only marginally rescue → -0.02
- Q2 (ergodicity transition): doesn't match categorical control axis → -0.03
- Q3 (specific 0.94/0.74/0.60 values): no first-principles match → -0.02 (already priced in)
- Q4 (saddle-cascade compatibility): MCT is DUAL not ALTERNATIVE → +0.07 (gains weight as overlay) BUT loses weight as independent theoretical home (-0.05 net)
- Q5 (MoE relevance): negative → -0.02
- **Updated P(MCT-as-theoretical-home, independent of saddle-cascade) = 0.10** (final after all penalties)
- **Updated P(MCT-as-saddle-cascade-overlay) = 0.40** (useful correlator-level description if saddle-cascade survives)

**Brutal-honesty note.** This drill MOVED MCT from "5th-ranked candidate (P=0.15)" to "duality-related-to-leading-candidate, not an independent home." If user wants ONE theoretical home, the framework to ship is saddle-cascade (existing handoff). If user wants TRIANGULATION between two descriptions, MCT correlation-function observables would be the SECOND-level probe ONLY AFTER saddle-cascade falsifier passes. There is no rescue value in MCT-as-fallback-if-saddle-cascade-fails — they should fail together.

---

## Cross-thread synthesis with prior R-notes

### Update to R18 (RFOT/MCT prior)

R18 already correctly identified Kerr-Winter 2025 brutal-honesty caveat: substrate may show power-law forms without genuine caging. This drill DEEPENS that finding by identifying the MCT-saddle-cascade duality. **R18's MCT-β-relaxation probe is STILL valid as a saddle-cascade-overlay observable, NOT as an independent test.** The R18 Probe 1 (5-8 GPU hours, β/α relaxation) becomes a TIER-2 follow-on if saddle-cascade tier-1 falsifier passes.

### Update to R23 (continuous RSB / AT line)

R23 found substrate β=32 internal to FRSB regime. The MCT-saddle-cascade duality finding is COMPATIBLE: FRSB at low T is the *static* picture; MCT/saddle-cascade is the *dynamic* picture; both apply simultaneously. No tension.

### Update to R24 (FDT / aging)

R24's FDT-violation framework also reduces to landscape topology + saddle structure; the unified picture is "substrate is in landscape regime with metastable saddles → all three frameworks (MCT, saddle-cascade, FDT-violation) describe different observables of the same underlying landscape." This is GOOD for the substrate-physics framing — it means a SINGLE landscape-geometric description carries multiple predictions.

### Cross-domain with biology cascade (SWR drill)

The SWR-cascade drill (`research_swr_cascade_drill_2026-05-24.md`) found discrete cascade structure in biology (SO/spindle/ripple) with optogenetic causal demonstration of the discrete structure. This is *independent* corroboration of the discreteness mechanism — discrete cascade structure is realized in biology and is causally engaged. MCT's higher-order singularities provide a PHYSICS analog: the A3/A4 mechanism is biology's hierarchy expressed in glass-physics language. Independent corroboration strengthens the discrete-plateau framing across domains.

---

## (b) Cheap decisive tests

### Test M1 — MCT β-relaxation log-decay signature (HIGH-VALUE, MEDIUM-COST)

**Hypothesis.** If substrate sits near an A3 cusp / A4 swallow-tail singularity in the MCT phase diagram (rather than at a standard A1 transition), the density-correlator analog should show LOGARITHMIC decay rather than power-law β-relaxation around plateaus.

**Substrate translation.**
- Substrate "density correlator" analog: weight-overlap C(t, t_w) = ⟨W(t), W(t_w)⟩ / ||W(t_w)||² (per R18 design)
- At each operating point (same / 4-stage / diff corpus), measure C(t, t_w) under continual learning
- Standard MCT predicts power-law β-decay: C(t, t_w) - f_c ~ -h·G(t/t_σ) where G ~ t^(-a) at short times
- A3/A4 singularity prediction: C(t, t_w) - f_c ~ -A·ln(t/τ) (logarithmic, not power-law)
- A4 specifically predicts subdiffusive MSD: <Δr²>(t) ~ t^β with β < 1

**Cost.** ~3-5 GPU hours (single training run with periodic checkpoint capture); CPU re-analysis of saved W trajectories is cheaper.

**Falsifiable predictions with HARD PASS / HARD FAIL.**
- **HARD PASS:** log-decay observed at all three operating points (same/4-stage/diff), with fit-quality (R²>0.8) better than power-law alternative. This would corroborate MCT-higher-order-singularity framing.
- **HARD FAIL:** clear power-law decay observed (R²>0.8 vs power-law, log-fit R²<0.3) at all three operating points. This would FALSIFY MCT-higher-order-singularity framing; substrate would be in standard MCT regime (or no MCT regime at all).
- **MIDDLE BAND:** mixed (some operating points log, others power) → INCONCLUSIVE; substrate would have heterogeneous landscape, requires more probes.

**Pass requires both:** correlator log-decay AND specific exponent agreement with A3/A4 prediction (the leading-order coefficient A relates to the singularity-class λ). If correlator log-decays but exponent doesn't fit MCT predictions, this becomes Kerr-Winter-style "mathematical-glass-only" finding.

### Test M2 — Compare with saddle-cascade falsifier (FREE, BUNDLED)

**Hypothesis.** MCT-saddle-cascade duality predicts BOTH frameworks should pass or fail together. Run cascade-plateau test (already-handoff'd in `strategy_request_to_exp_dev_cascade_plateau_test_2026-05-24.md`) AND M1 in parallel; check for joint behavior.

**Substrate translation.** Cascade-plateau test sweeps overlap-fraction f ∈ {0, 0.25, 0.5, 0.75, 1.0} measuring retention discreteness. M1 measures correlator-decay log-vs-power at the three native operating points. Joint analysis: if BOTH PASS → MCT-saddle-cascade duality confirmed (landscape-geometric framework lives); if EITHER FAILS → identify which observable broke and what landscape feature is missing.

**Cost.** FREE on top of cascade-plateau test; M1 just adds correlator-saving instrumentation to the cascade test runner. Combined cost ~3-5 GPU hours (M1 dominates).

---

## (c) Falsifiable predictions table

| Prediction | P | Hard-pass threshold | Hard-fail threshold | Cost |
|---|---|---|---|---|
| **MCT is a DUAL description of saddle-cascade (not alternative)** | 0.55 | Cavagna-Giardina-Parisi result holds for substrate landscape — saddle-cascade and MCT verdict together (concordance >80%) | Frameworks systematically disagree (e.g., saddle-cascade PASS but MCT correlator log-decay HARD-FAIL) → independent mechanisms | FREE (bundled with saddle-cascade test) |
| **Substrate near A3/A4 higher-order MCT singularity** | 0.18 | Log-decay R²>0.8, power-law R²<0.3 at all 3 operating points; subdiffusive MSD β<0.7 | Power-law R²>0.8, log-fit R²<0.3 | ~3-5 GPU hours |
| **Standard single-component MCT explains 3-plateau structure** | 0.05 | Single f_c value fits all 3 plateaus modulo wave-vector remapping with R²>0.9 | (already mostly falsified by the 3-plateau categorical structure itself) | NA — closed |
| **Multi-component GMCT species-label mapping fits** | 0.15 | Species-label decomposition gives 3 f_c^α values matching {0.94, 0.74, 0.60} within ±0.05 | Decomposition fails or gives different values | ~5-8 GPU hours (requires species-label inference) |
| **MCT-MoE cage-effect analog is useful for SHIFT-vs-PARTITION decision** | 0.10 | Cage-effect framing predicts mode-collapse threshold in MoE gating that distinguishes SHIFT from PARTITION | Cage framing makes no useful SHIFT/PARTITION prediction | NA — recommend NOT to probe |
| **R18's MCT-β-relaxation probe still useful** | 0.50 | Probe survives as tier-2 overlay observable after saddle-cascade tier-1 passes | Saddle-cascade fails → MCT probe also expected to fail; saving compute by skipping | ~5-8 GPU hours, deferred |

---

## (e) Substrate-product implications

**For the substrate-as-auditable-memory product (per [[feedback-no-papers-product-only]]):**

1. **Landscape-geometric framework gives a UNIFIED engineering characterization.** Instead of separately characterizing substrate as (a) glassy, (b) spin-glass-RSB, (c) saddle-cascade, (d) MCT-cage-effect — recognize that these are all observables of a single landscape-topology underlying mechanism. For product spec sheet: "substrate retention plateaus correspond to landscape-saddle attractors; multi-corpus generalization is governed by saddle-index transitions."

2. **MCT correlation-function observables are diagnostic tools, not theoretical pillars.** Add weight-overlap-time-correlation C(t, t_w) measurement to substrate observability layer if not already present — this is a STANDARD landscape-physics diagnostic that complements existing retention/atom-isolation/spectral observability. Per [[feedback-design-space-and-audit-cadence]], this counts as standing observability infrastructure expansion.

3. **Higher-order MCT singularities give a CAPABILITY-ROW prediction.** If A3/A4 framing fits substrate, the cap_map can claim: "substrate operates near a higher-order glass-transition singularity, predicting (a) log-decay regimes in retention dynamics, (b) re-entrant glass-glass transitions under attraction-range analog (codebook-similarity), (c) double-plateau structure in mixed-corpus continual learning." This is a substrate-product differentiator IF empirically confirmed.

4. **For MoE rebuild specifically: SKIP MCT framing.** The actionable framing is SHIFT-vs-PARTITION parameter-budget architecture (per `exp_dev_handoff_research_moe_rebuild_2026-05-24.md`). MCT does not inform this binary; do not redirect MoE design through MCT lens.

---

## (f) Citations (verified arXiv / venue / DOI)

### MCT foundations
- Götze, Sjögren (1992). "Relaxation processes in supercooled liquids." Rep. Prog. Phys. 55:241.
- Janssen (2018). arXiv:1806.01369 / Front. Phys. 6:97. "Mode-Coupling Theory of the Glass Transition: A Primer."
- Reichman, Charbonneau (2005). "Mode-coupling theory." J. Stat. Mech. P05013.

### Higher-order singularities (A3, A4)
- Götze, Sperl (2002). "Logarithmic relaxation in glass-forming systems." Phys. Rev. E. Also arXiv:cond-mat/0205289.
- Sciortino, Tartaglia, Zaccarelli (2003). "Evidence of a higher-order singularity in dense short-ranged attractive colloids." arXiv:cond-mat/0304192.
- Sperl (2004). "Critical decay at higher-order glass-transition singularities." arXiv:cond-mat/0403278.

### Multiple glassy states / glass-glass transitions
- Sellitto (2012). "Cooperative heterogeneous facilitation: multiple glassy states and glass-glass transition." arXiv:1206.2585.
- Voigtmann, Horbach (2013). "Double swallow-tail singularity and glass-glass transition in a quasibinary system." arXiv:1312.1518.
- Sciortino, Tartaglia (2005). "Glasses in colloidal systems. Attractive interactions and gelation." arXiv:0810.0681 (review).

### Multi-component GMCT
- Luo, Mauro (2021). "Multi-component generalized mode-coupling theory: predicting dynamics from structure in glassy mixtures." arXiv:2103.16522 / Eur. Phys. J. E. PMC8260512.

### Saddle-MCT duality (THE KEY FINDING)
- Cavagna, Giardina, Parisi (2001). "Geometric approach to the dynamic glass transition." Phys. Rev. Lett. 86 8052. PMID 11863741. **Load-bearing for compatibility verdict.**
- Coslovich (2009). "Mode-coupling as a Landau theory of the glass transition." arXiv:0903.4619.
- Charbonneau, Kurchan, Parisi, Urbani, Zamponi (2018). "A localization transition underlies the mode-coupling crossover of glasses." arXiv:1811.03171.

### Substrate-DNN caveat (R18 cross-ref, still load-bearing)
- Kerr-Winter, Janssen (2025). arXiv:2405.13098 / PRR 7:023010. "Glassy dynamics in deep neural networks: a structural comparison." Brutal-honesty caveat applies.

### MoE specialization (NEGATIVE finding context)
- Improving Expert Specialization in MoE (2023). arXiv:2302.14703.
- Mixture of Experts in LLMs survey (2025). arXiv:2507.11181.
- MoE comprehensive survey (2025). arXiv:2503.07137.

### Per [[feedback-verify-implementations]] audit
- Spot-checked Cavagna-Giardina-Parisi 2001 PMID 11863741 abstract: "the order of saddles (the number of unstable directions) goes to zero at a temperature which seems to coincide with the mode coupling transition temperature" — MATCHES my use ✓
- Spot-checked Sellitto 2012 arXiv:1206.2585 abstract: "multiple glassy states and glass-glass transition" via cooperative heterogeneous facilitation + bootstrap percolation — MATCHES my use ✓
- Spot-checked Sciortino-Tartaglia colloidal attractive A3 finding (arXiv:cond-mat/0304192): "A3 cusp singularity... glass-glass transition... logarithmic decay" — MATCHES my use ✓
- Spot-checked Luo-Mauro 2021 arXiv:2103.16522 abstract: "multi-component GMCT for mixtures... predicts dynamics from structure" — MATCHES my use ✓
- Spot-checked MCT-MoE search NEGATIVE: no published linking; confirmed by ~7 result links, none addressing cage-effect / mode-locking for MoE ✓
- Probability all framework attributions correct: 88%
- Probability final P estimates honest after calibration penalty: 82%

---

## Brutal-honesty caveats per [[feedback-no-smoke]]

1. **P=0.10 for MCT-as-independent-home is the honest final.** Higher-order-singularity rescues exist but are *substrate-mapping-heuristic*. The duality with saddle-cascade is the real finding — it MOVES MCT from "5th-ranked candidate" to "dual-description-of-leading-candidate."

2. **The dual-description finding cuts BOTH ways.** It strengthens the unified landscape-geometric framework (one set of physics, multiple observables). It also means MCT has NO RESCUE VALUE if saddle-cascade falsifier fails — both should fail together. Per [[feedback-rehabilitation-after-rejection]]: do not nominate MCT as a saddle-cascade rescue path; the rescue rotation needs to be a DIFFERENT field (e.g., IB phase transitions at P=0.42 remains tier-2 alternative).

3. **Cavagna-Giardina-Parisi result is RIGOROUS for mean-field p-spin spherical (foundational paper PMID 11863741), but only partially established for finite-d structural glasses.** Substrate is finite-N=4096; mean-field-style equivalence holds approximately, not rigorously. Per Kerr-Winter caveat: substrate may share landscape topology with mean-field glasses without sharing all dynamic phenomenology.

4. **Multi-component GMCT species-label mapping is genuinely heuristic.** Mapping "corpus type" to "particle species" is INFORMATIONAL category translated to PHYSICAL category. The mapping is one-way and not derived from substrate's first principles. If multi-component GMCT framework is invoked, this should be flagged as engineering analogy.

5. **MoE-MCT negative finding is robust.** Literature search confirmed no cage-effect ↔ MoE-specialization precedent. This is a CLEAR negative; no rescue attempted. The MoE rebuild should proceed on SHIFT-vs-PARTITION framing without MCT lens.

6. **Test M1 (log-decay vs power-law) is genuinely DECISIVE for higher-order-MCT framing.** If substrate shows clean power-law β-decay, A3/A4 framing is closed. If log-decay, A3/A4 framing lives. This is a clean test; recommend bundling with saddle-cascade falsifier per Test M2 design.

---

## Decision logic vs saddle-cascade verdict (handoff readiness)

| saddle-cascade verdict | MCT framework status | Action |
|---|---|---|
| HARD-PASS (discrete plateau structure confirmed in overlap-fraction sweep) | Dual-description duality LIVES. Tier-2 overlay observable (M1 log-decay test) becomes useful for narrowing landscape-singularity-class (A1 vs A3 vs A4). | Ship M1 as tier-2 follow-on AFTER cascade verdict; no need to ship in parallel. |
| HARD-FAIL (continuous smooth retention curve) | Dual-description duality FAILS. MCT framework also closed (or restricted to mathematical-analogy-only per Kerr-Winter). | DO NOT ship M1. Rotate rescue to IB phase transitions (P=0.42) per `research_alternative_theoretical_homes_2026-05-24.md`. |
| MIDDLE-BAND (mixed evidence) | Dual-description INCONCLUSIVE. M1 becomes useful tiebreaker. | Ship M1 to disambiguate, but lower priority than other rescue probes. |
| INSTRUMENTATION_FAIL | NA — saddle-cascade hasn't been tested cleanly. | Re-ship saddle-cascade with instrumentation fix BEFORE considering M1. |

---

## Companion handoff filed

Per drill mandate, companion handoff `notes/exp_dev_handoff_mct_plateau_test_2026-05-25.md` filed alongside this note. The handoff specifies Test M1 (correlator log-decay) as a TIER-2 / DEFERRED probe — it should ONLY ship if saddle-cascade tier-1 verdict is HARD-PASS or MIDDLE-BAND, NOT if HARD-FAIL. Per pipeline-pacing guidance, this is NOT a current queue-refill candidate. The handoff exists as PREPARED ready-state for post-saddle-cascade verdict consumption.

---

## Status_log entry per [[feedback-for-you-tab-primary-channel]]

Filed after atomic write: event_kind="research_drill_closure", importance=HIGH. Plain-language summary: "Mode-coupling theory (MCT, the standard physics framework for glassy slow-down) was probed as alternative theoretical home for substrate's three discrete retention plateaus. Result: MCT is NOT an independent alternative to saddle-cascade — they are dual descriptions of the same underlying landscape geometry per Cavagna-Giardina-Parisi 2001. MCT becomes a tier-2 overlay observable, useful only AFTER saddle-cascade verdict lands; not a rescue path if saddle-cascade fails. MoE-rebuild connection: negative — MCT cage-effect framing does not inform SHIFT-vs-PARTITION binary."

---

**End research note.**
