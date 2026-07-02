# Pre-registration: substrate_activity_energy_confidence_signal_v2_extended

**Filed:** 2026-07-02 (post-v1 MIDDLE_BAND landing; USER auth "if the confidence signal landed MB, let's explore that more -- that is not a small deal")
**Anchor:** `substrate_activity_energy_confidence_signal_v2_extended`
**Cell:** `experiments/exp_substrate_activity_energy_confidence_signal_v2_extended.py`
**Author role:** hdi_exp_dev (extension of Option C — orthogonality push toward HP band)

## Framing

v1 landed MIDDLE_BAND at 3-seed FULL: `dE=0.550 sJ=0.429 rn=0.513 cb=0.571` (COMBINED=0.571 beat best individual 0.550 by 0.021 — small orthogonality dividend).

**Key insight from v1:** individual activity signals were weak (0.505-0.576) but COMBINED was above chance. Adding MORE orthogonal signals should push combined AUC toward HP (0.65) threshold. Brain analog per USER's cortex-primitive discussion + Kool 2018: PFC integrates multi-dimensional signals (metabolic effort, ACC signal, PFC prediction error, dopamine tone). No single signal is a great uncertainty predictor; the combination is.

**v2 extends v1** with 3 new activity observables from distinct physical bases:
- ΔE (energy change) — v1, retained
- σ_max(J) (retrieval stability) — v1, retained
- **TEMP_ENTROPY** (NEW) — Shannon entropy of softmax over KB; brain analog: PFC-predicted entropy of cortical response
- **MULTI_SAMPLE_VOTE** (NEW) — 5 query perturbations; top-1 disagreement fraction; brain analog: trial-to-trial consistency
- **RECONSTRUCTION_ERR** (NEW) — ‖cleanup(cleanup(q)) - cleanup(q)‖²; brain analog: predictive-coding second-order error

## Prior-work check (substrate-KB concept-query 2026-07-02)

`bash tools/substrate_query.sh "activity energy confidence signal Jacobian entropy multi-sample reconstruction combined"` — top hit cosine=0.296 (active-inference-loop convergence-count note; different mechanism). v1 anchor NOT in top-5 (as expected — anchor filename won't cross char-trigram cosine 0.30). **No prior arc extending v1 combined-5 at cosine>0.30.** Genuine novel extension of v1's orthogonality insight.

## Regime (same as v1 to enable direct comparison)

- `N = 8192` (substrate dim)
- `n_items = 3600` (60 clusters x 60 items)
- `INTRA_COS = 0.35` (reframed regime; h4-harness empirically dead)
- `p_target = 0.40` (contamination fraction)
- `TOPK = 10`
- `n_queries_per_seed = 400` (200 pos + 200 neg; 200 train + 200 test)
- `seeds = [7, 17, 23]` (3-seed FULL for direct v1 comparison)
- `beta = 8.0` (dense-Hopfield softmax inverse-temperature)
- Multi-sample perturbation: 5 samples, σ_pert = 0.30 (tuned at smoke: σ=0.05 was degenerate on N=4096 unit sphere — all 5 perturbed queries collapsed to same top-1, VOTE arm produced constant zeros. σ_pert=0.30 produces non-trivial angular disagreement while queries remain "near" original)

## Arms (7 — v1's 4 + 3 new observables)

- **ARM_DELTA_E** — v1 retained; risk = ‖cleaned - q‖²
- **ARM_SIGMA_J** — v1 retained; risk = σ_max(J) via 5-step power iteration
- **ARM_TEMP_ENTROPY** (NEW) — risk = -Σ p_i log p_i over the softmax distribution p = softmax(β sims). Higher entropy = more spread = more uncertain retrieval. Formula MEASURED@run-code.
- **ARM_MULTI_SAMPLE_VOTE** (NEW) — perturb q by ε~N(0, σ_pert² I) for 5 samples; compute top-1 index per sample; risk = 1 - (max_freq_top1 / 5). Higher disagreement = less consistent retrieval.
- **ARM_RECONSTRUCTION_ERR** (NEW) — cleaned1 = K^T softmax(β K q); cleaned2 = K^T softmax(β K cleaned1); risk = ‖cleaned2 - cleaned1‖². Higher = attractor unstable = less confident.
- **ARM_ABLATED_RANDOM** — negative control; uniform random per query
- **ARM_COMBINED_5** (LOAD-BEARING) — logreg on [ΔE, σ_J, TEMP_ENTROPY, VOTE, RECONSTRUCTION] fit on train half

## Discriminator

Per-arm AUC on test half (rank-based; matches v1). Contaminated label = 1 iff any injected-false-fact index in top-K of aug-KB sims for that query.

## Bands (extending v1 bands to combined-5)

Primary discriminator = ARM_COMBINED_5 AUC on test half (3-seed mean).

- **HARD_PASS**: ARM_COMBINED_5 AUC_mean ≥ 0.65 AND ARM_ABLATED_RANDOM in [0.42, 0.58] AND cv(COMBINED_5) ≤ 0.10. Optional bonus: at least one individual signal ≥ 0.60.
- **MIDDLE_BAND**: ARM_COMBINED_5 AUC_mean in [0.55, 0.65] (matches or slightly beats v1's 0.571)
- **HARD_FAIL**: ARM_COMBINED_5 AUC_mean < 0.55 (adding signals doesn't help; substrate-activity has structural floor)

**Interpretation table:**
- HP: Confidence-Header primitive CG-eligible; M3 cortex can build on it. Reopens confidence architecture with fully-working multi-signal corner.
- MB: 5-signal combiner marginally-better-than-2; substrate-activity is real but bounded; consider Bayes-floor argument for dynamical class next.
- HF: 5 orthogonal activity observables all near chance individually; substrate ACTIVITY class joins graveyard as fully-explored.

## Prognosis (per orthogonality argument)

v1 combined-2 delta over best individual: 0.021. Under IID lift assumption of +0.02 per orthogonal signal, expected combined-5 ≈ 0.571 + 3*0.02 = 0.63.

- P_CG (HARD_PASS) = 0.35-0.45 (higher than v1's 0.30 given orthogonality evidence; still bounded by v1's individual-signal ceiling ≈0.60)
- P_MB = 0.35
- P_HF = 0.20 (redundant-signals-collapse-to-best-individual scenario)

HYPOTHESIZED@this doc. Actual outcome depends on signal correlation structure (may be more or less independent than assumed).

## Compute architecture

**(a) batched-GPU / batched-CPU-torch** — matmul-heavy per-query. Load estimates for FULL (400 queries × 3 seeds = 1200 units on the 7-arm loop):

- Cleanup pass 1: (400, 8192) @ (8192, 3600) = (400, 3600) — matmul
- Cleanup pass 2 (for RECONSTRUCTION arm): repeat above on cleaned — matmul
- Power-iteration for σ_J: 5 steps × 2 matmuls per query (batched) = 10 matmuls
- MULTI_SAMPLE: 5 perturbed cleanup passes = 5 matmuls of size (400, 8192) @ (8192, 3600)
- TEMP_ENTROPY: elementwise on existing p distribution (free — reuses cleanup pass 1's p)

Per-seed wall on GPU: ~5-10s; 3 seeds total ~30s. On CPU-torch: per-seed ~2-5 min; 3 seeds ~10-15 min.

**FULL routing:** `remote_cpu_queue` (per USER 2026-07-01 CPU-batched acceptable when GPU queue depth OK); overnight_queue GPU acceptable alternative. exp_dev cannot push — Orchestrator must handle push+dispatch.
**SMOKE routing:** `local_cpu_queue` (per USER 2026-07-01 smoke-only-local).

**Storage strategy:** no_storage (retrieval-only cell; no compositional storage of items). SHARDED_STORAGE_DEFAULT not applicable.

## Multi-seed smoke gate (Skunkworks META_RULE_smoke_single_seed_inflates_AUC 2026-07-02)

**Mandatory 3-seed variance probe at reduced regime BEFORE FULL:**
- SMOKE seeds = [1, 2, 3] at N=4096, items=1200, N_Q=25 per side (50 total)
- Reject FULL if 3-seed smoke ARM_COMBINED_5 AUC < 0.55 (chance-band)
- Reject FULL if ARM_ABLATED_RANDOM AUC not in [0.35, 0.65] over 3 smoke seeds

## SCHEMA-VET pre-dispatch fields

```yaml
arms_differ_verified: true
final_metrics_atomicity: "tmp_replace"
cardinality_ok: true  # EXPECTED_N_UNITS = 7 arms * 3 seeds = 21
per_unit_failure_class_instrumentation: true
discriminator_fires_gate: true  # ARM_ABLATED_RANDOM baseline in [0.42, 0.58] chance-band
baseline_in_band: true
strictly_above_floor: true  # HP band 0.65 vs floor 0.55 (10-pt margin > 5% band-width)
hp_scope:
  ARM_DELTA_E: [activity_signal]
  ARM_SIGMA_J: [activity_signal]
  ARM_TEMP_ENTROPY: [activity_signal]
  ARM_MULTI_SAMPLE_VOTE: [activity_signal]
  ARM_RECONSTRUCTION_ERR: [activity_signal]
  ARM_COMBINED_5: [combined_gate_LOAD_BEARING]
  ARM_ABLATED_RANDOM: [control_sanity_only]
calibration_check: "default_ok_for_this_regime"  # beta=8; sigma_pert=0.05 fixed
crlb_n_a: "AUC discriminator; multi-signal Bayes-floor argument not yet closed-form for dynamical mixed class"
discriminator_reachability: true
discriminator_survives_scale: true
cell_chunked: false  # 7-arm 3-seed loop within cell; 21 units well within single-cell budget
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false  # cell wall <20min; heartbeat exempted per §13
defensive_error_checking: "passed_start_marker+crash_diagnostic; heartbeat_exempted_short_wall"
progress_logging: "print_flush_true"
composition_edges: []  # single-cell orthogonality probe; not composing prior CG
positive_control_arms:
  - arm: ARM_ABLATED_RANDOM
    primitive: uniform_random
    tolerance: 0.08
    if_outside: HARD_FAIL_CONTROL_BROKEN
sweep_alignment_verdict: N/A
discriminating_fraction: 1.0
functional_requirements:
  - "detect contamination via substrate-activity observables (5 orthogonal channels)"
  - "verify each individual signal has non-trivial AUC (>= chance)"
  - "verify COMBINED_5 beats best individual by >= 0.03 AUC (orthogonality lift)"
  - "test whether 3 new signals produce independent lift beyond v1's combined-2"
```

## Grep-check discipline

Cell invokes substrate primitives per activity observable:
1. `softmax(β * K @ q)` — cleanup (used by ΔE, σ_J, TEMP_ENTROPY, VOTE, RECONSTRUCTION)
2. `K^T @ p` — attractor recall (used by ΔE, σ_J, RECONSTRUCTION)
3. Power-iteration matmul chain (σ_J only)
4. Perturbed cleanup passes × 5 (VOTE only)
5. Second-order cleanup (RECONSTRUCTION only)

Grep pattern `matmul|@ K|@ K_t|softmax|entropy|argmax` — expect ≥ 10 hits in run_seed.

## Stage-progression compliance

Stage 3 (higher-function cortex; M3 cortex confidence-routing primitive). NOT Stage 4. NOT a language benchmark.

## Non-blockers

- Do NOT touch v1 cell (comparison baseline)
- Do NOT fire follow-up sub-agents
- Do NOT block on parallel multi-F DAG cell spawn
- If HF: 4th activity observable class atom; substrate-activity class fully explored
- If HP: Confidence-Header primitive CG-eligible; USER decides how to fold into M3 cortex

## Dispatch plan

1. Author cell + pre-reg (this doc)
2. `python -u experiments/exp_substrate_activity_energy_confidence_signal_v2_extended.py --self-test` — formula selftest
3. Dispatch smoke to `local_cpu_queue` via queue_add
4. Verify multi-seed smoke gate (COMBINED_5 >= 0.55; RANDOM in [0.35, 0.65])
5. Report to caller: FULL dispatch to `remote_cpu_queue` (30-min timeout); exp_dev cannot push — Orchestrator handles push+queue_add
6. REMOTE VERIFY post-FULL

## Smoke results (2026-07-02, appended post-run)

3-seed smoke at N=4096 items=1200 N_Q=50 (150 test queries per seed):
- `COMBINED_5` AUC mean=0.663 (seeds 0.620/0.583/0.785; cv=0.133)
- `RANDOM` AUC mean=0.466 (control-fires in [0.35, 0.65])
- `RECONSTRUCTION_ERR` best individual: AUC mean=0.581 → COMBINED_5 lifts +0.082 over best individual (vs v1's +0.021 lift; strong orthogonality dividend)
- `VOTE` AUC mean=0.351 (below chance polarity, but LR combiner uses magnitude via sign learning)
- Multi-seed smoke gate PASSES: COMBINED_5 >= 0.55; RANDOM in band
- Smoke MEASURED@data/exp_substrate_activity_energy_confidence_signal_v2_extended/metrics.json (post-smoke; will be overwritten by FULL)
- Metrics.json file was overwritten by direct smoke invocation (not via queue_add); FULL dispatch will replace it. Smoke evidence preserved in this pre-reg + selftest+smoke report.

Wall time: 2.47s CPU-torch for 3-seed smoke; FULL projected ~50s CPU-torch (16x more matmul work vs smoke). Comfortable under 30-min timeout.

Regression-to-mean caveat: seed 3 (0.785) is a lucky-draw outlier; seeds 1+2 average 0.601. Estimated FULL COMBINED_5: 0.55-0.62 range (likely MB with real +0.02-0.04 lift vs v1). HP outcome (>=0.65) possible if regression is small.

## References

- experiments/exp_substrate_activity_energy_confidence_signal_v1.py — v1 base + KB/injection functions
- data/exp_substrate_activity_energy_confidence_signal_v1/metrics.json — v1 MEASURED baseline
- preregs/2026-07-02_substrate_activity_energy_confidence_signal_v1.md — v1 pre-reg
- notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md — Option C rationale
- Kool et al 2018 J Neurosci — PFC metabolic-effort tracking (CITED)
- Shenhav et al 2013 Neuron — EVC theory (CITED)
- Skunkworks META CG 2026-07-02 — `META_RULE_smoke_single_seed_inflates_AUC`
- USER 2026-07-02 spawn auth: "if the confidence signal landed MB, let's explore that more — that is not a small deal"
