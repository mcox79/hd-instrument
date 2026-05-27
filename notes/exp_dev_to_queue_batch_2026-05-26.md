# exp_dev batch ship — 2026-05-26

10 experiments shipped this cycle. All passed selftest + smoke before queue_add.

## Schema A routing entries

queue=overnight_queue name=wave14_moe_shift_K_scaling_v2 script=experiments/exp_wave14_moe_shift_K_scaling_v2.py prereg=preregs/2026-05-26_wave14_moe_shift_K_scaling_v2.md timeout=7200
queue=overnight_queue name=wave14_moe_top_edge_v3 script=experiments/exp_wave14_moe_top_edge_v3.py prereg=preregs/2026-05-26_wave14_moe_top_edge_v3.md timeout=7200
queue=overnight_queue name=wave14_betB_replay_hA_direct_v2 script=experiments/exp_wave14_betB_replay_hA_direct_v2.py prereg=preregs/2026-05-26_wave14_betB_replay_hA_direct_v2.md timeout=10800
queue=overnight_queue name=wave14_1rsb_pq_retained_v3 script=experiments/exp_wave14_1rsb_pq_retained_v3.py prereg=preregs/2026-05-26_wave14_1rsb_pq_retained_v3.md timeout=14400
queue=overnight_queue name=wave14e_bet_n_wta_v4 script=experiments/exp_wave14e_bet_n_wta_v4.py prereg=preregs/2026-05-26_wave14e_bet_n_wta_v4.md timeout=7200
queue=overnight_queue name=wave14_betB_5corpus_noreplay_fix_v1 script=experiments/exp_wave14_betB_5corpus_noreplay_fix_v1.py prereg=preregs/2026-05-26_wave14_betB_5corpus_noreplay_fix_v1.md timeout=14400
queue=overnight_queue name=wave14_betB_nscaling_v2 script=experiments/exp_wave14_betB_nscaling_v2.py prereg=preregs/2026-05-26_wave14_betB_nscaling_v2.md timeout=14400
queue=remote_cpu_queue name=wave14_moe_intraexpert_overlap_v1 script=experiments/exp_wave14_moe_intraexpert_overlap_v1.py prereg=preregs/2026-05-26_wave14_moe_intraexpert_overlap_v1.md timeout=3600
queue=remote_cpu_queue name=wave14f_hippo_eigenspace_v1 script=experiments/exp_wave14f_hippo_eigenspace_v1.py prereg=preregs/2026-05-26_wave14f_hippo_eigenspace_v1.md timeout=7200
queue=remote_cpu_queue name=wave14_betB_rd_perturbation_recovery_v2 script=experiments/exp_wave14_betB_rd_perturbation_recovery_v2.py prereg=preregs/2026-05-26_wave14_betB_rd_perturbation_recovery_v2.md timeout=3600

## Post-ship verification

overnight_queue pending at ship time: 6 (+ 1 running = 7 total new)
remote_cpu_queue pending at ship time: 5 (3 new + 2 pre-existing: saddle_cascade_v4_n2048, hippo_replay_w_v1)

All 10 confirmed present in remote queue.json via queue_add.sh built-in verify (exit-5 on miss).
wave14_moe_shift_K_scaling_v2: confirmed RUNNING in overnight_queue at verification time.

## Bugs fixed during this batch

1. exp_wave14_betB_5corpus_noreplay_fix_v1.py: run_one_4class_cell() rewrote to use
   base.train_w_with_replay() API. Prior manual Hebbian loop used pool_v=byte_atoms[val_idx]
   where val_idx is shape (T,4) bigram index, producing (T,4,N) pool_v that fails matmul.
   Fix: pass train_a_idx (T,4) + train_a_tgt (T,) directly to train_w_with_replay().

2. exp_wave14_betB_5corpus_noreplay_fix_v1.py: bic_k_gaussian() used sklearn.cluster.KMeans
   which is not installed on remote (marsh@home). Replaced with _kmeans_1d() pure numpy impl.

3. exp_wave14_betB_5corpus_noreplay_fix_v1.py: selftest BIC assertion used exact-value mock
   data (sigma2 -> 0) causing BIC to not distinguish k=4 from k=3. Fixed to use overlapping
   Gaussians (std=0.025, spacing=0.10, n=30/cluster) where k=4 is genuinely better.
