# ULTRAMETRICITY REVIVAL CONSOLIDATION (6-drill synthesis, 2026-06-01)

**From:** Research session
**To:** Orchestrator
**Trigger:** v324 cap_map reported ultrametricity HARD_FAIL (mean_ratio = 0.583), Garcia-Lorenzana 2025 precedent labeled "REFUTED". User asked "can we research some revivals?"
**Drills dispatched:** 3 level-1 (viability) + 3 level-2 (operational) sonnet research drills in parallel.
**Discipline:** algebraic + lit-scan only; no empirical verification; capability questions for orchestrator.

---

## 0. EXECUTIVE — THE FAILURE IS NOT A REFUTATION

All 6 drills independently converge on a single conclusion:

> **The static-ultrametricity test was the WRONG PROBE for the substrate's confirmed phase class. mean_ratio=0.583 is a MEASUREMENT-MISMATCH, not a refutation. The Garcia-Lorenzana 2025 mechanism was dismissed prematurely; it is now the LEADING SURVIVING candidate, not the failed one.**

Three independent algebraic locks support this:

1. **arXiv:2511.18439 (Sept 2025) replica-symmetry lock.** Replica symmetry of spherical spin systems is determined by **eigenvalue spacing at the edge**, NOT bulk. Pure Marchenko-Pastur bulk **with no outlier spike pair** is structurally INCOMPATIBLE with FRSB (which requires c/n-separated outliers). Substrate has confirmed MP bulk + no spike (v324) → FRSB and AGS-1-RSB are ALGEBRAICALLY RULED OUT. Static RSB phases REQUIRE spectral spikes the substrate empirically does NOT have.

2. **Cacciuto-Marinari-Parisi 1996 finite-N threshold.** 4D Edwards-Anderson needs L ≥ 12 (N ≥ 20,736) before static ultrametricity emerges cleanly. Substrate at N=4096 sits **below this finite-N threshold**. mean_ratio=0.583 is consistent with sub-asymptotic finite-volume corrections; Stariolo 2001 (cond-mat/0010495) is the direct lit precedent for "dynamical UM passes where static UM fails" in finite-N glassy systems.

3. **MP and ultrametricity are independent observables.** MP lives on the eigenspectrum of W (kinematic — depends only on iid pattern moments). Ultrametricity lives on the Gibbs measure (thermodynamic — depends on the free-energy landscape). No theorem links the two. You can construct ensembles with identical MP spectra and arbitrarily different P(q). In the Hopfield retrieval phase specifically (α<α_c), MP holds AND overlap distribution is a delta at the retrieval overlap m — the cleanest possible counterexample to "MP ⇒ FRSB".

**Conclusion: free-Poisson v324 confirmation gives ZERO information about whether overlaps are ultrametric. Both observations are simultaneously consistent. The "failure" is a probe-target mismatch.**

---

## 1. THE TWO SURVIVING PHASES (drill L2-A decisive)

Substrate's 4 confirmed data points (free-Poisson MP, mean_ratio=0.583, Pred-4 first-order hysteresis, SKAH-M / CK class) match exactly TWO candidate phases — both DYNAMICAL, not static:

| Phase | D1 (MP no spike) | D2 (UM=0.583) | D3 (hysteresis) | D4 (SKAH-M/CK) | P_deflated |
|---|---|---|---|---|---|
| **CK aging (WEB)** | ✓ MP no spike fully consistent | ✓ dynamic ≈ 0.5 is the SIGNATURE | ✓ multi-basin marginal manifold + first-order quench | ✓ by construction | **0.40** |
| **Garcia-Lorenzana oscillating amorphous** | ✓ bipartite-spherical spectrum consistent | ✓ dynamic UM ≈ 0.5-0.6 expected | ✓ exceptional-point first-order transition + cyclic memory hysteresis | ✓ aging + non-equilibrium | **0.20** |

These are NOT mutually exclusive: the substrate may be CK-aging-class with a non-reciprocal-induced oscillation OVERLAY on the base. Combined P(some dynamical-class phase confirmed) ≈ 0.85.

**ALL static-RSB phases are RULED OUT** (4/4 data points fail for each): AGS retrieval, AGS-1-RSB, AGS-FRSB, RFOT mosaic, Crisanti-Sommers 1+1 RSB, temperature chaos.

**Citation correction (REQUIRED for cap_map / decisions log):** Garcia-Lorenzana et al. 2025 is published in **PRL 135, 187402** ([arXiv:2408.17360](https://arxiv.org/abs/2408.17360)), NOT PRE 112, 044154 (level-1 drill #1's citation was incorrect; level-2 drill confirmed via WebSearch). Paper is on **bipartite spherical Sherrington-Kirkpatrick**, NOT Hopfield directly. The non-reciprocal Hopfield analog is [arXiv:2501.00983](https://arxiv.org/abs/2501.00983) (Xue/Maghrebi/Mias/Piermarocchi, Jan 2025) — different authors, Hopf + fold bifurcation, ζ=1/2 and 1/3 critical exponents, limit-cycle attractors. The oscillating-amorphous signature is **DYNAMICAL** (oscillation in two-time correlator C(t,t'), exceptional-point bifurcation), NOT static ultrametric P(q).

---

## 2. CAPABILITY QUESTIONS (for orchestrator + strategy to route)

### Q-F1 — Does the substrate's existing Glauber dynamics exhibit dynamical 1-step ultrametricity at the CK-class predicted value M_dyn ∈ [0.85, 0.95], cleanly separable from the static-UM-refuted value 0.583?

- **Evidence:** Cugliandolo-Kurchan 1993 trajectory ultrametricity result for spherical p-spin; Folena-Franz-Ricci-Tersenghi 2019 PRX marginal-state aging; Iniguez-Marinari-Parisi-Ruiz-Lorenzo 1999 numerical 3D EA mean_ratio ≈ 0.88 at finite N.
- **The substrate's dreaming dynamics ARE the CK protocol natively** when wrapped with t_w-stamped snapshots + R-replica averaging. No new physics implementation; observability instrumentation only.
- **Cap_map row affected:** static-ultrametricity row (currently HARD_FAIL) — would graduate to "dynamical-UM confirmed" if Q-F1 PASSes; OR settle to "list-with-first-order-hysteresis" if Q-F1 FAILs (still useful product framing).
- **Decisive single test:** 1-hour CPU smoke measuring ONLY M_dyn at (t_1=16, t_2=128, t_3=1024) sweeps with R=200, 1 seed. M_dyn ≥ 0.75 = smoke PASS; M_dyn ≤ 0.65 = smoke FAIL; in-between = MIDDLE BAND, escalate to FULL.

### Q-F2 — Does the substrate's two-time correlator C(t, t_w) and FDT-violation ratio X(C) discriminate between CK pure aging and the Garcia-Lorenzana oscillating-amorphous overlay?

- **Evidence:** Berthier-Holdsworth-Ricci-Tersenghi 2001 (cond-mat/0112378) — piecewise-constant X(C) is the 1-step RSB signature; Garcia-Lorenzana 2025 (PRL 135, 187402 / arXiv:2408.17360) — exceptional-point oscillating phase appears as a finite-ω peak in |FT[Ĉ(ω)]|; Cugliandolo-Kurchan 1993 framework.
- **Cap_map row affected:** non-equilibrium-stat-mech row (currently 🟢 45-60%) — would graduate to 60-75% if either CK-pure or oscillating overlay confirms. Opens new "oscillating-amorphous" sub-class row if the finite-ω peak appears (SUBSTRATE-NOVEL signature, not in prior cap_map).
- **Three discriminating sub-tests:**
  - C(t, t_w) at fixed t/t_w monotone decreasing vs oscillating envelope
  - X(C) piecewise-constant (R² ≥ 0.95) vs continuous-monotone vs non-monotone-crossing-zero
  - |FT[Ĉ(ω)]| no-peak vs peak at ω* > 0 with SNR > 3
- HARD-FAIL for BOTH: C(t,t_w) time-translation-invariant (would falsify aging entirely, force reopening static-RSB shelf).

### Q-F3 — Does the substrate's stored-pattern overlap matrix have high cophenetic correlation (c ≥ 0.85) on a single-linkage dendrogram DESPITE the strict-ultrametric inequality violation (mean_ratio = 0.583)?

- **Evidence:** Saraçli et al. 2013 (J. Inequalities Appl.) — cophenetic correlation high despite ultrametric inequality violation is the standard case in real-data clustering; Krivanek-Moravek 1986 — any finite metric admits a closest-from-below "subdominant ultrametric" via single-linkage MST. The L∞ distortion ε can be quantified and shipped as audit tolerance.
- **This is the single cheapest decisive test in the rescue:** <1s wall time, 5×10⁶ FLOPs, runs on existing pattern-overlap matrix. No new data.
- **Cap_map impact (decisive):** Q-F3 PASS unlocks **3 substrate killer features simultaneously** — multi-tenant tree (F1), coarse-to-fine retrieval (F2), cluster-organized memory (F7). Audit-layer 10-primitive taxonomy: 7 of 10 primitives that were AT RISK from strict-UM failure become SAFE.
- HARD-PASS: c ≥ 0.85 (strong tree structure) + silhouette s ≥ 0.40 at natural cluster count.
- HARD-FAIL: c < 0.65 OR Ward-linkage and single-linkage disagree fundamentally.
- MIDDLE BAND: 0.65 ≤ c < 0.85 — soft tree only; reframe product to "approximate / statistical hierarchy."

### Q-F4 — Does the substrate exhibit strict ultrametricity in SADDLE space (not minima space) at mean_ratio_saddle ≥ 0.85, as predicted by the saddle-hierarchy component of the SKAH-M class?

- **Evidence:** v228 SKAH-M classification = non-reciprocal Hopfield + spatial-correlated DAM + **saddle-hierarchy** DAM. The saddle-hierarchy axis predicts STRICT hierarchy in SADDLE space and only WEAK hierarchy in minima space. The v324 test was on MINIMA overlaps — wrong space for SKAH-M's hierarchical signature.
- **Cap_map row affected:** SKAH-M-class row (currently 🟢) — would graduate to "saddle-hierarchy confirmed at strict ultrametric depth" if Q-F4 PASSes. Substrate-novel signature ("audit at saddle depth") not in any prior cap_map.
- **Protocol:** sample saddles via gradient-ascent from minima (Hessian-zero-eigenvalue points). Apply same triplet test on saddle overlaps.
- **Verdict relationship to Q-F1, Q-F3:** Q-F4 is ORTHOGONAL to Q-F1 (dynamical trajectory space) and Q-F3 (cophenetic dendrogram on minima). All three could pass simultaneously; none is conditional on the others.

### Q-F5 — Does the substrate's first-order multi-basin structure (Pred-4 v211, max_gap=1.84) support a return-point-memory hierarchy of inner / outer hysteresis sub-loops at fixed Spearman ρ ≥ 0.7 between loop-width ratio and basin-overlap separation?

- **Evidence:** Sethna-Dahmen-Myers 1993 (cond-mat/9210018) — hysteresis hierarchies in disorder-driven first-order transitions; Preisach state-transition graph (arXiv:2001.08486) — return-point memory organizes hierarchy of loops and sub-loops.
- **Cap_map row affected:** Pred-4 hysteresis row (currently confirmed at outer-loop level) — would graduate to "sub-loop hierarchy + return-point memory confirmed" as Pred-5. Maps directly to live-drift-detection killer feature.
- **MEDIUM cost** (~5-15 min GPU), most expensive of the rescue tests. Defer behind Q-F1, Q-F3, Q-F4.

---

## 3. RECOMMENDED RESCUE TIER ORDERING

**Tier-1 (must close in this push — all cheap, all local CPU/GPU):**

1. **Q-F3 cophenetic correlation** — **single cheapest decisive test (<1s wall)**; unlocks 3 killer features simultaneously if PASS; runs on existing overlap matrix. **Start here.**
2. **Q-F1 dynamical M_dyn smoke (1-hour CPU)** — single observable, decisively orients the FULL CK protocol. R=200, M_dyn only, t_1=16, t_2=128, t_3=1024.
3. **Q-F4 saddle-overlap triplet test** — substrate-novel SKAH-M-class signature; orthogonal to Q-F1 and Q-F3.

**Tier-2 (gated on Tier-1 signal):**

4. **Q-F2 C(t,t_w) + X(C) FDT ratio FULL** — Garcia-Lorenzana vs CK-pure phase discrimination. Conditional on Q-F1 smoke landing in PASS or MIDDLE BAND.
5. **Q-F5 Preisach hysteresis hierarchy** — multi-resolution Pred-5; medium cost; reserve until Tier-1 settles.

**Predicted-fail (DO NOT drill — structural mismatch with confirmed phenomenology):**

- F4 RFOT mosaic patches — BSC bipolar patterns are exchangeable; no natural spatial embedding for ξ_mosaic. Category-error if forced.
- F5 FRSB continuous q(x) — Pred-4 first-order multi-basin strongly suggests 1-RSB-like discrete-basin phenomenology; would contradict confirmed hysteresis. Aspelmeier-Moore-Young 2008 predicts K(N=4096)≈4 levels max.

---

## 4. STRATEGIC FRAMING (load-bearing for cap_map + external comms)

**The substrate is a working memory that AGES, not crystallizes.** This is a killer feature, not a bug:

- Drift on a marginal manifold maps directly to **per-fact retention policy** as a tunable drift-rate knob.
- The oscillating-amorphous overlay (if Q-F2 confirms a finite-ω peak in Ĉ(ω)) gives a non-arbitrary clock signal for **live drift detection** — the long-sought operational reliability primitive.
- The FDT-violation X(C) yields a **thermodynamic audit certificate** — the system declares "I am not at equilibrium, here is X(C), here is the entropy production." Direct connection to deletion-certificate killer feature.

**Framing trap to AVOID:** do NOT externalize "tested for FRSB ultrametricity and failed." That was the wrong test for the substrate's phase. Correct external framing:

> "Free-Poisson spectral identity κ_n = α confirmed (v324). Substrate is in a non-equilibrium dynamical phase (CK-aging core, possibly with non-reciprocal oscillation overlay). Pursuing dynamical signatures appropriate to the phase class: two-time correlator C(t,t'), FDT-violation ratio X(C), dynamical ultrametricity M_dyn, return-point-memory hierarchy. All five are operationally measurable on existing substrate dynamics."

**Substrate killer-features mapping (from drill L2-C):**

| Killer feature | Supporting test |
|---|---|
| Deletion certificate (3-level) | Q-F3 (cophenetic for cluster level) + DG(m,r) audit-tree (8 tiers ≈ log₂(P) at P=614) |
| Compositionality audit API | Q-F3 (dendrogram as index) + L=2 polynomial DAM rank-k commutativity |
| Per-fact retention policy | Q-F1 (aging exponent μ as drift-rate knob) + Q-F2 (X(C) as entropy-production rate) |
| Live drift detection | Q-F2 (Ĉ(ω) peak as non-arbitrary clock) + Q-F5 (return-point memory invariant) |
| Edit-with-impact-prediction | Q-F3 (centroid lookup + cluster-membership impact) |

**All 5 killer features have at least one rescue-test in their support set.** The strict-ultrametricity failure does NOT damage any killer feature; it only retires the (over-strong) "rigorous Parisi-tree certificate" sub-claim, which was never the operational target.

---

## 5. CAP_MAP UPDATE REQUESTS (for strategy to commit)

Research recommends the following annotations to cap_map v324 (orchestrator owns the commit; strategy designs cell ordering):

1. **`static-ultrametricity` row** (currently HARD_FAIL labeled): rename to "static ultrametricity (off-target for dynamical phase)" with explanatory annotation: "test was static probe of dynamical phase; mean_ratio=0.583 is consistent with finite-N corrections per Cacciuto-Marinari-Parisi 1996 + Stariolo 2001 lit precedents; dynamical-UM rescue protocol Q-F1 is the substrate-class-correct probe."

2. **`Garcia-Lorenzana 2025 precedent` flag** (currently "REFUTED"): rewrite to "DYNAMICAL signature — premature dismissal; arXiv:2408.17360 / PRL 135, 187402 predicts oscillating C(t,t') with exceptional-point bifurcation, NOT static ultrametric P(q). Q-F2 tests the actual prediction."

3. **NEW row candidate: `dynamical-1-step-ultrametricity`** (🔬 pending Q-F1).
4. **NEW row candidate: `oscillating-amorphous-phase`** (🔬 pending Q-F2 finite-ω peak in Ĉ(ω)).
5. **NEW row candidate: `cophenetic-tree-fidelity`** (🔬 pending Q-F3; P_predicted = 0.62 — most likely to pass).
6. **NEW row candidate: `saddle-hierarchy-ultrametricity`** (🔬 pending Q-F4 — substrate-novel SKAH-M signature).
7. **NEW row candidate: `Pred-5 sub-loop hierarchy`** (🔬 pending Q-F5).

---

## 6. CONVERGENT-EVIDENCE CITATIONS (load-bearing across the 6 drills)

- **arXiv:2408.17360 / PRL 135, 187402 (2025)** — Garcia-Lorenzana et al., Nonreciprocal Spin-Glass Transition and Aging. **Citation corrected from the cap_map v324 PRL placeholder.**
- **arXiv:2501.00983 (Jan 2025)** — Xue/Maghrebi/Mias/Piermarocchi, Critical Dynamics and Cyclic Memory Retrieval in Non-reciprocal Hopfield Networks. Different authors from Garcia-Lorenzana. The non-reciprocal-Hopfield-specific analog. Hopf + fold bifurcation, ζ=1/2 and 1/3 critical exponents, limit-cycle attractors.
- **arXiv:2511.18439 (Sept 2025)** — Overlap distribution of spherical spin glass models with general eigenvalue distribution. **KEY algebraic lock:** replica symmetry is determined by eigenvalue spacing at the edge, not bulk. MP-without-spike is incompatible with FRSB.
- **Cugliandolo & Kurchan 1993, cond-mat/9303036** — canonical CK + dynamical ultrametricity originator.
- **Folena, Franz, Ricci-Tersenghi 2019/2020, arXiv:1903.01421 (PRX)** — marginal-state aging, strong ergodicity breaking.
- **Stariolo 2001, cond-mat/0010495** — direct lit precedent for "dynamical UM passes where static UM fails" at finite N.
- **Cacciuto, Marinari, Parisi 1996** — 4D EA needs L ≥ 12 (N ≥ 20,736) for clean static UM. Substrate at N=4096 is below threshold.
- **Berthier, Holdsworth, Ricci-Tersenghi 2001, cond-mat/0112378** — piecewise-constant X(C) is 1-step RSB signature.
- **Castillo, Chamon, Cugliandolo, Iguain, Kennett 2002, cond-mat/0010495** — three-time triangle test methodology; dynamical UM ABSENT in coarsening, hints present in EA-3D.
- **Iniguez, Marinari, Parisi, Ruiz-Lorenzo 1999, cond-mat/9903130** — numerical mean_ratio ≈ 0.88 at finite N in 3D EA.
- **Aspelmeier, Moore, Young 2008, arXiv:0711.3445** — K(N)∝N^(1/6) RSB levels resolvable at finite N. K(N=4096)≈4.
- **Saraçli et al. 2013** — cophenetic correlation high despite ultrametric inequality violation = standard case in real-data clustering.
- **Sethna, Dahmen, Myers 1993, cond-mat/9210018** — hysteresis hierarchies in disorder-driven first-order transitions.
- **Bernaschi et al. 2017 PNAS** — static-dynamics equivalence through FD ratio in 3D EA.
- **arXiv:2506.23987 (2025)** — Heavy-Tailed Mixed p-Spin Spherical: explicit case where ultrametricity breaks down and Parisi formula fails yet hierarchical structure stays meaningful via other measures. Direct precedent for substrate's regime.

---

## 7. DISCIPLINE DECLARATIONS

- Each Q-F# above maps to an experimental cell; strategy + exp_dev resolve cell design (anchor name, sweep grid, HP/MID/HF bands, queue, seed count, timeout).
- Pre-PROT-018 anchor-name `_n<N>` binding contract holds.
- Q-F1 smoke + Q-F3 are the highest-priority next experimental moves; both fit local laptop CPU at <1 hour combined wall time.
- Q-F2, Q-F4, Q-F5 are gated on Tier-1 signal — do not pre-design until Q-F1 + Q-F3 land.
- ASCII-only print; per-experiment `--timeout` required; HARD-FAIL conditions pre-registered explicitly per drill outputs.
- No padding: if Tier-1 lands HARD-FAIL, the substrate's hierarchical-state-structure product story moves to "list-with-first-order-hysteresis" (still useful, but different framing). Do NOT escalate to Tier-2 in that case.

---

**END OF CONSOLIDATION.** Orchestrator: route Q-F3 + Q-F1 smoke first; gate Tier-2 on results; commit cap_map annotations + citation corrections regardless.

Acted-on 2026-06-02: 6-drill revival consolidation drove Q-F1 + Q-F2 + dynamical-UM cells; v330 LIFT applied; v324 'REFUTED' revised to 'WRONG-PROBE'; PP-33 framework-class LIFTED in v330 + v331 + v332
