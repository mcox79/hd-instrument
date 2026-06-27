# RESEARCH (Director): 2x DRILL — cortex-as-router (operators LIVE in cortex schemas)

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER deep drill. Cortex-closure agent is authoring `cortex_as_router_v1` (sequential-dependency on PFC-controller + schema-integration). My job here is the 2x DRILL that pressure-tests the design + proposes alternatives + locks fairness discipline.
**Calibration:** lit-scan deflation -0.15 to -0.25; novel-synthesis cap 0.50; brain-existence-proof bump +0.10 where earned; generic-terms-only per query-privacy.
**Builds-on:**
- `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` — prior depth drill (Cand 1 = separate-pathway R_schema query-router from query; assumes SEPARATE operator bank).
- `notes/research_drill_brain_multihop_M1_schema_chunking_cortex_3x_2026-06-27.md` — same-day drill on schema-chunking; operators-as-extracted-schemas mechanism.
- Wave 1 `pfc_controller_per_step_operator_select_v1` (currently runs separate operator bank; cosine-argmax over 4 operators).

---

## HEADLINE (one-line synthesis)

When PFC routes operators, the brain does NOT pick from a separate operator bank — it picks from the SAME cortex schemas that store content. This is structurally analogous to the **continuation-passing-style (CPS) interpreter** in pure math (operators ARE first-class data in the same memory) and the **mixture-of-experts (MoE) with token-conditioned gating where experts share representation space** in computation. In the brain, this is the **Miller-Cohen 2001 PFC theory** (PFC encodes task-rules-as-context that BIAS cortex schemas; the schemas themselves carry the operator semantics via their connectivity profile) combined with **Mante-Sussillo 2013 PFC-driven contextual gating** (same neurons compute different functions depending on PFC context vector). Two CONCRETE substrate-native architectures emerge: (TOP-1) **Cortex-schema-as-operator with PFC-emitted context-key gating** — at each hop, PFC emits a context-key c_h; the operator is the cortex schema whose key is closest to c_h; binding step is `state_h+1 = bind(state_h, schema_argmax)` where the schema's role is BOTH content-binding (it gates which atoms are in scope) AND function-binding (it determines unbinding direction by being COMPOSED with state); (TOP-2) **Two-channel routing where context-vector multiplicatively modulates a SHARED schema bank** — operators don't exist as discrete items; PFC's context-vector `c_h` element-wise modulates the cortex-schema cleanup `cleanup(modulate(c_h, schema_bank) @ key)` which gives a CONTINUOUS operator selection (no hard argmax) — this is the Mante-2013 contextual-gating brain mechanism translated to substrate-FHRR. Both arms must beat separate-operator-bank baseline by ≥ 0.10 at EQUAL operator-count to be chain-grade-eligible. **P_deflated TOP-1 = 0.40; P_deflated TOP-2 = 0.45.** TOP-2 ranks higher because Mante-2013 is a stronger brain prior (recorded from PFC neurons; not just inferred).

Plain English: the brain doesn't keep "the operators" in one drawer and "the data" in another. It uses the same cortex tissue for both — what makes something an "operator" vs "data" at any given moment is which PFC context-vector is currently biasing the cortex. Substrate analog: don't store 4 operators in a separate bank; let cortex schemas BE the operators, picked by a PFC-emitted context-vector that biases the cortex bank. Two flavors: hard-pick (cosine-argmax over schemas — TOP-1) or soft-modulate (context-vector element-wise multiplies the schema bank — TOP-2). The soft variant is closer to Mante-2013's brain finding.

---

## ANGLE A — PURE MATH + COMPUTATION (interpreter theory + tensor structure)

### A.1 — Free-monad / CPS interpreter view

**Mechanism (lit anchor):** in functional-programming theory, the free monad over a functor F gives the most general "first-class operations" model — operations are DATA (constructors of the free monad), and an `interpret` function unfolds them by pattern-match. In continuation-passing style (CPS), the program is rewritten so every operation explicitly threads its "what to do next" continuation; the result is that the choice of next operation is literally a value in the same address space as the data being computed on.

**Substrate-native mapping:** at each hop, the substrate state is `state_h`. A free-monad-substrate interpreter would treat `state_h` as carrying BOTH the data AND a "next-operation tag" in its high-dimensional encoding. The PFC controller's job is to READ the next-operation tag (project out a sub-component of `state_h`) and apply the corresponding cortex schema. Crucially: the operator-tag and the data live in the SAME vector — they are not in separate banks.

**Substrate-feasibility:** FHRR's bind/unbind operations support this directly. `state_h = data_h ⊕ tag_h` (additive superposition); unbind via `tag_h ≈ state_h ⊙ data_h⁻¹` IF tag_h is in cortex-schema basis. Substrate primitive: existing bundle/unbind; no new primitive needed.

**What this gives us mathematically:** the COMPUTATIONAL CLASS of the substrate becomes equivalent to a small-instruction-set machine where the "instructions" are cortex schemas — and the number of instructions scales with cortex-schema count (potentially thousands), not the 4-operator bank Wave 1 tests. This is a strict superset of Wave 1's expressive power.

### A.2 — Mixture-of-Experts (MoE) with shared-representation experts

**Mechanism (lit anchor):** Switch Transformer (Fedus 2021) routes each token to ONE of N experts via top-1 gating. Standard MoE keeps experts in SEPARATE parameter banks. BUT **GShard's "shared-routing" variant** (Lepikhin 2020) lets multiple experts share a base parameter space and differ only in a context-modulated projection — equivalent to "the experts ARE the same parameters, viewed through different gates."

**Substrate-native mapping:** treat each cortex schema as an MoE "expert," but the experts share the same N-dim representation space (substrate's cortex bank). The PFC controller is the gate. Routing = softmax(PFC_query · cortex_schema_keys); the winning schema applies its specific projection. The operators are NOT separate from cortex — they ARE the cortex schemas, addressed by PFC-emitted gates.

**Mathematical difference from "operators in separate bank":** capacity (substrate cortex bank has 5-200x more atoms than a 4-operator bank); cognitive load (no separate parameter set to maintain); compositionality (operators can be COMBINED via bundling cortex schemas — `op_combined = schema_A + schema_B` — which is impossible with a discrete operator bank). The mathematical class moves from "4-state finite automaton" to "vector-addressed Turing-like machine" with capacity bounded by cortex-bank size.

### A.3 — Tensor-network contraction with op-choice at each node

**Mechanism (lit anchor):** in tensor networks (Penrose; Markov-Shi 2008; MERA — multi-scale entanglement renormalization ansatz), a computation is a graph where each NODE applies a tensor; the "operator" at each node is chosen from a vocabulary. In MERA, the choice IS the tensor — and the tensors are SHARED across scale via a translation-invariance assumption (the same operator-tensor appears at many nodes of the network).

**Substrate-native mapping:** the multi-hop chain is a tensor-network contraction. At each hop, the operator-tensor is a cortex schema. SHARED-schema MERA-style means cortex schemas are RE-USED across hops (the same "navigate-spatial-relation" schema applies at hop 3 AND hop 5 — substrate doesn't allocate a separate operator per hop). This is a substrate-cognitive-economy argument: brain doesn't need a new operator per cognitive step; it re-uses the schema that fits the current PFC context.

**Why it's mathematically cleaner than separate-bank:** with a SHARED cortex-as-operator bank, the per-hop computational cost is O(|cortex|) instead of O(|cortex| + |op_bank|). The information theory: PFC's context vector is the ONLY per-hop state; everything else is shared. Compression argument.

### A.4 — Routing as attention over operator-space

**Mechanism (lit anchor):** Transformer attention is literally Q-K-V routing where Q is the current state and K are candidate addresses. When K are interpreted as "operator addresses" (rather than memory addresses), attention IS operator-selection. The "attention head" abstraction is precisely a learned router from state-space to operator-space.

**Substrate-native mapping:** PFC emits a query vector Q_pfc; cortex schemas have keys K_schema; attention weights = softmax(Q_pfc · K_schema / sqrt(N)); winning schema (top-1 or top-K) is the operator for this hop. The values V_schema are the cortex content. Soft-attention version: state_h+1 = Σ_i softmax_i · V_schema_i (continuous mixture; no hard choice).

**Why it differs from Wave 1's argmax:** Wave 1 uses cosine-argmax over 4 discrete operators. Attention-substrate uses softmax over the full cortex bank. Strict generalization.

### A.5 — Differentiable Neural Computer (DNC) read/write head model

**Mechanism (lit anchor):** Graves 2016 DNC has separate read and write heads operating over a SHARED memory. The controller decides at each step which memory location to read from / write to via content-based + location-based addressing. "Operators" in DNC are not a separate bank — they are READ/WRITE OPERATIONS on the same memory.

**Substrate-native mapping:** PFC controller = DNC controller. Cortex = DNC memory. At each hop, PFC emits (read_key, write_key, gates). Cortex content addressed by content-similarity to keys. The "operator" at each hop is determined by WHICH cortex location PFC reads from — and that location's content IS the operator semantics.

**This is a cleaner brain analog than Wave 1's separate bank.** DNC is a literal implementation of "operators-live-in-memory."

### ANGLE A — concrete mechanism proposals (3)

| # | Proposal | Mechanism in 1 line | Fairness considerations |
|---|---|---|---|
| **A-Prop-1** | **PFC-emitted context-key cosine-argmax over cortex** | At hop h, PFC emits `c_h ∈ R^N`; pick cortex schema `s* = argmax_i(c_h · cortex_keys_i)`; apply `state_h+1 = bind(state_h, s*)` | (a) shared-W: cortex bank N-dim = operator-bank N-dim; (b) equal-count: cortex-schema-as-operator arm restricted to TOP-K=4 cortex schemas (matches separate-bank count) UNLESS sub-experiment isolates the "MORE operators help" hypothesis; (c) verify-the-referent: log which cortex schema was picked per hop; check that DIFFERENT hops pick DIFFERENT schemas (not always same one) — else discriminator failed to fire |
| **A-Prop-2** | **PFC context-vector multiplicative modulation (Mante-2013 substrate analog)** | At hop h, PFC emits `c_h`; modulated cortex bank = `cortex_keys * c_h` (element-wise); apply `state_h+1 = bind(state_h, cleanup(cortex_modulated @ key_h))` — soft, continuous, no argmax | (a) shared-W constraint mandatory; (b) `c_h` initial scale matched to operator-bank baseline — same parameter count budget; (c) verify the modulation is non-trivial (track `|c_h - 1|` magnitude across hops; if collapses to 1, modulation is silent) |
| **A-Prop-3** | **CPS-style tag-projection within bundled state** | `state_h = data_h + tag_h` (additive bundle); at hop h, unbind `tag_h ≈ state_h ⊙ data_h⁻¹`; project tag_h onto cortex-bank to pick operator; data_h carries the content | (a) data/tag space-sharing — substrate must have enough N-dim to bundle without crosstalk (N≥8192 likely required); (b) discrimination test: tag_h decoded from state_h must MATCH PFC-intended operator with cosine ≥ 0.5; otherwise tag was destroyed in bundling |

### ANGLE A P-estimate

- Raw P (≥1 of A-Prop-1/2/3 lifts compositional reasoning ≥ 0.10 over separate-bank baseline): **0.55** (MoE-shared-experts + Mante-2013 multiplicative gating + DNC-shared-memory all have lit precedent in deep-learning success cases).
- Lit-scan deflation: **-0.20** (substrate-FHRR composition is novel; deep-learning MoE doesn't directly port).
- Novel-synthesis cap: 0.50 binds.
- **A-angle P_deflated = 0.40.**

---

## ANGLE B — BIOLOGY + BRAIN (PFC ↔ cortex routing literature)

### B.1 — Miller-Cohen 2001 PFC theory

**Mechanism (lit anchor):** Miller & Cohen 2001 (Annu Rev Neurosci, ~24,000 citations) — PFC theory: PFC neurons encode TASK RULES (not stimuli or responses directly). When a rule is active, PFC outputs a context signal that biases posterior cortex (sensory + parietal + temporal) toward the rule-relevant pattern. The mechanism is BIASED-COMPETITION (Desimone-Duncan 1995): cortex neurons compete; PFC context bias makes some win.

**Key insight for substrate:** the "operators" in the brain are NOT separate from the cortex schemas they operate on. PFC emits a CONTEXT (task-rule encoding); the context biases the cortex; whichever cortex schema fires under that bias IS the operator for this moment. Same cortex tissue can implement DIFFERENT operators under different PFC contexts.

**Substrate-native mapping:** PFC = controller that emits context vector `c_h ∈ R^N` per hop. Cortex = schema bank. The operator at hop h is determined by which cortex schema wins biased competition under `c_h` — NOT by picking from a separate operator bank.

### B.2 — Mante-Sussillo 2013 PFC contextual gating

**Mechanism (lit anchor):** Mante, Sussillo, Shenoy, Newsome 2013 (Nature) — recorded from PFC of monkeys doing a context-dependent perceptual decision task (sometimes attend-color, sometimes attend-motion; same stimulus). Found PFC neurons encode the CURRENT CONTEXT as a low-dim manifold; the context selectively GATES which sensory dimension drives the decision. RNN modeling reproduces the data: same units, different context input, completely different computation. The PFC context vector ACTS BY MULTIPLICATIVELY MODULATING the sensory representation — not by switching to a separate "color processor" vs "motion processor."

**Why this is the strongest brain prior for cortex-as-router:** Mante-2013 is the LANDMARK empirical demonstration that the brain does context-dependent computation via PFC-modulation of shared cortex, NOT via switching between separate processors. The 2013 paper has ~2000 citations and is the foundational empirical result for the cortex-as-router hypothesis.

**Substrate-native mapping:** PFC's context vector `c_h` element-wise multiplies (or matrix-multiplies via low-rank projection) the cortex schema bank. The "operator" at hop h is whichever cortex pattern survives the modulation. Continuous; no hard argmax. This is structurally identical to A-Prop-2.

### B.3 — Wallis-Anderson-Miller 2001 task-relevant categorical PFC neurons

**Mechanism (lit anchor):** Wallis, Anderson, Miller 2001 (Nature) — PFC neurons in monkeys encode TASK-RELEVANT CATEGORIES (cat vs dog, same vs different, etc) AS A FUNCTION OF THE CURRENT RULE. Same neuron, different rule → different category boundary. The categorical representation IS task-rule-dependent.

**Substrate-native mapping:** PFC's per-hop context vector `c_h` parameterizes a CATEGORY BOUNDARY in cortex-schema-space. Whichever side of the boundary the current state falls on determines which cortex schema applies. This is a softer version of B.1 — instead of "PFC picks an operator," "PFC defines a category boundary; cortex decides which side state falls on."

### B.4 — Tonegawa engram cells = cortex schemas

**Mechanism (lit anchor):** Tonegawa lab 2014-2020 (Liu, Ramirez, et al; multiple Nature/Cell papers) — memory engrams stored in distributed cortex; the engram is a sparse population code that can be optogenetically reactivated to evoke the original memory. Engrams are BOTH content (the memory's sensory features) AND functional pointers (their connectivity profile determines what gets activated next).

**Substrate-native mapping:** cortex schemas = engram-like sparse population codes. Each schema has BOTH content (W_value: what gets retrieved) AND function (W_key: which PFC context activates it; what schema is "next" in a chain via its lateral connectivity to other schemas). This dual role (data + function) is THE key insight — operators ARE engrams; engrams ARE both content and function-pointers.

### B.5 — Glascher 2010 PFC vs basal ganglia model-based vs model-free

**Mechanism (lit anchor):** Glascher, Daw, Dayan, O'Doherty 2010 (Neuron) — fMRI shows PFC encodes a model-based value signal (forward-planning that uses an explicit world-model) vs basal ganglia which encodes model-free TD value. The model-based PFC signal IS the substrate of "schema-driven planning" — and the schemas it uses are cortex schemas (representations of the world's structure).

**Substrate analog:** "model-based" computation = PFC-driven multi-hop where each step's operator is selected from cortex schemas based on what the world-model predicts. "Model-free" = direct cached cortex-to-cortex association (skip the PFC step). Both should exist in substrate; PFC-routed-cortex is the model-based path.

### B.6 — Hierarchical attention + working-memory priming

**Mechanism (lit anchor):** brain doesn't search over millions of cortex schemas at each step. Working memory (PFC dlPFC) PRIMES a small relevant subset (~7±2 items per Miller 1956 + more recent ~4 per Cowan 2010); attention (parietal/PFC) further narrows; final selection is fast because the search space was pre-narrowed.

**Substrate-native mapping:** TWO-STAGE routing — first stage uses a coarse PFC pre-filter to select a small candidate set of cortex schemas (~10-50 of thousands); second stage does fine attention/cosine-argmax over the pre-filtered set. This is computationally efficient AND brain-aligned.

### ANGLE B — concrete mechanism proposals (3)

| # | Proposal | Mechanism in 1 line | Fairness considerations |
|---|---|---|---|
| **B-Prop-1** | **PFC-context-vector multiplicative gating of cortex (Mante-2013 substrate analog)** | At hop h, PFC emits `c_h`; cortex schemas modulated by `cortex_active = cortex_bank ⊙ c_h`; cleanup picks among modulated schemas | (a) `c_h` parameter count = separate-bank's operator count × N — keep budget matched by low-rank `c_h = U @ rank_k_proj` with k=4 to match 4-operator-bank's parameter count; (b) discriminator: per-hop gating pattern must vary (silent gating ≡ no operator selection); (c) regime check: at substrate N≥8192, gating noise floor must be below cortex-schema signal — measure SNR pre-cell |
| **B-Prop-2** | **PFC-emits-context, biased-competition argmax over cortex (Miller-Cohen 2001 substrate analog)** | At hop h, PFC emits `c_h`; biased cortex similarity `sim_i = (state_h · cortex_keys_i) · sigmoid(c_h · cortex_keys_i)`; pick `s* = argmax_i sim_i` | (a) shared-W: cortex_keys serve both state-similarity AND PFC-bias roles; (b) operator count = TOP-K cortex schemas matched to 4 if equal-baseline test; (c) verify-fire: log argmax per hop, check distribution NOT uniform |
| **B-Prop-3** | **Two-stage WM-prime + attention-select (hierarchical brain analog)** | Stage 1: PFC emits coarse-context that pre-narrows cortex bank to top-K candidates (K=10-50); Stage 2: fine attention over candidates picks operator | (a) Stage 1 must use a SEPARATE projection than Stage 2 (not just one projection split in two — that's not two-stage); (b) ablate Stage 1 by setting K=|cortex| (collapses to one-stage); discriminator if two-stage > one-stage by ≥0.05; (c) operator-count fairness: at K=4, exactly matches separate-bank baseline; sweep K |

### ANGLE B P-estimate

- Raw P (≥1 of B-Prop-1/2/3 lifts compositional reasoning ≥ 0.10 over separate-bank baseline): **0.65** (Mante-2013 is direct empirical evidence; Miller-Cohen is the foundational theory; Tonegawa engrams give molecular substrate).
- Lit-scan deflation: **-0.15** (brain-grounded mechanisms get smaller deflation per [[feedback-brain-is-existence-proof]]).
- Brain-existence bump: **+0.10** (earned — Mante-2013 is direct empirical evidence for the mechanism).
- Novel-synthesis cap doesn't bind (Mante-2013 IS the mechanism; only substrate-port is novel).
- **B-angle P_deflated = 0.50.**

---

## TOP-2 PICKS ACROSS BOTH ANGLES

### TOP-1: B-Prop-1 = A-Prop-2 — PFC-context multiplicative gating of cortex (Mante-2013 substrate analog)

**P_deflated: 0.45.** This is the convergence of Angle A (MoE shared-expert via multiplicative modulation; mathematically clean) and Angle B (Mante-2013 strongest empirical brain prior). Both angles independently nominate this; that convergence raises confidence.

**Falsifiable discriminator (concrete numbers, pre-registered):**
- Baseline: `pfc_controller_per_step_operator_select_v1` separate-operator-bank arm at compositional-reasoning accuracy `acc_sep_bank`. (Use whatever Wave 1 measured; if not yet landed, pre-reg uses smoke estimate.)
- Test arm: cortex-as-operator with Mante-2013 multiplicative gating; PFC emits `c_h` of dimension N (matching cortex-bank dim); cortex modulated = `cortex_bank ⊙ c_h`; cleanup proceeds within modulated bank; operator-count restricted to **K=4 cortex schemas (the 4 closest to `c_h`)** to match separate-bank's operator-count.
- **HARD_PASS:** `acc_cortex_as_op` ≥ `acc_sep_bank` + 0.10 across 5 seeds (cv ≤ 0.08); AND per-hop gating-pattern entropy ≥ 1.5 bits (proves gating actually varies); AND cone-cosine of `cortex ⊙ c_h` to original cortex ≤ 0.95 (proves modulation is non-trivial).
- **HARD_FAIL:** `acc_cortex_as_op` ≤ `acc_sep_bank` + 0.02 (no meaningful lift) — refutes the cortex-as-operator-via-multiplicative-gating hypothesis at this substrate regime.
- **By-construction-saturation guard:** if `acc_cortex_as_op` returns ≥ 0.95 absolute, trigger Q-discipline check — verify discriminator FIRED, log per-hop operator choices, check that DIFFERENT operators are picked at different hops (not just same one repeatedly). If single-operator-always = TRUE, mechanism is by-construction, NOT chain-grade.
- **Operator-count fairness sweep:** also run with K=4,8,16 cortex-schemas-as-operators; if K=4 matches separate-bank but K=16 wins by 0.20, the lift is from "more operators" not from "operators-in-cortex"; pre-register: chain-grade claim ONLY at K=4 (equal count).

### TOP-2: B-Prop-2 — Biased-competition argmax (Miller-Cohen substrate analog)

**P_deflated: 0.35.** Hard-argmax variant; testably distinct from TOP-1 (which is soft); foundational Miller-Cohen 2001 theory; substrate-feasible with existing primitives.

**Falsifiable discriminator (concrete numbers, pre-registered):**
- Baseline: same `acc_sep_bank`.
- Test arm: biased-competition cortex-as-operator; per-hop `sim_i = (state_h · cortex_keys_i) · sigmoid(c_h · cortex_keys_i)`; `s* = argmax_i sim_i` from TOP-K=4 cortex schemas.
- **HARD_PASS:** `acc_cortex_argmax` ≥ `acc_sep_bank` + 0.10 across 5 seeds (cv ≤ 0.08); AND per-hop argmax distribution covers ≥ 3 distinct schemas (proves competition fires).
- **HARD_FAIL:** `acc_cortex_argmax` ≤ `acc_sep_bank` + 0.02; OR per-hop argmax collapses to 1 schema always (mechanism degenerate).
- **Discrimination from TOP-1:** if both HARD_PASS and TOP-1 - TOP-2 ≥ 0.05, soft-gating outperforms hard-argmax (Mante-2013 winning); if difference ≤ 0.02, they are equivalent; pre-register: choose by simplicity (TOP-2 hard-argmax has fewer continuous parameters to tune).

---

## CRITICAL FAIRNESS DISCIPLINE (per USER directive "very careful that it's a fair experiment")

The cortex-closure agent's `cortex_as_router_v1` must satisfy ALL of the following or it tests something other than the intended mechanism. These are NOT optional — each catches a specific by-construction-saturation pattern I've personally violated:

1. **By-construction risk #1 (renamed-atoms):** if cortex schemas are JUST renamed copies of operator-bank atoms, the cell trivially works — operators are just renamed atoms. **Guard:** verify cortex schemas were extracted by schema-integration cell from CONTENT (not seeded from operator templates). Provenance check pre-tier: each cortex schema atom must trace to a content-extraction event in schema-integration's metrics.

2. **By-construction risk #2 (operator-count inflation):** if cortex variant uses 100 schemas vs separate-bank's 4 operators, capacity differs; lift could be from capacity not architecture. **Guard:** chain-grade-eligible claim ONLY at K=4 cortex-schemas-as-operators matching the 4-operator-bank baseline. Sweep K=4,8,16 as a SEPARATE arm to isolate "operators-in-cortex" from "more operators help."

3. **By-construction risk #3 (PFC parameter inflation):** if PFC's `c_h` projection has 100x more parameters than the separate-bank arm's PFC controller, lift could be from PFC capacity. **Guard:** match parameter count by low-rank `c_h = U @ z_h` with rank-k chosen so `params(c_h) ≈ params(separate-bank PFC controller)`.

4. **Shared-W discipline:** cortex bank and operator bank MUST be same RANK, same DTYPE (complex64 for FHRR), same N_DIM. The ONLY difference between baseline and test arm is whether the operator-source is shared with cortex or separate.

5. **Verify-the-referent ROUTING (not STORAGE):** the discriminator must test that operators are SELECTED PER HOP based on state (the routing question), NOT just that cortex stores something. **Concrete test:** if per-hop selection is always the SAME schema (regardless of state), the test only measured "cortex stores correctly" — fail with reason "discriminator did not fire routing condition." Pre-reg: per-hop operator-selection entropy ≥ 1.5 bits across the test set.

6. **META_RULE_K (smoke must FIRE discriminator):** smoke at small-N must demonstrate (a) cortex schemas are picked, (b) DIFFERENT schemas are picked at different hops based on different states. If smoke shows always-same-schema, reject full dispatch — the mechanism didn't fire even at small scale.

7. **Discriminator-survives-scale (per [[feedback-discriminator-must-survive-scale]]):** smoke at N=1024 must include a full-N=8192 preview arm showing baseline acc ≤ 0.50 of mechanism at full-N preview. Without this, full dispatch is gambling.

8. **Q-discipline (suspect 1.000):** if any arm returns absolute accuracy ≥ 0.95, trigger by-construction investigation BEFORE classifying as HARD_PASS. Real compositional-reasoning at substrate N=8192 with 4 operators should NOT saturate; if it does, something is contaminating.

9. **CARDINALITY_OK per [[feedback-cardinality-ok-mandatory]]:** pre-reg EXPECTED_N_UNITS for operator-selection events = N_test_chains × N_hops; HARD_FAIL_CARDINALITY_BREACH if observed selection-events < 0.9 × expected (silent-drop signal).

10. **BIAS-7 contamination (per BIAS master checklist):** the chains used at test-time MUST NOT be the same chains used to extract the cortex schemas via schema-integration — otherwise it's a memorization test, not a compositional-reasoning test. Pre-reg: held-out chain test set, distinct from schema-extraction training set.

---

## RELATION TO CORTEX-CLOSURE AGENT'S IN-FLIGHT CELL

The cortex-closure agent is authoring `cortex_as_router_v1`. My TOP-2 picks (multiplicative-gating soft variant; biased-competition hard-argmax variant) may overlap with their design — that's fine. My role here is:

(a) **Independent verification:** my drill independently nominates Mante-2013-multiplicative-gating from BOTH math (MoE shared-expert) and brain (PFC contextual gating) angles. If the cortex-closure agent's cell uses this mechanism, P_deflated = 0.45 is the calibrated prior.

(b) **Alternative if their design differs:** if their cell uses argmax-over-cortex without multiplicative gating, my B-Prop-2 (biased-competition) is the brain-aligned hard-argmax variant; queue as Wave 2 follow-up.

(c) **Fairness pressure-test:** the 10 fairness disciplines above are the MUST-INCLUDE pre-reg fields. Skunkworks should vet against these before tiering. If the cortex-closure agent's design misses any, the cell is at risk of by-construction-saturation per [[feedback-fix28-recurring]].

(d) **Composition with Wave 1 PFC controller:** Wave 1's PFC-controller is the upstream component that emits `c_h`. Cortex-as-router consumes `c_h` and applies it to cortex bank. If Wave 1 PFC-controller HARD_FAIL, the cortex-as-router cell's upstream prerequisite is broken — pre-reg condition: cortex-as-router requires Wave 1 PFC-controller PASS to be meaningful.

---

## RISKS + WHAT WOULD FALSIFY THE WHOLE DESIGN

- **Risk 1 (mechanism degenerate):** if PFC's `c_h` collapses to a constant across hops (no actual context-switching), both TOP-1 and TOP-2 degrade to "cortex picks first schema always" — no compositional power. Falsifier: per-hop entropy of `c_h` ≥ 2.0 bits in smoke.
- **Risk 2 (cortex schemas are too narrow):** if schema-integration extracted only ~3 schemas (the brain has thousands), the cortex bank is too small to be a meaningful operator vocabulary. Falsifier: cortex bank size ≥ 20 schemas before this cell ships.
- **Risk 3 (substrate noise floor):** at N=8192, modulating cortex by `c_h` might push schemas below noise floor; cleanup fails. Falsifier: smoke at N=8192 with arm shows cleanup top-1 ≥ 0.70 on clean (non-modulated) cortex; if not, raise N to 16384.
- **Risk 4 (Wave 1 PFC controller doesn't fire):** if the upstream Wave 1 cell HARD_FAIL, this cell is meaningless. Pre-condition: Wave 1 PASS before cortex-as-router runs.

**Kill-switch:** if Wave 1 PFC-controller is in MIDDLE_BAND or HARD_FAIL, defer this cell until upstream fixed; do NOT dispatch into a broken stack.

---

## ESTIMATED WALL + ROUTING

- **Smoke:** 30 min laptop CPU at N=1024 with full-N=8192 preview arm (per [[feedback-discriminator-must-survive-scale]]).
- **Full:** 6-10 CPU-hr at N=8192, 5 seeds, both TOP-1 (soft-gating) + TOP-2 (biased-comp) arms in single 4-arm cell.
- **Routing:** spawn `hdi_orchestrator` for routing decision; expect remote_cpu (numpy-bound FHRR bind/cleanup is CPU-efficient; GPU underutilized per [[feedback-fix24]]).

---

## SOURCES

Sources:
- [An Integrative Theory of Prefrontal Cortex Function (Miller & Cohen 2001, Annu Rev Neurosci)](https://www.annualreviews.org/doi/10.1146/annurev.neuro.24.1.167)
- [Context-dependent computation by recurrent dynamics in prefrontal cortex (Mante, Sussillo, Shenoy, Newsome 2013, Nature)](https://www.nature.com/articles/nature12742)
- [Single neurons in the prefrontal cortex encode abstract rules (Wallis, Anderson, Miller 2001, Nature)](https://www.nature.com/articles/35082081)
- [States versus Rewards: Dissociable neural prediction error signals (Glascher, Daw, Dayan, O'Doherty 2010, Neuron)](https://www.cell.com/neuron/fulltext/S0896-6273(10)00287-1)
- [Optogenetic stimulation of a hippocampal engram activates fear memory recall (Liu, Ramirez, Tonegawa 2012, Nature)](https://www.nature.com/articles/nature11028)
- [Memory engram cells have come of age (Tonegawa, Pignatelli, Roy, Ryan 2015, Neuron)](https://www.cell.com/neuron/fulltext/S0896-6273(15)00640-5)
- [Switch Transformers: Scaling to Trillion Parameter Models (Fedus, Zoph, Shazeer 2021, arxiv 2101.03961)](https://arxiv.org/abs/2101.03961)
- [GShard: Scaling Giant Models with Conditional Computation (Lepikhin et al. 2020, arxiv 2006.16668)](https://arxiv.org/abs/2006.16668)
- [Neural Turing Machines / Differentiable Neural Computer (Graves et al. 2016, Nature)](https://www.nature.com/articles/nature20101)
- [Neural mechanisms of selective visual attention - biased competition (Desimone & Duncan 1995, Annu Rev Neurosci)](https://www.annualreviews.org/doi/10.1146/annurev.ne.18.030195.001205)
- [Capacity Analysis of Vector Symbolic Architectures (arxiv 2301.10352)](https://arxiv.org/abs/2301.10352)
- Internal: `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` (separate-pathway depth drill, prior)
- Internal: `notes/research_drill_brain_multihop_M1_schema_chunking_cortex_3x_2026-06-27.md` (schema-chunking complementary mechanism)

---

**End of drill.**

TOP-1 P_deflated = 0.45 (Mante-2013 multiplicative gating — both math+brain convergence); TOP-2 P_deflated = 0.35 (Miller-Cohen biased-competition argmax). Both ≥ chain-grade-eligible probability range. 10-point fairness discipline is MUST-INCLUDE pre-reg for any cell using cortex-as-operator framing.
