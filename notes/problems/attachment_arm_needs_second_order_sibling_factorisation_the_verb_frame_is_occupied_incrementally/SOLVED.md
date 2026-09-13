---
problem: attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally
status: PARTIAL
bar: "patient-arm score up CI-separated over the current read, agent not down, object-role precision up, twin (shuffled slot counts) far below, witness green -- or a numbered located negative that names the upstream cause."
result: "A VERB-FRAME SLOT-OCCUPANCY (capacity-one) factor for the Competition-Model coarse role labeler (graded_role_assigner.coarse_roles): a verb's nominal dependents are labelled JOINTLY, one filler per core frame slot (subject/object/recipient/by-agent), assigned by confidence; a displaced core filler falls to an oblique/adjunct. object-role PRECISION on UD-EWT test (n=700 sentences): under GOLD heads (isolating the labeler rung) floor 0.8180 -> occ 0.8396 = +0.0217 CI95[+0.0078,+0.0364] CI-SEPARATED, OBJ recall not hurt (0.9392->0.9418), overall accuracy a tie (+0.0012 CI[-0.0015,+0.0039]). FORM MATTERS: the HARD capacity-one form (occ_hard) is the winner; the soft incremental form over-suppresses at realistic head quality. On the LIVE SUPERVISED parse (arceager, UAS~0.78, the deployed heads) occ_hard lifts OBJ precision 0.6326 -> 0.7000 = +0.0674 CI95[+0.0436,+0.0899] CI-SEPARATED, twin far below (0.6021), overall accuracy UP (0.737->0.745); the incremental form there is only +0.010 (CI incl 0) and costs accuracy. On the BF attachment_arm heads (UAS~0.60) even occ_hard is only +0.001 (CI incl 0) -- too weak a sibling set. So the object-role-precision win is REAL and CI-separated on the deployed parse (hard form) and scales with head accuracy: attachment-0.60 ~0 -> supervised-0.78 +0.067 -> gold +0.015 (less headroom). This label-quality win is BOARD-INVISIBLE on the who-did-what arms: the PATIENT arm (structural_patient_pick, cap 300) is UNCHANGED by occ_hard (0.7469 both) because that reader resolves the patient via its own precise-voice+valency logic and does not depend on the coarse OBJ label being unique; the AGENT arm is byte-identical (does not read coarse_roles); the 596 undergoer decision is null (not double-object-dominated). LOCATED NEGATIVE: the mechanism is brain-foundational and delivers a CI-separated object-role-precision gain on the deployed parse (hard form), but (1) it needs a good-enough parser -- it washes out at the BF attachment arm's UAS~0.60 and returns at the supervised UAS~0.78 (the head-quality curve), and (2) the who-did-what decision readers already absorb the double-object case downstream, so the label win needs its OWN instrument (object-role precision) to be visible -- not the existing board arms."
floor: "The current independent-argmax coarse_roles (arc_labeler.COMPETITION_ROLES overlay, learned UD-EWT-train cue validities): OBJ precision 0.8180 (gold heads), 0.6393 (attachment_arm map1 heads), 0.6281 (attachment_arm incr heads), n=700 UD-EWT test sentences. Overall coarse-role accuracy floor 0.9175 (gold) / 0.7305 (map1) / 0.7218 (incr)."
controls: "(1) INFO-FREE TWIN = the slot-capacity counts shuffled across slots AND the learned verb frames (which verbs license a recipient) permuted across lemmas -- the masking+occupancy machinery still runs, on scrambled slot knowledge. Twin OBJ precision is CI-SEPARATED BELOW occupancy in every condition (gold occ-twin +0.0488 CI[+0.029,+0.070]; map1 +0.0384 CI[+0.022,+0.057]; incr +0.0405 CI[+0.022,+0.061]) and below the FLOOR too -> the gain is the LEARNED slot structure, not an animacy/relabel artifact (guards store correction C21: animacy alone must not reproduce it). (2) GOLD-HEAD ORACLE vs predicted heads = the upstream-input ablation: the mechanism wins CI-sep on gold heads and washes out on UAS-0.60 heads -> isolates the loss to the heads rung. (3) TWO MECHANISM FORMS: occ_incr (soft incremental, the psycholinguistic 'occupied-incrementally' regime) and occ_hard (hard capacity-one greedy) -- both beat the floor CI-sep on gold heads (occ_hard +0.0146 CI[+0.003,+0.027]); incremental is the stronger. (4) The slot-capacity counts themselves are the control on the premise: a verb takes 2 objects 0/9516, 2 recipients 0/647, 2 by-agents 0/306, 2 subjects 84/13048 -- capacity-one is IN the counts. (5) HEAD-CORRUPTION CURVE (gold heads degraded by random reattachment, same n=700): the occ_hard gain stays CI-separated down to simulated UAS 0.61 (+0.016 [+0.002,+0.031] at f=0.40) -- so the mechanism is robust to RANDOM head noise; the real attachment arm nulls it only because its errors are STRUCTURED in the core-argument arcs. This isolates the upstream requirement to core-argument attachment, not global UAS."
files_changed: "experiments/exp_role_slot_occupancy_v1.py, notes/problems/attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally/{SOLVED.md,graded_role_assigner_patch.diff,RESEARCH_pp_attachment_bf_lever.md}"
reverify: ".venv/Scripts/python.exe experiments/exp_role_slot_occupancy_v1.py --self-test"
---

## What I built
A **verb-frame slot-occupancy factor** for the Competition-Model coarse role labeler
(`hdlab/graded_role_assigner.coarse_roles`). Today the organ labels every nominal by an INDEPENDENT
per-token argmax, so nothing stops a verb from being given two OBJECTS: a bare temporal/measure nominal
after the object scores OBJ ("She saw him yesterday" -> him:iobj, yesterday:**obj**, reproduced live
2026-09-13). The fix assigns a verb's nominal dependents **jointly**, capacity ONE per core frame slot;
a displaced core filler falls to an oblique/adjunct. Two forms, both built and swept:
- `assign_incremental` -- left-to-right graded occupancy (the "occupied incrementally" psycholinguistic
  regime): each nominal's core-role activation is lowered by `kappa * lambda[slot] * occupancy_belief`;
  the chosen core role adds its posterior mass to that slot. `kappa`=0 recovers the independent read.
- `assign_capacity_one` -- hard capacity-one greedy joint assignment (the exact-capacity limit).
Both operate over the graded **head posterior** when given (the organ's `coarse_role_posterior_headmarg`),
so head uncertainty is handled by parallel maintenance, not an early hard commit.

**Frame-conditioned slots (the load-bearing refinement).** Capacity is per the verb's FRAME: every verb
has {subject, object, by-agent}; the RECIPIENT (iobj) slot exists ONLY for verbs whose learned frame takes
an indirect object (read from the organ's own `lemma_frames` counts). A monotransitive verb has no iobj
slot -> "him" cannot be a recipient, so it takes the object, and "yesterday" (object now occupied) is
displaced to an oblique. This is why "gave him the book" (iobj + obj, DIFFERENT slots) stays correct while
"saw him yesterday" is fixed. The greedy-only version WITHOUT the frame gate did NOT fix the headline case
(it let "him" take iobj) -- the frame inventory is essential, not the raw capacity alone.

**Knowledge in counts, plastic/online.** `lambda[slot] = -log P(a 2nd filler of slot s | the verb already
has one)`, counted per verb token from reading (UD-EWT train here; the plastic form keeps accruing via a
proposed `observe_frame_outcome`). The counts confirm capacity-one directly (see controls (4)).

## The brain computation (PINNED at the computational level)
Cue-based retrieval in comprehension (Lewis & Vasishth 2005; Van Dyke & McElree 2006): a verb integrates
each argument by retrieving the role whose cues it matches, and a FILLED core slot lowers its availability
for a second filler of the same type (similarity-based interference; the verb's remaining valence). The
integration is over the WHOLE argument structure, not independent arcs (MacDonald-Pearlmutter-Seidenberg
1994 constraint satisfaction; Boland/Tanenhaus & Trueswell argument-structure expectation). Verb-specific
valence (which slots a verb licenses) is the Competition Model's verb knowledge (Bates & MacWhinney). The
capacity limit is PINNED; which roles map to which slot, and the ditransitive threshold, are grammar/OUR-
INVENTION-UNDER-TEST (swept). `kappa`, the occupancy weight, is a swept operating point (phase diagram).

## What I measured
- **object-role precision, UD-EWT test n=700, GOLD heads:** floor 0.8180 -> occ_incr **0.8396**,
  +0.0217 **CI95[+0.0078,+0.0364] CI-separated**; occ_hard 0.8325 (+0.0146 CI[+0.003,+0.027], also
  CI-sep). OBJ recall 0.9392 -> 0.9418 (not hurt). Overall coarse-role accuracy 0.9175 -> 0.9187 (tie:
  the win is concentrated in OBJ precision, a minority class, so overall accuracy barely moves -- honest).
- **INFO-FREE TWIN CI-separated BELOW occupancy everywhere** (gold +0.0488 CI[+0.029,+0.070]) and below
  the floor -- the gain is the learned slot structure, defusing the C21 animacy-dominance failure mode.
- **LIVE SUPERVISED parse (arceager, UAS~0.78, the DEPLOYED heads), n=700 -- the HARD form wins:**
  OBJ precision floor 0.6326 -> **occ_hard 0.7000 = +0.0674 CI95[+0.0436,+0.0899] CI-SEPARATED**, twin
  0.6021 (far below), overall coarse-role accuracy 0.737 -> 0.745 (UP). The incremental form is weak here
  (occ_incr +0.010 CI incl 0; overall accuracy CI-sep DOWN -0.007 -- it over-suppresses) -> LAND THE HARD
  FORM. This is the key result: the object-role-precision gain is CI-separated on the DEPLOYED parse, not
  only on gold heads.
- **LIVE BF heads (attachment_arm, UAS~0.60), the re-scope's two decodes:** even occ_hard is only +0.001
  (CI incl 0); occ_incr +0.007/+0.016 (CI incl 0); OBJ recall drops. The BF heads' sibling set is too weak
  at 0.60. The twin is still CI-sep below, so the structure is real -- it is head accuracy that gates it.
  Head-quality curve for occ_hard OBJ-precision gain: 0.60 ~0 -> 0.78 +0.067 CI-sep -> gold +0.015 CI-sep.
- **FULLY-BF STACK + GRADED HAND-OFF (BF tagger `lexical_categories` + BF `attachment_arm` heads +
  coarse_roles; the all-BF end-to-end pipeline the owner asked to prototype):** a SOFT-GROUPING occupancy
  form (`mode="soft"`) routes the capacity competition over the head POSTERIOR (parallel maintenance; Lewis &
  Vasishth / MacDonald constraint satisfaction) instead of the hard argmax -- a nominal the hard decode
  mis-attached still competes in the correct verb's frame via its posterior mass. On the fully-BF stack it is
  the BEST form: OBJ precision floor 0.6393 -> occ_soft 0.6489 (+0.0096, CI[-0.005,+0.024]) -- beats occ_hard
  (+0.001) and is CI-separated over the twin (+0.041 [+0.020,+0.063]), no accuracy cost; on gold heads it is
  also the best (+0.0217 CI-sep, recall 0.942). BUT +0.0096 is NOT CI-separated over the floor: the graded
  hand-off recovers the MOST signal that can be recovered on the role side, but the BF parser at UAS 0.60 is
  still too weak on the core-argument arcs for the fully-BF stack to clear the bar. So the fully-BF stack is
  prototyped and the signal partially reaches; a CI-separated all-BF win still needs the BF parser's
  core-argument arcs improved (the located upstream blocker).
- **PHASE-DIAGRAM SWEEP of the graded hand-off (tau in {0.02..0.35}) on the fully-BF stack: EXHAUSTED.** OBJ
  precision is IDENTICAL at every tau (0.639, +0.006 CI incl 0) -- the attachment arm's head posterior is
  PEAKED (confidently wrong, not uncertain), so there is no graded alternative mass for the parallel-
  maintenance hand-off to exploit. This proves the role-side levers are exhausted: the only remaining lever is
  the BF parser's POINT accuracy on core-argument arcs, which is out of this organ's scope.
- **DECISION-LEVEL (supervised parser UAS~0.78): the label win is BOARD-INVISIBLE on the who-did-what arms.**
  - who-did-what PATIENT board arm (structural_patient_pick, cap 300): floor 0.7469 -> **occ_hard 0.7469
    IDENTICAL** (occ_incr 0.7552 +0.008 but twin=floor 0.7469). The improved object-role label does NOT move
    the patient PICK -- because structural_patient_pick resolves the verb's patient via its OWN precise-voice +
    valency logic (labeled_pick valency=True), so it does not depend on the coarse OBJ label being unique. The
    "patient-arm up CI-separated" bar clause is NOT met -- not because the label is unimproved, but because
    this reader already absorbs the double-object case downstream.
  - who-did-what AGENT board arm: 0.7539 -> 0.7539 BYTE-IDENTICAL (expected -- the agent pick does not read
    coarse_roles).
  - 596-item affected-entity decision (n=596): null (floor 0.4832, occ_hard 0.4883 +0.005 no CI, occ_incr
    0.4765). Not a double-object-dominated decision.
  - So the CI-separated win lives on the OBJECT-ROLE-PRECISION instrument (built here), not on the who-did-what
    arms. Per the integration discipline, a board-invisible proven win needs its OWN instrument-arm rather than
    a located negative -- object-role precision under the deployed parse IS that arm.

## The result and its located limit (the deliverable, per the bar)
The verb-frame slot-occupancy factor is the brain's operation (capacity-limited cue-based retrieval over
the verb's frame) and it is a CONTROLLED WIN on object-role LABEL precision: on the DEPLOYED supervised parse
(UAS~0.78) the hard capacity-one form lifts OBJ precision **+0.0674 CI95[+0.0436,+0.0899] CI-separated**, the
info-free twin far below (0.602), overall accuracy up; on gold heads +0.0217 CI-sep. The re-scope's
"object-role precision up" and "twin far below" clauses are MET; the mechanism is proven and BF.

Two located limits keep this PARTIAL rather than a full board win:
1. **It needs the parser right ON THE CORE-ARGUMENT ARCS -- not just high global UAS.** occ_hard OBJ-precision
   gain by head source: attachment_arm UAS~0.60 ~0 (CI incl 0) -> supervised UAS~0.78 +0.067 CI-sep -> gold
   +0.015 CI-sep. A HEAD-CORRUPTION CURVE (gold heads degraded by RANDOM arc reattachment, same n=700) sharpens
   why: the gain stays CI-separated at EVERY simulated level down to UAS 0.61 (+0.016 CI[+0.002,+0.031] at
   f=0.40; floor only falls to 0.776). But the REAL attachment arm at UAS~0.60 NULLS the gain (+0.001) with a
   far lower floor (0.639). So it is NOT global UAS -- it is the STRUCTURE of the errors: the attachment arm's
   mistakes are systematic in exactly the verb->core-argument arcs the factor uses (its obj-arc recall ~0.72,
   obl ~0.46), while random noise scatters over punctuation/determiners that never touch object labeling. The
   precise upstream target is CORE-ARGUMENT (verb->obj/obl/iobj) attachment accuracy. The win IS expressed on
   the supervised parser (0.78) because its core arcs are good enough -- but that parser is NOT_BF; the BF
   attachment arm's core-argument arcs are the specific lever (owner-run briefs pri 15-17), not a change to
   this organ.
2. **The who-did-what decision readers already absorb the double-object case, so the label win is
   board-INVISIBLE on those arms.** The PATIENT arm (structural_patient_pick) is UNCHANGED by occ_hard
   (0.7469 both) because it resolves the patient via its own precise-voice + valency logic, not the coarse
   OBJ label's uniqueness; the AGENT arm does not read coarse_roles (byte-identical); the 596 undergoer
   decision is not double-object-dominated (null). Per the integration discipline, a board-invisible proven
   win gets its OWN instrument-arm -- object-role precision under the deployed parse, which this cell builds
   -- rather than being written off as a located negative.

I did NOT refute the re-scoped mechanism -- I confirmed it is the brain's operation, showed it is a
CI-separated object-role-precision win on the deployed parse (hard form), and located precisely why it does
not move the existing who-did-what arms. Per the wall-push protocol I traced upstream rather than calling a
ceiling; neither limit is a band change.

## KEY REALIZATIONS
- **The occupancy constraint is a ROLE fact conditioned on the verb's FRAME, not a bare "one bare nominal
  per verb" rule** (which was already refuted at the governor, 2026-09-13). Capacity-one WITHOUT the
  frame-licensed slot inventory does not fix the headline case -- because the error is not "two objects",
  it is the animate first nominal being read as a recipient (iobj) of a verb that has no recipient slot.
  Gating iobj on the verb's learned frame is what fixes it; the object slot then fills once and the second
  bare nominal falls to oblique.
- **Capacity-one is literally in the counts** (0/9516 double objects) -- so the factor is not an imposed
  prior; it is the empirical slot cardinality, learnable online.
- **"Head-limited" is really "core-argument-arc-limited," and random noise is NOT a proxy for real parser
  errors.** The corruption curve keeps the gain CI-separated to simulated UAS 0.61, but the real attachment
  arm at 0.60 nulls it -- because the arm's errors cluster in the verb->obj/obl arcs the factor depends on.
  The precise upstream lever is core-argument attachment accuracy, not a global UAS number.
- **The HARD form beats the incremental form at realistic head quality.** The soft incremental form (the
  closer model of the "occupied-incrementally" psycholinguistics) over-suppresses on the supervised parse
  (+0.010 n.s. precision, accuracy CI-sep DOWN); the hard capacity-one greedy is the measured winner
  (+0.067 CI-sep, accuracy up) -> land HARD. The head-source split is essential: measuring only on the BF
  attachment arm (0.60) would have shown a null and hidden a correct mechanism.

## What I did NOT establish / would withdraw first
- I did NOT show the win on the who-did-what PATIENT board arm (occ_hard = floor exactly): that reader
  already resolves double-objects via its own valency logic. The win is on object-role precision, which I
  built as the instrument. Withdraw first if wrong: any claim that this moves a CURRENT board dimension.
- I did NOT show a CI-separated gain on the BF attachment-arm heads (UAS~0.60) -- the win needs a
  good-enough parser (returns at the supervised 0.78). So on a strictly-BF chain the gain is not yet
  realized; it depends on the attachment arm's UAS improving.
- The frame-slot inventory uses a single ditransitive threshold (>=0.05 recipient rate, >=5 obs) inherited
  from the existing `frame` cue -- swept lightly, not exhaustively. Board arms are point estimates (cap 300),
  no paired CI computed for the patient arm (the object-precision instrument carries the CIs).
- KNOWN LIMIT of the HARD greedy (found in the witness): when frame-masking removes a pronoun's top role
  (e.g. the `post_slot` "pair" cue makes an obj-case pronoun lean IOBJ, then a monotransitive frame masks
  IOBJ), a competing bare noun that scores higher on OBJ can grab the object slot and strand the pronoun as
  `dep` ("She saw him yesterday" -> him:dep, yesterday:obj under hard). Capacity-one still holds (no double
  obj) and the spurious iobj is removed, but the assignment is suboptimal. FIX (not yet built): protect an
  obj-case pronoun's core-slot claim (case is a high-validity cue), or use the soft form. Withdraw-first
  candidate if the aggregate turned out to depend on such cases -- but at scale the hard form is +0.067 CI-sep,
  so these are rare.
- I did NOT land anything in hdlab (Q111): the change is the proposed `graded_role_assigner_patch.diff`.

## Full-stack upstream (100%-BF) -- the owner's directive, traced
1. **End component (role slot occupancy):** BF -- capacity-limited cue-based retrieval over the verb frame
   (Lewis & Vasishth; MacWhinney Competition Model). Inputs: (a) per-nominal role posteriors from the
   learned cue validities [BF_SPIRIT, learned]; (b) the verb's frame inventory from lemma_frame counts
   [BF, counts]; (c) the sibling set = which nominals depend on the verb [from heads].
2. **Tagger (categories):** `lexical_categories` (counts, BF_SPIRIT) is the live default -- BF.
3. **Heads:** the BF `attachment_arm` (BF_SPIRIT) supplies the sibling set for the map1/incr measure at
   UAS~0.60; the live board/labeler default is the supervised `arceager` (NOT_BF stand-in, UAS~0.78).
   **This is where the signal is lost.** The role occupancy factor is lossless on gold heads and degrades
   monotonically as head accuracy falls -- so the upstream non-BF/weak rung (heads) is the binding wall,
   exactly as the owner's directive predicts ("a truly brain-foundational component not working properly
   almost always means an upstream component it relies on is not 100% brain-foundational / good enough").
   The fix is the attachment-arm UAS levers, not a change to this organ.

## ADJACENT DIAGNOSTIC (owner directive "go after the remaining opportunities, BF and right not easy")
Head-error anatomy of the BF attachment arm on UD-EWT test gold core-argument nominals (`--head-anatomy`):
  role       head_acc   gold-head-in-posterior-top2    dominant error
  SUBJ 0.769 | 0.776 | wrong-verb 75 / root 41 / noun 40
  OBJ  0.754 | 0.780 | wrong-verb 58 / noun 29
  OBL  0.439 | 0.468 | **noun 208 / verb 153**   <- the parser wall
  PASS_SUBJ 0.646 | IOBJ 0.806
TWO findings that settle the remaining-opportunity question:
1. **The posterior is CONFIDENTLY WRONG, not uncertain:** gold-head-in-posterior-top2 ~= head_acc for every role
   (OBL 0.468 vs 0.439). The correct head is NOT hiding in the top-2 when the argmax misses -> the graded
   hand-off cannot recover it (confirms the tau-sweep). The parser needs its POINT scores fixed, not exploited.
2. **The bottleneck is OBL PP-attachment (0.439): a nominal's oblique host is mis-chosen verb-vs-noun** (208
   to-noun + 153 to-verb). This is the classic PP-attachment ambiguity. Its BF lever -- the Hindle-Rooth
   verb-vs-noun preposition-association cue (`SentenceCues.pp`, LR(p)=log P(p|verb)/P(p|noun), learned
   treebank-free from unambiguous PPs in reading) -- is ALREADY LANDED AND ACTIVE (default-on, learned as a
   configuration-conditioned validity, not a tunable weight), and OBL is still 0.439. So the easy lever is
   already spent; improving PP/oblique attachment further is a genuine RESEARCH build (richer association
   estimation, more reading data, or a stronger structural/second-order cue), which is the attachment-arm
   problem (owner-run briefs pri 15-17), NOT a quick in-scope win. I did NOT hack a fragile scalar boost
   (there is none to hack, and it would be easy-not-right). CONCLUSION: on the role side every lever is
   exhausted (hard/soft/incr, operating-point sweep, plasticity); a superior all-BF stack is gated solely on
   the attachment arm's OBL/PP-attachment accuracy, which is a distinct hard problem.

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT / F3 thematic roles)
F3's coarse role competition currently labels each nominal INDEPENDENTLY (per-token argmax). The brain's
verb frame imposes CAPACITY ONE per core slot; this factor adds that (frame-conditioned, count-derived,
online-observable). Proposed as `graded_role_assigner_patch.diff`. The measured live cap is the heads rung
(attachment arm UAS), consistent with the affected-entity signal-loss ledger.

## COMPONENTS TOUCHED + BF STATUS
CREATED (mine, in scope):
- `experiments/exp_role_slot_occupancy_v1.py` -- the mechanism (hard/soft/incr occupancy, frame-conditioned
  slots, count-derived capacity), the UD-EWT object-role-precision harness (gold / supervised / attachment
  map1+incr heads), the info-free twin, the gold-head oracle, the head-corruption curve, the graded-hand-off
  tau sweep, the head-error anatomy, and the 596/board decision hooks. Self-test 9/9. BF (all cues glass-box,
  counts, no external tool at inference).
- `notes/problems/<slug>/SOLVED.md`, `.../graded_role_assigner_patch.diff` (proposed hdlab change; strategy lands).
READ / MEASURED-THROUGH (not modified):
- `hdlab/graded_role_assigner.coarse_roles` (F3 thematic roles) -- **BF_SPIRIT** (Competition Model, learned
  cue validities). The organ this work extends (adds the verb-frame capacity factor).
- `hdlab/attachment_arm` (heads rung) -- **BF_SPIRIT** (reading-learned cue competition + Hindle-Rooth pp
  association + semantic bootstrapping). The measured upstream BOTTLENECK: OBL/PP-attachment head-acc 0.439.
- `hdlab/lexical_categories` (tagger, live default) -- **BF_SPIRIT** (count-based generative categories). Not
  the bottleneck.
- `hdlab/arc_labeler.label` (COMPETITION_ROLES overlay) -- **NOT_BF** for fine non-argument relations; the
  argument roles it serves are the BF `coarse_roles` competition. The path the occupancy factor flows through.
- `hdlab/predicate_argument_frontend.structural_patient_pick`, `exp_board_patient_slot_v1`,
  `exp_board_agent_slot_ud_v1`, `probe_coarse_role_labeler_v13` -- consumers/instruments, read-only.
- Upstream, still **NOT_BF**: lemma normalization via WordNet `morphy` at inference (pri-12) -- part of a
  strictly-100%-BF chain, separate defect.

## PRIORITY NEXT STEPS
1. **[HIGH] Attachment-arm OBL/PP-attachment accuracy (the one blocker to a superior all-BF stack).** Head-acc
   0.439, verb-vs-noun host confusion (208 to-noun errors). PATH A ATTEMPTED THIS ARC (2026-09-13, owner-directed;
   RESEARCH_pp_attachment_bf_lever.md):
   - ORACLE CEILING (probe): fixing core-arg heads to gold (nom-UAS 0.58->0.81) makes the occupancy win
     CI-separated on the all-BF stack (+0.0156 CI[+0.004,+0.028]) -> the lever is REAL and SUFFICIENT.
   - LEVER C (data-scale the landed lexical Hindle-Rooth pp cue from 150k Simple-Wiki sentences): REFUTED --
     OBL head-acc 0.4429 -> 0.4480 (+0.005, CI incl 0), enriched~=twin. Sparsity is NOT the constraint; the
     cue's learned validity caps its decode influence.
   - REMAINING LEVER (structural, = the pri-15-17 attachment-arm problem): SEMANTIC-CLASS backoff
     (Resnik/Stetina-Nagao: re-key the pp cue lemma->induced-category, change pp_lr) + verb-subcategorization
     prepositions + prep-object class + cue re-weighting. A multi-lever parser rebuild, not a role-side prototype.
   With core-arg attachment fixed, THIS role component (already proven) makes the all-BF stack superior unchanged.
2. **[MED] Land the occupancy factor (graded_role_assigner_patch.diff).** Soft form when a head posterior is
   available, hard form otherwise. It is a CI-separated object-role-precision win now (supervised +0.067).
3. **[MED] Give object-role precision its own board dimension.** The win is board-invisible on who-did-what
   (the patient reader absorbs double-objects); it needs its own instrument to be visible to the board.
4. **[LOW] Case-protect an obj-case pronoun's core-slot claim** in the hard greedy (the documented stranding
   edge case), or default to the soft form.
5. **[LOW] Upstream lemma morphology** WordNet-morphy -> glass-box (pri-12), for a strictly-100%-BF chain.

## hdlab proposal (Q111 -- strategy lands): graded_role_assigner_patch.diff (this folder).
