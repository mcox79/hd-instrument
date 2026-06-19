# exp_dev -> queue routing note (2026-05-24 pipeline-refill batch of 5 anchors)

Dispatched per orchestrator invocation: "GPU running NOW but gpu_queue=0
pending behind it; remote_cpu also idle. FILL BOTH QUEUES with substantive
work — at least 2 GPU + 3 CPU anchors, ETAs 30min to 4hr each."

Pause flag CLEARED (verified absent at dispatch time).

| queue            | name                                       | script                                                       | prereg                                                              | timeout(s) |
|------------------|--------------------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_rect_free_conv_mn8_v1               | experiments/exp_wave14_rect_free_conv_mn8_v1.py              | preregs/2026-05-24_wave14_rect_free_conv_mn8_v1.md                  | 3600       |
| remote_cpu_queue | wave14_mingo_speicher_2nd_order_mn8_v1     | experiments/exp_wave14_mingo_speicher_2nd_order_mn8_v1.py    | preregs/2026-05-24_wave14_mingo_speicher_2nd_order_mn8_v1.md        | 3600       |
| remote_cpu_queue | wave14_hatano_sasa_cap3_long_traj_v2       | experiments/exp_wave14_hatano_sasa_cap3_long_traj_v2.py      | preregs/2026-05-24_wave14_hatano_sasa_cap3_long_traj_v2.md          | 7200       |
| overnight_queue  | wave14_tropical_kerdock_N4096_smaller_v1   | experiments/exp_wave14_tropical_kerdock_N4096_smaller_v1.py  | preregs/2026-05-24_wave14_tropical_kerdock_N4096_smaller_v1.md      | 1800       |
| overnight_queue  | wave14_interp_family_N8192_reduced_v1      | experiments/exp_wave14_interp_family_N8192_reduced_v1.py     | preregs/2026-05-24_wave14_interp_family_N8192_reduced_v1.md         | 5400       |

## Hypotheses (one-line each)

- **rect_free_conv_mn8_v1** (B): does substrate Kerdock spectrum match
  rectangular Marchenko-Pastur(c=8) at high aspect ratio, or carry higher
  rect-free cumulants beyond MP universality?

- **mingo_speicher_2nd_order_mn8_v1** (A): does substrate Kerdock match
  iid-Gauss reference at Mingo-Speicher 2nd-order moment alpha_pq for
  (p,q) in {(2,2),(2,3),(3,3)} at c=8?

- **hatano_sasa_cap3_long_traj_v2** (G): does v1's Cap 3 HS-IFT MIDDLE
  band disappear at 2x glauber_steps (60->120) + 2x n_traj (150->300)?

- **tropical_kerdock_N4096_smaller_v1** (F): does empirical bit-flip
  margin at N=1024 4-coset MM Kerdock match the N=4096 WELL_DEFINED
  baseline at the same cv / deg_frac bounds?

- **interp_family_N8192_reduced_v1** (H): does Cap 12 predictor (Spearman
  rho >= 0.50) hold at N=8192 on SRHT + Hadamard with 3 alphas x 3 seeds
  reduced grid?

## Smoke results

All 5 smokes PASS structurally with valid metrics.json + assert-driven
self-tests:
- B: 5/5 self-test cells; smoke INCONCLUSIVE (N=64 Kerdock skip expected).
- A: 4/4 self-test cells; smoke INCONCLUSIVE (kerdock skipped at N=64).
- G: 14 verdict + 4 formula self-test cells (from v1); smoke MIDDLE_BAND
  (expected at smoke length 80).
- F: 5/5 self-test cells; smoke EMP_MARGIN_WELL_DEFINED at N=1024.
- H: 9/9 self-test cells (from v1); smoke INCONCLUSIVE (N=64 not 8192).

## Routing reasons

- B, A, G to **remote_cpu_queue**: pure-CPU SVD / Markov work; G especially
  is long-running.
- F, H to **overnight_queue (GPU)**: F is GPU-vectorized empirical margin;
  H requires N=8192 SVD which is feasible on CPU but the AMP+VAMP loops
  on N=8192 benefit from CUDA when available.

## Status_log entries

5 entries filed (HIGH for B/A/G/H — first-time tests of new
free-probability / Hatano-Sasa / N=8192 frontiers; MEDIUM for F as
companion to existing N=4096 anchor).

## Blockers

None. Name uniqueness verified pre-ship; remote post-ship VERIFIED step
in queue_add.sh confirms each entry lands in remote queue.json.
