# Skunkworks back-fill batch — 9 items — A5-gated atomize 2026-06-25

Date: 2026-06-25 (evening; USER-approved cert-ledger back-fill batch)
Cert-owner: Skunkworks (audit-only)
Method: independent recompute off `metrics.json` per-seed per-arm; substrate-mine of existing atoms.jsonl + cert_ledger.jsonl; Q-discipline applied throughout.
Driver: USER quote — "Yes I want a cert ledger back fill - I am sick of us rediscovering old experiments." Director routed via `notes/director_to_skunkworks_cert_trail_backfill_tasks_2026-06-25.md`.

## Summary of rulings (overrides + agreements with Director spec)

| # | Item | Director spec | My ruling | Reason |
|---|---|---|---|---|
| 1 | Consolidation v3 HARD_FAIL | atomize | **AGREE** HARD_FAIL honest_negative | 3 seeds full; mechanism refuted; per-class smoking gun confirmed |
| 2 | WM-scaffolded HARD_FAIL | atomize | **AGREE** HARD_FAIL honest_negative | 3 seeds full; depth-degrades; per-hop survival ~0.70 compounding |
| 3 | Refuse-gate near-domain v2 chain-grade | atomize chain-grade | **AGREE** chain_grade | Mechanism honest (out-of-library bipolar relations); envelope: V_RELATIONS_IN=8 |
| 4 | NESS envelope chain-grade | atomize chain-grade | **SKIP** (already in Store + ledger CERT 592) | Director didn't verify atoms.jsonl + ledger; both already present from 2026-06-20 atomize |
| 5 | capacity_sweet_spot_v1_cpu_v1 chain-grade | atomize chain-grade | **OVERRIDE → MEASURED_MECHANISM** | v1 selector picks sel_f=0.01 for EVERY task (degenerate, not adaptive); v2 already atomized as MM proving fixed f=0.01 never beaten; Fix #28 inflated-claim pattern caught |
| 6 | per_cluster_stratified chain-grade | atomize chain-grade | **OVERRIDE → MEASURED_MECHANISM** | run_mode=smoke, n_seeds=1; BIAS-14 (production scale) + symmetric anti-negativity; cannot chain-grade on smoke + single seed |
| 7 | sparse_onset_higher_loads chain-grade | atomize MEASURED_MECHANISM | **AGREE** MEASURED_MECHANISM | run_mode=smoke, n_seeds=1; Director already framed as MM tier in spec |
| 8 | META_M4 + META_M5 atoms back-fill | atomize | **AGREE** back-fill atoms.jsonl entries from existing ledger rows (no new ledger writes; idempotency-aware) | Phase 3 cert-trail integrity gap; flag for atoms.jsonl ↔ cert_ledger.jsonl consistency check META rule next cycle |
| 9 | META_BARRIER_1_TRIPLE_NEGATIVE | optional META composition | **AGREE** atomize META composition (CERT-neutral, delta=0) | Composes consolidation_v3 + pointer_chain_v2 + WM_scaffolded as triple-negative for Barrier 1 substrate-native multi-hop at production scale |

## Expected CERT N delta

- pre: 594 (verified live read at spawn start)
- chain-grade atom adds (+1 ledger delta each): refuse_gate v2 = +1
- honest-negative atom adds (+0 ledger delta each, count as proven negative): consolidation v3, WM-scaffolded = +0 cert delta but +2 honest_negative entries
- MM atom adds (+0 ledger delta): capacity_sweet_spot v1, per_cluster_stratified v1_smoke, sparse_onset v1 = +0
- META atoms (+0 ledger delta): META_M4, META_M5 back-fill, META_BARRIER_1_TRIPLE_NEGATIVE = +0
- **post: expected 595** (+1 for refuse_gate v2 chain-grade)

Director's expected 600-602 was based on assuming 4 older HARD_PASS verdicts could all be chain-graded at face value. Q-discipline overrides 3 of those to MM (one was already in cert, one was selector-degenerate, two were smoke + n_seeds=1). Honest CERT N = 595.

This is exactly the "back-fill PREVENTS rediscovery" outcome — the cert architecture says these capabilities EXIST as mechanism characterizations (MM tier), they just don't reach chain-grade rigor (smoke + single seed cannot do that work). Future cycles can promote MM→chain-grade with full multi-seed dispatch IF the substrate-product story needs them.

## Per-item rulings (off-data verify + Q-discipline)

### 1. Consolidation v3 HARD_FAIL — math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL

**Verdict: HARD_FAIL honest_negative.** Mechanism refuted.

Off-data per-seed recompute (verified):
- NAIVE 2hop: [0.845, 0.905, 0.800] mean=0.8500 cv=0.062
- CONSOL K=1 HELDOUT: [0.020, 0.000, 0.000] mean=0.0067
- CONSOL K=3 HELDOUT: [0.120, 0.100, 0.100] mean=0.1067
- CONSOL K=10 HELDOUT: [0.120, 0.100, 0.100] mean=0.1067
- CONSOL K=50 HELDOUT: [0.400, 0.400, 0.400] mean=0.4000 cv=0.000
- HYBRID K=3+cleanup: [0.120, 0.100, 0.100] mean=0.1067

Smoking gun per-class: consolidated → ~0%; unconsolidated → 100% (matches naive). K=50 "best" 0.40 is mechanically (1 destroyed class × 30/50 + 2 untouched × 20/50) / 1 = 0.40. The K=50 arm wins by doing the consolidation primitive LESS.

Rails fired: NAIVE_OUT_OF_BAND (0.850 not in [0.62, 0.68]) + KTHR_GATING_NOT_DIFFERENTIATING (train spread 0.006 < 0.10). Both rails are M2/M6 rail-derivation debt (band copied from v2 single-pair regime; v3 has V_P=6 multi-class). The mechanism failure is per-class consolidated→0% regardless of rails.

Composes with: pointer_chain_v2_HARD_FAIL (atomized morning 2026-06-25) + this batch's WM-scaffolded_HARD_FAIL for Barrier 1 triple-negative.

### 2. WM-scaffolded multi-hop HARD_FAIL — math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL

**Verdict: HARD_FAIL honest_negative.** WM scaffold reduces to pointer-chain at production scale.

Off-data per-seed recompute (verified):
- BASELINE 2hop: [0.605, 0.670, 0.675] mean=0.6500 cv=0.060 (1/3 seeds out-of-band low: seed7=0.605)
- WM_2HOP: [0.485, 0.375, 0.415] mean=0.4250 cv=0.131
- WM_5HOP: [0.145, 0.110, 0.110] mean=0.1217 cv=0.166
- WM_10HOP: [0.040, 0.035, 0.030] mean=0.0350 cv=0.143

Per-step accuracy seed 7 (d=10): [0.69, 0.485, 0.31, 0.205, 0.145, 0.1, 0.07, 0.065, 0.04, 0.04] — per-hop survival ratio ~0.70; compounding 0.70^10 ~ 0.028 matches observed 0.035.

Director's spec cited cv values [0.107, 0.136, 0.117]; my recompute is [0.131, 0.166, 0.143] (using statistics.stdev sample-stdev; Director may have used pstdev). Doesn't change HARD_FAIL ruling. WM_2hop=0.425 underperforms baseline 0.650 by 22.5pp. Identical structure to pointer_chain v2 (also 0.425) — the WM scaffold adds zero discriminative information vs pointer-chain.

Composes with: consolidation_v3_HARD_FAIL + pointer_chain_v2_HARD_FAIL for Barrier 1 triple-negative.

### 3. Refuse-gate near-domain v2 HARD_PASS_BOTH_WORK — math::T3/EXP_substrate_refuse_gate_near_domain_v2_chain_grade

**Verdict: chain_grade.** Audit-relation-check ALONE closes the medqa-style failure.

Off-data per-seed recompute (verified) NEAR_DOMAIN_MIXED refuse_rate:
- AUDIT_NAIVE_ALONE: [0.0, 0.0, 0.0] mean=0.000 cv=0.000 (MEDQA failure reproduced — naive audit can't catch out-of-domain relations on in-domain subjects)
- AUDIT_RELATION_CHECK: [1.0, 1.0, 1.0] mean=1.000 cv=0.000 (smarter audit alone closes the gap)
- INTENT_ALONE: [1.0, 0.96, 1.0] mean=0.987 cv=0.023
- AUDIT_NAIVE+INTENT: [1.0, 0.96, 1.0] mean=0.987 cv=0.023

Per pre-reg HARD_PASS_BOTH_WORK branch: "pick the simpler" — audit-relation-check is the substrate-product refuse-gate design.

Q-discipline saturation check on 1.000 result:
- Mechanism honest: `arm_audit_relation_check` does `max(W_relations_in @ rel_vec) >= 0.40` where W_relations_in is the 8-relation in-library and rel_vec is sampled from out_relation_atoms (separate bipolar random library, NOT in W_relations_in).
- Random bipolar dot product at N=8192: noise floor sqrt(2/8192) ~ 0.016, well below threshold 0.40.
- Out-of-library relations therefore yield max-sim ~0 reliably → refuse=1.000 is mechanically correct, not by-construction-saturation.
- ENVELOPE CAVEAT (atomize as metadata): mechanism works because V_RELATIONS_IN=8 is small + out_relation_atoms are random bipolar. At larger V_RELATIONS_IN, false-refuse rate on in-library relations would grow. Operating envelope: V_RELATIONS_IN <= ~50 at N=8192 with random bipolar; structured/learned relations TBD.

CERT-grade conditions met: 3 seeds full, cv=0.000 across seeds, 100 queries per category per seed, sanity rails passed (PURE_IN answer=1.000, PURE_OUT refuse=1.000), pre-reg discriminator NEAR_DOMAIN refuse >= 0.70 met by 1.000, MEDQA failure reproduced on naive-alone arm.

### 4. NESS envelope SKIP — ALREADY ATOMIZED

Already in Store as `math::T3/EXP_kmax_ness_envelope_corrected_v1` with provenance_quality=CERT_CHAIN_GRADE; already in cert_ledger.jsonl via `phase_a_backfill` row (cert_increment_delta=1). Verified via grep at spawn start.

Director's spec omitted to verify atoms.jsonl + ledger before listing this item. No write needed; Director re-audit notes should be updated to reflect.

### 5. capacity_sweet_spot_v1_cpu_v1 — math::T3/EXP_capacity_sweet_spot_v1_cpu_v1_MM

**Verdict OVERRIDE: MEASURED_MECHANISM (NOT chain_grade as Director framed).**

Off-data inspection:
- v1's "adaptive" selector picks sel_f=0.01 for EVERY task (lowload, midload, highload, veryhigh). It is NOT adaptive — it always picks the sparsest f.
- v1 verdict_msg claims "f-adaptivity beats fixed-f by ≥10pct on ≥2 high-load tasks". Technically true (sel_f=0.01 outperforms fixed f=0.05 because more sparse → more capacity), but the SELECTOR added NO value — picking f=0.01 always would yield the same result.
- v2 (`math::T3/EXP_capacity_sweet_spot_v2_cpu_v1`, already atomized as MEASURED_MECHANISM) makes this explicit: `earns_keep=False`, fixed f=0.01 never beaten by the adaptive selector, within 0.019 of oracle.
- v1 HARD_PASS framing is the Fix #28 inflated-claim pattern: claim from verdict_msg without checking per-arm sel_f varies.

Atomize as MEASURED_MECHANISM; metadata records that v2 supersedes the framing with honest characterization. v1 is the FIRST observation of the broad-sweet-spot phenomenon (informative); v2 is the proof that the selector adds no value.

### 6. per_cluster_stratified_extraction_with_random_control_v1_smoke — math::T3/EXP_substrate_per_cluster_stratified_extraction_with_random_control_v1_smoke_MM

**Verdict OVERRIDE: MEASURED_MECHANISM (NOT chain_grade).**

- `run_mode: smoke`, `n_seeds: 1` — cannot chain-grade on single seed at smoke regime per BIAS-14 (production-scale instrument calibration) + symmetric anti-negativity discipline.
- Director's spec said "chain_grade candidate"; cert-owner ruling: cannot chain-grade evidence from n_seeds=1 smoke. The random-control discriminator IS valid (arm2_cov@sp1000=0.457 vs arm1=1.000; discrim=0.543) but the multi-seed CV check the chain-grade tier requires is absent.
- Atomize as MEASURED_MECHANISM (mechanism characterization); upgrade path to chain-grade = re-dispatch at run_mode=full with n_seeds>=3 (queue this as next-cycle research follow-up).

### 7. sparse_onset_higher_loads_followup_cpu_v1 — math::T3/EXP_sparse_onset_higher_loads_followup_cpu_v1_MM

**Verdict: MEASURED_MECHANISM** (Director's spec already framed as MM tier; ruling agrees).

Off-data check: run_mode=smoke, n_seeds=1, located alpha_c(f) for f=[0.02, 0.03, 0.04, 0.05, 0.1] at LOADS<=8, monotonic Willshaw rise, seed-stable cv<=0.05 (single seed). f=[0.002, 0.005, 0.01] still capped >=lower-bound at LOADS<=8.

MEASURED_MECHANISM tier-appropriate for boundary-refinement work. Atomize as theoretical-limit measurement; not capability claim.

### 8. META_M4 + META_M5 atoms.jsonl back-fill

Both have cert_ledger rows from 2026-06-25 morning (atomized_by `skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25`) but NO entries in `data/substrate_index/meta/atoms.jsonl`. The atom-write step was skipped in the original flow.

**Action:** back-fill atoms.jsonl entries using existing ledger rows as source-of-truth for atom name, content, provenance. No new ledger writes (rows already exist; idempotency-aware via `_ts_stripped` check).

Phase 3 cert-trail integrity gap caught. Next-cycle META candidate: `META_atoms_jsonl_cert_ledger_consistency_check` — verify every cert_ledger row has a matching atoms.jsonl entry; alert if drift. Surface as recurring-pattern META if found in 2+ instances (this is instance #1; flag for second-instance triggering).

### 9. META_BARRIER_1_TRIPLE_NEGATIVE — meta::T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent

**Verdict: META composition rule, CERT-neutral (delta=0).** Optional per Director spec; I'm INCLUDING it because the three constituent cells are all atomized now and the cross-cell pattern is load-bearing for substrate-product positioning.

Composes:
- `math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL` (morning 2026-06-25)
- `math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL` (this batch)
- `math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL` (this batch)

Together: substrate-native multi-hop generalization at production-scale random-bipolar isotropic regime (V_C=200-600, V_P=2-10, N=8192, K_SET=20) is REFUTED across compound-predicate consolidation AND pointer-chain hybrid AND WM-scaffold mechanisms. 2-hop ceiling is substrate-product permanent at this regime.

Does NOT refute: (a) multi-hop at OTHER regimes (anisotropic encoder, structured corpus, learned attention over pointer keys), (b) semantic-consolidation under feature-share cortical analog (different cell), (c) external scaffold (PFC-analog) routing.

## Discipline checks (load-bearing for cert architecture)

### Verify off data (every cited number)
- Every number reproduced from per_seed via .venv Python statistics.mean/stdev independent recompute (not from verdict_msg framing). Director's WM-scaffolded cvs slightly differ from mine (Director [0.107, 0.136, 0.117] vs mine [0.131, 0.166, 0.143]); both confirm HARD_FAIL.

### Q-discipline (suspect 1.000 results)
- refuse_gate_v2 1.000 verified honest (corpus-surface-mismatch + 8-relation library mechanism); chain-grade with envelope caveat.
- per_cluster_stratified 1.000 arm1_cov = perfect-by-construction (stratified sampling by definition covers strata); discriminator is arm2 vs arm1, not arm1 alone. Discriminator is honest (random control fails at 0.457).
- capacity_sweet_spot v1 rec_selector=1.000 = degenerate selector picks always-sparsest-f; v2 already proved this. MM not chain-grade.

### BIAS-13/14/15 (contamination/regime/mismatch)
- smoke + n_seeds=1 caught on per_cluster_stratified + sparse_onset → MM not chain-grade.
- production-scale verification done on consolidation v3 + WM-scaffolded (full mode, 3 seeds, N=8192).

### Verify the referent
- NESS envelope already-in-ledger caught via atoms.jsonl + cert_ledger.jsonl grep BEFORE atomize attempt; Director's spec didn't verify.
- META_M4 + META_M5 ledger-only state verified before back-fill.

### Symmetric anti-negativity
- Honest UPWARD: refuse_gate_v2 ruled chain-grade despite USER concern about 1.000 results (mechanism verified honest).
- Honest DOWNWARD: 3 Director-claimed chain-grades demoted to MM at same rigor as upward correction.

## Atomization map (this batch only)

| # | atom_id | corpus | cert_status | delta | atomize_action |
|---|---|---|---|---|---|
| 1 | T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL | math | honest_negative | 0 | NEW atom + NEW ledger row |
| 2 | T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL | math | honest_negative | 0 | NEW atom + NEW ledger row |
| 3 | T3/EXP_substrate_refuse_gate_near_domain_v2_chain_grade | math | chain_grade | +1 | NEW atom + NEW ledger row |
| 4 | T3/EXP_kmax_ness_envelope_corrected_v1 | math | (SKIP — already present) | 0 | SKIP |
| 5 | T3/EXP_capacity_sweet_spot_v1_cpu_v1_MM | math | measured_mechanism | 0 | NEW atom + NEW ledger row |
| 6 | T3/EXP_substrate_per_cluster_stratified_extraction_with_random_control_v1_smoke_MM | math | measured_mechanism | 0 | NEW atom + NEW ledger row |
| 7 | T3/EXP_sparse_onset_higher_loads_followup_cpu_v1_MM | math | measured_mechanism | 0 | NEW atom + NEW ledger row |
| 8a | T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated | meta | meta_rule | 0 | NEW atom only (ledger row already exists, idempotency-checked) |
| 8b | T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match | meta | meta_rule | 0 | NEW atom only (ledger row already exists, idempotency-checked) |
| 9 | T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent | meta | meta_rule | 0 | NEW atom + NEW ledger row |

Total atoms landed: 9 (3 math experiment_record HARD_FAIL/MM/chain_grade, 1 chain_grade refuse_gate, 3 MM math, 2 META back-fill, 1 META composition).
Ledger rows added: 7 (8a/8b idempotency-skip).
CERT N delta: +1 (refuse_gate_v2 chain_grade).

## Path-scoped commit pattern

```
git add -f data/substrate_index/math/atoms.jsonl
git add -f data/substrate_index/meta/atoms.jsonl
git add -f data/substrate_index/meta/cert_ledger.jsonl
git add notes/skunkworks_back_fill_batch_2026-06-25.md
git add tools/skunkworks_back_fill_batch_2026-06-25.py
git commit -m "skunkworks: back-fill batch — 9 items A5-gated atomize (cert_n 594->595)"
```

Never `git add -A` (canonical Store in repo; blanket-add commits corrupt partition).

## Director feedback (next-cycle inputs)

1. **Fix #28 violation count (this batch caught 3 inflated chain-grade claims):** Director propagated "HARD_PASS = chain_grade" without checking per-arm sel_f varies (capacity_sweet_spot v1), without checking n_seeds + run_mode (per_cluster_stratified, sparse_onset already MM-framed). The capability re-audit v2 needs a per-item smoke+seed check column before classifying chain-grade-candidate.

2. **Cert-trail integrity META candidate (instance #1, atomize on instance #2):** atoms.jsonl ↔ cert_ledger.jsonl consistency. The cell3_cell4_consolidation atomize flow wrote ledger rows without atom-writes for META_M4/M5; this back-fill catches it. If a second instance occurs in next 5 cycles, atomize as META rule + add pre-commit hook to enforce.

3. **NESS envelope re-audit miss:** capability_audit_CORRECTION_v2 listed NESS as "missing from cert" but NESS was already CERT 592 since 2026-06-20. Director should re-grep atoms.jsonl + cert_ledger.jsonl before each "missing from cert" claim. This is Fix #28 #11 (re-narrative pattern: "I checked once 3 days ago" vs verifying NOW).

4. **2-hop ceiling now substrate-product permanent (META_BARRIER_1_TRIPLE_NEGATIVE):** three independent mechanism HARD_FAILs at production-scale isotropic regime closes the substrate-native multi-hop revival angle at THIS regime. Product positioning should now lead with "substrate IS 2-hop chain-grade; multi-hop reasoning routes via external scaffold OR feature-share semantic consolidation under different cell". Wave D encoder pivot strengthened by this triple-negative.

— Skunkworks (cert-owner; A5-gated atomize)
