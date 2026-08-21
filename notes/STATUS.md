# STATUS -- THE RECOVERY ENTRY POINT. READ THIS, THEN THE PLAN.

AS OF: 2026-08-21 ~133 CONTINUATIONS IN (autoloop `auto_cdc11bb529`), LOOP ARMED | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | **NOTHING IS RUNNING** | **BOTH BOARD QUESTIONS ANSWERED (Q92 cap raise + archiving; Q95 brain-foundational criterion)** | **TOP ITEM: 36 of 150 modules run when it reads; 81 are built, blessed WIRE, and never called -- that is the backlog, and it is a WIRING backlog** | **THE PLAN `notes/BUILD_PLAN_post_audit_2026-08-19.md` FIRST BLOCK, THEN `## POSITION` BELOW**

Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). FOUR literals
MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `### 2026-08-21 -- THE THREE-WAY COMPARISON THAT DECIDES WHAT F5 BUILDS ON

| arm, paired hit@1 discrimination, 4 sets | median | verdict |
|---|---|---|
| untrained codebook (nothing read) | **~0** | CIs span zero -- donates nothing |
| **THE TRAINED SUBSTRATE** | **+16.3 pp** | **`REPLICATED`, all 4 CIs exclude zero** |
| second-order counting (**the bar**, upper bound **+44.2**) | +29.4 pp | `REPLICATED` |

**LEARNING BOUGHT SOMETHING REAL** -- 0 -> +16.3 pp, same representation and comparison, the only
difference being 7,535 sentences read. First replicated positive from our side on this task.
**AND IT DOES NOT CLEAR THE BAR** (best CI +30.8 vs gate +44.2), reproducing the standing position
*at or below counting* on a task that did not exist when that position was formed.
**AND THE PAIRED TEST NOW SAYS WE ARE MEASURABLY BEHIND, not merely not-ahead:
`SUBSTRATE - COUNTING = -0.142 per item over 478 items, 95% CI [-0.203, -0.082]`, SEPARATED.**
Marginal CIs overlapped, which is NOT a test of a difference; the paired test is. `notes/THE_TRAINED_SUBSTRATE_SCORES_16pp_...md`

"TOP ITEM" and "WHAT IS RUNNING" (`session_start_hook.py`, `board.py`).
**Inside a section use `###`, never `##`.** *And NEVER let a line BEGIN with one of those literals
even when merely NAMING it: on 2026-08-21 this very sentence wrapped so that a line started with
`## TOP ITEM -- **36 OF 150 MODULES RUN WHEN IT READS. 81 ARE BUILT, BLESSED `WIRE`, AND NEVER CALLED.**

**Owner asked: *"Why did we stop working on reading? Where are we on the different functions of
substrate?"*** Measured, not recalled (`tools/substrate_function_status.py`, runtime + disk
enumeration, because the registry's `pipeline_status` is documented wrong in BOTH directions).

| | |
|---|---|
| modules on disk | **150** |
| registered | **150** (was *"62 of 141 unregistered"* -- **that figure is stale, it is now 0**) |
| **loaded by a LIVE read** | **36** (`CLAUDE.md`'s *"35 of 141"* held up almost exactly) |
| **`gate=WIRE` but NOT loaded by a live read** | **81** |

### 🚨 **THAT 81 IS PROBABLY THE ANSWER TO "WHY DID READING STALL".**
*Reading is not unbuilt -- the loop is a real ~36-part pipeline (`reading_grounding_loop`,
`grounding_acquisition_loop`, `definitional_extraction`, `coreference_resolver`,
`situation_model_accumulate`, `hd_fact_store`, `information_foraging`, `hippocampal_encoder`, ...).*
**It stalled because two thirds of what we built sits BESIDE the loop rather than inside it.**

**Islanded and directly relevant:** `prelim_tier` + `three_tier_loop` (**the owner's cold storage AND
the hierarchical-memory idea they proposed -- proven, 3 HARD_PASS**), `successor_representation`
(D7, fully pinned), `situation_model_multibank`, `pos_tagger`/`arc_parser`/`semantic_parser`,
`modern_hopfield_readout`, `streaming_attention`, `learning`, `word_learning_tool`,
`sensorimotor_spoke` (**the one route measured NOT subsumed by counting**).

### ⚠️ **SCOPE:** *"not loaded by a live read"* does **NOT** mean dead -- a module may serve query or
consolidation. It means the READING path does not touch it, which is the question that was asked.
### 🎯 **THE BACKLOG IS A WIRING BACKLOG, NOT A BUILD ONE.** But 81 assumptions would be 81 chances to
repeat today's pattern of proposing before measuring: **each needs a measured target, per
WIRE-or-SHELVE.** `notes/WHERE_THE_SUBSTRATE_FUNCTIONS_STAND_36_of_150_run_when_it_reads_2026-08-21.md`

## WHAT IS RUNNING

- **NOTHING IS RUNNING.** No cells, no agents, no detached processes spawned by this session.
- **BOARD Q92 AND Q95 ARE OPEN** (Q91->Q92 superseded on new arithmetic; Q93->Q94->Q95 on a
  reversed recommendation and then a fact I had not CI-checked). Q92: this file is ~2.3x its
  8,704 B cap after the 2026-08-21 trim. Escalation
  steps 1-2 are spent. **Per `STATUS_SPEC.md` sec 6 the agent that needs the room may NOT raise the
  cap; do not self-approve it.** The session-start hook now REPORTS the size every session
  (`STATUS_CAP_BYTES` in `session_start_hook.py` mirrors the spec -- change both together).
- **HAZARD: `data/foundation/` is READ-ONLY, ~63 MB, ONE DISK, NO BACKUP, gitignored.**
- **GATES: origin push needs in-session USER AUTH. Never `git add -A` on the canonical store.**
  **Never bundle a deletion (`rm`/`Remove-Item`) with real work in one call.**
  **Never edit `preregs/**` or any `arm_key*` file.**
- **2026-08-21 landed:** anomaly set + hand-scores; the F5 bar measured and replicated; the cell
  flagger tightened 13 -> 1 with its survivor examined and cleared
  (`_tie_mass_examination_2026-08-21.json`); this file trimmed 308,692 -> ~20 KB with **nothing
  deleted**; the hook size guard. All committed.

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
