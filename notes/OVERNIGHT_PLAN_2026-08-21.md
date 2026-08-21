# OVERNIGHT PLAN -- 2026-08-21. **FOUR THRUSTS, DELIBERATELY DIFFERENT IN KIND.**

> # 🛑 **READ THIS BEFORE ANY BUILD DECISION BELOW. THREE INDEPENDENT MEASUREMENTS SAY THE SUBSTRATE'S SEMANTIC OUTPUT IS AT OR NEAR CHANCE.**
>
> | measurement | task | result |
> |---|---|---|
> | `exp_meaning_asset_vs_production_v1` | SimLex word similarity, n=322 | `P_LIVE_CONCEPT` rho **0.1048, CI [-0.0073, +0.2126] -- CROSSES ZERO** |
> | `exp_grounding_quality_readout_v1` + `B3_RESOLVED.md` | **100 BLIND** hand-scored facts | **3 MEANINGFUL / 19 RELATED / 78 NOISE** |
> | `exp_sensorimotor_spoke_grounding_v1` | candidate selection, **3 seeds x 40k sentences** | `SUBSTRATE` **0.0194 / 0.0275 / 0.0274** vs `RANDOM` **0.0194 / 0.0153 / 0.0182** -- *tied 7-of-361 on seed 1* |
>
> **DIFFERENT BENCHMARKS, SCORERS, YEARS AND FAILURE MODES. THEY AGREE.** *Each alone is dismissible
> and I would dismiss each alone -- but a benchmark artifact cannot explain a blind hand-score, a
> lenient scorer cannot explain a CI crossing zero, and a hard task cannot explain tying a random
> picker where a 12-dim human-norm profile scores 3x higher.*
>
> **EACH CARRIES A CONTROL THAT FIRED:** planted-semantic arm **0.9269**; **0 of 100** self-tautologies
> plus the charter's own bio-53%/adv-14% prediction reproducing; `SHUFFLED_NORMS` collapsing at
> **p = 0.008 / 0.014 / 0.0025**. **Each detects signal when signal is present.**
>
> ## ⛔ **WHAT THIS DOES TO EVERY THRUST BELOW**
> **T1 foraging patch-choice, the F5 monitor, the meaning-consumption link, the B5 adapter -- ALL FOUR
> assume the substrate's semantic output is a usable INPUT.** **AN ORGAN THAT CONSUMES A CHANCE-LEVEL
> SIGNAL PRODUCES A CHANCE-LEVEL RESULT *AND LOOKS CORRECTLY BUILT WHILE DOING IT*.**
> **➡️ THE ORDERING QUESTION IS NOT "WHICH ORGAN NEXT". IT IS "WHY IS THE OUTPUT AT CHANCE" -- AND THE
> ANSWER IS NOT KNOWN.**
>
> ## 🔴 **T3'S PREMISE IS WRONG AND THIS IS THE THIRD TIME THE SAME MISTAKE HAS BEEN MADE**
> **`GRADED_COMPARATOR` IS DEFAULT-*ON*, not default-off.** *`exp_graded_path_vs_orthographic_floor_v1`
> carries a field literally named **`premise_correction`** for this:* **"GRADED_COMPARATOR is
> default-ON as of `38f7a0d5c`, NOT default-OFF as the dispatch brief assumed."** **THREE INDEPENDENT
> CONFIRMATIONS:** that field; `STATUS`'s night-of table; and tonight's runtime probe
> (`live_constants_observed: {"CTX_D": 256, "GRADED_COMPARATOR": true}`).
> **A prior dispatch made this mistake, the correction was written INTO A DEDICATED FIELD, and I made
> it again anyway in this plan.** *And that cell's verdict is `DOES_NOT_CLEAR_ORTHOGRAPHIC_FLOOR` --
> so the graded path was already tested against the floor and did not clear it.*
> **➡️ T3 IS NOT A WIRING JOB. THERE IS NOTHING TO WIRE, AND THE TEST IS ALREADY RUN.**
>
> ## 🟢 **AND A SECOND EXCEPTION, RECOVERED 2026-08-21 FROM BEHIND A WRONG LABEL: ON DENSE MATERIAL, READING WORKS.**
> **`exp_bootstrap_dense_process_article_reading_fade_v6` -- `verdict` says
> `HARD_FAIL_dense_explicit_no_better_than_scattered`; its `final_verdict` says
> `MIDDLE_BAND_dense_reading_works_per_process_aggregate_capped_by_volume`, and its message opens
> *"(overstated conclusion CORRECTED)"*.** *Invisible to every query until tonight's
> `experiment_index` fix.*
>
> | process | reading-only | (seed) |
> |---|---|---|
> | `igneous_rock_cycle` | **0.6923** | (0.8462) |
> | `erosion` | **0.60** | |
> | `electricity_generation` | **0.561** | (0.6585) |
> | `digestion` / `combustion` | 0.50 / 0.4516 | |
>
> **Scramble floor ~0.1879 -> 2.4x-3.7x it, APPROACHING THE SEED.** *Its own words: **"This REFUTES
> 'reading can't supply the knowledge'."*** **The aggregate looked bad (0.2121 vs scattered 0.2788)
> because THE DENSE CORPUS IS SMALL -- 155 facts vs ~735** -- and 2 of 7 processes fail for NAMED
> reasons (entity mismatch; an article that is *"descriptive not mechanistic"*).
>
> **⚠️ NOT A CLEAN WIN: the aggregate genuinely is below the scattered baseline, it has NEVER been
> floored against COUNTING, and 5 of 7 is promising rather than proven.**
> **➡️ BUT IT LOCATES THE WEAKNESS IN *WHAT WE FEED IT*, NOT IN THE READING MECHANISM** -- and every
> chance-level number above was measured on general or scattered material.
>
> **THE ONE EXCEPTION WORTH PRESSING:** the **DEFINITIONAL** half hand-scores several times better
> than the distributional half on **three independent samples** (32%/4% paired, 48%/4% same-rows,
> 28%/6% my per-row re-score). *That is the only part of the output with a repeatable quality signal.*
> **Any organ proposal must now state WHAT IT CONSUMES and whether that input is shown ABOVE CHANCE.**
>
> ---
>
> ## 💡 **AND THE ONE ACTIONABLE LEVER FOUND TONIGHT: WRITE LESS. IT IS 4.3x AND IT IS UNTUNED.**
> **`exp_predictive_coding_write_gate_dissociation_v1` (08-18) swept the write threshold over four
> percentiles of the surprise distribution:**
>
> | threshold | **P1** (prediction-gated) | **N1** (**random**, same rate) | band | vs incumbent 0.0710 |
> |---|---|---|---|---|
> | p25 | 0.0961 | 0.0971 | `NOT_SEPARATED` | +0.0251 |
> | p50 | 0.1526 | 0.1368 | `NOT_SEPARATED` | +0.0816 |
> | p75 | 0.2268 | 0.2165 | `NOT_SEPARATED` | +0.1558 |
> | **p90** | **0.3079** | **0.3007** | `NOT_SEPARATED` | **+0.2369** |
>
> **(a) WRITING LESS IMPROVES MONOTONICALLY -- 0.0710 -> 0.3079, 4.3x, NO NEW MECHANISM.**
> **(b) A RANDOM GATE MATCHES PREDICTION-ERROR AT EVERY RATE**, and the gap SHRINKS as the rate
> tightens. ***So my Angle B write-gate half is REFUTED: the gain is RATE, not error.***
> **(c) `BEST_P1_THRESHOLD` = the HIGHEST value tested -- the sweep HIT THE EDGE OF ITS RANGE STILL
> CLIMBING. The optimum is not in the data.**
>
> **⛔ AND THE CEILING THAT MUST BE QUOTED WITH IT: EVERY ARM AT EVERY THRESHOLD IS
> `BELOW_0.5_COOCCURRENCE`.** *4.3x and still below counting. **"4.3x" alone is the most misleading
> number available from tonight's work.***
>
> **➡️ CHEAPEST REAL EXPERIMENT AVAILABLE: EXTEND THE SWEEP PAST p90.** *One parameter. No new
> mechanism. And credit NO selection rule until one separates from a rate-matched random gate.*

> # 🏆 **BEST FINDING OF THE NIGHT: THE STRONGEST SEMANTIC ASSET WE OWN IS 12 HUMAN-MEASURED NUMBERS**
> **`ASSET_NORMS12` = `hdlab/grounded_similarity.py` -- 11 Lancaster sensorimotor norms + 1 Brysbaert
> concreteness norm.** *Not a trained model.*
>
> | arm | rho on SimLex |
> |---|---|
> | **`ASSET_NORMS12`** (12 human dims) | **0.2701** -- **+0.1653 over incumbent, CI [0.0159, 0.3084]** |
> | `ASSET_V2` -- **121.1M-token encoder, 237.7M-token corpus** | 0.078-0.189 |
> | `P_LIVE_CONCEPT` (ours, 256-d) | 0.1048, **CI crosses zero** |
>
> **➡️ 12 HUMAN-RATED DIMENSIONS BEAT A 121-MILLION-TOKEN ENCODER AND OUR 256-d PRODUCTION ENCODING,
> AT 21x SMALLER.** **AND IT IS THE BRAIN-FOUNDATIONAL OPTION EXPLICITLY** -- ATL amodal hub pools
> graded multimodal sensorimotor experience (Cox et al. 2024); Lancaster norms are *"a direct
> behavioral measurement of exactly that signal"*. ***The most brain-faithful asset is also the
> best-performing one -- the cleanest vindication of Q95 found so far.***
>
> ## 🔴 IT IS LIVE, AND IT IS CAPPED OUT OF INFLUENCING ANY DECISION
> `GROUNDED_CAP = 0.45`, structurally below `SIMILARITY_LINK_THRESHOLD = 0.50`, **so the fallback can
> never trigger a merge** -- deliberate and correct for THAT job. Measured live: `sofa/couch` **0.45**,
> `dog/cat` **0.45**, `stone/idea` 0.0. **Effectively two-valued.**
> **THE ARM THAT WON USED `grounded_vector()` (raw 12-d). THE LIVE PATH USES `grounded_similarity()`
> (capped scalar). DIFFERENT OBJECTS.** *`grounded_vector` has exactly one other consumer,
> `sensorimotor_spoke.py`.*
>
> ## ⚠️ WHAT TEMPERS IT (both from `exp_meaning_asset_norms_coverage_gap_v1`, 08-16)
> - **usable table = 36,810 words, NOT 39,707** -- *"39,707 is the Lancaster CSV filename, not the
>   usable asset"*. **I quoted the wrong number first.**
> - **SimLex pair coverage = 100%; whole-corpus TOKEN coverage = 60.4%; TYPE coverage = 10.3%**;
>   type coverage by band 0.757 / 0.602 / **0.438**. **The headline was measured where the asset is
>   strongest.**
> - **PRIOR NEGATIVE:** `exp_grounded_inductive_concept_encoder_heldout_new_v1` **HARD_FAIL** -- a
>   grounded inductive encoder scored AUC **0.5879** against a **POPULARITY baseline at 0.8148**,
>   losing by **0.2269**. *Different task, but **score any use of these vectors against POPULARITY,
>   not only random.***

> # 🔬 **THE MOST CONSEQUENTIAL THING FOUND ALL NIGHT -- AND IT WAS ALREADY ON DISK.**
> **`exp_encoding_quality_instrument_v2` (08-15, `INSTRUMENT_VALIDATED`, 21/21 gates) SCORED OUR LIVE
> ENCODER.** *v1 validated the instrument on 17/17 and published no number -- validate first, score
> second.*
>
> ## THE DESIGN RULE IT ENCODES, WHICH GENERALISES
> **Two axes, NEVER averaged.** IDENTITY: *"a RANDOM encoding is near-OPTIMAL here; scoring high is
> NOT a win."* STRUCTURE: *"a random encoding must sit at ~1.0 / ~0.0; any real lift IS the signal."*
> **Averaging them lets noise launder itself into a respectable score.**
>
> ## WHAT IT MEASURED (d=256, the live dimension)
> | arm | SimLex rho | GOLD_ORTHO lift |
> |---|---|---|
> | **`P_LIVE_CONCEPT`** | **0.1048** | **26.855** |
> | `C_CONCEPT_SHUFFLED` (control) | -0.0092 | **1.021** |
> | `P_LIVE_WORD` | -0.0019 | 0.987 |
>
> **➡️ THE CONCEPT ENCODING CARRIES A LARGE, CONTROL-VERIFIED *SPELLING* EFFECT AND A MODEST BUT
> **GENUINE** SEMANTIC ONE.**
>
> > 🔴 **AND THE "SPELLING IS THE SIGNAL" READING IS REFUTED -- BY THE ARM NEXT TO IT.**
> > **`A_ORTHOGRAPHIC` -- a PURE spelling encoding -- has `GOLD_ORTHO_lift = 102.926` (FOUR TIMES
> > OURS) and `simlex_rho = -0.0122`.** *A pure spelling encoding scores **ZERO** on meaning.*
> > **So our 0.1048 CANNOT come from our orthographic content. The semantic signal is REAL and is a
> > SEPARATE property.** *I put the opposite framing in this plan two turns earlier; it is withdrawn.
> > An orthographic floor wins orthographic golds and has nothing with which to win a semantic one.*
> >
> > **AND THE READOUT IS VALIDATED END TO END:** `A_PLANTED_SEMANTIC` **0.9269** (it CAN detect
> > meaning), its own shuffle **-0.0163** (detection dies with structure), three noise arms at
> > **-0.0019 / -0.028 / 0.0008**.
> >
> > **➡️ THE CI EXISTS AND IT CROSSES ZERO. `P_LIVE_CONCEPT` rho `0.10478`, CI95
> > `[-0.00731, +0.21257]`, n=322** (reported in `exp_meaning_asset_vs_production_v1`, not in the
> > instrument cell). **SO OUR PRODUCTION ENCODING HAS NO *ESTABLISHED* SEMANTIC SIGNAL -- not "a
> > small one", an UNESTABLISHED one.** *My "small, real, not an artifact" is withdrawn; the cell's own
> > `reading_rule` says **"the incumbent itself does not clear [the zero-meaning floor]"**.*
> >
> > ## ✅ **BUT TWO BUILT-BUT-UNWIRED ASSETS BEAT IT, CI-SEPARATED**
> > | arm | rho | vs incumbent | CI95 |
> > |---|---|---|---|
> > | **`d12\|ASSET_NORMS12`** | **0.2701** | **+0.1653** | **[0.0159, 0.3084]** |
> > | **`d512\|ASSET_RETRAIN_ISOL`** | 0.2581 | +0.1533 | [0.0220, 0.2807] |
> >
> > **`ASSET_NORMS12` DOES IT AT d=12 -- 21x SMALLER THAN THE 256-d INCUMBENT.** *And
> > `ASSET_RETRAIN_ISOL` is the same arm that cleared the frequency floor in the fair test: **two
> > independent comparisons, one winner.***
> > **⚠️ NEITHER CLEARS THE ZERO-MEANING FLOOR EITHER, so "wire it" is NOT yet evidenced.**
> > *Also worth a look: **1,364 lemma collisions in a 4,096-word vocabulary.***
>
> ## ⚠️ TWO THINGS NOT TO MISREAD (I MISREAD BOTH, ONE TURN APART)
> 1. **`P_LIVE_WORD` rho ~ 0 IS NOT A DEFECT.** The live word encoder is
>    `sha256(w) -> seed -> choice([-1,+1])` -- **random BY CONSTRUCTION**, orthodox VSA, and zero is
>    the required answer. *Verified live: `byte_equality_vs_live_context_vector_masked 200/200`.*
> 2. **NO CAPACITY CLAIM IS AVAILABLE HERE.** `P_LIVE_CONCEPT` was **only ever run at d=256**. The
>    d=1024 numbers are `P_LIVE_WORD` -- the random arm -- and `A_RANDOM_IID` **moves the same way**
>    over the same jump. **Two random arms rising together is not capacity.**
>
> ## 🔎 AND, BESIDE THE ISLANDING WORK
> **12 encoder-named candidates, `0 on the live path`; every encoder registry row is
> `WIRED_BUT_NOT_PIPELINE_REACHABLE`; NO registry row names the live word encoder at all.**

> # 📚 **KNOWLEDGE-EVALUATION PRIOR WORK -- FOUND ON OWNER INSTRUCTION. 126 CELLS, 116 LANDED.**
> **Owner: *"we did work on evaluating our knowledge too -- we did a ton of it. Why haven't you
> already found all this?"*** **Correct. The four that matter:**
>
> | cell | what it says |
> |---|---|
> | **`exp_grounding_quality_readout_v1`** (08-12) | **100 BLIND rows, scored and joined 10 min later. `B3_RESOLVED.md` (08-20): 3 MEANINGFUL / 19 RELATED / 78 NOISE; `BASE-F1F3 = -0.020` CI[-0.080,+0.040] NOT separated -- the read-out fix did not move quality.** *I redid this UNBLINDED tonight.* |
> | **`exp_meaning_asset_fair_test_v1`** (08-15, 2 h) | **`ASSET_RETRAIN_ISOL` rho 0.2581, +0.1665 over the frequency floor, CI [0.016, 0.313] -- THE ONLY 1 OF 11 ARMS TO SEPARATE, and marginally. Random control 0.0099.** *Do NOT quote as "the assets clear the floor".* |
> | `exp_storage_quality_instrument_v1` (08-15, 59 m) | `INSTRUMENT_STILL_LOOSE`: 10/11 gates, **refused to publish any number** |
> | `exp_meaning_asset_handlexicon_scorability_v1` | `NOT_SCORABLE`: lexicon covers **3.9%** of the instrument vocabulary, 16 SimLex pairs vs a floor of 100 |
>
> ## ✅ **THE PAYOFF: THE SELF-GRADING NEGATIVE NOW REPLICATES ON BLIND DATA**
> `best_cos` vs hand verdict -- **blind n=100 separation `+0.0095`; my unblinded n=50 `-0.0316`.**
> **Both ~zero and the sign FLIPS -- that is noise.** *The "hint of inversion" I declined to claim
> does NOT replicate; declining was correct.* **`best_cos` carries no usable quality signal.**
>
> ## ⚠️ **AND THE RULE THIS EARNED (now in `CLAUDE.md`)**
> **The prior-work trigger fired on BUILDING and I was never BUILDING -- I was hand-scoring.**
> ➡️ **THE TRIGGER IS *STARTING ANYTHING*. AND QUERY THE ACTIVITY ("hand-score", "blind", "quality"),
> NOT ONLY THE ARTIFACT.**

> # 🧭 **LATEST STATE (2026-08-21, after the owner's two COMMENTARY notes). READ THIS BLOCK FIRST.**
> **The owner pointed at prior work on distance-to-the-grounded-foundation and said to drill it. It
> exists, it is good, and it is not connected to anything.**
>
> ## WHAT THE DRILL ESTABLISHED
> | | |
> |---|---|
> | **the hop measure is real** | `exp_cold_placement_usefulness_v1` -- `reach_frac_h1/h2/h3` over a **141,511-node** graph, 3 must-fail controls all firing |
> | **how many hops are useful** | **ONE.** `40.8x` the popularity floor at h1, **`1.9x` by h3** -- *going further looks better, but guessing-by-popularity improves faster* |
> | **the 11x lift, and its cause** | `..._recovery_opt_v1`: opaque exact **0.0262 -> 0.2930**, abstain **31% -> 3.7%**. **Cause = MORE EDGE TYPES** (gloss -> +hypernym +synonym), **not deeper search** |
> | **a properly closed wall** | `FRONTIER_FIT_PLATEAU_REPRESENTATION_WALL`: h@10 asymptotes **0.594** across a 2x capacity jump, **dense core rules out "not enough data"** |
>
> ## 🔧 **THE 101 "NOT REACHABLE" ROWS HAVE AN IDENTIFIED CAUSE, AND IT IS A STALE FACT**
> **`tools/capability_registry_audit.py` was rooted at 9 entry points and `hdlab/substrate.py` was
> NOT one of them** -- excluded by a 2026-08-13 comment stating it *"DO[ES] NOT EXIST"* with *"no git
> history at all"*. **It exists (64,370 b) and was added by `2f9f3ae95`, whose message is "the
> assembled substrate exists, runs end to end, and self-tests PASS".**
> **RUNTIME CROSS-CHECK:** a real `read(n_sentences=40)` loads **37** top-level modules -> **34
> registry rows agree, 4 are WRONG** (`definitional_extraction`, `information_foraging`,
> `corpus_registry`, and **`substrate_assembled_reader_v1` ITSELF**). *The registry asserted the
> assembled substrate is unreachable by the pipeline while running it loaded every other module in
> the trace.*
> **FIXED** -- added to both root lists (9->10, 7->8), evidence recorded at both call sites,
> `--self-test` green before and after. *`pipeline.py` deliberately NOT added: that half of the
> original claim is still true.*
> **➡️ SO 101 IS AN UPPER BOUND FOR A CONCRETE REASON, NOT A VAGUE ONE. Re-audit pending.**
>
> ## 🔴 AND THE FINDING THAT MATTERS MOST
> **THREE WORKING, CONTROLLED CAPABILITIES THAT NOTHING CONSUMES** -- `gap_driven_reader` (zero
> callers), **cold placement (no `hdlab/` module, 0 of 208 registry rows)**, banked meanings (nothing
> reads them). **That is why the owner had to remember this work: the registry-first check returns
> NOTHING for it.**
> *My earlier framing -- "a library with no reader" -- was too kind. **Several finished instruments,
> none plugged in.***
>
> ## ⚠️ CARRY THESE
> - **WordNet dependency must be stated** whenever cold placement is described. *"The system worked
>   out where the word belongs" and "a dictionary told it" are different claims; only the second is
>   supported.*
> - **Do not quote `ratio_vs_floor` 148.76 / 570 / 427** -- all divide by a ~0.001 epsilon floor.
> - **The hop profile of the OPTIMISED method has never been measured** -- cheapest open question here.
> - **5 corrections to my own claims tonight**, all one family: *a quantity that pre-dated the
>   intervention, or a companion artifact I did not open, credited to the thing I was looking at.*

> # 🎯 **THE RECOMMENDATION AFTER TONIGHT, GIVEN TO THE OWNER 2026-08-21: MAKE THE BANKED MEANINGS SUPPLY THE PREDICTION.**
> **The substrate is a library, a librarian and a filing system with no reader.** It writes down what
> words mean and **never opens the file again.** Every other candidate improves a part that feeds a
> drawer nobody opens.
>
> | candidate | brain status | what it buys |
> |---|---|---|
> | **1. MEANINGS SUPPLY THE PREDICTION** ⬅️ **FOCUS** | **equation known** (prediction error) | **the only option where being WRONG about a word COSTS the system something** |
> | 2. patch-CHOICE (which text next) 🔻 **RE-RANKED: CHEAPER THAN I SAID** | equation unknown, **BUT THE MECHANISM IS ALREADY BUILT** | MVT says when to LEAVE, never where to GO -- **and `gap_driven_reader.rank_material()` IS the where-to-go half** |
> | 3. graded codes ON | equation known | cheap, real, **not a discovery** -- already measured at probe scale |
> | 4. coherence monitor (F5) | reference point only | gives the PASSAGE picture a use, **not the word meanings** |
> | 5. sleep (D8+D4) | equation fully known | **blocked**, and D8 is a published null at our scale |
>
> **WHY 1 AND NOT THE OTHERS:** until a wrong meaning produces a persistent error, the system has no
> way to tell good knowledge from bad **and neither do we without hand-grading** -- the single most
> expensive bottleneck of the last two days. **The corollary is worth more than the mechanism:**
> accumulated error per term would be a **gold-free quality estimate**, checkable against hand-scores
> that already exist.
>
> **⚠️ TONIGHT'S YIELD WAS NEGATIVE-CLEARING, NOT CAPABILITY.** Four findings withdrawn, every one
> the same error -- **a quantity that pre-dated the intervention, credited to the intervention.**
> The ground is firmer; nothing new was added.
> **OPEN FOR THE OWNER (non-blocking):** F5's test set is finished and ready; the build order puts it
> later and it does not address the core gap. *Moving it up is a legitimate call for a visible result.*

**Owner, dash 02:22Z:** *"You should make an overngiht plan with a clear and varied plan of attack,
including a few high priority organs / capabilities"* -- and, in session: *"make sure we're keeping
track of brain foundationality, and drilling negatives."*
**Owner Q95:** *"I'll only say that we should chase things that are brain foundational in every way."*

---

## 🚨 0. FIRST, A CORRECTION TO THE PLAN THIS REPLACES -- AND IT IS THE Q95 TEST WORKING

**`BUILD_PLAN` currently says: *"THE DECISION, APPLYING Q95: SLEEP (D8+D4) IS THE TOP ITEM. NOT
F5."*** It justified that with `ORGAN_MAP` STEP 5's own words -- *"the ONE place in the plan where
the brain's equation is FULLY PINNED and we have literally none of it."* **That quote is accurate.
The conclusion drawn from it is wrong, and the SAME organ entry says why, twice:**

| what STEP 5 also says, verbatim | consequence |
|---|---|
| ***"After step 1."*** *"Interleaved retention is untestable without a stream of genuinely new material to forget. Today the loop reads the same 4 segments forever."* | **SLEEP IS BLOCKED.** The test cannot run. |
| **D8 is *"🅿️ PARKED-BY-SCALE"*** -- *"the cascade only beats simpler multistate models above ~1e6 synapses; we run d = 256..4096. **A negative here is the PUBLISHED PREDICTION.**"* | **Half of it is a known null at our scale.** |

**➡️ SO THE TOP ITEM IS STEP 1, NOT STEP 5** -- and step 1 is *how you get to* step 5. This is the
repo's own third-archive rule (*read ORGAN_MAP's corrections, not only its pinned table*) catching a
decision I made yesterday by quoting one line of a two-page entry. **Quoting one section of a
document is not reading it.**

---

## 1. THE FOUR THRUSTS

**Varied by KIND on purpose** -- one build, one improvement, one wiring, one audit -- so a stall in
any single one does not idle the night, and so they do not contend for the same files.

| # | thrust | kind | brain fidelity **(stated up front, per Q95)** | blocks/unblocks |
|---|---|---|---|---|
| **T1** | **H2 -- decide what to read next** | **BUILD** (organ MISSING) | ⚠️ **FUNCTION parity only. The brain math here is UNPINNED** -- ORGAN_MAP says so explicitly. Not equation parity; the writeup must say so. | **UNBLOCKS SLEEP (step 5)** |
| **T2** | **E3 -- work out who "he"/"it" refers to** | **WIDEN A WORKING ORGAN** | ORDERING is brain-derived; **our β=0.5 / λ=0.1 arithmetic on top is OUR INVENTION.** Margin-abstention already faithful. | independent |
| **T3** | **B4 -- richer word codes on the live path** | 🔴 **PREMISE WRONG: THE SWITCH IS ALREADY DEFAULT-*ON*.** ~~3 flags landed, all default OFF~~ | Equation **PINNED**. ⚠️ **NOT A WIRE-IT TEST EITHER -- there is nothing to wire.** | -- |
| **T4** | **DRILL THE NEGATIVES** | **AUDIT** | n/a -- this is about our evidence, not the brain | feeds all |

### 🚫 EXPLICITLY NOT TONIGHT, WITH REASONS
- **SLEEP (D8+D4)** -- blocked behind T1, and D8's negative is the published prediction. *It becomes
  available the moment T1 lands, which is the main reason T1 is first.*
- **F5 coherence monitor** -- ORGAN_MAP queues it **behind step 4** and calls it **Phase B**, gated
  on *"no organ enters Phase B until its Phase-A parity is measured against a floor."* **Its
  120-item hand-scored anomaly set is READY and keeps.** *Angle A built the prerequisite; the
  prerequisite was never the permission.*
- **D7 successor representation** -- fully pinned and entirely missing, but serves multi-hop
  reasoning, *"not on the critical path until the foundation carries meaning"*. Step 6.

---

## 2. T1 -- 🔴 **SUPERSEDED WITHIN THE HOUR. THE ORGAN EXISTS, IS PINNED, AND HAS ALREADY BEEN RUN.**

> **`tools/organ_map_cite.py H2` returned as its FIRST line: *"§6 STEP 1 (H2) is superseded."***
> **Every clause of the T1 below was wrong** -- the organ is NOT missing
> (`hdlab/information_foraging.py`, witnessed, registry `WIRED`), its math is **PINNED** (Charnov
> 1976 MVT; Constantino & Daw 2015; Hayden 2011; Wittmann 2016), and **both floors I specified have
> already been run** at 10,000 sentences per arm.
>
> **➡️ WHAT THE DRILL FOUND INSTEAD IS BETTER, AND IT IS A NEGATIVE THAT SURVIVES ITS OWN CONFOUNDS:
> the organ that exists to break a 64.5% biology skew read its way to `dominant_domain =
> textbook_biology, 0.63245` -- from a free choice over 36 corpora, having visited 19 of them --
> WHILE WINNING on its own currency (gain rate 6.96 vs 5.90).**
> **MVT is a rule for WHEN TO LEAVE a patch. It is silent on WHERE TO GO.** That silence is filled by
> our patch-CHOICE function, which the map marks **UNPINNED** -- so the failure localises cleanly to
> the unpinned half of a half-pinned organ. **Breadth was never in the currency.**
> **`notes/T1_foraging_the_negative_drilled_MVT_says_WHEN_TO_LEAVE_not_WHERE_TO_GO_2026-08-21.md`**
>
> **REAL REMAINING WORK:** ~~(1) a clean re-score on a probe **not register-matched** to either arm --
> no new run;~~ 🔴 **(1) IS IMPOSSIBLE -- VERIFIED ON DISK. THE CELL PERSISTED ITS SCORES BUT NOT ITS
> OUTPUTS**: zero list-valued per-arm fields in `metrics.json`, none in `units.jsonl`'s 5 units, and
> a 9,482-byte stdout log. **The banked terms exist nowhere, so every re-analysis costs a full
> re-run** (4,144 s x 5 arms). *(2) the **patch-choice** primitive, the actual build target; (3) the
> live-path call site (`IS-REACHED: no`) -- a wiring, not a build.*
>
> **AND THE CONFOUND IS NOW QUANTIFIED, WHICH WITHDRAWS THE INVERSION HEADLINE:** measuring what each
> arm **BANKED FROM** rather than what it read -- **FROZEN 88.2% news/conversational, FORAGE 11.6%**
> -- against a probe whose backbone is **SUBTLEX-US (51M words of film/TV subtitles)**. That is a
> **7.6x register bias favouring FROZEN sitting under a 1.20x margin.** **The comparison cannot
> support a claim about selection quality in EITHER direction**, and flipping it ("FORAGE actually
> wins") would be the same overclaim reversed.
> **`notes/T1_the_register_confound_is_QUANTIFIED_a_7_6x_bias_sits_under_a_1_2x_effect_2026-08-21.md`**

## ~~2. T1 -- THE SYSTEM CANNOT NOTICE WHAT IT DOES NOT KNOW~~ **(the superseded version, kept visible on purpose)**

**The single most damning line in the whole organ map:** *"seven organs do not exist at all -- and
one of those seven is the organ that decides what to read next, which is why the system cannot
notice what it does not know."*

Today the loop **reads the same 4 segments forever**, which is why the foundation is **64.5%
biology**. Three connections, and **we already own two of them**: the corpus shelf exists now;
`gap_driven_reader.rank_material()` is already HARD_PASS and just needs calling with real candidates
instead of a synthetic dict; the driver is ~60-100 lines.

- **CAN-FAIL TEST:** seed with today's biology-heavy foundation, let it pick its next corpus from the
  36 available for N cycles, measure **what share of newly-learned words are everyday vocabulary
  rather than more biology.**
- **FLOORS -- BOTH MUST BE BEATEN, and the first one is the one that kills it:**
  **(i) RANDOM corpus choice** over the same 36 -- *if gap-ranked selection cannot beat a coin flip,
  the organ adds nothing*; **(ii) the FROZEN 4-entry schedule** that produced the skew.
- **HONEST CAVEAT, IN THE WRITEUP:** function parity, **not** equation parity. UNPINNED.

## 3. T2 -- 🔴 **SUPERSEDED. THE PROPOSED MECHANISM ALREADY RAN AND MADE COREFERENCE *WORSE*.**

> **`exp_coref_cue_based_retrieval_actr_activation_v1`, landed 2026-08-14: `HARD_FAIL`.**
> `delta vs base_principle_b = **-0.1348 (CI -0.2500..-0.0337)**`, on link-level pronoun accuracy
> over the **COMPETITIVE subset (>=2 gn-compatible candidates)** -- *my proposed mechanism, on my
> proposed can-fail test.* **A CI-separated harm, not a null.** Neighbours: `..._tiebreak_under_
> centering_v2` **VACUOUS**, `..._cb_tier_error_anatomy_v1` **RANKING_DOMINATED**.
>
> **BUT NOT "CUE-BASED RETRIEVAL IS WRONG":** the brain side is pinned as an **ORDERING**, and the
> map says *"the cue weights and the activation equation are UNPINNED."* **A brain-faithful
> mechanism lost to our invented arithmetic -> `presumed impl-bug until proven structural`.**
> **The open question is a DIAGNOSIS of an existing artifact -- *why did our ACT-R activation lose
> 13.5 points?* -- not a build.**

## ~~3. T2 -- WHO DOES "HE" REFER TO~~ **(superseded version, kept visible)**

Corrected floors, from the **same run** that measures our resolver (never across runs):
**our resolver 0.7193** vs **most-recent-mention 0.5614** and **subject-position-majority 0.3860**.

**➡️ WE ARE ALREADY ABOVE BOTH FLOORS. This is a WIDEN-THE-MARGIN step, not a rescue** -- and the
honest gap is **oracle 0.9298 vs earned 0.6842**, not "we lose to pick-the-last-subject." *The
hazard is live regardless: `frame_induction` already LOST to a position-majority baseline, 0.833 vs
1.000.*
Fix: replace our invented arithmetic with genuine parallel cue-based retrieval with similarity-based
interference, scored by the semantic comparator rather than token overlap. **Test at n in the
hundreds, not n=10.**

## 4. T3 -- 🔴 **SUPERSEDED: THE SWITCHES ARE ALREADY ON. THE REAL DEFECT IS SHARPER.**

> `reading_grounding_loop.py:103` -- `GRADED_COMPARATOR` defaults to **`"1"` = ON**; `:683`
> `graded_query` follows it. And `exp_graded_path_vs_orthographic_floor_v1/metrics.json` carries a
> field named **`premise_correction`**: *"GRADED_COMPARATOR is default-ON ... NOT default-OFF as the
> dispatch brief assumed"* -- **a PRIOR dispatch made my identical mistake.**
>
> **THE REAL DEFECT:** `canonicalize_fast` honours the switch (`:821-825`); **`canonicalize` `:776`
> hardcodes `np.sign(new_raw_sum)` with no branch** -- and **the grounding decisions (`:1330`,
> `:1593`) call the one that cannot do a graded query**, while `definitional_extraction.py:19` says
> it is *"the loop's ONLY grounding signal."* So the field is GRADED and the query is BINARY -- the
> configuration `:663` itself calls **"worse than either"**. Unreached effect, measured: **0.6997 vs
> 0.6395, +0.0602 CI [+0.0440,+0.0762]**. *Not transferred, not measured on the grounding task.*
> **`notes/T3_the_live_grounding_path_reads_a_GRADED_field_with_a_SIGNED_query_2026-08-21.md`**
>
> ## 🅃5 -- **AND FOLLOWING T3 FOUND THE BIGGER ONE (owner-authorised expansion)**
> **`A6_TRIGRAM_ONLY` -- pure spelling, ZERO substrate signal -- beats the meaning read-out
> `A1_BASE` at hit@1 `0.087` vs `0.048`, CIs NON-OVERLAPPING** (0.078 > 0.055), identical
> items/pool/gold/scorer. **And `A8_MAXORTHO`, documented as *"the strongest available zero-meaning
> attack"*, is `_z(trig) + _z(pre)` -- a SUM, scoring `0.061`, 30% BELOW its own component.**
> ⚠️ **The deciding check -- tie mass -- was never computed in EITHER cell; it is RUNNING NOW
> (`tools/orthographic_floor_tie_mass_v1.py`).** Median rank is identical (37.0 vs 37.0), so the
> whole effect lives in the top slot, which is the most tie-sensitive statistic there is.
> **`notes/T5_the_orthographic_floor_drilled_pure_SPELLING_beats_meaning_and_the_MAXORTHO_arm_is_not_a_MAX_2026-08-21.md`**

## ~~4. T3 -- TURN ON THE BETTER WORD CODES~~ **(superseded version, kept visible)**

Three switches are **already built and already default-OFF**. Live path runs `d=256` quantised at
**0.6395**; at probe scale the graded versions read **0.7030** and **0.78225**.
**⚠️ SAY IT PLAINLY: this is a WIRE-IT test. Re-measuring a known effect on the live path is not a
discovery, and must not be written up as one.**
**MANDATORY:** report the **between-projection-draw sd** (0.0090 at d=256) beside the CI -- item
bootstraps are blind to shared-randomness variance.

## 5. T4 -- **DRILL THE NEGATIVES** (owner instruction, tonight)

> ### ✅ **T4 RAN, AND ITS BEST FINDING IS A BUG IN T4 ITSELF.**
> **The archive-wide question** -- *"is saving scores-but-not-outputs one careless cell or how we
> build?"* -- **produced two numbers from scans biased in opposite directions, 96.5% and 7.0%.**
> **BOTH ARE VOID.** `tools/audit_archive_reanalysability.py` v1 read only the **first 2 MB** of
> each sibling file; anything larger raised `JSONDecodeError`, was swallowed by an
> `except: continue`, and **counted as "saved no outputs."**
> **➡️ THE BIAS RAN EXACTLY BACKWARDS: cells that persisted the MOST data were the ones most likely
> to be called defective.**
>
> **CAUGHT BY THE TRIPLE-CHECK RULE, ON THE ONE CELL I NAMED.** I accused
> `exp_context_vector_signal_v1` of being load-bearing-but-unrecoverable. **False** -- its
> `_pass_encounters.json` is **4,011,507 bytes** and a corrected read finds a **167-item** list.
> **And my second charge was also wrong:** the cell **documents its own amendments with reasons and
> preserves the unamended verdict** (`prereg_literal_primary = MIDDLE_BAND_CEILING_LIMITED`), plus
> `no_leak_violations: 0`, `arms_differ_verified: true`, per-arm digests. *That is well-instrumented
> work. I had conflated the artifact with a separate incident about an AGENT not disclosing a
> denial.* **Both accusations withdrawn.**
>
> **THE DURABLE OUTPUT: the tool now runs a POSITIVE CONTROL before it can report any absence** --
> negative control, nested-list, a `>2 MB` regression fixture, and a live check on the cell that
> exposed the bug; `main()` calls it unconditionally. *Verified in both directions: reintroducing
> the cap reproduces the swallowed error.*
> **`notes/T4_the_archive_saves_scores_not_outputs_bounded_between_7_and_96_percent_2026-08-21.md`**
>
> **⚠️ CORRECTED FIGURES STILL PENDING.** v2 (whole-file reads) was correct but starved the machine;
> v3 credits large files by SIZE without parsing. **Until it lands, quote NO archive-wide number.**

> ### 🔴 **T4's OWN HEADLINE WAS WITHDRAWN -- MY SCANNER'S BIAS RAN BACKWARDS.**
> I reported *"96.5% of scoring cells saved no outputs"* and *"at least 251 genuinely lost, 61 of
> them HARD_PASS"*. **`tools/audit_archive_reanalysability.py` v1 read only the first 2 MB of each
> sibling JSON**, so any file **bigger** than that raised `JSONDecodeError`, was swallowed by an
> `except: continue`, and **was counted as "saved nothing."** *The cells that persisted the MOST data
> were the ones most likely to be called defective.*
>
> **CAUGHT BY THE TRIPLE-CHECK RULE, ON THE ONE CELL I NAMED.** `exp_context_vector_signal_v1`'s
> `_pass_encounters.json` is **4,011,507 bytes** and holds a **167-item** population. *It saved its
> data. I called it unrecoverable.* **And my second charge against it -- that its HARD_PASS was
> irregular -- is also withdrawn:** the cell **documents its amendments with reasons and preserves
> the unamended verdict** (`prereg_literal_primary = MIDDLE_BAND_CEILING_LIMITED`), alongside
> `no_leak_violations: 0`, `arms_differ_verified: true`, per-arm digests, `n_encounters: 8282`.
> *I conflated an agent's non-disclosure incident with a defect in this artifact.*
>
> **THE FIX IS IN THE CODE, NOT THE NOTE** -- `--self-test` with four cases (negative control,
> nested list, **a >2 MB regression fixture**, and a live control on the cell that exposed the bug),
> and `main()` calls it **unconditionally**, so no absence figure can come from an unverified
> detector. Verified both ways: it passes with the fix, and re-introducing the 2 MB cap reproduces
> the swallowed `JSONDecodeError`. *v2 (read whole files) was correct but starved the machine for
> 20+ minutes; **v3 credits large files by SIZE without parsing** -- a stated heuristic that errs
> toward UNDER-counting the defect, the conservative direction.*
>
> **➡️ FOURTH APPLICATION OF THE ONE PATTERN THAT IS 4-FOR-4 TONIGHT: EVERY CAUTION WRITTEN AS PROSE
> WAS LATER VIOLATED; EVERY CONTROL WRITTEN AS CODE CAUGHT SOMETHING.** *Corrected figures pending;
> the T4 note's table is marked void.*

Three negatives are open, and **the first is mine from tonight**:

1. 🔴 **"THE DECISIVE TEST" MEASURED NOTHING, AND ITS RE-RUN WAS KILLED.** It reported a clean
   double null -- `GROUNDED(last)=0` on both foundations. **Both zeros are probe artifacts.** The
   corpus was exhausted (asked 3x1200, got 1540 and 1600 = `1200+340+0`), so the grounded count was
   read off a `read()` call that **processed no text**; and it printed the LAST call's count while
   summing sentences across all three, discarding two thirds of the experiment.
   *`substrate.py:949` -- the repo's own self-test -- asserts `res.n_sentences > 0`. My probe omitted
   it.* **Standing rule, verbatim: a null that is exactly zero is a reachability failure, not a
   result.** Two independent bugs drove it to 0.0 and the two arms agreeing made it look robust.
   **RE-RUN with the guard; the corrected script exists at
   `tools/diagnose_read_with_loaded_foundation.py`.**
2. **THE REFUSAL ASYMMETRY IS UNEXPLAINED AND IS PROBABLY THE REAL SIGNAL.** Same reading, two
   foundations: **v1 (4322 anchors) refused 525 times; v2 (1415 anchors) refused 11,930**, 98.7% of
   them `TAUTOLOGY_NO_ANCHOR`. *A quality-filtered foundation refusing 22x more often is either the
   most informative thing in that run or a second bug.* **It survives the probe defect above,
   because refusals accumulate over the reads that DID happen.**
3. **54% OF THE CODE IS UNREACHABLE FROM ANY ENTRY POINT** (83 of 155 modules, union of 17 candidate
   drivers). *The WIRE-DON'T-ISLAND rule exists precisely for this and the number is still 54%.*

---

## 6. HOW BRAIN-FOUNDATIONALITY GETS TRACKED (owner instruction)

**Every thrust above already carries its fidelity label in the table, and no result may be written
up without it.** Three labels, and they are not interchangeable:

| label | meaning | tonight |
|---|---|---|
| **EQUATION PARITY** | we compute what the brain computes | T3 |
| **FUNCTION PARITY** | right job, brain math UNPINNED -- *say so, every time* | T1, T2 |
| **OUR INVENTION UNDER TEST** | we made it up; testing it is fine, **calling it brain-derived is barred** | T2's β/λ arithmetic |

**The failure this prevents is on record:** VSA binding -- *our core operation* -- was labelled
brain-derived across briefs and organ rows while the binding problem is **open in the literature**.
**Unfalsified is not confirmed.**

## TLDR

You asked for an overnight plan with a few high-priority pieces, brain-faithfulness tracked, and
negatives drilled. Here it is, and **it opens by overturning yesterday's top item.**

Yesterday I decided "sleep" was the most important thing to build, because the organ map says it is
the one place where we know the brain's exact formula and have none of it. That quote is right. **But
the same page says the sleep test cannot run yet** — you can't measure whether new learning damages
old learning when the system reads **the same four documents over and over forever**. And half of
that sleep organ is a known dead end at our size; the textbooks predict it won't help until we're a
thousand times bigger.

**So tonight's first job is the thing that unblocks it: teach the system to choose what to read
next.** Right now it can't, which is why what it knows is 64% biology. The organ map's bluntest line
is that this is *"why the system cannot notice what it does not know."* We already own most of the
pieces.

Then three more, deliberately different so nothing sits idle: **improving how it works out who "he"
refers to** (we're already better than the cheap tricks there, so this is widening a lead, not a
rescue); **switching on better word codes that are already built but turned off** (honest: that's
flipping a switch, not a discovery, and I'll write it up that way); and **drilling into three
negative results**, starting with one of my own from tonight that turned out to measure nothing at
all — it read "zero" off a step that never processed any text.

Every item says up front whether we're copying the brain's actual formula, just doing the same job
our own way, or testing something we invented. **Those are three different things and blurring them
is how we've fooled ourselves before.**

## QUESTIONS

None — but one flag: **F5, the "notice when a sentence doesn't fit" work whose test set I finished
tonight, is deliberately NOT in tonight's plan.** The organ map queues it later and gates it behind
work that isn't done. The 120 hand-scored sentences keep. If you'd rather I chase it now anyway, say
so and I'll move it up — it's your call, not the map's.

## NEXT STEPS

1. **T1 first** — it unblocks sleep, which is the item Q95 most points at.
2. **T4 in parallel** — re-run the corrected decisive test and drill the 22x refusal asymmetry.
3. T2 and T3 are independent and can proceed whenever T1 is waiting on a run.
