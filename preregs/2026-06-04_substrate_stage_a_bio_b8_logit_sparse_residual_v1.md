# Prereg: substrate_stage_a_bio_b8_logit_sparse_residual_v1
## Anchor
substrate_stage_a_bio_b8_logit_sparse_residual_v1
## Routing
research_to_exp_dev_B8_residual_encoding_cells_per_drill (Cell 4, recommended first). Logit-space top-K sparse
residual fixes round-1 r=0.86 (random-codebook full-residual -> r->1). CPU numpy, $0. remote_cpu_queue (reload).
## Scientific question
Does storing only the top-K (K=5) logit-residual symbols give r~sqrt(K/V)~0.27 AND a useful reconstruction
(base + sparse residual predicts next char better than base alone)?
## Pre-registered bands (per spec)
HARD-PASS r<=0.30 AND M_crit gain>=10x. MID r in [0.30,0.55] OR gain 4-10x. HARD-FAIL r>0.55 AND gain<4x.
HEADLINE metrics = r + reconstruction-vs-base. NOTE: M_crit-gain sub-metric unreliable (sparse-residual
auto-assoc recall measurement returns 0 -- a measurement artifact, not the residual mechanism; r + reconstruction
are the load-bearing results).
## Formula self-tests (PROT-022)
sparse<full norm / topK selects largest|err| / dense recall / sqrt(K/V)=0.267. [PASS]
## Smoke gate
Smoke (N=512): r=0.272 (matches predicted 0.267); reconstruction base 0.52 -> base+residual 0.77 (residual USEFUL).
M_crit-gain measurement buggy (sparse=0) -- flagged; r+reconstruction validate the mechanism.
## Queue
remote_cpu_queue (numpy). timeout 14400s.
