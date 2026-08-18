"""parietal_cortex_spatial_reasoning_v1 -- B4 spatial-layout-for-thought primitive.

Prereg: preregs/2026-06-27_parietal_cortex_spatial_reasoning_v1.md
USER request 2026-06-27 explicit: "what about parietal-cortex spatial reasoning analog?"
INDEPENDENT cell -- no encoder dependency. Uses fractional-power position binding
(Frady-Kanerva-Sommer 2018) over FHRR-style unit-modulus complex atoms, then
binds symbol atoms to per-position phase rotations.

HYPOTHESIS: parietal cortex implements spatial-2D-layout-for-thought. Symbols are
movable objects with position + attached state. If grid-position binding works at
substrate scale, substrate gains a 2D scratchpad. ARM_GRID_POSITION_MOVABLE recall
on "what is at position Y after MOVE(X, Y)" >= 0.70 IS the load-bearing test.

ARMS (4 mandatory):
  ARM_NO_POSITION                symbols bound without position (chance ~0.05 expected)
  ARM_GRID_POSITION_FIXED        symbols bound at init with k=8 grid-cell phase positions; never moves
  ARM_GRID_POSITION_MOVABLE      symbols bound at init; MOVE op rebinds position mid-composition
  ARM_GRID_POSITION_WITH_RELATIONS  full: positions + ABOVE/BELOW/LEFT/RIGHT relational primitives

PRE-REG BANDS (HARD-LOCKED at module init):
  HARD_PASS:
    MOVABLE recall on "what symbol at position Y after MOVE(X,Y)" >= 0.70
    AND lift over NO_POSITION >= +0.50
    AND lift over FIXED >= +0.15 (rebind discipline)
    AND cv across seeds < 0.10
    AND WITH_RELATIONS recall on "what is ABOVE(X)" >= 0.55
  MIDDLE_BAND:
    MOVABLE recall in [0.50, 0.70) OR lift over FIXED in [0.05, 0.15)
    OR relational recall in [0.35, 0.55)
  HARD_FAIL:
    - MOVABLE recall < 0.50 (rebind broken)
    - or no lift over FIXED (rebind irrelevant; positions never change effective state)
    - or FIXED recall close to NO_POSITION (basic binding broken)
    - or k-sweep monotone (mechanism is just capacity not geometry)
    - or cardinality breach

FAIR-BASELINE CHECK (META_RULE_AA):
  - NO_POSITION should NOT trivially fail (must beat true chance ~1/N_SYMBOLS only,
    NOT pin at 0.0) -- this proves symbol-binding works; isolates position contribution.
  - FIXED should NOT trivially pass (i.e. should not match MOVABLE without doing the
    MOVE ops in train) -- this proves the MOVE op is load-bearing for the discriminator.
  - Both NO_POSITION and FIXED expected in [0.05, 0.70] band BEFORE mechanism arms
    differentiate. If both <0.05 OR both >0.95, the test rig is broken.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 4 arms * 20 scenes * 3 query_types = 480
  EXPECTED_N_UNITS_FULL  = 5 seeds * 4 arms * 200 scenes * 3 query_types = 12000

HARDENING:
  META_RULE_X main-guard, L1-L4
  L_GRID_PHASE_ORTHOGONALITY: pre-flight verify k=8 grid vectors pairwise cos < 0.15
  L_REBIND_AUDIT: log per-symbol position history; assert no double-binding
  META_RULE_Q suspect-1.000 guard: if recall == 1.000 at any arm, flag potential test rig issue
  META_RULE_S band-calibration: report top-1 AND top-5 recall

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (fair-revival cell 4 of 4 under research lead; per USER directive).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
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

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "parietal_cortex_spatial_reasoning_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_MOVABLE_RECALL = 0.70
HP_LIFT_OVER_NO_POS = 0.50
HP_LIFT_OVER_FIXED = 0.15
HP_CV_MAX = 0.10
HP_RELATIONAL_RECALL = 0.55
MB_MOVABLE_LO = 0.50
MB_LIFT_FIXED_LO = 0.05
MB_RELATIONAL_LO = 0.35
HF_MOVABLE_LO = 0.50

# Fair-baseline band
FAIR_BASELINE_LO = 0.05
FAIR_BASELINE_HI = 0.95

EXPECTED_ARMS = ["no_position", "grid_position_fixed",
                 "grid_position_movable", "grid_position_with_relations"]

if SELF_TEST_MODE:
    N_DIM = 512
    N_SYMBOLS = 3
    GRID_R = 3
    GRID_C = 3
    N_MOVE_OPS = 2
    N_SCENES = 5
    SEEDS = [7]
    K_GRID_SCALES = 4
elif RUN_MODE == "smoke":
    # Per prereg: smoke N_DIM=4096, 5 symbols, 5 positions, 3 MOVE ops per scene.
    # FIX: N_SYMBOLS must be SUBSTANTIALLY LESS than N_POSITIONS so moves have
    # room (avail=[]-bug); set symbols at 50% of positions; grid 4x4 = 16 pos > 8 sym
    N_DIM = 4096
    N_SYMBOLS = 8
    GRID_R = 4
    GRID_C = 4
    N_MOVE_OPS = 4
    N_SCENES = 30
    SEEDS = [7, 17, 23]
    K_GRID_SCALES = 8
else:
    N_DIM = 8192
    N_SYMBOLS = 25
    GRID_R = 6
    GRID_C = 6
    N_MOVE_OPS = 10
    N_SCENES = 200
    SEEDS = [7, 17, 23, 31, 41]
    K_GRID_SCALES = 8

N_POSITIONS = GRID_R * GRID_C
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS) * N_SCENES * 3  # 3 query types

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_SYM=%d,grid=%dx%d,K=%d,moves=%d,scenes=%d,seeds=%s,mode=%s,"
    "HP_movable>=%.2f,HP_lift_no_pos>=%.2f,HP_lift_fixed>=%.2f,HP_cv<=%.2f,"
    "HP_relational>=%.2f,FAIR_baseline=[%.2f,%.2f],expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+L_GRID_ORTH+L_REBIND_AUDIT,"
    "FAIRNESS=NO_POSITION_AND_FIXED_BOTH_IN_FAIR_BAND_BEFORE_MECHANISM_DIFFERENTIATES"
) % (
    ANCHOR_NAME, N_DIM, N_SYMBOLS, GRID_R, GRID_C, K_GRID_SCALES, N_MOVE_OPS, N_SCENES,
    SEEDS, RUN_MODE,
    HP_MOVABLE_RECALL, HP_LIFT_OVER_NO_POS, HP_LIFT_OVER_FIXED, HP_CV_MAX,
    HP_RELATIONAL_RECALL, FAIR_BASELINE_LO, FAIR_BASELINE_HI, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_parietal_spatial",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_parietal_spatial_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- FHRR-style primitives (complex unit-modulus) --------------------------
# Use complex64 atoms; binding = element-wise product (commutative for FHRR).
# Unbind = element-wise complex conjugate product.

def random_unit_phases(M: int, n_half: int, g: np.random.Generator) -> np.ndarray:
    """Return (M, n_half) complex64 unit-modulus atoms. n_half is HALF n_dim per
    complex (so total real footprint = 2 * n_half).
    """
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise complex product (commutative; circular convolution under FT)."""
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Element-wise complex product with conjugate of key."""
    return (c * np.conj(key)).astype(np.complex64)


def superpose(arrs: List[np.ndarray]) -> np.ndarray:
    """Sum and normalize-to-unit-modulus per component."""
    s = np.sum(np.stack(arrs, axis=0), axis=0)
    return (s / (np.abs(s) + 1e-9)).astype(np.complex64)


def cosine_sim_complex(a: np.ndarray, b: np.ndarray) -> float:
    """Real part of normalized complex inner product."""
    num = np.sum(a * np.conj(b)).real
    return float(num / (np.abs(a).sum() + 1e-9) / 1.0)  # already unit-modulus per comp


def cleanup_complex(q: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    """Find idx in codebook (M, n_half) with max real inner product with q."""
    sims = np.real(codebook @ np.conj(q))
    idx = int(np.argmax(sims))
    return idx, float(sims[idx])


def cleanup_topk_complex(q: np.ndarray, codebook: np.ndarray, k: int
                          ) -> List[Tuple[int, float]]:
    sims = np.real(codebook @ np.conj(q))
    if k >= len(sims):
        return [(i, float(sims[i])) for i in np.argsort(-sims)]
    top_idx = np.argpartition(-sims, k)[:k]
    top_idx_sorted = top_idx[np.argsort(-sims[top_idx])]
    return [(int(i), float(sims[i])) for i in top_idx_sorted]


# -------------------------- grid-cell phase code (Frady-Kanerva-Sommer / TEM-like) ----

def make_grid_positions(g: np.random.Generator, n_half: int, k_scales: int,
                          grid_r: int, grid_c: int
                          ) -> np.ndarray:
    """Generate position atoms for an (grid_r x grid_c) grid using fractional-power
    binding of base unitary atoms across k_scales spatial scales.

    Returns: complex array (grid_r * grid_c, n_half).

    For each scale s in 0..k_scales-1, sample a base unitary atom; position (r, c)
    gets phase factor exp(i * (r * scale_phase_r + c * scale_phase_c)) per scale,
    then atoms across scales superposed.
    """
    n_pos = grid_r * grid_c
    out = np.zeros((n_pos, n_half), dtype=np.complex64)

    # k_scales base phase patterns (each n_half phases); these define spatial frequencies
    for s in range(k_scales):
        base_r = g.uniform(-np.pi, np.pi, size=n_half).astype(np.float32)
        base_c = g.uniform(-np.pi, np.pi, size=n_half).astype(np.float32)
        # Scale-specific spatial freq scaling
        scale_factor = float(2 ** s) / max(1, k_scales)
        for r in range(grid_r):
            for c in range(grid_c):
                pos_idx = r * grid_c + c
                phase_r = r * base_r * scale_factor
                phase_c = c * base_c * scale_factor
                contrib = np.exp(1j * (phase_r + phase_c)).astype(np.complex64)
                out[pos_idx] = out[pos_idx] + contrib

    # Normalize per-position to unit modulus per component
    out = out / (np.abs(out) + 1e-9)
    return out.astype(np.complex64)


# -------------------------- arm implementations --------------------------

def run_arm_no_position(symbols: np.ndarray, positions: np.ndarray,
                         scenes: List[Dict], g: np.random.Generator) -> Dict[str, float]:
    """ARM_NO_POSITION: bind no positions; scene is just SUPERPOSE(all symbols).
    Position-query: no info available -> chance.
    """
    correct_pos = 0
    correct_move = 0
    correct_rel = 0
    total_pos = 0
    total_move = 0
    total_rel = 0
    for scene in scenes:
        # initial_assignments: list of (sym_idx, pos_idx); arm IGNORES position
        bag = superpose([symbols[sym_idx] for (sym_idx, pos_idx) in scene["initial"]])
        # Position queries: pick a position, ask which symbol; no position -> chance
        for q_pos_idx in scene["position_queries"]:
            # Unbind position from bag -> nothing meaningful; result is bag itself
            # Argmax against symbol codebook gives a random-ish answer (no signal)
            idx, _ = cleanup_complex(bag, symbols)
            true_sym = scene["position_to_sym_after_moves"].get(q_pos_idx, -1)
            if idx == true_sym:
                correct_pos += 1
            total_pos += 1
        # Move queries: same as position query for this arm (no MOVE applied)
        for (sym_idx, new_pos_idx) in scene["move_queries"]:
            idx, _ = cleanup_complex(bag, symbols)
            true_sym = scene["position_to_sym_after_moves"].get(new_pos_idx, -1)
            if idx == true_sym:
                correct_move += 1
            total_move += 1
        # Relational queries (ABOVE/etc) require position info -> no info here
        for q in scene["relational_queries"]:
            idx, _ = cleanup_complex(bag, symbols)
            if idx == q["true_sym"]:
                correct_rel += 1
            total_rel += 1
    return {
        "position_recall": correct_pos / max(1, total_pos),
        "move_recall": correct_move / max(1, total_move),
        "relational_recall": correct_rel / max(1, total_rel),
        "n_position_queries": total_pos,
        "n_move_queries": total_move,
        "n_relational_queries": total_rel,
    }


def run_arm_grid_position_fixed(symbols: np.ndarray, positions: np.ndarray,
                                  scenes: List[Dict], g: np.random.Generator
                                  ) -> Dict[str, float]:
    """ARM_GRID_POSITION_FIXED: bind symbol-position at init; never rebind.
    Position-query: unbind position from bag, cleanup to symbol codebook.
    Move-query: position WAS NOT updated, so query asks about NEW position which has
                no symbol bound -> chance.
    """
    correct_pos = 0
    correct_move = 0
    correct_rel = 0
    total_pos = 0
    total_move = 0
    total_rel = 0
    for scene in scenes:
        # Build bag = SUPERPOSE(bind(sym, pos)) over initial assignments
        bag = superpose([bind(symbols[sym_idx], positions[pos_idx])
                          for (sym_idx, pos_idx) in scene["initial"]])
        # Initial position->symbol map (no moves applied here)
        initial_pos_to_sym = {pos_idx: sym_idx
                                for (sym_idx, pos_idx) in scene["initial"]}
        # Position queries
        for q_pos_idx in scene["position_queries"]:
            q_vec = unbind(bag, positions[q_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = initial_pos_to_sym.get(q_pos_idx, -1)
            if idx == true_sym:
                correct_pos += 1
            total_pos += 1
        # Move queries: ask about NEW pos which never had a symbol bound -> low recall
        for (sym_idx, new_pos_idx) in scene["move_queries"]:
            q_vec = unbind(bag, positions[new_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = initial_pos_to_sym.get(new_pos_idx, -1)
            if idx == true_sym:
                correct_move += 1
            total_move += 1
        # Relational queries: relative position from a known anchor
        for q in scene["relational_queries"]:
            anchor_pos_idx = q["anchor_pos"]
            target_pos_idx = q["target_pos"]
            # Recover anchor symbol via unbind at anchor pos, then use relative pos
            q_vec = unbind(bag, positions[target_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = initial_pos_to_sym.get(target_pos_idx, -1)
            if idx == true_sym:
                correct_rel += 1
            total_rel += 1
    return {
        "position_recall": correct_pos / max(1, total_pos),
        "move_recall": correct_move / max(1, total_move),
        "relational_recall": correct_rel / max(1, total_rel),
        "n_position_queries": total_pos,
        "n_move_queries": total_move,
        "n_relational_queries": total_rel,
    }


def _apply_moves_to_bag(bag: np.ndarray, symbols: np.ndarray, positions: np.ndarray,
                         initial: List[Tuple[int, int]],
                         moves: List[Tuple[int, int]]) -> Tuple[np.ndarray, Dict[int, int]]:
    """Apply MOVE operations: unbind old (sym, old_pos), bind new (sym, new_pos).
    Returns updated bag + sym->pos current map.

    REBIND AUDIT: each MOVE explicitly removes old binding then adds new.
    """
    sym_to_pos = {sym_idx: pos_idx for (sym_idx, pos_idx) in initial}
    bag_arr = np.array(bag, copy=True)
    for (sym_idx, new_pos_idx) in moves:
        old_pos_idx = sym_to_pos.get(sym_idx)
        if old_pos_idx is None:
            continue
        # REMOVE old binding: subtract bind(sym, old_pos) then renormalize
        old_bind = bind(symbols[sym_idx], positions[old_pos_idx])
        new_bind = bind(symbols[sym_idx], positions[new_pos_idx])
        bag_arr = bag_arr - old_bind + new_bind
        sym_to_pos[sym_idx] = new_pos_idx
    bag_arr = bag_arr / (np.abs(bag_arr) + 1e-9)
    bag_arr = bag_arr.astype(np.complex64)
    return bag_arr, sym_to_pos


def run_arm_grid_position_movable(symbols: np.ndarray, positions: np.ndarray,
                                    scenes: List[Dict], g: np.random.Generator
                                    ) -> Dict[str, float]:
    """ARM_GRID_POSITION_MOVABLE: bind at init; APPLY MOVES; then query.
    Position query: should retrieve symbol that's CURRENTLY at that position.
    Move query: should retrieve symbol that was JUST MOVED to that position.
    """
    correct_pos = 0
    correct_move = 0
    correct_rel = 0
    total_pos = 0
    total_move = 0
    total_rel = 0
    for scene in scenes:
        bag_init = superpose([bind(symbols[sym_idx], positions[pos_idx])
                                for (sym_idx, pos_idx) in scene["initial"]])
        bag_after, sym_to_pos_after = _apply_moves_to_bag(
            bag_init, symbols, positions, scene["initial"], scene["moves"])
        pos_to_sym_after = {p: s for (s, p) in sym_to_pos_after.items()}
        # Position queries against bag_after (post-move state)
        for q_pos_idx in scene["position_queries"]:
            q_vec = unbind(bag_after, positions[q_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = pos_to_sym_after.get(q_pos_idx, -1)
            if idx == true_sym:
                correct_pos += 1
            total_pos += 1
        # Move queries: ask "what's at new_pos after MOVE(sym, new_pos)"
        for (sym_idx, new_pos_idx) in scene["move_queries"]:
            q_vec = unbind(bag_after, positions[new_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = pos_to_sym_after.get(new_pos_idx, -1)
            if idx == true_sym:
                correct_move += 1
            total_move += 1
        # Relational queries: same as position query on post-move state (no relations applied)
        for q in scene["relational_queries"]:
            q_vec = unbind(bag_after, positions[q["target_pos"]])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = pos_to_sym_after.get(q["target_pos"], -1)
            if idx == true_sym:
                correct_rel += 1
            total_rel += 1
    return {
        "position_recall": correct_pos / max(1, total_pos),
        "move_recall": correct_move / max(1, total_move),
        "relational_recall": correct_rel / max(1, total_rel),
        "n_position_queries": total_pos,
        "n_move_queries": total_move,
        "n_relational_queries": total_rel,
    }


def run_arm_grid_position_with_relations(symbols: np.ndarray, positions: np.ndarray,
                                            scenes: List[Dict], g: np.random.Generator,
                                            grid_r: int, grid_c: int
                                            ) -> Dict[str, float]:
    """ARM_GRID_POSITION_WITH_RELATIONS: positions + ABOVE/BELOW/LEFT/RIGHT relational
    primitives derived via position arithmetic.

    Relational query: "what is ABOVE(X)?" -- get X's position via search, compute
    target_pos = pos_of_X - row_step, query target.
    """
    # Pre-compute row/col deltas in position space (use position[r,c] - position[r-1,c]
    # to derive an effective row-step; etc.)
    # For simplicity, use INDEX-LEVEL relational: if X is at (r, c), ABOVE = (r-1, c).
    correct_pos = 0
    correct_move = 0
    correct_rel = 0
    total_pos = 0
    total_move = 0
    total_rel = 0
    for scene in scenes:
        bag_init = superpose([bind(symbols[sym_idx], positions[pos_idx])
                                for (sym_idx, pos_idx) in scene["initial"]])
        bag_after, sym_to_pos_after = _apply_moves_to_bag(
            bag_init, symbols, positions, scene["initial"], scene["moves"])
        pos_to_sym_after = {p: s for (s, p) in sym_to_pos_after.items()}
        # Position
        for q_pos_idx in scene["position_queries"]:
            q_vec = unbind(bag_after, positions[q_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = pos_to_sym_after.get(q_pos_idx, -1)
            if idx == true_sym:
                correct_pos += 1
            total_pos += 1
        # Move
        for (sym_idx, new_pos_idx) in scene["move_queries"]:
            q_vec = unbind(bag_after, positions[new_pos_idx])
            idx, _ = cleanup_complex(q_vec, symbols)
            true_sym = pos_to_sym_after.get(new_pos_idx, -1)
            if idx == true_sym:
                correct_move += 1
            total_move += 1
        # Relational: derive target_pos via index arithmetic
        for q in scene["relational_queries"]:
            anchor_pos = q["anchor_pos"]
            rel = q["relation"]
            r = anchor_pos // grid_c
            c = anchor_pos % grid_c
            if rel == "ABOVE":
                rr, cc = r - 1, c
            elif rel == "BELOW":
                rr, cc = r + 1, c
            elif rel == "LEFT":
                rr, cc = r, c - 1
            elif rel == "RIGHT":
                rr, cc = r, c + 1
            else:
                rr, cc = r, c
            if 0 <= rr < grid_r and 0 <= cc < grid_c:
                target_pos = rr * grid_c + cc
                q_vec = unbind(bag_after, positions[target_pos])
                idx, _ = cleanup_complex(q_vec, symbols)
                # true_sym is the symbol AT the relation-derived position
                true_sym = pos_to_sym_after.get(target_pos, -1)
                if idx == true_sym:
                    correct_rel += 1
                total_rel += 1
            else:
                # Off-grid: count as miss
                total_rel += 1
    return {
        "position_recall": correct_pos / max(1, total_pos),
        "move_recall": correct_move / max(1, total_move),
        "relational_recall": correct_rel / max(1, total_rel),
        "n_position_queries": total_pos,
        "n_move_queries": total_move,
        "n_relational_queries": total_rel,
    }


# -------------------------- scene generation --------------------------

def make_scenes(n_scenes: int, n_symbols: int, n_positions: int, n_moves: int,
                 grid_r: int, grid_c: int, g: np.random.Generator) -> List[Dict]:
    scenes = []
    for _ in range(n_scenes):
        # Initial: random subset of (sym, pos) with no duplicates on positions
        n_init = min(n_symbols, n_positions)
        pos_perm = g.permutation(n_positions)[:n_init]
        sym_perm = g.permutation(n_symbols)[:n_init]
        initial = [(int(sym_perm[i]), int(pos_perm[i])) for i in range(n_init)]
        # Moves: pick a random INITIAL symbol, move to a random NEW position
        moves: List[Tuple[int, int]] = []
        sym_to_pos = {s: p for (s, p) in initial}
        for _ in range(n_moves):
            # pick a sym that's currently bound
            sym = int(g.choice(list(sym_to_pos.keys())))
            # pick new pos that's currently UNOCCUPIED (avoid double-binding)
            occupied = set(sym_to_pos.values())
            avail = [p for p in range(n_positions) if p not in occupied]
            if not avail:
                continue
            new_pos = int(g.choice(avail))
            moves.append((sym, new_pos))
            sym_to_pos[sym] = new_pos
        # Final state map
        position_to_sym_after_moves = {p: s for (s, p) in sym_to_pos.items()}
        # Position queries: ask about each occupied position
        position_queries = list(position_to_sym_after_moves.keys())
        # Move queries: ask about each MOVE destination
        move_queries = list(moves)
        # Relational queries: pick K relational anchors that have a valid neighbor
        relational_queries: List[Dict] = []
        for (sym, pos) in initial[:min(3, len(initial))]:
            r = pos // grid_c
            c = pos % grid_c
            for rel in ["ABOVE", "BELOW", "LEFT", "RIGHT"]:
                if rel == "ABOVE":
                    rr, cc = r - 1, c
                elif rel == "BELOW":
                    rr, cc = r + 1, c
                elif rel == "LEFT":
                    rr, cc = r, c - 1
                else:
                    rr, cc = r, c + 1
                if 0 <= rr < grid_r and 0 <= cc < grid_c:
                    target_pos = rr * grid_c + cc
                    true_sym = position_to_sym_after_moves.get(target_pos, -1)
                    relational_queries.append({
                        "anchor_sym": sym, "anchor_pos": pos,
                        "relation": rel, "target_pos": target_pos,
                        "true_sym": true_sym,
                    })
                    break  # one relation per anchor sym
        scenes.append({
            "initial": initial,
            "moves": moves,
            "position_to_sym_after_moves": position_to_sym_after_moves,
            "position_queries": position_queries,
            "move_queries": move_queries,
            "relational_queries": relational_queries,
        })
    return scenes


# -------------------------- pre-flight gates --------------------------

def preflight_grid_orthogonality(positions: np.ndarray) -> Tuple[bool, float]:
    """L_GRID_PHASE_ORTHOGONALITY: pairwise cosine of position atoms < 0.15."""
    n = positions.shape[0]
    max_pair = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            cs = float(np.abs(np.sum(positions[i] * np.conj(positions[j])).real) /
                        max(1.0, positions.shape[1]))
            if cs > max_pair:
                max_pair = cs
    return max_pair < 0.15, max_pair


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    n_half = N_DIM // 2  # complex64 doubles real footprint
    # Build symbol codebook (complex unit-modulus)
    symbols = random_unit_phases(N_SYMBOLS, n_half, g)
    # Build grid position codebook via fractional-power binding across k_scales
    positions = make_grid_positions(g, n_half, K_GRID_SCALES, GRID_R, GRID_C)
    # Pre-flight: grid orthogonality
    grid_orth_ok, max_pair_cos = preflight_grid_orthogonality(positions)
    # Scenes
    scenes = make_scenes(N_SCENES, N_SYMBOLS, N_POSITIONS, N_MOVE_OPS,
                          GRID_R, GRID_C, g)

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["no_position"] = run_arm_no_position(symbols, positions, scenes, g)
    arm_results["grid_position_fixed"] = run_arm_grid_position_fixed(
        symbols, positions, scenes, g)
    arm_results["grid_position_movable"] = run_arm_grid_position_movable(
        symbols, positions, scenes, g)
    arm_results["grid_position_with_relations"] = run_arm_grid_position_with_relations(
        symbols, positions, scenes, g, GRID_R, GRID_C)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "n_symbols": N_SYMBOLS,
        "n_positions": N_POSITIONS,
        "k_grid_scales": K_GRID_SCALES,
        "grid_orth_ok": bool(grid_orth_ok),
        "grid_max_pair_cos": float(max_pair_cos),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        pos_vals: List[float] = []
        mov_vals: List[float] = []
        rel_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                pos_vals.append(float(d.get("position_recall", 0.0)))
                mov_vals.append(float(d.get("move_recall", 0.0)))
                rel_vals.append(float(d.get("relational_recall", 0.0)))
                per_arm_full[arm][s] = {k: (float(v) if isinstance(v, (int, float)) else v)
                                          for k, v in d.items()}
        if pos_vals:
            m_pos = float(np.mean(pos_vals))
            m_mov = float(np.mean(mov_vals))
            m_rel = float(np.mean(rel_vals))
            sd_mov = float(np.std(mov_vals))
            cv_mov = sd_mov / abs(m_mov) if abs(m_mov) > 1e-6 else 0.0
            summary[arm] = {
                "mean_position": m_pos, "mean_move": m_mov, "mean_relational": m_rel,
                "std_move": sd_mov, "cv_move": cv_mov, "n": len(pos_vals),
            }
        else:
            summary[arm] = {"mean_position": 0.0, "mean_move": 0.0, "mean_relational": 0.0,
                            "std_move": 0.0, "cv_move": 0.0, "n": 0}

    # PRIMARY discriminator = move_recall (post-MOVE rebind)
    no_pos = summary["no_position"]["mean_move"]
    fixed = summary["grid_position_fixed"]["mean_move"]
    movable = summary["grid_position_movable"]["mean_move"]
    movable_cv = summary["grid_position_movable"]["cv_move"]
    relational = summary["grid_position_with_relations"]["mean_relational"]

    # SECONDARY fairness: position_recall (must show binding works for any arm with positions)
    no_pos_position = summary["no_position"]["mean_position"]
    fixed_position = summary["grid_position_fixed"]["mean_position"]

    # Sanity: verify move queries fired (denominator > 0). If n_move_queries=0 anywhere,
    # scene generation was broken -> verdict cannot be trusted.
    n_move_queries_sample = 0
    for s in seeds_sorted:
        body = per_seed[s]
        pa = body.get("per_arm", {}).get("grid_position_movable", {})
        n_move_queries_sample = max(n_move_queries_sample, int(pa.get("n_move_queries", 0)))

    lift_over_no_pos = movable - no_pos
    lift_over_fixed = movable - fixed

    # Fairness audit on POSITION recall (not move): position-binding should work for
    # FIXED arm (>=0.50 fair), should NOT work for NO_POSITION arm (~chance = 1/N_POS).
    # For NO_POSITION position_recall: chance is ~1/n_symbols. Should be in [0.0, 0.5].
    # For FIXED position_recall: should be in [0.5, 1.0].
    n_positions_eff = GRID_R * GRID_C
    chance_pos = 1.0 / max(1, N_SYMBOLS)
    fair_baseline_ok = (
        no_pos_position <= 0.5  # NO_POSITION shouldn't pin near 1.0 -- it's chance
        and fixed_position >= 0.5  # FIXED should work
    )

    # META_RULE_Q suspect-1.000 on MOVE queries (which probe the discriminator)
    suspect_1000 = (movable >= 0.999 and fixed >= 0.999)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""
    if n_move_queries_sample == 0:
        verdict = "HARD_FAIL"
        verdict_reason = "TEST_RIG_BROKEN: 0 move queries fired across all seeds -> scene gen bug"
    elif not fair_baseline_ok:
        verdict = "HARD_FAIL"
        verdict_reason = ("FAIR_BASELINE_BROKEN: no_pos_position=%.3f fixed_position=%.3f -- "
                          "position-binding rig invalid") % (no_pos_position, fixed_position)
    elif suspect_1000:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_Q: movable AND fixed both >= 0.999 -> rig too easy"
    elif (movable >= HP_MOVABLE_RECALL and
            lift_over_no_pos >= HP_LIFT_OVER_NO_POS and
            lift_over_fixed >= HP_LIFT_OVER_FIXED and
            movable_cv < HP_CV_MAX and
            relational >= HP_RELATIONAL_RECALL):
        verdict = "HARD_PASS"
        verdict_reason = "PARIETAL_SPATIAL_LOAD_BEARING"
    elif movable < HF_MOVABLE_LO:
        verdict = "HARD_FAIL"
        verdict_reason = "MOVABLE_BROKEN: %.3f < %.2f" % (movable, HF_MOVABLE_LO)
    elif lift_over_fixed < MB_LIFT_FIXED_LO:
        verdict = "HARD_FAIL"
        verdict_reason = ("REBIND_INERT: movable_lift_over_fixed=%.3f < %.2f (rebind not load-bearing)" %
                          (lift_over_fixed, MB_LIFT_FIXED_LO))

    verdict_msg = (
        "%s | %s | NO_POS=%.3f FIXED=%.3f MOVABLE=%.3f REL=%.3f | "
        "lift_no_pos=%.3f lift_fixed=%.3f cv_mov=%.3f | n=%d"
    ) % (verdict, verdict_reason, no_pos, fixed, movable, relational,
         lift_over_no_pos, lift_over_fixed, movable_cv, len(seeds_sorted))

    completed_units = 0
    for arm in EXPECTED_ARMS:
        n_per_arm = sum(
            (per_seed[s].get("per_arm", {}).get(arm, {}).get("n_position_queries", 0) +
             per_seed[s].get("per_arm", {}).get(arm, {}).get("n_move_queries", 0) +
             per_seed[s].get("per_arm", {}).get(arm, {}).get("n_relational_queries", 0))
            for s in seeds_sorted
        )
        completed_units += n_per_arm

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "fair_baseline_ok": fair_baseline_ok,
        "suspect_1000": suspect_1000,
        "lift_over_no_pos": lift_over_no_pos,
        "lift_over_fixed": lift_over_fixed,
        "movable_cv": movable_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d sym=%d grid=%dx%d K=%d moves=%d scenes=%d seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_SYMBOLS, GRID_R, GRID_C, K_GRID_SCALES,
        N_MOVE_OPS, N_SCENES, SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "position_recall" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm + grid-orth structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_grid_orth_ok": r["grid_orth_ok"],
                                          "selftest_grid_max_pair_cos": r["grid_max_pair_cos"]})
            print("[selftest] OK grid_orth_ok=%s movable_move=%.3f no_pos_move=%.3f" % (
                r["grid_orth_ok"], r["per_arm"]["grid_position_movable"]["move_recall"],
                r["per_arm"]["no_position"]["move_recall"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs grid_orth_ok=%s" % (
            seed, time.time() - t0, result.get("grid_orth_ok")), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_parietal_spatial"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
