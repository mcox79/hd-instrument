---
priority:
review: EXCELLENT
review_text: "Survives adversarial re-checking against a STRONGER comparator than it used: all three benchmarks clear the strongest floor CI-separated, and the WordSim win holds against the supplied arm the submission did not quote. Two gaps, neither overturning: the head-to-head quotes only the weaker supplied arm, and the scored population was not saved."
---

> # 🥇 **MY REVIEW OF THE SUBMISSION -- EXCELLENT. IT SURVIVED AN ADVERSARIAL RE-CHECK.**
> *Reviewed 2026-08-23 by the strategy session. I tried to break it against a comparator it did not
> use, and it held. Recomputed from `data/exp_learn_from_reading_strong_arm_v1/metrics.json`
> (`mode: full`, `38,091,176` tokens read, vocab `60,085`).*
>
> ## ✅ **THE GATE, RE-RUN MY WAY: CLEARS ON ALL THREE, CI-SEPARATED**
> *The project's actual bar is a CI-separated margin over the strongest floor ACTUALLY RUN, gated on
> that floor's UPPER bound. Recomputed per benchmark, on each one's own population:*
>
> | benchmark | learned arm | strongest floor (upper bound) | |
> |---|---|---|---|
> | SimLex-999 | `0.2552` `[0.1964,0.3141]` | idf-count `0.1235` (upper `0.1885`) | ✅ **CLEARS** |
> | SimVerb-3500 | `0.1290` `[0.0956,0.1623]` | idf-count `0.0365` (upper `0.0717`) | ✅ **CLEARS** |
> | WordSim-353 | `0.6301` `[0.5628,0.6975]` | idf-count `0.4120` (upper `0.5002`) | ✅ **CLEARS** |
>
> **AND THE SPELLING FLOOR -- the one that had been beating our shipped channel -- is `0.0104` /
> `0.0164` / `0.0487`.** *This arm clears it by 15-40x. That is the reversal the brief asked for.*
>
> ## 🔍 **THE ATTACK I MADE, AND WHY IT FAILED TO BREAK IT**
> **The head-to-head quotes `SUPPLIED_CORE`. The cell ALSO RAN `SUPPLIED_FULL`, which is higher on
> all three** (`0.3406` / `0.3547` / `0.4395` against `0.2502` / `0.2663` / `0.4047`). *Quoting the
> weaker of two comparators you ran yourself is exactly the "strongest floor actually run" failure,
> so I re-scored against the stronger one:*
>
> - **WordSim: learned is AHEAD of `SUPPLIED_FULL` too, CI-separated** (`0.6301` vs `0.4395`). **The
>   headline win survives the stronger comparator.**
> - SimLex: CIs OVERLAP against **both** supplied arms -- so *"ties"* is defensible either way,
>   though the point estimate sits `0.085` below `SUPPLIED_FULL`.
> - SimVerb: behind both. **The submission's own "LOSES verbs" is honest and if anything UNDERSTATED.**
>
> ⚖️ **AND THE CHOICE OF `CORE` MAY BE PRINCIPLED, NOT EVASIVE:** `SUPPLIED_FULL` covers `2-8%`
> FEWER pairs, so comparing against it crosses populations, while `CORE` matches the learned arm at
> `coverage 1.000`. *That is the right instinct.* **The defect is only that the sentence never tells
> the reader a stronger supplied arm exists.**
>
> ## 🔻 **THE ONE REAL GAP: THE SCORED POPULATION WAS NOT SAVED**
> `data/exp_learn_from_reading_strong_arm_v1/` contains **`metrics.json` and nothing else.** So the
> single check that would settle whether `SUPPLIED_FULL`'s edge is real or a coverage artifact --
> re-scoring every arm on the intersection of pairs it covers -- **requires a full re-run.**
> *The priority-1 submission saved its population and that audit cost minutes; this one costs hours.
> Same standing rule, opposite outcome, and it is worth noting the STRONGER result is the less
> examinable one.*
>
> ## ➡️ **WHAT THIS CHANGES: THE ROUTE IS CORPUS-LIMITED, NOT EXHAUSTED**
> **The curve is still climbing at the ceiling on all three** (SimLex `0.089`->`0.255` across the
> `1M`->`40M` sweep). **My brief's premise -- that sixteen prior losses meant the IDEA was dead --
> is REFUTED, and it was refuted the right way: by building the strong version and measuring it.**
> *The sixteen losses tested a weak implementation, which is the standing "do not generalise a
> narrow failure to impossible" rule catching a real error of mine.*

> # 🥈 **PRIORITY 2 of 9 — THE DIRECTION QUESTION, TURNED INTO AN EXPERIMENT**
> **OWNER, Q116, 2026-08-23: *"make this into a focused problem to give to the solver so we can
> resolve it fully."*** I asked whether to formally stop trying to learn word meaning from reading
> text and commit to supplied knowledge plus reasoning. **The owner declined to settle it by
> decision and asked for it to be settled by measurement.** This is that brief.
>
> 🚨 **SO THE DELIVERABLE IS NOT A RECOMMENDATION. IT IS A RESULT THAT MAKES THE RECOMMENDATION
> UNNECESSARY.** Do not write me an opinion. Run the arm that can kill the idea, and report what it
> did.

# PROBLEM: SIXTEEN MEASUREMENTS SAY LEARNING-FROM-READING LOSES. ALL SIXTEEN TESTED A WEAK VERSION.

**slug:** `does_learning_from_reading_deserve_to_continue` · **opened:** 2026-08-23 by the strategy
session, at the owner's instruction · **status:** OPEN

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

The system is supposed to learn what words mean by reading a lot of text. **Every time we measure
that, something much simpler beats it** — on the measure that best represents "did reading produce
useful knowledge", we score about 5 in 100 where a method that only looks at how words are *spelled*
scores about 9 in 100. That is the sixteenth measure where a simple counting method leads.

**The opposite is just as consistent.** Every time we *give* the system grounded knowledge and let it
reason outward, we win clearly.

So the obvious move is to stop trying to learn from reading. **The reason we should not do that
yet:** every one of those sixteen losses tested a *weak* attempt. A fair test of a weak version tells
you that version failed. It does not tell you the idea is impossible — and we have a standing rule
about exactly this mistake.

**The job: build the strongest honest version of learning-from-reading, test it once, properly, and
settle the question.** A clear loss is a real answer and closes a door we keep drifting through. A
win means we were about to throw away the more interesting half of the project.

---

## 2. WHY THIS ONE

- **IT IS A DIRECTION DECISION, AND WE HAVE BEEN DRIFTING.** Effort keeps going into a channel
  sixteen measurements call the weak one, without anyone deciding to. **The cost of no answer is not
  zero; it is the drift.**
- **BOTH OUTCOMES ARE VALUABLE AND THE BRIEF IS INDIFFERENT BETWEEN THEM.** A rigorous negative
  retires a route with evidence instead of by fatigue. A positive rescues it.
- ⚠️ **AND THE OWNER SPECIFICALLY DECLINED TO DECIDE IT BY FIAT.** *"Resolve it fully"* means the
  answer has to survive someone reading the numbers, not someone trusting my summary.

---

## 3. MEASURED vs INFERRED

### MEASURED — you may build on these

| what | number | scope you must carry |
|---|---|---|
| **our learned channel on VERBS** | **`+0.0000`** | SimVerb-3500, 2,651 covered pairs, null p95 `0.0372` |
| our learned channel on NOUNS | `0.1310` vs null `0.0843` | SimLex nouns — **clears, barely** |
| **the SUPPLIED sensorimotor channel on the same verbs** | **`+0.3107`** `[+0.2822,+0.3390]`, null `0.0304` | SimVerb, 3,487 covered ⚠️ *different coverage → NOT a subtraction* |
| supplied channel, action vs perceptual dims on verbs | `+0.0651` `[+0.0306,+0.1005]` **CI-separated** | somatotopy holds at power (3,487 pairs) |
| 🔻 **the supplied channel CANNOT GATE LINKS ALONE** | `66%` hit / **`37%` false alarm**; AUC `0.7002` | no threshold in `0.30`–`0.95` does better |
| 🔻 **our FORMAT keeps a good signal but COMBINING destroys it** | store `94%`; bundle with 2 → `47%`, with 8 → `26%` | *neither sparsity nor an addressed slot rescues it* |
| 🔻 **supplied knowledge is EASY TO OVER-CREDIT** | WordNet's pooled `+0.543` edge collapses within relation class; on the unselected 60% sensorimotor wins `+0.286` vs `+0.154` | **SimVerb's pairs were SELECTED by WordNet relation** |

### INFERRED — overturning any of this is a RESULT, not a failure

- 🔻 **That the sixteen losses reflect the IDEA rather than our IMPLEMENTATIONS.** Nobody has built a
  strong version. **This is the whole question and it is currently an assumption.**
- 🔻 **That "supplied knowledge wins" generalises.** The WordNet result above is a live warning that a
  supplied resource can look strong because the *benchmark was selected by it*.
- 🔻 That the learned and supplied channels are alternatives at all. **They may be complements**, and
  the hub test (below) is not settled.

---

## 4. ALREADY TRIED — DO NOT RE-RUN THESE

- ✅ **Sixteen measurements where a counting/orthographic method leads.** Do not add a seventeenth.
  **A seventeenth weak implementation is not evidence and will not be accepted as an answer.**
- ✅ **The supplied channel is measured end to end** (`test_sensorimotor_covers_the_verb_hole.py`,
  `test_which_number_is_the_meaning_asset.py`, `test_the_channel_cannot_gate_links_alone.py`).
- ✅ **A two-spoke hub (sensorimotor + WordNet) on the unselected class**: best rule is mean-of-both,
  gain over sensorimotor alone `+0.0245` `[-0.0021,+0.0520]` — **includes zero, NOT established.**
  *Its noise control is `-0.0507` `[-0.0891,-0.0105]`, so the second spoke carries real information.*
  **Re-running that exact comparison adds nothing; a POWERED version would.**
- ✅ Prior-work queries run: `sensorimotor`, `encoder`, `learn from reading`, `distributional`.
  **Use SINGLE keywords with `tools/experiment_index.py query` — a multi-word query returns 0 and
  reads as absence.**

---

## 5. VERIFY BEFORE YOU START — THE DISK OUTRANKS THIS BRIEF

1. `python tools/before_you_start.py "strongest learn-from-reading arm"` — read **every** row.
2. Re-run the three witnesses named in §4. *Notes go stale within hours; those do not.*
3. ⚠️ **Read `notes/problems/reader_meaning_channel/PROBLEM.md` FIRST — its orientation map.** It
   holds six measurements about the supplied channel and **its correction blocks record two pieces
   of advice I wrote before testing them.** Do not inherit those.
4. **`read()` still makes ZERO calls to the meaning asset.** Any end-to-end reading comparison has to
   deal with that, and it is priority 1's other half.

---

## 6. THE BAR

**ONE HEAD-TO-HEAD, ON ONE POPULATION, WITH ONE SCORER, WHERE THE LEARNED ARM IS THE BEST WE CAN
HONESTLY BUILD.**

- **THE LEARNED ARM MUST BE THE STRONGEST BRAIN-MOTIVATED VERSION YOU CAN JUSTIFY, AND YOU MUST WRITE
  DOWN WHY IT IS STRONGER** than what the sixteen losses tested — before you run it. *Examples of
  what "stronger" could mean, none mandated: a context window that respects sentence structure rather
  than a bag; a learning rule with an error signal rather than accumulation; enough reading volume
  that the curve has flattened; the definitional channel, which is built and unmeasured on this.*
- **THE SUPPLIED ARM MUST CARRY ITS OWN CONTROLS**, because the WordNet result shows supplied
  knowledge over-credits. **If the benchmark was selected using the supplied resource, condition on
  the selection variable and report the per-stratum table, not the pooled number.**
- **BOTH ARMS AGAINST THE SAME FLOOR**, recomputed on this population and representation, gated on
  the floor's upper bound. The orthographic/counting baseline is the one that has been winning:
  **it is the floor, and it must be run, not cited.**
- **REPORT THE CI HALF-WIDTH AND THE NULL p95 BESIDE EVERY MARGIN.**

### HOW WE WOULD KNOW IT FAILED — pre-register which fired
- **(a)** The strong learned arm still loses to the counting floor → **the route is genuinely
  exhausted and this is a PASS.** Say so plainly; that is the result the owner asked for.
- **(b)** It wins, but only *fitted* → you re-measured a ceiling, not built a mechanism.
- **(c)** It wins on covered words and coverage is too low to matter → **the coverage number is the
  headline.**
- **(d)** Neither arm clears the floor → the comparison is void; report the floor, not the winner.
- **(e)** You cannot build a stronger learned arm than the sixteen → **that is itself an answer, and a
  publishable one.** Write down what you tried and why each was not stronger.

🚫 **WHAT WILL NOT BE ACCEPTED:** a recommendation, a literature argument, a seventeenth weak
implementation, or a comparison where the two arms saw different populations.

---

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the supplied channel | `hdlab/grounded_similarity.py` (**12 z-scored dims; `GROUNDED_CAP=0.45`**) |
| the three supplied-side witnesses | `verification/test_sensorimotor_covers_the_verb_hole.py`, `..._which_number_is_the_meaning_asset.py`, `..._the_channel_cannot_gate_links_alone.py` |
| the learned channel | `hdlab/reading_grounding_loop.py`, `hdlab/substrate.py` |
| the definitional channel (built, unmeasured here) | `hdlab/definitional_extraction.py` |
| benchmarks | `data/encoder_eval_benchmarks/` (**SimVerb carries a WordNet relation column — see §3**) |
| 🚫 **DO NOT TOUCH** | `preregs/**`, any `arm_key*`, and **`GROUNDED_CAP`** — the cap sits below the link threshold on purpose |

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **`+0.0000` vs `+0.3107` as a subtraction.** Different coverage (2,651 vs 3,487 pairs). Quote it
  as *"ours is absent where this one is present, on the same benchmark"*.
- 🚫 **The same asset gives `+0.3107` / `+0.2676` / `+0.2463`** depending on entry point. **Measure the
  asset unclamped; ask what the substrate sees with `grounded_similarity()`. Never compare across.**
- 🚫 **"Motor for verbs, perceptual for nouns."** Only the verb half is established.
- 🚫 **WordNet's pooled `+0.543`.** It is reading its own selection.
- 🚫 **"The addressed slot is the fix."** I wrote that before testing it; it buys no signal.

---

## TLDR

We keep finding that our system is bad at working out word meanings by reading, and good at using
meanings we hand it. Sixteen separate measurements say so. The obvious conclusion is to stop trying
to learn from reading.

**The catch is that all sixteen tested a fairly crude attempt.** Showing a weak version fails does
not show the idea fails — and that is a mistake this project has been caught making before.

So instead of deciding by argument, the job is to build the best honest version of learning-from-
reading we can, and run it once against the best version of the alternative, on the same words, with
the same yardstick, both measured against the simple method that keeps beating us.

**If the good version still loses, we close the door with evidence and stop drifting.** If it wins,
we nearly threw away the more interesting half of the project. Either answer is worth having; what we
have now is neither.

One warning in the other direction, from today: the "handed knowledge wins" side is easy to
over-credit. One resource looked twice as good as ours until we noticed the test had been built out
of that same resource.

## QUESTIONS

None. **The board is empty — this brief is what the owner asked for instead of an answer from me.**

## NEXT STEPS

1. Read the priority-1 brief's orientation map first; it holds six measurements about the supplied
   side and records two pieces of advice I wrote before testing them.
2. Write down what makes your learned arm stronger **before** running it.
3. Report both arms with floors and intervals, whichever way it goes.
