# exp_dev hand-off -- research: substrate-augmented attention in LLM generation

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_substrate_augmented_attention_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by risk-adjusted value)

### 1. Cell A1 -- Cross-attention probe: frozen LLM + substrate KV on HotpotQA (HIGHEST PRIORITY)
Anchor pointer: SUBST-XATTN-A1 (new; not yet queued)
Substrate-product reading: validates that substrate-retrieved facts, when injected as cross-attention K/V at a mid-layer adapter, produce measurable F1 lift over one-shot RAG on multi-hop questions; this is the gate for all downstream cross-attention engineering (v1.5 authorization)
Tier hint: local GPU; Pythia-160M (frozen); 2-4h wall; HotpotQA dev set
Why-now: P_deflated=0.35 for the mechanism; this is the cheapest empirical test to convert that estimate to measured data; no LLM modification required; must pass before any Option A engineering is authorized
HARD-PASS: cross-attention F1 >= one-shot RAG + 0.05 on HotpotQA dev
HARD-FAIL: cross-attention F1 <= one-shot RAG + 0.02 (no architectural benefit; halt this direction)
Note: use standard dense retriever (FAISS over HotpotQA supporting facts) for this pre-test, NOT the full substrate -- isolate the cross-attention mechanism from substrate-specific representation alignment

### 2. Cell A2 -- Adaptive trigger threshold sweep on A1 model (MEDIUM PRIORITY; depends on A1 PASS)
Anchor pointer: SUBST-TRIGGER-A2 (new; not yet queued)
Substrate-product reading: determines whether a confidence-based trigger (FLARE-style) can match or exceed per-chunk retrieval F1 while reducing average retrieval calls per generation to <= 2.5; validates the latency-accuracy Pareto curve for Option C
Tier hint: local GPU; <1h wall on top of A1 model; entropy threshold sweep [0.3, 0.5, 0.7, 0.9]
Why-now: adaptive trigger is the highest-value latency optimization; if the Pareto curve is flat (no threshold reduces calls without degrading F1), per-chunk cadence becomes the default and Option C is deprioritized
HARD-PASS: a threshold exists where F1 >= A1 value AND average retrieval calls <= 2.5
HARD-FAIL: every threshold either degrades F1 by > 0.02 or keeps calls at per-chunk level

### 3. Cell A3 -- Multi-substrate cross-attention: base + domain split on HotpotQA (LOWER PRIORITY; depends on A1 PASS)
Anchor pointer: SUBST-MULTIKV-A3 (new; not yet queued)
Substrate-product reading: validates that two independent cross-attention heads (one for base substrate, one for domain-specific substrate) improve domain-specific F1 over single-substrate cross-attention; directly validates the per-customer knowledge isolation product architecture
Tier hint: local GPU; 3-5h wall; split HotpotQA into base (Wikipedia general) + domain (sports/science) subsets; train two cross-attention heads
Why-now: multi-substrate is a product differentiator but is higher engineering cost; only justified if A1 passes and A2 shows reasonable trigger behavior
HARD-PASS: multi-substrate F1 >= single-substrate F1 + 0.03 on domain-specific questions
HARD-FAIL: no improvement or regression on domain questions vs. single-substrate

---

## Context Pointers

- Research note (full drill): d:/AI/hd-instrument/notes/research_drill_substrate_augmented_attention_2x_2026-06-07.md
- Production architecture locked: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- HotpotQA whitening findings (prior): search notes for "HotpotQA whiten +63%" in exp_dev POST-COMPACTION BRIEF
- RETRO chunked cross-attention reference: arXiv:2112.04426 (Borgeaud et al. 2022)
- LongMem frozen LLM + SideNet reference: Wang et al. 2023
- FLARE adaptive trigger reference: Jiang et al. 2023

---

## Contract

exp_dev owns: anchor design, parameter sweeps, queue assignment, pre-reg bands, smoke gate, dispatch, post-ship verify.

This handoff owns: mechanism hypothesis, pre-test design intent, hard-pass/hard-fail thresholds, sequencing recommendation (A1 before A2 before A3), context pointers.

The research note (context pointer above) contains the full architecture spec, latency analysis, 6 implementation options, and calibration table. exp_dev should read it before designing anchor code.

Key constraint: do NOT use LoRA on attention heads for A1 (Option B is predicted to fail per cap_map LoRA-hurts-retrieval finding). Use new cross-attention sublayer (Option A) only.

Key constraint: A1 pre-test should use standard FAISS dense retriever, not substrate binding matrix, to isolate the cross-attention mechanism. Substrate-specific alignment is a separate concern tested after A1 passes.

---

## Autonomy Declaration

exp_dev has full autonomy over: anchor naming, code architecture, training hyperparameters, queue routing (local GPU vs remote), batch grouping, smoke configuration, result parsing.

exp_dev does NOT have autonomy over: the hard-pass/hard-fail thresholds defined above (pre-registered here), the sequencing constraint (A1 gates A2 and A3), the LoRA-exclusion constraint.

If A1 hard-fails, do not proceed to A2 or A3. File a verdict note and escalate to orchestrator for alternative mechanism consideration (Option F -- substrate decoder layer -- or return to Tier 4 text-mediated baseline).
