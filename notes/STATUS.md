# STATUS

AS OF: 2026-08-13 late | branch `dataprep/mcguffey-graded-corpus` @ 48a9900c1, PUSHED through
HEAD; `origin/main` is 1233 behind -- merging needs USER AUTHORIZATION.
Rules: `notes/STATUS_SPEC.md` -- READ BEFORE EDITING. Never-trim material (closed
routes, corrections, disciplines): `notes/STATUS_LESSONS.md`, uncapped. Rewritten in place, cap
8192 B. Follow every pointer; don't trust this summary alone.

## POSITION
EXTRACTION works (94%, no floor recorded). READ-OUT does not (1-3% MEANINGFUL). The binding
constraint is SETTLED by pre-registered experiment: the COMPARATOR, not candidate supply. So:
BYPASS the read-out comparator, don't feed it better candidates. GROWTH STAYS PAUSED until
grounding quality holds.

## TOP ITEM -- BYPASS THE COMPARATOR: definitional extraction as direct-bank + verifier
`notes/opportunity_map_2026-08-13.md` ranks candidates by P(acts on a MEASURED-binding
constraint) x magnitude x P(the gain survives its own control). **#1: wire definitional
extraction to bank facts DIRECTLY with an INDEPENDENT verifier** (64% MEANINGFUL vs the
read-out's 8% floor) -- the only item routing AROUND the constraint the anchor-pool cell measured
instead of pushing on it. GATE: in-flight `exp_wire_definitional_v1` reports first. #2: replace
the equidistant basis from a channel INDEPENDENT IN KIND. #3: measure the parser loader (open q
b). `DGProjection` does NOT fix equidistance -- it fixes interference (LESSONS C4).

## READ-OUT PATH -- THE COMPARATOR IS BINDING (settled 08-13)
`exp_anchor_pool_expansion_v1`, one variable = anchor pool size, verdict `COMPARATOR_IS_BINDING`.
Availability 0.199 -> 0.953 while recall@1 moved only 0.0081 -> 0.0333, BELOW its +0.03 floor;
**availability-conditioned recall@1 -0.0060** (negative); co-occurrence agreement ROSE 0.075 ->
0.102. Candidate supply is ELIMINATED as the explanation; the earlier "availability binds first"
reading of the e2e trace is CORRECTED as WRONG -- 386 -> 600 facts is VOLUME, not correctness
(LESSONS C1).
ATTRITION, e2e full corpus (`notes/e2e_substrate_trace_2026-08-13.md`): 16,812 lemmas -> 386
facts = 2.4%; admission alone loses 98.5%; only 6.6% of items reach commit strength. Of 24,939
refusals, 85% below-commit-strength / 14% no-standing-hypothesis. Absent-from-pool 79.0%,
present-but-not-argmax 17.2%, median rank when available 20. Read = 98.4% of wall-clock.
`Library._propose` returns None 24,494x (60.7%) WITH NO LOG ROW.
Three blind hand-scores: 1-3% M / 10-24% RELATED / 73-90% NOISE; 5 routes eliminated (LESSONS
9-11, 17-18).

## EXTRACTION PATH -- WORKING
v6.2 predicate recovery 94% MEANINGFUL, blind single-judge, n=50 of arm n=221 --
`notes/director_handscore_predicate_v62_2026-08-13.md`. Licenses "the parser hands the store a
correct fact ~94% of the time on this arm", nothing comparative: NO floor arm was run (C3).
221 facts BANKED to `data/foundation_provenance_v1/`, rebuildable from
`predicate_facts_v62.jsonl` -- `notes/foundation_reproducibility_2026-08-13.md`.

## MULTI-SOURCE LOOKUP WORKS, NOT WIRED TO READING
`notes/multisource_lookup_wiring_audit_2026-08-13.md` (modules, tests, CSKG). Unreachable
from reading: no lookup organ in `sys.modules` after importing `reading_grounding_loop`; `:1068`
detects the gap, `:1078` flags it, no branch reaches a source. GAP = missing TRANSLATION LAYER
(lookup CONCEPT-level, reading LEMMA-level). Registry misleads: 6 rows say `WIRED` +
`WIRED_BUT_NOT_PIPELINE_REACHABLE`.

## LEGACY FOUNDATION MOSTLY EMPTY
3,544 GROUNDED_MEANING rows: 65.7% self-referential tautologies `(X,GROUNDED_MEANING,X)`,
REPRODUCES EXACTLY on independent recount; >=76.5% contentless/wrong-category; ~10% over-stemmed,
UNFIXED. All from the READING LOOP, none from the extractor --
`notes/foundation_contents_audit_`, `notes/stemmer_corruption_` (both `_2026-08-13.md`).

## OPEN -- unresolved at compaction
(a) A DEFAULT-OFF change is NON-NEUTRAL: output moved 384 -> 386, all three self-tests passing;
anchor-pool hook is prime suspect BY ELIMINATION, its diff UNREAD.
(b) Live parser loads RICH-TRAINED weights into the BASE class; `RichArcParser`/`_arc_ids_rich`
exist NOWHERE in `hdlab/`; UAS unmeasured -- **the structured-comparator 0/50 null rests on it
and is UNINTERPRETABLE.**
(c) `exp_wire_definitional_v1` in flight (see RUNNING); gates TOP ITEM.
(d) 42% of the glass-box evidence trail is UNRECOVERABLE (`reading_grounding_loop.py:1382`).
(e) Encoder lineage under review -- the S8 fault verdict may be on a SUPERSEDED version.

## TODAY'S AUDITS -- all `notes/*_2026-08-13.md`, plus those cited above
`brain_fidelity_subsystems_`, `system_accounting_`,
`grounding_results_accounting_`, `process_rules_`, `subagent_denial_audit_`,
`metrics_overwrite_forensics_`, `uncollected_witness_audit_`.

## DO NOT REDO -- NEVER-TRIM -- numbers + criteria: `notes/STATUS_LESSONS.md` 1-22, C1-C4
All CLOSED; open the companion before re-proposing any. 1 intersection-over-argmax; 2 the "40%
ceiling"; 3 syntactic bootstrapping as a NEXT STEP; 4 F2 freq-corrected pool (revival criterion);
5 same-sentence cosine/PMI; 6 FHRR superposition for the 50-pair audit; 7 PBV; 8 read-out cell vs
v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 sensorimotor norms (SHELVED, revival
criteria); 12 context-conditioned sense selection v2; 13 minimum-grounded-basis derivation;
14 `genuine_cross_source_corroboration_v1` (source thinness, NOT mechanism);
15 `exp_combined_dictionary_consequence_word_learning_tool_v1`; 16 "the context vector is noise";
17 co-occurrence as the explanation; 18 role-bound structure alone; 19 frontmatter
`isolation:`/`background:`; **20 WIRING THE VOTING MECHANISM (0.0248, under blind union 0.0413
AND under its own scramble floor 0.0496; no correctness measure in its cells); 21 HAND-SCORING
ANY MEANINGFUL DELTA at 1-3%, esp. `blind_sample.json` in `data/exp_anchor_pool_expansion_v1/`
(`QUALITY_CLAIM: NONE`); 22 THE 2-HOP BRIDGES (ceiling ~ its scramble floor).** CORRECTIONS C1-C4: availability-binds-first (WRONG); CLIP visual grounding is
NOT a glass-box violation (the rule bars LLMs from runtime inference, not from building the
seed); the 94% has NO floor; DGProjection fixes interference, not equidistance.

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
