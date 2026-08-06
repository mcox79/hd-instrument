# research: does the "did-it-happen dominant / verb-pole tiny" driver distribution generalize beyond `goal_bearing_modern_eval_v1.jsonl`?

**Type:** GENERALIZATION probe (read-only analysis, no build/run). Deliverable is this note. Per the standing rule "TEST GENERALIZATION not just the instrument."

**Trigger:** `notes/research_goal_bearing_eval_driver_decomposition_2026-08-06.md` (the ORIGINAL decomposition) found, on the 36 OOV items of `experiments/data/goal_bearing_modern_eval_v1.jsonl`: DID-IT-HAPPEN 15/36 (41.7%) primary, GOAL-RELATION 13/36 (36.1%) primary, VERB-POLE 2/36 (5.6%) primary, OTHER 6/36 (16.7%). That finding grounded a pivot away from verb-valence-dictionary work toward did-it-happen detection wired into the existing goal-congruence organ. This probe asks: is that distribution a property of goal-bearing narrative in general, or an artifact of the specific 44 items (mostly `little_women`/`anne_of_green_gables`/`tom_sawyer`/`wizard_of_oz`/one `alice_in_wonderland` passage + 4 RACE + 5 OneStop) the original eval happened to draw from?

## Source selection and non-overlap confirmation

I read all 44 rows of `experiments/data/goal_bearing_modern_eval_v1.jsonl` in full (ids, `corpus` field, `line_citation`, RACE/OneStop `example_id`/filename) before selecting anything, specifically to build an exclusion list:

- **little_women**: 10 items (all from `little_women.clean.txt`) — EXCLUDED entirely from the fresh set.
- **anne_of_green_gables**: 12 items — EXCLUDED entirely.
- **tom_sawyer**: 5 items — EXCLUDED entirely.
- **wizard_of_oz**: 5 items — EXCLUDED entirely.
- **alice_in_wonderland**: 1 item (`alice_beautiful_garden`, Chapters V-VII) — EXCLUDED (this whole corpus avoided, not just the one chapter span, out of caution).
- **RACE**: 4 items — `example_id` middle3233 (Chen situps), middle1701 (German dog), middle4034 (Tim rescue), high5675 (Davey wiffle) — these 4 exact ids EXCLUDED.
- **OneStop**: 5 items — `Skydiver-ele.txt`, `Malala-ele.txt`, `WNL Man falls-ele.txt` (Carle), `Crowdfunding-ele.txt`, `Denmark-ele.txt` — these 5 exact filenames EXCLUDED.

Fresh set draws from three corpora, none of which the original eval touched at all, plus fresh ids/filenames within RACE/OneStop:

1. **`data/corpora/sherlock_holmes/cleaned/{adventures,memoirs}.clean.txt`** (9 items) — zero overlap by construction; this corpus never appears in the original eval.
2. **`data/corpora/onestop/Texts-SeparatedByReadingLevel/Ele-Txt/`** (7 items, 2 goal-owner sub-episodes drawn from one shared article) — 6 distinct filenames, all confirmed absent from the original 5-filename list above: `Norwegian sun-ele.txt`, `Everest-ele.txt`, `Banksy-ele.txt`, `Richard III-ele.txt`, `Gangs-ele.txt` (used twice, two different goal-owners: Junior Smart's own rehab program vs. government policy on arresting gang leaders), `Facebook deserted by millions of users-ele.txt`.
3. **`data/corpora/race/{middle_test,high_test}.jsonl`** (5 items) — `example_id` middle1198, middle139, middle1361, high123, high1144 — all confirmed distinct from the original's 4 excluded ids.

`data/corpora/{sherlock_holmes,simplewiki,litbank_coref_conll}` were the sources named as candidates in the task brief. I sampled `simplewiki_clean_v1.txt` and `litbank_coref_conll/*.conll` and set both aside: simplewiki's articles that I opened are almanac/reference-style entries (a "months of the year" leader article) rather than character-goal narrative, and the litbank files are raw CoNLL token-per-line coreference annotations (no readable running prose), both a poor match for "a character with an identifiable goal + a resolved outcome" versus the much higher hit-rate of Sherlock Holmes narrative prose. This is a disclosed, honest substitution, not a silent one.

**21 items total** (task asked for ~20-25). I did not force a round number — I stopped once each of the three corpora had produced a reasonably-sized, honestly-classifiable batch, prioritizing passages with OOV outcome verbs where the story naturally supplied them.

## Rubric (verbatim from the original note)

Primary driver of the gold MET/UNMET label = **(A) VERB-POLE** [outcome verb's own intrinsic result-state settles it, unnegated, no owner-mismatch, no threshold] / **(B) DID-IT-HAPPEN** [occurrence, negation, failure, achievement-confirmation, including direct recurrence of the goal's own verb] / **(C) GOAL-RELATION** [owner-attribution mismatch, goal-relative polarity flip, numeric/evaluative-threshold comparison against the specific stated goal] / **(D) OTHER/composite** [commonsense/world-knowledge bridging, no clean outcome verb present, implicit unstated goal, false-negative-requiring-override].

I additionally checked each outcome verb lemma against the substrate's actual in-production lexicon (`hdlab/verb_lexical_similarity.py` `OUTCOME_SEED_POS`/`OUTCOME_SEED_NEG`/`OUTCOME_HELDOUT_POS`/`OUTCOME_HELDOUT_NEG`, merged into `OUTCOME_POS_WORDS`/`OUTCOME_NEG_WORDS`) rather than guessing OOV status, for parity with the original eval's `outcome_in_lexicon` field.

## Per-item table (21 fresh items)

| id | source | outcome_verb | gold | primary | secondary | in_lex | justification |
|---|---|---|---|---|---|---|---|
| sh_scandal_bohemia_photo | sherlock_holmes/adventures.clean.txt:383,1030-1061 | recover | unmet | C | — | **TRUE** | King's stated goal is literally "It must be recovered" (the photo); Irene Adler never returns it and keeps it forever as insurance, yet the King calls the outcome "successful" because a DIFFERENT, unstated goal (safety from blackmail) was met — a goal-target mismatch trap on an IN-LEXICON verb, structurally identical to `race_chen_situps`/`onestop_carle_madeinfrance` in the original |
| sh_boscombe_valley_mccarthy | sherlock_holmes/adventures.clean.txt:3766-3900,3912 | acquit | met | A | — | FALSE | "James McCarthy was acquitted at the Assizes" — a rare, specific achievement-verb whose own sense (found not guilty) settles MET with no negation, no owner-mismatch (McCarthy is subject and goal-owner), no threshold |
| sh_five_orange_pips_openshaw | sherlock_holmes/adventures.clean.txt:4056,4611-4629 | (none — death report) | unmet | D | B | FALSE | No outcome verb is tied to Openshaw's own survival goal; his fate is conveyed only via a euphemistic newspaper "accidental drowning" report that must be recognized as the threat materializing — no clean tagged verb, composite/commonsense, same pattern as `lw_laurie_proposal_rejected` (no outcome verb present at all) |
| sh_blue_carbuncle_ryder | sherlock_holmes/adventures.clean.txt:6071-6082,6655-6699 | (get out / release) | met | B | — | FALSE | Ryder confesses; Holmes says "Get out!" and lets him go uncharged — direct, unnegated occurrence (he is released, not arrested), no owner-mismatch |
| sh_engineers_thumb_hatherley | sherlock_holmes/adventures.clean.txt:8074-8220,8725-8752 | lose | unmet | A | — | **TRUE** | "I have lost my thumb and I have lost a fifty-guinea fee" — first-person, unnegated, in-lexicon NEG verb whose own pole settles it alone, no owner or threshold confound |
| sh_beryl_coronet_holder | sherlock_holmes/adventures.clean.txt:10540-10581 | recover | met | B | — | **TRUE** | "hugged his recovered gems to his bosom" — direct recurrence of the (implicit) recover-the-coronet goal's own verb, unnegated, Holder is subject and goal-owner; classified B (goal-verb recurrence) not A per the original's own precedent (`woz_scarecrow_brains` pattern) |
| sh_noble_bachelor_st_simon | sherlock_holmes/adventures.clean.txt:9083-9110,9500-9534 | marry | unmet | C | — | FALSE | Lord St. Simon's goal was to keep Hatty as his wife; the resolution is conveyed purely relationally — she is introduced as "Mrs. Francis Hay Moulton," another man's wife — no negation, no verb-pole cue for St. Simon specifically, pure owner/identity inference |
| sh_speckled_band_stoner | sherlock_holmes/adventures.clean.txt:6833-6841,7756-7786 | die | met | B | D | FALSE | Helen Stoner's plea ("advise me how to walk amid the dangers which encompass me") is resolved when Dr. Roylott is killed by his own snake; his death directly and explicitly removes the threat (Holmes: "we can... remove Miss Stoner to some place of shelter") — borderline B/D, flagged rather than silently resolved |
| sh_silver_blaze_ross | sherlock_holmes/memoirs.clean.txt:378-381,961-993 | recover / win | met | D | B | **TRUE (both verbs)** | Colonel Ross's stated goal ("recovering my horse") stages an explicit FALSE NEGATIVE first ("That's not my horse... not a white hair upon its body") that must be OVERRIDDEN by the later correction (the horse was dyed; "It's my race, anyhow") — a naive first-signal-wins reader gets this wrong even though both verbs are in-lexicon; direct structural match to `agg_anne_avery_scholarship_gilbert_medal_ch36` (original's own D-primary exemplar) |
| os_norwegian_sun_andersen | onestop/.../Norwegian sun-ele.txt ¶10-14 | work | met | B | — | FALSE | Andersen's Solspeil mirror-idea goal is confirmed by "And it really works" — generic unnegated achievement-confirmation, no owner-mismatch |
| os_everest_kenton_cool | onestop/.../Everest-ele.txt ¶1 | reach / climb / continue | met | B | — | "reach" **TRUE** | Three-summit "horseshoe" goal narrated sequentially and explicitly achieved ("reached the summit of Nuptse... climbed to the summit of Everest... continued to the summit of Lhotse") — occurrence-confirmation across three sub-goals, unnegated |
| os_banksy_haringey_campaign | onestop/.../Banksy-ele.txt ¶1,4-5 | stop | met | B | — | FALSE | Local campaign's goal to block the sale; "the auction... was stopped just moments before it was going to be sold" — explicit negation-of-the-bad-outcome, clean |
| os_richard_iii_morris | onestop/.../Richard III-ele.txt ¶1,8-9 | find / confirm | met | B | — | FALSE | Team's goal to identify the car-park skeleton; "I think we've found him," later formally confirmed — direct occurrence/achievement confirmation |
| os_gangs_arrest_policy | onestop/.../Gangs-ele.txt ¶7-8 | worsen | unmet | B | A | "worsen" **TRUE** | Implicit government goal (arresting gang leaders solves the gang problem) explicitly negated: "the arrest of the gang leaders has no long-term effect... it can even make things worse" — the negation phrase is the primary textual cue; "worsen" is a corroborating in-lexicon NEG verb (noted secondary A) |
| os_gangs_smart_program | onestop/.../Gangs-ele.txt ¶3,11 | (reoffend, statistical) | met | D | C | FALSE | Junior Smart's rehab-program goal; "fewer than 20% of the people he helps reoffend" — requires implicit real-world-benchmark knowledge (a low reoffend rate is a good outcome) not stated as an explicit target in the text, unlike an explicit numeric threshold (contrast with `race_chen_situps`-style true threshold items, hence D not C) |
| os_facebook_user_decline | onestop/.../Facebook deserted...-ele.txt ¶1-2 | lose | unmet | A | — | **TRUE** | "Facebook has lost millions of users... has stopped growing" — implicit growth/dominance goal, unnegated in-lexicon NEG verb settles it alone, no owner/threshold confound |
| race_gertie_training | race/middle_test.jsonl middle1198 | (train, negated) | unmet | B | — | FALSE | "I decided that the dog would be trained. This didn't quite go as planned." — explicit negation phrase directly on the stated goal, same pattern as `lw_meg_currant_jelly` ("wouldn't jell") |
| race_love_rescued | race/middle_test.jsonl middle139 | take / rescue | met | B | C | FALSE | Love's goal to be saved from the sinking island; three companions (Richness, Vanity, Sadness/Happiness) each explicitly REFUSE for their own reasons before Time rescues her ("Come, Love, I will take you") — must read past 3 genuine interim refusals, direct structural match to `onestop_hunt_crowdfunding`/`onestop_limal_dating`'s multi-attempt persistence pattern (both classified B in the original) |
| race_antigua_holiday | race/middle_test.jsonl middle1361 | (best decision, evaluative) | met | C | — | FALSE | "This was the best decision I had ever made" — valence carried by an evaluative NP, not a typed result verb, direct structural match to `agg_anne_hair_dye_green_ch27` (original's own C-classified "result adjective, not verb" exemplar) |
| race_crocodile_rescue | race/high_test.jsonl high123 | survive | met | C | B | FALSE | Mother's goal is to save her son from a crocodile attack; she succeeds ("the little boy survived") but the goal-owner (mother) and outcome-subject (son) are different people — textbook owner/beneficiary split, direct structural match to `lw_ice_rescue_amy` (original's own C-primary exemplar) |
| race_dance_dream | race/high_test.jsonl high1144 | become | met | B | — | FALSE | Childhood goal ("I'm going to be one of those!") directly recurs in the outcome ("I became a member of the company") — unnegated direct goal-verb restatement, same pattern as `woz_scarecrow_brains`/`woz_dorothy_kansas_wish` |

Counts independently re-summed twice: 21 = 3(A) + 11(B) + 4(C) + 3(D); 21 = 14(met) + 7(unmet).

## Fresh distribution (21 items, primary driver)

| driver | count | % | met | unmet |
|---|---|---|---|---|
| A — verb-pole | 3 | 14.3% | 1 | 2 |
| B — did-it-happen | 11 | 52.4% | 9 | 2 |
| C — goal-relation | 4 | 19.0% | 2 | 2 |
| D — other/composite | 3 | 14.3% | 2 | 1 |
| **total** | **21** | **100%** | **14** | **7** |

## Side-by-side comparison to the original (36 OOV items)

| driver | original (36) | fresh (21) | delta (pp) | ordering preserved? |
|---|---|---|---|---|
| A — verb-pole | 5.6% (2) | 14.3% (3) | **+8.7pp** (~2.5x proportional) | still smallest-or-tied, but closer to the <15% hard-fail line than desired |
| B — did-it-happen | 41.7% (15) | 52.4% (11) | +10.7pp | YES — dominant in both, more so in the fresh set |
| C — goal-relation | 36.1% (13) | 19.0% (4) | **-17.1pp** (~half) | still 2nd-largest in both, but a real proportional shrink |
| D — other/composite | 16.7% (6) | 14.3% (3) | -2.4pp | consistent range |

## Verdict: GENERALIZES, with two honest caveats

By the letter of the pre-registered criteria (did-it-happen remains the largest or tied-largest primary driver AND verb-pole stays under ~15%): **HOLDS.** B is unambiguously the largest driver in both samples (52.4% fresh vs. 41.7% original — actually more dominant on the fresh set), and A came in at 14.3%, under the 15% line.

Two things temper a clean "confirmed, move on" reading:

1. **Verb-pole (A) nearly tripled in relative share (5.6% -> 14.3%) and landed right at the boundary, not comfortably inside it.** All three A items on the fresh set (`acquit`, `lose` x2) are plain, unnegated, first/third-person declarative resolution verbs typical of 19th-century detective-fiction prose style ("I have lost my thumb," "was acquitted," "has lost millions of users"). This looks like a genuine, mechanism-relevant signal, not noise: classic narrative and modern news-report prose states outcomes more bluntly and directly than the original eval's curated set, which was DELIBERATELY engineered (see its own `trap_type` field: `recency_trap`, `distractor_between`, `natural`) to stress-test owner-mismatch and distractor cases. A random-ish sample of real prose surfaces more "just say what happened plainly" resolutions than a hand-curated trap set does. Practical implication: the did-it-happen + goal-congruence build should NOT fully zero out lightweight verb-pole handling — a small in-lexicon-verb fast path (already present in the substrate lexicon: `acquit` would need adding, `lose`/`worsen` are already tagged) is cheap and catches a non-trivial minority of real-prose cases outright, even though it should stay subordinate to did-it-happen + goal-relation as the original found.

2. **Goal-relation (C)'s share roughly halved (36.1% -> 19.0%), which is the largest single delta in the comparison.** This is very likely a sampling-methodology difference rather than a property of goal-bearing narrative in general: the original eval's curator explicitly engineered `recency_trap`/`distractor_between` items to stress owner-attribution (that was the eval's designed purpose), while this fresh set was picked more organically from whichever passages a story happened to supply cleanly. Even so, C did not vanish — it is still the fresh set's 2nd-largest driver, and 3 of its 4 fresh items (`sh_scandal_bohemia_photo`, `sh_noble_bachelor_st_simon`, `race_crocodile_rescue`) are structurally identical to specific named C-primary items in the original (`race_chen_situps`-style goal-target mismatch, pure owner/identity inference, `lw_ice_rescue_amy`-style owner/beneficiary split) — so the MECHANISM goal-relation is diagnosing is clearly real and recurring, just less densely represented when the sampling isn't deliberately adversarial. The original's own "load-bearing on 69% of items (primary or required secondary)" claim likely also softens on a non-adversarial sample, though I did not re-run that specific secondary-driver tally here (out of scope for a ~21-item probe; flagged as a natural follow-up if a larger confirmatory batch is ever wanted).

**Net:** the core strategic call — wire did-it-happen detection into the existing goal-congruence organ rather than investing further in verb-valence dictionary expansion — is NOT refuted and is if anything reinforced (did-it-happen's dominance is larger on the fresh set, not smaller). The one real course-correction this probe motivates: don't treat verb-pole coverage as a rounding error to be ignored entirely — a cheap, small in-lexicon fast-path is worth keeping in the build (it was already implicitly part of "did-it-happen wired into the congruence organ" designs since the congruence organ already consumes lexicon polarity as one input) rather than being explicitly deprioritized to zero.

## Citations (verified count)

Zero external citations. This is a closed-corpus, internal read-only analysis: all 21 fresh items were read directly from `data/corpora/sherlock_holmes/cleaned/{adventures,memoirs}.clean.txt`, `data/corpora/onestop/Texts-SeparatedByReadingLevel/Ele-Txt/*.txt`, and `data/corpora/race/{middle_test,high_test}.jsonl` (exact line numbers / paragraph numbers / `example_id`s cited per row above). Lexicon membership was checked directly against `hdlab/verb_lexical_similarity.py` (`OUTCOME_SEED_POS`, `OUTCOME_SEED_NEG`, `OUTCOME_HELDOUT_POS`, `OUTCOME_HELDOUT_NEG`), not assumed. Non-overlap with the original 44-item eval was confirmed by reading all 44 rows of `experiments/data/goal_bearing_modern_eval_v1.jsonl` and cross-checking corpus/filename/`example_id` before selecting any fresh item. No lit-scan calibration penalty applies (no novel-synthesis P-estimate; this is a factual re-derivation exercise, independently re-summable by any reader from the table above).
