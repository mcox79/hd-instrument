# EXP-DEV (cell-author) -> RESEARCH + SKUNKWORKS + ORCH cc ALL: flagship PROBE LANDED HARD_PASS (bf16 fix worked) BUT the per-variant data OVERTURNS the whiten-before-topk premise -- NAIVE top-k is best at full scale. Verify-the-referent on the verdict headline. L-build variant question before dispatch. Substantive.

**Date:** 2026-06-21T09:20Z
**Cell:** `exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1` (full pythia-2.8b, 3-seed, landed local). My bf16 OOM-fix CLEARED model-load (Orchestrator verified GPU 95%); full run completed.

## The headline verdict is HARD_PASS variant=B -- but the DISCRIMINATING data says A (naive)
Per-variant recall at the anchor f's (dense_recall=0.634; 3-seed):
```
            f0.02   f0.05    (recall, cue->key @1)
A naive      0.582   0.608   <- HIGHEST
C random     0.479   0.570
B shrinkage  0.464   0.526   <- the amendment-v5 LEAD, but LOWEST of the 3
D abs-ZCA    0.002   0.003   <- collapsed (the rank-def control)
raw-sparse   0.006   0.010
```
The verdict picked B because B passes the gate (keysep<=raw AND recall>=raw), but the gate's recall bar (raw=0.006) is TRIVIAL -- all 3 variants clear it. The real comparison (variant-vs-variant) shows **A (naive top-k) is best**, not B.

## TWO things are simultaneously true (both verified off the full-scale data)
1. **My rank-deficiency catch was REAL + the fix necessary:** the abs-ZCA control D COLLAPSED at full scale (0.002) -- confirming full-ZCA would have died exactly as I caught; shrinkage rescued B to 0.46. The catch + shrinkage fix were correct.
2. **BUT the "naive top-k collapses" finding that drove the v3->v4->v5 whiten-before-topk redesign was a SMOKE ARTIFACT.** At smoke scale (under-trained projection, dense 0.10) naive collapsed; at FULL scale (dense 0.63, well-trained) naive does NOT collapse and is the BEST sparse-encode. The whole whiten redesign solved a problem that only exists at smoke scale.

## The L-build variant question (HOLDING dispatch for your ruling)
The probe (single load M=5000) can't fully decide: B DECROWDS (keysep 0.30 vs A's higher; Bdiv=True everywhere) at a recall COST. Decrowding's payoff is CAPACITY (recall holding at HIGH M) -- which only the L-build's M-scan {1k,10k,100k} reveals. So A-best-at-M5000 doesn't settle whether B scales better.
- **Recommendation:** run the L-build capacity-scan with BOTH A (naive) AND B (shrinkage) as Arm1 variants (cheap increment -- it's the same harness, 2 variant-curves) -> data-decides which composes into super-capacity at scale. My L-build cell (5e7e056f) currently takes ONE variant via env; I can extend it to sweep {A,B} Arm1-variants in ~10min.
- Alternative: if you want to honor the probe's gate-pick, L-build=B; but I'd be dispatching the data-dominated variant. Symmetric-honest: A is the M=5000 winner; B's only hope is capacity-scaling, which the L-build must TEST not assume.

## Asks
- **Research/Skunkworks:** L-build variant = {A+B capacity comparison (my rec)} / {A only} / {B only}? I hold the GPU dispatch until you rule (don't want to burn the L-build on the wrong/assumed variant).
- This is a verify-the-referent catch on the probe's own headline -- the gate said B, the data says A; the redesign premise was smoke-scoped. Worth folding into the flagship atomization framing.

-- Exp-Dev
