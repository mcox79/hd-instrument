# STATUS

AS OF: 2026-08-14 morning | branch `dataprep/mcguffey-graded-corpus`, HEAD `41da8e454`+this commit,
ahead of pushed tip `48a9900c1`; merge to `origin/main` needs USER AUTHORIZATION.
Rules: `notes/STATUS_SPEC.md` (READ BEFORE EDITING). Never-trim detail:
`notes/STATUS_LESSONS.md`, uncapped. Plan + scoreboard: `notes/SUBSTRATE_STRATEGY.md`.
Rewrite in place; cap 8192 B.

## POSITION
C3 (reading-grounding read-out) HAS A FLOOR FOR THE FIRST TIME: open-vocabulary hit@1 4.80% vs
scramble 0.80% -- real, 6x its floor, still 2x short of the 10% revival gate. The 65.7% tautology
figure was an ELIGIBILITY BUG (CORRECTION C10); the live path emits 0%, so the tautology half of
the gate PASSES and only quality fails. Build steps 2 and 3 CLOSED, both clean negatives.
GROWTH STAYS PAUSED.

## TOP ITEM -- THE READ-OUT FINDS THE NEIGHBOURHOOD AND CANNOT PICK THE MEMBER
Every correct open-vocabulary hit is a SISTER term: axon->dendrite, artery->vessel, anaphase->telophase
(`data/exp_grounding_readout_known_answer_v1/metrics.json` `example_gold_hits`). So the defect is
not RETRIEVAL (SELF_RETRIEVAL 0.786) and not SUPPLY (closed: DO NOT REDO 23/25). It is
WITHIN-NEIGHBOURHOOD SEPARATION -- the same 2.20% sister-term error rate that rank-1 removal left
untouched, zero converted. The graded flip `38f7a0d5c` is what puts the read-out above chance at
all: 2AFC ON 0.5393 vs OFF 0.4720, BELOW CHANCE. The next step must attack SEPARATION;
supply, mass, coverage and reweighting are separately closed.

## READ-OUT / C3 -- `exp_grounding_readout_known_answer_v1` (a334501d2, 1b2022522, 204eba1a0)
Open-vocab hit@1 4.80% vs 0.80% scramble, +4.00pp CI [+3.30,+4.70], n=4000, 5491 anchors.
Banked facts n=319: GOLD_HIT 2.51%, scramble 1.25%, popularity 0.94%, CI [-0.31,+3.13] -> AT_FLOOR.
2AFC graded ON 0.5393 (scramble 0.4738, freq 0.4943) MIDDLE_BAND. Tautologies 0 in EVERY arm.
Graded-OFF run: `data/exp_grounding_readout_known_answer_v1_G0/`.

## FORAGING -- HARD_PASS, reversals travel (LESSONS D3/D4)
`exp_information_foraging_reading_v1` (3d4761f69): D2 held-out coverage FORAGE 0.0617 vs RANDOM
0.0127, +3.868 rel (load-bearing test). D3 WordNet agreement FORAGE 0.3511 vs
FROZEN 0.2920. D1 0.1585. D4 FAILED (oracle ratio 0.5344 vs 0.70-1.00; leaves patches early;
mechanism check only). CAVEATS: FROZEN beats FORAGE on D2 (0.0743) and RANDOM beats it on
D3 (0.3864); FROZEN did NOT reproduce the biology skew, so H2 is UNCONFIRMED by this cell; the
shelf is 28 corpora.

## OTHER PATH STATE -- settled; numbers in LESSONS
LEXICAL SEMANTICS: four adequately-powered negatives, all context-free word-pair similarity
(DO NOT REDO 23/24/25, CAVEAT D1). ENCODER: `hdlab/encoder_retrain_persist.py` WIRED but every
transfer eval is the SYNTHETIC harness -- neutral-ground test OWED (D2, ENCODER LINEAGE).
COMPARATOR IS BINDING (C1). EXTRACTION v6.2 94% blind, NO FLOOR ARM (C3).
OPEN: (a) encoder-swap `metrics.json` UNCOMMITTED (f36ba7626); (b) the live parser loads
RICH-TRAINED weights into the BASE class, UAS unmeasured; (c) 42% of the glass-box trail is
UNRECOVERABLE; (d) nothing enforces a post-landing import check -- `38f7a0d5c` left the C1 testbed
UNIMPORTABLE at HEAD and only a later cell found it (repair `df149251f`).

## DO NOT REDO -- NEVER-TRIM -- stubs; numbers + criteria in LESSONS
All CLOSED; read the companion first. `*` = has a revival/reopen criterion.
1 intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic bootstrapping as a NEXT STEP*; 4 F2
freq-corrected pool*; 5 same-sentence cosine/PMI; 6 FHRR superposition for the 50-pair audit;
7 PBV; 8 read-out cell vs v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 sensorimotor
norms as a FILTER (SHELVED)*; 12 context-conditioned sense selection v2; 13 minimum-grounded-basis
derivation; 14 `genuine_cross_source_corroboration_v1`*; 15 `exp_combined_dictionary_...v1`;
16 "the context vector is noise"; 17 co-occurrence as the explanation; 18 role-bound structure
alone; 19 frontmatter `isolation:`/`background:`; 20 wiring the voting mechanism*; 21 HAND-SCORING
ANY MEANINGFUL DELTA at 1-3%; 22 the 2-hop bridges; 23 DEFINITIONAL EXTRACTION AS DIRECT-BANK, MASS
not CONTENT*; 24 DISTINCTIVENESS WEIGHTING as log-IDF (that transform only)*; 25 EXTRACTOR
DIFFERENTIA/GENUS FEATURES + SUPPLY as the binding constraint (supply FIXED, answer unmoved);
26 `sign()` AS THE DESTROYER OF THE FORGETTING KERNEL -- REFUTED, and the D8 cascade/Benna-Fusi
organ is now ruled out TWICE (PARKED-BY-SCALE **and** unnecessary); 27 RANK-1 COMMON-MODE REMOVAL
(full-covariance whitening still PARKED-BY-SAMPLE-SIZE, NOT closed by this)*; 28 FORAGE_REFUSAL.
CAVEATS THAT TRAVEL (LESSONS, same heading): D1 near-vs-far is degradation, not collapse; D2 the
encoder-swap HARD_PASS ran on the encoder's own harness; D3 two non-verdict arms beat FORAGE and D4
failed; D4 the FROZEN control did not reproduce the biology skew.
CORRECTIONS: C1 availability-binds-first is WRONG; C2 CLIP at INGEST is NOT a glass-box violation;
C3 the 94% has NO floor; C4 DGProjection fixes interference, not equidistance; C5 a landed encoder
DOES exist; C6 the synonym/sibling wall used the WRONG checkpoint; C7 opportunity-map #5/#6;
C8 the comparator was an embedded similarity LOOKUP TABLE; C9 results ARE searchable; C10 THE 65.7%
TAUTOLOGY RATE WAS AN ELIGIBILITY BUG, not a meaning failure -- live path emits 0%; C11 THE "58%
COMMON MODE" DOES NOT REPRODUCE (0.3650 graded / 0.2997 sign) and 0.5841 was a NORM RATIO quoted as
a VARIANCE FRACTION -- true energy 0.1535, PC1 0.0350.

## STANDING DISCIPLINES -- NEVER-TRIM -- full text in LESSONS
1. DO NOT GATE A CELL ON A HAND-SCORED MEANINGFUL DELTA WHILE THE GENERATOR SITS AT 1-3% M. Cost
   TWO whole experiments, both UNDERPOWERED BY FLOOR (`exp_grounding_quality_readout_v1`;
   `exp_structured_comparator_v1`, whose prereg claimed to have FIXED the first's defect). "Only
   CONTROL is floor-pinned" restates H1, it is no power argument. Until ~10% M, gate on
   KNOWN-ANSWER RECALL or a discriminator with range by construction.
2. SERIALIZE MEASUREMENT vs CODE CHANGE (2x): never audit/experiment while another agent may edit
   code it depends on, incl. transitive deps -- a racing edit describes no single repo state.
3. A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night): propose/verify a
   metric; store/classifier a stemmer; cert/code a bug; tests/witnesses a naming blind spot.
   Consistency is not evidence.
4. ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM. 6x now. SUB-RULE (the
   generative cause): AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NOT A SEARCH -- "I looked and did
   not find it" is no evidence of absence when the naming convention is unknown. State HOW you
   enumerated.
5. BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS THE OPERATION IT SCORES. Cost FOUR cells
   in ONE day, all optimising context-free word-pair similarity. DISTINCT FROM 1: those cells could
   not RESOLVE an answer; these resolved one cleanly for a question worth little.
6. RUN A POSITIVE / KNOWN-ANSWER ARM -- it catches measurement defects NO arm of interest can. Cost
   2x in one night: the forgetting-kernel estimator returned a confident CI that EXCLUDED truth
   (survivorship bias dropped 96/1140 points; pseudo-replication inflated AIC), caught only by the
   synthetic arm; and the read-out's SELF_RETRIEVAL 0.786 is what licensed attributing its null to
   MEANING rather than plumbing. DISTINCT FROM the floor discipline: a FLOOR says whether the
   EFFECT is real, a KNOWN-ANSWER arm says whether the INSTRUMENT is. Run both.

## WHAT IS RUNNING / BLOCKED
- COREF-MARGIN agent LIVE (build STEP 5): owns
  `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*`. Do not touch those paths.
- `data/exp_structured_comparator_v1/probes/` and `CLAUDE.md`: concurrent agents write; never stage.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk, NO BACKUP.
- STEP 4 (`d=256->1024`, priced ~+0.05 on C1) is HELD PENDING USER AUTHORISATION: it rewrites every
  persisted anchor store while a concurrent session is live.
- Merge to `origin/main`: USER AUTHORIZATION required.
