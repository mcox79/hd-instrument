"""
exp_resonator_ksweep_reachability_v1.py -- resonator K-SWEEP reachability wall-vs-budget probe.

RESEARCH CONTEXT (follow-on to exp_resonator_verifier_readout_v1 HARD_PASS +
notes/research_resonator_reachability_ceiling_2026-07-07.md):
At K=4 the resonator's answer-reachability ceiling (oracle_any=0.806 at best T0,
MEASURED@data/exp_resonator_verifier_readout_v1/metrics.json) was shown to be a RESTART-BUDGET
problem, not a basin-measure wall: the per-restart probability of landing in the true basin is
p_basin ~ 0.15 (backed out from oracle_any = 1-(1-p_basin)^R at R=10), so oracle_any->0.95 is
reachable with ~R=19 restarts. The OPEN question: does p_basin COLLAPSE at higher K (K=5,6) due
to a fundamental basin-proliferation / clustering-condensation / overlap-gap-property (OGP) wall --
the same 4th-family mechanism (recurrent-search / basin-proliferation) that falsified the CG_META
self-margin law? This cell MEASURES the p_basin(K) trajectory K3->K4->K5->K6 to discriminate a
fundamental WALL from a mere compute-BUDGET dial.

DESIGN (REUSE of exp_resonator_verifier_readout_v1 machinery; commit 09446de2d):
The Glauber-dither + R-restart + verifier-readout decode is IDENTICAL. decode_trial is a VERBATIM
port (K is already a parameter). ONLY K_GRID changes: [3,4,5,6] (K3/K4 = positive-control
reproducers of the known values; K5/K6 = the new probe). N=4096, M=30, MAXIT=60, R=10 held, and
the full T0 sweep [0.0,0.10,0.20,0.35,0.50] retained for comparability. The verifier read-out is
kept so oracle_any (reachability) is measured cleanly, separated from aggregation loss.

WHAT IS MEASURED per K (at best T0 by oracle_any):
  - oracle_any (reachability ceiling at fixed R=10)
  - p_basin backed out: p_basin = 1 - (1-oracle_any)^(1/R)  (per-restart true-basin probability)
  - R_to_95: smallest R' with 1-(1-p_basin)^R' >= 0.95  (compute cost to lift reachability to 0.95)
The HEADLINE is the p_basin(K) trajectory: K3(~0.383) -> K4(~0.151, known) -> K5 -> K6. Is p_basin
roughly STABLE / mildly-geometric (budget-liftable, just needs more R) or COLLAPSING super-linearly
toward zero (a fundamental basin-proliferation wall)?

PRE-REG bands (HARD distinction; discriminator = p_basin at K=6, per research Prediction B):
  BUDGET (HARD-PASS): p_basin(K6) >= 0.05. Restarts still work -- R_to_95(K6) modest (R~60 lifts to
             0.95); decline is roughly geometric. No fundamental K-dependent wall through K6. This is
             the favorable / capability-positive outcome (reachability is a compute dial).
  WALL (HARD-FAIL): p_basin(K6) < 0.01 (basin measure cratering toward the clustering/condensation
             regime; no realistic R rescues it) OR oracle_any(K6) < 0.10 despite R=10 restarts. This
             CONFIRMS the CG_META-style basin-proliferation algorithmic wall at K*<=6. Honest
             negative; report faithfully, do NOT force a budget read.
  MIDDLE (MIDDLE_BAND): 0.01 <= p_basin(K6) < 0.05 -- declining hard (super-geometric onset) but not
             fully collapsed; wall is emerging, ambiguous, needs K7+ or higher R to localize K*.
  (Geometric extrapolation of the KNOWN K3->K4 ratio predicts p_basin(K6)~0.024 = MIDDLE midpoint,
   so the pre-registered bands bracket the null geometric-decline hypothesis on both sides.)

POSITIVE CONTROL (Gate D -- reproduce prior chain-grade result AT TEST REGIME):
  K3 best-T0 oracle_any in [0.95,1.00] (ref 0.992) AND K4 best-T0 oracle_any in [0.72,0.90]
  (ref 0.806). Both MEASURED@data/exp_resonator_verifier_readout_v1/metrics.json. If either
  reproducer falls outside tolerance, the numpy port diverged -> K5/K6 trajectory UNTRUSTED -> HARD_FAIL.

INVARIANT (integrity gate): verifier harvest <= oracle_any per arm (verifier can only pick from the
R candidates it was given). Violation => read-out bug.

SMOKE DISCRIMINATOR-FIRES: reachability must actually MOVE across the K axis (else the sweep is
vacuous). Smoke asserts max_K(oracle_any_best) - min_K(oracle_any_best) >= 0.10 AND
oracle_any(K6) < oracle_any(K3). Smoke runs at FULL N=4096/M=30/MAXIT=60/R=10 (discriminator
survives scale trivially -- only TR and seed-count are reduced).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; verifier winners != plurality winners)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator_reachability: bands bracket geometric null (p_basin(K6)~0.024 predicted); reachable
# - baseline_in_band / positive-control at smoke (K3/K4 reproduce GPU/CPU port; Gate D)
# - discriminator survives scale (smoke at FULL N=4096 M=30 K sweep; reachability physics at scale)
# - cardinality_ok: EXPECTED_N_UNITS = seeds*K*T0 gate
# - PAIRED trials: identical codebooks + true tuples across all arms
# - progress_logging: print_flush_true + heartbeat
ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, json, argparse, time, math, traceback, platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "resonator_ksweep_reachability_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config (IDENTICAL decode machinery to exp_resonator_verifier_readout_v1) -
N = 4096
M = 30
MAXIT = 60
R = 10              # restarts per trial; HELD IDENTICAL so oracle_any/p_basin are comparable
T0_GRID = [0.0, 0.10, 0.20, 0.35, 0.50]
K_GRID = [3, 4, 5, 6]     # K3/K4 = positive-control reproducers; K5/K6 = the new probe
TR = 30 if SMOKE else 120
SEEDS = [3] if SMOKE else [3, 7, 13]   # reuse VET seeds -> directly comparable

# cardinality gate (META_RULE_H)
EXPECTED_N_UNITS = len(SEEDS) * len(K_GRID) * len(T0_GRID)

# reachability references (MEASURED@data/exp_resonator_verifier_readout_v1/metrics.json best-T0)
K3_ORACLE_REF = 0.992            # best-T0 (T0=0.50) oracle_any, K3
K4_ORACLE_REF = 0.806            # best-T0 (T0=0.50) oracle_any, K4
K3_ORACLE_LO, K3_ORACLE_HI = 0.95, 1.00
K4_ORACLE_LO, K4_ORACLE_HI = 0.72, 0.90

# wall-vs-budget bands on p_basin(K6) (research Prediction B)
PBASIN_BUDGET_FLOOR = 0.05       # >= this at K6 => BUDGET (no wall through K6)
PBASIN_WALL_CEIL = 0.01          # < this at K6 => WALL (basin-proliferation confirmed)
ORACLE_CRATER = 0.10             # oracle_any(K6) < this despite R=10 => also WALL


# --- reachability -> per-restart basin probability + cost-to-lift ------------
def p_basin_from_oracle(oracle_any: float, R_: int) -> float:
    """Back out per-restart true-basin probability from oracle_any = 1-(1-p)^R.

    p = 1 - (1-oracle_any)^(1/R). Clamped to [0,1] at the boundaries.
    """
    o = min(max(float(oracle_any), 0.0), 1.0)
    if o <= 0.0:
        return 0.0
    if o >= 1.0:
        return 1.0
    return 1.0 - (1.0 - o) ** (1.0 / R_)


def R_to_target(p: float, target: float = 0.95) -> float:
    """Smallest integer R' with 1-(1-p)^R' >= target (compute cost to lift reachability)."""
    if p <= 0.0:
        return float("inf")
    if p >= 1.0:
        return 1.0
    return float(int(math.ceil(math.log(1.0 - target) / math.log(1.0 - p))))


def _recon_score(books: List[np.ndarray], s: np.ndarray, cand: Tuple[int, ...], K: int) -> float:
    """Normalized real inner product between input probe s and candidate reconstruction (verifier)."""
    sh = np.ones(N, dtype=np.complex128)
    for k in range(K):
        sh = sh * books[k][cand[k]]
    return float(np.real(np.vdot(s, sh)) / N)


def _selftest() -> None:
    import numpy as _n
    # 1. phasor unit modulus
    ang = _n.array([0.0, _n.pi / 2, _n.pi])
    assert _n.allclose(_n.abs(_n.exp(1j * ang)), 1.0), "phasor modulus"
    # 2. reconstruction verifier: true tuple -> 1.0; wrong tuple -> small
    rng = _n.random.default_rng(0)
    K = 5
    books = [_n.exp(1j * (rng.random((M, N)) * 2 - 1) * _n.pi) for _ in range(K)]
    true = (7, 3, 19, 2, 11)
    s = _n.ones(N, dtype=_n.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    true_score = _recon_score(books, s, true, K)
    assert abs(true_score - 1.0) < 1e-9, "verifier exact-match must be 1.0, got %.6f" % true_score
    wrong = (7, 3, 19, 2, 5)
    wrong_score = _recon_score(books, s, wrong, K)
    assert abs(wrong_score) < 0.2, "verifier wrong-tuple must be small at N=4096, got %.4f" % wrong_score
    assert true_score - wrong_score > 0.5, "verifier margin must be large"
    cands = [(1, 2, 3, 4, 5), (7, 3, 19, 2, 11), (5, 5, 5, 5, 5)]
    pick = max(set(cands), key=lambda c: _recon_score(books, s, c, K))
    assert pick == true, "verifier argmax must recover truth when present"
    # 3. p_basin / R_to_target formulas (MEASURED anchors from verifier_readout_v1)
    p4 = p_basin_from_oracle(0.806, 10)
    assert abs(p4 - 0.1512) < 1e-3, "p_basin(K4) must be ~0.1512, got %.4f" % p4
    assert R_to_target(p4) == 19.0, "R_to_95(K4) must be 19, got %s" % R_to_target(p4)
    p3 = p_basin_from_oracle(0.992, 10)
    assert abs(p3 - 0.3830) < 1e-3, "p_basin(K3) must be ~0.3830, got %.4f" % p3
    assert R_to_target(p3) == 7.0, "R_to_95(K3) must be 7, got %s" % R_to_target(p3)
    # 4. round-trip: oracle = 1-(1-p)^R must invert to p
    p_in = 0.15
    o_rt = 1.0 - (1.0 - p_in) ** 10
    assert abs(p_basin_from_oracle(o_rt, 10) - p_in) < 1e-9, "p_basin round-trip"
    # 5. edge cases
    assert p_basin_from_oracle(1.0, 10) == 1.0 and R_to_target(1.0) == 1.0, "p_basin=1 edge"
    assert p_basin_from_oracle(0.0, 10) == 0.0 and R_to_target(0.0) == float("inf"), "p_basin=0 edge"
    # 6. monotonicity: lower oracle -> lower p_basin -> larger R_to_95
    assert p_basin_from_oracle(0.5, 10) < p4 < p3, "p_basin monotone in oracle"
    assert R_to_target(p_basin_from_oracle(0.5, 10)) > R_to_target(p4) > R_to_target(p3), "R_to_95 monotone"
    # 7. K=1 decode recovers truth (port health)
    s1 = books[0][7]
    sc = _n.conj(s1)[None, :] @ books[0].T
    assert int(_n.argmax(sc.real)) == 7, "K=1 decode recovers truth"
    print("[selftest] PASS: resonator-ksweep-reachability (7 checks; "
          "p_basin K3=%.4f K4=%.4f R95 K3=%d K4=%d)" % (p3, p4, int(R_to_target(p3)), int(R_to_target(p4))),
          flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# --- defensive instrumentation ----------------------------------------------
def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra: Dict) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": time.perf_counter() - t0,
    }
    row.update(extra)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
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
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# --- resonator decode (VERBATIM port of exp_resonator_verifier_readout_v1) ---
def phasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.abs(v) + 1e-8)


def decode_trial(books: List[np.ndarray], true: Tuple[int, ...], K: int,
                 R_: int, T0: float, rng: np.random.Generator) -> List[Tuple[int, ...]]:
    """Run R_ (dithered) coupled alternating-projection trajectories, batched. VERBATIM port."""
    s = np.ones(N, dtype=np.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    est = [np.tile(_norm(books[k].mean(0)), (R_, 1)) for k in range(K)]  # (R_, N)
    idxs = np.zeros((R_, K), dtype=np.int64)
    prev = None
    locked = np.zeros(R_, dtype=bool)
    answer = np.full((R_, K), -1, dtype=np.int64)
    denom = max(MAXIT - 1, 1)
    for it in range(MAXIT):
        T = T0 * max(0.0, 1.0 - it / denom)
        for k in range(K):
            others = np.ones((R_, N), dtype=np.complex128)
            for j in range(K):
                if j != k:
                    others = others * est[j]
            rr = s[None, :] * np.conj(others)          # (R_, N)
            sc = np.conj(rr) @ books[k].T              # (R_, M)
            newest = sc @ books[k]                     # (R_, N)
            if T > 0.0:
                noise = (rng.standard_normal((R_, N)) + 1j * rng.standard_normal((R_, N))) / np.sqrt(2.0)
                newest = newest + T * noise
            est[k] = _norm(newest)
            idxs[:, k] = np.argmax(sc.real, axis=1)
        if prev is not None:
            agree = np.all(idxs == prev, axis=1) & (~locked)
            if agree.any():
                answer[agree] = idxs[agree]
                locked[agree] = True
        prev = idxs.copy()
    if (~locked).any():
        answer[~locked] = idxs[~locked]
    return [tuple(answer[r].tolist()) for r in range(R_)]


def _hash_tuples(tuples: List[Tuple[int, ...]]) -> str:
    import hashlib
    b = json.dumps(tuples, sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def run_seed(seed: int, output_dir: Path, t0_start: float,
             unit_base: int, total_units: int) -> Dict:
    """All (K, T0) arms for one seed. PAIRED: same codebooks + true tuples across arms."""
    out: Dict[str, Dict] = {}
    arms_hashes: Dict[str, str] = {}
    unit = unit_base
    for K in K_GRID:
        rng_book = np.random.default_rng(seed * 100 + K)
        books = [phasor(M, N, rng_book) for _ in range(K)]
        rng_trial = np.random.default_rng(seed * 1000 + K)
        trues = [tuple(int(x) for x in rng_trial.integers(0, M, size=K)) for _ in range(TR)]

        # baseline arm: deterministic single-shot (T0=0, R=1) -- positive control
        rng_base = np.random.default_rng(seed * 99991 + K)
        base_succ = 0
        base_first_idxs: List[Tuple[int, ...]] = []
        for true in trues:
            t = decode_trial(books, true, K, R_=1, T0=0.0, rng=rng_base)
            base_succ += int(t[0] == true)
            base_first_idxs.append(t[0])
        out["K%d_baseline_T0_R1" % K] = {"plurality": base_succ / TR, "R": 1, "T0": 0.0}
        arms_hashes["K%d_baseline_T0_R1" % K] = _hash_tuples(base_first_idxs)

        # glauber arms: plurality (control) + verifier (lever) on identical candidate sets
        for T0 in T0_GRID:
            rng_dither = np.random.default_rng(seed * 100003 + K * 1009 + int(round(T0 * 1000)))
            plur_succ = 0
            ver_succ = 0
            oracle_any = 0
            wtd_list: List[int] = []
            wrong_set = set()
            plur_winners: List[Tuple[int, ...]] = []
            ver_winners: List[Tuple[int, ...]] = []
            ver_gt_oracle_violations = 0
            for true in trues:
                tuples = decode_trial(books, true, K, R_=R, T0=T0, rng=rng_dither)
                s = np.ones(N, dtype=np.complex128)
                for k in range(K):
                    s = s * books[k][true[k]]
                uniq = list(set(tuples))
                truth_present = any(t == true for t in tuples)
                plur_winner = Counter(tuples).most_common(1)[0][0]
                ver_winner = max(uniq, key=lambda c: _recon_score(books, s, c, K))
                plur_succ += int(plur_winner == true)
                ver_hit = int(ver_winner == true)
                ver_succ += ver_hit
                oracle_any += int(truth_present)
                if ver_hit and not truth_present:
                    ver_gt_oracle_violations += 1
                wtd_list.append(len(uniq))
                for t in tuples:
                    if t != true:
                        wrong_set.add(t)
                plur_winners.append(plur_winner)
                ver_winners.append(ver_winner)
            key = "K%d_verifier_T%03d_R%d" % (K, int(round(T0 * 1000)), R)
            out[key] = {
                "plurality": plur_succ / TR,
                "verifier": ver_succ / TR,
                "oracle_any": oracle_any / TR,
                "verifier_le_oracle_violations": ver_gt_oracle_violations,
                "mean_within_trial_distinct": float(np.mean(wtd_list)),
                "distinct_wrong_configs": len(wrong_set),
                "R": R, "T0": T0,
            }
            arms_hashes[key] = _hash_tuples(ver_winners)
            arms_hashes[key + "_plurality"] = _hash_tuples(plur_winners)
            unit += 1
            _heartbeat(output_dir, unit, total_units, t0_start,
                       {"seed": seed, "K": K, "T0": T0,
                        "oracle_any": oracle_any / TR, "verifier": ver_succ / TR})
            print("  seed=%d K=%d T0=%.2f oracle_any=%.3f verifier=%.3f plurality=%.3f wtd=%.2f distinct_wrong=%d" %
                  (seed, K, T0, oracle_any / TR, ver_succ / TR, plur_succ / TR,
                   float(np.mean(wtd_list)), len(wrong_set)), flush=True)

    return {"seed": seed, "by_arm": out, "arms_hashes": arms_hashes,
            "N": N, "M": M, "run_mode": RUN_MODE}


# --- verdict ----------------------------------------------------------------
def _best_oracle_by_K(per_seed: List[Dict]) -> Dict[int, Dict]:
    """For each K: best-T0 (max oracle_any over T0>0) across seeds -> oracle_any, p_basin, R_to_95."""
    traj: Dict[int, Dict] = {}
    for K in K_GRID:
        best_t0 = None
        best_orc = -1.0
        for T0 in [t for t in T0_GRID if t > 0.0]:
            key = "K%d_verifier_T%03d_R%d" % (K, int(round(T0 * 1000)), R)
            orc = float(np.mean([ps["by_arm"][key]["oracle_any"] for ps in per_seed]))
            if orc > best_orc:
                best_orc = orc
                best_t0 = T0
        # oracle_any at fixed R=10 = best_orc (that IS the fixed-R reachability)
        p_b = p_basin_from_oracle(best_orc, R)
        r95 = R_to_target(p_b, 0.95)
        traj[K] = {
            "best_t0": best_t0,
            "oracle_any_best": best_orc,
            "p_basin": p_b,
            "R_to_95": r95,
        }
    return traj


def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    """Classify the p_basin(K) trajectory: WALL vs BUDGET. Integrity gates first."""
    # integrity: verifier<=oracle invariant across all arms
    total_inv_viol = 0
    for ps in per_seed:
        for k, v in ps["by_arm"].items():
            total_inv_viol += int(v.get("verifier_le_oracle_violations", 0))

    traj = _best_oracle_by_K(per_seed)
    base = {K: float(np.mean([ps["by_arm"]["K%d_baseline_T0_R1" % K]["plurality"] for ps in per_seed]))
            for K in K_GRID}

    # decline ratios (shape of collapse)
    ratios = {}
    for i in range(1, len(K_GRID)):
        Kp, Kc = K_GRID[i - 1], K_GRID[i]
        pp, pc = traj[Kp]["p_basin"], traj[Kc]["p_basin"]
        ratios["K%d/K%d" % (Kc, Kp)] = (pc / pp) if pp > 0 else float("inf")

    detail = {
        "trajectory": {str(K): traj[K] for K in K_GRID},
        "baseline_by_K": {str(K): base[K] for K in K_GRID},
        "p_basin_decline_ratios": ratios,
        "verifier_le_oracle_invariant_violations": total_inv_viol,
        "R_fixed": R,
        "bands": {"budget_floor": PBASIN_BUDGET_FLOOR, "wall_ceil": PBASIN_WALL_CEIL,
                  "oracle_crater": ORACLE_CRATER},
    }

    K6 = K_GRID[-1]
    p6 = traj[K6]["p_basin"]
    o6 = traj[K6]["oracle_any_best"]
    r95_6 = traj[K6]["R_to_95"]

    # positive control (Gate D): K3/K4 reproduce known oracle_any AT TEST REGIME
    o3 = traj[3]["oracle_any_best"] if 3 in traj else float("nan")
    o4 = traj[4]["oracle_any_best"] if 4 in traj else float("nan")
    pc_k3 = (3 not in traj) or (K3_ORACLE_LO <= o3 <= K3_ORACLE_HI)
    pc_k4 = (4 not in traj) or (K4_ORACLE_LO <= o4 <= K4_ORACLE_HI)
    detail["positive_control_ok"] = bool(pc_k3 and pc_k4)
    detail["positive_control"] = {
        "K3_oracle": o3, "K3_band": [K3_ORACLE_LO, K3_ORACLE_HI], "K3_ok": bool(pc_k3),
        "K4_oracle": o4, "K4_band": [K4_ORACLE_LO, K4_ORACLE_HI], "K4_ok": bool(pc_k4),
    }

    traj_str = " ".join("K%d(orc=%.3f,p=%.4f,R95=%s)" %
                        (K, traj[K]["oracle_any_best"], traj[K]["p_basin"],
                         ("inf" if traj[K]["R_to_95"] == float("inf") else int(traj[K]["R_to_95"])))
                        for K in K_GRID)

    # gate 1: integrity invariant
    if total_inv_viol > 0:
        return ("HARD_FAIL",
                "HARD_FAIL_INVARIANT: %d trials where verifier succeeded with truth ABSENT from "
                "candidates -- reconstruction read-out bug (verifier<=oracle_any violated)." % total_inv_viol,
                detail)

    # gate 2: positive control reproduce
    if not detail["positive_control_ok"]:
        return ("HARD_FAIL",
                "HARD_FAIL_POSITIVE_CONTROL: K3 oracle=%.3f (need [%.2f,%.2f]) K4 oracle=%.3f "
                "(need [%.2f,%.2f]) -- numpy port diverged, K5/K6 trajectory UNTRUSTED (Gate D). traj: %s"
                % (o3, K3_ORACLE_LO, K3_ORACLE_HI, o4, K4_ORACLE_LO, K4_ORACLE_HI, traj_str),
                detail)

    # gate 3: wall-vs-budget classification on p_basin(K6)
    if p6 < PBASIN_WALL_CEIL or o6 < ORACLE_CRATER:
        return ("HARD_FAIL",
                "WALL_FUNDAMENTAL (HARD_FAIL): p_basin(K%d)=%.4f < %.2f (or oracle_any=%.3f < %.2f) -- "
                "basin measure craters toward the clustering/condensation regime; no realistic R rescues "
                "it (R_to_95=%s). CONFIRMS the CG_META basin-proliferation algorithmic wall at K*<=%d. "
                "Honest negative. traj: %s"
                % (K6, p6, PBASIN_WALL_CEIL, o6, ORACLE_CRATER,
                   ("inf" if r95_6 == float("inf") else int(r95_6)), K6, traj_str),
                detail)

    if p6 >= PBASIN_BUDGET_FLOOR:
        return ("HARD_PASS",
                "BUDGET_LIFTABLE (HARD_PASS): p_basin(K%d)=%.4f >= %.2f (oracle_any=%.3f, R_to_95=%s) -- "
                "restarts still work through K%d; reachability is a COMPUTE-BUDGET dial, NOT a fundamental "
                "basin-proliferation wall. No K-dependent wall below K%d. traj: %s"
                % (K6, p6, PBASIN_BUDGET_FLOOR, o6,
                   ("inf" if r95_6 == float("inf") else int(r95_6)), K6, K6, traj_str),
                detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: p_basin(K%d)=%.4f in [%.2f,%.2f) (oracle_any=%.3f, R_to_95=%s) -- declining hard "
            "(super-geometric onset) but not fully collapsed; a wall is emerging but K*=%d is not confirmed. "
            "Needs K7+ or higher R to localize K*. traj: %s"
            % (K6, p6, PBASIN_WALL_CEIL, PBASIN_BUDGET_FLOOR, o6,
               ("inf" if r95_6 == float("inf") else int(r95_6)), K6, traj_str),
            detail)


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    total_units = EXPECTED_N_UNITS
    _write_start_marker(output_dir, total_units)
    print("[config] anchor=%s mode=%s N=%d M=%d MAXIT=%d R=%d TR=%d K=%s T0=%s seeds=%s expected_units=%d" %
          (ANCHOR_NAME, RUN_MODE, N, M, MAXIT, R, TR, K_GRID, T0_GRID, SEEDS, total_units), flush=True)

    t0_start = time.perf_counter()
    run_config = {"N": N, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, output_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    unit_base = len(done) * len(K_GRID) * len(T0_GRID)
    for i, seed in enumerate(remaining):
        res = run_seed(seed, output_dir, t0_start,
                       unit_base=unit_base + i * len(K_GRID) * len(T0_GRID),
                       total_units=total_units)
        res["config_version"] = "ANCHOR=%s,N=%d,M=%d" % (ANCHOR_NAME, N, M)
        res["run_mode"] = RUN_MODE
        write_partial(output_dir, seed, res)

    per_seed = list(aggregate_partials(output_dir, SEEDS, run_config=run_config).values())
    if len(per_seed) != len(SEEDS):
        raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: expected %d seeds, got %d"
                           % (len(SEEDS), len(per_seed)))
    # per-seed unit cardinality (each seed must have all K x T0 arms)
    for ps in per_seed:
        n_arms = sum(1 for k in ps["by_arm"] if "_verifier_" in k)
        if n_arms != len(K_GRID) * len(T0_GRID):
            raise RuntimeError("HARD_FAIL_CARDINALITY_META_RULE_H: seed %s has %d verifier arms, expected %d"
                               % (ps.get("seed"), n_arms, len(K_GRID) * len(T0_GRID)))

    # ARMS-MUST-DIFFER (META_RULE_AF): verifier winners must differ from plurality winners (K4 T0=0.20)
    ref = per_seed[0]["arms_hashes"]
    g_key = "K4_verifier_T200_R%d" % R
    arms_differ_ok = True
    if g_key in ref and (g_key + "_plurality") in ref:
        arms_differ_ok = ref[g_key] != ref[g_key + "_plurality"]
    if not arms_differ_ok:
        raise RuntimeError("META_RULE_AF VIOLATION: verifier and plurality read-outs produced bit-identical "
                           "winners on K4 T0=0.20 -- aggregator swap had zero effect (implementation bug)")

    verdict, vmsg, detail = build_verdict(per_seed)
    detail["arms_differ_verified"] = arms_differ_ok

    # SMOKE DISCRIMINATOR-FIRES gate: reachability must actually move across K
    orc_by_K = {K: detail["trajectory"][str(K)]["oracle_any_best"] for K in K_GRID}
    spread = max(orc_by_K.values()) - min(orc_by_K.values())
    declines = orc_by_K[K_GRID[-1]] < orc_by_K[K_GRID[0]]
    detail["smoke_discriminator_spread"] = spread
    detail["smoke_discriminator_declines"] = bool(declines)
    detail["smoke_discriminator_fired"] = bool(spread >= 0.10 and declines)
    if SMOKE and not detail["smoke_discriminator_fired"]:
        print("[SMOKE_GATE_FAIL] discriminator did NOT fire: K-axis oracle_any spread=%.3f (need>=0.10) "
              "declines=%s. Reachability does not move across K -- sweep vacuous; DO NOT dispatch FULL."
              % (spread, declines), flush=True)

    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "per_seed": per_seed,
        "detail": detail,
        "config": {"N": N, "M": M, "MAXIT": MAXIT, "R": R, "TR": TR,
                   "T0_GRID": T0_GRID, "K_GRID": K_GRID, "SEEDS": SEEDS,
                   "EXPECTED_N_UNITS": EXPECTED_N_UNITS},
        "elapsed_s": time.perf_counter() - t0_start,
    }
    write_metrics(output_dir, metrics, per_seed)
    print("[metrics] written -> %s" % (output_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
