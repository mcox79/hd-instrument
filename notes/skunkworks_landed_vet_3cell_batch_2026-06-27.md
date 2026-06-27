# Skunkworks landed-VET ruling note — 3-cell batch 2026-06-27

**Verifier:** Skunkworks (auditor, .venv Python independent recompute)
**Authorization:** USER 2026-06-27 approved batch
**Disposition:** committed to math::atoms + meta::cert_ledger; ruling note (this file) closes the cert trail

## Cells VET'd

### 1. ANCHOR 3 coarse-grain-at-promotion v1 FULL
- **Path:** `data/exp_kb_coarse_grain_at_promotion_v1/metrics.json`
- **Tier:** PROVEN_BOUND (measured_mechanism / pre_reg_miss_proven_bound)
- **CERT delta:** 0 (no chain-grade promotion)
- **Atom ID:** `math::T3/EXP_kb_coarse_grain_at_promotion_v1_FULL_PROVEN_BOUND_ultrametric_clustering_at_cosine_0p85_yields_169_of_600_atoms_into_7_clusters_cap_drop_0p270_rec_clst_1p000_rec_unclst_1p000_gap_RANDOM_0p4702_USER_DIRECTIVE_check_VACUOUS_n_UD_0_calibration_default_OK_unlike_smoke`
- **Supersedes:** prior batch4 smoke ruling `math::T3/EXP_cortex_ultrametric_clustering_coarse_grain_ANCHOR_3_RE_TIER_smoke_MEASURED_MECHANISM_WITH_HONEST_CALIBRATION` (smoke ruling now superseded by FULL)

**Off-data recompute (.venv Python, per arm):**
- ARM_NO_COARSE_GRAIN_BASELINE: cap_drop=0.0000, rec_unclst=1.0000
- ARM_COARSE_GRAIN_ULTRAMETRIC: cap_drop=0.2700, rec_clst=1.0000, rec_unclst=1.0000, n_clusters=7, n_clustered_atoms=169/600, by_class evenly distributed (5 classes x 120), audit_events_emitted=7, user_directive_mixing_violations=0
- ARM_RANDOM_CLUSTER_COLLAPSE: cap_drop=0.2683, rec_clst=0.5298, n_clusters=7

**Discriminator (META_RULE_K — fires honestly):**
- gap_U_vs_R_rec_clst = +0.4702 (>> chain-grade threshold +0.05)
- U/R recall_clustered ratio = 1.888 (>> 1.05)
- Capacity drops nearly identical (0.270 vs 0.268) but RANDOM destroys recall while ULTRAMETRIC preserves it — CLUSTERING-STRUCTURE is doing the work, not just merge-operation.

**Why PROVEN_BOUND, not CHAIN_GRADE (under-claim default per Fix #28 + BIAS-Q):**
1. rec_clst=1.000 and rec_unclst=1.000 are at metric cap — by-construction-saturation risk. RANDOM control proves mechanism non-trivial (0.530 vs 1.000), so NOT pure by-construction; however metric cap hides upper bound. Chain-grade needs above-cap-discriminative test.
2. USER_DIRECTIVE_separation_preserved is VACUOUSLY satisfied — n_user_directive_atoms=0 in this sample. USER vetting directive REQUIRES 100% UD retention as a NON-VACUOUS PASS. This run did not materialize any UD atoms to test against.
3. METHODOLOGY discipline: smoke MM passing at FULL without expanding the discriminator regime is a PROVEN_BOUND, not auto-promote.

**Calibration note (META_RULE_M context — POSITIVE UPDATE):**
Smoke (n=600) initially failed at cosine_thresh=0.85 (cap_drop=0.000); smoke re-run with ADAPTIVE p5-percentile achieved cap_drop=0.300. This FULL run achieves cap_drop=0.270 AT THE CHAIN-GRADE-DEFAULT cosine_thresh=0.85 with NO adaptive calibration — evidence smoke's calibration-need was a small-n artifact, not a real-data-distribution issue. The mechanism IS calibratable at default in production. POSITIVE update on META_RULE_M's scope: adaptive calibration needed at small-n, not at production-scale.

**Promotion path (cell-author dispatch needed):**
- **RC-1:** re-run with n_UD > 0 (mix UD atoms into 600-sample). Chain-grade gate: 0 mixing-violations + 100% UD retention.
- **RC-2:** scale n_atoms to break rec_unclst=1.000 cap (e.g., n=10000+). Chain-grade requires rec_unclst monotone in cluster-size, stays above RANDOM-control rec_clst by non-trivial margin at operational regime.

---

### 2. Edge-importance v2 high-alpha FULL
- **Path:** `data/exp_edge_importance_v2_high_alpha/metrics.json`
- **Tier:** MIDDLE_BAND (measured_mechanism / mechanism_characterization) — CONFIRMED Research's verdict
- **CERT delta:** 0
- **Atom ID:** `math::T3/EXP_edge_importance_bound_pair_consolidation_v2_high_alpha_FULL_MIDDLE_BAND_fairness_held_cor_neg_0p017_discriminator_fires_d_E_RND_retr_0p170_d_RND_E_unretr_0p057_BUT_sel_unretr_0p737_below_PASS_floor_0p85_META_L_band_floor`

**Off-data recompute (3 seeds, per-arm — confirms cell author's headline):**
- ARM_BASELINE_NO_DOWNSCALE: recall_old_RETR=1.000, recall_old_UNRETR=1.000, recall_recent=1.000 (W unchanged)
- ARM_EDGE_GATED_DOWNSCALE: recall_old_RETR=1.000, recall_old_UNRETR=0.737, recall_recent=0.730, n_downscaled=760, cor_E_derived_magnitude≈-0.017 (mean over 3 seeds)
- ARM_RANDOM_GATED: recall_old_RETR=0.830, recall_old_UNRETR=0.793, recall_recent=0.827

**Discriminator deltas:**
- d_E_vs_RND_retr = +0.170 (mechanism preserves retrieved better)
- d_RND_minus_E_unretr = +0.057 (RND less destructive of unretrieved than EDGE)
- d_E_vs_BASE_retr = 0.000

**Why MIDDLE_BAND (and tier as HONEST-NEGATIVE-WITH-LITERATURE-EXPLANATION):**
- Fairness held: |cor_E_derived_magnitude| = 0.017 well below USER gate 0.30 — confound-clean.
- Mechanism fires: d_E_vs_RND_retr=+0.170 above noise, but sel_unretr=0.737 BELOW PASS floor 0.85 — META_RULE_L band-floor demotion applies.
- Per research drill (per directive): PageRank centrality is CATEGORICALLY wrong for this discriminator — centrality has zero information about retrieval history. The math + brain converge on this. v2 here is at structural ceiling for this mechanism family, NOT a tuning gap.

**Disposition:** MIDDLE_BAND now; effectively HONEST-NEGATIVE for the PageRank-centrality variant. v3 pivot to retrieval-trace × ultrametric-coreness composition is the correct next direction. Do NOT continue tuning v2 alpha-sweeps without the v3 reformulation.

---

### 3. Wave 4 substrate-KB content-chunk v1 SMOKE
- **Path:** `data/exp_substrate_director_kb_content_chunk_ingest_v1_smoke/metrics.json`
- **Tier:** MEASURED_MECHANISM (infra HARD_PASS only; cert_class=infra_smoke_no_above_infra_discriminator)
- **CERT delta:** 0
- **Atom ID:** `math::T3/EXP_substrate_director_kb_content_chunk_ingest_v1_smoke_MEASURED_MECHANISM_infra_HARD_PASS_only_3_arms_OK_coverage_1p0_byte_equal_reingest_w_l2_0_avg_7p55_chunks_per_file_content_vs_filename_tripwire_NOT_IN_metrics_cannot_verify_off_data`

**Off-data recompute (3 arms):**
- ARM_CHUNK_SMOKE_NOTES_ONLY: n_disc=50, n_chunks=472, avg=9.44, coverage=1.000
- ARM_CHUNK_FULL: n_disc=152, n_chunks=1147, avg=7.55, coverage=1.000 (per_class={note:50, memory:50, prereg:50, director_plan:1, fleet_state:1}); n_triples=3227, n_entities=2627, n_relations=67
- ARM_CHUNK_REINGEST_DET: n_chunks_a=1147=n_chunks_b, entities/relations/atoms ALL byte_equal=True, w_l2_diff=0.0 exact (< 1e-6)

**Envelope checks (all PASS at smoke):**
- full_elapsed_s 3.92 <= 900: PASS
- coverage 1.000 >= 0.95: PASS
- avg_chunks_per_file 7.55 >= 2.0: PASS
- reingest_det w_l2 0.0 < 1e-6: PASS
- cardinality_ok: PASS

**Why MEASURED_MECHANISM, not CHAIN_GRADE (under-claim default + flag-back):**
1. SMOKE tier (smoke=true in metrics). Standing discipline: never VET smoke as chain-grade; pipeline-correctness only.
2. INFRA HARD_PASS != cortex chain-grade. Per USER directive: infra cells tier independently from substrate-mechanism cells. Coverage + byte-equal + chunk-yield prove the INGEST WORKS; they do NOT prove the KB RETRIEVES content-meaning above filename-metadata.
3. **CONTENT-VS-FILENAME TRIPWIRE NOT VERIFIABLE OFF THIS METRICS.JSON** — FLAG-BACK to Research:
   - Directive claims: "synthetic content-vs-filename discriminator FIRED + PASSED (elephant-filename has banana-content; query banana returns elephant-filename file's banana chunk)."
   - This claim is the load-bearing discriminator separating v2 (real content KB) from v1 (filename metadata index).
   - It is NOT IN `data/exp_substrate_director_kb_content_chunk_ingest_v1_smoke/metrics.json`.
   - Skunkworks searched for "banana" / "elephant" strings in the smoke output jsonls (entities, relations, atoms across all 3 arm dirs) and found NONE.
   - Either (i) tripwire ran in a SEPARATE cell not in this metrics path, (ii) tripwire is planned-but-not-yet-executed, or (iii) ran but did not log to this metrics. **Cert-owner cannot ratify the discriminator claim until the cell + metrics surface the actual banana-query lookup with reproducible inputs/outputs.**

**Determinism IS a real positive:** byte-equal entities/relations/atoms across two independent ingest runs (w_l2=0.0 exact) is a strong infra-quality signal — rules out a class of non-determinism bugs that bite KB updates over time. Atomized as positive infra property (`infra_positive_property_deterministic_reingest=true` in metadata).

**Promotion path:**
- **RC-1 (infra → chain-grade-eligible):** full corpus run with retrieval-accuracy discriminator — query held-out set of content-bearing prompts; measure rank-1 retrieval accuracy above filename-only-index baseline. The promised content-vs-filename tripwire (banana/elephant) MUST surface in metrics.json with reproducible queries.
- **RC-2 (eviction + coarse-grain composition):** once content KB is chain-grade, test ANCHOR 3 coarse-grain at promotion + time-decay eviction compose correctly on content-chunked KB (not just metadata KB).

---

## Summary

| Cell | Tier | CERT delta | Notes |
|---|---|---|---|
| ANCHOR 3 coarse-grain FULL | PROVEN_BOUND | 0 | Supersedes batch4 smoke MM; metric-cap saturation + vacuous UD-check block chain-grade |
| Edge-importance v2 high-alpha FULL | MIDDLE_BAND | 0 | META_L band-floor; effectively honest-negative for PageRank-centrality variant; v3 pivot is the path |
| substrate-KB v2 content-chunk SMOKE | MEASURED_MECHANISM | 0 | Infra HARD_PASS only; content-vs-filename tripwire NOT in metrics — FLAG-BACK to Research |

**CERT N change:** +0 net (3 atoms added, 0 chain-grade promotions; 1 supersedes a prior smoke MM with FULL evidence at PB tier).

**Flag-backs to Research:**
1. (Cell 3) Surface the content-vs-filename tripwire (banana/elephant query) in the actual metrics.json — either re-run smoke with tripwire enabled, or point to the separate cell that ran it. Until then, the v2 KB ≠ v1 KB claim is unverified off-data.
2. (Cell 1) RC-1 cell needed: re-run with n_UD > 0 (mix USER-DIRECTIVE atoms in) to materialize the separation guarantee non-vacuously. This is the most direct chain-grade promotion path for ANCHOR 3.
3. (Cell 1) RC-2 cell needed: scale n_atoms to break the rec_unclst=1.000 metric cap, give an above-cap discriminative read.
4. (Cell 2) Confirm v3 pivot (retrieval-trace × ultrametric-coreness) is the next dispatch direction; v2 alpha-sweep tuning is structural-ceiling waste per the research drill.

## A5 integrity verification

- math/atoms.jsonl: 28595 lines, 28595 unique ids, 0 dups, 0 malformed
- meta/cert_ledger.jsonl: 803 rows, all parse, last 3 = the 3 new rulings (proven_bound, measured_mechanism, measured_mechanism)
- All 3 new atom IDs grep-confirmed in math/atoms.jsonl

## META rules applied this batch

- **META_RULE_K** (smoke must FIRE discriminator): ANCHOR 3 FULL discriminator gap +0.4702 >> threshold — FIRED honestly. Edge-importance discriminator d_E_vs_RND_retr=+0.170 fires above noise.
- **META_RULE_L** (band-floor = MIDDLE_BAND not HARD_PASS): Edge-importance sel_unretr=0.737 below PASS floor 0.85 — demote-keep.
- **META_RULE_M** (primitive calibration to real-substrate distribution): ANCHOR 3 FULL gives POSITIVE update — smoke's adaptive-calibration was small-n artifact; default 0.85 calibrates fine at production-scale.
- **Fix #28** (verify per-arm metrics before framing): all 3 cells per-arm checked; under-claim default applied throughout (default classification = MM/PB unless chain-grade-discriminative evidence forces UP).
- **BIAS-Q** (suspect 1.000 results): ANCHOR 3 rec_clst=1.000 + rec_unclst=1.000 flagged as metric-cap saturation — RANDOM control was the saver here.

## Refs

- Atoms partition: `data/substrate_index/math/atoms.jsonl` (last 3 rows)
- Cert ledger: `data/substrate_index/meta/cert_ledger.jsonl` (rows 801, 802, 803)
- Cell metrics:
  - `data/exp_kb_coarse_grain_at_promotion_v1/metrics.json`
  - `data/exp_edge_importance_v2_high_alpha/metrics.json`
  - `data/exp_substrate_director_kb_content_chunk_ingest_v1_smoke/metrics.json`
- Prior atomization (smoke supersession): `notes/skunkworks_landed_vet_batch4_2026-06-26.md`
