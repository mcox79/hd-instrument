# exp_dev -> strategy routing: caching_admission_control_v2 BLOCKED

**Date:** 2026-06-02
**Priority:** MEDIUM (not urgent — production pipeline has 9 anchors queued)

## What was blocked

`caching_admission_control_v2` smoke HARD_FAIL. Script design: use spectral proxy (alpha_eff = M/N_eff) to trigger admission control threshold (ADMIT_THRESHOLD=0.12). Deny patterns that would push capacity beyond alpha_c.

## Smoke failure details

- N=512, M_TOTAL=105 (writes planned), alpha_effective = 105/512 = 0.205 > alpha_c_theory=0.138
- All 105 patterns admitted (admission rate = 1.0), acc_naive = 1.0
- The proxy alpha_eff NEVER reached ADMIT_THRESHOLD=0.12 during the test
- Suspicious: acc_naive=1.0 > HF=0.75 (too good = likely measurement wrong, not below alpha_c)

## Root cause hypothesis

The spectral proxy (current count / N_eff) accumulates linearly but the admission gate fires at M/N > 0.12, which is alpha=0.12. At smoke N=512 with 105 total writes, the first write is pattern 1/512 = alpha=0.002 — far below threshold. The threshold is NEVER hit because the smoke runs TOO FEW patterns before hitting the target ceiling.

Alternatively: the proxy may underestimate alpha at small N due to finite-size effects in the spectral gap used for N_eff estimation.

## What strategy needs to decide

1. Is the admission control mechanism correct (deny patterns when alpha_eff > alpha_c proxy)?
2. Should the test operate at HIGHER alpha (pre-fill to near alpha_c, then test admission)?
3. Should the smoke scale be redesigned (pre-load M_base = 0.10 * N, then test admission at 0.12-0.20)?
4. Is the alpha_c proxy itself reliable at small N?

## Rehabilitation options

A. Pre-fill the substrate to alpha=0.10 (baseline), then test writes from 0.10 to 0.20 — this puts the test in the regime where admission control fires.
B. Use a directly measurable retrieval accuracy gate instead of spectral proxy: deny when acc_batch drops below 0.85.
C. Drop the probe from this batch — caching_admission_control_v1 already completed with verdict (check verdict log).

## Cap map row affected

CAP-7 (caching / admission control) — not yet in cap_map as confirmed row.

Acted-on 2026-06-02: caching_admission_control_v2 block noted; deferred to research redesign queue
