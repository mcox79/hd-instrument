# Pre-registration: representation_canonicalization_v1

## Context / motivation

`exp_three_tier_loop_concept_coherence_v1` (commit e3712e8b5, HARD_PASS) solved cross-source
paraphrase corroboration via a GATE: two accumulated context traces are matched POST-HOC at
retain-time by `concept_coherence_score` (shared-in-lexicon-word overlap, graded via
`hdlab.lexical_similarity.concept_similarity`). That is a real, controlled, VET'd win, but it is
a MATCH step bolted onto whatever representation each source happened to produce -- it does not
touch how the fact is REPRESENTED.

USER's deeper principle: "ideas should have the SAME REPRESENTATION no matter how they're
worded." Brain analogy: the ATL amodal semantic hub converts surface/modality-specific form into
one amodal concept; the semantic control network (state-of-mind context) disambiguates polysemous
wordings to the right concept before/during that conversion. This cell tests the DEEPER form:
CANONICALIZE each fact's (subject, relation, object) surface rendering to a canonical concept
representation AT ENCODE TIME, so that two independently-worded sources of the SAME fact produce
the IDENTICAL stored representation and corroborate AUTOMATICALLY (native store-level dedup),
with NO concept_similarity gate-match step required at retrieval.

## Prior-work check (mandatory, per exp_dev discipline)

`bash tools/substrate_query.sh "canonicalize surface form same representation amodal concept
encode time automatic corroboration"` -- top hit cosine=0.3438 (`preregs/2026-07-21_perception_
bridge_scene_vector_digits_v1.md`, entity "Representation"), on inspection an unrelated scene-
vector-classification cell's generic section header ("## Representation"), not substantively
about canonicalizing (s,r,o) surface forms. No relevant prior work at cosine>0.30. This is novel,
additive work building on e3712e8b5, not a rediscovery.

## Mechanism (reuse owned organs, additive only, ZERO edits to any hdlab/ file)

- **Entity canonicalization**: `canon_entity(word, anchors)` -- literal match against a fixed
  known-vocabulary anchor set (the real `via_material`/`whole`/`process` strings already used to
  build the gaps) short-circuits; otherwise fuzzy-collapse via `hdlab.lexical_similarity.
  concept_similarity(word, anchor) >= SIMILARITY_LINK_THRESHOLD` (0.50, REUSED VERBATIM, same
  binarization discipline as e3712e8b5 -- never re-tuned here), binarized so a same-role-different-
  specific-material pair (wood vs coal, measured concept_similarity=0.450 < 0.50) never merges.
  Deny-by-default: OOV or sub-threshold -> the word stays its own literal singleton id.
- **Relation canonicalization + explicit direction handling**: a small hand-authored, documented,
  NOT-tuned-per-pair table (`RELATION_DIRECTION_TABLE`) maps each source template's relation
  marker to one of 4 canonical relation ids (`PART_OF` / `PRODUCES` / `CONSUMES` / `MOVES`; a 5th,
  `CAUSALLY_LINKED`, is declared for the CauseNet axis but NOT exercised this run -- scope
  disclosed below) PLUS whether the surface (subject,object) order must SWAP to reach the
  canonical slot order. CSKG's `"{whole} bridges to {material} via ... MadeOf"` surface order
  (whole, material) SWAPS to canonical (material, PART_OF, whole); the "X composes Y" / "X is
  part of Y" paraphrases are already in canonical order (no swap) -- same underlying fact, two
  structurally different surface orders, must resolve to the IDENTICAL canonical triple. This is
  the direct, at-scale generalization of the task's own worked example ("wood MadeOf cellulose"
  vs "cellulose composes wood").
- **State-of-mind disambiguation**: `hdlab.situation_model_accumulate.RelationRegister` (imported
  verbatim, used exactly as its own docstring intends -- "carry an OPEN-vocabulary concept
  representation" via `bind_filler`/`decode_filler` on `GOAL_ROLE`) accumulates a passage's
  context-word concept vectors (`hdlab.lexical_similarity.concept_vector`) into one FHRR-bundled
  "state of mind" register per episode; an ambiguous surface token with >=2 candidate canonical
  senses is resolved by cosine-matching the accumulated register against each candidate sense's
  anchor concept vector.
- **Representation**: `hdlab.hd_fact_store.HDFactStore` (imported verbatim). Two representations
  are used, deliberately distinguished:
  1. **content-only representation vector** (this cell's own `content_repr_vector`, reusing the
     SAME primitives `HDFactStore._encode_fact` uses internally --
     `hdlab.role_slot_summarizer._bipolar_bind`/`_bipolar_quantize` bound over ONLY `REL`+`ARG0`+
     `ARG1`, via a shared store instance's `EventBundleCodec` for symbol-vector consistency) --
     this is the literal "same idea, same representation" claim: it deliberately EXCLUDES
     `SOURCE`/`TRUST`, which are provenance METADATA about the fact, not part of the fact's
     content/idea. torch.equal on this vector is the strict same-representation test.
  2. **`HDFactStore.store(subject, relation, obj, source, trust)`** (the FULL fact, source+trust
     included) -- demonstrates the OPERATIONAL "automatic corroboration" claim: when a second
     source's canonicalized triple matches an already-stored (subject,relation,object), the
     store's OWN native `_find_same_sr` + object-match logic (an O(1) content-hash of the
     (subject,relation) HD signature, ALREADY built into the organ, never touched by this cell)
     returns `resolution="CONSISTENT_DUP"` with **no concept_similarity gate-match call anywhere
     in the retrieval path** -- corroboration is a side-effect of canonicalize-then-store, not an
     extra matching step.

## Scope (honest, declared before running)

- Real-data population: gaps from `build_gap_set` (via `build_reading_facts`/`reading_vocab`/
  `build_cskg_bridges`, imported verbatim from `exp_state_of_mind_relevance_gather_reasoning_
  union_v1`) with >=2 real per-source waves from `build_genuine_waves` (imported verbatim from
  `exp_three_tier_loop_genuine_cross_source_corroboration_v1`), using ONLY the CSKG (wave0) and
  KB-role-schema (wave2) axes -- **CauseNet (wave1) is OUT OF SCOPE this run** (`do_causenet=
  False`): CauseNet's causal-link axis is semantically DIFFERENT from PART_OF/FATE-role axes (a
  causal pair is not a composition fact), so forcing it onto the same canonical id would itself be
  an over-merge risk; `CANONICALLY_LINKED` is declared in the relation table for architectural
  completeness but not exercised. This ALSO means this cell does NOT reuse the CA3-relevance-
  gather reasoning-eligibility stage (`_eligible_targets`/hop1/hop2/`fresh_kg`) at all -- a
  deliberate scope narrowing (this cell tests representation identity, not reasoning-reachability,
  a different concern from e3712e8b5's own eligibility gate) that also removes the CauseNet-scan
  and CA3-gather compute cost entirely (lighter than the parent cell).
- The prior e3712e8b5 gate-matching mechanism (`ThreeTierLoop`/`TierState`/`consolidation_pass`/
  `schema_consistency_split_half`/`coherence_fn`) is NOT imported, NOT touched, NOT re-run by this
  cell -- "core preserved" is verified by re-running `hdlab.grounding_acquisition_loop.self_test()`
  and `hdlab.prelim_tier.self_test()` (the two organs e3712e8b5 extended) as a pure regression
  check, proving the working gate-matching fallback remains fully intact regardless of this
  cell's own verdict.

## Tests (all can-fail, pre-registered bands BEFORE running)

**T1 -- SAME-IDEA -> SAME REP.** For every real gap with a CSKG wave, canonicalize the real CSKG
text AND a generated "composes"/"is part of" direction-flipped paraphrase of the SAME
(material,whole) pair; assert `content_repr_vector` torch.equal. Same for every real gap with a
KB-role-schema wave, against a generated same-fate paraphrase (produces/generates/yields family
etc, hand table, documented, not tuned). PLUS closed-form near-synonym entity collapse: wood /
timber / log / kindling (identical COMBUSTION_CONSUME_ROLE+COMBUSTION_DOM tags in the ALREADY-
validated lexicon, cosine=1.0) must all canonicalize to the SAME entity id.
`same_idea_match_rate` = fraction of all such pairs (real + closed-form) that match.
**Band: HARD requires `same_idea_match_rate >= 0.90`.**

**T2 -- DISTINCT-IDEA -> DISTINCT REP (mandatory can-fail, checked FIRST).**
(a) wood vs coal, same process+fate (concept_similarity=0.450 MEASURED < 0.50 threshold) must
canonicalize to DIFFERENT entity ids -> different `content_repr_vector` -> both `store()` calls
`CLEAN_STORE`/`detected_conflict=False` (recognized as two distinct, non-conflicting facts).
(b) same material+process, PRODUCES vs CONSUMES fate (KB "produces" vs "consumes") must
canonicalize to DIFFERENT relation ids -> different representation.
(c) real-data scale: the SET of canonical `(material, PART_OF, whole)` triples derived from all
distinct real (material,whole) pairs has ZERO collisions (`len(set) == n_distinct_pairs`).
**Band: HARD requires ALL of (a)/(b)/(c) to hold with zero tolerance** (task-mandated: "A
canonicalizer that merges everything is broken -> HARD_FAIL").

**T3 -- STATE-OF-MIND DISAMBIGUATION (load-bearing test).** 2 ambiguous surface terms wholly OOV
of `hdlab.lexical_similarity.CONCEPT_FEATURES` (MEASURED: `cell`, `bank` both `in_lexicon=False`,
so the base lexicon carries zero prior bias toward either candidate sense) x 4 constructed
episodes each (8 trials total), each episode's context words drawn from real, unmodified
`CONCEPT_FEATURES` entries of the intended domain. WITH state-of-mind context (accumulated via
`RelationRegister.bind_filler`): pick the candidate sense whose anchor concept vector best cosine-
matches the accumulated register. WITHOUT context (ablation): a context-blind FIXED default
(alphabetically-first candidate sense) -- by construction wrong on episodes whose true sense
isn't the default.
**Band: HARD requires `accuracy_with_context >= 0.875` (7/8) AND `accuracy_baseline <= 0.625`
(5/8) AND `(accuracy_with_context - accuracy_baseline) >= 0.25`** -- proves context is load-
bearing (ablating it measurably degrades disambiguation), isolating that state-of-mind helps.

**T4 -- AUTOMATIC CORROBORATION.** For every T1 same-idea pair, the SECOND `store()` call (the
paraphrase, tagged with a DIFFERENT `source`) must resolve `CONSISTENT_DUP` -- corroboration fires
from the store's OWN native (subject,relation) signature + object match, with no
`concept_similarity` call anywhere in the store/query path (that organ is used ONLY upstream, at
canonicalization/encode time, never at retrieval). **Band: `automatic_corroboration_rate >= 0.90`,
mirroring `same_idea_match_rate` (CONSISTENT_DUP requires identical canonical (s,r,o) by
construction, so this should track T1 exactly).**

## Controls

- **no_leak_ok**: every `HDFactStore` instance's `query()` returns `[]` for the relevant subjects
  BEFORE any `store()` call in that group.
- **scramble_control_ok**: the T1 closed-form synonym-collapse (timber/log/kindling -> wood) is
  re-run under a SCRAMBLED `CONCEPT_FEATURES` mapping (same permutation-scramble recipe as
  `hdlab.lexical_similarity.self_test`'s own circularity check, seed=999, reused via that module's
  own `_feature_vectors`/`_concept_vector_from`/`_cos_complex` helpers -- NOT reimplemented).
  **Band: real (unscrambled) collapse rate >= 0.90 (expect exactly 1.0, tags identical) AND
  scrambled collapse rate <= 0.20** -- corrupting the canonicalization signal must collapse the
  same-rep result, proving T1 depends on genuine concept structure, not construction artifact.
  Exact-literal-string matches (e.g. the real-data CSKG-vs-composes-paraphrase pairs, whose entity
  strings are already identical across both renderings by construction) are UNAFFECTED by this
  scramble (they never call `concept_similarity` at all) -- the scramble control therefore ONLY
  and CORRECTLY targets the fuzzy/near-synonym collapse path, not the whole T1 population; this is
  disclosed, not hidden.
- **core_preserved_ok**: `hdlab.lexical_similarity.self_test()` passes; `hdlab.hd_fact_store.
  _run_all_selftests()` passes; `hdlab.grounding_acquisition_loop.self_test()` and `hdlab.
  prelim_tier.self_test()` pass UNCHANGED (proves e3712e8b5's gate-matching fallback remains
  fully intact -- this cell edits none of these files).

## Verdict tree (pre-registered, no post-hoc tuning)

- `distinct_idea_distinct_rep_ok == False` -> `HARD_FAIL_canonicalization_merges_everything`
  (the explicit anti-collapse mandatory-can-fail failure mode).
- else `no_leak_ok AND scramble_control_ok AND core_preserved_ok == False` ->
  `HARD_FAIL_controls_broken`.
- else `state_of_mind_load_bearing_ok == False` -> `MIDDLE_BAND_canonicalization_ok_state_of_
  mind_not_isolated` (canonicalization/anti-collapse/corroboration may still hold; the STATE-OF-
  MIND sub-claim specifically is not proven -- reported honestly, not folded into a PASS).
- else `same_idea_match_rate >= 0.90 AND automatic_corroboration_rate >= 0.90` ->
  `HARD_PASS_representation_canonicalization_realizes_same_rep_principle`.
- else -> `MIDDLE_BAND_canonicalization_partial_coverage` (anti-collapse + controls +
  state-of-mind all hold, but real-data same-idea match rate is below the 90% floor -- an honest
  lexicon/template-coverage finding, same honest framing convention as e3712e8b5's own MIDDLE_BAND
  branch, NOT papered over by loosening the 0.90 floor post-hoc).

## Compute architecture

Class: (b) sequential-CPU with justification -- single CSKG streaming pass (~1.2M rows, same
`compute_cskg_extra`/`build_cskg_bridges` scans the parent cells use) + one KB-role-schema JSON
load; NO CauseNet scan (scoped out, see above) and NO `ThreeTierLoop`/CA3-gather pipeline (scoped
out, see above) -- lighter than every prior cell in this lineage. Storage: sharded (`HDFactStore`
per test group, each fact its own signature-keyed entry). Wall time budget: self-test <10s, smoke
~15-30s (2-process subset, `{"combustion","photosynthesis"}`, same convention as prior cells in
this lineage), FULL ~30-90s (one CSKG pass, no CauseNet, no consolidation pipeline).

## Dispatch

RUN LOCAL, inline, foreground (Autonomy Declaration: no queue_add, no remote, no push). Smoke
first, self-test gate re-confirmed, then FULL. LOCAL commit, targeted `git add` (never `git add
-A`).

## Schema-vet declarations

- `arms_differ_verified`: N/A in the META_RULE_AF sense (no parallel pipeline arms competing on
  the same discriminator) -- the equivalent check here is `distinct_idea_distinct_rep_ok`
  (representations for genuinely different facts are asserted UNEQUAL via `torch.equal(...) ==
  False`, the direct content-level analog).
- `final_metrics_atomicity`: tmp_replace (single-shot).
- `except SystemExit`/`KeyboardInterrupt` re-raised BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: discrete triple-identity/collapse-rate gates, not a Gaussian noise-floor metric;
  `discriminator_reachability=TRUE` proven closed-form (wood/coal, PRODUCES/CONSUMES, synonym-
  collapse) before touching real data.
- `baseline_in_band`: N/A -- this cell tests representation identity, not a baseline-vs-mechanism
  accuracy gap; the closest analog (`accuracy_baseline` in T3) is pre-registered at ~0.50 by
  construction (a fixed-default policy on a 2-way choice), which is itself the point (context-
  blind is unable to do better than the fixed default it always emits).
- `discriminator survives scale`: T1/T2/T4 run against the REAL full-scale gap population (not a
  toy fixture) in smoke already (2-process subset is still real CSKG+KB data, not synthetic).
- `HP_SCOPE`: HARD_PASS/HARD_FAIL gates apply to T1/T2/T4's real-data + closed-form populations
  combined; T3 carries its own independent load-bearing gate (state-of-mind), scoped separately
  per the verdict tree (a T3 miss demotes to MIDDLE_BAND, it does not invalidate T1/T2/T4).
- `cardinality_ok`: EXPECTED = all real gaps with a CSKG wave (T1a/T4a), all real gaps with a
  KB-role wave (T1b/T4b), 3 closed-form synonym probes (T1c), 3 closed-form anti-collapse probes
  (T2a/T2b), all distinct real (material,whole) pairs (T2c), 8 state-of-mind trials x 2 conditions
  (T3) -- every count is logged in metrics, verdict counts checked against population size.
- `calibration_check`: default_ok_for_this_regime -- `CONCEPT_MATCH_THRESHOLD` reused verbatim
  from `hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD` (independently pre-registered,
  already-validated, never tuned by this cell); T3's context-word lists and T1/T2's paraphrase
  verb tables are hand-authored ONCE before running (documented in-code), never adjusted post-hoc
  against a measured result.
- `progress_logging`: print_flush_true; N/A strictly (declared `--timeout` below 1800s threshold),
  included anyway for audit parity.

## Honest disclosure (pre-registered BEFORE running, per task instruction)

If `distinct_idea_distinct_rep_ok` fails, that is `HARD_FAIL_canonicalization_merges_everything`
-- reported plainly, not tuned away. If `same_idea_match_rate` falls short of 0.90 on real data
while every control holds, that is `MIDDLE_BAND_canonicalization_partial_coverage`, an honest
lexicon/template-coverage finding pointing at source/paraphrase-template expansion as the next
lever -- NOT folded into a PASS, and the task's own honest note is taken seriously: if owned
`concept_similarity`/encoders cannot reliably map surface->same-rep without over-merging, that is
reported as an informative negative pointing back at e3712e8b5's gate-matching solution as the
working fallback, not papered over.
