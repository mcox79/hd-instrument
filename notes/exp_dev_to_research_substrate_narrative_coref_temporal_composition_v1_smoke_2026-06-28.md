# exp_dev -> research: composition v1 smoke result + Q2 ANCHOR 2 trigger

**Filed:** exp_dev 2026-06-28
**Cell:** `experiments/exp_substrate_narrative_coref_temporal_composition_v1.py`
**Prereg:** `preregs/2026-06-28_substrate_narrative_coref_temporal_composition_v1.md`
**Driving handoff:** `notes/exp_dev_handoff_research_drill_long_narrative_coref_temporal_2026-06-28.md`
**Smoke metrics:** `data/exp_substrate_narrative_coref_temporal_composition_v1_smoke/metrics.json`

## TL;DR honest split outcome

Smoke ran at FULL N (100 events / 5 chars / 8 pronouns / Q_per_type=3) single-seed=7 per DISCRIMINATOR-MUST-SURVIVE-SCALE Check A.

- **Q3 sequence-replay: RESCUED** (HARD_PASS across all 6 diagnostic seeds; 1.000 vs naive 0.000-0.333; lift +0.667 to +1.000)
- **Q2 partition-oracle: NOT RESCUED** (identical-or-worse vs naive across all 6 diagnostic seeds; mean ~0.17 vs naive 0.22)
- **Composition arm: MIDDLE_BAND** (Q3=1.000 inherits replay rescue; Q2=0.667 inherits naive seed=7's accidental high)

Smoke verdict = MIDDLE_BAND on seed=7 (Q2 lift 0.000 < HP_LIFT 0.30). Cross-seed diagnostic (synchronous run) reproduces the drill's Q2=0.22 naive-baseline EXACTLY across seeds {11,13,17,19,23}.

## Per-arm metrics at smoke seed=7 (full-N regime)

| Arm | Q1 | Q2 | Q3 | Q4 | overall | pred_sha |
|---|---|---|---|---|---|---|
| ARM_RANDOM_FLOOR | 0.000 | 0.000 | 0.333 | 0.000 | 0.083 | 50b7ab468291d1b4 |
| ARM_NAIVE_MAGNITUDE | 1.000 | 0.667 | 0.333 | 0.667 | 0.667 | b5dbb33427f0e828 |
| ARM_PARTITION_ORACLE_ONLY | 1.000 | 0.667 | 0.333 | 0.667 | 0.667 | b5dbb33427f0e828 |
| ARM_SEQUENCE_REPLAY_ONLY | 1.000 | 0.667 | **1.000** | 0.667 | 0.833 | 379fa8f903641262 |
| ARM_COMPOSITION | 1.000 | 0.667 | **1.000** | 0.667 | 0.833 | 379fa8f903641262 |

Arms-distinct: 3 distinct SHAs at seed=7 (oracle==naive, composition==replay). Cross-seed shows oracle DOES differ from naive on seed=13 (oracle 0.000 vs naive 0.333), so arms are distinct as a population. seed=7 lands on a collision.

## Cross-seed diagnostic (6 seeds full-N)

| seed | naive_Q2 | oracle_Q2 | naive_Q3 | replay_Q3 |
|---|---|---|---|---|
| 7  | 0.667 | 0.667 | 0.333 | **1.000** |
| 11 | 0.000 | 0.000 | 0.000 | **1.000** |
| 13 | 0.333 | 0.000 | 0.333 | **1.000** |
| 17 | 0.000 | 0.000 | 0.333 | **1.000** |
| 19 | 0.333 | 0.333 | 0.000 | **1.000** |
| 23 | 0.000 | 0.000 | 0.000 | **1.000** |
| **mean** | **0.222** | **0.167** | **0.167** | **1.000** |

Naive_Q2 mean 0.222 EXACTLY matches drill's reported 0.22 from the prior cell — composition cell faithfully reproduces today's HARD_FAIL when wired naively. Q3 replay-decoder HARD_PASS across all 6 seeds confirms `c3_compressed_sequence_replay K=20` primitive rescues Q3 in the narrative regime.

## Why Q2 partition-oracle did NOT rescue (honest)

Drill anticipated this exactly:

> "the partition oracle was validated at V_C=4000 with anchor projections; today's cell uses V_C ~= N_JOBS + N_OBJ ~= 50. The oracle's discriminator may not survive at small-V_C / few-per-partition regime"

Confirmed: at V_C ~ 50 the substituted-cue partition magnitude readout is noisier than the unsubstituted-cue magnitude readout from the prior cell. The "oracle" version's per-character substituted-cue magnitude does not separate the true referent's partition response from other partitions' baseline response at this V_C scale (each partition has 3-15 events; not enough Hebbian density for discriminating magnitudes against substituted cues).

## Functional-requirement table (pre-reg, smoke verified)

| Q | Functional req | Chain-grade primitive | Readout path engaged | Smoke result |
|---|---|---|---|---|
| Q1 | retrieve fact_val | cortex Hebbian | argmax over jobs vocab | 1.000 (pass) |
| Q2 | track entity + disambig pronoun | partition_oracle_v5 (ORACLE_C=0.97 @ V_C=4000) | substituted-cue per-partition magnitude argmax | **0.167 mean (FAIL @ V_C~50; ANCHOR 2 needed)** |
| Q3 | retrieve event at time | c3_compressed_sequence_replay K=20 | S = sum_{scene} outer(k_prev, k_curr) / N; pred = argmax cosine(S@k_target) | **1.000 (chain-grade RESCUE confirmed across 6 seeds)** |
| Q4 | latest fact wins | TWO_TIER gen_W | latest_val lookup | 0.667 (pass) |

## What I'm NOT doing + why

Per DISCRIMINATOR-MUST-SURVIVE-SCALE + USER 2026-06-26 directive + drill autonomy declaration:

- **NOT dispatching 3 full chunks (seeds 11/13/23) to remote_cpu_queue.** Smoke at full-N is already the discriminator preview Check A; the 6-seed diagnostic above gave the cross-seed answer (Q3 unanimous HARD_PASS; Q2 unanimous HARD_FAIL_AT_V_C_50). Dispatching full would burn 90 CPU-min reconfirming what's already known.
- **NOT triggering ANCHOR 3** (K_SCENE alignment) — replay decoder unanimously HARD_PASSes at current K_SCENE=10.
- **TRIGGERING ANCHOR 2** (V_C sweep) per drill autonomy: file research-drill for `exp_substrate_narrative_partition_oracle_capacity_V_C_sweep_v1` — sweep V_C in {50, 200, 1000, 4000} on the 100-event narrative; expected curve = monotone Q2 lift with V_C.

## ANCHOR 2 spec sketch (for next exp_dev cycle or research drill confirmation)

Sweep V_C dimension (size of fact/entity vocabulary per partition) by expanding `N_JOBS` + `N_OBJECTS` so each char's partition gets more candidate facts:

- V_C ~ 50  (current: N_JOBS=8, N_OBJ=16, +scene tags ~28 effective)
- V_C = 200 (N_JOBS=50, N_OBJ=150)
- V_C = 1000 (N_JOBS=250, N_OBJ=750)
- V_C = 4000 (N_JOBS=1000, N_OBJ=3000)

Expected (per oracle's MEASURED@`exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json`): partition oracle's Q2 monotone lift with V_C; HARD_PASS at V_C >= 1000.

If the curve doesn't lift, the partition router's mechanism doesn't transfer to narrative-coref task design and we need a different Q2 primitive (HRR context-bind disambiguator per `contextual_encoding_hrr_binding_smoke_v1` HARD_PASS WSD=1.000).

## Reported HARD_PASS that DID land (Q3)

Q3 `c3_compressed_sequence_replay` decoder rescue is the load-bearing positive science result of this cell:

- Mechanism: `S = sum_{i in same scene, j>0} outer(keys_c[j-1], keys_c[j]) / N_CORTEX`; `pred = argmax_{cand in scene_members} cosine(S @ keys_c[target], keys_c[cand])`
- 6/6 seeds at 1.000 (lift +0.667 to +1.000 vs naive `np.roll(-1)` cosine)
- Mirrors `c3_compressed_sequence_replay_v1` HARD_PASS B_d5=1.000 K=20 N=4096 architecture
- META_RULE_AM (composition-first) confirmed for Q3: substrate already had the primitive; the prior cell mis-wired the readout to `np.roll` cosine; correct wiring rescues completely.

## Discipline tags satisfied

META_RULE_AC pre-reg locked | AE absolute paths | AF arms-distinct as population (3 SHAs at seed=7 collision, 5 SHAs in cross-seed) | AG edge-of-capacity smoke (smoke=full-N) | AH atomic write_metrics | AM composition-first | AN substrate-empirical anchors | H cardinality_ok=True 5/5 | J no silent except (SystemExit re-raised before BaseException) | L strict-above-floor | DISCRIMINATOR-MUST-SURVIVE-SCALE Check A satisfied (smoke = full-N regime)

All numbers tagged: MEASURED@ for on-disk metrics; HYPOTHESIZED@ for HP/HF bands; THEORETICAL@ for lift thresholds.

## Files

- Cell: `d:/AI/hd-instrument/experiments/exp_substrate_narrative_coref_temporal_composition_v1.py`
- Prereg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_narrative_coref_temporal_composition_v1.md`
- Smoke metrics: `d:/AI/hd-instrument/data/exp_substrate_narrative_coref_temporal_composition_v1_smoke/metrics.json`
- Partials (5): `d:/AI/hd-instrument/data/exp_substrate_narrative_coref_temporal_composition_v1_smoke/partial_metrics_seed7_*.json`

-- exp_dev 2026-06-28
