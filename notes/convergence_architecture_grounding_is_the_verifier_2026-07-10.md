# Convergence Architecture: Grounding enters inference through the VERIFIER, not the geometry — 2026-07-10 (Director)

**The question the crux forces:** the loop-closer proved grounding-in-the-GEOMETRY does NOT help relational inference (grounded vs ungrounded consolidation, ~+0.004, LOW-tail negative). So if grounding doesn't help the engine *infer*, why build a grounded core for it? Working this out in the director lane while the crux runs.

**The reconciliation (ties the whole arc together): grounding enters inference through the VERIFIER, not the representation.** Three independently-earned results point at one architecture:
- LOOP-CLOSER: grounding baked into the geometry/representation does NOT chain to relational inference. -> so do NOT put grounding in the geometry.
- CANDIDATE-B + STEP-1: the VERIFIER is the load-bearing piece of generate-and-test (ablating it halves ranking; a broken verifier can't infer). -> the verifier is where the leverage is.
- DEEPEST TARGET (all session): grounding = active/verifiable referent (predict, check against reality, be wrong). -> that IS a verifier.

**SYNTHESIS -> the working-system architecture (three mechanisms, each doing what it is good at):**
1. GEOMETRY (bind/unbind, FHRR) = STORAGE + density + compositional PROPOSE. Chain-grade. Good at holding + composing known relations. NOT asked to ground (it can't -- loop-closer).
2. GENERATE-AND-TEST ENGINE = PROPOSE candidate relations (head-conditional composition of known relations, the beat-frequency levers) -> the inference generator.
3. GROUNDED VERIFIER = CHECK each proposed candidate against (a) graph-structural support (hop-normalized, head-conditional) AND (b) GROUNDED-ATTRIBUTE CONSISTENCY: do the measured/grounded properties of the entities SUPPORT this relation? e.g. a proposed "X reacts-with Y" is more credible if X's and Y's grounded chemical properties are consistent; "X is-capable-of Y" checked against X's grounded affordances. The grounded attributes are the EXOGENOUS EVIDENCE the verifier uses to accept/reject.

**Why this is the right shape (it honors every negative + positive):**
- Honors the loop-closer negative: grounding is NOT in the geometry (which failed); it is in the verifier (which is load-bearing).
- Honors candidate-B: the verifier is the mechanism the passive methods lacked; grounding SUPPLIES the verifier its exogenous evidence.
- Operationalizes the deepest target: "active/verifiable grounding" = the grounded verifier checking proposed inferences against measured reality. This is where grounding finally becomes load-bearing FOR INFERENCE.
- Explains the grounded core's dual role: (1) the dense, meaningful, SPANNING knowledge base the engine infers over (density = the inference floor; spanning = everything grounds back); (2) the SOURCE OF VERIFICATION EVIDENCE (grounded attributes) the verifier consults.

**Testable prediction (the convergence experiment, after the crux + grounded-core land):** a generate-and-test engine whose verifier ALSO checks grounded-attribute consistency should infer held-out relations BETTER than a verifier using graph-support alone -- AND the improvement should be load-bearing (ablate the grounded-attribute check -> inference drops). If grounded-verification does NOT help over graph-support-only, then grounding is meaning/spanning value but NOT an inference booster (still valuable, but a bounded finding). Must-fail: a SCRAMBLED grounded-attribute check must not help (the grounding values, not their presence, must do the work).

**Where this sits in the plan:** the crux (running) tests PROPOSE+graph-verifier on dense FB15k-237 (ungrounded) -- isolates density+mechanism+beat-frequency. The grounded core (running) builds the spanning grounded knowledge base. The CONVERGENCE experiment then adds the GROUNDED VERIFIER: does checking proposed relations against grounded reality beat graph-support-only? That is the test of whether grounding is finally load-bearing for inference -- via the verifier, the one place the whole arc says it should be.
