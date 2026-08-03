# PRE-REG: grounded_structure_phase0_probe_v1 (2026-08-03, REVISED after fairness gate)

## Question
Does a GROUNDED, STRUCTURED representation of a goal (TARGET self/other + harm/help
VALENCE + PRIOR-BLOCK-by-target context) disambiguate the near-synonym unstated_goal
categories (REVENGE_PUNISH / SELF_DISCIPLINE / CARE_FOR_OTHERS / PROTECT_OTHERS) better than
the STRONGEST prior TEXT-ONLY methods, on the 4-item confused subset
(relinf_unstated_007/010/011/012)?

**HONEST FRAMING:** this is a DIAGNOSTIC CEILING (glass-box hand-composed CLASSIFICATION
RULE over blind features), not the shipped/earned mechanism the USER bar requires.

## FAIRNESS GATE (revision after coordinator review of the v1 draft)
The v1 draft risked answer-leakage: hand-mapping VALENCE/PRIOR-BLOCK per confused item WITH
knowledge of the correct category launders the label (the categories are literally DEFINED
by target+valence, so "ground-by-X, grade-by-X" would make the result worthless). Revised
methodology below enforces BLIND, UNIFORM, category-independent feature derivation.

### 1. NO ANSWER-LEAKAGE -- every grounded feature is derived WITHOUT the item's gold category
- **VALENCE**: a FIXED verb/word -> harm/help table applied UNIFORMLY to ALL 12 items (not
  tuned per item). Reused verbatim from `experiments/exp_situated_goal_structure_valence_v1.py`
  `HARM_WORDS`/`HELP_WORDS` -- built PRIOR to this cell, already declared "deliberately
  DISJOINT from CATEGORY_PROTOTYPES word lists" (i.e. not built from these goal-category
  labels). Full table published in metrics.
- **TARGET**: `sgv.resolve_target` -- the same declared reflexive-marker structural proxy
  used by the prior situated-structure cell, blind to category, applied uniformly.
- **PRIOR-BLOCK**: TWO variants, both reported:
  - `AUTO_BLIND` -- derived PURELY from corpus structure: item X's prior_block=True iff
    there exists an earlier item (same novel, same chapter, strictly earlier line_range)
    whose OWN blind valence=HARM and blind target=OTHER (i.e. "an earlier
    other-directed-harm incident happened in this scene", entity-linking-free, coarse,
    expected noisy -- reported honestly including its false positives).
  - `ORACLE_NARRATIVE` -- explicitly DECLARED AN ORACLE CEILING (per the coordinator's own
    instruction: "if you use gold coref [or any oracle], declare it as an oracle ceiling").
    Supplied from a real, independently-checkable STORY FACT (not from the category label):
    for relinf_unstated_007, `relinf_unstated_008` (same gold file, same novel/chapter,
    earlier line_range 3149-3150 < 3278) narrates Amy's defiant confession of burning Jo's
    manuscript -- a textual fact, not a "this-is-revenge" flag. All other items default
    False (no oracle claim made for them). This variant answers "if entity-linking existed,
    would the payoff be there" -- it is NOT claimed as today's automatic capability.

### 2. The BLIND pipeline (AUTO_BLIND prior-block + uniform valence + blind target) is
EXPECTED to fail on 007 (irony: "take care of herself" surface-reads HELP, true intent is
spiteful HARM) and possibly 011 (slap-the-Lion: surface-valence HARM but the protected party
is Toto, not the struck Lion -- beneficiary-vs-patient). Getting these right via the BLIND
arm would be suspicious and is checked explicitly per-item.

### 3. Comparator = STRONGEST prior text-only result, not a strawman
- `TEXT_ONLY_LEXICAL` = `ci.score_goal_item(...)["lex_pick"]`, reused verbatim.
- Reference: prior `SITUATED_STRUCTURE` arm (auto-lexicon valence, NO prior-block feature)
  confused_4 = 0.500 (2/4)
  MEASURED@d:/AI/hd-instrument/data/exp_situated_goal_structure_valence_v1/metrics.json:metrics_by_scope.confused_4.SITUATED_STRUCTURE_accuracy.
  `strongest_text_only_confused4 = max(LEXICAL_confused4, 0.500)`.

### 4. FIXED classification rule, pre-registered here BEFORE scoring (not reverse-engineered)
`CATEGORY_STRUCTURE[category] = (target, valence, prior_block)`:
```
REVENGE_PUNISH:    (OTHER, HARM, True)
CARE_FOR_OTHERS:   (OTHER, HELP, False)
PROTECT_OTHERS:    (OTHER, HELP, False)   # declared collision w/ CARE_FOR_OTHERS when both
                                           # are co-candidates; tie-break = cosine (below)
SELF_DISCIPLINE:   (SELF, HARM, NA)       # prior-block not applicable to self-targeted acts
<5 remaining categories>: (SELF, NA, NA)  # MANIPULATE_AVOID_WORK, SELF_PRESERVATION_ESCAPE,
                                           # CURIOSITY_EXPLORATION, COMPLY_AVOID_TROUBLE,
                                           # ESCAPE_BLAME_DECEPTION (reused from sgv's own
                                           # CATEGORY_TARGET_VALENCE table, extended with NA
                                           # prior-block)
```
Per-candidate score = sum over the 3 features of: +1 if pred==gold (both non-NA), -1 if
pred!=gold (both non-NA), 0 if either side is NA. argmax wins; ties broken by
cosine(action_text_bundle, category_prototype_bundle) (reuses `ci.text_bundle`/`bundle`,
declared not hidden).

### 5. CONTAMINATION CHECK + negative control (scrambled valence)
Per-item report states explicitly: BLIND-solvable (AUTO_BLIND arm correct) vs
needs-ORACLE (only ORACLE_NARRATIVE arm correct) vs unsolved-by-either.
**Negative control**: `GROUNDED_ORACLE_SCRAMBLED_VALENCE` = same pipeline as
`GROUNDED_ORACLE_NARRATIVE` but with the verb valence table's two classes SWAPPED
(HARM_WORDS and HELP_WORDS exchanged wholesale -- a full permutation of the fixed table,
still deterministic and category-blind, but deliberately wrong). If the grounded arm's lift
over text-only is real (coming from grounded CONTENT, not an artifact), this control's
confused_4 accuracy MUST collapse to <= strongest_text_only_confused4 (+/- 1 item
tolerance). If it does NOT collapse, the lift is not attributable to the valence content and
the result is CONTAMINATED/inconclusive.

## APPRAISAL-THEORY FRAMING (brain-foundational gate, added after 2nd coordinator review)
The classifier is not an arbitrary if-then; it is framed explicitly as an appraisal
computation (Lazarus 1991 cognitive-appraisal theory; Scherer CPM; ToM literature), the SAME
appraisal dimensions already cited as the theoretical basis in
`notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` section 2a:
- **TARGET** (self/other) = the ToM dimension (who the action is directed at).
- **VALENCE** = harm-vs-help tendency toward the target (Scherer's goal-congruence /
  Lazarus's harm-benefit appraisal).
- **PRIOR-BLOCK** = CAUSAL-ATTRIBUTION (was the agent's goal blocked, and was it
  agent-caused, by this specific target) -- Scherer's causal-attribution dimension; this is
  the appraisal feature that (per Lazarus/Scherer) turns generic harm-valence into the
  ANGER/REVENGE appraisal specifically, vs. undirected harm.
- Composition: REVENGE_PUNISH = goal-blocked-by-agent (causal-attribution=target) +
  harm-tendency-toward-that-agent (anger appraisal, Lazarus); SELF_DISCIPLINE = harm-tendency
  self-directed (no external causal-attribution needed); CARE/PROTECT = help-tendency
  toward other (no causal-attribution required, benevolent appraisal).
This is the SAME 3-of-4 Scherer CPM dimensions (goal-relevance is held constant -- all 12
items are goal-directed by construction; congruence=valence; causal-attribution=prior-block;
coping-potential is not modeled in this cheap pass, declared out of scope).

**SUPPLY-vs-EARN line (explicit):** the VALENCE TABLE and the CLASSIFICATION RULE are
SUPPLIED (hand-built, fixed, disjoint-from-labels) -- a DIAGNOSTIC CEILING, not brain-faithful
EARNING. What IS being tested brain-foundationally is the STRUCTURE/HYPOTHESIS -- that
appraisal-composition over target+valence+causal-attribution is the right SHAPE for
goal-category disambiguation -- not whether the substrate can EARN these dimensions itself
(that is Phase-1, the simulation in the audited design doc, out of scope here).

## BRAIN-FIDELITY GATE ON FAILURES
Every per-item failure (across all arms) is classified as one of:
- `BRAIN_LIKE_MISS` -- the failure mode matches a plausible HUMAN appraisal error: (a)
  IRONY-FOOLED (surface valence read literally when the true intent is sarcastic/spiteful --
  a person without full pragmatic/ToM inference on that exact line would make the same
  surface misread), or (b) PATIENT-VS-BENEFICIARY CONFUSION (the action's direct object
  reads as harmed while the true protected party is a third entity -- a documented ToM
  confound, not unique to this substrate).
- `ARCHITECTURE_ARTIFACT` -- the classifier cannot represent the needed dimension at all
  (e.g. structural collision CARE_FOR_OTHERS/PROTECT_OTHERS both mapping to identical
  (OTHER,HELP,False) with no distinguishing feature in this feature set -- a genuine
  shape-gap, not a brain-like error).
A `BRAIN_LIKE_MISS` on 007/011 is EXPECTED and HONEST, not evidence against the grounding
premise (a full-ToM/pragmatics-aware system would need to represent irony/beneficiary
tracking as ADDITIONAL earned capacities, not falsify the target+valence+causal-attribution
frame itself).

**Verdict gating:** the PREMISE verdict (PAYS / PAYS_TODAY / WEAK) is reported ONLY IF BOTH
gates hold: (1) FAIRNESS -- no answer-leakage, scrambled-valence control collapses the lift,
comparator is the strongest prior text-only result; (2) BRAIN-FOUNDATIONAL -- the composition
is the declared appraisal-theory structure (not ad-hoc) and failures are classified
BRAIN_LIKE_MISS vs ARCHITECTURE_ARTIFACT. If either gate fails on inspection, report
INCONCLUSIVE_ON_THAT_GATE rather than a premise verdict.

## Prior-work check (substrate_query.sh, per standing discipline)
Query: "grounded structure target valence prior-block revenge punish goal category
disambiguation" -> top hit cosine=0.2764 (generic WordNet "disambiguation" node). All 5 hits
< 0.30. **NONE at cosine>0.30** -- novel probe, not a rediscovery.

## Pre-registered bands
- **PREMISE_PAYS**: `GROUNDED_ORACLE_NARRATIVE` confused_4 accuracy >= 0.75 (3/4) AND beats
  `strongest_text_only_confused4` by >= 0.25 (1 item) AND the scrambled-valence control
  collapses (per Section 5) -- i.e. the payoff exists in principle once entity-linked
  prior-block is available, and it's genuinely coming from the grounded content not an
  artifact.
- **PREMISE_PAYS_TODAY** (stronger, separately reported): the same bar cleared by
  `GROUNDED_AUTO_BLIND` alone (no oracle) -- means the payoff is achievable with ZERO
  hand-supplied facts, fully automatic today.
- **PREMISE_WEAK / CONTAMINATED**: neither oracle nor scramble-collapse condition holds, OR
  the scrambled control does NOT collapse (contamination) -- rethink before any expensive
  earned-simulation build.

## Compute architecture
Sequential-CPU, n=12 items x up to 5 arms, D=256 FHRR bag-of-words cosine only (`ci.bundle`/
`text_bundle`/`cos_sim`, reused) for tie-breaks; no HD bind/unbind exercised (this is a
feature-based glass-box classifier, not the earned HD mechanism -- declared). Wall time << 10s.
Storage: no_storage.

## SCHEMA-VET fields
`cardinality_ok` (EXPECTED_N_UNITS = 12 items x 5 arms = 60, asserted); `arms_differ_verified`
(hash-test, META_RULE_AF); `final_metrics_atomicity`: tmp_replace; `except SystemExit: raise`
before `except Exception`; `crlb_floor`: n/a (fixed small-N discriminator, no capacity claim);
`calibration_check`: "default_ok_for_this_regime" (weights fixed +1/-1/0, not tuned
post-hoc); `cell_chunked`: false; `start_marker_written`/`crash_diagnostic_present`: True;
`heartbeat_present`: false (elapsed_s expected < 10s, exempt per timeout_s>=1800 threshold).

## Dispatch
Foreground-to-completion inline in `.venv`, no queue dispatch (DIAGNOSTIC ONLY).
