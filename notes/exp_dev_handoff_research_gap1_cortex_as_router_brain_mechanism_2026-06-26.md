# exp_dev hand-off -- research: GAP 1 cortex-as-router (brain-mechanism drill)

filed-by: research (Opus 4.7 1M)
date: 2026-06-26
trigger: USER in-thread deep drill on Gap 1 routing -- HOW cortex provides destination hints + can substrate implement the same to break 0.66 routing ceiling
pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS to substrate-feasible mechanisms; exp_dev autonomously designs the experiment per anchor + verify-the-referent.

---

## Trigger (cite source)

`notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md`

Headline: 0.66 routing ceiling is a SINGLE-PATHWAY ceiling, not a substrate-physics ceiling. Brain solves it by routing via SEPARATE PATHWAY (mPFC schema-bias from query) that bypasses the noise-collapsed retrieval state. Substrate analog: closed-form R_schema query -> partition router (uses kv_learned_projection precedent at 0.827 chain-grade).

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (Rank 1): substrate_gap1_query_to_partition_router_v1_META_M7

- **Anchor pointer:** Cand 1 in research note Section 3 + Section 5 Rank 1
- **Substrate-product reading:** "Substrate retrieves multi-hop facts with schema-based query routing -- a separate pathway from query to partition (analogous to brain's mPFC-mediated retrieval); breaks the in-pathway noise ceiling"
- **Tier hint:** chain-grade-eligible if HP (HARD_PASS arm >= 0.80 AND lift over bidir >= 0.10); removes Cell B v2's BIAS-P scope flag
- **Why now:** cheapest decisive test of the brain-architecture insight; either outcome (HP or HF) is decisive; ~1.5-2 hr local_cpu single cell
- **P_deflated:** 0.55
- **Substrate-feasibility:** HIGH (kv_learned_projection precedent at 0.827 chain-grade-passed 2026-06-20)
- **Mechanism class:** closed-form pseudoinverse (no backprop, no gradient descent)
- **4 arms:** REPRODUCE_POINTER_CHAIN_V2_5HOP (META_M7 rail) / PART_ORACLE_5HOP (control) / PART_QUERY_TO_ROUTER_5HOP / PART_BIDIR_AS_ROUTER_5HOP

### ANCHOR 2 (Rank 2): substrate_gap1_two_stage_R_schema_plus_bidir_v1

- **Anchor pointer:** Cand 6 in research note Section 3 + Section 5 Rank 2
- **Substrate-product reading:** "Substrate routes via hierarchical cascade -- query-side schema-bias narrows search space; bidirectional collision confirms within candidate partitions; matches brain mPFC-CA3 two-stage retrieval architecture"
- **Tier hint:** chain-grade-eligible if HP_COMPOSED (>= 0.90 AND lift over MAX(R_schema, bidir) >= 0.05)
- **Why now:** GATED on Anchor 1 HP OR Anchor 1 PARTIAL with HP_QUERY in [0.70, 0.80]
- **P_deflated:** 0.40
- **Substrate-feasibility:** HIGH (downstream of Anchor 1)
- **Mechanism class:** composition of closed-form R_schema (Stage 1) + bidir-collide (Stage 2)

### ANCHOR 3 (Rank 3): substrate_gap1_route_by_gap3_schema_v1

- **Anchor pointer:** Section 4 composition with Gap 3 + Section 5 Rank 3
- **Substrate-product reading:** "Substrate retrieves like the brain -- query enters semantic hub (Modern Hopfield prototypes from Gap 3), hub identifies type, type biases destination region (Gap 1 R_schema), retrieval completes in biased subnetwork"
- **Tier hint:** highest brain-fidelity if HP (>= 0.85 AND within 0.10 of PART_ORACLE 0.955)
- **Why now:** GATED on Gap 3 Modern Hopfield HP AND Anchor 1 HP; downstream of two prior cells
- **P_deflated:** 0.40 (gated)
- **Substrate-feasibility:** MEDIUM (depends on Gap 3 categories aligning with Gap 1 partitions)
- **Mechanism class:** full ATL-mPFC-HPC cascade in substrate primitives

---

## Context pointers (file paths, not summaries)

- `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` -- THIS drill (mechanism, candidates, predictions)
- `notes/research_gap1_routing_bidirectional_as_router_2026-06-26.md` -- prior in-pathway drill (bidir-collide, fly-LSH-router)
- `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` -- Modern Hopfield prototype attractors (Gap 3 in queue)
- `data/substrate_index/atoms.jsonl` -- search for `kv_learned_projection` (chain-grade 0.827; 2026-06-20)
- Cell B v2 metrics.json -- PART_ORACLE 0.955 reference
- Cell C v2 metrics.json -- BIDIR_MEET_MID 0.62 + mean_midpoint_cosine 0.0000 (key probe)
- `hdlab/iterative_attractor.py` -- existing cleanup primitive (Anchor 3 reuses)
- `hdlab/multi_hop.py` -- existing per-hop W primitive (all anchors reuse)
- META_M7 REPRODUCE_PV2 band [0.08, 0.25] -- pointer-chain v2 reference rail

---

## Contract

- ANCHOR 1 first; ~1.5-2 hr local_cpu single 4-arm cell
- META_M7 rail MANDATORY (REPRODUCE_POINTER_CHAIN_V2_5HOP arm, band [0.08, 0.25])
- BIAS-Q guard at 1.000 (from Cell B v2 v2 design)
- BIAS-P flag fix: verdict_msg must EXPLICITLY state which arm removes BIAS-P
- Cone-preservation guard: measure cone-cosine of query vs R_schema @ query; flag CONE_ROTATION_RISK if rotation > 0.10 cosine
- Train/test discipline: R_schema fit on 80% chains; HP evaluation on 20% held-out; train >> test by > 0.10 flags overfit
- Cell-author smoke first (verify R_schema fit converges < 10s; train top1 >= 0.85)
- Fix #17 strict runtime measurement
- Pre-reg per-arm thresholds before dispatch per [[feedback-experiment-bias-master-checklist]]

---

## Autonomy declaration

exp_dev designs the cell autonomously per anchor pointer. Specifically:
- Decide whether to ship as single 4-arm cell or split into 2 cells
- Decide V_C, N_DIM, depth, n_seeds, V_C/N_PARTS ratio (Cell B v2 envelope is the baseline; deviate only with stated reason)
- Decide whether to dispatch local_cpu or remote_cpu (numpy-bound; local is fine)
- Decide whether ridge regularization for R_schema fit (recommended; lambda from training-set cross-validation)
- Decide whether to include extra ARM_PART_NONLINEAR_ROUTER (small MLP) as a stretch arm if compute budget allows

Research deliverable is the mechanism + candidate ranking + HP/HF thresholds. exp_dev owns experiment-design freedom per [[feedback-no-experiment-design-in-prompts]].

---

End of hand-off.
