
# READING MORE SOMETIMES LEAVES THE SYSTEM KNOWING LESS -- AND I DO NOT YET KNOW WHY

**2026-08-23, strategy session.** Drove the WRITE path end to end, the same way the read-out drive
found Q3's cost an hour earlier. **This is an observation with a live alternative explanation, not a
finding.** Recorded now so it is not lost, at the strength the evidence supports.

---

## 1. WHAT THE WRITE PATH DOES AT VOLUME -- THE HEALTHY PART FIRST

`substrate.py` records a defect it says was fixed: consolidation used to fire once per patch, so
grounding needed traces across passes and a single-patch read grounded nothing at any volume --
*"6,000 sentences of simplewiki: 0 grounded, 0 refused"*. **That fix holds on this path:**

| asked | read | grounded | refused | facts | episodes | secs |
|---|---|---|---|---|---|---|
| 200 | 200 | 30 | 26 | 152 | 1,457 | 3.1 |
| 400 | 400 | 30 | 91 | 152 | 2,749 | 5.4 |
| 800 | 800 | 49 | 345 | 190 | 5,766 | 11.9 |
| 1600 | **1,150** | 68 | 487 | 228 | 8,394 | 20.7 |

✅ **Grounding grows with volume, refusals grow with volume, and the gate accepts `68` of `555` =
`12.3%`** -- so it is discriminating rather than passing everything, which is what `substrate.py`'s
own self-test demands (*"the grounding gate refused nothing -- it cannot be discriminating"*).

*(The `1600 -> 1,150` row is the short-read guard firing, as designed.)*

---

## 2. THE ANOMALY, AND MY FIRST READING OF IT WAS WRONG

At 200 and 400 sentences, grounded was **identical at 30** and facts **identical at 152**, while
episodes nearly doubled. I called that a FROZEN store and a dissociation between the episodic and
semantic write paths.

**A finer sweep refuted that. It is not frozen -- it is NON-MONOTONE:**

| read | grounded | facts | facts/episode |
|---|---|---|---|
| 200 | **30** | **152** | 0.104 |
| 250 | 29 | 150 | 0.082 |
| 300 | 25 | 142 | 0.066 |
| 350 | 🔻 **24** | 🔻 **140** | 0.057 |
| 400 | 30 | 152 | 0.055 |
| 500 | 29 | 150 | 0.044 |
| 600 | 40 | 172 | 0.041 |
| 700 | 37 | 166 | 0.034 |
| 800 | 49 | 190 | 0.033 |

🔻 **READING 150 MORE SENTENCES (200 -> 350) COST `6` GROUNDED TERMS AND `12` FACTS.** The trend is
upward overall and dips repeatedly on the way. **The 200/400 identity I flagged was a coincidence of
a wobbling curve, not a freeze.**

⚠️ **AND THE SEMANTIC YIELD FALLS STEADILY: facts per episode `0.104 -> 0.033`, a 3x decline across
the range.** Episodes scale cleanly with input; facts do not.

---

## 3. THE ALTERNATIVE I HAVE NOT RULED OUT, WHICH IS WHY THIS IS NOT A FINDING

🚨 **EACH ROW IS A SEPARATE `Substrate` WITH ITS OWN FRESH READ. THE SAMPLES ARE NOT NESTED.** So the
dip at 350 is not necessarily knowledge being LOST -- it may be **consolidation-schedule phase**: a
run that stops at 350 may halt between checkpoints, with evidence banked but not yet consolidated,
while a run stopping at 400 lands just after one.

**Those need completely different repairs**, and nothing here separates them:

- **SCHEDULE PHASE** -> the numbers are snapshots at arbitrary points in a sawtooth; the fix is to
  measure at checkpoint boundaries, and there is no defect.
- **GENUINE LOSS** -> later reading is displacing earlier grounding; the fix is in the write rule,
  and it would matter a great deal.

**THE MEASUREMENT THAT SEPARATES THEM, AND IT IS CHEAP:** read ONE substrate incrementally, sampling
the store after every batch, so the samples ARE nested and a decrease is unambiguous. *I did not run
it and I am not going to imply which way it will come out.*

---

## 4. WHAT MAY AND MAY NOT BE QUOTED

- ✅ **MAY:** the write path grounds and refuses at volume, accept rate `12.3%` at 1,150 sentences;
  the once-per-patch defect does not reproduce on this path.
- ✅ **MAY:** the grounded/facts curve is non-monotone across independent runs at these volumes.
- 🚫 **MAY NOT:** *"reading more makes the system forget"*. **Not established** -- separate runs,
  schedule phase not excluded.
- 🚫 **MAY NOT:** the earlier claim that the store FREEZES while episodes grow. **I withdraw it**; the
  finer sweep refutes it.
- 🚫 **MAY NOT:** any of these as instrument numbers. One corpus, one seed, one 20-second read each.

---

## TLDR

I drove the writing side of the system the way I drove the reading side earlier.

The good news first: it works the way its notes claim. As it reads more, it learns more and it turns
away more of what it sees — accepting about one candidate in eight, which means it is being
selective rather than swallowing everything.

The odd part: the amount it knows does not climb smoothly. Reading 350 sentences left it knowing
slightly *less* than reading 200 did — six fewer concepts, twelve fewer facts. The overall trend is
up, but it wobbles downward on the way.

I do not know yet whether that is real forgetting or an artifact of when I happened to stop reading.
The system tidies up its knowledge periodically, so stopping just before a tidy-up versus just after
could explain the whole thing. **Those two possibilities need completely different fixes, so I am not
guessing between them.** The test that separates them is cheap and I have written down what it is.

I also had this wrong on first look — I reported the store as frozen, and a finer measurement showed
it wobbling instead. Different problem, and the coarse spacing of my first pass is what hid it.

## QUESTIONS

None. `Q115` and `Q116` remain open on the board.

## NEXT STEPS

1. **Run the nested version** -- one substrate, sampled after every batch -- which decides between
   schedule phase and genuine loss. Until then this is an observation.
2. **The 3x fall in facts-per-episode is unexplained** and may be the more important half: episodes
   scale with input and semantic yield does not.
3. If it turns out to be loss, it is a write-rule problem and belongs on the problems list; if it is
   schedule phase, the fix is to stop sampling the store at arbitrary points.

---

## 5. RESOLVED THE SAME HOUR: IT WAS SCHEDULE PHASE. THE WORRY IS DISCHARGED.

Ran the nested version named in §3 -- **ONE substrate, read in 150-sentence batches, store sampled
after each**, so every sample has read everything the previous one did plus more. A decrease there
cannot be explained by comparing separate runs.

| cumulative read | 150 | 300 | 450 | 600 | 750 | 900 | 1050 | 1200 | 1350 | 1500 | 1650 | 1800 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **grounded** | 0 | 23 | 30 | 35 | 41 | 47 | 61 | 71 | 82 | 95 | 105 | **111** |
| **facts** | 92 | 138 | 152 | 162 | 174 | 186 | 214 | 234 | 256 | 282 | 302 | **314** |

✅ **NO DECREASE AT ANY OF THE TWELVE NESTED SAMPLES. Monotone throughout, both columns.**

🔻 **SO "READING MORE MAY MAKE IT FORGET" IS DISCHARGED, AND THE DEFECT WAS IN HOW I SAMPLED.**
Comparing independent runs that stopped at different points sampled a consolidation sawtooth at
arbitrary phases. *The substrate was never the problem; my measurement design was.*

**AND A SECOND THING FALLS OUT, WORTH MORE THAN THE ANSWER:** the nested read reaches `111` grounded
and `314` facts by 1,800 sentences, where an independent single read of 1,150 reached only `68` and
`228`. **Reading in successive batches is markedly more productive per sentence than one long read**
-- which is exactly what the source predicts, since grounding needs `min_confirm` traces ACROSS
passes. *That also explains the falling facts-per-episode in §2: a single long read banks episodes it
never gets a second pass to confirm.*

⚠️ **STILL NOT QUOTED AS AN INSTRUMENT NUMBER.** One corpus, one seed, one run each.

---

## 6. WITHDRAWN THE SAME HOUR: THE BATCHING CLAIM IN SECTION 5 IS WRONG

**Section 5 says "reading in successive batches is markedly more productive per sentence than one
long read". THAT IS FALSE AND I AM WITHDRAWING IT.**

I reached it by putting `111` grounded after **1,800** batched sentences beside `68` after **1,150**
single-read sentences. **Raw totals at different volumes.** The batched arm simply read 650 more.

Per sentence, the same two numbers say the opposite of "markedly":

| | batched | single | ratio |
|---|---|---|---|
| grounded / sentence | `0.0617` | `0.0591` | `1.04x` |
| facts / sentence | `0.1744` | `0.1983` | 🔻 **`0.88x` -- favours the SINGLE read** |

**AND THE CONTROLLED TEST SETTLES IT.** Same corpus, same seed, same target volume, only the
batching changing:

| | read | grounded | facts | g/sentence | f/sentence |
|---|---|---|---|---|---|
| BATCHED (8 x 150) | 1,200 | 71 | 234 | `0.0592` | `0.1950` |
| SINGLE (one call) | 1,150 | 68 | 228 | `0.0591` | `0.1983` |
| **ratio** | | | | **`1.00x`** | **`0.98x`** |

🔻 **NO DIFFERENCE. Batching buys nothing.** The consequence I drew from it -- that a single long
read "banks episodes it never gets a second pass to confirm", explaining the falling
facts-per-episode -- **also goes.** That decline remains unexplained, which is where §2 left it.

⚠️ **AND THE PART WORTH KEEPING IS ABOUT ME, NOT THE SUBSTRATE.** I made this error in the very
commit where I noted that *"the second time today a wobble I found turned out to be in my instrument
rather than in the thing"*. **Comparing totals across populations of different size is the exact
error I had spent the night catching in other people's work and in my own.** Knowing the failure
mode by name did not stop me committing it twenty minutes later.

**THE CHEAP GUARD, AND IT IS NOT ANOTHER RULE: PRINT THE RATE BESIDE THE TOTAL, ALWAYS.** The probe
that refuted this printed `g/sentence` next to `grounded`, and the answer was visible in one line
without any analysis. My earlier probe printed both quantities too -- I just compared the column that
did not control for volume.

---

## 7. AND THE LAST OPEN THREAD CLOSES AS ARITHMETIC, NOT A DEFECT

§2 flagged facts-per-episode falling `0.104 -> 0.033` as unexplained, and §6 handed it back
unexplained after the batching account was withdrawn. **It is a type-token curve and it needed
asking-whether-it-is-surprising before it needed investigating.**

Fitting the twelve nested samples: **`facts = 8.4 x sentences^0.473`, mean absolute relative error
`6.0%`.**

**AN EXPONENT BELOW 1 MEANS NEW FACTS ARRIVE SUBLINEARLY WHILE EPISODES ARRIVE LINEARLY, SO
FACTS-PER-EPISODE MUST FALL.** No mechanism is required and none is broken. `0.473` -- facts growing
roughly as the SQUARE ROOT of sentences read -- sits squarely in the usual `0.4-0.6` band for
vocabulary growth in text, which is what you would expect if facts are keyed to distinct lemmas:
**the substrate is discovering facts at the rate text supplies new types.**

⚠️ **LIMITS, because a clean fit invites over-reading:** one corpus, one seed, twelve points, two
free parameters, fitted after the fact. **`6%` on twelve points is consistent with the curve, not a
test of it**, and I am not claiming Heaps' law is the mechanism -- only that the falling ratio needs
no explanation beyond sublinear type growth.

✅ **SO THE WHOLE WRITE-PATH INVESTIGATION CLOSES WITH NOTHING TO FILE:** the gate discriminates
(`12.3%` accept), the store never loses anything on nested sampling, batching buys nothing, and the
falling ratio is arithmetic. **Three apparent anomalies, three explanations, zero defects -- and two
of the three were my own measurement design.**
