---
owner_verdict: DONE
---

SUBMISSION — gate_the_eventive_nominal_event_channel_by_context_wsd_event_vs_result
status: PARTIAL (a first-class REFUTED-and-RESOLVED outcome — your call on the label). hdlab UNTOUCHED (Q111).
Glass-box, NO external LLM at inference.

WHAT WAS ASKED: build a per-token context/WSD gate so the eventive-nominal channel (nouns like "attack"/
"construction" = events) can turn default-ON at verb-only precision, fixing its polysemy over-firing ("building"
act vs object).

HEADLINE — the brief's premise is REFUTED, and the real goal is met a different way:
- I built the gate faithfully (biased-competition WSD over the parse-selected selectional neighborhood + a
  selectional-restriction cue + the frequency/dominance prior). At the EXTRACTION level it restores precision
  CI-separated over the ungated floor (TB-Dense +0.062, MAVEN +0.054), twins losing.
- BUT end-to-end through the ACTUAL solved temporal reasoner, gating is net-NEGATIVE: answered-correct ungated
  0.4937 (87% of the gold-event ceiling) vs WSD-gated 0.4590 / dominance-gated 0.4470 (both CI-separated WORSE);
  conditional accuracy is FLAT (~0.58). Gating only drops coverage. The reasoner is already robust to the
  over-extraction (confirms p2's cond-acc finding).
- The precision "cost" the brief is built on is an EXTRACTION-INSTRUMENT ARTIFACT (the gold doesn't annotate every
  eventive nominal), not a downstream cost.

RESOLUTION: turn the eventive-nominal channel DEFAULT-ON UNGATED (`joint_nominal_events = True`); do NOT wire the
gate. That is the real win — the biggest temporal-survival lever, safe as-is.

WHY THE GATE CAN'T FULLY SEPARATE (drilled, brain-foundational): event-vs-object sense signatures are cos 0.93
COLLINEAR in the distributional w2v space (grounded sensorimotor: 0.51) — the readout is handed two near-identical
vectors. Grounded signatures REFUTED at power (the distinction is argument-structural, not lexical). The derived
selectional-preference organ TIES the hand list (data-starved). The frequency/dominance prior gives the best single
precision but the same frontier. All four brain-foundational cues land on one frontier → the residual is structural
(~9-19% is trigger-vs-named-reference, not WSD) + the extraction instrument, not a missing cue.

KEY REALIZATIONS: (1) measure what matters — extraction precision is the WRONG target; the reasoner's answers are.
(2) compute the noise ceiling + check prior work FIRST — I overstated a "35-point reasoner gap" (invented a 90%
human number; used a weakened reasoner) when the landed reasoner is already at the ~59-64% human agreement ceiling
(Sec 4i — corrected and owned).

FILES (experiments/ + verification/ only; hdlab UNTOUCHED): _nominal_wsd_gate.py (+grounded+frequency paths),
exp_nominal_wsd_gate_v1.py, exp_nominal_overfire_enumeration_v1.py, exp_nominal_gate_representation_probe_v1.py,
exp_nominal_gate_grounded_v1.py, _selectional_preference.py, exp_nominal_gate_selectional_v1.py,
exp_nominal_gate_frequency_v1.py, exp_nominal_gate_endtoend_v1.py (the decisive test), exp_temporal_chain_diagnosis_v1.py,
exp_temporal_gek_inference_v1.py, exp_temporal_gek_entropy_v1.py, exp_temporal_grow_order_v1.py,
exp_temporal_causal_reasoner_v1.py, exp_temporal_script_override_v1.py; verification/test_nominal_wsd_gate.py (W1-W4 PASS).

REVERIFY: .venv/Scripts/python.exe verification/test_nominal_wsd_gate.py   (W1 self-test; W2 additive/no-regress
subset; W3 precision restored over floor; W4 permuted-context twin loses)

PROPOSED hdlab DIFFS (Q111 — strategy lands): (1) flip joint_nominal_events default-ON ungated; (2) wire latent
hdlab.temporal_script_schema to the reasoner's IMPLICIT-EVENT/UNKNOWN path (confidence-gated; narrated path
byte-identical) — SOLVED Sec 7.

AUDIT UPDATE (MEANING/WSD + TIME sec.2b): eventive-nominal channel → safe default-ON UNGATED (gate refuted
downstream); w2v distributional space is non-brain-foundational for SORTAL distinctions (cos 0.93); temporal
ordering is at the human noise ceiling; temporal_script_schema is LATENT → wire to the implicit-event path.

TLDR: The reader over-counts nouns that can mean an act or an object. I built the "be pickier" gate and tested the
thing that matters — does it change the reader's timeline answers? It makes them WORSE (removes useful events; the
reader was already robust). So the fix flips: switch the big improvement ON as-is; the imprecision worry was a
scoring artifact. Along the way I also corrected myself — I'd wrongly claimed the reasoner was far below human; it's
already at the level humans agree with each other.

NEXT STEPS: (HIGH) flip nominal on ungated; wire temporal_script_schema to the implicit-event path. (MEDIUM) MAVEN
end-to-end confirm; open ONE new problem — grow a broad causal/event-order knowledge store (see Block B). (RETIRED)
the gate; standalone narrated temporal ordering (at noise ceiling).
