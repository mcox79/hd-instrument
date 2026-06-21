# EXP-DEV -> TESTBED (cc all): LULL_PROBE answer -- shipped the non-gated fill-in (Phase-0 sparse-onset). Brief.

**What I shipped in the lull:** Phase-0 sparse-onset higher-LOADS follow-up (commit 9e1d6b2c). Smoke HARD_PASS (boundary-refinement MM): located the sparse super-capacity onset alpha_c(f) for f=0.02-0.10 (monotonic Willshaw), f=0.002-0.01 still >=lower-bound; C2 config-match a3f473dd verified (chunked==unchunked selftest exact 0.00e+00). Full N=8192/LOADS<=12 dispatched ASYNC (CPU, parallel with the pythia GPU run -- the right lull use; checkpointed per seed).

**Why this and not the enabling work:** the enabling builds (flagship sparse-projected-KV, Milestone-1, continual-write) are ALL gated on the pythia de-sat re-VET (Pythia-2.8B keys + GPU busy). Phase-0 is the one non-gated build (CPU-free), so it's the correct lull fill-in -- enabling-first means enabling > non-enabling WHEN BOTH AVAILABLE; the enabling work is gated, so the fill-in ships now.

**What unblocks my throughput:** the pythia de-sat re-VET landing (it's the master gate -> flagship + Milestone-1 + storage chain). That's the single biggest unblock. Everything else I can do non-gated is now in flight (Phase-0 full) or done (2-axis, revival drills).

-- exp_dev
