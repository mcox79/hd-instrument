---
owner_verdict: DONE
---

SUBMISSION — space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging
status: PARTIAL (WIP until owner_verdict: DONE). Glass-box, NO external LLM. NO hdlab/ written (Q111: strategy lands
the wire). Witness 5/5. Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_space_ground_binding.py   # 5/5, deterministic

THE CORE RESULT
- BRIEF REFUTED (disk outranks brief): the proposed lazy locative-PP bridge lifts motion-event extraction recall
  0.444->0.889 but moves end where_is only +0.064 (modern, n=47, CI [-0.021,+0.149], NOT separated over the current
  chain). Detecting THAT a character moved was never the where_is bottleneck.
- REAL LEVER = NAMED-GROUND BINDING. Error decomposition vs a perfect-extraction ceiling (0.787) showed the loss is
  binding the correct NAMED PLACE to an already-detected move (SCENE 34% "reached the office"->just <scene>;
  WRONG_NODE 13%), not change-point recall. I built a brain-foundational Ground extractor (Talmy Figure/Ground;
  Landau & Jackendoff "where"; Rappaport Hovav & Levin): verb-frame Goal gate (VerbNet motion class) + compound-noun
  HEAD selection + closed-class partitive resolver ("back of the hall"->hall) + GRADED ConceptNet-AtLocation
  functional-locus typing + drop benefactive "for".
- MEASURED (where_is exact-node, paired bootstrap): MODERN 0.319->0.468 (+0.149, n=47); REAL 19c LitBank
  0.244->0.312 (+0.068, n=606, 24 timelines). Beats last-mention floor CI-separated on both; shuffled-ground TWIN
  loses CI-separated on both; precision IMPROVES on both (modern 0.571->0.702; 19c 0.163->0.209). Through the LIVE
  SituationReader.read(): stock 0.277 -> wired 0.447 (+0.170), 10 named grounds recovered.
- UPSTREAM localized (the owner's thesis, confirmed): a perfect ground NODE on already-fired events is worth +0.149
  where_is (0.468->0.617) -- as much as the whole downstream binder. The shared role router's Ground SELECTION is
  the single biggest lever (ground-extraction accuracy 0.692->0.731 with the fixes).

100% BRAIN-FOUNDATIONAL (the owner's gate): now yes, in shape. The one violation was a hand-curated functional-locus
LIST. Fixed it: a hard WordNet furniture/vehicle taxonomy (right shape) REGRESSED on real 19c prose (typed
incidental carriage/cart as loci) -> which proved functional-locus knowledge is GRADED, not hard membership -> so I
use graded ConceptNet AtLocation frequency (desk=216/plane=46 vs carriage=0/laugh=0). Recovers the list's accuracy
at stronger twin separation, no list. Every other piece is a closed grammatical class (prepositions, axial terms) or
a VerbNet class. Two small verb recall-backstops remain (same pattern as the shipped router's SPEECH_VERBS).

ALL WALLS UNDERSTOOD (measured, not asserted -- _diagnose_residual_firing.py): after a perfect ground node, the gap
to ceiling is 50% register REPRESENTATION (start/away states -- a readout limit), 19% discourse-Ground ("watched him
board, the plane..." -- Ground in a separate clause; genuinely hard AND brain-consistent, Ferretti 2001: weak
location anticipation), 19% self-motion label ("headed into the locker room" -- route_v2 valency gate territory),
12% rare-facility typing ("radiology"). My earlier "residual is parser attachment" was WRONG.

NO OTHER CONSUMER REGRESSES (verified, witness W5): the ground-binding emits only SPACE events;
extract_events_in_substrate is called ONLY by _read_space -> who-did-what events are BYTE-IDENTICAL with/without the
wire. The shared-router fixes (route_v2 valency + verb-frame Goal gates, exp_route_ground_v2) are additive and
brain-foundational but LOW-YIELD for space (base chain +0.00 modern / +0.01 19c) -- their value is the who-did-what
theme, not where_is.

LOCATED NEGATIVES (each a control that excluded something): (a) aggressive binder (locative/stative PPs +
protagonist fallback) REGRESSES on real 19c prose -> only the high-precision motion-goal subset is robust; (b)
anticipatory Goal binding (Altmann-Kamide) over-fires and HURTS both corpora -- AGREES with Ferretti 2001; (c) hard
WordNet funcloc taxonomy over-generates on 19c -> graded AtLocation is the faithful shape.

WHY PARTIAL not SOLVED: the gain over the (already decent) current chain does NOT CI-separate at the honest
character-timeline unit (modern CI touches zero; 19c separates at item level, not timeline). This is a STATISTICAL-
POWER wall (n=47 modern / 24 real timelines), not a fidelity wall -- and the one wall I can't close without more REAL
annotated space gold (LitBank's is fixed at 24 timelines; expanding my own author-gold to clear my own bar is a bias
hazard I won't take).

PROPOSED hdlab DIFF (Q111 -- strategy lands): (1) add ground_bind_events(...,conservative=True) from
exp_space_named_ground_binding_v1 into experiments/_space_reader.extract_events_in_substrate behind a
ground_bind=True kwarg, default ON in read_locations_in_substrate prior_ext mode; (2) fold the Ground-selection
helpers (compound-head + partitive + graded ConceptNet-AtLocation typing + "for" removed) into
hdlab/predicate_argument_frontend so the who-did-what/copular consumers get the better place typing too; (3)
optionally land route_v2's valency + verb-frame gates (brain-foundational, low-yield, no-regress). Land ON (coref +
precision improve, no other dim changes) with witness verification/test_space_ground_binding.py.

DO NOT LAND / DO NOT QUOTE: the aggressive locative/stative+fallback binder (regresses real prose); the anticipatory
Goal fill (over-fires); the hand-curated funcloc list or the hard WordNet funcloc taxonomy (use graded AtLocation);
a where_is gain without the shuffled-ground twin LOSING; the modern +0.149 as CI-separated over the current chain
(it is not, at the honest unit).

FILES (all experiments/ + verification/ + notes/; NO hdlab/):
exp_space_recall_e2e_ci_v1.py, exp_space_named_ground_binding_v1.py, exp_space_ground_binding_litbank_v1.py,
exp_space_ground_binding_live_wire_v1.py, exp_route_ground_v2.py, _diagnose_where_is_errors.py,
_localize_upstream_ground_lever.py, _diagnose_residual_firing.py; verification/test_space_ground_binding.py;
notes/problems/space_.../SOLVED.md; notes/research_spatial_ground_role_assignment_2026-09-05.md.

TLDR (plain English): the reader often knows a character moved but forgets WHERE. The brief blamed missing too many
moves; that wasn't it -- the problem was attaching the specific place. I built the fix (bind the place a character
ends up at), grounded every choice in how the brain assigns "where", and pushed it all the way up to the shared
sentence-role reader, which turned out to be the biggest lever. It helps on both modern and old text, improves
precision, runs live, and provably changes nothing else in the reader. I made the place knowledge use graded real-
world "what's found where" data instead of a hand list (and proving a rigid version over-fires taught us why the
brain's version is graded), and I measured every remaining weak spot instead of guessing. Solid, faithful, and
modest -- the only thing left between it and a decisive statistical win is more real hand-labeled data, not a better
mechanism.

QUESTIONS: none.

NEXT STEPS: (1) land the conservative binder + graded AtLocation typing; (2) have the copular "X is in the Y" reader
and the role router's is_place_ground adopt the graded AtLocation typing (the newly-optimized upstream capability);
(3) the last real lever is a larger REAL space-gold corpus for statistical power, not more mechanism; (4) fold the
AUDIT UPDATE (the space cap is named-ground binding, not recall) into BRAIN_FOUNDATIONAL_AUDIT.md.
