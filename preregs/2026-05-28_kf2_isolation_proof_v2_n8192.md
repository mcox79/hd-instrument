# Pre-registration: kf2_isolation_proof_v2_n8192

**Date:** 2026-05-28
**Anchor:** kf2_isolation_proof_v2_n8192
**Script:** experiments/exp_kf2_isolation_proof_v2_n8192.py
**Queue:** remote_cpu_queue
**Routing note:** strategy_request_to_exp_dev_v260_kf2_n8192_envelope_extension_2026-05-28.md

## Hypothesis

KF-2 edit isolation (max_iso < 0.05) holds at N=8192 (production scale).
Theory bound at N=8192: 1/sqrt(8192) = 0.01105 (tighter than v1's 0.01563 at N=4096).
Expected: max_iso CLOSES toward theory_bound at higher N (if exceedance is finite-N artifact).

## Configuration

- N = 8192 (production scale; PROT-018 binding via _n8192 suffix)
- Seeds = [7, 17, 23, 31, 41] (5-seed; same as v1)
- M_fracs = [0.25, 0.5, 1.0, 2.0, 4.0] (same as v1)
- n_edits = 50 per M_frac cell (same as v1)
- Prior anchor: v1 N=4096 HARD_PASS max_iso=0.02020

## Pre-registered thresholds (HF1/HF2/HF3)

Prior anchor: v1 N=4096 HARD_PASS max_iso=0.02020. Bands NOT widened (prior empirical anchor).

**HARD_PASS_TIGHT:** max_iso < 0.02020 across ALL M_fracs AND all 5 seeds.
  Interpretation: N=8192 tightens the isolation; product story strengthens.

**HARD_PASS_STANDARD:** max_iso in [0.02020, 0.05) across all cells.
  Interpretation: N=8192 confirms structural edit isolation at production scale.

**HARD_FAIL:** max_iso >= 0.10 at any under-cap M_frac (structural contamination).
  Would require re-analysis of edit-isolation claim.

**MIDDLE_BAND:** max_iso in [0.05, 0.10); partial isolation.

## Cap_map impact

- HARD_PASS: KF-2 ACTIVE row promotion confirmed at N=8192; product narrative full-confidence.
- TIGHT variant: tighter bound annotated (edit isolation improves with N).
- HARD_FAIL: KF-2 requires re-analysis.

## Timeout estimate

- v1 ran 19.6s at N=4096 (5 seeds x 5 M_fracs x 50 edits).
- N-scale factor: (8192/4096)^1.5 = 2.828x.
- timeout_s = ceil(1.5 * 19.6 * 2.828) = 83s -> 600s (conservative).
- Under 2h: no extra flag.

## Formula self-tests

1. theory_bound at N=8192: 1/sqrt(8192) = 0.01105. Verified.
2. theory_bound(N=8192) < theory_bound(N=4096). Verified.
3. isolation_ratio = max(|delta_acc[j]|) over j != edited. Range [0, 1].
4. HARD_PASS fires at max_iso=0.01 < 0.05. Verified in selftest.
5. HARD_FAIL fires at max_undercap_iso=0.15 >= 0.10. Verified in selftest.

## OOM check

W float32 at N=8192: 268MB. No large key tensors. Peak ~300MB. Under 6GB. PASS.

## Smoke gate

Passed: N=1024 1-seed smoke. max_iso=0.030 < 0.05. HARD_PASS_STANDARD verdict at smoke scale.
elapsed_s=0.2s.
