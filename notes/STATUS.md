# STATUS

AS OF: 2026-08-17 | branch `dataprep/mcguffey-graded-corpus` | HEAD `daad41b48` | GROWTH PAUSED | origin merge needs USER AUTH
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `COMPACTION_HANDOFF_2026-08-17.md` -> HERE -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## POSITION
THE PARTIAL CUE IS STRUCTURALLY CAPPED AND A CHEATING ORACLE PROVES IT. Across 47 foundations
(KA 0.9807-1.0000, 47/47) a circular WordNet oracle reads 0.8787 at the exact key and 0.0365 under
the partial cue -- the best partial-cue reading in the entire grid. Purity predicts retrieval at
rho 0.961 exact-key, -0.0167 partial. Read-out still below its spelling floor (4.80% vs 8.70%).
THREE claims RETRACTED tonight (C32-C34), all ONE error: AN UNDERPOWERED NULL READ AS A CAPABILITY
STATEMENT.

## TOP ITEM -- DIAGNOSE THE PARTIAL-CUE CAP (LESSONS: PARTIAL-CUE CAP)
Nothing downstream is worth building first. An oracle allowed to cheat cannot beat 0.0365; a
two-stage cue moves 0.0225 -> 0.0322 and no further. The cue's cosine to its OWN stored row is
0.1621 while the same pipeline addresses 1.0000 exact / 0.0325 partial
(`exp_cue_to_store_translation_v1`) -- the address stage never gets close enough for the key to
matter. FIRST QUESTION, an INFORMATION AUDIT of our own encoder and not a mechanism claim: IS THE
ANSWER IN THE CUE AT ALL? Uncompressed count vectors vs the live 256-d projection, one variable,
identical store/pool/gold. If uncompressed also lands near chance the blocker relocates upstream to
WHAT WE WRITE -- a GOOD outcome. Design/floors/stop-if: `PLAN_NEXT_24H.md` ITEM 1.

## BRIDGING -- TWO MEASURED NULLS NOW (LESSONS: DO-NOT-REDO 38, 43)
Phase 2 FULL: B1 rho 0.0270 n=394 vs floors 0.0412/0.0317/0.0905 on the identical stratum,
NOT_SEPARATED, perm p 0.30, BOTH known-answer arms ABOVE (K1 0.3301, K2_ORACLE 0.2893); bridged
codes KEEP IDENTITY (96.12% distinct) and LOSE MEANING (retention 0.0819); the external curated
CSKG arm fails too. SELECTIONAL-CONSTRAINT BRIDGING -- the owner's own mechanism, built to beat
neighbour-copying -- LANDED as the SECOND null and a worse one: head-to-head -0.1049
[-0.2041,-0.0057] CI-separated BELOW the incumbent, -0.0015 NOT_SEPARATED from a random target,
retention -0.1224, instrument alive (K1 0.3311). Read at mtime 08-17T00:32; re-check it.

## STORAGE -- THE WRITE/READ ASYMMETRY IS THE ONE LIVE POSITIVE (LESSONS: WRITE/READ ASYMMETRY)
`exp_sparse_address_dense_value_v1` (n=3994, own floors, imports nothing): best partial-cue
addressing anywhere is 0.0719 at a DENSE address; a 1%-occupancy address (82 of 8192 units) READ
WITH A DENSE CUE matches it at 0.0699, CIs overlapping; the same config read SYMMETRICALLY is
0.0483, 1.45x worse; the dense read wins 18 of 24 matched pairs, max 6.27x. Sparse never beats dense
outright and the whole grid sits at or below 0.072 -- the asymmetry is real, the LEVEL is the cap
above. The owner's PER-ORGAN regime ruling as a measured effect.

## CLEANUP / SURPRISE / TARGET SPACE (LESSONS: CLEANUP MEMORY, SURPRISE, TARGET SPACE)
CLEANUP MEMORY IS REAL, NOT INERT (fixed points 1.0000, idempotent, capacity on VSA's own d/log d
scale): first measured cleanup lift, +0.0033 and +0.0078 CI-separated in 2 of 3 pools, every arm
still -0.1135 BELOW the binding constant floor. IT MAKES THE FIVE BANKED CLEANUP NULLS STRONGER --
the load-bearing half was NOT missing. SURPRISE-WEIGHTING: clean null, named cause -- signal
DEGENERATE (median 0.875 where 1.0 is orthogonal), selection beats a token-matched random subset in
4 of 18 comparisons, residual rule a near-no-op (cos 0.9771 to uniform) = the PRE-REGISTERED
bootstrapping problem. TARGET SPACE: affect +0.1013 is a CEILING DIAGNOSTIC, no floors, no null,
clears nothing; its verb half is SUSPENDED (C33).

## TOOLING STATE (LESSONS: VERDICT BAR, SKIPPED FULLS, C31, C32)
Corrected base rate: 7,789 enumerated, MEETS_BAR **1** (`exp_cue_to_store_translation_v1`), FAILS
7,770, NO_EVIDENCE 18; NO_FLOOR 2,967, SATURATED_CEILING 265, NO_CONSTANT_FLOOR 39; 238 flagged
cells ARE cited by an index -- OPEN OPERATOR DECISION, NOT TAKEN. The one pass is rejected on four
grounds (pool admits a fitted constant 0.7354 vs chance 0.0625; exact-key is not the operating
point; the cell declines a verdict; margin overstated 4.20x). `verdict_bar_check.py` HAS FALSE-PASSED
FOUR TIMES (enumerated in the 08-17 handoff) -- run it, NEVER rely on its verdict, state arm-by-arm
margins. Only 12 of 7,789 cells ever recorded a constant floor, so every historical bar decision
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
76.18% of SimLex on two values, NO revival; **43 SELECTIONAL-CONSTRAINT bridging -- CI-separated
BELOW the neighbour-copy incumbent and NOT_SEPARATED from a random target*.**
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
**C32 "0 of 7,769 meet the bar" -> 1 of 7,789, and that survivor is itself rejected; C33 "our
instrument cannot resolve verbs even when handed the answer" SUSPENDED -- n=86, floor 0.1776 = the
null width 1.645/sqrt(85); C34 "the constant floor is the binding one" FALSE in general -- it is
-0.1959 on the bridging stratum and -0.2253 on the selectional one, the WEAKEST member of the four.**

## STANDING DISCIPLINES -- NEVER-TRIM -- LESSONS
1 NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% -- cost TWO experiments, the
2nd claiming to have FIXED the 1st; gate on KNOWN-ANSWER RECALL. 2 SERIALIZE MEASUREMENT vs CODE
CHANGE (2x). 3 A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night; C31 = 5th).
4 ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM (6x); AN ABSENCE CLAIM REQUIRES
AN ENUMERATION, NOT A SEARCH -- state HOW. 5 BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS
THE OPERATION IT SCORES. 6 RUN A POSITIVE / KNOWN-ANSWER ARM (2x): a FLOOR says whether the EFFECT
is real, a KNOWN-ANSWER arm whether the INSTRUMENT is -- run both. 7 NO DEMOTION WITHOUT A FRESH
ON-DISK RE-CHECK -- ~11 wrongly demoted, 17 corrections-of-a-correction in 48h; keep
EXISTS/IS-REACHED/IS-GOOD separate. 8 A GATE IS A CI-SEPARATED MARGIN ABOVE max(ORTHOGRAPHIC,
FREQUENCY, SCRAMBLE, CONSTANT) on the IDENTICAL scorer/n/pool/gold -- never a bare number, baseline
STANDALONE, every floor recomputed on the item's OWN population. 9 DETECTORS FIRE ON HONESTY (49/49
flagged were false positives). 10 SILENT JOINS FABRICATE GREEN AND RED -- ASSERT+COUNT joined rows.
11 A NUMBER MAY NOT BE CARRIED BETWEEN SCORERS OR POPULATIONS -- cost 3x in one night (C28/C29/C30);
name the scorer, n, pool and gold for BOTH sides or you have no comparison. 12 A CLAIM MEASURED AT
THE EXACT-KEY OPERATING POINT DOES NOT TRANSFER TO THE PARTIAL-CUE REGIME, WHICH IS THE REAL ONE --
top-50 0.5566 exact vs 0.3758 partial; state the cue regime beside every retrieval number.
13 REPORT TIE CONVENTIONS BOTH WAYS, NEVER SILENTLY PICK THE FLATTERING ONE -- +0.0105 NOT_SEP flips
to +0.0641 ABOVE on tie mass alone. **14 REPORT THE CI HALF-WIDTH AND THE NULL p95 AT THAT n BESIDE
EVERY MARGIN -- A WIDTH IS NOT AN EFFECT. Cost 3x in one night (C32/C33/C34), each an UNDERPOWERED
NULL read as a CAPABILITY STATEMENT; at n=86 the "floor" WAS the null distribution's own spread.**

## WHAT IS RUNNING / BLOCKED
- No `.pid` file was modified on 08-17 and none names pid 3828, the process described as live;
  `pid_reconcile.py` had all 39 dead and 2 of 3 "lost" runs COMPLETED CLEANLY -- dead is not failed.
  `exp_selectional_constraint_bridge_v1/metrics.json` is a COMPLETE full at 08-17T00:32.
- TWO AGENTS STOPPED MID-TASK on a denied write, correctly (`partial-cue-structural`,
  `verb-target-space`): resume each with "write findings to `notes/`".
- `.claude/scan-out/` REFUSES FILE CREATION (4x); `notes/ tools/ experiments/ verification/` accept.
  `experiments/exp_propose_reject_retrieval_v1.py` IS A BLOCKED PATH -- OWNER'S CALL, never retry a
  variant.
- NO BACKUP, gitignored: `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB).
- USER AUTH: `d=256->1024` (rewrites every anchor store), merge to `origin/main`, any push.
  Autoloop ARMED at 200.
- `hd_director_kb_continuous_ingest` LIVELOCKED (10.65 GB, self-killed at 45 min) while the
  scheduler reports it healthy -- `director_kb_query.py` is STALE.
- `LONG_TERM_PLAN.md` DIRECTOR-OWNED: sec 2 rows 3/4/6 superseded by STORAGE + C30; sec 4's
  dual-hub `[PINNED]` should drop to CONTESTED (Director's call, not done here).
- OVER CAP AND DELIBERATELY SO: never-trim stubs alone cost 5,120 B of 8704 (added tonight:
  DO-NOT-REDO 43, C32-C34, discipline 14). Steps 1-2 are spent; step 3 is RE-MEASURED AND
  RE-PROPOSED in `STATUS_SPEC.md` sec 7 (9216 B is now insufficient) -- DIRECTOR'S CALL. Never close
  the gap by evicting a never-trim entry.
