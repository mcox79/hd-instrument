---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — wire_entity_tracking_end_to_end_on_running_narrative   (STATUS: SOLVED)
Session: solver (opus 4.8). hdlab/ UNTOUCHED throughout (proposed diff only; board Q111).
AWAITING owner_verdict: DONE in OWNER_NOTES.md before integration.

REVERIFY (scaffold-free, lands nothing):
  .venv/Scripts/python.exe verification/test_entity_tracking_end_to_end.py   ->  7/7 PASS
Ledger: python tools/problem_ledger.py --check  ->  malformed/incomplete: 0.
═══════════════════════════════════════════════════════════════════════════════════════

THE BAR (verbatim, PROBLEM.md §7): "Correct (salience-bound) entity linking must improve a DOWNSTREAM
entity task (next-argument prediction, or cross-sentence who-did-what) CI-separated over its UPPER bound
vs STRING-IDENTITY linking, with an info-free twin (shuffled entity links) LOSING CI-separated. Report CI
half-width + null p95. Attribute the gain to the LINKING (ablate the binder -> string-identity). DECISIVE
EITHER WAY."

ONE-LINE VERDICT. MET on cross-sentence WHO-DID-WHAT, and the composition yields a clean, brain-real
DISSOCIATION: correct pronoun linking buys ATTRIBUTION (keeping a character's history retrievable), NOT
anticipation (it does not help next-argument prediction). Three brain-fidelity drills grounded every step;
the deepening produced a concrete, brain-motivated accuracy win (graded binding).

#####################################################################################
1. THE BAR IS MET — cross-sentence who-did-what (LitBank, 100 novels, real hdlab register)
#####################################################################################
Composed the ACT-R salience binder + coref threads + the REAL organ hdlab.situation_model_accumulate
(multibank register): decode what an entity DID at a queried sentence, anchored on a NAME mention. Rich
task (majority-verb floor 0.137). Pronoun-contributed subset, n=9,078 queries, bootstrap over documents:
  ORACLE 0.6182 [.5977,.639] | ACTR_BINDER 0.1739 [.1536,.1959] | STRING_IDENTITY 0.0589 [.0515,.0679]
  RECENCY 0.1610 [.1429,.1814] | SHUFFLED_TWIN 0.1008 [.0929,.1095]
- Bar: ACT-R linking > string-identity, pronoun subset +0.115 [0.0951,0.1352] (hw 0.020), full task
  +0.0249 [0.0175,0.0329]. CI-separated. MET.
- Info-free twin LOSES: ACT-R > shuffled-link twin +0.0731 [0.0516,0.0934] (null p95 = twin upper 0.1095)
  -> CORRECT binding, not merely 'a link exists', is the source (the twin beats string-identity only
  +0.042, i.e. chance recovery -- which is why the twin, not the floor, is the load-bearing control).
- Attribution: the gain LOCALIZES to pronouns (pronoun-subset +0.115 >> full-set +0.025; names are
  string-resolvable in every arm), and the binder-ablation (ACT-R -> string-identity) restores the loss.

#####################################################################################
2. DECISIVE THE OTHER WAY — anticipatory PREDICTION does NOT benefit from linking (dissociation)
#####################################################################################
On next-object prediction via the grounded content-addressable channel (n=2,885; chance surprisal 2.9957;
LOWER=better), tested the KNOWN-WEAK entity-alone arm AND the faithful gist++entity AUGMENT arm:
  GIST_ONLY 2.9992 (already at chance) | AUG_ACTR 3.2183 | AUG_STRID 3.119 | AUG_ORACLE 3.2498
- Adding the entity state HURTS: entity augment of the gist -0.2192 [-0.2477,-0.1911] (cue-dilution).
- Correct linking is NOT better than string-identity: AUG_ACTR vs AUG_STRID -0.0993 [-0.1234,-0.0764]
  BELOW; name-targets -0.0004 NOT separated; even ORACLE linking -0.1307. Robust null.
- This is a GENUINE LIMIT (drill-confirmed): the brain predicts via entity-AGNOSTIC generalized event
  knowledge (schemas + verb-thematic-fit), so coreference feeds retrieval/consistency, not anticipation.

#####################################################################################
3. THE DEEPENING WIN — graded (Nref-faithful) binding, a divisive-normalization INTERIOR OPTIMUM
#####################################################################################
The ERP drill PINS that ambiguous reference evokes an Nref (hold candidates open under WM load), not a
silent wrong-commit. Implemented as GRADED binding: distribute a pronoun's event across candidates by
softmax(ACT-R activation). Full 100-doc, pronoun who-did-what recall:
  HARD_argmax 0.1783 | SOFT_graded 0.2051 | UNIF (uniform-weight control) 0.1322
  SOFT-HARD +0.0268 [0.0189,0.0346] ABOVE | SOFT-UNIF +0.0729 [0.053,0.0928] ABOVE | UNIF-HARD -0.0462 BELOW
-> the ACTIVATION weighting is essential (uniform hedging is WORSE than hard). Temperature sweep = textbook
INTERIOR OPTIMUM: SOFT rises from hard-argmax (temp->0, 0.1783) to a PEAK at temp~2.0 (0.2084), falls back
through hard (temp 4.0) toward the uniform-flat limit (temp 20 = 0.1386 ~ UNIF 0.1322); SOFT>UNIF at every
temp. This is exactly divisive normalization (Carandini & Heeger 2012): argmax/graded/uniform are one
family, and an INTERMEDIATE setting is the canonical cortical computation.

#####################################################################################
4. FIDELITY DIAGNOSTICS (drill-demanded) + honest deflations
#####################################################################################
- FAN EFFECT confirmed: oracle decode 0.6954 -> 0.6079 as an entity's event-count grows 1-3 -> 17+ ->
  the dense FHRR bundle IS the shortcut the drill flagged (faithful fix = SPARSE DG-style encoding + CA3
  completion, NOT a pointer -- a pointer alone would still fan; Norman & O'Reilly 2003).
- DEFLATION 1: ACT-R does NOT clearly beat simple RECENCY downstream (+0.0129 [-0.0004,0.0282], NOT
  separated). Tried the drill's actionable dilution test (stratify by candidate count) -- INCONCLUSIVE:
  the proxy saturated (9,006/9,078 queries in the "3+ competitors" bucket; long docs + unknown gender), so
  it neither confirms nor refutes dilution. Named follow-up: referential-distance / known-gender proxy.
- DEFLATION 2: ACT-R recovers only 0.1739 of oracle's 0.6182 (28%) -> large binder+decode headroom.
- The who-did-what win over string-identity is partly STRUCTURAL (a pronoun can't match a name), so the
  load-bearing non-tautological results are ACT-R > shuffled-twin and the graded win.

#####################################################################################
BRAIN-FIDELITY VERDICT (3 drills; PINNED vs OUR-INVENTION vs GENUINE-LIMIT)
#####################################################################################
- PINNED: pronoun -> REACTIVATES the referent's representation (Dijksterhuis 2024 Science single-unit;
  Ding 2023 MEG). Step 3 (reinstatement -> prediction) UNTESTED in humans; our composition is the
  computational test, and it comes back NULL for content-prediction -> loop does not auto-close.
- PINNED (dissociation, moderately): item-episodic retrieval (hippocampal) vs schema/verb prediction
  (mPFC/cerebellar forward model) are separable (Preston & Eichenbaum; Knowlton & Squire; Brown-Schmidt/
  Duff 2020: hippocampal amnesia SPARES online prediction). Caveat: active-harm direction is cue-overload,
  not a deep fact (Barron/Friston 2020: two modes of one machinery).
- PINNED (competition SHAPE): graded, activation-weighted, intermediate — divisive normalization / Luce /
  cue-based parallel activation. Temperature is a fitted parameter, not a biological constant.
- GENUINE-LIMIT: naive entity-history recurrence was never the brain's prediction mechanism. MISSING (a
  SEPARATE organ, not this composition): SCHEMA-ROLE-conditioned prediction (Cohn & Paczynski 2013 — role,
  not identity, predicts; Chen/Norman 2021 — role and filler must be kept separate). Does NOT change verdict.
- PROHIBITION honored: framed as a computational-level decomposition (salience selects -> content
  reinstates -> conditions readout), NOT a strict serial two-stage brain architecture.

#####################################################################################
PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands, Q111)
#####################################################################################
1. Wire the salience binder + coref threads into the entity register for a "who-did-what" RETRIEVAL readout
   (what did X do), NOT as a predictive prior (measured null).
2. Use GRADED (activation-weighted) binding, not hard argmax: softmax(activation/temp), temp a swept
   hyperparameter (~2.0 on LitBank). Interior optimum; +0.027 CI-sep over hard; uniform control confirms
   the activation weighting is essential. The one accuracy-relevant, brain-motivated change.
3. Replace the dense-bundle register with SPARSE (DG-style k-WTA ~1-5% active) conjunctive encoding + CA3
   attractor completion -- NOT merely an index/pointer (a pointer alone still fans). Keep the bundle as a
   gist. Fan effect measured; aligns with the audit's dense->sparse deviation.
4. Do NOT add an entity-conditioned PREDICTIVE prior for running narrative from this composition (null).
5. Keep pronoun BINDING salience-based; content-addressable retrieval is the store-access channel, not the pick.

#####################################################################################
AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md — coref/binding + situation-model entries)
#####################################################################################
- Composition measured end-to-end: correct pronoun linking buys ATTRIBUTION (+0.115 pronoun who-did-what,
  twin loses +0.073), NOT PREDICTION (entity augment -0.219; correct vs string-identity -0.099; oracle
  -0.131) -> value of coreference for the situation model is retrievability, not a predictive prior.
- Step 2 (reactivation) PINNED (Dijksterhuis 2024; Ding 2023); Step 3 (reinstatement->prediction) untested
  & here NULL. Dissociation neurally supported; active-harm = cue-overload, not a deep fact.
- Fan effect MEASURED on running narrative (0.695->0.608) -> upgrade dense->sparse from suspected to
  measured; faithful fix = sparse conjunctive encode + attractor completion (not a pointer).
- Graded activation-weighted binding BEATS hard argmax (interior optimum, peak temp~2.0; uniform WORSE) --
  divisive-normalization SHAPE pinned, temperature fitted.
- Prediction is entity-AGNOSTIC generalized event knowledge; the entity's real predictive contribution (if
  any) is its current SCHEMA-ROLE, a separate organ -- not the coreference channel.

FILES: experiments/exp_litbank_entity_tracking_end_to_end_v1.py (--run who-did-what, --predict, --graded);
verification/test_entity_tracking_end_to_end.py (7 witnesses); notes/problems/wire_entity_tracking_end_to_
end_on_running_narrative/SOLVED.md + research_composition_brain_mechanism_2026-08-27.md + research_limits_
finest_resolution_2026-08-27.md; data/litbank/who_did_what_events.json (spaCy event cache). hdlab/ UNTOUCHED.

WHAT I'D WITHDRAW FIRST IF WRONG: the who-did-what "beats string-identity" is partly structural (a pronoun
can't match a name) -- I stand on ACT-R > shuffled-twin and the graded win. ACT-R does NOT clearly beat
recency downstream, and my dilution test was inconclusive (saturated proxy). The prediction null is scoped
to next-OBJECT prediction at the 12-dim grounded space (the same channel WON on QA-SRL). spaCy roles/verbs/
objects are a stand-in for the substrate's incremental parser (parse errors unaudited, cap absolute numbers).

TLDR. On real novels, correctly resolving "he/she/they" (vs the cheap trick of matching identical names)
clearly helps a reader answer "who did what back in that scene" -- and a version that links pronouns to a
RANDOM compatible character does much worse, so it's the correct link that matters. But it does NOT help
predict what a character does next, even with perfect linking -- and the brain science says that's right:
prediction runs on general story/world knowledge, not on any one character's history. So pronoun resolution
earns its keep as MEMORY RETRIEVAL, not anticipation. Two brain-faithful bonuses: (a) when unsure who a
pronoun means, spreading the guess by confidence (as the brain does) beats forcing one choice -- and it
peaks at an intermediate spread, exactly as cortical "divisive normalization" predicts; (b) our character-
memory blurs as a character piles up events, pointing to a sparser, brain-like storage design.

QUESTIONS: none. One judgement call for integration: the headline "beats name-matching" is partly
structural; the honest one-liner is "correct linking makes a character's pronoun-referenced history
RETRIEVABLE (a random-link version can't), it buys retrieval not prediction, and the ACT-R form doesn't
clearly beat simple recency downstream."

NEXT STEPS: (1) land graded (activation-weighted, temp~2.0) pronoun binding -- the one accuracy-relevant,
brain-motivated change; (2) redesign the character-memory store to be sparse/separated (DG+CA3), not a
dense bundle; (3) do NOT wire this as a predictive prior -- use it for "what did X do" retrieval; (4) the
faithful route to entity-conditioned PREDICTION is the character's current schema-ROLE (a separate organ);
(5) optional: settle ACT-R-vs-recency downstream with a referential-distance / known-gender difficulty proxy.
═══════════════════════════════════════════════════════════════════════════════════════
