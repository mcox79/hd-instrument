# exp_dev Decisions 2026-06-02

## Batch: Overnight Cycle 1 completion (post-compaction)

**Context:** Context compaction occurred mid-cycle. Resuming from the 9-script pre-smoke stage.
Verified smoke on all 10 candidates. 7 shipped, 3 dropped.

---

## SHIPPED (7/10)

1. **spectral_zstat_v2** (HARD_PASS smoke 26s) -- remote_cpu_queue timeout=900s
   - Fix from v1: sequential O(k*N^2) outer product loop replaced with vectorized dups.T @ dups / N
   - Spectral Z-stat is now the correct architecture

2. **kappa3_hutchinson_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=1800s
   - Q-C3: kappa_3 free-cumulant fingerprint for Hopfield vs GOE discrimination
   - min_sigma_sep=12.5 at smoke scale; theory_ratio=12.59 (calibration probe, HP_MATCH=20x)

3. **implicit_gram_solve_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=1800s
   - Q-A4: Gram-solve retrieval equivalent to Hopfield, memory ratio 0.00015 vs 1.0

4. **frobenius_symdiff_verify_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=600s
   - Corrected formula: ||W_A-W_B||^2 ~ |symdiff| (not /N); empirical rel_err=0.001

5. **effective_rank_sweep_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=600s
   - r_eff = exp(H(sigma)) monotone in M: frac_monotone=1.00, mean_r_eff/M=0.966

6. **conformal_reject_option_v1** (HARD_PASS smoke <5s) -- remote_cpu_queue timeout=600s
   - Q24: split CP coverage guarantee. Fixed upper->lower quantile direction. frac_pass=1.00

7. **heteroassoc_chain_depth3_v1** (HARD_PASS smoke 102s) -- remote_cpu_queue timeout=3600s
   - Q-B1: depth-3 heteroassociative chain + cert deletion. d3=0.997, d2_after=-0.008

---

## DROPPED (3/10) -- routed to Strategy for redesign

### pp31c_knee_v3_widegrid -- INSTRUMENTATION_SUSPECT
- Root cause: precision-vs-coverage curve is CONSTANT (all precisions identical) because
  system is far below capacity (M=50, N=8192). No precision-coverage tradeoff exists here.
  Score distribution tightly clustered at 0.70 (1-2*0.15), and ALL queries retrieve
  correctly regardless of tau threshold.
- Signal: PP-31c requires a near-capacity operating regime to create a detectable knee.
  At M=50/N=8192 = 0.006 load, Hopfield is perfect at all tau values.
- Strategy routing: redesign needs near-capacity M or heterogeneous noise levels.

### tau_mem_decay_sweep_v1 -- HARD_FAIL at smoke
- Root cause: tau_emp / tau_theory = 30x (30x off from prediction).
  Formula tau_mem = N/(2*lambda) assumed single-pattern isolation, but our simulation
  has M_eff = lambda/gamma = 10 concurrent background patterns creating interference.
  The SDE model does not match the simulation setup.
- Signal: theory is wrong for the simulated regime.
- Strategy routing: need proper multi-pattern SDE theory or isolate single-pattern decay.

### signed_am_b_pattern_full_v1 -- HARD_FAIL at smoke
- Root cause: repulsion_rate=0.000 at M_A=20, M_B=5, N=4096.
  B-patterns converge TO xi_B (cos_sim > 0.5 in all trials) rather than diverging.
  W_A (20 patterns) creates interference that prevents effective B-pattern repulsion.
  The W_A random field at xi_B location is larger than the W_B penalty.
- Signal: signed-AM repulsion requires M_A << N for B-patterns to be actual energy maxima.
- Strategy routing: test with M_A=1-3, M_B=1 (clean case) to confirm theory, then scale.

---

## PROT-021 NOTE
Stale local partials from earlier wrong-tau-grid runs contaminated pp31c smoke results.
PROT-021 checks N/M/run_mode but not custom fields like tau_min. Cleared manually.
Recommendation: add tau_min (and other config-discriminating fields) to PROT-021 check keys
in _seed_checkpoint.py, or add a per-experiment config_hash field.

---

Generated: 2026-06-02
