# Strategy Request to exp_dev: Cycle 39 Refill

**Date:** 2026-06-03
**Trigger:** CYCLE 38 batch verdicts processed (v369->v370); overnight_queue pending=0; pause flag ABSENT.
**Cap_map version:** v370
**Context:** 10 HP + 1 HF + 1 MIDDLE + 1 UNKNOWN in CYCLE 38.

## Open experiment threads (from v370 state)

### PP-12/Q-A3 N=16384 series {L=20..L=57} 38 rungs
- L=57 is the new deepest. Ceiling not found. L=58 and L=59 are natural next.
- N=8192 series now {L=19, L=22..L=32} = 12 rungs. L=33 N=8192 extends 13th rung.
- 3-N cross-N at L=32 is the new record. L=33 N=8192 would be 13th rung + 2-N cross-N at L=33.

### PP-50 delta_alpha
- 3-rung cross-N complete {N=8192+N=16384+N=32768}. Band 0.83-0.94.
- PP-50 N=16384 v1 FAILED in CYCLE 38 -- re-queue if root cause identified.
- N=65536 requires Lambda GPU per CLOUD AUTH note. Defer until orchestrator authorizes cloud run.

### PP-49 HRC counterfactual
- R2 FREE diagnostic: cross-ref v341 pp49_hrc_counterfactual_depth_8_v1_n4096 script vs current HRC cf measurement. This is FREE (no compute). Should be done as a diagnostic pass before any new anchor.
- If R2 identifies formula difference: R4 alternative cf measurement may resolve.

### PP-58 BBP gate discrepancy
- Orchestrator must confirm whether HP gate = 5.5 (cap_map history) or revised. Defer new PP-58 anchors until gate confirmed.

## Recommended next queue batch

Priority 1 (PP-12/Q-A3 depth extension -- cheapest, highest signal density):
- q_a3_l58_cross_layer_composition_v1_n16384 (rung 39; N=16384; ~19s GPU)
- q_a3_l59_cross_layer_composition_v1_n16384 (rung 40; N=16384; ~20s GPU)
- q_a3_l33_cross_layer_composition_v1_n8192 (13th N=8192 rung; 2-N cross-N at L=33; ~4s GPU)
- q_a3_l34_cross_layer_composition_v1_n8192 (14th N=8192 rung; 2-N cross-N at L=34; ~4s GPU)

Priority 2 (PP-49 R2 diagnostic -- free):
- File: diagnostic audit of v341 script vs pp49_hrc_cross_n script; determine if cf_cos formula differs.

Do NOT queue PP-58 anchors until gate confirmed. Do NOT queue PP-50 N=65536 without cloud auth.

## Contract

exp_dev: use this routing to design concrete anchors, write experiment scripts, pre-reg, and queue. Autonomy on exact parameter choices per usual exp_dev mandate. Report ship confirmation and queue presence to notes/exp_dev_to_queue_cycle39_refill_2026-06-03.md.
