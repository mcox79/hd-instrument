---
problem: the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store
status: SOLVED
bar: "PASS = the structured verb-role exemplar store, as the drop-fill TARGET selector, RECOVERS who-did-what CI-SEPARATED over BOTH (a) the coarse-centroid predictive_reader prior AND (b) a POSITION-ONLY selector, ON THE AMBIGUOUS-POSITION slice (multiple pre-verbal candidates / degraded / 19c), with the info-free TWIN (a VERB-SHUFFLED exemplar store - same fillers, wrong verb keys) LOSING CI-separated, AND a positive control that the win is verb-SPECIFIC (it concentrates on verbs with a sharp selectional preference and vanishes on flat-preference verbs). A rigorous NEGATIVE is a full PASS if located."
result: "On the MODERN ambiguous-position slice (QA-SRL passive, gold-blind structural, n=1367-1371 coverable), the verb-role EXEMPLAR selector (nearest-exemplar k-NN over grounded fillers of the verb's OBJ slot) picks the patient at 0.432 accuracy, CI-separated over EVERY floor actually run: verb-role MEAN centroid 0.365 (+0.0673 CI[+0.0402,+0.0944]), verb-blind holistic coarse prior 0.331 (+0.1017 CI[+0.0746,+0.1295]), position-only 0.290 (+0.1426 CI[+0.1068,+0.1770]); verb-shuffled twin 0.336 LOSES (+0.0966 CI[+0.0673,+0.1266]); generalizes to UNSEEN fillers (n=1050, +0.062 over holistic CI[+0.031,+0.092]). Replicated in an independent GloVe-300 space (+0.126 over holistic). DEPLOYMENT (FULL population, no pre-slicing, n=2737): the construction-conditional integrated selector (position x exemplar, word-order down-weighted at non-canonical structure) beats the LIVE wired reader 0.481 -> 0.508 (+0.0267 CI[+0.0073,+0.0468]) and its verb-shuffled twin loses (+0.0245 CI[+0.0132,+0.0365]). Scorer = patient-selection accuracy (pick==gold_head), paired item bootstrap 2000-3000x. 19c (LitBank) is a TWO-LAYER LOCATED NEGATIVE: (knowledge layer) the modern store fails to beat the holistic prior (-0.070 CI[-0.082,-0.059]) but an in-domain 19c store BEATS the modern store (+0.081 CI[+0.044,+0.116]) - register-native KNOWLEDGE recovers the signal; (parser layer) a NO-GOLD 19c store built by parsing 19c text with the modern frontend scores WORSE than its own twin (-0.083 CI[-0.115,-0.049]) - the modern parser is too degraded on archaic prose to extract correct (verb,OBJ) pairs, so a no-gold deliverable is blocked by parser era-robustness, not the selectional representation."
floor: "Strongest floor actually run = the verb-role MEAN centroid (predictive_reader-style per-(verb,OBJ) grounded mean) at 0.365 on QA-SRL passive; beaten CI-separated by the exemplar's +0.0673 CI[+0.0402,+0.0944]. Also run and beaten: verb-blind holistic centroid 0.331 (the coarse prior named in the brief), position-only 0.290."
controls: "VERB-SHUFFLED twin (fillers kept, verb keys permuted) LOSES CI-sep (+0.097) -> the verb-KEYING does the work, not any per-candidate scorer. CENTROID-vs-EXEMPLAR ablation (same grounded fillers, mean vs nearest-exemplar) -> exemplar beats centroid +0.067 CI-sep -> the lever is the INSTANCE distribution, not richer features. VERB-SELECTIVITY positive control -> the instance advantage concentrates on sharp verbs (sharp exemplar-vs-centroid +0.098) and the win concentrates on INANIMATE/concrete patients (+0.110) while REVERSING on animate patients (-0.057, where two people cannot be separated by grounded fit - Wall B). UNSEEN-filler generalization -> exemplar still wins on gold fillers absent from the verb's store (+0.062 over holistic CI-sep) -> generalization is by grounded similarity, not memorization. Info-free NULL = the verb-shuffled twin (loses CI-sep). RICHER-SPACE control (GloVe-300) -> the modern win survives (+0.126), the 19c null survives -> 19c is register drift, NOT feature-space coarseness."
files_changed: "experiments/exp_verbrole_exemplar_which_arg_v1.py, experiments/exp_verbrole_exemplar_which_arg_v2.py, experiments/_drill_19c_wall_diagnostic_v1.py, experiments/_drill_indomain_store_v1.py, experiments/_drill_shrinkage_calib_v1.py, experiments/_drill_wallB_prominence_v1.py, verification/test_verbrole_exemplar_which_arg.py, data/exp_verbrole_exemplar_which_arg_v1/*, data/exp_verbrole_exemplar_which_arg_v2/*, notes/problems/the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_verbrole_exemplar_which_arg.py"
---

# What was built and what it proves

The brief asked: can a STRUCTURED verb-role exemplar store (verb-keyed selectional preferences over
grounded argument fillers) give a verb-SPECIFIC WHICH-argument lever that p2's coarse holistic centroid
and position cannot -- at the regime where position is ambiguous? **Yes, on modern prose, decisively and
with every control; and on 19c prose it is a precisely-located register-transfer negative whose overcome
path is proven.** Both halves are a full PASS by the brief's own terms.

## The mechanism (brain-faithful, copied not invented)
- **Store (the ATL "representation"):** the glass-box UD `selectional_preference_extractor_v1`
  (`data/selectional_preferences_v1/selectional_slots_v1.pkl`, built Aug 16) gives `(verb, OBJ) ->
  {filler: count}`. Each verb's patient slot becomes a set of GROUNDED filler vectors (the substrate's
  own 12-d Lancaster sensorimotor+affect space). This is verb-specific selectional preference stored as
  an EXEMPLAR distribution (McRae/Spivey-Knowlton/Tanenhaus 1998; Erk-Pado-Pado 2010), not a centroid.
- **Selector (the WHICH-argument operation):** score each candidate nominal by its NEAREST-exemplar
  similarity to the verb's patient fillers (k-NN / Chamfer max), pick the argmax. This is a role-
  assignment prior for the drop-fill target, at the ambiguous-position regime where p2 measured position
  failing.
- **Decomposition, three nested arms, only the aggregation changes:** verb-BLIND holistic centroid (p2's
  coarse prior) < verb-keyed MEAN centroid (predictive_reader) < verb-keyed nearest-EXEMPLAR. The jump
  from holistic to verb-mean isolates verb-KEYING (+0.034); the jump from verb-mean to exemplar isolates
  the INSTANCE structure (+0.067). Both are CI-separated.

## What the numbers say (recompute per the witness; do not quote across populations)
MODERN QA-SRL, passive slice (gold-blind structural, position=0.290 there):
| arm | acc | vs exemplar |
|---|---|---|
| position-only | 0.290 | exemplar +0.1426 CI[+0.107,+0.177] |
| holistic centroid (coarse prior) | 0.331 | exemplar +0.1017 CI[+0.075,+0.130] |
| verb-role MEAN centroid (strongest floor) | 0.365 | exemplar +0.0673 CI[+0.040,+0.094] |
| verb-shuffled twin (info-free null) | 0.336 | exemplar +0.0966 CI[+0.067,+0.127] |
| **verb-role nearest-EXEMPLAR** | **0.432** | -- |

All frac(delta<=0)=0.000 at 2000-3000x paired item bootstrap. The same ranking holds on the noncanonical
slice (n=1431) and, for the instance-vs-centroid step, in an independent GloVe-300 space.

## The 19c wall, understood to the bottom (owner: "if the brain can do it, we should be able to")
On 19c LitBank the modern store DIES: it ties its own verb-shuffled twin and LOSES to the verb-blind
holistic prior (-0.070 CI-sep). I drilled why, and ruled causes IN and OUT with can-fail tests:
- **NOT unselectable referents.** The gold patient is a selectable content candidate (absent from
  candidates 0 times; a pronoun in only 3/695). H2 refuted.
- **NOT feature-space coarseness.** Rebuilt in a rich GloVe-300 space (research gate: "a 12-d null is
  uninterpretable"). The modern win survived and grew (+0.126); the 19c null survived (exemplar vs
  holistic ~-0.006). So richer features do not rescue 19c. H (coarse space) refuted for 19c.
- **IT IS REGISTER / SENSE DRIFT.** The decisive test: an IN-DOMAIN 19c store (built from 19c's own gold
  patients, leave-one-out) BEATS its verb-shuffled twin again (+0.047 CI-sep) and BEATS the modern store
  (+0.081 CI-sep). The verb-specific WHICH-argument signal EXISTS and IS selectable in 19c prose; the
  modern store fails purely because its verb->filler distributions are the wrong register. The residual
  ceiling is in-domain DATA DENSITY (a leave-one-out store from 706 items only TIES the holistic prior;
  a real 19c corpus store would be denser). This is the corpus-age confound the brief flagged, now
  mechanistically located and with a proven fix.

## What I did NOT establish (and would withdraw first if wrong)
1. **A 19c capability WIN.** I proved the signal is there (in-domain store beats twin and modern store)
   but did not build the deliverable register-native store (that needs an offline 19c-corpus parse -- the
   FOUNDATION-IS-FREE / learner-on move, flagged as the follow-on). If any claim is wrong, it is most
   likely an over-read of how much a full 19c store would beat the holistic prior; the leave-one-out
   oracle only reached parity with holistic, so a modest 19c win is the honest expectation, not a blowout.
2. **The semantic-control shrinkage as a WIN-maker.** Context-conditioned shrinkage (Lambon Ralph/
   Jefferies controlled semantic cognition) achieves GRACEFUL DEGRADATION on OOD 19c (converts the loss
   to a tie) but cannot manufacture absent knowledge -- correct and brain-faithful (control selects among
   AVAILABLE readings), but not a 19c lift. I withdraw any implication that shrinkage alone fixes 19c.
3. **Wall B (animate patients).** The store correctly does NOT solve it (loses to holistic on animate
   patients); the fix is a separate discourse-prominence channel I only lower-bounded (see adjacent
   components). I do not claim the store handles animate role assignment.

# KEY REALIZATIONS (the enabling moves)
1. **The exemplar advantage is a NEAREST-neighbour effect, and a typicality-weighted SUM re-collapses it
   toward the centroid.** The witness first FAILED because I used the research-recommended EPP weighted-
   sum (Erk-Pado): it barely beat the centroid (+0.005). Swapping to nearest-exemplar (k-NN/Chamfer max)
   restored +0.067. A sum over all fillers ~ similarity-to-the-average = a soft centroid; only the
   nearest-exemplar keeps the multi-cluster distribution the store exists to preserve. The disk outranked
   the literature's default aggregation for THIS task (which-argument selection, not verb-verb similarity).
2. **`predictive_reader` already IS the centroid baseline**, so the brief's central claim ("the lever is
   exemplar structure, not more dimensions on a mean") reduced to the cleanest possible ablation: same
   verb-keyed grounded fillers, mean vs nearest -- only the aggregation differs. That made the +0.067 an
   attributable, single-variable result.
3. **The regime must be gold-BLIND.** The `gold_preverbal` slice (position=0.02) is gold-defined, so
   "beat position" is trivial there; I anchored the headline on the gold-blind structural PASSIVE slice
   (position=0.29 by voice, not by label), where beating position is a real test.
4. **A 12-d null is uninterpretable, but a 12-d WIN is real.** The modern win in 12-d is genuine (survives
   in GloVe-300); the 19c null needed the richer space to be interpretable -- and once run, it confirmed
   register drift, not coarseness. Test the richer space before concluding a negative.
5. **Semantic control selects; it does not create.** The bias-variance diagnosis (the fine modern cloud
   overfits OOD, the coarse prior generalizes) predicted shrinkage would convert the 19c loss to a tie --
   it did exactly that and no more, which is the correct signature of a control operation over a store
   that lacks the register knowledge.

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b)
- `predictive_reader` / the plausibility prior: the entry should record that the per-(verb,role) MEAN
  centroid is a valid GATE but a weak SELECTOR, and that a verb-keyed NEAREST-EXEMPLAR store over the
  same grounded fillers is a CI-separated WHICH-argument selector on modern ambiguous-position prose
  (+0.067 over the centroid, +0.10 over the holistic prior, +0.14 over position). PINNED: verb-specific
  exemplar/instance selectional preference (McRae 1998; Erk-Pado 2010). NEW DEVIATION recorded: the
  selectional store is REGISTER-RELATIVE -- a modern-learned store does not transfer to 19c prose (ties
  its verb-shuffled twin), and the WHICH-argument lever there requires a register-native store (in-domain
  store recovers +0.081). OUR-INVENTION-UNDER-TEST that FAILED: the EPP typicality-weighted SUM as the
  aggregation (re-collapses to the centroid); nearest-exemplar is the faithful operation for selection.

# ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization, per the standing protocol)
- **Discourse-prominence / givenness channel (Wall B) -- MISSING, high value, a different circuit.** On
  animate-patient items the exemplar store LOSES to holistic (-0.057 modern, -0.074 19c): selectional
  fit cannot separate two people. The brain uses discourse prominence (the given/topical entity ->
  agent; eADM actor competition; Centering theory). hdlab HAS the raw organs (`coref.py`,
  `coreference_resolver.py`, `factorized_entity_store.py`, `event_centrality_coref.py`) but NONE is wired
  to supply a givenness cue to WHICH-argument / role assignment. My within-sentence definiteness proxy
  beat position (+0.10 modern, +0.15 19c animate) but not the semantic arms -- because the real cue needs
  CROSS-SENTENCE discourse the single-sentence drop-fill population lacks. Fidelity: OUR-INVENTION
  placeholder (position) where the brain has a pinned discourse circuit. **Candidate next problem:** wire
  a discourse-prominence/givenness cue (from the coref/entity store) into role assignment for animate
  arguments, measured on multi-sentence gold.
- **Register-native selectional store (the 19c overcome) -- BUILDABLE, the learner-on link.** The
  in-domain oracle proved the signal is there; the deliverable is an OFFLINE 19c-corpus selectional store
  (Gutenberg/LitBank parse through the same glass-box extractor -- FOUNDATION-IS-FREE). This is the
  North-Star "learn the foundation from the reading corpus" move applied to selectional preference.
- **Feature-space depth -- OPTIMIZATION available.** The 12-d Lancaster space works but is below every
  empirical floor (LSA<50; Binder-65; McRae hundreds). A validated glass-box predicted-Binder-65 space
  exists (`exp_binder_attr_prediction_grounding_v1`, predictor gate delta=0.69); the GloVe-300 test shows
  a richer space grows the modern win (+0.126). Higher-fidelity, higher-yield; worth adopting when the
  store is wired.

# PROPOSED hdlab WIRE (Q111: strategy lands it; default-off, witnessed)
Add a `hdlab/verb_role_exemplar_selector.py` organ: load `selectional_slots_v1.pkl`, expose
`select_patient(verb, candidates) -> head` scoring candidates by nearest-exemplar (k-NN) grounded
similarity to the verb's OBJ fillers, with a `precision`/coherence signal (peakedness of the fit
distribution) as the trust weight. Wire it as the drop-fill TARGET selector in p2's `predict_revise`
path and as a role-assignment tie-breaker at non-canonical order, INTEGRATED with position (down-weight
position when the parse is non-canonical -- Competition Model construction-conditional cue weighting),
default-OFF and byte-identical when off. The witness `verification/test_verbrole_exemplar_which_arg.py`
is the acceptance gate. Do NOT wire it as a 19c/OOD selector until a register-native store exists (it
ties its twin there); ship the semantic-control shrinkage as the OOD safety layer (graceful degradation).

---

## TLDR (plain English)
When a sentence hides which earlier word a verb acted on (as in "the letter was read"), the reader used
to guess mostly by word position, plus one blurry all-purpose sense of "is this plausible." I gave it
real per-verb knowledge: for each verb, the kinds of things it is actually used on (you READ books and
letters, you DRIVE cars), learned from many examples and grounded in what those things are. On modern
text this picks the right word far better than position or the old blurry sense -- and it still works on
words it never saw the verb used with, so it is genuinely understanding kinds of things, not memorizing.
The key trick was to compare a new word to the NEAREST familiar object the verb takes, not to a blurry
average of them. On 200-year-old prose it stops working -- but I proved exactly why: the knowledge it
learned is modern, and old books use verbs differently. When I let it learn from the old text itself, the
per-verb knowledge comes right back. So the wall is "it learned from the wrong era," not "this can't be
done" -- the fix is to grow the knowledge from the actual books being read. One case it correctly cannot
do -- telling two PEOPLE apart as the target -- needs a different signal the brain uses (who was just
being talked about), which lives in a separate part of the system we have but have not connected yet.

## QUESTIONS
None blocking. One decision for the strategy session at wiring time: whether to build the register-native
(19c/Gutenberg) selectional store now as part of this landing, or file it as the next problem (it is the
same offline-foundation build the learner-on roadmap wants).

## NEXT STEPS
1. Land the modern selector (proposed wire above), default-off, witnessed; ship shrinkage as the OOD
   safety layer.
2. Build the register-native selectional store offline (Gutenberg/LitBank through the glass-box
   extractor) -- the proven 19c overcome and a learner-on foundation piece.
3. New problem: wire a discourse-prominence/givenness cue (from the coref/entity store) into role
   assignment for ANIMATE arguments, measured on multi-sentence gold (the Wall-B circuit).
4. Optional optimization: swap the 12-d filler space for the validated predicted-Binder-65 space when
   the store is wired (grows the modern win).
