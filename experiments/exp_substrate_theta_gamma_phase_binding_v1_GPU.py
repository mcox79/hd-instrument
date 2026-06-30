"""substrate_theta_gamma_phase_binding_v1_GPU.

Brain-mechanism cell B. Tests THETA-GAMMA NESTED PHASE BINDING for sequence
position encoding (different axis from cortex-hippo Hc rescue).

CITED@Lisman_Idiart_1995_theta_gamma_phase_coding +
CITED@Buzsaki_brain_rhythm_theta_gamma_nested_oscillations:
Items bound to gamma-burst phases nested inside theta cycles. Each theta
cycle holds 5-7 gamma bursts; items at distinct gamma-phases are bound into
distinct sequence positions. FHRR (Fourier Holographic Reduced Representations)
uses complex-valued phase multiplication for binding.

LINEAGE:
  Current substrate sequence binding (cyclic-shift baseline): chain-grade
  primitive at K=20 N=4096 (atom 586, MEASURED@1.000). Tests whether
  theta-gamma phase code adds sequence-position discriminability at LARGER
  K (capacity stress) where cyclic-shift may collapse.

HYPOTHESIS:
  THEORETICAL@FHRR_phase_binding_capacity: phase-code binding y = x * exp(i*phi_pos)
  with K_phases distinct phi_pos values. K_phases too small -> phase
  collisions; too large -> phase discriminability requires finer angular
  resolution. Predicts: at K_seq capacity ~ K_phases, binding fidelity rises
  with K_phases up to ~N_DIM/log(N_DIM) regime.

ARMS (4):
  ARM_NO_PHASE       -- baseline: cyclic-shift sequence binding (current substrate)
  ARM_THETA_GAMMA_8  -- 8 distinct phi_pos values (8 phases per theta cycle)
  ARM_THETA_GAMMA_16 -- 16 phases
  ARM_THETA_GAMMA_32 -- 32 phases (finer angular resolution)

For each arm: bind K_seq=25 items into sequence; probe position 12; measure
recall fidelity (cosine to ground truth).

PRE-REG BANDS:
  HARD_PASS: best THETA_GAMMA arm recall_at_pos >= R_NO_PHASE + 0.20
             (phase-binding adds capacity headroom over cyclic-shift)
  MIDDLE_BAND: lift in [0.05, 0.20)
  HARD_FAIL: no THETA_GAMMA >= R_NO_PHASE + 0.05 (phase doesn't help)

REGIME:
  FULL:  N=8192 complex (so 8192 real components), K_seq=25, seeds=[7,17,23]
  SMOKE: N=2048 complex, K_seq=15, seed=[7]

ROUTING: GPU (complex matmul + many seeds).

ATOMICITY: tmp+os.replace.
ASCII-only. PRESERVE_ENV_VARS: HDLAB_QUEUE
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch  # PROT-020 GPU gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "substrate_theta_gamma_phase_binding_v1_GPU"
_HARDENING_MARKER = "v1_THETA_GAMMA_PHASE_8_16_32"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")

RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _NAME_SAYS_SMOKE
        or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke")
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


N_DIM_FULL = 8192
K_SEQ_FULL = 100   # capacity-stress; cyclic-shift baseline expected to degrade
SEEDS_FULL = [7, 17, 23]

N_DIM_SMOKE = 2048
K_SEQ_SMOKE = 50   # 1/4 of full K_SEQ; matches dim scaling
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    N_DIM = N_DIM_SMOKE
    K_SEQ = K_SEQ_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    N_DIM = N_DIM_FULL
    K_SEQ = K_SEQ_FULL
    SEEDS = SEEDS_FULL

# Number of distinct items the substrate stores (item codebook).
V_ITEMS_FULL = 1000
V_ITEMS_SMOKE = 200
V_ITEMS = V_ITEMS_SMOKE if RUN_MODE == "smoke" else V_ITEMS_FULL

# Position to probe (mid-sequence; tests middle-of-bundle recall).
PROBE_POS = K_SEQ // 2

# Arm configs: (arm_name, K_phases) where K_phases=0 means cyclic-shift baseline.
ARM_CONFIGS: Tuple[Tuple[str, int], ...] = (
    ("ARM_NO_PHASE", 0),
    ("ARM_THETA_GAMMA_8", 8),
    ("ARM_THETA_GAMMA_16", 16),
    ("ARM_THETA_GAMMA_32", 32),
)
ARM_NAMES: Tuple[str, ...] = tuple(c[0] for c in ARM_CONFIGS)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

HARD_PASS_LIFT_MIN = 0.20
MIDDLE_BAND_LIFT_MIN = 0.05


def _select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


DEVICE = _select_device()
DTYPE_R = torch.float32
DTYPE_C = torch.complex64

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},K_SEQ={K_SEQ},V_ITEMS={V_ITEMS},"
    f"PROBE_POS={PROBE_POS},ARM_CONFIGS={ARM_CONFIGS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"DEVICE={DEVICE.type},"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+THETA_GAMMA_PHASE"
)


def _heartbeat_write(out_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx), "total_units": int(total_units),
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra: row["extra"] = extra
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError: pass


def _cyclic_shift(x, k):
    """Cyclic-shift binding (current substrate baseline). x: (..., N)."""
    return torch.roll(x, shifts=k, dims=-1)


def _arm_hash(arm_name, bundle_re):
    """Hash bundle's real-part sub-slice."""
    sample = bundle_re[:64].detach().cpu().to(torch.float64).numpy()
    blob = arm_name.encode("ascii") + sample.tobytes()
    return hashlib.sha256(blob).hexdigest()[:16]


def run_arm(arm_name, K_phases, seed, item_codebook, out_dir):
    """Bind K_SEQ items into a sequence bundle; probe PROBE_POS; measure recall.

    item_codebook: (V_ITEMS, N_DIM) real bipolar codes.

    NO_PHASE: bundle = sum_pos cyclic_shift(item[seq_pos], pos)
              probe = cyclic_shift(bundle, -PROBE_POS); recall = argmax cosine
              over codebook
    THETA_GAMMA: bundle (complex) = sum_pos item[seq_pos] * exp(i*phi_pos)
                 phi_pos = 2*pi * (pos % K_phases) / K_phases
                 probe = bundle * exp(-i*phi_PROBE_POS); take real part;
                 recall = argmax cosine over codebook
    """
    t0 = time.time()
    try:
        rng = np.random.RandomState(seed + 17)
        # Sequence: K_SEQ items drawn from codebook (with replacement OK).
        seq_item_ids = rng.randint(0, V_ITEMS, size=K_SEQ)
        target_id = int(seq_item_ids[PROBE_POS])

        if K_phases == 0:
            # Cyclic-shift baseline (real).
            bundle = torch.zeros(N_DIM, dtype=DTYPE_R, device=DEVICE)
            for pos in range(K_SEQ):
                shifted = _cyclic_shift(item_codebook[seq_item_ids[pos]], pos)
                bundle = bundle + shifted
            probe = _cyclic_shift(bundle, -PROBE_POS)
            probe_n = probe / max(float(torch.linalg.norm(probe).item()), 1e-12)
            codebook_n = item_codebook / torch.clamp(
                torch.linalg.norm(item_codebook, dim=1, keepdim=True), min=1e-12)
            sims = codebook_n @ probe_n
            recall_id = int(torch.argmax(sims).item())
            recall_match = float(recall_id == target_id)
            cos_to_target = float(sims[target_id].item())
            bundle_for_hash = bundle.detach()
        else:
            # Complex phase binding.
            phase_idx = torch.arange(K_SEQ, device=DEVICE) % K_phases
            phi_pos = 2.0 * math.pi * phase_idx.to(DTYPE_R) / K_phases
            # item_codebook is real bipolar; treat as complex with zero imag.
            codebook_c = item_codebook.to(DTYPE_C)
            # bundle = sum_pos item[seq_pos] * exp(i*phi_pos)
            phase_factors = torch.exp(1j * phi_pos)  # (K_SEQ,) complex
            seq_items_c = codebook_c[seq_item_ids]   # (K_SEQ, N_DIM) complex
            bundle_c = (seq_items_c * phase_factors[:, None]).sum(dim=0)
            # Probe: multiply by conjugate of probe-position phase.
            probe_phase = phase_factors[PROBE_POS].conj()
            probe_c = bundle_c * probe_phase
            # Take real part (matches codebook's real-bipolar codes).
            probe_re = probe_c.real
            probe_n = probe_re / max(float(torch.linalg.norm(probe_re).item()), 1e-12)
            codebook_n = item_codebook / torch.clamp(
                torch.linalg.norm(item_codebook, dim=1, keepdim=True), min=1e-12)
            sims = codebook_n @ probe_n
            recall_id = int(torch.argmax(sims).item())
            recall_match = float(recall_id == target_id)
            cos_to_target = float(sims[target_id].item())
            bundle_for_hash = probe_re.detach()

        _heartbeat_write(out_dir, unit_idx=0, total_units=1,
                         elapsed_s=time.time() - t0,
                         extra={"arm": arm_name, "K_phases": K_phases,
                                "target_id": target_id, "recall_id": recall_id,
                                "seed": int(seed)})

        # Re-run with MANY (item) replays to get robust accuracy estimate.
        # Aggregate over N_PROBE_TRIALS distinct probes.
        N_PROBE_TRIALS = 50 if RUN_MODE == "full" else 10
        hits = 0
        cosines = []
        for trial in range(N_PROBE_TRIALS):
            trial_seq = rng.randint(0, V_ITEMS, size=K_SEQ)
            trial_target = int(trial_seq[PROBE_POS])
            if K_phases == 0:
                bundle = torch.zeros(N_DIM, dtype=DTYPE_R, device=DEVICE)
                for pos in range(K_SEQ):
                    bundle = bundle + _cyclic_shift(item_codebook[trial_seq[pos]], pos)
                probe = _cyclic_shift(bundle, -PROBE_POS)
                probe_n = probe / max(float(torch.linalg.norm(probe).item()), 1e-12)
                sims = codebook_n @ probe_n
            else:
                seq_items_c = codebook_c[trial_seq]
                bundle_c = (seq_items_c * phase_factors[:, None]).sum(dim=0)
                probe_re = (bundle_c * probe_phase).real
                probe_n = probe_re / max(float(torch.linalg.norm(probe_re).item()), 1e-12)
                sims = codebook_n @ probe_n
            r_id = int(torch.argmax(sims).item())
            hits += int(r_id == trial_target)
            cosines.append(float(sims[trial_target].item()))

        accuracy = hits / float(N_PROBE_TRIALS)
        mean_cos = float(np.mean(cosines))

        arm_hash_val = _arm_hash(arm_name, bundle_for_hash)

        wall = time.time() - t0
        return {
            "arm_name": arm_name, "K_phases": int(K_phases), "seed": int(seed),
            "recall_accuracy": float(accuracy),
            "mean_cos_to_target": float(mean_cos),
            "n_probe_trials": int(N_PROBE_TRIALS),
            "arm_hash": str(arm_hash_val),
            "wall_s": float(wall), "arm_status": "OK",
        }
    except Exception as exc:
        return {
            "arm_name": arm_name, "K_phases": int(K_phases), "seed": int(seed),
            "recall_accuracy": float("nan"),
            "mean_cos_to_target": float("nan"),
            "n_probe_trials": 0, "arm_hash": "ERROR",
            "wall_s": float(time.time() - t0),
            "arm_status": f"ERROR: {type(exc).__name__}: {str(exc)[:200]}",
        }


def run_seed(seed, out_dir):
    t0 = time.time()
    rng = np.random.RandomState(seed)
    # Item codebook: V_ITEMS bipolar codes of dim N_DIM.
    codebook_np = rng.choice([-1.0, 1.0], size=(V_ITEMS, N_DIM)).astype(np.float32)
    item_codebook = torch.from_numpy(codebook_np).to(DEVICE)

    print(f"  [seed={seed}] N_DIM={N_DIM} K_SEQ={K_SEQ} V_ITEMS={V_ITEMS} "
          f"PROBE_POS={PROBE_POS} dev={DEVICE.type} run_mode={RUN_MODE}",
          flush=True)

    arms = []
    for arm_name, K_phases in ARM_CONFIGS:
        out = run_arm(arm_name, K_phases, seed, item_codebook, out_dir)
        arms.append(out)
        print(f"  [seed={seed} {arm_name:>20s} K_phases={K_phases:>3d}] "
              f"acc={out['recall_accuracy']:.3f} "
              f"mean_cos={out['mean_cos_to_target']:.3f} "
              f"hash={out['arm_hash']} status={out['arm_status'][:30]} "
              f"wall={out['wall_s']:.1f}s", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed), "N": N_DIM, "N_DIM": N_DIM, "K_SEQ": K_SEQ,
        "V_ITEMS": V_ITEMS, "PROBE_POS": PROBE_POS,
        "n_arms": len(ARM_NAMES), "backend": "torch", "device": DEVICE.type,
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arm_configs": [{"name": n, "K_phases": k} for n, k in ARM_CONFIGS],
        "arms": arms, "elapsed_s": float(elapsed),
    }


def _arm_metric_mean(arms_across, arm_name, key):
    vals = [float(a[key]) for sa in arms_across for a in sa
            if a["arm_name"] == arm_name and a["arm_status"] == "OK"]
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hashes(arms_across, arm_name):
    return [str(a["arm_hash"]) for sa in arms_across for a in sa
            if a["arm_name"] == arm_name and a["arm_status"] == "OK"]


def compute_verdict(results):
    if not results: return ("HARD_FAIL", "No seed results.")
    if len(results) != len(SEEDS):
        return ("HARD_FAIL", f"CARDINALITY_BREACH seeds")
    arms_across = []
    for r in results:
        if len(r.get("arms", [])) != len(ARM_NAMES):
            return ("HARD_FAIL", f"CARDINALITY_BREACH seed={r.get('seed')}")
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL", f"seed={r['seed']} arm={a['arm_name']} {a['arm_status']}")
        arms_across.append(r["arms"])

    af_v = []
    for i in range(len(ARM_NAMES)):
        for j in range(i + 1, len(ARM_NAMES)):
            a1, a2 = ARM_NAMES[i], ARM_NAMES[j]
            h1, h2 = _arm_hashes(arms_across, a1), _arm_hashes(arms_across, a2)
            any_diff = any(x != y for x, y in zip(h1, h2))
            if not any_diff and h1 and h2: af_v.append(f"{a1}/{a2}")
    if af_v: return ("HARD_FAIL", f"META_RULE_AF VIOLATION: {af_v}")

    accs = {arm: _arm_metric_mean(arms_across, arm, "recall_accuracy")
            for arm in ARM_NAMES}
    R_NO = accs["ARM_NO_PHASE"]
    theta_arms = [a for a in ARM_NAMES if a != "ARM_NO_PHASE"]
    best_arm = max(theta_arms, key=lambda a: accs[a])
    best_acc = accs[best_arm]
    best_lift = best_acc - R_NO

    summary_arm = " ".join(f"{a}={accs[a]:.3f}" for a in ARM_NAMES)
    summary = (f"N_DIM={N_DIM} K_SEQ={K_SEQ} V_ITEMS={V_ITEMS} "
               f"PROBE_POS={PROBE_POS} mode={RUN_MODE} {summary_arm} | "
               f"best_arm={best_arm} best_lift={best_lift:+.3f} R_NO_PHASE={R_NO:.3f}")

    if best_lift >= HARD_PASS_LIFT_MIN:
        return ("HARD_PASS",
                f"HARD_PASS (THETA_GAMMA_PHASE_CONFIRMED): {best_arm} lifts "
                f"position-binding accuracy by {best_lift:+.3f}. {summary}")
    if best_lift >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial phase-binding lift {best_lift:+.3f}. {summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: phase-binding does not improve over cyclic-shift "
            f"(best lift {best_lift:+.3f}). {summary}")


def _selftest_cyclic_shift():
    x = torch.arange(8, dtype=DTYPE_R, device=DEVICE)
    y = _cyclic_shift(x, 2)
    expected = torch.tensor([6, 7, 0, 1, 2, 3, 4, 5], dtype=DTYPE_R, device=DEVICE)
    if not torch.allclose(y, expected):
        raise AssertionError(f"cyclic_shift wrong: {y.cpu().numpy()} != {expected.cpu().numpy()}")


def _selftest_arm_count():
    if len(set(ARM_NAMES)) != len(ARM_NAMES):
        raise AssertionError("ARM_NAMES duplicates")
    if len(ARM_NAMES) * len(SEEDS) != EXPECTED_N_UNITS:
        raise AssertionError("EXPECTED_N_UNITS mismatch")


def _selftest_phase_orthogonality():
    """At K_phases=8, phi_0 and phi_4 should be opposite (cos=-1)."""
    K = 8
    phis = 2.0 * math.pi * np.arange(K) / K
    cos_0_4 = np.cos(phis[0] - phis[4])
    if abs(cos_0_4 - (-1.0)) > 1e-6:
        raise AssertionError(f"phase 0 vs 4 not orthogonal: cos={cos_0_4}")


def _selftest_torch():
    if not hasattr(torch, "complex64"):
        raise AssertionError("torch.complex64 missing")
    z = torch.tensor([1.0 + 0.0j], dtype=DTYPE_C, device=DEVICE)
    if z.real.item() != 1.0:
        raise AssertionError("complex .real broken")


def _instrumentation_selftest():
    try:
        _selftest_torch()
        _selftest_cyclic_shift()
        _selftest_phase_orthogonality()
        _selftest_arm_count()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True); sys.exit(2)
    except SystemExit: raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        sys.exit(3)
    print(f"[selftest] PASS  N_DIM={N_DIM}  K_SEQ={K_SEQ}  V_ITEMS={V_ITEMS}  "
          f"PROBE_POS={PROBE_POS}  arms={ARM_NAMES}  device={DEVICE.type}  "
          f"expected_n_units={EXPECTED_N_UNITS}  mode={RUN_MODE}  "
          f"marker={_HARDENING_MARKER}", flush=True)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "anchor_name": anchor_name, "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "run_mode": RUN_MODE,
    }
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(final))
    except Exception: pass


def _main():
    _instrumentation_selftest()
    if _ARGS.self_test: sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "_start_marker.txt").write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} device={DEVICE.type}",
        encoding="utf-8")

    try:
        run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
        done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
        print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds done; running {remaining}", flush=True)
        t_sweep_start = time.time()
        for seed in remaining:
            print(f"[seed={seed}] {ANCHOR_NAME} run_mode={RUN_MODE}...", flush=True)
            result = run_seed(seed, out_dir)
            write_partial(out_dir, seed, result)

        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        all_results = list(per_seed.values())
        verdict, verdict_msg = compute_verdict(all_results)
        elapsed_s = time.time() - t_sweep_start
        print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
        print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

        mode_in_results = {r.get("run_mode", "?") for r in all_results}
        if RUN_MODE == "full" and "smoke" in mode_in_results:
            verdict = "HARD_FAIL"
            verdict_msg = "HARD_FAIL: stale smoke partials. " + verdict_msg

        per_arm_rows = []
        for arm_name in ARM_NAMES:
            accs, coss, k_p = [], [], None
            for r in all_results:
                for a in r.get("arms", []):
                    if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                        accs.append(float(a["recall_accuracy"]))
                        coss.append(float(a["mean_cos_to_target"]))
                        k_p = a.get("K_phases")
            if accs:
                per_arm_rows.append({
                    "arm_name": arm_name, "K_phases": k_p,
                    "recall_accuracy_mean": float(np.mean(accs)),
                    "recall_accuracy_std": float(np.std(accs)) if len(accs) > 1 else 0.0,
                    "mean_cos_to_target_mean": float(np.mean(coss)),
                    "n_seeds_ok": len(accs),
                })

        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
            "summary": (f"n_seeds={len(all_results)} N_DIM={N_DIM} K_SEQ={K_SEQ} "
                       f"V_ITEMS={V_ITEMS} PROBE_POS={PROBE_POS} arms={ARM_NAMES} "
                       f"mode={RUN_MODE} device={DEVICE.type} theta_gamma_phase_binding"),
            "elapsed_s": float(elapsed_s), "config_version": CONFIG_VERSION,
            "N_DIM": N_DIM, "K_SEQ": K_SEQ, "V_ITEMS": V_ITEMS, "PROBE_POS": PROBE_POS,
            "backend": "torch", "device": DEVICE.type, "n_seeds": len(SEEDS),
            "expected_n_units": EXPECTED_N_UNITS,
            "cardinality_ok": (len(all_results) == len(SEEDS)
                               and all(len(r.get("arms", [])) == len(ARM_NAMES)
                                       for r in all_results)),
            "run_mode": RUN_MODE,
            "arm_configs": [{"name": n, "K_phases": k} for n, k in ARM_CONFIGS],
            "per_arm_rows": per_arm_rows,
            "per_seed": [{"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"),
                         "arms": r.get("arms")} for r in all_results],
        }
        metrics_path = out_dir / "metrics.json"
        tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp_path), str(metrics_path))
        print(f"[metrics] written to {metrics_path}", flush=True)
    except SystemExit: raise
    except KeyboardInterrupt: raise
    except Exception as exc:
        _write_crash_metrics(out_dir, ANCHOR_NAME, exc); raise


if __name__ == "__main__":
    _main()
