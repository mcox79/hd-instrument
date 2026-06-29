# Skunkworks HF Backlog Atomization (2026-06-27 verdicts) -- 2026-06-28

**AUDIT-ONLY landed-VET batch.** No new experiments dispatched. All cert_increment_delta=0 (cert-neutral; CERT N unchanged).

## Summary

- **Cells classified:** 25 (initially 24 in audit; v2_arm_count_fix + proper_import_guard handled together)
- **Math atoms appended:** 25 (to `data/substrate_index/math/atoms.jsonl`, 28723 -> 28748)
- **Meta cluster-amendment atoms appended:** 10 (to `data/substrate_index/meta/atoms.jsonl`, 255 -> 265)
- **Cert ledger rows appended:** 25 (to `data/substrate_index/meta/cert_ledger.jsonl`, 968 -> 993)
- **Cert delta total:** 0 (all delta=0)
- **A5 PRE/POST:** Store loads 177603 -> 177638 atoms (delta=+35, exact match)
- **Heartbeat:** touched 2026-06-29T01:09:41Z

## Disposition counts

- `honest_negative`: 5 (substantive negatives; mechanism characterized)
- `cert_ruling_dispatch_infra_failure`: 3 (runner died / OOM / missing manifest)
- `cert_ruling_test_design_failure`: 17 (cardinality breach / by-construction / NaN / setup exception / chain-gen under-yield / sanity breach)

## Cluster amendments (10)

| Cluster | n_cells |
|---|---|
| `edge_importance` | 7 |
| `substrate_multihop_brain_pushback` | 2 |
| `barrier1_M2_M3_M1_combined` | 2 |
| `cls_handoff_two_tier_BCM` | 1 |
| `edge_importance_NREM_modulated` | 1 |
| `kb_coarse_grain_anchor3_RC2_promotion` | 1 |
| `substrate_director_kb_v2_content_chunk` | 1 |
| `phase_diagram_capacity_multi_bank` | 1 |
| `phase_diagram_capacity_codebook_separated` | 1 |
| `kb_partition_by_source_class` | 1 |

## Per-cell verdict + tier (verified off-disk metrics.json)

### HONEST_NEGATIVE (5)

1. **swr_preplay_constructive_hypothesis_generator_v1_preview_fullN** (HF)
   - pipeline_top1=0.083 < 0.15 floor; ARM_PREPLAY recall@10=0.650 novelty=1.000 strong intra-arm; downstream pipeline collapses
   - Cluster: swr_preplay_constructive_hypothesis_generation
2. **edge_importance_v6_CFU_stronger_regime** (HF)
   - best v6 sel=+0.027 <= v5_baseline=+0.037; CFU LEAVE_K_OUT does NOT improve over canonical TRACE
   - Cluster: edge_importance
3. **edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix** (HF)
   - SURPRISE_NEGATIVE: TRACE cor=+0.060 << 0.30 drill claim (5x below); both v2 variants reproduce identical
   - Cluster: edge_importance
4. **substrate_director_kb_reingest_det_snapshot_isolated_v3** (HF)
   - smoke+full OK but content-vs-filename DISCRIMINATOR FAILED -- corroborates Skunkworks 2026-06-27 ruling that v2 content-KB tripwire was unverified
   - Cluster: substrate_director_kb_v2_content_chunk
5. **importance_ceiling_v7B_n_seeds_scale** (MIDDLE_BAND)
   - n_seeds=16 did NOT resolve cv=10.448; all readouts cluster near zero; TRACE=0.998 confirms substrate-encoding works for the encoding-control arm
   - Cluster: importance_ceiling_eight_readout_fisher

### DISPATCH_INFRA_FAILURE (3)

6. **substrate_multihop_brain_pushback_composition_v3_chain_gen_fix** (UNKNOWN -> INCOMPLETE)
   - 22/45 units completed; runner died mid-full-run (elapsed 43min); ties to 2026-06-28 SSH-disconnect-kill root cause
   - Cluster: substrate_multihop_brain_pushback
7. **phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu** (HF -- OOM)
   - GPU OutOfMemoryError on alpha=4.0 headroom=10x; n_units=0/3; composes with v2c chain_grade lower-alpha
   - Cluster: phase_diagram_capacity_multi_bank
8. **substrate_director_kb_remote_provision_v1** (HF)
   - Local manifest missing pre-condition; cell crashed in provisioning check before any test
   - Cluster: substrate_director_kb_provisioning

### TEST_DESIGN_FAILURE (17)

9. **self_explanation_deletion_fidelity_v1** (UNKNOWN -> IMPORT_CRASH)
   - AssertionError on setup invariant (argmax_idx=3 not 0); never ran
10. **substrate_multihop_brain_pushback_composition_v2_hardened** (UNKNOWN -> CRASHED)
    - Chain-gen yielded 0/200 chains (V=200 disallow=200 max_depth=8 over-constrained); v3 supersedes
11. **stage3_typed_routing_falsification_bijective_v1** (HF)
    - META_RULE_K self-detected by-construction-saturation (baseline=0.9991 >= 0.98); healthy self-check
12. **multihop_kbeam_pathsum_v1** (SANITY_BREACH)
    - Audit-flagged aggregation failure: depth-2 baseline 0.10 vs expected band [0.60, 0.70] (6x drift); main arms uninterpretable
13. **edge_importance_stratified_replay_baseline_diagnostic_v1** (HF)
    - META_RULE_H cardinality_ok breach (4 expected, 6 got); supersede by v2
14. **edge_importance_stratified_replay_baseline_diagnostic_v2** (NO_METRICS)
    - Bare-v2 supersede by v2_arm_count_fix + v2_proper_import_guard (substantive result tracked there as honest_negative)
15. **gap3_cls_two_tier_BCM_v2_init_fix** (HF)
    - BCM update overflows to float (numerical-stability); 1/12 units before crash
    - Extends CLS-handoff TWO_TIER cluster
16. **multihop_barrier1_M2_M3_M1_combined_5arm_v1** (HF)
    - Chain-gen under-yield (200/500 = 40%); V=200 max_depth=8 too tight
    - Extends Barrier 1 CLOSED-negative cluster
17. **multihop_barrier1_M2_M3_M1_combined_5arm_v2** (HF)
    - Even after V_C widening (200->500), enforce_distinct=True + disallow=320 still under-yields (180/200 = 90%)
    - Extends Barrier 1 CLOSED-negative cluster
18. **gap1_multihop_ldpc_rts_bidirectional_v1** (SANITY_BREACH)
    - Baseline_mean=0.3320 outside [0.125, 0.165] band (2x above); RTS HARD_PASS appears but uninterpretable
19. **phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels** (HF)
    - META_RULE_H cardinality (n_units=36 < expected=66); 30 units missing despite all-cap completed arms
20. **edge_importance_v3p2_trace_only_with_D1_audit_v1** (HF)
    - META_RULE_H cardinality (2 expected, 6 got); supersede by v2_arm_count_fix (MB)
21. **edge_importance_v3p2_trace_only_with_D1_audit_v2** (NO_METRICS)
    - Bare-v2 supersede by v2_arm_count_fix (MIDDLE_BAND: TRACE sel-rand=+0.083 PASS rec_retr, FAIL sel_unretr)
22. **edge_importance_v3_D1_alternative_discriminators_v1** (HF)
    - All D1_AUC=NaN across RAND/TRACE/ULTRA/COMP (numerical/init failure within 5ms); not a science result
23. **kb_partition_by_source_class_v3_self_contained** (HF)
    - v3_band_miss (ratio_resolved=0.14 vs 0.80 floor; ud_ret=0.21 vs 0.70 floor); v4_calibrated supersedes (chain-grade candidate)
24. **kb_coarse_grain_at_promotion_v4_with_ud_detection** (HF)
    - RC-2 invariant: n_atoms_full=4735 < 10000 scale-threshold; ANCHOR-3 RC-2 promotion path needs larger corpus
    - Extends ANCHOR-3 coarse-grain proven_bound cluster
25. **edge_importance_v4_NREM_replay_modulated_trace** (HF)
    - Fairness gate breached: cor(importance, |W|)=0.841 >> 0.30 threshold; mechanism secretly indexes via |W| not NREM-replay signal
    - Extends NREM proven_bound + edge_importance cluster

## Flagged (NO hidden chain-grade or MM)

After verifying every cited number off-disk against per_unit / arm_metrics / sanity-rails:

- **Zero cells reclassify as hidden chain-grade.** All HF and SANITY_BREACH verdicts hold under re-verification.
- **Zero cells reclassify as hidden MM.** importance_ceiling_v7B was already MB (atomized as honest_negative, cert-neutral consistent with prior policy).
- **One cell escalates substantive concern (already covered in directive):** substrate_director_kb_reingest_det_v3 corroborates that the load-bearing v2-vs-v1 content-discriminator does NOT pass. The 2026-06-27 ruling on content_chunk_smoke MM said "tripwire CLAIMED but NOT IN metrics"; now an isolated test confirms it FAILS. This is honest_negative with substantive implications for the substrate-Director-KB program (v2 content-KB value-add hypothesis is falsified at this implementation).

## A5 discipline observance

- **PRE-load gate:** PartitionedStore loads 177603 atoms clean before any write
- **Atomic write per partition:** tmp + os.replace; per-batch fresh load
- **Per-partition verify-load:** each appended file re-parsed JSON-valid line-by-line after os.replace
- **POST-load gate:** PartitionedStore re-loaded 177638 atoms; delta=+35 = exact (25 math + 10 meta)
- **No NULL-seam:** Store re-load clean; no partition truncation
- **Path-scoped:** no `git add -A`; only the three target partition files touched
- **Single-writer window:** no parallel Skunkworks in flight (confirmed by user)
- **Cell-author agents on local_cpu_queue (TASK_VECTOR v2 + Schema v3) do not touch substrate_index partitions** (verified -- they write to data/exp_* metrics dirs only)

## Cert-trail observability (HYBRID architecture compliance)

- All atoms written to canonical Store partitions (cert-record on disk)
- Cert ledger rows append to `meta/cert_ledger.jsonl` (queryable trail)
- This note filed (decision-grade summary; per-cell verdicts cited)
- Atomizer script preserved at `tools/skunkworks_atomize_2026-06-27_HF_backlog_24cell_2026-06-28.py` (reproducibility)

## Notes for Research (Director) / parent agent

- CERT N unchanged (583 headline holds per MEMORY.md; this batch is all cert-neutral)
- Cluster amendments densify the existing CLOSED-negative / proven_bound bodies of evidence; do NOT re-explore without a revival angle
- Two new revival angles surfaced:
  1. **substrate_director_kb content-discriminator failure** (kb_reingest_det_v3) -- the v2 content-KB value-add hypothesis needs a different implementation OR an honest re-statement that the current v2 still produces filename-metadata-equivalent retrieval
  2. **kbeam_pathsum + ldpc_rts SANITY_BREACH pattern** -- baseline regimes drifted from 2026-06-24 reference; suggests an upstream config/aggregation drift worth a separate audit
- Three dispatch-infra failures point to the same SSH-disconnect-kill root cause (per MEMORY.md 2026-06-28 fix); re-dispatching the v3 chain_gen_fix (22/45 units) should succeed under the new schtasks-lineage runner

-- Skunkworks (cert-owner / auditor), 2026-06-28
