# exp_dev hand-off -- research: LLM capability separation and substrate coupling

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_llm_capability_separation_substrate_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale only. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

User asked: have teams worked to extract just the language capabilities from LLMs before,
using our substrate for knowledge/math/logic? Research confirms: yes, this architectural
pattern (LLM = language + meta-reasoning; external backend = knowledge + logic + math) is
well-explored in the literature. The novel contribution is the substrate's specific backend
properties (multi-hop algebraic, counterfactual, bitemporal, GDPR-erase, sub-ms at 100M+)
-- the combination is not replicated anywhere.

Research identified 4 architectural recipes ranked by feasibility:
- Recipe 6.1 (pure tool-use, no architecture surgery): HIGHEST confidence, v1-ready
- Recipe 6.2 (distillation from frontier teacher): v2 R&D path
- Recipe 6.3 (cross-attention adapter, KBLaM-style): v2 R&D path
- Recipe 6.4 (surgical FFN replacement): P_deflated=0.12, defer

The v1 demo BUILD PLAN already uses Recipe 6.1 (gpt-4o-mini + substrate tool calls). This
handoff targets the LOCAL model path: can a 3B-7B model on the 4060 Ti provide
acceptable language quality while routing all knowledge/math/logic to substrate?

All 5 anchors below are CPU/local-GPU only. No cloud dispatch.

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. LLM-substrate routing smoke test at 3B (HIGHEST PRIORITY, run first)

Anchor pointer: LLM-ROUTING-T1 (new; not yet queued)
Substrate-product reading: Determines whether a 3B-class model can correctly identify
  which parts of a query require substrate lookup vs language-only generation at zero-shot.
  If yes, no fine-tuning needed for basic routing; if no, instruction tuning is required
  before further testing at this scale.
Tier hint: Laptop CPU/GPU; ~1-2 hours wall; no cloud
Why-now: Pre-test gate for all downstream 3B routing work; cheapest possible signal

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: >= 70% correct routing at zero-shot across 50 structured queries
             spanning factual, multi-hop, arithmetic, temporal, counterfactual types
  HARD-FAIL: < 40% correct routing at zero-shot
             (requires instruction tuning before any further testing at this size)
  MID-BAND: 40-70% correct routing (instruction tuning will likely close the gap)

Inputs required: Qwen-2.5-3B or Phi-3-mini loaded locally; 50 query test set covering 5
  query types (10 each); hand-scored routing ground truth; prompt template defining
  substrate tool schema.

---

### 2. Qwen-2.5-7B Q4 VRAM fit + latency test on 4060 Ti

Anchor pointer: LLM-VRAM-T2 (new; not yet queued)
Substrate-product reading: Validates practical feasibility of the 7B local architecture.
  4060 Ti has 8 GB VRAM; Qwen-2.5-7B Q4 requires ~5 GB; substrate KV cache requires
  ~1-2 GB at demo scale. If total <= 7.5 GB, the local demo architecture is viable.
Tier hint: Local 4060 Ti; ~30 min wall
Why-now: Must confirm before committing to 7B-based demo architecture; low-cost test

Pre-reg bands:
  HARD-PASS: Peak VRAM <= 7.5 GB co-resident; generation latency <= 10s/query at 7B Q4
  HARD-FAIL: Peak VRAM > 8 GB OR latency > 30s/query (forces downgrade to 3B or API-only)
  MID-BAND: 7.5-8 GB VRAM (quantize further or reduce substrate cache size)

Inputs required: Qwen-2.5-7B Q4 from HuggingFace hub; substrate KV cache from PP-135
  implementation; GPU VRAM monitor during inference.

---

### 3. Substrate API schema + zero-shot function call formatting test

Anchor pointer: LLM-SCHEMA-T3 (new; not yet queued)
Substrate-product reading: Validates that the substrate API JSON schema is clean enough
  for frontier models to use without fine-tuning. If gpt-4o-mini correctly formats
  substrate calls at >= 85%, the schema is production-ready and v1 demo can ship
  without any LLM training.
Tier hint: API cost ~$0.50; 1 hour
Why-now: Low-cost gate for v1 demo readiness; schema design is a prerequisite for
  any instruction-tuning dataset generation

Pre-reg bands:
  HARD-PASS: >= 85% correctly formatted calls (all required fields; valid types; correct
             entity names) on 20 test queries across all 5 query types
  HARD-FAIL: < 60% correct formatting (API schema has systematic ambiguities; redesign)
  MID-BAND: 60-85% correct formatting (specific query types have issues; targeted schema
             improvements needed)

Inputs required: Defined substrate API JSON schema (entity_lookup, multi_hop_traverse,
  temporal_asof, counterfactual_do, arithmetic_dispatch); 20 test queries with ground truth
  correct calls; gpt-4o-mini API access.

---

### 4. Substrate-KV (PP-135 pattern) scale-up from Pythia-1.4B to Qwen-2.5-3B

Anchor pointer: LLM-SUBSTRATEKV-T4 (new; not yet queued)
Substrate-product reading: PP-135 (substrate-KV) is validated on Pythia-1.4B. KBLaM
  (ICLR 2025) validates the pattern at 8B. This anchor closes the empirical gap at 3B
  with a stronger base model. If substrate-KV recall@10 meets or exceeds standard RAG
  at 3B scale, the adapter path becomes a concrete v2 candidate.
Tier hint: Local 4060 Ti; 2-4 hours; uses PP-135 implementation + Qwen-2.5-3B
Why-now: Closes empirical gap between PP-135 (Pythia) and KBLaM (8B); v2 anchor
  planning gate

Pre-reg bands:
  HARD-PASS: Substrate-KV recall@10 >= standard FAISS RAG recall@10 on same KB
             (1K-fact probe set from existing substrate KB)
  HARD-FAIL: Substrate-KV recall@10 < 60% while RAG achieves >= 70% (adapter fails
             to generalize from Pythia encoding to Qwen encoding)
  MID-BAND: Substrate-KV within 10% of RAG (acceptable; adapter needs tuning)

Inputs required: PP-135 substrate-KV implementation; Qwen-2.5-3B; existing 1K-fact
  substrate KB probe set; FAISS baseline from existing testbed.

---

### 5. Instruction-tuning dataset quality gate (1K examples)

Anchor pointer: LLM-DATASET-T5 (new; not yet queued)
Substrate-product reading: Dataset quality is the primary determinant of Recipe 6.2
  (distillation) success. Generating 1K (query, substrate_call, result, answer) tuples
  from gpt-4o-mini and manually auditing 100 estimates the systematic error rate before
  scaling to 100K+ for full fine-tuning. Low-cost gate that determines if the Recipe 6.2
  path is worth pursuing.
Tier hint: API cost ~$5-10; 2-3 hours
Why-now: v2 planning gate; do after T3 confirms schema is solid

Pre-reg bands:
  HARD-PASS: >= 85% of 100 audited examples are clean (correctly formed call + correct
             result interpretation + fluent answer)
  HARD-FAIL: < 60% clean examples (systematic errors in teacher output; redesign before
             scaling dataset)
  MID-BAND: 60-85% clean (specific failure modes; targeted fixes before scaling)

Inputs required: Confirmed substrate API schema (from T3); gpt-4o-mini API access;
  query generation covering 5 types x 200 = 1000 queries; manual audit rubric.
  Depends on T3 HARD-PASS or MID-BAND (schema must be stable first).

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_llm_capability_separation_substrate_5x_2026-06-08.md
- v1 demo build plan: d:/AI/hd-instrument/notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md
- PP-135 substrate-KV implementation: search experiments/ for exp_d2_pythia1p4b_substrate_kv_gpu_v1.py
- PP-135 cross-shard: search experiments/ for exp_d3_crossshard_substrate_kv_gpu_v1.py
- KBLaM prior art: arxiv 2410.10450 (ICLR 2025)
- Knowledge Offloading (KOFF): arxiv 2605.29075 (May 2025)
- Knowledge Capsules: arxiv 2604.20487 (April 2026)

---

## Contract section

exp_dev owns: anchor design, sweep grid, threshold validation, queue assignment, VRAM
  profiling methodology, model loading approach, quantization level choices.

Research provided: literature-grounded HARD-PASS/HARD-FAIL recommendations, LLM size
  guidance, architectural recipe ranking, honest P_deflated estimates.

Orchestrator owns: strategic priority ordering if multiple anchors compete for queue slots.

---

## Autonomy declaration

exp_dev MAY modify pre-reg bands if the anchor design changes scope (e.g., if T1 runs on
a different 3B model than specified, the HARD-PASS threshold may be adjusted for that
model's known capabilities). exp_dev MUST record any threshold changes in the anchor's
pre-reg block before dispatch.

exp_dev MAY skip T4 and T5 if T1 and T2 produce HARD-FAIL results that change the
strategic direction. In that case, escalate to orchestrator with failure analysis before
dispatching further anchors from this handoff.
