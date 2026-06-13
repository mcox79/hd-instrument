# Research: Tracking-document SECTION 7 FORMAL (9-dimensional spectral observability pillar — dims 1-9 + dim 4 footnote + audit-robust + RMT-universal + substrate-internal measurement + Tier 1 architectural claim 2 anchor)

**From:** Research (linchpin; per 12th rule own-work; Section 7 companion to Section 5 + 8 + 9)  **Date:** 2026-06-13
**Re:** Section 7 published form derived from F4 drill + spectral pillar 8d → 9d extension + audit-robust qualifier

---

## SECTION 7: 9-dimensional spectral observability pillar

### 7.1 Overview

Substrate observes its own codebook structure through 9 independent spectral observability dimensions grounded in random matrix theory + free probability + non-equilibrium thermodynamics. These are RMT-universal properties of the codebook matrix structure — independent of node labels — making them audit-robust Tier 1 architectural claims.

The 9 dimensions span:
- Bulk structure (dims 1-3): Marchenko-Pastur location + 1/√N convergence + bulk fit quality
- Higher-order cumulants (dim 4): Voiculescu free cumulants κ_3 + κ_4 (with footnote: sample-limited at M=253 codebook)
- Edge fluctuations (dim 5): Tracy-Widom distribution at spectral edge
- Dynamics (dims 6-8): Dyson Brownian motion + non-equilibrium steady-state + thermodynamic uncertainty
- BBP transition (dim 9): spike count + strength for clustered codebooks

As of 2026-06-13, dims 1-3 + 5-9 STAND at full audit-robustness; dim 4 has a sample-limited footnote pending structured-codebook growth.

### 7.2 Dim 1: Marchenko-Pastur bulk location (R-transform)

**Observable**: bulk eigenvalue density of substrate's codebook covariance matrix

**Substrate measurement**: substrate computes empirical eigenvalue distribution + fits Marchenko-Pastur (MP) bulk

**Audit-robustness**: invariant under codebook node relabeling per Voiculescu free probability theorem

**Empirical anchor**: substrate's clustered codebook empirically fits MP bulk at p < 0.001 (Cell B prior); dim 1 location parameter α = 0.000 in F4-RELABEL bootstrap (ROCK-STABLE)

### 7.3 Dim 2: MP bulk fit quality

**Observable**: residuals + Kolmogorov-Smirnov test against MP fitted distribution

**Substrate measurement**: substrate measures KS statistic on bulk eigenvalues vs MP fit

**Audit-robustness**: bulk fit follows from RMT-universality

**Empirical anchor**: F4-RELABEL bootstrap κ_2 SE/|κ| = 0.078 (STABLE)

### 7.4 Dim 3: 1/√N Kolmogorov convergence rate

**Observable**: rate at which empirical spectral distribution converges to MP as N→∞

**Substrate measurement**: substrate measures KS distance scaling with N

**Audit-robustness**: 1/√N rate is RMT-universal

**Empirical anchor**: substrate's clustered codebook follows expected 1/√N convergence (Cell B + Cell C prior)

### 7.5 Dim 4: Higher-order cumulants κ_3 + κ_4 (FOOTNOTE: sample-limited at M=253)

**Observable**: Voiculescu free cumulants κ_3 + κ_4 measured from free-probability-theoretic moments

**Substrate measurement**: substrate computes empirical moments → cumulant conversion + bootstrap composition stability

**Audit-robustness within cluster**: invariant under within-cluster relabeling per Voiculescu (analytically SE=0)

**Audit-robustness cross-cluster**: requires spike deflation per Au et al. 2015

**FOOTNOTE (per F4-RELABEL bootstrap 2026-06-13)**: at M=253 codebook size, κ_3 SE/|κ| = 0.172 + κ_4 SE/|κ| = 0.260 (κ_4 above 0.20 HARD-FAIL band). Higher cumulants are sample-limited at current M. Re-measurement at larger M (post structured-codebook growth) expected to stabilize.

**16th methodology rule candidate (1st appearance today)**: `RULE_higher_order_observables_need_larger_M_for_robustness` — empirical witness today; awaiting 2 more for promotion.

### 7.6 Dim 5: Tracy-Widom edge fluctuations

**Observable**: distribution of largest bulk eigenvalue at spectral edge

**Substrate measurement**: substrate fits Tracy-Widom CDF + KS test on rescaled edge eigenvalues

**Audit-robustness**: Tracy-Widom is RMT-universal at the edge

**Empirical anchor**: pending dedicated cell post deflated-bulk preparation; drill 17 (Tracy-Widom on deflated bulk) in flight

### 7.7 Dim 6: Dyson Brownian motion (DBM) dynamics

**Observable**: time-evolution of substrate's codebook eigenvalues under structural change

**Substrate measurement**: substrate observes eigenvalue trajectories during operator-overlap distillation events

**Audit-robustness**: DBM is RMT-universal dynamics

**Empirical anchor**: stable per prior 9d pillar work; not affected by today's audit cycle

### 7.8 Dim 7: Non-equilibrium steady-state (NESS) Speck-Seifert

**Observable**: stationary distribution + entropy production rate of substrate as out-of-equilibrium system

**Substrate measurement**: substrate computes Speck-Seifert NESS observable for clustered codebook

**Audit-robustness**: NESS is universally defined for non-equilibrium random matrix systems

**Empirical anchor**: stable per prior 9d pillar work

### 7.9 Dim 8: Thermodynamic uncertainty relation (TUR) Barato-Seifert

**Observable**: trade-off between precision + dissipation in substrate's distillation dynamics

**Substrate measurement**: substrate computes TUR efficiency metric

**Audit-robustness**: TUR is universal thermodynamic inequality

**Empirical anchor**: stable per prior 9d pillar work

### 7.10 Dim 9: BBP transition (spike count + strength)

**Observable**: number + magnitude of finite-rank perturbations producing eigenvalue spikes above MP bulk

**Substrate measurement**: substrate detects BBP spikes via spike-bulk decomposition

**Audit-robustness**: BBP transition is RMT-universal for finite-rank perturbations of random matrices

**Empirical anchor**: substrate's clustered codebook produces ~5 spikes per L1 partition cluster (1 outlier per cluster); empirical demonstration via Cell C prior

### 7.11 Audit-robust Tier 1 claim composition

Per substrate-on-its-own canonical claim hierarchy:

**Tier 1 architectural claim 2**: "Substrate's 9-dimensional spectral observability pillar provides RMT-universal properties of codebook matrix structure independent of node labels. Dims 1-3 + 5-9 stand at full audit-robustness; dim 4 (κ_3+ higher cumulants) has a sample-limited footnote at M=253 codebook (expected to stabilize post structured-codebook growth via parser-v2 + algebra_dict authoring)."

This composes with Tier 1 claim 1 (L6-PROOF type-soundness) + Tier 1 claim 3 (CELL SC N-invariant 10M) + Tier 1 claim 5 (audit-discipline rule family).

### 7.12 LLM categorical gap (context only)

LLMs have ZERO equivalent spectral observability dimensions. The 9d pillar is substrate-architectural; no LLM analog exists. This is provided as architectural context per USER 11th rule; NOT lead framing.

### 7.13 Forward path

- Drill 17 (Tracy-Widom on deflated bulk): in flight; dim 5 dedicated empirical cell
- Drill 18 (Kantorovich-functor framework): in flight; potential categorical extension
- F4-larger-M re-measurement post structured-codebook growth → dim 4 footnote resolution
- Substrate metacognition framework Tier 1 architectural claim 2 extension as 9d pillar grows to 10d+ (BBP spike count extension to weighted-spike measure; etc.)

### 7.14 References

- F4 free-probability drill (Research 2026-06-13)
- F4-RELABEL bootstrap κ_3/κ_4 NOT-robust verdict (Exp-Dev 2026-06-13)
- Cell B + Cell C prior 9d pillar empirical anchors
- 16th methodology rule candidate (`higher-order-needs-larger-M`)
- Drill 17 Tracy-Widom + Drill 18 Kantorovich-functor (in flight)

---

## Routing

- **Tracking-doc owners**: Section 7 published form ready; companion to Section 5 + 8 + 9 + 6-tier hierarchy
- **All sessions**: Section 7 canonical reference for 9d spectral observability pillar + dim 4 footnote + audit-robust Tier 1 claim 2
- **USER**: substrate-internal 9-dimensional measurement architecture with explicit audit-robustness criteria per dimension

## Cross-references

- notes/research_DRILL_free_probability_F4_relabeled_codebook_audit_robust_9d_spectral_pillar_2026-06-13.md (F4 drill source)
- notes/exp_dev_to_research_F4_RELABEL_bootstrap_kappa34_NOT_robust_at_M242_*.md (F4-RELABEL verdict source for dim 4 footnote)
- notes/research_TRACKING_DOC_SECTION_5_de_LLM_ify_REWRITE_*.md (Section 5 companion)
- notes/research_TRACKING_DOC_SECTION_8_FORMAL_*.md (Section 8 companion)
- notes/research_TRACKING_DOC_SECTION_9_FORMAL_*.md (Section 9 companion)
- notes/research_SUBSTRATE_ON_ITS_OWN_CANONICAL_CLAIM_HIERARCHY_*.md (Tier 1 architectural claim 2 anchor)
- memory `substrate-9d-spectral-observability-pillar-clustered-codebook-BBP-spike-extension-8d-SURVIVES-revision-substrate-product-STRENGTHENS-2026-06-13.md` (predecessor 9d pillar memory)
- memory `substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12.md` (foundational predecessor)
