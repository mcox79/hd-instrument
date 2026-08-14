# STATUS

AS OF: 2026-08-14 | branch `dataprep/mcguffey-graded-corpus` | GROWTH PAUSED | origin merge needs USER AUTH
HEAD + push delta: `git log -1` / `git status`. Rules: `notes/STATUS_SPEC.md` (READ BEFORE EDITING).
Never-trim detail: `notes/STATUS_LESSONS.md` (uncapped). Rewrite in place; cap 8192 B.
RECOVERY CHAIN: `notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md` (THE entry point) ->
THIS FILE -> `notes/RECOVERY_PROGRAM.md` -> `SUBSTRATE_STRATEGY.md` + `ORGAN_MAP.md`. The 08-04
POST_COMPACTION_BACKUP is SUPERSEDED; do not start there.

## POSITION
C3 read-out HAS A FLOOR FOR THE FIRST TIME: open-vocab hit@1 4.80% vs scramble 0.80% (n=4000, 5491
anchors) -- 6x its floor, 5.2pp short of the >=10% gate (`exp_grounding_readout_known_answer_v1`,
204eba1a0). Banked-facts arm AT_FLOOR (2.51% vs 1.25%); 2AFC 0.5393 MIDDLE_BAND; tautologies 0 in
EVERY arm (the 65.7% was an eligibility bug, C10). GROWTH PAUSED until quality holds.

## TOP ITEM -- THE DEFECT IS MEANING SUPPLY INTO THE CODEBOOK, NOT A RULE APPLIED TO IT
The read-out finds the right NEIGHBOURHOOD and picks the wrong MEMBER (axon->dendrite,
artery->vessel). Not RETRIEVAL (SELF_RETRIEVAL 0.786), not CANDIDATE SUPPLY (DNR 23/25). FOUR
attacks DOWNSTREAM of meaning content all failed in one night (DNR 26/27/29, D5), and the codebook
pre-check found ZERO near-duplicates but real semantic crowding, median NN 0.4637 vs null 0.2264
(DNR 30). Meanwhile meaning is a 359-word HAND LEXICON (`lexical_similarity.CONCEPT_FEATURES`)
while a 39,707-word norms island (`data/grounding_testbed`) and a 237.7M-token encoder sit OFF the
inference path. NEXT: fair-test wiring those assets into live canonicalization -- HANDOFF Q1,
untested end-to-end. The encoder is EXPERIMENT-ONLY (RECOVERY_PROGRAM F5): wiring = BUILDING.

## PHASE DIAGRAM -- THE STORE'S CORNER IS A CHOICE (full text, curves and sources in LESSONS)
Sparse-vs-dense codes, superposition load (facts per vector), K and n_dim are ALL tunable at will,
with the scaling laws banked. The store deliberately sits in the most conservative corner -- dense
bipolar, SHARDED at ONE FACT PER VECTOR -- OPTING OUT of the capacity phase diagram entirely, which
buys exact recovery and inspectability: A CHOICE, NOT A LIMITATION. TWO UNSPENT CASH-INS: RAM
CEILING -> controlled superposition; BUILDING REASONING -> sparse codes + composition depth.
NEITHER IS HIT -- quality binds. CORRECTION: `d=256->1024` is a MOVE ALONG A KNOWN CURVE, not a
priced "+0.05 upgrade".

## OTHER PATH STATE -- numbers in LESSONS
LANDED: graded comparator DEFAULT ON (`38f7a0d5c`), live path 0.6395 -> 0.6980 (+0.058); MECHANISM
WITHDRAWN, number survives (`f05b8a88a`); never quote 0.7495 (d=1024) or 0.69975 (probe arm) as
live. FORAGING (`3d4761f69`) HARD_PASS on its declared test (coverage 0.0617 vs RANDOM 0.0127) with
CAVEATS THAT TRAVEL: FROZEN beats it on coverage (0.0743), RANDOM on quality (0.3864 vs 0.3511).
RECOVERY: `notes/RECOVERY_PROGRAM.md` (LIVING, 95 systems) -- 5 FOUND / 76 VERIFIED / 1 WIRED /
2 SHELVED / 11 REFUTED at open; 10 tiers NOT-YET-TRIAGED (544 chain-graded, 127 reading cells).
Count: `grep -oE 'STATE:[A-Z]+'` that file.
INDEX (`tools/result_index_join.py`, probe `fa94a18e2`): 6566 of 7623 results (86%) UNINDEXED;
floor-vocabulary DRIFT ALARM FIRING at 26.4%. Settled workstreams are retired to the stubs below.
OPEN: (a) grounding-quality validation OWES a re-run vs the current foundation (C13 -- NOT un-run);
(b) sub-linear gap index NOT BUILT: design
`notes/research_sublinear_gap_detector_cleanup_shard_dg_ca3_design_2026-08-12.md` (C12), target
`hdlab/sharded_gap_index.py`; (c) fresh-checkout-broken orphan `hdlab/` files + 4 unregistered
load-bearing modules (`glass_box_loop`, `grounding_acquisition_loop`, `multi_hop`,
`script_grain_acquisition_loop`); (d) four older threads -- LESSONS "OPEN THREADS (older)".

## DO NOT REDO -- NEVER-TRIM -- stubs only; numbers + criteria in LESSONS
All CLOSED. `*` = has a revival criterion. 1 intersection-over-argmax; 2 the "40% ceiling";
3 syntactic bootstrapping as a NEXT STEP*; 4 F2 freq-corrected pool*; 5 same-sentence cosine/PMI;
6 FHRR superposition for the 50-pair audit; 7 PBV; 8 read-out vs v5's 64%; 9 F1+F3 stabilisation;
10 news->textbook swap; 11 sensorimotor norms as a FILTER*; 12 context-conditioned sense selection
v2; 13 minimum-grounded-basis derivation; 14 `genuine_cross_source_corroboration_v1`*;
15 `exp_combined_dictionary_...v1`; 16 "the context vector is noise"; 17 co-occurrence as the
explanation; 18 role-bound structure alone; 19 frontmatter `isolation:`/`background:`; 20 wiring the
voting mechanism*; 21 HAND-SCORING ANY MEANINGFUL DELTA at 1-3%; 22 the 2-hop bridges;
23 DEFINITIONAL EXTRACTION AS DIRECT-BANK (MASS not CONTENT)*; 24 DISTINCTIVENESS WEIGHTING as
log-IDF (that transform only)*; 25 EXTRACTOR DIFFERENTIA/GENUS + SUPPLY as the binding constraint;
26 `sign()` as destroyer of the forgetting kernel (D8 cascade organ ruled out TWICE); 27 RANK-1
COMMON-MODE REMOVAL (whitening NOT closed by it)*; 28 FORAGE_REFUSAL; 29 THE COMPOSED FIVE-STAGE
READ-OUT CHAIN (every arm worse); 30 NEAR-DUPLICATE ANCHORS AS THE DEFECT (zero at NN>=0.99).
CAVEATS (LESSONS): D1 near-vs-far = degradation not collapse; D2 encoder-swap ran on its own
harness; D3/D4 foraging reversals (above); D5 sharpening is SMOKE-scale MIDDLE_BAND, NOT an
SNR-wall verdict.
CORRECTIONS (LESSONS): C1 availability-binds-first WRONG; C2 CLIP-at-INGEST is no violation; C3 the
94% has NO floor; C4 DGProjection fixes interference not equidistance; C5 a landed encoder DOES
exist; C6 wrong checkpoint behind the synonym/sibling wall; C7 opportunity-map #5/#6; C8 comparator
was a LOOKUP TABLE; C9 results ARE searchable; C10 the tautology rate was an ELIGIBILITY BUG (live
0%); C11 the "58% common mode" does NOT reproduce; C12 the sub-linear design doc is dated 08-12 and
the HANDOFF's 08-14 filename does NOT exist; C13 the validation FULL run DID report (08-12, later
OVERSTATED).

## STANDING DISCIPLINES -- NEVER-TRIM -- full text in LESSONS
1. NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% M -- cost TWO whole
   experiments, both UNDERPOWERED BY FLOOR (`exp_grounding_quality_readout_v1`,
   `exp_structured_comparator_v1`, the second claiming to have FIXED the first). "Only CONTROL is
   floor-pinned" restates H1; no power argument. Gate on KNOWN-ANSWER RECALL instead.
2. SERIALIZE MEASUREMENT vs CODE CHANGE (2x): a racing edit, incl. a transitive dep, describes no
   single repo state.
3. A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night). Consistency is not
   evidence.
4. ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM (6x). SUB-RULE, the generative
   cause: AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NOT A SEARCH. State HOW you enumerated.
5. BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS THE OPERATION IT SCORES -- cost FOUR
   cells in ONE day on context-free word-pair similarity. DISTINCT FROM 1: those could not resolve
   an answer; these answered a question worth little.
6. RUN A POSITIVE / KNOWN-ANSWER ARM (cost 2x in one night): a FLOOR says whether the EFFECT is
   real, a KNOWN-ANSWER arm whether the INSTRUMENT is. Run both.
7. NO DEMOTION WITHOUT A FRESH ON-DISK RE-CHECK -- ~11 wrongly demoted, 17
   corrections-of-a-correction in 48h; the AUDIT layer was less reliable than the measurements.
   Keep EXISTS / IS-REACHED / IS-GOOD as separate questions.

## WHAT IS RUNNING / BLOCKED
- COREF-MARGIN agent LIVE (STEP 5) owns
  `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` -- do not touch.
- `data/exp_structured_comparator_v1/probes/` and `CLAUDE.md`: concurrent agents write; never stage.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB) on one disk, NO BACKUP; the
  37 MB snapshot is GITIGNORED and NOT in the remote (reproducible from code + corpora only).
- STEP 4 (`d=256->1024`) HELD PENDING USER AUTHORISATION; its framing was WRONG (see PHASE DIAGRAM)
  and it rewrites every persisted anchor store while a concurrent session is live.
- Merge to `origin/main`: USER AUTHORIZATION required.
