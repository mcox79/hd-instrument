# Integration audit — hdlab wired vs. islands, and the ARC frontier's bypass of the core

**Date:** 2026-07-25 · **Owner:** hdi_testbed (disk-verified import graph) · **Trigger:** USER "do a full eval of the components we've produced and if they're wired in — I assume this happened a number of times."

## Headline correction to the Director's 13% probe
- 13% is real (599/5326 = 11% of exp cells import any `hdlab.` module) but points at the WRONG debt.
- **hdlab is internally healthier than 13% implies:** counting absolute + relative imports, only **7 of 93 modules are truly dead**. hdlab is a modular library of well-wired subtrees. Grade **B-**.
- **The real debt is a different axis: the ARC/reasoning FRONTIER bypasses hdlab almost entirely.** The current-best ARC pipeline is a tower of `exp_` cells importing other `exp_` cells; it touches hdlab in only ~3 spots. The proven core (reader, cortex, encoders) and the live frontier are **two disconnected worlds.**

## 1. Core-library wired-vs-dead
- **Wired subtrees (good news):** READER cluster (`situation_reader` -> event_centrality_coref, scene_segment, situation_focus, coref, event_bundle, state_of_mind, working_memory, ...); `cortex` cluster; `director_kb`/ingestion cluster; `semantic_parser` cluster; encoder cluster (`composed_encoder_v3` -> vwfa/ppmi); `hdlab/multi_hop.py` (the WEAKER K=2 chain); core VSA via `__init__` (tracing/atoms/binding/bundling/memory/semantic/store...).
- **Truly dead (7):** action_selection, compose_freq_routing, excitability, k_cliff_scaling, lock_in_amp, profiling, self_manager.
- **Utility leaves (used by cells, not composed — fine):** session_log (236 cells), arc_labeler (28), continual (15), ...

## 2. Composed substrate? — NO
- 4 disjoint composition ROOTs (`cortex`, `situation_reader`, `bundle_focus_coref`, `semantic_parser`); none imports another; **none is the ARC pipeline.**
- Current-best ARC = `experiments/exp_arc_selection_pool_tightness_ablation_v1.py`, a tower re-importing 8 sibling exp cells as de-facto modules (learned/ppr/mr/gate/agg/arc/fixedsel + SemanticHDEncoder). **Only 3 hdlab touches in the whole ARC tower:** char_trigram_encoder, event_bundle, hd_fact_store.
- Ad-hoc re-assembly points: `parse_tablestore_typed` inside `exp_arc_selection_relational_meaning_v1.py`; `SemanticHDEncoder` inside `exp_semantic_hd_encoder_meaning_match_v1.py`; `mr.*`/`agg.*`/`gate.*`/`ppr.*`/`learned.*` each an exp cell used as a module via alias.

## 3. Reasoning/comprehension stack — where each piece lives
| Capability | Location | hdlab-wired? | In ARC frontier? |
|---|---|---|---|
| (a) Reader / comprehension | `hdlab/situation_reader.py` + submodules | YES (internally composed) | **NO** — 0 ARC consumers (well-built island) |
| (b) Typed-rule parser `parse_tablestore_typed` | exp-TRAPPED (relational_meaning_v1) | No | Yes, by re-import |
| (c) M3 meet-in-middle multihop (0.62 chain-grade) | exp-TRAPPED (multihop_..._v3) | No | **NO** — a WEAKER K=2 is in `hdlab/multi_hop.py`; the better one never promoted |
| (d) CI/polarity consistency | exp-TRAPPED (aggregation_polarity_ci_v1), imported by nothing | No | **NO** — frontier uses agg=bindsettle, not polarity_ci |
| (e) HD fact store | `hdlab/hd_fact_store.py` | YES | YES (one of the few hdlab pieces reaching ARC) |
| (f) Encoders | SemanticHDEncoder exp-trapped; composed_encoder_v3 in hdlab but UNUSED by ARC; char_trigram in hdlab + used | Mixed | ARC uses the exp encoder + char_trigram, NOT hdlab's composed_encoder_v3 |
| (g) Retrieval `mr.*` + combiner `agg.*` | exp-TRAPPED | No | Yes, by re-import |

## 4. Verdict + prioritized wiring plan
- Grades: hdlab internal **B-**; substrate composition **D** (no entry, 4 disjoint roots); frontier->core **F**; overall **~C-/D+**.
- Non-defensive: the exp->exp tower is a reasonable RAPID-ITERATION pattern; promoting every iteration would be premature churn. The debt turns real NOW because the reasoner-as-integration pivot needs stable module boundaries the exp-tower can't provide.
- **Worst islands (proven, no wired core path):** (1) M3 meet-in-middle multihop 0.62; (2) parse_tablestore_typed; (3) CI/polarity; (4) situation_reader full stack.
- **PRIORITIZED WIRING PLAN (order = unblock the reasoning pivot):**
  - **P1** promote `parse_tablestore_typed` -> hdlab (typed_rule_parser.py) — the graph builder the reasoner consumes; small, high-leverage.
  - **P2** promote the de-facto pipeline (SemanticHDEncoder, mr retrieval, agg combiner, selection) into a stable `hdlab.arc_pipeline` API (stop `from experiments import ... as mr`).
  - **P3** promote the M3 meet-in-middle multihop into hdlab, superseding K=2 `multi_hop.py` — the derivation-search primitive.
  - **P4** wire CI/polarity into hdlab as the consistency stage.
  - **P5** create the MISSING COMPOSED ENTRY `hdlab/reasoner.py` (or substrate.py): reader -> typed_rule_parser -> hd_fact_store retrieval -> multihop derivation -> CI consistency -> selection. Does not exist today; this IS "the substrate."
  - **P6** decide situation_reader's role (ARC comprehension front-end vs Frontier-2).
  - Housekeeping: quarantine/delete the 7 dead modules.
- **Bottom line:** blocked less by missing capability than by capability TRAPPED in terminal exp cells with no stable API. P1->P3 are the unlock; P5 is the absent composed entry. **The verification-by-derivation reasoner build IS P5** — building it promotes P1/P3/P4 as its parts.
