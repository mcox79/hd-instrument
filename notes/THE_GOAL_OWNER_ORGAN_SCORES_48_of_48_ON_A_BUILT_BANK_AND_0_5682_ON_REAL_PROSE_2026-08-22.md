# **THE PROMOTED GOAL-OWNER ORGAN SCORES `48/48` ON ITS CONSTRUCTED BANK AND `0.6136` ON REAL PROSE -- BELOW `majority` (`0.7273`) AND `first_mention` (`0.7955`), WHICH WERE DOCUMENTED IN THE SAME REPO ALL ALONG.**

> ## 🔻 **CORRECTED WITHIN THE HOUR, BY ME: THE FIRST VERSION OF THIS NOTE SAID `0.5682`.**
> **I scored against `goal_owner` (who WANTS the thing). The documented baselines score against
> `gold_outcome_owner` (whose OUTCOME it is) -- their `gold` field matches it `44/44` and matches
> `goal_owner` only `41/44` -- and `gold_outcome_owner` is also the right field for a function named
> `select_outcome_owner`. The two fields differ on 3 of 44 items.**
> **CORRECT FIGURE: `27/44` = `0.6136`.** *The finding stands -- still below `majority` and `-0.1818`
> below `first_mention` -- but two things change:*
> 1. *the gap is `-0.1818`, not `-0.2273`;*
> 2. 🔻 ***THE EXACT TIE WITH `recency` (both `25/44`) WAS AN ARTIFACT OF MY WRONG GOLD FIELD AND
>    DISAPPEARS.** I built a whole "is it recency in disguise?" analysis on a coincidence I had
>    manufactured. The per-item agreement numbers below are still real measurements of BEHAVIOUR;
>    the tie that motivated computing them was not.*
> **Second gold-field category error in one session** -- the first gave a flat `0/44`, which was
> obviously wrong; this one gave a plausible number, which is worse.

**The comparison had never been made, because the organ's witness reports NEVER-TYPED COUNTS and
NON-REGRESSION -- not accuracy against the floors sitting in the bank's own baselines file.**

---

## 1. THE TWO POPULATIONS

| | |
|---|---|
| `goal_owner_fair_v1` (constructed) | ✅ **content `48/48`**, positional `47/48` |
| multigoal coherence bank | ✅ **content `12/12`**, positional `6/12` |
| 🔻 **`goal_bearing_modern_eval_v1`, REAL PROSE, 44 items** | 🔻 **`25/44` = `0.5682`**, and **`13/44` produce NO prediction at all** |

## 2. AGAINST THE FLOORS THE REPO ALREADY RECORDED

| | accuracy |
|---|---|
| `first_mention` | **`0.7955`** |
| `majority` | `0.7273` |
| **OUR PROMOTED SELECTOR** | 🔻 **`0.5682`** |
| `recency` | `0.5682` |
| `nearest_subject` | `0.2955` |

> # **`-0.2273` BELOW THE STRONGEST DOCUMENTED FLOOR, AND BELOW "GUESS THE MAJORITY" TOO.**

*Even if all 13 non-predictions were right, the ceiling is `38/44` = `0.8636`.*

## 3. 🔑 **THE EXACT TIE WITH `recency` IS A COINCIDENCE, AND I CHECKED RATHER THAN ASSUMING**

*`0.5682` is `25/44` for BOTH our selector and the recency baseline. That invites "the organ is just
recency in disguise" -- the reduces-to-a-trivial-rule hypothesis this project takes seriously.*
**Agreement, item by item, on the 31 items where ours predicts:**

| | agreement |
|---|---|
| with `recency` | **`17/31` = `0.548`** |
| with `first_mention` | **`23/31` = `0.742`** |

🔻 **IT IS NOT RECENCY.** *It behaves most like `first_mention` (74%) while scoring 23 points worse --
so **where it departs from first-mention, it departs wrongly.*** **An accuracy tie is not a behavioural
tie, and only the per-item agreement can tell them apart.**

## 4. WHY THIS WAS NEVER SEEN

**The organ's own witness (`verify_speaker_attribution_goal_holder_2a_part2.py`) is thorough and passes
-- it checks `before_never_typed=15/44 -> after=13/44`, names the two recovered items, verifies
`29/44` already-resolvable picks are byte-identical, and confirms no regression.** *All of that is
about CHANGE, not LEVEL.* **Nothing in it computes accuracy on those 44 items, and the baselines live
in a different file (`goal_bearing_modern_eval_v1_baselines.json`) written for a different sub-task
comparison.** ➡️ **Two halves in one repo, never multiplied together.**

## 5. ⚠️ LIMITS

1. **n=44.** *`0.5682` vs `0.7955` is 10 items; the ordering is clear, the exact gap is not.*
2. **My matching is string-based** (`pred == gold`, or either containing the other). *A stricter or
   looser rule moves the number; I used the same leniency for ours and for the baselines.*
3. **`roster` is passed from the bank's own metadata**, as the organ's docstring requires (gold-free).
4. 🔻 **I FIRST SCORED THE WRONG FUNCTION.** *`find_desired_state(...)["referent"]` returned `wanted`,
   `head`, `courage`, `piano` -- the THING DESIRED, not the PERSON desiring -- giving a flat `0/44`.
   **An exactly-zero score with 28 non-empty predictions is a category error, not a capability
   finding**, and the standing "exactly zero is a reachability failure" rule is what stopped me
   reporting it.*

## TLDR

We have a component whose job is to work out **which character in a story wants something**. On the
purpose-built test set it was developed against, it is perfect: 48 out of 48.

**On real story passages it gets 25 out of 44 — worse than simply always guessing the most common
answer, and much worse than a one-line rule that just picks the first character mentioned.** Those
comparison numbers were already written down in this repository, in a file next to the test data.
Nobody had put the two side by side.

**It also gives no answer at all on 13 of the 44.** Even if every one of those were right, it still
wouldn't reach the simple first-mention rule.

**One thing I checked rather than assumed:** its score is *identical* to a "pick the most recent
character" rule, which looks like the component secretly being that rule. It isn't — comparing answer
by answer, it agrees with recency only about half the time and with first-mention three-quarters of
the time. **It behaves like the first-mention rule but makes worse choices where it differs.**

**Why nobody noticed:** the component's own test is careful and passes, but it checks whether recent
changes broke anything and how many items it can answer — never how often it is right compared to the
simple alternatives. Both halves were in the repo; nobody multiplied them together.

**And I got it wrong first:** I initially scored the wrong function and got a flat zero out of 44. A
perfect zero with plenty of non-empty answers is a sign you asked the wrong question, not a discovery.

## QUESTIONS

None — Q106 (the scoring sheet) remains the only open one.

## NEXT STEPS

1. ⚠️ **`first_mention` (`0.7955`) is now the floor any goal-owner claim must clear on real prose.**
   *The `48/48` figure is a constructed-bank number and may not be quoted as owner-selection ability.*
2. 🎯 **The 13 non-predictions are the cheapest lead** -- *a third of the bank gets no answer, and the
   organ's own witness already tracks that count (15 -> 13) without asking what it costs.*
3. *Method note: **the repo held the organ's score and the baselines in separate files for two weeks.**
   The finding needed no new data -- only putting two existing numbers on the same population.*
