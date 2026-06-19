# Pre-registration: wave14r_orthkeys_capsweep

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14r_orthkeys_capsweep.py](../experiments/exp_wave14r_orthkeys_capsweep.py)
Priority source: [active_priorities.md](../notes/active_priorities.md) Bet 2 follow-up;
companion to validated [wave14r_erase_orthkeys_v1](../experiments/exp_wave14r_erase_orthkeys_v1.py)
Author: experiment_dev session, cycle 4

## Why

[wave14r_erase_orthkeys_v1] validated `STRUCT_KEYS_FIX_MIRAGE` at M_stored=200
(N=4096). Strategy needs the **operating envelope**: how high can M_stored
go before the multi-probe Mirage protection breaks down? This is what
lifts the cap_map row from 🟢-validated (single-point) to ✅-validated
(envelope characterized).

For Hadamard-orthogonal keys, the theoretical capacity floor is M = N
(N orthogonal vectors in R^N). At M_stored << N, the substrate has slack;
as M_stored approaches N, kept-fact retrieval becomes increasingly fragile
because each k_e perturbation has more potential bridge-targets in the
stored subset.

## Hypothesis

At N=4096 with Hadamard-subcode keys, all 5 Mirage probes continue to
pass (per the v1 PASS thresholds) for M_stored ∈ {200, 800, 1600, 3200}.
The substrate's orthogonal-key Mirage protection is robust across the
0.05–0.78 ratio of M_stored/N tested here.

## Multi-probe success criteria (per M_stored)

Same as v1, at α=1.0 (the validated operating point):

1. argmax_leak < 0.05
2. mean_rank > 100
3. norm_ratio < 0.15
4. paraphrase_leak < 0.05 at Hamming h=8
5. kept_preservation > 0.95

Reported per M_stored across 3 seeds.

## Kill criterion (per M_stored)

Failing any criterion at a given M_stored = that M_stored is past the
envelope. The verdict reports the highest M_stored that still passes all
five, plus the failure mode at the first M_stored that breaks.

## Verdict labels (4)

- `CAPSWEEP_ROBUST` — all 4 M_stored values pass all 5 criteria;
  envelope extends through at least M_stored=3200
- `CAPSWEEP_BREAKS_AT_<M>` — passes through M_pass and breaks at M_pass*4
  or smaller; envelope characterized; verdict_msg reports the breaking
  probe(s) at the failure point
- `CAPSWEEP_BREAKS_IMMEDIATELY` — even M_stored=200 fails (would
  contradict v1; indicates test-setup divergence)
- `CAPSWEEP_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. Hadamard codebook orthogonality (reused from v1):
   `oracle.assert_in_range("hadamard_max_pairwise_ip", max_ip, (0.0, 0.01))`
2. At smoke's smallest M_stored, multi-probe must replicate v1's
   FIX_MIRAGE — argmax_leak should be low.

## Pre-mortem (3 failure causes)

1. **Sylvester Hadamard construction at N=4096 is slow if not cached** —
   build once per script, not per M_stored. Mitigation: codebook built
   in script setup, reused across the sweep.
2. **At M_stored close to N, kept_preservation depends sensitively on
   which N rows are sampled** — if a poorly-conditioned subset is drawn,
   noise dominates. Mitigation: 3 seeds + report std across seeds; v1's
   threshold band already accommodates seed noise.
3. **probe runtime at M_stored=3200 + n_erase=30 + paraphrase × 4 radii
   exceeds the 15-min target** — predicted total ~8-12 min; mitigation:
   smoke aborts on >180s; full mode will surface in dashboard timing.

## Operational definition

Reuses [exp_wave14r_erase_orthkeys_v1.py](../experiments/exp_wave14r_erase_orthkeys_v1.py)
functions directly:
- `make_hadamard_keys`
- `antihebbian_erase`
- `multi_probe`
- value codebook generation

Only differences vs v1:
- Loops over `M_stored ∈ {200, 800, 1600, 3200}` (smoke: {40, 100})
- Hadamard arm only (correlated arm omitted — v1 established the
  contrast; no need to re-burn cycles on the failing baseline)
- α = 1.0 (single point, not the {1.0, 1.5, 2.0} sweep)
- 3 seeds (instead of 5 — exploratory follow-up, not promotion-grade)

## Cited mechanism / sources

Same as v1; this is a parameter sweep of v1's exact mechanism.

## Expected runtime

- Smoke (N=512, M_stored ∈ {40, 100}, 1 seed): ~5-8 s on CPU
- Full (N=4096, M_stored ∈ {200, 800, 1600, 3200}, 3 seeds): estimated
  8-12 min on GPU. Probe matmul cost scales roughly linearly with
  M_stored; largest single M_stored ≈ 4-5 min.

## What product decision this enables

- `CAPSWEEP_ROBUST` → cap_map row "GDPR-grade surgical erase under
  orthogonal keys" moves 🟢 → ✅ with envelope up to M_stored = 3200
  at N = 4096. Concrete operating range for the product claim.
- `CAPSWEEP_BREAKS_AT_<M>` → cap_map row stays 🟢 with explicit
  envelope: "Mirage-protected up to M_stored=<X>, breaks above."
- `CAPSWEEP_BREAKS_IMMEDIATELY` → re-audit v1 test setup; would
  contradict the v1 result.
