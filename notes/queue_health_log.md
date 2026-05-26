# Queue health log

Append-only. One line per cycle. Format:
`<ts> | GPU=<status>:<current> | CPU=<status>:<current> | pending_gpu=N | pending_cpu=M`

2026-05-21T07:58 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | bootstrap: PAUSED patch applied, cutover relaunch, both runners healthy
2026-05-21T08:11 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot 08:06, hb 08:06; healthy idle, no action
2026-05-21T08:11 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot 08:10:36 (fresh); healthy idle, no action
2026-05-21T08:16 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot 08:15:36 (fresh); healthy idle, no action
2026-05-21T08:21 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot 08:21:06 (fresh); healthy idle; runners will self-exit ~09:01 if no queue
2026-05-21T08:26 | GPU=running:wave14d_icl_via_pool_v3_scaling | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU picked up work at 08:24:38 (wall ~1m); CPU still idle; healthy
2026-05-21T08:31 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU finished wave14d_icl_via_pool_v3_scaling at 08:25:42 (64.3s exit 0); both idle; healthy
2026-05-21T08:36 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot 08:35:36 (fresh); healthy idle, no action
2026-05-21T08:41 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14r_erase_orthkeys_v1 08:38:13-08:38:50 (36.8s exit 0); both idle; GPU exit ~09:38:50
2026-05-21T08:46 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot 08:45:46 reports Visibility TimeoutError; fell back to direct ssh (hb 08:43:56/57); healthy
2026-05-21T08:54 | GPU=DEAD:None | CPU=DEAD:None | pending_gpu=0 | pending_cpu=0 | workstation rebooted 08:44:16; both runners + healer killed; pending=0 so invariant does NOT require relaunch; ALERT raised
2026-05-21T08:56 | GPU=running:wave14s_chargeflip_forensics_v1 | CPU=idle:None | pending_gpu=? | pending_cpu=0 | user override: cutover --skip-healer; GPU pid 7760, CPU pid 40128; alert cleared
2026-05-21T09:00 | GPU=running:wave14s_chargeflip_forensics_v1 | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot fresh 09:00:06; GPU wall ~4m; Visibility recovered too; healthy
2026-05-21T09:05 | GPU=running:wave14s_chargeflip_forensics_v1 | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot fresh 09:04:37; GPU wall ~8.5m; healthy
2026-05-21T09:10 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU exp wave14s_chargeflip_forensics_v1 FAIL exit=1 at 09:07:19 (652s) - experiment-side, not queue-health; both idle
2026-05-21T09:15 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14t_multihop_v3 09:10:39-09:10:51 (11.8s exit 0); both idle; healthy
2026-05-21T09:20 | GPU=running:wave14s_chargeflip_forensics_v1_b | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU on retry of forensics_v1 (started 09:15:06, wall ~5m); CPU idle; healthy
2026-05-21T09:28 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU retry DONE wave14s_chargeflip_forensics_v1_b 09:26:11 (664s exit 0); both idle; healthy
2026-05-21T09:33 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14u_multihop_envelope_v1 09:28:36-09:29:19 (42.9s exit 0); both idle; healthy
2026-05-21T09:38 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14u_multihop_envelope_v1_b 09:36:29-09:37:40 (70.9s exit 0); both idle; healthy
2026-05-21T09:43 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | snapshot fresh 09:42:43; no new activity; CPU idle-exit due ~09:56; healthy
2026-05-21T09:48 | GPU=idle:None | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14v_erase_kerdock_v2 09:45:10-09:45:50 (40.3s exit 0); both idle; healthy
2026-05-21T09:53 | GPU=running:wave14w_icl_extended | CPU=idle:None | pending_gpu=0 | pending_cpu=0 | GPU on wave14w_icl_extended since 09:51:01 (wall ~2m); CPU idle; healthy
2026-05-21T09:58 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU done wave14w_icl_extended at 09:56:11 (310s exit 0); CPU graceful idle-exit at 09:56:08; invariant satisfied (pending_cpu=0); no relaunch
2026-05-21T10:03 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14x_multihop_N_scaling 09:58:11-09:58:30 (18.8s exit 0); CPU still exited (pending_cpu=0 → no relaunch); healthy
2026-05-21T10:08 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity; GPU exit ~10:58:30; CPU still exited; healthy
2026-05-21T10:13 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14z_multihop_hadamard_entities 10:08:35-10:08:48 (13s exit 0); CPU still exited; healthy
2026-05-21T10:18 | GPU=running:wave14y_erase_kerdock_v3 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on wave14y_erase_kerdock_v3 since 10:17:24 (wall ~1m); CPU still exited; healthy
2026-05-21T10:23 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU done wave14y_erase_kerdock_v3 at 10:18:21 (57.2s exit 0); CPU still exited; healthy
2026-05-21T10:25 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | PROT-003 short-form fire; chat now clean; no new activity since 10:18:21; healthy
2026-05-21T10:30 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14ya_erase_kerdock_v4 10:26:36-10:28:45 (128.6s exit 0); CPU still exited; healthy
2026-05-21T10:35 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14yb_edit_then_query_kerdock 10:31:00-10:31:06 (5.5s exit 0); CPU still exited; healthy
2026-05-21T10:40 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14yc_continual_editing_kerdock 10:39:11-10:39:32 (21s exit 0); CPU still exited; healthy
2026-05-21T10:45 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity since 10:39:32; healthy
2026-05-21T10:50 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14yd_calibration_fact_retrieval 10:47:32-10:48:00 (27.3s exit 0); CPU still exited; healthy
2026-05-21T10:55 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU: wave14ye_erase_kerdock_v5 FAIL exit=1 (20s) at 10:53:10 (experiment-side), then wave14yf_continual_editing_v2_stress DONE 28s exit 0 at 10:53:38; CPU still exited; healthy
2026-05-21T11:00 | GPU=running:wave14yi_multihop_edited_factbase | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on yi (just started 10:59:40); also ran wave14yh_edit_query_overcapacity 6.1s exit 0; CPU still exited; healthy
2026-05-21T11:04 | GPU=running:wave14ym_continual_editing_v4_500 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | snapshot caught transient idle-with-pending; direct hb 11:04:09 shows GPU claimed wave14ym within 5s (POLL_INTERVAL_S); healthy
2026-05-21T11:09 | GPU=running:wave14yr_continual_editing_1000 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on yr since 11:08:05; also completed ym (87.8s) and yp (14.6s) since last cycle; healthy
2026-05-21T11:14 | GPU=running:wave14ys_continual_editing_2000 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU active+claimed (started 11:10:57 wall ~3m); yt/yu/yv pending; CPU still exited; healthy
2026-05-21T11:19 | GPU=running:wave14yx_calibration_temp_scaling | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on yx since 11:17:30; cleared yv (8.2s) and yw (8.6s) since last cycle; healthy
2026-05-21T11:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU cleared yx (118.6s) and yy (12.1s) at 11:19:29 and 11:20:56; both idle; healthy
2026-05-21T11:29 | GPU=running:wave14za_icl_continual_pool | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on za since 11:28:40; cleared yz (13.6s) since last cycle; healthy
2026-05-21T11:34 | GPU=running:wave14zb_continual_5000 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on zb since 11:29:27 (wall ~4m); zc/zd pending; cleared za (12.0s); healthy
2026-05-21T11:39 | GPU=running:wave14zb_continual_5000 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on zb (wall ~9m, well under 4h); 4 pending behind; healthy
2026-05-21T11:44 | GPU=running:wave14zc_erase_kerdock_v7_32coset | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | zb finished (677.1s exit 0); GPU now on zc since 11:40:44 (wall ~3m); 3 pending; healthy
2026-05-21T11:49 | GPU=running:wave14zc_erase_kerdock_v7_32coset | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on zc (wall ~8m); 4 pending now; healthy
2026-05-21T11:54 | GPU=running:wave14zc_erase_kerdock_v7_32coset | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU still on zc (wall ~13m); 5 pending; healthy
2026-05-21T11:59 | GPU=running:wave14zc_erase_kerdock_v7_32coset | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | GPU still on zc (wall ~18m); 8 pending now; healthy
2026-05-21T12:04 | GPU=running:wave14zc_erase_kerdock_v7_32coset | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | GPU still on zc (wall ~23m); 11 pending now; well under 4h; healthy
2026-05-21T12:09 | GPU=running:wave14zi_continual_4N | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | zc finished; pipeline draining (cleared zf 21.3s, zh 70.6s); GPU on zi since 12:07:31; healthy
2026-05-21T12:14 | GPU=running:wave14zl_calibration_after_edit | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on zl since 12:13:35; cleared zj (101s) + zk (9.6s); pending 6→3; healthy
2026-05-21T12:34 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | snapshot wrapper fresh (12:33:47) but embedded GPU hb stale (12:16:11) - Visibility-side issue; SSH fallback confirms GPU pid 7760 hb 12:34:26 healthy idle; pipeline emptied (cleared zl 63s, zm 3.4s, zn 8s, zo 6.5s)
2026-05-21T12:40 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | snapshot freshness now passes (embedded hb 12:39:47); transient Visibility issue resolved; GPU idle since 12:14:56 (exit ~13:14:56); healthy
2026-05-21T12:45 | GPU=running:wave14zp_kerdock_v8_32coset_retry | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU on zp since 12:44:37; zr pending; healthy
2026-05-21T12:50 | GPU=running:wave14zp_kerdock_v8_32coset_retry | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU still on zp (wall ~5m); 5 pending now; healthy
2026-05-21T12:55 | GPU=running:wave14zs_reversibility_long | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | zp done (550s); zr done (3.6s); GPU on zs since 12:53:51; healthy
2026-05-21T13:00 | GPU=running:wave14zs_reversibility_long | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on zs (wall ~6m); 4 pending; healthy
2026-05-21T13:05 | GPU=running:wave14zs_reversibility_long | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on zs (wall ~11m); 4 pending; healthy
2026-05-21T13:10 | GPU=running:wave14zs_reversibility_long | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on zs (wall ~16m); 4 pending; healthy
2026-05-21T13:15 | GPU=running:wave14zs_reversibility_long | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on zs (wall ~21m); 4 pending; healthy
2026-05-21T13:20 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | zs done (1277s exit 0); GPU on zq since 13:15:08; healthy
2026-05-21T13:25 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~10m); 3 pending; healthy
2026-05-21T13:30 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~15m); 3 pending; healthy
2026-05-21T13:35 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~20m); 3 pending; healthy
2026-05-21T13:40 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~25m); 3 pending; healthy
2026-05-21T13:45 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~30m); 3 pending; healthy
2026-05-21T13:50 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~35m); 3 pending; healthy
2026-05-21T13:55 | GPU=running:wave14zq_continual_8N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zq (wall ~40m); 3 pending; healthy
2026-05-21T14:00 | GPU=running:wave14zt_continual_16N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | zq done (~40m total); GPU on zt since 13:55:08 (wall ~5m); 3 pending; healthy
2026-05-21T14:04 | GPU=running:wave14zt_continual_16N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on zt (wall ~9m); 3 pending; healthy
2026-05-21T14:09 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | pipeline drained: zt + zu (4.6s) + zv (4.7s) + multihop_FHRR_v1 (12.1s) all done; healthy
2026-05-21T14:14 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran wave14r_multihop_hybrid_v1 14:13:19-14:13:40 (21.1s exit 0); healthy
2026-05-21T14:19 | GPU=running:wave14r_multihop_modernhopfield_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on modernhopfield_v1 since 14:18:30; healthy
2026-05-21T14:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU done modernhopfield_v1 at 14:19:03 (32.7s exit 0); healthy
2026-05-21T14:29 | GPU=running:wave14d_multi_task_cl_v2 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on multi_task_cl_v2 since 14:28:09; healthy
2026-05-21T14:34 | GPU=running:wave14d_multi_task_cl_v3 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | v2 done (49.9s); GPU on v3 since 14:30:34 (wall ~3m); healthy
2026-05-21T14:39 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | cleared v3 (400.8s) + parisi_pq_sweep_v1 (51.4s); GPU on zq_kerdock_only since 14:38:06; healthy
2026-05-21T14:44 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~5m); healthy
2026-05-21T14:49 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~10m); 2 pending; healthy
2026-05-21T14:54 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~15m); 2 pending; healthy
2026-05-21T14:59 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~20m); 2 pending; healthy
2026-05-21T15:04 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~25m); 2 pending; healthy
2026-05-21T15:09 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~30m); 2 pending; healthy
2026-05-21T15:14 | GPU=running:wave14zq_continual_8N_kerdock_only | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on zq_kerdock_only (wall ~35m); 2 pending; healthy
2026-05-21T15:19 | GPU=running:wave14zt_continual_16N_kerdock_only | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | zq_kerdock_only done (~40m total); GPU on zt_kerdock_only since 15:18:06; healthy
2026-05-21T15:24 | GPU=running:wave14zt_continual_16N_kerdock_only | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on zt_kerdock_only (wall ~5m); 1 pending; healthy
2026-05-21T15:29 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | zt_kerdock_only FAIL exit=1 (608s experiment-side); cleared bsc_v2_protected (3.3s) + parisi_pq_sweep_v2 (14.2s); pipeline drained; healthy
2026-05-21T15:34 | GPU=running:wave14d_multi_task_cl_v4 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | cleared multihop_soft_cleanup_v1 (54.5s) + multihop_adaptive_beta_v1 (57.3s); GPU on v4 since 15:32:14; healthy
2026-05-21T15:39 | GPU=running:wave14d_multi_task_cl_v4 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v4 (wall ~6m); 1 pending; healthy
2026-05-21T15:44 | GPU=running:wave14d_multi_task_cl_v5 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | cleared cooper_pair_v1 (33.8s) + area_law_probe1 (5.4s); GPU on v5 since 15:43:05; healthy
2026-05-21T15:49 | GPU=running:wave14d_multi_task_cl_v5 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on v5 (wall ~6m); 2 pending; healthy
2026-05-21T15:54 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | v5 done (494.7s); 2 quick FAILs exit=1 (delta_eff_probe2 2.5s + parisi_pq_sweep_v3 3.5s, experiment-side); all idle; healthy
2026-05-21T15:59 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity since 15:51:26; GPU exit ~16:51:26; healthy
2026-05-21T16:04 | GPU=running:wave14r_multihop_largeN_v1 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on multihop_largeN_v1 since 16:03:37; 2 pending; healthy
2026-05-21T16:09 | GPU=running:wave14d_multi_task_cl_v6 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | largeN_v1 done (14.5s); GPU on v6 since 16:03:51 (wall ~5m); 4 pending; healthy
2026-05-21T16:14 | GPU=running:wave14_parisi_pq_sweep_v3b | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | v6 done (479.7s); area_law_probe1_largeN done (28.4s); GPU on parisi_pq_sweep_v3b since 16:12:19; healthy
2026-05-21T16:19 | GPU=running:wave14_parisi_pq_sweep_v3b | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on parisi_pq_sweep_v3b (wall ~6m); 2 pending; healthy
2026-05-21T16:24 | GPU=running:wave14_parisi_pq_sweep_v3b | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on parisi_pq_sweep_v3b (wall ~11m); 2 pending; healthy
2026-05-21T16:29 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | parisi_pq_sweep_v3b FAIL exit=1 (775s experiment-side); cleared delta_eff_probe2b (2.2s) + bsc_v3_protected (17.6s); all idle; healthy
2026-05-21T16:34 | GPU=running:wave14d_multi_task_cl_v7 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU on v7 since 16:29:55 (wall ~4m); 1 pending; healthy
2026-05-21T16:39 | GPU=running:wave14d_multi_task_cl_v7 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v7 (wall ~9m); 1 pending; healthy
2026-05-21T16:44 | GPU=running:wave14d_multi_task_cl_v7 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v7 (wall ~14m); 1 pending; healthy
2026-05-21T16:49 | GPU=running:wave14d_multi_task_cl_v7 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v7 (wall ~19m); 1 pending; healthy
2026-05-21T16:54 | GPU=running:wave14d_multi_task_cl_v7 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v7 (wall ~24m); 1 pending; healthy
2026-05-21T16:59 | GPU=running:wave14d_multi_task_cl_v7 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v7 (wall ~29m); 1 pending; healthy
2026-05-21T17:04 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | v7 done (1970.7s = 33m exit 0); cleared multihop_N8192 (13.6s); all idle; healthy
2026-05-21T17:09 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity since 17:02:59; GPU exit ~18:02:59; healthy
2026-05-21T17:14 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity; healthy
2026-05-21T17:19 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity; healthy
2026-05-21T17:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity since 17:02:59; healthy
2026-05-21T17:29 | GPU=running:wave14_parisi_pq_sweep_v3c | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on parisi_pq_sweep_v3c since 17:24:10 (wall ~4m); healthy
2026-05-21T17:34 | GPU=running:wave14_parisi_pq_sweep_v3c | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on parisi_pq_sweep_v3c (wall ~9m); healthy
2026-05-21T17:39 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | parisi_pq_sweep_v3c FAIL exit=1 (754s; experiment-side - 3rd parisi failure); all idle; healthy
2026-05-21T17:44 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity since 17:36:45; healthy
2026-05-21T17:49 | GPU=running:wave14_parisi_pq_sweep_v3d | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU on parisi_pq_sweep_v3d since 17:46:25 (wall ~2m); healthy
2026-05-21T17:54 | GPU=running:wave14_parisi_pq_sweep_v3d | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on parisi_pq_sweep_v3d (wall ~7m); healthy
2026-05-21T17:59 | GPU=running:wave14_parisi_pq_sweep_v3d | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on parisi_pq_sweep_v3d (wall ~12m); healthy
2026-05-21T18:04 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | parisi_pq_sweep_v3d done (876.5s = 14.6m exit 0); all idle; healthy
2026-05-21T18:09 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity since 18:01:02; GPU exit ~19:01:02; healthy
2026-05-21T18:14 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | no new activity; healthy
2026-05-21T18:19 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran bet_f_sketch5_kerdock_coset_topology 18:14:07-18:14:34 (26.7s exit 0); all idle; healthy
2026-05-21T18:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran multihop_N32768 (11.7s) + bet_f_sketch1_burgers (17.1s); all idle; healthy
2026-05-21T18:29 | GPU=running:wave14_bet_f_label_cardinality_sweep | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | cleared multihop_N2048 (17.5s) + r17_sketch_c_deeper (203.7s); GPU on bet_f_label_cardinality_sweep since 18:28:15; healthy
2026-05-21T18:34 | GPU=running:wave14d_multi_task_cl_v8 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | cleared bet_f_sketch4 (13.6s) + bet_f_sketch3 (10.2s); GPU on v8 since 18:29:23 (wall ~4m); 2 pending; healthy
2026-05-21T18:39 | GPU=running:wave14d_multi_task_cl_v8 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on v8 (wall ~9m); 2 pending; healthy
2026-05-21T18:44 | GPU=running:wave14d_multi_task_cl_v8 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on v8 (wall ~14m); 2 pending; healthy
2026-05-21T18:49 | GPU=running:wave14d_multi_task_cl_v8 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on v8 (wall ~19m); 2 pending; healthy
2026-05-21T18:54 | GPU=running:wave14d_multi_task_cl_v8 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on v8 (wall ~24m); 2 pending; healthy
2026-05-21T18:59 | GPU=running:wave14d_multi_task_cl_v8 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU still on v8 (wall ~29m); 2 pending; healthy
2026-05-21T19:04 | GPU=running:wave14_r17_area_law_N16384 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | v8 done (1935.6s = 32m exit 0); GPU on area_law_N16384 since 19:01:38; healthy
2026-05-21T19:09 | GPU=running:wave14_r17_area_law_N16384 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU still on area_law_N16384 (wall ~7m); 6 pending; healthy
2026-05-21T19:14 | GPU=running:wave14_r17_area_law_N16384 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU still on area_law_N16384 (wall ~12m); 6 pending; healthy
2026-05-21T19:19 | GPU=running:wave14_r17_area_law_N16384 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU still on area_law_N16384 (wall ~17m); 6 pending; healthy
2026-05-21T19:24 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | area_law done; cleared multihop_N1024 (10.9s) + multihop_N65536 (13.4s); GPU on v9 since 19:23:40; healthy
2026-05-21T19:29 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU still on v9 (wall ~5m); 1 pending; healthy
2026-05-21T19:34 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on v9 (wall ~10m); 4 pending; healthy
2026-05-21T19:39 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on v9 (wall ~15m); 4 pending; healthy
2026-05-21T19:44 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on v9 (wall ~20m); 4 pending; healthy
2026-05-21T19:49 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on v9 (wall ~25m); 4 pending; healthy
2026-05-21T19:54 | GPU=running:wave14d_multi_task_cl_v9 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU still on v9 (wall ~30m); 4 pending; healthy
2026-05-21T19:59 | GPU=running:wave14_continual_32N_500edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | v9 done (1973.6s = 33m exit 0); GPU on continual_32N_500edits since 19:56:34; 3 pending; healthy
2026-05-21T20:04 | GPU=running:wave14_r17_area_law_N32768 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | cleared continual_32N_500edits + multihop_NUMFACTS_500 (96.2s) + bet_f_fine_noise (27.2s); GPU on area_law_N32768 since 20:01:13; healthy
2026-05-21T20:09 | GPU=running:wave14_r17_area_law_N32768 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on area_law_N32768 (wall ~7m); healthy
2026-05-21T20:14 | GPU=running:wave14_r17_area_law_N32768 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on area_law_N32768 (wall ~12m); healthy
2026-05-21T20:19 | GPU=running:wave14_r17_area_law_N32768 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU still on area_law_N32768 (wall ~17m); healthy
2026-05-21T20:24 | GPU=running:wave14_r17_area_law_N32768 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU still on area_law_N32768 (wall ~22m); 6 pending; healthy
2026-05-21T20:29 | GPU=running:wave14_r17_area_law_N32768 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU still on area_law_N32768 (wall ~27m); 6 pending; healthy
2026-05-21T20:34 | GPU=running:wave14_continual_2N_1000edits | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | area_law_N32768 done; pipeline ripped through; GPU on continual_2N_1000edits since 20:32:15; healthy
2026-05-21T20:39 | GPU=running:wave14_continual_2N_1000edits | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU still on continual_2N_1000edits (wall ~6m); 6 pending; healthy
2026-05-21T20:44 | GPU=running:wave14d_multi_task_cl_v10_lowreplay | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | cleared continual_2N_1000edits + NUMFACTS_200 (39.5s) + depth_100 (41.4s); GPU on v10_lowreplay since 20:40:28; healthy
2026-05-21T20:49 | GPU=running:wave14d_multi_task_cl_v10_lowreplay | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on v10_lowreplay (wall ~8m); 3 pending; healthy
2026-05-21T20:54 | GPU=running:wave14d_multi_task_cl_v10_lowreplay | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU still on v10_lowreplay (wall ~13m); 3 pending; healthy
2026-05-21T20:59 | GPU=running:wave14d_multi_task_cl_v10_lowreplay | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU still on v10_lowreplay (wall ~18m); 5 pending; healthy
2026-05-21T21:04 | GPU=running:wave14d_multi_task_cl_v10_lowreplay | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU still on v10_lowreplay (wall ~23m); 5 pending; healthy
2026-05-21T21:11 | GPU=running:wave14d_multi_task_cl_v10_lowreplay | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU still on v10_lowreplay (wall ~31m); 5 pending; healthy
2026-05-21T21:16 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU finished v10_lowreplay (BET_B_PASS) + r17_area_law (PASS) + bet_f_N2048 FAIL fast-exit; now on continual_8N; healthy
2026-05-21T21:21 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on continual_8N (wall ~6m); pending unchanged; healthy
2026-05-21T21:25 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on continual_8N (wall ~10m); pending grew 2->3 (betX_skill_composition queued); healthy
2026-05-21T21:29 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on continual_8N (wall ~14m); pending unchanged; healthy
2026-05-21T21:33 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on continual_8N (wall ~18m); pending unchanged; healthy
2026-05-21T21:37 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on continual_8N (wall ~22m); pending unchanged; healthy
2026-05-21T21:41 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on continual_8N (wall ~26m); pending unchanged; healthy
2026-05-21T21:45 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~30m); pending grew 3->4 (R31_S1_pyrkov_cgle queued); healthy
2026-05-21T21:49 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~34m); pending unchanged; healthy
2026-05-21T21:53 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~38m); pending unchanged; healthy
2026-05-21T21:57 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~42m); pending unchanged; healthy
2026-05-21T22:01 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~46m); pending unchanged; healthy
2026-05-21T22:05 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~50m); pending unchanged; healthy
2026-05-21T22:09 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~54m); pending unchanged; healthy
2026-05-21T22:13 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~58m); pending unchanged; healthy
2026-05-21T22:17 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~1h 2m); pending unchanged; healthy
2026-05-21T22:21 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~1h 6m); pending unchanged; healthy
2026-05-21T22:25 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_8N (wall ~1h 10m); pending unchanged; healthy
2026-05-21T22:29 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=12 | pending_cpu=0 | GPU on continual_8N (wall ~1h 14m); pending grew 4->12 (Experiment Dev queued 8 new); healthy
2026-05-21T22:34 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=12 | pending_cpu=0 | GPU on continual_8N (wall ~1h 19m); pending unchanged; healthy
2026-05-21T22:38 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=12 | pending_cpu=0 | GPU on continual_8N (wall ~1h 23m); pending unchanged; healthy
2026-05-21T22:42 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 27m); pending grew 12->14 (R32_M1, betB_kovacs queued); healthy
2026-05-21T22:46 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 31m); pending unchanged; healthy
2026-05-21T22:50 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 35m); pending unchanged; healthy
2026-05-21T22:54 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 39m); pending unchanged; healthy
2026-05-21T22:58 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 43m); pending unchanged; healthy
2026-05-21T23:02 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 47m); pending unchanged; healthy
2026-05-21T23:06 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 51m); pending unchanged; healthy
2026-05-21T23:10 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 55m); pending unchanged; healthy
2026-05-21T23:14 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~1h 59m); pending unchanged; healthy
2026-05-21T23:18 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 3m); pending unchanged; healthy
2026-05-21T23:22 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 7m); pending unchanged; healthy
2026-05-21T23:26 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 11m); pending unchanged; healthy
2026-05-21T23:30 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 15m); pending unchanged; healthy
2026-05-21T23:34 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 19m); pending unchanged; healthy
2026-05-21T23:38 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 23m); pending unchanged; healthy
2026-05-21T23:42 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 27m); pending unchanged; healthy
2026-05-21T23:46 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 31m); pending unchanged; healthy
2026-05-21T23:50 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 35m); pending unchanged; healthy
2026-05-21T23:54 | GPU=running:wave14_continual_8N_2000edits | CPU=exited:None | pending_gpu=14 | pending_cpu=0 | GPU on continual_8N (wall ~2h 39m); pending unchanged; healthy
2026-05-22T07:52 | GPU=running:wave14d_multi_task_cl_v11_per_batch_ema | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | overnight: NUMFACTS_1000 DONE 170s + multihop_depth_200 DONE 34s + continual_8N_5000edits (6h between START lines - likely timed out at 4h, log lines scrolled off); now on v11_per_batch_ema (wall ~28m); pending 14->6; healthy
2026-05-22T07:57 | GPU=running:wave14_parisi_M4N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU rapid progress: v11_per_batch_ema done + NUMENT_500 (30s) + r17_M_stress (12s); now on parisi_M4N (wall ~7s); pending 6->3; healthy
2026-05-22T08:01 | GPU=running:wave14_parisi_M4N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on parisi_M4N (wall ~4m); pending unchanged; healthy
2026-05-22T08:05 | GPU=running:wave14_parisi_M4N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on parisi_M4N (wall ~8m); pending unchanged; healthy
2026-05-22T08:09 | GPU=running:wave14_parisi_M4N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on parisi_M4N (wall ~12m); pending unchanged; healthy
2026-05-22T08:13 | GPU=running:wave14_parisi_M4N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on parisi_M4N (wall ~16m); pending unchanged; healthy
2026-05-22T08:17 | GPU=running:wave14_parisi_M4N | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on parisi_M4N (wall ~20m); pending unchanged; healthy
2026-05-22T08:21 | GPU=running:wave14_continual_N_5000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | parisi_M4N FAIL exit=1 after 1230s; GPU advanced to continual_N_5000edits (wall ~3m); Experiment Dev queued 5 new; pending 3->7; healthy
2026-05-22T08:26 | GPU=running:wave14_continual_N_5000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_N_5000edits (wall ~8m); pending unchanged; healthy
2026-05-22T08:30 | GPU=running:wave14d_betB_kovacs_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU progress: continual_N_5000edits DONE 536s + R32_M1_phasor DONE 28s; now on betB_kovacs_v1 (wall ~3m); pending 7->5; healthy
2026-05-22T08:34 | GPU=running:wave14d_betB_kovacs_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betB_kovacs_v1 (wall ~7m); pending unchanged; healthy
2026-05-22T08:38 | GPU=running:wave14d_betB_kovacs_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betB_kovacs_v1 (wall ~11m); pending unchanged; healthy
2026-05-22T08:42 | GPU=running:wave14d_betB_kovacs_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betB_kovacs_v1 (wall ~15m); pending unchanged; healthy
2026-05-22T08:46 | GPU=running:wave14d_betB_kovacs_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betB_kovacs_v1 (wall ~19m); pending unchanged; healthy
2026-05-22T08:50 | GPU=running:wave14d_betB_kovacs_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betB_kovacs_v1 (wall ~23m); pending unchanged; healthy
2026-05-22T08:54 | GPU=running:wave14d_multi_task_cl_v12_phaseA_boost | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU rapid drain: betB_kovacs done + FHRR_largeN done + FHRR_N8192 (14s) + K50 (12.5s); now on v12_phaseA_boost (wall ~20s); pending 5->1; healthy
2026-05-22T08:58 | GPU=running:wave14d_multi_task_cl_v12_phaseA_boost | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU on v12_phaseA_boost (wall ~4m); pending unchanged; healthy
2026-05-22T09:02 | GPU=running:wave14d_multi_task_cl_v12_phaseA_boost | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU on v12_phaseA_boost (wall ~8m); pending unchanged; healthy
2026-05-22T09:06 | GPU=running:wave14d_multi_task_cl_v12_phaseA_boost | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | GPU on v12_phaseA_boost (wall ~12m); pending grew 1->10 (Experiment Dev queued 9 new); healthy
2026-05-22T09:11 | GPU=running:wave14d_multi_task_cl_v12_phaseA_boost | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | GPU on v12_phaseA_boost (wall ~17m); pending unchanged; healthy
2026-05-22T09:15 | GPU=running:wave14_continual_4N_2000edits | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | v12_phaseA_boost DONE 1070s; GPU advanced to continual_4N_2000edits (wall ~3m); pending 10->9; healthy
2026-05-22T09:19 | GPU=running:wave14_continual_4N_2000edits | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | GPU on continual_4N_2000edits (wall ~7m); pending unchanged; healthy
2026-05-22T09:23 | GPU=running:wave14_continual_4N_2000edits | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | GPU on continual_4N_2000edits (wall ~11m); pending unchanged; healthy
2026-05-22T09:27 | GPU=running:wave14_continual_4N_2000edits | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | GPU on continual_4N_2000edits (wall ~15m); pending unchanged; healthy
2026-05-22T09:31 | GPU=running:wave14_continual_4N_2000edits | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | GPU on continual_4N_2000edits (wall ~19m); pending unchanged; healthy
2026-05-22T09:35 | GPU=running:wave14_continual_4N_2000edits | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | GPU on continual_4N_2000edits (wall ~23m); pending unchanged; healthy
2026-05-22T09:39 | GPU=running:wave14r_multihop_NUMFACTS_2000 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | continual_4N_2000edits FAIL exit=4294967295 (Win32 -1, abnormal) after 1540s; runner advanced to multihop_NUMFACTS_2000 (wall ~2m); pending 9->8; healthy
2026-05-22T09:44 | GPU=running:wave14d_multi_task_cl_v13_a05 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU rapid drain: NUMFACTS_2000 + K10 + K100 (scrolled) + N12288 (11s) + NUMFACTS_300 (27s); now on v13_a05 (wall ~3m); pending 8->3; healthy
2026-05-22T09:54 | GPU=running:wave14d_multi_task_cl_v13_a05 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on v13_a05 (wall ~13m); pending unchanged; healthy
2026-05-22T09:59 | GPU=running:wave14_r17_N12288 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | v13_a05 DONE 809s; GPU advanced to r17_N12288 (wall ~5m); pending 3->2; healthy
2026-05-22T10:03 | GPU=running:wave14_r17_N12288 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on r17_N12288 (wall ~8m); pending unchanged; healthy
2026-05-22T10:07 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | r17_N12288 DONE 588s; continual_16N_1000edits FAIL exit=1 fast 5.7s; GPU now on continual_2N_10000edits (wall ~3m); pending refilled 2->7; healthy
2026-05-22T10:11 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~7m); pending unchanged; healthy
2026-05-22T10:15 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~10m); pending unchanged; healthy
2026-05-22T10:19 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~14m); pending unchanged; healthy
2026-05-22T10:23 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~18m); pending unchanged; healthy
2026-05-22T10:27 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~22m); pending unchanged; healthy
2026-05-22T10:31 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~26m); pending unchanged; healthy
2026-05-22T10:35 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~30m); pending unchanged; healthy
2026-05-22T10:39 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~34m); pending unchanged; healthy
2026-05-22T10:43 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~38m); pending unchanged; healthy
2026-05-22T10:47 | GPU=running:wave14_continual_2N_10000edits | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on continual_2N_10000edits (wall ~42m); pending unchanged; healthy
2026-05-22T10:51 | GPU=running:wave14r_multihop_NUMFACTS_600 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | continual_2N_10000edits DONE 2743s (45.7m); GPU advanced to multihop_NUMFACTS_600 (wall ~22s); pending 7->6; healthy
2026-05-22T10:55 | GPU=running:wave14d_multi_task_cl_v14_a05 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU rapid drain: NUMFACTS_600 + K5 + K30 (scrolled) + NUMENT_100 (13s) + NUMENT_300 (14.5s); now on v14_a05 (wall ~2.5m); pending 6->1; healthy
2026-05-22T11:00 | GPU=running:wave14d_multi_task_cl_v14_a05 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | GPU on v14_a05 (wall ~7.5m); pending unchanged; healthy
2026-05-22T11:04 | GPU=running:wave14d_multi_task_cl_v14_a05 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on v14_a05 (wall ~11.5m); pending grew 1->4 (betY_modern_dense_AM, R27_L2_dynamic_W, betP_engineering_proxy queued); healthy
2026-05-22T11:08 | GPU=running:wave14_continual_2N_3000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | v14_a05 DONE 836s; GPU advanced to continual_2N_3000edits (wall ~2m); pending 4->3; healthy
2026-05-22T11:12 | GPU=running:wave14_continual_2N_3000edits | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on continual_2N_3000edits (wall ~6m); pending unchanged; healthy
2026-05-22T11:16 | GPU=running:wave14_continual_2N_3000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_2N_3000edits (wall ~10m); pending grew 3->4 (betY_phase1_beta_calibration queued); healthy
2026-05-22T11:20 | GPU=running:wave14_continual_2N_3000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_2N_3000edits (wall ~14m); pending unchanged; healthy
2026-05-22T11:24 | GPU=running:wave14_continual_2N_3000edits | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on continual_2N_3000edits (wall ~18m); pending unchanged; healthy
2026-05-22T11:29 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU drained queue: continual_2N_3000edits (scrolled) + R27_L2_dynamic_W (4s) + betP_engineering_proxy (7s) + betY_phase1_beta_calibration FAIL (179s); now alive+idle pending=0; invariant n/a; healthy (Experiment Dev needs to refill)
2026-05-22T11:34 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU blitzed 3 fast experiments: betU_decay099 (2s) + betV_largeN (2s) + betQ_M4N (5s); now alive+idle+pending=0; invariant n/a; healthy
2026-05-22T11:39 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran delta_lambda_drift_v1 (10s) since last cycle; now alive+idle+pending=0; invariant n/a; healthy
2026-05-22T11:43 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU ran lane_D_cognitive_arch (2s) since last cycle; now alive+idle+pending=0; invariant n/a; healthy
2026-05-22T11:47 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle since 11:41:28 (~5.5m idle); pending=0; invariant n/a; healthy
2026-05-22T11:51 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | betY_phase2_v1 FAIL exit=1 fast 7s; runner picked up v2 (wall ~1m); pending=0; healthy
2026-05-22T11:55 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~5m); pending grew 0->2 (lane_D_end_to_end + capacity_stress queued); healthy
2026-05-22T11:59 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~9m); pending unchanged; healthy
2026-05-22T12:03 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~13m); pending unchanged; healthy
2026-05-22T12:07 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~17m); pending unchanged; healthy
2026-05-22T12:11 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~21m); pending unchanged; healthy
2026-05-22T12:15 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~25m); pending unchanged; healthy
2026-05-22T12:19 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~29m); pending unchanged; healthy
2026-05-22T12:23 | GPU=running:wave14_betY_phase2_kerdock_betacalibrated_v2 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | GPU on betY_phase2_v2 (wall ~33m); pending unchanged; healthy
2026-05-22T12:27 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | betY_phase2_v2 DONE 2149s (35.8m) + lane_D_end_to_end (5.8s) + lane_D_capacity_stress (2.7s); now alive+idle+pending=0; invariant n/a; healthy
2026-05-22T12:31 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~5m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:35 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~9m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:39 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~13m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:43 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~17m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:47 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~21m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:51 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~25m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:55 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~29m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T12:59 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~33m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T13:03 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~37m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T13:07 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~41m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T13:11 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~45m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T13:15 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~49m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T13:19 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~53m (last DONE 12:25:23); pending=0; invariant n/a; healthy
2026-05-22T13:23 | GPU=idle:None | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | Experiment Dev queued betY_phase2_beta_blend_v1; runner alive+idle hasnt picked up yet (POLL_INTERVAL race, expect claim within 30s); watch for persistence next cycle; healthy
2026-05-22T13:28 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | runner claimed betY_phase2_beta_blend_v1 at 13:22:37 (POLL race resolved); now wall ~5m; pending 1->2 (lane_D N_scaling + noise_robust queued); healthy
2026-05-22T13:32 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~9m); pending grew 2->3 (betR_pbody_polynomial queued); healthy
2026-05-22T13:36 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~13m); pending unchanged; healthy
2026-05-22T13:40 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | snapshot stale (wrapper 13:39:57 vs embedded heartbeat 13:36:44, gap 3:13>2min); SSH fallback confirmed live heartbeat 13:40:44 alive+running; Visibility snapshot domain not Queue Health; runner healthy
2026-05-22T13:45 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | snapshot recovered (heartbeat 13:44:44 fresh); GPU on betY_phase2_beta_blend_v1 (wall ~22m); pending unchanged; healthy
2026-05-22T13:50 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~27m); pending unchanged; healthy
2026-05-22T13:54 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~31m); pending unchanged; healthy
2026-05-22T13:58 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~35m); pending unchanged; healthy
2026-05-22T14:02 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~39m); pending unchanged; healthy
2026-05-22T14:06 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~43m); pending unchanged; healthy
2026-05-22T14:10 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~47m); pending unchanged; healthy
2026-05-22T14:14 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~51m); pending unchanged; healthy
2026-05-22T14:18 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~55m); pending unchanged; healthy
2026-05-22T14:22 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~59m); pending unchanged; healthy
2026-05-22T14:26 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 3m); pending unchanged; healthy
2026-05-22T14:30 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 7m); pending grew 3->4 (observability_suite_v1 queued); healthy
2026-05-22T14:34 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 11m); pending grew 4->5 (betS_K_ceiling_N65536 queued); healthy
2026-05-22T14:38 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 15m); pending unchanged; healthy
2026-05-22T14:42 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 19m); pending unchanged; healthy
2026-05-22T14:46 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 23m); pending unchanged; healthy
2026-05-22T14:50 | GPU=running:wave14_betY_phase2_beta_blend_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU on betY_phase2_beta_blend_v1 (wall ~1h 27m); pending grew 5->6 (betZ_srht_readout queued); healthy
2026-05-22T14:54 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | betY_phase2_beta_blend_v1 DONE (scrolled) + lane_D_N_scaling (3.8s) + lane_D_noise_robust (12.2s); now on betR_pbody_polynomial (wall ~1m); pending 6->3; healthy
2026-05-22T14:58 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~5m); pending grew 3->4 (betZ_c2po queued); healthy
2026-05-22T15:02 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~9m); pending unchanged; healthy
2026-05-22T15:06 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~13m); pending unchanged; healthy
2026-05-22T15:10 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~17m); pending unchanged; healthy
2026-05-22T15:14 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~21m); pending grew 4->5 (betS_K_ceiling_diagnosis queued); healthy
2026-05-22T15:18 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~25m); pending unchanged; healthy
2026-05-22T15:22 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~29m); pending unchanged; healthy
2026-05-22T15:26 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~33m); pending grew 5->6 (betV_N65536 queued); healthy
2026-05-22T15:30 | GPU=running:wave14_betR_pbody_polynomial_v1 | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | GPU on betR_pbody_polynomial (wall ~37m); pending grew 6->7 (multihop_K100_N65536 queued); healthy
2026-05-22T15:36 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | betR_pbody_polynomial DONE 2540.3s exit 0; claimed observability_suite_v1 (wall ~47s); healthy
2026-05-22T15:41 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | observability_suite (wall ~5m47s); pending stable; healthy
2026-05-22T15:45 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | observability_suite (wall ~9m45s); pending stable; healthy
2026-05-22T15:50 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | observability_suite (wall ~14m45s); pending grew 6->8 (hessian_vdos, musr_kubo_toyabe queued); healthy
2026-05-22T15:54 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | observability_suite (wall ~18m45s); pending stable; healthy
2026-05-22T15:58 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | observability_suite (wall ~22m45s); pending stable; healthy
2026-05-22T16:02 | GPU=running:wave14_observability_suite_v1 | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | observability_suite (wall ~26m45s); pending grew 8->9 (lane_C_compliance_audit_FULL queued); healthy
2026-05-22T18:04 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | ~2h gap since cycle 314; observability_suite completed off-window; betS_K_ceiling_N65536 DONE 3.3s exit 0; betZ_srht_readout DONE 2.0s exit 0; now on betZ_c2po (wall ~28m34s); pending 9->6 (3 consumed); healthy
2026-05-22T18:08 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | betZ_c2po (wall ~33m20s); pending stable; healthy
2026-05-22T18:12 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | betZ_c2po (wall ~37m20s); pending stable; healthy
2026-05-22T18:17 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=6 | pending_cpu=0 | betZ_c2po (wall ~42m20s); pending stable; healthy
2026-05-22T18:21 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | betZ_c2po (wall ~46m20s); pending grew 6->8 (kerdock_AMP_universality_pretest, pseudoinverse_capacity queued); healthy
2026-05-22T18:25 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | betZ_c2po (wall ~50m20s); pending stable; healthy
2026-05-22T18:29 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | betZ_c2po (wall ~54m20s); pending stable; healthy
2026-05-22T18:33 | GPU=running:wave14_betZ_c2po_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | betZ_c2po (wall ~58m20s); pending stable; healthy
2026-05-22T18:37 | GPU=running:wave14_multihop_K100_N65536_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | betZ_c2po finished ~18:37:21 (rolled off window, wall ~62m); betS_K_ceiling_diagnosis DONE 2.2s exit 0; betV_N65536 DONE 2.4s exit 0; now on multihop_K100_N65536 (wall ~13s); pending 8->5 (3 consumed); healthy
2026-05-22T18:42 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | queue drained; lane_C_compliance_audit_FULL DONE 4.9s exit 0; kerdock_AMP_universality_pretest DONE 3.1s exit 0; pseudoinverse_capacity DONE 6.2s exit 0 (PINV_PASS); multihop_K100_N65536 also DONE (rolled off window); runner idle since ~18:40:49 (alive); invariant n/a (pending=0); healthy
2026-05-22T18:47 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~7m since 18:40:49; invariant n/a; healthy
2026-05-22T18:51 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | pseudoinverse_basin_width_v1 DONE 3.3s exit 0 (BASIN_NARROW r=0.050); GPU idle ~2m since 18:49:32; invariant n/a; healthy
2026-05-22T18:56 | GPU=running:wave14_one_over_f_noise_spectroscopy_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | pseudoinverse_kerdock_combo DONE 23.2s exit 0; now on one_over_f_noise_spectroscopy (wall ~1m42s); pending=0 (just claimed); healthy
2026-05-22T19:01 | GPU=running:wave14_ac_susceptibility_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | one_over_f_noise_spectroscopy DONE 138.4s exit 0; now on ac_susceptibility (wall ~4m8s); pending=1 (multihop_resonator_N65536); healthy
2026-05-22T19:05 | GPU=running:wave14_multihop_resonator_N65536_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | ac_susceptibility DONE 417.8s exit 0 (CHI_FLAT); now on multihop_resonator_N65536 (wall ~1m11s); pending=1 (multihop_spectral_validation); healthy
2026-05-22T19:10 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | multihop_resonator_N65536 DONE 89.8s exit 0; now on multihop_spectral_validation (wall ~4m41s); pending=1 (multihop_K_scaling_N65536); healthy
2026-05-22T19:14 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | multihop_spectral_validation (wall ~8m20s); pending stable; healthy
2026-05-22T19:19 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | multihop_spectral_validation (wall ~13m20s); pending stable; healthy
2026-05-22T19:23 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | multihop_spectral_validation (wall ~17m20s); pending grew 1->3 (bidirectional_N65536, sparse_cleanup_N65536 queued); healthy
2026-05-22T19:27 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | multihop_spectral_validation (wall ~21m20s); pending stable; healthy
2026-05-22T19:31 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | multihop_spectral_validation (wall ~25m20s); pending stable; healthy
2026-05-22T19:35 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | multihop_spectral_validation (wall ~29m20s); pending stable; healthy
2026-05-22T19:40 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | multihop_spectral_validation (wall ~34m20s); pending stable; healthy
2026-05-22T19:44 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | multihop_spectral_validation (wall ~38m20s); pending grew 3->4 (multihop_hub_census queued); healthy
2026-05-22T19:48 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | multihop_spectral_validation (wall ~42m20s); pending grew 4->5 (multihop_vamp_chain_N65536 queued); healthy
2026-05-22T19:52 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | multihop_spectral_validation (wall ~46m20s); pending stable; healthy
2026-05-22T19:56 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | multihop_spectral_validation (wall ~50m20s); pending stable; healthy
2026-05-22T20:01 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | multihop_spectral_validation (wall ~54m50s); pending stable; healthy
2026-05-22T20:05 | GPU=running:wave14_multihop_spectral_validation_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | multihop_spectral_validation (wall ~59m20s); pending stable; healthy
2026-05-22T20:09 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | queue drained; multihop_spectral_validation completed off-window plus blitz: sparse_cleanup_N65536 DONE 6.2s exit 0; hub_census DONE 2.1s exit 0; vamp_chain_N65536 DONE 11.9s exit 0 (VAMPCHAIN_RESTORES acc_50hop=1.000); GPU idle ~3m since 20:06:30; invariant n/a; healthy
2026-05-22T20:14 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~8m since 20:06:30; invariant n/a; healthy
2026-05-22T20:19 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | vamp_chain_depth_ceiling DONE 35.8s; vamp_chain_K_stress DONE 106.3s; vamp_chain_noise_robust DONE 16.9s (VAMPNOISE_ROBUST acc(p=0.10)=1.000); GPU idle ~1m since 20:18:25; invariant n/a; healthy
2026-05-22T20:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | vamp_chain_extreme_stress_v1 FAIL exit=1 after 32.5s (smoke produced EXTREME_MID acc=1.0 K=10000/depth=300; full crashed - Experiment Dev concern); runner handled, idle ~3m since 20:21:52; healthy
2026-05-22T20:29 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~8m since 20:21:52; no activity since cycle 347; invariant n/a; healthy
2026-05-22T20:33 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~12m since 20:21:52; invariant n/a; healthy
2026-05-22T20:37 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | lane_D_end_to_end_N65536_vamp DONE 3.5s exit 0; betZ3_vamp_single_hop_v2 DONE 2.7s exit 0 (BET_Z3_VAMP_PARTIAL); GPU idle ~50s since 20:36:49; invariant n/a; healthy
2026-05-22T20:42 | GPU=running:wave14_betC_M_N_capacity_N65536_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | betC_M_N_capacity_N65536 START 20:40:10 (wall ~2m32s); pending=0 (just claimed); healthy
2026-05-22T20:47 | GPU=running:wave14_betC_M_N_capacity_N65536_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | betC_M_N_capacity_N65536 (wall ~7m31s); pending=0; healthy
2026-05-22T20:51 | GPU=running:wave14_betC_M_N_capacity_N65536_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | betC_M_N_capacity_N65536 (wall ~11m29s); pending=0; healthy
2026-05-22T20:56 | GPU=running:wave14_betC_M_N_capacity_N65536_v1 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | betC_M_N_capacity_N65536 (wall ~16m28s); pending grew 0->2 (multihop_hmm_three_way, betA_continual_edit_N65536 queued); healthy
2026-05-22T21:01 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | betC_M_N_capacity_N65536 completed off-window; multihop_hmm_three_way DONE 12.6s exit 0; betA_continual_edit_N65536 FAIL exit=1 22.6s; multihop_hmm_geometric_scaling DONE 9.2s exit 0 (GEOMETRIC_FALSIFIED); GPU idle ~2m since 20:59:49; healthy
2026-05-22T21:06 | GPU=running:wave14_multihop_resonator_warmstart_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | multihop_hmm_per_hop_pfail DONE 97.5s exit 0; now on multihop_resonator_warmstart (wall ~59s, smoke WARMSTART_RESCUES acc_50hop=1.000); pending=0 (claimed); healthy
2026-05-22T21:11 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | multihop_resonator_warmstart DONE 55.2s exit 0 (WARMSTART_RESCUES acc_50hop=1.000); GPU idle ~5m since 21:06:37; invariant n/a; healthy
2026-05-22T21:16 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | vamp_chain_N_sweep_v2 DONE 6.7s exit 0; multihop_hmm_K_scaling DONE 8.8s exit 0 (HMMK_INCONCLUSIVE); GPU idle ~29s since 21:16:13; healthy
2026-05-22T21:21 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | chain_smoother_only_v2 DONE 5.0s exit 0; chain_smoother_K_stress FAIL exit=1 33.7s; chain_smoother_depth_ceiling DONE 36.1s exit 0 (SMOOTHER_DEPTH_HIGH d=500 acc=1.0); GPU idle ~50s since 21:20:52; healthy
2026-05-22T21:26 | GPU=running:wave14_chain_smoother_mega_characterization_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | chain_smoother_n_sweep DONE 5.7s exit 0; chain_smoother_extreme_K FAIL exit=1 2.3s; now on chain_smoother_mega_characterization (wall ~1m21s, smoke MEGA_BROAD_ENVELOPE 3/3); healthy
2026-05-22T21:31 | GPU=running:wave14_smoother_validation_matrix_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | smoother_mega_variant4 DONE 3.3s; variant5 DONE 3.0s; now on smoother_validation_matrix (wall ~1m21s, smoke MATRIX_BROAD_VALIDATED 16/16); healthy
2026-05-22T21:36 | GPU=running:wave14_smoother_validation_matrix_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | smoother_validation_matrix (wall ~6m25s); pending grew 0->3 (cluster_census_N65536, W_L_effective_rank, cluster_census_N_sweep queued); healthy
2026-05-22T21:41 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | smoother_validation_matrix FAIL exit=1 389.7s; cluster_census_N65536 DONE 4.8s exit 0; now on W_L_effective_rank (wall ~4m51s); pending grew to 4 (cluster_census_N_sweep, lane_D_end_to_end_N65536_smoother, W_endpoint_injection, demo_2_lane_C_multihop_N65536); healthy
2026-05-22T21:46 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | W_L_effective_rank (wall ~9m47s); pending stable; healthy
2026-05-22T21:51 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | W_L_effective_rank (wall ~14m51s); pending stable; healthy
2026-05-22T21:56 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | W_L_effective_rank (wall ~19m47s); pending stable; healthy
2026-05-22T22:00 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | W_L_effective_rank (wall ~23m52s); pending stable; healthy
2026-05-22T22:04 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | W_L_effective_rank (wall ~27m51s); pending grew 4->5 (cluster_identity_diagnostic queued); healthy
2026-05-22T22:09 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | W_L_effective_rank (wall ~32m50s); pending grew 5->8 (cluster_basin_size, substrate_N131072, multi_target_disambiguation queued); healthy
2026-05-22T22:14 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | W_L_effective_rank (wall ~37m57s); pending grew 8->10 (substrate_cross_task_transfer, betG_TEMPSCALE_N65536 queued); healthy
2026-05-22T22:19 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | W_L_effective_rank (wall ~42m57s); pending stable; healthy
2026-05-22T22:23 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | W_L_effective_rank (wall ~46m57s); pending stable; healthy
2026-05-22T22:28 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | W_L_effective_rank (wall ~51m57s); pending stable; healthy
2026-05-22T22:32 | GPU=running:wave14_W_L_effective_rank_v1 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | W_L_effective_rank (wall ~55m57s); pending stable; healthy
2026-05-22T22:37 | GPU=running:wave14_cluster_identity_diagnostic_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | W_L_effective_rank_v1 completed off-window; lane_D_end_to_end_N65536_smoother off-window; W_endpoint_injection DONE 3.1s exit 0; demo_2_lane_C_multihop_N65536 DONE 4.1s exit 0; now on cluster_identity_diagnostic (wall ~27s); pending 10->5 (5 consumed); healthy
2026-05-22T22:42 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | queue drained; final batch: multi_target_disambiguation DONE 9.2s; substrate_cross_task_transfer DONE 7.5s; betG_TEMPSCALE_N65536 DONE 2.5s (BETG_N65K_KILLED ECE=0.85); GPU idle ~5m since 22:37:46; invariant n/a; healthy
2026-05-22T22:47 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~10m since 22:37:46; invariant n/a; healthy
2026-05-22T22:51 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~14m since 22:37:46; invariant n/a; healthy
2026-05-22T22:55 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~18m since 22:37:46; invariant n/a; healthy
2026-05-22T22:59 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~22m since 22:37:46; invariant n/a; healthy
2026-05-22T23:03 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~26m since 22:37:46; invariant n/a; healthy
2026-05-22T23:08 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~30m since 22:37:46; invariant n/a; healthy
2026-05-22T23:12 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~35m since 22:37:46; invariant n/a; healthy
2026-05-22T23:16 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~39m since 22:37:46; invariant n/a; healthy
2026-05-22T23:20 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~43m since 22:37:46; invariant n/a; healthy
2026-05-22T23:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~47m since 22:37:46; invariant n/a; healthy
2026-05-22T23:29 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~52m since 22:37:46; ~8m to idle-exit; invariant n/a; healthy
2026-05-22T23:33 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~56m since 22:37:46; ~4m to idle-exit; invariant n/a; healthy
2026-05-22T23:38 | GPU=running:wave14_heavy_validation_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | runner did NOT idle-exit (claimed heavy_validation_v1 at 23:35:50, just before 23:37:46 cutoff); wall ~2m47s; pending=1 (retraction_phase1_combined_v1); healthy
2026-05-22T23:43 | GPU=running:wave14_heavy_validation_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | heavy_validation (wall ~7m47s); pending stable; healthy
2026-05-22T23:48 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | heavy_validation FAIL exit=1 736.9s; runner immediately claimed retraction_phase1_combined (wall ~30s, smoke RETRACT_REFUTED 0/3); pending=0; healthy
2026-05-22T23:53 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | retraction_phase1_combined (wall ~5m29s); pending=0; healthy
2026-05-22T23:58 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | retraction_phase1_combined (wall ~10m29s); pending=0; healthy
2026-05-23T00:02 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | retraction_phase1_combined (wall ~14m29s); pending=0; healthy
2026-05-23T00:07 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | retraction_phase1_combined (wall ~19m29s); pending=0; healthy
2026-05-23T00:11 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | retraction_phase1_combined (wall ~23m29s); pending=0; healthy
2026-05-23T00:16 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | retraction_phase1_combined (wall ~28m11s); pending grew 0->8 (smoother_burst_1..8 queued); healthy
2026-05-23T00:21 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined (wall ~33m11s); pending grew 8->11 (substrate_limit_cycle_period, demo_1_smoother_5seed, substrate_N262144 queued); healthy
2026-05-23T00:26 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined (wall ~38m11s); pending stable; healthy
2026-05-23T00:30 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined (wall ~42m11s); pending stable; healthy
2026-05-23T00:35 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined (wall ~47m11s); pending stable; healthy
2026-05-23T00:40 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined (wall ~52m11s); pending stable; healthy
2026-05-23T00:44 | GPU=running:wave14_retraction_phase1_combined_v1 | CPU=exited:None | pending_gpu=21 | pending_cpu=0 | retraction_phase1_combined (wall ~56m11s); pending grew 11->21 (overnight_1..10 queued - large overnight batch); healthy
2026-05-23T00:49 | GPU=running:wave14_overnight_1_v1 | CPU=exited:None | pending_gpu=9 | pending_cpu=0 | retraction_phase1_combined finished off-window; 11 experiments consumed in ~5min (smoother_burst_1..8, substrate_limit_cycle_period, demo_1_smoother_5seed DONE 4.6s, substrate_N262144 DONE 4.9s); now on overnight_1 (wall ~25s); pending 21->9; healthy
2026-05-23T00:54 | GPU=running:wave14_overnight_3_v1 | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | overnight_1 DONE 122.8s exit 0; overnight_2 DONE 124.2s exit 0; now on overnight_3 (wall ~1m16s); pace ~2min/exp; pending=7; healthy
2026-05-23T00:59 | GPU=running:wave14_overnight_5_v1 | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | overnight_3 DONE 123.1s; overnight_4 DONE 123.4s; now on overnight_5 (wall ~2m9s); pace ~123s/exp; pending=5; healthy
2026-05-23T01:03 | GPU=running:wave14_overnight_7_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | overnight_5 DONE 123.0s; overnight_6 DONE 125.6s; now on overnight_7 (wall ~2m); pending=3; healthy
2026-05-23T01:08 | GPU=running:wave14_overnight_10_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | overnight_8 DONE 123.5s; overnight_9 DONE 123.6s (ON_ENVELOPE 24/24); now on overnight_10 (wall ~51s, last in batch); pending=0; healthy
2026-05-23T01:13 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | overnight_10 DONE 123.5s exit 0 (ON_ENVELOPE 24/24); overnight batch complete (10/10 clean); GPU idle ~3m48s since 01:09:55; invariant n/a; healthy
2026-05-23T01:18 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~8m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:23 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~13m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:28 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~18m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:33 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~23m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:38 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~28m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:42 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~32m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:47 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~37m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:52 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~42m47s since 01:09:55; invariant n/a; healthy
2026-05-23T01:57 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~47m47s since 01:09:55; ~12m to idle-exit; invariant n/a; healthy
2026-05-23T02:02 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~52m47s since 01:09:55; ~7m to idle-exit; invariant n/a; healthy
2026-05-23T02:07 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU alive+idle ~57m47s since 01:09:55; ~2m to idle-exit; invariant n/a; healthy
2026-05-23T02:12 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle-exited gracefully at 02:09:53 after ~60min idle; both runners now exited; invariant n/a (pending=0); if Experiment Dev queues more, runner needs relaunch (not Queue Health domain); healthy
2026-05-23T02:17 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | both runners exited; pending=0; invariant n/a; healthy
2026-05-23T02:21 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | both runners exited; pending=0; invariant n/a; healthy
2026-05-23T02:26 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | both runners exited; pending=0; invariant n/a; healthy
2026-05-23T02:30 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | both runners exited; pending=0; invariant n/a; healthy
2026-05-23T02:34 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | both runners exited; pending=0; invariant n/a; healthy
2026-05-23T02:38 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | both runners exited (steady state); pending=0; invariant n/a; healthy
2026-05-23T02:43 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T02:47 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T02:51 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T02:55 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T02:59 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:03 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:07 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:12 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:16 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:20 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:24 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:29 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:33 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:37 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:41 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:45 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:50 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:54 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T03:58 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:03 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:08 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:12 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:17 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:21 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:25 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:29 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:33 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:37 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:42 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:47 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:51 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T04:56 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:00 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:04 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:09 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:15 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:19 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:24 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:28 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:33 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:37 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:42 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:47 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:51 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T05:56 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:00 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:04 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:09 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:14 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:18 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:23 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:28 | GPU=exited:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | steady state; healthy
2026-05-23T06:33 | GPU=exited:None | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | **INVARIANT VIOLATION**: pending_gpu=5 (limit_cycle_N_sweep, limit_cycle_K_sweep, betA_continual_edit_v2, retraction_phase1_combined_v2, heavy_validation_v2) but GPU exited (since 02:09:53 idle-exit) and not PAUSED; runner needs relaunch (Strategy/META domain); ALERT raised in queue_health_alert.md
2026-05-23T06:38 | GPU=exited:None | CPU=exited:None | pending_gpu=5 | pending_cpu=0 | INVARIANT VIOLATION persists (no change since 06:33); pending unchanged; GPU still exited; alert active
2026-05-23T06:43 | GPU=running:claimed_at_relaunch | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | INVARIANT RESTORED: ran tools/cutover.py --gpu-only on marsh@home; new GPU runner pid=200624 (launcher 189832); status=running (already claimed an experiment from pending=5); alert cleared
2026-05-23T06:44 | GPU=running:wave14_limit_cycle_K_sweep_v1 | CPU=exited:None | pending_gpu=stale_snapshot | pending_cpu=0 | snapshot stale (wrapper 06:43:40, embedded heartbeat 02:09:53; lag ~4h34m); SSH fallback per cycle 52 pattern shows live heartbeat ts=06:44:09 pid=200624 status=running current=limit_cycle_K_sweep; invariant satisfied; healthy
2026-05-23T06:49 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | snapshot now fresh (heartbeat ts 06:48:09); K_sweep DONE 55.7s exit 0 (PERIOD_K_SCALES); betA_continual_edit_v2 FAIL exit=1 20s; N_sweep off-window; now on retraction_phase1_combined_v2 (wall ~5m1s); pending dropped 5->1; healthy
2026-05-23T06:54 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~10m1s); pending stable; healthy
2026-05-23T06:59 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~15m1s); pending grew 1->7 (K_resonance_fine_sweep, K_resonance_wide_sweep, demo_1_K1000_smoother, forward_argmax_K1000, substrate_N524288, vamp_vs_smoother_head_to_head queued); healthy
2026-05-23T07:04 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=7 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~20m1s); pending stable; healthy
2026-05-23T07:09 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~25m1s); pending grew 7->8 (K1000_eigenspectrum_check queued); healthy
2026-05-23T07:14 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~30m1s); pending grew 8->11 (chi4_dynamic_overlap, K_ceiling_critical_exponents, substrate_order_parameter queued); healthy
2026-05-23T07:19 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~35m1s); pending stable; healthy

2026-05-23T07:25 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~40m11s); pending stable; healthy
2026-05-23T07:30 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~44m41s); pending stable; healthy
2026-05-23T07:34 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~48m41s); pending stable; healthy
2026-05-23T07:38 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~52m41s); pending stable; healthy
2026-05-23T07:41 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~56m12s); pending stable; healthy
2026-05-23T07:45 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~1h0m12s); pending stable; healthy
2026-05-23T07:49 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~1h4m12s); pending stable; healthy
2026-05-23T07:54 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~1h8m42s); pending stable; healthy
2026-05-23T07:58 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~1h13m12s); pending stable; healthy
2026-05-23T08:02 | GPU=running:wave14_retraction_phase1_combined_v2 | CPU=exited:None | pending_gpu=11 | pending_cpu=0 | retraction_phase1_combined_v2 (wall ~1h17m12s); pending stable; healthy
2026-05-23T08:06 | GPU=running:wave14_heavy_validation_v2 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | retraction_phase1_combined_v2 DONE 08:03:13 (4695.2s, exit 0); heavy_validation_v2 START 08:03:13 (wall ~3m22s); pending 11->10; healthy
2026-05-23T08:10 | GPU=running:wave14_heavy_validation_v2 | CPU=exited:None | pending_gpu=10 | pending_cpu=0 | heavy_validation_v2 (wall ~6m57s); pending stable; healthy
2026-05-23T08:15 | GPU=running:wave14_K_resonance_wide_sweep_v1 | CPU=exited:None | pending_gpu=8 | pending_cpu=0 | heavy_validation_v2 FAIL 08:11:47 (513.7s, exit 1); K_resonance_fine_sweep_v1 DONE 08:12:09 (22.4s, exit 0); K_resonance_wide_sweep_v1 START 08:12:09 (wall ~2m31s); pending 10->8; healthy
2026-05-23T08:19 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | substrate_N524288_v1 DONE 08:15:30 (5.4s); vamp_vs_smoother_head_to_head_v1 DONE 08:16:06 (35.8s); K1000_eigenspectrum_check_v1 START 08:16:06 (wall ~3m4s); pending 8->3 fast drain; healthy
2026-05-23T08:23 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~7m4s); pending stable; healthy
2026-05-23T08:27 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~11m4s); pending stable; healthy
2026-05-23T08:31 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~15m4s); pending stable; healthy
2026-05-23T08:35 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~19m4s); pending stable; healthy
2026-05-23T08:40 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~23m34s); pending stable; healthy
2026-05-23T08:43 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~27m4s); pending stable; healthy
2026-05-23T08:47 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~31m4s); pending stable; healthy
2026-05-23T08:51 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~35m4s); pending stable; healthy
2026-05-23T08:56 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~39m34s); pending stable; healthy
2026-05-23T09:00 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~44m4s); pending stable; healthy
2026-05-23T09:05 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~48m34s); pending stable; healthy
2026-05-23T09:09 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~52m34s); pending stable; healthy
2026-05-23T09:13 | GPU=running:wave14_K1000_eigenspectrum_check_v1 | CPU=exited:None | pending_gpu=3 | pending_cpu=0 | K1000_eigenspectrum_check_v1 (wall ~56m34s); pending stable; healthy
2026-05-23T09:17 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | queue drained — chi4_dynamic_overlap DONE 09:16:23 (16.8s); K_ceiling_critical_exponents DONE 09:16:26 (3.1s); substrate_order_parameter DONE 09:16:32 (5.7s); runner alive+idle, 60min countdown begins; healthy
2026-05-23T09:22 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~5min (last DONE 09:16:32); 60min idle-exit countdown active; healthy
2026-05-23T09:26 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~9min (last DONE 09:16:32); 60min idle-exit countdown active; healthy
2026-05-23T09:30 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~13.5min (last DONE 09:16:32); 60min idle-exit countdown active (~46m left); healthy
2026-05-23T09:34 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~17.5min (last DONE 09:16:32); 60min idle-exit countdown (~42m left); healthy
2026-05-23T09:37 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~21min (last DONE 09:16:32); 60min idle-exit countdown (~39m left); healthy
2026-05-23T09:41 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~25min (last DONE 09:16:32); 60min idle-exit countdown (~35m left); healthy
2026-05-23T09:45 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~29min (last DONE 09:16:32); 60min idle-exit countdown (~31m left); healthy
2026-05-23T09:49 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | backfill+drain: order_param_sub_K_region_v1 DONE 09:47:06 (33.3s); substrate_N1048576_v1 DONE 09:47:15 (9.0s); betA_continual_edit_N65536_5seed_v1 FAIL 09:47:35 (19.8s, exit 1); now idle ~2min; healthy
2026-05-23T09:54 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | GPU idle ~7min (last FAIL 09:47:35); 60min idle-exit countdown (~53m left); healthy
2026-05-23T09:58 | GPU=running:wave14_pq_distributional_op_v1 | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | pq_distributional_op_v1 START 09:58:20 (wall ~26s); single-item backfill consumed; healthy
2026-05-23T10:02 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | pq_distributional_op_v1 DONE 09:59:34 (74.0s, exit 0); idle ~3min; 60min idle-exit (~57m left); healthy
2026-05-23T10:06 | GPU=running:wave14_endpoint_RM1m_projection_v1 | CPU=exited:None | pending_gpu=2 | pending_cpu=0 | endpoint_RM1m_projection_v1 START 10:05:55 (wall ~15s); pending=2 (pq_discrete_spikes_v1, betA_continual_edit_5seed_v2); active; healthy
2026-05-23T10:10 | GPU=running:wave14_pq_discrete_spikes_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | endpoint_RM1m_projection_v1 DONE 10:08:47 (171.8s, exit 0); pq_discrete_spikes_v1 START 10:08:47 (wall ~1m23s); pending=1; healthy
2026-05-23T10:14 | GPU=running:wave14_pq_discrete_spikes_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | pq_discrete_spikes_v1 (wall ~5m23s); pending stable; healthy
2026-05-23T10:19 | GPU=running:wave14_critical_slowing_down_self_monitor_v1 | CPU=exited:None | pending_gpu=4 | pending_cpu=0 | betA_continual_edit_5seed_v2 FAIL 10:19:24 (6.3s, exit 1); crooks_forensic_erase_audit_v1 DONE 10:19:29 (5.2s); critical_slowing_down_self_monitor_v1 START 10:19:29 (wall ~17s); pending=4 backfilled; healthy
2026-05-23T10:24 | GPU=idle:None | CPU=exited:None | pending_gpu=0 | pending_cpu=0 | queue drained: continuous_streaming_inference DONE 10:20:31 (15.9s), conformal_pq_confidence DONE 10:21:35 (64.1s), online_W_robbins_monro DONE 10:21:39 (4.0s); idle ~3min; healthy
2026-05-23T10:29 | GPU=running:wave14_pq_high_resolution_v1 | CPU=exited:None | pending_gpu=1 | pending_cpu=0 | endpoint_coset_census_v1 DONE 10:27:33 (173.0s, exit 0); pq_high_resolution_v1 START 10:27:33 (wall ~1m37s); pending=1; healthy