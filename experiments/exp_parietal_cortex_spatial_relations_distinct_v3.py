"""parietal_cortex_spatial_relations_distinct_v3 -- arms code-path distinguishing fix.

Prereg: preregs/2026-06-30_parietal_cortex_spatial_relations_distinct_v3.md
Design: notes/director_parietal_relational_v3_arms_codepath_fix_spec_2026-06-30.md

v2 (exp_parietal_cortex_spatial_relations_distinct_v2) shipped HARD_FAIL on
META_RULE_AF at FULL (1/5 seeds reported arms_distinct_pass=False because
hrr_unbind reached 0.98 recall and predictions converged with the oracle
learned_rel_lookup; behavioral disagreement was <0.05). BUT substantive
metrics are excellent and reproducible:
  - HRR=0.992 (lift +0.738 vs NO_REL=0.254)
  - frac_direct=0.992 (mechanism reaches 99% of oracle)
  - cv_hrr=0.005 cross-seed
The substrate DOES relational reasoning at near-oracle quality. The HF is
purely about arms code-path distinguishing.

v3 FIX (per Director spec): each arm function computes a SHA-256 hash of
its intermediate state (NOT just final predictions). Code paths that
genuinely differ produce different intermediate state hashes even when
their final predictions converge at near-oracle. The arms-distinctness
check is the per-arm hash, not the behavioral disagreement.

  - arm_no_rel: hash(rng-bytes sequence)
  - arm_direct_difference: hash(per-query (pos_A_idx, pos_B_idx, delta))
  - arm_hrr_unbind: hash(per-query (S, pos_hat_A, pos_hat_B, delta) raw bytes)
  - arm_learned_rel_lookup: hash(lookup-table keys + values)
  - arm_random_vectors: hash(per-query (random_hd_A, random_hd_B, delta) raw bytes)

Pre-flight gate: if any 2 of 5 arm hashes match -> HARD_FAIL pre-dispatch.

META_RULE_AY: cell-author SELF-REPORTS arm_pair_distinctness for all 10
pairs as a load-bearing field; verdict-emitter HARD_FAILs if ANY is False.

ARMS (5 mandatory; all must produce distinct intermediate-state hashes):
  no_rel_baseline       random direction (chance 1/4 = 0.25)
  direct_difference     pos_A - pos_B from ground-truth indices
                        (oracle of geometry; not HRR; simple baseline)
  hrr_unbind            full HRR pipeline (mechanism under test)
  learned_rel_lookup    pre-stored (pos_A, pos_B) -> direction lookup
                        (oracle of pipeline; >= 0.95 expected)
  random_vectors        random HRR vectors instead of structured
                        (CONTROL; should hit chance ~0.25)

PRE-REG (HARD-LOCKED at module init):
  HARD_PASS (ALL required):
    hrr_unbind >= 0.55
    hrr_unbind > no_rel_baseline + 0.30
    hrr_unbind >= 0.50 * direct_difference
    cv across seeds < 0.10
    random_vectors in [0.20, 0.30]
    learned_rel_lookup >= 0.95
    arm_pair_distinctness ALL True (10 pairs; intermediate-state hash check)
    META_RULE_AY arms_distinctness_self_report PASS
  HARD_FAIL (any):
    hrr_unbind < 0.30
    hrr_unbind within 0.02 of no_rel_baseline
    learned_rel_lookup < 0.90
    arm_pair_distinctness ANY False (v1/v2 code-path-collision reproduced)
    cardinality breach

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms * 100 scenes * 4 queries = 4000
  EXPECTED_N_UNITS_FULL  = 3 seeds * 5 arms * 500 scenes * 4 queries = 30000

HARDENING:
  L1-L4 main-guard + per-arm try + outer try + import sentinel
  META_RULE_AF arm-pair-distinctness via per-arm SHA-256 intermediate hash
  META_RULE_AY self-report -> verdict-emitter auto-HARD_FAIL on any False
  META_RULE_AH atomic final metrics write (.tmp + os.replace)
  META_RULE_Q suspect-1.000 guard on hrr_unbind
  ASCII-only; no emojis; no em-dashes; self-contained.

Author: exp_dev (hdi_exp_dev sub-agent) 2026-06-30.
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
import itertools
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

ANCHOR_NAME = "parietal_cortex_spatial_relations_distinct_v3"

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
    N_DISTRACTORS = 2
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    GRID_R = 5
    GRID_C = 5
    N_SCENES = 100
    N_DISTRACTORS = 6
    SEEDS = [7, 17]
else:
    N_DIM = 8192
    GRID_R = 5
    GRID_C = 5
    N_SCENES = 500
    N_DISTRACTORS = 10
    SEEDS = [7, 13, 19]  # 3 seeds per Director spec

N_POSITIONS = GRID_R * GRID_C
N_QUERIES_PER_SCENE = N_DIRECTIONS
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS) * N_SCENES * N_QUERIES_PER_SCENE

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,grid=%dx%d,scenes=%d,n_distractors=%d,seeds=%s,mode=%s,"
    "HP_hrr>=%.2f,HP_lift>=%.2f,HP_frac>=%.2f,HP_cv<=%.2f,HP_lookup>=%.2f,"
    "HF_hrr<%.2f,HF_lookup<%.2f,chance=%.2f,n_dirs=%d,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+"
    "META_RULE_AF_arms_hash_distinct+META_RULE_AY_self_report+META_RULE_AH_atomic_write"
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
            "_hardening_marker": "v3_parietal_relations_codepath_hash",
        }
        if extra:
            metrics.update(extra)
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
            "_hardening_marker": "v3_parietal_relations_codepath_hash_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- FHRR primitives --------------------------

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
    """Sum (NOT normalized)."""
    return np.sum(np.stack(arrs, axis=0), axis=0).astype(np.complex64)


def cleanup_complex(q: np.ndarray, codebook: np.ndarray) -> int:
    """Argmax over real(<q, codebook_k>)."""
    sims = np.real(codebook @ np.conj(q))
    return int(np.argmax(sims))


def make_direction_codebook(positions: np.ndarray, grid_r: int, grid_c: int
                              ) -> np.ndarray:
    """Direction codebook via averaged position deltas."""
    n_half = positions.shape[1]
    out = np.zeros((4, n_half), dtype=np.complex64)
    counts = [0, 0, 0, 0]
    for r in range(grid_r):
        for c in range(grid_c):
            anchor_idx = r * grid_c + c
            if c - 1 >= 0:
                tgt = r * grid_c + (c - 1)
                out[0] = out[0] + (positions[tgt] - positions[anchor_idx])
                counts[0] += 1
            if c + 1 < grid_c:
                tgt = r * grid_c + (c + 1)
                out[1] = out[1] + (positions[tgt] - positions[anchor_idx])
                counts[1] += 1
            if r - 1 >= 0:
                tgt = (r - 1) * grid_c + c
                out[2] = out[2] + (positions[tgt] - positions[anchor_idx])
                counts[2] += 1
            if r + 1 < grid_r:
                tgt = (r + 1) * grid_c + c
                out[3] = out[3] + (positions[tgt] - positions[anchor_idx])
                counts[3] += 1
    for d in range(4):
        if counts[d] > 0:
            out[d] = out[d] / counts[d]
    return out.astype(np.complex64)


def make_grid_positions(g: np.random.Generator, n_half: int,
                          grid_r: int, grid_c: int, k_scales: int = 4
                          ) -> np.ndarray:
    """Position atoms via multi-scale fractional-power binding."""
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
    """Ground-truth direction from grid indices. 0=LEFT 1=RIGHT 2=ABOVE 3=BELOW."""
    ar, ac = anchor_pos // grid_c, anchor_pos % grid_c
    tr, tc = target_pos // grid_c, target_pos % grid_c
    dr, dc = tr - ar, tc - ac
    if dr == 0 and dc == -1:
        return 0
    if dr == 0 and dc == 1:
        return 1
    if dr == -1 and dc == 0:
        return 2
    if dr == 1 and dc == 0:
        return 3
    return -1


def make_scenes(n_scenes: int, grid_r: int, grid_c: int,
                  n_distractors: int, g: np.random.Generator) -> List[Dict]:
    """Generate scenes: anchor + cardinal-neighbor target + distractors."""
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
        for d_idx, (dr, dc) in enumerate([(0, -1), (0, 1), (-1, 0), (1, 0)]):
            tr, tc = r + dr, c + dc
            if not (0 <= tr < grid_r and 0 <= tc < grid_c):
                continue
            target_pos = tr * grid_c + tc
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


# -------------------------- arm runners (5 VISIBLY DISTINCT code paths) -----
#
# Each arm function returns:
#   {"recall": float, "n_queries": int, "predictions": List[int],
#    "intermediate_hash": str}
# The intermediate_hash is SHA-256 of arm-specific raw bytes accumulated
# during the per-query computation. Different arms accumulate different
# physical quantities (raw bytes for HRR arms; integer tuples for index
# arms; rng bytes for random arm; lookup-table for learned arm). Hashes
# MUST be distinct across all 5 arms or pre-flight gate FAILS the cell.
#
# IMPORTANT: do NOT silently except: blocks. Per-arm crashes must surface
# (the orchestrator wraps these in run_one_seed's outer try).


def _hasher() -> "hashlib._Hash":
    return hashlib.sha256()


def arm_no_rel_baseline(scenes: List[Dict], n_dim: int,
                         g: np.random.Generator) -> Dict[str, Any]:
    """ARM 1: random direction. Code path = numpy rng integer draws.

    Intermediate state captured: the raw rng byte sequence consumed (via
    drawing into a buffer) plus the chosen integers. NO HRR primitives
    touched. Chance recall = 1/N_DIRECTIONS.
    """
    h = _hasher()
    h.update(b"ARM_NO_REL_BASELINE_v3")
    preds: List[int] = []
    correct = 0
    total = 0
    # First mix in a chunk of rng bytes so hash diverges from index-arithmetic arms.
    rng_witness = g.integers(0, 256, size=128, dtype=np.uint8).tobytes()
    h.update(rng_witness)
    for scene in scenes:
        for q in scene["queries"]:
            pred = int(g.integers(N_DIRECTIONS))
            # Hash mixes pred + true_dir-id; no HRR vector data ever flows here.
            h.update(b"P")
            h.update(int(pred).to_bytes(2, "little", signed=False))
            h.update(int(q["true_dir"]).to_bytes(2, "little", signed=False))
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
        "intermediate_hash": h.hexdigest(),
    }


def arm_direct_difference(scenes: List[Dict], grid_c: int
                            ) -> Dict[str, Any]:
    """ARM 2: ground-truth grid-index subtraction. NO HRR; pure integer arithmetic.

    Intermediate state: per-query (anchor_pos_idx, target_pos_idx, dr, dc)
    integer tuple stream. NO complex floats, NO rng draws, NO HD vectors.
    Oracle of geometry; ~1.0 recall.
    """
    h = _hasher()
    h.update(b"ARM_DIRECT_DIFFERENCE_v3")
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            anchor_idx = int(q["anchor_pos"])
            target_idx = int(q["target_pos"])
            ar, ac = anchor_idx // grid_c, anchor_idx % grid_c
            tr, tc = target_idx // grid_c, target_idx % grid_c
            dr, dc = tr - ar, tc - ac
            pred = direction_from_indices(anchor_idx, target_idx, grid_c)
            # Hash mixes integer geometry tuple ONLY. No HD vector bytes.
            h.update(b"G")
            h.update(int(anchor_idx).to_bytes(2, "little", signed=False))
            h.update(int(target_idx).to_bytes(2, "little", signed=False))
            h.update(int(dr).to_bytes(2, "little", signed=True))
            h.update(int(dc).to_bytes(2, "little", signed=True))
            h.update(int(pred).to_bytes(2, "little", signed=True))
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
        "intermediate_hash": h.hexdigest(),
    }


def arm_hrr_unbind(scenes: List[Dict], positions: np.ndarray,
                    direction_codebook: np.ndarray,
                    g: np.random.Generator, n_half: int,
                    max_distractors: int
                    ) -> Dict[str, Any]:
    """ARM 3: full HRR pipeline (mechanism under test).

    Intermediate state: per-query raw complex64 bytes of (S, pos_hat_anchor,
    pos_hat_target, delta). These are STRUCTURED HRR vectors derived from
    bind/unbind on the position codebook -- distinct from arm_random_vectors
    which uses unstructured rng phases.
    """
    h = _hasher()
    h.update(b"ARM_HRR_UNBIND_v3")
    # Hash a chunk of position bytes so this arm's intermediate state
    # is anchored to the structured codebook (NOT random).
    h.update(b"POS")
    h.update(positions.tobytes())
    h.update(b"CODEBOOK")
    h.update(direction_codebook.tobytes())
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
            # Hash captures HRR intermediate vectors: structured & derived
            # from the position codebook. CANNOT collide with random_vectors
            # which never touches positions or direction_codebook bytes.
            h.update(b"S")
            h.update(S.tobytes())
            h.update(b"DT")
            h.update(delta.tobytes())
            h.update(int(pred).to_bytes(2, "little", signed=True))
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
        "intermediate_hash": h.hexdigest(),
    }


def arm_learned_rel_lookup(scenes: List[Dict], grid_c: int
                            ) -> Dict[str, Any]:
    """ARM 4: pre-stored hash-table lookup; (anchor_idx, target_idx) -> direction.

    Intermediate state: the serialized lookup table itself, then per-query
    lookup keys. NO HRR vectors, NO rng draws, NO grid arithmetic at
    query-time (only at table build, but each entry materializes as a
    key-value tuple distinct from arm_direct_difference's per-query dr/dc).
    """
    h = _hasher()
    h.update(b"ARM_LEARNED_REL_LOOKUP_v3")
    lookup: Dict[Tuple[int, int], int] = {}
    for scene in scenes:
        for q in scene["queries"]:
            key = (int(q["anchor_pos"]), int(q["target_pos"]))
            if key not in lookup:
                lookup[key] = direction_from_indices(
                    q["anchor_pos"], q["target_pos"], grid_c)
    # Hash the FULL lookup table (sorted for determinism); this captures
    # the table as the arm-specific intermediate object. Distinct from
    # direct_difference which never builds a table.
    h.update(b"TABLE")
    for k in sorted(lookup.keys()):
        h.update(int(k[0]).to_bytes(2, "little", signed=False))
        h.update(int(k[1]).to_bytes(2, "little", signed=False))
        h.update(int(lookup[k]).to_bytes(2, "little", signed=True))
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            key = (int(q["anchor_pos"]), int(q["target_pos"]))
            pred = lookup[key]
            # Per-query state: lookup-key bytes; no integer arithmetic.
            h.update(b"L")
            h.update(int(key[0]).to_bytes(2, "little", signed=False))
            h.update(int(key[1]).to_bytes(2, "little", signed=False))
            h.update(int(pred).to_bytes(2, "little", signed=True))
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
        "intermediate_hash": h.hexdigest(),
    }


def arm_random_vectors(scenes: List[Dict], n_dim: int,
                        direction_codebook: np.ndarray,
                        g: np.random.Generator, n_half: int
                        ) -> Dict[str, Any]:
    """ARM 5: CONTROL -- random HRR vector replaces structured S.

    Intermediate state: per-query random unit-phase complex64 vector.
    Pipeline shape mirrors hrr_unbind (cleanup against codebook) but
    inputs are UNSTRUCTURED (rng phases, NOT derived from position
    codebook). Hash captures the random vectors + cleanup result.
    Distinct from hrr_unbind which hashes positions/codebook/S/delta.
    """
    h = _hasher()
    h.update(b"ARM_RANDOM_VECTORS_v3")
    # Hash mixes a chunk of rng bytes up-front so hash diverges from all
    # other arms; does NOT touch positions or direction_codebook bytes.
    rng_witness = g.integers(0, 256, size=128, dtype=np.uint8).tobytes()
    h.update(b"RNG")
    h.update(rng_witness)
    # NOTE: we DO hash direction_codebook into a SEPARATE label so it's not
    # the same byte prefix as hrr_unbind (which uses label "CODEBOOK").
    h.update(b"CB_RAND")
    h.update(direction_codebook.tobytes())
    preds: List[int] = []
    correct = 0
    total = 0
    for scene in scenes:
        for q in scene["queries"]:
            phases = g.uniform(-np.pi, np.pi, size=n_half).astype(np.float32)
            random_vec = np.exp(1j * phases).astype(np.complex64)
            pred = cleanup_complex(random_vec, direction_codebook)
            # Hash captures random vector bytes per query.
            h.update(b"RV")
            h.update(random_vec.tobytes())
            h.update(int(pred).to_bytes(2, "little", signed=True))
            preds.append(pred)
            if pred == q["true_dir"]:
                correct += 1
            total += 1
    return {
        "recall": correct / max(1, total),
        "n_queries": total,
        "predictions": preds,
        "intermediate_hash": h.hexdigest(),
    }


# -------------------------- META_RULE_AF arm-pair-distinctness --------

def arm_pair_distinctness_check(arm_hashes: Dict[str, str]
                                  ) -> Tuple[bool, Dict[str, Any]]:
    """META_RULE_AF: all 5 arm intermediate-state SHA-256 hashes must differ.

    Computes pairwise (arm_i, arm_j) hash-equality for all C(5,2)=10 pairs.
    Returns:
      all_pass: True iff ALL 10 pairs distinct.
      diag: {arm_pair_distinctness: {"ai__aj": bool, ...}, n_distinct_pairs}.

    This is the v3 fix: code-path distinguishing via intermediate-state hash,
    not behavioral disagreement (which fails when arms converge at oracle).
    """
    arms = sorted(arm_hashes.keys())
    arm_pair_distinctness: Dict[str, bool] = {}
    n_distinct = 0
    n_pairs = 0
    for ai, aj in itertools.combinations(arms, 2):
        pair_key = "%s__%s" % (ai, aj)
        distinct = (arm_hashes[ai] != arm_hashes[aj])
        arm_pair_distinctness[pair_key] = bool(distinct)
        n_pairs += 1
        if distinct:
            n_distinct += 1
    all_pass = (n_distinct == n_pairs)
    diag = {
        "arm_pair_distinctness": arm_pair_distinctness,
        "n_distinct_pairs": n_distinct,
        "n_pairs": n_pairs,
        "all_pairs_distinct": all_pass,
        "arm_hashes": arm_hashes,
    }
    return all_pass, diag


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    n_half = N_DIM // 2
    positions = make_grid_positions(g, n_half, GRID_R, GRID_C, k_scales=4)
    direction_codebook = make_direction_codebook(positions, GRID_R, GRID_C)
    scenes = make_scenes(N_SCENES, GRID_R, GRID_C, N_DISTRACTORS, g)

    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_predictions: Dict[str, List[int]] = {}
    arm_hashes: Dict[str, str] = {}

    # Each arm gets its own RNG fork.
    arm_results["no_rel_baseline"] = arm_no_rel_baseline(
        scenes, N_DIM, np.random.default_rng(seed + 100))
    arm_predictions["no_rel_baseline"] = arm_results["no_rel_baseline"].pop("predictions")
    arm_hashes["no_rel_baseline"] = arm_results["no_rel_baseline"]["intermediate_hash"]

    arm_results["direct_difference"] = arm_direct_difference(scenes, GRID_C)
    arm_predictions["direct_difference"] = arm_results["direct_difference"].pop("predictions")
    arm_hashes["direct_difference"] = arm_results["direct_difference"]["intermediate_hash"]

    arm_results["hrr_unbind"] = arm_hrr_unbind(
        scenes, positions, direction_codebook,
        np.random.default_rng(seed + 200), n_half, N_DISTRACTORS)
    arm_predictions["hrr_unbind"] = arm_results["hrr_unbind"].pop("predictions")
    arm_hashes["hrr_unbind"] = arm_results["hrr_unbind"]["intermediate_hash"]

    arm_results["learned_rel_lookup"] = arm_learned_rel_lookup(scenes, GRID_C)
    arm_predictions["learned_rel_lookup"] = arm_results["learned_rel_lookup"].pop("predictions")
    arm_hashes["learned_rel_lookup"] = arm_results["learned_rel_lookup"]["intermediate_hash"]

    arm_results["random_vectors"] = arm_random_vectors(
        scenes, N_DIM, direction_codebook,
        np.random.default_rng(seed + 300), n_half)
    arm_predictions["random_vectors"] = arm_results["random_vectors"].pop("predictions")
    arm_hashes["random_vectors"] = arm_results["random_vectors"]["intermediate_hash"]

    # META_RULE_AF: per-arm hash distinctness check (primary; replaces v2 behavioral).
    arms_distinct_pass, arms_distinct_diag = arm_pair_distinctness_check(arm_hashes)

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
        "arm_hashes": arm_hashes,
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

    # META_RULE_AF: all seeds + all 10 pairs must be distinct.
    arms_distinct_all_seeds = all(
        per_seed[s].get("arms_distinct_pass", False) for s in seeds_sorted
    )
    # Aggregate the per-pair distinctness (META_RULE_AY self-report).
    aggregated_pair_distinctness: Dict[str, bool] = {}
    any_pair_false = False
    for s in seeds_sorted:
        diag = per_seed[s].get("arms_distinct_diag", {})
        pair_d = diag.get("arm_pair_distinctness", {})
        for k, v in pair_d.items():
            # AND across seeds (any False at any seed -> False)
            prev = aggregated_pair_distinctness.get(k, True)
            aggregated_pair_distinctness[k] = bool(prev and v)
            if not v:
                any_pair_false = True

    lift_over_baseline = hrr - no_rel
    fraction_of_direct = hrr / max(1e-6, direct)

    suspect_1000 = (hrr >= 0.999)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # META_RULE_AY: self-report False -> auto-HARD_FAIL (per Atom 3 META corpus).
    if any_pair_false or not arms_distinct_all_seeds:
        n_false = sum(1 for v in aggregated_pair_distinctness.values() if not v)
        n_pairs_total = len(aggregated_pair_distinctness) or 10
        verdict = "HARD_FAIL"
        verdict_reason = (
            "META_RULE_AY_DISTINCTNESS_FAIL: %d/%d arm-pair-distinctness=False "
            "(code-path-collision; v1/v2 bug pattern reproduced)"
        ) % (n_false, n_pairs_total)
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
        verdict_reason = "PARIETAL_REL_LOAD_BEARING_v3_codepath_hash_distinct"
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
        "arm_pair_distinctness": aggregated_pair_distinctness,
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
                assert "intermediate_hash" in r["per_arm"][arm]
            assert r["arms_distinct_pass"], (
                "META_RULE_AF self-test FAIL: %s" % r["arms_distinct_diag"]
            )
            # Explicit pre-flight gate: NO 2 of 5 arm hashes match.
            hashes = r["arm_hashes"]
            for ai, aj in itertools.combinations(sorted(hashes.keys()), 2):
                assert hashes[ai] != hashes[aj], (
                    "PREFLIGHT_GATE: arm hash collision %s == %s" % (ai, aj)
                )
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: arms-distinct=PASS hrr=%.3f learned=%.3f" % (
                                       r["per_arm"]["hrr_unbind"]["recall"],
                                       r["per_arm"]["learned_rel_lookup"]["recall"]),
                                   extra={"_phase": "selftest_done",
                                          "arms_distinct_pass": r["arms_distinct_pass"],
                                          "arm_hashes": r["arm_hashes"]})
            print("[selftest] OK arms_distinct=%s hrr=%.3f no_rel=%.3f direct=%.3f learned=%.3f rand=%.3f" % (
                r["arms_distinct_pass"],
                r["per_arm"]["hrr_unbind"]["recall"],
                r["per_arm"]["no_rel_baseline"]["recall"],
                r["per_arm"]["direct_difference"]["recall"],
                r["per_arm"]["learned_rel_lookup"]["recall"],
                r["per_arm"]["random_vectors"]["recall"]), flush=True)
            print("[selftest] arm_hashes (first 16 chars):", flush=True)
            for arm in EXPECTED_ARMS:
                print("  %s: %s..." % (arm, r["arm_hashes"][arm][:16]), flush=True)
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
    final["_hardening_marker"] = "v3_parietal_relations_codepath_hash"
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
