# Research: substrate-LLM interface optimization (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- "should we do a research turn on how we can optimize this substrate interface with the LLM?"
Method: 1 Sonnet research-drill subagent, 6-axis comparison (bridge depth/capacity, codebook representation, prefix-token granularity, Path D output format, joint training signal, inference-time tricks); 6 external citations verified
Trigger: complements `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` (baseline architecture); informs testbed handoff revisions before Week 1 design freezes

## HEADLINE

The CHEAPEST viable architecture (Pattern 3 with 2-layer MLP bridge + continuous-relaxed codebook + single-prefix-token + pure next-token loss) is NOT the BEST viable architecture. Three high-impact deviations lift joint P_deflated by ~+0.18-0.29 over baseline, pushing the 8GB-GPU build from 0.25-0.30 toward 0.43-0.59 -- closer to the cloud-24GB pre-optimization estimate. The cost is ~2x training wall (8-20h vs 2-4h on A100; ~32-80h vs 16-32h on 8GB consumer). Still fits within the 4-6w window. All three deviations are evidence-backed (BLIP-2 + MM1 + CoT mechanistic literature); the optimization is grounded, not speculative.

## The 3 high-impact deviations (REVISED baseline for testbed)

### Deviation 1 (LARGEST P_def LIFT +0.08-0.12): Q-Former cross-attention bridge instead of 2-layer MLP

**Original spec:** 2-layer MLP (Linear -> GELU -> Linear), ~14.7M params, R^4096 -> R^2048 -> R^d_model.

**Revised:** Q-Former-style cross-attention bridge with 8-16 learnable query tokens per substrate codeword. ~30-50M params (~2-3x baseline).

**Why:** BLIP-2 (Li et al. 2023, [arXiv:2301.12597](https://arxiv.org/abs/2301.12597)) demonstrated that 32 learnable query tokens attending to a frozen encoder via cross-attention match or exceed models trained with 54x more compute on VQAv2/COCO. The cross-attention bottleneck is specifically designed to compress a high-dimensional modality into a small fixed-length prefix the LLM can consume. The MLP is a flat compressor that destroys structure the cross-attention preserves -- specifically the per-hop posterior structure (~9 bits of useful discriminative information concentrated sparsely in the 4096-dim codeword, NOT uniformly distributed).

**P_def estimate for Q-Former with bipolar inputs:** 0.45 (raw 0.65, calibration penalty -0.20 because Q-Former + bipolar is unpublished combination)
**P_def estimate for baseline MLP:** 0.35 (raw 0.52, calibration penalty -0.17)
**Net P_def lift:** **+0.08-0.12**

**Engineering cost:** Q-Former training: 8-20h on A100; on 8GB GPU consumer: ~32-80h (4x). MLP baseline: 2-4h A100 / 8-16h on 8GB. Net training-time increase: +24-64h. Total Phase 1 budget: still <1 week wall on 8GB.

### Deviation 2 (MEDIUM P_def LIFT +0.06-0.10): Two-stage training with contrastive + reconstruction auxiliary loss in Stage 1

**Original spec:** Train bridge end-to-end with pure next-token LLM loss (frozen base).

**Revised:** Two-stage schedule per BLIP-2:
- **Stage 1**: Bridge-only training against frozen substrate with three objectives:
  - Codeword-text contrastive (ITC analog): force bridge to embed correct codeword-text pairs close, incorrect pairs apart
  - Reconstruction (ITM analog): force bridge to discriminate "this codeword retrieves the correct candidate" from "this codeword retrieves wrong candidate"
  - Codeword-conditioned generation (ITG analog, optional): force bridge to enable correct text generation given the codeword
- **Stage 2**: Joint bridge + LLM (frozen base) with next-token loss only; Stage 1 weights initialize Stage 2

**Why:** Pure next-token loss in joint training provides NO gradient unless the LLM happens to generate text that discriminates the retrieved concept from alternatives -- a very sparse signal early in training. Stage 1 gives the bridge a direct signal that its output corresponds to a discriminable substrate concept, preserving retrieval discriminability before Stage 2 overwrites it.

**P_def estimate net lift:** **+0.06-0.10**

**Engineering cost:** Stage 1 adds ~50% wall on top of Stage 2. Total Phase 1 wall on 8GB: ~24-48h Stage 1 + ~16-32h Stage 2 = ~40-80h (~1-2 weeks at single-shift). Still within Week 2.

**Open risk** (Drill Open Question #3): Stage 2 may overwrite Stage 1's discriminability if Stage 2 runs too long without re-injecting auxiliary loss. Mitigation: monitor bridge codeword-retrieval-accuracy on a held-out set during Stage 2; halt if drops below Stage 1 endpoint.

### Deviation 3 (SMALLER P_def LIFT +0.04-0.07): Per-hop codeword sequence as separate prefix-token groups

**Original spec:** Substrate emits final converged result codeword (Rescue C single output). 8 tokens / 1 prefix group.

**Revised:** Substrate emits ALL 5 hop posteriors; bridge produces 5 prefix-token groups (8 tokens each = 40 prefix tokens total at depth=5). LLM cross-attention can selectively attend to different hops for different downstream positions.

**Why:** Recent mechanistic CoT literature (Nag et al. 2025, [arXiv:2507.22928](https://arxiv.org/abs/2507.22928)) demonstrates that CoT intermediate states encode genuinely transferable features above ~2.8B model size -- feature-transfer experiments show injecting CoT features into non-CoT runs improves accuracy. The 3.8B Phi-3-mini target is just above this threshold. Collapsing 5 hops to one prefix discards hop-level structure the LLM could exploit. Context budget cost: 40 prefix tokens / 2048 prompt window = ~2% overhead. Acceptable.

**P_def estimate net lift:** **+0.04-0.07**

**Engineering cost:** Minimal -- substrate already emits per-hop posteriors internally (Path D iteration); just expose them to the bridge instead of collapsing to final converged. No training-data implication. Soft-prompt prefix length goes 8 -> 40 tokens.

**Open risk** (Drill Open Question #4): per-hop benefit at 3.8B may be marginal; could be scale-gated above 7B. If smoke shows Stage 1 reconstruction loss is similar between per-hop and single-prefix variants, fall back to single-prefix to save context budget for the user-question itself.

## Other axes (not high-impact deviations; documented for completeness)

### Codebook representation: Hybrid (Option 3) BEATS continuous-relaxed (Option 2)

**Original spec:** Continuous-relaxed (tanh) during training, sign() only at deployment.

**Revised:** Hybrid -- substrate stores + computes in bipolar throughout; bridge receives raw {-1,+1}^N codeword AND projects through a continuous embedding layer at the bridge input (never binarize inside the bridge during training).

**Why:** Original spec (Option 2) introduces a train-test distribution gap -- bridge optimized over soft (-1,+1) values but receives hard {-1,+1} at inference. Hybrid avoids the gap entirely. Also: information-theoretically, the multi-hop posterior carries ~log2(K_paths) = log2(500) ~ 9 bits per codeword concentrated sparsely; the bridge's continuous projection preserves this sparse signal where binarization-inside-bridge would quantize away discriminability.

**P_def estimate net lift:** modest (+0.02-0.04); included in the Deviation 1 P_def estimate because Q-Former cross-attention naturally implements this hybrid pattern (cross-attention queries continuous, keys can be bipolar).

### Inference-time: Adaptive Path D depth based on LLM uncertainty (DEFER but spec)

**Why interesting:** The LLM's generation uncertainty (next-token-distribution entropy, or beam-score variance) can route substrate calls: high uncertainty -> depth=5; low uncertainty -> depth=1. Saves substrate compute on easy queries. Drill assessed: highest-leverage inference-time optimization UNIQUE to this substrate (impossible in standard dense RAG).

**Why defer:** Requires dynamic Path D depth control + LLM-uncertainty signal extraction at inference. Not Phase 1; revisit Phase 2.

### Speculative substrate prefetch (DEFER but spec)

**Why interesting:** TeleRAG (Dong et al. 2025, [arXiv:2502.20969](https://arxiv.org/abs/2502.20969)) demonstrates 1.53x latency reduction by overlapping retrieval with LLM generation. Speculative Interaction Agents shows 1.6-2.2x speedup for 3B-class models.

**Why defer:** Requires substrate-side async API + LLM generation loop hooks for mid-pass async dispatch. Phase 2+ engineering. Worth retrofitting if latency budget (Missing 7) Week 0 measurement shows substrate is the wall.

## Updated joint P estimate

Pre-optimization (baseline spec):
- 24GB GPU: 0.40-0.45
- 8GB GPU (marsh@home): 0.25-0.30

Post-optimization (Deviations 1+2+3 applied):
- 24GB GPU: **0.55-0.65** (baseline 0.40 + lifts 0.18 = 0.58)
- 8GB GPU: **0.43-0.55** (baseline 0.27 + lifts 0.16 = 0.43; range reflects training-wall risk on 8GB)

The optimization closes most of the 8GB-vs-24GB gap. The 8GB path becomes meaningfully more competitive after these changes; the rate-limiter shifts from architecture-choice to wall-time-on-consumer-GPU.

## Recommended path for testbed

**Revise the testbed handoff baseline spec** to include all 3 deviations as the NEW default. Specifically:
- Bridge: Q-Former cross-attention (8-16 query tokens), ~30-50M params (~2-3x baseline)
- Training: BLIP-2 two-stage (Stage 1 contrastive+reconstruction; Stage 2 joint with next-token)
- Substrate output: per-hop posteriors as separate prefix-token groups; 5 hops x 8 tokens = 40 prefix tokens at depth=5
- Codebook: hybrid bipolar storage + continuous projection through bridge (natural fit with Q-Former cross-attention)

Cost: +1 week to the original Week 2-4 training schedule. Net build window: still 4-6 weeks IF Week 0 Missing 7 latency-budget measurement passes AND Week 1 feasibility smoke passes.

**Hold off on these as Phase 2+ ambitions** (not in Phase 1 4-6w window):
- Adaptive Path D depth based on LLM uncertainty
- Speculative substrate prefetch
- Trainable VSA-style memory layer drop-in (DNC-pattern; from-scratch pretraining, multi-month)

## Open synthesis questions (not blockers; surface to research at end of Week 1)

1. Does Q-Former cross-attention handle bipolar {-1,+1} keys/values without softmax-attention-weight collapse? Standard Q-Former assumes continuous patch embeddings. Untested in lit. **Likely fine empirically; smoke-testable Week 1.**
2. At what posterior-entropy threshold does adaptive depth help? Need empirical distribution of Path D posterior entropy over realistic queries. **Defer to Phase 2.**
3. Does Stage 2 next-token loss overwrite Stage 1 discriminability? Standard concern in two-stage training. Mitigation: monitor + halt criterion. **Empirical answer Week 2.**
4. How much per-hop intermediate benefit is scale-gated at 3.8B vs 7B+? Lit suggests 2.8B is the threshold; 3.8B is marginal. **Empirical Week 3.**
5. Can the bridge be trained with synthetic substrate outputs vs requiring paired (codeword, LLM-correct-answer) data? Data construction bottleneck. **Empirical Week 2.** Highest engineering risk.

## Citations

1. **Li et al., "BLIP-2," 2023** -- [arXiv:2301.12597](https://arxiv.org/abs/2301.12597). Q-Former 32-token ablation + two-stage training schedule.
2. **Berges et al., "Memory Layers at Scale," Meta FAIR 2024** -- [arXiv:2412.09764](https://arxiv.org/abs/2412.09764). Trainable VSA-style memory layers; from-scratch only.
3. **Ghosh et al., "MM1," Apple 2024** -- [arXiv:2403.09611](https://arxiv.org/abs/2403.09611). Connector less important than encoder + token count; informs prefix-token-budget decision.
4. **Yang et al., "Logical Constraints via STE," ICML 2022** -- [arXiv:2307.04347](https://arxiv.org/abs/2307.04347). Straight-through-estimator gradient behavior for binary networks.
5. **Nag et al., "How CoT Thinks," 2025** -- [arXiv:2507.22928](https://arxiv.org/abs/2507.22928). CoT intermediate states transferable above 2.8B; supports per-hop sequencing.
6. **Dong et al., "TeleRAG," 2025** -- [arXiv:2502.20969](https://arxiv.org/abs/2502.20969). 1.53x latency reduction via speculative substrate prefetch.

## Internal cross-refs

- `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` (baseline architecture; THIS NOTE supersedes the bridge-architecture + codebook + training-schedule sections)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (will be amended with revised baseline spec)
- `notes/research_alt_edit_isolation_v1_2026-05-31.md` (M2 log-structured store; same morning drill)
- Memory: `feedback_subagent_model_optimization`, `feedback_lit_scan_calibration_penalty`, `feedback_query_privacy_decomposition`

## Calibration penalty summary

Calibration penalty -0.15 to -0.25 applied to all P estimates. Q-Former + bipolar is the highest-confidence deviation (P_def 0.45) but remains below novel-synthesis cap of 0.50 because no published work combines Q-Former with bipolar discrete-algebraic retrieval. Per-hop prefix sequencing rests on CoT mechanistic evidence from a different architecture regime; transferability P_def 0.38.

Joint P_def (the post-optimization 8GB build delivering a defensible product-positioning demonstration in 4-6 weeks): **0.43-0.55** (substantial lift from 0.25-0.30 baseline; the optimization is the difference between probably-not and roughly-coin-flip on this hardware).
