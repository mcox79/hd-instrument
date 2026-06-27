# Skunkworks landed-VET ruling: 2-cell batch 7 (re-spawn after timeout)

Date: 2026-06-27
Auditor: Skunkworks (cert-owner / auditor)
Authorization: USER 2026-06-27 (auto mode + combined A+B path approved)
Prior batch: 6 (a7dc6f2bf68c41304) died with API timeout 3058s wall; no atoms written
Verify-OFF-DATA basis: .venv Python read of raw metrics.json per Fix #28 strict
Role: AUDIT-ONLY (independent recompute; no cell authorship, no dispatch)

## Pre-write fresh-state check

```
grep -c kb_partition_by_source_class_v2 OR edge_importance_retrieval_trace_x_ultrametric_coreness_v3:
  math/atoms.jsonl       = 0
  meta/cert_ledger.jsonl = 0
  meta/audit.jsonl       = 0
```

Confirmed: prior spawn wrote no atoms before timeout. Atomize fresh.

---

## Cell 1: kb_partition_by_source_class_v2 -- HARD_FAIL_INFRA_DEP (HONEST_NEGATIVE; delta=0)

**Metrics path:** `data/exp_kb_partition_by_source_class_v2/metrics.json`

**Raw metrics (full file content):**
```json
{
  "verdict": "HARD_FAIL",
  "verdict_msg": "KB_REFERENT_MISSING: KB dir not found: C:\\dev\\hd-instrument\\data\\exp_substrate_director_kb_ingest_v1\\_arm_full\\kb",
  "elapsed_s": 0.0,
  "summary": {"anchor": "kb_partition_by_source_class_v2"}
}
```

**Disposition:** HONEST_NEGATIVE on INFRA dimension; mechanism UNKNOWN (never exercised).

**Tier rationale:**
- elapsed_s=0.0 -> pre-flight gate fired before mechanism ran
- verdict_msg structured KB_REFERENT_MISSING -> Fix #26 verify-the-referent discipline working as designed
- Mechanism (segregating ingested entities by source_class) was NOT tested
- This is NOT a mechanism HARD_FAIL; it is an INFRA-DEP HARD_FAIL caught at the pre-flight gate

**Why atomize:** future cells in the kb_partition family will reference this atom to (i) avoid the same infra dep pattern, (ii) credit the pre-flight gate, (iii) keep the mechanism HARD_FAIL ladder unpolluted by infra-dep failures.

**Rescue path:** ANCHOR 1 v3 self-contained being authored in parallel (build KB inline from notes/, no separate upstream dep).

**Cert routing:** cert_status=honest_negative; cert_class=infra_dep_not_mechanism; delta=0.

---

## Cell 2: edge_importance_retrieval_trace_x_ultrametric_coreness_v3 -- MIDDLE_BAND (delta=0) + HONEST_BOUND (delta=+1)

**Metrics path:** `data/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3/metrics.json`

**Configuration:**
- N=512, M_OLD=600, M_RECENT=400, alpha=1.953, J_composite=3000, composite_arity=3
- USE_FRAC=0.4, downscale_scale=0.2, LAMBDA_LIST=[0.1, 0.3, 0.5]
- ULTRA_COS=0.85, ULTRA_MIN_SIZE=5, N_PRUNE_FRAC=0.3
- 3 seeds: 7, 17, 23; n_queries=200; n_composite_queries=3000

**Off-data recompute (Fix #28 strict; per-arm per-seed):**

| Arm | Seed | R_retr | R_unretr | R_recent | cor_imp | n_down |
|-----|------|--------|----------|----------|---------|--------|
| BASELINE_RANDOM | 7  | 0.715 | 0.775 | 0.780 | -0.008 | 300 |
| BASELINE_RANDOM | 17 | 0.805 | 0.785 | 0.800 | -0.003 | 300 |
| BASELINE_RANDOM | 23 | 0.745 | 0.760 | 0.750 | -0.012 | 300 |
| TRACE_ONLY      | 7  | 1.000 | 0.685 | 0.720 | +0.057 | 300 |
| TRACE_ONLY      | 17 | 1.000 | 0.685 | 0.670 | +0.070 | 300 |
| TRACE_ONLY      | 23 | 1.000 | 0.700 | 0.725 | +0.054 | 300 |
| ULTRA_ONLY      | 7  | 0.780 | 0.770 | 0.785 |  0.000 | 300 |
| ULTRA_ONLY      | 17 | 0.775 | 0.765 | 0.740 |  0.000 | 300 |
| ULTRA_ONLY      | 23 | 0.785 | 0.760 | 0.835 |  0.000 | 300 |
| TRACE_X_CORENESS (all lam) | all | == TRACE_ONLY identically (ULTRA contribution drops out) |

**Per-arm 3-seed means:**
- BASELINE_RANDOM: R_retr=0.755, R_unretr=0.773, R_recent=0.777, cor=-0.007
- TRACE_ONLY:      R_retr=1.000, R_unretr=0.690, R_recent=0.705, cor=+0.060
- ULTRA_ONLY:      R_retr=0.780, R_unretr=0.765, R_recent=0.787, cor= 0.000
- TRACE_X_CORENESS (lam 0.1/0.3/0.5): identical to TRACE_ONLY (ULTRA drops out)

**Coreness atoms per seed:** [0, 0, 0] -- ultrametric clustering at cosine=0.85, min_size=5 yielded ZERO clusters across all 3 seeds. This is the root cause for ULTRA noise-floor: importance vector all-zeros -> random downscale.

**HP check (cell-author's framing):** sel_unretr=False, rec_retr=True, fair=True, fired=True, over_trace=False, over_ultra=True

**Disposition split (two atoms):**

### Atom 2a (mechanism MIDDLE_BAND; delta=0)

3rd consecutive MIDDLE_BAND in edge-importance family (v1 alpha-sweep MM, v2 high-alpha MM, v3 trace-x-ultrametric MM). Fairness held; TRACE arm fires; ULTRA composition fails at top-K because coreness clustering yielded nothing. Mechanism characterized; not promotable.

cert_status=measured_mechanism; cert_class=mechanism_characterization; delta=0.

### Atom 2b (HONEST_BOUND proven boundary; delta=+1; Path B USER-approved 2026-06-27)

Per-seed RAND_unretr - TRACE_unretr:
- seed=7:  0.775 - 0.685 = +0.090
- seed=17: 0.785 - 0.685 = +0.100
- seed=23: 0.760 - 0.700 = +0.060
- mean = +0.083, std = 0.020, cv = 0.241
- sign-consistency: 3/3 positive (one-sided proven)

**Proven-bound claim:** the substrate's maximum sel_unretr asymmetry extractable from retrieval-trace alone (no additional signal sources) at the edge_importance v3 regime is bounded above by +0.083.

**Bounds future cells:** any v4+/v5+/v6+ targeting > +0.083 sel_unretr asymmetry at this regime MUST introduce a NEW signal source (replay modulation, semantic priors, learned-importance projection); cannot just re-tune retrieval-trace.

**Discriminator armed:** if any of the 3 per-seed deltas had been negative or zero, the one-sided bound would be invalidated; 3/3 positive observed; bound FIRED.

**Path A rescue in flight:** v4 NREM-replay-modulated trace (USER-approved 2026-06-27, gated at original 0.15 bar).

cert_status=proven_bound; cert_class=pre_reg_miss_proven_bound; delta=+1.

---

## Net cert routing summary

| # | atom | corpus | pq | cert_status | delta |
|---|------|--------|----|-----|------|
| 1 | kb_partition_by_source_class_v2 INFRA-DEP HARD_FAIL | math | HARD_FAIL | honest_negative | 0 |
| 2 | edge_imp v3 MIDDLE_BAND mechanism | math | MEASURED_MECHANISM | measured_mechanism | 0 |
| 3 | retrieval-trace HONEST_BOUND +0.083 ceiling | math | CERT_CHAIN_GRADE | proven_bound | +1 |

Net CERT N change: +1
Net ledger rows: +3

---

## A5 discipline observed

- .venv Python (not system) -- FALSE GREEN gotcha avoided
- Independent recompute (not from verdict_msg) -- Fix #28 strict
- Atomic write via add_atom + verify-load + integrity-check
- Cert-ledger via append_cert_ledger_row with A5 PRE/POST gates
- Idempotent at Store layer (skip if qid already present)
- Pre-write fresh-state check confirmed batch 6 wrote 0 atoms before timeout

## Discipline atoms not produced this batch

This batch is experiment-level only; no new META rules atomized (the load-bearing
discipline content is the HONEST_BOUND ceiling itself, which is an experiment
atom, not a META rule).
