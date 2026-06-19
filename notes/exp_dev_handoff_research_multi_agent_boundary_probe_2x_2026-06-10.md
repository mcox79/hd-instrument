# exp_dev hand-off -- research: multi-agent boundary probe 2x

**Filed-by:** research sub-agent (2026-06-10)
**Trigger:** notes/research_drill_multi_agent_boundary_probe_2x_2026-06-10.md
**Pause state:** dispatch when queue depth permits; all 5 anchors are laptop-CPU testable,
no cloud GPU required, priority MEDIUM (not blocking any current vertical).

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and passes context
pointers. exp_dev reads the research note and designs the actual experiment scripts autonomously.

---

## Anchor candidates (rank-ordered)

### 1. MULTI-AGENT-4: HYBRID-NASH-SUBSTRATE-SOLVER
**Anchor pointer:** research note section 4, anchor 4.
**Substrate-product reading:** validates the "coordination engine Mode 3" framing -- substrate +
classical Nash solver as a complete production multi-agent system. This is the commercially
defensible hybrid claim that the orchestrator's prior retraction was questioning. MULTI-AGENT-4
is the anchor that directly answers the pushback: yes, substrate + solver works.
**Tier hint:** laptop CPU, pure numpy, estimated <5 min wall. No cloud. Fits current queue.
**Why now:** prior drill rated this P_deflated=0.75 (highest of the 5 anchors); it is the
lowest-risk highest-signal anchor in the batch; expected HARD-PASS given PP-39, PP-265, PP-288,
PP-270 all validated. Pre-reg bands: HARD-PASS >= 0.90 Nash outcome; HARD-FAIL when retrieval
is error-free and solver is correct but Nash outcome fails.

### 2. MULTI-AGENT-3: ITERATED-PRISONER-DILEMMA-STRATEGY-LEARNING
**Anchor pointer:** research note section 4, anchor 3.
**Substrate-product reading:** validates substrate AGM belief revision (PP-266/287) as a practical
opponent strategy classifier in repeated games. Directly demonstrates the iterated cooperation
class of coordination (Axelrod). P_deflated=0.65, medium confidence.
**Tier hint:** laptop CPU, <2 min wall. Extends PP-287 depth test to IPD framing.
**Why now:** cheapest anchor, grounded in validated PP-266/287 depth results, natural product demo
(IPD strategy learning is a canonical multi-agent benchmark).

### 3. MULTI-AGENT-5: ADVERSARIAL-MANIPULATION-RESISTANCE-SCALED
**Anchor pointer:** research note section 4, anchor 5.
**Substrate-product reading:** extends PP-39 v331 adversarial sub-property from K=5 m=1 to K=10
m in {1,2,3}. Characterizes the manipulation threshold for production multi-agent enterprise use.
**Tier hint:** laptop CPU, <5 min wall. Extends existing PP-39 multi-agent infrastructure.
**Why now:** PP-39 band-lift requires 4th independent sub-property for next lift (0.70-0.85 ->
0.75-0.90); adversarial scaling characterization is the natural next sub-property. Dual purpose:
cap_map evidence + coordination engine claim validation.

### 4. MULTI-AGENT-1: COMMON-KNOWLEDGE-CONVENTION-FORMATION
**Anchor pointer:** research note section 4, anchor 1 and "Cheap decisive test" section.
**Substrate-product reading:** tests whether PP-265 + PP-285 + PP-288 compose to implement Lewis
convention formation without pre-encoding. This is the novel composition claim (P_deflated=0.52).
High-value if it passes; credible partial-negative expected (composition risk).
**Tier hint:** laptop CPU, <3 min wall. Pure substrate operations, write-read-confirm loop.
**Why now:** the "cheap decisive test" in the research note was designed for this anchor. Low cost
for potentially high cap_map evidence value.

### 5. MULTI-AGENT-2: CAUSAL-COUNTERFACTUAL-OPPONENT-MODELING
**Anchor pointer:** research note section 4, anchor 2.
**Substrate-product reading:** tests PP-270 + PP-291 composition in multi-agent causal inference.
Agent learns causal model of opponent, predicts counterfactual responses. P_deflated=0.60.
**Tier hint:** laptop CPU, <5 min wall. Extends PP-270 + PP-291 tests to multi-agent framing.
**Why now:** causal opponent modeling is the strongest product differentiation claim (no vector
database answers causal queries). If this passes, it is a top-tier product demo.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_multi_agent_boundary_probe_2x_2026-06-10.md
- Prior drill: d:/AI/hd-instrument/notes/research_drill_multi_agent_beyond_context_exchange_2x_2026-06-10.md
- Cap_map (PP-39, PP-250, PP-265, PP-266, PP-270, PP-272, PP-280, PP-285, PP-286, PP-287, PP-288,
  PP-291): d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

Pre-registered bands per anchor are in research note section 4 (HARD-PASS / HARD-FAIL per anchor).
exp_dev uses those bands verbatim. If a band is unclear, resolve by reading the research note --
do not re-derive bands from first principles.

Multi-seed discipline: MULTI-AGENT-4 and MULTI-AGENT-5 should run 3+ seeds (they use stochastic
elements). MULTI-AGENT-1, MULTI-AGENT-2, MULTI-AGENT-3 can smoke at n=1 seed first.

Queue routing: all 5 anchors are laptop CPU (no GPU, no cloud). Route to local_cpu_queue or
remote_cpu_queue per current queue depth.

## Autonomy declaration

exp_dev decides: script design, exact implementation of each anchor, seed count, queue routing,
smoke vs full decision, and verdict envelope. Research specifies the problem; exp_dev owns
implementation and execution.
