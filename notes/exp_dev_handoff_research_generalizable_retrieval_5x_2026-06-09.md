# exp_dev hand-off — research: generalizable retrieval training for KB-adapter LLMs

**Filed:** 2026-06-09 by research sub-agent (5x lit-scan, T5C-C1-FACT gate).

**Trigger:** C1-FACT v1 HARD_FAIL (train recall 1.000, held-out recall 0.000). Research note path: `notes/research_drill_generalizable_retrieval_training_5x_2026-06-09.md`

**Pause state:** Check `data/orchestrator_paused.flag` before queue dispatch. Annotation bumps allowed while paused; queue-triggering commits require ACTIVE state.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters beyond the evidence-backed starting points in the research note.

---

## What just failed

**C1-FACT v1 HARD_FAIL:** Pythia-160M + KB adapter on 9 training facts, train recall 1.000, held-out recall 0.000. Adapter memorized the 9 training facts as a lookup table. No generalizable "retrieve the matching slot" behavior learned. Root cause: KB too small (9 facts is within 160M model memorization capacity per scaling law arXiv:2406.15720), no KB-absent training examples, loss likely on KB reconstruction not answer prediction.

**Architecture HARD_PASS (separate finding):** Substrate-attention IMPROVES Pythia-160M perplexity 20%, Qwen-2.5-1.5B perplexity 15%. The attention injection mechanism works; the KB adapter training recipe is what failed.

---

## Anchor candidates (rank-ordered, cheapest-first per PROT-004)

### Anchor 1 — FHRR-space compatibility validation (CPU-local)
- **Pointer:** research note Section 7.1, "Wirtinger Differentiability" subsection; cap_map pool retrieval ✅ Validated
- **Substrate-product reading:** If FHRR cosine similarity structure is compatible with Sentence-BERT structure (Spearman rho > 0.70 on 1K shared facts), FHRR can serve as the frozen KB encoder for C1-FACT-v2 — eliminating the separate sentence encoder dependency and enabling a fully substrate-native KB pipeline. If not, Sentence-BERT is the encoder and the substrate provides retrieval only.
- **Tier hint:** CPU-local (pairwise cosine matrix comparison, no GPU needed; ~30-60 min)
- **Why now:** This is the pre-test gate (per [[feedback-drill-pretest-required]]) before any GPU spend. Costs ~0, directly determines encoder choice for Anchors 2-5. Cheap decisive test.

### Anchor 2 — Minimal held-out generalization smoke (GPU)
- **Pointer:** research note Section "Specific Recommendations — Training KB size" + "Mixed distribution" + "Loss function"; KBLaM arXiv:2410.10450 training recipe
- **Substrate-product reading:** Confirms or refutes whether the generalizable retrieval recipe (50K+ facts, separate W_k/W_v, 50/50 KB-present/absent, 600 steps, cross-entropy on answer tokens) achieves held-out recall > 0.40 on Pythia-160M. This is the direct C1-FACT product claim gate: "substrate is the LLM's swappable knowledge store."
- **Tier hint:** GPU (50K fact KB, instruction-tuning Pythia-160M adapter, ~1-2h A100)
- **Why now:** The architecture is now lit-validated. KBLaM achieved this in 601 steps. With frozen LLM and only W_k/W_v trained, this is a lightweight training run.

### Anchor 3 — SR-KI-style attention supervision (GPU)
- **Pointer:** research note Section "SR-KI" + "Loss function (secondary recommendation)"; arXiv:2511.06446
- **Substrate-product reading:** Adding explicit attention supervision loss (L_attn at retrieval layer) is the delta between ~80% and ~98% Recall@10 in SR-KI. For C1-FACT-v2, this is the path from MIDDLE_BAND (~0.40 held-out recall) to HARD_PASS (>0.60 held-out recall). Depends on Anchor 2 result.
- **Tier hint:** GPU (builds on Anchor 2 checkpoint; adds L_attn supervision term; ~1-2h additional)
- **Why now:** Should be run as Anchor 2 follow-up if Anchor 2 lands in MIDDLE_BAND.

### Anchor 4 — PP-107 algebraic abstention gate (CPU-local)
- **Pointer:** research note Section 7.2 "PP-107/PP-180/PP-182 as Architectural Pressures"; cap_map PP-107 ✅ Validated (AUC=1.000)
- **Substrate-product reading:** Coupling the already-validated PP-107 abstention primitive as a pre-gate on KB attention (zero out attention weights when max cosine similarity < 0.70 threshold) reduces false-positive KB lookups and may allow reducing KB-absent training fraction from 50% to 20-30%. Entirely a substrate-native innovation; no equivalent in KBLaM or RETRO.
- **Tier hint:** CPU-local (inference-time gate evaluation; no training; ~1-2h implementation + eval)
- **Why now:** Direct reuse of validated PP-107 primitive; zero training cost; product differentiator.

### Anchor 5 — Substrate-consistency coupling term (GPU, longer)
- **Pointer:** research note Section 7.3 "Can Algebraic Primitives Add Retrieval Pressure?"; pool retrieval ✅ Validated
- **Substrate-product reading:** Adding L_consistency = ||substrate_retrieve(query_FHRR) - target_fact_FHRR||^2 jointly optimizes the LM adapter AND the substrate KB encoding to remain compatible. This is the "fully integrated substrate-LLM retrieval loop" claim — the most novel relative to published prior art. Creates a product claim no competitor has: gradient flows from LLM adapter training back into substrate-compatible KB structure.
- **Tier hint:** GPU (requires substrate differentiable retrieval path; ~2-3 days implementation + ~1 day training)
- **Why now:** Only after Anchor 2 confirms the base recipe works. Do not attempt until held-out recall > 0.40 validated.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_generalizable_retrieval_training_5x_2026-06-09.md`
- Cap_map for PP-107/PP-180/PP-182/pool retrieval validated rows: `d:/AI/hd-instrument/notes/substrate_capability_map.md`
- Scaling law reference: arXiv:2604.00715 (L(N,D,R) formula with eta~1e-3; threshold D/N=4.14)
- Fact memorization ceiling: arXiv:2406.15720 (C = C* - alpha*exp(-beta*Epoch); 160M model cannot memorize >few hundred facts)
- KBLaM recipe: arXiv:2410.10450, github.com/microsoft/KBLaM, README: N=120K, B=20, total_steps=601
- SR-KI attention supervision: arXiv:2511.06446 (two-stage: locate retrieval layer, supervise attention)
- RETRO anti-memorization mechanism: arXiv:2112.04426, ICML 2022 (same-document neighbor filtering = document filtering during training)
- Atlas EMDR2 loss for future multi-hop extension: arXiv:2208.03299, JMLR v24

---

## Contract section

- exp_dev owns ALL experiment design decisions (N, M, K, LR, batch size, anchor name, queue routing, threshold bands, smoke profile, full profile)
- Research note provides evidence-backed starting points; exp_dev applies judgment on adaptation to current substrate and runner constraints
- No inline experiment design in this handoff per [[feedback-no-experiment-design-in-prompts]]
- Per [[feedback-drill-pretest-required]]: Anchor 1 (FHRR compatibility) is the mandatory pre-test before GPU spend on Anchors 2-5
- Per [[feedback-short-cloud-runs-preferred]]: Anchors 2-3 are designed to be ~1-2h A100 runs, not overnight; scale is 50K facts, 600 steps; no extended pretraining required

## Autonomy declaration

exp_dev decides: encoder choice (FHRR vs Sentence-BERT pending Anchor 1), exact KB-present/absent split ratio within recommended 40-60% range, LR schedule, whether to combine Anchors 2+3 into one run, queue routing (Tier A/B/C), smoke vs full profiles, hold-out evaluation exact implementation, and the substrate-consistency lambda hyperparameter if Anchor 5 is pursued.

Research does NOT constrain: specific LR value, exact batch size, exact hold-out size, choice of fact source for synthetic KB, sequence of anchors beyond the cheapest-first ordering.
