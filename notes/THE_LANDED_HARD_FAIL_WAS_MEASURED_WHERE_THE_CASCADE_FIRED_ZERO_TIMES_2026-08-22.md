# **THE LANDED `HARD_FAIL` ON THIS LINE WAS MEASURED ON A VERSION WHERE THE FOUR-TIER STRUCTURAL CASCADE FIRED `0` TIMES OUT OF `36`. TODAY IT FIRES `10`.**

**No new data and no re-run. The landed run stored its own per-item details in its checkpoint, and
nobody had opened them.** Reproduce: `tools/known_answer_arm_goal_bearing_in_lexicon.py`.

---

## 1. THE COMPARISON -- SAME 36 ITEMS, BOTH EMPTY OVERLAY

| | landed (started `2026-08-06T20:05:00Z`) | today, HEAD |
|---|---|---|
| accuracy | `0.1667` | **`0.3889`** |
| returns `NONE` | `29/36` | `20/36` |
| **STRUCTURAL FIRINGS** | 🔻 **`0`** | **`10`** |
| of which correct | `0` | `9` |

**In the landed run EVERY ONE of the 36 items carries `reason = abstain_fallback_to_lexicon`.**
*Not "the cascade fired and was wrong" -- **the cascade did not run.** All 6 of its correct answers
came from the goal-independent word lexicon.*

> # 🚫 **THE VERDICT DOES NOT CHANGE. `0.3889` IS STILL FAR BELOW THE `0.6389` FLOOR AND `HARD_FAIL` STANDS.** ***WHAT CHANGES IS THE DIAGNOSIS.***

## 2. WHY IT MATTERS: SEVERAL LIVE ANALYSES DESCRIBE MACHINERY THAT DID NOT RUN IN THE RUN THEY CITE

The plan's structural-rule analysis -- *`same_class_same_referent` -> `MET` x9,
`referent_mismatch` -> `UNMET` x8, `opposed_class` -> `UNMET` x2, `grounded_result` -> `UNMET` x1*,
about **20 firings** -- **cannot be describing the landed run, which had zero.** It is describing a
RECENT overlay-condition measurement. *Both are real; they are different runs of a changed organ,
and the landed `metrics.json` still reads `0.1667` while the plan reasons from `0.4722`.*

**This is standing discipline 4 -- ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM
-- for the seventh time**, and it is the same shape as the certification repair's
*"THE SYSTEM IMPROVED AND THE TEST FAILED"*: **the organ got better and its landed record did not
move.**

## 3. ⚠️ THE SIX CHECKS, RUN BEFORE WRITING THIS DOWN (CLAUDE.md evidence discipline 5)

*A claim that something differs from the documented record is itself a claim and gets the same
scrutiny.*

1. **Right file** -- the cell's own output dir; `units.jsonl` written by the landed run itself.
2. **Right version** -- **this IS the variable.** `_start_marker.json` dates the run to
   `2026-08-06T20:05:00Z` and both artifacts were written `16:08:52` local that day.
3. **Right environment** -- `.venv` on my side; the landed side ran through the cell's own harness
   (`host FrameworkMPC`).
4. **Right corpus** -- the same `goal_bearing_modern_eval_v1` OOV subset, `n=36` on both sides.
5. **Right metric** -- the same `_score` `details` schema, the same `correct` and `reason` fields.
   *I did not recompute their number; I read the one they stored.*
6. **Right arm** -- **both EMPTY overlay.** Theirs by accident (`n_registered=0`: learning
   registered nothing, so `main` collapsed onto `baseline`, and the stored
   `fallthrough_baseline_accuracy 0.1667` confirms they coincide). Mine deliberately, and
   positive-controlled: it reproduces the documented EMPTY-map `0.3889` to four digits.

⚠️ **ONE LIMIT, STATED: `units.jsonl` IS GITIGNORED** (`.gitignore:53`, `data/*/**`), so it is a
LOCAL artifact and not part of the committed record. *Its provenance here is established by the
start marker and mtimes, not by git.* **The tool SKIPS this section rather than failing when the
file is absent, so it will not fabricate a comparison on a machine that lacks it.**

## 4. 🎯 IT ADDS A THIRD POINT TO YESTERDAY'S PINNED PREDICTION -- AND THE POINT IS FREE

*Last turn I pinned an arithmetic prediction: if the empty condition commits `10` times for `9`
correct and the overlay commits `19` for `10`, the overlay buys `+9` commitments and `+1` correct.*
**The landed run supplies a third point at the bottom of that curve, at zero cost:**

| condition | structural firings | correct |
|---|---|---|
| landed 08-06, empty | `0` | `0` |
| today, empty | `10` | `9` |
| today, overlay (plan's figure) | `19` | `10` |

> ### **THE SHAPE IS DECLINING MARGINAL PRECISION: THE FIRST `10` FIRINGS RETURN `9` CORRECT; THE NEXT `9` RETURN `1`.**

🚫 **STILL A HYPOTHESIS, NOT A RESULT.** *The third point crosses conditions and the `19` also
conditions on goal recognition, so the subtraction is not licensed -- **the same "no number crosses
populations" rule I invoked when I pinned it.*** ✅ **What the third point DOES buy: the curve is no
longer two dots and a story. Three points, one of them free and adversarial to the tidy version.**

---

## TLDR

The official recorded score for this line of work was measured on a version of the machine whose
main reasoning machinery never actually ran -- every one of the 36 questions fell through to a
crude word-lookup. Today that machinery runs on 10 of the 36 and gets 9 of them right, and the
score has gone from about 17% to about 39%. **The machine is meaningfully better than its own
record says, and still nowhere near passing** -- the bar is 64% and the official verdict of failure
is unchanged.

The part worth acting on: some of our current reasoning about *why* it fails describes machinery
that was switched off in the run being quoted. That is not a small bookkeeping point, because those
descriptions are what the next build would be aimed at.

## QUESTIONS

None. Q106 and Q107 remain open with the owner and neither blocks this.

## NEXT STEPS

1. 🎯 **Re-land this cell so the record matches the organ.** *Its stored number is 16 days and at
   least one behaviour change stale, and every analysis that cites it inherits that.*
   ⚠️ **Requires an experiment-cell run, which this repo routes to `hdi_exp_dev` rather than the
   main thread -- NOT done here.**
2. **The overlay-condition per-reason split remains the one test that settles section 4**, and it
   comes free with that same re-run now that `per_item_predictions` ships.
3. ⚠️ **Check the other cells on this line for the same staleness before quoting them** --
   `exp_verbclass_backoff_coverage_v1`/`v2` and `exp_grounding_acquisition_loop_v1` all read this
   bank, and the question *"which version produced the number I am citing"* has now been wrong once.
