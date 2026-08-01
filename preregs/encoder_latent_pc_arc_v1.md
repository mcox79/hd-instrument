# Pre-registration: encoder-level latent predictive coding (JEPA) on ARC -- rep-quality lever #1

- Anchor: `encoder_latent_pc_arc_v1`
- Cell: `experiments/exp_encoder_latent_pc_arc_v1.py`
- Metrics: `data/exp_encoder_latent_pc_arc_v1/metrics.json`
- Spec source: `notes/encoder_representation_lever_ranking_2026-07-29.md` (lever #1 + section-3 measurement plan);
  founding diagnosis `notes/brain_foundational_component_analysis.md` components 1+2.
- Author: hdi_exp_dev, 2026-07-29. Status: LOCAL build + self-test PASS; FULL held for GPU (queued behind Track-A WM verdict).
- Prior-work check (USER-locked): `substrate_query.sh` top hits cosine 0.37-0.39 are research-DRILL notes
  describing JEPA/predictive-coding conceptually (research_drill_embodied_revival C8, realtime_multimodal_biology,
  fact_representation_rethink). NO prior experiment CELL implements an encoder-level latent-PC objective.
  This is the first BUILD of the concept; NOT a rediscovery.

## Question
Does an encoder-level latent-predictive-coding (JEPA) objective produce a RICHER representation than the
current MLM objective, at MATCHED training budget, judged purely on representation geometry (no WM module)?
This repairs the founding-diagnosis objective gap (static target -> stream/latent prediction) as a standalone
encoder lever, testable independently of and in parallel with the stateful-core WM gate.

## Mechanism (brain-faithful; invariant-respecting)
- JEPA latent prediction (I-JEPA/V-JEPA; Rao&Ballard 1999 / Friston 2005 predictive coding): mask contiguous
  target SPANS; predict the TARGET-span LATENT from the CONTEXT latent via a small predictor MLP. Everything
  stays in d-dim latent space -> OOM-free (NO [B,L,vocab] tensor anywhere; avoids the v5 causal-LM OOM class).
- Collapse guard (REQUIRED per lit): EMA/stop-grad target encoder (SimSiam-style, m=0.996) + VICReg variance
  floor (hinge on per-dim std >= gamma=1.0) + covariance/decorrelation term (off-diag cov -> 0, coef 0.04).
- Base encoder = the v2 TinyTransformer (imported from `exp_scale_meaning_learn_arc_heldout_v2.py`),
  learned from scratch under the latent-PC objective. NO borrowed vectors / LLM / GloVe / BGE anywhere.
- Temporal-contiguity ABLATION arm: wires the ALREADY-BANKED `hdlab/temporal_trace.py` (Foldiak slow-feature
  exponential trace) as a one-variable aux loss -- contiguous window runs form pseudo-documents; the current
  window's pooled latent is pulled toward the running trace of prior windows (slowness). LPC alone vs LPC+TC.

## Arms (matched budget: same tokens/steps/architecture; base-encoder params matched)
- ARM_LPC     : latent-PC alone. PRIMARY.
- ARM_LPC_TC  : latent-PC + temporal-contiguity. ABLATION (reported, not HP-gated).
- ARM_MLM     : current MLM baseline (v2 mlm_train), same steps/tokens/architecture. Known-good reference (29591 baseline 0.56-0.63 band).
- ARM_RANDOM  : random-init encoder (untrained). Floor.

## Independent rep-quality battery (frozen encoder; KB read-only, NEVER a training target)
1. graded_geometry_spearman : Spearman(encoder cosine, KB graded proximity {1-hop=3, 2-hop=2, far=1}) over
   held-out-NEW concepts. THE HEADLINE. Leak-proof (held-out has zero relational input; KB is diagnostic read).
2. heldout_probe_acc : frozen closed-form ridge linear probe (lexname supersense) trained on TRAIN concepts,
   tested on held-out-NEW. Linear + frozen head -> gains attributable to representation, not probe capacity.
3. relational_auc : per-query neighborhood AUC (reuses v2.relational_eval; text-alone arm = this encoder).
4. rep_std + mean_pairwise_cos (frozen-rep collapse witness) + training-time min target-embedding std (VICReg telemetry).

## Pre-registered bands (deflated per lit-scan calibration; section 3 of the ranking note)
- HARD_PASS = ARM_LPC graded_geometry beats ARM_MLM by >= +0.10 AND beats ARM_RANDOM by >= +0.15,
  in >= 1 of 2 seeds with the OTHER seed non-negative, AND held-out probe does NOT regress (>= MLM - 0.01),
  AND NO collapse (rep_std >= 0.02 AND training min_target_std >= 0.05).
- HARD_FAIL_NO_EFFECT = ARM_LPC ties BOTH MLM and RANDOM within +/-0.03 on graded_geometry.
- FAIL_BY_COLLAPSE = rep_std < 0.02 OR training min_target_std < 0.05 (variance collapsed) ->
  distinct diagnosis; mechanism class NOT refuted (retune VICReg/EMA or use --co-scaled).
- HARD_FAIL_UNDERPOWERED = graded-geometry min query count < 40.
- MIDDLE_BAND = real-but-below-band gain.
- ARM_LPC_TC reported as ablation delta (does temporal-contiguity add over LPC alone?).

## Compute architecture
- Class: (a) batched-GPU. Transformer training + batched encode are matmul-heavy; FULL runs CUDA+AMP.
  Local self-test = CPU (tiny). No sequential-CPU dependency.
- Storage strategy: no_storage / no_composition (this is encoder pretraining + frozen-rep geometry; no
  sharded/bundled atom table, no chained retrieval).
- OOM-free by construction: loss lives entirely in d-dim latent space; no vocab-sized logits tensor.

## SCHEMA-VET / cell-template compliance
- arms_differ_verified: True (self-test asserts all 4 held-out rep matrices bit-distinct via SHA-256).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace + per-seed write_partial).
- except-ordering: except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep gate PASS).
- crlb_n/a: this is a representation-geometry comparison (Spearman / probe-acc), not a noise-floor estimator;
  the empirical floor is witnessed by ARM_RANDOM (near-chance geometry) + the no-effect band.
- baseline_in_band: ARM_MLM graded_geometry expected in (0.05, 0.95) (cited 29591 band 0.56-0.63); ARM_RANDOM near floor.
- discriminator_survives_scale: (B) analytical -- the objective gap is architectural (stream vs static target),
  and the battery is NOT saturated: MLM ~0.56-0.63 leaves >0.10 headroom to HP-over-MLM; RANDOM near 0 gives
  >0.15 headroom to HP-over-RANDOM. Self-test at 40 steps is near-chance across arms (expected: proves machinery,
  not discrimination). NO smoke-saturation risk (no arm at ceiling).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (2 at FULL); verdict counts len(per_seed).
- calibration_check: default_ok_for_this_regime -- VICReg gamma=1.0 std-floor + off-diag cov + EMA m=0.996
  are literature-standard defaults; collapse telemetry (target_std per step) is logged so the guard is OBSERVED, not assumed.
- real_code_path: --self-test runs the REAL pipeline (v2 prepare_data + BPE + TinyTransformer + lpc_train +
  mlm_train + full battery) at N~16 tiny scale (SELFTEST_CFG). MEASURED@ self-test 2026-07-29:
  loss descends (pred 0.4419 -> 0.4007 LPC; 0.4402 -> 0.3990 LPC+TC), no collapse (min_target_std 1.0004),
  TC aux fired (tc 0.006-0.008), all 4 arms produced battery numbers, arms bit-distinct, cuda-safety audit params_on_device=True.
- defensive_error_checking: start-marker + crash-diagnostic + heartbeat + no silent except -> passed_all_4_patterns.
- progress_logging: print flush=True per train step + _heartbeat.jsonl (timeout_s >> 1800). REQUIRED (long GPU run).
- cell_chunked: False (per-arm x per-seed loop with per-seed write_partial; single cell handles both seeds).

## CUDA-device-safety (recurring bug class: WM.to(device) then cpu-Generator-used-with-cuda)
- Every module (online / target / predictor) .to(device); EMA target on device.
- EVERY torch.rand/randint/randperm/arange created with device= from ids.device. NO torch.Generator in the hot path
  (numpy default_rng only selects host-side window indices into a numpy array, then .to(device)).
- The ONLY host<->device crossing is the temporal_trace numpy primitive: explicit .detach().cpu().numpy() out,
  torch.from_numpy(...).to(device) back.
- `_cuda_safety_audit()` runs 2 end-to-end LPC+TC steps on the run device (cuda when present) and asserts finite
  loss + all params on-device BEFORE data prep, so the eventual GPU launch fails fast in seconds if a device bug exists
  rather than after the (expensive) data prep. On this CPU box cuda_tested=False; the identical device-routed step ran
  on CPU (params_on_device=True) and the static routing is documented above.

## Capacity-ratio watch
512d over ~130M tokens; SimSiam small-scale sensitivity finding (SCAN 1) says collapse risk is
capacity/data-ratio dependent. `--co-scaled` (d=256, L=4) is a pre-registered follow-up if FULL shows collapse
or over-capacity; the training-time min_target_std telemetry is the early-warning signal.

## Ready-to-launch (HELD for GPU; queued behind Track-A WM verdict)
FULL, GPU (overnight_queue), 2 seeds [7,13], 4 arms:
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_latent_pc_arc_v1 experiments/exp_encoder_latent_pc_arc_v1.py preregs/encoder_latent_pc_arc_v1.md <timeout_s>`

---

## AMENDMENT 2026-08-01: --lite causal-vs-bidir-vs-random SMALL-PROXY bundle (Probe 2a + Probe 3)

Context: `notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md` Part 2
identifies a ONE-axis amendment (masked-bidirectional -> causal next-latent prediction, + hold-then-revise
gate + clause head) as a candidate fix for the measured cross-voice role-INVERSION on the frozen MLM
encoder (`exp_syntactic_role_agent_patient_voice_probe_v1.py`, 0.16-0.18, below chance). The FULL GPU build
is ~15-19 GPU-hrs; this amendment authors a SMALL/SHORT SCALING PROXY (~1-3 GPU-hrs total) to get an early
directional read BEFORE committing to FULL, per the Director's explicit de-risking-ladder brief.

**Prior-work / KB-check (USER-locked 2026-07-01):** `substrate_query.sh "causal predictive coding encoder
role-inversion voice probe scaling proxy"` -> top cosine=0.3564 (`notes/research_learning_control_
neuromodulation_inventory_2026-07-24.md`, general predictive-coding concept), no prior CELL or drill at
cosine>0.30 running THIS specific causal-vs-bidir-vs-random-vs-MLM bundled small-proxy test. Genuinely new
build, not a rediscovery -- consistent with the design note's own KB-check (line 10-13 of that note).

**What changed from the FULL-run arms above:** `--lite` (already existed 2026-07-30 for ARM_LPC_CAUSAL
alone; EXTENDED here) now bundles THREE arms at ONE seed (7), ~10x fewer steps (6000 vs 60000 FULL),
SAME architecture (d_model=512, n_layers=6, n_heads=8, ffn_mult=4, vocab=16000, max_len=128) as FULL:
- `ARM_LPC_CAUSAL` -- already trained+checkpointed 2026-07-30 (`data/exp_encoder_latent_pc_arc_v1_lite/
  ckpt_seed_7_ARM_LPC_CAUSAL.pt`); (seed,arm) checkpoint/resume (Fix 2c) means this dispatch SKIPS
  retraining it (already in `units.jsonl`).
- `ARM_LPC_BIDIR` -- NEW at lite budget: isolates causal-mask-vs-bidirectional-objective (Antonello & Huth
  confound per the design note's "Honest risk read" section).
- `ARM_RANDOM` -- NEW at lite budget: untrained floor control. Code amendment 2026-08-01: `_save_arm_ckpt`
  used to skip ARM_RANDOM ("untrained, nothing to reuse"); it is now saved like every other arm (zero extra
  cost -- the model already exists in memory) because the bundled fair test needs a real FrozenV2Encoder-
  shaped ckpt for the floor arm too.
- `ARM_MLM` intentionally EXCLUDED from this lite bundle: the probe cell's own DEFAULT checkpoint (V2_CKPT,
  the FULL-trained v2 MLM encoder) already IS the measured MLM reference (re-verified fresh this cycle,
  see Fair-test section below) at zero extra GPU cost; retraining an MLM arm at lite (6000-step) budget
  would not even be budget-matched to that existing FULL reference.

**Cost estimate (HYPOTHESIZED@ prior lite run + this amendment):** ARM_LPC_CAUSAL's own 2026-07-30 run
measured 1944s (32.4min) wall for ONE trained arm's train+encode+battery at this config
(MEASURED@`data/exp_encoder_latent_pc_arc_v1_lite/metrics.json:per_seed.7.elapsed_s`). ARM_LPC_BIDIR is
architecturally identical (same steps/d_model/data) -> HYPOTHESIZED comparable ~30-35min. ARM_RANDOM has
NO training loop (untrained model, straight to the rep-battery) -> HYPOTHESIZED faster, ~5-15min (battery
cost only). Total incremental wall HYPOTHESIZED ~35-50min; combined with the 32min already spent on
ARM_LPC_CAUSAL, total project cost for this proxy stays ~65-85min, well inside the 1-3 GPU-hr budget this
amendment is scoped to.

**Timeout:** 5400s (1.5h) on the incremental dispatch -- >3x the HYPOTHESIZED incremental wall, covering
data-prep-bundle-cache-hit overhead (should be a cache HIT per Fix D, keyed on corpus mtime + cfg subset,
already produced 2026-07-30) + queue/runner startup + margin. Per-experiment timeout formula
(`ceil(1.5 * smoke_wall_s * ...)`): smoke_wall_s here = the already-MEASURED 1944s for one arm; two more
arms at comparable-or-lesser cost -> `ceil(1.5 * 1944 * 2) = 5832`, rounded to 5400 is close enough given
ARM_RANDOM's expected sub-linear cost; using 5400s.

**"Moves" pre-registration (what the small proxy is asked to answer, per the Director's brief) --
gated entirely on the SEPARATE, ALREADY-BUILT fair-test cell (`exp_syntactic_role_agent_patient_voice_
probe_v1.py`, path-swapped per-arm via `--ckpt-path`, ZERO new probe code, same HARD-PASS/HARD-FAIL/
PARTIAL bands already pre-registered in that cell (ROLE_PROBE_PASS_MIN=0.70, ROLE_PROBE_FAIL_MAX=0.55,
chance=0.50)):**
- HARD-PASS-DIRECTIONAL (causal genuinely helps): ARM_LPC_CAUSAL cross-voice accuracy (both directions)
  clears the shuffled-control/no-longer-inverted band [0.35,0.65] AND is >= +0.15 above ARM_LPC_BIDIR in
  BOTH directions (isolates causal-mask-specific gain from generic-retrain noise) AND ARM_LPC_BIDIR itself
  stays inverted/near the MLM wall (control did NOT move, so the causal axis specifically is responsible).
- PARTIAL (informative, not a refutation): ARM_LPC_CAUSAL moves toward invariance but ARM_LPC_BIDIR moves
  comparably (confounded -- generic-retrain-at-this-budget effect, not causal-specific) OR ARM_LPC_CAUSAL
  moves only partway (still below 0.35 or between 0.35-0.65 without a clear BIDIR gap).
- NULL-AMBIGUOUS (per the design note's own "Honest risk read," 3rd risk -- MANDATORY framing, do not
  collapse to refutation): if ARM_LPC_CAUSAL's lite training shows COLLAPSE (rep_std < 0.02 or
  min_target_std < 0.05 -- ALREADY the case for the existing 2026-07-30 causal ckpt, rep_std=0.0181
  marginally under the 0.020 floor per `data/exp_encoder_latent_pc_arc_v1_lite/metrics.json`), any
  resulting flat-or-worse cross-voice read is AMBIGUOUS between "causal-mask hypothesis wrong" and
  "insufficient budget at this proxy size causing near-collapse" -- report BOTH readings, do not force one.
- Discriminator-reachability check: chance=0.50 exact-by-construction (binary balanced task, per the probe
  cell's own CRLB-n/a declaration); the wall is measured at 0.16-0.18 (inverted, BELOW chance) so there is
  headroom in BOTH directions (toward 0.50 = no-longer-inverted, toward 0.70 = passing) -- not saturated.

**Data-prep-headroom gate:** N/A for this incremental dispatch -- the dataprep bundle cache
(`dataprep_bundle_4a6982f330d29375.pt`) already exists on disk from the 2026-07-30 run and is keyed by
corpus-mtime + cfg-subset hash (Fix D); this run is expected to HIT the cache (verify in landed metrics
`data_prep_headroom` stays null / cache-hit log line present) and skip data-prep entirely.

**SCHEMA-VET deltas from the FULL-run declarations above (unchanged otherwise):**
- `cell_chunked`: unchanged (per-arm x per-seed loop, single seed here).
- `arms_differ_verified`: re-verified for the 3-arm lite bundle (ARMS-MUST-DIFFER hash check over
  `arm_digests` for whichever arms ran this dispatch, per `run_one_seed`'s existing generic assertion --
  no code change needed, it already iterates `arms_to_run` generically).
- `real_code_path` / self-test: re-run 2026-08-01 after the `_save_arm_ckpt` ARM_RANDOM amendment +
  LITE_ARMS extension; MEASURED@ local CPU self-test this cycle: `[encoder_latent_pc_arc_v1]
  PLUMBING SELF-TEST PASS` + `[encoder_latent_pc_arc_v1] SELF-TEST PASS` (arm-ckpt round-trip now
  covers ARM_RANDOM too).
- `guard_baseline_valid` / control-vs-floor: N/A here (this amendment doesn't add a POP-vs-RANDOM guard;
  the existing lite-verdict gates (`lite_no_collapse`, `lite_clause_descended`, `lite_gate_fired`) are
  UNCHANGED and still apply to ARM_LPC_CAUSAL only, per `build_lite_verdict`'s existing (unmodified)
  logic -- the two new arms are trained/checkpointed/battery-scored but not separately verdict-gated by
  this cell; their DECISIVE read is the probe cell above.

**Companion fair-test cell fixes (2026-08-01, both bugs pre-dated this amendment, caught while wiring the
path-swap):**
1. `os.path.relpath(ckpt_path, REPO_ROOT)` in `exp_syntactic_role_agent_patient_voice_probe_v1.py` main()
   raised `ValueError: path is on mount 'C:', start on mount 'D:'` on every one of 3 prior local
   invocations (cwd resolved to a C: mount at invocation time) -- CELL_CRASHED on a LOGGING-ONLY field.
   Fixed via `_safe_relpath()` (try/except ValueError -> abspath fallback; never blocks a real run over a
   cosmetic drive mismatch).
2. The top-level crash handler wrote to the bare `OUTPUT_DIR` module constant instead of the per-ckpt
   suffixed `out_dir`, so all 3 prior --ckpt-path crash attempts clobbered the SAME base metrics.json
   instead of each landing in its own `__<ckpt-basename>` dir. Fixed via `_resolve_out_dir_from_argv()`
   mirroring main()'s suffix logic from argv, used in the `if __name__ == "__main__"` except-handler.
   MEASURED@ this cycle: re-ran `--full` (default V2_CKPT) FRESH after the fix -> reproduces the
   previously-cited wall cleanly: active_to_passive=0.1792, passive_to_active=0.1625 (matches the
   0.16-0.18 cited in the design note), verdict=ENCODER_POSITION_ONLY, within-voice reference
   {active=0.90, passive=0.85}.

**Runner-dispatch fix (2026-08-01, discovered while wiring this dispatch):** `runner_v2_prod.py`'s
`run_one()` invokes every queued cell as `[sys.executable, "-u", script_path]` with ZERO CLI flags --
only `HDLAB_EXP_NAME`/`HDLAB_RUN_MODE` env vars are injected. A CLI-only `--lite` flag is therefore
UNREACHABLE through `queue_add.sh` -> the standard queue -> runner path (the 2026-07-30 lite run must
have been launched by a direct manual invocation, not through the queue). Fix: `_parse_args()` now
auto-detects lite mode from `HDLAB_EXP_NAME` (`"_lite" in os.environ.get("HDLAB_EXP_NAME","")`) so a
queue entry literally NAMED `..._lite` dispatches into lite mode without needing a CLI flag the runner
can never pass -- **the queue entry name MUST be exactly `encoder_latent_pc_arc_v1_lite`** (not a
distinguishing suffix like `..._lite_bundle_20260801`), because `get_output_dir()` resolves the on-disk
directory from `HDLAB_EXP_NAME` verbatim (SH-4/SH-5 convention) and this run MUST land in the EXISTING
`data/exp_encoder_latent_pc_arc_v1_lite/` dir to (a) resume ARM_LPC_CAUSAL from `units.jsonl` instead of
retraining it, and (b) hit the existing data-prep bundle cache instead of re-running the 2-4h data-prep.

## Ready-to-launch (2026-08-01 amendment)
LITE bundle extension, GPU (overnight_queue), 1 seed [7], 3 arms (1 resumed + 2 new):
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_latent_pc_arc_v1_lite experiments/exp_encoder_latent_pc_arc_v1.py preregs/encoder_latent_pc_arc_v1.md 5400`

---

## AMENDMENT 2026-08-01 (iteration 2): one-variable anti-collapse fix for ARM_LPC_CAUSAL

**MEASURED@`data/exp_encoder_latent_pc_arc_v1_lite/metrics.json` (remote, run 1, 2026-08-01, cuda,
1183s):** verdict LITE_COLLAPSE. Per-arm rep_std -- ARM_LPC_BIDIR=**0.0248** (ABOVE 0.020 floor, trained
clean), ARM_LPC_CAUSAL=**0.0128** (BELOW floor, barely above ARM_RANDOM=**0.0121**), with a HEALTHY EMA
target on the causal arm (min_target_std=**0.966**). Causal final_pred_loss=0.182 vs bidir 0.084.
**Read:** the budget is ADEQUATE (bidir trained clean at it); the causal arm UNIQUELY collapses -- an
ONLINE-encoder representation collapse (low online rep_std, healthy target) = the textbook JEPA/BYOL/
SimSiam collapse mode, NOT an encoder-hypothesis refutation. We cannot read causal-de-inversion off a
collapsed encoder, so the probe on run-1's causal ckpt (active/passive 0.0167/0.0167, further inverted)
is UNINTERPRETABLE for the hypothesis (it reflects the collapse, not the causal mask's effect).

**One-variable fix (single knob, causal-only):** DOUBLE the VICReg variance-term weight for the causal
arm, `lpc_var_coef` 1.0 -> `lpc_var_coef_causal`=**2.0** (used in `lpc_train` only when `causal=True`).
Everything else held IDENTICAL: architecture (d=512/L=6/H=8), budget (6000 steps), tokens (9M), LR
(3e-4), warmup, mask_frac, EMA m, clause/gate coefficients, seed (7). Why THIS lever, not the other two
offered:
- vs lower peak LR / longer warmup: ARM_LPC_BIDIR is CLEAN at the SAME LR/warmup/budget -> LR/warmup are
  demonstrably adequate for this arch; lowering LR treats a non-cause and would slow useful learning,
  risking under-training rather than fixing the collapse mechanism.
- The VICReg variance hinge (`relu(gamma - std).mean()`, gamma=1.0) is the literature-standard
  anti-collapse term (Bardes VICReg 2022); doubling its weight directly and specifically opposes the
  measured symptom (per-dim std below floor). Conservative single step (2x, not 5x).
Causal-only keeps the causal-vs-bidir contrast one-variable-clean AND leaves the resumed BIDIR/RANDOM
arms byte-for-byte untouched. `lpc_var_coef_causal` is NOT in `_DATA_CFG_KEYS` -> data-prep bundle cache
key unchanged (cache HIT preserved). Effective var_coef is now recorded per-arm in
`train_diag.var_coef` for landed verification.

**Retrain mechanics (retrain ONLY causal; reuse BIDIR/RANDOM ckpts + data-prep cache):** on remote
`C:/dev/hd-instrument/data/exp_encoder_latent_pc_arc_v1_lite/`, backed up `units.jsonl` ->
`units.jsonl.pre_causal_retrain_bak`, removed the `7|ARM_LPC_CAUSAL` unit line + deleted
`ckpt_seed_7_ARM_LPC_CAUSAL.pt` (kept `7|ARM_LPC_BIDIR`, `7|ARM_RANDOM`, both `.pt` ckpts, and
`dataprep_bundle_4a6982f330d29375.pt`). Re-dispatched the SAME entry name via `--allow-duplicate` (resets
the terminal entry to pending). On the runner: data-prep cache HIT, BIDIR RESUMED, RANDOM RESUMED, CAUSAL
retrains with var_coef=2.0 -> writes a fresh `ckpt_seed_7_ARM_LPC_CAUSAL.pt`.

**GATE before probing:** confirm the retrained ARM_LPC_CAUSAL rep_std >= 0.020 (clears the collapse
floor) in the landed metrics BEFORE running the voice-role probe. If it STILL collapses at var_coef=2.0
(same budget), STOP -- do NOT silently escalate budget or stack knobs; report + recommend the MINIMAL
budget bump (still <<15h) as the next single lever.

**Re-dispatch command:**
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_latent_pc_arc_v1_lite experiments/exp_encoder_latent_pc_arc_v1.py preregs/encoder_latent_pc_arc_v1.md 5400 --allow-duplicate`

---

## AMENDMENT 2026-08-01 (iteration 3): probe-crash fix + minimal budget bump (LAST cheap proxy iteration)

**MEASURED@remote run-2 (var_coef=2.0):** ARM_LPC_CAUSAL rep_std 0.0128 -> **0.0180** (monotone better,
var_coef confirmed =2.0 in train_diag) but STILL under the 0.020 floor -> verdict LITE_COLLAPSE persists.
BIDIR rep_std=0.0248 (var_coef=1.0, unchanged/resumed), RANDOM=0.0121. The armed gate CORRECTLY blocked
probing (poll log: `GATE_FAIL causal_rep_std=0.0180 -- STOP, do not probe a collapsed encoder`).

**Fix 1 (BLOCKING -- probe CELL_CRASHED root-cause):** the probe crashed on ARM_LPC_BIDIR + ARM_RANDOM
(and produced no causal cross-voice number) at `check_arms_differ` -- an `assert digests[ka] != digests[kb]`
(META_RULE_AF) fired because the two cross-voice DIRECTIONS of the SAME method (`role_probe`) produced
BIT-IDENTICAL digests for these degenerate/undertrained lite encoders. That is a MEASURED encoder-
degeneracy property (both directions collapse to the same prediction), NOT a code bug -- the bagofwords
pair is already declared identical-by-design in ARMS_DIFFER_EXEMPTED for exactly this reason; META_RULE_AF's
real target is a cross-METHOD arm-implementation collision. The assert crashed the cell AFTER computing the
numbers, discarding them. **Fix:** `check_arms_differ` is now NON-FATAL + classifying -- same-method
cross-direction collisions are recorded as `direction_degenerate_collisions` (informative, does not flip
`arms_differ_verified`); only cross-METHOD collisions are `suspicious_collisions` (loud flag,
`arms_differ_verified=False`) and even those no longer crash -- metrics are ALWAYS written so the cross-voice
numbers are readable. MEASURED@ local re-run on the EXISTING lite ckpts after the fix:
- **ARM_LPC_BIDIR (baseline): active_to_passive=0.000, passive_to_active=0.000** (FULLY inverted; within-voice
  ref ~0.996/1.0) -- verdict ENCODER_POSITION_ONLY.
- **ARM_RANDOM (floor): active_to_passive=0.000, passive_to_active=0.000** (fully inverted) -- ENCODER_POSITION_ONLY.
- (frozen MLM reference, unchanged: 0.179/0.163.) So at lite budget BIDIR and RANDOM both FULLY invert,
  worse than the frozen full-budget MLM's 0.16-0.18 -- the bidir baseline + random floor are now in hand.

**Fix 2 (persistent marginal collapse -- ONE new variable):** minimal budget bump, `lite_causal_steps_mult`=2.0
= causal arm optimizer steps 6000 -> **12000**, LITE-ONLY + CAUSAL-ONLY. var_coef=2.0 KEPT (now-standard, not
a new variable this round). Tokens/data UNCHANGED (train_token_budget stays 9M -> data-prep cache HIT
preserved; more steps = more epochs = the standard escape from the cell's own "undertrained" diagnosis). NOT
cranking var_coef further (avoid over-regularizing). BIDIR/RANDOM resumed byte-untouched. Budget-asymmetry
caveat (causal 12k vs bidir 6k at lite) ACCEPTED for the proxy: goal is a NON-COLLAPSED causal encoder to READ
at all; if it de-inverts, matched-budget FULL is the real confirmation; if it still just inverts, that is
itself informative. Stays in the ~2-4 GPU-hr class (run-1 all-3-arms = 1183s; causal-only at 2x steps ~
20-35min).

**GATE (fixed + confirmed working):** poll checks retrained ARM_LPC_CAUSAL rep_std >= 0.020 BEFORE any probe;
if it STILL collapses at 2x steps + var_coef=2.0, STOP -- do NOT iterate further (no 4th tweak). Report the
persistent collapse as the honest go/no-go signal: the causal objective is training-stability-costly at small
scale; a clean read needs the fuller build budget.

**Re-dispatch command (iteration 3):**
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_latent_pc_arc_v1_lite experiments/exp_encoder_latent_pc_arc_v1.py preregs/encoder_latent_pc_arc_v1.md 5400 --allow-duplicate`

---

## AMENDMENT 2026-08-01 (iteration 4): OBJECTIVE PIVOT -- brain-faithful collapse-free objective (USER-approved)

**iter-3 one-liner (last old-objective datapoint):** the 2x-steps (12000) old-objective run CRASHED on a
config bug I introduced (an earlier edit accidentally dropped the `**_LPC_COMMON` spread from `LITE_CFG`
-> `KeyError: lpc_pred_hidden_mult` at predictor init; now fixed + guarded by self-test). So NO clean
2x-budget-alone rep_std datapoint was obtained. Valid old-objective datapoints stand: EMA+VICReg causal
rep_std = 0.0128 (var_coef 1.0) and 0.0180 (var_coef 2.0), both at 6000 steps, both < 0.020. Per the
objective-pivot directive (which SUPERSEDES the budget-bump path) I am NOT separately re-running the 2x
old objective; the new run retrains ARM_LPC_CAUSAL (EMA+VICReg, var_coef 2.0) at 6000 steps as the
in-run baseline reference (expected ~0.018).

**Source:** `notes/research_brain_faithful_collapse_free_predictive_encoder_objective_2026-08-01.md`
(3-way lit-scan drill). ROOT CAUSE of the collapse: the EMA self-distillation target co-adapts with the
student (degenerate constant fixed point), fragile at small model/batch scale; VICReg's variance HINGE is
a weak small-batch repulsion. Cortex predicts a REAL externally-grounded next signal (Rao&Ballard 1999;
Friston) and decorrelates STRUCTURALLY (Barlow redundancy-reduction / lateral inhibition). The more
brain-faithful choice is also the more collapse-robust one.

**WHAT CHANGED (new causal training path `causal_realtarget_train`, drill RANK 1 + RANK 3):**
- RANK 1 (target): regress the ACTUAL next-span token's OWN INPUT EMBEDDING (real, data-determined, own
  entropy). DROP the EMA target encoder + self-distillation loop. Keep the d_model->d_model predictor head
  (STILL OOM-safe; `_assert_no_vocab_dim` fires on the real call). CITED@ arXiv:1902.11269. A constant
  output cannot match varying real targets -> collapse cause removed, not fought.
- RANK 3 (regularizer): replace VICReg variance+covariance with `_barlow_decorrelation` (cross-
  correlation-to-identity: diagonal->1 = unit variance/anti-collapse, off-diagonal->0 = decorrelation).
  CITED@ Zbontar 2021 "does not rely on batch size"; most small-batch-robust + most brain-faithful.
- Regularizer applied to the ENCODER latents zc (the measured representation) for BOTH reg modes (clean
  attribution); for real_emb ALSO to the live tok_emb targets (guards the "mildly self-referential"
  learned-embedding weak point the standard regress-to-embedding way).

**ARMS (all trained fresh at the SAME cheap 6000-step budget where EMA+VICReg collapsed; one seed 7):**
- ARM_CAUSAL_REAL_BARLOW -- PRIMARY (full brain-faithful package: real target + Barlow).
- ARM_CAUSAL_REAL_VICREG -- attribution (a): isolates the TARGET change (real vs ema), reg held = vicreg.
- ARM_CAUSAL_EMA_BARLOW  -- attribution (b): isolates the REGULARIZER change (barlow vs vicreg), target held = ema.
- ARM_LPC_CAUSAL (old EMA+VICReg+clause+gate, var_coef 2.0) -- in-run collapsed baseline reference.
- ARM_LPC_BIDIR (0.0248) + ARM_RANDOM (0.0121) -- RESUMED from existing ckpts (free controls).
2x2 attribution: {real,ema} x {barlow,vicreg}; the 4th cell (ema+vicreg) is referenced via the existing
old baseline (which additionally has clause/gate/reg-locus differences -- caveat flagged, honest).

**PRE-REGISTERED BAND (decisive, collapse axis; BEFORE running):**
- HARD-PASS = ARM_CAUSAL_REAL_BARLOW rep_std >= 0.020 (COLLAPSE_REP_STD_FLOOR) at 6000 steps
  -> verdict LITE_COLLAPSE_FIXED (the brain-faithful objective removes the collapse cause at the cheap budget).
- HARD-FAIL = ARM_CAUSAL_REAL_BARLOW rep_std < 0.020 -> verdict LITE_COLLAPSE_PERSISTS (collapse is
  scale/data at this proxy budget, not the target framing; the fuller build budget is genuinely required).
- ATTRIBUTION (reported, not gated): compare the 4 causal arms' rep_std to isolate whether the TARGET
  change, the REGULARIZER change, or only the FULL package clears the floor.
- Voice-role probe: run for RECORD ONLY on all arm ckpts (proxy-limit finding: role-reading does not
  emerge at lite budget for ANY arm -- bidir/random both 0.0/0.0 -- so the go-signal is rep_std, not the probe).

**Death-fixes carried verbatim:** data-prep bundle cache (HIT; key unchanged -- new keys not in
_DATA_CFG_KEYS), OOM tripwire (`_assert_no_vocab_dim` on the new loss path), (seed,arm) checkpoint/resume,
start-marker + crash-diagnostic + heartbeat, print-flush. run_one_seed's arms-differ made NON-FATAL (a
collapse experiment can legitimately produce coincident degenerate arms; record, do not crash the run).

**Dispatch (iteration 4):** remote units.jsonl already holds exactly BIDIR + RANDOM (deduped) so no
cleanup needed -- the 4 causal arms train, BIDIR/RANDOM resume, data-prep cache HITs.
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_latent_pc_arc_v1_lite experiments/exp_encoder_latent_pc_arc_v1.py preregs/encoder_latent_pc_arc_v1.md 7200 --allow-duplicate`
