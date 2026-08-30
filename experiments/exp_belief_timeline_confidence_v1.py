"""DECAYING CONFIDENCE on the belief timeline (brain-fidelity deepening).

Research drill Q2: an attributed belief's VALUE persists (sample-and-hold, rep A) but its ACCESS /
CONFIDENCE decays with time-since-last-observation -- a MEASURED human signature (the here-and-now
dominates: Anderson, Garrod & Sanford 1983; Glenberg 1987 accessibility; the Temporal Context Model
contiguity kernel, Howard & Kahana 2002). A faithful belief timeline should therefore output not just
WHAT A believes but HOW confidently (freshly) A holds it -- which is what adjudicates conflicting
evidence and predicts revisability.

Mechanism (reuses hdlab.graded_temporal_context, the substrate's drifting temporal-context organ):
  confidence_A(X, T) = kernel(ctx(T), ctx(last_observed_event)) = Re<conj(ctx(T)), ctx(c)> / d
which is 1.0 at the moment of observation and DECAYS as the belief goes stale (more intervening
events). The VALUE is unchanged (rep A); only the confidence moves.

Can-fail: the confidence must be MONOTONE-DECREASING in staleness and PREDICT it (Spearman) far better
than an info-free twin that SHUFFLES which event was last observed (destroys the recency signal).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_confidence_v1")


def _kernel(gtc, t0, t1):
    import torch
    a, b = gtc.ctx(float(t0)), gtc.ctx(float(t1))
    return float(torch.real(torch.sum(torch.conj(a) * b))) / gtc.d


def run(d=1024, seed=20260830, k_max=12, n_inst=200, twin_seeds=200):
    from hdlab.graded_temporal_context import GradedTemporalContext
    gtc = GradedTemporalContext(d=d, seed=seed, horizon=float(k_max * 2))

    # confidence-vs-staleness curve: last observed at event-time c, query at c+s, s in 0..k_max.
    # Average over instances with different c (phase varies the crosstalk); event-time axis (staleness
    # measured in EVENTS -- the brain-faithful, event-segmented unit).
    rng = np.random.default_rng(seed)
    curve = {s: [] for s in range(k_max + 1)}
    for _ in range(n_inst):
        c = float(rng.integers(0, k_max))
        for s in range(k_max + 1):
            curve[s].append(_kernel(gtc, c + s, c))
    curve_mean = {s: float(np.mean(v)) for s, v in curve.items()}

    # monotone-decreasing check + Spearman(confidence, -staleness) on the TRUE mapping
    staleness, conf = [], []
    for s in range(k_max + 1):
        for v in curve[s]:
            staleness.append(s)
            conf.append(v)
    staleness, conf = np.array(staleness), np.array(conf)

    def spearman(x, y):
        rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
        rx = rx - rx.mean(); ry = ry - ry.mean()
        return float((rx * ry).sum() / (np.sqrt((rx**2).sum() * (ry**2).sum()) + 1e-12))

    rho_true = spearman(staleness, -conf)   # more stale -> lower confidence -> positive rho

    # info-free twin: shuffle the staleness labels against the confidences (destroys the mapping)
    twin_rhos = []
    for ts in range(twin_seeds):
        r = np.random.default_rng(1000 + ts)
        perm = r.permutation(len(staleness))
        twin_rhos.append(spearman(staleness[perm], -conf))
    twin_p95 = float(np.percentile(np.abs(twin_rhos), 95))

    # monotone fraction (consecutive decreases)
    means = [curve_mean[s] for s in range(k_max + 1)]
    mono = sum(1 for i in range(1, len(means)) if means[i] <= means[i - 1] + 1e-9) / (len(means) - 1)

    # USE: conflict resolution -- an OLD observation (stale, low conf) vs a RECENT one (high conf).
    # The recent source is held more confidently; a reader weights it. (The sample-and-hold already
    # picks the latest; confidence is what adjudicates when reliabilities differ.)
    c_old, c_new, T = 0.0, 8.0, 9.0
    conf_old, conf_new = _kernel(gtc, T, c_old), _kernel(gtc, T, c_new)

    metrics = {
        "d": d, "seed": seed, "k_max": k_max, "n_inst": n_inst,
        "confidence_vs_staleness": curve_mean,
        "spearman_true": rho_true, "twin_abs_rho_p95": twin_p95,
        "monotone_fraction": mono,
        "confidence_at_0_vs_kmax": [curve_mean[0], curve_mean[k_max]],
        "conflict_resolution": {"conf_old": conf_old, "conf_new": conf_new,
                                "recent_more_confident": conf_new > conf_old},
        "verdict": {"decays_with_staleness": rho_true > 0.5 and abs(rho_true) > twin_p95,
                    "fresh_is_confident": curve_mean[0] > curve_mean[k_max] + 0.1,
                    "monotone": mono >= 0.8},
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(n_inst=(40 if args.self_test else 200), twin_seeds=(40 if args.self_test else 200))
    if args.self_test:
        assert m["verdict"]["decays_with_staleness"] and m["verdict"]["fresh_is_confident"], m["verdict"]
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("DECAYING CONFIDENCE on the belief timeline (access decays, value persists)")
    print("=" * 78)
    print(f"  confidence at staleness 0 -> {m['k_max']} events: "
          f"{m['confidence_at_0_vs_kmax'][0]:.3f} -> {m['confidence_at_0_vs_kmax'][1]:.3f}")
    print(f"  Spearman(confidence, -staleness) = {m['spearman_true']:.3f}  vs twin |rho| p95 "
          f"{m['twin_abs_rho_p95']:.3f}")
    print(f"  monotone-decreasing fraction: {m['monotone_fraction']:.2f}")
    cr = m["conflict_resolution"]
    print(f"  conflict: recent source conf {cr['conf_new']:.3f} > old source conf {cr['conf_old']:.3f} "
          f"= {cr['recent_more_confident']}")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    print(f"  curve: {json.dumps({k: round(v,3) for k,v in m['confidence_vs_staleness'].items()})}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
