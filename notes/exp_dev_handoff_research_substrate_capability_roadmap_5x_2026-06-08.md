# exp_dev hand-off -- research: substrate capability roadmap 5x

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_substrate_capability_roadmap_5x_2026-06-08.md
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

Substrate has PP-1 through PP-178 validated (cycles 175-194). The comprehensive
capability roadmap identifies 60+ capability candidates across 8 levels. The top-10
ranked by leverage x feasibility x demo impact are mostly SPRINT-class (1-5 days) because
the required algebraic primitives are already HP. The highest-value next experiments
are presentation/assembly layer anchors that turn existing HP primitives into user-visible
product features.

The five anchor candidates below are ranked by P_actionable x engineering cost x demo
impact for the v1 demo build (4-6 week timeline, Audit Week ongoing).

---

## Anchor Candidates (rank-ordered)

### 1. HALLUCINATION-DETECTOR-V1 (HIGHEST PRIORITY)

Anchor pointer: HALLUCINATION-DETECTOR-V1 (new; not yet queued)
Substrate-product reading: Substrate cross-checks LLM-generated factual claims against
  stored facts using PP-107 abstention-ROC + PP-163 negation + PP-174 AND-NOT.
  Catches factual errors without external API calls. Categorical differentiator.
Tier hint: CPU laptop; ~2-3 hours wall; no cloud; no new substrate changes
Why-now: All required primitives (PP-107, PP-163, PP-174) are HP. This is a 2-3 day
  assembly task. Hallucination detection is the #1 enterprise LLM trust concern as of
  mid-2026. Earliest possible green = immediate demo-day feature.

Pre-reg guidance (exp_dev refines):
  HARD-PASS: precision >= 0.75 AND recall >= 0.70 on incorrect claims; FPR <= 0.15
  MID: precision 0.55-0.75
  HARD-FAIL: precision < 0.50

Dependencies: PP-107 (HP), PP-163 (HP), PP-174 (HP), Wikipedia substrate shard.

---

### 2. RETRIEVAL-EXPLANATION-V1

Anchor pointer: RETRIEVAL-EXPLANATION-V1 (new; not yet queued)
Substrate-product reading: Expose the K-hop path as a natural-language chain of reasoning
  ("Retrieved via Entity_A -> relation_B -> Entity_C"). Highest trust-to-cost ratio.
Tier hint: CPU laptop; ~1-2 hours wall; no cloud
Why-now: PP-119 KG-K-hop-QA (HP) + PP-166 khop-audit-replay (HP). Path is already
  logged in chain retrieval. This is a 1-day presentation wrapper. No algorithmic work.

Pre-reg guidance:
  HARD-PASS: path correctness >= 0.85 on n=50 multi-hop queries; human NL rating >= 3.5/5
  MID: path correctness 0.70-0.85
  HARD-FAIL: path correctness < 0.50

---

### 3. CLIP-MULTIMODAL-V1

Anchor pointer: CLIP-MULTIMODAL-V1 (new; not yet queued)
Substrate-product reading: Ingest CLIP image embeddings into substrate using existing
  PCA whitening pipeline. Cross-modal retrieval: text query -> image fact. Zero architecture
  change needed.
Tier hint: CPU laptop; ~2-3 hours wall; requires CLIP model download (~330MB)
Why-now: PCA whitening validated at cycle 157. CLIP is publicly available. If green,
  substrate becomes multimodal with no engineering investment beyond assembly.

Pre-reg guidance:
  HARD-PASS: recall@1 >= 0.60 AND recall@5 >= 0.80 on n=200 cross-modal queries
  MID: recall@1 0.40-0.60
  HARD-FAIL: recall@1 < 0.25

---

### 4. EPISTEMIC-IDK-V1

Anchor pointer: EPISTEMIC-IDK-V1 (new; not yet queued)
Substrate-product reading: Substrate distinguishes absent-entity (epistemic uncertainty)
  from conflicting-facts (aleatoric uncertainty). Returns "not in KB" vs "conflicting
  information found" vs "here is the answer." Transparent AI for enterprise governance.
Tier hint: CPU laptop; ~1-2 hours wall
Why-now: PP-107 abstention-ROC (HP) + PP-125 two-stage-disambiguation (HP). Falls out
  of existing primitives with a classification wrapper.

Pre-reg guidance:
  HARD-PASS: category (B absent) IDK rate >= 0.75; category (C conflict) detection >= 0.65;
    category (A present) answer rate >= 0.85
  HARD-FAIL: category (B) IDK rate < 0.40

---

### 5. TABULAR-INGEST-V1

Anchor pointer: TABULAR-INGEST-V1 (new; not yet queued)
Substrate-product reading: Ingest a standard CSV (SEC EDGAR or company data) as triples
  using PP-113 numeric-payload + PP-159 COUNT-filter. Answer point-lookup and range queries.
  Opens the enterprise structured data category.
Tier hint: CPU laptop; ~2-3 hours wall; free public data (SEC EDGAR)
Why-now: PP-113 (HP) + PP-159 (HP) + existing ingest pipeline. ETL wrapper only.
  Directly relevant to v1 demo corporate intelligence overlay.

Pre-reg guidance:
  HARD-PASS: recall@1 >= 0.85 on point-lookup; range filter >= 0.80; 3-hop join correct
  MID: point-lookup 0.70-0.85
  HARD-FAIL: point-lookup < 0.50

---

## Context pointers (file paths)

- Research note: notes/research_drill_substrate_capability_roadmap_5x_2026-06-08.md
- Capability map history: notes/substrate_capability_map_history.md (tail = current state)
- PP-107 (abstention-ROC): cycle 180 -- see history.md v506
- PP-113 (numeric-payload): cycle 192 -- see history.md v518
- PP-119 (KG-K-hop-QA): cycle 181 -- see history.md v507
- PP-159 (COUNT-filter): cycle 193 -- see history.md v519
- PP-162 (CRDT): cycle 162/163 -- see history.md v482/v483
- PP-163 (negation): cycle 192 -- see history.md v518
- PP-166 (khop-audit-replay): cycle 166 -- see history.md v487
- PP-174 (AND-NOT): cycle 193 -- see history.md v519
- v1 demo brief: notes/testbed_post_compaction_brief_2026-06-08_v1_demo_audit_week.md

---

## Contract

exp_dev owns anchor design, sweep grids, thresholds, and queue placement.
Research has provided candidate anchors and pre-reg guidance only.
All five anchors are SPRINT-class (< 3 days each). Parallelizable: anchors 1 and 2
can run concurrently on CPU; anchors 3, 4, 5 can follow immediately.
No cloud dispatch needed for any of these five anchors.

---

## Autonomy declaration

exp_dev is authorized to:
- Design the exact anchor implementations from the pointer descriptions above
- Adjust pre-reg bands based on observed smoke results
- Queue all five anchors in the overnight_queue (CPU lane)
- Skip any anchor whose dependencies turn out not to be met (check PP rows first)

exp_dev is NOT authorized to:
- Modify the substrate architecture
- Add new PP rows without passing the standard HONEST-count gate
- Dispatch cloud experiments for these five anchors (all are CPU-viable)
