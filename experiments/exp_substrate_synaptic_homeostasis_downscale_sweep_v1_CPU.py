"""substrate_synaptic_homeostasis_downscale_sweep_v1_CPU.

Stage 2 NREM rescue cell E. Tests SYNAPTIC HOMEOSTASIS (Tononi+Cirelli SHY
hypothesis) global down-scaling as rescue for Hc CORTEX_WRITE_SATURATION.

CITED@Tononi_Cirelli_2003_synaptic_homeostasis_hypothesis: during sleep, ALL
cortical synapses get globally down-scaled (~5-30% in animal studies);
prevents weight saturation while preserving relative weight structure.
Mechanism: a global proportional rescale W -> alpha * W (alpha < 1) reduces
saturation without erasing the learned associations.

LINEAGE:
  Hippo bottleneck v2 MEASURED@d:/AI/hd-instrument/data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json:
    R_STANDARD=0.219; Hc cortex write saturation confirmed (CLEAN=0.985 closes gap).
  This cell tests: does interleaving down-scaling between replays let STANDARD
  noisy reconstructions still consolidate without saturating W_c?

HYPOTHESIS:
  THEORETICAL@write_saturation_with_homeostasis: cumulative writes
  W_c = sum_t eta * v_t @ c_t.T saturate at norm O(M*eta); down-scaling
  W_c <- gamma * W_c per round limits cumulative norm to eta / (1 - gamma).
  Per-round noisy writes still accumulate signal proportionally to alignment
  with previous writes; uncorrelated noise cancels.

ARMS (5):
  ARM_NO_HOMEO            -- baseline: STANDARD pipeline, no down-scaling
  ARM_HOMEO_GAMMA_0_9     -- W_c <- 0.9 * W_c every 100 items
  ARM_HOMEO_GAMMA_0_7     -- W_c <- 0.7 * W_c every 100 items
  ARM_HOMEO_GAMMA_0_5     -- W_c <- 0.5 * W_c every 100 items
  ARM_ADAPTIVE_HOMEO      -- per-row down-scale: rescale only rows whose norm
                              exceeds threshold (preserves under-utilized
                              capacity)

PRE-REG BANDS:
  HARD_PASS: best HOMEO arm recall >= R_NO_HOMEO + 0.20
  MIDDLE_BAND: best HOMEO recall in (R_NO_HOMEO+0.05, R_NO_HOMEO+0.20]
  HARD_FAIL: no HOMEO >= R_NO_HOMEO + 0.05

REGIME (matches v2):
  FULL:  M=2048, N_h=8192, N_c=2048; alpha_simple=0.25; seeds=[7,17,23]
  SMOKE: M=512, N_h=2048, N_c=512; same alpha

DISCRIMINATOR-MUST-SURVIVE-SCALE: same alpha at smoke + full.

ROUTING: CPU (scalar W_c rescaling not GPU-amenable; matmul cost dominated
by M-dim sum, ~equivalent on CPU vs GPU at this scale).

ATOMICITY: tmp+os.replace at final metrics write.

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


ANCHOR_NAME = "substrate_synaptic_homeostasis_downscale_sweep_v1_CPU"
_HARDENING_MARKER = "v1_HOMEO_NONE_0_9_0_7_0_5_ADAPTIVE"

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


# Config (matches v2).
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
N_REPLAY_PER_ITEM = 1

# Arm config: (arm_name, kind, gamma)
# kind in {"none", "global", "adaptive"}; gamma is the down-scale factor for
# global rescale or threshold-trigger fraction for adaptive.
ARM_CONFIGS: Tuple[Tuple[str, str, float], ...] = (
    ("ARM_NO_HOMEO", "none", 1.0),
    ("ARM_HOMEO_GAMMA_0_9", "global", 0.9),
    ("ARM_HOMEO_GAMMA_0_7", "global", 0.7),
    ("ARM_HOMEO_GAMMA_0_5", "global", 0.5),
    ("ARM_ADAPTIVE_HOMEO", "adaptive", 0.7),
)
ARM_NAMES: Tuple[str, ...] = tuple(c[0] for c in ARM_CONFIGS)

# Down-scale CADENCE: every HOMEO_INTERVAL items, apply rescale.
HOMEO_INTERVAL = max(1, M_ITEMS // 8)  # 8 rescale rounds per full sweep

EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

HARD_PASS_LIFT_MIN = 0.20
MIDDLE_BAND_LIFT_MIN = 0.05


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"alpha_simple={_alpha_simple(M_ITEMS, N_HIPPO):.3f},"
    f"ARM_NAMES={ARM_NAMES},HOMEO_INTERVAL={HOMEO_INTERVAL},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},backend=numpy,"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+HOMEOSTASIS_SWEEP"
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


def _apply_homeostasis(W: np.ndarray, kind: str, gamma: float) -> None:
    """In-place rescale of W per the arm config."""
    if kind == "none":
        return
    if kind == "global":
        W *= gamma
        return
    if kind == "adaptive":
        # Per-row: rescale rows whose norm exceeds 1.5x median norm.
        row_norms = np.linalg.norm(W, axis=1)
        median = np.median(row_norms)
        if median > 0:
            threshold = 1.5 * median
            saturated = row_norms > threshold
            if saturated.any():
                # Scale saturated rows by gamma (= 0.7 by default in this arm).
                W[saturated] *= gamma
        return
    raise ValueError(f"unknown homeostasis kind: {kind}")


def run_arm(arm_name: str, kind: str, gamma: float, seed: int,
            keys_raw: np.ndarray, vals_raw: np.ndarray,
            P_in: np.ndarray, P_hc: np.ndarray,
            out_dir: Path) -> Dict:
    """STANDARD pipeline with interleaved homeostasis on W_cortex."""
    t0 = time.time()
    try:
        k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
        keys_h = _sparse_dg(keys_raw, P_in, k_active)
        vals_h = _sparse_dg(vals_raw, P_in, k_active)

        keys_c = _l2_normalize_batch(keys_h @ P_hc.T)
        vals_c = _l2_normalize_batch(vals_h @ P_hc.T)

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

        # Replay with interleaved homeostasis.
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        n_homeo_applications = 0
        n_total_writes = 0
        for i in range(M_ITEMS):
            W_cortex += ETA_CORTEX * np.outer(vals_c_react[i], cues_c[i])
            n_total_writes += 1
            if (i + 1) % HOMEO_INTERVAL == 0 and kind != "none":
                _apply_homeostasis(W_cortex, kind, gamma)
                n_homeo_applications += 1

        _heartbeat_write(out_dir, unit_idx=0, total_units=1,
                         elapsed_s=time.time() - t0,
                         extra={"arm": arm_name, "kind": kind, "gamma": gamma,
                                "n_homeo": n_homeo_applications,
                                "seed": int(seed)})

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
            "kind": kind,
            "gamma": float(gamma),
            "seed": int(seed),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "n_homeo_applications": int(n_homeo_applications),
            "arm_hash": str(arm_hash_val),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "kind": kind,
            "gamma": float(gamma),
            "seed": int(seed),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "n_homeo_applications": 0,
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
          f"arms={ARM_NAMES} interval={HOMEO_INTERVAL} run_mode={RUN_MODE}",
          flush=True)

    arms = []
    for arm_name, kind, gamma in ARM_CONFIGS:
        out = run_arm(arm_name, kind, gamma, seed,
                      keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name:>22s} kind={kind:>8s} gamma={gamma:.2f}] "
            f"recall={out['recall_cortex']:.3f} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"n_homeo={out['n_homeo_applications']} "
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
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "homeo_interval": HOMEO_INTERVAL,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": "numpy",
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arm_configs": [{"name": n, "kind": k, "gamma": g}
                        for n, k, g in ARM_CONFIGS],
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


def _arm_recall_mean(arms_across_seeds: List[List[Dict]], arm_name: str) -> float:
    vals = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                vals.append(float(a["recall_cortex"]))
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hashes(arms_across_seeds: List[List[Dict]], arm_name: str) -> List[str]:
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

    af_violations: List[str] = []
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

    R_NO_HOMEO = _arm_recall_mean(arms_across, "ARM_NO_HOMEO")
    arm_recalls = {arm: _arm_recall_mean(arms_across, arm) for arm in ARM_NAMES}

    homeo_arms = [a for a in ARM_NAMES if a != "ARM_NO_HOMEO"]
    best_arm = max(homeo_arms, key=lambda a: arm_recalls[a])
    best_recall = arm_recalls[best_arm]
    best_lift = best_recall - R_NO_HOMEO

    arm_summary = " ".join(
        f"{arm}={arm_recalls[arm]:.3f}" for arm in ARM_NAMES
    )
    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} alpha_simple="
        f"{_alpha_simple(M_ITEMS, N_HIPPO):.3f} mode={RUN_MODE} "
        f"{arm_summary} | best_arm={best_arm} best_lift={best_lift:+.3f} "
        f"R_NO_HOMEO={R_NO_HOMEO:.3f}"
    )

    if best_lift >= HARD_PASS_LIFT_MIN:
        return ("HARD_PASS",
                f"HARD_PASS (HOMEOSTASIS_RESCUE_CONFIRMED): {best_arm} "
                f"lifts recall by {best_lift:+.3f} (>= {HARD_PASS_LIFT_MIN}). "
                f"{summary}")
    if best_lift >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial homeo rescue lift {best_lift:+.3f} below "
                f"HARD_PASS threshold {HARD_PASS_LIFT_MIN}. {summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: homeostasis does not rescue Hc (best lift "
            f"{best_lift:+.3f} < {MIDDLE_BAND_LIFT_MIN}). {summary}")


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
        raise AssertionError(
            f"k-WTA sparsity wrong: got {active}, want {k_test}")


def _selftest_homeo_kinds() -> None:
    kinds = set(c[1] for c in ARM_CONFIGS)
    if kinds != {"none", "global", "adaptive"}:
        raise AssertionError(f"unexpected kinds: {kinds}")
    # Test homeostasis ops in isolation.
    W = np.ones((4, 4), dtype=np.float64)
    _apply_homeostasis(W, "none", 1.0)
    if not np.allclose(W, 1.0):
        raise AssertionError("'none' kind modified W")
    W = np.ones((4, 4), dtype=np.float64)
    _apply_homeostasis(W, "global", 0.5)
    if not np.allclose(W, 0.5):
        raise AssertionError("global 0.5 incorrect")


def _selftest_arm_count() -> None:
    if len(set(ARM_NAMES)) != len(ARM_NAMES):
        raise AssertionError(f"ARM_NAMES has duplicates: {ARM_NAMES}")
    expected = len(ARM_NAMES) * len(SEEDS)
    if expected != EXPECTED_N_UNITS:
        raise AssertionError(f"EXPECTED_N_UNITS mismatch")


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
        _selftest_homeo_kinds()
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
        f"interval={HOMEO_INTERVAL}  seeds={SEEDS}  arms={ARM_NAMES}  "
        f"expected_n_units={EXPECTED_N_UNITS}  mode={RUN_MODE}  "
        f"marker={_HARDENING_MARKER}",
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

        per_arm_rows: List[Dict] = []
        for arm_name in ARM_NAMES:
            recalls = []
            kind_b = None
            gamma_b = None
            for r in all_results:
                for a in r.get("arms", []):
                    if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                        recalls.append(float(a["recall_cortex"]))
                        kind_b = a.get("kind")
                        gamma_b = a.get("gamma")
            if recalls:
                per_arm_rows.append({
                    "arm_name": arm_name,
                    "kind": kind_b,
                    "gamma": gamma_b,
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
                f"synaptic_homeostasis_downscale_sweep"
            ),
            "elapsed_s": float(elapsed_s),
            "config_version": CONFIG_VERSION,
            "M": M_ITEMS,
            "N_c": N_CORTEX,
            "N_h": N_HIPPO,
            "eta_c": ETA_CORTEX,
            "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
            "homeo_interval": HOMEO_INTERVAL,
            "n_replay_per_item": N_REPLAY_PER_ITEM,
            "backend": "numpy",
            "n_seeds": len(SEEDS),
            "expected_n_units": EXPECTED_N_UNITS,
            "cardinality_ok": (
                len(all_results) == len(SEEDS)
                and all(len(r.get("arms", [])) == len(ARM_NAMES) for r in all_results)
            ),
            "run_mode": RUN_MODE,
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "arm_configs": [{"name": n, "kind": k, "gamma": g}
                            for n, k, g in ARM_CONFIGS],
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
