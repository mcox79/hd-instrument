# MY PROPOSAL ALREADY EXISTS AS **ORGAN B5**, AND THE SUBSTRATE NAMES THE EXACT GAP ITSELF

**I proposed exposing the raw 12-dim sensorimotor vectors as a feature space and called it "a wiring,
not a build" and "the highest-value cheap move tonight."** *It is a wiring. It is also **already
built, already named, already slotted, and already diagnosed**, and the substrate's own organ table
states the remaining gap in one clause.*

**`hdlab/sensorimotor_spoke.py` -- ORGAN B5, "a second spoke: what things look like, feel like, are
done with", added 2026-08-19, status `NEEDS_ADAPTER`.**

---

## 1. THE GAP, IN THE SUBSTRATE'S OWN WORDS

> *"The organ EXISTS, self-tests, and is invoked by `exp_sensorimotor_spoke_grounding_v1`, **but
> `read()` does not consult it**, so it is `NEEDS_ADAPTER` and not `FILLED`."*

**That is the whole of my proposal, written down two days before I made it.** *`cortical_recall.py:86`
imports `profile` from it, so it has one live consumer; the READING path has none.*

## 2. WHY THE ORGAN EXISTS -- AND IT IS THE STRONGEST BRAIN-FOUNDATIONAL ARGUMENT IN THE REPO

| | |
|---|---|
| **PINNED-BY-EVIDENCE** | modality-specific cortex feeds the anterior temporal hub; **concepts are not built from linguistic co-occurrence alone** |
| **PINNED-BY-EVIDENCE** | *"text recovers non-sensorimotor meaning well, **SENSORY meaning poorly, and MOTOR meaning minimally**"* (Xu et al. 2025, Nat Hum Behav) -- **"a published PREDICTION of exactly the ceiling this substrate measured on its own co-occurrence channel, and it is why this organ exists"** |
| **BOUNDING RESULT** | a sensory-INDEPENDENT colour code exists in congenitally blind and sighted alike (Wang et al. 2020, Neuron) -- **so a spoke is NOT the only route. Do not over-claim it.** |
| **UNPINNED** | **the hub-spoke COMBINATION RULE.** No equation exists. *"Every weighting or selection rule here is OUR-INVENTION-BEING-TESTED."* |

**➡️ THE CEILING WE KEEP MEASURING ON THE TEXT CHANNEL IS A *PUBLISHED PREDICTION*, NOT A MYSTERY.**
*Text is expected to do badly on sensory and motor meaning. Our co-occurrence channel is a text
channel. **The result we keep re-deriving was forecast in the literature.***

## 3. AND IT DECLARES ITS OWN HONESTY CONSTRAINTS UNPROMPTED

> *"The Lancaster norms are HUMAN RATINGS... the substrate does not GROW this spoke, it is handed one.
> **That is SUPPLY, not learning, and no result from this organ may be reported as the substrate
> having learned perceptual structure.**"*

> *"`grounded_similarity.py` already loads Lancaster + Brysbaert... **This module CALLS it. Authoring
> a second loader would be islanding.**"*

**A module that pre-emptively forbids the over-claim it would most benefit from, and that refuses to
duplicate a loader on anti-islanding grounds.** *That is the standard the rest of the repo is
measured against.*

## 4. WHAT IS ACTUALLY LEFT TO DO -- SMALLER AND SHARPER THAN "WIRE THE VECTORS"

1. **AN ADAPTER SO `read()` CONSULTS B5.** *That single clause is the entire remaining gap.*
2. **A COMBINATION RULE, WHICH IS UNPINNED** -- so whatever is chosen is **our invention under test**
   and must be labelled that way, never as brain-derived.
3. **SCORED AGAINST POPULARITY**, per the `HARD_FAIL` where a grounded encoder lost to a popularity
   baseline by **0.2269 AUC**.
4. **COVERAGE STATED EVERY TIME: 60.4% of tokens, 10.3% of types** -- it is a spoke, not a
   replacement.

## TLDR

I proposed wiring up the twelve human-rated dimensions as a second source of meaning, and called it
the best cheap move available. **It turns out that organ was built two days ago, and the system's own
component list already says exactly what's missing from it: the reading process doesn't consult it.**
One clause, written before I said it.

**The reason it exists is the strongest piece of reasoning I've read in this project.** Published work
predicts that learning meaning from text alone recovers abstract meaning well, **sensory meaning
poorly, and physical-action meaning barely at all.** Our system learns from text alone. **So the
ceiling we keep bumping into isn't a mystery — it was forecast in the literature, and this organ
exists specifically to address it.**

It also polices itself in ways I rarely see: it states up front that the human ratings are **handed
to the system, not learned by it**, and forbids anyone reporting its results as the system having
learned about perception. And it refuses to write its own copy of the data loader on the grounds that
duplicating one would be exactly the isolation problem I've been cataloguing all night.

**What's actually left is smaller than I said:** a connector so the reading process can use it, plus a
rule for how to combine it with what text already gives us — and that combination rule is explicitly
**not** something the brain research settles, so whatever we choose is our invention and must be
labelled as such.

## QUESTIONS

None.

## NEXT STEPS

1. **The remaining work is the ADAPTER, not the asset.** *That is a much smaller and better-defined
   job than the one I proposed an hour ago.*
2. **`exp_sensorimotor_spoke_grounding_v1` already invokes the organ** -- read it before building the
   adapter; it may already show what the combination rule should be.
3. Any adapter is scored against POPULARITY and reports token/type coverage.
