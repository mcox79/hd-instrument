# ANGLE A -- THE FREQUENCY-MATCHED ANOMALY SET IS **BUILT**, AND THE LESSON IS THAT **A PERFECT BALANCE TABLE SHIPPED BROKEN ITEMS TWICE**

**Artifact:** `data/anomaly_set_frequency_matched_v3.json`, 120 items.
**Builder:** `tools/build_frequency_matched_anomaly_set.py` (seeded; other seeds give other items).
**What it is for:** the F5 coherence-monitor evaluation, whose design
(`notes/F5_EVALUATION_DESIGN_...md`) names this as its **mandatory** construction.

---

## 1. THE ACHIEVED MATCHING

| matched on | standardized mean difference | bar |
|---|---|---|
| log document frequency | **+0.0157** | \|smd\| < 0.10 |
| word length | **-0.0749** | \|smd\| < 0.10 |
| UPOS NOUN share | **0.951 vs 0.951** (min intruder 0.800) | -- |
| grammatical number | **120 of 120 agree, 0 violations** (53 PL / 67 SG) | -- |

Distributions match at every quartile, not only at the mean. 107 distinct targets, 102 distinct
intruders, anomaly position spread across the sentence (mean 0.54 of the way through, range
0.03-1.00) so **"flag the last content word" cannot win.**

## 2. ⚠️ **THE FINDING THAT MATTERS MORE THAN THE ARTIFACT**

**V1's balance table was BETTER than v3's -- log-frequency smd +0.0126, length -0.0085, quartiles
aligned -- and its items were unusable.** Reading twelve of them found three defects, **every one
of which would have let a detector win WITHOUT COMPREHENSION** -- the exact confound the matching
exists to remove, arriving through a door the matching does not watch:

| defect | example it shipped | what it would have rewarded |
|---|---|---|
| **WordNet noun-hood is not a POS check** -- `begin`, `past`, `independent`, `inside`, `middle` all carry a rare noun sense | *"the only month to both carbon and end"* | **SYNTAX** |
| **lemmatisation lowercases proper nouns** | *"Several december species"* | orthography / capitalisation |
| **table debris is not prose** | *"Kandahar 1,127,000 54,022 Pashto, Dari 16 districts"* | nothing -- unscoreable |

Fixed with an in-context UPOS tag from the owned perceptron, a case-based proper-noun filter, and a
prose filter. **V2 then passed all of those and STILL shipped an agreement cue** -- *"an English
cultures"*, *"a churches"*, *"a certain events"*, **3 of 14 items detectable on grammatical number.**
Fixed in v3 by requiring number agreement (via the substrate's own `lemma_word` normaliser, verified
against the traps that break a trailing-s rule: `glass`, `species`, `news`, `half` all read singular
correctly) plus an `a`/`an` guard.

**➡️ THE GENERAL RULE, AND IT IS THE ONE TO KEEP: A BALANCE TABLE MEASURES THE MATCHING, NEVER THE
ITEM.** Three rounds of matching statistics got better while the items were, in turn, ungrammatical,
then proper-noun-contaminated, then number-mismatched. **Only reading the items ever found any of
it** -- and v1's numbers were good enough to have been reported as success.

*This is the same shape as tonight's other measurement failures: the statistic the construction
optimises is not the outcome.*

## 3. WHAT IS STILL WRONG WITH IT, MEASURED RATHER THAN ASSUMED

**On a 14-item read of v3: 12 clean, 2 weak (~14%).** Topical disjointness at the corpus level does
not guarantee contextual implausibility -- *"A great example of their **regime**..."* and *"This
**shell** will work, but it will take a very long time"* are both odd but defensible.

**This is a REAL residual and it belongs in the read-out, not in a footnote:** ~1 item in 7 may not
have a detectable anomaly at all, which **caps the achievable score and must not be read as detector
failure.** *The honest handling is a human pass over the full 120 before any verdict, exactly as the
evaluation design demands -- an anomaly set nobody has read is the same mistake as a hand-score
nobody performed.*

## 4. WHAT THIS DOES **NOT** DO

It does not measure anything. **F5 does not exist**; this is its prerequisite. No claim about
coherence monitoring, N400, or the substrate follows from this file.

## TLDR

The test for the missing "notice when a sentence doesn't fit" component needs sentences with an odd
word planted in them. The trap is that odd words are usually **rare** words, so a system that just
flags unusual vocabulary would ace the test while understanding nothing. **The planted word is
therefore matched to the one it replaces on how common it is, how long it is, and what kind of word
it is.** That matching is now essentially exact, and there are 120 sentences.

**The useful part was a mistake I made twice.** The very first version produced a *better* matching
table than the final one — and its sentences were garbage. It had swapped in words that made the
sentence **ungrammatical**, so anyone could spot the odd word without understanding a thing. I fixed
that, and the second version still slipped in a subtler version of the same problem: singular and
plural mismatches like *"a churches"*.

**The matching statistics never once revealed any of this. Reading the sentences revealed all of
it** — which is worth remembering, because the statistics looked like success both times.

Honest remaining flaw: about one sentence in seven, the swapped word is odd but not clearly wrong.
That puts a ceiling on any score from this set, and that ceiling has to be stated up front so a
detector isn't blamed for it.

## QUESTIONS

None.

## NEXT STEPS

1. **A human pass over all 120** before this set is used for any verdict -- I have read 14.
2. The F5 build itself remains cell-authoring work and is not started.
3. Angle B (the meaning-consumption link) is designed and recorded separately.
