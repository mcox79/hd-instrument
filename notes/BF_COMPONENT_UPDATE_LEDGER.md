# BF COMPONENT-UPDATE LEDGER — every solution's brain-foundational component updates, classified + tracked

**Why this exists (owner 2026-09-10):** *"many of the solutions have BF component updates — have you been integrating those? They may be focused on their particular problems, so it might be just specific arms for those functions; I want to understand how you're tracking, implementing, and managing that."* Nearly every solution audits the components it touches and reports **AUDIT UPDATE**s (per the SOLVER OPERATING PROTOCOL + `BRAIN_FOUNDATIONAL_AUDIT.md`). Those updates were being folded **opportunistically at integration** (§2b + `bf_status_registry.jsonl`) and propagated via `CROSS_SOLUTION_IMPROVEMENT_MAP.md` — but there was **no single always-current view that enumerates every solution's BF updates and classifies each NARROW-vs-GENERAL**, so a general correction to a *shared live organ* could sit unrecognized in an in-review solution's BF doc. This ledger is that view.

## The classification (the owner's nuance)
- **NARROW** = the BF update is specific to THIS solution's arm/experiment; it applies to the live substrate only when this solution lands (owner-DONE). Nothing to do independently.
- **GENERAL** = the BF update is a correction/characterization of a **shared live organ** (parser cluster, `pos_tagger`, `commonnoun_binder`, meaning channel, …) that the live substrate should reflect **independent of this solution's headline**. These are the ones at risk of being lost — they need explicit tracking + propagation.

## The rule (implementing — unchanged gate)
- A BF update's *fix* (code / status-flip) lands in the live `bf_status_registry.jsonl` + §2b **only at owner-DONE** for its solution (the integration gate; I do not front-run).
- A BF update's *characterization refinement* (e.g. "this organ's NOT_BF is really the supervised scorer, the decode is now fixable") is TRACKED here immediately and folded to the registry note at integration — it is not silently adopted early, but it is never lost.
- At each integration I: (1) apply the solution's own BF updates (§2b + registry), (2) walk this ledger's GENERAL rows touching the same organ and apply/propagate them, (3) update the row status.

---

## TABLE — status: `APPLIED` (live) · `PENDING-DONE` (captured, awaits owner-DONE) · `LOCATED-NEGATIVE` (characterization only, no fix to land)

### IN-REVIEW submissions (awaiting owner review — BF updates captured, NOT yet applied)
| solution | BF component update | narrow/GENERAL | shared live organ(s) | status |
|---|---|---|---|---|
| pri-3 `the_parser_is_a_frozen_supervised_hard_decode…` | Per-stage BF decomposition: DECODE now BF-fixable (exact fwd-bwd posterior + Matrix-Tree marginals built); residual NOT_BF = the **supervised surface arc-scorer** (~99% of head error) + the acquisition question; `parse_confidence` is **decision-dead → droppable**; `arc_labeler` graded readout exists opt-in | **GENERAL** (sharpens 5 live NOT_BF organs' characterization) | pos_tagger, arc_parser, arceager_parser, arc_labeler, parse_confidence | **PENDING-DONE** (BF_AUDIT_UPDATE.md + UPSTREAM_CHAIN_BF_AUDIT.md; fold to §2b + refine registry notes on land) |
| pri-4 `the_common_noun_binder_is_string_identity…` | `commonnoun_binder.head_lemma` (surface-regex) marked **NOT_BF**; BF replacement `concept_lemma` (morphy, non-alpha-safe); loose-synonymy identity gate REFUTED (identity is lemma-tight); board `common_noun` floor embeds a +0.0158 redaction leak (de-leak to 0.5254) | **GENERAL** (head_lemma is shared by `online_entity_cluster`) | commonnoun_binder, online_entity_cluster | **PENDING-DONE** (pre-staged in INTEGRATION_LEDGER READY WAVE; reconciled clean) |
| pri-7 `harm_help_valence_is_a_fitted_verb_list…` | `force_dynamics_valence` **NOT_BF→BF_SPIRIT** (Wolff force-structure × grounded valence + affectedness gate; retire FrameNet read-path enum); upstream `pos_tagger` **nominal_head_correction** (DP-head ADJ→NOUN via lexical prior) | **GENERAL** (pos_tagger is the shared parser-cluster organ) | force_dynamics_valence, pos_tagger | **PENDING-DONE** (pre-staged in INTEGRATION_LEDGER READY WAVE; reconciled clean) |
| pri-5 `measure_end_to_end_whether_the_meaning_fusion…` | Finding: the meaning-fusion chain is BF at EVERY computation; the ONE loss is unordered distributional pooling (syntagmatic≠paradigmatic) — a representational gap, not a stand-in; lever = clean is-a knowledge | **GENERAL** (characterization of the live meaning channel) | grounded_similarity / distributional_meaning_channel / reading_grounding_loop | **LOCATED-NEGATIVE** (characterization; the fix is pri-1, not this solution; fold finding to §2b on DONE) |

### RECENTLY INTEGRATED (owner-DONE) — BF updates APPLIED
| solution | BF component update | status |
|---|---|---|
| grow_the_causal_mechanism (pri-1 causal) | `predictive_world_model`/`situation_reader` causal-antecedent relabeled counterfactual→**rung-1**; `causal_reasoner`=BF_SPIRIT rung-2/3 (+`is_necessary_abductive` rung-3); `causal_sign` formal-model sign wired live | **APPLIED** (§2b + registry + `sm.causal_sign` live) |
| meaning_representation_is_a_point_vector | 3 BF pieces landed latent (directional ROUTE-B parser-free channel, `valence_polarity_channel`, `convergent_cue_reader.intrinsic_gain_w` retiring fitted DEFAULT_W) | **APPLIED-latent** (registry; live fusion-flip gated on pri-5) |
| world_knowledge_name_bridge | `safe_kb_gate` BF safety theorem landed; who_is_who_lexicon durable | **APPLIED** (registry + KNOWLEDGE_ASSET_REGISTER) |
| reward_action_selection_vigor audit | reward cluster decision-core confirmed FAITHFUL-but-DORMANT, NO live unflagged stand-in (clean) | **APPLIED** (§2b, no code) |

---

## THE HONEST STATE (what this ledger revealed)
- **Integrated solutions' BF updates → folded** (§2b + registry + propagation log). Good.
- **In-review solutions' BF updates → captured here, NONE applied to the live registry** (owner-DONE gate). pri-4/pri-7 were already pre-staged in the INTEGRATION_LEDGER; pri-3/pri-5 are **newly captured here** (they were previously only in their own BF side-docs).
- **The registry carries only 4 formal `__bf_corrections__` fields** vs ~40 solutions carrying AUDIT UPDATEs — because most AUDIT UPDATEs are (a) confirmations, (b) newly-LOCATED stand-ins that become posted problems, or (c) fixes pending owner-DONE. This ledger makes the (c) set explicit so none is lost.
- **No general-to-live correction is currently being wrongly withheld:** every GENERAL row above is PENDING-DONE for a solution that is *in the owner's review queue* — i.e. it lands the moment the owner marks its solution DONE. The gate is doing its job; this ledger just makes the queue of pending BF corrections visible and organ-indexed.

## MAINTENANCE
At each new SOLVED (or when a submission's BF doc changes): add/refresh its row, classify narrow/GENERAL, set status. At each integration: apply the solution's BF updates + walk GENERAL rows on the same organ. Cross-refs: `bf_status_registry.jsonl` (live status), `BRAIN_FOUNDATIONAL_AUDIT.md §2b` (narrative log), `CROSS_SOLUTION_IMPROVEMENT_MAP.md` (consumer reverse-index + PROPAGATION STATUS), `INTEGRATION_LEDGER.md` (per-solution gain/wiring).
