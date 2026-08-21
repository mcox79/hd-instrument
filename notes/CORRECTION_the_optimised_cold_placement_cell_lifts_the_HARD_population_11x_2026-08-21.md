# CORRECTION -- **I QUOTED THE BASELINE AS THE STATE OF THE ART. ITS COMPANION CELL, LANDED THE SAME DAY, LIFTS THE HARD POPULATION 11x AND NEARLY ELIMINATES THE ABSTENTIONS.**

**An hour ago I reported `exp_cold_placement_usefulness_v1` and told the owner:** *"placing a word
exactly right happens only 3-15% of the time"* and *"for 31% of opaque words it proposes nothing --
that abstention set IS the reading list."*

**Both statements describe the BASELINE. `exp_cold_placement_recovery_opt_v1` landed THE SAME DAY,
2026-07-14, and is the optimised version of exactly that mechanism.**

---

## 1. WHAT THE COMPANION CELL ACTUALLY DID

| population | base exact | **optimised exact** | delta |
|---|---|---|---|
| **transparent** (decomposable), n=135 | 0.1488 | 0.1556 | **+0.0068 -- nothing** |
| **OPAQUE** (not decomposable), n=215 | **0.0262** | **0.2930** | **+0.2668, an 11x lift** |

**And the abstentions the previous note called "the reading list":**

| | base | **optimised** |
|---|---|---|
| opaque words the system refuses to place | **31%** (72 of 229) | **3.7%** |

**➡️ THE METHOD HELPS EXACTLY WHERE THE NAIVE APPROACH FAILED, AND NOWHERE ELSE.** *Transparent words
were already at their ceiling -- you can take them apart, and a better method cannot beat
decomposition. **The entire gain is on the population that could not be taken apart at all.***

**Relation-level, both HARD_PASS:** transparent `topk_rel` **0.5704**, opaque **0.4279**, against
random 0.0000, with `scramble_ok / random_ok / graph_self_reference_ok` all true.

## 2. ⚠️ TWO NUMBERS IN ITS OWN SUMMARY LINE THAT SHOULD NOT BE QUOTED

`ratio=570.3704` and `ratio=427.9070` are computed against `rnd_topk_rel = 0.0000` -- **a division by
an epsilon, exactly like the `148.76` I flagged in the companion cell.** *Use the absolute rates and
the deltas; the ratios are artifacts of a zero floor.*

## 3. AND THE HOP TABLE IS **NOT** IN THIS CELL

Every `reach_frac_h1/h2/h3` in the optimised cell reads **0** -- the hop metric was simply not
computed there. **So the two cells are complementary, not sequential:**

| cell | what it measures |
|---|---|
| `..._usefulness_v1` | **the HOP structure** (h1/h2/h3) on the baseline method |
| `..._recovery_opt_v1` | **exact + relation-level** on the optimised method, **no hops** |

**➡️ NOBODY HAS EVER MEASURED THE HOP PROFILE OF THE OPTIMISED METHOD.** *The "signal lives at one
hop, decays to the popularity floor by three" finding I reported is a property of the BASELINE. It
may or may not hold for the version that is 11x better on opaque words -- and that is a genuinely
open, cheap question.*

## 4. 🔁 THE PROCESS FAULT, WHICH IS THE FIFTH OF THE NIGHT IN THE SAME FAMILY

**I found one cell, read it thoroughly, and did not check whether it had a companion.** The two sit
adjacent in the same query result -- `experiment_index.py query "cold placement"` returns **4 cells,
and I opened one.**

*`CLAUDE.md` already carries this: **notes go stale -- re-verify before citing.** What it does not
say, and what cost me here, is the narrower version:* **A CELL NAMED `..._v1` IS NOT NECESSARILY THE
LATEST WORD ON ITS OWN QUESTION -- READ EVERY CELL THE QUERY RETURNED BEFORE QUOTING ANY OF THEM.**
*Four rows, and the fourth reversed the headline of the first.*

## TLDR

I need to correct what I told you an hour ago.

I reported that the system places new words exactly right only 3–15% of the time, and that for about a
third of the hard cases it gives up entirely — and I said that give-up list was the reading list you
remembered.

**Those were the numbers from the first attempt. A second experiment, landed the same day, improved
the hard cases elevenfold** — from under 3% to **29%** — and cut the give-up rate from **31% to under
4%**.

**And it did nothing at all for the easy cases.** That's the interesting part: words you can take
apart, like *sunflower*, were already being handled as well as they ever would be. **Every bit of the
improvement went to the words that can't be taken apart** — exactly where the simple approach had
nothing to offer.

Two smaller notes. Its summary line advertises "570 times better than random", which is a
divide-by-zero artifact and should be ignored — same flaw I flagged in the first cell. And **the
hop-counting analysis I described earlier was only ever run on the weaker version**; nobody has
measured how many hops the improved method needs. That's an open and cheap question.

**The mistake was mine and it's a simple one:** I searched, got four results, read one thoroughly,
and reported it. **The fourth result reversed the headline of the first.**

## QUESTIONS

None.

## NEXT STEPS

1. **Withdraw "the 72-word abstention set is the reading list"** -- the optimised method abstains on
   under 4%.
2. **Run the hop profile on the OPTIMISED method** -- it has never been done, and the one-hop finding
   may not survive an 11x change in the hard population.
3. **Read the remaining two cells** in that query before quoting either of these.
