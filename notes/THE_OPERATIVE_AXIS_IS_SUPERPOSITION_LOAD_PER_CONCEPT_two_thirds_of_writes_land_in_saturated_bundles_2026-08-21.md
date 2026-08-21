# **TWO-THIRDS OF ALL WRITING LANDS IN CONCEPT BUNDLES THAT ARE ALREADY PAST 1/3 RECOVERY. MEASURED ON THE ACTUAL STREAM, AGAINST A MEASURED CAPACITY CURVE.**

**Owner asked WHY writing less helps. The crosstalk law gave the family (interference). This gives
the operative axis, on our own data, with both quantities measured rather than assumed.**

---

## 1. TWO MEASUREMENTS, DELIBERATELY KEPT APART

**(a) WHAT OUR STORE CAN HOLD.** `hdlab/vsa_cleanup_memory.capacity_curve(d=256, M=1000,
n_probe=300, seed=3)` -- an existing, self-tested organ, not a new instrument:

| superposition load L | 1 | 4 | **8** | **16** | **32** | 64 | 128 |
|---|---|---|---|---|---|---|---|
| recovery | 1.0000 | 1.0000 | **0.9967** | **0.7867** | **0.3267** | 0.1267 | 0.0400 |

*Half-recovery at **L ~ 22**. Theory O(d/log d) gives 46.2 (ln) / 32.0 (log2), so the measurement sits
just below its own theory -- which is the expected direction, not a discrepancy.*

**(b) WHAT WE ACTUALLY WRITE.** `scratch/night/obs_stream_v1.npz`, the stream the write-gate cell
itself used (`lens` = traces per lemma, `lens.sum() == n_obs`):

**153,352 observations over 5,491 lemmas. MEAN 27.9 traces/lemma, MEDIAN 17, MAX 72.**

## 2. 🎯 **PUT THEM SIDE BY SIDE**

| threshold | recovery there | lemmas over it | **share of ALL WRITES landing in them** |
|---|---|---|---|
| **L = 8** | 0.9967 | 4,277 (77.9%) | **94.4%** |
| **L = 16** | 0.7867 | 2,760 (50.3%) | **82.3%** |
| **L = 32** | 0.3267 | 1,683 (30.7%) | **65.8%** |
| L = 64 | 0.1267 | 921 (16.8%) | 43.0% |

> ### **THE MEDIAN LEMMA CARRIES 17 TRACES, SITTING ALMOST EXACTLY ON THE 0.79-RECOVERY POINT. AND 65.8% OF EVERYTHING WE WRITE GOES INTO BUNDLES ALREADY BELOW ONE-THIRD RECOVERY.**
>
> ***That is why writing less helps, and it is not a subtle effect: most of the writing is going
> into containers that are already full.***

## 3. 🔻 **A CORRECTION TO MY OWN NUMBER FROM TWO STEPS AGO**

**I wrote "6.2 traces per lemma" and concluded we were comfortably inside capacity. That was
wrong.** *I divided the write-gate arm's `n_tokens_accepted` (33,907) by the stream's `n_lemmas`
(5,491) -- **two different populations**, since the arm ran on a subset of the 153,352-observation
stream.* **The stream's own `lens` array gives 27.9, and the median is 17.** ***Same fault I have
now made twice tonight: pairing a numerator and denominator that do not come from the same
population.*** *Caught by loading the array instead of dividing two summary fields.*

## 4a. ✅ **THE 72 CAP IS NOW TRACED, AND IT IS BY DESIGN -- WHICH BOUNDS EVERYTHING ABOVE**

**`K_SENT_TOTAL = 90` ("sentences kept per lemma") x `PROFILE_FRAC = 0.8` -> `_n_profile(k) =
min(k-1, int(k*0.8))` = `int(90*0.8)` = **72**.** *The other 18 are held out for evaluation --
`exp_grounding_readout_known_answer_v1:89-90,364-368`, reached via
`exp_surprise_weighted_update_v1:166`.* **A deliberate proportional profile/eval split, not a defect.
One grep, as promised, and no theory required.**

> ### 🔻 **AND IT SCOPES SECTION 2: THAT DISTRIBUTION IS THIS EXPERIMENT'S SAMPLING, NOT THE LIVE LOOP'S.**
> **The stream is capped at 90 sentences per lemma by construction, so `mean 27.9 / median 17 /
> max 72` describes the write-gate cell's population -- which IS the right population for the
> write-rate question, because that sweep ran on exactly this stream.** ***It does NOT transfer to
> the live reading loop, which caps by a completely different mechanism: a word STOPS accruing
> traces once it grounds*** (the standing example: `century`, **7 traces / 92 occurrences**).
> **Two different capping regimes. Do not quote either number for the other.**
> *If anything the live loop's frequent words would saturate WORSE without the 90-sentence ceiling --
> but that is a prediction, not a measurement, and it is not made here.*

## 4. ⚠️ AND AN UNEXPLAINED FINDING WORTH FLAGGING SEPARATELY

**`max = 72`, and `p90 = p99 = max = 72`.** *At least 10% of lemmas sit at EXACTLY 72 traces.* **That
is a CAP, not the tail of a natural distribution -- Zipfian word frequencies do not produce a
plateau.** *Something in the pipeline stops at 72.* **I have not traced where, and I am not guessing:
it is recorded as an observation, not a diagnosis.** *It bears on the standing "does the loop stop
taking notes?" question the owner raised, which was previously answered in terms of grounding, not a
hard count.*

## 5. HOW THIS RELATES TO THE CROSSTALK LAW -- SAME FAMILY, DIFFERENT AXIS

**Both are interference. They are NOT the same quantity and must not be merged:**

| | crosstalk law | this |
|---|---|---|
| stores what | key -> value in a Hebbian outer product | many items **summed into one vector** |
| capacity scale | `c x inv_e_sq` = `c x d` -> **257-1,297** at d=256 | **O(d/log d)** -> measured **~22** |
| varies | the ENCODER at native D | the LOAD at fixed geometry |

***The write-rate sweep adds traces into a SUPERPOSITION, so (b) is the operative axis for it, and it
is ~50x smaller than the Hebbian number.*** **Quoting the Hebbian 257-1,297 as headroom for the
write-rate question would have been badly wrong, and I nearly did.**

## TLDR

You asked why writing less helps. I now have the specific answer, measured on our own data.

**Two numbers, measured separately, then set side by side.**

**What one of our memory slots can actually hold:** about 8 things perfectly, 16 things at
roughly three-quarters accuracy, and by 32 it's down to a third. Half-accuracy lands around 22.

**What we actually put in them:** the typical word gets **17** entries — right at the
three-quarters-accuracy point. And **two-thirds of everything we write goes into slots that are
already past the one-third mark.**

**So writing less helps because most of the writing was going into containers that were already
full.** Not subtle — the dominant effect.

**A correction to my own figure from earlier:** I said the average was about 6 entries per word and
concluded we had plenty of room. That was wrong — I divided two numbers that came from different
sets. **The real average is 27.9 and the median is 17.** That's the second time tonight I've paired a
top and bottom of a fraction that didn't belong together, and both times what caught it was opening
the actual data instead of dividing two summary figures.

**One oddity I'm flagging without explaining:** the count stops dead at 72. More than one word in ten
sits at exactly 72 entries, which is a ceiling somewhere in the pipeline rather than anything natural
— real word frequencies don't pile up like that. **I haven't traced where it comes from and I'm not
going to guess.**

**And one trap avoided:** an earlier measurement suggested capacity in the hundreds-to-thousands. That
was a *different kind* of storage. Quoting it here would have suggested we had fifty times more room
than we do.

## QUESTIONS

None.

## NEXT STEPS

1. **This sharpens the approved sweep into a prediction with a number:** the gain should track the
   share of writes moved below L~16, and should stop once the median lemma sits under it.
2. **The 72 cap wants tracing** -- one grep of the write path, not a guess.
3. **Do not quote the Hebbian 257-1,297 for write-rate questions.** *Different store, ~50x apart.*
