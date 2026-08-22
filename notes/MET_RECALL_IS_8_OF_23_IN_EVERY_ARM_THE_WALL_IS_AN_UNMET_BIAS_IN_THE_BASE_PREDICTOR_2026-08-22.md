# **THE WALL IS NOT CREDIT ASSIGNMENT AND NOT THE LEARNED LEXICON. `MET` RECALL IS `8/23`, `7/23`, `8/23` -- ESSENTIALLY INVARIANT ACROSS EVERY ARM INCLUDING NO-LEARNING-AT-ALL.**

**And my first explanation of this was wrong, refuted by the direct test twenty minutes after I formed
it. That is in section 2, not buried at the bottom.**

---

## 1. WHAT I FOUND FIRST -- A SPECTACULAR-LOOKING SKEW

Persisting the per-verb canary detail (it was being filtered down to four summary numbers) showed
**every single light verb locked NEG**, at margins far above the `0.34` neutral band:

| verb | POS | NEG | total | margin |
|---|---|---|---|---|
| `be` | 31 | **259** | 290 | 0.786 |
| `have` | 17 | **140** | 157 | 0.783 |
| `say` | 12 | **97** | 109 | 0.780 |
| `see` | 0 | **20** | 20 | 1.000 |

**And it is global, not a light-verb quirk:** `soft_combine_registered` is **120 NEG / 5 POS = 96.0%
NEG** across 125 words, while the eval gold is **23 MET / 13 UNMET**.

> ### **THE OBVIOUS STORY: the system learns "everything is bad", the eval is 64% good, so it scores below the majority floor. It is tidy, it is mechanistic, and it fits every number on the page.**

*The pre-registered gate agrees something is wrong here: `HP3` demands a light-verb neutral rate
`>= 0.70` and `HF_lightverb` HARD-FAILS below `0.30`. **We read `0.0`** -- a gate failing at its extreme.*

## 2. 🔻 **AND IT IS WRONG. I SCORED THE MAPS DIRECTLY INSTEAD OF ASSERTING IT.**

| overlay | accuracy | **MET recall** | UNMET recall |
|---|---|---|---|
| **EMPTY** -- no learning at all | `0.3889` | **8/23** | 6/13 |
| **AND-gate** -- 18 words, **50/50 BALANCED** | 🔻 **`0.3056`** *(WORST)* | **7/23** | 4/13 |
| **SOFT-COMBINE** -- 125 words, **96% NEG** | ✅ **`0.4722`** *(BEST)* | **8/23** | 9/13 |

> # **THE SKEWED MAP IS THE BEST ARM. THE BALANCED MAP IS WORSE THAN NO LEARNING. THE NEG COLLAPSE IS NOT WHAT IS HURTING US.**

*Had I written up section 1 and moved on -- which I was one step from doing -- I would have filed a
confident mechanistic explanation of the wall that the cheapest possible test refutes.*

## 3. 🔑 **WHAT THE SAME TABLE ACTUALLY SHOWS, READING THE COLUMN I WAS NOT LOOKING AT**

**`MET` recall is `8/23`, `7/23`, `8/23`.** *Across a 7x change in lexicon size, across a 96%-vs-50%
polarity split, across learning-versus-no-learning at all.* **Every point of movement in this cell,
in either direction, is in the UNMET column.**

- **The eval is 64% MET. The system predicts `UNMET` 21 times and `MET` 10 times out of 36.**
- **The majority floor IS "always say MET" = `23/36` = `0.6389`.** *We cannot clear a floor built out
  of the one answer we systematically fail to give.*

> ## ➡️ **THE DEFICIT IS AN `UNMET` BIAS IN THE BASE PREDICTOR (`congruence_with_lexicon_fallback`), UPSTREAM OF THE TEACHER, THE CREDIT SCAN AND THE LEARNED LEXICON ALIKE. NONE OF THE THREE THINGS I HAVE SPENT THIS SESSION ON CAN REACH IT.**

## 4. WHAT THIS RETIRES, AND WHAT IT DOES NOT

| | |
|---|---|
| 🔻 **credit assignment as the bottleneck** | *the role logic was already right (Q104, withdrawn); the verb-gate fix changed 12 of 36 decisions and the paired test refused the gain (`p=0.1460`)* |
| 🔻 **the light-verb wash-out as a defect worth fixing** | *the gate fires, but the skew it detects is not what costs accuracy -- the balanced map scores WORSE* |
| ✅ **still open, and now the only live lead** | **why the base predictor says UNMET for a corpus and an eval that are majority MET** |

## 5. ⚠️ LIMITS

1. **n=36, and `8/23` vs `7/23` is one item.** The INVARIANCE is the finding, not the exact value;
   at this n I cannot resolve small real differences between arms. **Underpowered is not negative.**
2. **Three overlays, one eval bank, one corpus.** The MET-bias claim is about THIS predictor on THIS
   bank.
3. **I have NOT yet looked at why the base predictor is UNMET-biased.** *Naming a component is not
   diagnosing it, and the last two times I named one I was wrong about what it did.*
4. **`light_verb_detail` and `noise_detail` now ship** (the aggregate was discarding them); the landed
   run is unchanged at `0.4722`, so both additions are purely additive.

## TLDR

The system is supposed to learn whether an action turned out well or badly by reading stories. It
scores worse than a strategy of just answering "well" every single time.

**I thought I had found why.** The learned vocabulary is overwhelmingly negative — 96 out of every 100
words it learns get filed as "bad outcome", including *be, have, say, see*. The stories it reads are
not that negative, so it looked like the system had simply learned to call everything bad.

**Then I tested it instead of believing it, and it turned out backwards.** I compared the lopsided
negative vocabulary against a small perfectly-balanced one, and against no learned vocabulary at all.
**The lopsided one is the best of the three. The balanced one is worse than knowing nothing.** So the
negativity isn't what's hurting us.

**Looking at the column I'd been ignoring gave the real answer.** Out of 23 questions where the true
answer is "it turned out well", the system gets 7 or 8 right — **and that number barely moves no matter
what it has learned, or whether it has learned anything at all.** All the movement is in the "turned out
badly" questions.

**So the problem is not what it learns. It is that the underlying judgement it starts from almost never
says "this went well"** — and since the easy baseline is "always say it went well", we can't beat a
baseline made of the one answer we can't produce. **That is upstream of all three things I worked on
today**, which is worth knowing before spending another day on any of them.

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Diagnose the MET side of `congruence_with_lexicon_fallback` directly** -- on what fraction of
   MET-gold items does it return `UNMET` versus `AMBIGUOUS`/`NONE`, and is the bias in the structural
   congruence call or in the lexicon fallback? *Diagnose before touching it: I have now been wrong
   twice this session by naming a component from its symptom.*
2. **Everything on this line is still being decided by 36 items.** *The invariance above is visible at
   n=36; a fix will not be.*
3. *Method note: **the finding was in a column of a table I had already printed twice.** I was reading
   the accuracy row and the polarity split, and `met_recall` sat beside them the whole time.*
