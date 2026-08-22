# **`185` GROUNDING RESULTS ARE LABELLED HARD_PASS. `7` CARRY BOTH A CONFIDENCE INTERVAL AND A NULL. `4` ARE DISTINCT FULL-SCALE RESULTS. AND ONE "WIN" IS A SMOKE RUN WHOSE FULL RUN READS `MIDDLE_BAND_FLOOR_HUGGING`.**

**Now produced by a self-tested tool that CALLS the census rather than imitating it -- after I got this
count wrong twice yesterday by imitating it.**

---

## 1. THE FUNNEL

| | |
|---|---|
| grounding cells with a `metrics.json` | **711** |
| verdict is HARD_PASS | **185** |
| **...AND carries BOTH a CI and a null** | 🔻 **7** |
| ...AND a floor as well | **7** *(all of them)* |
| **distinct FULL-SCALE results after removing smoke twins** | **4** |

## 2. ✅ **THE FOUR THAT SURVIVE THE CHEAPEST HURDLE**

| cell | what it actually shows |
|---|---|
| **`exp_reading_grounding_loop_cycle2_v1`** | **the loop genuinely accumulates while reading**: foundation `185 -> 3,544` in one cycle, scramble ratio `0.077`, no-leak + monotonicity checked |
| **`exp_foundation_validation_harness_v1`** | three claims each with controls that discriminate: gap `0.2533`; cohesion `0.4765` with **zero contradictions**; mechanism `1.0` vs **scramble `0.0` and ablation `0.0`** |
| **`exp_foundation_validation_harness_v4_proximity_v1`** | clears a **frequency floor**: gap `0.2667` over floor `0.22`, precision `0.4867`, known-answer validity gate PASSES (`chance_hat 0.04`) |
| **`exp_graded_divisive_comparator_v1`** | *n=4,000*: `0.6395 -> 0.6997`, **d `0.0602`, CI `[0.0440, 0.0762]`** -- CI excludes zero -- against floors scramble `0.5065`/`0.4975`, frequency `0.4800`, chance `0.50` |

**That last one is the best-evidenced number in the grounding archive**: a real n, a CI that excludes
zero, and *four* floors including two scrambles and a frequency control. **It is also a `+0.06`
improvement on a discrimination task, not a capability.**

## 3. 🔻 **AND ONE CAUTIONARY CASE, WHICH IS WHY THE SMOKE TWINS MATTER**

| | verdict |
|---|---|
| `exp_context_conditioned_near_neighbour_v1_SMOKE_n600` | ✅ **HARD_PASS** |
| **`exp_context_conditioned_near_neighbour_v1`** *(full run)* | 🔻 **`MIDDLE_BAND_FLOOR_HUGGING`** |

> ### **THE SMOKE PASSED AND THE FULL RUN HUGGED THE FLOOR. Anyone citing this cell by name, or counting HARD_PASS rows, gets the smoke's answer.**

*It carries CI, null AND floor -- so the evidence gate cannot catch this. Only reading the pair does.*

## 4. 🔑 THE METHOD NOTE THAT MATTERS MORE THAN THE COUNT

**Yesterday I counted this subset twice and was wrong twice: `198`, then `58`, against a true `14`
archive-wide.** *Both times I reimplemented the census's logic instead of calling it.* **Two causes:**

1. **I matched the string `HARD_PASS` anywhere in the file. `assess()` reads the VERDICT FIELD**, and
   prefers `final_verdict` over `verdict`.
2. **The census population is `data/exp_*` only.** *I walked every directory.*

✅ **`tools/grounding_evidence_map.py` now imports `assess` and does NO detection of its own, and its
self-test FAILS unless it reproduces the census's archive-wide `14` exactly** -- plus a negative
control on the specific cell that fooled me, and a check that the grounding filter excludes anything
at all. *If a future edit reintroduces private matching, the number drifts and the test fails.*

## 5. ⚠️ WHAT THIS MAP STILL DOES NOT SAY

1. **Carrying a CI and a null is the CHEAPEST hurdle.** *The gate cannot see a written-in answer, gold
   defined by the rule under test, a skipped stronger floor, or a gate tuned after the fact. **A cell
   can pass it and still be worthless.***
2. **I have read verdict fields, not methods.** *Four cells is now few enough to actually read, which
   was the point of narrowing.*
3. **The `711` population is any cell whose file mentions "ground"** -- broader than the `237` that
   match by name. Both numbers are real; they answer different questions.
4. **`178` HARD_PASS grounding cells are not refuted by this.** *They are unevidenced in the file,
   which is a statement about the file.*

## TLDR

You asked me to understand all the grounding work. Here is the shape of it.

**185 grounding experiments are marked as wins. Seven of them carry the two basic statistical checks
that would justify calling them wins. Four of those are genuinely distinct full-size experiments.**

**The four are real and worth knowing.** The reading loop really does build up knowledge as it reads —
185 entries to 3,544 in one pass, with the scrambled control failing as it should. One shows the
mechanism scoring 1.0 where both its sanity-checks score 0.0, which is the cleanest control result in
the set. Another beats a proper baseline with a validity check attached. The fourth is the best-
evidenced number we have: a 6-point improvement on 4,000 items with an error bar that excludes zero and
four separate baselines beneath it — **though it is a 6-point improvement on a matching task, not a
capability.**

**One of the seven is a warning.** A quick reduced-size trial of one experiment passed; **the full-size
run of the same experiment came back hugging the floor.** Anyone counting the "win" labels — or citing
that experiment by name — gets the small trial's answer, not the real one.

**And the count itself is the lesson.** I tried twice yesterday to work out this number by writing my
own version of the checking tool, and got 198 and then 58, against a true 14. I have now rebuilt it so
it *calls* the official tool instead of imitating it, and it refuses to run if it stops agreeing with it.

## QUESTIONS

None — Q105 remains open and this work proceeds either way.

## NEXT STEPS

1. 🎯 **Read the METHOD of the four**, which is now feasible. *Carrying an interval is the cheapest
   hurdle; the real question is whether the gold is independent of the mechanism under test.*
2. **Check the other smoke/full pairs in the archive for the same pattern** *-- one instance of
   "smoke passes, full hugs the floor" justifies looking for more, and the evidence gate is blind to it
   by construction.*
3. *Method note: **the smoke twin appearing in the readable set is what exposed the scale failure.** I
   nearly filtered smoke runs out as noise before printing them.*
