"""RECENCY -> PRECISION unification (research drill Q4): confidence and the posterior are not two
channels -- they are ONE quantity, the posterior's PRECISION (Pouget/Drugowitsch/Kepecs 2016). A
belief's recency (time since last observation) should act as the precision of its graded posterior:
a FRESH belief is a SHARP posterior (low entropy, confident ranking); a STALE belief FLATTENS toward
uniform (high entropy, uncertain ranking) -- you keep the gist, lose the fine structure. Confidence is
then DERIVED from posterior entropy, retiring the free-floating scalar the confidence cell used.

Mechanism (substrate-native): recency beta(T) = kernel(ctx(T), ctx(c)) in [0,1] from the drifting
temporal-context organ; the effective posterior tempers the stored weights w_v^beta (renormalised):
beta=1 -> w_v (sharp); beta->0 -> uniform (flat). entropy(T) = H(effective posterior).

Can-fail: entropy must RISE monotonically with staleness (the belief becomes uncertain) and confidence
= 1 - normalised-entropy must FALL -- a signature a FIXED-precision floor (posterior never flattens)
structurally cannot produce (its entropy is flat in staleness). Info-free twin (shuffled staleness)
LOSES. Below-MAP ranking degrades GRACEFULLY toward chance as the belief goes stale (faithful: fine
structure is lost), where the fixed floor falsely claims permanent certainty.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_precision_v1")


def _temper(w, beta):
    """Effective posterior = normalised w^beta. beta=1 -> w; beta->0 -> uniform."""
    w = np.asarray(w, float)
    beta = max(0.0, min(1.0, beta))
    p = np.power(w, beta)
    return p / p.sum()


def _entropy(p):
    p = np.asarray(p, float)
    p = p[p > 1e-12]
    h = -(p * np.log(p)).sum()
    return float(h / np.log(len(p))) if len(p) > 1 else 0.0    # normalised to [0,1]


def run(d=1024, seed=20260830, k_max=12, n_inst=200, twin_seeds=200):
    from hdlab.graded_temporal_context import GradedTemporalContext
    import torch
    gtc = GradedTemporalContext(d=d, seed=seed, horizon=float(k_max * 2))
    rng = np.random.default_rng(seed)

    def beta(t0, t1):
        a, b = gtc.ctx(float(t0)), gtc.ctx(float(t1))
        return max(0.0, float(torch.real(torch.sum(torch.conj(a) * b))) / d)

    # for each instance: a stored posterior over n spots set at time c; query at c+s (s=staleness)
    ent_unified = {s: [] for s in range(k_max + 1)}
    ent_fixed = {s: [] for s in range(k_max + 1)}
    conf_unified = {s: [] for s in range(k_max + 1)}
    for _ in range(n_inst):
        n = int(rng.integers(4, 7))
        w = rng.uniform(0.1, 1.0, size=n)
        w = w / w.sum()
        c = float(rng.integers(0, k_max))
        for s in range(k_max + 1):
            bt = beta(c + s, c)
            eff = _temper(w, bt)
            ent_unified[s].append(_entropy(eff))
            ent_fixed[s].append(_entropy(w))               # fixed precision: never flattens
            conf_unified[s].append(1.0 - _entropy(eff))
    eu = {s: float(np.mean(v)) for s, v in ent_unified.items()}
    ef = {s: float(np.mean(v)) for s, v in ent_fixed.items()}
    cu = {s: float(np.mean(v)) for s, v in conf_unified.items()}

    def spearman(x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        rx = np.argsort(np.argsort(x)).astype(float); ry = np.argsort(np.argsort(y)).astype(float)
        rx -= rx.mean(); ry -= ry.mean()
        return float((rx * ry).sum() / (np.sqrt((rx**2).sum() * (ry**2).sum()) + 1e-12))

    stal = [s for s in range(k_max + 1) for _ in ent_unified[s]]
    ent_u_flat = [v for s in range(k_max + 1) for v in ent_unified[s]]
    ent_f_flat = [v for s in range(k_max + 1) for v in ent_fixed[s]]
    rho_unified = spearman(stal, ent_u_flat)       # entropy rises with staleness -> positive
    rho_fixed = spearman(stal, ent_f_flat)         # fixed -> ~0 (flat)

    twin_rhos = []
    for ts in range(twin_seeds):
        r = np.random.default_rng(5000 + ts)
        perm = r.permutation(len(stal))
        twin_rhos.append(spearman(np.array(stal)[perm], ent_u_flat))
    twin_p95 = float(np.percentile(np.abs(twin_rhos), 95))

    # confidence-from-entropy tracks the independent recency signal (they are unified now)
    recency = [beta(c := s, 0) for s in range(k_max + 1)]  # kernel(ctx(s),ctx(0))
    conf_curve = [cu[s] for s in range(k_max + 1)]
    rho_conf_recency = spearman(recency, conf_curve)

    metrics = {
        "d": d, "seed": seed, "k_max": k_max, "n_inst": n_inst,
        "entropy_unified_curve": eu, "entropy_fixed_curve": ef, "confidence_unified_curve": cu,
        "spearman_entropy_staleness_unified": rho_unified,
        "spearman_entropy_staleness_fixed": rho_fixed,
        "twin_abs_rho_p95": twin_p95,
        "spearman_confidence_recency": rho_conf_recency,
        "entropy_fresh_vs_stale": [eu[0], eu[k_max]],
        "verdict": {
            "entropy_rises_with_staleness": rho_unified > 0.5 and abs(rho_unified) > twin_p95,
            "fixed_precision_floor_is_flat": abs(rho_fixed) < 0.1,
            "confidence_unified_with_recency": rho_conf_recency > 0.9,
        },
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(n_inst=(40 if args.self_test else 200), twin_seeds=(40 if args.self_test else 200))
    if args.self_test:
        v = m["verdict"]
        assert all(v.values()), (v, m["spearman_entropy_staleness_unified"], m["spearman_entropy_staleness_fixed"])
        print("self-test PASS", json.dumps(v))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("RECENCY -> PRECISION: a stale belief FLATTENS its posterior (confidence = entropy)")
    print("=" * 78)
    print(f"  posterior entropy fresh -> stale: {m['entropy_fresh_vs_stale'][0]:.3f} -> "
          f"{m['entropy_fresh_vs_stale'][1]:.3f}  (rises = belief gets uncertain)")
    print(f"  Spearman(entropy, staleness)  UNIFIED {m['spearman_entropy_staleness_unified']:.3f}  "
          f"vs FIXED-precision floor {m['spearman_entropy_staleness_fixed']:.3f}  (twin |rho| p95 {m['twin_abs_rho_p95']:.3f})")
    print(f"  confidence(=1-entropy) tracks the recency signal: Spearman {m['spearman_confidence_recency']:.3f} "
          f"(the two channels are now ONE)")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
