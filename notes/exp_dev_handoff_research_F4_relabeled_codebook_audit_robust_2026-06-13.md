# exp_dev hand-off — research: F4 free-cumulant relabeled-codebook audit-robust 9d spectral pillar

Filed-by: research:opus
Date: 2026-06-13
Trigger: drill delivery at notes/research_DRILL_free_probability_F4_relabeled_codebook_audit_robust_9d_spectral_pillar_2026-06-13.md
Pause state: respect data/orchestrator_paused.flag — if pause active, file this hand-off but do NOT queue_add.

Per [[feedback-no-experiment-design-in-prompts]]: experiment design lives in exp_dev's autonomy. The cells below are CANDIDATES with reading; exp_dev chooses the smoke-gate framing, the seeds, the budget, and the per-cell config.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): CELL F4-RELABEL-WITHIN

- **Anchor pointer**: F4 free cumulants kappa_3, kappa_4 on production codebook under N=100 WITHIN-CLUSTER relabelings.
- **Substrate-product reading**: PASS validates the within-cluster invariance corollary of Voiculescu's theorem on the clustered codebook; provides direct evidence that 9d pillar's higher-cumulant dimensions are reading eigenvalue STRUCTURE not atom LABELS.
- **Tier hint**: tier-1 (free-probability anchor, 100% yield, scope-expansion eligible).
- **Why-now**: closes audit-robust claim 2 of the 9d pillar; cheap (~15 min CPU); pairs with existing Cell C spike deflation protocol.
- **Pre-reg bands (suggested)**: HARD-PASS SE(kappa_3)/|kappa_3| <= 0.05 AND SE(kappa_4)/|kappa_4| <= 0.05; HARD-FAIL SE/|kappa| > 0.20.

### Anchor 2 (SECONDARY): CELL F4-RELABEL-CROSS

- **Anchor pointer**: same as Anchor 1 but CROSS-CLUSTER (uniform-random) relabelings on spike-deflated bulk (top-12 eigenvalues deflated first per 9d Cell C protocol).
- **Substrate-product reading**: PASS validates the strong audit-robust claim that 9d pillar is unitary-invariance-equivalent in practice; FAIL with within-cluster PASS becomes new methodology rule "deflation required for cross-cluster cumulant comparability."
- **Tier hint**: tier-1.
- **Why-now**: pairs naturally with Anchor 1 (same codebook load, same compute path).
- **Pre-reg bands (suggested)**: HARD-PASS SE/|kappa| <= 0.10 on deflated bulk; HARD-FAIL SE/|kappa| > 0.30.

### Anchor 3 (DIAGNOSTIC): CELL F4-BLOCK-LEAKAGE-INDEX

- **Anchor pointer**: ratio SE_cross / SE_within for kappa_3 and kappa_4, computed from Anchors 1 and 2 outputs (no new sampling).
- **Substrate-product reading**: defines a NEW observable — the block-leakage index — quantifying how much cluster structure is in higher cumulants. Candidate Dimension-10 of the spectral observability pillar.
- **Tier hint**: tier-1 (definitional, near-zero compute, leverages Anchors 1+2).
- **Why-now**: substrate-novel metric, derives at no extra cost.
- **Pre-reg bands**: descriptive — report the ratio; no pass/fail until calibration on multiple codebook versions.

## Context pointers (file paths, not summaries)

- notes/research_DRILL_free_probability_F4_relabeled_codebook_audit_robust_9d_spectral_pillar_2026-06-13.md (this drill)
- notes/substrate_9d_spectral_observability_pillar_clustered_codebook_BBP_spike_extension_8d_SURVIVES_revision_substrate_product_STRENGTHENS_2026-06-13.md (9d pillar definition + Cell C deflation protocol)
- notes/substrate_CELL_SC_HARD_PASS_VSA_partition_routing_survives_10M_N_invariant_existential_validation_categorical_gap_widens_at_scale_2026-06-13.md (12-archetype block structure used here = L1 categorical clustering used in Cell SC)
- hdlab/ (codebook loader path — exp_dev to resolve canonical fixture)
- verification/theory.py (sample-moment-to-free-cumulant inversion oracle if exp_dev wants to implement from scratch)

## Contract section

- Experiments are LOCAL CPU only (no GPU required); ~30 min budget for all three cells.
- Pause-flag check before queue_add per usual.
- Atomic write (.tmp + rename) for any verdict notes.
- Smoke-gate per envelope-fail-bands: any cell with within-cluster SE > 0.20 must pause and re-check oracle, not proceed.
- REMOTE VERIFY post-ship per standard protocol.
- Self-test per formula-selftests: the sample-moment estimator m_n = (1/N) trace(W^n) should match the textbook free moment-cumulant inversion to within 1e-6 on a synthetic Wigner matrix; verify before running on production codebook.

## Autonomy declaration

exp_dev chooses:
- Seed strategy (single seed vs ensemble across seeds).
- Whether to ship all 3 anchors in one cycle or split.
- The specific moment order to estimate (text suggests m_1..m_8 for kappa_3, kappa_4; exp_dev may extend to kappa_5, kappa_6 if budget allows).
- Smoke-gate proxy if N=100 relabels is too costly (e.g., N=20 smoke first).
- How to deflate the top-12 eigenvalues (eigendecomposition vs power-iteration vs SVD truncation).
