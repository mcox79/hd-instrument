# **I DID NOT RUN THE OBVIOUS NEXT EXPERIMENT. TWO MEASURED REASONS, BOTH FOUND BEFORE WRITING ANY OF IT: THE CLEAN VERSION IS UNDERPOWERED AT n=40, AND THE POWERED VERSION IS ALREADY DONE TWICE.**

**Tonight established that the masked context vector carries WORD-IDENTITY signal (0.1549 vs a
strongest floor of 0.0179, CI-separated, on source-balanced lemmas). The obvious follow-on is
whether it carries MEANING signal on that same population. Here is why that is not the next move.**

---

## 1. REASON ONE -- **THE CONFOUND-FREE VERSION IS UNTESTABLE AT THIS n**

*SimLex-999 pairs where BOTH words clear each bar, measured on the same 60,000-sentence shelf:*

| requirement | usable pairs |
|---|---|
| both words have **>=41 sentences** | **533** ✅ |
| both words are **SOURCE-BALANCED** (<=50% from one corpus) | **40** 🚫 |

***The balanced population -- the only one free of the book confound I measured tonight -- yields 40
pairs.*** **A rho on 40 pairs would have a CI wide enough to contain almost any answer, so the run
could not have failed informatively.** *That is the "could this experiment have succeeded?" question,
asked before rather than after, and the answer is no.*

## 2. REASON TWO -- **THE POWERED VERSION IS ALREADY MEASURED, WITH BETTER CONTROLS THAN I PLANNED**

*`exp_meaning_asset_vs_production_v1`, the FULL SimLex column at d=256, disk-verified:*

| arm | SimLex rho | what it is |
|---|---|---|
| `A_PLANTED_SEMANTIC` | **0.9269** | ✅ **positive control -- the readout CAN detect meaning** |
| **`P_LIVE_CONCEPT`** | **0.1048** *(CI `[-0.0073, +0.2126]`, n=322, CROSSES ZERO)* | **ours** |
| `C_CONCEPT_SHUFFLED` | -0.0092 | our shuffle control |
| `A_ORTHOGRAPHIC` | **-0.0122** | ✅ **a PURE spelling encoding scores ZERO on meaning** |

**That is a validated-end-to-end readout with a positive control, a shuffle control and an
orthographic control -- a better battery than the one I was about to build.**

**AND A POWER EXTENSION OF IT ALREADY EXISTS**
(`exp_meaning_asset_power_extension_v2_paired`), which is *precisely* the "raise n from 322" move the
crossing CI invites. **Seventh prior-work catch tonight.**

## 3. ⚠️ WHAT REMAINS GENUINELY OPEN, STATED SO IT IS NOT MISTAKEN FOR CLOSED

***`P_LIVE_CONCEPT`'s CI crosses zero. The meaning question is UNRESOLVED, not answered negatively.***
**What is closed is that MY PROPOSED RUN would resolve it** -- the clean version cannot (n=40), and
the powered version has been run twice.

*The move that WOULD resolve it is a corpus-balanced shelf, not a corpus-balanced SELECTION from this
shelf: 40 usable pairs is a property of reading nine separate books, and no re-analysis fixes it.*

## TLDR

Tonight I showed that when our system hides a word, what's left still carries real information about
*which* word it was. **The obvious next question is whether it carries information about what the
word MEANS.** I checked whether that experiment could work before building it, and it can't — for two
separate reasons.

**First, the clean version has almost no data.** To avoid the "which book" problem I found earlier, I
need word pairs where both words appear across many books. **Out of 999 standard test pairs, only 40
qualify** — far too few to conclude anything either way.

**Second, the version with enough data has already been run — twice — and with better checks than I
had planned.** It includes a deliberately meaningful encoding that scores 0.93, proving the test can
detect meaning at all, and a pure-spelling encoding that scores zero, proving spelling can't fake it.

**What I want to be clear about:** the actual question is still open. Our system's score on that test
is small and its uncertainty range includes zero, so we don't know. **What's settled is that the
experiment I was about to run wouldn't have told us** — one version can't gather enough evidence, the
other has already been done.

**The real fix isn't a cleverer analysis. It's a broader reading list** — 40 usable pairs is a
consequence of having read nine separate books, and no amount of re-slicing changes that.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not propose "measure the masked/concept encoding against SimLex".** *Powered version done
   twice; clean version is n=40.*
2. **If the meaning question is to be resolved, the lever is CORPUS BREADTH**, not analysis. *Note
   that growth is PAUSED by standing decision, so this is a decision, not a task.*
3. *Method note: **the feasibility check cost one command and killed a run I would otherwise have
   spent an hour on.** It also caught my own SimLex parser returning 0 pairs -- the file is
   tab-separated with the score in column 4, and `split()` had been reading the POS tag.*
