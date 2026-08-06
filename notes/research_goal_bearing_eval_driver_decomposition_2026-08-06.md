# research: what actually drives MET/UNMET on the goal-bearing modern eval — per-item driver decomposition

**Type:** analysis drill (no build/run). Deliverable is this note.
**Source eval:** `experiments/data/goal_bearing_modern_eval_v1.jsonl` (44 items; 36 `outcome_in_lexicon=false` OOV + 8 `outcome_in_lexicon=true` controls).
**Trigger:** `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` TOP, "COMBINED DICTIONARY+CONSEQUENCE TOOL -> HARD_FAIL + THE DEEP REFRAME" block — 5 decisive HARD_FAILs all attacked only the verb's result-pole; open question was whether "did-it-happen" (occurrence/negation/failure/achievement) is a higher-yield, more tractable lever than more verb-valence-dictionary work.

## HEADLINE

On this eval, **DID-IT-HAPPEN (occurrence/negation/failure/achievement detection) is the single largest primary-driver bucket and by far the highest-ceiling standalone lever** — 15/36 OOV items (42%) primary, up to 17/36 (47%) "could-solve" generously counted, versus verb-valence-dictionary's hard 2/36 (6%) ceiling. **The reframe hypothesis HOLDS directionally: pivot away from more dictionary work.** But it needs one correction: **GOAL-RELATION (owner-attribution + goal-congruence) is comparably large as a PRIMARY driver (13/36, 36%) and is a REQUIRED companion on roughly half of did-it-happen's own primary items** (7/15, via owner/subject mismatch) — so a bare negation/achievement scanner with no relational binding would land correctly standalone on only ~8/36 (22%), not the full 15-17. The highest-leverage next build is **did-it-happen detection wired as an INPUT SIGNAL into the existing goal-congruence/owner-binding organ**, not a standalone replacement detector. Verb-valence dictionary work stays capped at 6% and is actively counter-productive (gives the wrong answer) on at least 2 items (numeric-threshold cases where the verb reads positive but the goal's literal bar is unmet).

## Per-item table — 36 OOV items (`outcome_in_lexicon=false`)

| id | outcome_verb | gold | primary | secondary | dict-solve? | did-it-happen-solve? | justification |
|---|---|---|---|---|---|---|---|
| lw_jo_laurie_snowball | croak | met | C | B | N | N | "croak" is manner-of-speech, valence-neutral; MET hinges on whether Laurie's response satisfies Jo's acquaintance-goal, not on the verb or on bare occurrence of *an* event |
| lw_ice_rescue_amy | drag | met | C | B | N | N | goal is implicit (unstated rescue intent); "drag a rail" is neutral, only "got the child out" (not the tagged lemma) signals achievement — needs implicit-goal inference + coref (child=Amy) |
| lw_beth_piano_invite | practice | met | C | D | N | N | Mr. Laurence's indirect invitation must be related back to Beth's yearning-for-piano goal through an intervening pragmatic bridge (invitation not addressed to Beth) |
| lw_beth_slippers_piano_gift | give | met | C | D | N | N | zero lexical overlap between goal-content (slippers/thank) and outcome-content (piano/letter) — pure bridging inference, no verb or occurrence signal carries it |
| lw_jo_mr_laurence_confront | admit | met | C | A | N | N | "admit" has no fixed valence (admissions can be bad); success = the SPECIFIC content admitted matches what Jo's confrontation goal wanted |
| lw_aunt_march_opposition | whisper | unmet | C | B | N | N | textbook goal-relative polarity flip — identical event ("Yes, John") is UNMET for March, MET for Meg; "whisper" itself is valence-neutral |
| lw_meg_currant_jelly | jell | unmet | B | A | N | Y | "wouldn't jell" — clean negation of the domain achievement-verb; a dictionary without negation-handling misreads MET |
| lw_jo_editor_dashwood | take | met | D | C | N | N | "take" is polysemous/neutral; requires WSD to business-sense "accept for publication" before any goal-relation check applies |
| lw_laurie_proposal_rejected | refuse | unmet | D | B | N | N | no literal "refuse" token in text at all — resolution is stated only via Jo's dialogue ("I can't... it would be a lie"), needs dialogue-entailment |
| lw_laurie_flower_table_amy | buy | met | B | D | N | Y | goal literally says "make them buy" and outcome literally has "bought up the bouquets" — direct unnegated goal-verb recurrence; owner-attribution (Amy absent from resolving clause) is a separate secondary issue |
| agg_anne_liniment_cake_ch21 | spoil | unmet | D | A | N | N | "spoil" never appears; negativity is inferred purely from commonsense (liniment in cake = disaster) — no lexical or negation signal present |
| agg_matthew_puffed_sleeves_dress_ch25 | like | met | C | D | N | N | Matthew's goal (please Anne) is verified only relationally, through a third party's (Anne's) reaction — "like" is Anne's word, not about Matthew directly |
| agg_anne_avonlea_school_gilbert_sacrifice_ch38 | give | met | C | D | N | N | "given the school" is instrumental to the real goal (stay with Marilla) — needs bridging inference from means to end, plus recency-trap owner resolution (Gilbert acts, Anne's goal resolves) |
| agg_anne_hair_dye_green_ch27 | turn | unmet | C | — | N | N | valence carried entirely by the RESULT ADJECTIVE (green vs. desired raven black) vs. the verb — flagship case for typed-result-state-vs-goal-target comparison |
| agg_anne_concert_recitation_encore_ch33 | encore | met | A | C | Y | Y | being encored is an intrinsically strong achievement marker for a performance goal — one of only 2 items where a (rare, domain-specific) verb-valence entry cleanly settles it |
| agg_anne_diana_bosom_friend_ch12 | agree | met | A | C | Y | Y | "agree" directly answers a yes/no request ("can you be my friend?") with an affirmative-response verb — clean, unnegated, minimal owner ambiguity |
| agg_anne_avery_scholarship_gilbert_medal_ch36 | win | met | D | C | N | N | text stages an explicit FALSE negative ("so she had failed") that must be overridden by a later correction ("winner of the Avery") — a naive negation-scan stops at the wrong (earlier, false) signal |
| agg_gilbert_pond_rescue_friendship_plea_ch28 | befriend | unmet | B | — | N | Y | unambiguous double negation ("never... and I don't want to be") — clean did-it-happen case |
| agg_anne_pudding_sauce_mouse_ch16 | ruin | unmet | B | D | N | Y | "I meant to cover it... but I forgot" — explicit failure-of-intended-action marker; mouse-in-sauce detail is corroborating commonsense, not load-bearing |
| agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17 | relent | unmet | B | — | N | Y | "hasn't relented" — explicit negation, confirmed by nonverbal headshake |
| ts_tom_whitewash_fence | whitewash | met | D | C | N | N | Tom's real goal (escape the chore) is never stated via a desiderative verb at all — must be inferred from famous reverse-psychology world-knowledge; "whitewash" occurring says nothing about whether TOM specifically benefited |
| ts_becky_anatomy_book_confession | whip | met | C | — | N | N | polarity-inversion: "whip" is intrinsically negative, but WHO receives it (Tom, not Becky) determines whose goal is met — pure goal-owner-relational reasoning |
| ts_tom_sugar_theft | rap | unmet | D | A | N | N | "got his knuckles rapped" is an idiomatic negative-consequence phrase; failure of the theft itself is inferred via commonsense (punishment implies being caught), not stated |
| ts_tom_wish_free_potter | flee | met | D | C | N | N | connecting "Joe fled" to "Potter goes free" requires courtroom/narrative-logic world-knowledge not present in the local sentence |
| woz_dorothy_kansas_wish | carry | met | B | A | N | Y | outcome text nearly restates the goal verbatim ("carry me back to Kansas"), affirmed, unnegated — direct goal-verb match |
| woz_scarecrow_brains | give | met | B | — | N | Y | goal says "give me brains", outcome says "I have given you... brains" — literal unnegated goal-verb recurrence, cleanest case in the set |
| woz_tin_woodman_heart | put | met | B | — | N | Y | same pattern: "give me a heart" -> "now you have a heart", direct fulfillment restated |
| woz_lion_courage_granted | drink | met | C | D | N | N | "drink" has no inherent tie to courage; success is confirmed only via the Lion's own dialogue ("Full of courage"), not the tagged lemma |
| woz_lion_courage_denied | have | unmet | B | — | N | Y | "I shall never have courage" — explicit negation directly on the goal-object |
| alice_beautiful_garden | find | met | B | — | N | Y | near-verbatim restatement of the goal ("that beautiful garden" repeated), affirmed, unnegated |
| race_chen_situps | improve | unmet | C | — | N | N | **decisive counter-example**: "improve" is intrinsically positive and WOULD mislead a dictionary to MET; gold is UNMET only because 30 < the stated 35-threshold — pure numeric goal-relation |
| race_german_dog | come | unmet | B | D | N | Y | final instance "never came back" is a clean negation, but the item's real difficulty is NOT extrapolating from the repeated prior MET pattern ("German was back again" xN) — occurrence-detection must read to the true final state |
| race_davey_wiffle | curve | met | B | D | N | Y* | "all the balls failed, EXCEPT the one..." — exception-clause scoping; a naive negation-scanner that stops at "failed" gets this WRONG; also owner-mismatch (dad's goal, Davey's outcome) |
| onestop_malala | go | met | B | D | N | Y | "she goes to school every day" directly and affirmatively restates "trying to get an education"; embedded double-negative ("they failed to silence her") is corroborating, not load-bearing |
| onestop_carle_madeinfrance | be | unmet | C | — | N | N | **decisive counter-example**: "96.9%... given a medal" is a strong surface-POSITIVE distractor; gold is UNMET only against the goal's strict 100%/"entirely possible" bar — numeric goal-relation, dict and did-it-happen both actively misled |
| onestop_hunt_crowdfunding | make | met | B | D | N | Y | final numeric achievement ("made 400,000 pounds") is unnegated and decisive, but only if the detector reads past the earlier explicit sub-attempt failure ("tried... but it's slow and difficult") — multi-attempt goal-persistence tracking |
| onestop_limal_dating | find | met | B | D | N | Y | "finally found love" directly restates "wanted to find love", but only if the detector tracks past the interim "without success" — same two-stage pattern as crowdfunding |

\* marked Y with caveat: correct only if the detector performs exception-clause scope resolution, not naive first-negation-wins scanning.

## Controls — 8 `outcome_in_lexicon=true` items (noted separately, per instructions)

| id | outcome_verb | gold | what actually decides it | dict-alone verdict |
|---|---|---|---|---|
| lw_jo_wanted_forgive_amy | forgive | unmet | negation ("couldn't quite forgive yet") | **WRONG** (dict says positive -> MET) |
| lw_jo_story_prize | win | met | clean, unnegated achievement verb | correct |
| agg_gilbert_porch_apology_ch15 | forgive | unmet | negation ("never forgive") + owner mismatch (Anne speaks, Gilbert is goal-owner) | **WRONG** |
| agg_anne_picnic_wish_ch14 | punish | unmet | clean, unnegated negative-valence verb applied to the goal-owner | correct |
| agg_anne_avery_scholarship_gilbert_medal_ch36 | win | met | staged false-negative ("she had failed") must be overridden by later correction; naive dict+recency reads it as Gilbert's win only | **WRONG** if read at first occurrence |
| ts_potter_failed_escape | escape | unmet | negation ("wanted to... but couldn't") — explicitly built as the lexicon-fails-under-negation control | **WRONG** |
| race_tim_rescue | reach | met | clean, unnegated achievement verb, direct goal match | correct |
| onestop_skydiver | break | met | clean, unnegated achievement verb | correct |

**Half of the in-lexicon controls (4/8) are traps where a pure dictionary lookup gets the WRONG answer** despite the verb being in-vocabulary — negation and owner-attribution defeat it just as often as OOV does. This is an independent confirmation, on the *easiest* possible subset, that verb-valence-dictionary work has a hard ceiling well under 100% even before touching the OOV problem.

## Distribution (36 OOV items, primary driver)

| driver | count | % | met | unmet |
|---|---|---|---|---|
| A — verb-pole | 2 | 5.6% | 2 | 0 |
| B — did-it-happen | 15 | 41.7% | 9 | 6 |
| C — goal-relation | 13 | 36.1% | 9 | 4 |
| D — other/composite | 6 | 16.7% | 3 | 3 |
| **total** | **36** | **100%** | **23** | **13** |

Secondary-driver footprint (where a lever is required as companion, not primary): C appears as secondary on 5 more items (10, 19, 20, 25, 29); D-type owner/discourse attribution appears as secondary on 12 items (4 of which already have C primary). Net: a goal-congruence-class organ (C, relational binding, owner attribution, threshold comparison) is **load-bearing (primary or required companion) on 25/36 items (69%)** even though it is the *sole* primary driver on only 13/36 (36%).

## Ceiling estimate per approach (36 OOV items)

**1. Perfect verb-valence dictionary, alone (no negation-handling, no occurrence-check, no relational binding):** ceiling = **2/36 (5.6%)** — items `agg_anne_concert_recitation_encore_ch33` and `agg_anne_diana_bosom_friend_ch12`, the only two where the verb's own sense intrinsically and unambiguously settles polarity with no negation or owner confound in play. On 2 further items (`race_chen_situps`, `onestop_carle_madeinfrance`) a positive-valence verb ("improve") or positive surface markers ("medal", "96.9%") **actively produce the WRONG answer** because the true gate is a numeric threshold the verb doesn't encode. Counting the 8 in-lexicon controls too: only 4/8 are dict-safe, so even on the *best-case* in-vocabulary subset the ceiling doesn't clear 50%.

**2. Did-it-happen detector (negation / failure / prevention / explicit-achievement scanning), alone:** generous ceiling (any item with a clean occurrence/negation signal) = **17/36 (47.2%)**. But roughly half of that count (7 of the 15 primary-B items: `lw_laurie_flower_table_amy`, `agg_anne_pudding_sauce_mouse_ch16`, `race_german_dog`, `race_davey_wiffle`, `onestop_malala`, `onestop_hunt_crowdfunding`, `onestop_limal_dating`) additionally needs owner-attribution, exception-scope parsing, or multi-attempt discourse-persistence tracking to land correctly — a *bare* negation scanner with no companion machinery would realistically land only **~8/36 (22%)** standalone (the fully clean subset: `agg_meg_currant_jelly`-style single-clause negation, `woz_*` and `alice_*` direct goal-verb restatements). Two items (`race_chen_situps`, `onestop_carle_madeinfrance`) are HARD-FAILs for this lever too — occurrence did happen, just insufficiently against a numeric bar.

**3. Goal-relation (typed outcome-state + owner-relative goal-congruence organ):** sole primary driver on **13/36 (36%)**, but load-bearing (primary or required secondary) on **25/36 (69%)** — the single largest total footprint of any lever, because it is what correctly handles goal-relative polarity flips (same event, opposite verdict per goal-owner — `lw_aunt_march_opposition`, `ts_becky_anatomy_book_confession`), owner/subject mismatches (pervasive — present as a secondary factor in a third of all items), and numeric-threshold comparisons that both other levers get flatly wrong.

**4. OTHER/composite (D):** **6/36 (17%)** need commonsense/world-knowledge inference (`agg_anne_liniment_cake_ch21` liniment-in-cake, `ts_tom_sugar_theft` rapped-knuckles-implies-caught), unstated/implicit goals requiring genre knowledge (`ts_tom_whitewash_fence` reverse psychology, `ts_tom_wish_free_potter` courtroom-logic causal chain), WSD (`lw_jo_editor_dashwood` "take"), or pure dialogue-entailment with no outcome verb present at all (`lw_laurie_proposal_rejected`). None of the three structural levers above solves these without additional machinery.

**Overlap:** did-it-happen and goal-relation are NOT competing levers on this eval — they are complementary and co-occur on a large share of items (7 of B's 15 primary items need C-class owner-attribution as a companion; 5 items where C is primary have B as a secondary occurrence-check). The two levers together (did-it-happen occurrence signal + goal-congruence/owner-binding organ) cover essentially the full B+C footprint (28/36, 78%) with only D's 6 items (17%) needing genuinely separate machinery, and 2 items (`race_chen_situps`, `onestop_carle_madeinfrance`, both already counted in C) standing as **hard proof that dictionary-only work is not just insufficient but actively wrong on numeric-threshold cases**.

## Cheap decisive test

Build the smallest possible did-it-happen detector (negation-scope + explicit-failure/achievement-marker scan over the outcome clause, reusing the existing dependency-parse/negation-scope machinery already in the substrate rather than a new parser) and wire its output as an ADDITIONAL SIGNAL into the existing goal-congruence organ (the same one diagnosed in the BACKUP doc's combined-tool HARD_FAIL) — not as a standalone replacement scorer. Run it over the same 36-item eval used here.

- **HARD-PASS:** correctly resolves at least the ~8 fully-clean B-primary items (woz/alice-class direct goal-verb restatements + single-clause negations) with NO regression on the 2 in-lexicon items already correctly handled by the existing tool, AND does not flip `race_chen_situps` / `onestop_carle_madeinfrance` to MET (i.e., does not get fooled by positive-surface-but-under-threshold cases — this is the discriminating check that the signal is being consumed by the congruence organ rather than short-circuiting it).
- **HARD-FAIL:** accuracy on the full 36-item OOV set does not clear the existing combined-tool HARD_FAIL baseline by a real margin (own baseline TBD by cell-author from the HARD_FAIL run cited in the BACKUP doc), OR the detector regresses any of the 4 in-lexicon items that were already correct, OR it flips either numeric-threshold item to a wrong answer (would indicate the occurrence signal is overriding rather than feeding the congruence check).

## Falsifiable predictions

1. **Prediction:** wiring did-it-happen as an input signal to the existing goal-congruence organ improves whole-eval accuracy by at least +15 points over the combined-dictionary+consequence-tool HARD_FAIL baseline. **HARD-FAIL if:** improvement is under +5 points or any regression occurs on previously-correct items.
2. **Prediction:** owner-attribution (subject != goal-owner resolution, i.e., reusing coreference-resolver machinery per [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]]) is a SEPARATE, comparably-sized lever from did-it-happen — wiring both together should outperform did-it-happen alone by a nontrivial margin on the 7 flagged owner-mismatch items. **HARD-FAIL if:** did-it-happen alone already resolves those 7 items correctly (would mean owner-attribution is not actually load-bearing on this eval, contrary to this analysis).
3. **Prediction:** the 2 numeric-threshold items (`race_chen_situps`, `onestop_carle_madeinfrance`) remain unsolved by did-it-happen + owner-attribution alone and require a THIRD, distinct component (quantity/threshold comparison against a goal-specified numeric target). **HARD-FAIL if:** either resolves correctly without an explicit threshold-comparison mechanism (would mean the numeric case was overfit-diagnosed here, not real).
4. **Prediction:** the 6 D-class items remain unsolved by any combination of the above three levers and require commonsense/world-knowledge or discourse-persistence machinery not yet scoped. **HARD-FAIL if:** 4 or more resolve correctly anyway (would mean this analysis over-estimated their difficulty / mis-tagged their true driver).

## Cross-thread synthesis

Directly closes the open question from `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` TOP: the 5 prior HARD_FAILs (structural-read/reward-constant/consequence-learning/dictionary/combined) all attacked driver A (verb-pole) exclusively, which this analysis shows has a hard 5.6% ceiling on the actual eval — those failures were not "almost there," they were aimed at a component that structurally cannot cover the eval's dominant failure modes. This reframes (without contradicting) `project_build_the_6yo_grounded_foundation_reading_builds_on_USER_2026-08-03` and the goal-owner-selector / outcome-valence goal-congruence organs already BUILT+WIRED per the CURRENT FOCUS banner (cert 220) — those organs are the right SHAPE (per the brain-fidelity audit, `notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md` if that ran, or the referenced synthesis doc) but have been starved of the occurrence/negation SIGNAL this analysis shows is the largest single missing input. This is consistent with, and sharpens, [[feedback_every_negative_check_missing_component_especially_learning_USER_2026-08-04]] — the missing component here is not a new organ, it is a new SIGNAL (did-it-happen) feeding an organ that already exists.

## Substrate-product implications

A user-facing "did this character get what they wanted" reading capability on real prose is currently bottlenecked NOT on vocabulary coverage (dictionary size) but on two structurally distinct, roughly co-equal capabilities: (1) recognizing whether the goal-relevant event occurred at all (negation/failure/achievement scanning — the reframe's proposed pivot, confirmed highest standalone ceiling), and (2) correctly binding an outcome to the RIGHT goal-owner and comparing it against that owner's SPECIFIC desired state, including numeric thresholds (goal-congruence — confirmed highest total load-bearing footprint). Shipping only (1) without (2) will look like a win on ~8/36 clean items and then plateau hard, misleadingly resembling "further dictionary work needed" when the actual gap is relational binding. The product-correct build order is: wire did-it-happen INTO the existing congruence organ in one step, not as a separate standalone tool to be evaluated in isolation.

## Citations (verified count)

Zero external citations — this is a closed-corpus, internal-eval analysis; every claim above is directly re-derived from `experiments/data/goal_bearing_modern_eval_v1.jsonl` (44/44 items read in full) cross-referenced against `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`. No lit-scan calibration penalty applies (no novel-synthesis P-estimate is being made; this is a factual decomposition of an on-disk eval, fully falsifiable by re-reading the same 36 rows). Per-item counts independently re-summed twice (36 = 2+15+13+6 by driver; 36 = 23+13 by polarity) to catch tabulation errors before delivery.
