# Research -> Exp-Dev: N1b iterative-on-native + Tier 5 Arch 8 MVE additions

**From:** Research  **Date:** 2026-06-08 ~02:50  **Re:** User request to add (1) iterative
ablation on native substrate; (2) re-queue Tier 5 Arch 8 MVE (was in morning batch; not
picked up).

## Addition 1: N1b — Iterative ablation on native substrate

### Context
N1-N3 / R1-R3 already test SINGLE-PASS K-hop traversal on native substrate (parse full
question into roles → algebraic K-hop in one pass). User asked: should we also test
ITERATIVE-style on the native substrate?

### Anchor N1b: Per-hop parse + traverse on native substrate
- Substrate-product reading: same NER+relation extraction ingest as N1; but at query
  time, parse hop-1 first, traverse 1 hop, use intermediate result to parse hop-2,
  traverse second hop separately; ablation vs N1's single-pass full-question parse
- Tier: LOCAL CPU (~2-3 hr) — runs after N1 to enable comparison
- HARD-PASS: per-hop iterative matches single-pass within ±2pp (validates both work; pick cheaper)
- BORDER: per-hop -2 to -5pp (single-pass wins; clean signal lost per hop)
- HARD-FAIL: per-hop >-5pp worse than single-pass (iterative reformulation lossy even on
  clean bindings; single-pass is required)

### What HF means
If HF (per-hop iterative lossy even on clean substrate bindings), it confirms the
ACROSS-THE-BOARD hypothesis: iterative reformulation degrades signal regardless of
substrate quality. The 5 iterative HFs on fuzzy embeddings would extend to clean
bindings = iterative is a SIGNAL-DEGRADATION pattern, not a retrieval-quality pattern.

If HP, substrate iterative IS viable on clean bindings — opens agentic/multi-step
workflows on structured substrate (legal case-law iterative, medical differential
diagnosis iterative, etc.) as v2.0 capability.

## Addition 2: Tier 5 Arch 8 substrate-KV-cache MVE re-queue

### Context
Tier 5 substrate-intrinsic LLM was queued in morning batch handoff (2026-06-07
~21:45) but not picked up by Exp-Dev. Cycle 179 reported queues empty. Re-priority
this as foundational substrate-attention-backbone test for v3.0+ roadmap.

### Anchor T5-1: Pythia-160M Arch 8 substrate-KV-cache replacement MVE
- Substrate-product reading: replace one attention layer's KV-cache in Pythia-160M with
  substrate retrieval (Pattern B bindings as keys; binding payloads as values; modern
  Hopfield retrieval = attention computation per Ramsauer 2020 equivalence); evaluate
  on small benchmark (WikiText perplexity or HellaSwag)
- Tier: LOCAL GPU (~4-6 hr) OR LOCAL CPU (~12-24 hr)
- HARD-PASS: substrate-KV-cache Pythia-160M perplexity within 10% of standard Pythia-160M
  (substrate-as-attention bridge validated at minimum scale)
- BORDER: within 10-20% (works but needs tuning)
- HARD-FAIL: >20% perplexity degradation OR catastrophic failure (substrate-as-attention
  not viable at small scale; Tier 5 path requires fundamental rework)

### Strategic note
This is the FOUNDATIONAL Tier 5 test. If HP at Pythia-160M, Tier 5 substrate-intrinsic
LLM is empirically anchored as feasible direction; scale up to Pythia-1.4B or larger.
If HF, Tier 5 needs alternative architectures (cross-attention adapters, Tier-4.5
substrate-augmented attention instead of attention REPLACEMENT).

Combined with cycle 178's modern Hopfield production-confirmation (P/N=2 + β=0.5..64
hyperparameter-insensitive), the substrate-as-attention bridge has STRONG theoretical
backing; Pythia-160M MVE is the empirical anchor.

## Cross-references

- Native substrate multi-hop battery (N1-N3): notes/research_to_exp_dev_NATIVE_substrate_multihop_HotpotQA_2026-06-07.md
- Multi-hop CORRECTION (single-shot+attention IS production): notes/research_to_exp_dev_multihop_CORRECTION_works_via_single_shot_attention_2026-06-07.md
- Modern Hopfield production HP (cycle 178): notes/orchestrator_to_research_results_summary_2026-06-08_cycle178.md
- Tier 5 Arch 8 original morning batch routing: notes/exp_dev_handoff_research_overnight_2026-06-07_batch.md (Anchor T5)
- Ramsauer 2020 attention=Hopfield identity: notes/research_drill_field_modern_hopfield_5x_2026-06-07.md

---

**Exp-Dev:** authorize both anchors. N1b runs after N1 lands (ablation requires N1 baseline).
T5-1 is foundational Tier 5 MVE; ~4-6 hr GPU OR 12-24 hr CPU per resource availability.
Both fill clear capability gaps identified by user audit.
