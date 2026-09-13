

## pasted by the owner 2026-09-13 13:46 (raw; strategy reads this)

Submitting solver problem: attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally

STATUS: PARTIAL — a brain-foundational COMPONENT WIN + an airtight located negative, with the upstream
blocker probed to its ceiling and the tractable upstream lever built and honestly refuted.

MECHANISM (built, self-test 9/9): verb-frame SLOT-OCCUPANCY factor for the Competition-Model coarse role
labeler (graded_role_assigner.coarse_roles) — a verb's nominal dependents are labelled JOINTLY, capacity ONE
per core frame slot (subject/object/recipient/by-agent), frame-conditioned (a monotransitive verb has no
recipient slot), displaced core fillers fall to oblique. Brain: capacity-limited cue-based retrieval (Lewis &
Vasishth; MacWhinney verb valence). Knowledge in counts (a verb takes 2 objects 0/9516 — capacity-one IS the
counts), plastic/online (witnessed). Hard form for point heads, SOFT graded-hand-off form with a posterior.

RESULT (UD-EWT test n=700, object-role precision): gold heads 0.818->0.840 (+0.022 CI[+0.008,+0.036] CI-sep);
deployed supervised parse 0.633->0.700 (+0.067 CI[+0.044,+0.090] CI-sep, accuracy up); info-free twin far
below everywhere. Agent board arm byte-identical (not down).

FULL-STACK / all-BF stack (owner-directed Path A): on the fully-BF stack (BF tagger lexical_categories + BF
attachment_arm heads) the gain is not CI-sep (+0.010) because the BF parser's core-argument arcs are too weak
(OBL/PP-attachment head-acc 0.439) and its posterior is confidently wrong (graded hand-off + tau sweep
exhausted). ORACLE probe: fixing core-arg heads to gold (nom-UAS 0.58->0.81) makes the occupancy win CI-sep
on the all-BF stack (+0.0156 CI[+0.004,+0.028]) — so improving core-arg attachment is SUFFICIENT. LEVER C
(data-scale the landed Hindle-Rooth pp cue from 150k Simple-Wiki sentences): REFUTED — OBL 0.443->0.448
(CI incl 0), enriched~=twin; sparsity is not the constraint (the cue's learned validity caps its decode
influence). The who-did-what patient arm doesn't move (its reader absorbs double-objects); the win lives on
object-role precision, its own instrument.

FILES: experiments/exp_role_slot_occupancy_v1.py; notes/problems/<slug>/{SOLVED.md,
graded_role_assigner_patch.diff, RESEARCH_pp_attachment_bf_lever.md}
REVERIFY: .venv/Scripts/python.exe experiments/exp_role_slot_occupancy_v1.py --self-test

COMPONENTS/BF: graded_role_assigner BF_SPIRIT (extended); attachment_arm BF_SPIRIT (the located bottleneck,
OBL 0.439); lexical_categories BF_SPIRIT (tagger, not the bottleneck); arc_labeler NOT_BF for fine relations
(argument roles are the BF competition); WordNet-morphy lemma at inference still NOT_BF (pri-12).

TOP NEXT STEP: a dedicated attachment-arm problem for SEMANTIC-CLASS-backed PP-attachment (Resnik/Stetina-Nagao:
re-key the pp cue lemma->induced-category + verb-subcategorization + prep-object class + cue re-weighting) —
data-scaling is spent; the lever is structural (pri 15-17). Ceiling shown: with core-arg attachment fixed,
this already-proven role component makes the all-BF stack superior unchanged. Then land
graded_role_assigner_patch.diff (soft with posterior, hard otherwise) + case-protect the pronoun-object edge
case + give object-role precision its own board dimension.

hdlab changes are PROPOSED only (Q111); owner_verdict is unset — solver did not self-integrate.
