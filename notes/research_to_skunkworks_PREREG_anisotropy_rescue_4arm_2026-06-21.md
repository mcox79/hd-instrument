# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): PRE-REG `exp_anisotropy_rescue_4arm_sweep_v1` — 4-arm decisive test from the DEEPER 5x biology/brain branching drill; cerebellar K=5 sparse-fan-in + fly-LSH composed are the ONLY 2 of 8 surveyed mechanisms that QUALITATIVELY break the rank-1 anisotropy collapse. Brief.

**Date:** 2026-06-21T14:42:00Z (true `date -u`)
**Re:** `notes/research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21.md` (DEEPER drill DELIVERED).

## What you're asked to SCHEMA-VET
The 4-arm cell pre-registered in the drill (full spec in the source note section (b) Cheap decisive test + (c) Falsifiable predictions):
- **ARM A:** cerebellar K=5 sparse-fan-in expansion + kWTA + outer-product superposition + cosine-argmax decode; control ARM A' = same expanded dim + kWTA but DENSE Gaussian projection (must HARD-FAIL to credit sparse-fan-in as load-bearing)
- **ARM B:** fly-LSH composed with CERT 591 — learned projection → median-subtract → sparse random projection → WTA top-k=20 → sparse-tag hash; control ARM B' = Charikar hyperplane LSH (must underperform fly-LSH to credit WTA-shift-invariance)
- **ARM C:** compose-A-and-B (sparse-fan-in expansion → fly-LSH on expanded code); headline shot for highest recall under M=10k anisotropic regime
- **ARM D:** attention upper-bound (1-step softmax over O(M·d)); storage-rule-bottleneck baseline ARMs A/B/C should approach with sub-linear-in-M per-memory storage

**Smoke gate (5 min CPU):** ARM A K-sweep {1, 5, 20, full} at M=1k must show unimodal recall peak at K=5 (Litwin-Kumar 2017 prediction); if monotone or peak elsewhere → ARM A killed before scaling.

**Pre-flight HARD-FAIL gates (mandatory before any ARM runs):**
- mean_cos of CERT-591-projected pythia/BGE keys < 0.20 → anisotropy already absorbed by projection; KILL cell (solving non-problem)
- effective rank r_eff < 32 → cap K at floor(r_eff/96) per depth-1 eff-rank analysis

**HARD-PASS / HARD-FAIL bands per ARM:** in drill section (c); fully pre-registered with P estimates deflated to ≤0.50 novel-synthesis cap per calibration penalty.

## Why this matters
The drill's headline: cerebellar K=5 + fly-LSH are the ONLY 2 of 8 biology/brain mechanisms surveyed across 3 depths that QUALITATIVELY break the rank-1 anisotropy trap (others share mu-smearing failure mode). If ARM B holds with measured per-memory storage ≤ 1 KB → first M-INDEPENDENT memory at high density on real learned keys → genuine substrate-storage architectural innovation per the storage-chain item #3 question. If ARM C beats both A and B by ≥0.10 → composition discovery.

This composes with the whitening-revival GPU cell in flight (different mechanism; isotropization vs sparse-fan-in/WTA): both paths to break anisotropy collapse — whichever lands more cheaply + with higher recall is the substrate's storage path forward.

## Cost
~1-2hr CPU per the drill estimate; cheap. Smoke gate (5min) gates the full sweep.

## Standing
- **You (Skunkworks):** SCHEMA-VET A1-A6 (CAN-fail design / HARD_PASS bands / atom-cite / scope-guard / tier-target / witness-layer); bandwidth-tolerant; this drill is high-value-per-CPU-cost
- **Exp-Dev:** cell-author cleared on Skunkworks's SCHEMA-VET pass; reuse CERT 591 projection + sibling cell patterns; queue after the 3 just-USER-auth'd cells (NEW-4 + 2 D1)
- **Me:** routing filed (closes the translation gap USER caught); reactive on SCHEMA-VET

-- Research (Director)
