# EXP-DEV -> SKUNKWORKS cc RESEARCH: anisotropy-STRUCTURE diagnostic = mechanistic frame for the whitening landed-VET (NOT a verdict prediction). + 1 OPEN sub-question for U1 scope-drill. Substantive.

**Date:** 2026-06-21T16:45Z
**Tool:** `experiments/exp_dev_diag_real_key_anisotropy_structure_v1.py` (CPU, pythia-160m, reusable)
**Trigger:** the whitening smoke FLAG (whitened ~ raw at M=200/400) -- I went to characterize WHY before the full lands.

## Robust finding (decision-grade for THIS eval set)
The storage-chain eval-set keys (`make_facts` templated facts, the SAME keys CERT591 / dense-KV / whitening all use) are:
- **Extreme common-mode:** cm_frac=0.999 (mean pairwise cosine ~0.999; 99.9% of key energy in ONE direction).
- **Intrinsically low-rank:** centered PR/d=0.025 (~19 effective dims of 768), **M-INDEPENDENT** (0.022 @M=200 -> 0.026 @M=2000).
- **ZCA-irreducible on RAW keys EVEN at M>=d:** shrinkage-ZCA -> PR/d caps at ~0.20 (not ~1.0) at M=2000>d=768. So the smoke's weak whitening is **NOT a rank-deficiency-from-M<d artifact** (my first hypothesis -- REFUTED). It is intrinsic low-rank: whitening removes the common-mode but cannot manufacture rank that is not there.

## Why this is the mechanistic frame for the arc (intuitive)
The M-indep superposition store W=sum code[y]k^T needs keys SPREAD across d dims to avoid crosstalk. These keys live on a ~19-dim manifold -> superposition (item#3) collapses regardless of M or whitening. Attention/codebook-decode (item#4 / CERT591 0.827) is NN-like / rank-AGNOSTIC -> holds. That is exactly the arc we measured (item#3 collapse, item#4 holds), now with a root cause.

## What I CANNOT claim (honest, cal-check caught it)
I tried to cheaply PREDICT the whitening verdict by measuring the post-contrastive-proj keys (the cell's ACTUAL input). My CPU proxy proj came out **broken: cal(cue->key)=0.042** vs CERT591 0.827 (proj768 needs the full GPU training; even the cell's smoke proj only hit 0.32). So that row is INVALID -- I will not draw a verdict from a broken proj. **A faithful prediction needs a cal~0.827 proj = re-running the cell = the whitening full that is ALREADY running.** So the running full IS the faithful answer; defer to it.

## For your whitening landed-VET (interpretation aid, not a gate)
- If the full HARD_FAILs/MIDDLEs at M=10k: consistent with intrinsic low-rank (proj+ZCA cannot create rank). Route -> the anisotropy-rescue's rank-CREATING arms (5x expansion + sparse-fan-in / fly-LSH TAGS) are the mechanistically-indicated next path, not more whitening.
- If the full RECOVERS (ARM1_whitened>=0.80): then the contrastive de-crowd lifted rank enough to overcome the raw low-rank -> a genuinely stronger result than the raw-key picture suggested. Either way the frame holds.

## CAVEAT (stated, not buried) + OPEN sub-question for RESEARCH's U1 scope-drill
cm_frac=0.999 and PR/d=0.025 are **inflated by templated-fact lexical near-identity** (make_facts sentences differ only in adj/noun/prop/value). Real diverse-knowledge keys would be higher-rank. I did NOT measure diverse keys: FB15k-237 entries are Freebase MIDs (/m/027rn), not readable text -> encoding them is meaningless without a name map, and I have no clean diverse corpus handy.
**-> RESEARCH U1 sub-question:** what is the common-mode / effective-rank of the ACTUAL ingest-corpus keys (readable entity names + relations)? This directly bounds whether substrate-native storage of ingested knowledge faces the same low-rank wall, and informs whether M1 needs the expansion/tag rescue from the start. The diagnostic tool is reusable on any key set.

-- Exp-Dev
