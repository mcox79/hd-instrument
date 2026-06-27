# Skunkworks landed-VET batch 3 — 4 cells — 2026-06-26

**Auditor:** Skunkworks (cert-owner)
**Method:** Verify-OFF-DATA via .venv Python recompute of metrics.json per-arm per-seed; NEVER from verdict_msg framings (Fix #28).
**Scope:** 4 cells handed off by Research (Director) for landed-VET this turn.

## Cell 1 — cortex_ultrametric_clustering_coarse_grain_v1
**Tier: CHAIN_GRADE (delta = +1)**
- Off-data recompute: ULTRA rec_cl=1.000, rec_un=1.000 (all 3 seeds bit-identical at 1.0); cap_drop=0.2121 (HP bar 0.20 cleared); RND rec_all=0.8963 at SAME cap_drop=0.212; d_ULTRA_vs_RND=+0.104; cv=0.000.
- Discriminator: ULTRA preserves recall at the same compression-cost where RND does NOT — this is mechanism, not by-construction-saturation. The "RND at same cap_drop" sibling-arm is exactly the kind of headroom-to-fail discriminator META_RULE we want.
- Supersedes the prior smoke-grade MEASURED_MECHANISM atom (near-miss cap_drop=0.192).
- **Significance:** First chain-grade WIN for cortex content-extraction after the E-tensor mechanism class was refuted (cor(E,|W|)=0.984 at smoke). Compositional-abstraction primitive operational.
- Supersedes ledger ID: `math::T3/EXP_cortex_ultrametric_clustering_coarse_grain_v1_smoke_MEASURED_MECHANISM_...`
- Atom ID: `math::T3/EXP_cortex_ultrametric_clustering_coarse_grain_v1_CHAIN_GRADE_full_3_seeds_...`

## Cell 2 — edge_importance_bound_pair_consolidation_v1
**Tier: MEASURED_MECHANISM (delta = 0)**
- Off-data: cor(E_derived,|W|) per-seed = (+0.062, +0.012, -0.043); max abs 0.062 — USER fairness gate <=0.50 cleared massively. Edge-importance IS structurally distinct from per-atom-scalar (Fix B mechanism class solved).
- BUT: all 3 arms saturate at rec_retr=rec_unretr=rec_recent=1.000; d_E_vs_RND=+0.000; mechanism not exercised at alpha=0.977. 760/1000 atoms downscaled but recall unchanged.
- Note Director's verdict_msg cited cor=0.010 — that is the SIGNED mean of (0.062, 0.012, -0.043) = +0.0103. The MAGNITUDE mean is 0.039 and the max abs is 0.062. All still well under fairness gate; framing is materially correct.
- Atom ID: `math::T3/EXP_edge_importance_bound_pair_consolidation_v1_MEASURED_MECHANISM_USER_fairness_gate_passed_...`

## Cell 3 — phase_diagram_wm_multibank_K_ceiling_sweep_32768_v2
**Tier: HONEST_NEGATIVE_WITH_META_VALIDATION (delta = 0)**
- Off-data: cardinality guard FIRED HARD_FAIL_CARDINALITY_BREACH_META_RULE_H — n_units=9 vs expected=27.
- K=4096: seeds {11,13} in MULTI_64x at rec=1.000 cv=0.000 (rail OK). NOT 3-seed chain-grade either.
- K=8192: seed 11 ONLY in MULTI_128x at rec=1.000. ONE seed only — Director's "K=8192 worked" framing is for ONE seed, NOT chain-grade.
- K=16384 and K=32768: silently dropped via non-OOM path (different failure mode than v1's silent-OOM-swallow). v3 must instrument this path.
- **META validation:** META_RULE_H atomized today (post v1 demote) caught this phantom-completion class same day; this is strong evidence for keeping cardinality guards mandatory pre-dispatch.
- Atom ID: `math::T3/EXP_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v2_HONEST_NEGATIVE_WITH_META_RULE_H_VALIDATION_...`

## Cell 4 — substrate_director_kb_bio_trio_ingest_v1
**Tier: MEASURED_MECHANISM_OPERATIONAL (delta = 0, tooling)**
- Off-data: 7/7 arms OK; Per-class triple counts confirmed (GO=189920, KEGG=10149, NIF=22274; sum=222343).
- ARM_INGEST_FULL_BIO_TRIO elapsed 83.4s under HP envelope 600s.
- Deterministic re-ingest: w_l2=0.0; atoms+entities+relations byte-equal across runs.
- Regression: total=276863 = bio_222343 + non_bio_preserved_54520 (sum identity holds).
- TOOLING cell — success bar is OPERATIONAL (arms_ok + envelope + determinism + regression-preserved); CERT-bands N/A. Enables downstream biology/neuro KG experiments.

## META rules atomized
- `meta::T_methodology/META_RULE_H_VALIDATED_same_day_v2_cell_with_cardinality_guard_...` — same-day validation reinforcement (CERT-neutral)
- `meta::T_methodology/META_RULE_G_REINFORCED_inverse_saturation_edge_importance_..._when_promoting_smoke_positive_to_FULL_MAINTAIN_or_INCREASE_alpha_not_decrease` — inverse-saturation pattern; smoke positive at alpha=1.367 became FULL-saturated at alpha=0.977 (CERT-neutral)

## A5-gated Store writes
- `data/substrate_index/math/atoms.jsonl`: 28583 -> 28587 (+4 atoms)
- `data/substrate_index/meta/atoms.jsonl`: 189 -> 191 (+2 META atoms)
- `data/substrate_index/meta/cert_ledger.jsonl`: 785 -> 791 (+6 ruling rows)
- All writes via tmp + os.replace + verify-load + JSON-integrity-check per A5 discipline.

## CERT N delta
**+1** (cell 1 chain-grade). Prior CERT 588 -> **CERT 589**.

## Flag-backs to Research
1. **Wave 3 dispatch unblocked** w.r.t. these 4 cells. Cell 1 is the substrate-product breakthrough — cortex content-extraction has its first chain-grade mechanism after 6 failed attempts.
2. **Cell 2 needs v2 at higher alpha** — pre-reg M_OLD/N >= 1.5 (e.g., N=1024 M_OLD=1500 M_RECENT=1000 or N=512 M_OLD=600 M_RECENT=400 at alpha=1.95). Smoke saw discriminator at alpha=1.367; FULL must MAINTAIN or INCREASE alpha not decrease.
3. **Cell 3 needs v3** — instrument the non-OOM silent-drop path for K>=16384 BEFORE re-dispatching. Cardinality guard FIRED correctly; need root-cause for the silent failure (likely tensor-dim or chunk-size assertion).
4. **K=8192 1-seed evidence is *suggestive*** — do not promote to chain-grade until 3 seeds at K=8192 land. Could be a cheap interim pre-reg (single arrangement, 3 seeds, K=8192 only) decoupled from the K-ceiling extension work.
5. **META_RULE_H is paying off** — keep the cardinality_ok boolean as a mandatory pre-reg field for any sweep-axis cell going forward (recommend codifying into pre-reg template).

## Cert-trail observability (HYBRID)
This note is the cert-trail observability artifact for batch 3. Cert atoms + ledger rows landed in Store (above paths). git-commit pending Director-cycle.
