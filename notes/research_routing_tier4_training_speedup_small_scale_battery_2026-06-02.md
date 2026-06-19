# RESEARCH ROUTING — Tier-4 training-speedup SMALL-SCALE EMPIRICAL BATTERY

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev
**Date:** 2026-06-02
**Trigger:** User strategic directive — our substrate's UNIQUELY ENABLING training-speedup primitives (PP-45/PP-46/PP-48/PP-49/PP-50/PP-12/PP-33/Q-B1) go well beyond generic Hebbian one-shot claims. Test these aggressively at small scale; scale up what works.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names full form, sweep grids, queue specifics, timeout) resolved by strategy + exp_dev. Per-PROT compliance. No empirical verification in drill bodies (drill outputs inform; tests in this routing are empirical).

---

## 0. STRATEGIC FRAMING

Substrate's training-speedup story is NOT "one-shot Hebbian is faster than gradient descent" (generic). It is:

**"Cert-grade training with one-shot writes + exact rollback + algebraic safety + counterfactual diagnostics + real-time drift detection + hierarchical composition — all in one unified algebraic API."**

This combination is uniquely ours. No other Hebbian / VSA system has the audit primitive stack confirmed across PP-45 / PP-46 / PP-48 / PP-49 / PP-50 + PP-12 / PP-33 / Q-B1.

**Test strategy:** 3 clusters (A / B / C) of progressively larger empirical tests. Fire cluster A immediately on CPU (~$0, hours). Stage cluster B / C based on what A reveals.

---

## 1. CLUSTER A — Substrate-only training-speedup primitives (CPU, ~$0, fires immediately)

**Goal:** validate the UNIQUELY OURS primitives at training scale before substrate-LLM coupling tests.

### A1 — Hebbian-vs-gradient-descent identity at small scale

**Capability question:** does one-shot Hebbian write achieve the same encoding fidelity as gradient descent (cross-entropy + Adam) for a simple (key, value) memorization task, at orders-of-magnitude lower compute?

**Algebraic basis:** substrate's free-Poisson identity + 9-primitive matrix-trace surface + confirmed L=3 composition predict that Hebbian write produces an optimal-in-the-MSE-sense encoding when patterns are bipolar and key-orthogonal. Gradient descent on a quadratic loss converges to the same fixed point.

**Test:** at N=1024, store M=100 (key, value) pairs via:
- (a) Standard gradient descent (linear regression on (k, v) batches; cross-entropy + Adam; train to convergence)
- (b) Substrate Hebbian one-shot writes
Compare: final retrieval accuracy on stored keys; retrieval accuracy on near-key probes (noise tolerance); wall time; FLOPs.

**Pre-registered HARD-PASS:** Hebbian matches gradient descent retrieval accuracy within ±2pp AND ≥100× speedup wall-time AND ≥1000× speedup FLOPs across 5 seeds.

**HARD-FAIL:** Hebbian accuracy < 90% of gradient descent baseline OR speedup < 10× (would mean substrate has no operational advantage over standard training).

**MIDDLE BAND:** match accuracy within ±5pp OR speedup 10-100× — substrate is useful but not decisive.

**Cost:** ~30 min CPU at N=1024, 5 seeds. $0 cloud.

### A2 — Deletion cert at training scale (exact rollback)

**Capability question:** can substrate exactly remove K randomly-selected training examples from M=1000 via PP-46 deletion cert, with verifiable cert chain replay AND retained examples preserving full accuracy?

**Algebraic basis:** PP-46 confirmed Z=156-223 at N=32768; rank-1 subtraction is algebraically exact. Cert chain replay should be reproducible by independent verifier.

**Test:** store M=1000 training examples; delete K∈{10, 50, 100, 500} via cert; verify (a) deleted examples no longer retrievable (cosine < 3σ noise floor); (b) retained examples retain ≥95% accuracy; (c) cert chain reproducible.

**Pre-registered HARD-PASS:** deletion cert produces clean exact removal at all K∈{10, 50, 100, 500} across 5 seeds; retained-accuracy ≥0.95; cert chain reproducible.

**HARD-FAIL:** any K-value shows residual cosine > 5σ noise floor OR retained-accuracy < 0.80.

**Substrate-novel claim:** no other training framework can exactly remove training events with verifiable cert. This is the substrate's #1 training-speedup moat (failed experiments recoverable in milliseconds).

**Cost:** ~30 min CPU at N=4096, 5 seeds. $0 cloud.

### A3 — Counterfactual training diagnostic via PP-49

**Capability question:** can PP-49 counterfactual abduction answer "what would the substrate have encoded if training example X had been omitted?" without retraining, at ≥90% fidelity to the ground-truth omit-and-retrain baseline?

**Algebraic basis:** PP-49 confirmed at N=4096 v334 with l3_fid=1.0. Counterfactual primitive operates on substrate state via CNDC primitive (per COMBO-3 unified API algebraic theorem).

**Test:** store M=100 training examples + 1 CORRUPTED training example; use PP-49 counterfactual to predict "what would substrate state look like if corrupted example had been omitted?"; compare to ground-truth omit-and-retrain baseline.

**Pre-registered HARD-PASS:** PP-49 counterfactual matches omit-and-retrain baseline within ±5pp on retrieval accuracy AND on κ_3 fingerprint within 1% AND cosine of substrate state ≥0.95 across 5 seeds.

**HARD-FAIL:** counterfactual deviation > 15pp from baseline OR cosine < 0.80 (would invalidate the "counterfactual training diagnostics without retraining" claim — a substrate-novel product moat).

**Cost:** ~1 hr CPU at N=4096, 5 seeds. $0 cloud.

### A4 — Active-repulsion training via signed-AM at p=4

**Capability question:** does signed-AM training (W = W_A − W_B; positive examples + active-repulsion negative examples per PP-48) match standard cross-entropy with positive+negative examples on a simple classification task, at orders-of-magnitude lower compute?

**Algebraic basis:** COMBO-2 v334 confirmed l3_fid=1.0 + b_rep=1.0 + parity=0.0. Signed-AM at p=4 is parity-clean (no spurious −ξ_B attractors). Active repulsion is operationally distinct from non-attraction — substrate-novel primitive.

**Test:** classification task with N_pos=50 positive + N_neg=50 negative examples; train via:
- (a) Standard cross-entropy with positive+negative examples
- (b) Signed-AM Hebbian writes (W_A on positives, W_B on negatives)
Compare: classification accuracy on held-out test set; wall time; FLOPs.

**Pre-registered HARD-PASS:** signed-AM matches cross-entropy accuracy within ±2pp AND ≥100× speedup wall-time AND active repulsion confirmed (cosine of negative examples post-training is significantly negative, not just zero).

**HARD-FAIL:** signed-AM accuracy < 90% of cross-entropy baseline OR no measurable active repulsion (negative cosine within 1σ of zero).

**Cost:** ~1 hr CPU at N=4096, 5 seeds. $0 cloud.

### Cluster A scheduling

**Fire A1 + A2 + A3 + A4 in parallel as next CPU queue refill. Total wall: ~3-4 hr CPU at $0.** Pre-PROT-018 anchor names: `hebbian_vs_gd_identity_v1`, `deletion_cert_training_scale_v1`, `pp49_counterfactual_training_diag_v1`, `signed_am_training_repulsion_v1`. All N default 4096 (no _nN suffix needed).

**Gating logic:** ALL FOUR HARD-PASS → cluster B authorized. Any HARD-FAIL → diagnose substrate-novel-training-primitive that broke; reconsider Tier-4 architectural plans.

---

## 2. CLUSTER B — Substrate-augmented small LLM (Remote GPU, $5-30, 1-3 days each)

**Goal:** validate that the cluster-A confirmed primitives integrate with an actual (small) LLM. Tier-4-lite scope.

### B1 — Hebbian-augmented mini-transformer attention layer

**Capability question:** can one attention layer in a small transformer (Pythia-160M / GPT-Neo-125M) be replaced with substrate query without destabilizing generation, AND does the substrate-augmented variant achieve training-cost speedup on knowledge addition?

**Test:** take pre-trained Pythia-160M or GPT-Neo-125M; replace ONE attention layer (mid-stack) with substrate query (substrate holds K/V; query is the residual; output is weighted retrieval). Fine-tune on a small corpus (Wikitext-2 or similar) to validate generation doesn't destabilize. Then add 100 new facts via:
- (a) LoRA fine-tuning
- (b) Substrate Hebbian writes
Compare: fact-recall accuracy, wall time, generation perplexity on held-out corpus.

**Pre-registered HARD-PASS:** substrate-augmented variant matches baseline perplexity within ±5% on held-out corpus AND substrate fact-addition achieves ≥95% recall accuracy AND ≥1000× wall-time speedup vs LoRA fine-tuning.

**HARD-FAIL:** substrate-augmented variant perplexity > 1.10 × baseline (substrate destabilizes generation) OR substrate fact-addition < 70% LoRA accuracy OR speedup < 10×.

**Cost:** 1-3 days engineering + $5-20 cloud (Lambda T4 or RTX 4090).

### B2 — Hebbian distillation MVP on Pythia-410M

**Capability question:** can substrate-via-knowledge-graph-distillation capture pre-trained Pythia-410M's factual knowledge with ≥90% fidelity at $5-30 cost vs $1000+ for fine-tuning equivalent knowledge?

**Test:** elicit 10,000 (subject, predicate, object) triples from Pythia-410M via fact-elicitation prompts; encode each triple via substrate VSA binding; verify substrate-augmented Pythia-410M (substrate state loaded) matches base Pythia-410M on TriviaQA factual subset within ±2pp accuracy.

**Pre-registered HARD-PASS:** distilled substrate matches base LLM accuracy on factual benchmark within ±2pp AND distillation cost ≤ $30 AND audit primitives (PP-46 deletion cert + PP-50 κ_3 fingerprint) operate correctly on distilled state.

**HARD-FAIL:** accuracy gap > 10pp OR distillation cost > $100 OR audit primitives don't compose with distilled state.

**Cost:** 2-3 days engineering + $5-30 cloud.

### B3 — Substrate-augmented in-context learning small-scale

**Capability question:** does substrate-augmented mini-transformer achieve same ICL accuracy on a few-shot task as baseline mini-transformer with in-context examples, while NOT requiring the ICL examples in context (saving context-window space) AND with ≥100× speedup per ICL "step"?

**Algebraic basis:** mesa-optimization lit (von Oswald 2022 / Akyürek 2022 / Garg 2022 / Dai 2023) shows transformers implement implicit gradient descent in attention during ICL. If substrate's Hebbian write is algebraically equivalent to ONE k=1 step of that implicit gradient descent, substrate-ICL should match baseline-ICL at ~10⁷× lower compute.

**Test:** synthetic ICL task (linear regression in-context, per Garg 2022); 2-layer transformer; compare:
- Baseline: standard ICL with K=10 examples in context
- Substrate: K=10 examples written to substrate Hebbian; substrate-augmented attention reads from substrate instead of context
Measure: test accuracy on novel queries; wall time per "learning step"; FLOPs per "learning step".

**Pre-registered HARD-PASS:** substrate-ICL matches baseline-ICL accuracy within ±3pp AND substrate-ICL "step" is ≥1000× faster (compute + wall-time) AND substrate-ICL examples can be queried via PP-49 counterfactual abduction ("what if example X weren't shown?").

**HARD-FAIL:** substrate-ICL accuracy < 80% of baseline-ICL OR speedup < 100×.

**Cost:** 1 day engineering + ~$0 cloud (runs on laptop GPU).

### Cluster B scheduling

**Fire B1 + B2 + B3 sequentially after cluster A all-PASS.** B1 first (validates substrate-augmented architecture works at all); B2 next (validates distillation pathway — practical productization); B3 third (validates theoretical ICL speedup ceiling claim empirically).

Total wall: ~4-6 days engineering + ~$10-50 cloud across the three.

---

## 3. CLUSTER C — Tier-4-lite full at production-scale LLM (Remote GPU + small cloud, $50-300, 2-4 weeks)

**Goal:** if cluster A + B all PASS, validate Tier-4 at production-grade LLM (Llama-3-8B-Instruct via vLLM).

### C1 — Llama-3-8B substrate-augmented attention layer with full audit primitives

**Capability question:** does Llama-3-8B with ONE attention layer substituted for substrate query + full audit primitives (PP-46 cert + PP-48 NKT + PP-49 HRC + PP-50 κ_3 drift) match baseline Llama-3-8B on standard benchmarks (MMLU, Wikitext perplexity) within ±5%?

**Pre-registered HARD-PASS:** substrate-augmented Llama-3-8B matches baseline MMLU within ±3pp AND baseline Wikitext perplexity within ±5% AND all 4 audit primitives operate correctly.

**Cost:** 1-2 weeks engineering + $50-100 cloud.

### C2 — Distillation + one-shot fact addition demo at production scale

**Capability question:** does substrate-augmented Llama-3-8B with distilled state from Cluster-B2 + 10,000 one-shot Hebbian-written facts (added during inference) achieve fact recall ≥95% AND maintain baseline MMLU within ±3pp?

**Pre-registered HARD-PASS:** ≥95% fact recall on Hebbian-added 10K facts AND MMLU within ±3pp AND total cost ≤ $200 AND wall time for fact addition ≤ 1 minute (vs ≥1 hour for LoRA equivalent).

**Cost:** 1-2 weeks engineering + $50-200 cloud (depends on distillation corpus size).

### Cluster C scheduling

Fire C1 first; C2 after C1 PASS. **REQUIRES USER PER-CASE AUTH per `feedback_short_cloud_runs_preferred`** (cloud spend ≥ $50).

---

## 4. SCHEDULING + AUTHORIZATION

**IMMEDIATE — no user auth needed (substrate-only, $0):**
- Cluster A (A1 + A2 + A3 + A4) — fire NEXT CPU queue refill, parallel

**NEAR-TERM — no user auth needed for B (under $30 each):**
- Cluster B (B1 + B2 + B3) — fire sequentially after Cluster A all-PASS

**HIGH-VALUE — REQUIRES USER PER-CASE AUTH:**
- Cluster C (C1 + C2) — fire after Cluster B all-PASS; C1 first ($50-100), then C2 ($50-200)

**Total program cost ceiling:** ~$110-350 cloud + ~6-8 weeks engineering for full Cluster A + B + C. **If A or B HARD-FAILs, program closes at that gate; cost stops.** This is significantly less than the Phase 0.5 Tier-7 MVP authorization ($50-100) IF cluster A succeeds and we proceed to B.

---

## 5. CROSS-THREAD SYNTHESIS

**This battery complements rather than replaces the 4 in-flight research drills** (Tier-4 economics, LLM compute decomposition, ICL vs Hebbian, distillation pathway). Drills will inform Cluster B/C cell design when they land (~20-25 min from dispatch). Cluster A fires NOW because:
- All 4 cluster-A tests use substrate-only primitives confirmed at v324+ (no LLM-coupling risk)
- All 4 use $0 cloud (no auth gate)
- All 4 take hours not days (cheap iteration)
- The substrate-novel claims (deletion cert + counterfactual + signed-AM + Hebbian-vs-GD) need to be empirically locked at training scale BEFORE we commit to substrate-LLM coupling tests

**Integration with LLM-integration program:** Cluster B1 + B3 are essentially Tier-4-lite tests at small LLM scale. If they PASS, they directly inform whether to accelerate Tier-4 in the LLM-integration program (Phase 4 → Phase 2-3 timing).

**Integration with Phase 0.5 Tier-7 MVP:** Phase 0.5 tests substrate as PASSIVE read-side companion (LLM internal state monitoring). Cluster B/C tests substrate as ACTIVE training participant (writes happen during inference). The two paths are orthogonal — both could PASS or one could PASS and the other FAIL.

---

## 6. DISCIPLINE DECLARATIONS

- **Capability questions only; HP/MIDDLE/FAIL bands pre-registered.** Strategy + exp_dev resolve cell design.
- **Pre-PROT-018 anchor names** default N=4096 for cluster A (no _nN suffix needed); cluster B/C anchors carry _nN if LLM dimension differs.
- **ASCII-only print; per-experiment `--timeout`.**
- **Single-instance per cluster-B test** (B1 / B2 / B3 each one bootstrap); cluster A all 4 anchors share one CPU queue refill.
- **No padding.** Each test validates ONE substrate-novel training-speedup primitive at one scale. No exploratory padding.
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** task prompts MUST NOT pre-frame any cluster-A test as HARD-PASS. Pre-register HARD-FAIL conditions explicitly; verdict_handler does honest re-read.
- **Per `feedback_lit_scan_calibration_penalty`:** these tests USE confirmed primitives at training scale; no novel-synthesis cap applied. Honest P estimates per cluster: A = 0.70+ (confirmed primitives at known-good regime), B = 0.45-0.55 (substrate-LLM coupling untested), C = 0.30-0.40 (production-LLM coupling at scale).
- **Per `feedback_obey_user_pause_explicitly`:** Cluster A authorized (substrate-only, $0); Cluster B authorized (under per-case threshold); Cluster C requires user per-case auth.
- **Per `feedback_pipeline_pacing`:** Cluster A goes on NEXT CPU queue refill — research authorizes immediate dispatch.

---

## 7. CAP_MAP UPDATE REQUESTS

On Cluster A all-PASS:
- **NEW sub-property PP-46a** "exact training rollback via deletion cert at K=10-500" — extends PP-46 to training-event scope
- **NEW sub-property PP-49a** "counterfactual training diagnostic without retraining" — extends PP-49 to training-time use case
- **NEW sub-property PP-48a** "active-repulsion training via signed-AM p=4" — extends PP-48 to training-time use case
- **NEW top-level row candidate PP-53** "one-shot Hebbian training equivalence to gradient descent at memorization tasks" (pending cluster-A A1 PASS)

On Cluster B all-PASS:
- **NEW top-level row candidate PP-54** "substrate-augmented LLM training acceleration at small-LLM scale" (pending cluster B all-PASS)
- **PP-46 + PP-48 + PP-49 LIFTs** to "production-LLM coupling confirmed at small-LLM scale"

On Cluster C all-PASS:
- **PP-54 LIFT to production-LLM scale**
- **NEW killer feature #11 "auditable one-shot LLM customization at $0.001/fact"** (vs $100s+ for fine-tuning)

---

## 8. STRATEGIC IMPACT IF ALL THREE CLUSTERS PASS

Substrate's product narrative shifts from "auditable AI memory" to **"auditable one-shot LLM customization infrastructure."** The three-cluster battery empirically validates that:
- Substrate can substitute for gradient descent at training scale (Cluster A)
- Substrate can integrate with actual LLMs without destabilization (Cluster B)
- Substrate at production LLM scale delivers 1000-10000× cost speedup on knowledge addition with cert-grade audit (Cluster C)

This is category-defining. Combined with the Phase 0.5 Tier-7 MVP (audit primitive on live LLM state), substrate becomes **"the universal substrate for auditable LLM customization + audit"** — a positioning no other system has approached.

Honest joint probability of all three clusters HARD-PASS: ~0.10-0.20 (low joint, but conditional probabilities per cluster compound). Even at 10-20% joint, strategic value is massive AND cost is bounded at ~$110-350 + 6-8 weeks engineering — well-spent relative to the substrate's 24-36 month market window.

---

**END.** Orchestrator: queue Cluster A (4 anchors) on next CPU queue refill immediately; gate Cluster B on Cluster A all-PASS; gate Cluster C on Cluster B all-PASS + user per-case auth. Strategy: fold cluster outcomes into cap_map per Section 7. exp_dev: design Cluster A cells from capability questions + HARD bands above; all 4 share CPU queue refill, anchor names per Section 1 suggestions.
