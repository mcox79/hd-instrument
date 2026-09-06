---
problem: infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence
status: SOLVED
bar: "PASS = a glass-box OCC-appraisal inference -- a transparent, hand-auditable composition of the LIVE affect/goal/causal registers (event E appraised against character A's active goal G -> inferred emotion, reading valence [+ OCC type] off goal-conduciveness x prospect), NO external LLM at inference -- that predicts the UNSTATED emotion a competent reader attributes on a MODERN gold, with ALL of: (1) CI-separated over the strongest REAL floor (most-frequent-emotion/valence-only OR last-stated-emotion-word), gate on its upper CI bound; (2) an info-free twin LOSES CI-separated (shuffle the goal<->event binding); (3) a brain-faithful mechanism (OCC forward appraisal, OCC type from goal-status x prospect, not a lexical lookup); (4) a MODERN gold, verified. A rigorous LOCATED NEGATIVE naming the exact cause is a FULL PASS."
result: "Glass-box OCC appraisal (desirability x prospect -> OCC type + valence) over the LIVE reader's extracted affect+goal+event registers, on a constructed MODERN OCC gold (n=50, named characters, balanced 25/25 valence). TYPE task: APPRAISAL 0.940 vs strongest floor (valence-only, oracle-valence -> majority-type-of-valence) 0.440 = +0.500 CI[+0.340,+0.660]; vs last-stated-emotion-word floor 0.200 = +0.740; vs the CURRENT live substrate (baseline track_status, no prospect) 0.060 = +0.880 CI[+0.780,+0.960]. VALENCE task: 0.940 vs majority floor 0.500 = +0.440 CI[+0.260,+0.600]. LOAD-BEARING prospect subset {relief, fears_confirmed} (n=18): APPRAISAL 1.000 vs valence-only floor 0.000 and last-word floor 0.000 (+1.000; valence is PROVABLY insufficient for the OCC type). Composition control: ORACLE (gold structural variables) = 1.000 (the rule is exact). Info-free goal<->event-shuffle twin 0.220 loses (+0.720 CI[+0.560,+0.860])."
floor: "STRONGEST type floor actually run = valence-only with ORACLE valence -> majority-type-of-that-valence = 0.440 (its upper CI bound; appraisal +0.500 CI-sep above it); also most-frequent-type 0.240, last-stated-emotion-word 0.200. STRONGEST valence floor = majority-valence 0.500 (balanced), last-word 0.420. NOFIX (current live substrate) 0.060 -- the appraisal beats it +0.880 CI-sep, so the upstream generalization is the whole lever. Twin null: type-shuffle 0.220 / valence-shuffle 0.480."
controls: "(1) info-free goal<->event-shuffle TWIN (permute the (desirability,prospect) structural variables across items; class balance matched) -- LOSES CI-sep on TYPE (+0.720) and VALENCE (+0.460) -> the goal<->event BINDING is load-bearing. (2) NOFIX = the CURRENT live substrate (hdlab.goal_register.track_status, no thwart + NO prospect) -- collapses to 0.060 (right only on goal-satisfaction) -> the two upstream generalizations are the lever. (3) ORACLE (gold desirability+prospect) = 1.000 -> the OCC RULE is exact; every point of end-to-end headroom is EXTRACTION. (4) prospect-subset floors PROVABLY 0.000 (valence-only + last-word cannot separate relief from fears_confirmed -- both carry a stated FEAR word) -> the prospect branch is load-bearing. (5) DENSITY SWEEP (matched sparse gold, semantic not lexical goal->outcome cues): type acc 0.940->0.060 while ORACLE stays 1.000/1.000 -> the ceiling is EXTRACTION density, not the rule. (6) UPSTREAM NO-REGRESSION: track_status_thwart is a STRICT SUPERSET of the live track_status (0 satisfied/failed flips over 53 goals on ROC Stories + the gold; 14 active->failed additions; 0 wants() regressions). (7) EXTERNAL Social IQa feel-slice: appraisal fires on 1/23 (goal->outcome is semantic on real MC prose -> localizes the same ceiling)."
files_changed: "experiments/_occ_appraisal.py (the OCC organ: pure rule + prospect confirm/disconfirm detection + the sm.infer_emotion read-out), experiments/_occ_upstream_goal_status.py (the upstream goal-FAILURE-by-thwart generalization + agent-coref-canon + irregular-past, strict superset of hdlab.goal_register.track_status), experiments/_occ_probe.py (diagnostic + protagonist-coref helper), experiments/exp_occ_appraisal_emotion_v1.py (the measurement: arms, paired-bootstrap CIs, valence+type, prospect subset), experiments/exp_occ_upstream_no_regression_v1.py (no-regression on ROC+gold), experiments/exp_occ_social_iqa_generalization_v1.py (external modern check), experiments/exp_occ_density_sweep_v1.py (the cue-density phase cut), experiments/data/occ_appraisal_gold_v1.jsonl (dense gold, 50), experiments/data/occ_appraisal_gold_sparse_v1.jsonl (sparse gold, 50), verification/test_occ_appraisal.py (scaffold-free witness, 9/9), data/exp_occ_appraisal_emotion_v1/metrics.json, data/exp_occ_upstream_no_regression_v1/metrics.json, data/exp_occ_density_sweep_v1/metrics.json, data/exp_occ_social_iqa_generalization_v1/metrics.json, experiments/exp_occ_converse_matching_v1.py (the event<->goal ROLE-FILLER polarity layer decisive test) + experiments/data/occ_converse_probe_v1.jsonl + data/exp_occ_converse_matching_v1/metrics.json, experiments/exp_occ_realprose_corroboration_v1.py (external real-prose corroboration, located negative) + data/exp_occ_realprose_corroboration_v1/metrics.json, experiments/{exp_occ_intensity_v1.py (intensity WIN), exp_occ_social_agency_v1.py + data/occ_social_probe_v1.jsonl (social located negative), exp_occ_scene_inference_v1.py (scene-inference located negative)} + their data/*/metrics.json, notes/problems/infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence/{research_occ_appraisal_brain_mechanism_2026-09-06.md, research_walls_event_goal_matching_and_intensity_2026-09-06.md}. hdlab/ UNTOUCHED (Q111 diff in section 6)."
reverify: ".venv/Scripts/python.exe verification/test_occ_appraisal.py   # 9/9; drives the LIVE reader over the gold + recomputes the headline/floors/twin/NOFIX + the upstream strict-superset from source (re-runs NO landed cell)"
---

# The reader now INFERS the UNSTATED emotion: event-vs-goal congruence x prospect -> the felt emotion

## The one-line answer
The reader read STATED emotion, tracked GOALS + status, and logged the event stream, but never COMPOSED
event-vs-goal into the feeling the text leaves UNSAID. I built that composition -- the glass-box OCC forward
appraisal (desirability x prospect -> OCC type + valence), the exact SIBLING of the landed ToM chain (belief x
desire -> action; here EVENT x GOAL -> felt emotion) -- and proved it on a constructed MODERN OCC gold: it names
the unstated emotion 0.94 (type) / 0.94 (valence) vs a strongest floor 0.44 / 0.50, with the goal<->event twin
losing and the CURRENT substrate at 0.06. On the load-bearing prospect subset (relief vs fears-confirmed, which a
valence/last-word floor is PROVABLY 0% on -- both carry a stated FEAR word) the appraisal is 1.000. The composition
RULE is EXACT (oracle 1.000); a matched sparse-cue phase cut shows the entire remaining gap is EXTRACTION density
(event<->goal SEMANTIC matching = the meaning channel), not the appraisal.

## Section 0 -- the brain opening move (PINNED vs OUR-INVENTION)
- **PINNED -- emotion is an APPRAISAL of an event w.r.t. the agent's GOALS** (OCC: Ortony, Clore & Collins 1988;
  Scherer component-process goal-conduciveness-first; Lazarus 1991). The OCC TYPE is a structural decision over
  (a) DESIRABILITY for the goal and (b) PROSPECT (actual vs a still-prospective hoped/feared event, and did the
  outcome CONFIRM or DISCONFIRM it) -- NOT a lexical emotion lookup. The load-bearing PROSPECT branch separates
  satisfaction (actual good) from RELIEF (a feared bad DISCONFIRMED) and disappointment (a hoped good failed) from
  FEARS-CONFIRMED (a feared bad CONFIRMED). This is the exact mapping the brief pinned; I copied the computation
  (research-verified word-for-word against OCC 1988 Table 1: hope/fear = pleased/displeased about a PROSPECT;
  satisfaction/fears-confirmed = its CONFIRMATION; relief/disappointment = its DISCONFIRMATION). Lazarus 1991
  INDEPENDENTLY defines relief as "a goal-incongruent condition that changes for the better" -- a second theory
  converging on the same structure. NUANCE (Gygax et al. 2003/2004): online reading recovers general VALENCE
  automatically but the FINE discrete label (relief vs satisfaction) is more effortful/resource-dependent -- which
  is a point IN FAVOR of computing it as DELIBERATE glass-box composition rather than claiming it mirrors automatic
  reading (my two-level valence-then-type scoring reflects exactly this coarse-fast / fine-deliberate split).
- **PINNED -- Barrett constructed emotion**: core affect (valence) is CONSTRUCTED with situational knowledge into
  a discrete category. Here the "situational knowledge" that turns valence into satisfaction-vs-relief IS the goal
  STATUS + prospect the goal register + affect register + event stream already carry (vmPFC/OFC goal-value +
  amygdala appraisal; Campanella 2022 triple dissociation -- affect is a SEPARATE dimension, already PINNED).
- **PINNED -- goals carry a FAILED status that is tracked, not deleted, and a failed goal LINGERS longest**
  (probe-recognition RTs failed 1994ms < completed 2136ms < neutral 2387ms). Tightest primary sources: **Dopkins,
  Klin & Myers 1993** (JEP:LMC 19:70) + **Huitema, Dopkins, Klin & Myers 1993** (JEP:LMC 19:1053) for failed>completed;
  Lutz & Radvansky 1997 (JML 36:293) for completed>neutral; Suh & Trabasso 1993 reinstatement. And goal-outcome status
  is a STRUCTURAL PRIMITIVE, not one-of-five: Zwaan & Radvansky 1998 call the motivational+causal dimensions the
  "backbone" of the situation model; Trabasso & van den Broek 1985's episode skeleton is Goal->Attempt->OUTCOME. The
  goal register's OWN docstring pins this; its track_status implemented it only for a NEGATED goal clause, not a
  THWARTING event -- an incomplete realization of a pinned, backbone primitive. (research-verified 2026-09-06.)
- **OUR-INVENTION-UNDER-TEST (swept, labelled):** the thwart cue lexicon (failure verbs / negated head / adverse
  resultant), the prospect confirm/disconfirm cue lexicon (favorable vs adverse resolution), the fear/hope-cue
  fallback, the irregular-past map. All are register-generalizations of PINNED operations, none a new mechanism.

REUSE, not rebuild (mirrors hdlab.theory_of_mind): the appraisal COMPOSES the LIVE promoted registers --
desirability <- goal STATUS (hdlab.goal_register, generalized upstream for thwart); prospect <- STATED fear/hope
(hdlab.affect_register) + the event stream's confirm/disconfirm. It defines NO new register.

## Section 1 -- the mechanism (glass-box, hand-auditable, NO LLM)
For character A, appraise the recent event stream against A's goals + feared/hoped prospects:
1. **desirability** = does the outcome ADVANCE (+) or THWART (-) A's goal -> `g.status` (satisfied -> +, failed ->
   -), read via the upstream thwart-aware status generalization.
2. **prospect** = a stated FEAR/HOPE about a prospect (affect register) + whether the event stream CONFIRMED /
   DISCONFIRMED it (favorable vs adverse resolution / the feared event recurring).
3. **appraise(desirability, prospect) -> OCC type** (the fixed a-priori table, `_occ_appraisal.appraise`):
   `+actual->satisfaction | -actual->disappointment | +prospective->hope | -prospective->fear |
   -confirmed->fears_confirmed | -disconfirmed->relief | +confirmed->satisfaction | +disconfirmed->disappointment`.
   Valence = the type's sign. Output only where the affect register found NO stated emotion for A (fills the gap).
The RULE was authored BEFORE any gold item (the analog of theory_of_mind.forward_action); the gold was then
authored to SPAN the OCC type space, and the twin/floors/oracle are the controls that keep it non-circular.

## Section 2 -- what I measured (constructed MODERN OCC gold, n=50; floors recomputed per population)
| task | APPRAISAL | strongest floor | vs floor (paired bootstrap) | ORACLE | TWIN | NOFIX |
|---|---|---|---|---|---|---|
| TYPE | **0.940** | 0.440 (valence-only) | **+0.500 CI[+0.340,+0.660]** | 1.000 | 0.220 | 0.060 |
| TYPE vs last-word | | 0.200 | +0.740 CI[+0.620,+0.860] | | | |
| TYPE vs NOFIX | | 0.060 | **+0.880 CI[+0.780,+0.960]** | | | |
| VALENCE | **0.940** | 0.500 (majority) | **+0.440 CI[+0.260,+0.600]** | 1.000 | 0.480 | 0.060 |
| **TYPE prospect-subset** (relief+fears_confirmed, n=18) | **1.000** | 0.000 | **+1.000** | 1.000 | 0.167 | 0.000 |
- **Twins LOSE** CI-sep on both tasks (goal<->event binding load-bearing). **NOFIX** (the current live substrate)
  collapses to 0.060 -- it can only read goal-satisfaction, so it is right on nothing negative or prospective.
- **The prospect subset is the discriminator**: relief and fears_confirmed BOTH carry a stated fear word, so the
  last-stated-word floor and the valence-only floor are PROVABLY 0.000 there -- only the appraisal (feared prospect
  x confirm/disconfirm) separates them. This is the false-belief-subset analog of the ToM chain.
- **ORACLE = 1.000**: given the structural variables the composition is exact -> every point of headroom is
  EXTRACTION, not the inference rule.

## Section 3 -- the UPSTREAM brain-foundational work ("EVERY component, you and upstream, brain-foundational")
The positive control found the current substrate was INERT on everything negative/prospective: `track_status`
detects goal SATISFACTION (head recurs) but sets `failed` ONLY on a negated goal clause -- a goal THWARTED by an
adverse event stays `active` -- and there is NO prospect detection at all. Two upstream generalizations (both
register-generalizations of PINNED operations, both landable, exactly like the ToM chain's two upstream fixes):
1. **Goal-FAILURE by thwart** (`_occ_upstream_goal_status.track_status_thwart`, PINNED Lutz & Radvansky failed
   status): sets `failed` when a later event thwarts the goal (failure verb / negated head / adverse-resultant on
   the goal object). PLUS two extraction generalizations the appraisal needs on modern prose: (i) event-agent COREF
   canonicalization (an outcome clause with a PRONOUN subject -- "he passed" -- binds to the goal's named agent),
   (ii) IRREGULAR-PAST normalization ("won"->"win"). **STRICT SUPERSET, verified**: 0 satisfied/failed flips over
   53 goals on ROC Stories + the gold; 14 active->failed additions; **0 wants() regressions** (a goal that becomes
   `failed` can only REMOVE a wrong current-want, since wants() already skips failed).
2. **Prospect confirm/disconfirm** (`_occ_appraisal.detect_prospect_sign`, PINNED OCC prospect branch): reads a
   feared/hoped prospect off the affect register (+ a fear/hope-cue fallback that COMPOSES with, does not rebuild,
   the affect register -- catching the "dread"-verb the psych lexicon omits), and resolves it against the outcome
   (favorable dominates a colliding adverse cue: "no house was lost" -> relief).
These lift end-to-end TYPE extraction 0.06 (NOFIX) -> 0.94, and they are the WHOLE lever (Section 2).

## Section 4 -- performance vs a competent reader: the DENSITY PHASE CUT (the ceiling, MEASURED)
Same 50 OCC contrasts, same rule, only the goal->outcome / prospect-resolution CUE DENSITY dialed (the owner's
phase-diagram point: any dataset sparse<->dense at will). DENSE = the head verb recurs + explicit cue/emotion words;
SPARSE = the SAME outcomes via WORLD KNOWLEDGE ("stood on the top step of the podium" = won; "tail lights shrink
into the dark" = missed the train; "the doctor smiled" = the feared thing was averted), no lexical/cue anchors.

| metric | DENSE | SPARSE |
|---|---|---|
| appraisal fire-rate | 0.940 | 0.140 |
| TYPE acc (end-to-end) | 0.940 | 0.060 |
| TYPE acc WHEN it fires | 1.000 | 0.429 |
| prospect-subset TYPE acc | 1.000 | 0.000 |
| **ORACLE (the RULE)** | **1.000** | **1.000** |

Density delta +0.880 CI[+0.780,+0.960]. **The RULE is density-invariant (oracle 1.000 both); the entire drop is
EXTRACTION** -- when the goal->outcome link is SEMANTIC (converse verbs, world knowledge) not lexical, the glass-box
extractor ABSTAINS. So the ceiling is event<->goal SEMANTIC matching = **the meaning channel (Phase-1)**, itemized:
- The DENSE end-to-end 0.94 has 3 residuals -- all satisfaction realized by a CONVERSE/CAUSATIVE event ("wanted to
  sell" -> "a collector bought it"; "land the internship" -> "the studio offered her the place") -- the head
  doesn't recur, so status stays active. The SAME gap, at scale, is the sparse collapse.
- COREF binding of outcome pronouns is held constant with single-protagonist gold coref (the KNOWN 87%-loss coref
  bottleneck the affect register already measured, a SEPARATE filed problem, not this appraisal).

## Section 5 -- the located sub-negatives, RESEARCH-DRILLED (each a control + a fully-drilled wall)
- **event<->goal MATCHING is the dominant ceiling -- and it DECOMPOSES (research 2026-09-06, 4 convergent
  literatures; `research_walls_...md`).** It is NOT a meaning-STRENGTH problem: I evaluated the LIVE hub
  `hdlab.bridging_inference` and it is **POLARITY-BLIND** (rel(sell,buy)=0.29 but rel(win,lose)=0.26 too -- high
  relatedness, OPPOSITE outcome), so similarity CANNOT sign satisfy-vs-thwart. The faithful mechanism (Cruse
  converseness; FrameNet Perspective_on; Talmy force dynamics; Trabasso causal-network; Jara-Ettinger naive-utility;
  Gratch-Marsella EMA) is a ROLE-FILLER / STATE match -- "who ends up in the goal-holder's valued role" -- a
  SEPARABLE structural layer, NOT Phase-1. **I BUILT + MEASURED it** (`exp_occ_converse_matching_v1.py`, n=12
  converse gold): a converse/antonym/beneficiary role-filler layer lifts baseline 0.417 -> **0.833 (+0.417)**, fire
  0.50->0.92, the goal<->event-shuffle twin LOSES (0.333). So the CLOSED-CLASS converse/perspective slice is a real
  buildable win (default-off; does not touch the headline). The RESIDUAL is DISTINCT and open-ended: ~10/12 of the
  SPARSE gold's failures are SCENE-INFERENCE ("stood on the podium" = won; "tail lights shrank into the dark" =
  missed) -- a Talmy force-dynamic / Schank-script world-knowledge layer, the genuine meaning-channel-adjacent
  next-problem. (This CORRECTS a first-pass framing that called the whole wall "Phase-1-gated"; only the
  scene-inference half is.)
- **emotion INTENSITY needs a NEW organ, not the N400 channel (research-drilled).** I probed adding OCC intensity
  (unexpectedness) via the reader's forward-prediction surprisal and MEASURED it INERT: the N400 channel is
  argument-level P(word|context) and is INVARIANT to the discourse expectation ("certain to pass...failed" ==
  "expected to fail...failed", surprisal 1.007 both). The literature (Kumar et al. 2023: event boundaries track
  BAYESIAN belief-shift surprise not lexical surprisal; Schultz reward-PE; Mellers decision affect theory) says
  intensity needs a DISCOURSE-LEVEL belief-vs-outcome comparison -- a distinct organ (stance-marker belief-state +
  base-rate prior + outcome-vs-belief surprise). CAVEAT (OCC's OWN audit, Frijda/Ortony/Sonnemans/Clore 1992):
  unexpectedness is SECONDARY to goal-IMPORTANCE -- so a faithful intensity = importance + unexpectedness, never
  surprise alone. A next-problem, deliberately NOT hacked with the wrong (argument-level) signal.
- **`sm.causal_links` does NOT attribute the goal->outcome relation** (it fires on connective/mental causation, e.g.
  "wanted->catch" mental_bridge, not "doors shut -> thwarts catch-the-train"). So the pinned causal-attribution path
  is itself gated by the same event<->goal matching wall -- my cue/role-filler heuristic was not bypassing an
  available signal.
- **Social IQa is not an OCC instrument**: on its feel-slice (unstated + goal-cue + scorable, n=23) the appraisal
  FIRES on 1/23 -- SIQa's goal->outcome relations are semantic ("hoped to get it" / "Aubrey gave it to the
  friend"), the same matching gap. This is a located negative on the EXTERNAL instrument + a second measurement of
  the same ceiling, not a weakness of the appraisal.
- **Prospect resolution needs negation scope**, not a cue bag: the collisions ("no X was lost" = relief; "confirmed
  ... safe" = relief) are handled by favorable-dominance, but a general solution is comprehension, not a lexicon.

## Section 6 -- FOR STRATEGY (proposed hdlab landing -- Q111, you own it, witnessed)
All additive; mirrors `_read_tom_action` / `_read_affect` (default-off read-out, lazy, byte-identical off vs on).
0. **Land the upstream goal-FAILURE generalization** into `hdlab/goal_register.track_status` (the strict superset
   in `_occ_upstream_goal_status.track_status_thwart`: thwart branch + event-agent coref-canon + irregular-past).
   Witness: the no-regression cell (0 satisfied/failed flips, 0 wants() regressions) + a board goal-QA no-regress.
1. **Promote `_occ_appraisal.py` -> `hdlab/occ_appraisal.py`** (stdlib+hdlab only already) and add a default-off
   `infer_emotion(char[, t])` read-out on `SituationReader` composing the LIVE affect/goal/event registers, FILLING
   the gap only where the affect register found NO stated emotion for the char (never overwrites a stated feeling).
   Witness: `verification/test_occ_appraisal.py` + a pure-hdlab landing witness (other dimensions byte-identical).
2. **Add a board OCC-appraisal arm** (unstated-emotion valence + type on a modern OCC set) -- a NEW instrument-arm
   (this capability is board-invisible today: no dimension scores inferred emotion).

## Section 7 -- ADJACENT COMPONENTS (fidelity + optimization -> next problems; walls RESEARCH-DRILLED)
- **event<->goal ROLE-FILLER matching (the appraisal's dominant ceiling)** -- research-drilled + PART-BUILT. NOT a
  distributional-similarity problem (`bridging_inference` is polarity-blind). Faithful = a converse-perspective
  lexicon (FrameNet Perspective_on + WordNet antonymy, closed-class, free) + a role-filler/beneficiary match --
  a SEPARABLE structural layer, measured +0.417 recovery here (`exp_occ_converse_matching_v1.py`, default-off).
  FILE AS: promote the role-filler layer (converse-satisfy / antonym-thwart / beneficiary-dispossess) into the
  landed goal-status tracker. The OPEN residual = a Talmy force-dynamic / Schank-script SCENE-INFERENCE layer
  ("stood on the podium" = won) -- a distinct, bigger, meaning-channel-adjacent problem. HIGH.
- **emotion INTENSITY (a NEW organ)** -- research-drilled. OCC likelihood/unexpectedness is a DISCOURSE-level
  belief-vs-outcome surprise (Kumar 2023 Bayesian belief-shift, NOT the argument-level N400 -- measured inert),
  combined with goal-IMPORTANCE (Frijda/Ortony 1992: unexpectedness is secondary). A clean glass-box next-problem
  (stance-marker belief-state + base-rate prior + outcome-vs-belief surprise + a goal-importance term). MEDIUM-HIGH.
- **goal register status granularity** -- now thwart-aware (this work), but failure-by-adverse-event still relies on
  a cue lexicon; a meaning-channel thwart detector is the upgrade.
- **the affect register's fear extraction** -- the psych lexicon omits "dread" (the fallback covers it here); a
  small gap to fold back into `hdlab.affect_register`.
- **social OCC types** (anger/gratitude/pity via agency+deservingness) -- the causal network carries the agent;
  a clean next extension once event<->goal matching is stronger.

## KEY REALIZATIONS (the enabling moves)
1. **RELIEF is the load-bearing discriminator, and it is the false-belief-subset analog.** A relief item literally
   contains a FEAR word, so every emotion-word-reading floor predicts fear/negative and is provably WRONG; only the
   appraisal (feared prospect + DISCONFIRMING outcome -> positive relief) is right. Designing the gold around the
   relief-vs-fears_confirmed pair made the whole result sharp -- the same move as leading the ToM chain with the
   floor-0.000 false-belief subset.
2. **The current substrate was inert for a boringly specific reason** -- `track_status` sets `failed` only on a
   NEGATED GOAL CLAUSE, never on a THWARTING EVENT, and there was no prospect detection. Both fixes are
   register-generalizations of PINNED operations (Lutz-Radvansky failed status; OCC prospect), provably additive
   (strict superset, 0 wants() regression) -- "every component brain-foundational" meant completing the goal
   register's own pinned status field, not inventing mechanism. (Identical shape to the ToM chain's two upstream fixes.)
3. **The phase cut separates the rule from the reading.** Dialing cue-density sparse<->dense holds the appraisal
   RULE at oracle 1.000 while the end-to-end falls 0.94->0.06 -- so the ceiling is EXTRACTION density (event<->goal
   semantic matching = the meaning channel), MEASURED, not asserted. bridging_inference is directionally-correct but
   POLARITY-BLIND (win~lose as related as sell~buy), which is exactly why it cannot yet close the gap.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- Tier-6 affect/appraisal; strategy to fold)
The OCC-appraisal INFERENCE that composes the built affect + goal + event registers into an UNSTATED emotion was
ABSENT (the affect register's own located negative, and the deferred consumer named in the 2026-09-05 causal
mental-bridge integration: "affect_register -> its OCC-appraisal inferred-emotion channel"). It is now DEMONSTRATED
as a glass-box forward OCC appraisal (PINNED: Ortony/Clore/Collins prospect-based emotions; Scherer
goal-conduciveness; Barrett core-affect-plus-conceptualization; Lutz-Radvansky failed status), measured on a MODERN
OCC gold: TYPE +0.500 CI-sep over the strongest floor, prospect subset +1.000 over provably-0 valence floors,
goal<->event twin loses, composition exact with oracle. **NEW MEASURED DEVIATION (the fidelity gap crossed):** the
goal register's `track_status` was THWART-BLIND (satisfaction-only + negated-clause failure) -> generalized to a
strict-superset failure-by-thwart tracker (0 regression). **NEW MEASURED CEILING:** event<->goal SEMANTIC matching
is the appraisal's bound (density phase cut: oracle density-invariant 1.000, end-to-end 0.94->0.06 sparse). RESEARCH-
DRILLED (2026-09-06): this wall is NOT the distributional meaning channel (`bridging_inference` is POLARITY-BLIND:
rel(sell,buy)~=rel(win,lose)) -- it DECOMPOSES into (a) a converse/perspective ROLE-FILLER layer (FrameNet
Perspective_on + WordNet antonymy), a SEPARABLE structural layer BUILT + measured here (+0.417 recovery, twin loses),
and (b) an open-ended Talmy force-dynamic / script SCENE-INFERENCE residual (the meaning-channel-adjacent next
problem). A SECOND wall: emotion INTENSITY needs a discourse-level belief-vs-outcome surprise organ (Kumar 2023),
NOT the argument-level N400 (measured inert), combined with goal-importance (Frijda/Ortony 1992). This fills part of
the Tier-6 AFFECT-GOALS-SOCIAL fidelity gap (previously un-fidelity-scored): the appraisal COMPUTATION is now scored
and PINNED, and the two ceilings are localized with buildable brain-faithful mechanisms.

## Section 8 -- what I did NOT establish (and would withdraw first)
- The headline gold is CONSTRUCTED (by me), not externally authored. WITHDRAW FIRST if wrong: I mitigate with the
  info-free twin (loses), decorrelated + oracle-valence floors, the a-priori-fixed rule, extraction through the
  REAL reader (0.94 with honest converse-verb misses), and the density phase cut -- but a purely self-authored gold
  is weaker than an external one, and NO external MODERN OCC-typed goal-outcome-emotion set exists on disk (Social
  IQa is too noisy -- measured: 1/23 fire, free-text non-emotional answers). A next step is to acquire/annotate one
  (e.g. Rashkin 2018 Story-Commonsense Plutchik labels over ROCStories, pre-authorized). I ATTEMPTED an external
  real-prose corroboration (`exp_occ_realprose_corroboration_v1.py`): over ~5000 ROC Stories, where the goal branch
  fires (BLIND to any emotion word) AND the text separately states an emotion, does the appraised valence agree with
  the stated valence? Result (overlap n=92): agreement 0.576 -- BEATS the char-shuffle twin (+0.087, a weak real
  signal) but DOES NOT beat the majority-valence floor 0.630. LOCATED NEGATIVE: real prose does NOT isolate the
  goal->emotion relation (the stated emotion frequently has a DIFFERENT cause than the tracked outcome -- a confound,
  not an appraisal failure) and the goal branch fires only ~8% (extraction sparsity). So a clean real-prose
  validation needs the emotion CAUSALLY LINKED to the outcome -- the SAME event<->goal/causal-attribution wall. The
  controlled headline stands (there the outcome IS the goal-relevant cause, twin loses, floors decorrelated); the
  uncontrolled real-prose number is honestly at floor.
- The prospect-subset +1.000 vs 0.000 is on n=18 (9 relief + 9 fears_confirmed); the effect is categorical (valence
  cannot name the type) but the n is small -- the CLAIM is the categorical separation, not a precise margin.
- I did NOT wire event<->goal semantic matching (bridging_inference is polarity-blind + thin) -- shipping it would
  lower fidelity; it is a filed Phase-1 next-problem, not part of this result.
- COREF of outcome pronouns is held constant with single-protagonist gold coref (the separate 87%-loss coref
  problem); the LIVE reader's coref would cap the experiencer binding, exactly as it caps the affect register.

## TLDR (plain English)
When you read a story you feel with the characters even when the text never says how they feel -- the thrill of a
goal won, the sting of one blocked, the dread of a feared thing, and the flood of relief when the feared thing does
not happen. Our reader already read feelings the text states outright and tracked what each character wants; it
never put those together to sense the UNSAID feeling. I built that step and tested it on 50 modern test stories: it
names the right unstated feeling about 94% of the time, versus about 20-44% for readers that just guess the most
common feeling or echo the last feeling-word, and a scrambled version that ties the wrong outcome to the wrong goal
loses badly. The hardest and most telling case -- relief -- it gets right every time, where those simple baselines
get it wrong every time (the story SAYS "terrified", but once the feared thing is averted the real feeling is
relief). The reasoning itself is exact; the one limit is READING: when the story shows an outcome through everyday
knowledge ("she stood on the top step of the podium" means she won) rather than plain words, our reader can't yet
connect it to the goal -- and I measured exactly that by making an easy and a hard version of the same 50 stories.
That missing piece is the same world-knowledge/"meaning" component the project has already identified as its next
big lever. Two small, safe upstream fixes (noticing when a goal is BLOCKED, not just met; noticing when a feared
thing did or didn't happen) are what made it work, and neither breaks anything else.

## QUESTIONS
None.

## NEXT STEPS
(1) Land the upstream goal-FAILURE-by-thwart generalization into `hdlab/goal_register.track_status` (strict
superset, 0 wants() regression) + the default-off `sm.infer_emotion` read-out (Section 6). (2) Add a board
OCC-appraisal arm (unstated-emotion valence+type) -- board-invisible today. (3) Promote the ROLE-FILLER event<->goal
matcher (converse-satisfy / antonym-thwart / beneficiary-dispossess -- built + measured +0.417, twin loses) as the
polarity layer on the goal-status tracker; then the SCENE-INFERENCE (Talmy force-dynamic / script) residual as its
own problem. (4) Build the emotion-INTENSITY organ (discourse-level belief-vs-outcome surprise + goal-importance --
research-drilled; NOT the argument-level N400). (5) Acquire an external modern OCC/emotion-attribution gold (Rashkin
2018 over ROCStories) to corroborate the constructed headline. (6) Fold the AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md.

## Section 9 -- FURTHER EFFICIENCIES / BRAIN-FOUNDATIONAL UPGRADES EVALUATED (owner asked; deepening pass)
Asked "any other efficiencies or brain-foundational upgrades?", I evaluated the adjacent levers and drilled every
wall (owner: "do the right things, not the cheap things"):
- **Consume `sm.causal_links` for desirability** -- EVALUATED, not a lever: it fires on connective/mental causation,
  not the goal->outcome relation (empty on these items). Not a bypassed signal.
- **Emotion INTENSITY via the N400 surprisal channel** -- EVALUATED + MEASURED INERT (argument-level, invariant to
  discourse expectation). Research-drilled -> needs a distinct discourse-belief organ (Section 5/7), NOT a patch.
- **Event<->goal ROLE-FILLER matching** -- research-drilled + BUILT (the right way: role-filler/beneficiary, seeded
  from WordNet antonymy + the closed-class converse set, NOT verb-pair-fitted; proper goal<->event twin). Measured
  +0.417 recovery on the converse slice; the scene-inference residual is a distinct next-problem. Default-off, so
  the headline is untouched.
- **Social OCC types (anger/gratitude via agency+deservingness)** -- the causal network carries the event AGENT; the
  tractable slice (other-agent-caused outcome) is buildable, but full fidelity (blameworthiness/deservingness) needs
  norm knowledge -> a filed next-problem, not a cheap now-win.

### Section 9a -- the three specced next-problems PROTOTYPED (owner asked; each with a can-fail floor + info-free twin)
1. **INTENSITY (CLEAN WIN)** -- `exp_occ_intensity_v1.py`. The RIGHT mechanism (research): DISCOURSE belief-vs-outcome
   surprise + goal-IMPORTANCE (primary, Frijda/Ortony 1992), NOT the argument-level N400. On 10 minimal pairs (same
   OCC type, mild vs intense): intensity(intense) > intensity(mild) = **1.000** vs 0.5 floor, cue-shuffle twin
   collapses to 0.20. Importance (stakes cues) is solid; surprise (belief-vs-outcome, negation/conflict-aware stance
   extraction) works. CAVEAT: stance-marker extraction on real prose is coverage-limited (the same extraction wall).
   -> the strongest of the three; ready to spec as an organ.
2. **SOCIAL / ATTRIBUTION (anger/gratitude) (LOCATED NEGATIVE -- rule sound, extraction walled)** --
   `exp_occ_social_agency_v1.py` (n=18). The socialize RULE is EXACT (oracle 1.000: satisfaction/disappointment +
   OTHER agency -> gratitude/anger), and the agency DETECTOR works (all social items tagged other-caused). But
   end-to-end is 0.167 because the GOAL BRANCH does not fire: gratitude needs goal-satisfaction BY ANOTHER AGENT for
   the beneficiary ("Tom paid the rent FOR her" -- the same-agent rule blocks it), and anger's antecedent is usually
   an IMPLICIT goal / violated investment ("saved the seat", "prepared the report" -- no explicit want to extract).
   pride/shame OMITTED (need a norms/praiseworthiness representation). WALL (research-drilled, see §9b).
3. **SCENE-INFERENCE (LOCATED NEGATIVE -- confirms the Phase-1 residual)** -- `exp_occ_scene_inference_v1.py` (n=22
   sparse goal cases). A GENERAL, non-circular Talmy force-dynamic MOTION template (arrival->success, departure->
   thwart) recovers only ~1/22 (+0.045) -- because 18/22 sparse failures are RESULT-STATE world knowledge ("podium"
   = won, "keys in hand" = bought, "register of attorneys" = passed). A result-state lexicon fitted to those would be
   CIRCULAR, so it is deliberately NOT built; its size (18/22) is the MEASURED genuine meaning-channel (Phase-1)
   residual. This is the "right not cheap" outcome: refuse the circular hack, report the residual.
