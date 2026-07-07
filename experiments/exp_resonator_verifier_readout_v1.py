"""
exp_resonator_verifier_readout_v1.py -- resonator K4 SMARTER-AGGREGATOR (verifier) read-out lever.

RESEARCH CONTEXT (follow-on to exp_resonator_glauber_plurality_v1 VET):
The Glauber-dither + R-restart resonator REACHES the true K4 factorization in ~80% of trials
(oracle_any=0.800 at T0=0.35, MEASURED@data/exp_resonator_glauber_plurality_v1/metrics.json:
per_seed) but the PLURALITY read-out harvests only 0.464 -- because the R=10 restarts are
near-all-distinct (mean_within_trial_distinct~9.18), so the plurality vote is a near-10-way tie
and throws the signal away. distinct_wrong_min=992 => failures scatter (NOT a basin trap). The
residual gap is AGGREGATION-LOSS + restart-budget, NOT unreachable basins.

THE LEVER TESTED HERE: replace the plurality vote with a RECONSTRUCTION VERIFIER read-out. The
Glauber+restart machinery is IDENTICAL (same decode_trial, same R=10, same T0 grid, same seeds).
ONLY the aggregator changes: instead of most-frequent tuple, SCORE each of the R candidate tuples
by how well its factors reconstruct the GIVEN input probe s (bind the candidate factors back,
measure normalized inner product to s) and pick the best. The verifier uses only s (the input
being factored) + the codebooks -- both available at decode time; it NEVER sees the true index
tuple. This is the standard resonator-with-verifier idea; it needs no new dynamics.

WHY IT SHOULD WORK (THEORETICAL@ normalized-phasor-inner-product): the true tuple reconstructs s
EXACTLY -> recon score = 1.0. Any wrong tuple differs in >=1 factor -> its reconstruction is s times
an independent random phasor product -> recon score ~ N(0, 1/N), magnitude ~1/sqrt(N)~0.0156 at
N=4096. So whenever the true tuple is among the R candidates (prob = oracle_any), the verifier picks
it with near-certainty. Expected verifier harvest ~= oracle_any (~0.80 at T0=0.35) >> 0.50 bar.
Discriminator SHARPENS with N (wrong recon shrinks as 1/sqrt(N)) -> survives scale trivially.

PRE-REG bands (K=4 target; direct comparison to plurality 0.464):
  HARD-PASS: K4 VERIFIER harvested success >= 0.50 AND verifier > plurality + 0.05 (genuine lift,
             not read-out noise) AND positive control K3 baseline in [0.40, 0.95] (~0.7). Clears the
             bar the plurality read-out missed -> residual gap WAS aggregation-loss (confirms VET).
  HARD-FAIL: verifier <= plurality + 0.02 (no material lift over plurality). If a reconstruction
             verifier CANNOT beat plurality, the gap is NOT aggregation-loss after all -> REFUTES the
             VET diagnostic. Report HONESTLY; do NOT force a pass.
  MIDDLE:    plurality+0.05 < verifier < 0.50 (real lift, does not clear the 0.50 bar).

INVARIANT (integrity gate): verifier harvest <= oracle_any per arm (verifier can only pick from the
R candidates it was given; it cannot invent the true tuple). Violation => read-out bug.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; verifier winners != plurality winners)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator_reachability: verifier <= oracle_any(0.80); HARD_PASS 0.50 reachable (declared)
# - baseline_in_band at smoke (K3 baseline ~0.7 reproduces GPU port; positive control Gate D)
# - discriminator survives scale (smoke runs at FULL N=4096 M=30 K=4; verifier sharpens with N)
# - PAIRED trials: identical codebooks + true tuples across all arms; plurality & verifier share trials
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
import os, json, argparse, time, traceback, platform
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

ANCHOR_NAME = "resonator_verifier_readout_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config (IDENTICAL machinery to exp_resonator_glauber_plurality_v1) ------
N = 4096
M = 30
MAXIT = 60
R = 10              # restarts per trial; HELD IDENTICAL so oracle_any ceiling is unchanged
T0_GRID = [0.0, 0.10, 0.20, 0.35, 0.50]
K_GRID = [3, 4]
TR = 30 if SMOKE else 120
SEEDS = [3] if SMOKE else [3, 7, 13]   # reuse VET seeds -> directly comparable

# bands
PLURALITY_K4_REF = 0.464            # MEASURED@data/exp_resonator_glauber_plurality_v1/metrics.json (T0=0.35 across-seed mean approx)
HARD_PASS_FLOOR = 0.50
LIFT_MIN = 0.05                     # verifier must beat plurality by this for genuine-lift PASS
HARD_FAIL_LIFT = 0.02              # verifier <= plurality + this == no material lift (refutes VET)


def _recon_score(books: List[np.ndarray], s: np.ndarray, cand: Tuple[int, ...], K: int) -> float:
    """Normalized real inner product between input probe s and the candidate reconstruction.

    s and s_hat are both unit-modulus phasor products (|.|=sqrt(N)); exact match -> 1.0,
    wrong tuple -> ~N(0, 1/N) (magnitude ~1/sqrt(N)). Uses only s + codebooks, not the true tuple.
    """
    sh = np.ones(N, dtype=np.complex128)
    for k in range(K):
        sh = sh * books[k][cand[k]]
    return float(np.real(np.vdot(s, sh)) / N)   # vdot conjugates first arg


def _selftest() -> None:
    import numpy as _n
    # 1. phasor unit modulus
    ang = _n.array([0.0, _n.pi / 2, _n.pi])
    assert _n.allclose(_n.abs(_n.exp(1j * ang)), 1.0), "phasor modulus"
    # 2. reconstruction verifier: true tuple -> 1.0; wrong tuple -> small
    rng = _n.random.default_rng(0)
    K = 4
    books = [_n.exp(1j * (rng.random((M, N)) * 2 - 1) * _n.pi) for _ in range(K)]
    true = (7, 3, 19, 2)
    s = _n.ones(N, dtype=_n.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    true_score = _recon_score(books, s, true, K)
    assert abs(true_score - 1.0) < 1e-9, "verifier exact-match must be 1.0, got %.6f" % true_score
    wrong = (7, 3, 19, 5)   # differs in last factor
    wrong_score = _recon_score(books, s, wrong, K)
    assert abs(wrong_score) < 0.2, "verifier wrong-tuple must be small at N=4096, got %.4f" % wrong_score
    assert true_score - wrong_score > 0.5, "verifier margin must be large"
    # 3. verifier argmax over a candidate set containing truth picks truth
    cands = [(1, 2, 3, 4), (7, 3, 19, 2), (5, 5, 5, 5), (0, 0, 0, 0)]
    pick = max(set(cands), key=lambda c: _recon_score(books, s, c, K))
    assert pick == true, "verifier argmax must recover truth when present"
    # 4. plurality (control) mode
    assert Counter([(1, 2), (1, 2), (3, 4)]).most_common(1)[0][0] == (1, 2), "plurality mode"
    # 5. invariant sanity: verifier success implies truth in candidate set (<= oracle_any)
    cands_no_truth = [(1, 2, 3, 4), (5, 5, 5, 5)]
    pick2 = max(set(cands_no_truth), key=lambda c: _recon_score(books, s, c, K))
    assert pick2 != true, "verifier cannot invent truth absent from candidates"
    # 6. K=1 decode recovers truth (port health)
    s1 = books[0][7]
    sc = _n.conj(s1)[None, :] @ books[0].T
    assert int(_n.argmax(sc.real)) == 7, "K=1 decode recovers truth"
    print("[selftest] PASS: resonator-verifier-readout (6 checks; verifier true=%.4f wrong=%.4f)"
          % (true_score, wrong_score), flush=True)


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


# --- resonator decode (VERBATIM port of exp_resonator_glauber_plurality_v1) --
def phasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """(m, d) unit-modulus complex phasor codebook."""
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.abs(v) + 1e-8)


def decode_trial(books: List[np.ndarray], true: Tuple[int, ...], K: int,
                 R_: int, T0: float, rng: np.random.Generator) -> List[Tuple[int, ...]]:
    """Run R_ (dithered) coupled alternating-projection trajectories, batched.

    IDENTICAL to exp_resonator_glauber_plurality_v1.decode_trial. Returns the list of R_ decoded
    joint-index tuples (one per restart). Transient-capture early-break (first consecutive-agreement
    iteration) faithfully reproduces the original; T0 anneals linearly to 0 over MAXIT.
    """
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
    """All (K, T0) arms for one seed. PAIRED: same codebooks + true tuples across arms.

    For each glauber arm: plurality (control) AND verifier (lever) computed on the SAME R candidate
    tuples, so the lift is a within-trial paired comparison. s (input probe) is reconstructed for the
    verifier from the codebooks; the verifier never touches the integer true tuple.
    """
    out: Dict[str, Dict] = {}
    arms_hashes: Dict[str, str] = {}
    unit = unit_base
    for K in K_GRID:
        rng_book = np.random.default_rng(seed * 100 + K)
        books = [phasor(M, N, rng_book) for _ in range(K)]
        rng_trial = np.random.default_rng(seed * 1000 + K)
        trues = [tuple(int(x) for x in rng_trial.integers(0, M, size=K)) for _ in range(TR)]

        # baseline arm: deterministic single-shot (T0=0, R=1) -- positive control (Gate D)
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
                # rebuild the input probe s (given at decode time; NOT the integer true tuple)
                s = np.ones(N, dtype=np.complex128)
                for k in range(K):
                    s = s * books[k][true[k]]
                uniq = list(set(tuples))
                truth_present = any(t == true for t in tuples)
                # control: plurality
                plur_winner = Counter(tuples).most_common(1)[0][0]
                # lever: verifier argmax reconstruction score
                ver_winner = max(uniq, key=lambda c: _recon_score(books, s, c, K))
                plur_succ += int(plur_winner == true)
                ver_hit = int(ver_winner == true)
                ver_succ += ver_hit
                oracle_any += int(truth_present)
                # invariant: verifier can only succeed if truth present in candidates
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
            # arm signature = verifier winners; keep plurality-winner hash to prove arms differ
            arms_hashes[key] = _hash_tuples(ver_winners)
            arms_hashes[key + "_plurality"] = _hash_tuples(plur_winners)
            unit += 1
            _heartbeat(output_dir, unit, total_units, t0_start,
                       {"seed": seed, "K": K, "T0": T0,
                        "verifier": ver_succ / TR, "plurality": plur_succ / TR})
            print("  seed=%d K=%d T0=%.2f verifier=%.3f plurality=%.3f oracle_any=%.3f wtd=%.2f distinct_wrong=%d" %
                  (seed, K, T0, ver_succ / TR, plur_succ / TR, oracle_any / TR,
                   float(np.mean(wtd_list)), len(wrong_set)), flush=True)

    return {"seed": seed, "by_arm": out, "arms_hashes": arms_hashes,
            "N": N, "M": M, "run_mode": RUN_MODE}


# --- verdict ----------------------------------------------------------------
def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    """Aggregate K4 across seeds; pick best T0>0 by VERIFIER harvest; apply bands vs plurality."""
    base_k4 = [ps["by_arm"]["K4_baseline_T0_R1"]["plurality"] for ps in per_seed]
    base_k4_mean = float(np.mean(base_k4))
    base_k3 = [ps["by_arm"]["K3_baseline_T0_R1"]["plurality"]
               for ps in per_seed if "K3_baseline_T0_R1" in ps["by_arm"]]
    base_k3_mean = float(np.mean(base_k3)) if base_k3 else float("nan")

    # integrity: total verifier<=oracle invariant violations across all arms
    total_inv_viol = 0
    for ps in per_seed:
        for k, v in ps["by_arm"].items():
            total_inv_viol += int(v.get("verifier_le_oracle_violations", 0))

    t0_summary = {}
    for T0 in T0_GRID:
        key = "K4_verifier_T%03d_R%d" % (int(round(T0 * 1000)), R)
        ver = [ps["by_arm"][key]["verifier"] for ps in per_seed]
        plur = [ps["by_arm"][key]["plurality"] for ps in per_seed]
        wtd = [ps["by_arm"][key]["mean_within_trial_distinct"] for ps in per_seed]
        dw = [ps["by_arm"][key]["distinct_wrong_configs"] for ps in per_seed]
        orc = [ps["by_arm"][key]["oracle_any"] for ps in per_seed]
        t0_summary[T0] = {
            "verifier_mean": float(np.mean(ver)),
            "plurality_mean": float(np.mean(plur)),
            "mean_within_trial_distinct": float(np.mean(wtd)),
            "distinct_wrong_min": int(min(dw)),
            "oracle_any_mean": float(np.mean(orc)),
        }

    nonzero = [t for t in T0_GRID if t > 0.0]
    best_t0 = max(nonzero, key=lambda t: t0_summary[t]["verifier_mean"])
    b = t0_summary[best_t0]
    ver = b["verifier_mean"]
    plur = b["plurality_mean"]
    orc = b["oracle_any_mean"]
    lift = ver - plur

    # positive-control (Gate D): K3 baseline ~0.7 (robust port reproducer) AND K4 baseline not saturated
    if base_k3:
        pc_ok = (0.40 <= base_k3_mean <= 0.95) and (base_k4_mean <= 0.35)
    else:
        pc_ok = 0.02 <= base_k4_mean <= 0.35

    detail = {
        "baseline_K4_mean": base_k4_mean, "baseline_K3_mean": base_k3_mean,
        "positive_control_ok": pc_ok,
        "best_t0": best_t0, "best_t0_verifier_mean": ver, "best_t0_plurality_mean": plur,
        "best_t0_lift": lift, "best_t0_oracle_any_mean": orc,
        "best_t0_distinct_wrong_min": b["distinct_wrong_min"],
        "best_t0_mean_within_trial_distinct": b["mean_within_trial_distinct"],
        "verifier_le_oracle_invariant_violations": total_inv_viol,
        "t0_summary": {str(k): v for k, v in t0_summary.items()},
    }

    # integrity gate first: verifier must never exceed oracle (would be a read-out bug)
    if total_inv_viol > 0:
        return ("HARD_FAIL",
                "HARD_FAIL_INVARIANT: %d trials where verifier succeeded with truth ABSENT from "
                "candidates -- reconstruction read-out bug (verifier<=oracle_any violated)." % total_inv_viol,
                detail)

    if not pc_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_POSITIVE_CONTROL: baseline K3=%.3f (need [0.40,0.95]~0.7) K4=%.3f (need <=0.35) "
                "-- numpy port diverged, downstream arms untrusted (Gate D). best_t0=%.2f ver=%.3f"
                % (base_k3_mean, base_k4_mean, best_t0, ver), detail)

    if ver >= HARD_PASS_FLOOR and lift >= LIFT_MIN:
        return ("HARD_PASS",
                "HARD_PASS: K4 VERIFIER harvest=%.3f (>=0.50) at T0=%.2f, +%.3f over plurality=%.3f "
                "(oracle_any=%.3f). Reconstruction verifier harvests the already-reached answer; the "
                "residual gap WAS aggregation-loss, confirming the VET diagnostic. baseline_K4=%.3f."
                % (ver, best_t0, lift, plur, orc, base_k4_mean), detail)

    if lift <= HARD_FAIL_LIFT:
        return ("HARD_FAIL",
                "HARD_FAIL_NO_LIFT: K4 verifier=%.3f <= plurality=%.3f + %.2f (lift=%.3f) at T0=%.2f. A "
                "reconstruction verifier CANNOT beat plurality -> the gap is NOT aggregation-loss; this "
                "REFUTES the VET diagnostic. oracle_any=%.3f. Honest negative, reported not forced."
                % (ver, plur, HARD_FAIL_LIFT, lift, best_t0, orc), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: K4 verifier=%.3f at T0=%.2f -- genuine lift +%.3f over plurality=%.3f but below "
            "0.50 (oracle_any=%.3f). Aggregation-loss partly recovered; not fully. NOT forced to PASS."
            % (ver, best_t0, lift, plur, orc), detail)


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    total_units = len(SEEDS) * len(K_GRID) * len(T0_GRID)
    _write_start_marker(output_dir, total_units)
    print("[config] anchor=%s mode=%s N=%d M=%d MAXIT=%d R=%d TR=%d K=%s T0=%s seeds=%s" %
          (ANCHOR_NAME, RUN_MODE, N, M, MAXIT, R, TR, K_GRID, T0_GRID, SEEDS), flush=True)

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
        raise RuntimeError("HARD_FAIL_CARDINALITY: expected %d seeds, got %d" % (len(SEEDS), len(per_seed)))

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
                   "T0_GRID": T0_GRID, "K_GRID": K_GRID, "SEEDS": SEEDS},
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
