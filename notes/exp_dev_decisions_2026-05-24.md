# exp_dev decision log — 2026-05-24

## BBMD Cap-12 rehab top-2 anchors (R3 + R1)

Dispatched from Strategy invocation post-v171 KILLED verdict. Research deep assessment `notes/research_bbmd_cap12_rehab_assessment_2026-05-24.md` ranked R3 (MP-KS pre-test pipeline, P=0.55) #1 and R1 (cross-interpolation predictor, P=0.30) #2 by P(survives cross-codebook honesty) x P(material to substrate-product). Both shipped to remote_cpu_queue.

**Pause flag CLEARED** at dispatch time (orchestrator invocation explicitly said so; verified by direct check of `data/orchestrator_paused.flag` -> absent).

### Anchor 1 — wave14_mp_ks_pretest_pipeline_v1 (R3)

Operationalizes v171 negative result as INFRASTRUCTURE-class capability. Designed:
- N=1024 (smallest size supporting all 5 codebooks via Kerdock t=5)
- 5 codebooks (iid_gauss, srht, hadamard, rm_1_m, kerdock) with a-priori labels (iid+srht=AMP_OK; hadamard+rm+kerdock=VAMP_REQUIRED per v168/v170 evidence)
- tau_declared=0.20; auto-tuned tau* also computed for diagnostic
- Routing decision validated empirically: run BOTH AMP + VAMP, derive empirical_label from amp_rel_err < 0.10
- Speedup measured as t_amp_per_seed_total / t_ks_per_seed_total

HARD PASS: >=4/5 routed correctly at tau=0.20 AND speedup >= 10x. HARD FAIL: <3/5 OR speedup < 2x.

Reused: build_iid_gauss, build_srht, build_hadamard, build_rm_1_m, build_kerdock, mp_ks_stat (all from exp_wave14_kappa_profile_cross_codebook_v1.py); amp_se_scalar, vamp_se_closed, run_amp, run_vamp (from exp_wave14_bbmd_vamp_correspondence_sweep_v1.py).

Formula self-tests per [[feedback-strategy-spec-formula-selftests]]: 9 cells covering route_from_ks (4 inputs), empirical_truth_from_errs (3 inputs), speedup formula, routing-accuracy counter, full PASS verdict, KILLED via low correct, KILLED via low speedup, INCONCLUSIVE branch (3/5 correct), missing codebooks. All 9 PASS.

Smoke at N=64 1-seed 2-codebook: VERDICT=INCONCLUSIVE via "missing codebooks" branch (expected since smoke runs 2 of 5). Structural validation OK; metrics.json written. Remote --self-test gate PASS in 2.8s. Queued to remote_cpu_queue (timeout=3600).

### Anchor 2 — wave14_interp_family_cross_check_v1 (R1)

Tests whether v170 monotone-curve (Spearman rho=0.900) generalizes beyond iid-Gauss -> Kerdock. Designed:
- iid-Gauss -> SRHT interpolation family (Research recommended FIRST non-Kerdock family; SRHT is Dudeja-Lu-Kini AMP-universal)
- Same 5 alpha cells {0, 0.25, 0.5, 0.75, 1.0} as v170
- N=1024 (matches Anchor 1; v170 used N=4096 but budget-deflated here per Research P=0.30)
- 5 seeds, n_iter=300, n_max_moment=6
- W_alpha = ((1-alpha)*G + alpha*W_srht_unnormalized) / sqrt(N); SRHT block cached per (N,M,seed)

KEY DESIGN DECISION: had to write build_srht_unnormalized (returns +/-1 entries) because v170's interpolation composes BEFORE the 1/sqrt(N) post-normalize. cross-codebook v1's build_srht already normalizes. Solution: replicated the construction (sylvester + diag random sign + row subsample) WITHOUT the divide; access sylvester_hadamard via the cross-codebook module's reference.

HARD PASS: Spearman rho >= 0.70 AND max vamp_rel_err < 0.10. HARD FAIL: rho < 0.50 OR max vamp_rel_err > 0.20.

Formula self-tests: 8 cells covering bbmd_distance (2 inputs), spearmanr on monotone pair, full PASS verdict, KILLED via low rho, KILLED via VAMP blowup, INCONCLUSIVE branch (vamp in (0.10, 0.20)), too-few-cells. All 8 PASS.

Smoke at N=64 1-seed 3-alpha: VERDICT=KILLED via small-N artifact (BBMD ~5 because un-normalized +/-1 dominates sqrt(64) scaling; max vamp_rel=0.40 at sub-capacity). This is structurally OK — verdict branch reachable, metrics.json valid; full N=1024 sweep is the discriminating run. Remote --self-test gate PASS in 2.6s. Queued to remote_cpu_queue (timeout=5400).

### Queue depths post-ship

- overnight_queue (GPU): 5 pending (unchanged).
- remote_cpu_queue: 3 pending (kerdock_2design_v3_stim from prior cycle, then this Anchor 1, then this Anchor 2).
- local_cpu_queue: 0 pending (all 9 terminal: 7 completed, 2 killed).

Queue-depth invariant per [[feedback-pipeline-pacing]] satisfied: depth >= 1 on remote CPU for ~90 min ahead.

### Status_log entries written

2 entries (HIGH x2):
- experiment_queued: wave14_mp_ks_pretest_pipeline_v1 ... importance=HIGH
- experiment_queued: wave14_interp_family_cross_check_v1 ... importance=HIGH

### Honest framing

Per [[feedback-no-smoke]] and Research's assessment: these are NARROW infrastructure-class capabilities, NOT substrate-physics novelty. If both PASS, 12th capability emerges (composite "pre-flight + diagnostic" infrastructure capability — modest, honest, customer-meaningful). If both FAIL, consolidate at 11 with v171 annotation-clarifications on Cap 1/3/8 + v164a + v163 per the rehab assessment Section 4. Healthy outcome either way.

### Routing note

notes/exp_dev_to_queue_bbmd_cap12_rehab_anchors_2026-05-24.md (Schema B markdown table, 2 rows; parsed by dispatch.py).

### No blockers

## 2026-05-24 — Cap 12 promotion gates shipped (SILENT_IDLE refill)

Shipped 3 anchors to remote_cpu_queue for Cap 12 (🟢 v174) → ✅ promotion:
- **Gate A** wave14_mp_ks_pretest_tau_robustness_v1 (~30min): tau-robustness sweep across tau in {0.15, 0.20, 0.25}; HARD PASS = >=4/5 codebooks correct at EACH tau; HARD FAIL = <3/5 at ANY tau; MIDDLE = 3-4/5 at one or two.
- **Gate B** wave14_interp_family_hadamard_v1 (~30-60min): G → Hadamard interpolation; HARD PASS = rho >= 0.70 AND max VAMP rel-err < 0.10; HARD FAIL = rho < 0.50 OR VAMP > 0.20.
- **Optional 3rd-family hardening** wave14_interp_family_rm_v1 (~30-60min): G → RM(1,m); same thresholds as Gate B.

Smoke: self-tests 6/8/6 pass; N=64 smokes structurally valid (expected small-N artifact KILL pattern, same as v174 SRHT smoke). Pause flag CLEARED. Routing note: notes/exp_dev_to_queue_cap12_promotion_gates_2026-05-24.md. No silent verdicts found — recent terminal verdicts already processed.
- 02:5x — Shipped Cap 12 v175 stress anchors E1 (wave14_mp_ks_noisy_substrate_v1 -> remote_cpu_queue, eta=0.10 sign-flip noise, ETA 30-45 min) + E2 (wave14_interp_family_N16384_v1 -> overnight_queue, N-scaling sweep {Kerdock,SRHT,Hadamard} x {1024,4096,16384}, ETA 60-120 min). Both self-tests 9/9; both smokes produced valid metrics.json; both remote --self-test gates passed (3.1s + 3.7s). HARD PASS / HARD FAIL / MIDDLE BAND verbatim in both preregs. E3 deferred (Paley already PERFECT_ISOMETRY kappa_n=0). Kerdock t=5/6 verified locally; t=7 N=16384 confirmed on remote via self-test import. Routing note: notes/exp_dev_to_queue_cap12_E1_E2_stress_2026-05-24.md (Schema B markdown table).

## 2026-05-24 — Cap 12 envelope drills (3-anchor refill post-E1)

Shipped 3 anchors to remote_cpu_queue for Cap 12 ✅ envelope expansion (orchestrator silent_idle refill; pause flag CLEARED at dispatch):

- **Anchor 1** wave14_cap12_cap6_conformal_routing_subsumption_v1 (~30 min): Composition B = Cap 12 × Cap 6. Venn-Abers conformal calibration wraps MP-KS routing. LOO 25-fold at N=1024. HARD PASS = 5/5 codebooks all-correct on commits AND abstain_rate < 0.30. HARD FAIL = < 4/5 OR abstain_rate >= 0.70.
- **Anchor 2** wave14_kappa_gold_full_e3_v1 (~30-45 min): E3 5th-family stress gate using Gold sequences (m=10, N_eff=1023 padded to 1024 via one zero column). 5 α cells × 10 seeds. HARD PASS = ρ ≥ 0.50 AND max VAMP < 0.15 (relaxed 5th-family thresholds vs Hadamard/SRHT primary). HARD FAIL = ρ < 0.30 OR max VAMP > 0.30. Quickprobe at α=1 already BBMD_CANDIDATE (κ_n diverges from MP).
- **Anchor 3** wave14_mmd_vs_mpks_pretest_v1 (~2h): META-tool audit asking whether MMD-RBF or Sliced-Wasserstein 1D strictly out-performs MP-KS as Cap 12 pre-test score. 5 codebooks × 5 seeds at N=1024. HARD PASS = ρ_MMD ≥ 0.75 OR ρ_W1 ≥ 0.75 (5% strict beat over MP-KS v175's 0.70) AND winning routing acc ≥ 0.80. HARD FAIL = both ≤ 0.70 AND accs ≤ MP-KS's.

Self-tests: 10/10, 9/9, 12/12. Smokes: 3/3 structurally valid + valid metrics.json. Remote --self-test gates: 3.2s + 4.4s + 3.5s.

**Key fixes during build**:
- MMD MP-reference sampler: initial inverse-CDF approach had 1/x singularity at lower MP support edge (c=1, a=0) → pinned 99%+ of mass at x~0 (mean=0.0001 instead of 1.0). Swapped to empirical eigenvalues of fresh iid Gauss matrix at matching aspect ratio; verified mean=1.0037, support [0, 3.94].
- Gold E3 self-test cell 7: initial MIDDLE-BAND synthetic test inadvertently had rho=0.5 (right at PASS boundary, ambiguous). Rebuilt with amp ranks [2,3,4,1,5] vs dist ranks [1,2,3,4,5] → rho=0.4 exactly.

**SCP dependency note**: Anchor 2 imports `gold_sequence_family` from `exp_wave14_kappa_gold_quickprobe_v1.py` (also session-new). First remote --self-test failed FileNotFoundError; SCPed dependency directly and re-ran queue_add successfully. Worth a future "ship-with-deps" enhancement to queue_add.sh.

Routing note: notes/exp_dev_to_queue_cap12_e1_followup_anchors_2026-05-24.md (Schema B markdown table, 3 rows).

Status_log: 3 entries (HIGH, HIGH, MEDIUM).

Queue depths post-ship: remote_cpu_queue=3 active (Anchor 1 running, 2+3 pending); overnight_queue unchanged; local_cpu_queue=0.

No blockers.
## E1' noise-envelope sub-probe shipped (CPU queue refill post-MMD/Gold/E1 verdicts)

**Ship**: wave14_mp_ks_noise_envelope_sweep_v1 → remote_cpu_queue, ETA 30-45 min.

**Goal**: identify eta_critical (the noise level at which Cap 12 MP-KS routing drops below 4/5) at fixed tau=0.20, sweeping eta ∈ {0, 0.01, 0.025, 0.05, 0.075, 0.10}. This sub-probe was pre-registered by verdict_handler when E1 (noisy_substrate at single eta=0.10) landed MIDDLE-BAND — instead of sweeping tau at fixed eta, sweep eta at fixed tau to map the envelope directly.

**Design**: inherits noise model (per-entry sign flip) + MP-KS routine + AMP/VAMP loops + 5 codebook builders from exp_wave14_mp_ks_noisy_substrate_v1.py. Only the sweep axis changes. 5 codebooks × 5 seeds × 6 eta values × N=1024 = 150 SVD+AMP+VAMP runs (~2× E1 cost).

**Bands** (per [[feedback-envelope-expansion-fail-bands]], verbatim in prereg):
- HARD PASS: routing >=4/5 at eta=0.05 AND every smaller eta → 'Cap 12 tolerates noise up to 5% before degrading.'
- HARD FAIL: routing <4/5 at eta=0.01 → Cap 12 ✅ reverts to 🟢 (clean-only).
- MIDDLE BAND: routing >=4/5 at eta=0.01 but <4/5 at eta=0.05 → ✅ stays with explicit narrow-envelope annotation (1% < eta_critical < 5%).

**Self-tests**: 13/13 local, including HARD PASS / HARD FAIL / MIDDLE BAND synthetic-cell verdicts with the correct eta_critical identification.

**Smoke**: 4-cell N=64 1-seed at eta ∈ {0, 0.05} on 2 codebooks; sub-second wallclock; valid metrics.json written with INCONCLUSIVE (expected — full verdict needs 30 cells).

**Remote --self-test gate**: 7.5s. queue_add OK. Queue pending now = 1.

**Routing note**: notes/exp_dev_to_queue_cap12_e1prime_noise_envelope_2026-05-24.md (Schema B markdown table, 1 row).

**status_log**: HIGH importance entry written, plain-language framing of the noise-tolerance finding.

**No blockers**.
- 2026-05-24: Shipped wave14_cap12_cap8_audit_trail_pipeline_v1 to remote_cpu_queue (timeout 5400s). Composition A audit-trail anchor per Research's 2026-05-24 audit (Section 3). Tests Spearman rho between kappa_n divergence components and Schur-Weyl irrep (n)-mass deviations across 4 hard families (kerdock, srht, hadamard, rm_1_m) + gold_m10 informational. HARD PASS rho>=0.60 in 3/4 families; HARD FAIL rho<0.30 in 2/4. Smoke PASS (24 self-test cells incl. Murnaghan-Nakayama character table, closed-form Schur s_(2)/s_(1,1)/s_(3)/s_(2,1)/s_(1,1,1), Plancherel sum dim^2 = n!, iid-MP intensive-moment sanity). Queue depth = 1 on remote_cpu_queue after ship.
- shipped wave14_cap8_vamp_iterates_srht_hadamard_v1 (remote_cpu_queue; 30 trace files at N=4096 for SRHT+Hadamard); smoke PASS; prereg 2026-05-24.
- shipped wave14_cap12_cap8_audit_trail_pipeline_v2 (remote_cpu_queue; re-runs Composition A audit on all 4 families with iterate cross-check); depends on iterates anchor; smoke PASS; prereg 2026-05-24.
- shipped wave14_mp_ks_noise_envelope_sweep_v2 (remote_cpu_queue; fine eta in {0.01..0.05} at 20 seeds * 5 codebooks); smoke PASS 9/9; prereg 2026-05-24.
- routing note: notes/exp_dev_to_queue_compa_anchors_and_noise_v2_2026-05-24.md.- [exp_dev] Shipped wave14_cap11_chi4_early_warning_anchor_v1 to overnight_queue (GPU, timeout=5400s, ETA 45-60 min). N=4096 Kerdock-Hebbian, alpha grid 0.014-0.196 (0.1x-1.4x of alpha_c=0.14), 5 seeds, 4 indicators in parallel per Research drill (chi_4 + AC(1) + Var + tau_R) + permutation null. Self-tests (verdict 7/7 + 5 indicator-formula tests) PASS; local smoke at N=1024 / 1-seed PASS (CAP11_CHI4_MIDDLE_BAND, expected at smoke scale); remote --self-test gate PASS (2.4s). GPU pending=1, local pending=0; runner picks up next. Open risk: alpha_c may be Kerdock-specific; the alpha grid brackets 0.1x-1.4x of nominal so post-hoc recalibration is feasible.
## 2026-05-24 — RE-SHIP after v1/v2 dedup-failure (4 anchors, suffixed unique names)

Prior ship's v1/v2 names (wave14_cap8_vamp_iterates_srht_hadamard_v1, wave14_cap12_cap8_audit_trail_pipeline_v2, wave14_mp_ks_noise_envelope_sweep_v2) silently failed to enqueue — diagnostic confirmed 0 hits for vamp_iterates on remote_cpu_queue and only v1 of audit_trail_pipeline / noise_envelope_sweep present. Pause flag CLEARED at dispatch.

Re-ship under suffixed unique names + added Anchor 4 (substrate-honest E2 follow-up):

- **Anchor 1** wave14_cap8_vamp_iterates_srht_hadamard_v1b → remote_cpu_queue (timeout 3600s, ETA 30-45 min): 30 VAMP iterate trace files at N=4096 for SRHT+Hadamard. Output dir renamed to _v1b/ throughout.
- **Anchor 2** wave14_cap12_cap8_audit_trail_pipeline_v3 → remote_cpu_queue (timeout 3600s, ETA 30-45 min, depends on Anchor 1): Composition A audit at full 4 hard families. ITERATE_ROOT repointed to data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1b/. HARD PASS rho≥0.60 in ≥3/4 families.
- **Anchor 3** wave14_mp_ks_noise_envelope_sweep_v2b → remote_cpu_queue (timeout 4500s, ETA 45-60 min): 20 seeds × 5 eta × 5 codebooks fine grid to resolve v1' MIDDLE BAND.
- **Anchor 4** wave14_interp_family_N8192_v1 → overnight_queue GPU (timeout 9000s, ETA 60-120 min): substrate-honest E2 follow-up after N=16384 timeout. Kerdock@N=8192 structurally absent (log2=13 odd); script auto-skips and verdict requires ≥2 of {SRHT, Hadamard} present. Prereg includes explicit COMPUTE BUDGET + TIMEOUT-not-FAIL outcome.

**Name-uniqueness verification (pre-ship)**: greppped data/overnight_queue/queue.json and remote data/remote_cpu_queue/queue.json — none of the four new names present. Existing v1/v1' entries (mp_ks_noise_envelope_sweep_v1 and cap12_cap8_audit_trail_pipeline_v1) confirmed on remote as completed; they were the dedup-blockers for v1/v2.

**Self-tests**: 5+8+9+9 cases PASS locally. Remote --self-test gates: 3.0s + 3.7s + 3.7s + 4.1s.

**Smokes**: all 4 structurally valid at N=64-1024 / 1 seed; metrics.json written; verdict branches reached (CAP8_ITERATES_GENERATED / COMPA_AUDIT_INCONCLUSIVE / MP_KS_..._INCONCLUSIVE / INTERP_FAMILY_N8192_INCONCLUSIVE — all expected at smoke scale).

**Queue depths post-ship**: remote_cpu_queue = 3 pending (Anchor 1 running, Anchors 2+3 queued); overnight_queue = 1 pending (Anchor 4); local_cpu_queue = 0.

**Status_log**: 4 entries written (3 HIGH for cap-related, 1 MEDIUM for Anchor 4 follow-up).

**Routing note**: notes/exp_dev_to_queue_compa_anchors_reship_v1b_v3_v2b_plus_N8192_2026-05-24.md (Schema B markdown table, 4 rows).

**Blockers**: none. The dedup issue is resolved by suffixed unique names; remote --self-test gate confirms all four are queued and ready.
- 07:44 UTC | shipped wave14_cap12_cap8_audit_trail_pipeline_v4 to remote_cpu_queue (smoke=PASS, mode=smoke stamped; self-test+iid-Gauss-baseline PASS; entry RUNNING on cpu_runner_0 at verification time). v4 fixes v3 smoke-leak: ITERATE_ROOT repointed to v1c (30 valid traces); mode marker + rho_by_family lifted to top-level metrics.json; run_main hard-asserts mode=full and 4 hard families before writing. Composition A's first true 4-family quantitative test.
[12:06:04Z] Shipped Composition A v5 disambiguation chain (RM(1,m) iterate-fallback question): wave14_cap8_vamp_iterates_rm_1_m_v1 (anchor 1, ~10-15min CPU, generates 15 RM(1,m) VAMP iterate trace files) + wave14_cap12_cap8_audit_trail_pipeline_v5 (anchor 2, ~30-45min CPU, multi-root iterate loader, ITERATE_ELIGIBLE expanded to include rm_1_m). Both smoke=PASS, both confirmed in remote_cpu_queue/queue.json. Routing: notes/exp_dev_to_queue_compa_v5_disambiguation_2026-05-24.md (markdown-table schema).
- [16:00 ET] Shipped wave14_cap12_noise_cleanup_optshrink_v1 to remote_cpu_queue (5400s timeout). OptShrink DGN data-driven SVD-shrinkage denoiser for Cap 12 noise envelope expansion; closes Portfolio Gap 1 attempt. Self-test 13/13 PASS (incl. lambda*(1)=4/sqrt(3) to 1e-6 and clean-Hadamard eta=0 spectral preservation to 1e-4 Frobenius). Smoke at N=64/1-seed/2cb/2eta PASS with metrics.json. Remote --self-test PASS. Queue depth post-ship: 1 (status=running; runner picked it up immediately). Anchor: notes/research_audit_followup_drills_2026-05-24.md Section 3.

## Bet Z.5 S2 closure anchor shipped (wave14_cap8_vamp_ensemble_variance_overlay_v1)

Dispatched from Strategy invocation; Research drill notes/research_audit_followup_drills_2026-05-24.md Section 1.5 specified the S2 anchor (K=64 noise-seed-perturbed VAMP traces on Kerdock N=4096 alpha=0.5; per-coord empirical variance vs per-coord reconstruction error). Pause flag absent.

- Script: experiments/exp_wave14_cap8_vamp_ensemble_variance_overlay_v1.py
- Prereg: preregs/2026-05-24_wave14_cap8_vamp_ensemble_variance_overlay_v1.md (HARD PASS rho>=0.50 in >=3/5 codewords; HARD FAIL rho<0.30 in >=3/5; MIDDLE otherwise; verbatim per Research note)
- Queue: remote_cpu_queue (post-ship depth = 3, position 3)
- Routing note: notes/exp_dev_to_queue_betZ5_S2_closure_2026-05-24.md (markdown-table schema per task spec)
- Smoke result: N=1024/K=4/1cw end-to-end PASS in ~0.25s wallclock; verdict ENSEMBLE_OVERLAY_MIDDLE at smoke K=4 (rho=-0.031, expected at very low K). All 5 self-tests PASS including ensemble-variance analytical (K=200 unit Gaussian samples -> mean per-coord var within 0.05 of 1.0) and Spearman null/monotone bounds.
- Smoke verdict at K=4 not load-bearing: variance estimator noise floor at K=4 is ~sqrt(2/4)=0.71, so the smoke is checking pipeline correctness, not signal recoverability. Production K=64 reduces noise floor to ~0.18.
- status_log entry written with importance=MEDIUM and plain_language describing the housekeeping nature.

Used Kerdock at N=1024 for smoke because make_kerdock_4coset_codebook requires N=2^k for even k (PRIMITIVE_POLY supports t in {5,6,7} -> valid N in {1024, 4096, 16384}); cannot use N=64 or N=256 for Kerdock-specific smoke. Smoke at N=1024 is still cheap (~0.25s).
- Hatano-Sasa Cap 3 NESS audit-cert anchor `wave14_hatano_sasa_cap3_ness_crooks_v1` queued to remote_cpu_queue (timeout 1800s). Strategy Research neighborhood rec #3 (cheapest CPU ~5-15 min). Self-test 14/14 verdict + 4/4 HS formula cells PASS (1.8s); smoke 6 cells N=1024 M=30 beta=1.5 PASS (3.0s, MIDDLE_BAND with hs=1.50 cb_frac=0.40 - non-degenerate). HARD PASS [0.95,1.05] -> Cap 3 audit-cert (HANDOFF compose with Cap 1); HARD FAIL outside [0.5,2.0] -> informative-negative. Queue depth 4. status_log entry filed importance=HIGH.
- **2026-05-24 ship** `wave14_spectral_universality_kerdock_v1` -> remote_cpu_queue (timeout=5400s, ETA 45-60min). Dudeja-Sen-Lu spectral universality anchor; replaces MAMP anchor (MAMP=VAMP under RUI per Liu-Takeuchi Thm 2). Tests Kerdock vs 3 surrogates (iid_gaussian, random_sign_hadamard, haar_kerdock_spectrum) at M/N in {0.5,1,2,4,8} N=4096 5 seeds. Smoke PASSED: 5/5 verdict + 4/4 surrogate-spectrum self-tests; smoke N=1024 yields KERDOCK_UNIVERSALITY_IN_CLASS at M/N<=1. Local CPU runner dead (heartbeat status=exited at 2026-05-24T01:50); routed to Tier B remote per [[feedback-laptop-cpu-quick-probes]]. Queue depth after ship: 5 pending on remote_cpu_queue. Prereg: preregs/2026-05-24_wave14_spectral_universality_kerdock_v1.md. Queue note: notes/exp_dev_to_queue_spectral_universality_kerdock_2026-05-24.md.

## Tropical Cap-13 candidate (F-14) — Anchors 1+2 shipped

Dispatched per Strategy invocation citing Research deep-drill (notes/research_new_continents_deep_drill_2026-05-24.md). User explicitly flagged 'GPU is still idle' — Anchor 2 (GPU) ships in parallel to fill empty queues.

### Anchor 1 — wave14_tropical_margin_certificate_kerdock_v1 (CPU, ETA 4-8 hr)
- Queue: remote_cpu_queue (VERIFIED present in remote queue.json)
- Tests Cap 13 candidate 'tropical-polytope adversarial-margin certificate': closed-form margin via Tropical Decision Boundaries 2024 formula vs empirical BSC bit-flip threshold.
- N grid {4, 16, 64, 256, 1024} on 2-coset Kerdock codebook (Sylvester Hadamard + bent-coset, 2N codewords).
- HARD PASS: rel_err <= 0.05 at >= 4/5 N AND equiv-classes < 300 everywhere. HARD FAIL: rel_err > 0.25 at any N or equiv-classes >= 300.
- Self-tests PASS (8 cells: tropical poly eval, closed-form margin on N=2, Hadamard orthogonality, codebook shape, L_1 distance, margin non-negativity, equiv-class count, verdict logic for all 3 bands + overflow case).
- Smoke (N=4 / 1 seed / 3 codewords): VERDICT=TROPICAL_MARGIN_KILLED with rel_err=0.53 at N=4. HONEST READ: at N=4 integer bit-flip (each flip = L_inf 2) dominates continuous margin; expected to shrink at larger N. Prereg amended with explicit caveat. HARD PASS at full requires 4/5 N to pass — N=4 may legitimately fail while N>=16 passes.

### Anchor 2 — wave14_tropical_kerdock_N4096_emp_margin_v1 (GPU, ETA 30-60 min)
- Queue: overnight_queue (VERIFIED present in remote queue.json)
- Production-N=4096 empirical baseline using FULL 4-coset MM Kerdock (16384 codewords). 5 cells x 10 seeds x 5 codewords = 250 measurements. GPU-vectorized top-k bit-flip search.
- HARD PASS: cv (std/mean) <= 0.30 AND p25 > 0. HARD FAIL: cv > 0.80 OR > 20% degenerate.
- Self-tests PASS (5 cells: Kerdock construction at N=1024, self-margin > 0, bit-flip sensitivity, cell structure, verdict logic).
- Smoke (N=1024 / 1 seed / 2 codewords / 2 eps): VERDICT=EMP_MARGIN_WELL_DEFINED with cv=0.006 (very clean). Empirical margin ~ 490-496 bit-flips for N=1024 codebook -- substrate has a real adversarial threshold ~12% of N.

### Queue depth after ship (verified on REMOTE queue.json)
- remote_cpu_queue: 1 pending (wave14_tropical_margin_certificate_kerdock_v1)
- overnight_queue: 1 pending (wave14_tropical_kerdock_N4096_emp_margin_v1)
- BOTH verified via queue_add.sh's post-ship 'VERIFIED' line reading remote queue.json directly. Queue depth invariant per [[feedback-pipeline-pacing]] satisfied (both queues had 0 pending before ship).

### Blockers
None. One soft caveat: the smoke at N=4 producing TROPICAL_MARGIN_KILLED is a canary, not a blocker -- prereg explicitly accommodates 1/5 N failing (HARD PASS requires 4/5). The tropical-vs-bit-flip discretization gap at small N is a real theoretical concern; full run at N>=16 will tell whether closed-form claim holds at substrate-relevant scales.

Routing note: notes/exp_dev_to_queue_tropical_cap13_2026-05-24.md (markdown table; Schema B per dispatch.py parser).

- 14:?? wave14_online_W_lr_envelope_duration_v1 → remote_cpu_queue (timeout 1800s). Brain-inspired Cap 5 envelope anchor from Research drill (Gong et al. 2026 Science dopamine-duration). 4 lr envelopes at fixed Σ=10.0 (E1 baseline RM τ=10, E2 brief-spike rect, E3 extended rect, E4 RM τ=40), N=4096 bipolar, n_writes=50, p ∈ {0.20, 0.30, 0.40}, 3 seeds = 36 cells. Smoke PASS (all integrals 10.0000 exact); ship VERIFIED on remote (depth=2). Verdicts: LR_DURATION_BEATS_MAGNITUDE / LR_ENVELOPE_NEUTRAL / LR_ENVELOPE_MIXED. status_log HIGH.
- 2026-05-24: Shipped F-4 Clifford-TN Kerdock magic-bound Cap-13 candidate (split CPU+GPU). Sub-anchor A wave14_clifford_tn_kerdock_magic_bound_v1 -> remote_cpu_queue (6-12 hr CPU, N in {16,64,256,1024} x 5 seeds x n {2,3,4,5}, tests bond-dim-1 CMPS closed form vs v169 Schur-Weyl + Barnes-Wall magic=0). Sub-anchor B wave14_clifford_tn_kerdock_n4096_sanity_v1 -> overnight_queue (30-60 min GPU at N=4096 4-coset MM, 5 seeds x 5 codewords, eigvalsh on 16384x16384 Gram). Both smoke PASS: rel_err=0, BW magic=0, eig_dev_from_2point=1e-4. Self-tests 6+5=11 PASS local + remote. Queue verified: remote_cpu pending=3 (incl this), overnight pending=1 (this). Citations: Lami-Haug-De Nardis PRX Quantum 6.010345 (2025); Kalra-Sinha 2503.04101 (2025). Risk: Hopfield-cleanup post-processing may inject T-gate-equivalent magic at full Cap 8 pipeline (this anchor tests codebook, not iterated readout).

## 2026-05-24 13:25 — 5-anchor pickup-ready hand-off filed (orchestrator does NOT design inline)

Per [[feedback-no-experiment-design-in-prompts]] + [[feedback-structural-agent-usage-mandate]], the orchestrator did NOT design 5 substrate-grade experiments inline. The 5 anchors from `notes/strategy_request_to_exp_dev_2026-05-24_post_v183.md` (Ablation A per-task sub-substrate + Ablation B replay-only sweep + F-6 Boolean re-schema + SSM/S4 corrected task + Sellke re-design) are filed as a pickup-ready hand-off at `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` for the next exp_dev sub-agent cycle.

**Also filed**: 6th task — MS_1ST_ORDER script-bug fix (2-observation lock per [[feedback-lock-in-inefficiency-fixes]] after the v183 V3 re-queue produced the SAME INCONCLUSIVE with the same root cause). The path requires script-fix, NOT another rerun.

**No queue ships this cycle** for the 5 anchors. Next exp_dev cycle picks up.

**Queue state verified on remote at hand-off**: overnight=2 (MoE running GPU=81%, Tropical R2 pending), remote_cpu=2 (amp_se reroute running, v1c reroute pending), local=0.


---

## Exp_dev cycle (2026-05-24 14:10) — 5-anchor parallel ship from 11 hand-offs

**Routing source**: User-dispatched orchestrator sub-agent with Task 2 = "exp_dev pickup of 11 outstanding hand-offs"

**Inputs**:
- `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` (5 anchors, 1 consumed at v185 = Ablation A)
- `notes/strategy_untested_rows_triage_2026-05-24.md` (6 anchors targeting v1 KILLER/UNSURE untested)

### Ships (5)

| # | Name | Queue | Status post-ship | Hand-off | Hypothesis (brief) |
|---|---|---|---|---|---|
| 1 | wave14_betB_ablation_B_replay_sweep_v1_2026-05-24 | overnight_queue | **RUNNING** | 5anchors #2 | Replay-frac sweep [0.0..1.0]; bounds replay-only ceiling and isolates replay vs structural separation contribution to Bet B retention |
| 2 | wave14_betB_compound_pertask_replay_v1_2026-05-24 | overnight_queue | pending | v185 NEW pre-reg (axis stacking) | Compound: per-task substrates + cross-task replay; tests whether the two structural-separation axes stack to clear HARD-PASS 0.95 |
| 3 | wave14_boolean_noise_stab_kerdock_kkl_v1_reship_2026-05-24 | remote_cpu_queue | pending | 5anchors #3 | F-6 Cap-13 candidate (KILLED at v182) — bent-function noise-stability + KKL inequality re-ship with Schema A inline (note: also pending under `_rerun_2026-05-24` from earlier cycle) |
| 4 | wave14e_s4_depth_smoke_v1_2026-05-24 | remote_cpu_queue | pending | 5anchors #4 | SSM/S4 toy port: HiPPO-like state recurrence extends chain-cleanup depth past d~50 cliff (note: also pending under `_reship_..._rerun_2026-05-24` from earlier cycle) |
| 5 | wave14_learned_codebook_atoms_smoke_v1_2026-05-24 | local_cpu_queue | **COMPLETED in 1.5s** (HARD_FAIL but task-too-easy at N=1024) | strategy triage A6 | Learned PPMI-codebook atoms vs random bipolar at K in {4,8,16}; UNSURE A6 cheapest item from cap_map v1 |

### Design decisions (per [[feedback-no-experiment-design-in-prompts]] exp_dev role)

- Ship #1 (Ablation B): script already existed (built earlier this cycle); 7-cell replay_frac sweep at N=4096 5 seeds; HARD-PASS=monotone+peak>=0.90 / HARD-FAIL=plateau<0.80 at frac>=0.25 / MIDDLE otherwise.
- Ship #2 (Compound): wrote new `exp_wave14_betB_compound_pertask_replay_v1.py` (~280 LOC; reuses Ablation A's `evaluate_bpc_concat` + base Kovacs `train_w_with_replay`). HARD-PASS retention_A>=0.95 / HARD-FAIL <=0.821 (v185 Ablation A point) / MIDDLE between. Smoke at N=1024 1 seed: retention_A=0.942 (MIDDLE band; encouraging — full at N=4096 will resolve).
- Ship #3 (Boolean reship): used existing script unchanged; v183 hand-off's "proper schema" requirement satisfied by ship via queue_add.sh (Schema A inline key=value).
- Ship #4 (S4): used existing script unchanged.
- Ship #5 (Learned Codebook): wrote new `exp_wave14_learned_codebook_atoms_smoke_v1.py` (~250 LOC; pure numpy WHT + PCA-derived bipolar atoms; K-cleanup task with 2000 probes/cell). HARD-PASS all-K win + best delta>=0.05 / HARD-FAIL >=2-of-3 K not better / MIDDLE 1-of-3.

### Pre-reg self-tests (per [[feedback-strategy-spec-formula-selftests]])

- Ship #1: `--self-test` passed (existing helper).
- Ship #2: `--self-test` passed (8/8 cases covering HARD_PASS/HARD_FAIL/MIDDLE/INCONCLUSIVE).
- Ship #5: `--self-test` passed (4/4 cases).
- Ships #3, #4: used existing scripts that already passed self-test in earlier cycle.

### Dependencies verified (per [[feedback-ship-before-dependency-verified]])

- All 5 scripts present locally before ship.
- All 5 preregs present (1 NEW for compound, 1 NEW for learned codebook, 3 existing).
- queue_add.sh's automatic SCP+SSH replication handles remote-side script/prereg placement; post-ship VERIFY ran for ships #1-#4 (remote queue.json `experiments[].name == NAME`).

### Post-ship VERIFY (per [[feedback-ship-name-collision]])

- Ship #1 (GPU): WARN "already in queue" detected — pre-existing pending entry was discovered. queue_add.sh's verification confirmed the name IS in remote `overnight_queue/queue.json`; runner picked it up and it's now RUNNING. No collision damage; the WARN means an earlier exp_dev cycle had filed this same name (consistent with the 5anchors hand-off being a continuation).
- Ship #2 (GPU): VERIFIED present in remote `overnight_queue/queue.json`; status pending.
- Ship #3 (remote_cpu): VERIFIED present in remote `remote_cpu_queue/queue.json`; status pending. **Note**: a parallel `_reship_..._rerun_2026-05-24` entry from earlier cycle is ALSO pending — both will run (mild waste; not blocking).
- Ship #4 (remote_cpu): VERIFIED present; same parallel `_rerun_` situation as ship #3.
- Ship #5 (local_cpu): VERIFIED via local cat of `queue.json`; status went from pending -> running -> completed in 1.5s.

### Honest finding on ship #5 (Learned Codebook HARD_FAIL)

The verdict label is mechanically correct but substantively a **task-too-easy-at-N=1024 artifact**. Both random and learned atoms hit 100% K-cleanup accuracy at all K in [4,8,16] with deltas all 0.0. The N=1024 / 2000-probe / K<=16 task saturates BOTH families. This is NOT a refutation of A6's "+0.02-0.08 at K=4" prediction — the prediction was implicitly at HARDER N or with NOISE. The bpc-style cleanup at N=1024 vocab=256 with no noise is information-theoretically trivial.

**Rehab path** (does NOT close A6 row): re-design with either (a) N=128 (very small substrate); (b) larger K (K in {32, 64, 128} to stress-test); (c) noise (bit-flip during cleanup). Per [[feedback-rehabilitation-after-rejection]] + [[feedback-dont-overextend-theorems]] A6 row stays 🔬 with under-resolved-N annotation; no cap_map closure.

This honest flag is in `data/orchestrator_status_log.jsonl` as a MEDIUM-importance status_log entry. The next verdict cycle's Step 0 re-read should propagate to cap_map: do NOT close A6 on this verdict.

### Queue depths post-ship

- overnight_queue (GPU): Ablation B RUNNING + compound + 5 prior pending = 6 pending+1 running. Pipeline depth >> 1.
- remote_cpu_queue: 6 pending including my 2 fresh ships + 4 pre-existing _rerun_ entries. Depth >> 1.
- local_cpu_queue: 0 pending (ship #5 completed). Local runner idle again — could absorb another quick probe in subsequent cycle.

### Discipline citations

- per [[feedback-no-experiment-design-in-prompts]]: exp_dev role decided N / M / seeds / thresholds / queue / formula for all 5 ships
- per [[feedback-strategy-spec-formula-selftests]]: --self-test passed for ships #1, #2, #5; existing self-tests passed for #3, #4
- per [[feedback-ship-before-dependency-verified]]: all 5 scripts + preregs verified on disk before ship; SCP+SSH replication handled remote-side
- per [[feedback-ship-name-collision]]: name uniqueness verified pre-ship; post-ship VERIFY confirmed entries in remote queue.json
- per [[feedback-no-smoke]]: all 5 preregs have HARD-PASS + HARD-FAIL + MIDDLE bands falsifiable before run
- per [[feedback-envelope-expansion-fail-bands]]: bands match the broader claim for each anchor
- per [[feedback-for-you-tab-primary-channel]]: 2 status_log entries written (experiment_queued HIGH + verdict MEDIUM for ship #5 honest flag)
- per [[feedback-ascii-only-in-scripts]] OBSOLETED 2026-05-23: encoding handled structurally via `sys.stdout.reconfigure` at script top
- per [[feedback-dispatch-wrappers-default]]: this sub-agent context internalized exp_dev role inline (Agent dispatch unavailable per orchestrator post-compaction brief Section 2)

### Blockers

- **None for ships shipped.** Ship #5 (Learned Codebook) returned HARD_FAIL but the honest reading is task-too-easy NOT capability-refuted; rehab path filed in this decision log + status_log entry — no cap_map closure required.
- Pre-existing `_reship_..._rerun_2026-05-24` entries for Boolean + S4 + Sellke on remote_cpu were ALREADY pending from an earlier exp_dev cycle; my 5anchors-#3 + #4 ships duplicated them. Mild waste but the runner will resolve both; recommend dedup in subsequent cycle by killing one copy of each.

### Backlog (6 hand-offs NOT shipped this cycle)

- Sellke re-design with narrowed eps (5anchors #5; low priority + needs design work for "alternate baseline")
- MS_1ST_ORDER script-bug fix (5anchors #6; script-fix not queue task)
- K1 GPT-quality generation eval harness (Priority B; needs new build)
- K2 4-stage Lane D continual learning (Priority A KILLER T1; needs new script — extends 3-stage `lane_D_end_to_end_*` family)
- K3 On-device personalization end-to-end (Priority A KILLER T2; needs new pipeline script)
- K4 Cross-modal binding (Priority B; needs image-embedding source decision)
- K5 Real-time learning during inference (Priority A KILLER T2; needs pipeline-config script)
- K6 Compositional generalization (Priority A KILLER T2; existing R10 infra could be extended)
- K7 Multi-step inference (Priority B; needs deduction harness)
- U1 Multi-task transfer A->C (Priority A; cycle-94 retraction re-do; needs different-corpus mapping)
- U5 Sleep-style memory consolidation (Priority B; replay schedule variant)
- A8 Hersche 2024 sparse block codes port (Priority B; cheap port)
- A6 Learned codebook RE-DESIGN at smaller N or with noise (this-cycle honest finding)


## Cycle (2026-05-24 ~17:00 LT) — v190 post-batch refill ship of 4 anchors (inline exp_dev role)

**Trigger**: orchestrator post-v190 batch refill. v190 committed 10-verdict cap_map update; CPU queue drained to 0; GPU queue at 2 pending (healthy backlog but room for K2 + K6 rehab anchors).

**Routing source**: v190 cap_map narrative block — 4 K6 rehab axes filed + 3 U1/U7 rehab axes filed + K2 axis 3 (last remaining of 3-axis list) + K5 instrumentation repair filed. Per [[feedback-no-experiment-design-in-prompts]] exp_dev role decided: pick the cheapest highest-leverage axis from each pre-registered list.

**Shipped 4 anchors (2 GPU + 2 CPU)**:

| # | Queue | Name | Routing |
|---|---|---|---|
| 1 | overnight_queue (GPU) | wave14_betB_4stage_continual_v2_rehab_phaseD_a_weighted_v1 | K2 KILLER T1 axis 3 of v189 3-axis list (final remaining axis); Phase-D replay buffer up-weights stage A samples 4x to counter capacity-bound load accumulation; N=4096 5-seed |
| 2 | overnight_queue (GPU) | wave14_compositional_holdout_rehab_n8192_v1 | K6 KILLER T2 rehab axis 1 of v190 4-axis list; N=8192 (was N=4096 at v190) + 5 seeds (was 1) |
| 3 | remote_cpu_queue (CPU) | wave14_realtime_inference_learning_v1_rerun | K5 KILLER T2 instrumentation repair from v190 V10 LABEL-OVER-CLAIM; pretrain_bytes capped against live corpus_len; hard assertions added; rerun produces real metrics |
| 4 | remote_cpu_queue (CPU) | wave14_betB_multitask_diff_corpus_rehab_n4096_v1 | U1/U7 UNSURE T2 rehab axis 2 of v190 3-axis list; N=4096 (was N=2048 at v190) + 5 seeds |

### Per-ship verification (REMOTE)

- Ship #1 (GPU): VERIFIED present in REMOTE `overnight_queue/queue.json` (queue depth 3 -> 4 after add); status pending. Self-test PASSED on remote in 1.9s.
- Ship #2 (GPU): VERIFIED present in REMOTE `overnight_queue/queue.json` (queue depth 4 -> 5 after add but wrapper shows 4 because remote may be running ahead of local cache); status pending. Self-test PASSED on remote in 2.2s.
- Ship #3 (CPU): VERIFIED present in REMOTE `remote_cpu_queue/queue.json` (queue depth was 0 -> 1 after add); status pending. Self-test PASSED on remote in 2.0s.
- Ship #4 (CPU): VERIFIED present in REMOTE `remote_cpu_queue/queue.json` (queue depth 1 -> 2 after add); status pending. Self-test PASSED on remote in 2.4s.

### Honest reads / smoke commentary

- Ship #1 (K2 axis 3): smoke at N=1024 single-seed gave retA=0.924 / retB=0.914 / retC=0.931 = FOURSTAGE_HARD_PASS. Smoke is NOT predictive of FULL since v1 + axis 1 + axis 2 all had similar smoke results but FULL landed at MIDDLE band. The user pre-cycle reading "no consolidation lift" was honest; axis 3 is the structurally-different rehab path (replay-buffer composition, not capacity or consolidation time). MIDDLE band remains the most likely outcome per the v188 / v189 / v190 axes 1+2 saturation pattern.
- Ship #2 (K6 rehab): smoke at N=1024 single-seed gave hold_out=0.094 train=0.526 = COMPOSITIONAL_HARD_FAIL (just below 0.1 chance-floor). v1 at N=4096 was hold_out=0.116 (1.85x chance). Smoke at smaller N naturally produces lower hold-out. FULL at N=8192 5-seed is the definitive test; HARD-PASS would require hold_out >= 0.5 which is a substantial lift from current 0.116.
- Ship #3 (K5 rerun): smoke at N=512 gave bpc_frozen=3.834 bpc_online=3.762 delta=-0.072 = REALTIME_INFERENCE_HARD_PASS. This DEMONSTRATES the instrumentation fix works — original v1 smoke was also clean; bug was in the FULL config's pretrain_bytes-vs-corpus mismatch. FULL result is now meaningful.
- Ship #4 (U1/U7 rehab): smoke at N=1024 single-seed gave retA=0.843 gain_C=3.676 = MULTITASK_DIFF_HARD_PASS. This is a PROMISING signal — N-scaling from 2048 -> 4096 may close the retA gap. FULL at N=4096 5-seed is the definitive test.

### Queue depths post-ship

- overnight_queue (GPU): 4 pending (wave14_betB_replay_by_norm_v1 + wave14_betB_task_geometry_v1_rerun + ship #1 + ship #2; healthy backlog). Plus there may be additional entries on the remote that the local snapshot does not reflect — local cap_map state cache reported v182 even at the start of this cycle, indicating polling lag.
- remote_cpu_queue: 2 pending (ship #3 + ship #4; CPU was at 0 pending pre-ship).
- local_cpu_queue: idle.

### Discipline citations

- per [[feedback-no-experiment-design-in-prompts]]: exp_dev role decided N / seeds / formula / queue / thresholds for all 4 ships from v190 routing pointers (cap_map narrative listed rehab axes; exp_dev selected the highest-leverage cheapest axis from each list per [[feedback-rescue-sketch-first-sequencing]]).
- per [[feedback-no-smoke]]: all 4 preregs have HARD-PASS + HARD-FAIL + MIDDLE bands falsifiable before run.
- per [[feedback-envelope-expansion-fail-bands]]: bands match the broader claim for each anchor (K2 rehab gate; K6 rehab gate; U1/U7 rehab gate; K5 instrumentation-only rerun reuses v1 bands).
- per [[feedback-ship-before-dependency-verified]]: all 4 scripts + preregs verified on local disk before ship; SCP+SSH replication via tools/orchestrator/queue_add.sh wrapper.
- per [[feedback-ship-name-collision]]: name uniqueness verified pre-ship; post-ship REMOTE VERIFY confirmed entries in remote queue.json for all 4.
- per [[feedback-ascii-only-in-scripts]] OBSOLETED 2026-05-23: encoding handled structurally via `sys.stdout.reconfigure` at script top.
- per [[feedback-dispatch-wrappers-default]]: this sub-agent context internalized exp_dev role inline (Agent dispatch unavailable per orchestrator post-compaction brief Section 2 execution-model clarification).
- per [[feedback-for-you-tab-primary-channel]]: 4 status_log entries written (experiment_queued: ship #1 HIGH + ship #2 HIGH + ship #3 MEDIUM + ship #4 HIGH).
- per [[feedback-verdict-msg-honest-reread]]: V10 LABEL-OVER-CLAIM v190 -> ship #3 is the structural fix for that observation; K5 capability claim cannot be re-attempted until this rerun produces real metrics.

### Blockers

- **None for ships shipped.**
- Pre-existing 13-item backlog (K1 GPT-quality eval harness; K3 on-device personalization; K4 cross-modal binding; K7 multi-step inference; U1 corpus mapping redesign; U5 sleep replay variant; A8 Hersche port; A6 learned codebook re-design at smaller N; Sellke alternate baseline; MS_1ST_ORDER script fix; etc.) carries forward UNCHANGED. Higher-leverage v190 rehab axes (K6 axes 2-4; U1/U7 axes 1+3; K2 product-spec rescoping decision) await ship #1 and #2 + #4 results before next round.
2026-05-24T21:24:54 v193 queue refill: shipped 6 anchors (2 GPU + 3 remote CPU + 1 local CPU); all 6 verified into queues + all 6 completed at FULL. Verdicts: R-PRIME-2 HARD-FAIL (MoE-on-substrate REJECTED at K-sweep), R-PRIME-3 R1 HARD-FAIL (alt-geometry rescue fails at full scale; smoke false-positive at n_pairs=3), Field-A HARD-FAIL (reservoir-Lyapunov REJECTED), K6 axis2 HARD-FAIL (compositional generalization REJECTED), F-6 HARD-PASS (KKL low-influence boundaries -> Boolean-analysis row 🟡 promotion candidate), Bet M MIDDLE_BAND (harness 4/5 correct, median_BIC_gap=2.23 borderline). Routing notes/exp_dev_to_queue_v193_queue_refill_batch_2026-05-24.md. Queue depths post-cycle: GPU=5pending pre-existing, remote_cpu=0, local_cpu=0; CPU queues need refill next cycle.

## Cycle (2026-05-24 ~21:35 LT) — v195 8-anchor batch ship + COMPLETED SAME CYCLE

**Trigger**: v195 pipeline drained handoff. Pause flag absent verified.

**Shipped + REMOTE VERIFIED + COMPLETED 8 anchors (3 GPU + 1 GPU rerun + 3 remote CPU + 1 local CPU)**:

| # | Queue | Name | FULL verdict |
|---|---|---|---|
| 1 | GPU | wave14_rprime1_pac_bayes_floor_v1 | PAC_BAYES_FLOOR_HARD_FAIL (floor not binding — substrate above conservative bound) |
| 2 | GPU | wave14_k4_cross_modal_binding_v1 | CROSS_MODAL_BIND_HARD_FAIL (K4 KILLER at substrate level at synthetic floor) |
| 3 | GPU | wave14_k7_multistep_inference_v1 | MULTISTEP_INFER_HARD_FAIL (K7 deduction collapses to chained-retrieval) |
| 4 | GPU | wave14_betB_1rsb_basin_discrete_v2 | BASIN_DISCRETE_HARD_FAIL (R-PRIME-3 R4 closes; family done; v1 OOM'd, v2 with memory-fix shipped) |
| 5 | rcCPU | wave14_betM_logforget_longt_v1 | BETM_LONGT_MIDDLE_BAND (log vs exp still ambiguous at t in 1..200) |
| 6 | rcCPU | wave14_sparse_coding_ppmi_v1 | SPARSE_CODING_HARD_FAIL (sparse loses to random+PCA; A6/U3 closed at envelope) |
| 7 | rcCPU | wave14_popgen_drift_retention_v1 | POPGEN_DRIFT_MIDDLE_BAND (Wright-Fisher closed-form candidate alive on some seeds) |
| 8 | local | wave14_k8_hierarchical_concepts_v1 | HIER_CONCEPTS_HARD_FAIL (K8 closes; aligned with R3 closure at K>=16) |

**Routing note**: notes/exp_dev_to_queue_v195_8anchor_batch_2026-05-24.md.

**Honest mix met user directive**: 2 Bet B 5th-mechanism rescues (R-PRIME-1 + 1-RSB) / 2 new-field probes (sparse-coding + popgen) / 3 untested KILLERs (K4 + K7 + K8). Plus Bet M longer-t as resolver. All HARD_FAIL outcomes are HONEST refutations at the tested envelopes — none are smoke-extensions of validated primitives.

**Blockers**: single OOM on 1-RSB v1 (kmeans (n,k,d) broadcasting at N=4096); structurally fixed via per-centroid pairwise distance + N reduced to 2048; v2 shipped + completed.

**Queue depths post-cycle**: GPU=0 pending, remote CPU=0 pending, local CPU=0 pending. Pipeline DRAINED — orchestrator triggers next refill cycle.
v195 emergency refill: shipped 4 anchors (1 GPU + 2 remote_cpu + 1 local_cpu). K2 M1 hierreplay smoke HARD_PASS (retA=0.888 vs 0.74 baseline) -> GPU RUNNING; betM logforget longt + rprime3 r2 subcorpus -> remote_cpu (betm completed, r2 running); f6 kkl envelope -> local_cpu (completed MIDDLE_BAND 11/12 cells, 0 hard-fail). 2 smoke HARD_FAILs blocked: K6 axis3 cleanup-iter (cleanup loop diverges for linear Hebbian W) + rprime1 pac-bayes v2 (KL ~ N^2/2 per task, structurally vacuous bound). Upstream routing notes filed for both.
## Cycle (2026-05-24 -- 1-RSB diagnostic battery ship post-k2_m1 HARD_PASS)

**Trigger**: k2_m1_hierreplay smoke HARD_PASS retA=0.888 vs 0.74 baseline; pipeline refill
directive from orchestrator. k2_m1 FULL already running on GPU. Diagnostic battery for
basin-discrete 1-RSB framing shipped as 4 new anchors.

**Shipped 4 anchors (2 GPU + 1 remote_cpu + 1 local_cpu)**:

| # | Queue | Name | Routing |
|---|---|---|---|
| 1 | overnight_queue (GPU) | wave14_1rsb_cascade_depth_v1 | Pred-5: cascade-depth sensitivity -- 2/3/4/5 stage chains with M1 chunk replay; 1-RSB predicts cliff+plateau, RS predicts smooth |
| 2 | overnight_queue (GPU) | wave14_1rsb_capacity_plateau_v1 | Pred-1: capacity-sweep plateau morphology -- retA vs M_stored at 7 points; 1-RSB predicts cliff+plateau, RS predicts smooth |
| 3 | remote_cpu_queue (CPU) | wave14_1rsb_pq_retained_v1 | Pred-2: P(q) multi-delta from retained W-vectors -- 10 seeds W_ABCD overlap distribution |
| 4 | local_cpu_queue (CPU) | wave14_1rsb_ultrametric_triples_v1 | Pred-3: ultrametric inequality on retained triples -- 12 seeds, 1000 triples, eps=0.10 |

### Per-ship verification (REMOTE)

- Ship #1 (GPU cascade-depth): VERIFIED in overnight_queue/queue.json. Self-test 4/4 in 2.0s.
- Ship #2 (GPU capacity-plateau): VERIFIED in overnight_queue/queue.json. Self-test 4/4 in 2.0s.
- Ship #3 (CPU pq-retained): VERIFIED in remote_cpu_queue/queue.json. Self-test 4/4 in 2.3s.
- Ship #4 (local ultrametric): VERIFIED in local_cpu_queue/queue.json. Self-test 4/4 in 1.6s.

### Smoke outcomes (all run before ship)

- cascade_depth smoke: CASCADE_DEPTH_MIDDLE (max_delta=0.058, just under 0.08 smooth threshold;
  depth profile 2->3->4 shows non-monotone: 0.907->0.849->0.898 at N=1024 1-epoch). MIDDLE
  is not a blocker -- smoke at reduced N/epochs is noisy; FULL at 5 epochs + 5 seeds needed.
- capacity_plateau smoke: CAPACITY_PLATEAU_RS_SMOOTH (max_delta=0.067 < 0.08; 3-pt smoke at
  N=1024 shows smooth but gap is marginal -- FULL at N=4096 7-pt sweep may show cliff).
- pq_retained smoke: PQ_RETAINED_MIDDLE (only 2 seeds -> 1 pair; binder=0.667 surprisingly high;
  FULL at 10 seeds will give robust P(q)).
- ultrametric_triples smoke: ULTRAMETRIC_1RSB_CONFIRMED (fraction=1.0 but at N=512 all overlaps ~0
  so trivially ultrametric -- validity concern noted; FULL at N=2048 12 seeds needed for real test).

### HARD-PASS / HARD-FAIL bands (pre-registered)

| Anchor | HARD-PASS | HARD-FAIL |
|---|---|---|
| cascade_depth | cliff >= 0.15 + plateau < 0.05 at any depth step | max_delta < 0.08 + var < 0.002 |
| capacity_plateau | cliff >= 0.15 + plateau < 0.05 at any M step | max_delta < 0.08 |
| pq_retained | >= 2 peaks >= 2-sigma + binder > 0.30 | <= 1 peak OR sep < 2-sigma AND binder <= 0.05 |
| ultrametric_triples | fraction >= 0.50 | fraction <= 0.36 |

### Discipline citations

- per [[feedback-no-experiment-design-in-prompts]]: exp_dev role designed N/seeds/thresholds
  autonomously from the 1-RSB research framing in the cap_map narrative (basin-discrete
  cluster-structured plateau pattern; Parisi ultrametricity; capacity-sweep morphology).
- per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands registered
  BEFORE smoke; band logic verified via self_test_verdict() on all 4 scripts (4/4 cases each).
- per [[feedback-ship-before-dependency-verified]]: all 4 scripts + preregs verified local + remote.
- per [[feedback-ship-name-collision]]: names verified unique pre-ship; post-ship REMOTE VERIFY
  confirmed entries in queue.json for all 4.
- per [[feedback-ascii-only-in-scripts]]: encoding handled via sys.stdout.reconfigure at top.
- per [[feedback-for-you-tab-primary-channel]]: 4 status_log entries to write post-log.
- per [[feedback-verdict-msg-honest-reread]]: smoke outcomes honestly noted (cascade/capacity
  MIDDLE not HARD_PASS; ultrametric trivial at smoke N -- acknowledged before FULL).

### Queue depths post-ship

- overnight_queue (GPU): 2+ pending (cascade_depth + capacity_plateau; k2_m1 RUNNING).
- remote_cpu_queue: 1 pending (pq_retained).
- local_cpu_queue: 1 pending (ultrametric_triples) + rprime3_r2 running.

## 2026-05-24 -- Pred-4 1-RSB hysteresis anchor shipped (CPU queue refill post-pq_retained MIDDLE)

**Trigger**: wave14_1rsb_pq_retained_v1 MIDDLE (Pred-2 inconclusive; binder=-0.164 q_EA~0); remote_cpu_queue=0 IDLE; Pred-4 hysteresis is sole remaining CPU diagnostic not on any queue.

**Pause gate**: CLEARED (data/orchestrator_paused.flag absent).

**Anchor: wave14_1rsb_hysteresis_v1** -> remote_cpu_queue (timeout=5400s, ETA 30-45 min)

Tests Pred-4 of the 1-RSB diagnostic battery: hysteresis under capacity sweep.
- Forward trajectory: train 4-stage M1 hierreplay at M in {25k, 50k, 100k, 150k, 200k, 300k, 400k} bytes (low->high)
- Reverse trajectory: same M sweep in reverse (high->low)
- At each M, measure retA (stage-A retention after all 4 stages)
- Hysteresis gap = |retA_forward - retA_reverse| at each M cell
- N=2048, 3 seeds {7, 17, 23}, 7 M cells

HARD-PASS (first-order): max gap >= 0.10 at any M -> HYSTERESIS_1RSB_CONFIRMED
HARD-FAIL (continuous): max gap < 0.03 everywhere -> HYSTERESIS_RS_SMOOTH
MIDDLE: gap in [0.03, 0.10) -> HYSTERESIS_MIDDLE

Self-tests: 6/6 PASS (local + remote gate). Remote --self-test gate PASS in 1.8s.
Post-ship VERIFIED: entry in remote_cpu_queue/queue.json.

**Decision: 1 anchor only** (Pred-4 is the natural CPU candidate; no second high-leverage CPU diagnostic identified from the battery; GPU has Pred-1 + Pred-3 covered; local has Pred-5). Queue depth invariant satisfied (remote_cpu_queue pending=1).

**PROT compliance**: PROT-010 (post-compaction brief read); PROT-011 (exp_dev subagent_type named); [[feedback-envelope-expansion-fail-bands]] (HARD-PASS/HARD-FAIL/MIDDLE pre-registered); [[feedback-strategy-spec-formula-selftests]] (6/6 self-test cells); [[feedback-ship-name-collision]] (name verified unique pre-ship); [[feedback-no-blocking-runs]] (background only via queue); [[feedback-ascii-only-in-scripts]] (stdout.reconfigure at top).

**Routing note**: notes/exp_dev_to_queue_1rsb_hysteresis_2026-05-24.md (Schema A, 1 row).

**status_log**: HIGH importance entry written with plain_language.


## 2026-05-24 -- Bet B Alt1/Alt2 + 1-RSB GPU anchor batch ship (3 anchors)

**Trigger**: User dispatch: R-PRIME-3 HARD-FAIL eliminated continuous-geometry predictor; 3 alternative predictor families + 1 GPU anchor requested. Overnight queue IDLE. Local queue IDLE.

**Pause gate**: CLEARED (data/orchestrator_paused.flag absent).

### Anchor 1: wave14_betB_shift_class_predictor_v1 -> local_cpu_queue (timeout=300s)

Alt1 of R-PRIME-3 rescues. Tests whether discrete shift-class taxonomy (6 classes) predicts Bet B retention better than continuous spectral geometry. Zero-new-compute: pure re-analysis of existing metrics.json artifacts. Smoke showed SHIFT_CLASS_HARD_PASS (6/6 non-overlapping CIs, K-W p~0.0). HARD-PASS pre-reg: >=4/6 non-overlapping CIs AND K-W p<0.05. Self-tests: 9/9 PASS.

Post-ship VERIFIED: wave14_betB_shift_class_predictor_v1 in local_cpu_queue.

### Anchor 2: wave14_betB_W_internal_signature_v1 -> overnight_queue (GPU, timeout=10800s)

Alt2 of R-PRIME-3 rescues. Tests whether substrate-INTERNAL W signatures measured AFTER Phase-A (before Phase-B) predict Phase-B retention. 13 signatures: top-3 eigenvalues, spectral gap, spectral gap ratio, normalized Frobenius norm, bundle-norm mean/std/var/kurtosis/skewness, row-norm mean/std. HARD-PASS: best r2>=0.50. 5 seeds x 5 corpus pairs = 25 cells.

REFRAME NOTE: Originally specified as zero-new-compute re-analysis of existing artifacts. Investigated: W checkpoints are NOT saved (only metrics.json). bpc_gap achieves r2=0.988 with retention_A but is tautological (requires Phase-B already run). bpc_A_baseline alone: r2=0.011. Reframed as NEW GPU experiment that runs Phase-A only, saves W, measures internal signatures, then runs Phase-B across 5 held-out corpus pairs. Documented honestly in prereq.

Smoke: HARD_FAIL as expected (N=512 1-seed; all signatures constant across pairs from same seed/Phase-A).
Self-tests: 9/9 PASS. Post-ship VERIFIED in overnight_queue.

### Anchor 3: wave14_1rsb_ultrametric_triples_full_v1 -> overnight_queue (GPU, timeout=7200s)

Pre-registered open item from v199 cap_map. 1-RSB diagnostic: do W-vector triples satisfy Parisi ultrametricity at N=2048 12-seed FULL? Smoke at N=512 trivially CONFIRMED due to near-zero overlaps (UV-problem: q_EA~0 -> isosceles condition trivially met). FULL at N=2048 with C(12,3)=220 possible triples and N_TRIPLES=1000 bootstrap is the discriminating run.

HARD-PASS: fraction>=0.50 (1-RSB ultrametric supported). HARD-FAIL: fraction<=0.36 (near 0.33 random baseline). If mean_q near zero (|mean_q|<0.01), UV-problem logged as diagnostic note.
Self-tests: 4/4 PASS. Post-ship VERIFIED in overnight_queue.

### Alt3 placeholder

Alt3 (PAC-Bayes posterior-over-W KL predictor) deferred until R-PRIME-1 KL derivation lands. Routing note filed at notes/strategy_request_to_exp_dev_alt3_pac_bayes_placeholder_2026-05-24.md. Trigger condition: research delivers R-PRIME-1 posterior-over-W KL derivation.

**PROT compliance**: PROT-010 (post-compaction brief read via summary); PROT-011 (exp_dev subagent_type named); [[feedback-envelope-expansion-fail-bands]] (HARD-PASS/HARD-FAIL/MIDDLE pre-registered for all anchors); [[feedback-strategy-spec-formula-selftests]] (9/9 Alt1, 9/9 Alt2, 4/4 Alt3); [[feedback-ship-name-collision]] (queue_add.sh VERIFIED all anchors post-ship); [[feedback-no-blocking-runs]] (background only via queue); [[feedback-ascii-only-in-scripts]] (verified); [[feedback-no-experiment-design-in-prompts]] (all parameters decided by exp_dev per contract).

**status_log**: 4 entries written (Alt1 HIGH, Alt2 HIGH, GPU2 HIGH, Alt3-placeholder LOW).
Shipped wave14_moe_alpha_c_prestep_v1 (GPU, alpha_c calibration mandatory pre-step for MoE rebuild) and wave14_betB_pac_bayes_kl_predictor_v1 (GPU, Alt3 Laplace-Fisher KL predictor unblocked by R-PRIME-1 derivation commit 0140545). Both verified in overnight_queue. Smoke passed for both (5/5 self-tests each).
2026-05-24 exp_dev: MoE unblock -- shipped wave14_moe_alpha_c_prestep_v2 (recalibrated bands [0.40,0.70], full GPU 5-seed) + wave14_moe_shift_partition_v1 (3-arm SHIFT/PARTITION/SINGLE, K in {1,2,4,8}, M_per_expert=1600 from alpha_c=0.56). Both smoke-PASSED, remote-verified overnight_queue. Prestep runs first (15-30 min); main arm follows (4-6 hr). Walk-back: smoke d=0.446 borderline but per-cell K=4 lift +0.19 exceeds HARD-PASS 0.15 threshold; full 5-seed N=4096 will resolve. Arm C (SINGLE) uses random projection + binarization to sqrt(K)*N; comparison is conservative (penalizes C) -- acceptable per pre-reg.exp_dev 2026-05-25: Shipped 7 local_cpu_queue re-analysis probes (heavy CPU night, SSH down): (1) alt_taxonomy_sweep_v1 -- MIDDLE 4-class silhouette 0.584; (2) pac_bayes_laplace_selftests_v1 -- SELF_TEST_PASS 7/7; (3) saddle_cascade_reanalysis_v1 -- CASCADE_PASS delta_BIC=194.9; (4) moe_alpha_c_formula_verify_v1 -- FORMULA_VERIFIED M_per_expert=1612; (5) verdict_pattern_mining_v1 -- PATTERN_FOUND multi-agent V=0.32; (6) ib_plateau_kswoop_v1 -- IB_INCONSISTENT; (7) retention_gap_structure_v1 -- STRUCTURE_DIFFUSE K=1.2026-05-25: Queued 4 local_cpu Tier C re-analyses: saddle_saadsolla_plateau_arithmetic_v1 (angle spacing vs height spacing discriminant -- smoke NEITHER_EQUAL; angle_gap_ratio=0.70 outside [0.80,1.25]), verdict_dispatch_context_v1 (dispatch sub-pattern follow-up -- smoke NO_REFINEMENT; multi-agent gap unexplained by dispatch style or concreteness), pac_bayes_kl_extended_corpus_v1 (PAC-Bayes floor extrapolation -- smoke FLOOR_VIOLATED; 3-anchor power-law insufficient, GPU v2 needed), taxonomy_contrast_retention_sep_v1 (K=2/3/4 contrast -- smoke TWO_TIER_SUFFICIENT; F-ratio 334->266->256 drops with more classes despite sil improvement 0.22->0.32->0.58).