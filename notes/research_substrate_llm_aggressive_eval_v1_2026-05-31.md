# Research: aggressive evaluation of substrate-LLM Phase 1 scope (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- "why are we deferring some of the most exciting things?" + "do another aggressive evaluation just to be safe"
Method: systematic audit of (a) every Phase 2 deferral, (b) every cap_map-validated capability not yet exposed, (c) substrate-unique inference tricks, (d) eval-rigor gaps, (e) hardware fallback paths, (f) implicit assumptions in the spec. Cross-referenced against `notes/substrate_capability_map.md` v290-v291.

## HEADLINE

Honest result of an aggressive audit: **I was over-conservative on 3 deferrals and under-considered 3 capabilities.** Adding all 6 lifts Phase 1 from "cheapest viable substrate-LLM demonstration" to "fullest substrate-killer-feature demonstration the 4-6w window admits." Cost: ~1.5-2 weeks additional engineering (total Phase 1 budget shifts from ~6-7 weeks to ~7-8 weeks; still inside the user's stated 24-36mo competitive window). Joint P_def lift estimate: **+0.08-0.15 above the post-optimization baseline** (8GB: 0.43-0.55 → 0.51-0.65; 24GB: 0.55-0.65 → 0.63-0.75).

## What I was wrong to defer (now PROMOTED to Phase 1)

### Promotion 1: Adaptive Path D depth based on LLM uncertainty

**Original deferral reason**: "Requires a dynamic-length prefix mechanism that most frozen LLM inference frameworks don't support cleanly."

**Why this was over-conservative**: variable-length prefixes ARE hard; but **fixed-max-length prefix with zero-masked unused hops** is trivial. Use the depth=5 prefix budget (40 tokens) always; at lower depths, zero out the unused-hop positions.

**Engineering cost**: ~1-2 days
- LLM uncertainty signal: next-token entropy from Phi-3-mini logits → 2 lines
- Dynamic depth: Path D already accepts depth parameter
- Routing: `depth = 5 if entropy > threshold else 1` → ~10 lines + threshold calibration

**Why substrate-unique**: Dense RAG retrievers (FAISS) don't have a "depth" parameter; you get one shot per query. Substrate's depth-as-parameter + per-hop independence make this trivial.

### Promotion 2: Real-time learning during inference

**Original omission reason**: Wasn't in the initial integration design space; treated as Phase 2.

**Why this was over-conservative**: This is **the ONLY ✅ Validated Tier-2 killer capability** in the substrate's cap_map (v191 `wave14_realtime_inference_learning_v1_rerun` FULL: bpc_online=2.198 vs bpc_frozen=2.745, delta=-0.548 bpc, **cleared HARD-PASS threshold by 11x**). Not exposing it in Phase 1 omits the strongest empirically-validated killer feature.

**Phase 1 implementation**: After each LLM+substrate answer, if the answer is correct (verifiable for benchmarks; or self-rated for open-ended), substrate writes the (question_codeword, answer_codeword) atom to W. Substrate's edit-isolation (T2 PASS 45/45) prevents corruption during the eval run. Each subsequent query sees a slightly-smarter substrate.

**Engineering cost**: ~1 day. Substrate's write primitive already exists; just call it inside the eval loop after each answer.

**Why substrate-unique**: Transformers cannot update weights at inference (would require re-training); substrate's rank-1 edit IS the update. This is the single capability that most distinguishes substrate from RAG.

### Promotion 3: Mixed-confidence Path D retrieval

**Original omission reason**: Considered scope-creep; the depth=5 retrieval was the "minimum viable" substrate output.

**Why this was over-conservative**: T1 path_d_mixed_confidence is VALIDATED (calib_dev=0.16-0.32; conservative-calibration; safe direction = substrate under-predicts confidence). The confidence-aware output is "production-deployable" per the v290 cap_map T1 honest-reading: "Path D is the ONLY confidence-aware-deployable mechanism among the three [B/D/E]."

**Phase 1 implementation**: Path D's Bayesian posterior produces a confidence scalar per hop (entropy of posterior over K_paths=500 candidates). Bridge surfaces this scalar as an extra prefix-token dimension (~1 token per hop). LLM learns to emit a confidence-threshold token in its output; downstream consumer (eval harness) parses + filters / abstains when below threshold.

**Engineering cost**: ~2 days. Bridge architecture needs minor extension (extra dim per hop); LLM training data needs (confidence, answer-correctness) pairs for the LLM to learn to use the signal.

**Why substrate-unique**: Dense RAG returns cosine-similarity scores but those don't correspond to retrieval *correctness*. Substrate's Bayesian posterior IS a calibrated correctness signal.

## What I missed entirely (3 new ablations needed)

The eval-rigor protocol (locked into testbed handoff this morning) covered statistical hygiene but missed **ablation rigor**. Without ablations, we can demonstrate "LLM+substrate beats LLM-only" but not "WHICH substrate properties drove the gain." For product positioning that matters.

### Ablation A: static-depth-5 vs adaptive-depth
- Two variants of LLM+substrate: (a1) fixed depth=5 always; (a2) adaptive depth per Promotion 1
- Measures whether adaptive-depth provides a real gain or whether depth=5 is good enough
- ~3-5 days incremental wall (one extra eval pass)

### Ablation B: per-hop prefix groups vs single converged codeword
- Two variants: (b1) all 5 hops as separate prefix-token groups (revised baseline); (b2) only final converged codeword
- Tests the CoT-mechanistic-prediction that per-hop intermediate states transfer at 2.8B+ scale; sanity-checks that the +0.04-0.07 P_def lift from D3 is real for Phi-3-mini-4bit
- ~2-3 days incremental wall

### Ablation C: frozen-base Stage 2 vs Phase-2-QLoRA Stage 2
- Two variants: (c1) frozen Phi-3-mini-4bit, only Stage 1 + Stage 2 bridge training; (c2) Phase-2-QLoRA-on-Phi-3-mini-4bit, full bridge + LLM-LoRA
- The eval-rigor protocol requires a Phase-2-QLoRA control variant; this ablation reuses it to also answer "is the QLoRA step worth the extra training week?"
- ~0 incremental wall (the control variant already exists)

All three ablations report PASS/MIDDLE/FAIL bands pre-registered before Week 5 evaluation kickoff.

## Hardware fallback tiers (locked in case of OOM)

If 8GB VRAM cannot accommodate the revised baseline (Q-Former + Phi-3-mini-4bit + per-hop prefix), step down through these tiers explicitly. Decision criterion at each Week-0 hardware-blocker surface: **OOM on training-loop forward pass at batch_size=1 + grad-accum=4 + Phase 1 Stage 2 max sequence length 1024**.

| Tier | Bridge | Base LLM | Path D depth | Expected P_def (8GB) |
|---|---|---|---|---|
| Tier 1 (revised baseline) | Q-Former 8 query tokens | Phi-3-mini-4bit | depth=5 per-hop | 0.51-0.65 |
| Tier 2 (Q-Former too heavy) | 2-layer MLP | Phi-3-mini-4bit | depth=5 per-hop | 0.40-0.55 |
| Tier 3 (Phi-3-mini too heavy) | Q-Former 8 query tokens | TinyLlama-1.1B fp16 | depth=5 per-hop | 0.30-0.45 |
| Tier 4 (both too heavy) | 2-layer MLP | TinyLlama-1.1B fp16 | depth=3 single-prefix | 0.20-0.35 |
| Tier 5 (everything is too heavy) | (escalate to user for cloud-or-pause decision) | (TBD) | (TBD) | N/A |

Tier 5 ONLY triggers escalation. Testbed does NOT silently downgrade past Tier 4 without orchestrator + user explicit assent (per the no-cloud-spend policy).

## What stays deferred (with explicit reasons after the aggressive audit)

### Speculative substrate prefetch (TeleRAG-style)
- **Why defer**: substrate Path D depth=5 = ~1-3ms GPU; Phi-3-mini-4bit per-token = ~10-50ms. LLM is latency-dominant, NOT substrate. Speculative prefetch saves <5% wall in this regime.
- **Revisit**: if Missing 7 Week 0 measurements show substrate latency >>10ms (unexpected; would change the analysis)
- **NOT a "low-cost" win at our scale** -- the literature gain of 1.53x assumes retrieval >> generation, which is INVERTED for us

### Trainable VSA-style memory layer drop-in (DNC pattern)
- **Why defer**: Requires from-scratch pretraining OR full LLM fine-tune. Multi-month scope.
- **Revisit**: Phase 3+ ambition; would need separate project planning cycle
- **Genuinely correct defer** -- 4-6w window cannot fit this

### Path E spectral coherence as alternative retrieval path
- **Why defer**: Path E's validated niche use cases (top-K candidate ranking + early-termination + sigma-tradeoff) don't have a clear use case in the Phase 1 evaluation suite. Multi-hop QA benefits from Path D; substrate-favored benchmarks expose Path D properties.
- **Revisit**: Phase 2 if specific use cases emerge (e.g., latency-sensitive deployment, narrow-domain retrieval)
- **Optional Phase 1 if testbed has bandwidth** -- could add as 5th eval condition (LLM+substrate-Path-D vs LLM+substrate-Path-E) -- but estimated +1 week and modest payoff

### N=8192 or N=16384 substrate operating point
- **Why defer**: Phase 1 stays at N=4096 to match the most-tested envelope. N=16384 is validated at substrate level (v291 max_M=4N) but the bridge has not been validated at that input dim; doubling N doubles bridge input params.
- **Revisit**: Phase 2 if Phase 1 PASSES at N=4096 and we want to push absolute capacity

### Compositional query construction via bind/unbind ops
- **Why defer**: Substantial design work. The substrate's binding algebra allows the LLM to compose queries algebraically (e.g., "facts about X bound with relation Y"), but this requires LLM to emit STRUCTURED queries (sequence of bipolar atoms + binding ops), not just a single query codeword.
- **Revisit**: Phase 2 if compositional generalization becomes a load-bearing claim

### Concept drift detection mechanism
- **Why defer**: NO research filed yet (Missing 6 from morning's research-focus-expansion). Needs its own ~2-3 week research drill before any engineering.
- **Revisit**: dispatch the research drill in parallel; engineering follow-on later

### Cross-modal binding
- **Why defer**: Phase 1 is text-only. Vision-language extension is out of scope.

### Edit-with-impact-prediction
- **Why defer**: SVD-cascade falsifier HARD_FAILED (per `project_substrate_killer_features_2026-05-26`); the underlying mechanism (predict edit side-effects via singular-mode cascade) has no validated substrate-physics framework. KILLER FEATURE PARKED.

## What got added to the eval suite

### New eval-rigor item: test-set contamination acknowledgment
- Phi-3-mini-4bit was pretrained on web data that likely overlaps with MuSiQue / HotpotQA / 2WikiMultihop / TriviaQA training portions
- Mitigation: report contamination check (look for verbatim question-string matches in Phi-3-mini's reported training corpus; flag any matches)
- Stronger mitigation: substrate-favored bespoke benchmarks (edit-then-query, deletion-cert audit, provenance citation) are SYNTHETICALLY CONSTRUCTED from substrate populations and CANNOT BE in any LLM pretraining set -- these benchmarks are the strongest defensible claims
- Adds ~1 day to Week 5 eval-rigor work

### New killer-feature exposure in eval: 4th substrate-favored bespoke benchmark "real-time-learn-then-query"
- 500 questions; substrate is initially empty (or populated with K=500 unrelated facts)
- For each question: (i) LLM-only condition answers using whatever it knows from pretraining; (ii) LLM+substrate condition runs LLM-only first, then writes the (question, answer-fragment) pair to substrate via Promotion 2's real-time-learn mechanism, then re-answers the SAME question to demonstrate substrate-augmented retention
- Substrate-augmented should show LARGER accuracy on the second pass than LLM-only on the second pass (because the LLM-only model didn't update)
- This is the demonstration of the "every query makes substrate smarter" property
- Specced for testbed; ~1-2 days to construct

## Updated Phase 1 budget

| Item | Original | Aggressive-eval revision |
|---|---|---|
| Base architecture (Q-Former + 2-stage + per-hop) | spec'd | unchanged |
| Adaptive Path D depth | DEFERRED | ADD (~1-2 days) |
| Real-time learning | OMITTED | ADD (~1 day) |
| Mixed-confidence retrieval | OMITTED | ADD (~2 days) |
| Ablation A (static vs adaptive depth) | not specced | ADD (~3-5 days) |
| Ablation B (per-hop vs single) | not specced | ADD (~2-3 days) |
| Ablation C (frozen vs QLoRA) | implicit | EXPLICIT (~0 incremental) |
| Hardware fallback tiers | not specced | ADD (~0 days; design spec only) |
| Test-set contamination check | not specced | ADD (~1 day) |
| 4th bespoke benchmark (real-time-learn-then-query) | not specced | ADD (~1-2 days) |
| **Total additional Phase 1 wall** | -- | **~10-15 days (~1.5-2 weeks)** |

Phase 1 total: ~6 weeks → ~7-8 weeks. Total project budget (Week 0 + Phase 1): ~8-9 weeks vs original 6-7 weeks. Still inside the 24-36mo competitive window from `project_substrate_strategic_inversion_48h_2026-05-26`.

## Updated P_def estimates

Joint P_def for "working end-to-end build delivering substrate-augmented gain on at least one benchmark AND demonstrating all substrate-distinctive killer features":

- **8GB GPU (revised aggressive): 0.51-0.65** (was 0.43-0.55 after optimization drill; was 0.25-0.30 pre-optimization)
- **24GB GPU: 0.63-0.75**

The lifts from the 3 promotions are non-additive with the optimization drill's 3 deviations (some overlap in expected gain). Net P_def increase from aggressive eval: **+0.08-0.15** above optimization-drill baseline. The build is now ~coin-flip-or-better on 8GB hardware, which is materially different from "probably-not."

## 5 open questions resolvable empirically during Phase 1

Carried forward from optimization drill + added from aggressive eval:

1. **Does Q-Former cross-attention handle bipolar {-1,+1} keys without softmax-attention collapse?** Untested in lit. Smoke-testable Week 1.
2. **Does Stage 2 next-token loss overwrite Stage 1 discriminability?** Mitigation: monitor + halt criterion. Empirical Week 2.
3. **How much per-hop intermediate benefit is scale-gated at 3.8B vs 7B+?** Lit suggests 2.8B is the threshold; 3.8B is marginal. Empirical Week 3 via Ablation B.
4. **Can the bridge be trained with synthetic substrate outputs vs requiring paired (codeword, LLM-correct-answer) data?** Data construction bottleneck; highest engineering risk. Empirical Week 2.
5. **Does real-time learning during eval preserve calibration?** Substrate's confidence calibration was validated standalone (T1); writing during eval may shift calibration. Empirical Week 4 via mixed-confidence ablation.
6. **At what LLM-uncertainty threshold does adaptive depth provide net benefit?** Empirical Week 3 via Ablation A; calibrate threshold on a held-out subset before running Ablation A.

## Recommended path forward

Amend the testbed handoff with:
1. **3 promotions** (adaptive depth, real-time learning, mixed-confidence) added to Phase 1 build spec
2. **3 ablations** (A: depth, B: per-hop, C: QLoRA) added to Week 5 eval suite
3. **Hardware fallback 5-tier ladder** spec'd explicitly
4. **Test-set contamination check** added to Week 5 eval-rigor protocol
5. **4th substrate-favored bespoke benchmark** (real-time-learn-then-query) added to Week 5
6. **Updated total Phase 1 budget** (~7-8 weeks vs ~6-7 weeks)
7. **Open questions list updated** with item 5 (calibration under real-time learning) and item 6 (uncertainty threshold)

This is the **honest most-aggressive Phase 1 scope** that fits the substrate's validated capability roster + 4-6 week engineering window. Anything cut from this would be artificial under-scoping; anything added would push into multi-month scope.

## Citations (incremental over optimization drill)

Internal cross-refs only (no new external lit-scan; aggressive eval is audit, not lit search):
- `notes/substrate_capability_map.md` v291 (Modern Hopfield N=16384 max_M=4N green LIFT; sparse-W large-N integration confirmed)
- `notes/substrate_capability_map.md` v191 line 133 (real-time learning ✅ Validated HARD_PASS at 11x threshold)
- `notes/substrate_capability_map.md` v290 T1 (Path D mixed-confidence calib_dev=0.16-0.32; conservative-calibration confirmed; "Path D is the ONLY confidence-aware-deployable mechanism")
- `notes/research_substrate_llm_deep_integration_v1_2026-05-31.md` (baseline architecture)
- `notes/research_substrate_llm_interface_optimization_v1_2026-05-31.md` (optimization drill; 3 deviations from baseline)
- `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (Missing 6 concept drift detection = stays deferred per aggressive eval)
- `project_substrate_killer_features_2026-05-26` (5 product-layer features; alignment check)
- `project_substrate_strategic_inversion_48h_2026-05-26` (24-36mo competitive window)
