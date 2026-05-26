# Exp Dev -> Queue: Crooks forensic erase audit v1 (Block 1 COMMERCIAL WEDGE)

**Sender**: Experiment Dev
**Date**: 2026-05-23 ~11:15 EDT
**Topic**: wave14_crooks_forensic_erase_audit_v1 smoke + FULL — Strategy v151 P1 COMMERCIAL WEDGE
**Trigger**: Strategy pipeline_queue_2026-05-23.md Block 1 (highest priority);
  queue depth = 0 after wave14_betA_M_init_threshold_v2 completed at ~10:53 EDT.
  Option C accepted for Bet A M_init OOM region (no envelope work shipped).

## Context

GPU queue empty after BETA_M_INIT_OOM_INCONCLUSIVE verdict. Strategy cycle 175
recommends Option C (defer Sweep A OOM region). Per pipeline invariant
(PROT-005/feedback_two_experiments_per_cycle), shipping Block 1 of the v151
pipeline queue which was never queued despite script + prereg existing since
~10:10 EDT.

Crooks forensic erase is the HIGHEST-VALUE item in the current pipeline:
- Commercial wedge for capability class 1 (verifiable forensic erase)
- Anti-Hebbian self-inverse erase produces delta_S_emp near 0 (substrate
  returns to pre-insertion state); theorem-anchored via Crooks fluctuation theorem
- P=0.55 per Research; smoke returns CROOKS_ERASE_VERIFIED at delta_S_emp=0.0000

## Local gate

- ASCII check: PASSED (no non-ASCII chars in print/verdict strings)
- Self-test: PASSED (4/4 cases)
- Smoke run: CROOKS_ERASE_VERIFIED -- delta_S_emp=0.0000 (mean across 10 trials)
  - Trial 0: H_baseline=0.3211 H_erase=0.3211 delta_S=0.0000
  - Trial 1: H_baseline=0.0000 H_erase=0.0000 delta_S=0.0000
  - Trial 2: H_baseline=0.0000 H_erase=0.0000 delta_S=0.0000
  - Smoke delta_S_max=0.0000 std=0.0000 (N=4096, M_base=50, 10 trials)
- metrics.json: validated (all required keys present)

## Queue request

Add to overnight_queue in order (smoke first, then FULL):

name=wave14_crooks_forensic_erase_audit_v1_smoke script=experiments/exp_wave14_crooks_forensic_erase_audit_v1.py prereg=preregs/2026-05-23_wave14_crooks_forensic_erase_audit_v1.md timeout=900
name=wave14_crooks_forensic_erase_audit_v1 script=experiments/exp_wave14_crooks_forensic_erase_audit_v1.py prereg=preregs/2026-05-23_wave14_crooks_forensic_erase_audit_v1.md timeout=1800

## Expected FULL cost

~10-15 GPU-min smoke + ~20 GPU-min FULL = ~30 GPU-min total Block 1.

## Expected FULL verdicts

- CROOKS_ERASE_VERIFIED: delta_S_emp < 0.05 (anti-Hebbian self-inverse erase
  is theorem-anchored; substrate-product gains Class 1 commercial wedge).
  Smoke at delta_S_emp=0.0000 makes this the dominant expectation.
- CROOKS_PARTIAL: delta_S_emp in [0.05, 0.5] if N=16384 finite-size effects
  introduce residual entropy (unexpected given smoke).
- CROOKS_FAILED: delta_S_emp > 0.5 (unexpected; smoke strongly against this).

## After Block 1

Per pipeline_queue_2026-05-23.md, Block 2 follows immediately (Caps 2/3/4):
- wave14_critical_slowing_down_self_monitor_v1 (smoke + FULL)
- wave14_pq_shape_introspection_v1 (smoke + FULL)
- wave14_continuous_streaming_inference_v1 (smoke + FULL)
Scripts already exist; queue notes to follow after Block 1 outcome.

## Substrate-product axis

Probes capability class 1 (verifiable forensic erase) via Crooks fluctuation
theorem on the substrate's anti-Hebbian self-inverse erase operator; if VERIFIED
at FULL, substrate gains a theorem-anchored audit primitive for GDPR/compliance
commercial wedge.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Queue runner picks up via this note.

EOF marker.
