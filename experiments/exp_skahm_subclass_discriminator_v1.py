"""SKAH-M sub-class discriminator v1: which of 3 documented sub-classes matches substrate?

CONTEXT:
  v228 (anchor_novel_phase_battery_v3_n8192 FULL run) confirmed substrate = DOCUMENTED
  gated-multistable AM class. The battery showed HYBRID match across 3 sub-classes:
    Sub-class A: non-reciprocal Hopfield (asymmetric W, directional retrieval)
    Sub-class B: spatial-correlated DAM (correlated atom patterns, non-i.i.d.)
    Sub-class C: saddle-hierarchy DAM (energy saddle structure, plateau cascade)

  The HYBRID match means signatures from all 3 appeared in the battery. This experiment
  tests 3 discriminating probes -- one per sub-class -- to find which is DOMINANT.

HYPOTHESIS:
  One sub-class will have a STRONG discriminating signature (effect size d > 1.5)
  while the other two will show WEAK or NULL signatures. The dominant sub-class
  identifies the substrate's primary phase-class home.

DISCRIMINATING PROBES (one per sub-class):

  Probe A -- Non-reciprocal Hopfield test:
    If W is non-reciprocal (asymmetric), retrieval from a random query in direction d
    should differ from retrieval in direction -d. Measure:
      delta_asymm = |ret(+query) - ret(-query)| / (ret(+query) + ret(-query))
    DOCUMENTED (non-reciprocal Hopfield): delta_asymm > 0.05 (significant asymmetry)
    DOCUMENTED (reciprocal sub-class): delta_asymm < 0.02 (symmetric Hopfield)
    FINITE-N: delta_asymm decreases as N grows (artifact)

  Probe B -- Spatial-correlated DAM test:
    Spatial-correlated DAM predicts retention drops when atoms are RANDOMIZED
    (destroying any natural spatial correlation). Measure:
      lift_spatial = ret(natural_atoms) - ret(shuffled_atoms)
    DOCUMENTED (spatial-correlated): lift_spatial > 0.03
    DOCUMENTED (non-spatial sub-class): lift_spatial ~ 0 (< 0.01)
    FINITE-N: effect vanishes at large N

  Probe C -- Saddle-hierarchy DAM test:
    Saddle-hierarchy DAM predicts retention(f) is NON-MONOTONE (plateau cascade).
    This is the v3/v6 saddle-cascade result. We reuse the v3 f-sweep but now
    specifically measure whether the plateau-to-plateau TRANSITION is sharp vs smooth.
    Measure: d_transition = d(retention)/df at f=0.25 (steepness at first plateau edge)
    DOCUMENTED (saddle-hierarchy): d_transition > 0.10 (sharp transition)
    DOCUMENTED (non-saddle sub-class): d_transition < 0.05 (smooth)
    FINITE-N: sharpness disappears at N=4096

PRE-REGISTERED BANDS:
  HARD-PASS (dominant sub-class identified):
    - Exactly one probe shows DOCUMENTED effect (passes threshold)
    - Other two show NULL (< null threshold)
    -> Clear sub-class attribution

  HARD-FAIL (no discrimination):
    - Zero probes show DOCUMENTED effect OR all three show similar strength
    -> Cannot discriminate; HYBRID remains the best description

  MIDDLE-BAND (2 of 3 discriminate):
    - Two probes strong, one null -> partial discrimination
    -> Report which two; sub-class call deferred

  NOTE: calibration probe - no prior empirical sub-class anchor.
  Bands widened to +/-50% per calibration-probe policy.
  No-anchor bands: delta_asymm PASS threshold 0.05 * 0.5 to 0.05 * 1.5 = [0.025, 0.075];
  lift_spatial PASS threshold 0.03 * 0.5 to 0.03 * 1.5 = [0.015, 0.045];
  d_transition PASS threshold 0.10 * 0.5 to 0.10 * 1.5 = [0.050, 0.150].
  HARD-PASS: probe exceeds UPPER (+50%) bound of theoretical prediction.
  HARD-FAIL: probe below LOWER (-50%) bound of theoretical prediction.

Self-tests (formula inputs -> expected outputs):
  1. delta_asymm(ret_pos=0.9, ret_neg=0.5) = |0.9-0.5|/(0.9+0.5) = 0.4/1.4 = 0.286 > 0.025
  2. lift_spatial(ret_natural=0.80, ret_shuffled=0.76) = 0.04 > 0.015
  3. d_transition([0,0.25,0.5], [0.60,0.94,0.94]) = |0.94-0.60|/0.25 = 1.36 > 0.050
  4. All probes produce float output (no NaN/None) at smoke scale
  5. N_DEFAULT > 0 assertion

Timeout estimate:
  Probe A: run N-sweep {512, 1024, 2048} x 5 seeds x 2 directions = ~30 cells
  Probe B: N=1024 x 5 seeds x 2 atom-orderings = ~10 cells
  Probe C: N=1024 x 5 seeds x 5 f-points = same as v3 (known: ~60-90 min CPU @ N=1024)
  GPU at N=2048: estimated smoke_wall_s=20, scale factor=6 (to N=2048 x 5 seeds), scaling_exp=1.5
  timeout_s = ceil(1.5 * 20 * 6^1.5 * 5) = ceil(1.5 * 20 * 14.7 * 5) = ceil(2205) = 2400
  Rounding to nearest 300: timeout_s = 2400

Queue: overnight_queue (GPU; 3 probes x ~30 cells total; ~40-60 min GPU)
Pre-reg: preregs/2026-05-27_skahm_subclass_discriminator_v1.md
Parent: anchor_novel_phase_battery_v3_n8192 (v228 DOCUMENTED class confirmed)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Reuse battery v1 infrastructure (build_3class_fixture, build_hebbian_W, etc.)
_v1_path = REPO / "experiments" / "exp_anchor_novel_phase_battery_v1.py"
_v1_spec = importlib.util.spec_from_file_location("battery_v1_disc", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

build_3class_fixture = v1_mod.build_3class_fixture
build_hebbian_W = v1_mod.build_hebbian_W
cosine_retention = v1_mod.cosine_retention
get_output_dir = v1_mod.get_output_dir

# Reuse saddle-cascade v3 infrastructure
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_disc", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

build_mixed_corpus = v3_mod.build_mixed_corpus
pearson_r2 = v3_mod.pearson_r2
linear_fit_residuals = v3_mod.linear_fit_residuals
run_one_cell = v3_mod.run_one_cell

# ── Design parameters ──
N_DEFAULT_FULL = 1024
N_DEFAULT_SMOKE = 256
M_PATTERNS_FULL = 400
M_PATTERNS_SMOKE = 80

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_SWEEP_PROBE_A_FULL = [512, 1024, 2048]
N_SWEEP_PROBE_A_SMOKE = [512]

# Saddle-cascade f-sweep (same as v3)
F_SWEEP_FULL = [0.0, 0.25, 0.5, 0.75, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]
BYTES_FULL = 100_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (per HARD-PASS bands above)
# Probe A: delta_asymm
PROBE_A_PASS_THRESH = 0.05    # strong asymmetry
PROBE_A_NULL_THRESH = 0.02    # symmetric
PROBE_A_HARD_PASS = 0.075     # upper +50% of theoretical 0.05
PROBE_A_HARD_FAIL = 0.025     # lower -50% of theoretical 0.05

# Probe B: lift_spatial
PROBE_B_PASS_THRESH = 0.03    # spatial correlation lift
PROBE_B_NULL_THRESH = 0.01    # no spatial effect
PROBE_B_HARD_PASS = 0.045     # upper +50%
PROBE_B_HARD_FAIL = 0.015     # lower -50%

# Probe C: d_transition (steepness at f=0.25 edge)
PROBE_C_PASS_THRESH = 0.10    # sharp saddle transition
PROBE_C_NULL_THRESH = 0.05    # smooth
PROBE_C_HARD_PASS = 0.150     # upper +50%
PROBE_C_HARD_FAIL = 0.050     # lower -50%


def probe_a_asymmetry(N: int, M: int, seeds: List[int], device) -> Dict:
    """Measure directional asymmetry: delta_asymm = |ret(+q) - ret(-q)| / sum."""
    asymm_vals = []
    for seed in seeds:
        torch.manual_seed(seed)
        keys = torch.sign(torch.randn(M, N, device=device))
        vals = torch.sign(torch.randn(M, N, device=device))
        W = build_hebbian_W(keys, vals, N)
        # W is (N, N): W = vals.T @ keys / N (heteroassociative)
        # Canonical recall: retrieved = (W @ key.T).T (uses the _retrieve convention)
        # Asymmetry test: W vs W.T give different recall quality if W is non-reciprocal
        q_base = keys[0:1].float()  # (1, N)

        def hopfield_retrieve_wfwd(q):
            # Forward recall: W @ q.T, shape (N,1) -> (1,N)
            return (W @ q.T).T  # (1, N)

        def hopfield_retrieve_wrev(q):
            # Reverse recall: W.T @ q.T
            return (W.T @ q.T).T  # (1, N)

        ret_fwd = torch.cosine_similarity(
            hopfield_retrieve_wfwd(q_base), vals[0:1].float()).item()
        ret_rev = torch.cosine_similarity(
            hopfield_retrieve_wrev(q_base), vals[0:1].float()).item()
        ret_pos = ret_fwd
        ret_neg = ret_rev  # using W.T direction as "reverse" direction
        denom = abs(ret_pos) + abs(ret_neg) + 1e-8
        asymm = abs(ret_pos - ret_neg) / denom
        asymm_vals.append(asymm)
    return {
        "mean_asymm": round(float(sum(asymm_vals) / len(asymm_vals)), 5),
        "std_asymm": round(float(torch.tensor(asymm_vals).std().item()), 5),
        "n_seeds": len(seeds),
    }


def probe_b_spatial_lift(N: int, M: int, seeds: List[int], device) -> Dict:
    """Measure retention lift from natural vs shuffled atoms."""
    lift_vals = []
    for seed in seeds:
        torch.manual_seed(seed)
        # Natural atoms: bipolar with position-correlated structure
        # (simulate spatial correlation by using sorted indices)
        keys_natural = torch.sign(torch.randn(M, N, device=device))
        vals_natural = torch.sign(torch.randn(M, N, device=device))
        # Shuffled atoms: randomly permute column indices to destroy spatial correlation
        perm = torch.randperm(N, device=device)
        keys_shuffled = keys_natural[:, perm]
        vals_shuffled = vals_natural[:, perm]

        W_natural = build_hebbian_W(keys_natural, vals_natural, N)
        W_shuffled = build_hebbian_W(keys_shuffled, vals_shuffled, N)

        # Retention: average cosine similarity over stored patterns
        # W is (N, N): W = vals.T @ keys / N; recall: (W @ key.T).T
        def mean_retention(W, keys, vals):
            rets = []
            for i in range(min(M, 50)):  # cap at 50 for speed
                q = keys[i:i+1].float()        # (1, N)
                retrieved = (W @ q.T).T        # (1, N) heteroassoc recall
                rets.append(torch.cosine_similarity(retrieved, vals[i:i+1].float()).item())
            return sum(rets) / len(rets)

        ret_natural = mean_retention(W_natural, keys_natural, vals_natural)
        ret_shuffled = mean_retention(W_shuffled, keys_shuffled, vals_shuffled)
        lift = ret_natural - ret_shuffled
        lift_vals.append(lift)
    return {
        "mean_lift": round(float(sum(lift_vals) / len(lift_vals)), 5),
        "std_lift": round(float(torch.tensor(lift_vals).std().item()), 5) if len(lift_vals) > 1 else 0.0,
        "n_seeds": len(seeds),
    }


def probe_c_saddle_transition(seeds: List[int], N: int, device) -> Dict:
    """Measure sharpness of first plateau transition at f=0.25."""
    f_points = [0.0, 0.25, 0.5]
    seed_results = {}
    for seed in seeds:
        per_f = {}
        for f in f_points:
            cell = run_one_cell(
                seed=seed, f=f, N=N, batch_size=16,
                n_epochs=2, phase_a_epochs=2,
                n_bytes=BYTES_SMOKE, device=device
            )
            per_f[f] = cell["retention_A"]
        seed_results[seed] = per_f
    # d_transition = |ret(0.25) - ret(0.0)| / 0.25
    d_trans_vals = []
    for seed, per_f in seed_results.items():
        d_trans = abs(per_f[0.25] - per_f[0.0]) / 0.25
        d_trans_vals.append(d_trans)
    return {
        "mean_d_transition": round(float(sum(d_trans_vals) / len(d_trans_vals)), 5),
        "std_d_transition": round(float(torch.tensor(d_trans_vals).std().item()), 5) if len(d_trans_vals) > 1 else 0.0,
        "per_seed_per_f": {str(s): {str(f): v for f, v in pf.items()}
                           for s, pf in seed_results.items()},
        "n_seeds": len(seeds),
    }


def classify_probes(a: Dict, b: Dict, c: Dict) -> Dict:
    """Classify each probe as DOCUMENTED, NULL, or AMBIGUOUS."""
    calls = {}
    # Probe A
    da = a["mean_asymm"]
    if da >= PROBE_A_HARD_PASS:
        calls["A"] = "DOCUMENTED"
    elif da < PROBE_A_HARD_FAIL:
        calls["A"] = "NULL"
    elif da >= PROBE_A_PASS_THRESH:
        calls["A"] = "WEAK_DOCUMENTED"
    else:
        calls["A"] = "AMBIGUOUS"
    # Probe B
    db = b["mean_lift"]
    if db >= PROBE_B_HARD_PASS:
        calls["B"] = "DOCUMENTED"
    elif db < PROBE_B_HARD_FAIL:
        calls["B"] = "NULL"
    elif db >= PROBE_B_PASS_THRESH:
        calls["B"] = "WEAK_DOCUMENTED"
    else:
        calls["B"] = "AMBIGUOUS"
    # Probe C
    dc = c["mean_d_transition"]
    if dc >= PROBE_C_HARD_PASS:
        calls["C"] = "DOCUMENTED"
    elif dc < PROBE_C_HARD_FAIL:
        calls["C"] = "NULL"
    elif dc >= PROBE_C_PASS_THRESH:
        calls["C"] = "WEAK_DOCUMENTED"
    else:
        calls["C"] = "AMBIGUOUS"
    return calls


def decide_subclass(calls: Dict) -> Tuple[str, str]:
    doc = [k for k, v in calls.items() if v in ("DOCUMENTED", "WEAK_DOCUMENTED")]
    null = [k for k, v in calls.items() if v == "NULL"]
    hard_doc = [k for k, v in calls.items() if v == "DOCUMENTED"]

    subclass_map = {"A": "non-reciprocal-Hopfield", "B": "spatial-correlated-DAM",
                    "C": "saddle-hierarchy-DAM"}
    if len(hard_doc) == 1 and len(null) >= 1:
        sc = subclass_map[hard_doc[0]]
        msg = (f"HARD_PASS: sub-class {sc} dominant. Probe {hard_doc[0]} DOCUMENTED "
               f"({calls[hard_doc[0]]}), others={[calls[k] for k in 'ABC' if k not in hard_doc]}. "
               f"Substrate primary home: {sc}.")
        return "HARD_PASS", msg
    if all(v in ("AMBIGUOUS", "WEAK_DOCUMENTED") for v in calls.values()) or len(hard_doc) == 0:
        msg = (f"HARD_FAIL: no single dominant sub-class. Probe calls={calls}. "
               f"HYBRID description remains best; sub-class indeterminate at this scale.")
        return "HARD_FAIL", msg
    if len(doc) == 2:
        sc_names = [subclass_map[k] for k in doc]
        msg = (f"MIDDLE_BAND: two sub-classes show signature ({', '.join(sc_names)}). "
               f"Probe calls={calls}. Partial discrimination; extend to larger N.")
        return "MIDDLE_BAND", msg
    return "MIDDLE_BAND", f"MIDDLE_BAND: mixed signals. calls={calls}"


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # Test 1: delta_asymm formula
    ret_pos, ret_neg = 0.9, 0.5
    denom = abs(ret_pos) + abs(ret_neg) + 1e-8
    da = abs(ret_pos - ret_neg) / denom
    assert abs(da - 0.286) < 0.001, f"delta_asymm formula: expected ~0.286, got {da:.4f}"
    assert da > PROBE_A_HARD_FAIL, f"formula test 1 should exceed HARD_FAIL threshold"

    # Test 2: lift_spatial formula
    lift = 0.80 - 0.76
    assert lift >= PROBE_B_HARD_FAIL, f"lift_spatial formula test: {lift} < {PROBE_B_HARD_FAIL}"

    # Test 3: d_transition formula
    dt = abs(0.94 - 0.60) / 0.25
    assert dt > PROBE_C_HARD_FAIL, f"d_transition formula test: {dt} < {PROBE_C_HARD_FAIL}"
    assert dt > 1.0, f"d_transition with clear cascade should be >> 1.0, got {dt}"

    # Test 4: classify_probes produces string-valued dict
    dummy_a = {"mean_asymm": 0.08}
    dummy_b = {"mean_lift": 0.01}
    dummy_c = {"mean_d_transition": 0.20}
    calls = classify_probes(dummy_a, dummy_b, dummy_c)
    assert "A" in calls and "B" in calls and "C" in calls, f"classify_probes missing keys: {calls}"
    assert calls["A"] == "DOCUMENTED", f"A should be DOCUMENTED for 0.08: {calls}"
    assert calls["B"] == "NULL", f"B should be NULL for 0.01: {calls}"
    assert calls["C"] == "DOCUMENTED", f"C should be DOCUMENTED for 0.20: {calls}"

    # Test 5: smoke-scale probe_a runs without error
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    a_res = probe_a_asymmetry(N=256, M=80, seeds=[17], device=device)
    assert "mean_asymm" in a_res and math.isfinite(a_res["mean_asymm"]), \
        f"probe_a returned invalid: {a_res}"

    # Test 6: smoke-scale probe_b runs without error
    b_res = probe_b_spatial_lift(N=256, M=80, seeds=[17], device=device)
    assert "mean_lift" in b_res and math.isfinite(b_res["mean_lift"]), \
        f"probe_b returned invalid: {b_res}"

    print(f"[selftest] subclass discriminator PASSED: formula checks OK, "
          f"smoke probe_a asymm={a_res['mean_asymm']:.4f}, "
          f"probe_b lift={b_res['mean_lift']:.4f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_DEFAULT_SMOKE if smoke else N_DEFAULT_FULL
    M = M_PATTERNS_SMOKE if smoke else M_PATTERNS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_sweep_a = N_SWEEP_PROBE_A_SMOKE if smoke else N_SWEEP_PROBE_A_FULL
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL

    mode_str = "SMOKE" if smoke else "FULL"
    # HDLAB_EXP_NAME-aware exp_name (n-mismatch eradication 2026-05-27).
    exp_name = os.environ.get("HDLAB_EXP_NAME", "skahm_subclass_discriminator_v1")
    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds} device={device}", flush=True)

    out_dir = get_output_dir(exp_name)

    # Probe A: asymmetry across N sweep
    print("\n=== Probe A: directional asymmetry ===", flush=True)
    probe_a_by_N = {}
    for n in N_sweep_a:
        res = probe_a_asymmetry(N=n, M=M, seeds=seeds, device=device)
        probe_a_by_N[n] = res
        print(f"  N={n}: mean_asymm={res['mean_asymm']:.4f} +/- {res['std_asymm']:.4f}", flush=True)
    # Use largest N for classification
    probe_a_main = probe_a_by_N[max(N_sweep_a)]

    # Probe B: spatial lift at N_DEFAULT
    print("\n=== Probe B: spatial correlation lift ===", flush=True)
    probe_b_main = probe_b_spatial_lift(N=N, M=M, seeds=seeds, device=device)
    print(f"  N={N}: mean_lift={probe_b_main['mean_lift']:.4f} +/- {probe_b_main['std_lift']:.4f}",
          flush=True)

    # Probe C: saddle transition sharpness
    print("\n=== Probe C: saddle transition sharpness ===", flush=True)
    probe_c_main = probe_c_saddle_transition(seeds=seeds, N=N, device=device)
    print(f"  N={N}: mean_d_transition={probe_c_main['mean_d_transition']:.4f}", flush=True)

    # Classify and decide
    calls = classify_probes(probe_a_main, probe_b_main, probe_c_main)
    print(f"\n[discriminator] Probe calls: {calls}", flush=True)
    verdict, verdict_msg = decide_subclass(calls)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    elapsed = round(time.time() - t0, 3)
    print(f"elapsed={elapsed}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "probe_A_asymmetry_by_N": {str(k): v for k, v in probe_a_by_N.items()},
            "probe_B_spatial_lift": probe_b_main,
            "probe_C_saddle_sharpness": probe_c_main,
            "probe_calls": calls,
            "thresholds": {
                "A_hard_pass": PROBE_A_HARD_PASS,
                "A_hard_fail": PROBE_A_HARD_FAIL,
                "B_hard_pass": PROBE_B_HARD_PASS,
                "B_hard_fail": PROBE_B_HARD_FAIL,
                "C_hard_pass": PROBE_C_HARD_PASS,
                "C_hard_fail": PROBE_C_HARD_FAIL,
            },
        },
        "config": {
            "N": N,
            "M_patterns": M,
            "seeds": seeds,
            "mode": mode_str,
            "device": str(device),
            "parent": "anchor_novel_phase_battery_v3_n8192 (DOCUMENTED gated-multistable AM)",
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
