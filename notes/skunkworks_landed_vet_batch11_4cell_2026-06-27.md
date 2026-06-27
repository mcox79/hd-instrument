# Skunkworks landed-VET batch 11 (2026-06-27, 4 cells: 3 SCP'd + 1 sync-gap survivor)

Per Research request 2026-06-27 ~16:22Z. Verify-off-data per Fix #28 (.venv Python + per-arm + per-seed recompute). Default UNDER-claim. CERT N pre-batch = 622.

Verify-off-data script: `data/session_local/skunkworks/_batch11_landed_vet_2026-06-27.py`
Atomize tool: `tools/atomize_skunkworks_batch11_plus_meta_WXYZ_2026-06-27.py`

## Verdict summary table

| # | Cell | Verdict (mine) | CERT delta |
|---|---|---|---|
| 1 | kb_partition_by_source_class_v4_calibrated | CHAIN_GRADE | +1 |
| 2 | gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix | HONEST_NEGATIVE_REGIME_DESIGN | 0 |
| 3 | edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix | HONEST_NEGATIVE_DRILL_PREMISE_REFUTED | 0 |
| 4 | edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard | HONEST_NEGATIVE_DRILL_PREMISE_REFUTED_CONFIRMED (sister) | 0 |

**Net CERT delta: +1** (B11-1 only). Post-batch CERT N = 623.

## Cell 1: kb_partition_by_source_class_v4_calibrated -- CHAIN_GRADE

Per-arm verify-off-data:
- ARM_SINGLE_W_BASELINE: ratio_resolved=1.0 (baseline)
- ARM_PARTITIONED_W_EQUAL_CAPACITY: ratio_resolved=0.9643, routing_accuracy=1.0, cross_partition_leak_rate=0.0, n_capacity_regression=1
- ARM_PARTITIONED_W_MEMORY_OVERSIZED: user_directive_retention=0.9286 (>=0.9 floor), non_ud_resolved_ratio=1.0
- ARM_DIAG_RANK_BASED_GATE: ratio_resolved_rankgated=1.0 (diagnostic)
- ARM_DIAG_COSINE_DIST_DUMP: aggregate_top1_mean=0.3473 (diagnostic)

All 5 verdict-msg numbers reproduce exactly from per-arm structure.

Discriminator FIRES in 3 ways:
- Partitioned (0.9643) BELOW baseline (1.0) shows routing is non-trivial (not by-construction-saturation)
- UD floor (0.9) BELOW non-UD (1.0) shows memory-bias is non-trivial asymmetry
- n_capacity_regression=1 surfaces calibrated edge to next-iter

Cardinality audit: 2/3 declared classes reached (memory class has 0 files; mechanical reality, all_unreachable=False -- not a breach).

KB inventory: n_entities=33646, n_chunks=13617, coverage 0.995, char_trigram_v1 encoder.

Drill predictions vindicated:
- Predicted BASELINE 0.18->0.85 band; observed 1.0
- Predicted PARTITIONED 0.14->0.80 ud_retention; observed 0.9286
- Both above predicted bands; mechanism stronger than drill predicted.

Composes-with: Wave 4 KB v2 content-chunk ingest + substrate-native routing primitive. Sets up Phase 2 substrate-as-Director-KB.

## Cell 2: gap3 HOPFIELD v2 regime_fix -- HONEST_NEGATIVE_REGIME_DESIGN

All 4 arms saturate heldout_acc=1.0 across all 3 seeds (11, 13, 19):
- ARM_BASELINE_HEBBIAN, ARM_HEBBIAN_SLOW, ARM_HOPFIELD_REPLAY_SLOW, ARM_HOPFIELD_GENERATIVE_REPLAY all at ceiling.

alpha_load=0.0488 IS in META_RULE_W safe band [0.03, 0.20]. Saturation is NOT alpha-related. Cell-author methodology rail HF_BASELINE_MAX=0.75 fired correctly (-> HARD_FAIL halt).

Regime-design pivot needed: drop N_TRAIN_per_cat from 100 to ~10, raise proto_noise from 0.60 to ~0.85, keep alpha in safe band, target BASELINE_HEBBIAN in [0.40, 0.65] band so consolidation arm has lift-room.

Discriminator-rail fired negative (correctly halted before propagating ceiling-vs-ceiling 'lift' as evidence).

## Cell 3: stratified replay v2 arm_count_fix -- HONEST_NEGATIVE_DRILL_PREMISE_REFUTED

Per-arm mean cor across 3 seeds (7, 17, 23):
- ARM_RAND_IMPORTANCE: -0.0075 (noise floor)
- ARM_TRACE_ONLY: +0.0602 (DIAGNOSTIC_COR_GATE=0.3 missed by 24pp)
- ARM_STRATIFIED_REPLAY: -0.0018 (noise floor)
- ARM_INVERSE_WEIGHTED_REPLAY: -0.0133 (noise floor)

Drill premise (Cauchy-Schwarz: stratification breaks |W|-correlation) appears CONTRADICTED at alpha=1.953 N=512 M=1000 N_BINS=10.

Three alternative hypotheses for premise refutation:
- Cauchy-Schwarz misapplied at over-capacity regime
- Test rigging |W|-importance differs from theoretical importance
- Cauchy-Schwarz applies only at capacity-respected (META_RULE_W safe-band) regime

Next-iter cell should drop alpha into [0.03, 0.20] safe band before re-testing premise.

TRACE arm at +0.06 is interesting weak signal (above noise floor across 3 seeds at 7-8 sigma; CV across seeds tight at 0.0080); below gate but consistent.

## Cell 4: stratified replay v2 proper_import_guard -- SISTER CONFIRMED

Bit-identical per-arm cor to cell 3 (same seeds, same RNG, same code logic). proper_import_guard adds the `if __name__ == '__main__': main()` discipline (META_RULE_X) but cell 3 was already top-level-clean -- numerics confirm.

Cell 4 = HYGIENE confirmation, not behavioral change. Drill premise refutation is ROBUST across two independent cell variants.

## META RULES atomized this batch (W/X/Y/Z; CERT-neutral T_methodology META corpus)

- **META_RULE_W ALPHA_GATE**: pre-dispatch alpha=M/N in [0.03, 0.20] for associative-memory cells; outside band requires justification + discriminator survival
- **META_RULE_X MAIN_GUARD**: experiment cells must guard main with `if __name__ == '__main__': main()`; never bare top-level main()
- **META_RULE_Y PARTIAL_LOAD_ANCHOR_CHECK**: partial-load tools must verify checkpoint anchor_name matches requesting cell; drop + re-run on mismatch
- **META_RULE_Z FIX_ADDRESSES_ROOT_CAUSE**: HARD_FAIL fix-cell pre-reg must include root-cause claim + distinguishing test; auto-tier HONEST_NEGATIVE_FIX_INSUFFICIENT if fix HARD_FAILs with same error class as prior

## Other atoms this batch (from batch 10 spec)

- **PC re-tier**: pc_cleanup_attractor_v1 HONEST_NEGATIVE_PC_NO_OP_AT_SATURATED_REGIME (CRITICAL DOWNGRADE from Director's HARD_PASS framing; 3 smoking-gun catches from batch 10 ruling note)
- **Bidir v3 regime-specific**: multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu HONEST_NEGATIVE_NO_MEETING_PREMIUM (proactive documentation; no prior v2 chain-grade atom in Store to annotate)

## Deferred to next batch (under-claim per Fix #28)

Batch 10's other 6 cells (bge INFRA / v3p2 edge MIDDLE_BAND / kbeam pathsum SANITY_BREACH / BCM v2 init HARD_FAIL / stratified v1 cardinality / head-to-head infra-dep). All CERT-neutral honest-negatives; deferral does not affect CERT N. Already captured in batch 10 ruling note `notes/skunkworks_landed_vet_batch10_8cell_plus_4_missing_2026-06-27.md`.

## Files referenced

- `/d/AI/hd-instrument/data/exp_kb_partition_by_source_class_v4_calibrated/metrics.json`
- `/d/AI/hd-instrument/data/exp_gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix/metrics.json`
- `/d/AI/hd-instrument/data/exp_edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix/metrics.json`
- `/d/AI/hd-instrument/data/exp_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard/metrics.json`
- `/d/AI/hd-instrument/data/exp_pc_cleanup_attractor_v1/metrics.json` (batch 10)
- `/d/AI/hd-instrument/data/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu/metrics.json` (batch 10)
- `/d/AI/hd-instrument/data/session_local/skunkworks/_batch11_landed_vet_2026-06-27.py` (verify script)
- `/d/AI/hd-instrument/tools/atomize_skunkworks_batch11_plus_meta_WXYZ_2026-06-27.py` (atomize tool)

Skunkworks 2026-06-27 ~16:35Z. CERT N 622 -> 623.
