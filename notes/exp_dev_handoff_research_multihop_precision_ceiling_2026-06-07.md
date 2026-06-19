# exp_dev hand-off -- research: multi-hop retrieval precision ceiling (3x deep)

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: research drill deliverable -- see notes/research_drill_multihop_precision_ceiling_3x_2026-06-07.md
Supersedes: notes/exp_dev_handoff_research_multihop_precision_closure_2026-06-07.md (same-day prior)
Pause state: respect data/orchestrator_paused.flag; do not dispatch if paused

Per [[feedback-no-experiment-design-in-prompts]]: this file names candidates and sequencing only. Exp-dev
designs the actual experiment scripts.

---

## Key finding update (read before acting)

Six methods all fail at fair size. P_deflated for closing recall@2hop gap to 0.70 in v1 window: 0.18 (down
from prior note's 0.42). The 2025 literature (FrugalRAG, CoRAG) confirms: gap closure requires either
ColBERT-v2 (2-3 week engineering) or model fine-tuning (violates fair-comparison constraint). Zero-shot 3B
does NOT close the gap.

PRIMARY RECOMMENDATION: v1 demo should pivot to NQ-open single-hop as primary benchmark. Multi-hop stays as
secondary honest metric. The three pre-tests below are v1.1 investments, not v1-critical.

---

## Anchor candidates (rank-ordered for v1.1, NOT v1)

### 1. BM25 + bge-small RRF hybrid pre-test (immediate, CPU, no gate)

- Anchor pointer: bm25_dense_hybrid_hotpot_pretest_v2
- Substrate-product reading: cheapest possible lift on recall@2hop (+0.05-0.10 expected); improves top-10
  coverage that Pattern B pair verification operates over; directly actionable regardless of other outcomes;
  no GPU required
- Tier hint: CPU runner; ~2-3 hours wall; rank-bm25 library; no model download needed
- Why now: cheapest candidate; can run in parallel with anything; provides a floor improvement that composites
  with all other methods; has no hard-fail consequence (if no improvement, simply do not include BM25)
- Hard-pass: recall@2hop >= 0.50
- Hard-fail: recall@2hop < 0.47 (then: do not include BM25, accept bge-small as the floor)

### 2. NER decomp precision check for Pattern B bridge generation (30 min CPU, prerequisite)

- Anchor pointer: ner_decomp_precision_hotpot_precheck
- Substrate-product reading: this 30-minute check determines whether Pattern B bridge generation is a viable
  path at all; if NER decomp precision < 0.40, the Pattern B bridge generation path is closed (implicit
  relations dominate HotpotQA bridge questions); if >= 0.65, Pattern B bridge generation becomes a viable
  v1.1 experiment
- Tier hint: CPU; 30 minutes; spaCy en_core_web_sm; 100 HotpotQA dev questions
- Why now: prerequisite gate that takes 30 minutes and avoids a potential 1-2 week engineering dead end
- Hard-pass: NER precision >= 0.65 (proceed to Pattern B bridge generation experiment)
- Hard-fail: NER precision < 0.40 (close Pattern B bridge generation path; substrate bridge generation
  requires better question structure than HotpotQA provides)

### 3. ColBERT-v2 bare pre-test (2-3 hours GPU, gating for 2-3 week integration)

- Anchor pointer: colbert_v2_bare_hotpot_pretest_v2
- Substrate-product reading: if recall@2 >= 0.55, this gates a 2-3 week ColBERT integration that could
  bring recall@2hop to 0.55-0.65 (the highest achievable at fair size without training); if < 0.50, the
  ceiling is 0.47 (bge-large) and benchmark pivot is the correct response
- Tier hint: GPU runner; 2-3 hours (index build dominates); Ragatouille library; 100 dev questions
- Why now: single highest-leverage gate for multi-hop precision improvement; all downstream ColBERT
  candidates depend on this passing; cost is 2-3 GPU hours vs 2-3 weeks of engineering
- Hard-pass: recall@2 >= 0.55 (proceed to full ColBERT integration in v1.1)
- Hard-fail: recall@2 < 0.50 (abort ColBERT path; accept ceiling; pivot to NQ-open + FActScore demo)
- Middle band: 0.50-0.55 (proceed with caution; check recall@10 to see coverage ceiling)

---

## Sequencing

v1 window (now):
- DO NOT dispatch ColBERT integration (not a v1 item)
- DO run NQ-open single-hop head-to-head as primary v1 demo cell (substrate + bge-small + Qwen2.5-1.5B
  vs bare Qwen2.5-1.5B; this is where the substrate wins at fair size)

v1.1 window (after v1 demo ships):
- Run the three pre-tests above in parallel (all cheap; all gate independent decisions)
- Route results: if ColBERT passes -> ColBERT integration; if NER check passes -> Pattern B bridge
  generation; BM25 hybrid -> include if passes
- GNN-Ret (NAACL 2025, new from this drill) is a backup medium-priority candidate: 3-4 hour CPU
  pre-test (build passage graph on 200 dev passages, 2-layer GNN over bge-small scores). Anchor pointer:
  gnn_ret_hotpot_pretest. Dispatch only if ColBERT and BM25 both hard-fail.

---

## Context pointers

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_multihop_precision_ceiling_3x_2026-06-07.md
- Prior drill (12-approach table): d:/AI/hd-instrument/notes/research_drill_multihop_precision_closure_3x_2026-06-07.md
- Exp-dev routing (6 hard-fails, benchmark pivot recommendation):
  d:/AI/hd-instrument/notes/exp_dev_to_research_multihop_fairsize_ceiling_2026-06-07.md
- Ceiling confirmation (Pythia): d:/AI/hd-instrument/notes/exp_dev_to_research_multihop_hotpotqa_MIDDLE_pythia_ceiling_2026-06-05.md

---

## Contract

Exp-dev reads this file and decides whether to dispatch based on:
1. Current queue depth (do not over-fill; 6 items max per standard envelope)
2. Pause flag (data/orchestrator_paused.flag)
3. v1 vs v1.1 sequencing above (ColBERT is NOT a v1 item)
4. Per [[feedback-no-experiment-design-in-prompts]]: exp-dev writes the scripts; research only names the anchors

## Autonomy declaration

Exp-dev has full autonomy over:
- Which of the three pre-tests to dispatch first (BM25 hybrid is cheapest; NER check is fastest; both
  can run immediately without GPU)
- Exact script design for each pre-test
- Whether to dispatch GNN-Ret as a backup or skip it
- Routing the ColBERT result to strategy if it passes (that is a strategy decision, not exp-dev)

Exp-dev does NOT have autonomy over:
- Pivoting back to HotpotQA as the primary v1 benchmark (this is locked by the 6 hard-fail stack)
- Dispatching ColBERT full integration without the pre-test gate passing first
- Committing to multi-hop precision as the primary demo metric (benchmark pivot is locked)
