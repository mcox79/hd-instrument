# exp_dev -> queue: 3-CPU-drill batch (post-Glauber-INCONCLUSIVE, user CPU-bandwidth directive)

**Date filed**: 2026-05-23 ~18:55
**Trigger**: user directive "any experiments you want to run on cpus? you have a lot of bandwidth you're not using right now obviously" + GLAUBER_INCONCLUSIVE verdict refill from verdict_handler request file.

## Shipped (all to remote_cpu_queue)

```
queue=remote_cpu_queue name=wave14_glauber_kerdock_v2          script=experiments/exp_wave14_glauber_kerdock_v2.py          prereg=preregs/2026-05-23_wave14_glauber_kerdock_v2.md          timeout=3600
queue=remote_cpu_queue name=wave14_S_transform_kerdock_v1      script=experiments/exp_wave14_S_transform_kerdock_v1.py      prereg=preregs/2026-05-23_wave14_S_transform_kerdock_v1.md      timeout=1800
queue=remote_cpu_queue name=wave14_parisi_pq_kerdock_v1        script=experiments/exp_wave14_parisi_pq_kerdock_v1.py        prereg=preregs/2026-05-23_wave14_parisi_pq_kerdock_v1.md        timeout=5400
```

## 1-line hypotheses

- **glauber_kerdock_v2**: substrate Kerdock-Hopfield supports bimodal stationary P(q) at low T (beta>=4) for sub-critical alpha (<=0.10) -- the v1 INCONCLUSIVE was a parameter problem, v2 smoke at alpha=0.10 beta=6 already shows bimodal_score=1.000.
- **S_transform_kerdock_v1**: Voiculescu S-transform coefficients of the Kerdock spectrum deviate from MP closed form 1/(c+z); independent multiplicative free-prob axis beyond the additive free-cumulant probe (smoke shows 50-99% deviation).
- **parisi_pq_kerdock_v1**: replica overlap distribution P(q12) on Kerdock-Hebbian W shows non-trivial low-T shape (RSB-continuous, RS-two-delta, or paramagnet-single-delta); canonical Parisi spin-glass order parameter probe on substrate's actual codebook.

## Smoke results

| script | self-test | smoke verdict | smoke time |
|---|---|---|---|
| glauber_v2 | 4/4 PASS | GLAUBER_BIMODAL_KERDOCK | ~25s |
| S_transform_v1 | 5/5 PASS | S_TRANSFORM_DIVERGE | ~10s |
| parisi_v1 | 8/8 PASS | PARISI_INCONCLUSIVE (smoke-scale artifact) | ~20s |

All three queued via queue_add.sh; gate self-test passed on the remote runner; status_log entries written importance=HIGH.

## Routing-handler conflict note

verdict_handler had filed `notes/verdict_handler_request_to_exp_dev_glauber_rerun_2026-05-23.md` proposing a Glauber v2 rerun. As of dispatch time, routing_handler had NOT yet picked it up and the remote_cpu_queue was empty after the v1 INCONCLUSIVE. I shipped glauber_v2 directly per the user's "any experiments you want to run on cpus?" directive. If routing_handler subsequently acts, it should either:
  - See v2 already pending/running and skip
  - File a different drill instead (Option B from the request file)

## Queue depth + runtime span after dispatch

remote_cpu_queue depth: 3 pending (glauber_v2 may have already started given gate output sequence)
Expected total CPU-runtime span: ~50-100 min staggered (glauber_v2 ~30min + S_transform ~20min + parisi ~50min); GPU continues its independent ~hours-long free_cumulants_kerdock run during this.

## Pre-registered intent

If glauber_v2 + (free_cumulants OR S_transform) + parisi all fire substrate-novel verdicts (BIMODAL + DIVERGE + RSB respectively), this becomes the substrate's first multi-axis non-MP signature with three independent probe families (dynamical retrieval, additive free-prob, multiplicative free-prob, replica-overlap) on the same Kerdock 4-coset codebook. Strategy is the next consumer for the verdict ensemble.
