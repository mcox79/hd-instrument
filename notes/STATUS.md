# STATUS

AS OF: 2026-08-13 late | branch `dataprep/mcguffey-graded-corpus` @ 48a9900c1, pushed through
HEAD; `origin/main` 1233 behind -- merge needs USER AUTHORIZATION.
Rules: `notes/STATUS_SPEC.md` -- READ BEFORE EDITING. Never-trim material: `notes/STATUS_LESSONS.md`
(uncapped). Rewritten in place, cap 8192 B. Follow every pointer; don't trust this summary alone.

## POSITION
EXTRACTION works (94%, no floor recorded). READ-OUT does not (1-3% MEANINGFUL). Binding
constraint SETTLED by pre-registered experiment: the COMPARATOR, not candidate supply -- BYPASS
it, don't feed better candidates. No final landed encoder exists (see ENCODER PATH). GROWTH
STAYS PAUSED until grounding quality holds.

## TOP ITEM -- BYPASS THE COMPARATOR: definitional extraction as direct-bank + verifier
`notes/opportunity_map_2026-08-13.md` ranks by P(acts on a MEASURED-binding constraint) x
magnitude x P(gain survives its own control). #1: wire definitional extraction to bank facts
DIRECTLY with an INDEPENDENT verifier (64% MEANINGFUL vs the read-out's 8% floor) -- the only
item routing AROUND the measured constraint. GATE: in-flight
`exp_wire_definitional_v1` reports first. #2: replace the equidistant basis with a channel
INDEPENDENT IN KIND. #3: measure the parser loader (open q b). `DGProjection` fixes
interference, not equidistance (LESSONS C4).

## READ-OUT PATH -- THE COMPARATOR IS BINDING (settled 08-13)
`exp_anchor_pool_expansion_v1`, one variable = anchor pool size, verdict `COMPARATOR_IS_BINDING`.
Availability 0.199 -> 0.953 while recall@1 moved only 0.0081 -> 0.0333, BELOW its +0.03 floor;
availability-conditioned recall@1 -0.0060 (negative); co-occurrence agreement ROSE 0.075 -> 0.102.
Candidate supply ELIMINATED as the explanation; the earlier "availability binds first" reading is
CORRECTED as WRONG -- 386->600 facts is VOLUME, not correctness (LESSONS C1).
ATTRITION, e2e full corpus: 16,812 lemmas -> 386 facts (2.4%); 98.5% lost at admission, 6.6%
reach commit strength; full refusal/rank breakdown in `notes/e2e_substrate_trace_2026-08-13.md`.
Three blind hand-scores: 1-3% M / 10-24% RELATED / 73-90% NOISE; 5 routes eliminated (LESSONS
9-11, 17-18).

## EXTRACTION PATH -- WORKING
v6.2 predicate recovery 94% MEANINGFUL, blind single-judge, n=50/221 --
`notes/director_handscore_predicate_v62_2026-08-13.md`. NO floor arm run (C3), nothing
comparative licensed. 221 facts BANKED, rebuildable -- `notes/foundation_reproducibility_2026-08-13.md`.

## ENCODER PATH -- NO FINAL LANDED ENCODER
Line ABANDONED, not won: 40 hdlab modules load, 0 encoders; live similarity =
lexical+grounded_similarity, capped 0.45. S8 verdict SURVIVES, reason WRONG (dead
`concept_encoder.py`, not the successor, which learns but loses its edge to a random-init twin
on the synonym/sibling wall). CLIP grounding ruled out in error (C2), best-floored result in the
corpus. 18 pass-vs-conflicting-data cases, worst 2 + detail:
`notes/encoder_lineage_final_2026-08-13.md`, `notes/STATUS_LESSONS.md` ENCODER LINEAGE.

## MULTI-SOURCE LOOKUP WORKS, NOT WIRED TO READING
`notes/multisource_lookup_wiring_audit_2026-08-13.md`. No lookup organ in `sys.modules` after
importing `reading_grounding_loop`; `:1068` detects the gap, `:1078` flags it, no branch reaches
a source. GAP = missing TRANSLATION LAYER (lookup CONCEPT-level, reading LEMMA-level). Registry
misleads: 6 rows say `WIRED` + `WIRED_BUT_NOT_PIPELINE_REACHABLE`.

## LEGACY FOUNDATION MOSTLY EMPTY
3,544 GROUNDED_MEANING rows: 65.7% self-referential tautologies `(X,GROUNDED_MEANING,X)`,
reproduces on recount; >=76.5% contentless/wrong-category; ~10% over-stemmed, unfixed. All from
the READING LOOP, none from the extractor -- `notes/foundation_contents_audit_`,
`notes/stemmer_corruption_` (both `_2026-08-13.md`).

## OPEN -- unresolved at compaction
(a) A DEFAULT-OFF change is NON-NEUTRAL: output moved 384 -> 386, all three self-tests passing;
anchor-pool hook is prime suspect BY ELIMINATION, its diff UNREAD.
(b) Live parser loads RICH-TRAINED weights into the BASE class; `RichArcParser`/`_arc_ids_rich`
exist NOWHERE in `hdlab/`; UAS unmeasured -- the structured-comparator 0/50 null rests on it
and is UNINTERPRETABLE.
(c) `exp_wire_definitional_v1` in flight (see RUNNING); gates TOP ITEM.
(d) 42% of the glass-box evidence trail is UNRECOVERABLE (`reading_grounding_loop.py:1382`).

## TODAY'S AUDITS -- `notes/*_2026-08-13.md` (Glob); key ones cited inline above.

## DO NOT REDO -- NEVER-TRIM -- numbers + criteria: `notes/STATUS_LESSONS.md` 1-22, C1-C4
All CLOSED; open the companion before re-proposing any. 1 intersection-over-argmax; 2 the "40%
ceiling"; 3 syntactic bootstrapping as a NEXT STEP; 4 F2 freq-corrected pool (revival criterion);
5 same-sentence cosine/PMI; 6 FHRR superposition for the 50-pair audit; 7 PBV; 8 read-out cell vs
v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 sensorimotor norms (SHELVED, revival
criteria); 12 context-conditioned sense selection v2; 13 minimum-grounded-basis derivation;
14 `genuine_cross_source_corroboration_v1` (source thinness, NOT mechanism);
15 `exp_combined_dictionary_consequence_word_learning_tool_v1`; 16 "the context vector is noise";
17 co-occurrence as the explanation; 18 role-bound structure alone; 19 frontmatter
`isolation:`/`background:`; 20 WIRING THE VOTING MECHANISM (0.0248, below blind union 0.0413 and
scramble floor 0.0496; no correctness measure); 21 HAND-SCORING ANY MEANINGFUL DELTA at
1-3%, esp. `blind_sample.json` in `data/exp_anchor_pool_expansion_v1/` (`QUALITY_CLAIM: NONE`);
22 THE 2-HOP BRIDGES (ceiling ~ its scramble floor). CORRECTIONS C1-C4: availability-binds-first
(WRONG); CLIP visual grounding is NOT a glass-box violation (rule bars LLMs from runtime
inference, not building the seed); the 94% has NO floor; DGProjection fixes interference, not
equidistance.

## STANDING DISCIPLINES -- NEVER-TRIM -- full text: `notes/STATUS_LESSONS.md`
1. DO NOT GATE A CELL ON A HAND-SCORED MEANINGFUL DELTA WHILE THE GENERATOR SITS AT 1-3% M.
   Cost TWO whole experiments, both UNDERPOWERED BY FLOOR: `exp_grounding_quality_readout_v1`
   (3 M rows/100, max |delta| 0.06, inside its own NULL band) and `exp_structured_comparator_v1`
   (1 M row, max |delta| 0.02, 5.5x below its own declared min-detectable -- after a prereg
   claiming to have FIXED the first defect). "Only CONTROL is floor-pinned so TREATMENT is free
   to rise" restates H1; it is not a power argument. Until the generator clears ~10% M, gate on
   KNOWN-ANSWER RECALL or a MECHANISTIC discriminator with range by construction. Cites:
   LESSONS discipline 1.
2. SERIALIZE MEASUREMENT vs CODE CHANGE (2x): never audit/experiment while another agent may
   edit code it depends on, incl. transitive deps -- a racing edit describes no single repo
   state. `notes/measurement_layer_drift_2026-08-13.md` sec.8.
3. A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night): propose/verify a
   metric; store/classifier a stemmer; cert/code a bug; tests/witnesses a naming blind spot.
   Consistency is not evidence. `notes/shared_flaw_invisibility_2026-08-13.md` (P1-P6).
4. ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM. 3 audits in one day (08-13)
   judged a superseded/wrong artifact (S8 vs dead `concept_encoder.py`; a WIRE row pointed at a
   HARD_FAIL cell; `hippocampal_encoder` FAITHFUL quoted w/o its own HARD_FAIL cell). Full text:
   `notes/STATUS_LESSONS.md`, `notes/encoder_lineage_final_2026-08-13.md`.

## WHAT IS RUNNING / BLOCKED
- `data/exp_wire_definitional_v1/` RUNNING detached, PID 30436 (verified live). Arms OFF/ON/
  SHUFFLE written; FREQMATCH mid-run at chunk 31/228. Do NOT touch, kill or stage it -- it gates
  the TOP ITEM.
- `data/exp_anchor_pool_expansion_v1/` FINISHED (PID 9260 gone, `metrics.json` written); verdict
  above; its `blind_sample.json` is DO-NOT-REDO 21, do not hand-score.
- `data/exp_structured_comparator_v1/probes/` and `CLAUDE.md` -- concurrent agents may write;
  never stage either.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk, NO BACKUP.
- Merge to `origin/main`: USER AUTHORIZATION required (branch push itself is done).
