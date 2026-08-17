# STATUS

AS OF: 2026-08-17 | branch `dataprep/mcguffey-graded-corpus` | HEAD `30cc1fd8a` | GROWTH PAUSED | origin merge needs USER AUTH
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `COMPACTION_HANDOFF_2026-08-17.md` -> HERE -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## POSITION
THE CUE SIDE IS FINISHED AND IT DID NOT FIX THE READING; THE WRITE RULE IS THE ONLY ROAD LEFT AND IT
IS THE FIRST ONE THAT HAS EVER MOVED. Plainly: we spent four cells changing the QUESTION we hand the
store (compress it, don't, keep only presence, sparsify the address, sparsify the cue, settle it) and
one cell changing WHAT IS STORED. Everything on the question side improved FINDING THE RIGHT DRAWER
and nothing improved READING WHAT IS IN IT. Best cue-side result: binarising the cue takes addressing
0.0711 -> 0.1094 (+0.0383 [+0.0295,+0.0473]) while hit@1 moves 0.0223 -> 0.0249, +0.0026
[-0.0026,+0.0078] NOT_SEPARATED -- ADDRESSING AND READ-OUT ARE SEPARATELY CAPPED (stop-if fired).
The one write-side arm moved hit@1 0.0223 -> 0.0298, +0.0075 [+0.0023,+0.0128] ABOVE, with the
frequency-matched and random-profile controls both failing to reproduce it. It is still 2.9x short of
its own floor. Verbs MEASURED at n=222 (C33); C35/C36 correct this project's own prior docs.

## TOP ITEM -- THE WRITE RULE IS THE FIRST THING IN THE PROGRAMME TO MOVE READ-OUT (LESSONS: WRITE RULE)
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
a bare number, baseline STANDALONE, every floor recomputed on the item's OWN population.
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

## WHAT IS RUNNING / BLOCKED
- **ALL THREE PLAN ITEMS ARE NOW DONE.** ITEM 1 `eec21487d`, ITEM 2 `0652e20a5`, ITEM 3 `2e5a467ae`
  (a clean null). Four more cells landed after them: `201776cc9` (compression diagnosis),
  `a8fdc968f`/`24ca42661` (the write rule), `1e085d761` (binarised read-out transfer). The
  08-16 22:41 basin cell has now been READ, twice and independently.
- **TWO AGENTS ARE LIVE AS OF THIS PASS:** one authoring a 2x2 write-rule composition in
  `experiments/` (do not edit `experiments/` or `hdlab/`), one writing
  `notes/verb_representation_*` (`30cc1fd8a` is its first landing -- do not edit that file).
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
