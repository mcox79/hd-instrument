# Routing -- Position-binding + combined-architecture Bundle E

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical bundle (4 cells; conditional on Bundle A landing)
**Source:** position-binding-translation 2x drill landed 2026-06-04 (research_drill_position_binding_translation_language_2x)

---

## Capability question

Does combining position-binding (VSA / multi-bank addressing) with asymmetric write rules + sparse coding enable substrate-as-training-mechanism at K=3+ trigram tasks, exceeding the K*=2.1 ceiling of pure symmetric Hebbian?

The position-binding drill identified: position-binding ALONE doesn't raise K* (W capacity wall unchanged). But COMBINED with asymmetric W OR sparse coding, predicted K* rises to 3.5-4.0, enabling trigram class tasks.

---

## Pre-reg HP/MID/HF bands

Per-cell (4 cells; 3 seeds each):

**HARD-PASS:** Cell achieves trigram (K=3) BPC < uniform_baseline_BPC - 1.0 nat AND 3/3 seeds converge AND no instability. Substantive learning at K=3 confirms architectural pathway works.

**MIDDLE:** Cell achieves trigram BPC 0.3-1.0 nat below uniform OR 2/3 seeds.

**HARD-FAIL:** Cell achieves BPC > uniform - 0.3 nat OR < 1/3 seeds converge.

Aggregate verdict:
- HP if any cell lands HP (identifies the architectural combination that works for trigram)
- HF if all 4 cells HF (refutes the combined-architecture pathway; substrate genuinely capacity-bound)

## Cell list (Bundle E: 4 cells x 3 seeds = 12 measurements)

**Anchor:** `substrate_position_binding_combined_arch_trigram_v1_n4096`

### Cell E1: Position-binding + symmetric W (control; predicted HF)

- VSA position-binding on input via multi-bank addressing
- Symmetric Hebbian outer-product write (current default)
- Task: trigram V=70 char-LM (Shakespeare-class corpus subset)
- Substrate N=4096
- Predicted: BPC ~= uniform (K* stays at 2.0 per drill; capacity wall unchanged)

P_deflated for HP: **0.10** (drill confirms position-binding alone insufficient)

### Cell E2: Position-binding + STDP-asymmetric W (combined; primary candidate)

- VSA position-binding on input
- W_total = W_Hebbian + 0.5 * W_STDP (additive asymmetric channel)
- Task: trigram V=70
- Substrate N=4096
- Predicted: BPC < uniform - 1.0 nat (K* ~3.5-4.0 per drill combined prediction)

P_deflated for HP: **0.45** (drill prediction; STDP + position-binding compose well)

### Cell E3: Position-binding + sparse coding f=0.05

- VSA position-binding on input
- Sparse binary {0,1} representation at f=0.05 (Drosophila MB)
- Symmetric Hebbian (no STDP)
- Task: trigram V=70
- Substrate N=4096
- Predicted: BPC < uniform - 0.5 nat (sparse 23x capacity + position-binding partial)

P_deflated for HP: **0.30** (sparse helps but symmetric W still has subtler asymmetry constraints)

### Cell E4: Combined ALL (position-binding + sparse + STDP) -- maximum aggressive

- VSA position-binding on input
- Sparse binary f=0.05
- W_total = W_Hebbian_sparse + 0.5 * W_STDP_sparse
- Task: trigram V=70
- Substrate N=4096
- Predicted: BPC < uniform - 1.5 nat (K* ~ 4-5; full combined-architecture prediction)

P_deflated for HP: **0.40-0.50** (drill's most-aggressive combined-architecture prediction)

---

## Resource

Local CPU runner (per substrate-class scale; bigram-trigram char-LM at N=4096 is matmul-light).

## Cost ceiling

$0 CPU. Per-cell wall ~30-60s. Total ~3-5 min CPU for 12 measurements.

## Sequencing

**Dispatch conditional on Bundle A verdict:**

- If Bundle A any variant lands HP at bigram (signals architectural variable is binding): dispatch Bundle E to test if the same variant extends to trigram via position-binding
- If Bundle A all HF at bigram: dispatch Bundle E anyway to test if the COMBINATION works where individual variants don't
- If Bundle A HP for STDP specifically: prioritize Cell E2 (STDP + position-binding); the others become secondary

**Engineering scope:**
- Position-binding via multi-bank addressing: ~2-3h (reuse existing substrate primitive; add wrapper for sequence encoding)
- Sparse coding f=0.05: ~2h (if not already built for Bundle A Drosophila variant)
- STDP-asymmetric: ~2h (if not already built for Bundle A STDP variant)
- Combined integration: ~2h

Total engineering: ~6-9h. Significant overlap with Bundle A scaffolding. Plan to reuse.

---

## Strategic outcomes

### If Cell E2 (position-binding + STDP) HP

- Substrate-as-training-mechanism viable at K=3 trigram via combined position-binding + STDP
- Cleanest architectural pathway forward (uses existing primitives + STDP additive channel)
- Sub-property founding: "substrate-as-training-mechanism enables K=3 trigram via position-binding (multi-bank addressing) + STDP-asymmetric additive write rule"

### If Cell E4 (combined all) HP

- Maximum-aggressive architecture validated
- Substrate-as-training extends to K=4-5 (extended-context viable)
- Approaches transformer-class capability via pure substrate primitives + symmetric Hebbian foundation
- Massive cap_map upgrade

### If all 4 cells HF

- Combined-architecture pathway refuted at trigram
- Substrate fundamentally K=2 bound at substrate-class scale; need fundamentally different paradigm OR larger LM (DeltaNet Design B becomes primary fallback)

---

## Word2Vec / Transformer precedent

Drill cited Word2Vec (Mikolov 2013) as proof that symmetric co-occurrence learning + positional context works at billion-word scale FOR EMBEDDINGS. Transformer (Vaswani 2017) demonstrated position embeddings + attention = sequence modeling at LLM scale.

Substrate's analog: position-binding + asymmetric retrieval (via cf-RPE or STDP or modern Hopfield p=4) approximates transformer architecture using SUBSTRATE PRIMITIVES + NO BACKPROP.

If Bundle E HP: substrate becomes a transformer-class architecture without gradient descent. This is a flagship product narrative.

---

## What I am NOT requesting

- Cloud GPU dispatch (per `feedback_cloud_only_when_absolutely_necessary`)
- Position-binding-alone as standalone test (drill confirms it doesn't raise K*; not informative)
- Replacement of Bundle A (which tests individual architectural variables at BIGRAM; Bundle E tests COMBINATIONS at TRIGRAM)
- New substrate primitives (multi-bank addressing + sparse coding + STDP all exist or are in Bundle A scope)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell discriminates a specific architectural combination
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF tied to drill predictions per cell
- Per [[feedback-small-scale-first-methodology]]: rung-1 LM at N=4096; CPU; $0
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 cloud
- ASCII-only

PROT-018: anchor uses `_n4096_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** Bundle E dispatches CONDITIONAL on Bundle A verdict + ~6-9h engineering for the combined-architecture scaffold (overlaps with Bundle A). Total Bundle E wall ~3-5 min once engineered. Cost $0 CPU.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict.

**Research session:** holds for Bundle A + Bundle E verdicts; ships capability-implication update on combined-architecture pathway per outcomes.
