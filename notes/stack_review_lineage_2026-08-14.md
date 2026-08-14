# STACK-REVIEW LINEAGE — every periodic whole-stack review this project has run, and what fell off between them (2026-08-14)

READ-ONLY. No `hdlab/`, `experiments/`, `tools/` or `verification/` file was modified. No experiment was
run. `notes/STATUS.md`, `notes/STATUS_LESSONS.md`, `CLAUDE.md`, `notes/ORGAN_MAP.md`,
`notes/SUBSTRATE_STRATEGY.md`, `data/exp_structured_comparator_v1/probes/` were READ, never written.
Only this file is committed.

**USER's ask:** *"we also periodically did a review of the whole stack - you should look for the last
one of those too … make sure you allow for slight changes in the way things are measured / recorded."*
The convention changed at least five times. This document is the map.

---

## 0. ANSWER IN ONE PARAGRAPH

The whole-stack review is real and has run roughly **every 2-4 weeks since 2026-05-22**, under **six
different names and three different units of account** (PP-numbered capability → hdlab module →
brain organ). The most recent one whose contents are **not** already folded into the current docs is
**`notes/system_accounting_2026-08-13.md`** (commit `fd81d9e60`, 2026-08-13 12:51) — a 141/141 hdlab
module census measured by *runtime import trace*, not grep. Its headline finding is one that
`ORGAN_MAP.md`, `SUBSTRATE_STRATEGY.md` and `data/capability_registry.jsonl` between them do not
state: **57 modules pass their own self-test, are absent from the live path, and 24 of those have no
registry row at all — they are invisible to every registry-based audit we run.** Separately, the
registry's `pipeline_status` field is **wrong in both directions** (3 rows claim USED and are not; 19
claim unreachable and are reachable — including `reading_grounding_loop`, the pipeline entry point
itself). Meanwhile the *current* review, `ORGAN_MAP.md`, accounts for **38 organs** against that
census's **141 modules** and **127 registry rows**: the current doc covers roughly a quarter of the
module surface, at a coarser grain, by design.

---

## 1. THE MOST RECENT WHOLE-STACK REVIEW

**`notes/system_accounting_2026-08-13.md`** — 48 KB, 20 sections, commit `fd81d9e60`, dated **2026-08-13**
(content date, matches commit date). Subtitle: *"what exists, what runs, what is reachable."*

**Coverage (all machine-measured, method stated per row):**

| unit | count |
|---|---|
| `hdlab/` `.py` modules assigned to a subsystem | **141 / 141**, no dupes, no omissions (S1–S12) |
| import cleanly under `.venv` | 141 / 141 (zero failures) |
| reachable from the LIVE path (runtime `sys.modules` trace) | **35 / 141** |
| have a `__main__` self-test | 81 / 141 |
| registry rows at the time | 123 (now 127) |
| hdlab modules with NO registry row | **62 / 141** |
| experiment cells | 5,745 |
| result dirs with `metrics.json` | 7,551 |
| `tools/` scripts | 1,016 |
| `verification/` scripts | 72 |

### 1.1 WHAT IT SAYS THAT THE CURRENT DOCS DO NOT — the delta

Each item below was checked against `notes/ORGAN_MAP.md`, `notes/SUBSTRATE_STRATEGY.md` and
`data/capability_registry.jsonl` by literal token count. `0/0/0` = absent from all three.

1. **A 57-module "works but is not on the live path" shelf, itemised.** 33 modules self-test PASS +
   registry says `WIRED` + absent from the runtime closure; **plus 24 that self-test PASS, are not
   live-reachable, and carry NO registry row at all.** The 24 by name:
   `atom_consultation, bayesian_inference, char_positional_encoder, clarify_gate, conformal,
   context_retention, coref_distractor_suppress, definitional_predicate_v61, dg_pattern_separation,
   event_centrality_coref, glass_box_loop, goal_outcome_relation_grounded, late_combine,
   mcscript_extraction, modern_hopfield_readout, noise_channel, outcome_event_extraction, per_item_log,
   perceptron, script_grain_acquisition_loop, semantic_parser, temporal_trace, word_learning_tool,
   wordnet_polarity_propagation`.
   No current doc carries this list. It is the single most reusable thing in the lineage.

2. **`pipeline_status` is unreliable in BOTH directions.** (A) 3 (row, module) pairs claim
   `WIRED_AND_PIPELINE_USED` and are measurably not in the closure (`composition`/`concept_encoder`;
   both `goal_owner_*` rows / `goal_owner_select`). (B) **19 pairs claim unreachable and are reachable**,
   including `reading_grounding_loop_definitional_reading_pipeline` — *the pipeline entry point is filed
   as not-pipeline-reachable*. (C) 13 modules sit inside the live closure with no registry row at all,
   including **`grounding_acquisition_loop`, one of the two live entry points**.
   ⇒ **A compliance audit run against the registry cannot see the live path.** That sentence appears
   nowhere in the current docs.

3. **Dead weight is tiny; the debt is unwired-but-working.** Only **2** modules have never demonstrably
   executed (`k_cliff_scaling`, `profiling`). 2 are unknown (`concept_encoder`, `reasoner` — self-test
   TIMEOUT at 180 s). 1 has a stale failing pin (`goal_achievement`). Everything else runs.
   The current docs discuss organ *fidelity*; none of them states that the repo's dead-code problem is
   ~2–7 modules and its islanding problem is ~57.

4. **`wordnet_polarity_propagation` is the ONLY live dictionary lookup in the repo** (`nltk.corpus.wordnet`).
   Verified `0/0/0` — absent from ORGAN_MAP, SUBSTRATE_STRATEGY and the registry. Its orchestration glue
   `word_learning_tool` has exactly 1 consumer; their one landed evaluation HARD_FAILED. Given the
   current arc is a *lexical within-neighbourhood separation* failure, a live dictionary path that no
   plan document knows exists is directly load-bearing.

5. **`hdlab/glass_box_loop.py` is `0/0/0`** — no ORGAN_MAP entry, no STRATEGY mention, no registry row —
   despite `architecture_audit_2026-08-11.md` (item 7) naming it as *"exactly the arbitration/fusion
   `three_tier_loop.answer()` lacks (Gap G1)"*, validated on real ConceptNet V=48000, zero importers.

6. **A specific correction to a sibling audit** that no current doc carries: the three-tier design
   audit's gap **G5** ("the MDL conjunctive gate was never invoked, `mdl_gate_fn=None` at both call
   sites") is **stale** — `reading_grounding_loop.py:1278` *does* pass `mdl_gate_fn=gate`, but the gate
   passed is the **refusal** gate, not the `hdlab/learner` MDL gate. The hook is occupied by the wrong
   object. That is a different and more actionable bug than "never invoked".

7. **Its own honest not-verified list (S19)**, which is itself absent from current docs: two self-test
   outcomes unknown (timeout, not fail); no landed verdict was recomputed per-arm; **no written
   definition of "pipeline" exists** for the registry field it audits, so some Q2 mismatches may be
   definitional rather than errors; ConceptNet/Wikidata row counts not decompressed.

---

## 2. THE LINEAGE — every whole-stack review found, in content-date order

Dated by content and by `git log --format=%ci` on the file's own commits. mtimes were **not** trusted.

| # | Era / unit of account | Artifact | Date | Covered | Superseded because |
|---|---|---|---|---|---|
| 1 | **4-session fleet, cycle-numbered** | `notes/meta_audit_2026-05-22_cycle59.md` … `_2026-05-23_cycle{80..96}.md`, `_cycles77-78_consolidated.md`, `_2026-05-24.md` (19 files) + `notes/strategy_audit_2026-05-24_cycle199.md` + `notes/strategy_research_shoreup_matrix_2026-05-23.md` | 2026-05-22 → 05-24 | per-cycle process + capability state | cycle numbering died with the 4-session model; cadence lapsed (last meta_audit of any kind = `notes/meta_audit_2026-07-07.md`) |
| 2 | **PP-numbered capability, TIER A/B/C** | `notes/capability_scorecard.md` (279 KB, "Created 2026-06-04", cycle-by-cycle appends) + append log `notes/substrate_capability_map.md` (4.86 MB) + `notes/substrate_capability_map_history.md` (2.87 MB) | 2026-06-04 → 2026-06-17 | every validated capability by PP number | **self-declares SUPERSEDED at head, 2026-07-28**: "checkboxes rotted". `substrate_capability_map.md` last real update 2026-07-08 |
| 3 | same | `notes/capability_matrix_HONEST_AUDIT_2026-06-11.md` | 2026-06-11 | honesty re-tiering; **only ~5 capabilities were truly Tier A** | one-shot honesty pass, never repeated in that form |
| 4 | same | `notes/research_to_skunkworks_exp_dev_GLOBAL_capability_verification_pass_2026-06-17.md`; `notes/research_to_USER_capability_optimality_substrate_mine_REPORT_2026-06-18.md` | 2026-06-17/18 | global verification sweep | fleet-era routing docs; not carried forward |
| 5 | **capability × brain-analog × theoretical-limit** | `notes/research_substrate_load_bearing_capability_assessment_2026-06-25.md` | 2026-06-25 | Stage 1–4, per capability: brain analog / tier / **theoretical limit** / truly-enabling? | the "theoretical limit" column was never reproduced in any later review — see §3 |
| 6 | **import-graph / wired-vs-island** | `notes/integration_audit_hdlab_wired_vs_islands_2026-07-25.md` + `notes/promotion_backlog.md` (P1–P6, superseded-banner 07-28) | 2026-07-25 | 93 modules; **237 promotion candidates; 4133/5327 (78%) bypass cells; 7 dead; composed entry = ABSENT** | checkbox rot (P1/P5 landed 07-25, boxes still unchecked 07-28); replaced by the registry |
| 7 | **WIRE-or-SHELVE gate** | `notes/capability_integration_ledger.md` (21 KB, entries 07-28 → **08-05**) | 2026-07-28 → 08-05 | island inventory with an explicit gate decision + revival criteria per capability | still the best *decision* record; superseded operationally by `data/capability_registry.jsonl` |
| 8 | **component × brain metric** | `notes/component_brain_fidelity_ledger.md` (14 rows) + `notes/brain_foundational_component_analysis.md` (07-29) + `notes/brain_foundational_confirmation_whole_architecture_2026-07-29.md` | 2026-07-28 → 07-30 | 14 components, each gated on the BRAIN's metric | **explicitly superseded by `ORGAN_MAP.md` §7** (named components, not equations; no runtime WIRED column; missed 7 organs) |
| 9 | **the one that calls itself a full-stack review** | **`notes/brain_foundational_stack_assessment_2026-07-30.md`** — "FULL COMPREHENSION-STACK ASSESSMENT" | 2026-07-30 | 8 brain components, disk-verified placement + ranked levers | its #1 lever (assembly cell) has since been run → `LOCALIZED_WALL`; carried into ORGAN_MAP §7 |
| 10 | **invisible-island reconciliation** | `notes/capability_reconciliation_invisible_islands_audit.md` (5 HARD_PASS organs with zero registry rows) + `notes/brain_audit_our_components_status.md` | 2026-08-04 / 08-05 | HARD_PASS→registered direction (the audit tool only checked registered→wired) | gate closed 08-05 in the integration ledger; method not re-run since |
| 11 | **organ × GREAT/MEH × shore-up order** | `notes/architecture_audit_2026-08-11.md` | 2026-08-11 | ~15 organs, 3 parallel code-read clusters, 6 honest self-corrections | folded partly into ORGAN_MAP; several items (glass_box_loop, sweep-never-fired-on-sparse) not carried |
| 12 | **module census, runtime-measured** | **`notes/system_accounting_2026-08-13.md`** | **2026-08-13** | **141/141 modules** + tools + verification + data | ← **THE DELIVERABLE.** Not superseded; simply not folded in |
| 13 | **organ × equation (CURRENT)** | `notes/ORGAN_MAP.md` (living, 1,456 lines) + `notes/SUBSTRATE_STRATEGY.md` | 2026-08-14 | **38 organs**: 5 do the brain's arithmetic, 13 measure the wrong thing, 7 missing, 16 never tested against anything they could fail | current |
| 14 | **results census (complementary, not capability-level)** | `notes/vscode_week_results_validity_audit_2026-08-14.md` (`0887b54f8`) + `notes/vscode_era_unrecognised_assets_2026-08-14.md` (`6b43be02d`) | 2026-08-14 | 284 attacked results; 7,649 metrics.json enumerated, 3,153 normalised passes, 1,500 floored | current |

**Cadence observed:** 05-22 → 06-04 → 06-11 → 06-25 → 07-25 → 07-30 → 08-05 → 08-11 → 08-13 → 08-14.
Roughly fortnightly, tightening to near-daily in August. The USER is right that this is a standing habit.

---

## 3. WHAT WAS LOST IN EACH TRANSITION

Capabilities and *measurement columns* that appear in an older review and in **no** current doc.
Verified by token count against ORGAN_MAP / SUBSTRATE_STRATEGY / capability_registry.jsonl.

### 3.1 Capabilities that fell off the list

| capability | last named in | ORGAN_MAP / STRATEGY / REGISTRY | why it matters now |
|---|---|---|---|
| **`glass_box_loop`** — Go/NoGo value gate + Merkle audit trail, real ConceptNet V=48000 | architecture_audit 08-11 (item 7) | **0 / 0 / 0** | named as *the* fix for `three_tier_loop.answer()`'s missing arbitration (Gap G1); zero importers |
| **`wordnet_polarity_propagation`** — the repo's ONLY live dictionary lookup | system_accounting 08-13 | **0 / 0 / 0** | the current defect is lexical near-neighbour separation; a live dictionary path is on-topic |
| **`word_learning_tool`** | system_accounting 08-13 | 0 / 0 / 3 | 1 consumer; its one evaluation HARD_FAILED — but the *tool* passes its self-test |
| **`gated_fusion` (+0.297, 8 seeds, scramble-controlled, MRR 0.36→0.66)** | integration ledger 07-28, tagged **"TOP forgotten asset"** | **0 / 0** / 4 | was gate-decided **WIRE** on 07-28 and is named in no plan document today |
| **`sr_routing` multihop (+0.253)** | integration ledger 07-28 / 08-04 | **0 / 0** / 1 | registry status `orphaned_source_not_locatable_retired_2026-08-03`; ledger says git-recover before reinventing |
| **`scale_win` TinyTransformer encoder** (learned from scratch on 237.7M ARC tokens; "beats grounding +0.050 semantic / +0.071 relational") | architecture_audit 08-11 (Tier 1) + integration ledger 07-28 | **0 / 0** / 3 | gate=WIRE, `TRAPPED_SHARED`, zero hdlab imports — flagged as half of the **#1 shore-up** on 08-11 |
| **39,707-word grounding norms** (Lancaster sensorimotor / Brysbaert concreteness / Warriner VAD / AoA, `data/grounding_testbed`) | architecture_audit 08-11 (Tier 1) | not in STRATEGY | the other half of the #1 shore-up: a grep-confirmed disconnected island |
| **`vamp_ep_deep_chain_solver`** — acc 1.000 to depth ~200, K=5000, 30% noise | integration ledger 08-04, *"the repo's best deep-chain mechanism"* | **0 / 0** / 1 | SHELVE with revival = NL causal-chain transfer smoke; never revisited |
| **`theory_of_mind_sally_anne_nested_hrr`** — HARD_PASS Q2 0.806 vs 0.138, oracle 1.0, 5 seeds | invisible-islands audit 08-04; gate **WIRE** 08-05 | **0 / 0** / 2 | gate said WIRE ("partition situation-model by protagonist"); never executed |
| **`k_cliff_scaling`, `profiling`** | promotion_backlog 07-25 ("quarantine 7 dead") → system_accounting 08-13 | 0 / 0 / 1 each | the only two modules that have provably never run; still not quarantined 3 weeks later |
| **`modern_hopfield_readout`, `dg_pattern_separation`** | vscode_era sweep 08-14 | 1 / 0, 3 / 0 | *mentioned* in ORGAN_MAP but confirmed NOT REACHED by either live loop |

### 3.2 Measurement columns that fell off (the quieter loss)

- **Theoretical limit / closed-form bound per capability** — present in `research_substrate_load_bearing_capability_assessment_2026-06-25.md`, present in **no** review since. We stopped recording what a component's ceiling *is*, which is precisely the column that would settle "ceiling vs impl-bug" arguments.
- **"Truly enabling? YES / PARTIAL / NO"** — same doc, same fate.
- **Bypass ratio** — `4133/5327 (78%) of exp cells bypass hdlab` and `237 promotion candidates` (07-25). Never recomputed. The 08-13 census measures a *different* thing (live-path reachability), so the trend line is broken.
- **Revival criteria as a first-class field** — the 07-28→08-05 integration ledger recorded, for every SHELVE, the specific condition that would revive it. The registry keeps a `revival_criteria` field but no doc reviews them; several are now satisfiable (e.g. `action_selection`'s "when the grounded appraisal→action layer is built"; `situation_reader`'s "when a narrative/multi-sentence reading pipeline is built" — that pipeline now exists).
- **The 4-session-era `PP-` identifiers** — capabilities PP-217/225/226/227/228 (Tier A, 2026-06-11) have no successor identifier in any current scheme. They are recoverable only by reading `capability_scorecard.md`.

### 3.3 The structural reason things fall off

Each transition changed the **unit of account**, and anything that did not map onto the new unit
silently vanished:

`cycle number` → `PP capability` → `hdlab module import edge` → `WIRE/SHELVE gate decision` →
`brain component` → `brain organ + equation`

A capability proven as a *cell* (gated_fusion, sr_routing, sally-anne ToM, VAMP) has no organ, so it
cannot appear on an organ map. A module that is dead but harmless (`k_cliff_scaling`) has no equation,
so it cannot appear either. **The registry is the only artifact whose unit survived two transitions —
and §1.2 shows its own status field is wrong in both directions.**

---

## 4. WHAT I COULD NOT DETERMINE

1. **Whether a whole-stack review exists between 2026-06-25 and 2026-07-25** — a one-month gap. I
   enumerated `notes/` (9,834 files) and filtered on `audit|inventory|scorecard|census|stocktake|ledger|
   backlog|map|state|digest|POST_COMPACT|protocol|charter`, and I ran `git log --diff-filter=A` over
   `notes/`. Nothing whole-stack-shaped falls in that window. I did **not** exhaustively read all 9,834
   filenames, so this is a filtered enumeration, not a proof of absence.
2. **Whether any of the §3.1 assets would actually help if wired.** Nothing tests those pairings. The
   08-13 census says the same thing about itself (S19 item 2). Stating a benefit either way is speculation.
3. **Whether the fortnightly cadence was ever an explicit rule** or an emergent habit. `notes/active_protocols.md`
   (44 KB) documents a meta_audit cadence, but the last meta_audit of any kind is `notes/meta_audit_2026-07-07.md`
   — the *named* cadence lapsed 5 weeks ago while the *practice* continued under new names. I did not
   read all 44 KB of active_protocols to check for a whole-stack-review clause.
4. **Whether `git log --all` would surface stack reviews deleted from this branch.** Two full-history
   sweeps timed out at 120 s each on this repo. I fell back to per-file `git log` and to on-disk
   enumeration. Every artifact in §2 exists on disk today; a review that was created *and* deleted in
   history would not have been caught.
   (Note: an earlier pass in this session wrongly concluded `notes/promotion_backlog.md` did not exist,
   because a timed-out `git log` returned empty output. It exists. Empty output from a killed command is
   not evidence of absence — the trap CLAUDE.md warns about, encountered live.)

---

## 5. RECOMMENDED PICK-UP (not actioned here)

If one thing is taken from this document: **run the §1.2 delta as a reconciliation pass.** The 24
no-registry-row modules and the 22 wrong `pipeline_status` rows are a half-hour of bookkeeping that
would make every future registry-based audit trustworthy. Second: **`glass_box_loop` and
`wordnet_polarity_propagation` are `0/0/0`** — neither is on any plan, both are live-code, and both
target currently-open gaps (arbitration in `answer()`; lexical separation).
