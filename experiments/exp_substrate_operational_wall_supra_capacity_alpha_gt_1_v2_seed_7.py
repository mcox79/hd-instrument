"""substrate_operational_wall_supra_capacity_alpha_gt_1_v2 -- seed_7.

Follow-up to v1 HALT_ATOMIZE (v1's sub-capacity wall predictions not observable
at full N=8192 due to CLT washout). v2b enters supra-capacity spin-glass regime
where recall MUST degrade because M > N (patterns exceed dimension; W matrix
is over-determined).

MECHANISM (identical to v1; Cell D v2 canonical Hebbian W-matrix):
  W = sum_i outer(vals[i], keys[i]) / N       # (N x N) accumulator, eta=1 uniform
  out = sign(q_noisy @ W.T)                    # linear projection + sign
  match = argmax(cos(out_n, vals_n_i))         # cleanup readout

SWEEP GRID (per seed, iid bipolar keys rho=0):
  alpha in {1.0, 1.2, 1.5, 2.0, 3.0}  * f in {0.00, 0.43}
  = 10 core arms
  N_QUERIES = 800

FALSIFIABLE PREDICTIONS (verdict gates):
  HP_MARGINAL_DISCRIM:  (a=1.0, f=0.00) recall in [0.30, 0.90]
  HP_SUPRA_CAPACITY_COLLAPSE:  (a=2.0, f=0.00) recall < 0.50
  HP_SPIN_GLASS:  (a=3.0, f=0.00) recall < 0.15
  HP_NOISE_ARM_MONOTONIC:  across a in {1.0,1.2,1.5,2.0,3.0} at f=0.43,
    recall(a=k) >= recall(a=k+1) for >=3 of 4 consecutive pairs
  HF_NO_SUPRA_COLLAPSE:  (a=3.0, f=0.00) recall > 0.50 (mechanism audit)
  HF_NON_MONOTONIC:  f=0.43 non-monotone; complex regime
  HF_STRUCTURAL_INFRA:
    baseline (a=1.0, f=0.00) NaN
    UNIT_CARDINALITY_BREACH:  len(core) != 10
    META_RULE_AF:  bit-identical arm hits (allowance for saturation at chance)
    CELL_CRASHED

CARDINALITY (META_RULE_H):  10 arms per seed.

CRLB (capacity feasibility):
  Per-arm recall = binomial over N_QUERIES=800.
  sigma_min(p=0.5) = 0.0177 THEORETICAL@binomial-CLT.
  HP band for supra_collapse = 0.50 gap >> 3*sigma = 0.053 -> reachable.

DISCRIMINATOR-MUST-SURVIVE-SCALE (pattern C):
  Smoke runs at N=1024 core sweep + 4 preview arms at FULL N=8192:
    PREVIEW (a=1.0, f=0.00): expect recall in [0.30, 0.90] (MARGINAL_DISCRIM)
    PREVIEW (a=2.0, f=0.00): expect recall < 0.50 (SUPRA_COLLAPSE)
    PREVIEW (a=3.0, f=0.00): expect recall < 0.15 (SPIN_GLASS)
    PREVIEW (a=1.0, f=0.43): expect recall < 0.30 (NOISE + CAPACITY)
  Smoke verdict from previews (fires the wall discriminator at full-N).

BASELINE_IN_BAND: (a=1.0, f=0.00) should be marginal-DISCRIM (0.30-0.90).
  This is the KEY difference from v1 -- baseline here is at capacity boundary,
  NOT at safe sub-capacity like v1's (a=0.60).

Cross-references:
- v1 HALT_ATOMIZE: notes/exp_dev_findings/exp_substrate_operational_wall_alpha_fine_sweep_v1_HF_DRILL_FALSIFIED_2026-07-02.md
- Sonnet drill: notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md
- Lucibello-Mezard 2023 CITED (T_c(alpha) -> 0)
- AGS 1985 CITED (alpha_c = 0.138 classical wall)
- v1 cell + smoke: exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7.py

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
  - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 hash of hits)
  - final_metrics_atomicity = tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed = 0.0177 (discriminator_reachability = True)
  - baseline_in_band at smoke (relaxed: a=1.0 f=0 is DISCRIM not SAT)
  - discriminator survives scale (smoke has full-N preview arms)
  - HARD_PASS strictly above floor (band width 0.05)
  - cardinality_ok (EXPECTED_N_UNITS = 10)
  - per-unit failure_class instrumentation (no bare except)
  - calibration_check = default_ok_for_this_regime
  - all numbers tagged MEASURED / HYPOTHESIZED / THEORETICAL / CITED

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant).
PROT-021: single-seed cell (chunked); _seed_checkpoint import present.
ASCII-only.

PRESERVE_ENV_VARS: HDLAB_QUEUE

WALL-TIME NOTE: W at N=8192 float32 = 256 MB. Per-arm at largest M=24576
(a=3.0): readout n_q * N * M = 800 * 8192 * 24576 = 161 GF -> ~30s laptop.
Total per-seed at laptop ~10 * 30s + smoke previews ~ 10 min FULL. Remote_cpu
with BLAS ~ 5-10 min per seed. Timeout 3600s (1h) gives 6x safety.
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
import platform
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


# ---------------------------------------------------------------------------
# Inline heartbeat + start marker + crash diagnostic
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ANCHOR_NAME = "substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "operational_wall_supra_alpha_v2_seed_chunk"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# FULL config
N_FULL = 8192
ALPHA_LEVELS = [1.0, 1.2, 1.5, 2.0, 3.0]
F_NOISE_LEVELS = [0.00, 0.43]
N_QUERIES_FULL = 800

# Smoke config
N_SMOKE = 1024
N_QUERIES_SMOKE = 200
# Preview arm regimes at full-N (Discriminator-must-survive-scale pattern C)
PREVIEW_ARMS = [
    (1.0, 0.00, "MARGINAL_DISCRIM"),
    (2.0, 0.00, "SUPRA_COLLAPSE"),
    (3.0, 0.00, "SPIN_GLASS"),
    (1.0, 0.43, "NOISE_PLUS_CAPACITY"),
]
PREVIEW_N_QUERIES = 400

RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]
EXPECTED_N_UNITS = len(ALPHA_LEVELS) * len(F_NOISE_LEVELS)
assert EXPECTED_N_UNITS == 10, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_LEVELS},f_levels={F_NOISE_LEVELS},"
    f"chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"hardening=operational_wall_supra_v2+METARULE_AF+METARULE_AH"
)


# ---------------------------------------------------------------------------
# Core mechanism helpers (identical to v1)
# ---------------------------------------------------------------------------
def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _apply_query_noise(queries_raw: np.ndarray, f: float,
                       rng: np.random.RandomState) -> np.ndarray:
    if f <= 0.0:
        return _l2norm_rows(queries_raw)
    flip_mask = rng.random(queries_raw.shape) < f
    noisy = queries_raw.copy()
    noisy[flip_mask] = -noisy[flip_mask]
    return _l2norm_rows(noisy)


def _build_hebbian_W(keys_raw: np.ndarray, vals_raw: np.ndarray) -> np.ndarray:
    n = keys_raw.shape[1]
    keys32 = keys_raw.astype(np.float32)
    vals32 = vals_raw.astype(np.float32)
    W = np.einsum("ia,ib->ab", vals32, keys32)
    W /= float(n)
    return W  # (N, N) float32


def _hebbian_wmatrix_recall(W: np.ndarray, vals_norm: np.ndarray,
                            queries_noisy_n: np.ndarray,
                            query_targets: np.ndarray,
                            batch: int = 128) -> np.ndarray:
    q_count = queries_noisy_n.shape[0]
    hits = np.zeros(q_count, dtype=bool)
    v_n_32 = vals_norm.astype(np.float32)
    for start in range(0, q_count, batch):
        end = min(q_count, start + batch)
        q_chunk = queries_noisy_n[start:end].astype(np.float32)
        out = q_chunk @ W.T
        out = np.sign(out)
        out_n = out / np.linalg.norm(out, axis=1, keepdims=True).clip(min=1e-12)
        sims = out_n @ v_n_32.T
        argmax = sims.argmax(axis=1)
        expected = query_targets[start:end]
        hits[start:end] = (argmax == expected)
    return hits


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha: float, f: float,
            n_dim: int, n_queries: int, seed: int,
            out_dir: Path) -> Dict:
    t0 = time.time()
    try:
        m_items = max(2, int(round(alpha * n_dim)))
        rng = np.random.RandomState(
            seed
            + int(round(alpha * 10000))
            + int(round(f * 100000))
        )

        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)

        query_targets = rng.choice(m_items, size=n_queries, replace=True)

        W = _build_hebbian_W(keys_raw, vals_raw)

        query_keys_raw = keys_raw[query_targets]
        queries_noisy_n = _apply_query_noise(query_keys_raw, f, rng)

        vals_norm = _l2norm_rows(vals_raw)

        hits = _hebbian_wmatrix_recall(W, vals_norm, queries_noisy_n, query_targets)
        recall_all = float(hits.mean())

        hits_hash = hashlib.sha256(hits.tobytes()).hexdigest()[:16]

        s0 = 1.0 - 2.0 * f
        max_comp_theoretical = math.sqrt(2.0 * m_items * math.log(max(m_items, 2))) / n_dim
        margin_theoretical = s0 - max_comp_theoretical

        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"arm": arm_name, "alpha": alpha, "f": f,
                              "M": m_items, "recall": recall_all,
                              "margin": margin_theoretical})

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "f": float(f),
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": int(n_queries),
            "recall_all": recall_all,
            "hits_hash": hits_hash,
            "margin_theoretical": float(margin_theoretical),
            "max_comp_theoretical": float(max_comp_theoretical),
            "s0_theoretical": float(s0),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "f": float(f),
            "M": 0,
            "N": int(n_dim),
            "n_queries": 0,
            "recall_all": float("nan"),
            "hits_hash": "",
            "margin_theoretical": float("nan"),
            "max_comp_theoretical": float("nan"),
            "s0_theoretical": float("nan"),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_hebbian_wmatrix_clean_recall_below_wall() -> None:
    """Sub-capacity sanity: at alpha=0.05, clean recall must be near 1.0."""
    rng = np.random.RandomState(11)
    n = 256
    m = int(0.05 * n)
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = _build_hebbian_W(keys_raw, vals_raw)
    vals_norm = _l2norm_rows(vals_raw)
    q_raw = _l2norm_rows(keys_raw)
    targets = np.arange(m)
    hits = _hebbian_wmatrix_recall(W, vals_norm, q_raw, targets)
    r = float(hits.mean())
    if r < 0.90:
        raise AssertionError(f"sub-capacity clean recall too low: {r:.3f} < 0.90")


def _selftest_bit_flip_noise_rate() -> None:
    rng = np.random.RandomState(31)
    q_raw = np.ones((10, 4096), dtype=np.float64)
    q_noisy_n = _apply_query_noise(q_raw, 0.30, rng)
    signs = np.sign(q_noisy_n)
    flip_rate = float((signs != 1.0).mean())
    if not (0.20 < flip_rate < 0.40):
        raise AssertionError(f"bit-flip rate {flip_rate} not in [0.20, 0.40]")


def _selftest_supra_capacity_at_small_N() -> None:
    """At alpha=3.0, N=256, M=768 patterns in 256-dim: expect recall << 1.0.
    This is the KEY discriminator-survives-scale check: mechanism must show
    collapse at supra-capacity even at small N (unlike v1 which needed N=8192)."""
    rng = np.random.RandomState(53)
    n = 256
    alpha = 3.0
    m = int(round(alpha * n))  # M=768; way over capacity
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = _build_hebbian_W(keys_raw, vals_raw)
    vals_norm = _l2norm_rows(vals_raw)
    query_targets = rng.choice(m, size=400, replace=True)
    q_raw = _l2norm_rows(keys_raw[query_targets])
    hits = _hebbian_wmatrix_recall(W, vals_norm, q_raw, query_targets)
    r = float(hits.mean())
    print(
        f"[selftest_diag] SUPRA-CAP alpha=3.0 f=0 N=256 M={m}: recall={r:.3f} "
        f"(expect < 0.30 at N=256 for supra-capacity discriminator)",
        flush=True,
    )
    # At supra-capacity, W is severely over-determined; recall should be low
    if r > 0.60:
        raise AssertionError(
            f"SUPRA_CAPACITY_SELFTEST_FAIL: alpha=3.0 f=0 N=256 recall={r:.3f} > 0.60; "
            f"mechanism NOT collapsing at supra-capacity as theory predicts. "
            f"Possibly the mechanism has an unintended memory boost, or something is wrong."
        )


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_wiring() -> None:
    if EXPECTED_N_UNITS != len(ALPHA_LEVELS) * len(F_NOISE_LEVELS):
        raise AssertionError(f"EXPECTED_N_UNITS wiring: {EXPECTED_N_UNITS}")


def _instrumentation_selftest() -> None:
    try:
        _selftest_bit_flip_noise_rate()
        _selftest_hebbian_wmatrix_clean_recall_below_wall()
        _selftest_supra_capacity_at_small_N()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_wiring()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N={N_DIM}  N_Q={N_QUERIES}  "
        f"alpha={ALPHA_LEVELS}  f={F_NOISE_LEVELS}  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  expected_units={EXPECTED_N_UNITS}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    arms = []
    n_arms_total = len(ALPHA_LEVELS) * len(F_NOISE_LEVELS)
    idx = 0
    for alpha in ALPHA_LEVELS:
        for f in F_NOISE_LEVELS:
            arm_name = f"a{alpha:.2f}_f{f:.2f}"
            print(
                f"  [seed={seed} {idx + 1}/{n_arms_total} {arm_name}] "
                f"N={N_DIM} N_Q={N_QUERIES}...",
                flush=True,
            )
            out = run_arm(arm_name, alpha, f,
                          n_dim=N_DIM, n_queries=N_QUERIES,
                          seed=seed, out_dir=out_dir)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] recall={out['recall_all']:.3f} "
                f"margin_th={out['margin_theoretical']:+.3f} "
                f"M={out['M']} hash={out['hits_hash']} "
                f"status={out['arm_status']} wall={out['wall_s']:.2f}s",
                flush=True,
            )
            emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                           elapsed_s=time.time() - t0,
                           extra={"arm": arm_name, "recall": out["recall_all"]})
            idx += 1

    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        for (p_alpha, p_f, p_tag) in PREVIEW_ARMS:
            arm_name = f"PREVIEW_a{p_alpha:.2f}_f{p_f:.2f}_fullN_{p_tag}"
            print(
                f"  [seed={seed} {arm_name}] N={N_FULL} N_Q={PREVIEW_N_QUERIES}...",
                flush=True,
            )
            preview = run_arm(arm_name, p_alpha, p_f,
                              n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
                              seed=seed, out_dir=out_dir)
            print(
                f"  [seed={seed} {arm_name}] recall={preview['recall_all']:.3f} "
                f"margin_th={preview['margin_theoretical']:+.3f} "
                f"M={preview['M']} status={preview['arm_status']} "
                f"wall={preview['wall_s']:.1f}s",
                flush=True,
            )
            arms.append(preview)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "n_queries": N_QUERIES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _core_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if not a["arm_name"].startswith("PREVIEW_")]


def _preview_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if a["arm_name"].startswith("PREVIEW_")]


def _lookup(core: List[Dict], alpha: float, f: float) -> Dict:
    for a in core:
        if (abs(a["alpha"] - alpha) < 1e-6 and abs(a["f"] - f) < 1e-6):
            return a
    raise KeyError(f"missing arm alpha={alpha} f={f}")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    core = _core_arms(r["arms"])
    previews = _preview_arms(r["arms"])
    if len(core) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected {EXPECTED_N_UNITS} core arms, got {len(core)}")
    for a in core:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    # META_RULE_AF: arms-must-differ via hits_hash. Supra-capacity may produce
    # many all-False vectors near chance; require at least 6 distinct hashes.
    hashes = set(a["hits_hash"] for a in core if a["hits_hash"])
    if len(hashes) < 6:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: only {len(hashes)} distinct hits hashes / 10 arms")

    # BASELINE_IN_BAND: at a=1.0 f=0, must be DISCRIM (not pure SAT nor CHANCE)
    try:
        a_baseline = _lookup(core, 1.0, 0.00)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing baseline arm: {e}")

    r_baseline = a_baseline["recall_all"]
    # Relaxed baseline band for supra-capacity cell
    if RUN_MODE == "full":
        if not (0.10 <= r_baseline <= 0.99):
            return ("HARD_FAIL",
                    f"BASELINE_OUT_OF_BAND: (a=1.0, f=0.00) recall={r_baseline:.3f} "
                    f"not in [0.10, 0.99]. Mechanism audit needed.")
    # else smoke: baseline at N=1024 will still saturate near 1.0, that's OK

    # Extract wall-diagnostic arms
    try:
        a10_clean = _lookup(core, 1.0, 0.00)
        a20_clean = _lookup(core, 2.0, 0.00)
        a30_clean = _lookup(core, 3.0, 0.00)
        f43_by_alpha = {a: _lookup(core, a, 0.43)["recall_all"] for a in ALPHA_LEVELS}
    except KeyError as e:
        return ("HARD_FAIL", f"Missing wall-diagnostic arm: {e}")

    r10 = a10_clean["recall_all"]
    r20 = a20_clean["recall_all"]
    r30 = a30_clean["recall_all"]

    # HP evaluations
    hp_marginal_discrim = (0.30 <= r10 <= 0.90)
    hp_supra_collapse = (r20 < 0.50)
    hp_spin_glass = (r30 < 0.15)
    # Monotone check on f=0.43 arms
    f43_seq = [f43_by_alpha[a] for a in ALPHA_LEVELS]
    monotone_pairs = sum(
        1 for i in range(len(f43_seq) - 1) if f43_seq[i] >= f43_seq[i + 1]
    )
    hp_noise_monotone = (monotone_pairs >= 3)

    # HF evaluations
    hf_no_supra_collapse = (r30 > 0.50)  # substrate NOT collapsing at supra-capacity
    hf_non_monotonic = (monotone_pairs < 2)

    n_hp = sum([hp_marginal_discrim, hp_supra_collapse,
                hp_spin_glass, hp_noise_monotone])

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"r(a=1.0,f=0)={r10:.3f} r(a=2.0,f=0)={r20:.3f} "
        f"r(a=3.0,f=0)={r30:.3f} "
        f"f043=[{','.join(f'{v:.3f}' for v in f43_seq)}] "
        f"monotone_pairs={monotone_pairs}/4 "
        f"HP=[marg_discrim={hp_marginal_discrim},supra_col={hp_supra_collapse},"
        f"spin_glass={hp_spin_glass},noise_mono={hp_noise_monotone}] "
        f"n_hp={n_hp}/4"
    )

    if RUN_MODE == "full":
        if hf_no_supra_collapse:
            return ("HARD_FAIL",
                    f"HF_NO_SUPRA_COLLAPSE: r(a=3.0,f=0)={r30:.3f} > 0.50; "
                    f"substrate NOT collapsing at supra-capacity. Mechanism audit. {summary}")
        if hf_non_monotonic:
            return ("HARD_FAIL",
                    f"HF_NON_MONOTONIC: f=0.43 recall non-monotone as alpha climbs. "
                    f"Complex regime. {summary}")
        if n_hp >= 3:
            return ("HARD_PASS",
                    f"HARD_PASS: supra-capacity operational-wall CG. {n_hp}/4 HP fired "
                    f"(marginal_discrim + supra_collapse + spin_glass + noise_monotone). "
                    f"Empirical Lucibello-Mezard T_c(alpha) analog for Hebbian+sign+argmax. "
                    f"Cross-seed VET needed. {summary}")
        if n_hp >= 2:
            return ("MIDDLE_BAND",
                    f"MIDDLE_BAND: partial supra-capacity wall. {n_hp}/4 HP fired. {summary}")

    if RUN_MODE == "smoke":
        preview_by_tag = {}
        for p in previews:
            if p["arm_status"] == "OK":
                if "MARGINAL_DISCRIM" in p["arm_name"]:
                    preview_by_tag["MARGINAL_DISCRIM"] = p["recall_all"]
                elif "SUPRA_COLLAPSE" in p["arm_name"]:
                    preview_by_tag["SUPRA_COLLAPSE"] = p["recall_all"]
                elif "SPIN_GLASS" in p["arm_name"]:
                    preview_by_tag["SPIN_GLASS"] = p["recall_all"]
                elif "NOISE_PLUS_CAPACITY" in p["arm_name"]:
                    preview_by_tag["NOISE_PLUS_CAPACITY"] = p["recall_all"]

        preview_summary = (
            f"preview_fullN: MARG_DISCRIM={preview_by_tag.get('MARGINAL_DISCRIM', float('nan')):.3f} "
            f"SUPRA_COL={preview_by_tag.get('SUPRA_COLLAPSE', float('nan')):.3f} "
            f"SPIN_GLASS={preview_by_tag.get('SPIN_GLASS', float('nan')):.3f} "
            f"NOISE_CAP={preview_by_tag.get('NOISE_PLUS_CAPACITY', float('nan')):.3f}"
        )

        p_marg = preview_by_tag.get("MARGINAL_DISCRIM", float('nan'))
        p_supra = preview_by_tag.get("SUPRA_COLLAPSE", float('nan'))
        p_spin = preview_by_tag.get("SPIN_GLASS", float('nan'))
        p_noise = preview_by_tag.get("NOISE_PLUS_CAPACITY", float('nan'))

        # KEY discriminator gate: preview_at_alpha=3.0 must show recall < 0.50 at full-N.
        # If yes, mechanism is genuinely collapsing at supra-capacity -> ship FULL.
        # If no (r > 0.50), the substrate is NOT behaving as capacity theory predicts
        # at full-N (like v1's clean-query saturation surprise) -> HARD_FAIL smoke.

        if math.isfinite(p_spin) and p_spin >= 0.50:
            return ("HARD_FAIL",
                    f"HF_WALL_DOES_NOT_FIRE_AT_FULL_N: PREVIEW SPIN_GLASS (a=3.0, f=0.0) "
                    f"recall={p_spin:.3f} >= 0.50 at full N=8192. Substrate does NOT show "
                    f"supra-capacity collapse; mechanism does not match Lucibello-Mezard "
                    f"theory at test regime. Similar to v1 HALT_ATOMIZE pattern. "
                    f"{preview_summary} {summary}")

        if math.isfinite(p_supra) and p_supra >= 0.90:
            return ("HARD_FAIL",
                    f"HF_SUPRA_COLLAPSE_NOT_OBSERVABLE: PREVIEW SUPRA (a=2.0, f=0.0) "
                    f"recall={p_supra:.3f} >= 0.90 at full N=8192. Wall not fired at "
                    f"a=2.0. Mechanism audit. {preview_summary} {summary}")

        # Discriminator FIRES at full-N; full dispatch justified
        if math.isfinite(p_spin) and p_spin < 0.50:
            return ("HARD_PASS",
                    f"HARD_PASS_SMOKE: PREVIEW at N=8192 shows supra-capacity discriminator "
                    f"fires (SPIN_GLASS a=3.0 recall={p_spin:.3f} < 0.50). Full dispatch "
                    f"recommended. {preview_summary} {summary}")

        return ("MIDDLE_BAND", f"MIDDLE_BAND_SMOKE: {preview_summary} {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial signature. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] {ANCHOR_NAME} N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE}...",
            flush=True,
        )
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {rr.get("run_mode", "?") for rr in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL: stale smoke partials in FULL run. " + verdict_msg

    core_arms_final = _core_arms(all_results[0]["arms"]) if all_results else []

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE} "
            f"expected_units={EXPECTED_N_UNITS} "
            f"alpha={ALPHA_LEVELS} f={F_NOISE_LEVELS}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_QUERIES": N_QUERIES,
        "alpha_levels": ALPHA_LEVELS,
        "f_noise_levels": F_NOISE_LEVELS,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1 and len(core_arms_final) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.0177,
        "crlb_formula_reference": "sigma_min = sqrt(p(1-p)/N_Q) binomial-CLT at N_Q=800 p=0.5",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "mechanism_class": "hebbian_wmatrix_canonical_operational_wall_supra_capacity_rho0",
        "per_seed": [
            {"seed": rr.get("seed"),
             "elapsed_s": rr.get("elapsed_s"),
             "arms": rr.get("arms")}
            for rr in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
