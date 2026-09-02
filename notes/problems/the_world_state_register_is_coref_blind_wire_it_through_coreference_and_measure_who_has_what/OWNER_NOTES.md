---
owner_verdict: DONE
---

SUBMISSION -- the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what
status: SOLVED (WIP until owner_verdict: DONE). NO hdlab/ written (Q111). Witness 18/18; ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_world_state_coref_densify.py   # 18/18 FROM SOURCE

WHAT WAS BUILT: a two-stage brain-foundational entity binder in front of the mutable world-state register, so
possession keys on the DISCOURSE ENTITY, not the raw word (Glenberg 1987; Zwaan-Radvansky). experiments/
world_state_entity_binding.py = the Stage-1 dispatcher: pleonastic-it filter -> INDEXICAL (I/me/my->NARRATOR,
Kaplan) -> ANAPHORIC he/she (reuse the reader's OWN coref) -> OBJECT ANAPHORA (it->salient recent nominal,
recency+number+pleonastic) -> nominal; plus a CONFIDENCE-ABSTAIN gate (defer on high-entropy coref). Stage-2
(the register) was already faithful; the whole defect was Stage-1.

DISK OUTRANKS BRIEF: "wire the reader's own coref" cannot resolve object 'it' or first-person 'I' (its coref is
he/she-only). Decomposing the parent's "81% pronoun agents" into THREE routes of very different size/difficulty was
the key move; I built the two the reader lacked.

HEADLINE NUMBERS (CI-sep; floors + twins + change-point):
 * he/she densification, LitBank gold, the bites-population (n=26): coref-BLIND 0.000 -> READER 0.500 [0.308,0.692],
   +0.500; aggregate (n=135) reader 0.719 vs blind 0.570, paired +0.148 [0.096,0.208]; shuffled-coref null p95
   0.154; change-point 0.956; gold oracle 1.000.
 * OBJECT ANAPHORA accuracy, LitBank object gold (n=189): recency 0.730 [0.667,0.794] vs random-twin p95 0.323 vs
   first-mention 0.132 vs reader-coref 0.000 (abstains). BRAIN-FOUNDATIONAL SWEEP: number-agreement +0.206 CI-sep;
   subject-salience HURTS objects -0.212 CI-sep (objects aren't the backward-looking center -> recency, not
   Cf-prominence). MCScript2: 259/374 'it'-transfers relocated.
 * END-TO-END who-has-what, MCScript2 deterministic gold (n=2437): coref-BLIND 0.285 -> FULL BINDER 1.000,
   +0.715; change-point 0.976. (Indexical route dominates; caveat: full==gold by construction on the unambiguous
   subset -> this is the BLIND-GAP + route decomposition; per-route accuracy is the non-circular LitBank numbers.)
 * DOWNSTREAM benefit: who-has-what QA consumer BLIND 0.293 -> DENSIFIED 1.000. Powered impossible-action/bridging
   detection (n=2827 balanced): coref-BLIND balanced 0.637 (raw 0.382, BELOW the always-possible floor 0.862 --
   71.5% FALSE-flag) -> DENSIFIED 1.000 (0% false-flag/miss).

WALLS -- all understood: he/she ceiling is GROUPING-bound (grouping sweep: ~91% of the headroom is PRONOUN-CHAINING
/ incremental entity maintenance; realistic glass-box ceiling ~0.46, NOT the 0.75 gold-grouping figure -- a
self-correction); graded pick residual = long-distance (2x distance when wrong, entropy-flagged); graded params
near-optimal (held-out sweep, located negative); parser recipient-recall 0.33 caps live who-has-what (cited, needs
gold SRL to re-measure). Generalizes across two opposite corpora (LitBank he/she; MCScript2 indexical+object);
untested axis = OOD gold-coref corpus.

TO REALIZE THE GAINS (ordered, in SOLVED.md "TO FULLY REALIZE THE GAINS"):
 1. Land the densifier: promote the binder + default-off `densify_world_state` on _read_world_state (holder via
    bind_participant(coref_cluster=sm.coref_resolutions), theme via bind_theme). Accept: OFF byte-identical; ON
    entity-keyed.
 2. Wire a who-has-what QA consumer of sm.world_state -- the step that makes the gain a LIVE number. Accept:
    densified beats blind CI-sep live.
 3. Raise the ceiling via INCREMENTAL ENTITY MAINTENANCE (pronoun-chaining, the ~91% lever -> recurrent-completion/
    resonator organs; graded_coref_pick gives the modest pick gain).
 4. Close resource-bound gaps: OOD gold-coref (OntoNotes/GUM); confidence-abstain gate (built); object-coref CI-sep;
    we(group)/you(addressee)/quoted-I routes (currently abstaining, filed with spec).

FILES: experiments/world_state_entity_binding.py; exp_world_state_{coref_diagnose,coref_densify,deixis_object,
object_anaphora_gold,he_she_ceiling,graded_optimize,grouping_optimize,endtoend_whohaswhat,downstream,
bridging_powered}_v1.py; verification/test_world_state_coref_densify.py (18/18). AUDIT UPDATE for
BRAIN_FOUNDATIONAL_AUDIT.md 2b included.
