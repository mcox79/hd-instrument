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

## EVALUATION RIGOR PROTOCOL (locked-in before Week 5; testbed reads + applies throughout)

User raised the question: are we measuring rigorously enough to make causal claims about substrate contribution? Standard ML eval rigor is necessary but NOT sufficient here -- the Phase 2 QLoRA introduces a confounder that needs explicit control. The protocol below makes the substrate-vs-baseline comparison causally interpretable.

### 1. Mirror LLM implementation (load-bearing requirement)

Same Phi-3-mini-4bit weights, same GPU, same Python/torch/transformers versions, same lm-evaluation-harness commit hash, same random seeds.

Three eval conditions per benchmark question:
- **LLM-only**: Phi-3-mini-4bit; standard prompt structure `[Question] [Answer:]`
- **LLM+text-RAG**: same Phi-3-mini-4bit + FAISS-retrieved Wikipedia passages stuffed into context: `[Retrieved passages] [Question] [Answer:]`
- **LLM+substrate**: same Phi-3-mini-4bit + substrate-retrieved bipolar codewords projected through bridge into soft-prompt prefix: `[substrate-prefix-tokens] [Question] [Answer:]`

All three use IDENTICAL: decode params (temperature, top-p, top-k, max_tokens), seed, compute budget cap.

### 2. Phase 2 QLoRA confounder control (HIGHEST-rigor item)

**Problem**: when Phase 2 fine-tunes the base on substrate-augmented examples, the LLM+substrate condition benefits from BOTH (a) substrate retrieval at inference AND (b) the fine-tune signal. Without controlling (b), a Week 5 "+12pp on MuSiQue" gain could be a fine-tune effect (the model learned MuSiQue style from the training data), not a substrate effect.

**Control variant**: train an LLM-only-control with the SAME Phase 2 QLoRA, on the SAME substrate-augmented training data, but with the substrate prefix MASKED to a null/empty-prefix token sequence during training. This control variant has been fine-tuned identically EXCEPT it never saw the substrate prefix during training, so any LLM+substrate gain over THIS control isolates the substrate contribution.

Final 4-way comparison at Week 5:
- (i) LLM-only (no fine-tune)
- (ii) LLM-only-control (Phase 2 QLoRA on null-prefix training data)
- (iii) LLM+text-RAG (no fine-tune)
- (iv) LLM+substrate (Phase 2 QLoRA on substrate-prefix training data)

The "substrate effect" is rigorously `(iv) - (ii)`, not `(iv) - (i)`. Report both deltas.

### 3. Statistical protocol

- Minimum **3 random seeds** per condition; report mean + min/max + standard deviation
- **Paired comparisons**: same set of questions run across all 4 conditions; per-question delta computed; bootstrap CI over 1000 resamples
- **Multiple-comparison correction**: Bonferroni or Benjamini-Hochberg across the 6 paired comparisons ((i)-(ii), (i)-(iii), (i)-(iv), (ii)-(iii), (ii)-(iv), (iii)-(iv))
- Pre-register the PRIMARY hypothesis test BEFORE running Week 5: "LLM+substrate (iv) beats LLM-only-control (ii) by >=10pp on MuSiQue EM at p<0.05 across 3 seeds" -- this is THE claim Week 5 lives or dies on

### 4. Per-query latency measurement

End-to-end wall measured per question, not just LLM inference:
- LLM forward-pass time (Phi-3-mini generation)
- Substrate retrieval time (Path D depth=5 for LLM+substrate; FAISS lookup for LLM+text-RAG)
- Bridge MLP forward time (LLM+substrate only)
- Total wall = sum of above

Report p50 + p99 per condition. Same compute budget cap enforced across conditions (e.g., 30 second hard timeout per question).

### 5. Substrate atom-population protocol

For LLM+substrate condition on benchmarks like MuSiQue / HotpotQA / 2WikiMultihop: populate substrate W from the benchmark's gold-context passages (parsed into entity-relation triples or atomic facts). For text-RAG: index the same passages in FAISS. **Both retrieval conditions get the same source corpus** -- substrate gets it as bipolar atoms in W; text-RAG gets it as token sequences in FAISS index. This isolates retrieval-MECHANISM differences from corpus differences.

For TriviaQA closed-book: substrate gets a Wikipedia subset; text-RAG gets the same Wikipedia subset. Same atom-population scale per benchmark; document the size + composition per benchmark.

### 6. Substrate-favored bespoke benchmarks (testbed designs Week 5)

Three benchmarks that test substrate-distinctive capabilities the LLM cannot deliver alone:

**(A) Edit-then-query**: 1000 questions over a substrate populated with K=2000 facts; for 200 of those questions, edit the gold answer (substrate's edit primitive on (k_v, ov, nv)); measure whether each condition serves the UPDATED answer or stale. LLM-only and LLM-only-control will serve stale (no edit mechanism); LLM+text-RAG depends on whether the FAISS index was re-indexed (typically NO in production = stale); LLM+substrate uses the edited W and should serve updated. **Metric**: post-edit accuracy on the 200 edited questions.

**(B) Deletion-cert audit**: 100 questions where the gold fact was previously erased from substrate via M2 log-structured-store deletion-cert; verifier checks whether the substrate-augmented LLM response contains the erased fact (it should NOT). Each substrate query produces a cryptographic deletion-cert that the auditor verifies. LLM-only / text-RAG cannot produce audit certs. **Metric**: (a) post-deletion accuracy (should drop to 0 for properly-deleted facts); (b) audit-cert verifiability (testbed implements verifier; counts cert-verified responses).

**(C) Provenance citation**: 500 multi-hop questions; for each substrate-augmented response, the bridge surfaces which substrate atoms contributed (via Path D's compositional decomposition + per-hop posteriors); testbed checks whether the cited atoms match the gold-evidence atoms. LLM-only / text-RAG cannot produce atom-level provenance. **Metric**: cited-atom precision + recall vs gold evidence.

### 7. Benchmark dataset versioning

Pin: lm-evaluation-harness git commit hash; HuggingFace datasets versions for ARC/HellaSwag/PIQA/BoolQ/WinoGrande/TriviaQA/MuSiQue/HotpotQA/2WikiMultihop; FAISS version. Record in `notes/testbed_decisions_*.md` at Week 0 (so the run is reproducible).

### 8. Failure-mode logging

For each Week 5 benchmark run, log per-question outcomes across all 4 conditions in JSONL: question_id, condition, response, gold, correct (bool), wall_ms, retrieved_atoms (substrate only), retrieved_passages (text-RAG only). Enables post-hoc qualitative analysis: where does substrate beat text-RAG? Where does the QLoRA-control beat LLM-only without any retrieval? Failure-mode tables surface the substrate-distinctive vs fine-tune-distinctive cases.

### 9. Pre-registration

Before Week 5 evaluation kicks off, testbed writes a brief pre-registration to `notes/testbed_substrate_llm_prereg_<date>.md`:
- Primary hypothesis (the one Week 5 lives or dies on)
- Secondary hypotheses (the 6 paired comparisons)
- Per-benchmark expected directionality (e.g., ARC: no delta; TriviaQA: +5-15pp; MuSiQue: +10-30pp; bespoke benchmarks: substrate-only capability)
- HARD-PASS / HARD-FAIL thresholds per benchmark
- Statistical test + multiple-comparison correction method

This locks the claims testbed will make BEFORE seeing the data.

## REVISED BASELINE (post-optimization drill 2026-05-31; supersedes original Pattern 3 baseline)

Research session optimization drill (`notes/research_substrate_llm_interface_optimization_v1_2026-05-31.md`) identified 3 high-impact deviations from the original baseline that lift joint P_def by +0.18-0.29. Cost: ~1 extra week training wall on 8GB. Net build window still 4-6 weeks. **TESTBED USES THE REVISED BASELINE for Week 1+ design.** Week 0 Missing 7 latency-budget measurements proceed unchanged (architecture-agnostic profiling).

### Revised Deviation 1: Q-Former cross-attention bridge (replaces 2-layer MLP)

- **Architecture**: Q-Former-style cross-attention bridge with **8-16 learnable query tokens PER substrate codeword** (start with 8; ablate to 16 if Phase 1 underperforms)
- **Parameter count**: ~30-50M params (vs 14.7M MLP baseline)
- **Why**: BLIP-2 ablation shows cross-attention preserves structure that MLP destroys; specifically the per-hop posterior structure (~9 bits sparsely concentrated in 4096-dim codeword, NOT uniformly distributed). MLP is a flat compressor; Q-Former's bottleneck is selective.
- **Training time**: Phase 1 bridge-only ~8-20h on A100, ~32-80h on 8GB consumer
- **Implementation note**: Use HuggingFace transformers `Blip2QFormerModel` or equivalent as scaffolding; cross-attention keys+values are the substrate codewords (passed through a linear embedding layer to handle bipolar -> continuous), queries are learnable token vectors

### Revised Deviation 2: BLIP-2 two-stage training (replaces single-stage end-to-end)

**Stage 1 (bridge-only pre-training, ~1-2 weeks wall on 8GB):**
- Bridge trained against frozen substrate with **three objectives** (BLIP-2 ITC/ITM/ITG analogs):
  - **Codeword-text contrastive loss (ITC)**: minimize distance between bridge-projected codeword and correct answer embedding; maximize distance to negatives
  - **Codeword-answer matching (ITM)**: binary classifier head over bridge output: "does this codeword retrieve the correct candidate?"
  - **Codeword-conditioned generation (ITG, optional)**: small decoder head that generates the correct answer text from bridge output -- enables generative loss signal even before LLM joining
- Bridge weights at Stage 1 end initialize Stage 2

**Stage 2 (joint bridge + LLM, ~1 week wall on 8GB):**
- LLM frozen; bridge fine-tuned with **next-token loss only** against the LLM
- **Monitor codeword-retrieval-accuracy on held-out validation set during Stage 2**; halt Stage 2 if drops more than 5% below Stage 1 endpoint (catches the discriminability-overwrite failure mode)

**Implementation note**: Stage 1 dataset is `(codeword, correct_answer, incorrect_candidates)` triples; can be constructed entirely from substrate population (no LLM queries required). Stage 2 dataset is `(prompt, substrate_codeword, gold_completion)` from real benchmark data (MuSiQue/HotpotQA/synthetic substrate-augmented Q&A).

### Revised Deviation 3: Per-hop codeword sequence as separate prefix-token groups

- **Output format**: Substrate Path D depth=5 emits **ALL 5 hop posteriors** (not just final converged). Bridge produces 5 prefix-token groups (8 tokens each = 40 prefix tokens total at depth=5).
- **Why**: CoT mechanistic literature (Nag et al. 2025) shows intermediate reasoning states encode transferable features above ~2.8B scale; 3.8B Phi-3-mini is just above this threshold
- **Context overhead**: 40 prefix tokens / 2048 prompt window = ~2% (acceptable)
- **Fallback**: if Stage 1 reconstruction loss is similar between per-hop and single-prefix variants, fall back to single-prefix (Rescue C original) to save context budget for user-question

### Revised Codebook representation: HYBRID bipolar storage + continuous bridge projection

- Substrate stores + computes in bipolar throughout (unchanged)
- Bridge receives raw bipolar {-1,+1}^4096 codeword AND projects through continuous embedding layer immediately at bridge input
- **NEVER binarize inside the bridge during training** (avoids the spec'd-tanh train-test distribution gap)
- This is the natural pattern with Q-Former cross-attention (queries continuous; keys can be bipolar without internal binarization)

### Updated trainable parameter count

- Q-Former bridge: ~30-50M params
- Query read-out head (LLM -> bipolar codeword for initial query emission): ~12.6M params
- Optional ITG decoder head for Stage 1: ~5-10M params (small)
- Phase 2 QLoRA on Phi-3-mini-4bit (if Week 1 GO): ~30M params
- **Total trainable**: ~80-100M params (vs ~57M original spec). Still <3% of base LLM.

### Decision matrix for testbed (Week 0 / Week 1 design freezes)

| Choice | Original spec | REVISED spec (use this) |
|---|---|---|
| Bridge architecture | 2-layer MLP | Q-Former cross-attention 8-16 query tokens |
| Training stages | 1-stage end-to-end | 2-stage: Stage 1 bridge-alone (contrastive+ITM+ITG); Stage 2 joint with next-token |
| Codebook handling | Continuous-relaxed (tanh) during training, sign() at deploy | Hybrid: bipolar throughout; continuous projection at bridge input only |
| Substrate output | Final converged codeword only (Rescue C) | All 5 hop posteriors as 5 prefix-token groups |
| Total trainable params | ~57M | ~80-100M |
| Phase 1 wall on 8GB | 16-32h | 40-80h (about +1 week) |
| Joint P_def | 0.25-0.30 | **0.43-0.55** |

### Deferred to Phase 2+ (NOT in 4-6w window)

These were considered but defer:
- Adaptive Path D depth based on LLM uncertainty (highest-leverage substrate-unique inference trick; needs dynamic Path D depth + uncertainty signal extraction)
- Speculative substrate prefetch (TeleRAG-style 1.53x latency reduction; needs substrate async API + LLM forward-pass hooks)
- Trainable VSA-style memory layer drop-in (DNC pattern; from-scratch pretraining; multi-month scope)

Testbed scopes these as Phase 2 targets if Phase 1 PASSES.

### Open questions empirically resolvable during Phase 1 (updated post-aggressive-eval)

1. Does Q-Former cross-attention handle bipolar {-1,+1} keys without softmax-attention-weight collapse? **Smoke-testable Week 1.**
2. Does Stage 2 next-token loss overwrite Stage 1 discriminability? **Empirical Week 2 with halt criterion above.**
3. How much per-hop intermediate benefit is scale-gated at 3.8B vs 7B+? **Empirical Week 3 via Ablation B below.**
4. Can the bridge be trained with synthetic substrate outputs vs requiring paired (codeword, LLM-correct-answer) data? **Empirical Week 2. HIGHEST engineering risk.**
5. Does real-time learning during eval preserve Path D's confidence calibration? **Empirical Week 4 via mixed-confidence ablation.**
6. At what LLM-uncertainty threshold does adaptive depth provide net benefit? **Empirical Week 3 via Ablation A below; calibrate threshold on held-out subset first.**

## AGGRESSIVE-EVAL ADDITIONS (locked-in 2026-05-31; supersedes "deferred to Phase 2" framing where overlapping)

User pushed back on Phase 2 deferrals ("why are we deferring some of the most exciting things?"). Aggressive audit of all deferrals + cap_map-validated capabilities surfaced 3 over-conservative deferrals + 3 implicit ablations + 1 missing benchmark + hardware fallback spec. Full reasoning in `notes/research_substrate_llm_aggressive_eval_v1_2026-05-31.md`. Testbed implements the additions; they extend Phase 1 budget by ~1.5-2 weeks (total ~7-8 weeks vs original ~6-7).

### 3 PROMOTIONS from Phase 2 to Phase 1 (add to build spec)

**Promotion 1: Adaptive Path D depth based on LLM uncertainty (~1-2 days)**
- LLM uncertainty signal: next-token-distribution entropy from Phi-3-mini logits
- Routing rule: `depth = 5 if entropy > threshold else 1`; threshold calibrated on held-out subset Week 3
- Fixed-max-length prefix (40 tokens budget for depth=5) + zero-mask unused hops at lower depths → avoids variable-length prefix engineering
- Substrate-unique inference optimization; impossible in dense RAG

**Promotion 2: Real-time learning during inference (~1 day)**
- After each LLM+substrate correct answer, substrate writes the (question_codeword, answer_codeword) atom to W
- Substrate's edit-isolation (T2 PASS 45/45 cells) prevents corruption during eval
- Demonstrates v191 ✅ Validated Tier-2 killer capability (`wave14_realtime_inference_learning_v1_rerun` HARD_PASS at 11x threshold) -- the strongest empirically-validated substrate-distinctive feature; should not be omitted
- LLM-only-control variant does NOT write back to anywhere; LLM-only has no write mechanism

**Promotion 3: Mixed-confidence Path D retrieval (~2 days)**
- Path D's Bayesian posterior produces a confidence scalar per hop (entropy of posterior over K_paths=500)
- Bridge surfaces this scalar as extra prefix-token dimension (~1 dim per hop)
- LLM trained to emit confidence-threshold token in output; eval harness parses + applies abstention threshold
- Path D mixed-confidence validated v290 T1 (conservative-calibration; safe direction = under-predicts)

### 3 ABLATIONS (add to Week 5 eval suite; ~5-8 days total wall)

**Ablation A: static-depth-5 vs adaptive-depth (~3-5 days)**
- Variant (a1): LLM+substrate with fixed depth=5 always (revised baseline)
- Variant (a2): LLM+substrate with adaptive depth per Promotion 1
- Measures whether adaptive-depth provides real gain or whether depth=5 alone is sufficient
- Pre-reg threshold: adaptive beats static-depth-5 by >=2pp on at least 1 multi-hop benchmark for ablation to count as supportive

**Ablation B: per-hop prefix groups vs single converged codeword (~2-3 days)**
- Variant (b1): all 5 hops as separate prefix-token groups (revised baseline; 40 prefix tokens)
- Variant (b2): only final converged codeword (8 prefix tokens)
- Tests the CoT-mechanistic prediction that per-hop intermediate states transfer at 2.8B+ scale
- Pre-reg threshold: per-hop beats single-converged by >=3pp on at least 1 multi-hop benchmark

**Ablation C: frozen-base Stage 2 vs Phase-2-QLoRA Stage 2 (~0 incremental wall)**
- Variant (c1): frozen Phi-3-mini-4bit, Stage 1 + Stage 2 bridge training only
- Variant (c2): Phase-2-QLoRA-on-Phi-3-mini-4bit, full bridge + LLM-LoRA training
- Reuses the Phase 2 QLoRA confounder control variant from the eval-rigor protocol
- Pre-reg threshold: QLoRA beats frozen Stage 2 by >=5pp on at least 1 benchmark to justify the extra training week

### Hardware fallback 5-tier ladder (explicit decision criteria)

OOM-trigger: training-loop forward pass at batch_size=1 + grad-accum=4 + Stage 2 max seq_len=1024.

| Tier | Bridge | Base LLM | Path D | Expected P_def (8GB) |
|---|---|---|---|---|
| Tier 1 (revised baseline) | Q-Former 8 query tokens | Phi-3-mini-4bit | depth=5 per-hop | 0.51-0.65 |
| Tier 2 (Q-Former OOM) | 2-layer MLP | Phi-3-mini-4bit | depth=5 per-hop | 0.40-0.55 |
| Tier 3 (Phi-3-mini OOM at Tier 2) | Q-Former 8 query tokens | TinyLlama-1.1B fp16 | depth=5 per-hop | 0.30-0.45 |
| Tier 4 (everything OOM at Tier 3) | 2-layer MLP | TinyLlama-1.1B fp16 | depth=3 single-prefix | 0.20-0.35 |
| Tier 5 (Tier 4 OOM) | escalate to user | escalate | escalate | N/A; no silent cloud downgrade |

### Eval-rigor additions

**Test-set contamination acknowledgment (~1 day)**
- Phi-3-mini-4bit was pretrained on web data that likely overlaps with MuSiQue / HotpotQA / 2WikiMultihop / TriviaQA training portions
- Report verbatim question-string contamination check (look for question strings in Phi-3-mini's reported training corpus or via a contamination-detection tool)
- **Strongest defensible claims come from substrate-favored bespoke benchmarks** (constructed synthetically from substrate populations; CANNOT be in any LLM pretraining set)

**4th bespoke benchmark: "real-time-learn-then-query" (~1-2 days)**
- 500 questions; substrate is initially empty (or populated with K=500 unrelated facts)
- Per question: (i) LLM-only answers using pretraining knowledge; (ii) LLM+substrate runs LLM-only first, writes (question, answer-fragment) pair to substrate via Promotion 2, then re-answers SAME question
- LLM+substrate should show LARGER accuracy on second pass than LLM-only does on second pass (because LLM-only didn't update)
- Demonstrates the "every query makes substrate smarter" property
- Substrate-unique; LLM-only and LLM+text-RAG cannot match this

### Updated Phase 1 budget table

| Phase 1 item | Original wall | Revised wall |
|---|---|---|
| Week 0 Missing 7 latency | 1 week | 1 week |
| Week 1 feasibility smoke | 1 week | 1 week |
| Week 2 Stage 1 bridge training | 1 week | 1 week |
| Week 3 multi-hop iteration + Promotion 1 + adaptive-depth threshold calibration | 1 week | 1 week |
| Week 4 Phase 2 QLoRA + Promotion 2 + Promotion 3 + halt-criterion monitoring | 1 week | 1 week |
| Week 5 4-condition eval + 3 ablations + 4 bespoke benchmarks + contamination check | 1 week | **2 weeks** |
| Week 6+ buffer + polish + cap_map LIFT routing | 1 week | 1 week |
| **Total** | **6 weeks** | **7-8 weeks** |

### Updated joint P_def estimates

| Hardware path | Pre-optimization | Post-optimization | Post-aggressive-eval |
|---|---|---|---|
| 8GB marsh@home | 0.25-0.30 | 0.43-0.55 | **0.51-0.65** |
| 24GB GPU (cloud or local) | 0.40-0.45 | 0.55-0.65 | **0.63-0.75** |

Build is now ~coin-flip-or-better on 8GB hardware; materially different from "probably-not."

### What stays deferred (post-aggressive-eval; reasons audited)

| Item | Stays deferred? | Reason after aggressive audit |
|---|---|---|
| Speculative substrate prefetch | YES | Substrate at 1-3ms vs LLM token 10-50ms; LLM is latency-dominant; prefetch saves <5% wall; literature gain assumes inverted regime |
| Trainable VSA-style memory layer | YES | From-scratch pretraining; multi-month scope; genuinely Phase 3+ |
| Path E spectral coherence retrieval | YES (optional) | Niche use cases don't have a Phase 1 evaluation need; +1 week if added; modest payoff |
| N=8192 / N=16384 substrate operating point | YES | Bridge has not been validated at higher input dim; Phase 1 stays N=4096 |
| Compositional query construction via bind/unbind | YES | Substantial design work; LLM must emit structured queries |
| Concept drift detection mechanism | YES (parallel research) | Needs own ~2-3 week research drill before any engineering; dispatch in parallel |
| Cross-modal binding | YES | Phase 1 is text-only |
| Edit-with-impact-prediction | YES | Underlying SVD-cascade falsifier HARD_FAILED; killer feature parked |

Testbed should NOT add any of these to Phase 1 without orchestrator + research re-evaluation.

## EXTERNAL-FEEDBACK UPDATES (locked-in 2026-05-31; sharpens 3 areas of the bridge design)

User shared the bridge design with an external technical reviewer; 3 substantive points returned. Per-point evaluation in `notes/research_decisions_2026-05-31.md`. The 3 updates below tighten the spec:

### Update 1: VQ-Bottleneck Tier 1.5 fallback for LLM→memory query emission

**Problem the reviewer flagged**: STE + tanh-relaxation at the binarization step (sign() at deployment) has well-documented train/test distribution shift. Tanh values typically hover near 0 during training to maintain gradient flow; sign() violently snaps them to ±1 at inference. This is one of the load-bearing risks (a) in the "5 open questions" list above.

**Tier 1.5 fallback (use if Tier 1 STE training is unstable)**: replace the LLM→memory query emission path with a VQ-VAE-style bottleneck. The LLM's hidden state at the [QUERY] position passes through a small linear head producing a continuous readout vector; map to nearest centroid in a LEARNED CODEBOOK of memory-query centroids (k=512-2048 centroids; size TBD). Commitment loss + codebook update path per van den Oord et al. 2017 VQ-VAE.

**Why this fixes the problem**: at inference, the lookup is the SAME nearest-neighbor operation as at training — no train/test distribution shift. Bonus: the LLM emits one of a finite vocabulary of "query types", which likely IMPROVES training stability (constrained output space).

**Trigger conditions to pivot Tier 1 → Tier 1.5**: any of (a) Stage 2 retrieval accuracy gap between train (continuous-tanh) and eval (sign()-binarized) >5pp; (b) Stage 1 contrastive loss fails to converge after 3 epochs; (c) downstream multi-hop accuracy below 50% at Week 3 ablation A.

**Engineering cost of pivot**: ~3-5 days. Replaces the linear query-readout head with the VQ codebook lookup; rest of the architecture unchanged. Adds k_centroids × d_model params (~1.5-6M extra for k=512, d=3072 to k=2048, d=3072).

**Decision authority**: testbed pivots Tier 1 → Tier 1.5 inline (does not require orchestrator re-arbitration) IF the trigger conditions fire AND testbed has confirmed via 1-2 day diagnostic that STE is the culprit (not e.g. data scale or learning rate).

### Update 2: Stage 1 hard-negative generation via teacher-model bootstrap

**Problem the reviewer flagged**: Stage 1 contrastive + ITM losses need HARD negatives to avoid the bridge learning shallow lexical-matching shortcuts. Original spec just said "construct paired examples from substrate population" without specifying negative-mining.

**Concrete addition**: bootstrap Stage 1 training data via teacher-model synthesis. Use Anthropic API (key already available per `project_anthropic_api_key_available`; Tier 2b LLM comparison harness already integrates with the API) to generate (query, ground-truth retrieval trace, hard-negative trace, final answer) tuples. The teacher model is provided with a graph snapshot of the substrate's stored facts/chains and asked to construct queries where the hard-negative is plausible-but-wrong (e.g., adjacent fact with the same predicate; off-by-one-hop chain; correct entities but wrong relation).

**Volume**: ~50K tuples for Stage 1 training (~$50-150 Anthropic spend; within reasoning-amortization experiment's filed budget). Adds ~1 day setup + ~6 hours generation wall.

**Validation gate**: after generation, manually inspect ~50 random tuples to verify the hard-negatives are actually plausible-but-wrong (not trivial random negatives). If <80% pass quality bar, re-prompt the teacher with sharper instructions; iterate.

**Reuse path**: tuple-generation pipeline becomes infrastructure for the reasoning-amortization experiment (`notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md`); not throwaway.

### Update 3: Zero-out ablation arm added to Phase 1 Week 3

**Problem the reviewer flagged**: per-hop prefix-token groups (40 prefix tokens at depth=5) may cause attention collapse at small/quantized base-LM scale. The LLM might just attend to the final prefix token and ignore the reasoning trace — treating memory as a single-hop lookup rather than mechanistic CoT.

**Diagnostic test (Week 3, runs alongside Ablation B)**: zero out the intermediate hop prefix tokens (keep only the final memory-state prefix token group), measure downstream accuracy.

**Pre-reg interpretation bands**:
- **CoT-effective**: ≥3pp accuracy drop on multi-hop benchmarks (MuSiQue / HotpotQA / 2WikiMultihop) when intermediate hops zeroed → LLM IS using the reasoning trace; per-hop prefix-token design pays off
- **Single-hop lookup**: <1pp drop → LLM is ignoring the reasoning trace; treating memory as a single-hop oracle. Per-hop prefix-token design is dead weight; revert to single-converged prefix
- **Partial**: 1-3pp drop → LLM uses the trace sometimes; consider Q-Former tuning (e.g., increase per-hop token count from 8 to 16) before deciding

**Cost**: ~0 incremental wall (re-runs Week 3 evaluation suite with the prefix-zeroing modification; ~1 day extra eval-run time).

**Why this matters for the build's positioning**: the per-hop prefix-token design is one of the 3 optimization-drill deviations from the original baseline (+0.04-0.07 P_def lift); if the zero-out ablation shows the LLM isn't using the trace at this scale, the lift collapses and the build returns to single-converged-codeword (Rescue C original framing).

### Updated open-question list (post-external-feedback)

7. **Does STE binarization actually train stably, or does Tier 1.5 VQ-Bottleneck become the default?** Empirical Week 2 (Stage 1 contrastive loss convergence) and Week 3 (eval retrieval accuracy gap).
8. **Does the teacher-model-generated hard-negative regime actually produce hard negatives, or does the LLM teacher generate easy-to-distinguish negatives that lead to shallow bridge learning?** Inspected at data-generation time + via Stage 1 contrastive loss curve.
9. **Does the LLM attend to intermediate hop prefixes at base-LM-3.8B scale, or does attention collapse to final-prefix-only?** Empirical Week 3 zero-out ablation; binary classifier on the LLM's behavior at this scale.

### What the external reviewer DID NOT address (carried forward)

The reviewer engaged with the LLM-side bridge but did NOT touch the substrate-side empirical risks:
- Structured-key envelope (drill α today; P_def 0.35 unmitigated; conclusion re-encoding mitigation needed)
- Inter-hop key construction gap (drill β today; substrate is retrieval primitive not reasoning primitive)
- 44K shared-rule-atoms threshold for spectral collapse (drill A today)

These remain the higher empirical risks. The bridge is well-grounded engineering; the substrate's structured-key behavior at production scope is the empirical unknown.
