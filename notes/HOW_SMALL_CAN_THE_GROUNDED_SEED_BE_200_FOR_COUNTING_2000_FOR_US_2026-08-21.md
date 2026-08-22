# **HOW MANY WORDS MUST BE GROUNDED BEFORE THE REST COME FREE? ~200 FOR COUNTING. MORE THAN 2,000 FOR US. A 10x SEED-EFFICIENCY GAP -- AND BOTH SATURATE.**

**This turns the neighbour read-out from a property of the space into a PRICE.** *`tools/how_small_can_the_grounded_seed_be.py`.*

> **CONFIG:** *28 corpora, 286,069 sentences, 41 sentences/word, 3,000 words, `K=min(25,seeds)`.*
> **The HELD-OUT SET IS FIXED AT 1,000 WORDS AND IDENTICAL AT EVERY SEED SIZE**, seeds drawn from the
> disjoint 2,000, 5 independent draws per size. *If the evaluation population moved with the seed
> size the curve would be uninterpretable -- that is the "queries grew with the depth" error already
> made once tonight.*

---

## 0. 🔻 **TWO DEFECTS IN MY OWN SCRIPT, STATED BEFORE ANY NUMBER IS READ**

1. **THE 25-SEED ROW IS A HARNESS ARTIFACT, NOT A MEASUREMENT -- IT IS EXCLUDED.** *At `seeds=25`,
   `K=min(25,25)=25`, so every held-out word's "neighbourhood" is ALL the seeds and the prediction is
   the SAME CONSTANT for every word. A rank correlation with a constant is undefined and my helper
   returns `0.0`.* **It printed `0.0000` for BOTH arms AND the null -- the exactly-zero signature this
   project already documents as a REACHABILITY FAILURE. Reading it as "25 seeds buys nothing" would
   have been a fabricated negative.**
2. ⚠️ **THE `null95` COLUMN IS COMPUTED ON CONCRETENESS ONLY.** *It validly gates the Concreteness
   column. **Beside `MEAN15` it is INDICATIVE ONLY** and no MEAN15 row may be called "clears its null"
   on the strength of it.*

## 1. THE SWEEP

| arm | seeds | nearest seed | **Concreteness** *(gated)* | Valence | MEAN15 | null95 *(conc.)* |
|---|---|---|---|---|---|---|
| OURS | 50 | 0.2800 | **0.2114** | 0.0816 | 0.0952 | 0.1239 |
| OURS | 100 | 0.3013 | **0.2599** | 0.1247 | 0.1287 | 0.1264 |
| OURS | 200 | 0.3248 | **0.3539** | 0.1309 | 0.1628 | 0.1156 |
| OURS | 400 | 0.3478 | **0.3783** | 0.2163 | 0.2051 | 0.1021 |
| OURS | 800 | 0.3686 | **0.3914** | 0.2511 | 0.2246 | 0.1099 |
| OURS | 1600 | 0.3900 | **0.4325** | 0.2684 | 0.2570 | 0.0946 |
| **OURS** | **2000** | 0.3965 | **0.4323** | 0.3035 | **0.2638** | 0.0967 |
| IDF | 50 | 0.1067 | 0.3585 | 0.1541 | 0.1816 | 0.1890 |
| IDF | 100 | 0.1290 | **0.4477** | 0.1981 | 0.2460 | 0.1907 |
| **IDF** | **200** | 0.1499 | **0.5119** | 0.3065 | **0.2971** | 0.1752 |
| IDF | 400 | 0.1787 | **0.5295** | 0.3389 | 0.3285 | 0.1927 |
| IDF | 800 | 0.2061 | **0.5322** | 0.3593 | 0.3568 | 0.1346 |
| IDF | 1600 | 0.2339 | **0.5417** | 0.3753 | 0.3809 | 0.1265 |
| IDF | 2000 | 0.2415 | 0.5397 | 0.3728 | 0.3760 | 0.1254 |

## 2. 🎯 **THE ANSWER, ON THE PROPERLY-GATED COLUMN**

**CONCRETENESS, ours:** `50 seeds -> 0.2114` against a `0.1239` null -- **already clears.** *`100 ->
0.2599`, `400 -> 0.3783`, then it flattens: 400 to 2,000 is FIVE TIMES the grounding for `+0.054`.*

> ### **SO THE SEED DOES NOT NEED TO BE LARGE. ~50-100 GROUNDED WORDS ALREADY PROPAGATE, AND PAST ~400 MORE GROUNDING BUYS ALMOST NOTHING.** *That is the encouraging half and it is real.*

## 3. 🔻 **AND THE PRICE COMPARISON, WHICH IS THE HARD HALF**

> ### **IDF AT 200 SEEDS (`MEAN15 0.2971`) BEATS OURS AT 2,000 (`0.2638`). TEN TIMES THE GROUNDING TO NOT QUITE MATCH IT.**

**The standing "behind counting" position now has a COST reading: whatever grounding we buy, counting
turns it into roughly ten times as much reach.** *This is the sixteenth independent measure on which
counting leads.*

**BOTH SATURATE.** *IDF `1600 -> 2000` actually goes DOWN (`0.3809 -> 0.3760`). **More grounded words
is not the lever for either channel past ~400-800.***

## 4. 🔬 **THE DIAGNOSTIC I DID NOT EXPECT, AND IT NAMES A DEFECT**

***OUR SPACE HAS SYSTEMATICALLY HIGHER NEIGHBOUR SIMILARITY AND CARRIES LESS INFORMATION.***

| | nearest-seed cosine at 2,000 | MEAN15 |
|---|---|---|
| **OURS** | **0.3965** *(higher)* | **0.2638** *(worse)* |
| **IDF** | **0.2415** *(lower)* | **0.3760** *(better)* |

*The earlier read-out run measured the same thing on full neighbourhoods: mean top-1 cosine **OURS
0.4091 vs IDF 0.2598**.* **HIGH COSINE IN OUR SPACE IS NOT SEMANTIC PROXIMITY -- everything is
somewhat similar to everything, which is an ANISOTROPY / COMMON-MODE signature.**

⚠️ *`MEMORY.md` carries **"27 rank-1 common-mode removal"** on the DO-NOT-REDO list **with a revival
criterion (`*`)**. This may be revival evidence. **I have NOT read that entry's criterion and am NOT
claiming it is met** -- naming it as the next thing to check, not as a result.*

## 5. 🧭 **HOW THIS SITS AGAINST THE FRONTIER WORK ALREADY ON DISK**

*Read before building, per the standing rule:* `exp_frontier_distance` (2026-08-13) found **15,036 of
16,812 corpus lemmas UNREACHABLE (89%)** from the symbolic grounded core -- only 371 at distance 1.

***The reading-derived frontier has no unreachable words at all: every held-out word has a nearest
seed at every seed size.*** ⚠️ **BUT THAT IS NEARLY VACUOUS ON ITS OWN -- in a dense space everything
has a nearest neighbour. THE USEFULNESS IS THE CORRELATION, NOT THE CONNECTIVITY**, and at 50 seeds
our `MEAN15` is inside its (indicative) null. *The honest statement is that the two frontiers fail
differently: the symbolic one says "no path"; the reading one always offers a path and may offer a
useless one.*

⚠️ **DIFFERENT NEIGHBOURHOODS, NOT CONFLATED:** *the frontier notes use CO-OCCURRENCE neighbours
("words appearing alongside it"); this uses PROFILE-SIMILARITY neighbours (words used in similar
contexts -- second order).*

## 6. ⚠️ LIMITS

1. **The 25-seed row is excluded as degenerate** (section 0).
2. **`null95` gates Concreteness only**; MEAN15 has no valid null here.
3. **`K=25` still never swept** -- carried over from the previous run, still unaddressed.
4. **3,000 of 5,021 eligible words**, seeded cap.
5. **Seed draws are RANDOM.** *A real grounded core would be the FREQUENT and CONCRETE words, which
   is a much better draw. **This measures the price of a random seed and is therefore pessimistic.***
6. **No paired test between arms at any seed size**; the 10x claim rests on the curves, not a CI.

## TLDR

The last result showed that if you know the answer for a word's neighbours, you can work out the
answer for the word. **The obvious question was: how many words do we have to be told before the rest
come free?**

**Fewer than I expected.** Around fifty to a hundred grounded words already work, and past about four
hundred, extra grounding buys almost nothing. That is genuinely good news for the "ground a small
core and spread outward" idea.

**The bad news is the comparison.** Plain word-counting does more with two hundred grounded words than
our system does with two thousand. **Ten times the grounding, and we still don't match it** — the same
result we keep getting, now in the currency of how much work we'd have to do by hand.

**One unexpected clue.** In our system words look *more* similar to each other than they do under
counting, and yet our similarity is *less* informative. Everything is a bit like everything, which
means high similarity isn't telling us much. There's a shelved fix for exactly that pattern and I've
flagged it to look at — without claiming it applies yet.

**Two things I got wrong in my own script**, both caught and both reported above: the smallest test
size produced a meaningless number that looked like a real zero, and the noise floor I printed only
applies to one of the columns.

## QUESTIONS

None.

## NEXT STEPS

1. **Re-run with a REALISTIC seed** -- frequent, concrete words rather than a random draw. *Section 6
   limit 5: the current number is the price of the worst seed, not the sensible one.*
2. **Check the shelved common-mode entry's revival criterion** against the anisotropy in section 4.
3. **Sweep `K`.** *Twice deferred now.*
4. *Method note: **the exactly-zero row would have read as a clean finding.** What caught it was the
   project's own rule that a zero-width null is a reachability failure, not a result.*
