# STATUS

AS OF: 2026-08-14 | branch `dataprep/mcguffey-graded-corpus` | GROWTH PAUSED | origin merge needs USER AUTH
Rules: `notes/STATUS_SPEC.md` (READ BEFORE EDITING).
Never-trim detail: `notes/STATUS_LESSONS.md` (uncapped). PLAN: `notes/PLAN_NEXT_12H.md`.
Rewrite in place; cap 8704 B (raised 2026-08-15, SPEC sec 7).
CHAIN: HANDOFF_full_project_report_for_new_team_2026-08-14.md -> HERE -> PLAN_NEXT_12H.md ->
RECOVERY_PROGRAM.md -> SUBSTRATE_STRATEGY.md + ORGAN_MAP.md. 08-04 BACKUP SUPERSEDED.

## POSITION
C3 read-out 4.80% hit@1 clears scramble (0.80% / 1.375%, DONOR-RULE dependent) but is BELOW the
ORTHOGRAPHIC floor 8.70% -- see FLOOR VET
(`exp_grounding_readout_known_answer_v1`, `204eba1a0`). THE GATE WAS GAMEABLE, NOW HARDENED
(`9316f98ee`): a PURE-SPELLING channel on the base arm reaches 0.10275, clearing the old ">=10% vs
a floor" criterion, now RETIRED. C3 needs FOUR conditions via `tools/c3_gate.py`; no string-form
control = NOT_EVALUABLE, never PASS. NOTHING passes: 0 of 13 arms, incl. the gate's own cell.
"5.2pp short of 10%" measured the RETIRED criterion; never re-quote it.

## TOP ITEM -- A FLAT BAG OF CO-OCCURRING WORDS CANNOT HOLD MEANING
FACTORED role/filler held-out 1.000 vs FLAT 0.003 (`exp_role_filler_factorization_compgen_v1`).
CONJUNCTIVE 1.000 vs ADDITIVE 0.273 at M=256
(`exp_interference_avoidance_conjunctive_vs_additive_v1`) -- the additive arm IS our bag geometry.
PERMUTATION binding 1.0000 vs FHRR 0.0629 on same-role collision
(`exp_substrate_permutation_binding_multiocc_v2_full`). NEXT = CONNECT EXISTING WORK, not invent:
give the live comparator a structured code. QUALIFIED: perirhinal CONJUNCTION OP is UNPINNED +
feature-ambiguity CONTESTED (real failed replications) -- OURS to choose, NOT pinned brain
fidelity (4 rescued `lit_scan_*_2026-08-14.md`).

## FLOOR VET -- SPELLING MEASURED AND BEATS US (LESSONS: ORTHOGRAPHIC-FLOOR VET)
`exp_orthographic_floor_vet_v1`: TRIGRAM-ONLY (zero substrate signal) 0.0870 vs OURS 0.0480
(+0.0390, CI excl. 0); PREFIX-ONLY 0.0588 also beats us. REVERSES `9ca1cffa2`:
"we underperform a spell-checker" IS ESTABLISHED. `char_trigram_encoder` EXISTS but NOT REACHED;
its registry row wrongly says WIRED.

## FOUNDATION VALIDATION -- HARD_FAIL, SCORER LOOSE (metrics.json cited below, no LESSONS entry)
Claim1 0.9667 vs FREQUENCY floor 0.96, CIs overlap -- HARD_FAIL
(`exp_foundation_validation_harness_v2_floors_v1`, `62ecec9d5`). Claims 2/3 HOLD ROBUSTLY:
coherence 0.3111 vs -0.0055; can-reason 1.0 vs 0.0267. v3 fixed the freq-floor bug (claim1 ->
MIDDLE_BAND) but exposed the SCORER is loose: random decoy scores 0.76 on all 4 arms ->
INSTRUMENT_STILL_LOOSE. NO VERSION YET TRUSTWORTHY. v4 running, gated on decoy<=0.15. Store
CLEAN (0 junk/334 strings), not contamination.

## RECOVERY TRIAGE (LESSONS: TRIAGE RESIDUE)
MERGED into `RECOVERY_PROGRAM.md` (`2fbd28ea5`): 974 rows/~696 investigations, count over THAT
FILE ONLY ("all three" DOUBLE-COUNTS to 1944). 172/565 chain-graded have a real floor; 0 WIRED.
RE-CHECK FLOOR+SCORER BEFORE WIRING -- green rows used weak floors. UNTRIAGED: 263
atoms; ~7,150/7,634 metrics. Triage FP rate 49/49 (`kf2` sole true positive) -- disc.9.

## OTHER PATH STATE
LANDED: graded comparator DEFAULT ON (`38f7a0d5c`; 2AFC scorer, NOT C3 -- see 34/35),
MECHANISM WITHDRAWN (`f05b8a88a`); FORAGING `3d4761f69` HARD_PASS w/ caveats.
PHASE DIAGRAM closed, neither cash-in hit; OPEN (C13/C12, orphan hdlab/): LESSONS "OPEN THREADS
(older)".
NOT INVALIDATED: GROWTH stands (no-leak 0, scramble 0.077, round-trip bit-identical;
`ac430868d`) -- a DIFFERENT claim: grounding tracks real reading context vs shuffled, which
spelling overlap cannot touch. INVALIDATED: the absolute-threshold framing and
any "did this help?" on raw hit@1.

## DO NOT REDO -- NEVER-TRIM -- stubs; detail in LESSONS
All CLOSED. `*` = revival criterion. 1 intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic
bootstrapping*; 4 F2 freq-corrected pool*; 5 same-sentence cosine/PMI; 6 FHRR superposition; 7 PBV;
8 read-out vs v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 sensorimotor norms as
FILTER*; 12 context-conditioned sense selection v2; 13 minimum-grounded-basis derivation;
14 `genuine_cross_source_corroboration_v1`*; 15 `exp_combined_dictionary_...v1`; 16 "the context
vector is noise"; 17 co-occurrence as the explanation; 18 role-bound structure alone; 19 frontmatter
`isolation:`/`background:`; 20 wiring the voting mechanism*; 21 hand-scoring a MEANINGFUL delta at
1-3%; 22 the 2-hop bridges; 23 definitional extraction as DIRECT-BANK*; 24 distinctiveness weighting
as log-IDF*; 25 extractor differentia/genus + supply; 26 `sign()` vs the forgetting kernel; 27 rank-1
common-mode removal*; 28 FORAGE_REFUSAL; 29 the five-stage read-out chain; 30 near-duplicate anchors
as the defect; 31 meaning supply as an ADDITIVE CHANNEL -- REFUTED; NARROWED 08-15, a native /
in-distribution encoder is NOT refuted\*; 32 DG / pattern-separation
for grounding -- beaten on the real task in July; 33 crowding as a gate criterion; 34 flipping the GRADED SWITCH for a C3 gain -- MEASURED
NULL\*; 35 quoting +0.0602 / 0.6395->0.6980 as a C3 number -- 2AFC, WRONG CURRENCY;
36 `k_eff~=50` as a MEASURED limit -- it is the configured `SHORTLIST_K`, never swept\*;
37 "right neighbourhood, wrong member" as the C3 diagnosis -- zero-meaning spelling ties
median_rank 37.0\*.
CAVEATS: D1 near-vs-far = degradation not collapse; D2 encoder-swap on its own harness; D3/D4
foraging reversals; D5 sharpening is SMOKE-scale only.
CORRECTIONS: C1 availability-binds-first; C2 CLIP-at-INGEST; C3 the 94% has NO floor;
C4 DGProjection: interference not equidistance; C5 a landed encoder DOES exist; C6 wrong checkpoint
behind the synonym wall; C7 opportunity-map #5/#6; C8 comparator was a LOOKUP TABLE; C9 results ARE
searchable; C10 tautology rate was an ELIGIBILITY BUG (live 0%); C11 the "58% common mode";
C12 sub-linear doc date; C13 the validation FULL run DID report; C14 whiten+pinv IS tested
end-to-end; C15 that chain's expansion stage is CONTRADICTED inside its own tier -- may DELETE a
stage; C16 `A5_STRINGCTRL` is NOT zero-meaning; the gate note's wording is corrected, its
conclusion stands.

## STANDING DISCIPLINES -- NEVER-TRIM -- LESSONS
1. NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% M -- cost TWO experiments,
   both UNDERPOWERED BY FLOOR (`exp_grounding_quality_readout_v1`, `exp_structured_comparator_v1`,
   the 2nd claiming to have FIXED the 1st). Gate on KNOWN-ANSWER RECALL instead.
2. SERIALIZE MEASUREMENT vs CODE CHANGE (2x): a racing edit describes no single repo state.
3. A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night).
4. ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM (6x). SUB-RULE: AN ABSENCE CLAIM
   REQUIRES AN ENUMERATION, NOT A SEARCH. State HOW you enumerated.
5. BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS THE OPERATION IT SCORES (cost 4 cells/day).
6. RUN A POSITIVE / KNOWN-ANSWER ARM (2x in one night): a FLOOR says whether the EFFECT is real, a
   KNOWN-ANSWER arm whether the INSTRUMENT is. Run both.
7. NO DEMOTION WITHOUT A FRESH ON-DISK RE-CHECK -- ~11 wrongly demoted, 17 corrections-of-a-
   correction in 48h. Keep EXISTS / IS-REACHED / IS-GOOD separate.
8. A GATE IS A CI-SEPARATED MARGIN ABOVE max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE) on the IDENTICAL
   scorer / n / pool / gold -- NEVER a bare absolute number. Cost: the whole ">=10%" C3 criterion,
   which a spelling channel cleared. The baseline must also be STANDALONE -- an arm adding a shortcut
   ON TOP of the system under test is a decomposition, not a floor.
9 DETECTORS FIRE ON HONESTY -- a scanner misreads scope disclosure as overclaim; 49/49 flagged
in 3 passes were false positives (arm under a different name; derived number absent BY
CONSTRUCTION). `smoke`=reduced SEEDS not N; discriminator is REPRODUCTION not vocabulary. 10
SILENT JOINS FABRICATE BOTH GREEN AND RED, truncation incl. -- unmatched join reads as a result;
ASSERT+COUNT joined rows. CT1 consistent!=good; CT2 run_mode is an ingestion constant.

## WHAT IS RUNNING / BLOCKED
- COREF-MARGIN agent LIVE (STEP 5) owns
  `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` -- do not touch.
- `data/exp_structured_comparator_v1/probes/` + `CLAUDE.md`: concurrent writers; never stage.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), NO BACKUP; 37MB snapshot
  GITIGNORED, not in remote (reproducible from code+corpora).
- STEP 4 (`d=256->1024`) HELD PENDING USER AUTH -- rewrites every persisted anchor store while a
  concurrent session is live.
- Merge to `origin/main`: USER AUTH required.
