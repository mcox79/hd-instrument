---
priority: 4
review: 
review_text: 
---

# PROBLEM: THE SCORER COUNTS "I DON'T KNOW" AS A WRONG ANSWER, AND IT IS NOW LIVE

**slug:** `score_counts_abstention_as_error` · **opened:** 2026-08-22 by the strategy session

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.** *A dropped precondition invalidates the
> declared gate even when the result may be fine.*

---

## THE PROBLEM IN PLAIN LANGUAGE

The goal-bearing cell scores its predictions with `ok = (pred == gold)`. **The token `AMBIGUOUS`
never appears in that file.** So when the organ says *"I cannot tell"*, the scorer records a wrong
answer.

**Everywhere else in this repo, `AMBIGUOUS` is an ABSTENTION** — including in the organ's own
engine. It is a wrong answer in exactly one place: the cell the whole line is graded on.

**It disagrees with its own engine, and it disagrees by accident.**

**Your job: make the cell's scorer treat `AMBIGUOUS` the way its engine does, and report every
number that moves.**

## WHY THIS ONE

**Because it stopped being latent today.** It used to bite nothing — the OOV-36 population contained
zero `AMBIGUOUS` predictions, so the defect was real but harmless.

**On the 2026-08-22 re-land it fires 3 times** (`befriend` -> gold UNMET, `find` -> gold MET,
`come` -> gold UNMET) under the learned overlay, **all three scored WRONG by omission.**

**It is small, bounded, and has a clear right answer** — which is exactly the kind of thing that
should be fixed while it is still 3 items rather than after it has silently shaped a verdict.

## MEASURED vs INFERRED

**MEASURED:**
- `AMBIGUOUS` is an ABSTENTION in **five** consumers: `verification/verify_levin_lastresort_backoff.py:51`
  (`_ABSTAIN = ("NA","NONE","AMBIGUOUS")`), `exp_verbclass_backoff_coverage_v1.py:214`, `v2.py:73`,
  `verify_request_response_typing.py:200`, and — in words — `hdlab/consequence_learning_loop.py:219,235`
  (*"AMBIGUOUS -> abstain"*).
- It is a WRONG ANSWER in exactly one: `exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py`,
  whose `_score` does `ok = (pred == gold)` and never mentions the token.
- **`ambiguous_pred_count = 3`** now ships in that cell's `metrics.json` (added on the re-land).
- The cell's current landed verdict is `HARD_FAIL` at `primary_accuracy = 0.3056`, floor `0.6389`.

**INFERRED, NOT MEASURED:**
- 🔻 **That fixing it changes the verdict. It almost certainly does not** — 3 items on 36 cannot
  close a `0.33` gap to the floor. **Do not sell this as a rescue.** It is a correctness fix to a
  measurement instrument, and its value is that the instrument stops lying, not that the number
  improves.

## ALREADY TRIED

- **A guard exists and is the reusable part: `tools/score_with_abstention.py`.** An `AbstentionScore`
  that carries its own convention, **no call signature returning a bare accuracy**, and
  `both_conventions().agree` flagging when the choice could change a headline. Self-test 6/6.
  **REUSE IT — do not write a third convention.**
- That guard's self-test contains an assertion that **FAILS the day the OOV-36 acquires an
  `AMBIGUOUS`** — precisely so this would stop being latent without anyone watching.
- 🔻 **The strategy session did NOT fix it**, twice, deliberately: it is an `experiments/*.py` edit
  and the tripwire routes those to a cell author.

## VERIFY BEFORE YOU START

1. **Confirm the three predictions are still there.** Notes go stale within hours here; read
   `ambiguous_pred_count` and `per_item_predictions` in the cell's current `metrics.json`.
2. **Read `hdlab/consequence_learning_loop.py:219,235`** — the engine's own convention is the
   authority for what the cell should do, not my summary.
3. `python tools/score_with_abstention.py --self-test` before relying on it.

## THE BAR

**The cell's scorer agrees with its own engine, and every number that moves is reported both ways.**

- **Report the primary accuracy under BOTH conventions**, with the counts — abstentions as errors,
  and abstentions excluded. `score_with_abstention.both_conventions().agree` tells you whether the
  choice could change a headline; **quote it.**
- 🚨 **DO NOT let this change a gate's threshold.** If a gate was tuned against the miscounted
  number, say so and file it — **adjusting a band is not a result.**
- **Positive control:** show the scorer producing a DIFFERENT number on the 3 known items after the
  fix than before. A fix that changes nothing on the items that motivated it has not been applied.
- **Negative control:** the OOV-36 baseline (empty overlay, zero `AMBIGUOUS`) must be **byte-identical**
  before and after. If it moves, you changed more than the abstention handling.

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| the defect | `experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py`, `_score` |
| the engine whose convention wins | `hdlab/consequence_learning_loop.py:219,235` |
| the guard to REUSE | `tools/score_with_abstention.py` (self-test 6/6) |
| the four other consumers | listed under MEASURED above |
| the re-land that made it live | `data/exp_consequence_learning_loop_oov_outcome_verb_valence_v1/metrics.json` |

## DO NOT QUOTE

- 🚫 **This as a reason the cell fails.** It fails by `0.33` against its floor; 3 items are not that.
- 🚫 **"the repo convention governs"** as a clean statement — **BOTH conventions live here**, in
  adjacent files. That is the defect. The engine's convention wins *for this cell* because the cell
  wraps that engine, not because one convention is globally correct.
- 🚫 **`0.3056` as a post-fix number** until it has been re-run.
