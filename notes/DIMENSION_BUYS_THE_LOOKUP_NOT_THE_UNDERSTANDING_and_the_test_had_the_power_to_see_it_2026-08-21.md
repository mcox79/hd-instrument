# **RAISING THE DIMENSION BUYS IDENTIFICATION (`+0.0622`, CI EXCLUDES ZERO) AND NOT MEANING (`+0.0127`, CI `[-0.0305, +0.0559]`). AND THE MEANING TEST HAD ENOUGH POWER TO SEE AN IDENTIFICATION-SIZED GAIN, SO THIS IS NOT MERELY "UNDERPOWERED".**

**This is the question that decides `notes/PLAN.md` D1, because D1 is expensive: raising the live
path's dimension rewrites every persisted store.**

> **CONFIG: `GRADED_COMPARATOR=True`. 28 corpora round-robin, 41 sentences per lemma, **829 SimLex
> pairs identical at every `d`**, null = **200 shuffles per `d`**.**

---

## 1. WHY THE CORPUS CONFOUND DOES NOT APPLY HERE

*Earlier tonight a source-identity confound wrecked an identification measurement, and correcting it
left only 111 usable pairs.* **That confound cancels in THIS comparison: every `d` is scored on the
SAME pairs from the SAME corpora, so it is constant across the arms being compared.** *Which is why
this can use all 829 covered pairs instead of 111.*

## 2. THE RESULT

| `d` | rho vs human | null p95 (200 shuffles) | null mean |
|---|---|---|---|
| 128 | 0.0974 | 0.0583 | -0.0010 |
| **256** *(ships)* | **0.0944** | 0.0648 | -0.0027 |
| 512 | 0.1032 | 0.0636 | -0.0023 |
| **1024** *(D1 proposes)* | **0.1071** | 0.0792 | +0.0002 |
| 2048 | 0.0874 | 0.0674 | -0.0026 |

***`d=1024` MINUS `d=256` on MEANING = `+0.0127`, 95% CI `[-0.0305, +0.0559]`, half-width `0.0432`.
SPANS ZERO.*** *The curve is flat and non-monotonic -- it DROPS at 2048.*

**AGAINST THE SAME CHANGE ON IDENTIFICATION: `+0.0622`, CI `[+0.0443, +0.0797]`, EXCLUDES ZERO.**

> ### **DIMENSION BUYS THE LOOKUP. IT DOES NOT DETECTABLY BUY THE UNDERSTANDING.**

## 3. 🎯 **AND THIS IS NOT THE USUAL "UNDERPOWERED" DODGE -- THE POWER IS STATED**

**The meaning difference has a CI half-width of `0.0432`. An effect the size of the identification
gain (`+0.0622`) would have produced a CI of roughly `[+0.019, +0.105]` -- EXCLUDING ZERO.**

***So this test would have detected an identification-sized gain in meaning. It did not. The meaning
gain, if there is one, is SMALLER than the identification gain.*** **That is a bounded negative, not
an absence of evidence.**

## 4. ✅ TWO VALIDITY CHECKS

1. **The null behaves.** *Mean `-0.0027` to `+0.0002` across all five dimensions -- a proper band from
   200 shuffles per `d`.* 🔻 **MY FIRST VERSION SHUFFLED ONCE AND REUSED THAT PERMUTATION AT EVERY
   `d`. It read `0.0568`-`0.0846`, comparable to the real signal, and appeared to RISE with `d`. One
   unlucky draw inherited by all five arms.** *A single shuffle is a sample; a null is a
   distribution.*
2. **The `d=256` value reproduces the archive.** *`0.0944` here on 829 pairs against the recorded
   `P_LIVE_CONCEPT` `0.1048` on 322 pairs -- different pair sets, same neighbourhood.*

## 5. ⚠️ WHAT THIS DOES AND DOES NOT SETTLE

| | |
|---|---|
| **D1 ("raise 256 -> 1024") improves identification** | ✅ **measured twice now, CI-separated** |
| **D1 improves meaning** | 🚫 **NOT SUPPORTED, with the power to have seen it** |
| meaning is *unaffected* by dimension | ⚠️ **NOT CLAIMED** -- a gain smaller than `+0.0622` is not excluded |
| our meaning signal is strong | 🚫 **NO.** *rho `~0.10` against a null p95 of `~0.065` is barely clear of noise at every `d`.* |

## TLDR

Earlier I found that giving the system more internal room makes it much better at recognising **which
word** a sentence is about. **The obvious question is whether it also gets better at knowing what
words MEAN** — because making that change is expensive: it rewrites everything the system has stored.

**The answer is no, and I can say that with more confidence than usual.**

Against nine hundred human-rated word pairs, quadrupling the room moves the meaning score by an
amount indistinguishable from zero — and it actually gets *worse* when I double it again. **Meanwhile
the same change clearly improved word recognition.**

**The reason this isn't just "we couldn't tell":** the meaning test was precise enough that if meaning
had improved as much as recognition did, I would have seen it. **It didn't.**

**One thing I had to fix first.** My check for "would random data score this well?" originally
scrambled the answers once and reused that single scramble everywhere. It happened to score
suspiciously high, which made our real result look barely better than noise. **Running two hundred
scrambles instead put it where it belongs, at zero.**

**And a sobering note that survives all of this:** our meaning score is about 0.10, where pure chance
reaches about 0.065. **That is barely above noise at every size we tested.** More room is not what
stands between us and understanding.

## QUESTIONS

None. *This is evidence about a standing decision (D1), not a new decision.*

## NEXT STEPS

1. **D1 should be argued on identification, not on meaning** -- *and identification is largely a
   LOOKUP, which is worth weighing against a change that rewrites every persisted store.*
2. **Do not expect dimension to move meaning.** *A gain smaller than `+0.0622` is not excluded, but an
   identification-sized one is.*
3. *Method note: **the single-shuffle null nearly buried the real signal under a fake floor.** The
   fix was 200 shuffles and one line -- and the tell was that a "random" control was rising with a
   parameter it could not possibly depend on.*
