"""DISTRIBUTIONAL / PARTIAL belief -- the belief is a SET the agent considers possible, not a crisp
point (brain-fidelity deepening; the belief-as-posterior / Bayesian-brain view). Under partial
observation (an agent sees an object enter a region but not exactly where, or is occluded), a
faithful reader attributes a DISTRIBUTION over candidate locations and NARROWS it as the agent rules
places out over time. A crisp sample-and-hold cannot represent "A knows it is in one of these two."

Substrate-native: an FHRR SUPERPOSITION of candidate (obj,value) pairs IS the substrate's belief
distribution, read out by `hdlab.situation_model_accumulate.cleanup_set` (CA3 context-cued set
reactivation; Nakazawa 2002; Bramao 2022). A crisp `cleanup_argmax` read collapses the distribution
to one value -- that is the FLOOR that cannot represent uncertainty.

Scenario: A sees the object enter a region of N candidate spots (belief = uniform over N); then A
observes a sequence of EXCLUSIONS ("not here") that shrink the set over time; the true location is
hidden. Query the belief SET at each time. F1(predicted set, gold set): the distributional timeline
tracks the shrinking set; the crisp floor (one value) and the omniscient floor (the true location A
does not know) both fail; the info-free twin (shuffled exclusion order) LOSES.
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

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_uncertain_v1")
ROOM = ["nook", "sofa", "rug", "hearth", "sill", "stair", "closet", "bench"]


def _belief_set(cands, excluded_by_t):
    """Gold: the candidate spots the agent has NOT observed excluded by time t."""
    return [c for c in cands if c not in excluded_by_t]


def _mk_scenario(rng, sid, n_cand=5, n_excl_observed=2):
    """A sees the object enter a region of n_cand spots (uniform belief); then observes some exclusions
    (rules out spots) and misses others. Truth is hidden among the non-excluded."""
    cands = rng.sample(ROOM, n_cand)
    truth = rng.choice(cands)
    others = [c for c in cands if c != truth]
    rng.shuffle(others)
    # exclusions are always of NON-true spots (you cannot truthfully exclude where it actually is)
    excl_order = others[:]                          # up to n_cand-1 possible exclusions
    observed_excl = set(excl_order[:n_excl_observed])   # the ones A witnesses
    # timeline: chrono 0 = enter (uniform); chrono k = exclusion of excl_order[k-1] (observed iff in set)
    events = [("enter", None, 0)]
    observed = {("A", 0): True}
    for k, spot in enumerate(excl_order, start=1):
        events.append(("exclude", spot, k))
        observed[("A", k)] = (spot in observed_excl)
    return {"sid": sid, "cands": cands, "truth": truth, "excl_order": excl_order,
            "observed": observed, "n_cand": n_cand}


def _gold_set_at(sc, t):
    """A's belief set at time t = candidates minus the exclusions A OBSERVED with chrono <= t."""
    excl = set()
    for k, spot in enumerate(sc["excl_order"], start=1):
        if k <= t and sc["observed"].get(("A", k), False):
            excl.add(spot)
    return _belief_set(sc["cands"], excl)


def _f1(pred, gold):
    pred, gold = set(pred), set(gold)
    if not pred and not gold:
        return 1.0
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    return (2 * p * r / (p + r)) if (p + r) else 0.0


def run(n=80, seed=20260830, d=1024, twin_seeds=150, rel_margin=0.5):
    import torch
    from hdlab.belief_partition import BeliefPartition
    from hdlab.situation_model_accumulate import cleanup_set, cleanup_argmax
    bp = BeliefPartition(d=d, seed=seed)
    rng = random.Random(seed)
    scens = [_mk_scenario(rng, f"unc_{i}", n_cand=rng.choice([4, 5, 6]),
                          n_excl_observed=rng.choice([1, 2, 3])) for i in range(n)]

    def read_set(members, distributional=True):
        """Encode the belief set as an FHRR superposition of bind(obj, spot) and read it back:
        distributional -> cleanup_set (the whole set); crisp -> cleanup_argmax (one value)."""
        if not members:
            return []
        obj = bp.code("obj", "obj")
        bank = torch.zeros(d, dtype=torch.complex64)
        for m in members:
            bank = bank + obj * bp.code("loc", m)
        readback = bank * torch.conj(obj)           # unbind the object
        vocab = {c: bp.code("loc", c) for sc in scens for c in sc["cands"]}
        if distributional:
            names, _ = cleanup_set(readback, vocab, rel_margin=rel_margin)
            return names
        best, _ = cleanup_argmax(readback, vocab)
        return [best]

    def score(arm, twin_seed=None):
        f1s = []
        for sc in scens:
            obs = sc["observed"]
            excl_order = sc["excl_order"]
            if arm == "twin":
                # info-free twin: shuffle WHICH spot is excluded at WHICH time (destroys the
                # over-time narrowing signal -- the belief set at t now excludes the wrong spots)
                r = random.Random(twin_seed + hash(sc["sid"]) % 9973)
                excl_order = excl_order[:]
                r.shuffle(excl_order)
            for t in range(1, sc["n_cand"]):     # query at each post-enter time
                # gold uses the TRUE observation set; arms differ in HOW they represent it
                excl = set(sp for k, sp in enumerate(excl_order, 1)
                           if k <= t and obs.get(("A", k), False))
                mem = _belief_set(sc["cands"], excl)
                gold = _gold_set_at(sc, t)
                if arm == "distributional" or arm == "twin":
                    pred = read_set(mem, distributional=True)
                elif arm == "crisp":
                    pred = read_set(mem, distributional=False)      # forced to ONE value
                elif arm == "omniscient":
                    pred = [sc["truth"]]                             # the true location A does not know
                f1s.append(_f1(pred, gold))
        return float(np.mean(f1s))

    dist = score("distributional")
    crisp = score("crisp")
    omni = score("omniscient")
    twin_scores = [score("twin", twin_seed=1000 + ts) for ts in range(twin_seeds)]
    twin_p95 = float(np.percentile(twin_scores, 95))

    # a "correctly represents uncertainty" sub-metric: on queries where |gold|>1, does the arm return
    # a set of the right SIZE (the crisp floor structurally cannot)?
    def uncertain_recall(arm):
        hit = tot = 0
        for sc in scens:
            for t in range(1, sc["n_cand"]):
                gold = _gold_set_at(sc, t)
                if len(gold) <= 1:
                    continue
                excl = set(sp for k, sp in enumerate(sc["excl_order"], 1)
                           if k <= t and sc["observed"].get(("A", k), False))
                mem = _belief_set(sc["cands"], excl)
                pred = read_set(mem, distributional=(arm == "distributional"))
                tot += 1
                hit += int(len(pred) == len(gold))
        return hit / tot if tot else None

    metrics = {
        "seed": seed, "d": d, "n": len(scens), "rel_margin": rel_margin,
        "distributional_f1": dist, "crisp_floor_f1": crisp, "omniscient_floor_f1": omni,
        "twin_p95": twin_p95, "twin_mean": float(np.mean(twin_scores)),
        "uncertain_setsize_recall": {"distributional": uncertain_recall("distributional"),
                                     "crisp": uncertain_recall("crisp")},
        "verdict": {"beats_crisp": dist > crisp, "beats_omniscient": dist > omni,
                    "beats_twin": dist > twin_p95},
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run(n=(20 if args.self_test else 80), twin_seeds=(30 if args.self_test else 150))
    if args.self_test:
        v = m["verdict"]
        assert v["beats_crisp"] and v["beats_omniscient"] and v["beats_twin"], (v, m)
        print("self-test PASS", json.dumps(v))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("DISTRIBUTIONAL / PARTIAL belief -- belief as a SET, narrowing over time")
    print("=" * 78)
    print(f"  DISTRIBUTIONAL (superposition + cleanup_set)  F1 {m['distributional_f1']:.3f}")
    print(f"  crisp-argmax FLOOR (one value)                F1 {m['crisp_floor_f1']:.3f}")
    print(f"  omniscient FLOOR (the truth A lacks)          F1 {m['omniscient_floor_f1']:.3f}")
    print(f"  info-free TWIN p95                            F1 {m['twin_p95']:.3f}")
    us = m["uncertain_setsize_recall"]
    print(f"  correct set-SIZE on uncertain queries: distributional {us['distributional']} "
          f"vs crisp {us['crisp']} (crisp structurally can only say 1)")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
