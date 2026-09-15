# How efficiently is this project being developed? A frank review (2026-09-15)

Written for the owner, by the strategy session, at the owner's request. Plain language; numbers where they change a decision.

## The short answer
Output is high and quality is good; direction has been the problem. This week (13 to 15 Sep) produced 386 commits, 110 ledger rows and 10 landings. But most of that effort was graded by a scoreboard that never ran the reader, so for months the work optimised parts the product could not use. A one-day outside review found that; one day of work since then changed the ruler and landed the largest product-visible gain of the project (plain-text "who did it" from 19 to 75 in 100). The lesson is not "work harder", it is "measure the product first".

## Where the time actually went (this session, roughly)
| activity | share | comment |
|---|---|---|
| waiting on runs (boards 70-150 min, witness batches 1-3 h, agents 2-4 h) | ~40% | one laptop, shared by three agents and my own runs; everything slows 2-3x when they overlap |
| witness re-pins after a landing changed a population | ~20% | five re-pins for pri 125 alone; each needs a manual diagnosis of which clause failed |
| bookkeeping per landing (ledger, STATUS, plan head, scorecard, live doc, retired claims, SOLVED mark, Updates post) | ~15% | 6-8 files per landing, by hand, with hooks that refuse partial briefs |
| reading and probing agent reports (the phase-7 push) | ~15% | high value: it turned an invalid control into a root cause today |
| building and diagnosing myself | ~10% | the audits and hygiene fixes |

## The wrong directions, named
1. **The blind board (the big one).** Every headline row rebuilt its own read from the annotated test file. Landings that helped the real reader looked like zero; landings that helped the rebuilt rows looked like progress. Cost: weeks of attention on a ruler that did not measure the product. Root cause: instruments were built per organ, never one end-to-end read; and nobody counted whether the reader was called. Fixed today (pri 122).
2. **A root cause found and left unfixed.** The blank file card (no gender or number on the reader's own referents) was diagnosed on 3 Sep, recorded, and not repaired at the organ that wrote it. pri 125 rediscovered it twelve days later. Cost: one solver-day, and twelve days of an anaphora rung that could not work. Rule to add: a located root cause becomes a brief the same day, with the organ named.
3. **Capability left switched off for a reason that no longer applies.** The word-order-plus-override agent route has been default-off since 6 Sep because a 19th-century test set regressed; 19c has been banned from requirements since then. Cost: about five points of plain-text "who did it" sitting unused. There are likely more such flags; they need an audit.
4. **Exact-number pins in witnesses.** Witnesses that assert "n == 2855" or "delta < 1e-6" go red on every honest population change and each red costs a diagnosis. Today's five re-pins were all of this kind; none was a regression.
5. **Numbers travelling without provenance.** 0.62 was quoted as the reader's accuracy in chat and on the scorecard when it was a component number. The retired-claims file existed only in my memory folder; the briefs pointed at a path that did not exist in the repository until today.

## What is working and should be kept
- **Solver agents with the push script.** Two agents today produced 88 KB of reports, 21 and 11 measured runs, root causes with counts, and diffs that applied cleanly. The phase-7 probe caught an invalid control and produced the anaphora win. Keep it; it is the highest-yield hour of the day.
- **Layered controls.** Twins, floors recomputed in place, annotation-invariance triples. They are why today's numbers can be trusted.
- **The outside review.** One day, thirteen findings, five briefs, two landings. It found what the inside could not see because it started from the product.

## Concrete changes to make (in order of payoff)
1. **Score the product, always.** Done for the board today. Extend the rule: no new instrument without a "does this run the reader on raw text?" line, and a counted witness that it does.
2. **A landing tool.** One command that writes the ledger row, STATUS line, plan head, scorecard line, live-doc line, retired-claims line, SOLVED mark and the Updates post from one record. Saves an hour per landing and removes the hook-refusal loop.
3. **Witnesses pin claims, not numbers.** Direction, separation, invariants, bounded losses. A re-pin helper that prints which clause failed with its numbers (I computed those by hand five times today).
4. **Move compute off the laptop.** The desktop is 2-3x faster and idle. A runner that ships a bundle and runs a witness batch or a board there, returning the log, would cut wait time roughly in half. Until then, never run more than two heavy jobs at once.
5. **A dormant-flags audit** (a sonnet job): every default-off capability flag, the reason it is off, whether the reason still holds. Flip or delete.
6. **A "located, not yet fixed" list** at the top of STATUS, so a diagnosed root cause cannot go quiet.
7. **An outside read-only review every two weeks**, fresh model, starting from the product's raw-text read.
8. **The autoloop backs off while agents run.** Empty loop iterations only cost context; a bounded wait on the agents' report files (what I did today by hand) should be the loop's default when agents are out.

## How to read the score now
The old component board stays at 0.62. The product ruler reads 0.47 before the pronoun fix and will read higher after it lands tonight. Both are published with provenance. The product number is the one that should move from here on.
