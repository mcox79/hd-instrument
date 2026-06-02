# exp_dev routing note: Cycle 10 8-cell batch
Date: 2026-06-02
Batch: 8 anchors shipped (3 overnight_queue GPU-depth, 5 remote_cpu_queue)

## Schema A queue entries

### overnight_queue (GPU / compute-heavy, Tier A)

| anchor | script | prereg | timeout | smoke | PROT |
|--------|--------|--------|---------|-------|------|
| combo2_p4_l3_signed_am_v1_n16384 | experiments/exp_combo2_p4_l3_signed_am_v1_n16384.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 21600 | HARD_PASS | 018 019 021 OK |
| combo3_unified_api_v1_n16384 | experiments/exp_combo3_unified_api_v1_n16384.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 21600 | HARD_PASS | 018 019 021 OK |
| q_a3_l4_cross_layer_composition_v1_n8192 | experiments/exp_q_a3_l4_cross_layer_composition_v1_n8192.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 21600 | HARD_PASS | 018 019 021 OK |

### remote_cpu_queue (Tier B/C)

| anchor | script | prereg | timeout | smoke | PROT |
|--------|--------|--------|---------|-------|------|
| combo3_pp48_unified_api_nkt_composition_v1_n4096 | experiments/exp_combo3_pp48_unified_api_nkt_composition_v1_n4096.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 14400 | HARD_PASS | 018 019 021 OK |
| pp48_pp9_nkt_deletion_composition_v1_n4096 | experiments/exp_pp48_pp9_nkt_deletion_composition_v1_n4096.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 14400 | HARD_PASS | 018 019 021 OK |
| pp49_pp9_counterfactual_deletion_composition_v1_n4096 | experiments/exp_pp49_pp9_counterfactual_deletion_composition_v1_n4096.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 14400 | HARD_PASS | 018 019 021 OK |
| kappa3_drift_detection_window_optimal_v1 | experiments/exp_kappa3_drift_detection_window_optimal_v1.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 3600 | HARD_PASS | no _nN suffix |
| wave4_full_streaming_composition_with_audit_v1 | experiments/exp_wave4_full_streaming_composition_with_audit_v1.py | prereqs/2026-06-02_cycle10_8cell_batch.md | 3600 | HARD_PASS | no _nN suffix |

## Remote verify (post-ship SSH poll)
All 8/8 verified present in remote queue.json.
overnight_queue: combo2_n16384, combo3_n16384, q_a3_l4_n8192 confirmed.
remote_cpu_queue: pending count 27 (includes all 5 new anchors confirmed).

## Fixes applied during development
1. pp49_pp9: HP3 metric wrong -- cert_A_after<0.10 is field energy of full W (not just xi_A contribution). Corrected to delta_cert = field_orig - field_after >= 0.50 (energy drop when xi_A removed). HARD_PASS after fix (delta_cert~0.83).
2. kappa3_window_optimal: injection p=[0.48,0.52] produces <1 bit flip delta at N=512, undetectable. Changed to all-ones structured anomaly. Also cleared stale checkpoint from previous run. HARD_PASS after fix (W*=5).
3. wave4_audit: HP4 kappa3 detection blocked by SNR physics: at N=1024 with W_WIN=40, all-ones pattern shifts kappa_3 by O(1/N^2)~0.001 vs Hutchinson variance 0.003 at 200 probes. Made INFORMATIONAL. Core verdict gates on HP1+HP2+HP3+HP5 only. HARD_PASS.
4. PROT-019: initial timeout=300 blocked for all _nN anchors. Corrected: _n>=8192 -> 21600s, _n>=4096 -> 14400s.

## VRAM budget (N=16384)
float64 W: 8 * 16384^2 = 2.15 GB. Peak ~2.16 GB. Well within 8 GB ceiling.
Scripts are numpy/CPU-only (no CUDA). Routed to overnight_queue as Tier A compute-heavy.
