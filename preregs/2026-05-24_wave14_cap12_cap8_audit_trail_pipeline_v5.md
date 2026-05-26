# Pre-registration: wave14_cap12_cap8_audit_trail_pipeline_v5

**Date:** 2026-05-24
**Queue:** `remote_cpu_queue`
**Script:** `experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v5.py`
**ETA:** ~30-45 min CPU
**Depends on:** `wave14_cap8_vamp_iterates_rm_1_m_v1` (Anchor 1, same queue)
**Anchor type:** Composition A audit-trail with REAL iterates across ALL 4 hard families

## Purpose

Composition A audit v4 reported per-family Spearman rho on the
kappa_n-divergence vs Schur-Weyl mass-n-deviation vectors:

| family   | v4 rho | iterates loaded? |
|----------|--------|------------------|
| Kerdock  | (per v4) | no (v1 archived; not in audit-loader layout) |
| SRHT     | (per v4) | yes (v1c) |
| Hadamard | (per v4) | yes (v1c) |
| RM(1, m) | 0.40   | **no -- silently fell back to spectrum-only** |

v5 disambiguates whether RM(1, m) rho=0.40 is a FALLBACK ARTIFACT (shorter
fingerprint vectors) or a GENUINE property of the family by:

1. Multi-root iterate loader (v1c + rm_1_m_v1).
2. Iterate-eligible family set expanded to `{srht, hadamard, rm_1_m}`
   (Kerdock continues spectrum-only).
3. Per-family `iterate_root_used` recorded.

## Configuration

- `N = 4096`, `M_over_N = 1.0`, `n_seeds = 5`, `n_max_order = 5`
- `codebooks = ["kerdock", "srht", "hadamard", "rm_1_m"]` (HARD_FAMILIES)
- `use_iterates = True`, `iterate_wait_seconds = 1200`
- `ITERATE_ROOTS = [v1c, rm_1_m_v1]`
- `ITERATE_ELIGIBLE = {srht, hadamard, rm_1_m}`

## Verdict bands (pre-registered)

### HARD PASS — `COMPA_AUDIT_LICENSED` (Composition A licensed at full 4-family scope)

- Spearman `rho >= 0.60` across `>= 3 of 4` hard families with REAL iterates
- AND no family with `rho < 0.30`
- AND no family is TIED (`sw_std` and `kd_std` both `>= 1e-9`).

### HARD FAIL — `COMPA_AUDIT_KILLED` (Composition A definitively killed)

- `rho < 0.30` on `>= 2 of 4` hard families.

### MIDDLE BAND — `COMPA_AUDIT_MIDDLE_BAND`

- Anything else (incl. 1-2 families passing).

## Key disambiguation question

- If RM(1, m) v5 rho **rises above 0.60** -> v4's 0.40 was a fallback artifact;
  Composition A licenses (assuming SRHT/Hadamard also clear 0.60).
- If RM(1, m) v5 rho **stays near 0.40 or drops** -> RM(1, m) genuinely has weak
  kappa_n / Schur-Weyl structure; the per-family character is real, not artifact.
- Either way, the v5 vs v4 delta on RM(1, m) is the ANSWER to this dispatch's
  driving question.

## Self-tests (run before main)

1. All v3 self-tests inherited (iterate fingerprint, load-missing-returns-None,
   verdict branches, schur-weyl basics).
2. `find_iterate_trace_v5` multi-root search returns None for absent seed,
   non-None paths exist. ITERATE_ROOTS deduplication. RM(1, m) root present.
3. `ITERATE_ELIGIBLE` contains `rm_1_m` (this is the point), and excludes
   `kerdock` (its iterate root is not in audit-loader layout).
4. iid-Gauss x Schur-Weyl analytical baseline: at c=1, MP-baseline mass_(2,)=1.0
   exactly; empirical Gauss N=M=1024 mass_(2,) > 0.95. Plus mp_m_1=1.0, mp_m_2=2.0.

## Smoke

`N=1024, n_seeds=1, n_max=4, codebooks=[kerdock, iid_gauss], use_iterates=False`
-> INCONCLUSIVE verdict expected (only 2 of 4 hard families); self-tests +
loader logic + iid baseline must all pass.
Smoke output: `data/exp_wave14_cap12_cap8_audit_trail_pipeline_v5_smoke/`.
Smoke result (2026-05-24): **PASS**, verdict=COMPA_AUDIT_INCONCLUSIVE,
iid_gauss mass_(2,)=1.000000 matches MP exactly, multi-root loader logic verified.

## Blockers / risks

- v5 depends on Anchor 1 having produced 15 RM(1, m) trace files in
  `data/exp_wave14_cap8_vamp_iterates_rm_1_m_v1/iterates/rm_1_m/alpha_{0p50,0p75,1p00}/`.
  The 1200s iterate_wait_seconds gives Anchor 1 up to 20 min runway if v5 starts
  before Anchor 1 finishes (Anchor 1 ETA 10-15 min).
- If Anchor 1 fails or partials, v5's RM(1, m) result reverts to spectrum-only
  fallback -- check `iterate_used_by_family["rm_1_m"]` in metrics.json before
  interpreting v5 rho.

## Outputs

- `data/exp_wave14_cap12_cap8_audit_trail_pipeline_v5/metrics.json`
  - top-level: `verdict`, `mode="full"`, `rho_by_family`, `tied_by_family`,
    `iterate_used_by_family`, `iterate_roots`, `iterate_eligible_families`.
  - `summary.codebook_results[*].iterate_root_used_per_seed` -- per-seed audit trail.
