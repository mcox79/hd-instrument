# WHAT 2026-08-21 ESTABLISHED -- THE FLAT LEDGER OF WHAT SURVIVES AND WHAT I WITHDREW

**Companion to `WHAT_2026-08-20_ESTABLISHED_...md`, same format, same purpose.** The plan, STATUS and
~15 notes carry the day in the order it happened, which is the right way to keep a record and the
wrong way to read one. **This is the flat version. Where this file and an older note disagree, this
file is later.**

> **THE WHOLE DAY IN FIVE LINES.**
> 1. **The measuring apparatus for the coherence monitor is built, replicated, and self-defending** --
>    items, hand-scores, harness, and a bar that no arm can be scored against without passing four
>    diagnostics first.
> 2. **The bar moved three times and every move was UPWARD, each from a defect in MY OWN
>    instrument** -- never from new evidence about the task.
> 3. **The substrate carries real signal (+16.3 pp) and is MEASURABLY BEHIND plain counting** -- the
>    first properly paired statement of a position the project has held informally for weeks.
> 4. **The "good half" of our stored meanings carries NO signal for the consumer I designed** --
>    the hand-score rubric pointed exactly the wrong way, and I had used it to decide, all session.
> 5. **Four failures moved out of prose and into code.** Every caution I wrote as prose this week was
>    later violated by me; every control written as code caught something.

---

## ✅ SURVIVES -- with evidence and with scope stated

### 1. The anomaly-detection apparatus, and it is self-defending
`data/anomaly_set_frequency_matched_v8.json` (120 frequency-matched items) + `_v8_handscores.json`
(**102 CLEAN / 17 WEAK / 1 BROKEN**, every item read by hand). Balance: log-frequency smd **-0.0134**,
length **-0.0289**, number agreement **120/120**, **120/120 distinct pairs**. Builder is
**byte-deterministic** (a rebuild reproduced the committed SHA-256 exactly).
**CEILING ~86%: with 17 WEAK items a perfect detector cannot score higher -- print it beside any score.**
`tools/f5_evaluation_harness.py` **RAISES instead of returning a number** when the error distribution
is quantised, the arg-max is positional, tie mass is degenerate, or the detector has never been shown
to fire. *Scope: one corpus, one task; anomaly detection is not comprehension.*

### 2. The three-way comparison, all `REPLICATED` on 4 independently-built sets
| arm -- paired anomalous-vs-original hit@1 | median |
|---|---|
| untrained codebook (nothing read) | **~0** -- CIs span zero; the geometry donates nothing |
| **the trained substrate** | **+16.3 pp** -- 4/4 CIs exclude zero |
| second-order counting -- **the bar** | **+29.4 pp**, upper bound **+44.2** |

**Learning bought something real** (0 -> +16.3; same representation, same comparison, only the
reading differs -- a clean attribution because the codebook was measured separately at zero).

### 3. We are measurably BEHIND counting, paired -- not merely not-ahead
`SUBSTRATE - COUNTING = -0.142 per item over 478 items, 95% CI [-0.203, -0.082]`, **SEPARATED**.
*Overlapping marginal CIs are not a test of a difference; this is. The project's standing position
can now be stated in its strong form for this task.*

### 3b. 🚨 THE SUBSTRATE'S SIGNAL IS **PARTIALLY SUBSUMED** -- union gain **1.28x** *(corrected: first written as flat SUBSUMED on a discriminator this project had already flagged as mis-specified; cortical read 1.1x = subsumed, substrate **1.28x** = partial, sensorimotor spoke union 2.15 median / 1.50 min over 9 seeds -- union SOLID, but its independence claim FAILED its own pre-registration (ratio 6/9))*
On 478 anomalous sentences: both arms hit **88** where independence predicts 62.3; **substrate-only
58 where independence predicts 83.7**. Substrate-unique rate minus independence = **`-0.0537`, CI
`[-0.0741, -0.0330]`, EXCLUDES ZERO.** *The arms agree far more than two independent arms would --
one signal read twice.* **This closes the room "+16.3 vs +29.4" left open**: "we get different items
so combining helps" is refuted, not merely unsupported. *The same analysis returned NOT SUBSUMED for
the sensorimotor spoke, so the test discriminates.* **It does not say we have no signal** -- +16.3 is
replicated and we score 0 before reading.

### 4. The "good half" of our meanings carries NO signal for a prediction-error consumer
On the 48 items where both routes fire, scored alone with no mixing:
**definitional `-0.021`/item, CI `[-0.062, +0.000]`**; **distributional `+0.188`, CI `[+0.042, +0.333]`**;
paired **`-0.208`, CI `[-0.375, -0.042]`, SEPARATED**. Definitions cover only **24.6%** of encountered
words. **Narrowly: this is NOT "the definitions are bad"** -- a correct definition need not share
vocabulary with an arbitrary sentence. They may suit a LOOKUP; not a prediction-error monitor.

### 5. The substrate is clean of the surface-vs-lemma bug class
Enumerated across `hdlab/`. One site would genuinely break; it survives only because `SEED_VOCAB`
holds **both** `called` and `call`. **A lucky property is one careless edit from a silent bug**, so it
is now `verification/test_seed_vocab_is_lemma_closed.py` with a positive AND a negative control.

### 6. `ORGAN_MAP` queues F5 behind step 4 and classes it Phase B
*"recorded so it is not started by accident."* **Board Q95.** And E3, the alternative, is a WORKING
organ -- but its margin over the STRONG floor is **not CI-separated at n=57** (**nine items**).

---

## 🚫 WITHDRAWN -- what I published and then killed

| claim | why it died |
|---|---|
| *"co-occurrence separates my hand-scored CLEAN from WEAK items"* | **+0.37, CI [-0.82, +1.56], p=0.316.** The number came from the LEAKED run and I carried the conclusion across after fixing the leak |
| *the bar is median rank 4.0* | **absolute rank is slot-inflated for EVERY arm** -- not a valid read-out |
| *the bar is +18.8 / +20.7 pp* | one set, then a surface-vs-lemma lookup bug deflating both floors |
| *"most of the floor's skill is a SLOT effect" (42.6%)* | **largely the lemma bug**; the original-sentence rate fell 42.6% -> 12.5% |
| *"bind only the definitional half -- the filter is one field that already exists"* | wrong twice: **coverage 24.6%**, and **no signal where it fires** |
| *"E3 beats both of its baselines"* | **n=57, no CI in the file**; the strong-floor margin is **nine items**, CI `[-0.016, +0.332]` |
| *"the hybrid's loss might be my z-score glue"* | tested and **exonerated** -- it is the definitions |

---

## 🎓 THE FOUR CONTROLS THAT MOVED FROM PROSE INTO CODE
`organ_map_cite.py` (constraints BEFORE the entry -- **I quoted F5's math row all session and never
read "queue behind step 4" in the same file; second time with that exact file**) ·
`verify_number_on_disk.py` (finds a number AND its n AND whether anything bounds it) ·
`f5_evaluation_harness.py` (refuses to score) · `test_seed_vocab_is_lemma_closed.py`.

**Every one exists because a rule written as prose failed.** *The self-tests found real defects in
three of the four while they were being written -- an off-by-boundary that a fixture landed exactly
on, a positive control whose probe lay outside the detector's world, and a ranking that surfaced
`n_total=349` instead of the `n=57` that governed the number.*

## TLDR

Today built the measuring equipment for the next component, and then used it to knock down three of
my own claims — including the one I had repeated most often.

**What stands:** the test set and scoring machine exist, are checked, and refuse to grade anything
that is broken. Our system, having read 7,500 sentences, genuinely detects something (it scores
zero before reading, so the reading is what bought it). And plain word-counting still beats us — now
measured properly, sentence by sentence, rather than inferred.

**What fell:** the number our component must beat moved three times, always upward, and **every move
came from finding a fault in my own equipment rather than learning anything new about the problem.**
And the "good half" of the system's stored word meanings — the half I have been championing all
session on the strength of hand-marking — turns out to detect **nothing at all** for the job I
designed it for, while the half I dismissed detects something real.

**The thread running through it:** a score you tuned toward can tell you where to look and must never
decide anything. I let it decide, repeatedly.

Four separate failures got moved out of written rules and into programs that enforce them, because
every rule I wrote as prose this week I later broke myself.

## QUESTIONS

**Q92** (recovery-note size limit) and **Q95** (build the coherence monitor, or the pronoun step
first) are open and are yours.

## NEXT STEPS

1. Board answers gate the next build.
2. The apparatus is reusable for any detector, not just F5.
