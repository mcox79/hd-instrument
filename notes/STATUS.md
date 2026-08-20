# STATUS

AS OF: 2026-08-20 AUTOLOOP ARMED, ~15 CONTINUATIONS IN | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | **NOTHING IS RUNNING; every thread opened tonight is CLOSED or CORRECTED** | **ONE VERIFIED RESULT (`keep_noting_grounded`) AND ONE OWNER DECISION (board Q74)** | **THE PLAN `notes/BUILD_PLAN_post_audit_2026-08-19.md` IS CURRENT AND CARRIES EVERYTHING -- READ ITS FIRST BLOCK, THEN `## 🧭 RESUME HERE` BELOW**
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` (**THE PLAN; READ SEC 6.18 FIRST -- it supersedes the
step hunt. 6.16 holds the PRE-COMMITTED decision branches; 6.15 the five gated steps**) ->
HERE -> `COMPACTION_HANDOFF_2026-08-17.md` -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## POSITION

## 🧭 RESUME HERE -- **REWRITTEN 2026-08-20 (LATEST). BOTH BOARD Qs ANSWERED; NEXT STEP UNSTARTED.**

> ### ➡️ THE ONE UNSTARTED ACTION
> **Turn on `StructuralEncoder` (additive, default-off) and measure context-as-STRUCTURE against
> context-as-BAG-OF-NEARBY-WORDS.** Cleared to run: three-read check returned 1 archive hit / 0
> landed, no ORGAN_MAP prohibition, no registry claim; and the organ WORKS (norms 22-33 vs the bag's
> 32.68, front-end assets present).
> **⚠️ PASS TARGETS AS LEMMAS (`content_lemmas` output), NOT SURFACE FORMS -- a mismatch fails
> SILENTLY as a zero vector, and an all-zero arm scores median rank 1.0, i.e. a fake breakthrough.
> That cost me a wrong claim tonight and one command to catch.**
>
> ### ⚖️ THE DISCRIMINATOR WAS AMENDED BY THE OWNER, DATED, BEFORE ANY ARM WAS SCORED
> *Owner 12:31Z: "You don't approach a textbook like a story... it's not the same kind of learning."*
> **SUPERSEDED:** *structure must help narrative MORE than exposition or it is only a better encoder.*
> **CURRENT:** judge structure on **EXPOSITORY prose**, where our fact-recall task fairly measures
> what the text was there to teach. **Narrative is a separate OBSERVATION, not pass/fail.**
>
> ### 🚨 AND THAT AMENDMENT DEMOTES TONIGHT'S HEADLINE "GAP"
> I reported *textbook grounds 12.6%, Sherlock 0.7%, therefore a fidelity failure.* **Our task is
> FACT RECALL -- expository-kind knowledge.** Scoring what a novel taught with a textbook's metric is
> a METRIC infidelity. **We have NO measure of narrative-kind learning, so that claim is currently
> UNFALSIFIABLE -- do not quote it as a finding.**
>
> ### 📉 CLOSED SINCE THE LAST REWRITE
> - **D7 / successor representation: DO NOT WIRE.** Faithful to its pinned closed form, but on
>   reading order plain 1-step co-occurrence beats it **18.5 vs 45.0** (SR-ONE_STEP **+25.5**, CI
>   [+21.0,+29.0]). SR is pinned for NAVIGATION; mapping it onto text was OUR invention and did not
>   transfer. *(Caveat: ONE text sample with CIs over 408 pairs -- the script says "seeds" and is
>   wrong; only the uniform arm was seeded.)*
> - **Owner Q74 answered: SURPRISE DOES NOT SELECT.** High-, low- and random-surprise halves are
>   indistinguishable at matched count (all +0.0, CI [+0.0,+1.0]); only VOLUME moves it (ALL-NONE
>   **-8.0**, CI [-11.0,-5.0]). **Mean surprise 0.4206-0.4252 against a 0.5 no-information floor --
>   the signal is ~4% from chance, so there was nothing to select on.**
> - **ORGAN_MAP gap list was 2/5 STALE** (D7, H2 labelled MISSING while both exist). Corrected in
>   place; all 39 organ sections re-audited; contradictions now NONE.
>
> ### 🧠 THE FIDELITY AUDIT THE OWNER ASKED FOR: 6 of 8 negatives had one; the 2 gaps are filled
> **And filling one INVERTED it:** "the sum beats any single encounter" is CONSISTENT with pinned
> ORGAN_MAP B1' (*LATL conceptual combination is approximately ADDITIVE*). **The first POSITIVE
> fidelity result of the session, filed for hours as a dead lead.**

## [PREVIOUS REWRITE] **ONE RESULT, FOUR RETRACTIONS, ONE DECISION.**

> ### ✅ THE ONE VERIFIED RESULT -- `keep_noting_grounded` (shipped, ADDITIVE, DEFAULT-OFF)
> **The substrate used to seal a word's representation the instant it grounded: 0 of 60 grounded
> terms gained a single trace over 14,000 further sentences, `cos(profile_16k, profile_2k)` =
> 1.000000.** Two gates enforced it (`Library.flag`'s `return False`, and a terminal short-circuit in
> `process_sentence` that fires BEFORE `is_gap`), and the read-out discarded the fix a third time
> until `profile()` was taught to merge POST-grounding traces only.
> **VETTED: 3 seeds x 2 corpora, paired on identical probes, all separated.**
>
> | corpus | DEFAULT | shipped fix |
> |---|---|---|
> | `simplewiki` (3 seeds) | 4.71x / 5.00x / 5.00x | **2.57x / 3.00x / 3.22x** |
> | `textbook_biology_2e` (3 seeds) | 5.45x / 5.63x / 4.76x | **2.60x / 2.66x / 2.74x** |
>
> Phase slope **+1.410 -> +0.667** per e-fold. Post-only BEAT whole-pile in 3 of 3 (the double-count
> was mildly hurting). **⛔ STILL LOSES TO WORD-COUNTING -- the curve bends, it does not cross.**
> **📋 BOARD Q74 IS THE ONLY OWNER DECISION: make it the default? Not blocking.**
>
> ### ⛔ FOUR THINGS I CLAIMED AND THEN RETRACTED. DO NOT RE-QUOTE THE FIRST VERSIONS.
> 1. *"The `gap_detector` ablation is inert; prior results need re-checking."* **FALSE ALARM,
>    WITHDRAWN.** The organ is CORRECT (positive control: seed-known False 8/8, grounded False 8/8,
>    pending True 8/8). It says "gap" 8,053/8,053 only because two earlier filters remove everything
>    it would reject. **Correct and redundant -- a POSITION result. No audit needed.**
> 2. *"Accumulation is the problem, 4th independent time."* **WITHDRAWN.** That rested on the anchor
>    MARGIN. On the task the sum BEATS any single trace (+13.0, CI [+6.0, +17.5]).
> 3. *"Our code is 4-12x too diffuse, so the projection is the defect."* **OVER-ATTRIBUTED** -- an
>    ordinary text encoder (MiniLM, d_eff 91.6) sits there too, under a different formula.
> 4. *"PBV discarded recoverable signal, so build cross-situational tracking."* **CIRCULAR** (margin
>    IS the grounding criterion). Re-tested properly: pooling scores 0.75-0.80x of a SINGLE encounter,
>    so the mechanism would destroy signal. **DO NOT BUILD IT.**
>
> ### 🧠 THE STANDING LESSON, NOW A RULE IN CLAUDE.md
> **A statistic the mechanism OPTIMISES is not an outcome -- it may DIAGNOSE, never DECIDE.** Anchor
> margin, trace coherence and effective dimensionality each produced a confident mechanistic story
> the held-out task then refused. *Three of tonight's more confident claims died to one question:
> "what does the TASK do under this intervention?"*
>
> ### 📌 THE BIGGEST NEWLY-VISIBLE GAP (not acted on, deliberately)
> **This substrate is an EXPOSITORY-TEXT learner.** Grounding rate at 8,000 sentences:
> textbook **12.6%**, simplewiki 3.6%, Little Women 0.8%, Sherlock **0.7%** -- and it is NOT exposure
> (encounters/item 4.16 vs 3.66). **Children acquire most vocabulary from exactly the narrative
> regime this substrate cannot use.** *The obvious fixes were tested and rejected; this needs fresh
> judgement, not another mechanism hunt at 3am.*

## [PREVIOUS] RESUME BLOCK -- **THE OWNER GAVE TWO DIRECTIONS AND BOTH CHANGED THE PLAN.**
> **1. "adjusting a belief ... integrate where it needs to go" (01:31Z).** Answered: belief revision
> in `hd_fact_store` is REAL and CORRECT and **has never once fired** -- 668 facts, 668 distinct
> (subject, relation) keys, **0 ever contested**. Chasing why found worse: **the fact store holds no
> facts.** Its whole relation vocabulary is `KNOWN_WORD` (380, object always the constant `CORE`) and
> `GROUNDED_MEANING` (288). A constant cannot be contradicted.
> **2. "be brain foundational -- don't wire organs because you think it could help" (02:14Z).** This
> **invalidated my own recommendation.** I had proposed wiring contradiction detection *"because it
> feeds the revision path"* -- a utility argument naming no brain structure. And the machinery under
> it, **AGM contraction, is 1985 formal logic, not neuroscience.** The brain's actual mechanism is
> **RECONSOLIDATION** (retrieval makes a trace labile, then re-stores it -- Nader/Schafe/LeDoux 2000),
> and it returns **0 hits in 8,836 archived cells, 0 in 151 `hdlab` modules, 0 in ORGAN_MAP.**
> *We built the philosopher's version of changing your mind and never the brain's.*
> **⛔ CONSEQUENCE: "go fill the fact store" is DOWNGRADED from next-step to diagnosis** -- the store
> is an addressable symbolic database where cortex has a distributed representation, so enriching it
> is not a brain-foundational goal.
>
> **➡️ CURRENT TOP ITEM, CHOSEN BECAUSE ORGAN_MAP PINS IT:** divisive normalisation over a POPULATION
> POOL (*"graded competition implemented BY the normalisation pool, not a hard argmax"*). We tested
> competition twice and both times WITHIN an item (k-WTA on one trace; per-trace L2). **Smoke says no
> win** -- DIVNORM +1.346 vs SUM +1.161, ties its shuffled-pool control, and does NOT concentrate the
> code (28.5 vs 28.9). **The full sweep decides; the smoke must not be quoted** (I published smoke
> numbers as a finding once today already and had to correct it).
>
> ## 🧭 RESUME HERE AFTER COMPACTION -- written 2026-08-19 at the end of the fidelity-audit session
*Written deliberately short. The five commits named here are the record; this block only says where
to stand. **The LEDGER and `git log` OUTRANK anything I remember.***

**STATE: CLEAN. Nothing is running. Nothing is half-done. No orphaned processes, no uncommitted work
of mine.** HEAD is `c6710d753`. The last five commits are the whole of this session's output:

    c6710d753  correct a smoke-numbers finding, answer Q72 with CIs
    3cf399a6e  two archive-found caveats on claims committed earlier today
    e027ccd11  complete the brain-fidelity audit on all three open negatives
    0b987588d  record held-out leak fault and archive-mining finding
    ea62d96a2  fidelity audit on the biggest negative + the honest accounting

**WHAT WAS FINISHED.** The owner asked that every negative get a brain-fidelity check. All three
that had none now have one. **Three of my four explanations were REFUTED by their own pre-committed
controls** -- see the audit block further down. The one surviving account: *a write gate chooses
WHICH counts get added and cannot change that the code IS a count.*

**⛔ THREE CORRECTIONS LIVE IN THIS FILE. DO NOT RE-QUOTE THE SUPERSEDED VERSIONS:**
1. **"Four of four refuted" is WRONG -- it is THREE of four.** The familiarity hypothesis was NOT
   refuted; I had read SMOKE numbers (161 terms). At full n (1,590) the slope separates negative:
   mean -0.0035, CI [-0.0052, -0.0018], 63% of words.
2. **Never quote "spreading reading across corpora made it worse."** Point estimates 91.0 -> 106.5
   look like a negative; the difference is **+15.8, 95% CI [-10.0, +42.5], NOT separated.** Passive
   breadth is **UNTESTED at this n**, not a negative.
3. **"Our code is 4-12x too diffuse" is OVER-ATTRIBUTED.** A prior cell measured MiniLM -- an
   ordinary working text encoder -- at d_eff 91.6, using a **different formula** for participation
   ratio than today's diagnostic. The geometry stands; blaming OUR design does not, yet.
   **⤷ RESOLVED, AND THE CORRECTION ITSELF NEEDED CORRECTING -- SEE THE BLOCK BELOW. The invalid
   comparison was real (formula AND population both differed), but "probably normal for text" was
   NOT supported: measured on the same formula we are 2.60x MiniLM, and on a fully matched
   comparison we are MORE diffuse than the raw counts we are built from.**

**➡️ NEXT STEPS, IN THIS ORDER, AND THE FIRST ONE RESOLVES CORRECTION 3:**
1. **Recompute our participation ratio under BOTH formulas** -- `(sum s)^2/sum s^2` over singular
   values (the prior cell's) and `1/sum(v^2)` over variance shares (today's) -- on our profiles AND
   on a text-encoder reference, so the MiniLM comparison becomes legitimate. Until then we cannot
   say whether we are unusual or merely normal-for-text.
2. **Test the gap-targeted growth loop on the current substrate.** It is the only thing in this area
   with a clean prior win (`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`, HARD_PASS,
   coverage 0.50 -> 0.79, real-vs-shuffle AUC 0.8924 vs 0.5122) **and it is the owner's own idea**
   -- the load-bearing half of Q72 is "patchy", not "another textbook".
3. **Leave the write gate alone.** Four explanations tested; tuning thresholds cannot reach it.

**🔁 THE HABIT THAT PAID OFF MOST AND SHOULD CARRY FORWARD: query the RESULTS archive before
building, not just the code registry.** `python tools/experiment_index.py query "<kw>"` -- it found
that today's write-gate negative had been measured a month earlier, that a prior residual gate
already recorded skip=0.00, and both of the corrections above. **`substrate_query.sh` returns zero
bytes and exits 0 -- never use it.**

## 📖 WHERE WE ARE, IN PLAIN WORDS -- added 2026-08-19 because everything below this is jargon
*The owner answered two board questions with "too jargony so I don't really know how to help".
That was about the board, but this file has the same problem and the owner reads it. Everything
below is unchanged; this block is the translation. **If the two disagree, the blocks below are the
record and this one is the summary.***

**THE GOAL.** Get a system to learn what words mean by reading, with no language model doing the
understanding -- every step has to be inspectable.

**WHERE IT ACTUALLY IS.** It reads text, decides which words it does not know, and writes down what
it learns so each fact can be traced back to the sentence it came from. That part works. **What it
cannot yet do is use what it learned to answer a question better than a crude word counter can.**

**THE ONE THING TO UNDERSTAND ABOUT TODAY.** Give the system a sentence it has never seen and ask
which word belongs in it. A crude method -- just counting which words tend to appear near each
other -- narrows it to about the top 15 out of 450 candidates. **Our system gets to about 70-80.**
Today I tried three different clever ways to close that gap. All three lost. *Three different
clever ideas losing to the crude one usually means the problem is not the thinking -- it is what
went in.*

**THE MOST USEFUL THING FOUND TODAY, and it is a plumbing problem, not a clever one.** The system
stops taking notes on a word once it decides it knows that word -- like a student who stops writing
things down the moment a topic feels familiar. So the words it meets constantly have the fewest
notes: for the word "century" it wrote 7 notes across 92 sightings. **Roughly 3 of every 10
encounters are never recorded, and that alone costs more than all three clever ideas were trying
to win.**

**WHAT IS ON THE OWNER'S DESK.** Two questions, in plain language, on the board: should it keep
taking notes after it thinks it knows a word, and should we change what we feed it rather than how
it thinks.

**HOW MUCH OF TODAY WAS ME CORRECTING MYSELF: a lot, and deliberately so.** Several numbers I
published were wrong and were caught by controls -- a comparison built on text the system had never
read, a measurement inflated by comparing something to a copy of itself, and a claim that our
storage "destroys information" which turned out to be mostly "never wrote it down". *Each is
corrected at the original text below, not just above it.*


# â±ï¸âž¡ï¸ 2026-08-19 -- THE PLAN IS `notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT. IT IS CURRENT.
**The autoloop is ARMED at 200 and is executing that plan. It is rewritten every continuation and
carries every number below with its controls. THIS BLOCK IS A POINTER, NOT THE RECORD.**
*Stop the loop with `python tools/autoloop.py disarm`.*

## 🔴 2026-08-19 -- **THE POSITIVE CONTROL FAILED AND IT CONDEMNS MY EARLIER PROBE: THE BASELINE**
## **AND OUR ARM WERE BUILT ON DIFFERENT TEXT. THE "2x GAP" AS STATED IS CONFOUNDED.**
`scratch/diag_does_coverage_explain_the_gap.py` was built to separate coverage from quality. Its
first output was the control, and the control did not hold: **`PROJ_COOC_ALL` reads median 17.0
where the earlier probe measured 42.0 for the same arm.**
**⛔ CAUSE, AND IT IS A REAL DEFECT IN THE EARLIER PROBE: it built the counter from
`read_split = pool[:N_READ]` -- MY slice of the corpus handle -- while our profiles are built from
`sub.state.sentence_pool`, THE SENTENCES THE FORAGER ACTUALLY CHOSE. Those are different sentence
sets. The baseline was scored on text the substrate had partly never read.** *So the earlier
"compression costs 20 -> 42, ours costs 20 -> 81" decomposition is void. Same class as the
corpus-arithmetic bug from earlier today: I assumed a slice was what the substrate consumed.*

**✅ ON MATCHED TEXT -- both arms from the substrate's OWN pool -- the decomposition is cleaner and
says something different:**

| arm (256 dims, same items, same candidates) | hit@10 | hit@50 | **median** |
|---|---|---|---|
| **PROJ_COOC_ALL** (every occurrence) | 0.4247 | 0.7057 | **17.0** |
| **PROJ_COOC_TRACED** (only what we recorded, 68.8%) | 0.3211 | 0.5251 | **46.0** |
| **OURS** | 0.1304 | 0.3779 | **81.0** |

**➡️ COVERAGE IS THE DOMINANT COST, NOT A SIDE ISSUE: 17 -> 46 from recording only 68.8% of
occurrences. The remaining 46 -> 81 is real but SMALLER than the coverage penalty.**
*Both factors survive; their sizes have swapped. What I first called "we destroy information" is
the minority term, and "we never wrote it down" is the majority one.*
**🎯 THIS SHARPENS BOARD Q69 CONSIDERABLY: "keep recording traces after a word grounds" is now the
single largest measured lever on this representation, worth more than everything the three closed
mechanism lines were chasing.** *Still an owner call -- it changes core reading behaviour and its
cost profile -- but it is no longer a tidy-up, it is the main event.*

## 🟠 [ITS "31% NEVER RECORDED" STANDS; ITS SIZE-ORDERING IS SUPERSEDED ABOVE] 2026-08-19 -- **PARTIAL CORRECTION TO THE BLOCK BELOW, AND MY VERDICT STATISTIC WAS WRONG.**
## **WE RECORD ONLY 69% OF OCCURRENCES, AND THE SHORTFALL IS CONCENTRATED ON FREQUENT WORDS.**
I published "our representation is DESTROYING information a random matrix preserves". Reading the
code then showed `context_vector(graded=True)` returns the RAW SUM of per-word bipolar draws --
**a LINEAR random projection.** By linearity, summing a term's per-sentence vectors should EQUAL
projecting its summed counts, so OURS and PROJ_COOC should be the same object and there is nothing
for a "quality" difference to live in. Unless they are built from different OCCURRENCES. Measured:

| traces recorded vs sentences containing the term | |
|---|---|
| median ratio | **0.958** |
| mean ratio | 0.802 |
| **OVERALL (total traces / total occurrences)** | **0.688** |
| least covered | `century` 7/92 = 0.076, `european` 5/44, `ways` 5/41, `unite` 7/50 |

**⛔ THE SHORTFALL IS SYSTEMATIC AND FREQUENCY-DEPENDENT: rare terms are covered almost completely,
FREQUENT terms are covered barely at all.** *That is the loop working as designed -- a word stops
being a gap once it grounds, so it stops accruing traces -- but the consequence is that **the terms
with the MOST evidence available have the LEAST recorded**, which is exactly backwards for
estimating a profile.*
**⚠️ AND MY PRE-REGISTERED VERDICT STATISTIC WAS THE WRONG ONE. I gated on the MEDIAN ratio (0.958,
"coverage is not the story"), when the quantity that matters is the FREQUENCY-WEIGHTED TOTAL
(0.688) and its CORRELATION WITH FREQUENCY. The median hides a systematic truncation by
construction.** *Third time this session a threshold I wrote was badly specified. The pattern is
always the same: I pick a statistic that is easy to compute rather than the one that answers the
question.*
**➡️ SO BOTH MECHANISMS ARE LIVE AND NEITHER IS CLEAN: ~31% of occurrences were never recorded
(concentrated where it hurts most), AND that alone may not account for a 2x median-rank gap. The
"destroys information" claim below is NOT refuted but is NO LONGER THE SOLE EXPLANATION and must
not be quoted as one.** *The clean next test: rebuild PROJ_COOC from ONLY the recorded traces. If
it then matches OURS, coverage explains everything.*

## 🔴🔴🔴 [SEE THE PARTIAL CORRECTION ABOVE -- COVERAGE IS ALSO IN PLAY] 2026-08-19 -- **A RANDOM PROJECTION OF THE CO-OCCURRENCE COUNTS BEATS OUR REPRESENTATION**
## **BY 2x AT IDENTICAL DIMENSIONALITY. WE LOSE MORE THAN COMPRESSION EXPLAINS.**
`scratch/diag_is_our_vector_a_compressed_counter.py`. The question the whole session pointed at and
nobody had asked: both sides use co-occurrence, so **is our representation simply a LOSSY VERSION
of the baseline that keeps beating it?** Matched dimensionality, one variable.

| arm | hit@1 | hit@10 | hit@50 | **median rank** |
|---|---|---|---|---|
| **FULL_COOC** (6,145 dims) | 0.1137 | 0.3478 | 0.7124 | **20.0** |
| **PROJ_COOC@256** (same counts, RANDOM projection) | 0.0803 | 0.2475 | 0.5619 | **42.0** |
| **OURS** (accumulated context vectors, 256 dims) | 0.0569 | 0.1304 | 0.3779 | **81.0** |

*POSITIVE CONTROL: FULL_COOC median 20.0, against the 15-20 two other cells measured. Same thing
being scored.*
**⛔ THE PRE-REGISTERED THIRD BRANCH FIRES, AND IT WAS THE ONE I THOUGHT LEAST LIKELY. Compression
to 256 dims costs 20 -> 42. OUR representation at the SAME 256 dims costs 20 -> 81. So HALF THE
GAP IS DIMENSIONAL AND HALF IS OURS: a RANDOM PROJECTION of the same counts beats a carefully
accumulated context representation by 2x on median rank.**
**➡️ THIS IS THE FIRST SPECIFIC, FIXABLE DEFECT THE SESSION HAS FOUND IN THE REPRESENTATION,
rather than another ceiling.** Everything until now said "the representation is the limit"; this
says **the representation is DESTROYING information that a random matrix preserves**, which is a
much stronger and much more actionable claim.
**🧠 AND IT GIVES QUANTITATIVE WEIGHT TO AN EXISTING QUALITATIVE FINDING: `notes/ORGAN_MAP.md` §1
already records 34 `np.sign` call sites across 12 modules and calls the result "mathematically a
PROTOTYPE EXTRACTOR -- the signature of a degrading ATL hub". A sign-quantised accumulation would
lose exactly what a linear random projection keeps.** *That is now the leading hypothesis for the
2x and it is directly testable: rebuild the profile WITHOUT the sign step and re-measure.*
**⚠️ SCOPE: one seed, one corpus, 4,300 sentences, 223 candidates, held-out only. The direction is
large but this is a single measurement and the sign hypothesis is UNTESTED.**

## ⛔ 2026-08-19 -- **WRITE-GATE CELL LANDED, 3 SEEDS. FORMAL VERDICT: (C) AND (D) BOTH FIRE.**
## **READING (A) IN 0 OF 54 CELLS. FLOOR CLEARED IN 0 OF 54.**
`exp_predictive_write_gate_v1`, 1,064 s, 3 seeds x 6 thresholds x 3 k = 54 cells, read by a script
written BEFORE the result existed (`scratch/read_write_gate_result.py`).

| seed 7 | hit@10 | hit@50 | median | skip |
|---|---|---|---|---|
| ACCUMULATE | 0.1533 | 0.3433 | 115.5 | 0% |
| GATED@0.25 | 0.1533 | 0.3533 | 116.0 | 4.7% |
| GATED@0.40 | 0.1600 | 0.3300 | 113.5 | 26.9% |
| GATED@0.50 | 0.0833 | 0.2867 | 138.5 | 72.6% |
| GATED@0.60 | 0.0800 | 0.1733 | 222.5 | 92.1% |
| **COOC_floor** | **0.3667** | **0.7233** | **20.5** | -- |

**THE SHAPE IS THE ARGUMENT: at low thresholds the gate barely skips and MATCHES accumulation; as
it skips more it MONOTONICALLY DEGRADES. There is no window where selectivity helps.** *At 0.60,
GATED and RANDOM_SKIP are IDENTICAL to four decimals on every metric -- at that skip rate the two
selectors have nothing left to disagree about.*
**➡️ AND THE TWO NEGATIVES SAY DIFFERENT THINGS, WHICH IS WHY BOTH ARE REPORTED:**
**(C)** the pinned residual rule does not help AS WIRED HERE -- a real negative about this wiring.
**(D)** no arm clears the floor at any threshold or k, so the representation is not competitive
*regardless* of what happens between the arms.
**✅ THE PINNED EQUATION IS NOT REFUTED, AND THE DISTINCTION IS LOAD-BEARING.** Measured the same
day: profiles DO predict their own contexts 10.4% better than an unrelated term's, CI-separated.
**So the residual is real but too UNIFORM to threshold (sd 0.076 about a mean 0.44). Predictive
coding needs a predictor sharp enough that being wrong is INFORMATIVE. Ours is evenly mediocre, so
its errors carry no ranking.** *That is a statement about our predictor, not about the brain's rule.*

## ⚠️ 2026-08-19 -- **CORRECTION TO MY OWN INTERPRETATION ONE BLOCK BELOW: THE PROFILES DO**
## **PREDICT. WEAKLY, BUT REALLY -- 10.4%, CI-SEPARATED, ON 73% OF OBSERVATIONS.**
I wrote that the write-gate negative was explained by "the profile predicts nothing in particular".
**That was an interpretation, not a measurement, and turning it into one refutes it.**
`scratch/diag_does_a_profile_predict_its_own_contexts.py`, 16,930 PAIRED observations, 1,753 terms.

| residual magnitude (LOWER = better prediction) | mean | median | sd |
|---|---|---|---|
| **OWN** (leave-one-out profile) | **0.4375** | 0.4522 | 0.0759 |
| OTHER (a random other term's profile) | 0.4884 | 0.4904 | 0.0378 |
| **paired difference** | **+0.0510** | +0.0384 | CI **[+0.0498, +0.0522]** |

**A term's profile predicts its own next context 10.4% better than an unrelated term's does, on
73.2% of observations, with the CI nowhere near zero.** *Leave-one-out throughout, so OWN is never
a self-match -- that discipline exists because this session already found a 34% self-match
inflation in a number I published.*
**➡️ SO THE CHAIN IS NARROWER AND MORE HONEST THAN I SAID: the profiles DO carry term-specific
predictive content (10.4%); that content is TOO WEAK AND TOO UNIFORM to threshold (sd 0.076 about
a mean of 0.44); so a residual gate lands where a coin does. The failure is in the SELECTOR'S
RESOLUTION, not in the representation being empty.**
**⛔ AND THAT MATTERS FOR WHAT COMES NEXT: "the representation predicts nothing" would have closed
the representation line entirely. "It predicts 10.4% and that is too little to act on" points
somewhere specific -- the question becomes what would make the prediction SHARPER, not whether
prediction exists at all.** *Second time this session I overstated a negative and the measurement
walked it back. Both times the overstatement was mine and in the pessimistic direction.*

## 🔴 2026-08-19 -- [SEE THE CORRECTION ABOVE: "predicts nothing in particular" IS REFUTED] **THE RESIDUAL GATE HURTS, AND IS INDISTINGUISHABLE FROM RANDOM SKIPPING.**
## **READINGS (C) AND (D) BOTH FIRE. 2 of 3 seeds banked; the picture is not close.**
`exp_predictive_write_gate_v1`. **ACCUMULATE -- keeping everything, what the substrate does today
-- is the BEST of our arms at every k on both seeds.**

| seed 20260819 | hit@1 | hit@10 | hit@50 | median |
|---|---|---|---|---|
| **ACCUMULATE** | 0.0567 | **0.1800** | **0.3433** | **126** |
| GATED@0.45 | 0.0300 | 0.1767 | 0.2933 | 120.5 |
| RANDOM_SKIP@0.45 | 0.0300 | 0.1267 | 0.2967 | 132.5 |
| GATED@0.50 | 0.0200 | 0.0800 | 0.2733 | 133.5 |
| RANDOM_SKIP@0.50 | 0.0400 | 0.0900 | 0.2800 | 135.0 |
| **COOC_floor** | **0.0867** | **0.4067** | **0.7533** | **15** |

**⛔ READING (C): GATED never beats ACCUMULATE -- it LOSES at every threshold on both seeds.**
**⛔ READING (D): nothing comes near the floor (0.3433 vs 0.7533).**
**🎯 AND THE RATE-MATCHED ARM EARNS ITS PLACE: GATED ~= RANDOM_SKIP throughout, and RANDOM is
SLIGHTLY AHEAD at 2 of 3 thresholds on seed 20260819 (0.2967 vs 0.2933; 0.2800 vs 0.2733).** *So
the residual gate is not selecting informatively -- it is just discarding data, and discarding it
no better than a coin would. Without that arm this would have read as "predictive coding hurts";
with it, the honest statement is "the residual carries no usable selection signal here".*
**✅ THE PRE-BUILD PROBE PREDICTED EXACTLY THIS AND IS WHY THE ARM WAS THERE.** Residuals measured
near-constant (p10 0.3575, median 0.4648, p90 0.5237) -> a near-constant selector is a random
selector. **The probe cost minutes and made the negative interpretable instead of merely
disappointing.**
*Also: the "cliff" I described was an artifact of a coarse grid. The fine sweep is smooth --
skip rates 0.057 / 0.279 / 0.482 / 0.721 / 0.884 / 0.912 across thresholds 0.25-0.60. Sweeping
finely is what showed that; adopting 0.50 would have hidden it.*
**➡️ MORE DATA BEATS SELECTIVELY LESS DATA HERE, WHICH IS ITSELF THE FINDING: with a selector that
carries no information, accumulation is the right rule. The pinned equation does not fail -- OUR
RESIDUAL DOES, because the profile it is measured against predicts nothing in particular.**

## 🧠 2026-08-19 -- **BRAIN-FIDELITY AUDIT ON THE SUBSUMPTION NEGATIVE, AND FIRST THE HONEST**
## **ACCOUNTING: OF SIX NEGATIVES TODAY, ONE GOT A FIDELITY CHECK, TWO PARTIAL, THREE NONE.**
*Owner: "I want to make sure that you're properly drilling all negative findings and doing a brain
fidelity check." Audited rather than claimed. **Full: the cortical read (CLS position inversion).
Partial: the residual gate, the random-projection gap. NONE: the SUBSUMPTION result, the 9-seed
spoke failure, the reading-(C) void.** The biggest negative of the day had no fidelity audit at
all -- it was reported as a number and a consequence. This is that audit.*

**IT IS CHECKABLE AGAINST A PINNED QUANTITY, which is rare here.** ORGAN_MAP B4 is one of the twelve
organs whose equation is actually pinned: *"dense, graded, ~4-12 effective dims; IT sparseness
index ~0.2-0.3"* (Huth 2012, first ~4 group PCs define the shared semantic space).

| | effective dims (participation ratio) | components for 90% var | top-4 share |
|---|---|---|---|
| **brain, PINNED** | **~4-12** | -- | first ~4 define the space |
| **OUR PROFILES** | **50.4** | 92 | 0.201 |
| pure noise, same shape | 119.1 | 122 | 0.063 |

**✅ OUR CODE IS REAL STRUCTURE, NOT NOISE: 50.4 against noise's 119.1, and the first four
components hold 20.1% against noise's 6.3%. That much is a genuine positive and I had not measured
it before.**
**⛔ BUT IT IS 4-12x TOO HIGH-DIMENSIONAL AGAINST THE PINNED FIGURE, AND THAT EXPLAINS THE
SUBSUMPTION RESULT MECHANISTICALLY RATHER THAN JUST REPORTING IT: a LINEAR projection PRESERVES
THE RANK of what it projects. It cannot concentrate variance the way a LEARNED code does. So our
"hub" is a compressed COUNT VECTOR, and a compressed count vector cannot beat the counter it
compresses.** *That is why three mechanisms all lost to counting: they were all reading a lossy
copy of the counter.*
**⚠️ THE COMMENSURABILITY CAVEAT, STATED BEFORE ANYONE QUOTES THE COMPARISON: participation ratio
over 223 word profiles and Huth's "~4 group PCs" over voxel-wise encoding across subjects are NOT
the same measurement. The ORDER OF MAGNITUDE gap is the finding; the exact ratio is not.**
**⚠️⚠️ AND A SECOND CAVEAT FOUND AFTERWARDS BY QUERYING THE ARCHIVE I SHOULD HAVE QUERIED FIRST --
IT WEAKENS THE CLAIM ABOVE AND IS RECORDED WHERE THE CLAIM IS, NOT IN A FOOTNOTE:**
- **THE TWO CELLS USE DIFFERENT FORMULAS FOR THE SAME WORD.** `exp_effective_rank_svd_v1`
  (HARD_PASS) defines participation ratio as **(sum s)^2 / sum s^2 over SINGULAR VALUES**; today's
  diagnostic used **1 / sum(v^2) over normalised VARIANCE shares**. Those are different statistics
  and generally give different numbers. **50.4 and any number in that cell must not be put side by
  side until one of them is recomputed.**
- **AND ITS NUMBER MAKES THE "WE ARE UNUSUALLY DIFFUSE" READING LOOK PREMATURE:** that cell measured
  **MiniLM -- a normal, working sentence encoder -- at d_eff 91.6, rank90 175, rank99 296**, and
  landed HARD_PASS for being *intrinsic-dim-limited at d_eff <= 120*. If a competent text encoder
  also sits far above the brain's ~4-12, then **being 4-12x too diffuse may be a property of
  LEARNING-FROM-TEXT rather than a defect specific to OUR code**, and the subsumption explanation
  above is over-attributed. *The geometry finding stands; the blame does not, until both numbers are
  computed the same way on both objects.*
**➡️ AND IT AGREES WITH THE OWNER'S OWN DIAGNOSIS FROM A DIFFERENT DIRECTION: a code that only
ACCUMULATES cannot concentrate. Concentration is what LEARNING buys. Same conclusion as the
novelty work -- prediction first -- reached through geometry instead of through surprise.**

## 🧠✅ 2026-08-19 LATER -- **THE FIDELITY AUDIT IS NOW COMPLETE: ALL THREE GAPS FILLED, AND**
## **THREE OF MY FOUR EXPLANATIONS WERE REFUTED BY THEIR OWN PRE-COMMITTED CONTROLS.**
*The accounting above said: NONE for the subsumption result, the 9-seed spoke failure, the
reading-(C) void. All three now have one. **Every diagnostic was written with a pre-committed
alternative reading, and in three cases out of four the ALTERNATIVE is what fired.** That is the
system working, and it is worth more than three confirmations would have been.*
*(Header corrected from "four of four". The familiarity hypothesis was NOT refuted -- I had read
smoke numbers. See item 3 below, which is left standing as the correction rather than edited away.)*

**GAP 2 -- THE 9-SEED SPOKE FAILURE.** Hypothesis: hub-and-spoke POSITION. In the brain the
sensorimotor spokes are INPUTS that shape the hub over experience; ours is a supplied Lancaster
table consulted AFTER the hub has ranked. Prediction: the hub carries no sensorimotor structure.
**REFUTED.** Ridge read-out of the grounded dimensions from the 256-dim profile, 5,950 covered
words, 5-fold out-of-fold R^2, gated at max(0, shuffled-null p95):

| | R^2 |
|---|---|
| log corpus frequency (positive control) | **0.4819** |
| best sensorimotor dim (Gustatory) | 0.1145 |
| typical sensorimotor dim | **0.01 - 0.05** |
| Head | -0.0086 (no better than the mean) |

11 of 12 dimensions ARE carried, so the hub is **not** sensorimotor-blind and position is not the
explanation. **But the magnitude is the real story: the hub carries frequency ~20x more strongly
than a typical sensorimotor dimension.** Not blind -- overwhelmingly a frequency code.
*⚠️ A THRESHOLD BUG CAUGHT MID-RUN, LOGGED BECAUSE IT NEARLY PUBLISHED A FALSE POSITIVE: the first
gate was "above the shuffled null", and the shuffled null sits at **-0.12** because a 256-dim ridge
on shuffled targets OVERFITS. Under that gate 12 of 12 dims "passed" while every R^2 was NEGATIVE --
worse than predicting the mean. **The bar is max(0, null p95); the ZERO is the binding half.***

**GAP 3 -- THE READING-(C) VOID (the residual write gate did nothing).** Four explanations tested,
four dead:
1. *"It was thresholding noise."* The residual's median 0.4648 sits at the 0.5 that two UNRELATED
   vectors produce, so this looked certain. **REFUTED, n=55,399:** matched 0.4546 vs mismatched
   0.4888 vs chance 0.5001, difference CI [-0.0348, -0.0336]. The prediction carries real
   term-specific information.
2. *"Between-word variation swamped the encounter signal, so a global absolute threshold could only
   sort vocabulary."* **REFUTED:** ICC = **0.201**. Within-word variation is **80%** of the total.
   The absolute rule had exactly the encounter-level variation it needed.
3. *"It is a familiarity detector, not a novelty detector"* (the owner's Q71 distinction).
   **NOT REFUTED -- AND THIS ENTRY IS A CORRECTION OF WHAT I FIRST WROTE HERE.** I published the
   SMOKE numbers (161 terms: slope +0.0103, median -0.0046, 55% negative) as the finding and called
   it refuted. **At full n (1,590 terms) the sign flips and separates: mean slope -0.0035, median
   -0.0061, 63% of words negative, 95% CI [-0.0052, -0.0018].** The residual DOES fall as a word
   becomes familiar. *My own rule -- a smoke with smaller numbers does not test the full run -- and
   I broke it inside the very audit that was checking my rigour.*
   **A detrended encounter-level signal also survives (r = +0.733), BUT I AM NOT LEANING ON THAT
   NUMBER:** the residual is a distance to the word's own profile and "how unusual this use is" is a
   leave-one-out distance to the word's other contexts. **Those are nearly the same computation, and
   the positive control (+0.802) shows the construction correlates by itself.** So (2) mostly
   confirms the arithmetic, not a discovery. *A per-word DETRENDED gate is a real lead; it is not
   yet evidence.*
4. *"The missing PRECISION term is the divergence."* `precision` appears **nowhere** in
   `hdlab/predictive_coding.py` -- enumerated, 15 public names, not one mentions precision, variance,
   confidence or weighting, and `threshold_gate` takes exactly one knob. **But the archive already
   tested the precision-weighted form and it ALSO sat at chance** (Friston arm 0.530 vs flat 0.542).

**🔑 SO THE ACCOUNT THAT SURVIVES IS NOT ABOUT THE SIGNAL AT ALL -- IT IS ABOUT THE ACTION.** The
gate's signal is fine by every test we can put to it. What a write gate can do is choose WHICH
counts get added. **It cannot change that the representation IS a count.** Selectivity inside an
accumulate-only store is a no-op on the KIND of code produced -- which is the same conclusion the
effective-dimensionality measurement reached from geometry, and the same one the subsumption result
reached from ranking. *The fix is a NON-ADDITIVE write, not a better gate. Tuning thresholds cannot
reach it.*
## 🧱 2026-08-20 -- **THE UPDATE RULE CHANGES NOTHING EITHER. THE SUM IS OPTIMAL IN ITS OWN**
## **FAMILY, AND THE PRE-REGISTERED RISK IS EXACTLY WHAT HAPPENED.**
*The three POSITION errors all pointed here: precision belongs on HOW MUCH TO UPDATE, and `acc +=
trace` has no step size to modulate. So the profile was given a delta rule `p <- p + eta*(trace - p)`
-- which has both a residual and a step size, the form G2 actually pins. All arms at full coverage.*

| sentences | SUM | **1/n (control)** | eta .05 | eta .20 | eta .50 | **PREC** |
|---|---|---|---|---|---|---|
| 1000 | 0.98x | 0.98x | 0.84x | 1.07x | 1.16x | 0.93x |
| 2000 | 1.71x | 1.71x | 1.57x | 1.86x | 2.14x | 1.50x |
| 4000 | 2.23x | 2.23x | 2.42x | 2.90x | 3.42x | 2.44x |
| 8000 | 2.06x | 2.06x | 1.89x | 2.92x | 4.24x | 1.90x |
| 16000 | **4.39x** | 4.39x | 6.92x | 8.69x | 10.08x | 6.06x |

    phase slope  SUM +1.035 | 1/n +1.035 | .05 +1.798 | .20 +2.354 | .50 +2.879 | PREC +1.536
    beats SUM at:  1/n 0/5   .05 3/5   .20 0/5   .50 0/5   PREC 3/5

**✅ THE NESTED POSITIVE CONTROL PASSED AT EVERY POINT: `eta = 1/n` IS the running mean, and it
reproduced SUM's ranking EXACTLY (delta +0.00 at all five reads).** *That is what makes the rest of
the table interpretable rather than decorative -- the sum is not a separate arm, it is a POINT
INSIDE the delta-rule family, so "no arm beats the sum" means the family's optimum sits at the
no-forgetting end.*
**⛔ EVERY FIXED LEARNING RATE IS WORSE THAN THE SUM, AND WORSE FASTER: slopes +1.798 / +2.354 /
+2.879 against +1.035, and at 16,000 the recency arms blow out to 6.92-10.08x against the sum's
4.39x.** Precision on the step size does not rescue it (+1.536, 3/5).
**➡️ AND THE RISK WAS WRITTEN DOWN BEFORE THE RUN, VERBATIM: *"if the eta sweep says
smaller-is-always-better, the winner IS the sum and this is a NULL. Say so plainly."* It does, it is,
and I am.**
**🔑🔑 SO THE REPRESENTATION IS INSENSITIVE TO **HOW** IT IS WRITTEN AS WELL AS TO **WHICH** TRACES
GO IN.** Six write-side interventions have now failed on the phase curve (residual gate, k-WTA,
normalisation, incremental decorrelation, novelty/precision selection, and now the whole delta-rule
family). **The only two things that have EVER moved it are HOW MANY traces exist (coverage) and a
POST-HOC transform (centring) -- neither of which is a rule about writing.** *The limit is the
REPRESENTATION -- a random projection of counts -- not the procedure that fills it.*
**🧠 FIDELITY, AND IT NAMES THE ONE HONEST ESCAPE FOR THE DELTA RULE: the brain DOES forget, and
recency weighting is real synaptic behaviour. But forgetting BUYS adaptation to a CHANGING world,
and `simplewiki` read front-to-back is STATIONARY -- there is nothing to adapt to, so tracking can
only discard evidence.** *We tested a rule for non-stationarity on a stationary corpus, which is a
fourth POSITION error of the same shape: right mechanism, wrong regime.* **That is testable: on a
deliberately NON-STATIONARY reading order (topic-blocked, so word senses drift), recency should beat
accumulation. If it does not even there, the delta rule is dead on this instrument outright.**
*⚠️ Single seed per point, one corpus. Per-point deltas reported before slopes.*

## 🎚️ 2026-08-20 -- **PRECISION WEIGHTING, THE PINNED TERM, BUILT TO THE ARCHIVE'S OWN CONSTRAINT.**
## **MEASURABLE, WELL-BEHAVED -- AND STILL NOT A USABLE GATE. FOURTH NEGATIVE ON SELECTION.**
*ORGAN_MAP G2 pins the rule as the residual PRECISION-WEIGHTED, and enumeration found the term
absent from the module. Three lines pointed here. Precision = bias-corrected resultant length of the
term's contexts, computed from the PREFIX ONLY so an occurrence never contributes to its own weight.*

| sentences | AS_IS | **PREC_50** | NOVEL_50 | RANDOM_50 | FULL |
|---|---|---|---|---|---|
| 1000 | 1.20x | **0.84x** | 1.09x | 1.11x | 0.98x |
| 2000 | 2.29x | 1.86x | 1.57x | 1.79x | 1.71x |
| 4000 | 3.12x | 2.58x | 2.92x | 2.56x | 2.23x |
| 8000 | 3.69x | 3.02x | 2.53x | 2.39x | 2.06x |
| 16000 | 6.42x | **4.75x** | 6.64x | 5.44x | 4.39x |

    phase slope   AS_IS +1.708   PREC +1.294   NOVEL +1.740   RANDOM +1.337   FULL +1.035
    PREC beats RANDOM at 2/5 points, beats NOVEL at 3/5 -- a coin flip, deltas swing -0.69 to +0.63

**✅ THE DESIGN CAME FROM THE ARCHIVE, NOT FROM ME, AND THAT MATTERS.** A four-cell arc exists:
`..._reliability_gate_v1` HARD_PASS **but DOWNGRADED on adversarial VET -- its confidence was
INJECTED**; `..._derived_v1` HARD_FAIL_INERT_OR_HARMFUL with a strong same-item signal
(auc **0.8303**) that **still gave a gate delta of -0.0280**; `..._independent_channel_v1` HARD_PASS
**because it was LEAVE-ONE-ITEM-OUT**; `..._correlated_error_v1` HARD_FAIL, fooled **below chance
(auc 0.3198)** by systematic errors. *Reading that arc first is why precision here is prefix-only --
building it without leave-one-out would have reproduced a known failure exactly.*
**⛔ AND IT LANDED IN THE SAME PLACE THE DERIVED CELL DID: MEASURABLE BUT NOT USABLE.** The statistic
is real and its self-test is clean (consistent contexts 0.989, scattered 0.167, single observation
0.000). Weighting the residual by it does not make selection work.
**🔑🔑 AND THIS CORRECTS MY OWN MECHANISTIC STORY, WHICH IS THE MOST USEFUL PART. I had explained the
residual gate's failure as "the selector has no spread to rank on" (sd 0.066 about mean 0.44).
PRECISION HAS 2-3x MORE SPREAD (sd 0.134-0.208) AND FAILS ANYWAY. So spread was NOT the binding
constraint, and the story I have been telling since the write gate closed is wrong.**
**➡️ FOUR INDEPENDENT TESTS NOW AGREE: WHICH TRACES ARE KEPT DOES NOT MATTER ON THIS INSTRUMENT --
ONLY HOW MANY.** (residual write gate 0 of 54; NOVEL vs RANDOM a tie; PREC vs RANDOM a coin flip;
and every selective arm sits between AS_IS and FULL regardless of rule.) *That is a real, useful
negative: STOP BUILDING SELECTORS.*
**🧠 FIDELITY -- POSITION AGAIN, AND IT IS THE ONE HONEST ESCAPE LEFT FOR THE PINNED RULE. G2's
precision-weighted residual is a claim about LEARNING -- how much to UPDATE -- not about WHICH
EPISODES TO STORE. We have now tested it four times in the storage role and never in the update
role, because our profiles have no update rule to modulate: they only ever add.** *So the pinned
term may still be right and tested in the wrong place -- which is the same POSITION error found for
the sensorimotor spoke and for k-WTA. Third time.*
*⚠️ Single seed per point, one corpus. Per-point deltas reported BEFORE slopes, per last night's
endpoint lesson.*

## 📝 2026-08-19 -- **THE OWNER'S Q71 RULE, TESTED: WHAT MATTERS IS HOW MANY NOTES, NOT WHICH.**
## **AND I NEARLY HEADLINED A STRONG CLAIM THAT RESTED ENTIRELY ON ONE POINT.**
*Owner Q71: "it's NEWNESS that gets notes, not just words used the same way." Tested at MATCHED
BUDGET -- keep half of each term's occurrences, chosen by novelty vs chosen at random. The
rate-matched control was demanded by the plan in advance, and it is what makes this readable.*

| sentences | AS_IS | NOVEL_50 | RANDOM_50 | FULL | NOVEL - RANDOM |
|---|---|---|---|---|---|
| 1000 | 1.20x | 1.00x | 1.11x | 0.98x | **-0.11** |
| 2000 | 2.29x | 1.64x | 1.79x | 1.71x | **-0.14** |
| 4000 | 3.12x | 2.69x | 2.56x | 2.23x | +0.13 |
| 8000 | 3.69x | 2.34x | 2.39x | 2.06x | **-0.05** |
| 16000 | 6.42x | 6.39x | 5.44x | 4.39x | **+0.94** |

**✅ THE DEFENSIBLE FINDING: VOLUME, NOT SELECTION. Both half-budget arms land between AS_IS and
FULL, and NOVEL vs RANDOM is a coin flip -- NOVEL wins 3 of 5 points, and every delta except one is
within +-0.14.** *Practically useful either way: half the traces buys ~55% of full coverage's
benefit no matter how they are chosen.*
**🚨 AND THE VERDICT MY SCRIPT PRINTED WAS "NOVELTY SELECTION IS WORSE THAN RANDOM (8% vs 55%) --
our residual is ANTI-correlated with usefulness". THAT CLAIM IS NOT SUPPORTED AND I ALMOST FILED
IT.** It came from a SLOPE over five points, and **the final point's delta (0.944) is 8.7x the mean
of the other four (0.109)** -- one endpoint dragging the whole fit. *Fifth gate defect of the
session, and a new species: not too lenient, but ENDPOINT-SENSITIVE. A slope is a summary, and a
summary can be carried by one observation. The per-point column is now printed and the verdict
refuses to headline a slope that one point dominates.*
**🧠 BRAIN-FIDELITY DRILL, AND IT IS THE THIRD INDEPENDENT ROUTE TO THE SAME MISSING TERM.** Our
residual measures "unlike this word's average so far", which CONFLATES two things the owner's rule
separates: **a genuinely NEW SENSE, and a merely NOISY occurrence.** In `simplewiki` most words are
monosemous, so the noisy ones dominate and the selector behaves as an OUTLIER detector rather than a
new-sense detector. **Distinguishing those two is exactly what PRECISION WEIGHTING does in the
brain -- and precision was measured absent from `hdlab/predictive_coding.py` by enumeration (15
public names, not one mentions precision, variance, confidence or weighting).**
*So the owner's principle is NOT refuted here. What is measured is that WE HAVE NO SIGNAL CAPABLE OF
IMPLEMENTING IT.* **That is now the third independent line pointing at the same absent term** (the
write gate's flat residual; the archive's flat-surprise-at-chance; this).
*⚠️ Single seed per point, one corpus, same caveats as the rest of the sweep family.*

## 🧮 2026-08-19 -- **THE 2x2: THE TWO WORKING FIXES ARE SYNERGISTIC, NOT INDEPENDENT -- AND THERE**
## **IS NO CHEAP VERSION. CENTRING ALONE BUYS 19% OF A 63% TOTAL.**
*Both fixes had shown 39%, but from DIFFERENT runs, and the centring run already had full coverage
on -- so chaining them to "-63%" was an inference. Four cells, ONE run, ONE population per point.*

| sentences | cov | COOC | A as-is+sum | B as-is+**centred** | C **full**+sum | D **full+centred** |
|---|---|---|---|---|---|---|
| 1000 | 0.816 | 22.5 | 1.20x | 1.16x | 0.98x | 1.02x |
| 2000 | 0.730 | 14.0 | 2.29x | 2.14x | 1.71x | 1.64x |
| 4000 | 0.708 | 26.0 | 3.12x | 3.10x | 2.23x | 2.00x |
| 8000 | 0.564 | 31.0 | 3.69x | 3.32x | 2.06x | 1.84x |
| 16000 | 0.435 | 18.0 | **6.42x** | 5.36x | 4.39x | **3.11x** |

    phase slope   A +1.708   B +1.384   C +1.035   D +0.631
    centring:  at as-is coverage 19%  |  at FULL coverage 39%
    coverage:  without centring  39%  |  WITH centring    54%
    A -> D total 63%   |   multiplicative prediction +0.838, MEASURED +0.631, deviation -0.207

**⛔ NO CHEAP VERSION EXISTS, AND THAT WAS THE PRACTICAL QUESTION. Centring alone -- a change to how
profiles are READ, costing nothing and touching no reading behaviour -- buys only a 19% slope
reduction against 63% for both. That is under a third of the achievable benefit.** *Centring needs
complete counts underneath it to pay off; the two are entangled and I should stop offering the cheap
option, which I had been ready to recommend shipping.*
**✅ THEY ARE SUPER-ADDITIVE, NOT MERELY ADDITIVE: the independence prediction was +0.838 and the
measured value is +0.631 (deviation -0.207).** Each fix makes the other work better -- centring is
worth 19% alone and 39% once coverage is complete; coverage is worth 39% alone and 54% once centring
is on. *Mechanistically coherent: centring can only remove the shared direction accurately if the
counts it is estimated from are complete.*
**✅ AND IT VALIDATES THE CROSS-RUN ARITHMETIC I FLAGGED AS UNSAFE: I predicted -63% by chaining two
separate runs, warned in the pre-reg that chaining was an inference and not a measurement, and the
one-run measurement came back at exactly -63%.** *The earlier sweeps are mutually consistent -- a
real check on four experiments, not a formality.*
**⚠️ AND THE POSITION IS STILL NOT WON: the best cell is 3.11x behind the counter at 16,000. Both
fixes together FLATTEN the curve by two thirds and do not CLEAR the floor.** *At 1,000 sentences
every cell is at parity (0.98-1.20x); the whole effect is about how fast we fall away, not whether.*

## 🔁 2026-08-19 -- **INCREMENTAL DECORRELATION: HYPOTHESIS REFUTED IN THE OPPOSITE DIRECTION.**
## **DOING IT AFTERWARDS BEATS DOING IT AS YOU GO -- AND MY SCRIPT COULD NOT SEE ITS OWN WINNER.**
*The plan predicted that removing the shared component INCREMENTALLY AT WRITE would beat removing it
post-hoc, "so the store never accumulates the correlated component". All arms at full coverage.*

| sentences | COOC | SUM | **POSTHOC_CENTER** | INCR_CENTER | INCR_OJA |
|---|---|---|---|---|---|
| 1000 | 22.5 | 0.98x | 1.02x | 0.96x | 1.11x |
| 2000 | 14.0 | 1.71x | 1.64x | 1.50x | 2.14x |
| 4000 | 26.0 | 2.23x | 2.00x | 2.60x | 3.10x |
| 8000 | 31.0 | 2.06x | **1.84x** | 2.21x | 3.56x |
| 16000 | 18.0 | 4.39x | **3.11x** | 5.47x | 7.42x |

    phase slope   SUM +1.035   POSTHOC +0.631   INCR_CENTER +1.406   INCR_OJA +2.025
    effective dims at 16,000   SUM 92.3   POSTHOC 29.1   INCR_CEN 100.3   INCR_OJA 143.7

**⛔ THE HYPOTHESIS IS REFUTED, AND BACKWARDS: incremental removal HURTS (+1.406, +2.025 vs SUM's
+1.035) while POST-HOC removal is the best arm measured all session (+0.631, 39% flatter, and the
ONLY intervention that has ever concentrated the code -- 92.3 -> 29.1 effective dims, 3.2x).**
**🔑 MECHANISM, AND IT IS THE SAME LESSON k-WTA TAUGHT LAST NIGHT: an EARLY running estimate of the
shared direction is a BAD estimate, and subtracting a bad estimate corrupts every trace it touches.
OPERATIONS ON THE ADDENDS HURT; THE SAME OPERATION ON THE ACCUMULATED RESULT HELPS. Two independent
experiments now agree, having been designed to show the opposite.** *This retires the "the store
must never accumulate it" intuition, which was mine and was stated confidently in the plan.*
**🚨 AND MY OWN VERDICT LINE SAID "THE ACCUMULATION ROUTE IS EXHAUSTED" -- FLATLY WRONG. The gate
compared only the two INCREMENTAL arms against SUM; POSTHOC was never on the left-hand side of any
comparison, so the best result of the session was invisible to the code that judged it. FOURTH
mis-specified gate in two sessions** (the floor gate that ignored FREQ; "DISCRIMINATES" on 1 nonzero
in 900; arms-differ passing at 0.981 overlap; now a verdict blind to one of its own arms).
*Every one was caught by reading the NUMBERS rather than the VERDICT LINE. That habit is now the
single most load-bearing thing I do.*
**⚠️ WHAT IT DOES NOT DO, STATED BEFORE ANYONE GETS EXCITED: POSTHOC IS STILL 3.11x BEHIND THE
COUNTER AT 16,000. It flattens the curve; it does not clear the floor.** *And at the single 8,000
point I earlier recorded centring as "NOT A LEAD" because it lost to a cue-blind FREQ ranking --
BOTH are true, and they are answers to different questions: it is the best SLOPE intervention and
still not a capability win.*
**➡️ THE OBVIOUS NEXT TEST, AND IT IS CHEAP: FULL COVERAGE gave a 39% slope cut and POST-HOC
CENTRING gives 39%. They target DIFFERENT defects (recording vs concentration) and were measured
independently. DO THEY ADD?** If they compose, the slope lands near +0.4 and the position at 16,000
improves materially; if they do not, they were the same 39% twice and that is worth knowing too.

## ⛔ 2026-08-19 -- **COMPETITION AT WRITE TIME FAILS, AND IT FAILS FOR A REASON THAT OVERTURNS MY**
## **OWN DESIGN ASSUMPTION: SPARSIFYING THE ADDENDS MAKES THE SUM *MORE* DIFFUSE, NOT LESS.**
*All arms at FULL COVERAGE so the note-taking term is held constant. Same corpus, terms, items,
floors. They differ only in the write operation.*

| sentences | COOC | SUM | KWTA8 | KWTA32 | NORM (control) |
|---|---|---|---|---|---|
| 1000 | 22.5 | 0.98x | 1.07x | 0.98x | **0.89x** |
| 2000 | 14.0 | 1.71x | 2.21x | 1.86x | 1.57x |
| 4000 | 26.0 | 2.23x | 3.35x | 2.77x | 2.23x |
| 8000 | 31.0 | 2.06x | 3.40x | 2.34x | 2.15x |
| 16000 | 18.0 | 4.39x | 6.31x | 4.81x | 3.97x |

    phase slope   SUM +1.035   KWTA8 +1.683   KWTA32 +1.174   NORM +0.972

**⛔ NO ARM CUTS THE SLOPE. k-WTA is WORSE than plain summing at every single point and STEEPENS the
degradation (+1.035 -> +1.683). NORM ties SUM (+0.972 vs +1.035) -- within noise, not a win.**
**🔑🔑 AND HERE IS THE MECHANISM, WHICH IS THE OPPOSITE OF WHAT I DESIGNED THE TEST TO GUARD
AGAINST. I wrote in the pre-reg that "k-WTA REDUCES EFFECTIVE DIMENSIONALITY BY CONSTRUCTION", so PR
would be a tautology and must not be the outcome. IT DID THE REVERSE: at 16,000 the effective
dimensionality is SUM 92.3 -> KWTA8 130.2.** *Sparsifying each trace before adding does not sparsify
the total -- it DECORRELATES the addends, so their sum spreads across MORE independent directions
than the dense traces did.* **Sparsity applied to the INPUT of an accumulator is an
anti-concentration operation.** That is a genuine mechanistic result and it explains the ranking
loss rather than merely reporting it.
**📕 THIS IS NOW THE THIRD PLACE SPARSITY HAS FAILED IN THIS CODEBASE, and the prior two were read
BEFORE building, not after:** `exp_c1_sparse_value_k10_cpu_v1` HARD_FAIL (dense capacity 332 vs
sparse 132, ratio 0.40) and `exp_arc_aggregation_sparse_code_regime_v1` SPARSITY_NEUTRAL (0.308 vs
0.301). *The third, `exp_cortex_schema_tonegawa_sparse_ensemble_v2`, is uninformative -- its
baseline sat at 1.000, a saturated regime.* **A low prior was recorded in advance and it was right.**
**🧠 BRAIN-FIDELITY DRILL ON THIS NEGATIVE -- POSITION, and it names the next build precisely.**
Cortical/DG sparse coding is COMPETITION ACROSS THE POPULATION at encoding, with recurrent settling;
the units that win SUPPRESS the others, and what is stored is the settled pattern. **Ours applies
k-WTA WITHIN a single incoming trace and then sums the results INDEPENDENTLY -- there is no
competition BETWEEN encounters and none BETWEEN terms at all.** *We copied the shape of sparsity and
not its position.* **➡️ SO THE UNTESTED FAITHFUL VERSION IS COMPETITION ON THE ACCUMULATED STATE --
between the stored profiles themselves, which is the ATL hub story -- NOT a filter on the incoming
trace. Every variant tested so far, including this one, competes in the wrong place.**
*⚠️ Single seed per point, one corpus, pool grows 58 -> 480. Internal consistency check that
passed: SUM here reads +1.035, exactly the FULL_COV slope from the previous experiment, as it must.*

## 🔬 2026-08-19 -- **WHICH CAUSE? NOTE-TAKING IS WORTH 39% OF THE DEGRADATION AND NOT ONE POINT**
## **OF THE DIFFUSION. THE TWO DEFECTS ARE INDEPENDENT AND ONLY ONE IS VISIBLE TO THE RANKING.**
*The phase diagram said we fall away from the counter as we read. Two causes tracked that curve --
falling coverage and a spreading code. This is the experiment that separates them: same terms, same
corpus, same projection, arms differing ONLY in whether every encounter gets written down. **Because
the arms share the projection, the projection cannot explain a difference between them.***

| sentences | coverage | AS_IS gap | **FULL_COV gap** | COOC | PR as-is | **PR forced** |
|---|---|---|---|---|---|---|
| 1000 | 0.816 -> 1.0 | 1.20x | **0.98x** | 22.5 | 12.6 | 13.2 |
| 2000 | 0.730 -> 1.0 | 2.29x | 1.71x | 14.0 | 18.2 | 20.1 |
| 4000 | 0.708 -> 1.0 | 3.12x | 2.23x | 26.0 | 50.3 | 52.3 |
| 8000 | 0.564 -> 1.0 | 3.69x | **2.06x** | 31.0 | 71.5 | 73.7 |
| 16000 | 0.435 -> 1.0 | 6.42x | **4.39x** | 18.0 | 91.8 | 92.3 |

    slope of the gap vs log(sentences)   AS_IS +1.708   FULL_COV +1.035   -> 39% reduction

**✅ NOT-RECORDING IS REAL AND WORTH FIXING: forcing a note on every encounter improves the LEVEL at
every single point (3.69x -> 2.06x at 8,000; 6.42x -> 4.39x at 16,000) and holds parity with the
counter out to 1,000 sentences (0.98x).** *The owner's instinct that this is about what gets written
down is CORRECT, and it is the largest single lever measured all session.*
**⛔ AND IT IS NOT SUFFICIENT -- THE VERDICT IS PARTIAL, NOT SOLVED. The slope only falls 39% and is
still climbing at +1.035. Even with PERFECT note-taking we are 4.39x behind at 16,000 and still
degrading.** *Anyone quoting "fix the note-taking" must quote this sentence with it.*
**🔑🔑 THE DISSOCIATION IS THE REAL RESULT, AND IT WAS THE PRE-COMMITTED "MOST INFORMATIVE" OUTCOME:
FORCING COMPLETE NOTES DOES NOT MOVE THE DIFFUSION AT ALL. PR goes 12.6 -> 91.8 as-is and
13.2 -> 92.3 forced -- identical to within noise at every point.** So coverage and diffusion are
INDEPENDENT defects: coverage drives the ranking, diffusion is invisible to the ranking metric, and
**writing MORE cannot concentrate a code. Concentration has to come from the write RULE.**
**🧠 BRAIN FIDELITY, and this is the sharpest statement of it yet: the brain's hub CONCENTRATES with
experience (pinned ~4-12 effective dims). We now know that is NOT achievable by recording more --
we just recorded everything and the code diffused exactly as before. A learned code concentrates
because of COMPETITION between representations; ours sums. THE DIVERGENCE IS THE WRITE OPERATION
ITSELF, not the amount written.** *That is a build target, not a shortfall.*
*⚠️ Same caveats as the phase diagram: single seed per point, one corpus, pool grows 58 -> 480.
The MONOTONICITY and the 5-point slope carry the weight, not any single cell.*

## 🌡️🌡️ 2026-08-19 -- **THE PHASE DIAGRAM. THERE IS A REAL PHASE BOUNDARY NEAR ~1,000 SENTENCES:**
## **WE BEAT THE COUNTER BELOW IT AND FALL AWAY FROM IT MONOTONICALLY ABOVE IT.**
*Owner, COMMENTARY 22:27:04Z: "don't forget the phase diagram for these different components".
Built over READ VOLUME -- the one axis every component shares and the one we had never varied.
**Every conclusion reached earlier today came from a single column of this table (8,000).***

| sentences read | candidates | OURS | COOC | **GAP** | coverage | PR_var | resid_sd |
|---|---|---|---|---|---|---|---|
| 600 | 40 | 15.0 | 10.0 | 1.50x | 0.961 | 10.0 | 0.1099 |
| **900** | 58 | **20.0** | **21.0** | **0.95x -- WE WIN** | 0.882 | 12.6 | 0.0929 |
| 1000 | 58 | 27.0 | 22.5 | 1.20x | 0.816 | 12.6 | 0.0896 |
| 2000 | 74 | 32.0 | 14.0 | 2.29x | 0.730 | 18.2 | 0.0793 |
| 4000 | 222 | 81.0 | 26.0 | 3.12x | 0.708 | 50.3 | 0.0662 |
| 8000 | 330 | 114.5 | 31.0 | 3.69x | 0.564 | 71.5 | 0.0661 |
| 16000 | 480 | 115.5 | **18.0** | **6.42x** | 0.435 | 91.8 | 0.0661 |

**⛔⛔ THE PHASE VARIABLE MOVES MONOTONICALLY THE WRONG WAY: 0.95x -> 6.42x, slope +1.708 per
e-fold of reading. MORE DATA IS NOT THE LEVER -- IT IS THE PROBLEM.**
**🔑 AND THE CLEANEST FORM OF IT IS IN THE LAST TWO ROWS: FROM 8,000 TO 16,000 SENTENCES *OUR* ARM
DOES NOT MOVE (114.5 -> 115.5) WHILE THE COUNTER IMPROVES (31.0 -> 18.0). Our representation stops
extracting anything from additional text while plain counting keeps getting better on the same
text.** *That is saturation, stated as directly as this instrument can state it.*
**➡️ ALL FOUR COMPONENT VARIABLES DEGRADE TOGETHER, WHICH IS WHY THIS IS ONE STORY AND NOT FOUR:**
coverage **halves** (0.961 -> 0.435, we record ever fewer of what we meet); effective dimensionality
**rises 9x** (10.0 -> 91.8, the code spreads out instead of concentrating); the residual spread
**shrinks and then FLATLINES** (0.1099 -> 0.0661, then 0.0661, 0.0661).
**✅ THAT FLATLINE IS A PROPER DRILL OF THE WRITE-GATE NEGATIVE, AND IT HARDENS IT.** The gate closed
because the residual was too uniform to threshold. **The spread does not widen with scale -- it
saturates. So the closure is NOT a single-point artifact and no amount of reading reopens it.**
*I flagged that closure as possibly scale-dependent when I set this up; it is not. Recorded because
the prediction was wrong in the safe direction.*
**⚠️ CAVEATS, BEFORE ANYONE QUOTES THE 6.42x: single seed per point, one corpus, and the candidate
pool GROWS with reading (40 -> 480) so the task itself changes down the column. The ratio is used
precisely because the pool cancels between arms at each point -- but a ratio of medians is not a
CI-separated statistic, and no CI was computed ON THE RATIO.** *What carries the weight is the
MONOTONICITY across seven points, not any single value.*
**🧠 BRAIN FIDELITY, since the owner asked for it on every negative: the brain's hub CONCENTRATES
with experience -- that is what the pinned ~4-12 effective dims means. Ours does the opposite,
moving 10.0 -> 91.8 as it reads. SHAPE diverges, and it diverges PROGRESSIVELY. A learned code buys
concentration; an accumulating random projection buys diffusion. This is the same divergence the
geometry and subsumption results found, now shown as a TRAJECTORY rather than a snapshot.**

## 🧪 2026-08-19 -- **GAP-TARGETED READING, TESTED TWICE. THE FIRST RUN WAS VOID AND MY OWN GATE**
## **PASSED IT AT 98% ARM OVERLAP. THE SECOND IS UNDERPOWERED, NOT NEGATIVE.**
*The owner's "patchy" half of Q72, wired from the existing organs. One variable: WHICH sentences get
read, never how many. Three arms, 6,000 sentences each from one 12,000-sentence pool.*

**⛔ RUN 1 WAS VOID AND IT NEARLY GOT REPORTED. GAP and PASSIVE overlapped 0.981 -- 5,943 of 6,057
sentences identical.** Cause: I drew targets from the top-400 frequent non-consolidated words, which
gave 298 targets; frequent words appear in nearly every sentence, so almost everything scored >= 1,
the ranking was flat, and **ties broke by INDEX -- i.e. corpus order -- so the "gap-targeted" arm
silently reproduced passive reading.** *My arms-differ gate asserted `jac < 0.99` and PASSED at
0.981.* **THAT IS THE THIRD TOO-LENIENT GATE I HAVE WRITTEN TODAY** (the floor gate that ignored
FREQ; the "DISCRIMINATES" check that fired on 1 nonzero in 900). Gate now refuses above 0.60 and
fails loud; targets now drawn from MID-frequency words (5 <= count <= 200) with RANDOM tie-breaks.

**RUN 2, arms genuinely distinct (overlap 0.327 / 0.335 / 0.326), 4,924 shared candidates, 300 items:**

| arm | median rank | 95% CI |
|---|---|---|
| PASSIVE | 1296.0 | [860.5, 1692.1] |
| RANDOM_N (rate-matched) | 1205.5 | [1031.0, 1466.0] |
| GAP | 1292.5 | [1028.8, 1501.0] |
| FREQ floor (cue-blind) | 354.0 | [276.5, 432.0] |
| COOC floor | 195.5 | [135.0, 262.0] |

    GAP minus PASSIVE    -88.98  95% CI [-220.31,  +40.72]   NOT separated
    GAP minus RANDOM_N    -6.68  95% CI [-133.01, +121.76]   NOT separated

**⚠️ THE VERDICT IS "UNDERPOWERED", NOT "DOES NOT HELP", AND THE CI IS WHY: a half-width of 130-220
ranks means this test could only ever have detected an enormous effect.** *Same category as the
corpus-diversity result. My script printed "GAP-TARGETED SELECTION DOES NOT HELP HERE" -- too strong
for what a CI that wide can support.*
**🔑 AND A DISTINCTION THAT MATTERS MORE THAN THE NUMBERS: the prior HARD_PASS I was chasing
(`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`) measured COVERAGE, 0.50 -> 0.79. THIS TEST
MEASURES RANK. Those are different claims, and coverage improving does not imply rank improving.**
*So this is NOT a failure to reproduce that cell -- it is a different question, asked for the first
time, and answered "not at this power".* **⛔ Nothing here licenses "the owner's idea does not work".**
**➡️ Every arm remains 6.6x from the COOC floor and well behind a cue-blind FREQ ranking, exactly as
in every other line this session.**

## 🔌 2026-08-19 -- **THE GAP-TARGETED ORGANS ARE BUILT, IMPORT CLEAN, AND ARE DIRECTLY**
## **STATE-COMPATIBLE WITH THE SUBSTRATE. THEY ARE SIMPLY NOT WIRED IN. NO ADAPTER NEEDED.**
*The top item was "test gap-targeted growth". Per the query-before-building rule I checked the code
registry first, and it is another BUILT-PASSING-UNWIRED case: `hdlab/gap_detector.py`,
`hdlab/gap_driven_reader.py` and `hdlab/three_tier_loop.py` all exist, all import, and
`substrate.py` references **none** of them.*
**✅ COMPATIBILITY CONFIRMED WITHOUT AN ADAPTER: `sub.state` IS a `reading_grounding_loop.
ReadingLoopState`, which is exactly what these functions take.**
**✅ AND THE GAP SIGNAL WORKS, shown with a POSITIVE AND A NEGATIVE CONTROL rather than one:**

    is_gap_now on CONSOLIDATED words (already grounded)   0 of 40   correctly NOT gaps
    is_gap_now on NON-consolidated frequent words        20 of 40   correctly ARE gaps
    rank_material over 10 docs x 30 sentences   scores 8,4,4,2,1,1,1,0,0,0 -- discriminates

**⚠️ AND I NEARLY FILED THE OPPOSITE. My first probe reported "0 of 68 gaps" and "1 nonzero score in
900 pairs" and I was one step from recording THE ORGAN IS INERT. Both signals were MY OWN BUGS:**
1. `rank_material` takes `doc_id -> a sequence of SENTENCES`; **I passed `s.split()`, a sequence of
   single WORDS**, so almost nothing could ever match.
2. I ran `is_gap_now` on the **CONSOLIDATED** terms -- words the substrate has already grounded,
   which by definition are not gaps. **I tested the one population guaranteed to return zero.**
*Both are the same underlying error: an absence result was produced by MY setup and would have been
attributed to the ORGAN. The positive control is what separated them -- "20 of 40 on the other
population" cannot be faked by a broken detector.* **AND MY OWN CHECK PRINTED "DISCRIMINATES" ON A
SINGLE NONZERO OUT OF 900 -- too lenient, the same failure mode as the floor gate two results
earlier. Twice in one session I wrote a gate that could not fail.**

## 📐 2026-08-19 -- **THE DIMENSIONALITY CLAIM, SETTLED ON MATCHED FORMULA AND MATCHED**
## **POPULATION. MY ORIGINAL CLAIM WAS INVALID AND MY CORRECTION TO IT WAS ALSO WRONG.**
*Three versions of this claim now exist. Only the third is measured on a comparison where everything
matches, and it is the only one to quote.*

| object (8,450 sentences, same corpus, same 256 dims) | PR_variance | PR_singular | rank90 | top-4 share |
|---|---|---|---|---|
| **OUR PROFILES (all 9,624 terms)** | **191.5** | **238.6** | 201 | 0.054 |
| OUR PROFILES (consolidated, 330) | 71.5 | 163.9 | 115 | 0.151 |
| **RAW COUNT VECTORS (9,305 terms)** | **131.7** | **219.7** | 182 | 0.092 |
| our profiles, shuffled | 249.1 | 254.2 | 223 | 0.021 |
| pure noise, same shape | 249.4 | 254.3 | 223 | 0.021 |
| MiniLM (CITED, archive, ITS population) | not stored | 91.6 | 175 | -- |
| brain, PINNED (Huth) | ~4-12 | ~4-12 | -- | -- |

**⛔ V1 -- "we are 4-12x too diffuse vs the brain" -- WAS NOT A COMPARISON.** Two mismatches, either
of which alone invalidates it: the archive's formula is `(sum s)^2/sum s^2` over SINGULAR VALUES,
mine was `1/sum(v^2)` over VARIANCE SHARES (they differ by 1.2x on our own matrix); and my 50.4 was
measured on the CONSOLIDATED population while the natural comparison is all profiled terms
(**71.5 vs 191.5 -- the population effect is 2.7x, larger than the formula effect**).
**⛔ V2 -- "so it is probably just what learning from text looks like" -- NOT SUPPORTED.** On the
SAME formula we read **238.6 against MiniLM's 91.6, i.e. 2.60x**. *That comparison still has its own
population caveat -- their number is over sentence embeddings on their corpus, ours over word
profiles on ours -- so it is suggestive, not decisive. But it does not support the shrug.*
**✅ V3, THE ONE TO QUOTE, BECAUSE EVERYTHING MATCHES -- same corpus, same sentences, same terms,
same width, same formula: OUR PROFILES ARE LESS CONCENTRATED THAN THE RAW COUNTS THEY ARE BUILT
FROM. 191.5 vs 131.7, and the top four components hold 0.054 of the variance against the counts'
0.092.** Both are real structure (noise and shuffled sit at ~249).
**🔑 SO THE RANDOM PROJECTION IS NOT NEUTRAL -- IT DE-CONCENTRATES.** We take a count matrix and
produce something MORE spread out than what we started with. *That is a sharper statement of the
subsumption result than the brain comparison ever was, it needs no pinned figure to make its point,
and it names a specific suspect: **the projection, not the counting**.*
**➡️ AND IT MAKES THE NEXT TEST OBVIOUS AND CHEAP:** the ridge read-out says the profile's most
recoverable content is FREQUENCY (R^2 0.4819). If a dominant common direction is eating the
variance, removing it should concentrate the code. *Swept over k, scored against the COOC and FREQ
floors on the same items -- because "better than our own previous arm" is the trap that has caught
three lines already.*

## 📉 2026-08-19 -- **REMOVING THE COMMON DIRECTION: A SMALL REAL GAIN, AND A FLOOR THAT MAKES IT**
## **IRRELEVANT. MY OWN SCRIPT'S VERDICT WAS TOO GENEROUS AND IS CORRECTED HERE.**
330 candidates, 300 held-out items (0.0% leaked -- drawn from the substrate's own advanced handle),
paired bootstrap on identical items:

| arm | median rank | 95% CI | vs RAW, paired |
|---|---|---|---|
| RAW | 91.0 | [74.5, 104.0] | -- |
| **MEAN_REMOVED** | **83.0** | [70.0, 100.0] | **-4.41, CI [-6.83, -2.06] SEPARATED** |
| PC1_REMOVED | 83.5 | [69.0, 107.0] | -3.67, CI [-7.58, +0.15] not separated |
| PC2_REMOVED | 97.5 | [83.0, 118.0] | +3.73 SEPARATED **WORSE** |
| PC4_REMOVED | 106.0 | [86.5, 127.0] | +6.06 SEPARATED **WORSE** |
| PC8_REMOVED | 115.0 | [92.0, 135.5] | +11.71 SEPARATED **WORSE** |
| **FREQ floor** (cue-blind) | **71.0** | [60.5, 71.0] | -- |
| **COOC floor** | **20.5** | [15.0, 26.0] | -- |

**⛔ THE HEADLINE IS THE FLOOR, NOT THE GAIN: A RANKING THAT NEVER LOOKS AT THE SENTENCE -- ORDER
EVERY CANDIDATE BY HOW OFTEN IT APPEARS IN THE CORPUS -- REACHES 71.0. OUR BEST ARM REACHES 83.0.
EVERY ARM WE RAN LOSES TO A FLOOR THAT IGNORES THE QUESTION.** And the real bar, COOC at 20.5, is
four times better again.
**⚠️ AND THE SCRIPT I WROTE DECLARED "REAL LEAD" ANYWAY, because its verdict gate compared only to
COOC and I never wired FREQ into the decision -- I printed it and did not gate on it.** The standing
rule is *CI-separated margin over the STRONGEST floor actually run*; I ran the floor and then failed
to use it. **Corrected verdict: NOT A LEAD.**
**✅ WHAT IS NEVERTHELESS TRUE, AND SMALL: centring the profiles helps by a separated margin**
(91.0 -> 83.0). *Note MEAN_REMOVED is simply CENTRING -- and `PC1_REMOVED` is centring PLUS removing
one more component, which is already no better. Removing further components degrades MONOTONICALLY.*
So there is exactly one direction worth deleting and it buys 8 ranks out of 330.
**🔑 READ TOGETHER WITH THE GEOMETRY ABOVE, THIS IS COHERENT AND IT IS NOT ENCOURAGING: our code is
MORE diffuse than the counts it comes from, and the diffuseness is NOT concentrated in a few
removable directions -- if it were, removing them would help and it makes things worse. The variance
is spread thin across the whole spectrum, which is what a random projection does to a signal.**
*No post-hoc transform reaches that. It is a property of how the code is WRITTEN.*

## 📚 2026-08-19 -- **THE OWNER'S Q72 ("GIVE IT ANOTHER TEXTBOOK") HAS TWO HALVES. THE HALF I**
## **TESTED IS UNTESTED-AT-THIS-N; THE HALF I DID NOT TEST ALREADY HARD_PASSED A MONTH AGO.**
*Owner, Q72: "Why aren't we identifying where the notes are PATCHY and/or giving them another
textbook? There's only so much you can get from one textbook."* They are two proposals and they have
different answers.

**HALF ONE -- PASSIVE BREADTH (read the same amount, spread over more sources). TESTED TODAY, AND
THE ANSWER IS "NO MEASURABLE DIFFERENCE", NOT "IT HURTS".** One variable, same total reading, each
arm scored against its own counter so a harder candidate pool cannot be mistaken for progress:

| | corpora | OUR median rank | counter median rank | ratio |
|---|---|---|---|---|
| ONE_CORPUS | 1 | 91.0 (CI 68.5-111.0) | 19.5 (CI 15.5-25.0) | 4.67x |
| MANY_CORPORA | 27 | 106.5 (CI 89.0-122.0) | 20.0 (CI 16.5-29.0) | 5.33x |

**MANY minus ONE, ours: +15.8, 95% CI [-10.0, +42.5] -- NOT separated from zero.** Counter: +1.2,
CI [-5.0, +10.0], also not separated. **⛔ SO THE HONEST VERDICT IS UNTESTED AT THIS n, AND I NEARLY
FILED IT AS A NEGATIVE:** the point estimates alone (91 -> 106.5) read as "diversity hurts us", and
the pre-committed third reading was written for exactly that. The CI says the width swallows it.
*Do not quote "spreading reading across corpora made it worse."*

**HALF TWO -- ACTIVE, GAP-TARGETED GROWTH (find the patchy bits, then go read for them). ALREADY
LANDED, HARD_PASS, AND I DID NOT KNOW IT WHEN I DESIGNED TODAY'S TEST.**
`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`, disk-verified:

    on_miss_ratio   0.348      per-token miss 0.43 -> 0.15
    coverage        0.50 -> 0.79   (d = +0.291)
    use_real_auc    0.8924     vs shuffle 0.5122 +- 0.1003, delta 0.3802
    retention_gap   0.852      n_sent 6000, n_grown 8422, n_escalations 2099

**➡️ THE OWNER'S INSTINCT IS RIGHT, BUT THE LOAD-BEARING WORD IS "PATCHY", NOT "ANOTHER TEXTBOOK".**
Reading more widely at random does nothing measurable. Reading TO FILL A NAMED GAP moves coverage
from half to four-fifths with a real-vs-shuffled separation of 0.38. *That is the same shape as
GAP == GROUNDING: naming the gap and traversing it are one act.*

**⚠️ AND "NON-ADDITIVE" MUST NOT BE READ AS "IN-PLACE EDITING" -- I CHECKED THE ARCHIVE BEFORE
PROPOSING IT THIS TIME.** `exp_additive_only_cert_cpu_v1` (MIDDLE_BAND) set out to certify that
additive writes stay stable while in-place edits accumulate error ~ edits^2/N and collapse recall.
**Disk-verified, the discriminator did NOT fire: additive@200 = 1.000 and in-place@200 edits =
1.000.** Both arms sat at ceiling, which is why it landed MIDDLE_BAND. *So that cell neither
supports nor blocks a non-additive write -- it is uninformative at that scale, and the honest
statement is that the question is OPEN.* What the geometry argues for is a write that can
CONCENTRATE variance -- competition, normalisation, sparsification, something learned -- **not
subtract-old-and-add-new, which is a different proposal that this cell tried and could not
discriminate.**

## 🟢🟢 2026-08-19 -- **THE OWNER REMEMBERED PRIOR WORK THAT PREDICTED TODAY'S FAILURE THREE WEEKS**
## **AGO, AND IT GIVES THE ORDER OF OPERATIONS: PREDICTION FIRST, NOVELTY SECOND, NOTES THIRD.**
*Owner, COMMENTARY 20:22Z: "on the note taking and a 'newness detector' - I think we did do some
work on this - so is worth looking back at the experimental corpus." They were right; I had not
looked.*
`exp_ingest_gate_strong_foundation_novelty_v2` (2026-07-16), verdict
**`SEMANTIC_NOVELTY_derivability_dose_dependent_on_foundation_strength`**:

| foundation strength (inferable MRR) | novelty-detection AUC |
|---|---|
| **DEAD 0.013** | **0.605 -- near chance** |
| WEAK 0.331 | 0.969 |
| STRONG 0.741 | 0.988 |

**dose-response +0.384; encoding-status AUC tracked separately (0.627 / 0.976 / 1.000) so the two
were never conflated; per-candidate arrays dumped and the key AUC RECOMPUTED OFF-DISK.**
**➡️ ITS CENTRAL SENTENCE EXPLAINS TODAY IN ONE LINE: *"surprise = can the CURRENT foundation
predict this, which BECOMES semantic-novelty as the foundation strengthens"* -- and *"a DEAD
non-generalizing foundation must COLLAPSE the KEY AUC to ~chance."***
**⛔ THAT IS EXACTLY WHAT TODAY'S RESIDUAL WRITE GATE DID.** Our profiles predict their own next
context only 10.4% better than an unrelated term's, and our median rank is 81 of 223 -- **we are in
the DEAD regime by this cell's own dial, where it MEASURED that novelty detection collapses to
chance.** *The gate did not fail because predictive coding is wrong. It failed because novelty
detection is DOWNSTREAM of prediction quality, and ours has none to speak of.*
**🎯 SO THE OWNER'S "NEWNESS GETS NOTES" PRINCIPLE IS RIGHT AND IS NOT YET BUILDABLE. The order is
forced: (1) make the foundation PREDICT, (2) novelty detection then works for free -- it is the
same signal -- (3) only then do notes-on-newness mean anything.** *Steps 2 and 3 are not separate
builds; they fall out of step 1. Everything today was an attempt at step 3 while step 1 was unmet.*
**⚠️ THE HONEST LIMIT, STATED BEFORE ANYONE CITES THIS: that dose-response was measured in a
SYNTHETIC compositional TransE arena, chosen deliberately because a strong generalizing foundation
does not exist on our real data (the same note records real CSKG capping at MRR ~0.13). TRANSFER TO
OUR SUBSTRATE IS A HYPOTHESIS, NOT A RESULT.** *But the DEAD-regime prediction is the part we
already match, and we match it exactly.*

## ✅ 2026-08-19 -- **9-SEED SWEEP FINAL. THE PRE-REGISTERED CONJUNCTION FAILS, AND THE TWO**
## **QUANTITIES SEPARATE CLEANLY -- ONE IS SOLID, THE OTHER IS NOISE AROUND A LOW CENTRE.**

| quantity | mean | median | min | max | sd | seeds passing |
|---|---|---|---|---|---|---|
| **union / counter** | **2.03** | 2.15 | **1.50** | 2.23 | 0.24 | **9 of 9** |
| independence ratio | 0.87 | 0.91 | 0.70 | 0.98 | 0.09 | **6 of 9** |

**⛔ VERDICT AS PRE-REGISTERED: FAILS.** The conjunction required ratio >= 0.85 AND union >= 1.5 on
EVERY seed. Union holds 9 of 9; the ratio holds 6 of 9. **The strong claim -- "the spoke is a
genuinely independent second channel" -- IS NOT ESTABLISHED, and no combination build proceeds on
it.**
**✅ WHAT NINE SEEDS BOUGHT THAT THREE COULD NOT: the two quantities have DIFFERENT RELIABILITY and
should never have been quoted as one finding.** The union gain is **tight and never below 1.50**.
The ratio is **noisy (sd 0.09) around a centre of 0.87-0.91, i.e. slightly BELOW independence**.
*So 0.70 was neither an outlier nor the centre -- it is the low tail of a distribution whose centre
sits just under the bar.*
**🎯 THE SURVIVING, DEFENSIBLE STATEMENT: the spoke and the counter succeed on almost entirely
DIFFERENT items -- only 1-6 of ~250 are ever got right by both, on every seed -- so combining them
would roughly double what counting achieves alone. What is NOT established is that the spoke's
unique contribution exceeds what chance overlap predicts.** *Both halves are needed; either alone
misleads.*
**⚠️ AND THE PROCESS NOTE THAT MATTERS MORE THAN THE RESULT: I characterised this quantity from 1
seed (0.94, "at independence"), then 4 (0.83), then 7 (0.88), then 9 (0.87). Three of those four
characterisations were wrong, and each was stated with more confidence than the data carried.
Nine seeds cost about 80 minutes of compute and prevented a build on a number that was never
there.*

## 📈 [SUPERSEDED BY THE FINAL 9-SEED READ ABOVE] 2026-08-19 -- **RUNNING READ, 7 OF 9 SEEDS: THE ESTIMATE HAS MOVED TWICE AND IS STILL MOVING.**
Ratios in landing order: **0.70 / 0.94 / 0.89 / 0.81 / 0.92 / 0.93 / 0.98**. Union/COOC:
**1.50 / 2.23 / 1.94 / 2.23 / 2.00 / 2.17 / 2.18 -- all seven >= 1.5.**
**My running mean has gone 0.94 (1 seed) -> 0.83 (4 seeds) -> 0.88 (7 seeds). Two of seven sit
below the 0.85 threshold; five clear it.**
*I have now characterised this quantity three times and been wrong twice. The honest statement at
7 seeds: **the union gain is STABLE and unambiguous (1.50-2.23, every seed); the independence
ratio is NOISY around ~0.88 with a low tail.** Those are different quantities with different
reliability, and only the first is safe to build on.*
**⚠️ AND THE PRE-REGISTERED CONJUNCTION STILL FAILS on the ratio arm, exactly as it did at 3
seeds. More data has NOT rescued it -- it has just made the failure better characterised.**
*2 seeds outstanding. The verdict is the 9-seed distribution, not this line.*

## 📉 [SUPERSEDED BY THE 7-SEED READ ABOVE] 2026-08-19 -- **RUNNING READ, 4 OF 9 SEEDS: THE FIRST SEED I HAPPENED TO RUN WAS THE BEST**
## **ONE, AND I CHARACTERISED THE FINDING FROM IT.**
Spoke-independence ratios as they land: **0.70 / 0.94 / 0.89 / 0.81** (seeds 20260819 / 7 / 101 /
13). Union/COOC: 1.50 / 2.23 / 1.94 / 2.23 -- **all four >= 1.5.**
**⚠️ I DESCRIBED THIS FINDING AS "~INDEPENDENT OF COUNTING (0.94)" OFF A SINGLE SEED. The running
mean is ~0.83, and 0.94 is the HIGHEST of four.** *Seed 7 was not cherry-picked -- it was simply
the first one I ran -- but a single seed is as likely to be the best of its distribution as the
worst, and I characterised a distribution from one draw of it. **The correction is not that the
finding is gone; it is that "at independence" was the top of the range, not the centre.***
**🔎 AND BOTH THINGS ARE TRUE AT ONCE, WHICH IS THE ACTUAL SHAPE: the ratio sits consistently a
little BELOW independence (~0.83), AND the union still nearly doubles counting -- because the
ABSOLUTE overlap is tiny (2-6 items of ~250).** A slight positive correlation in which items each
arm gets right coexists with almost no shared successes. *Neither "complementary" nor "subsumed"
is the right word; the honest statement needs both numbers.*
*5 seeds still to land. No verdict until they do.*

## 🔎 2026-08-19 -- **THE INSTRUMENT IS NOT FREQUENCY-DOMINATED, AND THAT MAKES OUR RESULT WORSE.**
A `FREQ_floor` that never looks at the cue beat every cortical arm at k>=10, which raised the
question of whether this task is winnable by cue at all. **It is.** From the v3 metrics already on
disk, no new run:

| seed | COOC@10 | FREQ@10 | ratio | COOC@50 | FREQ@50 | ratio |
|---|---|---|---|---|---|---|
| 101 | 0.3933 | 0.1667 | **2.36x** | 0.7633 | 0.4867 | 1.57x |
| 20260819 | 0.4067 | 0.1767 | **2.30x** | 0.7533 | 0.4700 | 1.60x |
| 7 | 0.3667 | 0.2167 | 1.69x | 0.7233 | 0.4567 | 1.58x |

**Counting beats the cue-blind floor by 2.12x at k=10 and 1.59x at k=50, on every seed, and by
median rank 15-20.5 against 52-61 -- roughly 3x.**
**⛔ SO THE TASK HAS REAL CUE-EXPLOITABLE SIGNAL AND COUNTING HARVESTS IT. THE EXCUSE THAT "THIS
INSTRUMENT MOSTLY MEASURES WORD FREQUENCY" IS NOT AVAILABLE.** *Our arms losing to `FREQ_floor` is
therefore not a property of the task being frequency-shaped -- it is our representation failing to
use a cue that a word counter uses successfully. That reading is strictly worse for us than the
one I flagged two blocks ago, and it is the correct one.*

## 🟡 2026-08-19 -- **THE SPOKE REPLICATION: PARTIAL. BY MY OWN PRE-REGISTRATION IT DOES NOT**
## **REPLICATE, AND I AM HONOURING THAT RATHER THAN RE-READING THE THRESHOLD.**
`scratch/diag_spoke_independence_seeds.py`, 3 seeds, 8,000 sentences each, n=246-277.

| seed | n | SPOKE | COOC | both | spoke-only | predicted | ratio | **union/COOC** |
|---|---|---|---|---|---|---|---|---|
| 20260819 | 277 | 0.0614 | **0.0794** | 6 | 11 | 15.6 | **0.70** | 1.50 |
| 7 | 246 | 0.0732 | 0.0528 | 2 | 16 | 17.0 | 0.94 | 2.23 |
| 101 | 250 | 0.0720 | 0.0640 | 3 | 15 | 16.8 | 0.89 | 1.94 |

**PRE-REGISTERED: ratio >= 0.85 AND union >= 1.5 on ALL THREE. Union holds 3 of 3 (1.50 / 2.23 /
1.94). Ratio holds 2 of 3 -- seed 20260819 reads 0.70. THE CONJUNCTION FAILS, so the strong claim
is NOT established and the combination build DOES NOT PROCEED.**
**⚠️ AND I AM FLAGGING THE TEMPTATION RATHER THAN ACTING ON IT.** Last turn I argued that the
UNION GAIN is the correct discriminator, and union passes 3 of 3 here. Adopting it now, when it is
the criterion that rescues the result, would be motivated reasoning **even though I named it
before seeing this data**. *The pre-registration for THIS run required both. Both is what it gets.*
**✅ WHAT SURVIVES, NARROWED AND USEFUL: the union gain is CONSISTENT (1.50-2.23 on every seed),
and only 2-6 of ~250 items are ever got right by BOTH arms.** So the channels do overlap very
little; what is NOT stable is whether the spoke's unique contribution sits at or below what
independence predicts. **AND THE SPOKE DOES NOT BEAT COUNTING: it wins 2 seeds and LOSES the third
(0.0614 vs 0.0794), which is the same tie reading (B) already gave on the precision instrument.**
**➡️ NEXT IS MORE SEEDS, NOT A BUILD.** The quantity that moved is a ratio of small counts
(11-16 spoke-only against a ~16 prediction); 3 seeds cannot separate real instability from
sampling noise at that count. *Anything built now would rest on the one seed that happened to fire.*

## 🔴🔴 2026-08-19 -- **v3 SETTLES IT: THE CORTICAL READ RETRIEVES AND IS NOT COMPETITIVE.**
## **18 OF 18 FLOOR CELLS FAIL. AND A CUE-BLIND FREQUENCY RANKING BEATS IT AT k>=10.**
`v3_floors_at_k`, 3 seeds, 966 s, 300 items/seed, 428-480 candidates. **I recorded the prediction
BEFORE the run (`3ca164923`): "I expect v3 to show the route does NOT clear the floor." It does not.**

| seed 20260819 | hit@1 | hit@10 | hit@50 | median rank |
|---|---|---|---|---|
| **RANK_COOC_floor** | **0.0867** | **0.4067** | **0.7533** | **15** |
| RANK_FREQ_floor *(never sees the cue)* | 0.0400 | 0.1767 | 0.4700 | 61 |
| RANK_BOTH | 0.0300 | 0.1533 | 0.3967 | 69 |
| RANK_CONTEXT | 0.0567 | 0.1800 | 0.3433 | 126 |
| RANK_SCRAMBLE | 0.0067 | 0.0367 | 0.1900 | 173 |

**⛔ `CONTEXT_clears` AND `BOTH_clears` ARE FALSE AT EVERY k ON EVERY SEED -- 18 of 18 cells.**
Counting puts the target at median rank **15-20 of ~450**; our best arm puts it at **69-79**.
**🚨 AND THE PART I DID NOT PREDICT, WHICH IS WORSE THAN THE PREDICTION: `FREQ_floor` -- a ranking
that NEVER LOOKS AT THE CUE -- BEATS every cortical arm at k>=10** (hit@50 0.4700 vs BOTH's 0.3967
and CONTEXT's 0.3433). *The route does use its cue: it beats SCRAMBLE, CI-separated, on every seed.
But most of the achievable score on this task comes from knowing WHICH TERMS ARE COMMON, and a
constant ranking harvests more of that than our cue-dependent route does.* **That is what the
frequency floor exists to expose, and it is the first time this session it has caught something.**
**➡️ THIS CLOSES THE CORTICAL READ AS A LINE OF WORK. Both claims are now established and they must
travel together: IT RETRIEVES (reading A fires, 3 seeds) and IT IS NOT COMPETITIVE (0 of 18 floor
cells). Combined with the subsumption result -- unique contribution BELOW independence at every k --
there is nothing left to build here.** *The accumulated-context representation is the ceiling, not
the read-out, and that has now been shown three independent ways.*

## ✅ [SUPERSEDED BY v3 ABOVE, WHICH ADDS THE FLOORS v2 LACKED] 2026-08-19 -- **v2 LANDED, 3 SEEDS: READING (A) FIRES. THE CORTICAL READ RETRIEVES --**
## **AND THE CELL CANNOT SAY WHETHER IT BEATS COUNTING, WHICH IS A GAP I BUILT.**
`exp_cortical_read_consolidated_v1` spec `v2_hitk_sentencecue`, 811 s, 300 items/seed, 428-480
consolidated terms. **`READING (C): [True, True, True]` -- the cue fix held on every seed.**
**k where REAL clears SCRAMBLE's upper CI AND chance: [1,5,10,25,50] / [1,5,10,25,50] / [5,10,25,50].**

| seed 20260819 | hit@1 | hit@10 | hit@50 | median rank |
|---|---|---|---|---|
| RANK_CONTEXT | 0.0567 | 0.1800 | 0.3433 | 126 |
| RANK_SPOKE | 0.0100 | 0.1067 | 0.3433 | **82** |
| **RANK_BOTH** | 0.0300 | 0.1533 | **0.3967** | **69** |
| RANK_SCRAMBLE | 0.0067 | 0.0367 | 0.1900 | 173 |
| chance | 0.0023 | 0.0234 | 0.1168 | -- |

**🟢 `BOTH` HAS THE BEST MEDIAN RANK ON ALL THREE SEEDS (69 / 75.5 / 79) and the best hit@50 on two
-- while SPOKE ALONE has a better median (82-88) than CONTEXT (115-126) despite a WORSE hit@1.**
*The two channels are good at different things, which is the independence result showing up
independently in a different table.*
**⛔ THE GAP, AND IT IS MINE: I computed hit@k for the cortical arms and the scramble BUT NOT FOR
THE FLOORS.** So reading (A)'s bar is *"clears SCRAMBLE and chance"*, which is WEAKER than this
project's standard *"clears the strongest floor's upper bound"*. **THIS TABLE THEREFORE CANNOT SAY
WHETHER THE CORTICAL READ BEATS COUNTING AT ANY k, AND MUST NOT BE READ AS SAYING SO.**
*The separate subsumption diagnostic already indicates it does not -- COOC hit@50 0.6800 vs
cortical 0.3767 at 223 candidates -- but that is a different pool size and does not transfer.*
**➡️ FIX: add `COOC_floor` and `FREQ_floor` to the hit@k block. Until then the honest claim is
"the route retrieves", NOT "the route is competitive".**

## 🟢 2026-08-19 -- **THE SPOKE IS NOT SUBSUMED. IT IS ~INDEPENDENT OF COUNTING, AND THE UNION**
## **MORE THAN DOUBLES IT. THE CONTRAST WITH THE CORTICAL ROUTE IS THE FINDING.**
`scratch/diag_spoke_complementary_or_subsumed.py`, on the spoke's OWN instrument (grounded terms,
co-occurring candidates, provenance-filtered ConceptNet gold), 8,150 sentences, n=246.

| | SPOKE | COOC | both | spoke-only | predicted | ratio | **UNION / COOC** |
|---|---|---|---|---|---|---|---|
| spoke | 0.0732 | 0.0528 | **2** | 16 | 17.0 | **0.94** | **0.1179 / 0.0528 = 2.2x** |
| cortical (for contrast) | 0.3767 | 0.6800 | 93 | 20 | 36.2 | 0.55 | 0.7467 / 0.6800 = **1.1x** |

**⚠️ MY PRE-REGISTRATION WAS MIS-SPECIFIED AND I AM NOT GOING TO READ IT LITERALLY.** I wrote
"materially ABOVE independence -> complementary; AT OR BELOW -> subsumed", which lumps *at
independence* together with *below independence*. **Those mean OPPOSITE things for buildability.**
A ratio of 0.94 means the two arms succeed on DIFFERENT items at chance-overlap rates -- only
**2 of 246** items were got right by both -- which is precisely the case where combining them pays.
Subsumption is ratio << 1 **AND** union ~= the stronger arm alone. **The correct discriminator is
the UNION GAIN, and by it the two channels separate cleanly: the spoke's union is 2.2x counting,
the cortical route's was 1.1x.**
**➡️ SO THE SPOKE IS A REAL SECOND CHANNEL AND THE CORTICAL ROUTE WAS NOT.** *That is exactly what
the hub-and-spoke frame predicts: a spoke carries modality information text does not, while another
way of reading the same text-derived profiles carries nothing new.*
**⛔ POWER, STATED HONESTLY: the counts are SMALL -- 18 spoke hits, 13 counting hits, 2 overlapping,
n=246. The direction is clear and the union gain is large, but this is ONE measurement at low
count and it needs seeds before it is quoted as a result.** *It also does NOT rescue the spoke's
tie on precision (reading B, 0 of 3 seeds significant) -- a tie plus independence means two
comparable channels, not a better one.*

## 🔴🔴 2026-08-19 -- **THE CORTICAL ROUTE IS SUBSUMED BY WORD COUNTING. NOT MERELY BEATEN --**
## **ITS UNIQUE CONTRIBUTION IS BELOW WHAT INDEPENDENCE PREDICTS, AT EVERY k.**
`scratch/diag_complementary_or_subsumed.py`. **This is the FIXED route (sentence cue), not the
broken one** -- so it is the best version of our representation, on held-out text, over the same
candidate set as the counter. 4,300 sentences, 223 candidates, n=300.

| k | CORTICAL | COOC | both | **cortical-only** | independence predicts | **ratio** |
|---|---|---|---|---|---|---|
| 1 | 0.0567 | 0.0433 | 4 | 13 | 16.3 | **0.80** |
| 10 | 0.1300 | 0.3367 | 27 | 12 | 25.9 | **0.46** |
| 50 | 0.3767 | 0.6800 | 93 | 20 | 36.2 | **0.55** |

**⛔ AT EVERY k THE CORTICAL-ONLY CELL IS BELOW ITS INDEPENDENCE PREDICTION.** The two routes are
POSITIVELY correlated in what they get right, and our route's unique contribution is *smaller than
chance would give* -- it is not a different view of the problem, it is a WEAKER VIEW OF THE SAME
ONE. *"Scores lower" and "knows nothing new" are different claims, and this is the second.*
**⛔ AND THE GAP WIDENS WITH k: at hit@50 counting reaches 0.6800 against our 0.3767.** The union
oracle -- an impossible arm that always picks the better route -- reaches only 0.7467, barely above
counting alone, which is exactly the signature of subsumption rather than complementarity.
**➡️ THE CONSEQUENCE, AND IT IS A STOP RATHER THAN A PIVOT: STOP BUILDING READ-OUT VARIANTS ON THE
ACCUMULATED-CONTEXT REPRESENTATION.** Three read-out variants have now been built on it (episodic,
cortical-context, cortical-both) and the ceiling is not in the read-out. **The lever is the
REPRESENTATION or the SUPPLY, never another way of querying the same profiles.**
**⚠️ SCOPE, STATED: one seed, one corpus, 4,300 sentences, 223 candidates, held-out only. The
direction is unambiguous at every k but the exact ratios are a single measurement.**

## 🟢🟢 2026-08-19 -- **v2 SEED 1: THE CUE FIX WORKED AT FULL SCALE, AND THE SCRAMBLE COLLAPSED.**
Same seed, same 16,600 sentences, same 428 consolidated terms -- **only the cue construction and
the scorer changed.**

| arm | v1 (profile-sum cue) | **v2 (sentence cue)** |
|---|---|---|
| CORTICAL_CONTEXT | 0.0433 | **0.0567** |
| **SCRAMBLE** | **0.0500** | **0.0067** |

**⛔ THAT IS THE WHOLE VOID VERDICT EXPLAINED: the scramble arm fell 7.5x while the real arm rose.**
v1's arms were indistinguishable because the profile-sum cue let an UNRELATED donor sentence score
almost as well as the real one; querying the space the index is actually built in removes that.
**SO THE ANSWER TO THE OPEN CONFOUND IS CUE CONSTRUCTION, NOT SCALE** -- this is the cell's own
scale, unchanged.
**⚠️ ONE SEED. `COOC_floor` still leads at 0.0867 and the cortical arms have NOT beaten it. Reading
(A) needs REAL to clear SCRAMBLE **and** chance at the same k, per-seed, across three seeds -- the
hit@k table decides that, not this line.** *Do not quote 0.0567 as a capability.*

## ⚠️ 2026-08-19 -- **CORRECTION TO MY OWN "4.9x" -- A THIRD OF THE SEEN CONTROL WAS A VECTOR**
## **MATCHING ITSELF. THE READING SURVIVES; THE MAGNITUDE WAS OVERSTATED BY ME.**
`scratch/diag_seen_control_is_inflated.py`. A term's profile IS THE SUM OF THE CONTEXT VECTORS IT
WAS SEEN IN, so on SEEN text the cue sentence's own context vector is one of the summands and the
cosine is partly **a vector against itself**. I applied this project's no-leak rule to the TARGET
TOKEN and never to the CUE SENTENCE.

| SEEN cue-to-target cosine | value |
|---|---|
| FULL profile (**what I published**) | 0.2588 |
| **LEAVE-ONE-OUT** (cue's own trace removed) | **0.1702** |
| self-match contribution | **+0.0886 = 34% of the full value** |

**POSITIVE CONTROL BINDS: exactly 1 trace removed on 200 of 200 items** -- the leave-one-out was
not vacuous, which is the empty-set trap that already caught me once today.
**➡️ THE CORRECTED NUMBER: the memorise-vs-transfer drop is 3.3x, NOT the 4.9x I published two
turns ago (0.1702 / 0.0519, not 0.2551 / 0.0519).** *The DIRECTION and the reading are unchanged --
profiles still memorise far better than they transfer -- but anyone quoting "4.9x" is quoting a
number inflated by a third by self-match.* **USE 3.3x.**
*Nothing else in that diagnostic moves: the held-out side never had this confound (the cue sentence
was never read, so it contributed no trace), and the hit@k separation is measured on held-out only.*

## 🟢 2026-08-19 -- **THE CORTICAL READ DOES RETRIEVE. READING (A) FIRES AT EVERY k -- AND THE**
## **CELL'S VOID VERDICT IS PART CUE-CONSTRUCTION DEFECT, WHICH IS MINE.**
`scratch/diag_cortical_hit_at_k.py` + `scratch/diag_cue_construction_one_variable.py`, 4,300
sentences, 223 consolidated terms, n=300 held-out items, ties broken AGAINST us.

| k | chance k/N | REAL | SCRAMBLE | CI-separated |
|---|---|---|---|---|
| 1 | 0.0045 | **0.0567** [0.033,0.083] | 0.0067 [0.000,0.017] | ✅ |
| 10 | 0.0448 | 0.1300 [0.093,0.170] | 0.0533 [0.030,0.077] | ✅ |
| 50 | 0.2242 | **0.3767** [0.323,0.427] | 0.2367 [0.190,0.283] | ✅ |

**Median target rank 82 vs the scramble's 108, of 223. REAL beats chance k/N at EVERY k.** *This is
retrieval, NOT discrimination -- being in a top-50 of 223 is not knowing the answer, and it must
not be upgraded into a capability claim.*

**🔧 THE ONE-VARIABLE TEST, SCALE HELD FIXED, ONLY THE CUE VARIED:**

| cue construction | median rank | hit@1 | hit@10 | hit@50 |
|---|---|---|---|---|
| **SENTENCE (`context_vector_masked`)** | 82 | ✅ sep | ✅ sep | ✅ sep |
| **PROFILE-SUM (`cortical_recall.cue_vector`, what the CELL used)** | 74 | ✅ sep | ❌ | ❌ |

**⚠️ A DEFECT IN MY OWN ORGAN, NAMED PRECISELY: the index is built from accumulated CONTEXT
VECTORS, and `cue_vector` queries it with a SUM OF PER-LEMMA PROFILES -- a different kind of
object.** The profile-sum cue is not signal-free (median rank 74 is actually the better of the
two), but **its SCRAMBLE retains far more signal** (hit@50 0.3177 vs the sentence cue's 0.2367),
which is exactly what collapses the separation the cell was testing for.
**⛔ AND THE HONEST LIMIT: SCALE IS STILL UNCONTROLLED between these diagnostics (4,300 sentences,
223 terms) and the cell (16,600 sentences, 428-480 terms). So cue construction is DEMONSTRATED to
matter and is NOT demonstrated to be the whole explanation of the void.** *The cell's own
CORTICAL_CONTEXT hit@1 of 0.0100-0.0433 brackets the profile-sum cue's 0.0234 here, which is
consistent; its SCRAMBLE of 0.0233-0.0500 against 0.0000 here is not, and scale is the open
suspect.*
**➡️ NEXT: fix `cue_vector` to query the space the index is actually built in, then RE-RUN THE CELL
AT THE CELL'S OWN SCALE with hit@k arms. Both changes are needed and only the re-run settles it.**

## 🔬 2026-08-19 -- **THE REPRESENTATION DIAGNOSTIC. THE SPACE IS NOT BROKEN AND NOT A BLOB: THE**
## **SIGNAL IS THERE ON HELD-OUT TEXT AND IS 4-7x WEAKER THAN ON READ TEXT.**
`scratch/diag_cue_vs_profile_space.py`, 4,300 sentences, 223 consolidated terms, n=200 per
condition. Measured on the VECTORS directly rather than through hit@1, with the SEEN condition as
the positive control.

| question | HELD-OUT | SEEN (control) |
|---|---|---|
| cue vs its own target | **0.0519** | 0.2551 🔴 inflated, see below: leave-one-out 0.1702 |
| SCRAMBLED cue vs that target | 0.0231 | 0.1345 |
| **gap (the void condition)** | **+0.0288** | **+0.1206** |
| cue-to-target vs cue-to-RANDOM term | +0.0318 | +0.2218 |
| argmax concentration | 112 distinct winners / 200 cues, top 7.5% | 96 / 200, top 11.5% |

**✅ THREE THINGS ARE RULED OUT.** The measurement is not broken (the control separates strongly).
The index is not degenerate -- 112 distinct winners over 200 cues, no hub. And the held-out gap is
**NOT zero**: +0.0288 real-vs-scramble, +0.0318 target-vs-random.
**⚠️ SO I MUST NARROW MY OWN VOID VERDICT. Reading (C) fired as pre-registered and the cell's
numbers remain void AS A CAPABILITY CLAIM -- that stands. But the MECHANISM is not "the route
ignores the cue". It is "the cue carries a real but very weak signal, and a top-1 argmax over 223
candidates cannot resolve +0.03".** *The scramble arm is not signal-free either (0.0231 vs a
random-term 0.0201), which is exactly why hit@1 could not separate them at n=300.*
**➡️ THIS IS THE PROGRAMME'S STANDING DIAGNOSIS ARRIVING ON A FOURTH INSTRUMENT, AND FOR THE FIRST
TIME AT THE VECTOR LEVEL: the profiles MEMORISE AND BARELY TRANSFER.** Not a retrieval bug, not a
code bug -- the representation itself.
**🔴 THE NUMBERS ON THIS LINE WERE 0.2551 READ / 0.0519 UNREAD, "a 4.9x drop". THAT SEEN FIGURE IS
INFLATED BY SELF-MATCH AND IS RETRACTED AT SOURCE. Leave-one-out gives 0.1702, so the drop is
3.3x. USE 3.3x -- see the correction block at the top of this file.**
**➡️ NEXT, AND IT IS THE DISTINCTION THIS PROJECT ALREADY ESTABLISHED: score hit@k, not hit@1.**
Retrieval dwarfs discrimination here on four corpora already; a +0.03 signal may well place the
target in the top-50 of 223 while never winning top-1. **If hit@50 is above chance, the cell was
measuring the wrong thing rather than measuring nothing.**

## 🔴 [SEE THE DIAGNOSTIC ABOVE: THE MECHANISM IS "SIGNAL TOO WEAK FOR TOP-1", NOT "IGNORES THE CUE"] 2026-08-19 -- **THE CORTICAL READ CELL IS VOID BY ITS OWN READING (C). NOT A NEGATIVE -- VOID.**
`exp_cortical_read_consolidated_v1`, 3 seeds, 1,594 s, 300 items each, 428-480 consolidated terms.
**`READING (C) route reads the cue: [False, False, False]` -- the SCRAMBLE arm (an UNRELATED donor
sentence) TIES OR BEATS the real cue on ALL THREE SEEDS.** My pre-registration says exactly what
that means: *"the route is not reading the cue and EVERY other number in this cell is void."*

| seed | CTX | SPOKE | BOTH | EPI | COOC (floor) | SCRAM |
|---|---|---|---|---|---|---|
| 101 | 0.0200 | 0.0033 | 0.0100 | 0.0000 | **0.0900** | 0.0233 |
| 20260819 | 0.0433 | 0.0100 | 0.0233 | 0.0000 | **0.0867** | 0.0500 |
| 7 | 0.0100 | 0.0100 | 0.0200 | 0.0000 | **0.0700** | 0.0233 |

*p(SCRAMBLE vs CORTICAL_CONTEXT) = 1.0000 / 0.8081 / 0.2704 -- nowhere near separated.*
**⛔ DO NOT REPORT "the cortical read scores 0.02" AS A CAPABILITY, AND DO NOT REPORT COOC BEATING
IT AS A COMPARISON.** Both are void: an arm that scores the same on an unrelated sentence is not
reading anything. The credible bar was 0.1000-0.1233 and nothing came close. *`EPISODIC_FILTERED`
reads 0.0000 on every seed -- the episodic route, restricted to consolidated candidates, never once
retrieves the right one.*
**➡️ WHAT THIS DOES AND DOES NOT SAY. It does NOT say a cortical read is impossible; it says THIS
one, on THIS task, is not reading its cue. The organ's self-tests pass on synthetic fixtures where
the families are separable, so the failure is in the REPRESENTATION the cue and the index are built
from -- accumulated context profiles -- not in the retrieval code.** *Next diagnostic, not next
build: check whether held-out cue vectors and consolidated-term profiles occupy the same space at
all before building anything else on them.*

## ⛔⛔ CORRECTION TO MY OWN CORRECTION, 2026-08-19. **I WAS RIGHT, THEN I "CORRECTED" MYSELF INTO**
## **BEING WRONG. THE BLOCK BELOW IS THE WRONG ONE. VERIFIED AT RUNTIME, TWICE.**
**`checkpoint` defaults `pbv=False`, and the substrate never passes `pbv=True`. Instrumented at
runtime: `_make_grounding_gate` fires 5 times, `_make_pbv_grounding_gate` ZERO. Refusals are
`TAUTOLOGY_NO_ANCHOR` (297) and `CLOSED_CLASS_SUBJECT` (48) -- both the OLD gate's reasons.
THE OLD GATE IS LIVE.**
**So my ORIGINAL v2 replay used the RIGHT rule, the 31.8% IS explained by anchor-field growth as
first stated, and my provenance fix went into the LIVE path all along.** *Verified: 36 of 36
successful gate decisions carried `n_anchors` + `anchor_field_sha1`.*
**🧪 AND THE THING THAT FOOLED ME: `state.gate_decisions` IS DRAINED EVERY PASS.** Peak during the
run 23, after the run **0** -- so reading it afterwards shows zero even though 36 decisions were
recorded. I read an emptied dict, concluded the branch was dead, and published a correction that
reversed a claim that had been right. **The lesson is the one I keep re-learning: I diagnosed by
READING the code and was wrong both times; both were settled in one runtime instrumentation.**
*The PBV fingerprint I added last turn sits in a path that does not execute. Harmless, left in
place with this note, and NOT to be cited as live provenance.*

## ⛔ [THIS BLOCK IS THE WRONG CORRECTION -- SEE ABOVE] CORRECTION 2026-08-19, TO THE BLOCK DIRECTLY BELOW, WHICH I COMMITTED AND WHICH IS WRONG
## **I REPLAYED A RULE THE SYSTEM DOES NOT RUN. The 31.8% is explained by that, NOT primarily by**
## **anchor-field growth, and the auditability claim below is OVERSTATED.**
**`checkpoint` runs with `pbv=True`, which selects `_make_pbv_grounding_gate` -- NOT
`_make_grounding_gate`.** The PBV gate's meaning is **`h.obj`, a STANDING HYPOTHESIS carried
across encounters**; it does **not** canonicalize at consolidation time, and its own docstring says
the summed-trace argmax is the OLD rule it replaced. **My v2 "exact" replay called `canonicalize`
on summed traces -- the retired rule. Of course it did not reproduce the live decision.**
**🧪 AND THE VERIFICATION I WROTE FOR MY OWN FIX PASSED VACUOUSLY:** it asserted "gate decisions
MISSING the new fields: 0" over **ZERO gate decisions**, because I had instrumented the dead
branch. *An absence check over an empty set. Fifth recorded instance of a checker sharing a flaw
with what it checks.*
**✅ WHAT SURVIVES, NARROWED:** the anchor field DOES grow during a pass and `canonicalize` DOES
scan it as-of-call, so a canonicalize-based decision is genuinely path-dependent. **But the live
gate's decision is MORE traceable than I said** -- `gate_decisions` already stores the full
hypothesis record: `proposed_pass`, `proposed_at_n_traces`, `n_confirm` / `n_disconfirm`, the
rejected list and the entire `hypothesis_log`. **The un-recorded quantity is narrower than "the
path": it is the ANCHOR FIELD THE PROPOSER SCANNED at propose time.**
**🔧 FIX APPLIED TO THE LIVE GATE:** `n_anchors_at_bank` + `anchor_field_sha1_at_bank` now recorded
in the PBV gate, which bounds the propose-time field from above. *Pinning the propose-time field
itself belongs in the proposer and is NOT done yet.*
**➡️ THE BUILD CONCLUSION IS UNCHANGED AND IS THE USEFUL PART: the spoke-vs-gate comparison still
cannot be made post-hoc, and must be an ONLINE arm.** It just has to be an arm on the PBV
HYPOTHESIS PROPOSER, not on `canonicalize`.

## 🔴 [SEE THE CORRECTION ABOVE -- THIS BLOCK'S CAUSAL CLAIM IS WRONG] 2026-08-19 -- **THE GATE'S DECISION CANNOT BE REPLAYED FROM THE FINAL STATE. TWO CONTROLS**
## **FAILED BEFORE THAT WAS CLEAR, AND IT IS AN AUDITABILITY PROBLEM, NOT A PROBE PROBLEM.**
`scratch/probe_gate_exact_v2.py`. v2 calls **the gate's own `canonicalize`**, on the gate's own
vector (the Library item's summed traces), with the gate's own `is_eligible_meaning` predicate and
its own `SENSE_MATCH_THRESH=0.45` -- it recomputes NOTHING. It still reproduces only
**71 of 223 decisions (31.8%)**.
**⛔ SO THE ANSWER TO v1's OPEN QUESTION IS NEITHER OF THE TWO I NAMED.** Not "the gate
underperforms its own rule" and not merely "my cosine was wrong": **THE GATE'S DECISION IS
PATH-DEPENDENT AND THE PATH IS NOT RECORDED.** `canonicalize` scans `space.anchors()` AS IT WAS AT
DECISION TIME; by the end of the read the field has grown to 273 anchors, so a replay argmaxes over
a strictly larger set than the gate ever saw. *The codebase already knew this -- `FrozenAnchorSpace`
(READ-OUT FIX 3) exists precisely so a verification episode "compares against a STABLE field instead
of a field that grew under it". I did not connect it until two controls had failed.*
**🚨 THE CONSEQUENCE IS BIGGER THAN THE PROBE. The substrate's stated output is an AUDITABLE store
of facts, and one of its central decisions cannot be re-derived from the artifact it leaves.**
Provenance records the subject, the object and the sentence -- **not the anchor field the choice
was made against.** A fact you cannot re-derive is a fact you can only take on trust.
**➡️ AND IT SETTLES THE BUILD DESIGN, WHICH IS THE USEFUL PART: THE SPOKE-vs-GATE COMPARISON
CANNOT BE MADE POST-HOC AT ALL.** It has to be made ONLINE, inside the gate, with both rules
scoring the same decision against the same field at the same moment. **That is the wiring
experiment itself, so the pre-build probe collapses into the build.** *Two failed controls were
the cheap way to find that out; building a post-hoc comparison cell would have been the expensive
way.*
**📌 SEPARATE, SMALL, AND WORTH DOING ANYWAY: record the anchor-field size (and ideally a hash of
`space.anchors()`) in the provenance row at decision time.** Cheap, and it makes every future
grounding decision re-derivable.

## ⚠️ 2026-08-19 -- [v1, SUPERSEDED BY THE BLOCK ABOVE] **A PRE-BUILD PROBE WHOSE OWN POSITIVE CONTROL FAILED. READ THE CAVEAT FIRST.**
`scratch/probe_spoke_vs_gate_on_anchors.py`, 4,300 sentences, 273 anchors, 209 scorable grounded
terms, gold = provenance-filtered ConceptNet. **Built to answer one question BEFORE wiring the
spoke into the consolidation gate: the spoke's win over the gate was measured on CO-OCCURRING
candidates, and the gate chooses among ANCHORS -- a different population, so discipline 2 says it
does not transfer.**

| arm | hits | n | precision |
|---|---|---|---|
| GATE_ACTUAL (what the gate chose) | 12 | 209 | 0.0574 |
| **CONTEXT_COS (the gate's OWN rule, recomputed)** | 20 | 209 | **0.0957** |
| SPOKE_NEAREST (the candidate wiring) | 21 | 181 | 0.1160 |
| RANDOM_ANCHOR | 0 | 209 | 0.0000 |

**⛔ THE POSITIVE CONTROL FAILED, AND I PRE-COMMITTED TO WHAT THAT MEANS.** `CONTEXT_COS` exists to
check that this probe reproduces the gate's decision; it reads **0.0957 against the gate's 0.0574**,
which is NOT the same decision. My own pre-registered text says: *"If it does not, this probe is
not looking at the gate's decision and NEITHER arm means anything."* **So SPOKE_NEAREST 0.1160 vs
GATE_ACTUAL 0.0574 IS NOT A CLEAN COMPARISON AND MUST NOT BE QUOTED AS ONE**, and the pre-committed
"wire it" trigger does NOT fire. *Also unpaired: 181 vs 209 items, because only anchors with
sensorimotor norms can be ranked by the spoke.*

**🔎 BUT THE FAILURE IS ITSELF THE INTERESTING SIGNAL, AND IT IS A HYPOTHESIS, NOT A RESULT: THE
GATE MAY BE UNDERPERFORMING ITS OWN SIMILARITY RULE.** A plain cosine argmax over the same anchors
scored 20 hits where the gate scored 12. Two live explanations and the probe cannot separate them:
(i) the gate's extra machinery -- encounter-time decision, `SENSE_MATCH_THRESH=0.45`, margin-z, a
growing anchor field -- COSTS accuracy against a plain consolidation-time argmax; or (ii) my
recomputation is simply not the gate's rule. **(ii) is the null and is the more likely of the two.**
**➡️ WHAT SETTLES IT, AND IT IS CHEAP: reproduce the gate's decision EXACTLY by calling the organ's
own `canonicalize` path rather than re-deriving cosine, and re-run PAIRED on the common subset.
Do that BEFORE any wiring.** *Do not build on a probe whose control did not bind.*

## 🟡 2026-08-19 -- **THE SENSORIMOTOR SPOKE LANDED. READING (B) FIRES: IT TIES THE TEXT CHANNEL.**
`exp_sensorimotor_spoke_grounding_v1`, 3 seeds, 4,150 s, n=327-361 scorable per seed, NOT
underpowered. Scored on the CORTICAL instrument (ConceptNet gold), bar pre-registered as
`TOP_COOCCURRENT`.

| arm | seed 101 | seed 20260819 | seed 7 | paired p vs SPOKE |
|---|---|---|---|---|
| **SPOKE_EUCLID** | 0.0699 (23) | 0.0526 (19) | 0.0703 (23) | -- |
| SPOKE_COSINE | 0.0729 (24) | 0.0582 (21) | 0.0887 (29) | 1.0000 / 0.7206 / 0.0600 |
| **TOP_COOCCURRENT** (THE BAR) | 0.0517 (17) | 0.0499 (18) | 0.0673 (22) | **0.3353 / 1.0000 / 1.0000** |
| **SHUFFLED_NORMS** (can-fail) | 0.0182 (6) | 0.0166 (6) | 0.0275 (9) | **0.0025 / 0.0080 / 0.0145** |
| RANDOM_CANDIDATE | 0.0182 (6) | 0.0194 (7) | 0.0153 (5) | 0.0010 / 0.0190 / 0.0020 |
| SUBSTRATE (the gate's own anchor) | 0.0274 (9) | 0.0194 (7) | 0.0275 (9) | **0.0155 / 0.0290 / 0.0170** |

**✅ READING (C) PASSES ON ALL THREE SEEDS: THE NORMS GENUINELY CARRY THE ARM.** Permuting every
profile onto another word, marginals preserved, costs ~2.5-3x the hits and separates at p<0.05
every time. *The channel is reading something real -- that is not in doubt.*
**⛔ READING (B) FIRES: IT IS A TIE WITH COUNTING. SPOKE is higher in 3 of 3 seeds and significant
in 0 of 3** (+1, +1, +6 hits; p 1.0000 / 1.0000 / 0.3353). **DO NOT REPORT THIS AS A WIN.** *It is
a negative FOR THIS WIRING, and it is NOT a refutation of the 0.6413 sensorimotor finding, which
was a different task, scorer and population.*
**🟢 NOT PRE-REGISTERED AND THEREFORE HYPOTHESIS-ONLY, BUT IT REPLICATES 3/3: THE SPOKE PICKS
BETTER MEANINGS THAN OUR OWN CONSOLIDATION GATE** -- 0.0639 pooled vs SUBSTRATE's 0.0248, p<0.05
every seed. *So the gate is the weaker link, not the spoke.*
**⚠️ AND MY OWN METRIC CHOICE IS REFUTED ON THE REAL INSTRUMENT. I pre-registered EUCLID as
primary off a fixture probe (synonym-vs-sibling, 1.348 vs 0.511 pooled SDs). On the actual task
COSINE scores >= EUCLID in ALL THREE SEEDS (24v23, 21v19, 29v23).** *A hand-built fixture probe
did not transfer to the instrument. The sweep is what caught it; adopting euclid would have hidden
it.* **Coverage, measured pre-filter and able to fail: terms 0.651-0.731, candidates 0.764-0.779,
~1,400-1,500 candidates removed.**

## 🛑 2026-08-19 -- **THE CORTICAL READ ROUTE IS UNWINNABLE ON THE CLOZE TASK, MEASURED BEFORE**
## **BUILDING IT. AND THE REASON IS BRAIN-FAITHFUL, NOT A DEFECT.**
`scratch/probe_cortical_route_feasibility.py`, on the read-out cell's OWN call (simplewiki,
`max_patches=1`, `consolidate_every=200`): **1,150 sentences -> 68 consolidated facts, 487
refusals. Only 18 of 300 held-out targets (6.0%) have ANY entry in the consolidated store, which
covers 2.4% of the candidate pool.**
**⛔ SO THE NEXT STEP I HAD WRITTEN DOWN -- "build the cortical read path and score it on the
read-out cell" -- WOULD HAVE PRODUCED A GUARANTEED NEAR-NULL, from having NO ENTRY rather than
from being wrong.** *Caught before the build. Third time this session that asking "could this
experiment have succeeded?" changed the plan; the first two were caught after the compute.*
**🧠 AND THE SPARSITY IS CORRECT BEHAVIOUR, WHICH REFRAMES IT:** the episodic pool holds 2,883
words while the consolidated store holds 68 -- a **42x** gap, with the gate refusing ~88%. That
IS Complementary Learning Systems: the hippocampus holds everything, cortex holds the slowly
distilled residue, and consolidation takes many repetitions. **The cortical store is not
too thin -- the CLOZE TASK IS ASKING IT ABOUT WORDS IT HAS NOT CONSOLIDATED YET.**
**➡️ CONSEQUENCE: WE HAVE TWO INSTRUMENTS AND THEY MEASURE DIFFERENT ORGANS.**
`exp_substrate_end_to_end_readout_v1` = the HIPPOCAMPAL instrument (scores episodic recall) and is
the only one wired. `exp_grounding_precision_gold_v1` = the CORTICAL instrument (scores what was
actually consolidated). **A cortical read route must be scored on the cortical instrument, or on
far more reading -- never on the cloze task.** *Do not re-derive this; the probe is on disk.*

## 🧠🔴 2026-08-19 -- **READING (e) FIRED. THE READ-OUT NEVER CONSULTS GROUNDED FACTS.**
## **AND THE BRAIN-FIDELITY NAME FOR IT: WE BUILT HIPPOCAMPUS-TO-CORTEX TRANSFER AND THEN READ**
## **THE ANSWER OUT OF THE HIPPOCAMPUS.**
`exp_substrate_end_to_end_readout_v1` spec `v3_consolidation`, 18 units, 3 seeds, 1,053 s.
**THE MANIPULATION WAS TOTAL AND VERIFIED BOTH WAYS: control grounded 38 / 68 / 112 provenance
rows, the B3-ablated twin grounded 0 / 0 / 0.** *Reading (g) checked FIRST and in code.*

| contrast | result |
|---|---|
| **consolidation OFF vs control, read-out** | **IDENTICAL in 9 of 12 cells**; the 3 that move are SEMANTIC-at-exact-key by **+0.0033 to +0.0067 = 1-2 items of 300** |
| **EPISODIC route** | **identical to 4 decimals in ALL 6 cells**, both regimes, every seed |
| `definitions` OFF | grounding falls **68->46, 112->64, 38->31** -- it genuinely feeds grounding -- and the read-out moves **EXACTLY 0.0000 in all 12 cells** |
| `gap_detector` OFF | moves nothing, anywhere |
| `foraging` OFF | **now properly rate-matched (1150/1150, 1800/1800, 750/750)** and moves **exactly 0.0000** -- the void arm is fixed and reads a clean null |
| `episodic` OFF | the ONLY organ that moves anything: exact-key **0.9467 -> 0.0000** |

**⛔ AND IT IS NOT AN INFERENCE FROM A NULL -- THE MECHANISM IS A CODE FACT, VERIFIED AT HEAD:**
`recall_sentence` -> `recall()` reads `self._epi_codes`, the episodic DG codes, and **NEVER touches
`state.store`**. `profile()` reads Library `Trace.context_vec`s plus `state.space._sums`, and
ConceptSpace is observed **only at grounding time** -- which is exactly why SEMANTIC moves by 1-2
items and nothing else moves at all. `query()` DOES address the fact store; **the scored arms do
not use `query()`.** *So the consolidated store is WRITTEN AND NEVER READ.*

**🧠 BRAIN-FIDELITY AUDIT (SHAPE / POSITION / METRIC), because the wall is a fidelity divergence:**
- **POSITION -- THE DEFECT.** CLS: hippocampus writes fast and sparse, replay transfers to
  neocortex, and retrieval of CONSOLIDATED knowledge is a **CORTICAL** read. We built the write
  (D3, one of only 5 of 38 organs that compute the brain's actual equation) and the transfer (B3,
  which fires and refuses ~87%), **and then answered every question from the hippocampus.**
  Consolidation sits DOWNSTREAM of retrieval here; in the brain it is upstream. *Position inverted.*
- **METRIC.** The cell scores cloze naming, a LEXICAL-SEMANTIC task, i.e. a cortical one. Scoring
  a cortical task through a hippocampal route is a route/metric mismatch.
- **SHAPE (secondary, named so it is not lost).** Our consolidated store is HD-bound
  `(subject, relation)` triples -- an addressable symbolic database. Cortical semantic memory is a
  distributed overlapping representation. Real divergence, but not what is costing us here.
**🔑 THIS REFRAMES THE STANDING NEGATIVE. "The store memorises and does not transfer" (exact-key
0.9333, held-out 0.0044) IS THE SIGNATURE OF HIPPOCAMPUS-ONLY RETRIEVAL** -- a pure-hippocampal
system recognises what it has seen and generalises nothing. **That is a MISSING ORGAN, not a
representational ceiling.** *And the slot table already named it: `semantic_parser` (Q1,
question -> retrieval cue) and `cortex` (Q3, accept/clarify/refuse) are BOTH NEEDS_ADAPTER. Those
two ARE the cortical read path. The ablation just proved the gap costs everything.*
**✅ CROSS-CHECK, TWO INSTRUMENTS AGREE ONCE THE WIRING IS KNOWN:** the grounding-precision cell
scores the GROUNDED FACTS directly and the substrate DOES beat random there (0.0244 vs 0.0031).
Grounding works; the read-out cannot see it.
**⛔⛔ CONSEQUENCE FOR THE PRIMARY FOCUS, AND THIS IS WHY THE ORDER WAS FLIPPED: A SENSORIMOTOR
CHANNEL FEEDS THE CORTICAL/CONSOLIDATED SIDE, WHICH THIS INSTRUMENT DOES NOT READ. Building B5
first and scoring it end-to-end here would have produced a GUARANTEED NULL, and it would very
likely have been filed as "sensorimotor does not help inside the substrate".** *That is "ask
whether the experiment could have succeeded" paying out a second time -- this time IN ADVANCE.*
**➡️ REVISED NEXT STEP: build the cortical read path (Q1 + Q3 adapters) so the consolidated store
has a reader, OR score B5 on an instrument that reads that store. Do not score B5 here.**
*Floors, recomputed per regime and NOT asserted in advance: `COOC_floor` is strongest in all six
blocks (0.0167-0.0333 held-out); `COOC_COS_floor` is far WEAKER (0.0033-0.0067). My "strongest
floor" wording was an import from another setup and was corrected before it landed.*

## 🔧 2026-08-19 LATER -- PHASE 2 RE-RUN AS A **WIRING DIAGNOSTIC**, NOT A REPORT CARD [LANDED]
**Owner authorised the recommendation in full. `SPEC_VERSION = v3_consolidation`, detached run in
flight.** *The score stays retired: best achievable on this task is 0.0300 vs our 0.0150, so
fixing every defect wins a TIE WITH A FLOOR. What is being recovered is the ABLATION CONTRASTS.*
**⛔ WHY THE OLD TABLE WAS NOT MERELY STALE BUT MEANINGLESS** (`scratch/phase2_cost_probe.py`):
`n_provenance` was **0 on ALL 30 units**, and the `definitions` / `gap_detector` ablations returned
**BIT-IDENTICAL episode counts to the control, 8,394 in every unit**. Those organs feed the
grounding path and the grounding path never ran. **"Changes exactly nothing" was the bug restated.**
**🎯 THE ONE PRE-REGISTERED QUESTION: with consolidation firing, does the read-out change AT ALL?**
(i) NO -> the read-out never consults grounded facts: a WIRING DEFECT that must be known BEFORE
building the sensorimotor channel, because that channel would be invisible to this instrument.
(ii) YES -> the ablation table is interpretable for the first time.
**✅ READING (g) ALREADY PASSES ON THE FIRST LANDED UNIT: control n_provenance 38, refusals 199.**
*The consolidation ablation binds BOTH WAYS by substrate self-test -- on: 30 rows / 91 refusals;
off: 0 / 0. An ablation asserted only by "the ablated arm grounds nothing" would have PASSED on
the broken run, which is exactly why both directions are asserted.*
**⚠️ AND A CORRECTION I MADE TO MY OWN TEXT BEFORE IT LANDED: `COOC_COS_floor` is carried as a
CANDIDATE floor, NOT declared the strongest.** The 0.0300-vs-0.0125 figure came from a DIFFERENT
setup; on this cell's own smoke cosine is WEAKER than counting (0.0 vs 0.0167 held-out). It is a
genuinely different computation, not a no-op -- checked, because the scramble control already
failed that way here.

## ⏹️ AUTOLOOP **DISARMED** BY OWNER 2026-08-19. BOTH EARLIER CELLS LANDED.
**➡️ THE COMPACTION HANDOFF AND THE PRIMARY FOCUS ARE THE FIRST BLOCK OF
`notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT AND READ ONLY THAT BLOCK.**
**PRIMARY FOCUS: wire the sensorimotor norms in as a foundation asset and test whether the
substrate can USE them.**

## 🔬 GROUNDING PRECISION LANDED (3 seeds, n=398-441, NOT underpowered by the cell's own gate)
**Reading (iii) fires: the gate assigns meanings BETTER THAN RANDOM and WORSE THAN CO-OCCURRENCE.**

| arm | precision | hits per seed | paired p vs SUBSTRATE |
|---|---|---|---|
| **TOP_COOCCURRENT** | **0.0573** | 21, 26, 26 | **0.004 / 0.018 / 0.015 -- BEATS us 3 of 3** |
| SUBSTRATE | 0.0244 | 7, 12, 12 | -- |
| RANDOM_ANCHOR | 0.0031 | 1, 1, 2 | 0.069 / 0.005 / 0.011 |
| MOST_FREQUENT_ANCHOR | 0.0023 | 1, 1, 1 | 0.065 / 0.002 / 0.004 |

**So the grounding gate DOES assign meanings above chance (2 of 3 seeds at p<0.05) -- and "the word
it co-occurs with most" beats it in ALL THREE.** *What the substrate learned is co-occurrence.
Third instrument, same standing diagnosis.*
**✅ AND THE DEGENERACY IS LARGELY GONE AT SCALE: anchor diversity 0.544, top-anchor share 3.1%,
against 39 anchors for 96 terms and 17.7% earlier -- the shelf-rotation fix did that.**
**⛔ CONSEQUENCE FOR THE NEXT BUILD: any sensorimotor channel must be pre-registered to beat
`TOP_COOCCURRENT`, not merely random. Beating random is not the bar here and never was.**

## 🟢🟢 2026-08-19 -- THE BEST-CONTROLLED POSITIVE THIS PROGRAMME HAS: **THE SIGNAL TEXT LACKS IS IN
## THE SENSORIMOTOR NORMS. 0.6413 vs CO-OCCURRENCE'S 0.3067, FOUR CONTROLS BINDING.**
**Task: given 50 candidates that ALL co-occur with the target, pick the taxonomically related one.
Gold = provenance-filtered ConceptNet, no WordNet source. Word-disjoint 5-fold CV. 538 target
words.** *(All fitted -- CEILING DIAGNOSTICS, never capabilities.)*

| feature set | hit@1 |
|---|---|
| **PAIRWISE sensorimotor (11 Lancaster dims + cosine + euclid + |conc diff|)** | **0.6413** |
| co-occurrence + POS + sensorimotor | 0.6394 *(adds nothing)* |
| **CO-OCCURRENCE, every form tried** | **0.3067** |
| co-occurrence + POS | 0.2993 |
| **POS only** | **0.1022** |
| **CANDIDATE-ONLY, never sees the query** | **0.0985** |
| **SHUFFLED PAIRING, marginals preserved** | **0.0595** |

**CO-OCCURRENCE TOPS OUT AT ~0.31 HOWEVER PROCESSED** -- raw, Dice, NPMI, full 1,024-dim profile,
linear, nonlinear, supervised on the answers. **Eight scalars with a tree ensemble and the full
profile with a linear model BOTH land on 0.3104.** *The remaining 69% is not in text.*
**AND SENSORIMOTOR ALONE MATCHES SENSORIMOTOR-PLUS-EVERYTHING -- co-occurrence adds nothing on top
of it.**

**🚨 I EXPECTED AN ARTIFACT AND THE ARCHIVE TOLD ME WHICH ONE.** The 2026-08-18 sensorimotor cell
found a **QUERY-INDEPENDENT genericity score reading 0.6195** that beat every pairwise distance. My
first number was **0.6152**. *So their control ran before anything was written: candidate-only
0.0985, shuffled-pairing 0.0595, and dropping the candidate-only features IMPROVED the score.
**The pairing carries it.***

**🔓 IT RE-OPENS A CLOSED ROUTE. The SAME 11 dimensions were filed at 0.6039 against a 0.6791 bar
as "refuting THIS RESOLUTION".** *That was pairwise similarity on the dissociation instrument; on a
better-posed problem the same eleven numbers double the text-only ceiling.* **"DO NOT GENERALISE A
NARROW FAILURE TO IMPOSSIBLE" (owner, 08-11) paid out, on an asset marked closed.**

**⚠️ WHAT IT IS NOT: a mechanism. It says the INFORMATION is there and text does not have it. The
norms are SUPPLIED human ratings -- admissible (static, offline, no LLM at inference) but not
learned. One gold, one corpus, 538 words, no CI. NEXT BUILD, not next claim.**

## 🎯 THE STRONGEST RESULT OF 2026-08-19, AND IT REFRAMES THE TOP ITEM: **IT IS A RANKING PROBLEM**
**hit@k on the paradigmatic gold, 635 scorable words, 852 candidates** (`scratch/hit_at_k_ceiling.py`):

| arm | hit@1 | hit@10 | **hit@50** | hit@100 |
|---|---|---|---|---|
| BAG cosine | 0.148 | 0.417 | 0.639 | 0.735 |
| TYPED cosine | 0.134 | 0.361 | 0.567 | 0.660 |
| **RAW co-occurrence COUNT** | **0.150** | **0.510** | **0.787** | **0.846** |
| RANDOM | 0.003 | 0.030 | 0.167 | 0.277 |

**A RELATED WORD IS IN THE TOP 50 OF A PLAIN COUNT LIST FOR 78.7% OF WORDS (random 16.7%). THE
INFORMATION IS PRESENT. WE CANNOT PUT IT FIRST.** *That agrees with the one result this programme
trusts from the other direction: the fitted oracle moves AUC 0.03-0.07 -> 0.8629 ON THE SAME
COUNTS. Two independent demonstrations that the counts carry it and the READ-OUT does not.*
**⛔ SO "THE MISSING INGREDIENT IS A LEARNING SIGNAL" MUST NOT BE READ AS "THE INFORMATION IS NOT
IN THE COUNTS". The problem is DISCRIMINATION among ~50 co-occurrence-plausible candidates, with a
79% ceiling -- which is a far better-posed problem than the one we have been working on.**

**⛔⛔ TWO CLAIMS THAT WERE HERE ARE RETRACTED BY MY OWN CONTROLLED CELL
(`exp_discrimination_ceiling_v1`, 4 corpora x 150,000 sentences, paired tests):**
- **"DICE buys +31%" -- RETRACTED. 0 of 4 corpora at p<0.05, and NEGATIVE on two.** *The +31% came
  from one 1,024-word table. The smoke had warned the effect was scale-dependent; I pre-registered
  that warning and promoted the number anyway.*
- **"SECOND-ORDER cosine is WORSE than the raw count" -- RETRACTED, IT IS THE OPPOSITE: it beats
  RAW in 4 of 4 corpora.** *I called it "fifth instrument, same conclusion". It was one instrument
  at one scale.*
- **A BUG IN THAT CELL, DISCLOSED: `BAG_COSINE` and `SECOND_ORDER` are the same computation, so
  that table has THREE arms, not four.**
**✅ WHAT SURVIVES IS THE CLAIM THAT MATTERED: retrieval dwarfs discrimination on ALL FOUR corpora
-- hit@50 0.280-0.542 vs hit@1 0.078-0.136, random 0.066-0.074.** **⚠️ AND THE NUMBER MOVES: the
0.787 above is ONE corpus with an 852-word pool; at 2,400 words it is 0.280-0.542. POOL SIZE
BELONGS BESIDE IT.**

## 🧭 WHAT THE 2026-08-19 SESSION CONVERGES ON -- STRATEGIC READ, **HYPOTHESIS-PENDING-VET**
**EVERY REPRESENTATION WE OWN TIES OR LOSES TO CO-OCCURRENCE COUNTING, ON THREE INSTRUMENTS -- and
the reason may not be that we lack a teacher.**
**MEASURED THIS SESSION: 74% of taxonomically-related word pairs CO-OCCUR in the corpus. Only 26%
of words have a taxonomic relative they are never seen beside.** *So co-occurrence is not a weak
baseline a better mechanism ought to beat -- it is most of the signal text makes available.*
**That reframes the standing "the missing ingredient is a LEARNING SIGNAL" diagnosis: the residue a
teacher would have to capture is a small and genuinely hard 26%, and nothing we own -- bag, typed
slots, episodic, semantic, successor representation -- lifts it above ~0.02 on 4-7 hits.**
**⚠️ NOT A RESULT: one gold (ConceptNet), one corpus, 852 words capped by the asset's own
co-occurrence table. VET BEFORE QUOTING.** *Corollary that would change the programme if it
survives: `SET_P` -- synonym pairs with ZERO co-occurrence -- tests the rare 26% BY CONSTRUCTION.*

## 🚨 THE MOST TRANSFERABLE THING FROM 2026-08-19: **SEVEN DEFECTS, ALL MINE, ALL IN THE TOOLING, AND
## EVERY ONE LOOKED LIKE A FINDING ABOUT THE SUBSTRATE.**
1. a refusal arm that passed because the store returned NOTHING for every cue -- **pair every
   refusal arm with a binding arm**; 2. a working organ reported DEAD because my counter could not
   see the spine invoking it -- **count the artifact, not the call**; 3. a scramble control that
   was a NO-OP against a bag representation (shuffled cue tied the real cue, p=1.0000);
   4. a rate-matched twin broken **TWICE, in opposite directions**; 5. **the substrate consolidated
   only when the forager changed books, so every Phase 2 run grounded NOTHING**; 6. **25 of 28
   corpora unreachable because every read restarted alphabetically -- which produced a textbook
   LEARNING-CEILING curve**; 7. **an encoding repair that VERIFIED ITSELF WITH ITS OWN BROKEN
   DETECTOR -- fixed 9 lines, reported "0 remaining", and 56 were damaged.**
**FOUR OF THE SEVEN WOULD HAVE BEEN PUBLISHED AS SUBSTRATE FINDINGS.** *None was caught by reading
the code. Every one was caught by a control on a control, or by asking whether the experiment
COULD have succeeded before asking why it did not.*
**🔑 AND #7 GENERALISES THE WHOLE LIST: VERIFY WITH A POSITIVE CONTROL, NEVER ONLY AN ABSENCE
CHECK.** *"No mojibake found" inherits the detector's bug; "the character 🚨 is present" does not.
An absence test inherits every blindness of the thing that measures it -- which is also why
"nothing was refused", "no organ was invoked" and "no prior work found" were all wrong this week.*
**THAT QUESTION IS THE HIGHEST-YIELD HABIT
THIS SESSION FOUND -- ask it before every negative, without exception.**

## WHAT LANDED 2026-08-19 (Phases 0-3; `2e8134fd2` .. `85b146f69`)
- **PHASE 0 DONE.** `situation_reader` import **205 s -> 30.4 s** (it trained a model AT IMPORT
  TIME); its self-test now PASSES at 102.7 s where it TIMED OUT. Scratch file out of `hdlab/` and
  the registry. **The dashboard now shows `UNVETTED` instead of a blank** -- 0 blank of 14, checked
  at the rendered cell.
- **PHASE 1 DONE. `hdlab/substrate.py` EXISTS** -- the assembled reader, organs built lazily,
  every organ's use PROVEN by a call count or by the artifact it leaves. Self-test PASSES:
  400 sentences, 3,400 episodic writes, **19 facts grounded with provenance, 124 refused**.
  Slots: **9 FILLED / 6 NEEDS_ADAPTER / 8 EMPTY / 3 EXCLUDED**, reported by the object itself.
- **🚨 PHASE 2 IS THE RESULT, AND IT IS A RESOLVED NEGATIVE**
  (`data/exp_substrate_end_to_end_readout_v1/metrics.json`, 3 seeds, n=300, pool 2,114):
  **exact-key hit@1 0.9333, HELD-OUT 0.0044 against a 0.0233 co-occurrence floor whose credible
  bar is 0.0367.** **AND FEEDING IT AN UNRELATED SENTENCE SCORES THE SAME AS THE REAL ONE
  (0.0033, p up to 1.00) -- ON NEW TEXT IT IS NOT READING THE CUE.** *The same twin separates at
  p=0.0005 at exact key, which is what makes this a result and not a broken cell.*
  **THE STORE MEMORISES ALMOST PERFECTLY AND TRANSFERS NOTHING. That is ORGAN A's conclusion
  reached end-to-end through an assembled substrate on a different task and instrument.**
  **âš ï¸ SCOPE CORRECTION THAT MUST TRAVEL WITH IT: that cell ran `max_patches=1`, and the substrate
  only consolidated when the forager CHANGED CORPUS -- so EVERY Phase 2 run grounded NOTHING and
  the consolidation organ never fired. The retrieval result stands (both routes read from episodic
  writes and Library traces, which happen regardless), but re-run before quoting its ablation
  table. The smoke printed `n_provenance: 0` and I read past it.**
- **🔭 AND THE CLOZE TASK IS RETIRED AS A REPORT CARD (Director's call).** Its BEST achievable score
  is 0.0300 -- exact co-occurrence, cosine-ranked -- against our 0.0150, so **the whole prize for
  fixing every defect found is to tie a floor.** *Also measured: the `COUNT_FLOOR` our cells used
  is NOT the strongest available (0.0125 vs 0.0300), which makes the Phase 2 negative WORSE, not
  better. And the single biggest loss in the pipeline is CUE CONSTRUCTION (a full halving) -- do
  NOT cross that with the older "cue side is closed" null, which was a different scorer and
  population.*
- **🎯 REPLACEMENT TASK RUNNING: GROUNDING PRECISION vs an independent gold.** Gold built and
  admissibility CHECKED FIRST: `data/conceptnet_gold_v1`, **422,082 provenance-filtered edges, no
  WordNet-sourced edge present**, meaning relations only. *The convenient pre-extracted ConceptNet
  file carries NO provenance field and is INADMISSIBLE -- the available-tool trap in one file.*
  **FIRST RESULT: the grounding gate is DEGENERATE -- one word was the meaning of 17.7% of terms.
  A varied shelf halves that to 9.5% and anchors become meaning-like (`physics -> biology`), but a
  NEW generic attractor forms (`campus -> available`), so it is part cold-start and part
  structural.** Precision 0.0355 vs floors 0.0142/0.0071 -- **5 hits of 141, UNDERPOWERED, not a
  win.** ✅ **Self-anchoring, the 2026-08-18 defect, is 0.0% -- a genuine repair.**
- **ABLATIONS: `definitions` and `gap_detector` change EXACTLY NOTHING**, both regimes, all seeds.
  `episodic` is the organ doing the memorising (0.9333 -> 0.0000). **The `foraging` arm is VOID --
  rate-matched on the BUDGET instead of on what the live arm consumes; fix by running the live arm
  first and giving the twin its sentence count.** *Second failure of the same control in two days.*
- **PHASE 3: `hdlab/successor_representation.py`, `M = (I - gamma*P)^-1`** -- built, 7 can-fail
  self-tests PASS, **AND MEASURED AS A REAL NEGATIVE.** *I first filed it STARVED (median ONE
  observed successor per word) and named one way to settle it. **The re-test settled it against
  me.*** `exp_sr_scale_ladder_v1`, pool FROZEN, nested corpora: **across a 32x range in
  transitions per state the COOC floor TRIPLES (0.019 -> 0.058) while SR FALLS to a seventh.** At
  the top rung SR is **27 CI half-widths** below the floor -- resolved, not underpowered.
  **MECHANISM MEASURED: at gamma=0.9 the chain mixes past the cue, so at 40,000 sentences SR gives
  just 31 distinct answers to 300 DIFFERENT cues and ONE WORD TAKES 83.7%. A pinned equation
  converged into the constant floor.** *The gamma SWEEP is what made that legible; adopting one
  value would have shown neither half.*
- **AUDIT, GOOD NEWS: the no-op scramble control I built today did NOT propagate.**
  `tools/scramble_control_audit.py`, all **13,553** `.py` enumerated: **HIGH = 0**, 26 cells
  already use the correct content-destroying recipe. *A word-ORDER shuffle against a BAG scorer is
  the same vector -- it tied the real cue at p=1.0000. My own pre-committed reading caught it.*

## FOUR CONTROL DEFECTS I BUILT AND FIXED IN ONE DAY -- THE PATTERN IS THE LESSON
1. a refusal arm that passed because the store returned NOTHING for every cue -- **always pair a
   refusal arm with a binding arm**; 2. a working organ reported DEAD because my counter could not
   see the spine invoking it -- **count the artifact, not the call**; 3. a scramble that could not
   move the number; 4. **a rate-matched twin broken TWICE, in both directions.**
*Every one was caught by a control on a control. None was caught by reading the code.*

---

# â±ï¸ COMPACTION HANDOFF -- 2026-08-18 END OF SESSION. READ THIS BLOCK, THEN STOP AND ACT.
**Everything below this block is the session's working record and is 112 KB. DO NOT read it top to
bottom on recovery. This block is the entry point; the four artifacts it names are authoritative.**

## WHERE WE ARE, IN TWO SENTENCES
**The CLAIMS layer is mostly unverified: 30 vetted, 1 upheld, and 99.5% of the archive's 2,678
HARD_PASS carry neither a CI nor a null, so they cannot be checked from their own files.**
**The ORGAN layer is in genuinely good shape: 163/163 import, 83/87 self-tests pass, 0 constants
among the 13 largest -- and 67 organs are BUILT, SELF-TEST-PASSING, AND UNWIRED.**

## THE FOUR ARTIFACTS -- USE THESE, DO NOT RE-DERIVE THEM
| artifact | answers |
|---|---|
| `tools/experiment_index.py` | what exists in 8,834 cells. **Prints rows scanned BEFORE results**, so silence can never again read as absence. **REPLACES `substrate_query.sh`, WHICH RETURNS ZERO BYTES AND EXITS 0.** |
| `tools/verdict_evidence_gate.py --census` | which claims carry a CI + null (13 of 2,678) |
| `notes/VETTING_LEDGER.md` + `tools/vetting_ledger.py --cite NAME` | may I cite this, and with what narrowing attached? 1 WIRE / 12 WIRE_NARROWED / 4 RERUN_NAMED / 13 SHELVED_REFUTED |
| `notes/ORGAN_ACCOUNTING_2026-08-18.md` | what machinery works, what is unwired, what would be false coverage |

**PLAN = `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`, SECTION 7 (prepended; read it BEFORE sec 6).**

# âž¡ï¸ THE PLAN TO EXECUTE IS `notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT AND START AT PHASE 0.
**It is self-contained, owner-approved, and written for exactly this handoff.** Phase 0 is one hour
(fix `situation_reader`'s import-time training; remove a scratch file from `hdlab/`; make the
dashboard show `UNVETTED` instead of a blank). Phase 1 wires Tier 0+1 (~75 s import). **PHASE 2 IS
THE ONE THAT MATTERS: an end-to-end can-fail test with a real floor and a scramble twin, because
every organ was validated ALONE and wiring ten together is exactly how the 0-for-30 claims layer
happened.** Phase 3 builds the empty slots. The ranked list below is the same plan in summary.

## NEXT STEPS, RANKED -- START AT 1
1. **WIRE THE SIX ORGANS BOTH AUDITS AGREE ON:** `hippocampal_encoder`, `cortex`,
   `information_foraging`, `coref`, `goal_owner_select`, `definitional_extraction`. **Recovering
   built machinery beats building new machinery.** Re-run `situation_reader`'s self-test with a
   >240 s budget first (it needs 204 s just to import) and add it if clean.
   **⛔ A PASSING SELF-TEST IS NOT SUFFICIENT: `atom_consultation` passes AND has `applied`
   hard-coded `False`; `definitional_predicate_v61` passes AND fires on 0.27% of its intended
   population. BOTH SIT INSIDE THE 67. WIRE ONLY THE INTERSECTION of self-test-passing AND
   probe-FUNCTIONAL.**
2. **MINE MIDDLE_BAND, NOT HARD_PASS.** 117 meaning-relevant, never read. **Building the queue from
   HARD_PASS SELECTED FOR OVER-CLAIMING** -- two cells found this session had MIDDLE_BAND as their
   honest tier while an over-claimed sibling took HARD_PASS. **Highest expected yield in the archive.**
3. **Fix `goal_achievement`** -- the one genuine self-test failure (`AssertionError: channel
   'relation:recur' != 'majority'`), and the SAME organ the constant-probe independently flagged.
   Two methods converged; that is the strongest signal in the organ layer.
4. **Remove `_scratch_orig_goal_owner_select`** from `hdlab/` and from the registry. It is a scratch
   file counted as recoverable capability.
5. **Re-rank the remaining claim queue by ITEM-PRIORITY** (below), not by evidence-carrying.
6. **No new verdict without** a CI, a null, a declared STRONGEST floor, and a statement of whether
   the items predate the mechanism.

## THE STRONGEST PREDICTOR, AND IT IS FREE
**DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?** Every vetting survivor was scored on items
built independently of the rule; every pass-5 refutation had detectors authored against the items
they were scored on. **It beat every statistical signal tried. Ask it first.**

## MY FOUR ERRORS THIS SESSION -- ALL ONE FAULT, DO NOT REPEAT IT
1. "No prior work found" x3 -- from a tool that returns zero bytes and exits 0.
2. "25 results landed 08-17" -- my index dated cells by **file mtime**; 60 share one bulk-touch
   minute. True count 3. Now reads `ts_iso`.
3. "1,042 never run" -- a LOCAL-DISK claim. **At least 142 had run; 15 recovered from the remote.**
4. "31 organs self-test" -> ~82 -> **87 measured.** A too-narrow regex, corrected upward twice.
**EVERY ONE WAS AN ABSENCE CLAIM MADE FROM A SEARCH INSTEAD OF AN ENUMERATION.**
*Also: I twice framed the owner's WORKING process as a defect (the remote's intentional idleness,
the deliberate SSH-back of results). **Ask what the operator intended before naming something broken.***

## STANDING CONTEXT
Remote `marsh@home` idle **BY INTENT**; results deliberately SSH'd back to this laptop. Growth
paused. Origin push needs USER AUTH. `data/foundation/` READ-ONLY, one disk, NO BACKUP. Never bundle
a deletion with real work. Never `git add -A`.

---

**ðŸ“ WHY WE KEEP PRODUCING NEGATIVES -- NOW A NUMBER, NOT A COMPLAINT (Director, inline, 08-18).
THE ANSWER TO THE OWNER'S "why aren't we narrowing in on GOOD results?" IS PARTLY THAT OUR
INSTRUMENTS CANNOT SEE A WIN AT THE SAMPLE SIZES WE RUN.**
**A floor is itself an ESTIMATE with its own error bar, so an arm must clear the floor's UPPER
bound to be credible -- not the floor's point value.** That gives a **CREDIBLE BAR**:

| instrument | n/cell | floor quoted | floor's own half-width | **CREDIBLE BAR** |
|---|---|---|---|---|
| WordNet (DSI) | 242 | 0.5431 | 0.0513 | **0.5944** |
| human (v3/v4) | 65 | 0.5943 | 0.0975 | **0.6918** |
| **arc representation (the BINDING one)** | 242 | **0.6317** | 0.0493 | **0.6810** |

**AND THAT SETTLES TONIGHT'S ARM INDEPENDENTLY OF EVERY OTHER OBJECTION: `U1_TYPED_CONTEXT` 0.6669
vs a credible bar of 0.6810 -- IT DOES NOT CLEAR.** *The retraction did not depend on this, but this
would have caught it on its own.*
**METHOD AND ITS LIMIT, STATED: Hanley-McNeil analytic SE, an APPROXIMATION. It is trustworthy HERE
because it reproduces the cells' own bootstrap half-widths -- 0.0513 vs observed 0.0516, 0.0975 vs
0.0987, 0.0493 vs 0.0481. IT DOES NOT REPLACE THE BOOTSTRAP; it is for required-n and order of
magnitude.**
**WHAT IT WOULD TAKE.** Per-cell n to tighten a floor's half-width: **±0.05 -> ~250-290; ±0.03 ->
~770; ±0.02 -> ~1,550-1,780; ±0.01 -> ~6,300-7,200.** *The human instrument runs at **65**. Getting
its bar to ±0.03 needs roughly **12x** the pairs, and its matching funnel is what caps it -- which is
why "buy n by loosening the matcher" keeps being proposed and must keep being refused: **a bigger
sample of an unlicensed instrument is worse than no sample.***
**âŒ MY STRATEGIC READ WAS "we have been running experiments that could not have returned a credible
positive, then treating the absence as evidence about the substrate." I TESTED IT IMMEDIATELY AND ON
THE HUMAN SIDE IT IS FALSE. RETRACTED, SAME SESSION, BEFORE IT COULD BE QUOTED.**
Classified all 24 human-side arms by whether their CI **upper** bound could even reach the credible
bar 0.6918: **24 of 24 CANNOT. ZERO are undetectable. EVERY ONE IS A REAL NEGATIVE.** The best arm
`F1_NO_FILTER` tops out at **0.6508** and the runner-up `T1_TYPED_ROLE` at **0.6057** -- both short
of 0.6918 *even in the most favourable corner of their own error bars.*
**SO BOTH THINGS ARE TRUE AND THE SECOND DOMINATES: the human instrument IS underpowered (it demands
>=0.69), AND our arms are so far below that the power problem does not rescue a single one.** *I
reached for an instrument-level excuse for a substrate-level result; the excuse does not survive
contact with the arm table.*
**WHERE THE POWER ISSUE GENUINELY BITES IS NARROW: arms sitting NEAR a floor -- which tonight means
exactly ONE, `U1_TYPED_CONTEXT` at 0.6669 against a 0.6810 credible bar.** *Discipline 18 is still
right and still binding; its SCOPE is "arms near the bar", NOT "our negative record generally".*
**AND THE OWNER'S QUESTION KEEPS ITS HONEST ANSWER: the negatives are mostly REAL. The instrument is
not what is holding us back -- what we are BUILDING is.**

**🚨 OVERNIGHT 08-18, AND THIS BLOCK IS MIRRORED TO YOUR BOARD SO READ IT FIRST: I HEADLINED A WIN AND
THEN TOOK IT APART. NO ARM CURRENTLY CLEARS A TRUSTWORTHY BAR.**
- **A TYPED-ROLE ARM READ 0.6669 AND I CALLED IT THE FIRST EVER TO CLEAR THE BAR. RETRACTED.** Its bar
  was computed on a DIFFERENT REPRESENTATION; rebuilt correctly, **a control containing NO WORDS AT
  ALL reads 0.6317** against that 0.6669.
- **BOTH BARS THIS PROGRAMME GATES ON INCLUDE CHANCE AT THEIR OWN n: 0.5431 CI [0.4922, 0.5953] and
  0.5943 CI [0.4937, 0.6911].** *I spent two days correcting people that "the bar is 0.5431, NOT 0.5";
  at these sample sizes THE TWO CANNOT BE TOLD APART.*
- **AN AUDIT (`37181d944`) FOUND 21 ARMS ACROSS 3 CELLS GATED THE SAME WRONG WAY -- ALL SUSPENDED, NOT
  REFUTED.** *A wrong floor makes a verdict unsupported; it does not prove the opposite.* **NOT
  programme-wide: the main write-rule ladder does it correctly.** No false positive was manufactured.
- **A VERIFIED CODE DEFECT: the prediction-error rule was applied to the BAG channel, not the typed
  one, so "prediction error doesn't help" IS RETRACTED AND THAT QUESTION IS FULLY OPEN AGAIN.**
- **THE ONE FINDING I TRUST, REACHED INDEPENDENTLY BY TWO LANES ON TWO POPULATIONS: THE TYPED CHANNEL
  WAS NEVER GIVEN ENOUGH DATA TO BE TESTED.** ~8.6 slotted observations per word spread over 10,121
  dimensions; the dense 58-dimension arm on the SAME data does not collapse. **A density sweep is
  running against branches pre-committed at `0504bfd00`.**
- **🧠 THE REFRAME WORTH KEEPING (biology, PINNED): the brain's "what is this LIKE" system (ATL) and
  its "what goes WITH this in an event" system (pMTG/TPJ) doubly dissociate. OUR INSTRUMENT IS THAT
  DISSOCIATION. WE BUILT THE SECOND ORGAN AND GRADED IT ON THE FIRST ORGAN'S EXAM.** *Grammatical
  frames CONSTRAIN a meaning hypothesis; they do not SUPPLY it -- stage one of two.*
- **UNCHANGED BELOW AND STILL TRUE:** Organ A closed, the corpus exonerated, the missing ingredient is
  a learning signal. **Tonight did not touch that; it was about what came after.**

**ORGAN A (THE WRITE RULE) IS CLOSED. ALL FIVE STEPS GATED. THE ANSWER IS A LEARNING SIGNAL, AND THE
CORPUS IS EXONERATED (`0f8a3254a`).** The substitutability signal **IS PRESENT** in first-order counts
from our own corpus: a supervised diagonal reweighting of a PPMI+SVD space reaches AUC **0.9670**
fitted / **0.9606** held-out and -- after the leakage objection was TESTED rather than waved away
(37.6% of pair-member words appear in >1 pair) -- **0.8629 under GROUP-DISJOINT, word-clean CV**
(`56175e456`, `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`). **AND NOTHING UNSUPERVISED
REACHES IT:** our five steps 0.03-0.42; vanilla PPMI **0.0519**; TUNED counts **0.1144** (shift
selected on a WORD-DISJOINT held-out set, the Levy/Goldberg/Dagan steelman, `120cfefae`); second-order
cosine 0.0510; **from-scratch SGNS 0.4417 -- BELOW its own UNTRAINED random-init control at exactly
0.5000.** *Training a neural predictor on this corpus moves it TOWARD co-occurrence.* **So: the corpus
is NOT the blocker, first-order counts CONTAIN the signal, no unsupervised transform extracts it, and
the missing ingredient is WHAT TO SUPERVISE WITH.**

**THE TRAP THAT GOVERNS EVERYTHING NEXT, and it must be stated before any build: the instrument
defines its positive set by WORDNET SYNONYMY and its known-answer arm IS WordNet (0.9599). ANY
supervision derived from WordNet TRAINS ON THE TEST. The 0.8629 fitted oracle is a CEILING
DIAGNOSTIC, NEVER a candidate build.** Drill in flight: `admissible_supervision_sources_drill`.

**METHOD RESULT WORTH AS MUCH AS THE SCIENCE: FOUR arms produced apparent CI-separated wins that their
own controls destroyed** -- max-pool, prediction-error gating (**+0.2369, a 4.3x "improvement"**, killed
by a RATE-MATCHED random gate reading 0.3007 vs 0.3079), the `C2` denominator, and the learned basis.
**Without rate-matched and identity-matched twins this session would have reported four breakthroughs
and built on all of them.** *Any arm that changes HOW MUCH gets written now REQUIRES a rate-matched
random twin.*

**ELIMINATED, each with its own control:** the basis (learned = random), the denominator (row-norm is
a cosine no-op, PROVEN by an identical wrongpool control), not-collapsing (max-pool **-0.0210 BELOW**
the sum at 55x storage; its random-occurrence control sat AT CHANCE, proving the loss is
content-specific), the filter (**a same-size RANDOM draw reads 0.5041 vs the incumbent's 0.4173 --
our stopword selection is WORSE than random**), superposition (**DOES NOT EXIST** -- each word
reconstructs from its own counts to **1.76e-08** across all 617 words), prediction-error gating, and
corpus capacity.

**SUPERSEDED BELOW BUT KEPT FOR ITS REASONING:** **DRILL 1'S CENTRAL PREDICTION IS REFUTED. `CODE` IS
EXONERATED -- TWICE (`ac629b1e7`,
`exp_writerule_learned_basis_denominator_gate_v1`).** The drill argued our store is `H^T p_a`, a random
rotation of `Sigma_yx`, and that the missing operation is factorisation `Sigma_yx Sigma_xx^-1` living
in the `CODE` slot -- so a LEARNED basis should create substitutability where a random projection
cannot. **IT DOES NOT.** `C1_LEARNED_BASIS` +0.0073 [-0.0005,+0.0150] **NOT_SEPARATED**, and
`C1_CTRL_MATCHED_RANK_RANDOM` **MATCHES IT** (-0.0060). Composition moves for NO arm, while
`C1_CTRL_FREQUENCY_SHUFFLED` moves it **+0.0858 [+0.0486,+0.1229] ABOVE (worse)** -- which PROVES the
composition instrument can see change, so the flat readings are real nulls. **"Cortex expands where we
compress" also fails:** accuracy fell MONOTONICALLY across the k sweep, 0.0553 (k=64) -> 0.0393
(k=2048). And `C2`'s one CI-separated accuracy gain is **NOT a denominator effect** -- its winning
`pool='row'` divides each row by a scalar and **cosine is provably invariant to that** (the identical
`WRONGPOOL` control is the PROOF, not a control failure); the genuine denominators (`col`,
`both`=PPMI) scored BELOW A0. **AN ELEGANT DERIVATION IS A HYPOTHESIS. This one made a specific
prediction and its own controls killed it.**

**WHAT IS ESTABLISHED INSTEAD, on TWO independent instruments.** (1) `ACCUMULATE` is the measured
INTERFERENCE source (`b6cad69ca`): the CORRECT score is STATIONARY with depth (POP_128 +0.0013
[-0.0006,+0.0034]) while the competing FIELD's mean AND p95 rise CI-separated; mean pairwise anchor
cosine 0.0127 -> 0.272; **common-mode removal does NOT help (DO-NOT-REDO 27 stays closed)** and the
interference is DIFFUSE, not top-200 words. (2) **THE DISSOCIATION INSTRUMENT IS LICENSED**
(`0eb44eb1d`) -- **the first instrument this programme owns whose FOUR FLOORS SIT AT CHANCE and are
VERIFIED there** (0.5000 / 0.4901 / 0.4664 / 0.5431, every CI including 0.5; known-answer 0.9599 vs a
0.95 gate; random store 0.4862). On it, above 0.5 = substitutability, below = co-occurrence:
`RAW_COUNT_SINGLE_OCC` **0.4173** > `PARADIGMATIC_PROFILE_WRITE` **0.2165** > `INCUMBENT` **0.0710** >
`RAW_COUNT_FULL_ACCUM` **0.0510** > `PRESENCE_ABSENCE_BINARIZED` **0.0294**; the ranking is RESOLVABLE
(max_lo 0.3835 > min_hi 0.0470). **STOP-IF (iii) fired: the incumbent is CI-separated BELOW 0.5.**

**THE ANSWER IS THE LEARNING SIGNAL, AND IT IS MEASURED (`exp_corpus_capacity_ppmi_svd_ceiling_v1`,
plan sec 6.18).** Instrument licensed by EXACT reproduction -- all 8 regression checks at **delta
0.0000**; population loaded BYTE-IDENTICAL from the instrument's own checkpoint; matrix 5,491 x 21,576,
density 0.91%, 1.82M tokens, **coverage PERFECT 242/242 in both cells**.
- **PPMI+SVD FAILS ON OUR CORPUS AT EVERY RANK -- but QUALIFIED 2026-08-18 (`96caca8de`): we ran the
  VANILLA construction (no context-distribution smoothing, no shift, no subsampling). Levy & Goldberg
  proved SGNS implicitly factorises SHIFTED PMI, and a TUNED count method MATCHES SGNS. So the honest
  claim is "UNTUNED PPMI+SVD fails", and A TUNED-COUNT ARM IS NOW MANDATORY AND MUST BE REPORTED
  BEFORE ANY SUPERVISED ARM -- if it clears 0.5 unsupervised, the supervision conclusion below is
  WRONG and the missing thing was hyperparameters.** Numbers as run: k=50/100/300/500 -> **0.0519 / 0.0285 / 0.0230 / 0.0278**, all BELOW 0.5,
  and its BEST is WORSE than our incumbent 0.0710. No k dropped for cost. **We are NOT being beaten by
  truncated SVD.**
- **A SUPERVISED LOW-RANK REWEIGHTING OF THE SAME COUNTS READS 0.8629 UNDER THE STRICTEST TEST.**
  CORRECTED, and the agent caught it before reporting clean: the landed pair-level held-out figure is
  0.9606, but **37.6% of the 617 pair-member words appear in >1 pair**, so pair-level CV leaks word
  identity across folds. Group-disjoint GroupKFold (union-find -> 148 word-disjoint components,
  `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`) gives **0.8629**. **QUOTE 0.8629, NOT 0.9606**
  -- the finding SURVIVES, clearing 0.5 by a wide margin on pairs never jointly seen in fitting.
- **SAME counts, SAME 242 pairs, SAME scorer. SUPERVISION IS THE ONLY VARIABLE, AND IT MOVES AUC FROM
  0.03-0.07 TO 0.96.** So the missing thing is **NOT information, NOT representation capacity, NOT the
  write steps** -- **IT IS THE LEARNING SIGNAL.** Every arm we have ever built is unsupervised and
  chooses what to write with no error signal about which directions matter. **Routes to the project's
  own named flavour MISSING-LEARNING -> REUSE/EXPAND the learner, never a parallel build.**
- **NEVER QUOTE 0.9606 AS A CAPABILITY.** The oracle is FITTED ON THE EVALUATION CONSTRUCT. It proves
  the counts CONTAIN the signal; it does NOT show an unsupervised or brain-plausible learner finds it.
  The live question is what supervision a BRAIN has that we do not -- not a labelled synonym list, but
  prediction error, cross-modal correspondence, consequences of use. **DRILL, NOT BUILD.**

**ORGAN A IS NOW FULLY GATED -- ALL FIVE STEPS (`f311d0ac2`, `34d3fdbab`, plan sec 6.15).** FILTER:
**REAL BUT NEGATIVE-VALUE** -- a same-size RANDOM token draw reads **0.5041, CI-separated ABOVE** the
incumbent's 0.4173. CODE: exonerated x2. ACCUMULATE: interference source. NORMALISE: not in the live
path. SUPERPOSE: **DOES NOT EXIST** -- rebuilding each word from its OWN counts alone reproduces the
incumbent to **1.76e-08 across all 617 words**; proven by reconstruction, not argued.

**RETRACTED 2026-08-18: "the operative defect is COLLAPSING OCCURRENCES INTO ONE VECTOR."** Tested
directly and **FALSE**: `M1_MAXPOOL` (every occurrence kept, scored by best match) reads **0.0299,
-0.0210 [-0.0393,-0.0020] CI-separated BELOW** the sum, at **55x the storage**. Its control decides the
reading: `N1_MAXPOOL_RANDOM_OCC` sits **AT CHANCE (0.4545)**, NOT depressed -- so the depression needs
the word's OWN occurrence content and is not an artifact of the max operator. Not-collapsing is not
the fix.

**THE ORGAN-LEVEL FINDING, AND IT IS THE REAL RESULT: NOT ONE ARM THIS PROGRAMME HAS EVER MEASURED IS
CI-SEPARATED ABOVE 0.5 ON THE LICENSED INSTRUMENT.** Everything tops out AT chance and never above it
(`N2_SHUFFLED` 0.5296 NOT_SEP, `N1_RANDOM_FILTER` 0.5041 NOT_SEP, `S1_SINGLE_OCC` 0.4173), and
everything carrying MORE accumulated corpus content sits FURTHER BELOW (incumbent 0.0710, full accum
0.0510, max-pool 0.0299, binarised 0.0294). **Interventions that DESTROY information move us TOWARD
chance; interventions that ADD accumulated content move us AWAY from substitutability.** So the
ceiling is not a step we have yet to fix -- **first-order co-occurrence counts from this corpus appear
to carry a co-occurrence signal and NO substitutability signal for these five steps to expose.** The
best any configuration achieves is encoding NOTHING.
**CAVEAT, do not collapse these into one claim:** across `ACCUMULATE` the winner no-relation rate
FALLS 0.8400 -> 0.7971 (-0.043 CI-separated) -- **adjacency was present from sentence one; a bag of
neighbours IS an adjacency record.** Summing does not CREATE adjacency; it raises INTERFERENCE and
degrades retrieval. **REPORT WINNER SHARE, GOLD SHARE AND RATIO TOGETHER, ALWAYS** (the Director once
quoted 66.0->94.4 while dropping the gold's 23.9->60.3 and the ratio, which FELL 3.967->3.822).
**LIMIT: the dissociation instrument is n=242 matched pairs, ALL NOUNS** -- verb/adj/adv strata did not
survive its frequency caliper.
**RETRACTED (VET COMPLETE, off `exp_writerule_step_ladder_v1` `COMPOSITION_DELTA_TABLE`): "summing is
what converts our store from could-replace to appears-near."** FALSE, and backwards: across
`ACCUMULATE` the no-close-relation rate FALLS 0.8400 -> 0.7971, **-0.043 [-0.0800,-0.0086]
CI-SEPARATED**. Adjacency was there from sentence one -- a bag of neighbours IS an adjacency record.
The Director quoted the winner's co-occur share (66.0->94.4) and dropped the gold's (23.9->60.3) and
the RATIO, which FELL 3.967->3.822. **REPORT WINNER SHARE, GOLD SHARE AND RATIO TOGETHER, ALWAYS.**

ONE ORGAN AT A TIME, AND THE ORGAN IS THE WRITE RULE (owner ruling 2026-08-18, `PLAN_ORGAN_STEP_LADDERS`
sec 6.7). The cue side is finished and did not fix the reading; four cells changed the QUESTION we hand
the store and every one improved FINDING THE DRAWER while none improved READING WHAT IS IN IT
(binarising takes addressing 0.0711 -> 0.1094 while hit@1 moves 0.0223 -> 0.0249, +0.0026
[-0.0026,+0.0078] NOT_SEPARATED -- ADDRESSING AND READ-OUT ARE SEPARATELY CAPPED).
**THE DECISIVE WRITE-RULE MEASUREMENT, and it is why this organ is the one:** varying ONLY the target's
own stored row, `SUM_ALL` reads **0.0100**, ONE occurrence picked at RANDOM reads **0.0367**, and
`BEST_SINGLE_ORACLE` reads **0.3033** against the **0.1390** floor we have never cleared. *Summing is
worse than not summing, and individual sentences already carry enough to clear the floor.* The oracle
is a CEILING DIAGNOSTIC, never a capability. **DEPTH IS RETRACTED (sec 6.6): "+0.0503 still climbing"
was an ORACLE-CUE number; on the REAL partial cue POP_72 32->72 is BELOW and POP_128 is NOT_SEPARATED,
with winner composition FLAT at every depth.** Eleven cells across six organs on 08-17 returned ~+0.01
each; the two LADDERS redirected the programme. Method is not in question -- organ selection was.

## TOP ITEM -- FIND AN ADMISSIBLE SUPERVISION SIGNAL THAT IS NOT THE EVALUATION GOLD
**🆕 2026-08-19: THE FIRST CANDIDATE IS BUILT AND UNDER TEST -- D7 SUCCESSOR REPRESENTATION**
(`hdlab/successor_representation.py`). **It clears the circularity constraint outright: it is
self-supervised from the corpus's own transitions and derives from NO gold, NO WordNet, NO LLM.**
Full run in flight; **the pre-registered risk is that it is a better COUNTER rather than a
different kind of thing**, since `M` is a discounted multi-step co-occurrence statistic and the
floor is the 1-step one. *Phase 2 independently re-confirmed that the missing ingredient is a
learning signal, end-to-end through the assembly -- see the 2026-08-19 block at the top of POSITION.*

Organ A is closed and its answer is that we need a LEARNING SIGNAL. **The whole question is now WHICH
ONE, and the binding constraint is CIRCULARITY, not performance.**
**VERIFIED OFF DISK 2026-08-18, not asserted** (`exp_dissociation_score_instrument_v1.py`):
`SET_P` is built by `build_wordnet_synonym_candidates()` (line 304) from `wn.synsets()` (line 312);
the known-answer arm is WordNet path similarity (0.9599); and `SET_S` **explicitly EXCLUDES any
WordNet pair even at high co-occurrence** (evidence key
`set_S_excludes_wordnet_pair_even_at_high_cooccurrence`, line 674). **So WordNet does not merely
influence the labels -- it DEFINES both sides of them.** Therefore **any signal derived from WordNet --
synonyms, hypernyms, glosses, or anything computed from them -- trains on the test and is UNUSABLE AS
SUPERVISION however well it scores.** Second constraint, the
owner's invariant: **NO LLM in the operational path**, and a pretrained table is disqualified as a
MEANING SOURCE (ceiling reference only) -- **but a STATIC OFFLINE-BUILT ASSET IS ADMISSIBLE** (owner
Q3: *"we can build that foundation however we want, as long as it is a strong foundation, and the
operation is not llm"*). Do not hold us to a stricter standard than the brain meets.
**IN FLIGHT:** `admissible_supervision_sources_drill` -- biology first (what supervises cortical
semantics, and what the prediction-error NULL does and does NOT rule out: it tested error against the
word's OWN accumulator, which is not error against ANOTHER MODALITY or a DOWNSTREAM CONSEQUENCE);
then an **on-disk enumeration by `os.walk`, never registry-first** (a 1.21M-edge CSKG read by nobody
live -- **check whether it CONTAINS WordNet before trusting it**; OpenStax 117,642 sentences;
Brysbaert concreteness; Warriner VAD; Binder; UD parses); then a ranking on brain fidelity /
independence-from-gold / coverage on the 617 matched-pair words / no-LLM survival; then ONE build
with a mandatory rate-matched control.

## SUPERSEDED TOP ITEM -- THE WRITE RULE WAS THE FIRST THING TO MOVE READ-OUT (LESSONS: WRITE RULE)
`exp_readout_writerule_paradigmatic_v1` (full, `a8fdc968f` / `24ca42661`) rebuilt the STORE so a
word's code sums its neighbours' own context PROFILES instead of their arbitrary identity tags, and
left the comparator untouched. `W1_PARADIGMATIC` **0.0298** vs `W0_SYNTAGMATIC` **0.0223**: **+0.0075
[+0.0023,+0.0128]**, half-width 0.00525, analytic null half-width 0.00458, **ABOVE** (~34% relative).
A frequency-matched profile control reads 0.0225 and does NOT beat W0 (+0.0002 NOT_SEPARATED); a
random-profile null reads 0.0188 and does not either (-0.0035 NOT_SEPARATED -- lower, not separated);
three hybrid alphas all land +0.0065..+0.0070 ABOVE; K1 addressing 1.0000 on all seven arms;
orthographic leakage flat at W0's own value. **NO STOP-IF FIRED CLEANLY** and the cell wrote the
honest fourth reading itself: *the write rule was PART of the defect but is not sufficient* -- W1 is
still **-0.0575 [-0.0673,-0.0478] BELOW** its own binding floor (orthographic 0.08731), 2.9x short.
**THE CONTRAST IS THE FINDING: the read-out scoreboard's ~39 prior arms ALL changed the COMPARATOR
and none beat the incumbent CI-separated; this one changed the WRITE RULE and did.** `wire_status` is
`VET_PENDING` -- WIRE-or-SHELVE not decided.

## CUE SIDE -- CLOSED IN FOUR CELLS (LESSONS: CUE SIDE CLOSED; DO-NOT-REDO 44, 45, 46)
(1) PLAN ITEM 3 landed a CLEAN NULL (`2e5a467ae`): `A0_FLAT` reproduces item 1's 0.0849 target
exactly (regression gate PASS), `T1` key-sparsified 0.0704 = **-0.0145 [-0.0203,-0.0088] BELOW**,
`T2` cue-sparsified 0.0886 is the grid's raw MAXIMUM yet **+0.0037 [-0.0013,+0.0088] NOT_SEPARATED**,
T2 vs T1 +0.0182 ABOVE, oracle 1.0000 and random 0.0000 both passing. **Stop-if (i) fired. The cell's
own verdict: "Neither, cleanly" -- no arm beat the flat store and the sparsified arms LOST accuracy
rather than matching it more cheaply.** `C1` vs `T1` is bit-identical 0.0 [0,0] BUT CARRIES A
CONSTRUCTION CAVEAT: K=32 exceeds the cue's own median nnz of 12.0, so that truncation is a no-op for
most items and the tie is partly an artifact. (2) COMPRESSION DIAGNOSED (`201776cc9`): what matters
is PRESENCE, not counts -- the losing property is MAGNITUDE, not sparsity and not non-negativity.
`B1_BINARIZED_RAW` (presence only, uncompressed) +0.0383 [+0.0293,+0.0476]
above the incumbent and +0.0248 [+0.0160,+0.0338] above raw counts; S1 -0.0100 BELOW, N1 -0.0003
NOT_SEPARATED. Loss is CONCENTRATED: the 93 lost items have shorter cues (10.80 vs 12.48) and much
sparser store profiles (106.4 vs 210.8), both CI-separated. (3) IT DOES NOT TRANSFER (`1e085d761`) --
see POSITION; R2 (binarised THEN projected) gives back two thirds of the addressing gain, so **the
two defects are not independent**. (4) THE BASIN THEORY IS REFUTED -- see CLEANUP.

## PHASE DIAGRAM -- THERE ISN'T ONE (LESSONS: PHASE DIAGRAM)
`substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md` (`32cc8ce71`), enumerated
from the filesystem: 7,804 `metrics.json` (re-walked 7,807, delta = this session's own files, nothing
missing); ~59 vary dimensionality, ~21 sparsity, 2 expansion; **23 of 42 parameter-by-operation
squares NEVER MEASURED**, 13 usable, six diagrams on six scorers that may NOT be merged. The "55-65%
coverage" recollection traces to `director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`, whose own line
items say ~10% and <5%. Q13's sparsity sweep has NO cell under `data/` -- it is in gitignored
`scratch/sparsify_right_object/`; promote before the next clear. **Its d-sweep row is corrected by
C36.**

## BRIDGING -- TWO MEASURED NULLS (LESSONS: DO-NOT-REDO 38, 43)
Phase 2 FULL: B1 rho 0.0270 n=394 vs floors 0.0412/0.0317/0.0905, NOT_SEPARATED, perm p 0.30, both
known-answer arms ABOVE (K1 0.3301, K2_ORACLE 0.2893); bridged codes KEEP IDENTITY (96.12% distinct)
and LOSE MEANING (retention 0.0819); the curated CSKG arm fails too. SELECTIONAL-CONSTRAINT
BRIDGING, the owner's own mechanism, is the SECOND and worse null: -0.1049 [-0.2041,-0.0057] BELOW
the incumbent, -0.0015 NOT_SEPARATED from a random target, instrument alive (K1 0.3311). KILL
STATUS: withdrawn for thematic, re-worded for selectional, per HANDOFF 8b(B) -- whose numbers remain
NOT re-verified by any pass.

## STORAGE -- THE WRITE/READ ASYMMETRY IS REAL AND DID NOT SURVIVE AS A WIN (LESSONS: WRITE/READ ASYMMETRY)
`exp_sparse_address_dense_value_v1` (n=3994, own floors): best partial-cue addressing anywhere is
0.0719 at a DENSE address; a 1%-occupancy address (82 of 8192 units) read with a DENSE cue matches
it at 0.0699, CIs overlapping; read SYMMETRICALLY it is 0.0483, 1.45x worse; the dense read wins 18
of 24 matched pairs, max 6.27x. **RE-TESTED 08-17 on the UNCOMPRESSED base, where it is a DIRECTION
AND NOT A WIN: T2 (cue sparsified) beats T1 (key sparsified) +0.0182 CI-separated, but T2 does not
beat the flat store (+0.0037 NOT_SEPARATED).** C36: the d-sweep line "0.0711 -> 0.0716 at 8192" mixes
read regimes; matched at `a_read=1.0` it is 0.0711 / 0.0714 / **0.0709** -- 32x the memory buys less
than nothing, so the conclusion strengthens.

## CLEANUP / SURPRISE / TARGET SPACE (LESSONS: CLEANUP MEMORY, SURPRISE, TARGET SPACE)
**AND THE BASIN EXPLANATION FOR THE CLEANUP NULLS IS REFUTED (`exp_cleanup_basin_conditional_v1`,
landed 08-16 22:41, UNREAD BY ANYONE FOR ~14 HOURS).** Six tau strata summing to 3994, known-answer
arm 1.0000 in every one: lift is CI-separated ABOVE **only in the LOWEST-tau stratum** (+0.0036
[+0.0009,+0.0072]) and NOT_SEPARATED in every higher one **including the highest** (+0.0154
[-0.0039,+0.0347]) -- the OPPOSITE of what basin theory predicts and of what the cell pre-registered
as confirming. It licensed skipping an elaborate settle mechanism, and the one cheap settle arm run
anyway is null (-0.0010 [-0.0025,+0.0003]). **AN UNREAD RUN IS A RUN THAT DID NOT HAPPEN -- second
instance in two days.**
CLEANUP MEMORY IS REAL, NOT INERT (fixed points 1.0000, idempotent, capacity on VSA's own d/log d
scale): first measured lift, +0.0033 and +0.0078 CI-separated in 2 of 3 pools, every arm still
-0.1135 BELOW the binding constant floor -- which makes the FIVE BANKED CLEANUP NULLS STRONGER, the
load-bearing half was NOT missing. SURPRISE-WEIGHTING: clean null, named cause -- signal DEGENERATE
(median 0.875 where 1.0 is orthogonal), selection beats a token-matched random subset in 4 of 18
comparisons, residual rule a near-no-op (cos 0.9771 to uniform) = the PRE-REGISTERED bootstrapping
problem. TARGET SPACE: affect +0.1013 is a CEILING DIAGNOSTIC, no floors, no null, clears nothing;
its verb half is now MEASURED, not suspended (C33).

## TOOLING STATE (LESSONS: VERDICT BAR, SKIPPED FULLS, C31, C32)
Corrected base rate: 7,789 enumerated, MEETS_BAR **1** (`exp_cue_to_store_translation_v1`), FAILS
7,770, NO_EVIDENCE 18; 238 flagged cells ARE cited by an index -- OPEN OPERATOR DECISION, NOT TAKEN.
The one pass is rejected on four grounds (pool admits a fitted constant 0.7354 vs chance 0.0625;
exact-key is not the operating point; the cell declines a verdict; margin overstated 4.20x).
`verdict_bar_check.py` HAS FALSE-PASSED FOUR TIMES -- run it, NEVER rely on its verdict, state
arm-by-arm margins; it also returns NO_EVIDENCE on any cell whose arms are nested per-stratum
(ITEM 2's). Only 12 of 7,789 cells ever recorded a constant floor, so every historical bar decision
used a THREE-floor max. `matched_candidate_sets` WAS VOID and is rebuilt; `eligB` still suspect.
FOUNDATION v4 ~49% (`d62acfe58`); TRIAGE -> `RECOVERY_PROGRAM.md`.

## DO NOT REDO -- NEVER-TRIM -- stubs; detail in LESSONS
All CLOSED. `*` = revival criterion. 1 intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic
bootstrapping*; 4 F2 freq-corrected pool*; 5 same-sentence cosine/PMI; 6 FHRR superposition; 7 PBV;
8 read-out vs v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 norms as FILTER*; 12 sense
selection v2; 13 minimum-grounded-basis; 14 `genuine_cross_source_corroboration_v1`*; 15 combined
dictionary v1; 16 "context vector is noise"; 17 co-occurrence as the explanation; 18 role-bound
structure alone -- STRUCTURE_HURTS*; 19 frontmatter `isolation:`/`background:`; 20 the voting
mechanism*; 21 hand-scored delta at 1-3%; 22 the 2-hop bridges; 23 extraction as DIRECT-BANK*;
24 distinctiveness as log-IDF*; 25 differentia/genus + supply; 26 `sign()` vs forgetting kernel;
27 rank-1 common-mode removal*; 28 FORAGE_REFUSAL; 29 five-stage read-out chain; 30 near-duplicate
anchors; 31 supply as an ADDITIVE CHANNEL -- NARROWED*; 32 DG/pattern-separation for grounding;
33 crowding as a gate criterion; 34 the GRADED SWITCH*; 35 +0.0602 as a C3 number; 36 `k_eff~=50` as
a MEASURED limit*; 37 "right neighbourhood, wrong member"*; 38 bridging WITH the THEMATIC hub --
MEASURED NULL*; 39 sparsifying the READING anchor -- dies on the real task*; 40 quoting +0.2285 as
the bridging margin; 41 quoting a "0.073 lift gap"; 42 `grounded_similarity()` AS A SCORER --
76.18% of SimLex on two values, NO revival; 43 SELECTIONAL-CONSTRAINT bridging -- CI-separated
BELOW the neighbour-copy incumbent and NOT_SEPARATED from a random target*; **44 SPARSIFYING THE
STORED KEY under a partial cue -- -0.0145 [-0.0203,-0.0088] BELOW the flat store with oracle 1.0000*;
45 THE BASIN EXPLANATION for the cleanup nulls -- lift separates ONLY in the LOWEST-tau stratum,
opposite to prediction; do NOT build a settle mechanism*; 46 CUE-SIDE ENGINEERING AS A READ-OUT FIX
-- the biggest addressing gain we have (+0.0383) transfers to hit@1 at +0.0026 NOT_SEPARATED*.**
CAVEATS: D1 near-vs-far; D2 encoder-swap; D3/D4 foraging reversals; D5 sharpening SMOKE-only;
CT1 consistent!=good; CT2 run_mode is an ingestion constant.
CORRECTIONS: C1 availability-binds-first; C2 CLIP-at-INGEST; C3 the 94% has NO floor;
C4 DGProj=interference; C5 an encoder EXISTS; C6 wrong checkpoint; C7 opp-map #5/#6; C8 comparator
was a LOOKUP TABLE; C9 results ARE searchable; C10 tautology=eligibility bug; C11 "58% common mode";
C12 doc date; C13 the FULL DID report; C14 whiten+pinv IS tested; C15 chain self-contradiction;
C16+C22 `A5_STRINGCTRL` not zero-meaning; C17 scramble is DONOR-RULE dependent; C18 conjunctive lean
QUALIFIED; C19 k_eff correction-of-a-correction; C20 "0.90 precision" UNSOURCED; C21 "0.95"=parse
coverage; C23 121.1M-token encoder/237.7M corpus; C24 norms stale BOTH ways; C25 shortlist-hit out
of scope; C26 FHRR 0.956 bare threshold; C27 VET residue; C28 +0.2285 was a NEIGHBOUR-CHOICE
diagnostic; C29 the "0.073 lift loss" is 0.0034, populations mixed; C30 "retrieval fine / we tie
spelling" is EXACT-KEY + OPTIMISTIC-TIE ONLY; C31 the checker's false pass was THREE defects;
C32 "0 of 7,769 meet the bar" -> 1 of 7,789, and that survivor is itself rejected; **C33 "our
instrument cannot resolve verbs even when handed the answer" -- SUSPENDED at n=86, now MEASURED at
n=222: rho 0.2607 [0.1282,0.3841], strongest floor (scramble p95) 0.1152 against a 0.1107 null-width
orientation, margin +0.1452 [-0.0496,+0.3379] NOT_SEPARATED, permutation p 0.001. The null genuinely
tightened, so this is a real negative and not the n=86 artifact. A verb-channel build is licensed
CITING THIS AND NEVER THE RETIRED n=86 NUMBER;** C34 "the constant floor is the binding one" FALSE
in general -- it is -0.1959 on the bridging stratum and -0.2253 on the selectional one, the WEAKEST
member of the four; **C35 "the binding-operator choice is EMPIRICALLY NULL across two cells and six
operators" (HANDOFF 8b(D)) is PART-WRONG THREE WAYS -- a 3-BIN instrument is not a null (and FHRR
reads 0.8000 vs Hadamard 0.2889 inside the very bin that produced "invariant"); the 500/500/500 half
names the wrong cell and is SUPERSEDED, not absent; and two of the six operators COLLAPSE (0.0720
and 0.0000 against ~0.81). The operator has never been varied on any job this programme runs on.**
**C36 "d 256->8192 moves partial-cue addressing 0.0711->0.0716" MIXES READ REGIMES -- 0.0716 is the
`a_read=0.2` cell at D=8192; matched at `a_read=1.0` the sweep is 0.0711/0.0714/0.0709, so the
conclusion (dimensionality does nothing for addressing) STRENGTHENS. The correction already filed
against it is ALSO wrong: 0.0716 does NOT trace to a D=2048 draw, it is a genuine D=8192 reading
(`BEST_ASYMMETRIC_REGIME_SWITCH_CONFIG`). Both notes fixed in place. Second correction-of-a-
correction in one day.**

## STANDING DISCIPLINES -- NEVER-TRIM -- LESSONS
1 NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% -- cost TWO experiments, the
2nd claiming to have FIXED the 1st; gate on KNOWN-ANSWER RECALL. 2 SERIALIZE MEASUREMENT vs CODE
CHANGE (2x). 3 A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night; C31 = 5th).
4 ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM (6x); AN ABSENCE CLAIM REQUIRES
AN ENUMERATION, NOT A SEARCH -- state HOW. 5 BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS
THE OPERATION IT SCORES. 6 RUN A POSITIVE / KNOWN-ANSWER ARM (2x): a FLOOR says whether the EFFECT
is real, a KNOWN-ANSWER arm whether the INSTRUMENT is -- run both. 7 NO DEMOTION WITHOUT A FRESH
ON-DISK RE-CHECK -- ~11 wrongly demoted, 17 corrections-of-a-correction in 48h; keep
EXISTS/IS-REACHED/IS-GOOD separate. **C35 is the 18th: a correction said a claim "does not
reproduce" when the cell it reproduces in was never opened.** 8 A GATE IS A CI-SEPARATED MARGIN
ABOVE max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE, CONSTANT) on the IDENTICAL scorer/n/pool/gold -- never
a bare number, baseline STANDALONE, every floor recomputed on the item's OWN population **AND ITS OWN
REPRESENTATION (widened 08-18 -- see 16; "population" alone did NOT catch the 0.5431 import).**
9 DETECTORS FIRE ON HONESTY (49/49 flagged were false positives). 10 SILENT JOINS FABRICATE GREEN
AND RED -- ASSERT+COUNT joined rows. 11 A NUMBER MAY NOT BE CARRIED BETWEEN SCORERS OR POPULATIONS
-- cost 3x in one night (C28/C29/C30); name the scorer, n, pool and gold for BOTH sides or you have
no comparison. 12 A CLAIM MEASURED AT THE EXACT-KEY OPERATING POINT DOES NOT TRANSFER TO THE
PARTIAL-CUE REGIME, WHICH IS THE REAL ONE -- top-50 0.5566 exact vs 0.3758 partial; state the cue
regime beside every retrieval number. 13 REPORT TIE CONVENTIONS BOTH WAYS, NEVER SILENTLY PICK THE
FLATTERING ONE -- +0.0105 NOT_SEP flips to +0.0641 ABOVE on tie mass alone. 14 REPORT THE CI
HALF-WIDTH AND THE NULL p95 AT THAT n BESIDE EVERY MARGIN -- A WIDTH IS NOT AN EFFECT. Cost 3x in
one night (C32/C33/C34), each an UNDERPOWERED NULL read as a CAPABILITY STATEMENT; at n=86 the
"floor" WAS the null distribution's own spread. **15 A GRID'S RESOLUTION IS PART OF ITS VERDICT: an
equality reported on a 3-value grid is a BIN, not a measurement (C35). State the swept values and
the number of queries per point beside every "no difference".**
**18 GATE ON THE FLOOR'S UPPER BOUND, NOT ITS POINT VALUE -- AND IF NO ACHIEVABLE SCORE COULD CLEAR
IT, THE POINT IS UNTESTABLE, NOT NEGATIVE.** A floor is an ESTIMATE and carries its own error bar, so
**CREDIBLE BAR = floor + its own 95% half-width.** Measured 08-18: WordNet 0.5431 -> **0.5944**;
human 0.5943 -> **0.6918**; the binding arc floor 0.6317 -> **0.6810**. *`U1_TYPED_CONTEXT` 0.6669
clears the floor and FAILS the credible bar -- this alone would have caught the night's retraction.*
**AND THE SECOND HALF IS THE ONE THAT CHANGES BEHAVIOUR: WHEN A FLOOR'S HALF-WIDTH IS SO WIDE THAT NO
ACHIEVABLE AUC COULD CLEAR ITS CREDIBLE BAR, THAT CONFIGURATION IS UNTESTABLE AND MUST NOT BE FILED
AS A FAILURE OF THE THING BEING TESTED.** *This is discipline 14 one level up: **a width in the FLOOR
is not a GATE.** Required per-cell n to tighten a floor: +-0.05 ~250-290, +-0.03 ~770, +-0.02
~1,550-1,780, +-0.01 ~6,300-7,200 -- **the human instrument runs at 65.*** **BEFORE BUILDING AN ARM,
DECIDE WHAT n ITS INSTRUMENT NEEDS; IF THAT n IS UNREACHABLE, THE ARM IS NOT YET WORTH BUILDING.**
*Never buy n by loosening the matcher -- a bigger sample of an unlicensed instrument is worse than no
sample.*
**17 EVERY NEGATIVE GETS A BRAIN-FIDELITY DRILL, EVERY TIME -- OWNER INSTRUCTION 2026-08-18
(COMMENTARY): *"All negative results you should drill (safely -- we shouldn't be giving away any of
our substrate specifics here) for brain fidelity and what we should do to get closer to that -- every
time."*** A negative is not filed until it has been asked: **WHICH BRAIN STRUCTURE performs this
operation, are we REPLICATING it or SUBSTITUTING something convenient, and WHAT WOULD CLOSE THE
GAP?** *This is not new doctrine -- it is the standing rule made non-optional and applied at the
moment of the negative rather than in a later drill that may never happen.* **🔒 SAFETY CLAUSE, OWNER
EXPLICIT: NEVER PUT OUR SUBSTRATE SPECIFICS INTO AN EXTERNAL QUERY.** Research drills ask about the
BIOLOGY in general terms -- *"how does cortex represent grammatical role"* -- **never about our
architecture, our organs, our operators, our dimensionalities or our results.** *Web search is a
one-way door; a query naming our design is disclosure that cannot be recalled.*
**AND THE FIRST QUESTION OF ANY SUCH DRILL IS WHETHER THE NEGATIVE IS EVEN REAL: on 2026-08-18, FOUR
of the night's "negatives" were MEASUREMENT DEFECTS, not results** -- a bar computed on the wrong
representation, an error rule applied to the wrong channel, an instrument with 10.9% coverage of the
arm it was testing, and a corruption control that was near rank-preserving and so **incapable of
failing.** *Drilling a defect for brain fidelity would have produced a confident, wrong story about
the brain. **ESTABLISH THAT THE EXPERIMENT COULD HAVE SUCCEEDED BEFORE ASKING WHY THE BRAIN
SUCCEEDS WHERE WE DID NOT.***
**16 A FLOOR IS SPECIFIC TO THE REPRESENTATION IT WAS COMPUTED ON, NOT ONLY TO THE POPULATION --
AND THIS RULE EXISTS BECAUSE RULE 8 AS WRITTEN COULD NOT CATCH THE VIOLATION.** 0.5431 was computed
on the BAG-of-words representation and quoted as "THE bar" across `STATUS.md` and the plan for two
days -- **including in the banner that corrected everyone for saying 0.5** -- then applied to arms
built on grammatical ARCS. Rebuilt on the arc representation, a **no-words attestation floor read
0.6317 [0.5820, 0.6781]** against a 0.6669 headline: **the gate was meaningless and the coverage
control could not catch it (`COVERAGE_MIN=3` dropped 0 of 242 pairs).** *Same population, same
scorer, same gold -- so rules 8 and 11 both PASSED while the comparison was already void.* **STATE
THE REPRESENTATION BESIDE EVERY FLOOR, AND REBUILD THE FLOOR WHENEVER THE REPRESENTATION CHANGES,
EVEN IF NOTHING ELSE DID.** *Corollary, earned the same night: a control with a threshold that
excludes nothing is not a control -- report how many items each control actually removed.*

## WHAT IS RUNNING / BLOCKED

- **🟢 AUTOLOOP IS ARMED (owner, 2026-08-19: "enable your stop hook and make sure it's working
  properly"), 26 continuations in.** Stop it with `python tools/autoloop.py disarm`. Anything
  other than exactly boolean `true` in `data/hook_state/autoloop.json` reads DISARMED -- the
  fail-safe direction is OFF. *Both `stop_hook.py --self-test` and `autoloop.py self-test` PASS.*
  **⚠️ THIS BULLET SAID "DISARMED" FOR ~20 CONTINUATIONS AFTER THE LOOP WAS RE-ARMED.** This
  section is MACHINE-PARSED by `tools/session_start_hook.py`, so a resuming session was being told
  the loop was off and the wrong cell was running. **A stale `WHAT IS RUNNING` is worse than an
  empty one -- it is confidently wrong. Update it in the same turn as the launch, not later.**
- **🔵 IN FLIGHT (2 detached, they CONTEND so both are slow -- that is expected, not a stall):**
  - **9-seed spoke independence sweep** -- `scratch/spoke9.log` / `.err`, PID `scratch/spoke9.pid`.
    Decides whether the spoke's independence from counting is real or a small-count artefact.
    **3 of 9 seeds in and reproducing the earlier run EXACTLY (0.70 / 0.94 / 0.89).**
  - **`exp_predictive_write_gate_v1`** spec `v1_residual_gate`, 3 seeds -- `scratch/pwg_full.log`
    / `.err`, PID `scratch/pwg_full.pid`. The pinned residual rule against pure accumulation,
    **with a rate-matched RANDOM_SKIP arm and the threshold SWEPT, both in from the first draft.**
  **DO NOT RESPAWN EITHER.** *Neither writes an artifact until a whole unit lands, so mid-unit the
  only progress signal is the CHILD process's CPU -- never the shim PID's, which reads 0 s on a
  healthy run.*
- **✅ LANDED AND SUPERSEDED: `exp_cortical_read_consolidated_v1`.** v1 was VOID (cue-construction
  defect), v2 fixed the cue, **v3 (`v3_floors_at_k`) is the final word: retrieves, NOT competitive,
  0 of 18 floor cells.** *Its first full run also died on corpus arithmetic -- `simplewiki` yields
  exactly 20,000 sentences and it read all of them, leaving an EMPTY held-out split. That is now a
  CLAUDE.md rule, because the smoke used 2,000+360 and could not have caught it.*
- **✅ LANDED 2026-08-19 12:25Z: `exp_substrate_end_to_end_readout_v1` spec `v3_consolidation`,
  18 units in 1,053 s, 30 older-spec units excluded from the report. NOTHING IS RUNNING.**
  Result and its brain-fidelity audit are the first block of ## POSITION. Read it with
  `scratch/read_v3_result.py`, which reads the pre-committed readings in their own order.
- **[SUPERSEDED -- IT LANDED] IN FLIGHT: `exp_substrate_end_to_end_readout_v1` FULL, spec `v3_consolidation`.** 18 units
  (3 seeds x 6 ablations: control / episodic / definitions / gap_detector / **consolidation** /
  foraging). Detached; shim PID in `scratch/readout_v3_full.pid`, logs
  `scratch/readout_v3_full.log` / `.err`. Read progress with `scratch/peek_v3_units.py`.
  **DO NOT RESPAWN IT** -- a duplicate is the more expensive error.
  **⚠️ THE SHIM PID IS NOT THE WORKER: `.venv/Scripts/python.exe` spawns the real interpreter as a
  CHILD and then idles, so the recorded PID reads 0 s CPU on a perfectly healthy run.** Judge
  progress by `units.jsonl`, or by the child via
  `Get-CimInstance Win32_Process -Filter "ParentProcessId=<pid>"`.
  *Unit keys carry `SPEC_VERSION`, and v3 additionally FILTERS `load_units` at assembly time --
  the bump protects the compute, the filter protects the report. Without it the 30 dead-grounding
  v2 units would have been folded into the new metrics and fired the gate on a run that worked.*
- **â“ Q66 OPEN AND WORKED AROUND, NOT BLOCKING: `hdlab/ca3_completer.py` IS UNTRACKED IN GIT.**
  23 KB, on the Tier 1 wire list, **zero git history to recover from**; any checkout/reset/clean
  destroys it. My recommendation is on the board: commit it alone, in a commit that states the
  authorship is not mine. *I have not done it -- committing another session's in-progress work
  under my name is the thing I declined to do for Q52.*
  **✅ CLOSED 2026-08-19, `f102e7081`. COMMITTED ALONE, 444 lines, nothing bundled.** Verified
  before committing: imports cleanly, carries 5 named self-tests. **Flagged as an owner decision
  twice and passed back twice; the third time it was made, because the commit is protective and
  reversible and the alternative was leaving a 23 KB organ one `git checkout` from deletion.**
  *Slot D2 remains NEEDS_ADAPTER -- it consumes FHRR bundles plus per-spoke codebooks and the
  ingest path produces neither. The commit protects the FILE; it does not WIRE the organ.*
- **📋 BOARD TRIAGE -- 12 OPEN, BUT ONLY 5 NEED YOU. SEVEN ARE ONE FAULT AUTO-FILED SEVEN TIMES.**
  **Q47, Q48, Q53, Q54, Q55, Q57, Q58 are all the SAME `rm`-bundling denial** -- the loop files a
  board question per denial, so a recurring fault floods the board. **I verified two of them touched
  no result** (the deleted paths were a smoke directory and a log truncated by `>` anyway) and the
  rest are the same shape. **Q49 asks the one policy question they all reduce to; answering Q49
  disposes of all seven.** *Read them as one item, not seven.*
  **THE FIVE THAT ARE REAL, in the order I would take them:**
  1. **Q52 -- 844 uncommitted insertions across 10 experiment files that are NOT mine**, last
     modified 2026-08-17, existing only in the working tree. **Any reset/checkout/worktree op
     destroys them.** I did not touch them: committing a concurrent session's in-progress state
     under my name would be wrong either way. *Highest consequence on the list.*
  2. **Q51 + Q56 (one issue, evidence added) -- 3,894 watchdog files, 31% of `notes/`, still
     arriving every 10 min from the DEAD four-session fleet.** **Now MEASURED, not hypothesised: a
     plain `find` over `notes/` TIMED OUT at 300 s tonight**, and the same cost hit the supervision
     drill and two agents. Cheapest performance fix in the repo. *Disable the task first, then
     clear; otherwise it refills at 6/hour.*
  3. **Q50 -- `CLAUDE.md` tells every session to open by running a tool that returns ZERO BYTES and
     exits 0.** I flagged it in this file but did NOT edit the conventions file unprompted.
  4. **Q49 -- keep halting the loop on the `rm` fault, or log-and-continue?** *My recommendation is
     KEEP HALTING and fix the cause; it is the only thing that reliably catches dropped
     preconditions, and it caught them tonight.*
  5. **Q16 / Q17 (older) -- build a word-onset channel? is that blocked file path deliberate?**
  **Nothing on this list blocks the science.** All four research lanes ran to completion or are
  still running.
- **âš ï¸ THE BAR IS `max(four floors)` = 0.5431 ON THE LICENSED INSTRUMENT, **NOT 0.5**. CHANCE is 0.5;
  the BAR is 0.5431 (the constant/prototype floor). Sections of this file below still say "above 0.5
  = substitutability" -- **that describes CHANCE, not the GATE.** No conclusion flips (every arm sat
  0.03-0.44, far below both), but **any future arm must clear 0.5431**, and the Director spent a night
  describing 0.5 as the target. Corrected in `PLAN_ORGAN_STEP_LADDERS` 6.29.
- **✅ THE HUMAN INSTRUMENT IS LICENSED (`f792c3ab8`, v3, THIRD attempt). n=7 -> 65 per cell.**
  Frequency-STRATIFIED matching -- bin each POS stratum's frequency into 3 quantile bins, then run
  the UNCHANGED matcher inside each (POS, bin) cell. **All four floors CI-include 0.5;
  `max(four floors)=0.5943`** (higher than the WordNet instrument's 0.5431). Known-answer is the
  **published human rating**, NOT WordNet -- its AUC 1.0 is **tautological plumbing, not a result**.
  **All seven arms scored AT OR BELOW CHANCE on human judgements** (INCUMBENT 0.2265, SINGLE_OCC
  0.4644, PARADIGMATIC 0.2788) -- the same qualitative picture WordNet gave.
  **THE DECIDING NUMBER IS INCONCLUSIVE, on the PRE-COMMITTED branch: rho = 0.7857 between the two
  instruments' arm orderings, permutation p = 0.048, BUT bootstrap-of-arms 95% CI = [-0.0439, 1.0],
  WHICH INCLUDES ZERO. The 6.24 WordNet caveat REMAINS OPEN.** *rho 0.79 is NOT agreement; the wide
  CI is NOT disagreement.*
  **THE POWER LIMIT MOVED TO THE ARM COUNT.** The bootstrap resamples **ARMS, not pairs** -- 7 items
  cannot give a tight CI however good each AUC is. **Fix = MORE ARMS, not more pairs.** *In flight:
  `arm-expansion`, harvesting the 20+ store variants already built tonight and scoring them on both
  instruments.*
  **CAVEAT THAT TRAVELS WITH EVERY v3 NUMBER:** post-match balance is materially WORSE than its
  sibling's (`mean_log_freq` -0.4382 vs -0.0416; `mean_length` 0.3988 vs -0.0121). **Floors pass,
  which is the gate -- but this instrument is LOOSER.** And absolute AUCs are **NOT comparable across
  the two instruments; only the ORDERING is.**
- **SUPERSEDED: HUMAN INSTRUMENT v1/v2, BOTH `POWER_INSUFFICIENT` AT n=7 (`6976f08ca`).**
  v2 used the FULL 5,491-anchor set and got the SAME n=7 as v1 -- **which disproves the Director's
  own diagnosis.** *I claimed v1 collapsed because I restricted it to the WordNet instrument's 617
  words; v1's checkpoint diagnostics show that restriction NEVER EXISTED. Plan 6.30 is RETRACTED by
  6.33(B).* **The real cause: a structural frequency gap between the human-labelled sets (pre-match
  SMD on `mean_log_freq` = -1.8396) colliding with the WordNet-tuned caliper (0.02), which drops
  429 of 436 candidates. Adjective and noun strata yield ZERO matches; the 7 survivors are VERBS.**
  **So the blocker is the MATCHER, not the population** -- and loosening the caliper stays forbidden
  because it would unlicense the instrument. **The 6.24 WordNet caveat REMAINS OPEN.**
- **0.8629 IS VERIFIED AND NOW HAS AN ARTIFACT (`dfc84429a`).** Spot-checking found the night's most
  load-bearing number lived ONLY in prose -- zero hits in the capacity cell's `metrics.json`. Its
  script was committed, so reproducible not fabricated. **Re-ran: group-disjoint 5-fold CV AUC
  0.8629, pair-level 0.9587, both exact.** Log at `notes/groupdisjoint_verification_log_2026-08-18.txt`.
- **🚨🚨🚨 THIS DOCUMENT HAS BEEN DESCRIBING A TINY, ACCIDENTAL SLICE OF THE PROJECT. THE OWNER SAID
  SO AND THE INDEX PROVES IT. TREAT EVERY "WE HAVE NEVER" AND "NOTHING REACHES" CLAIM BELOW AS
  UNVERIFIED UNTIL RE-CHECKED AGAINST `tools/experiment_index.py`.**
  Measured 2026-08-18 off the newly built index (8,834 cells, 7,570 with verdicts):
  **2,678 HARD_PASS** (June 323 / July 2,193 / August 162), 1,369 HARD_FAIL, 1,068 MIDDLE_BAND.
  Excluding substrate-physics cells (capacity, scaling laws, binding, Hopfield), **236 HARD_PASS are
  MEANING-RELEVANT** -- June 14 / July 182 / August 40.
  **🔴 RETRACTED WITHIN THE HOUR BY THE VET (`a2e65896`): "25 HARD_PASS LANDED 2026-08-17" IS FALSE.
  THE TRUE COUNT IS 3, AND THE ERROR WAS MY OWN TOOL.** `experiment_index.py` dated cells by the
  metrics.json **FILE MTIME**. **Exactly 60 metrics.json share the minute 2026-08-17 17:44 and 3,850
  share 2026-07-03 14:28 -- BULK TOUCHES, NOT RUNS.** Their internal `ts_iso` says the six I vetted
  actually ran **2026-07-17 to 07-23**, and ZERO ran on 08-17. *A file's mtime is when it was last
  WRITTEN, not when the science happened; any copy, checkout or sync rewrites it.* **FIXED: the index
  now reads `ts_iso` first and records `date_source` per row.** *I told the owner we had ignored 25
  results the day after they landed. We had not. The July work was resurfaced by a touch.*
  **âš ï¸ AND THE FIX IS ONLY PARTIAL, SO DO NOT TRUST RANKING BY DATE YET: of 7,794 landed rows only
  **2,538 carry a `ts_iso`**; **5,256 STILL FALL BACK TO MTIME**. Two-thirds of the archive has no
  trustworthy run-date at all.**
  **[SUPERSEDED CLAIM, KEPT VISIBLE] "25 HARD_PASS landed 2026-08-17 and this document mentions none
  of them."** Among the cells named:
  `exp_read_grow_openvocab_fastmap_v1` (**learn NEW words WHILE reading instead of abstaining**),
  `exp_read_grow_oov_verb_extension_v1`, `exp_read_grow_foundation_realprose_glassbox_ie_v1`
  (*"THE SUBSTANTIVE READING STEP"*), `exp_online_knowledge_condenser_selectional_v1`
  (**condenses generalizable knowledge as it reads**), `exp_role_filler_factorization_compgen_v1`
  (brain-faithful structure-content factorization), `exp_three_factor_eligibility_distal_credit_v1`
  (**a three-factor eligibility trace solving DISTAL CREDIT ASSIGNMENT**),
  `exp_reward_contingency_credit_assignment_v1`, and
  `exp_relational_vs_similarity_conflict_viability_probe_v1` (**GREEN_LIGHT_PENDING_VET -- the
  taxonomic-vs-thematic conflict**).
  **THE MOST EMBARRASSING SPECIFIC: I SPENT 2026-08-18 CONCLUDING "THE MISSING INGREDIENT IS A
  LEARNING SIGNAL" AND "WE HAVE NEVER BUILT THE TAXONOMIC ORGAN". A THREE-FACTOR LEARNING RULE AND
  A RELATIONAL-VS-SIMILARITY PROBE BOTH HARD_PASSED THE PREVIOUS DAY, AND
  `hdlab/random_indexing.py` -- AN EARNED DISTRIBUTIONAL ORGAN -- HAS EXISTED SINCE 2026-08-06.**
  **âš ï¸ THE DEFLATION, AND IT IS NOT OPTIONAL: A HARD_PASS IN THIS PROJECT IS A CLAIM, NOT A
  CAPABILITY.** Five apparently clean wins died to their own controls in ONE session on 08-18, one
  of these 25 is explicitly `PENDING_VET`, and this file already records 21 arms suspended for a
  mis-imported bar. **THE CORRECT STATEMENT IS: A LARGE BODY OF CLAIMED POSITIVE RESULTS EXISTS THAT
  OUR POSITION DOCUMENT IGNORES, AND IT NEEDS VETTING -- NOT THAT WE HAVE 2,678 WINS.**
- **🟢🟢 VETTING PASS 5 (`ae41755a`) -- *** THE FIRST UPHELD RESULT IN 30 VETTED CELLS. ***
  1 UPHELD, 2 QUALIFIED, 1 SUSPENDED, 2 REFUTED.**
  **✅ UPHELD -- `exp_agreement_depth_productivity_generalization_v1`. IT GENERALISES, AND THE SPLIT
  IS ASSERTED IN CODE.** A learned function-word accumulator **supervised ONLY on depth<=1**, tested
  on **2,597 HELD-OUT depth>1 Linzen items: 0.7324 [0.7154, 0.7494]** against the strongest floor
  ACTUALLY RUN (majority 0.5741, upper bound 0.5931) -- **margin +0.1223 READ FROM THE CI LOWER
  BOUND.** Still holds out-of-distribution at **depth 4+: 0.6810 [0.6462, 0.7111]** vs majority
  upper 0.5751. Real seed spread (not one measurement printed n times); scramble drops 0.2947 and
  changes 86.5% of decisions; five filters removed 350 / 289 / 518 / 9,887 / 7,122 items, so the
  controls BIND. No LLM on the path.
  **âš ï¸ ITS HONEST CEILING, STATED BY THE AUDITOR AND NOT TO BE DROPPED: IT *TIES* THE HAND-WRITTEN
  RECURSIVE RULE (0.7312). IT DOES NOT BEAT IT.** *So: a learned mechanism reaches parity with the
  symbolic rule it was meant to replace, generalising to depths it never saw. That is a real result
  and a bounded one.*
  - **QUALIFIED -- `exp_graded_divisive_comparator_v1`:** real +0.0602 [0.0440, 0.0762] with a
    scramble twin at 0.5065, **but the CI lower bound does NOT clear its own pre-registered
    `d >= 0.05`, and the "divisive normalisation" half of the title contributes +0.00175.**
  - **QUALIFIED -- `exp_read_xsent_coref_scene_protagonist_v1`:** the gain is real (0.2462 -> 0.4003,
    McNemar CI lower +0.1039) **but the mechanism is a 5-sentence window, not "scenes" -- the cell
    says so itself.**
  - **SUSPENDED -- `exp_multi_turn_loop_realtext_nphead_gate_v1`:** "true zero confident-wrong" is
    **0 wrong of 18 kept** (rule-of-three upper bound 0.167) against a declared band of 0.01, and its
    one new variable fired on **two items that are the same passage, same answer, same gold** -- n=1.
  - **REFUTED -- `exp_social_relational_grounding_axis_v1`: THE SUBSTRATE CANNOT CHANGE ANY
    PREDICTION.** `valence` takes exactly **three distinct values across all 12 items**, and
    `acc_real` equals the WordNet `dictionary_lookup` accuracy **EXACTLY** (10/12). It is a 3-entry
    lookup table wearing a substrate.
  - **REFUTED -- `exp_desiderative_negation_channel_v1`: 8 OF 8 RECOVERIES LIE INSIDE THE 10-ITEM SET
    THE TAXONOMY WAS DESIGNED FROM, AND 0 OF 27 NON-DESIGN ITEMS RECOVERED.** The channel is
    **bit-identical ON vs OFF on both full benches** (n=80: 0.6992/0.6992; n=160: 0.6623/0.6623).
- **🚨 A BUG IN MY OWN GATE, CAUGHT BY THE AUDITOR, AND I HAD ALREADY QUOTED ITS NUMBER TO THE OWNER.**
  `CI_PAT` contained a bare `confidence`, which matched `lookup_confidence` and
  `high_confidence_idxs` -- model confidences, not intervals -- so two cells computing NO interval
  entered the "best evidenced" shortlist. **CORRECTED FIGURES: 28 carry a CI (not 52), 13 carry BOTH
  a CI and a null (NOT 26), and EVIDENCE_INSUFFICIENT is 2,665 = 99.5% (not 99.0%).** *The direction
  was right and the shortlist was half the size I said.*
- **🎯 THE BEST PREDICTOR IS NOT EVIDENCE-CARRYING, AND THIS IS THE MOST USEFUL THING FIVE PASSES
  PRODUCED: WHAT SEPARATES THE SURVIVORS FROM THE FAILURES IS *** WHETHER THE TEST ITEMS EXISTED
  BEFORE THE MECHANISM DID. ***** The three that survived this batch were scored on items built
  independently of the rule; the three that failed had detectors authored against the very items
  they were scored on -- one docstring even names the specific token pair its rule was written for.
  **CARRYING A CI IS NECESSARY AND WEAK; ITEM-PRIORITY IS THE STRONG TEST, AND IT SHOULD BE THE
  FIRST QUESTION ASKED OF EVERY REMAINING CLAIM.**
- **🔬🔬🔬 VETTING PASS 4 (`a6e60cfa`): 3 REFUTED, 1 SUSPENDED, 2 QUALIFIED, 0 UPHELD.
  RUNNING TOTAL OVER 24 CELLS: 11 REFUTED, 4 SUSPENDED, 9 QUALIFIED, *** ZERO UPHELD ***.**
  - **🚨 THE CAUSAL-LINK RESULT IS PROVEN CONTENT-FREE, NOT MERELY SUSPECT. The auditor RE-RAN the
    organ WITH THE GOLD LINKS REPLACED BY ARBITRARY RANDOM PAIRS AND GOT `organ_integration =
    0.9722` -- BIT-IDENTICAL TO THE HEADLINE.** The cell writes `add_causal_link(cause, effect)` for
    every gold item and queries the same indices back; no text is read (its own label is
    "GOLD-ISOLATION"). **It measures FHRR write/read fidelity at bundle-load 2 and nothing else.**
    **⛔ AND THE BASELINE WAS TUNED UNTIL IT FAILED.** The cell's own comment records sweeping
    distractor density from 200/20 to 15/10 to find *"the smallest min_dist that keeps mr_control >=
    the 0.50 can-fail floor WHILE DRIVING mr_integration TO 0.0000"*. **That is a gate adjusted
    until it passed. All three siblings die together: `pilot_v1`, `fuller_v2`, `fuller_v3_cleaned`.**
  - **REFUTED -- `exp_unified_self_learning_loop_v3`: ITS OWN SCRAMBLE CONTROL BEAT IT.** MAIN LOW
    gain **0.0243** vs SCRAMBLED **0.0288** -- scrambled text learns MORE. Every separation gate is
    `HP_CONTROL_SEP = 0.0` and `CONTRAST_EPS = 0.0`: **a margin of literally zero.** Its own
    label-shuffle null on the same slice wobbles **0.0258** cycle-to-cycle, larger than the entire
    claimed gain. Two arms are one measurement (`NO_READ` and `READ_NO_SLEEP` share the store digest
    `c23b44bc…`). **AND `..._loop_v4`, LANDED FIVE HOURS LATER THE SAME DAY, RECORDS
    `teaches_new=False` AND CARRIES v3's OWN NUMBER AS A CONTROL THAT FAILS. v3 WAS ALREADY DEAD AND
    WAS STILL SITTING ON THE QUEUE AS HARD_PASS.**
  - **QUALIFIED -- `exp_pivot_selectional_knowledge_richness_2afc_v1`: THE TABLE IS THE ANSWER KEY.**
    Its 117 rated pairs and its 59 items x 2 fillers = 117 evaluation pairs are a **PERFECT
    BIJECTION** (eval-not-rated 0, rated-not-in-eval 0): an LLM rated EXACTLY THE TEST. *Offline
    LLM-built foundations are admissible under the owner's ruling, but a table whose vocabulary IS
    the eval is an ORACLE, not a foundation.*
    **✅ THE PART THAT SURVIVES AND MATTERS: the dumb twins DO NOT reproduce it** -- verb-noun
    `Counter` 0.5508, noun frequency 0.5339, length 0.4915. **So the knowledge is REAL and ABSENT
    FROM OUR CORPUS. Honest claim: a cheating oracle reaches 0.78-0.85 on these 59 items and THE
    SUBSTRATE DID NONE OF IT.** *Convention was never declared: tie->0.5 gives 0.8136, tie->loss
    0.7797, tie->win 0.8475.*
  - **SUSPENDED -- `exp_outcome_valence_goal_congruence_v1`: THE DUMBEST RULE SITS EXACTLY ON THE
    BAR.** "Predict MET iff the goal's infinitival verb lemma equals the outcome verb's lemma" --
    no referent, no NP head, no registry -- scores **7/8 = 0.875, precisely the pre-registered
    HARD-PASS floor.** Mechanism 8/8 beats it by ONE item; CIs overlap; P(8/8 | p=0.875) = 0.34.
    *Its v2 reaches 1.0 at N=22 and self-tiered MIDDLE_BAND -- the honest tier v1 should have had.*
  - **QUALIFIED -- `exp_learned_argstruct_parser_lccp_independent_gold_v1`: THE WRONG COMPONENT IS
    CREDITED.** Arm B (cue-competition, **no LCCP**) already clears EVERY gate; adding the LCCP
    prior moves F1 0.3934 -> 0.4048, two items. **Its "generalization" gate is ONE-SIDED and fired
    because held-out precision (0.632) EXCEEDS seen (0.449) -- an EASIER held-out subset, not
    generalization.** *"Independent gold" means independent of reader output; the annotator was the
    authoring agent, same day, single pass. Absolute performance: P=0.50, R=0.34.*
  - **🚨🚨 THE CROSS-CUTTING FINDING, AND IT IS THE ONE THAT EXPLAINS THE 0-FOR-24: NOT ONE OF THESE
    SIX CELLS COMPUTED A SINGLE CONFIDENCE INTERVAL, NULL DISTRIBUTION OR p-VALUE.** Grepped for
    `confidence|ci_low|bootstrap|p_value|binomtest|permutation|half_width`: two hits, both unrelated
    words. **EVERY HARD_PASS IN THIS BATCH IS A POINT ESTIMATE COMPARED TO A POINT ESTIMATE, SEVERAL
    AT GATE MARGINS OF EXACTLY 0.0.** *That is not a scoring accident; it is the archive's method.*
- **🔬🔬 VETTING PASS 3 (`a04ef6b9`): 4 REFUTED, 2 QUALIFIED, 0 UPHELD. RUNNING TOTAL OVER 18 CELLS:
  8 REFUTED, 3 SUSPENDED, 7 QUALIFIED, *** STILL ZERO UPHELD AS CLAIMED ***.**
  **AT 0-FOR-18 THE PRIOR HAS MOVED: A HARD_PASS IN THIS ARCHIVE SHOULD BE READ AS "UNVERIFIED
  CLAIM", NOT AS EVIDENCE. THAT IS NOW A MEASURED BASE RATE, NOT A CAUTION.**
  - **REFUTED -- `exp_gap_driven_reader_controlled_v1`: A 12-LINE `Counter` WITH NO SUBSTRATE
    REPRODUCES THE HEADLINE 8/8 EXACTLY.** Ranking co-occurring unknown words by raw count scores
    1.0000, identical to the treatment. *The templates write the target into 2 of 2 intro sentences
    and the distractor into 1 of 2 -- **the margin is AUTHORED**. Its "ablated=0.0000" arm replaces
    the novelty filter with noise, removing the candidate SET rather than changing the RANKING: an
    extreme lesion, not a matched control.*
  - **🚨 REFUTED -- `exp_reading_grounding_loop_cycle2_v1`: THIS PROJECT ALREADY REFUTED IT ON DISK
    AND THIS DOCUMENT NEVER CAUGHT UP.** `exp_reading_grounding_loop_cycle3_groundingfix_v1` records
    `B1_taut 0.656885 -> 0.0` and `B4_grounded 3544 -> 634`. Independently recomputed from
    `data/foundation/reading_grounding_v1/store/store_facts.json`: **2,328 of 3,544
    GROUNDED_MEANING facts are SELF-ANCHORED -- 67% of "grounded concepts" have THEMSELVES as their
    meaning.** Of the 1,216 real links the top anchors are `also` (31), `say` (15), `people` (10),
    with samples like `web -> polar` and `stargaz -> million`; 121 stem/full-form pairs
    (`cigarett`/`cigarette`) are counted as separate concepts.
    **⛔ RETIRE THE FIGURE "3,544 CONCEPTS / 9.87x THE HAND LEXICON" WHEREVER IT APPEARS.**
  - **REFUTED -- `exp_verb_class_openvocab_similarity_v1`: THE "HELD-OUT" SET IS FOUR VECTORS.**
    In `hdlab/verb_lexical_similarity.py` every desiderative word -- 10 seeds AND all 16 held-out --
    carries the SAME four hand-written tags. **Held-out similarity to its own class is EXACTLY
    1.0000, cross-class 0.0104. The 64 "held-out" decisions are 4 distinct vectors; accuracy 1.0 is
    AN IDENTITY, NOT GENERALIZATION.**
    **AND ITS CITED BASELINE DOES NOT EXIST AS QUOTED:** it claims owner-acc 0.30 from
    `exp_real_text_goal_owner_generalization_diagnostic_v1`, whose single copy on disk reads
    **0.6000** and was written AFTER this cell ran. **The claimed +0.20 is unreproducible.** *In its
    own landed numbers the organ scores 0.5 owner vs recency 0.7 and ties its own lexicon baseline
    on polarity -- it LOSES to one dumb baseline and TIES the other, inside a HARD_PASS.*
  - **REFUTED -- `exp_c5_multigoal_content_coherence_tiebreak_v1`: GOLD IS DEFINED BY THE RULE THE
    MECHANISM APPLIES.** Plain bag-of-words overlap scores **12/12 = 1.0000 under all three tie
    conventions with zero ties**; margin over the strongest floor is **0.0000**. The cell's own
    docstring says gold IS the unique theme-overlapper.
  - **QUALIFIED -- `exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1`: LEAK-CLEAN AND
    REAL, BUT NOT CI-SEPARATED.** It explicitly fixed a predecessor's gold leak and proves it with
    seven self-tests. **But its four floors are ALL POSITIONAL and read 0.0000 BY CONSTRUCTION**,
    while a lexical-overlap floor scores 0.80 / 0.675 depending on tie convention. System 20/20,
    Wilson lower 0.8389 vs the floor's upper 0.9193 -- **overlapping**; paired exact test on the one
    discordant item, p=1.0. *The auditor MEASURED THIS FLOOR AT 0.9839 FIRST AND CORRECTED ITSELF --
    that convention used roster-key order, which favours the owner. Both are reported.*
  - **QUALIFIED -- `exp_reading_grounding_loop_cycle1_v1`:** its context-scramble control BINDS
    (removed 132 of 185), but the same 67% self-anchoring applies, and its curriculum-order arm
    moved link-rate 0.3297 -> 0.3047 -- **a null shipped inside a pass**.
  - **✅ CLEAN ON TWO DIMENSIONS, AND WORTH SAYING: NO LLM in any operational path across six cells
    and four organs (grepped), and every cited path in this batch exists.** *But **NO CELL IN THIS
    BATCH REPORTS A p-VALUE OR A CI AT ALL**, and all three "3-seed" cells return bit-identical
    per-seed numbers BY DESIGN -- one measurement, printed three times.*
- **🔬 VETTING PASS 2 (`afb293f4`): 3 REFUTED, 3 QUALIFIED, 0 UPHELD. RUNNING TOTAL OVER 12 CELLS:
  4 REFUTED, 3 SUSPENDED, 5 QUALIFIED, *** ZERO UPHELD AS CLAIMED ***.**
  - **REFUTED -- `exp_causal_link_comprehension_fuller_v2`: THE ANSWER IS WRITTEN IN.** The cell
    calls `reg.add_causal_link(cause_idx, effect_idx)` for every item and then queries
    `query_effect_of(c_idx)` against `e_idx`. **That is write-then-read from a register at bundle
    load 2, and the two "baselines" NEVER RECEIVED THE WRITE**, so `most_recent=0.0000` and
    `random=0.0000` are STRUCTURAL, not measured. **NO COMPREHENSION WAS TESTED.** *What is
    actually there is 91.7% exact-key retrieval at 697 slots [0.782, 0.971] -- an 8% error rate at
    load 2, which reads as a MILD NEGATIVE ABOUT THE STORE.*
  - **REFUTED -- `exp_pivot_scaled_seed_knowledge_table_v1`: A ZERO-KNOWLEDGE FLOOR COMPUTABLE FROM
    THE CELL'S OWN CACHE SCORES 1.0000 (108/108) AGAINST THE LLM TABLE'S 0.6898.** Its gold is the
    verb's most-frequent attested patient and its distractor a never-attested noun, so plain corpus
    attestation is perfect by construction. **AND SCALING CHANGED NOTHING: the scaled and tiny
    digests are IDENTICAL (`5df85d80df03d57b`), `arms_differ_verified=False`.** *Surviving: LLM
    ratings do carry attestation signal (+0.1852, p=0.0054, n=108). That is not the claim made.*
  - **REFUTED -- `exp_read_grow_adaptor_pyp_kn_breadth_v1`: THE GATE CANNOT FAIL.** `kn_covered =
    (count>0) OR (...)` is a STRICT SUPERSET of flat coverage by construction. **Its "3/3 seeds" is
    ONE measurement printed three times** (identical gain 0.037475 across seeds; the tables do not
    depend on the salt). A **Zipf-count null with no linguistic mechanism reproduces the preemption
    correlation** (-0.60 vs the observed -0.5639 against a -0.15 gate). **On the only genuine
    generalization test -- 132 unseen items -- KN scores 0.1439 vs its OWN scramble 0.1591, WORSE
    in 2 of 3 seeds.**
  - **QUALIFIED -- `exp_information_foraging_reading_v1`: A FLOOR-BEATER, NOT A SHELF-BEATER.**
    FORAGE genuinely beats RANDOM (185 vs 38 of 3000, z=10.1) -- **but FROZEN, the fixed schedule
    foraging exists to REPLACE, scores HIGHER (0.0743 vs 0.0617).** The headline compares only
    against RANDOM. *Any claim that the decision organ improved reading must say this.*
  - **QUALIFIED -- `exp_lexicon_coverage_audit_barrier2_v1`: the COVERAGE half is UPHELD EXACTLY**
    (independently re-implemented: 2077 sentences, 2605 verb tokens, 568 types; union 0.9893/0.9648;
    every figure reproduces to 4 dp). **The second half is a SINGLE-RATER, UNBLINDED LLM
    HAND-AUDIT BY THE AUTHORING AGENT OF THE PREDICTION IT WAS TESTING**, no inter-rater
    reliability. **Under the stricter rubric THE CELL ITSELF NAMES in `honest_limitations`, it is
    89/120 = 0.7417 [0.657, 0.812] -- BELOW its own 0.80 floor.**
  - **✅ QUALIFIED -- `exp_context_vector_signal_v1`, AND A LONG-OPEN QUESTION IS NOW CLOSED CLEAN.**
    CLAUDE.md records that its figure came from a run whose clean-slate teardown was DENIED and
    silently dropped, that the figure is LOAD-BEARING in MEMORY.md, and that closing it needs a
    clean-slate re-run. **IT DOES NOT: the heartbeat trace settles it.** `_start_marker` 22:49:29.5,
    reading pass logged from unit 0 (22:49:43) to unit 49 (22:53:01), `pass_elapsed_s=208.99`; the
    cache is checked BEFORE the pass and skips it on hit, so **unit-0 heartbeats PROVE a cache
    miss**, and the FULL run wrote to a different directory than the denied smoke.
    **CONTAMINATION DID NOT OCCUR -- DEMONSTRATED, NOT ASSUMED. NO RE-RUN NEEDED.**
    **âš ï¸ BUT TWO CORRECTIONS TO HOW IT IS CITED: (a) the HARD_PASS IS POST-HOC -- the pre-registered
    ceiling guard fired on SCRAMBLE_SENT 0.9984 and was AMENDED AWAY AFTER THE RUN; the
    prereg-literal verdict is MIDDLE_BAND. (b) STOP QUOTING 0.7830 vs 0.9984 -- it is
    ceiling-saturated, all three nulls sit at 0.995-0.999. QUOTE `argmax_in_own_window_rate` REAL
    0.2871 vs an EXACTLY BAG-MATCHED SCRAMBLE 0.0050 (informative_rate 0.416808 vs 0.416687).
    A RATE-MATCHED TWIN DOES NOT REPRODUCE IT -- the strongest control-passing result in the batch.**
- **🚨 A THIRD FLOOR-DEFECT CLASS, DISTINCT FROM THE IMPORTED-BAR ONE, AND IT IS THE MOST COMMON:
  THE CELL HAD A STRONGER FLOOR ALREADY COMPUTABLE FROM ITS OWN DATA AND DISCRIMINATED AGAINST A
  WEAKER ONE.** Three of six this pass: attestation at **1.0000**, a superset-by-construction
  coverage gate, and FROZEN at **0.0743**. **THE RULE IS NOT JUST "RECOMPUTE THE FLOOR ON THIS
  REPRESENTATION" -- IT IS "RUN THE STRONGEST FLOOR THE CELL'S OWN DATA SUPPORTS".**
  **AND AUDIT "N SEEDS" FOR SEED-DEPENDENCE: three identical numbers are one measurement.**
- **🔬 FIRST SIX VETTED (`a2e65896`, AUDIT-ONLY, all recomputed off disk from per-item arrays, never
  from `verdict_msg`). ONE REFUTED, TWO SUSPENDED, THREE QUALIFIED. NOT ONE IS UPHELD AS CLAIMED.**
  - **REFUTED -- `exp_base_reader_grounded_relations_coref_v1`.** Headline `coref_lift=0.714,
    p=0.000` is on **SEVEN questions**, and that p is **resample degeneracy**: bootstrapping 7 paired
    diffs gives (2/7)^7 = 0.00016. **Exact paired McNemar on the same 7: p=0.0625, which FAILS its own
    alpha.** Worse, **the cell RAN a real floor arm that scores 5/7 on that slice** -- full vs floor
    p=1.0000 -- and then did not use it as the discriminator. Its NOCOREF control removed **0** items.
    *Surviving secondary: relation_lift over all 25 items, full vs floor exact p=0.0215. That holds.*
  - **SUSPENDED -- `exp_read_grow_foundation_realprose_glassbox_ie_v1`.** Its only floor is a
    **HARDCODED LITERAL `1.0`** (line 749) imported from a DIFFERENT cell on a DIFFERENT corpus (23
    pre-cleaned tuples, where that cell's own docstring says accuracy is 1.0 BY CONSTRUCTION). No
    floor was ever run on this cell's 34 sentences. **This is the SAME defect that suspended 21 arms
    on 08-18 -- and it was already present in JULY.**
    **✅ AND THERE IS A v2 THAT IS THE REAL RESULT: `..._realprose_glassbox_ie_v2` -- 46 sentences,
    correct_rate 0.891 against a REAL STANDALONE baseline of 0.565, delta +0.326, hardcoded stub
    REMOVED. CITE v2. v1 SHOULD NOT APPEAR IN THIS DOCUMENT AT ALL.**
  - **SUSPENDED (UNDERPOWERED) -- `exp_online_knowledge_condenser_selectional_v1`**, the
    best-designed of the six: real held-out split, explicit leakage guard, 4,151 mining sentences.
    **But n=48. FULL 0.750 [0.6275, 0.8725] against a SHUFFLE floor of 0.650 -- the CI lower bound
    sits BELOW the shuffle mean. z=1.07, p=0.285. The "+0.10" is 4.8 items.** Its gate was a bare
    point estimate. **Separating 0.75 from 0.65 at 80% power needs n~350.**
  - **QUALIFIED -- `exp_read_grow_construction_induction_dop_fragments_v1`, and it is the STRONGEST
    thing in the queue.** Only cell on a real external corpus (UD English-EWT, 846 sentences).
    **Scramble binds HARD and is deprel-multiset-preserving: 2/124 vs 44/124, 0/156 vs 44/156, 0/171
    vs 50/171 across three seeds; CI-separated 0.355 [0.271, 0.439] vs scramble upper ~0.038;
    `split_overlap=0`.** *Narrower than "construction induction": the input is GOLD UD `upos`+`deprel`,
    so parsing is ORACLE-SUPPLIED, and the metric is COVERAGE, not correctness (tunable 0.508 /
    0.355 / 0.25 by min_count). Its own verdict says FEASIBILITY PROBE -- that is the honest label.*
  - **QUALIFIED (toy) -- `exp_read_grow_openvocab_fastmap_v1`:** real mechanism, **26 hand-authored
    sentences, 3 nonce words, 5 query cues**; `ABSTAIN_BASELINE=0.0` BY CONSTRUCTION; 5 seeds vary
    only the codebook, so **n=1 dataset**; no CI, no floor, no scramble. Its NO_CONFIRM control DOES
    bind (removed 2 false facts).
  - **QUALIFIED (sharply) -- `exp_read_grow_oov_verb_extension_v1`:** `OOV_VERB_BASE_LEX` (line 165)
    **hardcodes munch->eats, pursue->chases, dwell->live -- THE SAME TABLE GENERATES THE SENTENCE AND
    SCORES IT**, and `coverage_current_pooled = 0.0` by construction, so "+88.2pp" is a gain over a
    definitional zero. Real residue: the morphology inverter. Its OOS control removed **0** items.
  - **🎯 THE CHEAPEST FIX IN THE WHOLE BACKLOG, and it needs no new experiment: SEVERAL CELLS ALREADY
    COMPUTED THE RIGHT FLOOR AND THEN DISCRIMINATED AGAINST SOMETHING ELSE. RE-SCORE EVERY LANDED
    CELL AGAINST THE FLOOR IT ALREADY HAS ON DISK.**
  - **NO LLM IN ANY OPERATIONAL PATH (verified by import scan).** But state these wherever "grounded"
    is claimed: WordNet is LIVE in the coref cell's path supplying the animacy that drives
    resolution, beside a 28-entry hand override and a 13-entry name-gender table curated for those 7
    passages; the condenser's 29-entry seed table is LLM-built OFFLINE and read-only (admissible).
  **ROOT CAUSE, FIXED: `tools/substrate_query.sh` -- the MANDATORY prior-work check -- RETURNS ZERO
  BYTES AND EXITS 0, so every "no prior work found" report from every agent and from me was
  vacuous, and the position document got assembled from whatever I happened to stumble into.**
  Replacement `tools/experiment_index.py` (`dc408b95e`) indexes all 8,834 cells, answers in about a
  second, and **PRINTS HOW MANY ROWS IT SCANNED BEFORE ITS RESULTS**, so an empty answer can never
  again pass for an established absence. **QUERY IT BEFORE WRITING ANY "WE HAVE NEVER" SENTENCE.**
- **â¸ï¸ HALTED ON A WEEKLY USAGE LIMIT (resets 1pm America/New_York). NOT a code, permission or design
  failure -- the scaling-curve cell was dispatched and its agent died on the API limit before writing
  anything. NOTHING IS RUNNING. NOTHING IS HALF-WRITTEN. NO PARTIAL ARTIFACT EXISTS TO CLEAN UP.**
  **RESUME HERE, AND THE WHOLE BRIEF IS ALREADY DECIDED -- DO NOT RE-DERIVE IT:**
  **BUILD: a CORPUS SCALING CURVE, not a single endpoint.** Rebuild the usage representation from
  `data/corpora/simplewiki/simplewiki_clean_v1.txt` at NESTED subsets -- ~0.6M (reproduces today's
  regime as the anchor), 2M, 6M, 20M, 42M tokens -- each smaller set a SUBSET of the larger so the
  curve is about SIZE, not about which text. Score every rung on the dissociation instrument.
  **REPORT MEDIAN CONTEXTS PER EVALUATION WORD at each rung -- that, not raw token count, is the
  quantity that governs a second-order statistic and it is what makes the curve interpretable.**
  **THE PRE-COMMITTED READINGS, decided BEFORE any number exists:** RISING and reaching ~0.5 by 42M
  -> scale was a genuine precondition we never met, and every "this mechanism does not work" verdict
  in this programme was reached where it COULD NOT have worked and must be RE-OPENED, not re-quoted.
  RISING but extrapolating to need MUCH MORE THAN ~50M -> **THE MACHINERY IS NOT BRAIN-FAITHFUL, and
  this is the MOST USEFUL outcome the cell can produce** (report the extrapolated requirement
  explicitly). FLAT -> supply was never binding; the mechanism answers the wrong question; scale
  hypothesis closed. NON-MONOTONIC -> the informative case; report it, do not smooth it.
  **WHY THE CRITERION IS BRAIN-FRAMED AND NOT AN EXCUSE (OWNER, and it is the point of the cell):**
  *"the brain doesn't need 600000 words - if we've set up the machinery right, shouldn't it work?"*
  A child hears on the order of millions of words a year and has real vocabulary by 4-6, so TENS of
  millions of tokens is roughly child scale. **623K is BELOW that -- we have been starving it, which
  is itself not brain-faithful. But needing 1e8-1e9 would be an ADMISSION THE MACHINERY IS WRONG,
  because no child gets that. That is what makes this falsifiable rather than a fudge.**
  **CONTROLS THAT ARE NOT OPTIONAL:** rank-matched null at EVERY rung
  (`tools/rank_matched_null_dissociation.py`) -- without it, a rise toward 0.5 is indistinguishable
  from information destruction, which is exactly the claim that was retracted today; all four floors
  AND the bar RECOMPUTED per rung (a bigger corpus is a DIFFERENT representation, so never import
  0.5431 / 0.5510 / 0.5943 / 0.6317); `F_SCRAMBLE` as a POLICY over >=500 permutations at the 95th
  percentile, reusing the fixed implementation already in
  `experiments/exp_crossview_convergence_hub_v1.py`; CI half-width AND null p95 beside every margin,
  with any rung whose half-width exceeds the chance-to-bar interval marked UNDERPOWERED rather than
  given a verdict; evaluation population HELD FIXED across rungs; checkpoint per rung (42M is a long
  run and must resume).
- **🚨🚨🚨 THE FINDING OF THE NIGHT, AND IT REFRAMES EVERY NEGATIVE ABOVE: WE HAVE BEEN MEASURING
  EVERYTHING ON 623,522 TOKENS. THE METHODS WE KEEP TESTING COME FROM A LITERATURE THAT OPERATES AT
  1e8-1e9. WE ARE 160x TO 1,600x BELOW THE REGIME THEY WERE BUILT FOR.**
  Measured just now, off disk: the store corpus every arm tonight was built on is **34,169 sentences
  / ~623,522 tokens**. **`data/corpora/simplewiki/simplewiki_clean_v1.txt` -- 2,779,032 lines,
  ~41,918,879 tokens, 252 MB -- HAS BEEN SITTING ON DISK THE WHOLE TIME AND WAS NEVER USED TO BUILD
  THE STORE. It is ~67x larger than what we measure on.** *We used it tonight only as a source of
  definition sentences, never as the usage corpus.*
  **WHAT THIS REFRAMES:** SGNS reading BELOW its own untrained control; dependency-typed contexts
  adding nothing; the drill's own note that symmetric-coordination and typed contexts are *"the
  right idea, measured on 1e8-1e9 tokens; our corpus is ~1e6"*; and the definitional teacher channel
  sitting AT CHANCE. **SUBSTITUTABILITY IS A SECOND-ORDER STATISTIC -- it needs enough contexts per
  word to compare two words' context DISTRIBUTIONS. At 0.62M tokens most words have far too few.**
  **âš ï¸ DO NOT OVERSELL THIS EITHER, AND I HAVE ALREADY OVERSOLD ONCE TONIGHT: MORE DATA CANNOT FIX A
  MECHANISM THAT ANSWERS THE WRONG QUESTION.** Co-occurrence accumulated over 42M tokens is still
  co-occurrence. **The honest claim is that SCALE IS A PRECONDITION WE HAVE NEVER ONCE MET, not that
  scale is the answer.** Every "this mechanism does not work" verdict in this programme was reached
  in a regime where the mechanism could not have worked, and that is a DIFFERENT statement from the
  mechanism being wrong. **CHEAP AND DECISIVE: rebuild the usage view on simplewiki and re-measure
  the incumbent. Nothing else should be built until that number exists.**
- **🔴 CROSS-VIEW CONVERGENCE HUB: CLEAN NEGATIVE, `B_NEGATIVE` FIRED AS PRE-COMMITTED. THE
  BEST-CONTROLLED CELL OF THE SESSION, AND THE FIRST BUILT FROM THE BIOLOGY RATHER THAN FROM WHAT
  WAS LYING AROUND.** `experiments/exp_crossview_convergence_hub_v1.py`, all 16 mechanism arms fail.
  Primary `HUB_CCA_BOTH` **0.3129 [0.2630, 0.3644]** against a **RECOMPUTED** bar of **0.5510**;
  margin **-0.2880**. **NOT UNDERPOWERED -- the CI upper bound sits 5.7 half-widths below the bar**,
  so this is a resolved negative, not a width.
  **✅ WHY THE NEGATIVE IS TRUSTWORTHY, and it clears every trap that caught us earlier:** BOTH trap
  pairings stayed dead (0.0446 / 0.1375, `ANY_TRAP_CLEARS_ITS_OWN_BAR` false) so it is not a trap
  artifact; held-out split 3,064 fit / 617 eval with eval words excluded from the SVD basis,
  vocabulary, CCA, ridge, lambda AND k*; all four floors NOT_SEPARATED, known-answer 0.9612, random
  0.4919; **the coverage control removed 40 of 242 rows (16.5%) -- IT BINDS**, unlike the one that
  removed 0 of 242 earlier tonight. A **planted-positive self-test** refused the cell until the
  pipeline could recover a planted invariant (now hub 0.9934, raw views 0.0000).
  **🔴 RETRACTED WITHIN THE HOUR BY THE BRAIN DRILL (`9f27cc5e9`) -- I RELAYED THE 0.06 -> 0.31 MOVE
  TO THE OWNER AS "GENUINELY STRIPS CO-OCCURRENCE". IT IS NOT. THERE IS ZERO MEASURED EXTRACTION.**
  **A RANDOM 8-DIMENSIONAL PROJECTION OF THE INCUMBENT STORE -- WHICH NEVER SEES THE DEFINITIONAL
  CHANNEL AT ALL -- READS 0.3079 [0.2697, 0.3495]. THE ARM READS 0.3129, INSIDE THAT BAND.**
  Dose-response on RANK ALONE reproduces the whole effect: k=2 -> 0.4127, k=8 -> 0.3079, k=32 ->
  0.1770, k=128 -> 0.0798, k=256 -> 0.0536 (centring alone 0.0536, so it is RANK, not centring).
  **AND WORSE: pipeline-matched -- same whitening, same rho, same k*=8, ONLY THE DIRECTIONS
  RANDOMISED -- the null reads 0.3312 and BEATS the real `HUB_CCA_X` (0.2458) IN 200 OF 200 DRAWS.
  THE CROSS-VIEW-CHOSEN DIRECTIONS ARE WORSE THAN RANDOM ONES.**
  **🚨 THE GENERAL LESSON, AND IT IS A NEW FLOOR WE HAVE NEVER HAD: WHEN THE BASELINE SITS FAR BELOW
  CHANCE, DESTROYING INFORMATION MOVES THE SCORE TOWARD 0.5 AND READS AS PROGRESS. THE ENTIRE
  INTERVAL (0.06, 0.50) IS REACHABLE BY PURE DEGRADATION, AND NOT ONE FLOOR IN OUR BATTERY CATCHES
  IT.** *Any future "we moved from 0.06 toward 0.5" claim is void until it beats a RANK-MATCHED
  null.* Control now exists: `tools/rank_matched_null_dissociation.py`.
  **ALSO: the teacher channel was AT CHANCE BEFORE THE HUB WAS BUILT ON IT -- `A_DEF` 0.4780
  [0.4223, 0.5350], NOT separated from 0.5.** *I quoted 0.4780 as a point value; it is a width.*
  **TWO SETUP WEAKNESSES NAMED: the channel-independence preflight has a CEILING (r >= 0.95) but NO
  FLOOR, and the pairing sat at r=0.0363 with held-out cosine 0.0512 -- the channels were nearly
  UNRELATED, which is as fatal as being redundant; and `lam_rel=1.0` was selected AT THE GRID
  BOUNDARY in 3 of 4 pairings with the objective still climbing, so k*=8 is a truncated-search lower
  bound, not an optimum.**
  **SCOPE, as pre-registered: one definitional channel, one usage channel, one LINEAR extractor,
  one instrument, n=202. It says the missing ingredient is not a second view OF THIS KIND.**
- **🚨 A LICENSING DEFECT THIS CELL FOUND THAT REACHES BACKWARDS INTO EVERY RUN WE HAVE GATED:
  `F_SCRAMBLE` WAS A SINGLE COIN FLIP.** Its first smoke voided on `F_SCRAMBLE` 0.4266
  [0.3701, 0.4867] -- **one permutation's own CI excludes 0.5 about 5% of the time BY CONSTRUCTION,
  and across four floors that voids or passes roughly 18% of runs ON NOISE ALONE.** Measured
  single-draw false-fire rate **0.010-0.080 across 17 floors** -- that is the receipt, not an
  estimate. **FIXED HERE: `F_SCRAMBLE` is now a POLICY over 500 permutations with the bar term taken
  from the 95th percentile of that distribution -- which RAISED the bar and made it the BINDING
  term (0.5510).** *So this cell was judged against a HARDER bar than any predecessor.*
  **OPEN AND NOT YET ASSESSED: every earlier licensing decision in this programme used the
  single-draw form. That does not invalidate them, but it means an unknown fraction turned on a coin
  flip, and the fix belongs in the shared instrument, not in one cell.**
- **🚨🚨🚨 AUDIT LANDED 06:52 (`37181d944`) -- BRANCH (i): 3 CELLS, 21 ARMS MIS-GATED, TWO OF THEM NEW.
  AND IT SURFACED SOMETHING LARGER THAN THE IMPORT: THE BAR ITSELF WAS NEVER SEPARATED FROM CHANCE.**
  **`F_CONSTANT_PROTOTYPE` = 0.5431 CARRIES CI [0.4922, 0.5953] -- IT INCLUDES 0.5.** I checked the
  human instrument's bar too: **`F_SCRAMBLE` = 0.5943, CI [0.4937, 0.6911] -- ALSO INCLUDES 0.5.**
  **BOTH BARS THIS PROGRAMME GATES ON ARE STATISTICALLY INDISTINGUISHABLE FROM CHANCE AT THEIR OWN n.**
  *I spent two days correcting people that "the bar is 0.5431, NOT 0.5" -- and the honest statement is
  that at these sample sizes THE TWO CANNOT BE TOLD APART. That correction was itself a width read as
  an effect: discipline 14, committed by the person who wrote it.*
  **MECHANISM (DSI L99-108): `F_SCRAMBLE` and `F_CONSTANT_PROTOTYPE` are computed FROM THE STORE
  MATRIX; the other two are not. The bar is always owned by one of those two -- SO THE BAR IS
  INHERENTLY THE REPRESENTATION-BOUND QUANTITY.** *That is why importing it across representations
  was guaranteed to be wrong, not merely unlucky.*
  **THE THREE, ALL `SUSPENDED, NOT REFUTED` -- a wrong floor makes a verdict UNSUPPORTED, it does NOT
  establish the opposite:** (A) the typed-role arc cell, already retracted; (B) **NEW --
  `exp_typed_role_selectional_asset_writerule_v1` (`c1d2bc80e`, 7 arms)**, corroborated off its own
  data: **its must-fail controls `N1` 0.5516 and `N3` 0.5630 sit ABOVE the 0.5431 bar**, so its native
  floor is ~0.55-0.56 and the imported bar was too low, *same direction as the arc rebuild*; (C)
  **NEW -- tonight's human-instrument cell (`16475c9c5`, 4 arms)**, which re-derived its bar sincerely
  but along the wrong axis -- right population, from v3 arrays built on the **bag** store.
  **✅ WHAT SURVIVES UNTOUCHED, and this matters: (B)'s `WORD_SELECTION_NOT_TYPE` verdict is
  WITHIN-CELL and same-representation, so it STANDS; no false positive was manufactured anywhere
  (B's `T1` never cleared the bar even at its CI lower bound 0.5296); and BRANCH (B) FROM 6.39 STANDS
  *A FORTIORI* -- `U1` 0.4125 failed a bar we now know was TOO LOW.**
  **NOT A PROGRAMME-WIDE CRISIS, and I was primed to call it one.** The write-rule ladder already does
  this correctly **per arm** (`F_CONSTANT_PROTOTYPE__<arm>`); `corpus_capacity`, `tuned_count` and
  `predictive_coding` gate on 0.5 and hold 0.5431 only inside regression gates. **Branch (iii) ALSO
  fired: NO `metrics.json` ANYWHERE records the REPRESENTATION a floor came from** -- every
  determination above needed the source, so this is unauditable from artifacts today.
- **🔴🔴 07:05 -- THE DEGENERACY HYPOTHESIS BELOW IS NOW CONFIRMED FROM THE CELL'S OWN PERSISTED
  DIAGNOSTICS, AND IT MEANS THE HUMAN INSTRUMENT COULD NOT FAIRLY TEST `U1` AT ALL.**
  `report/OCCURRENCE_DATA_STATS`: **`n_occurrences_total` = 10,215, `n_occurrences_with_slot` =
  1,112. ONLY 10.9% OF OCCURRENCES ON THIS POPULATION CARRY THE SLOT INFORMATION THE TYPED ARM IS
  BUILT FROM.** And `report/ARM_DIAGS` gives `U1` **`vocab_size` = 10,121** dimensions. **That is
  ~8.6 SLOTTED OCCURRENCES PER WORD SPREAD OVER A 10,121-DIMENSIONAL SPACE.** *Nearly every pair of
  words shares no dimension at all, so nearly every cosine is zero and the arm collapses onto the
  constant-prototype value -- which is EXACTLY the 0.4125/0.4125 tie the audit spotted.*
  **THE CONTRAST INSIDE THE SAME RUN SETTLES IT: `U3_ROLE_ONLY` uses `vocab_size` = 58 -- DENSE --
  and reads 0.5037, at chance but NOT degenerate. Same corpus, same population, same 28,832 arc
  events; the only thing that changed is how thinly they were spread.**
  **WHAT THIS DOES TO BRANCH (B). THE BRANCH FIRED AS PRE-COMMITTED AND I AM NOT UNFIRING IT -- BUT
  ITS INTERPRETATION IS NOT SUPPORTED. "The 0.6669 was WORDNET-SPECIFIC" REQUIRES THAT THE HUMAN
  INSTRUMENT GAVE THE ARM A FAIR TEST, AND AT 10.9% SLOT COVERAGE IT DID NOT.** *The correct reading
  is much closer to 6.39's branch (C): **this population cannot test this arm.** The agent noted (C)
  "did not fire only because `U1` is not above chance" -- and a starved arm sitting ON its own
  constant floor is precisely how an untestable arm presents.*
  **WHAT IS STILL TRUE AND MUST NOT BE QUIETLY DROPPED: THIS DOES NOT RESCUE THE 0.6669.** That
  number died for an unrelated and still-standing reason -- **its bar was a bag-representation floor,
  and on a rebuilt arc floor a no-words attestation control reads 0.6317.** *Two independent defects,
  one per instrument; fixing this one does not touch that one.*
  **AND IT CONVERGES WITH THE BIOLOGY DRILL, WHICH REACHED THE SAME DIAGNOSIS FROM THE OTHER
  INSTRUMENT: "a median 130 arcs per word cannot populate 21,093 dimensions -- the lexical channel
  was STARVED, NOT FALSIFIED." TWO LANES, TWO POPULATIONS, SAME CAUSE.** *The typed channel has never
  once been given enough data to be tested, on EITHER instrument.*
  **HONEST SCOPE: I measured SLOT COVERAGE, which is the upstream CAUSE. I did NOT measure the
  pairwise-cosine spread, which is the direct SYMPTOM and is still the cleaner confirmation.** *I said
  I would not rewrite branch (B) before measuring, and I am recording a re-interpretation on
  different evidence than the check I named -- stronger evidence, but not the same evidence. The
  cosine-spread check stays open.*
- **🔬 [SUPERSEDED BY THE CONFIRMATION ABOVE] MY OWN FOLLOW-UP, HYPOTHESIS NOT FINDING -- THE ONE ITEM THE AUDIT FLAGGED AND LEFT UNVERIFIED,
  NOW CONFIRMED NUMERICALLY AND IT MAY RE-INTERPRET BRANCH (B).** In the human cell, `U1_TYPED_CONTEXT`
  reads **0.4125 [0.3148, 0.5138]** and `F_CONSTANT_PROTOTYPE` reads **0.4125 [0.3164, 0.5153]** --
  **IDENTICAL TO FOUR DECIMALS, different CIs** (so two genuinely different computations, not one value
  copied). **`F_CONSTANT_PROTOTYPE` IS BY DEFINITION WHAT YOU SCORE WHEN EVERY WORD HAS THE SAME
  VECTOR.** *So the live alternative to "typed context is bad at human similarity" is **"typed context
  produced near-DEGENERATE vectors on this 65-pair population"** -- which would make branch (B) a
  statement about COVERAGE COLLAPSE, not about the channel.* **CHEAP DECISIVE CHECK, NAMED AND NOT RUN:
  the pairwise-cosine spread of `U1`'s vectors on that population -- near-zero spread confirms
  degeneracy.** **DO NOT REWRITE BRANCH (B) UNTIL THAT IS MEASURED; an exact tie at n=65 is suggestive,
  not proof, and I have twice tonight promoted a suggestive number too early.**
- **🚨🚨 RETRACTION, 06:15 -- I HEADLINED "THE FIRST ARM EVER TO CLEAR THE BAR" AND TWO INDEPENDENT
  LANES TOOK IT APART WITHIN THE HOUR. THREE OF THE FOUR SUPPORTS ARE GONE. READ THIS BEFORE THE
  GREEN BLOCK BELOW, WHICH IS SUPERSEDED.**
  1. **THE BAR WAS THE WRONG BAR -- MY OWN RULE, BROKEN BY THE CELL AND MISSED BY ME.**
     `bfc0e941c` rebuilt the arms from the cell's persisted `arc_events`, **reproduced U1 0.6669 /
     U3 0.6466 exactly**, then recomputed the floors **on the arc representation the arms actually
     use.** An **ATTESTATION floor -- `log(min(arc_mass))`, NO WORDS, NO MEANING -- reads 0.6317
     [0.5820, 0.6781]**, effectively at the 0.6669 headline. The 0.5431 bar was a **BAG**-
     representation number imported across representations. *"EVERY FLOOR RECOMPUTED ON THE ITEM'S
     OWN POPULATION, NEVER IMPORT" is discipline (2) in this file, and the run imported one.*
     `U1_COVERAGE_MATCHED` could not catch it -- `COVERAGE_MIN=3` dropped **0 of 242 pairs**, so the
     control never bound.
     **WHAT SURVIVES, AND IT IS NOT NOTHING:** on a **mass-matched subsample (n=189, residual floor
     0.507)** the effect holds -- **U3 0.6369, U1 0.6284** -- and against **frequency-matched random
     noun pairs** U3 reads **0.5958 [0.5458, 0.6458]** vs floors 0.5141 / 0.5053. **A 64-bin role
     histogram with the words thrown away does carry real substitutability. It is a SMALLER, HONEST
     result standing on a REBUILT floor, not the headline I wrote.**
  2. **🔴 "SECOND INDEPENDENT NEGATIVE ON PREDICTION ERROR" IS RETRACTED OUTRIGHT -- I VERIFIED THE
     DEFECT IN SOURCE MYSELF.** `store_from_s1` and `store_from_s1_permuted_magnitude` both iterate
     **`rec["bag_counts"]`** (`experiments/exp_typed_role_context_write_rule_dissociation_v1.py`
     ~590-640, called at 954-957). **The prediction-error rule was applied to the BAG channel -- the
     one already known to be a pure co-occurrence detector at A0 0.0510 -- NOT to the typed channel.**
     That is why S1 0.0695 and N3 0.0591 sit right beside A0. **A null there says essentially nothing
     about whether an error signal helps the typed representation. PREDICTION ERROR ON THE TYPED
     CHANNEL HAS NEVER BEEN TESTED.** *I propagated this claim twice tonight.*
  3. **THE CORRUPTION-TOLERANCE EVIDENCE IS RETIRED.** `N6` replaces corrupted arcs by drawing from
     the marginal, which **adds a shared vector to every word -- near rank-preserving for a rank-sum
     AUC. THE CONTROL AS BUILT IS NEARLY INCAPABLE OF FAILING**, so "survives 50% corruption" was a
     property of the corruption model, not of the representation.
  4. **BRANCH (B) FIRED ON THE HUMAN INSTRUMENT (`16475c9c5`), EXACTLY AS PRE-COMMITTED AT
     `fa5da1d2c`: `U1_TYPED_CONTEXT` = 0.4125 [0.3148, 0.5138] -- BELOW CHANCE.** (`U3` 0.5037,
     `T2` 0.3567; bar 0.5943 **derived here, nothing imported**; both gates PASS.) **6.24 PARTIALLY
     RE-OPENS: the two instruments agree about the poor arms (rho 0.9034) and DISAGREE at the top of
     the range, which is the only region anyone cares about.** **THIS IS THE INFORMATIVE CASE AND IS
     NOT TO BE WRITTEN UP AS "MIXED".**
     **CONFOUND, FLAGGED BY THE AGENT AND NOT RESOLVED: that human population is 83% VERB pairs
     (108v / 18n / 4a) while the WordNet instrument is NOUNS-ONLY. "WORDNET-SPECIFIC" AND
     "NOUN-SPECIFIC" ARE NOT SEPARATED BY THIS RUN.** *A POS-stratified re-read is named, not run.*
  - **WHERE THAT LEAVES THE "WHICH KIND OF SLOT, NOT WHICH WORD" READING -- THE TWO LANES DISAGREE,
    AND THE DISAGREEMENT IS THE POINT.** The OBSERVATION replicates on both sticks (`U1-U3` NOT
    separated: +0.0203 [-0.0185, 0.0591] WordNet, **-0.0911 [-0.2014, 0.0192] human**). But
    `bfc0e941c` argues the tie is **DATA POVERTY, NOT A FINDING: a median 130 arcs per word cannot
    populate 21,093 dimensions, so the lexical channel was STARVED, NOT FALSIFIED** (effective code
    is **~3 relation bins**; top-3 gives 0.6240 of U3's 0.6466). **A starved lexical channel would
    tie on BOTH instruments too, so replication does not discriminate.** *The observation stands;
    my interpretation of it does not follow. I stated it as the finding twice.*
  - **🧠 THE BIOLOGY PUTS THE WHOLE NIGHT IN A DIFFERENT FRAME (PINNED, and the most useful thing
    anyone produced tonight): taxonomic (ATL) and thematic (pMTG/TPJ) systems DOUBLY DISSOCIATE.
    OUR INSTRUMENT *IS* THAT DISSOCIATION MEASURED IN A CORPUS, AND THE WINNING ARM IS THE THEMATIC
    ORGAN DOING THE TAXONOMIC ORGAN'S JOB.** Coarse frames drive **CATEGORY** induction unsupervised
    (Mintz 2003); syntactic bootstrapping shows frames **CONSTRAIN** a meaning hypothesis, they do
    not **SUPPLY** it. **So role profile = STAGE ONE, grounded cross-modal convergence = STAGE TWO --
    WE BUILT STAGE ONE AND SCORED IT ON A STAGE-TWO INSTRUMENT.** *That, not the AUC, is the finding
    worth keeping.* **OPEN (do NOT write as pinned): whether role is coded SEPARATELY from filler --
    F&G's own ROIs reanalyse as non-orthogonal, and Fedorenko 2020 finds NO syntax-selective region.*
- **[SUPERSEDED BY THE RETRACTION ABOVE -- KEPT SO THE OVERCLAIM STAYS VISIBLE] LANDED 05:36
  (2026-08-18) -- `exp_typed_role_context_write_rule_dissociation_v1` (`5170c7751`).**
  Instrument re-licensed IN THIS RUN (all 8 cached DSI checks reproduced at delta 0.0000, floors at
  chance, **n=242 per cell** -- not the n=7 of the human v1 attempt). **Matching is per-POS-stratum,
  so SET_P/SET_S cannot differ in POS by construction.**
  **`U1_TYPED_CONTEXT` 0.6669 [0.6184, 0.7136] vs incumbent bag-of-words `A0` 0.0510** -- and the
  three mandatory controls all held: beats `N1_LABEL_PERMUTED` **+0.1105 [0.0800, 0.1420]**, beats
  `N2_RANDOM_TYPING` **+0.1068 [0.0696, 0.1449]**, and `U1_COVERAGE_MATCHED` is 0.6669, unmoved.
  **READ THE MARGINS FROM THE PAIRED-DIFFERENCE CI, NOT FROM WHETHER THE TWO ARMS' OWN CIs OVERLAP**
  -- I misread overlap as "not separated" while checking this, and the two tests disagree.
  **BUT `STOPIF3` FIRED AND IT DOWNGRADES THE HEADLINE: `U3_ROLE_ONLY` 0.6466 TIES `U1`**
  (+0.0203 [-0.0185, 0.0591], NOT separated), and an independent parse-noise sweep **barely moved the
  score -- 0.667 -> 0.651 with 50% of the parse neighbours CORRUPTED.** *If half the neighbours can be
  wrong and the answer survives, the specific typed neighbours are not what is carrying it.*
  **THE HONEST CLAIM IS THE COARSER ONE: most of the signal is WHICH KIND OF SLOT a word fills, not
  WHICH WORD fills it.** `T2_UNTYPED_SAME_COVERAGE` 0.6128 clears the bar on its own -- selection
  carries the bulk -- with the type label adding a real but small CI-separated increment
  (**+0.0541 [0.0339, 0.0753]**). **DO NOT WRITE "GRAMMAR CARRIES SUBSTITUTABILITY."**
  **SECOND INDEPENDENT NEGATIVE ON PREDICTION ERROR:** `S1_SLOT_COMPETITION` 0.0695 does NOT beat
  `N3_MAGNITUDE_PERMUTED` 0.0591 (+0.0104 [-0.0069, 0.0289]). *That is now twice, on different
  mechanisms.*
  **AND 6.38's PREMISE REPLICATES ACROSS CORPORA:** `T3_COMBINED` (the published Komninos &
  Manandhar window+dependency pattern) **HURT in both corpora** -- 0.3533 here, **-0.3136
  [-0.3476, -0.2812] vs `U1` alone**, and 0.2264 on SimpleWiki. **Concatenating an anti-correlated
  channel is now a two-corpus finding, not a one-off.**
  **CORRECTION TO MY OWN 93d54ba72, MADE 10 MINUTES EARLIER: I claimed this run's stdout log lagged
  its `units.jsonl` because stdout was block-buffered. THAT WAS WRONG.** Re-checked at 05:34: both
  mtimes 2 min ago, in sync. The 11-minute gap I saw was **PRINT CADENCE** -- the occdata stage prints
  every 100 words, and 381 units sat between the 300 and 400 marks. *There is no buffering defect;
  `units.jsonl` mtime is still the better liveness signal, but the log is not lying.*
- **🟢 LANDED 05:44 -- `exp_dissociation_score_instrument_human_v4` (`75e093747`). THE 6.24 WORDNET
  CAVEAT IS DISCHARGED. VERIFIED OFF DISK BY THE DIRECTOR, NOT TAKEN FROM THE AGENT'S PROSE.**
  **rho = 0.9034 at 24 arms, bootstrap-of-arms 95% CI [0.7548, 0.9676] -- EXCLUDES ZERO**, against
  rho 0.7857 / CI **[-0.0435, 1.0]** at 7. **Pre-committed branch (i) fired.** *The arm count really
  was the limit: with 7 arms the CI could not separate from zero at any estimate quality.* Both
  regression gates PASS (DSI 8 checks at tol 0.0005; v3 floors + n=65 bit-for-bit).
  **WHAT THIS BUYS: every Organ A conclusion rested on an instrument built from WordNet, and the fear
  was that we had only ever measured AGREEMENT WITH WORDNET. Two independently-built instruments --
  one from WordNet, one from published HUMAN similarity ratings -- now rank our 24 arms the same way.
  ORGAN A'S CLOSURE IS A FACT ABOUT OUR STORE.**
  **🚨 BUT READ THE HUMAN ARM TABLE BEFORE CELEBRATING: ALL 24 ARMS SIT AT OR BELOW CHANCE ON HUMAN
  JUDGEMENTS.** The two best straddle 0.5 and clear nothing -- `F1_NO_FILTER` [0.4542, 0.6508],
  `T1_TYPED_ROLE` [0.4054, 0.6057] -- and the human bar is **0.5943**. *Agreeing about the ordering of
  24 arms is not the same as any arm being good; the instruments agree that they are all poor.*
- **🎯 THE OBVIOUS NEXT TEST, AND NOBODY HAS RUN IT: `U1_TYPED_CONTEXT` (0.6669, the only arm ever to
  clear the WordNet bar) IS NOT IN THE 24.** It landed at 05:36; the harvest was already built. The
  `T1_TYPED_ROLE` in the table is the **SimpleWiki** arm, a DIFFERENT cell. **So the one arm that
  cleared a bar has never been scored against human judgement.** v4 now has the harvesting machinery,
  so this is cheap. **rho = 0.9034 predicts it should replicate -- WHICH IS EXACTLY WHY IT IS WORTH
  RUNNING: a pre-committed prediction that can FAIL.** *Recorded, deliberately NOT dispatched --
  CLAUDE.md's rule is that an agent report ends my involvement and the owner decides what happens
  next.*
- **🔴 LANDED (`1b79ae57b`) -- SENSORIMOTOR CHANNEL: BRANCH (B) FIRED, EXACTLY AS PRE-REGISTERED AT
  `73edbca69`. THE PERCEPTUAL ROUTE IS CLOSED AT THIS RESOLUTION, AND THE MECHANISM IS THE VALUABLE
  PART.**
  Best arm `SM11_Z_NEG_EUCLID` **0.6039 [0.5439, 0.6644]** against a **credible bar of 0.6791**
  (margin **-0.0752**). **AND IT IS WORSE THAN THAT: IT SITS BELOW THE CONSTANT/PROTOTYPE FLOOR'S OWN
  POINT VALUE (0.6195). 0 OF 6 GRID POINTS CLEAR; ALL SIX CIs OVERLAP THAT FLOOR.** Coverage **166 of
  242** matched units, **557/617 = 90.3% of words -- independently reproducing the drill's §3.2
  figure**, so this is not a coverage failure.
  **🔬 THE MECHANISM, AND IT IS THE FINDING: THE ONLY THING THAT DISCRIMINATES IS A *QUERY-INDEPENDENT
  PER-WORD GENERICITY SCORE* -- ONE THAT NEVER COMPARES THE TWO WORDS AT ALL -- READING 0.6195,
  CI-SEPARATED ABOVE CHANCE AND BEATING EVERY PAIRWISE DISTANCE.** Centring collapses cosine
  0.5990 -> 0.5381 while euclidean is unmoved: **the cosine "signal" was carried by the SHARED
  PROTOTYPE DIRECTION.** Both cells sit in a narrow cone (within-pair cosine 0.8768 vs 0.8434) and
  **effective dimensionality is 6.26 OF 11.** *So the norms do carry a real signal -- "how generic is
  this word" -- and it is NOT "are these two words alike". That is the constant/prototype floor's
  signature, which is precisely what the drill predicted.*
  **✅ THE NEGATIVE IS REAL AND WAS CHECKED BEFORE ANY BRAIN TALK (discipline 17's first clause):**
  instrument still licensed at n=166 (four floors CI-include 0.5; incumbent 0.0884); the
  **planted-separable self-test fires at the deciding n or the cell aborts**; scramble changes 100%
  of scores. **NOT A POWER PROBLEM -- the best arm is below the floor's POINT value, so no amount of
  n converts it.** *Concreteness alone (1 dim): 0.5388 vs its own bar 0.6256 -- also beaten by its
  own floor.*
  **âš ï¸ TWO DISCLOSURES, BOTH THE AGENT'S OWN:** (1) known-answer reads **0.9448 [0.9204, 0.9654]** vs
  a 0.95 **point** gate -- **fails strict-point by 0.005, passes CI-inclusive**; the branch was driven
  by the CI form, both printed, decided and written into the docstring BEFORE the FULL run. (2)
  **`F_PROTOTYPE_MAGNITUDE__CONC1` = 0.3195: `SET_S` PAIRS ARE RELIABLY MORE CONCRETE THAN `SET_P`.**
  *The matcher balances on frequency/length/POS -- NOT on rating-norm properties -- so **discipline 16
  is live here in a new form: the POPULATION is unbalanced on the very axis this channel measures.***
  **WHAT IT DOES AND DOES NOT CLOSE: it refutes THIS RESOLUTION (11 dims), NOT GROUNDING.** And the
  trade is now measured rather than assumed: **Binder's 65 dimensions discriminate far better but
  cover 9.2% of eval words / 5.0% of anchors, and a unit needs ALL FOUR words covered -- which
  collapses the instrument below the "a win on 20 pairs is not a win" line. NO ASSET WE CURRENTLY
  HOLD SITS ON THE GOOD SIDE OF THE COVERAGE-RESOLUTION TRADE.** *The image-derived relational subset
  (57.9%) is a different KIND of signal and a separate cell.*
- **[SUPERSEDED -- LANDED ABOVE] SECOND LANE (08:05) -- `sensorimotor-discrimination`. THE MOST CONSEQUENTIAL TEST OF THE NIGHT,
  AND IT IS PRE-REGISTERED TO FAIL IN A SPECIFIC WAY. DO NOT RESPAWN.**
  **Question, deliberately narrow: does a PERCEPTUAL profile separate `SET_P` from `SET_S` AT ALL?
  A SIGNAL THAT CANNOT DISCRIMINATE CANNOT TEACH**, so this gates every downstream supervision idea.
  Data verified on disk by me: `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`,
  16.4 MB, 39,707 rows, all 11 mean dimensions present. **NOT text-derived, NOT WordNet-derived, NOT
  an LLM -- which is exactly why it is admissible where every other candidate was circular.**
  **Branches pre-committed at `73edbca69` (6.43) BEFORE dispatch. THE FAILURE MODE IS NAMED IN
  ADVANCE: `SET_S` pairs are same-POS same-domain nouns ("calcium/carbonate") that may share a
  sensorimotor profile just as the synonyms do, so this channel may behave like the
  constant/prototype floor -- OUR STRONGEST. IF THAT FIRES IT REFUTES THIS RESOLUTION (11 dims), NOT
  GROUNDING**, and the report must name what resolution would be needed rather than concluding
  grounding fails. *Binder's 65 dimensions discriminate better but cover 9.2% of eval words.*
  **IT IS A DISCRIMINATION TEST, NOT A SUPERVISION BUILD -- if it passes, the supervision cell is a
  SEPARATE decision with its own pre-commitment.**
- **🔵 FIRST LANE (07:20) -- `typed-density-sweep`. DO NOT RESPAWN.**
  Sweeps the typed channel's density by coarsening `(neighbour, relation, direction)` binning from
  ~10,121 dimensions toward `U3`'s 58, **recomputing every floor PER CONFIGURATION on that
  configuration's own representation.** **Branches PRE-COMMITTED at `0504bfd00` (plan 6.41) BEFORE
  dispatch -- READ THEM BEFORE READING ITS RESULT:** *(α) some density clears its own rebuilt floor
  -> the channel was starved, and **the occurrences-per-dimension at which it turns on IS the
  finding, not the AUC**; (β) nothing clears anywhere -> it does not carry substitutability at any
  density reachable **on THIS corpus** -- **state the corpus and range, do NOT call it impossible**;
  (γ) it clears only once coarsened onto `U3` -> **role identity is the carrier, typed context adds
  nothing, headline is `U3`** -- pre-committed as **the branch I expect to dislike**, and it must not
  be softened.*
  **IT WAS TOLD TO COPY THE WRITE-RULE LADDER'S PER-ARM FLOOR PATTERN AND EXPLICITLY *NOT* THE CELL
  THAT IMPORTED 0.5431.**
- **📋 BOARD FELL 13 -> 3 WITH NO OWNER INPUT THIS SESSION. NOTED, NOT CHASED.** *Consistent with the
  seven duplicate `rm`-denial questions being auto-closed -- which is what the triage predicted would
  happen once the underlying fault stopped recurring -- but **I have not verified that** and it
  should not be reported as if I had.*
- **[LANDED -- kept for the compaction reader] IN FLIGHT (2 lanes, both dispatched 05:50-05:55). DO NOT RESPAWN EITHER -- a duplicate is the
  more expensive error, and I made exactly that mistake twice tonight.**
  1. **`U1` ON THE HUMAN INSTRUMENT** -- scoring `U1_TYPED_CONTEXT`, `U3_ROLE_ONLY` and
     `T2_UNTYPED_SAME_COVERAGE` against human similarity ratings (n=65, bar **0.5943**). **Its
     branches were PRE-COMMITTED at `fa5da1d2c` BEFORE dispatch -- plan 6.39. READ THEM BEFORE
     READING ITS RESULT.** *(A) clears CI-separated -> holds on two independent instruments;
     (B) at or below chance -> the 0.6669 was WordNet-specific, rho 0.9034 was carried by the poor
     arms, instruments DISAGREE where it matters, 6.24 partially RE-OPENS -- **the informative case,
     NOT "mixed"**; (C) above chance but not separated -> **`POWER_INSUFFICIENT`, NOT a ceiling.***
  2. **BIOLOGY DRILL: role vs filler** -- how cortex represents a word's grammatical role, whether
     role is coded separately from the word filling it, and **whether our coarse corruption-tolerant
     role profile REPLICATES something real or is a symptom of an impoverished encoding.** *That
     second reading is the one that would deflate tonight's result, which is why the drill was told
     to argue both.* Writes a note only; touches no cell.
- **âš ï¸ WHY (C) IS A LIVE OUTCOME, NOT A HEDGE: the human population is n=65 against the WordNet
  instrument's n=242 -- 3.7x smaller -- and v4's human CI half-widths run ~0.10, WIDE ENOUGH TO
  SWALLOW THE ENTIRE 0.6669-vs-0.5943 MARGIN BEFORE ANY CAPABILITY QUESTION IS ASKED.** *Do not let
  a width be read as an effect in either direction.*
  **This is NOT evidence it is dead.** I misread agent silence as death twice tonight and was wrong
  both times -- once standing down a healthy agent that was authoring a 58 KB cell. **Do not respawn
  it; a duplicate is the more expensive error.**
  **NEITHER MAY BE HEADLINED ALONE.** Pre-commitment 6.35 governs (a): it is one half of a
  cross-corpus PAIR with the landed SimpleWiki arm, and *"one of two independent tests is not a
  result"*. **If the two DISAGREE that is the informative case and must NOT be reported as "mixed".**
- **SUPERSEDED IN-FLIGHT NOTE (2026-08-18 ~04:45):** (a) **typed-role write rule** (re-dispatched tight after the
  first attempt stalled an hour on my own over-broad enumeration instruction); (b) **frequency-
  stratified matcher** -- matches WITHIN frequency bands instead of one global caliper, to fix the
  n=7 cause above. **Its gate is unchanged: if it buys n but ANY floor leaves chance, it is REJECTED
  as a worse matcher.** A bigger sample of an unlicensed instrument is worse than no sample.
- **SUPERSEDED IN-FLIGHT NOTE (2026-08-18 ~04:20):**
  (1) **`typed-role write rule`** -- the FIRST arm in ~15 experiments to use the GRAMMATICAL RELATION
  rather than an unordered bag of words. *Every prior arm varied WHICH words counted or HOW they were
  weighted; none used the role label.* Uses `data/selectional_preferences_v1/` (41,529 verb+ROLE
  slots, 90.0% coverage of the 617 scored words, no WordNet, no LLM). Carries an UNTYPED
  same-coverage twin so a win cannot be credited to TYPE when it is really SELECTION, plus
  label-permuted / magnitude-permuted / coverage-matched controls (SET_P 218 vs SET_S 185 coverage
  asymmetry is the flagged artifact risk).
  (2) **`human instrument v2`** -- rebuilt on ITS OWN population after v1 collapsed to **n=7**. That
  collapse was a DESIGN error, not sampling: the deciding statistic is a RANK CORRELATION OVER ARMS,
  which does not require shared ITEMS, and restricting to the WordNet instrument's 617 words threw
  away ~550 of 573 usable SimLex pairs. **Absolute AUCs will NOT be comparable across the two
  instruments -- ONLY the ordering.** See `PLAN_ORGAN_STEP_LADDERS` 6.30.
- **DISK IS FINE (checked 04:20):** one KB staging dir at ~0 MB (not the documented 10.65 GB
  runaway), 456 GB free. The main director KB is **16.4 GB** and answers every query with nothing.
- **🚨 THE MANDATORY PRIOR-WORK CHECK IS NON-FUNCTIONAL. `CLAUDE.md`'s SESSION STARTUP RITUAL TELLS
  YOU TO RUN IT AS "THE LOAD-BEARING FIRST ACTION". DO NOT TRUST ITS ANSWER.** Measured 2026-08-18,
  both interpreters, twice: `tools/substrate_query.sh` and `tools/director_kb_query.py` **return ZERO
  BYTES and exit 0** after ~38-51 s. Bare `python` resolves fine (3.12.10), so this is NOT the
  venv trap and NOT a hang -- the tool runs, prints nothing, and reports success. **AN EMPTY RESULT
  IS NOT EVIDENCE OF ABSENCE**, and this project has a standing rule that an absence claim requires
  an ENUMERATION. **Every "not a rediscovery" claim made through this tool is unsupported.**
  **DO INSTEAD, and SAY WHICH YOU DID:** `ls notes/ | grep -i <topic>` then READ the hits; `os.walk`
  over `data/` for `metrics.json`, then reconcile to the registry, never the reverse.
  **PROVEN COST:** enumerating by hand on 2026-08-18 found `exp_pc1_predictive_coding_residual_gate_v1`
  (2026-06-22) -- the SAME write-gate mechanism as `e822eeaaf`, uncited in its brief. *It turned out
  to REPLICATE tonight's null on a different substrate and instrument, which is a gain, but it was
  found by hand and not by the tool that exists to find it.* Header of `substrate_query.sh` carries
  the full measurement; a 25 s guard was added there and is marked **UNPROVEN** because its firing
  could not be demonstrated.
- **WRITE-RULE ORGAN, GATE STATE (2026-08-18).** `CODE` **EXONERATED TWICE** (`ac629b1e7` -- a learned
  basis is MATCHED by a same-rank RANDOM basis; nothing moves composition; drill 1's prediction is
  REFUTED). `ACCUMULATE` **GATED = the INTERFERENCE source** (`b6cad69ca`). **The DISSOCIATION
  INSTRUMENT IS LICENSED** (`0eb44eb1d`) -- four floors AT CHANCE and verified there, the first such
  instrument this programme owns; incumbent AUC **0.0710**, single-occurrence **0.4173**, above 0.5
  would mean substitutability. `FILTER` and `SUPERPOSE` are the two steps still UNGATED.
- **ONE AGENT LIVE:** `noncollapse-maxpool` -- the organ's decisive build. Scores MAX-over-occurrences
  vs the incumbent SUM on the licensed dissociation instrument, with `N1_MAXPOOL_RANDOM_OCC` as the
  control that decides whether any gain is the mechanism or merely the max operator. Do NOT edit
  `experiments/` or `hdlab/` while it runs. **It replaces `exp_organ_f_noncollapsing_accumulation_v1`,
  which was KILLED at ~9 h projected runtime (spherical k-means per anchor); that cell is on disk,
  self-tested, and is NOT the current attempt.**
- **THE OVERNIGHT LOOP IS FIXED AND VERIFIED (2026-08-18), after running exactly ONE turn for days.**
  Three defects, all real: the `Stop` hook was registered ONLY in `hd-instrument/.claude/settings.json`
  which is NOT the session's project root, so it never executed (canary silent since 08-13) -- now
  registered in `D:/AI/.claude/settings.json` beside the SessionStart hook that demonstrably fires;
  `_plan_path()` resolved only `PLAN_NEXT_12H.md`/`PLAN.md`, NEITHER OF WHICH EXISTS, so every
  continuation pointed at a missing file; and **GUARD 1 returned on `stop_hook_active`
  unconditionally, so the chain could continue ONCE and the cap of 200 was unreachable by
  construction.** GUARD 1 now continues while ARMED, bounded by the cap AND a 20 s wall-clock floor;
  DISARMED behaviour is unchanged. GUARD 1D narrowed to `permission-rule` + `user-rejected` only
  (owner ruling) -- `cancelled` teardowns are logged, never halt. Self-test OVERALL PASS.
- `.claude/scan-out/` REFUSES FILE CREATION (4x); `notes/ tools/ experiments/ verification/` accept.
  `experiments/exp_propose_reject_retrieval_v1.py` IS A BLOCKED PATH -- OWNER'S CALL, never retry a
  variant.
- NO BACKUP, gitignored: `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB).
  Also gitignored and citation-bearing: `scratch/sparsify_right_object/` (the Q13 sparsity numbers).
- Three `data/cornerstone_results/*/metrics.json` are deleted in the working tree but PRESENT in
  git (`39cc197ff`) -- recoverable, not lost; nobody has decided whether the deletion was intended.
- USER AUTH: `d=256->1024` (rewrites every anchor store; the phase-diagram pass says it is justified
  for the comparison job and NOT for addressing), merge to `origin/main`, any push. Autoloop ARMED
  at 200.
- `hd_director_kb_continuous_ingest` LIVELOCKED (10.65 GB, self-killed at 45 min) while the
  scheduler reports it healthy -- `director_kb_query.py` and `substrate_query.sh` are STALE and
  `substrate_query.sh` currently ERRORS on a locked cache file rather than returning no hits.
- **DATA HAZARD FOUND AND FIXED 2026-08-17 -- THIS ENTRY'S EARLIER WORDING IS SUPERSEDED.** It read
  "`notes/LONG_TERM_PLAN.md` HAS NEVER BEEN COMMITTED", which was true when written. **It is now
  TRACKED, committed unchanged at `0c8d202d7`** (`git log -- notes/LONG_TERM_PLAN.md` returns that
  one commit; the working tree is clean against it at 32,823 B). The hazard is closed; the staleness
  below is not.
- `LONG_TERM_PLAN.md` also stale: sec 2 rows 3/4/6 superseded by STORAGE + C30; sec 4's dual-hub
  `[PINNED]` (line 185) should drop to CONTESTED; its Phase 2 kill banner (line 343) is recorded as
  FIRED without the 8b(B) withdrawal-for-thematic. Director's call, NOT done here (PLAN sec 9).
- OVER CAP AND DELIBERATELY SO, AND THE GAP GREW AGAIN: **19,450 B against the 8,704 cap** (11,571 B
  on 08-16, 15,149 B after the first 08-17 docs pass, this figure after the third). The new growth is
  never-trim class -- five landed results, DO-NOT-REDO 44/45/46 each with a revival criterion, C36 --
  offset only partly by tier trims to PHASE DIAGRAM, BRIDGING and STORAGE. **`STATUS_SPEC.md` sec 7's
  own measurement is now stale by ~7.9 KB and BOTH of its options (raise to 12,288 B; move the stub
  index into an uncapped `STATUS_CLOSED.md`, which was sized to land this file at ~8,580 B) are now
  undersized -- re-measure before enacting either.** Still PROPOSED, NOT ENACTED: DIRECTOR'S CALL.
  Never close the gap by evicting a never-trim entry.
