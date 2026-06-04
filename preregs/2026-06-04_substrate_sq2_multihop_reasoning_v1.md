# Prereg: substrate_sq2_multihop_reasoning_v1
## Anchor
substrate_sq2_multihop_reasoning_v1
## Routing
research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration (SQ2 exploration; P_drill=0.72). CPU numpy, $0.
remote_cpu_queue (standard exploration experiment per user "more standard experiments on remote cpu").
## Scientific question
Store G reasoning chains (heteroassoc W); iterate sign(W q) K hops; how deep (K) does the substrate traverse
before chaining breaks, at load = 0.5*alpha_c*N? Tests iterated-retrieval multi-hop (TC0 single-pass -> NC1 iterated).
## Pre-registered bands (depth = max K with mean acc>=0.80)
HARD-PASS depth>=8. MIDDLE depth in {2,4}. HARD-FAIL depth<2.
## Formula self-tests (PROT-022)
1-hop / 2-hop traversal / distinct items / alpha_c=0.138. [PASS]
## Smoke gate
Smoke (N=512, G=2): HARD_PASS all 12 hops (low load); full N=2048 (~11 chains) is the load test.
## Queue
remote_cpu_queue (numpy). timeout 14400s.
