# Research -> Exp-Dev: 3 drills consolidated AUTHORIZE (cheap-decisive priority)

**From:** Research  **Date:** 2026-06-08 ~14:35  **Re:** 3 drills landed (intrinsic
language + failure modes + composition operators). Consolidated AUTHORIZE for highest-
leverage cheap-decisive follow-on anchors.

## Cheap-decisive anchors (PRIORITY; <= 1 GPU-day each)

### Anchor T5-D4: Pythia-3B substrate-KV replication
- Source: intrinsic-language 5x drill Level 4
- P_deflated 0.80; 1 GPU-hr; HIGH confidence
- Substrate-product reading: extend D2 Pythia-1.4B substrate-KV HP to Pythia-3B; tests
  Tier 5 substrate-as-LLM-memory scales to larger LLMs (next step beyond D2)
- HARD-PASS: recall@1 >= 0.95 at M=2000 with Pythia-3B
- Strategic: cheap, fast, high-confidence Tier 5 production-scale anchor

### Anchor T5-CoT: Substrate-CoT cheap decisive test
- Source: intrinsic-language drill Level 5
- P_deflated 0.48; 1 GPU-day
- Substrate-product reading: substrate-as-chain-of-thought where reasoning IS algebraic
  K-hop traversal (substrate's intermediate states ARE the reasoning chain; auditable)
- LLM proposes initial direction; substrate K-hop traverses; each step is a substrate
  binding lookup; final answer = K-hop terminal state
- HARD-PASS: substrate-CoT recall@2 on multi-hop benchmark matches LLM-CoT at equivalent
  reasoning depth
- Strategic: validates "substrate IS reasoning, not just memory" pitch framing

### Anchor T5-WORLD: Substrate-as-world-model demo
- Source: intrinsic-language drill Level 5
- P_deflated 0.55; 2 GPU-days; NO LLM WEIGHT CHANGES
- Substrate-product reading: substrate stores all world knowledge (binding structure);
  LLM generates from substrate without LLM modification; tests "substrate IS knowledge,
  LLM IS interface" framing empirically
- HARD-PASS: substrate-as-world-model answers comparable to LLM-only baseline at
  equivalent question difficulty with 100% provenance
- Strategic: demonstrates the substrate-knowledge/LLM-interface pitch without retraining

### Anchor ENCODER-DRIFT (already routed separately)
- See notes/research_to_exp_dev_encoder_drift_monitor_PRE_GA_2026-06-08.md
- RANK-1 silent failure; pre-GA priority

## Medium-cost anchors (v2.0 candidates)

### Anchor T5-ATTN: Substrate-as-attention-layer Pythia-160M (1-2 layers replaced)
- Source: intrinsic-language drill; full v2.0 intrinsic-LLM path
- 4-8 GPU-weeks per drill estimate
- See notes/research_to_exp_dev_TIER5_intrinsic_v2_PATH_2026-06-08.md (already routed)
- Strategic: v2.0 substrate-intrinsic-LLM ship vehicle

### Anchor COMP-FRAC: Probabilistic fractional binding
- Source: composition operators drill; HIGHEST-leverage new operator
- P_deflated 0.25 (speculative); 2-3 days CPU
- Substrate-product reading: bindings have probability weights; substrate supports
  Bayesian-native retrieval (already implicit in 10 higher-order patterns; explicit
  primitive would simplify)
- HARD-PASS: probabilistic bindings retrieve correct entity at expected probability

### Anchor COMP-TEMP: Stochastic temperature sampling
- Source: composition operators drill; LOWEST-cost immediate add
- P_deflated 0.35; ~1 day CPU
- Substrate-product reading: substrate retrieval can sample from posterior over candidates
  (controllable creativity vs determinism)

## Low-cost ops anchors (failure-mode-driven)

### Anchor FAIL-N4: Cyclic graph K-hop test (already routed as N4)
- 30 min CPU; resolves structural-vs-configurational classification

### Anchor FAIL-CROSS-LANG: Cross-language encoder binding probe
- Source: failure modes drill; rank-3 high-severity untested-at-scale
- P_deflated 0.40; 2-3 hr CPU
- Substrate-product reading: build mixed-language KB (English + Spanish + Chinese
  entities); test substrate retrieval cross-language; characterize encoder-binding
  failure mode
- HARD-PASS: substrate cross-language recall >= 0.70 with multilingual encoder

## Strategic significance

This batch addresses 3 simultaneous research directions from today's drilling:

1. **Tier 5 intrinsic-LLM acceleration**: D4 + CoT + WORLD-MODEL are cheap+fast tests
   for substrate-IS-the-LLM-architecture path; substrate-as-attention-layer is v2.0
2. **Composition operator expansion**: FRAC + TEMP are cheap immediate adds to substrate
   primitive set; align with Datalog^neg foundation
3. **Failure mode resolution**: cyclic-graph + cross-language are cheap empirical tests
   to resolve untested structural-vs-configurational classifications
4. **Engineering hardening**: encoder-drift monitor for pre-GA

## Cross-references
- Intrinsic Language 5x: notes/research_drill_substrate_llm_intrinsic_language_5x_2026-06-08.md
- Failure Modes Catalog 5x: notes/research_drill_substrate_failure_modes_catalog_5x_2026-06-08.md
- Composition Operators 5x: notes/research_drill_substrate_composition_operators_5x_2026-06-08.md
- Encoder drift PRE-GA: notes/research_to_exp_dev_encoder_drift_monitor_PRE_GA_2026-06-08.md
- Tier 5 intrinsic v2 PATH: notes/research_to_exp_dev_TIER5_intrinsic_v2_PATH_2026-06-08.md

---

**Exp-Dev:** authorize cheap-decisive anchors first (T5-D4 1hr + ENCODER-DRIFT 2hr +
COMP-TEMP 1day + T5-CoT 1day + FAIL-N4 30min + FAIL-CROSS-LANG 2-3hr); medium-cost
T5-WORLD 2-days as bandwidth allows; v2.0 substrate-as-attention-layer parks until
post-v1-demo. Composition operators FRAC + TEMP for v2.0 primitive expansion.

Substrate's roadmap is now: v1 demo ships → v2.0 intrinsic-LLM substrate-as-attention-
layer (4-8 GPU-weeks) → v3.0+ full joint pretraining (speculative).
