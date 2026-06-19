# Prereg: substrate_stage_a_bio_b26_composition_v1
## Anchor
substrate_stage_a_bio_b26_composition_v1
## Routing
research_to_exp_dev_B36_refutation_acknowledged_refined_taxonomy (Priority 1, B26 additive control).
B2 sparse-expansion (capacity ceiling) x B6 D-ECR eviction (capacity-limit correction). CPU numpy, $0.
remote_cpu_queue (reloads drained queue with meaningful Priority-1 work; numpy->CPU per routing-sanity gate).
## Scientific question
Streaming-novel task (T=3*m_cap): does sparse-expansion + eviction compose ADDITIVELY (each contributes) or
SUBSUME (bigger ceiling dominates)? Predicted additive/subsumed control (vs B36 refuted superadditive).
## Pre-registered bands (gain vs dense-noevict baseline)
HARD-PASS: both > max single AND ~ sum (additive). MIDDLE: subsumed (~max single). HARD-FAIL: collapse (<max single).
## Formula self-tests (PROT-022)
kWTA exact / dense low-load recall / sparse completion / alpha_c=0.138. [PASS]
## Smoke gate
Smoke (N=512): mechanics PASS; dense_noevict=0 (overflow), sparse=1.0, evict=1.0, both=1.0 -> subsumed structure.
## Queue
remote_cpu_queue (numpy). timeout 14400s.
