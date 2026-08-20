# ANGLE A -- THE ANOMALY SET IS **BUILT AND HAND-SCORED**, AND THE LESSON IS THAT **THE BALANCE TABLE WAS PERFECT AT EVERY STAGE WHILE THE ITEMS WERE BROKEN IN FIVE DIFFERENT WAYS**

**Artifact:** `data/anomaly_set_frequency_matched_v8.json`, 120 items.
**Hand-scores:** `data/anomaly_set_frequency_matched_v8_handscores.json` -- **all 120 read.**
**Builder:** `tools/build_frequency_matched_anomaly_set.py` (`--self-test`; refuses to build if it fails).
**Serves:** the F5 coherence-monitor evaluation, whose design names this construction as mandatory.

> 🚫 **`data/anomaly_set_frequency_matched_v3.json` IS SUPERSEDED AND DEFECTIVE -- DO NOT USE.** It
> is still tracked (committed before the defect was found) and contains **10 grammatical-number
> violations** that its own check reported as **"120 of 120 agree, 0 violations"**.

---

## 1. THE FINAL SET

| matched on | smd | bar |
|---|---|---|
| log document frequency | **-0.0134** | \|smd\| < 0.10 |
| word length | **-0.0289** | \|smd\| < 0.10 |
| UPOS NOUN share | 0.953 vs 0.947 | -- |
| grammatical number | **120/120 agree** | -- |

**120 of 120 distinct (target, intruder) pairs**, no target used more than twice -- *V7 used
`cities -> changes` four times, and repeated pairs are not independent items.*

## 2. 🚨 **THE HAND-SCORE, WHICH IS THE ONLY THING THAT MEASURES ITEM QUALITY**

| verdict | n | meaning |
|---|---|---|
| **CLEAN** | **102** | grammatical sentence, intruder clearly does not belong -- the anomaly is SEMANTIC |
| **WEAK** | **17** | grammatical, intruder **defensible in context** -- there may be no anomaly to find |
| **BROKEN** | **1** | detectable WITHOUT comprehension -- exclude before scoring |

**➡️ THE CEILING: WITH 17 WEAK ITEMS, A PERFECT DETECTOR CANNOT SCORE ABOVE ~86% ON THIS SET. THAT
NUMBER MUST BE PRINTED BESIDE ANY RESULT** -- otherwise the shortfall gets read as detector failure,
which is this project's most expensive recurring error in miniature.

The single BROKEN item is instructive: `touch` is a **verb** in *"when people touch animals"* but the
tagger called it a NOUN, so the intruder landed in a verb slot -- *"When people debt animals"*. **A
POS tagger's error becomes a syntax cue**, i.e. the confound comes back through the tool hired to
prevent it.

## 3. ⚠️ **FIVE ROUNDS. THE BALANCE TABLE WAS FINE EVERY TIME.**

**V1's matching was the BEST of all eight versions -- log-frequency smd +0.0126, length -0.0085 --
and its items were unusable.** Each round the statistics stayed excellent and reading the items
found something new:

| v | what reading found | what it would have rewarded |
|---|---|---|
| **1** | WordNet noun-hood admits verbs/adjectives (`begin`, `past`, `inside`) -> *"the only month to both carbon and end"* | **syntax** |
| **1** | lemmatisation lowercased proper nouns -> *"Several december species"* | orthography |
| **1** | table debris -> *"Kandahar 1,127,000 54,022 Pashto"* | nothing -- unscoreable |
| **2** | number mismatch -> *"a churches"*, *"an English cultures"* | **agreement** |
| **4** | **the number CHECK was broken** (below) | agreement, silently |
| **5** | **near-synonym intruders** -> *"Many countries have RULES based on this idea of fairness"* -- **still TRUE** | **nothing: a perfect detector must FAIL** |
| **5** | corpus misspellings as intruders -- `countrys`, `todays`, `cetera` | **orthography** (a mandatory floor) |
| **6** | repeated pairs: `cities -> changes` x4 | overstated n |
| **7** | the splice **destroyed punctuation** -- `fire)` -> `music` left an unbalanced paren | **punctuation, at the scored position** |

**THE NEAR-SYNONYM CASE IS THE WORST AND THE MOST INSTRUCTIVE.** My topical-disjointness rule --
*"the intruder must never co-occur with a host content word"* -- was supposed to guarantee
anomalousness. **It cannot, and worse, it was actively SELECTING for synonyms: co-occurrence is not
relatedness, and synonyms are precisely the words that SUBSTITUTE for one another rather than
appearing together.** A plausible-sounding constraint was producing the exact failure it was written
to prevent. Fixed with a WordNet sense/hypernym/co-hyponym block.

## 4. 🔁 **AND THE CHECK ITSELF WAS BROKEN, TWICE, IN THE WAY THE REPO ALREADY DOCUMENTS**

**V3 reported "120 of 120 agree, 0 violations" and shipped 10 violations** -- *"Many countries have
thing"*, *"Usually the days is used"*. Two causes, both worth more than the artifact:

1. **THE CHECK CALLED THE SAME FUNCTION THE BUILDER DID.** `lemma_word` is documented to return a
   real English word rather than a stem -- which is why it is right for concept identity -- and that
   same guarantee leaves `laws -> laws` and `values -> values` unchanged, so both read SINGULAR.
   *A checker sharing a flaw with what it checks hides it: standing discipline 3, again.*
2. **THE SELF-TEST PASSED THROUGHOUT, BECAUSE IT NEVER USED THE PRODUCTION CALL SIGNATURE.** It
   called `gn(w)`; the builder called `gn(w, vocab)` with the FILTERED common-noun set, which omits
   `law`. **A self-test that does not exercise the call the caller makes is a self-test of a
   different function.** *Fixed by DELETING the parameter -- removing an argument removes the class
   of bug where a caller passes the wrong one.* The v4 regression is now a permanent case in
   `--self-test`, and the builder refuses to run if it fails.

## 5. WHAT THIS DOES NOT DO

**It measures nothing. F5 does not exist.** No claim about coherence monitoring, the N400, or the
substrate follows from this file.

## TLDR

The test for the missing "notice when a sentence doesn't fit" part needs sentences with an odd word
planted in them. The trap: **odd words are usually rare words**, so a system that just flags unusual
vocabulary would ace the test while understanding nothing. So the planted word is matched to the one
it replaces on commonness, length and word type. That matching is now essentially exact.

**The valuable part was getting it wrong five times in a row.** Every version produced excellent
matching statistics. Every version had broken sentences, and **only reading them ever found out** —
first sentences that were simply ungrammatical, then singular/plural mistakes, then, worst,
**sentences where the swapped-in word was a synonym, so the sentence stayed perfectly true and there
was no odd word to find at all.** My rule for guaranteeing oddness was quietly causing that: it
picked words that never appear near each other, and synonyms are exactly the words that replace each
other instead of appearing together.

**Twice the checking code was broken too**, and in the most embarrassing way available: it reported
"zero problems" while ten sentences were wrong, because the check used the same faulty helper as the
thing it was checking, and its own self-test never tested the way the program actually calls it.

I then read all 120 final sentences myself: **102 good, 17 arguable, 1 unusable.** The 17 arguable
ones matter — they mean **even a perfect system could only score about 86% here**, and that number
has to be stated up front so the system doesn't get blamed for the test's own limits.

## QUESTIONS

None.

## NEXT STEPS

1. **v8 + its hand-scores are ready to serve the F5 evaluation.** Exclude the 1 BROKEN item; report
   the ~86% ceiling beside any score.
2. **F5 itself is not started** -- cell-authoring work.
3. Both standing angles are now closed; the next pair needs choosing.
