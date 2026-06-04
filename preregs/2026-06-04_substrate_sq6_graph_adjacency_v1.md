# Prereg: substrate_sq6_graph_adjacency_v1
## Anchor
substrate_sq6_graph_adjacency_v1
## Routing
research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration (SQ6; P_drill=0.72; GraphHD precedent).
CPU numpy, $0. remote_cpu_queue (standard exploration experiment).
## Scientific question
How many edges E can one bundled substrate vector hold (G=sum node_u*node_v) with separable edge-membership
queries (>=95% balanced accuracy)? Maps graph capacity.
## Pre-registered bands (E_max = max E with acc>=0.95)
HARD-PASS E_max>=N. MIDDLE E_max in [0.25N, N). HARD-FAIL E_max<0.25N.
## Formula self-tests (PROT-022)
bind symmetric / true-edge~1 non-edge~0 / distinct nodes / N set. [PASS]
## Smoke gate
Smoke (N=512): acc degrades with E (0.86@0.25N -> 0.63@2N); likely modest capacity (<0.25N at 95%). Honest
characterization; full N=2048 gives the number. (SNR ~ 1/sqrt(E/N) so E_frac-dependent, not N-dependent.)
## Queue
remote_cpu_queue (numpy). timeout 14400s.
