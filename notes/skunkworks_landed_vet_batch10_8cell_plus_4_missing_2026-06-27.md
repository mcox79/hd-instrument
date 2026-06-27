# Skunkworks landed-VET batch 10 (2026-06-27, 8 cells landed-local + 4 missing-on-laptop)

Per Research request 2026-06-27 ~15:00Z. Verify-off-data per Fix #28 (.venv Python + per-arm + per-seed re-derive). Default UNDER-claim. CERT N pre-batch = 622 (per live Store query).

## Verdict summary table

| # | Cell | Verdict (mine) | CERT delta | Note |
|---|---|---|---|---|
| 1 | bge_index_refresh_full_corpus_v1 | INFRA_OK (not a science cell) | 0 | Cache write only; 177655/177655 indexed; not atomize-worthy |
| 2 | edge_importance_v6_CFU_stronger_regime | NO_METRICS_LOCAL | n/a | Not landed on laptop; cannot VET |
| 3 | edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix | MIDDLE_BAND_PARTIAL_PASS | 0 | TRACE arm sel-minus-rand=+0.083; only 2 of 6 hp_checks pass; ULTRA arm fails |
| 4 | n8_proofwiki_smoke_ingest_chunk_kb_v2_retry | NO_METRICS_LOCAL | n/a | Not landed on laptop |
| 5 | stage3_typed_routing_falsification_bijective_v1 | NO_METRICS_LOCAL | n/a | Not landed on laptop |
| 6 | multihop_kbeam_pathsum_v1 | SANITY_BREACH_HONEST_NEGATIVE (regime-drift) | 0 | sanity_d2 baseline=0.1017 << [0.60,0.70] band; main arms uninterpretable; halt was correct |
| 7 | substrate_multihop_brain_pushback_composition_v1 | NO_METRICS_LOCAL | n/a | Not landed on laptop |
| 8 | multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu | HARD_FAIL_NO_MEETING_PREMIUM (REGIME-SPECIFIC reframe of v2 chain-grade) | 0 | All 4 verdict_msg numbers reproduce; bidir indistinguishable from fwd_half + only marginally above random at all depths |
| 9 | gap3_cls_two_tier_BCM_v2_init_fix | HARD_FAIL_UNIT_EXCEPTION_BCM_NUMERICAL_OVERFLOW | 0 | RuntimeError float-overflow at init; mechanism not exercised; not even a science result |
| 10 | edge_importance_stratified_replay_baseline_diagnostic_v1 | HARD_FAIL_CARDINALITY_BREACH | 0 | META_RULE_H breach (expected 4 arms, got 6); cardinality_ok=False halt; halt was correct |
| 11 | substrate_vs_md_head_to_head_post_compaction_recovery_v1 | UNKNOWN_INFRA_DEP (substrate needs chunk KB built first) | 0 | All 3 arms halt-per-META_RULE_J on substrate subprocess error "no chunk KB built yet"; A/B never ran |
| 12 | pc_cleanup_attractor_v1 | **HONEST_NEGATIVE_PC_NO_OP_AT_SATURATED_REGIME (NOT chain-grade)** | 0 | **CRITICAL DOWNGRADE from HARD_PASS framing.** Three smoking-gun catches below. |

**Net CERT delta: 0** (no chain-grade ratifications this batch; 1 CRITICAL downgrade vs Director framing).

## CRITICAL CATCH 1: PC_cleanup_attractor v1 NOT chain-grade

The cell-author + Director framed this as HARD_PASS / CHAIN_GRADE candidate (CERT +1). Verify-off-data caught THREE blocking issues:

**Catch 1a: All three arms produce BIT-IDENTICAL fe_per_hop arrays across all seeds and depths.**

```
seed=7 d=5: VANILLA / PC_AT_EACH_HOP / PC_FINAL_ONLY all == (1.487089, 1.488344, 1.498771, 1.498464, 1.499331)
seed=7 d=10: all three arms == (1.472871, 1.513795, 1.487466, 1.473475, 1.502632, 1.524853, 1.521860, 1.485921, 1.488436, 1.480491)
seed=17 d=5: all three == (1.517916, 1.475389, 1.490377, ...)
seed=23 d=5: all three == (1.514630, 1.465313, 1.499993, ...)
```
Identical to 6 decimal places. This is NOT noise; this is the same number.

**Catch 1b: `fe_monotone_non_increasing` flag is FALSE on every arm of every depth of every seed in per_seed, but verdict_msg ASSERTS "monotone FE".**

Direct cell-data contradiction. The cell COMPUTED `monotone = bool(all(fe[i] >= fe[i+1] - 1e-6 ...))` and got False, then `verdict_msg` says the opposite. Classic verdict_msg miscite.

**Catch 1c: All arms saturate at recall=1.000 across both depths in all 3 seeds.**

V=1024, N=2048, M_CHAINS=80 — the regime is too easy for the discriminator. Vanilla baseline already at 1.0, so PC arms cannot demonstrate lift. By-construction-saturation per META_RULE_K + Fix #28 BIAS-Q (suspect 1.000 results).

**Off-code mechanism diagnosis:** `run_chain_pc_each_hop` calls `hop_pc_refined`, which computes `top1_idx = top_k_idx[argmax(top_k_sims)]` — at this regime (no noise breakdown), the top-K-restricted argmax IS the full-codebook argmax, AND the FE is computed from the SAME softmax over the SAME sims. So PC is operationally a no-op when recall=1.0 and PC_TOP_K is large enough to contain the true index. The PC mechanism may still help at harder regimes (higher V, noisier hops, deeper chains where vanilla degrades below saturation) — but THIS regime does not exercise it.

**Tier: HONEST_NEGATIVE_PC_NO_OP_AT_SATURATED_REGIME** (cert-neutral; delta=0). Not chain-grade; not even MM (no mechanism-specific lift measured).

**Follow-up:** Re-run at V in {4096, 8192}, N=8192, M_CHAINS in {200, 500}, with explicit HOP_NOISE_P_FLIP sweep [0.05, 0.15, 0.30] to FORCE vanilla baseline below saturation. The PC arms should then either lift (chain-grade evidence) or fail at the same level (mechanism-falsifying). Either is informative; the saturated regime is not.

## CRITICAL CATCH 2: Bidirectional v3 GPU correctly reframes v2 as REGIME-SPECIFIC

v2 had landed BIDIR_MEET_MID=0.620 at d=5 (chain-grade candidate). v3 with proper controls (fwd_half, random_meet, depth-scaling d in {3,5,7,9}) shows:

```
d=3: fwd=0.320, bidir=0.443, fwd_half=0.684, rand=0.402, mscale=0.430
d=5: fwd=0.131, bidir=0.329, fwd_half=0.460, rand=0.319, mscale=0.329
d=7: fwd=0.071, bidir=0.258, fwd_half=0.320, rand=0.254, mscale=0.258
d=9: fwd=0.032, bidir=0.179, fwd_half=0.216, rand=0.180, mscale=0.179
```
All numbers reproduce from per_seed (5 seeds: 7, 17, 23, 41, 53). At every depth: **bidir < fwd_half**. So the "bidirectional meeting in the middle" claim was actually just "forward-half-depth retrieval" — the meeting step adds nothing over half-depth forward. Worse, bidir is only marginally above random at all depths (cond3 over_rand>=0.15 FAILS at every depth).

**Two cell-design notes:**
- `arm_multiscale_bidirectional ≡ arm_bidir_meet_mid` (identical per-seed values at d=5,7,9). Code-duplicate or intentional alias; not contributing independent evidence. Flag to cell-author for v4.
- `_llm_forward_calls_at_inference = 0` confirmed. Substrate-only-decode gate PASS.

**Tier: HARD_FAIL_NO_MEETING_PREMIUM_REGIME_SPECIFIC** (cert-neutral; delta=0). Importantly: this DOES NOT demote the v2 chain-grade — it reframes its REGIME (d=5 only, with v2's specific arm config) as not generalizing to depth-scaled or fwd-half-controlled regime. The v2 cert atom should be ANNOTATED with this regime-narrowing finding via a cert-ledger note (not full demote).

## Other dispositions (briefer)

**v3p2 edge_importance MIDDLE_BAND (cell 3):** verdict_msg reproduces (alpha=1.953, lam=0.1, RAND retr/unretr=0.755/0.773, TRACE retr/unretr=1.000/0.690, sel_minus_rand=+0.083). 2-of-6 hp_checks pass (rec_retr, fair). ULTRA arm sel_minus_rand=+0.008 = at-noise-floor. MIDDLE_BAND tier is correct; not chain-grade. Follow-up: drop ULTRA composition (same finding as batch 8 cell 4 — ULTRA cluster geometry mismatch).

**K-beam pathsum SANITY_BREACH (cell 6):** sanity_d2 numbers reproduce exactly: baseline=0.1017 vs band [0.60, 0.70] band FAILS. 2026-06-24 regime not reproduced. Cell-author halt-on-sanity-breach is correct discipline. Cardinality 45/45 OK. Main arm K10_PATHSUM d5=0.0117 is uninterpretable because sanity broke. HONEST_NEGATIVE_REGIME_DRIFT. Follow-up: cell-author must reconstruct 2026-06-24 regime parameters (codebook seed, chain construction) before re-attempting beta-sweep.

**gap3 BCM v2 init-fix HARD_FAIL (cell 9):** RuntimeError on init "value cannot be converted to type float without overflow" — exit at 1/12 units. The init-fix patch did not address the actual init bug. Tier: HONEST_NEGATIVE_INIT_FIX_INSUFFICIENT (sister to batch 8 cell 2 BCM_AT_CHANCE finding — BCM mechanism is failing across multiple cell variants).

**stratified replay diagnostic v1 HARD_FAIL (cell 10):** META_RULE_H cardinality breach (expected 4 arms, got 6 at seed=7) — arm-count drift between summary's `arms=[...]` (4 declared) and per_seed (6 actual). v2 with proper import guard (sister cell) already landed MIDDLE_BAND with same content; v3 is in CONTAMINATED state. Cell 10 finding: cell-author cardinality declaration must match actual loop iteration.

**head-to-head substrate-vs-md UNKNOWN (cell 11):** ALL 3 arms (latency, content, freshness) halt with same substrate subprocess error "ERROR: --chunk-content requested but no chunk KB built yet. Run experiments/exp_substrate_director_kb_content_chunk_ingest_v1.py first." So head-to-head was prerequisite-blocked, not an A/B verdict. UNKNOWN_INFRA_DEP. Follow-up: dispatch chunk-KB-ingest cell FIRST, then re-run head-to-head.

## 4 cells with NO local metrics

`exp_edge_importance_v6_CFU_stronger_regime`, `exp_n8_proofwiki_smoke_ingest_chunk_kb_v2_retry`, `exp_stage3_typed_routing_falsification_bijective_v1`, `exp_substrate_multihop_brain_pushback_composition_v1` have NO `data/<cell>/metrics.json` on laptop. They were named in the request but not actually present. Either (a) sync from remote didn't include them, OR (b) they were dispatched but never landed. Cannot VET without metrics. Defer to next batch when files arrive.

## META rule candidates (4) — atomization recommended

These are atomization-grade discipline findings from today's batch + drills. I'm NOT atomizing them in this spawn (time-budget; default to under-claim per Fix #28). Recommending next-spawn atomize via tool pattern in `tools/atomize_skunkworks_meta_3rules_plus_retier_barrier1_quadruple_2026-06-27.py`.

**META_RULE_W (pre-dispatch alpha-in-[0.03, 0.20] gate for associative-memory cells):** Hopfield-family / Hebbian-tied cells with `alpha = M / N` outside [0.03, 0.20] either operate below the capacity floor (under-loaded, no discriminator pressure) or above the crosstalk wall (recall collapses). v3p2 ran at alpha=1.953 (massively over-capacity); BCM v2 also at high alpha. Pre-reg gate: cell-author MUST declare alpha + justify if outside [0.03, 0.20].

**META_RULE_X_MAIN_GUARD (experiment cells must guard main with `__name__ == '__main__'`):** From import-bug drill today. When a cell module is imported (e.g. for partial-load recovery), top-level code that calls `main()` re-fires the full experiment. Required: `if __name__ == "__main__": main()` at bottom; never bare `main()` call.

**META_RULE_Y_PARTIAL_LOAD_ANCHOR_CHECK (partial_load must verify anchor name):** Partial-metric load tools must check that loaded `anchor_name` MATCHES the requesting cell's anchor; otherwise contamination (e.g., the v3_anchor_leak we saw in stratified). Drop the load + re-run if mismatch.

**META_RULE_Z_FIX_ADDRESSES_ROOT_CAUSE (HARD_FAIL fix must address root cause not symptom):** BCM v2_init_fix HARD_FAILED on the SAME numerical-overflow type-class as v1 — the "fix" patched a symptom (likely a default-value tweak) without addressing the BCM update equation's numerical instability. Discipline: a HARD_FAIL fix-cell must include in its pre-reg a SPECIFIC root-cause claim + a test that would distinguish "root-cause fixed" from "symptom masked".

## Files referenced

- /d/AI/hd-instrument/data/exp_pc_cleanup_attractor_v1/metrics.json (the bit-identical-arms catch)
- /d/AI/hd-instrument/data/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu/metrics.json (regime-specific reframe)
- /d/AI/hd-instrument/data/exp_edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix/metrics.json (MIDDLE_BAND)
- /d/AI/hd-instrument/data/exp_multihop_kbeam_pathsum_v1/metrics.json (SANITY_BREACH)
- /d/AI/hd-instrument/data/exp_gap3_cls_two_tier_BCM_v2_init_fix/metrics.json (init-fix HARD_FAIL)
- /d/AI/hd-instrument/data/exp_edge_importance_stratified_replay_baseline_diagnostic_v1/metrics.json (META_RULE_H breach)
- /d/AI/hd-instrument/data/exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1/metrics.json (UNKNOWN infra-dep)
- /d/AI/hd-instrument/data/exp_bge_index_refresh_full_corpus_v1/metrics.json (infra OK)
- /d/AI/hd-instrument/experiments/exp_pc_cleanup_attractor_v1.py (off-code diagnosis lines 302-345 + 350-397)
- /d/AI/hd-instrument/data/session_local/skunkworks/_batch10_*.py (off-data verify scripts; reproducible)

Skunkworks 2026-06-27 ~15:15Z. CERT N unchanged at 622.
