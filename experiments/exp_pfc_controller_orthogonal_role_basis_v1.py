"""pfc_controller_orthogonal_role_basis_v1 -- Battery 2 Barrier 1 RANK 3 drill (CPU).

Prereg: preregs/2026-06-27_pfc_controller_orthogonal_role_basis_v1.md
Drill: Gram-Schmidt orthogonalize role-basis against filler-basis at INIT (cheap single-init change).
Sister cell: exp_pfc_controller_softmax_margin_abstain_v2 (HARD_PASS, same regime).

MECHANISM: at init, the role atoms (operator-identity vectors) and the filler atoms
(entity codebook E) are independently random -> they share random alignment that leaks
during routing (cosine-based op-scoring mixes role-similarity with filler-similarity).
Gram-Schmidt projects role atoms ONTO the orthogonal complement of span(E) -> roles
are by-construction-orthogonal to fillers; routing becomes filler-content-invariant.

ARMS (3):
  ARM_SHARED_BASIS         baseline: roles + fillers from same random distribution (current)
  ARM_ORTHOGONAL_ROLE_BASIS    roles Gram-Schmidted against E at init (CHEAP single-init change)
  ARM_PARTITIONED_BASIS    sanity intermediate: roles drawn from a disjoint random subspace
                            (random partition; not GS-projected) -- tests whether the lift
                            comes from orthogonality vs from disjoint-subspace alone.

TASK: 4-hop heterogeneous query (per Battery 2 Barrier 1 spec). 4 operators; each operator
  is a learned (Hebbian) (subject, object) -> next mapping; chain depth 4.

PRE-REG BANDS (depth=4 is decision depth per drill):
  HARD_PASS:
    ORTHOGONAL_ROLE_BASIS lift over SHARED_BASIS >= +0.10 at depth=4
    AND cv across seeds < 0.10
    AND ORTHOGONAL > PARTITIONED by >= +0.03   (orthogonality matters above disjoint-subspace)
  MIDDLE_BAND: lift in [+0.05, +0.10) OR cv in [0.10, 0.20)
  HARD_FAIL: lift < +0.05 OR ORTHOGONAL <= SHARED_BASIS + 0.03 (mechanism null)

FAIR-BASELINE (META_RULE_AA): SHARED_BASIS uses same random-init dimension + same SAME number
  of role atoms (= N_OPERATORS); difference is ONLY the orthogonalization step. Identical readout.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 3 arms * 3 seeds * 2 depths(3,4) = 18
  EXPECTED_N_UNITS_FULL  = 3 arms * 5 seeds * 4 depths(3,4,6,8) = 60

HARDENING: L1-L4 + import-crash sentinel + main-guard (META_RULE_X).
ASCII-only; no emojis; self-contained (no hdlab/ imports beyond _seed_checkpoint).
Author: exp_dev 2026-06-27 (Battery 2 Barrier 1 RANK 3 drill).
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

ANCHOR_NAME = "pfc_controller_orthogonal_role_basis_v1"

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
HP_LIFT_OVER_SHARED = 0.10
HP_LIFT_OVER_PARTITIONED = 0.03
HP_CV_MAX = 0.10
MB_LIFT_LO = 0.05
MB_CV_HI = 0.20
HF_LIFT_LO = 0.05

EXPECTED_ARMS = ["shared_basis", "orthogonal_role_basis", "partitioned_basis"]

DECISION_DEPTH = 4

if SELF_TEST_MODE:
    N_DIM = 512
    N_OPERATORS = 4
    SEEDS = [7]
    HOP_DEPTHS = [3]
    N_TRIPLES_PER_OP = 30
    N_TEST_CHAINS = 10
elif RUN_MODE == "smoke":
    N_DIM = 4096
    N_OPERATORS = 4
    SEEDS = [7, 17, 23]
    HOP_DEPTHS = [3, 4]
    N_TRIPLES_PER_OP = 300
    N_TEST_CHAINS = 60
else:
    N_DIM = 8192
    N_OPERATORS = 4
    SEEDS = [7, 17, 23, 31, 41]
    HOP_DEPTHS = [3, 4, 6, 8]
    N_TRIPLES_PER_OP = 500
    N_TEST_CHAINS = 100

V_ENTITIES = max(200, N_TEST_CHAINS * max(HOP_DEPTHS) * 4)
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_OPS=%d,V=%d,seeds=%s,depths=%s,decision_depth=%d,"
    "n_train=%d,n_test=%d,mode=%s,"
    "HP_lift_shared>=%.2f,HP_lift_partitioned>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "FAIR=SAME_INIT_DIFFER_ONLY_BY_GRAM_SCHMIDT,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_OPERATORS, V_ENTITIES, SEEDS, HOP_DEPTHS, DECISION_DEPTH,
    N_TRIPLES_PER_OP, N_TEST_CHAINS, RUN_MODE,
    HP_LIFT_OVER_SHARED, HP_LIFT_OVER_PARTITIONED, HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_pfc_orthogonal_role_basis",
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
            "_hardening_marker": "v1_pfc_orthogonal_role_basis_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gram_schmidt_orthogonalize_against(R: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Project rows of R onto orthogonal complement of span(E).
    R: (n_roles, n_dim); E: (n_entities, n_dim). Returns (n_roles, n_dim) unit-norm.

    Method: per-row R[i] := R[i] - sum_j (R[i].E[j]) E[j] / ||E[j]||^2; then renormalize.
    For numerical stability we do batched: R - (R @ E^T) @ (E / ||E||^2 expanded).
    Since E rows are unit-norm bipolar, ||E[j]||^2 = 1 -> R := R - (R @ E^T) @ E.
    But E spans a high-d subspace and is not orthonormal -- use QR on E for proper projection.
    """
    # Get orthonormal basis for span(E) via QR
    # E.T is (n_dim, n_entities); we need column basis for E.T -> rows of E span
    # QR of E.T gives Q (n_dim, n_entities) orthonormal columns spanning row-space of E.
    Qe, _ = np.linalg.qr(E.T)   # Qe: (n_dim, min(n_dim, n_entities))
    # Projection of R[i] onto span(E) is R[i] @ Qe @ Qe^T
    proj = (R @ Qe) @ Qe.T
    R_perp = R - proj
    # Renormalize; guard zero (degenerate if R was in span(E))
    norms = np.linalg.norm(R_perp, axis=1, keepdims=True) + 1e-8
    return (R_perp / norms).astype(np.float32)


def make_partitioned_basis(n_roles: int, n_dim: int, g: np.random.Generator,
                            partition_frac: float = 0.5) -> np.ndarray:
    """Roles drawn from a disjoint random subspace: zero out the first half of dims;
    sample bipolar on the second half. Tests whether disjoint-subspace ALONE accounts
    for the orthogonal-basis effect (sanity intermediate)."""
    R = np.zeros((n_roles, n_dim), dtype=np.float32)
    split = int(n_dim * partition_frac)
    R[:, split:] = (g.integers(0, 2, size=(n_roles, n_dim - split)) * 2 - 1).astype(np.float32)
    R = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-8)
    return R


def hebbian_write(triples: List[Tuple[int, int]], E: np.ndarray, n_dim: int) -> np.ndarray:
    """W = sum_i E[s].T outer E[o] / n. Returns (n_dim, n_dim)."""
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    if not triples:
        return W
    arr = np.asarray(triples, dtype=np.int64)
    s_idx, o_idx = arr[:, 0], arr[:, 1]
    S = E[s_idx]
    O = E[o_idx]
    W = S.T @ O / float(n_dim)
    return W.astype(np.float32)


def cleanup_to_E(v: np.ndarray, E: np.ndarray) -> Tuple[int, np.ndarray]:
    vn = v / (np.linalg.norm(v) + 1e-8)
    sims = E @ vn
    idx = int(np.argmax(sims))
    return idx, E[idx]


def op_scores_with_roles(state: np.ndarray, W_ops: List[np.ndarray],
                          role_atoms: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Score each op by: cosine of (role[i] + state @ W_ops[i] / 2) projected on-manifold.

    The role atom contributes additive bias to the op-score. With shared basis, roles
    leak into filler-similarity (random alignment). With orthogonal roles, the role
    contribution is by-construction-decoupled from the filler subspace.
    """
    state_n = state / (np.linalg.norm(state) + 1e-8)
    scores = np.zeros(len(W_ops), dtype=np.float32)
    for i, W in enumerate(W_ops):
        # Op score = mixture of role-prior (state cosine to role atom) + content-fit
        role_cos = float(state_n @ role_atoms[i])
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        content_fit = float(np.max(E @ out_n))
        scores[i] = 0.5 * role_cos + 0.5 * content_fit
    return scores


def apply_W(state: np.ndarray, W_op: np.ndarray,
            E: np.ndarray) -> Tuple[int, np.ndarray]:
    out_raw = state @ W_op
    idx, out_clean = cleanup_to_E(out_raw, E)
    return idx, out_clean


# -------------------------- arms --------------------------

def run_arm_with_roles(W_ops: List[np.ndarray], role_atoms: np.ndarray,
                        E: np.ndarray,
                        test_chains: List[Tuple[int, List[int], int]],
                        depth: int) -> float:
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            scores = op_scores_with_roles(state, W_ops, role_atoms, E)
            op = int(np.argmax(scores))
            idx, state = apply_W(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


# -------------------------- per-seed runner --------------------------

def make_kb_and_chains(n_ops: int, V: int, n_train: int, n_test: int,
                        max_depth: int, g: np.random.Generator
                        ) -> Tuple[List[List[Tuple[int, int]]],
                                   List[Tuple[int, List[int], int]]]:
    per_op_triples: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_train):
        s = int(g.integers(0, V))
        o = int(g.integers(0, V))
        op = int(g.integers(0, n_ops))
        per_op_triples[op].append((s, o))

    test_chains: List[Tuple[int, List[int], int]] = []
    attempts = 0
    while len(test_chains) < n_test and attempts < n_test * 100:
        attempts += 1
        s = int(g.integers(0, V))
        cur = s
        op_seq: List[int] = []
        for _ in range(max_depth):
            op = int(g.integers(0, n_ops))
            candidates = [o for (ss, o) in per_op_triples[op] if ss == cur]
            if not candidates:
                new_o = int(g.integers(0, V))
                while new_o == cur:
                    new_o = int(g.integers(0, V))
                per_op_triples[op].append((cur, new_o))
                cur = new_o
            else:
                cur = candidates[0]
            op_seq.append(op)
        test_chains.append((s, op_seq, cur))
    return per_op_triples, test_chains


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(V_ENTITIES, N_DIM, g)
    max_d = max(HOP_DEPTHS)
    per_op, test_chains = make_kb_and_chains(
        N_OPERATORS, V_ENTITIES, N_TRIPLES_PER_OP, N_TEST_CHAINS, max_d, g)
    W_ops = [hebbian_write(per_op[i], E, N_DIM) for i in range(N_OPERATORS)]

    # SAME random init for shared_basis roles (the baseline)
    g_role = np.random.default_rng(seed * 7919)
    roles_shared = bipolar(N_OPERATORS, N_DIM, g_role)

    # Orthogonal: project roles_shared against E (deterministic from same seed)
    roles_orthogonal = gram_schmidt_orthogonalize_against(roles_shared.copy(), E)

    # Partitioned: roles from disjoint subspace (different generator for fairness)
    g_part = np.random.default_rng(seed * 7919 + 1)
    roles_partitioned = make_partitioned_basis(N_OPERATORS, N_DIM, g_part)

    # Diagnostic: report role-vs-E alignment for each variant
    def mean_abs_alignment(R, E_):
        return float(np.mean(np.abs(R @ E_.T)))

    align_shared = mean_abs_alignment(roles_shared, E)
    align_orth = mean_abs_alignment(roles_orthogonal, E)
    align_part = mean_abs_alignment(roles_partitioned, E)

    out: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    for depth in HOP_DEPTHS:
        out["shared_basis"][str(depth)] = run_arm_with_roles(
            W_ops, roles_shared, E, test_chains, depth)
        out["orthogonal_role_basis"][str(depth)] = run_arm_with_roles(
            W_ops, roles_orthogonal, E, test_chains, depth)
        out["partitioned_basis"][str(depth)] = run_arm_with_roles(
            W_ops, roles_partitioned, E, test_chains, depth)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_depth": out,
        "alignments": {
            "shared_mean_abs_align_with_E": align_shared,
            "orthogonal_mean_abs_align_with_E": align_orth,
            "partitioned_mean_abs_align_with_E": align_part,
        },
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)
    summary: Dict[str, Dict[str, Dict[str, float]]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}

    for arm in EXPECTED_ARMS:
        summary[arm] = {}
        per_arm_full[arm] = {}
        for depth in HOP_DEPTHS:
            d = str(depth)
            vals: List[float] = []
            per_arm_full[arm][d] = {}
            for s in seeds_sorted:
                body = per_seed[s]
                pad = body.get("per_arm_per_depth", {})
                v = pad.get(arm, {}).get(d)
                if v is not None:
                    vals.append(float(v))
                    per_arm_full[arm][d][s] = float(v)
            if vals:
                m = float(np.mean(vals))
                sd = float(np.std(vals)) if n_seeds > 1 else 0.0
                cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
                summary[arm][d] = {"mean": m, "std": sd, "cv": cv, "n": len(vals)}
            else:
                summary[arm][d] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    decision_depth = DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS)
    dd = str(decision_depth)

    orth_m = summary["orthogonal_role_basis"][dd]["mean"]
    orth_cv = summary["orthogonal_role_basis"][dd]["cv"]
    shared_m = summary["shared_basis"][dd]["mean"]
    part_m = summary["partitioned_basis"][dd]["mean"]

    lift_over_shared = orth_m - shared_m
    lift_over_partitioned = orth_m - part_m

    verdict = "MIDDLE_BAND"
    if (lift_over_shared >= HP_LIFT_OVER_SHARED and
            orth_cv < HP_CV_MAX and
            lift_over_partitioned >= HP_LIFT_OVER_PARTITIONED):
        verdict = "HARD_PASS"
    elif (lift_over_shared < HF_LIFT_LO or
            orth_cv >= MB_CV_HI):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | depth=%d | ORTH=%.3f SHARED=%.3f PART=%.3f | "
        "lift_shared=%.3f lift_part=%.3f cv=%.3f | n_seeds=%d"
    ) % (verdict, decision_depth, orth_m, shared_m, part_m,
         lift_over_shared, lift_over_partitioned, orth_cv, n_seeds)

    completed_units = n_seeds * len(HOP_DEPTHS) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "decision_depth": decision_depth,
        "lift_over_shared": lift_over_shared,
        "lift_over_partitioned": lift_over_partitioned,
        "orth_cv": orth_cv,
        "n_seeds_complete": n_seeds,
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
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "expected_depths": HOP_DEPTHS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V=%d seeds=%s depths=%s n_ops=%d expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, SEEDS, HOP_DEPTHS,
        N_OPERATORS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_depth" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_depth"]
            # Validate alignments: orthogonal should be lowest
            al = r["alignments"]
            assert al["orthogonal_mean_abs_align_with_E"] <= al["shared_mean_abs_align_with_E"] + 1e-3, (
                "orthogonal alignment %.4f should <= shared %.4f" % (
                    al["orthogonal_mean_abs_align_with_E"],
                    al["shared_mean_abs_align_with_E"]))
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm + alignment-monotonicity verified",
                                   extra={"_phase": "selftest_done",
                                          "alignments": al})
            print("[selftest] OK alignments=%s" % al, flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
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
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_pfc_orthogonal_role_basis"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
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
