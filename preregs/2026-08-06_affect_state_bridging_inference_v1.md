# Pre-registration: affect-state bridging inference (2026-08-06)

## Task / brief
Director's brief (2026-08-06): extend the validated evaluative-speech-act bridging inference
(`experiments/exp_evaluative_bridging_inference_v1.py`, commit 17dd3567b, HARD_PASS; wired to
production Tier-3 owner-selection at commit d157941c6) to a SIBLING construction: AFFECT-STATE
outcomes -- the protagonist's OWN emotion expresses the goal outcome ("Oh, how glad I am!" after
achieving a goal = goal MET; "he felt ashamed" = goal UNMET), rather than an external evaluative
speech act about the addressee's character ("you are a good boy"). Same Graesser Class-7 backward
causal-antecedent bridging pattern (valence -> goal-outcome), different construction (INTERNAL
affect predicate, first- or third-person, vs EXTERNAL evaluation of the addressee). Real-prose
blocker `mg1_frank_fishing` (`experiments/data/real_text_goal_owner_diagnostic_v1.jsonl`) contains
this exact affect phrasing ("Oh, how glad I am!").

## Prior-work check (substrate-KB, mandatory per exp_dev discipline)
`bash tools/substrate_query.sh "affect state emotion bridging inference goal outcome glad ashamed
interoceptive appraisal own affect protagonist"` -> max cosine = 0.2852 (entity='affect', a general
concept-graph node pulling from atoms/verbnet/wordnet, and a `2026-08-04_lexicon_induction_
selectional_association_v1.md` chunk about the OFC/vmPFC affect-appraisal brain structure -- neither
is this specific construction-bridging build). NONE at cosine>0.30. Genuinely novel increment, not a
rediscovery; the evaluative-bridging sibling itself scored max cosine 0.252 on its own prior-work
check the same day, so this result is consistent with that precedent.

## Mechanism (strict ADD, reuses owned organs, no new binding operator)
1. DETECT: `detect_affect_state_construction(sentence, roster)` -- TWO patterns, both hand-supplied
   POS-blind valence lexicons (SUPPLY schema, same pattern as `EVAL_POS/EVAL_NEG` in the sibling
   cell and `RESULT_VERB_CLASS`/`V2_OUTCOME_MET/_UNMET` in `hdlab/goal_typing.py`):
   - **Pattern A (third person):** a roster NAME or a gender-resolvable pronoun (he/she) immediately
     followed by a feel-verb or copula (`feels|felt|is|was`) followed within a small window by an
     AFFECT word. `is/was` chosen deliberately over `are/were` so this pattern can NEVER match a
     2nd-person "you are ADJ" address -- that is the sibling's EXTERNAL-EVALUATION construction,
     deliberately out of scope here (verified disjoint by the interference gate below, not just
     asserted).
   - **Pattern B (first person, dialogue):** the token "i" adjacent to the copula "am" (covers both
     "I am so AFFECT" and "how AFFECT I am!" word orders -- the AFFECT-word scan covers the whole
     sentence for this pattern, not just a forward window, since "how AFFECT I am" places the AFFECT
     word BEFORE "i am"). Holder resolved as the first roster name token in the sentence (the
     reporting-verb speaker attribution, e.g. "Frank cried, ...I am!" -- same sentence-scoped
     attribution shape as the sibling's mg2 "She said, ... 'You are ... Henry.'").
   `AFFECT_POS = {glad, happy, joyful, delighted, proud, pleased, thankful, merry, cheerful}`,
   `AFFECT_NEG = {sad, ashamed, sorry, miserable, disappointed, unhappy, grieved, downcast,
   sorrowful}` (exact lexicon as specified in the task brief).
2. VALUE: POS lexicon hit -> pos-affect, NEG lexicon hit -> neg-affect (lexicon lookup, NOT verb
   typing, NOT reward-PE / appraisal-sim grounding -- see Follow-ups).
3. BRIDGE: `bridge_outcome(entity, sentence, roster, register)` reuses
   `hdlab.goal_owner_select.GoalOutcomeRegister` (byte-identical, UNMODIFIED import, no new binding
   operator) -- fires ONLY if the affect-state construction's HOLDER == `entity` (the affect must be
   the GOAL-HOLDER's OWN affect, not a bystander's) AND `register.appraise(entity)["has_goal"]` is
   True. POS+has_goal -> OUTCOME_MET; NEG+has_goal -> OUTCOME_UNMET. No match / wrong holder / no
   open goal -> abstain (None), never forces a bridge. This is the critical over-fire guard: a
   BYSTANDER's affect (a non-goal-holder feels glad) must not bridge to the protagonist's goal --
   enforced structurally by the holder==entity check, tested explicitly (category BYSTANDER below).
4. STRICT-ADD GATING: identical architecture to the sibling -- LEXICAL verb-typing
   (`hdlab.goal_typing.type_goal_events`, unmodified production organ) on the outcome sentence
   FIRST; the bridge is consulted ONLY when lexical typing produced NOTHING for every candidate
   (OUTCOME_NEVER_TYPED). Existing production/sibling behavior is byte-identical whenever verb-typing
   already fires.

No production file is modified (`hdlab/goal_typing.py`, `hdlab/goal_owner_select.py` imported
read-only) and the sibling evaluative-bridging cell is imported read-only ONLY for the interference
check below (its own file is not modified either) -- `verification/run_certification.py` is
therefore NOT required for this increment.

## Instrument
Hand-authored bank, `experiments/data/affect_state_bridging_bank_v1.jsonl`, N=12 items, 4
categories: POS_MET (n=5, incl. `frank_fishing_glad` -- the "how glad I am!" first-person-dialogue
pattern modeled on real-prose `mg1_frank_fishing`'s affect phrasing), NEG_UNMET (n=3),
BYSTANDER (n=2), UNCHANGED (n=2). Zero-lexical-overlap between the goal clause and the outcome
clause is mechanically checked in self-test (content-token intersection, minus roster names and a
closed-class stopword list, must be empty) for every POS_MET/NEG_UNMET item.

**HONEST SCOPE (mandatory statement, not a caveat buried in a footnote):** this pre-reg validates the
AFFECT-STATE BRIDGING MECHANISM IN ISOLATION on a hand-authored bank. `frank_fishing_glad` is
MODELED ON `mg1_frank_fishing`'s affect phrasing, not that item verbatim, because `mg1_frank_fishing`'s
own GOAL is expressed only through a dialogue REQUEST ("would you like to go?" / "may I go?"), which
is a SEPARATE competency (dialogue-request goal recognition) this cell does not build. Passing this
pre-reg does NOT mean `mg1_frank_fishing` is solved end-to-end; it means the affect-state bridge
mechanism itself is validated, ready to compose with a future dialogue-request-goal competency.

## Arms
(a) AFFECT-BRIDGING (strict-add mechanism above) vs (b) LEXICAL-ONLY (production `type_goal_events`
verb-typing alone, no bridge step) -- (b) is expected to abstain on every POS_MET/NEG_UNMET item
(verified empirically in self-test, not just assumed, because `type_goal_events`'s Tier-2 open-vocab
verb-similarity fallback -- `_tier2_outcome_polarity_scan`, live similarity classifier, not a fixed
set -- could in principle OOV-classify one of this bank's outcome-sentence verbs against the
MET/UNMET seed pools; each item's outcome-sentence verb choice was checked against a live run of
`lexical_hits_for` before this bank was finalized, and any item where it fired was reworded).

Control (iv) SCRAMBLE: a fixed-seed cyclic shift (offset=1, asserted zero-fixed-points) over the 8
POS_MET+NEG_UNMET item ids reassigns each item's GOAL register to a DIFFERENT item's register before
bridging; all 8 item holder names are distinct, so a shuffled register never has an open goal for the
real holder -> bridging is predicted to collapse to 0/8.

**Composition gate (mandatory, not optional):** verify this new detector composes with the EXISTING
evaluative bridge with NO interference, in both directions, using the REAL other-detector (not a
re-implementation):
- `detect_affect_state_construction` run over all 13 evaluative-bridging-bank outcome sentences
  (`experiments/data/evaluative_bridging_bank_v1.jsonl`) -> must fire 0 times (predicted 0, incl. the
  one genuine lexicon-overlap case: `AFFECT_POS` and `EVAL_POS` share the token "cheerful" --
  `jack_kate_fence_bystander`'s outcome "You are a cheerful, good girl, Kate." contains it, but
  Pattern A never matches 2nd-person "you are", so no cross-fire is predicted).
- `detect_evaluative_construction` (sibling's detector, imported read-only) run over all 12
  affect-bank outcome sentences -> must fire 0 times (predicted 0; none of this bank's AFFECT words
  are `EVAL_POS`/`EVAL_NEG` members, and "cheerful" was deliberately avoided in this bank's own
  sentences to keep the check unambiguous).
- The sibling cell's own `self_test()` re-run in-process -> must still return True (proves this
  strict-ADD file caused zero regression to the existing evaluative bridge).

## Bands (declared before running)
- `zero_overlap_bridging_acc` = accuracy of arm (a) on the 8 POS_MET+NEG_UNMET items (exact dict
  match: bridge binds MET/UNMET to the gold goal-holder and nobody else), incl. `frank_fishing_glad`
  specifically correct.
- `lexical_only_acc` = accuracy of arm (b) on the same 8 items (predicted ~0.0).
- `gap` = zero_overlap_bridging_acc - lexical_only_acc.
- `valence_pos_acc` = fraction of the 5 POS_MET items bridging to MET (not UNMET).
- `valence_neg_acc` = fraction of the 3 NEG_UNMET items bridging to UNMET (not MET).
- `bystander_no_bridge_acc` = fraction of the 2 BYSTANDER items where arm (a) binds NOBODY.
- `unchanged_control_acc` = fraction of the 2 UNCHANGED items where arm (a) == arm (b) (both
  correct) AND `source=="LEXICAL"` (bridge never engaged).
- `scramble_acc` = arm (a) accuracy on the 8 POS_MET+NEG_UNMET items under the offset-1 scramble.
- `no_interference` = both interference-gate counts are 0 AND the sibling's `self_test()` returns
  True.

**HARD-PASS**: `zero_overlap_bridging_acc >= 0.85` (incl. `frank_fishing_glad` specifically correct)
AND `gap >= 0.50` AND `valence_pos_acc == 1.0` AND `valence_neg_acc == 1.0` AND
`bystander_no_bridge_acc == 1.0` AND `unchanged_control_acc == 1.0` AND `scramble_acc <= 0.15` AND
`no_interference == True`.

**HARD-FAIL**: `zero_overlap_bridging_acc < 0.85` OR `gap < 0.25` OR `bystander_no_bridge_acc < 1.0`
(over-fires: binds a non-goal-holder / bystander) OR `unchanged_control_acc < 1.0` (over-fires:
hijacks an already-verb-typed outcome) OR `valence_pos_acc < 1.0` OR `valence_neg_acc < 1.0` (wrong
valence) OR `scramble_acc > 0.15` (mechanism secretly keys off surface affect words alone, not the
goal-content link) OR `no_interference == False` (breaks the existing evaluative bridge, or the two
detectors cross-fire on each other's bank).

Anything strictly between the two bands (partial numeric shortfall, no over-fire) -> `MIDDLE_BAND`.

## Compute architecture
(a)/(b)/(c) classification: (b) sequential-CPU with justification -- rule-based, N=12-item
hand-authored bank scored with FHRR decode over d=1024, effectively instantaneous. 3 seeds x 12 items
plus the two interference scans complete in well under 1 second.

## crlb / discriminator-reachability
`crlb_n/a`: no swept capacity claim; FHRR decode of <=8 bound event-slots at d=1024 is far below any
capacity ceiling (established by the sibling cell + `goal_owner_select`/`grounded_appraisal_sim`
self-tests: decode fidelity > 0.99 at this scale). The discriminator here is a boolean
construction-detector + registry lookup, not a noise-limited decode.

## Cardinality / determinism
`EXPECTED_N_ITEMS=12` (5 POS_MET + 3 NEG_UNMET + 2 BYSTANDER + 2 UNCHANGED). `SEEDS=[0,1,2]`
(EXPECTED_N_SEEDS=3) -- deterministic given seed. `deterministic_seeding: true` (fixed integer seeds;
scramble permutation is a fixed cyclic shift, not `hash()`-derived -- PROT-023/F.5 compliant).

## Cell-template mandates
- arms_differ_verified: bridging vs lexical-only arm outputs differ (bridging arm binds all 8
  POS_MET/NEG_UNMET items, lexical-only arm binds none) -- checked in self-test.
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException).
- per-unit failure-class instrumentation: no bare except anywhere in the cell.
- cell_chunked: true (per-seed unit via tools/exp_checkpoint.py).
- HP_SCOPE: HARD-PASS/HARD-FAIL bands above apply to the aggregate (all-seeds-agree) verdict; the
  interference gate is seed-independent (pure detector composition, computed once) and is folded
  into the same aggregate verdict as a hard gate.

## Follow-ups (explicitly NOT attempted here, per task brief)
- Grounding affect-valence in reward-PE / the appraisal-sim (the interoceptive/OFC-vmPFC route per
  `notes/audit_brain_feature_acquisition_grounding_2026-08-06.md`) instead of a hand-supplied
  POS-blind lexicon -- the deeper, brain-faithful move; this increment stays lexicon-based, same
  scope discipline as the evaluative sibling.
- Wiring this bridge into production `hdlab/goal_owner_select.py` Tier-3 (mirrors d157941c6's wiring
  of the evaluative bridge) -- deferred to a future landed-VET decision, not attempted in this
  isolation-validation cell.
- `mg1_frank_fishing` end-to-end resolution needs a dialogue-request-goal-recognition competency
  (separate build).
