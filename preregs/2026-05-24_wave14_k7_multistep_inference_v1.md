# Prereg — K7 Multi-step inference (deduction over chained retrievals)

**Anchor**: `wave14_k7_multistep_inference_v1`
**Queue**: overnight_queue (GPU)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

K7 KILLER Tier-2. Substrate stores M (subj, rel, obj) facts as bundles. Test
deduction: follow chain (R1, R2, ..., R_d) starting from subj_A. If chain
accuracy decays slower than the geometric-exponential law established by
existing-data analysis (r=0.97 per hop), substrate has DEDUCTION beyond
mere pre-stored chained retrieval. If it tracks pure retrieval decay, K7
is multi-hop retrieval relabeled.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: accuracy at depth=5 >= 0.50 AND per-step decay r >= 0.85
  -> K7 deduction capability supported.
- **HARD-FAIL**: accuracy at depth=5 < 0.10 OR per-step r < 0.65
  -> K7 KILLER at this envelope.
- **MIDDLE-BAND**: any intermediate; report bands.

## Parameters (exp_dev autonomy)

- N (substrate dim) = 8192 FULL / 1024 smoke
- N entities = 100 FULL / 30 smoke
- Depths = {1, 2, 3, 4, 5} FULL / {1, 2, 3} smoke
- N queries = 50 FULL / 10 smoke
- Seeds = {7, 17, 23, 31, 41} FULL

## ETA

GPU FULL ~30-60 min.

## Smoke outcome

Smoke at N=1024 single-seed depth=3: acc={1:0.2, 2:0.0, 3:0.2}. The acc=0 at
d=2 is suspicious of a cleanup issue at small N. FULL at N=8192 + larger
entity pool is the test.
