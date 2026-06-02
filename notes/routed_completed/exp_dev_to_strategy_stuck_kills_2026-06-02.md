# Stuck-Kill Diagnostic Routing Note -- 2026-06-02

Filed by: exp_dev
Date: 2026-06-02T14:39Z
Action: Both stuck anchors had no running process at kill time (processes had already died or
  were never spawned under the expected name). Queue entries were stuck in status=running with
  pid=None. Both marked failed manually.

---

## Anchor 1: q_f4_saddle_overlap_correlated_v1

Queue: remote_cpu_queue
Started: 2026-06-02T08:44:15
Killed at: 2026-06-02T14:39:48 (approx 5h55m elapsed -- far beyond 10-30 min expected)
Process found at kill time: None (already dead)
Error filed: stuck_killed_over_1.7h_no_progress_process_not_found

### Likely failure mode

Saddle-overlap / gradient-ascent algorithms are prone to infinite convergence loops when:
- The saddle condition (F_4 exponent regime) is not within the basin of convergence of the
  numerical solver.
- No explicit max_iter or convergence tolerance guard was set.
- Floating-point cycle: gradient steps oscillate around the saddle without contracting.

### Recommended re-design

Before re-shipping q_f4 successor:
1. Add explicit max_iter guard (e.g. max_iter=500) to all gradient / ascent loops.
2. Add convergence tolerance: if |delta| < 1e-8 for 10 consecutive steps, declare converged.
3. Add per-cell timeout using signal.alarm (Unix) or threading.Timer watchdog (Windows).
4. Add _instrumentation_selftest() assertion that at least one cell exits via convergence
   rather than max_iter at smoke scale N=256.
5. Run smoke at N=256 and verify wall < 60s before queuing FULL.

---

## Anchor 2: q_c2_mp_hc_v2_corrected_n4096

Queue: overnight_queue (GPU)
Started: 2026-06-02T08:48:11
Killed at: 2026-06-02T14:39:48 (approx 5h51m elapsed -- far beyond 30-60 min expected)
Process found at kill time: None (already dead)
Error filed: stuck_killed_over_1.7h_no_progress_process_not_found

### Likely failure mode

MP-HC (Marchenko-Pastur hard-core) spectral-edge computation at N=4096 can stall when:
- scipy.linalg.eigvalsh (or np.linalg.eigvalsh) hangs inside LAPACK dstevd/dsyevd on certain
  nearly-singular or ill-conditioned matrices.
- No eigenvalue solver timeout is set; the LAPACK call blocks the GIL indefinitely.
- The "corrected" v2 variant introduced a conditioning fix that accidentally creates a
  near-zero eigenvalue cluster, causing LAPACK bisection to take O(N^3) fallback path.

### Recommended re-design

Before re-shipping q_c2 successor:
1. Wrap eigvalsh call with a threading.Timer watchdog: if eigvalsh takes > 30s for a single
   cell, kill the thread and record cell as NaN.
2. Add condition-number pre-check: if cond(M) > 1e12, skip eigvalsh and record cell as
   ILL_CONDITIONED.
3. Add _instrumentation_selftest() assertion: smoke N=512 must complete all cells in < 30s
   wall time.
4. Consider switching to scipy.sparse.linalg.eigsh (ARPACK) for the k=5 extreme eigenvalues
   only -- much cheaper than full eigvalsh at N=4096.
5. Add per-experiment-file timeout argument check: assert args.timeout > 0.

---

## Status-log note

Both anchors flagged as FAILED -- no data recoverable. Strategy should treat them as
design-blocked and require explicit re-design (not just re-queue) before next ship.

## Runners

cpu_runner_0 (PIDs 182380 / 196548) and gpu_runner_0 (PIDs 104624 / 164580) were NOT touched.
Both are alive and idle after the stuck experiments exited. No runner restart needed.

Acted-on 2026-06-02: q_f4 + q_c2 stuck-kill diagnostics filed; both anchors marked failed in queue.json; redesigns deferred to research
