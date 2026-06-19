# Anticipatory Pre-builds Index -- 2026-05-27

All scripts are SMOKE-TESTED and QUEUE-READY. DO NOT queue_add until the trigger condition fires.

---

## Pre-build 1: anchor_novel_phase_battery_v2_lit_threads -- 3-thread discrimination

**Script:** `experiments/exp_anchor_novel_phase_battery_v2_lit_threads.py`
**Prereg:** `preregs/2026-05-27_anchor_novel_phase_battery_v2_lit_threads.md`
**Queue:** overnight_queue (GPU; N=2048; ~1.5-2h)
**Trigger (PATH A -- DOCUMENTED_BUT_UNTESTED):** v1 returns DOCUMENTED_BUT_UNTESTED (>= 5/6 cells match documented column)
**What it tests:** Which of 3 lit threads best matches the substrate?
  - Arm1: cooling-rate independence (Thread A: Non-reciprocal Hopfield)
  - Arm2: alpha_c shift structured vs random (Thread B: Spatial-correlated DAM)
  - Arm3: singular-value staircase alignment (Thread C: Saddle-hierarchy DAM)
**Expected bands:** THREAD_A_PARTIAL or THREAD_A_DOMINANT (substrate shows rate-independent hysteresis per v1 data)
**Smoke result:** PASS -- verdict THREAD_A_PARTIAL; selftest 5/5 OK

---

## Pre-build 2: anchor_novel_class_declaration_probe_v1 -- 5-step SKAH-M characterization

**Script:** `experiments/exp_anchor_novel_class_declaration_probe_v1.py`
**Prereg:** `preregs/2026-05-27_anchor_novel_class_declaration_probe_v1.md`
**Queue:** overnight_queue (GPU; N=2048 N-sweep; ~1.5-2h)
**Trigger (PATH B -- NOVEL or HARD_FAIL on v1):**
  v1 returns NOVEL (>= 4/6 novel cells + anomaly) OR HARD_FAIL (< 3/6 documented)
  ALSO OVERLAPS with rate_dep_hysteresis HARD_FAIL (geometric frustration rejected)
**What it tests:** 5-step novel-class methodology (symmetry, order parameter, Goldstone,
  free-energy wells, response susceptibility). Determines if SKAH-M class declaration warranted.
**Expected bands:** DOCUMENTED_CONFIRMED (S2 CONVERGENT is most likely per prior data)
**Smoke result:** PASS -- verdict DOCUMENTED_CONFIRMED; selftest 5/5 OK; fixed rand_like->rand() bug

---

## Pre-build 3: wave14_moe_cosine_router_v2_k_stress -- K=32/64/128 stress test

**Script:** `experiments/exp_wave14_moe_cosine_router_v2_k_stress.py`
**Prereg:** `preregs/2026-05-27_wave14_moe_cosine_router_v2_k_stress.md`
**Queue:** overnight_queue (GPU; M_total up to 102400 at K=128)
**Trigger (HARD_PASS on v1):** v1 returns COSINE_ROUTER_HARD_PASS
  (routing_entropy@K=16 < 2.0b AND retention delta >= -0.005)
**What it tests:** Does cosine-dot routing extend K-ceiling all the way to K=128?
  Tests token-choice, expert-choice, and Hebbian-anchor variants.
**Expected bands:** COSINE_ROUTER_K_STRESS_MIDDLE or HARD_PASS at N=4096
**Smoke result:** PASS -- verdict MIDDLE at smoke scale (K smoke range: 8/16/32 at N=512);
  selftest 5/5 OK

---

## Pre-build 4: wave14_moe_remoe_relu_router_v1 -- ReLU router rescue

**Script:** `experiments/exp_wave14_moe_remoe_relu_router_v1.py`
**Prereg:** `preregs/2026-05-27_wave14_moe_remoe_relu_router_v1.md`
**Queue:** remote_cpu_queue (CPU; ~2000-4000s)
**Trigger (HARD_FAIL on cosine_router_v1):** v1 returns COSINE_ROUTER_HARD_FAIL
  (entropy > 3.0b or retention < K=4 - 0.015)
**What it tests:** ReMoE-style ReLU gating on cosine scores. Dynamic K_eff ~K/2 from
  bipolar symmetry. 3 variants: ReLU-cosine, Threshold-cosine, Top-2 cosine.
**Expected bands:** REMOE_HARD_FAIL expected (shared-W design means retention is constant;
  real value is entropy characterization; K_eff ~ K/2 at N=4096 is the hypothesis)
**Smoke result:** PASS -- selftest 4/4 OK (fixed assert for threshold k_eff=0 at tiny N);
  verdict HARD_FAIL at smoke is expected because shared W + small N

---

## Pre-build 5: wave14_corpus_N_scaling_tau_unblock_v1 -- tau-limit unblock probe

**Script:** `experiments/exp_wave14_corpus_N_scaling_tau_unblock_v1.py`
**Prereg:** `preregs/2026-05-27_wave14_corpus_N_scaling_tau_unblock_v1.md`
**Queue:** overnight_queue (GPU; N=16384 requires GPU; ~1-2h)
**Trigger (HARD_FAIL on corpus_size_scaling_v1):** v1 returns CORPUS_SCALING_HARD_FAIL
  (tau-limit binding at N=1024; bpc non-monotone or top_edge < 1.5)
**What it tests:** N-corpus coupling. Does increasing N to 16384 unblock the tau-limit
  at fixed 500KB corpus? Measures bpc proxy + spectral top-edge across N in {1024, 4096, 16384}.
**Expected bands:** TAU_UNBLOCK_HARD_PASS or MIDDLE
**Smoke result:** PASS -- verdict TAU_UNBLOCK_HARD_PASS at smoke scale; selftest 4/4 OK

---

## Pre-build 6: wave14_spin_ice_frustration_comparison_v1 -- spin-ice precedent check

**Script:** `experiments/exp_wave14_spin_ice_frustration_comparison_v1.py`
**Prereg:** `preregs/2026-05-27_wave14_spin_ice_frustration_comparison_v1.md`
**Queue:** remote_cpu_queue (CPU; extended epochs + M-scan; ~1-2h)
**Trigger (RATE_DEPENDENT_KINETIC on rate_dep_hysteresis_v1):** v1 confirms geometric frustration
  (Pearson r < -0.50 AND gap@epochs=32 < 50% of gap@epochs=1)
**What it tests:** 4-signature comparison: SIG1 (ice rule), SIG2 (correlation decay exponent),
  SIG3 (non-monotone vs monotone cooling gap), SIG4 (Kasteleyn-like load threshold).
  Does substrate match documented Ising/dipolar spin-ice or is it qualitatively distinct?
**Expected bands:** FRUSTRATED_NOVEL (most likely given structured-codebook geometry)
**Smoke result:** PASS -- verdict FRUSTRATED_NOVEL at smoke; selftest 4/4 OK

---

## Pre-build 7: tda_moe_w_crossvalidation_v1 -- TDA offline audit reliability

**Script:** `experiments/exp_tda_moe_w_crossvalidation_v1.py`
**Prereg:** `preregs/2026-05-27_tda_moe_w_crossvalidation_v1.md`
**Queue:** remote_cpu_queue (CPU; ~15-30 min)
**Trigger (HARD_PASS on tda_reanalysis_5probe_v1):** 5probe returns TDA_HARD_PASS
  (TDA-C agree >= 4/5 cases at full scale)
**What it tests:** Can TDA-C (b_0-plateau width SHIFT/PARTITION diagnostic) be applied
  as an offline audit tool to existing W matrices from production pipeline experiments?
  Cross-validates against 5 reference experiments; also measures TDA-B vs top-edge correlation.
**Expected bands:** TDA_CROSSVAL_HARD_FAIL (b_0 plateau is sensitive to N and subsampling;
  offline reliability not guaranteed); TDA_CROSSVAL_MIDDLE plausible
**Smoke result:** PASS -- selftest 4/4 OK; verdict HARD_FAIL at smoke is expected
  (only 2 smoke cases; agree_rate=0.50 is below 4/5 threshold)

---

## Overlap notes

- Pre-builds 1 and 2 are MUTUALLY EXCLUSIVE (both triggered by v1 outcome but on different branches).
- Pre-build 6 shares the "novel frustration" framing with Pre-build 2 -- if both fire,
  run pre-build 6 first (cheaper); its result informs pre-build 2's SKAH-M framing.

---

## Summary table

| Pre-build | Script | Trigger anchor | Queue | Smoke |
|---|---|---|---|---|
| v2_lit_threads | exp_anchor_novel_phase_battery_v2_lit_threads.py | SKAH-M HARD_PASS | overnight | PASS |
| novel_class_v1 | exp_anchor_novel_class_declaration_probe_v1.py | SKAH-M HARD_FAIL / NOVEL | overnight | PASS |
| cosine_v2_k_stress | exp_wave14_moe_cosine_router_v2_k_stress.py | cosine_router HARD_PASS | overnight | PASS |
| remoe_relu_v1 | exp_wave14_moe_remoe_relu_router_v1.py | cosine_router HARD_FAIL | remote_cpu | PASS |
| tau_unblock_v1 | exp_wave14_corpus_N_scaling_tau_unblock_v1.py | corpus HARD_FAIL | overnight | PASS |
| spin_ice_v1 | exp_wave14_spin_ice_frustration_comparison_v1.py | rate_dep KINETIC | remote_cpu | PASS |
| tda_crossval_v1 | exp_tda_moe_w_crossvalidation_v1.py | TDA 5probe HARD_PASS | remote_cpu | PASS |
