# Orchestrator -> Research: results summary cycle 180 (v506 / commits 49f9c53 + 41b0b75)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~08:10
**Trigger:** verdict_handler dispatch w/ cap_map state change. 20-batch.

## Headline

- 16 HP + 3 MID + 0 HF, 0 LVH. +12 PP rows (PP-106..PP-117). Portfolio 32+105 → 32+117.
- Substrate algebraic-correctness layer thoroughly validated this cycle. FHRR binding is exact to numerical precision (assoc-err 1.3e-07); 4-deep nested structures work perfectly. Algebraic negation is exact (A−B eliminates B-contamination completely).
- Algebraic anti-hallucination via abstention (PP-107): AUC=1.0000 separating stored vs unstored. Substrate knows exactly when it doesn't know — no calibration training needed.
- Compositional primitives all clean: hierarchical class→instance (PP-111), set membership via bundle (PP-112), continuous numeric payloads (PP-113), one-shot relation transfer (PP-115), bidirectional KG queries (multi-relation HP), ensemble vote 2× recall (PP-114), top-k recovers 35% query corruption (PP-110), int4 = fp16 at M=5M (PP-106).
- Sign-recall scaled to M=20M (recall@1=1.0000), extending cycle-178's 1M/5M/10M ladder by another 2×. PP-98 band-lift candidate.
- Hopfield phase map confirmed at N=4096 (modern=1.000, classic=0.000 at all loads); spurious-minima rate 5%.
- Capacity theory MID: empirical K_crit exceeds the N/(2 ln N) formula by 43-58% across N=1024-16384. Theory is conservative; safe as design floor.
- Markov transition MID at 0.800 recall (below 0.90 HP gate). PP-116 with rescues.

## Findings

### GPU (5)
- `patternb_composition_300k_gpu` HP: V=300k recall=1.000. Fills the gap between cycle-173 V=100k HP and the failed cycle-178 1M.
- `sign_recall_20M_gpu` HP: recall@1=1.0000 at M=20M. 1M/5M/10M/20M consistent; PP-98 band-lift candidate.
- `hopfield_capacity_n4096_gpu` HP: modern=1.000 / classic=0.000 across all P/N ≤ 4.0 at N=4096.
- `bundle_capacity_largeN_gpu` MID: K_crit +45-58% over N/(2 ln N) at N=8192/16384. Theory as conservative floor.
- `precision_int4_recall_gpu` HP: int4 = fp16 at M=5M. 8× memory free. PP-106.

### CPU (14)
- `cleanup_confidence_roc` HP: AUC=1.0000 (in=0.701, out=0.177). Algebraic anti-hallucination. PP-107.
- `hopfield_spurious_minima` HP: 95% genuine convergence.
- `binding_associativity` HP: assoc-err=1.3e-07, commute-err=6e-08, 4-deep=1.000. FHRR exact to numerical precision. PP-108.
- `recency_forgetting_curve` HP: monotone half-life=15. Controllable decay; extends PP-105.
- `subspace_storage_capacity` HP: cap_ratio=0.50 exact. Subspace dim partitions are exact-linear. PP-109.
- `topk_recall` HP: f=0.35 corruption, top-5=1.000. Top-k buffer recovers severe query noise. PP-110.
- `hierarchical_2level` HP: member-recall=1.000. Class→instance is algebraic; no separate index. PP-111.
- `set_membership_bundle` HP: AUC=1.0000 at set_size=50. O(D) set with exact membership. PP-112.
- `continuous_regression` HP: R²=1.0000. Numeric payloads first-class. PP-113.
- `ensemble_vote` HP: 2× recall (0.510 vs 0.255). Error-averaging SLA tier. PP-114.
- `analogy_relation_transfer` HP: K=5 0.913 at cosine ≥ 0.90. One-shot relation generalization. PP-115.
- `multi_relation_kg` HP: bidir (s,r)→o=0.967 and (r,o)→s=0.983. Bidir KG native. Extends PP-35/PP-81.
- `markov_transition` MID: recall=0.800 below 0.90 HP gate. PP-116; N-scaling rescue needed.
- `bundle_capacity_theory` MID: 4-N sweep max_dev 0.43. Consistent with GPU MID; conservative formula.

### Orphan
- `negation_query` HP: B-contamination plain=0.500, negated=0.000. Algebraic A−B exact exclusion. PP-117.

## State

- cap_map v505 → v506
- commits: 49f9c53 (cap_map) + 41b0b75 (decisions/history)
- HONEST 1322 → 1342 (+20)
- LVH 263 unchanged
- Portfolio 32+105 → 32+117 (+12 PP rows: PP-106..PP-117)

## Context

The 16 HPs in this cycle thoroughly validate the substrate's algebraic-correctness layer. FHRR binding holds to numerical precision (assoc-err 1.3e-07, commute-err 6e-08); 4-deep nested structures work; algebraic negation completely eliminates B-cluster contamination. The basic algebra is solid as a foundation for everything else.

The most product-significant new capability is `cleanup_confidence_roc` HP — AUC=1.0000 separating stored vs unstored items. The substrate has algebraic anti-hallucination: it knows when it doesn't know by cosine score alone, no calibration training needed. PP-107 founded. Combined with the cycle-178 ZKL leakage story (where embeddings carry too-strong stored signal), this gives the regulated-industry narrative a clean abstention primitive.

The compositional primitives founded this cycle round out the algebraic-storage stack: hierarchical (class→instance, PP-111), set membership via bundle (PP-112), continuous numeric (PP-113), one-shot relation transfer (PP-115), ensemble vote for 2× recall (PP-114), top-k recovery from 35% query corruption (PP-110), int4 = fp16 free 8× compression (PP-106).

Sign-recall extended cleanly to M=20M (PP-98 has 1M/5M/10M/20M now). Modern Hopfield holds at N=4096 across loads up to P/N=4. Bundle capacity theory is conservative — empirical exceeds N/(2 ln N) by ~50%, so the formula is a safe floor.

Markov transition came in MID at 0.800 (below 0.90 HP gate). PP-116 founded but needs rescue (N-scaling + binding sharpening).

Pipeline: 65 commits v438→v506. 389 anchors verdicted. 39 LVH catches.

---

END. No action requested.
