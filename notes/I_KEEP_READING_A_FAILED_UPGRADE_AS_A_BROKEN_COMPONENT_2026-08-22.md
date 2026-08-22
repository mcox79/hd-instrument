# **CORRECTION: THE PRESCRIBED FIX'S INPUTS ARE *NOT* BROKEN. I READ TWO FAILED *UPGRADES* AS TWO BROKEN COMPONENTS -- WHICH IS THE FOURTH TIME TONIGHT I HAVE MADE THAT EXACT MISTAKE.**

**Last turn I concluded the frontier was blocked because its two inputs had `HARD_FAIL`ed. The inputs
exist and the charter calls them FAITHFUL.**

---

## 1. 🔻 WHAT I GOT WRONG

*I wrote: "the prescribed replacement is unattempted because the two things it consumes do not work
yet", citing two `HARD_FAIL`s and a `NO_GO`.*

**RE-READING THE SAME SUMMARIES:**

| cell | what it actually says |
|---|---|
| `..._learned_stateful_write_v1` | *"learned-write **<= MAIN_ENC** on ALL 3"* -- **a LEARNED variant failed to beat the EXISTING encoder** |
| `..._learned_identity_head_v1` | *"**no better than frozen baseline**"* -- **explicitly measured AGAINST a working frozen component** |
| `extraction_quality_gate_neural_..._v1` | **`NO_GO` on a NEURAL UPGRADE** -- *`fastcoref` installs clean, crashes at model-load on transformers 5.10.1 version-skew* |

> ### **ALL THREE ARE FAILED ATTEMPTS TO IMPROVE ON SOMETHING THAT ALREADY WORKS. A BASELINE THAT AN UPGRADE FAILS TO BEAT IS, BY CONSTRUCTION, A WORKING BASELINE.**

## 2. ✅ AND THE CHARTER SAYS SO DIRECTLY

*`SUBSTRATE_CHARTER_read_first.md`, 2026-08-04/05 -- the file I am instructed to read FIRST:*

> *"CORRECTED a wrong premise (**coref is FAITHFUL/Centering-Cb**, never 'recency-falsified')...
> **3/6 components are faithful (coref, situation-model binding, select+abstain)**"*

***BOTH INPUTS THE CHARTER PRESCRIBES ARE ON ITS OWN LIST OF FAITHFUL COMPONENTS.*** **The neural coref
that returned `NO_GO` was never the prescribed one -- the charter names Centering-Cb, which we own.**

## 3. 🔑 **THE PATTERN, AND IT IS THE FOURTH INSTANCE TONIGHT**

| # | what I called it | what it was |
|---|---|---|
| 1 | *"the body-part gap is the architecture failing on open vocabulary"* | **a hole the authors dug ON PURPOSE to measure it** |
| 2 | *"the `== "UNK"` guard is a harm detector switching off for violent verbs"* | **a deliberate HAND-OFF to the governor stage** |
| 3 | *"the more correct lookup makes the pipeline worse -- the consumer is calibrated on its error"* | **retracted; `arm` scores correctly** |
| 4 | *"the prescribed fix's inputs are broken"* | **two FAILED UPGRADES to components the charter calls FAITHFUL** |

> # 🔑 **I KEEP READING "AN ATTEMPT TO IMPROVE X FAILED" AS "X IS BROKEN". THE ARCHIVE IS FULL OF HONEST NEGATIVE RESULTS ABOUT UPGRADES, AND I HAVE BEEN MINING THEM AS EVIDENCE OF DECAY.**

***THE TELL IS ALWAYS PRESENT IN THE SUMMARY LINE ITSELF*** -- *`<= MAIN_ENC`, `no better than frozen
baseline`. **Both name a baseline that works.** A failure report that cites a comparator is a report
about the comparator's rival, not about the comparator.*

## 4. ➡️ WHAT THIS CHANGES

✅ **THE PRESCRIBED BUILD IS NOT BLOCKED BY MISSING INPUTS.** *The faithful Centering-Cb coref and the
maintained SituationModel both exist; the failures were attempts to LEARN better versions of them.*

⚠️ **BUT IT IS ALSO NOT OBVIOUSLY EASY.** *The learned upgrades failed for a reason -- the identity head
scored `1.000` on training entities and `0.672` held-out, which is memorisation, so **generalising
entity identity to unseen entities is genuinely hard.** The frozen version works; making it better did
not.*

🔻 **AND MY "REAL BLOCKING ITEM" FROM LAST TURN IS WITHDRAWN.** *I named "the maintained situation model
generalising to unseen entities" as the blocker. **That is the blocker for the LEARNED UPGRADE, not for
the prescribed build**, which uses the frozen one.*

## 5. ⚠️ LIMITS

1. **I have not verified the frozen components RUN today** -- *only that the charter calls them faithful
   and that the failed upgrades measured against them.*
2. **`MAIN_ENC` and "frozen baseline" are quoted from summary lines**, *not traced to the modules they
   name.*
3. **The charter statements are dated 08-04/08-05** *and I have not checked for supersession.*
4. **This corrects an interpretation. No measurement is retracted.**

## TLDR

Last turn I told you the next build was blocked because the two things it needs are broken. **That is
wrong, and I should have caught it from the sentences I was already quoting.**

Both failures say, in their own summary lines, that a *new learned version* failed to beat the *existing
version* — "no better than the frozen baseline". **A thing that a new attempt fails to beat is a thing
that works.** And the document I am told to read first lists both of them among the components it calls
faithful.

**This is the fourth time tonight I have made the same mistake**: reading an honest negative result about
an attempted improvement as evidence that something is broken. The archive is full of careful reports
saying "we tried to make X better and could not", and I have been repeatedly mining them as "X is
broken".

**What genuinely changes:** the next build is not blocked for want of parts. **What I should not
overclaim:** it is not therefore easy — the attempt to learn a better entity-tracker memorised its
training examples and failed on new ones, so that problem is real. It just is not in the way.

## QUESTIONS

None.

## NEXT STEPS

1. **Verify the frozen Centering-Cb coref and the maintained SituationModel actually RUN today** *--
   limit 1. That is the honest precondition, and it is cheap.*
2. **Then the prescribed build is unblocked** *-- feed both as the extraction context in place of the
   local window.*
3. *Method note: **"we could not improve X" is the most common sentence in this archive, and I have been
   reading it as "X is broken" all night.** The tell is that the sentence names a comparator.*
