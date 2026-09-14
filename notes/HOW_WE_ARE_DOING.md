<!--
HOW TO KEEP THIS CURRENT  (strategy session -- 10 lines, read before editing)
 1. This file IS the owner's "how we're doing" view. The window (tools/scorecard_gui.py) and the
    browser page (tools/how_we_are_doing_web.py) render THESE SECTIONS. Nothing else is parsed.
 2. Keep the eight "## " headings exactly as they are spelled; add nothing between them.
 3. WHERE WE ARE ON THE PLAN is a 4-column table. Column 2 must START with one of:
    SOLID / IMPROVING / WEAK / NEXT FRONT / AT RISK / NOT STARTED  (that word sets the colour).
 4. Per landing, edit at most three things: the stage row that moved, one dated line at the TOP of
    WHAT MOVED, and WHAT IS RUNNING. That is the few-lines-per-landing contract.
 5. Numbers come ONLY from notes/INTEGRATION_LEDGER.md, notes/SCORECARD.md or notes/BOARD_TREND.jsonl.
 6. Check the retired-figures memory file before quoting any number that feels familiar.
 7. Plain words only: no organ names, no file paths, no metric names, no arm/switch names.
 8. Every number gets units in words ("right 63 in 100"), never a bare decimal.
 9. WHAT MOVED: keep ~10 newest dated lines; older ones drop off (the ledger is the archive).
10. POSITION is ONE sentence and it is the headline; rewrite it whenever the honest answer changes.
-->

# HOW WE ARE DOING

## GOAL
A fully functional glass-box AI: a working brain recreated in software, where every part computes
what the brain computes and anyone can look inside and see why it answered as it did. Reading
comprehension is where we are working now, because that is where the parts can be checked against
what people actually do. The test board is the instrument we measure with, not the objective.

## POSITION
The whole front of the reading chain now runs on brain-style parts and the board sits at right 63
in 100 against 54 in 100 for simple rules, but two rungs are weak and hold everything above them
back: working out which word hangs off which (right 64 in 100) and keeping track of who is who
across a passage (right 47 in 100 on he/she/it) -- and that second one is the front we are on now.

## WHERE WE ARE ON THE PLAN

| Stage | Status | How well | What it means |
|---|---|---|---|
| Word kinds | SOLID | right 93 in 100 | Deciding, as each word arrives, whether it is a noun, a verb, a name and so on. Learned by counting from reading rather than trained on hand-labelled text. |
| Word forms | SOLID | right 98 in 100 | Recovering the base form of a word (ran -> run). Two routes, one for stored irregulars and one for regular endings, the way people do it. |
| Which word hangs off which | WEAK | right 64 in 100 | The sentence's skeleton. With the answer key for word kinds it is right 64 in 100, with the system's own word kinds 63 in 100. A parser trained on forty thousand hand-corrected sentences reaches 78 here and people are above 95, so this is the biggest single gap. |
| Who did what to whom | IMPROVING | right 92 in 100 given a correct skeleton | On a correct skeleton the roles are read almost perfectly. On the system's own skeleton that gain mostly disappears, which is why the rung above matters so much. On the board: who did the action 83 in 100, who it was done to 81 in 100. |
| Helped or harmed, how it feels | SOLID | right 100 in 100 on the careful test, 67 in 100 on fresh prose | Judging whether an action hurt or helped someone by the state it leaves them in, and how a character would feel about an event. Strong where the test is careful; the drop on fresh prose is the skeleton again. |
| Who is who across a passage | NEXT FRONT | right 47 in 100 on he/she/it | Following the same person or thing through a passage. Built in the brain's spirit but not yet rebuilt part by part the brain's way. This is the current front of the work. |
| Reasoning on top | IMPROVING | right 24 to 90 in 100 depending on the question | Time, cause, belief and goals. These work well when handed a correct reading of the sentence and slump on real prose, so the wall they hit is the chain below them, not the reasoning itself. Best: how a character feels about an event, 90 in 100. Worst: answering "why" when the cause is several sentences away, 24 in 100. |

## WHAT MOVED THIS WEEK
- 2026-09-14 -- Landed: 'is'/'has'-only sentences now have a predicate. The word-attachment organ gains about 1 in 100 overall and 5 in 100 on those sentences; unseen sentences 33 -> 9 in 1,240; board 'who was acted on' 81.0 -> 81.2, nothing down.
- 2026-09-14 -- Eighteen test stories had their words blacked out (only the answer key survives); dropped from the board. Common-noun reference 49 -> 55 in 100 (simple rule 54: still about even), main character 30 -> 27 (small set), pronoun reference unchanged at 42. Overall board 61.5 in 100 on the honest basis. The copula fix (a sentence whose only verb is 'is' or 'has' still has a predicate) is solved and being landed: the word-attachment organ gains a little everywhere and no score falls.
- 2026-09-14 -- Correction: the who-is-who scores were being graded with help from the answer key. Re-scored honestly: pronoun reference 47 -> 42 in 100 (still clearly above the simple rule, 32), common-noun reference 57 -> 49 in 100 (now about even with the simple rule, 49: that win was the answer key), main character 26 -> 30. Overall board 61.5 in 100 on the honest basis. The reader's own who-is-who test asks 200 questions again where it had been asking none.
- 2026-09-14 -- The part that names each word's job can now say "this belongs to that" (the roof OF the house): such links went from 0 to 74 in 100 with a correct skeleton, and every nominal link the organ can express from 58 to 71 in 100 on the system's own skeleton. On the board: 'who was acted on' 80.6 -> 81.0, 'what things are like' 74.3 -> 74.9, nothing down; overall 63.5 in 100.
- 2026-09-14 -- The word-kind part now hears from the passage: the people and things already met feed
  back into the decision about what kind of word is arriving. Names picked out of long documents on
  repeat mention improved from 57 to 58 in 100; word kinds overall held at 93 in 100.
- 2026-09-14 -- Verbs that the word-kind part mis-calls are rescued properly again. The rescue had
  two defects (its evidence had gone missing, and its cut-off sat above three quarters of the verbs
  it was meant to catch). Events the reader finds rose from 92 to 95 in 100. The board did not move
  at all, because no board question reads the reader's event list -- a real win the board cannot see.
- 2026-09-14 -- Two solutions for the sentence-skeleton part landed together after I found a defect
  in wiring them up (the builder never handed the new teacher its knowledge of which phrases go with
  which words, which had collapsed "of"-phrases to 24 in 100). With that fixed: skeleton 63.0 to
  63.8 in 100 with the answer-key word kinds, "of"-phrases 44 to 54 in 100, nothing down.
- 2026-09-14 -- Correction: the "what things are like" score had been showing 81 in 100, but that
  number came from an off-the-shelf trained parser that was still hiding inside the reader. The
  honest brain-style number on the same questions is 74 in 100, and the board baseline is 63 in 100.
  The old figure is retired and must not be quoted again.
- 2026-09-14 -- Correction found by a checking job: the board's who-is-who scorer had been reading
  part of the answer key. Without that peek the pronoun result still holds up (42 in 100 against 32
  for the simple rule), but the common-noun result ("the dog" -> which dog) was the answer key, not
  the system. The scorer is being rebuilt; treat the common-noun number as unproven until it is.
- 2026-09-13 -- Five solutions from separate solver sessions folded in together and re-checked on the
  full test: overall 63.5 to 63.7 in 100; who was acted on 79 to 81 in 100; nothing else moved.
- 2026-09-13 -- The parts that read a sentence now take words in the order they arrive rather than
  looking at the whole sentence first, which is how a person reads. Measured the same or better.

## WHAT IS RUNNING
- The board's who-is-who rows are being re-scored WITHOUT the answer key (the old scores read five answer-key columns); the honest numbers land in the next hour and the old ones retire.
- Two solver sessions: one on the sentences whose only verb is 'is' or 'has' (one grammar convention costing two organs), one letting the readers that combine clues trust the 'who did what' decision in proportion to how sure it is.
- The move to the desktop machine: everything is placed and the environment built there; a final catch-up copy runs right before the switch.
## NEXT
- Rebuild the who-is-who layer part by part the brain's way. It is the current front and the
  measurements say it is where the most is left on the table.
- Repair the "what is X like" reading so it can cope with the brain-style skeleton, rather than
  putting the old trained parser back.
- Five problems written up and waiting for a solver session, in order: the verb-versus-helper-verb
  confusion, passing the role decision's confidence through to the parts that use it, the
  subordinating-word class, keeping the role evidence learning while reading, and long-distance
  "and"/"or" links.
- Longer term: the system predicting what happens next as it reads, and using that prediction to
  settle who is who and what caused what. That is where the remaining headroom is.

## RISKS AND CORRECTIONS
- The board's "who did the action" question does not go through the reading chain at all -- it uses
  a word-order shortcut. Its 83 in 100 therefore says nothing about the chain, and the chain's own
  answer on the same question is 80 in 100 against 84 for the plain rule. This is being fixed.
- Two figures are retired and must never be quoted again: "what things are like 81 in 100" (it was
  the off-the-shelf parser; the honest number is 74) and the who-is-who common-noun result (it read
  the answer key).
- The trend chart: some checks were run on a smaller set of questions than others. Only runs on the
  same set of questions are joined by the line; the others are shown as hollow marks and must not be
  read as a rise or a fall.
- Six building blocks out of ninety are still stand-ins that do not compute what the brain computes.
  Each landing is supposed to remove one or move one from "a reasonable model" to "the brain's own
  maths"; today eight of the ninety are at that standard.
- The move to the desktop machine is the near-term operational risk: if anything is missed in the
  final copy, a day of work has to be re-run rather than lost.
