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
| distinct atoms | 1925 | **1925** (from 1978 non-null `atom_id`) | **agrees exactly** — `atom_id` is not unique per row (53 repeats = re-rulings) |
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

## 5. RANKED CANDIDATES

### 5.0 The single most important structural fact in this ledger

**The chain-grade tier and the C3-relevant work barely overlap.**
Of the 574 terminal chain-graded cells, only **35 are dated 2026-07-15 or later**. The entire
late-July reading / grounding / comprehension arc — the work that actually bears on the read-out gate —
is banked as **`proven-bound`**, not chain-grade: **127 terminal non-CG (`proven-bound`/`measured_mechanism`)
cells in the reading/grounding families dated ≥ 07-15, of which 120 carry a Class-A control arm.**

Sample from the 07-22 → 07-24 window (all `proven-bound`, all live, none superseded):
`exp_read_xsent_coref_*` (5 cells), `exp_read_events_supply_*` (4), `exp_multipred_argstruct_*` (8),
`exp_pivot_selectional_*` (2), `exp_reader_perception_meaning_grounding_*` (3),
`exp_agreement_*` (9), `exp_compgen_native_bind_*` (4), `exp_hd_fact_store_*` (3),
`exp_arc_retrieval_*` (2), `exp_learner_*` (5).
**Exactly ONE cell in that entire three-day window is chain-grade**
(`exp_consolidated_reader_passive_mechanism_heldout_v1`).

**Consequence for a cold session: "terminal chain-graded" is the wrong filter for finding C3 leads.**
It selects June/early-July substrate physics. The C3-relevant seam is the *proven-bound* tier. The
ranking below therefore covers the chain-graded set as assigned, but §5.3 flags the proven-bound cells
that outrank most of it.

### 5.1 TOP 10 — ranked by whether they could move C3 (read-out quality 4.80% vs 0.80% floor, 5.2pp short)

The C3 defect as diagnosed: read-out scores are weak — **median target rank 84 of 647 anchors, 60%
outside the top-50**, every correct hit a *paradigmatic neighbour* (right neighbourhood, wrong member).
Cleanup-rule fixes are closed as a class (SNR wall). So the question for every candidate is: **does it
raise the anchor score, or separate within-neighbourhood?** Ranked on that, not on how impressive it reads.

---

**#1 — `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1`**
`chain_grade` · date **~2026-06-16 (git-date only, no `ts_iso` in metrics)** · artifact **EXISTS**
(`data/exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1/metrics.json`) · superseded-by: **none**
**Floor: Class A** — near-dup floor 0.1333 stated; de-dup arm vs full arm; 3 seeds (bit-identical, cv=0).
**Numbers:** 241 atoms at dim 1024. **49 near-duplicate pairs at cos>0.9; 54/241 (22%) of atoms have a
nearest neighbour above threshold. Top colliding pair cos = 1.0000 —
`math::T1/probability_space` ↔ `math::T1/measure_space`, two DISTINCT concepts with an IDENTICAL vector.**
De-dup at 0.95 (K 241→209) takes F1 to 1.0000 and lifts F=3 cleanup by **+0.1704**.
**Why #1:** this is the only cell in the entire ledger that *measures* the exact failure C3 exhibits —
right neighbourhood, wrong member — and it names the residual in the same words the C3 write-up uses:
*"the residual is genuine distinct-but-close atoms needing finer encoding."*
**Moves: C3 directly.** Run the same near-dup diagnostic over the **5491 live anchors** (not 241 math
atoms). If the rank-84 median is partly a collision artifact, the fix is upstream of any cleanup rule —
which is consistent with cleanup-rule fixes being closed as a class.
**Deflation:** 241 atoms, one domain (math T1), CPU, deterministic. This is a *diagnostic*, not a
demonstrated lift on the read-out corpus. Treat as a measurement to re-run, not a result to cite.

**#2 — `exp_encoder_retained_trace_requery_coarse_to_fine_v1`**
`chain_grade_retained_trace_req…` · **2026-07-08** · artifact **EXISTS** · superseded-by: **none**
**Floor: Class A** — sparse control (`sparse_fullV=0.541`, reproduces the v1 wall 0.5383), Gate-D
dense-reproduce check (0.9933).
**Numbers:** cheap COARSE shortlist by condensing the retained dense code (random projection D=128),
then FINE read *within the shortlist*: `final_recall=0.992` against a full-fine **ceiling of 0.992**
(i.e. it loses nothing), vs sparse max 0.561. **Gap +0.432. `shortlist_hit@k=0.1 = 1.000`.**
**Why #2:** C3's problem statement is literally a ranking problem — the target sits at median rank 84
of 647 and the read-out has to pick 1. A two-stage coarse→fine read-out is the standard structural
answer, and this cell shows it costs **zero** recall against the full-fine ceiling.
**Moves: C3.** Concretely: shortlist to k≈0.1·647 ≈ 65 candidates, then score finely inside it. The 60%
of targets outside the top-50 is the population this addresses.
**Deflation:** measured on encoder traces, not on the live grounding anchors; "ceiling 0.992" means the
fine reader was already near-perfect in that regime, which the live read-out is not (4.80%). It shows the
*architecture* is lossless, not that it lifts a weak scorer.

**#3 — `exp_substrate_last_token_vs_whitening_mean_pool_v1`**
`chain_grade` · **~2026-06-17 (git-date only)** · artifact **EXISTS** · superseded-by: **none**
**Floor: Class D by the detector — this is a DETECTOR FALSE NEGATIVE.** The arms are
`last_token_raw` / `mean_pool_whiten` / `last_token_whiten`; none of those strings match a
control-word regex, but the *design* is a clean 3-arm contrast with a raw arm. **Real floor: Class A.**
(Flagged here as the clearest instance of the §4 lexical limitation.)
**Numbers:** capacity `last_token_raw = 0`, `mean_pool_whiten = 40`, `last_token_whiten = 122`.
Combined / best-single = **3.05×**. 3 seeds, bit-identical.
**Why #3:** a pure representation-side lever on the *same* real sentence encoder the read-out uses.
If the live read-out mean-pools and does not whiten, it is operating at 40 where 122 is available —
a 3× separation headroom with no new mechanism.
**Moves: C3 (and C1 near-neighbour 2AFC 0.698, which is the same separation quantity).**
**Action for a cold session:** first check what the live read-out actually pools/whitens. `hdlab/whitening.py`
exists; nothing else in `hdlab/` imports it (it is imported from `substrate/kv_memory.py` and ~28
`experiments/` scripts). **The whitening lever may be islanded from the read-out path — verify before
building anything.**
**Deflation:** "capacity" here is items-recoverable, not read-out accuracy; the mapping to hit@1 is
unproven.

**#4 — `exp_kv_learned_projection_v1`**
`chain_grade` · **2026-06-20** · artifact **EXISTS** · superseded-by: **none**
**Floor: Class A** — analytic ceiling 0.080, **shuffled control 0.015**, held-out split.
**Numbers:** LEARNED contrastive projection generalises the value-cue→key alignment to **held-out** facts:
worst-seed held-out recall **0.827** (std 0.019), key-separation 0.878, vs analytic ceiling 0.080
(margin +0.747) and shuffled control 0.015.
**Why #4:** this is the **missing-LEARNING** flavour of the error routing rule, not a missing primitive —
a *learned* projection that improves key separation and is shown to transfer off-training. C3's defect is
a scoring/separation defect; a learned metric is the brain-compatible answer (and reuses the existing
`hdlab/learner` rather than a parallel build).
**Moves: C3, C1.** **Deflation:** `n_enc=2`; the recall scale (0.83) is on a synthetic KV task, not on
open-vocabulary anchors.

**#5 — the whitening / expansion / pseudoinverse recipe stack (4 cells, one seam)**
All `chain_grade`, all **~2026-06-16/17 (git-date only)**, all artifacts **EXIST**, none superseded.
- `exp_pseudoinverse_real_encoder_keys_v1` — pinv vs Hebb on **real whitened MiniLM keys**;
  `hebb_alpha_c=0.000` → `pinv_alpha_c=0.400`. Floor: Class D by detector; real design is a 2-arm
  contrast (Hebb arm is the floor). **The headline "400000000×" is a divide-by-zero artifact — the true
  statement is "Hebb reaches 0 where pinv reaches 0.400". Do not propagate the ratio.**
- `exp_substrate_pca_prewhitening_codebook_v1` — cap 3 → 7 at N=384, ratio 2.33×, 3 seeds bit-identical.
  **Deflate hard: the absolute capacities are 3 and 7 items.** "One-line universal real-encoder rescue"
  is the cell's own framing and is not supported by n=7.
- `exp_substrate_etf_minilm_dim_expansion_v1` — whitened cap D384 = 844 → D4096 = 9011 (10.68× scale);
  within-D whitening gain 3.06× at D384, 1.29× at D1024/D4096.
- `exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` — **expand + whiten STACK; no
  subsumption.** Production rule stated. **The "7000000000×" figure is again a divide-by-zero
  (`expand_only = 0.0`). Do not propagate.**
**Moves: C3, C1** — same argument as #3, this is the recipe that #3 sits inside.
**Why below #3:** the numbers are at toy scale and two of the four headline ratios are arithmetic
artifacts. The *recipe* (last-token pool → expand → whiten → pinv readout) is the asset, not the ratios.

**#6 — `exp_situation_model_assembly_encoder_retrain_scale_v1`**
`chain-grade` · **2026-07-31** · artifact **EXISTS** · superseded-by: **none**
**Floor: Class A** — degenerate `d6` arm FAILS the guard (an explicit can-fail control); frozen-vs-loop
comparison; collapse guard (loop≥frozen, wc_drift≤0.15, entcons≥0.85, q_agree≥0.60).
**Numbers:** encoder retrain **BREAKS the wall on held-out entities** in configs `d1_div40`/`d1_div80`:
all 3 query types ≥0.60 loop accuracy across seeds, memorisation gap closed, `best_loop=0.830`.
`name↔name frozen=0.057`. Verdict text ends **"ESCALATE TO SCALE"** — an explicit un-taken next step.
**Why #6:** this is the landed-encoder seam that MEMORY records as *opt-in by design*. It is the one
recent chain-graded result whose own conclusion is "scale me up", and it operates on entity identity,
which is upstream of anchor scores.
**Moves: C3 (via better anchors), C4 (coref 0.7193).**
**Deflation:** 2 configs out of a grid; `name↔name` frozen is 0.057, i.e. the *starting* point is near-zero.

**#7 — `exp_encoder_alltype_transfer_stress_v1`**
`chain-grade` · **2026-08-01** — **the most recent terminal chain-graded cell in the ledger** ·
artifact **EXISTS** · superseded-by: **none**
**Floor: Class A** — frozen (`fz`) vs tuned (`tn`) arms, held-out eval-draw, independent
entity-file harness (3 stress conditions).
**Numbers:** all 3 stress conditions clear lift ≥0.05 on ≥2 types **including non-coref**.
c1_harder: name_maintenance +0.108, competitive_coref +0.142, overwrite +0.231.
c2_heldout: +0.200 / +0.150 / (overwrite fz 0.360).
Conclusion: *"the certified encoder break is a REAL representation improvement, not a
base_loop-harness-specific artifact."*
**Why #7:** independent confirmation that the #6 encoder gain survives a harness swap — the exact
control class MEMORY says apparent comprehension wins keep failing. It is a *validation* of #6, not a
new lever, hence below it.
**Moves: C4 directly; C3 indirectly** (better entity representations → better anchors).

**#8 — `exp_metacog_abstain_readout_signal_thresholding_v1`**
`chain_grade` · **2026-07-20** · artifact **EXISTS** · superseded-by: **none**
**Floor: Class A** — `beats_rand=True, p=0.0, rand_p50=0.732`; baseline out-of-band gate declared.
**Numbers:** `S1_reader_best_score` **HARD_PASS** (rel_red 0.327 at coverage 0.5, wrong-rate
0.493 vs base 0.732); `S2_reader_margin` MIDDLE_BAND; `S3_coherence_score` **HARD_FAIL**;
**`S4_cleanup_margin` HARD_FAIL**.
**Why #8 and why it matters more than its rank suggests:** it is **independent, pre-C3 corroboration of
the "cleanup-rule fixes are closed as a class" conclusion** — the cleanup margin carried no usable
signal a month before the SNR-wall diagnosis. Meanwhile the raw **reader best score DOES** carry usable
confidence. That says: *stop rescoring the cleanup, start using the reader score.*
**Moves: C3** — as an abstention/selection layer on the existing read-out score, not as a quality lift.
**Deflation:** it improves *precision at 50% coverage*; the C3 gate is hit@1 at full coverage. This
raises reliability, not the 4.80%.

**#9 — `exp_consolidated_reader_passive_mechanism_heldout_v1`** *(the flagged "strongest unpromoted result")*
`chain-grade` (note the **hyphen** — this is one of the 10 rows a `chain_grade` exact grep misses) ·
**2026-07-24** (`ts_iso` 2026-07-24T00:29:16, ledger `ts` 2026-07-23) · artifact **EXISTS** ·
superseded-by: **none** · **1 ledger row only, op `landed_vet_atomize`**
**Floor: Class A** — `naive_acc = 0.0` (n=24), P2 flag-OFF ablation reproducing the banked
parse-luck baseline (2 passages), McGuffey composed-F1 non-regression check.
**Numbers:** held-out passive-voice who-did-what **23/24 = 0.9583 vs naive 0.0** (margin +23);
flag ON/OFF **12/13 fired vs 2** (Δ+10) across 13 independent held-out passages, 11 novels;
McGuffey composed F1 0.5868 → 0.5868 (no regression); parser UAS 0.7882.
The metrics file's own verdict says *"CHAIN-GRADE CANDIDATE — HYPOTHESIS pending skunkworks
landed-VET; NOT banked"* — **but the ledger row that cites it is `landed_vet_atomize` with
`cert_status: "chain-grade"`. The VET happened; the metrics prose was never updated.** The
"unpromoted" framing is wrong: it IS promoted, it is just invisible to a `chain_grade` grep.
**Moves: C4/C3 (reading).** It is a *construction competency* win (passive voice), which is the
declared shape of comprehension progress. It does **not** bear on read-out separation.
**Why only #9 on a C3 ranking:** it is the strongest *reading* result here and the honest
answer is that it moves the reading arc, not the 4.80%.

**#10 — `exp_anchor_compose_identity_shuffle_cskg_v2` (+ `_scaling_ladder_cskg_v3`)**
`chain_grade` / `chain_grade_anchor_compose_ind…` · **2026-07-13** · artifacts **EXIST** ·
superseded-by: **none**
**Floor: Class A and unusually complete** — held-out MRR with **RANDOM 0.0005, SCRAMBLE 0.0087,
IDSHUF 0.0025, POPULARITY 0.0001, ORACLE 0.1374**, n_q=3000, 2 seeds.
**Numbers:** `ANCHOR = 0.1275` vs `ORACLE = 0.1374` — **the anchor route reaches 93% of its own
oracle.** `ADDITIVE = 0.0000`, `ONESHOT = 0.0001`. v3 shows it holds under half-support and
sparse-core-big-N (retention 0.94–1.01, N up to 38772).
**Why #10 — and read this one as a WARNING, not a lead:** it is the same shape as the flagged
`exp_resonator_verifier_readout_v1` finding (harvest equals its own oracle). **When the mechanism is
already at 93% of its oracle, the ceiling is the ORACLE (0.1374), not the mechanism.** Two independent
cells now say the read-out route is oracle-bound. That is a strong argument that C3's 5.2pp gap
will not be closed by a better read-out rule — it must be closed upstream, at the anchors
(→ #1, #3, #5, #6).
**Moves: nothing directly. It BOUNDS C3** and is the reason #1–#5 are ranked where they are.

---

### 5.2 Ranks 11–20 (shorter)

| # | cell | date | status | floor | what it could move |
|---|---|---|---|---|---|
| 11 | `exp_substrate_hallucination_detection_minilm_v1` | ~06-17 (git) | `chain_grade` | **D (detector FN — grounded vs hallucinated IS the 2-arm contrast)** | AUC **0.999** separating grounded from hallucinated; grounded_conf 0.204 vs hall 0.107. A verification gate on read-out output. **C3 precision, not recall.** |
| 12 | `exp_attention_salience_common_mode_detector_v1` | 07-20 | `chain-grade` | A (shuffle control quiet both modes, 0.0001/0.0003) | detector separates common-mode from genuine agreement, gap 0.0829, per-seed 5/5. **Explains why the rank-1 common-mode removal came back HARD_FAIL_NO_EFFECT** — it fires only in the correlated mode. Diagnostic for C3, not a lift. |
| 13 | `exp_learned_codebook_generalization_gate_v1` | 07-20 | `chain_grade` | A (`random` neg-control AUC 0.496) | ppmi_svd AUC 0.927±0.001 vs random 0.496; ws_sp 0.652. 8M-token corpus, V=10000, N=1024. Codebook-quality gate — a supply-side lever on anchor quality. **C3.** |
| 14 | `exp_scale_meaning_learn_arc_heldout_v2` | 07-27 | `chain-grade` | A (`RAW_TEXT-RANDOM=0.1034`, per-seed min stated) | from-scratch text-at-scale **beats grounding** on held-out-NEW semantic; zavg 0.6469 vs raw 0.5968. Bears on the supply route. **C3 (supply).** |
| 15 | `exp_leakproof_relational_inference_heldout_v1` + `_context_sweep_v1` + `_twonew_v1` | 07-26 | `chain-grade` | A, exemplary — LEARNED 0.6534 / RAW_GROUNDING 0.5459 / RANDOM_INIT 0.5246 / STRUCT_2HOP 0.5602 / POPULARITY 0.5055 / COLLAPSE 0.4978, **leak witness 0/22299** | learned relational inference +0.1076 over raw grounding, and the context sweep shows the margin **grows monotonically with context** (+0.0675 at 1 edge → +0.1116 at ALL). **C2 (context gap +0.1005) most directly.** |
| 16 | `exp_generation_decoder_rns_crt_highvocab_v1` | 07-05 | `chain_grade` | A (`scram` control collapses to 0.000; iid ceiling 1.000) | RNS/CRT pushes exact-ordered decode to 1.000 at V=65536 where correlated single-block falls to 0.160. A **high-vocabulary** decode mechanism — relevant if the 647→5491 anchor scale is the problem. **C3 (scale).** |
| 17 | `exp_generation_decoder_gsbc_native_blocklocal_v1` | 07-05 | `chain_grade` | A (dense_gsbc_fullreso **0.000** vs dense_synth_fullreso 1.000 — the encoding-mismatch control) | block-local sparse factorizer 1.000 where the dense bipolar resonator **collapses to 0.000 on the same fillers**. Named finding: *dense multiply-bind is the encoding mismatch.* **C3 (architecture).** |
| 18 | `exp_joint_operator_capstone_selective_readouts_v1` | 07-15 | `chain_grade` | A (`SHUF=0.4222`, chance 0.52 / freq 0.7778, 9 declared gates all True) | two operators solved jointly with no interference (rel_drop −0.0061/0.0000). Infrastructure for stacking read-outs. **C3 (composition).** |
| 19 | `exp_frame_order_recovery_hard_comprehension_v2` | 07-06 | `chain_grade_frame_order_recove…` | A (chance 0.167; occupancy control stuck at 0.195) | role→block ORDER recovered at 1.000 vs occupancy 0.195; parse survives superposition at 0.800. **C4/C3 (structure survives superposition).** |
| 20 | `exp_c1_entmax_envelope_sweep_v2` + `exp_substrate_c1_entmax_alpha_readout_v1` | 06-18 / undated | `chain_grade` | B (contrast arms; envelope grid 80/80 cells) | sparse read-out wins **80/80 discriminating cells on FLOPs at ISO-recall** (median 94% FLOP reduction), recall **1.000 vs 1.000 — Δ+0.000**. **Explicitly does NOT move C3 quality.** Listed so a cold session does not mistake "read-out WIN" in the title for a quality lift. `_alpha_readout_v1` has **no directory on disk** (ledger row resolves by `atom_id` slug only). |

### 5.3 Outranking non-chain-graded cells a C3 hunt must not skip

These are `proven-bound` / `measured_mechanism`, so out of scope for the assigned filter, but they
score higher on C3 relevance than most of §5.2:

- **`exp_resonator_verifier_readout_v1`** — see §6. **NOT chain-graded**; it is `cert-neutral`. Its
  harvest = 0.806 = its own oracle. Together with #10 this is the second independent oracle-bound result.
- **`exp_read_xsent_coref_scene_protagonist_v1`** — `proven-bound`, 07-24. See §6.
- The **127-cell** `proven-bound` reading/grounding block dated ≥07-15 (120 with Class-A floors),
  notably `exp_reader_component_oracle_ablation_audit_v1`,
  `exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1` (`measured_mechanism`),
  `exp_hd_fact_store_semantic_capacity_whitening_v1` (whitening applied to the *fact store* — the
  closest thing to #3 already being on the live path), and `exp_semantic_hd_encoder_meaning_match_v1`.
  **`exp_hd_fact_store_semantic_capacity_whitening_v1` should probably be read before acting on #3.**

---

## 6. THE SPECIFICALLY FLAGGED CELLS — verified, with corrections

**Three of the five flags need correcting. Two are not chain-graded and one is not in the ledger at all.**

| flagged | ledger status found | verdict |
|---|---|---|
| `exp_consolidated_reader_passive_mechanism_heldout_v1` | **`chain-grade`**, terminal, 1 row (`landed_vet_atomize`), 07-23/24 | **CONFIRMED** — see §5.1 #9 |
| `exp_resonator_verifier_readout_v1` | **`cert_neutral_…`** — NOT chain-graded | **CORRECTION** |
| `exp_read_xsent_coref_scene_protagonist_v1` | **`proven-bound`** — NOT chain-graded | **CORRECTION** |
| `exp_consol_conjunction_replay_v1` + 2 siblings | **ABSENT from the ledger entirely** | **CORRECTION** |
| the 07-23 CHAIN_GRADE reader triple | **does not exist as a triple** | **CORRECTION** |

### 6.1 `exp_resonator_verifier_readout_v1` — real, but CERT-NEUTRAL, not chain-grade
Two ledger rows, both dated **2026-07-07**, resolved via the `anchor` field (the cell name never appears
verbatim in the ledger — `grep exp_resonator_verifier_readout_v1` returns **0**; `grep
resonator_verifier_readout` returns 5). `cert_status` values:
`proven_fuller_contra_verifier_readout_harvests_oracle_ceiling_0p806_reachability_0p806_remains` and
`cert_neutral_residual_gap_decomposition_aggregation_vs_reachability`.
**Artifact EXISTS.** Floor: Class A (`baseline_K4=0.133`, plurality 0.453, oracle_any, 3 seeds, `by_arm`).
**Numbers confirmed:** K4 verifier harvest **0.806** at T0=0.50, **+0.353 over plurality 0.453**,
`oracle_any = 0.806` — i.e. **the verifier harvests exactly the oracle, no more**;
`verifier_le_oracle_violations = 0` at every arm.
**The C3 diagnosis is already banked here**, in the cell's own words: *"the residual gap WAS
aggregation-loss, confirming the VET diagnostic."*
**Correction to the brief: this is not an unpromoted chain-grade finding. It was deliberately tiered
CERT-NEUTRAL** as a residual-gap decomposition. Its value is as a **bound**, matching §5.1 #10:
two independent cells say the read-out is oracle-bound.

### 6.2 `exp_read_xsent_coref_scene_protagonist_v1` — `proven-bound`, terminal, artifact exists
**2026-07-24T05:45:55**, 1 row, `landed_vet_atomize`, verdict HARD_PASS, `cert_status: proven-bound`.
Floor: Class A and genuinely well-built — a **LOCALITY null** with two arms (`fixed5 = 0.4070`,
`Kmean-random = 0.3710`).
**Numbers:** same-gender subset `topical_perscene_charset = 0.4003` vs backbone 0.2462 (Δ +0.1541,
sign_stability 1.000); whole-doc topical lever **FAILED** on the subset (0.2412, Δ −0.0050).
**The conclusion is exactly as flagged**, and stated in the metrics verbatim:
*"scene_structure_supported=False: the lever is LOCAL-WINDOW subject-role-mass, NOT scene detection
(a dumb fixed-5-sentence window matches/beats detected scenes)."* `best_diag_arm = topical_local_fixed5`
at 0.4070 — **the dumb window BEATS the detected scenes (0.4070 > 0.4003).**
**This was re-derived from scratch three weeks later. The re-derivation was avoidable.**
It is `proven-bound` — a correctly-tiered negative-shaped bound, not a suppressed positive.
**Moves C4** (coref 0.7193): the standing instruction it implies is *use a fixed local window; do not
build scene detection.*

### 6.3 `exp_consol_conjunction_replay_v1` and siblings — **ZERO ledger rows**
`grep consol_conjunction_replay data/substrate_index/meta/cert_ledger.jsonl` → **0 matches.**
No `cert_status`, no atom, no ruling. Same for `exp_consol_interleaved_replay_v1` and
`exp_consol_inductive_entity_replay_cskg_v1` (the two siblings that exist on disk;
there is no `exp_consol_negation_replay_v1` or `_relative_clause_replay_v1`).
**All three artifacts EXIST on disk** (each with `_selftest`/`_smoke` variants and per-seed
`partial_metrics_*.json`).
`exp_consol_conjunction_replay_v1`: **2026-07-15T12:40:33**, 5 seeds (101/103/107/109/113), run_mode full.
Verdict `REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT`.
**Floor: Class A, textbook** — `chance = 0.5118`, `FREQ_NULL = 0.4768`, `SHUFFLE = 0.5192`,
`MEMO = 0.4768`, `ORACLE = 1.0000`, plus an under-trained probe null.
**Numbers:** INTERLEAVED 1.0000 = CONTINUAL 1.0000 → **primary schedule gap = 0.0000**, votes 0/3,
`compute_matched = True`. Read-out works (INTER−FREQ = 0.5232).
**These are three properly-floored, 5-seed July refutations of consolidation-schedule advantage that
never entered the certification system at all.** They are *negative* results, which is exactly the
class the ledger is worst at capturing — and the ledger's own `atomized_by` field shows no
skunkworks batch covering 07-15 replay cells.
**Moves: nothing on the scoreboard. It closes a route** — do not re-run consolidation-schedule
experiments expecting a schedule advantage; the effect is a read-out effect.

### 6.4 "The 07-23 CHAIN_GRADE reader triple" — does not exist as described
On 2026-07-23 the ledger has **~40 reader/parser/learner cells, and not one of them is chain-grade.**
The four `exp_consolidated_reader_*` cells resolve as:

| cell | 07-23 status | artifact |
|---|---|---|
| `exp_consolidated_reader_chaingrade_demo_v1` | **`proven-bound`** | exists |
| `exp_consolidated_reader_chaingrade_FULL_v1` | **`cert_status` field ABSENT on its only row** | exists |
| `exp_consolidated_reader_hardsyntax_heldout_v1` | **`proven-bound`** | exists |
| `exp_consolidated_reader_passive_mechanism_heldout_v1` | **`chain-grade`** (dated 07-23 in ledger `ts`, 07-24 in `ts_iso`) | exists |

**The name `chaingrade` in `exp_consolidated_reader_chaingrade_FULL_v1` is an ANCHOR NAME, not a
cert tier.** Two of the three cells with "chaingrade" in the filename are `proven-bound`; the third
has no `cert_status` at all. **A grep for `chaingrade` over cell names will report a chain-grade triple
that the ledger does not contain.** This is the same failure class as the `scramble` floor trap: reading
the *word* instead of the *field*.

---

## 7. WHAT I COULD NOT FINISH — explicit gaps

1. **NOT DONE — per-cell floor verification beyond the ~30 hand-read cells.** The §4 table (132 Class A /
   322 Class D) is a **lexical** classification of `metrics.json` only. I hand-verified ~30 cells and found
   **at least 4 Class-D false negatives** (`last_token_vs_whitening`, `pseudoinverse_real_encoder_keys`,
   `pca_prewhitening_codebook`, `hallucination_detection_minilm` — all have real contrast arms whose arm
   names simply don't contain a control word). **The true Class-A count is higher than 132 and I did not
   measure how much higher.** Do not cite 132/574 as a verified floor rate.
2. **NOT DONE — dates for the June substrate batch.** ~505 terminal cells have no `ts_iso` in
   `metrics.json` and no `ts` in the ledger. For the §5.1 #1/#3/#5 cells I fell back to **git dates**,
   which the project's own convention says lie. They are internally consistent (the whole
   whitening/pseudoinverse/codebook family shows 2026-06-16/17), so I report them as a **batch estimate**,
   not a run date. A proper fix needs the dispatch logs, which I did not open.
3. **NOT DONE — the ~1350 non-chain-graded atoms** (1925 distinct atoms − 574 terminal chain-graded).
   I traversed and classified the chain-graded tier as
   assigned. §5.0 shows that decision is itself questionable: **127 proven-bound reading cells ≥07-15 with
   Class-A floors were not individually triaged.** That block is probably richer for C3 than the
   chain-graded tier and is the obvious next pass.
4. **NOT DONE — did not verify what the live read-out actually does.** The §5.1 #3 recommendation
   ("check whether the read-out mean-pools without whitening") is a *hypothesis*. I confirmed
   `hdlab/whitening.py` exists and that no other `hdlab/` module imports it, and that
   `experiments/exp_grounding_readout_known_answer_v1.py` **does not exist on disk** (only its
   `data/` outputs do, plus two SMOKE variants) — so I could not read the read-out's own code path.
   **Verify before building.**
5. **NOT DONE — the 32 dangling 16-hex `supersedes` hashes.** Each appears exactly once in the ledger
   and matches nothing in `atoms.jsonl`. I did not search the four `cert_ledger.jsonl.bak_*` backups
   (1.2 MB each, dated 07-01/02) which may contain the superseded rows. If provenance matters, start there.
6. **NOT DONE — untracked result JSONs.** The brief notes ~28–35 result JSONs are untracked. I enumerated
   directories and read `metrics.json` by path, so tracked-ness never gated my reads — but I also never
   **measured** how many of the 552 terminal artifacts are untracked. Unknown.

---

## 8. ONE-SCREEN ACTION SUMMARY FOR A COLD SESSION

1. **Do not use "chain-graded" as your filter for C3 work.** Only 35 of 574 are dated ≥07-15; the reading
   arc is `proven-bound` (§5.0).
2. **Two independent chain-graded cells say the read-out is ORACLE-BOUND** (`anchor_compose` at 93% of
   oracle 0.1374; `resonator_verifier` harvest = oracle exactly at 0.806). Combined with the
   `S4_cleanup_margin` HARD_FAIL from 07-20, **the evidence that C3's 5.2pp gap cannot be closed by a
   better read-out rule is now three-fold and predates the SNR-wall diagnosis.** Work upstream.
3. **The highest-value un-run measurement is #1**: run the near-duplicate diagnostic over the 5491 live
   anchors. It found 22% of a 241-atom codebook had a near-identical neighbour and one pair at cos=1.0000
   between two genuinely distinct concepts. If that reproduces at 5491, median rank 84 has a mechanical
   explanation that no cleanup rule can fix.
4. **Then check the pooling/whitening of the live read-out** (§7 gap 4) against the 0 / 40 / 122 capacity
   ladder in #3.
5. **Do not re-derive** the local-window coref result (§6.2) or the consolidation-schedule refutation
   (§6.3). Both are on disk with clean floors; neither is in a planning doc.

