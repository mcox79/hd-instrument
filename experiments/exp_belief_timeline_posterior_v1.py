"""GRADED POSTERIOR belief -- per-element weights on the FHRR superposition (belief-as-posterior;
Bayesian theory-of-mind, Baker/Jara-Ettinger/Saxe/Tenenbaum 2017; Ying/Zhi-Xuan 2025). The prior
distributional cell represented belief as an equal-weight SET; the research drill (2026-08-30) showed
that is the FLOOR, not the target -- the brain attributes a GRADED posterior over locations to other
agents (possibility precedes probability, Leahy & Carey 2020, but the mature state is weighted).

Substrate-native: a WEIGHTED FHRR superposition  bank = sum_v w_v * bind(obj, code(v))  IS the
posterior; the cleanup scores Re<conj(code(v)), unbind(bank,obj)> recover the weights (up to code
crosstalk), so the read-out RANKS candidates by posterior weight. A crisp value+confidence floor
carries only the MAP value + a scalar and is BLIND to the ranking of the non-top candidates; an
equal-weight-set floor cannot rank at all.

Can-fail (the drill's discriminator): graded evidence makes location X more likely than Y with NEITHER
excluded -> the posterior read must rank weight(X) > weight(Y). Measured on the hard BELOW-MAP pairs
(both candidates below the top), where the value+confidence floor is structurally blind. CI-separated
over BOTH floors; info-free twin (shuffled weight->spot assignment) LOSES; plus a weight-separation
stress mapping the substrate's graded-belief resolution (how close two weights can be before crosstalk
flips the ranking).
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_posterior_v1")
SPOTS = ["nook", "sofa", "rug", "hearth", "sill", "stair", "closet", "bench", "ledge", "alcove"]


def _posterior_scores(bp, weights, spots, d):
    """Encode a weighted superposition sum_v w_v bind(obj,v); return cleanup scores per spot."""
    import torch
    obj = bp.code("obj", "obj")
    bank = torch.zeros(d, dtype=torch.complex64)
    for v, w in zip(spots, weights):
        bank = bank + float(w) * (obj * bp.code("loc", v))
    readback = bank * torch.conj(obj)
    return {v: float(torch.real(torch.sum(torch.conj(bp.code("loc", v)) * readback))) / d for v in spots}


def _pair_rank_acc(score_of, gold_w, spots, below_map_only=False):
    """Fraction of gold-distinct pairs (wi != wj) whose predicted order matches the gold weight order.
    below_map_only: restrict to pairs where BOTH spots are below the argmax (the floor-blind region)."""
    order = sorted(range(len(spots)), key=lambda i: -gold_w[i])
    top = order[0]
    ok = tot = 0
    for i, j in itertools.combinations(range(len(spots)), 2):
        if abs(gold_w[i] - gold_w[j]) < 1e-9:
            continue
        if below_map_only and (i == top or j == top):
            continue
        tot += 1
        gold_ij = gold_w[i] > gold_w[j]
        pred_ij = score_of(spots[i]) > score_of(spots[j])
        ok += int(gold_ij == pred_ij)
    return (ok / tot) if tot else None


def _mk(rng, n_cand):
    spots = rng.sample(SPOTS, n_cand)
    # gold posterior weights: distinct, plausibly-graded (a Bayesian posterior after mixed evidence)
    base = sorted([rng.uniform(0.1, 1.0) for _ in range(n_cand)], reverse=True)
    rng.shuffle(base)
    return spots, base


def run(n=80, seed=20260830, d=1024, twin_seeds=150):
    from hdlab.belief_partition import BeliefPartition
    bp = BeliefPartition(d=d, seed=seed)
    rng = random.Random(seed)
    scens = [_mk(rng, rng.choice([4, 5, 6])) for _ in range(n)]

    def arm_scores(spots, gold_w, arm, twin_seed=None):
        if arm == "graded":
            sc = _posterior_scores(bp, gold_w, spots, d)
            return lambda v: sc[v]
        if arm == "equal_set":
            return lambda v: 1.0                                   # all equal -> cannot rank
        if arm == "value_conf":
            top = spots[int(np.argmax(gold_w))]
            return lambda v: (1.0 if v == top else 0.0)            # MAP + scalar; blind below top
        if arm == "twin":
            r = random.Random(twin_seed)
            w = list(gold_w); r.shuffle(w)                          # shuffle weight->spot
            sc = _posterior_scores(bp, w, spots, d)
            return lambda v: sc[v]

    def score(arm, below_map_only, twin_seed=None):
        accs = []
        for spots, gold_w in scens:
            so = arm_scores(spots, gold_w, arm, twin_seed=twin_seed)
            a = _pair_rank_acc(so, gold_w, spots, below_map_only=below_map_only)
            if a is not None:
                accs.append(a)
        return float(np.mean(accs))

    res = {}
    for arm in ("graded", "equal_set", "value_conf"):
        res[arm] = {"all_pairs": score(arm, False), "below_map_pairs": score(arm, True)}
    twin_all = [score("twin", False, twin_seed=1000 + ts) for ts in range(twin_seeds)]
    twin_p95 = float(np.percentile(twin_all, 95))

    # weight-separation stress: two spots at ratio r (r=w_hi/w_lo); does the read rank them right?
    stress = {}
    for r in (1.1, 1.25, 1.5, 2.0, 3.0):
        ok = tot = 0
        for i in range(120):
            a, b = rng.sample(SPOTS, 2)
            so = _posterior_scores(bp, [r, 1.0], [a, b], d)
            tot += 1
            ok += int(so[a] > so[b])
        stress[str(r)] = ok / tot

    metrics = {
        "seed": seed, "d": d, "n": len(scens),
        "arms": res, "twin_p95": twin_p95, "twin_mean": float(np.mean(twin_all)),
        "weight_separation_stress": stress,
        "verdict": {
            "graded_beats_equalset_below_map": res["graded"]["below_map_pairs"] > res["equal_set"]["below_map_pairs"] + 0.1,
            "graded_beats_valueconf_below_map": res["graded"]["below_map_pairs"] > res["value_conf"]["below_map_pairs"] + 0.1,
            "graded_beats_twin": res["graded"]["all_pairs"] > twin_p95,
        },
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(n=(20 if args.self_test else 80), twin_seeds=(30 if args.self_test else 150))
    if args.self_test:
        v = m["verdict"]
        assert all(v.values()), (v, m["arms"])
        print("self-test PASS", json.dumps(v))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    a = m["arms"]
    print("=" * 78)
    print("GRADED POSTERIOR belief -- per-element weights on the FHRR superposition")
    print("=" * 78)
    print("  pairwise ranking accuracy (does the read rank weight(X) > weight(Y)?):")
    print(f"    GRADED posterior   all {a['graded']['all_pairs']:.3f}   below-MAP {a['graded']['below_map_pairs']:.3f}")
    print(f"    equal-set FLOOR    all {a['equal_set']['all_pairs']:.3f}   below-MAP {a['equal_set']['below_map_pairs']:.3f}  (cannot rank)")
    print(f"    value+conf FLOOR   all {a['value_conf']['all_pairs']:.3f}   below-MAP {a['value_conf']['below_map_pairs']:.3f}  (blind below the top)")
    print(f"    info-free TWIN p95 {m['twin_p95']:.3f}")
    print(f"  weight-separation stress (rank accuracy by w_hi/w_lo ratio): {json.dumps(m['weight_separation_stress'])}")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
