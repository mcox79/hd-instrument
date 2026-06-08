# exp_dev hand-off -- research: streaming + DP composition DEEPER 5x

Filed-by: research sub-agent
Trigger: notes/research_drill_field_streaming_DP_composition_DEEPER_5x_2026-06-07.md
Date: 2026-06-07

## Pause state block
This file is written unconditionally. exp_dev MUST check data/orchestrator_paused.flag before dispatching to queue. If paused, hold this handoff until resume.

## Per [[feedback-no-experiment-design-in-prompts]]
This file provides TASK + WHY + CONTRACT + AUTONOMY pointers only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA. No inline experiment design below.

---

## Anchor candidates (rank-ordered)

### Rank 1: SVT epsilon savings vs basic composition
- Anchor pointer: Implement Sparse Vector Technique for simulated entity frequency threshold
  alerts on a Zipf-1.0 stream of 10M items with k=100 true heavy hitters; compare total
  epsilon consumed under SVT vs basic composition for T threshold crossings.
- Substrate-product reading: If SVT gives >= 50x epsilon savings for sparse threshold events
  (k=100 crossings in 10M stream), this is an immediate drop-in improvement for substrate's
  dashboard alert layer with zero accuracy cost. Direct enabler for "continuous DP dashboard"
  product claim. CPU only, 20 min wall.
- Tier hint: CPU probe, laptop. pip install no dependencies beyond numpy.
- Why-now: Cheapest highest-signal anchor in this batch. Zero GPU dependency. SVT is
  algorithmically trivial (10-20 lines); measurement is the work.

### Rank 2: Streaming betweenness centrality smoke test for bridge entity discovery
- Anchor pointer: Generate a random entity graph (n=1000 nodes, m=5000 edges, 10 planted
  bridge entities with high betweenness); stream edge insertions; maintain approximate
  betweenness via k=100 random BFS samples; measure top-10 betweenness recall vs planted
  bridges.
- Substrate-product reading: This is the multi-hop revival anchor. The prior drill
  established bridge entity discovery as the multi-hop bottleneck. Streaming betweenness
  centrality (Riondato-Upfal 2016) provides a 5MB-space incremental solution. If recall
  >= 70% at k=100 BFS samples, the approach is worth implementing at full scale (k=400
  for n=10000 entities). If recall < 70%, BFS sample count needs to be increased, which
  drives up the space budget estimate.
- Tier hint: CPU probe, laptop. NetworkX available. Wall time ~10 min.
- Why-now: Multi-hop revival is flagged as "extremely important" in project memory. This
  is the cheapest feasibility check for the streaming betweenness path.

### Rank 3: Mergeable Misra-Gries accuracy and space overhead
- Anchor pointer: Run Agarwal 2013 mergeable MG on two independent client streams (5M
  items each, Zipf s=1.0); merge after each round of 1M items; compare merged heavy-hitter
  F-score and space overhead vs single-pass ground truth.
- Substrate-product reading: The current MG implementation is not mergeable; federated
  clients cannot combine their heavy-hitter sets without extra passes. Agarwal 2013
  mergeable MG requires 2x space but enables direct federation. If F-score >= 0.90 at 2x
  space, this is a drop-in upgrade to the federated substrate layer. HARD-PASS F-score >=
  0.90; HARD-FAIL if space overhead > 3x (would undermine the engineering tradeoff).
- Tier hint: CPU probe, laptop. Pure Python. ~15 min wall.
- Why-now: Directly blocks federated substrate deployment; current MG cannot federate.

### Rank 4: Smooth Binary Mechanism epsilon scaling vs basic composition
- Anchor pointer: Implement the Smooth Binary Mechanism binary tree structure for a running
  count; simulate T=10,000 releases; compare privacy budget consumed (epsilon_total) under
  the Smooth Binary Mechanism vs basic composition at the same per-release epsilon.
- Substrate-product reading: The research note predicts 285x epsilon savings (log^1.5(10000)
  ~ 350 vs T=10,000). If confirmed, continuous DP histogram dashboard (1 update per second,
  all day) becomes feasible within epsilon_total = 1.0 for a full deployment day. Without
  this, the dashboard would exhaust the privacy budget in minutes. HARD-PASS: epsilon_total
  under SBM <= 500 for T=10,000 releases; HARD-FAIL: >= 5,000.
- Tier hint: CPU probe, laptop. Pure Python binary tree. ~15 min wall.
- Why-now: Directly enables the continuous DP dashboard product feature without which the
  "DP-by-construction" pitch breaks at real-time dashboard update rates.

### Rank 5: DP-CMS adversarial injection resistance
- Anchor pointer: Implement CMS with Laplace noise on cell outputs (epsilon_dp = 1.0);
  simulate an adaptive adversary that observes CMS output and injects targeted items to
  corrupt the frequency estimate for a target entity; measure corruption success rate with
  and without DP noise.
- Substrate-product reading: The research note claims DP-CMS thwarts adversarial injection
  because the adversary cannot lock onto threshold values. If corruption success rate drops
  by >= 50% with DP noise vs without, this confirms the Ben-Eliezer theorem applies in
  practice for the substrate's CMS structure. Product claim: "adversarially robust frequency
  tracking by construction." HARD-PASS: adversary success rate reduction >= 50% at epsilon=1.0
  and adversary controlling 20% of stream; HARD-FAIL if reduction < 10%.
- Tier hint: CPU probe, laptop. ~20 min wall.
- Why-now: Lower priority than Ranks 1-4 since the Ben-Eliezer theorem is well-established;
  this is a demo anchor rather than a research-blocking check. Queue after Ranks 1-3 confirm.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_field_streaming_DP_composition_DEEPER_5x_2026-06-07.md
- Prior streaming 5x drill: d:/AI/hd-instrument/notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md
- Prior DP 5x drill: d:/AI/hd-instrument/notes/research_drill_field_differential_privacy_5x_2026-06-07.md
- Prior federated 2x drill: d:/AI/hd-instrument/notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
- DP 5x exp_dev handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_field_differential_privacy_5x_2026-06-07.md
- Streaming 5x exp_dev handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_field_streaming_algorithms_5x_2026-06-07.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev is autonomous over: anchor naming, sweep grids, threshold formulas, queue assignment
(overnight_queue vs remote_cpu_queue vs local), ETA, order within tiers.

exp_dev is NOT autonomous over: dispatching cloud GPU experiments without explicit authorization,
modifying cap_map rows, writing strategy notes, interpreting verdicts (verdict_handler's lane).

## Autonomy declaration

Research has provided task + why + context pointers. exp_dev executes within its role contract.
All anchors in this handoff are CPU probes; no GPU authorization required. Each anchor is
independently runnable; no dependency ordering imposed. exp_dev may re-order within tiers.
