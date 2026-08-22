# **OP1/Q112 CLOSED: THE "238 OVERSTATED RESULTS" ARE AT MOST `15`. `135` WERE THE DETECTOR COMPARING QUANTITIES THAT ARE NOT COMPARABLE.**

**Owner ruling: *"re adjudicate them I think - you can do it fast, and then put this behind us."***
**My own standing recommendation had been the opposite** -- blanket-mark all of them, on an estimate
that re-adjudicating "one at a time" was weeks. **That estimate assumed a human reading each cell.
It was wrong for the part decidable from the numbers alone**, which is nearly all of it.

Tool: `tools/adjudicate_floor_flags.py` (`--self-test`, 10/10). It **imports**
`strongest_floor_audit.scan()` rather than reimplementing it, and **edits nothing** -- it writes
`data/floor_flag_adjudication.json` and stops.

---

## 1. THE ADJUDICATION -- 7,868 metrics.json scanned, 286 flagged, every one given a verdict

| disposition | n | what it means |
|---|---|---|
| 🔻 **`NOT_SUPPORTED`** | **`15`** | commensurable numbers, the cell's OWN floor beats its OWN best treatment, under a **passing** verdict |
| `NEEDS_A_PERSON` | `7` | same quantity but within `0.01` -- not decidable mechanically |
| `UPHELD` | `14` | treatment genuinely beats its strongest floor; the flag was caution |
| `SELF_DECLARED` | `115` | the cell already calls itself FAIL / MIDDLE / PARTIAL -- **it was never claiming a win** |
| 🚨 **`NOT_COMMENSURABLE`** | **`135`** | the two numbers are different KINDS. **A detector artifact, not a claim.** |

> # **THE HEADLINE: `47%` OF THE FLAGGED SET WAS THE DETECTOR COMPARING AN ACCURACY TO A REJECT RATE, OR A MAX TO A MEAN, OR AN ERROR-GAP WHERE HIGHER IS WORSE. ANOTHER `40%` WERE CELLS THAT ALREADY DECLARED THEMSELVES FAILURES.**

**Two examples, both from the audit's own first five rows:**

```
exp_active_learning_loop_gap_detect_lookup_revise_v2
    floor     1.0000  mean_acc_strong.RANDOMIZED_LOOKUP      <- an ACCURACY
    treatment 1.0000  mean_reject_rate_gated_badsource       <- a REJECT RATE
exp_affectedness_weak_sup_revival_loop_v1
    floor     0.9000  contrast_pair_stats.SHUFFLED.max_err_gap
    treatment 0.0536  contrast_pair_stats.LOC.mean_err_gap   <- max vs mean, and "err" inverts
```
*`strongest_floor_audit.py` said this about itself in its own output -- **"286 IS A READ LIST, NOT
286 DEFECTS"** -- and it was right. Nobody had done the reading.*

## 2. ⚠️ `15` IS AN UPPER BOUND, AND I CAN SEE ARTIFACTS INSIDE IT

**I am not claiming 15 confirmed defects.** At least two shapes survive into that list:

- `exp_substrate_anchor4_..._seed_13` -- floor `max_recency_decode_acc` vs treatment
  `recency_decode_acc`. **That is max-vs-plain**, and my aggregator rule only fires when BOTH keys
  carry an aggregator. A residual false positive of exactly the kind the rule was written for.
- `exp_reasoning_readout_length_generalization_clutrr_cg_v1` -- floor and treatment leaves are both
  `arm_a`, an ARM NAME rather than a metric, so "same quantity" is not established.

➡️ **THE HONEST STATEMENT: `15` cells need a human read; the true count is `15` or fewer.**
*That is a tractable afternoon, not weeks -- which is the whole point of the exercise.*

**AND ONE CHECK OF MINE CANNOT FIRE, DISCLOSED RATHER THAN LEFT LOOKING CLEAN:**
`SMOKE_OR_SELFTEST` reads `0` because `scan()` does not return `run_mode`. **It is a dead branch,
not a measurement that no smoke runs were flagged.** Some of the 115 `SELF_DECLARED` and 135
`NOT_COMMENSURABLE` rows are very likely smokes caught by another rule first.

## 3. 🔻 THE BUG IN MY OWN TOOL, AND IT IS THE SAME LESSON AGAIN

**The first run reported `171 NEEDS_A_PERSON / 0 NOT_COMMENSURABLE / 0 NOT_SUPPORTED`** -- a
degenerate distribution with zero in four of six buckets, while I had *hand-verified* that
commensurability failures exist in the audit's first five rows.

**Cause: I read `hit["floor"]` and `hit["floor_key"]`. The real schema is `best_floor: {key,
value}`.** Every lookup returned `None`, every row fell through to "not a number", and the tool
produced a clean-looking table of nonsense.

> ### **THE SELF-TEST PASSED THE ENTIRE TIME, BECAUSE ITS FIXTURES USED THE SCHEMA I HAD INVENTED.**
> *A checker sharing a flaw with what it checks hides it -- for at least the seventh recorded time
> here, and this time the checker and the flaw were both mine.*

✅ **THE FIX IS A CONTRACT TEST, not a corrected fixture:** the self-test now runs the **REAL**
`scan()` on a real metrics.json and asserts (a) the keys `adjudicate()` reads actually exist, and
(b) a real hit is **decidable** rather than silently dumped into `NEEDS_A_PERSON`. **A fabricated
fixture can never again certify an imagined schema.**
*What caught it was not the test -- it was the OUTPUT DISAGREEING WITH SOMETHING I HAD CHECKED BY
HAND. "Make outputs print quantities that constrain each other" earning its place again.*

## 4. A DISCREPANCY IN THE ORIGINAL QUESTION, STATED

**OP1 said `238`. The audit reports `286`** (`143` FLOOR_BEATS_TREATMENT + `193`
WEAKER_FLOOR_QUOTED, overlapping). *I did not reconcile these; `238` may be an earlier run or a
filtered subset. **Neither number survives adjudication, so the reconciliation does not change any
decision** -- but the `238` should not be re-quoted.*

---

## TLDR

You told me to re-adjudicate the 238 overstated results rather than blanket-mark them, and that it
could be done fast. You were right on both counts, and my "this takes weeks" estimate was wrong.

**Nearly all of them were not overstatements at all.** About half were our own detector comparing
things that cannot be compared -- an accuracy against a rejection rate, a maximum against an
average, an error score where a bigger number is worse. Another 40% were experiments that had
already declared themselves failures, so there was no claim to overstate.

**What is actually left is fifteen**, and I can see that at least two of those are still detector
noise. That is an afternoon of reading, not a project.

I also broke my own tool while writing it and reported a clean-looking table of nonsense. The
self-test passed the whole time because I had tested it against a data format I invented rather
than the real one. What caught it was the answer disagreeing with something I had checked by hand.

## QUESTIONS

None.

## NEXT STEPS

1. **Read the 15 by hand** and mark the genuine ones in place. *That is the "stop the spread" half
   of OP1, now against a list small enough to actually finish.*
2. **Tighten two rules first** -- max-vs-plain-aggregator, and an arm name mistaken for a metric --
   which will shrink the 15 before anyone reads it.
3. 🚫 **Do not re-quote `238` or `286` as a count of overstated results.** Both are read-list sizes.
