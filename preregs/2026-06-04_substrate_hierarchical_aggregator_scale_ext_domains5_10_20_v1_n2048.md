# Prereg: substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048
## Anchor
substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048
## Routing
routing_hierarchical_aggregator_scale_extension_n10_n20_2026-06-04. Extends 5-corpus aggregator HARD_PASS to
N_domains=10/20. torch->GPU (route-by-torch). $0. Reuses 5-corpus scaffold. 3 cells (D=5,10,20) x 3 seeds.
## Scientific question
Does multiplicative-capacity aggregation hold 5->10->20 domains at substrate N=2048: aggregator beats
cross-domain, preserves >=~87% specialist skill, deletion-cert retention >=0.95?
## Pre-registered bands (per cell; BPC nats)
HP: H3<H2 AND H3<=H1*1.15 AND H4>=0.95 AND 3/3 seeds. MID: H3<H2 but skill 70-87% OR H4 in[0.85,0.95).
HF: H3>=H2 OR H3>H1*1.43 OR H4<0.85. AGG: SCALES_CLEANLY/PARTIALLY/BREAKS_EARLY.
P_joint (HP at D10) ~0.32 per routing (deflated).
## Formula self-tests (PROT-022)
D=20 keys orthogonal(|cos|<0.2) / bind invertible / cf-RPE shrinks / distinct Zipf / uniform=ln(V). [PASS]
## Smoke gate
Smoke (N=256,D=3/5): HARD_PASS SCALES_CLEANLY; H3 beats H2, ~specialist, retention~1.0. Full D=5/10/20 N=2048 is the test.
## Cost control
H4 deletion-cert sampled at K_DEL=4 deleted domains/cell (bounds O(D^2) retraining at D=20); H2 cross sampled<=40 pairs.
## PROT-018/019/021
_n2048 -> substrate N=2048 (domain sweep is a cell var). timeout 14400s. 3 seeds, per-seed partials.
## Queue
overnight_queue (GPU; behind Llama v6).
