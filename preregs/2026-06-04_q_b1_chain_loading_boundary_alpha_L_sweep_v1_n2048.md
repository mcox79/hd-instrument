# Prereg: q_b1_chain_loading_boundary_alpha_L_sweep_v1_n2048

## Anchor
q_b1_chain_loading_boundary_alpha_L_sweep_v1_n2048

## Priority
A (Q-B1 highest-priority handoff, appears in qb1_chain_loading_boundary + qb1_chain_ceiling). Pins the
chain retrieval-depth ceiling chain_depth_max(alpha) and alpha_c_eff; engineering curve for product spec.

## Scientific question
Sweep background load alpha=M_BG/N in {0.05,0.10,0.15,0.20,0.25,0.28} x chain depth L in
{50,100,150,200,300,400} at N=2048. Measure cos at depth L (hold if >=0.5). For each alpha the largest
holding L = chain_depth_max(alpha). Compare to fit chain_depth_max(alpha)=22/(0.302-alpha); estimate alpha_c_eff.

## Pre-registered bands
HARD-PASS: monotone-decreasing boundary resolved (>=4 alpha cells finite ceiling) AND alpha_c_eff (first
alpha where depth_max collapses to <= min L) in [0.25,0.35] (consistent with 0.302 fit) AND 5/5 seeds.
MIDDLE: boundary visible but alpha_c_eff outside [0.25,0.35] OR 3-4/5 seeds.
HARD-FAIL: no boundary (all-hold or all-collapse across grid).

## Formula self-tests (PROT-022)
1. chain_depth_max(0.10)=108.91. 2. chain_depth_max(0.25)=423.08. 3. cos(xi,xi)=1.0.
4. single-link retrieve cos>0.9. [ALL PASS in smoke]

## N-suffix binding (PROT-018)
anchor _n2048; production N=2048. 5 seeds (PROT-021).

## Timeout
6x6 cells x 5 seeds, chain build + L hops at N=2048; ~3 min est. timeout_s=3600 (well above small-N floor).

## Smoke gate
Smoke PASSED (N=512, 2 seeds): monotone-decreasing boundary observed (depth_max falls with alpha);
self-tests pass. Full N=2048 gives the production curve.

## Queue
remote_cpu_queue (pure numpy; CPU).
