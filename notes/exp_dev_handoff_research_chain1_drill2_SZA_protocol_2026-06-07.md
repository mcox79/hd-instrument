# exp_dev hand-off -- research: SZA black-box protocol (Chain 1 Drill 2)

Filed-by: research session
Trigger: Chain 1 Drill 2 (notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill2_2026-06-07.md)
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: anchors + WHY + pre-reg bands only.

Subset of cells in this hand-off OVERLAP with the ZKL Certificate 10-hour battery (separate hand-off). When both run, share results across both.

---

## Anchor candidates (ranked by strategic value)

### 1. zkl_substrate_vs_rag_paraphrase_attack (~3 hr CPU; Tier-1)
- Substrate-product reading: comparative ZKL measurement -- substrate vs simulated RAG baseline under paraphrase attack at k=50. Quantifies the "substrate ~64% leakage of RAG baseline" prediction from the sign-quantization 2/pi factor.
- Why now: validates a substrate-vs-incumbent quantitative claim that customers will ask for
- HP: ZKL_substrate / ZKL_RAG <= 0.70 at k=50 (substrate leaks 30% less)
- MID: 0.70-0.90 (qualify)
- HF: > 1.0 (substrate does NOT leak less; commercial advantage gone)

### 2. whitening_zkl_reduction_ablation (~2 hr CPU; Tier-2)
- Substrate-product reading: substrate WITH vs WITHOUT whitening on identical KB + attack; measure ZKL reduction factor
- Why now: validates the dual-purpose-whitening claim (retrieval AND privacy)
- HP: ZKL(whitening ON) <= 0.60 * ZKL(whitening OFF) (>= 40% reduction)
- MID: 0.60-0.90 (partial reduction)
- HF: > 0.90 (no meaningful privacy contribution from whitening)

### 3. rsa_accumulator_post_quantum_swap_smoke (~1 hr CPU; Tier-2)
- Substrate-product reading: replace RSA accumulator with hash-based accumulator (Merkle root only); verify audit chain still works end-to-end; measure CPU overhead
- Why now: validates post-quantum migration path for DOD tier per GOLD 4.0
- HP: < 0.1% CPU overhead vs RSA; audit chain verifies correctly
- MID: 0.1-1% overhead (qualify; document migration cost)
- HF: > 1% overhead OR audit chain breaks (post-quantum path needs redesign)

---

## Context pointers

- Research note: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill2_2026-06-07.md
- Prior drill (Drill 1): SAS framework foundation
- Cross-reference: ZKL Certificate 10-hour battery hand-off (subset overlap on ZKL(k=50))

---

## Contract + Autonomy

exp_dev designs implementation. Anchor 1 cell may share results with ZKL Certificate cell 3 if implementation aligns.
