# PROBLEM: THE WAY WE STORE THINGS DESTROYS ALMOST ALL OF WHAT WE STORE

**slug:** `flat_store_destroys_the_code` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · **highest value after the reader, and far more bounded**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

When the system reads, it adds each word's pattern into one running total per concept.

**The analogy the owner used, and it is exact: mixing paint.** Pour red, blue and yellow into one
bucket and you get brown. You cannot later ask the bucket which part was the red. The information
is not hidden in there -- it is gone.

**There is a second store in this codebase that keeps a label on every item and can pull it back
out cleanly. Nothing calls it.** It has been built, proven, and left disconnected -- three separate
times, by three separate efforts.

**The job: stop adding into one bucket. Use the store that keeps addresses, and show that the win
survives on the real reading task rather than only in isolation.**

---

## 2. WHY THIS ONE

- **It is the clearest case of this project's defining pattern:** the solution exists, is proven,
  and is not connected. *That is a wiring problem, which is far more tractable than a research
  problem.*
- **It has decisive isolation evidence already** -- effect sizes of the kind that need no
  confidence interval to believe.
- **It explains why downstream repairs measure null.** No amount of re-scoring recovers information
  the storage step already discarded.

---

## 3. MEASURED vs INFERRED

### MEASURED -- with the caveat that these are ISOLATION proofs, not capability wins

| comparison | result |
|---|---|
| structured storage vs flat bundle | **`1.000` vs `0.003`** |
| combination-coding vs adding | **`1.000` vs `0.273`** |
| binding vs flat, on the collision case | **`1.0` vs `0.06`** |

> ### ⚠️ **THE CAVEAT THAT MUST TRAVEL WITH ALL THREE: these are ISOLATION proofs. This project's own rule is CONSTRUCTION-PROOF != CAPABILITY-WIN.** Wiring is necessary; the win still has to survive on the real reading task, and that is the actual job here.

**Independently, on the live path:**
- **Our "semantic profile" is a SUM of context bags, and it is beaten by literally counting the
  same co-occurrences** -- reached on four separate instruments, which is why it is trusted.
- **Interference, not key quality, is the binding constraint.** Crosstalk over raw keys dominates
  Hebbian capacity (`r 0.976`, n=11), and **our keys already sit AT the Welch bound -- so "use
  better keys" is closed BY GEOMETRY.** The two remaining levers are **fewer items** and **more
  dimensions**.
- **The episodic store was wired as a WRITE-ONLY SINK**: 3,400 encounters written, nothing read
  them, because `hippocampal_encoder.retrieve` existed and was never called. *That specific defect
  may since be fixed -- CHECK, do not assume.*

**The brain side:** the brain never dumps everything into one pile. It is hub-and-spoke -- each
sense keeps its own copy with its own handle and a hub links them. It is **sparse**, so memories do
not smear. And it stores **combinations as units** ("furry AND barks"), not a loose bag of separate
features. **Perirhinal cortex exists more or less specifically to tell apart two things that share
features -- which is precisely the failure mode here.**

### INFERRED -- and one of these is UNVERIFIED, treat it accordingly

- 🔻 **"Adding vectors destroys `6.93` of `7` bits of the real concept codes, while squashing them
  to signs destroys ZERO; permuting the codes does not help, so it is the GEOMETRY of the codes and
  not their content."**
  **⚠️ THE STRATEGY SESSION HAS NOT VERIFIED THIS ON DISK.** It comes from a report relayed by the
  owner from another session. **It is the single most quotable number in this brief and it is the
  one you should check FIRST.** *If it does not reproduce, say so -- that is a result, and it would
  materially change this brief.*
- *That wiring the bound store improves the live reading task.* **Untested.** The isolation wins do
  not transfer automatically; this project has been burned by exactly that inference.
- *That "fewer items and more dimensions" is the right lever pair.* Follows from the Welch-bound
  argument, which is sound, but has not been driven to a task win.

---

## 3b. 🔑 THE PLAN ALREADY DECIDED THE ORDERING, AND ALREADY FOUND THE BRIDGE BETWEEN THIS AND THE READER

**`notes/LONG_TERM_PLAN.md` PHASE 3 IS THIS PROBLEM, AND IT IS "BLOCKED UNTIL PHASE 1 CLEARS."**
*Its gate is worded to catch precisely the trap in section 3: "addressed beats flat CI-separated on
the REAL reading task, not in isolation. An isolation win is a construction proof; this project has
repeatedly mistaken one for a capability."* **That ordering is a decision, not my inference -- do
not re-argue it, and read Phase 1 before starting here.**

> ### 🎯 **AND PHASE 1 ALREADY FOUND THE THING THAT JOINS THE TWO PROBLEMS, WHICH IS THE MOST USEFUL POINTER IN THIS BRIEF.**
> `C1_KCAP_GRD_f005_BOOST@d1024` -- **a SPARSE, GRADED population code** -- carries meaning at
> **`0.2801`, CI-separated above all three floors**, *and* retains **`3.5264` of 7 bits through
> bundling: `4.0x` the incumbent and `7x` the pre-registered `0.5`-bit criterion.**
> **"Meaning that survives superposition is the combination this programme needs and had never
> achieved."**
>
> **The contrast makes the trade-off concrete:** `C4_PHASOR` wins on meaning outright (`0.3345`) and
> **dies in bundling at `0.0097` bits.** *Meaning you cannot superpose is meaning you cannot store.*
>
> ⚠️ **HONEST CAVEAT, FROM THE PLAN ITSELF: the CELL fails the standing bar (`verdict_bar_check` ->
> `FAILS_BAR`; G0/G4 failed on a degenerate denominator, not on the candidates). THE ARM IS
> PROMISING; THE CELL IS NOT A PASS.** *Do not cite `0.2801` as a landed result.*
>
> ➡️ **SPARSITY IS NAMED AS THE LIVE PHASE 1 LEVER AND AS THE LARGEST FIDELITY GAP WE HAVE -- THE
> BRAIN IS SPARSE AND WE ARE DENSE.** *But see the closed route in section 4: sparsifying the STORED
> KEY under a partial cue is dead. Sparsity in the CODE and sparsity in the KEY are different
> interventions and this project has already confused them once.*

## 4. ALREADY TRIED -- AND THE SHAPE OF THE FAILURE

- **The mechanism has been solved THREE TIMES and islanded THREE TIMES.** The pattern is not that
  it does not work; it is that it never gets connected. **Read the three cells before building
  anything -- you may be able to wire rather than rebuild.**
- **`hd_fact_store` has a native `(subject, relation)` bound key**, and its exact `O(1)` index is
  **switched off on the live path** while the reading loop uses the flat bundle instead. *Find out
  WHY it is off before turning it on -- there may be a reason, and if there is not, that is your
  answer.*
- **Sparsifying the stored key under a partial cue: CLOSED** (`DO NOT REDO 44`) --
  `-0.0145 [-0.0203,-0.0088]` BELOW the flat store, with an oracle at `1.0000`. **A sparse arm also
  breaks rank metrics** (~91% of pairs tie at exactly 0.0 and every tie counts as beaten), so if you
  sparsify, **assert tie density and report both tie conventions** via `tools/rank_with_ties.py`.
- **Rank-1 common-mode removal: CLOSED HARD** (`DO NOT REDO 27`).

---

## 5. VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

```bash
python tools/before_you_start.py "wire the bound fact store into the reading loop instead of the flat sum"
python tools/experiment_index.py query "structured"
python tools/experiment_index.py query "binding"
python tools/experiment_index.py query "flat bundle"
python tools/organ_map_cite.py hd_fact_store
python tools/symbol_corrections.py retrieve
```
**And verify the `6.93 of 7 bits` claim yourself before leaning on it.**

---

## 6. THE BAR

**A read-out on the LIVE reading path that uses addressed storage instead of the flat sum, and
beats the strongest floor CI-separated on HELD-OUT text.**

- **The floor to beat is a counting baseline, and it must be the strongest form actually run** --
  not the weakest convenient one. This project has already refuted three of its own cells for
  choosing a weak floor, and did it again on 2026-08-19.
- **Gate on the floor's UPPER bound** (floor + its own half-width).
- **Controls, none optional:** a scramble twin that destroys the cue's CONTENT (not its word order
  -- a word-order shuffle against a bag scorer is a no-op that ties the real cue at `p = 1.0000`);
  an **information-free version of your own arm** which must LOSE; and **report how many items each
  control removed.**
- **An ablation:** turn the addressed store off, re-run, report the delta. *If nothing moves, the
  floor is what is scoring and the organ is decoration -- report it that way.*

### HOW WE WOULD KNOW IT FAILED
- **(a)** No margin over the floor's upper bound -> a real negative; go to the brain-fidelity drill.
- **(b)** A margin, but the ablation moves nothing -> the store is not what is scoring.
- **(c)** A margin only at exact-key and not held-out -> **that is the ALREADY-KNOWN result**
  (`0.9333` exact vs `0.0044` held-out) and is not progress. *The held-out column is the one that
  counts.*
- **(d)** The isolation win does not reproduce once wired -> the most informative outcome in this
  brief, and worth writing up carefully.

---

## 7. FILES AND ENTRY POINTS

- **The flat sum:** the accumulation line in the reading loop -- `hdlab/reading_grounding_loop.py`.
  *Read it before matching it: an arm that normalises where the substrate accumulates RAW vectors
  (mean norm ~44.5) is 1/44th of a real write and will produce a clean-looking null.*
- **The store that keeps addresses:** `hdlab/hd_fact_store.py` (bound key, exact index)
- **The episodic path:** `hdlab/hippocampal_encoder.py` (`retrieve`)
- **The assembled substrate:** `hdlab/substrate.py`
- **🚫 DO NOT TOUCH:** `preregs/**`, `arm_key*`, `notes/STATUS.md`, the build plan, other problem
  folders. **`data/foundation/` is READ-ONLY -- one disk, no backup.**

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **Never quote `1.000` / `1.0` from the isolation table as a capability.** They are
  construction proofs.
- 🚫 **Never quote an exact-key score as a capability** -- at exact key the cue IS the vector the
  episode was written from. It is a ceiling diagnostic that proves the instrument works.
- 🚫 **Do not re-propose sparsifying the stored key, or rank-1 common-mode removal.** Both closed.
- ⚠️ **Do not carry `6.93 of 7 bits` into a write-up until you have reproduced it.** It is currently
  an unverified relay, flagged as such above.
