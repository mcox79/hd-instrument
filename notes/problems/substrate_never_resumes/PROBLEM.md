---
priority:
review: EXCELLENT
review_text: Refuted my own brief's premise, caught its own artifact, and the DECOY control proved it is bins not meaning.
---

> # MY REVIEW OF THE SUBMISSION: **EXCELLENT**
> *(reviewed 2026-08-23 by the strategy session, which owns integration. I re-ran their witness and
> it reproduced to the digit: COLD `168.0` vs RESUMED `9.0` new groundings across 3 seeds, and the
> pure-mechanism probe at COLD `0.955` / RESUMED `0.000` / DECOY `0.000`.)*
>
> **THEY REFUTED THE PREMISE OF MY OWN BRIEF, AND THAT IS THE BEST THING A SOLVER CAN DO HERE.** I
> filed this expecting a wiring job -- the substrate throws its store away every run, so let it
> resume and the generic-attractor degeneracy should fall. **They wired it, measured it, and the
> prediction is dead.** Resuming makes a matched re-read ~18x LESS productive (`168` -> `9` new
> groundings), and grounding precision sits at its RANDOM_ANCHOR floor in *every* arm.
>
> **THE MOVE THAT MAKES THIS EXCELLENT RATHER THAN MERELY CORRECT: they caught their own artifact.**
> Their first metric counted each self-return (`canon_obj == the word`) as its own anchor, which
> read as "every word got a distinct meaning" -- a clean, impressive-looking result that was exactly
> backwards. A self-return is `canonicalize`'s NO-MATCH signal, a refusal. They noticed, excluded
> it, and the apparent win evaporated. **That is the failure mode this project keeps paying for,
> found by the one person who stood to gain from not finding it.**
>
> **AND THE DECOY ARM IS THE CONTROL I WOULD HAVE ASKED FOR.** Loaded anchors with the labels
> permuted match RESUMED *exactly* (`0/164` both). A bijection on labels cannot change which vectors
> clear a threshold, so the loaded anchors' MEANING is irrelevant to the outcome -- it is anchor
> geometry. That converts "resuming does not help" from a result into an explanation.
>
> **WHAT THEY DECLINED TO CLAIM IS AS GOOD AS WHAT THEY CLAIMED.** They flag their own precision arm
> as under-powered (`3` hits / `151` scorable against a standing bar of `>=300`), lean on it only
> for "not above random", and name what they would withdraw first. They did not test recall/query
> and said so. They left `hdlab/` alone and proposed the diff instead, which is the protocol.
>
> 🔻 **THE ONE THING I WOULD PUSH BACK ON, AND IT IS SMALL:** the headline "~18x less productive" is
> true but easy to misread as a *regression*. A resumed substrate grounds fewer NEW words partly
> because it already knows the recurring vocabulary -- that is the system working. The damning
> number is not `168` vs `9`; it is **`0/164` novel words matching any loaded anchor**, which is
> where the mechanism actually fails.
>
> ## WHAT I DID WITH IT
>
> **LANDED the wiring** in `hdlab/substrate.py` -- their diff, in shape -- **for persistence and
> accumulation only.** Cold construction is byte-identical: still `92` live facts, `_pass_idx` `0`.
> Resumed carries `390` and `_pass_idx` `81` from the manifest.
> `verification/test_foundation_dir_does_not_lie.py` was rewritten: it pins the LOADING, and its
> last test **pins the refutation itself inside the constructor comment**, positive-controlled
> (damage the text -> the test fails). The risk after wiring was never that loading breaks; it is
> that someone re-bills persistence as the grounding fix. That prediction is retired.
>

> # 🥈 **PRIORITY 3 of 8.** *(ranked by the strategy session, 2026-08-22)*
> **NOTHING THIS SYSTEM LEARNS SURVIVES THE RUN THAT LEARNED IT, so no result can ever compound.**
> Measured 2026-08-22: `Substrate(foundation_dir=...)` was read ZERO times and no caller passed it;
> it now raises rather than pretending.
> ✅ **A WIRING JOB, NOT A BUILD, AND THAT IS WHY IT RANKS THIS HIGH:**
> `hdlab/foundation_persistence.py` implements save AND load, is registered, and **passes `9/9` of
> its own self-tests at HEAD** -- including `continuation_matches_uninterrupted_run` and
> `full_foundation_roundtrip_and_resume_grounds`. **Resuming is already behaviourally correct; it is
> simply never called.**
> 🔻 **AND IT COMPOUNDS WITH A SECOND CAP FOUND THE SAME DAY:** one `read()` call delivers
> ~1,000 sentences however many you ask for (raise `max_patches`, not `n_sentences`). **Capped per
> call AND discarded between calls -- which is why the vocabulary cannot grow, and why the plan's own
> prediction that the generic-attractor degeneracy should FALL with scale is unreachable by
> construction rather than merely untested.**
> ⚠️ *FIRST MOVE: build a CLEAN snapshot. The only two resumable snapshots on disk are the two
> PRE-stemmer-fix ones, carrying `7.87%` junk.*

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

## ✅ **TEST 4 ANSWERED 2026-08-22: THE DEFECT ITSELF COSTS US, AND HERE IS THE NUMBER**

**The fourth ranking test asks whether a number shows THE DEFECT costs us, or only that an
ALTERNATIVE would be better. That test refuted `flat_store` and deflated `lookup_does_not_lemmatise`.
This brief passes it, measured rather than argued:**

| | store `live_facts` | consolidated |
|---|---|---|
| fresh substrate, BEFORE any read | `92` | `0` |
| same substrate, after reading ~520 | `100` | `4` |
| same substrate, after a second ~520 | `104` | `6` |
| 🔻 **NEW substrate -- WHAT EVERY RUN ACTUALLY DOES** | 🔻 **`92`** | 🔻 **`0`** |

> 🔻 **CORRECTED WITHIN THE HOUR, AND THE FIRST VERSION OF THIS TABLE WAS WRONG.** I read
> `state.store.facts`, which does not exist; my helper caught the `AttributeError` and silently
> returned `len(consolidated())` instead, **so both columns showed the same number and looked
> plausible.** The real accessor is `state.store.live_facts`. *A fallback that returns a DIFFERENT
> QUANTITY on error is worse than a crash -- it produced a table that agreed with itself.*
> ✅ **The brief's long-standing `92` was right all along, and my "correction" of it was the error.**

> ### **THE NEXT RUN STARTS AT ZERO REGARDLESS OF WHAT THE LAST ONE REACHED. READING IS NOT CUMULATIVE.**

**That is not "resuming would be better" -- it is the cost of not resuming, stated as a number.**
*A new run resets `104 -> 92` live facts and `6 -> 0` consolidated: back to the `107`-seed baseline. Everything learned beyond the seeds is discarded, so a hundred runs leave exactly what one run leaves.*
⚠️ *Small absolute counts (`n_dim=256`, ~520-sentence reads) -- the SHAPE is the finding, not the
magnitude. And the short-read guard fired during this very measurement: 600 asked, 520 read.*

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

> # 🔑 **READ THIS FIRST: THIS IS A *WIRING* JOB, NOT A BUILD. THE PERSISTENCE ORGAN EXISTS AND ITS ROUND-TRIP PASSES AT HEAD TODAY.**
> **`hdlab/foundation_persistence.py` implements BOTH `save_foundation` and `load_foundation`, is
> REGISTERED** (*"foundation save/reload persistence (bit-identical round-trip, resumable
> per-segment)"*), **and its module docstring names the exact gap this brief is about:** *"every run
> starts from an EMPTY store."*
> ✅ **RUN ON DISK 2026-08-22, NOT QUOTED FROM THE REGISTRY -- `python hdlab/foundation_persistence.py`
> returns `9/9` PASS**, including `store_roundtrip_identical_ok`, **`continuation_matches_uninterrupted_run_ok`**
> and **`full_foundation_roundtrip_and_resume_grounds_ok`**. ➡️ **So resuming is not merely
> BYTE-correct, it is BEHAVIOURALLY correct: a continued run matches an uninterrupted one, and a
> resumed foundation actually grounds.**
> 🔑 **THE ENTIRE GAP IS THAT NOTHING ON THE LIVE PATH CALLS `load_foundation`.** *This is the
> WIRE-DON'T-ISLAND pattern, not a missing capability -- so DO NOT BUILD A SECOND PERSISTENCE LAYER.*
> ⚠️ *Limit: those 9 self-tests run on their own fixtures. They establish the round-trip works; they
> do not establish it works on a REAL foundation written by a real reading run. **Checking that on a
> clean snapshot is the first move.***
>
> ### ✅ **STRENGTHENED 2026-08-22 BY A SECOND, DIFFERENT TEST -- AND THE PARAMETER NO LONGER LIES.**
> **The measurement below counts `load_foundation` CALLS. That could miss a read that used the path
> some other way, so the claim was re-tested AS STATED**, with a descriptor recording every READ of
> the attribute: **`self.foundation_dir` is read `0` times across construction plus a 120-sentence
> read** -- *positive control: a deliberate read IS observed, so zero means zero, not a broken spy.*
> 🔑 **AND REPO-WIDE, NO CALLER PASSES THE ARGUMENT AT ALL** (`hdlab/`, `experiments/`,
> `verification/`, `tools/`). **The substrate has never been ASKED to load a foundation by anybody.**
> ✅ **`Substrate(foundation_dir=...)` NOW RAISES `NotImplementedError` instead of accepting a path
> and ignoring it.** *Safe precisely because no caller passes it; `None` stays silent so no
> construction anywhere changes. **Whoever implements loading deletes that raise** --
> `hdlab/substrate.py`, and `verification/test_foundation_dir_does_not_lie.py` (3/3) pins both the
> refusal and the zero-read measurement, so wiring it up makes that test fail on purpose.*

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
