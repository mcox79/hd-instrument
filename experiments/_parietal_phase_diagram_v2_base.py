"""Shared engine for substrate_parietal_movable_rebind_phase_diagram_v2.

CHUNKED across 3 seed siblings (seed_7 / seed_13 / seed_19). Each sibling
imports this module and calls run_one_seed(seed_int).

Pre-reg: preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v2.md

v2 design vs v1:
  - v1 found cliff at n_obj=200 at N_DIM=1024 grid=32 but did NOT characterize
    the failure-mode floor or how cliff location scales with substrate dim.
  - v2 EXTENDS the sweep to fill the phase diagram:
       * N_DIM in {512, 1024, 2048} (sub/equal/super scale relative to v1)
       * n_obj in {50, 100, 200, 400} (push past the v1 cliff into floor)
       * grid in {16, 32} (drop tiny grids; need room for big n_obj)
       * move_freq in {0.0, 0.2, 0.5, 0.8}
  - PARETO-AUC discriminator added (chain-grade lesson: report area under
    recall-vs-load curve, not just one-shot recall).
  - HONEST-DOWNWARD: cell can return MIDDLE_BAND when phase diagram is
    partially-mapped; HARD_PASS requires all 4 quadrants (sat, strong, cliff,
    floor) populated by >=1 point each.

CRLB pre-validation (Plate capacity N_cap = N_DIM / (4 * ln(M_codebook));
M_codebook = max n_pos = 32*32 = 1024):
  N_DIM=512:  cap=18.5; n_obj=50 ratio=2.7 -> floor; n_obj=400 ratio=21.7 -> floor
  N_DIM=1024: cap=36.9; n_obj=50 ratio=1.4 -> cliff; n_obj=200 ratio=5.4 -> floor
  N_DIM=2048: cap=73.9; n_obj=50 ratio=0.7 -> strong; n_obj=100 ratio=1.4 -> cliff;
              n_obj=200 ratio=2.7 -> floor
Discriminator-survives-scale: the (N_DIM, n_obj) cross-product spans saturate
through floor across the grid. v1 smoke confirmed cliff at (grid=32, n_obj=200,
N_DIM=1024) -> 0.25 recall; v2 smoke at the same corner is an explicit anchor.

Three arms per point (BIT-DISTINCT per META_RULE_AF):
  SUBSTRATE_HRR    : HRR-bind + apply MOVE rebind + unbind cleanup
  RANDOM           : chance 1/n_pos
  STATIC_BINDING   : HRR-bind at init; NEVER apply MOVE; query post-move pos

ASCII-only; no emojis; self-contained.
Author: exp_dev 2026-06-28.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME_PREFIX = "substrate_parietal_movable_rebind_phase_diagram_v2"

# Pre-reg LOCKED bands
HP_SATURATE = 0.90             # saturate band
HP_STRONG = 0.60               # strong-recall band
HP_CLIFF = 0.40                # cliff band (recall <= HP_CLIFF)
HP_FLOOR = 0.10                # floor band (recall <= HP_FLOOR)
HP_LIFT_OVER_STATIC = 0.30     # min substrate - static lift to count as "mechanism active"
HP_MIN_FRAC_LIFT = 0.30        # >=30% of points show lift >= HP_LIFT_OVER_STATIC
HP_PARETO_AUC_MIN = 0.20       # AUC(substrate) - AUC(static) >= 0.20 to PASS
META_AM_TOL = 0.02             # SUBSTRATE must beat RANDOM by >= this at EVERY point

# Substrate constants
POSITION_NOISE = 0.05          # fixed (chunking decision)

# Sweep grids (FULL)
N_DIMS = [512, 1024, 2048]
GRID_SIZES = [16, 32]
N_OBJS = [50, 100, 200, 400]
MOVE_FREQS = [0.0, 0.2, 0.5, 0.8]

# Smoke corners: span saturate / strong / cliff / floor at FULL N_DIM values
# (DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke runs at the same N_DIM range as full)
# Each entry: (N_DIM, grid, n_obj, move_freq, expected_band)
SMOKE_CORNERS = [
    (2048, 16, 50, 0.5),   # saturate expected (~0.95+)
    (1024, 16, 50, 0.5),   # cliff expected (~0.40-0.60)
    (1024, 32, 200, 0.5),  # v1-anchored cliff (~0.25)
    (512,  32, 400, 0.5),  # floor expected (<0.10)
]

N_SCENES_PER_POINT_FULL = 20
N_SCENES_PER_POINT_SMOKE = 20  # same; smoke discriminator must survive scale

EXPECTED_ARMS = ["substrate_hrr", "random", "static_binding"]


def _hardening_config_str(seed: int, mode: str, n_points: int) -> str:
    return (
        "ANCHOR=%s_seed_%d,N_DIMS=%s,grids=%s,n_objs=%s,move_freqs=%s,"
        "pos_noise=%.2f,n_scenes=%d,mode=%s,n_points=%d,"
        "HP_sat=%.2f,HP_strong=%.2f,HP_cliff=%.2f,HP_floor=%.2f,"
        "HP_lift_static=%.2f,HP_frac_lift=%.2f,HP_pareto_auc_min=%.2f,"
        "META_AM_tol=%.2f,arms=%s,"
        "hardening=META_AC_CRLB+AE_smoke_gate+AF_arms_differ+AG_atomic_write+"
        "AH_main_guard+AM_no_trivial+AN_complete+H_cardinality_ok"
    ) % (
        ANCHOR_NAME_PREFIX, seed, N_DIMS, GRID_SIZES, N_OBJS, MOVE_FREQS,
        POSITION_NOISE,
        (N_SCENES_PER_POINT_SMOKE if mode == "smoke" else N_SCENES_PER_POINT_FULL),
        mode, n_points,
        HP_SATURATE, HP_STRONG, HP_CLIFF, HP_FLOOR,
        HP_LIFT_OVER_STATIC, HP_MIN_FRAC_LIFT, HP_PARETO_AUC_MIN,
        META_AM_TOL, EXPECTED_ARMS,
    )


# ---------------------- FHRR primitives ----------------------

def random_unit_phases(M: int, n_half: int, g: np.random.Generator) -> np.ndarray:
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (c * np.conj(key)).astype(np.complex64)


def cleanup_argmax(q: np.ndarray, codebook: np.ndarray) -> int:
    sims = np.real(codebook @ np.conj(q))
    return int(np.argmax(sims))


def make_grid_positions(g: np.random.Generator, n_half: int,
                          grid_r: int, grid_c: int,
                          k_scales: int = 4,
                          noise: float = 0.0) -> np.ndarray:
    """Frady-Kanerva multi-scale fractional-power binding."""
    n_pos = grid_r * grid_c
    out = np.zeros((n_pos, n_half), dtype=np.complex64)
    for s in range(k_scales):
        base_r = g.uniform(-np.pi, np.pi, size=n_half).astype(np.float32)
        base_c = g.uniform(-np.pi, np.pi, size=n_half).astype(np.float32)
        scale_factor = float(2 ** s) / max(1, k_scales)
        for r in range(grid_r):
            for c in range(grid_c):
                pos_idx = r * grid_c + c
                phase = (r * base_r + c * base_c) * scale_factor
                contrib = np.exp(1j * phase).astype(np.complex64)
                out[pos_idx] = out[pos_idx] + contrib
    if noise > 0:
        jitter = g.normal(0.0, noise, size=(n_pos, n_half)).astype(np.float32)
        out = out * np.exp(1j * jitter).astype(np.complex64)
    out = out / (np.abs(out) + 1e-9)
    return out.astype(np.complex64)


# ---------------------- scene generation ----------------------

def make_scenes(n_scenes: int, n_obj: int, n_pos: int,
                  move_freq: float, g: np.random.Generator) -> List[Dict]:
    """Each scene = initial assignments + MOVE ops + query."""
    scenes: List[Dict] = []
    n_obj_eff = min(n_obj, n_pos)
    for _ in range(n_scenes):
        initial = g.choice(n_pos, size=n_obj_eff, replace=False).tolist()
        obj_to_pos = {k: int(initial[k]) for k in range(n_obj_eff)}
        n_moves = int(np.floor(move_freq * n_obj_eff))
        moves: List[Tuple[int, int]] = []
        for _ in range(n_moves):
            obj_k = int(g.integers(n_obj_eff))
            avail = [p for p in range(n_pos)
                     if p not in obj_to_pos.values()]
            if not avail:
                break
            new_pos = int(g.choice(avail))
            moves.append((obj_k, new_pos))
            obj_to_pos[obj_k] = new_pos
        if moves:
            query_obj = moves[-1][0]
        else:
            query_obj = int(g.integers(n_obj_eff))
        true_pos = obj_to_pos[query_obj]
        scenes.append({
            "initial": [(k, int(initial[k])) for k in range(n_obj_eff)],
            "moves": moves,
            "query_obj": query_obj,
            "true_pos": true_pos,
            "n_obj_eff": n_obj_eff,
        })
    return scenes


# ---------------------- arms ----------------------

def run_arm_random(scenes: List[Dict], n_pos: int,
                     g: np.random.Generator) -> Dict[str, Any]:
    preds: List[int] = []
    correct = 0
    for sc in scenes:
        p = int(g.integers(n_pos))
        preds.append(p)
        if p == sc["true_pos"]:
            correct += 1
    return {"recall": correct / max(1, len(scenes)),
            "n_queries": len(scenes), "predictions": preds}


def run_arm_static_binding(scenes: List[Dict], positions: np.ndarray,
                              role_atoms: np.ndarray) -> Dict[str, Any]:
    """HRR bind at init; NEVER apply MOVE; query post-move pos."""
    preds: List[int] = []
    correct = 0
    for sc in scenes:
        parts = []
        for (k, pos) in sc["initial"]:
            parts.append(bind(role_atoms[k], positions[pos]))
        bag = np.sum(np.stack(parts, axis=0), axis=0).astype(np.complex64)
        q = unbind(bag, role_atoms[sc["query_obj"]])
        pred = cleanup_argmax(q, positions)
        preds.append(pred)
        if pred == sc["true_pos"]:
            correct += 1
    return {"recall": correct / max(1, len(scenes)),
            "n_queries": len(scenes), "predictions": preds}


def run_arm_substrate_hrr(scenes: List[Dict], positions: np.ndarray,
                            role_atoms: np.ndarray) -> Dict[str, Any]:
    """HRR bind at init + APPLY MOVE ops (sub old bind, add new bind) + query."""
    preds: List[int] = []
    correct = 0
    for sc in scenes:
        parts = []
        cur_pos = {}
        for (k, pos) in sc["initial"]:
            parts.append(bind(role_atoms[k], positions[pos]))
            cur_pos[k] = pos
        bag = np.sum(np.stack(parts, axis=0), axis=0).astype(np.complex64)
        for (obj_k, new_pos) in sc["moves"]:
            old_pos = cur_pos[obj_k]
            old_bind = bind(role_atoms[obj_k], positions[old_pos])
            new_bind = bind(role_atoms[obj_k], positions[new_pos])
            bag = bag - old_bind + new_bind
            cur_pos[obj_k] = new_pos
        q = unbind(bag, role_atoms[sc["query_obj"]])
        pred = cleanup_argmax(q, positions)
        preds.append(pred)
        if pred == sc["true_pos"]:
            correct += 1
    return {"recall": correct / max(1, len(scenes)),
            "n_queries": len(scenes), "predictions": preds}


# ---------------------- per-point evaluator ----------------------

def eval_one_point(n_dim: int, grid: int, n_obj: int, move_freq: float,
                    n_scenes: int, seed: int) -> Dict[str, Any]:
    n_half = n_dim // 2
    g = np.random.default_rng(
        seed * 100003 + n_dim * 9973 + grid * 1009
        + n_obj * 101 + int(move_freq * 1000))
    n_pos = grid * grid
    positions = make_grid_positions(g, n_half, grid, grid,
                                       k_scales=4, noise=POSITION_NOISE)
    role_atoms = random_unit_phases(max(1, n_obj), n_half, g)
    scenes = make_scenes(n_scenes, n_obj, n_pos, move_freq, g)

    rand_res = run_arm_random(scenes, n_pos, g)
    static_res = run_arm_static_binding(scenes, positions, role_atoms)
    subst_res = run_arm_substrate_hrr(scenes, positions, role_atoms)

    return {
        "n_dim": n_dim,
        "grid": grid, "n_obj": n_obj, "move_freq": move_freq,
        "n_pos": n_pos, "n_scenes": n_scenes,
        "substrate_recall": subst_res["recall"],
        "random_recall": rand_res["recall"],
        "static_recall": static_res["recall"],
        "substrate_lift_over_random": subst_res["recall"] - rand_res["recall"],
        "substrate_lift_over_static": subst_res["recall"] - static_res["recall"],
        "n_queries": subst_res["n_queries"],
        "predictions_substrate": subst_res["predictions"],
        "predictions_random": rand_res["predictions"],
        "predictions_static": static_res["predictions"],
    }


# ---------------------- arms-must-differ ----------------------

def arms_differ_check(per_point: List[Dict]) -> Tuple[bool, Dict[str, str]]:
    """SHA-256 over concatenated prediction lists per arm.

    All 3 hashes must be distinct (META_RULE_AF).
    """
    def _hash(arm_key: str) -> str:
        h = hashlib.sha256()
        for pt in per_point:
            for p in pt[arm_key]:
                h.update(str(p).encode("ascii"))
            h.update(b"|")
        return h.hexdigest()
    hashes = {
        "substrate": _hash("predictions_substrate"),
        "random": _hash("predictions_random"),
        "static": _hash("predictions_static"),
    }
    distinct = len(set(hashes.values())) == 3
    return distinct, hashes


# ---------------------- Pareto-AUC discriminator ----------------------

def compute_pareto_auc(per_point: List[Dict]) -> Dict[str, Any]:
    """Pareto-AUC: area under (recall vs n_obj) curve, averaged across other axes.

    For each (n_dim, grid, move_freq) bucket, sort by n_obj ascending and
    trapezoidally integrate recall over normalized n_obj range. Average the
    bucket-AUCs to get an overall arm-AUC.

    Returns AUC for substrate / static / random + lift = substrate - static.
    Higher AUC = better recall-load tradeoff.
    """
    def _bucket_key(pt):
        return (pt["n_dim"], pt["grid"], pt["move_freq"])

    buckets: Dict[Tuple[int, int, float], List[Dict]] = {}
    for pt in per_point:
        buckets.setdefault(_bucket_key(pt), []).append(pt)

    def _arm_auc(arm: str) -> float:
        bucket_aucs = []
        for _, pts in buckets.items():
            if len(pts) < 2:
                continue
            ordered = sorted(pts, key=lambda p: p["n_obj"])
            xs = np.array([p["n_obj"] for p in ordered], dtype=np.float64)
            ys = np.array([p[arm] for p in ordered], dtype=np.float64)
            x_min, x_max = xs[0], xs[-1]
            if x_max <= x_min:
                continue
            xs_norm = (xs - x_min) / (x_max - x_min)
            auc = float(np.trapz(ys, xs_norm))
            bucket_aucs.append(auc)
        if not bucket_aucs:
            return float("nan")
        return float(np.mean(bucket_aucs))

    auc_subst = _arm_auc("substrate_recall")
    auc_static = _arm_auc("static_recall")
    auc_random = _arm_auc("random_recall")
    return {
        "auc_substrate": auc_subst,
        "auc_static": auc_static,
        "auc_random": auc_random,
        "pareto_lift_subst_static": (
            auc_subst - auc_static
            if not (math.isnan(auc_subst) or math.isnan(auc_static))
            else float("nan")),
        "pareto_lift_subst_random": (
            auc_subst - auc_random
            if not (math.isnan(auc_subst) or math.isnan(auc_random))
            else float("nan")),
        "n_buckets": len(buckets),
    }


# ---------------------- verdict ----------------------

def _meta_am_violated(p: Dict) -> bool:
    """META_RULE_AM: substrate must beat random + tol.

    Floor-regime exemption: when substrate is at or below chance (1/n_pos),
    the test has no statistical power -- both arms can hit zero in n_scenes.
    Only fire META_AM when substrate exceeds 2x chance (meaningful regime)
    AND fails to beat random + tol.
    """
    chance = 1.0 / max(1, p["n_pos"])
    if p["substrate_recall"] <= 2.0 * chance:
        # Floor regime: no statistical power to distinguish; both arms near zero
        return False
    return p["substrate_recall"] < p["random_recall"] + META_AM_TOL


def compute_verdict(per_point: List[Dict],
                     arms_distinct: bool, hashes: Dict[str, str],
                     n_expected: int) -> Tuple[str, str, Dict[str, Any]]:
    cardinality_ok = (len(per_point) == n_expected)
    am_breach = [(p["n_dim"], p["grid"], p["n_obj"], p["move_freq"])
                 for p in per_point
                 if _meta_am_violated(p)]
    n_sat = sum(1 for p in per_point if p["substrate_recall"] >= HP_SATURATE)
    n_strong = sum(1 for p in per_point if HP_STRONG <= p["substrate_recall"] < HP_SATURATE)
    n_cliff = sum(1 for p in per_point if HP_FLOOR < p["substrate_recall"] <= HP_CLIFF)
    n_floor = sum(1 for p in per_point if p["substrate_recall"] <= HP_FLOOR)
    n_strong_lift = sum(1 for p in per_point
                        if p["substrate_lift_over_static"] >= HP_LIFT_OVER_STATIC)
    frac_lift = n_strong_lift / max(1, len(per_point))

    pareto = compute_pareto_auc(per_point)

    # cliff_curve: (n_dim, grid) -> smallest n_obj where substrate <= HP_CLIFF
    cliff_curve: Dict[str, Any] = {}
    for pt in per_point:
        key = "N=%d_grid=%d" % (pt["n_dim"], pt["grid"])
        if pt["substrate_recall"] <= HP_CLIFF:
            cur = cliff_curve.get(key)
            if cur is None or pt["n_obj"] < cur:
                cliff_curve[key] = pt["n_obj"]

    extra = {
        "cardinality_ok": cardinality_ok,
        "n_points": len(per_point),
        "n_expected": n_expected,
        "arms_distinct": arms_distinct,
        "arms_hashes": hashes,
        "META_AM_breaches": am_breach,
        "n_saturated": n_sat,
        "n_strong": n_strong,
        "n_cliff": n_cliff,
        "n_floor": n_floor,
        "n_strong_lift": n_strong_lift,
        "frac_strong_lift": frac_lift,
        "pareto_auc": pareto,
        "cliff_curve_first_failure_n_obj": cliff_curve,
    }
    if not cardinality_ok:
        return ("HARD_FAIL", "CARDINALITY_BREACH n=%d expected=%d" % (
            len(per_point), n_expected), extra)
    if not arms_distinct:
        return ("HARD_FAIL", "ARMS_NOT_DISTINCT hashes=%s" % hashes, extra)
    if am_breach:
        return ("HARD_FAIL", "META_AM_BREACH %d points SUBSTRATE<=RANDOM"
                % len(am_breach), extra)

    pareto_lift = pareto["pareto_lift_subst_static"]
    quadrants = (n_sat >= 1) + (n_strong >= 1) + (n_cliff >= 1) + (n_floor >= 1)

    # HARD_PASS: all 4 quadrants populated + frac_lift OK + pareto_auc OK
    if (quadrants == 4
            and frac_lift >= HP_MIN_FRAC_LIFT
            and not math.isnan(pareto_lift)
            and pareto_lift >= HP_PARETO_AUC_MIN):
        return ("HARD_PASS",
                "HARD_PASS | quadrants=4/4 sat=%d strong=%d cliff=%d floor=%d "
                "frac_lift=%.2f pareto_auc_lift=%.3f"
                % (n_sat, n_strong, n_cliff, n_floor, frac_lift, pareto_lift),
                extra)
    # ALL_SATURATE: discriminator did not survive scale (caught Wave 3 ANCHOR 3)
    if n_sat == len(per_point):
        return ("HARD_FAIL",
                "ALL_SATURATE n_sat=%d/%d (discriminator did not survive scale)"
                % (n_sat, len(per_point)), extra)
    # ALL_FLOOR: cell broken
    if n_floor == len(per_point):
        return ("HARD_FAIL",
                "ALL_FLOOR n_floor=%d (cell broken)" % n_floor, extra)
    # HONEST-DOWNWARD: partial phase-fill = MIDDLE_BAND
    return ("MIDDLE_BAND",
            "MB | quadrants=%d/4 sat=%d strong=%d cliff=%d floor=%d "
            "frac_lift=%.2f pareto_auc_lift=%s"
            % (quadrants, n_sat, n_strong, n_cliff, n_floor, frac_lift,
                ("%.3f" % pareto_lift if not math.isnan(pareto_lift) else "nan")),
            extra)


def smoke_verdict(per_point: List[Dict],
                    arms_distinct: bool, hashes: Dict[str, str]
                    ) -> Tuple[str, str, Dict[str, Any]]:
    """Smoke gate (4 corner points): per pre-reg."""
    cardinality_ok = (len(per_point) == 4)
    am_breach = [(p["n_dim"], p["grid"], p["n_obj"], p["move_freq"])
                 for p in per_point
                 if _meta_am_violated(p)]
    n_sat = sum(1 for p in per_point if p["substrate_recall"] >= HP_SATURATE)
    n_floor = sum(1 for p in per_point if p["substrate_recall"] <= HP_FLOOR)
    n_strong = sum(1 for p in per_point
                   if (p["substrate_recall"]
                       - max(p["random_recall"], p["static_recall"])) >= 0.20)
    extra = {
        "cardinality_ok": cardinality_ok, "n_points": len(per_point),
        "arms_distinct": arms_distinct, "arms_hashes": hashes,
        "META_AM_breaches": am_breach,
        "n_saturated": n_sat, "n_floor": n_floor,
        "n_strong_discriminator": n_strong,
    }
    if not cardinality_ok:
        return ("HARD_FAIL", "SMOKE_CARDINALITY_BREACH n=%d expected=4"
                % len(per_point), extra)
    if not arms_distinct:
        return ("HARD_FAIL", "SMOKE_ARMS_NOT_DISTINCT %s" % hashes, extra)
    if am_breach:
        return ("HARD_FAIL", "SMOKE_META_AM_BREACH %d points"
                % len(am_breach), extra)
    if n_strong < 2:
        return ("HARD_FAIL",
                "SMOKE_DISCRIMINATOR_WEAK n_strong=%d (<2 required)"
                % n_strong, extra)
    if n_sat < 1:
        return ("HARD_FAIL",
                "SMOKE_NO_SATURATION (need >=1 corner saturating at N=2048)",
                extra)
    if n_floor < 1:
        return ("HARD_FAIL",
                "SMOKE_NO_FLOOR (need >=1 corner at floor for full-N discrim)",
                extra)
    return ("HARD_PASS",
            "SMOKE_PASS | n_sat=%d n_floor=%d n_strong=%d arms_distinct=%s"
            % (n_sat, n_floor, n_strong, arms_distinct), extra)


# ---------------------- top-level seed runner ----------------------

def _full_points() -> List[Tuple[int, int, int, float]]:
    """Generate full (n_dim, grid, n_obj, move_freq) tuples, filtering n_obj<=n_pos."""
    pts = []
    for n_dim in N_DIMS:
        for grid in GRID_SIZES:
            n_pos = grid * grid
            for n_obj in N_OBJS:
                if n_obj > n_pos:
                    continue
                for mf in MOVE_FREQS:
                    pts.append((n_dim, grid, n_obj, mf))
    return pts


def run_one_seed(seed: int, smoke: bool = False,
                  self_test: bool = False) -> int:
    """Run all points for a single seed; write metrics.json.

    Returns exit code (0 ok, non-zero fail).
    """
    started = time.time()
    anchor = "%s_seed_%d" % (ANCHOR_NAME_PREFIX, seed)
    env_name = os.environ.get("HDLAB_EXP_NAME", anchor)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # self-test: 1 corner only, tiny scenes, prove mechanism
    if self_test:
        config_str = _hardening_config_str(seed, "self_test", 1)
        try:
            pt = eval_one_point(n_dim=512, grid=4, n_obj=3, move_freq=0.5,
                                  n_scenes=3, seed=seed)
            ok = (pt["substrate_recall"] > pt["random_recall"] + 0.05)
            arms_distinct, hashes = arms_differ_check([pt])
            res = {
                "anchor_name": anchor,
                "verdict": ("HARD_PASS" if (ok and arms_distinct) else "HARD_FAIL"),
                "verdict_msg": ("SELFTEST_PASS substrate=%.3f random=%.3f static=%.3f arms_distinct=%s"
                                if ok and arms_distinct
                                else "SELFTEST_FAIL substrate=%.3f random=%.3f static=%.3f arms_distinct=%s") % (
                    pt["substrate_recall"], pt["random_recall"],
                    pt["static_recall"], arms_distinct),
                "summary": "selftest seed=%d substrate=%.3f random=%.3f static=%.3f" % (
                    seed, pt["substrate_recall"], pt["random_recall"],
                    pt["static_recall"]),
                "elapsed_s": round(time.time() - started, 2),
                "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "run_mode": "self_test",
                "config_version": config_str,
                "_arms_hashes": hashes,
            }
            tmp = out_dir / "metrics.json.tmp"
            tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
            os.replace(str(tmp), str(out_dir / "metrics.json"))
            print("[selftest seed=%d] verdict=%s msg=%s" % (
                seed, res["verdict"], res["verdict_msg"]), flush=True)
            return 0 if res["verdict"] == "HARD_PASS" else 1
        except Exception as e:
            print("[selftest seed=%d] CRASH %s" % (seed, e), file=sys.stderr)
            traceback.print_exc()
            return 2

    # smoke or full
    if smoke:
        points_to_run = SMOKE_CORNERS
        n_scenes = N_SCENES_PER_POINT_SMOKE
        expected = 4
        mode = "smoke"
    else:
        points_to_run = _full_points()
        n_scenes = N_SCENES_PER_POINT_FULL
        expected = len(points_to_run)
        mode = "full"

    config_str = _hardening_config_str(seed, mode, expected)

    per_point: List[Dict] = []
    for tup in points_to_run:
        n_dim, grid, n_obj, move_freq = tup
        try:
            pt = eval_one_point(n_dim, grid, n_obj, move_freq, n_scenes, seed)
            per_point.append(pt)
            print("[seed=%d %s N=%d grid=%d n_obj=%d mf=%.2f] subst=%.3f rand=%.3f static=%.3f lift_static=%.3f" % (
                seed, mode, n_dim, grid, n_obj, move_freq,
                pt["substrate_recall"], pt["random_recall"],
                pt["static_recall"], pt["substrate_lift_over_static"]),
                  flush=True)
        except Exception as e:
            print("[POINT_CRASH seed=%d N=%d grid=%d n_obj=%d mf=%.2f] %s" % (
                seed, n_dim, grid, n_obj, move_freq, e), file=sys.stderr)
            traceback.print_exc()

    arms_distinct, hashes = arms_differ_check(per_point)
    if smoke:
        verdict, msg, extra = smoke_verdict(per_point, arms_distinct, hashes)
    else:
        verdict, msg, extra = compute_verdict(per_point, arms_distinct, hashes,
                                                  expected)

    summary_points = [
        {k: v for k, v in p.items()
         if not k.startswith("predictions_")}
        for p in per_point
    ]
    metrics = {
        "anchor_name": anchor,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": round(time.time() - started, 2),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": mode,
        "n_seeds": 1,
        "seed": seed,
        "config_version": config_str,
        "phase_map": summary_points,
        "extra": extra,
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[seed=%d %s] FINAL verdict=%s msg=%s elapsed=%.1fs" % (
        seed, mode, verdict, msg, time.time() - started), flush=True)
    return 0 if verdict in ("HARD_PASS", "MIDDLE_BAND") else 1
