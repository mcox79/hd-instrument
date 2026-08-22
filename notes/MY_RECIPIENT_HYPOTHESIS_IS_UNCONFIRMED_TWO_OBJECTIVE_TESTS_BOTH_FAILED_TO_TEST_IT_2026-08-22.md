# **I HAND-READ A PATTERN WHILE HOLDING THE HYPOTHESIS, THEN TRIED TWICE TO CONFIRM IT OBJECTIVELY AND BOTH TESTS FAILED TO TEST IT. THE CLAIM IS UNCONFIRMED AND I AM NOT BUILDING ON IT.**

**Separating what is objectively established from what rests on my own reading, because those two got
mixed together in the previous note and only one of them is safe to use.**

---

## 1. ✅ WHAT IS OBJECTIVELY ESTABLISHED (source code, no judgement)

```
hdlab/goal_typing.py:776   SUBJECT_IS_REFERENT_CLASSES = {...}
hdlab/goal_typing.py:777   OBJECT_IS_REFERENT_CLASSES  = {...}
```

**The goal-referent test recognises exactly two grammatical positions. There is no recipient,
beneficiary or possessor category.** *That is a fact about the code and it does not depend on any
interpretation of any story.*

## 2. 🔻 WHAT IS **NOT** ESTABLISHED: THAT THIS GAP CAUSES THE FAILURES

*My previous note claimed all 5 `referent_mismatch` errors -- and, extending it, 4 of 7 no-goal errors --
fail because the goal-holder sits in an unrecognised position. **I read those passages myself, AFTER
forming the hypothesis, knowing which items were wrong.** That is the exact condition under which
hand-classification confirms whatever it set out to find.*

**TEST 1 -- the bank's own owner annotations. INVALID: measures the wrong construct.**
`goal_owner` vs `gold_outcome_owner` differ on only **3 of 36** items (Fisher exact `p = 1.0000`).
*But that field encodes **whose outcome it is**, not **who performed the act** -- the brains are the
Scarecrow's outcome even though the Wizard hands them over. **This is not a refutation; it is a
non-test**, and reporting it as a refutation would have been as wrong as reporting it as support.*

**TEST 2 -- parse the outcome verb and take its subject. TOO WEAK: could not locate the verb.**

| | n | correct | wrong |
|---|---|---|---|
| 🔻 **`NO_VERB_FOUND`** | **22** | 11 | 11 |
| `PRONOUN_UNRESOLVED` | 6 | 2 | 4 |
| `SUBJECT_IS_OTHER_NOUN` | 5 | 2 | 3 |
| `SUBJECT_IS_GOAL_OWNER` | 3 | 2 | 1 |

***The locator fails on 61% of items***, and the non-owner bucket is contaminated with contraction
fragments (`he's`, `we'll`, `they're`) rather than real subjects. **It also never reached the two
clearest cases -- the Scarecrow and the Tin Woodman.** *A test that misses the items the hypothesis is
about cannot speak to the hypothesis.*

## 3. 🔑 SO THE HONEST STATE

| claim | status |
|---|---|
| the referent test knows only SUBJECT and DIRECT OBJECT | ✅ **established, from source** |
| a project about goals lacks the RECIPIENT role | ✅ **established** |
| **the 5+4 failures are CAUSED by that gap** | 🔻 **UNCONFIRMED -- one biased hand-read, two failed objective tests** |
| the fix would clear the floor | 🔻 **NO -- ceiling `0.6111` on the 5, established independently** |

> # **A MECHANISM GAP I CAN PROVE, AND A CAUSAL STORY I CANNOT. THE TEMPTING MOVE IS TO LET THE FIRST VOUCH FOR THE SECOND.**

## 4. WHAT WOULD ACTUALLY TEST IT

1. **A working outcome-verb locator** -- the current one fails on 61% of items, which is its own finding
   and probably worth more than the hypothesis it was built to test.
2. **Blind classification** -- items shuffled, correctness hidden, positions labelled, THEN joined.
   *I cannot do this credibly myself now: I have read all 36 and remember which failed.*
3. **A positive control** -- construct passages where the goal-holder IS the subject and check the
   mechanism succeeds on them. *If it fails there too, the position hypothesis is dead regardless.*

## 5. LIMITS

1. **Both failed tests are MY probes, written quickly.** *Test 2's weakness is a defect in my locator,
   not evidence about the cascade.*
2. **The hand-read pattern may well be right.** *"Unconfirmed" is not "refuted" -- five-for-five is
   striking. It is simply not evidence I am entitled to lean on given how it was produced.*
3. **n=36 throughout.**

## TLDR

Last note I said I had found the root cause: the system looks for the character in only two places in a
sentence — who did the action, and who it was done to — and misses cases where somebody else grants the
wish, like the Wizard giving the Scarecrow brains.

**Half of that is solid and half of it isn't, and I mixed them together.**

**Solid:** the code really does check only those two positions. I read the source; there is no third
category. A system built around whether wishes come true has no notion of "the person the thing was done
*for*". That stands.

**Not solid:** that this is what's causing the wrong answers. **I found that pattern by reading the
failing stories myself, after I'd already guessed the answer, and knowing which ones were wrong** — which
is the ideal way to find a pattern whether or not it's there.

So I tried twice to check it without my own judgement involved. **The first check measured the wrong
thing** — the data does record who each outcome belongs to, but the brains still belong to the Scarecrow
even though the Wizard hands them over, so that field can't tell me who *performed* the act. **The
second check couldn't find the relevant verb in 22 of the 36 stories**, including both of the clearest
examples.

**So I have a gap I can prove and a story about it I can't.** The tempting move is to let the proven half
vouch for the unproven half. I'm recording it this way so that doesn't happen quietly later.

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Fix the outcome-verb locator first** -- *failing on 61% of items, it is a bigger and more certain
   problem than the hypothesis it was written to test, and everything downstream needs it.*
2. 🚫 **Do not build the recipient-role check.** *Unconfirmed cause, and a ceiling of `0.6111` even if
   the cause is right.*
3. *Method note: **two objective tests, neither of which tested the thing.** Checking that a test can
   actually see the phenomenon -- before reading its result -- is the same "could this experiment have
   succeeded?" question that keeps paying, and I ran both of these before asking it.*
