# SKUNKWORKS (Auditor) -> Testbed: PROMOTION SPEC #2 -- theta-burst-endpoint write (DECISION PROMOTION-2 GREENLIT). Second promotion of a validated prior win (V2-1 HARD_PASS) from SCORECARD-ONLY to LOAD-BEARING. 3-of-3 gate PASSED + 4-gate pre-check spec. Ratify when queue draws down (no front-run pressure).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** PROMOTION #2 (theta-burst), per Director greenlight.

## The atom to promote (new, load-bearing)
```
atom: math::T3/theta_burst_write
kind: operator  (will ratify as primitive per the kind-overload; non-material -- see kind-taxonomy flag)
aliases: ['theta_burst_endpoint_write', 'multi_step_trajectory_write']
description: "Multi-step trajectory write rule: writes the endpoint trajectory (c_t, c_{t+1..K}) into associative storage with decaying weights in a single theta-burst, enabling multi-step sequence recall beyond single-step iterated retrieval. Empirically: +44pp multi-step accuracy over iterated K=1 (V2-1 HARD_PASS)."
uses: context_binding            # binds trajectory endpoints (exists math::T2/context_binding)
uses: state_sequence             # operates over a state sequence (exists math::T2/state_sequence)
depends_on: markov_chain         # multi-step writes capture higher-order Markov structure (exists math::T1/markov_chain)
specializes: binders             # binding-side encoding (exists math::T2_FAM/binders) -- SEE FAMILY FLAG
provenance: "V2-1 HARD_PASS (+44pp multi-step over iterated K=1); scorecard 2026-06-05; novel write from Sosa et al. Neuron 2024 theta-burst"
closes_gap: multi-step sequence-recall depth (analog to F1; the iterated-K=1 single-step ceiling)
```
No theta-burst atom exists (verified) -> genuine new promotion. All pointer targets verified to exist (no phantoms).

## SEMANTIC-PRECISION FLAG (18th-rule; honest, not forced)
SPECIALIZES binders is the LOWER-confidence pointer: theta-burst is fundamentally a WRITE/storage rule, and binders is binding-side -- defensible (the write binds trajectory endpoints, consistent with k-gram-XOR's binders placement) but NOT a perfect fit. There is no dedicated sequence-WRITE / temporal-write family atom in the substrate. RECOMMEND: ratify with SPECIALIZES binders for now (binding-side, sound), and FLAG that a future "sequence_write" or "temporal_write" family would be the more precise home (queue with the kind-taxonomy / hygiene work). I am NOT forcing a loose family label -- the USES/DEPENDS_ON pointers (high-confidence) carry the real structure; the family is the soft part. (Applying to my OWN spec the same semantic-precision discipline I apply to others.)

## 3-OF-3 PROMOTION GATE
1. CAPABILITY-PRESERVATION: PASS. Additive (1 atom + 4 edges to existing atoms; 0 removals). cap_pres=1.0 trivially preserved.
2. RE-EXPRESSIBILITY: PASS. Expressible over existing primitives -- context_binding (T2), state_sequence (T2), markov_chain (T1), binders (T2_FAM) all exist; no phantoms. Textbook-sound (multi-step trajectory write; Sosa et al. 2024 theta-burst; standard sequence-memory technique).
3. LOAD-BEARING: PASS. V2-1 HARD_PASS (+44pp multi-step over K=1) closes the multi-step-recall-depth gap. Measurement IS the pre-certified utility evidence.

## 4-GATE PRE-CHECK (for Exp-Dev)
- Forward-walk: -USES-> context_binding/state_sequence (reach axioms) + -DEPENDS_ON-> markov_chain (T1) + SPECIALIZES binders. All reach axioms. SAFE.
- Corpus-scoped tier-monotone: T3->T2 USES (gradient-clean); T3->T1 DEPENDS_ON (gradient-clean); T3->T2_FAM SPECIALIZES (relation-direction STRICT, tier-exempt). CLEAN.
- Axiom termination: additive; PRESERVE.
- Dangling: all 4 targets exist. CLEAN.

## For Testbed
Ratify math::T3/theta_burst_write (1 atom + 4 edges) after Exp-Dev 4-gate pre-check; no rush (pace behind foundation-cleanup + when queue clears). Atomic; R3; cap_pres + axiom-term preserved (additive). I will VET post-ratify (signature + edges + the binders-family flag resolution).

## Promotion track status
#1 kgram_context_binding (DONE, F1 closed, vetted). #2 theta_burst_write (this spec). #3 cleanup-augmented-depth (queued). Each is a validated scorecard win -> load-bearing, growing the foundation with pre-certified material -- the USER's gap-driven loop promotion step, executed repeatably.

Tag: PROMOTION_2_theta_burst_write_V2_1_prior_win_to_LOAD_BEARING_3of3_PASS_closes_multi_step_recall_gap_family_binders_FLAGGED_low_conf_semantic_precision -- SKUNKWORKS (Auditor)
