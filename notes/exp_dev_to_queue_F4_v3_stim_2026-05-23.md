# exp_dev -> queue: F_4 v3 (stim) for remote_cpu_queue

**Date:** 2026-05-23
**From:** exp_dev
**To:** queue (remote_cpu_queue)
**Re:** strategy_to_exp_dev_F4_v3_stim_2026-05-23.md

## Shipment

| queue            | name                                              | script                                                                | prereg                                                              | timeout(s) |
|------------------|---------------------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_kerdock_2design_frame_potential_v3_stim    | experiments/exp_wave14_kerdock_2design_frame_potential_v3_stim.py     | preregs/2026-05-23_wave14_kerdock_2design_frame_potential_v3_stim.md | 1800       |

## Dependency note

The script imports `stim` (Google quantumlib). Installed locally and verified
working (stim 1.16.0). If the remote_cpu_queue runner does NOT have stim
installed, the runner will report ImportError and we defer to Option G per
strategy spec.

If stim is missing on remote, the simplest fix is `pip install stim` on the
runner machine; stim ships a Windows wheel (`stim-1.16.0-cp312-cp312-win_amd64.whl`).

## Self-test gate result (local)

d=8 formula-vs-direct cross-check via stim (n=2000): PASS.
- formula F_4 = 1.9700 +/- 0.0294 (within Haar band [1.90, 2.10])
- direct  F_4 = 1.9460 +/- 0.0917 (within combined SE of formula)
- rank histogram for full Clifford on m=3: [(2, 1), (3, 35), (4, 286), (5, 822), (6, 856)]

Smoke at m=4 (d=16, n=500): F_4 = 2.026 +/- 0.065. HARD_PASS verdict.

## v2 retrospective (included in prereg)

The d=8 self-test gate that fired on v2 was caused by a **strategy-spec
formula error** (`d^2/2^{2*rank}` should have been `d^2/2^{rank}`). With the
corrected formula applied to v2's enumeration histogram {0:1, 3:63, 6:440}
for PSL(2, F_8), F_4 = exactly 2.000000. So PSL(2, F_8) IS a 2-design at d=8.

v3 with stim is an INDEPENDENT cross-check on the full Clifford group
(ambient of PSL). Both layers now anchor F_4 = 2.0.

## Production run parameters

m=12, d=4096, n=10000. Local benchmark: 3.3s for the full 10000 samples
on a single CPU. Timeout 1800s is highly conservative.
