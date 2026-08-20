# THE BRANCH THE OWNER ENDORSED, AUDITED BY THE SAME STANDARD I APPLIED ALL NIGHT TO THE OTHER ONE

**2026-08-20.** I spent the whole session stress-testing the reading-pipeline branch of Q89 --
scoring it, replicating it, retracting two of my own findings about it. **The perceptual/supplied-
norms branch, which is the one I RECOMMENDED and the owner has now endorsed, got none of that
scrutiny.** That asymmetry is the thing to fix before anything is built there.

## THE POSITIVE EVIDENCE, STATED AS IT IS RECORDED

The claim carrying the branch: **the 11 Lancaster sensorimotor dimensions "double the text-only
ceiling" on a well-posed problem, and supplied norms beat the learned substrate on 3 seeds.**

**The record's OWN caveat, written by whoever landed it, in the same paragraph:**

> *"**WHAT IT IS NOT: a mechanism.** It says the INFORMATION is there and text does not have it. The
> norms are SUPPLIED human ratings -- admissible (static, offline, no LLM at inference) but not
> learned. **One gold, one corpus, 538 words, no CI. NEXT BUILD, not next claim.**"*

**`tools/replication_gate.py` verdict: `SINGLE_SEED_HYPOTHESIS`.** One gold, one corpus, no CI.
**By the standard I enforced on myself four times tonight, the headline result of the endorsed
branch is a HYPOTHESIS, not a finding.** *That is not a reason to abandon it -- it is a reason to
replicate it FIRST, which is exactly what I demanded of my own phrase result before quoting it.*

## THE NEGATIVE EVIDENCE, AND IT IS THE BETTER-CONTROLLED OF THE TWO

`exp_sensorimotor_channel_discrimination_v1` (2026-08-18):

| | |
|---|---|
| best arm `SM11_Z_NEG_EUCLID` | **AUC 0.6039**, CI [0.5439, 0.6644] |
| credible bar | **0.6791**, from `F_CONSTANT_PROTOTYPE__SM11` (floor AUC 0.6195) |
| margin | **-0.0752** (and -0.0156 against the floor's POINT value) |
| instrument licensed? | **YES** -- known-answer AUC **0.9448** [0.9204, 0.9654] |
| above the nulls? | **YES** -- paired-swap p=**0.0011**, label-shuffle p95 0.552 |
| coverage | 166/242 units survive; **76 removed by the norms filter**; word coverage 90.3% |

**THIS IS A WELL-BUILT TEST.** The floor is computed **on the same 11-dimensional representation**,
the instrument is separately shown able to detect a real effect, and the nulls are run.

**AND THE PRECISE READING MATTERS: the dims carry SIGNAL but not DISCRIMINATION.** They beat the
shuffled nulls decisively (p=0.0011) -- **so the information is real** -- and yet fail to beat
*"predict the prototype for everything"*. **A query-INDEPENDENT genericity score reading 0.6195 beat
every pairwise distance measure tried.**

**➡️ THAT IS THE SAME FAILURE SHAPE AS THE TEXT SIDE, IN A DIFFERENT CHANNEL: real signal, no
discriminative power over a trivial constant.** *The text read-out loses to co-occurrence counting;
the perceptual read-out loses to a constant prototype. Both clear their nulls. Neither clears a
floor.*

## ⚖️ SO THE HONEST STATE OF THE ENDORSED BRANCH

- **It is NOT refuted.** The 2026-08-18 failure is one instrument on one resolution, and the
  standing rule -- *do not generalise a narrow implementation failure to impossible* (owner,
  08-11) -- explicitly paid out here once already: the same 11 dimensions later did better on a
  better-posed problem.
- **It is NOT established either.** Its positive result is single-run, no CI, 538 words, and its
  own author wrote *"NEXT BUILD, not next claim"*.
- **And its one well-controlled test failed a floor of exactly the kind that has defeated every
  text-side arm this project has built.**

**THE PATTERN WORTH SEEING: supplying perceptual norms did not escape the failure mode -- it
reproduced it in a new channel.** That is a real caution for a branch chosen partly because
"three of the four things that work are bring-in-signal".

## 🔑 WHY I AM WRITING THIS RATHER THAN GETTING ON WITH THE BUILD

**I recommended this branch. It is now endorsed. That makes it exactly the claim I am least likely
to audit and most likely to be wrong about** -- and tonight produced four retractions, every one of
them a result I wanted to be true.

*The definitional branch got: blind scoring, a second corpus, a population count that corrected my
own estimate downward, an exhaustive false-positive check on its proposed fix, and two retractions.
**The endorsed branch has had none of that.** Applying the weaker standard to my own recommendation
is precisely how a project talks itself into a direction.*

## TLDR

All night I have been pulling apart one of the two options in front of you -- measuring it,
replicating it, and twice taking back things I had said about it. **The other option is the one I
recommended, and I had not examined it at all.**

So I did. **The result supporting it is a single run, on one word list, with no error bars** -- and
the person who recorded it wrote at the time that it was "not a claim yet". By the same rule I
have been applying to myself all night, that makes it a promising hypothesis rather than a finding.

**And the one carefully-built test of it failed.** Rating words by how touchable or visible they
are did contain genuine information -- it beat scrambled versions decisively. **But it could not
beat simply guessing the same answer for every word.**

That is the same shape of failure as the text side, in a different channel: **real signal, no
useful discrimination.** Which is a caution worth having before spending on it, because part of the
appeal was that it seemed to escape the problem.

None of this says the direction is wrong. It says the evidence for it is thinner than the evidence
I have been holding the other option to, and **the difference was that I liked this one.**

## QUESTIONS

None. The direction is the owner's and it stands; this is about what to do FIRST inside it.

## NEXT STEPS

1. **REPLICATE the positive result before building on it** -- second gold, second corpus, and a CI.
   It is the same demand I made of my own phrase result, and it is cheap relative to a build.
2. **Understand the 0.6195 constant-prototype floor**, because a query-INDEPENDENT score beating
   every query-dependent one is the same tell that has appeared repeatedly tonight. If perceptual
   norms mostly encode *how generic a word is*, that is worth knowing before they are wired in.
