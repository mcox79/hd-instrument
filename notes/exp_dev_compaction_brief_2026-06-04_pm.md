# Exp-Dev compaction brief -- 2026-06-04 PM (READ FIRST after context reset)

## Role + scope
Exp-Dev session (4-session arch: Orchestrator + Exp-Dev + Research + Testbed). I ship experiments
(build -> smoke/self-test -> queue_add -> verify). Route DIRECTLY to me. I do NOT interpret verdicts
(read data/exp_<name>/metrics.json for COMPLETION STATUS only). Cadence: 30-min wakeups, ship from newest
Research handoffs/routings/change-requests To: Exp-Dev; skip if both queues pending>=5; no padding; smoke
EVERY ship (caught real bugs at smoke all session).

## Infra cheat-sheet
- remote marsh@home = Windows/PowerShell; runner repo C:\dev\hd-instrument; queues data\<q>\queue.json.
  Local repo d:/AI/hd-instrument. Metrics at data/exp_<anchor>/metrics.json (exp_ prefix).
- Remote python: C:\dev\hd-instrument\.venv\Scripts\python.exe (-X utf8). 'tail'/';'-chaining are unix-isms
  that break in remote cmd -> use .ps1 files or powershell -Command.
- queue_add.sh <queue> <name> <script> <prereg> <timeout> [--rerun-as <new> | --allow-duplicate].
  PROT-019 timeout floor: 21600 for _n>=8192, 14400 for _n4096. swept-N anchors: name as _N1_N2 (NO _n prefix).
- ROUTING-SANITY GATE now live in queue_add.sh: REJECTS numpy(no torch)->overnight_queue(GPU); WARNs
  numpy+large-N-grid(>=16384)->CPU. (Added after q_f5 + mini_lm incidents.)
- No cancel/requeue tool: cancel = kill python subprocess by cmdline + the runner auto-marks failed.
- get_output_dir() does NOT mkdir -> add out_dir.mkdir(parents=True,exist_ok=True) before manual per-cell writes.

## CURRENT IN-FLIGHT (at compaction)
- CPU running: substrate_trained_mini_lm_readout_fix_nsweep_v2_capped (started 14:45; ~2h more; finishes
  ~18:00 under the 4h/14400s timeout; per-cell checkpointed; N8192 cells ~50min each = the bottleneck; NOT
  hung, correctly CPU-routed numpy Python-loop class).
- CPU pending: phase05_v1_substrate_audit_core_v1, substrate_alpha_ramp_mct_slowing_v1_n4096,
  substrate_eviction_ecr_vs_lru_v1_n4096.
- GPU: FREE (Llama held -- see blocker). Autonomous wakeup armed ~16:10 to feed GPU from backlog.

## *** LLAMA BLOCKER -- DO NOT RE-QUEUE until Testbed confirms ***
phase05 Llama-3.2-1B residual extraction (Testbed's script) fails at tokenizer.from_pretrained with 401
gated-repo. ROOT CAUSE (fully diagnosed, cycle 66): the runner's HF_TOKEN env var = hf_ulw... (WRONG,
unlicensed) OVERRIDES the correct .hf_token file = hf_KHX... (licensed). The script's _load_hf_token() reads
env FIRST. Testbed's verify_runner_llama_access.py PASSES (reads the file), masking it. Surfaced in
notes/exp_dev_to_testbed_phase05_llama_v5_ENV_TOKEN_OVERRIDES_FILE_2026-06-04.md (fix: align env / unset env /
make script prefer file). User instruction: on issues, note Testbed + tell user + WAIT. So: HOLD Llama; when
Testbed sends a new testbed_to_exp_dev_*ready_to_queue* / *resolved* note, re-verify access then queue v6.
Three prior blockers already cleared: import-crash (v3 patch), datasets-missing (I pip-installed datasets
4.8.5 cycle65), v3 stage-logging in place. Only the env-token precedence remains.

## When Llama DOES produce the npz
Run the Exp-Dev substrate-side core on REAL residuals: re-queue phase05_v1_substrate_audit_core_v1 with env
HDLAB_RESIDUAL_NPZ pointed at the npz (rerun-as a _real variant). The core (Algorithm1 + kappa3-drift z-test
+ deletion-cert) is built + validated on synthetic; refusal-cert deferred (needs refusal-labeled probes from Testbed).

## SESSION WINS (completed/validated)
- HIERARCHICAL 5-CORPUS AGGREGATOR: HARD_PASS at full N=2048 (H3_agg 2.598 vs specialist 2.561 vs cross-domain
  6.196, deletion retention 1.002). Flagship "parallel sub-models -> substrate meta-aggregator" works at scale.
- alpha-ramp/MCT: smoke HARD_PASS (graceful->catastrophic capacity curve + 10.3x MCT critical-slowing free
  early-warning) -- running on CPU.
- Completed GPU: Bundle E (posbind trigram), finer-N spectral arbiter, resonator dense K-sweep, Bundle G
  (ext-context ceiling), cf-RPE+STDP superadditive, n-threshold sweep (flat -> no threshold), PP-50 v4.
- Structural: queue_add routing-sanity gate; mini_lm v1 mis-route fixed (v2 capped+per-cell-checkpoint).

## BACKLOG (high-priority, next builds)
- cross_domain anchor 3: orthogonal vs random domain keys capacity (CPU/numpy).
- change_request_mode4_resonator_add_sparse_noise_injection_cells (GPU; extends resonator).
- routing_k3_synthetic_uniform_zipf_falsifier_test (CPU).
- change_request_bundle_f_add_iterated_mode_cells.
- exp_dev_handoff_research_position_binding_trigram_corrected_k_star; ..._true_scaling_law_2x.
- CIFAR-10 non-linguistic probe (routing_substrate_cifar10...): needs a MANUAL CIFAR loader -- torchvision is
  ABSENT on the runner venv; would need urllib download + unpickle.
- multimodal_substrate_primitives + unified_cross_modal handoffs (design-stage 2x drills).

## OPEN THREADS / GOTCHAS
- datasets-install side effect: testbed.substrate_lm.data wikitext loader hits HfUriError -> falls back to
  local cache (data OK; experiments run). Could pin datasets or fix the loader if it matters.
- Phase 1a (substrate_drosophila_mb_sparse_single_modulator_v1_n4096, CPU): still not landed (Bundle A
  already HARD_PASSed the architectural question).
- kappa_3 NLO normalization: still unanswered by Research -> kappa3-NLO v2.1 not buildable.
- substrate_position_binding_combined_arch_trigram (Bundle E) script committed; completed on GPU.

**END.** Next after compaction: (1) check CPU mini_lm v2 completion + Llama-v6 readiness (Testbed token note);
(2) feed GPU from backlog; (3) when Llama npz lands, run audit core on real residuals.
