# exp_dev hand-off -- research: substrate-LLM communication + native concept training

**Filed-by.** research sub-agent (Sonnet), 2026-06-04.
**Trigger.** Research drill at notes/research_drill_substrate_llm_communication_and_native_concept_training_2x_2026-06-04.md delivered 5-priority actionable experiment roadmap.
**Pause state.** Check data/orchestrator_paused.flag before dispatch; abort if set.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands WHY + TASK + CONTRACT to exp_dev; it does NOT specify anchor names, sweep grids, threshold formulas, or queue choice.

---

## Anchor candidates (rank-ordered by urgency + cost)

### 1. Substrate concept-level prediction via VQ concept-IDs (HIGHEST PRIORITY)

Anchor pointer: EX-CONCEPT-1 class (new; no prior anchor in this exact form)
Substrate-product reading: Opens the concept-level language axis, the single largest untested
  capability gap. B8 logit-space encoding is algebraically equivalent to a sparse VQ concept-ID
  in logit-space; VQ concept training on substrate W should be cheap and fast.
Tier hint: CPU (Pythia-160M concept extraction + substrate Hebbian training; no GPU needed
  for substrate W; GPU only needed for one-time VQ codebook training pass).
Why now: ConceptLM (arXiv:2602.08984) and CoCoMix (arXiv:2502.08524) confirm discrete
  concept-level training is more sample-efficient than token-level; substrate can execute
  the same paradigm at inference scale; this is a 1-2 eng-day CPU experiment.
Pre-reg note: metric is concept-level perplexity (NOT token-level ppl); HARD-PASS <= 20,
  HARD-FAIL >= 40 at V_c=256 concept vocabulary on Wikitext-2 held-out.
3 composition lessons apply: same-axis collinear (use fixed random concept hypervectors);
  linear-W replay-incompatible (fixed codebook, no drift); metric-must-match-axis (concept ppl).

### 2. Phase 0.5 v1 Hyperprobe audit core

Anchor pointer: Phase 0.5 v1 audit (engineering deliverable; npz from Llama-3.2-1B expected)
Substrate-product reading: Establishes which LLM layers carry substrate-predictable signal.
  This is a PREREQUISITE for Option C geometry alignment (need target layer before training W_proj).
  Also prerequisite for C1/C2/C3 cornerstone dispatch at 8B scale.
Tier hint: GPU (Llama-3.2-1B inference needed to generate activations; then CPU for analysis).
Why now: npz already generated or near-generation; audit core is short (< 1 hr GPU); unblocks
  two downstream experiments.

### 3. EX1 Wikitext-2 char-level LM

Anchor pointer: EX1-revised (prior spec exists; awaits Wikitext-2 natural language confirmation)
Substrate-product reading: Smoke showed ppl=7.4 on synthetic counting task; Wikitext-2
  confirms whether substrate char-LM generalizes to natural language at substrate-class.
Tier hint: CPU (char-LM on N=8192, Wikitext-2; ~20-60 min per cell).
Why now: closes the largest uncertainty in the native-language perplexity ceiling.
Pre-reg from 3x drill: HARD-PASS ppl < 20, MIDDLE-BAND 20-60, HARD-FAIL > 60 on held-out.

### 4. Option C geometry alignment via B8 logit-bridge

Anchor pointer: New (no prior anchor); W_proj training from B8 logit-space to LLM residual
Substrate-product reading: B8 r=0.263 logit-space residual encoding is a geometry bridge
  between substrate and LLM activation space. One linear projection layer (~4M params at D=2048)
  is the ONLY training needed for Option C migration. This is the key technical enabler for
  direct substrate-to-LLM residual injection.
Tier hint: GPU (contrastive training on (substrate_retrieval, LLM_hidden) pairs from Hyperprobe npz;
  ~4-8 hrs GPU). Depends on anchor 2 completing first.
Pre-reg: HARD-PASS cos(W_proj * x_substrate, x_LLM) >= 0.60; HARD-FAIL <= 0.30.

### 5. Level 3 meta-LLM text injection smoke test

Anchor pointer: Level 3 smoke (new; builds on 5-corpus HP substrate artifact)
Substrate-product reading: Validates the full Option A+SQ2 product pipeline end-to-end.
  Frozen Llama-3.2-1B + substrate-retrieved context -> cross-domain QA accuracy.
  Pre-reg from Level3 drill: HARD-PASS >= 65% QA accuracy WITH context vs <= 30% without;
  HARD-FAIL <= 35% with context (no material lift).
Tier hint: GPU (~3-4 hrs; Llama-3.2-1B already loaded for Hyperprobe).
Why now: validates the primary near-term product claim; prerequisite for C1/C2/C3 dispatch.

---

## Context pointers (file paths)

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_llm_communication_and_native_concept_training_2x_2026-06-04.md
- Prior Level3 drill: d:/AI/hd-instrument/notes/research_drill_level3_meta_llm_over_substrate_aggregator_2x_2026-06-04.md
- Prior System1 drill: d:/AI/hd-instrument/notes/research_drill_substrate_system1_hybrid_architecture_2x_2026-06-04.md
- Prior 3x generative LM drill: d:/AI/hd-instrument/notes/research_drill_substrate_direct_generative_language_modeling_3x_2026-06-04.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Orchestrator post-compaction brief: d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md

---

## Contract

exp_dev designs and queues anchors 1-5 above per its own role contract (envelope-fail-bands,
smoke gate, queue_add.sh, post-ship REMOTE VERIFY). The rank order is the recommended dispatch
sequence but exp_dev may re-sequence based on queue depth, runner availability, and dependency
constraints (anchor 4 depends on anchor 2).

## Autonomy declaration

exp_dev decides ALL of: anchor names, N/K sweep grids, exact threshold values, queue choice
(CPU vs GPU), timeout formulas, and cap_map pre-decisions. This file provides strategic
context and WHY, not HOW.
