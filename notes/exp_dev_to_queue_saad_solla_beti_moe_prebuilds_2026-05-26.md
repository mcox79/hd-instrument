# exp_dev to queue: 5-corpus extension + Bet I 3rd envelope + MoE SHIFT K-scaling pre-build

**Filed**: 2026-05-26 by exp_dev
**Status**: READY FOR DISPATCH (two immediate ships + one gated pre-build)

---

## SMOKE RESULTS

**wave14_betB_5corpus_equalspacing_v1**: PASS
- All 5 selftests pass
- Runs in < 2s (pure re-analysis of existing data)
- Verdict: MIDDLE_BAND (BIC_delta=-8.64, borderline; spacing_error=0.0284 PASSES < 0.05)
- Interesting finding: spacing_error passes but BIC misses -10 threshold by 1.36 BIC units
- Calls for full-scale GPU 5-corpus experiment for clean BIC test

**wave14_beti_depth_polylog_v1**: PASS
- All 5 selftests pass; multi-scale smoke PASS
- Smoke is MIDDLE_BAND as expected (d_sweep too small to find cliff at smoke N)
- Full run needs N={256..4096}, d_sweep up to 40+

**wave14_moe_shift_K_scaling_v1**: PASS (pre-build gated on v2 SHIFT verdict)
- All 5 selftests pass; multi-scale smoke PASS
- Smoke MIDDLE_BAND expected (N=512 sub-threshold for K-scaling; full test at N=4096)

---

## IMMEDIATE SHIPS (LOCAL CPU)

**wave14_betB_5corpus_equalspacing_v1** ships immediately (pure re-analysis, < 30s):

```
queue=local_cpu_queue name=wave14_betB_5corpus_equalspacing_v1 script=experiments/exp_wave14_betB_5corpus_equalspacing_v1.py prereg=prereqs/2026-05-26_wave14_betB_5corpus_equalspacing_v1.md timeout=120
```

---

## GPU SHIPS (overnight_queue)

**wave14_beti_depth_polylog_v1** ships to overnight_queue (N-sweep, 5 seeds per cell):

```
queue=overnight_queue name=wave14_beti_depth_polylog_v1 script=experiments/exp_wave14_beti_depth_polylog_v1.py prereg=prereqs/2026-05-26_wave14_beti_depth_polylog_v1.md timeout=7200
```

---

## GATED PRE-BUILD (ship only on SHIFT verdict)

**wave14_moe_shift_K_scaling_v1** is a conditional pre-build: ship ONLY when
`wave14_moe_shift_partition_v2` returns verdict containing "SHIFT" (Arm A exceeds Arm C > 0.15).

Schema A entry (for orchestrator use on SHIFT verdict):

```
queue=overnight_queue name=wave14_moe_shift_K_scaling_v1 script=experiments/exp_wave14_moe_shift_K_scaling_v1.py prereg=prereqs/2026-05-26_wave14_moe_shift_K_scaling_v1.md timeout=28800
```

If PARTITION verdict: this script is NOT relevant; archive.

---

## WHAT WAS BUILT

1. `experiments/exp_wave14_betB_5corpus_equalspacing_v1.py` — 5-corpus Saad-Solla extension
   (NO_REPLAY_SAME_CORPUS as 5th plateau; n=5 boundary of statistical power; MIDDLE_BAND result
   at re-analysis scale; spacing_error=0.0284 PASSES; recommends full-scale GPU experiment)

2. `experiments/exp_wave14_beti_depth_polylog_v1.py` — Bet I 3rd envelope probe
   (d_c = sqrt(N * log(N) / K) polylog correction across N-sweep; R16 free probability)

3. `experiments/exp_wave14_moe_shift_K_scaling_v1.py` — MoE SHIFT K-scaling pre-build
   (K sweep {2,4,8,16,32} at N=4096; ships immediately on SHIFT verdict)

4. PROT-013 appended to active_protocols.md (evaluate_bpc signature self-test mandate)

---

## SCHEMA A ENTRIES

```
queue=local_cpu_queue name=wave14_betB_5corpus_equalspacing_v1 script=experiments/exp_wave14_betB_5corpus_equalspacing_v1.py prereg=prereqs/2026-05-26_wave14_betB_5corpus_equalspacing_v1.md timeout=120
queue=overnight_queue name=wave14_beti_depth_polylog_v1 script=experiments/exp_wave14_beti_depth_polylog_v1.py prereg=prereqs/2026-05-26_wave14_beti_depth_polylog_v1.md timeout=7200
```
