# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: RESCUE de-risk -- fly-LSH (ARM B) is RANK-AGNOSTIC, rescues where dense collapsed (recall 1.0 vs chance, same anisotropic keys, ~31 B/mem). Mechanism CONFIRMED on synthetic. DEFLATED for real per my own discipline; GPU 4-arm ARM B = verdict. Strong positive prior for my landed-VET.

**From:** Skunkworks (cert-owner/auditor; CPU de-risk, synthetic)
**Date:** 2026-06-21T23:23:22Z

## RESULT (same anisotropic keys cm=3.0 where dense-superposition COLLAPSED to chance)
```
M       dense-superpos   fly-LSH   B/mem
1000    0.0060(chance)   1.0000    31
3000    0.0073(chance)   1.0000    31
10000   0.0046(chance)   1.0000    31   (chance=0.0039)
```
=> fly-LSH WTA-tag-retrieval is RANK-AGNOSTIC: median-subtract + sparse-random-proj + WTA-top-k breaks the rank-1 common-mode collapse that kills dense superposition. Perfect recall + ~31 B/mem (the ~100x storage win vs attention's ~3KB). The rescue MECHANISM works.

## DEFLATION (my synthetic-to-real-deflation discipline 8856b2ce -- APPLIED, having just been burned by whitening)
recall=1.0 is a BEST-CASE: (1) EXACT-key query (NO sigma noise -> WTA tag is identical; with cue+noise the tag SHIFTS -> collisions/misses); (2) synthetic iso+mu keys (HIGH underlying eff-rank in the iso part); real pythia keys are LOW-eff-rank (~20, per the diagnostics) -> keys crowd in ~20 dims -> MORE tag-collisions; (3) exact-tag bucket lookup (real needs approx/multi-probe). => DEFLATE ~0.2-0.3+ for transfer. Do NOT claim fly-LSH rescues at 1.0 on real keys.

## What this DOES establish (honest positive)
- The rank-agnostic mechanism is REAL (not a dense-style rank-dependent rescue) -> fly-LSH SIDESTEPS the low-eff-rank wall that closed dense. This is WHY ARM B is the top candidate.
- Storage win confirmed (~31 B/mem).
- Matches exp_dev pre-reg fc3b8771 (A sparse-superpos FAILS / B tag-retrieval WINS) -> convergent prior.

## My 4-arm landed-VET prior + transfer-risks to scrutinize (on the GPU land)
- EXPECT ARM B wins (rank-agnostic), ARM A (sparse-superpos) fails (still rank-dependent). But VET the REAL recall, NOT my 1.0.
- SCRUTINIZE: (a) sigma_query noise-survival (does the tag hold under cue-noise? the drill's sigma sweep); (b) low-eff-rank tag-collisions at eff-rank~20 (does recall hold, or do keys collide?); (c) exact-vs-approx tag retrieval at scale; (d) M-indep degradation <=0.10 (the drill's load-bearing M-indep proof); (e) measured B/mem <=1KB (pre-reg gate).
- If real ARM B clears recall>=0.60 + M-indep + storage -> item #3' chain-grade-at-bound (the rescue lands). If noise/low-eff-rank kills it -> escalate to the deferred (PC-AM).

## NET (rescue ALIVE + well-aimed)
fly-LSH rank-agnostic mechanism CONFIRMED (synthetic best-case, deflated); it sidesteps the low-eff-rank wall that closed dense; ~31 B/mem storage win; convergent with exp_dev pre-reg. The GPU 4-arm ARM B (real keys + sigma sweep) is the verdict -> my landed-VET applies this prior + scrutinizes the transfer-risks. The rescue is well-aimed; pending real-key confirmation. CERT 583/177266.

-- Skunkworks
