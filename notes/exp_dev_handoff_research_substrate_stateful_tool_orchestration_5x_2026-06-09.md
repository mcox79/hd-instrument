# exp_dev hand-off -- research: substrate stateful memory + tool orchestration

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_substrate_stateful_tool_orchestration_5x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by integration-criticality)

### 1. STATEFUL-A1 -- Session-start memory retrieval benchmark (HIGHEST PRIORITY)
Anchor pointer: STATEFUL-A1 (new; not yet queued)
Substrate-product reading: validates the critical path for cross-session statefulness; hybrid recency+similarity retrieval at N=1000 atoms per user; if recall@10 < 0.80 or latency > 500ms, the statefulness integration story fails before any product engineering begins
Tier hint: CPU; <30 min wall; N=1000 atoms
Why-now: this is the single gate that must pass before any downstream session-persistence work is justified; it tests PP-195 in the agent-memory integration context, not just the substrate-physics context

### 2. STATEFUL-A2 -- Intent classifier + cascade router smoke test (HIGHEST PRIORITY)
Anchor pointer: STATEFUL-A2 (new; not yet queued)
Substrate-product reading: 100-query benchmark across 6 intent classes {REMEMBER, FORGET, MATH_COMPUTE, WEB_SEARCH, LLM_GENERATE, RETRIEVE}; validates PP-198 + PP-123 as the routing primitives for substrate-as-orchestrator architecture; if macro-F1 < 0.80, the orchestrator design must be reconsidered before tool dispatch is integrated
Tier hint: CPU; <1 hr wall
Why-now: RouteLLM (ICLR 2025) validated 85% cost reduction at 95% quality with a lightweight classifier router; PP-198+123 are the substrate equivalent; they need a calibrated benchmark before tool dispatch integration

### 3. STATEFUL-A3 -- PP-104 exact erasure end-to-end in agent-memory context (HIGH PRIORITY)
Anchor pointer: STATEFUL-A3 (new; not yet queued)
Substrate-product reading: write 1000 atoms for a user; issue exact erasure; verify zero residual atoms AND zero cross-tenant leakage AND cryptographic proof chain; validates GDPR compliance in the agent-memory integration context (distinct from prior substrate-physics tests)
Tier hint: CPU; <30 min wall
Why-now: GDPR exact erasure is a v1 product blocker; OWASP LLM08:2025 names vector embedding non-deletion as a top-10 LLM security risk; PP-104 is the differentiating answer; it must be tested end-to-end in the agent-memory context

### 4. STATEFUL-A4 -- Sleep-defrag consolidation benchmark with agent-memory load (HIGH PRIORITY)
Anchor pointer: STATEFUL-A4 (new; not yet queued)
Substrate-product reading: simulate 50 sessions each writing 20 atoms; run PP-141/142 sleep-defrag with the concrete replay algorithm (re-insert with refreshed timestamp + confidence boost); measure consolidation ratio, retrieval precision before/after, and wall time; validates that defrag is safe to run in production without degrading retrieval
Tier hint: CPU; <1 hr wall
Why-now: memory bloat is the dominant failure mode in long-running agents (60-70% of raw tokens are noise per 2025 lit); defrag is the substrate answer; the replay algorithm (re-insert + confidence boost) is not yet specified in PP documentation -- this anchor validates the algorithm

### 5. STATEFUL-A5 -- Bitemporal AS-OF query benchmark (HIGH PRIORITY)
Anchor pointer: STATEFUL-A5 (new; not yet queued)
Substrate-product reading: load 10k atoms with timestamps spanning 90 days; issue 100 AS-OF queries at random past timestamps; measures whether the strongest substrate differentiator for conversational memory (AS-OF temporal queries) is empirically reliable and fast enough for production
Tier hint: CPU; <30 min wall
Why-now: AS-OF is structurally impossible in flat-vector stores (Mem0, Chroma, Pinecone); this is the cleanest v1 demo differentiator; it must be benchmarked to be credibly positioned

### 6. STATEFUL-A6 -- PII pre-write scrubber integration (MEDIUM PRIORITY)
Anchor pointer: STATEFUL-A6 (new; not yet queued)
Substrate-product reading: route 500 synthetic PII-containing strings through a pre-write scrubber (spaCy NER or equivalent); measures PII recall, false positive rate, and throughput; this is a mandatory compliance filter -- OWASP LLM08:2025 shows 40% of PII in embeddings is recoverable via inversion attack
Tier hint: CPU; <2 hr wall
Why-now: compliance requirement for any demo with real user data; 1-day integration task; OWASP risk makes this non-optional

### 7. STATEFUL-A7 -- Multi-tool composition latency end-to-end (MEDIUM PRIORITY)
Anchor pointer: STATEFUL-A7 (new; not yet queued)
Substrate-product reading: 3-step tool chain (substrate retrieve -> Python compute -> LLM generate); measures end-to-end latency and LLM-avoidance rate; the LLM-avoidance rate is the primary operational cost lever -- if substrate retrieval answers 40%+ of queries without LLM, cost drops proportionally
Tier hint: CPU for retrieve+compute; GPU or API credit for LLM calls; <2 hr wall
Why-now: establishes the empirical baseline for the substrate-as-orchestrator cost argument before any product marketing claims are made

---

## Context Pointers

Research note (primary): d:/AI/hd-instrument/notes/research_drill_substrate_stateful_tool_orchestration_5x_2026-06-09.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
PP-195 multi-turn state: substrate cap row
PP-104 exact erasure: substrate cap row
PP-184 Merkle audit: substrate cap row
PP-141/142 sleep-defrag: substrate cap row
PP-198 intent classifier: substrate cap row
PP-123 cascade router: substrate cap row
PP-101 cross-tenant isolation: substrate cap row
Prior handoffs: scan notes/exp_dev_handoff_*.md sorted by mtime for conflicting dispatches

---

## Contract

- All 7 anchors are CPU-runnable except partial GPU/API for anchor 7
- HARD-PASS/HARD-FAIL bands are specified in the research note for each anchor
- Anchors 1+2 are the cheap decisive test; run them first before anchors 3-7
- PII scrubber (anchor 6) is a compliance requirement; do not skip regardless of queue pressure

---

## Autonomy declaration

exp_dev designs the actual sweep grids, threshold values, queue assignment, and run ordering autonomously. This file provides strategic rationale and pointers only. Do not treat the anchor descriptions as implementation specs.
