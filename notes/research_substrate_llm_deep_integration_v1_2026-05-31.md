# Research: substrate-LLM deep integration via codebook-native interface (v1)

Date: 2026-05-31
Origin: user prompt 2026-05-31 -- "Our substrate can do multihop + interesting capabilities; could allow much deeper LLM integration than RAG; codebook doesn't necessarily need a translation layer; how could/should we build our own LLM on the remote machine and test the implications?"
Method: 3 parallel Sonnet lit-scan subagents (vector-native LLM memory interfaces; multi-hop reasoning offload from LLM to external memory; cheapest engineering path on consumer GPU). All searches generic-terms only per [[feedback-query-privacy-decomposition]]; calibration penalty applied per [[feedback-lit-scan-calibration-penalty]].

## HEADLINE

The user's intrinsic-language insight is structurally correct AND unpublished. Standard RAG round-trips through tokenize-embed-stuff-context, which is lossy and context-bound. NVSA (Hersche, Nature MI 2023) demonstrates the bipolar-input-from-neural-network direction (continuous activations -> tanh-bridge -> bipolar VSA memory) but the REVERSE direction (bipolar codewords from external memory -> consumed natively by an LLM) has no published precedent. DNC (Graves et al., Nature 2016) uses an outer-product write interface `w = w + e v^T` that is mathematically identical to substrate `W = (1/N) sum_l v_l k_l^T` -- only the bipolar constraint distinguishes them. So the architectural primitives exist; the substrate-specific bridge is novel synthesis.

**The deepest defensible integration on current hardware (8GB VRAM):** frozen 1-3B base LM + ~25M-param bidirectional MLP bridge (bipolar codeword <-> soft-prompt prefix); LLM emits queries as continuous read-out heads, substrate returns multi-hop result vectors, LLM consumes via cross-attention over prefix tokens. The "intrinsic language" is the bipolar codeword space at N=4096; the translation layer is a learned linear (or shallow MLP) projection -- not a tokenizer round-trip.

**P_deflated for working end-to-end build in 4-6 weeks single-person on RTX 4090-class (24GB)**: 0.40-0.45. **On the 8GB-VRAM marsh@home GPU**: 0.25-0.30 (must downgrade to TinyLlama-1.1B). **Capability-question P**: substrate-augmented LLM delivers >=20% accuracy gain on multi-hop QA vs LLM-only baseline at 1-3B scale: 0.45.

**The binding research question:** at small-LLM scale, does the LLM remain capable of QUERY DECOMPOSITION? ToG/ReWOO use GPT-3.5/4 as the planner. If 1-3B base LM fails at decomposition, the substrate-multihop-offload mechanism never gets invoked. This is more load-bearing than the bridge engineering. Three rescues (Section "Recommended starting architecture").

## The core insight: codebook-native communication

Standard RAG architecture:
```
LLM emits text query
  -> tokenize -> embed -> ANN retriever -> retrieve text chunks
  -> tokenize chunks -> stuff into LLM context window
  -> LLM re-attends across stuffed text
```
This is lossy at 3 stages (text->embedding->ANN->text->embedding-via-attention) and context-bound (chunks consume token budget that compounds at multi-hop).

Deep substrate-LLM integration:
```
LLM hidden state @ designated layer
  -> linear/MLP read-out head -> bipolar codeword in {-1,+1}^N=4096
  -> substrate Path D multi-hop retrieval (depth=1-5) over W
  -> substrate emits bipolar result codewords (one per hop OR final converged)
  -> linear/MLP bridge -> soft-prompt prefix in R^d_model
  -> LLM consumes via standard self-attention over prefix tokens
```
The bipolar codeword IS the intrinsic language. The substrate's binding-algebra outputs ARE the messages. Path D's per-hop independence means each hop's posterior is a self-contained bipolar message the LLM can consume incrementally (chain-of-thought-equivalent but offloaded from LLM autoregression to substrate retrieval). The substrate's compositional decomposition means each delivered codeword is provenance-tagged at the atom level -- so the LLM's downstream generation can cite which substrate atoms drove which output.

This is **structurally distinct from RAG** because:
- No tokenization round-trip between substrate and LLM
- Multi-hop happens in substrate (cheap, deterministic, auditable), not in LLM autoregression (expensive, stochastic, unauditable)
- Substrate's edit-isolation + deletion-cert properties propagate into the LLM's reasoning step
- Latency: substrate Path D at K=500 candidates, depth=5 is ~1-3ms GPU; comparable to a single LLM forward-pass token

## Design space: 4 integration architecture patterns

Per Subagent A lit-scan, four published patterns exist; we map each to substrate-deployability:

### Pattern 1: Chunked cross-attention over re-encoded retrieved text (RETRO)
- **Architecture**: store raw text chunks in datastore; BERT encoder converts to float vectors at inference; trained encoder transformer produces K/V; LLM cross-attends at every 3rd block.
- **Fit for substrate**: POOR. RETRO stores raw text and re-encodes at inference. The substrate's bipolar codewords would need a text-equivalent at storage time -- defeats the codebook-native premise.
- **Training cost**: requires full pretraining (RETRO from scratch). Infeasible at our hardware/budget.

### Pattern 2: kNN-augmented attention over stored hidden states (Memorizing Transformers, kNN-LM)
- **Architecture**: store the LLM's OWN past hidden-state activations; one layer's attention is gated mixture of local-context-attention + kNN-attention over the cache.
- **Fit for substrate**: PARTIAL. The substrate's W is NOT the LLM's hidden-state cache. But the gating mechanism (learned scalar combining two attention streams) is the architectural primitive that's most relevant: it shows minimum-parameter-cost injection of an external float vector stream into existing attention.
- **Training cost**: lightweight (~hours on single GPU for small models). kNN-LM requires no training at all.
- **Substrate adaptation**: store substrate-codeword-projected-to-d_model vectors in the kNN cache; LLM does kNN over this hybrid cache. Doesn't exploit substrate's multi-hop structure but is the cheapest viable starting point.

### Pattern 3: Cross-attention bridge with learnable queries (Flamingo, Q-Former, LLaMA-Adapter)
- **Architecture**: external encoder produces float vector sequence; small bridge module (learnable queries or prefix tokens) translates into LLM hidden dim via cross-attention.
- **Fit for substrate**: **STRONGEST**. The substrate plays the role of the "external encoder" -- producing bipolar codeword sequences (one per hop, K total). The bridge is a learnable MLP projection R^4096 -> R^d_model.
- **Training cost**: bridge-only ~20-30M params; ~1-8 hours on single GPU with 50K-200K paired examples; LLM backbone frozen.
- **Substrate adaptation**: each multi-hop step emits one bipolar codeword; bridge maps to K=8 soft-prompt tokens prepended to LLM input; LLM attends over prefix. **THIS IS THE RECOMMENDED PRIMARY PATTERN.**

### Pattern 4: Trainable VSA associative memory layer inside LLM (Memory Layers at Scale, DNC)
- **Architecture**: replace one FFN layer with a product-key lookup memory (continuous keys, ~d/2-dim); soft-attention-weighted value retrieval into residual stream. DNC: outer-product write `M = M + w v^T`, content-based softmax read.
- **Fit for substrate**: TIGHTEST MATHEMATICAL MATCH. DNC's outer-product write is `M = M + w v^T`; our substrate is `W = (1/N) sum_l v_l k_l^T` -- the same operation modulo bipolar quantization and the 1/N normalization. **This is the pattern to evolve toward**, not start from.
- **Training cost**: requires from-scratch pretraining or full fine-tuning. Multi-week single-GPU; out of scope for first prototype.
- **Substrate adaptation**: long-term goal. Phase 3+ work.

## Recommended starting architecture (Pattern 3 + Path D)

```
                LLM (frozen 1-3B base)
                 |
                 |  [QUERY] token's final hidden state
                 v
       [Query read-out head: Linear R^d_model -> R^4096] (~12.6M params)
                 |
                 v  [bipolar relaxed via tanh; sign() at deployment]
       q in R^4096 continuous-relaxed
                 |
                 v
       Substrate W (current production system, no changes)
                 |
                 v  Path D depth=5 multi-hop iteration
       result_codewords: K bipolar vectors in {-1,+1}^4096
                 |
                 v
       [Bridge MLP: Linear -> GELU -> Linear; 4096->2048->d_model] (~14.7M params)
                 |
                 v
       K soft-prompt prefix tokens in R^d_model
                 |
                 v
                LLM (frozen 1-3B base; same instance)
                 |
                 v
       Standard autoregressive decoder output
```

**Total trainable params**: ~27M (well under 1% of base LM). Frozen base LM during Phase 1. Optional Phase 2 adds QLoRA on attention/MLP layers (~30M additional).

**Training data construction (the load-bearing engineering item)**: paired examples of (input prompt, expected output) where the expected output benefits from substrate-retrieved facts. Two construction approaches:
1. **Synthetic from substrate**: store known facts in W; generate questions; expected output is the answer + substrate's retrieval path. ~50K examples from a single afternoon's substrate population.
2. **Re-purposed multi-hop QA**: HotpotQA / MuSiQue / 2WikiMultihop. Encode entities as substrate atoms; bind into W; LLM must use substrate to traverse multi-hop chains.

**Three rescues for the query-decomposition bottleneck at 1-3B scale** (per Subagent B's binding open question):
- **Rescue A**: train the small LM specifically on the decomposition task during Phase 2 LoRA. Decomposition becomes part of the supervised fine-tune signal.
- **Rescue B**: use a larger LLM (Claude/GPT-4 via API) for offline decomposition during training-data generation; small LM learns to imitate. Bootstrapping pattern.
- **Rescue C**: bypass decomposition by leveraging substrate's per-hop independence -- LLM emits a single initial query, substrate runs depth-5 iteration autonomously and returns the final converged result. The substrate IS the iteration; LLM doesn't need to plan multi-step. This is the most substrate-leveraging rescue and the one I'd start with.

## Build plan: 4-6 weeks single-person, marsh@home GPU (8GB VRAM)

**Hardware constraint:** 8GB VRAM forces either (a) downgrade base LM to TinyLlama-1.1B (~2.2GB fp16) OR Pythia-1B (~2GB), OR (b) use QLoRA 4-bit base for Phi-3-mini (~2GB at 4-bit, leaves room for bridge + activations). **(b) is recommended -- Phi-3-mini at 4-bit retains quality advantage; bridge stays in fp16.**

Surface as decision gate: is there a bigger GPU available, or do we commit to 8GB?

**Week 1: Infrastructure + baseline**
- Install lm-evaluation-harness; run Phi-3-mini-4bit baseline on ARC-Easy/Challenge, HellaSwag, PIQA, WinoGrande, BoolQ, TriviaQA-closed-book (~3-4 hr wall).
- Implement bipolar codeword interface: substrate W (existing) -> Path D retrieve (existing) -> bipolar codeword sequence output (NEW glue code, ~50 LOC).
- Scaffold the bridge MLP (PyTorch nn.Module, ~50 LOC).
- Single forward-pass smoke test: random bipolar codeword -> bridge -> prefix tokens -> Phi-3-mini -> output. Validates no shape mismatches.

**Week 2: Adapter training (Phase 1, frozen base)**
- Construct dataset: 50K synthetic examples from substrate ("question about stored fact -> answer with substrate retrieval"). Use existing exp_evaluation primitives.
- Train bridge + query head; expected wall-time ~4-8 hr on RTX-4090, ~16-32 hr on 8GB.
- Gate: does augmented model retain LLM-only baseline within 5pp on core benchmarks?

**Week 3: Multi-hop iteration**
- Wire Path D depth=5 into the inference loop. LLM emits query -> Path D runs depth=5 autonomously (Rescue C) -> bridge maps result to prefix tokens -> LLM generates.
- Test on MuSiQue subset (200 examples). Measure: EM / F1 / latency.
- Gate: substrate-augmented MuSiQue beats LLM-only by >=10pp (deflated target; literature predicts +24pp at large scale).

**Week 4: QLoRA on base (Phase 2)**
- Add LoRA r=16 to Phi-3-mini-4bit attention + MLP layers. ~30M LoRA params + 27M bridge = ~57M trainable.
- Resume training on combined dataset (synthetic substrate + MuSiQue + HotpotQA reformulated). Expected wall ~1-3 days on RTX 4090; ~4-8 days on 8GB.
- Gate: LoRA boost is measurable vs frozen-base.

**Week 5: Substrate-favored evaluation suite**
- LLM-only vs LLM+text-RAG (FAISS over Wikipedia subset) vs LLM+substrate comparison.
- Standard benchmarks (ARC/HellaSwag/PIQA/BoolQ/WinoGrande): expect minimal delta (these are reasoning-bound, not recall-bound).
- TriviaQA closed-book: expect measurable substrate-augmented gain (recall-sensitive).
- MuSiQue / HotpotQA / 2WikiMultihop: expect substantial substrate-augmented gain (multi-hop sensitive).
- Custom substrate-favored: edit-then-query (substrate's edit-isolation should beat LLM-only retraining-required), deletion-cert audit (only substrate can emit), provenance-citation (substrate emits atom-level; LLM-only can't).

**Week 6: Buffer + polish + write-up**

## Test design: what we're trying to learn

| Question | Test | Expected substrate-wins-direction |
|---|---|---|
| Does substrate-augmented LLM match LLM-only on commonsense? | ARC/HellaSwag/PIQA/BoolQ/WinoGrande | NO regression (substrate shouldn't hurt) |
| Does substrate-augmented LLM beat LLM-only on factual recall? | TriviaQA closed-book | +5-15pp expected |
| Does substrate-augmented LLM beat LLM-only on multi-hop QA? | MuSiQue / HotpotQA / 2WikiMultihop | +10-30pp expected (deflated from +24/+38/+8 lit gaps) |
| Does substrate enable LLM operations LLM cannot do alone? | Edit-then-query benchmark; deletion-cert audit; provenance citation | Substrate-only capabilities (binary yes/no) |
| Does the codebook-native interface beat text-RAG? | LLM+text-RAG vs LLM+substrate on identical multi-hop QA | Substrate-native should match or beat RAG; latency should be substantially better |
| Does substrate-augmented latency stay within LLM token-generation budget? | Per-query latency profiling at production-scale | Substrate Path D ~1-3ms vs LLM token ~10-50ms; should be net positive |
| What's the failure mode at small-LM scale? | Per-task error analysis | Query decomposition expected to be primary failure (per Subagent B) |

## Open risks and decision gates

**Risk 1 (HIGHEST): Query-decomposition bottleneck at 1-3B scale.** Subagent B's binding constraint -- ToG/ReWOO use GPT-3.5/4 as planner. Mitigation: Rescue C (substrate runs depth=5 autonomously, LLM emits single initial query). Decision gate at Week 3: if Rescue C insufficient, escalate to Rescue A or B.

**Risk 2: Bipolar-to-LLM bridge alignment is unpublished.** NVSA does the opposite direction. No published validation that a learned linear projection from bipolar {-1,+1}^4096 to R^d_model preserves enough information for the LLM to decode usefully. Mitigation: start with continuous-relaxed codewords (sign only at deployment); train end-to-end with straight-through estimator. Phase 1 frozen-base + linear bridge has P ~0.55 alone.

**Risk 3: 8GB VRAM ceiling.** Phi-3-mini-4bit ~2GB + bridge fp16 ~100MB + activations ~3-4GB at batch_size=4, seq_len=512 = comfortable. But Phase 2 QLoRA adds optimizer state + gradients that push to ~6-7GB; batch_size 1 with grad accumulation may be required. Wall-time ~4-8x on 8GB vs 24GB. **Decision gate at session start: is a bigger GPU available?**

**Risk 4: Synthetic training data distribution mismatch.** If training is on synthetic substrate-augmented pairs and eval is on MuSiQue, the bridge may overfit to synthetic distribution. Mitigation: mix in genuine multi-hop QA reformulations early.

**Risk 5: Benchmark suite includes too few substrate-favored tasks.** Standard LLM benchmarks (ARC/HellaSwag) are reasoning-bound, not recall-bound; expected near-zero delta. The substrate-favored benchmarks (edit-then-query, deletion-cert audit) are NOT in lm-eval-harness; they must be constructed bespoke. Time budget: ~3-5 days to build the substrate-favored eval suite. Add to Week 5.

**Risk 6: This work is research not engineering commitment.** Per user "do some (safe) research". This deliverable is design space + build plan + test design. Decision to commit to the 4-6 week engineering build comes AFTER design review + hardware decision + (optionally) a 1-week feasibility smoke (Week 1 only).

## Decision gates (orchestrator + user decide; not auto-dispatched)

1. **GPU resource decision**: 8GB marsh@home GPU vs bigger GPU available? Determines base-LM choice (Phi-3-mini-4bit on 8GB vs Phi-3-mini-fp16 on 24GB) and training wall-time (1-3 days vs 4-8 days at Phase 2).
2. **Hardware budget**: if no bigger local GPU, cloud H100 80GB (~$3-5/hr) for the 4-6 week build is ~$200-400 total spent on training. Falls in the "production-LLM integration prototype" cloud-warranted bucket from this morning's research-focus-expansion routing.
3. **Pre-commit feasibility smoke (recommended)**: spend Week 1 ONLY -- baseline + scaffold + smoke test. Decide GO/NO-GO for Weeks 2-6 based on whether (a) interface works mechanically, (b) baseline numbers match published Phi-3-mini reports, (c) any hardware blocker surfaces.
4. **Sequencing**: this is the substrate's product-positioning load-bearing test (per [[project_substrate_killer_features_2026-05-26]] and [[project_substrate_strategic_inversion_48h_2026-05-26]]). Should be queued AFTER the cheaper near-term drills (LLM-integration latency budget characterization, audit-trail rotation, storage efficiency) per this morning's research-focus-expansion routing -- because those are 1-2 week probes that inform the larger 4-6 week build.

## Citations (verified URLs)

External lit-scan citations from the 3 subagent drills:

1. **Borgeaud et al., "RETRO: Improving Language Models by Retrieving from Trillions of Tokens," ICML 2022** -- [arXiv:2112.04426](https://arxiv.org/abs/2112.04426). Chunked cross-attention canonical pattern.
2. **Wu et al., "Memorizing Transformers," ICLR 2022** -- [arXiv:2203.08913](https://arxiv.org/abs/2203.08913). Gated kNN-attention adapter; lightweight retraining.
3. **Hersche et al., "A Neuro-Vector-Symbolic Architecture for Solving Raven's PMs," Nature MI 2023** -- [Nature link](https://www.nature.com/articles/s42256-023-00630-8). Closest published bipolar bridge precedent; OPPOSITE direction from ours.
4. **Graves et al., "Differentiable Neural Computer," Nature 2016** -- [Nature link](https://www.nature.com/articles/nature20101). Outer-product write `M = M + w v^T`; mathematically identical to our substrate W.
5. **Zhang et al., "LLaMA-Adapter," ICLR 2024** -- [arXiv:2303.16199](https://arxiv.org/abs/2303.16199). 1.2M-param prefix adapter on frozen LLM; sets parameter-budget floor.
6. **Berges et al., "Memory Layers at Scale," Meta 2024** -- [arXiv:2412.09764](https://arxiv.org/abs/2412.09764). Product-key memory layer as FFN replacement; closest vector-native memory inside LLM.
7. **Dziri et al., "Faith and Fate," NeurIPS 2023** -- [arXiv:2305.18654](https://arxiv.org/abs/2305.18654). LLM compositional reasoning is pattern-matching; structural offload motivation.
8. **Sun et al., "Think-on-Graph (ToG)," ICLR 2024** -- [arXiv:2307.07697](https://arxiv.org/html/2307.07697). +23.5pp CWQ / +51.8pp GrailQA vs CoT-only GPT-4 via KG-walk.
9. **Xu et al., "ReWOO," 2023** -- [arXiv:2305.18323](https://arxiv.org/abs/2305.18323). 5x token reduction + 4% HotpotQA gain via decoupled planning from observations.
10. **Mirzadeh et al., "GSM-Symbolic," Apple 2024** -- [arXiv:2410.05229](https://arxiv.org/abs/2410.05229). 65% accuracy drop from single irrelevant clause; structural symbolic-reasoning failure mode.
11. **Abdin et al., "Phi-3 Technical Report," 2024** -- [arXiv:2404.14219](https://arxiv.org/pdf/2404.14219). Phi-3-mini architecture + MIT license.
12. **EleutherAI lm-evaluation-harness** -- [GitHub](https://github.com/EleutherAI/lm-evaluation-harness). Standard eval backend; 400+ tasks.

## Internal citations

- `notes/substrate_capability_map.md` v290-v291 (Path D edit-resilience, Modern Hopfield large-N, in-context-learning-via-pool ✅, real-time-learning ✅, autoregressive-generation v2-strict-baseline ✅)
- `notes/research_alt_edit_isolation_v1_2026-05-31.md` (M1+M2 log-structured store; audit-by-construction is part of the substrate-distinctive feature set this integration exposes)
- `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` (D1+D2+D3 defenses; integration deployment must include these)
- `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (this drill addresses Missing #1 -- substrate-augmented LLM absolute-quality benchmark)
- Memory: `project_substrate_killer_features_2026-05-26`, `project_substrate_strategic_inversion_48h_2026-05-26`, `feedback_no_papers_product_only`, `feedback_capabilities_mapping_not_competitive_analysis`, `feedback_query_privacy_decomposition`, `feedback_aggressive_cross_domain_research`

## Lit-scan calibration penalty summary

- Subagent A (vector-native interfaces) raw P 0.55-0.65 -> deflated 0.30-0.40 for full bipolar-round-trip; 0.55 for frozen-base linear bridge alone
- Subagent B (multi-hop offload) raw 0.65 -> deflated 0.45 for >=20% gain at 1-3B
- Subagent C (engineering path) raw 0.60 -> deflated 0.40 on RTX 4090, 0.25-0.30 on RTX 3060/8GB

Joint P that **the codebook-native deep integration delivers a defensible product-claim demonstration within 4-6 weeks on the marsh@home 8GB GPU**: 0.20-0.30. On a 24GB cloud GPU: 0.35-0.45. The novel-synthesis cap at 0.50 is not binding because the architecture combines published primitives in an unpublished arrangement -- not a from-scratch novel theory.
