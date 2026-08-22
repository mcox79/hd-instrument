# BUILD PLAN -- WHAT TO DO NEXT, POST-AUDIT. START HERE.

> # 📍 **STATE AS OF 2026-08-22. ONE BLOCK, CURRENT ONLY. DO NOT APPEND -- FOLD.**
> *This block has blown up THREE times (6,895 lines -> 309 -> 343) against a 160-line cap, every time by appending to a document whose own header forbids it. Consolidated 08-22. **Every entry cites the note holding its evidence; nothing is lost and `git log` has the full sequence.***
>
> ## 🔑 **THE MEANING ASSET IS NOT SHORT OF WORDS -- THE LOOKUP CANNOT INFLECT (08-22)**
> 🔑 **AND THE MEANING ASSET IS NOT SHORT OF WORDS -- THE LOOKUP CANNOT INFLECT.** `grounded_similarity.py:165` is `_table().get(word.lower())`, so we hold `country` and read past `countries`. **Token coverage `0.6035` -> `0.7350`, type `0.1027` -> `0.1633`** under our own `normalize_lemma` (landed cell reproduced to 4 decimals first as the control). **+13.2 points of running text, zero new norms = 44% of the way to the `90%` target** -- so **`+14,704 words to norm` counts inflected forms of ALREADY-NORMED words.** ⚠️ *~5 of 130 recoveries wrong; irregulars (`women`, `feet`) missed by both methods, so the ceiling is HIGHER.* 🚫 **COVERAGE, NOT CAPABILITY -- no task run, `grounded_similarity.py` deliberately UNCHANGED.** *Filed `notes/problems/lookup_does_not_lemmatise/`.* `THE_NORMS_LOOKUP_DOES_NOT_LEMMATISE_...`
>
> ## ✅ **THE 36-ITEM BANK IS NO LONGER THE BINDING CONSTRAINT -- v2 IS `124` SCORABLE AND BOTH CHEATS ARE DEAD (08-22, SOLVER, INTEGRATED)**
> **`experiments/data/goal_bearing_modern_eval_v2.jsonl` -- `166` items, `124` scorable, `3.4x` the old 36.** *Second solver problem closed; `eval_bank_too_small` was the one I was DISQUALIFIED from building, having read the per-item predictions.*
> ✅ **RE-VERIFIED BY ME ON THE ARTIFACT, NOT BY RE-RUNNING THEIR PIPELINE** (a re-run shares the pipeline's bugs): counts `166`/`124` MATCH, majority floor `0.605` MATCH (`unmet 75` / `met 49`), length independent of the label at permutation `p = 0.984` (theirs `0.988`).
> 🔑 **AND THE POSITIVE CONTROL IS WHAT MAKES IT MEAN ANYTHING: the same instrument run on v1's 36 reads `met 410.9` vs `unmet 340.3` chars, `+70.6`, `p = 0.0027` -- IT DETECTS THE CHEAT WHERE IT LIVES AND FINDS NOTHING ON v2. That `+70.6 / p=0.0027` reproduces TO THE DIGIT a measurement I took independently days before the brief existed.**
> 🔻 *Negation `p` did NOT reproduce exactly (mine `0.564`, theirs `0.844`) -- different last-sentence extraction; both far from significance so the CONCLUSION stands, but `0.844` is not a reproduced number.*
> 🎯 **DESIGN PROPERTY THE SUBMISSION DID NOT CLAIM: THE MAJORITY CLASS FLIPPED.** v1 was `64%` MET, v2 is `60.5%` UNMET. **v1's floor was "always say MET" -- the exact answer the organ systematically fails to give, so it could never clear its own floor. That coincidence is gone.**
> 🚫 **NO v1 RESULT BECOMES WRONG, AND v1/v2 NUMBERS MAY NOT BE COMPARED** -- different populations, different majority class.
>
> ## ✅ **Q113 ANSWERED 2026-08-22 -- THE BUILD LANE IS OPEN, AND THE PROBLEMS FOLDER IS NOT MINE**
> **Owner, verbatim: *"you can definitely start and run experiments and helpers. eliminate that line from your instructions. Remember that any 'problem' you have in the problems tab is going to be worked on, so try not to compete with that"*.**
> ➡️ **SO: cell work and `hdi_*` spawns are AUTHORIZED — the "the loop can only measure, document and guard" constraint is RETIRED.** *That premise was doubly wrong: Q109 retracted the `verification/` half, and this retracts the rest.*
> 🚫 **AND A NEW STANDING CONSTRAINT: THE SIX BRIEFS IN `notes/problems/` ARE THE SOLVER'S. DO NOT WORK THEM HERE** — `lookup_does_not_lemmatise`, `harness_cannot_recompute`, `substrate_never_resumes`, `reader_meaning_channel`, `flat_store_destroys_the_code`, `eval_bank_too_small`. *Filing a problem hands it away; the value I add after filing is integration, not solving.*
> 🎯 **THIS SESSION'S WORK IS THEREFORE WHAT IS *NOT* FILED:** re-landing the stale goal-bearing cell (dispatched), the `STATUS.md` structural split, tracing the short-read cause, and the B3'/Q3 scored paths.
>
> ## 🚨 **`Substrate.read(n_sentences=N)` DOES NOT READ `N` -- ASK FOR 8,000 AND GET ~1,000 (08-22)**
> **`read(3000)`, `read(6000)` and `read(10000)` ALL returned `1,060` sentences, the same 9 checkpoints and the same 30 consolidated terms.** Not one seed or dimension: asked `8,000`, every config stopped between **`960` and `1,500`**. **Successive calls degrade further -- `1,060 -> 240 -> 220`**, so three calls asking 8,000 each delivered `1,520` TOTAL. 🔻 **SILENT: no exception, no warning -- while `ReadResult.n_sentences` held the truth on the object every caller already had.**
> ✅ **GUARDED (`e335fa220`): `ReadResult` now carries `n_sentences_requested` + `short_read`, `read()` prints a stderr banner under 90% delivery, and it survives `to_dict()` into `metrics.json`.** *Warn not raise -- the results are REAL, only their DESCRIPTION was at risk. Controlled both ways; `verification/test_read_reports_short_reads.py` 3/3.*
> 🔻 **AND IT RETRACTS MY OWN GROWTH CURVE FROM THE SAME NIGHT: chunked reading did NOT grow consolidation to 180 by reading more -- each CALL buys a fresh smaller allowance. The "30-term consolidation cap" was the READ cap in disguise.**
> 🔻 **BLAST RADIUS ENUMERATED, AND IT DEFLATES THIS: NO EXPERIMENT CELL USES THE FAILING CALL SHAPE.** *14 literal call sites, only 2 over 1,500 and BOTH are the witness I wrote. All 16 variable sites bind `chunk = 400` and loop.* **The real pattern measured: 25 successive `read(400)` calls deliver `8,060 / 10,000` = `81%`** (short_read fired 13/25). ➡️ **So the honest impact is a ~19% shortfall on real cells, NOT ~87%. A cell reporting 40,000 sentences across 100 chunks probably read ~32,000.** 🚫 **DO NOT QUOTE THE `13%` AS OUR EXPOSURE -- it is the exposure of a call shape that appears nowhere but in its own test.** *Still not claimed: that any published number is wrong, or that the CAUSE is traced.* `SUBSTRATE_READ_SILENTLY_READS_A_FRACTION_...`
>
> ## 🔌 **THE 8 `NEEDS_ADAPTER` SLOTS, ENUMERATED -- AND THEIR BLOCKERS ARE NOT THE SAME KIND (08-22)**
> **`python tools/slot_status.py` (NEW, the SIXTH prior-work read; `substrate.py`'s slot table was searched by NOTHING in `tools/` or `verification/`).** Table is **28 slots: `9` FILLED, `8` NEEDS_ADAPTER, `8` EMPTY, `3` EXCLUDED** -- *four states needing different work; never collapse them into one "not done" count.*
> | slot | organ | what actually blocks it |
> |---|---|---|
> | **B3'** | `cortical_recall` | 🟢 **already CALLED; only NO SCORED PATH.** ✅ **08-22: it IS the consolidation-sensitive route -- ablating consolidation CHANGED the read on `8/8` probes, against a positive control where the same config twice is IDENTICAL `8/8`.** *The episodic routes were unchanged in 9 of 12 cells; that contrast is B3's whole reason to exist and is now demonstrated.* 🚫 **SENSITIVITY != CORRECTNESS -- the returned terms look unrelated (`water` -> `lory`/`lynde`/`swim`); no task, no floor, no CI.** `THE_CORTICAL_READ_IS_CONSOLIDATION_SENSITIVE_...` |
> | **Q3** | `cortex` | 🟢 has a written recipe: *"wire with `atom_consultation` OFF"* |
> | B5 | `sensorimotor_spoke` | combination rule **UNPINNED** -> a DESIGN decision, our-invention-under-test |
> | E2 | `situation_reader` | input SHAPE mismatch (reads a FILE, not the sentence stream) + 30 s import |
> | D2 | `ca3_completer` | ingest produces neither FHRR bundles nor per-spoke codebooks |
> | R4 | `prelim_tier` | needs `TierState` + a `cluster_key_fn` the ingest path does not define |
> | Q1 | `semantic_parser` | no fitted `IntentClassifier` artifact on the ingest path |
> | 🔻 **E3** | `coreference_resolver` | **NOT a wiring problem -- a VALIDITY one. Its `0.7193` vs recency `0.5614` is TRUE OF GOLD-ANNOTATED LITBANK and "does not transfer to raw prose".** Do not quote it as capability |
> ✅ *D2's row also claimed "UNTRACKED IN GIT" -- **a resolved hazard (Q66, fixed at `f102e7081`) left standing as live.** Corrected; `verification/test_slot_table_claims_are_true.py` 4/4 now checks the table's machine-verifiable claims and is positive-controlled against that exact defect.*
>
> ## ⛔ **AND THE WHOLE COVERAGE THREAD IS DOWNSTREAM OF A WIRING THAT DOES NOT EXIST (08-22)**
> **RUNTIME, positive-controlled: counters on `grounded_similarity` / `grounded_vector` / `_table` register `0` CALLS across a 150-200 sentence `read()`. THE NORMS TABLE IS NEVER EVEN LOADED.** *This confirms the substrate's OWN B5 slot entry -- "the organ EXISTS, self-tests... but `read()` does not consult it, so it is `NEEDS_ADAPTER` and not `FILLED`" -- which I read past while spending four continuations arguing the coverage case.* ➡️ **SO THE `+13.2` POINTS ARE REAL AND CURRENTLY UNREACHABLE: fix the lookup, re-run a reading task, and NO MOVEMENT IS THE EXPECTED RESULT, not a refutation.** 🔑 **THE BLOCKING PIECE IS B5's ADAPTER, and its hub-spoke COMBINATION RULE IS UNPINNED -- so any selection rule built on it is OUR-INVENTION-BEING-TESTED, not brain-derived.** 🔻 *Method error caught en route: my first two probes wrapped `grounded_similarity` and `_table` while `sensorimotor_spoke` imports `grounded_vector` -- **watching the wrong door.** Re-run wrapped and controlled; same answer, defensible reason.* ⚠️ *`recall_cortical` also read `0` in all three spaces, but its branch may not have been REACHED at 150 sentences -- a probe limit, NOT a finding.*
>
> ## 🔑 **THE VERB HOLE IS OURS, NOT THE ASSET'S (08-22) -- SUPPLY IS MOST VALUABLE EXACTLY WHERE WE ARE WORST**
> **SimLex, one scorer, only WORD CLASS changing, 400-shuffle nulls: the ASSET reads NOUN `+0.2745` (null `0.0732`) and VERB `+0.2607` (null `0.1241`) -- BOTH CLEAR, Fisher `z=0.192` NOT SEPARATED.** Not coverage either: **`3,487` of `3,500` SimVerb pairs = `99.6%`**, rho `+0.2676`. *Positive control `cos(w,w)=1.0`.* ➡️ **So against our LEARNED channel (noun clears `0.1310`, verb INSIDE its null): THE MEANING FOR VERBS IS AVAILABLE ON 99.6% OF PAIRS AND WE ARE NOT LEARNING IT.** 🧠 *ATL hub-and-spoke has verb meaning leaning on SENSORIMOTOR spokes rather than distributional company -- so a sensorimotor asset carrying full verb signal is expected, and a co-occurrence channel carrying none is too. **Our architecture reads text and expects verbs to fall out of it.*** ⚠️ **ADJECTIVES `+0.1472` inside a `0.1952` null at n=111 -- UNDERPOWERED, NOT a capability statement; UNRESOLVED.** 🚫 *Do not cross `0.2676` (3,487 pairs) with the archived `SUPPLIED 0.2983` (2,651).* `THE_VERB_HOLE_IS_OURS_NOT_THE_ASSETS_...`
>
> ## 📉 **THE LOOP'S OWN OUTPUT, MEASURED: `205` commits, **`3`** touched capability code**, 288 note-writes, **`16` of my own claims withdrawn.** Performance: we beat an UNTRAINED codebook by `+16.3 pp` (replicated) and **LOSE TO COUNTING ON 16 MEASURES**. *Commercial: not close; `55 of 210` organs on the live path.* `OWNER_ASSESSMENT_...` **Q108 WITHDRAWN (premise too broad -- `verification/` was open all along); Q109 narrowed it: THE LOOP CAN MEASURE, DOCUMENT AND GUARD; IT CANNOT RUN A CELL. So defects it finds get GUARDED, not FIXED.** *And see the top block: the second premise (agents disallowed) was false too -> Q113.*
> 🚫 **I AM A CONTAMINATED AUTHOR FOR THE EVAL BANK** -- I have read the per-item predictions, so hand-building gold here violates *did the test items exist before the mechanism did?* The 08-06 build used four independent surveyors fixing gold by entailment BEFORE any organ ran.
>
> ## 🏗️ **OPERATING MODEL (OWNER 08-22): STRATEGY SESSION + SOLVER SESSIONS, MACHINE-CHECKED HAND-OFF**
> **Owner:** *"keep the long vision and longterm strategy here... I'll have a separate session dig in to specifically solve those problems... you keep the 10k view and integrate solved issues."*
> ✅ **BUILT:** `notes/problems/README.md`, `SOLVER_SESSION_PROMPT.md` (on disk -- chat does not survive compaction), `tools/problem_ledger.py` (**REFUSES a `SOLVED.md` with no floor or no controls**; self-test 7/7), `verification/test_problem_briefs_and_flags.py` 5/5, and **SIX briefs**.
> ✅ **Q111 ANSWERED: THIS SESSION OWNS ALL INTEGRATION; SOLVERS NEVER WRITE `hdlab/`.** *Owner: "if we fracture our live substrate modification I fear we'll lose sight of state."* Hand-back = a result plus a PROPOSED change; I re-verify and land it. *Corrected in all briefs + protocol + prompt the same hour.* 💡 *Owner floated a SECOND substrate for the research session -- parked until the loop has run once.*
> 📋 **QUEUE:** `stored_terms_are_stems` (**SOLVED, integrated**) · `reader_meaning_channel` (flagship) · `lookup_does_not_lemmatise` (**new, 08-22**) · `flat_store_destroys_the_code` · `substrate_never_resumes` · `eval_bank_too_small` (**I am disqualified**).
> 🔑 *"Read-out discrimination" was MERGED into `reader_meaning_channel` rather than written -- same task, two names; writing both would have handed two sessions identical work.* 🚫 **CLOZE framing stays RETIRED (ceiling `0.0300` vs our `0.0150` -- a tie with word-counting).** ⚠️ *Reader and store COUPLE: fix the store first and you preserve a code with no meaning; fix the reader first and the store destroys it.*
>
> ## ✅ **FIRST PROBLEM SOLVED AND INTEGRATED -- `stored_terms_are_stems`, PARTIAL, UPHELD**
> 🔑 **THE STEM DAMAGE IS A STALE DATA ARTIFACT, NOT A LIVE DEFECT.** `normalize_lemma` (`reading_grounding_loop.py:230`) was an UNGUARDED suffix stripper until `01093ac1f`/`7d6036bca` added `is_known_word(residue)`; **`v2_qualityfix` was built the day BEFORE.** *Runtime: the pre-fix function turns **8,692** dictionary words into non-words, reproducing the repair commit's `8,692 -> 0` exactly.* **Stale `119/1512 = 7.87%` vs fresh HEAD `0/141 = 0.00%`.**
> ✅ *Independent spot-check on the owner's 13 words: all untouched except `arteries -> artery` -- correct, and the positive control for "prove you did not break lemmatisation". Nothing changing at all would have been the suspicious result.* ✅ *The solver's detector caught its OWN false positive (`and -> andes`) -- a negative control firing on its author.*
> 🔻 **`7.9%` MAY NOT BE QUOTED AS A SYSTEM PROPERTY** -- it is one stale artifact; any grounding number computed on `v1`/`v2q` inherits it and must say so.
> 🎯 **DECIDES A COUPLING: the two resumable snapshots ARE the two pre-fix ones, so "load an old foundation" feeds `7.87%` junk into the anchor pool `substrate_never_resumes` exists to measure. FIRST MOVE THERE: BUILD A CLEAN SNAPSHOT, do not load `v2q`.**
>
> ## 🚨 **THE OWNER HAND-SCORED THE BLIND SHEET (08-22). MY DIAGNOSIS WAS WRONG THREE TIMES, IN ALTERNATING DIRECTIONS.**
> *Owner: "a lot of words there are missing letters, and a lot of them unrelated." Scored `75` of `150`: `1` MEANINGFUL, `15` RELATED, `31` NOISE.*
> 🔻 *C1: I reported `24%` not-words, **2.3x overstated** -- "not in WordNet" counts real words WordNet lacks (`archaea`, `adipocytes`, `Abdullah`). **Round-trip test** (stemmer output iff NOT a word AND a plausible suffix makes one) gives sheet `10.4%` / v2q `7.9%` / v5 `0.4%`.* ⚠️ **TRAP: v5 has the HIGHEST not-a-word rate and LOWEST stem rate -- a cruder detector would have scored the FIXED foundation WORST.**
> 🔻 *C2 (withdrawn): "the stem repair already shipped".* 🔻 *C3 REINSTATES the finding: all NINE foundation dirs were written `2026-08-12`, THE SAME DAY, and only `v1`/`v2q` are LOADABLE -- `v3/v4/v5` lack all four artifacts `load_foundation` needs, so they are **a different pipeline's fact dumps**, not later versions. The `0.4%` is definitional extraction's DEFINIENDA; the `7.9%` is the grounding loop's SUBJECTS -- **I invoked no-number-crosses-populations twice that day and then broke it.***
> ✅ **STANDS: the grounding loop stores ~`8%` STEMMER OUTPUT AND IS NOT KNOWN TO BE FIXED.** Only the `24% -> 10.4%` deflation survives from C1. `THE_GROUNDING_LOOP_STORES_8pc_...`
>
> ## 🚨🧠 **NOTHING LOADS A FOUNDATION -- THE SUBSTRATE IS PINNED IN COLD START**
> ✅ **RE-TESTED AS STATED AND FIXED 08-22 (`7a810a34b`): a descriptor recording every READ shows `self.foundation_dir` read `0` times across construction + a 120-sentence read** *(positive control: a deliberate read IS seen)*, **and NO CALLER ANYWHERE PASSES THE ARGUMENT.** ➡️ **`Substrate(foundation_dir=...)` now RAISES instead of accepting a path and ignoring it** -- safe because nobody passes it, `None` unchanged, `verification/test_foundation_dir_does_not_lie.py` 3/3 pins the refusal AND the zero-read measurement so wiring loading up fails it on purpose. 🚫 *Still NOT a claim that resuming helps.*
> **RUNTIME, not grep:** counters on `load_foundation`/`save_foundation`, `foundation_dir` set to v5, 120 sentences -> **`load_foundation` calls `0`; store facts `92` -> `92`, the `92` deriving from the `107` SEED WORDS. `self.foundation_dir` is assigned at `substrate.py:378` AND NEVER READ AGAIN -- THE PARAMETER IS DEAD.** ✅ *Enumerated with comments separated from calls: 6 files, only live-path hit is a COMMENT at `reading_grounding_loop.py:1732`.* 🔻 *Grep got it wrong BOTH ways first -- the documented trap, on the module the rule was written about.*
> 🎯 **MAKES THIS PLAN'S OWN PREDICTION UNREACHABLE: the `way`-attractor (`17.7%` of grounded terms) was predicted to FALL as vocabulary grows. IT CANNOT GROW ACROSS RUNS. The degeneracy is ARITHMETIC, not tuning or scale.** 🧠 *Consolidation is DEFINED by persisting across episodes; we have no slow store at all -- the persistence half of the 08-19 replay gap, one dead attribute wide.*
> ⚠️ **NOT MEASURED: whether loading helps. THAT IS THE EXPERIMENT.** 🚫 *Do not quote `92 -> 92`; 120 sentences is below the 100-400 grounding threshold.* `THE_ASSEMBLED_SUBSTRATE_NEVER_LOADS_A_FOUNDATION_...`
>
> ## 🧠 **Q102 -- THE FORM ORGAN: WIRED ADDITIVELY, AND BOUNDED BY MEASUREMENT**
> ✅ **RECOGNITION: IT DOES THE JOB.** Right lemma from a MISMATCHED surface form (`cats`->`cat`) hit@1 **`0.0053 -> 0.9645`** (n=564 pairs/400 lemmas, chance `0.0025`); live hash AT CHANCE. Meaning channel `+0.095782`, untouched. *Wired beside `symbol_vector`, `symbol_vector` BYTE-IDENTICAL (no store invalidated), relation labels still hashed, witness 6/6, registry 211 rows.*
> ⛔ **MEANING: IT DOES NOT, AND THE PATH IS BARRED IN THE DOCSTRING.** Masked context bag `+0.0573` INSIDE its own null p95 `0.0716`; **its PERFECT version is also a null -- lemmatising the bag (the lossless merge that UPPER-BOUNDS a form code) reads `-0.0351` at d=1024, CI `[-0.0921, +0.0218]`, on 21.8% of tokens (3,018/13,824).** *Prediction written before the run and FAILED.* 🚫 *Verb cell `+0.1071` inside its own `0.1372` null.*
> **ONE REPRESENTATION, TWO JOBS NEEDING OPPOSITE THINGS:** meaning needs the word DELETED from its sentence (else grounding learns "artery means artery"); identification needs it PRESENT. **masked hit@1 `0.1417` vs unmasked `0.4750`, chance `0.0167`.** ➡️ **THE BRAIN DOES NOT FACE THIS -- VWFA and ATL hub+spokes ARE SEPARATE SYSTEMS.** *Form invariance is an IDENTITY property; the VWFA FEEDS lexical access rather than being it.*
> ✅ *RISK DISARMED: form channel `rho -0.0259` (p=0.41, n=999) on SimLex meaning, INSIDE the shuffled null `-0.0172..+0.0426` -- safe as a SEPARATE channel, clearly wrong to BLEND.* ✅ *Prior work confirms the do-not-blend half: `..._vwfa_late_combine_2spoke` **HARD_FAIL**, late-combine `0.2000` < form-alone `0.2533`.* 🚫 **SCOPE: that cell's population is the SimLex+WordSim list, "may not be quoted as such"; do NOT swap `0.2701` with its `0.2449` CI `[0.1830,0.3036]`; WordSim353 `0.4093` is a THIRD population.** `ONE_REPRESENTATION_TWO_OPPOSITE_JOBS_...` `FORM_INVARIANCE_CANNOT_BUY_MEANING_...`
>
> ## 🔎 **THE GOAL-BEARING LINE -- WHERE THE WALL ACTUALLY IS**
> 🔻 **Q104 WITHDRAWN: the credit mechanism is ALREADY role-based.** `_credit_targets` bounds each verb's own clause and excludes bystanders STRUCTURALLY. *Run, not read: "the girl stumbled badly and the man laughed loudly" -> girl `['stumble']`, man `['laugh']`.*
> 🎯 **THE REAL EXPOSURE WAS THE MORPHOLOGICAL GATE** `_is_verblike`: **recall `0.6026` -- `3,528` of `8,877` real verbs NEVER SEEN**; precision `0.4718` (`0.5816` excluding the AUX convention). **The missed verbs are the exact words Q104 named -- right population, BACKWARDS direction.**
> 🔻 **THE SWAP MOVED THE WALL TO EXACTLY ITS FLOOR AND THE PAIRED TEST REFUSED IT.** `HD_VERB_GATE=tagger` -> `0.4722 -> 0.6389` = **exactly the majority floor**, so still `HARD_FAIL`. *Not a majority collapse (`met 16/23`, `unmet 7/13`).* **McNemar exact `p = 0.1460`, `9` fixed / `3` BROKEN -- the intervention CHURNS.** ✅ *SURVIVES: it changes DECISIONS (12 of 36 flipped) where the `lemma_verb` repair changed only LABELS. `per_item_predictions` now ships.*
> 🔑 **THE FINDING WAS THE COLUMN I WAS NOT READING: MET recall `8/23`, `7/23`, `8/23` -- INVARIANT across a 7x lexicon-size change, 96%-vs-50% polarity, and learning-vs-none. ALL movement is in the UNMET column.** *Scored the maps rather than asserting: EMPTY `0.3889` / AND-gate BALANCED `0.3056` (WORST) / SOFT-COMBINE 96%-NEG `0.4722` (BEST) -- **the skewed map WINS; the NEG collapse is not what costs accuracy.*** ➡️ **RETIRES credit assignment AND the light-verb wash-out as bottlenecks.**
> 🔑 **AND IT IS NOT ANSWERING WRONG -- IT IS NOT ANSWERING.** OOV 36, empty overlay: accuracy `14/36 = 0.3889`, `NONE` `20/36`, **accuracy WHEN IT COMMITS `14/16 = 0.8750`, genuinely wrong `2/36`.** ➡️ **A COVERAGE FAILURE, NOT A DISCRIMINATION FAILURE** -- converging with the 08-07 charter's *"HIGH-PRECISION + COVERAGE-LIMITED; coverage is the universal wall."*
> 🔻 **SUPPLYING THE WORD CONVERTS SILENCE INTO GUESSING: in-lexicon 8 score `4/8 = 0.5000` against a BALANCED `0.5000` floor.** ⚠️ *n=8 can demonstrate competence, NOT incompetence -- declared BEFORE running; INCONCLUSIVE, not a negative.* 🔑 *Structural fact: "the 36-item bank" is the `outcome_in_lexicon is False` subset of the 44-item `goal_bearing_modern_eval_v1`, not a separate bank.*
> 🔻 **TWO RETRACTIONS ON THE REPO'S OWN CONVENTION: `AMBIGUOUS` is an ABSTENTION here** (`verify_levin_lastresort_backoff.py:51`). *So abstention is `2/8`, Fisher `p = 0.2404` NOT `0.0049`; and precision is `0.8182` -- **there is NO precision regression**, and an existing guard pins `(17,4,23)` and PASSES.* 🔑 **The number passed a positive control, a pre-registration and a power calculation, and broke on a definition I never looked up.**
> 🚨 **A REAL DEFECT BEHIND IT: the landed cell scores abstentions as ERRORS, BY OMISSION.** *`AMBIGUOUS` abstains in 5 consumers including `hdlab/consequence_learning_loop.py` itself; it is a wrong answer in exactly one -- the cell the whole line is graded on, whose `_score` does `ok = (pred == gold)` and never mentions the word.* ✅ **NOT bitten today (OOV 36 has zero `AMBIGUOUS`); it would be wrong on the in-lexicon 8.** ✅ **GUARD: `tools/score_with_abstention.py`, no signature returns a bare accuracy, self-test 6/6, and it FAILS the day the population acquires an `AMBIGUOUS`.**
> 🚨 **THE LANDED RECORD IS STALE IN A WAY THAT CHANGES THE DIAGNOSIS: the `HARD_FAIL` was measured where the cascade fired `0` of `36`.** *From the landed run's OWN `units.jsonl`, no re-run:* **landed `0.1667`, `NONE 29/36`, firings `0`; today `0.3889`, `NONE 20/36`, firings `10`, correct `9`.** 🚫 **VERDICT UNCHANGED -- still far below the `0.6389` floor.** ➡️ *So the structural-rule analysis (~20 firings) CANNOT describe the landed run.* 🎯 *Free third point: firings/correct `0/0 -> 10/9 -> 19/10` = **DECLINING MARGINAL PRECISION** (hypothesis; crosses conditions).* ⚠️ **RE-LANDING NEEDS A CELL RUN.**
> 🔻 **THE ARCHIVE WAS AHEAD OF ME: attacking that abstention has been tried TWICE and bought `1` of `23`.** *`exp_verbclass_backoff_coverage_v1` `HARD_FAIL` (held-out `4/8` vs bar `6/8`); `v2` `PARTIAL`, `na 23 -> 22`.* 🚫 **Do not re-propose "supply verb-class knowledge so the cascade can decide".** ✅ *Their shared 08-07 baseline independently replicates the profile 15 days earlier: `17`/`4`/`23`, precision `0.8095`, abstaining on `52.3%`.* ⏱️ *Dates the staleness to a ONE-DAY window: 08-06 had `0` firings, 08-07 already shows `referent_mismatch` firing.*
> 🎯 **CEILING ARITHMETIC POINTED AWAY FROM THE OBVIOUS TARGET:** `referent_mismatch` returns `UNMET` in **8 of 8** -- a DEFAULT, not an inference -- **but its ceiling if made PERFECT is `0.6111`, BELOW the `0.6389` floor.** ✅ *Only tier that clears: `abstain_fallback_to_lexicon`, n=16, ceiling `0.7500`.* 🚫 **DO NOT repair `referent_mismatch`.**
> 🔻 **AND "MAKE THE CASCADE FIRE" IS RETIRED: when it DOES fire it is `10/19 = 0.5263`, binomial vs a coin flip `p = 1.0000`.** **COVERAGE WITHOUT DISCRIMINATION BUYS NOTHING.** ⚠️ *n=19: "never demonstrated to discriminate", NOT "proven equal to chance".*
> 🔑 **AND NO RULE EVER JUDGES AN ITEM -- EVERY STRUCTURAL RULE EMITS A CONSTANT:** `same_class_same_referent` -> `MET` x9 (`7/9`, the one working part); `referent_mismatch` -> `UNMET` x8; `opposed_class` x2; `grounded_result` x1. **ALL SIGNAL IS IN *WHICH RULE FIRES*, and the UNMET branches run `4/11` = WORSE THAN SILENCE.** 🚫 *"Flip them to MET" REFUSED -- `0.5556`, still below floor, and it FITS THE TEST SET.*
> 🧠 **ROOT CAUSE, HAND-READ: in all 5 `referent_mismatch` errors someone ELSE performs the act** (*the Wizard gives the Scarecrow brains; Jo drags the rail for Amy*). **The goal-holder is RECIPIENT / BENEFICIARY -- never SUBJECT or DIRECT OBJECT, and `goal_typing.py:776-777` implements exactly those two.** ➡️ **MISSING PRIMITIVE: a project about GOALS omits the role meaning "the one it was for".** ⚠️ **THE CAUSAL CLAIM IS UNCONFIRMED -- I hand-read it while holding the hypothesis and BOTH objective tests failed to test it** (one measured whose OUTCOME it is, not who ACTED; the other hit `NO_VERB_FOUND` on 22 of 36). **The code gap is established; the causal story is not.**
>
> ## 🚨 **FLOORS NOBODY HAD RUN -- AND THEY INVALIDATE PAST GRADES ON THIS LINE**
> **A ONE-LINE NEGATION COUNTER SCORES `0.8056` WHERE THE FOUR-TIER CASCADE SCORES `0.4722`.** *Counting `no|not|never|n't|failed|refuse` in the FINAL sentence; permutation null p95 `0.6944` with best-`t` recomputed INSIDE each permutation. MET items average `0.04` cues, UNMET `0.69`. Monotone decay by window (`0.8056/0.7778/0.6944/0.7222/0.7222`) -- localised, not a knife-edge fit.*
> 🚫 **NEVER SHIP IT: a lexical cue detector is the word-counting pattern; such a result RAISES THE BAR rather than becoming the mechanism.** ✅ *What it proves: the evidence IS in the text, in plain words -- **the machinery is not missing information, it is failing to use information that is right there.*** 🔻 *Real weakness: the null prices THRESHOLD but not FEATURE/WINDOW selection, and I chose both after reading the failing passages -- safe as a FLOOR, fatal in a treatment.*
> 🚨 **`tools/floor_battery.py` (12 baselines, permutation null each) IMMEDIATELY FOUND A LENGTH CONFOUND: `text_length_chars` ALONE scores `0.8056`; MET passages are `+70.6` chars = `+20.7%` LONGER, `p = 0.0027`.** ✅ **BUT OURS DOES NOT EXPLOIT IT -- `0.4722` is below ALL 12 baselines: the organ is not cheating, it is failing to use signal a ruler picks up.**
> ✅ **LENGTH-MATCHED CONTROL (13/13 nearest-length pairs): `text_length` COLLAPSES to its own null (`0.7308`) -- the control demonstrably worked -- while NEGATION SURVIVES (`0.7692`). The organ moves `0.4722` (floor `0.6389`) -> `0.5385` (floor `0.5000`): below-floor to AT floor, a ONE-ITEM margin on n=26.** ➡️ **THE WALL IS NOT A MEASUREMENT ARTIFACT.** ⚠️ *`clears_majority` alone FLATTERS -- `quote_marks`/`comma_count` "beat the majority" at `0.7222` while sitting EXACTLY at their own null; every row now carries `clears_own_null`.*
>
> ## 🗺️ **THE GROUNDING MAP -- `185` LABELS -> `7` EVIDENCED ROWS -> `4` DISTINCT RESULTS**
> **`711` grounding cells with a `metrics.json`; `185` verdict HARD_PASS; 🔻 `7` carry BOTH a CI and a null; `4` distinct at full scale.** ✅ **THE FOUR:** `reading_grounding_loop_cycle2` (foundation `185 -> 3,544` in one cycle, scramble `0.077`); `foundation_validation_harness_v1` (mechanism `1.0` vs **scramble `0.0` AND ablation `0.0`** -- the cleanest control result in the set); `v4_proximity` (gap `0.2667` over a frequency floor `0.22`); **`graded_divisive_comparator`** (n=4,000, `0.6395 -> 0.6997`, **d `0.0602` CI `[0.0440,0.0762]` EXCLUDING ZERO** -- best-evidenced number in the archive, and a DISCRIMINATION gain, NOT a capability).
> 🚨 **A WARNING THE GATE IS STRUCTURALLY BLIND TO: `context_conditioned_near_neighbour_v1_SMOKE_n600` = HARD_PASS while the FULL run = `MIDDLE_BAND_FLOOR_HUGGING`.** *Anyone counting HARD_PASS rows gets the SMOKE's answer.* ⚠️ **The other `178` are NOT refuted -- they are UNEVIDENCED IN THE FILE.**
>
> ## 🔻 **THE AUTOMATIC QUALITY CRITERION IS REFUTED -- "FOUNDATION VALIDATED" MUST BE RE-WORDED**
> **Same `100` blind human-scored rows, harness's own `cooccurs()` IMPORTED:** human GOOD `19/22 = 0.864` vs human NOISE `67/78 = 0.859`, **difference `+0.0047`, Fisher `p = 1.0000`. THE CRITERION CANNOT TELL MEANING FROM NOISE.** ✅ *What STANDS: facts DO beat random decoys (`0.860` vs `0.710`) -- but the gap is IDENTICAL for noise and meaning, so it certifies TOPICAL ADJACENCY, which is what a reader calls NOISE (`whisky->wedding`).*
> 🔻 *A GRADED count IS monotone (`8.0 > 4.0 > 2.0`, rho `+0.2279` p `0.0349`) -- **but I ran five tests, Bonferroni `p = 0.1745`: the result did not survive the search that found it.*** ✅ *Frozen into `tools/graded_cooccurrence_quality.py`: one measure, one test, **required n=150 below which it REFUSES to be read**.*
> ✅ **AND THE ANSWER WAS ALREADY ON DISK: `v4`'s PROXIMITY criterion WORKS -- GOOD `0.591` vs NOISE `0.244`, Fisher `p = 0.0038`, surviving Bonferroni x7 (`0.0266`), rejecting `76%` of human-NOISE while keeping `59%` of human-GOOD.** ➡️ **THE DECIDING DIFFERENCE IS PROVENANCE: `PROXIMITY_WINDOW=6` came from corpus structure BEFORE any result existed and was tested ONCE.** 🔑 *`v4` is the THIRD repair attempt and its docstring already said same-sentence-anywhere is insufficient -- **validated against a frequency floor and never against a person**; that check took twenty minutes.* ✅ **WIRED: `hdlab/quality_proxy.py`, witness 3/3, registry 211 -> 212.** 🚫 **A BETTER RULER, NOT BETTER FACTS -- the blind score is still `3/19/78`.**
> 🔻 **TWO CALIBRATION TRAPS, BOTH SHUT:** *(a) inverting the proxy's pass rate on a NEW foundation gives `74%` meaningful against a directly measured `22%` -- a `3.4x` error; **a filter's hit rates are properties of the DISTRIBUTION, not constants of the filter.** (b) The `3/19/78` sample passes at `0.3200` where full foundations pass at `0.5683`/`0.5016`, CIs NOT overlapping -- it was drawn `50/50` ACROSS TWO ARMS, **built to measure a DELTA, not a LEVEL**, and I had put it in `STATUS.md` as the foundation's quality.* ➡️ **THE FOUNDATION-WIDE MEANINGFUL FRACTION IS UNMEASURED.**
> ✅ *`tools/draw_representative_blind_sample.py` draws uniformly, strips provenance, and REFUSES a sample whose proxy pass rate drifts >`0.12` from its population. DRAWN AND WAITING: n=`150`, drift `0.0584`, seed `20260822`.* 🚫 **I WILL NOT SCORE IT -- whoever draws a blind sample must not label it.**
>
> ## 🔧 **ENGINEERING + VERIFICATION (08-22)**
> 🚨 **`import hdlab.reading_grounding_loop` SILENTLY REWROTE `sys.stdout`'s ENCODING AND SET `OMP_NUM_THREADS=1` PROCESS-WIDE**, by dragging in 9 experiment cells. ✅ **FIXED after a reach analysis changed the job's shape: `hdlab.learner` ALONE pulls all 8 and one file is the SOLE GATEWAY** -- `learner/registry.py` now builds a lazy name->module map. *After: `0` cells, `MUTATED: False`, order preserved; test 5/5 in a FRESH INTERPRETER.* ⚠️ **THE COUPLING REMAINS: `6` hdlab files import `13` experiment CELLS, undeletable and unmarked** -- guarded by a test that re-derives the list FROM SOURCE.
> 🚨 **THE CERTIFICATION GATE WAS DEAD FOR TWO DAYS WHILE ITS OWN REPORT OPENED WITH `RESULT: PASS`** -- a module-level `raise SystemExit` under a `test_*` name aborts the pytest session; the PASS line printed BEFORE the crash. ✅ **FIXED (neither step a narrowing): collection now succeeds, `458` tests, ZERO errors.** ✅ **TRUE STATE: `96` files, `403` test functions + `32` witnesses, ZERO GENUINE FAILURES.** *The one real failure was a STALE EXPECTATION -- **the system improved and the test failed.***
> 🔻 **SIX SELF-INFLICTED MEASUREMENT ARTIFACTS, EVERY ONE MINE:** *counting `exit 0` as a pass when **35 files run NOTHING** (285 functions scored as passing without executing); a zero-byte file on timeout; three "TIMEOUTs" that were CONTENTION with my own sweep; two "crashes" that were my own `timeout` killing the process group.* ➡️ **A MEASUREMENT HARNESS NEEDS THE SAME CONTROLS AS AN EXPERIMENT.**
> 📐 **REACHABILITY AT RUNTIME: live closure = `45` hdlab modules. Of `94` rows claiming NOT-reachable, exactly ONE looked live -- and it was MY OWN row, a granularity artifact.** ➡️ *~`94` + `25` ISLAND -- roughly HALF of `212` registered -- built and not reached. Not automatically waste; it IS the honest denominator.* 🚫 *The `11.4%` disagreement is a CEILING, not an error rate.*
>
> ## 🎯 **AN ORGAN SCORES `48/48` ON ITS CONSTRUCTED BANK AND `0.6136` ON REAL PROSE**
> **`hdlab/goal_owner_select`: `48/48` constructed, `12/12` multigoal -- and `27/44 = 0.6136` on the real bank, against floors in the bank's OWN baselines file: `first_mention` **`0.7955`** · `majority` `0.7273` · **OURS `0.6136`**.** 🔻 *Corrected within the hour from `0.5682`: I scored against `goal_owner` (who WANTS it) where the baselines mean `gold_outcome_owner`. **The exact tie with `recency` was an artifact of that wrong field -- I built an analysis on a coincidence I manufactured.** Second gold-field error this session, and this one gave a PLAUSIBLE number, which is worse.*
> 🔑 **WHY IT WAS NEVER SEEN: the organ's witness is thorough and PASSES -- but all of it is about *CHANGE*, not *LEVEL*. Nothing in it computes accuracy, and the floors live in a DIFFERENT FILE. TWO HALVES IN ONE REPO, NEVER MULTIPLIED TOGETHER.**
> 🔻 **THE SYSTEMIC VERSION IS REFUTED AND I FILED IT AS A NEGATIVE:** *across 96 verification files, `48` name a floor, `31` name only CHANGE, `17` neither -- **but `32%` is NOT a defect rate**: many are PLUMBING where a floor is meaningless, and the promotion-witness convention here is DELIBERATELY a non-drift check.* ➡️ **The accurate question is not keyword-answerable: *which POPULATION was this organ's level established on, and has it been re-measured on real text?*** ✅ **GUARD: `tools/gold_field_guard.py`, positive-controlled on the real miss.** 🚫 *`48/48` may NOT be quoted as owner-selection ability.*
>
> ## 🔻 **CLOSED DOORS -- DO NOT REOPEN WITHOUT READING THE NOTE**
> 1. **CA3 cannot complete** -- our rule MERGES correlated memories (margin `-0.1021`; local error-driven rule fixes it to `+0.0975`). ***BUT REAL WITHIN-LEMMA OVERLAP IS `0.0056` vs A `0.22` FAILURE THRESHOLD -- the regime never occurs, so DO NOT BUILD IT.***
> 2. **Surprise cannot gate writes** -- real spread (sd `0.096`) but UNCORRELATED with value (r `+0.238`, spans zero). ***Gating on an uncorrelated signal IS gating at random.***
> 3. **12-dim feature context is FLAT** -- `0.0266` at L=37 vs incumbent `0.1328`; NORMS12's own note predicted it.
> 4. 🚫 **ANISOTROPY / rank-1 removal: CLOSED HARD.** *Removal fully worked (`0.1427 -> -0.0004`) for accuracy `+0.0005`, and **a RANDOM rank-1 direction gives the SAME `+0.0005`** -- perturbation, not decorrelation-that-helps.* ⚠️ *The revival `*` is for FULL-COVARIANCE WHITENING, which this closes in NEITHER direction.*
> 5. 🚫 **DIVISIVE NORMALISATION: do not re-propose** -- analytic, the denominator is a scalar and cosine is scalar-invariant.
>
> ## 🌙 **THE 08-21 MEASUREMENT PASS -- ALL BAG-OF-WORDS; KEPT AS FLOOR, NOT DIRECTION**
> | finding | the number |
> |---|---|
> | **VERBS** | `+0.0000` on SimVerb's 2,651 pairs (null `0.0372`) and `-0.0002` on SimLex's 203, while NOUN `0.1310` clears its `0.0843` null. **WEAK ON NOUNS, ABSENT ON VERBS.** Coverage cutoff DISCHARGED to 97% of verbs. `COUNTING raw 0.0025 \| +idf 0.0689 \| OURS 0.0000 \| SUPPLIED 0.2983` -- our zero is a REAL DEFICIT, but every text arm is 4.3x below the human-rated one. 🚫 **SUPPLY != LEARNING.** |
> | **THE FLOOR** | `raw counting 0.0885 \| OURS 0.1071 \| ours+drop 0.1558 \| **idf-counting 0.1835** \| supplied 0.2876`. **`IDF - OURS = +0.0764` CI `[+0.0263,+0.1278]`.** 🚫 **ANY CLAIM MUST CLEAR `0.1835`.** |
> | **LEVERS, CLOSED** | more sentences saturates by ~10 (live median ~10); more dimensions buys IDENTIFICATION not MEANING (`1024-256 = +0.0127`, SPANS ZERO); combining channels `+0.0035` despite rho `0.0901` independence; accumulation rule NULL; PC removal, graded/signed, metric change all closed. |
> | **WITHDRAWN** | *drop-ubiquitous (`d=256 -0.0050`, `d=1024 +0.0434`, neither excludes zero); two weighting schemes `~+0.03` in-sample, neither separated; 12-dim verb dissociation (superseded by 3 AFFECT dims beating all 12).* |
> | 🔧 **PROCESS** | **9 PRIOR-WORK CATCHES** (3 in the docstring of the thing I was changing) -> new reads `symbol_corrections.py` (3.8% base rate) + `cite_check.py`. **THE SHELF IS 28 CORPORA / 286,069 SENTENCES, not the 9 my alphabetical cap showed** -- **and THE LIVE READER STILL WALKS IT ALPHABETICALLY: 8 of 28 opened, all textbooks unreached.** |
> `ON_VERBS_...` `COUNTING_WITH_ONE_STANDARD_WEIGHTING_...` `THE_LIMIT_IS_DIMENSIONAL_...` `SUPPLIED_BEATS_LEARNED_2_69x_...` `THE_SHELF_IS_28_CORPORA_NOT_9_...` `THE_READER_STILL_WALKS_...`
>
> ## ⚠️ **OWNER-FACING: `BOARD.md` IS A MIRROR AND EDITING `STATUS.md` DOES NOT REFRESH IT**
> *It carried "BOARD: NOTHING OPEN" for ~2 hours beside its own table of 2 open rows.* ➡️ **A doc MIRRORED by code goes stale silently, and the stale copy is the one the owner reads.** **RUN `python tools/board.py sync` AFTER EVERY `STATUS.md` EDIT.**
>
> ## 🧭 **METHOD -- THE RULES THAT PAID OUT**
> ***PUT A NUMBER BESIDE ANOTHER NUMBER THAT CONSTRAINS IT*** *(killed 5 claims, cleared 3);* **QUOTE THE NOTE, NEVER THE HEADLINE;** **CHECK PRIOR WORK FIRST** *(changed the answer 3x that night and 5x since);* ⭐ **MAKE THE ARITHMETIC CLOSE TO THE REPORTED NUMBER** *-- three plausible stories died to that one check, which was available every time and which I never ran.*
> ## ➡️ **NEXT -- 2026-08-22 (3rd consolidation). THIS SECTION IS ACTIONS; CLOSED WORK IS ONE LINE EACH BELOW.**
> 🔻 *Its previous form was 47 lines of seven STATUS REPORTS under a heading saying "THIS IS WHAT TO DO" -- and contained no action at all. Folded to numbers + a real list.*
>
> **DO NEXT, and none of these is in `notes/problems/` (those are the solver's):**
> **A.** 🟢 **Score the goal-bearing organ on the v2 bank (`124` scorable).** The n=36 constraint that capped every margin on this line is gone; the organ's level on v2 is UNMEASURED. *Cell run -- authorized by Q113.*
> **B.** 🟢 **B3' -- build the SCORED path for `cortical_recall`.** It is already CALLED and demonstrably consolidation-sensitive (`8/8` probes); what is missing is a task with floors. **Measure POOL SELECTION, not just ranking** -- the within-pool ranking read `+0.0675` NOT_SEPARATED, while consolidated-vs-not read `+0.1514` at n=24.
> **C.** 🟢 **Q3 `cortex` -- it ships with a written recipe: "wire with `atom_consultation` OFF".** Its probe already reads monotone confidence `1.0 -> 0.0256`, `11/11` distinct, so the live-or-inert question is answered.
> **D.** Fold this state block properly (`206` lines vs a `160` cap) -- the residue is v1-era detail, superseded in PRIORITY but not WRONG, so it folds to pointers rather than deletes.
>
> **CLOSED, ONE LINE EACH -- numbers kept, reasoning in the named notes:**
> **1. Q102 form organ -- DONE + WIRED** (full write-up in the digest above). *Numbers the digest lacks:* **BRAIN BAR (VWFA = INVARIANCE): case `1.0000`, inflection GRADED `0.31-0.51`, unrelated `0.03-0.08`; `cos(entombment,burial) = -0.023` so it CANNOT inflate meaning. THE LIVE CODE FAILS THAT BAR -- `symbol_vector` is a sha256 draw, case invariance `-0.0026` vs `+1.0000`.** ⚠️ **NOTHING CONSUMES THE FORM CHANNEL YET.** 🔧 *Process: my `--limit` flag dropped the bare value only `if limit != 40`, so `--limit 40` left "40" as a SEARCH TERM -- **`1,106` hits against a true `4`, a `275x` error I nearly acted on.***
> **2. DIRECTION = ANCHOR + PROPAGATE** (set 08-06/07; ground a SMALL affective anchor -- good/bad is in neither grammar nor text statistics because **ANTONYMS ARE DISTRIBUTIONAL TWINS**). ✅ **FOUR components `HARD_PASS`, THREE now REPRODUCED:** *S1 12-word seed -> `0.833` held-out with **ablation `0.000`** both identical, `theta_witness` RECIPROCITY `+0.603` vs BLOCK_HIGH `-0.505` SIGNS DIFFER; S2 map collapse `1.000` vs scramble `0.300`; S4 learned-from-exposure `1.000` vs scramble-consequence `0.429`, `spoil_ok=True`.* ⚠️ **REPRODUCTION DOES NOT CHANGE SCALE: 6 words / 28 items on CLEAN signal. SOUND != WORKS.**
> **3. 🚫 THE CREDIT LEVER IS MEASURED OUT.** *`HARD_FAIL` primary `0.4167` vs floor `0.6389`, lift `0.0167`, precision `0.4676 -> 0.4941`.* 🔁 **The wall reproduces TWICE, 15 days apart, two lemmatizers -- `0.4722` IDENTICAL TO FOUR DIGITS.** 🎯 *Precision problem is LIGHT VERBS: `53.2%` of credited exposures not loaded, `46` of 173 error types are GENUINE VERBS, **non-verb junk only `5.4%` of credited tokens** (measured 3x: `73%` -> `12.2%` -> `5.4%`; I quoted the biggest twice first). Coverage is NOT the cause (`439/1655`).* `I_RE_RAN_THE_WALL_...`
> **4. ✅ THE GROUNDING ORGAN WORKS; MY OWNER REPORT WAS SCOPED WRONG.** *`governor_grounding` HARD_PASS `0.967` vs **bow `0.517`**; `twostage_event_situation_v2` B and C `1.000` vs governor `0.500`; DOUBLE DISSOCIATION -- each subset's MATCHED scramble degrades, the UNMATCHED one does not.* 🔻 **SCALE: n = `21/12/12/8`, and one `1.000` IS n=2 -- it CARRIES NOTHING.** 🔻 **"counting beats us EVERYWHERE" WAS WRONG: all 16 measures are the WORD-SIMILARITY channel, which both plans ruled out (bow `0.5167` = chance HANDED THE GOLD SENSE).** ⚠️ *READ, not REPRODUCED (`399`/`7,868` cells replay).*
> **5. ✅ OPEN VOCABULARY: CLOSED.** *`B` 10/12 = `0.8333`, `Bgen` 6/8 = `0.750`, and **ALL FOUR ERRORS HAVE AN ADVERSARIAL PATIENT** -- the animacy map cannot express it, an EXPRESSIVENESS GAP. WordNet supplies it `7/8` at a `0.8%` base rate and **misses `rival` CORRECTLY**.* 🔑 **THE `== "UNK"` GUARD IS A DELIBERATE HAND-OFF -- DO NOT TOUCH IT.**
> **6. 🚫 ANISOTROPY: CLOSED** -- see CLOSED DOORS #4 above.
> **7. THE HONEST TENSION:** *the supplied table beats everything we LEARN on the word-similarity channel.* **Owner ruled supply ADMISSIBLE (08-16), so this is PRIORITISATION, not permission.**
**Written 2026-08-18 end of session, at the owner's direction, to be executed after compaction.**
Supersedes the forward-looking parts of `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`. Its Section 7
(the audit findings) and Section 6 (the ladder METHOD) both still stand as reference.

> **⛓️ COUPLING NOTE, BOTH SIDES (CLAUDE.md "a doc parsed by code is coupled to it"): THIS
> FILENAME IS AN API.** `data/hooks/staging/stop_hook.py` `_plan_path()` (~line 1155) matches
> `BUILD_PLAN_post_audit_2026-08-19.md` as the FIRST entry in its priority list, and every autoloop
> continuation tells the session to open it. **If this file is renamed, edit that list in the same
> commit** -- the previous version of that list named two plans that had not existed for weeks, and
> the hook silently emitted a "re-read a file that is not there" instruction on every turn.

> **🤖 AUTOLOOP ARMED 2026-08-19 AT 200 CONTINUATIONS (owner: "200 iterations authorized").**
> Stop it with `python tools/autoloop.py disarm`, or set `armed: false` in
> `data/hook_state/autoloop.json`, or from the dashboard's RUNNING tab. Anything other than exactly
> boolean `true` reads as DISARMED -- the fail-safe direction is OFF.

## THE DECISION THIS PLAN IMPLEMENTS

**Owner:** *"we need to have a current best substrate... we should envision a complete substrate (or
close to) and wire in the best versions of each."* Plus: **mine MIDDLE_BAND**, **parity is
interesting**, and the instrument rebuild is **deferred on the Director's recommendation**.

**Director's recommendation, accepted into this plan: WIRE TIER 0+1, THEN SPEND THE EFFORT ON THE
EMPTY SLOTS, NOT ON POLISHING THE FILLED ONES.** Assembly alone produces a well-organised filing
system. The two empty slots -- **inference** and **producing an answer in words** -- are the
difference between that and something that understands.

---

## ✅ PHASE 0 IS DONE AND MEASURED (`2e8134fd2`, 2026-08-19). DO NOT REDO IT.

- **0.1 `situation_reader` import 205 s -> 30.4 s, and its self-test now PASSES in 102.7 s** where
  it previously TIMED OUT at 240 s. Same induced hypothesis (`ruleind`), so the fix changed cost and
  nothing else. **`situation_reader` IS ON THE WIRE LIST.**
- **0.2 `_scratch_orig_goal_owner_select` removed** from `hdlab/` and from the registry (202 -> 201
  rows, all re-parsed). Git-tracked, so recoverable from history.
- **0.3 The dashboard now says `UNVETTED`, never a blank.** Tab 7 carries a HAS ANYONE CHECKED IT?
  column; a `SHELVED_REFUTED` cell colours its row red regardless of what the run called itself.
  Checked at the RENDERED CELL by the self-test: 0 blank of 14. Lookup is EXACT-match only --
  looser matching mapped `..._selftest` onto the full run's record, and a wrong disposition is worse
  than UNVETTED.
- **⚠️ FOUND WHILE DOING IT, NOT FIXED: `hdlab/ca3_completer.py` (23 KB) IS UNTRACKED.** It is on
  the Tier 1 wire list and exists ONLY in the working tree -- any checkout, reset or clean destroys
  it. Same class as board Q52. **Not committed here: it is not this session's work to sign.**

## PHASE 0 -- ONE HOUR, DO IT FIRST

**0.1 Fix `situation_reader`'s import-time training.** `hdlab/situation_reader.py:108` runs
`_INDUCED_SUBJ_NAME, _INDUCED_SUBJ_HYP = get_induced_subj_hypothesis()` **at module level**, so
merely importing the module trains a frame-induction hypothesis: loads the train split, enumerates
classes, builds a spec, runs `induce()`. That is the whole 204.5 s import and why its self-test
times out at 240 s. **The author already caches it ("trains at most once per process") -- the design
is sound, the PLACEMENT is not.**
**FIX: move it behind a lazy accessor so it fires on first USE, not first IMPORT.** Keep the cache.
**THEN `situation_reader` JOINS the wire list** -- it is genuinely functional (cross-sentence 0.5292
vs a blind baseline of 0.0000). *Excluding a working organ over where one statement sits is the
wrong trade; the earlier "exclude it" recommendation is withdrawn.*

**0.2 Remove `hdlab/_scratch_orig_goal_owner_select.py`** from `hdlab/` and from
`data/capability_registry.jsonl`. 55 KB, a scratch file registered as a capability, 103 s to import.
**Do NOT bundle the deletion with other work in one call -- that pattern is auto-denied here and
destroys whatever is bundled alongside it.**

**0.3 Fix the dashboard's honesty defect** (`PLAN` 7.5b). Tabs `4. SCORES` and `7. LATEST RESULTS`
render verdict strings straight from `metrics.json`, and 99.5% of those cannot be checked from their
own files. **Every verdict must show its ledger disposition beside it, with `UNVETTED` as the
VISIBLE DEFAULT** -- `tools/vetting_ledger.py --cite` already answers this and already refuses
unknown cells. A blank currently reads as endorsement.

---

## ✅ PHASE 1 IS BUILT AND SELF-TESTING (`2f9f3ae95`, 2026-08-19). `hdlab/substrate.py` EXISTS.

**`python -m hdlab.substrate` -> ALL SELF-TESTS PASSED.** Measured on that run: **400 sentences
read from 2 corpora it chose off a 36-corpus shelf, 3,400 lemma flags, 3,400 one-shot episodic
writes, 19 facts grounded WITH PROVENANCE, 124 refused by the consolidation gate**, persisted to
disk, query refuses a nonce and binds a seeded word. 7.9 s. Slots: **9 FILLED / 6 NEEDS_ADAPTER /
8 EMPTY / 3 EXCLUDED**, and the object reports all four itself.

**THE SELF-TEST CAUGHT FOUR DEFECTS IN THE ASSEMBLY CODE ON ITS FIRST RUNS. That is the return on
writing RULE 2 the way it is written, and the two worth carrying forward:**
- **`query()` returned zero facts for EVERY cue** (it scanned `live_facts()` as dicts; they are
  `FactRecord` dataclasses) **and the nonce arm passed anyway.** *A store that refuses everything
  passes a refusal test trivially.* **ALWAYS PAIR A REFUSAL ARM WITH A BINDING ARM.**
- **`gap_detector` was reported never-invoked WHILE RUNNING.** `ReadingLoopState` builds its own,
  so a call counter on the wrapper is structurally blind to it. Fixed by counting the ARTIFACT
  (`gap_cache`), not the call. **Reporting working machinery as dead is the false-negative twin of
  the false coverage this audit exists to catch, and it took 20 minutes to nearly commit.**

### 🔎 PHASE 1 FINDING #2 -- GROUNDING TURNS ON BETWEEN 100 AND 400 SENTENCES, AND THE GATE BINDS HARD
Measured, `scratch/phase1_grounding_scale.py`: **100 sentences -> 0 provenance rows; 400 -> 19.**
Provenance is written ONLY at the consolidation gate, so it is the proof grounding fired at all.
**The gate refused 124 and grounded 19 -- it rejects roughly 87% of what reaches it**, which is the
2026-08-12 grounding-refusal fix working rather than a gate that says yes to everything.
*Observed once and NOT a finding: reading 550 sentences produced FEWER grounded terms than 400
(14 vs 19). Consistent with the measured ACCUMULATE interference result, but n=1 -- do not quote it.*

### 🔎 PHASE 1 FINDING #3 -- THE FORAGER DECIDES WHEN TO LEAVE, NOT WHAT TO OPEN. PATCH ORDER IS ALPHABETICAL.
**It read `alice_in_wonderland` then `anne_of_green_gables` -- the first two names in sorted order --
and found 5 definitions in 400 sentences.** `definitional_extraction` pulled 228,133 definitions
from SimpleWiki; on narrative fiction it has almost nothing to find. **Charnov's theorem is about
WHEN TO LEAVE a patch; WHICH PATCH TO ENTER is a separate decision and we have not made it.**
*The shelf was the point of wiring `corpus_registry`, and we are still reading whatever is
alphabetically first.* **BUILD TARGET, cheap and well-posed: patch CHOICE by expected gain.**

---

## PHASE 1 -- WIRE THE SUBSTRATE (Tier 0 + Tier 1). **BUILT; TIER 2 REMAINS NEEDS_ADAPTER.**

**THE DELIVERABLE IS ONE FILE: `hdlab/substrate.py`.** Not a diagram, not a registry edit -- an
importable object that holds the organs in dependency order and can be run. Until that file exists
and self-tests, "wired" is a word.

**Required shape, so a post-compaction session builds the same thing:**
- `class Substrate` with **LAZY per-organ construction** -- an organ is imported and built on FIRST
  USE, never at `import hdlab.substrate`. *Phase 0 existed because one module trained at import
  time; do not rebuild that defect at the assembly layer.*
- `Substrate.read(source, limit) -> ReadResult` -- the INGEST path (Tier 0 + Tier 1).
- `Substrate.query(question) -> QueryResult` -- the RETRIEVAL path (Tier 2), returning the store
  entry, the confidence, the ACCEPT/CLARIFY/REFUSE decision, and the provenance trace.
- `Substrate.organ_report() -> dict` -- which slots are FILLED, which are EMPTY, which are
  DELIBERATELY EXCLUDED and why. **An empty slot must be visible from the object itself**, not only
  from a note; that is how P1/P2 went unwritten for weeks.
- `python -m hdlab.substrate` self-test: builds, reads a few sentences, queries, asserts each wired
  organ actually ran (count its invocations -- an organ that is imported and never called is not
  wired), prints the organ report.

**Wiring order (dependencies, not preferences) from `notes/COMPLETE_SUBSTRATE_DESIGN_2026-08-18.md` 4.1:**
**Tier 0 (reading):** `corpus_registry` -> `information_foraging` -> `definitional_extraction`
**Tier 1 (memory):** `hippocampal_encoder` -> `ca3_completer` -> `prelim_tier` -> `foundation_persistence`
**Tier 2 (comprehension):** `coreference_resolver` -> `situation_model_accumulate`; `semantic_parser` -> `cortex`

**Cost ~75 s one-time import**, dominated by `definitional_extraction` -- and after Phase 0,
`situation_reader` (30 s) is affordable too.

**WIRE ONLY THE INTERSECTION of self-test-passing AND probe-FUNCTIONAL.**
**⛔ DO NOT WIRE:** `atom_consultation` (`applied` hard-coded `False` -- cannot change a decision),
`definitional_predicate_v61` (fires on 0.27% of its intended population), `goal_achievement`'s
desiderative-negation channel (7/7 on authored exemplars, 4/7 on paraphrases; also the one genuine
self-test failure: `AssertionError: channel 'relation:recur' != 'majority'`). **All three are
self-test-passing. That is exactly why the intersection rule exists.** `cortex` is wired with
`atom_consultation` OFF.

**⚠️ `hdlab/ca3_completer.py` IS UNTRACKED IN GIT** -- 23 KB living only in the working tree, on
this wire list, destroyed by any checkout/reset/clean. Same class as board Q52. Commit it or get an
owner ruling BEFORE any git operation that touches the tree.

### 🔎 PHASE 1 FINDING #1 -- THE ORGANS DO NOT SHARE A DATA FORMAT, AND ONE IS NOT A TEXT ORGAN AT ALL

**Measured 2026-08-19 by runtime signature introspection of all 11 wire-list modules**
(`scratch/phase1_api_survey.py`, `scratch/phase1_glue_check.py`), not by grep and not from a
docstring. **This is exactly the risk Phase 2 was written to catch, arriving one phase early.**

**`hdlab/coreference_resolver.build_mention_stream(passage)` READS `passage["entities"]` -- A GOLD
MENTION INVENTORY KEYED BY GOLD ENTITY NAME**, and the records it emits carry a `gold_entity` field.
It also requires `passage["clauses"]`. **It decides which mention links to which entity GIVEN the
mentions and the entity set; it does not find them in prose.** So the ingest story in
`COMPLETE_SUBSTRATE_DESIGN` 4.3 -- *"`coreference_resolver` decides which later mention is which
earlier entity"* as a step in a text-in pipeline -- **is not runnable on unannotated text as
written.** Its probe score (0.7193 vs recency 0.5614) was measured on gold-annotated LitBank and
remains true OF THAT REGIME.

***TRIPLE-CHECK STATEMENT (CLAUDE.md Evidence discipline 5), because this calls something narrower
than documented:*** right file (`hdlab/coreference_resolver.py` at HEAD, source read directly, not
the docstring); right version (HEAD after `2e8134fd2`); right env (`.venv`); right metric (the
function's own parameter reads, not a summary); right arm (the PUBLIC entry point, not an internal
helper). **What rules out the obvious alternative: there IS a raw-text path and it is a DIFFERENT
organ.** `situation_reader.SituationReader.read(path)` takes a FILE OF PROSE -- verified by running
its self-test this session, which writes plain sentences to a temp file and passes -- and gets its
mentions from our own parser (`_pick_role_mentions(pred_idx, sent_noms)`), reusing `coref` and the
event-bundle codec internally. **So the finding is "the coreference RESOLVER is gold-fed", NOT
"we cannot do coreference on text".**

**THE SAME SHAPE HOLDS ACROSS THE LIST, and it is the thing to design around:**
| organ | what it actually consumes | composes on raw text? |
|---|---|---|
| `corpus_registry` | a directory | **YES** -- hands out sentences |
| `definitional_extraction` | sentences | **YES** |
| `situation_reader` | a file of prose | **YES** (30 s import after Phase 0) |
| `information_foraging` | a stream of GAIN FLOATS the caller defines | needs a gain signal named by us |
| `hippocampal_encoder` | a dense HD vector | needs an encoder in front |
| `ca3_completer` | FHRR bundles + per-spoke codebooks | **a different representation** from the above |
| `prelim_tier`, `foundation_persistence` | a `ReadingLoopState` / `Library` / `HDFactStore` | only via `reading_grounding_loop` |
| `coreference_resolver` | **gold mentions + gold entity set** | **NO** |
| `semantic_parser` | a TRAINED `IntentClassifier` + slot dicts | needs a fitted artifact |
| `cortex` | torch HD tensors + its own codebooks | needs an encoder in front |

**THE CONSEQUENCE FOR THE BUILD, AND IT IS A REUSE RULING, NOT A REWRITE:** `prelim_tier` and
`foundation_persistence` both key off `ReadingLoopState`, which is `reading_grounding_loop`'s --
**a LIVE entry point.** So the adapter layer this substrate needs mostly EXISTS, inside the live
loop. **Build `hdlab/substrate.py` ON TOP of `reading_grounding_loop`'s text->facts path and wire
the unwired organs INTO it. Do NOT author a parallel ingest path** -- that is the WIRE-DON'T-ISLAND
rule and the MISSING-LEARNING rule in the same costume, and a parallel path is how we would get a
second thing to audit instead of one thing that works.

**`organ_report()` MUST DISTINGUISH THREE STATES, not two:** `FILLED` (wired and invoked on the
real path), `NEEDS_ADAPTER` (works, but its input is not produced anywhere upstream -- name the
missing adapter), and `EMPTY` (nothing implements it). **A `NEEDS_ADAPTER` organ counted as FILLED
is precisely the false coverage the organ audit exists to prevent.**

---

## 🔻🔻 THE CONTROLLED CELL REFUTES TWO OF MY OWN FINDINGS -- INCLUDING ONES I PUT IN `STATUS.md`
`data/exp_discrimination_ceiling_v1/metrics.json`, 4 corpora, 150,000 sentences each, paired
permutation tests. **It was built to convert the continuation-33/34 scratch probes into citable
results. It refuted them instead.**

| corpus | inpool | RAW | DICE | Δ | p | BAG_COSINE | Δ |
|---|---|---|---|---|---|---|---|
| simplewiki | 1047 | 0.1356 | 0.1184 | **-0.0172** | 0.156 | 0.1557 | +0.0201 |
| onestop | 515 | 0.0913 | 0.0641 | **-0.0272** | 0.070 | 0.1010 | +0.0097 |
| mcguffey_graded | 589 | 0.0781 | 0.0866 | +0.0085 | 0.618 | 0.0985 | +0.0204 |
| arc | 913 | 0.1117 | 0.1260 | +0.0142 | 0.297 | 0.1566 | +0.0449 |

**⛔ RETRACTED #1 -- "DICE BUYS +31%". IT DOES NOT. 0 OF 4 CORPORA AT p<0.05, and it is NEGATIVE on
two of them.** *The scratch probe measured +31% on a 1,024-word table built from ~737,000
sentences; four corpora at 150,000 say there is nothing there. The smoke had already warned that
the effect was scale-dependent -- I pre-registered that and then still promoted the number.*

**⛔ RETRACTED #2 -- "SECOND-ORDER COSINE IS WORSE THAN THE RAW COUNT IT IS BUILT FROM". THE
OPPOSITE: IT BEATS RAW IN 4 OF 4 CORPORA.** *I called that "fifth instrument, same conclusion" and
put it in STATUS. It was one instrument at one scale, and the controlled version reverses it.*

**🐛 AND A BUG IN MY OWN CELL, DISCLOSED: `BAG_COSINE` and `SECOND_ORDER` return IDENTICAL numbers
in all four corpora because I implemented them as the same operation** -- `Cn[i] @ Cn[j]` and
`(Cn[i] * Cn[j]).sum()` are the same computation. **There are three arms in that table, not four.**

### ✅ WHAT SURVIVES, AND IT IS THE CLAIM THAT MATTERED
**RETRIEVAL still dwarfs DISCRIMINATION on every corpus: hit@50 runs 0.280-0.542 against hit@1 of
0.078-0.136, with RANDOM at 0.066-0.074.** *The answer is in reach and we cannot pick it out. That
is the finding that reframed the TOP ITEM, it holds on four corpora, and it is untouched.*
**⚠️ But the SPECIFIC NUMBER changes: I reported hit@50 = 0.787. Across four corpora it is
0.280-0.542. The 0.787 was one corpus with a 852-word pool; a 2,400-word pool halves it. POOL SIZE
BELONGS BESIDE THAT NUMBER -- I said so when I first reported it, and then quoted it without.**

**🟢 THE SENSORIMOTOR RESULT IS UNTOUCHED BY THIS.** *Different measurement, different assets, and
its strongest form is UNFITTED with a CI-separated paired bootstrap on human ratings. Nothing in
this cell bears on it.*

---

## ✅✅ REPLICATED ON A DIFFERENT GOLD *AND* A DIFFERENT SCORER -- **AND THIS ONE IS UNFITTED**
`scratch/simlex_replication_sensorimotor.py`. **988 SimLex-999 pairs -- HUMAN similarity ratings,
sharing no construction method with ConceptNet -- scored by SPEARMAN CORRELATION rather than
top-1 retrieval. NO MODEL IS FITTED: this is a plain cosine in each space.**

| predictor of HUMAN similarity | rho | 95% CI |
|---|---|---|
| **SENSORIMOTOR cosine** | **0.3171** | **[0.2605, 0.3707]** |
| SENSORIMOTOR neg-euclidean | 0.3093 | [0.2514, 0.3660] |
| co-occurrence PMI | 0.1237 | [0.0641, 0.1923] |
| co-occurrence Dice | 0.0872 | [0.0358, 0.1624] |
| co-occurrence second-order cosine | 0.0826 | [0.0212, 0.1484] |
| **co-occurrence RAW count** | **0.0446** | **[-0.0177, 0.1077] -- CI INCLUDES ZERO** |

**PAIRED BOOTSTRAP ON THE DIFFERENCE: +0.2348, 95% CI [+0.1605, +0.3155]. CI-SEPARATED.**

**THIS IS THE STRONGEST FORM THE RESULT HAS TAKEN, AND IT IS THE ONE WITH THE FEWEST CAVEATS:**
- **UNFITTED.** No model, no cross-validation, no ceiling-diagnostic asterisk. Just a cosine.
- **A different gold** (human ratings, not a knowledge base) and **a different scorer**
  (correlation, not retrieval). The ConceptNet/top-1 result is not an instrument quirk.
- **RAW CO-OCCURRENCE DOES NOT PREDICT HUMAN SIMILARITY AT ALL** -- its CI includes zero. *Which
  is exactly what the whole session predicts: co-occurrence is THEMATIC, and "how similar are
  these two words" is TAXONOMIC.*
- **The capacity confound is dead**: 1,024 co-occurrence features reached 0.3104 on the other
  instrument; FOURTEEN sensorimotor features reached 0.6413. More features is not what is
  happening.

**⚖️ AND THE HONEST DEFLATION, WHICH MATTERS FOR HOW THIS IS SOLD: PERCEPTUAL NORMS PREDICTING
SEMANTIC SIMILARITY IS A KNOWN RESULT IN THE LITERATURE. WE HAVE NOT DISCOVERED EMBODIMENT.**
*What is new FOR THIS PROJECT is specific and worth stating plainly: our substrate has been working
in a modality that measurably cannot carry the target, while an admissible, already-on-disk,
100%-covering asset carries it 2.6-7x better -- and that asset was filed as CLOSED.*

---

## 🟢🟢 THE MISSING 69% IS IN THE SENSORIMOTOR MODALITY -- 0.6413 vs CO-OCCURRENCE'S 0.3067, CONTROLS BINDING
`scratch/grounding_features_ceiling.py` + `_query_independent_control.py`. **The co-occurrence
ceiling said the answer must come from grounding, structure or another modality. It comes from
grounding, and the margin is not marginal.**

| feature set (nonlinear, word-disjoint CV, identical folds and model) | hit@1 |
|---|---|
| **PAIRWISE sensorimotor only** (|dim diffs|, cosine, euclidean, |concreteness diff|) | **0.6413** (345/538) |
| GROUND_ONLY (pairwise + candidate-only features) | 0.6152 |
| **CO-OCCURRENCE ONLY -- the established ceiling** | **0.3067** (165/538) |
| **CANDIDATE_ONLY -- never sees the query word** | **0.0985** (53/538) |
| **SHUFFLED_QUERY -- pairing destroyed, marginals preserved** | **0.0595** (32/538) |

**COO + GROUND vs COOC alone: +0.3030, paired permutation p = 0.0005.**

### 🚨 I EXPECTED THIS TO BE AN ARTIFACT, BECAUSE THE ARCHIVE HAD ALREADY MEASURED THE NUMBER
The sensorimotor cell (2026-08-18) found *"the ONLY thing that discriminates is a QUERY-INDEPENDENT
PER-WORD GENERICITY SCORE -- one that never compares the two words at all -- **reading 0.6195**,
beating every pairwise distance."* **My 0.6152 sat almost on top of their 0.6195, and my feature
set contained exactly such a feature.** *So I ran their control before writing anything.*

**IT IS NOT THE ARTIFACT, AND THREE CONTROLS SAY SO:**
- **CANDIDATE_ONLY reads 0.0985.** A model that never sees the query is at floor. **The genericity
  trap is absent here.**
- **SHUFFLED_QUERY reads 0.0595** -- destroy the pairing, keep every marginal, and it collapses
  *below* candidate-only. **The PAIRING carries the signal.**
- **Removing the candidate-only features IMPROVED the score** (0.6152 -> 0.6413). They were
  distraction, not the source.

### 🔓 AND IT RE-OPENS A ROUTE THE PROJECT CLOSED -- EXACTLY AS THE STANDING RULE SAYS IT MIGHT
**The same 11 Lancaster dimensions were filed as failing at 0.6039 against a 0.6791 bar and
"refuting THIS RESOLUTION".** *That was a pairwise-similarity question on the dissociation
instrument. On a better-posed problem -- pick the right one of 50 co-occurrence-plausible
candidates -- THE SAME ELEVEN NUMBERS REACH 0.6413 AND DOUBLE THE TEXT-ONLY CEILING.*
**This is "DO NOT GENERALISE A NARROW FAILURE TO IMPOSSIBLE" (owner, 2026-08-11) paying out in
full, on an asset that was sitting on disk marked closed.**

**⚠️ WHAT THIS IS AND IS NOT. It is a CEILING DIAGNOSTIC -- fitted on the gold, word-disjoint CV,
never a capability. It says THE INFORMATION IS THERE and text does not contain it. IT DOES NOT
give us a mechanism that uses it; that is the next build.** *Coverage is 100% of our 1,024 words,
so this is not a coverage-limited result. Limits: one gold, one corpus, 538 target words, no CI on
the fitted numbers, and the norms are a static offline human-rated asset -- admissible under the
owner's ruling (no LLM at inference), but they are SUPPLIED knowledge, not learned.*

---

## 🧱 CO-OCCURRENCE TOPS OUT AT ~0.31, HOWEVER YOU PROCESS IT -- AND THAT CORRECTS ME AGAIN
`scratch/profile_vs_scalar_ceiling.py`. **Both checks I named last continuation, run. One of them
corrects my own claim, in exactly the direction I flagged as the way it could be wrong.**

| model (all fitted on the gold, word-disjoint CV -- CEILING DIAGNOSTICS, NEVER CAPABILITIES) | hit@1 |
|---|---|
| DICE, unsupervised, for reference | 0.2435 |
| FITTED linear, 8 scalar pair-features | 0.2751 |
| **FITTED NONLINEAR, the SAME 8 scalars** | **0.3104** |
| **FITTED linear, the FULL 1,024-dim PROFILE product** | **0.3104** |
| ORACLE | 1.0000 |

**⬇️ CORRECTION TO MY OWN CLAIM: "the features do not contain the discrimination" was TOO STRONG.
Nonlinearity buys +3.5pp over the linear fit, so part of what I attributed to the features was
LINEAR SEPARABILITY.** *I named that as the way the claim could fail and it did.*

**🔴 AND THE HYPOTHESIS I RAISED LAST CONTINUATION IS NOT SUPPORTED. "Learn on the profile, do not
summarise it" predicted the full-profile model would jump. IT LANDS ON EXACTLY THE SAME 0.3104 AS
NONLINEAR SCALARS.** *The full 1,024-dimensional profile carries NO MORE than nonlinear functions
of eight numbers computed from it. The elegant story about profile geometry is dead, one
continuation after I proposed it, and its own pre-committed control killed it.*

### 🧱 WHAT SURVIVES IS A CEILING, AND IT IS THE MOST USEFUL THING HERE
**TWO COMPLETELY DIFFERENT FEATURE SETS -- eight scalars with a tree ensemble, and a 1,024-dim
profile with a linear model -- CONVERGE ON 0.3104. That is 167 of 538 either way.**
***Co-occurrence, however it is processed -- raw, normalised, summarised, full-profile, linear,
nonlinear, supervised on the answers -- tops out near 0.31 on this task. THE REMAINING 69% IS NOT
IN CO-OCCURRENCE.***
**So the pre-committed reading fires: new features must come from somewhere OTHER than word
co-occurrence -- grounding, structure, or another modality. That is a much sharper instruction than
"we need a learning signal", and it is the first result today that constrains WHERE to look rather
than only where not to.**

**⚠️ THE EXACT TIE AT 0.3104 MAY BE COINCIDENCE: 167 hits of 538 both ways, and at this n a
one-hit difference is 0.0019. Do not read the identity as meaningful -- read the CONVERGENCE as
meaningful. One corpus, no CI on either fitted number.**

---

## 🧨 [SUPERSEDED BY THE CORRECTION ABOVE] A FITTED DISCRIMINATOR REACHES ONLY 0.2732 -- **THE FEATURES DO NOT CONTAIN IT**
`scratch/supervised_rerank_ceiling.py`. **CEILING DIAGNOSTIC, FITTED ON THE GOLD, NEVER A
CAPABILITY** -- the same rule the project applies to its own 0.8629 oracle. Word-disjoint 5-fold
CV (not pair-disjoint: this project measured that leak and it inflated 0.8629 to 0.9606).
26,314 candidate rows, 3.6% positive, 538 target words, eight pairwise features.

| re-ranker | hit@1 |
|---|---|
| RAW count | 0.1859 |
| DICE (best unsupervised) | 0.2435 |
| **FITTED, all 8 features, word-disjoint CV** | **0.2732** |
| ORACLE | 1.0000 |

***A MODEL TRAINED ON THE ANSWERS, GIVEN EVERY FEATURE WE CAN COMPUTE ABOUT A PAIR, BEATS A
ONE-LINE TEXTBOOK STATISTIC BY 3 POINTS AND LEAVES 73% OF THE GAP UNTOUCHED.***

**THE PRE-DECLARED READING FIRES, AND IT IS THE ONE I SAID WOULD BE MORE USEFUL: THE FEATURES DO
NOT CONTAIN THE DISCRIMINATION. NO TEACHER OVER THESE FEATURES WILL HELP. THE NEXT MOVE IS NEW
FEATURES, NOT NEW SUPERVISION.**

### 🔬 AND THE CONTRAST WITH THIS PROJECT'S OWN ORACLE POINTS SOMEWHERE SPECIFIC
The 0.8629 oracle was a supervised **low-rank reweighting of the FULL PPMI+SVD space** -- it saw a
word's entire high-dimensional profile. **This model saw EIGHT SCALAR SUMMARIES of a pair and got
0.2732.** *Hypothesis, and it is a hypothesis: the discrimination lives in the GEOMETRY OF THE FULL
PROFILE, and collapsing a pair to scalar statistics destroys it. If so, the instruction is "learn
on the profile, do not summarise it" -- which is the opposite of what every ranker in today's
tables does.*
**⛔ DO NOT QUOTE 0.2732 AND 0.8629 SIDE BY SIDE AS A COMPARISON. Different task, scorer,
population and instrument; the standing rule forbids it. The structural observation -- scalars vs
full profile -- is the part that transfers, and it is UNTESTED.**

**⚠️ LIMITS: 538 target words, no CI on the fitted number, one corpus, and the model is LINEAR
logistic regression -- this tests LINEAR separability of eight features, not every function of
them. A nonlinear model is the obvious next check and is cheap.**

---

## 🔎 WHAT SEPARATES THE RIGHT CANDIDATE FROM THE OTHER 49? AN UNSUPERVISED STATISTIC BUYS +31%
`scratch/rerank_top50.py`. Re-ranking the SAME top-50 co-occurrence candidate set, 538 words whose
candidate set contains a gold relative -- so this is a PURE DISCRIMINATION measurement with the
retrieval step held fixed.

| re-ranker | hit@1 | vs RAW |
|---|---|---|
| **DICE** `2c/(f(a)+f(b))` | **0.2435** | **+5.8pp (+31% relative)** |
| NPMI | 0.2249 | +3.9pp |
| PMI | 0.1914 | +0.6pp |
| ENTROPY_PEN | 0.1877 | +0.2pp |
| **RAW count** (the incumbent) | 0.1859 | -- |
| SYMMETRY | 0.1859 | **0.0 -- no effect at all** |
| **SECOND_ORDER** (shared-neighbour cosine) | **0.1506** | **-3.5pp, WORSE than raw** |
| ORACLE | 1.0000 | *ceiling diagnostic, never a capability* |

**SO THE "WE NEED A TEACHER" FRAME IS AT LEAST PARTLY WRONG: A ONE-LINE UNSUPERVISED STATISTIC
RECOVERS 31% OF THE INCUMBENT'S SHORTFALL, AND WE WERE NOT USING IT.**
***AND THESE ARE TEXTBOOK STATISTICS, NOT DISCOVERIES.*** *Dice and NPMI are the standard
frequency-normalisation moves in distributional semantics. The finding is not that they work -- it
is that our pipeline was ranking on RAW COUNTS and leaving the standard gain on the table.*

**🔴 AND THE ONE THAT MATTERS MOST IS THE LOSER: SECOND_ORDER -- "do these two words keep the same
company", the classic distributional-similarity move and the thing our SEMANTIC route computes --
IS WORSE THAN THE RAW COUNT IT IS BUILT FROM.** *Fifth instrument, same conclusion: our
second-order machinery destroys information rather than extracting it.*

**⚠️ UNCONTROLLED: no CI, one corpus, 538 items. The DICE-vs-RAW gap is ~31 items of 538. Real
enough to act on, not established. And 75.6% of the discrimination remains unexplained by ANY of
these features -- the teacher requirement is narrowed, not removed.**

---

## 🎯 IT IS A **RANKING** PROBLEM, NOT AN INFORMATION PROBLEM. hit@k SETTLES IT IN ONE PASS.
`scratch/hit_at_k_ceiling.py`, paradigmatic gold, 635 scorable words, 852 candidates.

| arm | hit@1 | hit@5 | hit@10 | hit@25 | **hit@50** | hit@100 |
|---|---|---|---|---|---|---|
| BAG cosine | 0.148 | 0.334 | 0.417 | 0.545 | 0.639 | 0.735 |
| TYPED cosine | 0.134 | 0.274 | 0.361 | 0.469 | 0.567 | 0.660 |
| **RAW co-occurrence COUNT** | **0.150** | **0.395** | **0.510** | **0.677** | **0.787** | **0.846** |
| RANDOM | 0.003 | 0.013 | 0.030 | 0.072 | 0.167 | 0.277 |

**A RELATED WORD IS IN THE TOP 50 OF A PLAIN COUNT LIST FOR 78.7% OF WORDS -- against a random
16.7%. THE INFORMATION IS OVERWHELMINGLY PRESENT. WE CANNOT PUT IT FIRST.**

***AND THE SECOND ROW OF THAT TABLE IS THE UNCOMFORTABLE ONE: RAW COUNTS BEAT BOTH OF OUR
REPRESENTATIONS AT EVERY SINGLE DEPTH.*** Cosine over accumulated profiles reads 0.639 at k=50
where the raw count reads 0.787 -- **a 15-point gap, and the "sophisticated" version is the loser.**
*Normalising and projecting the counts is DESTROYING information, not extracting it. That is the
ORGAN A write-rule conclusion again -- summing raises interference, the incumbent is worse than not
accumulating -- arriving on a fourth instrument.*

### 🔄 THIS REFRAMES THE PROGRAMME'S OWN DIAGNOSIS, AND IT UNIFIES WITH THE ONE RESULT WE TRUST
The standing line is *"the missing ingredient is a LEARNING SIGNAL"*, which has been read as **the
information is not in the counts**. **IT IS.** hit@50 = 0.787 says so directly, and the fitted
PPMI+SVD oracle already said the same thing from the other side -- **supervision moves AUC from
0.03-0.07 to 0.8629 ON THE SAME COUNTS.** *Two independent demonstrations that the counts carry it
and the read-out does not.*
**SO THE PROBLEM IS NOW WELL-POSED FOR THE FIRST TIME: given ~50 candidates that are ALL plausible
by co-occurrence, pick the RIGHT one. That is a DISCRIMINATION task with a 79% ceiling, not a
knowledge-acquisition task -- and it is exactly the shape a learning signal is for.**
*It also explains why every mechanism today tied or lost: they are all different ways of ranking
the same candidate pool, and none of them addresses discrimination.*

**⚠️ SCOPE: one corpus, 852 words, paradigmatic relations, top-1-of-852 retrieval. The hit@k shape
is robust (RANDOM's curve is visibly flat beneath all three), but the 0.787 is a property of THIS
pool size -- a larger pool lowers it. Report the pool with the number, always.**

---

## ✅ THE 74% REPLICATES ON HUMAN RATINGS -- AND IT WAS THE MOST FALSIFIABLE THING I CLAIMED TODAY
`scratch/cooccurrence_of_related_pairs_simlex.py`. **The obvious way my number could have been
wrong: ConceptNet is crowd-sourced and Wiktionary-derived, and both favour associations PEOPLE
VOLUNTEER -- which are exactly the ones that co-occur in text. So the 74% might have been a
property of the gold rather than of language.** SimLex-999 is the right second source: **human
similarity ratings, on a construction that explicitly SEPARATES similarity from association.**
988 of 999 pairs have both words in the corpus table.

| SimLex band | n | co-occur | never |
|---|---|---|---|
| very similar (>=7) | 226 | **69.0%** | 31.0% |
| similar (5-7) | 224 | 76.8% | 23.2% |
| middling (3-5) | 224 | **85.3%** | 14.7% |
| dissimilar (<3) | 314 | 65.6% | 34.4% |
| **high similarity (>=6)** | **321** | **71.0%** | **29.0%** |
| **high similarity AND LOW ASSOCIATION** | **267** | **70.0%** | 30.0% |

**CONCEPTNET SAID 74/26. HUMAN RATINGS SAY 71/29. THE FINDING REPLICATES ACROSS TWO SOURCES THAT
SHARE NO CONSTRUCTION METHOD.** *And the last row kills the obvious escape: pairs that MEAN the
same and are explicitly NOT ASSOCIATED still co-occur 70% of the time, so this is not an
association artifact.*

**🔬 AN EXTRA THAT SUPPORTS THE PICTURE STRUCTURALLY: CO-OCCURRENCE IS NOT MONOTONIC WITH
SIMILARITY -- IT PEAKS IN THE MIDDLE (85.3% at similarity 3-5, falling to 69% at >=7 and 65.6%
at <3).** *Middling-similarity pairs are the thematically-related ones -- associated but not
synonymous -- which is exactly the co-occurrence-heavy region, and exactly the taxonomic/thematic
dissociation this project has PINNED as biology, showing up in raw corpus statistics.*

**⚠️ THE CAVEAT THAT MAKES THE READ STRONGER, NOT WEAKER: "never co-occur" is relative to a
co-occurrence table built from a 64 MB slice, covering 1,024 words. WITH MORE TEXT, MORE PAIRS
CO-OCCUR.** *So ~26-29% is an UPPER BOUND on the never-co-occur residue at this corpus size, and
the true residue at scale is SMALLER. The thing a teacher would have to supply is at most a
quarter of related pairs, and shrinking.*

---

## 🧯 THE ZERO-CO-OCCURRENCE TEST: I NEARLY REPORTED A 20x COLLAPSE THAT WAS MOSTLY DEFINITIONAL
Masking every co-occurring candidate out of the pool for BOTH arms gave TYPED 0.0059 and BAG
0.0082 -- **a 20x drop from 0.10-0.14, tied, barely above a 0.0012 random floor.** That reads as
"neither representation generalises past direct co-occurrence", which is the strongest possible
form of this project's standing diagnosis. **I checked whether a correct answer was even reachable
before writing it down.**

**IT LARGELY WAS NOT. After masking, only 45.9% of items (ALL relations) and 26.3% (PARADIGMATIC)
still had ANY gold neighbour left in the pool. MEDIAN REACHABLE GOLD NEIGHBOURS: ZERO.**
*So 54% and 74% of items were scored as misses BY CONSTRUCTION. Per discipline 18 that is
UNTESTABLE, not negative -- and the "20x collapse" was mostly the denominator.*

### RE-SCORED ONLY WHERE A CORRECT ANSWER WAS REACHABLE
| gold subset | TYPED | BAG | diff | p |
|---|---|---|---|---|
| ALL (n=337) | 0.0148 (**5 hits**) | 0.0208 (**7 hits**) | -0.0059 | 0.72 |
| PARADIGMATIC (n=167) | 0.0240 (**4 hits**) | 0.0299 (**5 hits**) | -0.0060 | 1.00 |

**BOTH TIE, AT 4-7 HITS. THAT IS UNDERPOWERED AND IS NOT A VERDICT ON EITHER REPRESENTATION.**
*What survives: the drop from ~0.10 to ~0.02 on the fair subset is real and large. What does NOT
survive: any claim about TYPED vs BAG in the zero-co-occurrence regime.*

### 🎯 THE INCIDENTAL FINDING IS THE MOST USEFUL THING HERE, AND IT IS ABOUT LANGUAGE, NOT US
***74% OF PARADIGMATICALLY-RELATED GOLD PAIRS CO-OCCUR IN THE CORPUS. Only 26% of words have a
taxonomic relative they are never seen beside.*** *That is a fact about text and about ConceptNet,
not about our substrate -- and it does three things: it explains why co-occurrence is such a
punishing baseline in this domain; it BOUNDS how much any "same job, never seen together"
mechanism could ever buy; and it means the dissociation instrument's SET_P -- synonym pairs with
ZERO co-occurrence -- is testing a genuinely RARE configuration, which is worth knowing before
more effort is spent gating on it.*

**FOUR REFINEMENTS OF ONE QUESTION IN TWO CONTINUATIONS: aggregate -> split by relation family ->
mask co-occurring candidates -> score only where an answer is reachable. THE FIRST THREE WOULD ALL
HAVE BEEN REPORTED AS ANSWERS, AND THE THIRD WOULD HAVE BEEN THE MOST QUOTABLE AND THE MOST
WRONG.**

---

## 🔬 THE DRILL'S NAMED TEST, RUN: TYPED SLOTS DO **NOT** BEAT THE BAG -- AND THE SPLIT IS THE FINDING
`scratch/typed_vs_bag_probe.py` + `_split.py`. **UNUSUALLY CLEAN COMPARISON: both representations
live in the SAME file (`selectional_slots_v1.pkl`), built by the SAME parser on the SAME corpus in
the SAME run -- 944,990 slot observations over 736,967 parsed sentences. Representation is the
only variable.** Scored on the independent ConceptNet gold, 851 words with >=5 observations in
BOTH representations, comparable dimensionality (20,865 typed vs 21,740 bag).

| gold subset | TYPED (slots) | BAG (co-occurrence) | TYPED - BAG | p |
|---|---|---|---|---|
| **aggregate** | 0.1081 | **0.1363** | -0.0282 | 0.048 |
| **PARADIGMATIC** (IsA/Synonym/SimilarTo/PartOf...) | 0.1004 | 0.1110 | **-0.0106** | **0.447 -- TIED** |
| **THEMATIC** (AtLocation/UsedFor/Causes...) | 0.0230 | **0.0474** | -0.0244 | **0.006** |
| FREQUENCY floor | 0.0423 | | | |
| RANDOM floor | 0.0071 | | | |

**THE AGGREGATE LOSS IS ENTIRELY THE THEMATIC HALF.** *Which is unsurprising and should have been
predicted: co-occurrence IS thematic, so a bag predicting "what goes WITH this" is the
representation matching the construct.* **On the PARADIGMATIC half -- the relations typed slots
were supposed to win -- THEY TIE.**

**🟢 AND BOTH BEAT THEIR FLOORS BY A LOT: 0.10-0.14 against a frequency floor of 0.042 and random
of 0.007.** *That is the first thing measured today where one of our own representations clearly
clears its floors -- roughly 3x frequency and 15-19x random. Worth saying after a day of numbers
that did not.*

**VERDICT ON THE DRILL'S CLAIM: NOT SUPPORTED, AND NOT YET REFUTED EITHER.** *Typed slots buy
nothing here, and they cost a parser the bag does not need.*

### ⚠️ BUT MY TEST STILL DOES NOT ASK THE DRILL'S EXACT QUESTION, AND I AM SAYING SO RATHER THAN CLAIMING THE SCALP
The drill's mechanism is specifically about words that **NEVER CO-OCCUR**: *"two words that can
replace each other turn up as the subject of the same verbs... **even when they never appear in the
same sentence as each other**."* **My ConceptNet-related pairs are NOT restricted that way, and a
bag can only win on pairs that DO co-occur.** *That is the same structure as SET_P in the
dissociation instrument, and it is the one condition under which typed slots could show their
advantage.*
**THE DECISIVE TEST, NAMED AND NOT RUN: restrict the gold pairs to those with ZERO co-occurrence in
the corpus, then re-score.** *Cheap -- the co-occurrence counts are in the same file. Until it runs,
"typed slots do not help" is licensed only for pairs that co-occur.*
***This is the third refinement of the same question in one continuation. Each one moved closer to
what was actually claimed, and the first two would both have been reported as answers.***

---

## 🚨 A 123 KB DRILL ON THE TOP ITEM LANDED 21 HOURS AGO AND NOBODY READ IT -- INCLUDING ME, ALL DAY
`notes/admissible_supervision_sources_drill_2026-08-18.md` (67 KB) and
`notes/what_supervision_the_brain_has_that_we_do_not_error_driven_learning_drill_2026-08-18.md`
(56 KB). **STATUS's TOP ITEM is "find an admissible supervision signal", both drills answer it, and
I spent a full session building and measuring without opening either.** *This project has recorded
"AN UNREAD RUN IS A RUN THAT DID NOT HAPPEN" twice. This is the third, it is mine, and the material
was sitting in the directory the autoloop tells me to read.*

### ⚠️ AND IT CONTAINS A DIRECT INSTRUCTION THAT WOULD HAVE CHANGED TODAY'S WORK
> *"our whole 'we need a teacher' diagnosis rests on experiments that ALL represented a word's
> context as an **unordered bag of the words in its sentence**, which is the single most
> co-occurrence-flavoured choice available -- so before we spend anything on teaching, we must check
> whether simply recording **which job** each context word held is enough on its own."*

**EVERY ROUTE I MEASURED TODAY USES THE BAG.** `context_vector_masked` is a bag; the SEMANTIC route
sums bags; the episodic store encodes bags. **The drill names the bag as the suspect variable and
says to test the TYPED-SLOT representation FIRST.** *It also names the asset:
`data/selectional_preferences_v1/` -- 41,529 `(verb, ROLE) -> filler` slots from our own parser,
90.0% coverage of the scored words, no WordNet and no LLM anywhere in the pipeline.*
**THAT IS THE NEXT BUILD, AND IT WAS DECIDED BEFORE I STARTED.**

### ✅ MY GOLD SURVIVES THE DRILL'S PROVENANCE AUDIT -- CHECKED, NOT ASSUMED
The drill measured ConceptNet's WordNet contamination PER RELATION by streaming all 34,074,917
rows: `/r/MannerOf` **99.9%** WordNet, `/r/Entails` **100%**, `/r/SimilarTo` **70%**,
`/r/Synonym` **40%**, `/r/IsA` **33%**. **My gold keeps IsA, Synonym and SimilarTo.** Re-checked
its composition: **ZERO `/d/wordnet` edges** -- 185,580 `conceptnet/4/en`, 87,898 `opencyc`,
86,473 `wiktionary/en`, 35,511 `dbpedia`. **The provenance filter did its job.**

**BUT THE DRILL'S SHARPER POINT NEEDS THE RIGHT SCOPE, AND IT IS EASY TO OVER-APPLY:** it says even
the non-WordNet 60% of `/r/Synonym` is *"the SAME CONSTRUCT -- a curated synonym list built for the
same purpose"*, which makes it circular **as SUPERVISION for an instrument whose labels ARE WordNet
synonymy**. ***Circularity is a relation between the GOLD and WHAT THE SYSTEM WAS TRAINED ON, not a
property of the gold alone.*** *My substrate reads raw text and never sees ConceptNet, so as an
external referee for "did it ground this word to a plausible meaning" it is legitimate. The drill's
verdict is correct in its scope and does not transfer to mine -- and saying which is which is
exactly the discipline that stops a real caveat becoming a superstition.*

---

## 🧰 "THE CHEAPEST FIX IN THE WHOLE BACKLOG" IS NOW A TOOL: `tools/strongest_floor_audit.py`
The 2026-08-18 audit named it and nobody did it: *"SEVERAL CELLS ALREADY COMPUTED THE RIGHT FLOOR
AND THEN DISCRIMINATED AGAINST SOMETHING ELSE. RE-SCORE EVERY LANDED CELL AGAINST THE FLOOR IT
ALREADY HAS ON DISK."* **It is also personal: I committed that exact defect today**, reporting the
substrate as losing "~10x" against a `COUNT_FLOOR` of 0.0125 while a stronger floor from the same
data read 0.0300. *A rule that is easy to state and evidently hard to follow should be a tool.*

**7,861 `metrics.json` scanned. 286 cells flagged** -- 143 where a floor the cell computed ITSELF
beats its own best treatment, 193 where the verdict text quotes a floor that is NOT the largest
one in its own metrics.

### 🔬 THE NUMBER WENT 1,335 -> 286 BECAUSE ITS MOST EXCITING HIT WAS WRONG, AND I CHECKED IT
**The single most striking flag was `diag_stateful_core_gen_curve_v1`: a RANDOM-INIT CONTROL at
0.6250 beating a TRAINED arm at 0.5000, under a `PASS`.** That is the untrained-beats-trained
shape this project has genuinely recorded once before -- and it was tempting.
**Checked it: `run_mode: "selftest"`, and the cell's own message says "exercised at N~4-16". It
was verifying that code paths RUN, not claiming training worked. NOT A DEFECT.**
*Four false-positive shapes were found and filtered this way, each measured rather than imagined:*
ties at ceiling (`1.0 vs 1.0`), **a DELTA read as a floor** (`real_minus_shuffle` matched on the
word "shuffle"), cells that already declare themselves failures, and self-tests.

**⚠️ AND THE RESIDUAL FALSE-POSITIVE RATE IS STILL REAL AND IS NOT HIDDEN. Two shapes remain
UNFILTERED and visible in the top of the list:** comparing a `max_` statistic against a `mean_`
one, and near-ties across different seeds or subsets (one hit "quotes 0.6319 while holding
0.6337"). **286 IS A READ LIST, NOT 286 DEFECTS**, and the tool says so in its own output.

---

## 📖 MIDDLE_BAND ACTUALLY READ (owner: *"understanding what it was TRYING and the SIGNAL"*)
*I had produced a ranked list and a premise correction and had not read the cells. Owed, now done.*
**Only 26 of 580 carry a self-assessment field and only 31 have a readable docstring -- and ZERO
have both**, which is why the list looked thin. The 26 are the population worth reading.

### ⬇️ CORRECTION TO MY OWN FRAMING BELOW, MADE ONE CONTINUATION LATER AND BEFORE ANYONE BUILT ON IT
**I called this cell "a lead for the empty inference slot with a number attached". IT IS NOT A
REASONING MEASUREMENT.** Read from its metrics: the arms are *"recall vs independent nltk gold"*
over a *"materialized within-5k HYPERNYM+PART_OF backbone"*, by *"deterministic BFS"*. **nltk
hypernym/part-of IS WordNet, and the backbone is a MATERIALIZED COPY of that same relation set.**
So `recall 0.61` at 2 hops means **39% of gold pairs were not reachable in the copy** -- and the
cell says the mechanism itself: *"each hop multiplies out-of-5k-intermediate misses"*.
***THIS MEASURES HOW COMPLETELY A KNOWLEDGE GRAPH WAS COPIED AND HOW BFS DEGRADES WHEN THE COPY HAS
HOLES. The depth "cliff" is coverage decay, not a reasoning boundary.*** *The cell is honest about
this in its own scope line -- "NOT general reasoning", "measured-bounds not fundamental" -- and I
read past that to the part I wanted.*
**⚠️ LIMIT ON THIS CORRECTION, STATED: `experiments/exp_b_alpha_broad_envelope_cpu_v1.py` IS NOT
ON DISK, so I am inferring the backbone's provenance from the metrics rather than reading the
build. If the backbone were materialized from a NON-WordNet source the circularity would not
apply -- but nothing in the metrics suggests that, and the burden is on the claim.**

**🟢 AND THERE *IS* SOMETHING REAL HERE -- IT IS JUST NOT THE RECALL NUMBER.**
**`false_positives: 0` across all five benchmarks; `refuse_rate: 1.0`; 750 negatives verified
GENUINELY UNREACHABLE by exhaustive BFS at build ("not bounded-give-up"); and 4,344 of 4,344
returned path edges trace to a persisted Store tuple -- `n_unverifiable_edges: 0`.**
***The system refuses instead of confabulating, and every answer it gives is fully auditable.***
*That is the glass-box invariant demonstrated at scale, and it is worth more to this project than
a recall figure. Caveat that must travel with it: a system which only ever reports STORED paths
gets "no hallucination" cheaply -- the property is real, the difficulty of achieving it is not.*

**🎯 [SUPERSEDED BY THE CORRECTION ABOVE] THE ONE WITH A LEAD FOR A CURRENTLY-EMPTY SLOT.** `exp_b_alpha_broad_envelope_cpu_v1`:
> *"Characterizes WHERE composed reasoning works (**2-hop MIDDLE**) vs **CLIFFS (3-4 hop
> HARD_FAIL**). NOT general reasoning. Per-benchmark HARD_FAIL = **honest cliff FINDING**."*
**Q2 domain-general inference is a NAMED EMPTY SLOT in the substrate design, and this cell already
measured its boundary: composition survives two hops and falls off a cliff at three.** *That is a
starting point with a number attached, and it was sitting unread. Verify before leaning on it --
it is UNVETTED and the ledger still refuses it.*

**AND FOUR CELLS THAT EMBODY DISCIPLINES THIS PROJECT KEEPS RE-LEARNING, WRITTEN BY THEIR OWN
AUTHORS:**
- **The strongest-floor rule, applied by a cell to itself.**
  `exp_agreement_attractor_role_binding_cg_viability_v1`: *"Beating nearest-noun is TRIVIAL here
  (nearest is the attractor -> below chance); the HONEST discriminator is beating the FIRST-NOUN
  positional heuristic on the subject-not-first subset."* **It identified that its own obvious
  baseline was the wrong one and named the right one.**
- **A cell refusing to let its own metrics be read as quality.**
  `exp_grounding_quality_readout_v1`: *"**THIS CELL MEASURES NO QUALITY.** Everything it emits is
  structural or a stability/selectivity control."*
- **A cell delimiting what each of its arms licenses.** `exp_grounding_readout_known_answer_v1`:
  *"Convergence with the prior hand-score is evidence ABOUT THE PROXY, never a substitute for
  it"*, and *"STAGE B is a 2-candidate forced choice; it licenses NO statement about the
  open-vocabulary argmax rate."*
- **The circularity trap, flagged by the cell that fell into it.**
  `exp_learned_composition_glue_pun_selectional_generalization_v1_smoke`: *"generalization signal
  is WordNet-hypernym (KB-derived); a full-gate pass is a CANDIDATE for fresh adversarial VET,
  not a self-declared CG."*

**THE HONEST SYNTHESIS, WHICH IS NOT QUITE EITHER STORY: self-assessment is RARE EVERYWHERE
(MIDDLE_BAND 4.5%, HARD_PASS 3.0% -- no real difference, as measured). But the ones that exist
cluster at the TOP of the MIDDLE_BAND ranking, and they are worth reading INDIVIDUALLY rather than
aggregating.** *The owner's instinct was right about the cells and wrong about the population
statistic, and both halves are worth keeping.*

---

## 🧪 THE CELL THAT CAN SETTLE IT IS RUNNING: `experiments/exp_grounding_precision_gold_v1.py`
**IN FLIGHT**, detached, PID `scratch/gp_full.pid`, logs `scratch/gp_full.out` / `.err`.
3 seeds x 40,000 sentences, checkpointed units -> `data/exp_grounding_precision_gold_v1/`.
**DO NOT RESPAWN.** *Smoke clean: 2,000 sentences -> 76 grounded, 648 refused, coverage 98.7%, and
the shelf fix is visible -- SIX corpora visited where the old code reached three.*

**THE DECIDER IS `RANDOM_ANCHOR`, NOT A FLOOR OVER OTHER ITEMS, AND THE CELL SAYS SO IN ITS OWN
DOCSTRING.** *The gate was measured to accept terms with twice the gold degree, so any comparison
against a different item set is confounded by term difficulty. `RANDOM_ANCHOR` holds the TERMS
FIXED and randomises only the ANSWER -- it isolates "is this meaning right" from "is this term
easy". Paired permutation, not two independent CIs.*

**AND READING (iv) IS A REFUSAL TO ISSUE A VERDICT: below 300 scorable items the cell reports
UNDERPOWERED and reports the required n instead.** *At 2,000 sentences it produced 75 scorable and
flagged itself. That is the rule that would have stopped me quoting "6x" yesterday.*

---

## ⬇️ DOWNGRADED BY ITS OWN CONTROL, ONE CONTINUATION LATER: THE GATE'S PRECISION ADVANTAGE IS NOT ESTABLISHED
`scratch/gate_selection_control.py`. **Last continuation I reported the gate's accepted set at
0.0355 vs the raw argmax's 0.0058 -- "roughly 6x, the gate is doing real selection" -- flagged as
a direction rather than a result. The matched controls say even that was generous.**

**THE CONFOUND IS REAL AND NOW MEASURED: the gate accepts terms with TWICE the gold degree
(mean 42.3 vs 21.7; median 16 vs 8).** *Precision is P(anchor is a gold neighbour), so a term with
many neighbours is easier to be right about. The gate was partly selecting EASY TERMS, not good
meanings -- exactly the confound named before the probe ran.*

| arm | precision | n |
|---|---|---|
| RAW, ungated argmax | 0.0058 | 1712 |
| **RAW, DEGREE-MATCHED to the gated set** | **0.0089** | 112 |
| GATED (what we ground) | 0.0446 | 112 |
| **GATED, SAME TERMS, RANDOM ANCHOR** | **0.0179** | 112 |

**AGAINST THE STRONGEST CONTROL -- the same terms with a random anchor from the same pool -- THE
GATE IS 5 HITS AGAINST 2.** ***That is a width, not an effect (discipline 14), and the "6x" should
not be repeated.*** *Degree-matching alone raises the baseline 0.0058 -> 0.0089, so part of the
original gap was the easy-terms confound and the rest is unresolvable at this n.*

**FILED: the gate's precision advantage is NOT ESTABLISHED. It is not refuted either -- 5 vs 2 is
simply too few. The named way to settle it is more grounded items, which means more reading, not a
better argument.** *Fifth time today a matched control changed a reading. The base rate for an
apparent positive surviving its own twin in this project remains grim, and it applies to my
positives too.*

---

## ❌ HUBNESS HYPOTHESIS TESTED AND REFUTED -- AND IT MOVED THE PROBLEM TO A DIFFERENT ORGAN
`scratch/hubness_probe.py`. **I proposed that the generic attractor is HUBNESS in the
anchor-selection argmax, and that this might explain why the constant/prototype floor is the
strongest floor across this whole project.** Tested before building on it.

| | distinct / queries | top-share | gold precision |
|---|---|---|---|
| ARGMAX (what `canonicalize` does) | 205 / 1926 = **0.106** | **2.4%** | 0.0058 |
| hubness-corrected (similarity centering) | 205 / 1926 = 0.106 | 1.8% | **0.0058, identical** |

**THE CORRECTION CHANGES NOTHING**, and the correlation between an anchor's mean similarity to all
queries and how often it wins is only **r = 0.305** -- too weak to be the mechanism. **HYPOTHESIS
REFUTED.** *Cost: one probe, no build.*

### 🎯 AND THE REFUTATION IS MORE USEFUL THAN THE HYPOTHESIS WOULD HAVE BEEN
**THE RAW ARGMAX IS NOT DEGENERATE AT ALL: 205 distinct anchors over 1,926 pending items, top
anchor 2.4%.** *The grounded set was 39 anchors over 96 terms with the top at 17.7%.* **So the
concentration is NOT introduced when the anchor is CHOSEN. It is introduced by WHICH CANDIDATES
THE CONSOLIDATION GATE ACCEPTS.** *I was looking at the wrong organ, and the probe said so in one
run. The next investigation belongs at the gate -- schema consistency, vote margin, min_confirm --
not at `canonicalize`.*

**🟢 AND AN UNEXPECTED POSITIVE FOR THE GATE, STATED WITH ITS LIMIT: the gate's ACCEPTED set scores
0.0355 against the raw argmax's 0.0058 on the same gold -- roughly 6x. The gate is doing real
selection, not just thinning.** ***⚠️ That is 5 hits of 141 against 10 of 1,712, and it is a
SELECTION EFFECT BY CONSTRUCTION -- which is what a gate is for. It is a direction, not a result,
and single-digit hit counts cannot carry more than that.***

**⚠️ NOT A REDISCOVERY OF DO-NOT-REDO 27, and the difference was stated before running:** that
entry closed RANK-1 COMMON-MODE REMOVAL applied to the STORE in the ACCUMULATE-interference
setting on the dissociation instrument. This was applied to the ANCHOR-SELECTION ARGMAX, on
grounding degeneracy, on a different scorer and population. **A second independent negative for
the same family of fix, at a different site.**

---

## 🚨 SECOND DEFECT I BUILT: 25 OF 28 CORPORA WERE UNREACHABLE, AND IT LOOKED EXACTLY LIKE SATURATION
**The degeneracy trajectory was meant to test whether the anchor pool is a cold-start bottleneck.
It first produced a textbook learning ceiling: grounding plateaued at 180 terms, new anchors per
chunk fell 21 -> 9 -> 32 -> 7 -> 1 -> 1 -> 0, and `distinct/grounded` flattened at 0.42.**
*I was one paragraph from writing "the substrate saturates after ~1,600 sentences".*

**IT WAS NOT SATURATION. `readable_names()` IS SORTED, so EVERY `read()` restarted at the
alphabetical head and took the first `max_patches` names -- re-entering the SAME THREE BOOKS until
they drained. MEASURED: 113,649 sentences remained across just 12 of the 28 readable corpora, and
25 of 28 were NEVER OPENED.** *The reader had a 36-corpus shelf and could reach three of it.*
**FIX: skip drained patches, and rotate the start point so the next read continues where the last
stopped.** *This is the concrete cost of Phase 1 Finding #3 -- the forager chooses WHEN to leave
but not WHAT to open -- and the cheapest half of that fix.*

### 📈 WITH A VARIED SHELF, THE DEGENERACY ROUGHLY HALVES -- READING (A) FIRES, BUT ONLY PARTLY
| | narrow shelf | rotated shelf |
|---|---|---|
| top-anchor share | 23.6% -> **12.8%** | 23.6% -> **9.5%** |
| distinct anchors / grounded | 0.382 -> 0.428 (**plateau**) | 0.382 -> **0.524, still rising** |
| new anchors per chunk | collapses to **0** | still arriving (**8** in the last chunk) |
| grounded terms | plateaus at 180 | 55 -> **147 and climbing** |

**And the anchors become recognisably meaning-like:** `physics -> biology`,
`discipline -> physics`, `perform -> function`, `institute -> commons` -- against the narrow
shelf's `mouse -> way`, `swim -> way`, `cry -> way`.

**⚠️ BUT IT IS NOT PURELY A COLD START, AND THE STRUCTURAL HALF REPRODUCES: a NEW generic attractor
forms.** `bookstore -> available`, `campus -> available`, `custom -> available`. *One
high-frequency word still absorbs many terms; only its identity changed. `way` remains top at
9.5%.* **So: shelf breadth halves the degeneracy and does not remove it.**

**PRECISION RE-MEASURED on the varied shelf: 0.0215 -> 0.0355 (5 hits of 141), floors 0.0142 and
0.0071. ⚠️ FIVE HITS AGAINST TWO IS NOT A WIN AND IS NOT CLAIMED AS ONE** -- the direction agrees
with the degeneracy result, and that is all it is licensed to say.

---

## 🔴 GROUNDING PRECISION MEASURED FOR THE FIRST TIME -- AND THE ANCHORS ARE DEGENERATE
**Nobody had ever asked whether the terms the substrate grounds are grounded to the RIGHT thing.**
Now measured against the provenance-filtered ConceptNet gold (422,082 edges, no WordNet source).
`scratch/grounding_precision_probe.py`, alice, 750 sentences, 96 grounded pairs, 344 refused.

**✅ THE INSTRUMENT APPLIES: gold coverage is 96.9% -- 93 of 96 grounded terms have gold edges.**
*That was the risk and it did not fire.*

| arm | precision |
|---|---|
| `TOP_COOCCURRENT` floor (the word it co-occurs with most) | **0.0323** |
| **SUBSTRATE GROUNDING** | **0.0215** |
| `MOST_FREQUENT_ANCHOR` floor | 0.0108 |
| `RANDOM_ANCHOR` floor | 0.0108 |

**⚠️ AND THE PRECISION TABLE IS UNDERPOWERED AND MUST BE LABELLED SO: those are 3, 2, 1 and 1 HITS
out of 93. The difference between 2 and 3 hits is not a result.** *Per discipline 18 this is closer
to untestable than to resolved, and quoting "the floor beats the substrate" off single-digit counts
would be the width-as-effect error.*

### 🎯 THE FINDING THAT DOES NOT NEED A CI, AND IT IS THE MECHANISM
**39 DISTINCT ANCHORS FOR 96 GROUNDED TERMS. ONE WORD -- `way` -- IS THE MEANING OF 17.7% OF THEM.**
The top six anchors are `way, know, think, people, use, time`, and **48.5% of all anchors are
seed-vocabulary words**. Actual output: `mouse -> way`, `swim -> way`, `think -> way`,
`hall -> way`, `cry -> way`. ***THESE ARE THE SAME ANSWER TO DIFFERENT QUESTIONS.***
**The grounding gate is not selecting a MEANING, it is selecting a GENERIC ATTRACTOR -- the
constant/prototype floor appearing INSIDE the grounding organ.** *No gold that encodes meaning
could ever score `way` as the meaning of `mouse`, so the low precision is downstream of the
degeneracy and not an independent fact.*

**✅ ONE OLD DEFECT IS GENUINELY GONE, RE-CHECKED RATHER THAN ASSUMED: SELF-ANCHORING IS 0.0%.**
*The 2026-08-18 audit found 2,328 of 3,544 grounded facts had THEMSELVES as their meaning. Not one
of these 96 does.* **A real repair, and worth saying so.**

**NAMED NEXT STEP, and it targets the degeneracy rather than the precision number: the anchor pool
is `ConceptSpace`, which holds SEED words plus already-grounded words -- so early grounding is
forced to choose among ~107 generic seeds. That is a structural cause with a structural fix, and
it predicts the degeneracy should FALL as the grounded vocabulary grows.** *Testable, and it does
not require a bigger n to see.*

---

## 🚨 A DEFECT I BUILT, FOUND BY TRYING TO USE MY OWN SUBSTRATE: IT ONLY CONSOLIDATED WHEN THE FORAGER CHANGED BOOKS

**MEASURED, and the contradiction is what exposed it.** Setting up the replacement task, the
substrate grounded **NOTHING** on 6,000 sentences of simplewiki -- and nothing on 2,000 sentences
of each of FIVE other corpora, narrative included. Yet the self-test grounds 19 on 400 sentences.

**CAUSE: `read()` called `checkpoint()` ONCE PER PATCH.** Grounding needs `min_confirm=4` traces
**across passes**, and one patch is one pass, so **a single-patch read grounded zero at ANY
volume.** Consolidation frequency was tied to the corpus CHANGING, not to how much had been read.

| | before | after |
|---|---|---|
| simplewiki, 750 sentences, 1 patch | **0 grounded / 0 refused** | **38 / 199** |
| alice, 750 sentences, 1 patch | **0 / 0** | **97 / 344** |
| self-test config (400 / 2 patches) | 19 / 124 | 55 / 258 |

**FIX: consolidate on a SCHEDULE (`consolidate_every=200` sentences), which is also the more
faithful shape -- the brain consolidates offline and periodically, not when you pick up a new book.**

### ⚠️ SCOPE CORRECTION TO THE PHASE 2 NEGATIVE -- NOT A RETRACTION, BUT IT MUST TRAVEL WITH IT
**`exp_substrate_end_to_end_readout_v1` ran with `max_patches=1`, so EVERY Phase 2 run grounded
NOTHING. The consolidation organ never fired in the cell that reported on the assembled substrate.**
*The result still stands as measured -- the EPISODIC and SEMANTIC routes read from episodic writes
and Library traces, which happen regardless of consolidation -- but the substrate was running with
one of its central organs effectively OFF and I did not notice.*
**AND THE EVIDENCE WAS IN MY OWN OUTPUT THE WHOLE TIME: the smoke printed `"n_provenance": 0` and
I read past it.** *A zero in a field I chose to emit, in a cell I wrote to catch exactly this class
of thing.* **Re-run the cell with periodic consolidation before quoting its ablation table again.**

### 🔎 AND THE CORPUS-TYPE FINDING SURVIVES, NOW QUANTIFIED INSTEAD OF 0-vs-0
At matched volume (750 sentences, one patch): **narrative grounds 97, encyclopedic grounds 38 --
2.5x.** *The substrate grounds where words RECUR, not where they are DEFINED. That inverts the
naive expectation and it is worth keeping: `definitional_extraction` wants encyclopedias and the
consolidation gate wants stories, and the forager currently serves neither deliberately.*

---

## 🧭 DIRECTOR'S CALL, 2026-08-19: **STOP OPTIMISING INTO THE CLOZE TASK. IT CANNOT SHOW A WIN.**
*Full-auto ruling, made rather than filed, and it changes what the next continuations do.*

**THE ARITHMETIC THAT FORCES IT.** The BEST number anywhere in today's diagnostic is **0.0300**
(exact co-occurrence, cosine-ranked). Our best route is 0.0150. **So the entire prize available
from fixing every representation defect I found is to CLIMB FROM 1.5% TO 3% AND TIE A FLOOR.** A
task whose ceiling is a tie with the dumbest available method is not an instrument for detecting
understanding -- it is a way to spend continuations.

**THIS PLAN ALREADY SAID SO, IN THE DEFERRED SECTION, BEFORE ANY OF TODAY'S RUNS:**
> *"PREFER TASKS WITH LARGE EFFECT SIZES OVER BUYING POWER ON A TASK WITH A TINY ONE. When a
> mechanism genuinely works you see pattern completion 0.20 -> 0.92, or leave@3 vs leave@8 on an
> identical patch. No CI needed. A whole day of gated word-meaning arms fought over 0.63 vs 0.55 --
> THAT GAP IS THE PROBLEM, NOT THE SAMPLE SIZE."*

**0.0075 vs 0.0300 IS THAT SHAPE AGAIN, ONE ORDER OF MAGNITUDE SMALLER.** *I wrote the warning
into this file yesterday and then spent four continuations inside exactly the failure it names.
The cell itself even declared "this task favours the floors by construction" in its own docstring.
I shipped the caveat and ignored it.*

**WHAT STAYS AND WHAT STOPS.**
- **KEEP:** the cell, the harness, the ablation machinery, `readout_verdict.py`, and the negative.
  **The Phase 2 result is real and it stands** -- the substrate memorises and does not transfer.
  That was worth establishing and it is established.
- **KEEP:** the two cheap correctness fixes, because every FUTURE measurement inherits them --
  add an `EXACT_COOC_COSINE` arm as the strongest floor, and fix the query construction (worth 2x).
  **They are hygiene, not a research programme.**
- **STOP:** treating cloze hit@1 as the substrate's report card. **No further mechanism gets built
  to move it.**

### ➡️ THE REPLACEMENT TASK, AND IT TESTS THE CLAIM THE SUBSTRATE ACTUALLY MAKES
The substrate's stated output is **an auditable store of facts, each traceable to the sentence it
came from**. It grounds ~19 terms per 400 sentences and **REFUSES 124** -- a gate that discriminates
7:1. *Nothing has ever asked whether the 19 are RIGHT.*

**BUILD: grounding PRECISION against an INDEPENDENT gold.** For each term the substrate grounds,
does its meaning-anchor match a definition from a source the substrate never read? **Effect size is
plausibly large** (a gate at 0.8-0.9 against a floor near 0.3), which is the whole point of the
switch. **Floors, all runnable from the cell's own data:** most-frequent-co-occurrent, the term's
own nearest neighbour by count, and a random anchor from the grounded set.
**⚠️ AND THE TRAP IS NAMED IN ADVANCE: the gold must not be WordNet if anything on the path
touches WordNet, and `lemma_word` DOES use WordNet morphy.** *Morphology is not meaning, so this is
probably admissible -- but it must be checked and stated, not assumed, and the alternative
(dictionary/Wiktionary definitions already on disk) is cheap.*

### ✅ THE GOLD IS SETTLED, AND CHECKED BEFORE ANY CELL WAS WRITTEN
`scratch/conceptnet_admissibility.py`. **ConceptNet's FULL assertions file carries a `dataset`
provenance field per edge, so WordNet-derived edges are EXCLUDABLE BY CONSTRUCTION.** Measured over
400,000 English-English edges: **78.2% `/d/wiktionary/en`, 18.0% `/d/conceptnet/4/en` (crowd),
and only 0.1% `/d/wordnet/3.1` -- 254 edges, all droppable.** *So an independent, non-WordNet,
non-LLM gold exists on disk and the circularity constraint is satisfiable.*

**🪤 AND THE CONVENIENT FILE IS THE TRAP, CONCRETELY.** `data/datasets/conceptnet5_en_100k.jsonl`
is pre-extracted, small and ready to use -- **and it has NO provenance field at all**, only
subject/predicate/object. **WordNet edges cannot be excluded from it, so it is INADMISSIBLE as a
gold** however convenient it is. *That is "the way we lose is by trying fancy available tools",
in one file, and it would have been invisible after the fact.*

**⚠️ SCOPE OF THAT MEASUREMENT, STATED: the assertions file is sorted by URI, so the 400,000 rows
scanned are an ALPHABETICALLY-ORDERED PREFIX, not a random sample.** *The WordNet share elsewhere
in the file may differ, and `/r/IsA` is likely under-represented by that ordering. A full-file
count is cheap and must be run before the gold is frozen -- do not quote 0.1% as a file-wide fact.*
**PROBES, NOT A CELL: one seed, one corpus, one task, NO CI. Not citable. They exist to pick the
next build.** `scratch/projection_loss_probe.py` + `probe2.py`. Identical items, identical frozen
vocabulary (2,161), identical 12,000-sentence corpus, **matched scale** -- only the
REPRESENTATION and the CUE differ.

| representation | hit@1 |
|---|---|
| **EXACT co-occurrence, cosine-ranked** | **0.0300** |
| random projection of the same, d=1024 | 0.0275 |
| random projection of the same, d=256 | 0.0225 |
| **OUR encoder, cue = sum of the cue words' own profiles** | **0.0150** |
| **`COUNT_FLOOR` -- the floor our cells have been using** | **0.0125** |
| **OUR encoder, cue = whole-sentence vector (what the substrate does)** | **0.0075** |
| random projection, d=64 | 0.0050 |

### 🚨 CORRECTION TO MY OWN PHASE 2 REPORT, AND IT MAKES THE NEGATIVE WORSE, NOT BETTER
**`COUNT_FLOOR` IS NOT THE STRONGEST FLOOR THIS DATA SUPPORTS. Cosine over the SAME co-occurrence
counts scores 0.0300 against its 0.0125 -- 2.4x.** The standing rule is *"run the STRONGEST floor
the cell's own data supports"*, and this archive has already refuted three cells for using a weaker
one. **I did the same thing today.** *The Phase 2 verdict does not flip -- no substrate route was
anywhere near either floor -- but "loses to counting by ~10x" was measured against the weak floor,
and against the right one the gap is larger. **Any re-run of that cell must add an
EXACT_COOC_COSINE arm.***

### 🎯 WHERE THE LOSS ACTUALLY IS, DECOMPOSED
- **projection:** 0.0300 -> 0.0225. Real, ~25%, and **NOT the main cost.** d=1024 recovers almost
  all of it; d=64 is catastrophic. *A d-sweep buys something here, unlike on addressing (C36).*
- **our encoder vs a plain random projection at the SAME d and scale:** 0.0225 -> 0.0150.
  **We lose 33% to a random projection of the same counts.**
- **🔴 CUE CONSTRUCTION: 0.0150 -> 0.0075. THE SINGLE LARGEST FACTOR MEASURED -- A FULL HALVING,
  AND IT IS WHAT THE SUBSTRATE ACTUALLY DOES.** Building the query as a whole-sentence vector
  costs twice as much as any representation choice in the table.
  ***⚠️ DO NOT CROSS THIS WITH "THE CUE SIDE IS CLOSED" (four cells, DO-NOT-REDO 46).*** That
  closure was a DIFFERENT scorer, population and instrument (partial-cue addressing, hit@1
  0.0223 -> 0.0249 NOT_SEPARATED). **This is a new measurement on a new task, not a contradiction
  of that one, and the two numbers may never appear side by side.**

**WHAT THIS CHANGES ABOUT THE NEXT BUILD: the information is present and usable -- our own counts,
ranked properly, beat the floor 2.4x. So the next move is NOT a fifth mechanism. It is to stop
discarding what we already have, and the cheapest lever measured is the QUERY.**

---

## 🔻 RETRACTED, SAME NIGHT, BY MY OWN NAMED RE-TEST: SR WAS **NOT** STARVED. D7 IS A REAL NEGATIVE.
**`exp_sr_scale_ladder_v1`, 3 seeds, 400 items, pool FROZEN at 2,161, nested corpora, only the
transition data varies. 63 s.** *The block below filed SR as UNTESTABLE-AT-THIS-SCALE and named
exactly one way to settle it. It is settled, and against me.*

| transitions/state | SR γ=0.1 | SR γ=0.9 | **COOC floor** | FREQ floor |
|---|---|---|---|---|
| 2.48 | 0.01417 | 0.01167 | 0.01917 | 0.00667 |
| 6.91 | 0.00917 | 0.00417 | 0.03417 | 0.00917 |
| 25.68 | 0.00417 | 0.00333 | 0.04417 | 0.00917 |
| **80.19** | 0.01250 | **0.00167** | **0.05833** | 0.00917 |

**ACROSS A 32x RANGE: THE CO-OCCURRENCE FLOOR TRIPLES (0.019 -> 0.058). SR γ=0.9 FALLS TO A
SEVENTH. SR γ=0.1 IS FLAT.** *The data increase is real and usable -- the floor proves it on the
identical corpus, items and frozen pool. SR simply cannot use it.* **At the top rung SR would have
to move 27.2 CI half-widths to reach the floor. That is RESOLVED, not underpowered.**
**PRE-COMMITTED READING (iii) FIRES: starvation is REFUTED as the explanation, and D7 over lemma
transitions is a REAL NEGATIVE.**

### 🔬 AND THE MECHANISM IS MEASURED, NOT NARRATED -- LONG-HORIZON SR BECOMES A CONSTANT
`scratch/sr_mixing_probe.py`. γ=0.9 is ~100 steps of lookahead; over a word graph that is far past
the mixing time, so `P^k` converges to the STATIONARY DISTRIBUTION, **which does not depend on the
cue.** More text connects the graph better and mixes it FASTER. Distinct top-1 answers over 300
DIFFERENT cues:

| rung | γ | distinct answers / 300 cues | share taken by ONE word |
|---|---|---|---|
| 750 | 0.9 | 160 | 17.7% |
| **40,000** | **0.9** | **31** | **83.7%** |
| 40,000 | 0.1 | 133 | 5.0% |

**AT SCALE, LONG-HORIZON SR ANSWERS THE SAME WORD TO 84% OF ALL QUESTIONS.** *That is the
constant/prototype floor's signature, and this project already knows that floor is often the
strongest thing in the room. We built a pinned equation and it converged into a baseline.*
**γ was SWEPT and the sweep is what made this legible: short horizon keeps cue-specificity (133
distinct) and still loses; long horizon destroys it. Had we ADOPTED one γ we would have learned
neither half.**

### ⚠️ WHAT I GOT WRONG, EXPLICITLY, SO IT IS NOT REPEATED
I filed SR as starved citing "median ONE successor per word" and a dose-response of
**0.00111 -> 0.00556**. *I flagged that comparison as not-a-slope because `n_read` AND `pool` both
moved.* **With the pool held FIXED the effect does not merely shrink -- it REVERSES.** The
apparent rise was the confound, exactly as flagged. **A caveat I wrote and then leaned on anyway.**

---

## 🔴 [SUPERSEDED BY THE RETRACTION ABOVE -- KEPT SO THE OVERCLAIM STAYS VISIBLE] D7 RESULT LANDED (spec `v2_sr`, 30 units, 1,564 s)
**Verdict COMPUTED by `tools/readout_verdict.py`, which encodes the pre-committed readings as code
so the reading cannot be done after seeing the table.** Held-out, 3 seeds, n=300, bar 0.0411:

| route | held-out hit@1 |
|---|---|
| SEMANTIC | 0.00556 |
| EPISODIC | 0.00444 |
| **SR (all three gammas)** | **0.00111 -- the WORST substrate route** |
| COOC floor | **0.02333** |

**Reading (e) did NOT fire: SR clears at NO gamma, so it is not even "the 1-step counter wearing a
matrix" -- it loses everywhere.** Verdict stands at **(c)+(d)**: a real negative, and the pipeline
is not reading the held-out cue.

### ⚠️ BUT FILING THIS AS "SR DOES NOT WORK" WOULD BE THE C33 ERROR AGAIN. MEASURED, NOT ASSERTED:
`scratch/sr_density.py` -- **4,596 observed transitions across 2,114 states, and the MEDIAN NUMBER
OF DISTINCT SUCCESSORS PER WORD IS 1.0.** *Half the vocabulary was seen followed by exactly one
other word.* **That is not a test of a predictive map; it is a test of an empty matrix.** For scale,
this project has twice called a channel STARVED at ~8.6 observations per word and at a median 130
arcs per word. **2.17 transitions per state is far below both.**

### 🎯 AND THE DOSE-RESPONSE IS ALREADY IN THE RUN, AS A NATURAL EXPERIMENT
The `foraging` ablation reads the full budget instead of letting the forager leave early:

| | sentences read | pool | SR_g0.9 | COOC floor |
|---|---|---|---|---|
| forager ON | 1,233 | 2,899 | **0.00111** | 0.02333 |
| forager OFF | 4,000 | 6,094 | **0.00556** | 0.01889 |

**3.2x the text moves SR 5x UP while the floor moves DOWN** (the pool more than doubled, so the
task got harder). *Exactly the direction the starvation hypothesis predicts and the opposite of
the floor's.* **⚠️ NOT a clean one-variable comparison -- `n_read` AND `pool` both changed -- so it
is DIRECTIONAL EVIDENCE, not a measured slope. State it that way or not at all.**

### 🪞 THE IRONY, AND IT IS A REAL WIRING FINDING: OUR FORAGER IS STARVING OUR SUCCESSOR MAP
H2's leave rule cut reading to **1,233 of 4,000** requested sentences. **The organ that most needs
data got the least, because another organ decided to move on.** *That is a genuine interaction
between two wired organs, and it is invisible unless both are in the same substrate -- which is
the first concrete argument this session that assembling them was worth doing.*

**FILED AS: `UNTESTABLE-AT-THIS-SCALE`, NOT `REFUTED`. Per discipline 18, if no achievable score
could clear the bar on the data supplied, the point is untestable rather than negative.**
**THE NAMED RE-TEST: rebuild SR on 10-50x the transitions and re-measure. If it still does not
move, THAT is the negative -- and it will be a real one.**

---

## 🧠 BRAIN-FIDELITY DRILL ON THE PHASE 2 NEGATIVE (owed under discipline 17) -- AND IT FOUND THE GAP
`notes/brain_fidelity_drill_memorises_but_does_not_transfer_2026-08-19.md`.

**THE REFRAME: WE MEASURED A HIPPOCAMPUS AND REPORTED THAT IT IS NOT A NEOCORTEX.** An episodic
store that recalls its own episodes almost perfectly (0.9333) and transfers nothing to a new
context (0.0044) **is behaving exactly like the structure we copied** -- pattern separation makes
similar inputs MORE distinct, deliberately. *That is D3 working, not D3 failing.* Generalisation is
the slow system's job and **the transfer mechanism between them is REPLAY.**

**THE GAP IS EMBARRASSINGLY CONCRETE AND WAS ENUMERATED ON DISK, NOT GUESSED:**
`hdlab/hippocampal_encoder.py` ALREADY CONTAINS **`cls_replay_cycle`** and
**`cls_discrete_budget_consolidate`**. A grep across `hdlab/ tools/ experiments/ verification/
notes/` returns them in **exactly two files -- their own module and one witness.**
> **NO EXPERIMENT CALLS THEM. NOTHING LIVE CALLS THEM. THE SUBSTRATE I BUILT TODAY WRITES 3,400
> EPISODES AND CONSOLIDATES NONE OF THEM.** *We replicate the fast store and substitute NOTHING
> for the slow one; the transfer step is simply absent and its organ has sat built and unused.*

**NEXT BUILD, PRE-REGISTERED WITH FOUR WAYS TO FAIL** (A consolidation is the missing step / B it
helps but is not the answer / C replay over our codes carries no transferable structure / D it
needs implausibly many replays, which is an admission the machinery is wrong). **Mandatory: a
RATE-MATCHED RANDOM-REPLAY twin**, floors rebuilt on the consolidated representation, and a
rank-matched null -- *because held-out sits BELOW its floor, and destroying information moves a
sub-chance score TOWARD chance and reads as progress.*

**🛑 AND THE DRILL CORRECTED ITSELF BEFORE THE BUILD, WHICH IS THE POINT OF WRITING IT DOWN FIRST.**
Reading `cls_replay_cycle` at HEAD: it trains `cortex_W [dg_dim, dg_dim]` on
`outer(code, settle(code))` -- **an autoassociator over the SAME sparse pattern-separated codes**,
and its own docstring calls itself a minimal self-test scaffold whose real cortex *"would receive
PROJECTED codes rather than raw DG"*. **Replaying separated codes into their own space re-learns
the separation; it cannot generalise. Running it would have produced a guaranteed null that I
would have filed as reading (C) -- a property of my choice of target, not of replay.**
***WE HAVE THE REPLAY MACHINERY AND NO CORTICAL TARGET REPRESENTATION TO REPLAY INTO.*** The slow
system's whole point is DENSE OVERLAPPING codes, so shared structure superimposes and
episode-specific detail cancels. **Corrected build: replay into the DENSE context vectors, keep
the DG-space arm as the control that CANNOT work.**
**⚠️ HONEST DEFLATION, PRE-DECLARED: a dense accumulated per-word profile is VERY CLOSE to the
`SEMANTIC` route that already read 0.005.** *If the corrected build is only "that route again, fed
by replay", it is a REPLICATION of a measured null and must not be dressed as a new mechanism. The
one real difference is the SELECTION and REPEAT structure replay imposes -- so that is the
variable, and the rate-matched random-replay twin is what isolates it.*
**⚠️ Written before the build precisely because MY LAST PREDICTION IN THIS AREA WAS REFUTED INSIDE
ONE RUN.** *That refutation tested the parallel context accumulator, which is never fed by replay,
so it does not pre-empt this -- but a second bite needs its own stated way to be wrong.*

---

## 🆕 PHASE 3 STARTED -- D7 SUCCESSOR REPRESENTATION IS BUILT: `hdlab/successor_representation.py`
**`M = (I - gamma*P)^-1`. The only slot where the brain hands us a closed form and we had written
none of it.** Five self-tests PASS, and they are can-fail rather than plausibility checks: the
defining identity `M = I + gamma*P*M` to 1e-8 across four gammas; `gamma=0` reduces to `I`;
dead rows do not make the solve singular; **a PLANTED successor is recovered above a
frequency-matched decoy that never follows the cue**; and **the online TD rule converges to the
closed form** (6.1% relative error) -- so the mechanism can be checked against the thing it is
meant to compute rather than against a hope.

**WHY THIS ONE, AND NOT JUST BECAUSE IT WAS TOP OF A LIST.** Phase 2 says the missing ingredient is
a LEARNING SIGNAL. SR supplies one that is actually admissible here: **self-supervised from the
corpus's own transitions, derived from NO gold, NO WordNet, NO LLM** -- and the circularity trap
that disqualifies almost every other supervision candidate does not touch it.

**PINNED vs OURS, stated because presenting an invention as pinned is barred:** the COMPUTATION
(discounted expected future occupancy) is PINNED. **That a "state" is a LEMMA is OUR INVENTION
UNDER TEST** -- the brain's SR runs over places. **`gamma` is SWEPT (0.1 / 0.5 / 0.9) and never
adopted**: our worst result copied a pinned NUMBER, our best copied an OPERATION.

**⚠️ THE UNFLATTERING PREDICTION, PRE-REGISTERED IN THE MODULE BEFORE ANY NUMBER: M IS A
DISCOUNTED MULTI-STEP CO-OCCURRENCE STATISTIC AND OUR FLOOR IS THE 1-STEP ONE.** If SR only wins
at small gamma it is the 1-step counter wearing a matrix and must be reported as such.

**FIRST SMOKE, AND ONE BUG WORTH KEEPING VISIBLE: SR READ EXACTLY 0.0000 IN EVERY CELL.** Not a
result -- an artifact of the equation. `M = I + gamma*P + ...`, so **the IDENTITY TERM puts every
cue word at the top of its own ranking**, and the target is masked out of the cue by construction,
so hit@1 was zero by definition. Excluding the cue's own words fixes it, **and the SAME exclusion
was applied to the COOC floor** so the arms still differ in route and nothing else.
*Smoke after the fix (n=60, nothing resolved): SR 0.25 / 0.28 / 0.20 at exact key against COOC
0.217, and 0.0167 held-out against COOC 0.083.* **SR is the best substrate-side route on held-out
text and is still losing to counting.** **FULL RUN IN FLIGHT**, `scratch/p2_full_v2.pid`.
*Unit keys carry a `SPEC_VERSION`, so the 15 already-checkpointed v1 units cannot be silently
served for a changed specification -- which is exactly what would have happened.*

---

## ✅ PHASE 2 FULL RUN LANDED (`data/exp_substrate_end_to_end_readout_v1/metrics.json`, 15 units, 605 s)
**PRE-COMMITTED READING (c) FIRED: no substrate route beats the strongest floor, and the
instrument is alive.** simplewiki, 3 seeds, n=300 items per regime, pool 2,114, chance 0.00047.

| arm | SEEN (exact key) | **HELD-OUT (the real point)** |
|---|---|---|
| EPISODIC | **0.9333** clears bar, p=0.0005 | **0.0044** -- CI upper ~0.0105, **BELOW the 0.0367 bar** |
| SEMANTIC | 0.2789 clears bar | **0.0056** -- below the bar |
| **COOC floor** (~~strongest~~ **NOT the strongest -- see below**, standalone) | 0.1700 | **0.0233** |
| FREQ floor | 0.0011 | 0.0078 |
| ORTH floor | 0.0000 | 0.0033 |
| **SCRAMBLE twin** | **0.0011**, p=0.0005 vs EPISODIC | **0.0033, p = 0.48 / 0.64 / 1.00** |

**🚨 READING (d) ALSO FIRED, ON THE HELD-OUT REGIME ONLY, AND IT IS THE HEADLINE: FEEDING THE
SUBSTRATE AN UNRELATED SENTENCE SCORES THE SAME AS FEEDING IT THE REAL ONE (0.0033 vs 0.0044,
p up to 1.00). ON NEW TEXT IT IS NOT READING THE CUE AT ALL.** *At exact key the same twin
separates at p=0.0005, so the pipeline demonstrably CAN read -- which is what makes the held-out
tie a result rather than a broken cell.*

**THE ONE-SENTENCE FINDING: THE STORE MEMORISES EPISODES ALMOST PERFECTLY (0.93 at exact key) AND
TRANSFERS NOTHING TO A NEW CONTEXT (0.004, tied with its own scramble, beaten 5x by counting).**
*And the task is NOT impossible: a co-occurrence counter reaches 50x chance on it.*
**This is ORGAN A's conclusion reached end-to-end through the assembled substrate on a different
task and a different instrument -- perfect storage, no generalisation, and the missing ingredient
is the learning signal. Assembly did not supply it, and was never going to.**

### ABLATIONS -- TWO ORGANS CONTRIBUTE EXACTLY NOTHING, AND ONE ARM IS VOID
| ablation | effect |
|---|---|
| `definitions` (R1) | **ZERO change in EVERY number, both regimes, all 3 seeds.** |
| `gap_detector` (H1) | **ZERO change** -- and already known to be untestable while the foundation is near-empty. |
| `episodic` (D3) | exact-key 0.9333 -> **0.0000**. It IS the organ doing the memorising. Held-out 0.0044 -> 0.0000: nothing to lose. |
| `foraging` (H2) | **VOID IN THIS RUN -- DO NOT READ IT.** |

**⚠️ THE FORAGING ARM IS UNMATCHED AGAIN, IN THE OPPOSITE DIRECTION, AND IT IS THE SAME DEFECT I
"FIXED" ONE CONTINUATION EARLIER.** The forager LEFT its patch after **1,233** of 4,000 requested
sentences; my frozen quota is the whole budget, so FROZEN read **4,000**. *Last time frozen read
too LITTLE; I matched on the budget instead of on what the live arm actually consumes, and it now
reads too MUCH.* **FIX: run the live arm FIRST, then give the frozen twin exactly its sentence
count.** *Twice in two days on the same control. Rate-matching is not a step to add at the end.*

---

## 🧪 PHASE 2 CELL BUILT AND SMOKE-CLEAN: `experiments/exp_substrate_end_to_end_readout_v1.py`
**FULL RUN IN FLIGHT** on `simplewiki`, detached, PID in `scratch/p2_full.pid`, logs
`scratch/p2_full.out` / `.err`, 3 seeds x 5 ablations = 15 checkpointed units -> `data/<cell>/`.
**DO NOT RESPAWN IT** -- a duplicate is the more expensive error.

### 🚨 PHASE 2 FINDING #2 -- THE OBVIOUS SCRAMBLE CONTROL IS A NO-OP, AND IT TIED THE REAL CUE EXACTLY
**A word-ORDER scramble against a BAG-OF-WORDS cue is the same vector.** Measured: shuffled cue
`hit@1 0.7` vs real cue `0.7`, **permutation p = 1.0000**. *That is not a weak control, it is a
no-op wearing a control's name* -- the same class as the corruption control that was
near-rank-preserving and "incapable of failing", and as the coverage control that dropped 0 of 242.
**Pre-committed reading (d) fired on it as designed, which is the only reason it was caught.**
**THE FIX, AND IT IS THE RECIPE THE READING LOOP ALREADY OWNS** (`scramble_context_source`):
destroy the cue's CONTENT, not its ORDER -- swap in an unrelated sentence, keeping the target.
**Rebuilt that way it BINDS HARD: exact-key EPISODIC 0.667 vs SCRAMBLE 0.017, perm p = 0.0005.**
**🔎 LEAD CHASED, AND IT IS GOOD NEWS -- THE DEFECT IS NOT WIDESPREAD. `tools/scramble_control_audit.py`.**
Enumerated by `os.walk` over `experiments/ hdlab/ tools/ verification/`, **all 13,553 `.py` files,
no sampling, rows-scanned printed before results.** Of 66 files that declare a scramble control AND
carry an order-invariant scorer: **HIGH = 0**, 26 already use the CORRECT content-destroying
recipe, 23 CHECK (they scramble by a route the token regex cannot see -- index arrays, `sample` --
and need reading), 17 declare a scramble with no visible shuffle (several are prose mentions).
**No landed cell pairs a word-order shuffle with a bag scorer and nothing order-sensitive. The
defect was mine, in a cell written today, and it did not propagate.**
***SCOPE OF THAT ABSENCE CLAIM, STATED: `HIGH` requires the word "scramble" to appear. A cell that
scrambles without naming it would not be seen.*** *The tool's own first version keyed on the
shuffle's TARGET NAME and found 1 file in 13,553 -- it would have reported this defect as absent
because my regex was narrow, not because the code was clean. Rebuilt LABEL-FIRST, and the
self-test now asserts it still catches a shuffle of an INDEX ARRAY.*

### ✅ AND THE UNBIASED ITEM SELECTION MOVED THE FLOORS EXACTLY AS PREDICTED
Replacing "first known lemma" with a seeded RANDOM known lemma dropped the COOC floor from
**0.255 to 0.083** -- confirming the selection bias I named was inflating it. **The substrate did
not benefit: both its routes read 0.000 on held-out cues under the fair selection.** *At smoke n=60
the margin vs floor is `perm p = 0.065`, so this is a WIDTH, not yet a resolved negative. That is
what the full run is for.*

---


## 🚨 [SUPERSEDED TWICE -- READ THE TWO CORRECTIONS BEFORE THE NUMBERS] PHASE 2 FINDING #1 -- THE ASSEMBLED SUBSTRATE LOSES TO WORD-COUNTING BY ~10x ON HELD-OUT TEXT
> **⛔ SUPERSEDED-BY, added 2026-08-19 rather than left for the next reader to trip over:**
> **(1) THE "~10x" IS AGAINST THE WRONG FLOOR.** `COUNT_FLOOR` is NOT the strongest floor the data
> supports -- cosine over the SAME co-occurrence counts scores **0.0300 against its 0.0125**. The
> real gap is LARGER, not smaller. See the diagnostic block above.
> **(2) THE CONSOLIDATION ORGAN NEVER FIRED IN THIS CELL.** It ran `max_patches=1`, and the
> substrate only consolidated when the forager changed corpus, so **every Phase 2 run grounded
> NOTHING**. The retrieval result stands -- both routes read from episodic writes and Library
> traces, which happen regardless -- but the ablation table must be re-run before it is quoted.
> **(3) ADDED 2026-08-19 WITH THE EVIDENCE, WHICH IS SHARPER THAN (2) AND CHANGES WHAT THE
> ABLATION NULL MEANT.** Re-read off disk (`scratch/phase2_cost_probe.py`): **`n_provenance` is 0
> on ALL 30 units, no exceptions**, and the `definitions` and `gap_detector` ablations returned
> **BIT-IDENTICAL episode counts to the control -- 8,394 in every single unit**. Those two organs
> feed the grounding path, and the grounding path never ran. **So "definitions and gap_detector
> change EXACTLY NOTHING" was the bug restated, NOT a measurement of two organs** -- and two slots
> the substrate calls FILLED were resting on it. *Also visible in the same data: the foraging twin
> read 4,000 sentences against the live arm's 1,150, 3.5x more text.*
> **THE CELL IS BEING RE-RUN AS `v3_consolidation`, DEMOTED FROM A REPORT CARD TO A WIRING
> DIAGNOSTIC.** Its score stays retired (best achievable 0.0300 vs our 0.0150 -- fixing every
> defect wins a tie with a floor); what it is for is one pre-registered question: **with
> consolidation firing, does the read-out change AT ALL?** A new `consolidation` ablation decides
> it, and its binding is proven BOTH WAYS by a substrate self-test (on -> 30 provenance rows and
> 91 refusals; off -> 0 and 0). **That two-way proof is the point: an ablation asserted only by
> "the ablated arm grounds nothing" would have PASSED on the broken run.**

**The first end-to-end measurement of the assembly, and it is a clean negative that INDEPENDENTLY
REPLICATES THIS PROJECT'S CENTRAL DOCUMENTED RESULT on a different task, a different instrument
and a different route.** `scratch/recall_route_compare.py`, 400 sentences read, 200 items,
pool 996, one corpus, one seed. **No CI yet, so these are measurements and not yet a verdict.**

| route | SEEN (exact key) hit@1 | **HELD-OUT hit@1** |
|---|---|---|
| EPISODIC (DG code overlap after CA3 settling) | **0.795** | **0.025** |
| SEMANTIC (cosine to the accumulated context profile) | 0.165 | **0.005** |
| **COOC floor** (raw co-occurrence counting) | **0.320** | **0.255** |
| **FREQ floor** (ignores the cue entirely) | 0.170 | **0.265** |

**⛔ NEVER QUOTE 0.795 AS A CAPABILITY.** The cue at exact key IS the vector the episode was
written from -- the same write-then-read-a-register shape that refuted
`exp_causal_link_comprehension_fuller_v2` ("no comprehension was tested"). **It is a CEILING
DIAGNOSTIC and it is doing one useful job: it proves the store, the encoder and the scorer all
work, so the held-out collapse is a REAL NEGATIVE and not a broken instrument.**

**THE NUMBER THAT MATTERS: on sentences it never read, the substrate scores 0.025 where COUNTING
WORDS SCORES 0.255, and where a floor that DOES NOT LOOK AT THE CUE AT ALL scores 0.265.**

### ❌ AND MY OWN BRAIN-FIDELITY PREDICTION WAS REFUTED IN THE SAME RUN, BEFORE IT COULD BE QUOTED
I predicted the episodic collapse was us asking the WRONG ORGAN -- the dentate gyrus exists to make
similar inputs DISSIMILAR, so pattern separation is the enemy of generalisation, and the
consolidated semantic route should therefore do better. **IT DOES NOT. SEMANTIC IS 5x WORSE THAN
EPISODIC ON HELD-OUT CUES (0.005 vs 0.025), and raw co-occurrence counting beats it in BOTH
regimes, including at exact key (0.320 vs 0.165).** *The elegant story was wrong and its own
control killed it inside one run. Recorded because the reasoning will look attractive again.*

### 🎯 WHAT IT ACTUALLY CONVERGES ON, AND THIS IS THE VALUABLE PART
**Our "semantic profile" is a SUM of context bags, and it is beaten by literally counting the same
co-occurrences.** That is exactly the ORGAN A write-rule result -- summing raises interference,
single-occurrence beats the sum, and no unsupervised transform extracts substitutability --
**reached again end-to-end through the assembled substrate on a retrieval task, rather than on the
dissociation instrument.** *Two instruments, two tasks, two populations, one diagnosis: the
missing ingredient is the LEARNING SIGNAL, and assembling the organs did not supply it.*

**CAVEATS THAT TRAVEL WITH EVERY NUMBER ABOVE:** n=200, ONE corpus (children's fiction), ONE seed,
NO confidence interval and NO null yet -- that is what the Phase 2 cell is for. **And a named
selection bias: items are the FIRST content lemma of each sentence that the store has seen, which
skews toward frequent words and INFLATES both floors.** *It does not rescue the mechanism -- the
gap is ~10x, not marginal -- but the cell must select items without that bias.*

---

## 🔬 PHASE 2 IN PROGRESS -- THE ABLATION HARNESS EXISTS AND IT HAS ALREADY PAID FOR ITSELF

`Substrate(ablate=[...])` supports four one-organ-at-a-time ablations. **Smoke run, 400 sentences,
2 corpora, one seed -- OBSERVATIONS, NOT RESULTS: no CI, no null, n=1, and they are not to be
quoted as findings until the cell runs.** They already change what to build.

| ablation | what moved | reading |
|---|---|---|
| `episodic` (D3 off) | **ONLY its own counter** (3400 -> 0) | **I WIRED THE EPISODIC STORE AS A WRITE-ONLY SINK.** 3,400 encounters written, nothing reads them. Provenance, refusals, profiles all bit-identical. *This is MY wiring defect, not the organ's -- `hippocampal_encoder.retrieve` exists and I never call it.* **BUILD TARGET.** |
| `definitions` (R1 off) | **ONLY its own counter** (5 -> 0) | the `definition_map` handed to `checkpoint()` changed NOTHING about what grounded. **Under-powered on fiction (5 definitions in 400 sentences) -- re-run on SimpleWiki before concluding anything.** |
| `gap_detector` (H1 off) | **NOTHING AT ALL** | **AND IT IS UNINFORMATIVE, NOT A NULL -- READ THE NEXT BLOCK BEFORE QUOTING IT.** |
| `foraging` (H2 off, rate-matched) | 7 of 8 counters | **FROZEN reads the SAME 400 sentences and grounds 9 where the forager grounds 19.** It touches MORE lemmas (1,320 vs 1,137) and grounds FEWER -- spreading thinner, which is what MVT says foraging avoids. |

**⚠️ THE H1 ABLATION CANNOT SUCCEED AND MUST NOT BE FILED AS A NEGATIVE.** Verified rather than
assumed (`scratch/gapcache_values.py`): the real detector and a stub that always answers GAP agree
on **all 1,137 shared lemmas, zero disagreements**. The 19 lemmas the cache marks known are
**exactly the 19 grounded words**, written back by the consolidation path, not by the detector.
**But the foundation starts with 107 seed words and nothing else, so every content word in
children's fiction genuinely IS a gap. The detector is answering correctly; the question has one
true answer at this scale.** *Discipline 17's first clause: establish the experiment could have
succeeded before concluding anything from it.* **RE-TEST H1 AGAINST A POPULATED FOUNDATION.**

**AND TWO OF MY OWN CONTROLS WERE DEFECTIVE BEFORE THEY WERE FIXED, WHICH IS THE POINT OF RUNNING
CONTROLS ON CONTROLS:**
1. **The foraging twin was NOT rate-matched.** A fixed harvests-per-patch constant let FROZEN read
   **150 sentences against the forager's 400**, so every downstream difference was attributable to
   reading LESS rather than to choosing worse. **That is the unmatched-twin defect that killed four
   apparent wins in this project's own record, rebuilt from scratch by me.** Now splits the same
   budget across the same patches; both arms read exactly 400.
2. **Ablating H1 by setting `state.gap_detector = None` CRASHED** (`is_gap` calls `.familiarity()`
   unconditionally) -- and would have been the wrong control anyway, since removing the call
   changes the PATH rather than the ANSWER. Replaced by a stub with the interface intact and the
   discrimination removed.

---

## PHASE 2 -- THE RISK, AND IT IS THE MOST IMPORTANT STEP IN THIS PLAN

**EVERY ORGAN HERE WAS VALIDATED IN ISOLATION. WIRING TEN TOGETHER IS PRECISELY HOW THE 0-FOR-30
CLAIMS LAYER HAPPENED -- components that each look fine and produce nothing jointly.**

**THE DELIVERABLE IS ONE CELL: `experiments/exp_substrate_end_to_end_readout_v1.py`.**
Per CLAUDE.md this is `hdi_exp_dev`'s lane; if agent dispatch is unavailable in the running session,
author it in the main thread **with every gate below intact** -- the gates are the point, the lane
is not.

**The gates, and none is optional:**
- text in, traceable facts out, **on a corpus the mechanism did not see**;
- **a REAL floor run STANDALONE** -- the dumbest thing that scores well on this data. Run the
  STRONGEST floor the cell's own data supports, not the most convenient one. Report how many items
  each control actually removed: **a control that excludes nothing is not a control.**
- **a scramble twin** -- if scrambled text produces the same output, the pipeline is not reading;
- **CI half-width AND the null p95 beside every margin**, and gate on the FLOOR'S UPPER BOUND
  (floor + its own half-width), never its point value;
- **an ORGAN-ABLATION arm per wired organ** -- turn one off, re-run, report the delta. *This is the
  only thing that distinguishes an assembled substrate from an expensive `Counter`, and no cell in
  this archive has ever run it.*
- **and the first question, free and non-statistical: DID THE TEST ITEMS EXIST BEFORE THE MECHANISM
  DID?** State the answer in the metrics. That predictor beat every statistical signal in the audit.

**PRE-COMMIT THE READINGS BEFORE ANY NUMBER EXISTS:** (α) beats the floor CI-separated AND at least
one ablation degrades it -> the assembly is doing work, name which organ. (β) beats the floor but NO
ablation moves anything -> **the floor is what is scoring, the organs are decoration** -- report it
that way, do not soften it. (γ) does not beat the floor -> a real negative; go to the brain-fidelity
drill (discipline 17), and ask FIRST whether the experiment could have succeeded at all.

**This test does not currently exist. Nothing downstream should be trusted until it does.**

---

## PHASE 3 -- BUILD THE EMPTY SLOTS (this is where the real gain is)

Ranked. **The first is the only slot where the brain hands us a closed form and we wrote none of it.**

1. **D7 successor representation -- EQUATION FULLY PINNED: `M = (I - gamma*P)^-1`.** Highest
   value-per-effort in the document.
2. **Q2 domain-general inference -- EMPTY, and it is a WHOLE NETWORK.** `multi_hop`'s default
   `beta = n_dim` collapses its softmax to a Dirac delta (identical to argmax); its own code says
   two prior cells were confounded by this. **This explains `reasoner` matching a similarity
   baseline on 38 of 40 questions -- not a broken reasoner, a missing network.**
3. **P1/P2 answer production -- EMPTY.** `generation.py` returns codebook INDICES: no lemma stage,
   no morphology, no string. Its docstring admits its test regime "cannot fail by construction."
   **This is the slot the no-LLM invariant created and nobody wrote down.**
4. **D5 working memory -- EMPTY, and the filename is a trap.** `working_memory.py` is 116 lines of
   assertion guards, and it is LIVE.
5. F5 coherence monitor, F6 multi-sentence integration.
**NOT a build target: E4 discourse bridging** -- two measured nulls, one the owner's own mechanism,
CI-separated BELOW neighbour-copying.

**FREE LEAD, hypothesis-pending-VET:** `information_foraging.SurpriseSegmenter` (`:194-224`) is a
literal Event Segmentation Theory boundary detector **already built**, sitting in a module nobody
imports, never run on discourse. It fills the "no prediction-error segmentation" gap the organ map
lists as missing.

---

## ✅ MIDDLE_BAND MINED -- `tools/middle_band_miner.py`. TWO CORRECTIONS TO THIS PLAN'S OWN PREMISE.

**CORRECTION 1 -- THE POPULATION IS 580, NOT 117.** Enumerated by walking **all 8,148 result
directories** under `data/` (the 117 figure came from the index's `data/exp_*` scan; results also
live under `data/results`, `data/lambda_batch_results`, `data/skypilot_results` and ~60
`substrate_*` directories). **Meaning-relevant MIDDLE_BAND: 580. HARD_PASS: 1,359.**

**CORRECTION 2 -- AND IT IS THE ONE THAT MATTERS, BECAUSE THE OWNER AUTHORISED WORK ON THIS
RATIONALE. THE STATED MECHANISM IS NOT SUPPORTED.** This plan said MIDDLE_BAND "is where the
HONEST SELF-ASSESSMENTS went". Measured with the **IDENTICAL detector on both tiers** (same
directories, same fields, only the tier pattern differs -- a cross-tool comparison would have been
the very thing discipline 11 forbids):

| property | MIDDLE_BAND | HARD_PASS | |
|---|---|---|---|
| **states a limitation about itself** | **4.5%** | **3.0%** | **NO REAL DIFFERENCE -- the stated rationale fails** |
| carries a CI | 10.3% | 5.4% | MB nearly 2x |
| carries a floor | 76.4% | 69.2% | MB higher |
| carries a scramble | 24.1% | 19.5% | MB higher |
| carries a held-out split | 23.6% | 20.2% | MB higher |
| carries a null | 4.0% | 2.7% | no real difference |

**SO THE PREMISE IS HALF RIGHT AND THE HALF THAT SURVIVES IS NOT THE HALF WE ARGUED.** MIDDLE_BAND
IS modestly better-evidenced -- **twice as likely to carry a confidence interval** -- but **it is
NOT a population characterised by honest self-assessment: 4.5% is not a culture of caveats, it is
a rounding error, and HARD_PASS is at 3.0%.** *The mining stays worth doing on the evidence
gradient. The story we told about WHY must not be repeated.*

**THE READ LIST IS RANKED BY HOW MUCH MECHANISM IS IN THE CELL, and the top of it is substantive:**
`exp_bootstrap_passage_context_binding_fade_v4` (discourse-level passage-context binding under a
fairness lockdown), `exp_agreement_attractor_role_binding_cg_viability_v1` -- **whose own
`honest_scope` names its real discriminator and rejects the trivial one**: *"Beating nearest-noun
is trivial here... the HONEST discriminator is beating the FIRST-NOUN positional heuristic on the
subject-not-first subset"* -- and `exp_grounding_quality_readout_v1`, which opens its limitations
with ***"THIS CELL MEASURES NO QUALITY."*** *Those three are exactly the honesty the premise
predicted; the measurement says they are the 4.5%, not the norm.*

**NOTHING MINED HERE IS CITABLE.** `tools/vetting_ledger.py --cite` still governs and still
refuses every one of them.

---

## PARALLEL TRACK -- MINE MIDDLE_BAND (owner: "it's worth it")

**117 meaning-relevant cells, never read.** Owner's framing, and it changes the brief:
*"understanding what it was trying and the signal may be very important for the harder to obtain
capabilities."* **READ FOR THE ATTEMPT AND THE SIGNAL, NOT FOR THE VERDICT.**
**Why this population and not HARD_PASS: selecting on HARD_PASS SELECTED FOR OVER-CLAIMING.** Two
cells were found whose honest tier was MIDDLE_BAND while an over-claimed sibling took HARD_PASS.

---

## DEFERRED, WITH A TRIGGER

**Instrument rebuild.** Both bars carry CIs including chance (0.5431 CI [0.4922, 0.5953]; 0.5943 CI
[0.4937, 0.6911]); at n=242 the half-width (~0.05) is as large as the whole chance-to-bar interval
(~0.04). **Nothing in Phases 0-3 uses it.** **TRIGGER: rebuild before the next GATED WORD-MEANING
experiment.**
***AND THE DEEPER POINT, WORTH MORE THAN THE POWER FIX: PREFER TASKS WITH LARGE EFFECT SIZES OVER
BUYING POWER ON A TASK WITH A TINY ONE.*** When a mechanism genuinely works you see pattern
completion **0.20 -> 0.92**, or **leave@3 vs leave@8 on an identical patch**. No CI needed. A whole
day of gated word-meaning arms fought over **0.63 vs 0.55** -- that gap is the problem, not n.

---

## STANDING RULES THAT MUST SURVIVE COMPACTION

- **`tools/substrate_query.sh` RETURNS ZERO BYTES AND EXITS 0.** Use `tools/experiment_index.py`,
  which prints rows scanned BEFORE results.
- **A HARD_PASS is an UNVERIFIED CLAIM** (30 vetted, 1 upheld). Check `tools/vetting_ledger.py
  --cite NAME` before citing anything.
- **The organ layer is a DIFFERENT population** -- 163/163 import, 83/87 self-tests pass. Do not
  import the claims base rate into it.
- **AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NEVER A SEARCH.** Four of my errors this session were
  this one fault.
- **ASK WHAT THE OPERATOR INTENDED BEFORE NAMING SOMETHING A DEFECT.** The remote is idle BY INTENT;
  results were deliberately SSH'd back. I called both defects.
- Never bundle a deletion with real work. Never `git add -A`. `data/foundation/` is READ-ONLY, one
  disk, no backup. Origin push needs USER AUTH.
