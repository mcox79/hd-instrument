# THE CONTEXT-DIVERSITY TEST IS **INVALID BY CONSTRUCTION** -- REPORTED AS A FAILED DESIGN, NOT AS A REFUTATION

**2026-08-20, late.** The owner's directive to read the theory surfaced the instance-based account
of word learning (Bolger, Balass, Landen & Perfetti): meaning emerges by abstracting across
**DIVERSE** encounters, and context **variation** -- not volume -- is the active ingredient. Our
substrate accumulates a trace per encounter and abstracts by argmax, **so this is our own mechanism's
theory, and we have never tested its central claim.** I built the test. **It does not work, and the
reason is worth more than the number.**

## WHAT IT RETURNED

n=4,139 terms, >=3 traces each, cued from a held-out sentence split (**35,906 cue sentences
excluded**), ranks via `tools/rank_with_ties.py`:

| | rho with quality (rank; **lower rank = better**) |
|---|---|
| COUNT (number of encounters) | **+0.461** |
| DIVERSITY (1 - mean pairwise cosine of its traces) | **+0.204** |
| partial DIVERSITY given COUNT | +0.198 |
| partial COUNT given DIVERSITY | +0.461 |

**Read naively: more encounters make the read-out WORSE, and more varied encounters make it WORSE
-- i.e. the instance-based prediction fails and volume actively hurts.** That would have been a
striking headline.

## ⛔ WHY IT IS INVALID: THE OUTCOME REWARDS THE OPPOSITE OF THE PREDICTOR

**The outcome is "rank of the term when retrieved from a sentence that mentions it". That measure
rewards TOPICAL NARROWNESS.** A word that only ever occurs in one kind of sentence is trivially
retrievable from another sentence of that kind. A word occurring across many topics is not --
**regardless of how well its meaning was learned.**

**And "diversity" IS topical spread. So the predictor and the outcome are anti-correlated by
construction, before any learning happens.** The term lists make it unmissable:

| | terms |
|---|---|
| **LEAST diverse** | `uzbeki, turkmeni, heterotroph, decomposers, subfield, tom's, bob's, sally's, leap` |
| **HIGHEST count** | `atom, april, material, afghanistan, chemistry, australia, idea, study, finland` |

**The least-diverse terms appear in exactly ONE narrow place** -- a single country article, a single
story -- **so their held-out cue is drawn from that same narrow place and retrieval is easy.** The
highest-count terms are corpus-central words spread across many articles, whose profiles blend many
topics and are therefore LESS distinctive. **Both predictors are proxies for topical spread, and
topical spread is what the outcome actually measures.**

**➡️ SO THIS SAYS NOTHING ABOUT WHETHER CONTEXT VARIATION HELPS LEARNING. It says a retrieval task
favours narrow words, which we already knew and which is not the question.**

## WHAT A VALID TEST NEEDS, AND WHY IT IS NOT CHEAP HERE

**The outcome must not reward topical narrowness.** The obvious candidate is the one built earlier
tonight: does the term's BANKED MEANING contain a ConceptNet-attested hypernym? That is a property
of the meaning, not of the term's distribution.

**But it is underpowered on our data, and that is a fact about the substrate rather than about the
test.** Banked distributional meanings number ~190 per read; ConceptNet covers ~75% of them; and
their hit rate is **0-4%** -- so a correlation would rest on a handful of positive cases.
**A well-powered version needs either far more banked facts or a denser quality measure**, and
inventing one tonight would be exactly the kind of convenient instrument this project keeps
catching itself building.

## 🔑 THE THING WORTH KEEPING

**I nearly published "the instance-based prediction fails on our representation".** It was
pre-committed as one of four readings, the number was clean, n was 4,139, the leak control had
excluded 35,906 sentences, and the partial correlations were computed properly. **Every discipline
was followed except asking what the outcome measure actually rewards.**

**A control checks whether the RESULT is real. This needed a check on whether the QUESTION was
answerable by that instrument** -- the standing "could this experiment have succeeded?" question,
asked about the METRIC rather than about the mechanism. *Today's ledger already records that as the
highest-yield habit found; this is the fifth time it has paid, and the first time it saved a
theory from being wrongly refuted.*

## TLDR

The research the owner pointed me at says words are learned by meeting them in **varied** settings,
not merely often. Our system does the "meeting them often" part and ignores the variety. So I
measured whether variety predicts a better result.

**The numbers came out backwards -- suggesting both variety AND repetition make things worse. I do
not believe them, and the reason is a flaw in my own test.**

I measured "quality" by asking the system to find the right word given a sentence. But a word that
only ever appears in one corner of the corpus -- like a country name that shows up in a single
article -- is trivially easy to find that way, while a word that appears everywhere is hard.
**So my measure of quality was really a measure of narrowness, which is the opposite of the thing I
was testing.** The two were rigged against each other before any learning took place.

The honest outcome is: **the theory's central claim remains untested here, and the obvious better
test is underpowered on our data.** I have written down what a valid version needs so nobody
repeats this.

The near-miss is the useful part. Everything about the test was careful -- big sample, leak control,
the right statistics -- **except asking whether the yardstick could answer the question at all.**

## QUESTIONS

None.

## NEXT STEPS

1. **Do not cite the diversity numbers.** They measure topical spread.
2. A valid test needs a quality measure that is a property of the MEANING, not of the term's
   distribution -- and enough banked facts to power it. **Both are blocked on the same thing: the
   substrate banks few facts and few of them are right.**
3. **The instance-based framing still deserves a test**, because it is the only theory found so far
   that describes our own mechanism. The cheapest honest version is probably an INTERVENTION
   (hold encounter count fixed, select encounters to be maximally vs minimally varied, compare)
   rather than a correlation over existing terms.
