"""Shared engine for substrate_parietal_movable_rebind_phase_diagram_v1.

CHUNKED across 3 seed siblings (seed_7 / seed_13 / seed_19). Each sibling
imports this module and calls run_one_seed(seed_int).

Pre-reg: preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md

Layer-1 phase diagram for parietal MOVABLE-rebind.

Sweep: grid in {4,8,16,32} x n_obj in {3,8,20,50} x move_freq in {0,0.2,0.5,0.8}
       = 4 x 4 x 4 = 64 points per seed.
Smoke: 4 corner points only (cardinality_ok=4).

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
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME_PREFIX = "substrate_parietal_movable_rebind_phase_diagram_v1"

# Pre-reg LOCKED bands
HP_MIN_FRAC_LIFT = 0.30        # >=30% of points show substrate_lift_over_static >= 0.30
HP_SATURATE = 0.90             # at least 1 saturate point
HP_CLIFF = 0.40                # at least 1 cliff point
HP_LIFT_OVER_STATIC = 0.30     # lift bar for a "good" point
META_AM_TOL = 0.02             # SUBSTRATE must beat RANDOM by >= this at EVERY point

# Substrate constants
N_DIM = 1024                   # CRLB-chosen; capacity-cliff in sweep range
N_HALF = N_DIM // 2            # complex half-width
POSITION_NOISE = 0.05          # fixed (chunking decision)

# Sweep grids (FULL).
# Extended n_objs to {8, 20, 50, 100, 200} based on empirical probe:
# at N_DIM=1024, cliff begins around n_obj=100 (recall ~0.5) and reaches floor at 200+.
# Plate analytic cap underestimates substrate capacity by ~2x at this N.
GRID_SIZES = [4, 8, 16, 32]
N_OBJS = [8, 20, 50, 100, 200]
MOVE_FREQS = [0.0, 0.2, 0.5, 0.8]

# Smoke corners (4 points; cardinality_ok=4)
# Must span saturate AND cliff at FULL N=1024 (DISCRIMINATOR-MUST-SURVIVE-SCALE).
# Empirical cliff at n_obj=200, grid>=16; saturate at n_obj<=50, mid-grid.
SMOKE_CORNERS = [
    (8, 8, 0.5),     # mid-load mid-rebind -> SUBSTRATE saturate; STATIC fails (rebind discriminator)
    (16, 20, 0.5),   # higher load + rebind -> strong discriminator expected
    (32, 200, 0.5),  # far-over-cap + rebind -> CLIFF (substrate~0.20-0.25)
    (4, 8, 0.0),     # low load no rebind: SUBSTRATE = STATIC = saturate (sanity baseline)
]

N_SCENES_PER_POINT_FULL = 20   # 20 scenes per point * 1 query/scene
N_SCENES_PER_POINT_SMOKE = 20  # same; smoke discriminator must survive scale

EXPECTED_ARMS = ["substrate_hrr", "random", "static_binding"]


def _hardening_config_str(seed: int, smoke: bool) -> str:
    return (
        "ANCHOR=%s_seed_%d,N=%d,grids=%s,n_objs=%s,move_freqs=%s,pos_noise=%.2f,"
        "n_scenes=%d,mode=%s,HP_frac=%.2f,HP_sat=%.2f,HP_cliff=%.2f,"
        "HP_lift_static=%.2f,META_AM_tol=%.2f,arms=%s,"
        "hardening=META_AC_CRLB+AE_smoke_gate+AF_arms_differ+AG_atomic_write+AH_main_guard+AM_no_trivial+AN_complete"
    ) % (
        ANCHOR_NAME_PREFIX, seed, N_DIM, GRID_SIZES, N_OBJS, MOVE_FREQS,
        POSITION_NOISE,
        (N_SCENES_PER_POINT_SMOKE if smoke else N_SCENES_PER_POINT_FULL),
        ("smoke" if smoke else "full"),
        HP_MIN_FRAC_LIFT, HP_SATURATE, HP_CLIFF, HP_LIFT_OVER_STATIC,
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
        # phase jitter
        jitter = g.normal(0.0, noise, size=(n_pos, n_half)).astype(np.float32)
        out = out * np.exp(1j * jitter).astype(np.complex64)
    out = out / (np.abs(out) + 1e-9)
    return out.astype(np.complex64)


# ---------------------- scene generation ----------------------

def make_scenes(n_scenes: int, n_obj: int, n_pos: int,
                  move_freq: float, g: np.random.Generator) -> List[Dict]:
    """Each scene = initial assignments + MOVE ops + query.

    Assignments: pick n_obj distinct positions from [0, n_pos).
    MOVE ops: floor(move_freq * n_obj) objects move to fresh distinct positions.
    Query: pick a random moved-target (if any moves) else random initial object;
           ask "what position is object_k at" (true = post-move position).
    """
    scenes: List[Dict] = []
    if n_obj > n_pos:
        n_obj_eff = n_pos
    else:
        n_obj_eff = n_obj
    for _ in range(n_scenes):
        initial = g.choice(n_pos, size=n_obj_eff, replace=False).tolist()
        obj_to_pos = {k: int(initial[k]) for k in range(n_obj_eff)}
        n_moves = int(np.floor(move_freq * n_obj_eff))
        moves: List[Tuple[int, int]] = []
        for _ in range(n_moves):
            # pick a random object to move
            obj_k = int(g.integers(n_obj_eff))
            avail = [p for p in range(n_pos)
                     if p not in obj_to_pos.values()]
            if not avail:
                break
            new_pos = int(g.choice(avail))
            moves.append((obj_k, new_pos))
            obj_to_pos[obj_k] = new_pos
        # query: pick a moved object if any, else any
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
        # Query: unbind role of query_obj; cleanup -> position codebook
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
        # initial bag
        parts = []
        cur_pos = {}
        for (k, pos) in sc["initial"]:
            parts.append(bind(role_atoms[k], positions[pos]))
            cur_pos[k] = pos
        bag = np.sum(np.stack(parts, axis=0), axis=0).astype(np.complex64)
        # apply moves
        for (obj_k, new_pos) in sc["moves"]:
            old_pos = cur_pos[obj_k]
            old_bind = bind(role_atoms[obj_k], positions[old_pos])
            new_bind = bind(role_atoms[obj_k], positions[new_pos])
            bag = bag - old_bind + new_bind
            cur_pos[obj_k] = new_pos
        # query
        q = unbind(bag, role_atoms[sc["query_obj"]])
        pred = cleanup_argmax(q, positions)
        preds.append(pred)
        if pred == sc["true_pos"]:
            correct += 1
    return {"recall": correct / max(1, len(scenes)),
            "n_queries": len(scenes), "predictions": preds}


# ---------------------- per-point evaluator ----------------------

def eval_one_point(grid: int, n_obj: int, move_freq: float,
                    n_scenes: int, seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed * 100003 + grid * 1009 + n_obj * 101
                              + int(move_freq * 1000))
    n_pos = grid * grid
    positions = make_grid_positions(g, N_HALF, grid, grid,
                                       k_scales=4, noise=POSITION_NOISE)
    # role atoms: ceil(n_obj) of them
    role_atoms = random_unit_phases(max(1, n_obj), N_HALF, g)
    scenes = make_scenes(n_scenes, n_obj, n_pos, move_freq, g)

    rand_res = run_arm_random(scenes, n_pos, g)
    static_res = run_arm_static_binding(scenes, positions, role_atoms)
    subst_res = run_arm_substrate_hrr(scenes, positions, role_atoms)

    return {
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


# ---------------------- verdict ----------------------

def compute_verdict(per_point: List[Dict],
                     arms_distinct: bool, hashes: Dict[str, str],
                     n_expected: int) -> Tuple[str, str, Dict[str, Any]]:
    cardinality_ok = (len(per_point) == n_expected)
    # META_RULE_AM: SUBSTRATE > RANDOM at every point
    am_breach = [(p["grid"], p["n_obj"], p["move_freq"])
                 for p in per_point
                 if p["substrate_recall"] < p["random_recall"] + META_AM_TOL]
    n_sat = sum(1 for p in per_point if p["substrate_recall"] >= HP_SATURATE)
    n_cliff = sum(1 for p in per_point if p["substrate_recall"] <= HP_CLIFF)
    n_strong_lift = sum(1 for p in per_point
                        if p["substrate_lift_over_static"] >= HP_LIFT_OVER_STATIC)
    frac_lift = n_strong_lift / max(1, len(per_point))

    # cliff point: smallest grid OR largest n_obj where substrate drops below 0.40
    cliff_point = None
    if n_cliff > 0:
        cliffs = [p for p in per_point if p["substrate_recall"] <= HP_CLIFF]
        # smallest grid OR largest n_obj
        cliff_point = min(cliffs, key=lambda p: (p["grid"], -p["n_obj"], -p["move_freq"]))
        cliff_summary = "grid=%d n_obj=%d move_freq=%.2f recall=%.3f" % (
            cliff_point["grid"], cliff_point["n_obj"],
            cliff_point["move_freq"], cliff_point["substrate_recall"])
    else:
        cliff_summary = "NO_CLIFF_OBSERVED"

    extra = {
        "cardinality_ok": cardinality_ok,
        "n_points": len(per_point),
        "n_expected": n_expected,
        "arms_distinct": arms_distinct,
        "arms_hashes": hashes,
        "META_AM_breaches": am_breach,
        "n_saturated": n_sat,
        "n_cliff": n_cliff,
        "n_strong_lift": n_strong_lift,
        "frac_strong_lift": frac_lift,
        "cliff_point_summary": cliff_summary,
    }
    if not cardinality_ok:
        return ("HARD_FAIL", "CARDINALITY_BREACH n=%d expected=%d" % (
            len(per_point), n_expected), extra)
    if not arms_distinct:
        return ("HARD_FAIL", "ARMS_NOT_DISTINCT hashes=%s" % hashes, extra)
    if am_breach:
        return ("HARD_FAIL", "META_AM_BREACH %d points SUBSTRATE<=RANDOM" % len(am_breach), extra)
    # HARD_PASS criteria
    if (frac_lift >= HP_MIN_FRAC_LIFT and n_sat >= 1 and n_cliff >= 1):
        return ("HARD_PASS",
                "HARD_PASS | frac_lift=%.2f n_sat=%d n_cliff=%d | cliff: %s" % (
                    frac_lift, n_sat, n_cliff, cliff_summary), extra)
    if n_sat >= 1 and n_cliff == 0:
        return ("HARD_FAIL",
                "ALL_SATURATE n_sat=%d/%d (discriminator did not survive scale)" % (
                    n_sat, len(per_point)), extra)
    if n_cliff == len(per_point):
        return ("HARD_FAIL",
                "ALL_CLIFF_BROKEN n_cliff=%d (cell broken)" % n_cliff, extra)
    return ("MIDDLE_BAND",
            "MB | frac_lift=%.2f n_sat=%d n_cliff=%d | cliff: %s" % (
                frac_lift, n_sat, n_cliff, cliff_summary), extra)


def smoke_verdict(per_point: List[Dict],
                    arms_distinct: bool, hashes: Dict[str, str]
                    ) -> Tuple[str, str, Dict[str, Any]]:
    """Smoke gate (4 corner points): per pre-reg."""
    cardinality_ok = (len(per_point) == 4)
    am_breach = [(p["grid"], p["n_obj"], p["move_freq"])
                 for p in per_point
                 if p["substrate_recall"] < p["random_recall"] + META_AM_TOL]
    n_sat = sum(1 for p in per_point if p["substrate_recall"] >= 0.90)
    n_fail = sum(1 for p in per_point if p["substrate_recall"] < 0.40)
    n_strong = sum(1 for p in per_point
                   if (p["substrate_recall"]
                       - max(p["random_recall"], p["static_recall"])) >= 0.20)
    extra = {
        "cardinality_ok": cardinality_ok, "n_points": len(per_point),
        "arms_distinct": arms_distinct, "arms_hashes": hashes,
        "META_AM_breaches": am_breach,
        "n_saturated": n_sat, "n_failed": n_fail,
        "n_strong_discriminator": n_strong,
    }
    if not cardinality_ok:
        return ("HARD_FAIL", "SMOKE_CARDINALITY_BREACH n=%d expected=4" % len(per_point), extra)
    if not arms_distinct:
        return ("HARD_FAIL", "SMOKE_ARMS_NOT_DISTINCT %s" % hashes, extra)
    if am_breach:
        return ("HARD_FAIL", "SMOKE_META_AM_BREACH %d points" % len(am_breach), extra)
    if n_strong < 2:
        return ("HARD_FAIL",
                "SMOKE_DISCRIMINATOR_WEAK n_strong=%d (<2 required)" % n_strong, extra)
    if n_sat < 1:
        return ("HARD_FAIL", "SMOKE_NO_SATURATION (need >=1 corner saturating)", extra)
    if n_fail < 1:
        return ("HARD_FAIL",
                "SMOKE_NO_CLIFF (need >=1 corner failing to prove discriminator survives at full N)", extra)
    return ("HARD_PASS",
            "SMOKE_PASS | n_sat=%d n_fail=%d n_strong=%d arms_distinct=%s" % (
                n_sat, n_fail, n_strong, arms_distinct), extra)


# ---------------------- top-level seed runner ----------------------

def run_one_seed(seed: int, smoke: bool = False,
                  self_test: bool = False) -> int:
    """Run all 64 (or 4 smoke) points for a single seed; write metrics.json.

    Returns exit code (0 ok, non-zero fail).
    """
    started = time.time()
    anchor = "%s_seed_%d" % (ANCHOR_NAME_PREFIX, seed)
    env_name = os.environ.get("HDLAB_EXP_NAME", anchor)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    config_str = _hardening_config_str(seed, smoke)

    # self-test: 1 corner only, tiny scenes, prove mechanism
    if self_test:
        try:
            pt = eval_one_point(grid=4, n_obj=3, move_freq=0.5,
                                  n_scenes=3, seed=seed)
            ok = (pt["substrate_recall"] > pt["random_recall"] + 0.05)
            # quick arm-differ check
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
        # FULL sweep: skip points where n_obj > n_pos (would clip to n_pos,
        # creating duplicate effective configs). 4*5*4 = 80 raw, filtered:
        # grid=4 (n_pos=16): n_obj in {8} only (skip 20,50,100,200) -> 1*4 = 4
        # grid=8 (n_pos=64): n_obj in {8,20,50} -> 3*4 = 12
        # grid=16 (n_pos=256): n_obj in {8,20,50,100,200} -> 5*4 = 20
        # grid=32 (n_pos=1024): n_obj in {8,20,50,100,200} -> 5*4 = 20
        # total = 4+12+20+20 = 56 points per seed
        points_to_run = [(g, n, mf) for g in GRID_SIZES
                         for n in N_OBJS for mf in MOVE_FREQS
                         if n <= g * g]
        n_scenes = N_SCENES_PER_POINT_FULL
        expected = len(points_to_run)
        mode = "full"

    per_point: List[Dict] = []
    for (grid, n_obj, move_freq) in points_to_run:
        try:
            pt = eval_one_point(grid, n_obj, move_freq, n_scenes, seed)
            per_point.append(pt)
            print("[seed=%d %s grid=%d n_obj=%d mf=%.2f] subst=%.3f rand=%.3f static=%.3f lift_static=%.3f" % (
                seed, mode, grid, n_obj, move_freq,
                pt["substrate_recall"], pt["random_recall"],
                pt["static_recall"], pt["substrate_lift_over_static"]),
                  flush=True)
        except Exception as e:
            print("[POINT_CRASH seed=%d grid=%d n_obj=%d mf=%.2f] %s" % (
                seed, grid, n_obj, move_freq, e), file=sys.stderr)
            traceback.print_exc()

    arms_distinct, hashes = arms_differ_check(per_point)
    if smoke:
        verdict, msg, extra = smoke_verdict(per_point, arms_distinct, hashes)
    else:
        verdict, msg, extra = compute_verdict(per_point, arms_distinct, hashes,
                                                  expected)

    # strip predictions before write (large) but keep summary
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
    # META_RULE_AG atomic write
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[seed=%d %s] FINAL verdict=%s msg=%s elapsed=%.1fs" % (
        seed, mode, verdict, msg, time.time() - started), flush=True)
    return 0 if verdict in ("HARD_PASS", "MIDDLE_BAND") else 1
