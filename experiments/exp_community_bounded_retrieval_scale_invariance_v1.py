"""community_bounded_retrieval_scale_invariance_v1 -- BARRIER #3 fix (store
crowding at massive scale) via HIPPOCAMPAL INDEXING + community-bounded two-stage
retrieval.

Design source (brain-first drill, self-authored, no sub-agents):
  notes/research_reasoning_over_large_store_without_collapse_brain_first_2026-07-08.md
  ("Substrate-product implications" -> cheap decisive test, thread 4).

MECHANISM UNDER TEST
  The additive-store crosstalk wall M < N/(2 ln V) makes a flat/dense store
  collapse as total store size V grows. Brain thread-4 answer: route a query to
  its COMMUNITY first (coarse gist codebook, ~sqrt(V) near-orthogonal pointers),
  then resolve ONLY within that community (fine decode over ~sqrt(V) items). This
  converts the crosstalk-relevant codebook size from total-V (order/additive,
  grows without bound) to active-community size (bounded ~sqrt(V)). Store codes
  are near-orthogonal random (decoupled from routing semantics per the CERTIFIED
  correlation-hurts-store law); the community structure lives in a SEPARATE
  routing-feature space (guarded by a measured Newman modularity Q).

ARMS (2)
  CONTROL (dense-additive, must-collapse): one GLOBAL bound bundle over ALL V
    key-value pairs; retrieval unbinds a key then cleans up the value against the
    WHOLE V-item value codebook. Additive load = V; argmax over V. Reproduces the
    M < N/(2 ln V) collapse -- degrades as total V grows. This arm's job is the
    saturation-vacuous-smoke guard: if it does NOT collapse, the harness is not
    exercising the crosstalk regime and the test is void.
  TREATMENT (index + community, two-stage): per-community bound bundles. Stage 1:
    route the query cue to its community by argmax over the coarse community-gist
    codebook (n_comm ~ sqrt(V) near-orthogonal pointers). Stage 2: unbind + peel/
    SIC cleanup against ONLY the selected community's ~sqrt(V) value codebook.
    Effective codebook = community size, bounded ~sqrt(V). Should stay FLAT.

READOUT: reuses the operational hdlab.cleanup_family.peel_sic_readout (n_items=1
  = confidence-ordered single-item cleanup; composes to n_items>1 for multi-item
  answer sets). Binding = elementwise multiply on bipolar codes (self-inverse).

KILL-TEST (joint condition; the science question)
  End-to-end retrieval fidelity vs total store size V (sweep 580 -> 58000, ~100x):
  TREATMENT fidelity stays FLAT while CONTROL collapses. HARD-PASS requires BOTH
  (treatment flat AND control collapses) AND real community structure (Q>=0.30)
  AND coarse-route not leaking (route_acc>=0.90 at V_max).

CALIBRATION (MEASURED off-disk before authoring; scratchpad calib, N=8192, seeds 7/17):
  CONTROL fid : V=580 0.742  V=2900 0.039  V=29000 0.000  V=58000 0.000  (rd~0.95)
  TREATMENT   : V=580 1.000  V=2900 1.000  V=29000 1.000  V=58000 0.996  (rd~0.004)
  ROUTE acc   : 1.000 across all V (coarse-select does NOT leak with V)
  Newman Q    : 0.951 / 0.981 / 0.717 / 0.511 (all >> 0.30 guard)
  All numbers above are HYPOTHESIZED@this prereg for the FULL run; the smoke run
  of THIS cell re-MEASURES them at V in {580,2900} and gates on the contrast.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF hash-test on arm predictions)
  - final_metrics_atomicity = tmp_replace (write_metrics + os.replace)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb/capacity-feasibility declared (Plate V* ~ N/(2 ln V))
  - baseline_in_band at smoke (CONTROL spans high->collapsed, not saturated)
  - discriminator survives scale (smoke fires at V=2900; FULL analytic + preview)
  - assert_discriminator_fires: CONTROL must collapse at smoke V (vacuous guard)
  - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_V * n_arms
  - per-unit failure-class instrumentation (no bare except)
  - all cell-comment numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
    write_metrics, record_gate, assert_discriminator_fires,
)
from hdlab.cleanup_family import peel_sic_readout  # noqa: E402


ANCHOR_NAME = "community_bounded_retrieval_scale_invariance_v1"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_DIM = 8192                      # MEASURED@calib: CONTROL V*~630, treatment flat
Q_QUERIES = 128                   # queries per (seed,V)
ROUTE_NOISE = 0.6                 # cue = gist + ROUTE_NOISE*noise (SNR ~1.67)
MOD_SUBSAMPLE = 1500             # nodes sampled for Newman-Q kNN graph
MOD_K = 10                        # kNN degree for modularity graph

ARMS = ["CONTROL", "TREATMENT"]

if RUN_MODE == "smoke":
    V_GRID = [580, 2900]
    SEEDS = [7, 17]
else:
    V_GRID = [580, 2900, 29000, 58000]
    SEEDS = [7, 17, 23]

EXPECTED_N_UNITS = len(SEEDS) * len(V_GRID) * len(ARMS)

# --- bands (pre-reg; strict per META_RULE_L) --------------------------------
TREAT_FLAT_RD_MAX = 0.10         # treatment relative degradation must be <= this
CONTROL_COLLAPSE_RD_MIN = 0.30   # control relative degradation must be >= this (discriminator)
TREAT_ABS_MIN = 0.70             # treatment abs fidelity at V_max (holds, not flat-but-broken)
ROUTE_ACC_MIN = 0.90             # coarse-route accuracy at V_max (not leaking)
MODULARITY_MIN = 0.30            # real community structure (generator guard)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},Q={Q_QUERIES},route_noise={ROUTE_NOISE},"
    f"V_GRID={V_GRID},seeds={SEEDS},mode={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers (start marker + crash diagnostic)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir: Path) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS,
        "host": platform.node(),
        "config_version": CONFIG_VERSION,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Substrate primitives
# ---------------------------------------------------------------------------
def _bipolar(rng: np.random.Generator, shape: Tuple[int, ...]) -> np.ndarray:
    """Random +/-1 bipolar codes (near-orthogonal), float32."""
    return rng.integers(0, 2, size=shape, dtype=np.int8).astype(np.float32) * 2.0 - 1.0


def _newman_modularity_knn(feats: np.ndarray, labels: np.ndarray,
                           k: int = 10) -> Tuple[float, int]:
    """Newman modularity Q of the ground-truth partition on a kNN cosine graph.

    feats (n,N); labels (n,). Returns (Q, n_edges). Verifies the generator
    produced REAL community structure (guards against a secretly-uniform graph).
    """
    n = feats.shape[0]
    if n < 4:
        return 0.0, 0
    X = feats / (np.linalg.norm(feats, axis=1, keepdims=True) + 1e-12)
    S = X @ X.T
    np.fill_diagonal(S, -np.inf)
    kk = min(k, n - 1)
    knn = np.argpartition(-S, kk, axis=1)[:, :kk]
    rows = np.repeat(np.arange(n), kk)
    cols = knn.reshape(-1)
    edges = set()
    for a, b in zip(rows.tolist(), cols.tolist()):
        if a == b:
            continue
        edges.add((a, b) if a < b else (b, a))
    L = len(edges)
    if L == 0:
        return 0.0, 0
    deg: Dict[int, int] = {}
    Lc: Dict[Any, int] = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
        if labels[a] == labels[b]:
            Lc[labels[a]] = Lc.get(labels[a], 0) + 1
    dc: Dict[Any, int] = {}
    for i in range(n):
        lab = labels[i]
        dc[lab] = dc.get(lab, 0) + deg.get(i, 0)
    Q = 0.0
    for c, dsum in dc.items():
        Q += (Lc.get(c, 0) / L) - (dsum / (2.0 * L)) ** 2
    return float(Q), int(L)


def run_one_V(N: int, V: int, seed: int) -> Dict[str, Any]:
    """One (seed,V) point: build KB, run CONTROL + TREATMENT, measure fidelity.

    Returns dict with ctrl_fid, treat_fid, route_acc, modularity_Q, comm_size,
    n_comm, decouple_abs_cos, and (for arms-differ) prediction hashes.
    """
    rng = np.random.default_rng(seed * 100003 + V)
    comm_size = int(round(math.sqrt(V)))
    n_comm = int(math.ceil(V / comm_size))
    comm_of = np.repeat(np.arange(n_comm), comm_size)[:V]

    # Store codes: near-orthogonal random bipolar, DECOUPLED (keys/values indep).
    K = _bipolar(rng, (V, N))
    Vv = _bipolar(rng, (V, N))
    # Community gist pointers (routing space; SEPARATE from store codes).
    G = _bipolar(rng, (n_comm, N))

    # Bound pairs (elementwise mul; bipolar self-inverse under mul).
    P = K * Vv                                       # (V,N)

    # Decoupling telemetry: |cos| between store codes and their community gist.
    _s = rng.choice(V, size=min(256, V), replace=False)
    _kk = K[_s] / (np.linalg.norm(K[_s], axis=1, keepdims=True) + 1e-12)
    _gg = G[comm_of[_s]] / (np.linalg.norm(G[comm_of[_s]], axis=1, keepdims=True) + 1e-12)
    decouple_abs_cos = float(np.mean(np.abs(np.sum(_kk * _gg, axis=1))))

    # Query pairs.
    qidx = rng.choice(V, size=min(Q_QUERIES, V), replace=False)
    true_c = comm_of[qidx]

    # ---- CONTROL: global bound bundle; cleanup over ALL V ----
    B_global = P.sum(axis=0)                         # (N,)
    est_c = B_global[None, :] * K[qidx]              # unbind (Q,N)
    ctrl_pred, _ = peel_sic_readout(est_c, Vv, n_items=1)   # (Q,1) argmax over V
    ctrl_pred = np.asarray(ctrl_pred).reshape(-1)
    ctrl_fid = float((ctrl_pred == qidx).mean())

    # ---- TREATMENT: per-community bundles + two-stage routing ----
    Bc = np.zeros((n_comm, N), dtype=np.float32)
    np.add.at(Bc, comm_of, P)                        # (n_comm,N)
    # Stage 1: coarse route (cue = true gist + noise) -> argmax over gist codebook.
    cue = G[true_c].astype(np.float32) + ROUTE_NOISE * _bipolar(rng, (len(qidx), N))
    route_pred = (cue @ G.T).argmax(axis=1)          # (Q,) over n_comm ~ sqrt(V)
    route_acc = float((route_pred == true_c).mean())
    # Stage 2: unbind against predicted-community bundle, fine cleanup within it.
    treat_pred = np.full(len(qidx), -1, dtype=np.int64)
    members_by_comm: Dict[int, np.ndarray] = {}
    for i, qi in enumerate(qidx):
        cpred = int(route_pred[i])
        mem = members_by_comm.get(cpred)
        if mem is None:
            mem = np.where(comm_of == cpred)[0]
            members_by_comm[cpred] = mem
        if mem.size == 0:
            continue
        est2 = Bc[cpred] * K[qi]                      # (N,) unbind
        p_local, _ = peel_sic_readout(est2, Vv[mem], n_items=1)
        treat_pred[i] = int(mem[int(np.asarray(p_local).reshape(-1)[0])])
    treat_fid = float((treat_pred == qidx).mean())

    # ---- Modularity guard (generator produced real community structure) ----
    n_sub = min(MOD_SUBSAMPLE, V)
    sub = rng.choice(V, size=n_sub, replace=False)
    r_feats = G[comm_of[sub]].astype(np.float32) + ROUTE_NOISE * _bipolar(rng, (n_sub, N))
    mod_Q, mod_edges = _newman_modularity_knn(r_feats, comm_of[sub], k=MOD_K)

    # arms-differ hashes (META_RULE_AF): prediction vectors must not be bit-identical.
    import hashlib
    ctrl_h = hashlib.sha256(ctrl_pred.astype(np.int64).tobytes()).hexdigest()
    treat_h = hashlib.sha256(treat_pred.astype(np.int64).tobytes()).hexdigest()

    return {
        "V": int(V), "comm_size": int(comm_size), "n_comm": int(n_comm),
        "ctrl_fid": ctrl_fid, "treat_fid": treat_fid, "route_acc": route_acc,
        "modularity_Q": mod_Q, "modularity_edges": mod_edges,
        "decouple_abs_cos": decouple_abs_cos,
        "ctrl_pred_hash": ctrl_h, "treat_pred_hash": treat_h,
    }


def run_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_V: Dict[str, Any] = {}
    for V in V_GRID:
        tv = time.time()
        rec = run_one_V(N_DIM, V, seed)
        per_V[str(V)] = rec
        print(f"[seed={seed} V={V}] ctrl={rec['ctrl_fid']:.3f} "
              f"treat={rec['treat_fid']:.3f} route={rec['route_acc']:.3f} "
              f"Q={rec['modularity_Q']:.3f} comm_size={rec['comm_size']} "
              f"({time.time()-tv:.1f}s)", flush=True)
    return {
        "seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "arms": ARMS,
        "per_V": per_V,
        "elapsed_s": float(time.time() - t0),
    }


# ---------------------------------------------------------------------------
# Aggregation + verdict
# ---------------------------------------------------------------------------
def _mean_across_seeds(per_seed: List[Dict[str, Any]], V: int, field: str) -> float:
    vals = [s["per_V"][str(V)][field] for s in per_seed if str(V) in s["per_V"]]
    return float(np.mean(vals)) if vals else float("nan")


def _rel_deg(fid_lo: float, fid_hi_V: float) -> float:
    """Relative degradation from V_min fidelity to V_max fidelity."""
    denom = max(fid_lo, 1e-9)
    return float((fid_lo - fid_hi_V) / denom)


def compute_verdict(per_seed: List[Dict[str, Any]]
                    ) -> Tuple[str, str, Dict[str, Any], List[Dict[str, Any]]]:
    V_min, V_max = V_GRID[0], V_GRID[-1]
    ctrl_lo = _mean_across_seeds(per_seed, V_min, "ctrl_fid")
    ctrl_hi = _mean_across_seeds(per_seed, V_max, "ctrl_fid")
    treat_lo = _mean_across_seeds(per_seed, V_min, "treat_fid")
    treat_hi = _mean_across_seeds(per_seed, V_max, "treat_fid")
    route_hi = _mean_across_seeds(per_seed, V_max, "route_acc")
    mod_min = min(_mean_across_seeds(per_seed, V, "modularity_Q") for V in V_GRID)

    ctrl_rd = _rel_deg(ctrl_lo, ctrl_hi)
    treat_rd = _rel_deg(treat_lo, treat_hi)

    # cardinality (META_RULE_H)
    observed_units = sum(
        len(s["per_V"]) * len(s.get("arms", ARMS)) for s in per_seed
    )
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # per-seed cv of the headline treatment-flat metric (telemetry sanity)
    treat_hi_by_seed = [s["per_V"][str(V_max)]["treat_fid"] for s in per_seed
                        if str(V_max) in s["per_V"]]
    treat_cv = (float(np.std(treat_hi_by_seed) / (np.mean(treat_hi_by_seed) + 1e-9))
                if len(treat_hi_by_seed) > 1 else 0.0)

    gates = [
        record_gate("treat_flat_rd", treat_rd, TREAT_FLAT_RD_MAX, "<=",
                    "treatment relative degradation V_min->V_max"),
        record_gate("control_collapse_rd", ctrl_rd, CONTROL_COLLAPSE_RD_MIN, ">=",
                    "control relative degradation (discriminator must fire)"),
        record_gate("treat_abs_at_Vmax", treat_hi, TREAT_ABS_MIN, ">=",
                    "treatment absolute fidelity at V_max (holds)"),
        record_gate("route_acc_at_Vmax", route_hi, ROUTE_ACC_MIN, ">=",
                    "coarse-route accuracy at V_max (not leaking)"),
        record_gate("modularity_min", mod_min, MODULARITY_MIN, ">=",
                    "min Newman Q across V (real community structure)"),
    ]

    hp = (treat_rd <= TREAT_FLAT_RD_MAX and ctrl_rd >= CONTROL_COLLAPSE_RD_MIN
          and treat_hi >= TREAT_ABS_MIN and route_hi >= ROUTE_ACC_MIN
          and mod_min >= MODULARITY_MIN and cardinality_ok)

    # generator void: no real structure -> test meaningless
    if mod_min < MODULARITY_MIN:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_GENERATOR_NO_STRUCTURE: min modularity Q={mod_min:.3f} "
               f"< {MODULARITY_MIN} (KB not community-structured; test void).")
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: observed_units="
               f"{observed_units} != expected={EXPECTED_N_UNITS}.")
    elif ctrl_rd < CONTROL_COLLAPSE_RD_MIN:
        # discriminator did not fire (control did not collapse) -> inconclusive
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_DISCRIMINATOR_INERT: control_rd={ctrl_rd:.3f} "
               f"< {CONTROL_COLLAPSE_RD_MIN}; dense-additive control did NOT "
               f"collapse -> crosstalk regime not exercised; result void.")
    elif hp:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: TREATMENT flat (rd={treat_rd:.3f}<= {TREAT_FLAT_RD_MAX}, "
               f"abs@Vmax={treat_hi:.3f}) WHILE CONTROL collapses "
               f"(rd={ctrl_rd:.3f}>= {CONTROL_COLLAPSE_RD_MIN}); route@Vmax="
               f"{route_hi:.3f}; modQ_min={mod_min:.3f}. Community-bounded "
               f"two-stage retrieval decouples effective-V from total-V.")
    elif treat_rd < 0.5 * ctrl_rd:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: TREATMENT degrades slower than CONTROL "
               f"(treat_rd={treat_rd:.3f} < 0.5*ctrl_rd={0.5*ctrl_rd:.3f}) but "
               f"not flat (>{TREAT_FLAT_RD_MAX}). Partial mechanism; route "
               f"community-size v2. route@Vmax={route_hi:.3f} treat_abs={treat_hi:.3f}.")
    else:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL: TREATMENT degradation not distinguishable from CONTROL "
               f"(treat_rd={treat_rd:.3f} vs ctrl_rd={ctrl_rd:.3f}); community "
               f"routing does not decouple effective-V from total-V.")

    summary_stats = {
        "V_min": V_min, "V_max": V_max,
        "ctrl_fid_Vmin": ctrl_lo, "ctrl_fid_Vmax": ctrl_hi, "ctrl_rel_deg": ctrl_rd,
        "treat_fid_Vmin": treat_lo, "treat_fid_Vmax": treat_hi, "treat_rel_deg": treat_rd,
        "route_acc_Vmax": route_hi, "modularity_Q_min": mod_min,
        "treat_cv_across_seeds": treat_cv,
        "observed_units": observed_units, "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "curve": {
            str(V): {
                "ctrl_fid": _mean_across_seeds(per_seed, V, "ctrl_fid"),
                "treat_fid": _mean_across_seeds(per_seed, V, "treat_fid"),
                "route_acc": _mean_across_seeds(per_seed, V, "route_acc"),
                "modularity_Q": _mean_across_seeds(per_seed, V, "modularity_Q"),
            } for V in V_GRID
        },
    }
    return verdict, msg, summary_stats, gates


# ---------------------------------------------------------------------------
# Smoke self-checks (discriminator-fires + arms-differ)
# ---------------------------------------------------------------------------
def _smoke_gates(per_seed: List[Dict[str, Any]], summary_stats: Dict[str, Any]) -> None:
    """Runs only in smoke/self-test. Raises loudly on a vacuous or buggy smoke."""
    if RUN_MODE not in ("smoke",) and not _ARGS.self_test:
        return
    # META_RULE_AF: arms must differ (CONTROL vs TREATMENT predictions).
    for s in per_seed:
        for V, rec in s["per_V"].items():
            assert rec["ctrl_pred_hash"] != rec["treat_pred_hash"], (
                f"META_RULE_AF VIOLATION: CONTROL and TREATMENT predictions "
                f"bit-identical at seed={s['seed']} V={V}; arm-implementation bug.")
    # Vacuous-smoke guard: the dense-additive CONTROL MUST collapse at smoke V.
    # control_passed_headline = did CONTROL look flat (rd <= treat-flat gate)?
    ctrl_rd = summary_stats["ctrl_rel_deg"]
    control_passed_headline = bool(ctrl_rd <= TREAT_FLAT_RD_MAX)
    assert_discriminator_fires(
        control_passed_headline,
        control_name="CONTROL_dense_additive",
        headline_name="fidelity-flat-with-V",
        run_mode="smoke",
        extra=(f"ctrl_rel_deg={ctrl_rd:.3f}; needs to collapse "
               f">= {CONTROL_COLLAPSE_RD_MIN} for a discriminating smoke."))
    print(f"[smoke-gate] arms-differ OK; discriminator fires "
          f"(ctrl_rel_deg={ctrl_rd:.3f} >= {CONTROL_COLLAPSE_RD_MIN}).", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)

    if _ARGS.self_test:
        # Lightweight import + one tiny V point to prove the code path runs.
        rec = run_one_V(1024, 64, 7)
        assert rec["ctrl_pred_hash"] != rec["treat_pred_hash"], "self-test arms identical"
        print("[self-test] OK: one V point ran; arms differ.", flush=True)
        sys.exit(0)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds complete; running {remaining}",
          flush=True)

    t_start = time.time()
    for seed in remaining:
        result = run_seed(seed)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, result)

    per_seed_map = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    per_seed = list(per_seed_map.values())
    if not per_seed:
        raise RuntimeError("no per-seed partials aggregated; aborting")

    verdict, verdict_msg, summary_stats, gates = compute_verdict(per_seed)

    # smoke-only gates (raise loudly on vacuous/buggy smoke)
    _smoke_gates(per_seed, summary_stats)

    # stale-smoke-in-full guard
    modes = {s.get("run_mode", "?") for s in per_seed}
    if RUN_MODE == "full" and "smoke" in modes:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL: stale smoke partials in FULL run modes={modes}. " + verdict_msg

    elapsed_s = time.time() - t_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"community-bounded-retrieval V-sweep {V_GRID} N={N_DIM} "
            f"mode={RUN_MODE}: ctrl_rd={summary_stats['ctrl_rel_deg']:.3f} "
            f"treat_rd={summary_stats['treat_rel_deg']:.3f} "
            f"route@Vmax={summary_stats['route_acc_Vmax']:.3f} "
            f"modQ_min={summary_stats['modularity_Q_min']:.3f}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "V_grid": V_GRID,
        "n_seeds": len(SEEDS),
        "arms": ARMS,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": summary_stats["cardinality_ok"],
        "stats": summary_stats,
        "per_seed": [
            {"seed": s["seed"], "elapsed_s": s.get("elapsed_s"),
             "per_V": s["per_V"], "arms": s.get("arms", ARMS)}
            for s in per_seed
        ],
    }
    write_metrics(out_dir, metrics, gate_claims=gates)
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        _main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out, e)
        raise
