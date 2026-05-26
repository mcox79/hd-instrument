# Exp Dev -> Queue: Bet Z.5 absorbing-diffusion ensemble smoother vs VAMP-on-chain equivalence

**Filed**: 2026-05-23
**Trigger**: audit notes/research_comprehensive_audit_2026-05-23.md section (b) Rank 1 + section (c) row 1; strategy routing strategy_request_to_exp_dev_post_v158_pipeline_2026-05-23.md Pick 3; 13-cap_map-versions stale since v144.

---

## Queue entry

```
queue=local_cpu_queue name=wave14_betZ5_equiv_check_v1 script=experiments/exp_wave14_betZ5_equiv_check_v1.py prereg=preregs/2026-05-23_wave14_betZ5_equiv_check_v1.md timeout=3600
```

---

## Axis probed

Bet Z.5 structural equivalence vs VAMP-on-chain. Two-way decisive:
- BETZ5_EQUIVALENT_TO_VAMP (r >= 0.99): close candidate row; VAMP-on-chain already IS the Z.5 algorithm.
- BETZ5_STRICTLY_STRONGER (r < 0.99 AND var_cert > 0.01): confirm substrate-novel primitive; per-codeword
  posterior variance certificate that deterministic VAMP cannot produce.
- BETZ5_INCONCLUSIVE: degenerate output; redesign needed.

## Algorithm description

VAMP-on-chain: forward-backward EP, single deterministic pass, no variance estimate.
Absorbing-diffusion ensemble smoother: K_ensemble=50 independent noisy forward passes (nl=3.0
Gaussian noise on start entity, absorbed to bipolar via sign-quantize at each hop); ensemble
posterior mean as readout; per-codeword std as variance certificate.

Calibration note: nl <= 1.0 collapses all ensemble members to the same absorbing state (trivial
r=1.0, var_cert=0). nl=3.0 is the regime where ~8-15/20 ensemble members take distinct forward
paths at N=512 (verified). FULL N=4096 depth=10 3-seed 40-trial.

## Smoke result

Smoke (N=512, depth=3, 5 trials, 1 seed, nl=3.0):
- VERDICT: BETZ5_STRICTLY_STRONGER
- pearson_r=0.7762, var_cert=22.17, z5_acc=0.200, vamp_acc=0.000
- Self-test: 7/7 passed
- metrics.json written to data/exp_wave14_betZ5_equiv_check_v1_smoke/

The smoke-scale result shows distributions differ and ensemble variance is non-trivial.
FULL run at N=4096 will give the definitive characterisation at full signal-to-noise.

## Expected wall time

~20-40 min CPU (N=4096, K_ent=200, 3 seeds, 40 trials, K_ensemble=50, no GPU).

## Peak memory

< 50 MB CPU. Dominant: ensemble stack (K_ens=50 x K_ent=200 float32) = ~40 KB.

## Pipeline depth after filing

- local_cpu_queue: 2 queued + 1 running (amp_se_kerdock_v1 + sinova_cij_eigenvalue_v1 + betZ5_equiv_check_v1)
- Pipeline invariant: SATISFIED (depth >= 1).

## Substrate-product impact

If BETZ5_STRICTLY_STRONGER at FULL: closes audit Rank-1 action AND confirms substrate gains a third
readout primitive (beyond argmax + VAMP): per-codeword posterior variance, which is the distinguishing
feature of absorbing-diffusion ensemble smoothers vs deterministic EP. Justifies the 4-6 hr GPU impl
originally estimated at v144.

If BETZ5_EQUIVALENT_TO_VAMP at FULL: closes audit action cleanly; the candidate row is retired;
VAMP-on-chain (cycle 127, acc_50hop=1.000) is already the implementation; no additional work needed.
