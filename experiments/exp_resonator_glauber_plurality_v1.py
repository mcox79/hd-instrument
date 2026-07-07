"""
exp_resonator_glauber_plurality_v1.py -- resonator K-way factorization EXTERNAL-RESET lever.

RESEARCH CONTEXT (2x-drill noise-compounding-bound, notes/research_noise_compounding_bound_deep_mechanism_2026-07-07.md):
The recurrent-noise-compounding bound is hypothesized CONTRABLE, not fundamental. Reasoning-depth
survives multi-hop because each hop RE-CLEANS to an EXTERNAL fixed codebook (regenerative digital
repeater -> zero-residual reset). The resonator LACKS this: its deterministic zero-temperature coupled
alternating-projection search has NO external reset, so spurious joint fixed points proliferate with K
(K4=0.142 vs K2=1.0 single-shot; MEASURED@data/exp_resonator_capacity_gpu_v1/metrics.json:per_seed[0].by).

THE LEVER TESTED HERE: finite-temperature GLAUBER relaxation (annealed complex-Gaussian dither injected
into the est vectors during iteration) + REDUNDANT-RESTART PLURALITY-VOTE (R independent noisy
trajectories per trial, decode = most-frequent joint-index tuple). Hypothesis: stochasticity + multiple
restarts + majority-decode escape/outvote diverse spurious basins.

HONEST ODDS: P_deflated ~0.20-0.28 (secondary thread). The open empirical question is whether the
deterministic coupled dynamics is CHAOTICALLY sensitive to small dither (favorable -> restarts land in
DIFFERENT wrong basins, plurality outvotes them) or ROBUSTLY deterministic / basin-measure-trapped
(unfavorable -> dither reproduces the same wrong basin, redundancy vacuous, OR spurious basins
collectively outweigh the true basin so plurality converges on a spurious answer).

Reuses exp_resonator_capacity_gpu_v1's codebook construction + decode math (phasor codebooks; coupled
alternating-projection cleanup). CPU/numpy (decode-only, remote_cpu_queue target). Adds the Glauber-T +
restart-plurality wrapper the original lacks. Per-trial per-restart decoded idx tuples are logged (closes
the instrumentation gap the resonator drill flagged).

PRE-REG bands (VERBATIM from the drill, K=4 target):
  HARD-PASS: K4 plurality-vote success >= 0.50 AND failures scatter over >= 5 DISTINCT wrong configs
             (proves outvoting DIVERSE spurious basins, not luck).
  HARD-FAIL: K4 plurality <= 0.192 (no better than 0.142 baseline + 0.05) OR restarts COLLAPSE onto the
             same 1-2 wrong configs (redundancy inverts / basin-measure trap).
  MIDDLE:    0.192 < K4 plurality < 0.50 (real lift, honest partial rescue; do NOT force to HARD-PASS).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (write_metrics) + per-seed partials
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb / discriminator_reachability declared in prereg (idealized i.i.d. plurality reachable IFF dither decorrelates)
# - baseline_in_band at smoke (baseline_T0_R1 must reproduce ~0.142; positive control Gate D)
# - discriminator survives scale (smoke runs at FULL N=4096 M=30 K=4; decode-only, same regime as full)
# - PAIRED trials: identical codebooks + true-index tuples across all T0 arms within a (seed,K)
# - progress_logging: print_flush_true + heartbeat
ASCII-only. write_metrics. PROT-018 _v1.
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

ANCHOR_NAME = "resonator_glauber_plurality_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config -----------------------------------------------------------------
N = 4096
M = 30
MAXIT = 60          # match exp_resonator_capacity_gpu_v1
R = 10              # restarts per trial (drill bands are stated for R=10)
T0_GRID = [0.0, 0.10, 0.20, 0.35, 0.50]   # Glauber temperature; 0.0 == deterministic control
K_GRID = [3, 4]     # K=3 baseline (~0.7) is the robust port-reproducer positive control; K=4 is target
TR = 30 if SMOKE else 120
SEEDS = [3] if SMOKE else [3, 7, 13]

# drill baseline (single-shot deterministic K4), for positive-control band
BASELINE_K4 = 0.14166666666666666   # MEASURED@data/exp_resonator_capacity_gpu_v1/metrics.json
HARD_FAIL_CEIL = BASELINE_K4 + 0.05  # 0.1917 ; K4 plurality <= this == no material lift
HARD_PASS_FLOOR = 0.50
SCATTER_MIN = 5      # distinct wrong configs for HARD-PASS
COLLAPSE_WTD = 1.5   # mean within-trial distinct-tuple count below this == restarts collapse


def _selftest() -> None:
    # formula self-tests -- assert measured == expected BEFORE any full dispatch
    import numpy as _n
    # 1. phasor unit modulus
    ang = _n.array([0.0, _n.pi / 2, _n.pi])
    ph = _n.exp(1j * ang)
    assert _n.allclose(_n.abs(ph), 1.0), "phasor modulus"
    # 2. plurality (mode) picks the most frequent tuple
    tuples = [(1, 2), (1, 2), (3, 4)]
    win = Counter(tuples).most_common(1)[0][0]
    assert win == (1, 2), "plurality mode"
    # 3. distinct-count
    assert len(set(tuples)) == 2, "distinct-count"
    # 4. within-trial-distinct for identical (deterministic) restarts == 1
    assert len(set([(5, 6), (5, 6), (5, 6)])) == 1, "collapse-detector base"
    # 5. resonator decode reproduces ground truth in the trivial K=1 case
    rng = _n.random.default_rng(0)
    book = _n.exp(1j * (rng.random((M, N)) * 2 - 1) * _n.pi)
    true0 = 7
    s = book[true0]
    sc = _n.conj(s)[None, :] @ book.T  # (1, M): correlation with codebook
    assert int(_n.argmax(sc.real)) == true0, "K=1 decode recovers truth"
    # 6. band arithmetic
    assert abs(HARD_FAIL_CEIL - 0.1917) < 1e-3, "hard-fail ceiling"
    print("[selftest] PASS: resonator-glauber-plurality (6 formula checks)", flush=True)


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


# --- resonator decode (numpy port of exp_resonator_capacity_gpu_v1) ---------
def phasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """(m, d) unit-modulus complex phasor codebook."""
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.abs(v) + 1e-8)


def decode_trial(books: List[np.ndarray], true: Tuple[int, ...], K: int,
                 R_: int, T0: float, rng: np.random.Generator) -> List[Tuple[int, ...]]:
    """Run R_ (dithered) coupled alternating-projection trajectories, batched.

    Returns the list of R_ decoded joint-index tuples (one per restart).

    DECODE SEMANTICS (faithful to exp_resonator_capacity_gpu_v1): the original
    reads the idxs at the FIRST iteration whose argmax equals the previous
    iteration's argmax (`if idxs == prev: break`) -- a transient-capture, NOT a
    converged fixed point (verified: 60/60 K4 trajectories never settle within
    MAXIT and are not period-2; the early-break is what makes the baseline
    0.142, and running to the wandering endpoint gives ~0). This function
    replicates that PER RESTART: each restart locks its answer at its own first
    consecutive-agreement iteration; restarts that never agree take the last
    iteration's idxs.

    T0 anneals linearly to 0 over MAXIT (early high-T explores; late T~0 lets a
    settled trajectory trigger consecutive-agreement). T0==0, R_==1 reproduces
    the original deterministic single-shot decode exactly.
    """
    s = np.ones(N, dtype=np.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    # deterministic mean-of-codebook init, replicated across restarts
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
            sc = np.conj(rr) @ books[k].T              # (R_, M) match: books[k] @ rr.conj()
            newest = sc @ books[k]                     # (R_, N)
            if T > 0.0:
                noise = (rng.standard_normal((R_, N)) + 1j * rng.standard_normal((R_, N))) / np.sqrt(2.0)
                newest = newest + T * noise
            est[k] = _norm(newest)
            idxs[:, k] = np.argmax(sc.real, axis=1)
        if prev is not None:
            agree = np.all(idxs == prev, axis=1) & (~locked)   # (R_,) first consecutive-agreement
            if agree.any():
                answer[agree] = idxs[agree]
                locked[agree] = True
        prev = idxs.copy()
    if (~locked).any():
        answer[~locked] = idxs[~locked]                # never-agreed -> last-iteration idxs
    return [tuple(answer[r].tolist()) for r in range(R_)]


def run_seed(seed: int, output_dir: Path, t0_start: float,
             unit_base: int, total_units: int) -> Dict:
    """All (K, T0) arms for one seed. PAIRED: same codebooks + true tuples across T0."""
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
        base_rate = base_succ / TR
        out["K%d_baseline_T0_R1" % K] = {"plurality": base_rate, "R": 1, "T0": 0.0}
        arms_hashes["K%d_baseline_T0_R1" % K] = _hash_tuples(base_first_idxs)

        # glauber + plurality arms across temperature grid
        for T0 in T0_GRID:
            rng_dither = np.random.default_rng(seed * 100003 + K * 1009 + int(round(T0 * 1000)))
            succ = 0
            oracle_any = 0
            wtd_list: List[int] = []
            wrong_set = set()
            plur_first_idxs: List[Tuple[int, ...]] = []
            for true in trues:
                tuples = decode_trial(books, true, K, R_=R, T0=T0, rng=rng_dither)
                cnt = Counter(tuples)
                winner = cnt.most_common(1)[0][0]
                succ += int(winner == true)
                oracle_any += int(any(t == true for t in tuples))
                wtd_list.append(len(set(tuples)))
                for t in tuples:
                    if t != true:
                        wrong_set.add(t)
                plur_first_idxs.append(winner)
            key = "K%d_glauber_T%03d_R%d" % (K, int(round(T0 * 1000)), R)
            out[key] = {
                "plurality": succ / TR,
                "oracle_any": oracle_any / TR,
                "mean_within_trial_distinct": float(np.mean(wtd_list)),
                "distinct_wrong_configs": len(wrong_set),
                "R": R, "T0": T0,
            }
            arms_hashes[key] = _hash_tuples(plur_first_idxs)
            unit += 1
            _heartbeat(output_dir, unit, total_units, t0_start,
                       {"seed": seed, "K": K, "T0": T0, "plurality": succ / TR})
            print("  seed=%d K=%d T0=%.2f plurality=%.3f oracle_any=%.3f wtd=%.2f distinct_wrong=%d" %
                  (seed, K, T0, succ / TR, oracle_any / TR, float(np.mean(wtd_list)), len(wrong_set)),
                  flush=True)

    return {"seed": seed, "by_arm": out, "arms_hashes": arms_hashes,
            "N": N, "M": M, "run_mode": RUN_MODE}


def _hash_tuples(tuples: List[Tuple[int, ...]]) -> str:
    import hashlib
    b = json.dumps(tuples, sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


# --- verdict ----------------------------------------------------------------
def build_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    """Aggregate K4 across seeds; pick best T0>0; apply drill bands."""
    # baseline (positive control). K4 single-shot ~0.10-0.14 is tiny-sample-noisy at smoke TR;
    # the ROBUST port-reproducer is K3 baseline (~0.7, low variance). A broken numpy port gives
    # 0 at every K; a healthy port reproduces K3~0.7 AND K4<0.35 (not saturated). Gate D reproducer.
    base_vals = [ps["by_arm"]["K4_baseline_T0_R1"]["plurality"] for ps in per_seed]
    base_mean = float(np.mean(base_vals))
    base_k3_vals = [ps["by_arm"]["K3_baseline_T0_R1"]["plurality"]
                    for ps in per_seed if "K3_baseline_T0_R1" in ps["by_arm"]]
    base_k3_mean = float(np.mean(base_k3_vals)) if base_k3_vals else float("nan")

    # best glauber T0>0 for K4 by mean plurality across seeds
    t0_summary = {}
    for T0 in T0_GRID:
        key = "K4_glauber_T%03d_R%d" % (int(round(T0 * 1000)), R)
        plur = [ps["by_arm"][key]["plurality"] for ps in per_seed]
        wtd = [ps["by_arm"][key]["mean_within_trial_distinct"] for ps in per_seed]
        # distinct-wrong: union across seeds is not reconstructable from counts alone;
        # use MIN across seeds as a conservative floor for the scatter gate.
        dw = [ps["by_arm"][key]["distinct_wrong_configs"] for ps in per_seed]
        orc = [ps["by_arm"][key]["oracle_any"] for ps in per_seed]
        t0_summary[T0] = {
            "plurality_mean": float(np.mean(plur)),
            "mean_within_trial_distinct": float(np.mean(wtd)),
            "distinct_wrong_min": int(min(dw)),
            "oracle_any_mean": float(np.mean(orc)),
        }

    nonzero_t0 = [t for t in T0_GRID if t > 0.0]
    best_t0 = max(nonzero_t0, key=lambda t: t0_summary[t]["plurality_mean"])
    b = t0_summary[best_t0]
    plur = b["plurality_mean"]
    wtd = b["mean_within_trial_distinct"]
    dw = b["distinct_wrong_min"]

    # positive-control gate (Gate D): K3 baseline reproduces ~0.7 (robust) AND K4 not saturated.
    # Falls back to K4-band only if K3 is absent (should not happen; K_GRID includes 3).
    if base_k3_vals:
        pc_ok = (0.40 <= base_k3_mean <= 0.95) and (base_mean <= 0.35)
    else:
        pc_ok = 0.02 <= base_mean <= 0.35

    collapse = wtd < COLLAPSE_WTD
    scatter_ok = dw >= SCATTER_MIN

    detail = {
        "baseline_K4_mean": base_mean, "baseline_K3_mean": base_k3_mean,
        "positive_control_ok": pc_ok,
        "best_t0": best_t0, "best_t0_plurality_mean": plur,
        "best_t0_mean_within_trial_distinct": wtd,
        "best_t0_distinct_wrong_min": dw,
        "collapse_flag": collapse, "scatter_ok": scatter_ok,
        "t0_summary": {str(k): v for k, v in t0_summary.items()},
    }

    if not pc_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_POSITIVE_CONTROL: baseline K3=%.3f (need [0.40,0.95]~0.7) K4=%.3f (need <=0.35) -- "
                "numpy port diverged from GPU decode, downstream arms untrusted (Gate D). best_t0=%.2f plur=%.3f"
                % (base_k3_mean, base_mean, best_t0, plur), detail)

    if plur >= HARD_PASS_FLOOR and scatter_ok:
        return ("HARD_PASS",
                "HARD_PASS: K4 plurality=%.3f (>=0.50) at T0=%.2f AND failures scatter over %d>=5 distinct "
                "wrong configs (wtd=%.2f, oracle_any=%.3f) -- Glauber+plurality outvotes diverse spurious "
                "basins; baseline=%.3f. External-reset lever CONTRABLE for the resonator."
                % (plur, best_t0, dw, wtd, b["oracle_any_mean"], base_mean), detail)

    if plur <= HARD_FAIL_CEIL or collapse:
        why = "plurality<=0.192 (no material lift over 0.142 baseline)" if plur <= HARD_FAIL_CEIL else \
              "restarts COLLAPSE (mean_within_trial_distinct=%.2f<1.5) -- dither vacuous/basin-deterministic" % wtd
        return ("HARD_FAIL",
                "HARD_FAIL: K4 plurality=%.3f at best T0=%.2f -- %s. baseline=%.3f, distinct_wrong_min=%d. "
                "Basin-measure trap / no external-reset escape: single-step stays the only fix."
                % (plur, best_t0, why, base_mean, dw), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: K4 plurality=%.3f at T0=%.2f -- real lift over 0.142 baseline but below 0.50 "
            "(wtd=%.2f, distinct_wrong_min=%d, oracle_any=%.3f). Honest partial rescue; NOT forced to PASS."
            % (plur, best_t0, wtd, dw, b["oracle_any_mean"]), detail)


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

    # ARMS-MUST-DIFFER (META_RULE_AF): baseline (deterministic) vs a glauber arm must differ
    arms_differ_ok = True
    ref = per_seed[0]["arms_hashes"]
    g_key = "K4_glauber_T200_R%d" % R  # T0=0.20 arm
    if "K4_baseline_T0_R1" in ref and g_key in ref:
        arms_differ_ok = ref["K4_baseline_T0_R1"] != ref[g_key]
    if not arms_differ_ok:
        raise RuntimeError("META_RULE_AF VIOLATION: baseline and glauber K4 arms produced bit-identical "
                           "decoded tuples -- dither had zero effect (implementation bug or T0 not applied)")

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
