# T1 -- **THE REGISTER CONFOUND IS NOW QUANTIFIED: A 7.6x BIAS SITS UNDER A 1.2x EFFECT. THE COMPARISON IS NOT INTERPRETABLE.**

**No new run.** Every number here comes from `banked_by_source` in
`data/exp_information_foraging_reading_v1/metrics.json`, which survived even though the banked term
lists did not.

---

## 1. WHAT EACH ARM ACTUALLY *BANKED*, BY REGISTER

*Previous notes measured what each arm READ. This measures what it LEARNED FROM, which is the
quantity the probe scores.*

| arm | banked | **news / conversational** | **textbook** | other |
|---|---|---|---|---|
| **FROZEN** | 696 | **88.2%** | 11.8% | 0.0% |
| **FORAGE** | 604 | **11.6%** | **70.9%** | 17.5% |
| RANDOM | 157 | 36.9% | 22.9% | 40.1% |

FROZEN's top sources are `adv_new` (282), `int_cont` (255), `ele_cont` (77) -- **OneStop English
graded news.** FORAGE's are `textbook_concepts_biology` (149), `textbook_biology_2e` (116),
`textbook_anatomy_physiology_2e` (102).

## 2. 🚨 **THE ARITHMETIC THAT SETTLES IT**

**The probe is `base_vocabulary_ordered.csv` ranks 1001-4000, whose backbone is SUBTLEX-US
(Brysbaert & New 2009) -- 51 million words of film and TV subtitles. It is a CONVERSATIONAL-ENGLISH
instrument.**

| | |
|---|---|
| FROZEN's register alignment with the probe | **88.2%** |
| FORAGE's register alignment with the probe | **11.6%** |
| **ratio -- the size of the bias** | **7.6x, favouring FROZEN** |
| FROZEN's actual margin on the outcome | **1.20x** (0.0743 vs 0.0617) |

**➡️ A 7.6x MEASUREMENT BIAS SITS UNDERNEATH A 1.2x RESULT. THE COMPARISON CANNOT SUPPORT ANY CLAIM
ABOUT SELECTION QUALITY IN EITHER DIRECTION.**

**AND THE HONEST DISCIPLINE HERE IS TO STOP THERE.** It is tempting to say *"normalised for register
FORAGE is clearly better -- it reaches 83% of FROZEN's coverage while banking 71% of its terms from a
register the probe barely samples."* **That is the SAME OVERCLAIM I made four hours ago, run in
reverse.** The register-adjusted number **cannot be computed**, for the reason in §3. *A confound
large enough to destroy a claim is not thereby evidence for its opposite.*

## 3. 🔴 **AND THE ADJUSTED NUMBER CANNOT BE COMPUTED -- THE EXPERIMENT IS NOT RE-SCORABLE**

Tonight's plan listed as its top remaining item: *"a clean re-score on a probe **not**
register-matched to either arm -- **no new run**."* **That is not possible. Verified on disk:**

- `metrics.json` per-arm fields: **zero list-valued fields.** Counts only -- `heldout_hits`,
  `n_grounded`, `banked_by_source`.
- `units.jsonl`: **5 units, no list-valued fields in any result.**
- `run_stdout.log`: **9,482 bytes**, one matching line.

**THE BANKED TERMS EXIST NOWHERE. The cell persisted its SCORES but not its OUTPUTS.**

**➡️ THE GENERAL DEFECT, AND IT IS WORTH MORE THAN THIS EXPERIMENT: AN EXPERIMENT THAT SAVES ONLY
ITS SCORES CAN ONLY EVER ANSWER THE QUESTION IT WAS ORIGINALLY ASKED.** When that question turns out
to be confounded -- which is normal, not exceptional -- **every re-analysis costs a full re-run.**
Here: 4,144 seconds across 5 arms, to answer a question the existing run already contains the data
for and threw away.

**CHEAP STANDING FIX for any cell that scores a vocabulary against a probe: dump the banked term
list per arm.** *604 strings is a few kilobytes. It converts an unanswerable question into a
one-second re-score, and it is the difference between an experiment and a verdict.*

## 4. WHERE T1 ACTUALLY STANDS NOW

| claim | status |
|---|---|
| the organ is BUILT and landed HARD_PASS, not MISSING | ✅ **STANDS** |
| its math is **PINNED** (Charnov 1976 MVT et al.) | ✅ **STANDS** -- *I filed it as unpinned; that was wrong* |
| each gate was scored against whichever baseline it could beat | ✅ **STANDS** -- the cell recorded the losing number itself |
| **FORAGE has the best hit rate of any arm (27.0%), losing on attempt VOLUME** | ✅ **STANDS** -- register-independent |
| **"the trivial baseline beats it on every learning outcome"** | ❌ **WITHDRAWN -- confounded 7.6x** |
| **MVT says WHEN TO LEAVE, not WHERE TO GO; patch-choice is the UNPINNED half** | ✅ **the real finding** |
| single seed throughout | ⚠️ `SINGLE_SEED_HYPOTHESIS` |

## TLDR

Earlier tonight I reported that the clever "choose what to read" system lost to just reading the same
four documents forever. **I am withdrawing that.**

The vocabulary test used to compare them is built from film and TV subtitles — everyday spoken
English. I checked what each version actually *learned its words from*: **the winner learned 88% of
its words from news-style writing; the clever one learned 71% from biology textbooks.**

So the winner was tested in its own dialect, by a margin of about **seven and a half to one** — and
it only won by about **one and a fifth to one**. **A bias that big underneath a result that small
means the comparison tells you nothing about which method is better.**

**I am deliberately not flipping it the other way.** The tempting move is to say the clever one is
therefore secretly winning. That's the identical mistake I made four hours ago, just pointed the
opposite direction, and I can't compute the fair number anyway — **because the experiment threw away
the words it learned and kept only the score.** Re-checking it against a fairer test would mean
re-running the whole thing, about an hour of compute, for data the original run already had in memory.

**That last part is the lesson worth keeping:** save what an experiment *produced*, not just how it
*scored*. A few kilobytes of words would have turned tonight's dead end into a one-second
recalculation.

What does survive: the selector has the **best success rate of anything tested**, and the published
rule it's built on governs **when to stop reading something**, not **what to pick up next** — and
what to pick up next is exactly the job we need.

## QUESTIONS

None.

## NEXT STEPS

1. **The patch-choice primitive is the real build target** -- the unpinned half of a half-pinned organ.
2. Any re-scoring needs a re-run; **add a per-arm banked-term dump first** so it never needs a third.
3. Seeds before any claim in either direction.
