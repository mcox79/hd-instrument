# Pre-reg: landmark/hub-node subgoal routing for autonomous traversal (grounding_multihop_landmark_routing_v1)

Cell: `experiments/exp_grounding_multihop_landmark_routing_v1.py`
Phase-0 pre-check: `experiments/exp_grounding_multihop_landmark_routing_v1_phase0_precheck.py`
Anchor: `grounding_multihop_landmark_routing_v1`
Hand-off: `notes/exp_dev_handoff_research_landmark_subgoal_hub_routing_2026-07-09.md`
Research note: `notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md`
Builds on: `experiments/exp_grounding_multihop_autonomous_subgoal_greedy_v1.py` (commit 5aab289c3); fair-test MM.

## Question
Does routing an autonomous goal-directed walk through a precomputed hub/landmark waypoint (instead of aiming
continuously at the distant final goal) recover the supplied-waypoint ceiling that the plain-greedy autonomous
arm fell short of? (greedy landed MIDDLE_BAND_CG_PARTIAL: reach@2=0.181, 0.363x the 0.499 supplied ceiling.)

## Anchors (MEASURED)
- MEMORYLESS reach@2 = 0.121  MEASURED@data/exp_grounding_multihop_fair_test_unique_successor_goal_v1/metrics.json
- AUTONOMOUS_GREEDY (plain greedy) reach@2 = 0.181  MEASURED@data/exp_grounding_multihop_autonomous_subgoal_greedy_v1/metrics.json
- SUPPLIED_WAYPOINT reach@2 = 0.499 (ceiling)  MEASURED@fair-test metrics.json
- Gap to close = 0.499 - 0.181 = 0.318.

## PHASE 0 (mandatory zero-cost pre-check) -- ran BEFORE build; PROCEED
MEASURED@data/exp_grounding_multihop_landmark_routing_v1_phase0/phase0_result.json (FULL subgraph n=4440, 14767 edges, seed=1234):
- Degree: mean=6.65, median=4, max=337 (max/mean=50.7x), gini=0.504, top1%share=0.110, top5%share=0.281.
- Betweenness (600 sampled pivots): top1%share=0.383 (uniform ~0.01 => 38x over-representation), top5%share=0.659,
  gini=0.866, avg_clustering=0.146 (~100x an expander baseline).
- Nearest-landmark hop distance (betweenness selection): K=64 -> 62% of path nodes within 1 hop (median 1);
  K=128 -> 76% within 1 hop; K=256 -> 87% within 1 hop. maxhop=3, 0% unreachable.

DECISION: the mechanical AND-gate returned STOP because one degree sub-threshold (top5%share 0.281 < pre-registered
0.30) set hub_by_degree=False. This is a threshold-boundary artifact: the CONSTRUCT the gate measures ("clean hub
structure / bottlenecks vs expander-like") is decisively satisfied -- betweenness gini=0.866 (top1% holds 38% of
all betweenness) and degree max/mean=50.7x both reject the expander hypothesis the note warns is vacuous. The STOP
trigger ("no clean bottlenecks / landmarks too far") is absent; landmarks are ~1-hop reachable for the majority.
=> PROCEED to Phase 1. PRIMARY DOCUMENTED RISK carried forward: the reachability tail (13-24% of path nodes still
>1 hop from nearest landmark even at K=256; maxhop=3) -- for those the distant-target pathology can recur in-leg;
and, more fundamentally, "1-hop-reachable to SOME landmark" does not imply the landmark lies on the geodesic
between a given chain's start and its specific goal.

## Arms (paired: identical codes + planted chains + seeds; only the QUERY differs)
- NO_CLEANUP (must-fail control; collapses at reach>=2)
- MEMORYLESS (goal-blind floor; Gate-D repro of fair-test anchor)
- SUPPLIED_WAYPOINT (MM ceiling; Gate-D repro; one-step lookahead A*/UVFA)
- AUTONOMOUS_GREEDY (plain-greedy autonomous, reused VERBATIM; the thing landmark must beat)
- LANDMARK_SEEDED (CG candidate, primary): degree-proxy landmark set (top-K); per query L1 = argmax landmark of
  [cos(start,l)+cos(l,goal)] (ALT triangle midpoint); walk toward L1 via certified goal-conditioned local argmax,
  switch to direct goal-conditioning on G once cos(cur,G) >= cos(cur,L1) or L1 reached. Flat 2-leg skeleton.
- LANDMARK_GOAL_ONLY (secondary, logged not gated): same but L1 = argmax landmark of cos(l,goal) (note's literal default).

## Pre-registered bands (from research note; NOT loosened)
- HARD_PASS_CG_LANDMARK: LANDMARK_SEEDED reach@2 >= 0.40 AND > AUTONOMOUS_GREEDY reach@2 (recovers >=69% of the gap).
- HARD_FAIL_CG_LANDMARK_VACUOUS: LANDMARK_SEEDED reach@2 <= 0.20 (indistinguishable from plain-greedy 0.181).
- MIDDLE_BAND: 0.20 < reach@2 < 0.40.
- Reported (never gated): ratio@2(lm/sup), delta@2(lm-greedy), delta@2(lm-mem), aim_L1_frac, goal-only vs midpoint.
- Anti-saturation gates (must fire, else INCONCLUSIVE): NO_CLEANUP collapses; MEMORYLESS in (0.05,0.95);
  SUPPLIED >= MEMORYLESS + 0.10. Gate-D repro at FULL: mem1~0.453, sup1~0.756, sup2~0.500, auto2~0.181 (tol 0.10).

## Compute architecture
class (c) mixed. Storage SHARDED (per-node codes). Within-hop batched einsum (cuda when available); across-hop
sequential (inherent data dependency). Landmark selection = batched [C,K] cosine matmul. GAMMA=1.5 pre-registered
(= certified GOAL_GAMMA), NOT tuned on real data. K ~ 5% of nodes (Phase-0-informed), NOT tuned to the discriminator.
progress_logging: print_flush_true. final_metrics_atomicity: tmp_replace. cell_chunked: false (few seeds; sharded
per-seed write_partial). except SystemExit: raise before except Exception (no BaseException/bare).

## Self-test (clean-hub planted graph positive control) -- PASS (deterministic; torch seeded)
MEASURED@ smoke/self-test stdout: on a planted graph where chains route THROUGH a per-chain hub (pre-hub nodes
carry a toward-hub channel, hub carries goal signal + high degree, post-hub nodes carry goal signal):
NO_CLEANUP collapses; MEMORYLESS 0.0 (fully aliased); SUPPLIED reach@2=0.544; plain-greedy reach@2=0.0 (fails);
hubs 100% captured as landmarks; LANDMARK_SEEDED reach@2=0.933 (>> greedy, >= 0.70*supplied); arms differ.
=> mechanism CAN fire when the graph HAS clean hub structure => a real-data null is a genuine graph-structure /
signal-weakness result, not a broken mechanism or mis-set gamma.

## SMOKE result (2 seeds, real CN subgraph n=1525, dim=512) -- HARD_FAIL_CG_LANDMARK_VACUOUS
MEASURED@data/exp_grounding_multihop_landmark_routing_v1_smoke/metrics.json:
NO_CLEANUP@2=0.014 (collapses=True) | MEMORYLESS@1=0.499(in_band) @2=0.151 | SUPPLIED@1=0.744 @2=0.499(fires=True) |
AUTONOMOUS_GREEDY@2=0.167 | LANDMARK_SEEDED@2=0.111 | LANDMARK_GOAL_ONLY@2=0.154 |
ratio@2(lm/sup)=0.222, delta@2(lm-greedy)=-0.056, delta@2(lm-mem)=-0.041, aim_L1_frac=0.36.
Anchors reproduce (discriminator valid): sup2=0.499 matches ceiling, auto2=0.167 near 0.181 anchor.
=> LANDMARK routing is BELOW plain-greedy AND below memoryless; BOTH selection variants fail. HARD_FAIL fired
(lm2=0.111 <= 0.20). Smoke did NOT clear => per "multi-seed FULL only on smoke clearance", FULL NOT dispatched.

## FULL profile (declared; NOT dispatched -- smoke HARD_FAIL)
seeds=[7,13,17], n_nodes=5000, code_dim=2048, feat_dim=8192, epochs=140, K=256; overnight_queue/GPU; timeout ~1800s.
Dispatch command (for reference only; recommended AGAINST given smoke HARD_FAIL):
  bash tools/orchestrator/queue_add.sh overnight_queue grounding_multihop_landmark_routing_v1 \
    experiments/exp_grounding_multihop_landmark_routing_v1.py preregs/2026-07-09_landmark-routing.md 1800
