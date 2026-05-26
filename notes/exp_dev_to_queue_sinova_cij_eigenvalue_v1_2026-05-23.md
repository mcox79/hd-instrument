# Exp Dev -> Queue: wave14_sinova_cij_eigenvalue_v1

**Filed**: 2026-05-23
**Routing trigger**: research_meta_map_and_adjacencies_2026-05-23.md Drill 1 (H1) -- top next-drill
  P_deflated=0.50; flagged as "priority-1 probe; not yet fired at FULL"
**Axis**: Substrate-physics -- Sinova C_ij extensive-eigenvalue RSB discriminator

---

## Queue entry

```
queue=local_cpu_queue name=wave14_sinova_cij_eigenvalue_v1 script=experiments/exp_wave14_sinova_cij_eigenvalue_v1.py prereg=preregs/2026-05-23_wave14_sinova_cij_eigenvalue_v1.md timeout=3600
```

**Queue rationale**: pure CPU (numpy linear algebra only; no torch.cuda); expected wall time
~30-60 min (5 K values x 5 seeds x Glauber MC + N=4096 eigvalsh); all data generated
in-script (no remote data dependency) -> local_cpu_queue.

---

## Smoke gate

**Status**: PASSED

Self-test: 6/6 cases PASS.

Smoke at N=256, K_grid=[10, 25], n_seeds=2, n_sample=20:
- K=10 (alpha=0.039): n_extensive_C=0, n_extensive_W=0, excess=0,
  top_C_scaled=[0.0069, 0.0072, 0.0076, 0.0093, 0.0104]
- K=25 (alpha=0.098): n_extensive_C=0, n_extensive_W=0, excess=0,
  top_C_scaled=[0.0161, 0.0196, 0.0232, 0.0385, 0.0675]
- VERDICT: SINOVA_RS_PARAMAGNET
- metrics.json: data/exp_wave14_sinova_cij_eigenvalue_v1_smoke/metrics.json
- Elapsed: <1s

Smoke result is consistent with RS phase at sub-capacity alpha (10/256=0.039, 25/256=0.098).
Top scaled eigvals well below 0.1 threshold at smoke N=256 -- expected; N=4096 at FULL
gives much sharper separation.

---

## FULL config

- N=4096
- K_grid=[50, 100, 200, 400, 800] (alpha range 0.012 to 0.195)
- beta=2.0
- n_seeds=5 independent MC chains per K
- n_burn=100 sweeps, n_sample=200 configs, sample_interval=20
- threshold_rel=0.1 (lambda/N > 0.1 = extensive)
- Peak memory: ~205 MB CPU (W=67 MB + C_avg_accum=134 MB + samples)
- Timeout: 3600s (conservative upper bound for all 5 K values)

---

## Expected verdicts

- SINOVA_RS_PARAMAGNET (P=0.55): consistent with 4-anchor RS certification
- SINOVA_RSB_DETECTED (P=0.25): would contradict RS-cert; require re-examination
- SINOVA_INCONCLUSIVE (P=0.20): boundary excess==1 at N=4096

---

## Coordination notes

- Pipeline invariant: local_cpu_queue was empty (all prior entries completed)
- No PROT-004/006 needed (not a cap_map closure experiment)
- PROT-001: exp_dev_decisions_2026-05-23.md entry will be appended
- No dependency on remote data or prior experiment results
- Substrate-product axis: RS-cert cross-family validation; directly extends
  observability_suite_v1 (load-bearing cap_map row) with second independent family
