# Queue dispatch: cumulant_dichotomy_haar_vs_kerdock_v1

**Date:** 2026-05-23
**Author:** exp_dev
**Routing schema:** Schema B (markdown table) -- per Strategy directive to verify
the dispatch.py parser fix on the table schema.

## Shipment

This experiment ships the cumulant-dichotomy anchor from the cross-domain Research
probe `notes/research_cross_domain_probe_2026-05-23.md`. Top angle: ETH-free-probability
framing (Pappalardi-Foini-Kurchan; Jindal-Hosur JHEP09(2024)066) reframes BBMD as
"partially-thermalized algebraic-codebook regime." This is the cheapest disambiguator
for that framing.

Tier B per three-tier policy (non-GPU + 30-60 min wallclock; NOT a quick scoping
probe). Queue: `remote_cpu_queue` (marsh@home, "desktop"). NOTE: per
[[project-cpu-resource-underutilized]] / [[project-runner-race]], the remote CPU
runner may need a freshness check before this clears.

## Smoke gate

PASSED locally at N=1024, 2 seeds, both families. Verdict:
`CUMULANT_DICHOTOMY_HOLDS`. Haar classical kappa_3..kappa_6 = {+0.000, -0.006,
+0.003, +0.000} (all < 0.1). Kerdock kappa_4 = -0.935, kappa_6 = +4.94.
Excess-kurtosis magnitude ratio Kerdock/Haar = 255x. The dichotomy already shows
at N=1024 -- N=4096 will tighten it.

## Queue table

| queue            | name                                            | script                                                            | prereg                                                            | timeout(s) |
|------------------|-------------------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cumulant_dichotomy_haar_vs_kerdock_v1    | experiments/exp_wave14_cumulant_dichotomy_haar_vs_kerdock_v1.py   | preregs/2026-05-23_wave14_cumulant_dichotomy_haar_vs_kerdock_v1.md| 5400       |

## Verdict labels and what they mean

  - `CUMULANT_DICHOTOMY_HOLDS` -- ETH framing survives; BBMD reframed.
  - `CUMULANT_DICHOTOMY_HAAR_FAILS` -- asymptotic-freeness at N=4096 fails;
    need much larger N; weakens "Haar = fully thermalized" claim.
  - `CUMULANT_DICHOTOMY_KERDOCK_FAILS` -- Kerdock's kappa_n divergence not
    actually meaningful; prior v164a finding called into question.
  - `CUMULANT_DICHOTOMY_INCONCLUSIVE` -- both arms or discriminator failing.

## ETA

30-60 min wallclock at N=4096, 10 seeds, 2 families. Dominant cost is the
M x M Gram-matrix triu extraction at M = 4N = 16384 (~ 268M off-diagonal entries
per seed; the entry-vector is O(N^2) memory at ~ 2GB float64, fine on the
remote desktop). The Kerdock builder is O(M*N) bit-ops, sub-second at this N.
