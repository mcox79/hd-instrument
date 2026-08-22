> # 🥉 **PRIORITY 3 of 5 -- THE FLAGSHIP, AND THE BROADEST.** *(ranked 2026-08-22)*
> **This is the actual goal; it ranks third only because 1 and 2 are upstream of it and far more
> bounded.** *A better reader writing into a store that destroys what it writes, on a foundation that
> is discarded at the end of the run, cannot show what it is worth.*
> 🔑 **AND THIS BRIEF NOW OWNS A BLOCKER THE OTHERS DEPEND ON: `read()` NEVER CONSULTS THE
> MEANING ASSET AT ALL.** Runtime, positive-controlled: `0` calls to `grounded_similarity` /
> `grounded_vector` / `_table` across a 150-200 sentence read -- **the norms table is never even
> loaded.** The substrate's own B5 slot says so (`NEEDS_ADAPTER`, *"read() does not consult it"*).
> ⚠️ **SO THE ADAPTER IS PART OF THIS PROBLEM.** Until it exists, any meaning-side improvement --
> including PRIORITY 4 -- is real but UNMEASURABLE on a reading task. *Its hub-spoke combination rule
> is UNPINNED, so whatever you build there is our-invention-under-test, not brain-derived.*

# PROBLEM: THE READER'S MEANING CHANNEL IS THE WRONG MODALITY

**slug:** `reader_meaning_channel` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · **this is the highest-value problem in the project**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

Our system works out what a word means by noticing which other words show up near it. That is the
only channel it has. **We can now prove that channel cannot carry the answer** -- not that it is
weak, that it tops out, and we have hit the top.

Meanwhile a set of human sensory ratings already sitting on our disk -- how much a word involves
seeing, hearing, touching, moving -- predicts what words mean **two to seven times better**, and
covers 100% of the vocabulary we test on. It is not connected to anything that runs.

**The job: make the system get meaning from that channel instead, at reading time, and prove the
gain survives on text it has never seen.**

---

## 2. WHY THIS ONE

**It is upstream of nearly every negative in the archive.** The system stores word codes that carry
no meaning by construction, then combines them in a way that destroys most of what little arrives.
Every downstream repair has measured null -- and this explains why: *there was nothing there to
repair.*

**And it is the clearest case of the project's own pattern:** the fix is already on disk, unwired,
and was filed CLOSED.

---

## 3. MEASURED vs INFERRED

### MEASURED -- these have controls and you may build on them

| what | number | scope you must carry with it |
|---|---|---|
| **sensorimotor cosine predicts HUMAN similarity** | **rho `0.3171`, CI `[0.2605, 0.3707]`** | 988 SimLex-999 pairs; **UNFITTED** -- a plain cosine, no model |
| raw co-occurrence predicts the same | **rho `0.0446`, CI `[-0.0177, 0.1077]`** | **CI INCLUDES ZERO** -- same pairs |
| the paired difference | **`+0.2348`, CI `[+0.1605, +0.3155]`** | **CI-SEPARATED**, paired bootstrap |
| sensorimotor on pick-the-right-one-of-50 | **`0.6413`** (345/538) | fitted, **word-disjoint CV**, one corpus |
| co-occurrence on the same task | **`0.3067`** (165/538) | same folds, same model |
| **co-occurrence CEILING** | **`0.3104`** | **two completely different feature sets converge**: 8 scalars + tree ensemble, and the full 1,024-dim profile + linear model |
| controls on the sensorimotor arm | candidate-only **`0.0985`**, shuffled-query **`0.0595`** | **the PAIRING carries it**; removing candidate-only features IMPROVED the score |
| coverage | **100%** of the 1,024 test words | so this is NOT coverage-limited |

**The brain side, and it is why this is not just a benchmark trick:** form (spelling) and meaning
are **separate systems** -- a spelling area behind the left ear, and meaning distributed across the
senses with a hub at the front of the temporal lobe binding them. **We have been using a spelling
code as a meaning code.** That is structural, not a tuning problem.

### INFERRED -- overturning any of this is a RESULT, not a failure

- *That a read-time mechanism can capture what the fitted ceiling diagnostic sees.* **The 0.6413 is
  a CEILING, fitted on the gold. It says THE INFORMATION IS THERE. It does not give a mechanism, and
  building one is exactly this problem.**
- 🔻 **CORRECTED 2026-08-22: I first wrote "coverage at scale is UNMEASURED". IT IS MEASURED, and
  the number is in `notes/LONG_TERM_PLAN.md` Phase 1, which names this exact problem as the current
  bottleneck.** *The asset **covers `60.4%` of RUNNING TEXT but only `10.3%` of DISTINCT WORDS, and
  coverage falls to `4%` beyond rank 64,000.*** ➡️ **So coverage is not an unknown risk -- it is a
  KNOWN, QUANTIFIED constraint with a named work item beside it: widen the grounded core by
  **`+14,704` words** in frequency order to reach ~90% token coverage (`+40,160` -> 95%; `+103,558`
  -> 98%). **The ~15k option is the knee of the curve.***
  ⚠️ **AND THE PLAN'S OWN NON-NEGOTIABLE ON THAT WIDENING, WHICH IS THE TRAP: re-score the widened
  set ON ITS OWN NEW WORDS.** *The existing evidence that norms generalise is about rare words that
  ALREADY HAVE norms. Until new words are scored, the coverage number is arithmetic, not
  capability.*
- 🔑 **ADDED 2026-08-22 -- BEFORE NORMING A SINGLE NEW WORD, READ THIS: `+13.2` POINTS OF THAT
  COVERAGE ARE ALREADY ON DISK AND THE LOOKUP CANNOT REACH THEM.** `hdlab/grounded_similarity.py:165`
  is `_table().get(word.lower())` -- **a raw string match with no morphology**, so the asset holds
  `country` and reads past `countries`, holds `release` and misses `released`. *Corpus-scale, with
  the landed cell's `0.6035`/`0.1027` reproduced exactly first as the control:* **token coverage
  `0.6035` -> `0.7350` under the repo's own `normalize_lemma`; type coverage `0.1027` -> `0.1633`.**
  ➡️ **The gap from `60.35%` to the `90%` target is `29.65` points and this is `13.15` of them -- 44%
  of the way, at ZERO data cost. So `+14,704` counts inflected forms of ALREADY-NORMED words as words
  needing new norms.** ⚠️ *Two limits, both measured not assumed: ~4% of the recoveries are wrong
  (`using -> us`, `angeles -> angel`, `notes -> not`), and irregulars (`women`, `feet`) are missed by
  both methods so the ceiling is HIGHER than `0.7350`.* 🚫 **AND THE TRAP DIRECTLY ABOVE APPLIES TO
  IT UNCHANGED -- this is COVERAGE, not CAPABILITY. No task was run. `grounded_similarity.py` was
  deliberately NOT changed.** *The bar: a TASK score, with an information-free twin that lemmatises
  to a RANDOM covered word required to LOSE.*
  📎 `notes/THE_NORMS_LOOKUP_DOES_NOT_LEMMATISE_AND_THAT_IS_13_POINTS_OF_FREE_COVERAGE_2026-08-22.md`
- *That replacing rather than blending is right.* Argued from the brain and supported by one
  HARD_FAIL (below) -- not proven.

### ⚖️ THE HONEST DEFLATION, WHICH MUST TRAVEL WITH ANY WRITE-UP
**Perceptual norms predicting semantic similarity is a KNOWN result in the literature. We have not
discovered embodiment.** What is new *for this project* is narrow and worth stating plainly: our
substrate has been working in a modality that measurably cannot carry the target, while an
admissible, already-on-disk, 100%-covering asset carries it far better -- and that asset was filed
as CLOSED.

---

## 4. ALREADY TRIED -- DO NOT RE-RUN THESE

- **Blending form into one combined query: `HARD_FAIL`.**
  `exp_substrate_concept_encoder_v2_vwfa_late_combine_2spoke` -- combined `recall@5 0.2000` vs
  `max(form 0.2533, semantic 0.1667)`: *"composition HURTS relative to best single spoke."*
  **Note the form spoke also BEAT the semantic spoke.** ⚠️ smoke, N=100, 3 seeds, `n_dim=2048`.
- **The same 11 sensorimotor dimensions were filed CLOSED** at `0.6039` against a `0.6791` bar --
  on a DIFFERENT instrument (pairwise similarity). On the better-posed pick-one-of-50 problem the
  same eleven numbers reach `0.6413`. **This is "do not generalise a narrow failure to impossible"
  paying out; do not re-close it on the old instrument.**
- **Divisive normalisation over a population pool: ANALYTICALLY IMPOSSIBLE.** The denominator is a
  scalar for the whole representation and cosine is scalar-invariant. `ORGAN_MAP` §3 says *"do not
  re-propose"* with a measured null. **Do not.**
- **Rank-1 common-mode removal / anisotropy: CLOSED HARD** (`DO NOT REDO 27`). The operation fully
  worked -- mean pairwise cosine `0.1427 -> -0.0004` -- for accuracy `0.6980 -> 0.6985`, and a
  RANDOM rank-1 direction gives the same `+0.0005`.
- **Second-order cosine ("do these two words keep the same company")** -- our semantic route's own
  operation -- **is WORSE than the raw count it is built from** on one instrument (`0.1506` vs
  `0.1859`). ⚠️ *A controlled 4-corpus re-run REVERSED this: second-order BEAT raw in 4 of 4. Treat
  the question as OPEN, and note the earlier claim is retracted.*

**Prior-work counts already run (2026-08-22):** `query "grounding"` 711 cells · `"encoder"` and
`"sensorimotor"` not yet queried by this brief -- **run them.**

---

## 5. VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

*Written because this project retracted, un-retracted and re-retracted one recommendation inside
three hours on the day this brief was written.*

```bash
python tools/before_you_start.py "wire sensorimotor norms as the meaning channel at read time"
python tools/experiment_index.py query "sensorimotor"
python tools/experiment_index.py query "norms"
python tools/organ_map_cite.py <organ you intend to touch>
python tools/cite_check.py 0.6413        # confirm the caveats above are still the source's caveats
```
**If any of these disagree with section 3, the disk wins -- say so in `SOLVED.md`.**

---

## 6. THE BAR

**Turn the ceiling diagnostic into a MECHANISM.**

- **An UNFITTED read-time mechanism** -- no model trained on the gold -- that uses the sensorimotor
  channel to choose a word's meaning **on the live reading path**.
- **Scored on held-out text**, CI-separated over **the strongest floor actually run**, gated on the
  **floor's upper bound** (floor + its own half-width), with the floor recomputed on this
  population and this representation.
- **The three controls that bound the existing result must be rebuilt and must still bind:**
  candidate-only (never sees the query), shuffled-query (pairing destroyed, marginals kept), and an
  **information-free version of your own winning arm** which must LOSE.
- **Report coverage.** What fraction of the words encountered have norms? That number is the
  finding if it is low.

### HOW WE WOULD KNOW IT FAILED -- pre-register which of these fired
- **(a)** The mechanism does not clear the floor's upper bound -> a real negative; go to the
  brain-fidelity drill and ask FIRST whether it could have succeeded.
- **(b)** It clears, but the information-free twin also clears -> artifact, not mechanism.
- **(c)** It clears on covered words and coverage is too low to matter -> **say so in the headline**;
  a gain on 30% of tokens is a 30% gain.
- **(d)** It only works FITTED -> you have re-measured the ceiling, not built a mechanism.

---

## 7. FILES AND ENTRY POINTS

- **The live reading path:** `hdlab/reading_grounding_loop.py`, `hdlab/substrate.py`
- **The meaning read-out to replace or bypass:** the accumulated-context-profile route
- **The form channel, already wired ADDITIVELY:** `form_identity_vector` -- **do not blend it into
  the meaning query**; it is a recognition index and its meaning path is barred in its docstring
- **The assets:** the sensorimotor/Lancaster norms and the learned encoder, both on disk, both
  unwired -- locate them via the registry rather than trusting this line
- **🚫 YOU DO NOT WRITE TO `hdlab/` -- THE LIVE SUBSTRATE (owner ruling, board Q111, 2026-08-22).** *Prove the mechanism in `experiments/` and `verification/`, then state in `SOLVED.md` exactly what would have to change in `hdlab/` and why. **The strategy session re-verifies and lands it, and is the sole writer there** -- two writers on one live file already destroyed a full day's audit here, silently.*

**🚫 DO NOT TOUCH:** `preregs/**`, any `arm_key*` file, `notes/STATUS.md`, the build plan, or
  another problem's folder. **The `== "UNK"` guard in the animacy path is a deliberate hand-off.**

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **Never place `0.6413` beside a live-substrate number without saying it is a FITTED CEILING
  DIAGNOSTIC on word-disjoint CV.**
- 🚫 **`0.3104` is one corpus, 538 target words, no CI.** The CONVERGENCE of two feature sets is the
  finding; the exact tie may be coincidence (a one-hit difference is 0.0019).
- 🚫 **Do not re-propose divisive normalisation or rank-1 common-mode removal.** Both closed, one
  analytically.
- 🚫 **Do not re-close the sensorimotor route on the pairwise-similarity instrument.** That is the
  narrow failure this result already escaped.
- ⚠️ **Supplied knowledge is ADMISSIBLE** (owner ruling) but it is SUPPLIED, not learned. Say which.
- ⚠️ **No external LLM at inference. Ever.** That invariant is not negotiable and not in scope here.
