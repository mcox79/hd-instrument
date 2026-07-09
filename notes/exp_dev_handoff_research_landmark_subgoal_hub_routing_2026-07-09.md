# exp_dev hand-off — research: landmark/hub-node subgoal routing for autonomous traversal

**Filed by:** research sub-agent. **Trigger:** `notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md` — the SECOND-stage upgrade explicitly deferred by the prior drill (`notes/research_autonomous_subgoal_derivation_goal_directed_traversal_CG_path_2026-07-09.md`) for exactly this scenario ("if greedy hop-selection HARD-FAILs at longer chain depths"). `grounding_multihop_autonomous_subgoal_greedy_v1` landed MIDDLE_BAND_CG_PARTIAL (reach@2=0.181, inside that drill's own pre-registered HARD-FAIL band of <0.20), so the upgrade is due now. Brain (Balaguer et al. hierarchical subway planning) + graph-science (ALT/hub-labeling/highway-hierarchies/betweenness-subgoal HRL) independently converge on landmark/hub decomposition of long routes as the fix; graph-science also independently confirms the failure mode this fixes (a distant-target similarity signal underdetermining the next real hop) is exactly why production shortest-path engines abandoned plain greedy/Dijkstra in favor of landmark-mediated search.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. This hand-off's Anchor 0 (diagnostic pre-check) requires NO new dispatch — it is pure analysis on the already-built KB graph structure via the existing local-neighborhood-scoping primitive, and should be allowed even if experiments are paused. Anchor 1 (the landmark-routing cell itself) IS pause-gated per standard exp_dev discipline.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHOR + POINTERS + the falsifiable predictions/discriminator from the research note only. exp_dev designs ALL of: exact precompute script, K (landmark count), leg-cap, seed count, threshold implementation detail, queue choice, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered)

1. **Diagnostic pre-check: KB graph degree distribution + nearest-landmark hop-distance (Anchor 0, zero new dispatch, run FIRST)**
   - Anchor pointer: `notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md`, "Cheap decisive test / discriminator" section, "Pre-registered diagnostic gate."
   - Substrate-product reading: before spending a build cycle on landmark-mediated routing, measure (i) the KB graph's degree distribution (heavy-tailed/hub-and-spoke predicts the mechanism helps; near-uniform predicts it won't — this is the graph-science angle's own explicitly-stated failure mode, an expander-like graph with no clean bottlenecks makes the whole technique vacuous) and (ii) the hop-distance from every node to its nearest degree-proxy-selected landmark (if median/tail sits outside the short-range regime that produced the 0.499 supplied-waypoint ceiling, the landmark set is too sparse and needs densifying before the traversal cell runs). Both obtainable from the existing local-neighborhood-scoping primitive alone, no new tooling, no new dispatch.
   - Tier: local/analyzer-only (near-zero compute, one pass over the existing KB graph).
   - Why now: this is the cheapest possible test of whether the mechanism has a chance at all, and should run BEFORE the landmark-routing cell is funded — a favorable pre-check justifies Anchor 1; an unfavorable one (near-uniform degree, sparse landmark coverage) is itself a genuine finding (localizes any subsequent HARD-FAIL to graph structure, not mechanism) that should be reported before building anything.

2. **Landmark-seeded autonomous traversal cell (Anchor 1) — pause-gated, contingent on a favorable Anchor 0 read**
   - Anchor pointer: same research note, "ONE concrete substrate realization" + "Cheap decisive test / discriminator" sections.
   - Substrate-product reading: precompute a landmark set (degree-proxy top-K over the existing local-neighborhood-scoping primitive; escalate to sampled/approximate betweenness only if Anchor 0's diagnostic says degree-proxy is too sparse — both are one-time, offline, built entirely from the existing primitive, no new operator). Per query (current node C, final goal G): apply the ALREADY-CERTIFIED goal-conditioning primitive with the candidate pool restricted to landmarks to pick waypoint L1; walk C->L1 using the supplied-waypoint mechanism VERBATIM (local-neighborhood-scoping + goal-conditioning cosine-argmax) with L1 substituted for the externally-supplied waypoint; on reaching L1's neighborhood, either fall back to direct goal-conditioning on G (if no landmark now beats direct cosine-to-G) or repeat for L2. Build the FLAT, 2-leg-capped version first; do not build recursive multi-level landmark skeletons preemptively.
   - Discriminator (pre-registered, from the research note, bands should not be loosened): HARD-PASS reach@2 >= 0.40 (recovers >=69% of the 0.318 remaining gap to the 0.499 supplied-waypoint ceiling), reproducible across paired seeds, delta-vs-plain-greedy not shrinking with dimension. HARD-FAIL reach@2 <= 0.20 (statistically indistinguishable from the already-measured plain-greedy 0.181 — landmark precompute bought nothing). Middle band (0.20-0.40): diagnose via Anchor 0's two gates before declaring a verdict, mirroring the discipline already applied to the just-landed MIDDLE_BAND_CG_PARTIAL result.
   - Tier: local/CPU smoke first (small matched subgraph, few hundred nodes, 1 seed, degree-proxy landmarks only) before any FULL/GPU dispatch. Multi-seed FULL only on smoke clearance.
   - Why now: closes the exact gap the last verdict left open, using only already-certified primitives (zero new mechanism), with an explicit pre-registered discriminator and an explicit, cheap pre-check to avoid wasting a build cycle if the KB graph structurally can't support it.

3. **Escalation to sampled betweenness centrality (fallback, only if Anchor 1's degree-proxy version HARD-FAILs but Anchor 0's diagnostic was favorable)**
   - Anchor pointer: same research note, "One-time landmark precompute" section, escalation path.
   - Substrate-product reading: if the pre-check said hub structure exists but degree-proxy landmark selection still underperforms, escalate to sampled/approximate betweenness (iterated BFS-style expansion via the existing primitive from random source nodes, tally recurring frontier nodes, take top-K by tally) — implicates landmark SELECTION quality specifically, not the overall mechanism, per the graph-science angle's random-vs-centrality-selection gap finding.
   - Tier: local/CPU, only dispatch if Anchor 1's smoke/FULL result and Anchor 0's diagnostic jointly indicate this specific escalation is warranted (exp_dev's call).
   - Why now: cheap, well-precedented fallback (ALT literature: centrality-based selection much more effective than random/degree-only in some graph regimes) rather than abandoning the mechanism on a first HARD-FAIL if the graph structure itself looked favorable.

---

## Context pointers (file paths, not summaries)

- `notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md` — this drill's full note (HEADLINE, brain + graph-science convergence, substrate realization, discriminator, honest risk, citations, intuitive summary).
- `notes/research_autonomous_subgoal_derivation_goal_directed_traversal_CG_path_2026-07-09.md` — the prior drill that proposed and pre-registered the plain-greedy mechanism just tested, and explicitly deferred landmark precompute to this exact fallback scenario (see its "Cross-thread synthesis" section, final bullet).
- `notes/research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md` — the sibling-test drill diagnosing branch-point/tied-neighbor underdetermination; this drill's graph-science angle independently confirms the SAME mechanism as landmark-distance degeneracy in symmetric graph regions (third independent confirmation of one underlying failure mode — see Cross-thread synthesis).
- Verdict event (already-landed, per status_log): `grounding_multihop_autonomous_subgoal_greedy_v1`, overnight_queue, FULL dim=2048, `MIDDLE_BAND_CG_PARTIAL`, auto_reach2=0.181, ratio2_auto_sup=0.363, delta2_auto_mem=0.060, seeds=3, device=cuda — the anchors (0.121 floor / 0.181 plain-greedy / 0.499 supplied-waypoint ceiling) this hand-off's discriminator is built against.
- `notes/substrate_capability_map.md` — current cap_map; the goal-conditioning / autonomous-traversal cell rows this thread affects.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands are already specified in the research note (0.40 / 0.20); exp_dev may sharpen implementation detail but the bands themselves came from research and should not be loosened.
- Self-test per [[feedback-formula-selftests]].
- Anchor 0 (diagnostic pre-check) requires NO new dispatch — pure analysis on the existing KB graph via the existing primitive; run this FIRST regardless of pause state.
- Anchor 1 (landmark-routing cell) IS pause-gated per standard exp_dev discipline; smoke on CPU/local before any FULL/GPU dispatch; multi-seed FULL only on smoke clearance.
- Anchor 2/escalation (betweenness) is contingent and exp_dev's call, not pre-baked.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact diagnostic-pre-check script, K (landmark count), degree threshold, leg-cap (2 vs 3), seed count, precise threshold implementation (bands pre-specified in the research note; exp_dev implements them), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. If Anchor 0's diagnostic comes back unfavorable (near-uniform degree distribution, no meaningful hub structure), exp_dev's call whether to still run a small smoke-scale Anchor 1 anyway (to empirically confirm the predicted vacuous result, since that's itself informative) or to report the unfavorable pre-check as the deliverable and defer Anchor 1 entirely — that judgment call is exp_dev's, not pre-baked here.

---

## Filed by

Research sub-agent, 2026-07-09, brain-first landmark/hub-routing drill (Director-requested, continuation of the just-landed MIDDLE_BAND_CG_PARTIAL autonomous-traversal verdict). Hand-off ready for exp_dev pickup on next queue-refill or dedicated dispatch cycle.
