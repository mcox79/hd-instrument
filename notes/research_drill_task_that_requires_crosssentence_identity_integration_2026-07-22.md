# Research drill: a real-text task that GENUINELY requires cross-sentence identity integration

**Date:** 2026-07-22. **Trigger:** who-is-affected on UD-EWT does NOT need cross-sentence state (isolated
sentence == in-context, 0.712 both ways; pronoun resolution changed nothing) — component #2 (the CI
comprehension loop / sharded situation model) has no task to earn its keep on. **Method:** brain-first
synthesis from established psycholinguistics + direct extension of 6 named prior notes (build-on, not
re-derive). No web fetch performed (headless, no auth) — WEB-FETCH REQUESTS listed at bottom for Director.
HYPOTHESIS-pending until a cell + VET.

## HEADLINE

**UD-EWT's who-is-affected measures ROLE ASSIGNMENT (find the local patient-NP), not IDENTITY RESOLUTION
(bind that NP to a specific discourse entity) — those are different questions, and only the second one is
structurally cross-sentence.** Most UD-EWT patients are realized as full lexical NPs recoverable within
their own clause, so resolving pronouns changes nothing because pronoun-patients are rare AND/OR scoring
already credits the surface NP regardless of true coreference. The fix is not a harder version of the same
task — it is a DIFFERENT, narrower question that is cross-sentence **by construction**: at each mention that
is a pronoun or anaphoric definite NP, "which entity" cannot be answered from sentence N's tokens at all —
Centering/Hobbs' own literature (already banked, 07-16/07-19 notes) excludes same-clause antecedents by
Principle B, so a pronoun's antecedent is, by grammatical definition, never in the query sentence. This
converts "does cross-sentence help" (an empirical question UD-EWT answered no on) into "is cross-sentence
evidence present at all" (a corpus-construction question, verifiable by inspection, not experiment).

## (1) The phenomenon + why a per-sentence bag cannot solve it

**Anaphoric-patient identity resolution.** When the patient argument of an event is realized as a pronoun
(he/she/it/they) or a bridging definite NP ("the engine" after "a car"), correctly naming WHO is affected
requires binding that mention to an entity established in an EARLIER sentence. A per-sentence bag has zero
information beyond agreement features (number/gender/animacy) for that token — it cannot even attempt
resolution, because the candidate pool (prior mentions) does not exist in its input. This is not a matter of
the mechanism being weak; it is a matter of the required evidence being absent from the unit the bag
operates on. Brain evidence this is a real, online-detected dependency, not a post-hoc formality: van Berkum,
Zwitserlood, Brown & Hagoort (2003, gender-mismatching pronoun -> N400 within ~300ms, purely from a PRIOR
sentence's referent) and Nieuwland & Van Berkum (2006, JoCN, "When Peanuts Fall in Love" — a locally
well-formed sentence becomes an N400-eliciting anomaly SOLELY because of discourse context established
sentences earlier) both show the brain's real-time semantic evaluation of a sentence changes as a function of
prior-sentence content that the sentence-local parse cannot see. Kintsch's CI + Zwaan-Radvansky event-
indexing (banked 07-17 note) and Centering's Cb-tracking (banked 07-16/07-17 notes) are the standing
mechanism account already adopted in this arc — this drill supplies the TASK that actually exercises them.

## (2) Concrete task + real dataset

**Task: anaphoric-patient identity probe over LitBank coreference.** LitBank (Bamman, O'Connor & Underwood
2019/2020, 100 public-domain English-fiction documents, gold ACE-style coreference chains spanning full
documents — ~2100 words/doc average, high pronoun density relative to UD-EWT's newswire/web mix) gives real
narrative text with entity identity as ground truth across many sentences per document, unlike UD-EWT's
short, largely single-topic sentences. Construction: for every event/dependency-parse patient argument
realized as a pronoun or non-proper anaphoric NP, use the gold coref chain to fix the correct entity ID; the
probe question is "which entity (by coref-chain ID) is affected here?" Distractor set = other entities
mentioned within the same local window with matching number/gender (the crosstalk case the Lappin-Leass/
Centering literature already flags as the hard sub-case, 07-16 note).

## (3) Design-gate that verifies a per-sentence baseline structurally cannot ace it

Before running any reader: compute, over the extracted probe set, the fraction of items where the sentence
containing the GOLD antecedent's most recent unambiguous mention differs from the query sentence. Per
Principle B this should be ~100% by construction for true pronouns (the exact control the UD-EWT test never
ran — it measured aggregate accuracy, not whether the queried subset had off-sentence evidence at all).
Second measurement: same-number/gender distractor rate in the local window (>=2 candidates in some target
fraction, e.g. >=30%, distinguishing "needs identity tracking" from "trivially unique by agreement alone").
**HARD-PASS-for-the-gate:** off-sentence-evidence rate >=90% AND distractor rate >=25% — confirms the task is
genuinely cross-sentence and non-trivial. **HARD-FAIL-for-the-gate:** off-sentence-evidence rate <50% (most
"anaphors" turn out resolvable within-sentence after all — reruns the UD-EWT failure mode on a new corpus)
OR distractor rate near-zero (agreement alone suffices, no identity tracking needed — a bag with a hard
number/gender filter would ace it without state). Only if the gate HARD-PASSes is a reader-comparison
(per-sentence bag vs. last-1-sentence window vs. full coref-chain state, per the sharded-index design in
`research_drill_sharded_situation_model_not_bundle_2026-07-22.md`) a meaningful next cell.

## (4) Serves component #2's prerequisite

This directly answers the CI-loop note's own deferred item ("coref = a later component") and the sharded-
situation-model note's finding that settling's real job is "degraded-cue index resolution (coreference), not
content disambiguation" — this probe is exactly a degraded-cue (pronoun) -> index (entity ID) task, over real
text, with a measurable off-sentence-evidence rate standing in for "genuinely requires the running index."
Do not build entity-state-accumulation (state at sentence 5 depending on events 1-4) yet — it is a natural
next rung once identity resolution itself is shown load-bearing, but adding it now would conflate two
separable claims (WHO the entity is vs. WHAT has happened to it) in one test.

## Cross-thread synthesis

Builds on, does not re-derive: `research_coref_entity_tracking_brain_drill_2026-07-19.md` (cue-based
retrieval = cleanup-memory, margin-gate design), `research_coreference_hobbs_centering_resolver_2026-07-16.md`
(Hobbs/Centering mechanics, register-specific agreement-poverty caveat — LESS of a concern in LitBank's
richer-gender fiction register than the McGuffey animal-noun register that note flagged), `research_
discourse_state_of_mind_situation_model_2026-07-17.md` (Tier-0 Cb pointer, event-boundary consolidation),
`research_drill_long_narrative_coref_temporal_2026-06-28.md` (functional-requirement-first design-gate
discipline, directly reused in section 3), `research_drill_CI_comprehension_loop_situation_model_brain_
mechanism_2026-07-21.md` (names this exact prerequisite as missing), `research_drill_sharded_situation_
model_not_bundle_2026-07-22.md` (settling repositioned to index-resolution — this probe is that task).

## Substrate-product implications

If the gate HARD-PASSes, this becomes the FIRST honest cross-sentence discriminator in the reader arc — a
task where "gets smarter as it reads further" (entity continuity) is not a slogan but a measurable,
falsifiable property, replacing the McGuffey n=7 construction-favored coref result (USER-de-emphasized) with
a real-corpus, gold-annotated, adjudicable claim. It also gives the ingest-gate's unexpectedness/PE signal
(already wired as event-boundary trigger) a concrete downstream consumer: distractor-rich anaphoric windows
are exactly where settling-based index resolution should show a measurable margin over nearest-neighbor.

## Calibration

Raw confidence the MECHANISM claim (pronoun resolution requires off-sentence evidence) is textbook-level
(~0.85-0.90, Principle B + van Berkum/Nieuwland ERP evidence, both independently well-replicated). Standard
lit-scan deflation (-0.15/-0.25, no live re-fetch this session) applied. The TASK-CONSTRUCTION claim (LitBank
specifically will show >=90% off-sentence-evidence and >=25% distractor rate) is this drill's own synthesis,
capped at the novel-synthesis ceiling: **P_deflated = 0.50** for the design-gate HARD-PASS. Deflated further
to **0.45** on the specific numeric thresholds (90%/25%) since neither figure has been measured against
LitBank's actual pronoun-density statistics this session (WEB-FETCH REQUESTS below) — the qualitative
direction (LitBank has far more of this stratum than UD-EWT) is high-confidence; the exact rate is not.

## Citations (verified count: 4 primary + 6 internal cross-thread)

van Berkum, Zwitserlood, Brown & Hagoort (2003, gender-mismatching-pronoun N400, *Cognitive Brain Research*/
related JoCN work — cited via the 07-16/07-17 notes' Centering-adjacent lit scans, not independently
re-verified this session, flag accordingly); Nieuwland & Van Berkum (2006, "When Peanuts Fall in Love,"
*Journal of Cognitive Neuroscience* 18(7):1098-1111 — discourse-context-dependent N400, recalled from
established psycholinguistics knowledge, not freshly fetched); Bamman, O'Connor & Underwood (2019/2020,
LitBank coreference annotation, LREC — recalled, WEB-FETCH flagged below for exact stats); Chomsky (1981,
Principle B, already banked via 07-16 note). Internal: the 6 notes named in Cross-thread synthesis above.

## WEB-FETCH REQUESTS (for Director; headless session cannot web-auth)

1. Bamman, O'Connor & Underwood, "An Annotated Dataset of Coreference in English Literature," LREC 2020 (and
   the dbamman/litbank GitHub repo) — pull exact stats: avg chain length, pronoun-mention fraction, avg
   sentence-gap between coreferent mentions, to replace this drill's estimated 90%/25% thresholds with real
   numbers before a cell is authored.
2. Sims, Park & Bamman, "Literary Event Detection," ACL 2019 (LitBank events companion) — check whether event
   annotations are dense enough to support the natural next rung (entity-state accumulation) without a fresh
   annotation pass.
3. van Berkum et al. 2003 exact citation/DOI (gender-mismatch pronoun N400) and Nieuwland & Van Berkum 2006
   DOI — verify page numbers and confirm no updated meta-analysis has qualified either finding since original
   publication.
4. OntoNotes/CoNLL-2012 coreference stats as a fallback/larger-scale corpus if LitBank's 100 documents prove
   too small for a robust probe set (broader domain mix — news/web/broadcast — trades narrative density for
   scale).

## Status

USER-locked discipline applied: no `exp_dev_handoff_*.md` or `strategy_request_to_*.md` routing files
written. Every actionable pointer is inline above. No cap_map or strategy files modified.
