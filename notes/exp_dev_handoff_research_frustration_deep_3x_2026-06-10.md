# exp_dev hand-off -- research: frustration resolution deep 3x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_frustration_deep_3x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

The BG-analog mechanism achieves 4% lift on "irreducible" conflicts. Research drill 3x
identifies this as expected from Boltzmann sampling in a shallow frustration basin, NOT a
fundamental ceiling. Ten substrate-native resolution mechanisms are proposed, spanning
stochastic tunneling, symmetry-breaking injection, plan decomposition, meta-cognitive
recursion, dreaming/offline consolidation, attractor surgery, framing transformation,
recursive subgoal, delay resolution, and cultural-convention fallback.

The cheapest decisive test is STOCHASTIC-TUNNELING (E.4): replace energy E(x) with
E_tunnel(x) = 1 - exp(-gamma * E(x)) in the BG sampling step. No new infrastructure.
gamma = 1/(typical barrier height), derivable from existing BG benchmark data.
Expected runtime < 30 min CPU. Pre-reg: HARD-PASS >= 25% escape rate; HARD-FAIL < 10%.

All 10 mechanisms have pre-reg bands in the research note. Priorities below are ordered
by P_deflated x engineering cost (cheapest + highest P first).

---

## Anchor candidates (rank-ordered by P_actionable x engineering cost)

### 1. FRUSTRATION-TUNNEL-BG (HIGHEST PRIORITY -- zero new infrastructure)

Anchor pointer: FRUSTRATION-TUNNEL-BG (new; not yet queued)
Substrate-product reading: Replace E(x) with E_tunnel(x) = 1 - exp(-gamma * E(x)) in
  BG sampling. This flattens shallow barriers without changing the global landscape,
  allowing Boltzmann sampling to escape frustrated basins at lower temperature. The
  gamma parameter is set analytically from the observed 4% escape rate (back-calculate
  the implied barrier height, then set gamma = 1/barrier). Zero new code paths -- only
  the energy function changes in the sampler.
Tier hint: CPU laptop; < 30 min wall; no model loading or training needed
Why-now: Cheapest possible test of the tunnel mechanism. If HARD-PASS (>= 25%), no
  other mechanism is needed for the immediate product milestone. Test this FIRST.

Pre-reg bands (research recommendation):
  HARD-PASS: Frustration escape rate >= 25% vs 4% BG baseline (same benchmark)
  HARD-FAIL: Escape rate < 10% (tunneling not viable; landscape is wide not narrow)
  MID-BAND: 10-24% (viable but combine with E.9 symmetry-breaking for cascade)

### 2. FRUSTRATION-CONTEXT-DISAMBIG (HIGH PRIORITY -- minimal infrastructure)

Anchor pointer: FRUSTRATION-CONTEXT-DISAMBIG (new; not yet queued)
Substrate-product reading: When frustration is detected (top-2 candidate similarity gap
  < delta_thresh), apply context-conditioned symmetry-breaking field:
    x_perturbed = q + epsilon_SB * h_context
  where h_context is derived from the session context hypervector (already computed in
  current architecture for other uses). Then re-run argmax or BG from x_perturbed.
  h_context breaks the Z_2 symmetry of the frustration basin. If the context is aligned
  with the frustration axis, resolution is direct.
Tier hint: CPU laptop; < 1 hr wall; uses existing context vector
Why-now: Algebraically independent from E.4; can be run in parallel or immediately after.
  Also connects to empowerment policy bridge (same context-vector mechanism).

Pre-reg bands (research recommendation):
  HARD-PASS: Resolution rate >= 30% on frustrated queries with context provided
  HARD-FAIL: < 10% (context field orthogonal to frustration -- different mechanism needed)
  MID-BAND: 10-29% (context partially aligned; investigate epsilon_SB sweep)

### 3. FRUSTRATION-PLAN-DECOMP (MEDIUM PRIORITY -- 1-2 day implementation)

Anchor pointer: FRUSTRATION-PLAN-DECOMP (new; not yet queued)
Substrate-product reading: Decompose a multi-constraint frustrated query into a sequence
  of sub-queries, each adding one constraint via binding:
    q_1 = bind(q, R_{c_1}), q_2 = bind(x_1_answer, R_{c_2}), ...
  Each sub-query has a unique attractor (by construction). Requires: (a) constraint
  detection (which dimensions of q carry conflicting constraints), (b) a schedule for
  constraint ordering (hardest constraint first, or easiest first -- both variants should
  be tested). Directly addresses multi-hop retrieval failure (MULTI-HOP REVIVE PRIORITY).
Tier hint: CPU laptop; 1-2 hr wall per sweep; requires constraint decomposition utility

Pre-reg bands (research recommendation):
  HARD-PASS: 3-constraint correctness >= 0.75 vs 0.50 standard retrieval baseline
  HARD-FAIL: < 0.60 (constraints entangled, decomposition does not factor the frustration)
  MID-BAND: 0.60-0.74 (partial -- try 2-constraint version; may still be useful)

### 4. FRUSTRATION-DREAMING (MEDIUM PRIORITY -- offline operation, no latency impact)

Anchor pointer: FRUSTRATION-DREAMING (new; not yet queued)
Substrate-product reading: Implement periodic offline consolidation: after N retrieval
  cycles (or triggered by accumulation of frustrated queries), run one offline pass over
  the frustrated-query buffer using W_sparse (zero W entries < epsilon_sparse = median|W|).
  Conflicted attractors that depend on weak cross-connections are resolved to the strong-
  connection answer. Write results to a consolidated-memory register. During live retrieval,
  check the register first before running full Hopfield iteration.
Tier hint: CPU laptop; offline; < 30 min per consolidation pass
Why-now: Zero product latency impact. Can be run as background maintenance. If HARD-PASS,
  ships as a product "nightly maintenance" feature immediately.

Pre-reg bands (research recommendation):
  HARD-PASS: >= 40% of frustrated queries resolve correctly in offline consolidation pass
  HARD-FAIL: < 15% (frustrated queries also frustrated with sparse W -- weak connections
              not the source, different mechanism needed)

### 5. FRUSTRATION-ATTRACTOR-SURGERY (MEDIUM PRIORITY -- requires labeled frustration pairs)

Anchor pointer: FRUSTRATION-ATTRACTOR-SURGERY (new; not yet queued)
Substrate-product reading: For known frustrated pairs (a_1 correct, a_2 competitor), apply
  targeted W modification to suppress a_2's attractor basin:
    W_update = W - alpha * outer(a_2, a_2)
  with scoped correction to preserve a_2 for other queries. This is a surgical capability
  that requires known ground-truth for the frustrated pair. Useful for high-stakes domains
  where known ambiguities must always resolve to the authoritative answer.
Tier hint: CPU laptop; requires labeled dataset of frustrated pairs; < 1 hr per sweep
Why-now: Highest expected P_deflated for correctness on targeted queries (0.35). If a
  small labeled set of frustrated pairs is available from the BG benchmark, this can be
  tested immediately.

Pre-reg bands (research recommendation):
  HARD-PASS: >= 50% of targeted frustrated pairs resolve correctly; non-targeted recall
              degradation < 5%
  HARD-FAIL: Non-targeted recall degradation > 10% (surgery too broad; scoping failed)

---

## Context pointers (file paths)

- Research note: d:/AI/hd-instrument/notes/research_drill_frustration_deep_3x_2026-06-10.md
- Empowerment bridge (same context-vector mechanism): d:/AI/hd-instrument/notes/research_drill_empowerment_policy_bridge_2x_2026-06-10.md
- Multi-hop revive priority: C:/Users/marsh/.claude/projects/d--AI/memory/project_multihop_revive_priority.md
- Substrate capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Field advisor output: run python tools/orchestrator/research_field_advisor.py from hd-instrument root

---

## Contract section

Research has delivered:
- 5 literature streams (biology, brain, materials, LLM theory, substrate-native)
- 10 substrate-native mechanisms with math and pre-reg bands
- P_deflated estimates (0.20-0.50 after calibration penalty; two-mechanism cascade capped at 0.48)
- Cheap decisive test identified (FRUSTRATION-TUNNEL-BG, < 30 min CPU)
- Cross-thread synthesis to empowerment bridge, multi-hop, free-probability field

exp_dev is responsible for:
- Validating anchor pointers against current queue state
- Designing sweep grids and exact parameter ranges
- Confirming pre-reg bands or tightening them based on substrate specifics
- Queue assignment (CPU laptop vs remote CPU vs remote GPU)
- Post-ship REMOTE VERIFY

---

## Autonomy declaration

exp_dev has full autonomy to:
- Run FRUSTRATION-TUNNEL-BG first (cheapest, highest P_deflated)
- Combine FRUSTRATION-TUNNEL-BG + FRUSTRATION-CONTEXT-DISAMBIG in a single queue item
  (they are independent operations on the same BG step)
- Defer FRUSTRATION-PLAN-DECOMP until multi-hop revive is unblocked
- Skip FRUSTRATION-ATTRACTOR-SURGERY if no labeled frustration pairs are available
- Request Research follow-up on Tracy-Widom / free-probability for analytical gamma
  calculation if FRUSTRATION-TUNNEL-BG scores MID-BAND
