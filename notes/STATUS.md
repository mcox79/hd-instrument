# STATUS

AS OF: 2026-08-14 | branch `dataprep/mcguffey-graded-corpus` | GROWTH PAUSED | origin merge needs USER AUTH
HEAD/push delta: `git log -1`, `git status`. Rules: `notes/STATUS_SPEC.md` (READ BEFORE EDITING).
Never-trim detail: `notes/STATUS_LESSONS.md` (uncapped). PLAN: `notes/PLAN_NEXT_12H.md`.
Rewrite in place; cap 8192 B.
CHAIN: `HANDOFF_full_project_report_for_new_team_2026-08-14.md` -> HERE -> `PLAN_NEXT_12H.md` ->
`RECOVERY_PROGRAM.md` -> `SUBSTRATE_STRATEGY.md` + `ORGAN_MAP.md`. 08-04 BACKUP SUPERSEDED.

## POSITION
C3 read-out has a floor: open-vocab hit@1 4.80% vs scramble 0.80% (n=4000, 5491 anchors,
`exp_grounding_readout_known_answer_v1`, `204eba1a0`). THE GATE ITSELF WAS GAMEABLE, NOW
HARDENED (`9316f98ee`): bolting a PURE-SPELLING channel onto the base arm reaches 0.10275, clearing
the old ">=10% vs a floor" criterion (`c0e6ec0da`), now RETIRED. C3 needs FOUR conditions, EXECUTABLE
via `tools/c3_gate.py`; no string-form control = NOT_EVALUABLE, never PASS. NOTHING passes: 0 of 13
arms, incl. the gate's own cell (unmeasured on 3 of 4). "5.2pp short of 10%" measured the RETIRED
criterion; never re-quote it. GROWTH PAUSED -- the threshold did not separate meaning from
spelling.

## TOP ITEM -- A FLAT BAG OF CO-OCCURRING WORDS CANNOT HOLD MEANING
Three independent floored results converge; our live comparator loses all three.
FACTORED role/filler held-out **1.000 vs FLAT 0.003** (`exp_role_filler_factorization_compgen_v1`).
CONJUNCTIVE **1.000 vs ADDITIVE 0.273** at M=256
(`exp_interference_avoidance_conjunctive_vs_additive_v1`) -- the additive arm IS our bag geometry.
PERMUTATION binding **1.0000 vs FHRR 0.0629** on same-role collision
(`exp_substrate_permutation_binding_multiocc_v2_full`). NEXT = CONNECT EXISTING WORK, not invent:
give the live comparator a structured code. Rows: reading ledger #1/#3, chain-graded #1/#2.

## FLOOR VET (LESSONS: ORTHOGRAPHIC-FLOOR VET)
`notes/orthographic_floor_vet_and_rebaseline_2026-08-14.md` (`9ca1cffa2`). Pools ARE fair (bit-exact).
BUT `A5_STRINGCTRL` = `z(base) + w*z(trigram)` -- substrate PLUS spelling, NOT spelling
alone: **"we underperform a spell-checker" is NOT established, do not propagate it.**
It indicts the METRIC: spelling adds +0.0425 hit@1 vs the encoder's +0.0270. Strongest MEASURED
no-understanding floor = FREQUENCY 0.0185 (beaten 2.6x); the SPELLING-ALONE floor is
UNMEASURED (`scratch/ortho_floor_vet_trigram_only.py` drafted, NOT RUN) and blocks every floor
claim. `char_trigram_encoder` EXISTS but is NOT REACHED (runtime trace + positive control);
its registry row wrongly claims WIRED.

## RECOVERY TRIAGE (LESSONS: TRIAGE RESIDUE)
**968 cells now have rows**, in TWO ledgers NOT yet merged into `RECOVERY_PROGRAM.md`: chain-graded
565/565 + reading 403 (`51b6f247a`, `40997bf85`, `da7fe14d4`, `b4e90942a`, `63d5cccd2`).
**Until merged every count must run over ALL THREE** (`grep -oE 'STATE:[A-Z_]+'` = 1063 rows;
`RECOVERY_PROGRAM.md` alone returns 95). DEFLATIONS: 280 of 565 chain-graded rows are ONE
auto-generated grid, so "574 cells" is ~286 distinct investigations; only 172 (30%) have a
real floor; 0 of the 968 are WIRED. UNTRIAGED: ~1,180 atoms, ~7,150 of 7,660 `metrics.json`.

## OTHER PATH STATE
LANDED: graded comparator DEFAULT ON (`38f7a0d5c`, 0.6395 -> 0.6980), MECHANISM WITHDRAWN
(`f05b8a88a`) -- never quote 0.7495 or 0.69975 as live; FORAGING `3d4761f69` HARD_PASS w/ caveats.
PHASE DIAGRAM closed, neither cash-in hit; OPEN: C13 re-run, C12 sub-linear gap index NOT BUILT,
orphan hdlab/ files + 4 unregistered modules -- LESSONS "OPEN THREADS (older)".
NOT INVALIDATED: GROWTH stands (no-leak 0, scramble 0.077, persistence round-trip bit-identical;
`ac430868d`/`0472eeb0b`) -- a DIFFERENT claim, that grounding tracks real reading context rather
than shuffled, which spelling overlap cannot touch. INVALIDATED: the absolute-threshold framing and
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
as the defect; **31 MEANING SUPPLY AS THE C3 CONSTRAINT -- REFUTED**\*; **32 DG / pattern-separation
for grounding -- beaten on the real task in July**; **33 crowding as a gate criterion**.
CAVEATS: D1 near-vs-far = degradation not collapse; D2 encoder-swap on its own harness; D3/D4
foraging reversals; D5 sharpening is SMOKE-scale only.
CORRECTIONS: C1 availability-binds-first; C2 CLIP-at-INGEST; C3 the 94% has NO floor;
C4 DGProjection: interference not equidistance; C5 a landed encoder DOES exist; C6 wrong checkpoint
behind the synonym wall; C7 opportunity-map #5/#6; C8 comparator was a LOOKUP TABLE; C9 results ARE
searchable; C10 tautology rate was an ELIGIBILITY BUG (live 0%); C11 the "58% common mode";
C12 sub-linear doc date; C13 the validation FULL run DID report; **C14 whiten+pinv IS tested
end-to-end**; **C15 that chain's expansion stage is CONTRADICTED inside its own tier -- may DELETE a
stage**; **C16 `A5_STRINGCTRL` is NOT zero-meaning; the gate note's wording is corrected, its
conclusion stands**.

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
8. **A GATE IS A CI-SEPARATED MARGIN ABOVE max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE) on the IDENTICAL
   scorer / n / pool / gold -- NEVER a bare absolute number.** Cost: the whole ">=10%" C3 criterion,
   which a spelling channel cleared. The baseline must also be STANDALONE -- an arm adding a shortcut
   ON TOP of the system under test is a decomposition, not a floor.

## WHAT IS RUNNING / BLOCKED
- COREF-MARGIN agent LIVE (STEP 5) owns
  `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` -- do not touch.
- `data/exp_structured_comparator_v1/probes/` + `CLAUDE.md`: concurrent writers; never stage.
- The two `recovery_ledger_*` files: owned elsewhere; read, do not edit.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB) on one disk, NO BACKUP; the
  37 MB snapshot is GITIGNORED and NOT in the remote (reproducible from code + corpora only).
- STEP 4 (`d=256->1024`) HELD PENDING USER AUTH; framing WRONG (PHASE DIAGRAM), and it rewrites
  every persisted anchor store while a concurrent session is live.
- Merge to `origin/main`: USER AUTHORIZATION required.
