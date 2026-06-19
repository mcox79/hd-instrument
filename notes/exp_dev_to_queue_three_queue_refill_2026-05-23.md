# Exp Dev -> Queue: three-queue refill (post-CAP2_MARGIN_KILL + ONLINE_W_NARROW)

**Filed**: 2026-05-23
**Trigger**: orchestrator exp_dev sub-agent dispatch; all 3 runners alive; Research deliveries
  in hand (cap2 rehab + polyak-ruppert drill); pq_high_resolution 5-cycle overdue.

---

## Entry 1: local_cpu_queue (desktop CPU, cpu_runner_local)

```
queue=local_cpu_queue name=wave14_cap2_endpoint_id_confidence_v1 script=experiments/exp_wave14_cap2_endpoint_id_confidence_v1.py prereg=preregs/2026-05-23_wave14_cap2_endpoint_id_confidence_v1.md timeout=900
```

**Axis probed**: Cap 2 self-monitoring confidence — Rescue 1 (endpoint-ID + Mondrian/PLCP conformal)
**Research routing**: `research_cap2_self_monitoring_rehab_2026-05-23.md` Rescue 1; deflated P=0.35
**Self-test**: 6/6 PASS
**Smoke gate**: PASSED (structure valid; CAP2_ENDPOINT_UNCALIBRABLE expected at sub-capacity smoke;
  AUC signal degenerate when all retrievals correct at N=512 M=20 — FULL at N=4096 M=100 has errors)
**Peak memory**: 64 MB CPU (W=N x N float32 at N=4096)
**Expected wall time**: ~10 min CPU

Substrate-product impact: if PASS → Cap 2 returns to portfolio as "per-query confidence via
  endpoint-id-conditioned conformal (PLCP-anchored, substrate-novel 28-element basin partition)".
  If KILL → escalate to Rescue 2 (VAMP variance, GPU).

---

## Entry 2: remote_cpu_queue (marsh@home CPU, cpu_runner_0 REVIVED ~13:37)

```
queue=remote_cpu_queue name=wave14_online_W_polyak_noise_corrected_v1 script=experiments/exp_wave14_online_W_polyak_noise_corrected_v1.py prereg=preregs/2026-05-23_wave14_online_W_polyak_noise_corrected_v1.md timeout=300
```

**Axis probed**: Cap 5 Online W noise envelope — Polyak-Ruppert noise-corrected retention bound
**Research routing**: `research_online_W_noise_robust_2026-05-23.md` Mechanism #1; deflated P=0.50
**Self-test**: 4/4 PASS (H2 + verdict)
**Smoke gate**: PASSED (ONLINE_W_POLYAK_PASS on smoke fallback data; FULL verdict after dependency)
**Peak memory**: <1 MB (pure Python arithmetic over metrics.json)
**Expected wall time**: <5 min CPU

DEPENDENCY: requires `wave14_online_W_noise_envelope_v1` FULL data at
  `data/exp_wave14_online_W_noise_envelope_v1/metrics.json` on marsh@home.
  Note to queue_health: add this entry to remote_cpu_queue/queue.json on
  marsh@home ONLY after the overnight_queue FULL run confirms.

Substrate-product impact: if PASS → Cap 5 envelope widens from "p<=0.30" to tiered SLA
  "min_acc >= 0.95 - C*H2(p)"; same product story as v158 Cap 1 Sagawa-Ueda.
  If FAIL → escalate to Mechanism #1b (Polyak-averaged iterate swap, ~50 LOC + FULL re-run).

---

## Entry 3: overnight_queue (marsh@home GPU, gpu_runner_0)

```
queue=overnight_queue name=wave14_pq_high_resolution_v1 script=experiments/exp_wave14_pq_high_resolution_v1.py prereg=preregs/2026-05-23_wave14_pq_high_resolution_v1.md timeout=2400
```

**Axis probed**: substrate-physics P(q) hierarchical structure — 28-element endpoint partition
  cardinality verification (strategy_request_to_exp_dev_post_v158_pipeline_2026-05-23.md Pick 2)
**Research basis**: 5-cycle-overdue pipeline pick; already built + smoke-passed (PQ_HIERARCHICAL_28
  at N=2048 smoke); FULL at N=16384 200-seed 500-bin; builds on cycle 172 15-peak finding
**Self-test**: 4/4 PASS (already verified at initial build; utf-8 reconfigure already patched)
**Smoke gate**: PASSED (PQ_HIERARCHICAL_28 31 peaks at N=2048 smoke)
**Peak memory**: ~1.1 GB VRAM (N=16384 float32 W + VAMP chain)
**Expected wall time**: ~20 min GPU

Substrate-product impact: if PQ_HIERARCHICAL_28 → confirms 28-element endpoint partition
  structure (anchors Rescue 1 PLCP conformal claim; substrate-physics characterization).
  overnight_queue.json updated with this entry (depth = 3 pending).

---

## Queue depth summary (after this refill)

| Queue | Pending depth | New entries |
|---|---|---|
| overnight_queue | 3 | wave14_pq_high_resolution_v1 (added to queue.json) |
| local_cpu_queue | 2 | wave14_cap2_endpoint_id_confidence_v1 (added to queue.json) |
| remote_cpu_queue | 1 | wave14_online_W_polyak_noise_corrected_v1 (note filed; queue_health applies to remote) |

Pipeline invariant satisfied: all 3 runners have >= 1 pending item.
