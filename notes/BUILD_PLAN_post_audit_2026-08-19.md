# BUILD PLAN -- WHAT TO DO NEXT, POST-AUDIT. START HERE.

> # 🎯 **RESOLVED -- AND THE CONFIGURATION WE ACTUALLY RUN HAS NEVER BEEN MEASURED BY ANY CELL.**
> *Un-correcting my own correction: the graded-query evidence is REAL. It is in
> `exp_graded_divisive_comparator_v1`, not in the cell the docstring's prereg reference pointed me
> at, which is why I could not find it and wrongly called it unverified.*
>
> | arm | accuracy | |
> |---|---|---|
> | `R_LIVE` -- **fully QUANTISED** | 0.6395 | what "live" meant on 2026-08-13 |
> | `R_BASE` -- **fully GRADED** | **0.69975** | **delta +0.0602** |
> | `F_LOCAL_SCRAM` / `F_BASE_SCRAM` | 0.4953 / 0.5065 | scramble floors |
> | `B_FREQ` | 0.4800 | cue-blind frequency floor |
> | positive control, self-retrieval | **0.9133** vs floor 0.70 | ✅ passes |
>
> **Clean floors, a working positive control, and the delta is real.** *The near-identity with F3's
> `0.060289` is a genuine coincidence between two different cells measuring two different things --
> comparator accuracy vs read-out stability.*
>
> ## 🚨 **AND HERE IS THE PART THAT MATTERS: WE RUN NEITHER ARM.**
> Those two arms are the two PURE configurations. **The live path today is the MIXED one:**
> - `GRADED_COMPARATOR` was flipped True on **2026-08-14** -- AFTER this 2026-08-13 cell -- so the
>   **ANCHORS are now graded** (`bundle()` returns the raw sum; verified at runtime today).
> - **The QUERY is still signed**: `canonicalize` line 776 hardcodes `np.sign(new_raw_sum)`, with no
>   graded option, and it takes **451 of 451 live selection calls** (`canonicalize_fast`, the only
>   graded-query door, takes **0**).
>
> **So `R_LIVE` (both quantised) is NOT what we run, and `R_BASE` (both graded) is NOT what we run.
> We run signed-query-against-graded-anchors, and NO CELL HAS EVER MEASURED THAT ARM.**
> **⚖️ AND IT IS THE ONE COMBINATION THE CODE'S OWN DOCSTRING SINGLES OUT AS WORST:**
> > *"a graded field read by a signed query is worse than either, because the query's magnitudes are
> > exactly what the field's magnitudes are being compared to."*
> **⚠️ SCOPE, HONESTLY: that this is worse than both is an INFERENCE from the docstring plus the
> dates plus the runtime call counts. It is NOT measured. The measurable claim is only that the
> configuration we ship is unmeasured -- which is itself the finding.**
> **➡️ THE CHEAP DECISIVE RUN: score all THREE arms -- both-signed, both-graded, and the mixed one we
> actually ship -- on the same items and floors. If mixed lands below both, a one-line change to
> `canonicalize` recovers a measured +0.06 with clean floors behind it.**

> # 🚨 **THE ENTIRE READ-OUT FIX SUBSYSTEM IS DEAD CODE ON THE LIVE PATH -- `canonicalize_fast`**
> # **IS CALLED *ZERO* TIMES WHILE READING. AND I CLOSED THE SIGN HYPOTHESIS THIS MORNING ON HALF**
> # **AN INSPECTION.**
> *Runtime evidence, not grep -- both functions monkeypatched and counted through a real 1,500-
> sentence read:*
>
> | | live calls over 1,500 sentences |
> |---|---|
> | `canonicalize` -- **SIGNED query, `np.sign(new_raw_sum)` hardcoded at line 776** | **451** |
> | `canonicalize_fast` -- graded query when `readout=None`, and the ONLY door to `ReadoutConfig` | **0** |
>
> ## ⛔ **CORRECTION TO MY OWN CLOSURE FROM THIS MORNING**
> I wrote: *"the sign hypothesis is REFUTED BY CONSTRUCTION -- `GRADED_COMPARATOR` has been True
> since 08-14, verified at RUNTIME, the profile path has no sign step."* **I checked the ANCHOR side
> only.** `bundle()` and `anchor_matrix()` are indeed graded -- **and the QUERY is signed on 100% of
> live selection calls.** The code's own docstring says why that is the worst of both:
> > *"a graded field read by a signed query is worse than either, because the query's magnitudes are
> > exactly what the field's magnitudes are being compared to."*
> **So the sign hypothesis is NOT closed. It is half-closed, and the open half is the live half.**
>
> ## 📉 WHAT IS UNREACHABLE, AND ONE PIECE OF IT IS VET-CONFIRMED
> `ReadoutConfig` (FIX 1 informativeness gate, FIX 2 frequency-backbone correction, FIX 3 frozen
> anchor snapshot, and `graded_query`) is reachable ONLY through `canonicalize_fast`. **Zero calls
> means none of it runs.** From `exp_readout_fix_v1` (MIDDLE_BAND) and its landed-VET `8de3a9a20`:
> - **F3 -- CONFIRMED under 4 independent controls**, `F3_HELPS growing drop=0.060289`
> - F2 -- **load-bearing claim REFUTED** by the retention-matched arm the cell disclosed as not-run
> - F1 -- z-statistic under-credited
> **➡️ THE SUBSYSTEM IS BUILT AND NOT CONNECTED.** *Wire-don't-island in its purest form: built,
> measured, defaulted ON in the path that is never taken.*
>
> ## ⛔⛔ **TWO CORRECTIONS TO WHAT I WROTE ABOVE AN HOUR AGO. I OVERSTATED IT.**
> **1. "A VET-CONFIRMED IMPROVEMENT" OVERSTATES WHAT F3 IS CONFIRMED FOR.** `exp_readout_fix_v1`
> carries its own `scope` field and it is explicit:
> > *"READ-OUT STABILITY ONLY. Nothing here measures grounding QUALITY or whether any anchor means
> > anything; **a better read-out is not better meanings.** PBV was NOT re-run -- the confirm rate is
> > a PROJECTION of the Library.flag state machine over re-scored encounters."*
> **So F3 is confirmed for READ-OUT STABILITY, not for grounding quality**, and its `wire_status` is
> **`VET_PENDING`**, not wired-and-proven. *The cell disclaimed exactly the reading I gave it.*
>
> **2. THE `+0.0602` GRADED-QUERY FIGURE IS CITED BUT I HAVE NOT VERIFIED IT, AND I SHOULD NOT HAVE
> REPEATED IT.** The docstring credits it to prereg `d6c56353c`, n=4000. Checked:
> `exp_context_conditioned_near_neighbour_v1` (MIDDLE_BAND_FLOOR_HUGGING, n=4000) reports
> **A1=0.6395** with floors scrambled 0.4975 / frequency 0.4800 / chance 0.50 -- **and contains no
> 0.6997 and no graded arm at all.** ORGAN_MAP attributes `R_LIVE 0.6395, R_BASE 0.6997` to a
> DIFFERENT cell reproducing baselines. **So "graded query is worth +0.06" has no arm-level evidence
> I can point at, and the near-identity with F3's `0.060289` remains unexplained.**
> **✅ WHAT SURVIVES BOTH CORRECTIONS: 0 CALLS IS 0 CALLS.** The dead-code finding does not depend on
> what the improvement is worth -- only on the fact that nothing can reach it.
>
> ## 🔗 ONE INDEPENDENT CORROBORATION OF THE FREQUENCY STORY, FOUND IN PASSING
> `exp_readout_fix_v1`'s `fix2` field lists the **top hub anchors by background activation**:
> **`people, know, new, want, use, time, life, system, world, find`.** *Every one a high-frequency
> generic word. That is the frequency backbone, named by a cell from 12 August, agreeing with
> today's two-store frequency-bias measurement from a completely different direction.*
>
> ## 🧠 AND THE PINNED GEOMETRIC REASON THE SIGNED QUERY HURTS, FROM ORGAN_MAP
> > *"`cos(a1,a2)` is LOWER under sign than under the graded code at every distinctive:shared ratio
> > -- **sign() makes near-neighbours look MORE separated while making the separation MEAN LESS.**"*
> *That is precisely the failure mode for a mechanism whose whole job is picking the nearest
> neighbour.*
>
> ## ➡️ WHY THIS MATTERS MORE THAN ANY MECHANISM PROPOSED TODAY
> Thirteen interventions were tested and closed. **This is not a new mechanism -- it is measured,
> VET-confirmed work that is already built and simply not connected.** The two live call sites are
> `gate()` and `checkpoint()`: **the steps that decide what actually gets RECORDED as a grounded
> meaning.** *The cheap per-encounter scan was given the better read-out; the decisive recording
> step was not.*

> # 🎯 **ANCHOR SELECTION *IS* FREQUENCY-BIASED -- CONFIRMED ON TWO STORES. AND THE SCARIER**
> # **NUMBER NEXT TO IT IS WORTHLESS, WHICH A CONTROL CAUGHT BEFORE IT WAS REPORTED.**
> *No hand-scoring needed: "does selection prefer frequent words" is a question about the
> MECHANISM'S BEHAVIOUR, answerable against a random-draw-from-the-same-pool null on every fact in
> the store. This morning the same question read UNTESTABLE at n=22.*
>
> ## ✅ **A. THE FREQUENCY BIAS IS REAL AND REPRODUCES**
>
> | store | chosen anchor, mean log-freq | random draw from the SAME pool | |
> |---|---|---|---|
> | `reading_grounding_v1` (n=3,544) | **1.335** | 1.222, CI [1.173, 1.271] | ✅ separated |
> | `reading_grounding_v2_qualityfix` (n=634) | **2.641** | 2.240, CI [2.090, 2.392] | ✅ separated |
>
> **The null is the pool itself, so "frequent words get chosen because frequent words are what is
> available" is controlled for BY CONSTRUCTION.** *This converts the geometric finding -- the hub
> carries frequency at R^2 0.4819 against 0.01-0.05 for a sensorimotor dimension -- into a measured
> behaviour of the step that actually assigns meaning. It is the first time that gap has been shown
> to REACH anything.*
>
> ## ⛔ **B. WITHDRAWN BEFORE PUBLICATION: "WE NEVER PICK AN AVAILABLE CORRECT SYNONYM, 775 OF 775"**
> The run reported that where a true synonym WAS in the anchor pool we chose something else **732 of
> 732 times (v1) and 43 of 43 (v2)** -- 100.0%, on two independent stores. The examples read
> devastatingly: `artwork -> himself` with `art` available; `mice -> experiment` with `mouse`
> available; `often -> understand` with `frequently` available.
> **IT MEANS NOTHING, AND THE CONTROL SAYS SO:**
>
> | | expected hits if picking AT RANDOM | P(zero hits \| random) |
> |---|---|---|
> | v1 -- 732 opportunities, pool 2,744 | **0.44** | **0.642** |
> | v2 -- 43 opportunities, pool 334 | **0.16** | **0.848** |
>
> **A correct synonym is typically ONE word in a 334-2,744 word pool (median available: 1.0), so a
> random picker also scores zero most of the time. Observing 0 is UNSURPRISING.** *The measurement is
> UNDERPOWERED BY CONSTRUCTION -- with an expected hit count below 0.5 it can never distinguish good
> selection from random, no matter how many facts it runs on.*
> **🚨 I ALMOST REPORTED A 100.0% AS DAMNING. The tell was the same one that saved me twice already
> today: an exactly-100.0% figure is a reason to check, never a finding.** *And the pre-committed
> verdict logic held the line on its own -- it printed "the costly case is NOT established" because
> only 30-37% of misses were more frequent than the available correct answer.*
>
> ## ➡️ THE WELL-POWERED VERSION, AND IT IS THE NEXT RUN
> **Stop asking whether the correct synonym WON. Ask what RANK it got.** A binary hit/miss over a
> 1-in-2,744 event is unpowered; the RANK of the correct synonym among all anchors by cosine is
> continuous, uses every opportunity, and has an obvious null (uniform rank). **If selection carries
> real lexical meaning, correct synonyms should rank far above chance even when they lose. If they
> rank at chance, selection has no relationship to meaning at all -- and that would be the sharpest
> statement of the problem yet.** *Needs the substrate's own cosine scores rather than the stored
> facts, so it is a real run, not a re-slice.*

> # 🧠 **FIDELITY CHECK ON THE *ANSWER SHAPE* -- MY HYPOTHESIS REFUTED, AND THE REFUTATION IS**
> # **MORE USEFUL THAN THE HYPOTHESIS WOULD HAVE BEEN.**
> *Every fidelity pass so far audited a MECHANISM. Thirteen closed. Nobody had audited the SHAPE of
> the answer the mechanism is required to produce.*
>
> **THE FIDELITY OBSERVATION STANDS AND IS WORTH KEEPING:** `GROUNDED_MEANING(subject, obj)` is a
> POINTER FROM ONE LEXICAL ITEM TO ANOTHER -- `artery -> vessel`. Ask *which brain structure?* and
> there is **none**: conceptual semantics in the ATL hub is a DISTRIBUTED pattern over
> modality-specific features (ORGAN_MAP B4), and nothing in cortex stores *"the meaning of X is the
> word Y"*. **A lexical pointer is a DICTIONARY's format -- a convenient available structure.
> It is OUR-INVENTION-BEING-TESTED and it is labelled that way nowhere in the organ map or registry.**
>
> ## ❌ BUT THE MEASURABLE CONSEQUENCE I PREDICTED DOES **NOT** HOLD
> I predicted that if most words have no single other word meaning them, 78% noise would be the
> EXPECTED output of correct code. **Measured on 1,500 of the commonest content words we actually
> read, drawn independently of the hand-scored 100:**
>
> | | share | |
> |---|---|---|
> | **SYNONYM** -- a true one-word meaning EXISTS | **91.1%** | (93.4% of words WordNet knows) |
> | HYPERNYM only -- a broader word exists | 4.5% | |
> | NEITHER -- no one-word answer at all | 1.9% | |
> | no dictionary entry | 2.5% | |
>
> **➡️ THE ANSWER FORMAT IS NOT THE CEILING. The pre-committed negative branch fires: the answer
> shape is reachable for ~93% of what we read, so the noise is the MECHANISM's fault.**
>
> ## 🔑 **AND THE SHARPER FINDING IS INSIDE THE REFUTATION**
> On the blind-scored 100, split by whether a one-word answer was even available:
>
> | class | n | grounded meaningful-or-related |
> |---|---|---|
> | **SYNONYM (the answer EXISTS)** | 61 | **21%** |
> | HYPERNYM | 8 | 12% |
> | NEITHER | 7 | 71% *(n=7 -- ignore)* |
> | NO_ENTRY | 24 | 12% |
>
> **WORDS THAT DO HAVE A CORRECT ONE-WORD MEANING AVAILABLE ARE STILL GROUNDED CORRECTLY ONLY ~21%
> OF THE TIME. The answer is there and we do not find it.** *That is unambiguously a SELECTION
> failure, and it removes "the task is impossible" as an available excuse.*
> **🎯 SO BLAME RETURNS TO ANCHOR SELECTION -- and today's one surviving fidelity gap is exactly a
> selection story: the hub carries FREQUENCY at R^2 0.4819 against 0.01-0.05 for a sensorimotor
> dimension, so selecting the nearest anchor by cosine in that space should systematically return
> FREQUENT words.** That was UNTESTABLE at n=22 this morning. **It is now the leading candidate with
> a clean prediction, and what it needs is a stratified sample big enough to test it -- not another
> mechanism.**

> # 🔧 **A QUARTER OF THE GROUNDED FOUNDATION IS EITHER A DUPLICATE OR A CATEGORY ERROR, AND HALF**
> # **OF THAT IS A PLAIN BUG. MEASURED ON THE WHOLE STORE, NOT A SAMPLE.**
> *Followed up the flagged side-observation (24 of 100 hand-scored subjects had no dictionary entry).
> It reproduces at scale -- and the population is NOT what I assumed.*
>
> | store | n | no dictionary entry | **STEMMER ARTEFACTS** | likely NAMES/non-words |
> |---|---|---|---|---|
> | `reading_grounding_v1` | 3,544 | 919 (25.9%) | **442 (12.5%)** | 477 (13.5%) |
> | `reading_grounding_v2_qualityfix` | 634 | 153 (24.1%) | **87 (13.7%)** | 66 (10.4%) |
>
> **⛔ 107 CONFIRMED DOUBLE-COUNTS IN v1: the stem AND its full form are BOTH separate concepts in
> the same store** -- `billionair`/`billionaire`, `villag`/`village`, `cigarett`/`cigarette`,
> `centr`/`centre`, `statu`/`statue`. **This INDEPENDENTLY REPRODUCES a defect the charter already
> records** (*"121 stem/full-form pairs are counted as two concepts"*) by a different detection
> method -- which is why it counts as a positive control rather than a new claim.
> **➡️ MY PROPER-NOUN HYPOTHESIS WAS HALF RIGHT. Roughly half the no-entry population is names
> (`tesco`, `baumgartner`, `huffington`) -- the referent-vs-concept routing issue. THE OTHER HALF IS
> A STEMMING BUG, and it is data hygiene rather than a mechanism question.**
> **📉 AND THE QUALITY FIX DID NOT TOUCH IT: names fell 13.5% -> 10.4% between v1 and v2, while
> STEMS ROSE 12.5% -> 13.7%.**
> **⚖️ PRECISION ON "NAMES": the category is "no entry AND not a restorable stem", so it also holds
> contractions (`dont`), compounds (`midlife`, `crowdfund`) and neologisms (`facebook`). Calling all
> 13.5% proper nouns would be an over-read.**
>
> ## 🚨 AND A FAULT OF MINE INSIDE THIS RUN, RECORDED BECAUSE THE TELL IS REUSABLE
> The first version read `f.get("object")` where the schema field is **`obj`**. Every lookup returned
> `None`, and the script reported **"OBJECTS with no dictionary entry: 100.0%"** -- in all six stores.
> **AN EXACTLY-100.0% (OR EXACTLY-0.0%) RESULT IS A REACHABILITY FAILURE, NOT A FINDING** -- the same
> class as the exactly-zero-width CI already in CLAUDE.md. *I distrusted it on sight because it was
> too clean, checked the schema, and found the field name. The corrected figure is 5.7%-25.0%.*
> A populated-field assertion is now in the script.
>
> ## ➡️ WHY THIS MATTERS FOR DIRECTION
> The day's evidence says the lever is SUPPLY, and the unread hand-score says supply is 78% noise.
> **This names a concrete, non-speculative slice of that noise: ~25% of grounded concepts are
> duplicates or category errors, and the ~12-14% stemming half is fixable without touching any
> mechanism.** *It also further deflates the retired "3,544 grounded concepts" figure -- 107 of those
> were the same word twice.*

> # ❌ **POLYSEMY DOES NOT EXPLAIN THE BIOLOGY EFFECT. MY HYPOTHESIS, REFUTED BY ITS OWN**
> # **PRE-COMMITTED DECIDER. THE CONFOUND IS STILL OPEN.**
> *The hypothesis was mechanical, not vague: our grounding assigns ONE meaning per word, which CAN be
> right for a monosemous word and CANNOT be right for a polysemous one. Technical vocabulary is
> monosemous (`metaphase` 2 senses), general vocabulary is not (`head` 42). If that were the story,
> biology's advantage would not be about biology at all -- it would be about being handed words that
> HAVE one answer.* **Three measurements were specified in advance, with C as the decider.**
>
> | | result | |
> |---|---|---|
> | **A. bio subjects ARE more monosemous** | median **1.0** vs **4.0**; diff **-2.656**, CI [-4.073, -1.099] | ✅ **SEPARATED** |
> | **B. polysemy -> quality (pooled)** | +0.316, CI [-1.737, +2.632] | ❌ not separated |
> | **C. THE DECIDER -- same test, BIOLOGY REMOVED** | +1.756, CI [-0.923, +4.821] | ❌ **not separated** |
>
> **AND THE MOST CONVINCING PART IS THE DESCRIPTIVE ONE, BECAUSE IT NEEDS NO STATISTICS: the
> sense-count bands are FLAT.**
>
> | subject senses | n | grounded meaningful-or-related |
> |---|---|---|
> | **1 (monosemous)** | 22 | **27%** |
> | 2-4 | 28 | 25% |
> | 5-9 | 19 | 21% |
> | **10+** | 7 | **29%** |
>
> *If polysemy mattered there would be a gradient across a 1-to-10+ sense range. There is none.*
> **➡️ VERDICT (branch 3 of 4, written before the run): POLYSEMY MARKS THE SEGMENT WITHOUT EXPLAINING
> IT. The biology confound -- corpus vs domain vs definition density vs vocabulary -- REMAINS
> UNRESOLVED, and I am not claiming a mechanism.**
> *⚖️ WordNet was used strictly as a DIAGNOSTIC on the test items -- never in an arm, never as a
> grader. That is the charter-permitted use and a different thing from the circular-oracle failure
> MEMORY records, where WordNet was used to ANSWER the task.*
>
> ## 🔎 ONE SIDE-OBSERVATION, FLAGGED NOT CLAIMED
> **WordNet has NO ENTRY for 24 of the 100 subjects** (`baffin`, `tesco`, `abdullah` -- proper nouns).
> Those rows ground **12% good against 25% for known words** -- about half. *Not formally tested,
> n=24, and "no entry" was deliberately kept distinct from "one sense" so it could not manufacture
> the polysemy result. **A real candidate for a future test: we may be spending a quarter of our
> grounding effort on words that have no dictionary meaning to find.***
>
> ## ➡️ WHAT WOULD ACTUALLY RESOLVE THE CONFOUND, SINCE THIS SAMPLE CANNOT
> **The remaining candidate with a mechanism behind it is DEFINITION DENSITY**: the grounding organ
> IS a definitional extractor (`reading_grounding_loop_definitional_reading_pipeline`), and textbooks
> state definitions explicitly where news prose does not. **But measuring definition density per
> corpus would only reproduce measurement A -- a segment property, not a link to quality.**
> **THE HONEST STATEMENT: a 100-row sample scored once cannot separate four co-varying properties.
> Resolving it needs a purpose-built STRATIFIED sample -- technical-but-definition-poor text against
> general-but-definition-rich text -- so the properties come apart.** *That is a real experiment, not
> another slice of this one.*

> # 🎯 **WHY IS GROUNDING NOISE? THE SAMPLE CANNOT SAY -- BUT IT SAYS SOMETHING ELSE CLEANLY:**
> # **THE *KIND* OF TEXT IS THE LEVER, AND IT IS WORTH 3.4x.**
>
> ## ⚠️ FIRST, THE HONEST NEGATIVE: THE "WHY" QUESTION IS **UNTESTABLE AT THIS n**, NOT ANSWERED
> `scratch/diag_why_is_grounding_noise.py` tested the hypothesis today's fidelity pass predicts --
> *a frequency-dominated hub should hand out FREQUENT words as meanings, and those should be the
> NOISE ones* -- **and pre-registered the rival**, that the SUBJECTS differ (a population effect:
> we try to ground proper nouns and inflections that have no groundable meaning).
>
> | | NOISE | GOOD | diff | CI |
> |---|---|---|---|---|
> | log freq of assigned OBJECT | 2.303 | 2.197 | +0.105 | [-1.389, +0.938] |
> | log freq of SUBJECT | 0.693 | 1.242 | -0.549 | [-1.386, +0.405] |
> | SUBJECT unseen in corpus | 0.000 | 0.000 | +0.000 | [+0.000, +1.000] |
>
> **NOTHING SEPARATES. With 22 non-noise rows the CIs cannot exclude the effect sizes in play.**
> *The pre-committed third branch fired, and it was written before the run: **the hand-score answers
> WHETHER quality is poor and structurally cannot answer WHY.** Report as UNTESTABLE, never as
> evidence of no effect.* **So the frequency-hub-causes-bad-grounding story remains a HYPOTHESIS --
> it was not confirmed here and must not be quoted as if it were.**
>
> ## ✅ **WHAT THE SAMPLE *CAN* ANSWER, AND IT IS WELL-POWERED**
>
> | segment | n | meaningful-or-related | rate |
> |---|---|---|---|
> | **`bio_new`** (dense technical) | 17 | **9** | **52.9%** |
> | `ele_cont` | 18 | 4 | 22% |
> | `adv_new` | 42 | 6 | 14% |
> | `int_cont` | 21 | 3 | 14% |
>
> **`bio_new` vs ALL OTHERS: 9/17 vs 13/83, difference +0.373, 95% CI [+0.124, +0.620], SEPARATED.
> Fisher exact two-sided p = 0.00204.** *This is the charter's own prediction reproducing, which is
> what makes it a positive control rather than a fishing expedition.*
> **🔗 AND IT CONVERGES WITH AN INDEPENDENT MEASUREMENT ON A DIFFERENT INSTRUMENT AND SAMPLE:**
> grounding RATE at 8,000 sentences was textbook **12.6%** / simplewiki 3.6% / Little Women 0.8% /
> Sherlock **0.7%**. **Two different measurements, same direction: dense expository text grounds
> several times better than general prose.**
>
> ## 🚨 **THE QUALIFICATION THAT CHANGES HOW TO READ IT -- DO NOT SKIP THIS**
> **The 52.9% is "MEANINGFUL *or* RELATED". Biology's breakdown is 1 MEANINGFUL / 8 RELATED / 8
> NOISE.** So **even in the best segment, genuinely meaningful grounding is 1 of 17 (~6%)**, and the
> effect is mostly biology producing NEAR-MISSES rather than hits. *"Biology works" would be a
> serious over-read; "biology gets closer and still rarely lands" is what the data supports.*
> **⚠️ AND IT IS CONFOUNDED: `bio_new` differs from the others in corpus, domain, vocabulary AND
> definition density all at once. This sample cannot say WHICH of those is doing the work.**
>
> ## ➡️ WHERE THAT LEAVES THE SUPPLY DIRECTION -- REFINED TWICE IN ONE DAY, AND BOTH TIMES BY DATA
> 1. Fidelity synthesis said **the lever is SUPPLY** (13 interventions at 5 positions all closed).
> 2. The unread hand-score said **not more text -- 78% of what we ground is noise**, so growth would
>    multiply noise. *That reversed (1).*
> 3. This says **not quantity but KIND: dense expository text with explicit definitions, worth 3.4x**
>    -- *and even there the hit rate is ~6%, so it is a better starting point, not a solution.*

> # 🔴 **A COMPLETED HAND-SCORE HAS BEEN SITTING UNREAD ON DISK SINCE 2026-08-12, AND IT IS THE**
> # **GATE ON THE ENTIRE SUPPLY DIRECTION. IT DOES NOT SAY WHAT I HOPED.**
>
> ## HOW IT WAS FOUND. The charter's standing rule is **GROWTH STAYS PAUSED** pending three things.
> Checked all three rather than assuming, because every route today points at SUPPLY:
> 1. **grounding-quality fix lands** -- ✅ **MET.** Tautology gate + closed-class refusal are in
>    `reading_grounding_loop.py` with a self-test (`_selftest_tautology_is_refused_not_recorded`).
> 2. **read-out fix lands** -- ⚠️ **PARTIAL.** `9979af09e` IS an ancestor of HEAD, but its landed-VET
>    (`8de3a9a20`) reads **OVERSTATED**: F3 confirmed under 4 controls, **F2's load-bearing claim
>    REFUTED** by a retention-matched arm the cell had disclosed as not-run, F1 under-credited.
> 3. **re-measurement of quality with controls that can fail** -- **the cell exists and says
>    `STRUCTURAL_PASS_PENDING_B3`, and its own message reads: *"THIS CELL MAKES NO QUALITY CLAIM.
>    100 blind rows written for the director's hand-score."*** MEMORY agrees: *"the surviving number
>    is 634, and it has not been re-vetted."*
>
> ## 🚨 **BUT THE HAND-SCORE WAS ACTUALLY DONE.** `_joined_verdicts.json` (written 10 minutes AFTER
> the blind sample) holds **all 100 rows scored and already joined to their arms.** The verdict field
> was never updated and **nobody ever read the result.** Computed now:
>
> | arm | n | MEANINGFUL | RELATED | NOISE | MEANINGFUL rate [95% CI] |
> |---|---|---|---|---|---|
> | PBV_BASE | 50 | **1** | 12 | 37 | 0.020 [0.000, 0.060] |
> | PBV_F1F3 (the read-out fix) | 50 | **2** | 7 | 41 | 0.040 [0.000, 0.100] |
>
> **`BASE - F1F3` = -0.020, 95% CI [-0.080, +0.040] -- NOT separated. The read-out fix did not move
> grounding quality.** Overall: **3 MEANINGFUL / 19 RELATED / 78 NOISE out of 100.**
>
> ## ⚠️ THE SCOPE, STATED BEFORE ANYONE QUOTES THE NUMBER -- AND ONE COMPARISON IS BARRED
> - **POPULATION IS COMPARABLE on the one axis that matters: 0 of 100 rows are self-tautologies**, so
>   the gate worked and this is the cross-grounded population, not the tautology-inflated one.
> - **⛔ I AM NOT PLACING THIS BESIDE THE HISTORICAL 35% / 64% / 94% FIGURES.** MEMORY carries an
>   explicit standing prohibition on exactly that juxtaposition, and the corpora differ (this sample
>   is onestop reading-levels + biology). *The rate is reported for THIS sample only.*
> - **n IS TINY WHERE IT COUNTS: MEANINGFUL counts are 1 and 2.** Both CIs touch zero. This
>   distinguishes "poor" from "excellent"; it does NOT resolve 2% vs 5%.
> - **SINGLE SCORER, no second witness, and the scorer was a prior session's director.**
> - **DIFFERENT OBJECT FROM THE RECALL TASK.** This scores the GROUNDED_MEANING fact store, not the
>   word profiles the rank metric scores. Do not transfer the number between them.
> - ✅ **THE CHARTER'S OWN PREDICTION REPRODUCES**, which is the closest thing here to a positive
>   control: *"meaningful groundings concentrate in the dense technical (biology) segment"* --
>   `bio_new` is 9 of 17 meaningful-or-related (53%) against `adv_new`'s 6 of 42 (14%).
>
> ## ➡️ **CONSEQUENCE, AND IT REVERSES WHAT I WAS ABOUT TO RECOMMEND**
> **Condition 3 is now MET -- and it does NOT confirm quality.** So **GROWTH STAYS PAUSED, now on
> EVIDENCE rather than on a pending item**, and the charter line can finally be resolved either way
> instead of hanging.
> **🚨 AND IT CUTS AGAINST THE SUPPLY RECOMMENDATION I REACHED THREE BLOCKS ABOVE.** I was about to
> propose re-running gap-targeted growth. **You cannot fix a grounding process that is mostly noise
> by feeding it more text -- growing on a noisy foundation multiplies the noise.** *The fidelity
> synthesis said "the lever is supply". This says "not until the thing being supplied is worth
> keeping". Both are mine, from the same day, and the second one wins because it is measured.*
> **THE REAL NEXT QUESTION IS THEREFORE NARROWER AND BETTER: why is 78% of grounding NOISE, and does
> the biology-segment concentration (53% vs 14%) point at the fix?**

> # ✅ **CONFIRMED ON REAL DATA: THE DG WIN WAS 100% TIE-BREAKING. AND A PRIOR-WORK TOOL WAS**
> # **RETURNING SILENT ZEROS -- THE ARCHIVE HAD ALREADY ANSWERED THIS A MONTH AGO.**
>
> ## 1. THE TIE-CONVENTION TABLE (seed 7, real profiles -- not a simulation)
>
> | arm | OPTIMISTIC | MIDPOINT | PESSIMISTIC | median ties | % probes tied | % sims exactly 0 |
> |---|---|---|---|---|---|---|
> | **RAW** | 52.5 | 52.5 | 52.5 | **0.0** | **0.0%** | **0.0%** |
> | **DG@0.01** | **18.0** | 146.5 | **275.0** | **254.0** | **85.7%** | **89.4%** |
> | DG@0.02 | 56.0 | 148.2 | 239.5 | 173.5 | 65.3% | 64.5% |
> | DG@0.05 | 95.0 | 95.0 | 95.0 | 0.0 | 4.0% | 5.9% |
> | DG@0.25 | 63.0 | 63.0 | 63.0 | 0.0 | 0.0% | 0.0% |
>
> **`DG@0.01 - RAW` goes from `-29.0` [CI -36.0,-17.5] OPTIMISTIC to `+199.0` [CI +176.5,+216.5]
> PESSIMISTIC. The sign REVERSES.** RAW has **zero** ties, so the artifact is entirely a property of
> the sparse arms. **At the two sparsities with NO ties (0.05, 0.25) DG is unambiguously WORSE
> (+22.5 and +2.0).** *The post-hoc-transform family closes with the eleven write-side routes.*
>
> ## 2. ⛔ **`experiment_index.py` -- THE DESIGNATED PRIOR-WORK TOOL -- WAS RETURNING SILENT ZEROS**
> Matching was literal substring, so **a query with a SPACE could never match a cell name with an
> UNDERSCORE.** `query "active growth"` returned **0** against a LANDED HARD_PASS named
> `exp_breadth_foundation_active_growth_loop_ud_ewt_v1`. **5 false negatives in 12 of the day's
> checks** -- and the expensive one is `"pattern separation"`: **1 literal vs 12 normalised.**
> **🚨 I DESIGNED AND RAN THE DG DIAGNOSTIC PARTLY ON THE STRENGTH OF "1 cell, 0 landed". THE TRUTH
> WAS 12 CELLS, 9 LANDED, AND TWO WERE HARD_FAILS ON THE SAME ORGAN:**
> - `exp_dg_pattern_separation_mcscript_purity_v1` **HARD_FAIL** -- DG at sparsity 0.05, purity
>   **0.1013 against a 0.1999 baseline**. *"the substrate cannot discriminate 195-way online with
>   this keying signal even with DG-style separation."*
> - `exp_selfplay_dg_pattern_separation_xfit_v1`
>   **HARD_FAIL_REPRESENTATION_INSUFFICIENT_REDIRECT_EXOGENOUS** -- DG improved the metric by
>   **0.015**. **THAT VERDICT NAME IS THE SAME CONCLUSION TODAY'S FIDELITY SYNTHESIS REACHED
>   INDEPENDENTLY: GO GET EXOGENOUS INFORMATION.** It was on disk a month early.
> - `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` **HARD_PASS** -- but **PRE-WRITE**,
>   and on borrowed Pythia keys, not our accumulated profiles. *A POSITION difference worth noting,
>   not a licence to re-propose.*
> **✅ FIXED + SELF-TESTED (`--self-test`): folds `_` and `-` to spaces on both sides; asserts the
> three spellings return EQUAL counts, plus known-present and known-absent controls.**
> **⚠️ SINGLE-WORD queries were never affected -- `"moral"` and `"fable"` really are 0, so the
> thrust-2 conclusion stands. Every MULTI-WORD conclusion drawn before this fix is void.**
> *CLAUDE.md already documented this exact failure for `director_kb_query.py`. The replacement
> shipped with its own version of it.*
>
> ## 3. ✅ THE STRUCTURE-VS-BAG CONFOUND I FLAGGED THIS MORNING IS **NOT** REAL
> Coverage-matched re-run, restricting BAG to exactly the sentences STRUCT could parse (the
> restriction dropped 4.4% of pairs, positive-control asserted non-empty):
>
> | seed | COOC | BAG_ALL | BAG_MATCHED | STRUCT |
> |---|---|---|---|---|
> | 7 | 10.0 | 36.5 | **37.0** | 49.0 |
> | 101 | 6.0 | 36.0 | **35.5** | 50.0 |
>
> **BAG_MATCHED ~= BAG_ALL, so the coverage penalty is ~ZERO and my confound worry was unfounded.
> STRUCT still loses at equal coverage.** *I flagged it honestly and it cost one cheap run to close;
> the morning's reported tie was, if anything, generous to STRUCT.*

> # 🚨 **THE SWEEP FINISHED AND PRINTED A CONFIDENT FALSE POSITIVE. READ THIS BEFORE TRUSTING ANY**
> # **PRE-COMMITTED VERDICT IN THIS REPO.**
> The DG sweep completed all 3 seeds and printed, in its own words:
> *"VERDICT: **A POST-HOC NON-LINEAR TRANSFORM MOVES THE TASK** -- DG@0.01 beats RAW by -16.5,
> CI-separated. That is the FIRST mechanism family in eleven attempts to move this."*
> **THAT VERDICT IS FALSE, AND IT WAS ALREADY WITHDRAWN BEFORE THE SCRIPT PRINTED IT** (noise at the
> same sparsity scores 14.0 against the real arm's 18.0/15.0; an all-identical arm scores 1.0).
>
> | arm | pooled paired vs RAW | reading |
> |---|---|---|
> | **DG@0.01** | **-16.5, CI [-22.0, -10.0] SEPARATED** | ⛔ **THE ARTIFACT. Noise beats it.** |
> | DG@0.02 | +6.0, CI [+1.0, +11.0] SEPARATED | worse than RAW |
> | DG@0.05 | +19.0, CI [+15.0, +22.0] SEPARATED | much worse |
> | DG@0.10 | +6.0, CI [+4.0, +8.0] SEPARATED | worse |
> | DG@0.25 | +1.0, CI [+0.0, +2.0] not separated | ties RAW |
>
> **➡️ SO THE CLEAN READING IS: AT EVERY NON-ARTIFACT SPARSITY, DG IS WORSE THAN OR EQUAL TO RAW.
> The post-hoc-transform family CLOSES.**
> **🔑 THE TOOLING LESSON, AND IT IS THE ONE WORTH KEEPING: A PRE-COMMITTED READING IS ONLY AS GOOD
> AS THE GUARDS BEHIND IT.** The script's branch logic was sound, its floors were real, its CIs were
> bootstrapped, its held-out leak was 0, and its arms were asserted non-empty -- **and it still
> declared a breakthrough that random noise reproduces.** Pre-registration protects against moving the
> goalposts after the fact. **It does not protect against a metric that cannot fail safely in the
> regime being swept.** *Those are different failures and only one of them was defended against.*
>
> ## 🔧 AND A SECOND, CHEAPER TOOLING FAULT FROM THE SAME HOUR
> The refutation script itself **died after its full multi-minute corpus read** on
> `ValueError: unsupported format character '>'` -- a line left behind by a `sed` substitution that
> silently failed to match. **`py_compile` reported success**, because an invalid conversion character
> is a RUNTIME error, not a syntax error. **"COMPILES OK" was structurally incapable of catching it,
> and I treated it as verification.**
> **➡️ FIXED: `tools/check_format_strings.py`** walks the AST and renders every `%`-literal against
> dummy args. Self-tested with a positive control -- it fires on the exact literal that broke the run
> and stays silent on a valid one. *Two rules: a `sed` that does not match fails SILENTLY, so verify
> the edit took; and **COMPILING IS NOT EXERCISING** -- before an expensive run, exercise the cheap
> surfaces.*

> # 🧭 **WHERE THE FIDELITY PASS ACTUALLY LEAVES US -- THE SYNTHESIS, 2026-08-20.**
> *Marked as a SYNTHESIS, not a result: the DG sweep's third seed and the real-data tie-convention
> numbers had not landed when this was written. The analytic refutation is decisive for the sparse
> points regardless -- noise beats them -- but treat the "post-hoc family closes" line as
> pending-confirmation rather than banked.*
>
> ## THE SHAPE OF EVERYTHING WE HAVE TRIED, IN ONE TABLE
>
> | where we intervened | how many routes | outcome |
> |---|---|---|
> | **WHICH traces get written** | 8 | all closed |
> | **WHEN they get written** (the write moment) | 1 | closed |
> | **HOW they are written** (delta-rule family, incl. a nested positive control) | 1 | closed -- the sum is the family's optimum |
> | **WHAT a trace IS** (structure vs bag) | 1 | TIE -- and coverage-confounded, re-run written |
> | **HOW they are transformed AFTERWARDS** (DG pattern separation) | 1 | sparse points = artifact; dense points lose to RAW |
> | **HOW MANY traces exist** (coverage) | 1 | ✅ **the only thing that has ever worked** |
>
> ## 🔑 **THE ONE FIDELITY GAP THAT SURVIVED THE WHOLE PASS, IN ORGAN_MAP'S OWN NUMBERS**
> **Our hub carries FREQUENCY at R^2 0.4819 and a typical sensorimotor dimension at 0.01-0.05 --
> roughly TWENTY TIMES more strongly.** That was measured weeks ago as a by-product of the spoke
> audit and reported as "not blind, but overwhelmingly a frequency code". **Nobody connected it to
> the write rule.**
> **➡️ AND IT EXPLAINS THE TABLE ABOVE MECHANICALLY RATHER THAN BY ANALOGY: every transformation of
> a bag of word-forms is still a function of word-form statistics, and the dominant word-form
> statistic is frequency.** Selecting which bags, weighting them, changing the update rule, and
> re-projecting the result afterwards **cannot** change what the input is made of. *That is why
> thirteen interventions at five different positions all returned the same answer.*
> **⚠️ WHAT THIS IS NOT: it is not a proof, and "our code is a frequency detector" must not harden
> into an unscoped claim.** It is one R^2 on one profile set. **The honest status is: the strongest
> surviving HYPOTHESIS, consistent with every negative and contradicted by none of them.**
>
> ## ➡️ WHAT THAT MAKES THE NEXT REAL QUESTION -- AND IT IS THE OWNER'S OWN
> If the limit is what a trace is MADE OF, then the lever is SUPPLY, not mechanism -- which is
> exactly Q72: *"you need more textbooks / information"*, and the load-bearing word there was
> **PATCHY**, not "another textbook". Two concrete things already point the same way and neither is a
> new build:
> - `exp_breadth_foundation_active_growth_loop_ud_ewt_v1` -- **HARD_PASS**, gap-targeted active
>   growth moved coverage **0.50 -> 0.79**, real-vs-shuffle AUC **0.8924 vs 0.5122**. It is the
>   owner's own idea and it is the only landed win in this area.
> - **coverage is the only intervention that has ever moved the representation**, twice now
>   (`keep_noting_grounded`, and the 17 -> 46 trace-coverage measurement).
> *Both say the same thing: give it more and better-targeted evidence rather than a cleverer rule.*

> # ⛔🔴 **WITHDRAWN WITHIN THE HOUR: THE DG@0.01 "WIN" IS A TIE-BREAKING ARTIFACT. PURE NOISE**
> # **SCORES BETTER THAN IT DID. DO NOT QUOTE ANY NUMBER FROM THE BLOCK BELOW.**
> *`scratch/diag_what_would_a_meaningless_sparse_arm_score.py` -- no corpus, no substrate, seconds.*
> **THE REFUTATION IS THE PROJECT'S OWN RULE WITH THE SIGN FLIPPED.** CLAUDE.md says *"construct the
> EMPTY version of a winning arm and check that it LOSES."* The suspect arm was not empty but SPARSE,
> so: **construct the MEANINGLESS version and check whether it WINS.** It does.
>
> | k (non-zero of 1024) | RANDOM NOISE, optimistic | RANDOM NOISE, pessimistic | observed DG |
> |---|---|---|---|
> | **10 (sparsity 0.01)** | **14.0** | **272.0** | **18.0 / 15.0** |
> | 20 (0.02) | 49.0 | 239.0 | 56.0 / 46.0 |
> | 51 (0.05) | 142.0 | 156.0 | 95.0 / 78.5 |
> | 1024 (dense noise, control) | 143.0 | 143.0 | -- |
> | CONSTANT (degenerate extreme) | **1.0** | 286.0 | -- |
>
> **➡️ A CODE CONTAINING NO INFORMATION WHATSOEVER SCORES 14.0 -- BETTER THAN OUR 18.0 AND 15.0 --
> AND NOISE REPRODUCES THE WHOLE SWEEP SHAPE.** The arithmetic was predictable in advance and is
> stated in the script: `k=10` over 1024 slots makes **~91% of candidate/query pairs share no support
> at all**, so their dot product is EXACTLY 0.0; the rank statistic `1 + #{sims > sims[target]}` uses
> a STRICT inequality, so every one of those ties counts as BEATEN. **The emptier the code, the
> better the score.** The `CONSTANT` row is the proof in its purest form: identical profiles carrying
> zero information score a PERFECT 1.0.
> **✅ THE HARNESS ITSELF IS FINE -- positive control passed: query == profile scores rank 1.0 under
> both conventions.** The defect is the SPARSITY, not the scorer.
> **🚨 MY OWN GUARD PASSED THIS (`alive = 286 of 286`). NON-ZERO IS NOT NON-DEGENERATE, AND I WROTE
> THAT GUARD FOR THE EMPTY CASE WHILE BUILDING THE ARM MOST EXPOSED TO THE SPARSE CASE.** New rule
> added to CLAUDE.md.
> **📉 AND THE REAL READING OF THE SWEEP, ONCE THE ARTIFACT IS REMOVED: NO SPARSITY BEATS RAW.** At
> k=256 the real arm (63.0 / 41.5) does beat noise (152.0), so there IS genuine signal at dense
> settings -- **but it still loses to RAW (52.5 / 35.5).** *So the pre-committed "DG ties or loses"
> branch fires, and the post-hoc-transform family closes with the eleven write-side routes.*
>
> # [THE WITHDRAWN BLOCK, KEPT SO THE ERROR IS VISIBLE RATHER THAN EDITED AWAY]
> # ⚠️🔬 **DG PATTERN SEPARATION -- SEED 7 LOOKS LIKE THE BIGGEST WIN OF THE EFFORT, AND I DO NOT**
> # **BELIEVE IT. A REFUTATION IS RUNNING. NOBODY QUOTE THIS UNTIL IT LANDS.**
> *`scratch/diag_dg_pattern_separation_on_profiles.py`, seed 7 of 3, `simplewiki`, leak 0.*
>
> | arm | median rank | vs COOC floor 17.0 | mean-pair-cos | ranks changed vs RAW |
> |---|---|---|---|---|
> | RAW (what ships) | 52.5 | 3.09x | +0.0815 | -- |
> | **DG@0.01** | **18.0** | **1.06x** | **+0.0096** | 295 |
> | DG@0.02 | 56.0 | 3.29x | +0.0155 | 296 |
> | DG@0.05 | 95.0 | 5.59x | +0.0264 | 294 |
> | DG@0.10 | 79.0 | 4.65x | +0.0398 | 290 |
> | DG@0.25 | 63.0 | 3.71x | +0.0629 | 281 |
>
> **⛔ THREE TELLS SAY TIE-BREAKING ARTIFACT, NOT PATTERN SEPARATION, AND THEY WERE VISIBLE BEFORE
> ANY REFUTATION RAN:**
> 1. **The winning point is the SPARSEST point.** `sparsity=0.01` over `expand_dim=1024` keeps **10
>    non-zero components**. Two 10-sparse vectors over 1024 slots usually share NO support, so their
>    dot product is **exactly 0.0** -- and the rank statistic is `1 + #{sims > sims[target]}`, a
>    STRICT inequality, so **every candidate tied at 0.0 counts as BEATEN.**
> 2. **The sweep is NON-MONOTONE** (18.0 / 56.0 / 95.0 / 79.0 / 63.0). A real encoding improvement
>    does not change sign twice.
> 3. **DG@0.01 has the LOWEST mean pairwise cosine (+0.0096)** -- the most nearly-orthogonal arm,
>    which is exactly the condition that manufactures ties.
>
> **🚨 AND MY OWN GUARD PASSED IT: `alive = 286 of 286`. NON-ZERO IS NOT NON-DEGENERATE.** CLAUDE.md
> already carries this fault -- *"an arm whose accumulator was never written reported median rank 1.0,
> a 20x win, because tied similarities never sort above the target"* -- and I wrote the guard for the
> EMPTY case while building the arm most exposed to the SPARSE case. **The rule that would have caught
> it is the one already written down: ASK WHAT SCORE A BROKEN ARM WOULD GET.**
> **➡️ RUNNING: `scratch/diag_dg_is_the_win_a_tie_artifact.py` -- scores every arm under BOTH tie
> conventions (optimistic / midpoint / pessimistic) plus tie-density per probe.** Pre-committed:
> *survives pessimistic* -> real, and the most important result of the effort; *collapses* ->
> **withdraw it**, and record that the non-emptiness guard needs a tie-density check for sparse arms.

> # 🔄 THRUST 2 CORRECTED -- **Q77 SELF-RESOLVED AND MY OWN PREMISE WAS THE THING THAT WAS WRONG.**
> *I filed Q77 arguing that `social_iqa` might be unable to show a difference, because "when the
> clever method AND the crude word-counting floor both sit at chance, the likeliest reading is the
> test is not reaching either of them". **That reasoning is backwards for this dataset**, and
> settling it cost one script and no owner input.*
>
> **WHAT A METHOD WITH A REAL BUT SHALLOW ADVANTAGE SCORES** (all 1,954 validation items,
> `tools/diag_is_the_story_test_answerable.py`):
>
> | method | score |
> |---|---|
> | majority-class floor | 0.3362 |
> | **BAR** (floor + 3sd at n=1954) | **0.3682** |
> | LONGEST answer (the classic multiple-choice annotation artifact) | 0.3557 |
> | OVERLAP with context+question | 0.3449 |
> | RAREST word | 0.3234 |
>
> **NOT ONE SURFACE OR ARTIFACT METHOD CLEARS THE BAR.** The set was built so shallow tricks cannot
> work, **so a crude method scoring at chance is the instrument WORKING, not failing.**
> **➡️ THEREFORE OUR 2026-08-11 ARMS AT 0.3501-0.3975 ARE A GENUINE NEGATIVE, NOT AN UNTESTABLE
> MEASUREMENT.** And the one score that looked like it might clear a bar does not survive either:
> **0.3975 was on `n_dev = 400`, not 1,954** -- where the 3sd bar rises to **0.4069** -- and that same
> run recorded **28 of 100 sampled items LEAKING** from its training set.
> **🎯 THE CONSEQUENCE FOR THE PLAN, AND IT IS THE USEFUL PART: BUILDING A NEW STORY TEST WOULD NOT
> HAVE FIXED ANYTHING -- WE WOULD OWN TWO STORY TESTS WE FAIL.** The owner's moral/transfer test is
> still worth building, but as a way to understand HOW we fail, **not as a replacement instrument.**
> *"Ask whether the experiment could have succeeded before asking why it did not" -- applied to an
> INSTRUMENT, and this time it defended the instrument rather than condemning it.*

> # 🧠 DEEP BRAIN-FIDELITY PASS -- 2026-08-20, OWNER-DIRECTED. **THREE ROUTES CLOSED FOR FREE,**
> # **AND THE ELEVEN NEGATIVES RESOLVE INTO ONE POSITION ERROR.**
> *Owner: "begin with a deep brain fidelity check." Done by READING, before spending any compute --
> three standing leads died to the three-read check and one runtime probe, at a cost of minutes.*
>
> ## ⛔ CLOSED 1 -- **THE SIGN HYPOTHESIS IS REFUTED BY CONSTRUCTION. IT WAS ALREADY THE SHIPPED**
> ## **STATE.** STATUS carried *"a sign-quantised accumulation would lose exactly what a linear
> random projection keeps -- that is now the LEADING HYPOTHESIS for the 2x, and it is directly
> testable"* as an open lead. **`GRADED_COMPARATOR` has been `True` since 2026-08-14.** Verified at
> RUNTIME, not by reading: `bundle()` returns the raw `2*v`, `anchor_matrix()` rows are raw, `_sums`
> is raw. **The profile path has no sign step, and the 2x gap is measured on the profile path.**
> *The leading hypothesis for our largest gap could not have been true for six days.*
>
> ## ⛔ CLOSED 2 -- **DECORRELATION IS SHUT AT BOTH ENDS, AND ORGAN_MAP SAYS SO IN WRITING.**
> The drill's *"whitening is per-dimension gain but IN THE RIGHT BASIS -- our four failures were
> wrong-basis, NOT evidence the mechanism fails"* reads like a live lead. It is not:
> - **rank-1 / common-mode removal: `exp_rank1_common_mode_removal_v1` = HARD_FAIL_NO_EFFECT.**
>   `d_P1 = +0.0005, CI [-0.0043, +0.0053]` -- includes zero. Mean-removal arm `P5 = 0.6767` is
>   WORSE than baseline `P0 = 0.6980`. Random-direction control clean.
> - **full-covariance whitening: PARKED-BY-SAMPLE-SIZE**, `O(d^2)` samples required, with the
>   verbatim instruction **"do not queue full whitening"**.
> *This is the divisive-normalisation lesson repeating exactly. The third read paid for itself again.*
>
> ## ⛔ CLOSED 3 -- **A DEPRESSION / FORGETTING TERM IS NOT THE ANSWER EITHER, AND THE CONTROL THAT**
> ## **PROVES IT IS UNUSUALLY GOOD.** ORGAN_MAP G3 calls our rule *"reward-gated pure-Hebbian, no
> error term, no normalisation, no LTD"* and **"WRONG-OP relative to any named cortical plasticity
> rule"** -- which points straight at *add an LTD term*. **Already tested.** The delta-rule sweep
> `p <- p + eta*(trace - p)` has both a residual and a step size, and **`eta = 1/n` IS the running
> mean and reproduced SUM's ranking EXACTLY (delta +0.00 at all five reads)** -- so the sum is not a
> rival arm, it is a POINT INSIDE the family. **Every fixed learning rate is worse, and worse faster**
> (slopes +1.798 / +2.354 / +2.879 vs SUM's +1.035). **The family's optimum sits at the
> no-forgetting end.**
>
> ## 🟡 AND THE ONE ISLANDED HARD_PASS IS NOT OUR PROBLEM -- SAYING SO RATHER THAN SEIZING ON IT
> ORGAN_MAP flags `exp_excitability_gated_substrate_cpu_v1` (**HARD_PASS, +0.500, ZERO CONSUMERS**)
> as *"the largest fidelity gap in the §10 batch"*. Read it: it protects high-priority items **above
> the superposition capacity cliff, K=1200**. **We score 150-450 candidates. We are nowhere near that
> cliff.** Correctly `SHELVE`d with a capacity-framed revival criterion. **Wiring it would be exactly
> the "don't wire an organ because you think it could help" the owner barred on 2026-08-20.**
>
> ## 🔑 **THE SYNTHESIS, AND IT IS A *POSITION* ERROR IN THE SHAPE/POSITION/METRIC FRAME**
> **ELEVEN write-side interventions have now closed** -- residual gate, novelty, precision, k-WTA,
> divisive normalisation, incremental decorrelation, retrieval practice, best-single-trace, the write
> MOMENT, the whole delta-rule family, and today's structure-vs-bag.
> **The representation is insensitive to WHICH traces go in AND to HOW they are written.**
> **➡️ THE ONLY TWO THINGS THAT HAVE EVER MOVED IT ARE COVERAGE (how many traces exist) AND A
> POST-HOC CENTRING TRANSFORM. NEITHER IS A RULE ABOUT WRITING.**
> **That is the fidelity statement: we have been intervening at the WRITE for eleven attempts, and
> both things that worked act somewhere else.** *In CLS the transformation from experience into a
> semantic code is not at the write either -- the write is fast, additive and pattern-separated, and
> the REORGANISATION happens offline.*
> **⚠️ BUT DO NOT READ THAT AS "GO BUILD REPLAY". `experiment_index.py` returns `replay` 211 cells /
> 176 landed and `consolidation` 114 / 100.** This is the most-explored ground in the project, and
> the CLS replay cell that exists is MIDDLE_BAND (closed-loop 0.576 vs uniform 0.521, below its
> >=0.08 bar). **An "unexplored gap" claim over 176 landed cells needs an ENUMERATION, not a hunch.**
>
> ## ✅ **THE ENUMERATION IS DONE, AND THE GAP SURVIVES 266 LANDED CELLS.**
> `scratch/enumerate_consolidation_cells.py`. **311 replay/consolidation cells, 266 LANDED.**
> Classified by whether the stored code stays a (re)WEIGHTED SUM of traces or leaves that family --
> *selection, gating, prioritised replay and scalar normalisation all only change the WEIGHTS, and a
> weight of zero is still a weight.*
>
> | | count |
> |---|---|
> | **NON-LINEAR candidates** (sparsify / quantise / prototype / bind / truncate / learned / attractor) | **30** |
> | linear-only (weights) | 45 |
> | **matched NOTHING -- the filter says nothing about these** | **191** |
>
> **POSITIVE CONTROL PASSED, and the run was built to REFUSE without it: the same filter finds 1,356
> of 8,836 cells archive-wide, spread across all seven operations** (bind 501, prototype 431,
> attractor 326, sparsify 91, quantise 78, truncate 74, learned 24). *A filter that could not find
> k-WTA or binding in 8,836 cells could not be trusted to report their absence in a subset.*
>
> ## 🔑 **AND THE DECISIVE CUT: 29 OF THE 30 NEVER TOUCHED THE WORD-MEANING TASK.**
> Every one is a **STORE-level** result -- cortex/hippocampus handoff at M=2048/8192, Hopfield
> consolidation, codebook consolidation, compressed sequence replay, SVD atom merge, capacity. The
> single cell matching reading/vocabulary wording at all is `exp_ner_frame_semantic_cpu_v1`, a
> HARD_FAIL NER frame cell -- not a consolidation transform over word profiles.
> **➡️ SO THE CLAIM IS NOT "NOBODY TRIED IT". IT IS THE MUCH STRONGER "IT WAS TRIED 30 TIMES, ALWAYS
> ON A DIFFERENT OBJECT."** *That is what an enumeration buys over a search.*
> **⚠️ HONEST LIMIT, STATED BECAUSE 191 IS MOST OF THE POPULATION: the filter matched nothing on 191
> landed cells, so this is evidence about the 75 it classified, not about all 266.**
>
> ## 🎯 **THE ONE CANDIDATE IT SURFACED -- AND WHY THE ANSWER IS *MEASURE*, NOT *WIRE*.**
> `exp_cls_ca3complete_consolidation_v1` = **HARD_PASS** (Buzsaki two-stage CLS): consolidation keeps
> OLD **0.933** where naive forgets it at **0.020**, while still acquiring NEW 0.893.
> `hdlab/ca3_completer.py` is registered **`WIRE_BEHIND_FLAG` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`**,
> and `substrate.py:184` carries it as **slot D2 "complete a pattern from a partial cue",
> NEEDS_ADAPTER.** *It is a POST-HOC NON-LINEAR TRANSFORM -- exactly the family the evidence points
> at -- and it is not reachable from the reading path.*
> **⛔ BUT WIRING IT NOW WOULD REPEAT THE EXACT MISTAKE THE OWNER BARRED, AND THREE THINGS SAY SO:**
> 1. **Its headline win is anti-FORGETTING, and we do not have a forgetting problem** -- we measured
>    the opposite, `cos(profile_16k, profile_2k) = 1.000000`, a profile that never moved at all.
> 2. **Its own ablation puts the ATTRACTOR at +0.053** (NO_CLEANUP 0.880 vs FULL 0.933). The large
>    number belongs to two-stage replay, not to pattern completion.
> 3. **The partial-cue regime is already documented as STRUCTURALLY CAPPED** -- a cheating WordNet
>    oracle reads 0.8787 at the exact key and **0.0365 under the partial cue**. A cleanup attractor
>    cannot rescue a cue that thin.
> **➡️ SO THE NEXT TEST IS CHEAP AND WIRES NOTHING: apply a post-hoc non-linear cleanup to the
> profiles WE ALREADY HAVE and re-score on the SAME task, floors and CIs.** It is the one mechanism
> class eleven write-side failures point at, it is brain-pinned (D2 exists and is unfilled), and
> **it can fail cleanly: if a post-hoc transform cannot move our task either, the post-hoc lead dies
> too -- and that would be the single most informative negative available to us right now.**

> # 🧭 [PREVIOUS] HANDOFF -- 2026-08-20 POST-COMPACTION.
> *Supersedes the end-of-loop handoff below it.*
>
> ## 🛑 **THE OVERNIGHT LOOP IS DISARMED, BY OWNER INSTRUCTION, AND IT HAD BEEN MISSED.**
> `notes/COMMENTARY.md` **2026-08-20T12:48:12Z**: *"please turn off the hook loop when you see this,
> and in the running tab on gui make a button that turns the loop on, and another that turns it
> off."* Disarmed and verified. **It had sat unread through the whole compaction-prep sequence** --
> the loop kept firing while the instruction to stop it was already on disk.
>
> ## 🔴 **THE OWNER HAS BEEN LOOKING AT A THREE-DAY-OLD DASHBOARD. THIS IS THE FINDING OF THE**
> ## **SESSION, AND IT IS NOT A SUBSTRATE RESULT AT ALL.**
> **Their `status_gui.py` process started `2026-08-17 17:50` and was still running on 08-20.** Tk
> loads the file ONCE at startup, so **four landed commits were invisible to them** -- including the
> two they then asked for AGAIN, not knowing they already existed:
>
> | they asked | it already existed |
> |---|---|
> | on/off buttons for the loop (08-20 12:48) | `072c18b05`, **08-18 07:26** |
> | per-tab "updated" timestamp (08-19 19:44) | `d79473ab8`, **08-19** |
>
> **It also explains board Q67** (*"I still only see the old questions here - d1 d2 etc"*) and
> *"Why aren't you sharing any questions on the gui?"* **Every one of those was read as "the feature
> is missing" when the truth was "the window cannot see it".**
> **➡️ FIXED DURABLY (`faa255cc5`): the GUI now compares its own file's mtime at import against disk
> on every tick and shows an unmissable "THIS WINDOW IS RUNNING OLD CODE" banner.** Witness at
> `verification/test_gui_stale_banner.py` drives the REAL widget through four cases -- fresh, stale,
> restored (it must not latch), and no-baseline (it must stay silent). **All four pass, including the
> one that actually occurred.**
> **🧠 THE LESSON GENERALISES PAST THE GUI: a stale surface is INDISTINGUISHABLE from a current one,
> so the owner reasonably inferred absence from not-on-screen.** *This file already carried the rule
> -- "a stale RUNNING panel is read as evidence, which is worse than no panel" -- and the window was
> the one surface not held to it.*
>
> ## ✅ **THE REGISTRY "WHOLE-FILE DIFF" ANOMALY IS SOLVED AND BENIGN** (`2ad3d46a0`)
> 832 differing bytes, every one inside a `last_audit_utc` value (`08:35:45Z` -> `09:15:02Z`); the
> only byte substitutions are digits. The scheduled audit re-stamps every row, and an ISO timestamp
> is FIXED-WIDTH -- which is exactly why size, row count and id order all matched.
> **The prior session checked three PROXIES and wrote "identical on every check I could run". `cmp`
> answered it in one command.** *An absence claim built from proxies inherits every blind spot of the
> proxies.* **Do not re-open it.**
> **⚠️ STILL UNEXPLAINED AND UNTOUCHED: ~380 other modified files** (mostly `metrics.json` whose only
> change is a `ts_iso` marker) **plus 7 DELETIONS** (3 cornerstone `metrics.json`, 3
> `notes/_forensics_*`, 1 `prereqs/*.md`). The deletions are not marker churn. **Characterise before
> committing or reverting that tree.**
>
> ## 🔬 THRUST 1 LANDED -- **TIE. ROLE-BINDING BUYS NOTHING HERE.** 3 seeds, pre-committed verdict.
> Relaunched detached at `DIAG_N_READ=3000` after it died producing nothing.
>
> | seed | COOC floor | BAG | STRUCT | zero-struct skips |
> |---|---|---|---|---|
> | 7 | 10.0 | 36.5 (3.65x) | 49.0 (4.90x) | 131 |
> | 101 | 6.0 | 36.0 (6.00x) | 50.0 (8.33x) | 132 |
> | 20260819 | 7.0 | 36.5 (5.21x) | 47.0 (6.71x) | 121 |
>
> **POOLED PAIRED: `STRUCT - BAG +3.0`, 95% CI `[+0.0, +7.0]` -- NOT SEPARATED.**
> **⚠️ READ THE PER-SEED COLUMNS AND THE POOLED LINE CORRECTLY, BECAUSE THEY LOOK CONTRADICTORY AND
> ARE NOT: per-seed medians differ by ~13, the pooled paired median differs by 3. THE MEDIAN OF
> PER-PROBE DIFFERENCES IS NOT THE DIFFERENCE OF MEDIANS.** *The paired statistic is the correct one
> -- it is the one computed on identical probes -- and it does not separate from zero.*
> **➡️ PRE-COMMITTED THIRD BRANCH FIRES: a tie means THIS structural encoding is not the right
> structure, NOT that structure is irrelevant.** The four routes still point at the context unit;
> this particular unit is not the answer.
> **🚨 AND A CONFOUND I AM RECORDING RATHER THAN BURYING, BECAUSE IT CUTS AGAINST THE TIE: the STRUCT
> arm was built from LESS EVIDENCE.** 121-132 sentences per seed produced an all-zero structural
> vector (target absent from the parse) and were skipped, while the BAG arm took every one. **So
> "structure ties the bag" conflates ENCODING with COVERAGE, and coverage is already the single
> largest measured cost on this representation** (recording 68.8% of occurrences moved median rank
> 17 -> 46). *A coverage-matched re-run -- BAG restricted to exactly the sentences STRUCT could
> parse -- is the honest version of this test, and it was not run.*
> **⛔ BOTH ARMS STILL LOSE HEAVILY TO WORD-COUNTING (3.65x-8.33x). Neither is close.**
>
> ## 🎯 THRUST 2 UNBLOCKED, AND ITS PREMISE IS PARTLY WRONG
> The open question was where story pairs come from. **McGuffey carries exactly ONE labelled moral**
> across all seven readers -- that path is closed. `experiment_index.py` returns **0 cells** for both
> `moral` and `fable`, so the transfer test is genuinely unexplored.
> **BUT THE PLAN'S CLAIM THAT "WE CANNOT MEASURE NARRATIVE-KIND LEARNING AT ALL" IS TOO STRONG.**
> `social_iqa` is on the shelf: 33,410 items, three-way choice, *"what will Remy want to do next?"* /
> *"how would Others feel?"* -- **selection not generation, not fact-recall, and it existed years
> before any mechanism here.** It is the owner's own candidate shape (2), *what a character WANTED*.
> **AND WE ALREADY RAN IT.** Ten cells, 2026-08-11, `exp_crutch_fade_social_iqa_*`, all HARD_FAIL.
> **Every arm scored 0.3501-0.3975 against a majority-class floor of 0.3362** (validation n=1,954,
> balanced 3-way). **The word-counting baseline sat at 0.3501 too.** Scramble controls clean.
> **➡️ SO THE HONEST POSITION IS NOT "no instrument". IT IS: WE HAVE ONE, IT WAS RUN, AND BOTH THE
> SUBSTRATE AND THE CRUDE FLOOR CAME BACK AT CHANCE.** *Those cells were measuring something else --
> whether a crutch fades -- so chance was a by-product, not the target, and they predate
> `keep_noting_grounded`.* **⚠️ WHEN THE CLEVER METHOD AND THE CRUDE FLOOR BOTH SIT AT CHANCE, THE
> LIKELIEST READING IS THAT THE TEST IS NOT REACHING EITHER -- which is UNTESTABLE, not negative.**
> **THE CHEAP NEXT MOVE, AND IT IS HOURS NOT DAYS: hand that test the answer in a form it cannot
> miss and check the score rises.** If it does not, the instrument is broken for our purposes and
> building on it would waste weeks. If it does, we own a working narrative ruler already, and the
> owner's moral/transfer test becomes the harder SECOND step instead of the first.
> *This is the project's own highest-yield habit -- ask whether the experiment COULD have succeeded
> before asking why it did not -- applied to an instrument instead of a mechanism.*

> # [SUPERSEDED] 2026-08-20 END-OF-LOOP HANDOFF
> *Supersedes the 2026-08-19 handoff below it. Everything under this block is the RECORD, newest
> first; this block is the only thing that needs reading to resume.*
>
> ## 🎯 **Q76 ANSWERED -- THE NARRATIVE MEASURE IS "SUMMARISE + GENERALISE THE TAKEAWAY".**
> *Owner 2026-08-20: "stories typically have morals - what's the moral of the story? that's advanced
> - if someone does something stupid and goes to jail, the moral is, you should try to adhere to the
> law etc. PPL can take different morals from the same story. I think a high score would be able to
> summarize what happened in the story and generalize any takeways from it."*
>
> **TWO COMPONENTS, AND THE SECOND IS THE ONE THAT MAKES IT NOT FACT-RECALL:**
> 1. **SUMMARISE** what happened -- a story-level situation model.
> 2. **GENERALISE the takeaway** -- abstract from *these events* to a *transferable principle*.
>
> **⛔ THREE HARD DESIGN CONSTRAINTS, ALL FROM THE OWNER'S OWN WORDING OR THIS PROJECT'S INVARIANTS:**
> - **"PPL can take different morals from the same story"** -> there is **NO single gold answer**.
>   An exact-match scorer is invalid by construction. *This is the owner telling us the metric shape,
>   not just the metric.*
> - **NO LLM AT INFERENCE (the standing invariant)** -> we cannot have a model read a free-text
>   summary and judge it. **So the task must be SELECTION / DISCRIMINATION, not generation.**
> - **It must NOT be fact-recall wearing a costume** -- the failure that produced tonight's
>   unfalsifiable claim.
>
> **➡️ THE SHAPE THOSE THREE CONSTRAINTS FORCE, AND IT IS A GOOD ONE: A TRANSFER TEST.**
> Read story A (someone breaks a rule, suffers a consequence). Then present story B carrying the
> **SAME principle** with **DELIBERATELY ZERO SURFACE OVERLAP** -- different characters, setting,
> vocabulary. Ask the substrate to pick which of N candidate principles B shares with A.
> **THE CAN-FAIL FLOOR IS BUILT IN AND THAT IS WHY THIS SHAPE WINS: a system that memorised A's
> WORDS must fail B, because the word overlap is controlled to ~zero by construction.** *Surface
> matching cannot pass it, so passing means something abstracted. And "different people take
> different morals" is accommodated -- the candidates are principles, scored as discrimination, with
> no claim that one reading is uniquely correct.*
> *This merges Q76's options (1) situation model and (4) transfer; the TRANSFER half is what keeps it
> honest, and the SUMMARISE half is what the owner asked for on top.*
>
> **⚠️ OPEN AND NOT YET SOLVED -- WHERE THE STORY PAIRS COME FROM.** We would need story pairs sharing
> a principle with no lexical overlap. **Writing them ourselves risks encoding the answer in the
> structure we chose**, which is the "did the test items exist before the mechanism did?" trap this
> project already names as its strongest free predictor of a bogus result. *Check the corpus shelf
> for existing labelled material (fables have explicit morals) BEFORE authoring any.*
>
> ## ⛔ **THRUST 1 DIED AND PRODUCED NOTHING -- RE-LAUNCH REQUIRED, DO NOT READ ITS LOG AS A RESULT.**
> `scratch/struct_vs_bag.log` contains ONLY the encoder self-test line (`struct norm 27.857 | bag
> norm 32.062`). The harness reports no completion record -- it was killed when the previous process
> exited. **The script is correct and ready; it simply needs re-running.** *It is SLOW because the
> structural encoder parses every sentence -- budget accordingly, and consider a smaller
> `DIAG_N_READ` for a first pass.*

> ## 🔀 **TWO THRUSTS, RUN IN PARALLEL (owner 2026-08-20). THEY DO NOT COMPETE FOR ANYTHING.**
> *One is COMPUTE-bound and runs unattended; the other is DESIGN-bound and needs no compute. That is
> why both can be live at once -- and why the answer to "what else can you do while it runs" is not
> "a second experiment".*
>
> ### THRUST 1 -- **RUNNING**: is CONTEXT-AS-STRUCTURE better than CONTEXT-AS-BAG?
> `scratch/diag_structure_vs_bag.py`, 3 seeds, 8,000 sentences. ONE variable: what a word's context
> vector IS (`context_vector_masked` vs `structural_vector_masked`). Both arms built from the SAME
> sentence pool, same probes, same COOC floor.
> **Guarded against the trap that already cost me a wrong claim: the structural encoder returns an
> all-zero vector SILENTLY when handed a surface form instead of a lemma, and an all-zero arm scores
> median rank 1.0.** A positive-control self-test runs first; every arm's non-empty fraction is
> asserted before scoring; zero-vector skips are counted and printed.
> *Judged on EXPOSITORY prose per the owner's amendment. Narrative is an observation, not pass/fail.*
>
> ### THRUST 2 -- **THE INSTRUMENT GAP. NO COMPUTE. THE HIGHER-VALUE ONE.**
> **We cannot measure narrative-kind learning at all**, so every claim about this substrate failing
> on stories is currently unfalsifiable -- including the one I made tonight with a table and four
> decimal places. *Owner: "textbooks are supposed to have facts laid out for learning, stories are
> there to enjoy -- to get a new perspective... it's not the same kind of learning at all."*
> **THE QUESTION: what would count as EVIDENCE that this substrate got something from a story?**
> Candidate shapes, none yet chosen, all needing a can-fail floor before they mean anything:
> - **situation model** -- after reading, which entities are still "live", and who did what to whom?
>   *(E2 situation-model register exists in ORGAN_MAP)*
> - **perspective / stance** -- can it tell what a character WANTED, as distinct from what happened?
> - **expectation violation** -- does it register that something UNUSUAL happened in a scene, which
>   is narrative's analogue of a fact being surprising
> - **transfer** -- does reading a story change behaviour on a LATER, unrelated text?
> **⚠️ THE TRAP TO AVOID IS THE ONE WE JUST FELL INTO: any narrative metric must NOT be fact-recall
> wearing a costume.** If the scorer ends up asking "predict the missing word", it is the textbook
> ruler again and will return the same answer for the same wrong reason.
> **➡️ THIS IS THE ONE I WANT THE OWNER'S VIEW ON.** It is a definition question, not a measurement
> one, and getting it wrong costs more than any single experiment: *a bad narrative metric would make
> the substrate look fixed or broken for reasons unrelated to whether it understood anything.*

> ## ✅ WHAT IS TRUE AND SHIPPED
> **`keep_noting_grounded`** -- the substrate no longer seals a word's representation the instant it
> grounds. Additive, **DEFAULT-OFF**, all self-tests pass, registered (row 205).
> *Motivating fact: 0 of 60 grounded terms gained a single trace over 14,000 further sentences;
> `cos(profile_16k, profile_2k) = 1.000000`.* Three gates had to open -- two write-side and one
> read-side, where `profile()` was silently discarding what the fix collected.
>
> | corpus | 3 seeds, DEFAULT | 3 seeds, FIX |
> |---|---|---|
> | `simplewiki` | 4.71x / 5.00x / 5.00x | **2.57x / 3.00x / 3.22x** |
> | `textbook_biology_2e` | 5.45x / 5.63x / 4.76x | **2.60x / 2.66x / 2.74x** |
>
> Pooled paired: simplewiki **-6.0** CI [-8.0,-4.0]; textbook **-21.0** CI [-26.0,-16.0]. Phase slope
> **+1.410 -> +0.667**. Post-only beat whole-pile 3/3, so the shipped form merges only traces at
> `grounded_at_n_traces` onward. **⛔ STILL LOSES TO WORD-COUNTING: the curve bends, it does not cross.**
>
> ## ➡️ THE ONE UNSTARTED ACTION -- CLEARED, DOCUMENTED, NOT RUN
> **Turn on `StructuralEncoder` (additive, default-off) and measure context-as-STRUCTURE against
> context-as-BAG-OF-NEARBY-WORDS**, on the same task, floors and seeds.
> Three-read check: 1 archive hit / **0 landed**, no ORGAN_MAP prohibition, no registry claim. Organ
> verified working (norms 22-33 vs the bag's 32.68; front-end assets present).
> **⚠️ PASS TARGETS AS LEMMAS (`content_lemmas` output). A surface-form mismatch fails SILENTLY as a
> zero vector, and an all-zero arm scores median rank 1.0 -- a fake breakthrough. That cost me a
> wrong claim and one command to catch.**
>
> ## ⚖️ THE DISCRIMINATOR WAS AMENDED BY THE OWNER (dated, before any arm was scored)
> *"You don't approach a textbook like a story... it's not the same kind of learning at all."*
> **SUPERSEDED:** *structure must help narrative MORE than exposition, or it is only a better encoder.*
> **CURRENT:** judge structure on **EXPOSITORY prose**, where our fact-recall task fairly measures
> what the text was there to teach. **Narrative is a separate OBSERVATION, not pass/fail.**
>
> ## 🚨 DO NOT QUOTE THESE -- CLAIMS I MADE AND RETRACTED
> 1. *"The substrate can't learn from narrative (12.6% vs 0.7%) -- a fidelity failure."* **DEMOTED to
>    UNFALSIFIABLE.** Our task is FACT RECALL; scoring what a novel taught with a textbook's metric is
>    a METRIC infidelity. **We have no measure of narrative-kind learning at all.**
> 2. *"The `gap_detector` ablation is inert; prior results need re-checking."* **FALSE ALARM.** The
>    organ is correct (seed-known False 8/8, grounded False 8/8, pending True 8/8); it is only ever
>    asked about words two earlier filters have already left. **Correct and redundant. No audit needed.**
> 3. *"Accumulation is the problem, 4th time."* **WITHDRAWN** -- that rested on an internal statistic;
>    on the task the sum BEATS any single trace (+13.0, CI [+6.0,+17.5]).
> 4. *"Our code is 4-12x too diffuse, so the projection is the defect."* **OVER-ATTRIBUTED** -- an
>    ordinary text encoder sits there too, under a different formula.
> 5. *"PBV discarded recoverable signal -- build cross-situational tracking."* **CIRCULAR** (margin IS
>    the grounding criterion). Re-tested: pooling scores 0.75-0.80x of a SINGLE encounter. **Do not build.**
>
> ## 📉 CLOSED WITH EVIDENCE (do not re-propose without reading these)
> - **D7 / successor representation: DO NOT WIRE.** Faithful to its pinned closed form, but on reading
>   order plain 1-step co-occurrence beats it **18.5 vs 45.0** (+25.5, CI [+21.0,+29.0]). SR is pinned
>   for NAVIGATION; mapping it onto text was OUR invention. *(ONE text sample, CIs over 408 pairs --
>   the script says "seeds" and is WRONG; only the uniform arm was seeded.)*
> - **Owner Q74: SURPRISE DOES NOT SELECT.** High/low/random-surprise halves indistinguishable at
>   matched count (all +0.0, CI [+0.0,+1.0]); only VOLUME moves it. **Mean surprise 0.4206-0.4252
>   against a 0.5 no-information floor -- ~4% from chance, so there was nothing to select on.**
> - **Eight write-side routes closed** (residual gate, novelty, precision, k-WTA, divisive
>   normalisation, delta-rule family, retrieval practice, best-single-trace) **plus the write MOMENT**.
> - **ORGAN_MAP gap list was 2/5 STALE** (D7, H2 marked MISSING while both exist). Corrected in place;
>   all 39 sections re-audited; contradictions now **NONE**.
>
> ## 🧠 FIDELITY AUDIT (owner asked twice): 6 of 8 negatives had one; both gaps filled
> **And filling one INVERTED it:** *"the sum beats any single encounter"* is CONSISTENT with pinned
> ORGAN_MAP B1' (*LATL conceptual combination is approximately ADDITIVE*). **The first POSITIVE
> fidelity result of the session -- filed for hours as a dead lead.**
> **STANDING RULE ADDED TO CLAUDE.md: a statistic the mechanism OPTIMISES is not an outcome. It may
> DIAGNOSE, never DECIDE.** Anchor margin, trace coherence and effective dimensionality each produced
> a confident story the task then refused.
>
> ## 🎯 THE BIGGEST OPEN PROBLEM IS AN INSTRUMENT GAP, NOT A MECHANISM
> **We cannot measure narrative-kind learning.** Perspective, situation model, what a character
> wanted -- nothing in the instrument scores any of it. **Until that exists, no experiment can resolve
> whether this substrate learns from stories**, and more compute cannot help. *That is a design
> question for the owner, not a run.*
>
> # [SUPERSEDED] 2026-08-19 HANDOFF -- END OF FIDELITY-AUDIT SESSION
> *Everything below it is the record, newest-first. The older handoff blocks are SUPERSEDED: their
> "next steps" are all done.*
>
> ## ✅ LANDED SINCE THIS PLAN WAS LAST WRITTEN -- three items below are now ANSWERED, not pending
> **1. THE BRAIN-FIDELITY AUDIT THE OWNER ASKED FOR IS COMPLETE.** All three negatives that had no
> fidelity check now have one. **Three of my four explanations were REFUTED by their own
> pre-committed controls** -- the diagnostics were genuinely can-fail and they fired against me.
> - *Spoke failure:* hub-and-spoke POSITION was NOT the cause. 11 of 12 grounded dimensions read
>   back out of the profile (ridge, 5,950 words, out-of-fold). **The magnitude is the finding:
>   frequency reads out at R^2 0.4819 vs 0.01-0.05 for a typical sensorimotor dimension.**
> - *Reading (C):* not noise (matched 0.4546 / stranger 0.4888 / chance 0.5001, n=55,399), not a
>   between/within mismatch (ICC 0.201 -- within-word variation is 80%), and the missing precision
>   term is real but **the archive already tested the precision-weighted form and it also sat at
>   chance** (Friston arm 0.530 vs flat 0.542).
> - **THE ONE ACCOUNT THAT SURVIVES:** *a write gate chooses WHICH counts get added; it cannot
>   change that the code IS a count.* Same conclusion the geometry and subsumption results reached
>   from two other directions. **This is why "sharpen the predictor" below is now second-line.**
>
> **2. Q72 IS ANSWERED ON BOTH HALVES, AND THEY DIFFER.** The diversity test described further down
> as "running" has LANDED:
>
> | | corpora | OUR median rank | counter | ratio |
> |---|---|---|---|---|
> | ONE_CORPUS | 1 | 91.0 (CI 68.5-111.0) | 19.5 | 4.67x |
> | MANY_CORPORA | 27 | 106.5 (CI 89.0-122.0) | 20.0 | 5.33x |
>
> **Difference +15.8, 95% CI [-10.0, +42.5] -- NOT SEPARATED. Passive breadth is UNTESTED at this n,
> NOT a negative. ⛔ Never quote "spreading reading across corpora made it worse."**
> **BUT THE OTHER HALF ALREADY LANDED HARD_PASS a month ago:**
> `exp_breadth_foundation_active_growth_loop_ud_ewt_v1` -- gap-targeted active growth moved coverage
> **0.50 -> 0.79**, real-vs-shuffle AUC **0.8924 vs 0.5122 +- 0.1003**. *The load-bearing word in the
> owner's question is "PATCHY", not "another textbook".*
>
> **3. THE OWNER'S "WHAT ELSE ARE WE MISSING?" HAS A CONCRETE ANSWER AND IT KEEPS PAYING.** Querying
> the RESULTS archive (not the code registry) found: today's write-gate negative had been measured a
> month earlier (flat raw surprise at chance, 0.545 and 0.542, clean controls); a PRIOR residual gate
> already recorded **skip=0.00** (`exp_pc1_predictive_coding_residual_gate_v1`); and both corrections
> in the next block. **`tools/experiment_index.py query "<kw>"`. `substrate_query.sh` returns zero
> bytes and exits 0 -- never use it.**
>
> ## ⛔ THREE CORRECTIONS. DO NOT RE-QUOTE THE SUPERSEDED FORMS.
> 1. The audit is **THREE of four** refuted, not four. The familiarity hypothesis was NOT refuted --
>    I published SMOKE numbers (161 terms). At full n (1,590): slope **-0.0035, CI [-0.0052,
>    -0.0018]**, 63% of words negative. The residual DOES fall as a word becomes familiar.
> 2. **Passive corpus breadth is UNTESTED, not negative** (see the CI above).
> 3. **"Our code is 4-12x too diffuse" is OVER-ATTRIBUTED.** A prior cell measured MiniLM at
>    **d_eff 91.6** under a **DIFFERENT FORMULA**. **⤷ NOW RESOLVED, AND THIS CORRECTION WAS ITSELF
>    WRONG.** The invalid comparison was real -- formula differs 1.2x, POPULATION differs 2.7x
>    (consolidated 71.5 vs all-terms 191.5) -- but *"probably normal for text"* is NOT supported: on
>    the same formula we read **238.6 vs MiniLM 91.6 = 2.60x**.
>    **✅ THE CLEAN, FULLY-MATCHED COMPARISON IS THE ONE TO QUOTE: our profiles are LESS
>    CONCENTRATED THAN THE RAW COUNTS THEY ARE BUILT FROM -- 191.5 vs 131.7, top-4 share 0.054 vs
>    0.092, with noise/shuffled at ~249 so both are real structure. THE RANDOM PROJECTION
>    DE-CONCENTRATES.** *Sharper than the brain comparison ever was, needs no pinned figure, and
>    names the PROJECTION rather than the COUNTING as the suspect.*
>
> ## ➡️ NEXT STEPS, IN ORDER
> 1. ~~Recompute participation ratio under both formulas.~~ **DONE -- see correction 3 above.**
> 2. ~~Remove the dominant common direction and re-score.~~ **DONE, AND IT IS CLOSED. NOT A LEAD.**
>    Centring gives a small separated gain (median rank **91.0 -> 83.0**, paired -4.41, CI [-6.83,
>    -2.06]) and removing ANY further component makes it monotonically **worse** (PC2 +3.73, PC4
>    +6.06, PC8 +11.71). **⛔ But the FREQ floor -- ranking candidates by corpus frequency, never
>    looking at the sentence -- reaches 71.0, and COOC reaches 20.5. EVERY ARM LOSES TO A FLOOR THAT
>    IGNORES THE QUESTION.** *My script declared "REAL LEAD" because its gate compared only to COOC;
>    it printed FREQ and never used it. Gate fixed in the script; verdict corrected to NOT A LEAD.*
>    **🔑 AND IT CLOSES THE POST-HOC ROUTE: if the diffuseness lived in a few removable directions,
>    removing them would help. It hurts. The variance is spread thin across the whole spectrum --
>    which is what a random projection does -- so no transform applied AFTER the fact reaches it.**
> 3. ~~Test the gap-targeted growth loop.~~ **DONE. UNDERPOWERED, NOT NEGATIVE -- AND THE ORGANS
>    NEEDED NO ADAPTER.** `gap_detector` / `gap_driven_reader` / `three_tier_loop` are built, import
>    clean, and take `sub.state` directly; `substrate.py` wires none of them. Gap signal verified
>    with a positive AND negative control (0 of 40 grounded words are gaps, 20 of 40
>    non-consolidated ones are). **Result: GAP minus PASSIVE -88.98, CI [-220.31, +40.72]; GAP minus
>    rate-matched RANDOM -6.68, CI [-133.01, +121.76]. Neither separated, and a half-width of
>    130-220 ranks means only an enormous effect was detectable. UNTESTED AT THIS POWER.**
>    *⚠️ Run 1 was VOID at 0.981 arm overlap and my gate passed it at `jac < 0.99`. Third
>    too-lenient gate of the session. Fixed to refuse above 0.60 and fail loud.*
>    **🔑 AND THE PRIOR HARD_PASS MEASURED COVERAGE (0.50 -> 0.79), NOT RANK. Different claim. This
>    is not a failure to reproduce it, and nothing here licenses "the owner's idea does not work".**
> 4. ✅ **DONE -- THE PHASE DIAGRAM LANDED AND IT REFRAMES THE PROGRAM. THERE IS A REAL BOUNDARY
>    NEAR ~1,000 SENTENCES: at 900 we BEAT the counter (0.95x); by 16,000 we are 6.42x behind,
>    monotonically across seven points, slope +1.708 per e-fold.**
>    **⛔ MORE DATA IS NOT THE LEVER -- IT IS THE PROBLEM.** Sharpest form: 8,000 -> 16,000, our arm
>    does not move (114.5 -> 115.5) while the counter IMPROVES (31.0 -> 18.0). *We stop extracting
>    anything from extra text; counting does not.*
>    **All four component variables degrade together** -- coverage halves (0.961 -> 0.435),
>    effective dims rise 9x (10.0 -> 91.8), residual spread shrinks then FLATLINES (0.1099 -> 0.0661
>    -> 0.0661 -> 0.0661). **That flatline HARDENS the write-gate closure: the spread saturates
>    rather than widening, so scale never reopens it. My scale-dependence flag was wrong, in the
>    safe direction.**
>    **🧠 FIDELITY: the brain's hub CONCENTRATES with experience (the pinned ~4-12). Ours DIFFUSES,
>    progressively. Same divergence the geometry found, now as a TRAJECTORY not a snapshot.**
>    *⚠️ Single seed per point, one corpus, pool grows 40 -> 480, no CI on the ratio. The
>    MONOTONICITY across seven points carries the weight, not any single value.*
>    **⬅️⬅️ AND IT SETS THE NEXT ITEM, WHICH IS NOW THE TOP ONE: SATURATION HAS TWO CANDIDATE
>    CAUSES AND THEY ARE SEPARABLE.** Coverage falling (we record less of what we meet) and the
>    projection diffusing (the code spreads out) both track the phase curve. The 8,000-point
>    decomposition already said not-recording is the bigger term (17 all-occurrences / 46
>    recorded-only / 81 our profiles). **So: RE-RUN THE PHASE SWEEP WITH COVERAGE FORCED TO ~1.0 and
>    ask whether the curve FLATTENS.** If it does, the defect is note-taking and it is fixable. If
>    the curve still climbs, the defect is the projection and no amount of note-taking reaches it.
>    *That is one experiment that discriminates the two stories, and nothing else queued does.*
>    **✅ RAN. THE ANSWER IS "BOTH, AND THEY ARE INDEPENDENT."**
>    - **Note-taking is REAL and is the biggest lever measured all session.** Forcing a note on
>      every encounter improves the level at every point (8,000: **3.69x -> 2.06x**; 16,000:
>      **6.42x -> 4.39x**) and holds parity with the counter to 1,000 sentences (**0.98x**).
>    - **It is NOT sufficient. Slope falls only 39% (+1.708 -> +1.035) and STILL CLIMBS.** Perfect
>      note-taking still leaves us 4.39x behind at 16,000 and still degrading.
>    - **🔑 AND IT DOES NOT TOUCH THE DIFFUSION AT ALL: PR 12.6 -> 91.8 as-is vs 13.2 -> 92.3
>      forced.** Identical at every point. **WRITING MORE CANNOT CONCENTRATE A CODE.**
>    **🧠 SO THE BUILD TARGET IS NAMED, AND IT IS THE WRITE OPERATION, NOT THE WRITE VOLUME.** The
>    brain's hub concentrates through COMPETITION between representations; ours SUMS. Every
>    post-hoc route is now closed by measurement (centring helps 8 ranks then hurts; removing
>    components hurts monotonically; recording everything changes nothing about concentration).
>
> ## ✅ RAN AND FAILED -- **COMPETITION AT WRITE TIME DOES NOT WORK, AND THE REASON IS USEFUL.**
> No arm cut the phase slope: SUM **+1.035**, KWTA8 **+1.683**, KWTA32 **+1.174**, NORM **+0.972**.
> k-WTA is worse than plain summing at EVERY point. *Prior was recorded as low in advance (two
> adjacent sparsity failures, read before building) and the prior was right.*
> **🔑 THE MECHANISM INVERTS MY OWN PRE-REG. I wrote that k-WTA lowers effective dimensionality BY
> CONSTRUCTION so it must not be the outcome. It RAISED it: 92.3 (SUM) -> 130.2 (KWTA8) at 16,000.
> Sparsifying the addends DECORRELATES them, so the sum spreads over MORE directions.
> SPARSITY ON THE INPUT OF AN ACCUMULATOR IS AN ANTI-CONCENTRATION OPERATION.**
> **🧠 FIDELITY -- POSITION, and it names the next build exactly.** Cortical/DG sparse coding is
> competition ACROSS THE POPULATION at encoding, winners suppressing others, and the SETTLED pattern
> is stored. Ours filters WITHIN one incoming trace and then sums independently. **No competition
> between encounters, none between terms. We copied sparsity's SHAPE and not its POSITION.**
>
> ## ✅ RAN -- **REFUTED BACKWARDS, AND IT HANDED US THE BEST RESULT OF THE SESSION.**
> Incremental removal HURTS (INCR_CENTER **+1.406**, INCR_OJA **+2.025** vs SUM **+1.035**).
> **POST-HOC centring is the best arm measured all session: slope +0.631 (39% flatter) and the ONLY
> intervention that has ever CONCENTRATED the code -- effective dims 92.3 -> 29.1 at 16,000.**
> **🔑 Same lesson k-WTA taught: an EARLY estimate of the shared direction is a BAD estimate, and
> subtracting a bad estimate corrupts every trace. OPERATIONS ON THE ADDENDS HURT; THE SAME
> OPERATION ON THE ACCUMULATED RESULT HELPS.** *Retires my own "the store must never accumulate it"
> intuition, which the plan stated confidently.*
> **🚨 And my verdict line said "THE ACCUMULATION ROUTE IS EXHAUSTED" -- wrong. The gate compared
> only the INCREMENTAL arms to SUM, so POSTHOC was invisible to the code judging it. Fourth
> mis-specified gate; fixed to report the winner across ALL arms first.**
> *⚠️ POSTHOC is still 3.11x behind the counter at 16,000. It flattens the curve; it does not clear
> the floor. Both statements travel together.*
>
> ## ✅ 2x2 RAN -- **SYNERGISTIC, AND THERE IS NO CHEAP VERSION.**
> A **+1.708** / B as-is+centred **+1.384** / C full+sum **+1.035** / D full+centred **+0.631**.
> **Centring ALONE buys 19% of the 63% total -- under a third. The cheap standalone win I was about
> to recommend does NOT exist; the two are entangled and centring needs complete counts underneath.**
> Super-additive: independence predicted +0.838, measured +0.631. *And it VALIDATED the cross-run
> chaining I had flagged as unsafe -- predicted -63%, measured -63%.*
>
> ## ✅ Q71 RAN -- **VOLUME MATTERS, SELECTION DOES NOT. AND A SLOPE NEARLY FOOLED ME.**
> At matched budget (half of each term's occurrences): **NOVEL vs RANDOM is a coin flip** -- novelty
> wins 3 of 5 points, all deltas within +-0.14 except one. Both land between AS_IS and FULL, so
> **half the traces buys ~55% of full coverage's benefit however they are chosen.**
> **🚨 My script printed "novelty selection is ANTI-correlated with usefulness (8% vs 55%)". NOT
> SUPPORTED -- the final point's delta (0.944) is 8.7x the mean of the other four (0.109). Fifth
> gate defect, new species: ENDPOINT-SENSITIVE rather than too lenient.**
> **🧠 The residual conflates A NEW SENSE with A NOISY OCCURRENCE, so it acts as an OUTLIER detector.
> The owner's principle is NOT refuted -- WE HAVE NO SIGNAL CAPABLE OF IMPLEMENTING IT.**
>
> ## ✅ RAN -- **PRECISION WEIGHTING IS MEASURABLE BUT NOT USABLE. FOURTH SELECTION NEGATIVE.**
> Built prefix-only (leave-one-out) BECAUSE the archive's four-cell arc said that is what separates
> its HARD_PASS from its HARD_FAIL. Landed exactly where `..._derived_v1` landed: a clean, real
> statistic that does not translate into a working gate. PREC beats random at **2/5** points and the
> unweighted residual at **3/5**; slopes PREC **+1.294** vs RANDOM **+1.337** vs FULL **+1.035**.
> **🔑 AND IT CORRECTS MY OWN MECHANISTIC STORY: I had blamed the write gate's failure on the
> selector having NO SPREAD (sd 0.066). Precision has 2-3x MORE spread (sd 0.134-0.208) and fails
> anyway. SPREAD WAS NOT THE BINDING CONSTRAINT.**
> **➡️ FOUR INDEPENDENT TESTS NOW AGREE: WHICH TRACES ARE KEPT DOES NOT MATTER -- ONLY HOW MANY.
> STOP BUILDING SELECTORS.** (write gate 0/54; NOVEL~RANDOM; PREC~RANDOM; every selective arm sits
> between AS_IS and FULL regardless of rule.)
> **🧠 FIDELITY -- POSITION, THIRD TIME.** G2's precision-weighted residual is a claim about
> **LEARNING** (how much to UPDATE), not about **WHICH EPISODES TO STORE**. We have tested it four
> times in the storage role and never in the update role -- because our profiles HAVE no update rule
> to modulate; they only add. *Same position error as the sensorimotor spoke (a re-ranker where the
> brain has an input) and k-WTA (competition inside a trace where the brain has it across a
> population).* **THE PINNED TERM MAY STILL BE RIGHT AND TESTED IN THE WRONG PLACE.**
>
> ## ✅ RAN -- **THE UPDATE RULE CHANGES NOTHING. THE SUM IS OPTIMAL INSIDE ITS OWN FAMILY.**
> Nested control PASSED everywhere (`eta=1/n` reproduced SUM's ranking exactly, delta +0.00 at all
> five reads) -- so the sum is not a rival arm, it is a POINT INSIDE the delta-rule family.
> Every fixed eta is worse and worse faster: slopes **+1.798 / +2.354 / +2.879** vs SUM **+1.035**;
> at 16,000 the recency arms blow out to **6.92-10.08x** against the sum's **4.39x**. Precision on
> the step size does not rescue it (**+1.536**, 3/5).
> **The pre-registered risk is exactly what happened, and it was written verbatim: *"if the eta
> sweep says smaller-is-always-better, the winner IS the sum and this is a NULL."***
>
> ## 🧱🧱 STRATEGIC CONCLUSION, NOW SUPPORTED BY SIX FAILED INTERVENTIONS:
> **THE REPRESENTATION IS INSENSITIVE TO *HOW* IT IS WRITTEN AND TO *WHICH* TRACES GO IN.**
> Failed on the phase curve: residual gate, k-WTA, normalisation, incremental decorrelation,
> novelty/precision selection, the entire delta-rule family. **The ONLY two things that have ever
> moved the slope are HOW MANY traces exist (coverage, 39%) and a POST-HOC transform (centring,
> 39%) -- neither is a rule about writing.** *The limit is the REPRESENTATION -- a random projection
> of counts -- not the procedure that fills it.*
>
> ## ✅ RAN -- **THE NON-STATIONARY ESCAPE IS CLOSED, AND THE PREMISE WAS FALSE BEFORE IT STARTED.**
> **THE CORPUS WAS NEVER STATIONARY.** Measured drift: **NATURAL 0.6895, BLOCKED 0.6905 (within
> 0.1%), SHUFFLED 0.6146.** Natural reading order drifts as much as MAXIMAL topic-blocking, and
> shuffling is the only ordering that REMOVES structure. *Wikipedia arrives article by article, so a
> word's contexts already shift as you read.* **⛔ SO THE ESCAPE IN THE BLOCK BELOW WAS VOID WHEN I
> WROTE IT -- the delta rule had been under drift all along, and its earlier null was not a regime
> artifact.** You cannot add drift to text that already has it, which is ALSO why my blocking
> manipulation reads weak (1.12x). Same fact seen twice, not two problems.
>
> **AND THE DIRECTION THE ESCAPE PREDICTS RUNS BACKWARDS.** The hypothesis is not "some delta arm
> wins somewhere" -- it is that as drift rises, forgetting should cost LESS:
>
> | ordering | mean drift | penalty for forgetting (DELTA_020 - SUM) |
> |---|---|---|
> | SHUFFLED | 0.6146 | **+1.062** |
> | NATURAL | 0.6895 | +1.494 |
> | BLOCKED | 0.6905 | **+2.115** |
>
> **corr(drift, penalty) = +0.051 across 12 cells -- the escape predicts NEGATIVE. Forgetting gets
> MORE expensive as contexts drift, not less. A delta arm beats the sum in 3 of 24 cells.**
> **✅ FREE HARNESS CHECK, AND IT PASSED: SUM is order-invariant by construction and read identical
> across all three orderings at all four reads.** *A sum cannot care about order; if it had moved,
> the experiment was broken.*
> **➡️ PER THIS PLAN'S OWN PRE-COMMITMENT -- "if it loses even under drift, the delta rule is dead on
> this instrument outright and the write-side route is closed for good" -- IT IS CLOSED.**
> *⚠️ SCOPE, STATED WITH THE RESULT: the achievable drift range is narrow (0.6146-0.6905). This
> closes the escape AS PROPOSED (reordering ONE corpus). It does NOT test extreme regime change --
> an anatomy textbook followed by Sherlock Holmes. That version is queued below with its prior
> recorded LOW IN ADVANCE, because within the range we CAN see, more drift makes recency worse.*
>
> **🚨 SIXTH GATE DEFECT, AND A NEW SPECIES: EXIT-ORDER, NOT LENIENCY.** The script checked "did my
> manipulation work" FIRST and exited; the "is the corpus already drifting" check sat below it and
> never ran. Both conditions were true. **The run printed the uninformative reading and SUPPRESSED
> the informative one** -- it reported "treatment did not take, nothing else is reportable" when the
> data said "there was nothing to add, and here is the answer anyway." *Fixed: reading 4 is now
> evaluated first, and a weak manipulation no longer aborts a readable comparison.* **The five prior
> defects were gates set too LOW; this one was set in the wrong ORDER. Checking a gate's threshold is
> not enough -- check what it EXITS BEFORE.**
>
> ## 🔎 ARCHIVE HIT -- **"TRY A LEARNED PROJECTION (PPMI+SVD)" WAS ALREADY RUN. IT LOST. AND THE**
> ## **THING THAT WON WAS REMOVING EXACTLY ONE DIRECTION -- WHICH IS WHAT TODAY FOUND SEPARATELY.**
> *I was one step from building PPMI -> SVD as the successor to post-hoc centring. Queried first.
> `"svd"` returns 44 cells, `"ppmi"` 42. A FOUR-CELL ARC already walked this exact path.*
> Disk-verified from `metrics.json`, all glass-box and earned from corpus counts:
>
> | step | representation | ceiling | unstated-goal recovery |
> |---|---|---|---|
> | earned_v1 | raw PPMI, single novel | 0.500 | 0.333 |
> | earned_v2 | **PPMI + SVD**, 5 corpora, k=250 | **0.333** | **0.000** |
> | earned_v3 arm_a | raw PPMI, 5 corpora | 0.333 | 0.000 |
> | earned_v3 arm_b | **PPMI + MEAN REMOVAL (1 direction)** | **0.667** | 0.333 |
> | (reference) | borrowed BGE embedding | 0.833 | 1.000 |
>
> **⛔ SVD MADE IT WORSE, not better -- below even the single-novel baseline it was meant to improve.**
> **✅ AND `mean_removal_n_top_directions = 1` DOUBLED the ceiling and broke the collapse
> (`collapse_broken=True`, misrank 1.000 -> 0.667, structure accuracy 0.667 -> 1.000).**
> **🔑 TWO INDEPENDENT INSTRUMENTS, DIFFERENT TASKS, DIFFERENT REPRESENTATIONS, SAME SHAPE: REMOVE
> EXACTLY ONE DOMINANT DIRECTION AND STOP.** Today's phase curve found post-hoc centring is the best
> arm of the session (slope +0.631, PR 92.3 -> 29.1) and that removing PC2/PC4/PC8 makes it
> monotonically worse. *That agreement was reached by two routes that share no code.*
> **⚠️⚠️ AND THE CAVEAT IS SEVERE, SO IT TRAVELS ATTACHED: N = 6 PROBE ITEMS. The cell's own verdict
> says `CHEAP_EXHAUSTED (N=6 probe, directional)`. 0.333 -> 0.667 is TWO ITEMS. This is DIRECTIONAL
> AGREEMENT AND NOTHING MORE -- it must never be quoted as confirming centring.** *An underpowered
> WIN read as a capability statement is the same error as an underpowered null, wearing better
> clothes.*
> **➡️ WHAT IT CHANGES: "try a learned projection next" is retired as a fresh idea. If SVD is
> revisited it must be as a REPLICATION of a cell that already lost, with power, and stated as such.**
>
> ## ✅ RAN -- **EXTREME DRIFT TESTED ACROSS SIX CORPORA. THE ESCAPE IS CLOSED WITH NO CAVEAT LEFT,**
> ## **AND THE INSTRUMENT THAT COULD HAVE OVERTURNED IT WAS BUILT FIRST.**
> Six unrelated corpora -- anatomy, chemistry, psychology, biology, Sherlock Holmes, Little Women --
> read corpus-by-corpus vs round-robin vs shuffled. Same sentences, order is the only variable
> (asserted as a permutation, not assumed).
>
> **🔬 FIRST THE MANIPULATION CHECK FAILED, AND THE HONEST DIAGNOSIS WAS THE INSTRUMENT.** The
> context-vector drift metric read **1.08x** across six unrelated corpora -- NARROWER than reordering
> one wikipedia dump (1.12x). That is a metric hitting its floor, not a statement about the orderings:
> a word's contexts vary so much sentence to sentence that two half-means differ by ~0.75 even when
> nothing systematic changed. **⛔ THE BARRED MOVE WAS TO LOWER THE 1.15x GATE. I DID NOT.** I built a
> metric that measures regime change directly -- the total-variation distance between the CORPUS MIX
> of a word's first-half and second-half occurrences -- validated it on known-answer orderings
> (perfectly blocked **1.000**, perfectly interleaved **0.000**), and applied **THE ORIGINAL,
> UNCHANGED 1.15x GATE** to it.
>
> | | new metric (regime change) | old metric (context drift) |
> |---|---|---|
> | BLOCKED_BY_CORPUS | **0.6585** | 0.7901 |
> | ROUND_ROBIN | 0.3557 | 0.7885 |
> | SHUFFLED | **0.2695** | 0.7283 |
> | **band** | **2.44x -- PASSES** | 1.08x -- fails |
>
> **➡️ AND THE ARMS STILL SAY NO. corr(regime change, penalty for forgetting) = +0.123 across 9
> cells; the escape needs clearly NEGATIVE. A delta arm beats the sum in 2 of 18 cells.** At 12,000
> sentences the blocked ordering's delta arm blows out to **12.84x** against the sum's **5.71x**.
> **✅ FREE HARNESS CHECK PASSED AGAIN: SUM is order-invariant and read identical across all three
> orderings at all three points** -- asserted this time, not merely printed.
> *⚠️ HONEST WRINKLE: the penalty is NOT perfectly monotonic -- ROUND_ROBIN (2.292) sits BELOW
> SHUFFLED (2.752). The direction is flat-to-positive, not cleanly rising. That is enough to refute
> "penalty falls as drift rises"; it is not itself a clean positive trend, and I am not claiming one.*
> **🧠 FIDELITY NOTE: this does NOT say the brain lacks recency -- it plainly has it. It says recency
> applied to OUR accumulator, on THIS retrieval task, costs rather than pays. Fifth POSITION error of
> the same family: right mechanism, wrong place.**
>
> ## ⬅️⬅️ TOP ITEM NOW -- **OWNER INSTRUCTION 2026-08-20T01:31Z, AND IT CUTS AGAINST MY OWN CLOSURE:**
> > *"adjusting a belief sounds like an important capability for substrate - so let's keep that
> > finding and integrate where it needs to go"*
>
> **I WAS ABOUT TO WRITE "I STOP PROPOSING WRITE RULES" AND LEAVE IT THERE. THAT WOULD HAVE THROWN
> AWAY A CAPABILITY BECAUSE IT LOST ONE BENCHMARK.** The owner is drawing a distinction I had
> collapsed: *the delta rule as a REPLACEMENT FOR THE SUM* lost, robustly and now under genuine
> regime change. **That is a claim about a DEFAULT WRITE RULE on a cloze-retrieval task. It is NOT a
> claim about whether the substrate should be able to REVISE A BELIEF IT HOLDS.** Our profiles can
> only ever be diluted by later evidence -- a wrong early impression is never CORRECTED, only
> outvoted. Nothing in the six failed interventions tested revision, because the benchmark never
> contradicts anything.
>
> **🔎 AND THE ARCHIVE SAYS THE CAPABILITY IS ALREADY BUILT AND SITTING UNWIRED -- five landed
> HARD_PASS cells, none of them in `capability_registry.jsonl`:**
> `exp_lap2_2_belief_revision_cpu_v1` (HARD_PASS) · `exp_lap4_9_agm_contraction_depth_cpu_v1`
> (HARD_PASS -- AGM contraction, the formal theory of giving up a belief) ·
> `exp_cheap1_contradiction_detect_cpu_v1` (HARD_PASS) · `exp_a3_rollback_via_subtraction_v1`
> (HARD_PASS) · `exp_pp52_exact_rollback_n4096/n16384_v1` (HARD_PASS) ·
> `exp_pb_pinv_downdate_forgetting_v1` (HARD_PASS).
> **That is exactly the WIRE-DON'T-ISLAND failure mode: proven capability, no organ, no consumer.**
> ➡️ NEXT ACTIONS: verify these on disk, find the real integration point (contradiction detection ->
> revision, not accumulation), and register what is genuinely wired. **Report honestly if the
> HARD_PASS cells turn out to be synthetic-only** -- several this session did.
>
> ## ✅ RAN -- **THE TESTING EFFECT DOES NOT REPRODUCE. EIGHTH CONFIRMATION THAT ONLY VOLUME MOVES**
> ## **THIS, NOW EXTENDED FROM THE WRITE RULE TO THE WRITE *MOMENT*.**
> 6,000 read / 6,000 practice, final test on 300 never-read never-practised items, 288 candidates.
>
> | arm | median | vs COOC | 95% CI |
> |---|---|---|---|
> | BASELINE (no practice) | 97.5 | 3.75x | [87.0, 124.0] |
> | **STUDY (read it again)** | **75.5** | **2.90x** | [60.0, 86.0] |
> | TEST (retrieve, success-weighted) | 89.0 | 3.42x | [74.0, 109.5] |
> | TEST_SH (success borrowed from another item) | 80.0 | 3.08x | [67.0, 99.0] |
>
> **✅ THE EXPERIMENT HAD POWER, WHICH IS WHAT MAKES THE NULL READABLE.** Paired on the same items:
> **STUDY - BASE = -5.0, CI [-8.5, -2.0] SEPARATED**, and TEST - BASE = -2.0, CI [-4.0, -1.0]
> SEPARATED. *Practice genuinely helps. This is not the underpowered non-result the two smokes were.*
> **⛔ AND TEST TIES ITS OWN SHUFFLED-SUCCESS CONTROL: TEST - TEST_SH = +0.0, CI [-2.0, +0.5].**
> Which item was successfully retrieved carries **nothing**. TEST is a scaled-down STUDY.
> **⛔ TEST DOES NOT BEAT STUDY EITHER (+2.0, CI [+0.0, +3.0]) -- if anything it is worse.** At
> matched total input, concentrating that input on well-retrieved items is not better than spreading
> it evenly.
>
> **➡️ SO THE EIGHTH INDEPENDENT TEST AGREES WITH THE SEVEN BEFORE IT: HOW MANY, NOT WHICH.** The
> difference is that the seven acted on the write RULE and this one acted on the write MOMENT -- the
> one position never touched. **Retrieval-as-encoding buys nothing here. The pre-committed broader
> closure fires: the representation is insensitive to the write moment as well as the write rule.**
>
> **⚠️⚠️ THE LIMITATION, AND IT IS THE FAILURE MODE I WROTE INTO CLAUDE.md AN HOUR EARLIER:
> `added/base = 1.0301`.** The practice phase added slightly MORE than the entire reading phase, so
> this is not "practice modifying a memory" -- it is **a second, equal-sized reading phase whose
> input was redistributed.** That is still a fair test of *redistribution by retrieval success*, and
> the shuffled control makes the redistribution answer clean. **It is NOT a clean test of the human
> testing effect**, which is defined by what survives a DELAY. *Nothing in this substrate decays, so
> there is no retention interval for a testing effect to act on -- and that, not the arms, is the
> honest reason this task cannot express it.*
> **🧠 FIDELITY, STATED PLAINLY: the brain result is real and this is not evidence against it.** We
> tested the mechanism in a system with no forgetting, scored immediately. Expressing the effect
> would require decay between practice and test, which we do not have and have never built.
>
> ## [DONE -- SEE ABOVE] **THE SMOKE CAUGHT A CONFOUND THAT WOULD**
> ## **HAVE MADE IT THE EIGHTH "VOLUME MATTERS" RESULT IN DISGUISE.**
> Design is the real testing-effect design, because no other design can see the effect: read, then a
> PRACTICE phase, then a final test on a THIRD disjoint slice. Arms differ only in what a practice
> episode IS -- `BASELINE` (none) · `STUDY` (read it again) · `TEST` (retrieve it, update by success)
> · `TEST_SH` (same, success value borrowed from another item -- the control that decides it).
>
> **⛔ THE CONFOUND THE SMOKE EXPOSED.** Raw retrieval success on this substrate averages **0.0739**,
> so a success-scaled TEST arm added **eleven times less input than STUDY** (measured: 0.1062 vs
> 1.1622 mean added magnitude per term). **Volume is one of only two levers that has ever moved this
> metric.** Running that would have re-confirmed "volume matters" for the eighth time while wearing a
> retrieval label. **FIXED by normalising success weights to mean 1.0, so TOTAL input is equal and
> the only difference is how it is DISTRIBUTED** -- concentrated on well-retrieved items, or spread
> evenly. *That is the question the testing effect actually poses.* **A hard gate now refuses to
> report if the TEST/STUDY input ratio leaves 0.75-1.33** (currently 1.237).
> *⚠️ And the first smoke was correctly refused by its own power guard: at 1,500 read / 600 practice
> only 174 updates landed across 74 candidates, every paired difference was EXACTLY 0.0, and the
> script reported "underpowered, no arm comparison reportable" rather than a null. Practice must be a
> real fraction of total exposure -- now running at parity, 6,000 read / 6,000 practice.*
>
> ## 📌 THE CASE FOR IT (unchanged) -- **RETRIEVAL IS READ-ONLY HERE AND IS**
> ## **NOT READ-ONLY IN THE BRAIN. THIS IS THE ONE POSITION WE HAVE NEVER INTERVENED AT.**
> *Brain-first, and it is the mechanism the owner's "adjusting a belief" actually names.*
>
> **ORGAN_MAP ALREADY CARRIES IT, ALREADY CAVEATED** (its own words): the win is *"scoped to TEST-type
> practice (retrieval attempts)"*, **PINNED as a real 1978 effect** (Landauer & Bjork) for test-type
> practice at short delay, **and UNPINNED as a general optimum** -- Karpicke & Roediger 2007 and
> Storm, Bjork & Storm 2010 find equal-interval spacing matches or beats expanding at long retention.
> *"Do not build 'expanding, doubling' in as a fixed law."* **So the PINNED part is that RETRIEVING
> CHANGES THE TRACE; the schedule is not pinned and must not be imported.**
>
> **🔎 ENUMERATED ABSENCE, AND THE CONTRAST IS THE POINT:**
>
> | | archived cells |
> |---|---|
> | `replay` (OFFLINE reactivation) | **211 hits, 163 landed** |
> | `retrieval practice` | **0** |
> | `testing effect` | **0** |
> | `retrieval-induced` | **0** |
> | `reconsolid*` | **0** |
>
> **WE BUILT OFFLINE REACTIVATION EXHAUSTIVELY AND ONLINE RETRIEVAL-MODIFICATION NOT AT ALL.** Those
> are different mechanisms in different structures, and only one of them is in the substrate.
>
> **🔑 WHY THIS IS NOT A SEVENTH WRITE-RULE RETRY.** All six closed routes intervened at READING time
> -- which traces to keep, how to combine them, what step size to take. **Retrieval-modifies-memory
> acts at a moment we have never touched: our `profile()` and every recall path are strictly
> read-only.** *That is a genuinely new POSITION, not a new parameter in the old one.*
> *⚠️ AND THE PRE-COMMITMENT MUST SAY WHAT WOULD KILL IT: if a retrieval-modification arm behaves
> like the other six -- no slope change, no concentration -- then the representation is insensitive to
> the write moment as well as the write rule, and that is a broader and more useful closure than any
> of the six.*
>
> ## 🧠🚨 **OWNER 2026-08-20T12:31Z -- A DATED PRE-REG AMENDMENT, FILED BEFORE ANY ARM IS SCORED.**
> > *"When I read either of those, I read them in a very different way. You don't approach a
> > textbook like a story - textbooks are supposed to have facts laid out for learning, stories are
> > there to enjoy - to get a new perspective or imagine a different life or world. Yes, you can
> > learn from stories, but it's not the same kind of learning at all."*
>
> **THIS BREAKS MY PRE-REGISTERED DISCRIMINATOR, AND IT BREAKS IT CORRECTLY.** I had written:
> *"structure must help NARRATIVE MORE THAN EXPOSITION, or it is a better encoder rather than a
> fidelity fix."* **That test assumes narrative SHOULD yield the same kind of knowledge as a
> textbook, and the owner is pointing out that it should not.**
>
> **⛔ AND IT REFRAMES TONIGHT'S "BIGGEST NEWLY-VISIBLE GAP" AS POSSIBLY NOT A GAP AT ALL.** I
> recorded: *grounding rate textbook 12.6% vs Sherlock 0.7%, and children learn from narrative, so
> this is a fidelity failure.* **The missing step: OUR TASK IS A FACT-RECALL TASK** -- predict the
> missing word from its context, scored against co-occurrence floors. **That is EXPOSITORY-KIND
> knowledge.** Measuring what a novel taught us with a metric built for what a textbook taught us is
> a **METRIC infidelity** -- the third axis of SHAPE / POSITION / METRIC, and the one I have been
> cataloguing all night without applying it here.
> *So "narrative does not ground" may not be a failure of the LEARNER. It may be that we asked a
> novel to deliver textbook knowledge and scored it when it did not.*
>
> **📌 AMENDED DISCRIMINATOR (dated 2026-08-20, filed BEFORE any structural arm is scored; the
> superseded version is retained above verbatim, per this project's own precedent in ORGAN_MAP §3):**
> **On the CURRENT fact-recall task, structure is judged on EXPOSITORY prose, where that task is a
> fair measure of what the text was there to teach.** Narrative is reported as a SEPARATE
> observation, NOT as the pass/fail criterion. **A structural encoder that helps exposition and not
> narrative is NOT thereby disqualified.**
> **➡️ AND THE REAL QUESTION THE OWNER'S NOTE OPENS IS BIGGER THAN THE ENCODER: WE HAVE NO MEASURE OF
> NARRATIVE-KIND LEARNING AT ALL.** *Perspective, a situation model, what a character wanted --
> nothing in the instrument scores any of it. Until such a measure exists, EVERY claim about this
> substrate failing on narrative is unfalsifiable, including the one I made tonight with a table and
> four decimal places.*

> ## 🟢 **STRUCTURAL ENCODER IS USABLE -- AND I BRIEFLY CLAIMED THE OPPOSITE. RETRACTED HERE.**
> Reachability check before building anything. **First result: `structural_vector_masked` returned an
> ALL-ZERO vector (norm 0.000) against the bag's 32.680**, and I wrote that up as a reachability
> failure -- *"the encoder exists but returns no signal."* **THAT WAS WRONG.**
>
> **THE POSITIVE CONTROL CAUGHT IT: I passed the target `"mitochondria"`, and `content_lemmas`
> produces `"mitochondrion"`.** The target was never found in the parse, so the vector was empty --
> **my bug, in my test, not the encoder's.** With correctly-lemmatised targets it produces real
> vectors on every sentence tried:
>
>     "The dog chased the cat down the street."      cat 27.857 · chased 27.857 · dog 26.683
>     "Water freezes at zero degrees."               degree 25.768 · freeze 22.450 · water 24.249
>     "The mitochondria produce energy for the cell." cell 32.924 · energy 32.062 · mitochondrion 25.768
>
> Norms 22-33, comparable to the bag's 32.68. Its three front-end assets are present in
> `data/frontend_assets/` (hashed arc parser, arc labeler, UPOS tagger).
>
> **🔑 THIS IS EXACTLY THE FAULT THE SESSION ALREADY WROTE A RULE ABOUT, ARRIVING FROM THE OTHER
> SIDE.** CLAUDE.md now says *"an empty representation scores PERFECTLY on a rank metric"* -- had I
> built arms on that all-zero vector, they would have scored median rank 1.0 and looked like a
> breakthrough. **Instead the emptiness appeared in a REACHABILITY probe, where I misread it as a
> property of the code rather than of my own call.** *An absence check inherits every bug in the
> thing making the check -- which is why the standing rule is to verify with a POSITIVE control, and
> it is the only reason this was caught within one command.*
> **➡️ SO THE PATH IS CLEAR ON BOTH COUNTS: no prior work forbids it, and the organ genuinely works.
> The next step is the measurement, unstarted.** *And a practical note for whoever runs it: targets
> must be passed as LEMMAS (`content_lemmas` output), not surface forms -- a mismatch fails SILENTLY
> as a zero vector rather than raising.*

> ## ✅ **THREE-READ CHECK ON THE STRUCTURAL ENCODER: CLEAR. THIS IS THE NEXT THING TO TEST.**
> *Step 1 of the sequence I wrote when the owner asked for the next expansion. Done before touching
> anything, because the encoder being BUILT AND SWITCHED OFF is itself evidence someone may have had
> a reason.*
>
> | read | result |
> |---|---|
> | `experiment_index.py` -- structural encoder / structural_vector / role-bound | **1 hit, 0 LANDED.** Built, never produced a result. No prior negative to rediscover. |
> | ORGAN_MAP §3 CORRECTIONS | **no mention of structural or role encoding.** Not a re-proposal of anything already ruled out. |
> | `capability_registry.jsonl` | 50 keyword hits, all broad false positives (`superposition`, `catastrophic_forgetting`, ...). **No row claims this capability.** |
>
> *⚠️ ONE SCARE INVESTIGATED AND CLEARED: `exp_wave14r_erase_orthkeys_v1` carries the verdict
> `STRUCT_KEYS_FIX_MIRAGE`, which reads like a direct warning about structured codes. **It is not** --
> disk-verified, it concerns GDPR-style surgical ERASE under orthogonal Hadamard keys, and the
> "mirage" is a paraphrase-probe artifact in erasure. Unrelated to encoding context structurally.
> Recorded because the NAME alone would deter the next person who greps for it.*
>
> **➡️ SO THE PATH IS CLEAR AND THE CASE IS NOW FOUR-FOLD.** Four independent routes reached the same
> place tonight: the bag-of-nearby-words CONTEXT UNIT is the limit. (1) exposition grounds 12.6% and
> narrative 0.7%, and it is NOT exposure; (2) eight write-rule closures all argued about which bags to
> add, never about the bag; (3) surprise reads 0.42 against a 0.5 no-information floor because it is
> an error against a MEAN, not a prediction; (4) the one pinned predictive organ (D7/SR) fails on
> reading because sequence is the wrong structure -- **syntax chooses the next word, not a transition
> policy.**
> **NEXT, AND UNSTARTED: turn on `StructuralEncoder` additive/default-off, measure on the same task,
> same floors, BOTH genres. PRE-REGISTERED DISCRIMINATOR STANDS: it must help NARRATIVE MORE THAN
> EXPOSITION** -- exposition's bag already carries the definition, so it has less to gain. *If it
> helps both equally it is a better ENCODER, not a fidelity fix, and must be reported as that.*

> ## 🛑 **LINK ONE BREAKS -- AT EXACTLY THE POINT FLAGGED IN ADVANCE. THE CHAIN STOPS HERE.**
> *The previous block laid out: wire D7 -> real predictor -> real prediction error -> then the
> owner's idea becomes testable. It named the SR-over-reading mapping as OUR invention and the link
> most likely to fail, and said to test the predictor BEFORE building on its residual. **Tested. It
> failed.***
>
> | arm | median rank of the true next lemma (vocab 500) |
> |---|---|
> | **ONE_STEP** -- plain 1-step co-occurrence `P` | **18.5** |
> | **SR** -- `M = (I - 0.7P)^-1` | **45.0** |
> | FREQUENCY -- cue-blind floor | 121.5 |
> | UNIFORM | ~250 |
>
> **SR beats the cue-blind floor (-40.0, CI [-43.0,-37.0]) -- but PLAIN CO-OCCURRENCE BEATS SR by
> +25.5, CI [+21.0,+29.0], SEPARATED.** *The discounted multi-step structure does not merely fail to
> add; it actively DESTROYS predictive power that one-step counting already had.*
>
> **🧠 FIDELITY READ, AND THE DISTINCTION IS THE WHOLE POINT: D7 IS NOT AT FAULT.** Its self-test
> recovers the true successor on a deterministic chain, and its math is the pinned closed form. **SR
> is pinned for STATE TRANSITIONS IN NAVIGATION** (Dayan 1993; Stachenfeld 2017 -- grid cells as
> eigenvectors of `M`). **Reading is not a Markov walk over states in that sense: the "next lemma"
> is chosen by syntax and topic, not by a transition policy over a state space.** *We mapped a
> navigation organ onto text because both look like sequences. That mapping was OUR invention, it
> was labelled as such in advance, and it does not transfer.*
> **➡️ SO: DO NOT WIRE D7 INTO THE READING PATH. The organ stays correct, stays registered, and stays
> uncalled -- and now for a MEASURED reason rather than an oversight.** *And the owner's
> "note only what is new" idea remains blocked: we still have no real predictor, and the one candidate
> that looked pinned turns out to be pinned for a different problem.*
>
> *⚠️ LIMITATION, CAUGHT ON READING THE OUTPUT: the three "seeds" returned IDENTICAL numbers
> (45.0/18.5/121.5) because the corpus handle yields the same sentences each time -- only the UNIFORM
> arm is seeded. **This is ONE text sample with bootstrapped CIs over 408 held-out pairs, NOT three
> independent replications.** The margin is large and the CIs are over pairs, so the direction is
> safe; the word "seeds" in that script is wrong and must not be quoted as replication.*

> ## 🧩🧩 **THE THREADS CONVERGE. THE OWNER'S IDEA IS NOT DEAD -- IT IS BLOCKED BY A BROKEN**
> ## **INSTRUMENT, AND THE ORGAN THAT WOULD FIX THE INSTRUMENT IS ALREADY BUILT AND UNCALLED.**
> *Written because three separate findings tonight turn out to be one finding, and that is only
> visible from the end.*
>
> **1. THE OWNER'S HYPOTHESIS FAILED FOR A REASON THAT IS NOT ABOUT THE HYPOTHESIS.** Surprise did
> not select useful notes -- but our surprise reads **0.4252 / 0.4214 / 0.4206 against a
> no-information value of 0.5.** *You cannot gate on a signal that is 4% from chance.* The idea was
> never given a working instrument.
>
> **2. WHY THE INSTRUMENT IS BROKEN, AND IT IS A POSITION ERROR AGAIN.** Our "surprise" is
> `1 - cos(new context, ACCUMULATED AVERAGE)` -- **an error against a MEAN, not against a
> PREDICTION.** ORGAN_MAP G2 pins prediction error as `x - x_hat`, where `x_hat` is what a
> generative model PREDICTED. **A running average of bags predicts almost nothing, so its residual is
> almost pure noise -- by construction, not by accident.** *Eight closed routes all tried to USE that
> residual better. None asked whether it was a prediction error at all.*
>
> **3. THE ORGAN THAT MAKES A REAL PREDICTION IS D7, AND IT IS BUILT, FAITHFUL, AND NEVER CALLED.**
> A successor representation IS a predictive map -- `M = (I - gamma*P)^-1`, expected DISCOUNTED FUTURE
> occupancy. It predicts what should come next. **Surprise measured against an SR prediction is an
> actual prediction error; surprise measured against a bag-average is not.**
> *`hdlab/successor_representation.py` implements the closed form AND the TD variant, its math is
> FULLY PINNED, and no `hdlab` module imports it.*
>
> **➡️ SO THE CHAIN IS: wire D7 -> get a real predictor -> get a real prediction error -> AND ONLY
> THEN is the owner's "note only what is new" idea testable at all.** *Every step is brain-pinned,
> and the expensive step is already done.*
> *⚠️ HONEST RISK, RECORDED FIRST: this is a four-link chain and each link can break. D7 being
> faithful does not mean SR over READING ORDER is meaningful -- SR is pinned for state transitions in
> navigation, and sentences are not a Markov chain over states in the same sense. **That mapping is
> OUR invention, not the pinned part**, and it is the link most likely to fail. Test the predictor's
> accuracy BEFORE building anything on its residual.*

> ## ❌ **OWNER Q74 ANSWERED: SURPRISE DOES NOT SELECT THE USEFUL NOTES. IT IS VOLUME.**
> *The owner: "We shouldn't need notes every single time - only when there's something NEW... I still
> think it's the surprise measurement."* **Tested in the ONE population never selected over -- the
> POST-GROUNDING notes, which did not exist before tonight's fix. The answer is no.**
> 3 seeds, 16,000 sentences, halves COUNT-MATCHED so volume cannot explain a difference:
>
> | comparison | diff | 95% CI | |
> |---|---|---|---|
> | ALL - NONE | **-8.0** | [-11.0, -5.0] | **SEPARATED** -- the fix reproduces |
> | HIGH_SURP - RANDOM_HALF | +0.0 | [+0.0, +1.0] | not separated |
> | LOW_SURP - RANDOM_HALF | +0.0 | [+0.0, +1.0] | not separated |
> | HIGH_SURP - ALL | +1.0 | [+0.0, +2.0] | not separated |
>
> **⚠️ AND SEED 7 ALONE WOULD HAVE TOLD A COMPELLING STORY IN THE WRONG DIRECTION.** Per-seed:
> `LOW_SURP` 73.5 / 92.0 / 90.5 and `HIGH_SURP` 83.0 / 74.0 / 69.5 -- **the two arms swap places
> between seeds.** On seed 7 the least-surprising half beat everything including ALL at double the
> count; on seeds 101 and 20260819 it was the worst arm. *Reporting seed 7 would have produced a
> striking, quotable, entirely false finding -- "confirmation beats novelty". Three seeds is why it
> did not happen.*
>
> **🧠 FIDELITY READ (the owner's standing requirement -- a negative without one is not closed).**
> This negative is **BRAIN-CONSISTENT, and it is the SECOND confirmation tonight of the same pinned
> fact.** ORGAN_MAP B1': *LATL conceptual combination is approximately **ADDITIVE** (Baron & Osherson
> 2011).* **An additive hub has no notion of a special instance -- every contribution just adds.
> "Every note contributes a little and none is special" is precisely what additive combination
> predicts.** *Same pinned fact that reframed "the sum beats any single encounter" an hour ago. Two
> independent negatives, one brain property, both consistent.*
> **🔑 AND WHY SURPRISE COULD NOT SELECT, MEASURED NOT ASSUMED: mean surprise across seeds is
> 0.4252 / 0.4214 / 0.4206 -- against 0.5, which is the NO-INFORMATION value for unrelated vectors.**
> Our surprise signal sits a few percent from chance, so there was almost nothing in it to select on.
> *That was measured independently earlier tonight and it predicted this result.*
> **➡️ SO THE HONEST ANSWER TO "WHY IS IT SCORING BETTER": MORE EVIDENCE, EVENLY. Not novelty, not
> confirmation, not any subset -- volume, in a hub that adds.**

> ## 🧠 **OWNER 2026-08-20T12:06Z: "drilling and evaluating deeply the brain foundationality of any**
> ## **negatives" -- AUDITED, NOT ASSERTED. 6 OF 8 HAD ONE. THE 2 GAPS ARE NOW FILLED BELOW.**
> *Same request as 2026-08-19T20:23Z, when the honest answer was 1 of 6. Auditing the same way.*
>
> | negative (this session) | brain-fidelity check at the time? |
> |---|---|
> | divisive normalisation inert | **FULL** -- ORGAN_MAP §3 gave an ANALYTIC reason (pool denominator is a scalar; cosine is scalar-invariant) |
> | testing effect did not reproduce | **FULL** -- METRIC/regime mismatch named: the effect is defined by what survives a DELAY and nothing here decays |
> | delta rule under drift closed | **FULL** -- named as the 5th POSITION error; explicitly NOT a claim the brain lacks recency |
> | cross-situational: do not build | **FULL** -- PBV (Medina/Trueswell) vs Yu & Smith identified as competing accounts, then the premise measured false |
> | D8 cascade synapse ruled out | **FULL** -- checked against pinned Fusi/Benna-Fusi math; problem shown not to exist here |
> | narrative does not ground | **FULL** -- children acquire most vocabulary in exactly that regime |
> | **gap detector contributes nothing** | **PARTIAL** -- called a POSITION result, but I never asked what the brain's novelty gate DOES |
> | **one encounter vs the sum** | **NONE** -- closed purely on the task metric; no fidelity read at all |
>
> **⛔ SO 6 OF 8, NOT 8 OF 8. The two weakest are filled here rather than claimed.**
>
> **FILLING GAP 1 -- "the sum beats any single encounter" (+13.0, CI [+6.0,+17.5]).** This is the
> exemplar-vs-prototype question, and **ORGAN_MAP already PINS the answer: B1' "LATL conceptual
> combination is approximately ADDITIVE (Baron & Osherson 2011)."** *Our result is CONSISTENT with a
> pinned brain fact -- aggregation beating any instance is what an additive hub predicts.* **That
> reframes it from "a lead died" to "a pinned brain property was confirmed on our instrument", which
> is the first positive fidelity result of the session and I had not noticed it.**
> *⚠️ Scope: additive COMBINATION is pinned; it does not license our particular sum (raw, unweighted,
> unnormalised). Consistency is not identity.*
>
> **FILLING GAP 2 -- the gap detector discriminates nothing on the live path.** The brain's analogue
> is **H1 perirhinal familiarity** -- *"do I already know this?"* -- and ORGAN_MAP lists H1 as BUILT
> with its module on disk. **The fidelity read: in the brain, familiarity is a GRADED signal consumed
> at retrieval; ours is a BINARY gate consumed at intake, and positioned after two filters that
> already removed every word it would reject.** *POSITION again -- the same family as the other five.
> Not a broken organ: an organ asked a question whose answer is already determined.*
>
> *➡️ STANDING: a negative without a fidelity read is not closed, it is only unexplained. Both gaps
> above existed because the task metric gave a clean answer and I stopped there.*

> ## 🎯 **THE GAP THE DIRECTIVE ACTUALLY FOUND: D7 IS BUILT TO THE BRAIN'S CLOSED FORM AND THE**
> ## **SUBSTRATE NEVER CALLS IT. FOURTH "BUILT, CORRECT, NEVER REACHED" OF THE SESSION.**
> After correcting the stale label, the obvious follow-up was whether the built organ MATCHES its
> pinned math -- *a module existing is not the same as a module being faithful.* **It does.**
> `hdlab/successor_representation.py` (435 lines) exposes `successor_matrix` (the closed form) AND
> `successor_matrix_td`, with 71 references to the discount factor, a matrix inverse, and eigenvector
> code for the grid-cell claim. Its own docstring: *"D7. THE ONE SLOT WHERE THE BRAIN HANDS US A
> CLOSED FORM."* **This is one of the most faithfully-built organs in the substrate.**
>
> **AND NOTHING IN `hdlab/` IMPORTS IT.** Enumerated over `hdlab/` and `experiments/`: every importer
> is an EXPERIMENT cell (6 on disk). **No substrate module calls it, and its own registry row says
> `WIRED_BUT_NOT_PIPELINE_REACHABLE`.**
> **🔁 FOURTH INSTANCE TONIGHT OF THE SAME SHAPE** -- after the write-only consolidated store, the
> unwired gap organs, and post-grounding traces that were written and never read. *The registry
> answers "does it exist"; nothing answers "is it REACHED".*
>
> **➡️ SO THE GAP IS NOT "BUILD D7". IT IS "THE SUBSTRATE DOES NOT USE THE ONE ORGAN WHERE THE BRAIN
> HANDED US A CLOSED FORM."** *And that lands exactly on the next expansion named below: a successor
> representation is a PREDICTIVE, multi-step relational map -- a brain-pinned alternative to the
> bag-of-nearby-words context unit. The organ that could replace the bag is already written, already
> faithful, and never called.*
> *⚠️ TWO REGISTRY DEFECTS FOUND IN PASSING, NOT YET FIXED: its `used_by` lists 2 files where disk
> shows 6, and its `narrowing` is `None` -- no limits recorded at all, which by tonight's standard is
> itself a gap. **Do not read a `narrowing: None` row as "no known limits"; read it as "nobody wrote
> them down".***

> ## 🧭 **OWNER Q75 ANSWERED -- A STANDING DIRECTIVE, AND THE FIRST THING IT FOUND IS THAT THE**
> ## **GAP LIST ITSELF IS STALE.**
> *Owner: "When you get to a point where you're spinning your wheels you should take a deep look at
> brain foundationality and see where you can shift focus to fill in gaps."* **Not "stop" -- a rule
> for what to do WHEN stuck. Applied immediately.**
>
> ORGAN_MAP marks 5 of 46 organ headings MISSING. **Checked against disk and the registry, 2 of the 5
> are NOT missing:**
>
> | organ | ORGAN_MAP says | actually on disk |
> |---|---|---|
> | **D7** successor representation | *MISSING, math FULLY PINNED* | **`hdlab/successor_representation.py` EXISTS** + registry row `successor_representation_d7_v1` |
> | **H2** information foraging | *MISSING -- and it is step 1* | **`hdlab/information_foraging.py` EXISTS**, registry row `information_foraging_mvt_leave_rule`, and `Substrate` BUILDS it |
> | D8 cascade synapse | MISSING, math FULLY PINNED | genuinely absent (0 registry rows) -- **and RULED OUT on evidence tonight**: no memory-lifetime problem to solve |
> | F5 coherence monitor (N400) | MISSING, PHASE-B target | no `coherence_gate.py`; 21 registry rows mention "coherence" -- **needs a real check, not a keyword match** |
> | F6 construction-integration | MISSING | 24 registry rows mention "construction" -- same caveat |
>
> **🔑 SO THE FIRST GAP TO FILL IS THE GAP LIST.** *A stale MISSING label is worse than no label: it
> sends you to build something that exists, which is the rediscovery failure this session already hit
> six times through a different door.* **And the two false MISSINGs are both organs I might plausibly
> have proposed building next -- D7 in particular, since a successor representation is a
> brain-pinned alternative to the bag-of-words context unit named as the next expansion below.**
> *⚠️ F5/F6 are NOT yet cleared either way: "coherence" and "construction" are common words and 21/24
> keyword hits are not evidence of the organ. They need the same disk check D7 and H2 just got.*
> **➡️ ACTION: audit all 46 organ status labels against disk + registry, fix ORGAN_MAP in place, and
> only then choose a gap to fill.** *That is the owner's directive executed in the right order.*

> ## ⬅️⬅️⬅️ **NEXT EXPANSION (owner asked 2026-08-20): THE UNIT, NOT THE MECHANISM.**
> ## **OUR "CONTEXT" IS A BAG OF NEARBY WORDS. THE BRAIN ENCODES WHO DID WHAT TO WHOM.**
> `context_vector_masked` sums the content words around a target -- a FIRST-ORDER, SYNTAGMATIC
> statistic. **Every wall hit this session is downstream of that one choice.**
>
> | measurement | what the BAG explains |
> |---|---|
> | textbook grounds **12.6%**, novels **0.7%** | *"mitochondria are organelles that produce ATP"* -- the bag nearly IS the definition. *"he stumbled through the gorse"* -- the bag is useless; the **frame** says physical, traversable, outdoors |
> | coherence **0.027** narrative / 0.071 expository, both near zero | two scenes share almost no WORDS -- they share ROLE FRAMES |
> | pooling scores **0.75-0.80x** of a single encounter | averaging bags of different scenes converges to the corpus mean; averaging ROLE SLOTS would accumulate |
> | **eight** write-rule closures | every one chose WHICH bags to add or HOW. **None questioned the bag.** |
>
> **🧠 IT IS PINNED, NOT INVENTED.** ORGAN_MAP F3: MacWhinney Competition Model, cue validity =
> availability x reliability -- and its own FIDELITY line already says **"RIGHT-OP-WRONG-METRIC: the
> competition shape is right; raw counts are not cue validity."**
> **🛠️ AND IT IS ALREADY BUILT, DEFAULT-OFF, IN EXACTLY THE SHAPE `keep_noting_grounded` HAD:**
> `StructuralEncoder` (`reading_grounding_loop.py:318`) and `structural_vector_masked` (:456), with
> `encoder=None` giving the byte-identical shipped path (:269 *"NOTHING BELOW RUNS unless a caller
> explicitly builds a StructuralEncoder"*). Plus `hdlab/thematic_role_labeler.py` and
> `hdlab/role_slot_summarizer.py`.
>
> **SEQUENCE -- DO NOT SKIP STEP 1:**
> 1. **THREE-READ prior-work check** (`experiment_index.py` on structural/role encoding · the
>    registry · **ORGAN_MAP's CORRECTIONS**). *That habit caught six rediscoveries tonight, including
>    one where ORGAN_MAP said in writing "do not re-propose this".* **The encoder being built and
>    OFF is itself evidence someone may already have a reason.**
> 2. Turn it on ADDITIVE + DEFAULT-OFF; measure on the same task, same COOC/FREQ floors, 3 seeds,
>    BOTH genres. **Never on a statistic the mechanism optimises.**
> 3. **PRE-REGISTERED DISCRIMINATOR: structure must help NARRATIVE MORE THAN EXPOSITORY prose** --
>    exposition's bag already carries the definition, so it has less to gain. **If it helps both
>    equally it is a better ENCODER, not a fidelity fix, and must be reported as that.**
>
> *⚠️ HONEST RISK: role-binding leans on VSA binding, which ORGAN_MAP records as UNPINNED in the
> brain -- our invention under test. So the CONTEXT UNIT is brain-pinned; the BINDING that implements
> it is not. Both statements travel together.*

> ## 🗂️ **REGISTRY COVERAGE CLOSED (2026-08-20). 204 -> 208 ROWS, AND THE AUDIT CAUGHT ME 3x.**
> **`keep_noting_grounded` had NO registry row** -- the one verified result of the night was shipped
> into `hdlab` and islanded. Registered, plus the three modules the audit listed as unregistered
> (`ca3_completer`, `cortical_recall`, `vsa_cleanup_memory`). **That flag is now clear.**
>
> **THE AUDIT REJECTED MY FIRST ATTEMPT THREE TIMES, ALL THREE LEGITIMATE:** an invented
> `fidelity_basis` value (allowed set is pinned / invention_under_test / unpinned_and_unstated); a
> `brain_structure` that read as a COGNITIVE-THEORY LABEL with no neural system beside it -- *this
> project's own standing rule, and the audit has a heuristic for exactly it*; and a `path` written as
> a string containing a list-repr, which the audit walked character by character (204 of 205 rows use
> a real list).
> **✅ AND ONE I CAUGHT MYSELF: `brain_fidelity_score` is left NULL, not fabricated.** It is a dict
> emitted by `tools/brain_fidelity_score.py`, which I did not run. **A dict written in its shape
> would have looked scored while being invented**; the prose assessment moved to `narrowing`.
>
> **EVERY NEW ROW SAYS IN ITS OWN TEXT THAT IT RECORDS EXISTENCE AND CONSUMERS ONLY, NOT RESULTS.**
> `cortical_recall`'s row carries its own negative verbatim (built to fix a real measured defect, and
> a cue-blind FREQUENCY floor still beat every cortical arm at k>=10 -- *do not quote as a win*).
> `vsa_cleanup_memory` has NO hdlab consumer, so it is marked SHELVE/ISLANDED **on purpose**, with a
> BRAIN-framed revival criterion rather than a performance one.
> *⚠️ ONE FLAG DELIBERATELY NOT TOUCHED: row 200 `dissociation_score_instrument` carries an invalid
> `fidelity_basis` of `not_applicable_measurement_instrument`. It is pre-existing and not mine, none
> of the three allowed values honestly fits a measurement instrument, and silently rewriting another
> row's brain-fidelity semantics to clear a report-only flag is worse than leaving it visible.*

> ## ✅ **LAST OPEN THREAD CLOSED: THE GAP DETECTOR IS CORRECT AND REDUNDANT. NOT BROKEN, NOT USELESS.**
> Positive control -- asked the organ about the populations the live path never lets it see:
>
> | population | `is_gap` | correct? |
> |---|---|---|
> | SEED-KNOWN (`more`, `for`, `all`, `her`) | **False 8/8** | yes -- correctly "not a gap" |
> | GROUNDED (`march`, `month`, `days`, `april`) | **False 8/8** | yes -- correctly "not a gap" |
> | PENDING (`fourth`, `gregorian`, `julian`) | **True 8/8** | yes -- correctly "a gap" |
>
> **THE ORGAN DISCRIMINATES PERFECTLY.** It answered True 8,053 times out of 8,053 on the live path
> for one reason: **it is only ever ASKED about PENDING words.** `state.known_seed` filters seed words
> at the top of the loop, and the terminal short-circuit filters GROUNDED ones -- **both populations
> it would reject are removed before it is consulted.** Its answer is predetermined by its POSITION.
>
> **🔑 SO THIS IS A POSITION RESULT, NOT A CAPABILITY ONE, AND IT FULLY EXPLAINS THE ABLATION.**
> `ablate=["gap_detector"]` changed nothing because the organ's output is never load-bearing here --
> replacing a correct answer that is already determined with a constant that happens to match it is a
> no-op by construction. *The false alarm I raised (and withdrew) is now closed with a mechanism
> rather than just a retraction.*
> **➡️ AND IT NAMES A CHEAP WIN THAT IS NOT A RESEARCH QUESTION: the organ runs 8,053 times per 1,500
> sentences to compute an answer two earlier filters already guarantee.** *Not proposing the removal
> -- it is a correctness guard for a state handed in without those filters, which its own docstring
> says. Recording that its COST is real and its CONTRIBUTION here is zero.*
>
> ## ❌ **CLOSED -- AND IT CORRECTS THE ROUND BEFORE IT. ACCUMULATION *HELPS* ON THE TASK.**
> Three seeds, `simplewiki`, 8,000 sentences, paired on identical probes:
>
> | comparison | difference | 95% CI | |
> |---|---|---|---|
> | BEST - SUM | **+7.0** | [+3.0, +12.0] | SEPARATED -- the best single trace is **WORSE** |
> | BEST - RANDOM_ONE | -1.0 | [-6.0, +1.0] | not separated -- **NO selection effect** |
> | RANDOM_ONE - SUM | **+13.0** | [+6.0, +17.5] | SEPARATED -- one trace is worse than the sum |
> | BEST_HALF - SUM | +0.0 | [+0.0, +1.0] | not separated -- half the traces tie ALL of them |
>
> **THE HINT WAS SELECTION BIAS, exactly as flagged when it was recorded.** A max over ~8 noisy
> samples looked like signal and was not. *Pre-registering that suspicion is what made this cheap to
> close instead of expensive to build on.*
>
> **🚨 AND IT FORCES A CORRECTION TO THE PREVIOUS BLOCK, WHICH I WROTE CONFIDENTLY.** I claimed
> *"ACCUMULATION IS THE PROBLEM, for a fourth independent time"* on the strength of pooling scoring a
> worse anchor MARGIN than a single trace. **On the TASK the opposite is true: the sum beats any
> single trace by a separated margin (+13.0).** The margin statistic and the ranking task disagree,
> **and the task is the one that matters.** *So "accumulation is the problem" is NOT supported by that
> evidence and the fourth count is withdrawn. Accumulation is what the read-out is BUILT on and it
> earns its place here.*
> **➡️ WHAT SURVIVES IS SMALLER AND REAL: `BEST_HALF` ties `SUM` exactly (+0.0, CI [+0.0, +1.0]).
> HALF the traces carry the whole benefit** -- so there is genuine redundancy in the pile, but
> removing it buys nothing either. *Not a lever; a fact about the data.*
> **🔑 THE STANDING LESSON, THIRD TIME TONIGHT: A STATISTIC THE MECHANISM OPTIMISES IS NOT AN
> OUTCOME. Margin, coherence and effective dimensionality have each now pointed somewhere the task
> metric did not follow.**
>
> ## [DONE -- SEE ABOVE] **ONE ENCOUNTER vs THE SUM OF ALL OF THEM.**
> Four arms, identical corpus/terms/probes/floors, differing only in what a word's profile IS:
> `SUM` (today) · `BEST` (the single highest-margin trace) · **`RANDOM_ONE` -- the control that
> decides it** · `BEST_HALF` (top half by margin -- cliff or gradient?).
>
> **⚠️ SCORED ON THE TASK, NOT ON THE MARGIN, AND THAT IS DELIBERATE.** The margin is the quantity
> `canonicalize` optimises, so selecting the max-margin trace and then reporting its margin would
> repeat exactly the circularity caught one round ago. **These arms are scored on the same held-out
> ranking task and the same COOC/FREQ floors as everything else this session.**
>
> **WHY `RANDOM_ONE` IS THE ARM THAT MATTERS: if `BEST` ties it, there is no selection effect and the
> result collapses to "one trace beats a sum" -- a claim about ACCUMULATION, not about choosing
> well.** *And if `BEST` does beat it, the lever is new: every selector tried this session (novelty,
> precision, residual gating) chose WHICH TRACES TO STORE. None chose WHICH ONE TO READ OUT.*
>
> ## 🔁 **MY OWN "DO NOT BUILD" EVIDENCE WAS CIRCULAR. RE-TESTED PROPERLY -- SAME ANSWER, REAL**
> ## **REASON, AND IT REJOINS THE SESSION'S MAIN THREAD.**
> **THE CIRCULARITY, caught before it was quoted anywhere:** the block below compares the anchor
> margin of GROUNDED words against ESCALATED ones. **But a word grounds BECAUSE a clear anchor won --
> the margin IS essentially the grounding criterion.** "Words that failed the margin test have low
> margins" is a restatement of the definition, not evidence. *I nearly closed a research direction on
> a tautology.*
>
> **THE NON-CIRCULAR TEST, which is also what cross-situational learning actually claims:** does
> pooling evidence ACROSS encounters beat a SINGLE encounter? Both sides are averages over the same
> escalated items, so no selection is involved:
>
> | corpus (ESCALATED only) | n | pooled margin | mean SINGLE-trace margin | pooled / single |
> |---|---|---|---|---|
> | `textbook_biology_2e` | 1,784 | 0.0412 | 0.0550 | **0.75x** |
> | `sherlock_holmes` | 2,417 | 0.0285 | 0.0359 | **0.80x** |
>
> **⛔ POOLING IS WORSE THAN A TYPICAL SINGLE ENCOUNTER, in both corpora.** Cross-situational
> accumulation would not merely find nothing -- **it would actively destroy signal that individual
> encounters already carry.** *That is a real, non-circular reason not to build it, and it is the
> opposite of what the literature argument predicted.*
>
> **🔑 AND IT REJOINS THE DOMINANT FINDING RATHER THAN OPENING A FRONT: summing many context vectors
> converges toward the corpus mean -- the "responds to everything" direction -- washing out
> word-specific structure. Same mechanism as the de-concentration measured earlier: ACCUMULATION IS
> THE PROBLEM, for a fourth independent time.**
> *⚠️ ONE NUMBER I AM NOT CLAIMING: the BEST single trace scores 0.1511 / 0.1136, 3-4x the pooled
> value. That is a MAX over ~8 noisy samples and is biased upward by selection; it needs a null before
> it means anything. The clean comparison is pooled vs MEAN-single, and that one is unbiased.*
>
> ## 🛑 **DO NOT BUILD THE PARALLEL-CANDIDATE ORGAN -- ORIGINAL (CIRCULAR) EVIDENCE, KEPT FOR RECORD**
> *The previous block argued -- from real literature -- that cross-situational learning (Yu & Smith
> 2007) is the right mechanism for varied contexts, and that our single-hypothesis PBV explains the
> narrative failure. **That argument was good and the premise underneath it is false.***
>
> **THE PREMISE, MADE CHECKABLE WITHOUT BUILDING ANYTHING:** if PBV abandons a word because it can
> only hold ONE guess, then pooling evidence ACROSS that word's traces should still show a clear
> winner. **Measured as the substrate itself measures it** -- pooled traces scored against the
> ConceptSpace anchors, top-1 minus top-2 margin, the exact quantity `canonicalize` decides on:
>
> | corpus | group | n | **margin** | traces/item |
> |---|---|---|---|---|
> | `textbook_biology_2e` | GROUNDED | 831 | **0.3517** | 13.66 |
> | `textbook_biology_2e` | ESCALATED | 1,784 | **0.0412** | 7.79 |
> | `textbook_biology_2e` | PENDING | 108 | 0.0358 | 5.03 |
> | `sherlock_holmes` | GROUNDED | 49 | **0.5520** | 11.61 |
> | `sherlock_holmes` | ESCALATED | 2,417 | **0.0285** | 7.53 |
> | `sherlock_holmes` | PENDING | 143 | 0.0346 | 4.78 |
>
> **Abandoned words carry 8.5x (textbook) to 19x (fiction) WEAKER pooled evidence than grounded
> ones.** *PBV did not discard recoverable structure. It gave up on words that genuinely have no
> winner, and pooling across encounters -- which is exactly what cross-situational tracking does --
> would find nothing there.*
> **✅ THE GROUNDED GROUP IS WHAT MAKES THIS READABLE: a margin means nothing in the abstract, but
> against the margins of words THIS substrate did ground, 0.0285 against 0.5520 is unambiguous.**
> *Note ESCALATED and PENDING sit at the SAME margin (~0.03-0.04) in both corpora -- the mechanism is
> not failing to reach these words, there is simply nothing to reach.*
>
> **🔑 SO THE HONEST CONCLUSION INVERTS THE ONE I WAS BUILDING TOWARD.** Narrative words are not
> victims of a too-strict single-hypothesis rule. **In this substrate's own representation they are
> genuinely undetermined** -- and the interesting question moves upstream, to why a bag-of-context
> vector extracts so little from narrative that 2,417 of 2,417 escalated words look identical to
> noise. *That is a REPRESENTATION question, and it rejoins the session's dominant finding rather
> than opening a new front.*
> **⚠️ AND THIS IS THE TRAP THE OWNER NAMED, AVOIDED BY ONE MEASUREMENT: I had literature, a
> mechanism, a named failure mode and a plausible story. Building it would have been "wiring an organ
> because I think it could help." The premise cost one cheap probe to check and was wrong.**
>
> ## ⚠️🚧 **THE OBVIOUS NEXT MOVE IS BARRED, AND NAMING THAT IS THE POINT OF THIS BLOCK.**
> Last round's finding -- *"our grounding threshold demands more consistency than narrative
> supplies"* -- has an obvious follow-up: **lower the threshold.** *That is the band-adjusting move
> this loop explicitly forbids, and it would have produced a lovely number:* a looser gate grounds
> more words on fiction by construction. **Counting more groundings is not evidence they are RIGHT --
> lowering a threshold trades precision for recall, and nothing here measures grounding CORRECTNESS,
> only rate.** *The distinction I am holding: changing a MODEL parameter and re-measuring fairly is
> legitimate; changing it because it makes the number move is not. I could not tell those apart here
> without a correctness measure, so I did not do it.*
>
> ## 🧠 **WHAT THE BRAIN OFFERS INSTEAD IS A DIFFERENT MECHANISM, NOT A LOOSER ONE -- AND WE**
> ## **IMPLEMENTED ONE SIDE OF A LIVE SCIENTIFIC DEBATE WITHOUT NOTICING THE OTHER SIDE EXISTS.**
> `grounding_acquisition_loop.py:194`, our own code: *"SHAPE (Medina 2011 PNAS / Trueswell 2013 Cog
> Psych / Woodard 2016): **exactly one hypothesis** is [carried] ... **the thing the PBV literature is
> unambiguous about**"*, with `strength` from Stevens 2017 Hybrid Pursuit. **We implement
> PROPOSE-BUT-VERIFY: one candidate meaning at a time, abandoned on disconfirmation.**
>
> **AND PBV PREDICTS OUR FAILURE EXACTLY.** A single hypothesis meeting varied contexts is
> disconfirmed and abandoned repeatedly -- **which is precisely the elevated ESCALATED rate on
> narrative (0.3523 vs 0.2616).** *The mechanism is not malfunctioning; it is doing what that model
> says learners do, in a regime where that model struggles.*
>
> **THE COMPETING ACCOUNT IS ALSO LITERATURE, NOT INVENTION: cross-situational statistical learning
> (Yu & Smith 2007) tracks MULTIPLE candidates in parallel and lets accumulated co-occurrence decide,
> which needs no two contexts to resemble each other.** It is specifically demonstrated in
> HIGH-AMBIGUITY, varied-context settings -- our failing regime.
> *⚠️ HONESTY ABOUT STATUS: these two accounts CONFLICT and the debate is live. Swapping PBV for
> cross-situational is not "fixing an infidelity" -- it is **choosing the other side of an open
> question**, and it must be labelled that way rather than as brain-correction. Our archive has
> **1 hit** for `cross-situational` and **0** for `mutual exclusivity` / `fast mapping`, so the
> alternative has never been tried here.*
> **➡️ THE TEST THAT WOULD SETTLE IT FOR US: a parallel-candidate arm against PBV, scored on BOTH
> genres. If multi-hypothesis tracking rescues narrative while matching PBV on exposition, that is an
> answer about our substrate -- and a small piece of evidence in a real debate.**
>
> ## 🎯 ANSWERED -- **NOT EXPOSURE. CONTEXT CONSISTENCY, AND THE MACHINERY TRIES AND FAILS.**
> Same 8,000-sentence budget, four corpora, two genres:
>
> | corpus | library | grounded | enc/item | **coherence** | PENDING | ESCALATED |
> |---|---|---|---|---|---|---|
> | `textbook_biology_2e` | 6,475 | 831 | 4.85 | **0.0835** | 3,860 | 1,784 |
> | `simplewiki` | 9,212 | 330 | 3.46 | **0.0591** | 6,600 | 2,282 |
> | `little_women` | 7,520 | 59 | 3.60 | **0.0256** | 4,764 | 2,697 |
> | `sherlock_holmes` | 6,987 | 49 | 3.73 | **0.0278** | 4,521 | 2,417 |
>
> **grounding 11.0x apart · exposure only 1.14x apart · coherence 2.67x apart · escalation HIGHER in
> narrative (0.3523 vs 0.2616).**
>
> **⛔ (a) EXPOSURE IS RULED OUT. Narrative words get essentially the same number of encounters
> (3.66 vs 4.16).** More reading is not the fix, which is the cheap answer and it is dead.
> **✅ (b) COHERENCE CONFIRMED, and (c) with it: narrative words ESCALATE MORE.** The evidence
> arrives, the verifier runs, and it cannot settle on a hypothesis. *Novels USE words; textbooks
> EXPLAIN them.*
>
> **🔑 THE SHARPEST FRAMING, AND IT IS NOT "NOVELS ARE INCOHERENT": BOTH NUMBERS ARE TINY -- 0.071
> AND 0.027, BOTH NEAR ZERO. Our grounding threshold simply happens to sit BETWEEN THEM.** The
> mechanism demands more contextual consistency than narrative supplies, and expository text clears
> it only barely. *That is a statement about OUR threshold, not about literature.*
> **🧠 AND THE FIDELITY GAP IS EXACT: children acquire most of their vocabulary in precisely the
> regime that sits below our threshold.** A mechanism requiring repeated near-identical contexts is
> the wrong SHAPE for how word learning actually happens -- the brain does it from varied,
> single-pass, narrative exposure.
> *⚠️ SCOPE: 8,000 sentences, seed 7, four corpora, two per genre. The genre split is consistent
> across both members of each group, which is what makes it more than a two-corpus accident.*
>
> ## [DONE -- SEE ABOVE] **WHY DOES THIS SUBSTRATE BARELY LEARN FROM NOVELS?**
> *Three-read check done: `experiment_index` returns **0** for `expository`, `fiction` and
> `corpus type`; ORGAN_MAP's corrections carry nothing on acquisition regime. Genuinely new ground.*
>
> **🧠 THE BRAIN ARGUMENT, AND IT IS NOT A CONVENIENCE ONE.** Children acquire most of their
> vocabulary from **narrative and conversation**, not from definitional text. A learner that only
> works on expository prose is not a learner with a corpus preference -- **it is diverging from the
> acquisition regime the reference standard actually operates in.** The substrate fails precisely
> where the brain most obviously succeeds.
>
> **THE THREE CANDIDATES:** (a) EXPOSURE -- fewer encounters per word; (b) COHERENCE -- similar
> exposure but far more VARIED contexts, because *novels USE words and textbooks EXPLAIN them*;
> (c) the machinery TRIES AND REJECTS, which shows up as ESCALATED rather than PENDING.
> **The PENDING/ESCALATED split is the part that matters most: those two call for completely
> different fixes, and reporting "fiction does not ground" without separating them hides which.**
> *Coherence is measured only on items with >=4 traces, so a corpus is not penalised for words it
> barely met -- that would confound (a) into (b).*
>
> ## 📚 **FICTION COULD NOT BE TESTED, AND THE REASON IS A FINDING: THIS SUBSTRATE IS AN**
> ## **EXPOSITORY-TEXT LEARNER. ON NOVELS IT GROUNDS UNDER 1% OF THE WORDS IT MEETS.**
> The fiction arm **refused to report** -- 14, 15 and 17 shared candidates against a 40 minimum, so
> the guard fired rather than scoring noise. Chasing why:
>
> | corpus | grounded @2,000 | @4,000 | @8,000 | library @8,000 | grounding rate |
> |---|---|---|---|---|---|
> | `textbook_biology_2e` | 271 | 445 | **819** | 6,475 | **12.6%** |
> | `simplewiki` | 74 | 222 | 331 | 9,212 | 3.6% |
> | `little_women` | 42 | 51 | 59 | 7,520 | 0.8% |
> | `sherlock_holmes` | 14 | 37 | **50** | 6,987 | **0.7%** |
>
> **A biology textbook grounds ~16x more of what it reads than Sherlock Holmes does, from a SMALLER
> library.** *That is not a quirk of one novel -- both fiction corpora sit under 1% while both
> expository corpora sit well above it.*
> **🔑 SO THE FICTION TEST IS NOT INCONCLUSIVE, IT IS INAPPLICABLE, AND FOR A REASON THAT MATTERS
> MORE THAN THE TEST WOULD HAVE: `keep_noting_grounded` acts on words AFTER they ground, and on
> narrative text almost nothing grounds.** There is no surface for it to act on. *Reporting "the fix
> does not generalise to fiction" would have been false -- what does not reach fiction is GROUNDING
> ITSELF.*
> **➡️ AND IT SCOPES Q74 HONESTLY: the recommendation holds for expository prose, where it is now
> measured twice on genuinely different vocabularies. It is untested on narrative text and cannot be
> tested there until grounding works there.** *That is a bigger open question than the flag, and it
> is now visible instead of hidden inside a null.*
>
> ## ✅✅ **IT GENERALISES -- AND THE EFFECT IS BIGGER ON A REAL TEXTBOOK THAN ON WIKIPEDIA.**
> `textbook_biology_2e`, 3 seeds, 16,000 sentences, paired on identical probes within each seed.
> **Technical expository prose with a dense specialist vocabulary -- and a much harder task: 261-279
> candidates against simplewiki's 74.**
>
> | seed | candidates | COOC | DEFAULT | KEEP_NOTING | POSTONLY |
> |---|---|---|---|---|---|
> | 7 | 271 | 20.0 | 109.0 (5.45x) | **52.0 (2.60x)** | 48.5 (2.42x) |
> | 101 | 261 | 19.0 | 107.0 (5.63x) | **50.5 (2.66x)** | 49.0 (2.58x) |
> | 20260819 | 279 | 21.0 | 100.0 (4.76x) | **57.5 (2.74x)** | 61.0 (2.90x) |
>
> **3 of 3 seeds separated. Pooled paired difference -21.0, 95% CI [-26.0, -16.0]** -- against
> simplewiki's -6.0. **The gap roughly HALVES on every seed (5.45x -> 2.60x, 5.63x -> 2.66x,
> 4.76x -> 2.74x).**
> **🔑 THIS IS THE STRONGEST FORM THE GENERALITY CHECK COULD HAVE RETURNED: a different genre, a
> different vocabulary, a candidate pool 3.6x larger, and the effect is LARGER rather than smaller.**
> *The one-corpus limitation I wrote into Q74 myself is now substantially closed for expository prose.*
> *⚠️ Fiction (`sherlock_holmes`, 8,000 sentences) is still running -- the recommendation is not
> fully firmed until narrative text reports.*
>
> ## [DONE -- SEE ABOVE] **DOES IT HOLD ON TEXT THAT IS NOT WIKIPEDIA?**
> Every number supporting `keep_noting_grounded` so far comes from **one corpus**: `simplewiki`. That
> is the limitation I wrote into Q74 myself, so it is the next thing to close rather than something
> to wait on. Same 3-seed paired design, same probes within a seed, now on
> **`textbook_biology_2e`** -- technical expository prose with a dense specialist vocabulary, about as
> far from simple encyclopedia entries as the shelf offers without leaving non-fiction.
> *Queued after it: `sherlock_holmes` (narrative fiction, 10,799 sentences, so it runs at 8,000).*
>
> **PRE-COMMITTED, BEFORE THE NUMBERS EXIST:**
> - holds on both -> the result generalises across genre, and my Q74 recommendation firms up.
> - holds on the textbook, fails on fiction -> it is an expository-prose effect. **Say that, and
>   narrow the recommendation to the corpora where it is measured** rather than defending it.
> - fails on both -> **the simplewiki result is corpus-specific and Q74 must be withdrawn and
>   re-filed.** *An owner decision resting on one corpus is exactly the kind of thing that should be
>   retracted loudly, not quietly re-scoped.*
>
> ## 📈 **SCALE CURVE WITH THE SHIPPED FIX -- THE GAIN GROWS WITH SCALE, AND THE SLOPE HALVES.**
>
> | sentences | DEFAULT | KEEP_NOTING (shipped) | improvement |
> |---|---|---|---|
> | 2,000 | 2.29x | **1.68x** | 27% |
> | 4,000 | 2.91x | **2.20x** | 24% |
> | 8,000 | 3.56x | **2.35x** | 34% |
> | 16,000 | 5.33x | **3.17x** | **41%** |
>
> **Phase slope on this instrument: DEFAULT +1.410 -> KEEP_NOTING +0.667 per e-fold. A 53%
> reduction.** *The curve still CLIMBS -- we keep falling behind as we read more; we just fall behind
> at roughly half the rate.* Reachability rises with scale exactly as it should
> (`cos-to-snapshot` 1.000000 -> 0.899 -> 0.805 -> **0.740**), which is the profile being genuinely
> rewritten by later reading rather than nudged.
>
> **⚠️ THESE SLOPES DO NOT CROSS SCORERS, AND I ALMOST QUOTED THEM AS IF THEY DID.** The +1.708 /
> +1.035 / +0.631 figures recorded earlier come from a curve with a **GROWING candidate pool and
> different probes**; this one uses a **frozen 74-term set fixed at 2,000 sentences**, identical for
> both arms. **+0.667 must NOT be read as "better than the post-hoc coverage arm's +1.035" or
> "comparable to centring's +0.631".** The only legitimate comparison here is DEFAULT vs KEEP_NOTING,
> measured side by side on the same instrument -- and that one is clean.
>
> ## 📋 **ON THE BOARD AS Q74 -- THE ONLY OWNER DECISION OUTSTANDING. NOT BLOCKING; WORK CONTINUES.**
> *Should `keep_noting_grounded` become the DEFAULT?* It changes canonical substrate behaviour for
> every future experiment, so it is the owner's call, not mine. **Filed with the risk of my own
> recommendation stated in the question**: it makes the reader do strictly more work per sentence, it
> is tested on ONE corpus at ONE size, and **it makes a bad number better without making it good** --
> the arm still loses to word-counting. Middle option offered: leave the default alone but switch it
> on for all NEW experiments, so evidence accumulates on other texts before committing.
> *Until it is answered the result sits behind a flag nothing uses, which is a gain we are not
> collecting.*
>
> ## ✅ **SHIPPED POST-ONLY, RE-VETTED, AND IT IS BETTER THAN WHAT IT REPLACED.**
> `LibraryItem.grounded_at_n_traces` stamped at banking; `Substrate.profile()` under the flag adds
> only `traces[grounded_at_n_traces:]`. Re-ran the same 3-seed vet against the SHIPPED code:
>
> | seed | COOC | DEFAULT | shipped KEEP (post-only) | *was* whole-pile |
> |---|---|---|---|---|
> | 7 | 7.0 | 33.0 (4.71x) | **18.0 (2.57x)** | 19.5 (2.79x) |
> | 101 | 9.0 | 45.0 (5.00x) | **27.0 (3.00x)** | 30.0 (3.33x) |
> | 20260819 | 9.0 | 45.0 (5.00x) | **29.0 (3.22x)** | 31.0 (3.44x) |
>
> **Better in 3 of 3 seeds than the version it replaced.** Pooled paired difference vs DEFAULT
> **-6.0, 95% CI [-8.0, -4.0]**, separated in every seed. *And it now matches the independently
> computed POSTONLY arm, which is the cross-check: two different implementations of "post-grounding
> only" -- one via an exact trace count inside the substrate, one via `pass_idx` outside it -- agree.*
> **Gap to the counter across the session's best arms: 5.00x -> 3.00x.**
>
> ## ⚠️ **CORRECTION -- I RAISED A FALSE ALARM ABOUT THE `gap_detector` ABLATION. WITHDRAWN.**
> Earlier tonight I wrote that the ablation is *"accepted, recorded and inert"* and that **"ANY PRIOR
> RESULT RESTING ON THE `gap_detector` ABLATION NEEDS RE-CHECKING."** *That was wrong, and it was the
> kind of wrong that would have sent someone auditing clean work.*
>
> **INSTRUMENTED THE LIVE ORGAN, 1,500 sentences, DEFAULT run:**
>
>     is_gap returned True  (is a gap, proceed):  8,053
>     is_gap returned False (known, SKIP)      :      0
>     fraction of words the organ actually skips:  0.0000
>
> **THE ABLATION IS FAITHFUL.** `_NullGapDetector` says GAP to everything -- **which is exactly what
> the live organ already does on this path.** It looked inert because the organ is already maximally
> permissive, not because the instrument is broken. *So a prior cell reporting "ablating gap_detector
> changes nothing" was reporting a TRUE fact about the organ, not an artifact. The alarm is withdrawn
> in the same place it was raised.*
> **🔑 AND WHAT REPLACES IT IS A REAL NEGATIVE ABOUT AN ORGAN: the gap detector performs ZERO
> discrimination on the reading path at this scale.** Every word it is asked about is a gap. *That is
> also why grounded words stay blocked -- the terminal short-circuit stops them BEFORE `is_gap` is
> ever consulted, so the organ never even sees the population it would need to discriminate.*
> *⚠️ SCOPE: measured at 1,500 sentences on `simplewiki`, on the `process_sentence` path only. It does
> not say the organ is useless everywhere -- it says it discriminates nothing HERE.*
>
> ## ✅✅ **VET PASSED -- THIS IS A RESULT, NOT A HYPOTHESIS. FIRST ONE OF THE SESSION.**
> Three seeds at 16,000 sentences, arms paired on the SAME probes within each seed:
>
> | seed | candidates | COOC | DEFAULT | KEEP_NOTING | **POSTONLY** |
> |---|---|---|---|---|---|
> | 7 | 74 | 7.0 | 33.0 (4.71x) | 19.5 (2.79x) | **18.5 (2.64x)** |
> | 101 | 108 | 9.0 | 45.0 (5.00x) | 30.0 (3.33x) | **27.0 (3.00x)** |
> | 20260819 | 114 | 9.0 | 45.0 (5.00x) | 31.0 (3.44x) | **30.0 (3.33x)** |
>
> **3 of 3 seeds separated for BOTH arms.** Pooled paired differences: KEEP - DEFAULT **-5.0, 95% CI
> [-6.0, -3.5]**; POSTONLY - DEFAULT **-6.0, 95% CI [-8.0, -4.5]**.
>
> **🔑 AND THE DOUBLE-COUNT ARM DID NOT JUST SURVIVE -- IT WON, IN 3 OF 3 SEEDS.** POSTONLY adds ONLY
> traces recorded after grounding, so it cannot double-count, and it beats the shipped merge every
> time. **That inverts the concern: the shipped version's double-count was mildly HURTING, not
> flattering.** *The pre-registered failure mode was "KEEP wins but POSTONLY collapses -> retract".
> The opposite happened, which is the strongest form this check could have returned.*
> **➡️ SO THE SHIPPED MERGE SHOULD BE RE-SHIPPED AS POST-ONLY.** Concrete and small: record
> `grounded_at_pass` on the `LibraryItem` at promotion, and have `profile()` sum only traces with
> `pass_idx > grounded_at_pass`. Same additive, default-off discipline.
>
> **⛔ WHAT IT STILL IS NOT: A WIN OVER COUNTING.** 2.64x-3.33x behind COOC at 16,000. **The curve
> bends hard and does not cross.** One corpus, three seeds, and the probes are drawn from the
> candidate set frozen at 2,000 sentences -- all of which travel with the number.
>
> ## [KEPT FOR THE RECORD] the smoke that refused this claim, and why it did not count
> **The `DIAG_FINAL=4000` smoke returned "NOT ESTABLISHED" in 0 of 3 seeds.** It ran at the scale
> where the single-seed effect was SMALLEST (2.91x -> 2.50x) while the headline was at 16,000. Had I
> reported it, I would have retracted a real result on smoke numbers -- the third time tonight that
> error was available and the first time the trap pointed at a TRUE finding rather than a false one.
> `scratch/diag_keepnoting_multiseed.py`, running at 16,000. Three arms: DEFAULT · KEEP_NOTING (as
> shipped) · **KEEP_NOTING_POSTONLY** -- consolidated vector plus ONLY traces with
> `pass_idx > snapshot_pass`, which **cannot double-count**, because the shipped merge adds the whole
> Library sum to a consolidated vector partly built from those same pre-grounding traces.
> *Pre-committed: if KEEP wins across seeds but POSTONLY does not, the gain is the merge measuring its
> own arithmetic, and the headline number gets RETRACTED rather than explained.*
>
> **⚠️ THE SMOKE (`DIAG_FINAL=4000`) RETURNED "NOT ESTABLISHED" IN 0 OF 3 SEEDS -- AND IT IS NOT THE
> TEST.** The single-seed effect at 4,000 was **2.91x -> 2.50x**, its smallest; the headline is at
> **16,000 (5.33x -> 3.17x)**, where it is 41%. **Running a 4,000-sentence smoke and reporting its
> verdict would be the smoke-numbers error for the third time tonight.** It is recorded here so the
> full run cannot be quietly compared against a friendlier memory of it.
>
> ## 🟡 **CLAIMED, PENDING VET -- SINGLE-SEED HYPOTHESIS, NOT A WIN:**
> ## **A WIN, UNTIL IT HAS SEEDS AND CIs. BOTH FREEZES OPENED, MEASURED IN THE ASSEMBLY.**
> Write side (`Library.flag` + `process_sentence`) AND read side (`Substrate.profile` sums the
> Library traces into the consolidated vector instead of being overwritten by it). Both additive,
> both default-off, **all self-tests pass** (`grounding_acquisition_loop.self_test`, 7 substrate
> self-tests). Scoping verified: **68 of 68 grounded profiles differ between arms; every NON-grounded
> profile is byte-identical.**
>
> | sentences | DEFAULT gap | KEEP_NOTING gap |
> |---|---|---|
> | 2,000 | 2.29x | **1.93x** |
> | 4,000 | 2.91x | **2.50x** |
> | 8,000 | 3.56x | **2.55x** |
> | 16,000 | **5.33x** | **3.17x** |
>
> **Better at EVERY point, and the margin GROWS with scale (16% at 2,000 -> 41% at 16,000). Median
> rank at 16,000: 32.0 -> 19.0.** Reachability confirmed rather than assumed: `cos-to-snapshot`
> 1.000000 -> **0.825256**, rel change **1.7132**.
> **➡️ This is the first thing all session to bend the curve the substrate actually runs on, and it
> is the post-hoc coverage claim (3.69x -> 2.06x) finally reproducing INSIDE the assembly.**
>
> **⛔ WHAT IT IS NOT, AND THESE TRAVEL WITH THE NUMBERS:**
> 1. **SINGLE SEED, NO CI, MEDIANS ONLY.** This project's own rule: *a single-seed win is a
>    HYPOTHESIS.* **Do not quote 5.33x -> 3.17x as a result until it has seeds and intervals.**
> 2. **STILL LOSING.** 3.17x behind the word counter at 16,000. The curve bends; it does not cross.
> 3. **A DOUBLE-COUNT IS POSSIBLE AND UNRESOLVED.** The merge adds the Library trace sum to the
>    consolidated vector, and the Library still holds the PRE-grounding traces that produced that
>    consolidated vector. Some evidence may be counted twice. **The honest next test is
>    post-grounding traces ONLY**, which would also be the cleaner mechanism claim.
> 4. **THE SCRIPT'S OWN VERDICT LINE IS STALE** -- it still warns that "the ablation removes novelty
>    gating wholesale", which was true of the `gap_detector` attempt and is NOT true of the targeted
>    flag. *Ignore that sentence; the file has been corrected.*
>
> ## 🧱🧱 LANDED + MEASURED -- **THE FREEZE IS *TWO* FREEZES. I FIXED THE WRITE ONE; THE READ ONE**
> ## **SILENTLY DISCARDS EVERYTHING IT PRODUCES. THIRD "WRITTEN AND NEVER READ" OF THE NIGHT.**
> **SHIPPED (additive, default-off, all module self-tests pass including
> `_selftest_promotion_closes_the_gap_gate`): `keep_noting_grounded`.** `Library.flag()` appends to a
> `GROUNDED_*` item without changing status or running PBV; `process_sentence` opens the *second*
> gate too -- the terminal short-circuit that fires BEFORE `is_gap`, which is why ablating
> `gap_detector` alone had changed nothing. Exposed via `Substrate.ABLATIONS`.
> **Verified surgical at 1,500 sentences: traces 8052 -> 8242, with library items, consolidated count
> and every status count IDENTICAL.** Nothing un-grounds; only evidence accumulates.
>
> **⛔ AND THEN THE MEASUREMENT KILLED IT, FOR A REASON WORTH MORE THAN THE FIX.** With the flag ON,
> 2,000 -> 12,000 sentences, 60 grounded terms:
>
>     terms whose trace COUNT grew :  58 of 60      (2,893 new traces)
>     cos(traceMean_end, snapshot) :  0.775658      <- the LIBRARY genuinely moved
>     cos(profile_end,  snapshot)  :  1.000000      <- the READ-OUT serves the frozen vector
>
> **THE NOTES ARE NOW BEING TAKEN AND THEY ARE NEVER READ.** `Substrate.profile()` returns the sealed
> CONSOLIDATED vector for a grounded word -- its own docstring says so: *"ConceptSpace wins on
> collision because a grounded word's profile is the consolidated one."* So the arms came out
> equal (median 32.0 at every checkpoint in both), and the only moving number was the COOC floor.
> *A run reporting "keep_noting_grounded does not help" would have been true and completely
> misleading.*
>
> **🔁 THIRD INSTANCE TONIGHT OF THE SAME SHAPE, AND IT IS NOW THE DOMINANT FAILURE MODE HERE:**
> (1) the consolidated store -- written, never read by the retrieval routes; (2) `gap_detector` /
> `gap_driven_reader` / `three_tier_loop` -- built, wired by nothing; (3) post-grounding traces --
> now written, never read. **The registry answers "does it exist". Nothing answers "is its output
> CONSUMED".**
> **➡️ NEXT, AND IT IS SMALL: make the read-out respect the flag.** For a grounded word,
> `profile()` should fold the accumulated Library traces into the consolidated vector rather than
> discarding them. Same additive, default-off discipline. **Only then is the post-hoc coverage claim
> (3.69x -> 2.06x) actually being tested inside the assembly** -- everything before this point was
> testing a write that nothing reads.
>
> ## 🎯 RAN -- **THE FREEZE IS ONE `return False`, AND IT IS DELIBERATE. EXACT MECHANISM, IN CODE.**
> `hdlab/grounding_acquisition_loop.py:300-303`, `Library.note()`:
> ```python
> if it.status != "PENDING":
>     if not (revive_terminal and it.status == "ESCALATED" and it.n_revivals < max_revivals):
>         return False
> ```
> with its own docstring stating the intent: ***"GROUNDED_* items are NEVER revived here (a banked
> fact is the store's business, not the library's)."*** **So once a word grounds, `note()` refuses
> every future trace, permanently. ESCALATED items CAN be revived; GROUNDED ones cannot, by design.**
> *This is a deliberate handoff, not a bug -- and the handoff is the thing costing us.*
>
> **MEASURED CONSEQUENCE, three ways, all agreeing:**
>
>     grounded terms gaining ANY trace, 2,000 -> 16,000 sentences:   0 of 60
>     total new traces on those terms:                               0
>     mean cos(profile_16k, profile_2k):                             1.000000
>     mean cos(traceMean_16k, traceMean_2k):                         1.000000
>
> **⛔ AND TWO OF MY OWN HYPOTHESES DIED ON THE WAY HERE, BOTH CAUGHT BY MEASUREMENT:**
> 1. *"The `gap_detector` ablation will unfreeze it."* **NO.** With `ablate=["gap_detector"]` the run
>    is byte-identical to default -- profiled 2931, consolidated 68, library items 2883, **traces
>    8052 in BOTH arms**. The ablation IS registered (`sub.ablate = frozenset({'gap_detector'})`) and
>    changes nothing on this path. *An ablation that is accepted, recorded, and inert.*
>    **⚠️ THAT HAS CONSEQUENCES BEYOND TONIGHT: `gap_detector` is one of the ablations Phase 2 used to
>    argue organ contribution. An inert ablation manufactures "the organ contributes nothing".
>    ANY PRIOR RESULT RESTING ON THE `gap_detector` ABLATION NEEDS RE-CHECKING.**
> 2. *"It is a READ-OUT problem -- `profile()` returns the sealed consolidated vector while the
>    Library keeps accumulating."* **NO.** The Library stopped too: `cos(traceMean_16k, traceMean_2k)
>    = 1.000000` and zero new traces. **The writing genuinely stops.** *`profile()`'s docstring says a
>    grounded word's profile is the consolidated one, which made the read-out story very plausible --
>    and it was wrong.*
>
> **🧠 THE BRAIN DIVERGENCE, NAMED: there is no "banked, therefore closed" handoff in lexical memory.**
> A word being well-known does not stop its representation being tuned -- frequency, semantic drift
> and context-dependent tuning keep moving for life. *Ours implements UNKNOWN -> KNOWN -> DONE, which
> is a gap-filling TASK framing, not a memory architecture.*
>
> **➡️ THE PROPOSED CHANGE IS SMALL, ADDITIVE AND DEFAULT-OFF, MATCHING THIS CODEBASE'S OWN CONVENTION**
> (*"additive; default None preserves the prior behavior byte-for-byte"* appears twice in this file
> already): extend the existing `revive_terminal` / `max_revivals` parameters -- **which already exist
> and already handle ESCALATED** -- to optionally revive `GROUNDED_*` too. Then measure against the
> post-hoc coverage result (3.69x -> 2.06x at 8,000; 6.42x -> 4.39x at 16,000).
> *⚠️ PRE-COMMIT: the post-hoc number was produced by rebuilding profiles OUTSIDE the substrate. If
> reviving grounded items in-assembly does NOT reproduce it, the coverage lever does not survive
> contact with the real system, and that must be reported plainly rather than explained away.*
>
> ## [SUPERSEDED BY THE ABOVE] **TAKING THE COVERAGE GAIN INSIDE THE ASSEMBLY, WITH MACHINERY THAT**
> ## **ALREADY EXISTS -- the `gap_detector` ablation, which turned out to be INERT.**
> *Three-read prior-work check done first: registry/`hdlab` (the ablation already exists),
> `experiment_index` (`"full coverage"`, `"every encounter"`, `"note-taking"` all return **0**), and
> ORGAN_MAP's corrections (nothing bearing on this).*
>
> **🧠 WHY THIS IS ALLOWED UNDER THE OWNER'S RULE.** It does not wire an organ because it might help.
> **It REMOVES a rule the brain does not have.** There is no "known -> sealed" gate in lexical
> memory -- word representations keep being tuned by experience for life. *Our freeze is a
> GAP-FILLING task framing (unknown -> known -> done) imported into a system whose reference
> continuously tunes.*
>
> **AND THE INSTRUMENT WAS ALREADY THERE.** `Substrate.ABLATIONS` carries `gap_detector`: *"do not
> check novelty; treat every content lemma as a gap (H1 off)."* **Treating every lemma as a gap IS
> never stopping.** So: sanctioned machinery, real assembly, no defaults changed.
> **⚠️ AND ITS CONFOUND IS NAMED IN ADVANCE: that ablation removes novelty gating WHOLESALE, so the
> reader also loses the signal it forages on. A worse result would NOT show that continued
> note-taking hurts -- only that removing the whole gate hurts. The targeted flag would still be owed.**
> **Reachability is gated FIRST** (does `cos(profile_end, profile_snapshot)` actually leave 1.000000?)
> because the last three diagnostics all produced clean-looking numbers from interventions that never
> reached anything.
>
> ## 🧊 RAN -- **"DO WE HAVE A FORGETTING PROBLEM?" IS THE WRONG QUESTION: A CONSOLIDATED PROFILE**
> ## **IS FROZEN *EXACTLY*, FOREVER. NOTHING CAN BE FORGOTTEN BECAUSE NOTHING IS EVER WRITTEN AGAIN.**
> *Asked before building D8 (cascade synapse -- MISSING, math FULLY PINNED) because its pinned benefit
> is MEMORY LIFETIME, and scoring that on the phase curve would repeat tonight's testing-effect
> category error.*
>
> **THE DIAGNOSTIC'S OWN VERDICT WAS VOID AND I CAUGHT IT WITH THE RULE I WROTE THREE HOURS EARLIER.**
> It reported EARLY_RARE 32.0 and EARLY_COMMON 28.0 at **every one of five checkpoints**, drift
> exactly 1.00x, and concluded "nothing is forgotten". An exactly-constant series is a reachability
> failure until proven otherwise. Verified directly:
>
>     frozen terms whose profile changed, 2,000 -> 16,000 sentences:  0 of 74
>     mean relative change in profile norm:                           0.0000
>     mean cos(profile_16k, profile_2k):                              1.000000
>
> **THE PROFILES NEVER UPDATED. Of course nothing was forgotten -- nothing was written.**
>
> **🔑 AND THAT IS A REAL FINDING, STRONGER THAN THE ONE IT REPLACES.** The session already knew the
> reader "stops taking notes once it knows a word" (century: 7 notes across 92 sightings). **This
> measures the cutoff exactly: it is not FEWER notes, it is ZERO further notes, permanently, to
> `cos = 1.000000`.** Mechanism located in code, not inferred: `reading_grounding_loop.py:1716` --
> after a word grounds and its `KNOWN_WORD` fact is promoted it is no longer a GAP, so the reader
> stops collecting traces, and `Substrate.profile()` reads exactly those traces.
>
> **➡️ D8 IS NOT INDICATED -- BUT NOT FOR THE REASON MY SCRIPT GAVE.** Not "we do not forget", which
> was unmeasurable here. The correct reason: **you cannot have a memory-lifetime problem in a store
> that never writes again.** A cascade synapse manages decay of repeatedly-updated weights; ours are
> write-once-then-sealed. *Building it would be a faithful organ solving a problem the architecture
> forbids -- exactly the trap the owner named.*
> **⬅️ THE PRIOR QUESTION IS NOT "DO WE FORGET" BUT "WHY DO WE STOP WRITING", and that lands on the
> single biggest lever ever measured here: forcing a note on every encounter moved 3.69x -> 2.06x at
> 8,000 and 6.42x -> 4.39x at 16,000.** Coverage is one of only two levers that has ever moved the
> phase slope, and the freeze is its mechanism.
>
> ## 🚨🚨 CORRECTION -- **ORGAN_MAP ALREADY SAID "DO NOT RE-PROPOSE THIS", IN**
> ## **WRITING, IN THE SAME DOCUMENT I QUOTED TO JUSTIFY BUILDING IT.**
> `notes/ORGAN_MAP.md` §3 "THE THREE CORRECTIONS THIS METHOD FORCED ON ITS OWN AUTHOR", correction 1,
> verbatim: *"**Carandini & Heeger was TRANSPOSED.** The pool index `j` ranges over other NEURONS in
> the same population at the same moment, **so the denominator is a SCALAR for the whole
> representation. Cosine is invariant to a scalar, so canonical divisive normalisation cannot change
> a two-candidate argmax at all — 'not weakly, identically not at all.'** What was implemented and
> measured NULL (+0.0018, CI [−0.0030,+0.0065]) was efficient-coding ADAPTATION (Laughlin 1981;
> Fairhall 2001), a different real mechanism. **Do not re-propose 'apply divisive normalisation to
> fix the argmax.'"***
>
> **I READ §2 (THE PINNED TABLE) AND QUOTED IT. I DID NOT READ §3 OF THE SAME FILE.** The prior-work
> habit that has caught six rediscoveries covers `experiment_index.py` and the capability registry --
> **it does not cover the corrections section of the brain-reference document itself.** That is a new
> hole and it is exactly the shape of the ones before it: *the answer was on disk, in the file I was
> already citing.*
> **➡️ SO THE NULL BELOW IS A REDISCOVERY, NOT A DISCOVERY, AND ITS HEADLINE IS DEMOTED.** It is not
> "the strongest write-side closure we have"; it is **confirmation of a mechanism ORGAN_MAP had
> already ruled out on ANALYTIC grounds** -- cosine is scalar-invariant, so a scalar denominator
> cannot move a cosine ranking.
> *⚠️ ONE HONEST DIFFERENCE, AND IT IS WHY THE ARMS MOVED AT ALL: my divisor was a scalar PER
> SENTENCE, not one global scalar, so a term's history accumulated DIFFERENT weights and the profile
> did change (effective dims 94.7 vs SUM 92.3; ranks reordered). That is why it was not identically
> zero. It does not rescue the design -- ORGAN_MAP's analytic point stands and predicted the outcome.*
> **📌 NEW STANDING RULE, ADDED TO CLAUDE.md: BEFORE PROPOSING ANY BRAIN MECHANISM, READ THE
> CORRECTIONS SECTION OF ORGAN_MAP, NOT ONLY THE PINNED TABLE.** A pinned equation tells you what the
> brain computes; the corrections tell you what we already got wrong about it.
>
> ## ✅ RAN, FULL SWEEP -- **THE PINNED CORTICAL COMPUTATION, IN THE BRAIN'S OWN POSITION, IS INERT**
> ## **HERE -- AND ORGAN_MAP PREDICTED THAT ANALYTICALLY (see the correction above).**
> Five points, 1,000 -> 16,000 sentences. Slope of gap-to-counter per e-fold, lower is better:
>
> | arm | slope | effective dims 1k -> 16k |
> |---|---|---|
> | SUM (today's substrate) | +1.035 | 13.2 -> 92.3 |
> | NORM (within-item control) | **+0.972** | 15.5 -> 98.4 |
> | **DIVNORM (brain's position)** | **+1.206** | 13.5 -> **94.7** |
> | DIVNORM_SH (shuffled-pool control) | +1.179 | 12.6 -> 97.0 |
>
> **⛔ DIVNORM TIES ITS SHUFFLED-POOL CONTROL (+1.206 vs +1.179, 0.027 apart).** The divisor's
> correspondence to a term's OWN context carries nothing; what remains is scaling variance. **It is
> not competition, even when the pool is the population.**
> **⛔ AND IT DID NOT CONCENTRATE THE CODE AT ALL -- 94.7 against SUM's 92.3, the same trajectory
> point for point.** The prediction was that removing "responds to everything" would pull effective
> dimensionality toward the pinned ~4-12. It moved nothing. *k-WTA at least failed informatively by
> RAISING dims; this failed by being inert.*
> **✅ BEST ARM REPORTED FIRST, BEFORE ANY STORY: NORM at +0.972** -- the within-item control, and
> only 6% better than plain summing. *Floors at the largest point: COOC 18.0, FREQ 55.0. Every arm
> still loses to counting.*
>
> **🧠 WHY THIS CLOSURE IS STRONGER THAN THE SIX BEFORE IT.** Those closed a rule we CHOSE. This one
> closed **a computation the literature PINS, implemented in the POSITION the brain uses, with the
> control that distinguishes competition from scaling.** The brain-fidelity argument for intervening
> at write time is now spent: *we did the thing the brain does, where the brain does it, and the
> representation did not move.*
> **➡️ SEVENTH POSITION-FAMILY RESULT, AND THE FAMILY ITSELF IS NOW THE FINDING: every fix has been
> "right mechanism, wrong place", and fixing the place did not help either. The place was never the
> problem.**
> *⚠️ SMOKE vs FULL, recorded because I published smoke numbers as a finding earlier today: the smoke
> (900/1500/2200) read DIVNORM +1.346 / SUM +1.161. The full sweep reads +1.206 / +1.035. Same
> direction, different numbers -- the smoke was directionally right and quantitatively wrong, which
> is exactly why it was not quoted.*
>
> ## [DONE -- SEE ABOVE] TOP ITEM, RE-DERIVED UNDER THE OWNER'S RULE -- **THE PINNED CORTICAL COMPUTATION WE HAVE**
> ## **NEVER ACTUALLY RUN: DIVISIVE NORMALISATION OVER A POPULATION POOL.**
> *Chosen because ORGAN_MAP pins it, not because it looks useful. The pinned line, verbatim:*
> **"graded competition implemented BY the normalisation pool, not a hard argmax."** *(Carandini &
> Heeger -- divisive normalisation, a canonical cortical computation.)*
>
> **WHAT WE ACTUALLY TESTED WAS THE WITHIN-ITEM VERSION, BOTH TIMES. Read from the source, not
> remembered:**
> - `KWTA8/32` -> `kwta(trace, k)` keeps the k largest-magnitude **dimensions of that one trace**
> - `NORM` -> `acc += trace/||trace||`, **per-trace L2 scaling**
>
> **Neither involves any other term.** The plan already named this exact error -- *"we copied
> sparsity's SHAPE and not its POSITION"* -- and then never fixed it. **THIS IS THE FIX, AND IT IS
> THE SEVENTH INSTANCE OF THE SAME POSITION FAMILY.**
>
> **THE BRAIN'S FORM.** A neuron's response is divided by the pooled activity of OTHER neurons
> responding to the same stimulus: `R_i = x_i / (sigma + sum_j-in-pool x_j)`. **The pool is other
> units, not other dimensions of the same unit.** Mapped onto us: when a sentence is read, every
> candidate term responds to it; a term's write should be scaled DOWN by how strongly the whole
> population responded. **A word that responds to everything gets suppressed; a word that responds
> selectively gets through.**
>
> **🎯 AND IT PREDICTS SOMETHING SPECIFIC AND ALREADY-MEASURED, WHICH IS WHY IT IS WORTH RUNNING:**
> our hub carries **frequency at R^2 0.4819** against **0.01-0.05** for a typical sensorimotor
> dimension -- it is overwhelmingly a "responds to everything" code. **Divisive normalisation is
> precisely the operation that removes responds-to-everything from a representation.** Prediction:
> effective dimensionality should FALL (k-WTA RAISED it, 92.3 -> 130.2). Pinned target ~4-12.
> *Pre-commit both ways: if it does not concentrate the code, the population reading of competition
> is wrong too and the write side is closed on brain-faithful grounds as well as empirical ones.*
>
> ## 🧠🚨 OWNER CORRECTION 2026-08-20T02:14Z -- **AND IT INVALIDATES MY OWN RECOMMENDATION BELOW.**
> > *"I want to re-emphasize being brain foundational here. Don't just wire in organs because you
> > think it could help - we're making connections because the brain does"*
>
> **THEY ARE RIGHT AND IT LANDS EXACTLY ON WHAT I PROPOSED.** I recommended wiring
> `exp_cheap1_contradiction_detect_cpu_v1` **"because it feeds the revision path that already
> works."** That is a UTILITY argument. It never once named a brain structure. It is the precise move
> the standing frame forbids: *"WHICH BRAIN STRUCTURE, and are we replicating it or substituting
> something convenient?" -- never "did we consider the brain?"*
>
> **⛔ AND THE THING I WAS ABOUT TO BUILD ON IS NOT A BRAIN MECHANISM AT ALL.** AGM contraction is
> **Alchourrón, Gärdenfors & Makinson 1985 -- formal logic and philosophy.** No neuron does AGM
> contraction. We have TWO HARD_PASS cells for it (`exp_lap2_2_belief_revision_cpu_v1`,
> `exp_lap4_9_agm_contraction_depth_cpu_v1`). **We implemented the PHILOSOPHY of changing your mind
> and never the NEUROSCIENCE of it.**
>
> **🧠 SO: WHICH BRAIN STRUCTURE ACTUALLY REVISES A STORED BELIEF? RECONSOLIDATION.** Retrieving a
> consolidated memory returns it to a LABILE state, after which it is re-stored -- possibly altered
> (Nader, Schafe & LeDoux 2000; Nature 406:722). **In the brain, RETRIEVAL IS NOT READ-ONLY. Recalling
> a thing is an opportunity to change it.** That is the mechanism the owner's phrase "adjusting a
> belief" actually names.
>
> **🔎 ENUMERATED ABSENCE, WITH THE SEARCH STATED (not "I looked and did not find it"):**
>
> | term | archive (8,836 cells) | `hdlab/` (151 modules) | ORGAN_MAP |
> |---|---|---|---|
> | `reconsolid*` | **0** | **0** | **0** |
> | `destabil*` | **0** | -- | -- |
> | `memory update` | **0** | -- | -- |
> | AGM belief revision | **2 HARD_PASS** | 0 | 0 |
>
> **THE BRAIN'S ACTUAL BELIEF-REVISION MECHANISM HAS NEVER BEEN TOUCHED BY THIS PROJECT, AND THE
> PHILOSOPHER'S VERSION IS BUILT AND PASSING.** *Our substrate is also maximally far from it:
> retrieval is strictly read-only; profiles are written only at reading time. A POSITION divergence --
> the sixth of that family today.*
>
> **⚠️ THREE HONEST CONSTRAINTS, BEFORE ANYONE TREATS THIS AS A BUILD ORDER:**
> 1. **RECONSOLIDATION IS UNPINNED AS AN EQUATION.** It is a robust qualitative phenomenon, not a
>    formula. Per §1 of ORGAN_MAP that makes it UNSCORABLE for fidelity, and **any specific update
>    rule we pick is OUR-INVENTION-UNDER-TEST, not brain-derived.** Unpinned does not mean stop; it
>    means label it correctly.
> 2. **IT IS A WRITE-SIDE MECHANISM, AND I CLOSED THE WRITE-SIDE ROUTE SIX TIMES TODAY.** The
>    resolution is not to ignore that -- it is that **every one of those six was measured on a
>    benchmark that never contradicts anything.** Reconsolidation must be judged on a task where a
>    belief has to CHANGE. Scoring it on the phase curve would repeat the error, not test it.
> 3. **AND THE STRUCTURE IT WOULD OPERATE ON IS ITSELF NOT BRAIN-FAITHFUL.** STATUS already records
>    it: our fact store is HD-bound `(subject, relation, object)` triples -- *an addressable symbolic
>    database*, where cortical semantic memory is a distributed overlapping representation.
>    **⛔ SO "GO FILL THE FACT STORE WITH PROPOSITIONS" -- MY OWN LAST RECOMMENDATION -- IS NOT A
>    BRAIN-FOUNDATIONAL GOAL EITHER.** It makes a convenient substitution richer. The finding that the
>    store holds no facts STANDS as a description of what we built; it does NOT follow that filling it
>    is the right move. *Downgraded from "next step" to "diagnosis", by the owner's rule.*
>
> ## ✅ OWNER NOTE ANSWERED -- **BELIEF REVISION IS REAL, CORRECT, AND HAS NEVER ONCE FIRED.**
> *"adjusting a belief sounds like an important capability for substrate - so let's keep that finding
> and integrate where it needs to go" (2026-08-20T01:31Z).* **It needs to go somewhere it can be
> TRIGGERED. It currently cannot be.**
>
> **WHAT IS ALREADY BUILT AND WORKING.** `hdlab/hd_fact_store.py` implements trust-ordered
> prioritized revision -- REPLACE / DROP / COMBINE / FLAG by trust level and relation cardinality.
> Runtime-tested, not read off the source: storing `aspirin treats headache` at LOW trust and then
> `aspirin treats fever` at HIGH trust yields **REPLACE**, the old fact goes **SUPERSEDED**, and
> `query()` correctly returns only `fever`. Positive control held (retained beliefs still findable).
>
> **⛔ AND MY FIRST RECOMMENDATION FROM THAT WAS WRONG -- CAUGHT BY ENUMERATING CONSUMERS.** The
> superseded fact's HD vector survives (hidden by a status flag, not erased), so I was about to
> recommend wiring the proven exact-erasure organ (`exp_pb_pinv_downdate_forgetting_v1`, deviation
> **1.67e-16**, retained_recall 1.000) into the supersession path. Then I enumerated who READS those
> vectors: `query()`, `live_facts()` and the conflict search at `hd_fact_store.py:292` **all** filter
> on `ACTIVE_STATUSES`, and the only direct `._facts` reader outside the class is
> `foundation_persistence.py` -- serialization, which SHOULD retain superseded records as an audit
> trail. **There is no pollution path. Erasure would buy nothing today.** *Keeping EXISTS /
> IS-REACHED / IS-GOOD separate is the only reason that recommendation did not ship.*
>
> **🚨 THE ACTUAL FINDING, AND IT IS SHARPER THAN THE ONE I WENT LOOKING FOR.** Read 6,150 sentences
> and count what the store's resolution paths did:
>
> | | count |
> |---|---|
> | facts stored | 668 |
> | distinct (subject, relation) keys | **668** |
> | keys that ever saw more than one OBJECT | **0** |
> | beliefs superseded or dropped | **0** |
> | beliefs flagged as contradictions | **0** |
>
> **668 of 668 keys are unique. Not one belief was ever challenged, so revision could not fire even
> in principle. THE READER ADDS BELIEFS AND NEVER CONTRADICTS ONE.** Belief revision is not missing
> machinery -- **it is machinery with no input.**
>
> **➡️ SO THE BUILD TARGET THE OWNER'S NOTE LANDS ON IS A CONTRADICTION SOURCE, NOT MORE REVISION.**
> `exp_cheap1_contradiction_detect_cpu_v1` landed HARD_PASS (recall 1.000, FP 0.000) and **is not in
> `hdlab/`** -- enumerated, not searched: a word-boundary scan of all 151 hdlab modules for `AGM`
> returns ZERO, and every apparent hit was the substring inside "fragment" or "magma". That organ
> feeds the revision path that already works.
> *⚠️ AND THE LIMIT ON EVERY ONE OF THOSE HARD_PASSES, STATED WITH THEM: 1.000 / 1.000 / 0.000-FP /
> 1.67e-16 are CONSTRUCTION PROOFS on synthetic facts. Exact erasure is exact because it is linear
> algebra. They show the MACHINERY works; NONE shows that revising beliefs helps this substrate read
> better.*
>
> **🚨🚨 AND CHASING "WHY WAS NOTHING EVER CONTRADICTED" FOUND SOMETHING BIGGER: THE FACT STORE**
> **CONTAINS NO FACTS.** Dumped every stored belief after 6,150 sentences. The entire relation
> vocabulary is **TWO** entries:
>
> | relation | count | object |
> |---|---|---|
> | `KNOWN_WORD` | 380 | **always the constant `CORE`** |
> | `GROUNDED_MEANING` | 288 | varies |
>
> **There is not one propositional belief in it** -- nothing of the "X treats Y" shape that revision,
> contradiction detection and AGM contraction are all built to operate on. `KNOWN_WORD -> CORE` is a
> vocabulary flag with a constant object, so **it is not capable of being contradicted by
> construction.** That is the real reason 668 of 668 keys were uncontested, and it is a much duller
> reason than "the corpus lacks contradictions".
>
> **⛔ AND THE PROVENANCE TAGS SAY THE EXTRACTOR'S OUTPUT IS NOT LANDING HERE.** The store recognises
> four pipelines -- `SEED_VOCABULARY`, `UNKNOWN_LEGACY`, `DEFINITIONAL_EXTRACTOR`, `READING_GROUNDING`
> -- and **all 668 facts are tagged `UNKNOWN_LEGACY`. Not one carries `DEFINITIONAL_EXTRACTOR`.**
> Meanwhile the reader reports `n_definitions = 73` per 1,500 sentences, so the extractor IS finding
> definitions. *Either they are stored stripped of provenance under `GROUNDED_MEANING`, or they are
> not stored at all -- and I have not yet separated those two, so the honest claim stops here.*
> **➡️ THIS OUTRANKS WIRING A CONTRADICTION DETECTOR. A detector fed a store whose only contestable
> content is a constant would find nothing, correctly. FIND OUT WHERE THE 73 DEFINITIONS GO FIRST.**
>
> **🔁 THIRD TIME THIS EXACT SHAPE HAS APPEARED TODAY, AND IT IS NOW A PATTERN WORTH NAMING:
> BUILT, CORRECT, NEVER REACHED.** (1) the consolidated store -- WRITTEN AND NEVER READ; (2)
> `gap_detector` / `gap_driven_reader` / `three_tier_loop` -- import clean, wired by nothing; (3)
> belief revision -- correct, and never triggered. *The registry answers "does it exist". Nothing
> answers "is it reached". That gap is why the same surprise keeps arriving.*
>
> ## [DONE -- SEE ABOVE] **THE EXTREME-DRIFT VERSION, PRIOR RECORDED LOW BEFORE RUNNING.**
> The only honest remainder: cross-CORPUS blocking. The shelf holds **36 corpora** including five
> textbooks (anatomy, biology, chemistry, microbiology, psychology) and several novels. Reading
> anatomy -> chemistry -> Sherlock is a genuine regime change, far past the 0.6146-0.6905 band a
> single corpus can reach.
> **⚠️ PRIOR: LOW, AND WRITTEN FIRST.** Within the range we could measure, the penalty for forgetting
> *rose* with drift (+0.051 correlation, BLOCKED worst). Extrapolating says extreme drift makes it
> worse still. **I am running it because the measured range was narrow and extrapolation across a
> regime boundary is exactly the move this project keeps punishing -- not because I expect a win.**
> *Pre-commit: if the penalty still rises with drift across corpora, the write-side route is closed
> with no remaining caveat, and I stop proposing write rules.*
>
> ## [SUPERSEDED -- PREMISE FALSE, SEE ABOVE] previous top item: **THE ONE HONEST ESCAPE FOR THE DELTA RULE -- A NON-STATIONARY CORPUS.**
> **Forgetting BUYS ADAPTATION TO A CHANGING WORLD. `simplewiki` read front-to-back is STATIONARY,
> so recency can only DISCARD EVIDENCE and must lose.** *We tested a rule for non-stationarity in a
> stationary regime -- a FOURTH position error of the same shape: right mechanism, wrong regime.*
> **THE TEST: a deliberately TOPIC-BLOCKED reading order (so a word's typical context genuinely
> drifts), same total reading, same scorer, SUM vs the delta family. Recency should win THERE.**
> *Pre-commit both ways: if recency wins under drift, the delta rule is alive and the earlier null
> was a regime artifact -- a real finding about WHEN it applies. **If it loses even under drift, the
> delta rule is dead on this instrument outright and the write-side route is closed for good.***
> *⚠️ And the honest framing either way: this tests WHEN a rule applies, it does NOT reopen the
> strategic conclusion above. Only coverage and post-hoc transforms have ever moved the curve.*
>
> ## [SUPERSEDED] previous top item: **GIVE THE PROFILE AN UPDATE RULE, SO THERE IS SOMETHING TO MODULATE.**
> This is what the three POSITION errors have been pointing at all along, and it is the one thing
> never tried: **our profiles have no learning rate.** `acc += trace` is not an update rule -- it has
> no notion of how much to move, so precision has nothing to weight and every selector can only
> choose what to add. A profile with an update rule (`p <- p + eta*(trace - p)`, i.e. an
> error-correcting move toward the observation rather than a sum) has BOTH a residual AND a step
> size, which is the form G2 actually pins.
> **THE MINIMAL TEST: replace the sum with a delta-rule update, sweep eta, and put PRECISION on the
> LEARNING RATE (eta_i = eta0 * precision_i) -- the role the brain reference actually assigns it.**
> Test on the phase slope with per-point consistency, against COOC and FREQ floors.
> *⚠️ HONEST RISK, RECORDED FIRST: a delta-rule profile is a RUNNING MEAN, and a running mean of
> context vectors is close to what the sum already computes once normalised. If eta-sweep lands on
> "eta -> 0 is best", that IS the sum and the result is a null. Say so if it happens.*
> *⚠️ AND QUERY BOTH ARCHIVES BEFORE BUILDING -- that habit has now caught five rediscoveries.*
>
> ## [SUPERSEDED] previous top item: **IMPLEMENT PRECISION WEIGHTING -- THREE LINES NOW POINT AT THE SAME TERM.**
> ORGAN_MAP G2 pins the rule as the residual `x - x_hat` **PRECISION-WEIGHTED**. Enumeration of
> `hdlab/predictive_coding.py` found 15 public names and **not one** mentions precision, variance,
> confidence or weighting; `threshold_gate` takes exactly one knob. Three independent lines have now
> arrived at that absence: the write gate's flat residual; the archive's flat-surprise-at-chance
> (0.545 / 0.542); and today's outlier-vs-new-sense confusion.
> **THE CONCRETE FORM, and it is NOT the one the archive already killed:** precision = INVERSE
> VARIANCE OF THE TERM'S OWN CONTEXT DISTRIBUTION. A word seen in consistent contexts has a
> trustworthy prediction, so a large residual is meaningful; a word seen in scattered contexts has
> an untrustworthy one, so a large residual is noise. **That is exactly the distinction that made
> today's selector an outlier detector.**
> *⚠️ QUERY-BEFORE-BUILD, AND THE ARCHIVE ALREADY KILLED A DIFFERENT PRECISION FORM:
> `exp_ingest_gate_combination_rule_race_v1` tested Friston's `raw_PE * (1 - schema_fit)` and it sat
> at CHANCE (0.530 vs flat 0.542). That used SCHEMA-FIT as the weight; this uses per-term VARIANCE.
> Different quantity -- but the prior is low and must be recorded as low before the run.*
> **TEST IT ON THE PHASE CURVE with the rate-matched random control, not on a single point.**
>
> ## [SUPERSEDED] previous top item: **2x2 FACTORIAL -- DO COVERAGE AND CENTRING ADD?**
> Both gave 39%, but from DIFFERENT RUNS, and the centring run had full coverage already on, so
> chaining them to "-63%" is an INFERENCE not a measurement. **And one cell has never been measured:
> CENTRING WITHOUT CHANGING NOTE-TAKING -- the cheap, shippable one.** Full coverage rewrites how
> the substrate reads and the owner already rejected "record everything" as the framing (Q71);
> centring is a change to how profiles are READ and costs nothing.
> Cells: A as-is+sum / B as-is+centred / C full+sum / D full+centred, ONE run, ONE population.
>
> ## [SUPERSEDED] previous top item: **COMPETITION BETWEEN THE STORED PROFILES -- ON THE ACCUMULATED STATE.**
> Every write-side variant tested (gate, centring, PC-removal, full coverage, k-WTA, normalisation)
> competes in the WRONG PLACE or not at all. The untested faithful version is the ATL hub story:
> **profiles compete with EACH OTHER for capacity** -- e.g. decorrelate/whiten the store across
> terms, or suppress a new profile's overlap with existing ones at write time.
> **TEST IT ON THE PHASE SLOPE, and note the honest risk in advance: whitening across terms is a
> POST-HOC transform in disguise, and post-hoc transforms are already closed by measurement
> (centring, PC-removal). What would make it different is applying it INCREMENTALLY AT WRITE so the
> store never accumulates the correlated component in the first place.** If that distinction turns
> out not to matter empirically, the accumulation route is exhausted and the honest next move is a
> different representation, not another write rule.
>
> ## [SUPERSEDED] previous top item: **A COMPETITIVE (NON-SUMMING) WRITE RULE, TESTED ON THE PHASE CURVE.**
> Not a gate, not a transform, not more notes -- all three are closed by measurement above. The
> minimal brain-motivated candidate is a write where representations COMPETE for capacity rather
> than accumulate independently (normalisation across the active set, or a k-winners-take-all
> sparsification at write time, which is the ATL/IT sparseness the pinned row already names).
> **THE TEST IS THE PHASE CURVE, NOT A SINGLE POINT: does the slope come down?** A level gain at
> 8,000 proves nothing -- three separate things produced one of those today.
> *⚠️ QUERY BOTH ARCHIVES FIRST. `sparse cod` returned 16 cells / 15 landed and
> `exp_arc_aggregation_sparse_code_regime_v1` reads SPARSITY_NEUTRAL; `exp_c1_sparse_value_k10_cpu_v1`
> and `exp_cortex_schema_tonegawa_sparse_ensemble_v2` both HARD_FAIL. Read those three BEFORE
> building -- that is the habit that has caught three rediscoveries today.*
>
> 4b. **[SUPERSEDED BY 4] OWNER, COMMENTARY 2026-08-19T22:27:04Z: *"don't forget the phase diagram
>    for these different components / make sure you're drilling negative results and continue to
>    evaluate brain fidelity"*. THE PHASE DIAGRAM IS THE ITEM AND IT OUTRANKS 5 BELOW.**
>    **WHY IT IS NOT BUSYWORK, AND WHY IT SHOULD ARGUABLY HAVE COME FIRST: EVERY CONCLUSION REACHED
>    TODAY WAS MEASURED AT EXACTLY ONE OPERATING POINT -- 8,450 sentences.** Three components were
>    CLOSED and two called UNDERPOWERED on the strength of a single column of numbers. *The standing
>    discipline says a fair test of a WEAK SETUP proves that setup failed, not that the capability is
>    impossible.* **A phase diagram is that discipline made systematic: sweep the control parameter
>    and show WHERE each component's behaviour changes, so "it loses to counting" can be separated
>    from "it loses to counting AT THIS SCALE".** If the gap to the counter narrows with reading, the
>    negatives are scale statements and several of today's closures reopen.
>    *Prior use of the term in this repo is the physics sense -- "phase diagram maps operating
>    envelope", boundaries in a load parameter -- and that is the sense being built.*
> 5. **THEN: re-run gap-targeting at power, or on COVERAGE.** Coverage is cheaper and is what the
>    HARD_PASS cell actually measured -- "patchy" is a coverage word, not a ranking word.
> 6. **Leave the write gate alone.** Four explanations tested; tuning thresholds cannot reach it.
>    *⚠️ Caveat consistent with item 4: that closure is also single-point. If the phase diagram shows
>    the residual's spread widening with scale, the gate deserves one re-test at the new point --
>    not a re-tune at the old one.*
>
> ## ⚠️ A PATTERN WORTH MORE THAN ANY SINGLE RESULT ABOVE: **I WROTE THREE GATES TODAY THAT COULD
> ## NOT FAIL.** The floor gate that printed FREQ and never used it; a discrimination check that
> passed on 1 nonzero in 900; an arms-differ check that passed at 0.981 overlap. **Each would have
> published a false positive or a vacuous null.** All three were caught by looking at the NUMBERS
> rather than the VERDICT LINE. *Before trusting any verdict in this file, re-read what its gate
> actually compared.*
>
> ## ⛔ CLOSED 2026-08-19: **THE RESIDUAL WRITE GATE. 0 of 54 cells, both directions.**
> `exp_predictive_write_gate_v1`, 3 seeds x 6 thresholds x 3 k. **Reading (A) in 0 of 54; floor
> cleared in 0 of 54.** At low thresholds the gate barely skips and MATCHES accumulation; as it
> skips more it MONOTONICALLY DEGRADES; at 92% skip it is IDENTICAL to random skipping to four
> decimals. **No window where selectivity helps.**
> **✅ BUT THE PINNED EQUATION IS NOT REFUTED, AND THIS IS THE LOAD-BEARING DISTINCTION.** Measured
> the same day, 16,930 paired observations, leave-one-out: **a term's profile predicts its own next
> context 10.4% better than an unrelated term's, CI [+0.0498, +0.0522], on 73.2% of observations.**
> The residual is REAL. It is also **too UNIFORM to threshold** -- sd 0.076 about a mean of 0.44.
> **Predictive coding needs a predictor sharp enough that BEING WRONG IS INFORMATIVE. Ours is
> evenly mediocre, so its errors carry no ranking. That is a fact about OUR PREDICTOR.**
>
> ## 🧭 WHAT "SHARPEN THE PREDICTOR" WOULD HAVE TO MEAN -- write this down before anyone builds it
> The next person (probably me) will be tempted to reach for a better predictor immediately. Three
> constraints first, all earned this session:
> 1. **IT MUST BE A PREDICTOR, NOT A BETTER SELECTOR.** The gate failed because the residual does
>    not RANK, and no gating rule fixes a flat residual distribution. The target is the SPREAD of
>    the residual, and a candidate that does not widen that spread cannot help however clever it is.
> 2. **CHECK IT AGAINST `COOC_floor`, NOT AGAINST OUR OWN ARMS.** Counting reaches median rank
>    15-20 of ~450; our best arm 69-79. **Three lines have now closed while comparing us to us.**
> 3. **QUERY THE REGISTRY FIRST.** `predictive_coding` was BUILT, PASSING and UNWIRED and I nearly
>    rebuilt it. Assume the next organ exists too until an enumeration says otherwise.
> *And the honest prior: three structural lines (read-out variants, cortical read, residual gate)
> have closed on the SAME representation. A fourth mechanism on the same profiles is the least
> likely thing to work; SUPPLY is the lever that has not been exhausted.*
>
> ## 🗣️ THE OWNER ANSWERED, AND CORRECTED THE FRAMING BELOW. **READ THIS BEFORE THE TOP ITEM.**
> **Q71, on note-taking:** *"students don't take notes on words - they take notes on ideas etc. If
> they already understand a word, they're not going to take notes, but if perhaps the word is used
> in a NEW way, or in a new idea, yeah they'll take notes on that... it's NEWNESS that gets notes,
> not just on words used the same way."*
> **➡️ SO "RECORD EVERY OCCURRENCE" IS THE WRONG PROPOSAL AND THE BLOCK BELOW OVERSTATES IT.** The
> 31% we skip may be CORRECTLY skipped -- identical repeated usage. **The real defect is that we
> cannot tell a NOVEL usage from a REPEATED one**, which is exactly what the residual write gate
> was for, and it failed because the residual does not discriminate (sd 0.076 about a mean 0.44).
> *Two of today's findings join here: the goal is not MORE notes, it is notes on NOVELTY, and we
> currently have no working novelty signal at all.*
> **⚠️ AND IT PUNCTURES A READING OF MY OWN MEASUREMENT: the counter WANTS every occurrence because
> it computes a frequency statistic; a note-taker wants the novel ones. So "give the counter only
> our notes and it does worse" does NOT imply "take more notes" -- it implies our notes are the
> wrong SHAPE for a counting-style read-out.**
>
> **Q72, on direction:** *"Why aren't we identifying where the notes are patchy and/or giving them
> another textbook? There's only so much you can get from one textbook."*
> **➡️ CHECKED, AND THE OWNER IS RIGHT IN A WAY I HAD NOT NOTICED: the shelf holds 28 CORPORA AND
> 325,798 SENTENCES, including five real textbooks. EVERY read-out experiment today ran on
> `simplewiki` ALONE -- 6.1% of the shelf.** *Three mechanisms were compared against a word counter
> using one sixteenth of the available reading.* **Test running with DIVERSITY as the one variable:
> same total sentences, 1 corpus vs 12, both scored against the counter ON THEIR OWN TEXT so
> "the task got easier" cannot masquerade as "we got better".**
> **✅ THAT TEST HAS SINCE LANDED -- SEE THE TOP BLOCK. Result: 1 vs 27 corpora at constant total
> reading, difference +15.8 with 95% CI [-10.0, +42.5], NOT SEPARATED. Passive breadth is UNTESTED
> at this n. The GAP-TARGETED half of Q72 is the one with a prior HARD_PASS.**
> *⚠️ And the first version of that test LEAKED 100%: its held-out set came from a fresh
> `CorpusRegistry()`, whose handles start at sentence one -- exactly where the substrate had been
> reading. 600 of 600 sentences were already seen and the arm scored median rank 3.0. Rule now in
> CLAUDE.md: draw held-out from the SAME advanced cursor and PRINT the overlap every run.*
>
> ## 🥇 [THE OWNER CORRECTED THIS: THE PRINCIPLE IS NOVELTY, NOT VOLUME] THE TOP ITEM CHANGED LATE ON 2026-08-19: **IT IS NOT A MECHANISM, IT IS NOTE-TAKING.**
> **The system stops recording traces for a word once that word grounds.** So the words it meets
> most often carry the FEWEST traces -- `century`: **7 traces across 92 sightings**. Overall
> coverage **0.688**, and the shortfall is systematically concentrated on FREQUENT words.
> **MEASURED COST, on matched text (both arms from the substrate's OWN pool):**
>
> | arm, 256 dims, same items | median rank of the answer |
> |---|---|
> | random projection of ALL occurrences | **17** |
> | random projection of ONLY WHAT WE RECORDED | **46** |
> | our actual profiles | **81** |
>
> **So 17 -> 46 is the cost of not writing things down, and 46 -> 81 is everything else about our
> representation. NOT-RECORDING IS THE BIGGER TERM.** *It is worth more than all three mechanism
> lines that closed today were chasing, and it is the cheapest thing on the list.*
> **✅ Q71 IS NOW ANSWERED AND THE ANSWER KILLS THE "RECORD EVERYTHING" VERSION OF THIS ITEM.** The
> owner's principle is *newness gets notes*, so the proposal is NOT "record every occurrence" -- it
> is "record the novel ones", and **we have no working novelty signal** (the residual gate closed 0
> of 54, and the fidelity audit above found the signal is real but selecting on it cannot change
> that the code is a count). *When any version of this runs it MUST still carry a rate-matched arm
> keeping the same NUMBER of extra traces chosen at random -- otherwise "better notes" cannot be
> told from "more notes".*
> **⚠️ AND THE HONEST RISK, recorded before anyone starts: it may simply reproduce the co-occurrence
> counter more exactly rather than beating it. That would still be worth knowing -- it would say
> the representation IS the counter, badly sampled -- but it is not a win.**
>
> ## THE ONE-PARAGRAPH POSITION
> **The read-out is not the problem and is now closed. The REPRESENTATION is.** Three independent
> measurements say so: three read-out variants built and none competitive; the cortical route's
> unique contribution BELOW independence at every k; and 0 of 18 floor cells cleared. Counting
> reaches median rank **15-20 of ~450**; our best arm 69-79. **A cue-blind FREQUENCY ranking beats
> every cortical arm at k>=10** -- most of the achievable score here is knowing which words are
> common. **Two levers remain: SUPPLY and REPRESENTATION. Both are being measured right now.**
>
> ## WHAT IS RUNNING (2 detached, both mid-flight, they contend so both are slow)
> | run | what it decides | logs |
> |---|---|---|
> | 9-seed spoke sweep | is the spoke's independence from counting real, or a small-count artefact? 3 seeds gave ratios 0.70 / 0.94 / 0.89 -- **the conjunction FAILED my own pre-registration** | `scratch/spoke9.log` |
> | `exp_predictive_write_gate_v1` | does a RESIDUAL-GATED profile retrieve better than pure accumulation -- **and better than a rate-matched RANDOM skip?** | `scratch/pwg_full.log` |
>
> ## THE FOUR THINGS A RESUMING SESSION MUST NOT RE-DERIVE
> 1. **`hdlab/predictive_coding.py` implements the pinned residual equation, self-tests PASS, and
>    is NOT on the reading path** (runtime: a real `read()` loads 44 `hdlab.*` modules, not it).
>    The next step there is a WIRING, not a build.
> 2. **The residuals are nearly constant** (p10 0.3575, median 0.4648, p90 0.5237). So a residual
>    gate is close to a RANDOM gate, which is why the rate-matched arm is mandatory, and it is
>    already in the cell.
> 3. **The threshold is a CLIFF** -- 2.5% skipped at 0.25, 76.2% at 0.50, 100% at 0.75. SWEEP it.
> 4. **The live gate is `_make_grounding_gate`, NOT the PBV one** (`checkpoint` defaults
>    `pbv=False`; verified at runtime). `state.gate_decisions` is DRAINED EVERY PASS, which is what
>    made me publish a wrong correction. *Anchor-field provenance is live and verified 36 of 36.*
>
> ## THE HABIT THAT KEEPS PAYING, AND THE ONE THAT KEEPS COSTING
> **PAYS: run it, do not read it.** Reading the code misled me three times this session; runtime
> instrumentation has not misled me once. **PAYS: ask whether the experiment could have succeeded**
> -- it has changed the plan five times, including catching a 15-minute run that was arithmetically
> unwinnable and a wiring experiment whose arms would have been identical.
> **COSTS: my own pre-registered thresholds.** One was mis-specified (lumping *at* independence with
> *below* it). One I honoured against my own preference. **Write them, then obey them, and say
> plainly when they were badly written rather than quietly re-reading them.**

> # ✅ 2026-08-19 LATE -- PLAN UPDATED IN PLACE. THE BLOCK BELOW THIS ONE IS DONE; READ THIS FIRST.
> **Everything the next block calls "NEXT STEP, REVISED" HAS LANDED. Do not re-do it.**
>
> | item | state | evidence |
> |---|---|---|
> | Re-run Phase 2 as a wiring diagnostic | ✅ DONE | `v3_consolidation`, 18 units, reading (e) fired |
> | Q66 commit `ca3_completer.py` alone | ✅ DONE | `f102e7081`, 444 lines, nothing bundled |
> | B5 sensorimotor spoke, built + scored | ✅ DONE | `hdlab/sensorimotor_spoke.py`; **reading (B): TIES** |
> | Cortical read path | ✅ BUILT, NOT YET SCORED | `hdlab/cortical_recall.py`, 4 self-tests, slot B3' |
>
> ## WHAT THE SPOKE ACTUALLY SAID -- READING (B), A TIE. NOT A WIN.
> 3 seeds, n=327-361, scored on the CORTICAL instrument with `TOP_COOCCURRENT` pre-registered as
> the bar. **SPOKE higher in 3 of 3 seeds and significant in 0 of 3** (+1, +1, +6 hits;
> p 1.0000 / 1.0000 / 0.3353). **The can-fail control BINDS: permuting every profile costs ~2.5-3x
> the hits, p<0.05 every seed -- so the norms ARE carrying the arm.** *Real signal, no advantage
> over counting. It is NOT a refutation of the 0.6413 finding: different task, scorer, population.*
> **🟢 THE UNEXPECTED RESULT, replicating 3/3 but NOT pre-registered (hypothesis-only): THE SPOKE
> PICKS BETTER MEANINGS THAN OUR OWN CONSOLIDATION GATE** -- 0.0639 pooled vs SUBSTRATE's 0.0248,
> p<0.05 every seed. **THE GATE IS THE WEAKER LINK, NOT THE SPOKE. That is the new top target.**
> **⚠️ AND MY OWN PRE-REGISTERED METRIC WAS REFUTED BY THE INSTRUMENT: I chose EUCLID off a fixture
> probe; COSINE scores >= EUCLID in ALL THREE SEEDS.** *A hand-built probe did not transfer. The
> sweep caught it; adopting one metric would have hidden it.*
>
> ## THE CORTICAL READ EXISTS NOW (`hdlab/cortical_recall.py`, slot B3', NEEDS_ADAPTER)
> Retrieves CONSOLIDATED concepts by content similarity; ranks ONLY over the consolidated subset
> and returns the grounded MEANING. **NOT built on the fact store's keys, and that is MEASURED:
> related pairs 0.4850 vs unrelated 0.4717 in `sr_key` space (gap +0.0133, identical-key control
> 1.0000) -- the store is EXACT-KEY BY CONSTRUCTION and cannot be pattern-completed.** That SHAPE
> divergence is now the primary structural obstacle, not a footnote.
> **⛔ DO NOT SCORE IT ON THE CLOZE TASK.** Measured before building: only 6.0% of held-out targets
> have any store entry, covering 2.4% of the pool. *And that sparsity is CORRECT -- 2,883 episodic
> lemmas to 68 consolidated, ~88% refused, which is CLS behaving as described.*
>
> ## 🔧 THE ONLINE SPOKE ARM -- DESIGN SETTLED 2026-08-19, INSERTION POINT IDENTIFIED
> **Two failed post-hoc probes established that this comparison CANNOT be made after the fact**
> (the gate's choice depends on the anchor field as it stood at that moment, and my "exact" replay
> called a RETIRED rule -- `pbv=True` means the live gate reads a STANDING HYPOTHESIS, never
> `canonicalize` at consolidation time). **So it must be an ONLINE SHADOW ARM, and the place is
> exact:**
> ```
> hdlab/reading_grounding_loop.py:996  _encounter_best(item, tr)   # inside make_pbv_fns
>     sp = _space_for(item)                                        # the field, possibly FROZEN
>     return canonicalize_fast(item.lemma, tr.context_vec, sp, ...)  # the TEXT rule's pick
> ```
> **THE DESIGN: at this exact call, ALSO compute the SPOKE's pick over `sp.anchors()` -- the
> IDENTICAL candidate set, at the IDENTICAL moment -- and RECORD BOTH. Record, never replace.**
> A shadow arm changes no decision, so it cannot corrupt the run that produces it, and it yields
> the PAIRED per-encounter data that no post-hoc analysis can reconstruct.
> **⚠️ SIZE IT BEFORE BUILDING IT: this is the hot path, once per encounter per item. Doubling the
> anchor scan doubles the dominant cost. Measure the per-encounter cost first and, if it is
> material, sample (e.g. every Nth encounter) and SAY SO in the metrics rather than silently.**
> *Also still open and deliberately not done: the propose-time anchor field is logged by
> `Library.flag` in `grounding_acquisition_loop`, i.e. a second module's contract. The BANK-time
> fingerprint (`n_anchors_at_bank`, `anchor_field_sha1_at_bank`) is in and bounds it from above.*
>
> ## ✅ ITEM 1 IS DONE AND IT TURNED THE VOID AROUND. The representation diagnostic ran, and then
> ## a one-variable test found the void was PART MY OWN CUE-CONSTRUCTION DEFECT.
> **The space is NOT broken and NOT a blob.** Held-out cue-to-target 0.0519 vs a scrambled cue's
> 0.0231 (gap +0.0288); 112 distinct argmax winners over 200 cues, no hub. **Scored at hit@k
> instead of hit@1, REAL vs SCRAMBLE is CI-SEPARATED at k = 1, 10 AND 50 and beats chance k/N at
> every k** -- median target rank 82 vs 108 of 223. *Retrieval, NOT discrimination.*
> **The defect: the index is per-term ACCUMULATED CONTEXT VECTORS and `cue_vector` queried it with
> a SUM OF PER-LEMMA PROFILES.** One-variable test, scale fixed: sentence cue separates at
> k=1/10/50, profile-sum cue at k=1 only. **FIXED (`context_vec`, default unchanged so callers are
> byte-identical) + a new no-op self-test. Cell re-running as `v2_hitk_sentencecue` AT THE CELL'S
> OWN SCALE, because SCALE IS STILL THE OPEN CONFOUND.**
>
> ## ⛔ CLOSED 2026-08-19: **THE CORTICAL READ. RETRIEVES, NOT COMPETITIVE, 0 OF 18 FLOOR CELLS.**
> v3 with the floors in: **`CONTEXT_clears` and `BOTH_clears` FALSE at every k on every seed.**
> Counting reaches median rank **15-20 of ~450**; our best arm 69-79. **And `FREQ_floor`, which
> NEVER LOOKS AT THE CUE, beats every cortical arm at k>=10** -- most of the achievable score here
> is knowing which terms are COMMON, and a constant ranking harvests more of it than we do.
> *Prediction was recorded before the run (`3ca164923`) and held.*
> **THREE INDEPENDENT LINES NOW SAY THE SAME THING: read-out variants are exhausted (3 built),
> the unique contribution is BELOW independence, and the floors are uncleared. THE ACCUMULATED-
> CONTEXT REPRESENTATION IS THE CEILING, NOT THE READ-OUT.**
>
> ## ⚖️ 2026-08-19 -- **THE WIRING IS WINNABLE, BUT ON A CLIFF -- AND A RATE-MATCHED CONTROL IS**
> ## **NOW MANDATORY, NOT OPTIONAL.** (`scratch/probe_does_the_residual_gate_ever_skip.py`)
> Asked before building, on real traces from a real read: 16,211 writes over 2,270 multi-trace terms.
>
> | threshold | % writes skipped | |
> |---|---|---|
> | 0.05 / 0.10 / 0.25 | 0.0 / 0.3 / 2.5% | degenerate |
> | **0.50** | **76.2%** | **the only material band** |
> | 0.75 and above | 100% | degenerate |
>
> **At 0.50 the profile genuinely moves: cosine(accumulated, gated) = 0.6793 mean, 0.2198 min.** So
> the arms are not the same function and the cell is winnable.
> **🚨 BUT THE RESIDUALS ARE ALMOST CONSTANT, AND THAT IS THE REAL FINDING HERE: p10 0.3575,
> MEDIAN 0.4648, p90 0.5237 over a 0.024-0.606 range.** Every new context is about equally
> surprising to the accumulated profile. *A genuine predictive code would show SPREAD -- some
> contexts predicted well, some badly. Ours predicts everything equally poorly, which is the
> accumulate-don't-learn diagnosis showing up in a fourth place.*
> **⛔ CONSEQUENCE FOR THE CELL DESIGN, AND IT IS NOT NEGOTIABLE: if the residual is near-constant,
> gating on it is close to gating AT RANDOM. So the cell MUST carry a RANDOM-SKIP arm matched to
> the SAME 76% skip rate.** Without it, any difference is attributable to WRITING LESS rather than
> to WRITING SELECTIVELY. *This project broke the same control twice already this session (the
> foraging twin, in opposite directions); it does not get broken a third time.*
> **⛔ AND SWEEP THE THRESHOLD, NEVER ADOPT 0.50.** It sits on a cliff -- 2.5% skipped at 0.25,
> 100% at 0.75 -- so a single adopted value would be a parameter masquerading as a finding.
> *"Copy the computation, sweep the parameter" applies exactly here.*
>
> ## 🔑 2026-08-19 -- **THE ORGAN FOR THE PINNED EQUATION ALREADY EXISTS AND IS NOT WIRED.**
> **The organ-reuse rule paid off before a line was written.** I was about to propose BUILDING an
> error signal. `hdlab/predictive_coding.py` already implements it:
> `predict(W, key)` / **`residual(observed, predicted)`** / `residual_magnitude` /
> `threshold_gate` / **`gated_write`** / **`vanilla_hebbian_write`**.
> **Its self-test PASSES** (`first_residual_mag=0.500, gate_skipped=0/8, relative_gate_ok=True`).
> **AND IT IS NOT ON THE READING PATH -- VERIFIED AT RUNTIME, not read: a real `Substrate.read()`
> loads 44 `hdlab.*` modules and `predictive_coding` IS NOT ONE OF THEM.** (`hdlab.learner` IS
> live, but it is MDL construction-induction -- `entropy_bits`, `mdl_select` -- a different thing.)
> *This is the BUILT-PASSING-UNWIRED class the 2026-08-18 audit counted 67 of. Here is number 68,
> and it is the one holding the pinned equation for the exact defect three measurements point at.*
>
> **➡️ SO THE NEXT STEP IS A WIRING, NOT A BUILD, AND IT IS CAN-FAIL BY CONSTRUCTION:**
> the organ already ships `gated_write` (write only when the residual clears a threshold) beside
> `vanilla_hebbian_write` (write always). **Our current profile accumulation IS the vanilla arm.**
> So the comparison is the organ's own two functions on the same reading run, same corpus, same
> items, against the floors that just closed the cortical read (`COOC_floor` reaches median rank
> 15-20 of ~450 -- that is the number to beat, and nothing we own has come near it).
> **⚠️ STILL REQUIRED BEFORE RUNNING IT: a named floor in the pre-registration, and an honest check
> that a residual-gated profile is even ARITHMETICALLY DIFFERENT from an accumulated one at our
> volumes -- if the gate never skips, the arms are identical and the cell measures nothing.**
> *That last check is the "could this experiment have succeeded?" question, which has changed this
> session's plan four times and has never once been wasted.*
>
> ## 🧭 WHERE THAT POINTS -- A PROPOSAL, NOT A DECISION, AND IT NEEDS A CAN-FAIL DESIGN FIRST
> Two levers remain, and only two: **the REPRESENTATION** and **the SUPPLY**.
> - **SUPPLY** = the sensorimotor spoke. Measurably NOT a re-derivation of counting (union 2.2x,
>   only 2 of 246 items shared). **Replication across seeds is IN FLIGHT and gates any build.**
> - **REPRESENTATION** = the deeper one, and it has a PINNED brain equation we are not using.
>   **A term's profile is built by pure ACCUMULATION -- `sum(context_vecs)` -- with NO ERROR
>   SIGNAL ANYWHERE.** ORGAN_MAP G2 records the brain's rule as pinned: *the residual `x - x_hat`
>   is the learning signal, precision-weighted*. **We never compute a residual, so nothing in the
>   representation is ever CORRECTED -- it only ACCUMULATES.** That is a mechanism divergence with
>   a pinned equation available, and it is consistent with everything measured: an accumulator
>   memorises what it has seen (0.1702 leave-one-out) and transfers weakly (0.0519), and no
>   read-out can recover information the store never encoded.
>   *MEMORY anchor "missing-LEARNING -> REUSE/EXPAND `hdlab/learner`, don't build parallel" applies
>   -- check that organ before writing anything new.*
> **⚠️ NOT A DECISION. Before any build: (1) does `hdlab/learner` already do this, (2) what is the
> can-fail cell, (3) what floor must it clear. This project's own record says the expensive failure
> mode is building before those three are answered.**
>
> ## 📍 WHERE THIS ACTUALLY STANDS, 2026-08-19 (read this before the direction change below)
> **THE CORTICAL READ WORKS AND IS PROBABLY NOT COMPETITIVE, AND THOSE ARE SEPARATE CLAIMS.**
> v2 landed 3 seeds: `READING (C)` True on every seed (v1 was void on every seed), and reading (A)
> fires -- REAL clears SCRAMBLE's upper CI and chance at k=[1,5,10,25,50] on two seeds and
> [5,10,25,50] on the third. **`BOTH` has the best median rank on ALL THREE seeds (69/75.5/79)
> while SPOKE ALONE beats CONTEXT on median (82-88 vs 115-126) despite a worse hit@1** -- the two
> channels are good at different things, which is the independence 2x2 reappearing in a different
> table.
> **⛔ BUT v2's BAR WAS TOO WEAK AND THAT WAS MY GAP: it scored the cortical arms against SCRAMBLE
> and chance ONLY, never the floors.** So it supports *"the route retrieves"* and is SILENT on
> *"the route is competitive"*. **v3 (`v3_floors_at_k`) adds `RANK_COOC_floor` + `RANK_FREQ_floor`
> at every k and a per-k `clears_strongest_floor_per_k`. RUNNING. It is the first version that can
> answer the only question that matters.**
> *Prior expectation, stated so it cannot be quietly revised: the subsumption diagnostic says
> counting reaches hit@50 0.6800 against the cortical 0.3767 at a 223 pool, so I expect v3 to show
> the route does NOT clear the floor. If it does clear it, that is a surprise and gets re-checked
> before it is believed.*
>
> ## 🔴🔴 DIRECTION CHANGE 2026-08-19 -- **A STOP, NOT A PIVOT. STOP BUILDING READ-OUT VARIANTS.**
> **The cortical route is SUBSUMED by word counting, not merely beaten: its unique contribution is
> BELOW the independence prediction at EVERY k** (ratios 0.80 / 0.46 / 0.55 at k = 1 / 10 / 50).
> The two routes are POSITIVELY correlated in what they get right. *"Scores lower" and "knows
> nothing new" are different claims; this is the second.* The union oracle reaches 0.7467 against
> counting's own 0.6800 -- the signature of subsumption, not complementarity.
> **THREE READ-OUT VARIANTS HAVE NOW BEEN BUILT ON THE ACCUMULATED-CONTEXT REPRESENTATION**
> (episodic, cortical-context, cortical-both). **THE CEILING IS NOT IN THE READ-OUT.** The lever is
> the REPRESENTATION or the SUPPLY.
> **⛔ THIS DEMOTES THE SHADOW ARM.** It is a read-out variant on the same profiles, and the finding
> above says that class is exhausted. *Do not build it on this evidence.*
> **➡️ THE LIVE QUESTION: the SENSORIMOTOR SPOKE is the only channel we own that is NOT derived
> from co-occurrence. It must face the SAME subsumption test -- does it get right what counting
> gets wrong, above independence? That is now the sharpest measurement available, and it decides
> whether the spoke is a real second channel or another re-derivation.**
>
> ## TOP UNBLOCKED ITEM, IN ORDER -- REWRITTEN 2026-08-19 AFTER THE CORTICAL CELL CAME BACK VOID
> **1 and 3 below are DONE. The cortical read was scored and its own reading (C) VOIDED it: the
> SCRAMBLE arm (an unrelated donor sentence) tied or beat the real cue on ALL THREE seeds, so the
> route was not reading the cue and none of its numbers count.** *Not a negative about a cortical
> read -- a void cell about THIS one on THIS task.*
>
> 1. **🔬 DIAGNOSE THE REPRESENTATION, AND DO IT BEFORE BUILDING ANYTHING ELSE ON IT.** The
>    retrieval code is fine -- `cortical_recall`'s self-tests pass on fixtures where the families
>    are separable. What failed is the space: **do held-out cue vectors and consolidated-term
>    profiles occupy a comparable space at all?** If a scrambled cue scores like a real one, the
>    likely answer is no, and everything built on accumulated context profiles inherits that.
>    **This is a diagnostic, not a build. It is cheap and it gates items 2 and 3.**
> 2. **HOLD the online shadow arm** (design settled, insertion point at `_encounter_best`, cost
>    measured at 1.6% so no sampling needed). *Building a rival meaning-selection rule on a
>    representation that may not support retrieval would repeat the failure just measured.*
>    Unblock it when item 1 answers.
> 3. **Register `cortical_recall`** only if item 1 shows the space is usable. `sensorimotor_spoke`
>    IS registered (`WIRE_NARROWED`, fidelity 3/10). **Registering an organ whose only cell came
>    back VOID would be registering on hope.**
>
> ## 🔧 GATE FACTS, CORRECTED AND VERIFIED AT RUNTIME -- earlier text in this file may contradict
> **`checkpoint` defaults `pbv=False` and the substrate never overrides it. Instrumented:
> `_make_grounding_gate` fires, `_make_pbv_grounding_gate` NEVER. THE OLD GATE IS LIVE** --
> meaning is a `canonicalize` argmax over the anchor field as it stands at the call, refusals are
> `TAUTOLOGY_NO_ANCHOR` / `CLOSED_CLASS_SUBJECT`. **`state.gate_decisions` IS DRAINED EVERY PASS**
> (peak 23, zero after), which is why reading it post-run shows nothing and is what led me to
> publish a wrong correction. *Anchor-field provenance (`n_anchors`, `anchor_field_sha1`) is LIVE
> and verified 36 of 36. The PBV-gate copy is in a path that never executes -- do not cite it.*

> # 🧠🔴 2026-08-19 -- [SUPERSEDED BY THE BLOCK ABOVE; ITS "NEXT STEP" IS DONE] THE ORDER OF THE PLAN CHANGED, AND A MEASURED RESULT CHANGED IT.
> **`exp_substrate_end_to_end_readout_v1` v3 landed: 18 units, 3 seeds, 1,053 s. READING (e)
> FIRED. THE READ-OUT NEVER CONSULTS GROUNDED FACTS.** Grounding was manipulated totally and
> verified both ways (control 38 / 68 / 112 provenance rows; B3-ablated 0 / 0 / 0), and the
> read-out is **IDENTICAL in 9 of 12 cells** -- the EPISODIC route identical to four decimals in
> **all six**. Ablating `definitions` cuts grounding by a third and moves the read-out by
> **exactly 0.0000 in all twelve**.
>
> **IT IS NOT AN INFERENCE FROM A NULL. IT IS A CODE FACT, VERIFIED AT HEAD:** `recall_sentence`
> reads the episodic DG codes and never touches `state.store`; `profile()` reads Library traces
> plus ConceptSpace, which is observed only at grounding time. `query()` does address the fact
> store -- **the scored arms do not use `query()`.** The consolidated store is written and never
> read.
>
> ## THE BRAIN-FIDELITY NAME FOR IT
> **WE BUILT HIPPOCAMPUS-TO-CORTEX TRANSFER AND THEN READ THE ANSWER OUT OF THE HIPPOCAMPUS.**
> CLS: the hippocampus writes fast and sparse, replay transfers to neocortex, and retrieval of
> consolidated knowledge is a **cortical** read. We have the write (D3 -- one of only 5 of 38
> organs computing the brain's actual equation) and the transfer (B3 -- it fires and refuses
> ~87%). **The cortical read does not exist.** *POSITION is inverted: consolidation sits
> downstream of retrieval here and upstream in the brain. METRIC compounds it -- cloze naming is
> a cortical task scored through a hippocampal route.*
>
> **⛔ THIS REFRAMES THE STANDING NEGATIVE.** "Memorises and does not transfer" (exact-key 0.9333,
> held-out 0.0044) **IS the signature of hippocampus-only retrieval** -- such a system recognises
> what it has seen and generalises nothing. **A MISSING ORGAN, NOT A REPRESENTATIONAL CEILING.**
> The slot table already named it: `semantic_parser` (Q1) and `cortex` (Q3) are both
> NEEDS_ADAPTER, and those two ARE the cortical read path.
> **✅ Two instruments agree once the wiring is known:** grounding-precision scores the grounded
> facts directly and the substrate beats random there (0.0244 vs 0.0031). Grounding works; the
> read-out cannot see it.
>
> ## WHAT THIS DOES TO THE PRIMARY FOCUS
> **The sensorimotor channel feeds the cortical/consolidated side, which this instrument does not
> read. Building B5 first and scoring it end-to-end here would have produced a GUARANTEED NULL,
> and it would very likely have been filed as "sensorimotor does not help inside the substrate".**
> *That is "ask whether the experiment could have succeeded" paying out a second time, in advance.*
> **NEXT STEP, REVISED: build the cortical read path (Q1 + Q3 adapters) so the consolidated store
> has a reader, OR score B5 on an instrument that already reads that store. Do not score B5 here.**
> The sensorimotor result itself is untouched by this and still stands.

> # ⏹️ COMPACTION HANDOFF -- 2026-08-19, AUTOLOOP **DISARMED** BY OWNER. READ THIS BLOCK ONLY.
> **NOTHING IS RUNNING. Both cells finished and are committed. The loop is off (`armed: false`).**
>
> ## THE PRIMARY FOCUS, IN ONE SENTENCE
> **WIRE THE SENSORIMOTOR NORMS IN AS A FOUNDATION ASSET AND TEST WHETHER THE SUBSTRATE CAN USE
> THEM.** *That is the one live positive with a mechanism-shaped next step, and everything else
> this session established is a boundary around it.*
>
> ## WHY -- THE THREE RESULTS THAT MATTER, IN ORDER
> 1. **🟢 THE SIGNAL TEXT LACKS IS IN THE SENSORIMOTOR NORMS.** Fitted, 4 controls binding:
>    **0.6413 vs co-occurrence 0.3067**. Unfitted replication on HUMAN ratings, different scorer:
>    **rho 0.3171 vs 0.0826, paired bootstrap +0.2348, CI [+0.1605, +0.3155]**. Raw co-occurrence
>    does not predict human similarity at all (CI includes 0). **100% coverage of our vocabulary.
>    The asset is on disk and was filed CLOSED on one narrow test.**
> 2. **🧱 CO-OCCURRENCE HAS A CEILING.** ~0.31 however processed -- raw, Dice, NPMI, full 1,024-dim
>    profile, linear, nonlinear, supervised on the answers. **Retrieval dwarfs discrimination on
>    4 corpora: hit@50 0.280-0.542 vs hit@1 0.078-0.136.** The answer is in reach; we cannot pick
>    it out. *This is why more text-only mechanism is not the move.*
> 3. **🔴 THE ASSEMBLED SUBSTRATE MEMORISES AND DOES NOT TRANSFER.** Exact-key 0.9333, held-out
>    0.0044, and an unrelated cue scores the same as the real one. Real, resolved, and it stands.
>
> ## THE THREE CONCRETE NEXT STEPS
> 1. **BUILD:** a sensorimotor channel in `hdlab/` + a can-fail cell scoring it INSIDE the
>    substrate (not as an offline feature table). **Pre-register that it must beat `TOP_COOCCURRENT`,
>    not just random** -- see the grounding result below for why.
> 2. **RE-RUN `exp_substrate_end_to_end_readout_v1`** with periodic consolidation and an
>    `EXACT_COOC_COSINE` arm. Its ablation table is currently NOT quotable: that cell ran
>    `max_patches=1`, so its consolidation organ never fired.
> 3. **Q66 IS STILL OPEN AND STILL NEEDS YOU:** `hdlab/ca3_completer.py` is UNTRACKED with ZERO git
>    history. Any checkout/reset/clean destroys it. My recommendation stands: commit it alone.
>
> ## WHAT LANDED THIS SESSION (44 commits, `2e8134fd2` .. HEAD)
> Phase 0 done (import 205s->30s, dashboard says UNVETTED). Phase 1 done (`hdlab/substrate.py`,
> self-testing). Phase 2 done (resolved negative). D7 successor representation built and REFUTED
> by its own scale ladder. **Eight defects found in my own tooling, four of which would have been
> published as substrate findings.** Two of my own promoted claims RETRACTED by my own controlled
> cell. New durable tools: `readout_verdict.py`, `strongest_floor_audit.py`, `middle_band_miner.py`,
> `scramble_control_audit.py`, `build_conceptnet_gold.py`.
>
> ## THE HABIT THAT PAID FOR ITSELF, AND THE ONE RULE TO CARRY FORWARD
> **ASK WHETHER THE EXPERIMENT COULD HAVE SUCCEEDED BEFORE ASKING WHY IT DID NOT** -- it caught a
> guaranteed-null replay build, an unwinnable zero-co-occurrence test, and a fake learning ceiling.
> **AND VERIFY WITH A POSITIVE CONTROL, NEVER ONLY AN ABSENCE CHECK:** "no mojibake found"
> inherits the detector's bug; "the character is present" does not.


> **📖 HOW TO READ THIS FILE (it is 67 KB and every autoloop continuation is told to open it).
> IT IS NEWEST-FIRST. The top ~250 lines are the current position; everything below is the record
> in reverse order, kept so retracted claims stay VISIBLE rather than quietly deleted.**
> **THREE THINGS IN THE LOWER HALF ARE SUPERSEDED AND ARE MARKED AT THE STALE TEXT ITSELF, not
> only corrected above it:** the "~10x" Phase 2 headline (wrong floor, AND its consolidation organ
> never fired), `COOC_floor` described as "strongest" (it is not -- cosine over the same counts
> beats it 0.0300 vs 0.0125), and SR filed as "starved" (refuted by its own re-test).
> *If you are resuming and want only what to DO next, read to the first `---` and stop.*

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
