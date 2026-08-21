# **THE FORM CHANNEL SCORES 1.0000 ON IDENTIFICATION -- WHICH PROVES THE TASK IS A LOOKUP, NOT THAT THE CHANNEL IS GOOD. THIS IS THE "BETTER INDEX" RISK IN ITS PUREST FORM, AND IT DE-RISKS Q102 BY INVALIDATING MY OWN BENCHMARK.**

**I filed Q102 recommending we wire the spelling-based recognition organs, and flagged the risk that
it would produce "a better index rather than better understanding". This measurement was meant to
test that risk. It answers it -- by showing the benchmark I would have used is circular.**

---

## 1. THE MEASUREMENT

*80 lemmas, 8 held-out probes each, chance 0.0125.*

| channel | hit@1 |
|---|---|
| CONTEXT (accumulated masked context, the live path) | 0.1141 |
| **FORM (`CharTrigramEncoder` spelling code)** | **1.0000** |

| error overlap | |
|---|---|
| both right | 0.1141 |
| **CONTEXT right, FORM wrong** | **0.0000** |
| FORM right, CONTEXT wrong | 0.8859 |
| both wrong | 0.0000 |

## 2. 🚫 **WHY THE 1.0000 IS A TAUTOLOGY AND NOT A RESULT**

***The task is "which of 80 words is this?" and the form code IS a function of the word's spelling.
The query and the answer are the same object. A perfect score was guaranteed before the code ran.***

**So the strict domination -- not one case where context is right and form is wrong -- is not
evidence that form is a better representation. It is evidence that IDENTIFICATION IS NOT A TEST OF
IT.** *I nearly reported "form beats context 1.0000 to 0.1141" as a finding.*

## 3. ✅ **WHAT THIS ACTUALLY SETTLES FOR Q102**

**The risk I flagged was: wiring form gives "a better index rather than better understanding".**
***This shows the index is PERFECT and therefore uninformative -- so the decision cannot be judged on
any identification-style metric at all. It must be judged on MEANING.***

**And on meaning, the archive already has the alarming number:**

> **pure SPELLING beats our MEANING read-out at rank 1 -- `0.0767` vs `0.0480`, surviving the
> strictest tie convention, with the substrate arm at 0.0% ties so no defence is available.**

*A form code outscoring a meaning code ON A MEANING TASK is exactly the confusion `notes/PLAN.md`
names as foundational: "a spelling-derived code is a FORM code, and we have been calling it a meaning
code... that single confusion explains why a spell-checker beats us."*

## 4. ➡️ **THE SHARPENED VERSION OF THE Q102 TELL**

**Before this: "watch for recognition rising while meaning stays flat."**
**After this, sharper and checkable:**

> ### **THE FORM CHANNEL WILL SCORE PERFECTLY ON ANY TASK WHERE THE WORD IS THE ANSWER. IT MUST THEREFORE BE EVALUATED ONLY ON TASKS WHERE THE WORD IS THE *QUESTION* -- what it means, what it resembles, what follows from it. Any evaluation it wins trivially is an evaluation that cannot inform the wiring decision.**

*That is a stronger and more useful caution than the one I filed, and it comes from a measurement
whose headline number is worthless.*

## TLDR

I recommended switching on the components that recognise words by their spelling, and flagged one
worry: that it would make the system better at *looking things up* rather than better at
*understanding*. **This was meant to test that worry. It settles it in an unexpected way — by showing
the test I was about to trust is meaningless.**

The spelling channel scored **perfectly** — 100%, against 11% for the current approach, with not a
single case where the current approach won.

**That sounds decisive and it proves nothing.** The task was "which word is this?", and a
spelling-based code is *derived from the word's spelling*. **The question and the answer are the same
thing.** It couldn't have scored anything else.

**So the useful outcome is a rule rather than a number:** the spelling channel will score perfectly on
any test where the word itself is the answer. **It can only be judged on tests where the word is the
question** — what it means, what it's similar to, what follows from it.

**And on that kind of test we already have a troubling result:** spelling alone already beats our
meaning read-out. Our own planning document names this exact confusion as foundational — we built a
recognition code and have been treating it as a meaning code, which is why a spell-checker beats us.

**So the decision stands, with a sharper warning than I first gave.** Connecting these components is
still probably right, since recognising a word and understanding it genuinely are separate jobs. But
**any evaluation it wins easily is an evaluation that can't tell us whether it helped.**

## QUESTIONS

*Q102 remains open and unchanged in its recommendation; only its risk section is sharpened by this.*

## NEXT STEPS

1. **Never evaluate the form channel on identification.** *It is a lookup and scores 1.0000 by
   construction.*
2. **Judge it only where the word is the QUESTION** -- meaning, similarity, entailment. *The
   archive's `0.0767 vs 0.0480` is the relevant prior, and it is not reassuring.*
3. *Recorded because I nearly filed it as a finding: a perfect score is usually a sign the task is
   broken, not that the method is good. Same shape as the D3 self-test reading 1.000.*
