# Routing: gold-sequence kappa quickprobe -> local_cpu_queue

**From:** exp_dev
**Date:** 2026-05-23
**Tier:** C (quick scoping, <60s, single-config, 1 seed)

## Context

Cross-domain codebook landscape probe. Existing landmarks on the BBMD
axis:
- Paley Type-I Hadamard sub-block: PERFECT_ISOMETRY (kappa_n=0)
- Kerdock 4-coset: BBMD candidate (kappa_n grows, bulk-bounded)
- Haar: free (kappa_n -> 0)
- iid Gauss: MP (kappa_n = c)

Gold sequences disambiguate between "GF(2^m)-trace algebraic structure"
(shared with Kerdock) vs "4-coset combinatorics" (Kerdock-specific) as
the driver of the BBMD signature.

## Smoke result

`python experiments/exp_wave14_kappa_gold_quickprobe_v1.py --smoke` at
m=6, N=63, alpha=1 returned **GOLD_BBMD_CANDIDATE** in <1s:
- self-test PASS: family shape OK, 3-valued cross-correlation verified
  on 50/50 random pairs (allowed values {-17, -1, 15})
- m=10 family generates without error; m-sequences balanced
- kappas k_1..k_4 = [+1.0000, +0.0474, -0.0136, +0.0422]
  (n>=2 values are tiny but non-zero -- still in BBMD class because they
  diverge from MP reference c=1; spectrum is bulk-bounded
  [0.000, 2.016] within MP edges [0.000, 4.000])

Smoke smoke FAIL would have been: assertion failure in self-test, missing
metrics, or NON_MP_OUTLIER class (which would have required H3 follow-up).

## Hypothesis

If m=10 / N=1023 result is BBMD_CANDIDATE: BBMD signature is GENERIC
to GF(2^m)-trace codebooks, not Kerdock-4-coset-specific (expands
substrate addressable envelope). If MP_LIKE: Kerdock-specific. If
NON_MP_OUTLIER: new axis (spectral outliers from 3-valued correlation).

## Queue entry

| queue            | name                                  | script                                                    | prereg                                                | timeout(s) |
|------------------|---------------------------------------|-----------------------------------------------------------|-------------------------------------------------------|------------|
| local_cpu_queue  | wave14_kappa_gold_quickprobe_v1       | experiments/exp_wave14_kappa_gold_quickprobe_v1.py        | preregs/2026-05-23_wave14_kappa_gold_quickprobe_v1.md | 180        |

ETA: <60s wallclock on local CPU. Timeout 180s for safety.

## Note on CPU runner

Per [[project-cpu-resource-underutilized]] the local CPU runner has been
dead since 2026-05-21. If `cpu_runner_local` heartbeat is stale, the
entry will sit in `data/local_cpu_queue/queue.json` until the runner
is revived. exp_dev recommends the orchestrator check
`data/local_cpu_queue/heartbeat.cpu_runner_local.json` and revive via
`tools/orchestrator/cpu_runner_0_launcher.bat` (or the schtasks revive
script) before relying on quickprobe turnaround.
