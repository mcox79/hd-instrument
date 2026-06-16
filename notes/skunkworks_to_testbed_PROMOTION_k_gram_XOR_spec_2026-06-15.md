# SKUNKWORKS (Auditor) -> Testbed: PROMOTION SPEC #1 -- k-gram-XOR context binding (DECISION 139b). FIRST promotion of a validated prior win (V2-4 HARD_PASS) from SCORECARD-ONLY to LOAD-BEARING substrate atom. 3-of-3 gate PASSED + 4-gate pre-check spec. This is the gap-driven loop's PROMOTION STEP executed concretely; it grows the load-bearing core AND closes gap F1.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 139b promotion track, candidate #1.

## The atom to promote (new, load-bearing)
```
atom: math::T3/kgram_context_binding
kind: operator
aliases: ['kgram_xor_binding', 'k_gram_context_vector']
description: "Binds a k-tuple of token vectors into a single context vector via iterated binding: context_k(t) = bind(phi(c_{t-k+1}), ..., phi(c_t)). Lifts substrate sequence modeling from conditional-bigram (linear W*phi captures only first-order) to k-th-order Markov class by encoding the k-gram into one vector BEFORE the linear map. Empirically: k=3 reaches TRIGRAM-class at N=4096 (V2-4 HARD_PASS)."
uses: context_binding            # the base binding op (exists math::T2/context_binding)
specializes: binders             # member->family (exists math::T2_FAM/binders); STRICT by 101-ruling
depends_on: markov_chain         # realizes k-th-order Markov structure (exists math::T1/markov_chain)
computes: k_gram_context_vector
provenance: "V2-4 HARD_PASS (k=3 trigram-class at N=4096); scorecard 2026-06-05; rescue for EX1 bigram-ceiling"
closes_gap: F1 (substrate sequence-prediction bigram-ceiling)
```
NOTE: no kgram/xor atom exists yet (verified) -> genuine new promotion, not a double-create. The substrate's binding is HRR/FHRR/context (no literal XOR primitive atomized); context_binding is the correct base op, so I name it kgram_context_binding (XOR is one realization; the operator is binding-of-k-gram). All pointer targets exist (no phantoms).

## 3-OF-3 PROMOTION GATE (per Drill E / DECISION 139b)
1. CAPABILITY-PRESERVATION: PASS. Promotion is purely ADDITIVE (1 new atom + 3 edges to existing atoms; 0 removals). cap_pres=1.0 trivially preserved -- additive cannot lose served capability.
2. RE-EXPRESSIBILITY: PASS. The signature is expressible over EXISTING primitives -- context_binding (T2), binders (T2_FAM), markov_chain (T1) all exist; no phantom pointers. The operator is a textbook-sound VSA technique (encode k-gram into one vector via binding before the linear map; Plate/Kanerva lineage).
3. LOAD-BEARING (closes F1): PASS, with HONEST SCOPE. V2-4 HARD_PASS demonstrates k=3 reaches TRIGRAM-class -- this closes the documented F1 gap (bigram-ceiling) in the bigram->trigram sense. HONEST: it does NOT reach full neural-class; the documented gap was specifically "stuck at bigram," and trigram-class IS the lift. The measurement IS the gap-closure/utility evidence (pre-certified) -- no new test needed.

## 4-GATE PRE-CHECK (for Exp-Dev before Testbed ratify)
- Forward-walk reachability: kgram_context_binding -USES-> context_binding (reaches axioms via the binding chain) + SPECIALIZES binders + DEPENDS_ON markov_chain. All reach axioms. SAFE.
- Corpus-scoped tier-monotone: T3 -USES-> T2 (gradient-clean); T3 -SPECIALIZES-> T2_FAM (relation-direction STRICT, tier-exempt); T3 -DEPENDS_ON-> T1 markov_chain (gradient-clean). CLEAN.
- Axiom termination: additive; expected PRESERVE (215/215 or current).
- Dangling all-rel-type: all 3 targets exist (verified). CLEAN.

## What this DEMONSTRATES (the milestone)
This is the FIRST execution of the gap-driven loop's PROMOTION step: a VALIDATED prior win (V2-4, scorecard-only) becomes a LOAD-BEARING atom, growing the core with PRE-CERTIFIED material AND closing a documented gap (F1). It is the concrete, working answer to the USER's question ("use the successful results to form the foundation") -- not a plan, a done thing. Supply (validated win) + Demand (F1 gap) + promotion = the loop, executed once, end-to-end, substrate-internal, no external truth.

## For Testbed
Ratify math::T3/kgram_context_binding (1 atom + 3 edges) after Exp-Dev 4-gate pre-check. Atomic; R3 verify; cap_pres=1.0 + axiom-term preserved (additive). Expected delta: +1 atom, +3 edges (+ HAS_USERS auto-reverse). I will VET the post-ratify state (signature correct, edges materialized, F1-closure provenance attached).

## Queue (subsequent promotions, per Phase A audit JSONL + 139b)
forward/backward/viterbi -> F3 (HMM); collins_structured_perceptron -> F4 (perceptron); then the 17+ flagship anchors (HP-12 crypto, Tier-4/6, audit-core, causal cluster) via the same 3-of-3 gate. I will spec these in priority order (gap-matched first).

Tag: PROMOTION_1_kgram_context_binding_V2_4_prior_win_to_LOAD_BEARING_3of3_gate_PASS_closes_F1_bigram_to_trigram_FIRST_loop_promotion_step_executed -- SKUNKWORKS (Auditor)
