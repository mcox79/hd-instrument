# Pre-reg: R7 prioritized-replay with CLOSED-LOOP SURPRISE priority

anchor_name: `wave14c_r7_surprise_closedloop_replay_v1`
script: `experiments/exp_wave14c_r7_surprise_closedloop_replay_v1.py`
date: 2026-07-17
author: hdi_exp_dev
queue target: overnight_queue (GPU-preferred; dense 4096x4096 W) or remote_cpu_queue (fallback)

## Question
Was R7's FALSIFICATION of prioritized replay (static Hebbian-MIR / concept tag LOST to uniform
random replay on this BSC delta-rule substrate) SIGNAL-specific (collapsed static tag) or
ARCHITECTURE-general (the rank-1 Hebbian delta-rule cannot benefit from ANY priority-replay signal)?

Test the ONE distinct thing not yet measured: a CLOSED-LOOP surprise priority re-scored against the
CURRENT W each epoch (Schaul et al. 2015 Prioritized Experience Replay analog; PER beat uniform on
41/49 Atari because priority = a re-scored TD-error, not a frozen tag). CITED@Schaul2015 arXiv:1511.05952.

Prior context (CITED@notes/wave14c_random_replay_mechanism_research.md): random replay in this substrate
is an implicit subspace projection (A-GEM with a uniform reference set); the note predicts random > any
priority because non-uniform sampling biases the constraint-set estimator. That was measured only for
STATIC tags + MIR (which collapses to cosine-to-batch in a rank-1 rule). A re-scored closed-loop signal
is a DISTINCT sampling rule -> this is a genuine, decisive can-fail test of that prediction.

## Design (ONE variable = Phase-B replay SELECTION rule)
Reuses exp_wave14b_r7_multiseed.py infrastructure verbatim (corpus = repo .md files ~64KB, BSC atoms,
rank-1 delta-rule, Phase-A -> Phase-B shuffled-corpus continual shift, ALPHA-mixed retrieval eval).

Arms (all from the identical W_A / pool / corpus / seed):
- `no_replay` -- do-nothing Phase-B; bwt_no reference for recovery.
- `random_replay` -- uniform sample from pool. THE HEAD-TO-HEAD BASELINE (real, not strawman).
- `surprise_closedloop` -- priority ~ (surprise|current W)^0.6, re-scored each epoch. MECHANISM.
- `surprise_static` -- priority ~ (surprise|W_A)^0.6, FROZEN at Phase-A end. CONTROL isolating the
  closed-loop re-scoring property (a static-tag reproduction of R7's collapse holding signal TYPE fixed).

surprise_i = 1 - reciprocal_rank(true_target_i | ctx_i, W). additive_map.score_all analog computed
through the cell's own predict_W readout. High surprise = current model predicts the item worst = the
item being forgotten most ("rehearse what you are forgetting").

## Metric (R7 native BWT recovery)
recovery_X = bpc_a(no_replay) - bpc_a(X). Primary discriminator
delta_cl_vs_random = recovery_cl - recovery_random = bpc_a(random) - bpc_a(surprise_closedloop).
Secondary: delta_cl_vs_static (does re-scoring matter), delta_static_vs_random (reproduce R7 collapse sign).

## Bands (verdict on >=2/3 seeds; seeds=[17,23,31])
- HARD_PASS: delta_cl_vs_random >= +0.10 bpc on >=2/3 seeds. R7 collapse was SIGNAL-specific;
  licenses the full prioritized-consolidation pipeline. HYPOTHESIZED (theory leans against).
- HARD_FAIL: delta_cl_vs_random <= +0.02 bpc (tie/lose within noise) on >=2/3 seeds. The rank-1
  Hebbian delta-rule structurally cannot benefit from priority replay = a REAL architectural wall.
  PRE-SPECIFIED brain-check: biological prioritized replay works because dopamine-gated STDP is a
  THREE-FACTOR / eligibility-trace rule (NOT a simple Hebbian product); the fix is a plasticity-RULE
  upgrade (eligibility traces / three-factor), the next build. Do NOT torture toward pass.
- MIDDLE_BAND: otherwise.
- 5x band gap (0.10 vs 0.02) satisfies META_RULE_L strict-above-floor.

## Design gate (verified at smoke; a vacuous regime auto-demotes to VACUOUS_REGIME at full)
1. REAL baseline: random_replay is a genuine uniform-sample arm (not abstain/blank). By construction.
2. DIFFICULTY-ON: bwt_no < -0.10 (do-nothing damages task A; real forgetting).
3. CAN-FAIL / HEADROOM: recovery_random > 0 (random replay recovers, so priority has room to differ);
   surprise CAN win or tie/lose -> both outcomes reachable.
4. PRIORITY-NONUNIFORM: pool-surprise std > 0.02 AND surprise arm sampled-index total-variation from
   uniform > 1.5x the random arm's; else surprise_replay == random_replay by construction (vacuous).
5. ONE variable: only the pool-sampling rule differs; W_A/pool/corpus/fraction shared. By construction.
6. ARMS-MUST-DIFFER: four Phase-B W hashes pairwise distinct (META_RULE_AF).
NOTE: a small smoke delta is CONSISTENT with the theory-predicted HARD_FAIL and is NOT grounds to reject
the full run. Smoke proves the cell is a VALID can-fail test, not the verdict sign.

## Schema-vet fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_selections = 3 * 4 = 12 (full). Verdict counts per_seed.
- final_metrics_atomicity: tmp_replace.
- arms_differ_verified: true (self_test + per-seed hash gate).
- crlb_n/a: bpc/BWT has no closed-form noise floor; bands anchored to R7 MEASURED random recovery
  (+0.66 bpc @ N=4096/15ep) CITED@notes/wave14c_random_replay_mechanism_research.md.
- baseline_in_band analog: forgetting non-trivial AND random-recovery non-saturated (smoke-checked).
- calibration_check: default_ok_for_this_regime (PER_ALPHA=0.6 standard Schaul; verified non-uniform sampling).
- discriminator survives scale: smoke reports headroom + arm separation at N=2048/6ep; full N=4096/15ep.
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- cell_chunked: false (3 seeds in one cell; CPU/GPU-cheap, seed loop; single-seed loss acceptable at pilot).
- defensive_error_checking: passed_all_4_patterns (start marker, crash metrics, heartbeat, no bare except).
- real_code_path: self_test runs train_phase_a/train_phase_b(all 4 selections)/pool_surprise/eval_bpc @N=64.
- deterministic seeding: fixed int seeds + torch.Generator(seed); no hash()-seed, no list(set()).
- Compute architecture: MIXED (batched matmuls; epoch loop sequential by online-CL dependency). GPU-preferred.
- Storage strategy: no_storage / no_composition (continual-learning training loop, not a retrieval chain).

## Functional requirements
- Continual retention under distribution shift -> replay (existing R7 pool + interleave).
- Priority signal that tracks current forgetting -> closed-loop surprise via predict_W reciprocal-rank.
