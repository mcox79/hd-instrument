# STATUS

AS OF: 2026-08-13 late | branch `dataprep/mcguffey-graded-corpus` | HEAD 0db7cfdaa+this |
58 ahead of origin (a37b8abeb), UNPUSHED -- push needs USER AUTHORIZATION.
Structure + trim rules: `notes/STATUS_SPEC.md` -- READ IT BEFORE EDITING THIS FILE. Never-trim
material lives in `notes/STATUS_LESSONS.md` (uncapped). Rewritten in place, never appended.
Cap 8192 B. Follow every pointer; don't trust this summary.

## POSITION
EXTRACTION (hand-written parser) works, 94% correct. READ-OUT does not, 1-3% MEANINGFUL -- and
the cause is now LOCATED: it can only name a lemma that is already an ANCHOR, and the anchor set
is 6% of corpus vocabulary. A working MULTI-SOURCE LOOKUP subsystem sits unwired. GROWTH STAYS
PAUSED until read-out grounding quality holds.

## TOP ITEM -- THE BOTTLENECK IS THE CANDIDATE SET (traced 08-13)
`notes/downstream_bottleneck_trace_2026-08-13.md`. On `banana` the structured comparator
isolated `(^nsubj, fruit)`, the correct hypernym, and the arm still scored 0/50. `fruit` (and
`zone` for `aphotic`) dies at STAGE 2, THE CANDIDATE SET, in BOTH arms: the comparison was never
OFFERED, so no score gap is reportable and none is given. `canonicalize_fast` argmaxes over
`anchor_matrix()` alone (`hdlab/reading_grounding_loop.py:656-703`) and lemmas enter
`ConceptSpace` only at `:1039-1044` (seed) and `:1279` (already grounded), so anchors = seed
UNION already-grounded: 1261 (CONTROL 1271) vs 16,812 content lemmas = 0.0599. Of 40 sampled
lemmas 32 isolate a head, only 11/32 = 0.3438 have it available as an anchor;
25,643/27,402 refusals are `HYPOTHESIS_BELOW_COMMIT_STRENGTH`; no displacement.

## READ-OUT PATH -- 1-3% MEANINGFUL, 5 ROUTES ELIMINATED
Three blind hand-scores, all 1-3% M / ~10-24% RELATED / 73-90% NOISE. Eliminated: F1+F3
stabilisation (NULL, floor-limited, 3% M, delta +0.02, max |d| 0.06); news->textbook swap
(REFUTED, 0/50 vs 4%, p=0.6529); co-occurrence as the explanation (either_top1 0.04/0.12);
sensorimotor anchoring (SHELVED); role-bound structure alone (NULL 0% vs 2%, yet DID bind --
argmax disagree 97.80%, cooc top5 0.2552->0.0749, 0db7cfdaa). Numbers + note paths:
`notes/STATUS_LESSONS.md` 9-11, 17-18.

## EXTRACTION PATH -- WORKING
v6.2 predicate recovery 94% MEANINGFUL, blind single-judge, n=50 of arm n=221; 70%->94% over
v6/v6.1/v6.2 (5e188ac1f, 405a25817) -- `notes/director_handscore_predicate_v62_2026-08-13.md`.
221 facts BANKED to `data/foundation_provenance_v1/` (`pipeline=DEFINITIONAL_EXTRACTOR`, gated,
b8d98509e); legacy store read-only, BYTE-IDENTICAL; rebuildable from `predicate_facts_v62.jsonl`
(221 lines, 5ea354285) -- `notes/foundation_reproducibility_2026-08-13.md`. Licenses ONLY
"parser hands store a correct fact ~94% of the time here"; NOT comparable to a read-out score.

## MULTI-SOURCE LOOKUP WORKS, NOT WIRED TO READING
`notes/multisource_lookup_wiring_audit_2026-08-13.md`. `hdlab/three_tier_loop.py`,
`gather_reason.py`, `prelim_tier.py`, `gap_driven_reader.py`; `pytest
verification/{test_three_tier_loop_e2e,test_prelim_tier,test_gather_reason}.py` = 9 passed; full
CSKG (1,213,912 edges) 3 HARD_PASS / 1 HARD_FAIL. But unreachable from reading: 40 `hdlab.*`
modules in `sys.modules` after importing `reading_grounding_loop`, none a lookup organ;
`reading_grounding_loop.py:1068` detects the gap, `:1075` builds the context vector, `:1078`
flags -- no branch reaches a source. GAP = missing TRANSLATION LAYER, lookup is CONCEPT-level
(`three_tier_loop.py:85`) vs LEMMA-level reading. Registry misleads -- 6 rows say
`integration_status: WIRED` + `pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`. KB on disk,
read only by cells: CSKG 1,213,912 rows; ConceptNet 5.7; ATOMIC 24,313; CauseNet 11.6M pairs.

## LEGACY FOUNDATION MOSTLY EMPTY
`notes/foundation_contents_audit_2026-08-13.md`, 3,544 GROUNDED_MEANING rows: >=76.5%
contentless/wrong-category (2712/3544), 65.69% self-referential tautologies
`(X,GROUNDED_MEANING,X)` (2328); ~10% of subjects over-stemmed by a pre-fix lemmatiser
(`notes/stemmer_corruption_2026-08-13.md`, unfixed). All of it from the READING LOOP, none from
the extractor. Certification is now honest -- `verification/test_all_witnesses_exit_clean.py`
27 witnesses, 29/29 (27+2 self-checks), c6279d2eb+1421c21db, 5 stale pins converted to `>=`
floors (improve=pass, regress=fail): `notes/uncollected_witness_audit_2026-08-13.md`,
`notes/false_certification_goal_typing_2026-08-13.md`.

## DO NOT REDO -- NEVER-TRIM -- numbers, criteria, evidence: `notes/STATUS_LESSONS.md` 1-19
All CLOSED; open the companion before re-proposing any. 1
intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic bootstrapping as a NEXT STEP; 4 F2
freq-corrected pool (has a revival criterion); 5 same-sentence cosine/PMI as a quality signal;
6 FHRR superposition for the 50-pair audit; 7 PBV; 8 read-out cell vs v5's 64%; 9 F1+F3
stabilisation as a quality route; 10 news->textbook corpus swap; 11 sensorimotor norms as a
read-out filter (SHELVED, has revival criteria); 12 context-conditioned sense selection v2;
13 the minimum-grounded-basis derivation; 14 `genuine_cross_source_corroboration_v1` (source
thinness, NOT mechanism); 15 `exp_combined_dictionary_consequence_word_learning_tool_v1`;
16 "the context vector is noise"; 17 co-occurrence as the explanation; 18 role-bound structure
alone; 19 frontmatter `isolation:` / `background:`.

## STANDING DISCIPLINES -- NEVER-TRIM -- full text: `notes/STATUS_LESSONS.md`
1. DO NOT GATE A CELL ON A HAND-SCORED MEANINGFUL DELTA WHILE THE GENERATOR SITS AT 1-3% M.
   Cost two whole experiments, both UNDERPOWERED BY FLOOR: `exp_grounding_quality_readout_v1`
   (3 M rows/100, max |delta| 0.06, inside its own NULL band --
   `notes/director_handscore_readout_v1_2026-08-13.md:31-44`) and `exp_structured_comparator_v1`
   (1 M row, max |delta| 0.02, 5.5x below its own declared min-detectable, after a prereg that
   claimed to have FIXED the first defect --
   `notes/director_handscore_structured_comparator_2026-08-13.md:56-81`). "Only CONTROL is
   floor-pinned so TREATMENT is free to rise" restates H1; it is not a power argument. Until the
   generator clears ~10% M, gate on KNOWN-ANSWER RECALL or a MECHANISTIC discriminator with
   range by construction.
2. SERIALIZE MEASUREMENT vs CODE CHANGE (2x): never audit/experiment while another agent may
   edit code it depends on, incl. transitive deps -- a racing edit describes no single repo
   state. `notes/measurement_layer_drift_2026-08-13.md` sec.8.
3. A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night): propose/verify share
   a metric; store/classifier a stemmer; cert/code a bug; tests/witnesses a naming blind spot.
   Consistency is not evidence. `notes/shared_flaw_invisibility_2026-08-13.md` (P1-P6).

## WHAT IS RUNNING / BLOCKED
- `data/exp_anchor_pool_expansion_v1/` RUNNING detached (PID 9260 / worker 29624, LARGE arm).
  The TOP ITEM trace supports its premise (anchor scarcity is the defect); it is no longer a
  suspected workaround, but it cannot fix candidate availability alone.
- `data/exp_structured_comparator_v1/probes/` -- concurrent agent writing; never staged.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk, NO BACKUP.
- Origin has the canonical-store tarball but NOT the scripts or the 221 facts. Push is the fix
  and needs USER authorization.
