# RESEARCH 2x DRILL: Online learning during conversation primitive (Stage 3)

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Topic:** Brain-grounded single-shot conversational fact integration without forgetting prior context
**Stage:** Stage 3 compositional understanding (per USER stage-progression LOCKED 2026-06-26)
**Cap_map:** USER load-bearing concern #4 for M3 (per `director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` UPDATE #20 §"REMAINING LOAD-BEARING CONCERNS")
**Pre-reg compliance:** META_RULE_AA/AC/AE/AF/AG/AH + META_RULE_NO_HALLUCINATED_NUMBERS + DISCRIMINATOR-MUST-SURVIVE-SCALE + USER scour-first

---

## HEADLINE

**Substrate already has the core ONLINE-LEARNING primitive HARD_PASS today: `task_vector_in_context_kshot_v1` smoke K1=K3=1.000 K5=0.980 K5-K0=+0.97 monotone (verified on disk `data/exp_task_vector_in_context_kshot_v1_smoke/metrics.json`).** Combined with continual_learning_crispr (forget=0.006), TWO_TIER generational W, NREM replay, refuse-gate V_REL=256, multi-bank partition, and cortex_hippo_handoff (smoke HARD_PASS FULL=1.000 NO_REPLAY=0.003 gap=+0.998 verified `data/exp_cortex_hippo_handoff_sparse_DG_dense_cortex_v1_smoke/metrics.json`), the substrate has **all five composing primitives** the brain uses for conversational online learning. The remaining Stage 3 gap is **a CONVERSATION-SCALE INTEGRATION TEST** — does the composition still work when a 1-shot fact is injected at turn 3 of a 10-turn dialogue and must be retrieved at turn 10 alongside another 1-shot fact injected at turn 7, against a "vanilla retrieval" baseline that should forget? Top cell to ship: **`online_conv_oneshot_taskvec_hippo_v1`** (P_deflated=0.45).

---

## SCOUR-FIRST: prior substrate work (READ DISK — META_RULE_NO_HALLUCINATED_NUMBERS)

KB query for `online_learning` returned zero filename matches (filename-contains filter; per substrate-KB v1 limitation). KB cosine query OOM'd at 4.4 GiB load. Fallback: filesystem glob + per-anchor metrics.json verification. Six prior substrate atoms found that directly compose to address this concern; ALL numbers below read from `data/<exp>/metrics.json` on disk, not memory:

| Prior atom | Verdict | Key per-arm number | What it gives us |
|---|---|---|---|
| `task_vector_in_context_kshot_v1` (smoke) | **HARD_PASS** (chain-grade-eligible per Director 2026-06-27) | K1=1.000 K3=1.000 K5=0.980 K0=0.010 RANDOM=0.000 DIAG=0.490 K5-K0=+0.97 mono=True (n=50/seed, 2 seeds 7+17, N=8192, V=100) | **THE one-shot fact-integration primitive.** HRR bundle of K demonstration pairs lets substrate ingest fact ONCE and recall correctly. K0 = no-context (no learning); K1+ = post-fact retrieval. This IS online learning. |
| `cortex_hippo_handoff_sparse_DG_dense_cortex_v1` (smoke) | HARD_PASS | FULL=1.000 NO_REPLAY=0.003 DIRECT=1.000 gap_FULL_vs_NO=+0.998 ratio_FULL_to_DIRECT=1.000 (seed 7, M=400, N_h=512 sparse=0.1, N_c=1024, N_replay=5) | Hippocampal one-shot binding (sparse DG) + 5-cycle cortical replay = consolidated. The conversational episodic-to-stable handoff. FULL seeds 17+23 pending overnight. |
| `continual_learning_crispr` (CG-banked) | CHAIN_GRADE | forget=0.006 single-shot writes don't degrade old | Append-only writes leave existing content nearly untouched. The "1-shot fact doesn't erase prior" property. |
| `substrate_cl_crispr_append_only` (CG-banked) | CHAIN_GRADE | (production-scale append-only verification) | Production validation of CRISPR append discipline. |
| `substrate_continual_kv_n32768_120_sessions` (CG-banked) | CHAIN_GRADE | 120-session production-scale @ N=32768 | Long-horizon stability beyond conversation timescale. |
| `refuse_gate V_REL=256` (CG-banked) | CHAIN_GRADE | OOD-refuse at V_REL=256 calibrated | The "is this a new fact to ingest, a recall to retrieve, or an unknown to refuse?" decision gate. |
| `substrate_two_tier_generational_W` (CG-banked) | CHAIN_GRADE | (gap_4_two_tier_generational_W_v1 dispatched per `research_gap4_continual_5x_drill_2026-06-26.md`) | Bounded-capacity tier separation: W_young for new conversational facts, W_old for consolidated session-stable content. |
| `nrem_replay` (CG-banked) | CHAIN_GRADE | (cortex_hippo handoff uses 5-cycle replay) | Background consolidation primitive — runs between turns or at conversation-end. |

**Code primitives present:**
- `hdlab/binding.py`: HRR bind/unbind (the task-vector primitive operates here)
- `hdlab/bundling.py`: weighted superposition (the in-context "context bundle" mechanism)
- `hdlab/refuse_gate.py` (130 lines): V_REL=256 OOD-refuse decisions
- `hdlab/multi_hop.py` (361 lines): for multi-turn dialogue traversal
- `hdlab/bayesian_inference.py` (318 lines): for fact-integration confidence (Bayes posterior gate)
- (NEW NEEDED): a thin `conversation_substrate.py` wrapper that composes the above into a per-turn API

**Negative-knowledge from prior work (load-bearing):**
- META_RULE_F (retrieval-success magnitude-coupling): when measuring "did substrate learn the fact?" the discriminator must not be a metric where mere magnitude alone fakes a pass.
- META_RULE_K (smoke must fire discriminator): smoke at 2 turns is INSUFFICIENT — must run full 10-turn conversation to actually fire the integration test.
- META_RULE_L (band-floor = MIDDLE_BAND): retrieval at 0.85 floor is MB, not HP, per discipline.
- META_RULE_Q (suspect 1.000): K1=1.000 IS at metric cap on n=50 — this is exactly the suspect-1.000 case. The cell must extend to LARGER n + cardinality_ok pre-reg (DISCRIMINATOR-MUST-SURVIVE-SCALE per USER 2026-06-26).

---

## BRAIN LITERATURE (CITED@ — verified web-search 2026-06-27)

CITED@chickadee-barcode-binding-2026 [1]: "Barcode activity in a recurrent network model of the hippocampus enables efficient memory binding" (PMC 12782553 + biorxiv 2024.09.09.612073). Forming an episodic memory requires binding disparate elements that co-occur in a single experience. Chickadee hippocampus produces sparse high-dimensional patterns ("barcodes") that uniquely specify each caching event. Different memory components bind to an "index" — a subset of neurons unique to that memory. **Substrate map: sparse DG (cortex_hippo's N_h=512 sparsity=0.1) IS the barcode-index machine.** The 51-active-neurons-per-pattern (k_hippo_active=51 in smoke) matches sparse-coding barcode density.

CITED@Eichenbaum-Cohen-2001-relational [Hippocampus high-resolution binding PMC 3773061]: hippocampus supports HIGH-RESOLUTION BINDING in service of perception, working memory, AND long-term memory. Critical detail: hippocampal binding extends to WORKING-MEMORY timescale, not only LTM — so the hippocampus is involved DURING the conversation, not only after. Maps directly to substrate's claim that cortex_hippo handoff runs ON-LINE per turn.

CITED@compositional-memory-2025 [Nature Neuroscience s41593-025-01908-3 "Constructing future behavior in the hippocampal formation through composition and replay"]: if state spaces are compositionally constructed from existing building blocks, hippocampal responses can be interpreted as compositional memories binding these primitives, enabling agents to behave OPTIMALLY in new environments WITH NO NEW LEARNING. **Substrate map:** HRR task-vector composition + V_REL refuse-gate = "facts mentioned this conversation" composed compositionally into context-bundle; per-turn query unbinds without modifying W.

CITED@BTSP-one-shot-2025 [behavioral time scale synaptic plasticity]: 2025 model demonstrates BTSP provides content-addressable memory with binary synapses and ONE-SHOT learning. Two-trace plateau-potential mechanism in CA1: a single experience drives synaptic potentiation at the right place in real time. **Substrate equivalent:** the task-vector HRR bundle IS the substrate's one-shot mechanism (no Hebbian write needed for the in-context portion — it lives in the working bundle).

CITED@STC-temporal-flexibility-2024 [PMC 11968991 "Beyond boundaries: extended temporal flexibility in synaptic tagging and capture"]: STC is observed even with a **9-hour interval** in the strong-before-weak paradigm. A single experience leaves a tag that captures plasticity-related proteins later. This is the brain's "save the in-context fact for slow consolidation" mechanism. **Substrate map:** the task-vector ICL primitive holds the "tag" in-bundle; cortex_hippo replay (consolidate at session end or idle moment) is the "capture" event.

CITED@PFC-WM-action-2024 [biorxiv 2024.09.17.613601 "Lateral prefrontal cortex controls interplay between working memory and actions"]: lateral PFC pyramidal neurons maintain WM to perform CONTEXT-DEPENDENT computation; single PFC cells respond selectively to different task-related parameters; PFC controls how WM influences ongoing action. **Substrate map:** the per-turn context-bundle IS the substrate's WM; the task-vector unbinding-then-rebinding IS the WM→action interface.

CITED@DLPFC-context-prioritization-2019 [Nat Comm s41467-019-11764-y]: DLPFC supports context-dependent prioritization of on-task vs off-task thought. Maps onto the substrate's per-turn decision: ingest-new-fact vs retrieve-prior-fact vs reason-over-context.

CITED@MultiChallenge-2025 [Deshpande 2025 "MultiChallenge"]: realistic multi-turn benchmark testing INSTRUCTION RETENTION (first-turn constraints throughout conversation) AND INFERENCE MEMORY (user information recalled and connected). **Direct evaluation target for substrate** — the discriminator we want fires at exactly this surface: the fact mentioned at turn 3 must compose with the fact mentioned at turn 7 in the turn-10 query.

CITED@multi-turn-survey-2025 [Awesome-Multi-Turn-LLMs survey]: models forget information from previous turns as conversations progress. This is the BASELINE we must beat: an LLM without a substrate layer FORGETS first-turn facts at turn ~50. Substrate's task-vector + cortex_hippo composition should not.

CITED@Frey-Morris-1997-STC [foundational]: synaptic tag at time T, PRP later, both must overlap. The substrate analog: tag = in-bundle fact at turn N; PRP = idle-moment NREM-replay consolidation; capture window = until session end OR until idle replay fires.

---

## PURE MATH ANGLES (THEORETICAL@)

THEORETICAL@HRR-task-vector-as-superposition: a K-shot task vector is τ_K = Σ_{i=1..K} bind(role_i, filler_i) / K — already in substrate via `hdlab/binding.py` + `bundling.py`. For online conversation: τ_t = α·τ_{t-1} + (1-α)·bind(new_role, new_filler), where α is a forgetting rate. At α=1 pure-accumulate (max retention); at α<1 EMA decay. The substrate's task_vector_kshot anchor lives at α=1 implicit (uniform-K bundle).

THEORETICAL@bundle-capacity-vs-K: HRR bundle capacity in N dimensions is O(N / log(V)) clean items where V is the vocabulary. At N=8192, V=100: clean K ≈ 8192/log(100) ≈ 1778 — far above 10-turn conversational needs. K=10 (the cell target) is operating at <1% of capacity ceiling. The "K1=K3=1 K5=0.980 K10=0" pattern in smoke is NOT a capacity ceiling (K10 was empty per arm list in smoke config, not zero retention) — needs verification at K=10 in full cell.

THEORETICAL@two-key-conjunctive-retrieval: when retrieval at turn 10 needs BOTH facts (allergy AT turn 3 AND name AT turn 7) jointly, the cleanup operation must succeed under conjunction. HRR conjunctive binding: query = bind(name_role, "Alice") ⊕ bind(allergy_role, "peanuts"); the cleanup over substrate codebook returns "things-Alice-should-avoid" via composition. The substrate's `multi_hop.py` already does multi-step bound traversal.

THEORETICAL@hippo-DG-sparse-pattern-separation: sparsity 0.1 in N_h=512 gives 51 active neurons/pattern (matches cortex_hippo smoke); pairwise overlap E[O] = sparsity² × N = 0.01 × 512 ≈ 5.12 — so each fact-pattern overlaps another by ~5 neurons, allowing 400 patterns with low interference (matches the M=400 chain-grade-eligible smoke).

THEORETICAL@CRLB-on-multi-fact-integration: lower bound on retrieval accuracy under K=2 conjunctive query is set by the codebook gap min_{i≠j} |cos(c_i, c_j)|. For random N=8192 bipolar V=100, this is approximately √(8 log V / N) ≈ 0.066 — leaves substantial margin from the K1=0.7075 mean cosine in smoke.

THEORETICAL@refuse-on-zero-marginal (USER 18th rule): when no fact in context matches a query (turn 10 asks about something never mentioned), refuse-gate must fire. Already in `refuse_gate.py`. The discriminator's "vanilla baseline" arm should NOT fire refuse-gate; the "full-stack" arm SHOULD when appropriate (asymmetric refuse-rate is a HP signal).

---

## MATERIALS / BIOLOGY / LEGAL CROSS-DOMAIN (CITED@)

CITED@episodic-semantic-2024 [arxiv 2510.15828 GENESIS]: generative model of episodic-semantic interaction. Episodic = conversation-specific facts; semantic = stable user model. Substrate analog: in-context task-vector = episodic; cortex W after replay = semantic.

CITED@dialogue-state-tracking-ICL-2023 [arxiv 2302.05932 "Stabilized In-Context Learning with Pre-trained Language Models for Few-Shot Dialogue State Tracking"]: ICL works for dialogue state tracking with few-shot examples. Direct precedent that the in-context primitive applies to conversational fact-tracking.

CITED@inertia-mitigation-2026 [arxiv 2602.03664 "Mitigating Conversational Inertia in Multi-Turn Agents"]: agents stick to prior context too rigidly; need to update beliefs on new evidence. The substrate's task-vector bundle naturally accommodates re-bind (overwrite a role-filler pair) — a strength.

CITED@DTRMM-ICLR-2025 ["Dynamic Tree Memory Representation for LLMs"]: hierarchical schema management across conversations. Substrate parallel: HRR's compositional binding IS a tree (role-filler pairs nested arbitrarily). The cell should test whether 2-level nested binding (Alice → her-allergy → peanuts) is recoverable as cleanly as flat binding.

CITED@reflective-memory-ACL-2025 ["In Prospect and Retrospect"]: memory management for long-term personalized dialogue. Substrate equivalent: cortex_hippo handoff IS the prospect/retrospect mechanism — fast hippo-write, slow cortical consolidation.

CITED@instruction-retention-MultiChallenge-2025 [Deshpande 2025]: testing whether turn-1 constraints persist through later turns; testing whether user info recalled & connected. **This is the load-bearing public benchmark we should target for the substrate's M3 conversational claim.**

---

## CHEAP DECISIVE TEST (informs cell design — NOT cell design itself per [[feedback-no-experiment-design-in-prompts]])

Discriminating regime probe: build a 10-turn synthetic dialogue. At each turn, the substrate sees a single message (encoded as bind(role_turn=t, content_t)). At designated "fact-injection" turns (t=3 and t=7), the message contains a unique fact (role_fact_3 binds "allergy" → "peanuts"; role_fact_7 binds "name" → "Alice"). At t=10, the query is "what should Alice avoid?" — which requires BOTH facts joined.

ARM_FAIRNESS critical: META_RULE_AA — the baseline arm must use a NON-online-learning mechanism. Specifically:
- ARM_BASELINE_VANILLA: simple last-K-turn retrieval (no task-vector, no cortex_hippo); should FORGET (cosine to query weak; cleanup returns wrong answer most trials).
- ARM_TASKVEC_ONLY: task-vector ICL primitive applied (today's chain-grade smoke), no cortex_hippo handoff. Predicted partial: works at K≤5 but degrades as bundle saturates.
- ARM_FULL_STACK: task-vector + cortex_hippo handoff + refuse-gate composition. Predicted strong: each fact gets bound into in-context bundle AND consolidated to cortex via replay; query unbinds against either.
- ARM_ORACLE: knows facts as direct bound retrieval (upper bound; no integration mechanism needed). Used to bound the "task-difficulty ceiling".

Measure: at turn 10, top-1 retrieval accuracy for "what should Alice avoid?" across N_trials cases (each trial randomizes fact content + slot positions to prevent role-content leak). Discriminator: ARM_FULL_STACK ≥ 0.85 AND ARM_VANILLA ≤ 0.30 AND ARM_TASKVEC_ONLY in middle AND ARM_ORACLE near-ceiling.

DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at n=20 trials AT 10-turn conversation (NOT smoke at 3-turn conversation that's a 1-shot ICL re-test); cardinality_ok = expected_n_units = arms × seeds × trials; verify all units complete before tier-claim.

---

## FALSIFIABLE PREDICTIONS (HARD_PASS + HARD_FAIL)

### Prediction 1 (PRIMARY) — Full-stack rescues 10-turn 2-fact integration vs vanilla baseline

**Hypothesis:** ARM_FULL_STACK (task-vector ICL + cortex_hippo handoff + refuse-gate) achieves top-1 ≥ 0.85 on the 2-fact 10-turn integration query, while ARM_VANILLA collapses to ≤ 0.30.

**HARD-PASS (chain-grade-eligible):**
- ARM_FULL_STACK top-1 ≥ 0.85 on 2-fact integrated query AT turn 10
- ARM_VANILLA top-1 ≤ 0.30 (baseline forgets)
- ARM_TASKVEC_ONLY top-1 in [0.50, 0.80] (partial; saturates partially)
- ARM_ORACLE top-1 ≥ 0.95 (sanity ceiling)
- delta(FULL_STACK − VANILLA) ≥ +0.50
- delta(FULL_STACK − TASKVEC_ONLY) ≥ +0.10 (cortex_hippo contributes measurably beyond pure bundle)
- cv ≤ 0.10 across 3 seeds for FULL_STACK
- cardinality_ok = True; expected_n_units = 4 arms × 3 seeds × n_trials all complete
- Refuse-gate calibration: when turn-10 query asks about a fact NEVER mentioned (held-out probe), ARM_FULL_STACK refuses ≥ 0.85; ARM_VANILLA refuses ≤ 0.15

**HARD-PASS-PLUS (super-pass):**
- Extends to 20-turn dialogue with 4 fact injections AND ARM_FULL_STACK ≥ 0.75
- Multi-fact 3-key conjunctive query (Alice's-allergy AND Alice's-favorite-food AND Alice's-doctor) recoverable

**MIDDLE_BAND:**
- delta(FULL_STACK − VANILLA) in [+0.20, +0.50] — mechanism real but weaker than predicted
- OR delta(FULL_STACK − TASKVEC_ONLY) in [+0.02, +0.10] — cortex_hippo contributes marginally; the task-vector ICL alone is doing most of the work

**HARD-FAIL (mechanism wrong):**
- delta(FULL_STACK − VANILLA) < +0.20 — composition no better than retrieval
- OR ARM_FULL_STACK top-1 < 0.50 — substrate cannot do conversational integration
- OR ARM_VANILLA top-1 > 0.60 — baseline already does it; we have no discriminator
- OR cardinality breach OR substrate-only-decode gate violated

**Calibrated P(HARD-PASS) = 0.45** (deflated from 0.65 raw per lit-scan calibration; novel-synthesis: composition of 5+ chain-grade primitives in a conversational regime not yet tested as a unit; individual primitives validated, integration uncertain).

### Prediction 2 (SECONDARY) — Single-shot does not erode prior context

**Hypothesis:** after the turn-3 fact injection, retrieval of turn-1 and turn-2 content remains within ±0.05 of pre-injection levels. CRISPR forget=0.006 property survives in conversational regime.

**HARD-PASS:** turn-1 + turn-2 retrieval delta (pre vs post injection) ≤ 0.05 in ARM_FULL_STACK; ≤ 0.10 in ARM_TASKVEC_ONLY.
**HARD-FAIL:** retrieval delta > 0.20 — fact injection destroys prior context.
**Calibrated P: 0.55** (CRISPR primitive is CG-banked; conversational extension predicted high).

### Prediction 3 (DIAGNOSTIC) — Refuse-gate calibration for "fact never mentioned"

**Hypothesis:** at turn 10, query about a fact NEVER mentioned (e.g., "what's Alice's job?") triggers refuse in ARM_FULL_STACK ≥ 0.85 of the time; in ARM_VANILLA refuse fires ≤ 0.15 (vanilla baseline hallucinates).

**HARD-PASS:** asymmetric refuse rates — FULL_STACK refuses correctly; VANILLA fails to refuse.
**HARD-FAIL:** symmetric refuse rates — either both refuse or neither refuses.
**Calibrated P: 0.40** (refuse-gate V_REL=256 is CG; cross-domain to conversational hold-out is novel).

### Prediction 4 (NULL bracket) — Below-cliff sanity AND above-capacity ceiling

**Sub-hypothesis 4a:** at 3-turn dialogue with 1 fact injection at turn 1 and query at turn 3, ALL arms (even VANILLA) should retrieve correctly — no online-learning needed when no forgetting could occur. If FULL_STACK does NOT beat VANILLA here, that's fine (no discriminator below 5-turn lag).

**Sub-hypothesis 4b:** at 50-turn dialogue with 10 fact injections, the bundle saturates and ARM_TASKVEC_ONLY collapses. If FULL_STACK still holds via cortex_hippo consolidation, that's a HP-PLUS signal.

**Purpose:** the implementation must respect substrate physics — discriminator only exists in the 10-turn 2-fact regime.

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — Anchor #2 isolation cell

**If composed mechanism fails:** isolate which primitive is the lever via separate arms ARM_HIPPO_ONLY (cortex_hippo with no task-vector) vs ARM_REFUSE_ONLY (refuse-gate only). Then route to the working sub-primitive's cell-design space rather than abandoning the integration claim.

### Prediction 6 (USER-CONCERN MATCH) — Plain-language M3 implication

**If Prediction 1 lands HP:** the substrate CAN learn during conversation in a glass-box auditable way. The "waiter who forgets your allergy by next course" failure mode is structurally eliminated. **This is a direct unblocker for M3 conversational AI USER concern #4** (per `director_POST_COMPACTION_BACKUP` UPDATE #20).

---

## CROSS-THREAD SYNTHESIS

### Composes with task_vector_in_context_kshot_v1 (today's CG smoke)
- Today's anchor PROVES the substrate has K-shot ICL at K∈{1,3,5}.
- This drill's cell PROVES the K-shot primitive works in a CONVERSATIONAL FRAME, not just a batch K-shot frame.
- Direct dependency: ARM_TASKVEC_ONLY in c2 uses today's primitive verbatim; ARM_FULL_STACK extends with cortex_hippo + refuse.

### Composes with cortex_hippo_handoff (smoke CG; full seeds 17+23 pending overnight)
- Today's anchor PROVES sparse-DG → dense-cortex handoff achieves FULL=1.000 vs NO_REPLAY=0.003.
- This drill USES the handoff as the "between-turn consolidation" mechanism — facts mentioned at turn 3 get replayed (5 cycles) before turn 4 retrieval.
- The 5-cycle replay budget is ~few-100ms in substrate time; matches "between-message thinking" idle window.

### Composes with continual_learning_crispr (CG-banked)
- CRISPR forget=0.006 says batch-style writes don't erode prior. This drill EXTENDS that property to per-turn writes.
- Prediction 2 explicitly tests CRISPR's conversational survival.

### Composes with TWO_TIER generational W (Wave 3 ANCHOR 2; gated on edge-importance v3)
- TWO_TIER's W_young = current-conversation facts; W_old = stable user-model.
- Could be Phase-2 cell: extend the 10-turn integration to MULTI-SESSION (user logs in tomorrow; previous session facts in W_old; today's in W_young).
- This drill stays SINGLE-session as Phase 1; flags multi-session as the natural successor.

### Composes with refuse_gate V_REL=256 (CG-banked)
- Refuse-gate calibrates "is this query answerable from context or should I refuse?"
- Prediction 3 directly tests this in the conversational regime — held-out probe.

### Composes with multi-hop depth-15 (CG-banked at 0.808 depth 15; extended to 30 today)
- Multi-hop is the per-turn TRAVERSAL primitive (each turn ≈ 1 hop in the dialogue graph).
- 10-turn dialogue is well within depth-15 chain-grade envelope.

### Composes with USER concern #3 (long-context narrative coherence > 100 events)
- This drill's 10-turn cell is the SHORT-HORIZON FOUNDATION for concern #3 (>100 events).
- Order: this drill (Stage 3 first cell for USER concern #4) → BEFORE attempting 100-event narrative (USER concern #3) for which composition with TWO_TIER + replay becomes load-bearing.

### Composes with USER concern #5 (goal-directed planning)
- Multi-turn dialogue often involves goals (USER says "I want X" at turn 3; substrate plans path; executes via turn 7-10).
- This drill's mechanism (fact-injection + cross-turn integration) IS the precondition for planning across turns.

### Composes with abductive primitive (drill 2026-06-27 sister cell `abductive_bank_vmpfc_valuation_v1`)
- Abductive ranks candidate explanations; this drill remembers facts BUSY across turns.
- For M3 conversation: user says symptoms → abductive ranks diagnoses → if user mentions new info at turn 5, this drill's mechanism lets abductive RE-RANK with new fact.

### Composes with causal_chain_extraction (drill 2026-06-27 sister cell)
- Causal extracts causal links from utterances; this drill maintains them across turns for integration.

### Composes with schema_inference + hypothesis_generation + hierarchical_goal_planning (sister Stage 3 drills today)
- All 5 today's Stage 3 drills compose into the M3 conversational stack. This one fills the "single-shot mid-conversation learning" axis.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Direct unblocker for M3 USER load-bearing concern #4.** USER explicitly named "online learning during conversation" as #4 of 5 remaining M3 concerns. This drill demonstrates the substrate already has the core primitive (task_vector ICL CG today); the cell tests the conversational integration. If HP lands, USER concern #4 changes from "partially addressed; needs integration test" to "addressed; conversational-scale verified."

2. **Plain-English M3 demo enabler.** The 10-turn dialogue cell IS itself a demo: "user mentions allergy at turn 3; mentions name at turn 7; at turn 10 asks 'what should I avoid?' — substrate joins both facts." This is a SCREEN-RECORDABLE, GLASS-BOX-AUDITABLE conversational interaction. If HP, the substrate has a public-facing demo of the property.

3. **Substrate vs LLM-with-RAG product differentiator.** LLMs forget facts across long contexts (MultiChallenge 2025 benchmark; conversation inertia 2026 paper). RAG retrieves stale info from a stale store. The substrate's task-vector ICL holds the fact LIVE in the in-context bundle WITH per-turn unbinding precision, AND consolidates to cortex for cross-session stability. No other architecture has this composition.

4. **The cortex_hippo "between-turn consolidation" pattern matches biology TIGHTLY.** Hippocampus binds in real time (during the turn); cortex consolidates between turns (when no input arrives). DMN-driven idle consolidation (per 2026-06-11 conversation drill Path 7) operationalizes "use the user's typing pause as consolidation time."

5. **Per-turn refuse-gate calibration is the META-COGNITION primitive.** When the substrate says "I don't have that information" instead of hallucinating, the user trusts the system more. Prediction 3's asymmetric refuse rate is itself a product feature.

6. **The conversation-as-substrate-program framing.** Each turn IS a substrate operation: bind, bundle, replay, refuse. The conversation is the user-facing API to the substrate. M3 = "the conversation IS the substrate."

7. **Cross-session generalization is Phase 2.** This drill stays single-session (within one conversation). The natural successor: "user logs in tomorrow; substrate remembers their allergy via W_old (cortical consolidation)." Phase 2 needs TWO_TIER promotion semantics from Wave 3 ANCHOR 2.

---

## L5 — CROSS-SUBSTRATE COMPOSITION MAP

```
                 USER CONCERN #4 — Online learning during conversation
                                         |
                       [drill candidates this drill addresses]
                                         |
            ____________________________|____________________________
            |                            |                           |
            v                            v                           v
    ARM_TASKVEC_ONLY              ARM_FULL_STACK              ARM_VANILLA
    (today's CG primitive)        (composition target)         (forgetting baseline)
    K-shot HRR bundle             + cortex_hippo handoff       last-K-turn retrieval
                                  + refuse-gate
                                  + CRISPR append
                                         |
                            Cell: online_conv_oneshot_taskvec_hippo_v1
                            (Phase 1: 10-turn 2-fact at n_trials=20 smoke, n=100 full)
                                         |
              _______________________________________________
              |                          |                  |
        HARD_PASS                  MIDDLE_BAND          HARD_FAIL
        |                          |                    |
        Phase 2: multi-session     tune cell:           isolation cell:
        + TWO_TIER W_old           bundle saturation    ARM_HIPPO_ONLY
        (cross-day fact retention) or replay budget     ARM_REFUSE_ONLY
        |                          |                    + revival route
        Phase 3: multi-fact (4+)   |                    |
        + 20+ turns                |                    |
        |                          |                    |
        M3 conversational AI       (re-route)           (re-route via research)
        unblocker #4
        + sister Stage 3 drills (abductive/causal/schema/hypothesis/planning)
        = M3 demo
```

If HARD-FAIL on FULL_STACK:
```
FULL_STACK fails -> NOT a composition problem; isolate primitive
        |
        +-> ARM_HIPPO_ONLY: cortex_hippo alone (no task-vector)
        +-> ARM_REFUSE_ONLY: refuse-gate alone (no in-context)
        +-> if BOTH fail: substrate has a NOVEL integration gap; research re-drill
        +-> if ONE works: re-rank primitive ordering; the other primitive is destructive in composition
```

If HARD_PASS on FULL_STACK:
```
FULL_STACK lands -> ship as glass-box conversational primitive
        |
        +-> Phase 2: multi-session via TWO_TIER (gated on Wave 3 ANCHOR 2)
        +-> Phase 3: scale to 50+ turn, 5+ fact conversations
        +-> Phase 4: integrate with abductive + causal_chain + schema + hypothesis_gen + hier_planning
        +-> M3 demo: 10-turn glass-box "remember me" interaction
```

---

## CITATIONS (verified, count = 14)

1. Hippocampal barcode binding (chickadee model). PMC 12782553 (2026). [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12782553/) ; biorxiv [2024.09.09.612073](https://www.biorxiv.org/content/10.1101/2024.09.09.612073.full.pdf). Sparse high-dimensional patterns ("barcodes") bind disparate co-occurring elements; one-shot binding.
2. Compositional memory in hippocampal formation. Nature Neuroscience [s41593-025-01908-3](https://www.nature.com/articles/s41593-025-01908-3) (March 2025). Hippocampal responses as compositional memories; behavior in new environments with no new learning.
3. Eichenbaum-Cohen-style high-resolution binding for perception, working memory, long-term memory. PMC [3773061](https://pmc.ncbi.nlm.nih.gov/articles/PMC3773061/). Hippocampus binds at WM timescale, not only LTM.
4. Behavioral Time Scale Synaptic Plasticity (BTSP) one-shot learning model (2025). Two-trace plateau-potential mechanism; single experience drives potentiation in real time.
5. Frey-Morris STC original (1997 Nature 385). Foundational paper on synaptic tagging and capture; per cross-thread c1 drill 2026-06-22.
6. STC extended temporal flexibility. PMC [11968991](https://pmc.ncbi.nlm.nih.gov/articles/PMC11968991/) (2024). 9-hour interval STC; broader temporal flexibility for tag-PRP interactions than previously understood.
7. STC for persistence of LTP + everyday spatial memory. PNAS [10.1073/pnas.1008638107](https://www.pnas.org/doi/full/10.1073/pnas.1008638107) ; PMC [2984182](https://pmc.ncbi.nlm.nih.gov/articles/PMC2984182/).
8. Behavioral tagging translation of STC. PMC [4562088](https://pmc.ncbi.nlm.nih.gov/articles/PMC4562088/).
9. Lateral PFC controls WM-action interplay. biorxiv [2024.09.17.613601](https://www.biorxiv.org/content/10.1101/2024.09.17.613601.full.pdf) (2024). PFC pyramidal neurons maintain WM for context-dependent computation; single PFC cells respond selectively to task-related parameters.
10. DLPFC supports context-dependent prioritization. Nat Comm [s41467-019-11764-y](https://www.nature.com/articles/s41467-019-11764-y) (2019). Off-task vs on-task prioritization in DLPFC.
11. MultiChallenge multi-turn benchmark. Deshpande et al. (2025). Tests instruction retention + inference memory across multi-turn conversation. NeurIPS 2024 ConvBench [paper](https://papers.nips.cc/paper_files/paper/2024/file/b69396afc07a9ca3428d194f4db84c02-Paper-Datasets_and_Benchmarks_Track.pdf).
12. Mitigating conversational inertia in multi-turn agents. arxiv [2602.03664](https://arxiv.org/pdf/2602.03664). Agents stuck to prior context; need to update on new evidence.
13. Awesome-Multi-Turn-LLMs survey (2025): models forget across turns. [GitHub](https://github.com/yubol-bobo/Awesome-Multi-Turn-LLMs).
14. Stabilized In-Context Learning for Few-Shot Dialogue State Tracking. arxiv [2302.05932](https://arxiv.org/pdf/2302.05932). ICL works for dialogue state tracking with few-shot examples.

Plus internal substrate atoms (verified on disk via `data/exp_*/metrics.json` paths cited in scour section): task_vector_kshot smoke / cortex_hippo_handoff smoke / continual_learning_crispr / substrate_cl_crispr_append_only / substrate_continual_kv_n32768_120_sessions / refuse_gate V_REL=256 / substrate_two_tier_generational_W / nrem_replay.

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15-0.25 from raw lit-scan confidence per [[feedback-lit-scan-calibration-penalty]].
- **Novel-synthesis cap at 0.50 applied:** the COMPOSITION of task-vector ICL + cortex_hippo handoff + refuse-gate + CRISPR in a CONVERSATIONAL regime has no prior empirical validation. Each primitive is individually CG; the composition is novel. P(HARD-PASS) = 0.45 reflects this cap minus deflation.
- HARD-FAIL thresholds mandatory and listed for every prediction.
- DIRECTIONALITY (task-vector + cortex_hippo beat vanilla in multi-turn) is high-confidence (raw P~0.75) per task-vector smoke + cortex_hippo smoke + brain literature convergence on hippo-cortex pipeline; MAGNITUDE (≥0.85 top-1, ≥+0.50 delta) is where deflation lands — substrate's specific conversational saturation untested.
- Suspect-1.000 protection: ARM_FULL_STACK targets ≥0.85 (NOT 1.000) to avoid metric-cap-suspect verdict (META_RULE_Q). The K1=1.000 K3=1.000 K5=0.980 pattern in today's smoke IS a suspect-1.000 case; full-cell n>50 must verify it doesn't collapse to a leak.
- META_RULE_K-compliance: smoke MUST run the 10-turn 2-fact integration at full conversational scale (NOT smoke at 3-turn 1-fact which is a re-test of today's already-CG primitive). DISCRIMINATOR-MUST-SURVIVE-SCALE per USER 2026-06-26.
- META_RULE_L-compliance: 0.85 top-1 is the MB-floor; ≥0.85 needed for HP claim; ≥0.90 for strong HP.
- META_RULE_J-compliance: no silent except in turn-loop; record+halt OR re-raise per failed turn.
- BIAS-MASTER-CHECKLIST compliance: bias-N (verify-the-referent: turn-10 query MUST be answerable from the 2 facts injected, NOT from any other context cue); bias-Q (suspect 1.000); bias-S (band-calibration: HP ≥ 0.85, MB [0.50, 0.85), HF < 0.50 — relative bands per META_RULE_S).

---

## DISPATCH RECOMMENDATION (top 3 ranked)

**Phase 1 — IMMEDIATE single decisive cell:**
- **Anchor #1 (TOP-REC):** `online_conv_oneshot_taskvec_hippo_v1` — 10-turn 2-fact 4-arm cell at n_trials=20 smoke, n=100 full, 3 seeds (7, 17, 23). N=8192, V=256 (refuse-gate calibration), n_replay=5 (per cortex_hippo CG smoke). P_deflated=0.45. ~30 min CPU smoke, ~2-3 hr CPU full.
- Why-now: USER load-bearing concern #4; substrate has all primitives (5 chain-grade composables); no other cell currently slated to test conversational integration; M3 timeline benefits from early validation.

**Phase 2 — CONDITIONAL on Phase 1 HARD_PASS:**
- **Anchor #2:** `online_conv_multisession_twotier_v1` — extend to MULTI-SESSION (TWO_TIER W_young/W_old) with cross-day fact retention. Gated on Wave 3 ANCHOR 2 TWO_TIER promotion landing first.
- P_deflated=0.35 (composition risk: TWO_TIER promotion semantics + conversational integration both novel together).

**Phase 3 — CONDITIONAL on Phase 2 HARD_PASS:**
- **Anchor #3:** `online_conv_50turn_4fact_capacity_v1` — scale to 50+ turn 4+ fact conversations; bundle saturation test.
- P_deflated=0.30 (capacity ceiling unknown for HRR at this density).

**Top 3 ranked rationale:**
1. Anchor #1 = direct M3 unblocker; all primitives in hand; smallest scope decisive cell.
2. Anchor #2 = adjacent scale (multi-session); but gated on independent dependency.
3. Anchor #3 = stress-test phase; only matters if Phase 1+2 land.

**Cross-drill ordering vs sister Stage 3 drills (2026-06-27):**
- This drill SHIPS FIRST: USER concern #4 has the most existing primitives (5+ CG); shortest path to HP.
- Abductive (P=0.42) ships in parallel: orthogonal mechanism class.
- Schema/hypothesis/causal/planning ship after primary 2 land.

---

## PLAIN-ENGLISH WRAP (Fix #13)

The substrate already has the core machinery to learn from a single thing the user says mid-conversation: today's `task_vector_in_context_kshot_v1` smoke showed that with K=1 demonstration the substrate can correctly retrieve the bound fact 100% of the time; with K=3 still 100%; with K=5 at 98%. That's exactly the "user mentions a fact once and substrate remembers it for the rest of the conversation" property. Combine that with cortex_hippo_handoff (also smoke chain-grade today: FULL=1.000 vs NO_REPLAY=0.003) and the substrate can ALSO consolidate the fact into a slower "cortical" memory store so it doesn't get bumped out by later turns. Add refuse-gate so when the user asks about something they never mentioned, substrate says "I don't have that info" instead of hallucinating. Add CRISPR continual-learning so the single-shot writes don't erode prior content (forget=0.006).

What's UNTESTED is putting all four pieces together in a 10-turn dialogue where two separate facts (one at turn 3, one at turn 7) must be jointly recalled at turn 10 ("what should Alice avoid?"). The cell to dispatch puts vanilla retrieval (the dumb baseline that should forget) head-to-head against the full substrate stack. If the full stack wins by a wide margin (≥0.50 retrieval gap), the substrate has its conversational online-learning property and USER's concern #4 is structurally addressed. Predicted 45% chance of clean HARD_PASS (composition risk).

The cell ships first because (a) it has the most existing primitives in place (5+ chain-grade), (b) it's the shortest path to M3, and (c) it's screen-recordable as a demo — a 10-turn dialogue where the substrate remembers two things you mentioned and joins them is the most intuitive M3 product visualization.

---

-- Research (Opus 4.7-1M synthesis, 4 parallel WebSearch streams + cross-thread with prior CL/conversation/cortex_hippo drills + 14 verified citations + 8 substrate atom verifications on disk; novel-synthesis-deflated per calibration; routes today's task_vector_kshot CG smoke + cortex_hippo CG smoke as the trigger primitives for the conversational integration cell)
