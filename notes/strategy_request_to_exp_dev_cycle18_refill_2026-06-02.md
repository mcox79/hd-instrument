# exp_dev queue refill: Cycle 18 post-verdict pipeline-pacing

**Filed:** 2026-06-02
**Trigger:** Cycle 18 verdict batch (v348->v349) complete; both queues empty; pause-flag ABSENT; pipeline-pacing queue-depth=0 refill required.
**Priority:** IMMEDIATE (queues empty)

## Context

cap_map v349. HONEST 518. LVH 207. Portfolio 32+75.

Cycle 18 batch results:
- 3 HP: Q-B1 d=100 N=8192 (flat-profile complete); PP-48 d=19 N=16384 (3rd cross-N vertex); PP-55 VSA-bind-over-SKAH-M (NEW ROW founded, single N=4096)
- 1 HF: composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096 (Arrhenius constant-M formula refuted; I-20 open)
- 3 MIDDLE: kappa3_noise_robustness (Wave-2 over-conservative; I-19 open); hebbian_vs_gd_identity (PP-52 corroboration; HP3 FLOPs gate missed); ck_aging_mu_alpha_invariance (partial 3rd CK sig; not unanimous)

## Dispatch candidates (prioritized by cheapest + open rescue paths)

**GPU queue (overnight_queue):**

1. **PP-48 depth-23 cross-N N=8192** -- BAND-LIFT gate to 0.80-0.95. d=23 confirmed at N=4096 (v348). Cross-N N=8192 is the next vertex. Anchor family: pp48_nkt_cross_n_depth23_v1_n8192.

2. **kappa3 extended sigma_g sweep to sigma_g=0.50** -- R2 rescue for I-19 (Wave-2 over-conservative). Find actual sigma_g_critical empirically. Extends existing kappa3_noise_robustness_sigma_g_sweep experiment to sigma_g grid [0.30, 0.35, 0.40, 0.45, 0.50]. GPU sweep at N=4096.

3. **PP-55 cross-N N=8192** -- BAND-LIFT gate for VSA-bind-over-SKAH-M. N=4096 founding (v349); N=8192 is the next production-N vertex. Anchor family: vsa_binding_over_static_skahm_class_v1_n8192.

**CPU queue (remote_cpu_queue):**

4. **composition_ceiling I-20 diagnostic rerun** -- R2 rescue. Verify depth_fid={} empty = genuine flat across all k vs script exit before computing first cell. Add diagnostic prints at each k iteration. CPU ~30min at N=4096. Anchor: composition_ceiling_k_c_alpha_constant_m_per_stage_diagnostic_v1_n4096.

5. **CK-aging mu-alpha invariance N=8192 rescale** -- R2 rescue for ck_aging MIDDLE. hp_unanimous=False at N=4096 (seed7 delta=0.057). N=8192 expected to reduce per-seed variance. CPU ~2h. Anchor: ck_aging_mu_alpha_invariance_matched_tc_v1_n8192.

6. **Q-A3 L=16 N=4096** -- L-ceiling chase. L=15 all EXACT-1.0 v348; L-ceiling not reached; cheap CPU algebraic. Anchor: q_a3_l16_cross_layer_composition_v1_n4096.

## Contract

- Design scripts + preregs per role contract
- Pre-reg HARD-PASS/MIDDLE/HARD-FAIL bands per envelope-fail-bands feedback
- Smoke gate before FULL ship
- ASCII-only in print()/verdict_msg (PROT feedback)
- PROT-018 _n<N> suffix binding
- PROT-022 formula self-tests
- No inline experiment design from orchestrator -- agent decides anchor names, sweep grids, thresholds
- Post-ship REMOTE VERIFY (queue presence confirmation)
- timeout formula: 1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)
