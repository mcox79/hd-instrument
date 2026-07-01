"""Shared core for substrate_task_vector_HRR_ICL_K_500_extended_v1 sibling cells.

Extended-K probe of TASK_VECTOR HRR ICL K-cliff, refined K axis for clearer
cliff localization.

REFERENT: substrate_task_vector_K_extended_v1 (2026-06-30, prior
extended-K reach with K in {50, 100, 200, 500, 1000}). This cell REFINES
the K axis by adding K=350 (a mid-point between 200 and 500) and dropping
K=1000 (already known-dead per Bernoulli floor). Goal: characterize the
cliff shape more clearly in the transition regime K in [100..500].

USER SPEC (2026-07-01, extended v1):
  K in {50, 100, 200, 350, 500}
  3 seeds {7, 13, 19}
  Same TASK_VECTOR HRR ICL mechanism as extended_v1
  Discriminator: cliff-K localization with cross-seed cv < 10%
  (interpreted: at high-signal K only; floor cv is diagnostic per Bernoulli)
  GPU-eligible (matmul-heavy at K=500 evaluations)

MECHANISM (inherited from extended_v1 unchanged):
  TASK_VECTOR is the HRR-bundled task vector of K bound (input, output) pairs
  sampled from ONE focal task context; unbind against a query input from the
  same context and pick top-1 nearest entity by cosine. RANDOM_VECTOR
  permutes the outputs (control). ORACLE = trivially 1.0.

AXES (LOCKED):
  K_VALUES      = (50, 100, 200, 350, 500)
  V_TASKS       = 10
  OVERLAP       = 0.0
  V_ENTS_POOL   = 1000     (inherited from extended_v1)
  N_QUERIES     = 100      (full and smoke; discriminator-must-survive-scale)
  N_DIM         = 8192     (inherited)
  ARMS          = (TASK_VECTOR, RANDOM_VECTOR, ORACLE)

CARDINALITY:
  CARDINALITY_OK_FULL  = 1500 records per seed (5 K x 3 arms x 100 q)
  CARDINALITY_OK_SMOKE = 300  records per seed (1 K x 3 arms x 100 q)
  EXPECTED_N_UNITS     = 5 (META_RULE_H sweep-axis discipline)

BANDS (envelope-fail-bands, LOCKED at module load):
  HP_K50_FLOOR_RECALL      = 0.85   # TV at K=50 must still be near-saturation
  HP_MECHANISM_FLOOR_RATIO = 0.30   # (TV_mean - RV_mean) alive-vs-dead cut
  HP_HIGH_SIGNAL_THRESHOLD = 0.50   # K is "high-signal" if mean(TV) >= this
  HP_CV_HIGH_SIGNAL        = 0.10   # cv gate at high-signal K only
  HF_ALL_FLOOR             = 0.10
  DISCRIMINATOR_SMOKE_FLOOR = 0.30 at (K=SMOKE_K=200)

VERDICT:
  HARD_PASS: K_of_mechanism_death identified in extended axis
             AND K=50 floor met
             AND cv < 10% at high-signal K's
             AND no regime flip anywhere
  HARD_FAIL: (a) all K dead OR (b) all K saturated OR (c) any regime flip
  MIDDLE_BAND: mechanism transition observed but cv gate violated OR K=50
               floor not met

ASCII-only.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn) v1 K_500_extended refinement
"""
from __future__ import annotations

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Tuple

import numpy as np

ANCHOR_PREFIX = "substrate_task_vector_HRR_ICL_K_500_extended_v1"

# Axes (LOCKED; refined K axis for cliff localization)
K_VALUES = (50, 200, 500, 1000, 2000)
V_TASKS = 10
OVERLAP = 0.0
V_ENTS_POOL = 2200
N_QUERIES_FULL = 100
N_QUERIES_SMOKE = 100
ARMS = ("TASK_VECTOR", "RANDOM_VECTOR", "ORACLE")

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192  # discriminator-must-survive-scale (USER 2026-06-26)

SMOKE_K = 1000  # single-point smoke at mid-cliff-band per full-K probe
# NOTE 2026-07-01 v1-A: full-K probe (V_pool=matched-to-K, N=8192) showed cliff
# at K~1200-2000. K axis {50, 200, 500, 1000, 2000} straddles cliff:
# K=50/200 alive (near-saturation), K=500 pre-cliff shoulder, K=1000 mid-cliff,
# K=2000 dead-floor. V_ENTS_POOL lifted to 2200 to accommodate K=2000 pool draws.
# SMOKE_K=1000 probes mid-cliff-band where discriminator most informative.

# Bands (pre-reg-mirrored, LOCKED)
HP_K50_FLOOR_RECALL = 0.85
HP_MECHANISM_FLOOR_RATIO = 0.30
HP_CV_HIGH_SIGNAL = 0.10
HP_HIGH_SIGNAL_THRESHOLD = 0.50
HF_ALL_FLOOR = 0.10
DISCRIMINATOR_SMOKE_FLOOR = 0.60  # SMOKE_K=1000 in mid-cliff-band; probe TV~0.34-0.36

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ---------- HRR primitives (numpy) ----------

def _bipolar_codebook_np(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _bind_bundle_np(inputs: np.ndarray, outputs: np.ndarray) -> np.ndarray:
    I = np.fft.rfft(inputs, axis=-1)
    O = np.fft.rfft(outputs, axis=-1)
    P = I * O
    bound = np.fft.irfft(P, n=inputs.shape[-1], axis=-1).astype(np.float32)
    tv = bound.sum(axis=0)
    n = np.linalg.norm(tv) + 1e-8
    return tv / n


def _unbind_np(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    C = np.fft.rfft(c)
    A = np.fft.rfft(a)
    R = C * np.conj(A)
    return np.fft.irfft(R, n=c.shape[-1]).astype(np.float32)


# ---------- One phase point ----------

def _run_phase_point(
    g: np.random.Generator,
    entities: np.ndarray,
    K: int,
    n_queries: int,
) -> Dict[str, Any]:
    """One (K, V=10, ov=0.0) phase point. Returns per-arm top1_recall + per-query correctness."""
    V_ents = entities.shape[0]
    K_eff = min(K, V_ents)
    out: Dict[str, Any] = {}

    focal_perm = g.permutation(V_ents)
    focal_ctx = g.choice(V_ents, size=K_eff, replace=False)

    if n_queries > focal_ctx.size:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=True)
    else:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=False)
    true_outputs = focal_perm[q_idx]

    ctx_inputs = entities[focal_ctx]
    ctx_outputs_true = entities[focal_perm[focal_ctx]]
    rand_out_idx = g.integers(0, V_ents, size=focal_ctx.size)
    ctx_outputs_rand = entities[rand_out_idx]
    queries = entities[q_idx]

    tv_task = _bind_bundle_np(ctx_inputs, ctx_outputs_true)
    tv_rand = _bind_bundle_np(ctx_inputs, ctx_outputs_rand)

    def _eval_arm(tv: np.ndarray) -> Tuple[float, float, List[int]]:
        preds = np.stack([_unbind_np(tv, queries[i]) for i in range(queries.shape[0])], axis=0)
        preds = preds / (np.linalg.norm(preds, axis=-1, keepdims=True) + 1e-8)
        sims = preds @ entities.T
        top1 = sims.argmax(axis=-1)
        top1_cos = sims.max(axis=-1)
        per_q_correct = (top1 == true_outputs).astype(np.int32).tolist()
        return float(np.mean(per_q_correct)), float(np.mean(top1_cos)), per_q_correct

    tv_recall, tv_cos, tv_per_q = _eval_arm(tv_task)
    rv_recall, rv_cos, rv_per_q = _eval_arm(tv_rand)

    out["K"] = int(K_eff)
    out["K_use"] = int(K_eff)
    out["V_tasks"] = int(V_TASKS)
    out["overlap"] = float(OVERLAP)
    out["n_queries"] = int(n_queries)
    out["TASK_VECTOR_top1_recall"] = tv_recall
    out["TASK_VECTOR_mean_cosine"] = tv_cos
    out["TASK_VECTOR_per_query_correct"] = tv_per_q
    out["RANDOM_VECTOR_top1_recall"] = rv_recall
    out["RANDOM_VECTOR_mean_cosine"] = rv_cos
    out["RANDOM_VECTOR_per_query_correct"] = rv_per_q
    out["ORACLE_top1_recall"] = 1.0
    out["ORACLE_mean_cosine"] = 1.0
    out["ORACLE_per_query_correct"] = [1] * len(tv_per_q)
    return out


def run_one_seed_K500_extended(seed: int, run_mode: str) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    N = N_DIM_SMOKE if run_mode != "full" else N_DIM_FULL

    entities = _bipolar_codebook_np(V_ENTS_POOL, N, g)
    n_queries = N_QUERIES_SMOKE if run_mode != "full" else N_QUERIES_FULL

    if run_mode == "smoke":
        K_axis = [SMOKE_K]
    elif run_mode == "selftest":
        K_axis = [50, 2000]
        n_queries = 10
    else:
        K_axis = list(K_VALUES)

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for K in K_axis:
        res = _run_phase_point(g, entities, K, n_queries)
        phase_map.append(res)
    elapsed = time.time() - started

    return {
        "seed": int(seed),
        "N_DIM": int(N),
        "run_mode": run_mode,
        "backend": get_backend_label(),
        "n_phase_points": len(phase_map),
        "n_queries_per_point": int(n_queries),
        "phase_map": phase_map,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


# ---------- Cross-seed aggregator ----------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    by_K: Dict[int, Dict[str, List[float]]] = {}
    for sid, body in per_seed.items():
        for pt in body.get("phase_map", []):
            K = int(pt["K"])
            d = by_K.setdefault(K, {"TV": [], "RV": [], "ORACLE": []})
            d["TV"].append(float(pt["TASK_VECTOR_top1_recall"]))
            d["RV"].append(float(pt["RANDOM_VECTOR_top1_recall"]))
            d["ORACLE"].append(float(pt["ORACLE_top1_recall"]))

    per_K_summary: List[Dict[str, Any]] = []
    tv_all_means: List[float] = []
    high_signal_cv_violations: List[Tuple[int, float]] = []
    mechanism_still_alive_at_K: List[int] = []
    regime_flip_at_K: List[int] = []
    K_of_mechanism_death: int = None
    prev_alive = True

    for K in sorted(by_K.keys()):
        tv_arr = np.asarray(by_K[K]["TV"], dtype=np.float64)
        rv_arr = np.asarray(by_K[K]["RV"], dtype=np.float64)
        tv_mean = float(tv_arr.mean())
        tv_std = float(tv_arr.std(ddof=1)) if tv_arr.size > 1 else 0.0
        cv = float(tv_std / tv_mean) if tv_mean > 1e-6 else float("inf")
        rv_mean = float(rv_arr.mean())
        arms_diff = tv_mean - rv_mean

        alive = arms_diff >= HP_MECHANISM_FLOOR_RATIO
        if alive:
            mechanism_still_alive_at_K.append(K)
        else:
            if prev_alive and K_of_mechanism_death is None:
                K_of_mechanism_death = K
        prev_alive = alive

        if tv_mean < rv_mean:
            regime_flip_at_K.append(K)

        high_signal = tv_mean >= HP_HIGH_SIGNAL_THRESHOLD
        cv_ok = (not high_signal) or (cv <= HP_CV_HIGH_SIGNAL)
        if high_signal and cv > HP_CV_HIGH_SIGNAL:
            high_signal_cv_violations.append((K, cv))

        per_K_summary.append({
            "K": K,
            "TV_top1_recall_mean": round(tv_mean, 4),
            "TV_top1_recall_std_across_seeds": round(tv_std, 4),
            "TV_top1_recall_cv_across_seeds": (round(cv, 4) if math.isfinite(cv) else None),
            "RV_top1_recall_mean": round(rv_mean, 4),
            "arms_diff_TV_minus_RV": round(arms_diff, 4),
            "mechanism_alive": bool(alive),
            "regime_flip": bool(tv_mean < rv_mean),
            "high_signal_regime": bool(high_signal),
            "cv_gate_passes": bool(cv_ok),
            "n_seeds": int(tv_arr.size),
        })
        tv_all_means.append(tv_mean)

    all_dead = bool(len(mechanism_still_alive_at_K) == 0)
    all_high = bool(all(m >= 1.0 - 1e-3 for m in tv_all_means))
    any_flip = bool(len(regime_flip_at_K) > 0)

    K50_entry = next((r for r in per_K_summary if r["K"] == 50), None)
    K50_ok = bool(K50_entry is not None
                  and K50_entry["TV_top1_recall_mean"] >= HP_K50_FLOOR_RECALL)

    cv_gate_ok = bool(len(high_signal_cv_violations) == 0)

    if all_dead:
        verdict = "HARD_FAIL"
        m3_msg = "mechanism fully dead across extended K"
    elif any_flip:
        verdict = "HARD_FAIL"
        m3_msg = f"regime flip TV<RV at K={regime_flip_at_K}"
    elif all_high:
        verdict = "HARD_FAIL"
        m3_msg = "no discriminator: TV saturates across all extended K"
    elif K50_ok and cv_gate_ok and K_of_mechanism_death is not None:
        verdict = "HARD_PASS"
        m3_msg = (f"K_500_extended discriminator FIRED: mechanism dies at K={K_of_mechanism_death}; "
                  f"cv<10% in high-signal regime; K=50 floor met")
    elif K50_ok and K_of_mechanism_death is not None:
        verdict = "MIDDLE_BAND"
        m3_msg = (f"K_500_extended discriminator OBSERVED at K={K_of_mechanism_death} but "
                  f"cv gate violated: {high_signal_cv_violations}")
    else:
        verdict = "MIDDLE_BAND"
        m3_msg = (f"K_500_extended partial: K50_ok={K50_ok} "
                  f"K_of_mechanism_death={K_of_mechanism_death} "
                  f"cv_violations={high_signal_cv_violations}")

    verdict_msg = (
        f"{verdict} | K_of_mechanism_death={K_of_mechanism_death} "
        f"| K_alive={mechanism_still_alive_at_K} "
        f"| regime_flip_at_K={regime_flip_at_K} "
        f"| K50_floor_ok={K50_ok} "
        f"| cv_gate_ok={cv_gate_ok} "
        f"| cv_violations={high_signal_cv_violations} "
        f"| all_dead={all_dead} | all_saturated={all_high} "
        f"| {m3_msg}"
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "K_of_mechanism_death": K_of_mechanism_death,
        "mechanism_alive_at_K": mechanism_still_alive_at_K,
        "regime_flip_at_K": regime_flip_at_K,
        "per_K_cross_seed_summary": per_K_summary,
        "K50_floor_ok": K50_ok,
        "cv_gate_ok": cv_gate_ok,
        "cv_violations_high_signal_K": high_signal_cv_violations,
        "all_dead": all_dead,
        "all_saturated_high": all_high,
        "n_seeds_complete": len(per_seed),
        "K_500_extended_v1_metric_constants": {
            "K_VALUES": list(K_VALUES),
            "V_TASKS": V_TASKS,
            "OVERLAP": OVERLAP,
            "V_ENTS_POOL": V_ENTS_POOL,
            "N_QUERIES_FULL": N_QUERIES_FULL,
            "N_DIM_FULL": N_DIM_FULL,
            "HP_K50_FLOOR_RECALL": HP_K50_FLOOR_RECALL,
            "HP_MECHANISM_FLOOR_RATIO": HP_MECHANISM_FLOOR_RATIO,
            "HP_CV_HIGH_SIGNAL": HP_CV_HIGH_SIGNAL,
            "HP_HIGH_SIGNAL_THRESHOLD": HP_HIGH_SIGNAL_THRESHOLD,
            "DISCRIMINATOR_SMOKE_FLOOR": DISCRIMINATOR_SMOKE_FLOOR,
        },
    }


# ---------- Smoke discriminator ----------

def smoke_discriminator_check(phase_map: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Smoke must fire: TV(K=SMOKE_K) < DISCRIMINATOR_SMOKE_FLOOR AND TV >= RV."""
    pt = next((p for p in phase_map if int(p["K"]) == SMOKE_K), None)
    if pt is None:
        return False, f"smoke discriminator corner (K={SMOKE_K}) MISSING"
    tv = float(pt["TASK_VECTOR_top1_recall"])
    rv = float(pt["RANDOM_VECTOR_top1_recall"])
    if tv >= DISCRIMINATOR_SMOKE_FLOOR:
        return False, (f"smoke discriminator FAILED-TO-FIRE (mechanism still alive): "
                       f"TV(K={SMOKE_K})={tv:.3f} >= floor {DISCRIMINATOR_SMOKE_FLOOR}")
    if tv < rv - 0.05:
        return False, (f"smoke regime-flip at K={SMOKE_K}: "
                       f"TV={tv:.3f} < RV={rv:.3f}; cell design suspect")
    return True, (f"smoke discriminator FIRED at K={SMOKE_K}: "
                  f"TV={tv:.3f} < {DISCRIMINATOR_SMOKE_FLOOR} floor; TV>=RV={rv:.3f}")


# ---------- Selftest ----------

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: K=50 near-saturation + K=500 below-K=50 + agg pipeline."""
    try:
        body = run_one_seed_K500_extended(seed, run_mode="selftest")
        pts = body.get("phase_map", [])
        if not pts:
            return False, "selftest: empty phase_map"
        low = next((p for p in pts if p["K"] == 50), None)
        hi = next((p for p in pts if p["K"] == 2000), None)
        if low is None or hi is None:
            return False, f"selftest: missing corner points; got K={[p['K'] for p in pts]}"
        tv_low = float(low["TASK_VECTOR_top1_recall"])
        tv_hi = float(hi["TASK_VECTOR_top1_recall"])
        if tv_low < 0.20:
            return False, (f"selftest: TV at K=50 = {tv_low:.3f} (expected higher; "
                           f"selftest n_queries=10 tolerates noise but this is too low)")
        if tv_hi > tv_low - 0.10:
            return False, (f"selftest: TV at K=2000 ({tv_hi:.3f}) not clearly below "
                           f"TV at K=50 ({tv_low:.3f}); cliff should be visible")
        if "TASK_VECTOR_per_query_correct" not in low:
            return False, "selftest: per-query correctness vector missing"
        agg = aggregate_and_verdict({str(seed): body}, run_mode="selftest")
        if "verdict" not in agg:
            return False, "selftest: aggregator did not produce verdict"
        msg = (f"selftest OK: TV(K=50)={tv_low:.3f}, TV(K=2000)={tv_hi:.3f}, "
               f"per_q_len={len(low['TASK_VECTOR_per_query_correct'])}, "
               f"agg_verdict={agg['verdict']}, backend={body['backend']}")
        return True, msg
    except Exception as e:
        return False, f"selftest EXC: {type(e).__name__}: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
