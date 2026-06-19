# Strategy request: substrate-LLM deep integration via codebook-native interface

## Trigger: user prompt 2026-05-31 + research drill 2026-05-31 (delivery `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md`)

## Finding (one paragraph)

User raised a sharp question: substrate's multi-hop + Bayesian-independence + compositional-decomposition + edit-isolation + deletion-cert capabilities suggest a deeper LLM integration than standard RAG -- specifically, the substrate's bipolar codeword IS an "intrinsic language" the LLM could potentially consume without text-tokenization round-trip. 3 parallel Sonnet lit-scan subagents confirm the architectural primitives exist (RETRO chunked cross-attention, Memorizing Transformers gated kNN, Flamingo/Q-Former cross-attention bridge, DNC outer-product memory with mathematically-identical interface to substrate W) BUT the specific direction of bipolar-codeword-OUTPUT consumed by an LLM-INPUT is unpublished. NVSA (Hersche, Nature MI 2023) is closest precedent but in the opposite direction (neural -> bipolar). Recommended starting architecture: Pattern 3 (Flamingo/LLaMA-Adapter style) -- frozen 1-3B base LM + ~27M-param bidirectional MLP bridge (LLM query head + substrate-result bridge) + substrate Path D depth=5 autonomous multi-hop (Rescue C: bypasses the small-LM query-decomposition bottleneck identified by Subagent B). On the marsh@home 8GB VRAM GPU, Phi-3-mini-4bit is the feasibility-tight choice; on 24GB the same model at fp16 is comfortable. P_deflated joint (full end-to-end build delivering defensible product-claim demo in 4-6 weeks): 0.20-0.30 on 8GB, 0.35-0.45 on 24GB cloud. The binding research risk is the query-decomposition bottleneck at 1-3B scale (Subagent B's primary open question). The binding engineering risk is bridge-alignment debugging (Subagent A's primary uncertainty). The binding hardware risk is the 8GB VRAM ceiling.

## Recommended action

**1. Cap_map: NEW row (research-only 🔬) under "Production positioning" category.**

Row name: "Substrate-LLM deep integration via codebook-native interface"

Initial P-band (deflated): 0.30-0.45 (range reflects 8GB-local vs 24GB-cloud hardware path)

Caveats: (a) bipolar-codeword-to-LLM-input direction unpublished; (b) query-decomposition bottleneck at small-LM scale unknown; (c) hardware constraint determines feasibility window; (d) requires synthetic training data construction (~50K-200K paired examples) which is its own engineering risk.

Cross-references: directly addresses Missing #1 from `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (substrate-augmented LLM absolute-quality benchmark vs LLM-only). The research drill delivered today is the design-space + build-plan + test-design for that benchmark.

**2. Decision gate sequencing (NOT auto-dispatched; user + orchestrator decide).**

Three decisions must land before any 4-6 week engineering commitment:

(a) **GPU resource decision.** Is the marsh@home 8GB GPU the target, or is a bigger GPU available (24GB local 4090, cloud H100 80GB, or other)? Determines base-LM (Phi-3-mini-4bit vs fp16), training wall-time (1-3 days vs 4-8 days at Phase 2 QLoRA), and overall P_deflated (0.20-0.30 vs 0.35-0.45). **Highest-leverage decision.**

(b) **Pre-commit feasibility smoke (RECOMMENDED).** Spend ONE week on infrastructure + scaffold + smoke test (Week 1 of the build plan). Decide GO/NO-GO for Weeks 2-6 based on (i) does the bridge mechanically connect substrate -> LLM without shape mismatches, (ii) do baseline Phi-3-mini numbers match published reports, (iii) does any hardware blocker surface. This Week 1 is ~$0 if local; ~$30-50 if rented cloud GPU. **Cheap insurance against committing to a 4-6 week build that hits a hard blocker.**

(c) **Sequencing vs other queue items.** This is the substrate's product-positioning LOAD-BEARING test but it's a 4-6 week scope. Per [[feedback-substrate_value_framing_2026-05-26]] plumbing > physics. But this drill also needs the 1-2 week probes (LLM-integration latency budget, audit-trail rotation, storage efficiency) to inform the larger build. Recommend: ship the 3 smaller drills FIRST (~1-2 weeks combined), THEN commit to Week 1 feasibility smoke of the deep-integration build, THEN GO/NO-GO for Weeks 2-6.

**3. Cloud-routing assessment.**

Per this morning's research-focus-expansion routing, cloud is the EXCEPTION not default. This substrate-LLM build is one of the 3 explicitly cloud-warranted candidates (the "Pattern B production-LLM integration" item, properly reframed without the Pattern-B terminology confusion). If the 8GB local GPU is insufficient (likely for Phase 2 QLoRA at reasonable wall-time), cloud H100 80GB at ~$3-5/hr for 4-6 weeks build is ~$200-400 total. This is within the cloud-budget envelope.

Alternative if user wants to AVOID cloud: stick with TinyLlama-1.1B on 8GB GPU. P_deflated drops to 0.20-0.25 (Subagent C's risk-4 estimate), but the integration architecture proof-of-concept is still achievable; just smaller-scale absolute quality.

**4. Routing-file lifecycle.**

Per the session sync protocol, this routing file requests orchestrator action (cap_map row addition + decision-gate scheduling + queue sequencing). When acted on, file should move to `notes/routed_completed/`.

## Confidence

P_deflated estimates (calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]):

- Working end-to-end build (LLM-only baseline + bridge + substrate retrieval + benchmark suite) in 4-6 weeks single-person:
  - On 24GB GPU (RTX 4090 local OR cloud H100): **0.40-0.45**
  - On 8GB GPU (marsh@home): **0.25-0.30**
- Substrate-augmented LLM delivers >=20% accuracy gain on multi-hop QA vs LLM-only at 1-3B scale: **0.45** (Subagent B; novel-synthesis cap not binding)
- Substrate-LLM integration delivers DEFENSIBLE product-positioning demonstration (i.e., gain on substrate-favored benchmarks + audit trail emitted + provenance citation + edit-then-query): **0.55-0.65** (lower bar than +20% multi-hop; depends only on bridge mechanics and substrate's existing capabilities propagating through)

The binding research-risk: query-decomposition at 1-3B (Subagent B). Three rescues filed in research delivery; Rescue C (substrate-autonomous multi-hop, LLM single-query emission) is the most substrate-leveraging and the recommended starting position.

The binding engineering-risk: bridge-alignment training (Subagent A). Mitigation: start with continuous-relaxed (tanh) codewords + straight-through estimator; binarize only at deployment.

## Files of interest

- `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` (primary deliverable; 4 architecture patterns, recommended starting design, build plan week-by-week, test design, 6 risks, 12 external + 6 internal citations)
- `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (this morning's routing; Missing #1 substrate-vs-LLM benchmark is what THIS drill provides design space for)
- `notes/research_alt_edit_isolation_v1_2026-05-31.md` (M1+M2 log-structured store; audit-by-construction is the substrate-distinctive property the integration exposes)
- `notes/substrate_capability_map.md` v290-v291 (Path D edit-resilience + Modern Hopfield large-N + ICL via pool + autoregressive generation + real-time learning -- the substrate properties this integration depends on)
- Memory: `project_substrate_killer_features_2026-05-26.md`, `project_substrate_strategic_inversion_48h_2026-05-26.md`

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator + user decide:
- (a) GPU resource (8GB local vs bigger GPU vs cloud)
- (b) Pre-commit feasibility smoke timing (recommend Week-1-only first)
- (c) Sequencing vs other queue items (recommend smaller drills first, then feasibility smoke, then full build commit)

No engineering work begins without explicit user GO signal on all three decision gates.
