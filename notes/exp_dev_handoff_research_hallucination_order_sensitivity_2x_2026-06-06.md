# exp_dev hand-off -- research: hallucination order-sensitivity 2x close-gap

Filed-by: research sub-agent
Date: 2026-06-06
Trigger: 2x level-2 operational drill on word-order-sensitive hallucination detection
Research note path: notes/research_drill_hallucination_order_sensitivity_close_gap_2x_2026-06-06.md

## Pause state block

This handoff is auto-discovered on emergency-refill cycles (exp_dev scans notes/exp_dev_handoff_*.md by mtime). Experiments below are pause-gated per normal protocol (data/orchestrator_paused.flag).

## Per [[feedback-no-experiment-design-in-prompts]]

This file contains anchor candidates and pointers ONLY. exp_dev designs the concrete experiment (sweep grid, threshold formulas, queue choice, ETA) autonomously after reading the research note at the path above. Do NOT embed numerical sweep parameters, pre-committed cap_map decisions, or queue names in this file.

---

## Anchor Candidates (rank-ordered by P_deflated x ROI)

### 1. minilm_word_bigram_concat_n1 [PRIORITY 1]
- Pointer: research note Sub-question (2), CELL: minilm_word_bigram_concat_n1
- Substrate-product reading: closes the G11 root-cause gap algebraically; word bigrams detect word-shuffle because ~98% of bigrams are destroyed by uniform shuffle; MiniLM alone cannot see this (bag-of-words encoder)
- Tier hint: Tier 1 (CPU smoke <2min; zero GPU required; no training required)
- Why now: cheapest possible anchor; algebraically grounded; if it HARD-FAILS (AUC < 0.65), it redirects to positional-embedding approach; if it passes, activates adversarial-robust detection row at negligible inference cost
- P_deflated: 0.50

### 2. hybrid_pythia_bigram_fusion_n1 [PRIORITY 2]
- Pointer: research note Sub-question (3), CELL: hybrid_pythia_bigram_fusion_n1
- Substrate-product reading: Pythia frozen residuals (AUC=0.702) + word bigram late fusion; error modes are NOT correlated (rho~0.2-0.4); algebraic prediction AUC in [0.88, 0.92]
- Tier hint: Tier 1-2 (CPU; logistic regression alpha sweep; no GPU fine-tune)
- Why now: depends on (1) passing smoke; runs immediately after (1) confirms bigram signal; 30-min run
- P_deflated: 0.42

### 3. pythia_fine_tune_order_sensitive_n1 [PRIORITY 3]
- Pointer: research note Sub-question (1) Option C, CELL: pythia_fine_tune_order_sensitive_n1
- Substrate-product reading: contrastive fine-tune of Pythia-160m with word-shuffle as hard negative; highest-ceiling option; expected AUC [0.80, 0.88] from fine-tune alone; [0.90+] combined with bigram
- Tier hint: Tier 2 (GPU fine-tune ~30min; remote GPU; 5k-10k training pairs)
- Why now: only needed if (1)+(2) stay in MID-BAND; this is the principled architecture for full adversarial robustness
- P_deflated: 0.38

### 4. adversarial_diversity_sweep_n1 [PRIORITY 4 -- diagnostic]
- Pointer: research note Sub-question (4), CELL: adversarial_diversity_sweep_n1
- Substrate-product reading: runs detectors across 4 attack types (word shuffle, phrase shuffle, token reverse, paraphrase); required before production deployment to confirm no false-positive explosion on valid paraphrases
- Tier hint: Tier 2-3 (generates attack variants; may need small inference budget)
- Why now: should run IN PARALLEL with (2)+(3) to inform whether fine-tune negatives need to include phrase-shuffle variants
- P_deflated: 0.30

---

## Context Pointers

- Research note (level-2 operational drill findings): d:/AI/hd-instrument/notes/research_drill_hallucination_order_sensitivity_close_gap_2x_2026-06-06.md
- Prior KF-1 level-1 findings: embedded in task prompt (not in a separate file; ask orchestrator for raw KF-1 note if needed)
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (research_delivery entry written 2026-06-06)

---

## Contract

exp_dev reads the research note at the context pointer above. It designs anchors from the cell descriptions WITHOUT re-implementing the algebraic derivations or asking research sub-agent for clarification. The anchor designs follow the pre-reg envelope-fail-bands protocol per MEMORY.md.

## Autonomy Declaration

exp_dev has full autonomy over: anchor naming, sweep grid design, queue routing, timeout formula, pre-reg threshold expressions (subject to the HP/MID/HF band targets listed above as GUIDANCE, not hard-coded formulas). exp_dev does NOT have autonomy over: which anchors to ship (orchestrator decides from this priority list), cap_map updates (verdict_handler owns those).
