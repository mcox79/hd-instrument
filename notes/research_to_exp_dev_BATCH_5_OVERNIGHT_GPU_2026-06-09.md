# Research -> Exp-Dev: BATCH 5 OVERNIGHT GPU — 30+ experiments

**From:** Research  **Date:** 2026-06-09 ~14:30 UTC
**Re:** User direction (about to sleep) — load Exp-Dev queue with overnight GPU experiments.

## Tier 5c Path A follow-ups (architecture demo claim deepening)

### GPU-T5C-1: 3-layer Flamingo at Pythia-160M
- Substrate-product reading: does adding L4+L5+L6 (3 layers) improve over 2-layer baseline (0.836x)?
- HARD-PASS: ppl ratio < 0.836 (improvement) + stable training

### GPU-T5C-2: 4-layer Flamingo at Pythia-160M
- L4+L5+L6+L7 — saturation vs continued improvement
- HARD-PASS: ppl ratio < 4-layer test continues improvement OR saturation identified

### GPU-T5C-3: 6-layer Flamingo at Pythia-160M
- L3-L8 — half the layers
- HARD-PASS: characterize layer count vs improvement curve

### GPU-T5C-4: Every-layer rectangular at Pythia-160M
- KBLaM pattern at architecture level (not full KBLaM retrieval; just architecture)
- HARD-PASS: ppl ratio characterized vs 2-layer baseline

### GPU-T5C-5: Layer position L8+L9 Pythia-160M (late position)
- vs L4+L5 middle
- HARD-PASS: position-ablation curve

### GPU-T5C-6: Layer position L2+L3 Pythia-160M (early position)
- vs L4+L5 middle
- HARD-PASS: complete position ablation

### GPU-T5C-7: Pythia-1.4B 2-layer Flamingo
- Scale Pythia path A to larger size
- HARD-PASS: ppl ratio < 1.0 at Pythia-1.4B (confirms scaling)

### GPU-T5C-8: Qwen-2.5-3B Flamingo (Path A scaling)
- Same recipe as Qwen-1.5B (L12+L13); extend to 3B
- HARD-PASS: ppl ratio < 1.0 at Qwen-3B

### GPU-T5C-9: Llama-3.2-3B Flamingo (cross-family validation)
- Third LLM family (after Pythia + Qwen)
- HARD-PASS: ppl ratio < 1.0 confirms cross-family Path A claim

## Path A mechanism testing (per mechanism drill)

### GPU-MECH-1: Random-substrate baseline
- Replace substrate retrievals with random vectors; train normally
- HARD-PASS for substrate-real-helps: random shows < 5% improvement (real shows 15-17%); falsifies regularization-only hypothesis

### GPU-MECH-2: Sequence-length sweep
- 256 / 512 / 1024 / 2048 sequence lengths
- HARD-PASS: improvement grows with seq length → extended-context hypothesis confirmed

### GPU-MECH-3: Gate dynamics logging
- Log gate value per token + per layer during inference
- HARD-PASS: gate dynamics correlate with token-specific information content

## Path B variation tests (per variations drill anchors)

### GPU-PATHB-1: Zero-training K/V prefix injection
- Inject substrate K/V at sequence start; no training; inference-only
- HARD-PASS: held-out fact recall > 0.25 (cheap path; P_deflated=0.48)

### GPU-PATHB-2: PP-107 algebraic gate substitution
- Replace learned gate with substrate's PP-107 confidence; no gradient on gate
- HARD-PASS: ppl ratio maintained + categorical preservation (substrate-unique)

### GPU-PATHB-3: FHRR-native adapter
- Use substrate's FHRR Wirtinger differentiability as adapter (vs dense)
- HARD-PASS: held-out recall ≥ 0.40 + gradient flow validated

### GPU-PATHB-4: K-hop multi-step retrieval
- Substrate provides K-hop chain (not single fact) per query
- HARD-PASS: multi-hop benchmark improvement over single-fact baseline

### GPU-PATHB-5: Discriminative re-de-risk (DBpedia entities)
- KBLaM pattern with REAL DBpedia entities (per Exp-Dev's diagnosis)
- HARD-PASS: held-out ≥ 0.40 (architecture validated; substrate-unique preservation testable next)

## Programmable routing pre-tests (per routing drill)

### GPU-ROUTE-1: 2-source Pythia-160M learned gate
- 2-source attention (self + substrate) with learned gate per layer
- HARD-PASS: > 5% ppl improvement over 1-source baseline (gates engineering cost)

### GPU-ROUTE-2: Fixed vs learned gate ablation
- Externally-controlled fixed gates vs learned gates
- HARD-PASS: external control achieves > 70% of learned-gate improvement

### GPU-ROUTE-3: Multi-tenant isolation correctness check
- Gate_weight = 0 → exact algebraic isolation; verify no leak
- HARD-PASS: 0% leakage on 1000-query cross-tenant test

## Substrate-augmented benchmarks (categorical demo claims)

### GPU-VER-1: VER-MMLU substrate-augmented
- Qwen-1.5B + substrate vs gpt-4o-mini bare on MMLU knowledge subset
- HARD-PASS: substrate-augmented Qwen-1.5B ≥ gpt-4o-mini bare

### GPU-VER-2: VER-GSM8K substrate-augmented
- Qwen-1.5B + substrate (math facts) vs Qwen-1.5B bare
- HARD-PASS: substrate-augmented ≥ +10pp

### GPU-VER-3: VER-TRIVIAQA substrate-augmented
- 500 TriviaQA questions; substrate-augmented Qwen
- HARD-PASS: ≥ 0.85 (vs Qwen bare ~0.70)

### GPU-VER-4: B4 substrate+small-LLM vs gpt-4o-mini head-to-head
- 100 mixed-domain questions; full comparison with cost ticker
- HARD-PASS: substrate-augmented Qwen-1.5B wins ≥ 50% knowledge tasks at <100x cost

### GPU-VER-5: Substrate + Llama-3.2-3B vs gpt-4o-mini
- Cross-family substrate-augmented comparison
- HARD-PASS: substrate-augmented Llama-3B beats gpt-4o-mini on knowledge tasks

## Substrate scaling extensions

### GPU-SCALE-1: Latency at 100M facts (extends PP-150)
- HARD-PASS: P95 < 5ms at 100M (extrapolates O(1))

### GPU-SCALE-2: Latency at 200M facts
- HARD-PASS: P95 < 10ms

### GPU-SCALE-3: Latency at 500M facts (stretch)
- HARD-PASS: P95 < 50ms (still O(1)-like)

### GPU-SCALE-4: Cyclic K-hop at 1M entities (extends PP-161 + PP-177)
- HARD-PASS: recall ≥ 0.90 at 1M entities; termination=1.000

### GPU-SCALE-5: Encoder drift critical radius (per emergent-scale drill)
- 10M facts; simulate 6 months drift; identify critical radius
- HARD-PASS: critical drift radius identified (anchors production maintenance cadence)

## Substrate compression at production scale

### GPU-COMPRESS-1: 1-bit substrate at 100M facts (extends PP-200)
- 1-bit storage at 100M production scale
- HARD-PASS: 1-bit quality matches float32 ± 0.03 at 100M

### GPU-COMPRESS-2: 1-bit substrate retrieval latency at 100M
- HARD-PASS: P95 < 1ms with 1-bit + 100M facts

## Tier 5c v2.0 architectural exploration

### GPU-T5C-V2-1: Substrate-conditioned softmax (cycle 199 PP-191 follow-up)
- Substrate atom-vocabulary distributions bias LLM output logits at generation
- HARD-PASS: ≥ 30% hallucination reduction vs unconditioned baseline on TriviaQA

### GPU-T5C-V2-2: Semantic positional encoding (substrate as RoPE replacement)
- Replace standard RoPE with substrate-derived semantic positional encoding
- HARD-PASS: perplexity within 20% of RoPE baseline + substrate-positional shows position-aware retrieval

### GPU-T5C-V2-3: Substrate-augmented context window (virtual tokens per layer)
- Substrate provides virtual context tokens visible to attention
- HARD-PASS: effective context > nominal context window

## Sequencing recommendation

**Highest priority (Path A deepening):**
- GPU-T5C-1/2/3 (layer count saturation)
- GPU-T5C-5/6 (layer position ablation)
- GPU-T5C-7/8/9 (scale up + cross-family)
- GPU-MECH-1 (random baseline; mechanism falsification)

**Next priority (Path B alternatives if KBLaM fails):**
- GPU-PATHB-1 (zero-training prefix; cheap)
- GPU-PATHB-2 (PP-107 gate substitution)
- GPU-PATHB-5 (discriminative re-de-risk)

**Then (categorical demo claims):**
- GPU-VER-1/2/3/4/5 (substrate-augmented benchmarks)

**Stretch (scaling + compression):**
- GPU-SCALE-1/2/3/4/5
- GPU-COMPRESS-1/2

**v2.0 exploration (low priority):**
- GPU-T5C-V2-1/2/3

## Strategic intent

This batch GIVES EXP-DEV PLENTY OF OVERNIGHT GPU WORK:
- Path A 9 deepening anchors (layer count + position + scale + cross-family + mechanism)
- Path B 5 alternative anchors
- Programmable routing 3 pre-tests
- 5 substrate-augmented benchmarks (categorical demo)
- 5 scaling anchors
- 2 compression anchors
- 3 v2.0 exploration anchors

**Total: 32 GPU anchors** prioritized for overnight execution.

Per Exp-Dev's autonomy: queue runners drain as authorized; pre-flight checklist applies;
use experiments/_stream.py for long cells; foreground timeout patterns; resume capability
mandatory for anything > 5 min.

## Cross-references
- Path A SHIPPED: notes/exp_dev_to_research_PATH_A_SHIPPED_2026-06-09.md
- Path A mechanism drill: notes/research_drill_path_a_mechanism_5x_2026-06-09.md
- Path B variations drill: notes/research_drill_path_b_variations_5x_2026-06-09.md
- Programmable routing drill: notes/research_drill_programmable_attention_routing_5x_2026-06-09.md
- Emergent extreme-scale drill: notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md
- BATCH 3/4 (prior CPU + GPU): notes/research_to_exp_dev_BATCH_3_FRESH_30_ANCHORS_2026-06-08.md + BATCH_4_CRITICAL_2026-06-08.md

---

**Exp-Dev:** 32 GPU anchors. Load the overnight queue. User explicitly directed "shit ton of
GPU experiments" before going to sleep. Pre-flight hardening + checkpoint persistence per
established discipline. Prioritize Path A deepening + Path B alternatives + categorical
substrate-augmented benchmarks; scaling and v2.0 exploration are stretch.

Standing for results in the morning.
