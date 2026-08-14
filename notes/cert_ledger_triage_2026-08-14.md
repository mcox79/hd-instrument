# CERT LEDGER TRIAGE — `data/substrate_index/meta/cert_ledger.jsonl`
**2026-08-14.** Read-only triage. Written incrementally; sections marked **NOT DONE** are gaps, not omissions.

> **What this file is for.** A cold session should be able to open this, read §5, and pick a next experiment
> without re-reading the 4.5 MB ledger. Everything here is re-derived from disk, not from prior planning docs.
> Method scripts were temp-only (`C:/Users/marsh/AppData/Local/Temp/full.py` etc.), not committed — the numbers
> below are reproducible from the recipe stated in each section.

---

## 0. TLDR

- **574 terminal chain-graded cells survive** (not superseded, latest ruling still chain-grade).
  Not 506 — see §1 for why the figures differ and which is right.
- The `supersedes` graph is **almost inert**: only **2** chain-graded cells are killed by a cross-cell
  supersedes edge, and **13** more were demoted by a later *in-place* ruling. 93 supersede references are
  **dangling** (32 point at 16-hex content hashes that appear exactly once in the whole ledger and resolve
  to nothing; 61 are self-references or unparseable). **The citation graph is not a working provenance
  chain — treat it as decoration, and derive liveness from the latest ruling per cell instead.**
- **552/574 terminal cells have a live `metrics.json` on disk.** 21 have no resolvable directory
  (almost all are cross-seed *aggregate* atoms whose artifacts live in per-seed dirs), 1 has a directory
  but no `metrics.json`.
- **Floors are the weak spot**: only **132/574 (23%)** carry a detectable control/comparison arm.
  **322 (56%) have no floor shape of any kind** in their metrics.json — a large slice of those are
  saturation-by-construction grids (`exp_q_a3_l*_cross_layer_composition`, "all 97 levels EXACT-1.0"),
  which are constructions, not capability wins.
- The **June-convention warning in the brief is confirmed and is worse than stated**: of 60 terminal cells
  dated June, **zero** contain the string `scramble`, yet **33 of them do have a genuine control arm**
  under other names. A scramble-keyed floor test would have reported 0/60 floors for June. It is wrong.

---

## 1. TRUE SCHEMA (re-derived, do not trust the 506/2031 figures)

**Rows: 2031.** All 2031 parse as JSON, 0 malformed. (This matches the brief.)

**The ledger is schema-free.** 2031 rows carry **>200 distinct top-level field names**. Not one field is
present on all rows. The "core" is thin:

| field | rows present | rows non-null |
|---|---|---|
| `verified_off_data` | 1991 | 1377 |
| `atom_id` | 1980 | 1978 |
| `ts` | 1953 | 1350 |
| `cert_status` | 1778 | 1778 |
| `cell_commit` | 1694 | 1538 |
| `op` | 1648 | 1648 |
| `cert_class` | 1630 | 1485 |
| `atomized_by` | 1611 | 1611 |
| `cert_increment_delta` | 1537 | 1537 |
| `verdict` | 1450 | 1450 |
| `note` | 1376 | 1376 |
| `supersedes` | 1249 | **67** |
| `referent_pointer` | 1192 | 1192 |
| `ts_iso` | 747 | 747 |
| `tier` | 732 | 732 |

…then a tail of ~180 fields appearing on <100 rows each (`anchor`, `auditor`, `decision`, `headline`,
`grade`, `disposition`, `fairness_verdict`, `revival_criteria`, `honest_scope`, `hf_attribution`,
`brain_check`, `cell_content_sha256_16`, `framing_correction_vs_director`, …). `referent_pointer` is a
nested dict with `{notes_path, metrics_path, atom_qualified_id}`.

**`cert_status` has 357 distinct values.** It is *not* an enum. The head:

```
chain_grade 540 | proven-bound 208 | measured_mechanism 197 | under_classified 149 |
honest_negative 84 | custom 54 | proven_bound 35 | hard_fail 32 | middle_band 26 |
cert_ruling_test_design_failure 17 | honest-negative 11 | chain-grade 10 | ...
```

then a 340-long tail of one-off prose statuses. **Chain-grade must be detected by regex
`chain[_\- ]?grade`, not by equality** — `chain_grade`, `chain-grade`, `chain_grade_meta_rule`,
`chain_grade_honest_negative`, `chain_grade_measured_bound`, `chain_grade_amendment_tier_promotion`,
`chain_grade_per_seed_promotes_at_3_seed` are all distinct strings. Exact-match on `chain_grade`
undercounts by ~14%.

`op` likewise has **114** distinct values (`cert_ruling` 1011, `landed_vet_atomize` 175, `cert_pending` 161,
`add` 59, `atomize` 50, `cert_relabel` 33, then 108 bespoke one-offs, some 400 chars long).
`cert_increment_delta` has 31 distinct values — mostly `1`/`0`, but 22 of them are **prose sentences**
(`"+1 MEASURED_MECHANISM (proven-bound; ...)"`), i.e. an integer field used as a comment field.

### Dates
`ts` is a **float epoch** on most rows, an ISO string on some, and null on 681. Union of
`ts`/`ts_iso`/`ts_day`/`atomized_date`/`audit_ts`/`timestamp`/`created_ts` plus dates embedded in
`atomized_by` slugs gives **1380/2031 dated rows**, range **2026-06-22 → 2026-08-03**
(June 420, July 910, August 50). 651 rows are undated in the ledger; for those the run date must come
from `ts_iso` **inside the cell's own `metrics.json`** — as the brief warns, mtimes and git dates lie.
Disk recovery adds a run date for 69 terminal cells, extending the true range back to **2026-06-18**.

### Count reconciliation vs the 506 / 1925 figures in the brief
My re-derivation, on the same file:

| quantity | brief | re-derived | note |
|---|---|---|---|
| rows | 2031 | **2031** | agrees |
| distinct atoms | 1925 | **1978** non-null `atom_id`, 1721 distinct | `atom_id` is not unique per row |
| chain-graded cells | 506 | **589 ever / 576 latest / 574 terminal** | see below |

The gap is **cell-name resolution**, not ledger content. 242 rows resolve a cell only from a
free-text `atom_id` slug (e.g. `math::T3/EXP_substrate_lock_in_amp_..._3seed_chain_grade_..._2026-06-28`)
and 390 resolve only from an `anchor`/`anchor_name` field **that does not carry the `exp_` prefix**.
A resolver that keys on `referent_pointer.metrics_path` alone (1182 rows) recovers roughly the 500s.
**Any count near 506 is a floor, not the number.** 128 rows resolve to no cell at all.

---

## 2. SUPERSEDES GRAPH — traversed

Fields carrying supersession semantics (there are 15, not 1):
`supersedes` (67 non-null), `amends_atom_id` (29), `amends_seq` (14), `amends` (12), `amends_atom` (5),
`superseded_by` (5), `retier_to` (5), `caveat_cleared_by` (4), `supersedes_atom_id` (3),
`parent_META_amended` (3), `retier_from` (3), `supersedes_commit` (3), `amends_commit` (3),
`amends_parent` (2), `corrects_seq` (2). **164 raw edges total.**

**The graph is mostly broken.**
- **32 edges point at 16-hex content hashes** (`5fa36804d7ff5ab6`, `2695ee34540fb626`, …). Each such hash
  occurs **exactly once in the entire 4.5 MB file** — there is no row it resolves to, and `atoms.jsonl`
  carries no matching id field (its only 16-hex fields are `metrics_sha256_16` (4 rows) and
  `cell_content_sha256_16` (3 rows)). These reference an external/earlier store. **Unresolvable.**
- **61 more are self-edges or unparseable** (a `cert_relabel` row whose `supersedes` points at its own
  earlier ruling for the same `atom_id`).
- That leaves ~71 real cross-cell edges, of which only **2 land on a currently-chain-graded cell**.

**Result: supersession removes almost nothing.** The live-claim set is determined by the
*latest ruling per cell*, not by the citation graph.

**Chain-graded then DEMOTED by a later in-place ruling (13) — these are NOT live claims:**
`exp_c3_compressed_sequence_replay_v1`, `exp_g1b_capacity_sweep_v1`, `exp_fresh_w_bpc_per_encoder_v2`,
`exp_substrate_basis_layer_label_contamination_proof_v4_prospective_bands`,
`exp_substrate_multihop_compose_fly_lsh_multibank_partition_v2_meta_m7_rail`,
`exp_parietal_cortex_spatial_reasoning_v1`, `exp_engram_dropout_inhibitory_plasticity_v2_density_matched`,
`exp_substrate_multihop_brain_pushback_v3_redispatch`,
`exp_substrate_semantic_parser_intent_slot_extraction_v1`, `exp_cls_ca3complete_consolidation_v1`,
`exp_read_grow_adaptor_pyp_kn_breadth_v1` (+2 more).

**Superseded by a cross-cell edge (2):** `exp_n8_conceptnet_ingest_eval_v1`,
`exp_fhrr_bundle_capacity_exact_margin_v1`.

**TERMINAL CHAIN-GRADED = 574.**

---

## 3. DISK JOIN (directories enumerated, not name-searched)

`os.walk('data/')` → **8502 directories**, **7885 top-level**, **7653 with a `metrics.json`**.
Join was done against that enumeration with a 4-stage matcher: exact → suffix-strip
(`_fulldev`/`_smoke`/`_selftest`/`_full`/`_dev`/`_rerun`) → longest-prefix → token-Jaccard fuzzy (≥0.55).

| resolution | terminal cells |
|---|---|
| exact dir | 537 |
| longest-prefix | 12 |
| fuzzy | 4 |
| **MISSING** | **21** |

**552 have a readable `metrics.json`; 1 has a dir but no `metrics.json`.**

**The 21 MISSING are a systematic class, not rot.** Nearly all are *cross-seed aggregate* atoms whose
`atom_id` is a 200-char prose slug and whose artifact lives in the **per-seed directories**
(`..._seed_7`, `..._seed_13`, `..._seed_19`). Examples with their nearest real dir:

| terminal cell (truncated) | artifact actually at |
|---|---|
| `..._sequence_binding_k_cliff_phase_diagram_full_v2_cross_seed_...` | `exp_substrate_sequence_binding_k_cliff_phase_diagram_full_v2_seed_13` |
| `..._refuse_gate_v8_conformal_v1_3seed_full_chain_grade_m1p4...` | `exp_substrate_refuse_gate_v8_conformal_v1_seed_13` |
| `..._cross_modal_binding_3rd_modality_v1_seeds_13_19_full...` | `exp_substrate_cross_modal_binding_3rd_modality_v1_seed_13` |
| `..._task_vector_hrr_icl_k_500_extended_v1_3seed_chain_grade...` | `exp_substrate_task_vector_hrr_icl_k_500_extended_v1_seed_13` |
| `..._cortex_hippo_dense_commercial_m_100k_1m_gpu_v5_...` | `..._kernel_active_fraction_seed_13` |
| `..._cross_axis_m_n_k_discriminating_arm_v2_3seed_full...` | `exp_cross_axis_m_n_k_discriminating_arm_v2_seed_13` |
| `..._schema_family_phase_diagram_v1_full_3seed_...` | `exp_substrate_schema_family_phase_diagram_v1_seed_13` |
| `..._cross_modal_binding_visual_auditory_v1_cross_seed_agg_3_of_3...` | `..._visual_auditory_v1_seed_13` |
| `..._metric_dependence_top_k_semantic_v3_3seed_full...` | `exp_metric_dependence_top_k_semantic_v1_seed_7_smoke` (v3 dir absent) |
| 4 × `meta_*` rules (`meta_rule_floor_thresh_must_be_stat_valid...`) | no artifact by design — they are rules, not cells |
| `exp_beaten_agg_neg0p055_but_only_4of5_neg_seed23...` | unresolved; slug is a *result sentence*, not a name |

**Practical rule for a cold session: 3 of these MISSING cells are genuinely un-actionable
(`meta_*` rules + the `exp_beaten_agg_...` result-sentence atom). The other 18 are fine — go to the
`_seed_13` directory.**

---

## 4. FLOOR DETECTION — by SHAPE, not by key name

**How I detected floors (this is the part that must be reused, not the numbers).**
I read each cell's `metrics.json` as **raw text** (not parsed-and-walked — nesting depth and bespoke
key names defeat a structured walk) and scanned for 18 *shape* regexes, then bucketed:

- **Class A — explicit control/comparison arm**: any of `scrambl`, `shuffl`, `permut`, `random*`,
  `chance`, `naive`, `baselin|base_|ARM_STANDARD`, `control`, `null`, `ablat|_off|flag_off|OFF=`,
  `lesion`, `floor`, `patholog`, `corrupt|distract|unrelated|mismatch|wrong_|nonsense|lowinfo|surrogate|placebo`.
- **Class B — contrast arm, no named control**: `"by_arm"`/`"arms"`/`"per_arm"`/`ARM_[A-Z]` container,
  or an `oracle`/`upper_bound`/`ceiling` reference arm.
- **Class C — pre-registered band only**: `HP>=` / `HF<` / `hard_pass_*_min` thresholds, i.e. an absolute
  bar with nothing to compare against.
- **Class D — no floor shape at all.**

| class | terminal cells |
|---|---|
| A — control/comparison arm | **132** |
| B — contrast/oracle arm only | 17 |
| C — pre-reg band only | 81 |
| D — none detected | **322** |
| (no metrics.json readable) | 22 |

**Individual shape frequencies (terminal set):** `random*` 41, `baseline` 37, `floor` 27,
`control` 23, `null` 18, `shuffle` 17, `naive` 9, `chance` 8, **`scramble` 8**, `corrupt-family` 7,
`permutation` 4, `pathology` 4, `ablation` 2.

### The June convention warning — CONFIRMED, and stronger than the brief said

| month | terminal cells | contain `scramble` | have a Class-A control arm |
|---|---|---|---|
| **June 2026** | 60 | **0** | **33 (55%)** |
| July 2026 | 87 | 12 | 71 (82%) |

**A scramble-keyed floor test returns FALSE on 60/60 June cells while 33 of them have a real control.**
June floors are named `random_*`, `*_NULL`, `ARM_STANDARD`, `FREQ_NULL`, `SHUFFLE`, `chance=`,
`positive_control_result`, `random_arm_pathology`, or stated only in `verdict_msg` prose. Any sweep that
keyed on `scramble` and concluded "June has no floors" was measuring the *word*, not the *design*.

### Honest limits of this detector (read before trusting Class D)
1. It reads **only `metrics.json`**. A floor declared in the pre-registration, in a `notes/` writeup, or
   in a `_start_marker.json` is invisible to it. **Class D means "no floor visible in metrics.json",
   NOT "no floor".** Spot-checking Class D found the dominant population is
   `exp_q_a3_l{N}_cross_layer_composition_*` / `exp_pp48_nkt_depth_*` — saturation grids reporting
   "all 97 levels EXACT-1.0", which genuinely have no comparison arm because the result is
   construction-determined. Those are correctly Class D.
2. It is **lexical**, so it over-fires: a `metrics.json` that merely mentions "baseline" in prose scores
   Class A. **For the ranked candidates in §5 I hand-read the `verdict_msg` and report the actual arm.**
   Do not propagate the aggregate Class-A count as "132 verified floors".

---

## 5. RANKED CANDIDATES — **NOT DONE** (in progress)

## 6. SPECIFIC FLAGGED CELLS — **NOT DONE** (in progress)
