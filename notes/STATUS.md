# STATUS

AS OF: 2026-08-12T~22:00Z (testbed rewrite) | branch dataprep/mcguffey-graded-corpus | commit af8e286ae (local; origin at 00e7c4221, 13 commits behind, not pushed)

Rewritten in place every session. Never append -- if it doesn't fit in 6KB, it's an
evidence-doc claim with a pointer, not content that belongs here.

LEDGER CONVENTION: any multi-step arc keeps `notes/ledger_<arc-slug>.md`; first line names
the arc, one line per completed step with its commit hash; after compaction, the ledger +
`git log` outrank recollection. Active: `notes/ledger_grounding_quality_2026-08-12.md`.

## WHAT IS TRUE NOW (every claim sourced -- follow the pointer, don't trust this summary)
- v1 foundation HARD_PASS was OVERSTATED (circular claim-1: grounding target selected by
  same-sentence cosine, then tested for co-occurrence in that same text; 2/4 band conditions
  cannot fail by construction). 65.7% (2328/3544) of GROUNDED_MEANING facts were
  self-tautologies `(X,X)`. -> `notes/landed_vet_foundation_validation_2026-08-12.md`,
  `notes/foundation_grounding_sample_2026-08-12.md`
- Root cause: `canonicalize()` returned the lemma as its own no-match sentinel;
  `checkpoint()` banked that sentinel as fact. Fixed 04b922c0e.
- v2 corrected run (634 grounded, tautologies/closed-class -> 0, provenance 0->100%,
  MEASURED@`data/exp_reading_grounding_loop_cycle3_groundingfix_v1/metrics.json`): B3
  fresh 50-pair hand-score 8% MEANINGFUL / 26% RELATED / 66% NOISE -- FAILS the pre-registered
  <0.15 floor (`preregs/2026-08-12_grounding_quality_fix_v1.md:24-26`).
  -> `notes/definitional_grounding_v3_2026-08-12.md` sec 1
- v3 definitional-sentence extraction (NEW signal: copula/appositive/glossary-colon/called/
  refers-to, extracted from the corpus text itself, not a dictionary) built + run: 1751 facts
  (1749 not produced by the distributional path). Cell verdict on disk is still
  `STRUCTURAL_PASS_PENDING_B3` (`data/exp_definitional_grounding_v3/metrics.json`) -- the
  DEF-arm hand-score (38% MEANINGFUL/18% RELATED/44% NOISE) and the DIST_LOWINFO-control
  score (reported as 8/26/66, matching DIST_ASIS baseline) are director-reported in this
  session's conversation but are **NOT YET WRITTEN to metrics.json or to the notes doc**
  (`notes/definitional_grounding_v3_2026-08-12.md` sec 4 explicitly ends "NOT SCORED HERE").
  Treat the 38/18/44 number as unpersisted until it lands on disk.
  Pre-reg: `preregs/2026-08-12_definitional_grounding_v3.md` (HARD_PASS >=35% + >=200 facts).
- Islanding hypothesis (store can't hold multiple senses) REFUTED in code + on landed data:
  FLAGGED facts stay live+queryable (`hd_fact_store.py:66`); re-banking 1751 v3 facts gives
  1751 live, 288/1316 subjects (21.9%) already hold >1 sense. Real gap = no context KEY for
  sense selection, not storage. FHRR superposition store is NOT a validated organ (lives in
  `experiments/exp_bootstrap_fhrr_superposition_fade_v3.py`, unregistered, cell verdict
  HARD_FAIL_PARTIAL). -> `notes/wire_reader_to_meaning_organs_2026-08-12.md`
- `definitional_extraction.py` confirmed DISJOINT/novel (not a rebuild of the "0.90 extractor",
  which is `exp_stated_entity_fate_reading_extractor_v2_highprecision.py`, a different job).
  -> `notes/reinvention_and_registry_audit_2026-08-12.md`
- Registry, CURRENT disk state (verified fresh this pass, not the pre-registration 107-row
  snapshot): **113 rows** (WIRED 56 / TRAPPED_SHARED 26 / ISLAND 29 / N_A_SHELVED 2) after
  registering 6 modules in 411d2fb6f; unregistered hdlab modules 77->71.
  `hdlab/lexical_similarity.py` (23 consumers) still unregistered, a real gap.
  -> `notes/reinvention_and_registry_audit_2026-08-12.md` sec B
- Infra: 27,079 watchdog ping files archived out of notes/ (35,474 -> 8,408, per `ccbc95a0b`);
  session-start hook injects rules + durability status. Branch pushed to origin through
  00e7c4221 (confirmed via `git merge-base --is-ancestor`); 13 commits since are local-only.

## WHAT IS RUNNING
- Context-conditioned sense-selection experiment (concurrent agent, live): can the substrate
  pick the RIGHT sense given context, on the 288 multi-sense words, against the MEASURED
  random floor mean(1/k)=0.4316. Writing `notes/context_conditioned_sense_selection_2026-08-12.md`
  -- DO NOT TOUCH. Not yet reported.

## NEXT (ordered)
1. That context-conditioned sense-selection result.
2. Persist the v3 DEF/DIST_LOWINFO hand-scores (38/18/44 and 8/26/66) to disk -- currently
   conversation-only, not in metrics.json or the notes doc. Update the cell verdict off
   `STRUCTURAL_PASS_PENDING_B3` once done.
3. Definitional-extractor parse bugs: person/word collisions (`fan`->expert from a person
   named Fan), lists misread as appositives, truncated subjects (`transcription bubble`->
   `bubble`).
4. Speed fix: `familiarity()` rescans the full codebook (~180ms/probe) instead of the existing
   O(1) index.
5. Foundation growth stays PAUSED until grounding quality holds.
6. Close the `lexical_similarity.py` registry gap (23 consumers, unregistered).

## BLOCKED
- DO NOT TOUCH (concurrent session, standing constraint this pass): `hdlab/reading_grounding_loop.py`,
  `hdlab/hd_fact_store.py`, anything under `data/foundation/`,
  `notes/context_conditioned_sense_selection_2026-08-12.md`.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22MB+23MB) exist on one disk only,
  not backed up.
- 71 unregistered hdlab modules triaged (5 true islands -> SHELVE; ~55 mid-tier deferred to
  batched review) but not decided. -> `notes/reinvention_and_registry_audit_2026-08-12.md` sec B.3

## DO NOT REDO
See `notes/director_transition_digest_2026-08-12.md` Section C (Dead Ends). Add: same-sentence
cosine as a grounding-correctness signal (definition-blind, 2.2% pair-link measured); PMI as a
meaning-quality ranking (rewards rare co-occurrence, scores `shed->quirky` above every
meaningful pair); wiring FHRR superposition to move the 50-pair audit (storage representation
is provably invariant to that metric -- fix the extractor, not the store).
