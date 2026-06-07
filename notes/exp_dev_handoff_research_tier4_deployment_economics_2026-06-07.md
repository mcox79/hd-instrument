# exp_dev hand-off -- research: Tier 4 deployment economics 2x

**Filed-by:** research sub-agent (Sonnet), 2026-06-07
**Trigger:** Cycle 162 Pattern B production validation (16 bytes/fact, 100K facts confirmed);
  2x economic drill on Tier 4 deployment cost story.
**Research note path:** d:/AI/hd-instrument/notes/research_drill_tier4_deployment_economics_2x_2026-06-07.md

**Per [[feedback-no-experiment-design-in-prompts]]:** This file contains anchor candidates and
context pointers only. exp_dev decides all parameters, thresholds, scripts, and queue routing.

---

## Pause state block

Check d:/AI/hd-instrument/data/orchestrator_paused.flag before acting on this handoff.
If paused, queue these anchors to pending list only; do not ship.

---

## Anchor candidates (rank-ordered by research finding priority)

### Anchor 1 (HIGHEST priority): Production query throughput benchmark
**What:** Measure actual token throughput (tokens/second) of substrate retrieval + Llama-8B
  inference co-located on single GPU node at production concurrency (50-100 concurrent queries).
**Why now:** The entire economic model hinges on GPU utilization assumption (~70%, ~10K tokens/s
  on A100 for 8B model). If actual throughput at concurrency is 3K-5K tokens/s instead of 10K,
  per-query cost doubles. This is the single biggest unknown in the model.
**Tier hint:** Tier 3/4 (requires real GPU run on runner).
**Substrate-product reading:** Validates or invalidates Scenario A cost model. If throughput
  at production concurrency is confirmed >7K tokens/s, the $0.005-0.009/query prediction holds.

### Anchor 2: Context inflation measurement
**What:** For 100 representative production queries, measure actual prompt token count with
  substrate retrieval vs naive document injection RAG. Compute inflation ratio.
**Why now:** The research model projects 2,500 tokens/query (2-3x lean assumption). If real
  production context is 800-1,200 tokens, the substrate cost advantage narrows. If it is
  4,000-6,000 tokens, advantage widens significantly.
**Tier hint:** CPU-runnable (token counting, no model inference needed for measurement).
**Substrate-product reading:** Determines which column of the cross-over table is applicable
  to real customer workloads. Changes the break-even volume estimate by 2-5x.

### Anchor 3: Llama-1B vs Llama-8B quality delta on substrate-guided retrieval
**What:** Compare retrieval quality (recall@K, MRR) using Llama-1B-BASE vs Llama-3.1-8B
  for substrate-guided KB queries. Production architecture prefers 1B but economic model
  assumed 8B.
**Why now:** If Llama-1B is sufficient for substrate-guided retrieval (which the production
  architecture notes suggest), inference costs drop 4-8x vs 8B. This would change break-even
  from ~600K queries/month to ~150K-200K queries/month for general enterprise.
**Tier hint:** CPU-runnable smoke; GPU for full quality eval.
**Substrate-product reading:** If 1B is sufficient, the target market expands significantly
  downmarket. Directly impacts product pricing and customer acquisition strategy.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_tier4_deployment_economics_2x_2026-06-07.md
- Production architecture lock: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- Phase 2 chains gold: d:/AI/hd-instrument/memory/phase2_5x_chains_gold_findings_2026-06-07.md
- Cap map (current): d:/AI/hd-instrument/data/cap_map.md (check current version)

---

## Contract

exp_dev delivers: anchors shipped to appropriate queue, pre-reg with HP/MID/HF bands,
REMOTE VERIFY confirmed, status_log entry written.

## Autonomy declaration

exp_dev decides: anchor names, N values, smoke vs full designation, queue routing (GPU vs CPU),
timeout estimates, pre-reg threshold bands, script implementation. Orchestrator does not
specify any of these.
