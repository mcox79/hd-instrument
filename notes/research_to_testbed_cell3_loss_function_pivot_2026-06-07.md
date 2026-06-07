# Research -> Testbed: CELL-3 loss function pivot (MSE→InfoNCE/cosine direct)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator
**Date:** 2026-06-07
**Re:** testbed_note_substrate_cell3_distilled_22M_student_v1_smoke_2026-06-07.md

The cosine HARD_FAIL at 0.79 (despite MSE HARD_PASS at 0.05) is the meaningful signal.
For substrate retrieval applications, cosine direction matters more than MSE magnitude.
The "best-of-two" combined verdict is misleading here.

## Why MSE passes but cosine fails

Well-documented distillation regime: MSE optimizes L2 distance which is dominated by
magnitude in high-dim spaces (2048-D in this case). The student converges to representations
that match the teacher's mean and scale but lose fine-grained directional structure that
distinguishes individual facts. This is the same loss-function failure mode as cycle 156's
SFT-for-retrieval collapse (SFT retrieval quality drops to 0.3%; InfoNCE retains 66%).

## Three next steps

### 1. CELL-3 FULL is still worth running but expect modest cosine improvement

Dispatching CELL-3 FULL at 5.84M is informative but the bottleneck is the loss function,
not data quantity. Expect cosine to improve modestly (perhaps 0.79 → 0.83-0.87 range)
but probably not reach the 0.95 target.

If you want to confirm this prediction cheaply: run CELL-3 FULL at the existing MSE loss
and report whether cosine actually closes. If yes, my prediction is wrong and the existing
recipe is sufficient. If no, proceed to step 2.

### 2. Loss function pivot: InfoNCE or direct cosine loss

Replace MSE distillation with one of:

**Option A: Direct cosine loss**
- Loss = 1 - cosine(student(x), teacher(x))
- Directly optimizes the metric we care about
- Simple implementation; same training infrastructure
- Predicted cosine after training: 0.92-0.97

**Option B: InfoNCE contrastive distillation**
- Treat (student(x), teacher(x)) as positive pair; (student(x), teacher(y_random)) as negatives
- Captures the SCALE of the embedding space plus directional alignment
- More sophisticated; needs careful negative sampling
- Predicted cosine after training: 0.93-0.98 with downstream retrieval quality preserved

Either option, ~5 hours wall on GH200 to retrain at 1M scale; 30-40 min at 5.84M scale
if FULL.

### 3. Downstream retrieval test of the existing 0.79-cosine student

Independent of whether we pivot the loss, run a downstream HotpotQA retrieval test on
the current student to measure whether 0.79 cosine is actually usable for retrieval or
if directional precision matters in practice.

Method: 50 HotpotQA questions, use distilled student as the encoder, measure recall@10
against published bge-small baseline (0.74) and against teacher Llama-1B (disqualified at
<5% in cycle 156 -- comparison for context).

HARD-PASS at this test: student recall@10 >= 0.65 (within 90% of bge-small).
HARD-FAIL: student recall@10 < 0.50.

A PASS here means we can use the 0.79-cosine student for v1 demo, even if we pivot the
loss for v1.1 quality upgrade. A FAIL confirms the cosine gap matters and we MUST pivot
the loss.

Wall: 2-3 hours CPU.

## Methodology meta-flag

The "best-of-two" combined verdict logic introduces ambiguity. For future distillation
cells, recommend reporting each metric independently and letting the routing rule decide
based on the application. For retrieval cells, cosine should be primary; MSE is a
sanity check.

This is similar to the storage cells' multi-dim acceptance criteria: don't collapse
multiple metrics into a single HARD_PASS/HARD_FAIL. Report the full picture and let the
synthesis decide.

## Cross-references

- CELL-3 smoke result: notes/testbed_note_substrate_cell3_distilled_22M_student_v1_smoke_2026-06-07.md
- Cycle 156 SFT vs InfoNCE finding: notes/orchestrator_to_research_results_summary_2026-06-07_cycle156.md (online_lora_infonce_proxy MID)
- Two-encoder architecture: notes/research_to_exp_dev_URGENT_two_encoder_architecture_2026-06-07.md
- Multi-dim criteria supplement: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md

---

**END.**

**Testbed:** Three options, prioritize per cost:
- Cheap path: run the 2-3hr downstream HotpotQA retrieval test FIRST on the current
  0.79-cosine student. If it passes, the current student is usable for v1 (loss pivot
  becomes v1.1).
- Standard path: dispatch CELL-3 FULL at MSE to confirm the cosine prediction.
- Pivot path: retrain at 1M smoke with InfoNCE or direct cosine loss; if HP, dispatch
  pivoted CELL-3 FULL.

My recommendation: cheap path first. The downstream test tells us whether we even need
to pivot.
