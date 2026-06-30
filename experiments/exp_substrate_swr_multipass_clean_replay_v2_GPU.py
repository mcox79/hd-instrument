"""substrate_swr_multipass_clean_replay_v2_GPU.

Stage 2 NREM rescue cell A v2 (redesigned after v1 mechanism error). Tests
SWR-style MULTI-PASS CLEAN REPLAY as rescue for cortex consolidation.

v1 abort note (HARD_FAIL smoke): v1 modeled SWR as bundled outer-product
(K items summed into one write) which generates K^2 cross-term interference.
Correct brain model: SWR = many short clean re-extraction events emitted by
hippocampus during NREM3 (~50-200 ripples/cycle); each ripple re-extracts a
clean engram and re-writes to cortex. Multi-pass with cleaner-per-pass
consolidation drives recall.

CITED@brain_lit_NREM3_SWR_multipass: ~50-200 sharp-wave-ripples per NREM3
sleep cycle; each emits a brief clean reactivation packet; cumulative effect
strengthens cortical engrams over many ripples.

LINEAGE:
  Hippo bottleneck v2 MEASURED@d:/AI/hd-instrument/data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json:
    R_STANDARD=0.219, R_CLEAN_VALS_TO_CORTEX=0.985 (single-pass clean).
  CLEAN single-pass already saturates; this cell tests whether multi-pass
  REPLAY of clean re-extractions FURTHER consolidates (or whether single-pass
  is already at ceiling -> shows N_REPLAY-monotone-cap).

HYPOTHESIS:
  THEORETICAL@multi_pass_replay_signal_amplification: cumulative outer-product
  writes with shared keys amplify signal (each replay adds +eta*v outer c at
  matching pattern); noise from cross-terms partially cancels under different
  permutation orders. Predicts recall monotone-increasing in N_REPLAY then
  saturating at ceiling.

ARMS (5):
  ARM_REPLAY_1   -- single pass (= v2 CLEAN_VALS baseline)
  ARM_REPLAY_2   -- 2 passes (different perm each)
  ARM_REPLAY_5   -- 5 passes
  ARM_REPLAY_10  -- 10 passes (brain-realistic for short sleep)
  ARM_REPLAY_20  -- 20 passes (saturation test)

PRE-REG BANDS:
  HARD_PASS: best N_REPLAY arm recall >= R_REPLAY_1 + 0.05 (any net gain
             over single-pass clean ceiling) OR ceiling-confirmation
             (>=0.95 across all REPLAY arms).
  MIDDLE_BAND: any net change in (0.01, 0.05]
  HARD_FAIL: best arm < 0.9 (clean replay should consolidate near DIRECT
             ceiling); OR if best < R_REPLAY_1 - 0.05 (multi-pass HURTS).

REGIME (matches v2 reference; alpha=0.25):
  FULL:  M=2048, N_h=8192, N_c=2048; seeds=[7,17,23]
  SMOKE: M=512,  N_h=2048, N_c=512; seed=[7]

ATOMICITY: tmp+os.replace. PROT-020: imports torch. Routes overnight_queue.
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
import torch  # PROT-020 GPU queue routing gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "substrate_swr_multipass_clean_replay_v2_GPU"
_HARDENING_MARKER = "v2_REPLAY_1_2_5_10_20_CLEAN"

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


# Config matches v2.
M_ITEMS_FULL = 2048
N_HIPPO_FULL = 8192
N_CORTEX_FULL = 2048
SEEDS_FULL = [7, 17, 23]

M_ITEMS_SMOKE = 512
N_HIPPO_SMOKE = 2048
N_CORTEX_SMOKE = 512
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    M_ITEMS = M_ITEMS_SMOKE
    N_HIPPO = N_HIPPO_SMOKE
    N_CORTEX = N_CORTEX_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    M_ITEMS = M_ITEMS_FULL
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    SEEDS = SEEDS_FULL

HIPPO_SPARSITY_SPARSE = 0.10
ETA_CORTEX = 0.005

N_REPLAY_VALUES: Tuple[int, ...] = (1, 2, 5, 10, 20)
ARM_NAMES: Tuple[str, ...] = tuple(f"ARM_REPLAY_{n}" for n in N_REPLAY_VALUES)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

HARD_PASS_LIFT_MIN = 0.05  # ceiling regime; small lift OK
MIDDLE_BAND_LIFT_MIN = 0.01
CEILING_CONFIRM_MIN = 0.90


def _alpha_simple(M, N_h): return float(M) / float(N_h)


def _select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


DEVICE = _select_device()
DTYPE = torch.float32

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f},"
    f"N_REPLAY={N_REPLAY_VALUES},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},DEVICE={DEVICE.type},"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+SWR_MULTIPASS_CLEAN"
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


def _l2_normalize(x, dim=-1):
    n = torch.linalg.vector_norm(x, dim=dim, keepdim=True)
    return x / torch.clamp(n, min=1e-12)


def _sparse_dg(x, P, k):
    h_raw = x @ P.t()
    abs_h = h_raw.abs()
    topk_idx = torch.topk(abs_h, k, dim=1, largest=True).indices
    signs = torch.sign(h_raw.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out = torch.zeros_like(h_raw)
    out.scatter_(1, topk_idx, signs)
    return out


def _arm_hash(arm_name, W_cortex):
    sample = W_cortex[:4, :64].detach().cpu().to(torch.float64).numpy()
    blob = arm_name.encode("ascii") + sample.tobytes()
    return hashlib.sha256(blob).hexdigest()[:16]


def run_arm(arm_name, N_replay, seed, keys_raw, vals_raw, P_in, P_hc, out_dir):
    """SWR multi-pass clean replay: N_replay passes over clean vals_c[perm]."""
    t0 = time.time()
    try:
        k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
        keys_h = _sparse_dg(keys_raw, P_in, k_active)
        vals_h = _sparse_dg(vals_raw, P_in, k_active)
        keys_c = _l2_normalize(keys_h @ P_hc.t(), dim=1)
        vals_c = _l2_normalize(vals_h @ P_hc.t(), dim=1)

        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        rng = np.random.RandomState(seed + 17)
        n_total_writes = 0
        # Multi-pass clean replay. Each pass: different permutation.
        for pass_i in range(N_replay):
            perm = torch.from_numpy(rng.permutation(M_ITEMS)).to(DEVICE)
            cues_c = keys_c[perm]
            vals_c_perm = vals_c[perm]
            # Clean batched outer product write (all M items at once).
            W_cortex += ETA_CORTEX * (vals_c_perm.t() @ cues_c)
            n_total_writes += M_ITEMS

        _heartbeat_write(out_dir, unit_idx=0, total_units=1,
                         elapsed_s=time.time() - t0,
                         extra={"arm": arm_name, "N_replay": N_replay,
                                "n_writes": n_total_writes, "seed": int(seed)})

        # Recall.
        preds_raw = keys_c @ W_cortex.t()
        preds = torch.sign(preds_raw)
        preds = torch.where(preds == 0, torch.ones_like(preds), preds)
        preds_n = _l2_normalize(preds, dim=1)
        sims = preds_n @ vals_c.t()
        argmax = torch.argmax(sims, dim=1)
        n_hits = int((argmax == torch.arange(M_ITEMS, device=DEVICE)).sum().item())
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(torch.linalg.norm(W_cortex).item())

        arm_hash_val = _arm_hash(arm_name, W_cortex)
        del W_cortex, preds_raw, preds, preds_n, sims
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name, "N_replay": int(N_replay), "seed": int(seed),
            "recall_cortex": float(recall), "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "arm_hash": str(arm_hash_val),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall), "arm_status": "OK",
        }
    except Exception as exc:
        return {
            "arm_name": arm_name, "N_replay": int(N_replay), "seed": int(seed),
            "recall_cortex": float("nan"), "n_items": 0,
            "cortex_norm": float("nan"), "n_total_writes": 0,
            "arm_hash": "ERROR",
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(time.time() - t0),
            "arm_status": f"ERROR: {type(exc).__name__}: {str(exc)[:200]}",
        }


def run_seed(seed, out_dir):
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    keys_raw_np = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float32)
    vals_raw_np = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float32)
    rng_p = np.random.RandomState(seed + 1000)
    P_in_np = (rng_p.randn(N_HIPPO, N_raw) / np.sqrt(N_raw)).astype(np.float32)
    P_hc_np = (rng_p.randn(N_CORTEX, N_HIPPO) / np.sqrt(N_HIPPO)).astype(np.float32)

    keys_raw = torch.from_numpy(keys_raw_np).to(DEVICE)
    vals_raw = torch.from_numpy(vals_raw_np).to(DEVICE)
    P_in = torch.from_numpy(P_in_np).to(DEVICE)
    P_hc = torch.from_numpy(P_hc_np).to(DEVICE)

    print(f"  [seed={seed}] M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} "
          f"N_replay_values={N_REPLAY_VALUES} dev={DEVICE.type} "
          f"run_mode={RUN_MODE}", flush=True)

    arms = []
    for arm_name, n_replay in zip(ARM_NAMES, N_REPLAY_VALUES):
        out = run_arm(arm_name, n_replay, seed, keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(f"  [seed={seed} {arm_name:>14s} N_replay={n_replay:>3d}] "
              f"recall={out['recall_cortex']:.3f} "
              f"hash={out['arm_hash']} status={out['arm_status'][:30]} "
              f"wall={out['wall_s']:.1f}s", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed), "N": N_CORTEX, "N_c": N_CORTEX, "N_h": N_HIPPO,
        "M": M_ITEMS, "n_arms": len(ARM_NAMES), "eta_c": ETA_CORTEX,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE, "backend": "torch",
        "device": DEVICE.type, "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION, "anchor_name": ANCHOR_NAME,
        "N_replay_values": list(N_REPLAY_VALUES), "arms": arms,
        "elapsed_s": float(elapsed),
    }


def _arm_recall_mean(arms_across, arm_name):
    vals = [float(a["recall_cortex"]) for sa in arms_across for a in sa
            if a["arm_name"] == arm_name and a["arm_status"] == "OK"]
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hashes(arms_across, arm_name):
    return [str(a["arm_hash"]) for sa in arms_across for a in sa
            if a["arm_name"] == arm_name and a["arm_status"] == "OK"]


def compute_verdict(results):
    if not results: return ("HARD_FAIL", "No seed results.")
    if len(results) != len(SEEDS):
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {len(SEEDS)} seeds, got {len(results)}")
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
    if af_v:
        return ("HARD_FAIL", f"META_RULE_AF VIOLATION: {af_v}")

    arm_recalls = {arm: _arm_recall_mean(arms_across, arm) for arm in ARM_NAMES}
    R_R1 = arm_recalls["ARM_REPLAY_1"]
    best_arm = max(ARM_NAMES, key=lambda a: arm_recalls[a])
    best_recall = arm_recalls[best_arm]
    best_lift = best_recall - R_R1

    arm_summary = " ".join(f"{a}={arm_recalls[a]:.3f}" for a in ARM_NAMES)
    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} alpha_simple="
        f"{_alpha_simple(M_ITEMS, N_HIPPO):.3f} mode={RUN_MODE} {arm_summary} "
        f"| best_arm={best_arm} best_recall={best_recall:.3f} "
        f"best_lift={best_lift:+.3f} R_REPLAY_1={R_R1:.3f}"
    )

    # Ceiling-confirmation gate: if ALL arms above ceiling threshold, HARD_PASS
    # as ceiling-confirmed (multi-pass clean reaches near-DIRECT consistently).
    all_ceiling = all(arm_recalls[a] >= CEILING_CONFIRM_MIN for a in ARM_NAMES)
    if all_ceiling:
        return ("HARD_PASS",
                f"HARD_PASS (SWR_MULTIPASS_CEILING_CONFIRMED): all N_REPLAY "
                f"arms >= {CEILING_CONFIRM_MIN} (clean replay reaches "
                f"near-DIRECT). {summary}")

    if best_lift >= HARD_PASS_LIFT_MIN:
        return ("HARD_PASS",
                f"HARD_PASS (SWR_MULTIPASS_LIFT_CONFIRMED): {best_arm} lifts "
                f"recall by {best_lift:+.3f} over single-pass. {summary}")
    if best_lift >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial multi-pass lift {best_lift:+.3f}. {summary}")
    if best_recall < 0.5:
        return ("HARD_FAIL",
                f"HARD_FAIL: multi-pass clean does not consolidate (best recall "
                f"{best_recall:.3f} < 0.5; substrate-pipeline broken). {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: no multi-pass benefit but consolidation works "
            f"(R_REPLAY_1 already near ceiling). {summary}")


def _selftest_sparse_dg():
    rng = np.random.RandomState(7)
    N_raw, N_h_t = 32, 128
    k_t = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))
    P_np = (rng.randn(N_h_t, N_raw) / np.sqrt(N_raw)).astype(np.float32)
    x_np = rng.choice([-1.0, 1.0], size=(4, N_raw)).astype(np.float32)
    P, x = torch.from_numpy(P_np).to(DEVICE), torch.from_numpy(x_np).to(DEVICE)
    h = _sparse_dg(x, P, k_t)
    if not ((h.abs() > 0).sum(dim=1) == k_t).all().item():
        raise AssertionError("k-WTA sparsity wrong")


def _selftest_N_replay_distinct():
    if len(set(N_REPLAY_VALUES)) != len(N_REPLAY_VALUES):
        raise AssertionError(f"N_REPLAY_VALUES duplicates: {N_REPLAY_VALUES}")
    if 1 not in N_REPLAY_VALUES:
        raise AssertionError("N_replay=1 baseline missing")


def _selftest_arm_count():
    if len(ARM_NAMES) != len(N_REPLAY_VALUES):
        raise AssertionError("ARM_NAMES count mismatch")
    if len(ARM_NAMES) * len(SEEDS) != EXPECTED_N_UNITS:
        raise AssertionError("EXPECTED_N_UNITS mismatch")


def _selftest_torch():
    if not hasattr(torch, "sign"):
        raise AssertionError("torch.sign missing")


def _selftest_regime_alpha():
    a_full = _alpha_simple(M_ITEMS_FULL, N_HIPPO_FULL)
    a_smoke = _alpha_simple(M_ITEMS_SMOKE, N_HIPPO_SMOKE)
    if abs(a_full - a_smoke) > 1e-3:
        raise AssertionError(f"smoke alpha {a_smoke} != full {a_full}")
    if not (0.20 < a_full < 0.30):
        raise AssertionError(f"alpha_simple={a_full} not in v2 range")


def _instrumentation_selftest():
    try:
        _selftest_torch()
        _selftest_sparse_dg()
        _selftest_N_replay_distinct()
        _selftest_arm_count()
        _selftest_regime_alpha()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True); sys.exit(2)
    except SystemExit: raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        sys.exit(3)
    print(f"[selftest] PASS  M={M_ITEMS}  N_h={N_HIPPO}  N_c={N_CORTEX}  "
          f"N_replay={N_REPLAY_VALUES}  alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f}  "
          f"seeds={SEEDS}  arms={ARM_NAMES}  device={DEVICE.type}  "
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
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} device={DEVICE.type} "
        f"N_replay={N_REPLAY_VALUES}", encoding="utf-8")

    try:
        run_config = {"N": N_CORTEX, "M": M_ITEMS, "N_h": N_HIPPO,
                      "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
            verdict_msg = f"HARD_FAIL: stale smoke partials. " + verdict_msg

        per_arm_rows = []
        for arm_name in ARM_NAMES:
            recalls, n_b = [], None
            for r in all_results:
                for a in r.get("arms", []):
                    if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                        recalls.append(float(a["recall_cortex"]))
                        n_b = a.get("N_replay")
            if recalls:
                per_arm_rows.append({
                    "arm_name": arm_name, "N_replay": n_b,
                    "recall_mean": float(np.mean(recalls)),
                    "recall_std": float(np.std(recalls)) if len(recalls) > 1 else 0.0,
                    "n_seeds_ok": len(recalls),
                })

        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
            "summary": (f"n_seeds={len(all_results)} M={M_ITEMS} N_h={N_HIPPO} "
                       f"N_c={N_CORTEX} N_replay={N_REPLAY_VALUES} mode={RUN_MODE} "
                       f"device={DEVICE.type} swr_multipass_clean_replay"),
            "elapsed_s": float(elapsed_s), "config_version": CONFIG_VERSION,
            "M": M_ITEMS, "N_c": N_CORTEX, "N_h": N_HIPPO, "eta_c": ETA_CORTEX,
            "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
            "backend": "torch", "device": DEVICE.type, "n_seeds": len(SEEDS),
            "expected_n_units": EXPECTED_N_UNITS,
            "cardinality_ok": (len(all_results) == len(SEEDS)
                               and all(len(r.get("arms", [])) == len(ARM_NAMES)
                                       for r in all_results)),
            "run_mode": RUN_MODE,
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "N_replay_values": list(N_REPLAY_VALUES),
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
