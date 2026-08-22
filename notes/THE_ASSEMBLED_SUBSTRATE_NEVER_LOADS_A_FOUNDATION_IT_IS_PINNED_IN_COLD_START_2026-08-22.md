# **THE ASSEMBLED SUBSTRATE NEVER LOADS A FOUNDATION. IT STARTS FROM 107 SEED WORDS ON EVERY RUN, AND ITS `foundation_dir` PARAMETER IS DEAD.**

**Established at RUNTIME by instrumenting the functions, not by grep -- because grep got this wrong
in both directions first.** Found while chasing the owner's stale-sheet observation.

---

## 1. THE RUNTIME MEASUREMENT

`hdlab/substrate.py`, constructed with `foundation_dir` **explicitly set** to
`data/foundation/reading_grounding_v5_termboundary`, then asked to read 120 sentences, with
`foundation_persistence.load_foundation` / `save_foundation` wrapped in call counters:

| | |
|---|---|
| **`load_foundation` calls** | 🔻 **`0`** |
| `save_foundation` calls | `0` (it fires only on an explicit `persist()`, not on `read()`) |
| store facts BEFORE the read | **`92`** -- derived from the `107` seed words |
| store facts AFTER the read | `92` |

> # **`self.foundation_dir` IS ASSIGNED AT `substrate.py:378` AND NEVER READ AGAIN. THE PARAMETER DOES NOTHING.**

*The `92 -> 92` is NOT itself the defect: this plan already measured that grounding turns on between
100 and 400 sentences, so 120 is below threshold. **The defect is the `0`.***

## 2. 🔻 GREP GOT THIS WRONG IN BOTH DIRECTIONS, AND BOTH ERRORS WERE MINE

1. **First I searched `self.foundation_dir` and concluded the substrate "never persists either".**
   **WRONG** -- `save_foundation` IS called at `:813`, it just takes `dir_path` as an argument
   rather than reading the attribute.
2. **Then `load_foundation` grep returned `hdlab/reading_grounding_loop.py` and I nearly filed
   "the live loop loads it".** **WRONG** -- line 1732 is a **COMMENT**:
   *"# by foundation_persistence.save_foundation and reloaded by load_foundation"*.

**That is precisely the trap `CLAUDE.md` documents** (*"`grounding_acquisition_loop.py:195` names
`foundation_persistence` only in a comment, which grep reads as an import"*) -- **and I fell into
it on the very module the rule was written about.** *Runtime observation decided it; static search
only located candidates.*

### THE ENUMERATION, WITH COMMENTS SEPARATED FROM CALLS
`load_foundation` appears in **6 files**: its own module, **two diagnostics**
(`tools/diagnose_refusals_at_load.py`, `tools/diagnose_read_with_loaded_foundation.py`), **one
test** (`verification/test_grounding_refusal.py`), one skunkworks atomiser, and **one comment** in
`reading_grounding_loop.py`.
> ### **NO LIVE READING PATH CALLS IT. ONLY DIAGNOSTICS DO.**

## 3. 🎯 IT MECHANISTICALLY EXPLAINS THE DEGENERACY THIS PLAN ALREADY SPENT DAYS ON

The plan's own diagnosis of the generic-attractor problem -- `way` being the meaning of **17.7%** of
grounded terms, `mouse -> way`, `swim -> way`, `cry -> way` -- reads:

> *"the anchor pool is `ConceptSpace`, which holds SEED words plus already-grounded words -- so
> early grounding is forced to choose among ~107 generic seeds. That is a structural cause with a
> structural fix, and **it predicts the degeneracy should FALL as the grounded vocabulary grows**."*

> # **IF NO RUN EVER LOADS THE PREVIOUS RUN'S FOUNDATION, THE GROUNDED VOCABULARY CANNOT GROW ACROSS RUNS. THE PREDICTED FALL IS UNREACHABLE BY CONSTRUCTION.**

**The substrate is permanently pinned in the cold-start regime that its own analysis identified as
the cause.** *Every run re-enters the ~107-seed bottleneck, so the degeneracy is not a tuning
problem or a scale problem -- it is arithmetic.*

## 4. 🧠 THE BRAIN READ, AND IT IS NOT DECORATION

**Consolidation is the transfer of episodic traces into a durable semantic store, and its defining
property is that it PERSISTS ACROSS EPISODES.** A system that discards its accumulated semantic
memory at the end of every session does not have a slow store that is weak -- **it has no slow
store at all.** *This is the same gap the 08-19 brain-fidelity drill named from the other side
(`cls_replay_cycle` built, never called, no cortical target); this is the persistence half of it,
and it is one dead attribute wide.*

## 5. ⚠️ SCOPE -- WHAT IS AND IS NOT CLAIMED

- **This is about `hdlab/substrate.py`**, the Phase 1 assembled substrate. It is NOT a claim that
  `reading_grounding_loop` cannot persist -- `save_foundation` genuinely lives there and the four
  foundations on disk were written by something.
- **`save_foundation` works.** The asymmetry is load, not save. *We have been writing foundations
  and never reading them back.*
- **NOT MEASURED HERE: whether loading one would actually help.** The cold-start explanation is
  mechanistically forced, but *"the degeneracy falls when the vocabulary grows"* is still the
  plan's PREDICTION, not a result. **Wiring the load is the experiment, not the fix.**
- **One run, one config, 120 sentences.** The `0` load calls is a structural fact and does not need
  n; the `92 -> 92` does, and is not offered as a finding.

## 6. AND IT EXPLAINS THE OWNER'S STALE SHEET

**Four foundations sit on disk in two incompatible shapes** -- `v1`/`v2q` carry a full `store/` plus
`concept_space.npz` and `manifest.json`; `v3`/`v4`/`v5` are a single `definitional_facts_*.jsonl`.
**Nothing marks one as current, and nothing loads any of them.** *That is why the sampler could draw
from a three-versions-old artifact without anything objecting: there is no notion of a current
foundation in the code, only in filenames.*

---

## TLDR

Our system reads text, works out what a few words mean, saves that to disk -- and then, next time it
starts, ignores the file and begins again from the same 107 starter words. Every run. The setting
that is supposed to point it at its own accumulated knowledge is read once into a variable and never
used again.

This explains something we had been treating as a hard research problem. The system keeps deciding
that the meaning of `mouse`, `swim` and `cry` is all the same word, `way` -- and our own analysis
said that would stop happening once its vocabulary grew. Its vocabulary can never grow, because it
throws it away between runs.

It also explains how the owner ended up hand-scoring a three-versions-old file: nothing in the code
has any notion of which knowledge base is the current one.

**Two cautions on my own enthusiasm.** I have not shown that loading the foundation would fix
anything -- that is the next experiment, not a conclusion. And I got this wrong twice with grep
before running it, in both directions, on the exact module whose documented trap is that grep reads
comments as calls.

## QUESTIONS

None new. Q107 and Q109 remain with the owner.

## NEXT STEPS

1. 🎯 **Wire `load_foundation` into `hdlab/substrate.py` behind the existing `foundation_dir`, and
   measure the degeneracy with and without.** *This is a real experiment with a pre-registered
   prediction already on record (the plan's own: degeneracy FALLS as vocabulary grows), a clean
   one-variable design, and an obvious way to be wrong.* ⚠️ **Edits `hdlab/`, so it is buildable in
   the main thread; the MEASUREMENT is a cell and routes to `hdi_exp_dev`.**
2. **Mark a current foundation** -- a pointer file or a manifest field -- and make
   `draw_representative_blind_sample.py` refuse anything else.
3. 🚫 **Do not quote `92 -> 92` as evidence of anything.** 120 sentences is below the measured
   grounding threshold.
