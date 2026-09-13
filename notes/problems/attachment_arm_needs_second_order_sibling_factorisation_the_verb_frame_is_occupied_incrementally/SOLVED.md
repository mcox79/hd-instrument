---
problem: attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally
status: PARTIAL
bar: "patient-arm score up CI-separated over the current read, agent not down, object-role precision up, twin (shuffled slot counts) far below, witness green -- or a numbered located negative that names the upstream cause."
result: "A VERB-FRAME SLOT-OCCUPANCY (capacity-one) factor for the Competition-Model coarse role labeler (graded_role_assigner.coarse_roles): a verb's nominal dependents are labelled JOINTLY, one filler per core frame slot (subject/object/recipient/by-agent), assigned by confidence; a displaced core filler falls to an oblique/adjunct. object-role PRECISION on UD-EWT test (n=700 sentences): under GOLD heads (isolating the labeler rung) floor 0.8180 -> occ 0.8396 = +0.0217 CI95[+0.0078,+0.0364] CI-SEPARATED, OBJ recall not hurt (0.9392->0.9418), overall accuracy a tie (+0.0012 CI[-0.0015,+0.0039]). Under the LIVE BF heads (attachment_arm, UAS~0.60) the OBJ-precision gain is NOT CI-separated (map1 +0.0068 CI[-0.008,+0.021]; incr +0.0161 CI[-0.006,+0.037]) and OBJ recall drops -- the gain WASHES OUT because a wrong sibling set (from UAS-0.60 heads) fires the capacity constraint on the wrong group. On the DEPLOYED DECISIONS (supervised parser UAS~0.78) there is NO CONTROLLED gain: the 596-item affected-entity decision is null (floor 0.4832, occ_incr 0.4765, occ_hard 0.4883) and the who-did-what PATIENT board arm change (0.7364->0.7500) is reproduced EXACTLY by the info-free twin (not the learned structure); the AGENT arm is byte-identical (not down). LOCATED NEGATIVE: the mechanism is brain-foundational and proven correct on the labeler's own metric when its inputs are correct, but its downstream payoff is capped by (1) the HEADS rung (wrong sibling set at UAS<1) and (2) decision instruments not sensitive to double-object/temporal-NP ambiguity -- matching the ledger's own decomposition (the labeler is a clean rung; its signal is lost in the heads/tagger above it)."
floor: "The current independent-argmax coarse_roles (arc_labeler.COMPETITION_ROLES overlay, learned UD-EWT-train cue validities): OBJ precision 0.8180 (gold heads), 0.6393 (attachment_arm map1 heads), 0.6281 (attachment_arm incr heads), n=700 UD-EWT test sentences. Overall coarse-role accuracy floor 0.9175 (gold) / 0.7305 (map1) / 0.7218 (incr)."
controls: "(1) INFO-FREE TWIN = the slot-capacity counts shuffled across slots AND the learned verb frames (which verbs license a recipient) permuted across lemmas -- the masking+occupancy machinery still runs, on scrambled slot knowledge. Twin OBJ precision is CI-SEPARATED BELOW occupancy in every condition (gold occ-twin +0.0488 CI[+0.029,+0.070]; map1 +0.0384 CI[+0.022,+0.057]; incr +0.0405 CI[+0.022,+0.061]) and below the FLOOR too -> the gain is the LEARNED slot structure, not an animacy/relabel artifact (guards store correction C21: animacy alone must not reproduce it). (2) GOLD-HEAD ORACLE vs predicted heads = the upstream-input ablation: the mechanism wins CI-sep on gold heads and washes out on UAS-0.60 heads -> isolates the loss to the heads rung. (3) TWO MECHANISM FORMS: occ_incr (soft incremental, the psycholinguistic 'occupied-incrementally' regime) and occ_hard (hard capacity-one greedy) -- both beat the floor CI-sep on gold heads (occ_hard +0.0146 CI[+0.003,+0.027]); incremental is the stronger. (4) The slot-capacity counts themselves are the control on the premise: a verb takes 2 objects 0/9516, 2 recipients 0/647, 2 by-agents 0/306, 2 subjects 84/13048 -- capacity-one is IN the counts."
files_changed: "experiments/exp_role_slot_occupancy_v1.py, notes/problems/attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally/{SOLVED.md,graded_role_assigner_patch.diff}"
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
- **LIVE BF heads (attachment_arm, UAS~0.60), the re-scope's two decodes:** OBJ precision gain is NOT
  CI-separated (map1 +0.0068 CI[-0.008,+0.021]; incr +0.0161 CI[-0.006,+0.037]); OBJ recall DROPS (map1
  0.638->0.609; incr 0.675->0.632); overall accuracy a slight tie-to-down (~-0.003). The twin is still
  CI-sep below, so the mechanism's structure is real -- it is the WRONG SIBLING SET from UAS-0.60 heads
  that washes out the net gain.
- **DECISION-LEVEL (supervised parser UAS~0.78): NO CONTROLLED GAIN.**
  - 596-item affected-entity decision (probe v13 machinery, n=596): floor 0.4832; occ_incr 0.4765 (-0.0067);
    occ_hard 0.4883 (+0.0050); twin 0.4765 = occ_incr EXACTLY. Null, and the twin match (below) shows it is
    not the learned structure.
  - who-did-what PATIENT board arm (structural_patient_pick, cap 250): floor 0.7364 -> occ_incr 0.7500
    (+0.0136) -- BUT the info-free twin ALSO scores 0.7500 (identical), so the change is NOT attributable to
    the learned capacity structure; no CI computed at this n. The "patient-arm up CI-separated" bar clause is
    NOT met.
  - who-did-what AGENT board arm (cap 250): 0.7363 -> 0.7363 BYTE-IDENTICAL (agent not down; expected -- the
    agent pick does not read coarse_roles).
  - WHY the decision twin matches occ_incr exactly: every core-slot lambda is large (obj 9.85, iobj 7.17,
    byagent 6.42, subj 5.04), so the soft penalty acts near-HARD under both true AND scrambled capacity; the
    596/patient items are not iobj/double-object-sensitive enough to separate them. The twin is a MEANINGFUL
    control on the label-precision metric (where it loses CI-sep, because scrambled frames misfile iobj) but
    is saturated/undiscriminating on these decision instruments.

## The located negative, with its mechanism (this is the deliverable, per the bar)
The verb-frame slot-occupancy factor is the brain's operation (capacity-limited cue-based retrieval over
the verb's frame) and it WORKS on the labeler's OWN metric: on gold heads it lifts object-role precision
CI-separated (+0.0217 [+0.008,+0.036]) with no recall or accuracy cost, and the info-free twin loses
CI-separated. But it produces NO CONTROLLED GAIN on the downstream DECISIONS as measured, for two compounding
reasons -- BOTH located:

1. **The sibling set comes from the heads rung.** The factor must know which nominals are a verb's dependents;
   that grouping is the parse. At the BF attachment arm's UAS~0.60, ~40% of arcs are wrong, so the capacity
   constraint fires on the wrong group -- object-precision gain collapses to +0.007/+0.016 (CI incl. 0) and
   recall drops. This is the SAME conclusion the affected-entity signal-loss ledger reached from the other
   direction: the coarse role labeler is a clean rung; its signal is lost in the HEADS and TAGGER above it.
2. **The decision instruments are not double-object-sensitive, and the downstream patient reader may already
   absorb the case.** Even on the BETTER supervised parse (UAS~0.78), the 596 decision is null (occ_incr
   -0.007, occ_hard +0.005) and the patient-arm change (+0.014) is exactly reproduced by the info-free twin
   -- so it is not the learned capacity structure. The number: the mechanism recovers +0.022 OBJ precision on
   gold heads, ~0 (CI incl. 0) on UAS-0.60 heads, and no twin-separated decision gain on UAS-0.78 heads.

I did NOT refute the re-scoped mechanism -- I confirmed it is the brain's operation and it is measurably
correct on its own rung, and I located precisely why it does not (yet) pay off on the deployed decisions.
Per the wall-push protocol I traced upstream rather than calling a ceiling. The way past: (a) a higher-UAS BF
heads rung (the attachment-arm levers, owner-run briefs pri 15-17) supplies a correct sibling set, after
which the proven role-occupancy factor expresses its gold-head gain; and (b) the payoff wants a decision
instrument that actually turns on double-object / temporal-NP ambiguities (object-role precision IS that
instrument -- and there, on correct heads, it already wins). Neither is a band change.

## KEY REALIZATIONS
- **The occupancy constraint is a ROLE fact conditioned on the verb's FRAME, not a bare "one bare nominal
  per verb" rule** (which was already refuted at the governor, 2026-09-13). Capacity-one WITHOUT the
  frame-licensed slot inventory does not fix the headline case -- because the error is not "two objects",
  it is the animate first nominal being read as a recipient (iobj) of a verb that has no recipient slot.
  Gating iobj on the verb's learned frame is what fixes it; the object slot then fills once and the second
  bare nominal falls to oblique.
- **Capacity-one is literally in the counts** (0/9516 double objects) -- so the factor is not an imposed
  prior; it is the empirical slot cardinality, learnable online.
- **The gold-head vs predicted-head split is the whole finding.** Measuring only on the deployment parse
  would have shown a null and hidden a correct, brain-foundational mechanism; the gold-head oracle proves
  the mechanism and points the null at the upstream heads.

## What I did NOT establish / would withdraw first
- I did NOT show a CI-separated LIVE object-precision gain on the BF attachment-arm heads -- it is
  head-limited. Withdraw first if wrong: the claim that the incremental form is meaningfully better than
  the hard form (they are close; both win only on gold heads).
- The frame-slot inventory uses a single ditransitive threshold (>=0.05 recipient rate, >=5 obs) inherited
  from the existing `frame` cue -- swept lightly, not exhaustively.
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

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT / F3 thematic roles)
F3's coarse role competition currently labels each nominal INDEPENDENTLY (per-token argmax). The brain's
verb frame imposes CAPACITY ONE per core slot; this factor adds that (frame-conditioned, count-derived,
online-observable). Proposed as `graded_role_assigner_patch.diff`. The measured live cap is the heads rung
(attachment arm UAS), consistent with the affected-entity signal-loss ledger.

## hdlab proposal (Q111 -- strategy lands): graded_role_assigner_patch.diff (this folder).
