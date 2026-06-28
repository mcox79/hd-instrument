# exp_dev verdict: pfc_wm_state_tracker_v1 smoke HARD_FAIL all 3 adapters

**Date:** 2026-06-28
**Cell:** `substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7`
**Run:** smoke (N=8192 V_C=4000 d=15 psz=800 n_chains_test=100, single seed)
**Metrics:** `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/metrics.json`
**Pre-reg:** `d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_pfc_wm_state_tracker_v1.md`

## Verdict

**HARD_FAIL_ARMS_TIED (trips first; HARD_FAIL_ALL_ADAPTERS_DEAD also satisfied)**

All 3 dlPFC-WM-state-tracker adapter sub-mechanisms hit top1=0.0000 at depth=15. 4-primitive brain-faithful composition CLOSES (drill Rank 2 dead per pre-reg HARD_FAIL band).

## Per-arm metrics (seed=7 smoke; n_chains_test=100)

| Arm | top1 | per-hop part-acc h5/h10/h15 | adapter verdict |
|---|---|---|---|
| A BASELINE | 0.4000 | n/a | rail_ok (target 0.449; MEASURED@v5 0.39) |
| B PATH2_PER_CHAIN | 0.0100 | 0.20 / 0.20 / 0.24 | reproduces today's HARD_FAIL (MEASURED@PATH2 0.01) |
| C_SUB_A PRIOR_MODULATION | 0.0000 | 0.19 / 0.12 / 0.23 | out_of_band; per-hop part-acc BELOW chance |
| C_SUB_B FAKE_EVIDENCE | 0.0000 | 0.22 / 0.18 / 0.23 | out_of_band; near-chance partition pick |
| C_SUB_C STATE_CONDITIONED | 0.0000 | 0.22 / 0.18 / 0.23 | out_of_band; IDENTICAL to SUB_B |
| D ORACLE_PER_HOP | 0.8400 | n/a | upper bound (MEASURED@v5 0.84) |
| E RANDOM | 0.0000 | n/a | floor (matches PATH 2 RANDOM_F=0.00) |

**arms_must_differ_sha256:** SUB_B and SUB_C produced IDENTICAL hashes (`c6217c981403fdd3`) — `arms_distinct=False` trips the META_RULE_AF gate FIRST.

## Adapter winner

**None.** All 3 adapters HARD_FAIL by the per-adapter spec:
- top1=0.00 <= HF_ADAPTER_ABS=0.30 (all 3)
- lift_over_B=-0.01 < HF_ADAPTER_LIFT_OVER_B=0.10 (all 3)
- per-hop part-acc never reaches HP_PER_HOP_PARTACC=0.50 (all 3)

## Dispatch decision

**NO FULL DISPATCH.** Per `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`, the discriminator failed at smoke (full-N=8192 + full-depth=15; only reduced n_chains_test=200->100). Full run on remote_cpu_queue would burn ~3 hours per seed × 3 seeds = 9 hours for the same HARD_FAIL. Smoke is definitive.

## Diagnostic: why all 3 adapters died

Root cause is structural, not parameter-tuning:

The `schema-to-partition` map `cluster_to_target_part[k]` is computed in `build_schema_prototypes` from **first-hop targets only**:
```
member_parts = [chains_train[ci][0][2] // PART_SIZE ...]
```
So every schema cluster `k` maps to the HOP-0 target partition of its training chains. State-context bias from WM (SUB_A/B/C) can shift WHICH cluster fires per hop — but ALL clusters' partition outputs encode HOP-0 partitions, not per-hop trajectory partitions. Per-hop partition-acc therefore caps at ~1/N_PARTS = 0.20 = chance.

This is the drill's "most likely failure mode P=0.45": *state-conditioning injection isn't load-bearing because the schema-Bayes posterior collapses after 1-2 hops*. The drill correctly identified that schema-Bayes is **too coarse for per-hop discrimination at depth 15**.

SUB_B === SUB_C identical hashes: at the argmax-over-clusters operation, `(q_hop + w*wm_state)` (SUB_B with harmonic decay) and `(sum_{j<=i} R[p_j] + wm_state)` (SUB_C) reduce to the same effective query at the partition-vote stage when both pickers route through `cluster_to_target_part`.

## M3 implication (per pre-reg)

**4-primitive brain-faithful composition closes.** M3 needs different mechanism class. Drill Rank 3 fallback options:
1. Per-state schema selector (5th primitive class; Sutton-Precup analog — drill closed this as needing per-state-trained policies)
2. External cortex layer (non-brain-faithful)
3. Re-design schema-Bayes primitive to output PER-HOP partition (rather than hop-0-only)

Option 3 is structurally the highest-value direction — the existing primitive is the bottleneck, not the WM-bank state-tracker.

## Files filed

- Pre-reg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_pfc_wm_state_tracker_v1.md`
- Cell sibling seed_7: `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7.py`
- Cell sibling seed_13: `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_13.py`
- Cell sibling seed_19: `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_19.py`
- Smoke metrics: `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/metrics.json`
- Smoke stdout: `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke_stdout.log`

Siblings seed_13 + seed_19 are **filed but NOT dispatched** (per HARD_FAIL smoke).

## Cardinality / discipline

- cardinality_ok=True (expected_units=7 observed_units=7)
- arms_distinct=False (SUB_B = SUB_C SHA-256 collision)
- saturated_any=False
- baseline_rail_ok=True (A=0.40 in [0.05, 0.95])
- ORACLE_D=0.84 > all adapters (upper bound sanity)
- E < HP_RANDOM_CEIL=0.05 (E=0.00 floor sanity)
- pause flag absent at dispatch time
- META_RULE_AC/AE/AF/AG/AH/AL/AN/AP/H tags applied
- zero LLM calls during inference (_llm_forward_calls_at_inference=0)
