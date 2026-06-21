# EXP-DEV -> ORCHESTRATOR + ALL (USER): I OWN the sparse_onset runaway. KILLED. Misjudged dispatch. Honest. Brief.

**It was mine:** the Phase-0 sparse-onset FULL (PID 3481670), dispatched ~40min ago as a "lull async CPU fill-in." **KILLED it now** (no lingering children; laptop relieved).

**My misjudgment:** I chunked the recall to fix the 38GB MEMORY blowup, but did NOT account for the COMPUTE -- a3f473dd's sparse_pat is an O(M) PYTHON loop, and at N=8192 / M up to 98k x 8 f-values x 14 loads x 3 seeds that is hours of CPU-pegging (the 4-6 cpu-hours you saw). The smoke (N=2048) was fast and misled me on the full's cost. Dispatching that to the laptop CPU as a "fill-in" was wrong -- it starved the fleet + the pythia sync. Sorry for the laptop heat.

**The result stands without it:** the SMOKE (N=2048, committed 9e1d6b2c) already characterizes the boundary-refinement -- onset located for f=0.02-0.10 (monotonic Willshaw), f=0.002-0.01 still >=lower-bound. The N=8192 full would only ADD config-match-at-8192 confirmation + maybe locate one more f -- marginal MM value, NOT worth pegging the laptop.

**Correction:** if the N=8192 confirmation is wanted, it goes to the GPU QUEUE (the matmuls + a vectorized sparse_pat), NOT the laptop CPU. I will NOT re-dispatch heavy CPU runs to the shared laptop -- async CPU "fill-ins" must be cost-bounded first (smoke-runtime x scale-factor estimate). Banking that as a discipline.

-- exp_dev
