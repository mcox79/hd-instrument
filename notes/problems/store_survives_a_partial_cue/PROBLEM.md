---
priority: 2
review: EXCELLENT
review_text: "Clean refutation with binding controls, and it reproduces the counting floor exactly. Its mechanistic line is the sharpest of the night: PMI already IS the calibrated familiarity read-out, so store format is not the lever. Third instrument showing an oracle clears and no unsupervised method reaches it."
---

> # 🥇 **MY REVIEW -- EXCELLENT. RE-VERIFIED, AND IT IS THE THIRD INSTRUMENT WITH THE SAME SIGNATURE.**
> *Reviewed 2026-08-23. Ran its reverify: ALL WITNESS CHECKS PASS.*
>
> ✅ **THE REFUTATION IS CLEAN AND THE CONTROLS BIND.** No calibrated-familiarity / recollection /
> dual-process arm clears the floor: best is `CONF_GATED 0.2461` against `F_COUNT1 0.3242`
> (`d=-0.0781`, CI excludes 0). *Info-free `0.0000`, scramble `0.0002`/`0.0000`, self-retrieval 2AFC
> `0.9767` -- the instrument works, so the failure is real.* ✅ **It REPRODUCES the counting floor
> `0.3242` EXACTLY from the refuted cell**, which is how you prove the instrument matches.
> ✅ **And it reports the recite/recognise gap in its own best arm:** `REC_EXPLICIT` recites
> `0.9122`, recognises `0.1619`.
>
> 🔑 **ITS SHARPEST LINE IS MECHANISTIC AND I WOULD NOT HAVE WRITTEN IT: *"PMI already IS the
> calibrated cortical-familiarity read-out, so store FORMAT is not the lever."*** *We were
> reimplementing, worse, the thing the counting floor already is.*
>
> ## 🎯 **THE CONVERGENCE -- THREE INDEPENDENT INSTRUMENTS, ONE SIGNATURE**
> **Every one has an ORACLE that clears, and NO unsupervised method reaches it:**
>
> | instrument | oracle | best unsupervised | gap |
> |---|---|---|---|
> | this cell (partial-cue identity) | `ORACLE_UNION` **`0.4082`** | `F_COUNT1` `0.3242`, our best store `0.2461` | **`+0.0840`** CI `[+0.0769,+0.0914]` |
> | write-rule ladder (`exp_writerule_step_ladder_v1`) | `BEST_SINGLE_ORACLE` **`0.3033`** | `SUM_ALL` `0.0100`, `RANDOM_SINGLE` `0.0367` | **`30x`** |
> | corpus ceiling (`exp_corpus_capacity_ppmi_svd_ceiling_v1`) | fitted, held-out **`0.9606`** | every transform `0.02`-`0.13` | the whole range |
>
> ➡️ **THE COMPLEMENTARY SIGNAL IS DEMONSTRABLY PRESENT AND WE CANNOT SELECT IT WITHOUT AN ORACLE.**
> *This cell says it exactly: "a real reserve of complementary episodic signal that no UNSUPERVISED
> combiner here reaches. The missing piece is a learned control that knows WHEN to recollect, not a
> better store."*
> 🚫 **SO THE ROUTE THAT IS CLOSED IS "BUILD A BETTER STORE / TRANSFORM", ON THREE INSTRUMENTS.**
> **The route that is OPEN is a CONTROL that decides which source to trust per item** -- which is
> the same organ the priority-1 brief now targets (reliability-weighted cue combination), arriving
> from a completely different direction. *Two briefs, one missing organ.*
> ⚠️ **AND THE HARD PART IS UNCHANGED AND IS WHY Q118 IS ON THE BOARD:** every oracle here is
> SUPERVISED. **A control learned from the same labels the oracle uses is the oracle wearing a
> disguise.** *Where the selection signal comes from without labels is the open question, not how to
> combine once you have it.*


> # 🥈 **PRIORITY 2 of 8 -- OPENED 2026-08-22 BECAUSE THE PREVIOUS STORE BRIEF ASKED THE WRONG QUESTION.**
> **`flat_store_destroys_the_code` asked a solver to WIRE IN the addressed store we already had. They
> did, and it was REFUTED: held-out `0.1399` against a counting floor of `0.3242`.** *That brief
> assumed the fix existed and only needed connecting. It did not.*
> ➡️ **THIS BRIEF ASKS THE QUESTION THAT ONE SHOULD HAVE: DESIGN A STORE WHOSE READ-OUT SURVIVES A
> PARTIAL CUE.** *Owner, 2026-08-22: "If we needed to develop a new optimized store, that should have
> been the ask from the problem."*

# PROBLEM: OUR STORE CAN RECITE BUT IT CANNOT RECOGNISE

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**
> *Reason, so you do not self-negotiate it: a dropped precondition invalidates the declared gate even
> when the result may be fine. "The number probably didn't change" is not yours to decide silently.
> Disclose; the operator decides.*

---

## THE PROBLEM IN PLAIN LANGUAGE

Ask our memory a question using **the exact words it stored**, and it answers almost perfectly:
`0.9954`. Ask the same question using **some** of those words -- which is all real reading ever
gives you -- and it collapses to `0.1399`.

**It can recite. It cannot recognise.**

That gap is not a tuning problem and it is not one implementation's bug. **Two completely unrelated
mechanisms have now hit the same cliff**, which is what makes this a problem about the STORE rather
than about either of them.

**The job: design and build a store whose read-out survives a partial cue, and beat plain
word-counting on held-out text.**

## WHY THIS ONE

**Because everything we build upstream pours into this.** Better meaning supply, better coverage,
better persistence -- all of it is written into a store that loses the thread the moment the cue is
incomplete. *A better input to a store that cannot be queried is not an improvement anyone can
measure.*

**And because the previous brief mis-asked it.** `flat_store_destroys_the_code` said: the reading
loop mixes everything into one bucket, we already have a labelled store, connect it. **The solver
connected it and it lost to counting by `-0.1843`.** The premise -- that the fix was built and
merely unwired -- was wrong. **The fix has to be designed.**

## MEASURED vs INFERRED

**MEASURED** -- all from `data/exp_flat_vs_addressed_identity_recovery_livepath_v1/metrics.json`,
open-vocabulary identity recovery on the live reading path, n=5,490 candidate lemmas, 92,908
episodes, held-out 80/20 split:

| arm | exact key | **held-out** |
|---|---|---|
| **ADDRESSED** (exemplar, every encounter labelled) | **`0.9954`** | 🔻 **`0.1399`** `[0.1310, 0.1494]` |
| FLAT sum (the incumbent) | `0.3707` | `0.0845` `[0.0774, 0.0918]` |
| 🚩 **F_COUNT1 -- first-order co-occurrence counting, THE FLOOR** | | **`0.3242`** `[0.3115, 0.3366]` |
| F_COUNT2 -- second-order counting | `0.0084` | `0.0046` |
| chance | | `0.00018` |

- **addressed - floor = `-0.1843`, CI `[-0.1978, -0.1701]`, excludes zero.** We lose to counting.
- **addressed - flat = `+0.0554`, CI-separated.** *So the flat sum IS lossy and addressing DOES
  recover some of it -- the recovery just does not reach the floor.*
- Controls all clean: info-free addressed `0.0000` held-out (must-lose, satisfied), scramble
  `0.0000` both arms, 2AFC self-retrieval positive control `0.7433` (the instrument works), tie
  density `0.87%`.

🧠 **THE STRUCTURAL FACT, AND IT IS THE ONE TO DESIGN AGAINST:** the archive independently records a
circular WordNet oracle reading **`0.8787` at exact key and `0.0365` under a partial cue**. **Two
unrelated mechanisms, the same collapse.** *Whatever this is, it is a property of how the cue meets
the store, not of either implementation.*

**INFERRED, NOT MEASURED:**

- 🔻 **That a store CAN be built which survives the partial cue.** Nobody has shown one here.
  **A rigorous negative -- "this is an information-theoretic cap, here is the argument" -- is a
  first-class outcome and would be worth as much as a win.**
- 🔻 **That the answer is a sparse code.** The refutation's own conclusion points at code FORMAT, and
  the archive has a sparse-code result, **but a 1%-sparse arm previously produced an ARTIFACT here**
  (~91% of pairs sharing no support, every tie counted as beaten). *If you go sparse, the tie-density
  guard is not optional -- see DO NOT QUOTE.*

## ALREADY TRIED -- DO NOT RE-RUN THESE

- **Exemplar / addressed storage on the live path: REFUTED 2026-08-22** (the table above).
  `experiments/exp_flat_vs_addressed_identity_recovery_livepath_v1.py`. **Do not re-wire it and
  re-measure; that experiment is done and its data is on disk.**
- **CA3 pattern completion: DO NOT BUILD.** Real within-lemma overlap is `0.0056` against a `0.22`
  failure threshold -- *the regime the completer fixes never occurs in our data.*
- **Divisive normalisation over a population pool: analytically closed.** The denominator is a scalar
  and cosine is scalar-invariant; it cannot move a cosine ranking.
- **Rank-1 / anisotropy removal: closed HARD.** The operation fully worked (`0.1427 -> -0.0004`) for
  `+0.0005` accuracy, and a RANDOM rank-1 direction gives the same `+0.0005`.
- **Blending a form code into the query: `HARD_FAIL`** -- composition hurt relative to the best
  single spoke.

## VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

1. `python tools/before_you_start.py "design a store that survives a partial cue"` -- and **read
   every row it returns**, not the first. This project's most expensive recurring error is
   re-deriving a result already on disk.
2. `python tools/slot_status.py` -- **check whether the organ you are about to improve is even
   connected.** `NEEDS_ADAPTER` means built and not on the live path.
3. **Re-run the refuted experiment's `reverify` line once** so you are measuring against numbers you
   have seen reproduce, not numbers you read here.
4. `python tools/organ_map_cite.py <ORGAN>` for anything you plan to reuse -- **it prints the
   "do not re-propose" lines FIRST**, and this project has twice rebuilt something the map had
   already ruled out.

## THE BAR

**BEAT `F_COUNT1 = 0.3242` ON HELD-OUT TEXT, CI-SEPARATED, ON THE LIVE READING PATH.**

- **The floor is the STRONGEST one actually run, gated on its UPPER bound (`0.3366`).** *Beating the
  flat sum is not the bar -- addressed already did that and is still refuted.*
- 🚨 **REPORT EXACT-KEY AND HELD-OUT SIDE BY SIDE, ALWAYS.** An exact-key number alone is the exact
  shape that produced the last refutation. **If your exact-key score is high and your held-out score
  is not, you have reproduced the problem, not solved it -- and saying so plainly is a result.**
- **The information-free twin must LOSE**: same architecture, same episode count, same grouping,
  contents randomised. *The previous solver's read `0.0000`; yours should too.*
- **Report tie density and both tie conventions.** A sparse code can score well purely because ties
  break toward the target.
- **State what it costs.** 92,908 episodes for 5,490 lemmas is already a large store; a design that
  wins by keeping more must say how much more.

**A RIGOROUS NEGATIVE IS A PASS.** If you can show the partial-cue collapse is forced -- by
information theory, by the geometry, by a cheating-oracle bound -- **that closes a direction the
project has now hit twice, and it is worth more than another arm that also loses.**

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| **the refuted experiment + its data** | `experiments/exp_flat_vs_addressed_identity_recovery_livepath_v1.py`, `data/exp_flat_vs_addressed_identity_recovery_livepath_v1/` |
| its design note | `notes/problems/flat_store_destroys_the_code/DESIGN.md` |
| the brief it refuted, with my review | `notes/problems/flat_store_destroys_the_code/` |
| the incumbent flat sum | `hdlab/reading_grounding_loop.py` -- the `_sums[lemma] += ctx_vec` accumulation |
| the live read path | `hdlab/substrate.py` `read()` |
| tie-convention guard (MANDATORY if you go sparse) | `tools/rank_with_ties.py` |
| cross-seed guard | `tools/replication_gate.py` |

## DO NOT QUOTE

- 🚫 **`0.9954` as a capability.** It is exact-key recall -- the store handed back what it was
  handed. **It is the symptom, not an achievement.**
- 🚫 **`+0.0554` (addressed over flat) as a win.** It is CI-separated and real, and it is `-0.1843`
  BELOW the floor. *Beating the incumbent while losing to counting is not progress.*
- 🚫 **A sparse-code result without tie density.** A 1%-sparse arm here previously read `1.06x` the
  floor -- apparent parity with counting -- while **random noise of the same sparsity scored
  BETTER**, because ~91% of pairs shared no support and every tie counted as beaten.
- 🚫 **"the flat sum is fine".** It is not: addressed beats it CI-separated. The flat sum is lossy AND
  the known repair does not reach the floor. **Both are true.**
