# Strategy → Experiment Dev: PIPELINE QUEUE — run these 20 experiments in this exact order

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~10:05 EDT
**Topic**: Comprehensive pipeline queue per user "share more priorities than that - exp dev needs more of a pipeline"
**cap_map state**: v151 (commit `0691d24`)

## Run these 20 experiments in this exact order

Total Phase 1+2 ~5-8 GPU-hours. Each line is a single experiment with smoke OR FULL.

### Block 1 — Cap 1 Crooks forensic erase (COMMERCIAL WEDGE Class 1; HIGHEST VALUE)

1. `wave14_crooks_forensic_erase_audit_v1_smoke` — ~10 min — verdict CROOKS_ERASE_VERIFIED/PARTIAL/FAILED
2. `wave14_crooks_forensic_erase_audit_v1` FULL — ~20 min — confirm at FULL

### Block 2 — Other capabilities (Caps 2, 3, 4 from Research; CHEAP)

3. `wave14_critical_slowing_down_self_monitor_v1_smoke` (Cap 2) — ~5 min — verdict SLOWING_DOWN_DETECTS / NO_CORRELATION
4. `wave14_critical_slowing_down_self_monitor_v1` FULL — ~10 min
5. `wave14_pq_shape_introspection_v1_smoke` (Cap 4) — ~5 min — verdict PQ_INTROSPECTION_DETECTS / NO_PHASE_SIGNATURE
6. `wave14_pq_shape_introspection_v1` FULL — ~10 min
7. `wave14_continuous_streaming_inference_v1_smoke` (Cap 3) — ~5 min — verdict STREAMING_CONTINUOUS_PASS / NESS_BREAKS
8. `wave14_continuous_streaming_inference_v1` FULL — ~10 min

### Block 3 — META gap rescues (Gap B + Gap C; substantial substrate-product gains)

9. `wave14_conformal_pq_confidence_v1_smoke` (Gap C calibration rescue) — ~10 min — verdict CONFORMAL_COVERED / OVER / UNDER
10. `wave14_conformal_pq_confidence_v1` FULL — ~30 min
11. `wave14_online_W_robbins_monro_snap_v1_smoke` (Gap B online W) — ~10 min — verdict ONLINE_W_RESISTS_CF / GRADUAL_FORGETTING / CATASTROPHIC
12. `wave14_online_W_robbins_monro_snap_v1` FULL — ~30 min

### Block 4 — cycle 170 Research-informed substrate-physics (P-B/C/D)

13. `wave14_endpoint_RM1m_projection_v1_smoke` (cycle 170 P-C) — ~10 min — verdict RM1M_25_PASS / FAIL
14. `wave14_endpoint_RM1m_projection_v1` FULL — ~15 min
15. `wave14_pq_discrete_spikes_v1_smoke` (cycle 170 P-D) — ~10 min — verdict PQ_DISCRETE_28 / CONTINUOUS
16. `wave14_pq_discrete_spikes_v1` FULL — ~20 min
17. `wave14_coset_count_sweep_v1_smoke` (cycle 170 P-B) — ~15 min — verdict COSET_25_GEOMETRIC / DYNAMICAL / MIXED
18. `wave14_coset_count_sweep_v1` FULL — ~45 min

### Block 5 — pending pickups (long-overdue)

19. `wave14_K1000_eigenspectrum_check_v1` FULL — was running ~44 min last check; may still be in progress
20. `wave14_K_resonance_wide_sweep_v1` FULL — pending from cycle 160 batch

### DEFERRED (run AFTER blocks 1-5)

- `wave14_betZ5_diffusion_smoother_phase1_v1` — Bet Z.5 ~6-9 hrs (longest; new readout primitive)
- `wave14_spatially_coupled_codebook_block_vamp_v1` — Gap A ~1 day (M-storage rescue)
- `wave14_extreme_stress_v1` FULL — cycle 128 long-overdue

## What to do if a smoke FAILS

- **CROOKS_FAILED**: stop Block 1; skip to Block 2
- **NO_CORRELATION / NO_PHASE_SIGNATURE / NESS_BREAKS**: log negative, skip to next Block 2 item, continue to Block 3
- **CONFORMAL_UNDER/OVER**: log, continue to Block 3 next item
- **ONLINE_W_CATASTROPHIC**: log, continue to Block 4
- Any FULL after PASS smoke: run regardless (per cycle 162-170 smoke→FULL precedent)

## Substrate-product priority logic

**Block 1 Crooks forensic erase** = COMMERCIAL WEDGE; highest substrate-product
value of any new direction across session arc. **RUN THIS FIRST**.

**Block 2** = cheap substrate-product capability extensions; all from Research
theorem-implied capabilities; smoke+FULL each <30 min total per cap.

**Block 3** = META substrate-product breakout rescue paths; substantial
substrate-product gains if pass.

**Block 4** = substrate-physics characterization completion (RM(1,16) geometric
origin + P(q) discrete spike connection to 28-element endpoint + coset-count
sweep).

**Block 5** = long-pending pickups.

**DEFERRED** = longest substrate-product/physics work.

## Total cost

Blocks 1-5: ~5 GPU-hours (with smoke→FULL discipline; many CONSISTENT will accelerate)
DEFERRED: ~7-12 GPU-hours additional.

## Per [[feedback-no-papers-product-only]]

ALL blocks substrate-product oriented.

## Per [[feedback-sessions-self-coordinate]]

File-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
