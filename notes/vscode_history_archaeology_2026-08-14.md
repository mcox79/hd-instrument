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

## 2. THE CHAIN_GRADE TIER — 32 CELLS, 31 INVISIBLE

`CHAIN_GRADE` is the project's highest historical verdict tier (a full rubric: discriminator fires,
glass-box replay/tamper/causal-edit, non-ceiling, held-out). Enumerated by scanning every verdict
string for `CHAIN_GRADE` / `CHAIN-GRADE` — **NOT** by expected cell name.

**Result: 32 distinct cells carry a CHAIN_GRADE verdict. 31 of them appear in NONE of the four
docs.** The single exception, `exp_cleanup_floor_learned_encoder_v1`, has a registry row only.
26 of the 32 have a floor.

**This is the single largest invisible block in the repo, and it is the top of the quality ladder.**

### 2a. The three that matter most — VERIFIED ON DISK TODAY

All three are `run_mode: full`, git-**tracked**, and **clean at HEAD** (no working-tree diff), so
they are the same bytes that were committed. Read with `.venv` python.

**`exp_consolidated_reader_chaingrade_demo_v1`** — `CHAIN_GRADE_DEMONSTRATED`,
`ts 2026-07-23T21:11:15.667744+00:00`. All 4 rubric parts held.
**Floor:** naive positional baseline F1 **0.3407**; `arm_a_baseline_svo` F1 **0.2708** (prec 0.1956,
recall 0.44). Reader F1 **0.592**, margin **+0.2513**, recovering 18 gold tuples the naive baseline
misses. Non-ceiling shown on BOTH disjoint halves (A=0.2775, B=0.2332) and 7/7 lessons.
Glass-box: deterministic replay stable, sha256 audit hash tamper-detected, causal role-edit flips
the who-did-what tuple, bridge head-edit re-routes a candidate.
**A floored, full-run, glass-box, two-baseline win on the who-did-what reading competency, and it is
in no current doc.**

**`exp_consolidated_reader_hardsyntax_heldout_v1`** — `CHAIN_GRADE_HARDSYNTAX_EARNED`,
`ts 2026-07-23T23:48:58`. **Floor:** naive **0/24 (0.0)** — at floor. Reader **4/24 (0.1667)**,
discriminator margin +4, recovering `opposed_agent`, `opposed_patient`, `revealed_agent`,
`revealed_patient` that an ORDER baseline misses. Per-type: `passive_agent_by` n=9 reader 1 naive 0;
`passive_patient_preverbal` n=13 reader 2 naive 0. **N=24 across 11 novels — the cell itself calls
this a "small-N held-out probe". Underpowered; cite as a lead, not as evidence.** But the direction
is clean and the floor is a true zero.

**`exp_consolidated_reader_chaingrade_FULL_v1`** — `CHAIN_GRADE_HELDOUT_PARTIAL`,
`ts 2026-07-23T23:24:24`. **`chain_grade_heldout_earned = False`.** 2 of 4 bars held
(`ARM_C_glass_box_ok`, `ARM_D_non_ceiling_reported`); 2 short (`ARM_A_transfer`,
`ARM_B_discriminator_fires`). Composed LitBank who-did-what **10/13 (0.7692) vs naive 11** — the
reader LOSES to naive on held-out LitBank. STEP1 McGuffey composed f1=0.6423 (STEP1_HARD_PASS).

**The load-bearing reading of the triple, and why it should be in the plan.** Taken together these
three establish, on 2026-07-23, exactly the shape the project re-derived in August: **the reader
beats its baseline decisively IN-DOMAIN (McGuffey, +0.2513) and ATTENUATES OR REVERSES on HELD-OUT
prose (LitBank, reader 10 vs naive 11).** That is the same in-domain/held-out gap the current
banner describes as the entity-knowledge wall. It was measured, floored, glass-boxed and reported
honestly three weeks earlier under a verdict string (`CHAIN_GRADE_*`) that no current search
pattern looks for. **This is the strongest single instance of the USER's hypothesis being right.**

### 2b. The rest of the CHAIN_GRADE block (all invisible, floor status noted)

Multihop / routing arc — `exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1_smoke`
(`HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING`, floored, tracked, clean),
`..._multihop_bidirectional_meet_middle_v1_smoke` (`..._BIDIRECTIONAL`) and `_v2_META_M`
(`..._BIDIRECTIONAL_REVIVAL`), `..._multihop_compose_fly_lsh_multibank_partition*`
(`..._COMPOSITION_ADDITIVE`, `..._BARRIER_1_REVIVAL`),
`exp_gap1_partition_routing_bidirectional_collide_and_fly_lsh*` (`..._BOTH_ROUTERS`),
`exp_substrate_partition_routing_hierarchical_2level_v1` (`CHAIN_GRADE_AT_M_10M`, **no floor**).

Phase-diagram arc — `exp_phase_diagram_multihop_depth_extension_via_partition_o*`
(`CHAIN_GRADE_DEPTH_EXTENDS`, floored), `..._depth_ceiling_sweep_20_25_30_v1`
(`CHAIN_GRADE_DEPTH_CEILING_30`, **no floor**), `exp_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1`
(`CHAIN_GRADE_K_8192_3SEED`, floored, 3 seeds).

Scaling / verification arc — `exp_lln_point_mass_verification_N_V_C_f_sweep_v1`
(`CHAIN_GRADE_LLN_POINT_MASS_VERIFIED`, floored), `exp_lln_point_mass_large_vc_10k_1M_v1`
(`CHAIN_GRADE_COMMERCIAL_SCALE_VC`, floored),
`exp_substrate_intent_classifier_v2_production_scale_100plus` (`CHAIN_GRADE_AT_CLIFF_X`, floored),
`exp_substrate_stage3_integrated_audit_device_demo_v2_production` (`CHAIN_GRADE_AT_LOWER_X`, **no
floor**).

Basis / contamination arc — `exp_substrate_basis_layer_label_contamination_proof_v3_bank`
(`HARD_PASS_CHAIN_GRADE`) and `_v4_proof` (`HARD_PASS_CHAIN_GRADE_DEFINITIVE`), both floored.
`exp_substrate_role_tagged_compositional_generalization_on_*` (`HARD_PASS_CHAIN_GRADE`, floored).

Stage-1 arc — `exp_substrate_stage1_definitive_validation_v1` (`STAGE_1_CHAIN_GRADE_ALIVE`),
`exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1` (`CHAIN_GRADE`), both floored.

Schema arc — `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_*` (`CHAIN_GRADE_MULTI`),
**5 seeds, 2026-06-29, all floored** — the only DATED CHAIN_GRADE block before 07-23.

**NOT DONE:** individual hand-verification of the 26 CHAIN_GRADE cells in §2b. Only the three in
§2a plus `..._multihop_pfc_chunked_2hop_decomposition_v1_smoke` were opened and read. The rest are
reported at their recorded verdict + floor-key presence, which is weaker evidence, and are labelled
as such. Supersession was NOT checked for any of §2b.

---

## 3. MEASUREMENT-CONVENTION DRIFT — the key that unlocks the old material

The USER explicitly warned about this. It is severe, and it fully explains why the older arc is
invisible to current searches. Computed over all 7,649 metrics.json, bucketed by `ts_iso` month.

### 3a. Verdict-string vocabulary EXPLODED, then contracted

| month | files | DISTINCT verdict strings |
|---|---|---|
| 2026-06 | 386 | **13** |
| 2026-07 | 1,699 | **444** |
| 2026-08 | 370 | 151 |
| UNDATED | 4,975 | **1,003** |

June used a 13-word controlled vocabulary. July invented **444 distinct verdict strings for 1,699
files** — roughly one new string per four runs. **Any filter written against the current August
vocabulary is reading a language the July arc did not speak.** This is the mechanism behind the
prior sweep's finding that an exact-match filter misses ~24% of passes; the family view shows the
loss is not uniform — it is concentrated in July, which is when most brain-foundational work
happened.

### 3b. Verdict SHAPE by month

| shape | 2026-06 | 2026-07 | 2026-08 | UNDATED |
|---|---|---|---|---|
| exact `HARD_PASS` / `HARD-PASS` | 117 | 491 | 62 | 1,733 |
| `HARD_PASS` + prefix/suffix | 0 | **95** | 30 | 173 |
| `CHAIN_GRADE` variant | 5 | 3 | 0 | 15 |
| other PASS-containing | 0 | 48 | 37 | 308 |
| **bespoke (NO PASS/FAIL token at all)** | **104** | **426** | **110** | **717** |
| middle / partial | 89 | 306 | 61 | 1,060 |
| fail / refute | 71 | 326 | 70 | 960 |
| no `verdict` key at all | 0 | 0 | 1 | 218 |

**1,357 results carry a verdict with NO `PASS` or `FAIL` token anywhere in it** (e.g.
`OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE`, `MEANING_MATCH_PASS` is fine but
`CHAIN_GRADE_AT_M_10M`, `LANE_D_E2E_PASS`, `STAGE_1_CHAIN_GRADE_ALIVE`, `BET_B_PASS`,
`FOURSTAGE_HARD_PASS`, `PIPELINE_HARD_PASS`, `CASCADE_HARD_PASS` are not). A grep for `HARD_PASS`
finds `FOURSTAGE_HARD_PASS` only because it is a substring; it finds `CHAIN_GRADE_AT_CLIFF_X`
never. **218 results have no `verdict` key whatsoever** and are invisible to any verdict-based
search by construction.

### 3c. Hyphen-vs-underscore is real but RARE, and it is an AUGUST innovation

`HARD-PASS` (hyphen): 2026-06 **0**, 2026-07 **1**, 2026-08 **4**, UNDATED **1** — 6 total against
2,692 underscore. So the hyphen trap flagged in the memory index is genuine but tiny, and it does
NOT explain the older material. **The `_fulldev` suffix and the bespoke-vocabulary problem explain
far more.** Correcting the emphasis: hunting hyphens will recover 6 results; hunting bespoke
verdict strings will recover ~1,357.

### 3d. FLOOR-KEY NAMING drifted completely — this is the worst trap

The name of the control key changed every month:

| month | dominant floor/control key names |
|---|---|
| **2026-06** | `positive_control_result` (59), `random_arm_pathology` (29), `random_arm_pathology_pts` (29), `low_kv_mechanism_floor_met` (25), `n_FLOOR` (10), `all_floored` (10), `crlb_floor_computed` (8), `lift_over_baseline` (6) |
| **2026-07** | `baseline_in_band` (284), `crlb_floor_computed` (86), `chance` (73), `controls` (46), `positive_control_result` (41), `chance_theoretical` (21) |
| **2026-08** | `chance` (29), `stage0_bow_baseline_accuracy` (16), `positive_control` (15), `positive_control_self_retrieval` (12), `scramble_collapses` (11), `non_fork_controls` (9) |
| **UNDATED** | `crlb_floor_computed` (43), `beta_floor` (20), `baseline_in_band_check` (19), `chance` (17), `scramble` (13), `majority_floor` (12), `crumble_floor` (11) |

**The word `scramble` — the project's current canonical name for a floor — appears 11 times in
August and ZERO times in June.** June's floor was called `random_arm_pathology` or
`positive_control_result`. **A search for "does it have a scramble control" run over June's
results returns FALSE for every single one, and that answer is wrong.** July's dominant key,
`baseline_in_band` (284 files), is likewise not a word any current search uses. This is the
single highest-leverage drift finding in this sweep: **the floor test is the gate that decides
whether an old result counts, and the gate has been asking the wrong question of everything before
August.**

### 3e. THREE incompatible timestamp formats

- `2026-06-29T07:01:32Z` — Zulu suffix (June, most of July)
- `2026-07-23T21:11:15.667744+00:00` — microseconds + numeric UTC offset (the consolidated-reader
  CHAIN_GRADE block, 07-23)
- **absent entirely** — 5,193 of 7,649 files (68%)

A parser keyed on a trailing `Z` silently drops the 07-23 block, which is where the three most
live-relevant CHAIN_GRADE results live. **This is not hypothetical — it is exactly the block §2a
recovered.**

### 3e-bis. THE FLOOR IS USUALLY NOT A KEY — it is prose inside `verdict_msg`, or an ARM NAME

Discovered while hand-verifying §4. Of the brain-family cells opened, **most have NO top-level key
matching any floor word at all** — and yet every one of them IS floored. The floor is carried:
- **as an arm name**: `exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1` has arms
  `MARR / CORTEX / DG_ONLY / DENSE_HOPF / NO_CONSOL / NAIVE_WTA`. `CORTEX`, `NO_CONSOL` and
  `NAIVE_WTA` ARE the lesion controls. No key contains the word "control".
- **as prose in `verdict_msg`**: `exp_hippocampal_sharp_wave_ripple_v1` reads
  `fidelity_fast=1.0000 >= 0.7 vs random=0.0857`. The floor is `random=0.0857`, inside a string.
- **as a bracketed arm table in `verdict_msg`**: `exp_substrate_acc_evc_adaptive_halting_v1_smoke`
  reads `accpc[FIXED=0.0333 ADAPT=0.1839 RAND=0.0396 SCR=0.0369 ORC=0.1839]`.

**Therefore any key-based floor test UNDERCOUNTS floors badly, and the direction of the error is to
make old brain-foundational work look unfloored when it is in fact floored with 3-6 arms.** The
prior sweep's recursive key/value scan caught more than a top-level scan would, but neither reads
prose. **This, not the hyphen and not the `_fulldev` suffix, is the largest single reason the older
arc scores badly against current gates.**

### 3f. The 5,193 UNDATED results are a DIFFERENT CELL TEMPLATE, not merely undated

Top-level key vocabulary separates them cleanly. Dated cells (all months) carry `ts_iso` at
**100%** plus `anchor_name`, `config_version`, `elapsed_s`. The undated block instead leads with
`n_seeds` (2,908), `per_seed` (2,444), `config` (1,247), `N` (1,231) — a multi-seed sweep template
— and carries `anchor_name` on only 3,053 of 5,193 and `config_version` on 656. June-only markers
`_hardening_marker` (361) and `pid` (361) vanish after June.

**Consequence:** the undated block is not a dating gap to be patched, it is a distinct generation
of the harness. **68% of all results in the repo were produced by a cell template whose
conventions no current tool matches.** The prior sweep correctly refused to substitute mtime or
git-date; the finding here is *why* that matters — the whole template differs, so date is not the
only field that will not join.

---

## 4. VERIFIED-BUT-INVISIBLE — the named list (priority 2)

Each entry below was opened on disk TODAY with `.venv` python, by enumerating candidate directories
from a full `os.walk` index and taking the non-smoke variant first — **never by guessing a name**.
Run mode, floor and arm structure are quoted from the primary `metrics.json`. All are absent from
`notes/ORGAN_MAP.md`, `notes/SUBSTRATE_STRATEGY.md`, `notes/STATUS.md` and
`data/capability_registry.jsonl`.

Ordered by how directly they bear on a CURRENTLY-OPEN question.

### V1. `exp_read_xsent_coref_scene_protagonist_v1` — **THE 08-14 COREF CONCLUSION, REACHED ON 07-24**
`HARD_PASS`, **run_mode FULL**, `ts 2026-07-24T05:45:55`. Tracked, clean at HEAD.
Same-gender subset `sub_acc = 0.4003` vs backbone **0.2462** (delta **+0.1541**, sign_stability
1.000); overall xsent 0.4023 vs 0.2487, no regression.
**It carries its own refuting control and reports it:** LEVER 1 whole-doc topical FAILED on the
subset (0.2412, delta **-0.0050**) — "global protagonist over-applies". And the scene-structure
control: charset-detected 0.4003 vs **LOCALITY null max(fixed5=0.4070, Kmean-random=0.3710) =
0.4070**, delta **-0.0067**, so `scene_structure_supported = False` — **"the lever is LOCAL-WINDOW
subject"**.
**Why this is load-bearing.** Commit `cba64a577` (2026-08-14) concluded of the Centering/Cb arc:
*"the whole effect is the PREVIOUS-CLAUSE WINDOW, Cf role-grading adds nothing."* **That is the same
conclusion, on the same competency, reached three weeks earlier by a different mechanism and a
different control, and it is cited nowhere.** The E3 PHASE-1/PHASE-2 programme (`5f31c838f`,
`27a2f27a8`, `36a2a68aa`, `cba64a577`) re-derived it from scratch. Had this cell been visible, E3's
prereg could have STARTED from "the window is the lever, test whether anything beats it".

### V2. `exp_consol_conjunction_replay_v1` — **CONSOLIDATION SCHEDULING ALREADY REFUTED, 5-ARM FLOOR**
`REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT`,
**run_mode FULL, n_seeds 5**, `ts 2026-07-15T12:40:33`.
**Floor battery (the most complete in this sweep):** `chance = 0.5118`, `SHUFFLE = 0.5192`,
`FREQ_NULL = 0.4768` (HOM 0.4323 / POP 0.4768), `MEMO = 0.4768`, `ORACLE = 1.0000`.
Arms: `INTERLEAVED = 1.0000`, `CONTINUAL = 1.0000`. **Primary schedule-gap INTER-CONT = 0.0000**
(HP bar >= 0.0488 -> False; REFUTE bar <= 0.0100 -> met), votes 0/3. Validity gates all pass:
`freq_at_chance = True`, `shuffle_flat = True`, `compute_matched = True (mism 0.0000)`.
Positive direction retained: `readout_works INTER-FREQ = 0.5232` (>= 0.10).
**Why this is load-bearing.** The current banner records the forgetting-kernel / Benna-Fusi cascade
as REFUTED on 2026-08-14 and treats it as news. **Consolidation SCHEDULING was already refuted on
2026-07-15, at 5 seeds, compute-matched, with a complete floor battery** — and the same cell
positively attributes the conjunction effect to **the READ-OUT**, which is precisely where the C3
defect is now diagnosed to live. This is a July result pointing at the August diagnosis.
Corroborating sibling: `exp_course_c_operator_fix_ssp_phase_rotation_replay_v1` (2026-07-11),
`OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE`. Two independent July refutations, both dark.

### V3. `exp_consolidated_reader_chaingrade_demo_v1` + `_FULL_v1` + `_hardsyntax_heldout_v1`
Fully detailed in §2a. In one line: **the in-domain-wins / held-out-attenuates shape of the current
entity-knowledge wall was measured, floored, glass-boxed and honestly reported on 2026-07-23**
(McGuffey F1 0.592 vs naive 0.3407, +0.2513; LitBank held-out reader 10 vs naive 11).

### V4. `exp_substrate_acc_evc_adaptive_halting_v1_smoke` — ACC/EVC halting, ORACLE-MATCHING
`HARD_PASS`, **run_mode SMOKE, n_seeds 2**, `ts 2026-07-08T13:53:23`.
**5-arm floor, inside `verdict_msg`:** `accpc[FIXED=0.0333 ADAPT=0.1839 RAND=0.0396 SCR=0.0369
ORC=0.1839]`. `adapt_vs_fixed = 4.517x`, `adapt_vs_random = 3.640x`, `scramble_gap = 0.799`,
`closure = 1.000`. Task accuracy `acc[FIXED=0.133 ADAPT=0.733 ORC=0.733]` — **the adaptive halting
arm EQUALS THE ORACLE (0.733 vs 0.733)** while using fewer hops (3.99 vs 4.00). Signal-specificity
control `corr[A=1.000 S=-0.071]` — correlates with the true signal and NOT with the scrambled one.
Gates `nav_rail / baseline_band / pressure / repro` all True.
**HONEST CAVEAT, and it is the finding:** this exists ONLY as a SMOKE plus two SELFTESTs
(`_v1` and `_v1_selftest`, both `SELFTEST_OK`, 07-08/07-09). **There is no FULL run.** A
brain-mechanism arm that matches its own oracle with a 4-arm floor and a signal-specificity control
was smoked, self-tested twice, and never promoted. That is a process finding as much as a result.
Directly relevant: ACC/EVC "when to stop searching" is the same decision the newly-landed
information-foraging (MVT) organ now makes — **and the foraging prereg does not cite it.**

### V5. `exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1_smoke` — integrated hippocampal stack
`HARD_PASS`, **run_mode SMOKE**, `ts 2026-07-02T23:46:48`.
**Ablation ladder as ARM NAMES:** `MARR imm=1.000 after=0.000 pat=1.000 intf=0.000 sparse=0.0104`;
lesions `CORTEX imm=0.000`, `DG_ONLY pat=0.705`, `NO_CONSOL after=0.000`, `NAIVE_WTA imm=0.100`;
comparator `DENSE_HOPF imm=1.000`.
One cell carrying DG + CA3 + Marr + CLS + replay with a five-way lesion ladder. **SMOKE only.**
`after=0.000` on both MARR and NO_CONSOL is worth reading before reuse — the consolidation arm did
not retain, which is consistent with V2's refutation.

### V6. `exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1` — Hopfield INSIDE a real LM
`HARD_PASS`, **run_mode FULL, n_seeds 2**, no `ts_iso`.
Substrate-attention is training-stable inside Pythia-160M: `entropy_ratio(substrate/others) = 3.58`,
`grad_ratio = 0.6`, **`ppl_ratio(substrate/baseline) = 0.94`** — i.e. the substrate's own attention
mechanism reaches slightly BETTER perplexity than the baseline attention it replaced, in a real
transformer. A sibling exists for `llama_3_2_*`. Neither is in any doc; there is no
`hopfield` registry row. Floor = the baseline it is ratioed against; no separate scramble.

### V7. `exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_{7,13,...}` — k-WTA at production N
`HP_WM_SPARSITY_AXIS_CG_ARCH_FIX`, **run_mode FULL**, `ts 2026-07-02T00:31:28Z`, 7 seed dirs.
**Explicit floor KEYS (rare for this era):** `hp_random_floor = True`, `positive_control_wm_ok =
True`, `hp_in_band_mid_c = True`. `rho_c <= -0.60` at all 9 (M, alpha) pairs; c-lever range >= 0.10
at all 9; cross-seed cv < 0.15. The k-WTA family is **17 of 17 invisible** and this is its
best-evidenced member.

### V8. `exp_hopfield_spurious_minima_cpu_v1` — the control an attractor cleanup must pass
`HARD_PASS`, **run_mode SMOKE**, undated. `genuine-convergence = 0.957` (>= 0.90 bar): 96% of random
starts settle on a REAL stored pattern rather than a spurious attractor. Smoke only, but it is the
specific safety property a Hopfield read-out needs, and the two Tier-1 Hopfield assets recommended
by the prior sweep do not cite it.

### V9. `exp_hippocampal_sharp_wave_ripple_v1` — the literal SWR organ
`HARD_PASS`, **run_mode SMOKE**, undated. `fidelity_fast = 1.0000` (>= 0.7) **vs random = 0.0857**
(>2.0x bar); `wrong_fidelity = 0.0000` (<= 0.2); sub-checks A/B/C all 1.00. Floor is prose. Smoke
only.

### Cross-cutting reading of V1-V9

Two of the nine (**V1, V2**) are not merely invisible — **they answer questions the project spent
August re-opening.** That is the concrete, costed form of the USER's hypothesis: the loss is not
only unused assets, it is **repeated work**. Four of the nine (**V4, V5, V8, V9**) are
SMOKE-ONLY brain-mechanism results with strong arm structure that were never promoted to FULL —
a distinct and separately actionable category: *not wrong, not superseded, just never finished.*

**SUPERSESSION — NOT DONE except where stated.** V1 is not superseded by the E3 arc (E3 tested
Centering Cb tiers, a DIFFERENT mechanism, on a different gold set; it CORROBORATES rather than
replaces). V2 is not superseded by the 08-14 forgetting-kernel work (that tested a sign-readout and
a cascade kernel, not schedule). For V3-V9 no supersession check was run, and none should be assumed.

## 5. THE INVISIBLE NEGATIVES — the mirror finding, and it may cost more than the positives

The USER's hypothesis was about missed PROGRESS. The inventory surfaces the symmetric problem,
which no previous sweep looked for: **failed and middling arcs are ALSO invisible, so a mechanism
can be re-proposed as novel after having already been attacked and beaten.**

### 5a. ATL / hub-and-spoke — attacked THREE times, never passed, and re-scanned yesterday

Enumerated every cell whose name matches `atl|hub_and_spoke|hub_spoke|anterior_temporal`.
**7 stems. ZERO floored passes. The arc is a documented failure ladder:**

| cell | verdict | floor present |
|---|---|---|
| `exp_substrate_hub_spoke_E1_encoder_v1` | **HARD_FAIL** | yes |
| `exp_substrate_hub_spoke_E1_encoder_v1_smoke` | MIDDLE_BAND | yes |
| `exp_substrate_hub_spoke_E1_v2_diverse_algorithm` | MIDDLE_BAND | yes |
| `exp_substrate_hub_spoke_E1_v2_diverse_algorithm_smoke` | MIDDLE_BAND | yes |
| `exp_substrate_hub_spoke_E1_v2_diverse_algorithm_smoke_ti*` | MIDDLE_BAND | yes |
| `exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing` | **HARD_FAIL** | yes |
| `exp_hub_spoke_cross_encoder_alignment_smoke_v1` (+`_selftest`) | SELFTEST_OK | no |

Three generations — a base encoder, a diverse-algorithm v2, and an MRC-calibrated-routing v3 —
all floored, none clearing. All UNDATED (the pre-`ts_iso` template, §3f).

**Why this matters right now.** ATL/hub-and-spoke is the brain's answer to exactly the defect the
substrate currently has: the ATL is the graded, amodal hub whose job is to hold near-neighbours
apart. `notes/lit_scan_atl_hub_and_spoke_2026-08-13.md` (28.4 KB, written yesterday) went to the
literature on this mechanism. **VERIFIED: that note contains no reference to `hub_spoke_E1`,
`E1_encoder`, `E1_v2`, `E1_v3` or `MRC_calibrated` — and neither does `ORGAN_MAP.md`,
`SUBSTRATE_STRATEGY.md` or `STATUS.md`.** (Checked by reading all four files and testing for the
literal strings, with `.venv` python.)

So the project holds three floored in-house refutations of its own ATL implementations and
commissioned a fresh literature scan of the same mechanism without citing any of them. That is not
a wasted lit scan — the literature is worth having — but the scan could not perform its most
valuable function, which is to explain WHY the three in-house attempts failed and what the
literature says to do differently.

### 5b. Cerebellum — built, then found to have no consumer

- `exp_pfc_gate_cerebellum_sr_rollout_v1_smoke` (2026-07-07) —
  **`HARD_FAIL_NO_CEREBELLAR_CONSUMER`**, floored.
- `exp_substrate_cerebellar_random_expansion_write_v1` — **HARD_FAIL**, floored.
- `exp_pfc_gate_cerebellum_sr_rollout_v1` — `SELFTEST_OK`.

**The verdict string itself is the finding.** `HARD_FAIL_NO_CEREBELLAR_CONSUMER` is a machine-
readable record of the ISLANDING failure mode: an organ was built and nothing downstream consumed
it. The memory index's "WIRE DON'T ISLAND" rule and the standing registry-leak audit both describe
this class in the abstract; here is a cell that measured a specific instance on 2026-07-07 and
named it in its verdict. It is in no doc.

### 5c. Entorhinal / grid — one cell, a pass, and no floor

`exp_crt_multi_scale_grid_cell_composition_v1` — `HARD_PASS`, **no floor**, undated. The entire
entorhinal/grid family is this one unfloored cell. Reported for completeness; **an unfloored pass
is not evidence** and it is ranked accordingly.

### 5d. Consistent, well-replicated negatives that are also dark

- `exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}` (2026-07-01) — **HARD_FAIL on all three
  seeds**, floored. A three-seed replicated negative on binding-operator-by-capacity.
- `exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE` — **HARD_FAIL**; the rescue attempt on the STDP arc
  failed. The `_RESCUE` suffix is itself a convention no current search knows about.
- `exp_grounding_iterative_settling_cascade_depth_v1` (2026-07-09) —
  **`HARD_FAIL_NO_EXTENSION`**: iterative settling does not extend with depth. Directly relevant to
  the cue-clamped iterative-cleanup asset (A6) the prior sweep listed as a Tier-1 lead — **this cell
  is the closest thing to a prior refutation of that lead, and the prior sweep did not surface it**
  because it was hunting passes, not failures.
- `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_c*` (2026-06-28) — HARD_FAIL on
  three variants, floored, alongside `..._v2_narrow_re*` HARD_PASS. A pass and a fail in the same
  family on the same day; only reading both tells you where the cliff is.

**The general rule this suggests.** A capability index that records only WIRE-or-SHELVE for passes
is half an index. The failures are what stop the next agent from re-proposing a beaten mechanism,
and they are exactly what the current docs do not carry. `HARD_FAIL_NO_CEREBELLAR_CONSUMER`,
`HARD_FAIL_NO_EXTENSION` and the three-seed binding failure are worth more per byte than most of
the passes in §4, because they are cheap to record and they prevent expensive repeats.

## 6. THE HONEST HEADLINE NUMBER — 72 FULL, FLOORED, INVISIBLE

§1's 251 is a floor-KEY count and includes smokes. Tightening it to the strictest defensible gate:
opened all 251 primary `metrics.json` with `.venv` python and kept only `run_mode == "full"`.

**Of the 251 floored brain-mechanism passes, 97 are FULL runs. 72 of those 97 are invisible to all
four planning artifacts.** The remainder: 88 smoke, 39 selftest, 20 with no `run_mode` key, 5 with
a junk `run_mode`.

| family | FULL + floored + INVISIBLE |
|---|---|
| cleanup memory / resonator | **19** |
| conjunctive binding / role binding | **14** |
| CLS / systems consolidation | **8** |
| hippocampus CA3/CA1/DG | **6** |
| attractor / Hopfield | 5 |
| k-WTA / sparse coding | 5 |
| replay / sharp-wave ripple | 5 |
| Hebbian/STDP, PFC/IFG, V1/VWFA, forgetting | 2 each |
| Centering/coref, predictive coding | 1 each |
| **TOTAL** | **72** |

**72 is the number to quote.** It is FULL-run only, floored, pass-flavoured, brain-mechanism-named,
and named in no plan doc or registry row. It is the tightest form of the USER's hypothesis and it
holds.

### 6a. Three more verified today, and one of them is the best result in this sweep

**`exp_consolidated_reader_passive_mechanism_heldout_v1` — THE STRONGEST INVISIBLE RESULT FOUND.**
`PASSIVE_MECHANISM_CAPABILITY_EARNED`, **run_mode FULL**, `ts 2026-07-24T00:29:16`.
**Floor: `naive_acc = 0.0`, `n_naive = 0`, plus a `naive_hash` for reproducibility.**
Reader recovers **23/24 who-did-what (acc = 0.9583) vs naive 0/24 (0.0), margin +23**, on
**INDEPENDENT HELD-OUT passages**. The mechanism fires on **12/13 held-out passages, up from
OFF = 2** (delta +10) — i.e. an explicit flag-ON/flag-OFF ablation. Non-regression verified:
McGuffey composed F1 `base = 0.5868 -> on = 0.5868`, unchanged. P2 ablation with the flag OFF
reproduces the banked parse-luck baseline exactly. Fired predicates are listed individually
(`assailed, confined, evinced, freed, made, met, opposed, overset, overtaken, revealed, supplied,
washed`) and the rule is stated as systematic (`subject -> PATIENT, by-obj -> AGENT`), not learned
per-item.
**Why this is the best one.** It is a FULL, held-out, floored-at-zero, ablated, non-regressing,
glass-box win on a NAMED CONSTRUCTION TYPE (the passive). The standing anchor
*"comprehension = a growing library of construction-competencies, not one objective"* asks for
exactly this artifact — **a single construction type with its own learned, modular, glass-box
capacity.** It exists, it is at 0.9583 against a true zero floor, it landed on 2026-07-24, and it is
in **no** plan doc and **no** registry row. If any single item in this sweep should be promoted,
it is this one.
*Honest caveats:* n = 24 items / 13 passages is small; `n_seeds` is null (single run); and the
mechanism is a systematic syntactic rule, so the win is a PARSER-side competency, not evidence
about the substrate's own representation. It should be filed under the reading pipeline, not
under C3.

**`exp_resonator_verifier_readout_v1` — a read-out that REACHES ITS OWN ORACLE.**
`HARD_PASS`, **run_mode FULL, n_seeds 3**, undated.
K4 verifier `harvest = 0.806` (bar >= 0.50) at T0 = 0.50, **+0.353 over plurality = 0.453**, with
**`oracle_any = 0.806`** and **`baseline_K4 = 0.133`**. The verifier's harvest EQUALS the oracle.
The cell's own words: *"Reconstruction verifier harvests the already-reached answer; the residual
gap WAS aggregation-loss, confirming the VET diagnostic."*
**Why this is live-relevant.** The current C3 diagnosis is that retrieval is fine
(`SELF_RETRIEVAL 0.786`) and the failure is selecting the right member from the right neighbourhood
— i.e. **a loss at aggregation/selection, not at retrieval.** This cell states that same diagnosis
and reports a mechanism that closes it to the oracle on its own task. Two siblings in the same
invisible block point the same way: `exp_resonator_theta_gamma_peel_v1` and
`exp_resonator_deflation_lowsnr_v1` (both FULL, HARD_PASS, invisible), and the peel/deflation family
is the same mechanism class as the prior sweep's top-ranked A1 (`peel_sic`). **This strengthens the
prior sweep's A1 recommendation with independent, previously-unlisted evidence.**
*Honest caveat:* no `ts_iso`, and the floor is prose (`baseline_K4 = 0.133`, `plurality = 0.453`),
not a key.

**`exp_consol_inductive_entity_replay_cskg_v1` — the THIRD July replay/consolidation refutation.**
`REFUTE_REPLAY_NO_INDUCTIVE_ADVANTAGE`, **run_mode FULL, n_seeds 5**, `ts 2026-07-15T11:40:51`.
Full floor battery on inductive held-out MRR (nq = 2000): `RANDOM = 0.0021`, `SHUFFLE = 0.0026`,
`SCRAMBLE = 0.0274`, `POP_RELFREQ = 0.0576`, `ORACLE = 0.1030`; arms `INTERLEAVED = 0.0556`,
`CONTINUAL = 0.0307`. Headroom fires (`ratio = 50.1x`). Replay **beats CONTINUAL (+0.0249)** but
**FAILS to beat the popularity baseline (`beat_pop = -0.0020`, bar >= 0.0101)** — and the cell
reports that as the refutation rather than headlining the arm it won.
Together with V2 (`exp_consol_conjunction_replay_v1`, same day-range, 5 seeds) and
`exp_course_c_operator_fix_ssp_phase_rotation_replay_v1`, **there are THREE independent, floored,
multi-seed July refutations of replay/consolidation advantage, all invisible.** The 08-14 banner
records the cascade/forgetting-kernel refutation as a fresh conclusion. It is the fourth.

### 6b. Other FULL+floored+invisible cells worth a second look (NOT individually verified)

Listed so they are visible, explicitly WITHOUT hand-verification — they carry their recorded
verdict only, which is weaker evidence:
`exp_substrate_operational_wall_dual_readout_bit_matched_*` (3 variants, HARD_PASS),
`exp_object_permanence_binding_stability_v1` (2026-07-09, HARD_PASS),
`exp_cortex_attention_binding_router_v1/v2_seed_{7,13,19}` (HARD_PASS),
`exp_cross_modal_binding_4_5_modality_v1_seed_{13,19}` (2026-07-01) and
`exp_substrate_cross_modal_binding_3rd_modality_v1_seed_*`,
`exp_interference_avoidance_conjunctive_vs_additive_v*`,
`exp_e3b_permutation_binding_endtask_cpu_v1`, `exp_substrate_permutation_binding_multiocc_v2`,
`exp_cls_distributed_protection_heldout_replay_v1`, `exp_substrate_continual_NREM_replay_v1`,
`exp_c3_compressed_sequence_replay_v1_timing`,
`exp_substrate_multihop_consolidation_memory_v1`, `exp_consolidation_correct_regimes_v1`
(2026-07-16), `exp_d2_7_intentional_forgetting_cpu_v1`,
`exp_fuzzy_shard_router_attractor_stage12_v1` (2026-07-17),
`exp_substrate_resonator_focus_lever_depth_v2`,
`exp_stage2_cleanup_latency_operating_curve_v1_seed_*`,
`exp_pfc_gate_branching_depth_entropy_grid_v1` (2026-07-05),
`exp_lap2_9_predictive_coding_cpu_v1`.
Also in the block and already covered by the prior sweep:
`exp_dense_hopfield_readout_capacity_correlated_codes_v1` (its A2),
`exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` (its A4),
`exp_reader_image_word_grounding_v1` and `exp_vision_integrated_recognize_bind_ground_v1`
(its Tier 2) — this sweep independently re-derived them from the brain-family angle, which is a
weak convergence check between two differently-constructed enumerations.

### 6c. REGISTRY COVERAGE BY MECHANISM — a fairness correction to §1

§1's "invisible" test is a CELL-NAME test. To avoid overstating, the registry was also searched by
MECHANISM TERM (`data/capability_registry.jsonl`, 127 rows, case-insensitive substring count):

| well covered | term count | ZERO or near-zero coverage | term count |
|---|---|---|---|
| coref | 143 | **k-WTA / kwta** | **0** |
| binding | 62 | **STDP** | **0** |
| consolidat* | 45 | **sharp_wave / ripple** | **0** |
| situation_model | 42 | **dentate** | **0** |
| cleanup | 25 | **acc_evc** | **0** |
| attractor | 21 | **cerebell*** | **0** |
| replay | 18 | **hub_spoke** | **0** |
| foraging | 17 | sparsity | 1 |
| hebbian | 6 | pattern_separation | 1 |
| predictive_coding | 6 | hopfield | 2 |
| resonator / divisive / centering | 4 each | atl | 2 |

**This is a genuine correction to the strong reading of §1.** The registry is NOT blind to
brain mechanisms in general — coref, binding, consolidation and situation-model are well
represented. **But seven mechanisms have literally zero registry presence: k-WTA, STDP,
sharp-wave ripple, dentate gyrus, ACC/EVC, cerebellum, and hub-and-spoke.** Three of those
(k-WTA, SWR, DG) have FULL floored passes on disk; two (cerebellum, hub-and-spoke) have only
floored FAILURES, which is exactly the material §5 argues should be recorded and is not.

So the precise claim is: **coverage is bimodal.** The mechanisms worked on RECENTLY are indexed;
the June-July arc is not, and the sparse-coding / spike-timing / hippocampal-replay-primitive
layer has no index entry at all.

## 7. THE BIGGEST FINDING — AN ENTIRE CERTIFICATION LEDGER THAT NO 2026-08-14 SWEEP TOUCHED

This section supersedes §2's framing. §2 is not wrong, it is **6% of the truth.**

### 7a. How it was found

Not by searching `data/`. By reading NOTE FILENAMES. A filename census of `notes/` surfaced
**`notes/research_experimental_archaeology_comprehensive_inventory_2026-06-25.md`** (48 KB) — a
**prior archaeology sweep, USER-directed, on 2026-06-25, with almost this exact brief.** Its opening
quotes the USER:

> "we've never properly crawled through the existing experimental data and really understood the
> meaning of it and filed it correctly... should we do a proper accounting of all the results and
> the relevance for current and future work?"

That note names its tooling and its join key. **All of it still exists on disk:**

| artifact | status | size | mtime |
|---|---|---|---|
| `data/_archaeology_extractor.py` | **EXISTS** | 7,477 B | 2026-06-25 |
| `data/_archaeology_synthesize.py` | **EXISTS** | 12,904 B | 2026-06-25 |
| `data/_archaeology_inventory_enriched.jsonl` | **EXISTS** | 2,418,546 B | 2026-06-25 |
| `data/_archaeology_summary.json` | **EXISTS** | 99,430 B | 2026-06-25 |
| **`data/substrate_index/meta/cert_ledger.jsonl`** | **EXISTS** | **4,553,798 B** | **2026-08-03** |

### 7b. The cert ledger, measured today

`data/substrate_index/meta/cert_ledger.jsonl` — **2,031 rows, 0 unparseable.** This is a SECOND,
INDEPENDENT results index. It is not `data/capability_registry.jsonl` (127 rows) and it is not
`metrics.json`. Its mtime is **2026-08-03**, so it was live during the current arc.

| `cert_status` | rows |
|---|---|
| **`chain_grade`** | **540** |
| (none) | 253 |
| `proven-bound` | 208 |
| `measured_mechanism` | 197 |
| `under_classified` | 149 |
| `honest_negative` | 84 |
| `custom` | 54 |
| `proven_bound` | 35 |
| `hard_fail` | 32 |
| `middle_band` | 26 |
| `cert_ruling_test_design_failure` | 17 |
| `honest-negative` | 11 |
| **`chain-grade`** | **10** |
| `mm_tentative_methodology_rule`, `observation`, `proven-negative`, `honest_negative_proven_bound`, `chain_grade_meta_rule`, `test_design_infra_failure`, `measured_mechanism_tentative_synthesis` | 4-9 each |

**Total chain-graded rows = 550** (`chain_grade` 540 + `chain-grade` 10).

### 7c. THE NUMBER

- **550 chain-graded ledger rows → 506 DISTINCT CELLS.**
- **537 distinct `atom_id`s** carry a chain-grade certification.
- **Of the 506 chain-graded cells, 13 are named in any of the four planning docs. 493 ARE NOT.**
- **Of the 537 chain-graded atom IDs, ZERO appear in any of the four docs.**

**Compare with §2, which searched `metrics.json` verdict strings and found 32 CHAIN_GRADE cells.
The real figure is 506. A verdict-string search recovers 6% of the chain-graded work.**

The reason is pure measurement-convention drift, and it is the single most important instance in
this note: **chain-grade is not primarily a VERDICT STRING in `metrics.json`. It is a
`cert_status` FIELD in a separate ledger.** No tool in the current arc reads that ledger. Neither
`notes/vscode_week_results_validity_audit_2026-08-14.md` nor
`notes/vscode_era_unrecognised_assets_2026-08-14.md` mentions `cert_ledger.jsonl`, and neither does
`ORGAN_MAP.md`, `SUBSTRATE_STRATEGY.md`, `STATUS.md` or `capability_registry.jsonl`.

### 7d. The ledger has its OWN internal drift — three field-value pairs split by punctuation

Inside the SAME field, in the SAME file:
- `chain_grade` **540** vs `chain-grade` **10**
- `proven-bound` **208** vs `proven_bound` **35**
- `honest_negative` **84** vs `honest-negative` **11**

**Any exact-match filter on `cert_status` silently loses 56 rows (10 + 35 + 11), including 10
chain-grades.** This is the hyphen trap from the memory index — but it lives HERE, in the cert
ledger, at 9x the rate it occurs in `metrics.json` verdict strings (6 total there, §3c).
**The memory index's hyphen warning is correct and has been pointed at the wrong file.**

Also: `ts_iso` is present on only 747 of 2,031 rows and `ts` on 1,953, so **1,282 rows carry no
parseable month** — the same undated problem as §3f, in a second index.

### 7e. What the `atom_id`s actually are

They are not integers. They are **content-addressed semantic slugs**, e.g.
`math::T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1`, and at the long end they encode
an ENTIRE result in the identifier — one sampled atom is a ~1,400-character slug recording arms,
floors, per-seed margins, controls and a commit hash inline.

**This resolves the numeric atom references in the memory index** ("29587", "banked 29590"). Those
numbers appear INSIDE the slugs as cross-references — e.g. one atom is named
`..._CHAIN_GRADE_VET_CONFIRM_CLEAN_WIN_PROMOTES_29590_from_MEASURED_MECHANISM_...` and another
`..._AMENDS_29631_removes_gold_verified_false_caveat_...`. So the atoms form a **versioned,
self-amending citation graph** — atoms promote, amend and supersede other atoms by number.
`supersedes` is a populated field on **1,249 rows**.

**This is a far richer provenance structure than anything in the current planning docs, and it is
entirely unread by the current arc.** 1,925 distinct atoms exist in total.

### 7f. What the 2026-06-25 sweep already concluded — and it is the same conclusion as today

Its own headline numbers, quoted from the note (NOT recomputed by me — see §9):
- 3,269 full experiments banked (excluding 816 smoke); 201 lacking a verdict field.
- All-time: 1,402 HARD_PASS, 591 MIDDLE_BAND, 526 HARD_FAIL, 22 KILLED, ~700 other.
- Cert ledger at that date: 718 rows; chain_grade 466, under_classified 149,
  measured_mechanism 76, honest_negative 17.
- **"2026-06 HARD_PASS NOT in cert ledger at all: 841 (65% of recent HARD_PASS). This IS the
  user's pain. The cert pipeline is dropping the majority of recent passes."**

**Read that last line against today's finding.** On 2026-06-25 the diagnosis was that 65% of passes
never reached the cert ledger. Today's finding is that **97% of what DID reach the cert ledger
never reached the planning docs.** The leak moved one stage downstream and got worse. The
2026-06-25 note also flagged a second thing worth carrying forward: *substrate-as-LM was the
single most-tested capability AND the worst-performing* (81 experiments, 14% HARD_PASS, 42%
HARD_FAIL) — the only capability with an HP:HF ratio below 1.0.

### 7g. Consequence for the rest of this note

§1's family inventory and §6's "72 FULL+floored+invisible" were computed from `metrics.json` only.
**They are therefore LOWER BOUNDS.** They do not incorporate the cert ledger's 506 chain-graded
cells. Reconciling the two indexes is the highest-value follow-up available and is **NOT DONE** —
see §9. Nothing in §1-§6 is retracted; all of it is understated.

---

## 7h. THE PERIODIC WHOLE-STACK REVIEWS — what the FILENAME CENSUS shows (priority 4)

A parallel agent owns the notes-side hunt (`notes/stack_review_lineage_2026-08-14.md`). Reported
here is only the CENSUS, which is measurement rather than reading, plus what it implies.

**`notes/` holds 9,830 markdown files.** By date suffix:

| month | notes |
|---|---|
| 2026-05 | 394 |
| **2026-06** | **6,209** |
| 2026-07 | 652 |
| 2026-08 | 253 |

**63% of the entire notes corpus is from June.** And **4,891 files (50%) use the legacy
`<from>_to_<recipient>_*.md` naming** that `CLAUDE.md` explicitly retires ("Do NOT use
`<from>_to_<recipient>_*.md` filenames; those came from the legacy ferry mechanism"). Half the
written record is in a naming convention the current model has abandoned — a filename-shaped
instance of exactly the drift §3 documents in metrics.

**A recurring whole-stack review cadence is visible in the filenames**, spanning May to August:

- 2026-05-21 `synthesis_design_space_audit`; `strategy_research_angles_inventory`;
  `meta_request_to_strategy_capability_test_inventory`
- 2026-05-23 `research_comprehensive_audit`
- 2026-05-29 `master_synthesis_v278_all_research`; `strategic_synthesis_v265_v276`
- 2026-06-04 `exp_dev_state_of_experiments`
- 2026-06-08 `research_STATE_OF_PLAY`
- 2026-06-13 `research_TRACKING_DOCUMENT_RESYNTHESIS_post_audit_cycle_substrate_state_..._canonical_state_record_all_5_sessions`
- **2026-06-18 the CAPABILITY_MAP series** — `research_to_skunkworks_CAPABILITY_MAP_atom_DRAFT_FINAL_VET_ask`,
  `..._LANDED_verify_plus_parallel_landings`, `..._corrected_atom_unset_2_quick_reverify_ask`, and the
  auditor's ruling **`skunkworks_to_research_432_map_VET_capability_map_kind_APPROVE_honest_61_not_432`**
  — i.e. a capability map was VET'd DOWN from 432 claimed to 61 honest. That deflation event is
  the direct ancestor of today's registry, and it is not referenced in any current doc.
- 2026-06-23 `research_negative_landings_evidence_totality_synthesis` — a synthesis OF NEGATIVES,
  the artifact §5 argues is missing today. It existed.
- **2026-06-25 `research_experimental_archaeology_comprehensive_inventory`** (§7a) +
  `research_capability_audit_CORRECTION_v2` + `research_drill_all_open_load_bearing_items`
- 2026-07-05 `research_thrust_brain_component_inventory_and_build_priorities`
- 2026-07-20 `drill5x_1_brain_reading_components_inventory`
- 2026-07-22 `reader_capability_map_and_glassbox_improvement_roadmap`
- 2026-07-23 `reader_space_MAP_and_deep_lessons_SESSION_SYNTHESIS`
- 2026-08-01 `research_brain_fidelity_broad_audit_synthesis`
- 2026-08-06 `brain_component_map_narrative_comprehension_ROADMAP`
- 2026-08-09 `director_brain_fidelity_SYNTHESIS_and_direction_verdict`

Plus the superseded standing maps still on disk: `substrate_capability_map.md`,
`substrate_capability_map_history.md`, `capability_scorecard.md` — the three `CLAUDE.md` records as
having "rotted silently".

**Conclusion for priority 4: the USER is right that periodic whole-stack reviews happened. There
have been at least fifteen since 2026-05-21, roughly fortnightly.** The failure is not that reviews
were never done — it is that **each review started over rather than extending the last one**, and
none of them is cited by the current planning docs. The 2026-06-25 archaeology sweep is the
clearest case: it built durable tooling, wrote 48 KB of findings, diagnosed the exact leak, and
seven weeks later three fresh sweeps ran on 2026-08-14 without any of the three knowing it existed.

**NOT DONE:** reading the CONTENT of the fifteen reviews. Only the 2026-06-25 one was opened (first
3,000 chars). The rest are identified by filename and date only. The parallel agent's
`stack_review_lineage_2026-08-14.md` should be treated as authoritative on content.
