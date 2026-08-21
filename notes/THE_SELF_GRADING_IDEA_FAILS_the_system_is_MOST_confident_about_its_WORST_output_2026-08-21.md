# **THE SELF-GRADING IDEA FAILS ON ITS FIRST REAL TEST -- AND THE SYSTEM IS MOST CONFIDENT ABOUT ITS WORST OUTPUT**

**The proposal, from my own Angle B design, presented as its highest-value consequence:** *"accumulated
error per term would be a self-generated estimate of how good that term's banked meaning is --
computed with no gold, no ConceptNet, no hand-scoring."*

**It is now testable, because I spent tonight persisting per-row hand verdicts beside the substrate's
own recorded confidence.** *That was the whole point of redoing the hand-score.*

**IT DOES NOT WORK.**

---

## 1. THE TEST: `best_cos` (the substrate's own confidence) vs THE HAND VERDICT, n=50

| verdict | n | mean `best_cos` |
|---|---|---|
| MEANINGFUL | 3 | 0.5008 |
| RELATED | 20 | 0.5010 |
| **NOISE** | **27** | **0.5325** |

| | |
|---|---|
| GOOD (MEANINGFUL + RELATED), n=23 | **0.5009** |
| NOISE, n=27 | **0.5325** |
| **separation** | **-0.0316 -- THE WRONG SIGN** |

**Ranking test:** sorting by confidence and taking the top 25 yields **10 non-noise rows against a
chance expectation of ~11.5.** *Sorting by the system's own confidence is slightly WORSE than not
sorting at all.*

## 2. 🚨 **THE TAIL IS THE STORY: THE FIVE MOST CONFIDENT ROWS, FOUR ARE NOISE**

| `best_cos` | pair | verdict |
|---|---|---|
| **0.7409** | `bolivian -> danny` | **NOISE** |
| **0.7160** | `backpack -> telescopic` | **NOISE** |
| **0.6721** | `dancer -> janeiro` | **NOISE** |
| 0.6254 | `coral -> reef` | RELATED |
| **0.5835** | `heroin -> mad` | **NOISE** |

**And at the other end, among the eight LEAST confident rows, five are RELATED** -- `solute ->
solvent`, `duke -> son`, `inversion -> karyotype`, `debit -> card`, `generate -> potential`. **Those
are among the most defensible pairs in the whole sample.**

## 3. WHY, MECHANISTICALLY -- AND IT IS NOT A BUG

`best_cos` is **cosine to the nearest EXISTING anchor.** A high value means ***"this resembles
something I already hold"*** -- **not "this is a correct meaning."** For a junk pair, high similarity
arises when the accumulated vectors are dense and noisy, which is exactly the regime that produces
junk in the first place. **The quantity is doing its job; its job is simply not quality.**

*This is the repo's own standing rule landing on my own proposal: **a statistic the mechanism
optimises is not an outcome.** `best_cos` is what the matcher maximises. Grading with it is measuring
the thing you selected on.*

## 4. WHAT IS AND IS NOT CLAIMED

**CLAIMED:** on this sample, **`best_cos` carries no usable positive signal about meaning quality**,
and the free-quality-estimate idea **in its `best_cos` form is dead.**

**NOT CLAIMED: that confidence is reliably INVERTED.** *n=50, only 3 MEANINGFUL rows, one relation
type, the distributional half only, and a separation of just -0.03. **The honest statement is "no
usable signal, with a hint of inversion in the tail" -- not "the signal runs backwards."*** Calling
it inverted would be the same overclaim I made six times tonight, in a more flattering direction.

**STILL OPEN:** the Angle B proposal was about **PREDICTION ERROR accumulated during reading**, which
is a different quantity from `best_cos` and **has never been computed** -- `predictive_coding` is not
on the live path. *This kills the cheap proxy, not the original idea.* **But it removes the "we can
test it immediately for free" argument, which was the proposal's main appeal.**

## TLDR

I proposed that the system could learn to **grade its own knowledge** — spotting which of its
definitions are rubbish without a human. Tonight I did the hand-grading needed to check that, and
**the check fails.**

The system records, for every meaning it stores, how confident it was. I compared that confidence
against my own judgement of whether the meaning was any good. **There is no useful relationship — and
the small relationship there is points the wrong way.**

**The clearest way to see it:** of the five meanings the system was *most* confident about, **four are
nonsense** — it was surest that "bolivian" means "danny" and that "backpack" means "telescopic".
Meanwhile several of its most defensible entries — *solute/solvent*, *debit/card* — sit at the very
bottom of its confidence ranking.

**The reason isn't a bug.** That confidence number measures *"does this look like something I already
have?"*, not *"is this right."* Junk pairs can look very familiar. The number is doing its job
faithfully; its job just isn't quality.

**I'm not claiming confidence is reliably backwards** — fifty examples, three good ones, and a small
gap. The honest version is **"no usable signal, with a hint of inversion"**. Claiming inversion would
be the same overreach I made repeatedly tonight, just in a direction that sounds cleverer.

**What survives:** the original idea was about a different measurement — how *surprised* the system is
while reading — which has never been built. **This kills the cheap shortcut, not the real proposal.
But the cheap shortcut was the reason the proposal looked attractive.**

## QUESTIONS

None.

## NEXT STEPS

1. **Withdraw "the error signal is a free quality estimate" in its `best_cos` form.** The real
   version needs prediction error, which does not exist on the live path.
2. **The inversion in the tail is worth one cheap re-check on a larger sample** -- if the most
   confident outputs really are the worst, that is a usable signal with the sign flipped, and it
   would be a genuinely useful thing to own.
3. The 100-row gold set makes both checks cheap from here on.
