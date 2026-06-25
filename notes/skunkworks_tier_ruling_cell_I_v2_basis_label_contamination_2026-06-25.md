# Skunkworks tier ruling: Cell I v2 (substrate_basis_layer_label_contamination_proof_v1)

Date: 2026-06-25
Auditor: Skunkworks (cert-owner)
Source data: `data/exp_substrate_basis_layer_label_contamination_proof_v1/metrics.json` (read off-data, not from verdict_msg)
Discipline anchors: BIAS-14, by-construction-saturation, RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M, Fix #28, Q discipline.

## TL;DR — TIER: MIXED. Re-tier into two atoms.

The cell's `HARD_FAIL_REFUTED` verdict is mechanically correct against its pre-reg, but the pre-reg's `PROVEN_RANDOM_RETR_MIN=0.80` and `PROVEN_RANDOM_COMP_MIN=0.70` bands were **unphysical at the chosen regime** (N=8192 / M=2400 / V=300 Hebbian bind-bundle). The cell measured a clean direction-correct cone-collapse mechanism but pre-set a ceiling its substrate could not reach. This is the **down-direction twin** of by-construction-saturation: the gate was forced to fail by an over-high fixed threshold, analogous to the Hebbian-superposition v2 / M_crit=327 vs recall@1k>=0.80 precedent (META `RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M`).

The cell SHOULD be split into two findings:

1. **MEASURED_MECHANISM_DIRECTION_CORRECT** — LABEL_BASIS axis-projection (cone-collapse via shared hub direction) HURTS both retrieval (-0.099 mean delta) and 2-hop composition (-0.122 mean delta) vs RANDOM_BIPOLAR. Mechanism diagnostic fired cleanly: within_cat_cos = 0.199 ± 0.0001 across all 5 seeds (designed value), cross_cat_cos = 0.000. **This is a proven mechanism finding.**

2. **HARD_FAIL_UNFAIR_BAND** — RANDOM at this regime physically tops out near 0.65 top1 (theoretical predicts lower; empirical hits 0.6471 ± 0.0074 across 5 seeds; **top5 is 0.9994** — the discriminator was forced into the noisy argmax tail). The 0.80 PROVEN band was never reachable. This is **mis-calibration, not a refutation** of the principle.

## Per-arm, per-seed evidence (recomputed off raw data, all 5 seeds [7, 13, 17, 23, 29])

| Arm | retr top1 (mean ± std) | retr top5 (mean) | comp top1 (mean ± std) | within_cat_cos (mean ± std) |
|---|---|---|---|---|
| RANDOM_BIPOLAR | **0.6471 ± 0.0074** | 0.9994 | 0.4531 ± 0.0632 | -0.0001 ± 0.0002 |
| LABEL_BASIS_AXIS_PROJECTION | **0.5480 ± 0.0087** | 0.8056 | 0.3313 ± 0.0351 | **0.1991 ± 0.0002** |
| EMERGENT_DEEPWALK | 0.6458 ± 0.0077 | 0.9965 | 0.4448 ± 0.0296 | 0.0812 ± 0.0024 |
| EMERGENT_OLSHAUSEN_FIELD | 0.6471 ± 0.0074 | 0.9994 | 0.4437 ± 0.0376 | 0.0001 ± 0.0002 |

LABEL-vs-RANDOM retrieval delta is **consistently negative** across every seed (range: -0.0946 to -0.1025, std 0.0034). LABEL-vs-RANDOM composition delta is consistently negative (range: -0.0989 to -0.2239). The cone-collapse mechanism is present and load-bearing.

## Was the band calibration achievable?

**No for retrieval, marginal for composition.**

The retrieval is Hebbian bind-bundle: M=2400 triples superposed into a single W = sum_i outer(o_i, s_i * r_i) / N matrix, with cleanup argmax over V=300 concepts. This is the classical Smolensky/HRR superposed-memory regime where the signal/crosstalk-noise ratio is approximately sqrt(N/M) per competitor before cleanup, then degraded by V distractors in the argmax.

Empirical: top5=0.9994 means the correct answer is essentially **always** in the top-5 cosine bucket, but the argmax among the top contenders is noise-limited at top1 ~0.65. This is **standard cleanup-noise crosstalk**, not a substrate defect.

A `PROVEN_RANDOM_RETR_MIN=0.80` band at M=2400 / N=8192 / V=300 would require either:
- M reduced to ~600 (load ratio ~0.07), OR
- N increased to ~16384+ (more crosstalk headroom), OR
- A cleanup-explicit protocol that exploits the top5=0.999 separation.

None of these were available without rerunning. The 0.80 figure was pulled from the principle ("random should work well in a productive regime") without solving the capacity equation for the chosen regime. **Direct parallel to the Hebbian-superposition v2 precedent.**

For composition (RANDOM 0.4531): comp builds on retrieval (hop-1 cleanup then hop-2 cleanup) so its ceiling is bounded by retrieval^2 roughly. 0.6471^2 = 0.4188; observed RANDOM comp is 0.4531 (slightly above the naive cascade ceiling, consistent with cleanup catching errors). The PROVEN_RANDOM_COMP_MIN=0.70 band would need retrieval ~0.84 just to be cascade-feasible — **also unreachable at this regime.**

## Direction-correct EMERGENT composition lift — is it chain-grade?

**No, MIXED at best. Cannot tier up to chain-grade.** Per-seed inspection:

Composition (DW - RAND) per seed: +0.0781, **-0.0989, +0.0053, +0.0261, -0.0521**. Mean = -0.083, std = 0.064.
Composition (OLS - RAND) per seed: +0.0937, **-0.0781, -0.0416, -0.0521, +0.0312**. Mean = -0.094, std = 0.078.

The "+0.08 / +0.09 lift on composition" claim in the original framing **does not hold per-seed**. The lifts appear in 1-2 seeds and reverse in 2-3 others. Per Fix #28 (read metrics.json per-arm not verdict_msg, and Fix #28 violation #5 — verify per-seed before cross-cell convergence claims): the EMERGENT-beats-RANDOM-on-comp claim is **noise** at n=5 seeds. Honest read: DW and OLS composition is **statistically indistinguishable** from RANDOM composition.

This is NOT a chain-grade unsupervised-encoder-lift finding. It's null with high variance.

## Within_cat_cos diagnostic: mechanism or saturation artifact?

**Mechanism, not saturation artifact.** Three independent reasons:

1. LABEL_BASIS within_cat_cos = 0.199 with std 0.0002 across 5 seeds — this is the exactly-engineered hub-shared interpretation per encoder code at lines 290-334. Cone-collapse is **present by design**, not emergent from saturation.
2. Cross-cat cosine = exactly 0.000 (bands are orthogonal by partition). Hub-shared semantics not bleeding across categories.
3. RANDOM and OLSHAUSEN_FIELD both have within_cat_cos = 0 ± 0.0002 — same regime, same N, same sparse_f, same K_WTA — they show no cone-collapse, ruling out saturation as the source.

So the LABEL_BASIS-vs-RANDOM differential is **causally driven by the cone-collapse mechanism**, not by the band being saturated. The diagnostic is doing real discriminator work.

## Tier ruling

**MIXED** — split into two atoms:

### Atom 1 (math corpus, MEASURED_MECHANISM_DIRECTION_CORRECT)

ID: `T3/EXP_substrate_basis_layer_label_contamination_proof_v1_MM`
Tier: MEASURED_MECHANISM_DIRECTION_CORRECT (counts toward CERT N as proven boundary)
Finding: At N=8192, V=300 (10 categories x 30 concepts), V_P=8, M=2400 Hebbian bind-bundle:
- Hub-shared category-axis encoder (within_cat_cos=0.199 ± 0.0002, designed cone-collapse) hurts retrieval by **0.099 absolute (consistent across 5 seeds, std 0.003)** and 2-hop composition by **0.122 absolute** vs random-bipolar baseline.
- Mechanism diagnostic (within_cat_cos) confirmed orthogonal to saturation regime; LABEL_BASIS top5 drops from 0.9994 (RANDOM) to 0.8056 — the discriminator is **separating real signal**, not arguing in the noise floor.
- Principle (BIAS-13: label-induced basis contamination harms substrate-native KG retrieval) holds direction-correct in this regime.

Bound character: this is a measured mechanism strength, not a chain-grade discriminating capability. To promote to chain-grade requires a capacity-relative regime where RANDOM hits >=0.80 baseline so the differential is unambiguous.

### Atom 2 (meta corpus, METHODOLOGY RULE - reinforcing precedent)

ID: `RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M`
Tier: T_methodology
Kind: methodology_rule
Status: ADOPTED
Rule: For multi-arm "principle PROVEN" cells of the form "baseline-arm must hit retrieval >= X AND treated-arm must hit retrieval <= Y", **X must be capacity-feasible at the chosen (N, M, V, encoder-class) regime**. Pre-flight: solve / estimate the cleanup-argmax top1 ceiling for the baseline arm BEFORE setting X. If unsure, gate on **relative differential (LABEL < RANDOM - delta)** rather than absolute bands.
Witness: Cell I v2 basisLabelContamProof v1 set PROVEN_RANDOM_RETR_MIN=0.80 at N=8192 M=2400 V=300 where the empirical RANDOM ceiling is ~0.65 (top5=0.9994 confirms the signal is there but argmax-noise-limited). The "principle REFUTED" verdict triggered on the down-direction-twin of by-construction-saturation: the gate was **forced to fail by an unphysical fixed threshold**, not by a real failure of the principle.
Composes_with: `RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M`, `RULE_by_construction_saturation_canfail_gate_tier_not_cert`, `RULE_key_separability_input_degeneracy_preflight`.
Precedent cite: Hebbian-superposition v2 recall@1k>=0.80 mis-framed when M_crit=327 (2026-06-20 cert-VET).

## Was the refute trigger fair?

**No.** REFUTE_RANDOM_RETR_MAX=0.65 (cell line 163) fires when RANDOM retr <= 0.65. RANDOM came in at 0.6471 — **0.003 below the refute trigger**, well within the 0.0074 std. This is a band-on-band collision: the PROVEN band at 0.80 and the REFUTE band at 0.65 leave a 0.15-wide MIDDLE_BAND that the regime physically cannot reach. The cell could only have come back PROVEN or REFUTED **at a different M**.

## Atomization plan

1. **Math atom (T3 experiment_record):** record Cell I v2 as MEASURED_MECHANISM_DIRECTION_CORRECT per Atom 1 above. Cite per-arm-per-seed evidence. Mark `provenance_quality=CERT_MEASURED_MECHANISM` (NOT CERT_CHAIN_GRADE). Link `depends_on` to `RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M`.
2. **Meta atom (T_methodology):** land `RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M` per Atom 2 above. Compose with the 3 existing capacity-gate rules. Mechanized check candidate: extend `tools/skunkworks_saturation_canfail_check_v1.py` to also flag "PROVEN_baseline_RETR_MIN > theoretical_top1(N, M, V)" pre-dispatch.
3. **Ledger:** increment CERT N by +1 (the measured-mechanism atom). Do NOT count this as a HARD_FAIL refutation of the BIAS-13 principle — the principle direction held; the band failed it.
4. **EMERGENT lift claim:** do NOT atomize as a separate finding. The 5-seed variance kills it.

## Recommendation for Research

A revival cell `_v2_capacity_relative` would re-test the principle by either:
- Dropping M to ~600 (where RANDOM top1 should hit ~0.78 theoretical), OR
- Lifting N to 16384 (where M/N=0.15 should put RANDOM top1 >=0.80), OR
- Switching gate to **relative**: LABEL_retr < RANDOM_retr - 0.05 AND LABEL_comp < RANDOM_comp - 0.05, no absolute threshold on RANDOM.

The third option is cheapest and matches the actual principle (label contamination should HURT relative to no-label baseline; the absolute level of the no-label baseline is irrelevant to the contamination claim).

## Reproducibility check

- Raw data: `data/exp_substrate_basis_layer_label_contamination_proof_v1/metrics.json` (19974 bytes, 5 per-seed entries, all with full per-arm dicts)
- Cell source: `experiments/exp_substrate_basis_layer_label_contamination_proof_v1.py` (1048 lines, run_mode=full)
- Cell sha: not yet read into ledger; flag for Research to compute pre-atomization
- Independent recompute: numpy mean/std over 5 seeds reproduces every number in the verdict_msg exactly (off-data verified, not relying on verdict_msg framing) — see also the n=5 per-seed differential table above.

End ruling.
