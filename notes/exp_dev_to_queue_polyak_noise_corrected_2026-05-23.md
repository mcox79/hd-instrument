# Exp Dev -> Queue: Polyak-Ruppert noise-corrected bound re-analysis (Cap 5)

**Filed**: 2026-05-23
**Routing trigger**: post-ONLINE_W_NOISE_ENVELOPE_NARROW v159 Research 2x drill; Research Mechanism #1 recommendation
**Research source**: `notes/research_online_W_noise_robust_2026-05-23.md` Mechanism #1 (P_deflated=0.50)

---

## Entry 1 (remote CPU — dependency on overnight_queue FULL data)

```
queue=remote_cpu_queue name=wave14_online_W_polyak_noise_corrected_v1 script=experiments/exp_wave14_online_W_polyak_noise_corrected_v1.py prereg=preregs/2026-05-23_wave14_online_W_polyak_noise_corrected_v1.md timeout=300
```

**Smoke gate**: PASSED. Self-test 4/4 PASS (H2 + verdict 4 cases). Smoke at N=1024:
- Source: smoke fallback data (FULL data on remote runner)
- Fitted C = 0.0000 (smoke data has min_acc=1.0 at all cells; C=0 natural)
- VERDICT: ONLINE_W_POLYAK_PASS (on smoke data; FULL verdict definitive)
- metrics.json: data/exp_wave14_online_W_polyak_noise_corrected_v1_smoke/metrics.json
- Elapsed: <1s

**FULL config**: reads `data/exp_wave14_online_W_noise_envelope_v1/metrics.json` on remote machine
**Memory budget**: pure Python arithmetic, <1 MB, <5 min CPU.
**Queue rationale**: Pure CPU, <15 min, BUT source data is on the remote machine
  (wave14_online_W_noise_envelope_v1 FULL run data lives on overnight_queue runner =
  marsh@home). Per routing Rule 4 fallback: remote_cpu_queue (which runs on marsh@home)
  has access to the overnight_queue runner's data directory.

**DEPENDENCY**: This experiment must run AFTER wave14_online_W_noise_envelope_v1 FULL
  completes. If the FULL data is not yet on disk when this job runs, the script
  falls back to smoke data with a warning and logs ONLINE_W_POLYAK_PASS on smoke data
  (non-definitive). Schedule re-run after FULL data confirms.

**Note for queue_health**: add this entry to the remote_cpu_queue queue.json on
  marsh@home after wave14_online_W_noise_envelope_v1 FULL has been confirmed completed.
  Local desktop cannot write remote_cpu_queue/queue.json directly.

---

## Substrate-product axis

Cap 5 (Gap B Online W + Robbins-Monro+SNAP) noise envelope characterization.
The v159 ONLINE_W_NOISE_ENVELOPE_NARROW verdict characterized the envelope as
p_flip <= 0.30. This re-analysis tests whether the p=0.40 FAIL is a metric-definition
artifact (flat threshold does not account for inherent noise floor in stochastic
approximation) or a structural substrate failure.

If ONLINE_W_POLYAK_PASS: Cap 5 commercial wedge widens from "p<=0.30" to a tiered SLA
"min_acc >= theta_ret(p) = 0.95 - C*H2(p) at any p". Same pattern as v158 Cap 1.

---

## Coordination notes

- 3-queue refill: local_cpu_queue gets wave14_cap2_endpoint_id_confidence_v1 (Cap 2 Rescue 1)
- overnight_queue gets wave14_pq_high_resolution_v1 FULL (5-cycle overdue pipeline pick)
- remote_cpu_queue gets this entry (dependency-gated but short)
- Pipeline depth after: local=2 pending, overnight=3 pending, remote_cpu=1 pending
