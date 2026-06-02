# Pre-registration: heteroassoc_chain_depth3_v1

**Date:** 2026-06-02
**Anchor:** heteroassoc_chain_depth3_v1
**Script:** experiments/exp_heteroassoc_chain_depth3_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 5400s

## Scientific question (Q-B1)

Does heteroassociative depth-3 chain encoding (H = sum_i val_i @ key_i^T / N)
achieve:
(a) d1 >= 0.90, d3 >= 0.80 (chain retrieval fidelity up to depth 3)
(b) d2_after_deletion <= 0.50 (targeted deletion of B->C link breaks chain)

## Bands (pre-registered)

**HARD-PASS (HP):**
- d1 >= 0.90 AND d3 >= 0.80 for >= 4/5 seeds
- d2_after_deletion <= 0.50 for >= 4/5 seeds (chain broken after deletion)

**MIDDLE:**
- d3 in [0.70, 0.80) OR d2_after in (0.50, 0.70]

**HARD-FAIL (HF):**
- d3 < 0.60 (depth-3 retrieval fails)

## Smoke result
HARD_PASS: seed7 d1=0.997 d3=0.997 d2_after=-0.008; seed17 d1=0.997 d3=0.997 d2_after=0.005.
Both seeds: chain depth-3 works, deletion breaks link.
Wall time: 102s (2 seeds). FULL estimate: ~1500s (5 seeds, N_CHAINS=15, M_BG=30, trials=50).

## PROT-018
No _nN suffix. Production N=4096 declared in script.

## Composition classification
HANDOFF (per-hop independence confirmed in smoke).
