# STATUS

AS OF: 2026-08-20 ~74 CONTINUATIONS IN (autoloop `auto_cdc11bb529`), LOOP ARMED | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | **NOTHING IS RUNNING** | **🧭 Q89 AND Q90 BOTH ANSWERED. THE DIRECTION IS DECIDED ON THE OWNER'S BRAIN-FOUNDATIONAL CRITERION: BUILD `ORGAN_MAP` F5 (the coherence monitor / N400 generator), NOT more perceptual norms -- see `## TOP ITEM`** | **6 ABANDONED HUMAN AUDITS SCORED; 4 THEORY DRILLS DONE ON OWNER INSTRUCTION** | **READ `notes/WHAT_2026-08-20_ESTABLISHED_survives_vs_withdrawn.md` FIRST -- it is the flat ledger of what survives vs what I withdrew** | **THE PLAN `notes/BUILD_PLAN_post_audit_2026-08-19.md` CARRIES EVERYTHING -- ITS FIRST BLOCK, THEN `## POSITION` BELOW**
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` (**THE PLAN; READ SEC 6.18 FIRST -- it supersedes the
step hunt. 6.16 holds the PRE-COMMITTED decision branches; 6.15 the five gated steps**) ->
HERE -> `COMPACTION_HANDOFF_2026-08-17.md` -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## MOVED OUT 2026-08-21 -- **NOTHING DELETED, TWO POINTERS**

**This file had grown to 308,692 B against an 8,704 B cap (35x)** by ACCUMULATING session findings
instead of being rewritten in place. **135 sections / 280,747 B were MOVED, not trimmed:**

- **`notes/STATUS_ARCHIVE_2026-08-21_pre_trim.md`** -- byte-identical snapshot of the whole file
  as it stood (sha256 of the copied region verified equal to the source).
- **`notes/STATUS_LESSONS.md`** -- the 135 blocks appended verbatim, with a numbered table of
  contents naming every one.

*The largest single block, 77,131 B (25% of the file), was self-labelled `[ARCHIVED 2026-08-19]
RUNNING / BLOCKED -- STALE, SUPERSEDED BY `## WHAT IS RUNNING`` -- spec sec 3 tier 5, a superseded
finding whose successor is present.*

**`## DO NOT REDO` and `## STANDING DISCIPLINES` below are UNTOUCHED** -- the never-trim sections
were not the growth and were not cut.

**STILL ~3x OVER CAP at ~26.5 KB.** Escalation steps 1 and 2 are now spent; the residue is the five
required sections themselves. **Per spec sec 6 the party that needs the room may not grant it, so
a further cap raise is ESCALATED, not self-authorised.** Filed on the board.

---

## POSITION

> # 📒 **READ THIS ONE FIRST: `notes/WHAT_2026-08-20_ESTABLISHED_survives_vs_withdrawn.md`**
> Today produced **11 findings and 6 retractions of my own claims**, several of them corrections OF
> corrections. The plan, this file and four notes carry those layers **in the order they happened**
> -- the right way to keep a record and the wrong way to read one. **That file is the FLAT version:
> what survives, what is withdrawn, why. Where it and an older note disagree, IT IS LATER.**
> **ONE LINE: the definitional-PHRASE half of the output is genuinely good and clears every floor on
> an independent gold; NOTHING in the substrate reads it; three attempts to change that all failed;
> co-occurrence counting still beats every arm by ~10x.**

### 🧭 **CONSOLIDATED, 2026-08-20. THE PLAN'S TOP BLOCK IS THE FULL VERSION; THIS IS THE SHORT ONE.**
*(`###` deliberately, not `##`: `## POSITION` is machine-parsed and a `##` here TERMINATED the
POSITION section at its own first line, so both `session_start_hook.py` and `board.py` were
mirroring an EMPTY position. See the WHAT IS RUNNING note below -- same defect, same file.)*

**WHAT THE SUBSTRATE IS.** On every properly-controlled test it is AT OR BELOW co-occurrence
counting, and BELOW it on both tests using an INDEPENDENT gold (ConceptNet, no WordNet source):
grounding precision **loses 2-3x to a trivial top-co-occurrent baseline** (p<.02, 3 seeds, precision
**1.6-3.0%**, and on one seed not distinguishable from a RANDOM anchor); discrimination re-ranking
**loses to bag-of-words** on 3 corpora. The synonym-rank TIE is the weakest evidence here -- that
task favours counting BY CONSTRUCTION -- so the independent-gold LOSSES carry the claim.

**WHY, AND IT IS NOT TUNING.** 13 interventions closed across which traces / when / how written /
what a trace is / how transformed. **ZERO role-assignment calls** on the reading path (5 entry
points, runtime-counted). **Consolidation, definitions and foraging are INERT on the read-out** --
ablations demonstrably fire (provenance 68->0) and change no arm to 4 decimals; only `episodic`
moves anything. SR **degrades** with more data, to exactly 0.0 at 40k sentences.

**THE FOUR THINGS THAT WORK:** coverage (`keep_noting_grounded`, 5.0x->2.6x); **combining channels**
(BOTH beats either alone on 3 seeds, median 126->69 -- the owner's own hypothesis, confirmed);
**supplied perceptual norms** beat the learned substrate on 3 seeds (p=.029/.017/.0155, shuffled
control collapses); **dense expository text** grounds 3.4x better (Fisher p=0.002).
**➡️ THREE OF THE FOUR ARE "BRING IN SIGNAL THE TEXT CHANNEL DOES NOT HAVE". NONE IS "COMPUTE THE
SAME THING BETTER".**

**THE SIZED UPSTREAM DEFECT.** The definitional extractor returns a definition for **10.7%** of
definitional sentences; hand-reading 50 drops, **~48% are real definitions we cannot parse**
(multi-word definienda, `which means` clauses, quoted definientia). Ceiling ~46% = **4x supply**.
**But quantity without quality multiplies noise: grounding is 78% noise by blind hand-score.**

**PROCESS FAULTS THAT COST MORE THAN ANY MECHANISM.** 3 tie artifacts in one day -> guard moved into
`tools/rank_with_ties.py`; **7 finished runs invisible for a day** over a missing verdict field ->
display fixed, verdicts in `notes/verdicts_for_the_seven_unread_runs_2026-08-19.md`; the prior-work
tool returned **silent zeros** for multi-word queries -> fixed + self-tested; **4 times** a point
estimate would have produced a false positive where the paired statistic said no.
**Two of the day's best results were already on disk, unread. The archive out-performed the runs.**


## TOP ITEM -- 🧭 **THE DIRECTION IS DECIDED: BUILD F5. AND KEEP TWO ANGLES LIVE AT ALL TIMES.**

> **📌 OWNER, 2026-08-20T21:59Z: *"Make sure you always have 2 high priority angles you can work on
> while you're waiting on results."*** **This is a STANDING RULE about how to work, and it was
> aimed at a real failure: I had spent several turns concluding "nothing further I can responsibly
> open" while a build sat blocked on cell-authoring.** *"Blocked on one thing" is never a stopping
> state -- it is a signal that the second angle was never lined up.*
>
> ### 🅰️ ANGLE A -- **SPECIFY THE F5 EVALUATION TASK** (pure judgement, no cell needed)
> The build cannot be judged without a scorable, **can-fail** task, and **every organ that failed
> tonight failed partly on a badly-posed task**: a retrieval metric that rewarded topical
> narrowness; a floor propped by an uncontrolled covariate; a gate that could never fire. **Posing
> the task well BEFORE the build is the highest-leverage work available.** Needs: the
> discriminator, the floors that will actually be RUN, the positive control, and the can-fail
> condition -- written down before anyone codes.
>
> **✅ ANGLE A DONE:** `notes/F5_EVALUATION_DESIGN_how_we_would_know_a_coherence_monitor_works_2026-08-20.md`
> -- task (**detect the anomalous word**, the N400 read-out), the confound that would ruin it
> (**anomalous words are RARE words -> the swap must be FREQUENCY-MATCHED**), the six floors that
> must actually be RUN (**co-occurrence surprisal is the one that decides it**), the four
> diagnostics that must print before any verdict, and the pre-committed can-fail condition.
> **Explicitly NOT a target: beating the 40-50% human miss rate -- an always-on checker beats an
> inattentive reader trivially.**
>
> **✅ ANGLE B DONE -- ANSWERED NEGATIVE:** the graded read-out banks **MORE OF THE SAME, NOT
> BETTER**. Of 600 terms, 40 are banked only by the graded query; hand-scoring 26 gives
> **1 MEANINGFUL / 9 RELATED / 16 NOISE = 3.8%** -- indistinguishable from the 0-4% already
> produced, and every addition sits at **cos 0.45-0.60**, just over the bar. **DO NOT SHIP THE
> GRADED-QUERY CHANGE AS A QUALITY FIX.** *The fidelity charge still stands; a gap can be real and
> consequential AND fixing it in one place can still not help.*
>
> **✅ ANGLE B (2nd) DONE:** `notes/ANGLE_B_the_meaning_consumption_link_designed_the_meaning_is_the_PREDICTION_2026-08-20.md`
> **WHICH:** the DEFINITIONAL half only (**32% MEANINGFUL vs 4%** -- feeding the bad half makes the
> system expect nonsense, and a system expecting nonsense is surprised by everything). **WHERE:** a
> dedicated `MEANING` role via the live `bind_filler`. **WHEN -- the load-bearing answer: the banked
> meaning must supply the PREDICTION, not sit in the register.** Predicted-from-meaning vs
> observed-from-context; the gap IS `‖Δ situation_model‖`. **A wrong meaning then costs the system
> something, which is the selection pressure it has never had.**
> *Falsifiable corollary worth checking cheaply: accumulated error per term would be a GOLD-FREE
> quality estimate for banked facts -- testable against tonight's several hundred hand-scores.*
>
> ### 🅰️ **NEW ANGLE A -- BUILD THE FREQUENCY-MATCHED ANOMALY SET**
> The F5 evaluation needs items where the anomalous word is matched to the coherent word it replaces
> on **frequency, length, POS and position** -- otherwise the test rewards "flag the rare word" and
> measures vocabulary statistics in a comprehension costume. **Constructible inline from existing
> corpora; no cell, no agent.** It is the concrete prerequisite for the build.

## WHAT IS RUNNING

- **🔴 NOTHING IS RUNNING** (both replication batches landed; verified against the process table
  when the last one exited).
- **✅ LANDED: seeds 101/13 of `experiments/analysis_definition_indexed_retrieval_v1.py`.**
  **THE DOWNGRADED CLAIM IS RESTORED ON EVIDENCE:** `DEFINIENS - PROFILE` = **+28.0 / +19.5 /
  +28.5**, gate **`REPLICATED`** (3/3 same sign, 1.5x spread). `SHUFFLE_DEF` is worse than
  `DEFINIENS` on all three, so the definiens IS term-specific -- just worse than the profile.
  **AND A THIRD SIGN-FLIP ON COMBINING: `BOTH - PROFILE` = +7.0 / -8.0 / +6.5, gate
  `INCONSISTENT_SIGN`** -- three separate datasets now agree that combining is inconsistent across
  seeds, independently confirming that NEITHER of my opposing boundary claims held.
- *(the launch record for those seeds, kept because recording at launch time is the discipline:)*
  **WHY: MY OWN NEW GATE DOWNGRADED ONE OF MY OWN KEPT CLAIMS.** Running
  `tools/replication_gate.py` over the ledger's surviving items returned
  **`SINGLE_SEED_HYPOTHESIS`** for *"indexing by the raw definiens text is 28 ranks worse"* -- filed
  under SURVIVES on seed 7 alone. *A guard I exempt my own favourites from is not a guard.*
  **The other kept claims cleared it:** phrase-vs-floor `REPLICATED` (4/4 same sign, 1.2x spread,
  no control within half); looked-up-definition-is-worse `REPLICATED` (3/3, 2.1x).
  **SEED 101 IS IN AND THE DOWNGRADED CLAIM IS HOLDING:** `DEFINIENS` is worse than `PROFILE` on
  both seeds (**+28.0, +19.5**), same sign, 1.4x spread. Seed 13 pending before the verdict string
  goes in the ledger.
  **🔎 AND A THIRD INDEPENDENT SIGN-FLIP ON THE COMBINING QUESTION: `BOTH` reads +7.0 (WORSE) on
  seed 7 and -8.0 (BETTER) on seed 101.** That is now the third dataset showing combining behaves
  inconsistently across seeds -- **further confirming that NEITHER of my two opposing boundary
  claims was ever established**, and that the honest position is the one already in the ledger.
- *(earlier in-flight entries, now landed, kept for the launch-time-recording discipline:)*
  - **phrase-floor seed replication, seed 29** (`scratch/phrase_floor_feasibility.py`).
    **SEEDS 7 / 101 / 13 ARE IN AND REPLICATE TIGHTLY: OURS 19.4 / 18.9 / 20.3%, strongest floor
    7.5 / 7.4 / 8.2%, SHUFFLE 0.0% on all three.**
  - **the HARDER floor, seed 7** (`tools/score_phrase_output_against_conceptnet_hypernyms.py`).
    Adds **`CO_SPAN`** -- a CONTIGUOUS same-length window from the SAME sentence. `CO_SENTENCE`
    samples words INDEPENDENTLY, which destroys syntax, so it may be beaten by mere phrase-hood
    rather than by definitional-ness. Also adds the **ORACLE** ceiling and a **treatment-overlap**
    column, because our definiens IS a contiguous window of that sentence and on a short sentence
    a random window can largely BE it -- **a floor that contains the treatment is not a floor, and
    failing to clear it would be a FALSE NEGATIVE, not a result.**
- *(Before that launch: nothing was running -- verified 2026-08-20 against the live process table,
  only the status GUI, shim PID 8900 / child 28648. Not inferred from a log or a PID file.)*
- **🚨 THIS SECTION WAS CONFIDENTLY WRONG FOR A FULL DAY, AND IT IS THE ONE `session_start_hook.py`
  INJECTS INTO EVERY COMPACTION RECOVERY.** The parsed copy sat at **line ~2535 under 2,300 lines of
  archive**, said *"26 continuations in"*, and named two runs as in flight that had **finished the
  previous afternoon** -- while the `AS OF:` line at the top of the SAME FILE named two *different*
  runs. **A stale WHAT IS RUNNING is worse than an empty one; that exact sentence was already
  written in the stale section, by someone who had just been burned by it.**
  **THE STRUCTURAL CAUSE, NOW FIXED: both `session_start_hook.py` and `board.py` take the FIRST
  line-start match, and the current sections had been buried under the archive.** They now sit at
  the top; the archived copies below are renamed so exactly one of each literal is parsed.
- **✅ COMPLETED 2026-08-19, both with positive evidence in their logs, neither previously recorded
  here:**
  - **9-seed spoke independence sweep** (`scratch/spoke9.log`) -- **PRE-REGISTERED CONJUNCTION
    (ratio>=0.85 AND union>=1.5 on EVERY seed): FAILS** -- 3 of 9 seeds fall under the ratio bar
    (union clears on 9 of 9). **BUT DO NOT READ THAT AS "THE ENCOURAGING SEED WAS AN OUTLIER".**
    The log poses that as a CONDITIONAL and the data takes the other branch: **ratio mean 0.87,
    median 0.91, sd 0.09, min 0.70, and 6 of 9 seeds clear 0.85.** The 0.70 is the extreme, not the
    0.94. **The honest verdict is: the pre-registered all-seeds bar FAILS and the effect is
    BORDERLINE-AT-INDEPENDENCE, not refuted.**
    *🚨 I first wrote "the single encouraging seed was the outlier" here, having copied the log's
    conditional prose without checking which branch its own numbers took. Caught by reading the
    table. That is the house error -- a narrative sentence sitting next to the data that contradicts
    it -- and it survived into this file for one edit.*
  - **`exp_predictive_write_gate_v1`** (`scratch/pwg_full.log`) -- `[done] 3 units in 1064s`.
    **ACC hit@10 0.1533 vs COOC hit@10 0.3667** (seed 7); 0.1667 vs 0.3933 (seed 101). **Accumulation
    loses to co-occurrence counting again**, consistent with everything else measured this week.
- **🔎 THE MACHINE ALREADY KNEW, AND THE WARNING WAS BEING READ PAST EVERY SESSION.** The hook's own
  `[pid-reconcile]` block prints **"4 RECENT RUN(S) DEAD WITHOUT FINISHING <-- do not describe these
  as live"**, naming `spoke9`, `onemany` and `cn_gold` as `DEAD_BUT_CLAIMED_LIVE`. It was correct
  about LIVENESS and was ignored while this file said the opposite two lines further up.
  **⚠️ BUT IT IS NOT RELIABLE ABOUT COMPLETION: it classifies `spoke9` as dead WITHOUT FINISHING,
  and that run demonstrably finished** -- all 9 seeds, summary statistics and its pre-registered
  verdict are in the log. It appears to infer "unfinished" from a missing `metrics.json`, which a
  scratch-script run never writes. **DEAD != UNFINISHED; the reconciler conflates them, so use it
  for liveness and read the log for completion.**
- **⚠️ FILE HEALTH: this file is ~272 KB / 3,373 lines against a stated cap of 8,704 B -- 31x over.**
  `STATUS_SPEC.md` sec 2 requires the state half to be REWRITTEN IN PLACE and the never-trim half to
  live in `STATUS_LESSONS.md`. It has instead become an append log. **NOT trimmed here on purpose:**
  the spec's own sec 8 records that an ad-hoc byte-shave deleted a discipline that had cost two full
  experiments to learn. A trim is a deliberate job against the spec, not a side-effect of a status
  update.

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
