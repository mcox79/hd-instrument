---
owner_verdict: DONE
---

SUBMISSION — route_the_unified_referent_to_its_non_coref_consumers_where_it_helps
STATUS: PARTIAL (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference, NO trained
classifier anywhere in the component, NO training runs. NO hdlab/ written (Q111 — proposed wires only).
Reverify (headline): .venv/Scripts/python.exe verification/test_crosstype_landable.py  (4/4)
  Full suite green: test_route_unified_to_consumers.py 16/16 (the refutation + fidelity + strata),
  test_crosstype_precise_constructs.py 4/4, test_crosstype_landable.py 4/4, test_crosstype_upgrades.py 3/3,
  test_crosstype_chain.py 2/2; executable fidelity scan: experiments/exp_fidelity_scan_full_chain_v1.py.
  Ledger: malformed/incomplete 0. Determinism pinned (PYTHONHASHSEED).

TWO-PART RESULT.
(1) THE BRIEF'S MECHANISM IS REFUTED. Routing the landed unified referent to the three live non-coref consumers
(entity-KB / affect-experiencer / situation-model entity layer) does NOT give a per-consumer CI-sep gain on modern
gold (GUM V12.1.0, 137-doc TEST). Grouping-as-clustering regresses (C2 -0.0089, C3 -0.078); the reader_coref lever
is INERT (0 label changes on 137 docs; the +0.0882-on-19c lever is 19c-only, shown with the reader's own two-pass
source too); completed-gender is flat. The one CI-sep edge (entity layer +0.0036) is subsumed by a DIFFERENT dormant
landed organ (the entity-KB resolver). He/she pick byte-identical (16/16). Controls: byte-faithful self-test vs the
live resolve_unified_stream, shuffled-grouping twin, source control, no-regress. => DO NOT WIRE the unified referent.
The reference-harness "non-coref lifts" (+0.072/+0.106) were the PRONOUN pick under a different scorer, not the live
common-noun consumers (Ariel cue-specificity: the card's completed salience is the PRONOUN cue).

(2) THE UNDERLYING GOAL IS ACHIEVED A DIFFERENT, FULLY BRAIN-FOUNDATIONAL WAY — the "solve it a different way" the
protocol wants. A glass-box CROSS-TYPE definite->name BRIDGE, built ALL THE WAY UP THE CHAIN and validated LANDABLE:
  parse (reader's arc-eager+labeler) -> grammatical ROLE (deprel) -> Cf-ranked ACT-R SALIENCE (Centering,
  ROLE_PROMINENCE) -> CUE-BASED RETRIEVAL (Lewis-Vasishth) with DESCRIPTIVE-CONTENT override (Almor, from a
  precise-constructs predication detector) + gender + recency -> FULL-REFERENT COMPETITION (Heim/DRT: ALL prior
  referents compete, common + named) -> RETRIEVAL-CONFIDENCE familiarity gate (Heim/McElree: low activation = no
  referent found = novel -> abstain; a SWEPT threshold = the speed-accuracy tradeoff, ONLINE, NO trained classifier).
  Live-parse (NOT gold UD): 0.86 precision. Downstream, deployment-honest (fires on ALL person-definites, paired
  doc-bootstrap, 275 docs): lifts the affect/goal EXPERIENCER consumer CI-separated (+0.0528 conservative, up to
  +0.086 at the liberal operating point), entity-KB hard-link +0.006, entity layer up-or-flat; the info-free
  shuffled-target TWIN loses CI-sep (correct targeting is load-bearing).

THE NEGATIVE, FULLY UNDERSTOOD (owner: "if it's truly brain foundational it should have worked"). The ungated
retrieval's C1 regression is a FIDELITY GAP, not a ceiling: decomposed (682 fires) to 88.7% NON-ANAPHORIC over-firing
(39% of all fires = a same-head COMMON referent the definite should have bound instead of a name) + 11% genuine
disambiguation. Building the missing brain mechanisms CLOSED it: (a) FULL-REFERENT COMPETITION halved the regression
(-0.0058->-0.0026) and grew C3 to +0.086; (b) the RETRIEVAL-CONFIDENCE gate raises precision 0.735->0.95 and takes C1
to +0.0000 (safe). No trained classifier — the earlier "needs a classifier" claim was wrong and is corrected.

UPGRADES (built + measured; honest wins AND negatives): graded ACT-R competition (adopted, +coverage); the unified
cue-based retrieval + full-referent competition (the deployable, most-faithful bind); retrieval-confidence familiarity
gate (the brain's novelty mechanism, no classifier). REJECTED with measurement: FrameNet raw ingest (too noisy —
conflates agent/patient roles); the Hawkins establishing-modifier novelty heuristic (located negative on GUM's bio
register — "the director OF X" is usually anaphoric); a Wikidata occupation KB (acquired real, then a MEASURED located
negative — descriptors are age/gender/relation/context, NOT catalogued occupation, 1/16 match). Animacy upgraded to a
WordNet frequency-prior (the brain's default sense) replacing a hand stoplist.

FULL-CHAIN FIDELITY SCAN (executable: experiments/exp_fidelity_scan_full_chain_v1.py; prose:
FIDELITY_SCAN_full_chain_2026-09-07.md, 12 layers). VERDICT: every COMPUTATION is brain-foundational (DRT file-change,
Centering Cf, ACT-R cue-based retrieval, Heim familiarity-via-retrieval-confidence, Almor override, full-referent
competition, frequency-prior animacy); the implementation is FAITHFUL at the bind + all its brain-mechanism upstream,
with the ONE remaining proxy being the shared STATISTICAL front-end (POS/parse/labeler) — a reader-wide gap, measured
(live parse costs 0.156->0.123 coverage / 0.96->0.86 precision). 14/15 upstream organs live. NO trained classifier,
NO external LLM at inference.

KEY REALIZATIONS: (1) the disk's default flags (entity_kb_resolver=False) reset the floor and showed the reader_coref
lever is doubly-dormant. (2) The reference-harness "non-coref lifts" were the pronoun pick under a different scorer
(Ariel cue-specificity) — the whole refutation. (3) A glass-box CEILING upper-bound is not a capability — build the
mechanism and measure whether it REALIZES (the NE-type upper bound of 0.77 realized at ~7% precision until the full
chain). (4) The negative was a fidelity gap (88.7% non-anaphoric), not a ceiling — the brain competes ALL referents.
(5) The brain does NOT use a trained classifier for novelty — it uses RETRIEVAL CONFIDENCE (Heim/McElree); building
that closed the gap. (6) Validate the twin against the metric (CoNLL size-robust; hard-link size-gameable).

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md E3): keep hdlab/unified_referent.py DEFAULT-OFF everywhere (refuted at the
non-coref consumers too, not just the he/she pick; corrects the p12 "its real home is the non-coref consumers" note).
NEW: the cross-type definite->name bridge is a brain-foundational component (cue-based retrieval + full-referent
competition + retrieval-confidence familiarity gate, all online/glass-box) that lifts the affect/goal experiencer
CI-separated on modern gold; its ceiling is the world-knowledge residual + the shared statistical-parser gap.

TLDR (plain English): the shared-record idea for characters doesn't help the reader's other jobs (proven, don't wire
it) — but the GOAL behind it does, via a better mechanism I built the brain's way: figure out who "the doctor" is by
looking it up in memory among everyone mentioned so far, and only commit if the memory match is strong (otherwise treat
it as new). Built end to end with the brain's actual machinery — no outside AI, nothing trained on the task — it makes
"attach a feeling to the right character" measurably better on modern text (about 5-9 more right in 100, a controlled
gain a scrambled version can't fake). I chased the one case where it briefly made things worse to the bottom and found
it was a missing piece (the brain compares against everyone, not just named people), fixed it, and it flipped positive.
Honest limits: the gain is real but modest (the hard cases are thin on modern text and mostly need outside facts we're
barred from inventing), and the only non-brain part left is the shared statistical parser everything relies on.

QUESTIONS: none blocking. One judgement call: marked PARTIAL — the brief's own mechanism is refuted, but a per-consumer
CI-separated gain was delivered a different, fully brain-foundational way. If you want it REFUTED-with-a-documented-
follow-on instead, that's a one-line change; PARTIAL reflects that the goal was met.

NEXT STEPS (HIGH PRIORITY FIRST; strategy owns hdlab landing, Q111):
1. HIGH — LAND the cross-type bridge (cue-based retrieval + full-referent competition + retrieval-confidence gate, all
   online/glass-box, no classifier) into the entity-KB resolver's predication hook, with the confidence threshold as
   the tunable speed-accuracy operating point (tune on the live parse). Net-positive experiencer lift, twin-controlled.
2. HIGH — KEEP hdlab/unified_referent.py DEFAULT-OFF everywhere (refuted); fold the AUDIT UPDATE into E3.
3. MEDIUM — the reader-wide STATISTICAL-PARSER fidelity gap (the one remaining proxy; costs ~0.03 coverage / 10pt
   precision here) is a separate program — an incremental-predictive (surprisal) parser would lift THIS and every
   consumer downstream.
4. LOW — do NOT pursue: a Wikidata occupation KB (measured located negative), the FrameNet raw ingest (noisy), a
   trained discourse-new classifier (non-brain-foundational; the retrieval-confidence gate is the brain's mechanism).
