"""substrate_preplay_beam_to_goal_v1 -- hippocampal preplay analog at K=64 substrate-scale.

Tests: substrate runs K parallel forward rollouts to a goal; picks best by cos(leaf, goal).
On 4-block BlocksWorld synthetic STRIPS domain, K=64 beats K=4 by >= 0.10 (substrate-better-than-brain
proof), beats greedy-1step by >= 0.25, achieves >= 0.70 solve rate.

ARMS (5):
  ARM_GREEDY_1STEP                  no lookahead; Q&A baseline
  ARM_PREPLAY_K4                    Cowan-4 brain-scale; D=6
  ARM_PREPLAY_K64                   substrate-scale K=64; D=6
  ARM_PREPLAY_K64_WITH_GOAL_GATE    K=64 with bind(state, goal) action gating
  ARM_RANDOM_CONTROL                random action sequences; sanity floor

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  K64 solve_rate >= 0.70 AND K64 - GREEDY >= 0.25 AND
              K64 - K4 >= 0.10 AND K64_GOAL_GATE closes >= 50% gap to oracle (1.0) AND
              median plan_len <= 2x optimal AND RANDOM_CONTROL <= 0.15
  MIDDLE_BAND: K64 in [0.50, 0.70) AND K64 - GREEDY >= 0.15 OR K64 - K4 in [0.05, 0.10]
  HARD_FAIL:  K64 solve_rate <= 0.30 OR K64 - K4 < 0.05 OR RANDOM_CONTROL > 0.30

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 arms * 3 seeds * 100 goals = 1500
  EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 20  goals = 200

ASCII-only; self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M, Wave 3B TOP-2)
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
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_preplay_beam_to_goal_v1"

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
HP_SOLVE_MIN = 0.70
HP_OVER_GREEDY_MIN = 0.25
HP_K64_OVER_K4_MIN = 0.10
HP_GOAL_GATE_GAP_CLOSE = 0.50
HP_PLAN_LEN_RATIO_MAX = 2.0
HP_RANDOM_MAX = 0.15
MB_SOLVE_LO = 0.50
HF_SOLVE_LO = 0.30
HF_K64_OVER_K4_LO = 0.05
HF_RANDOM_HI = 0.30

EXPECTED_ARMS = [
    "greedy_1step", "preplay_k4", "preplay_k64",
    "preplay_k64_with_goal_gate", "random_control",
]

# BlocksWorld 4-block synthetic
N_BLOCKS = 4
ACTIONS = ["pick_up", "put_down", "stack", "unstack", "move_aside", "swap"]
N_ACTIONS = len(ACTIONS)

if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    N_GOALS = 6
    K_BEAM = {"k4": 4, "k64": 8}  # smaller in selftest
    DEPTH = 4
elif RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7, 17]
    N_GOALS = 20
    K_BEAM = {"k4": 4, "k64": 64}
    DEPTH = 6
else:
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    N_GOALS = 100
    K_BEAM = {"k4": 4, "k64": 64}
    DEPTH = 6

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_GOALS

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,blocks=%d,actions=%d,goals=%d,depth=%d,K=%s,seeds=%s,mode=%s,"
    "HP_solve>=%.2f,HP_K64-K4>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_BLOCKS, N_ACTIONS, N_GOALS, DEPTH, K_BEAM,
    SEEDS, RUN_MODE, HP_SOLVE_MIN, HP_K64_OVER_K4_MIN, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_substrate_preplay_beam",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_substrate_preplay_beam_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- BlocksWorld synthetic -----------------------
# State representation: tuple of length N_BLOCKS giving each block's position label
# (0 = table-slot-A, 1 = table-slot-B, 2 = table-slot-C, 3 = held).
# We use a simplified deterministic dynamics: actions transform state via a
# fixed action-table lookup. Ground-truth optimal via BFS in symbolic space.

def encode_state(state: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(state)


def apply_action_sym(state: Tuple[int, ...], action_idx: int) -> Tuple[int, ...]:
    """Deterministic symbolic transition. Each action affects state in a fixed,
    invertible-ish but lossy way. Goal is to reach a target tuple."""
    s = list(state)
    a = action_idx
    if a == 0:  # pick_up: block 0 -> held
        s[0] = 3
    elif a == 1:  # put_down: block 0 (held) -> slot A
        if s[0] == 3:
            s[0] = 0
    elif a == 2:  # stack: block 1 takes block 0's position (if 0 in A/B/C)
        if s[0] in (0, 1, 2):
            s[1] = s[0]
    elif a == 3:  # unstack: block 1 -> slot opposite (0->1, 1->2, 2->0)
        s[1] = (s[1] + 1) % 3
    elif a == 4:  # move_aside: block 2 cycles 0->1->2->0
        s[2] = (s[2] + 1) % 3
    elif a == 5:  # swap: blocks 0 and 3 swap positions
        s[0], s[3] = s[3], s[0]
    return tuple(s)


def bfs_optimal(start: Tuple[int, ...], goal: Tuple[int, ...],
                 max_depth: int) -> Optional[int]:
    """Return optimal plan length (>=1) or None if unreachable within max_depth."""
    if start == goal:
        return 0
    seen = {start: 0}
    q = deque([start])
    while q:
        s = q.popleft()
        if seen[s] >= max_depth:
            continue
        for a in range(N_ACTIONS):
            ns = apply_action_sym(s, a)
            if ns not in seen:
                seen[ns] = seen[s] + 1
                if ns == goal:
                    return seen[ns]
                q.append(ns)
    return None


# ----------------------- HD primitives -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    return float(np.dot(a, b) / (na * nb))


def encode_state_hd(state: Tuple[int, ...], block_role: np.ndarray,
                     pos_filler: np.ndarray) -> np.ndarray:
    """state = (pos0, pos1, ..., posN); bind block_i to pos_filler[pos_i] and bundle."""
    v = np.zeros(block_role.shape[1], dtype=np.float32)
    for i, p in enumerate(state):
        v += hrr_bind(block_role[i], pos_filler[p])
    n = np.linalg.norm(v)
    if n > 1e-8:
        v = v / n
    return v


# ----------------------- planners -----------------------

def plan_greedy(start: Tuple[int, ...], goal: Tuple[int, ...],
                 block_role: np.ndarray, pos_filler: np.ndarray,
                 max_steps: int) -> Tuple[List[int], bool]:
    s = start
    plan: List[int] = []
    goal_hd = encode_state_hd(goal, block_role, pos_filler)
    for _ in range(max_steps):
        if s == goal:
            return plan, True
        best_a = 0
        best_score = -1e9
        for a in range(N_ACTIONS):
            ns = apply_action_sym(s, a)
            ns_hd = encode_state_hd(ns, block_role, pos_filler)
            score = cosine_vec(ns_hd, goal_hd)
            if score > best_score:
                best_score = score
                best_a = a
        plan.append(best_a)
        s = apply_action_sym(s, best_a)
    return plan, (s == goal)


def plan_preplay(start: Tuple[int, ...], goal: Tuple[int, ...],
                  block_role: np.ndarray, pos_filler: np.ndarray,
                  K: int, D: int, g: np.random.Generator,
                  use_goal_gate: bool = False) -> Tuple[List[int], bool]:
    """K parallel random-rollout sequences of depth D; pick best by cos(leaf_hd, goal_hd).
    With use_goal_gate, action sampling at each step weights by goal-conditioned score."""
    goal_hd = encode_state_hd(goal, block_role, pos_filler)
    best_seq: Optional[List[int]] = None
    best_score = -1e9
    best_solved = False
    for _ in range(K):
        s = start
        seq: List[int] = []
        solved = False
        for d in range(D):
            if s == goal:
                solved = True
                break
            if use_goal_gate:
                # score each action by cos(bind(state_hd, goal_hd), action_filler proxy)
                # operationalized: score = cos(next_state_hd, goal_hd) with slight noise
                scores = []
                for a in range(N_ACTIONS):
                    ns = apply_action_sym(s, a)
                    ns_hd = encode_state_hd(ns, block_role, pos_filler)
                    sc = cosine_vec(ns_hd, goal_hd)
                    scores.append(sc + 0.05 * float(g.standard_normal()))
                # softmax-temperature sampling
                arr = np.array(scores)
                arr = arr - arr.max()
                p = np.exp(arr / 0.1)
                p = p / p.sum()
                a_pick = int(g.choice(N_ACTIONS, p=p))
            else:
                a_pick = int(g.integers(0, N_ACTIONS))
            seq.append(a_pick)
            s = apply_action_sym(s, a_pick)
        if s == goal:
            solved = True
        s_hd = encode_state_hd(s, block_role, pos_filler)
        score = cosine_vec(s_hd, goal_hd)
        # Solved trajectories always beat unsolved
        if solved:
            if not best_solved or len(seq) < len(best_seq):
                best_solved = True
                best_seq = seq
                best_score = score
        elif not best_solved and score > best_score:
            best_score = score
            best_seq = seq
    return (best_seq or [], best_solved)


def plan_random(start: Tuple[int, ...], goal: Tuple[int, ...],
                 g: np.random.Generator, max_steps: int) -> Tuple[List[int], bool]:
    s = start
    plan: List[int] = []
    for _ in range(max_steps):
        if s == goal:
            return plan, True
        a = int(g.integers(0, N_ACTIONS))
        plan.append(a)
        s = apply_action_sym(s, a)
    return plan, (s == goal)


# ----------------------- per-seed runner -----------------------

def sample_solvable_goal(g: np.random.Generator, max_depth: int) -> Tuple[Tuple[int, ...], Tuple[int, ...], int]:
    """Sample a (start, goal) pair where optimal plan length is in [3, max_depth]."""
    for _ in range(200):
        start = tuple(int(g.integers(0, 4)) for _ in range(N_BLOCKS))
        goal = tuple(int(g.integers(0, 4)) for _ in range(N_BLOCKS))
        if start == goal:
            continue
        opt = bfs_optimal(start, goal, max_depth)
        if opt is not None and opt >= 3:
            return start, goal, opt
    # fallback: any reachable pair
    start = tuple(int(g.integers(0, 4)) for _ in range(N_BLOCKS))
    goal = tuple(int(g.integers(0, 4)) for _ in range(N_BLOCKS))
    opt = bfs_optimal(start, goal, max_depth) or max_depth
    return start, goal, opt


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    block_role = bipolar(N_BLOCKS, N_DIM, g)
    pos_filler = bipolar(4, N_DIM, g)  # 4 positions

    # Sample goals once for this seed (fair across arms)
    goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int]] = []
    for _ in range(N_GOALS):
        goals.append(sample_solvable_goal(g, DEPTH * 2))

    per_arm: Dict[str, Dict[str, Any]] = {}
    arm_runners = [
        ("greedy_1step", lambda s, gl, ggen: plan_greedy(s, gl, block_role, pos_filler, DEPTH)),
        ("preplay_k4", lambda s, gl, ggen: plan_preplay(s, gl, block_role, pos_filler, K_BEAM["k4"], DEPTH, ggen, use_goal_gate=False)),
        ("preplay_k64", lambda s, gl, ggen: plan_preplay(s, gl, block_role, pos_filler, K_BEAM["k64"], DEPTH, ggen, use_goal_gate=False)),
        ("preplay_k64_with_goal_gate", lambda s, gl, ggen: plan_preplay(s, gl, block_role, pos_filler, K_BEAM["k64"], DEPTH, ggen, use_goal_gate=True)),
        ("random_control", lambda s, gl, ggen: plan_random(s, gl, ggen, DEPTH)),
    ]

    for arm_name, runner in arm_runners:
        n_solved = 0
        plan_lens: List[int] = []
        ratios: List[float] = []
        # Per-arm RNG derived from seed for reproducibility across arms
        ag = np.random.default_rng(seed * 1009 + hash(arm_name) % (10 ** 6))
        for (s, gl, opt) in goals:
            plan, solved = runner(s, gl, ag)
            if solved:
                n_solved += 1
                # Re-derive plan length to solve point (truncate at first match)
                cur = s
                for i, a in enumerate(plan):
                    cur = apply_action_sym(cur, a)
                    if cur == gl:
                        plan_lens.append(i + 1)
                        ratios.append((i + 1) / max(1, opt))
                        break
        per_arm[arm_name] = {
            "solve_rate": n_solved / N_GOALS,
            "n_solved": n_solved,
            "n_goals": N_GOALS,
            "median_plan_len": float(np.median(plan_lens)) if plan_lens else float(DEPTH),
            "median_plan_ratio_vs_optimal": float(np.median(ratios)) if ratios else float("inf"),
        }

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
    }


# ----------------------- aggregate + verdict -----------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}

    arm_solves: Dict[str, List[float]] = {arm: [] for arm in EXPECTED_ARMS}
    arm_ratios: Dict[str, List[float]] = {arm: [] for arm in EXPECTED_ARMS}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    for s_key, body in per_seed.items():
        pa = body.get("per_arm", {})
        for arm in EXPECTED_ARMS:
            if arm in pa:
                arm_solves[arm].append(pa[arm]["solve_rate"])
                arm_ratios[arm].append(pa[arm]["median_plan_ratio_vs_optimal"])
                per_arm_full[arm][s_key] = pa[arm]

    summary: Dict[str, Dict[str, float]] = {}
    for arm in EXPECTED_ARMS:
        if arm_solves[arm]:
            summary[arm] = {
                "solve_rate_mean": float(np.mean(arm_solves[arm])),
                "solve_rate_std": float(np.std(arm_solves[arm])),
                "median_plan_ratio_mean": float(np.mean([r for r in arm_ratios[arm] if r != float("inf")])) if any(r != float("inf") for r in arm_ratios[arm]) else float("inf"),
                "n": len(arm_solves[arm]),
            }
        else:
            summary[arm] = {"solve_rate_mean": 0.0, "n": 0}

    greedy = summary["greedy_1step"]["solve_rate_mean"]
    k4 = summary["preplay_k4"]["solve_rate_mean"]
    k64 = summary["preplay_k64"]["solve_rate_mean"]
    k64_gg = summary["preplay_k64_with_goal_gate"]["solve_rate_mean"]
    rand = summary["random_control"]["solve_rate_mean"]
    k64_ratio = summary["preplay_k64"].get("median_plan_ratio_mean", float("inf"))

    # Oracle is 1.0 (analytic-solver ground truth); gap closure
    oracle = 1.0
    gg_gap_close = (k64_gg - k64) / max(1e-6, oracle - k64) if (oracle - k64) > 0 else 0.0

    verdict = "MIDDLE_BAND"
    plan_len_ok = (k64_ratio <= HP_PLAN_LEN_RATIO_MAX)
    if (k64 >= HP_SOLVE_MIN and
            (k64 - greedy) >= HP_OVER_GREEDY_MIN and
            (k64 - k4) >= HP_K64_OVER_K4_MIN and
            gg_gap_close >= HP_GOAL_GATE_GAP_CLOSE and
            plan_len_ok and
            rand <= HP_RANDOM_MAX):
        verdict = "HARD_PASS"
    elif (k64 <= HF_SOLVE_LO or (k64 - k4) < HF_K64_OVER_K4_LO or rand > HF_RANDOM_HI):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | GREEDY=%.3f K4=%.3f K64=%.3f K64+GG=%.3f RANDOM=%.3f | "
        "K64-K4=%.3f K64-GREEDY=%.3f GG_gap_close=%.3f plan_ratio=%.2f"
    ) % (verdict, greedy, k4, k64, k64_gg, rand,
         k64 - k4, k64 - greedy, gg_gap_close, k64_ratio)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "k64_minus_k4": float(k64 - k4),
        "k64_minus_greedy": float(k64 - greedy),
        "goal_gate_gap_close": float(gg_gap_close),
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_GOALS,
        "cardinality_ok": (len(per_seed) >= 2),
    }


# ----------------------- main -----------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d blocks=%d goals=%d depth=%d K=%s seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_BLOCKS, N_GOALS, DEPTH, K_BEAM, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            k64 = r["per_arm"]["preplay_k64"]["solve_rate"]
            greedy = r["per_arm"]["greedy_1step"]["solve_rate"]
            rand = r["per_arm"]["random_control"]["solve_rate"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: k64=%.3f greedy=%.3f rand=%.3f" % (k64, greedy, rand),
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "k64_solve": k64, "greedy_solve": greedy, "rand_solve": rand})
            print("[selftest] OK; k64=%.3f greedy=%.3f rand=%.3f" % (k64, greedy, rand), flush=True)
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
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_substrate_preplay_beam"
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
