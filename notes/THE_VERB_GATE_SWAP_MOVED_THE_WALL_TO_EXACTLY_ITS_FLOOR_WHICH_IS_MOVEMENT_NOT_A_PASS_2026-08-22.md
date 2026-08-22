# **THE VERB-GATE SWAP MOVED PRIMARY ACCURACY `0.4722 -> 0.6389`. THAT IS *EXACTLY* THE MAJORITY FLOOR, SO THE PRE-REGISTERED GATE STILL READS `HARD_FAIL`.**

**My pre-declared kill condition did NOT fire** *(it was: "if accuracy stays at 0.4722 +/- noise with
recall fixed, candidate selection is not the limit and the credit thread retires")*. **Accuracy moved.
But it moved to the floor, not past it, on 36 items -- so this is a HYPOTHESIS, not a result.**

---

## 1. WHAT WAS CHANGED, AND WHAT WAS DELIBERATELY NOT

`_credit_targets` gated candidate verbs on one line: `lemma_verb(tok) != tok or tok.endswith(("ed",
"ing"))` -- **recall `0.6026`, missing 3,528 of 8,877 real verbs** (measured yesterday against the
UD-EWT tagger already loaded on the live path).

**ADDED AS A SWITCH, NOT A SWAP: `VERB_GATE`, default `"morph"` = the shipped behaviour.** *Replacing
it outright would silently invalidate every landed credit number, so the old gate stays default and
`HD_VERB_GATE=tagger` selects the new one.* A POS tagger needs SEQUENCE context, so the gate could not
stay a per-token predicate -- tagging happens once per token list inside `_credit_targets`.

✅ **REUSE, NOT A PARALLEL BUILD.** *The tagger is already trained, already on disk under
`data/frontend_assets/`, already loaded by `reading_grounding_loop.StructuralEncoder`.*

## 2. ✅ BOTH CONTROLS PASSED BEFORE THE RESULT WAS READ

| control | outcome |
|---|---|
| **default path unchanged** | full cell re-run under `morph`: **`primary = 0.4722`, coverage `434`/`164` -- IDENTICAL to landed**, 71.2 s genuine recompute |
| **arms actually differ** | `"the children play in the yard"` -> `morph []` vs **`tagger ['play']`**; same for `help`, `eat` |
| **is it a majority-class collapse?** | 🔻 **CHECKED FIRST, because `0.6389` equalling the floor to four digits is the classic signature.** **NO: `met 16/23`, `unmet 7/13`** -- a collapse would read `23/23` and `0/13` |
| module witness | `WITNESS PASS` |

## 3. THE NUMBERS, WITH WHAT n=36 CAN ACTUALLY SUPPORT

| arm | correct | primary | 95% Wilson CI |
|---|---|---|---|
| MORPH (shipped) | 17/36 | `0.4722` | `[0.3199, 0.6299]` |
| **TAGGER** | **23/36** | **`0.6389`** | `[0.4757, 0.7752]` |
| *majority floor* | *23/36* | *`0.6389`* | -- |

> ### 🔻 **THE CIs OVERLAP HEAVILY, AND THE ARM LANDS *ON* THE FLOOR RATHER THAN ABOVE IT. THE GATE IS `primary <= floor -> chance`, SO THE VERDICT IS STILL `HARD_FAIL`.**

⚠️ **AND THE CORRECT TEST IS IMPOSSIBLE.** *These are the SAME 36 items under two conditions, so the
right statistic is PAIRED (McNemar). **The cell does not persist per-item predictions**, so I can only
offer an unpaired approximation (`p ~ 0.033`), which is the wrong test and I am not leaning on it.*
**This is the "SAVE THE POPULATION YOU SCORED" rule biting for the fourth recorded time -- and this
time it blocks the only analysis that would settle the finding.**

## 4. 🔑 WHAT IS GENUINELY NEW HERE

**This intervention CHANGES DECISIONS. The closest precedent changed only LABELS.** *The `lemma_verb`
repair took gold verb-inflection `53.50% -> 99.03%` and the wall reproduced to FOUR DECIMAL PLACES.
I cited that precedent as the reason to expect nothing.* **It was the right precedent to cite and the
outcome differed**, because that repair fixed what candidates were CALLED and this one fixes WHICH
TOKENS ARE CANDIDATES AT ALL. *Learnable-subset accuracy `0.3571 -> 0.6250`; newly-registered eval
lemmas include `carry` and `whisper` -- real content verbs the old gate could never see.*

## 5. ⚠️ A STANDING DEFECT VISIBLE IN **BOTH** ARMS, UNRELATED TO THIS CHANGE

**The light-verb canary reads `neutral_rate 0.0` -- `24` of `24` (morph) and `25` of `25` (tagger)
light verbs POLAR-LOCKED, zero landing `GROUNDED_NEUTRAL`.** The module docstring calls the wash-out
*"the pre-registered light-verb payoff"*: `be/go/make/give` co-occur with both met and unmet outcomes
and are supposed to cancel. **They are not cancelling. Every one of them is being forced to a
polarity.** *That is a separate, older defect than the one I fixed, and it is upstream of any accuracy
number this cell reports.*

## 6. LIMITS

1. **n = 36 eval items.** A 6-item swing. Everything above is small-n.
2. **One run, one config.** The cell is deterministic apart from scramble seeds, so cross-seed
   replication is not available here -- this is a `SINGLE_SEED_HYPOTHESIS` by the standing rule.
3. **The tagger brings its own noise**: contraction fragments (`don`, `t`, `didn`) and at least one
   proper noun (`matthew`) are tagged VERB. Pre-existing tokenizer behaviour, now newly admitted.
4. **`metrics.json` was restored to the landed MORPH run** after the experiment; the tagger output
   lives in `scratch/_wall_TAGGER.json` and is NOT presented as a landed result.

## TLDR

Yesterday I found that before the system can work out which action caused an outcome, it first has to
decide "is this word an action?" — and it was doing that with a spelling rule that **misses about four
in ten real actions**, including *see, go, come, help, eat, play*.

**We already own a proper grammar tool that does this proper.** I connected it as an option, leaving the
old behaviour as the default so nothing already measured changes.

**The score went from about 47 out of 100 to about 64 out of 100.** I had predicted, in writing, that
nothing would happen — a very similar repair earlier this month improved an underlying tool from half
right to almost fully right and changed the final score by literally nothing. **So this is the first
time in this line of work that a component fix has actually changed the system's decisions.**

**But I am not calling it a win, for two honest reasons.** First, the score landed *exactly* on the
"just guess the most common answer" baseline — it caught up with guessing, it did not beat it, and the
project's own pass/fail rule requires beating it. Second, the whole test is only 36 questions, so a
six-question swing is well within luck; the proper statistical test for this comparison **can't be run
at all**, because the experiment never saved which individual questions it got right.

**The most useful thing to do next is unglamorous: make it save that.** It's a few lines, and without
it this result can't be settled either way.

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **MAKE THE CELL PERSIST PER-ITEM PREDICTIONS, then re-run both arms and run McNemar.** *Until
   that exists, `0.6389` is a point estimate with no admissible test behind it.*
2. **The light-verb wash-out is broken in both arms** *(0 of 24 neutral where the design says they
   should cancel)* -- **that is upstream of this whole comparison and is worth more than another
   accuracy point.**
3. *Method note: I cited the right precedent for why this would fail, and it failed to fail. **A
   well-chosen precedent is a reason to test, not a reason to skip the test.***
