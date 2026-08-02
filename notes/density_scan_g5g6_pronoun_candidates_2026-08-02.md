# Density-scan report: g5/g6 pronoun-linking candidates (2026-08-02)

Mining pass over data/corpora/mcguffey_graded/clean/g5.txt (3151 lines) and clean/g6.txt
(3013 lines), targeting passages with (a) multiple same-gender co-present entities,
(b) many pronoun mentions that corefer to a NAMED antecedent, (c) role variation across
an entity's mentions, (d) agent-vs-agent turn-taking. Method: manual read of narrative
(non-biography, non-verse) sections plus grep for `said <Name>` and multi-name co-occurrence,
cross-checked against gold_multientity_dense_v1.jsonl to avoid re-mining already-covered scenes.

## Top candidates found, ranked (n_same_gender_entities, n_pronoun_link_mentions, n_role_varying_entities)

1. g5 "Gentle Hand" (clean lines 51-103): farmer/John/Dick(pony) all male + girl/mother female.
   (3, 7, 4) -- highest pronoun density found; cross-species trap (Dick the pony is "he/him"
   alongside two human males) layered on a human same-gender pair (farmer vs John).
2. g5 "Frederick the Great / two pages / Ernestine" (clean lines 1-25): King + 2 unnamed pages,
   all male, Ernestine female. (3, 5, 4). Two pages never get proper names in the source --
   noted as a harder no-proper-name-antecedent variant.
3. g6 "Duke of Newcastle / Cornish voter / porter" (clean lines 1-33): (3, 3, 3). Contains a
   pronoun-refers-outside-the-speech-dyad trap (porter says "he...him" about the Duke, to the
   voter) structurally similar to the Joab/Absalom entry already in gold_multientity_dense_v1
   but from an independent story.
4. g6 "Chub / Frank Meriwether / Ned" (clean lines 789-805, "Swallow Barn"): (3, 1, 3). Lower
   pronoun-mention count but a clean same-clause 3-way trap in the climax sentence.
5. g5 "Barber William Reed / stranger" (clean lines 269-281): (2, 2, 2). Below the 3-entity
   density bar but an unusually long 2-way pronoun chain (10 clauses) with a topic-vs-subject
   continuity trap; included as a lower-density control candidate.

## Candidates found but REJECTED (near-duplicate of existing gold)

- g5 "Lucy Forester / Michael / Agnes / Isabel / Jacob" (clean lines 575-604): the fuller
  source story for gold_multientity_dense_v1's existing `g5_dense_michael_agnes_isabel_jacob`
  entry (note: that entry is grade-labeled "g5" but its exact sentences -- "Michael stood up
  between Jacob and his wife, and looked into his heart" etc. -- are found in g6.txt in this
  scan, not g5.txt; flagging the grade-label mismatch for Director attention). Two candidate
  excerpts were drafted from adjacent, non-overlapping sentences in this story but on review
  both still shared 2+ verbatim sentences with the existing gold entry (e.g. the "stood up
  between Jacob and his wife" line appears in both draft attempts). Discarded rather than risk
  a near-duplicate entry padding the aggregate counts without adding real new material.
- g5 "Squeers / Mrs. Squeers / Nicholas / Smike" text is also present verbatim in g6.txt
  (clean lines 2089-2131) and matches gold_multientity_dense_v1's existing entry #15 --
  confirms the existing gold set's grade label for that entry may also be off by one grade
  (g5 vs g6); not re-mined.
- A satirical will-reading dialogue ("SWIPES, a brewer; CURRIE, a saddler; FRANK MILLINGTON",
  g5 clean lines 1189-1239) had strong multi-male same-gender density but is formatted as a
  stage play with ALL-CAPS speaker-name headers that were stripped by the corpus cleaning
  script -- the surviving clean text has NO reliable speaker attribution per turn. Rejected
  as too uncertain to annotate confidently without recovering the raw speaker tags.

## Honest scope note

Target requested 15-25 draft passages; this pass yielded 5 high-confidence, non-duplicate
passages plus documentation of what was found-and-rejected. g5/g6 are dominated by verse,
single-referent moral narration, and biography sketches (low pronoun-linking value); genuine
multi-same-gender dense scenes with reliable speaker attribution are less common than in the
g2/g4 material the existing gold set already mined. A further pass could likely find 5-10 more
candidates by reading the unscanned middle sections of both files (g5 lines ~150-560,
610-1180, 1240-3151; g6 lines ~100-750, 950-1900, 2150-2560, 2650-3013) at the same rate.
