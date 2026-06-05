# exp_dev hand-off -- research: unified cross-modal knowledge representation via VSA substrate

**Filed:** 2026-06-04 by research sub-agent.

**Trigger:** 2x depth drill on cross-modal VSA binding completed. Findings yield 2 concrete experiments with CPU-scale cheap decisive tests and 1 cap-map-opening mechanism (rank-1 multi-modal deletion).

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

**Research note:** `notes/research_drill_unified_cross_modal_substrate_2x_2026-06-04.md`

---

## Summary of actionable findings

1. Cross-modal VSA binding (XOR-modality-keys + Hebbian co-occurrence) is algebraically sound and testable in <30s CPU at N=4096. Dense capacity predicts ~191 triplets; sparse ~4400.

2. Rank-1 deletion of individual (text, image, audio) triplets from a multi-modal substrate is algebraically equivalent to ROME/MEMIT rank-1 MLP editing -- but at the memory-layer level, not the transformer-weight level. This is a substrate-novel audit primitive not available in CLIP/ImageBind/Perceiver-IO.

3. Hebbian co-occurrence + mean-centering + anti-Hebbian repulsion is algebraically equivalent to contrastive (InfoNCE) learning at large data (Zhang et al. ICML 2023 equivalence theorem). This closes the question of whether contrastive supervision is needed for the binding step: it is NOT needed for binding, only for the initial encoder alignment.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue policy)

### 1. Cross-modal VSA binding capacity validation

- Anchor pointer: `notes/research_drill_unified_cross_modal_substrate_2x_2026-06-04.md` Section 2 (Capacity for Multi-modal Storage) + Section -- Cheap Decisive Test
- Substrate-product reading: Confirms or refutes the algebraic capacity prediction (191 dense / 4400 sparse at N=4096). If sparse Frady bound holds, substrate can store thousands of auditable multimodal associations in a 4096-dim matrix -- a product-level claim for the audit-certified multimodal store use case.
- Tier hint: CPU local or remote CPU (N=4096, 3-modality binding, <200 patterns; smoke runs in seconds)
- Why now: cheapest possible test of the unified cross-modal architecture; algebraic prediction is clear; no GPU needed

### 2. Rank-1 multi-modal deletion certificate

- Anchor pointer: `notes/research_drill_unified_cross_modal_substrate_2x_2026-06-04.md` Section 4 (Audit Primitives) + HARD-PASS / HARD-FAIL thresholds
- Substrate-product reading: If rank-1 deletion (W' = W - outer(c, c^T) / N) preserves non-deleted triplet cosine within 0.05 degradation while dropping deleted triplet cosine below 0.10, this is the ROME/MEMIT analogue for substrate -- a certifiable deletion primitive. This is the strongest product differentiator vs CLIP/ImageBind.
- Tier hint: CPU local (rank-1 matrix update at N=4096 is microsecond wall-time; full sweep over deletion count is <1 min)
- Why now: algebraic prediction is precise; this is the highest-value cap-map implication of the research note

### 3. Hebbian co-occurrence alignment probe (encoder alignment without contrastive training)

- Anchor pointer: `notes/research_drill_unified_cross_modal_substrate_2x_2026-06-04.md` Section 3 (Hebbian vs Contrastive)
- Substrate-product reading: If mean-centered Hebbian encoder alignment achieves cosine retrieval comparable to contrastive pre-training at small dataset scale (<1M pairs), substrate can claim a cost advantage over CLIP for the encoder alignment step -- not just the binding step.
- Tier hint: CPU or GPU depending on dataset size; start with CPU smoke on synthetic binary feature pairs
- Why now: closes the open question from Section 3; finite-data gap is the main uncertainty

---

## Context pointers (file paths only)

- Research note: `d:/AI/hd-instrument/notes/research_drill_unified_cross_modal_substrate_2x_2026-06-04.md`
- VSA capacity lit: Hersche et al. 2023 arXiv:2301.10352; Frady et al. 2021 arXiv:2009.06734
- Deletion audit lit: Meng et al. 2022 ROME; Meng et al. 2023 MEMIT
- Contrastive equivalence lit: Zhang et al. ICML 2023 (joint distribution matrix factorization)
- HDC multimodal precedent: EventHD PMC9363880; AMIGOS/DEAP HDC fusion (Brain Informatics 2022)

---

## Contract

exp_dev owns: anchor naming, N/M/seed/threshold specification, queue assignment, smoke + full profile design, pre-reg bands, cap_map annotation proposal.

Orchestrator owns: cap_map write, verdict routing.

Research owns: this file and the research note. No further action required from research.

---

## Autonomy declaration

exp_dev is fully autonomous on experimental design within the pointers above. No inline parameter specifications are given here per [[feedback-no-experiment-design-in-prompts]].
