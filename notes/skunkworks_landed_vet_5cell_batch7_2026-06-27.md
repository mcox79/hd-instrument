# Skunkworks landed-VET 5-cell batch 7 ruling note (2026-06-27)

**Auditor:** Skunkworks (cert-owner)
**Date:** 2026-06-27
**Scope:** 5 cells with metrics.json SCP'd back local (orchestrator a4c81115ef77f5d37)
**Mode:** verify-OFF-DATA via .venv Python independent recompute from each metrics.json
**Net CERT delta:** +1 (one chain-grade promotion)
**Atom count:** 6 (one cell yields 2 per-arm atoms per Fix #28 verify-per-arm discipline)
**Ledger rows appended:** 6 (1 chain_grade + 2 measured_mechanism + 3 honest_negative)

---

## Per-cell tier rulings

### [1] phase_diagram_wm_multibank_K_8192_3seed_harvest_v1 -> **CHAIN_GRADE (+1)**

Atom id: `math::T3/EXP_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1_CHAIN_GRADE_single_arm_MULTI_128x_k_per_bank_64_envelope_preserved_RAND_rec_1p0_cv_0p0_ADV_rec_0p9999_cv_0p0001_route_acc_1p0_KNN_sentinel_1p0_n_seeds_3_extends_K_4096_chain_grade_WM_to_K_8192_GPU_util_85_zero_LLM_calls`

Per-arm evidence (off-data from `detail.arm_stats`):
- 9/9 units, cardinality_ok
- RANDOM|MULTI_128x: rec_mean=1.0 cv=0.0 route_acc=1.0 per_seed=[1.0, 1.0, 1.0]
- ADVERSARIAL|MULTI_128x: rec_mean=0.9999 cv=0.0001 route_acc=1.0 per_seed=[1.0, 0.9998, 1.0]
- KNN sentinel: mean=1.0 per_seed=[1.0, 1.0, 1.0]
- GPU util mean=85.07 max=93.0 (real GPU work, not laptop spoof)
- 0 LLM calls; substrate-only OK
- Above-floor on every band (META_RULE_L), discriminator fires on adversarial regime (META_RULE_K), cardinality 9/9 (META_RULE_H), no silent except (META_RULE_J)

Composes with prior K=4096 chain-grade WM result; this is a 2x K-axis extension with k_per_bank=64 envelope preserved.

### [2] phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1 -> **MEASURED_MECHANISM (0)**

Atom id: `math::T3/EXP_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1_MEASURED_MECHANISM_substrate_envelope_mapped_at_30_units_...`

Per-arm evidence (off-data from `detail.surface`):
- 30/30 units, cardinality_ok
- 5/9 phase points hit rec=1.0 cv=0.0 (all unique_sr mode, alpha_VC <= 4.1)
- 4/9 collapse to 0.42-0.63 when codebook exhausted (mode flips to duplicates_allowed)
- Clear pattern: rec=1.0 iff (alpha_VC <= 4.1 AND keys_unique_mode=unique_sr)
- KNN_sentinel mean=0.3133 is BY-DESIGN bare baseline (n_queries=500, no Hebbian W); the cell's HARD_FAIL_KNN_SENTINEL verdict is **misleading** - HP gate mis-spec applied sentinel HP to bare-baseline arm

Cell's HARD_FAIL label demoted to MEASURED_MECHANISM by cert-owner because:
- Substrate envelope IS characterized (5 phase points at rec=1.0; clear collapse rule)
- HARD_FAIL was on mis-spec'd sentinel HP gate, not on substrate arms
- BUT: under-claim per Fix #28 - chain-grade promotion requires follow-up cell that separates pure-substrate envelope from codebook-exhaustion (V_C extended such that V_C * V_R > M_max always)
- Composes with codebook-exhaustion drill `notes/research_drill_capacity_envelope_3x_2026-06-27.md`

### [3] kb_dual_store_audit_v1 -> **HONEST_NEGATIVE_INFRA_DEP (0)**

Atom id: `math::T3/EXP_kb_dual_store_audit_v1_FULL_HARD_FAIL_KB_REFERENT_MISSING_pre_flight_verify_the_referent_gate_caught_0s_elapsed_...`

Per-arm evidence:
- elapsed_s=0.0, verdict_msg KB_REFERENT_MISSING
- Mechanism (dual-store determinism audit) NEVER exercised
- Pre-flight Fix #26 gate caught upstream KB dir missing (C:\dev\hd-instrument\data\exp_substrate_director_kb_ingest_v1\_arm_full\kb)

Same infra-dep class as the prior ANCHOR 1 v2 atom and Atom 4 below.
**Note**: The sister cell (Atom 5b) DID exercise the same shape of determinism check and confirmed non-determinism (w_l2_diff=1.7M).

### [4] kb_coarse_grain_at_promotion_v2_chain_grade_path -> **HONEST_NEGATIVE_INFRA_DEP (0)**

Atom id: `math::T3/EXP_kb_coarse_grain_at_promotion_v2_chain_grade_path_FULL_HARD_FAIL_KB_REFERENT_MISSING_...`

Per-arm evidence: identical to cell 3. v3 self-contained rescue already committed (2d551f9c) pending dispatch after hd_metrics_sync auto-push.

### [5] kb_content_chunk_ingest_v2_tripwire_surfaced -> **MIXED_RESULT (2 atoms; 0 net delta)**

#### [5a] ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST -> **MEASURED_MECHANISM (0)**

Atom id: `math::T3/EXP_kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST_MEASURED_MECHANISM_...`

Per-arm evidence:
- ok=True; banana_query_assertion_passed=True; elephant_query_assertion_passed=True
- Banana query: rank-1 cosine=0.6367 returns `elephant_filename.md` CONTENT about bananas; filename-only baseline `banana_filename.md` ranks 3rd at cosine=0.1455 (4.4x lower)
- Elephant query: rank-1 cosine=0.5850 returns `banana_filename.md` CONTENT about elephants; filename-only baseline `elephant_filename.md` ranks 3rd at cosine=0.1104 (5.3x lower)
- Tripwire fired in **both directions**; substantiates v2 content-KB claim

Under-claim to MEASURED_MECHANISM (not chain_grade) per Fix #28 because n=2 adversarial document pairs at one regime is thin; chain-grade requires n>=10 pairs + second regime (longer natural text) + cross-corpus generalization.

#### [5b] ARM_CHUNK_REINGEST_DET -> **HONEST_NEGATIVE_REPRODUCIBILITY (0)**

Atom id: `math::T3/EXP_kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CHUNK_REINGEST_DET_HONEST_NEGATIVE_REPRODUCIBILITY_VIOLATION_...`

Per-arm evidence (4 dims of breach):
- entities_byte_equal=False
- atoms_byte_equal=False
- w_l2_diff=**1694119.0** (tolerance 1e-6; massive structural breach not float noise)
- n_chunks_a=131074 vs n_chunks_b=131379 (305-chunk delta same-input)
- relations_byte_equal=True (only non-breach dim)

The determinism arm IS the discriminator and fired in the negative direction.
**Breaks no-lock-in principle** per `project_substrate_as_director_kb_dogfood_USER_2026-06-26.md`. Future Wave 5+ cells MUST fix this before chain-grade promotion of the pipeline.

Repair candidates (cell-author scope): freeze file-discovery order via sorted(os.listdir()); pin random seeds before W init; make chunker boundaries deterministic; re-run with w_tolerance=0.0.

---

## Cert-owner discipline notes (load-bearing)

1. **Verify off DATA not off VERDICT_MSG** - Cell 2's HARD_FAIL_KNN_SENTINEL label was misleading; per-arm read revealed the HP gate was mis-spec'd, and substrate arms cleanly characterize an envelope. Without per-arm verification this would have been a false-negative atomization.

2. **Verify-per-arm (Fix #28)** - Cell 5 is MIXED_RESULT: discriminator arm PASSED, determinism arm FAILED. Atomize separately so neither outcome contaminates the other's evidentiary trail.

3. **Default UNDER-claim** - Cell 5a discriminator could have been framed as PROVEN_BOUND (one-sided ceiling on filename-baseline outranking); under-claimed to MEASURED_MECHANISM because n=2 documents at one regime is thin.

4. **Sentinel HP gate hygiene** - Cell 2 illustrates a recurring failure mode: applying chain-grade HP gates to bare-baseline cross-validation arms inflates HARD_FAIL counts. Cell-authors should declare per-arm HP scope; cert-owner should verify gate scope before crediting HARD_FAIL as a mechanism failure.

5. **Infra-dep ladder hygiene** - 3 cells (3, 4, prior ANCHOR 1 v2) hit by same KB referent missing. The rescue pattern is consistent: **self-contained or pinned-snapshot dependency**, not externally-materialized side-output dependency.

---

## Composes-with chain

- Atom 1 (K=8192 chain-grade) composes with prior K=4096 chain-grade WM result
- Atom 2 (envelope MM) composes with drill at `notes/research_drill_capacity_envelope_3x_2026-06-27.md`
- Atoms 3, 4 in same infra-dep family as prior ANCHOR 1 v2 atom; share rescue pattern
- Atoms 5a, 5b are per-arm split of same cell; reference each other via sister_atom metadata

---

## Atomization script

`d:/AI/hd-instrument/tools/atomize_skunkworks_5cell_batch7_landed_vet_2026-06-27.py`

Run order: DRY first; verify counts match this ruling; then `--apply`.

A5-gated writes with per-window PRE/POST cert count verification + ledger append.
