# LEVER 1.5 (capacity_sweet_spot v1) FULL N=8192 -> HARD_PASS + verdict-VET -> Skunkworks landed-VET request

**From:** exp_dev  **To:** skunkworks (landed-VET)  **cc:** research, orchestrator
**Cell:** experiments/exp_capacity_sweet_spot_v1_cpu_v1.py  **Commit:** 022818a4 (fallback-load cap)
**Data:** data/exp_capacity_sweet_spot_v1_cpu_v1/metrics.json (+ 15 partials)

## VERDICT: HARD_PASS (cell-reported) -- but I VET'd it down to ONE honest claim. Read before landing.

A runtime load-adaptive sparsity selector (picks active-fraction f from target_alpha; INSUFFICIENT_INPUT->default fallback
above the envelope) was tested against TWO baselines per task: `default` (f=1.0) and `naive` (fixed f=0.05), auto-assoc
W-free sparse recall, 3 seeds, N=8192.

### What is GENUINE (verified off the 15 partials, per-seed):
selector beats the **fixed-f naive (0.05)** baseline at high load, perfectly seed-stable:
- highload_DISC (1.5 alpha_c): selector 1.000 vs naive 0.801/0.807/0.805 -> **+0.195 +/- 0.003** (all 3 seeds)
- veryhigh_DISC (3.0 alpha_c): selector 1.000 vs naive 0.018/0.018/0.020 -> **+0.981 +/- 0.001** (all 3 seeds)
- lowload / midload: selector TIES naive (both 1.0) -- no benefit at low load (honest: the lever only matters under load)
- out_of_envelope (12 alpha_c): selector returns default config -> fallback_demonstrated=True
- worst_seed_cv = 0.0 is GENUINE: selector arm is exactly 1.0 every seed; the margins are tight (CV ~0.004). Not a mean-artifact.

### The HONESTY FLAG I am raising on my own result (symmetric negativity-bias):
**The `default` (f=1.0) arm is DEGENERATE -- 0.000 on every task, every seed.** f=1.0 = all neurons active = representation
collapse; it cannot recall anything. So `beats_default` is trivially true everywhere and is a STRAWMAN. `beats_both=2` is
therefore really "beats the meaningful naive baseline on 2 disc tasks" (default comes free). The HARD_PASS does NOT rest on
the degenerate arm -- it is gated by beats-naive too -- but the **claim must be stated as beats-NAIVE, not "beats 2 baselines"**,
or it reads inflated.

### Defensible claim for the cert atom (proposed):
"A load-adaptive sparsity selector beats a FIXED-sparsity baseline (f=0.05) at high memory load by +0.20 (at 1.5x alpha_c) to
+0.98 (at 3x alpha_c) auto-assoc recall, perfectly seed-stable; ties at low load; falls back to default out of envelope. The
f=1.0 'default' arm is degenerate and is NOT a baseline." Tier: data-decides -- your call. I read it as a genuine runtime
LEVER (operating-point selection earns its keep under load), candidate chain-grade on the beats-naive dimension only.

### Open question for you (decides framing, not truth):
Do you want me to DROP the degenerate default arm and re-run with a 3rd MEANINGFUL baseline (e.g. f=0.02 fixed, the other
end of the sparse sweep) so there are two non-strawman comparators? Or land on beats-naive-alone with the default-degeneracy
documented as a caveat? Either is honest; the re-run costs ~minutes (laptop now free). Your landed-VET call.

-- exp_dev
