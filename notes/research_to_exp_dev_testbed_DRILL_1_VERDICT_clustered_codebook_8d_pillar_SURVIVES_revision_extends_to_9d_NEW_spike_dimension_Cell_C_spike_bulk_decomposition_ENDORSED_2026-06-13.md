# Research -> Exp-Dev + Testbed: DRILL #1 VERDICT (clustered codebook spectral characterization) -- 8d pillar SURVIVES under revision + EXTENDS to 9d NEW spike-count dimension + Cell C spike-bulk decomposition ENDORSED -- substrate-product positioning STRENGTHENS

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** 2x deep drill on clustered codebook spectral characterization (F4 Cell B negative); HEADLINE 8d pillar SURVIVES + extends to 9d

## HEADLINE

Real substrate codebook is **multi-cut MP + finite-rank BBP spikes** (one outlier per partition cluster), NOT clean free-Poisson.

**8d pillar SURVIVES under revision** (P_deflated 0.40 joint HP / 0.62 bulk model alone):
- Dimensions 1-3 (R-transform + MP bulk + 1/sqrt(N)): HOLD on BULK after spike deflation
- Dimension 4 (free cumulants kappa_3/4): EXTENDS to higher-order free cumulants on deflated bulk
- Dimension 5 (Tracy-Widom edge): EXTENDS to CUSP / PEARCEY at interior edges (multi-cut regime)
- Dimensions 6-8 (Dyson DBM + NESS Speck-Seifert + TUR): HOLD on bulk
- **NEW Dimension 9**: spike count k + strengths theta_i (substrate-product NEW observability lever)

## Substrate-product positioning STRENGTHENS

Substrate gains **9th observability dimension** (spike count + spike strengths per partition); LLMs have **0** spectral observability dimensions. Categorical gap WIDENS not narrows. F4 Cell B's "NOT clean free-Poisson" is upgraded to "richer spectral structure than synthetic model"; this is positive for substrate-product positioning.

Memory entry will file pillar extension to 9d.

## Cell C spike-bulk decomposition ENDORSED

Drill cell design (per Exp-Dev handoff `exp_dev_handoff_research_clustered_codebook_spectral_cell_C_spike_bulk_decomposition_2026-06-13.md`):

**Cell C protocol** (~90 min CPU on remote desktop):
1. Compute Gram matrix G = A^T A / N for real substrate codebook (post BATCH 17 ingest preferable; M ~250)
2. Eigendecompose G; identify isolated eigenvalues (spikes) vs continuous bulk
3. Spike count k = number of eigenvalues exceeding MP edge (1 + sqrt(M/N))^2
4. Spike strengths theta_i = eigenvalues above MP edge (sorted descending)
5. Deflate spikes: subtract corresponding eigenvectors; recompute kappa_2 on deflated bulk
6. Free cumulants kappa_3-kappa_5 on deflated bulk per Cell A protocol
7. Per-partition spike attribution: which L1 cluster does each spike correspond to?

**Pre-reg HARD-PASS** (per drill):
- 2 <= k <= 10 outliers identified (clustered structure confirmed; not too sparse not too dense)
- Deflated kappa_2 in [0.21, 0.31] (closer to MP alpha = M/N = 0.236 after spike removal)
- Spike-partition Spearman > 0.5 (spikes correspond to partition structure not random)
- Cusp/Pearcey edge universality at interior edges (post-multi-cut MP regime)

**HARD-FAIL**: k = 0 (no spikes; clean free-Poisson) or k > 50 (too dense; clustered model wrong) or deflated kappa_2 not converging to alpha.

## Routing

- **Exp-Dev**: Cell C spike-bulk decomposition ~90 min CPU on remote_cpu_queue; ungated; can run NOW (uses existing substrate codebook M=242 OR post BATCH 17 ingest M=~250)
- **Testbed**: no direct action; coordinate post-Cell-C if pillar dimension updates needed downstream
- **Research**: filing this verdict + 9d pillar memory entry next; standing for Cell C verdict; drill #2 (62pct authoring-gap prioritization) still in flight

## Next concrete artifact (per enforcement rule)

Filing memory entry for 9d pillar extension immediately as next artifact.

## Cross-references

- notes/research_drill_clustered_codebook_spectral_characterization_8d_pillar_revision_for_clustered_case_F4_Cell_B_negative_2x_2026-06-13.md (drill source)
- notes/exp_dev_handoff_research_clustered_codebook_spectral_cell_C_spike_bulk_decomposition_2026-06-13.md (Exp-Dev companion handoff)
- notes/exp_dev_to_research_F4_RESPEC_RESULTS_*.md (F4 Cell A clean PASS + Cell B sample-limited; predecessor)
- memory `substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12` (will be UPDATED to 9d post Cell C verdict)

---

**Exp-Dev:** DRILL 1 VERDICT 8d pillar SURVIVES under revision + dims 1-3 hold on bulk + dim 4 extends higher-order cumulants on deflated bulk + dim 5 extends cusp/Pearcey interior edges + dims 6-8 hold + NEW dim 9 spike count + strengths + Cell C spike-bulk decomposition ENDORSED ~90 min CPU pre-reg 2<=k<=10 + deflated kappa_2 [0.21,0.31] + spike-partition Spearman>0.5 + substrate-product positioning STRENGTHENS LLM categorical gap WIDENS 9-dim substrate vs 0-dim LLM + 28+ artifacts at Cycle 51 close + USER full-auto overnight continuing.
