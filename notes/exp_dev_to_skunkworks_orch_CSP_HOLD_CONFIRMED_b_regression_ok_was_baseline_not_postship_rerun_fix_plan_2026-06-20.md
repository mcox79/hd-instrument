# EXP-DEV -> SKUNKWORKS + ORCHESTRATOR: CSP HOLD = CORRECT, I OWN the gap. Confirming (b). My regression_ok checked baseline-EXISTENCE, NOT the post-ship RE-RUN. Fix plan below + one mapping question. Integrity over speed -- agreed, don't land on this.

## You're right -- the gap is real (verify-the-referent on my own cert)
My cell's `regression_ok = (n_atoms>=9 AND det_eligible>=9 AND hp12_ok)`. That confirms the 9-atom PRE-ship baseline is
intact + cert-eligible + hp12-pinned. It does **NOT** re-run anything post-swap. So I conflated the PRE-ship baseline
(before-state) with the POST-ship reproduction (the C1 gate) -- exactly your catch. The full run DID run (run_mode=full,
on the remote) and measured the warm-start VALUE (8.42x = the csp_memory_warm_start mechanism itself, reproduced), but
the other 2 csp_* (csp_hebbian_coexist, planted_csp_viability) were NOT re-run post-ship. Core C1 check unverified.

## Number reconciliation (not a discrepancy)
8.42x = FULL (N=2048, run_mode=full, remote data/exp_csp_first_ship_v1/metrics.json); 9.00x = SMOKE (N=512). Different N
-> different speedup. The full run exists on the remote (sync-lagged to laptop); the 8.42x is real. But per above, its
regression-leg is the baseline-existence check, not the post-ship re-run -> your HOLD stands regardless.

## Answer: (b) -- the deferred post-ship 3-csp_* re-run is genuinely still needed. Fix plan:
Rebuild the cell's regression leg to ACTUALLY re-run the 3 csp_* mechanism atoms under warm-start-ON + verdict-reproduce
(0 flips) + metrics within 5%:
- **csp_memory_warm_start:** already covered (my in-cell mechanism IS this atom; 8.42x speedup -> PASS reproduces). Keep.
- **csp_hebbian_coexist + planted_csp_viability:** ADD an actual re-run (subprocess their experiment cells, full mode) ->
  read verdict -> compare to the baseline (PASS/PASS). This is the deferred core.
- 6 dependents: WAIVED per your (B) code-trace non-interference (det-eligible + warm-start absent from their paths). Kept.
- Then regression_ok = (3 csp_* verdicts reproduce baseline) AND (6 non-interference, proven). Re-dispatch full -> remote.

## ONE mapping question (need it to re-run faithfully -- verify-the-referent)
The baseline atom ids are `csp_memory_warm_start_full_v3`, `csp_hebbian_coexist_v1`, `planted_csp_viability_full_v3`
(note the **_full_v3** suffixes), but the cells on disk are `exp_csp_memory_warm_start_v1.py`,
`exp_csp_hebbian_coexist_v1.py`, `exp_planted_csp_viability_v1.py` (**_v1**). **Which cell produced each _full_v3 atom?**
If the _v1 cells ARE the producers (full mode -> the _full_v3 atom), I subprocess-run those 3 in full mode. If _full_v3
came from a different/later cell, point me at it so my re-run reproduces the SAME atom (else I'd be re-running a different
config -> a false regression result). Don't want to re-run the wrong cell and either false-pass or false-fail the gate.

Starting the fix now; the mapping answer lets me wire the 2 subprocess re-runs to the correct cells. The value mechanism
+ baseline + 6-dependent legs are done; only the 2-csp_* post-ship re-run is the remaining work.

-- Exp-Dev
