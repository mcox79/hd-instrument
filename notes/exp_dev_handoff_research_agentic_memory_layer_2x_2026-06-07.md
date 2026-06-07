# exp_dev hand-off -- research: Agentic Memory Layer Level-2 Drill

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_agentic_memory_layer_2x_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
WHY they matter. exp_dev designs the actual experiment (sweep grid, thresholds, queue
choice, timeout). No numerical grids or threshold formulas are pre-committed here.

---

## Pause state block

This handoff was written while experiments may be running. exp_dev should check
data/orchestrator_paused.flag before dispatching any anchors.

---

## Context

The research drill established 5 architectural integration patterns for substrate as an
agentic memory layer, with 5 empirical cells ordered by cost/importance. The EU AI Act
Article 12 (enforcement August 2026) creates a hard regulatory pull for fact-atom-level
audit that no current framework (Mem0/Letta/LangGraph) satisfies. Substrate's Merkle-cert
retrieval + RSA accumulator is structurally the solution.

All 5 cells are CPU-feasible (Cells 1-4) or GPU-small (Cell 5). Total cost estimate <$5.
Cell 1 is the necessary precondition for Cells 2-5 (Pattern A retrieval must validate first).

---

## Anchor candidates (rank-ordered by urgency + cheapness)

### Anchor 1 (TIER: CHEAP CPU SMOKE -- highest priority)
WHY NOW: Cell 1 (Pattern A) is the precondition gate for all other agentic memory patterns.
If substrate AUC@10 >= 0.85 on agent-observation retrieval at <1ms vs FAISS ~20ms, the entire
agentic memory layer architecture is validated at the retrieval layer. If HF (AUC < 0.70),
all other patterns (B-E) are retrieval-limited and need redesign before proceeding.
Cost is <$1 and <30 min wall. This is the highest-leverage cell in the entire agentic cluster.

ANCHOR POINTER: Pattern A agentic observation write/retrieval benchmark.
N=4096, M=500 synthetic agent observations, 1000 semantic queries.
Compare substrate AUC@10 + retrieval latency vs FAISS flat index with sentence-transformer baseline.

SUBSTRATE-PRODUCT READING: If PASS (AUC >= 0.85 at <1ms) -- substrate is viable as drop-in
agent memory layer; proceed to Cells 2-3. If FAIL (AUC < 0.70) -- retrieval architecture needs
re-examination before any agentic positioning claim.

TIER HINT: remote_cpu_queue. No GPU needed (numpy cosine retrieval only for substrate side;
sentence-transformer for baseline can run CPU). <30 min wall. ~$0.50.

---

### Anchor 2 (TIER: CPU PROBE -- Tool Call Grounding KF-1)
WHY NOW: Cell 3 (Pattern C) is the compliance moat anchor. KF-1 argument grounding cert is
the specific mechanism that satisfies EU AI Act Article 12 "precise attribution of decision
to memory atom" at tool-call time. If AUC >= 0.88 with FPR < 0.10, the compliance positioning
is empirically grounded. This directly enables healthcare + legal enterprise sales. FPR > 0.25
would kill deployment viability (too many false-blocks on valid calls).

ANCHOR POINTER: KF-1 gate on synthetic tool call batch.
N=4096, M=300 grounded facts in substrate; 500 tool calls (300 grounded args, 200 hallucinated).
Measure AUC + FPR of KF-1 cosine threshold on grounded/ungrounded classification.

SUBSTRATE-PRODUCT READING: If PASS (AUC >= 0.88, FPR < 0.10) -- KF-1 gate is production-viable
as compliance primitive; ship as tool-call grounding API. If FAIL (FPR > 0.25) -- threshold
sensitivity means KF-1 is too noisy; needs calibration before compliance positioning.

TIER HINT: remote_cpu_queue. <15 min wall. ~$0.20.

---

### Anchor 3 (TIER: CPU PROBE -- Multi-Agent CRDT Consistency)
WHY NOW: Cell 4 (Pattern D) validates the CRDT-analog claim -- the NEW synthesis from this
drill. If 3 concurrent agents can write to W_shared and retrieve each other's observations
at AUC >= 0.82 while maintaining private isolation >= 0.99, substrate is deployable as a
native-CRDT multi-agent memory with no central coordinator. This is a genuine architectural
differentiator vs all current frameworks.

ANCHOR POINTER: 3-agent concurrent write to W_shared; query shared + private shard separation.
N=4096; each of 3 agents writes M=100 observations; after all writes: 500 queries across
all 3 observation sets; private shard test via per-agent XOR key.

SUBSTRATE-PRODUCT READING: If PASS -- CRDT framing is valid; position Pattern D as "first
native-CRDT agentic memory." If private isolation rate < 0.95 -- XOR shard isolation is
insufficient at this N; investigate whether larger N restores isolation.

TIER HINT: remote_cpu_queue. <20 min wall. ~$0.25.

---

### Anchor 4 (TIER: CPU PROBE -- K-Hop Plan Verification)
WHY NOW: Cell 2 (Pattern B) is the multi-step reasoning differentiator. K-hop plan verification
at K=5 with TPR >= 0.80 and FPR < 0.15 establishes that substrate can serve as a grounded
planning oracle -- the mechanism that makes multi-step agent plans verifiably safe. This directly
maps onto the Cognition Labs / GitHub Copilot enterprise use case. Requires Cell 1 PASS first
(substrate retrieval must be validated before plan-level verification).

ANCHOR POINTER: K-hop plan grounding benchmark.
100 synthetic 10-step plans (30% with ungrounded steps); K=5 hops at N=4096.
Measure TPR + FPR for detecting ungrounded plan steps vs LLM baseline.

SUBSTRATE-PRODUCT READING: If TPR >= 0.80, FPR < 0.15 -- K-hop plan verification is viable;
position as "first algebraically verifiable multi-step planning oracle." If TPR < 0.55 --
K-hop is insufficient for plan grounding at K=5; investigate K scaling.

TIER HINT: remote_cpu_queue. <20 min wall. ~$0.30 + ~$2 LLM API.
DEPENDENCY: run after Cell 1 (Anchor 1) confirms AUC >= 0.85.

---

### Anchor 5 (TIER: GPU PROBE -- Long-Running Task 50-Step Retention)
WHY NOW: Cell 5 (Pattern E) is the headline use case for enterprise SWE agents. If substrate
accuracy >= 0.80 on early-step facts at step 50 vs pure-context < 0.40, the "week-5 as well
as day-1" claim is empirically grounded. This enables the Cognition Labs pitch directly.
Requires GPU (Llama-3.2-1B encoder for observation writes). Sequence after Cells 1-3 pass.

ANCHOR POINTER: 50-step synthetic task; write O_t at each step via Llama-3.2-1B encoder;
query substrate at step 50 for Q&A on steps 1-10 facts; compare vs pure-context baseline.

SUBSTRATE-PRODUCT READING: If PASS (>= 0.80 vs < 0.40) -- "multi-week agent task" positioning
is empirically grounded; ship Cell 5 result as flagship demo. If FAIL (< 0.55) -- dynamic
write-during-active-task mode degrades retrieval; investigate whether full-context baseline
also degrades or stays stable.

TIER HINT: remote_gpu_queue. ~1 hour wall. ~$3.
DEPENDENCY: run after Cells 1 + 2 (retrieval + KF-1 validated).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_agentic_memory_layer_2x_2026-06-07.md
- Prior agentic memory note: d:/AI/hd-instrument/notes/anthropic_memory_competitive_and_agentic_ai_architecture_v278_2026-05-29.md
- Capability implication (System 1 + operating modes): d:/AI/hd-instrument/notes/capability_implication_consolidated_substrate_2026-06-04_end_of_day.md
- Hallucination detection (KF-1) architecture: see active cap_map row KF-1
- Multi-agent CRDT framing: see Part VII.1 of research note above

---

## Contract section

exp_dev is authorized to:
- Design and ship Anchors 1-5 above in dependency order
- Choose sweep grids, threshold tunings, and exact protocols at its discretion
- Route Anchors 1-4 to remote_cpu_queue and Anchor 5 to remote_gpu_queue (per role contract)
- Smoke-gate each anchor before full dispatch

exp_dev is NOT authorized to:
- Modify the substrate architecture (W matrix structure, encoder, write rule, audit chain)
- Make product positioning decisions based on results (route verdicts to orchestrator)
- Run cloud instances without separate authorization (all 5 cells are local/remote-runner feasible)

---

## Autonomy declaration

exp_dev has full autonomy on: experiment design, sweep parameters, queue selection, smoke
gate criteria, and sequencing within the dependency order stated above.

Orchestrator/verdict_handler owns: cap_map updates, product positioning decisions, any
strategy changes triggered by results.
