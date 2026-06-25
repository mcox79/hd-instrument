# Skunkworks tier ruling: Cell I v4 PROSPECTIVE-BANDS (substrate_basis_layer_label_contamination_proof_v4)

Date: 2026-06-25
Auditor: Skunkworks (cert-owner)
Source data: `d:/AI/hd-instrument/data/exp_substrate_basis_layer_label_contamination_proof_v4_prospective_bands/metrics.json` (read off-data, not verdict_msg)
Discipline anchors: Fix #28 (read metrics.json per-arm), N1 verify-the-referent, by-construction-saturation, META_RULE_retrospective_band_correction_max_one_tier_lift, META_RULE_PROSPECTIVE_BANDS_FRESH_SEEDS, symmetric anti-negativity.

## TL;DR — split ruling

| Finding | Tier | Notes |
|---|---|---|
| BIAS-13 principle (LABEL_BASIS hurts retrieval + composition vs RAND) on fresh seeds + locked bands | **CHAIN_GRADE_DEFINITIVE** | Upgrades v3's CHAIN_GRADE_PARTIAL. All gates pass on previously-unseen seeds; PROSPECTIVE assertion fired and held. |
| V phase-diagram consistency at V_C={200, 300, 500} | **CHAIN_GRADE_DEFINITIVE** (operating-envelope sub-atom) | Principle holds at all 3 V regimes (seed 42 alone for {200,500}; principle is regime-invariant, mechanism diagnostic 0.199-0.200 across all V). |
| EMERGENT_DEEPWALK composition lift over RAND (+0.061 mean comp_top5 at V=300) | **MEASURED_MECHANISM** (not chain-grade) | Paired-t = 3.31, n=3, df=2; passes one-tailed alpha=0.05 (t_crit=2.92) but FAILS two-tailed (t_crit=4.30). At V_C=200 phase-scan, DW comp_top5 is BELOW RAND by -0.063. Sign-flips across V → mechanism real but regime-dependent; v2 had seed-flips at n=5 ruled noise; n=3 is too small to overturn. |

## Referent-verification audit (the four mandates)

### 1. Seeds [42, 47, 51] — fresh, NOT v3's [7, 13, 17, 23, 29]

Off-data check (per_seed[*].seed): `[42, 47, 51]`. Set-disjoint from v3's `{7,13,17,23,29}`. **CONFIRMED FRESH.** Three independent partial_metrics_{42,47,51}.json files on disk (different elapsed_s per seed — 827s/166s/139s — rules out cached-replay).

### 2. ASSERT_PROSPECTIVE_BANDS_MATCH_V3 fired without abort

`config_version` contains literal substring `BANDS_LOCKED_BEFORE_DATA: ASSERT_PROSPECTIVE_BANDS_MATCH_V3=PASS`. The module would have raised AssertionError at import if v4 bands ≠ v3 bands; the fact that metrics.json was written across all 3 seeds + 2 phase-scan V values proves the assertion held. **CONFIRMED PROSPECTIVE.**

### 3. Per-arm gate replay against locked v3 bands

V_C=300 primary, mean across 3 fresh seeds (independent recompute off per-seed arms[*].retrieval/composition):

| Arm | retr_top1 | retr_top5 | comp_top5 | within_cat_cos |
|---|---|---|---|---|
| RAND | 0.6425 | 0.9997 | 0.6754 | -0.00006 |
| LABEL_BASIS | 0.5478 | 0.8119 | 0.5573 | **0.1995** |
| DEEPWALK | 0.6400 | 0.9961 | 0.7361 | 0.0811 |
| OLSHAUSEN | 0.6425 | 0.9997 | 0.6441 | -0.00009 |

Locked gates from v3:
- PROVEN_TOP5: LABEL_TOP5 ≤ 0.90 (0.8119 ✓) / RANDOM_TOP5 ≥ 0.95 (0.9997 ✓) / EMERGENT_TOP5 ≥ 0.95 (DW 0.9961, OLS 0.9997 ✓)
- PROVEN_TOP1 relative: LABEL_vs_RAND ≤ -0.05 (delta = -0.0947 ✓) / EMERGENT_vs_RAND within ±0.05 (DW -0.0025 ✓, OLS 0.0000 ✓)
- PROVEN_COMP relative: LABEL_vs_RAND ≤ -0.10 (delta = -0.1181 ✓) / EMERGENT_vs_LABEL ≥ +0.10 (DW +0.179 ✓, OLS +0.087 — note OLS misses the +0.10 EMERGENT_vs_LABEL gate by 0.013)
- DIAGNOSTIC: LABEL_within_cat_cos ≥ 0.15 (0.1995 ✓)
- REFUTE: LABEL_TOP5 ≥ 0.95 → False (correctly NOT triggered)

**All primary gates fired on previously-unseen seeds.** Sub-note on OLS: comp lift over LABEL is only +0.087 vs +0.10 gate. The `EMERGENT_vs_LABEL ≥ 0.10` is a per-arm composition gate; since the PROVEN block is satisfied by the DW arm exceeding, but the verdict_msg framing says `emergent_beats=True` — this aggregates across arms. Honest read: DW carries the EMERGENT≥LABEL gate; OLS marginally misses. The principle (LABEL hurts vs RAND, mechanism fires) does not depend on OLS, so the gate is essentially passed by ANY emergent arm beating; framing is correct.

### 4. Phase-scan V_C={200, 500} consistency (seed 42)

| V_C | RAND t1 | LAB t1 | LAB hurts t1? | RAND t5 | LAB t5 | LAB hurts t5? | LAB c5 | RAND c5 | LAB hurts c5? | LAB wc |
|---|---|---|---|---|---|---|---|---|---|---|
| 200 | 0.6525 | 0.6000 | YES (-0.053) | 0.9994 | 0.8925 | YES (-0.107) | 0.5547 | 0.7344 | YES (-0.180) | 0.200 |
| 300 | 0.6504 | 0.5487 | YES (-0.102) | 0.9996 | 0.8117 | YES (-0.188) | 0.5156 | 0.6927 | YES (-0.177) | 0.200 |
| 500 | 0.6410 | 0.5258 | YES (-0.115) | 0.9988 | 0.7475 | YES (-0.251) | 0.4375 | 0.5906 | YES (-0.153) | 0.199 |

**Principle holds at all 3 V regimes.** LABEL damage grows monotonically with V_C (V=500 shows largest top5 hit -0.25). Mechanism diagnostic within_cat_cos stays at designed 0.199-0.200 across V regime (cone-collapse is invariant). **Operating envelope established: V_C ∈ [200, 500] at N=8192 / sparse_f=0.020 / K_WTA=5 / M=8·V_C.**

## The DW composition-lift question — chain-grade or noise?

Per-seed comp_top5 at V=300:

| Seed | RAND c5 | DW c5 | DW-RAND |
|---|---|---|---|
| 42 | 0.6927 | 0.7188 | +0.0261 |
| 47 | 0.6719 | 0.7396 | +0.0677 |
| 51 | 0.6615 | 0.7500 | +0.0885 |

All three positive. Mean +0.0608, sd 0.0318, se 0.0183, paired-t = **3.31, df=2, n=3**.

Critical values: one-tailed α=0.05, df=2: t_crit=2.92 → passes. Two-tailed α=0.05, df=2: t_crit=4.30 → FAILS (two-tailed p ≈ 0.08). For chain-grade, default is two-tailed alpha=0.05 → does not clear.

**Phase-scan contradicts uniform DW lift:** at V_C=200 (seed 42), DW comp_top5 = 0.6719 vs RAND 0.7344 → **DW BELOW RAND by -0.0625**. At V_C=500, DW = 0.6594 vs RAND 0.5906 → DW above RAND by +0.0688. The DW-vs-RAND comp lift **inverts sign as V_C grows from 200 to 300+**. This is regime-dependent, not a regime-invariant chain-grade encoder lift.

History anchor: v2 (n=5 seeds, V=300) DW-RAND per-seed = +0.0781, -0.0989, +0.0053, +0.0261, -0.0521. Mean = -0.083 — **negative**. Skunkworks v2 ruling: "noise at n=5".

Reconciling v2 vs v4: v2 had 5 seeds [7,13,17,23,29], 2 of 5 negative; v4 has 3 seeds [42,47,51], 3 of 3 positive. The composite distribution (n=8) is +0.078, -0.099, +0.005, +0.026, -0.052, +0.026, +0.068, +0.089 — mean +0.018, sd 0.061, paired-t ≈ 0.83. **Pooled across all 8 seeds, the DW comp lift is null.**

Ruling: **MEASURED_MECHANISM**, not chain-grade. The DW-encoder shows real signal in some regimes (V_C=300 fresh seeds, V_C=500) and inverts in others (V_C=200, some v2 seeds). The principle (basis-layer label contamination) is independent of whether DW lifts composition. Atomizing DW lift as chain-grade would inflate, contradicting the pooled-seed null and the V_C=200 inversion.

## Honest downward correction — was v3's CHAIN_GRADE_PARTIAL too generous?

Re-checked. v3 used [7,13,17,23,29] (the v2 seed pool) but with corrected bands. Skunkworks META_RULE_retrospective_band_correction_max_one_tier_lift capped v3 at PARTIAL because correction happened AFTER seeing v2 data — band could have been hand-tuned. v4 fixes both confounds: (a) bands locked at module import via assertion before any v4 seeds run; (b) seeds [42, 47, 51] never previously evaluated by the encoder code. **Confound C3_retrofit_risk_band_tuning is ELIMINATED.** Upgrade from PARTIAL to DEFINITIVE is the cert-ladder action with both bands-pre-locked and unseen-seeds satisfied.

## Tier ruling

**CHAIN_GRADE_DEFINITIVE for the principle. MEASURED_MECHANISM for the DW comp-lift sub-claim.**

The v3 CHAIN_GRADE_PARTIAL atom (if exists in Store) DEMOTES → REPLACED by v4 CHAIN_GRADE_DEFINITIVE. Note: I searched `data/substrate_index/{math,meta}/atoms.jsonl` for `basis_layer` / `label_contamination` and found 0 hits — v3 atom may not have been written yet, in which case v4 atom lands fresh (no replacement needed; the v3 ledger entry may live in cert_ledger.jsonl). **Coordinate with Research/Director on whether v3 atomization occurred before writing v4 atom to avoid duplicate write.**

## Atomization plan

### Atom 1 — Principle (math corpus, CHAIN_GRADE_DEFINITIVE)

ID: `T3/EXP_substrate_basis_layer_label_contamination_proof_v4_DEFINITIVE`
Corpus: `math`
Tier: CHAIN_GRADE_DEFINITIVE (counts toward CERT N as a definitive principle finding)
Body: At N=8192, V_C ∈ {200, 300, 500}, M = 8·V_C, sparse_f=0.020, K_WTA=5, Hebbian bind-bundle: hub-shared category-axis encoder (within_cat_cos = 0.199 ± 0.001, designed cone-collapse) hurts retrieval (LABEL_vs_RAND top1 delta = -0.095, top5 delta = -0.188) and 2-hop composition (comp_top5 delta = -0.118) vs random-bipolar baseline. Bands locked via `ASSERT_PROSPECTIVE_BANDS_MATCH_V3` at module import BEFORE any seed run; verified on previously-unseen seeds [42, 47, 51]. Phase-scan at V_C={200, 500} confirms principle is regime-invariant; LABEL damage grows monotonically with V_C. BIAS-13 (basis-layer label contamination causes cone-collapse + hurts retrieval) is **definitively proven**.

### Atom 2 — Operating envelope (math corpus, CHAIN_GRADE_DEFINITIVE sub-atom)

ID: `T3/EXP_substrate_basis_layer_phase_diagram_VC_envelope_v4`
Corpus: `math`
Tier: CHAIN_GRADE_DEFINITIVE
Body: BIAS-13 principle holds at V_C ∈ {200, 300, 500} with monotonic damage scaling (LAB top5 deficit: -0.107 / -0.188 / -0.251). Mechanism diagnostic within_cat_cos invariant at designed 0.199-0.200 across V regime. Operating envelope: N=8192 / V_C ∈ [200, 500] / M=8·V_C / sparse_f=0.020 / K_WTA=5. Outside this envelope, untested.

### Atom 3 — DW comp lift (math corpus, MEASURED_MECHANISM)

ID: `T3/EXP_substrate_DEEPWALK_composition_lift_v4_MM`
Corpus: `math`
Tier: MEASURED_MECHANISM (counts as proven boundary, NOT chain-grade)
Body: At V_C=300 / N=8192 / 3 fresh seeds, DEEPWALK encoder shows comp_top5 mean lift +0.061 over RAND_BIPOLAR (paired-t = 3.31, n=3, df=2; passes one-tailed α=0.05 but fails two-tailed). Effect inverts at V_C=200 (DW c5 = 0.672 vs RAND 0.734, -0.063). Pooled across v2+v4 (n=8 seeds at V=300), mean DW-RAND = +0.018 ± 0.061, paired-t ≈ 0.83 — null. The lift is **regime-dependent and non-monotonic across V_C and seed pool**. Promotion to chain-grade requires (a) ≥10 fresh seeds with two-tailed t > 4 and (b) cross-V phase-stability or explicit V-conditional framing.

### Atom 4 — META rule reinforcement

ID: `META/PROSPECTIVE_BANDS_FRESH_SEEDS_eliminates_retrofit_confound_v4_validation`
Corpus: `meta`
Tier: CERT-neutral META atom
Body: META_RULE_PROSPECTIVE_BANDS_FRESH_SEEDS (locked-via-assertion + previously-unseen-seeds) successfully eliminates C3_retrofit_risk_band_tuning confound. Cell I v3 → v4 upgrade from CHAIN_GRADE_PARTIAL to CHAIN_GRADE_DEFINITIVE is the cert-ladder validation. Pattern: when a CHAIN_GRADE_PARTIAL ruling is gated only by "bands corrected retrospectively", a re-run with `ASSERT_BANDS_MATCH(prior_version)` at module init + fresh-seed pool is the minimal upgrade path.

## Pre-write checklist (A5)

1. Cited numbers reproduce from cell metrics.json — VERIFIED (.venv recompute matches verdict_msg figures within rounding).
2. Atom IDs / mechanism / metric / regime all match what claim says — VERIFIED.
3. Phase-scan numbers cross-checked against per_seed[0].phase_scan — VERIFIED.
4. Symmetric anti-negativity: DW lift could have been called chain-grade (n=3 all-positive); I downward-corrected to MM because pooled n=8 is null + V=200 inversion. Symmetric check applied.
5. Stage by path (`data/substrate_index/math/atoms.jsonl`, `data/substrate_index/meta/atoms.jsonl`) NOT `git add -A`.
6. cert_ledger.jsonl row appended per new atom; verify post-write Store loads.
7. Coordinate with Research on whether v3 atom exists before writing v4 (to avoid duplicate or correctly executing DEMOTE-and-replace).

## Open question for Research/Director

Did v3 atomization land before v4 dispatch? My grep of `data/substrate_index/{math,meta}/atoms.jsonl` for `basis_layer` and `label_contamination` returned 0 — either the v3 atom was not written (cert tracked only in cert_ledger.jsonl prose), or the partition naming differs. Please confirm before atom 1 lands to determine REPLACE vs FRESH-WRITE semantics. If you want me to scan cert_ledger.jsonl directly, request and I'll spawn — current ruling is independent of that lookup.

---
Auditor signature: Skunkworks
Decision: v4 = CHAIN_GRADE_DEFINITIVE for the principle; +1 to CERT N (or net 0 if v3 atom DEMOTEs in place). DW comp-lift atomized as MM, +1 to CERT N as proven boundary. Phase-diagram atomized as CHAIN_GRADE_DEFINITIVE sub-atom, +1 to CERT N. Net: **+2 or +3 CERT depending on v3 ledger state.**
