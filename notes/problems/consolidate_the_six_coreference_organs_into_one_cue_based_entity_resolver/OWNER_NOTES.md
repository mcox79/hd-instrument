---
owner_verdict: DONE
---

SUBMISSION — problem: consolidate_the_six_coreference_organs_into_one_cue_based_entity_resolver
(status: SOLVED, WIP until owner_verdict: DONE — Q111: proof + proposed diff, strategy lands hdlab)

ONE-LINE RESULT. Built ONE cue-based `entity_resolver` — a single ACT-R content-addressable retrieval CORE +
mention-type-routed cue-arms (Ariel Accessibility) — that reproduces the SIX live coreference organs, proven
BYTE-IDENTICAL on real data. The retrieval MATH was never the fragmentation (all six already call ONE
`salience_binder.actr_activation`); the WRAPPERS were.

PROVEN (experiments/exp_entity_resolver_unified_v1.py; witnesses 12/12 + 2/2 + 3/3):
  • online_entity_cluster  — byte-identical, 8562 mentions/80 GUM docs, all arms (exact/isa/partwhole/hold/centering)
  • crosstype_bridge       — byte-identical, ALL 5 cue modes {retrieval,gated,competed,novelty,conf}, 60 docs
  • world_state_entity_binding — byte-identical, 400 dispatch calls + stats
  • typed_coref / _resolve_commonnouns — byte-identical, 801 records / 639 resolved bridges
  • pronoun pick == salience_binder.bind (3000 sets) → the ONE core serves all FOUR Ariel mention types
  • END-TO-END: live SituationReader byte-identical (entities+coref+common-noun+world-state) with all 4 organs
    substituted; board `crosstype_experiencer` dim MEASURED identical (n=130, model 0.1846, CI-sep). W5 non-vacuity
    control: a wrong arm config DIVERGES → the byte-identity is a real constraint.

DISPOSITION OF THE OTHER TWO (disk-outranks-brief corrections):
  • commonnoun_binder.situation_predict = NOT_BF (0.4904 < string-identity) and EMPIRICALLY DEAD on the live path
    (shadowed by online_entity_cluster; gate on/off byte-identical) → retires. But its LEXICAL HELPERS feed 4 live
    organs → it is INVERSE (split `lexical_utils`), NOT the brief's clean "drop".
  • entity_world_model_resolver = DORMANT → folds as a KB-prior BONUS cue-arm (the same core slot the crosstype
    descriptive-content boost uses; proven-in-kind).

BRAIN-FOUNDATIONAL / MATHEMATICAL BF STATUS (full table in SOLVED.md):
  • BF (pinned): salience_binder.actr_activation (ACT-R base-level) + the Ariel routing (cue-set is mention-type-
    specific — the naive one-cue merge was measured-REFUTED: form_the_unified_discourse_referent).
  • BF_SPIRIT: the unified organ + all reproduced organs (L&V retrieval pinned; cues glass-box/supply).
  • The ONE shared mathematical gap: HARD phi/type FILTER-then-rank vs L&V GRADED cue-combination with similarity-
    based interference — SHARED by all six, so the consolidation makes the fix a SINGLE edit to `retrieve()`
    (exact equation A_i=B_i+ΣW_j·S_ji−P·mismatch spec'd in SOLVED). No NEW stand-in introduced.
  • NOT_BF (pre-existing): situation_predict (retires); the frozen parse spine (declared scaffold, one live dep).

HIGH-PRIORITY NEXT STEPS:
  1. LAND (Q111, byte-identical/proven): create hdlab/entity_resolver.py, repoint the 4 reader call sites, retire
     situation_predict, split lexical_utils, fold the dormant KB arm; re-run the full board once.
  2. THE BF PRIZE (separate, behavior-changing problem — overlaps strengthen_the_cue_based_pronoun_...): upgrade
     retrieve() to graded L&V cue-combination — now single-point instead of six organs.
  3. Route crosstype_live_adapter's parse off the NOT_BF frozen spine onto the glass-box incremental_parser.

FILES: experiments/exp_entity_resolver_unified_v1.py + verification/test_entity_resolver_{unified,typed_commonnoun,
reader_substitution}.py. No hdlab/ writes (Q111; exact merge diff in SOLVED.md). Reverify: run the 3 witnesses.
Ledger malformed/incomplete: 0.
