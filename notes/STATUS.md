# STATUS

AS OF 2026-08-13 late | branch `dataprep/mcguffey-graded-corpus` | HEAD 0db7cfdaa+this |
**58 COMMITS AHEAD OF origin (a37b8abeb), UNPUSHED -- pushing needs USER AUTHORIZATION.**

Rewritten in place every session, never appended. Hard cap 6KB. Follow every pointer; do not
trust this summary.

## THE ONE-PARAGRAPH POSITION
Two paths diverged tonight. EXTRACTION (a hand-written parser SUPPLYING facts) works: 94%
correct. READ-OUT (what the substrate RECOVERS from its own representation) does not: 1-3%
MEANINGFUL, with five candidate explanations tested and eliminated. The surviving lead is that
the bottleneck is DOWNSTREAM of feature selection. Growth stays PAUSED.

## EXTRACTION PATH -- WORKING
- **v6.2 predicate recovery: 94% MEANINGFUL**, blind single-judge, n=50 of arm n=221
  (`notes/director_handscore_predicate_v62_2026-08-13.md`). Trajectory 70% -> 94% across
  v6/v6.1/v6.2 (5e188ac1f, 405a25817).
- **221 facts BANKED** into `data/foundation_provenance_v1/` with `pipeline=
  DEFINITIONAL_EXTRACTOR` provenance behind a gate (b8d98509e). The canonical legacy store was
  read-only throughout and is **BYTE-IDENTICAL**; the 221 are rebuildable from committed inputs
  (`predicate_facts_v62.jsonl`, 221 lines, tracked at 5ea354285) --
  `notes/foundation_reproducibility_2026-08-13.md`.
- Licenses ONLY "a parser hands the store a correct fact ~94% of the time on this corpus".
  **NOT** comparable to any read-out score; never place the two side by side.
- **GROWTH REMAINS PAUSED** otherwise, until read-out grounding quality holds.

## READ-OUT PATH -- 1-3% MEANINGFUL, FIVE ROUTES ELIMINATED
Three independent blind hand-scores, all 1-3% MEANINGFUL / ~10-24% RELATED / 73-90% NOISE.
- Read-out stabilisation (F1+F3): **NULL, floor-limited.** 3% M, delta +0.02, max |d| 0.06.
  `notes/director_handscore_readout_v1_2026-08-13.md`.
- Textbook corpus swap: **REFUTED.** Textbook arm **0/50 MEANINGFUL** vs news 4%; the prior
  n=17 "bio 52.9% vs news 16.1%" did not replicate (30.0% vs 24.0%, p=0.6529).
  `notes/director_handscore_text_vs_mechanism_2026-08-13.md`.
- Plain co-occurrence AS THE EXPLANATION: **refuted.** either_top1 only 0.04 (textbook) /
  0.12 (news) -- COOC_DOES_NOT_EXPLAIN / COOC_PARTIAL. Meaning-free, but not a sentence-window
  PMI table. (Same note, RECONCILIATION section.)
- Sensorimotor anchoring: **SHELVED** -- a filter cannot create meaning; coverage was never the
  blocker. `notes/sensorimotor_anchoring_scope_2026-08-13.md`.
- Role-bound dependency structure alone: **NULL** (0% vs 2%, delta -0.02) but it **DID bind
  mechanically** (argmax disagree 97.80%, cooc agree top5 0.2552 -> 0.0749, DIVERGED).
  `notes/director_handscore_structured_comparator_2026-08-13.md`, 0db7cfdaa.

## THE BANKED LEGACY FOUNDATION IS MOSTLY EMPTY
`notes/foundation_contents_audit_2026-08-13.md` (recomputed off disk, 3,544 GROUNDED_MEANING
rows): **>=76.5% demonstrably contentless or wrong-category** (2712/3544), of which **65.69%
are self-referential tautologies `(X,GROUNDED_MEANING,X)`** (2328). Separately ~10% of store
subjects are over-stemmed corruption from a pre-fix lemmatiser
(`notes/stemmer_corruption_2026-08-13.md`, no fix applied -- that is its own one-variable
change). **All of it came from the READING LOOP. None came from the extractor.**

## THE OPEN LEAD -- TOP ITEM
On `banana`, the structured comparator isolated **`(^nsubj, fruit)` -- the CORRECT hypernym --
and the arm still scored 0/50.** The right feature was selected and the system still did not
output it. **The bottleneck is DOWNSTREAM of feature selection**, not in the representation or
the feature alphabet -- this reframes every prior "the vector is the problem" read. Trace IN
PROGRESS -> `notes/downstream_bottleneck_trace_2026-08-13.md`.

## STANDING DISCIPLINES ADDED TONIGHT
1. **SERIALIZE MEASUREMENT vs CODE CHANGE** (happened 2x). Never dispatch an audit/witness-run/
   experiment while another agent may write code it depends on, including TRANSITIVE deps -- a
   measurement racing an edit describes no single repo state.
   `notes/measurement_layer_drift_2026-08-13.md` sec.8.
2. **A CHECKER THAT SHARES A FLAW WITH THE THING IT CHECKS MAKES THE FLAW INVISIBLE.** Four
   instances in one night: propose/verify share one metric; store/classifier share one stemmer;
   certification/code share one bug; test suite/witnesses share a naming blind spot. Consistency
   is not evidence. `notes/shared_flaw_invisibility_2026-08-13.md` (P1-P6 practices).
3. **DO NOT GATE A CELL ON A HAND-SCORED MEANINGFUL DELTA WHILE THE GENERATOR FLOORS AT 1-3%.**
   The comparator's max attainable |delta| was 0.02 against its own declared min-detectable 0.11.
   "Only CONTROL is floor-pinned" is a restatement of H1, not a power argument.

## CERTIFICATION IS NOW HONEST
`verification/test_all_witnesses_exit_clean.py` runs **27 witnesses** and asserts exit codes:
**29 passed / 0 failed** (27 + 2 self-checks), c6279d2eb + 1421c21db. Five witnesses were STALE
PINS (current values HIGHER); accumulating counts are now `>=` floors so improvement passes and
regression fails, with exactness KEPT where it is the property under test.
`notes/uncollected_witness_audit_2026-08-13.md`, `notes/false_certification_goal_typing_2026-08-13.md`.

## DO NOT REDO
Intersection-over-argmax; the "40% ceiling" (was term corruption, v5 -> 64%); syntactic
bootstrapping as a NEXT STEP (0 verb defs in 2092 facts, extractor is noun-only --
`notes/verb_definition_gap_2026-08-13.md`); F2 frequency-corrected pool (retention artifact);
same-sentence cosine / PMI as quality signals; FHRR superposition for the 50-pair audit; PBV
(HARD_FAIL, P1 0.286 vs 0.60); scoring a read-out cell against v5's 64%; agent frontmatter
`isolation:` (ignored) and `background:` (fails the whole definition to load).

## BLOCKED / DO NOT TOUCH
- `data/exp_structured_comparator_v1/probes/` -- concurrent agent writing; never staged.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk, no backup.
- Origin has the canonical-store tarball but NOT the scripts or the 221 facts. Push is the fix
  and push needs the USER.
