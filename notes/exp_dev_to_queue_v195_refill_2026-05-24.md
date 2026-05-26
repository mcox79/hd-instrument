# exp_dev -> queue: v195 emergency refill (4 anchors shipped)

**Filed**: 2026-05-24 by exp_dev
**Trigger**: v195 6-verdict batch closed; all queues at 0; pipeline-pacing reflex.

## Ships (Schema A)

```
queue=overnight_queue name=wave14_k2_m1_hierreplay_v1 script=experiments/exp_wave14_k2_m1_hierreplay_v1.py prereg=preregs/2026-05-24_wave14_k2_m1_hierreplay_v1.md timeout=21600
queue=remote_cpu_queue name=wave14_betm_logforget_longt_v1 script=experiments/exp_wave14_betM_logforget_longt_v1.py prereg=preregs/2026-05-24_wave14_betM_logforget_longt_v1.md timeout=3600
queue=remote_cpu_queue name=wave14_rprime3_r2_subcorpus_v1 script=experiments/exp_wave14_rprime3_r2_subcorpus_v1.py prereg=preregs/2026-05-24_wave14_rprime3_r2_subcorpus_v1.md timeout=1800
queue=local_cpu_queue name=wave14_f6_kkl_envelope_v1 script=experiments/exp_wave14_f6_kkl_envelope_v1.py prereg=preregs/2026-05-24_wave14_f6_kkl_envelope_v1.md timeout=300
```

## Smoke outcomes (before ship)

- wave14_k2_m1_hierreplay_v1: HARD_PASS (retA=0.888 vs baseline 0.74; +0.148)
- wave14_betm_logforget_longt_v1: MIDDLE_BAND (C_sqrt gap=4.86 at 4 t-points; inconclusive short-grid)
- wave14_rprime3_r2_subcorpus_v1: MIDDLE_BAND (r=0.187 at N=512; full run resolves at N=2048 + 5 seeds)
- wave14_f6_kkl_envelope_v1: HARD_PASS at smoke (4 cells); FULL completed in 13.8s -> MIDDLE_BAND (11/12 pass)

## Blocked (smoke HARD_FAIL -> upstream push)

- wave14_k6_axis3_cleanup_iter_v1: HARD_FAIL (cleanup loop diverges; acc=0.031 at T=0, drops to 0 by T=2)
  -> notes/exp_dev_to_strategy_k6_axis3_smoke_fail_2026-05-24.md
- wave14_rprime1_pac_bayes_v2: HARD_FAIL (KL = N^2/2 per task structurally; bound always vacuous)
  -> notes/exp_dev_to_strategy_rprime1_pac_bayes_reframe_2026-05-24.md

## REMOTE VERIFY

All 4 ships verified present in remote queue.json at ship time.
- wave14_k2_m1_hierreplay_v1: RUNNING on GPU (picked up immediately)
- wave14_betm_logforget_longt_v1: COMPLETED on remote CPU
- wave14_rprime3_r2_subcorpus_v1: RUNNING on remote CPU
- wave14_f6_kkl_envelope_v1: COMPLETED on local CPU (13.8s; MIDDLE_BAND 11/12)
