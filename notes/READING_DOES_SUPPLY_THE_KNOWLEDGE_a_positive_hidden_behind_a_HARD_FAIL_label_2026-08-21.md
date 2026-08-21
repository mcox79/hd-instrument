# **"THIS REFUTES *READING CAN'T SUPPLY THE KNOWLEDGE*" -- A POSITIVE RESULT THAT SAT BEHIND A `HARD_FAIL` LABEL AND WAS INVISIBLE TO THE ARCHIVE UNTIL TONIGHT**

`exp_bootstrap_dense_process_article_reading_fade_v6`:

| field | value |
|---|---|
| `verdict` *(what every tool read until an hour ago)* | 🔴 **`HARD_FAIL_dense_explicit_no_better_than_scattered`** |
| **`final_verdict`** | ⬆️ **`MIDDLE_BAND_dense_reading_works_per_process_aggregate_capped_by_volume`** |

**Its own corrected message opens: *"MIDDLE_BAND (overstated conclusion CORRECTED)"*.** *Someone
already caught the over-claim. The field every query reads was never updated.*

---

## 1. PER-PROCESS, READING WORKS -- AND NOT MARGINALLY

| process | reading-only | (seed) |
|---|---|---|
| `igneous_rock_cycle` | **0.6923** | (0.8462) |
| `erosion` | **0.60** | |
| `electricity_generation` | **0.561** | (0.6585) |
| `digestion` | **0.50** | |
| `combustion` | **0.4516** | |

**Against a scramble floor of ~0.1879.** *2.4x to 3.7x the floor, and **approaching the seed** -- the
seed being what the system was handed rather than what it read.*

**➡️ THE CELL'S OWN WORDS: *"This REFUTES 'reading can't supply the knowledge'."***

## 2. WHY IT LOOKED LIKE A FAILURE -- **A VOLUME CONFOUND, AND THE CELL LOCATES IT PRECISELY**

**Aggregate `reading_only = 0.2121` vs the scattered v4 baseline `0.2788`.** *That comparison is what
produced the `HARD_FAIL` label.* **But:**

| cause | detail |
|---|---|
| **the dense corpus is SMALL** | **1,229 sentences -> 155 facts**, against v4's **~735 facts** |
| `hydrocarbon_formation` | **0.0** -- *entity mismatch*, 32 facts extracted |
| `fossilization` | **0 facts** -- *"descriptive not mechanistic article"* |

**Two of seven processes fail for NAMED, LOCATABLE reasons, and neither is "the mechanism doesn't
work".** *One is a vocabulary alignment problem; the other is that the article chosen doesn't
describe a mechanism at all.*

**➡️ `"CONCLUSION: the corpus WAS a confound -- dense explicit reading CAN learn process-conditioned"`
knowledge.**

## 3. WHY THIS MATTERS TO TONIGHT'S CENTRAL QUESTION

**Every measurement I surfaced tonight said the substrate sits at or below counting, and I ended by
asking *"why is the output at chance?"* This is the first artifact that answers part of it: on
DENSE, EXPLICIT, TOPIC-MATCHED material, reading recovers 0.45-0.69 per process against a 0.19
floor.**

*The failures cluster on **corpus fit and volume**, not on the reading mechanism.* **That is exactly
the standing rule -- *don't generalise a narrow failure to impossible* -- and here the artifact
proving it was filed under a label saying the opposite.**

## 4. ⚠️ WHAT IT IS NOT

**NOT a clean win.** *The aggregate genuinely is below the scattered baseline (0.2121 vs 0.2788), and
that is the honest headline number for the run as a whole.*
**NOT floored against counting.** *A scramble floor at 0.1879 is a real control, but it is not the
co-occurrence baseline that has beaten this project all night.*
**NOT 7 of 7.** *5 succeeded, 2 failed -- and "for locatable reasons" is a hypothesis about the
failures, not a demonstration that fixing them would work.*

## TLDR

An experiment recorded as a **failure** actually concluded, in its own words, that it **"refutes
'reading can't supply the knowledge'."** Nobody could see that, because the field our search tool
reads still said failure — until I fixed that an hour ago.

**What it found:** when the system reads *dense, explicit articles about a specific process*, it
learns that process genuinely well — scoring roughly **0.45 to 0.69** where scrambled text scores
**0.19**, and approaching the score it gets when simply *handed* the answers.

**Why it looked like a failure:** the overall average came out below a comparison run, **because the
dense corpus was small** — 155 facts learned versus about 735. And two of the seven topics failed for
reasons somebody already diagnosed: one had a vocabulary mismatch, and the other's article **describes
a thing rather than explaining how it works**, so there was no mechanism in it to learn.

**Why this matters:** all night the picture has been "the system's output is near guesswork and below
simple word-counting," and I ended by asking *why*. **This is the first piece of evidence pointing at
an answer: give it dense, on-topic, explanatory text and it learns properly. The failures were about
what it was fed, not about whether it can read.**

**Being fair to the failure label though:** the overall average really was worse than the comparison,
that number is real, and this hasn't been tested against the word-counting baseline that has beaten us
all evening. **Five of seven worked. That's promising, not proven.**

## QUESTIONS

None.

## NEXT STEPS

1. **This is the strongest existing evidence that the reading mechanism itself works** -- it belongs
   in front of any plan built on "the output is at chance".
2. **The volume confound is testable and cheap** -- the same dense approach on a corpus sized to match
   the scattered baseline would settle whether the aggregate gap is volume or quality.
3. **`fossilization` produced 0 facts from a descriptive article.** *That is a corpus-selection
   criterion nobody has written down: an article must describe a MECHANISM, not a thing.*
