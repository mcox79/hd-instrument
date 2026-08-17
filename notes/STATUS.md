# STATUS

AS OF: 2026-08-17 | branch `dataprep/mcguffey-graded-corpus` | HEAD `0652e20a5` | GROWTH PAUSED | origin merge needs USER AUTH
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `COMPACTION_HANDOFF_2026-08-17.md` -> HERE -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## POSITION
THE CUE IS NOT EMPTY -- OUR OWN COMPRESSION IS THROWING PART OF THE ANSWER AWAY. On one identical
store/cue/pool/gold (n=3,994; chance 1/5,491 = 0.000182), uncompressed count vectors address the
right item 0.0849 of the time where the live 256-dim projection manages 0.0711: +0.0138
[+0.0083,+0.0195], half-width 0.0056, CI-SEPARATED; exact key 1.0000, random key 0.0003. The
compression is a MEASURED DEFECT, not a suspicion. The READ-OUT ceiling is untouched -- both regimes
still sit below their own floors at hit@1. Verbs now MEASURED at n=222 (C33). C35 is new and
corrects the Director's own handoff.

## TOP ITEM -- THE ADDRESS SIDE IS NOW AN EXPANSION QUESTION WITH A MEASURED TARGET (LESSONS: CUE INFORMATION AUDIT)
`exp_cue_information_audit_v1` (full, `eec21487d`) answered the question that blocked everything and
its stop-if (iii) fired: `U0_UNCOMPRESSED` 0.0849 beats `C0_PROJECTED_256` 0.0711 CI-separated, so
the information IS in the cue and the projection is what loses it. Recoverability of the held-out
sentence reproduced independently on all 3,994 items (max abs error 0.000e+00) plus a store-side
bit-exact encoder identity on 5,491 anchors, so it is no longer an unadopted agent measurement. That
UNBLOCKS the capability half of sparse-address/dense-value (PLAN ITEM 3). TWO CAUTIONS TRAVEL WITH
IT: the absolute level is still ~8%, and the owner's two-part partial cue is only HALF served --
same-meaning words +0.0113 [+0.008,+0.0148] ABOVE, word onset exactly 0.0 [-0.0013,+0.0013]
NOT_SEPARATED, because our only onset channel is a 4-character prefix hashed as one whole symbol.
BOARD question open on whether to build a real one.

## PHASE DIAGRAM -- THERE ISN'T ONE (LESSONS: PHASE DIAGRAM)
`substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md` (`32cc8ce71`) enumerated
the history from the filesystem: 7,804 `metrics.json` (re-walked today: 7,807, the difference being
exactly this session's three new files, nothing missing). Of those, ~59 vary dimensionality, ~21
vary sparsity, 2 vary expansion. Its tally: 23 of 42 parameter-by-operation squares NEVER MEASURED,
13 usable. Six diagrams on six scorers that may NOT be merged. The "55-65% coverage" recollection
traces to `director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`, whose own line items say
dimensionality ~10% and sparsity <5%. The sparsity sweep that Q13 leans on has NO cell under `data/`
-- it lives in gitignored `scratch/sparsify_right_object/` and should be promoted before the next
scratch clear.

## BRIDGING -- TWO MEASURED NULLS (LESSONS: DO-NOT-REDO 38, 43)
Phase 2 FULL: B1 rho 0.0270 n=394 vs floors 0.0412/0.0317/0.0905, NOT_SEPARATED, perm p 0.30, both
known-answer arms ABOVE (K1 0.3301, K2_ORACLE 0.2893); bridged codes KEEP IDENTITY (96.12% distinct)
and LOSE MEANING (retention 0.0819); the curated CSKG arm fails too. SELECTIONAL-CONSTRAINT
BRIDGING, the owner's own mechanism, is the SECOND and worse null: -0.1049 [-0.2041,-0.0057]
CI-separated BELOW the incumbent, -0.0015 NOT_SEPARATED from a random target, retention -0.1224,
instrument alive (K1 0.3311). KILL STATUS: withdrawn for thematic, re-worded for selectional, per
HANDOFF 8b(B) (`exp_cue_regime_one_variable_v1`, full, verdict `..._LAMBDA_STAR_0p60` confirmed on
disk) -- 8b(B)'s numbers were NOT re-verified in this pass.

## STORAGE -- THE WRITE/READ ASYMMETRY IS THE ONE LIVE POSITIVE (LESSONS: WRITE/READ ASYMMETRY)
`exp_sparse_address_dense_value_v1` (n=3994, own floors): best partial-cue addressing anywhere is
0.0719 at a DENSE address; a 1%-occupancy address (82 of 8192 units) read with a DENSE cue matches
it at 0.0699, CIs overlapping; read SYMMETRICALLY it is 0.0483, 1.45x worse; the dense read wins 18
of 24 matched pairs, max 6.27x. Sparse never beats dense outright and the grid sits at or below
0.072 -- the asymmetry is real, the LEVEL is the cap above.

## CLEANUP / SURPRISE / TARGET SPACE (LESSONS: CLEANUP MEMORY, SURPRISE, TARGET SPACE)
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
BELOW the neighbour-copy incumbent and NOT_SEPARATED from a random target*.
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
- ITEM 1 and ITEM 2 both LANDED today (`eec21487d`, `0652e20a5`); the two agents that had stopped
  mid-task were resumed and are done. An agent is building PLAN ITEM 3 in `experiments/` and
  `hdlab/` RIGHT NOW -- do not edit either tree.
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
- **DATA HAZARD FOUND 2026-08-17: `notes/LONG_TERM_PLAN.md` HAS NEVER BEEN COMMITTED.** `git log`
  on the path returns nothing and `.gitignore` does not cover it -- 32,823 B of strategy in a single
  uncommitted copy, exactly the state `PLAN_NEXT_24H.md` was in before it was preserved at
  `da678875c`. **Commit it unchanged before anything edits or supersedes it.** Not done here: it is
  DIRECTOR-OWNED and this pass was told not to touch it.
- `LONG_TERM_PLAN.md` also stale: sec 2 rows 3/4/6 superseded by STORAGE + C30; sec 4's dual-hub
  `[PINNED]` (line 185) should drop to CONTESTED; its Phase 2 kill banner (line 343) is recorded as
  FIRED without the 8b(B) withdrawal-for-thematic. Director's call, NOT done here (PLAN sec 9).
- OVER CAP AND DELIBERATELY SO, AND THE GAP GREW TODAY: **15,135 B against the 8,704 cap** (it was
  11,571 B this morning; `STATUS_SPEC.md` sec 7's measurement is stale by that difference). The
  growth is never-trim class -- C35, discipline 15, the C33 update, three data/agent hazards -- plus
  one new PATH STATE section; tiers 1-4 were applied to the older sections to partly offset it.
  Steps 1-2 are spent; step 3 is RE-MEASURED with TWO OPTIONS in `STATUS_SPEC.md` sec 7 (option 2,
  moving this file's stub index into an uncapped `STATUS_CLOSED.md`, recovers ~3.1 KB and deletes
  nothing) -- DIRECTOR'S CALL, NOT ENACTED HERE. Never close the gap by evicting a never-trim entry.
