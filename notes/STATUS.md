# STATUS -- THE RECOVERY ENTRY POINT. READ THIS, THEN THE PLAN.

AS OF: 2026-08-21 ~150 CONTINUATIONS IN (autoloop `auto_cdc11bb529`), LOOP ARMED | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | **TWO DETACHED DIAGNOSTICS LIVE (see `## WHAT IS RUNNING`)** | **BOTH BOARD QUESTIONS ANSWERED (Q92 cap raise + archiving; Q95 brain-foundational criterion)** | 🔴 **TOP ITEM CHANGED: THE OVERNIGHT PLAN'S FOUR THRUSTS WERE *ALL FOUR* ALREADY ANSWERED ON DISK -- found by READING, none by running, one command each. The defect was ORDER: I wrote the plan before running the three prior-work reads, then ran them per-thrust afterwards. RUN THEM BEFORE RANKING CANDIDATES, NOT AFTER COMMITTING.** | **THE PLAN `notes/BUILD_PLAN_post_audit_2026-08-19.md` FIRST BLOCK, THEN `notes/OVERNIGHT_PLAN_2026-08-21.md`, THEN `## POSITION` BELOW**

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
`## TOP ITEM -- **IT WAS SOLVED 8 DAYS AGO AND RANKED #1. WIRE DEFINITIONAL DIRECT-BANK.**

**Owner, 2026-08-21: *"i think this reading and grounding thing was figured out a while ago - but you
clearly didn't pick up on that."*** **They are right.** `notes/opportunity_map_2026-08-13.md` item
**#1**, verbatim:

> *"The extractor that reads 'X is a Y' out of real textbook prose currently runs only inside
> experiment cells. Its facts are written to files that nothing live re-reads. **Wiring it means the
> reading loop banks those facts into the foundation directly, at the moment of reading, WITHOUT
> ASKING THE BROKEN COMPARATOR TO CHOOSE ANYTHING.**"*

**Evidence already on record: 64% MEANINGFUL (32/50) against an 8% floor**, same scorer, same rubric,
same sampling, **pre-registered HARD_PASS band >=52%.** Ladder **v2 8% -> v3 38% -> v4 40% -> v5
64%**. `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`, **2,092
rows**. The brain-fidelity audit called that metric *"the best in the repository... the only place
where the thing being measured is the thing the brain is judged on."*

### 🚫 **AND I MUST CORRECT MY OWN HEADLINE FROM ONE TURN AGO: "READING GROUNDS ZERO" WAS WRONG.**
I measured `n_grounded`, which is **the comparator gate only** -- and that gate is precisely the
thing the 08-13 note says to BYPASS. **Reading DOES produce meanings.** 600 sentences of biology
gives **15 consolidated entries**, provenance **3 `DEFINITIONAL_EXTRACTION` / 12 none**:

| source | examples |
|---|---|
| **DEFINITIONAL** | **`hypothesis -> a suggested explanation that one can test`**, `biology -> a science` |
| none (distributional) | `brain -> people`, `create -> book`, `critical -> number` |

**That is the SAME split I spent today rediscovering at 32% vs 4% -- and it was already measured at
64% vs 8%, with the fix specified and ranked #1, eight days ago.**

### 🎯 THE ACTUAL TOP ITEM
**Wire the definitional channel to bank DIRECTLY at read time, bypassing `canonicalize`.** *The
deadlock I described -- grounding needs anchors, anchors need grounding -- is a real property of the
COMPARATOR path, and it is exactly why the fix is to not route through it.*
`notes/opportunity_map_2026-08-13.md` (item #1), `notes/director_handscore_b3_v5_termboundary_2026-08-12.md`

## 🌙 THE NIGHT OF 2026-08-21 -- FINDINGS, ALL FROM READING ARTIFACTS THAT ALREADY EXISTED

**Full notes named; do not re-derive.**

| # | finding |
|---|---|
| **META** | **All 4 planned thrusts were already answered on disk.** T1 organ exists+PINNED+run; T2 `HARD_FAIL` on the exact test; T3 switches already default-ON (a landed cell carries a `premise_correction` field recording a PRIOR dispatch making the identical mistake); T5 already measured. **`organ_map_cite.py` answered two in its FIRST LINE.** The defect was ORDER, not omission. [`T2_superseded_and_the_NIGHT_S_META_FINDING...`] |
| **H2** | The organ built to break a **64.5% biology skew read its way to `dominant_domain=textbook_biology 0.63245`** -- free choice over 36 corpora, 19 visited -- **while WINNING on its own currency** (gain 6.96 vs 5.90). **MVT is a LEAVE rule, silent on WHERE TO GO**; patch-CHOICE is the UNPINNED half. **Breadth was never in the currency.** *Register-inversion headline WITHDRAWN: a 7.6x register bias sits under a 1.2x margin, so the coverage comparison supports nothing either way.* [`T1_foraging_...`] |
| **E3** | **Our coreference "salience" is PROVABLY a mention-count.** `count + 0.5*exp(-0.1*d)`: bonus capped at 0.5, counts are integers, so **a one-mention lead can never be overturned**. The cell measured `D2_salience_equals_argmax_count_fraction = 1.0` on all 89 competitive decisions; its verdict never said so. **`base_principle_b` (0.7191) did not beat a cue-integration account -- it beat a counter.** We implement **none** of the brain's top three cues. [`T2c_...`] |
| **E3b** | That `HARD_FAIL` **cannot support its own verdict**: n=89 (CI 0.22 wide), **scramble control ABOVE the treatment** (0.5938 vs 0.5843, different subset -> unusable either way), **2 of 3 params hand-set with the sweep still CLIMBING at its boundary**. Re-label **UNDERPOWERED**. [`T2b_...`] |
| **B4** | **Pure spelling beats the meaning read-out at rank 1 and SURVIVES the strictest tie convention** (0.0767 vs 0.0480; substrate arm has **0.0% ties** -- no defence available). **BUT the "identical median rank 37.0" WAS the artifact** -- honestly scored, the substrate WINS the full ranking **37.0 vs 54.0**. **➡️ THE DEFECT IS PRECISION AT THE TOP, NOT COVERAGE.** *`A8_MAXORTHO`, documented as "the strongest zero-meaning attack", is a z-SUM 30% BELOW its own component; the true floor is `A6`.* [`T5b_...`] |
| **B4b** | **The live grounding path reads a GRADED field with a SIGN-QUANTISED query** -- `canonicalize:776` hardcodes `np.sign`, `canonicalize_fast` honours the switch, and **the grounding call sites use the one that cannot**. `:663` calls that pairing *"worse than either"*. **Under test now.** [`T3_...`] |

## WHAT IS RUNNING

- 🟢 **TWO DETACHED DIAGNOSTICS ARE LIVE** (this session; `Start-Process`, survive the session):
  - `tools/diagnose_read_with_loaded_foundation.py` -> `scratch/t4_decisive_out.log` (shim PID in
    `scratch/t4_decisive.pid`). **Healthy but SILENT: its prints lack `flush=True`, so redirected
    stdout is block-buffered and dumps only at exit.** Judge it by the CHILD process, never the
    shim: CPU advanced 937s -> 1720s. *It re-runs the "decisive test" whose original double null
    (`GROUNDED(last)=0`) was TWO probe bugs -- corpus exhausted (3x1200 requested, 1540 read =
    1200+340+0) so the count came off a read that processed no text, and only the LAST of three
    calls was reported.*
  - `tools/graded_vs_signed_query_v1.py` -> `scratch/gvs_out.log`. **Tests T5b's prediction:
    restoring the magnitude `:776` discards should move hit@1 SPECIFICALLY and leave median rank
    roughly alone.** Refuses to report unless `Q_GRADED` reproduces the landed C3 headline 0.0480.
- **DONE, one command each, all from READING:** `tools/orthographic_floor_tie_mass_v1.py` (621 s).
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
