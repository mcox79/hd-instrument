# Pre-registration: schema_relation_richer_content_vscan_v1

**Filed:** 2026-07-05 by exp_dev (cell author)
**Cell:** `experiments/exp_schema_relation_richer_content_vscan_v1.py`
**Anchor:** `schema_relation_richer_content_vscan_v1`
**Queue:** `overnight_queue` (GPU; JOINT arm is torch-autograd trainable; device auto->cuda on the box)
**Timeout:** 3600 s (GPU estimate ~10-12 min; 5x margin; kills a mis-routed CPU run ~8000s before it wastes hours)

## KB_REFERENT
notes/research_mechanism_envelope_frontier_inductive_transfer_off_zero_2026-07-05.md
data/exp_schema_relation_TEM_scorer_scaleup_envelope_v2/metrics.json (the scale-up wall this cell answers)

## Scientific question (the decisive expansion test)
The scale-up envelope (`..._scaleup_envelope_v2`, VET=MEASURED_MECHANISM) proved inductive
relational generalization is NARROW: real_minus_shuf(ind) crosses the 0.2075 bar ONLY at V=100
(CausesDesire/bge rms=+0.213), and the V-scan COLLAPSES at realistic vocab:
- V100 CausesDesire/bge rms=+0.213; AtLocation/bge +0.149  MEASURED@..._scaleup_envelope_v2:cells_aggregate
- V300 CausesDesire/bge rms=+0.087; AtLocation/bge +0.067  MEASURED (frozen collapses)
- V1000 CausesDesire/bge rms=+0.038; AtLocation/bge +0.049 MEASURED
The M_OP/df/steps scans all plateaued ~0.11 -> the ceiling is candidate-count / one-to-many ENTROPY
on the V-axis, NOT under-parameterization. The mechanism research predicted the FIX = RICHER,
JOINTLY-TRAINED content (the DKRL->KEPLER->BLP->SimKGC direction; BLP 0.180->0.285 MRR, +58% rel,
from richer jointly-trained content NOT more compute) CITED@notes/research_mechanism_envelope_frontier
_inductive_transfer_off_zero_2026-07-05.md. This is that untested lever.

**Decisive question:** does richer jointly-trained content push inductive real_minus_shuf >= 0.2075 at
V>=300 on >=2 relations x >=2 encoders -- a GENUINE broad win, not the V=100 corner? MAP the V-scan
{100,300,1000} for the RICHER (JOINT) arm vs the FROZEN baseline. Constructive; brain-first.

## Mechanism map (ONE manipulation: content representation; everything else held identical)
- **FROZEN** (baseline to beat) = the scale-up SCORER VERBATIM: frozen content feature (BGE/GSBC,
  centered+unit) -> FIXED random projection P_s,P_o (d->df=384) -> trained bilinear W (RESCAL/DistMult,
  2000 steps). Content code FIXED; only relation form W adapts.
- **JOINT** (richer, NEW) = a SHARED small content encoder g_theta (2-layer MLP d->h=256->df=128,
  tanh, dropout 0.1) trained END-TO-END with a bilinear relation R on the same inductive softmax-CE
  objective (Adam lr 2e-3, wd 1e-3, 500 steps, tau 0.1). Score s = g(f_s)^T R g(f_o). Content
  CO-ADAPTS with relation (BLP/SimKGC direction). Brain analog: cortical representations shaped BY the
  relational tasks they support. INDUCTIVE-VALID: g is a FUNCTION of the frozen feature -> novel
  (held-out) subjects encoded by the SAME g; no per-entity table, no transductive leak.
- **MEAN_OBJECT** = population-marginal (most-frequent train object) control for the rmm gate.
FROZEN and JOINT are PAIRED (same triples / split / seed / features; only the content representation
and the shuffle differ).

Load-bearing metric: REAL - SHUFFLED on INDUCTIVE (novel-subject) eval. Raw accuracy is a relation-
prior trap; real_minus_shuf is the subject->object correspondence that must transfer to unseen entities.

## Contract (gate on the VET's expansion criterion; report the V-scan curve richer-vs-frozen)
- **HARD_PASS** = JOINT real_minus_shuf(ind) >= 0.2075 at V>=300 on a set of (rel,enc) cells spanning
  >=2 relations AND >=2 encoders (AtLocation+CausesDesire x bge+gsbc), with JOINT real_gain >= 0.2075
  and rmm >= 0.05, JOINT discriminator firing. The expansion criterion: a genuine broad win (NOT the
  V=100 corner, NOT a single-cell fluke).
- **HARD_FAIL** = richer content does NOT beat frozen at V>=300 (max over V>=300 semantic cells of
  JOINT_rms - FROZEN_rms < IMPROVE_MIN=0.02) while discriminators fire -> the one-to-many entropy
  ceiling is GENUINE for this task class (honest wall-finding; thin generic-sentence content on
  crowd-sourced relations at realistic vocab is not rescued by richer jointly-trained content).
- **MIDDLE_BAND** = richer content LIFTS the V>=300 curve above frozen (by >= IMPROVE_MIN somewhere)
  but does not clear 0.2075 across >=2 rels x >=2 encoders -> content is directionally the right lever;
  iterate richness (structured attributes / multi-sentence descriptions) next. The lift-but-plateau IS
  the finding.

HYPOTHESIZED outcome distribution (calibration-penalized, not load-bearing): MIDDLE most likely
(~0.50); HARD_FAIL genuine-ceiling ~0.30; HARD_PASS broad-win ~0.20. The mechanism note's own
prediction P(scale clears HP)=0.18; richer content is the untested other lever. HYPOTHESIZED@this prereg.

## Compute architecture
- **Class: (a) batched-GPU.** JOINT trains BOTH paired arms (REAL,SHUFFLED) in ONE batched model
  (leading B=2 dim; einsum over M x V x df; identical init broadcast across arms -> only y differs).
  FROZEN trains both arms in one torch-bmm B=2 pass (verbatim scale-up code). No python-loop over
  independent phase points; each (cfg,rel,enc,seed) is a vectorized on-device job. device auto->cuda.
- **Storage strategy: no_storage** (no bundled/sharded memory; this is a scorer/encoder cell).
- numpy fallback for FROZEN if torch absent; JOINT records failure_class JOINT_TORCH_UNAVAILABLE if
  torch absent (never on the GPU queue, which gates on `import torch`).

## SCHEMA-VET gates
- `cardinality_ok`: EXPECTED_N_UNITS = sum over configs of rels x encs x 10 (FROZEN 4 + JOINT 4 +
  MEAN_OBJECT 2) x 3 seeds. Verdict emits HARD_FAIL_CARDINALITY_BREACH if good_units < expected
  (gsbc-cache-missing exempted). Smoke verified good_units=40/40.
- `arms_differ_verified`: hash-test FROZEN_real!=FROZEN_shuf, JOINT_real!=JOINT_shuf, FROZEN!=JOINT on
  the discriminating nonlinear-content regime. Smoke: True.
- `final_metrics_atomicity`: tmp_replace (os.replace(metrics.json.tmp, metrics.json)).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException); start-marker + crash-diag.
- `crlb_n/a`: "argmax transfer has no closed-form noise floor". chance = 1/V_eff stated; HP floor
  0.2075 far below saturation at all V (reachability declared, asserted at import).
- `baseline_in_band`: FROZEN in (chance, 0.95); SHUFFLED ~chance; synth controls in-band. FROZEN is
  the baseline-to-beat (not a mechanism arm); its band is informational.
- `discriminator_fires` (META_RULE_K): TWO proofs, both required to interpret real-data arms:
  - FROZEN fires: synth_content_map (LINEAR content) FROZEN - GLOBAL >= 0.05. Smoke adv=+0.175.
  - JOINT fires: synth_nonlinear_content (|3 F A1| A2 abs-teacher, non-bilinear) JOINT - FROZEN >= 0.05.
    Probed adv_mean=+0.22 / adv_min=+0.15 over 3 seeds (FROZEN~0.12 linear-capped, JOINT~0.34). Smoke
    adv=+0.107. If JOINT does not fire -> MIDDLE_BAND_VACUOUS (richer capacity unproven).
- `HARD_PASS strictly above floor` (META_RULE_L): 0.2075 = 0.20 + 5% band-width.
- `HP_SCOPE`: HP/HF/MB gates apply to JOINT REAL/inductive SEMANTIC (AtLocation,CausesDesire) at
  V>=300 only. FROZEN = baseline-to-beat (not a win). DerivedFrom = surface negative watchdog (NOT HP).
  SHUFFLED/MEAN_OBJECT/SYNTH not HP-eligible.
- `calibration_check`: adaptive_with_discriminator_gate (the two synth discriminator-fires proofs
  gate interpretation of the real-data arms; per-family).
- `progress_logging`: print_flush_true (all progress lines flush=True; per-(config,seed) timing line;
  heartbeat _heartbeat.jsonl per unit). timeout_s=3600 >= 1800 -> mandatory; satisfied.
- Defensive error-checking: start_marker_written=True, crash_diagnostic_present=True,
  heartbeat_present=True, cell_chunked=False (single-seed loop with _seed_checkpoint resume; runner
  death loses only in-flight seed; per-seed write_partial), passed_all_4_patterns.

## §15 test-design gates
- **A effective_vs_nominal**: swept V is BOTH nominal and effective (V_eff = len(codebook) directly);
  no partition-routing intermediary. `sweep_alignment_verdict: ALIGNED`.
- **B discriminating_fraction**: the V-scan itself IS the discriminator (JOINT rms landing in
  [0.03,0.25] at V>=300 is the whole question; base frozen V300/V1000 measured 0.038-0.087, in-band;
  JOINT expected same-or-higher band). Predicted >=2/3 V-points land in the discriminating band ->
  discriminating_fraction ~0.67 (>= 0.30). Not a saturated/floor sweep.
- **C composition_edges**: single edge encoder g_theta (output df=128) -> bilinear R (input df=128).
  `SHAPE_MATCH`. No multi-primitive chain.
- **D positive_control_arms**: FROZEN must REPRODUCE the scale-up SCORER V-scan rms AT MATCHED REGIME
  (M=800, df=384, steps=2000, seeds 7/13/19, same features/split) -- FULL-only gate:
  - V100|CausesDesire|bge ref=0.213, V300|CausesDesire|bge ref=0.087, V300|AtLocation|bge ref=0.067
    MEASURED@..._scaleup_envelope_v2; tolerance 0.06. If FROZEN does not reproduce -> MIDDLE_BAND
    (referent not matched, comparison suspect). SKIPPED in smoke (reduced regime).
- **E functional_requirements**: (1) turn stored facts into transferable relational knowledge about
  UNSEEN entities -> inductive novel-subject eval + paired real-minus-shuf gate. (2) content code must
  carry relational structure -> JOINT jointly-trained encoder (the mechanism under test). (3) guard
  against surface/encoding leakage -> DerivedFrom watchdog + SHUFFLED-stays-chance control.

## Bands (numeric, LOCKED)
HP_RMS_MIN=0.2075, HP_REAL_GAIN_MIN=0.2075, HP_RMM_MIN=0.05, IMPROVE_MIN=0.02, RMS_SIGNAL_MIN=0.05,
FROZEN_ADV_MIN=0.05, JOINT_ADV_MIN=0.05, SYNTH_CLEAN_MIN=0.90, BIND_ROUNDTRIP_MIN=0.90, GATE_D_TOL=0.06.

## Config grid
- V-scan (PRIMARY, M=800 matched to scale-up v2): V in {100,300,1000} x {AtLocation,CausesDesire,
  DerivedFrom} x {bge_semantic, gsbc}.
- M-scan (SECONDARY, V=300 realistic vocab; does more data let richer content clear the bar?): M in
  {1500,3000} x {AtLocation,CausesDesire} x {bge_semantic}.
- Seeds [7,13,19]. N_DIM=8192. EXPECTED_N_UNITS = (3*3*2 + 2*2*1)*10*3 = 660.

## Persistence
metrics.json includes: v_scan_curve_joint_vs_frozen (per V per rel|enc: frozen_rms/joint_rms/
joint_minus_frozen/joint_real), records (all cells), jt_wins, win_rels, win_encs,
expansion_criterion_met, best_joint_rms/best_joint_minus_frozen at V>=300, gate_d_positive_control,
both synth discriminator proofs, per_unit + cells_aggregate. Numbers tagged MEASURED@/HYPOTHESIZED@/
THEORETICAL@/CITED@ in the cell docstring.

## Smoke result (pre-dispatch, CPU local)
self-test 21s PASS (both discriminators fire); smoke 28s wall, good_units=40/40, arms_differ=True,
fires[frozen=True(adv+0.175), joint=True(adv+0.107)], all verdict branches reachable (smoke landed
HARD_FAIL because smoke deliberately under-trains JOINT for speed: steps=80; FULL uses steps=500 on GPU).

## POST-SHIP REMOTE VERIFY (required)
After landing: verify metrics.json run_mode=full, device=cuda, size>5KB, good_units>=660 (or
gsbc-cache-missing exempted), gate_d_ok=True (FROZEN reproduced the scale-up referent), both
discriminators fired. Report the V-scan curve richer-vs-frozen explicitly.
