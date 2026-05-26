# exp_dev -> queue: wave14_free_cumulants_kerdock_v1

**Date filed**: 2026-05-23 ~18:40
**Owner**: exp_dev sonnet sub-agent
**Triggering event**: AMP_SE_DIVERGES FULL (~18:13) — Kerdock outside AMP universality class
**Field-advisor**: F4 Voiculescu free cumulants (tier-1 free-probability, anchor_yield=100%, score=5.5)

queue=overnight_queue name=wave14_free_cumulants_kerdock_v1 script=experiments/exp_wave14_free_cumulants_kerdock_v1.py prereg=preregs/2026-05-23_wave14_free_cumulants_kerdock_v1.md timeout=3600

## One-line hypothesis

Kerdock 4-coset codebook has higher Voiculescu free cumulants kappa_n (n>=2)
that deviate >20% from Marchenko-Pastur baseline c=M/N, providing the
formal free-probabilistic mechanism for the AMP_SE_DIVERGES finding.

## Smoke result

Smoke at N=1024 (alpha={0.5, 1.0}, n_seeds=2): FREE_CUMULANTS_DIVERGE,
2/2 cells exceed 20% kappa_n deviation. Early-signal smoke strongly
favors DIVERGE; FULL N=4096 with 5 alpha cells will confirm.

## Routing rationale

Rule 0 + Rule 1 (compute-heavy SVD across 5 alpha x 5 seed = 25 cells at
N=4096, GPU machine has faster CPU + persistent runner). No CUDA in code
but routed to GPU machine for runtime benefit.
