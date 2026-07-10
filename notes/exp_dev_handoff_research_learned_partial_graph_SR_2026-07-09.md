# exp_dev hand-off — research: learned / partial-graph successor-representation reachability (CG vs MM discriminator)

**Filed by:** research sub-agent. **Trigger:** `notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09.md` — the VET-settled correction to the just-certified SR-reachability cell (HARD_PASS reach@2=0.434, but a reciprocal-necessity self-test proved the routing is closed-form graph search over a fully-known transition matrix T, with the learned-code term aliasable-to-useless with zero effect). This hand-off proposes the follow-up that makes the reachability signal genuinely LEARNED and tests it against structure the substrate was never directly shown, which is the field's own standard design for separating reasoning (CG) from search (MM).

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. Anchor 0 (code-space-vs-hop-distance correlation diagnostic) requires NO new dispatch — pure analysis on the already-built KB graph + already-learned substrate codes, and should be allowed even if experiments are paused. Anchor 1 (the learned/held-out SR cell itself) IS pause-gated per standard exp_dev discipline.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHOR + POINTERS + the falsifiable predictions/discriminator from the research note only. exp_dev designs ALL of: exact partial-T sampling procedure, held-out subgraph size/selection, k for code-space smoothing, seed count, threshold implementation detail, queue choice, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered)

1. **Diagnostic pre-check: code-space-similarity vs. graph-hop-distance correlation (Anchor 0, zero new dispatch, run FIRST)**
   - Anchor pointer: `notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09.md`, "Honest risk" section, risk 1.
   - Substrate-product reading: before spending a build cycle on learned/held-out SR, measure whether the substrate's own learned vector codes for graph-neighboring nodes are actually more similar (cosine/dot-product) than codes for random node pairs at the same or greater hop-distance. If code-space similarity does NOT correlate with graph-topological proximity on the already-visible portion of the KB graph, the entire code-space-smoothing mechanism (step 2 of the substrate realization) is structurally vacuous before any held-out test is even run — this is the fourth independent surfacing of the "does this substrate have exploitable local structure" question (after degree-distribution, community-structure, and mixing-time framings in the two sibling SR/landmark drills), now applied to code space specifically.
   - Tier: local/analyzer-only (near-zero compute, one pass over already-computed codes + already-known graph structure).
   - Why now: this is the cheapest possible test of whether the mechanism has a chance at all, and should run BEFORE the learned/held-out cell is funded. A favorable read (real correlation) justifies Anchor 1; an unfavorable read (near-zero correlation) is itself a genuine, reportable finding that localizes any subsequent HARD-FAIL to code-space structure rather than mechanism design, and should be reported honestly before building anything.

2. **Learned/code-space SR with held-out-subgraph discriminator (Anchor 1) — pause-gated, contingent on a favorable Anchor 0 read**
   - Anchor pointer: same research note, "ONE concrete substrate realization" + "Decisive discriminator" sections.
   - Substrate-product reading: build T from a SAMPLED/visible portion of the KB graph only (withhold a disjoint subgraph at construction time); score reachability to nodes inside the visible portion via the existing resolvent/TD mechanism (reusing the just-certified cell's machinery), and score reachability to WITHHELD nodes via a similarity-weighted average over each withheld node's k-nearest neighbors in the substrate's own learned code space (not graph space) among already-scored nodes. Route via the SAME argmax hop-selection loop already certified. Run TWO conditions side by side: full-graph (already-certified numbers as reference) and held-out (this cell's new contribution). CRITICAL construction constraint: the learned codes used for code-space smoothing must not have been formed with any access (direct or indirect) to the withheld subgraph — a genuine train/test split, not just a withheld T.
   - Discriminator (pre-registered, from the research note, bands should not be loosened): HARD-PASS held-out reach@2 >= 0.32 (>=~80% retention of the certified full-graph reach@2=0.434) AND the SAME reciprocal-necessity self-test (alias the learned-code term to useless) run specifically on the held-out condition shows a COLLAPSE toward the memoryless floor (0.121) -- confirming the codes are doing real generalizing work, not incidental leakage. HARD-FAIL: held-out reach@2 <= 0.20 (collapse toward memoryless floor -- still search, just missing rows it can't fill in) OR held-out reach@2 is UNCHANGED under code-aliasing (meaning even this "learned" version isn't actually using the codes -- some other artifact/leakage is doing the work). Middle band (0.20-0.32): diagnose via Anchor 0's correlation check before declaring a verdict.
   - Tier: local/CPU smoke first (small matched subgraph, few hundred nodes, 1 seed, small held-out fraction) before any FULL/GPU dispatch. Multi-seed FULL only on smoke clearance.
   - Why now: this is the discriminator that actually tests whether "autonomous traversal" is reasoning (CG) rather than closed-form search over a known map (MM) — the open question explicitly left by the just-certified cell's own self-test. Zero new retrieval primitive; reuses the certified resolvent machinery plus one new code-space-smoothing scoring function.

3. **Held-out-split leakage audit (fallback / pre-req check, run alongside or immediately before Anchor 1)**
   - Anchor pointer: same research note, "Honest risk" section, risk 3.
   - Substrate-product reading: verify the learned codes used for smoothing genuinely never saw the withheld subgraph during their own formation (no co-training exposure, no indirect leakage path). If the substrate's codes were formed with full-graph exposure (as is normal for many embedding methods), a naive held-out test would be a false positive (memorization masquerading as generalization) — exactly the WN18/FB15k inverse-relation-leakage cautionary tale the ML lit-scan flagged. This is exp_dev's call on how to construct a genuinely clean split given how the substrate's codes are actually trained.
   - Tier: design/audit step, near-zero compute, should gate Anchor 1's result interpretation regardless of when it's run.
   - Why now: without this check, a HARD-PASS on Anchor 1 would be uninterpretable — could be genuine generalization or could be leakage. Cheap to verify, expensive to discover after the fact.

---

## Context pointers (file paths, not summaries)

- `notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09.md` — this drill's full note (HEADLINE, brain + ML + substrate-realization convergence, substrate realization, decisive discriminator, honest risk, citations, intuitive summary).
- `notes/research_successor_representation_reachability_autonomous_traversal_2026-07-09.md` — the sibling drill whose certified cell this hand-off directly follows up on; contains the resolvent-construction mechanics (truncated Neumann series / sparse solve) this proposal reuses for the visible-T portion.
- `notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md` and `notes/research_autonomous_subgoal_derivation_goal_directed_traversal_CG_path_2026-07-09.md` — the two prior drills in this thread (landmark/hub, greedy-cosine); the graph-structure risk (expander vs. community) flagged in both recurs here in code-space form (Anchor 0).
- Verdict event (already-landed, per status_log): the just-certified SR-reachability cell — HARD_PASS, reach@2=0.434 (0.869x supplied ceiling 0.499 or similar reference number), beats greedy 0.181 and landmark 0.111; reciprocal-necessity self-test showed aliasing the learned-code term to useless leaves routing at 1.0 (no learned-code contribution) — the anchors this hand-off's discriminator (0.32 HARD-PASS / 0.20 HARD-FAIL, and the code-aliasing collapse requirement) are built against.
- `notes/substrate_capability_map.md` — current cap_map; the goal-conditioning / autonomous-traversal / CG-vs-MM cell rows this thread affects.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands are already specified in the research note (0.32 / 0.20, plus the code-aliasing collapse condition); exp_dev may sharpen implementation detail but the bands themselves came from research and should not be loosened.
- Self-test per [[feedback-formula-selftests]].
- Anchor 0 (code-space correlation diagnostic) and Anchor 3 (leakage audit) require NO new dispatch — pure analysis; run these FIRST regardless of pause state.
- Anchor 1 (learned/held-out SR cell) IS pause-gated per standard exp_dev discipline; smoke on CPU/local before any FULL/GPU dispatch; multi-seed FULL only on smoke clearance.
- The reciprocal-necessity self-test (code-aliasing on the held-out condition specifically) is MANDATORY, not optional — a HARD-PASS on reach@2 alone without this confirmatory self-test would repeat exactly the interpretive mistake this hand-off exists to correct (the prior cell's headline metric looked good and the self-test is what revealed it was search, not reasoning).
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact partial-T sampling/withholding procedure, held-out subgraph size and selection method, k (code-space neighbor count for smoothing), seed count, precise threshold implementation (bands pre-specified in the research note; exp_dev implements them), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, and how to construct a genuinely leak-free held-out split given how the substrate's codes are actually trained (Anchor 3's judgment call). If Anchor 0's diagnostic comes back unfavorable (no meaningful code-space/hop-distance correlation), exp_dev's call whether to still run a small smoke-scale Anchor 1 anyway (to empirically confirm the predicted vacuous result, since that's itself informative) or to report the unfavorable pre-check as the deliverable and defer Anchor 1 entirely.

---

## Filed by

Research sub-agent, 2026-07-09, brain-first learned/partial-graph SR drill (Director-requested continuation of the just-VET-settled SR-reachability HARD_PASS, specifically targeting its own self-test's exposure that the mechanism was closed-form search, not learned reasoning). Hand-off ready for exp_dev pickup on next queue-refill or dedicated dispatch cycle.
