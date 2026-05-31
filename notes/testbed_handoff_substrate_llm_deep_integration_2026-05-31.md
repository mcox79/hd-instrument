# Testbed handoff: substrate-LLM deep integration build (codebook-native interface)

## Origin
- User prompt 2026-05-31 (after research delivery + strategy routing) -- "sounds like a good experiment to run; route it to testbed and/or orchestrator to implement"
- Research design doc: `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` (full architecture, build plan, test design, 6 risks, 12 external citations -- this handoff points at it; testbed reads it for the engineering spec)
- Strategy request (orchestrator side): `notes/strategy_request_to_strategy_substrate_llm_deep_integration_2026-05-31.md` (cap_map row addition + decision-gate sequencing)

## TASK

Build a substrate-LLM deep-integration prototype on the remote machine that:
1. Loads a frozen 1-3B base LM (Phi-3-mini-3.8B at 4-bit on 8GB VRAM; or fp16 on bigger GPU if available)
2. Wires a ~27M-param bidirectional MLP bridge between substrate bipolar codewords (R^N=4096) and LLM prefix tokens (R^d_model)
3. Trains the bridge end-to-end on synthetic substrate-augmented data (frozen base; Phase 1 first; optional QLoRA in Phase 2)
4. Runs comparison evaluation: LLM-only vs LLM+text-RAG vs LLM+substrate on standard benchmarks (lm-evaluation-harness) + substrate-favored bespoke benchmarks (edit-then-query, deletion-cert audit, provenance citation)
5. Reports back at Week 1 feasibility-smoke gate before committing the full 4-6 week build

## WHY (substrate-product-positioning context)

This drill addresses Missing #1 from `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md`: substrate-augmented LLM absolute-quality vs LLM-only baseline. Currently the "GPT-quality generation with auditable memory" Tier-1 killer capability is at 🟢 Partial with 5 research paths dispatched but NO empirical absolute-quality validation against LLM-only. This build IS that validation, with codebook-native bridge as the load-bearing architectural choice.

The "intrinsic language" insight (bipolar codeword IS the substrate-LLM interface; no text-tokenization round-trip) is structurally unpublished. NVSA (Hersche Nature MI 2023) does the opposite direction. DNC's outer-product write is mathematically identical to substrate W modulo bipolar quantization. So the architectural primitives exist; the substrate-specific bridge is novel synthesis.

## CONTRACT (what testbed owns + what's pre-decided)

**Testbed owns** (per session ownership rules in `notes/session_architecture_v1_2026-05-31.md`):
- All engineering scaffolding: PyTorch + HuggingFace transformers + PEFT + lm-evaluation-harness integration
- The bridge MLP module + training loop + checkpointing
- Synthetic training data construction from substrate primitives (substrate populated by exp_evaluation paths; testbed scripts the dataset assembly)
- Benchmark scaffolding: LLM-only baseline, LLM+text-RAG baseline (FAISS over a Wikipedia subset), LLM+substrate variant
- The 3 substrate-favored bespoke benchmarks (edit-then-query, deletion-cert audit, provenance citation) -- design + implementation
- All code lands in `testbed/` and/or `hdlab_service/` per testbed ownership; new directories OK (e.g., `testbed/llm_integration/`)

**Pre-decided design choices** (from research delivery; testbed implements without re-arbitrating):
- Base LM: Phi-3-mini-3.8B (Microsoft, MIT license) -- 4-bit if 8GB GPU, fp16 if 24GB
- Adapter architecture: Pattern 3 (Flamingo/LLaMA-Adapter style) -- 2-layer MLP projection + cross-attention via soft-prompt prefix; ~27M params bidirectional
- Multi-hop strategy: Rescue C -- substrate runs Path D depth=5 AUTONOMOUSLY; LLM emits a single initial query. **Do NOT make the LLM plan multi-hop iteration.** This is the load-bearing design choice to bypass the 1-3B query-decomposition bottleneck.
- Training: Phase 1 frozen-base + bridge-only first (~50K synthetic examples, 2-8 hr on 24GB, 16-32 hr on 8GB). Phase 2 QLoRA optional after Phase 1 PASS gate.
- Discrete-gradient handling: continuous-relaxed (tanh) codewords during training + straight-through estimator; sign() binarization only at deployment.

**Open user-side decisions BLOCKING work-start** (do NOT begin until orchestrator confirms user has answered):
- **(a) GPU resource**: 8GB marsh@home (Phi-3-mini-4bit; P_def 0.25-0.30) OR 24GB local-or-cloud (fp16; P_def 0.40-0.45). The 8GB path is feasible but ~4-8x slower wall-time at Phase 2.
- **(b) Commitment depth**: Week 1 feasibility smoke ONLY (recommended; ~$0 local or ~$30-50 cloud; cheap insurance) OR full 4-6w commit upfront.
- **(c) Queue sequencing**: ship the 3 cheaper drills first (Missing 7 LLM-integration latency budget + Missing 2 storage efficiency + Missing 3 audit-trail rotation; combined ~3-4 weeks) BEFORE this larger build, OR run in parallel, OR replace those with this one. Research recommends shipping the smaller ones first because they INFORM the larger build.

## AUTONOMY (decisions testbed makes inline)

Testbed decides without escalation:
- Exact Python package versions (transformers, peft, bitsandbytes, accelerate, lm-eval-harness, faiss)
- Data-loading pipeline (HuggingFace datasets API vs custom)
- Training-loop framework (raw PyTorch vs HF Trainer vs Unsloth)
- Hyperparameter sweep granularity (LR / batch size / sequence length / LoRA rank/alpha)
- Logging + checkpointing infrastructure (wandb / tensorboard / plain JSON)
- Code layout under `testbed/llm_integration/` (testbed already owns testbed/)
- Whether to use Phi-3-mini or substitute TinyLlama-1.1B if Phi-3-mini hits unexpected blocker (e.g., MIT-license-clean version unavailable on chosen package version)

Testbed surfaces to orchestrator (don't decide inline):
- Hardware blocker that requires switching GPU paths
- Discovery that one of the 6 risks in the research note is materializing more severely than predicted (especially Risk 1 discrete-gradient or Risk 2 bridge-alignment)
- Training-data construction is harder than estimated (50K synthetic examples is the design assumption; if it takes >1 week to assemble, escalate)
- Benchmark numbers diverging meaningfully from published Phi-3-mini baselines (suggests something is broken with the base LM setup)

## WEEK 1 FEASIBILITY SMOKE (recommended commit-depth)

Recommended start: Week 1 ONLY. Decide GO/NO-GO for Weeks 2-6 based on:
- (i) Bridge mechanically connects substrate -> LLM without shape mismatches (single forward-pass smoke)
- (ii) Baseline Phi-3-mini numbers match published reports within +/-2pp on ARC/HellaSwag/PIQA/BoolQ
- (iii) No hardware blocker (e.g., 8GB OOM on inference, transformers/peft version conflict on the chosen GPU)
- (iv) Substrate Path D depth=5 retrieval populated with synthetic facts works in the testbed environment

Week 1 deliverables:
- `testbed/llm_integration/` skeleton with: `base_lm.py` (Phi-3-mini loader), `bridge.py` (2-layer MLP scaffold), `substrate_interface.py` (bipolar codeword <-> Path D depth=5 retrieve glue), `smoke_test.py` (forward-pass smoke), `baseline_eval.py` (lm-eval-harness on LLM-only at ARC/HellaSwag/PIQA/BoolQ/WinoGrande)
- Report file: `notes/testbed_decisions_2026-05-31.md` (or appropriate date) appending a "Week 1 substrate-LLM feasibility smoke" section with GO/NO-GO recommendation + per-gate measurement
- Status_log entry: importance=HIGH, source=testbed, plain_language="Week 1 substrate-LLM feasibility smoke [PASS / FAIL on which gates]; recommend [GO / NO-GO / pivot to X] for Weeks 2-6"

Week 1 budget: ~$0 if local; ~$30-50 if cloud H100. Wall: ~1 week single-person.

## WEEKS 2-6 (only if Week 1 GO)

Per `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` build plan section "4-6 weeks single-person, marsh@home GPU (8GB VRAM)":
- Week 2: Phase 1 bridge-only training (frozen base) on 50K synthetic substrate-augmented examples
- Week 3: Multi-hop iteration with Rescue C (substrate autonomous Path D depth=5)
- Week 4: Phase 2 QLoRA on Phi-3-mini-4bit attention + MLP layers
- Week 5: Substrate-favored evaluation suite + LLM-only vs LLM+text-RAG vs LLM+substrate comparison
- Week 6: Buffer + polish + write-up

Each week-end emits a status_log entry + appends to `notes/testbed_decisions_*.md` for visibility.

## REPORTING BACK

When the build finishes (Week 6 OR earlier kill if substrate-augmented gains don't materialize):
1. Write `notes/testbed_substrate_llm_integration_v1_2026-05-31.md` (or appropriate completion date) with: final benchmark numbers, code paths, replication recipe, failure modes encountered, recommendation for production-readiness
2. File `notes/strategy_request_to_strategy_substrate_llm_integration_v1_results_<date>.md` for orchestrator to cap_map the row (LIFT 🔬 -> 🟢 / 🟡 / ❌ per results)
3. Status_log entry importance=CRITICAL summarizing the load-bearing product-positioning finding

## SCOPE CLARIFICATIONS

**In scope (testbed implements):**
- Phi-3-mini base LM loading + tokenizer + inference loop
- Bridge MLP architecture + training infrastructure  
- Substrate -> bipolar codeword glue (read from existing substrate W; emit bipolar vectors)
- Path D depth=5 autonomous multi-hop integration (Rescue C)
- Synthetic substrate-augmented training data construction
- lm-evaluation-harness integration
- LLM+text-RAG baseline (FAISS over Wikipedia subset; ~standard RAG implementation)
- 3 substrate-favored bespoke benchmarks (edit-then-query, deletion-cert audit, provenance citation)

**Out of scope (research re-engages later):**
- Modifying substrate's core W / Path D / codebook construction (these are validated; do not touch)
- Theoretical analysis of why the integration works/fails (research drills if needed when results land)
- Pattern 4 (Memory Layers at Scale / DNC-style trainable VSA layer INSIDE the LLM) -- this is Phase 3+ ambition, NOT this build
- Bipolar query head training with full straight-through estimator + sign() at training time -- use continuous-relaxed (tanh) during training per the research note
- Decision-time architecture pivots (escalate to research before changing the bridge architecture)

**Out of scope for testbed (orchestrator owns):**
- Cap_map row addition / LIFT decisions (research's strategy request covers this)
- Cloud-cost approval (>$50 spend requires orchestrator + user assent)
- Experiment-queue refill (this is NOT a queueable experiment; it's a multi-week engineering build)

## RISKS (carried forward from research note)

Top 3 (the research note lists 6):
1. **Query-decomposition bottleneck at 1-3B (HIGHEST research-risk)** -- Mitigated by Rescue C; if Rescue C insufficient, escalate to Rescue A (train decomposition into Phase 2 LoRA signal) or Rescue B (use larger LLM via API for offline decomposition during data generation)
2. **Bridge-alignment training (HIGHEST engineering-risk)** -- Unpublished bipolar-to-LLM-input direction; mitigate with continuous-relaxed codewords during training + sign() at deployment
3. **8GB VRAM ceiling** -- Decision gate (a); if user picks 8GB and Phase 2 QLoRA wall-time exceeds expectations, fall back to bridge-only Phase 1 results as the deliverable

## Confidence

P_deflated for working end-to-end build delivering substrate-augmented gain on at least one benchmark within 4-6 weeks:
- On 24GB GPU: **0.40-0.45**
- On 8GB GPU: **0.25-0.30**

P_deflated for defensible product-positioning demonstration (substrate-favored benchmarks + audit + provenance work even without absolute-quality gain): **0.55-0.65**

P_deflated for >=20% multi-hop QA accuracy gain at 1-3B scale: **0.45** (from Subagent B; novel-synthesis cap not binding)

## Files of interest

- `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` (PRIMARY engineering spec; read in full)
- `notes/strategy_request_to_strategy_substrate_llm_deep_integration_2026-05-31.md` (cap_map proposal; orchestrator side)
- `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (this morning's queue-weighting context; Missing #1 is what this build delivers)
- `notes/research_alt_edit_isolation_v1_2026-05-31.md` (audit-by-construction property that's part of substrate-distinctive demonstration)
- `notes/substrate_capability_map.md` v290-v291 (Path D / Modern Hopfield / ICL via pool / autoregressive generation / real-time learning -- the substrate properties this integration depends on)
- Memory: `project_substrate_killer_features_2026-05-26.md`, `project_substrate_strategic_inversion_48h_2026-05-26.md`

## DECISIONS RESOLVED (user 2026-05-31, work-start UNBLOCKED)

- **(a) GPU resource: LOCAL REMOTE DESKTOP (marsh@home or equivalent).** User explicitly preferred local over cloud. Default assumption is marsh@home 8GB VRAM (Phi-3-mini-4bit / QLoRA path; P_def 0.25-0.30). **Verification step at Week 0 start:** testbed runs `nvidia-smi` (or equivalent) on the remote desktop to confirm actual VRAM; if >8GB available (e.g., RTX 3090/4090 24GB), upgrade base LM to Phi-3-mini-fp16, expect 4-8x faster training wall, P_def lifts to 0.40-0.45. NO cloud spend authorized; if a hardware blocker requires cloud, escalate to orchestrator + user before any cloud-runner activation.

- **(b) Commitment depth: WEEK 1 FEASIBILITY SMOKE FIRST.** Do NOT commit to full 4-6w upfront. Week 1 deliverables (below) are the GO/NO-GO gate. After Week 1 PASS, full 4-6w build commits with confidence. After Week 1 FAIL, we know what to fix or pivot.

- **(c) Queue sequencing: WEEK 0 = MISSING 7 FIRST, then WEEK 1 SMOKE, then WEEKS 2-6.** Missing 7 (LLM-integration latency budget characterization) gates the architectural assumption: the soft-prompt prefix-injection design presumes substrate Path D + bridge fit inside the LLM's per-token generation window (typically 10-50ms). Measure this before building. Missing 2 (storage efficiency) + Missing 3 (audit-trail rotation) are CPU-bound parallel work that doesn't gate this build; testbed may interleave them with weeks 2-6 GPU training time, or defer.

## WEEK 0: MISSING 7 -- LLM-INTEGRATION LATENCY BUDGET CHARACTERIZATION (~1 week wall)

**Why before Week 1**: the recommended starting architecture assumes substrate Path D depth=5 + bridge MLP forward pass fits within the LLM's per-token generation latency window (10-50ms is the published range for small LMs). If substrate ops take 100ms+, the soft-prompt prefix-injection pattern needs rework (batched-async, precomputed-prefix, or coarser-granularity integration). Resolving this BEFORE Week 1 saves 1-3 weeks of wrong-design rework.

**Measurements (testbed instruments, no training):**

1. **Substrate baseline latency on the target hardware:**
   - Single store at N=4096 and N=8192 (current published: ~530us at N=16384; need same at the prototype's N)
   - Single retrieve (Path D depth=1) at N=4096, K_paths=500
   - Path D depth=5 retrieve at N=4096, K_paths=500 (the production multi-hop op)
   - Use 5 seeds, report mean + p99
2. **Bridge MLP latency (scaffold the 2-layer MLP, no training):**
   - Forward pass R^4096 -> R^2048 -> R^d_model (Phi-3-mini d=3072), batch_size=1 and batch=8
   - Reverse direction R^d_model -> R^4096
3. **Phi-3-mini-4bit token-generation latency on the target GPU:**
   - Per-token latency at seq_len in {128, 512, 2048}
   - Mean + p99 across 100 generations
4. **End-to-end integrated forward-pass:**
   - Phi-3-mini emits query head -> substrate Path D depth=5 -> bridge -> prefix tokens -> Phi-3-mini decoder
   - Measure total wall per integrated query

**Decision criteria:**
- **PASS** (proceed to Week 1 substrate-LLM smoke): substrate Path D depth=5 + bridge round-trip < 50ms p99. Soft-prompt prefix-injection design viable.
- **MIDDLE** (proceed to Week 1 with design caveats): in [50ms, 150ms] -- design works but latency tight; mention as deployment-deployment caveat in eval.
- **FAIL** (escalate to research before Week 1): >150ms p99. Substrate-side throughput is the bottleneck; needs research drill on async-batched or precomputed-prefix variants BEFORE committing to Week 1 build.

**Deliverable: `notes/testbed_missing7_llm_integration_latency_v1_<date>.md`** with the 4 measurements + PASS/MIDDLE/FAIL classification + recommendation for Week 1.

**Wall budget:** ~1 week single-person; CPU + small GPU profiling.

## WEEK 1 GATE (after Missing 7 PASS)

Week 1 feasibility smoke per the existing build plan above. Decide GO/NO-GO for Weeks 2-6 based on the four gates already specified (bridge mechanical-connect / baseline Phi-3-mini numbers / no hardware blocker / substrate Path D depth=5 integration works in the testbed environment).

## SEQUENCE SUMMARY

| Week | Work | Owner | Gate at end |
|---|---|---|---|
| 0 | Missing 7: LLM-integration latency budget | testbed | PASS / MIDDLE / FAIL on substrate-fits-in-LLM-token-window |
| 1 | substrate-LLM feasibility smoke (Phi-3-mini-4bit baseline + bridge scaffold + smoke forward-pass) | testbed | GO / NO-GO for Weeks 2-6 |
| 2 | Phase 1 bridge-only training (frozen base, 50K synthetic examples) | testbed | bridge converges; LLM-only baseline preserved within 5pp |
| 3 | Multi-hop iteration with Rescue C (substrate-autonomous Path D depth=5) | testbed | substrate-augmented MuSiQue beats LLM-only by >=10pp |
| 4 | Phase 2 QLoRA on Phi-3-mini-4bit | testbed | LoRA boost measurable vs frozen-base |
| 5 | Substrate-favored eval suite + 3-way comparison | testbed | bespoke benchmarks show substrate-distinctive capabilities |
| 6 | Buffer + polish + write-up + cap_map LIFT proposal to orchestrator | testbed -> orchestrator | research delivery files testbed_substrate_llm_integration_v1_<date>.md |

Parallel CPU-bound work (any week with available person-time): Missing 2 (storage efficiency analysis) + Missing 3 (audit-trail rotation) per `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md`.

Testbed begins Week 0 immediately upon reading this handoff. No further user confirmation required; surface to orchestrator if any of the 6 risks materializes in a way that requires re-architecting.
