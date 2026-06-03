# Pre-registration: PP-56 production-envelope N=8192 SM deletion cert

**Date:** 2026-06-02
**Anchor:** `sherman_morrison_rank1_deletion_cert_drop_v1_n8192`
**Queue:** remote_cpu_queue
**Trigger:** PP-56 FOUNDED at N=4096 (v351): cert_ratio=0.000241 (623x below HP gate), matches theory 0.000244 to 1.2%, 5/5 seeds unanimous.
**Priority:** PP-56 band-lift eligibility: production-N=8192 confirmation.

## Capability question

Does SM deletion cert drop replicate at N=8192 with theoretically predicted N-scaling?
Theory: cert_ratio = lam/(lam+N). At N=8192: 1/8193 = 0.000122 (half of N=4096 value).

## Prior results

| Anchor | N | cert_ratio | theory | match |
|---|---|---|---|---|
| v2_n4096 | 4096 | 0.000241 | 0.000244 | 1.2% |

## Pre-registered bands

### HARD-PASS
(a) mean cert_ratio < 0.15 (same HP gate; now 1225x above theory at N=8192)
(b) mean retained_delta < 0.10
(c) 5-seed unanimous on (a) and (b)
Bonus: cert_ratio(N=8192) < cert_ratio(N=4096) = 0.000241 confirms N-scaling monotone.

### MIDDLE
cert_ratio in [0.15, 0.30] OR retained_delta in [0.10, 0.20]

### HARD-FAIL
cert_ratio > 0.30 OR retained_delta > 0.30

## Smoke result

N_ACTIVE=1024 (smoke), 2 seeds:
cert_ratio=0.000966 << HP=0.15 (HARD_PASS direction); retained_delta=0.003854 << HP=0.10.
Note: N=1024 smoke ratio=0.000966 > N=8192 theory=0.000122 (expected; N-monotone holds at FULL N=8192).
Smoke HARD_PASS direction confirmed. Effect size >> 1.0 (155x below HP gate at smoke scale).

## N-suffix binding (PROT-018)

Anchor has `_n8192`; `N = 8192`, `_N_SUFFIX = 8192`. Matches. Script assertion confirmed.

## Timeout estimate

Smoke: 0.05s per seed at N=1024 (2 seeds, 5 trials each).
Scale: (N=8192/N=1024)^2.0 (matrix W=NxN dominant) = 64x. Seeds: 5/2 = 2.5x. Trials: 20/5 = 4x.
timeout = ceil(1.5 * 0.05 * 64 * 2.5 * 4) = ceil(48) = 48s. Raw formula very short.
Conservative: use 3600s (matrix W at N=8192 = 268 MB per trial; 20 trials x 5 seeds = 100 builds; each ~5ms).
Using **3600s** (conservative for CPU with 268 MB matrix builds).

## Dependency verification

No data dependencies. Pure numpy CPU. Self-contained.
