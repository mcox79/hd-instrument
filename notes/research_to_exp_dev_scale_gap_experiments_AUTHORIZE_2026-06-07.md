# Research -> Exp-Dev: scale-gap empirical experiments AUTHORIZED (parallel to 3 drills)

**From:** Research  **Date:** 2026-06-07  **Re:** User directive "drill all 2x + route all
experiments to exp dev + keep the loop going" — 3 scale gaps identified; drills dispatched;
direct empirical experiments routed in parallel.

## 3 scale-gap experiments to dispatch immediately

These DON'T wait for the drills. The drills will surface failure modes + crazy options;
the experiments resolve the empirical question.

### Experiment 1: Qwen-7B benchmark promotion battery
Promote today's benchmark results from Qwen2.5-1.5B to Qwen-7B. Reasoning+code drill
already recommended this as v1 baseline (1.5B for ablation only).

Cells:
- hotpot_3baseline_qwen7b (~30-60 min local GPU; 200 questions; same as current 1.5B run)
- trivia_rc_3baseline_qwen7b (~30-60 min local GPU; same 200 questions)
- pubmedqa_3baseline_qwen7b (~30-60 min local GPU; same v3 config)
- babilong_qa1_qwen7b (~1-2 hr local GPU; same protocol)
- llm_decomp_hotpot_qwen7b (~1 hr GPU; does Fano-style closure from cycle 158 hold at 7B?)

HARD-PASS per cell: substrate-augmented Qwen-7B >= substrate-augmented Qwen-1.5B (substrate
value-add HOLDS at 7B); OR substrate-augmented Qwen-7B beats bare Qwen-7B by >= +0.05.

BORDER: substrate-augmented 7B matches bare 7B (substrate becomes auditing-only at 7B).

HARD-FAIL: substrate value-add evaporates at 7B (substrate-augmented 7B = bare 7B; substrate
becomes pure compliance layer).

Wall: ~5-6 hours local GPU total.

### Experiment 2: Substrate 1M scale validation
Promote CELL-4 100K perfect recall HP to 1M scale. Required for production deployment
claims + pre-trained Wikipedia substrate (5.84M articles) feasibility.

Cells:
- substrate_1M_recall_validation (~4 hr local GPU; build substrate at 1M; measure
  recall@1 + capacity behavior + latency)
- pinv_smw_timing_1M (~30 min CPU; verify pinv 1.77 ms scaling holds at 1M)
- pattern_b_chain_rescue_1M (~1-2 hr GPU; does L2 norm chain rescue hold at scale)
- bridge_collision_1M (~1-2 hr GPU; Pattern B binding collision rate at 1M)

HARD-PASS: substrate at 1M maintains >= 99% recall@1 AND pinv timing stays < 5 ms AND
chain rescue holds (>= 0.85 acc at K=4) AND bridge collision rate < 1%.

HARD-FAIL: any one collapses materially (substrate-at-scale claim breaks; v1.1 product
needs scale architecture redesign).

Wall: ~6-8 hours local GPU total.

### Experiment 3: v1.1 component composition end-to-end integration
Build full v1.1 stack and measure end-to-end at HotpotQA. This is the engineering
integration validation NOT a research drill.

Components composed:
- Pre-trained Wikipedia substrate base (CELL-2 v3; ship pending)
- DistilBERT-NER cascade for bridge entity extraction
- Pattern B Mech1 L2 normalization
- Sleep defrag streaming Misra-Gries aggregation
- Substrate retrieval (bge-small for retrieval; Llama-1B for KEY)
- Qwen-1.5B answer generation (Tier 4 LoRA pending)
- Audit chain (Merkle proof per hop)

Measure:
- End-to-end accuracy on HotpotQA 200 questions (compare to current 0.501)
- Per-component latency breakdown
- Per-component accuracy contribution (ablate one at a time)
- Composition latency vs sum-of-individual latencies (interaction overhead)

HARD-PASS: end-to-end accuracy >= 0.55 (clears multi-hop ceiling via composition);
total latency < 1.5 sec per query.

BORDER: 0.51-0.55 (composition holds individual benefits but doesn't compound).

HARD-FAIL: end-to-end < 0.50 (components cancel rather than compound; integration
redesign needed).

Wall: ENGINEERING-HEAVY — needs pre-trained substrate ship (1-2 weeks) + NER integration
(3-5 days) + test harness (2-3 days). Realistic ~3-4 week timeline parallel with v1
demo build.

## Sequencing

**Immediate (this session):**
- Experiment 1 cells queued local GPU; results in hours
- Experiment 2 cells queued local GPU; results in hours

**Next 1-2 weeks:**
- Pre-trained substrate ship (per substrate pre-training AUTHORIZE; 1-2 weeks)
- DistilBERT-NER cascade integration (per bridge-ID AUTHORIZE; 3-5 days)

**Next 3-4 weeks:**
- Experiment 3 integration validation (gated on pre-trained substrate + NER cascade)
- v1 demo build (FastAPI monolith + Streamlit frontend; per v1 demo design routing)

## 3 parallel drills dispatched (in flight)

- Qwen-7B promotion risks + opportunities 2x
- Substrate 1M scale risks 2x
- v1.1 composition integration risks 2x

These will return crazy options + failure modes within 20-30 min; pre-tests they
identify will be routed as they land.

## Cross-references

- Reasoning+code drill (Qwen-7B recommendation): notes/research_drill_reasoning_math_code_2x_2026-06-07.md
- Substrate iterative multi-hop 3x (1M scale flag): notes/research_drill_substrate_iterative_multihop_3x_2026-06-07.md
- v1 demo design routing: notes/research_to_exp_dev_v1_demo_design_routing_2026-06-07.md
- Pre-training AUTHORIZE: notes/research_to_exp_dev_substrate_pretraining_pretests_AUTHORIZE_2026-06-07.md
- Bridge-ID AUTHORIZE: notes/research_to_exp_dev_bridge_id_pretests_AUTHORIZE_2026-06-07.md

---

**Exp-Dev:** authorize Experiments 1 + 2 immediately (cheap; resolves scale gaps within
hours). Experiment 3 (integration) is gated on engineering ship of pre-training + NER
cascade. File results as they land; drill follow-ups will inform any architecture
refinements.

**Testbed:** Experiment 1 5th cell (LLM-decomp retest at Qwen-7B) may need your lane if
GPU contention.

Loop continues.
