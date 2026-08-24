---
priority:
review: STRONG
review_text: "Its central finding is real and retires a floor that was steering the whole thread -- the string control that beat us 2:1 is 78% morphology and collapses into its own info-free twin on clean gold. But its headline 'bundling is not the bottleneck' is contradicted by its own paired bootstrap: removing the bundle BEATS the flat bag +0.0125 CI[+0.0057,+0.0195], CI-separated."
---

> # 🥈 **MY REVIEW OF THE SUBMISSION -- STRONG. THE DISCOVERY IS REAL; THE HEADLINE OVERSHOOTS IT.**
> *Reviewed 2026-08-23 by the strategy session. Re-verify PASSED (~13 min). Everything below is
> recomputed from `data/exp_c3_surprise_weighted_vs_bundling_v1/metrics.json` (`run_mode: full`,
> `4,000` items, `5,491` anchors). Witness:
> `verification/test_removing_the_bundle_helps_it_just_does_not_help_enough.py`.*
>
> ## ✅ **THE REAL FINDING, AND IT RETIRES A FLOOR THAT HAS BEEN STEERING THIS THREAD**
> **The string control that beats us ~2:1 is MOSTLY MORPHOLOGY.** Strip stem-sharing pairs out of
> the WordNet gold and it collapses **`0.0867` -> `0.0193`** -- *`78%` of it was spelling overlap
> between morphologically related words* -- and at `0.0193 [0.0153,0.0238]` it **OVERLAPS its own
> info-free shuffled twin** (`0.0173 [0.0135,0.0213]`). **On leakage-free gold the string floor is
> statistically indistinguishable from noise, and the distributional arms beat it CI-separated.**
> 🔑 *This is the single most useful thing to come out of the three submissions: `A5_STRINGCTRL`
> `0.0870` has been quoted all week as the bar any arm must clear. **Most of that bar was an
> artifact of how the gold was built.***
> ✅ *Also excellent: a cosine-invariance guard proving a SHARED permutation is not a null, and a
> per-row shuffle that genuinely destroys structure. It caught a control that would have been fake.*
>
> ## 🔻 **WHAT ITS OWN PAIRED BOOTSTRAP SAYS AGAINST ITS HEADLINE**
> **The headline is "the bundling is NOT the c3 bottleneck." The same `metrics.json` contains:**
>
> | paired delta, full gold, 5000x bootstrap | value | |
> |---|---|---|
> | **`RAW_COOC` − `A1_BASE`** *(delete the bundle entirely vs the shipped flat bag)* | **`+0.0125` CI `[+0.0057,+0.0195]`** | ✅ **EXCLUDES ZERO** |
>
> ➡️ **DELETING SUPERPOSITION IS WORTH `+0.0125` -- about `26%` OF THE FLAT BAG'S OWN SCORE
> (`0.0480`) -- AND IT IS CI-SEPARATED.**
>
> **HOW BOTH ARE TRUE, AND WHY THE FRAMING STILL MATTERS.** The submission's argument is: removing
> the bundle *still loses to the spelling floor*, therefore bundling is not what limits c3. **The
> first half is correct** (`0.0605` vs `0.0867`, CI-separated). ⚠️ **But the SAME submission then
> demolishes that comparator as leakage.** *Against the floor it retired, the argument does not
> carry; against the actual shipped system, removing the bundle WINS.*
>
> 🎯 **THE ACCURATE STATEMENT: removing the bundle HELPS, CI-separated, and does NOT help ENOUGH to
> clear the task.** *That is a different claim from "bundling costs nothing", and only one of them
> tells the next reader to keep looking at the representation.* **"Not the bottleneck" reads as
> "stop working on it"; a CI-separated `+0.0125` from deleting superposition -- on the very task
> where two replacement operators LOST -- says those two were the WRONG REPLACEMENTS, not evidence
> of no cost.**
>
> ⚠️ **WHAT I AM NOT CLAIMING:** `+0.0125` is small and nowhere near clearing the task; the cell did
> NOT compute this pair as a paired delta on stripped gold (point estimates `0.0582` vs `0.0459`
> agree in sign and size); and `RAW_COOC` is an explicit count table, **not a deployable
> representation** -- it BOUNDS what the bundle costs, it is not a proposal to ship.
>
> ## ➡️ **AND THIS CONFIRMS THE BLOCK ABOVE RATHER THAN REPLACING IT**
> The pre-filing correction on this brief said the `62%` is about **code RANK** -- an 11-dimensional
> source cannot fill a 256-dim code, so our codes are `11.7x` less orthogonal than random ones and
> crosstalk under bundling. **A count table has no rank ceiling at all, and it is the arm that wins.
> Those two findings agree.** 🎯 **The build target is MORE INDEPENDENT SOURCE DIMENSIONS, not a
> different combination rule** -- *which is the opposite lesson from priority 1, where the
> combination rule IS the target. Two different organs, two different faults; do not merge them.*

> # 🥉 **PRIORITY 3 — A MEASURED COST AND TWO LANDED REFUTATIONS OF THE OBVIOUS FIX. RECONCILE THEM.**
> **This is a contradiction, not a build.** I measured that the reader's bundle destroys most of the
> meaning signal. Two landed cells say replacing that bundle makes a real task WORSE. **Both are
> credible and they cannot both be the whole story.** *Filed rather than worked, because it needs one
> person holding the whole thing rather than my incremental measurements.*

> ## 🔻🔻 **READ THIS BEFORE THE REST: THE 62% IS PROBABLY ABOUT OUR CODE GEOMETRY, NOT ABOUT BUNDLING**
> **Found 2026-08-23, hours after filing, in prior work this brief did not cite.**
> `verification/verify_bundling_destroys_flat_sum.py` establishes:
>
> > *"summing B=8 near-ORTHOGONAL dense codes and recovering each in the bundle's top-B is
> > **LOSS-FREE** (retains the full 7.000-bit ceiling). So **'adding' is NOT intrinsically
> > destructive** -- destruction is a property of the code's GEOMETRY (correlated codes crosstalk;
> > orthogonal ones do not)."*
>
> **AND OUR CODES ARE THE CORRELATED CASE, BY A LOT.** Measured on 800 real items:
>
> | codes | mean \|cosine\| between DIFFERENT items | max |
> |---|---|---|
> | **ours (sensorimotor-derived)** | 🔻 **`0.5842`** | `1.0000` *(some pairs IDENTICAL)* |
> | truly random bipolar, same shape | `0.0498` | `0.2969` |
>
> **Ours are `11.7x` LESS ORTHOGONAL than random codes of the same shape.**
>
> 🔑 **AND THE REASON IS STRUCTURAL, NOT A TUNING MISTAKE: the sensorimotor vectors live in an
> ELEVEN-DIMENSIONAL space.** Projecting to 256 dims cannot manufacture independent directions --
> there are at most 11. **The codes are confined to an 11-dim subspace by construction, so they
> crosstalk under bundling exactly as the prior work predicts.**
>
> ⚖️ **WHAT THIS DOES AND DOES NOT CHANGE.** The `62%` loss is REAL for our codes and the segregation
> comparison stands as measured. **What changes is the DIAGNOSIS: "the bundle is lossy" becomes "an
> 11-dimensional signal cannot fill a 256-dimensional code, and bundling correlated codes
> crosstalks".** ➡️ **That points at a different fix entirely -- give the code more independent
> directions (more source dimensions), not a different combination rule.** *Both refuted arms
> (`STRUCTURE_HURTS`, `CONJUNCTIVE_HURTS`) changed the combination rule. None of them changed the
> rank of the source.*
> **REVERIFY:** the orthogonality measurement is four lines; the prior work is
> `verification/verify_bundling_destroys_flat_sum.py`.

# PROBLEM: ~62% OF MEANING IS LOST PER SENTENCE, EVERY ATTEMPT TO REPLACE THE BUNDLE HAS MADE THINGS WORSE — AND THE CAUSE IS PROBABLY THE CODE'S RANK, NOT THE BUNDLE

*(Titled "the bundle destroys..." when filed. Corrected the same day -- see the block above: our
codes are `11.7x` less orthogonal than random ones because an 11-dimensional signal cannot fill a
256-dimensional code, and bundling NEAR-ORTHOGONAL codes is loss-free.)*

**slug:** `the_bundle_destroys_meaning_but_replacing_it_hurts` · **opened:** 2026-08-23 by the
strategy session · **status:** OPEN

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

When our system reads a sentence, it takes every meaningful word and **mashes them all into one
shared representation.** Real sentences have about six such words.

I measured what that costs: **at six words, about 62% of what distinguishes one word's meaning from
another's is destroyed.** Give a word its own small compartment instead and you keep more than
double — using a compartment sixteen times smaller than the shared one.

**So the fix looks obvious. It has been tried twice and both times it made a real task worse.**

That is the problem. Not "make the representation better" — **work out why the thing that clearly
loses information is nonetheless the thing that performs best**, and what that implies.

---

## 2. WHY THIS ONE

- **IT BLOCKS A WHOLE CLASS OF FIXES.** Until this is understood, every proposal of the form "store
  meaning better" is guesswork — two of them are already refuted and nobody knows why.
- **THE CONTRADICTION IS THE ASSET.** A measured cost with no benefit, and a measured benefit to
  keeping the cost, is a much sharper starting point than either alone.
- 🔑 **AND THERE IS A LARGER NUMBER SITTING IN THE SAME RECORD (§3) THAT MAY MATTER MORE THAN
  ANYTHING HERE.** Read it before deciding this is the interesting problem.

---

## 3. MEASURED vs INFERRED

### MEASURED — you may build on these

| what | number | scope |
|---|---|---|
| **the reader's bundler is a bare flat sum** | `sign(sum of content-word vectors)` | *`context_vector`'s own docstring; independently verified by runtime reconstruction, bit-exact, order-invariant (`perirhinal_conjunctive.py`)* |
| **k = content words per sentence** | mean `5.6`, median **`6`**, p75 `7` | 3,998 real corpus sentences |
| 🔻 **what superposing k=6 costs** | retains **`37.6%`** of the k=1 baseline (`+0.1095` vs `+0.2914`) | equal-budget D=256; **`~62%` destroyed per sentence** |
| **segregated alternative at the same budget** | `+0.2343` in a **42-dim** slot — *more than the full 256 shared* | same signal, only the scheme changes |
| **practical floor** | **~8 dims/slot** (`+0.1537`); below that both schemes lose | swept to k=256 |
| 🔻 **STRUCTURE_HURTS** | structured is **below** base by `-0.0113`, CI `[-0.0195,-0.0030]` | `exp_structured_code_vs_flat_bag_c3_v1` |
| 🔻 **CONJUNCTIVE_HURTS** | no conjunctive arm beat the flat bag; two are CI-separated **below** it | `exp_perirhinal_conjunctive_readout_c3_v1` |
| 🚨 **AND THE BIGGEST NUMBER IN THE RECORD** | **`A5_STRINGCTRL 0.0870` vs `live base 0.0480`** | **a STRING-MATCHING CONTROL BEATS THE LIVE SYSTEM ~2:1 on that task** |

### INFERRED — overturning any of this is a RESULT

- 🔻 **That the two are even in conflict.** *My test asks whether INDIVIDUAL WORD MEANING survives the
  representation. Task c3 may not need individual word meaning — if similarity-by-shared-context-
  words is what it wants, blending is the FEATURE, not the bug.* **This is the most likely
  resolution and it is untested.**
- 🔻 That the 62% matters downstream at all. It is a property of the representation; **no task has
  been shown to lose because of it.**
- 🔻 That segregation would beat the flat bag on task c3. **Nobody has run it there** — the two
  refuted arms were *conjunctive* and *structured*, which are different operators.

---

## 4. ALREADY TRIED — DO NOT REDO

- ✅ **`hdlab/perirhinal_conjunctive.py` EXISTS** — a default-off drop-in for `context_vector_masked`,
  duck-typing the encoder through the existing `process_sentence(encoder=...)` plug point, with brain
  fidelity properly labelled. **Do not rebuild it.**
- ✅ **Conjunctive readout measured → `CONJUNCTIVE_HURTS`.** ✅ **Structured code measured →
  `STRUCTURE_HURTS`.** *Re-running either as-is adds nothing.*
- ✅ **Sparsity swept 1%→100%** — every density collapses to ~`+0.08`; does not rescue bundling.
- ✅ **An addressed slot (key-bind into a shared superposition)** — buys NO signal; binding permutes
  interference rather than removing it.
- ✅ The `sign()` normalisation is separately known: `+0.0245`–`+0.0267` for dropping it
  (`exp_graded_divisive_comparator_v1`). **That is the NORMALISATION; this brief is the BUNDLING.**

---

## 5. VERIFY BEFORE YOU START — THE DISK OUTRANKS THIS BRIEF

1. `python tools/before_you_start.py "flat bag vs structured context code"` — read **every** row.
2. Read `hdlab/perirhinal_conjunctive.py`'s docstring in full. **It states the flat-sum finding better
   than this brief does** and it labels pinned-vs-ours correctly.
3. Re-run the two landed cells' records and this brief's witnesses:
   `verification/test_segregated_beats_superposed_at_equal_budget.py`,
   `..._does_our_format_survive_the_meaning_signal.py`.
4. ⚠️ **Read `notes/problems/reader_meaning_channel/PROBLEM.md`'s orientation map.** It carries the
   channel-side findings and **two pieces of advice I wrote before testing them.** Do not inherit them.

---

## 6. THE BAR

**AN EXPLANATION THAT PREDICTS BOTH RESULTS, TESTED ON THE TASK WHERE THE REFUTATIONS LANDED.**

- **Show what task c3 actually needs from the representation.** If it needs blended
  similarity-by-shared-words, say so and show it — *that resolves the contradiction and closes this
  brief as UNDERSTOOD, which is a PASS.*
- **If instead you claim the 62% does cost us, name the task where it costs and measure it there**,
  against the same floors those cells used. **The strongest floor already on record is
  `A5_STRINGCTRL 0.0870`; you must beat that, not the live base.**
- **Any new representation arm must run on task c3** alongside the flat bag, with the same floor,
  CI-separated, gated on the floor's upper bound.
- **Report coverage and the k distribution** of whatever population you use.

### HOW WE WOULD KNOW IT FAILED — pre-register which fired
- **(a)** The blending IS the feature → **explains both, closes the brief, a clean PASS.**
- **(b)** A representation change beats the flat bag AND the string control on c3 → the refutations
  were about the wrong operator, and this is a real gain.
- **(c)** Nothing beats `A5_STRINGCTRL 0.0870` → **the representation question is not the bottleneck
  and this whole thread is a distraction. Say so; that is the most valuable outcome.**
- **(d)** You cannot tell what c3 needs → report that as a defect in the task, not in the code.

🚫 **NOT ACCEPTED:** a third representation measured only on word-pair similarity (that is what I
did, and it does not settle anything); or any comparison against the live base rather than the
strongest floor.

---

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the bundler | `hdlab/reading_grounding_loop.py` → `context_vector`, `context_vector_masked` |
| the built alternative, default-off | `hdlab/perirhinal_conjunctive.py` |
| the two refutations | `data/exp_structured_code_vs_flat_bag_c3_v1/`, `data/exp_perirhinal_conjunctive_readout_c3_v1/` |
| my witnesses | `verification/test_segregated_beats_superposed_at_equal_budget.py`, `..._does_our_format_survive_the_meaning_signal.py`, `..._does_sparsity_fix_the_bundling_loss.py`, `..._does_an_addressed_slot_survive_bundling.py` |
| 🚫 **DO NOT TOUCH** | `preregs/**`, any `arm_key*`, `GROUNDED_CAP` |

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **"Segregation is the fix."** It is a property of representations at equal budget. **Two landed
  cells refute the build move it suggests.** I nearly wrote it as a recommendation.
- 🚫 **The 62% as a task loss.** It is a per-item-similarity loss. No task has been shown to suffer.
- 🚫 **`A5_STRINGCTRL 0.0870` as "the system is useless".** It is one task, and the comparison needs
  its own read — but it must not be ignored either.
- 🚫 Re-running conjunctive or structured arms unchanged. Both landed.

---

## TLDR

Our system mashes every meaningful word of a sentence into one shared representation. I measured that
this destroys about 62% of what tells one word's meaning from another — and that giving each word a
small private compartment would keep more than twice as much, in sixteen times less space.

**The obvious conclusion is wrong, or at least unproven.** Two experiments on file already tried
replacing the mashing with something more structured, and both made a real task *worse*. Someone even
built the replacement and left it switched off.

**And the loss may not be about the mashing at all.** Prior work on file shows that mashing together
codes that are *well spread out* loses nothing. Ours are not well spread out -- they are about twelve
times more similar to each other than they should be, because the underlying information only has
**eleven independent dimensions** and no amount of spreading it into 256 can create more. So the
crowding is built in, and every fix tried so far changed how things are combined rather than how much
independent information went in.

The likeliest explanation, untested, is that the task doesn't want individual word meanings — it
wants the blur. If so, the "loss" is the point, and confirming that closes the question properly.

**And there is a bigger number in the same file: on that task, plain string matching beats our whole
system by nearly two to one.** If that holds up, none of this representation work is the bottleneck.

## QUESTIONS

None. The board is empty.

## NEXT STEPS

1. Work out what the task actually needs before proposing any new representation.
2. Whatever you measure, beat the string control, not the live base.
3. If the string control result holds, say so loudly — it outranks this brief.
