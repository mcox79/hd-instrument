# STATUS

AS OF: 2026-08-13 night | branch `dataprep/mcguffey-graded-corpus`, HEAD 2 commits ahead of its
pushed tip `48a9900c1`; `origin/main` 1235 behind -- merge needs USER AUTHORIZATION.
Rules: `notes/STATUS_SPEC.md` (READ BEFORE EDITING). Never-trim numbers/evidence/reopen criteria:
`notes/STATUS_LESSONS.md`, uncapped. Rewritten in place, cap 8192 B; follow the pointers.

## POSITION
EXTRACTION works (94%, no floor). READ-OUT does not (1-3% MEANINGFUL). The binding
constraint is the COMPARATOR, not candidate supply; the one route AROUND it -- banking definitional
facts directly -- has now REPORTED NEGATIVE (fact MASS, not CONTENT). GROWTH STAYS PAUSED until
grounding quality holds.

## TOP ITEM -- #1 IS CLOSED BY ITS OWN CONTROL; RE-RANK BEFORE PICKING
`exp_wire_definitional_v1` FINISHED (full, band `MASS_NOT_CONTENT`). Held-out B, n=661: ON recall@1
0.037821 vs OFF 0.007564 clears its +0.03 bar BUT **SHUFFLE is IDENTICAL to ON to 6 decimals on
EVERY held-out metric**; FREQMATCH +0.0015. The manipulation DID work (injected-A ON live_banked
394/394 vs SHUFFLE 0/394; OFF regression 386==386): VALID CONTROL, not a smoke failure -- DO NOT
REDO 23. Next: opportunity #2 (a channel INDEPENDENT IN KIND from the one that made the basis) or
the FLOORED ASSETS below (CLIP was never gated). NOT #5/#6 of
`notes/opportunity_map_2026-08-13.md` -- wrong numbers (C7).

## READ-OUT PATH -- THE COMPARATOR IS BINDING (settled 08-13)
`exp_anchor_pool_expansion_v1`, one variable = anchor pool size, verdict `COMPARATOR_IS_BINDING`:
availability 0.199 -> 0.953 while recall@1 moved only 0.0081 -> 0.0333 and availability-conditioned
recall@1 went NEGATIVE -- candidate supply ELIMINATED (C1). ATTRITION 16,812 lemmas -> 386 facts
(2.4%): `notes/e2e_substrate_trace_2026-08-13.md`.

## EXTRACTION PATH -- WORKING
v6.2 predicate recovery 94% MEANINGFUL, blind single-judge, n=50/221 --
`notes/director_handscore_predicate_v62_2026-08-13.md`. NO floor arm (C3), nothing comparative
licensed. 221 facts BANKED (`notes/foundation_reproducibility_2026-08-13.md`).

## ENCODER PATH -- A LEARNED ENCODER DID LAND (prior claim CORRECTED: C5, C6)
`hdlab/encoder_retrain_persist.py` @ `367a42729`, clean at HEAD, registry WIRE/WIRED; ckpts in
`data/exp_encoder_retrain_persist_v1/` untracked by design, all load, verifier PASS. v2
TinyTransformer + minimal top-1-layer unfreeze, FOUR floors (three 08-01 transfer HARD_PASSes + a
CLEAN_PASS cert). **SCOPE, travels with every citation:** real ARC text as base, but the
DELTA and all transfer evals are the SYNTHETIC situation-model harness, naturalistic validation
PENDING, coref absolute 0.652 (< 0.70) -- a proven LEVER, NOT solved comprehension. OPT-IN BY
DESIGN (plug point `process_sentence(..., encoder=None)`), so the "40 modules, 0 encoders" trace
measured the DEFAULT path, not EXISTENCE. Synonym/sibling is OPEN, not a wall (C6). LESSONS
ENCODER LINEAGE + `notes/encoder_landed_correction_2026-08-13.md`.

## FLOORED ASSETS NEW TO THESE DOCS -- LESSONS, same heading
All five HARD_PASS with control floors. MAVEN-ERE causal + subevent on the FULL DEV split, hidden
by a `_fulldev` suffix. Multi-bank WM -- its registry row names `hdlab/working_memory.py`, the real
impl is the UNREGISTERED `hdlab/situation_model_multibank.py`. DG pre-write pattern separation.
CLIP visual grounding (T1 0.635 vs shuffled 0.074) has NO registry row, so WIRE-or-SHELVE never saw
it (C2). Teacher-free relational encoder on a ConceptNet subgraph.

## OTHER PATH STATE
MULTI-SOURCE LOOKUP WORKS, NOT WIRED TO READING -- the gap is a missing TRANSLATION LAYER
(lookup CONCEPT-level, reading LEMMA-level): `notes/multisource_lookup_wiring_audit_2026-08-13.md`.
LEGACY FOUNDATION MOSTLY EMPTY -- 65.7% of its 3,544 GROUNDED_MEANING rows are tautologies
`(X,GROUNDED_MEANING,X)`, all from the READING LOOP, none from the extractor:
`notes/foundation_contents_audit_2026-08-13.md`. Today's audits: `notes/*_2026-08-13.md`.

## OPEN
(a) A DEFAULT-OFF change is NON-NEUTRAL: 384 -> 386, all self-tests passing; anchor-pool hook is
prime suspect BY ELIMINATION, diff UNREAD. (b) The live parser loads RICH-TRAINED weights into the
BASE class, `RichArcParser`/`_arc_ids_rich` exist NOWHERE in `hdlab/`, UAS unmeasured -- so the
structured-comparator 0/50 null is UNINTERPRETABLE. (c) 42% of the glass-box trail is UNRECOVERABLE
(`reading_grounding_loop.py:1382`).

## DO NOT REDO -- NEVER-TRIM -- stubs only; every number and criterion is in LESSONS
All CLOSED; read the companion before re-proposing. `*` = has a revival/reopen criterion.
1 intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic bootstrapping as a NEXT STEP*; 4 F2
freq-corrected pool*; 5 same-sentence cosine/PMI; 6 FHRR superposition for the 50-pair audit;
7 PBV; 8 read-out cell vs v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 sensorimotor
norms (SHELVED)*; 12 context-conditioned sense selection v2; 13 minimum-grounded-basis derivation;
14 `genuine_cross_source_corroboration_v1`*; 15 `exp_combined_dictionary_consequence_word_learning_tool_v1`;
16 "the context vector is noise"; 17 co-occurrence as the explanation; 18 role-bound structure
alone; 19 frontmatter `isolation:`/`background:`; 20 wiring the voting mechanism*; 21 HAND-SCORING
ANY MEANINGFUL DELTA at 1-3% (esp. `exp_anchor_pool_expansion_v1/blind_sample.json`); 22 the 2-hop
bridges; 23 DEFINITIONAL EXTRACTION AS DIRECT-BANK -- MASS not CONTENT; reopens ONLY on a mechanism
that consumes fact CONTENT, i.e. a measurable ON-vs-SHUFFLE separation.
CORRECTIONS: C1 availability-binds-first WRONG; C2 CLIP visual grounding is NOT a glass-box
violation (the bar is on LLMs at RUNTIME INFERENCE, not on building the seed); C3 the 94% has NO
floor; C4 DGProjection fixes interference, not equidistance; C5 "no final landed encoder" WRONG,
and v2 is NOT superseded by v3_relobj (which changed the OBJECTIVE); C6 the synonym/sibling wall
ran on the v3_relobj HARD_FAIL ckpt and was superseded 43 min later (0.5888 > randinit 0.4615);
C7 opportunity-map #5/#6 rest on wrong numbers.

## STANDING DISCIPLINES -- NEVER-TRIM -- full text in LESSONS
1. DO NOT GATE A CELL ON A HAND-SCORED MEANINGFUL DELTA WHILE THE GENERATOR SITS AT 1-3% M. Cost
   TWO whole experiments, both UNDERPOWERED BY FLOOR (`exp_grounding_quality_readout_v1`;
   `exp_structured_comparator_v1`, whose prereg claimed to have FIXED the first's defect). "Only
   CONTROL is floor-pinned so TREATMENT is free to rise" restates H1, it is no power argument.
   Until the generator clears ~10% M, gate on KNOWN-ANSWER RECALL or a MECHANISTIC discriminator
   with range by construction.
2. SERIALIZE MEASUREMENT vs CODE CHANGE (2x): never audit/experiment while another agent may edit
   code it depends on, incl. transitive deps -- a racing edit describes no single repo state.
3. A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night): propose/verify a
   metric; store/classifier a stemmer; cert/code a bug; tests/witnesses a naming blind spot.
   Consistency is not evidence.
4. ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM. **6x now**; the newest three
   (08-13) cost the most -- an audit that called a whole capability line "abandoned, not won", and
   a diagnostic that measured a different, FAILED cell's checkpoint (C5, C6).
   **SUB-RULE (the generative cause): AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NOT A SEARCH.** "I
   looked and did not find it" is not evidence of absence when the naming convention is unknown
   (`_fulldev` suffix, untracked 105 MB assets, opt-in modules missing from a default-path trace).
   Before writing that something does not exist, state HOW you enumerated and what naming variants
   that would have caught.

## WHAT IS RUNNING / BLOCKED
- Nothing this session launched is running; `exp_wire_definitional_v1` FINISHED (process gone, log
  ends DONE). Another session may be running work.
- `data/exp_structured_comparator_v1/probes/` and `CLAUDE.md` -- concurrent agents may write;
  never stage either.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk, NO BACKUP.
- Merge to `origin/main`: USER AUTHORIZATION required.
