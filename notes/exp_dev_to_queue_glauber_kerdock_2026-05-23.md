# exp_dev -> queue: wave14_glauber_kerdock_v1

**Date filed**: 2026-05-23 ~18:43
**Owner**: exp_dev sonnet sub-agent
**Triggering event**: pipeline-pacing queue fill (CPU runner revived; queue depth invariant >=1)
**Field-advisor**: D1 Glauber dynamics on substrate codeword space (tier-1 semiconductor, anchor_yield=100%, score=5.0)

queue=remote_cpu_queue name=wave14_glauber_kerdock_v1 script=experiments/exp_wave14_glauber_kerdock_v1.py prereg=preregs/2026-05-23_wave14_glauber_kerdock_v1.md timeout=3600

## One-line hypothesis

Synchronous heat-bath Glauber dynamics on the Kerdock-Hebbian W matrix
shows bimodal stationary P(q) at low temperature (beta >= 4), with peaks
at q~1 retrieval and q~0 paramagnetic modes — substrate-novel dynamical
observability complementary to the spectral free-cumulants probe.

## Smoke result

Smoke at N=1024 (alpha=0.5, beta in {1, 4}, n_seeds=2): GLAUBER_INCONCLUSIVE
(coarse 50-sample histogram + high-alpha regime). abs_mean_q rises with
beta (good — system trends toward target at lower T). FULL with alpha=0.25
sub-critical cell and 400-sample chains should resolve.

## Note on dynamics

Switched from sequential single-spin Glauber to synchronous heat-bath
(Peretto 1984; Hertz-Krogh-Palmer 1991 Ch. 4) for vectorization. Equilibrium
phase structure preserved for symmetric diag-zero W; may exhibit period-2
cycles at zero T (harmless for stationary statistics). Documented in prereg.

## Routing rationale

Rule 2: pure numpy, >5 min, benefits from remote machine's persistent CPU
runner. GPU reserved for free-cumulants experiment.

## Runner revival

Remote CPU runner schtasks status was "Ready" (not running) at 18:32.
Revived via `ssh marsh@home 'schtasks /Run /TN hd_cpu_runner_0'` at 18:33;
schtasks returned SUCCESS. The runner should pick this entry up.
