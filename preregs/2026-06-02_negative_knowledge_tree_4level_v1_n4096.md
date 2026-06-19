# Pre-registration: negative_knowledge_tree_4level_v1_n4096

Date: 2026-06-02
Anchor: negative_knowledge_tree_4level_v1_n4096
Queue: remote_cpu_queue
Seeds: [7, 17, 23, 31, 41]
N: 4096

## Hypothesis
4-level Hadamard hierarchy (L0 policy -> L1 concept -> L2 pointer -> L3 instance)
with B-repulsion (negative knowledge) at each level. Tests whether NK Tree extends
to 4 depth levels while maintaining cert-chain validity and parity contamination isolation.
PP-48 depth-extension of PP-45/NK Tree.

## Pre-registered Thresholds
HARD-PASS: cert_valid >= 0.85 AND parity_contam <= 0.05 AND b_repulsion >= 0.90 (>=60% seeds).
HARD-FAIL: cert_valid < 0.50 OR parity_contam > 0.30.
MIDDLE: 2/3 cells pass.

## Calibration Source
3-level NK tree HARD_PASS at N=4096 (prior anchor). 4-level adds one more Hadamard
composition layer; slight degradation expected but HP=0.85 should hold at N=4096.

## Smoke Result
HARD_PASS: cert_valid=1.0, parity_contam=0.0, b_repulsion=1.0 (N=4096, 2 seeds).
