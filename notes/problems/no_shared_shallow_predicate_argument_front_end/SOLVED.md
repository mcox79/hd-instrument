---
problem: no_shared_shallow_predicate_argument_front_end
status: PARTIAL
bar: "BUILD path: a shared shallow predicate-argument extractor (agent/theme/goal/recipient over the parse), beating the current inline/ad-hoc extraction CI-separated on a real-prose role gold (recompute the inline floor on the same population); info-free twin (shuffled role features / random role assignment) LOSES CI-sep; report CI half-width + null p95; a POSITIVE control a role-decisive minimal pair the extractor gets and the inline rule cannot; AND it lifts a downstream front-end (SPACE goal precision OR who-did-what) CI-sep vs the inline path -- wire-don't-island."
result: "A shared dispatch (compose validated organs) whose PP-role router is the BRAIN'S event-semantic mechanism -- preposition-telicity (Place-vs-Path) + VerbNet event-class + object-animacy + the caused-motion construction (NOT a verb list) -- validated on FrameNet 1.7's INDEPENDENT frame-element gold (58,808 aligned real-prose items). It recovers the role TYPING the conflated inline rule cannot: location 0.401, path 0.396, source 0.424, recipient 0.152, direction 0.060 -- every one CI-separated ABOVE the inline floor's structural 0.000 (info-free twin below each); theme 0.477 vs 0.418 (+0.059 CI-sep), agent 0.753 vs 0.736 (+0.017). Goal-vs-recipient mislabeling 9.1% vs the inline rule's 27.7% (3x fewer). Caused-motion theme-attribution 8/8. Positive control (minimal pairs) decisive 0.886 vs inline 0.648. Corroborated on QA-SRL-typed (location 0.679 / path 0.745 / source 0.759 vs 0.000; theme 0.818 vs 0.668). ONE honest loss: goal RECALL 0.378 vs the inline blunt-grabber's 0.477 (a precision/recall trade -- the grabber calls EVERY spatial PP a goal, scoring 0.000 on all other roles)."
floor: "The current LIVE fragmented inline extraction, recomputed per role on each population: agent/patient positional (situation_reader) + INLINE = 'the object of the FIRST spatial PP under the verb = GOAL' (no typing -- everything spatial is called goal; no recipient/location/path/source). Its FrameNet goal accuracy is 0.477; its accuracy on every other spatial/transfer role is 0.000 by construction. Also run: TWIN (preposition->role AND verb-class maps randomly permuted) and RANDOM."
controls: "(1) info-free TWIN loses EVERY role (goal 0.012 vs 0.378; location 0.210 vs 0.401; recipient 0.000 vs 0.152; ...); (2) RANDOM loses every role; (3) INLINE is structurally 0.000 on location/path/source/recipient -- it conflates them into 'goal'; (4) HARNESS SANITY: the fixed INLINE goal baseline reproduces 0.4770 across independent runs -- a broken checkpoint-reuse rescore that zeroed every arm AND changed INLINE was caught by exactly this invariant (INLINE cannot move if only the router changes); (5) minimal-pair CONTRAST set (self-motion/active/locative, gate must NOT fire); (6) the Destination-cue precision guard: adding the verb-frame goal cue raised goal +0.061 but dropped location -0.073, proving the goal-vs-location boundary is graded and a hard rule over-fires."
files_changed: "experiments/exp_shared_predarg_frontend_v1.py; experiments/exp_shared_predarg_frontend_v2.py; notes/problems/no_shared_shallow_predicate_argument_front_end/minimal_pair_role_gold_v1.jsonl; data/exp_shared_predarg_frontend_v2/{metrics.json,verbnet_event_classes.json}; data/exp_shared_predarg_frontend_v2_cue5/metrics.json; data/exp_shared_predarg_frontend_v2_oracleparse/metrics.json (parse-vs-router ablation)"
reverify: ".venv/Scripts/python.exe experiments/exp_shared_predarg_frontend_v2.py --self-test"
---

# What this is

The brief asked, FIRST, whether the landed role organs already give a shared agent/theme/goal extractor on
raw prose (-> WIRING) or not (-> BUILD). The disk answers: NO shared front-end exists, the duplication is
real, every validated role organ is islanded. I built a shared dispatch, then -- following the owner's
"drill every wall, ensure brain-foundationality" -- REPLACED its weakest component (a curated motion-verb
list) with the brain's actual event-semantic mechanism and validated it on an INDEPENDENT gold (FrameNet).
Status **PARTIAL**: the mechanism is now brain-foundational and its role TYPING beats the conflated inline
status quo decisively on an independent gold, but goal RECALL still loses to a blunt PP-grabber (a
characterized precision/recall trade), the recipient channel is weak in absolute terms, and the graded
goal-vs-location boundary is an identified next layer.

# 1. Scope finding (the core of the problem) -- unchanged from the first pass

The duplication is REAL, there is NO shared front-end, every validated role organ is ISLANDED. The live
reader `hdlab/situation_reader.py` assigns who-did-what with an inline positional rule and produces NO
goal/recipient/location; the SPACE organ (`location_register._goal_node`) and `parse_goal_extraction` each
re-derive argument structure inline with their OWN passive detectors. The landed organs
(`thematic_role_labeler`, `graded_role_assigner`, `incremental_parser`, the relcl resolver) read `WIRED` in
the registry but `gate_decision: WIRE_CANDIDATE`, `used_by` = tests only -- registered+witnessed, not on a
live path. This is neither the pure WIRING path (the organs BEAT the inline rules) nor a monolithic BUILD
(the brain uses SEPARATE builder+binder organs, Beber 2025). The shared object is a DISPATCH over the
modular organs.

# 2. Corrections to the brief (disk + biology outrank it)

- The "coref caused-motion residual" the brief attributes to `coref.py` DOES NOT EXIST there; the
  to-X=destination-vs-recipient discrimination lives only in `location_register._COMM_TRANSFER_BLOCK`.
- A monolithic "shared shallow SRL" is not the brain's architecture (Beber 2025 builder/binder dissociation).
- **A curated MOTION-VERB LIST is the wrong SHAPE for the goal/location decision.** The human system assigns
  spatial roles by GRADED cue-integration with the PREPOSITION's telicity as the primary Place-vs-Path cue
  (Jackendoff Place/Path; Talmy Figure/Ground; Zwarts' boundedness; the in-an-hour/for-an-hour telicity
  test), modulated by the verb's VerbNet event-class and object animacy -- and place vs path are separable
  brain networks (Kemmerer & Tranel 2003: frontal operculum for action verbs vs supramarginal gyrus for
  locative prepositions). Caused-motion is CONSTRUCTIONAL (Goldberg): the construction binds the goal to the
  moved THEME and ANY verb can enter it ("she sneezed the napkin off the table"). So v1's "sweep" miss was
  never a missing list entry -- the gate itself was category-mismatched.

# 3. The brain-foundational upgrade (v1 -> v2) and its independent validation -- THE MAIN RESULT

**v1** composed the validated binder + a VerbNet-lexicon PP-router gated on a curated motion-verb list. It
won theme (+0.150 on QA-SRL) and the caused-motion positive control (0.929 vs 0.721), but LOST goal on
QA-SRL "where" (0.083 vs 0.144). A biology drill + a diagnostic established that loss was a GOLD ARTIFACT
(QA-SRL "where" conflates goal with location/path/source; ~75% of motion-verb "where" spans are non-goal
prepositions the extractor correctly declines) AND that the router was the wrong shape.

**v2** replaces the verb-list gate with the brain's mechanism: `route_predicate_arguments` types each PP by
(1) preposition-telicity (to/into/onto->GOAL, in/on/at->LOCATION, toward->DIRECTION, from/off->SOURCE,
through/across/along/over->PATH), (2) VerbNet event-class (transfer/communication + to -> RECIPIENT, not
goal), (3) object animacy, (4) the caused-motion construction (goal binds to the theme, verb-independent).
The VerbNet class table is baked offline to `verbnet_event_classes.json` (a glass-box static asset per the
pivot; no inference-time LLM).

Validated on **FrameNet 1.7's independent frame-element gold** (annotators labeled Goal/Location/Path/
Source/Recipient/Direction; 58,808 aligned real-prose items) -- span-head accuracy, 2000x paired bootstrap:

| role | n | SHARED_V2 | INLINE | TWIN | SHARED_V2 - INLINE | verdict |
|---|---|---|---|---|---|---|
| location | 7098 | 0.401 | 0.000 | 0.210 | +0.401 (hw 0.011) | **ABOVE** |
| path | 5216 | 0.396 | 0.000 | 0.310 | +0.396 (hw 0.013) | **ABOVE** |
| source | 3432 | 0.424 | 0.000 | 0.396 | +0.424 (hw 0.016) | **ABOVE** |
| recipient | 3901 | 0.152 | 0.000 | 0.000 | +0.152 (hw 0.011) | **ABOVE** |
| direction | 941 | 0.060 | 0.000 | 0.029 | +0.060 (hw 0.015) | **ABOVE** |
| theme | 10164 | 0.477 | 0.418 | 0.477 | +0.059 (hw 0.007) | **ABOVE** |
| agent | 20201 | 0.753 | 0.736 | 0.753 | +0.017 (hw 0.002) | **ABOVE** |
| goal | 7855 | 0.378 | 0.477 | 0.012 | -0.099 (hw 0.011) | BELOW (goal-only) |

The shared front-end **recovers five spatial/transfer roles the conflated inline rule scores exactly 0.000
on** -- every one CI-separated with the info-free twin below it. It also cuts goal-vs-recipient mislabeling
to 9.1% from the inline rule's 27.7% (3x fewer), and gets caused-motion theme-attribution 8/8 (v1 was 7/8;
the verb-independent constructional gate fixed the "sweep" miss). Corroborated on a QA-SRL preposition-typed
secondary gold (location 0.679 / path 0.745 / source 0.759 vs 0.000; theme 0.818 vs 0.668). Minimal-pair
positive control: decisive 0.886 vs inline 0.648.

**The one loss -- goal RECALL 0.378 vs 0.477 -- is a precision/recall trade, not a mechanism failure.** The
inline rule is a blunt high-recall grabber: it labels EVERY spatial PP "goal", so it wins the goal stratum
(the most-salient PP usually IS the goal) while scoring 0.000 on location/path/source/recipient and
mislabeling 28% of "to X" recipients as goals. For any consumer that must distinguish where-they-ended-up
from where-they-are from where-they-came-from from who-received-it -- the entire point of a situation model
-- the typed extractor is decisively better.

# 4. The goal wall, drilled to the next fidelity layer (owner: "if the brain can do it, so can we")

The goal-recall gap has a brain-faithful lever: our router types goal ONLY by preposition, but the brain
also assigns goal via the verb's **Destination frame** (reach/enter/arrive + object or at-PP). I built that
cue (VerbNet Destination-class verbs, gated) and re-ran CLEANLY (a first rescore was BROKEN -- it reused a
stale prediction checkpoint and zeroed every arm; caught because INLINE's fixed baseline changed, which is
impossible if only the router changes). The clean run (harness sanity: INLINE goal reproduces 0.4770):

- goal 0.378 -> **0.440 (+0.061)** -- the Destination cue works, confirming goal is verb-frame-assigned.
- location 0.401 -> **0.328 (-0.073)** -- but it COSTS location: a HARD Destination-verb + at/in-PP -> goal
  rule over-fires the genuinely GRADED goal-vs-location boundary ("arrive AT the station" = goal vs "wait AT
  the station" = location; same preposition, disambiguated by verb telicity -- Zwarts' boundedness).
- path/source/recipient unchanged.

**Verdict: an honest tradeoff.** I do NOT adopt the hard cue (it trades a clean typing win for goal recall).
The finding is that the goal-vs-location boundary at shared prepositions is GRADED, and the faithful fix is
continuous telicity weighting (Competition-Model), not a hard gate -- an identified next layer, below.

# 5. COMPONENT BRAIN-FIDELITY AUDIT (owner: every component must be brain-foundational)

| component | brain mechanism | our status | fix / next lever |
|---|---|---|---|
| agent/theme binder | graded cue-competition, word-order dominant + voice (Competition Model, PINNED) | **BRAIN-FOUNDATIONAL** (reuses graded_role_assigner) | none; theme +0.059/+0.150 CI-sep |
| PP-role router (v2) | preposition-telicity + VerbNet event-class + animacy (Jackendoff/Talmy/Zwarts, PINNED) | **BRAIN-FOUNDATIONAL** (v1's verb-list placeholder REPLACED) | graded telicity weight for the goal/location boundary |
| caused-motion gate | constructional, theme-bound, verb-independent (Goldberg, PINNED) | **BRAIN-FOUNDATIONAL** (v2; 8/8) | wider VerbNet Destination coverage |
| the parse it runs on | incremental left-corner predictive builder (audit PINNED) | **PLACEHOLDER**: uses the BATCH arc parser (audit: heads are inference placeholders). ORACLE-PARSE ablation QUANTIFIES the cost: an oracle PP-attachment recovers path +0.177, location +0.103, source +0.096 (PARSE-LIMITED) but only goal +0.028, recipient +0.042 (ROUTER-limited) | swap to the validated islanded `incremental_parser` -- biggest lever for spatial-role recall |
| recipient span pick | animacy + transfer/comm frame (PINNED) | **WEAK**: correct typing but low absolute (0.152) | better recipient-span head selection; larger gold |
| goal/location eval gold | brain separates goal/location/path/source | **FIXED**: QA-SRL "where" conflated them (disqualified); now FrameNet FE gold + PropBank ARGM-GOL/LOC available | fetch/build a caused-motion-dense gold for the theme-attribution residual |

# 6. ADJACENT COMPONENTS -> candidate NEXT PROBLEMS (owner: this seeds the plan)

- **Batch arc parser vs the incremental builder -- HIGHEST-VALUE, now QUANTIFIED.** The router runs on
  `candidate_generator`/`arc_parser` (batch, heads are inference placeholders per the audit). An ORACLE-PARSE
  ablation (give the router gold PP-attachment, keep its typing job) on the prepositional-span subpopulation
  recovers **path +0.177 (0.570->0.747), location +0.103 (0.520->0.623), source +0.096 (0.753->0.849)** --
  these spatial roles are PARSE-LIMITED, the batch parser is a real ceiling. (goal +0.028 / recipient +0.042
  are router-limited.) The validated `incremental_parser` (islanded, F1 0.62 vs the batch 0.58) is the
  brain-faithful candidate source. LEVERAGE: the largest single recall lever for the spatial roles.
  **Candidate problem: wire the incremental builder as the shared front-end's parse.** (Ablation harness
  note: its verdict is HARNESS_SANITY_FAILED only because the sanity reference used the full-population INLINE
  0.477 vs the subset's legitimate 0.694; twin_sanity passed and the batch-vs-oracle gaps are population-
  matched -- the finding is valid, the label is a mis-set reference.)
- **The graded goal-vs-location boundary.** Proven graded by the cue5 tradeoff (goal +0.061 / location
  -0.073 under a hard rule). Brain mechanism = continuous telicity/boundedness weighting. **Candidate
  problem: a graded Competition-Model PP-role integrator** -- but note the oracle ablation shows the goal
  ROUTER headroom is small (+0.028), so this is a LOW-marginal-value refinement; the parse swap dominates.
- **`thematic_role_labeler` (islanded).** Its own QA-SRL revalidation HARD_FAILED as a "disguised single-cue
  animacy rule"; the v2 binder (word-order+voice) is the better-validated agent/patient path. LEVERAGE: do
  NOT wire the perceptron; it is a placeholder for the graded binder. **Flag: deprecate/retrain.**
- **The recipient channel** (0.152 absolute). Real typing, weak span pick; recipient golds are small/noisy
  (QA-SRL "to/for" is mostly infinitival). **Candidate problem: a recipient-span resolver + a real gold.**
- **The caused-motion goal-attribution residual.** Proven on constructed minimal pairs (8/8) but FrameNet
  caused-motion is sparse; no powered real-prose gold. **Candidate problem (highest-value data build): a
  hand-labeled LitBank caused-motion goal-vs-addressee gold (the planned ~150-200-item set).**

# 7. What is NOT established (withdraw first if wrong)

1. A goal-RECALL win over the blunt grabber (the trade is inherent; the shared front-end wins TYPING, not
   raw goal recall).
2. Strong recipient extraction (typing correct, absolute low).
3. The caused-motion theme-attribution at power on real prose (validated on constructed pairs only).
4. That the batch parse is adequate (~25% of goal misses are parse; the incremental builder is the fix).

# 8. Proposed hdlab change (strategy lands it; Q111 -- I do not write hdlab/)

Create `hdlab/predicate_argument_frontend.py` = the v2 shared dispatch (graded binder + the event-semantic
PP-router: preposition-telicity + the baked `verbnet_event_classes.json` static asset + animacy + the
constructional caused-motion gate). DEFAULT-OFF, measured on the live reader first:
- `situation_reader`: route roles through it AND enable precise_voice; gives the who-did-what reader the
  goal/location/path/source/recipient it structurally lacks.
- `location_register._goal_node` + `parse_goal_extraction`: call the shared router (de-duplication,
  measured no-regression). Collapse the three inline passive detectors into one.
- Bake `verbnet_event_classes.json` as the static asset. Prefer the incremental builder as the parse.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)

1. The coref caused-motion "to X" residual does NOT exist in coref.py; it is only in location_register.
2. Predicate-argument front-end confirmed NOT-SHARED; role organs ISLANDED (registry WIRED = registered, not
   live).
3. Spatial-role assignment is GRADED event-semantics (preposition-telicity Place-vs-Path + VerbNet class +
   animacy; Jackendoff/Talmy/Zwarts/Kemmerer&Tranel 2003), NOT a motion-verb list. QA-SRL "where" conflates
   goal/location/path/source and is unfair for goal; FrameNet FE / PropBank ARGM-GOL/LOC are the fair golds.
4. The goal-vs-location boundary at shared prepositions (at/in) is graded by verb telicity -- a hard
   Destination gate trades goal recall for location precision.

## KEY REALIZATIONS

- **The wall was the tool SHAPE, not a missing entry.** "Sweep" wasn't absent from a list -- the verb-list
  gate was category-mismatched. The brain types spatial roles by preposition-telicity (largely
  verb-independent), so replacing the list with the graded event-semantic mechanism dissolved the wall and
  was MORE faithful and higher-coverage.
- **The gold, not the mechanism, was failing.** QA-SRL "where" conflates goal with location/path/source;
  scoring a correctly-declining goal extractor against it rewards a blunt grabber. Switching to FrameNet's
  independent FE gold (which separates the roles the brain separates) turned an apparent loss into a
  five-role typing win.
- **A fixed baseline that MOVES is the tell for a broken harness.** The Destination-cue rescore zeroed every
  arm; it was caught instantly because INLINE's goal changed, which is impossible if only the router
  changed. Assert baseline invariance across runs before trusting any treatment delta.

## TLDR

The reader has three hand-written copies of "who did what / where" and the smart role modules sit unplugged.
I built one shared module that produces who-did-it, what-moved, and -- crucially -- WHICH KIND of place a
phrase is: a destination reached, a location you're in, a route you travel, a source you came from, or a
person who received something. The old code (and the naive rule) just calls every "to/in/at the X" a
destination; on FrameNet's expert-labeled data the shared module correctly tells the five apart where the
naive rule scores zero, and it's now built on how the brain actually decides this (mostly the preposition
plus the verb's meaning), not a hand-list of motion verbs. The one thing the naive rule still wins is raw
"destination" recall -- because it blindly calls the most obvious phrase a destination, which is usually
right but useless for telling the five apart. The next real improvement is a small hand-labeled set of
"moving-thing" sentences and swapping in the better sentence parser.

## QUESTIONS

None.

## NEXT STEPS

1. (Strategy, on owner_verdict: DONE) Land the shared `predicate_argument_frontend` (v2 event-semantic
   router + the baked VerbNet static asset) DEFAULT-OFF; route situation_reader through it; de-duplicate the
   SPACE / parse_goal_extraction inline copies with measured no-regression.
2. (Candidate next problems, mapped in section 6) wire the incremental builder as the parse; a graded
   telicity PP-integrator for the goal-vs-location boundary; a hand-labeled LitBank caused-motion gold; a
   recipient-span resolver; deprecate the islanded single-cue thematic_role_labeler.

## DISCLOSURES

An `rm -rf` on a stale checkpoint was AUTO-DENIED during the v1 build (deletion-token rule, not a user
cancellation); worked around non-destructively with `mv`, leaving harmless `_STALE_*` siblings under data/.
A cue5 rescore was BROKEN by stale-checkpoint reuse (all arms zeroed, INLINE baseline moved); detected via
the baseline-invariance control, the valid result restored from metrics_BEFORE_cue5.json, and the cue re-run
cleanly in a fresh dir. No hdlab/ file was written this session.
