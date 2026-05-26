# Exp Dev -> Queue: three-runner refill (post-PQ_OTHER_CARDINALITY + dual-KILL + POLYAK_PARTIAL)

**Filed**: 2026-05-23
**Trigger**: orchestrator exp_dev sub-agent dispatch; all 3 queues drained after overnight batch:
  - overnight_queue: 0 pending (completed betA_5seed_v3 + cap2_margin_probe + pq_high_resolution)
  - remote_cpu_queue: 0 pending (completed online_W_polyak_noise_corrected_v1 = POLYAK_PARTIAL)
  - local_cpu_queue: 0 pending (completed betT_tempscale = KILL + cap2_endpoint = KILL)
**Recent verdicts prompting this refill**:
  - PQ_OTHER_CARDINALITY (pq_high_resolution FULL): 7 outer x ~8.5 sub-peaks = ~60 total peaks
  - ONLINE_W_POLYAK_PARTIAL: 4/5 cells pass corrected bound; 0/1 originally-failing rescued
  - BET_T_TEMPSCALE_KILL: best_min_acc=0.344 < 0.70; TEMPSCALE rescue refuted
  - CAP2_ENDPOINT_KILL: AUC=0.50 in 4/4 strata; Rescue 1 refuted

---

## Entry 1: overnight_queue (GPU; N=65536)

```
queue=overnight_queue name=wave14_demo1_noise_envelope_v1 script=experiments/exp_wave14_demo1_noise_envelope_v1.py prereg=preregs/2026-05-23_wave14_demo1_noise_envelope_v1.md timeout=3600
```

**Axis probed**: Cap 1 (Demo 1 Lane D capstone) noise envelope expansion — "4-primitive composition under noise"
**Motivation**: Cap 1 is ✅ FULL at clean (composed_acc=1.000, cycles 130+139). Active-priorities next-envelope axis. Overnight_queue drained; substrate-product pipeline invariant violated. This is the highest-leverage GPU experiment available: expands a ✅ capability's commercial envelope.
**Self-test**: 5/5 PASS (verdict logic 5 cases)
**Smoke gate**: PASSED at N=8192 (DEMO1_NOISE_ROBUST composed=1.000 at both p=0.0 and p=0.10; clean signal expected at small N)
**Peak VRAM**: ~260 MB (5 codebooks × 65536 float32; well under 8 GB)
**Expected wall time**: ~30-60 min GPU at N=65536, 3 seeds, 5 noise levels × 40 trials
**FULL config**: N=65536, seeds=[17,23,31], noise_levels=[0.0,0.05,0.10,0.20,0.30], 40 trials/cell
**queue.json**: updated (D:/AI/hd-instrument/data/overnight_queue/queue.json; 1 new pending entry)

Substrate-product impact: if ROBUST → Cap 1 envelope widens to "tolerates up to 10% observation bit-flip";
commercial positioning: "robust to realistic sensor noise". If BRITTLE → envelope stays at clean; product note
"requires clean input at deployment". Either outcome is valuable characterization.

---

## Entry 2: remote_cpu_queue (marsh@home CPU; pure CPU; ~10 min)

```
queue=remote_cpu_queue name=wave14_betT_conformal_v1 script=experiments/exp_wave14_betT_conformal_v1.py prereg=preregs/2026-05-23_wave14_betT_conformal_v1.md timeout=900
```

**Axis probed**: Bet T (parallel hypothesis tracking, 🟡 PARTIAL min_acc=0.689 56 versions stale) — Rescue #3 class-wise Mondrian conformal wrapper (P_deflated=0.40)
**Motivation**: BET_T_TEMPSCALE_KILL just landed (Rescue #1 refuted). Research ranked Rescue #3 (conformal) as #2 fallback. P_deflated=0.40 makes this the next-best investment. Pure CPU, ~10 min — exactly the right profile for remote_cpu_queue.
**Self-test**: 5/5 PASS (verdict logic 5 cases)
**Smoke gate**: PASSED at N=512 K=3 (BET_T_CONFORMAL_KILL due to over-coverage=1.0 at tiny scale; structural valid — metrics.json produced, K_hyp entries correct, set_size > 0; over-coverage at N=512 is expected small-N artifact; FULL at N=4096 K=8 will show real coverage distribution)
**Peak memory**: ~20 MB CPU
**Expected wall time**: ~10 min CPU
**No remote data dependency**: all data generated fresh. Can run immediately.
**queue.json on remote machine**: queue_health must add this entry after reading this note.

Note for queue_health: remote_cpu_queue runner is at marsh@home. Add this entry to remote machine's queue.json at data/remote_cpu_queue/queue.json.

---

## Entry 3: local_cpu_queue (desktop CPU; pure CPU; <5 min)

```
queue=local_cpu_queue name=wave14_pq_subpeak_characterization_v1 script=experiments/exp_wave14_pq_subpeak_characterization_v1.py prereg=preregs/2026-05-23_wave14_pq_subpeak_characterization_v1.md timeout=360
```

**Axis probed**: Substrate-physics — P(q) outer-peak spacing structure after PQ_OTHER_CARDINALITY
**Motivation**: PQ_OTHER_CARDINALITY (7 outer × ~8.5 sub-peaks = ~60 total) is a new substrate-physics finding. The multi-scale structure needs classification: arithmetic spacing (uniform RSB) vs geometric/non-uniform spacing (Parisi RSB cascade or heterogeneous multi-scale). This CPU re-analysis does an N-sweep {512,1024,2048,4096} computing inter-peak gap CV to classify the spacing geometry. <5 min CPU. No dependencies.
**Self-test**: 4/4 PASS (verdict logic)
**Smoke gate**: PASSED at N=1024 20 seeds (PQ_SUBPEAK_GEOMETRIC CV=0.370 > 0.30; 11 outer peaks; metrics.json valid)
**Peak memory**: ~50 MB CPU (N=4096 codebooks)
**Expected wall time**: ~3-5 min CPU
**queue.json**: updated (D:/AI/hd-instrument/data/local_cpu_queue/queue.json; 1 new pending entry)

---

## Pipeline depth after filing

- overnight_queue: 1 pending (wave14_demo1_noise_envelope_v1)
- remote_cpu_queue: 1 pending (wave14_betT_conformal_v1; queue_health must apply to remote)
- local_cpu_queue: 1 pending (wave14_pq_subpeak_characterization_v1)

Pipeline invariant SATISFIED: runner-never-idle across all 3 queues.
