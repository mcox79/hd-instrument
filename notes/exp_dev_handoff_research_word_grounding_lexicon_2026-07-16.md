# exp_dev hand-off — research: word grounding + lexicon structure-content unification

**Filed-by:** research (Sonnet lit-scan x3 + synthesis), 2026-07-16.
**Trigger:** `notes/research_word_grounding_lexicon_structure_content_unification_2026-07-16.md` — full findings, falsifiable predictions, and cited mechanism recipe live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — but re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's section (b)/(c) has the falsifiable predictions and HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## SUPERSEDING UPDATE (2026-07-16, same-day Director steer) — anchor to CoDEx, not a generic placeholder foundation

Director directed this hand-off to anchor against the REAL, already-on-disk CoDEx claim-validity foundation (`data/codex_claimvalidity/raw/`, `data/codex_m_claimvalidity/raw/`), not an abstractly-described "small foundation graph." Verified on disk before writing this: `train.txt` = 32,888 tab-separated `Q-id / P-id / Q-id` triples, 42 unique relations, top-frequency `P106` occupation (10,197), `P530` diplomatic-relation (5,563), `P463` member-of (4,985), `P27` citizenship (1,648), `P1412` languages-spoken (1,477). `test_negatives.txt`/`valid_negatives.txt` (real pre-built negative triples) already exist — no need to construct a scramble control from scratch. **No entity2text/relation2text label files exist anywhere in this repo** (searched exhaustively) — CoDEx's public release ships them, but fetching/ingesting them is a real prerequisite for a human-readable cell, flagged as a dependency, not assumed done.

**Honest structural correction to the ORIGINAL anchor candidates below:** CoDEx relations are encyclopedic (occupation, citizenship, languages-spoken), not early-reader action verbs (sees/runs/likes) — there is no "cat sees dog" claim in CoDEx. The smallest cell must use CoDEx's own relation vocabulary as the SVO verb (best surface-SVO fit: `P1412` speaks — clean transitive verb; `P27` is-citizen-of; `P106` has-occupation) with named entities (Q-ids) as subject/object, NOT literal Dolch nouns. This is a SEPARATE grounding thread from the Dolch/early-reader curriculum (`research_early_reader_language_acquisition_curriculum_2026-07-16.md`) — both are real, but they do not share a vocabulary, and joining them is a later, third step, not assumed here.

## Anchor candidates (rank-ordered) — CoDEx-concrete version supersedes the original abstract version

1. **[Primary] Smallest grounding-loop test — learned lexicon over CoDEx entity/relation vectors, feeding the proven role-filler scaffold, verified against the REAL CoDEx graph (non-circular, external ground truth).**
   - Concrete spec: ~20 entity word-forms (Q-ids) + 3 relation word-forms (`P1412` speaks, `P27` is-citizen-of, `P106` has-occupation), each assigned a fixed hypervector (same construction as the additive_map's existing concept vectors). Parse SVO sentences built from real CoDEx triples; bind `SUBJECT ⊗ v(entity) + RELATION ⊗ v(relation) + OBJECT ⊗ v(entity)`; unbind and check the recovered triple against `train.txt`/`test.txt`/`valid.txt`/`*_negatives.txt`.
   - **4 arms required:** (i) BOUND-REAL — held-out test/valid triples, checks nearest-neighbor unbind against true CoDEx rows; (ii) RANDOM-phasor control (existing negative, already known to fail); (iii) MEMORIZED-overfit control — same lexicon, evaluated only on train-seen triples, isolates rote lookup from genuine recovery; (iv) MUST-FAIL SCRAMBLE — query the pre-built `*_negatives.txt` real negative triples, BOUND-REAL must reject ≥90% of them (fairness/vacuousness gate — a system that says "yes" to everything is worthless).
   - **HARD-PASS:** BOUND-REAL held-out accuracy beats a frequency/most-common-object baseline by ≥20 points, is within ≤10 points of MEMORIZED's accuracy (genuine generalization, not overfit), AND correctly rejects ≥90% of `*_negatives.txt` scrambled triples.
   - **HARD-FAIL:** BOUND-REAL indistinguishable from RANDOM control, OR scores negatives as true at a rate indistinguishable from positives (vacuous), OR held-out accuracy collapses >20 points relative to MEMORIZED (rote lookup, not composition).
   - Tier hint: risk concentrated in the lexicon-learning/vector-assignment step and in the entity-label prerequisite (Q-id/P-id are glass-box-legal but unreadable without label files) — the verification-against-real-external-data step makes this a genuine (not construction-proof) result if it passes.
   - Why now: closes structure (proven scaffold) with content (already-verified-elsewhere CoDEx claim-validity foundation) via a check against real external ground truth, not a self-consistency check.

2. (Original abstract Dolch/early-reader anchor candidates below are RETAINED as a separate, later thread — do not merge with the CoDEx thread above without an explicit third design step joining the two vocabularies.)

### Original anchor candidates (Dolch/early-reader — separate thread, not superseded, just sequenced behind CoDEx per Director steer)

1. **[Primary, Dolch thread] Smallest grounding-loop test — learned lexicon feeding the proven syntactic scaffold, unbind-to-foundation-fact retrieval.**
   - Anchor pointer: research note section (b) "Cheap decisive test" + section (4) "The smallest grounding step."
   - Substrate-product reading: this is the first test of whether the language module's parse can YIELD an actual foundation triple rather than a syntactically-valid-but-meaningless structure — directly operationalizes the structure-content-factorization thrust as a running artifact, not just a design note.
   - Tier hint: novel-synthesis for the lexicon-learning component (capped P=0.35-0.42 per note); the binding-algebra component itself is well-precedented (TPR/HRR/SPA), so this is a legitimate NEAR-TERM cell, not a speculative one — the risk concentrated entirely in the lexicon-learning update rule, which is cheap to smoke-test (8-12 words, tiny paired corpus).
   - Why now: unifies two live arcs (language-structure scaffold + foundation-content build) that have been developing in parallel without a concrete join point; this closes that gap with the smallest possible artifact.

2. **[Secondary, gates Prediction 3] Syntactic-role-restriction ablation on the lexicon-learner.**
   - Anchor pointer: research note section (c) Prediction 3 + section 3 mechanism #3 (syntactic bootstrapping).
   - Substrate-product reading: cheap ablation (same corpus, same lexicon-learner, toggle role-eligibility restriction on/off) — answers whether the foundation's existing edge-type/role tagging is usable as a bootstrapping signal for FREE, before any new tagging infrastructure is built.
   - Tier hint: cheap, same-day relative to anchor 1 — should run alongside or immediately after, not as a separate cycle.
   - Why now: directly informs whether investment in richer role/category tagging on the foundation graph is justified before scaling the lexicon past the initial closed loop.

3. **[Tertiary, only if anchor 1 HARD-PASSes] Fast-mapping + mutual-exclusivity incremental-vocabulary-growth extension.**
   - Anchor pointer: research note section (e) implication #5 + section 3 mechanism #4.
   - Substrate-product reading: scales the lexicon past the initial 8-12-word closed loop toward the fuller Dolch tiers scoped in `research_early_reader_language_acquisition_curriculum_2026-07-16.md`, reusing the same update rule.
   - Tier hint: defer until anchor 1's HARD-PASS/HARD-FAIL result is in — building incremental-growth machinery on top of an unvalidated core mechanism is premature.
   - Why now: not yet — sequenced explicitly behind anchor 1.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_word_grounding_lexicon_structure_content_unification_2026-07-16.md` — this drill's full findings, decisive test, falsifiable predictions, citations.
- `notes/research_early_reader_language_acquisition_curriculum_2026-07-16.md` — the graded early-reader vocabulary/grammar curriculum this lexicon-loop should eventually scale into (Dolch tiers, Simple-Wikipedia grammar ladder, Tolerance Principle exemplar-budget formula).
- `notes/research_grounding_subsumed_by_measured_attribute_foundation_instrument_grounding_reachability_audit_2026-07-15.md` — why instrument/relational grounding is a legitimate channel for this substrate (philosophy-of-measurement argument); corroborated independently by this drill's symbol-grounding lit-scan.
- `notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md` — the hub-node / multi-attribute-fusion architecture already scoped; this drill's lexical-spoke finding is a direct, low-cost extension of that same hub-node option, not a new subsystem.
- `project_additive_map_builder_integration_endgame_functional_plus_strict_via_shared_api_2026-07-13` (memory ref) — the shared foundation-concept-vector API the lexicon table should target, so the SAME vectors serve as both reasoning-architecture fillers and language-scaffold fillers.
- The syntactic-scaffold probe result referenced in this drill's trigger (glass-box VSA parses/generates/compositionally-generalizes SVO with random phasors) — locate via most recent early-reader/SVO-probe artifact in the session's own working state; this hand-off does not re-cite its exact filename since it was referenced only descriptively in the dispatching prompt, not independently located this cycle.

---

## Contract section

- Cell-author owns: concrete pre-reg (exact word list, exact foundation-concept mapping, exact held-out-split construction for the LEXICON-MEMORIZED vs LEXICON-LEARNED arms), smoke gate, dispatch.
- Must implement all three arms named in the research note's decisive test (LEXICON-LEARNED, RANDOM-control, LEXICON-MEMORIZED-overfit-control) — the overfit control is not optional; it is the only thing distinguishing genuine compositional recovery from rote pair memorization.
- Must report per-arm nearest-neighbor retrieval accuracy against the foundation's OWN concept-vector space, not a proxy metric.
- HARD-PASS/HARD-FAIL bars are pre-registered in the research note section (b)/(c) — do not loosen them at pre-reg time without flagging the deviation explicitly in the pre-reg file.

## Autonomy declaration

Research does not prescribe exact code, exact foundation-concept selection, or exact corpus size beyond "8-12 words, tiny paired corpus" as an order-of-magnitude anchor. Cell-author has full autonomy over implementation detail, exact word/concept selection (subject to existing in the small foundation graph or being trivially instantiable), and smoke-scale parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note.
