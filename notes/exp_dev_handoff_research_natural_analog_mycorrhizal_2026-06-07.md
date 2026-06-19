# exp_dev hand-off -- research: natural analog mycorrhizal forest networks 5x deep drill

**Filed:** 2026-06-07 by research sub-agent (mycorrhizal network analog drill, series 4 of 5)

**Trigger:** Research delivery d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md

**Pause state:** check data/orchestrator_paused.flag before dispatching any queue-adding actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered by P_deflated x implementation cost)

### Anchor 1: Load-gradient shard routing (drought redistribution analog)
- Anchor pointer: Extension 4 in d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: shards expose real-time load metrics; routing layer uses load gradient to direct queries to under-loaded shards; self-organizing load balancing without central controller; exactly parallels mycorrhizal network's passive redistribution of water to drought-stressed trees via concentration gradients
- Tier hint: Tier C (local; routing change only, no GPU required; ~1-2 weeks)
- Why now: P_deflated=0.65 (highest of batch); purely infrastructure; no new math; no Pythia pre-test required; directly implementable; reduces operational cost without changing customer-facing behavior

### Anchor 2: Hub-weighted customer initialization (mother-tree warm-start)
- Anchor pointer: Extension 1 in d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: new customer onboarding uses DP-noised copy of top-k hub customer routing patterns as initialization rather than random initialization; directly parallels seedling growth benefit from mother tree mycorrhizal connections; Pythia-160M pre-test required: measure hit rate at N=0 with vs without warm-start; if >15% lift, proceed to engineering
- Tier hint: Tier B (remote CPU for at-scale test; local for 2-hour smoke)
- Why now: P_deflated=0.60; builds on existing DP histogram aggregation from cycles 170-171; pre-test is cheap (2 hours, $0 cloud cost); this is a product differentiator for onboarding pitch ("your substrate improves the moment you join the federation")

### Anchor 3: Mycorrhizal-type diversity preservation
- Anchor pointer: Extension 5 in d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: maintain diversity metric across customer KB profiles (KB density, domain coverage, binding age distribution); if diversity drops below threshold, apply diversity-preserving routing policy rather than normalizing customer KBs to homogeneous profile; Sachsenmaier 2024 is direct lit support (mixed-mycorrhizal-type stands only showed overyielding drought resilience)
- Tier hint: Tier C (local; metadata + routing; ~1 week)
- Why now: P_deflated=0.55; complements Anchor 1 (load routing) and Anchor 2 (hub initialization) by preserving the network diversity that makes hub-mediated routing valuable; low implementation risk

### Anchor 4: Cross-customer adversarial alert propagation (defense signaling analog)
- Anchor pointer: Extension 2 in d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: when customer A detects a high-confidence adversarial pattern, emit a DP-protected alert to the federated layer encoding contradiction type + domain sketch (NOT specific binding content); receiving customers lower contradiction threshold in flagged domain for 24 hours; implements cross-customer herd immunity with privacy; directly parallels JA defense signal propagation through AM fungal networks
- Tier hint: Tier B (remote CPU; 1-2 weeks; Pythia-160M pre-test required)
- Why now: P_deflated=0.50; builds directly on adversarial detection from cycle 167 + DP framework from cycles 170-171; pre-test is 3 hours; commercially strongest single feature in this batch ("your substrate warns you about adversarial patterns other customers have already seen")

### Anchor 5: LLM cheating detection via adversarial detector reuse (sanctions analog)
- Anchor pointer: Extension 3 in d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md, Section Level 4; Grasso 2025 (New Phytologist, doi: 10.1111/nph.70540) is the direct lit basis for detector reuse pattern
- Substrate-product reading: pipe LLM output through the existing adversarial contradiction detector before returning to user; LLM output treated as candidate insertion; contradictions with high-confidence bindings flagged and annotated; track per-LLM hallucination rate over time; routing layer preferentially uses higher-trust LLMs for factual queries; reuses existing adversarial detector without separate mechanism
- Tier hint: Tier B (remote CPU + LLM API calls; 2-3 weeks; Pythia-160M pre-test required)
- Why now: P_deflated=0.50; non-obvious insight from drill: reusing the adversarial detector for LLM quality monitoring is architecturally elegant and requires no new infrastructure; pre-test (2 hours, 50 known-false LLM outputs) confirms whether existing detector is sensitive enough before any engineering commitment

### Anchor 6: Federated fragmentation threshold monitoring
- Anchor pointer: Extension 5.2 in d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md, Section Level 5; lit basis: PMC6288094 (power laws and critical fragmentation in global forests)
- Substrate-product reading: pre-compute the percolation threshold for the substrate federated network (minimum fraction of participating customers needed to maintain giant connected component); build a health check that alerts when federation participation drops below threshold; addresses the non-obvious risk that gradual customer churn causes catastrophic collapse of federated benefit at threshold crossing, not gradual degradation
- Tier hint: Tier C (local; observability/monitoring; ~1 week; pure theory + observability, no Pythia pre-test needed)
- Why now: P_deflated=0.45; purely defensive infrastructure; percolation theory gives the mathematical framework directly; low engineering cost; high operational value if customer churn ever approaches threshold

---

## Context pointers (file paths)

- Research note (full drill): d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md
- Prior analog drill 1 (hippocampal): d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
- Prior analog drill 2 (swarm intelligence): d:/AI/hd-instrument/notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
- Prior analog drill 3 (immune system): d:/AI/hd-instrument/notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md
- Federated substrate cycle context: data/orchestrator_status_log.jsonl (cycles 170, 171)
- Adversarial detection context: data/orchestrator_status_log.jsonl (cycle 167)
- Handoff template reference: d:/AI/hd-instrument/notes/exp_dev_handoff_research_natural_analog_immune_system_2026-06-07.md
- Cap map (current state): d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract section

exp_dev picks which anchors to dispatch, in what order, with what parameters. This hand-off names anchors and pointers only.

Recommended sequencing:
- Anchors 1 + 3 first (load routing + diversity preservation): purely infrastructure, Tier C, no pre-tests required, no dependencies on other anchors in this batch.
- Anchor 2 second (hub initialization): 2-hour Pythia-160M pre-test required before committing to full engineering; if HARD-FAIL (<3% hit-rate lift), drop anchor without loss; if HARD-PASS (>15% lift), this becomes the highest-priority onboarding feature.
- Anchors 4 + 5 third: both require pre-tests; both build on adversarial detection infrastructure (cycle 167); Anchor 4 (alert propagation) before Anchor 5 (LLM cheating detection) because Anchor 4 establishes the propagation primitive that Anchor 5 can reuse.
- Anchor 6 last: purely observability/monitoring; no dependencies; can run in parallel with any other anchor.

Pre-test discipline: per feedback-drill-pretest-required, Anchors 2, 4, and 5 each require a Pythia-160M scale smoke before engineering authorization. Do not skip pre-tests for these three.

Privacy gate: Anchors 2 and 4 both involve cross-customer signal transfer. Privacy audit required (DP noise level sufficient to prevent customer re-identification via the warm-start or alert signal). Escalate to orchestrator if privacy audit reveals risk before dispatching these anchors at production scale.

## Autonomy declaration

exp_dev has full autonomy to:
- Select any subset of the above anchors for the current cycle
- Design all parameters (N, M, thresholds, seed counts, queue routing)
- Reorder anchors within the constraints of the sequencing notes above
- Reject any anchor with a local reason not visible to research
- Add complementary smoke anchors at exp_dev discretion

exp_dev does NOT have autonomy to:
- Override the pre-test requirement for Anchors 2, 4, and 5
- Skip the privacy audit for Anchors 2 and 4 before production-scale dispatch
- Modify the federated layer DP noise level without orchestrator sign-off
