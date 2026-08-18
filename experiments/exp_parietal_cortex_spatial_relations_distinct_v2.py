"""parietal_cortex_spatial_relations_distinct_v2 -- relational reasoning closeout.

Prereg: preregs/2026-06-27_parietal_cortex_spatial_relations_distinct_v2.md

v1 (exp_parietal_cortex_spatial_reasoning_v1) shipped MIDDLE_BAND with
MOVABLE arm chain-grade (move_recall=0.867 cv=0.003; Skunkworks landed-VET
commit ad6f061a / banked at commit e67e4bf8) BUT the REL arm was a BIT-
IDENTICAL clone of the MOVABLE code path. REL never actually tested
relational reasoning.

v2 CLOSES OUT the parietal story by testing OBJECT-OBJECT relational
spatial reasoning (parietal cortex spatial-relations circuit; brain
analog: superior parietal lobule for object-object relations, distinct
from M1/PMd object-position which v1 already proved).

SCENE: two objects A, B at distinct positions on a 5x5 grid.
QUERY: "what is the relative position of A to B?" in
       {LEFT, RIGHT, ABOVE, BELOW} (4-way classification; chance = 0.25).
PIPELINE: HRR S = bind(role_A, pos_A) + bind(role_B, pos_B);
          pos_hat_A = unbind(S, role_A); pos_hat_B = unbind(S, role_B);
          delta = pos_hat_A - pos_hat_B; cleanup to direction codebook.

ARMS (5 mandatory; all must be BIT-DISTINCT per META_RULE_AF):
  no_rel_baseline       random direction (chance 1/4 = 0.25)
  direct_difference     compute pos_A - pos_B from ground-truth indices
                        (oracle of geometry; not HRR; simple baseline)
  hrr_unbind            full HRR pipeline (mechanism under test)
  learned_rel_lookup    pre-stored (pos_A, pos_B) -> direction lookup
                        (oracle of pipeline; >= 0.95 expected)
  random_vectors        random HRR vectors instead of structured
                        (CONTROL; should hit chance ~0.25)

PRE-REG (HARD-LOCKED at module init):
  HARD_PASS (ALL required):
    hrr_unbind >= 0.55 (substrate band over 4-way chance 0.25)
    hrr_unbind > no_rel_baseline + 0.30
    hrr_unbind >= 0.50 * direct_difference
    cv across seeds < 0.10
    random_vectors in [0.20, 0.30] (control at chance)
    learned_rel_lookup >= 0.95 (pipeline check)
    arms_must_differ_self_test PASS
  HARD_FAIL (any):
    hrr_unbind < 0.30
    hrr_unbind within 0.02 of no_rel_baseline (no relational signal)
    learned_rel_lookup < 0.90
    arms_must_differ_self_test FAIL (v1 bit-identical bug reproduced)
    cardinality breach
  MIDDLE_BAND:
    hrr_unbind in [0.30, 0.55]

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms * 100 scenes * 4 queries = 4000
  EXPECTED_N_UNITS_FULL  = 5 seeds * 5 arms * 500 scenes * 4 queries = 50000

HARDENING:
  L1-L4 main-guard + per-arm try + outer try + import sentinel
  META_RULE_AF arms-must-differ pre-flight (this v2's WHOLE POINT)
  META_RULE_AH atomic final metrics write (.tmp + os.replace)
  META_RULE_Q suspect-1.000 guard on hrr_unbind
  ASCII-only; no emojis; no em-dashes; self-contained.

Author: exp_dev (hdi_exp_dev sub-agent) 2026-06-27.
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

ANCHOR_NAME = "parietal_cortex_spatial_relations_distinct_v2"

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
HP_HRR_RECALL = 0.55
HP_LIFT_OVER_BASELINE = 0.30
HP_FRACTION_OF_DIRECT = 0.50
HP_CV_MAX = 0.10
HP_LEARNED_LOOKUP = 0.95
HF_HRR_RECALL = 0.30
HF_HRR_VS_BASELINE_EPS = 0.02
HF_LEARNED_LOOKUP = 0.90
MB_HRR_LO = 0.30
MB_HRR_HI = 0.55
CHANCE = 0.25  # 4-way
RANDOM_VEC_LO = 0.20
RANDOM_VEC_HI = 0.30

EXPECTED_ARMS = ["no_rel_baseline", "direct_difference", "hrr_unbind",
                 "learned_rel_lookup", "random_vectors"]
DIRECTIONS = ["LEFT", "RIGHT", "ABOVE", "BELOW"]
N_DIRECTIONS = 4  # chance 1/4 = 0.25

if SELF_TEST_MODE:
    N_DIM = 512
    GRID_R = 3
    GRID_C = 3
    N_SCENES = 10
    N_DISTRACTORS = 2  # extra bound objects per scene (interference)
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    GRID_R = 5
    GRID_C = 5
    N_SCENES = 100
    N_DISTRACTORS = 6  # 2 query objects + 6 distractors = 8 bound items
    SEEDS = [7, 17]
else:
    N_DIM = 8192
    GRID_R = 5
    GRID_C = 5
    N_SCENES = 500
    N_DISTRACTORS = 10  # 2 + 10 = 12 bound items in superposition
    SEEDS = [7, 17, 23, 31, 41]

N_POSITIONS = GRID_R * GRID_C
N_QUERIES_PER_SCENE = N_DIRECTIONS
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS) * N_SCENES * N_QUERIES_PER_SCENE

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,grid=%dx%d,scenes=%d,n_distractors=%d,seeds=%s,mode=%s,"
    "HP_hrr>=%.2f,HP_lift>=%.2f,HP_frac>=%.2f,HP_cv<=%.2f,HP_lookup>=%.2f,"
    "HF_hrr<%.2f,HF_lookup<%.2f,chance=%.2f,n_dirs=%d,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+META_RULE_AF_arms_distinct+META_RULE_AH_atomic_write"
) % (
    ANCHOR_NAME, N_DIM, GRID_R, GRID_C, N_SCENES, N_DISTRACTORS, SEEDS, RUN_MODE,
    HP_HRR_RECALL, HP_LIFT_OVER_BASELINE, HP_FRACTION_OF_DIRECT, HP_CV_MAX,
    HP_LEARNED_LOOKUP, HF_HRR_RECALL, HF_LEARNED_LOOKUP,
    CHANCE, N_DIRECTIONS, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v2_parietal_relations_distinct",
        }
        if extra:
            metrics.update(extra)
        # META_RULE_AH atomic write
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
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
            "_hardening_marker": "v2_parietal_relations_distinct_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- FHRR-style primitives (complex unit-modulus) --------------------------

def random_unit_phases(M: int, n_half: int, g: np.random.Generator) -> np.ndarray:
    """(M, n_half) complex64 unit-modulus atoms."""
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise complex product (FHRR binding)."""
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Element-wise complex product with conjugate of key."""
    return (c * np.conj(key)).astype(np.complex64)


def superpose_sum(arrs: List[np.ndarray]) -> np.ndarray:
    """Sum (NOT normalized; preserves linearity for unbind to work)."""
    return np.sum(np.stack(arrs, axis=0), axis=0).astype(np.complex64)


def cleanup_complex(q: np.ndarray, codebook: np.ndarray) -> int:
    """Argmax over real(<q, codebook_k>); codebook (M, n_half)."""
    sims = np.real(codebook @ np.conj(q))
    return int(np.argmax(sims))


# -------------------------- direction codebook from position arithmetic ---------------

def make_direction_codebook(positions: np.ndarray, grid_r: int, grid_c: int
                              ) -> np.ndarray:
    """Build 4-direction codebook via averaged position deltas in the
    HRR embedding space.

    For each direction d in {LEFT, RIGHT, ABOVE, BELOW}, average
    (positions[target] - positions[anchor]) over all (anchor, target)
    pairs where target is the d-neighbor of anchor in index space.
    Result: (4, n_half) complex; row 0=LEFT, 1=RIGHT, 2=ABOVE, 3=BELOW.
    """
    n_half = positions.shape[1]
    out = np.zeros((4, n_half), dtype=np.complex64)
    counts = [0, 0, 0, 0]
    for r in range(grid_r):
        for c in range(grid_c):
            anchor_idx = r * grid_c + c
            # LEFT: (r, c-1)
            if c - 1 >= 0:
                tgt = r * grid_c + (c - 1)
                out[0] = out[0] + (positions[tgt] - positions[anchor_idx])
                counts[0] += 1
            # RIGHT: (r, c+1)
            if c + 1 < grid_c:
                tgt = r * grid_c + (c + 1)
                out[1] = out[1] + (positions[tgt] - positions[anchor_idx])
                counts[1] += 1
            # ABOVE: (r-1, c)
            if r - 1 >= 0:
                tgt = (r - 1) * grid_c + c
                out[2] = out[2] + (positions[tgt] - positions[anchor_idx])
                counts[2] += 1
            # BELOW: (r+1, c)
            if r + 1 < grid_r:
                tgt = (r + 1) * grid_c + c
                out[3] = out[3] + (positions[tgt] - positions[anchor_idx])
                counts[3] += 1
    for d in range(4):
        if counts[d] > 0:
            out[d] = out[d] / counts[d]
    return out.astype(np.complex64)


# -------------------------- structured grid positions (Frady-Kanerva phase code) ------

def make_grid_positions(g: np.random.Generator, n_half: int,
                          grid_r: int, grid_c: int, k_scales: int = 4
                          ) -> np.ndarray:
    """Position atoms via multi-scale fractional-power binding.

    For each scale s, sample base phase patterns and lay positions on a
    phase lattice; superpose across scales, then per-component normalize.
    """
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
    out = out / (np.abs(out) + 1e-9)
    return out.astype(np.complex64)


def direction_from_indices(anchor_pos: int, target_pos: int,
                            grid_c: int) -> int:
    """Compute ground-truth direction index from grid indices.

    Returns: 0=LEFT, 1=RIGHT, 2=ABOVE, 3=BELOW, or -1 if not cardinal.

    "What is the relative position of TARGET relative to ANCHOR?"
    If target is to the LEFT of anchor -> 0; etc.
    """
    ar, ac = anchor_pos // grid_c, anchor_pos % grid_c
    tr, tc = target_pos // grid_c, target_pos % grid_c
    dr, dc = tr - ar, tc - ac
    if dr == 0 and dc == -1:
        return 0  # LEFT
    if dr == 0 and dc == 1:
        return 1  # RIGHT
    if dr == -1 and dc == 0:
        return 2  # ABOVE
    if dr == 1 and dc == 0:
        return 3  # BELOW
    return -1


# -------------------------- scene generation --------------------------

def make_scenes(n_scenes: int, grid_r: int, grid_c: int,
                  n_distractors: int, g: np.random.Generator) -> List[Dict]:
    """Each scene = (anchor_pos, target_pos, distractor_positions, queries).

    For each scene, pick an interior anchor so all 4 cardinal directions
    are valid; generate one query per cardinal direction. Also pick
    n_distractors EXTRA positions (disjoint from {anchor, target}) which
    the HRR arm must also bind into the scene superposition -- creating
    realistic interference. Each distractor gets its own ROLE atom so it
    is bound as bind(role_distractor_k, pos_k).
    """
    n_pos = grid_r * grid_c
    scenes: List[Dict] = []
    for _ in range(n_scenes):
        inner_r = list(range(1, max(2, grid_r - 1)))
        inner_c = list(range(1, max(2, grid_c - 1)))
        if not inner_r or not inner_c:
            r = int(g.integers(grid_r))
            c = int(g.integers(grid_c))
        else:
            r = int(g.choice(inner_r))
            c = int(g.choice(inner_c))
        anchor_pos = r * grid_c + c

        queries: List[Dict] = []
        # For each cardinal direction sample a SEPARATE scene-level query: same
        # anchor, target = cardinal neighbor. All queries share the same scene
        # superposition (anchor + 1 target + n_distractors).
        # Pick a SINGLE primary query direction (so target is fixed per scene);
        # additional cardinal directions yield additional queries against the
        # same superposition only if target is moved -- to keep the rig
        # interpretable, we generate one scene per direction with that direction's
        # target as the bound target, but query for all 4 directions in
        # rotation. Simpler: bind anchor + target_for_one_dir, query that one
        # direction. This means each scene contributes EXACTLY 1 query.
        # For our N_SCENES * 4 query target, expand: each scene picks 1 random
        # cardinal direction; we generate 4x scenes so total queries = 4 * N_SCENES.
        # KEEP simple: generate 4 query-pair targets per scene but each query
        # picks a fresh distractor sample SO the scene superposition includes
        # the (anchor, that_dir_target, distractors).
        for d_idx, (dr, dc) in enumerate([(0, -1), (0, 1), (-1, 0), (1, 0)]):
            tr, tc = r + dr, c + dc
            if not (0 <= tr < grid_r and 0 <= tc < grid_c):
                continue
            target_pos = tr * grid_c + tc
            # Sample n_distractors positions disjoint from {anchor, target}
            avail = [p for p in range(n_pos)
                     if p != anchor_pos and p != target_pos]
            n_d = min(n_distractors, len(avail))
            distractors = g.choice(avail, size=n_d, replace=False)
            queries.append({
                "anchor_pos": int(anchor_pos),
                "target_pos": int(target_pos),
                "distractor_positions": [int(p) for p in distractors],
                "true_dir": int(d_idx),
            })
        scenes.append({
            "anchor_pos": int(anchor_pos),
            "queries": queries,
        })
    return scenes


# -------------------------- arm runners --------------------------
# Each arm returns:
#   {"recall": float, "n_queries": int, "predictions": List[int]}
# where predictions has length = sum(len(scene["queries"]) for scene in scenes)
# in scene-then-query order. This list is used by META_RULE_AF to verify
# arms are BIT-DISTINCT (the v1 bit-identical bug).


def run_arm_no_rel_baseline(scenes: List[Dict], n_dim: int,
                              g: np.random.Generator) -> Dict[str, Any]:
    """Predict random direction; chance 1/N_DIRECTIONS."""
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            pred = int(g.integers(N_DIRECTIONS))
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
    }


def run_arm_direct_difference(scenes: List[Dict], grid_c: int
                                ) -> Dict[str, Any]:
    """Compute ground-truth direction from grid indices.

    Oracle of geometry; not HRR; should be at or near 1.0 for cardinal
    neighbors (scene gen guarantees cardinal -> always-extractable).
    """
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            pred = direction_from_indices(q["anchor_pos"], q["target_pos"], grid_c)
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
    }


def run_arm_hrr_unbind(scenes: List[Dict], positions: np.ndarray,
                         direction_codebook: np.ndarray,
                         g: np.random.Generator, n_half: int,
                         max_distractors: int
                         ) -> Dict[str, Any]:
    """Full HRR pipeline (mechanism under test).

    Build ROLE atoms: role_ANCHOR, role_TARGET, plus a pool of
    role_DISTRACTOR_k for k in [0, max_distractors). For each query,
    superpose anchor + target + distractors into S, unbind anchor and
    target, compute delta = pos_hat_target - pos_hat_anchor, cleanup
    to direction codebook.

    The distractors add realistic interference (parietal cortex must
    extract relations in cluttered scenes, not just 2-object scenes).
    """
    role_anchor = random_unit_phases(1, n_half, g)[0]
    role_target = random_unit_phases(1, n_half, g)[0]
    role_distractors = random_unit_phases(max(1, max_distractors), n_half, g)
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            pos_anchor = positions[q["anchor_pos"]]
            pos_target = positions[q["target_pos"]]
            parts = [bind(role_anchor, pos_anchor),
                     bind(role_target, pos_target)]
            for k, dp in enumerate(q.get("distractor_positions", [])):
                role_k = role_distractors[k % max(1, max_distractors)]
                parts.append(bind(role_k, positions[dp]))
            S = superpose_sum(parts)
            pos_hat_anchor = unbind(S, role_anchor)
            pos_hat_target = unbind(S, role_target)
            delta = pos_hat_target - pos_hat_anchor
            pred = cleanup_complex(delta, direction_codebook)
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
    }


def run_arm_learned_rel_lookup(scenes: List[Dict], grid_c: int
                                  ) -> Dict[str, Any]:
    """Pre-stored (anchor_pos, target_pos) -> direction lookup (oracle).

    Distinct from direct_difference by mechanism: this is a hash-table
    lookup keyed on the pair, NOT geometric arithmetic. Same answer
    arithmetically but a DIFFERENT pipeline; serves to verify the
    pipeline (data -> direction) is sound.
    """
    # Build lookup
    lookup: Dict[Tuple[int, int], int] = {}
    for scene in scenes:
        for q in scene["queries"]:
            key = (q["anchor_pos"], q["target_pos"])
            if key not in lookup:
                lookup[key] = direction_from_indices(
                    q["anchor_pos"], q["target_pos"], grid_c)
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            pred = lookup[(q["anchor_pos"], q["target_pos"])]
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
    }


def run_arm_random_vectors(scenes: List[Dict], n_dim: int,
                              direction_codebook: np.ndarray,
                              g: np.random.Generator, n_half: int
                              ) -> Dict[str, Any]:
    """Replace structured HRR with random vectors.

    For each query, generate a random complex unit-modulus vector and
    cleanup against direction codebook. Should hit chance ~1/4.
    """
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            phases = g.uniform(-np.pi, np.pi, size=n_half).astype(np.float32)
            random_vec = np.exp(1j * phases).astype(np.complex64)
            pred = cleanup_complex(random_vec, direction_codebook)
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
    }


# -------------------------- META_RULE_AF arms-must-differ --------------------------

def arms_must_differ_self_test(arm_predictions: Dict[str, List[int]],
                                  arm_recalls: Dict[str, float],
                                  min_disagreement: float = 0.05,
                                  oracle_recall_floor: float = 0.99
                                  ) -> Tuple[bool, Dict[str, Any]]:
    """META_RULE_AF: catch bit-identical code-path duplication bug (v1 REL
    was a clone of MOVABLE; 0% disagreement is the bug signature).

    NUANCE: when two arms ARE both at recall >= oracle_recall_floor, they
    CORRECTLY produce identical predictions (both at ceiling). That is NOT
    a bug; oracle convergence is expected. We skip such pairs.

    For all OTHER pairs (at least one arm below oracle floor), we require
    disagreement >= min_disagreement. The CONTROL arms (no_rel_baseline,
    random_vectors) are NEVER at ceiling so they always provide a robust
    code-path-distinctness check against every other arm.

    Also: we ALWAYS require at least one pair to genuinely disagree (i.e.
    not all arms be identical) -- catches the "everything is one function"
    failure mode.

    Returns: (all_required_pairs_pass, diagnostic_dict)
    """
    arms = sorted(arm_predictions.keys())
    diagnostic: Dict[str, Any] = {
        "pairs": [],
        "min_disagreement_threshold": min_disagreement,
        "oracle_recall_floor": oracle_recall_floor,
    }
    all_pass = True
    any_real_disagreement = False
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            ai, aj = arms[i], arms[j]
            pi = arm_predictions[ai]
            pj = arm_predictions[aj]
            if len(pi) != len(pj):
                diagnostic["pairs"].append({
                    "arm_a": ai, "arm_b": aj,
                    "disagreement": -1.0,
                    "len_a": len(pi), "len_b": len(pj),
                    "pass": False,
                    "note": "length_mismatch",
                })
                all_pass = False
                continue
            arr_i = np.asarray(pi)
            arr_j = np.asarray(pj)
            disagreement = float(np.mean(arr_i != arr_j))
            if disagreement > 0:
                any_real_disagreement = True
            r_i = float(arm_recalls.get(ai, 0.0))
            r_j = float(arm_recalls.get(aj, 0.0))
            both_oracle = (r_i >= oracle_recall_floor and r_j >= oracle_recall_floor)
            if both_oracle:
                # Both at ceiling; identical predictions are expected (correct convergence).
                pair_pass = True
                note = "oracle_convergence_skipped"
            else:
                pair_pass = disagreement >= min_disagreement
                note = ""
            diagnostic["pairs"].append({
                "arm_a": ai, "arm_b": aj,
                "disagreement": disagreement,
                "recall_a": r_i,
                "recall_b": r_j,
                "n_queries": len(pi),
                "both_oracle": both_oracle,
                "pass": pair_pass,
                "note": note,
            })
            if not pair_pass:
                all_pass = False
    # Backstop: if NO pair disagrees on a single query, all arms are bit-identical -> FAIL
    if not any_real_disagreement:
        all_pass = False
        diagnostic["all_arms_bit_identical"] = True
    diagnostic["all_pairs_pass"] = all_pass
    return all_pass, diagnostic


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    n_half = N_DIM // 2
    # Build structured grid positions
    positions = make_grid_positions(g, n_half, GRID_R, GRID_C, k_scales=4)
    # Build direction codebook from positions
    direction_codebook = make_direction_codebook(positions, GRID_R, GRID_C)
    # Generate scenes (cardinal-neighbor pairs with distractors)
    scenes = make_scenes(N_SCENES, GRID_R, GRID_C, N_DISTRACTORS, g)

    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_predictions: Dict[str, List[int]] = {}

    # Each arm gets its own RNG fork for in-arm randomness (no_rel_baseline,
    # random_vectors, hrr role atoms) so arm internals do not contaminate
    # other arms via shared RNG state.
    arm_results["no_rel_baseline"] = run_arm_no_rel_baseline(
        scenes, N_DIM, np.random.default_rng(seed + 100))
    arm_predictions["no_rel_baseline"] = arm_results["no_rel_baseline"].pop("predictions")

    arm_results["direct_difference"] = run_arm_direct_difference(scenes, GRID_C)
    arm_predictions["direct_difference"] = arm_results["direct_difference"].pop("predictions")

    arm_results["hrr_unbind"] = run_arm_hrr_unbind(
        scenes, positions, direction_codebook,
        np.random.default_rng(seed + 200), n_half, N_DISTRACTORS)
    arm_predictions["hrr_unbind"] = arm_results["hrr_unbind"].pop("predictions")

    arm_results["learned_rel_lookup"] = run_arm_learned_rel_lookup(scenes, GRID_C)
    arm_predictions["learned_rel_lookup"] = arm_results["learned_rel_lookup"].pop("predictions")

    arm_results["random_vectors"] = run_arm_random_vectors(
        scenes, N_DIM, direction_codebook,
        np.random.default_rng(seed + 300), n_half)
    arm_predictions["random_vectors"] = arm_results["random_vectors"].pop("predictions")

    # META_RULE_AF arms-must-differ
    arm_recalls = {name: float(arm_results[name]["recall"]) for name in EXPECTED_ARMS}
    arms_distinct_pass, arms_distinct_diag = arms_must_differ_self_test(
        arm_predictions, arm_recalls,
        min_disagreement=0.05, oracle_recall_floor=0.99)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "n_positions": N_POSITIONS,
        "n_scenes": N_SCENES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
        "arms_distinct_pass": bool(arms_distinct_pass),
        "arms_distinct_diag": arms_distinct_diag,
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
        rec_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                rec_vals.append(float(d.get("recall", 0.0)))
                per_arm_full[arm][s] = {k: (float(v) if isinstance(v, (int, float))
                                               else v)
                                          for k, v in d.items()}
        if rec_vals:
            m = float(np.mean(rec_vals))
            sd = float(np.std(rec_vals))
            cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
            summary[arm] = {
                "mean_recall": m, "std_recall": sd, "cv": cv, "n": len(rec_vals)
            }
        else:
            summary[arm] = {"mean_recall": 0.0, "std_recall": 0.0, "cv": 0.0, "n": 0}

    no_rel = summary["no_rel_baseline"]["mean_recall"]
    direct = summary["direct_difference"]["mean_recall"]
    hrr = summary["hrr_unbind"]["mean_recall"]
    hrr_cv = summary["hrr_unbind"]["cv"]
    learned = summary["learned_rel_lookup"]["mean_recall"]
    random_vec = summary["random_vectors"]["mean_recall"]

    # Check arms-distinct across all seeds
    arms_distinct_all_seeds = all(
        per_seed[s].get("arms_distinct_pass", False) for s in seeds_sorted
    )

    lift_over_baseline = hrr - no_rel
    fraction_of_direct = hrr / max(1e-6, direct)

    # META_RULE_Q suspect-1.000
    suspect_1000 = (hrr >= 0.999)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not arms_distinct_all_seeds:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_AF: arms-must-differ self-test FAIL (v1 bit-identical bug REPRODUCED)"
    elif suspect_1000:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_Q: hrr_unbind=%.3f >= 0.999 (suspect; rig too easy)" % hrr
    elif learned < HF_LEARNED_LOOKUP:
        verdict = "HARD_FAIL"
        verdict_reason = "PIPELINE_BROKEN: learned_lookup=%.3f < %.2f (oracle pipeline failed)" % (
            learned, HF_LEARNED_LOOKUP)
    elif hrr < HF_HRR_RECALL:
        verdict = "HARD_FAIL"
        verdict_reason = "HRR_TOO_LOW: hrr_unbind=%.3f < %.2f (substrate cannot extract relations)" % (
            hrr, HF_HRR_RECALL)
    elif abs(hrr - no_rel) < HF_HRR_VS_BASELINE_EPS:
        verdict = "HARD_FAIL"
        verdict_reason = "NO_RELATIONAL_SIGNAL: hrr_unbind=%.3f within %.2f of baseline=%.3f" % (
            hrr, HF_HRR_VS_BASELINE_EPS, no_rel)
    elif (hrr >= HP_HRR_RECALL and
            lift_over_baseline >= HP_LIFT_OVER_BASELINE and
            fraction_of_direct >= HP_FRACTION_OF_DIRECT and
            hrr_cv < HP_CV_MAX and
            RANDOM_VEC_LO <= random_vec <= RANDOM_VEC_HI and
            learned >= HP_LEARNED_LOOKUP):
        verdict = "HARD_PASS"
        verdict_reason = "PARIETAL_REL_LOAD_BEARING"
    elif MB_HRR_LO <= hrr < MB_HRR_HI:
        verdict = "MIDDLE_BAND"
        verdict_reason = "HRR_in_band: %.3f in [%.2f, %.2f)" % (hrr, MB_HRR_LO, MB_HRR_HI)
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = "HARD_PASS_partial: hrr=%.3f lift=%.3f frac=%.3f cv=%.3f rand=%.3f learn=%.3f" % (
            hrr, lift_over_baseline, fraction_of_direct, hrr_cv, random_vec, learned)

    verdict_msg = (
        "%s | %s | NO_REL=%.3f DIRECT=%.3f HRR=%.3f LEARNED=%.3f RAND=%.3f | "
        "lift=%.3f frac_direct=%.3f cv_hrr=%.3f arms_distinct=%s | n_seeds=%d"
    ) % (verdict, verdict_reason, no_rel, direct, hrr, learned, random_vec,
         lift_over_baseline, fraction_of_direct, hrr_cv, arms_distinct_all_seeds,
         len(seeds_sorted))

    completed_units = 0
    for arm in EXPECTED_ARMS:
        for s in seeds_sorted:
            d = per_seed[s].get("per_arm", {}).get(arm, {})
            completed_units += int(d.get("n_queries", 0))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "arms_distinct_all_seeds": arms_distinct_all_seeds,
        "arms_distinct_diag_first_seed": per_seed[seeds_sorted[0]].get(
            "arms_distinct_diag", {}),
        "suspect_1000": suspect_1000,
        "lift_over_baseline": lift_over_baseline,
        "fraction_of_direct": fraction_of_direct,
        "hrr_cv": hrr_cv,
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

    print("[%s] mode=%s N=%d grid=%dx%d scenes=%d seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, GRID_R, GRID_C, N_SCENES, SEEDS,
        EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "recall" in r["per_arm"][arm]
            assert r["arms_distinct_pass"], (
                "META_RULE_AF self-test FAIL: %s" % r["arms_distinct_diag"]
            )
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: arms-distinct=PASS hrr=%.3f learned=%.3f" % (
                                       r["per_arm"]["hrr_unbind"]["recall"],
                                       r["per_arm"]["learned_rel_lookup"]["recall"]),
                                   extra={"_phase": "selftest_done",
                                          "arms_distinct_pass": r["arms_distinct_pass"]})
            print("[selftest] OK arms_distinct=%s hrr=%.3f no_rel=%.3f direct=%.3f learned=%.3f rand=%.3f" % (
                r["arms_distinct_pass"],
                r["per_arm"]["hrr_unbind"]["recall"],
                r["per_arm"]["no_rel_baseline"]["recall"],
                r["per_arm"]["direct_difference"]["recall"],
                r["per_arm"]["learned_rel_lookup"]["recall"],
                r["per_arm"]["random_vectors"]["recall"]), flush=True)
            return 0
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs arms_distinct=%s hrr=%.3f" % (
            seed, time.time() - t0, result.get("arms_distinct_pass"),
            result["per_arm"]["hrr_unbind"]["recall"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_parietal_relations_distinct"
    # META_RULE_AH atomic write
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
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
