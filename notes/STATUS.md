# STATUS

AS OF: 2026-08-13 night | branch `dataprep/mcguffey-graded-corpus`, HEAD `42792834c`+this commit,
ahead of pushed tip `48a9900c1`; merge to `origin/main` needs USER AUTHORIZATION.
Rules: `notes/STATUS_SPEC.md` (READ BEFORE EDITING). Never-trim numbers/evidence/reopen criteria:
`notes/STATUS_LESSONS.md`, uncapped. Rewritten in place, cap 8192 B.

## POSITION
FOUR cells on 08-13 tested CONTEXT-FREE word-pair similarity and ALL FAILED; per the same day's
brain drill that framing is itself un-brain-faithful -- the brain never computes a context-free
word-word similarity. Narrative: `notes/director_evening_digest_2026-08-13.md`. EXTRACTION works
(94%, no floor), the READ-OUT does not. GROWTH STAYS PAUSED until grounding quality holds.

## TOP ITEM -- CONTEXT-CONDITIONED NEAR-NEIGHBOUR DISCRIMINATION (drill element E4)
`concept_similarity(a,b)` is a bare 2-arg function with NO CONTEXT PORT. The brain separates near
neighbours by DISTINCTIVE features -- weakly-correlated, low-redundancy, hence FRAGILE (first lost
in semantic dementia, whose earliest errors are within-category coordinate confusions) -- under
semantic control that applies GAIN, not candidate selection:
`notes/brain_drill_encoder_lexical_semantics_2026-08-13.md` (471798502, 5 lit scans ce2e99388).
E4 UNTESTED: does CONTEXT create the signal context-free comparison provably cannot? It exploits a
measured REAL signal -- context flip 0.7830 vs scramble 0.9984
(`notes/context_vector_signal_v1_2026-08-12.md`). Cell IN FLIGHT (last section).

## LEXICAL-SEMANTICS PATH -- FOUR NEGATIVES (numbers + reopen criteria in LESSONS 23/24/25, D1)
All adequately powered. `exp_wire_definitional_v1` MASS_NOT_CONTENT (SHUFFLE == ON to 6 dp on
every held-out metric, injected-A witness proves that control VALID: gain is fact MASS not CONTENT);
`exp_distinctiveness_weighted_composition_v1` HARD_FAIL_SHAPE (weighted BELOW uniform; UNPLANNED
finding C8); `exp_differentia_feature_supply_v1` HARD_FAIL both clauses (supply fix WORKED, 29 ->
350 pairs, so SUPPLY NO LONGER BINDS and the answer is still no); `exp_near_vs_far_diagnostic_v1`
NEAR_COLLAPSE WITH A CAVEAT THAT TRAVELS (D1: MDE 0.212 at n=78 -- degradation, not collapse).

## ENCODER PATH -- A LEARNED ENCODER LANDED (C5, C6); NEUTRAL-GROUND TEST OWED (D2)
`hdlab/encoder_retrain_persist.py`, registry WIRED, FOUR floors. SCOPE TRAVELS WITH
EVERY CITATION: real ARC base text, but the DELTA and all transfer evals are the SYNTHETIC
situation-model harness -- naturalistic validation PENDING, coref 0.652, a LEVER not solved
comprehension. The encoder-swap cell is HARD_PASS /
REFUTES_USER_CLAIM (+0.5513) but ran on the ENCODER'S OWN TUNING HARNESS and its span control ties
all five arms at 1.000 -- trained-vs-simple is NOT settled (D2).

## OTHER PATH STATE -- settled
COMPARATOR IS BINDING (C1; anchor pool 4.8x, recall@1 barely moved):
`notes/e2e_substrate_trace_2026-08-13.md`. EXTRACTION v6.2 94% blind, NO floor
arm (C3): `notes/director_handscore_predicate_v62_2026-08-13.md`. FLOORED ASSETS: 5 HARD_PASS with
floors, CLIP unregistered (C2) -- LESSONS. MULTI-SOURCE LOOKUP works, NOT wired to
reading (no concept->lemma TRANSLATION LAYER):
`notes/multisource_lookup_wiring_audit_2026-08-13.md`. LEGACY FOUNDATION 65.7% tautologies:
`notes/foundation_contents_audit_2026-08-13.md`. RESEARCH PERSISTENCE: `data/literature_cache/`
(4fbe50f91) + `notes/research_persistence_policy_2026-08-13.md`.

## OPEN
(a) encoder-swap `metrics.json` UNCOMMITTED (cell+prereg f36ba7626). (b) USER QUESTION: is the
GAP-DRIVEN LEARNING LOOP functioning? A HUMAN, not the loop, noticed the biology-only corpus gap;
audit IN FLIGHT. (c) A DEFAULT-OFF change is NON-NEUTRAL, 384 -> 386,
anchor-pool hook prime suspect, diff UNREAD. (d) The live parser loads RICH-TRAINED weights into the
BASE class, UAS unmeasured, so the structured-comparator 0/50 null is UNINTERPRETABLE. (e) 42% of
the glass-box trail is UNRECOVERABLE.

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
not CONTENT*; 24 DISTINCTIVENESS WEIGHTING as log-IDF (that transform only, not every
distinctiveness transform)*; 25 EXTRACTOR DIFFERENTIA/GENUS FEATURES + SUPPLY as the binding
constraint (supply FIXED, answer unmoved).
CAVEATS THAT TRAVEL (LESSONS, same heading): D1 near-vs-far is degradation, not collapse; D2 the
encoder-swap HARD_PASS ran on the encoder's own harness, neutral-ground test owed.
CORRECTIONS: C1 availability-binds-first is WRONG; C2 CLIP at INGEST is NOT a glass-box violation
(the bar is on LLMs at RUNTIME INFERENCE); C3 the 94% has NO floor; C4 DGProjection
fixes interference, not equidistance; C5 a landed encoder DOES exist, v2 NOT superseded; C6 the
synonym/sibling wall used the WRONG checkpoint; C7 opportunity-map #5/#6 numbers; C8 the comparator
was an embedded similarity LOOKUP TABLE (0.536 -> 0.080 without lexrel edges); C9 results ARE searchable.

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
4. ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM. 6x now; the newest three
   (08-13) cost the most -- an audit that called a whole capability line "abandoned, not won", and
   a diagnostic that measured a different, FAILED cell's checkpoint (C5, C6). SUB-RULE (the
   generative cause): AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NOT A SEARCH -- "I looked and did
   not find it" is no evidence of absence when the naming convention is unknown (a `_fulldev` suffix,
   untracked assets, opt-in modules). State HOW you enumerated.
5. BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS THE OPERATION IT SCORES. Cost FOUR cells
   in ONE day, all optimising context-free word-pair similarity. Standard, well-controlled and
   well-powered does not make it the right question.
   DISTINCT FROM 1: those cells could not RESOLVE an answer; these resolved one cleanly for a
   question worth little.

## WHAT IS RUNNING / BLOCKED
- `exp_context_conditioned_near_neighbour` IS IN FLIGHT (the TOP ITEM cell, another agent). Do not
  touch `data/exp_context_conditioned_near_neighbour*` or anything it may write.
- GAP-LOOP AUDIT IN FLIGHT (another agent, answers OPEN (b)) ->
  `notes/gap_driven_learning_loop_audit_2026-08-13.md`; do not write that file.
- `data/exp_structured_comparator_v1/probes/` and `CLAUDE.md`: concurrent agents write; never stage.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk, NO BACKUP.
- Merge to `origin/main`: USER AUTHORIZATION required.
