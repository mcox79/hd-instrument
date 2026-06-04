# Exp-Dev compaction brief -- 2026-06-04 (READ FIRST after context reset)

## Role + scope
I am the **Exp-Dev** session (4-session arch: Orchestrator + Exp-Dev + Research + Testbed). I ship
experiments (stamp/build scripts -> prereg -> smoke/self-test -> queue_add -> verify). Per the
2026-06-04 user correction ([[feedback_routings_direct_to_exp_dev]]) ALL experiments route DIRECTLY to
me (substrate-physics Q-A3/Q-B1/PP-*; brain-inspired tiny LMs on CPU; owned-GPU); Testbed = cloud-GPU
only. I do NOT process/interpret verdicts or set strategy (Orchestrator/verdict_handler owns that) --
read data/exp_<name>/metrics.json ONLY for completion status. Cadence: ~30-min wakeups, ship from
newest notes/orchestrator_to_exp_dev_priorities_* + Research handoffs; skip if both queues pending>=5;
NO padding (ship a short queue + surface if no real work).

## Infra cheat-sheet (hard-won this session)
- remote `marsh@home` is **Windows/PowerShell**; runner repo at **C:\dev\hd-instrument**; queues at
  data\<queue>\queue.json (.experiments[].status). Local repo d:/AI/hd-instrument.
- Verdicts/metrics: **data/exp_<anchor>/metrics.json** (NOTE the exp_ prefix). [[feedback_metrics_path_exp_prefix]]
- SSH multi-line / regex-with-pipes BREAKS through bash->ssh->cmd->powershell. Use a **.ps1 file + scp + run**
  (tools/_read_verdicts.ps1 dumps verdicts+queue depth; reuse it). -ExecutionPolicy Bypass is blocked.
- **Route GPU vs CPU by `grep torch.cuda`, NOT by N.** A numpy script on overnight_queue idles the GPU +
  blocks real GPU jobs. [[feedback_route_gpu_vs_cpu_by_torch_not_N]] (caused the q_f5 GPU-1% incident).
- queue_add.sh <queue> <name> <script> <prereg> <timeout>. PROT-019 floor: 21600 for _n>=8192, 14400 for
  _n4096. No cancel/requeue tool (cancel = kill python subprocess by cmdline + edit queue.json UTF-8-no-BOM).

## In-flight queue (as of compaction)
- CPU (remote_cpu_queue): kappa3_nlo_formula_validation_sigma_g_v1_n4096, kappa3_nlo_..._v2_per_pattern_lognormal_noise,
  kappa3_noise_convention_sign_distinguisher_v1_n4096, substrate_polynomial_p4_bcm_factorial_rung1_v1_n512,
  + (draining) substrate_trained_mini_lm_readout_fix_nsweep_v1, q_b1_chain_loading_boundary_alpha_L_sweep_v1_n2048,
  nhse_annulus_tau_crit_boundary_v1_n8192.
- GPU (overnight_queue): EMPTY (PP-50 v2+v3 done; capacity-stress, L=10000, kappa3 sigma_g, q_f5-killed all resolved).

## Open threads / next actions
1. **kappa3-NLO v2 additive-on-patterns**: script BUILT
   (exp_kappa3_nlo_formula_validation_v2_additive_on_patterns.py) but NOT shipped (needs a prereg).
   This is the FORMULA-MATCHED convention (per kappa3-NLO 2x drill). Sign positive + shape ∝ exp(sg^2)-1
   confirmed, but raw free-cumulant magnitude OVERSHOOTS the formula ~20x even at N=4096 -> the exact
   kappa_3 NORMALIZATION the formula uses is an OPEN Q routed to Research. Ship when CPU has room.
2. **kappa3 3-convention sign map** (for cap_map sub-property, Orchestrator/Research synthesize):
   v1=additive-on-W->NEG; v2-lognormal=per-pattern->POS coeff~6; v2-additive-on-patterns->POS coeff~3 (formula);
   sign-distinguisher = back-to-back A(additive-W) vs B(additive-patterns).
3. **PP-50 N-sweep (TW vs Hadamard)**: RESOLVED. v2/v3 sigma_sep was unstable (near-zero k3_base denom).
   Research replied (notes/research_pp50_metric_reformulation_lambda1_power_iteration) with a stable
   observable = largest eigenvalue lambda_1 via power iteration; PRIMARY=std(lambda_1) across seeds.
   Built+shipped **pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu** (overnight_queue). Remote GPU smoke:
   std(l1) monotone, beta_std=0.700 = Tracy-Widom HARD_PASS, numerically STABLE. Awaiting full-grid verdict.
4. **Polynomial-p=4 modern-Hopfield (Q3 GREEN)**: factorial SHIPPED
   (substrate_polynomial_p4_bcm_factorial_rung1_v1_n512: p2/p4 x cumulative/episodic E=200). If it
   HARD_PASSes, the FULL primitive engineering remains (extend SubstrateCharLM: polynomial-p retrieval
   + episodic write mode + PROT-022 Lyapunov self-test + compatibility tests on PP-12/Q-A3 composition,
   deletion-cert, PP-50 drift). Joint D+H scaffold (exp_substrate_joint_dh_brain_correct_rung1_v1_n4096)
   is the reusable base (continuous float32 + cf-RPE + calibrated readout).
5. **Depth-ladder is STOPPED** (routing_redirect_depth_to_capacity_stress_test). Do NOT ship more Q-A3
   ladder rungs. Capacity-stress was the redirect (shipped, done).

## Key Research answers applied this session (Q1/Q2/Q3 + clarification)
Q1: keep v1+v2 as sign discriminator. Q2: PP-50 observable = sigma_sep(N) scaling exponent (but metric
unstable -- see thread 3). Q3: GO on polynomial-p=4; episodic E=200 hard-reset W/cf-RPE/capacity, LM
state preserved; extend SubstrateCharLM; minimal compat tests for factorial, full after HP.

## Tools added this session
tools/_read_verdicts.ps1 (verdict+queue dump), tools/_check_llm_brain_queued.ps1, tools/_kill_qf5_reroute.ps1,
tools/_check_pp50_runner.ps1. gen_qa3_scripts.py edits per cycle.

**END.** Next: ship kappa3-NLO v2-additive-on-patterns (write prereg first); await Research metric spec
for PP-50 + the kappa_3 normalization Q; watch the factorial verdict for the polynomial-p path.
