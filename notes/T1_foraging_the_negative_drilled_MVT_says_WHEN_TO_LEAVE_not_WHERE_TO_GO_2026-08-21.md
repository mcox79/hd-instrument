# T1 DRILLED -- **THE FLAGGED CONFOUND IS REFUTED, A DIFFERENT ONE IS REAL, AND UNDERNEATH BOTH IS A WORSE RESULT: THE ORGAN THAT EXISTS TO BREAK THE BIOLOGY SKEW READ ITS WAY TO 63.2% BIOLOGY**

**No new run. Everything here is a re-reading of `data/exp_information_foraging_reading_v1/metrics.json`
(`run_mode: full`, 5 arms x 10,000 sentences) and the cell source.**

---

## 0. 🚨 FIRST: TONIGHT'S TOP ITEM WAS SUPERSEDED, AND THE TOOL BUILT FOR THIS CAUGHT IT

I opened the overnight plan with **T1 = "BUILD H2, the organ is MISSING, brain math UNPINNED, floors
RANDOM and FROZEN."** `tools/organ_map_cite.py H2` returned, as its **first line**:

> **`L2168 - §6 STEP 1 (H2, "Independent. Start now") is superseded.`**

**Every clause of my T1 was wrong:**

| I wrote | the file says |
|---|---|
| organ **MISSING** | `hdlab/information_foraging.py` exists (38,533 b), witnessed, registry row `information_foraging_mvt_leave_rule` **WIRED** |
| brain math **UNPINNED** -- "function parity only" | **PINNED.** Charnov 1976 MVT (`g'(t) < ρ`); Constantino & Daw 2015 discrete form; Hayden 2011 (travel time raises threshold); Wittmann 2016 (two ρ timescales) |
| floors **RANDOM and FROZEN** must be run | **already run**, both of them, at 10,000 sentences per arm |

*This is the third time in two days that `ORGAN_MAP` has caught a decision I made by quoting one
part of it. **The tool CLAUDE.md added yesterday for exactly this failure worked on its first real
use.** The escalation from prose-caution to code-guard is now 3 for 3.*

## 1. THE MAP'S OWN FLAGGED CONFOUND -- **REFUTED**

The map says the FORAGE-vs-FROZEN comparison hinges on one unchecked thing, and that *"that single
check decides this"*:

> *"I do not know how the held-out probe range [1000,4000] was sampled -- **if the probes are drawn
> from the frozen corpora, the coverage metric favours FROZEN by construction.**"*

**They are not.** `load_base_vocab` (cell line 201) reads
`data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv` rows 1000-4000 -- **an external,
frequency-ordered vocabulary list, identical for every arm, drawn from no corpus in the experiment.**
Its backbone is **SUBTLEX-US** (Brysbaert & New 2009), 51M words of film/TV subtitles.
**➡️ Overlap-by-construction is NOT the explanation. That check is closed.**

## 2. ⚠️ BUT A DIFFERENT CONFOUND IS REAL, AND IT RUNS THE SAME DIRECTION

**The probe measures GENERAL CONVERSATIONAL ENGLISH. FROZEN reads general conversational English.**

| arm | what it actually read (top sources, from `sentences_read_by_corpus`) |
|---|---|
| **FROZEN** | `adv_new` 25% + `ele_cont` 25% + `int_cont` 25% -- **75% OneStop English graded NEWS** -- + `bio_new` 25% |
| **FORAGE** | `textbook_anatomy_physiology_2e` **25%**, `textbook_biology_2e` 11%, `textbook_concepts_biology` 8% -- **~45% biology/anatomy textbook** -- then `arc`, `ud_english_ewt`, `anne_of_green_gables` |

**FROZEN spends three quarters of its budget in the register the probe scores. FORAGE spends nearly
half its budget in the one register the probe barely touches.** So *"FROZEN 0.0743 beats FORAGE
0.0617"* is **not** clean evidence that gap-driven selection loses to a fixed schedule -- it
substantially measures **which arm read more everyday English.**
*Same directional bias as the confound the map flagged, arriving through a different door: not
corpus overlap, but **register match.***

**AND FORAGE IS NOT MERELY NOISE:** it is **4.87x RANDOM** (0.0617 vs 0.0127). The ordering
**FROZEN > FORAGE >> RANDOM** is what register-match predicts.

## 3. 🔴 **THE RESULT THAT SURVIVES BOTH CONFOUNDS, AND IT IS WORSE THAN THE ONE THEY EXPLAIN AWAY**

**`dominant_domain` = `textbook_biology`, share `0.63245`.**

**The organ exists to break a 64.5% biology skew. It produced a 63.2% biology skew.** *It did not
fail to move the system; it moved the system back to where it started, from a free choice over 36
corpora, having visited 19 of them.*

**And it did that while WINNING on its own currency:**

| | FORAGE | FROZEN |
|---|---|---|
| achieved gain rate | **6.96** | 5.90 |
| mean gain / sentence | **7.56** | 5.92 |
| patches visited / distinct | **107 / 19** | 4 / 4 |
| oracle ratio | **0.534** (band 0.70-1.00: **FAIL**) | 0.290 |
| **learning progress (1st half − 2nd)** | **−0.002 (FLAT)** | **+0.024** |

**The pinned machinery works.** ρ tracks, the leave rule fires 107 times, travel updates happen, and
FORAGE harvests **18% more information per unit time** than the incumbent. **Nothing is broken.**

## 4. 🧠 **THE BRAIN-FOUNDATIONAL DIAGNOSIS: MVT TELLS YOU WHEN TO *LEAVE*, NEVER WHERE TO *GO*.**

Charnov's theorem is a **stopping rule**: leave the current patch when its marginal return drops
below the environment's average. **It is silent on which patch you travel to next.** In a foraging
animal that silence is filled by the world -- the next patch is simply the nearest one.

**We have no nearest patch. We have 36 corpora and a free choice, and the thing that fills the
silence is our patch-CHOICE function -- which `ORGAN_MAP` marks UNPINNED, and which the module
itself declares a fallback.**

**➡️ SO THE FAILURE LOCALISES CLEANLY TO THE UNPINNED HALF OF A HALF-PINNED ORGAN.** A
biology-primed model gets its highest per-sentence information gain from **adjacent** biology text,
so a chooser maximising gain-per-sentence walks straight back into anatomy and physiology. **The
organ optimised exactly what it was told to optimise. BREADTH WAS NEVER IN THE CURRENCY.**

*And the flat learning-progress number (−0.002 vs FROZEN's +0.024) is the tell that this is a real
defect rather than a scoring artifact: **it kept harvesting at a high rate while learning nothing new
over time** -- which is what mining an adjacent seam looks like from the inside.*

**This is a MISSING-PRIMITIVE error, not a used-ability-wrong error** -- route (2) on the standing
error-flavour rule. **The primitive is a travel/patch-choice function.** *A cost-of-travel term is
the brain-side candidate (Hayden 2011 already pins that longer travel RAISES the leave threshold, so
travel cost is in the pinned half) -- but "which patch" needs its own answer, and the honest label is
OUR-INVENTION-UNDER-TEST until one is found.*

## 5. WHAT MUST **NOT** BE CONCLUDED FROM THIS

- **NOT "foraging does not work."** It fires, it beats RANDOM ~5x, it beats the incumbent on
  information-gain rate. *Standing rule: a fair test of a weak implementation proves THAT setup
  failed, not that the capability is impossible.*
- **NOT "FROZEN is better."** Its apparent win is register-matched to the probe.
- **NOT a re-scoring verdict yet.** The clean re-score is stated below; **I have not run it.**

## TLDR

Tonight's plan opened with "build the part that decides what to read next — it doesn't exist." **It
does exist.** A tool we added yesterday for exactly this mistake told me so in its first line, and
also told me the experiment had already been run.

The recorded result was that this organ **lost** to the old fixed reading schedule. I dug into why,
and found the comparison was unfair in a way nobody had noticed: **the test measures how many
ordinary everyday words the system picks up, and the old schedule spends three quarters of its time
reading ordinary news articles.** The challenger spent nearly half its time in biology and anatomy
textbooks. So the old schedule was being tested on its home turf.

**But fixing that comparison uncovered something worse.** This organ's entire reason for existing is
that the system's knowledge was 64% biology and it needed to go read something else. Given a free
choice of 36 different sources, **it read its way to 63% biology.** It went right back where it
started.

And it did that while *succeeding* by its own measure — it gathered 18% more information per minute
than the old schedule. Nothing is broken. **The problem is what we asked it to want.**

Here is the reason, and it is a real gap rather than a bug. The brain science we copied answers the
question *"when should I give up on this patch and move on?"* — and it is genuinely silent on *"where
should I go next?"* For an animal that silence doesn't matter: the next patch is whichever one is
nearby. **We have no "nearby" — we have 36 sources and a free choice**, and the piece that makes
that choice is the part nobody has a brain equation for. A system already full of biology learns the
most per sentence from *more* biology, so it kept mining the same seam. **Breadth was never part of
what it was told to want.**

The giveaway: it kept collecting information fast while its actual learning went flat.

## QUESTIONS

None.

## NEXT STEPS

1. **THE CLEAN RE-SCORE (no new run, and it is the decisive one):** score held-out coverage on a
   probe set that is **not** register-matched to either arm -- e.g. per-domain coverage, or a probe
   drawn from the union vocabulary of all 36 corpora. **Until that exists, neither arm's coverage
   number should be quoted as an organ verdict.**
2. **The real build target is the PATCH-CHOICE function**, not the leave rule. Brain-side candidate
   to drill first: travel cost (Hayden 2011 is already pinned and already in the module).
3. **The live-path call site is still owed** -- `IS-REACHED: no`. The loop still reads the 4-entry
   dict at `exp_reading_grounding_loop_cycle2_v1.py:132-137`. *That is a wiring, not a build.*
