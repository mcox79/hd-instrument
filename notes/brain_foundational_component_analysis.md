# BRAIN-FOUNDATIONAL COMPONENT ANALYSIS — no-shortcuts pass (USER 2026-07-29)

Per-component: the FOUNDATIONAL brain mechanism | our impl | is it foundational? | PRIORS (what we tried, why it was wrong) | the SPECIFIC correction. Companion to component_brain_fidelity_ledger.md (this one adds the priors + the why-wrong + the coupled-core synthesis). Executes FORMALIZE (deep-brain -> compare -> accurate-duplicate) rigorously. Honest: most of the core is NOT foundational, and the priors failed for ONE recurring reason.

---

## THE CORE (the coupled machinery comprehension actually needs)

### 1. Encoder OBJECTIVE (the learning signal)
- **Foundational brain mechanism:** cortex learns SELF-SUPERVISED from the temporal stream via (a) FORWARD predictive coding (Rao-Ballard/Friston: predict next input from past, error drives learning), (b) temporal-contiguity / slow-feature (nearby-in-time = similar meaning; Foldiak/Wiskott), (c) error-driven local plasticity. It is CAUSAL, TEMPORAL, and predicts in a LEARNED LATENT space at higher levels (not just the raw input).
- **Our impl:** MLM = BIDIRECTIONAL masked cloze. Sees future to fill a blank. A fine representation learner; NOT the brain's forward-temporal prediction.
- **Foundational? NO (half).** Bidirectional != forward; single objective vs the brain's stacked predictive+contiguity.
- **PRIORS + why wrong:** (a) relObj = MLM + foundation-relational-InfoNCE -> HARD_FAIL both seeds. WHY: contrastive alignment to a symbolic KB graph is SUPERVISED DISTILLATION from a noisy teacher, not predictive coding. (b) full R3/R4 self-teacher (landmark-geometry + VICReg + relational-InfoNCE + EMA) -> tied grounding, no gain. WHY: a pastiche of SSL tricks aligned to graph structure — still not forward-temporal prediction. (c) earlier encoder-migration DISTILLED a BGE teacher -> HARD_FAIL + violated no-borrowed-vector. WHY: distilling a borrowed oracle isn't earning meaning. **The recurring error: every "objective" attempt aligned to a STATIC target (graph, BGE) instead of PREDICTING THE STREAM.**
- **CORRECTION:** FORWARD predictive coding — causal next-token/next-span prediction (v5 retrain, shipping now = the first faithful step). DEEPER (not yet done): predict the next LATENT state (JEPA/latent-PC), stack temporal-contiguity + hierarchical multi-timescale prediction. v5 tests the shallow (token) rung; latent-predictive is the fuller version.

### 2. Encoder ARCHITECTURE
- **Foundational brain mechanism:** cortex is RECURRENT (persistent state), SPARSE (k active), columnar/laminar, with TOP-DOWN PREDICTIVE FEEDBACK (predictions down, errors up) and MIXED SELECTIVITY. Recurrence => PERSISTENT STATE => working memory + iterative computation.
- **Our impl:** DENSE FEED-FORWARD transformer (6L). Attention ~ dynamic routing (loosely brain-like). But dense, feed-forward, NO recurrence, NO top-down predictive feedback.
- **Foundational? NO — and this is the deepest gap.** A feed-forward net computes a STATIC function of a fixed window. It CANNOT maintain/update state across a stream. This is WHY a situation model (maintained state) is architecturally impossible on it.
- **PRIORS + why wrong:** we mostly DEPRIORITIZED architecture ("mechanism!=task-analog", "nail baseline first"). We DID build brain-faithful LEARNING PRIMITIVES (Stage-2 spokes: competitive-Hebbian WTA, temporal-contiguity, DG-CA3 pattern-sep, predictive-coding competitive-allocation) — but ON SYNTHETIC, never wired into the encoding architecture. WHY wrong: we built the right primitives in isolation and left the actual encoder a vanilla feed-forward transformer.
- **CORRECTION:** add PERSISTENT STATE. Cheapest faithful route = an explicit stateful WORKING-MEMORY module (component 6) rather than rebuilding a recurrent transformer. Plus k-WTA sparsity (primitive exists). Architecture-fidelity is largely bought via the WM component — but be honest that the feed-forward transformer is a foundational un-faithfulness we've lived with.

### 6. WORKING MEMORY / active maintenance  (the absent structural piece — pairs with arch)
- **Foundational brain mechanism:** persistent-activity attractor WM (Wang) or activity-silent synaptic WM (Mongillo/Stokes); ~4 items (Cowan); UPDATED by prediction-error GATING (basal-ganglia gating of PFC WM — O'Reilly PBWM: learned gate decides what enters/updates WM). This IS the substrate of the situation model.
- **Our impl:** ABSENT. Flat 128-token window; the only "memory" is attention within the window. No persistent, updatable entity-state that spans the stream.
- **Foundational? NO — ABSENT. Likely THE structural block on comprehension.**
- **PRIORS + why wrong:** we BUILT a DG episodic store (hippocampal fast-write, used in loop v4) + sequence_memory (Hebbian ordered-pair) — but used them as EPISODIC STORES (write/retrieve facts), NEVER as an ACTIVE, LEARNED, PE-GATED maintenance of a situation model DURING reading. Design-A (entity-slot + write-gate) tried — HARD_FAIL_STRUCTURE_ALONE. WHY: it (i) bolted onto FROZEN encoder reps, (ii) compressed state to 3 SCALARS (threw away the signal), (iii) was tested on a structurally-solvable construction. loop v1-v6: no comprehension-specific gain — WHY: they tried to DECODE/extract from a stateless encoder that never CONSTRUCTED a situation model.
- **CORRECTION:** build a proper active-WM: small entity slots / recurrent state, written+updated by a LEARNED PE-driven gate (PBWM-style), PRESERVING dimensionality (no scalar compression), trained END-TO-END with the encoder (NOT on frozen reps — that was the design-A error), reusing DG/sequence_memory as the store substrate. This is the big hard build after v5.

### 8. BINDING (role-filler)
- **Foundational brain mechanism:** ROLE-GENERAL binding — AGENT/PATIENT slots invariant to surface position (Frankland-Greene lmSTC); fillers bound to roles (synchrony/attractor). VSA/HRR binding is the computational model.
- **Our impl:** we HAVE FHRR/HRR binding (hdlab/binding.py) — genuinely brain-inspired. But comprehension attempts used ABSOLUTE-POSITION binding.
- **Foundational? PARTIAL — right primitive, wired wrong.**
- **PRIORS + why wrong:** v5 position-bind readout -> FAILED (0.52 self-consistency: same concept binds inconsistently at different positions). WHY: bound by ABSOLUTE POSITION, but the brain (and our own probe) binds by CONTENT/ROLE. This exactly matches Frankland-Greene.
- **CORRECTION:** role-general (content-keyed) binding — bind fillers to entity-slots by a LEARNED role-key. Composes INTO the WM build (component 6). Binding is a piece of the stateful core, not standalone.

---

## THE SYNTHESIS — why the priors failed, and the real correction

**The core components above are COUPLED, and in the brain they are ONE system:** the brain comprehends by MAINTAINING AND UPDATING A PREDICTIVE LATENT STATE over a temporal stream — recurrence (arch) + forward prediction (objective) + working-memory maintenance (WM) + role-general binding, all trained together. 

**Our substrate is a FEED-FORWARD, BIDIRECTIONAL, STATELESS encoder. It is architecturally incapable of the core operation.** Comprehension (a maintained/updated situation model) cannot be DECODED out of it — because it was never CONSTRUCTED. Every downstream failure (comprehension, the read->learn loop) traces to this.

**THE RECURRING ERROR (the one why-wrong behind almost every prior):** we kept building ISOLATED pieces and BOLTING them onto a FROZEN, feed-forward encoder — a contrastive objective aligned to a static graph; a slot-memory compressing state to scalars on frozen reps; a position-bind readout; loop-extraction from a stateless bag-of-tokens. The brain's machinery is COUPLED and trained END-TO-END; we assembled frozen isolated parts. That is why it kept almost-working and then failing the controls.

**This also reframes the v5 forward-PC retrain (shipping now):** it fixes the OBJECTIVE (forward), which is necessary — but a causal-LM transformer is STILL feed-forward/stateless ("causal" only masks attention; it is not persistent recurrent state). So v5 tests "does a faithful objective help the representation" (worth knowing), but it does NOT add the stateful maintenance comprehension needs. Do NOT expect v5 alone to comprehend. The real build is next regardless of v5's outcome.

---

## THE DOWNSTREAM (adequate-or-subsumed; do NOT over-invest)
- **3. REPRESENTATION geometry:** earned/graded/generalizes (29591) = fairly foundational in PRINCIPLE, but MODEST (0.56-0.63) + ARC-narrow. Not independently fixable — downstream of objective(1)+arch(2)+data. Prior: 178k encoder-migration collapsed (objective didn't form graded geometry at scale). Correction routes through 1/2.
- **4. READOUT:** was fixed-cosine (un-faithful) -> learned bilinear (better). Prior: AttnBilinearReadout HARD_FAIL_STRUCTURE_ALONE (random-init matched — too powerful, exploited raw structure). LESSON: a readout can only decode what's there; if the encoder signal is weak a strong readout cheats. Correction: capacity-controlled learned readout is fine; readout is NOT the comprehension lever. Improving; stop over-investing (the easy-path trap).
- **7. GROUNDING:** sensorimotor for CONCRETE (Barsalou), relational for ABSTRACT (semantic net). Prior: sensorimotor applied to abstract -> HARD_FAIL_NO_TRANSFER (0.560 ~ chance on relational). WHY: sensorimotor carries perceptual not relational structure. Correction: abstract grounding is SUBSUMED by the relational objective (a concept grounded in its relational neighborhood); sensorimotor reserved for concrete + needs real multimodal input we lack. Deferred.
- **9. REASONING:** CA3 attractor / additive constraint-satisfaction = FOUNDATIONAL (banked, hdlab/reasoner.py). Prior: local decision-time reasoning exhausted -> composition lives in the REPRESENTATION. WHY: reasoning amplifies rep quality; weak reps cap it. Correction: improves when 1/2 improve; do not rebuild.
- **10. CONSOLIDATION:** iterated SWR replay + schema-gate + surprise-budget. Ours = single averaging op (wrong op-class). Prior: retrieve-not-average failed (same class); certified cls_discrete_budget ISLANDED. Correction: wire the certified replay engine (drill #4 designed it). On-deck (not the bottleneck).
- **11. LEARNING LOOP:** CLS shape is right (fast-write + slow-consolidate); the missing piece is the EXTRACT step = comprehension. Prior: loop v1-v6 negative (nothing to extract without comprehension). Follows 5/6.
- **12. FOUNDATION:** symbolic typed graph as SEED/teacher (encoding learned downstream) = foundational-for-role. Prior: inference-over-raw-symbols failed (can't shortcut earned reps). Adequate.

---

## CORRECTED ROADMAP (no shortcuts)
1. **v5 forward-PC (shipping):** tests OBJECTIVE fidelity. Necessary, NOT sufficient (still stateless). Read its verdict as "does a faithful objective help the representation," not "does it comprehend."
2. **THE STATEFUL CORE (the real hard build):** active working-memory maintenance + role-general binding + (light) recurrence, trained END-TO-END with the encoder — NOT bolted on frozen reps (the recurring error). This is the machinery that CONSTRUCTS a situation model. Reuse DG/sequence_memory/binding primitives; PE-gated learned update (PBWM); preserve dimensionality; mandatory random-init + both-seed controls (they catch structure-alone).
3. **Then** consolidation-replay (wire the certified engine) + the read->learn loop, for continual learning from reading.
4. Deeper objective (latent predictive coding, temporal-contiguity, multi-timescale) if v5's token-level rung shows the objective matters but caps out.

**The one-sentence honest verdict:** our encoder is feed-forward + bidirectional + stateless where the brain is recurrent + forward-predictive + stateful; we have repeatedly bolted isolated pieces onto that frozen core instead of building the coupled stateful-predictive machinery end-to-end — and that is the hard thing we have been avoiding.
