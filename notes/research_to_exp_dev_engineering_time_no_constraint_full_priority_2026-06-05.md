# Research -> Exp-Dev: User -- engineering time is not a concern; reorienting priorities

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~08:45
**Subject:** User explicitly stated engineering time is not a constraint. Reorienting priorities accordingly. Both GPU-OPT-1 + CONT-LRN-1 are full-priority parallel builds. Plus surfacing other engineering-heavy work I had implicitly deferred.

---

## Reorientation

User feedback: "engineering time is not a concern"

What I should change: stop using engineering-time as a deprioritization axis. Prioritize cells based on empirical/strategic value only. Build aggressively across all valuable cells.

What this changes:

**Previous priority (GPU-OPT-1 vs CONT-LRN-1):** I recommended CONT-LRN-1 first because "lower engineering time." That was wrong framing.

**Corrected priority:** BOTH are full-priority. Build in parallel.

- CONT-LRN-1 (continual learning empirical 10^9x validation) -- builds NOW
- GPU-OPT-1 (substrate-specific GPU kernels vs torch.compile baseline) -- builds NOW

---

## Engineering-heavy work I was implicitly deferring (now in scope)

### Cell FULL-PYTHIA-1: Substrate-attention at ALL Pythia-160M attention layers (not just one)

**Anchor:** `substrate_full_pythia160m_all_attention_layers_substituted_v1`

Current: Tier 4 substituted ONE attention layer in Pythia-160M (HP at smoke).
Missing: substrate-attention at ALL layers -- full substrate-LLM at Pythia-160M scale.

### Architecture
- Pythia-160M scaffold
- Replace ALL transformer attention layers with substrate-Hebbian attention
- Keep FFN layers gradient-trained
- Train 5000 steps on Wikitext-2 char (or Shakespeare fallback)

### Pre-reg
- HP: full-substrate-attention Pythia-160M perplexity within 1.3x baseline + audit primitives operational throughout
- MID: ppl in [1.3, 2.0]x baseline OR audit primitives partial
- HF: ppl > 2x baseline OR audit primitives fail

### Cost + wall
- Engineering: ~2-3 days (significant; full LLM scaffold modification)
- Compute: ~2-4h cloud H100; $5-20

### Strategic
Validates substrate-as-FULL-LLM-attention at Pythia-160M scale, not just single-layer substitution. End-to-end substrate-attention LLM is the architectural completion of the substrate-as-intrinsic-LLM-component story.

---

### Cell CROSS-MODAL-1: Substrate cross-modal empirical test (vision + audio + text)

**Anchor:** `substrate_cross_modal_unified_binding_v1`

Current: modality-agnostic claim is ALGEBRAIC only (VSA binding works on any modality structurally).
Missing: empirical test that substrate handles vision + text + audio together.

### Architecture
- Substrate stores patterns from 3 modalities (CIFAR patches; spectrogram patches; text tokens)
- Bind each modality with modality-role-vector
- Test: cross-modal retrieval (query in modality A returns relevant patterns in modality B)
- Algebraic prediction: should work natively per VSA binding

### Pre-reg
- HP: cross-modal retrieval >=70% accuracy at substrate-class scale
- HF: <30% (substrate is unimodal-locked at empirical scale)

### Cost + wall
- Engineering: ~1-2 days (multimodal data prep + 3-modality substrate scaffold)
- Compute: $0 CPU; ~30-60 min wall

### Strategic
First empirical anchor for substrate's modality-agnostic claim. If HP: substantiates multi-modal product narrative.

---

### Cell LLAMA-1B-1: Substrate-attention scale-up to Llama-3.2-1B

**Anchor:** `substrate_tier4_pythia_to_llama32_1b_scale_up_v1`

Current: Tier 4 HP at Pythia-160M (one layer substituted).
Missing: scale-up to next-tier LLM (Llama-3.2-1B; 8x parameters).

### Architecture
- Llama-3.2-1B scaffold
- Replace ONE attention layer with substrate-Hebbian attention (matches Tier 4 pattern)
- Train 5000 steps on Wikitext-2 char
- Compare ppl_ratio + entropy_ratio + grad_ratio vs Pythia-160M baseline

### Pre-reg
- HP: substrate-attention at Llama-1B layer matches or exceeds Pythia-160M layer (scale-up preserves substrate-as-attention)
- MID: substrate-attention degrades 1.5-2x at scale-up
- HF: substrate-attention fails at Llama-1B scale (architecture doesn't scale)

### Cost + wall
- Engineering: ~3-5 days (Llama-1B scaffolding; substrate-attention adaptation for larger hidden dim)
- Compute: ~$500-2000 cloud H100

### Strategic
Tests scale-up of substrate-as-attention from 160M to 1B parameter regime. If HP: substrate-attention generalizes across LLM scales. Next gate before Llama-3.1-8B tier.

---

### Cell MULTI-LAYER-TIER4-1: Substrate-attention at MULTIPLE Pythia layers

**Anchor:** `substrate_tier4_multi_layer_substitution_v1`

Current: Tier 4 substituted ONE attention layer (HP).
Missing: 2, 4, 6, 8, 12 layers substituted (sweep).

### Architecture
- Pythia-160M
- Sweep: substitute 1, 2, 4, 6, 8, 12 of 12 attention layers with substrate-Hebbian attention
- Train 500 steps each
- Measure: ppl_ratio + entropy_ratio + grad_ratio per substitution count

### Pre-reg
- HP: ppl_ratio stays within 1.5x baseline up to 6 substituted layers
- MID: degradation starts at 4-6 layers
- HF: ppl_ratio > 2x at 4 layers (substrate-attention doesn't compose across layers)

### Cost + wall
- Engineering: ~1 day (sweep automation)
- Compute: ~$5-20 cloud H100 total

### Strategic
Tests how substrate-attention composes across multiple Pythia layers. If HP: substrate-attention can replace majority of LLM attention without quality collapse.

---

## Reorienting priority order

With engineering time NOT a constraint:

**Tier 1 (highest empirical / strategic value; build NOW in parallel):**
1. **CONT-LRN-1** -- 10^9x continual learning claim validation; $5-20 + 1 day eng
2. **GPU-OPT-1** -- substrate GPU optimization vs torch.compile baseline; $0 + 4-8h eng
3. **MULTI-LAYER-TIER4-1** -- substrate-attention sweep across Pythia layers; $5-20 + 1 day eng
4. **CROSS-MODAL-1** -- substrate multi-modal empirical anchor; $0 + 1-2 days eng

**Tier 2 (build after Tier 1 lands; depends on Tier 1 verdicts):**
5. **FULL-PYTHIA-1** -- substrate-attention at ALL Pythia layers (full substrate-LLM); $5-20 + 2-3 days eng
6. **LLAMA-1B-1** -- substrate-attention scale-up to Llama-3.2-1B; $500-2000 + 3-5 days eng

**Tier 3 (Testbed-gated; not engineering-bottlenecked):**
- CCC-1 REVISED-v2 (per-token Pythia + KG/QA datasets gated)
- CCC-1-EXTRA KG (KG/QA datasets gated)
- EX-CONCEPT-1 REAL (per-token Pythia gated)
- Medical Path Y UMLS prototype (UMLS license gated)

---

## Strategic frame

User's directive ("engineering time is not a concern") means we should be aggressive on empirical breadth. The empirical map gets deeper coverage faster.

What we get with Tier 1 (~1-2 weeks engineering parallel; ~$20-50 cloud):
- Continual learning claim empirically validated (or refuted; either is informative)
- GPU optimization claim addressed honestly
- Substrate-attention multi-layer composition characterized
- Multi-modal substrate empirically anchored

What we get with Tier 2 (~1-2 months parallel; ~$500-2k cloud):
- Substrate-as-FULL-LLM at Pythia-160M (end-to-end intrinsic substrate-LLM)
- Substrate-attention at 1B scale (next-tier LLM)

This is the engineering scope user is enabling. Substantially expanded vs my conservative routing earlier.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per user 2026-06-05 ~08:45: engineering time NOT a deprioritization axis
- Per [[feedback-no-padding-experiments]]: each cell tests distinct strategic empirical gap
- Per [[feedback-cloud-only-when-absolutely-necessary]]: all Tier 1 + Tier 2 cells are minimum-viable-cost; Llama-1B is justified by scale-up
- ASCII-only

---

**END.**

**Exp-Dev:** 6 cells reorganized into 3 tiers. Tier 1 (4 cells) builds in parallel NOW with full priority. Tier 2 (2 cells) builds after Tier 1 verdicts. Engineering time NOT a constraint per user.

**User:** substantially expanded engineering scope authorized. ~1-2 weeks of parallel engineering covers Tier 1 (continual learning + GPU optimization + multi-layer Tier 4 + cross-modal). Plus Testbed-gated cells (CCC-1 REVISED-v2; Medical Path Y) when authorized actions complete.
