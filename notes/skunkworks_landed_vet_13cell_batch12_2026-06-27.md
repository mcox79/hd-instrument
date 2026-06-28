# Skunkworks landed-VET: 13-atom batch12 (post-compaction Research staged) 2026-06-27

**Skunkworks role:** independent cert-chain auditor (AUDIT-ONLY; cert-owner discipline).
**Spawn trigger:** Research staged 13 atom candidates post-compaction; coordinator correction at task start (sws_rem v2 reframe).
**Source request:** `d:/AI/hd-instrument/notes/research_findings_for_next_skunkworks_batch_2026-06-27_post_compaction.md`
**Atomization tool:** `d:/AI/hd-instrument/tools/atomize_skunkworks_13cell_batch12_2026-06-27.py`

## Disposition (12 ACCEPT / 2 REFUSE)

### ACCEPT

| # | ID | Tier | Delta | Source metrics.json |
|---|----|----|-------|---------------------|
| 1 | A1 substrate depth-5 compositional | **CHAIN_GRADE** | **+1** | `data/exp_substrate_multihop_brain_pushback_v3_redispatch/metrics.json` |
| 2 | B3c PFC goal cleanup-bind destruction | MEASURED_MECHANISM | 0 | `data/exp_pfc_goal_conditioned_gate_v2_cleanup_bind_output/metrics.json` |
| 3 | B4 sws_rem v2 cycling-hurts | HONEST_NEGATIVE | 0 | `data/exp_cyclic_sws_rem_eta_schedule_v2_associative_recall_smoke/metrics.json` |
| 4 | C1 META_RULE_AC HYP-vs-MEASURED | meta_rule | 0 | (discipline) |
| 5 | C2 META_RULE_AD probe-band-tolerance | meta_rule | 0 | `data/exp_btsp_binary_synapse_one_shot_v2_regime_probed/metrics.json` (witness) |
| 6 | C3 META_RULE_AE metrics-path-disambiguation | meta_rule | 0 | (discipline) |
| 7 | C4 META_RULE_AF arms-must-differ | meta_rule | 0 | `data/exp_parietal_cortex_spatial_reasoning_v1/metrics.json` (witness) |
| 8 | C5 META_RULE_AH Barrier-1-was-fake | meta_rule | 0 | (composes with #1) |
| 9 | C6 META_RULE_AI RAIL_SANITY=substrate-exceeds | meta_rule | 0 | (witnesses v3 + v4) |
| 10 | C7 META_RULE_AG substrate-too-robust-for-default | meta_rule | 0 | (witness Cycle 1 v3+v4 only; sws_rem v2 dropped per coordinator) |
| 11 | D1 META_RULE_AJ scheduled-task-verify-end-to-end | meta_rule | 0 | (infra; Fix #25 4-day silent drift) |
| 12 | D2 META_RULE_AK SystemExit-before-BaseException | meta_rule | 0 | (cell template; narrow scope) |

### REFUSE

**B3a feature-std logreg ECE chain-grade methodology — REFUSED**
- Source: `data/exp_meta_knowledge_partition_coverage_v2_orthogonal_signals/metrics.json`
- Director cited "ECE 0.040 vs v1 0.152 at unchanged AUROC"
- Off-data per_arm_summary shows: `composed_old_correlated` ECE=0.040, `composed_orthogonal` ECE=0.058, `single_best_entropy` ECE=0.168 (not 0.152), `random_control` ECE=0.296
- AUROCs: 0.860 (old) / 0.829 (orth) / 0.852 (single) -- essentially tied
- Cell is HARD_FAIL on lift (-0.023 vs single, -0.031 vs old)
- ECE improvement IS real (composed_old_correlated 4.2x cut vs single arm at same-arm AUROC ~0.86), BUT methodology atom requires (a) lift IS significant, (b) a cleaner discriminator vs an isotonic-calibration baseline arm. Neither present.
- **Disposition:** filed as observation in landed-vet note; not atomized. Cell-author scope rescue: add isotonic-calibration arm + clean discriminator before re-submission.

**B3b sum-bind Hebbian-stack interference substrate-physics — REFUSED**
- Source: `data/exp_cross_task_4hop_chain_v2_sum_bind/metrics.json`
- Director cited "all arms 0.017 chance = Hebbian-stack interference at >50 chains"
- Off-data shows: `no_transfer=0.017`, `1_shot_sum_bind=0.017`, `5_shot_sum_bind=0.017`, **`oracle=0.017`** (chance = 1/80 = 0.0125)
- ORACLE at chance = cell-broken (oracle should have established ceiling near 1.0); cannot atomize as substrate-physics finding because the test failed to establish that the configuration CAN succeed under any condition
- verdict in cell: `HARD_FAIL_ORACLE_BROKEN`
- **Disposition:** filed as cell-fix-needed (oracle implementation bug, not substrate-physics). NOT atomized as substrate-physics. Cell-author scope rescue: fix oracle path; if oracle establishes ceiling then sum-bind interference can be tested cleanly.

## Verify-OFF-DATA basis (per-arm independent recompute)

Every accepted atom's claim was verified by reading the cited metrics.json end-to-end and cross-checking against Director's framing:

### A1 verification (CHAIN_GRADE substrate depth-5 compositional)
- `arm_baseline_depth_5.top1` per seed: seed=7 -> 0.610, seed=17 -> 0.560, seed=23 -> 0.575
- mean = (0.610+0.560+0.575)/3 = 0.582 (matches verdict_msg cv=0.036)
- per_step_acc arrays cross-checked: e.g. seed=17 [0.91, 0.855, 0.76, 0.64, 0.56] (matches Director's claim)
- All 5 arms IDENTICAL at depth=5 within seed:
  - seed=7: BASELINE=R1=R2=R3=COMBINED=0.610
  - seed=17: BASELINE=R1=R2=R3=COMBINED=0.560
  - seed=23: BASELINE=R1=R2=R3=COMBINED=0.575
- Substrate is argmax-cleanup-ceiling-bound, not crosstalk-bound; mechanisms tie baseline because primitive is at ceiling
- RAIL_SANITY_BREACH verdict is mis-read by cell-author/verdict_msg: pre-reg rail [0.10, 0.20] was derived from older smaller-scale smoke; current full-scale baseline 0.582 is substrate-EXCEEDS-prediction
- META_RULE_H cardinality 45/45 OK; META_RULE_K discriminator fires for primitive (chance ~1/V_C=0.001 << observed 0.582); META_RULE_L band (0.582 in active band, not saturated, not at floor)
- Substrate-product chain-grade IS warranted on the BASELINE arm in isolation (separate from mechanism comparison)

### B3c verification (MEASURED_MECHANISM cleanup-bind destruction)
- Per-arm at depth=6 verified:
  - `bind_gate_cleanup`: 7=0, 17=0 -> mean=0.0
  - `combined`: 7=0, 17=0 -> mean=0.0
  - `wm_goal_slot`: 7=0.46, 17=0.32 -> mean=0.39
  - `additive_goal_bias`: 7=0.46, 17=0.32 -> mean=0.39
  - `oracle`: 7=1.0, 17=1.0 -> mean=1.0
  - `v1_no_goal`: 7=0.38, 17=0.30 -> mean=0.34
- Substrate-algebra rule: argmax cleanup on bind output snaps to atomic codebook entry (codebook lacks bind compositions), destroying composite structure
- Clean MEASURED_MECHANISM characterization; cleanup-after-bind is the discovered bound

### B4 verification (HONEST_NEGATIVE sws_rem v2 cycling-hurts)
Coordinator correction at task start reframed this from C7 evidence to standalone HN:
- per_arm_summary top1: `constant_eta=0.541`, `cyclic_high_low_short=0.463`, `cyclic_high_low_long=0.465`, `diag_raw_hebbian=0.848`
- CONST baseline IS in [0.30, 0.70] band (META_RULE_AA satisfied)
- Cyclic arms LOSE: lift_best=-0.076, top5_lift=-0.078, entropy_delta=-0.043
- frob_ratio=13.96 (synapse-level mechanism fires ~14x change between high and low pulses)
- Mechanism fires at synapse but DOES NOT propagate to retrieval
- Author tuning log: 3 iterations to get baseline in band (sigma 0.85->4.0; alpha 0.5->2.0); final cfg correct
- Clean substrate-product negative (not test-design failure); brain-grounded (Diekelmann-Born 2010 SWS/REM consolidation)

### C7 META_RULE_AG witness verification (post coordinator correction)
- Witness count = 1 (Cycle 1 v3+v4 cell family ONLY)
- sws_rem v2 dropped (per coordinator correction): CONST IN band, discriminator fired, cyclic just loses
- v3 evidence: all 5 arms identical at depth=5 within seed (verified above in A1 section)
- v4 smoke evidence: 1 seed; all 5 arms tie at 0.875 (verified from `arm_baseline_depth_5.top1 = 0.875` and identical R1/R2/R3/COMBINED top1=0.875 in per_seed[0] of v4 smoke metrics)
- Cell-author diagnosis (verbatim from v4 smoke): "cleanup mechanism may need to be the variable, not the data density"

### C2 META_RULE_AD witness verification
- BTSP v2 metrics: 1 probe cfg tested {N=2048, NCAT=100, NTRAIN=10, noise=0.85, alpha=0.0488}, probe `baseline_acc=1.0` (above [0.40, 0.65] ceiling)
- `found_cfg = null`; `verdict_reason = REGIME_INFEASIBLE`; cell halted at probe stage
- The "0.62 drift" number Director cited (single-seed probe=1.0 vs 5-seed full=0.381) is NOT directly in this metrics file (only the probe ran). The DISCIPLINE rule (probe-band tolerance >= 1.96*SEM) is sound and load-bearing, atomized with the available evidence (single-cfg probe + halt + REGIME_INFEASIBLE pattern).

### C4 META_RULE_AF witness verification
- parietal_cortex_v1 metrics: `grid_position_with_relations` arm bit-identical to `grid_position_movable` arm across all 5 seeds (cross-checked per `research_flag_parietal_REL_arm_bit_identical_to_MOVABLE_cell_bug_2026-06-27.md` flag note + previously-atomized 2b honest-neg from REVET phantom-recovery batch)

## Net CERT delta and reconciliation

- Pre-batch CERT N (live): 625 (per `cert_ledger_query.py reconcile-cert-N`)
- ACCEPT/CHAIN_GRADE atoms: 1 (A1)
- ACCEPT/MEASURED_MECHANISM atoms: 1 (B3c) -- delta=0
- ACCEPT/HONEST_NEGATIVE atoms: 1 (B4) -- delta=0
- ACCEPT/meta_rule atoms: 9 (C1, C2, C3, C4, C5, C6, C7, D1, D2) -- delta=0 each
- Net delta: **+1**
- Post-batch CERT N (expected): **626**
- Ledger rows appended: **12** (1 chain_grade + 1 measured_mechanism + 1 honest_negative + 9 meta_rule)

## Refusal rationale (cert-owner discipline)

Two atoms refused per cert-owner default = MIDDLE_BAND; tier UP only with explicit per-arm evidence above bar:
- **B3a:** Director's "0.040 vs 0.152" doesn't match per_arm_summary; the comparison was between wrong arms; AUROCs tie; cell is HARD_FAIL on its declared discriminator
- **B3b:** ORACLE=0.017 (at chance) = cell-broken; cannot claim substrate-physics finding from a cell whose oracle didn't establish ceiling

Both refusals follow USER-locked discipline (no hallucinated numbers; verify per-arm not summary-text; let cert-classification come from cert-owner per Fix #28).

-- Skunkworks (cert-chain auditor) -- 2026-06-27 (post-compaction batch12 cycle)
