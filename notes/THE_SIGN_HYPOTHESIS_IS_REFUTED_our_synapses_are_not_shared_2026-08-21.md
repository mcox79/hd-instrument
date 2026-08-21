# THE `sign()` HYPOTHESIS IS **REFUTED** -- AND THE REASON IS ARCHITECTURAL: **OUR "SYNAPSES" ARE NOT SHARED**

**The one-line sleep experiment ran. The hypothesis does not survive, and the drill predicted the
reason against itself a week ago.**

| t (content ingested) | GRADED query | `sign()` query | FROZEN |
|---|---|---|---|
| 1 | 8.8774 | 8.1871 | 8.8774 |
| 256 | 8.4108 | 7.7350 | 8.8774 |
| 4096 | 6.4218 | 5.7550 | 8.8774 |
| **log-log slope** | **-0.031** | **-0.033** | **0.000** |

*(A `t^-1/2` system reads **-0.50**.)*

---

## 1. ✅ THE FLOOR CONTROL PASSED FIRST, WHICH IS WHAT MAKES THE NULL READABLE

**FROZEN shows the BEST retention (perfectly flat, slope 0.000) and acquires 0 of 200 new words,
while the live arms acquire 200 of 200.** **The metric demonstrably CAN expose the
learn-less-forget-less cheat.** *That was the mandatory control the design brief added, and without
it a flat retention curve would be uninterpretable -- this project has twice been fooled by an arm
that scored well by knowing nothing.*

## 2. ❌ THE HYPOTHESIS IS NOT SUPPORTED

**`sign()` on the query is NOT what destroys our forgetting exponent.** The two arms are
**-0.031 vs -0.033** -- indistinguishable, and both are **~15x shallower than the `-0.50` a
Benna-Fusi system produces.** Removing the quantiser recovers nothing, because **there is barely any
decay to recover.**

**AND THIS IS A REAL NULL, NOT A DEAD INSTRUMENT.** SNR does fall (8.88 -> 6.42), the live arms
separate cleanly from FROZEN, and the frozen arm is exactly flat. **The instrument reaches; the
effect is genuinely almost absent.**

## 3. 🚨 **THE REASON, AND THE DRILL FLAGGED IT AGAINST ITSELF BEFORE I RAN ANYTHING**

> *"`+= ctx_vec` with a BOUNDED number of encounters per concept is not the same regime as the
> continuous random-uncorrelated stream Benna-Fusi analyse, and our 'time' axis (new concepts
> ingested) is not their 'time' axis (memories stored AT THIS SYNAPSE)."*

**That is exactly what happened, and it is architectural rather than incidental.**

**IN BENNA-FUSI, MANY MEMORIES WRITE TO THE SAME SYNAPSE** -- that shared slot is the entire source
of interference, and the cascade exists to protect against it. **IN OUR SUBSTRATE, EVERY LEMMA OWNS
ITS OWN ACCUMULATOR.** Streaming 4,096 new sentences mostly writes to *other* terms' slots. A
tracked trace decays only when *its own* term recurs.

**➡️ SO WE DO NOT HAVE THE PROBLEM BENNA-FUSI SOLVES.** *Not because we solved it -- because our
storage is not shared in the way that creates it.*

## 4. WHAT THIS DOES AND DOES NOT MEAN FOR THE SLEEP BUILD

**It does NOT kill D8+D4.** It relocates the question, which is more useful than a win would have
been:

- **A cascade synapse protects a SHARED slot from interference. Our slots are private, so the
  cascade's stated benefit does not apply as stated.** Building it to "fix forgetting" would be
  building a defence against a problem this architecture does not currently have.
- **The real cost of private slots is elsewhere and is not what I measured**: unbounded growth in
  the number of slots, and no mechanism for a slot to ever decay or be reclaimed. **That is much
  closer to what the owner actually asked for on Q92** -- *"an auto aging feature"* -- than
  interference protection is.
- **The honest next question is therefore NOT "does the cascade help our forgetting curve"** but
  **"what is our capacity failure mode, given private slots?"** -- and that has not been measured.

## 5. THE PROCESS POINT

**The cheap probe MEASURED and did not SET DIRECTION**, which is what the brief required of it. It
cost one script and it converted a plausible, attractive hypothesis -- *our exponent is destroyed by
one line* -- into a refuted one, **before** any of it reached a build.

*And the refutation came from a caveat the drill's own author wrote against their own analysis. That
is the caveat doing its job, for the second time today.*

## TLDR

I ran the cheap experiment. **The idea was that our system already does the mathematically clever
part of memory and then ruins it on one line by rounding everything to plus-or-minus one. That is
wrong.**

Removing the rounding changes essentially nothing: both versions forget at almost exactly the same,
very slow rate — about fifteen times slower than the brain-derived model predicts. There is barely
any forgetting to rescue.

**The reason is a genuine difference in how our system is built, and the original write-up warned
about it a week ago.** In the brain model, many memories are crammed into the same connection, and
they interfere; the whole mechanism exists to manage that. In our system **every word gets its own
private storage**, so pouring in thousands of new sentences mostly writes elsewhere and leaves an
old memory largely untouched.

**So we do not have the problem that mechanism solves — not because we solved it, but because our
design does not create it.**

That does not kill the sleep work; it moves it somewhere more useful. Our actual weakness is not
memories corrupting each other, it is that **we never throw anything away** — the number of private
slots only grows and nothing ever fades. Which is much closer to what you actually asked for.

Worth noting the check that made this readable: I included a deliberately useless version that stops
learning entirely. It showed perfect memory and learned nothing at all — proving the measurement can
catch that cheat, which is what lets the other two columns be trusted.

## QUESTIONS

None.

## NEXT STEPS

1. **Measure the actual capacity failure mode of private slots** -- growth in slot count, and
   whether anything ever decays. That is the question this refutation hands over.
2. The cascade is not withdrawn, but its stated benefit does not apply as stated to private slots,
   and any brief must say so.
