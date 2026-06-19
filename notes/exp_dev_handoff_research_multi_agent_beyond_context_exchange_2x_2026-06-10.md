# exp_dev hand-off -- research: multi-agent reasoning beyond context exchange (2x drill)

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research 2x drill on multi-agent reasoning -- correction of overclaim that "context exchange solves coordination." Five engineering anchors identified covering ToM-grounded coordination, Schelling-point lookup, active inference opponent modeling, belief revision per agent, and hybrid substrate+classical-GT. See source note: `notes/research_drill_multi_agent_beyond_context_exchange_2x_2026-06-10.md`.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. TOM-DEPTH-K-COORDINATION -- ToM depth-3 coordination game validation

- **Anchor pointer:** Research note 2026-06-10, Section 6, Anchor 1. Construct coordination games where optimal action is derivable by level-3 cognitive hierarchy lookup; encode agent A's nested beliefs about agent B using PP-250 substrate structure; retrieve and map to action; compare to CH-model ground truth.
- **Substrate-product reading:** Validates whether PP-250 depth-3 ToM retrieval translates to coordination improvement in an actual two-agent game scenario. HARD-PASS >= 0.90 on level-3-solvable games; HARD-FAIL < 0.70. Honest test: deliberately includes games that REQUIRE Nash computation (not level-3-solvable) to verify the system fails gracefully on out-of-scope problems.
- **Tier hint:** Local CPU smoke. Pure retrieval test over PP-250 substrate; no GPU needed. Cheap decisive test per research note.
- **Why now:** Directly addresses the overclaim correction. This is the cheapest test that draws the honest boundary between what substrate ToM can do vs what it cannot.

### 2. SCHELLING-POINT-VIA-CULTURAL-SCHEMA -- convention-mediated cross-agent coordination

- **Anchor pointer:** Research note 2026-06-10, Section 6, Anchor 2. Encode N conventions in PP-265 scripts; two simulated agents independently query same substrate for expected action; verify cross-agent agreement on pre-encoded Schelling points.
- **Substrate-product reading:** HARD-PASS >= 0.95 cross-agent agreement on pre-encoded conventions. HARD-FAIL < 0.80. Tests substrate-mediated coordination on the honest scope: pre-specified conventions, not emergent ones.
- **Tier hint:** Local CPU. Can ride with Anchor 1 using same experiment infrastructure. Very cheap.
- **Why now:** PP-265 validated single-agent convention lookup; the cross-agent framing (two agents querying independently and converging on same action) has not been explicitly tested. Low risk, high product value.

### 3. ACTIVE-INFERENCE-OVER-OPPONENT-STATE -- opponent modeling via PP-285 multi-step active inference

- **Anchor pointer:** Research note 2026-06-10, Section 6, Anchor 3. Agent A uses PP-285 multi-step active inference to build generative model of agent B's policy from k=10 observed actions; predict B's next action on held-out set.
- **Substrate-product reading:** HARD-PASS prediction accuracy >= 0.75 after k=10 observations. HARD-FAIL <= 0.55 (near-chance). Non-stationarity test: B changes policy mid-sequence; measure accuracy degradation. P_deflated = 0.45 per research note (harder than single-agent active inference; includes policy inference not just pattern convergence).
- **Tier hint:** Local CPU. Likely 5-10 min wall. May benefit from 3-seed sweep for stochastic behavior. Still sub-GPU.
- **Why now:** PP-285 validated convergence on generating-distribution prediction; opponent policy modeling from observations is the natural multi-agent extension and has not been explicitly exercised. Strongest substrate-native multi-agent capability candidate.

### 4. BELIEF-REVISION-PER-AGENT -- AGM update pipeline for opponent model correction

- **Anchor pointer:** Research note 2026-06-10, Section 6, Anchor 4. Agent A holds a model of agent B encoded in substrate; B acts unexpectedly; A performs AGM belief revision (PP-287) on its model of B; evaluate whether revised model predicts B's subsequent actions better than prior model within 3 revision steps.
- **Substrate-product reading:** HARD-PASS: A's post-revision predictive accuracy > pre-revision accuracy within 3 steps. HARD-FAIL: belief revision oscillates or diverges over 3 steps. Tests PP-266+PP-287 in the multi-agent framing (revising an agent's model of another agent, not just updating world facts).
- **Tier hint:** Local CPU. Can sequence after Anchor 3 using same agent-B policy infrastructure. Moderate compute.
- **Why now:** PP-287 validated AGM revision depth up to mean 1.6 supersessions/key on single-agent fact updates. The multi-agent framing (revising beliefs about another agent's policy) is a structurally different use case that has not been tested.

### 5. MIXED-SUBSTRATE-CLASSICAL-GT -- hybrid substrate state layer + Nash solver integration

- **Anchor pointer:** Research note 2026-06-10, Section 6, Anchor 5. Substrate holds game state (beliefs, histories, payoff matrix encoded in HD structure); classical Nash solver (Lemke-Howson for bimatrix) reads substrate-retrieved state and outputs equilibrium; verify combined system achieves Nash outcome on games where equilibrium is unique.
- **Substrate-product reading:** HARD-PASS: Nash outcome achieved >= 0.90 of games; substrate retrieval latency < 1ms per query. HARD-FAIL: system fails on games where unique Nash equilibrium is not derivable from ToM lookup (intentional -- should fail gracefully and route to solver). This is the hybrid architecture validation.
- **Tier hint:** Local CPU. Plumbing test more than compute test. Lemke-Howson runs in microseconds on small bimatrix games.
- **Why now:** Establishes the correct product architecture claim: substrate as state layer, classical GT as solver. Lower urgency than Anchors 1-4 since it is a plumbing integration, not a capability boundary test.

---

## Context pointers

- Source research note: `notes/research_drill_multi_agent_beyond_context_exchange_2x_2026-06-10.md`
- Prior multi-agent infrastructure handoff (infrastructure primitives, now routed): `notes/routed_completed/exp_dev_handoff_research_multiagent_coordination_substrate_2026-06-01.md`
- Cap_map PP rows: PP-250 (ToM depth-3), PP-265 (cultural conventions), PP-266+PP-287 (AGM belief revision), PP-272+PP-285 (active inference), PP-280 (paraconsistent multi-context), PP-230 (multi-tenant isolation)
- Nash equilibrium PPAD-completeness: Daskalakis-Goldberg-Papadimitriou 2006, arxiv available
- Cognitive hierarchy model: Camerer-Ho-Chong 2004, Quarterly Journal of Economics
- MADDPG CTDE architecture: Lowe et al. 2017, NeurIPS; QMIX: Rashid et al. 2018, ICML
- Schelling focal points: Schelling 1960; Lewis conventions 1969

---

## Contract

exp_dev is authorized to:
- Design and queue Anchor 1 (TOM-DEPTH-K-COORDINATION) as local CPU smoke
- Design and queue Anchor 2 (SCHELLING-POINT) riding the same experiment infrastructure as Anchor 1
- Design and queue Anchor 3 (ACTIVE-INFERENCE-OPPONENT) as a separate local CPU anchor with seed sweep
- Design and queue Anchor 4 (BELIEF-REVISION-PER-AGENT) sequenced after Anchor 3
- Design and queue Anchor 5 (MIXED-SUBSTRATE-CLASSICAL-GT) as lowest-priority local CPU anchor
- Promote to remote CPU if multi-seed sweeps require > 30 min wall

exp_dev is NOT authorized to:
- Claim substrate solves general multi-agent coordination or Nash equilibrium -- these anchors test the CONSTRAINED subset only
- Modify cap_map rows without orchestrator approval
- Pre-specify HP/MID/HF numerical bounds (exp_dev derives from research note predictions + formula-selftests)
- Frame results as "multi-agent coordination demo" -- frame as capability boundary characterization

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: all anchor specifications (N, M, K, seeds, thresholds, queue routing, anchor names, ETAs) are exp_dev's design decisions. This hand-off provides the WHAT and WHY; exp_dev provides the HOW.
