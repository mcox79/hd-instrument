# exp_dev routing note: urgent_refill_v224 -- 8 anchors

**Filed:** 2026-05-27
**Trigger:** 8-verdict batch (v224 / commit 8bad9ae) -- mostly HARD_FAIL/AMBIGUOUS;
both GPU and CPU runners idle; refill needed.

## Shipment record

```
queue=overnight_queue name=wave14_1rsb_rate_dep_hysteresis_v2 script=experiments/exp_wave14_1rsb_rate_dep_hysteresis_v2.py prereg=preregs/2026-05-27_wave14_1rsb_rate_dep_hysteresis_v2.md timeout=14400
queue=overnight_queue name=wave14_corpus_size_scaling_v2 script=experiments/exp_wave14_corpus_size_scaling_v2.py prereg=preregs/2026-05-27_wave14_corpus_size_scaling_v2.md timeout=14400
queue=overnight_queue name=wave14_beti_depth_polylog_v4 script=experiments/exp_wave14_beti_depth_polylog_v4.py prereg=preregs/2026-05-27_wave14_beti_depth_polylog_v4.md timeout=21600
queue=remote_cpu_queue name=wave14_moe_remoe_relu_router_v1 script=experiments/exp_wave14_moe_remoe_relu_router_v1.py prereg=preregs/2026-05-27_wave14_moe_remoe_relu_router_v1.md timeout=5400
queue=remote_cpu_queue name=wave14_moe_hebbian_anchor_router_v1 script=experiments/exp_wave14_moe_hebbian_anchor_router_v1.py prereg=preregs/2026-05-27_wave14_moe_hebbian_anchor_router_v1.md timeout=5400
queue=remote_cpu_queue name=wave14_ortho_pme_ising_v2 script=experiments/exp_wave14_ortho_pme_ising_v2.py prereg=preregs/2026-05-27_wave14_ortho_pme_ising_v2.md timeout=3600
queue=remote_cpu_queue name=wave14_ortho_blahut_arimoto_v2 script=experiments/exp_wave14_ortho_blahut_arimoto_v2.py prereg=preregs/2026-05-27_wave14_ortho_blahut_arimoto_v2.md timeout=1800
queue=remote_cpu_queue name=wave14_ortho_jarzynski_crooks_v1 script=experiments/exp_wave14_ortho_jarzynski_crooks_v1.py prereg=preregs/2026-05-27_wave14_ortho_jarzynski_crooks_v1.md timeout=1800
```

## Justification per anchor

1. **wave14_1rsb_rate_dep_hysteresis_v2** (GPU): v1 AMBIGUOUS sign-flip was N=256 saturation artifact.
   N=1024 FULL + tighter M sweep [500-12000] resolves whether gap sign-flip is real or artifact.

2. **wave14_corpus_size_scaling_v2** (GPU): v1 HARD_FAIL was smoke-regime N=256 mismatch.
   N=1024 + 10x larger corpus sizes [100KB/1MB/10MB] re-tests path-(b) feasibility.

3. **wave14_beti_depth_polylog_v4** (GPU): v3 SMOKE_REGIME_MISMATCH fixed by smoke N=[1024,2048].
   D_SWEEP_SMOKE now includes d=30,40 to bracket d_c_pred(N=1024, K=10)~26.6.

4. **wave14_moe_remoe_relu_router_v1** (CPU): Pre-build triggered by cosine_router HARD_FAIL.
   ReMoE-style ReLU gating; K_eff ~ K/2 hypothesis.

5. **wave14_moe_hebbian_anchor_router_v1** (CPU): New design -- Hebbian-learned anchors after
   both LSH (K_perarm) and random cosine (cosine_router) failed K-scaling. Substrate-native
   Phase 1 + Phase 2 anchor refinement.

6. **wave14_ortho_pme_ising_v2** (CPU): v1 MIDDLE_BAND due to bad capacity formula. v2 fixes
   both the Z-based and RS alpha_c estimators. Smoke HARD_PASS (75% seeds in factor-2 band).

7. **wave14_ortho_blahut_arimoto_v2** (CPU): v1 label-vs-honest mismatch (queue=failed, data=HARD_PASS).
   v2 clean re-ship with explicit sys.exit(0) + extended N_tasks sweep.

8. **wave14_ortho_jarzynski_crooks_v1** (CPU): Orthogonal probe. Jarzynski equality P=0.45
   (highest undrilled candidate). Free-energy perturbation for substrate write operations.
   Cheaper Cap 1 capacity estimator hypothesis.

## Pre-build disposition

- remoe_relu_v1: SHIPPED (cosine HARD_FAIL trigger confirmed)
- cosine_v2_k_stress: DEAD (cosine HARD_FAIL)
- tau_unblock_v1: HOLD (corpus HARD_FAIL was smoke-regime; re-test via corpus_v2 first)
- spin_ice_v1: HOLD (rate_dep AMBIGUOUS; resolve via hysteresis_v2 first)
- tda_crossval_v1: HOLD (TDA INCONCLUSIVE; need FULL verdict)
- novel_class_v1, v2_lit_threads: HOLD (waiting for SKAH-M battery)

## Bridge-verified

8/8 confirmed in remote queues (overnight_queue: 3, remote_cpu_queue: 5).
GPU=3 pending CPU=5 pending post-ship.
