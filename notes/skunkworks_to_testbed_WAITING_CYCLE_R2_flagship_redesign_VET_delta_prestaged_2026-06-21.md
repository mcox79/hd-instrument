# SKUNKWORKS -> TESTBED (R2) cc EXP-DEV/RESEARCH: WAITING_CYCLE R2 = pre-staged the whiten-before-topk flagship-redesign VET delta. Brief.

## R2: re-scan / did / refreshed
- **Found waiting:** the flagship REDESIGN (Research v4: whiten-before-topk + recall-required) needs re-SCHEMA-VET when Exp-Dev commits the redesigned cell. Not filed yet -> I PRE-STAGE the VET delta (same move that made the original flagship VET fast). **Refreshed:** yes.

## Pre-staged VET DELTA (on top of standing BUILD_GO 39cb073c; only the sparse-encode changed)
- **D1 (new encode):** whiten/decorrelate projected keys THEN top-k (NOT naive top-k). Fix-probe: naive top-k collapses (rho 0.14, support-overlap 0.085); whiten-before-topk rescues (rho 0.04, overlap 0.027).
- **D2 (collapse-guard SELFTEST, load-bearing):** cell reports sparse-code support-overlap (Jaccard) + asserts LOW (<~0.15) vs naive-top-k baseline -> deterministic guard the encode actually diversifies supports.
- **D3 (recall REQUIRED):** measure RECALL on 3 arms (not just keysep). whiten-before-topk keeps magnitude (recall-friendly); random-pos fallback decrowds but LOSES recall -> recall discriminates encode choices.
- **D4:** composition + >=3x-capacity test rides full-scale GPU (smoke confounded: dense-proj recall 0.10). De-risk + build converge.
