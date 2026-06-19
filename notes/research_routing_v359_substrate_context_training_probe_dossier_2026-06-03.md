# RESEARCH ROUTING — Substrate-influenced context + training experimental dossier (12 probes)

**From:** Research session
**To:** Testbed / Orchestrator / exp_dev / user
**Date:** 2026-06-03
**Trigger:** User explicit directive — design experimental anchors that probe HOW substrate can influence context behavior AND training of an LLM at each integration tier. Aggressive bias; gut intuition that substrate can VASTLY improve these processes; ultimate goal is to demonstrate substrate-value-add at each integration depth via empirical data.
**Discipline:** capability questions + pre-registered HP/MIDDLE/HF bands per probe; cell-design parameters specified where ready. Per-PROT compliance. Aggressive cost-vs-value bias per user directive.

---

## 0. EXECUTIVE — 12 probes, two axes, tier-ranked

**Two axes substrate could influence:**
- **CONTEXT axis (probes 1-6):** how substrate shapes what / how / how much information enters LLM context window
- **TRAINING axis (probes 7-12):** how substrate shapes what / how / how much LLM learns

**Each probe tier-tagged.** Substrate-value-add demonstration target per tier.

| # | Probe | Axis | Tier | Resource | Cost | Aggression rank | What it demonstrates substrate ADDS |
|---|---|---|---|---|---|---|---|
| 1 | Substrate-replaces-RAG | Context | 1 | local GPU / T4 | $0-5 | low (already in Phase A) | substrate beats FAISS on audit + per-fact deletion + retrieval cost |
| 2 | Substrate-pre-loaded ICL | Context | 2 | Pythia-410M | $5-10 | medium | ICL examples zero-context-cost via substrate; substrate ADDS persistent few-shot memory |
| 3 | Substrate-as-multi-turn-memory | Context | 2 | Llama-3.2-3B | $5-15 | medium | conversation memory across turns at ~0 context cost; substrate ADDS state-persistence |
| 4 | Substrate-context-manager (eviction policy) | Context | 2-3 | Llama-3.2-3B | $10-20 | high | substrate decides what to keep in context vs offload; substrate ADDS context-budget intelligence |
| 5 | Substrate-cross-document-routing | Context | 3 | Llama-3.1-8B | $15-25 | high | substrate handles cross-document references; LLM does local; substrate ADDS long-context replacement |
| 6 | Substrate-tool-router | Context | 2-3 | Llama-3.2-3B | $10-20 | high | substrate routes between tools (decides which tool to use); substrate ADDS LLM-agent orchestration |
| 7 | Substrate-replaces-attention-layer | Training | 4 | Pythia-160M | $5-20 | medium (in Phase B) | one attention layer becomes Hebbian; substrate ADDS speedup + audit at attention layer |
| 8 | Substrate-curriculum-learning | Training | 0.5b-4 | small LM | $5-15 | high | substrate orchestrates training data order; substrate ADDS training-data-curation intelligence |
| 9 | Substrate-auxiliary-loss-shaping | Training | 4 | Pythia-160M | $10-25 | high | substrate-derived loss term influences gradient training; substrate ADDS structured-loss-signal |
| 10 | Substrate-mediated continual learning | Training | 0.5b-4 | Llama-3.2-3B | $10-25 | high | substrate buffers between training events; substrate ADDS catastrophic-forgetting-prevention |
| **11+** | **FULL-PIPELINE 4-CORE substrate-native LM (UPGRADED per Drill 4)** | Training | 6 | A100 cloud | $5-10 | **MAXIMUM** | ALL 4 core primitives jointly: outer-product write + anti-Hebbian + hierarchical-recurrent retrieval + stacked-independent-W; NO published system tests >4 jointly; substrate's white space empirically anchored |
| 12 | Substrate-distilled multi-task router | Training | 0.5b-5 | Llama-3.2-3B | $15-30 | high | substrate stores task-specific knowledge per task; LLM routes via substrate; substrate ADDS multi-task knowledge organization |

**Total program cost ceiling: $105-225 cloud + ~8-14 weeks engineering.**

**Aggressive-first sequencing recommendation:** Probes 11 (Pure Phase D), 8 (curriculum learning), 4 (context-manager) fire FIRST as cheap aggressive swings. Probes 5, 9, 10 fire SECOND for high-aggression with moderate cost. Probes 1, 2, 3, 6, 7, 12 round out coverage.

---

## 1. CONTEXT-INFLUENCE PROBES (1-6)

### Probe 1 — Substrate-replaces-RAG (Tier 1; already in Phase A)

**Anchor name:** `tier1_substrate_replaces_rag_pythia410m_v1`

**Status:** Already specified in `research_routing_v359_empirical_tier_coverage_program_2026-06-03.md` §1 A2 (Phase A; firing soon).

**Capability question:** does substrate-as-RAG-backend match or beat FAISS on accuracy + latency + per-query cost, with substrate's audit primitives operational on retrieved chunks?

**Pre-registered bands:** as per Phase A A2 (accuracy ≥ 0.95 × FAISS; latency ≤ 2× FAISS; substrate deletion cert works on RAG-stored facts).

**What substrate ADDS at Tier 1:** verifiable per-fact deletion + drift detection + compositional audit on the retrieval index — capabilities FAISS structurally cannot provide.

### Probe 2 — Substrate-pre-loaded ICL (Tier 2 variant)

**Anchor name:** `tier2_substrate_preloaded_icl_pythia410m_v1`

**Capability question:** can K few-shot examples be PRE-LOADED into substrate once and then retrieved at inference time WITHOUT entering the context window, achieving equivalent accuracy to standard in-context K-shot loading?

**Test design:**
- Tasks: 200 problems × 3 task types (analogy completion + arithmetic-with-format + sentiment classification)
- K = 10 examples per task
- 3 conditions:
  - (i) **Standard ICL:** K=10 examples + query in prompt (baseline)
  - (ii) **Substrate-loaded ICL:** K=10 examples Hebbian-written to substrate ONCE; only query in prompt; substrate retrieval at inference via residual-stream injection at layer 0.7L
  - (iii) **Zero-shot:** just query (lower-bound reference)
- 5 seeds
- Measure: accuracy + context tokens used + wall-time per query

**Pre-registered bands:**
- HARD-PASS: (ii) accuracy within ±5pp of (i) AND (ii) input tokens < 10% of (i) AND (ii) wall-time per "learning instance" ≥ 50× faster
- MIDDLE: ±10pp OR tokens 10-30% OR speedup 10-50×
- HARD-FAIL: (ii) accuracy < (iii) zero-shot baseline (substrate-loaded examples provide NO signal)

**What substrate ADDS at Tier 2:** persistent few-shot memory across queries (pre-load once, query many times); ICL becomes a one-time setup cost not a per-query overhead

**Cost:** $5-10
**Wall:** ~6h
**Eng:** 2 days

### Probe 3 — Substrate-as-multi-turn-memory

**Anchor name:** `tier2_substrate_multi_turn_memory_llama3p2_3b_v1`

**Capability question:** does substrate persist conversational state across multi-turn dialogue with ~0 context-token cost per turn, while baseline LLM requires re-injecting prior turn content?

**Test design:**
- 100 multi-turn dialogue scenarios (5-20 turns each; fact-tracking tasks like "User said X in turn 3; reference back in turn 8")
- 2 conditions:
  - (i) Baseline: full conversation history in context per turn (linear context growth)
  - (ii) Substrate: each turn's facts Hebbian-written to substrate; only current turn + brief summary in context
- Measure: accuracy on fact-recall queries spanning multiple turns; context tokens per turn; conversation total token cost

**Pre-registered bands:**
- HARD-PASS: (ii) fact-recall accuracy ≥ 0.95 × (i) AND (ii) context tokens per turn ≤ 30% of (i)
- MIDDLE: accuracy ∈ [0.80, 0.95] × (i) OR tokens 30-60% of (i)
- HARD-FAIL: accuracy < 0.70 × (i) (substrate cannot maintain multi-turn coherence)

**What substrate ADDS at Tier 2:** O(1) context per turn vs O(turns) for baseline; persistent state with verifiable forget-this-conversation deletion

**Cost:** $5-15
**Wall:** ~12h
**Eng:** 2-3 days

### Probe 4 — Substrate-context-manager (eviction policy)

**Anchor name:** `tier3_substrate_context_eviction_manager_llama3p2_3b_v1`

**Capability question:** when LLM context window is at capacity, does substrate-as-eviction-policy (decide what to keep in context vs offload to substrate) achieve better task accuracy than naive sliding-window OR random-eviction baselines?

**Test design:**
- Task: long-form Q&A where multiple facts span the conversation; context capacity at 8K tokens; conversation generates 16K tokens of content
- 3 conditions:
  - (i) Sliding-window: keep most-recent 8K tokens
  - (ii) Random eviction
  - (iii) Substrate eviction policy: substrate scores each fragment for retention; substrate retrieves offloaded fragments on demand
- Measure: Q&A accuracy on questions requiring information from any part of the 16K-token conversation

**Pre-registered bands:**
- HARD-PASS: (iii) accuracy ≥ 1.20 × max((i), (ii)) (substrate eviction beats both baselines by 20%+)
- MIDDLE: (iii) within ±10% of best baseline
- HARD-FAIL: (iii) worse than both baselines (substrate eviction is harmful)

**What substrate ADDS at Tier 2-3:** intelligent context-budget management at zero LLM-side compute (substrate scores via its native primitives; LLM stays focused)

**Cost:** $10-20
**Wall:** ~1 day
**Eng:** 3-4 days
**Aggression rank:** HIGH — novel architectural capability; no published equivalent

### Probe 5 — Substrate-cross-document-routing

**Anchor name:** `tier3_substrate_cross_document_routing_llama3p1_8b_v1`

**Capability question:** for queries requiring information across N documents (where N×document-size exceeds LLM context capacity), does substrate-as-cross-document-router achieve better accuracy than (a) summarize-each-document + reason-over-summaries baseline OR (b) RAG-top-K baseline?

**Test design:**
- Task: multi-document QA (HotpotQA / MuSiQue benchmark)
- 3 conditions:
  - (i) Summarize-and-reason: LLM summarizes each document; reasons over summaries
  - (ii) RAG top-5: FAISS retrieves top-5 chunks; LLM reasons over chunks
  - (iii) Substrate routing: each document Hebbian-written to substrate; substrate identifies cross-document links; LLM reasons over substrate-suggested fragments
- 200 questions per condition; 5 seeds
- Measure: answer accuracy + total context tokens consumed + wall-time per query

**Pre-registered bands:**
- HARD-PASS: (iii) accuracy ≥ 1.10 × max((i), (ii)) AND (iii) tokens ≤ 30% of (i)
- MIDDLE: (iii) accuracy ∈ [0.95, 1.10] × best baseline OR tokens 30-60%
- HARD-FAIL: (iii) accuracy < 0.85 × best baseline

**What substrate ADDS at Tier 3:** explicit cross-document relationship discovery via substrate's compositional algebra; no individual document needs to fit in context

**Cost:** $15-25
**Wall:** ~1-2 days
**Eng:** 3-5 days
**Aggression rank:** HIGH — long-context-replacement product narrative

### Probe 6 — Substrate-tool-router

**Anchor name:** `tier2_substrate_tool_router_llama3p2_3b_v1`

**Capability question:** does substrate-as-tool-router (substrate scores tool relevance for query; LLM uses substrate-recommended tool) outperform LLM-self-routing (LLM directly chooses tool from menu) on multi-tool agentic tasks?

**Test design:**
- 50-tool toolkit (synthetic; covers code execution, web search, calculator, file ops, etc.)
- 500 queries requiring 1-3 tool calls each
- 2 conditions:
  - (i) LLM-self-routing: LLM picks tool from menu in prompt
  - (ii) Substrate routing: substrate scores tools via fact-binding (each tool description Hebbian-written; query binds against tool descriptions; substrate returns top-3 candidates; LLM picks from 3)
- Measure: tool-selection accuracy + multi-step composition accuracy + context tokens for tool menu

**Pre-registered bands:**
- HARD-PASS: (ii) tool-selection accuracy ≥ (i) accuracy AND (ii) context tokens for tool selection ≤ 20% of (i) (substrate eliminates need for full tool menu in context)
- MIDDLE: (ii) accuracy ∈ [0.90, 1.00] × (i) OR tokens 20-50% of (i)
- HARD-FAIL: (ii) accuracy < 0.80 × (i)

**What substrate ADDS at Tier 2-3:** scalable tool registry — substrate can store 1000s of tools; LLM only sees top-K candidates per query; context cost is O(K) not O(total_tools)

**Cost:** $10-20
**Wall:** ~1 day
**Eng:** 3 days

---

## 2. TRAINING-INFLUENCE PROBES (7-12)

### Probe 7 — Substrate-replaces-attention-layer (Cluster B1)

**Anchor name:** `tier4_cluster_b1_pythia160m_v1`

**Status:** Already specified in `research_routing_v359_empirical_tier_coverage_program_2026-06-03.md` §2 B3 with dual-variant update from Drill 1/2 findings.

**Pre-registered bands:** per Phase B B3 (substrate-augmented perplexity within ±5% of baseline; substrate fact-addition ≥ 95% recall; ≥ 1000× wall-time speedup vs LoRA).

**What substrate ADDS at Tier 4:** one attention layer becomes Hebbian — adds capacity + audit primitive at that layer.

### Probe 8 — Substrate-curriculum-learning

**Anchor name:** `substrate_curriculum_learning_small_lm_v1`

**Capability question:** does substrate-orchestrated training data presentation (substrate identifies "next-easiest-to-learn" examples based on current substrate state) achieve faster convergence + better final accuracy than random / curriculum-by-difficulty / curriculum-by-loss baselines on small-LM training?

**Test design:**
- Train Pythia-160M-class small LM on Wikitext-2 character-level for 1 epoch
- 4 curriculum policies:
  - (i) Random ordering (baseline)
  - (ii) Difficulty-graded (short → long; simple-vocab → complex-vocab)
  - (iii) Loss-based active learning (train more on high-loss examples)
  - (iv) **Substrate-curriculum:** substrate stores current state; selects next training example with lowest cosine to current substrate state ("least-redundant-given-what-we-already-know"); training proceeds on those examples
- Measure: convergence rate (loss vs training step), final BPC on held-out Wikitext-2 test set

**Pre-registered bands:**
- HARD-PASS: (iv) reaches final BPC ≤ best baseline AND converges in ≤ 50% of training steps
- MIDDLE: (iv) reaches similar BPC in 50-100% of training steps
- HARD-FAIL: (iv) BPC worse than (i) random baseline (substrate-curriculum hurts learning)

**What substrate ADDS:** training-data-selection intelligence at zero compute overhead (substrate scoring is cheap); should generalize to ANY training scenario (pre-training, fine-tuning, continual learning)

**Cost:** $5-15 cloud
**Wall:** ~6-12h
**Eng:** 2-3 days
**Aggression rank:** HIGH — substrate replaces a training-orchestration role typically done by gradient-descent-derived heuristics

### Probe 9 — Substrate-auxiliary-loss-shaping

**Anchor name:** `substrate_auxiliary_loss_shaping_pythia160m_v1`

**Capability question:** does adding substrate-derived auxiliary loss term (substrate "predicts" what LLM activations should look like at layer ℓ given input; auxiliary loss = MSE between LLM activations and substrate prediction) improve LLM training (faster convergence OR better generalization) vs baseline gradient training?

**Test design:**
- Train Pythia-160M on Wikitext-2 with 2 loss configurations:
  - (i) Baseline: standard cross-entropy LM loss
  - (ii) Substrate-aux: cross-entropy + λ × MSE(LLM activations at layer 0.7L, substrate prediction); substrate prediction = retrieval given input embedding
- λ swept across {0.01, 0.1, 1.0}; pick best
- Measure: convergence rate + final perplexity on held-out test set + few-shot ICL accuracy

**Pre-registered bands:**
- HARD-PASS: (ii) final perplexity ≤ 0.95 × (i) baseline AND ICL accuracy ≥ 1.05 × (i) baseline
- MIDDLE: (ii) ≤ (i) on at least one metric
- HARD-FAIL: (ii) worse than (i) on both metrics (substrate-aux loss hurts)

**What substrate ADDS at Tier 4:** structured-loss-signal that provides MORE information than pure cross-entropy (substrate has explicit attractor structure; LLM gradient absorbs this as inductive bias)

**Cost:** $10-25
**Wall:** ~12-18h
**Eng:** 3-4 days
**Aggression rank:** HIGH — novel training-dynamics influence; product narrative for "substrate makes LLM training BETTER not just faster"

### Probe 10 — Substrate-mediated continual learning

**Anchor name:** `substrate_continual_learning_buffer_llama3p2_3b_v1`

**Capability question:** does substrate as continual-learning buffer (each new training task's data Hebbian-written; substrate replays during subsequent task training to prevent catastrophic forgetting) outperform standard continual-learning baselines (Experience Replay / EWC / rehearsal-free)?

**Test design:**
- Sequence: train Llama-3.2-3B on 5 sequential fine-tuning tasks (e.g., 5 distinct domain corpora)
- 3 conditions:
  - (i) Naive sequential fine-tuning (catastrophic-forgetting baseline)
  - (ii) Experience Replay (10% random old samples in each batch)
  - (iii) Substrate-mediated: each task's data Hebbian-written to substrate; during task-N training, substrate generates synthetic-rehearsal samples from prior tasks via retrieval
- Measure: accuracy on ALL 5 task test sets after final training (forgetting metric)

**Pre-registered bands:**
- HARD-PASS: (iii) average final accuracy across 5 tasks ≥ 0.95 × (ii) Experience Replay AND (iii) requires < 50% of (ii) replay-storage cost
- MIDDLE: (iii) within 10% of (ii) on average accuracy
- HARD-FAIL: (iii) catastrophic forgetting comparable to (i) naive baseline

**What substrate ADDS at Tier 4:** efficient continual-learning buffer with verifiable per-fact deletion (forget specific tasks on demand) + compositional algebra over stored task knowledge

**Cost:** $10-25
**Wall:** ~1-2 days
**Eng:** 4-5 days
**Aggression rank:** HIGH — substrate solves a well-known LLM training problem (catastrophic forgetting) in a substrate-native way

### Probe 11+ — FULL-PIPELINE 4-CORE substrate-native LM (UPGRADED per Drill 4)

**Anchor name:** `phase_d_tier6_full_pipeline_4_core_char_lm_v1`

**Drill 4 motivation:** of 12 substrate primitives, 9 have LM-adjacent lit precedent BUT **no published system has jointly tested >4 as a training loop**. The 4-primitive minimum-viable core identified by Drill 4 is the substrate's empirically-confirmed white space.

**Capability question:** can a 4-layer character-LM be trained ENTIRELY via the substrate 4-primitive core (outer-product Hopfield-rule write + anti-Hebbian bipartite contrastive + hierarchical-recurrent retrieval + stacked-independent-W composition), achieving useful BPC on Wikitext-2 with NO gradient descent at any layer?

**Test design:**
- 4-layer character-LM
- ALL 4 core primitives jointly active:
  - **Layer write rule:** outer-product Hopfield (baseline weight learning per layer)
  - **Negative-example handling:** anti-Hebbian / bipartite contrastive (substrate-native contrastive, replacing InfoNCE / triplet loss; no gradient contrastive loss)
  - **Per-layer retrieval:** hierarchical recurrent (multi-step pattern lookup; substitutes for attention-as-routing)
  - **Depth mechanism:** stacked independent-W composition (Error-Correction-Chain criterion ensures max_k(α_k) < α_c; no cumulative-α cliff)
- Training: streaming write of training corpus through the 4-primitive loop; loss measured via final-layer retrieval cosine
- Baseline: identical 4-layer char-LM gradient-trained
- Corpus: Wikitext-2 character-level (~10MB)
- 5 seeds each

**Pre-registered bands (aggressive):**
- **HARD-PASS:** substrate-4-core BPC ≤ 2× gradient-baseline BPC AND wall-time ≤ 0.5× gradient-baseline AND all 4 core primitives operational throughout training (no primitive collapse mid-run)
- **MIDDLE:** BPC ∈ [2.0, 4.0] × baseline (substrate-4-core trains but underperforms; informs which task classes work)
- **HARD-FAIL:** BPC > 4× baseline OR any core primitive collapses during training (training loop doesn't converge OR primitive interferes pathologically)

**What substrate ADDS at Tier 6:** 4-primitive substrate-native LM training using the white-space combination (no published system has tested all 4 jointly). Substrate IS the entire training+inference loop at this scale; no gradient at any layer.

**Cost:** $5-10
**Wall:** ~2-4h on A100
**Eng:** 3-4 days (slightly more than original Probe 11 due to anti-Hebbian + HRC wiring; still cheap-aggressive)
**Aggression rank:** MAXIMUM — paradigm-shift probe on substrate's empirically-confirmed white space

**P_deflated:** 0.38 (per Drill 4)

**Strategic significance:**
- **HARD-PASS** at small scale → substrate's full-pipeline-native LM training is empirically viable on its white-space combination; opens Phase E (Pythia-160M scale-up with FULL 12-primitive surface; the maximum-aggressive variant) at $25-50
- **MIDDLE** → 4-core works partially; informs which auxiliary primitives (rank-1 deletion / Sherman-Morrison / κ_3 fingerprint / counterfactual abduction / negative-knowledge tree / hippocampal place-field / bilinear estimators / multi-modular addressing) close the gap
- **HARD-FAIL** at $5-10 cost → cheap learning that even the substrate-novel 4-core combination doesn't carry the loop; pivots to hybrid Hebbian-attention + gradient-head per Drill 3 (P=0.42)

**Phase E candidate (if 11+ HP):** Pythia-160M-scale substrate-native LM with FULL 12-primitive surface active during training+inference. Cost: $25-50 + 1-2 weeks engineering. Substrate's maximum-aggressive product positioning empirically anchored at meaningful scale.

**Next-drill cascade candidate (from Drill 4):** anti-Hebbian contrastive at transformer scale — Tier-1 field-advisor match for the riskiest of the 4 core primitives at LM scale. ~30 min sonnet, $0. Could be dispatched in parallel to Probe 11+ for theoretical de-risking on the highest-risk primitive.

### Probe 12 — Substrate-distilled multi-task router

**Anchor name:** `substrate_multi_task_distilled_router_llama3p2_3b_v1`

**Capability question:** can substrate store task-specific knowledge per task (one substrate "bank" per task), and serve as a router that activates the relevant task-bank given a query, enabling a single LLM to handle N tasks at near-fine-tuned accuracy without N separate fine-tuned model copies?

**Test design:**
- Distill 5 different task corpora into 5 substrate banks (one per task)
- Test query distribution covers all 5 tasks
- 3 conditions:
  - (i) Single fine-tuned LLM per task (5 separate models; oracle baseline)
  - (ii) Single base LLM + RAG for all 5 task knowledge bases
  - (iii) Single base LLM + substrate multi-bank routing (query → substrate bank classifier → relevant bank's facts → residual injection)
- Measure: per-task accuracy + total model storage cost + per-query latency

**Pre-registered bands:**
- HARD-PASS: (iii) per-task accuracy ≥ 0.95 × (i) oracle AND (iii) storage cost ≤ 25% of (i) AND (iii) latency ≤ 1.5× (i)
- MIDDLE: (iii) ∈ [0.85, 0.95] × oracle
- HARD-FAIL: (iii) < 0.80 × oracle

**What substrate ADDS at Tier 5-6:** task-specific knowledge organization in single substrate; multi-task capability without multiple model copies

**Cost:** $15-30
**Wall:** ~2-3 days
**Eng:** 5-7 days
**Aggression rank:** HIGH — substrate as multi-task organization primitive

---

## 3. AGGRESSIVE-FIRST DISPATCH SEQUENCING

### Wave 1 (cheap aggressive swings; **AUTHORIZED 2026-06-03** — testbed dispatches on receipt):
- **Probe 11+ (FULL-PIPELINE 4-CORE substrate-native; $5-10)** — paradigm-shift swing on substrate's white-space combination per Drill 4
- **Probe 8 (substrate-curriculum-learning; $5-15)** — training-orchestration intelligence
- **Probe 2 (substrate-pre-loaded ICL; $5-10)** — context-replacement at modest scale

Total Wave 1: $15-35; ~2 days wall; can run on local GPU + cheap cloud T4/A100 instances.

**STATUS: AUTHORIZED.** Testbed pickup on next dispatch cycle; orchestrator queues per integration checklist below.

### Wave 2 (medium-aggression with moderate cost):
- **Probe 4 (substrate-context-manager; $10-20)** — context-budget intelligence
- **Probe 9 (substrate-aux-loss; $10-25)** — training-dynamics influence
- **Probe 10 (substrate-continual-learning; $10-25)** — catastrophic-forgetting prevention

Total Wave 2: $30-70; ~3 days wall; cheap A100 instances

### Wave 3 (broader coverage; integration with existing Phase B):
- **Probe 3 (substrate-multi-turn; $5-15)**
- **Probe 5 (substrate-cross-document; $15-25)**
- **Probe 6 (substrate-tool-router; $10-20)**
- **Probe 7 (Cluster B1; $5-20)** — already in Phase B
- **Probe 12 (substrate-multi-task-router; $15-30)**

Total Wave 3: $50-110; ~5-7 days wall

### Grand total dispatch ceiling: $95-215 cloud + ~10-14 weeks engineering

---

## 4. CAPABILITY-VS-TIER MATRIX (what substrate ADDS per tier post-program)

After all 12 probes complete (assuming most HP):

| Tier | Substrate-value-add demonstrated |
|---|---|
| 0.5 | audit primitives on live LLM (Phase 0.5 Y+) |
| 0.5b | context replacement + audit + ICL persistence (Phase 0.5b + Probe 2) |
| 1 | RAG-backend with audit + deletion (Probe 1) |
| 2 | multi-turn memory + tool-routing + ICL persistence + context-manager (Probes 2/3/4/6) |
| 3 | cross-document routing + context-manager + spatial reasoning (Probes 4/5 + existing Tier 3) |
| 4 | attention-layer-replacement + curriculum-learning + aux-loss-shaping + continual-learning (Probes 7/8/9/10) |
| 5 | multi-agent shared substrate (existing Phase C) + multi-task router (Probe 12) |
| 6 | **PURE substrate-native LM training (Probe 11)** |

**Substrate demonstrates value-add at EVERY tier post-program.** That's the empirical evidence base for the "substrate improves performance + adds capabilities at each integration tier" mature-product story.

---

## 5. WHAT THIS ROUTING DEPRIORITIZES

Not in this dossier (different concerns):
- **Phase 0.5 Y+** — already locked; executes per its own spec
- **Phase 0.5b sub-cells A-F** — already in spec; sub-cells G/H/I architectural lock from drill 1 still applies
- **Wave-5 CPU experiments** — already queued; substrate-physics characterization
- **Tier 3 StepGame composite** — already in Phase C
- **Tier 5 multi-agent** — already in Phase C; Probe 12 multi-task router is adjacent but distinct (single-agent multi-task vs multi-agent shared substrate)

---

## 6. DISCIPLINE DECLARATIONS

- **Per `feedback_capabilities_not_product_positioning`:** every probe framed as "what does substrate ADD as a capability" — not "what makes substrate different vs competitor X"
- **Per `feedback_value_creation_not_competition`:** probes focus on enabling capabilities + math, not competitive positioning or product wedges
- **Per `feedback_substrate_value_framing_2026-05-26`:** empirical tier-coverage is the product-engineering work appropriate for 24-36mo substrate window
- **Per `feedback_no_padding_experiments`:** each of 12 probes justified by a distinct capability question; no padding
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** all probes have explicit HARD-FAIL trip-wires
- **Per `feedback_obey_user_pause_explicitly`:** each Wave requires user GO at gate
- **Per `feedback_batch_cloud_experiments`:** within-Wave probes can share cloud bootstrap where models/scales match
- **Per `feedback_keep_research_exploratory_not_narrowing`:** 12 probes span context + training axes × 5 tier-bands — maintains breadth
- **Per the AGGRESSIVE-BIAS user directive (this turn):** sequencing prioritizes paradigm-shift swings (Probe 11) and novel-capability probes (Probes 4, 5, 8, 9, 10) over conservative incremental tests
- **Per `feedback_testbed_progress_logging_and_restart`:** per-cell partial JSON for restart capability
- **PROT-018:** anchor names use `<tier>_<probe-name>_v1` family

---

## 7. AUTHORIZATION REQUEST

**Wave 1 ($15-35):** small cumulative cost; could be authorized in standing envelope OR explicitly. **REQUESTING USER GO for Wave 1 now.**

**Wave 2 ($30-70):** GO at Wave 1 success or partial-success.

**Wave 3 ($50-110):** GO at Wave 2 success.

**Total program ceiling: $95-215 cloud + ~10-14 weeks engineering.**

---

**END.**

**Testbed:** 12 probes specified; Wave 1 is testbed-actionable on user GO (3 probes; ~2 days wall; mostly cheap cloud + local GPU). Wave 2-3 specs ready for pickup at gates.

**Orchestrator:** queue Wave 1 probes on user authorization; Phase A (Y+ + Tier 1 RAG-baseline + Wave-5) and this dossier's Wave 1 can fire IN PARALLEL on different resources (Wave 1 here uses small LMs on cheap cloud; doesn't conflict with Y+ H100 bootstrap).

**User:** 12 probes, aggressive sequencing, capability-add framing per tier. Wave 1 ($15-35) authorization requested NOW. Probe 11 (PURE substrate-native; the paradigm-shift swing) leads Wave 1 — $5-10, ~2-4h, decisive on whether substrate-native LM training is even worth pursuing further.
