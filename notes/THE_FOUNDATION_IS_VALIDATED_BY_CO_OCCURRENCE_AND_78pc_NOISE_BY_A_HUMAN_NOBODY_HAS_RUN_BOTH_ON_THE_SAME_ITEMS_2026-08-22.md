# **THE SAME FOUNDATION IS "VALIDATED" BY A CO-OCCURRENCE CRITERION (gap `0.2533`, n=150) AND `78%` NOISE BY A BLIND HUMAN (n=100). NOBODY HAS RUN THE TWO CRITERIA ON THE SAME ITEMS.**

**Third of the four evidenced grounding cells read. It passes honestly, on a criterion that a human
scorer contradicts -- and the contradiction has never been tested directly because the two were run on
different samples.**

---

## 1. WHAT `exp_foundation_validation_harness_v1` ACTUALLY TESTS

| claim | design | result |
|---|---|---|
| **1. CORRECTNESS** | sampled facts checked against **co-occurrence in a HELD-OUT modern corpus**, vs a **decoy-object** baseline | ✅ **gap `0.2533`** (band `>=0.20`), n=`150` |
| **2. COHERENCE** | same-idea/same-rep cohesion + the store's own contradiction invariant | ✅ cohesion gap `0.4765`, **0 contradictions** |
| **3. CAN-REASON** | 2-hop `A->B->C` chains answered by chaining two real `HDFactStore.query()` calls | ✅ `mech 1.0`, `scr 0.0`, `abl 0.0`, n=`150` |

✅ **Claim 1's gold is genuinely INDEPENDENT of the mechanism** -- co-occurrence in a held-out corpus is
not the substrate grading itself, and a decoy baseline is a real comparison. *That is the good part and
it is the reason this cell is in the evidenced set.*

## 2. 🔻 **CLAIM 3'S CONTROLS ARE LARGELY TRUE BY CONSTRUCTION**

***The cell's own words: the ablation "must collapse to near-0 since B != C by chain construction".***
**A control that is guaranteed by arithmetic is not evidence.** *And chaining two exact queries across
facts `A->B`, `B->C` that are both IN the store returns `C` with near-certainty -- so `mech = 1.0` is
close to definitional too.*

> ### **`1.0 / 0.0 / 0.0` IS A CONSTRUCTION PROOF: THE STORE CAN CHAIN TWO RETRIEVALS AND THAT DEPENDS ON THE STORED RELATIONS. IT IS NOT A REASONING CAPABILITY.** *The standing rule already says it: CONSTRUCTION-PROOF != CAPABILITY-WIN.*

*The scramble arm is the one informative control of the three, and it too collapses to exactly 0.0.*

## 3. 🚨 **THE COLLISION, WHICH IS THE POINT OF THIS NOTE**

| criterion | population | verdict |
|---|---|---|
| **co-occurrence vs a decoy** (`harness_v1`) | 150 sampled facts | ✅ **gap `0.2533` -- FOUNDATION VALIDATED** |
| **blind human MEANINGFUL/RELATED/NOISE** (`grounding_quality_readout`) | 100 blind rows | 🔻 **`3` MEANINGFUL / `19` RELATED / `78` NOISE** |

**Co-occurrence measures TOPICAL ASSOCIATION. Human judgement measures MEANING. This project's
documented failure mode is exactly the gap between them** -- *the recorded hand-score failures are
topical neighbours: `whisky->wedding`, `banana->people`, `checklist->joe`.* **A fact can co-occur far
above a decoy and still be noise to a reader**, which is precisely what `78%` says.

> # ⚠️ **BUT THEY WERE RUN ON DIFFERENT SAMPLES OF DIFFERENT SNAPSHOTS, SO THIS IS A FLAGGED DISCREPANCY, NOT A DEMONSTRATED CONTRADICTION.** *`harness_v1` ran on `reading_grounding_v1_full_20260812`; the hand-score came from a different cell's blind rows. **No number crosses populations** -- that rule applies to my own synthesis too.*

## 4. THE MEASUREMENT THAT WOULD SETTLE IT, AND IT IS CHEAP

**Score ONE sample of facts BOTH ways.** *Take the 100 blind hand-scored rows, run the co-occurrence
criterion over exactly those, and cross-tabulate.* Three possible outcomes, all informative:

1. **Co-occurrence passes the rows humans called NOISE** -> the automatic criterion is not measuring
   meaning, and "foundation validated" needs re-wording everywhere it appears.
2. **Co-occurrence fails them too** -> the criteria agree and the `0.2533` sample was simply luckier.
3. **They separate** -> co-occurrence is a usable cheap proxy, which would be genuinely valuable.

## 5. LIMITS

1. **n=150 for claims 1 and 3; n=100 for the hand-score.** *All small.*
2. **I have not verified the two samples are disjoint OR overlapping** -- only that nothing states they
   are the same.
3. **A stale scope line**: the cell's docstring says *"SELF-TEST + SMOKE ONLY, NO FULL dispatch"*, while
   the landed metrics read `run_mode: full` against a frozen snapshot. *The doc describes the dispatch
   at authoring time; the run is real. Worth knowing before quoting the docstring.*

## TLDR

The system builds up a store of facts by reading. Two different checks have been run on that store, and
they disagree completely.

**The automatic check says it is good.** It takes a fact the system learned and asks whether those words
actually appear together in a large body of real text, compared against a deliberately wrong decoy
answer. The real facts win by a comfortable margin, and that check is honest — the yardstick comes from
outside, not from the system marking its own homework.

**A human reading the facts says 78% of them are noise.**

**Both can be true, and that is the interesting part.** Words appearing near each other is not the same
as one meaning the other — this project has already collected the examples: whisky/wedding,
banana/people. **A fact can pass "these words go together" easily and still be meaningless.**

**Nobody has run both checks on the same facts**, so this is a strong suspicion rather than a proven
contradiction, and I am not going to state it as more than that. **The experiment that would settle it
is small**: take the same 100 facts a person already judged and run the automatic check over exactly
those.

**One thing to flag about the reasoning claim in that same experiment:** it scores a perfect 1.0 with
both its controls at exactly 0.0, which looks impressive but is close to guaranteed by how the test is
built — the experiment itself says one control "must collapse to near-0 by chain construction". It shows
the machinery can follow a two-step link it already stored. **That is a plumbing check, not thinking.**

## QUESTIONS

None — Q105 still open, independent of this.

## NEXT STEPS

1. 🎯 **Run the co-occurrence criterion over the 100 blind hand-scored rows and cross-tabulate.** *The
   cheapest experiment on the board and it tests our main automatic quality proxy against a human.*
2. **One evidenced grounding cell left unread** (`foundation_validation_harness_v4_proximity_v1`, same
   family).
3. *Method note: **"validated" and "78% noise" sat in the archive side by side for ten days without
   colliding, because they use different words for quality.** Reading the METHOD is what put them in the
   same sentence.*
