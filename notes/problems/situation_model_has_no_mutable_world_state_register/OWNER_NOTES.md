---
owner_verdict: DONE
---

SUBMISSION — situation_model_has_no_mutable_world_state_register (status: PARTIAL; owner-directed investigation folded in)

WHAT WAS BUILT (the assigned problem — DONE): the situation model's missing mutable WORLD-STATE dimension —
POSSESSION have(holder,obj) + a PRECONDITION-READ layer, as STRIPS operators. The register answers "who has X
at story-time t" and flags impossible (precondition-violated) actions — a capability the reader structurally
lacked (at/open already existed as location_register/state_register). Operators are derived FROM WHAT WE HAVE
(FrameNet: 105 transfer verbs across 13 frames, WITH the recipient role the stock front-end lacked) and are
LEARNABLE (OOV transfer verbs induced from observed possession transitions). Witness 36/36 from source. NO
hdlab/ written (Q111). Reverify: .venv/Scripts/python.exe verification/test_world_state_register.py

MEASURED (all CI-sep, twins lose): mechanism 1.000 vs strongest stateless floor 0.750 (+0.250), change-point
fires; precondition-read 1.000 vs ever-had 0.512 (+0.488); learning recovers FrameNet gold 1.000 vs shuffle
0.417, abstains on non-transfer; open text (MCScript2, reader's OWN parser) 1,467 transfer instances, recipient
now recoverable, residual LOCATED to coref (81% pronoun agents). Order-wall serve test: register does NOT break
the ~0.59 before/after wall (confirms order is conventional, not state — register is a STATE organ).

GAINS TO BE MADE AND HOW (deflated; the honest map after a full brain-mechanism sweep — see SOLVED.md table +
DISSECTION_before_after_order_wall.md):
1. REGISTER — a new capability, built+proven. HOW: promote core + wire default-off track_world_state flag
   THROUGH coref. RISK: coref-bound on real prose (81% pronoun agents).
2. SPREADING-ACTIVATION MEANING — mechanism VALIDATED (PPR beats shuffled-graph twin +0.099 CI-sep on WiC).
   HOW: land the grounded-semantic-graph organ + wire as a live meaning read-out. CRITICAL CAVEAT: that number
   is CLEAN-INPUT (gold lemma/POS, NO parser); the LIVE gain is PARSER-BOUNDED — measure it THROUGH the live
   extractor, never on gold WiC.
3. SYNTAGMATIC AXIS (SyntagNet) — TESTED, REJECTED (naive +0.000; up-weighted -0.011). Do NOT invest.
4. ORDERING — CLOSED by diagnosis (all 3 brain mechanisms replicated incl. abstain; ~half the pairs are
   genuinely order-free). Gain: ~0 aggregate; ~0.67 on the answerable ~1/4 via the partial-order ABSTAIN
   readout. Do NOT chase; the only remaining lever is a domain-matched everyday-script corpus (resource call).
5. PARSER / EXTRACTION FRONT-END — the highest-COMPOUNDING lever: it gates the LIVE payoff of BOTH validated
   mechanisms (roles for the register; lemma/POS for meaning). Everything above is validated and waiting on it.

THROUGH-LINE: both validated mechanisms prove out on clean input and realize their live gain only as far as the
parser supplies correct roles / lemma+POS — so the most compounding investment for effective LIVE comprehension
is the extraction front-end. Ordering is closed; the syntagmatic axis is a located negative.

FILES: experiments/world_state_register.py, exp_world_state_{query,precondition,learn_operators,realtext_mcscript,
serves_order_mcscript}_v1.py, possession_operators.py; the investigation cells exp_{order_wall_dissection,
event_mention_resolver,script_schema_foundation,partial_order_abstain,rocstories_order_prior,order_fusion_
precedence,role_structure_aligner,syntagmatic_axis_optimizes_wsd}_v1.py; verification/test_world_state_register.py
(36/36); SOLVED.md + DISSECTION_before_after_order_wall.md. python tools/problem_ledger.py --check = clean.
