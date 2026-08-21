# **SIX READS OPEN EIGHT OF TWENTY-EIGHT CORPORA, IN STRICT ALPHABETICAL ORDER. ALL SIX TEXTBOOKS ARE AMONG THE TWENTY NEVER OPENED. THE 2026-08-19 FIX WORKS AND IT IS EXPLICITLY THE CHEAP HALF.**

**Measured, not inferred: `remaining()` diffed per corpus across six `Substrate.read()` calls.**

---

## 1. WHAT SIX READS ACTUALLY OPEN

| call | corpora opened |
|---|---|
| 1 | `alice_in_wonderland` |
| 2 | `anne_of_green_gables`, `arc` |
| 3 | `breadth_v1` |
| 4 | `graded_readers_grade1` |
| 5 | `graded_readers_graded`, `litbank_coref_conll` |
| 6 | `little_women` |

**8 of 28 opened. 20 NEVER OPENED**, including **every one of the six textbooks** (anatomy,
biology, microbiology, psychology, chemistry, concepts-biology), plus `simplewiki`, `race`,
`onestop`, `social_iqa`, `sherlock_holmes`, `worldtree`.

> ### **THE TRAVERSAL IS STRICTLY ALPHABETICAL. `a` -> `b` -> `g` -> `l`, one or two patches per call.**

## 2. ✅ THE 2026-08-19 FIX IS WORKING -- AND IT SAYS ITSELF THAT IT IS HALF

*`substrate.read`'s own comment:* **"SKIP DRAINED PATCHES, AND DO NOT RESTART AT THE ALPHABETICAL
HEAD EVERY CALL... this is the concrete cost of that, and the cheapest half of the fix."**

**The `_patch_cursor` demonstrably does its job:** *call 1 opens alice, call 6 opens little_women --*
**it no longer re-enters the same three books forever, which was the failure that "looked exactly
like a learning ceiling".** ***What it does NOT do is CHOOSE. It advances a pointer along a sorted
list.***

## 3. 🎯 **WHY THE ORDERING IS NOT COSMETIC: THE BEST-GROUNDING MATERIAL SORTS LAST**

**This project's own recorded finding (board Q78, my own earlier claim to the owner): *"dense
technical writing grounds about three and a half times better than general reading material."***

***Every dense technical corpus we own begins with `t` for textbook, `s` for simplewiki, or `w` for
worldtree. Every novel and school reader begins with `a`, `b`, `g`, `l`, `m` or `s`.***

> ### **SO A SHORT READING SESSION READS ALICE IN WONDERLAND AND ANNE OF GREEN GABLES, AND NEVER REACHES THE BIOLOGY TEXTBOOK -- BECAUSE `a` SORTS BEFORE `t`.**

**That is not a foraging decision. It is `sorted()`.**

## 4. ⚠️ WHAT I AM NOT CLAIMING

1. **NOT that the fix failed.** *It fixed the thing it named and says plainly it is half.*
2. **NOT that alphabetical is worse than any specific alternative** -- *I have measured the ORDER, not
   the OUTCOME of changing it. That the best material sorts last is an argument for MEASURING a
   change, not for assuming one.*
3. **NOT a new architectural finding.** *`ORGAN_MAP`/plan already record that the forager's rule is
   MVT, a LEAVE rule, **silent on WHERE TO GO**, and that patch-CHOICE is the UNPINNED half.*
   **What is new is the measured size of the consequence: 20 of 28 unreached in six reads.**
4. **I have NOT changed the live reader.** *Changing what the substrate reads is a live-path build,
   not a diagnostic, and it belongs behind a can-fail test rather than my judgement at 11pm.*

## TLDR

Our reader picks what to read next **in alphabetical order**. I measured it: six reading sessions
opened eight of our twenty-eight sources — Alice in Wonderland, Anne of Green Gables, a couple of
graded readers — and **never reached any of our six textbooks.**

A fix two days ago stopped it re-opening the same three books forever, and that fix works. **But it
only moves a pointer down a sorted list; it does not choose.**

**Why that matters: we measured earlier that dense technical writing teaches this system about three
and a half times better than general prose. Every one of those technical sources begins with a letter
near the end of the alphabet.** So a short session reads storybooks and never opens the biology
textbook — **not because anything decided that, but because "a" comes before "t".**

**What I'm not saying:** that shuffling the order would help. I've measured the order, not the
outcome of changing it. That's an argument for testing a change, not for making one — **and I have
not touched the live reader**, because changing what the system reads deserves a real test rather
than my judgement late at night.

## QUESTIONS

None. *This is a measurement and a recommendation, not a decision needing you.*

## NEXT STEPS

1. **The candidate change is patch CHOICE, which the plan already carries as the UNPINNED half of the
   foraging organ.** *This note supplies the missing number for it: 20 of 28 unreached in six reads.*
2. **Any such change needs a can-fail test** -- *e.g. does reaching the textbooks earlier raise
   grounding quality, or merely change which words we fail on?*
3. *Method note: **the measurement was a `remaining()` diff, not a claim read off the code.** The
   code's comment said the fix was half; only running it showed which half and how much.*
