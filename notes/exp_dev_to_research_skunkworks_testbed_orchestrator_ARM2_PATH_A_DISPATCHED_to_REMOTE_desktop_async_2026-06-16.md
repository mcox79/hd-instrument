# Exp-Dev (Prover) -> Research + Skunkworks + Testbed + Orchestrator: ARM 2 PATH-A (extended runnable single-binder basis) DISPATCHED TO REMOTE DESKTOP (marsh@home, remote_cpu_queue) per DECISION 181 + USER compute policy. Full N=4096 n=3 runs on remote (laptop stays cool); result returns async. Queue-verified present. 208th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** ARM2_PATH_A_DISPATCHED_to_REMOTE_desktop_async

## Dispatch (heavy -> REMOTE per USER policy; via tools/orchestrator/queue_add.sh)
```
  queue: remote_cpu_queue  name: ternary_arm2_extended_basis_2026_06_16
  cell:  experiments/exp_ternary_motif_phase_B_arm2_extended_basis_cpu_v1.py  (pushed 008bffd9; SCP'd to marsh@home)
  prereg: preregs/ternary_arm2_extended_basis_2026-06-16.md
  timeout: 3600s; --self-test passed on remote (2.0s); VERIFIED present in remote queue.json
  -> remote runner executes FULL N=4096 n=3 (8-binder extended basis); result returns async.
```
NOTE: direct local queue_add.py was correctly BLOCKED (remote queue requires the SCP+SSH orchestrator path);
used tools/orchestrator/queue_add.sh as required. NO heavy compute on the laptop (USER policy honored).

## What ARM-2 PATH-A tests (REQUIRED-A; honest scope)
corr(bundle(a,b),c) vs the ~8 EXTENDED RUNNABLE single-binder 3-ary ops (xor3/conv3/bundle3/ghrr3/perm_idx3 +
xorperm3/bundleperm3/convperm3) -- the implemented inventory, not the 5-op proxy. HONEST: the "38 ops" are
SIGNATURES; ~8 are runnable functions. Per-effective-family + non-DFT closure + difficulty-normalized.
LOCAL SMOKE (N=1024; ZERO verdict per run_mode asymmetry) was encouraging: corr_bundle closes where all 8 fail,
universal margin -- but the LOAD-BEARING verdict is the remote FULL run, pending Skunkworks BUILD VET.

## Status of the 3 arms
- ARM 1: VET-CLEARED 2/3 robust HARD_PASS; 3-atom ratify (cleanup_distinct_count T3 + 2 CAPs) executing by Testbed.
  (Minor 4th-dep note: inner_product is the readout dep [T1 -> direct axiom-term]; role_filler_binding is the
   unbind; Testbed/Skunkworks finalize the exact dep set at write+VET -- both valid, minor.)
- ARM 2: PATH-A dispatched to REMOTE (this); load-bearing verdict async.
- ARM 3: QUALIFIED modest scope (mechanism confirmed; gerrymander-gated narrowed-gap = GO-time).

I process + report the ARM-2 remote verdict on return; spot-verify ARM-1 ratify on landing.
-- EXP-DEV (Prover)
