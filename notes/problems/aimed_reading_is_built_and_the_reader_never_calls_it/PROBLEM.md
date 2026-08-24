---
priority: 2
review:
review_text:
---

> # 🥈 **PRIORITY 2 — THE ORGAN IS BUILT, PINNED, WITNESSED, REGISTERED WIRED, AND THE LIVE READER DOES NOT CALL IT.**
> **This is not a build.** `hdlab/information_foraging.py` exists (38,533 bytes), its rule is pinned
> to Charnov's marginal-value theorem, and its can-fail cell HARD_PASSed a 10,000-sentence read.
> **What reads is still a hard-coded list of four sources.** *And the one run that tested it says
> something its own verdict does not: the OLD FIXED SCHEDULE BEATS IT on the headline measure.*

# PROBLEM: THE SYSTEM CANNOT CHOOSE WHAT TO READ NEXT — AND THE PART THAT COULD IS BUILT AND UNPLUGGED

**slug:** `aimed_reading_is_built_and_the_reader_never_calls_it` · **opened:** 2026-08-24 by the
strategy session · **status:** OPEN

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

A reader that cannot choose what to read next can only learn what happens to be in front of it. Ours
notices words it does not know — but only among words already on the page.

**The consequence is measured, not feared: `64.5%` of every definitional fact this substrate has ever
produced came from ONE source segment** (1,118 of 1,734 distinct terms). We own 36 corpora. The live
loop reads from a hard-coded list of **four**.

The organ that would fix this **already exists and is not called.** Someone built it, pinned its rule
to the foraging equation animals actually use, wrote it a witness, registered it — and the reading
loop never asks it anything.

---

## 2. WHY THIS ONE

- **IT BLOCKS ALL SELF-DIRECTED GROWTH.** Every other stage is limited by what got read; this decides
  what gets read.
- 🔑 **IT IS THE CHEAPEST REAL MOVE ON THE BOARD.** The build is done. What is missing is a call site
  and an honest re-measurement.
- ⚠️ **AND THE EXISTING RESULT IS WEAKER THAN ITS VERDICT SUGGESTS (§3). Reading that carefully is
  half the job.**

---

## 3. MEASURED vs INFERRED

### MEASURED — you may build on these

| what | number | where |
|---|---|---|
| the organ EXISTS, witnessed, registered `WIRED` | 38,533 bytes + `test_information_foraging_organ_witness.py` | `hdlab/information_foraging.py` |
| **its brain rule is PINNED** | leave when `g'(t) < rho`, travel time in rho's denominator | Charnov 1976 *Theor Popul Biol* 9:129-136; Constantino & Daw 2015 *CABN* 15:837-853 Table 2 |
| the cell RAN, full mode | 10,000 sentences, `HARD_PASS` | `data/exp_information_foraging_reading_v1/metrics.json` |
| aimed reading beats RANDOM | held-out coverage **`0.0617` vs `0.0127`** (3.87x) | same, check D2 |
| 🔻 **but the FROZEN schedule beats aimed reading** | **`0.0743` vs `0.0617`** on that same measure | same, check D2's own `frozen` field |
| 🔻 **and RANDOM beats it on dictionary agreement** | `0.386` vs `0.351` | same, check D3 |
| it did diversify sources | FORAGE read 19 corpora / banked from 16; FROZEN read 4 | same |
| **the live loop does not call it** | a hard-coded 4-entry corpus dict | `exp_reading_grounding_loop_cycle2_v1.py:132-137` |
| the imbalance it should fix | **`64.5%` of all definitional facts from one segment** (1,118/1,734) | ORGAN_MAP H2 BLOCKS |

### INFERRED — overturning any of this is a RESULT

- 🔻 **That the FROZEN loss is real rather than an artifact.** The one run carries a documented
  **`7.6x` register bias** in which kind of text the probe words came from (88.2% vs 11.6%
  news/conversational) — **under a 1.2x effect**. *The bias is large enough to produce the ordering
  by itself, in either direction. Nobody has separated them.*
- 🔻 That a call site is enough. **Aiming during reading may behave differently from aiming in a
  batch experiment**, and nothing has measured the live path.
- 🔻 That more source diversity is the goal. *Reading 19 corpora instead of 4 is a MEANS. It is only
  progress if the substrate ends up knowing more, and on one measure it ended up knowing less.*

---

## 4. ALREADY TRIED — DO NOT REDO

- ✅ **THE ORGAN IS BUILT. Do not rebuild it.** `hdlab/information_foraging.py`, witnessed,
  registered `information_foraging_mvt_leave_rule`, `gate_decision WIRE`.
- ✅ **The can-fail cell has run with BOTH floors the plan asked for** (RANDOM and FROZEN) at 10,000
  sentences. *Re-running it unchanged adds nothing.*
- 🔻 **`exp_gap_driven_reader_controlled_v1` HARD_PASSed on `n=8` SYNTHETIC f-string pseudoword
  templates.** *A pass on synthetic templates is not a floor for corpus selection.* **Do not cite it
  as evidence the organ works on text.**
- 🔻 **`hdlab/gap_driven_reader.py::rank_material` is "intentionally target-agnostic"** by its own
  docstring — it ranks only what the caller hands it, so it cannot choose a source.
- ⚠️ **ORGAN_MAP's H2 entry is SUPERSEDED and says so; read §10.1/H2b instead.** Its `BRAIN'S MATH`
  field contradicts itself (`UNPINNED ... WRONG, the operation IS pinned`). Run
  `python tools/substrate_map.py --organ H2` and read the constraint lines it prints FIRST.

---

## 5. THE BAR

**AIMED READING MUST BEAT THE FIXED SCHEDULE, NOT ONLY RANDOM — ON THE LIVE PATH, WITH THE REGISTER
BIAS CONTROLLED.**

1. **A live call site**: the reading loop asks the organ what to read next, rather than an experiment
   harness doing it. *State plainly whether the loop calls it, and show the call.*
2. **Beat `FROZEN`, CI-separated**, on held-out coverage. **The existing run LOSES this comparison
   (`0.0617` vs `0.0743`) and its gate never required winning it.** *That is the bar this brief
   exists to set.*
3. **CONTROL THE REGISTER BIAS.** The probe must not be drawn disproportionately from the register
   one arm happens to read. **Report the register composition of the probe per arm** — a 7.6x
   imbalance under a 1.2x effect decides the result by itself.
4. 🔑 **SAVE THE SCORED POPULATION.** The previous run did not, which is why its bias cannot be
   corrected without ~70 minutes per arm of re-running. One line beside the score.
5. **An information-free twin must LOSE**: a chooser that picks sources at random with the same
   switching rate. *Diversity for its own sake is not the capability.*

**A CLEAN NEGATIVE IS A FULL RESULT.** If aimed reading genuinely cannot beat a fixed curriculum on
this corpus set, that is worth knowing and would redirect real effort — **and it is the outcome the
current numbers point at.** ⚠️ **But do not stop at "refuted": if the marginal-value rule loses,
the underlying problem is unchanged — *the reader cannot choose, and 64.5% of what it knows comes
from one place.* Solve that some other way and say which routes you tried.**

---

## 6. HOW THE BRAIN DOES THIS — PINNED, AND UNUSUALLY SO

**PINNED BY EVIDENCE, and this is one of the better-pinned organs on our map.** Charnov's marginal
value theorem: leave the current patch when its instantaneous yield drops below the environment's
average rate, `g'(t) < rho`, with travel time in the denominator of `rho`. Animals do this; it is
measured, not modelled. Constantino & Daw 2015 give the discrete form.

**OUR INVENTION, LABEL IT AS SUCH:** what counts as a "patch", what "yield" means for a reader, and
how travel cost is estimated are all ours. **Say which proxy you used.** *The equation is pinned; the
mapping onto reading is not.*

---

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the organ | `hdlab/information_foraging.py` (READ-ONLY: do not write `hdlab/`) |
| its witness | `verification/test_information_foraging_organ_witness.py` |
| the run that HARD_PASSed | `data/exp_information_foraging_reading_v1/metrics.json` (checks D1-D4) |
| **the hard-coded corpus list that actually reads** | `experiments/exp_reading_grounding_loop_cycle2_v1.py:132-137` |
| the target-agnostic ranker | `hdlab/gap_driven_reader.py::rank_material` |
| the corrected organ entry | `python tools/substrate_map.py --organ H2` |
| the stage this shores up | `python tools/substrate_map.py --brief aimed_reading_is_built_and_the_reader_never_calls_it` |

**WRITE:** `experiments/`, `verification/`, this folder. **NOT** `hdlab/`, **NOT** `preregs/**`,
**NOT** any `arm_key*`. `data/foundation/` is READ-ONLY.

---

## 8. DO NOT QUOTE

- 🚫 **`HARD_PASS` as "aimed reading works".** It cleared the bands it declared; those bands never
  required beating the fixed schedule, and on the headline measure it loses to it.
- 🚫 **`0.0617` without `0.0743` beside it.** Quoting the win over random while omitting the loss to
  frozen is the exact shape this brief exists to correct.
- 🚫 **`exp_gap_driven_reader_controlled_v1`'s pass as evidence about text.** `n=8`, synthetic
  templates, never saw real prose.
- 🚫 **ORGAN_MAP H2's `BRAIN'S MATH: UNPINNED`.** Corrected in the same file: the operation IS
  pinned.
- 🚫 **`64.5%` as a current measurement.** It is the share across everything ever produced, not a
  reading of today's store.

---

## 9. VERIFY BEFORE YOU START — THE DISK OUTRANKS THIS BRIEF

1. `python tools/before_you_start.py "choose which corpus to read next"` — read **every** row.
2. `python tools/experiment_index.py query "foraging"` — read them all.
3. `python tools/substrate_map.py --organ H2` — **constraint lines print first, and there are three.**
4. `python tools/slot_status.py forag` — whether the organ is on the live path at all.
