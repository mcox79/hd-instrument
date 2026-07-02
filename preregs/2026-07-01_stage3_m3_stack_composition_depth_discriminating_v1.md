# Pre-reg: stage3_m3_stack_composition_depth_discriminating_v1

Date: 2026-07-01
Author: hdi_exp_dev (spawn)
Route: overnight_queue (GPU-heavy at N_DIM=8192; 90 units at full)
Timeout: 7200s per seed (chunked single-seed-per-cell)
Parents:
  - M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15)
  - M1.5 v2 TWOTIER context retention (Atom 18)
  - M1.6 v2 4-class attention-binding router (Atom D)
  - M1.7 role-slot summarization CG
  - M3 4-primitive stack meta CG (today)
  - deep_composition v2 landed MM (positive comp evidence at K=100/N=8192; saturation blocked CG)

## Substrate-KB concept-query check (mandatory)

Query: `M3 stack composition depth over-Amit-Gutfreund refuse context router summarization`
Top-5 hits (all cosine <= 0.34; source: substrate_kb v1):
  1. Compositional generalization context (cosine=0.34, BetX skill composition arc)
  2. Composition depth L=10,000 (cosine=0.32, hierarchical architecture drill)
  3. Composition (cosine=0.31, humaneval / substrate_aliveness misc)
  4. Composition depth L=10000 (cosine=0.31, cross-modal drill)
  5. Composition path (cosine=0.30, cascade continual v1/v2)

**Prior-work verdict: NONE at cosine>0.30 matching M3 4-primitive-stack composition-depth
in discriminating regime. Genuinely novel; rediscovery risk LOW.**

## Purpose

Chain-grade the M3 4-primitive stack composition depth by pushing into a regime
where discrimination is REAL (over-Amit-Gutfreund supra-capacity + noise arm).
Deep-composition v2 landed MM saturated (all mechanism arms at 1.0 across
regimes; discriminator saturation blocked CG). v1 (this pre-reg) fixes the
discriminator-saturation issue via:

  (a) STM bundle bank with M_items = alpha * V_CB (alpha in {0.5, 1.5, 3.0})
      Standard-Hopfield-style bundling means alpha=0.5 already at 3.62x critical
      Amit-Gutfreund capacity (alpha_c=0.138), alpha=3.0 at 21.7x critical.
      Substrate cannot handle these loads trivially.
  (b) Query-noise arm: independent Bernoulli bit-flip on step query with
      f in {0.0, 0.30}. At f=0.30, signal_cos = 1 - 2f = 0.40 (severe).
  (c) Depth axis in {5, 10, 25, 50, 100} with per-step noise compounding
      that refuse-gate can only PARTIALLY reset.

## HP conditions (chain-grade if ALL fire per HP_SCOPE below)

HP_STACK_HOLDS_AT_DEPTH_100: at (depth=100, alpha=0.5, f=0.0),
  ARM_FULL_STACK step_correct >= 0.95 (composed stack survives to
  depth 100 in easy regime). HP_SCOPE = [ARM_FULL_STACK]

HP_STACK_DEGRADES_AT_LOAD: at (depth=100, alpha=3.0, f=0.0),
  ARM_FULL_STACK step_correct drops by >= 0.30 vs (depth=100, alpha=0.5, f=0.0).
  Mechanism sensitive to load. HP_SCOPE = [ARM_FULL_STACK]

HP_STACK_DEGRADES_AT_NOISE: at (depth=50, alpha=1.5, f=0.30),
  ARM_FULL_STACK step_correct drops by >= 0.20 vs (depth=50, alpha=1.5, f=0.0).
  Mechanism sensitive to noise. HP_SCOPE = [ARM_FULL_STACK]

HP_NO_CROSS_STAGE_BUG: no depth > 5 point shows sudden collapse to <= 0.05
  (per-step score) in ANY regime where prior depth showed > 0.30. Mechanism has
  SMOOTH degradation. HP_SCOPE = [ARM_FULL_STACK]

## HF conditions

HF_STACK_SATURATES: ALL 4 primitives=1.000 across ALL regimes (discriminator
  saturation like v2; needs harder cell).

HF_STACK_BREAKS_EARLY: ARM_FULL_STACK step_correct < 0.30 at (depth=5,
  alpha=0.5, f=0.0). Composition broken by construction; positive control fails.

HF_CARDINALITY_BREACH_META_RULE_H: observed_n_units < 0.85 * expected.

HF_ARMS_IDENTICAL_META_RULE_AF: two distinct arms produce bit-identical
  output-tensors (predicted-route + recovered-val chains, NOT summary scores).

HF_BASELINE_OUT_OF_BAND_META_RULE_AG: at all sweep points, an easy-regime
  point produces baseline saturated >=0.95 (substrate too robust for regime).

## Cardinality

FULL: 5 depths x 3 alpha x 2 f x 1 seed_per_cell = 30 units/seed
      (main arm ARM_FULL_STACK)
      Plus per-cell ablations: SUB_ONLY_D50_alpha0.5_f0 and NO_REFUSE_D50_alpha1.5_f0.30
      = 32 units/seed. 3 chunked seed cells = 96 total units at cardinality.
EXPECTED_N_UNITS = 32 per seed cell.
HF_CARDINALITY_BREACH if observed < 27 (85% floor).

SMOKE: 3 depths {5, 25, 100} x 2 alpha {0.5, 3.0} x 2 f {0.0, 0.30} x
       1 seed = 12 units. Plus 2 ablations = 14 units. Includes full-N
       preview arm at (depth=100, alpha=3.0, f=0.30) per META
       DISCRIMINATOR-MUST-SURVIVE-SCALE rule (option C).

## Discriminator-survives-scale justification (META rule)

**Option B: analytical justification.**
  - Standard-Hopfield capacity alpha_c = 0.138 (Amit-Gutfreund).
  - Our sweep alpha in {0.5, 1.5, 3.0} = {3.62x, 10.87x, 21.7x} critical.
  - At alpha > alpha_c, retrieval collapses to random within O(1) attempts.
  - Substrate at these loads CANNOT trivially saturate.
  - Formula:
      signal_cos_after_M_items = 1 / sqrt(1 + M/N * factor)
    At M/N=3, signal_cos=~0.5 for single-shot cleanup (uncorrected).

**Option C also in play**: smoke includes (depth=100, alpha=3.0, f=0.30) at
  full-N=8192 as preview arm. If preview shows saturation >=0.95 in that arm,
  REJECT_FULL_DISPATCH per META rule.

## Baseline-in-band justification (META_RULE_AG)

  - At (depth=100, alpha=0.5, f=0.0): baseline expected >= 0.90 (easy regime)
  - At (depth=100, alpha=3.0, f=0.30): baseline expected <= 0.20 (hard regime)
  - Sweep spans wide difficulty; MAJORITY of sweep points expected in [0.30, 0.70]
    (discriminating band).
  - discriminating_fraction >= 5/12 = 0.42 (>= 0.30 threshold per gate B).

## CRLB / capacity-feasibility (META §9)

  - Chance floor: 1/V_CB = 1/1024 = 0.00098 THEORETICAL@codebook-argmax-uniform
  - N_TRIALS_FULL=4 per unit; Bernoulli sigma at p=0.5: sqrt(0.25 / (4 * 100 steps))
    = 0.025 for depth=100 unit. Detectable at HP delta=0.30 margin.
  - alpha_c margin: Amit-Gutfreund critical alpha_c=0.138. All sweep alphas
    supra-critical. discriminator_reachability = True.
  - HP_STACK_HOLDS_AT_DEPTH_100 = 0.95 floor: at (depth=100, alpha=0.5, f=0.0),
    per-step p_correct >= 0.99 required. Chain length 100, product p_correct^100 >= 0.37
    if p_correct=0.99. This is a **soft** definition: use MEAN over steps, not PRODUCT.
    Feasibility at alpha=0.5 (supra-critical for Hopfield but sub-critical for
    dense-Hopfield style cleanup with V_CB=1024 argmax) is expected to be 0.95+.
  - HP_STACK_DEGRADES_AT_LOAD delta=0.30: at alpha=3.0 M=3072 items -> average
    3 items per V_CB slot -> ambiguity floor. Expected step_correct ~ 0.40 in
    hardest regime. delta >= 0.55, well above 0.30 margin.

crlb_floor_computed: 0.025 (Bernoulli sigma per unit at n_trials=4, depth=100)
crlb_formula_reference: sigma = sqrt(0.25 / (n_trials * depth))
discriminator_reachability: True

## Composition edges / shape audit (META §15C)

  M1.4_refuse_gate -> M1.5_STM_recall : SHAPE_MATCH (both operate on
    perturbed_key -> boolean route + optional cleanup vector)
  M1.5_STM_recall -> M1.6_router     : SHAPE_MATCH (STM recovered_val
    becomes downstream step's query root)
  M1.6_router -> M1.7_summarization  : SHAPE_MATCH (route_prediction becomes
    role-slot binding target)
  M1.7_summarization -> next_step    : SHAPE_MATCH (bundle output is next
    step's chain query root)

sweep_alignment_verdict: ALIGNED (all sweep axes affect the primitive they
  measure -- alpha and depth both directly stress STM capacity + noise
  compounding)

## Positive control arm (META §15D)

  ARM_FULL_STACK at (depth=5, alpha=0.5, f=0.0): expected step_correct
  >= 0.90 (reproduces M1.5 v2 + M1.6 v2 baselines at short chain, light load,
  no noise). Cited prior: deep_composition v2 FS_D10 at RETRIEVE_CHAIN = 1.0.
  Tolerance: 0.15 (allow drift due to bundle vs class-HV route). If
  positive control fails, HARD_FAIL_POSITIVE_CONTROL_BROKEN.

## Functional requirements (META §15E)

  FR1: Deep chain preserves entity identity (STM handoff).
       Primitive: M1.5 v2 STM K=100 multi-bank.
  FR2: OOD probes trigger refuse mid-chain without corrupting later steps.
       Primitive: M1.4 v8 CONFORMAL_MODERATE tau=0.7.
  FR3: Router switches route-class per step (M1.6 v2 class-HVs).
  FR4: Composed stack shows lift vs single-primitive ablation in load or
       noise regime (not just easy regime).

## Schema-vet mandatory pre-reg fields (per exp_dev.md §14)

cell_chunked: true (3 seed cells: seed_7, seed_13, seed_19)
start_marker_written: true (inline per META §13)
crash_diagnostic_present: true (except Exception -> CELL_CRASHED metrics.json)
heartbeat_present: true (periodic _heartbeat.jsonl)
defensive_error_checking: passed_all_4_patterns
cardinality_ok: mandatory (verdict-level; observed >= 27 of 32)
arms_differ_verified: mandatory at smoke (fixed vs v2: hash raw
  output-tensor per_step arrays, NOT [1,1,1,1] trial_scores)
arms_differ_exempted: NONE
baseline_in_band: mandatory (0.05 < baseline_score < 0.95 at some sweep point)
crlb_floor_computed: 0.025
discriminator_reachability: True
sweep_alignment_verdict: ALIGNED
discriminating_fraction: 0.42
composition_edges: all SHAPE_MATCH
positive_control_arms: ARM_FULL_STACK at (depth=5, alpha=0.5, f=0.0)
final_metrics_atomicity: tmp_replace (atomic os.replace at end)
calibration_check: adaptive_with_discriminator_gate (STM_K scales with alpha;
  discriminator-still-fires verified in smoke)
progress_logging: print_flush_true (line-buffered stdout at cell start)
run_mode_default: full (cell defaults to full unless --self-test or --smoke)

## Preserved conventions

  - ASCII-only (no unicode in cell)
  - No emojis
  - REPO-relative paths (Path(__file__).resolve().parent.parent)
  - torch.Generator with known seeds (numpy Generator wrapped equivalently)
  - N_DIM=8192 fixed in BOTH smoke + full (discriminator on depth + alpha + f)
  - except SystemExit: raise BEFORE except Exception (META §8)

## Loading framing (if HP)

Promotes M3 4-primitive-stack meta atom from CG to
CG-WITH-DEPTH-CHARACTERIZATION (composed to depth 100 with load/noise
sensitivity mapped). Load-bearing for M3 Phase 1 architecture: quantifies
WHEN cortex layer needs to break composition into chunks vs run at depth.

## Route

overnight_queue via hdi_orchestrator handoff (harness-denied to exp_dev).
Cell-author (this spawn) DOES: pre-reg + cell code + smoke run + REMOTE VERIFY.
Orchestrator DOES: git push origin main + queue_add.py on remote GPU host.
