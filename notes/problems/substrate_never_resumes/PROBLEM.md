# PROBLEM: THE SYSTEM THROWS AWAY EVERYTHING IT LEARNED, EVERY RUN

**slug:** `substrate_never_resumes` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · **verified FIRST-HAND at runtime by the strategy session, not relayed**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

The system reads text, works out what a handful of words mean, and saves that to disk. Next time it
starts, **it ignores the file and begins again from the same 107 starter words.** Every run.

The setting that is supposed to point it at its own accumulated knowledge is read into a variable
once and never used again.

**And it explains something we had been treating as a hard research problem.** The system keeps
deciding that the meaning of `mouse`, `swim`, `hall` and `cry` is all the same word -- `way`, which
is the meaning of **17.7%** of everything it grounds. Our own analysis said that would stop once its
vocabulary grew past the generic starter words. **Its vocabulary can never grow, because it is
discarded between runs.**

**The job: decide whether the system should resume, from what, and prove whether resuming actually
helps.**

---

## 2. WHY THIS ONE

- **It converts a research problem into a wiring problem** -- or proves it does not, which is just
  as valuable.
- **It is one dead attribute wide.** The cost of finding out is small.
- **The brain reading is not decoration here.** Consolidation is *defined* by persisting across
  episodes. A system that discards its semantic store every run does not have a weak slow system --
  it has none. *This is the persistence half of a gap already found from the other side: the replay
  machinery (`cls_replay_cycle`) is built, called by nothing, and has no cortical target to replay
  into.*

---

## 3. MEASURED vs INFERRED

### MEASURED -- all of this was established at RUNTIME on 2026-08-22, by instrumenting the functions

| | |
|---|---|
| `load_foundation` calls, with `foundation_dir` **explicitly set** | 🔻 **`0`** |
| `save_foundation` calls during `read()` | `0` (it fires only on an explicit `persist()`) |
| store facts before the read | **`92`** -- derived from the `107` seed words |
| store facts after reading 120 sentences | `92` |

- **`self.foundation_dir` is assigned at `hdlab/substrate.py:378` and never read again.**
- **Only `v1` and `v2_qualityfix` are LOADABLE.** `load_foundation` requires `store/`,
  `concept_space.npz`, `library_pending.json` and `manifest.json`; **`v3`/`v4`/`v5` have NONE of
  them** -- they are a different pipeline's fact dumps, not resumable states.
- **All nine foundation directories were written on `2026-08-12`** -- the same day. They are not a
  version history.
- **Enumerated, with comments separated from calls:** `load_foundation` appears in 6 files -- its
  own module, **two diagnostics**, one test, one atomiser, and **a COMMENT** at
  `reading_grounding_loop.py:1732`. **No live reading path calls it.**

> ### ⚠️ **GREP GOT THIS WRONG IN BOTH DIRECTIONS BEFORE RUNTIME SETTLED IT.**
> The strategy session first concluded *"the substrate never persists either"* -- **wrong**,
> `save_foundation` IS called at `:813`, it just takes the path as an argument. Then nearly filed
> *"the live loop loads it"* off that comment -- **wrong again.** *Prefer runtime evidence here;
> this module is exactly where static search misleads.*

### INFERRED -- and the first one is the whole question

- 🔻 **That resuming would HELP.** **NOT MEASURED.** The cold-start explanation is mechanistically
  forced -- the vocabulary cannot grow across runs, so the predicted fall in degeneracy is
  unreachable -- **but "degeneracy falls as vocabulary grows" is the plan's PREDICTION, not a
  result.** *Wiring the load is the experiment, not the fix.*
- *That the `92 -> 92` is meaningful.* **It is not, and do not quote it.** 120 sentences is below
  the measured 100-400 threshold at which grounding turns on at all.

### 🔗 A COUPLING THAT IS NOW DECIDED, NOT JUST FLAGGED (updated 2026-08-22 after `stored_terms_are_stems` landed and was re-verified)

**The only two resumable snapshots (`v1`, `v2_qualityfix`) are EXACTLY the two built before the
lemmatiser fix**, and `7.87%` of `v2_qualityfix`'s stored subjects are chopped-up non-words.
**A fresh store on HEAD measures `0.00%` on the same detector** -- so the damage is a STALE DATA
ARTIFACT, not a live defect, and it is confined to the artifacts you would be loading.

> ### ➡️ **SO THE FIRST MOVE IS TO *BUILD* A CLEAN RESUMABLE SNAPSHOT, NOT TO LOAD `v2q`.**
> *Loading an old foundation resumes `7.87%` guaranteed-junk subjects into the anchor pool -- which
> is the very pool whose degeneracy this problem exists to measure. **You would be testing whether
> resuming helps while feeding it the one input known to be contaminated.*** A clean snapshot costs
> one read; the ambiguity it removes is worth far more than the read.

⚠️ **AND DO NOT QUOTE THE `7.9%` AS A PROPERTY OF THE SYSTEM.** It is a property of one stale
artifact. Any grounding-quality figure computed on `v1`/`v2_qualityfix` inherits it and must say so.

---

## 4. ALREADY TRIED

- **Two diagnostics already load a foundation** (`tools/diagnose_refusals_at_load.py`,
  `tools/diagnose_read_with_loaded_foundation.py`). **Read them first** -- they are the closest
  thing to prior art, and one of them already produced a correction: a *"22x refusal asymmetry"*
  turned out to be **93.2% pre-existing**, because a refusal log had been persisted INSIDE the
  foundation months earlier. **The real ratio was 1.54x.**
  > **That is the cheapest guard for this whole problem: MEASURE THE BASELINE BEFORE THE
  > INTERVENTION, especially when it obviously must be zero.** A loaded foundation brings its own
  > accumulated counters with it, and attributing them to your run is the documented failure here.
- **The degeneracy has been measured and partly moved by a different lever:** rotating the corpus
  shelf (rather than re-reading the same three books) took the top-anchor share `23.6% -> 9.5%` and
  distinct-anchors-per-grounded `0.382 -> 0.524, still rising`. **But a NEW generic attractor formed
  (`available`), so shelf breadth HALVES the degeneracy and does not remove it.** *Your arm must be
  compared against that, not against the un-rotated version.*

---

## 5. VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

```bash
python tools/before_you_start.py "make the substrate resume from a saved foundation"
python tools/experiment_index.py query "foundation"
python tools/experiment_index.py query "persistence"
python tools/symbol_corrections.py load_foundation
```
**Re-run the runtime probe yourself** -- construct `Substrate(foundation_dir=...)`, wrap
`load_foundation`/`save_foundation` in counters, read a few hundred sentences, and confirm the `0`.
*If it now loads, the brief is stale and that is your finding.*

---

## 6. THE BAR

**This problem is answered by a MEASUREMENT, not by a wiring diff.** A pull request that wires the
load and asserts it is better does not clear it.

1. **Wire `load_foundation` behind the existing `foundation_dir`, defaulting to OFF** so that
   passing nothing leaves behaviour byte-identical. *Additive, cannot regress.*
2. **Prove the wiring BOTH WAYS** with a self-test: off -> load not called, store starts at seeds;
   on -> load called, store starts populated. **An ablation asserted only by "the off arm grounds
   nothing" would pass on a broken build.**
3. **Then measure the thing that matters:** with a foundation loaded vs cold, on matched reading
   volume, report **top-anchor share**, **distinct anchors / grounded**, and **grounding precision
   against an independent gold** -- each with its floor and CI.
4. **Rate-match the arms.** *This project has broken its own foraging control twice in two days by
   matching on the budget rather than on what the live arm actually consumed. Run the live arm
   first, then give the twin exactly its sentence count.*

### HOW WE WOULD KNOW IT FAILED
- **(a)** Loading changes nothing -> the cold-start explanation is **refuted**, which is a genuinely
  important result and retires a standing prediction.
- **(b)** Degeneracy falls but precision does not -> we bought variety, not correctness. **Say so;
  do not let a moving statistic stand in for the outcome.**
- **(c)** It helps only because the loaded foundation brings its own counters -> the 22x trap above.
  **Measure the baseline first.**
- **(d)** There is nothing clean to load -> then the finding is that the pipeline stopped producing
  resumable states after `v2q`, and the build is a clean snapshot rather than a loader.

---

## 7. FILES AND ENTRY POINTS

- **The dead parameter:** `hdlab/substrate.py:378`
- **The loader:** `hdlab/foundation_persistence.py` (`load_foundation`, `save_foundation`)
- **The save call site:** `hdlab/substrate.py:813`
- **The snapshots:** `data/foundation/` -- **READ-ONLY, one disk, no backup. Never overwrite one;
  write a new directory.**
- **🚫 YOU DO NOT WRITE TO `hdlab/` -- THE LIVE SUBSTRATE (owner ruling, board Q111, 2026-08-22).** *Prove the mechanism in `experiments/` and `verification/`, then state in `SOLVED.md` exactly what would have to change in `hdlab/` and why. **The strategy session re-verifies and lands it, and is the sole writer there** -- two writers on one live file already destroyed a full day's audit here, silently.*

**🚫 DO NOT TOUCH:** `preregs/**`, `arm_key*`, `notes/STATUS.md`, the build plan, other problem
  folders.

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **Do not quote `92 -> 92`.** Below the grounding threshold; it is not evidence of anything.
- 🚫 **Do not describe `v3`/`v4`/`v5` as newer versions of `v2q`.** Different pipeline, same day.
- 🚫 **Do not quote the `22x` refusal asymmetry.** It is `1.54x`; the rest pre-dated the read.
- ⚠️ **Do not treat "degeneracy falls as vocabulary grows" as established.** It is the prediction
  this problem exists to test.
