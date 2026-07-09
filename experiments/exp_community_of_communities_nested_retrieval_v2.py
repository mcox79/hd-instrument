"""community_of_communities_nested_retrieval_v2 -- BARRIER #3 completion.

Design source (self-authored, no sub-agents), builds directly on:
  experiments/exp_community_bounded_retrieval_scale_invariance_v1.py (commit cc804bfc1)
  preregs/2026-07-08_community_bounded_retrieval_scale_invariance_v1.md

WHAT v1 PROVED (MEASURED@data/exp_community_bounded_retrieval_scale_invariance_v1/metrics.json)
  Single-tier community routing decouples crosstalk from TOTAL store size V:
  TREATMENT stayed flat (fid 1.000) across V=580..58000 because per-community
  load = round(sqrt(V)) stayed BELOW the FHRR bundle-capacity Plate cliff
  (~630 at N=8192). CONTROL (global additive) collapsed (rd=1.000).

THE GAP v1 LEFT (the VET's isolation, the exact next step)
  v1's flat behaviour holds ONLY within the per-community capacity envelope.
  A SINGLE community whose OWN load crosses the cliff still collapses:
    within-community fine-decode  (MEASURED, VET isolation, N=8192):
      comm load 241 -> 0.992 ; 630 -> 0.680 ; 1000 -> 0.313 ; 2000 -> 0.094
  So single-tier routing bounds effective-load to sqrt(V) ONLY when community
  structure is fine-grained. If the community structure is COARSE (few large
  communities) OR per-community load is otherwise pushed past the cliff, one
  overloaded community collapses and the store is NOT scale-invariant in load.

MECHANISM UNDER TEST (v2)
  NESTED community-of-communities: add a SECOND routing tier INSIDE each
  top-level community. Tier-1 routes the query to its super-community (as v1).
  Tier-2 routes WITHIN that super-community to a leaf-community. Fine decode is
  over the leaf's ~sqrt(L) items only, so the decode load is held BELOW the
  cliff regardless of the per-community load L (and regardless of total V).
  Store codes near-orthogonal random bipolar, DECOUPLED from routing (the
  CERTIFIED correlation-hurts-store law); tier-1 and tier-2 gists live in
  SEPARATE near-orthogonal routing spaces; leaves nest within supers (leaf
  partition is a strict refinement of the super partition).

ARMS (2; identical store + identical tier-1 route -- the ONLY difference is the
2nd tier, so this is a clean paired comparison)
  SINGLE_TIER (v1-flat control, must-collapse under per-community overload):
    route tier-1 to super; unbind + peel/SIC cleanup over the WHOLE super bundle
    (L pairs, argmax over L). Reproduces the within-community cliff: collapses as
    per-community load L crosses ~630. SATURATION-VACUOUS GUARD arm: if it does
    NOT collapse at the stressed L, the cliff regime is not exercised -> void.
  NESTED (v2 treatment, should stay flat): same tier-1 route to super, THEN
    tier-2 route to leaf, unbind + peel/SIC cleanup over the leaf bundle only
    (~sqrt(L) pairs). Effective decode load bounded ~sqrt(L). Should stay FLAT
    across the per-community-load axis.

READOUT: operational hdlab.cleanup_family.peel_sic_readout (n_items=1). Binding
  = elementwise multiply on bipolar codes (self-inverse).

KILL-TEST (joint; the science question)
  Sweep BOTH axes: total V (via n_comm) AND per-community load L. HARD-PASS
  requires the NESTED arm to stay FLAT along the L axis (rd_L <= 0.10, abs >=
  0.70) WHILE SINGLE_TIER COLLAPSES (rd_L >= 0.30, discriminator FIRES) AND both
  routing tiers hold (tier1_acc, tier2_acc >= 0.90 at the largest point) AND
  real nested modular structure at BOTH tiers (Q_super, Q_leaf >= 0.30).

CALIBRATION (THEORETICAL / cited; re-MEASURED at smoke before FULL):
  Plate cliff V* ~ N/(2 ln V) ~ 630 at N=8192  THEORETICAL@Plate 1995.
  SINGLE_TIER decode load = L: L=256 ok, L=4000 >> cliff -> collapse guaranteed.
  NESTED leaf load = ceil(L/ceil(sqrt(L))) ~ sqrt(L): L=4000 -> 63 << cliff.
  Within-community cliff numbers above are MEASURED@ the v1 VET isolation.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (hash of SINGLE_TIER vs NESTED preds)
  - final_metrics_atomicity = tmp_replace (write_metrics + os.replace)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb/capacity-feasibility declared (Plate V* ~ N/(2 ln V))
  - baseline_in_band at smoke (SINGLE_TIER spans high->collapsed over L, not saturated)
  - discriminator survives scale (smoke at FULL per-community load L=4000; cliff is
    a per-community-load phenomenon so full L at reduced n_comm/seeds fires it)
  - assert_discriminator_fires: SINGLE_TIER must collapse over L at smoke (vacuous guard)
  - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_L * n_ncomm * n_arms
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
import hashlib
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


ANCHOR_NAME = "community_of_communities_nested_retrieval_v2"

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
N_DIM = 8192                      # THEORETICAL@Plate: cliff V* ~ N/(2 ln V) ~ 630
Q_QUERIES = 128                   # queries per point
ROUTE_NOISE = 0.5                 # cue = true gist + ROUTE_NOISE*noise
MOD_SUBSAMPLE = 1200              # nodes sampled for Newman-Q kNN graphs
MOD_K = 10                        # kNN degree
MOD_SUPERS_FOR_LEAF_Q = 3         # supers sampled for tier-2 (leaf) modularity

ARMS = ["SINGLE_TIER", "NESTED"]

if RUN_MODE == "smoke":
    # Cliff is a per-community-LOAD phenomenon; run FULL L at reduced n_comm/seeds
    # so the discriminator (SINGLE_TIER collapse at L=4000) fires in the smoke.
    L_GRID = [256, 4000]          # per-community load: below cliff, well above
    NCOMM_GRID = [3]              # total-V invariance axis (light: V<=12000)
    SEEDS = [7, 17]
else:
    L_GRID = [256, 630, 1600, 4000]     # per-community load axis (crosses cliff)
    NCOMM_GRID = [4, 12]                 # total-V axis: V = n_comm*L (1024 -> 48000)
    SEEDS = [7, 17, 23]

# unit = (seed, L, n_comm, arm)
EXPECTED_N_UNITS = len(SEEDS) * len(L_GRID) * len(NCOMM_GRID) * len(ARMS)

# --- bands (pre-reg; strict per META_RULE_L) --------------------------------
TREAT_FLAT_RD_MAX = 0.10          # NESTED relative degradation over L must be <= this
CONTROL_COLLAPSE_RD_MIN = 0.30    # SINGLE_TIER relative degradation over L must be >= this (discriminator)
TREAT_ABS_MIN = 0.70             # NESTED abs fidelity at L_max (holds, not flat-but-broken)
ROUTE_ACC_MIN = 0.90             # tier-1 AND tier-2 route accuracy at largest point (not leaking)
MODULARITY_MIN = 0.30            # real nested community structure at BOTH tiers (generator guard)
V_INVARIANCE_MAX = 0.15          # NESTED fidelity spread across n_comm at fixed L (soft telemetry gate)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},Q={Q_QUERIES},route_noise={ROUTE_NOISE},"
    f"L_GRID={L_GRID},NCOMM_GRID={NCOMM_GRID},seeds={SEEDS},mode={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers
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
    """Newman modularity Q of a ground-truth partition on a kNN cosine graph.

    feats (n,N); labels (n,). Returns (Q, n_edges). Guards against a
    secretly-uniform generator (no real community structure).
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


def _peel_group(bundle_rows: np.ndarray, keys: np.ndarray,
                codebook: np.ndarray, global_ids: np.ndarray) -> np.ndarray:
    """Batched fine-decode for a group of queries sharing one codebook.

    bundle_rows (nq,N) = the community/leaf bundle repeated (or gathered) per
    query; keys (nq,N) = query keys; codebook (m,N) = value codes of that
    community/leaf; global_ids (m,) = global item id per codebook row.
    Returns predicted GLOBAL item id per query (nq,).
    """
    est = bundle_rows * keys                                   # unbind (nq,N)
    local, _ = peel_sic_readout(est, codebook, n_items=1)      # (nq,1) argmax over m
    local = np.asarray(local).reshape(-1)
    return global_ids[local]


def run_one_point(N: int, L: int, n_comm: int, seed: int) -> Dict[str, Any]:
    """One (seed,L,n_comm) point: build nested KB, run both arms, measure.

    Nested generator: n_comm super-communities, each of load L. Within a super,
    L items partitioned into n_leaf = ceil(sqrt(L)) leaf-communities of size
    ~sqrt(L). Leaves nest within supers (strict refinement).
    """
    rng = np.random.default_rng(seed * 100003 + L * 131 + n_comm)
    V = n_comm * L
    n_leaf = int(math.ceil(math.sqrt(L)))
    leaf_size = int(math.ceil(L / n_leaf))

    # Item -> (super, leaf) assignment. Items 0..V-1 laid out super-major.
    super_of = np.repeat(np.arange(n_comm), L)                 # (V,)
    # local leaf id within a super: item's position within its super // leaf_size
    pos_in_super = np.tile(np.arange(L), n_comm)               # (V,)
    local_leaf = np.minimum(pos_in_super // leaf_size, n_leaf - 1)
    leaf_of = super_of * n_leaf + local_leaf                   # (V,) global leaf id
    n_leaf_total = n_comm * n_leaf

    # Store codes: near-orthogonal random bipolar, DECOUPLED (keys/values indep).
    K = _bipolar(rng, (V, N))
    Vv = _bipolar(rng, (V, N))
    P = K * Vv                                                 # bound pairs (V,N)

    # Routing gists in SEPARATE near-orthogonal spaces (decoupled from store).
    G_super = _bipolar(rng, (n_comm, N))
    G_leaf = _bipolar(rng, (n_leaf_total, N))

    # Bundles.
    B_super = np.zeros((n_comm, N), dtype=np.float32)
    np.add.at(B_super, super_of, P)                            # (n_comm,N)
    B_leaf = np.zeros((n_leaf_total, N), dtype=np.float32)
    np.add.at(B_leaf, leaf_of, P)                              # (n_leaf_total,N)

    # Members index (global ids) per super and per leaf.
    members_super = [np.where(super_of == s)[0] for s in range(n_comm)]
    members_leaf = [np.where(leaf_of == lf)[0] for lf in range(n_leaf_total)]

    # Decoupling telemetry: |cos| between store keys and their super gist.
    _s = rng.choice(V, size=min(256, V), replace=False)
    _kk = K[_s] / (np.linalg.norm(K[_s], axis=1, keepdims=True) + 1e-12)
    _gg = G_super[super_of[_s]] / (np.linalg.norm(G_super[super_of[_s]], axis=1, keepdims=True) + 1e-12)
    decouple_abs_cos = float(np.mean(np.abs(np.sum(_kk * _gg, axis=1))))

    # Queries.
    qidx = rng.choice(V, size=min(Q_QUERIES, V), replace=False)
    q_super = super_of[qidx]
    q_leaf = leaf_of[qidx]
    Q = len(qidx)

    # ---- Tier-1 route (SHARED by both arms): route cue -> super argmax ----
    cue1 = G_super[q_super].astype(np.float32) + ROUTE_NOISE * _bipolar(rng, (Q, N))
    route1 = (cue1 @ G_super.T).argmax(axis=1)                 # (Q,) over n_comm
    tier1_acc = float((route1 == q_super).mean())

    # ---- Tier-2 route (NESTED only): within predicted super -> leaf argmax ----
    # restrict argmax to the predicted super's n_leaf leaf pointers.
    cue2 = G_leaf[q_leaf].astype(np.float32) + ROUTE_NOISE * _bipolar(rng, (Q, N))
    route2 = np.full(Q, -1, dtype=np.int64)
    for i in range(Q):
        s = int(route1[i])
        lo = s * n_leaf
        scores = cue2[i] @ G_leaf[lo:lo + n_leaf].T            # (n_leaf,)
        route2[i] = lo + int(scores.argmax())
    tier2_acc = float((route2 == q_leaf).mean())

    # ---- SINGLE_TIER arm: fine-decode over WHOLE super bundle (L items) ----
    st_pred = np.full(Q, -1, dtype=np.int64)
    for s in np.unique(route1):
        idx = np.where(route1 == s)[0]
        if idx.size == 0:
            continue
        br = np.repeat(B_super[s][None, :], idx.size, axis=0)  # (nq,N)
        st_pred[idx] = _peel_group(br, K[qidx[idx]], Vv[members_super[s]],
                                   members_super[s])
    st_fid = float((st_pred == qidx).mean())

    # ---- NESTED arm: fine-decode over leaf bundle (~sqrt(L) items) ----
    ne_pred = np.full(Q, -1, dtype=np.int64)
    for lf in np.unique(route2):
        idx = np.where(route2 == lf)[0]
        if idx.size == 0:
            continue
        mem = members_leaf[lf]
        if mem.size == 0:
            continue
        br = np.repeat(B_leaf[lf][None, :], idx.size, axis=0)
        ne_pred[idx] = _peel_group(br, K[qidx[idx]], Vv[mem], mem)
    ne_fid = float((ne_pred == qidx).mean())

    # ---- Modularity guards (nested structure at BOTH tiers) ----
    n_sub = min(MOD_SUBSAMPLE, V)
    sub = rng.choice(V, size=n_sub, replace=False)
    f_super = G_super[super_of[sub]].astype(np.float32) + ROUTE_NOISE * _bipolar(rng, (n_sub, N))
    Q_super, super_edges = _newman_modularity_knn(f_super, super_of[sub], k=MOD_K)

    # tier-2: modularity of leaf partition WITHIN sampled supers (nesting witness).
    leaf_Qs: List[float] = []
    sampled_supers = list(range(min(MOD_SUPERS_FOR_LEAF_Q, n_comm)))
    for s in sampled_supers:
        items = members_super[s]
        if items.size < 4:
            continue
        take = items if items.size <= MOD_SUBSAMPLE else rng.choice(items, size=MOD_SUBSAMPLE, replace=False)
        f_leaf = G_leaf[leaf_of[take]].astype(np.float32) + ROUTE_NOISE * _bipolar(rng, (len(take), N))
        ql, _ = _newman_modularity_knn(f_leaf, leaf_of[take], k=MOD_K)
        leaf_Qs.append(ql)
    Q_leaf = float(np.min(leaf_Qs)) if leaf_Qs else 0.0

    st_h = hashlib.sha256(st_pred.astype(np.int64).tobytes()).hexdigest()
    ne_h = hashlib.sha256(ne_pred.astype(np.int64).tobytes()).hexdigest()

    return {
        "L": int(L), "n_comm": int(n_comm), "V": int(V),
        "n_leaf": int(n_leaf), "leaf_size": int(leaf_size),
        "st_fid": st_fid, "ne_fid": ne_fid,
        "tier1_acc": tier1_acc, "tier2_acc": tier2_acc,
        "Q_super": Q_super, "Q_leaf": Q_leaf,
        "super_edges": int(super_edges),
        "decouple_abs_cos": decouple_abs_cos,
        "st_pred_hash": st_h, "ne_pred_hash": ne_h,
    }


def run_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_point: Dict[str, Any] = {}
    for L in L_GRID:
        for n_comm in NCOMM_GRID:
            tv = time.time()
            rec = run_one_point(N_DIM, L, n_comm, seed)
            key = f"L{L}_nc{n_comm}"
            per_point[key] = rec
            print(f"[seed={seed} L={L} n_comm={n_comm} V={rec['V']}] "
                  f"single={rec['st_fid']:.3f} nested={rec['ne_fid']:.3f} "
                  f"t1={rec['tier1_acc']:.3f} t2={rec['tier2_acc']:.3f} "
                  f"Qs={rec['Q_super']:.3f} Ql={rec['Q_leaf']:.3f} "
                  f"leaf_size={rec['leaf_size']} ({time.time()-tv:.1f}s)", flush=True)
    return {
        "seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION, "arms": ARMS,
        "per_point": per_point,
        "elapsed_s": float(time.time() - t0),
    }


# ---------------------------------------------------------------------------
# Aggregation + verdict
# ---------------------------------------------------------------------------
def _mean_over_points(per_seed: List[Dict[str, Any]], L: int, field: str,
                      n_comm: int = None) -> float:
    vals = []
    for s in per_seed:
        for key, rec in s["per_point"].items():
            if rec["L"] != L:
                continue
            if n_comm is not None and rec["n_comm"] != n_comm:
                continue
            vals.append(rec[field])
    return float(np.mean(vals)) if vals else float("nan")


def _rel_deg(fid_lo: float, fid_hi: float) -> float:
    return float((fid_lo - fid_hi) / max(fid_lo, 1e-9))


def compute_verdict(per_seed: List[Dict[str, Any]]
                    ) -> Tuple[str, str, Dict[str, Any], List[Dict[str, Any]]]:
    L_min, L_max = L_GRID[0], L_GRID[-1]
    nc_max = NCOMM_GRID[-1]

    st_lo = _mean_over_points(per_seed, L_min, "st_fid")
    st_hi = _mean_over_points(per_seed, L_max, "st_fid")
    ne_lo = _mean_over_points(per_seed, L_min, "ne_fid")
    ne_hi = _mean_over_points(per_seed, L_max, "ne_fid")
    st_rd = _rel_deg(st_lo, st_hi)          # SINGLE_TIER collapse over L (discriminator)
    ne_rd = _rel_deg(ne_lo, ne_hi)          # NESTED degradation over L (should be flat)

    # routing + modularity at the largest, most-stressed point.
    tier1_hi = _mean_over_points(per_seed, L_max, "tier1_acc", n_comm=nc_max)
    tier2_hi = _mean_over_points(per_seed, L_max, "tier2_acc", n_comm=nc_max)

    Q_super_min = min(_mean_over_points(per_seed, L, "Q_super") for L in L_GRID)
    Q_leaf_min = min(_mean_over_points(per_seed, L, "Q_leaf") for L in L_GRID)

    # total-V invariance of NESTED: spread of ne_fid across n_comm at fixed L.
    v_inv_spread = 0.0
    for L in L_GRID:
        by_nc = [_mean_over_points(per_seed, L, "ne_fid", n_comm=nc) for nc in NCOMM_GRID]
        by_nc = [x for x in by_nc if not math.isnan(x)]
        if len(by_nc) > 1:
            v_inv_spread = max(v_inv_spread, float(max(by_nc) - min(by_nc)))

    # cardinality (META_RULE_H)
    observed_units = sum(len(s["per_point"]) * len(s.get("arms", ARMS)) for s in per_seed)
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # per-seed cv of the headline nested-flat metric.
    ne_hi_by_seed = []
    for s in per_seed:
        vals = [rec["ne_fid"] for rec in s["per_point"].values() if rec["L"] == L_max]
        if vals:
            ne_hi_by_seed.append(float(np.mean(vals)))
    ne_cv = (float(np.std(ne_hi_by_seed) / (np.mean(ne_hi_by_seed) + 1e-9))
             if len(ne_hi_by_seed) > 1 else 0.0)

    gates = [
        record_gate("nested_flat_rd_L", ne_rd, TREAT_FLAT_RD_MAX, "<=",
                    "NESTED relative degradation over per-community load L"),
        record_gate("single_tier_collapse_rd_L", st_rd, CONTROL_COLLAPSE_RD_MIN, ">=",
                    "SINGLE_TIER collapse over L (discriminator must fire)"),
        record_gate("nested_abs_at_Lmax", ne_hi, TREAT_ABS_MIN, ">=",
                    "NESTED absolute fidelity at L_max (holds)"),
        record_gate("tier1_route_acc", tier1_hi, ROUTE_ACC_MIN, ">=",
                    "tier-1 route accuracy at largest point"),
        record_gate("tier2_route_acc", tier2_hi, ROUTE_ACC_MIN, ">=",
                    "tier-2 route accuracy at largest point"),
        record_gate("modularity_super_min", Q_super_min, MODULARITY_MIN, ">=",
                    "min Newman Q of super partition (tier-1 structure)"),
        record_gate("modularity_leaf_min", Q_leaf_min, MODULARITY_MIN, ">=",
                    "min Newman Q of leaf partition within supers (tier-2 structure)"),
        record_gate("nested_v_invariance_spread", v_inv_spread, V_INVARIANCE_MAX, "<=",
                    "NESTED fidelity spread across n_comm at fixed L (total-V invariance)"),
    ]

    hp = (ne_rd <= TREAT_FLAT_RD_MAX and st_rd >= CONTROL_COLLAPSE_RD_MIN
          and ne_hi >= TREAT_ABS_MIN and tier1_hi >= ROUTE_ACC_MIN
          and tier2_hi >= ROUTE_ACC_MIN and Q_super_min >= MODULARITY_MIN
          and Q_leaf_min >= MODULARITY_MIN and cardinality_ok)

    if Q_super_min < MODULARITY_MIN or Q_leaf_min < MODULARITY_MIN:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_GENERATOR_NO_NESTED_STRUCTURE: Q_super_min={Q_super_min:.3f} "
               f"Q_leaf_min={Q_leaf_min:.3f} (need both >= {MODULARITY_MIN}); "
               f"nested community structure absent -> test void.")
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: observed_units="
               f"{observed_units} != expected={EXPECTED_N_UNITS}.")
    elif st_rd < CONTROL_COLLAPSE_RD_MIN:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_DISCRIMINATOR_INERT: single_tier_rd_L={st_rd:.3f} "
               f"< {CONTROL_COLLAPSE_RD_MIN}; the v1-flat single-tier control did "
               f"NOT collapse under per-community overload -> cliff regime not "
               f"exercised; result void.")
    elif hp:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: NESTED flat over per-community load "
               f"(rd_L={ne_rd:.3f}<= {TREAT_FLAT_RD_MAX}, abs@Lmax={ne_hi:.3f}) WHILE "
               f"SINGLE_TIER collapses (rd_L={st_rd:.3f}>= {CONTROL_COLLAPSE_RD_MIN}); "
               f"tier1={tier1_hi:.3f} tier2={tier2_hi:.3f}; Qs_min={Q_super_min:.3f} "
               f"Ql_min={Q_leaf_min:.3f}; v_inv={v_inv_spread:.3f}. A 2nd routing "
               f"tier bounds decode load to ~sqrt(L) regardless of per-community load.")
    elif ne_rd < 0.5 * st_rd:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: NESTED degrades slower than SINGLE_TIER "
               f"(ne_rd={ne_rd:.3f} < 0.5*st_rd={0.5*st_rd:.3f}) but not flat "
               f"(> {TREAT_FLAT_RD_MAX}). Partial: leaf load still near cliff or a "
               f"3rd tier needed. tier2={tier2_hi:.3f} nested_abs={ne_hi:.3f}.")
    else:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL: NESTED degradation not distinguishable from SINGLE_TIER "
               f"(ne_rd={ne_rd:.3f} vs st_rd={st_rd:.3f}); a 2nd routing tier does "
               f"NOT bound decode load below the cliff.")

    curve = {}
    for L in L_GRID:
        curve[str(L)] = {
            "st_fid": _mean_over_points(per_seed, L, "st_fid"),
            "ne_fid": _mean_over_points(per_seed, L, "ne_fid"),
            "tier1_acc": _mean_over_points(per_seed, L, "tier1_acc"),
            "tier2_acc": _mean_over_points(per_seed, L, "tier2_acc"),
            "Q_super": _mean_over_points(per_seed, L, "Q_super"),
            "Q_leaf": _mean_over_points(per_seed, L, "Q_leaf"),
        }

    summary_stats = {
        "L_min": L_min, "L_max": L_max, "nc_max": nc_max,
        "single_tier_fid_Lmin": st_lo, "single_tier_fid_Lmax": st_hi,
        "single_tier_rel_deg_L": st_rd,
        "nested_fid_Lmin": ne_lo, "nested_fid_Lmax": ne_hi,
        "nested_rel_deg_L": ne_rd,
        "tier1_acc_Lmax": tier1_hi, "tier2_acc_Lmax": tier2_hi,
        "Q_super_min": Q_super_min, "Q_leaf_min": Q_leaf_min,
        "nested_v_invariance_spread": v_inv_spread,
        "nested_cv_across_seeds": ne_cv,
        "observed_units": observed_units, "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "curve": curve,
    }
    return verdict, msg, summary_stats, gates


# ---------------------------------------------------------------------------
# Smoke self-checks (arms-differ + discriminator-fires)
# ---------------------------------------------------------------------------
def _smoke_gates(per_seed: List[Dict[str, Any]], summary_stats: Dict[str, Any]) -> None:
    if RUN_MODE not in ("smoke",) and not _ARGS.self_test:
        return
    # META_RULE_AF: SINGLE_TIER vs NESTED predictions must differ.
    # LEGITIMATE exemption (declared arms_differ_exempted in pre-reg): at an EASY
    # per-community load (L below the cliff) BOTH arms recover ground truth
    # perfectly, so both prediction vectors equal qidx and hash identically. That
    # is correctness, not a shared-code-path bug. Flag identical-hash points ONLY
    # when they are NOT both-perfect; AND require arms differ at the stressed L_max
    # point (a real mechanism difference must manifest where the control collapses).
    for s in per_seed:
        for key, rec in s["per_point"].items():
            if rec["st_pred_hash"] == rec["ne_pred_hash"]:
                both_perfect = (rec["st_fid"] >= 0.999 and rec["ne_fid"] >= 0.999)
                assert both_perfect, (
                    f"META_RULE_AF VIOLATION: SINGLE_TIER and NESTED predictions "
                    f"bit-identical at seed={s['seed']} {key} but NOT both-perfect "
                    f"(st_fid={rec['st_fid']:.3f} ne_fid={rec['ne_fid']:.3f}); "
                    f"arm-implementation bug.")
    L_max = L_GRID[-1]
    any_diff_at_Lmax = any(
        rec["st_pred_hash"] != rec["ne_pred_hash"]
        for s in per_seed for rec in s["per_point"].values() if rec["L"] == L_max)
    assert any_diff_at_Lmax, (
        f"META_RULE_AF VIOLATION: SINGLE_TIER and NESTED predictions bit-identical "
        f"at every L_max={L_max} point; the discriminator did not manifest as a "
        f"prediction difference (arms not truly distinct at the stressed load).")
    # Vacuous-smoke guard: the v1-flat SINGLE_TIER control MUST collapse over L.
    st_rd = summary_stats["single_tier_rel_deg_L"]
    control_passed_headline = bool(st_rd <= TREAT_FLAT_RD_MAX)
    assert_discriminator_fires(
        control_passed_headline,
        control_name="SINGLE_TIER_v1_flat",
        headline_name="fidelity-flat-with-per-community-load",
        run_mode="smoke",
        extra=(f"single_tier_rel_deg_L={st_rd:.3f}; needs to collapse "
               f">= {CONTROL_COLLAPSE_RD_MIN} for a discriminating smoke."))
    print(f"[smoke-gate] arms-differ OK; discriminator fires "
          f"(single_tier_rel_deg_L={st_rd:.3f} >= {CONTROL_COLLAPSE_RD_MIN}).", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)

    if _ARGS.self_test:
        # N=1024 cliff ~ 1024/(2 ln 400) ~ 85; L=400 >> cliff so SINGLE_TIER
        # collapses while NESTED (leaf ~20) holds -> arms MUST differ (robust).
        rec = run_one_point(1024, 400, 2, 7)
        assert rec["st_pred_hash"] != rec["ne_pred_hash"], "self-test arms identical"
        assert rec["st_fid"] < rec["ne_fid"], (
            f"self-test discriminator inert: st_fid={rec['st_fid']:.3f} "
            f">= ne_fid={rec['ne_fid']:.3f}")
        print(f"[self-test] OK: nested point ran; arms differ "
              f"(single={rec['st_fid']:.3f} nested={rec['ne_fid']:.3f}).", flush=True)
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
    _smoke_gates(per_seed, summary_stats)

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
            f"nested-community-of-communities L-sweep {L_GRID} n_comm {NCOMM_GRID} "
            f"N={N_DIM} mode={RUN_MODE}: st_rd_L={summary_stats['single_tier_rel_deg_L']:.3f} "
            f"ne_rd_L={summary_stats['nested_rel_deg_L']:.3f} "
            f"tier1@Lmax={summary_stats['tier1_acc_Lmax']:.3f} "
            f"tier2@Lmax={summary_stats['tier2_acc_Lmax']:.3f} "
            f"Qs_min={summary_stats['Q_super_min']:.3f} Ql_min={summary_stats['Q_leaf_min']:.3f}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "L_grid": L_GRID,
        "n_comm_grid": NCOMM_GRID,
        "n_seeds": len(SEEDS),
        "arms": ARMS,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": summary_stats["cardinality_ok"],
        "stats": summary_stats,
        "per_seed": [
            {"seed": s["seed"], "elapsed_s": s.get("elapsed_s"),
             "per_point": s["per_point"], "arms": s.get("arms", ARMS)}
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
