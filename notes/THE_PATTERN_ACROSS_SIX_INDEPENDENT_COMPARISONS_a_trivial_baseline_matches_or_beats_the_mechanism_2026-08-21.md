# **SIX INDEPENDENT COMPARISONS, SIX SUBSYSTEMS, DIFFERENT AUTHORS AND MONTHS APART. IN NONE OF THEM DOES THE BUILT MECHANISM BEAT THE TRIVIAL BASELINE.**

**This was not looked for. It fell out of constraint-checking the standing claims one at a time, and
became visible only when the sixth was written next to the other five.** *`ORGAN_MAP`'s own phrase
applies again: the cells measured it and nobody set them beside each other.*

---

## 1. THE TABLE

| comparison | **TRIVIAL BASELINE** | **OURS** | outcome |
|---|---|---|---|
| rate-matched RANDOM gate vs prediction-error gate | 0.0971 / 0.1368 / 0.2165 / 0.3007 | 0.0961 / 0.1526 / 0.2268 / 0.3079 | **`NOT_SEPARATED` at all four thresholds** |
| second-order COUNTING vs the trained substrate | **+29.4 pp** | +16.3 pp | **counting wins; paired −0.142, CI [−0.203,−0.082] SEPARATED** |
| POPULARITY vs the grounded inductive encoder | **0.8148** | 0.5879 | **popularity wins by 0.2269** (shuffle control 0.4980, fired correctly) |
| pure SPELLING vs the meaning read-out, rank 1 | **0.0767** | 0.0480 | **spelling wins**, and survives the strictest tie convention |
| CA3 **OFF** vs CA3 **ON**, one-shot recall | 1.0000 | 1.0000 | **identical at every N — the memory contributes nothing** |
| WINDOW co-occurrence vs substrate, synonym rank | 38 / 30 / 31 | 46 / 35 / 42 | **ties**; paired gap 1 rank, CI spans zero |

**Six subsystems -- write-gating, meaning read-out, grounded link prediction, orthography, episodic
recall, distributional similarity. Different cells, different authors, months apart.**

## 2. WHY IT IS NOT ONE FINDING SIX TIMES

*The obvious objection is that these are all the same negative in different clothes.* **They are not:
they use different baselines (random, counting, popularity, spelling, ablation, window), different
tasks, different scorers and different populations, and three of them come with a control that FIRES
correctly** -- the shuffle at 0.4980, the scramble collapsing n11c's gain, the shuffled-label arm
collapsing to chance. ***The controls working is what makes the comparisons trustworthy rather than
uniformly broken.***

⚠️ **AND THEY MAY NOT BE COMBINED INTO A SINGLE NUMBER.** *Different scorers and populations --
discipline 11. The pattern is in the DIRECTION, which is unanimous; there is no pooled effect size
here and I am not computing one.*

## 3. 🎯 WHAT IT DOES AND DOES NOT LICENCE

**IT DOES SAY:** *every mechanism this project has scored against a trivial alternative has failed to
beat it.* **That is the honest summary of where the substrate stands, and it is stronger evidence
than any single one of the six.**

**IT DOES NOT SAY the approach is refuted.** *Three specific reasons, each already on record:*
1. **Four of the six were measured on the DISTRIBUTIONAL half.** *The binding/composition half is
   separately measured and separately weak, but for a NAMED and different reason -- role assignment
   from a sentence -- not for this one.*
2. **At least one comparison is now known to be un-improvable by better engineering:** our keys sit
   AT the Welch bound, so "better codes" is closed by geometry rather than by failure.
3. **The one thing that DID work is the same in every case: bring information in.** *12 human norm
   dimensions beat a 121M-token encoder; definitional extraction reads facts off the page at 90%
   precision; dense explanatory text lifts extraction where guessing-from-patterns does not.*

## 4. ⚡ **THE SHARPEST FORM OF IT**

> ***THE PROJECT'S MEASURED WINS ARE ALL ACTS OF SUPPLY. ITS MEASURED LOSSES ARE ALL ACTS OF
> INFERENCE.*** **Supplying human norms, lifting a stated fact off the page, feeding denser text --
> these win. Inferring meaning from co-occurrence, gating writes by surprise, completing a pattern,
> predicting a link -- these lose to something trivial, every time it has been checked.**

*That is a hypothesis-pending-VET about the shape of the whole programme, not a measured claim, and
it is labelled as one.*

## TLDR

I wasn't looking for this. It appeared while checking standing claims one at a time, and only became
visible when the sixth was set beside the other five.

**Six times, in six different parts of the system, built by different people months apart, we have
compared something we built against something embarrassingly simple. The simple thing has won or
tied every single time.**

Throwing away material **at random** works as well as choosing cleverly what to keep. **Plain word
counting** beats our trained system. **"Pick whichever thing is most popular"** beats our grounded
reasoning by a wide margin. **Spelling** beats our meaning read-out at the top rank. Switching a
memory component **off entirely** changes nothing.

**These aren't the same result six times.** Different comparisons, different tasks, different
measures — and in three of them the safety checks fired correctly, which is what makes them worth
believing rather than uniformly broken.

**What it doesn't mean:** the approach isn't disproved. Most of these test one half of the system.
One of them we now know can't be improved by better engineering, because that piece is already at the
mathematical limit.

**And there's a pattern in what does work.** Every measured win comes from **bringing information
in** — human ratings of what words feel like, facts lifted directly off the page, denser source
material. Every measured loss comes from **working it out from patterns**.

**Put plainly: we win when we supply, and lose when we infer.** That's a description of six results,
not a proven law — but it's the clearest shape the evidence has taken.

## QUESTIONS

None.

## NEXT STEPS

1. **Any new mechanism gets scored against the trivial baseline of its own task, not against random**
   -- popularity, counting, spelling, recency, whichever is the cheap one there.
2. **NORMS12's own note already does this correctly** and should be the template: it carries the
   popularity negative with it and narrows its own claim to "highest-value cheap move".
3. *This is 2 passes and 5 kills for the constraint check so far -- it discriminates.*
