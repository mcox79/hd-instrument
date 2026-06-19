# Research drill — Cap 11 chi_4 as early-warning indicator for Cap 10 capacity boundary

**Date:** 2026-05-24
**Trigger:** Daily research_drill_due (10:00 UTC); standing cadence per design-space-and-audit-cadence feedback.
**Status of related shore-up matrix items:** anti-RM closed via Kerdock-MUB-stabilizer theorem; Bet A OOM is engineering-only; THIS is the last still-open substantive weakness.

---

## Section 1 — chi_4 in glassy/supercooled-liquid literature

The four-point connected susceptibility chi_4(t) is the canonical measure of dynamical heterogeneity in supercooled liquids and structural glasses. Operationally, chi_4(t) = N * Var(C(t)) where C(t) is a two-point density-overlap correlator at lag t; equivalently, it integrates the four-point correlation function G_4(r, t). Berthier-Biroli (Rev. Mod. Phys. 2011, "Theoretical perspective on the glass transition and amorphous materials") and the earlier Toninelli-Wyart-Berthier-Biroli-Bouchaud line establish chi_4(t) as the scalar diagnostic that PEAKS at a timescale tau* close to the alpha-relaxation time tau_alpha, with peak height chi_4* growing as the system is supercooled. The peak signals the spatial extent (dynamic correlation length xi_4 ~ chi_4*^(1/d_f)) over which particles relax cooperatively — i.e. it is a non-Gaussian fluctuation amplitude that diagnoses how the system is approaching structural arrest.

Key empirical regularities relevant to Cap 11:
- chi_4* grows monotonically as approach-to-glass-transition proceeds (in our case: as memory load alpha approaches alpha_c).
- The peak is BROADER and more LEAD-TIME-rich the further from a sharp-transition limit; near a true dynamical singularity, peak narrows.
- Typical SNR in glass MD literature: chi_4* / chi_4(baseline) easily exceeds 5-10 for moderate supercooling; the field treats SNR >= 3 as routinely measurable.
- chi_4 is generically MORE SENSITIVE than two-point (chi_2) measures precisely because heterogeneity is a non-Gaussian effect.

Direct mapping to Kerdock-Hebbian substrate: Cap 11's primitive already measures chi_4 over substrate-write trajectories. Substrate state is a high-dim spin/atom configuration; "supercooling" = "approaching capacity boundary alpha_c." The glassy analogy is structural (spin-glass-adjacent algebra; see materials-science-probe feedback), not just rhetorical.

---

## Section 2 — Adaptation to Cap 10 capacity-boundary operation

Cap 10 (associative-memory write capacity) has a known soft boundary alpha_c at load where retrieval SNR collapses (Hopfield-style; Kerdock variant raises but does not eliminate). The substrate-monitor hypothesis is:

> **H1 (chi_4 peaks at crossover):** As running load alpha(t) approaches alpha_c during continual operation, chi_4 measured over a sliding window of W recent writes rises monotonically, peaks at a lead-time K writes before retrieval-SNR collapse, then either saturates or declines.

Falsifiable quantitative form:
- **Peak SNR:** chi_4*(near-boundary) / chi_4(baseline, alpha << alpha_c) >= 3.
- **Lead-time:** chi_4 first crosses 3-sigma-baseline at least K = 0.05 * alpha_c writes before the retrieval-SNR knee (so for alpha_c ~ 0.14 * N, K >= ~0.007 * N writes).
- **Specificity:** chi_4 baseline (alpha << alpha_c) shows < 1.5-sigma drift over a control run of equal length — i.e. the spike is not just random walk.

This is exactly the form the glassy literature delivers; the question is whether Kerdock-Hebbian dynamics inherits enough of the glassy structure to produce a usable peak-at-crossover. Three reasons to expect YES:
1. Hopfield/Kerdock attractor landscapes have replica-symmetric solutions near alpha_c that break to RSB — the same algebra as p-spin glasses where chi_4 peaks.
2. Substrate writes are sequential and quasi-equilibrium; trajectory fluctuations are exactly what chi_4 quantifies.
3. The retrieval-collapse transition is a sharp dynamical knee, not a smooth crossover — sharper transitions generically yield TALLER chi_4 peaks (good for SNR) but NARROWER lead-time windows (risk for K).

Risk: if Kerdock structure too thoroughly suppresses crosstalk until catastrophic collapse, chi_4 may stay flat then jump — high SNR, zero lead-time, useless as early-warning.

---

## Section 3 — Cross-domain early-warning candidates

Three fields, three candidate indicators, ranked vs chi_4 for this substrate context:

**Ecology / climate (Scheffer 2009 Nature; Dakos et al., PNAS 2008-2023 line):**
- Indicators: **lag-1 autocorrelation** AC(1) rising; **variance** of state variable rising; **skewness** + **kurtosis** drift; deep-learning EWS (Bury et al. PNAS 2021).
- Theoretical basis: critical slowing down at a saddle-node bifurcation — eigenvalue of linearized dynamics approaches 0, recovery time grows.
- Strength: directly applicable wherever the boundary is a fold/saddle-node. Cap 10 boundary plausibly IS saddle-node-like (retrieval basin shrinks to zero radius).
- Weakness: AC and variance are TWO-point, weaker SNR than chi_4 for non-Gaussian transitions; literature consistently reports 1.5-2.5x SNR vs ~3-10x for chi_4 in analogous systems.

**Power-grid / engineering stability:**
- Indicators: **voltage variance growth**, **return-time-to-equilibrium**, **damping ratio decay** of small-signal perturbations.
- Theoretical basis: same critical-slowing-down family; explicit linearization around operating point.
- Direct analog: probe substrate with small read-perturbation, measure relaxation time. Concrete and cheap.
- Weakness: requires defining the small-signal probe operationally — extra implementation.

**Neuroscience / pre-seizure:**
- Indicators: variance + AC(1) of intracranial EEG (Maturana et al., Nat Commun 2020); spike-train statistics.
- **Critically: literature is contradictory.** Maturana et al. 2020 supports CSD as biomarker; Wilkat et al. 2019 (arXiv:1908.08973) finds NO evidence for CSD prior to 105 seizures. The discrepancy is methodological (window length, detrending, multiple-comparison correction).
- Lesson for substrate: a positive chi_4 result must survive sensitivity-to-window-length analysis and a permutation null.

**Financial markets (mentioned for completeness):**
- Indicators: critical-slowing-down in log-returns; variance + AC. Generally weaker SNR than physical systems; high noise floor.

**Synthesis — does cross-domain probe point to something BETTER than chi_4?**
- For Cap 10 capacity boundary, chi_4 likely DOMINATES on peak SNR (non-Gaussian sensitivity).
- BUT lag-1 autocorrelation and variance are nearly free to compute alongside chi_4 — they should be measured in parallel as redundant indicators and as a check against the seizure-literature methodological-noise risk.
- Damping-ratio / return-time (engineering) is the strongest CANDIDATE COMPLEMENT: a small read-perturbation relaxation probe gives a different physical signature (timescale, not amplitude) and is robust to non-Gaussian artifact.

Recommendation: anchor on chi_4 but instrument AC(1), variance, AND a relaxation-time probe in the same experiment — three indicators at the cost of one, and the agreement/disagreement between them is itself diagnostic.

---

## Section 4 — Anchor experiment proposal

**Name:** `cap11_chi4_early_warning_anchor_v1`

**Queue / ETA:** GPU queue (substrate dynamics is depth-needing per Strategy's earlier estimate). ETA ~45-60 min wallclock; includes 5-seed replication.

**Setup:**
- Substrate: Kerdock-Hebbian, N = standard cap_map test size.
- Continual-write protocol: write sequence approaches alpha_c from below; record substrate state every dW writes (window W).
- Compute per-window: chi_4(W), Var(state), AC(1, state), relaxation-time-to-perturbation tau_R.
- Pre-register knee detection: retrieval-SNR knee at the write index where retrieval accuracy drops below 0.5 of its plateau.
- Pre-register baseline: median of indicator over the first 30% of writes (alpha well below alpha_c).
- 5 seeds; report median + IQR.

**Hard-pass:**
- chi_4 SNR (peak / baseline) >= 3
- Lead-time K >= 0.05 * alpha_c writes before knee
- Result holds across >= 4 of 5 seeds
- chi_4 spike SURVIVES permutation null (shuffle write order, recompute; spike should disappear)

**Hard-fail:**
- chi_4 SNR < 1.5, OR
- Zero / negative lead-time (peak at or after knee) on >= 3 of 5 seeds, OR
- Permutation null reproduces the spike (indicator is not specific to approach-to-boundary)

**Middle band (SNR 1.5-3 OR lead-time 0 - 0.05*alpha_c):**
- Check whether AC(1), Var, or tau_R provides usable signal where chi_4 falls short.
- If a complementary indicator hard-passes, propose a combined-indicator anchor v2.
- Otherwise downgrade Cap 11 to "passive monitor only; no early-warning license" and close Composition C.

**Composition-C unlock condition:** Hard-pass on chi_4 (or on a combined indicator) licenses Cap 12 + Cap 11 + Cap 1 = "adaptive routing under continual operation with predictive observability." This is the explicit downstream payoff.

**Risk mitigations baked in:**
- Multi-indicator instrumentation (chi_4 + AC + Var + tau_R) hedges against the seizure-literature methodological-noise risk.
- Permutation null hedges against false-positive from drift / non-stationarity.
- 5-seed replication catches stochastic flukes.

---

## Honest reading

chi_4 is the right PRIMARY indicator: the glassy-substrate analogy is structural, not rhetorical, and the literature SNR (5-10x) is comfortably above the >=3 hard-pass bar. The dominant residual risk is NOT "chi_4 is the wrong observable" but "Kerdock structure makes the transition too sharp, killing lead-time." Cross-domain literature does not suggest a better single indicator, but it does mandate instrumenting AC(1) / variance / relaxation-time in parallel — at near-zero marginal cost — both as redundant indicators and to inoculate against the methodological pitfalls that produced the contradictory pre-seizure literature.

**Sub-agents:** 3 Sonnet WebSearch (chi_4 glassy; Scheffer EWS; pre-seizure CSD), parallel dispatch, wallclock ~1 min for searches.
