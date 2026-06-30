"""substrate_sleep_spindles_iterative_consolidation_v1_CPU.

Stage 2 NREM rescue cell D. Tests NREM2 SLEEP-SPINDLE iterative consolidation
(slow ~12-15Hz rhythm; separate from NREM3 SWR bursts) as rescue for Hc
CORTEX_WRITE_SATURATION.

CITED@brain_lit_sleep_spindles_NREM2: spindles run iterative reactivation +
gradient-style cortical integration, NOT burst-transmit. Slow waves +
spindles + ripples cycle (NREM2 -> NREM3 -> back); spindles + ripples
together strongest learning consolidation.

LINEAGE:
  Hippo bottleneck v2 confirmed Hc (cortex write saturation).
  This cell tests: iterative gradient-style consolidation (read + correct +
  rewrite) vs one-shot Hebbian outer-product write.

HYPOTHESIS:
  THEORETICAL@iterative_gradient_consolidation: one-shot Hebbian write
  W += eta * v outer c writes the FULL outer product; cumulative interference
  among M items. Gradient consolidation: per-item, read current pred = sign(W @ c),
  compute residual = (v - L2(pred)); update W += eta * residual outer c.
  Self-correcting: items already well-stored don't add interference; items
  poorly stored get amplified. Slower per-item but lower cumulative noise.

ARMS (5):
  ARM_RIPPLE_ONLY      -- baseline: one-shot Hebbian write per item (=STANDARD)
  ARM_SPINDLE_ONLY     -- gradient/residual write per item (no ripple)
  ARM_RIPPLE_THEN_SPINDLE -- ripple write then spindle correction (sequence)
  ARM_SPINDLE_THEN_RIPPLE -- spindle correction first then ripple consolidation
  ARM_INTERLEAVED      -- ripple write item i, spindle correct items [0..i]

PRE-REG BANDS:
  HARD_PASS: best non-RIPPLE_ONLY recall >= R_RIPPLE_ONLY + 0.30
  MIDDLE_BAND: best in (R_RIPPLE_ONLY+0.05, R_RIPPLE_ONLY+0.30]
  HARD_FAIL: no arm >= R_RIPPLE_ONLY + 0.05

REGIME (matches v2): M=2048, N_h=8192, N_c=2048, alpha=0.25, seeds=[7,17,23]
SMOKE: M=512, N_h=2048, N_c=512.

DISCRIMINATOR-MUST-SURVIVE-SCALE: same alpha at smoke + full.
ROUTING: CPU (iterative per-item dynamics; not GPU-amenable).

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

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "substrate_sleep_spindles_iterative_consolidation_v1_CPU"
_HARDENING_MARKER = "v1_RIPPLE_SPINDLE_SEQUENCE"

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
ETA_SPINDLE = 0.005  # gradient learning rate for spindle phase

ARM_NAMES: Tuple[str, ...] = (
    "ARM_RIPPLE_ONLY",
    "ARM_SPINDLE_ONLY",
    "ARM_RIPPLE_THEN_SPINDLE",
    "ARM_SPINDLE_THEN_RIPPLE",
    "ARM_INTERLEAVED",
)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

HARD_PASS_LIFT_MIN = 0.30
MIDDLE_BAND_LIFT_MIN = 0.05


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f},"
    f"ARM_NAMES={ARM_NAMES},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},backend=numpy,"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+SPINDLE_RIPPLE_SEQUENCE"
)


def _heartbeat_write(out_dir: Path, unit_idx: int, total_units: int,
                     elapsed_s: float, extra: Dict = None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units),
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _l2_normalize_batch(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.maximum(norms, 1e-12)


def _l2_normalize_one(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / max(n, 1e-12)


def _sparse_dg(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    h_raw = x @ P.T
    abs_h = np.abs(h_raw)
    topk_idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]
    rows = np.arange(h_raw.shape[0])[:, None]
    signs = np.sign(h_raw[rows, topk_idx])
    signs[signs == 0] = 1.0
    out = np.zeros_like(h_raw)
    out[rows, topk_idx] = signs
    return out


def _arm_hash(arm_name: str, W: np.ndarray) -> str:
    sample = W[:4, :64].astype(np.float64)
    blob = arm_name.encode("ascii") + sample.tobytes()
    return hashlib.sha256(blob).hexdigest()[:16]


def _ripple_write(W: np.ndarray, v: np.ndarray, c: np.ndarray) -> None:
    """One-shot Hebbian outer product (NREM3 SWR ripple write). In-place."""
    W += ETA_CORTEX * np.outer(v, c)


def _spindle_correct(W: np.ndarray, v: np.ndarray, c: np.ndarray) -> None:
    """Gradient/residual correction (NREM2 spindle). In-place.

    Reads current prediction, computes residual, updates W toward target.
    Self-correcting: items already well-stored get small updates;
    poorly-stored items get larger updates.
    """
    pred_raw = W @ c
    pred = np.sign(pred_raw)
    pred[pred == 0] = 1.0
    pred_n = _l2_normalize_one(pred)
    residual = v - pred_n
    W += ETA_SPINDLE * np.outer(residual, c)


def run_arm(arm_name: str, seed: int,
            keys_raw: np.ndarray, vals_raw: np.ndarray,
            P_in: np.ndarray, P_hc: np.ndarray,
            out_dir: Path) -> Dict:
    """Sleep-spindle vs ripple arm variants."""
    t0 = time.time()
    try:
        k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
        keys_h = _sparse_dg(keys_raw, P_in, k_active)
        vals_h = _sparse_dg(vals_raw, P_in, k_active)

        keys_c = _l2_normalize_batch(keys_h @ P_hc.T)
        vals_c = _l2_normalize_batch(vals_h @ P_hc.T)

        # Hippo Hebbian readout (STANDARD path; produces noisy vals_c_react).
        W_h = vals_h.T @ keys_h
        rng = np.random.RandomState(seed + 17)
        perm = rng.permutation(M_ITEMS)
        cues_h = keys_h[perm]
        cues_c = keys_c[perm]
        vals_react_h_raw = cues_h @ W_h.T
        vals_react_h = np.sign(vals_react_h_raw)
        vals_react_h[vals_react_h == 0] = 1.0
        vals_c_react = _l2_normalize_batch(vals_react_h @ P_hc.T)
        del W_h, vals_react_h_raw, vals_react_h

        # Cortex write phase per arm.
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        n_total_writes = 0
        n_spindle_corrections = 0

        if arm_name == "ARM_RIPPLE_ONLY":
            for i in range(M_ITEMS):
                _ripple_write(W_cortex, vals_c_react[i], cues_c[i])
                n_total_writes += 1

        elif arm_name == "ARM_SPINDLE_ONLY":
            # Use clean v_react = vals_c_react; gradient correction only.
            for i in range(M_ITEMS):
                _spindle_correct(W_cortex, vals_c_react[i], cues_c[i])
                n_total_writes += 1
                n_spindle_corrections += 1

        elif arm_name == "ARM_RIPPLE_THEN_SPINDLE":
            # Phase 1: all ripples.
            for i in range(M_ITEMS):
                _ripple_write(W_cortex, vals_c_react[i], cues_c[i])
                n_total_writes += 1
            # Phase 2: spindle pass over same items (use shuffled).
            spindle_perm = rng.permutation(M_ITEMS)
            for i in spindle_perm:
                _spindle_correct(W_cortex, vals_c_react[i], cues_c[i])
                n_spindle_corrections += 1

        elif arm_name == "ARM_SPINDLE_THEN_RIPPLE":
            # Phase 1: all spindles.
            for i in range(M_ITEMS):
                _spindle_correct(W_cortex, vals_c_react[i], cues_c[i])
                n_spindle_corrections += 1
            # Phase 2: ripples (consolidates the now-cleaner state).
            ripple_perm = rng.permutation(M_ITEMS)
            for i in ripple_perm:
                _ripple_write(W_cortex, vals_c_react[i], cues_c[i])
                n_total_writes += 1

        elif arm_name == "ARM_INTERLEAVED":
            # Ripple write item i, then spindle correct a recent random item.
            for i in range(M_ITEMS):
                _ripple_write(W_cortex, vals_c_react[i], cues_c[i])
                n_total_writes += 1
                if i > 0:
                    j = rng.randint(0, i + 1)
                    _spindle_correct(W_cortex, vals_c_react[j], cues_c[j])
                    n_spindle_corrections += 1

        else:
            raise ValueError(f"unknown arm: {arm_name}")

        _heartbeat_write(out_dir, unit_idx=0, total_units=1,
                         elapsed_s=time.time() - t0,
                         extra={"arm": arm_name, "seed": int(seed),
                                "n_writes": n_total_writes,
                                "n_spindle": n_spindle_corrections})

        # Recall.
        preds_raw = keys_c @ W_cortex.T
        preds = np.sign(preds_raw); preds[preds == 0] = 1.0
        preds_n = _l2_normalize_batch(preds)
        sims = preds_n @ vals_c.T
        argmax = np.argmax(sims, axis=1)
        n_hits = int(np.sum(argmax == np.arange(M_ITEMS)))
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(np.linalg.norm(W_cortex))

        arm_hash_val = _arm_hash(arm_name, W_cortex)

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "seed": int(seed),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "n_spindle_corrections": int(n_spindle_corrections),
            "arm_hash": str(arm_hash_val),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "seed": int(seed),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "n_spindle_corrections": 0,
            "arm_hash": "ERROR",
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {str(exc)[:200]}",
        }


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    rng_p = np.random.RandomState(seed + 1000)
    P_in = rng_p.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng_p.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)

    print(f"  [seed={seed}] M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} "
          f"arms={ARM_NAMES} run_mode={RUN_MODE}", flush=True)

    arms = []
    for arm_name in ARM_NAMES:
        out = run_arm(arm_name, seed, keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name:>26s}] "
            f"recall={out['recall_cortex']:.3f} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"n_w={out['n_total_writes']} n_sp={out['n_spindle_corrections']} "
            f"hash={out['arm_hash']} status={out['arm_status'][:30]} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_CORTEX,
        "N_c": N_CORTEX,
        "N_h": N_HIPPO,
        "M": M_ITEMS,
        "n_arms": len(ARM_NAMES),
        "eta_c": ETA_CORTEX,
        "eta_spindle": ETA_SPINDLE,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "backend": "numpy",
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


def _arm_recall_mean(arms_across_seeds, arm_name):
    vals = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                vals.append(float(a["recall_cortex"]))
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hashes(arms_across_seeds, arm_name):
    out = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                out.append(str(a["arm_hash"]))
    return out


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No seed results.")
    if len(results) != len(SEEDS):
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {len(SEEDS)} seeds, got {len(results)}")
    arms_across = []
    for r in results:
        if len(r.get("arms", [])) != len(ARM_NAMES):
            return ("HARD_FAIL",
                    f"CARDINALITY_BREACH: seed={r.get('seed')} has "
                    f"{len(r.get('arms', []))} arms, expected {len(ARM_NAMES)}")
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"seed={r['seed']} arm={a['arm_name']} "
                        f"error: {a['arm_status']}")
        arms_across.append(r["arms"])

    af_violations = []
    for i in range(len(ARM_NAMES)):
        for j in range(i + 1, len(ARM_NAMES)):
            a1, a2 = ARM_NAMES[i], ARM_NAMES[j]
            h1, h2 = _arm_hashes(arms_across, a1), _arm_hashes(arms_across, a2)
            any_diff = any(x != y for x, y in zip(h1, h2))
            if not any_diff and h1 and h2:
                af_violations.append(f"{a1}/{a2}")
    if af_violations:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: identical arm_hash across all seeds "
                f"for: {af_violations}")

    R_RIPPLE = _arm_recall_mean(arms_across, "ARM_RIPPLE_ONLY")
    arm_recalls = {arm: _arm_recall_mean(arms_across, arm) for arm in ARM_NAMES}

    rescue_arms = [a for a in ARM_NAMES if a != "ARM_RIPPLE_ONLY"]
    best_arm = max(rescue_arms, key=lambda a: arm_recalls[a])
    best_recall = arm_recalls[best_arm]
    best_lift = best_recall - R_RIPPLE

    arm_summary = " ".join(f"{a}={arm_recalls[a]:.3f}" for a in ARM_NAMES)
    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} alpha_simple="
        f"{_alpha_simple(M_ITEMS, N_HIPPO):.3f} mode={RUN_MODE} {arm_summary} "
        f"| best_arm={best_arm} best_lift={best_lift:+.3f} R_RIPPLE={R_RIPPLE:.3f}"
    )

    if best_lift >= HARD_PASS_LIFT_MIN:
        return ("HARD_PASS",
                f"HARD_PASS (SPINDLE_RESCUE_CONFIRMED): {best_arm} lifts "
                f"recall by {best_lift:+.3f}. {summary}")
    if best_lift >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial spindle rescue lift {best_lift:+.3f}. "
                f"{summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: spindles do not rescue Hc (best lift "
            f"{best_lift:+.3f}). {summary}")


def _selftest_sparse_dg() -> None:
    rng = np.random.RandomState(7)
    N_raw = 32
    N_h_test = 128
    k_test = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_test)))
    P = rng.randn(N_h_test, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=(4, N_raw)).astype(np.float64)
    h = _sparse_dg(x, P, k_test)
    active = np.sum(np.abs(h) > 0, axis=1)
    if not np.all(active == k_test):
        raise AssertionError(f"k-WTA wrong: got {active}, want {k_test}")


def _selftest_spindle_correct() -> None:
    """Spindle correction must move W toward target; recall after one spindle
    correction on single item should approach 1.0."""
    rng = np.random.RandomState(31)
    N_c = 64
    v = rng.choice([-1.0, 1.0], size=N_c).astype(np.float64)
    c = rng.choice([-1.0, 1.0], size=N_c).astype(np.float64) / np.sqrt(N_c)
    v_n = _l2_normalize_one(v)
    c_n = c
    W = np.zeros((N_c, N_c), dtype=np.float64)
    # Do many spindle corrections; W should converge such that sign(W @ c) ~ v.
    for _ in range(50):
        _spindle_correct(W, v_n, c_n)
    pred = np.sign(W @ c_n)
    pred[pred == 0] = 1.0
    # Should match at least 80% of bits.
    bit_match = float(np.mean(pred == np.sign(v_n)))
    if bit_match < 0.5:
        raise AssertionError(
            f"spindle_correct converges poorly: {bit_match:.2f} bit match")


def _selftest_arm_count() -> None:
    if len(set(ARM_NAMES)) != len(ARM_NAMES):
        raise AssertionError(f"ARM_NAMES has duplicates: {ARM_NAMES}")
    expected = len(ARM_NAMES) * len(SEEDS)
    if expected != EXPECTED_N_UNITS:
        raise AssertionError("EXPECTED_N_UNITS mismatch")


def _selftest_regime_alpha() -> None:
    a_full = _alpha_simple(M_ITEMS_FULL, N_HIPPO_FULL)
    a_smoke = _alpha_simple(M_ITEMS_SMOKE, N_HIPPO_SMOKE)
    if abs(a_full - a_smoke) > 1e-3:
        raise AssertionError(
            f"smoke alpha {a_smoke:.3f} != full alpha {a_full:.3f}")
    if not (0.20 < a_full < 0.30):
        raise AssertionError(f"alpha_simple={a_full:.3f} not in v2 reference")


def _instrumentation_selftest() -> None:
    try:
        _selftest_sparse_dg()
        _selftest_spindle_correct()
        _selftest_arm_count()
        _selftest_regime_alpha()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  M={M_ITEMS}  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f}  "
        f"seeds={SEEDS}  arms={ARM_NAMES}  expected_n_units={EXPECTED_N_UNITS}  "
        f"mode={RUN_MODE}  marker={_HARDENING_MARKER}",
        flush=True,
    )


def _write_crash_metrics(output_dir: Path, anchor_name: str,
                         exc: BaseException) -> None:
    diag = {
        "anchor_name": anchor_name,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
    }
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(final))
    except Exception:
        pass


def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "_start_marker.txt").write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} arms={ARM_NAMES}",
        encoding="utf-8",
    )

    try:
        run_config = {
            "N": N_CORTEX, "M": M_ITEMS, "N_h": N_HIPPO, "run_mode": RUN_MODE,
            "anchor": ANCHOR_NAME,
        }
        done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
        print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
              f"running {remaining}", flush=True)

        t_sweep_start = time.time()
        for seed in remaining:
            print(f"[seed={seed}] {ANCHOR_NAME} run_mode={RUN_MODE}...",
                  flush=True)
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
            verdict_msg = (
                f"HARD_FAIL: stale smoke partials in FULL run. "
                f"mode_in_results={mode_in_results}. " + verdict_msg
            )

        per_arm_rows = []
        for arm_name in ARM_NAMES:
            recalls = []
            for r in all_results:
                for a in r.get("arms", []):
                    if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                        recalls.append(float(a["recall_cortex"]))
            if recalls:
                per_arm_rows.append({
                    "arm_name": arm_name,
                    "recall_mean": float(np.mean(recalls)),
                    "recall_std": float(np.std(recalls)) if len(recalls) > 1 else 0.0,
                    "n_seeds_ok": len(recalls),
                })

        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": (
                f"n_seeds={len(all_results)} M={M_ITEMS} N_h={N_HIPPO} "
                f"N_c={N_CORTEX} arms={ARM_NAMES} mode={RUN_MODE} "
                f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f} "
                f"sleep_spindles_iterative_consolidation"
            ),
            "elapsed_s": float(elapsed_s),
            "config_version": CONFIG_VERSION,
            "M": M_ITEMS,
            "N_c": N_CORTEX,
            "N_h": N_HIPPO,
            "eta_c": ETA_CORTEX,
            "eta_spindle": ETA_SPINDLE,
            "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
            "backend": "numpy",
            "n_seeds": len(SEEDS),
            "expected_n_units": EXPECTED_N_UNITS,
            "cardinality_ok": (
                len(all_results) == len(SEEDS)
                and all(len(r.get("arms", [])) == len(ARM_NAMES) for r in all_results)
            ),
            "run_mode": RUN_MODE,
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "per_arm_rows": per_arm_rows,
            "per_seed": [
                {"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"),
                 "arms": r.get("arms")}
                for r in all_results
            ],
        }
        metrics_path = out_dir / "metrics.json"
        tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp_path), str(metrics_path))
        print(f"[metrics] written to {metrics_path}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        _write_crash_metrics(out_dir, ANCHOR_NAME, exc)
        raise


if __name__ == "__main__":
    _main()
