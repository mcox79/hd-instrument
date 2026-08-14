# VS Code history archaeology — the transcripts back to 2026-05-31 (2026-08-14)

READ-ONLY sweep. No repo code changed, no experiment run. `notes/STATUS.md`,
`notes/STATUS_LESSONS.md`, `CLAUDE.md`, `notes/ORGAN_MAP.md`, `notes/SUBSTRATE_STRATEGY.md`,
`notes/stack_review_lineage_2026-08-14.md`, `data/exp_structured_comparator_v1/probes/` were READ
(for mention-joins) and never written. Only this file is committed.

**This sweep is distinct from the two that precede it.**
- `notes/vscode_week_results_validity_audit_2026-08-14.md` (`0887b54f8`) adjudicated results that
  were ATTACKED in the 08-02..08-12 window. Closed; not re-litigated here.
- `notes/vscode_era_unrecognised_assets_2026-08-14.md` (`6b43be02d`) enumerated the FILESYSTEM for
  floored passes the plan does not mention. It ranked by relevance to C3.
- **This sweep asks a different question: what does the BRAIN-FOUNDATIONAL arc look like across the
  WHOLE history (2026-05-31 onward), and how much of it is invisible to the current plan?** The
  USER's stated hypothesis is that "we did so much work on brain foundational architecture... I
  assume you're missing a lot of it."

---

## 0. ANSWER IN ONE PARAGRAPH

**CONFIRMED, and the magnitude is larger than the previous sweep implied.** The substrate contains
**21 distinct named brain-mechanism families** with experiment cells on disk — **843 distinct cell
stems, of which 251 have BOTH a pass-flavoured verdict AND a floor/control. Of those 251 floored
passes, 213 (85%) are named in NONE of the four current planning artifacts** (`ORGAN_MAP.md`,
`SUBSTRATE_STRATEGY.md`, `STATUS.md`, `data/capability_registry.jsonl`). Whole families are at zero
visibility: **k-WTA / sparse coding (17 of 17 invisible), attractor/Hopfield (12 of 12),
Hebbian/STDP (4 of 4), conjunctive binding (42 of 49), cleanup/resonator (51 of 53).** The
previous sweep found six Tier-1 assets; the family view shows those six sit on top of an arc that
ran from late June through July and was never rolled up. **Two families are the exception and prove
the rule** — `situation model (Kintsch/Zwaan)` is 0-of-7 invisible and `information foraging (MVT)`
is 0-of-1 invisible, because both were wired in the last three weeks while the planning docs were
being actively maintained. Everything built BEFORE that maintenance window is dark.

---

## 1. THE BRAIN-MECHANISM FAMILY INVENTORY (priority 1)

Method: enumerated all **7,649** `metrics.json` from the filesystem index built by the prior sweep
(`scratch/_classified.json`, itself built by `os.walk` + recursive key scan, never by expected
name). Cell names matched against 21 brain-mechanism regexes. Collapsed `_smoke` / `_selftest` /
`_fulldev` / `_full` / seed suffixes to a STEM. "floored PASS" = the stem has at least one
pass-flavoured verdict AND at least one floor/scramble/chance/control/lesion/ablation key.
"invisible" = the stem name (and its `exp_`-stripped core) appears in none of the four docs.

| brain family | stems | floored PASS | INVISIBLE | first dated cell |
|---|---|---|---|---|
| cleanup memory / resonator | 185 | 53 | **51** | 2026-06-29 |
| conjunctive binding / role binding | 112 | 49 | **42** | 2026-06-28 |
| replay / sharp-wave ripple | 95 | 23 | **19** | 2026-07-11 |
| CLS / systems consolidation | 59 | 20 | **11** | 2026-07-02 |
| hippocampus CA3/CA1/DG (pattern sep+comp) | 78 | 18 | **14** | 2026-06-28 |
| k-WTA / sparse coding | 31 | 17 | **17** | 2026-07-01 |
| Centering / coreference (Grosz) | 65 | 13 | **6** | 2026-07-24 |
| attractor / Hopfield | 65 | 12 | **12** | (undated) |
| PFC / semantic control / IFG | 44 | 11 | **7** | 2026-06-27 |
| forgetting kernel / Benna-Fusi cascade | 52 | 9 | **7** | 2026-07-09 |
| situation model (Kintsch/Zwaan) | 23 | 7 | **0** | 2026-07-24 |
| predictive coding / surprise | 18 | 5 | **2** | 2026-07-02 |
| Hebbian / STDP | 32 | 4 | **4** | 2026-07-02 |
| V1 / VWFA / visual grounding | 7 | 4 | **4** | 2026-07-18 |
| divisive normalisation | 14 | 3 | **2** | 2026-08-14 |
| ACC / conflict monitoring | 3 | 1 | **1** | 2026-07-08 |
| basal ganglia / dopamine | 2 | 1 | **1** | (undated) |
| information foraging / MVT | 2 | 1 | **0** | 2026-08-14 |
| ATL / hub-and-spoke | 7 | 0 | 0 | — |
| cerebellum | 3 | 0 | 0 | — |
| entorhinal / grid | 1 | 0 | 0 | — |
| **TOTAL** | **843** | **251** | **213** | |

**Reading the table honestly.** Three caveats, stated before the interpretation:
1. **"Floored" is a KEY-PRESENCE test, not a quality test.** It means the metrics file contains a
   floor/control/scramble/ablation key. It does NOT mean the floor was well-chosen or that the
   margin over it was large. Every individual claim below that matters was hand-checked; the 213
   as a bulk number was not.
2. **"Invisible" is a NAME test.** A family can be discussed in the docs conceptually while no cell
   stem is named — the plan docs are curated prose and mostly do not name cells. The prior sweep
   measured this directly: of 1,500 floored passes repo-wide, STRATEGY names 2 and ORGAN_MAP names
   13. **So invisibility ALONE is not the finding.** The finding is the *family-level* pattern:
   entire mechanisms with double-digit floored passes and a ZERO in the docs column, next to
   recent families with a ZERO in the invisible column.
3. **Per-stem verdicts shown below are one of possibly several** (multi-seed stems can carry
   HARD_PASS on some seeds and HARD_FAIL on others). Where a HARD_FAIL appears it is reported, not
   hidden.

### 1a. The zero-visibility families, named

These are the ones where the docs column is empty for EVERY floored pass in the family.

**k-WTA / sparse coding — 17 of 17 invisible.** A sustained June-July sweep:
`exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7` (2026-07-01, HARD_PASS),
`..._v4b_pc_widened_alpha_grid_n4096` (2026-07-02), `..._v5_wm_fixed_n4096_seed_7` (2026-07-02),
`exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192` and `_v2_n8192` (2026-07-01). This is a
free-axis / crossproduct sweep at production N (4096-8192), floored, multi-seed. Sparsity is a
first-order brain constraint and there is **no `sparsity` row in the registry and no mention in
either plan doc.**

**attractor / Hopfield — 12 of 12 invisible.** `exp_modern_hopfield_pipeline_validation_v1_n2048_n4096`
(PIPELINE_HARD_PASS), `exp_hopfield_spurious_minima_cpu_v1` (HARD_PASS — spurious-minima control is
exactly the failure mode an attractor cleanup must be shown to avoid),
`exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_*` and `_pythia160m` (HARD_PASS —
substituting Hopfield for attention in a real LM), `exp_pc_cleanup_attractor_v1` (HARD_PASS). Note
`hdlab/modern_hopfield_readout.py` exists on disk and is NOT on the default path (prior sweep §5).

**Hebbian / STDP — 4 of 4 invisible.**
`exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_*` (2026-07-02, HARD_PASS),
`exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness` (HARD_PASS — note "fair_harness"
in the name, i.e. it was built specifically to be a fair test), `exp_substrate_pcgrad_cfrpe_stdp`
(HARD_PASS), and `exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE` (HARD_FAIL — the rescue failed; both
reported). The learning-rule layer is the one the memory index flags as "missing-LEARNING -> REUSE
hdlab/learner"; this family shows learning-rule work WAS done and is not indexed.

**conjunctive binding / role binding — 42 of 49 invisible.** The largest invisible block after
cleanup. Includes `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7` (2026-06-28,
HARD_PASS) and `exp_substrate_order_binding_family_v2_seed_7` (2026-07-01, HARD_PASS), alongside
`exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}` (2026-07-01, **HARD_FAIL on all three
seeds** — a consistent, well-replicated negative that is equally invisible).

**cleanup memory / resonator — 51 of 53 invisible.** Dominated by the phase-diagram programme:
`exp_substrate_pc_cleanup_family_phase_diagram_v1_seed_7` (2026-06-29) and `_v2_M_sweep_s11`
(2026-07-03), plus the `exp_stage1_regime_probe_*` / `exp_stage1_regime_map_storage_x_cleanup_v1_s7`
grid (2026-07-03). The memory index already carries "PHASE-DIAGRAM LEVERAGE DEFERRED — cash in at
RAM ceiling", so the DEFERRAL is remembered while the ~50 floored passes underneath it are not
enumerated anywhere.

### 1b. Notable individually-invisible cells in visible families

- `exp_substrate_acc_evc_adaptive_halting` (2026-07-08, HARD_PASS, floored) — ACC/EVC
  (expected-value-of-control) adaptive halting. The ONLY ACC cell with a floor. Invisible.
  Directly relevant to "when to stop reading/searching", which the foraging organ now owns.
- `exp_substrate_multihop_pfc_chunked_2hop_decomposition` —
  `HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING`. **CHAIN_GRADE is the project's highest historical
  verdict tier.** A chain-graded multi-hop PFC decomposition result, invisible to all four docs.
- `exp_hippocampal_sharp_wave_ripple_v1` (HARD_PASS, floored, undated) — the literal SWR organ.
  Invisible.
- `exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay` (2026-07-02, HARD_PASS) — a single
  cell carrying DG + CA3 + Marr + CLS + replay in its name, i.e. the integrated hippocampal
  architecture. Invisible.
- `exp_counterfactual_regret_comparison_vmpfc_v1` (2026-06-28, HARD_PASS) — vmPFC counterfactual
  regret. Invisible.
- `exp_substrate_dopamine_duration_extension_LR_v1` (HARD_PASS, floored) — the only basal-ganglia /
  dopamine cell with a floor. Invisible.
- `exp_read_xsent_coref_scene_protagonist_v1` (2026-07-24, HARD_PASS) and
  `exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_{7,13}` (Lappin-Leass, the classical
  pre-Centering algorithm) — coreference work predating the current Centering/Cb arc, invisible.
  **This one is live-relevant:** the 08-14 E3 result (`cba64a577`) concluded the whole Centering
  effect is the previous-clause window and Cf role-grading adds nothing. The Lappin-Leass drills are
  a different algorithm on the same competency and were never compared against it.
- `exp_consol_conjunction_replay_v1` (2026-07-15) —
  `REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONFOUND` and `exp_course_c_operator_fix_ssp_phase_rotation_replay_v1`
  (2026-07-11) — `OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE`. Two floored REFUTATIONS of
  consolidation-schedule advantage. **These matter to the 08-14 forgetting-kernel refutation**: the
  banner records the cascade organ as "REFUTED / unnecessary" as if that were a new finding, but
  consolidation scheduling was already refuted twice in July under different names.

---

*(sections 2-5 follow; see below)*
