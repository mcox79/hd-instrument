"""edge_importance_bound_pair_consolidation_v2 -- HIGH-ALPHA regime.

Wave 2 ANCHOR 5 v2: v1 saturated at alpha=0.977 (M_OLD+M_RECENT=1000, N=1024;
ALL arms hit rec=1.000; discriminator never fired). v2 stresses capacity at
alpha=1.953 (N=512, same M_OLD=600, M_RECENT=400 -> alpha=1000/512=1.953)
per Skunkworks recommendation. This is the regime where Hopfield-style outer-
product memories begin to crosstalk-saturate, so any selectivity gain by
EDGE_GATED vs RANDOM is mechanism-driven, not capacity-driven.

NEW DISCIPLINES APPLIED (added today 2026-06-26):
  D1 -- Discriminator-must-survive-scale: smoke runs at FULL-N parameters
        (not reduced N). EDGE rec_old must differ from RANDOM rec_old by
        >= 0.05 at smoke, else regime still saturates -- STOP and route back.
  D2 -- Smoke-must-FIRE-discriminator: assert n_downscaled > 0 AND
        H_n_edges > 50 at smoke. Mechanism must actually trigger; cell not
        merely "runs without crashing".
  D3 -- No-silent-except: setup_substrate_and_populate_H + run_arm wrap their
        bodies; any exception is RECORDED to seed result with traceback and
        halts the seed (does not silently fall through).

PRE-REG BANDS (load-bearing):
  HARD_PASS:
    EDGE rec_RETRIEVED >= 0.85
    AND (RANDOM rec_UNRETRIEVED - EDGE rec_UNRETRIEVED) >= 0.10
        (EDGE_GATED selectively spares UNRETRIEVED less than RANDOM does,
         meaning EDGE_GATED is more aggressively pruning the unimportant)
        NOTE: equivalent expression with same direction-of-effect is
        EDGE rec_UNRETRIEVED < RANDOM rec_UNRETRIEVED by >= 0.10
    AND cor(E_derived, |W|) < 0.30

  HARD_FAIL:
    arms within 0.05 of each other on rec_RETRIEVED (saturation; regime
      still too easy -- bump alpha further next iteration)
    OR cor(E_derived, |W|) > 0.30 (fairness regression)
    OR n_downscaled == 0 (mechanism inert)
    OR H_n_edges < 50 (composite workload did not populate H)
    OR non-finite W_norm or rec values
    OR any caught exception from D3

  MIDDLE_BAND: in between PASS and FAIL bands.

ARMS (unchanged from v1):
  ARM_BASELINE_NO_DOWNSCALE -- rail; no pruning
  ARM_EDGE_GATED_DOWNSCALE  -- E+max_edge gate
  ARM_RANDOM_GATED          -- count-matched random pruning (selectivity ctrl)

ASCII-only; no unicode; no em-dashes; no emojis.
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)
from hdlab.edge_importance import EdgeImportance, HConfig, correlation_E_vs_magnitude


ANCHOR_NAME = "edge_importance_bound_pair_consolidation_v2"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# HIGH-ALPHA regime: N=512, M_OLD+M_RECENT=1000 -> alpha=1.953.
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
N_COMPOSITE_QUERIES_FULL = 3000
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
DOWNSCALE_SCALE = 0.20
E_THRESH = 2.0
H_THRESH = 3.0
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

# D1 discipline: smoke runs at FULL-N parameters (same N, M_OLD, M_RECENT),
# only seed/J/N_QUERIES count reduced. Discriminator must survive at scale.
if RUN_MODE == "smoke":
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = 1500   # half the J cycles
    USE_FRAC = USE_FRAC_FULL
    SEEDS = [7]
    N_QUERIES = 100
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = N_COMPOSITE_QUERIES_FULL
    USE_FRAC = USE_FRAC_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL

M_TOTAL = M_OLD + M_RECENT
ALPHA = M_TOTAL / N
N_USE = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_OLD)))

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"alpha={ALPHA:.3f},J_composite={N_COMPOSITE_QUERIES},"
    f"arity={COMPOSITE_ARITY},USE_FRAC={USE_FRAC},"
    f"DOWNSCALE_SCALE={DOWNSCALE_SCALE},E_THRESH={E_THRESH},"
    f"H_THRESH={H_THRESH},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation: bipolar keys/values
# ---------------------------------------------------------------------------
def generate_pairs(M_count: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    keys = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    return keys, values


def build_W_from_pairs(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return values.T @ keys


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def recall_subset(W: np.ndarray, keys: np.ndarray,
                  query_idx: np.ndarray, all_values: np.ndarray) -> float:
    N_dim = keys.shape[1]
    if len(query_idx) == 0:
        return float("nan")
    n_hits = 0
    for i in query_idx:
        pred = predict(W, keys[i])
        sims = all_values @ pred / float(N_dim)
        argmax = int(np.argmax(sims))
        if argmax == i:
            n_hits += 1
    return n_hits / float(len(query_idx))


# ---------------------------------------------------------------------------
# Composite-query workload
# ---------------------------------------------------------------------------
def composite_query_bundle(keys: np.ndarray, indices: np.ndarray) -> np.ndarray:
    bundle = np.sum(keys[indices], axis=0)
    out = np.sign(bundle)
    out[out == 0] = 1.0
    return out


def setup_substrate_and_populate_H(
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, EdgeImportance,
           np.ndarray, np.ndarray]:
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = HConfig(
        increment=1.0, decay_step=0.0, floor=0.0,
        e_thresh=E_THRESH, h_thresh=H_THRESH,
    )
    edge_graph = EdgeImportance(n_atoms=M_TOTAL, cfg=cfg)

    W = build_W_from_pairs(keys_old, values_old)

    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_OLD, size=N_USE, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_OLD, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    rng_q = np.random.RandomState(seed + 1117)
    for _q in range(N_COMPOSITE_QUERIES):
        triple = rng_q.choice(retrieved_idx, size=COMPOSITE_ARITY, replace=False)
        bundled_key = composite_query_bundle(all_keys, triple)
        _read = predict(W, bundled_key)
        edge_graph.increment_query(triple)
        edge_graph.decay_all()

    W = W + build_W_from_pairs(keys_rec, values_rec)

    return W, all_keys, all_values, edge_graph, retrieved_idx, unretrieved_idx


# ---------------------------------------------------------------------------
# Arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: Tuple) -> Dict:
    t0 = time.time()
    W_base, all_keys, all_values, edge_graph, retrieved_idx, unretrieved_idx = shared
    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    E_derived = edge_graph.derive_E_rowsum()
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_E_W = correlation_E_vs_magnitude(E_derived, atom_norms)

    n_downscaled = 0
    if arm_name == "ARM_BASELINE_NO_DOWNSCALE":
        n_downscaled = 0
    elif arm_name == "ARM_EDGE_GATED_DOWNSCALE":
        mask = edge_graph.downscale_mask(E_derived)
        prune_idx = np.where(mask)[0]
        n_downscaled = int(len(prune_idx))
        for idx in prune_idx:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_RANDOM_GATED":
        mask = edge_graph.downscale_mask(E_derived)
        n_target = int(np.sum(mask))
        if n_target <= 0:
            n_target = max(1, int(round(0.30 * M_TOTAL)))
        rng = np.random.RandomState(seed + 7777)
        rand_idx = rng.choice(M_TOTAL, size=n_target, replace=False)
        n_downscaled = n_target
        for idx in rand_idx:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    W_norm_post = float(np.linalg.norm(W))

    rng_eval = np.random.RandomState(seed + 503)
    n_q_ret = min(N_QUERIES, len(retrieved_idx))
    n_q_unret = min(N_QUERIES, len(unretrieved_idx))
    n_q_rec = min(N_QUERIES, M_RECENT)
    ret_query = rng_eval.choice(retrieved_idx, size=n_q_ret, replace=False)
    unret_query = rng_eval.choice(unretrieved_idx, size=n_q_unret, replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_q_rec, replace=False) + M_OLD

    recall_old_retrieved = recall_subset(W, all_keys, ret_query, all_values)
    recall_old_unretrieved = recall_subset(W, all_keys, unret_query, all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "recall_old_RETRIEVED": float(recall_old_retrieved),
        "recall_old_UNRETRIEVED": float(recall_old_unretrieved),
        "recall_recent": float(recall_recent),
        "W_norm_pre": W_norm_pre,
        "W_norm_post": W_norm_post,
        "cor_E_derived_magnitude": float(cor_E_W),
        "n_downscaled": int(n_downscaled),
        "downscale_frac_actual": float(n_downscaled) / float(M_TOTAL),
        "wall_s": float(elapsed),
        "E_derived_min": float(np.min(E_derived)),
        "E_derived_max": float(np.max(E_derived)),
        "E_derived_mean": float(np.mean(E_derived)),
        "H_n_edges": int(edge_graph.n_edges()),
        "H_total_mass": float(edge_graph.total_mass()),
        "n_retrieved": int(len(retrieved_idx)),
        "n_unretrieved": int(len(unretrieved_idx)),
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_composite_query_increments_H() -> bool:
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=10, cfg=cfg)
    triple = np.array([0, 3, 7])
    eg.increment_query(triple)
    assert eg.n_edges() == 3, f"3 edges expected; got {eg.n_edges()}"
    assert eg.total_mass() == 3.0
    return True


def _selftest_derived_E_separates_active_from_idle() -> bool:
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=20, cfg=cfg)
    active_pool = np.arange(0, 10)
    rng = np.random.RandomState(0)
    for _ in range(100):
        triple = rng.choice(active_pool, size=3, replace=False)
        eg.increment_query(triple)
    E = eg.derive_E_rowsum()
    assert np.mean(E[:10]) > 10.0, f"active E mean {np.mean(E[:10])} should be >> 10"
    assert np.all(E[10:] == 0.0), f"idle E should be 0; got {E[10:]}"
    return True


def _selftest_composite_bundle_decoding() -> bool:
    keys = np.random.RandomState(0).choice([-1.0, 1.0], size=(10, 32)).astype(np.float64)
    out = composite_query_bundle(keys, np.array([0, 3, 7]))
    assert out.shape == (32,)
    assert set(np.unique(out)).issubset({-1.0, 1.0})
    return True


def _selftest_fairness_orthogonality_synthetic() -> bool:
    rng = np.random.RandomState(0)
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=50, cfg=cfg)
    for i in range(10):
        for j in range(i + 1, 10):
            eg.increment_pair(i, j)
    E = eg.derive_E_rowsum()
    atom_norms = rng.rand(50)
    cor = correlation_E_vs_magnitude(E, atom_norms)
    assert abs(cor) < 0.30, f"orthogonality: |cor|={abs(cor):.3f} should be < 0.30"
    return True


def _selftest_alpha_regime_is_high() -> bool:
    """v2-specific: assert alpha is in the high-load regime where saturation
    should NOT occur trivially. v1 lesson: alpha=0.977 saturated."""
    assert ALPHA >= 1.5, (
        f"v2 must run at HIGH-alpha regime; got alpha={ALPHA:.3f} < 1.5. "
        f"N={N}, M_TOTAL={M_TOTAL}."
    )
    return True


def _instrumentation_selftest():
    _selftest_composite_query_increments_H()
    _selftest_derived_E_separates_active_from_idle()
    _selftest_composite_bundle_decoding()
    _selftest_fairness_orthogonality_synthetic()
    _selftest_alpha_regime_is_high()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J_comp={N_COMPOSITE_QUERIES}  "
        f"arity={COMPOSITE_ARITY}  N_USE={N_USE}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner (D3 no-silent-except: any failure recorded with traceback)
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] setup_substrate + populate H (J_comp={N_COMPOSITE_QUERIES}, "
        f"arity={COMPOSITE_ARITY}, N_USE={N_USE} of M_OLD={M_OLD})...",
        flush=True,
    )
    try:
        t_setup = time.time()
        shared = setup_substrate_and_populate_H(seed)
        print(
            f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s  "
            f"H_edges={shared[3].n_edges()}  H_mass={shared[3].total_mass():.0f}",
            flush=True,
        )
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed,
            "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
            "alpha": float(ALPHA), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "exception_phase": "setup",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    arms = []
    for arm_name in [
        "ARM_BASELINE_NO_DOWNSCALE",
        "ARM_EDGE_GATED_DOWNSCALE",
        "ARM_RANDOM_GATED",
    ]:
        try:
            out = run_arm(arm_name, seed, shared=shared)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] "
                f"rec_RETR={out['recall_old_RETRIEVED']:.3f} "
                f"rec_UNRETR={out['recall_old_UNRETRIEVED']:.3f} "
                f"rec_rec={out['recall_recent']:.3f} "
                f"cor_E_W={out['cor_E_derived_magnitude']:.3f} "
                f"n_down={out['n_downscaled']} ({out['downscale_frac_actual']:.2f}) "
                f"H_edges={out['H_n_edges']} "
                f"E_mean={out['E_derived_mean']:.2f} "
                f"wall={out['wall_s']:.1f}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} {arm_name}] ARM_EXCEPTION: {exc}\n{tb}", flush=True)
            arms.append({
                "arm_name": arm_name,
                "exception_msg": str(exc),
                "exception_traceback": tb,
            })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA), "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES), "n_use": int(N_USE),
        "downscale_scale": DOWNSCALE_SCALE,
        "e_thresh": E_THRESH, "h_thresh": H_THRESH,
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "composite_arity": COMPOSITE_ARITY,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (pre-reg bands; LOAD-BEARING)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # D3: any seed-level or arm-level exception is HARD_FAIL.
    for r in results:
        if "exception_phase" in r:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D3 caught {r['exception_phase']} exception "
                    f"seed={r['seed']}: {r['exception_msg']}")
        for a in r.get("arms", []):
            if "exception_msg" in a:
                return ("HARD_FAIL",
                        f"HARD_FAIL: D3 caught arm exception seed={r['seed']} "
                        f"arm={a['arm_name']}: {a['exception_msg']}")

    arm_names = ["ARM_BASELINE_NO_DOWNSCALE", "ARM_EDGE_GATED_DOWNSCALE",
                 "ARM_RANDOM_GATED"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec_retr = [a["recall_old_RETRIEVED"] for a in per]
        rec_unretr = [a["recall_old_UNRETRIEVED"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_E_derived_magnitude"] for a in per]
        wnorm = [a["W_norm_post"] for a in per]
        ndown = [a["n_downscaled"] for a in per]
        h_edges = [a["H_n_edges"] for a in per]
        agg[name] = {
            "mean_rec_RETRIEVED": float(np.mean(rec_retr)),
            "std_rec_RETRIEVED": float(np.std(rec_retr)),
            "cv_rec_RETRIEVED": float(np.std(rec_retr) / max(abs(np.mean(rec_retr)), 1e-9)),
            "mean_rec_UNRETRIEVED": float(np.mean(rec_unretr)),
            "mean_rec_recent": float(np.mean(rec_rec)),
            "mean_cor_E_W": float(np.mean(cor)),
            "mean_W_norm": float(np.mean(wnorm)),
            "mean_n_downscaled": float(np.mean(ndown)),
            "mean_H_n_edges": float(np.mean(h_edges)),
        }

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    e = agg["ARM_EDGE_GATED_DOWNSCALE"]
    rnd = agg["ARM_RANDOM_GATED"]
    base = agg["ARM_BASELINE_NO_DOWNSCALE"]

    delta_retrieved = e["mean_rec_RETRIEVED"] - rnd["mean_rec_RETRIEVED"]
    delta_unretrieved_random_minus_edge = (
        rnd["mean_rec_UNRETRIEVED"] - e["mean_rec_UNRETRIEVED"]
    )
    e_vs_base_retr = e["mean_rec_RETRIEVED"] - base["mean_rec_RETRIEVED"]

    summary = (
        f"alpha={ALPHA:.3f} "
        f"EDGE(retr={e['mean_rec_RETRIEVED']:.3f},"
        f"unretr={e['mean_rec_UNRETRIEVED']:.3f},"
        f"rec={e['mean_rec_recent']:.3f},"
        f"cor={e['mean_cor_E_W']:.3f},"
        f"cv={e['cv_rec_RETRIEVED']:.3f},"
        f"n_down={e['mean_n_downscaled']:.0f}); "
        f"RANDOM(retr={rnd['mean_rec_RETRIEVED']:.3f},"
        f"unretr={rnd['mean_rec_UNRETRIEVED']:.3f}); "
        f"BASE(retr={base['mean_rec_RETRIEVED']:.3f}); "
        f"d_E_vs_RND_retr={delta_retrieved:+.3f} "
        f"d_RND_minus_E_unretr={delta_unretrieved_random_minus_edge:+.3f} "
        f"d_E_vs_BASE_retr={e_vs_base_retr:+.3f}"
    )

    # ---- HARD_FAIL non-finite check ----
    for arm_name, a in agg.items():
        if not (np.isfinite(a["mean_W_norm"]) and
                np.isfinite(a["mean_rec_RETRIEVED"])):
            return ("HARD_FAIL",
                    f"HARD_FAIL: non-finite metrics in {arm_name}. {summary}")

    # ---- D2 mechanism-must-FIRE gate ----
    if e["mean_n_downscaled"] <= 0:
        return ("HARD_FAIL",
                f"HARD_FAIL: D2 EDGE_GATED mechanism inert (n_downscaled=0). "
                f"{summary}")
    if e["mean_H_n_edges"] < 50:
        return ("HARD_FAIL",
                f"HARD_FAIL: D2 H graph too sparse (n_edges={e['mean_H_n_edges']:.0f} "
                f"< 50). Composite-query workload did not populate H. {summary}")

    # ---- HARD_FAIL fairness gate (USER pre-reg) ----
    if e["mean_cor_E_W"] >= 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: fairness gate cor(E,|W|)={e['mean_cor_E_W']:.3f} "
                f">= 0.30. Edge-derived importance inherited magnitude "
                f"correlation. {summary}")

    # ---- HARD_FAIL saturation gate (arms within 0.05 on RETRIEVED) ----
    max_retr = max(base["mean_rec_RETRIEVED"], e["mean_rec_RETRIEVED"],
                   rnd["mean_rec_RETRIEVED"])
    min_retr = min(base["mean_rec_RETRIEVED"], e["mean_rec_RETRIEVED"],
                   rnd["mean_rec_RETRIEVED"])
    if (max_retr - min_retr) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: arms within 0.05 on rec_RETRIEVED "
                f"(spread={max_retr-min_retr:.3f}). Regime still too easy at "
                f"alpha={ALPHA:.3f}; bump alpha further. {summary}")

    # ---- HARD_PASS bands ----
    hp_cor = e["mean_cor_E_W"] < 0.30
    hp_recall_old = e["mean_rec_RETRIEVED"] >= 0.85
    # USER spec: EDGE rec_UNRETRIEVED < RANDOM rec_UNRETRIEVED by 0.10+
    # (EDGE selectively prunes the unimportant; UNRETRIEVED takes a deliberate hit)
    hp_selective_unretr = delta_unretrieved_random_minus_edge >= 0.10
    hp_mechanism_fired = (e["mean_n_downscaled"] > 0 and e["mean_H_n_edges"] >= 50)

    if all([hp_cor, hp_recall_old, hp_selective_unretr, hp_mechanism_fired]):
        return ("HARD_PASS",
                f"HARD_PASS: at alpha={ALPHA:.3f} EDGE_GATED preserves "
                f"RETRIEVED >= 0.85, selectively suppresses UNRETRIEVED by "
                f">= 0.10 vs RANDOM, cor<0.30, mechanism fired. {summary}")

    # MIDDLE_BAND: fairness held + RETRIEVED >= 0.65 + some selectivity signal
    if e["mean_cor_E_W"] < 0.50 and e["mean_rec_RETRIEVED"] >= 0.65 and \
       hp_mechanism_fired:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: fairness held + mechanism fired but PASS not "
                f"cleared. hp_checks=[cor={hp_cor},rec_old={hp_recall_old},"
                f"sel_unretr={hp_selective_unretr},fired={hp_mechanism_fired}]. "
                f"{summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: did not clear PASS or MIDDLE. "
            f"hp_checks=[cor={hp_cor},rec_old={hp_recall_old},"
            f"sel_unretr={hp_selective_unretr},fired={hp_mechanism_fired}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
# RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER (added 2026-06-27)
if __name__ == "__main__":
    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
                  "alpha": float(ALPHA), "J": N_COMPOSITE_QUERIES,
                  "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] edge_importance v2 N={N} alpha={ALPHA:.3f} "
            f"J_comp={N_COMPOSITE_QUERIES} arity={COMPOSITE_ARITY} "
            f"N_USE={N_USE} mode={RUN_MODE}...",
            flush=True,
        )
        result = run_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} N={N} M_OLD={M_OLD} M_RECENT={M_RECENT} "
            f"alpha={ALPHA:.3f} J_comp={N_COMPOSITE_QUERIES} "
            f"arity={COMPOSITE_ARITY} N_USE={N_USE} mode={RUN_MODE} "
            f"e_thresh={E_THRESH} h_thresh={H_THRESH}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA),
        "n_seeds": len(SEEDS), "n_queries": N_QUERIES, "n_use": int(N_USE),
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "composite_arity": COMPOSITE_ARITY,
        "downscale_scale": float(DOWNSCALE_SCALE),
        "e_thresh": float(E_THRESH), "h_thresh": float(H_THRESH),
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[metrics] written to {metrics_path}", flush=True)
