# **THE WORD'S OWN TOKEN IDENTIFIES IT 97% OF THE TIME. ADDING THE SENTENCE AROUND IT DROPS THAT TO 64%. FOR IDENTIFICATION, CONTEXT IS NOT A WEAKER CUE -- IT IS NOISE.**

**VET of the measurement board Q102 rests on. The note under test states its own caveat -- *"0.4750
is inflated by self-reference"* -- and never quantifies it. This quantifies it.**

---

## 1. THE ARM THE ORIGINAL WAS MISSING

*The original compared two arms. The decisive third is the exact COMPLEMENT of the masked one:*

| arm | what it contains |
|---|---|
| **MASKED** | the context WITHOUT the target tokens -- *what the live path stores* |
| **UNMASKED** | the context WITH them |
| **TARGET_ONLY** ⬅️ **NEW** | **the target tokens and NOTHING else** -- the pure self-reference ceiling |

## 2. THE RESULT

*60 lemmas x 41 sentences, leave-one-out, same code path all three arms, chance 0.0167.*

| arm | hit@1 | within-lemma | cross-lemma |
|---|---|---|---|
| MASKED | **0.0972** | 0.0694 | 0.0310 |
| UNMASKED | **0.6423** | 0.2229 | 0.0207 |
| **TARGET_ONLY** | **0.9687** | **0.8059** | **0.0005** |

> ### **TARGET_ONLY IS 1.51x THE FULL UNMASKED ARM. The word alone beats the word PLUS its sentence, by a wide margin -- so the context is not helping identification, it is DILUTING it.**

**`within = 0.8059` against `cross = 0.0005` is the signature this project already named tonight: the
form channel scored `hit@1 = 1.0000` because THE QUERY WAS THE ANSWER.** *This is the same shape.*

## 3. 🎯 WHAT THIS DOES AND DOES NOT DO TO THE ORIGINAL FINDING

| the original claim | after this |
|---|---|
| *"identification needs the word PRESENT -- by far the strongest cue"* | ✅ **CONFIRMED, and UNDERSTATED. It is not the strongest cue, it is very nearly the ONLY one.** |
| *"one representation is doing two jobs"* | ✅ **STANDS, and sharpens: the identification job is a LOOKUP that needs no accumulated context at all.** |
| *"masked 0.1417 vs unmasked 0.4750 = 3.4x"* | ⚠️ **DO NOT QUOTE AS EVIDENCE ABOUT CONTEXT.** *The unmasked arm's advantage is self-reference; a purer self-reference arm scores HIGHER still.* |

**➡️ AND A TRAP WORTH NAMING: ANY "IDENTIFICATION" BENCHMARK THAT LEAVES THE WORD IN THE QUERY IS
MEASURING A LOOKUP AND CANNOT FAIL.** *That is the third instance tonight of the same defect --
the form channel's 1.0000, the exact-key ceiling, and now this.*

## 4. ⚠️ **THE REPRODUCTION CAVEAT, STATED FIRST-CLASS BECAUSE IT LIMITS EVERYTHING ABOVE**

***I DID NOT REPRODUCE THE ORIGINAL'S NUMBERS.*** *The producing script did not survive (`scratch/`
is transient), so I rebuilt the setup from its description:*

| | mine | the note | delta |
|---|---|---|---|
| MASKED | 0.0972 | 0.1417 | **-0.0445** |
| UNMASKED | 0.6423 | 0.4750 | **+0.1673** |

**So this is a DIFFERENT POPULATION -- a different corpus mix and a different lemma sample -- and by
this project's own rule NO NUMBER HERE CROSSES INTO A SENTENCE ABOUT THE NOTE'S POPULATION.**
*What travels is the ORDERING, and it travels because the gap is enormous rather than marginal:
TARGET_ONLY beats UNMASKED by **+0.3264**, which no plausible population difference closes.*

## TLDR

Everything tonight rests on one measurement: our system barely recognises that two sentences concern
the same word, and it recognises far better when you stop deleting that word. **I tested the part
that measurement left unchecked.**

**I ran a third version: the target word on its own, with the entire sentence thrown away.** It
identifies the word **97% of the time** — far better than the word *plus* its sentence, at 64%.

**So the sentence is not helping. It is getting in the way.** Recognising which word a sentence is
about, as we currently measure it, is essentially looking at the word — **a lookup, not
understanding.** It is the same problem I found earlier tonight with the spelling channel, where a
perfect score turned out to mean the question already contained its answer.

**This does not overturn the original finding — it sharpens it.** The claim was that recognising a
word needs the word present. **That is right, and stronger than stated:** the word is very nearly the
*only* thing that matters. Which means the job genuinely is a lookup, and it should be given to a
part built for lookups rather than to the part that learns meanings.

**The honest limit:** the script behind the original numbers wasn't kept, so I rebuilt the setup and
**did not land on its exact figures.** Mine is a different sample. **The ordering is what carries** —
and the gap is so large that no reasonable difference in sample would reverse it.

## QUESTIONS

None.

## NEXT STEPS

1. **Q102 is strengthened again.** *Identification really is a lookup, and a form channel is exactly
   a lookup — this is the right shape for it, and the masked context vector should not be asked to
   do the job at all.*
2. **Stop quoting `0.1417 vs 0.4750` as evidence about CONTEXT.** *It is evidence about
   self-reference. Quote it as "the word itself is the cue", never as "context with the word helps".*
3. *`tools/vet_two_jobs_selfreference_share.py` is the promoted script (a durable note cites it, so
   it is no longer scratch). It REFUSES rather than reporting if it cannot build the population.*
