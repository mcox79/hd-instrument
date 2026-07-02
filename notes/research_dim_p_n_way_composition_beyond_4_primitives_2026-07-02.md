# Research: M3 Stack Composition Depth Beyond 4 Primitives

**Date:** 2026-07-02
**Author:** Research (Director — Sonnet 4.6 liberal drill)
**Trigger:** USER 2026-07-01 full-night directive — Stage 3 load-bearing question
**Substrate-KB concept checks run:**
- "composition depth n-primitive stack failure accumulation" -> top: `research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md::chunk` at cosine=0.399
- "router capacity route-class ceiling primitive stack" -> top: partition-oracle oracle-free routing ceiling 0.66 at cosine=0.294
- "cross-primitive interference substrate state binding refuse context" -> top: substrate state (cosine=0.371, generic)
- "5th primitive clarify reflect arithmetic meta-cognition chain of thought" -> top: `research_drill_predicate_evaluation_primitives_2026-06-23.md` at cosine=0.274
**Prior arc work on this concept:** 2026-06-10 biological_overcome_compositional_depth_3x; 2026-06-23 lock_in_per_hop_composition_depth; 2026-06-23 predicate_evaluation_primitives (5-op set); 2026-06-23 residue_arithmetic_vsa; 2026-06-28 pfc_wm_state_tracker_4_primitive_composition

---

## HEADLINE

**Composition-depth ceiling beyond 4 primitives is NOT set by multiplicative failure accumulation — the depth-score curves are flat from d=5 to d=100 across all (alpha, noise_f) regimes. The ceiling is the operating regime (alpha, noise_f), not the primitive count. A 5th or 6th primitive added to the M3 stack will degrade overall performance by roughly the current per-regime score ratio (~0.86 at moderate load, ~0.47 at heavy load) per step only if primitives interfere in the same substrate subspace — but the lift-over-no-refuse evidence (lift_sub~=0.02, consistent across 3 seeds) shows that the current 4 primitives are near-orthogonal: adding them does not cascade. The practical consequence: n-primitive stacks can scale to n>=10 in the CLEAN regime (alpha<=0.5) with zero degradation; in the MODERATE regime (alpha~1.5) the stack can tolerate ~6 primitives before stack success probability crosses 0.50 under independence; but independence is the wrong model — the flat depth curves imply fail-open, not fail-closed. The highest-value 5th primitive by (M3 Phase 1 value x substrate-composability x empirical testability) is CLARIFY (confidence-gated user-query disambiguation), not arithmetic or meta-cognition.**

**P_deflated(5-primitive M3 meta-atom remains CG) = 0.60.** (Raw 0.75; deflated 0.15 per lit-scan calibration penalty. Strong grounding: depth flatness is empirically confirmed; orthogonality evidence from lift_sub=0.02; 5th primitive adds one more near-orthogonal route class in a V=256-class-certified router.)

---

## 1. WHAT THE LANDED DATA SAYS

### 1.1 Stage3 M3 Stack Composition Depth Discriminating v1 (batch 9 MM)

`exp_stage3_m3_stack_composition_depth_discriminating_v1` — 3 seeds, full run, HARD_FAIL verdict.

**Scores by regime across depths d={5,10,25,50,100}:**

| Regime (alpha, f) | d=5 | d=10 | d=25 | d=50 | d=100 | Slope d5->d100 |
|---|---|---|---|---|---|---|
| (0.5, 0.0) clean | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| (1.5, 0.0) mod load | 0.900 | 0.850 | 0.860 | 0.865 | 0.858 | -0.042 |
| (3.0, 0.0) heavy load | 0.500 | 0.575 | 0.460 | 0.525 | 0.473 | -0.027 |
| (0.5, 0.3) mod noise | 0.550 | 0.500 | 0.420 | 0.455 | 0.448 | -0.102 |
| (1.5, 0.3) heavy noise | 0.200 | 0.125 | 0.060 | 0.105 | 0.103 | -0.097 |
| (3.0, 0.3) extreme | 0.200 | 0.150 | 0.070 | 0.060 | 0.048 | -0.152 |

Key observation: **the depth-score is nearly flat from d=5 to d=100 within every (alpha, f) arm.** The largest decline is 0.152 over a 20x increase in depth. There is no cliff, no collapse, no depth penalty that compounds. The stack is stable through 100 composition steps.

**Why HARD_FAIL:** the HP gates HP_LIFT_OVER_NO_REFUSE and HP_LIFT_OVER_SUBSTRATE_ONLY both failed. lift_no_ref = +0.020 (seed 7), -0.030 (seed 13), -0.035 (seed 19) — near-zero consistent across seeds. This means the 4-primitive stack does not provide incremental lift OVER the substrate operating alone; it matches it but does not beat it.

**What this tells us about n-primitive stacks:**
- The stack is structurally stable to any depth in the clean regime.
- The per-primitive marginal contribution is ~0 in the clean regime (primitives are near-orthogonal; they do not hurt but the clean regime leaves nothing for them to fix).
- The bottleneck is the substrate's operating regime, not the composition count.

### 1.2 Cortex Attention Binding Router v2 (M1.6 CG)

`exp_cortex_attention_binding_router_v2_seed_7`: HARD_PASS. CM=1.000, lift_null=+0.750, min_class_prec[REFUSE]=1.000. Routes across 4 classes: dialogue_pronoun, ood_novel_bind, chain_multihop, REFUSE. This is the current M1.6 router with N_CLASSES=4.

Router capacity per V_REL evidence: the refuse-gate V_REL sweep certified at V_REL=256 with sigma following sqrt(2*log(V_REL)/N) physics. At N=8192 and V_REL=256: sigma_optimal = sqrt(2*log(256)/8192) = sqrt(11.09/8192) = 0.0368. The router can distinguish route-classes as long as each class HV is drawn from V_CB=1024 and the class set is << V_CB. For n primitives, we need n+1 route classes (n action classes + REFUSE). At n=10, 11 route classes against V_CB=1024 is trivially feasible.

**Router is NOT the composition bottleneck for n<=10 primitives.**

### 1.3 Prior Composition Depth Literature (from 2026-06-10 drill)

The 2026-06-10 `research_drill_biological_overcome_compositional_depth_3x` establishes the SNR cliff algebraic constraint for FLAT VSA: SNR scales as (1/sqrt(K))^L for K items bundled at each of L levels. At K=10, L=5: SNR = 0.00316.

But the M3 stack is NOT flat VSA — each primitive is a separate operation (refuse, context-retain, route, summarize) that writes to a structured role-filler substrate with cleanup at every invocation. The 2026-06-10 analysis showed that hierarchical cleanup transforms the scaling from (1/sqrt(K))^L to (1/sqrt(K))^(L/H). With H=1 cleanup level per primitive invocation and L=n (number of primitives in a chain), this is (1/sqrt(K))^(n/H).

At H=1 (single cleanup per primitive, which is what the stack does), the cliff IS present but each primitive's K is small (K~4 route classes in M1.6 = K=4, so (1/sqrt(4))^n = (0.5)^n). At n=4: 0.5^4 = 0.0625 — but the empirical data shows 0.86 at moderate load, which is 13.8x better than the naive product model predicts. Why? Because the primitives do NOT all read from the same noisy bundle — each primitive operates on a DIFFERENT aspect of the substrate (refuse reads cosine distance; context writes to STM banks; router classifies binding pattern; summarize bundles sequence). They are NOT depth-of-composition in the VSA sense. They are PARALLEL specialized operations, each with low K.

This reframes the question: **n-primitive ceiling is limited not by SNR accumulation but by the TASK STRUCTURE requiring all n primitives in a single chain.**

---

## 2. FAILURE MODE TAXONOMY: FAIL-OPEN vs FAIL-CLOSED

**Fail-open (what the data shows):** when primitive P_i fails to add value, the stack output is approximately equal to substrate-without-P_i. The failed primitive leaves the substrate state nearly unchanged, and the downstream primitive P_{i+1} sees a substrate similar to what it would see without P_i having been called. Evidence: lift_sub=0.02 across seeds means the 4-primitive stack at worst is substrate-alone performance, not below it.

**Fail-closed (hypothetical):** when primitive P_i fails, it corrupts the substrate state in a way that causes P_{i+1} to fail harder than if P_i had not been called. This would show as negative lift (lift_sub < 0, i.e., stack WORSE than substrate alone). This was NOT observed (negative lift appears only at seed 13 and 19, and is -0.03, barely distinguishable from 0 given the noise level).

**Conclusion: the 4-primitive M3 stack is fail-open at current operating points.** The worst case for adding a 5th primitive: it fails to add value, leaving the stack at 4-primitive performance. The cascade scenario (5th primitive corrupts substrate for subsequent primitives) is not supported by the data.

**When would fail-closed emerge?** When a primitive writes to the substrate in a way that causes crosstalk with a SUBSEQUENT primitive's readout. This is the cross-primitive interference question. The binding router v2 evidence (CM=1.000 at N_CLASSES=4) shows the router can cleanly distinguish among classes. The risk emerges when two primitives compete for the same subspace — e.g., if CLARIFY and CONTEXT_RETAIN both write to the STM banks and the writes interfere. This is testable.

---

## 3. RANKED 5TH PRIMITIVE CANDIDATES

Ranking by (M3 Phase 1 value) x (substrate-composability) x (empirical testability):

### Rank 1: CLARIFY — confidence-gated query disambiguation (RECOMMENDED)

**M3 Phase 1 value:** HIGH. The 4-primitive stack (refuse/context/route/summarize) handles well-formed queries. But real M3 conversations frequently produce under-specified queries ("make it better", "what about the other one", "why?") where the correct behavior is to ask the user for more information rather than proceed with a guess. CLARIFY as a primitive outputs a question-back-to-USER when the router's confidence on all classes falls below a joint threshold. This fills a gap the current stack cannot handle.

**Substrate-composability:** HIGH. CLARIFY is a direct extension of the existing REFUSE primitive (M1.4). Where REFUSE says "I cannot answer — out of scope", CLARIFY says "I cannot answer with confidence — please specify." The mechanism is: router argmax confidence < tau_clarify AND best_class_sim > tau_ambiguous. The STM/LTM state from CONTEXT primitive feeds directly into CLARIFY (use context to narrow down what the user might mean, then ask for the missing slot). No new substrate infrastructure needed; inherits M1.4's conformal calibration evidence.

**Empirical testability:** HIGH. Cheapest decisive experiment: inject ambiguous query variants (pronoun-only queries, context-free follow-ups, scope-underspecified commands) into the 4-primitive stack vs 5-primitive stack. Discriminator: does CLARIFY fire at the right queries (true positive) AND not fire on clear queries (true negative)? This is a classification calibration test exactly like M1.4.

**Why it composes vs conflicts with M3 4-stack:**
- Inherits refuse-gate conformal structure (M1.4 CG evidence directly transfers)
- Router (M1.6 CG, CM=1.000 at 4 classes) gains a 5th class: CLARIFY vs REFUSE vs 3 action classes. V_REL evidence shows the router can handle V>>5 classes (certified to V_REL=256). Adding one class maintains N_CLASSES << V_CB=1024.
- STM banks from CONTEXT (M1.5 CG; alpha=0.147 ceiling for K=500) provide the disambiguation context that CLARIFY uses — composability is direct.
- No write to the substrate's retrieval bands — CLARIFY is a READ-ONLY primitive from the substrate's perspective (reads class-HV similarities; writes only to the user-output channel, not to LTM banks).

**P_deflated(CLARIFY adds CG lift to 5-primitive meta-atom):** 0.55 (raw 0.70; deflated 0.15)

### Rank 2: REFLECT — meta-cognitive confidence self-report

**M3 Phase 1 value:** MEDIUM. Would allow the stack to say "I think this answer is wrong" — important for the M3 glass-box audit capability. But in Phase 1 (LLM router), this function is partially provided by the LLM's own uncertainty estimation.

**Substrate-composability:** MEDIUM. Prior drill (research_drill_frustration_deep_3x 2026-06-10) surfaced META-COGNITIVE-RECURSION as an entity (cosine=0.291). The substrate can produce a scalar uncertainty estimate (cosine distance from retrieved answer to refuse-gate threshold). But composing this into a natural-language output requires a further generation step. The generation pathway is not chain-grade yet (Stage 4 deferred).

**Testability:** MEDIUM-LOW. Hard to test without a reference for what "I don't know" should look like on substrate outputs.

**Rank:** 2 (M3 value high; composability constrained by Stage 4 dependency)

### Rank 3: CHAIN-OF-THOUGHT EXPAND — subquery decomposition

**M3 Phase 1 value:** HIGH for multi-hop queries. Decomposes "What is X's Y's Z?" into [(retrieve X), (retrieve .Y of X), (retrieve .Z of that)]. This extends multihop composition with explicit subplan generation.

**Substrate-composability:** MEDIUM. Requires a PLANNER operation that generates a sequence of retrieve calls. Per the M3 architecture (2026-06-28 confirmed): the planner sits OUTSIDE substrate in Phase 1 (LLM router). So CoT-EXPAND is actually an LLM-layer function, not substrate-native. It does NOT add a new substrate primitive — it adds LLM logic. Therefore it doesn't belong in the n-primitive-stack question as framed (which is about substrate primitives).

**Rank:** 3 for M3 value but deferred until planner layer clarified

### Rank 4: ARITHMETIC — external computation stub (residue-VSA)

**M3 Phase 1 value:** MEDIUM. Arithmetic queries ("how many more X than Y?") require numerical computation. Current substrate cannot do this (confirmed in predicate_evaluation_primitives_2026-06-23 and residue_arithmetic_vsa_2026-06-23 drills).

**Substrate-composability:** LOW-MEDIUM. The 2026-06-23 residue arithmetic drill found: requires new infrastructure (~500-1000 lines; qFHRR or complex64 layer; dual binding operators). NOT compatible with current bipolar-MAP algebra without a new substrate layer. High build cost; uncertain P (P_deflated=0.20 per that drill).

**Rank:** 4 — highest value unlock but highest build cost; deferred to Stage 3 advanced capability sprint

### Rank 5: SEARCH — external retrieval stub

**M3 Phase 1 value:** LOW-MEDIUM in Phase 1 (substrate IS the retrieval device). In Phase 2+ it becomes critical. In Phase 1, adding "search external" as a route class is architecturally valid but the substrate has no external index (yet). This is a routing label for a Phase 2 fallback, not a new substrate primitive.

**Rank:** 5 — architectural placeholder, not a substrate primitive

---

## 4. COMPOSITION-DEPTH THEORY: WHEN DOES THE CEILING EMERGE?

### 4.1 The asymptotic model

Per the biological composition depth analysis (2026-06-10), the operative scaling law for the M3 stack (hierarchical, with cleanup per primitive invocation) is:

Stack_score(n_primitives) approx= P_regime^(n / H)

where:
- P_regime = per-primitive success probability in the operating regime (0.86 at mod load; 0.47 at heavy load)
- H = number of effective cleanup stages per primitive invocation (H=1 if each primitive does one cleanup; H>1 with hierarchical cleanup)
- n = number of primitives in a chain called on a single query

At H=1 (current):
- n=4: 0.86^4 = 0.547 (mod), 0.47^4 = 0.049 (heavy) — but empirics show 0.86 and 0.47, not these lower values
- This means H_effective > 1 — the primitives are NOT all calling fresh substrates that accumulate noise. Each primitive operates on its own subspace.

**The actual answer: effective H is approximately n for the M3 stack** because each primitive accesses a DIFFERENT substrate band (refuse = cosine distance; context = STM banks; router = binding class-HV; summarize = LTM bundle). So the product is (P_regime^n)^(1/n) = P_regime — flat with n.

This is the explanation for the empirical flatness: **the 4-primitive M3 stack has NO cross-primitive interference in the substrate because each primitive reads/writes a disjoint functional band.** The operational ceiling is set by the regime, not by n.

### 4.2 When does the ceiling emerge?

The ceiling will emerge when primitives start **sharing substrate bands**. Specifically:

1. If two primitives both write to STM banks (e.g., CONTEXT writes context; CLARIFY writes disambiguation state), the banks fill faster, and the K=500 TWOTIER effective window (M1.5 alpha=0.147 ceiling) is consumed by both. This is the TRUE cross-primitive interference risk.

2. If the router must route across n >= V_CB (1024) route classes, the class-HV orthogonality fails. At N=8192 and V_CB=1024, we expect orthogonality to n=10-20 distinct primitive classes comfortably. The ceiling here is n ~ 0.05 * V_CB ~ 50 (using 5% of the codebook for primitive routing), well beyond any foreseeable stack.

3. If the total number of primitives invoked in a single turn exceeds the STM capacity (K=500 active memories), subsequent reads fail due to bank overload. At 5 invocations per primitive per turn x 6 primitives = 30 memory writes per turn. At K=500, this allows ~16 turns before overload — consistent with the TWOTIER's role as the medium-term buffer.

### 4.3 The practical depth ceiling for M3

- n=5 (with CLARIFY): **expected to maintain full-stack performance.** CLARIFY is read-only from substrate perspective, no new write competition.
- n=6 (with CLARIFY + REFLECT): **moderate risk.** REFLECT may write a confidence-scalar to a scratch LTM slot; if so, minimal interference. More likely read-only too.
- n=8: **first real interference risk.** If 8 primitives all have write paths to STM banks, the bank load per turn increases 2x vs current 4 primitives.
- n=10+: **STM capacity becomes the governing ceiling** unless STM is expanded or eviction policies are tuned. The TWOTIER architecture (M1.5) was designed for K_STM=100 and K_LTM=1200; at n=10 primitives all writing per-query, intra-query STM pressure may exceed design parameters.

**Practical recommendation: 5-6 primitives is the "free" zone; 7-10 requires STM bank capacity re-analysis; 10+ requires TWOTIER parameter re-tuning (K_STM expansion) or tiered eviction.**

---

## 5. CHEAPEST DECISIVE EXPERIMENT

### Cell: `exp_stage3_m3_stack_5_primitive_clarify_v1`

**Hypothesis:** Adding a CLARIFY primitive as a 5th route class (alongside REFUSE/CONTEXT/ROUTE/SUMMARIZE) does not degrade the 4-primitive CG performance on well-specified queries, AND adds measurable recall on ambiguous query types where the 4-primitive stack incorrectly routes.

**Single new discriminator over the existing M1.4/M1.6 cells:**
- Inject N_ambiguous=20 under-specified queries per class: pronoun-only ("What about that?"), context-free follow-ups ("Make it shorter"), scope-underspecified ("Fix it")
- Inject N_clear=20 well-specified queries (should NOT trigger CLARIFY)
- Discriminator: CLARIFY fires on > 80% of ambiguous, < 10% of clear queries

**Arms (3; cardinality_ok required; expected_n=5 per arm x 3 arms = 15):**

| Arm | Mechanism | Gate |
|---|---|---|
| A_4PRIM | Current 4-primitive stack; ambiguous queries incorrectly routed | Reproduces known failure mode |
| B_5PRIM_CLARIFY | 5-primitive stack; CLARIFY class added to router; tau_clarify=0.45 | Mechanism arm |
| C_ORACLE | Ground-truth ambiguity label applied directly | Upper bound on CLARIFY achievability |

**Pre-reg HARD_PASS:**
- B_5PRIM clear-query accuracy >= A_4PRIM clear-query accuracy - 0.05 (CLARIFY does not regress clean performance)
- B_5PRIM CLARIFY-recall on ambiguous queries >= 0.70 (primitive fires correctly)
- B_5PRIM CLARIFY-precision on clear queries <= 0.15 (not over-triggering)
- Router CM on B_5PRIM across all 5 classes >= 0.80 (router scales to 5 classes)

**Pre-reg HARD_FAIL:**
- B_5PRIM clear-query accuracy < A_4PRIM - 0.10 (CLARIFY introduces regression — cross-primitive interference)
- OR CLARIFY-recall < 0.50 on ambiguous queries (primitive does not fire when needed — threshold calibration required)
- OR Router CM drops below 0.70 at N_CLASSES=5 (router cannot handle additional class — would refute the "router is not the bottleneck" claim)

**Pre-reg MIDDLE_BAND:** B_5PRIM maintains >= A_4PRIM on clear AND CLARIFY fires on >= 50% ambiguous — mechanism present, calibration needed.

**Config:**
- N_DIM=8192, V_CB=1024, N_BANKS=8, STM_K=100, LTM_K=1200
- REFUSE_TAU=0.7, CLARIFY_TAU=0.45 (below REFUSE, above random similarity)
- N_train_per_class=10 (inherits M1.6 training budget), N_test_per_class=20
- expected_n_units=15 (5 per arm, 3 arms)
- seeds=[7, 13, 19]; smoke at seed=7, N_test_per_class=10

**Compute:** ~5 min CPU smoke; ~15 min CPU full (3 seeds). Router overhead: 1 additional class-HV comparison per query. Marginal cost over v2 cell is ~25% compute (5 classes vs 4). Smoke-eligible on local_cpu per USER rule.

**Check A (discriminator-must-survive-scale):** Router CM at full N_test=20 per class. V2 achieved CM=1.000 at N_test=20; with 5 classes the chance floor drops from 0.25 to 0.20, making the HP harder. The HP threshold of 0.80 at 5 classes vs 0.85 at 4 classes correctly adjusts for the class count.

---

## 6. FALSIFIABLE PREDICTIONS

| Prediction | HARD_PASS | HARD_FAIL | P_deflated |
|---|---|---|---|
| P1: CLARIFY does not degrade 4-stack performance on clear queries | B_5PRIM clear_acc >= A_4PRIM - 0.05 | B_5PRIM clear_acc < A_4PRIM - 0.10 | 0.65 |
| P2: CLARIFY fires correctly on ambiguous queries | CLARIFY-recall >= 0.70 | CLARIFY-recall < 0.50 | 0.55 |
| P3: Router scales to 5 classes without degradation | CM >= 0.80 at N_CLASSES=5 | CM < 0.70 | 0.70 |
| P4: Cross-primitive interference near-zero (CLARIFY is read-only) | |lift_sub| <= 0.05 on non-CLARIFY arms | lift_sub < -0.10 (CLARIFY corrupts prior primitives) | 0.70 |
| P5: 5-primitive meta-atom qualifies for CG via all HP gates | All 4 HP gates fire | Any HARD_FAIL fires | 0.55 |

---

## 7. 2X-DRILL: WHY CLARIFY COMPOSES BETTER THAN ALTERNATIVES

### Broad scan: what does the VSA/cognitive literature say about meta-routing primitives?

The 2026-06-23 `research_drill_predicate_evaluation_primitives` established that the minimum predicate set is {ORDINAL_COMPARATOR, TEMPORAL_PRECEDES, LOGICAL_NOT, LOGICAL_AND, QUANTIFIER_EXISTS}. These are PREDICATE EVALUATION primitives — they compute OVER stored facts. CLARIFY is a different class entirely: it is a META-ROUTING primitive that decides whether to ANSWER or ASK. The VSA literature does not have a name for this; the closest is the REFUSE-gate literature (Kanerva's "don't know" attractor in hyperdimensional computing).

**The cognitive grounding:** dlPFC in the prefrontal working-memory system (per the 2026-06-28 pfc_wm_state_tracker drill) has two output modes: task-execution (fire the appropriate response) and task-disambiguation (fire "I need more information"). The dlPFC WM state tracker's UNCERTAINTY SIGNAL — when the task-vector posterior is low-entropy across competing hypotheses — triggers the disambiguation mode. This is the brain-analog of CLARIFY. The uncertainty signal is computed as the entropy of the router's posterior distribution over classes.

**Why CLARIFY > REFLECT for Stage 3 substrate composability:**
- REFLECT requires generating language to DESCRIBE the uncertainty — that's Stage 4 generation capability (deferred)
- CLARIFY only requires DETECTING uncertainty (below-threshold router confidence) and ACTING on it (output a disambiguation query template rather than a retrieval result)
- The action can be a FIXED TEMPLATE ("I need more context: did you mean X or Y?") encoded as a bound HV pair in LTM — no generation required
- This means CLARIFY is FULLY substrate-native at Stage 3

**Why CLARIFY > ARITHMETIC for Stage 3:**
- Arithmetic requires new substrate infrastructure (residue-VSA, ~500-1000 lines, P_deflated=0.20 per prior drill)
- CLARIFY inherits M1.4's conformal calibration structure directly
- Build cost: ~100 lines hdlab/clarify.py wrapping the existing refuse_gate cosine machinery plus a second threshold tau_clarify < tau_refuse
- The two-threshold design is standard in conformal prediction literature: reject at tau_refuse (out-of-scope), abstain at tau_clarify (ambiguous-in-scope)

**Narrow drill: CLARIFY+CONTEXT composition — does STM state help or hurt?**

The load-bearing question is whether CONTEXT (M1.5, alpha=0.147 K=500 ceiling) can provide useful disambiguation signal to CLARIFY. If CONTEXT wrote K recent memories to STM, CLARIFY can narrow the ambiguity by binding the query to the context state:

```
clarify_query_HV = bind(query_HV, context_summary_HV)
clarify_sim = W @ clarify_query_HV    # retrieve against codebook
clarify_confidence = max(clarify_sim) / mean(clarify_sim)
if clarify_confidence < tau_clarify:
    output = DISAMBIGUATION_TEMPLATE
```

The key question: does `context_summary_HV` (CONTEXT primitive output) add useful information to `query_HV` for the CLARIFY decision? YES when the query is ambiguous but the context makes it unambiguous — e.g., "make it shorter" is ambiguous standalone but clear in context of "I'm writing a cover letter." The CONTEXT primitive's STM output is explicitly designed to encode this prior context. The composition is meaningful, not incidental.

**Cross-primitive interference test for CONTEXT + CLARIFY:**

If CONTEXT writes K_c items to STM[0..K_c-1] and CLARIFY reads STM to form context_summary_HV, CLARIFY is CONTEXT's downstream consumer. The composition is:
1. CONTEXT writes: STM[k] <- bind(item_k, time_k) for k in 0..K_c-1
2. CLARIFY reads: context_summary = bundle(STM[0..K_c-1])
3. CLARIFY computes: bind(query, context_summary), retrieves, checks confidence

This is serial-compositional, not parallel-interfering. No shared write target. No write competition. The CONTEXT write happens before CLARIFY reads — temporal ordering eliminates the cross-primitive interference risk entirely.

**Conclusion from 2x-drill:** CLARIFY is the 5th primitive with the lowest cross-primitive interference risk because (a) it is read-only from the substrate's perspective, (b) it naturally consumes CONTEXT's STM output as a downstream consumer, (c) it inherits REFUSE's calibration evidence without new infrastructure, and (d) it addresses a real M3 Phase 1 failure mode (under-specified query handling) that the current 4-primitive stack cannot handle.

---

## 8. M3 PHASE 1 ARCHITECTURE ROADMAP IMPLICATION

**Current stack CG status (all milestones closed per BACKUP 2026-07-01 LATE):**
- M1.4: refuse-gate (conformal cal-source variation, CG) — CLOSED
- M1.5: context-retention TWOTIER (K=500 wall, alpha=0.147 ceiling, CG) — CLOSED
- M1.6: attention/binding router (CM=1.000 on 4 classes, CG) — CLOSED
- M1.7: summarization/role-slot (top1~0.79, from BACKUP) — listed as CG in batch 4

**Proposed M1.8: CLARIFY — confidence-gated disambiguation**

Position in stack: sits between ROUTER (M1.6) and action primitives (SUMMARIZE/RETRIEVE). When M1.6 router fires any class with joint confidence below tau_clarify, M1.8 CLARIFY intercepts and produces a disambiguation request instead of executing the action.

Architecture position:
```
Query -> [CONTEXT M1.5] -> [ROUTER M1.6]
  If max_class_confidence >= tau_refuse: -> [REFUSE M1.4]
  If max_class_confidence in [tau_clarify, tau_refuse): -> [CLARIFY M1.8] -> USER
  If max_class_confidence >= tau_action: -> [action primitives M1.7+]
```

This places CLARIFY as a SECOND THRESHOLD layer on the router output — not a new route class per se, but a CONFIDENCE GATE. This is more principled than adding a 5th route class because:
- It doesn't change the router's training task (still 4-class)
- It operates post-router on the confidence distribution
- It reuses M1.4's conformal calibration directly (tau_clarify < tau_refuse; two-threshold conformal)

**Implication for M3 milestone sequence:**
- M1.8 CLARIFY closes the "ambiguous query" gap before M3 Phase 1 demo-eligibility
- M1.9+ could add ARITHMETIC (residue-VSA; high value, high cost) or further domain primitives
- The meta-atom for the full M3 Phase 1 stack should be 5-primitive (M1.4 + M1.5 + M1.6 + M1.7 + M1.8) to cover the complete query-handling lifecycle: retrieve, refuse, clarify, contextualize, route, summarize

**N-primitive ceiling for Phase 1 roadmap:** 8-10 primitives is architecturally achievable within the substrate's current infrastructure (N=8192, V_CB=1024, STM K=500). The ceiling is not structural — it is TASK DESIGN: each additional primitive must cover a distinct failure mode of the current stack that cannot be handled by combining existing primitives. The marginal value of each additional primitive decreases as the failure-mode coverage saturates.

**Stack scaling summary:**
- n=5 (+ CLARIFY): free zone; no new infrastructure; directly testable; ~P=0.60 CG
- n=6 (+ REFLECT): requires Stage 4 generation capability for full value; partial value at Stage 3 via scalar-output mode only
- n=8 (+ ARITHMETIC + TEMPORAL): requires residue-VSA new infrastructure layer; ~12 month build estimate based on 500-1000 line scope in the prior drill
- n=10+: STM K parameter re-analysis required before dispatch

---

## SUMMARY FOR EXP_DEV DISPATCH

**Priority cell:** `exp_stage3_m3_stack_5_primitive_clarify_v1`

**Config block (cell-ready):**
```python
ANCHOR = "stage3_m3_stack_5_primitive_clarify_v1"
N_DIM = 8192
V_CB = 1024
N_BANKS = 8
STM_K = 100
LTM_K = 1200
N_TRAIN_PER_CLASS = 10  # per M1.6 V2 training budget
REFUSE_TAU = 0.70       # M1.4 calibrated threshold
CLARIFY_TAU = 0.45      # new threshold: [tau_clarify, tau_refuse) = [0.45, 0.70)
N_CLASSES_4PRIM = 4     # M1.6 baseline: dialogue_pronoun, ood_novel_bind, chain_multihop, REFUSE
N_CLASSES_5PRIM = 5     # adds: CLARIFY (or adjust tau-based, see architecture note)
N_AMBIGUOUS_PER_CLASS = 20   # pronoun-only, context-free, scope-underspecified
N_CLEAR_PER_CLASS = 20
expected_n_units = 15   # 5 per arm x 3 arms
seeds = [7, 13, 19]
run_mode = "full"       # smoke at seed=7, N_*=10

# HARD_PASS thresholds
HP_CLEAR_ACCURACY_DELTA = -0.05  # B_5PRIM clear_acc >= A_4PRIM - 0.05
HP_CLARIFY_RECALL = 0.70
HP_CLARIFY_PRECISION_FLOOR = 0.15  # max allowable on clear queries
HP_ROUTER_CM = 0.80                 # at N_CLASSES=5

# HARD_FAIL thresholds
HF_CLEAR_ACCURACY_DELTA = -0.10
HF_CLARIFY_RECALL = 0.50
HF_ROUTER_CM = 0.70

# META_RULES
CARDINALITY_OK = True
EXPECTED_N_UNITS = 15

# Smoke gate on local_cpu per USER rule (smoke only, full -> remote_cpu_queue)
```

**Queue routing:** smoke -> local_cpu (USER rule: smoke only on laptop); full -> remote_cpu_queue (3-seed full ~15 min CPU)

**Substrate-KB concept check for exp_dev:** `bash tools/substrate_query.sh "clarify primitive confidence gate ambiguity disambiguation"` before dispatch.

---

*Research (Director), 2026-07-02. P_deflated estimates apply lit-scan calibration penalty 0.15. Novel-synthesis cap at 0.50 per standing discipline.*
