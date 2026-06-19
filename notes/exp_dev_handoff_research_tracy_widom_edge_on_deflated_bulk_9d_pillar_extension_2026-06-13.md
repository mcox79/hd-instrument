# exp_dev hand-off -- research: Tracy-Widom edge on deflated bulk (9d pillar dim-5 verification)

Filed-by: research
Filed: 2026-06-13
Trigger: F4 free-cumulant 2x drill identified Tracy-Widom edge as next-drill candidate after F4-RELABEL kappa_3/kappa_4 NOT-robust at M=242; cheap CPU-only verification cells designed.
Source: d:/AI/hd-instrument/notes/research_DRILL_tracy_widom_edge_on_deflated_bulk_substrate_9d_pillar_extension_2026-06-13.md
Pause state: check d:/AI/hd-instrument/data/orchestrator_paused.flag before ship

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides anchor pointers + substrate-product reading + tier hints + why-now signals only. Exp_dev owns the actual experiment design (envelope-fail-bands, smoke gate, queue_add, REMOTE VERIFY, formula-selftests).

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): CELL-TW-DEFLATE-1 production-M Tracy-Widom edge KS test
  - **Anchor pointer:** clustered codebook Gram matrix at production M; top-k spike deflation where k = L1 partition cluster count from parent 9d pillar; Johnstone-Ma 2012 rescaling; KS test vs GOE-Tracy-Widom CDF (TracyWidom Python package or Bornemann spectral)
  - **Substrate-product reading:** if HARD-PASS, 9d pillar dim-5 moves from "structural artifact drafted" to "empirically verified KS p >= 0.10 vs tabulated GOE-TW1 CDF"; audit-robust claim 2 strengthens from RMT-universal narrative to checkable observability number; LLM categorical gap widens (LLMs have no deflatable spectral object)
  - **Tier hint:** Tier 1 architectural (foundational substrate observability)
  - **Why-now:** F4-RELABEL leaves kappa_3/kappa_4 dim-4 NOT-robust at M=242; need 9d pillar's 2nd-order edge dimension verified to backfill; scaffold-positioning pivot needs quantitative observability proof point
  - **Pre-reg numeric thresholds:**
    - HARD-PASS: KS p >= 0.10 vs GOE-TW1 CDF AND mean(W) within +/- 0.10 of -1.2065 AND var(W) within +/- 0.15 of 1.6078 AND skew(W) within +/- 0.20 of 0.2935
    - HARD-FAIL: KS p < 0.01 at >= 500 realizations OR mean(W) deviation > 0.30 OR KS p monotone-DECREASING with sample size OR visible 2nd mode in W histogram
    - MIDDLE_BAND: KS p in [0.01, 0.10] with first-three-moments within tolerance -> rerun at 2000 realizations as TW-DEFLATE-1-confirm

### Anchor 2 (CROSS-CHECK): CELL-TW-DEFLATE-2 sub-production-M convergence-direction check
  - **Anchor pointer:** same protocol at smaller M (substrate codebook variant in test harness)
  - **Substrate-product reading:** confirms TW-DEFLATE-1 PASS is asymptotic-regime convergence, not coincidence at one M; monotone direction (smaller M -> smaller KS p) rules out structural deviation
  - **Tier hint:** Tier 1 architectural (companion verification)
  - **Why-now:** Ma 2012 warned Wishart-TW convergence is slow at small d,M; need 2-point convergence curve before claiming asymptotic regime
  - **Pre-reg threshold:** TW-DEFLATE-2 KS p < TW-DEFLATE-1 KS p (correct finite-N direction); HARD-FAIL if reversed

### Anchor 3 (NULL CONTROL): CELL-TW-DEFLATE-3 flat-MP baseline KS test (no deflation)
  - **Anchor pointer:** unclustered MP-baseline codebook (substrate-internal flat Wishart); apply same KS-vs-TW1 test WITHOUT deflation
  - **Substrate-product reading:** demonstrates KS-test machinery is well-calibrated on canonical-case substrate; rules out "test rejects everything" tooling artifact; provides confidence that any HARD-PASS in TW-DEFLATE-1 is real positive evidence, not Type-II error
  - **Tier hint:** Tier 0 (verification scaffolding)
  - **Why-now:** 10th methodology rule (verify-before-asserting) requires null-control before claiming TW-DEFLATE-1 result
  - **Pre-reg threshold:** TW-DEFLATE-3 must HARD-PASS its own KS-vs-TW1 test (KS p >= 0.10); if it FAILS, tooling is broken and TW-DEFLATE-1 result is uninterpretable regardless of outcome

## Context pointers (file paths, not summaries)

  - Research source note: d:/AI/hd-instrument/notes/research_DRILL_tracy_widom_edge_on_deflated_bulk_substrate_9d_pillar_extension_2026-06-13.md
  - Predecessor F4-RELABEL audit-robust drill: d:/AI/hd-instrument/notes/research_DRILL_free_probability_F4_relabeled_codebook_audit_robust_9d_spectral_pillar_2026-06-13.md
  - Predecessor F2 Tracy-Widom 2x drill: d:/AI/hd-instrument/notes/research_drill_free_probability_F2_tracy_widom_edge_fluctuations_substrate_observability_2x_2026-06-12.md
  - Predecessor clustered-codebook spectral characterization: d:/AI/hd-instrument/notes/research_drill_clustered_codebook_spectral_characterization_8d_pillar_revision_for_clustered_case_F4_Cell_B_negative_2x_2026-06-13.md
  - F4 saturation + 8d pillar complete: d:/AI/hd-instrument/notes/research_to_testbed_exp_dev_2_DRILLS_VERDICT_F4_kappa_4_SATURATION_8d_pillar_COMPLETE_plus_CURRY_HOWARD_substrate_IS_simply_typed_fragment_USER_GOAL_ALIGNED_2026-06-12.md
  - 9d pillar memory (parent): C:/Users/marsh/.claude/projects/d--AI/memory/substrate_9d_spectral_observability_pillar_clustered_codebook_BBP_spike_extension_8d_SURVIVES_revision_substrate_product_STRENGTHENS_2026-06-13.md
  - Audit-robust canonical claim synthesis: d:/AI/hd-instrument/notes/research_DRILL_audit_robust_canonical_claim_synthesis_what_survives_INV1_2_3_full_HARD_FAIL_minimal_defensible_substrate_position_2026-06-13.md
  - Scaffold positioning pivot (CRITICAL): d:/AI/hd-instrument/notes/research_DRILL_substrate_as_verifiable_LLM_scaffold_positioning_strategic_pivot_analysis_2026-06-13.md
  - 10th methodology rule (verify-before-asserting): C:/Users/marsh/.claude/projects/d--AI/memory/substrate_methodology_rule_verify_before_asserting_5_class_cluster_cycle_51_F4_CH_P6_P4_smoke_GHRR_all_caught_before_report_2026-06-13.md
  - 16th methodology rule candidate (higher-order spectral less robust): see audit-pattern reference in research_to_exp_dev_F4_RELABEL_kappa34_NOT_ROBUST_M242_ACK note
  - cap_map (current state): d:/AI/hd-instrument/notes/substrate_capability_map.md

## Operational recipe (sketch, exp_dev owns final form)

  - Library candidates: numpy/scipy for linalg + KS test; TracyWidom Python package (pip install TracyWidom) for tabulated TW1 CDF; alternative: Bornemann (2010) "On the numerical evaluation of distributions in random matrix theory" spectral-method implementation if package unavailable.
  - Rescaling: Johnstone-Ma 2012 improved centering/scaling constants (see source note section g for formulas).
  - Deflation: numpy.linalg.eigh -> identify top-k spikes -> subtract sum(lambda_i * v_i v_i^T) -> re-eigendecomp residual -> take new top eigenvalue lambda_1^(deflated).
  - KS test: scipy.stats.kstest(W_samples, TW1.cdf) -- returns statistic and p-value directly.
  - Realization counts: TW-DEFLATE-1 = 500 (primary), 2000 (confirm if MIDDLE_BAND); TW-DEFLATE-2 = 1000; TW-DEFLATE-3 = 500.
  - Wallclock budget: ~30 min TW-DEFLATE-1; ~45 min TW-DEFLATE-2; ~20 min TW-DEFLATE-3. Total ~1.5 hr CPU local.

## Contract

  - Exp_dev owns: envelope-fail-band registration, smoke gate, queue_add.sh ship, REMOTE VERIFY, self-test per formula-selftests, choice of TW1 CDF source (TracyWidom package vs Bornemann), choice of deflation implementation (eigh-subtract vs Lanczos restart)
  - Research provides: KS-vs-TW1 protocol + Johnstone-Ma rescaling + sample-size guidance + threshold pre-reg (this note) + 11 citations
  - Strategy owns: cap_map row bump on verdict (9d pillar dim-5 status field)
  - Verdict_handler owns: post-verdict synthesis (HARD-PASS importance = HIGH; HARD-FAIL importance = HIGH because 9d pillar would lose dim-5 and audit-robust claim 2 would weaken)
  - Pause-gated: yes; check data/orchestrator_paused.flag before ship

## Autonomy declaration

Exp_dev decides:
  - Implementation language (Python expected) and library choices
  - Whether to ship all 3 cells in one shot (recommended; total ~1.5 hr CPU) or split TW-DEFLATE-3 (null control) as gating smoke before TW-DEFLATE-1+2
  - Whether to use TracyWidom Python package (preferred, simpler) or Bornemann spectral method (more authoritative)
  - Whether to add a TW-DEFLATE-4 "doubled-realization" pre-emptive confirm if local CPU has free time after the primary 3 cells
  - Whether to report mean/var/skew of W in addition to KS statistic (recommended; gives independent moment-matching evidence)
  - Random seed strategy across cells

Research does NOT decide: which queue (local CPU expected), runner identity, REMOTE VERIFY recipe, smoke-gate threshold values.
