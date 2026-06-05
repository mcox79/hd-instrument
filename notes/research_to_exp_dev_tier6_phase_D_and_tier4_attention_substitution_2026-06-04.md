# Research -> Exp-Dev: Tier 6 Phase D probe + Tier 4 Hopfield-attention substitution (substrate intrinsic LLM training gap)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + Testbed
**Date:** 2026-06-04
**Subject:** Substrate-intrinsic LLM training is the under-prioritized strategic gap. Two cheap empirical tests fill it. Both use substrate's empirically validated bio-primitives + don't depend on Llama v6 hang.

---

## Strategic context

Today's scorecard shows substantial substrate-class brain-training work (12 validated bio-primitives + capacity multiplicative HP) but ALMOST NO empirical Tier 4/6/7 work for substrate AS INTRINSIC PART OF LLM TRAINING.

User strategic framing 2026-06-04: "vastly increase LLM training time [speed] + make substrate intrinsic and vastly superior part of it"

Two cheap empirical tests fill the gap:

1. **Tier 6 Phase D probe** (spec'd 2026-06-03; never built) — substrate-hybrid 4-layer char-LM at Wikitext-2; substrate-Hebbian-attention layers + gradient output head
2. **Tier 4 Hopfield-attention substitution probe** — single attention layer swap in Pythia-160M scaffold

Both use validated bio-primitives. Both at substrate's existing empirical scale. Neither depends on Llama v6 hang.

---

## Cell 1: TIER 6 Phase D probe (substrate-hybrid LLM training)

**Anchor:** `substrate_tier6_phase_D_4layer_charLM_wikitext2_v1_n4096`

### Architecture (per 2026-06-03 Drill 3 spec; updated with today's bio-primitives)

```
4-layer character-level transformer-like architecture:

Layer 1-4: substrate-Hebbian-attention layer
  - Replace standard attention(Q, K, V) with substrate-Hebbian retrieval:
    - W += K @ V^T (Hebbian outer-product write; DeltaNet-class delta rule)
    - retrieve: V_predicted = W @ Q (substrate retrieval; iterated per Mode 4 if multi-step needed)
  - Add today's validated bio-primitives:
    - DG sparse-expansion f=0.02 on K, V (B2 HP)
    - cf-RPE NO (drill: inverts for generative)
    - Position-binding via multi-bank addressing (Bundle E E1 HP)
    - STDP-asymmetric write rule (Bundle E E2 HP)
    - D-ECR audit-preserving eviction at capacity boundary (B6 HP)

Output head: standard gradient-trained linear projection
Training: streaming through stacked substrate-Hebbian-attention; loss at output head only;
         gradient updates ONLY to output head + final layer norm
Corpus: Wikitext-2 character-level (~10MB)
Baseline comparison: identical architecture trained fully via gradient backprop
```

### Pre-reg HP/MID/HF (per 2026-06-03 Phase D + today's findings)

- **HARD-PASS:**
  - substrate-hybrid BPC <= 1.20x gradient-baseline BPC AND
  - wall-time training <= 0.5x gradient-baseline (2x speedup minimum) AND
  - audit primitives operational on substrate weights DURING training (substrate-novel claim)
- **MIDDLE:** BPC in [1.20, 2.0]x baseline OR wall-time speedup in [1.0x, 2x]
- **HARD-FAIL:** BPC > 2x baseline OR substrate-hybrid slower than gradient-baseline OR audit primitives non-operational

### WHY-DRILL on HF

- If BPC > 2x baseline: substrate-Hebbian attention not capturing enough structure; test with cf-RPE or position-binding individually first
- If wall-time slower than baseline: substrate-class N too large for layer-wise Hebbian; reduce N or use sparser variant
- If audit primitives broken: substrate W is being modified at training; deletion-cert needs at-rest test, not in-loop

### Resource

**Remote 4060 Ti GPU (NOT cloud).** 4-layer char-LM at substrate-class N=4096 fits 8GB easily. Per [[feedback-cloud-only-when-absolutely-necessary]]: cloud only when remote insufficient. Wikitext-2 char + 4 layers + N=4096 fits remote.

If Wikitext-2 loader still has HfUriError (per Exp-Dev's earlier note): use Shakespeare char-LM corpus as alternative (~5MB; tractable; standard fallback).

### Cost ceiling

$0 (remote 4060 Ti). Per-seed wall ~30-60 min. Total: ~1-3h for 3 seeds.

### Engineering scope

~1-2 eng-days:
- Substrate-Hebbian-attention layer (reuses Bundle E E1 + B2 DG sparse + STDP-asymmetric scaffolds)
- 4-layer char-LM scaffold (standard; reuse existing if available)
- Gradient output head (~1h)
- Wall-time measurement + comparison logic (~1h)
- Audit primitive validation during training (deletion cert at checkpoint; refusal cert from validation set; ~2h)

### P_deflated (per 2026-06-03 Drill 3)

P_algebraic = 0.55 (DeltaNet 1.3B precedent; today's bio-primitive validations)
P_implementation = 0.40 (4-layer substrate-Hebbian-attention scaffold is novel synthesis)
**Joint P = 0.22 for clean HP at >= 2x speedup; ~0.40 for MIDDLE-band BPC + speedup**

### Strategic outcome

**If HP:** substrate-hybrid LLM training validated empirically at small scale. Opens Phase E (Pythia-160M substrate-hybrid scale-up; ~$25-50). Substrate AS INTRINSIC PART of LLM training empirically anchored.

**If MIDDLE:** identifies which primitive(s) work; iterate before Phase E.

**If HF:** substrate-Hebbian attention at this configuration insufficient; specific WHY-DRILL fix paths.

---

## Cell 2: TIER 4 Hopfield-attention substitution probe

**Anchor:** `substrate_tier4_hopfield_attention_substitution_pythia160m_4layer_v1`

### Architecture (per 2026-06-03 Drill 2 spec)

```
Take Pythia-160M (12 layers); replace ATTENTION LAYER at layer 8 with substrate-Hebbian attention:
- Ramsauer 2020 modern Hopfield = transformer attention identity (P=0.95 algebraic)
- Substrate-Hebbian attention: W += K @ V^T per token
- Retrieval: softmax(Q @ W) or substrate-direct retrieval
- Other 11 layers UNCHANGED (standard transformer attention)

Training: 500 steps on Wikitext-2 char (just enough to characterize stability)
Measure: attention entropy at step 500; gradient norm variance ratio (substrate-layer vs other-layers)
```

### Pre-reg HP/MID/HF

- **HARD-PASS:**
  - Substrate-layer attention entropy > 50% of baseline attention entropy at step 500 AND
  - Gradient norm variance ratio (substrate vs other layers) < 8x AND
  - Final perplexity within 1.5x baseline
- **MIDDLE:** Entropy 25-50% of baseline OR gradient variance ratio 8-15x
- **HARD-FAIL:** Entropy collapse (< 25% baseline; substrate retrieval saturates) OR gradient ratio > 15x

### WHY-DRILL on HF

- If entropy collapse: substrate retrieval over-confident; add sparse-Modern-Hopfield (alpha-entmax) variant
- If gradient ratio > 15x: substrate layer training-incompatible; need pre-conditioning or W_proj alignment (per B8 logit-residual bridge insight today)

### Resource

**Remote 4060 Ti GPU OR cheap cloud H100 if Pythia-160M with substrate-attention doesn't fit 8GB.**

Pythia-160M baseline fits 8GB. Substrate-attention adds W matrix per layer (~N^2 floats = 16MB at N=2048; trivial). Should fit remote.

### Cost ceiling

$0 if fits remote. Otherwise cloud H100 ~$3-6 per cell; 30-60 min wall.

### Engineering scope

~4-6h:
- Pythia-160M loading + layer hook (~2h; reuse Phase 0.5 v1 scaffold if applicable)
- Substrate-Hebbian attention layer wrapper (~2h; reuse Bundle E E1 + B2 scaffolds)
- Wikitext-2 char training loop (~30 min)
- Entropy + gradient norm measurement (~1h)
- Per [[feedback-no-padding-experiments]]: targeted 500-step characterization, not full retraining

### P_deflated (per 2026-06-03 Drill 2 + Ramsauer identity P=0.95)

P_algebraic = 0.85 (Ramsauer identity is published theorem)
P_implementation = 0.55 (substrate-attention training stability is the unknown)
**Joint P = 0.47 for clean HP**

### Strategic outcome

**If HP:** substrate-as-attention-layer training-stable at Pythia-160M scale. Opens Tier 4 at scale (more layers swapped; production Pythia-160M with substrate-attention).

**If MIDDLE:** entropy collapse partial; sparse-Modern-Hopfield mitigation needed.

**If HF:** Tier 4 needs architectural refinement (pre-conditioning; alignment via B8 bridge; etc.).

---

## Priority + sequencing

**Build Cell 1 (Tier 6 Phase D) FIRST.** Reasons:
- P_deflated higher for MIDDLE-band outcome (~0.40)
- Wider empirical scope (BPC + wall-time + audit)
- Fewer external dependencies (no Pythia-160M loading)
- Pure substrate-Hebbian architecture (cleanest test of substrate-AS-LLM)
- Direct validation of training-speed product narrative

**Build Cell 2 (Tier 4) SECOND.** Reasons:
- Algebra confirmed (Ramsauer P=0.95); empirical-only question is stability
- Builds on Cell 1's substrate-Hebbian-attention scaffold
- Targeted 500-step test (smaller engineering)
- Validates substrate-as-attention-layer at small-LLM scale

---

## Why these two over other priorities

Current Priority 1 list (from scorecard):
1. EX-CONCEPT-1 REAL (BLOCKED on Pythia extraction; Testbed action)
2. Capacity scaling N=4096/N=8192 (running)
3. B5-bounded weights (cheap; queue)
4. SQ6-v2 cleanup (CPU)
5. Efficiency composition variants

**Cell 1 + Cell 2 fill the strategic gap (substrate intrinsic LLM training) that the user explicitly flagged as exciting.** They are EMPIRICALLY UNDER-PRIORITIZED relative to the substrate-class capacity work.

Per training-speed design space drill: substrate-hybrid at LLM scale is 24x realistic compound speedup; flagship product narrative. Without Cell 1 + Cell 2 empirical: no validation of this claim.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator + Testbed informed
- Per [[feedback-no-padding-experiments]]: 2 cells discriminate substrate-as-intrinsic-LLM-component hypotheses
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF with WHY-DRILL paths per cell
- Per [[feedback-cloud-only-when-absolutely-necessary]]: remote 4060 Ti for both cells if 8GB sufficient
- Per [[feedback-small-scale-first-methodology]]: 4-layer char-LM (Cell 1); 1 attention layer swap at Pythia-160M (Cell 2)
- ASCII-only

PROT-018: `_tier6_phase_d_v1` + `_tier4_hopfield_attention_v1`
PROT-021: source=remote 4060 Ti (or local CPU fallback), run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** Cell 1 (Tier 6 Phase D substrate-hybrid LLM training; ~1-2 eng-days + ~1-3h wall; $0 remote 4060 Ti) and Cell 2 (Tier 4 Hopfield-attention substitution at Pythia-160M; ~4-6h eng + 30-60 min wall; $0 remote OR ~$3-6 cloud if doesn't fit 8GB).

Per scorecard: these fill the substrate-INTRINSIC-LLM-training empirical gap (currently almost entirely untested while substrate-class brain-training has 12 validated bio-primitives). User strategic framing: "vastly increase LLM training time + make substrate intrinsic and vastly superior part of it."

Cell 1 priority over Cell 2 (cleaner test; broader scope; fewer dependencies).

Both don't depend on Llama v6 hang. Both use Wikitext-2 char-LM corpus (Shakespeare char-LM fallback if Wikitext loader still broken). Both fit remote 4060 Ti likely.

When verdicts land: scorecard + composition matrix updated per protocol. Standing for builds.

**Research session:** standing for Cell 1/Cell 2 verdicts + ongoing pipeline + ~20 min cadence.
