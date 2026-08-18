# THE HUMAN-JUDGEMENT INSTRUMENT: `POWER_INSUFFICIENT` AT n=7

**2026-08-18. `experiments/exp_dissociation_score_instrument_human_v1.py`. FULL run halted at the
matching step. NO `metrics.json` was produced and NO ARM WAS SCORED -- deliberately, and this note
exists so nobody rebuilds it.**

## What it was for

`exp_dissociation_score_instrument_v1` is licensed (four floors at chance, known-answer 0.9599) and
every Organ A conclusion rests on it. But it builds `SET_P` from `wn.synsets()` and excludes WordNet
pairs from `SET_S` (36 exact + 839 near-synonyms), and its known-answer arm IS WordNet path
similarity. **So it measures AGREEMENT WITH WORDNET, not substitutability in the abstract**
(`PLAN_ORGAN_STEP_LADDERS` 6.24).

This cell rebuilt the same instrument with **human similarity judgements** (SimLex-999 / SimVerb-3500)
defining the positive set instead, reusing the licensed matching machinery and floor battery verbatim.
**The decisive output was to be the rank correlation between the two instruments' arm orderings** --
which would say whether Organ A's closure is a fact about OUR STORE or a fact about WORDNET.

## What happened, with the funnel

| stage | n |
|---|---|
| benchmark pairs restricted to our 5,491 anchors | **2,233** |
| `SET_P_HUMAN` raw candidates (zero co-occurrence, human score >= 6.0) | **436** |
| `SET_S_HUMAN` raw candidates (>= decile-90 co-occurrence, score <= 4.0) | **122** |
| **after five-covariate matching** | **7 per cell** |

At n=7 an AUC confidence interval is wider than the entire range being discriminated.

## The call, and why it is trustworthy

**`POWER_INSUFFICIENT`, called per the pre-committed branch in `PLAN_ORGAN_STEP_LADDERS` 6.26, which
was written ~20 minutes BEFORE these numbers landed and WITHOUT reading any arm output.**

- **The WordNet caveat (6.24) remains OPEN. It is NOT resolved in either direction.**
- **No arm number from this run may be quoted.**
- **A null here is NOT evidence that the WordNet dependency was harmless.** Three retractions in this
  project came from reading an underpowered null as a capability statement, one of them earlier the
  same day (6.6). *The pre-commitment is the only reason this was called instead of spun.*

## Why it collapsed -- measured, not guessed

The supervision drill (`bd3fb130b`) quantified it independently: **SimLex-999 has 573 of 999 pairs
inside our anchor set, but only 23 touching the 617 evaluation words.** The binding constraint was
never the benchmark's size. It was the three-way intersection of *humans rate these similar*, *they
never co-occur in OUR corpus*, and *a frequency/length/orthography-matched partner exists*.

**The drill also classes SimLex as CONSTRUCT-ADJACENT -- a near-disjoint VALIDATOR, not a supervision
source -- and could not verify its provenance.**

## DO NOT

- **Do not re-run this cell hoping for a better draw.** The funnel is structural.
- **Do not loosen the matching to buy n.** Seven tightening rounds are what got the original
  instrument's four floors to chance; loosening them produces a bigger sample of an unlicensed
  instrument, which is worse than no sample.

## What WOULD answer the question

A benchmark with far greater coverage of our 5,491 anchors; **or** a label source that does not
require zero co-occurrence by construction; **or** an operationalisation of substitutability that is
neither WordNet-derived nor dependent on a small curated pair list -- for example held-out cloze
interchangeability measured on our own corpus, which has no coverage ceiling. **Each needs its own
circularity audit before it is trusted.**

**Status: the cell and its `units.jsonl` are committed as the record of a null. It is not wired,
not registered, and produced no capability claim.**
