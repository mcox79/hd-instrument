# Research -> Exp-Dev: queue five v1.1 moat-extension experiments

**From:** Research session
**To:** Exp-Dev
**Inform:** Testbed + Orchestrator
**Date:** 2026-06-07
**Re:** User directive ("send them all"); north-star validation already in via substrate_vs_bare_llm_hotpot_v1 smoke (+0.35 F1).

## Framing update (important)

Today's north-star result confirms substrate-augmented Qwen2.5-1.5B beats bare Qwen by
+0.35 F1 (0.234 -> 0.586) on HotpotQA at fair size. The v1 baseline is GO. The 5
experiments below are MOAT EXTENSIONS, not demo prerequisites. They expand substrate's
differentiation vs vanilla RAG.

Apply multi-dim acceptance criteria. Use the two-encoder architecture
(sentence-transformer for retrieval ranking; Llama-1B for KEY job).

## 1. bge-coverage + substrate-compositional-verification (HIGHEST LEVERAGE; CPU, 3 hours)

bge-small recall@10 = 0.74 (facts are in pool). The substrate K-hop tested in cycle 156-157
was used INSTEAD of bge, which hurt. What hasn't been tested: substrate compositional
verification operating ON the bge-small top-10 candidate set, selecting the right 2-hop
pair from those candidates rather than replacing bge.

Method:
- 50 HotpotQA bridge questions
- Step 1: bge-small retrieves top-10
- Step 2: substrate composition (Pattern B if SRL passes, fallback to K-hop with confidence
  filter) selects the most likely 2-hop pair from the top-10
- Compare answer F1 vs bge-top-2 (current baseline) and vs bge-top-10-as-context (what
  bare Qwen uses)

HARD-PASS: answer F1 lift >= +0.05 vs bge-top-10 baseline. This means substrate composition
adds value beyond what brute-context provides.

Why high-leverage: combines bge's contrastive coverage with substrate's compositional
selection. Sidesteps both the multi-hop ceiling AND the "substrate hurts strong encoders"
finding. If it works, it's a clean v1.1 enhancement that doesn't require Pattern B's SRL
gate.

## 2. d=30 PCA truncation full-stack storage validation (CPU+GPU, 4 hours)

PCA bottleneck KEY-job F1=1.0 at d=30 (cycle 157). Implication: per-fact KEY cost drops
from 4 KB to 60 bytes if d=30 truncation is sufficient at full stack scale.

Method:
- Build full substrate at 100K facts with d=30 PCA-truncated KEYs
- Stack with 4-bit W quantization (cycle 155 HP) + modern Hopfield (cycle 155 HP at
  N=4096-16384)
- Measure: actual per-fact storage cost, recall@1 across noise sweep, K-hop accuracy,
  audit integrity

HARD-PASS: per-fact cost < 1 KB AND recall@1 >= 0.95 AND K-hop accuracy >= 0.90 AND
audit integrity = 100%.

This was not in the original storage stack projection. Combined predicted reduction
~280x from current 286 KB (5 KB v1 + d=30 KEY + 4-bit + modern Hopfield = roughly 500
bytes - 1 KB target zone).

## 3. Substrate value-add curve vs encoder quality (CPU, 3 hours)

Cycle 156-157 paradox: substrate K-hop lifted MiniLM (15->20%) but hurt bge-small (29->27%).
Is substrate retrieval value-add a NEGATIVE function of encoder quality?

Method:
- Same substrate machinery (production whitening + K-hop with confidence filter at T=0.5)
- Applied to: MiniLM, bge-small, bge-base, e5-small, e5-large
- Same 50-question HotpotQA harness
- Measure recall@2hop change per encoder

Pre-registration: predicted curve shape -- substrate lift decreases with encoder quality
up to bge-large then plateaus at zero or negative. Disconfirmation: substrate lifts ALL
encoders or substrate hurts ALL encoders.

HARD-PASS: clear empirical curve shape with identified knee point.

Implication for customer pitch: tells us which encoder regimes the substrate's
distributed/audit/compositional advantages still matter at, vs which regimes the encoder
already does substrate's retrieval job.

## 4. Predicate inversion at sparse selectivity (CPU, 3 hours)

predicate_ratio_audit MID at cycle 155: 92% at 5% selectivity, degrades <80% at 10%+.
Pattern B's predicate routing works in the SPARSE regime. Specific use case: legal,
medical, regulated KBs where predicates are naturally sparse (case types, drug categories,
event types).

Method:
- 200-fact structured KB with sparse predicate distribution (5-10 unique predicates per
  KB)
- 20 schema-aware queries: "find all events where predicate = X"
- Pattern B routing
- Measure recall@10 with full multi-dim criteria (audit, K-hop, KF-1 unchanged)

HARD-PASS: recall@10 >= 0.85 at <= 5% selectivity AND all multi-dim criteria pass.

This is a BOUNDED Pattern B capability we can demo with confidence even if broader
Pattern B exploration shows mixed results. Specific value for regulated-market customers.

## 5. CELL-3 distillation with InfoNCE loss (GPU, 5 hours, ~$2)

CELL-3 smoke at MSE: cosine 0.79 (HARD_FAIL the 0.95 target). Same loss-function failure
mode as cycle 156's SFT-for-retrieval collapse. The drilling is done; we know the answer
needs InfoNCE.

Method:
- Same data, same architecture, same hyperparameters as CELL-3 v1
- Loss: 1 - cosine(student, teacher) -- direct cosine optimization
- OR InfoNCE contrastive distillation (positive: student/teacher of same input; negatives:
  student/teacher of different inputs)
- 1M smoke scale; if HARD-PASS, dispatch 5.84M FULL

HARD-PASS: val_cos >= 0.92 at 1M smoke AND val_mse remains within 1.5x of MSE-loss baseline.

If HP, the 22M distilled student is production-ready for Phase 0.5 deployment. Substrate
inference becomes cheap.

## Sequencing recommendation

Tier-A (CPU-cheap, run in parallel):
- Experiment 1 (bge + substrate composition)
- Experiment 3 (substrate value-add curve)
- Experiment 4 (predicate inversion sparse selectivity)

Tier-B (CPU + small GPU; run after Tier-A informs):
- Experiment 2 (d=30 PCA truncation full stack) -- depends partly on whether substrate
  composition adds value at d=30 representation

Tier-C (GPU, modest cost):
- Experiment 5 (CELL-3 InfoNCE loss)

Apply HARD-PASS/HARD-FAIL decision rules autonomously per cell. File synthesis when all
five resolve so the user can prioritize the v1.1 moat extensions.

## Cross-references

- North-star result: notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md
- CELL-4 100K HP: notes/testbed_note_substrate_hp12_v2_100k_pseudoinverse_v1_2026-06-07.md
- Multi-hop ceiling (now reframed): notes/exp_dev_to_research_multihop_fairsize_ceiling_2026-06-07.md
- Manifold + KEY-job convergence: notes/orchestrator_to_research_results_summary_2026-06-07_cycle157.md
- Pattern B exploration program: notes/research_to_exp_dev_pattern_b_full_exploration_program_2026-06-07.md
- Storage compression alternatives 3x: notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** queue all 5 in Tier-A/B/C sequencing. CPU-cheap experiments 1, 3, 4 first
in parallel. Apply decision rules autonomously. The v1 baseline is GO via the north-star
result; these are moat extensions.

**Testbed:** experiment 5 is the CELL-3 loss pivot; coordinate with experiment 2's
storage validation when both reach the GPU-needed stage.

**User:** all 5 queued. v1 demo recipe is already validated via the north-star result;
these expand substrate's moat vs vanilla RAG.
