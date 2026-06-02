# exp_dev to queue: Round 6 overnight batch (2026-06-01)

**Filed:** 2026-06-01
**From:** exp_dev (Sonnet)
**Batch:** 10 of 12 cells (2 cloud-handoff, 2 dropped, 8 queued)

## Cell disposition

| Cell | Status | Queue | Reason |
|------|--------|-------|--------|
| A | CLOUD_HANDOFF | H100 | N=32768 multi-tenancy -- testbed handoff filed |
| B | CLOUD_HANDOFF | H100 | N-scaling 4-point FDT collapse -- testbed handoff filed |
| C | SHIP | overnight_queue | CK discriminator N=2048 -- smoke MIDDLE_BAND, valid |
| D | SHIP | overnight_queue | L=2 Hadamard comp N=8192 -- smoke HARD_PASS |
| E | SHIP | remote_cpu_queue | tr(W1W2) identity -- smoke HARD_PASS |
| F | SHIP | remote_cpu_queue | CSP+Hebbian coexist -- smoke HARD_PASS |
| G | DROP | -- | INSTRUMENTATION_SUSPECT: sparse-W K={1..8} all 0.0 acc; random sparse W not K^2-capable |
| H | SHIP | remote_cpu_queue | PP-31c knee -- smoke HARD_FAIL valid (knee at tau=0.258 < [0.65,0.85]) |
| I | DROP | -- | INSTRUMENTATION: scalar ODE saturates max_steps, all N same tau; needs redesign |
| J | SHIP | remote_cpu_queue | TW spectral edge -- smoke MIDDLE_BAND valid |
| K | SHIP | remote_cpu_queue | Symbolic battery -- smoke HARD_PASS |
| L | SHIP | remote_cpu_queue | Bursty write -- smoke MIDDLE_BAND valid |

## Queue entries (Schema A)

```
queue=overnight_queue name=ck_seb_discriminator_v1 script=experiments/exp_ck_seb_discriminator_v1.py prereg=preregs/2026-06-01_ck_seb_discriminator_v1.md timeout=900
queue=overnight_queue name=l2_hadamard_comp_n8192_v1 script=experiments/exp_l2_hadamard_comp_n8192_v1.py prereg=preregs/2026-06-01_l2_hadamard_comp_n8192_v1.md timeout=900
queue=remote_cpu_queue name=tr_w1w2_set_intersect_v1 script=experiments/exp_tr_w1w2_set_intersect_v1.py prereg=preregs/2026-06-01_tr_w1w2_set_intersect_v1.md timeout=300
queue=remote_cpu_queue name=csp_hebbian_coexist_v1 script=experiments/exp_csp_hebbian_coexist_v1.py prereg=preregs/2026-06-01_csp_hebbian_coexist_v1.md timeout=300
queue=remote_cpu_queue name=pp31c_knee_calib_n8192_v1 script=experiments/exp_pp31c_knee_calib_n8192_v1.py prereg=preregs/2026-06-01_pp31c_knee_calib_n8192_v1.md timeout=1800
queue=remote_cpu_queue name=tracy_widom_n32768_v1 script=experiments/exp_tracy_widom_n32768_v1.py prereg=preregs/2026-06-01_tracy_widom_n32768_v1.md timeout=3600
queue=remote_cpu_queue name=symbolic_prim_battery_v1 script=experiments/exp_symbolic_prim_battery_v1.py prereg=preregs/2026-06-01_symbolic_prim_battery_v1.md timeout=300
queue=remote_cpu_queue name=bursty_write_stepdown_v1 script=experiments/exp_bursty_write_stepdown_v1.py prereg=preregs/2026-06-01_bursty_write_stepdown_v1.md timeout=300
```

## Smoke gate results

| Anchor | Smoke verdict | elapsed_s | metrics.json |
|--------|--------------|-----------|--------------|
| ck_seb_discriminator_v1 | MIDDLE_BAND | 147s | data/exp_ck_seb_discriminator_v1/metrics.json |
| l2_hadamard_comp_n8192_v1 | HARD_PASS | 0.1s | data/exp_l2_hadamard_comp_n8192_v1/metrics.json |
| tr_w1w2_set_intersect_v1 | HARD_PASS | 3.2s | data/exp_tr_w1w2_set_intersect_v1/metrics.json |
| csp_hebbian_coexist_v1 | HARD_PASS | 0.4s | data/exp_csp_hebbian_coexist_v1/metrics.json |
| pp31c_knee_calib_n8192_v1 | HARD_FAIL | 232s | data/exp_pp31c_knee_calib_n8192_v1/metrics.json |
| tracy_widom_n32768_v1 | MIDDLE_BAND | 0.1s | data/exp_tracy_widom_n32768_v1/metrics.json |
| symbolic_prim_battery_v1 | HARD_PASS | 0.9s | data/exp_symbolic_prim_battery_v1/metrics.json |
| bursty_write_stepdown_v1 | MIDDLE_BAND | 11.5s | data/exp_bursty_write_stepdown_v1/metrics.json |

Note: pp31c smoke HARD_FAIL is a legitimate result (knee at tau=0.258 outside [0.65,0.85]).
Shipping to confirm at FULL scale with 5 seeds. FULL run will quantify knee instability.

## Timeout estimates (per role contract formula)

- ck_seb_discriminator_v1: smoke=147s, FULL/smoke N ratio=1, seeds ratio=5/2=2.5, scaling=1.5
  ceil(1.5 * 147 * 1^1.5 * 2.5) = ceil(551) = 600 -> timeout=900 (1.5x safety)
- l2_hadamard_comp_n8192_v1: smoke=0.1s (N=1024), FULL_N/smoke_N=8, seeds=5/2=2.5, scaling=1.5
  ceil(1.5 * 0.1 * 8^1.5 * 2.5) = ceil(8.5) -- too low; using 900s (minimum for N=8192)
- tr_w1w2_set_intersect_v1: smoke=3.2s, FULL same N, seeds=5/1=5, scaling=1.0
  ceil(1.5 * 3.2 * 1 * 5) = ceil(24) -> timeout=300 (floor)
- csp_hebbian_coexist_v1: smoke=0.4s, FULL same N, seeds=5/2=2.5, scaling=1.0
  ceil(1.5 * 0.4 * 1 * 2.5) = ceil(1.5) -> timeout=300 (floor)
- pp31c_knee_calib_n8192_v1: smoke=232s, FULL same N, seeds=5/2=2.5, scaling=1.5
  ceil(1.5 * 232 * 1 * 2.5) = ceil(870) -> timeout=1800 (2x safety; slow convergence)
- tracy_widom_n32768_v1: smoke=0.1s (N=4096), FULL_N/smoke_N=8, seeds=5/2=2.5, scaling=2.0
  ceil(1.5 * 0.1 * 8^2.0 * 2.5) = ceil(24) -- dominated by eigendecomp; using 3600 (1h estimate)
- symbolic_prim_battery_v1: smoke=0.9s, FULL same N, seeds=5/2=2.5, scaling=1.0
  ceil(1.5 * 0.9 * 1 * 2.5) = ceil(3.4) -> timeout=300 (floor)
- bursty_write_stepdown_v1: smoke=11.5s, FULL same N, seeds=5/2=2.5, scaling=1.0
  ceil(1.5 * 11.5 * 1 * 2.5) = ceil(43) -> timeout=300 (floor)

## Drop notes

- Cell I (tau_mem): scalar ODE simulator doesn't capture N-dependent decay; all N give same tau.
  Filed: notes/exp_dev_to_strategy_tau_mem_instrumentation_2026-06-01.md
- Cell G (sparse_w): random sparse W with K={1,2,4,8} gives 0.0 accuracy; physics not instrumentation.
  Filed: notes/exp_dev_to_strategy_sparse_w_instrumentation_2026-06-01.md

## Testbed handoff

Filed: notes/testbed_handoff_overnight_round6_cloud_h100_cells_a_b_2026-06-01.md
Cells A (mt_depth_n32768_v1) and B (pp33_fdt_4pt_collapse_v1) require H100.

<!-- routing-completed: Acted-on 2026-06-01: Round 6 batch absorbed across v322 + v323 + v324 reclassification -->
