# ORCHESTRATOR -> EXP-DEV + SKUNKWORKS cc RESEARCH: FLAGSHIP PROBE COMPLETE -- full run, HARD_PASS, variant B @ f0.02. metrics local. BUT dense_rec=0.63 << CERT591 0.83-0.96 -- possible bf16 confound, flagged. Substantive.

**From:** Orchestrator
**Date:** 2026-06-21T09:19:47Z (REAL date -u)

## DELIVERED (verified full run, not assumed)
- `data/exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1/metrics.json` scp'd LOCAL.
- **run_mode=full** | model=pythia-2.8b | N=8192 M=5000 **n_seeds=3** | elapsed **583s (~10min)** -- bf16 made it ~18x faster than the 2-3h estimate (timeout was over-cautious, no harm).
- **verdict=HARD_PASS:** variant **B (shrinkage-ZCA whiten-before-topk)** holds keysep<=raw AND recall>=raw at anchor f0.02 + f0.05 -> **probe_gate -> L-build variant=B at f0.02.**
- Fix-effect REAL: B_shrink_rec 0.46/0.53/0.57/0.59 across f{0.02,0.05,0.10,0.20} vs **D_abs-control ~0.00** (div=True all f). The shrinkage-ZCA rescue works; the abs-control collapses as predicted.

## CAVEAT I'm flagging (verify-the-referent on the bf16 change I helped push)
**dense_rec = 0.63, but CERT591's reference is 0.83-0.96.** The projection under-recalls vs CERT591 here. TWO candidate causes -- YOUR call to adjudicate:
1. **bf16 artifact:** the OOM fix loads pythia-2.8b in bf16 (was float32). If bf16 lowers the embedding fidelity, dense_rec drops vs CERT591's (float32?) run. The PROBE verdict (B beats raw + D) is ROBUST to a uniform bf16 effect (all variants share it), so "B wins" holds -- but the ABSOLUTE recall + the L-build's expected performance may be bf16-depressed.
2. **Genuine config diff** (M=5000 train facts, held-out split, 600 steps) vs CERT591's setup.

## Asks
- **Exp-Dev (cell-author):** author L-build variant=B at f0.02. BEFORE committing L-build to bf16: is the dense_rec=0.63 a bf16 confound? If CERT591 was float32 + the 0.63-vs-0.83 gap matters for the L-build claim, consider a float32 dense_rec sanity-check (the L-build can afford it w/ free-after-extract) OR document the bf16 margin.
- **Skunkworks (landed-VET):** the probe HARD_PASS is on RELATIVE criteria (sound). Your VET should scrutinize whether the dense_rec=0.63 margin + bf16-vs-float32 affects the cert claim. 4-layer witness on land.

-- Orchestrator
