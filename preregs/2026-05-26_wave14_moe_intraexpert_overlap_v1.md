# Prereg: wave14_moe_intraexpert_overlap_v1

**Date:** 2026-05-26
**Question:** Is MoE SHIFT K-scaling flat due to intra-expert overlap (patterns not cleanly separated)?

## Hypothesis
K-scaling v1 MIDDLE (flat, p=-0.02). M-scaling HARD_FAIL (no structural lift). Gating sharpness HARD_FAIL.
Remaining hypothesis: the routing mechanism assigns similar patterns to ALL experts, so structural separation
provides no benefit. Measurable as: mean inter-expert cosine similarity >= 0.3 at K >= 8.

## Design
- K sweep: {2,4,8,16,32}; N=2048; M_per_expert=800; 3 seeds
- CPU (remote_cpu_queue); ~30-60 min

## Pre-registered bands
- **OVERLAP_DOMINANT**: inter_cosine >= 0.3 OR routing_entropy >= 1.5 bits at K >= 8
- **STRUCTURAL_SEPARATION_CLEAN**: inter_cosine < 0.1 AND routing_entropy < 0.5 bits
- **MIXED_EVIDENCE**: intermediate

## Calibration
No prior empirical anchor. First-probe policy (±50% on thresholds).
If OVERLAP_DOMINANT: MoE SHIFT is not a viable structural mechanism; escalate to alternative architectures.
