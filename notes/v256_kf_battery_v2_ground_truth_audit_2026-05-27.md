# v256 KF-Battery Ground-Truth Audit (2026-05-27)

## Trigger

Orchestrator flagged v254/v255/v256 cap_map lifts (portfolio 14+19 -> 14+23,
3 NEW evidence-strength rows, 5 framework-reliability lifts) as possibly
resting on infrastructure-failed runs because event-bus wall-times for the
v2-batch were 5-90s and bet_b_4stage_n16384_v1 took only 232s.

## Methodology

For each of 10 anchors:
1. SCP'd runner log from `marsh@home:C:/dev/hd-instrument/data/overnight_queue/<anchor>.log`.
2. SCP'd `C:/dev/hd-instrument/data/exp_<anchor>/metrics.json` where present.
3. Cross-checked against `data/overnight_queue/queue.json` per-entry
   `status / wall_s / started_at / completed_at / exit_code`.

Artifacts cached at `data/_audit_v256/`.

## Wall-time mystery RESOLVED

The 6300s "wall_s" values in the trigger message are
`completed_at - shipped_at` from event-bus -- they include queue-wait time
where the runner was busy on earlier jobs. The queue.json's own `wall_s`
field shows true script-execution time which matches the log "elapsed" lines:

| anchor              | queue.wall_s | log.elapsed_s | queue.status   | exit |
|---------------------|--------------|---------------|----------------|------|
| kf5_steerable_beta_v1 |   2.16 |  (crashed)  | failed     | 1 |
| kf5_steerable_beta_v2 |  12.41 |   9.98 s    | completed  | 1* |
| axis1_mb_chunk1_v1    |  13.78 |  11.18 s    | completed  | - |
| axis1_mb_chunk2_v1    |  81.69 |  79.01 s    | completed  | - |
| kf1_hallu_impossibility_v1 |  5.75 |   3.24 s | completed | - |
| kf1_hallu_impossibility_v2 |  7.63 |   5.33 s | completed | - |
| kf3_multisub_isolation_v1  |  3.93 |   1.66 s | completed | - |
| kf4_drift_detect_v1   |   4.45 |   2.08 s    | completed  | - |
| kf4_drift_detect_v2   |   5.72 |   3.21 s    | completed  | - |
| bet_b_4stage_n16384_v1 | 198.19 |  (OOM)    | failed     | 1 |

*kf5_v2 queue.exit_code=1 is the SECOND infrastructure-tag-vs-honest-metrics
mismatch v256 already documented -- metrics.json is HARD_PASS so v256
verdict_handler did the right re-read.

The "expected ~12h half-GPU-day" budgets in the trigger message DO NOT match
the scripts: each script header documents itself as inference-only or
short-training (kf5_v1 header explicitly says "~30s smoke / 2100s budget";
KF1/3/4 are inference-only OOS / coupling / drift probes; axis1 chunk1+2 are
retention-grid sweeps not training sweeps). Tier-1 ~hours/days framing was
caller-side and aspirational, not script-honest.

## Per-anchor ground truth

### Group A: REAL + HP/MB defensible (5 anchors)

1. **kf5_steerable_beta_v2  KF5_HARD_PASS REAL.**
   N=4096 5 seeds [7,17,23,31,41] x 7 betas; entropy collapse seed-7
   [7.71,6.35,3.06,1.25,0.54,0.25,0.12] range=7.59 bits = 7.6x the 1.0 bit
   HP threshold; all 5 seeds reproduce within 0.02 = deterministic phase
   signature. Honest under-claim (bpc_monotone=0/5 explicit). REAL.

2. **axis1_mb_chunk2_v1     AXIS1C2_HARD_PASS REAL.**
   140 cells M in {16384,32768,65536,131072} x 7 betas x 5 seeds; mean
   retention by M = [1.000, 0.503, 0.238, 0.117] = clean retention phase
   boundary at M*/N=8 (M=32768 N=4096). BNV monotone-increasing 1.4->16.
   REAL phase-boundary discovery.

3. **kf1_hallu_impossibility_v2  KF1_MIDDLE_BAND REAL.**
   5 seeds x 5 M_fracs; under-cap mean_oos_max_conf=0.000171-0.000172 (1e-4
   deterministic); over-cap saturates to 1.0 as expected. Verdict honestly
   notes "tight 5-seed gate / weaker than Tier-1 spec". REAL envelope-ext.

4. **kf4_drift_detect_v2   KF4_HARD_PASS REAL.**
   5 seeds x 50 edits N=4096 M=4096; r_drift=0.989+/-0.0007 5/5 >= 0.9;
   r_bnv=0.994+/-0.0006 5/5 >= 0.9; drift_final=0.1826+/-0.0002 deterministic.
   REAL 5-seed envelope-extension of v1 (3-seed).

5. **kf3_multisub_isolation_v1  KF3_MIDDLE_BAND REAL.**
   3 seeds x 7 coupling values; leakage_0 in [1.8e-3, 5.4e-3] HP-strength;
   contam_0 in [0.048, 0.062] = 5% baseline at coupling=0 (state-mix is
   shared-substrate baseline not coupling-induced); honest dual-framing.

### Group B: REAL but SCRIPT-VERDICT-BUG (1 anchor)

6. **axis1_mb_chunk1_v1   AXIS1_HARD_PASS  CRITERION-CONTRADICTING.**
   Ran cleanly: 5 seeds x M in {1024,2048,4096,8192} x 7 betas; ALL cells
   retention=1.0 (saturated; M_max=2N is under-capacity per axis1 phase
   diagram). BNV-range=0.9486 (modest signature). `ret_M_range=0.000` --
   FAILS its own pre-registered criterion `ret_M_range >= 0.2` -- yet
   prints `AXIS1_HARD_PASS / Phase structure detected`. Script verdict
   logic has a true bug (the verdict block fires HARD_PASS unconditionally
   when BNV-range is nonzero, even when retention-range criterion fails).
   v254 caught this as 93rd label-vs-honest catch already; v256 chunk2
   correctly does NOT credit chunk1's HP. Net cap_map impact: NEGATIVE for
   chunk1 alone but axis1 row 🟢 60-72% in v256 rests on CHUNK2's clean
   transition, not chunk1. **OK.**

### Group C: FAILED honestly (2 anchors)

7. **kf5_steerable_beta_v1  SCRIPT-CRASH.**
   Crashed at seed 7 first line:
   `RuntimeError: Expected 'cpu' device type for generator but found 'cuda'`
   in `pa.make_bsc_atoms` -- script passes a cuda-device generator to a
   torch.rand call that requires cpu generator. queue.status=failed exit=1.
   exp_<v1> dir is EMPTY (no metrics.json). v254 correctly classified as
   `KF5_INFRASTRUCTURE_FAIL_NO_FULL_DATA`; v2 was the fix. **OK.**

8. **bet_b_4stage_n16384_v1   CUDA OOM.**
   Crashed at seed 7 train_w_with_replay:
   `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 1024MiB.
    GPU 0 has 8GB total capacity, 6.80 GiB allowed, 5.19 GiB allocated.`
   queue.status=failed exit=1. exp_<v1> dir is EMPTY. NOT addressed in
   v256 verdict batch (was only 4 verdicts: kf5_v2 / axis1_chunk2 /
   kf1_v2 / kf4_v2); bet_b N=16384 needs separate handling. **No cap_map
   contamination -- never landed in batch.**

### Group D: PRE-v256 SUPPORTING (2 anchors)

9. **kf1_hallu_impossibility_v1  REAL** -- already credited in v254 row
   addition; v256 just lifts via v2 5-seed.

10. **kf4_drift_detect_v1  REAL** -- same pattern.

## Verdict on v256 cap_map lifts

| lift                                          | defensible? |
|-----------------------------------------------|-------------|
| KF-5 NEW row 🟢 60-72%                        | YES (real 5-seed FULL N=4096 inference sweep) |
| KF-1 row 🟢 60-70% -> 62-72% (+2)             | YES (5-seed envelope ext landed clean)        |
| KF-4 row 🟢 55-70% -> 65-78% (+10)            | YES (5-seed HP3-strength deterministic)       |
| axis1 row 🟡 -> 🟢 60-72%                     | YES (chunk2 found real boundary; chunk1 not credited) |
| phase-boundary direct-test 🟢 55-70% -> 60-75% (+5) | YES (built on KF1/KF4/KF5/axis1c2 stack) |
| product-feature framework-reliability +5 -> 73-85% | YES (built on above)                     |
| portfolio 14+22 -> 14+23                      | YES (KF-5 NEW row is genuine)                 |

**RECOMMENDATION: CONFIRM v256.  No revert needed.**

## Caveats to surface

1. **kf5_v1 (v254 batch member) was correctly diagnosed as INFRASTRUCTURE_FAIL** in v254
   -- the 30min queue-wait gap mistakenly attributed to "ran for 1.75h" in the
   trigger message was orchestrator-side mis-reading of event-bus timestamps,
   not a v254 verdict_handler failure. The v254 strategy_handler call did
   the right thing.

2. **axis1_chunk1 verdict-logic bug is REAL** -- the script will keep
   firing AXIS1_HARD_PASS on any chunk where BNV-range>0 even if
   ret_M_range fails. v254 caught it as 93rd label-vs-honest. Should
   fix script-side OR enforce via per-script verdict self-consistency
   gate (v254 rescue-sketch (c) already proposed this; not done yet).

3. **bet_b_4stage_n16384_v1 CUDA OOM** -- 8GB GPU cannot do N=16384
   4-stage with current batch size. Options: (a) batch=128 retry on
   same GPU (queue file already shows `bet_b_4stage_batch128_v1` ran
   successfully earlier in the day so framework exists); (b) ship to
   24GB workstation if available; (c) drop to N=12288 intermediate.
   This is NOT a v256 issue (not in v256 batch).

4. **5th N-enforcement leak (PROT-020 candidate)** -- v256 entry
   itself flagged this: anchors without `_n<N>` suffix bypass
   queue_add.py exit-6. In this batch no concrete harm (per-cell
   metrics confirm N=4096 5-seed for all real anchors) but systemic
   risk is real. Recommendation already on record.

5. **Wall-time interpretation discipline** -- orchestrator/Strategy
   should compute wall from queue.json `wall_s` not event-bus
   `completed_at - shipped_at`. The latter includes queue-wait and
   is misleading for short-running scripts. Worth a brief in
   `notes/active_protocols.md`.

## Files

- Logs:     data/_audit_v256/<anchor>.log
- Metrics:  data/_audit_v256/<anchor>_metrics.json
- queue.json snapshot: data/_audit_v256/queue.json

Auditor: research sub-agent
Date: 2026-05-27
