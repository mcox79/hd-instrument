# Pre-registration: wave14_moe_cosine_router_v3_dynamic

Date: 2026-05-27
Author: orchestrator

## Trigger

MoE router escalation after two HARD_FAIL:
- v1 (random BSC anchors + cosine): entropy@K=16=3.999b > HF=3.0b
- hebbian_anchor_router_v1 (static Hebbian anchors + cosine): entropy@K=16=3.995b > HF=3.0b
Root cause: static anchors (random OR Hebbian) degenerate to uniform routing at K>=16
because BSC anchor vectors lose discrimination in high-dimensional K-regime.
Cap_map v224: "cosine-dot rescue OUT; Hebbian-anchor static HARD_FAIL; dynamic routing needed."

## Design

W-matrix native routing (substrate-native attention):
- Route by argmax_k(v^T W_k v) where W_k is the expert's Hebbian weight matrix
- Dynamic: assignments and W_k co-evolve over 3 routing iterations
- Variant A: W-matrix quadratic score routing
- Variant B: Random-subspace routing (control)
- Bootstrap: random initial assignment; 3 EM-style iterations

## Pre-registered bands

DYNAMIC_ROUTER_HARD_PASS:
  entropy@K=16 < 2.0b for variant A or B AND retention_delta@K=16 >= -0.010
  -> W-matrix dynamic routing solves K-scaling; cap_map MoE row: K ceiling lifts to K>=16

DYNAMIC_ROUTER_HARD_FAIL:
  entropy@K=16 > 3.0b for ALL variants
  -> K-scaling collapse is architectural; K=4 is the confirmed MoE SHIFT ceiling

MIDDLE_BAND: entropy@K=16 in [2.0, 3.0b]
  -> Partial improvement; K=8 may be viable ceiling

## Cap_map rows addressed

- MoE SHIFT/PARTITION row: engineering-rate-limited (K-scaling); this probe resolves
  whether dynamic routing unblocks K=16 as a practical design point
