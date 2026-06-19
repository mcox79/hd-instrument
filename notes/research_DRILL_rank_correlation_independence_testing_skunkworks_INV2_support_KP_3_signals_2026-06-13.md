# Research drill — independence testing for KP-promotion 3-signal architecture (skunkworks INV-2 support)

Filed: 2026-06-13
Author: research sub-agent (Opus)
Trigger: skunkworks flag that KP promotion operator's claimed "3 independent signal classes" (P1 graph in-degree + P3 structural-bisimulation class size + P4 codebook-geometry archetype) may all read one latent hubness/centrality factor. Need a statistical test battery to MEASURE pairwise correlation rather than assert independence.

Honest framing: substrate-product positioning is uncharted; prior work informs but does not govern. Lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50).

---

## (a) HEADLINE

Three-signal independence claim is TESTABLE via a standard battery the network-science literature has converged on: **Spearman rho + Kendall tau on full ranking + Rank-Biased Overlap (RBO) on top-K + partial correlation residualization**. Empirically, in dense / scale-free / hub-rich networks, classical centrality metrics show |rho| in the 0.6-0.95 range (degree-betweenness-eigenvector are often **redundant**, factor-loading on 1 latent "centrality" factor with eigenvalue ratio >4:1). For KP to claim 3 independent signals, the substrate must clear meaningfully tighter bounds than that — and the test must be **pre-registered**, not chosen after seeing the numbers.

P_deflated(KP signals genuinely independent across all 3 pairwise) = 0.35
P_deflated(>=1 pair shows |rho| > 0.7 indicating partial-redundancy) = 0.55
P_deflated(all 3 collapse onto one latent factor, EFA first-eigenvalue dominance > 0.7 of total variance) = 0.25

## (b) Cheap decisive test (CELL INV-2 design)

**Input:** for the candidate set of T3 atoms scored for promotion, compute three independent rank-vectors:
- s1 = P1 graph in-degree score
- s3 = P3 structural-bisimulation class size score
- s4 = P4 codebook-geometry archetype distance score

**Battery (run on all 3 pairs s1xs3, s1xs4, s3xs4):**

1. **Spearman rho** — full-corpus rank correlation. Captures monotone agreement on the *entire* candidate ordering. This is the literature-default for centrality-metric comparison (chosen over Pearson because centrality distributions are heavy-tailed; Pearson is dominated by hubs).
2. **Kendall tau-b** — concordance-based rank correlation, more robust to ties and tail noise. Used as a Spearman cross-check; in heavy-tailed graphs Kendall typically reads ~0.7-0.8x of Spearman, so |tau| < 0.5x|rho| flags a discordance worth investigating.
3. **RBO (Rank-Biased Overlap, p=0.9)** — top-weighted ranked-list overlap on the top-K set we'd actually *promote* (K = production threshold). RBO is the right metric when the decision is "do these 3 signals SELECT THE SAME ATOMS for promotion" rather than "do they agree on the global ordering." Use p=0.9 ⇒ ~63% of weight on top-10, ~86% on top-30.
4. **Jaccard@K** on the top-K hard set — coarse set-overlap baseline; complements RBO with a non-weighted view.
5. **Partial Spearman** — for each pair (s_i, s_j), compute rho(s_i, s_j | s_k) by regressing each on the third score, ranking residuals, and correlating. If the marginal rho is large but partial rho is small, the apparent dependence is mediated by the third signal (which is itself a strong sign of single-latent-factor architecture).
6. **EFA / PCA on the score-matrix** — 3-column z-standardized matrix; report eigenvalue spectrum. If the first eigenvalue captures >70% of total variance and all three signals load >0.7 on PC1, that is the literature's accepted signature of a single latent factor (Kaiser criterion + Kuncheva-style dominance).
7. **Ensemble-diversity Q-statistic** — recast each signal as a binary classifier (promote vs not, at the production threshold). Compute pairwise Q. Q=0 ⇔ statistical independence; |Q| > 0.5 is the standard ensemble-learning "high correlation" cutoff. Double-fault measure as cross-check.

**Compute cost:** all 7 are O(N log N) on the candidate set; full battery is single-CPU minutes for typical promotion-batch sizes. Re-runnable; deterministic.

## (c) Falsifiable predictions (pre-registered fail-bands)

We pre-register before running, per [[feedback-held-out-test-methodology]]. The bands are derived from the centrality-redundancy literature (median pairwise rho in scale-free / dense graphs ~0.6-0.9, often >0.9 for degree-eigenvector pairs).

### HARD-PASS — three signals are genuinely independent
- ALL three pairwise |Spearman rho| < 0.4 (literature "weak" by Schober et al. 2018)
- ALL three pairwise |Kendall tau| < 0.3 (consistent with weak rho)
- ALL three pairwise RBO@K(p=0.9) < 0.5 (top-K hard set overlaps less than chance-rescaled)
- ALL three pairwise Jaccard@K < 0.4
- EFA first eigenvalue captures < 0.55 of total variance (no dominant latent factor); PC1 loadings not all >0.7
- Q-statistic |Q| < 0.4 on all pairs
- Partial rho within 0.1 of marginal rho (confirms NO mediation by third signal)

→ Pre-registered claim: "3-signal independence empirically supported; substrate-product positioning as 3 orthogonal axes is corroborated."

### HARD-FAIL — single latent factor (KP "3 signals" is really 1)
- ANY pair |Spearman rho| > 0.7 (literature "strong"; classical centrality-collapse signature)
- EFA first eigenvalue captures > 0.75 of total variance AND all 3 loadings on PC1 > 0.7
- Top-K RBO > 0.7 on at least 2 of 3 pairs (same atoms selected by ostensibly different signals)
- Q-statistic > 0.7 on at least 2 of 3 pairs

→ Pre-registered claim: "KP 3-signal independence REFUTED. The promotion operator collapses to one latent hubness/centrality factor. Substrate must downgrade claim to 1-signal-with-2-redundant-readouts, or redesign one of the signals to read a structurally orthogonal feature (suggestions in section (e))."

### MIDDLE BAND — partial redundancy (most likely outcome)
- ONE pair in |rho| in [0.4, 0.7]; other two below 0.4
- EFA first eigenvalue 0.55-0.75 of total variance
- Partial rho substantially smaller than marginal for at least one pair (indicates mediation)

→ Pre-registered claim: "Substrate has 2 independent + 1 partially-redundant signal class. Either drop the redundant signal, or re-define it to capture the residual variance. Pre-register CELL INV-3 to test the redefinition."

## (d) Cross-thread synthesis

- **Memory: substrate_architecture_3_axis_EMPIRICALLY_ORTHOGONAL_Cell_3_KP_P6_HARD_PASS** (2026-06-13) established 3-axis EMPIRICAL ORTHOGONALITY at the *architectural* layer (tool-citation-tier vs epistemic-tier vs substrate-load-bearing-axis) via 0.077 ratio + 48% tools-outside-top-100. That validates the *architecture* but does NOT validate the KP promotion *signal* triplet — different claim. KP-signal independence is a fresh test; the architecture result raises priors moderately (P_prior +0.05) but does not transfer.
- **Memory: methodology_rule_verify_before_asserting_5_class_cluster** (2026-06-13) is the meta-rule that mandates this drill — we are pre-empting a claim-asserting failure mode.
- **Memory: 11th-rule held-out test methodology** — the test battery here MUST run on a held-out atom set (NOT the set used during P1/P3/P4 tuning). Pre-registration covers this.
- **Memory: feedback_always_reconsider_frameworks_dont_lock_in** (2026-06-13) — the skunkworks flag is itself an instance of this rule firing. Do not lock in the "3 independent signals" architectural claim until the empirical test runs.
- **Centrality-redundancy literature (Meghanathan, Oldham, Ronqui-Travieso, Schoch)** — converges on the empirical fact that degree-eigenvector pairs in scale-free graphs show rho > 0.8 routinely; betweenness is the most differentiating classical metric; closeness-eigenvector pairs vary wildly by network class (0.91 in collaboration, -0.04 in power grids). This is the calibration we are deflating against.

## (e) Substrate-product implications

1. **If HARD-PASS:** substrate-product positioning gains a *measured* 3-signal KP architecture artifact — directly defensible vs. LLM categorical-gap framing (LLMs cannot decompose their own "this is important" judgment into orthogonal signal classes; substrate can both decompose AND empirically test the decomposition).
2. **If HARD-FAIL:** substrate-product narrative is REVISED, not lost. The claim shifts from "3 orthogonal signals" to "1 latent factor + 2 high-fidelity readouts of it." This is still a substrate-product win — LLMs have ZERO observable signal channels for their internal "importance" judgment. The substrate having 1 measured signal beats LLMs having 0. The redesign path: take the most-redundant signal (likely P1 graph-in-degree, the most classical centrality metric) and replace with a structurally orthogonal observable. Candidates:
   - **Replay-frequency** in sleep-replay traces (temporal, not structural)
   - **Cross-tier promotion attempts that FAILED** (negative-evidence channel)
   - **Use-in-proof-context** count from L6-PROOF FINDER (epistemic-load, not graph-load)
3. **If MIDDLE BAND:** pre-register CELL INV-3 to redesign the partially-redundant signal. This is the most likely outcome (~0.45 P_deflated).

## (f) Critical alternative-cause analysis

If the test reads |rho| > 0.7, **rho-elevation has 4 candidate causes**, NOT just "single latent factor":

1. **Shared data source contamination** — if P1, P3, P4 all derive from the same DAG snapshot, the snapshot's structural pathology (e.g., dense hub regions) drives all three correlations upward. **Diagnostic:** re-run on a held-out DAG snapshot taken at a different time; if rho drops, the issue is snapshot-shared. **Mitigation:** average over multiple snapshots / bootstrap.
2. **True latent-factor collapse** — the signals genuinely read one factor; this is the substantive claim under test.
3. **Methodological mistake — normalization** — if the three signals are normalized by overlapping denominators (e.g., all by total atom count), spurious correlation arises. **Diagnostic:** check the score-computation code for shared normalization; recompute with each signal independently scaled.
4. **Methodological mistake — selection bias on the candidate set** — if the candidate set was pre-filtered using a centrality-like criterion (e.g., "only atoms with > k incoming edges"), the candidate set is range-restricted and all three signals are squeezed into the high-centrality tail, inflating rho. **Diagnostic:** run the battery on an UN-PREFILTERED random atom sample as a calibration baseline. If correlations drop substantially on the random sample, selection bias dominates.

Cell INV-2 **must report** all 4 diagnostics alongside the primary battery, with explicit go/no-go on each before concluding "single latent factor." Without this, a HARD-FAIL verdict is itself unreliable.

## Citations (verified, 7)

1. Ronqui, J.R.F. & Travieso, G. (2015) — "Correlation Coefficient Analysis of Centrality Metrics for Complex Network Graphs," arXiv:1409.6033 — empirical centrality-pair rho distributions across network classes.
2. Schoch, D. et al. (2019) — "Consistency and differences between centrality measures across distinct classes of networks," PLOS ONE — power-grid vs collaboration network divergence (rho -0.04 vs 0.91).
3. Webber, W., Moffat, A., Zobel, J. (2010) — "A Similarity Measure for Indefinite Rankings," ACM TOIS — RBO original specification, p-parameter weighting.
4. Kuncheva, L.I. & Whitaker, C.J. (2003) — "Measures of Diversity in Classifier Ensembles and Their Relationship with the Ensemble Accuracy," Machine Learning — Q-statistic, double-fault, correlation coefficient for ensemble independence.
5. Schober, P., Boer, C., Schwarte, L.A. (2018) — "Correlation Coefficients: Appropriate Use and Interpretation," Anesthesia & Analgesia — the negligible/weak/moderate/strong/very-strong threshold table (0.1/0.39/0.69/0.89).
6. Meghanathan, N. (2024) — "Exploratory Factor Analysis of the Centrality Metrics for Complex Real-World Networks," arXiv:2403.03525 — EFA on degree/eigenvector/betweenness/closeness across 80 networks; methodology for latent-factor identification.
7. Epskamp, S. & Fried, E.I. (2017) — "A Tutorial on Regularized Partial Correlation Networks," arXiv:1607.01367 — partial-correlation methodology for direct-vs-indirect dependence in observational graphs.

## Next-drill candidate

Field: `network-science-graph-theory` (tier-1b new, scope-bonus active).
Angle: spectral-gap / Ramanujan bound on the candidate-overlap graph between the 3 signal selectors — gives a graph-theoretic, K-free bound on signal divergence that complements the rank-correlation battery. Cheap and adjacent.
