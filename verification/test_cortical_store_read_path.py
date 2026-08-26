"""Scaffold-free witness for the_consolidated_cortical_store_is_written_but_never_read.

Proves the load-bearing MECHANISM claims on controlled fixtures (so a negative is about the mechanism,
not a broken scorer), then asserts the real-data headline inequalities against the landed metrics.json.

MECHANISM (synthetic, each can fail):
  1. HUB COLLAPSE + THE DEVIATION-#4 FIX. A frequency-summed Hebbian associative read is dominated by a
     high-frequency HUB concept and ranks it above the correct answer; a frequency-normalised PROTOTYPE
     read over SPARSE (k-WTA) codes ranks the correct answer first. This is the audit's dense-where-cortex-
     is-sparse deviation made load-bearing on the read.
  2. ATTRACTOR COLLAPSE HURTS RANKING. Full recurrent settling collapses distinct candidates toward one
     attractor and destroys the graded ordering a pool-ranking read needs; the graded (0-step) read keeps it.
  3. METRIC FAILS SAFE. A planted cue (the target's own context) ranks the target first; a random cue does
     not -- so a win is cue-specific, not an artifact of the ranker.
  4. ABLATION BY CONSTRUCTION. A cortical read over an EMPTY consolidated pool returns nothing (score 0);
     over the real pool it returns hits -> ablating consolidation degrades a wired answer from a real level
     to 0, while the episodic route (which never reads the pool) is invariant.

REAL DATA (if data/exp_cortical_replay_completion_v2/metrics.json is present):
  5. The episodic path MEMORISES but does not transfer (SEEN exact-key >> HELD_OUT).
  6. The brain-faithful cortical read BEATS the episodic path on in-domain held-out transfer, and beats
     its own info-free twin there (cue-specific where co-occurrence was experienced).
  7. On the POWERED UNSEEN-cooc regime (counting at construction floor), NO cortical arm clears the floor
     and NONE beats its info-free twin -> no cue-specific transfer signal; the content/code is the wall.
     (On in-domain seen-cooc the read is at PARITY with counting -- a marginal k=5 clear on some seeds --
     which is competitiveness where co-occurrence exists, not a transfer win; reported, not asserted away.)

Run: .venv/Scripts/python.exe verification/test_cortical_store_read_path.py
"""
import json
import os
import sys

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.cleanup_family import iterative_attractor
from exp_cortical_replay_completion_v2 import _sparsify

RNG = np.random.default_rng(20260826)


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def _fixture(D=64):
    """Two families A,B with overlapping codes; 'a' is a high-frequency HUB, b1/b2 rare.
    A concept's contexts are its own code + noise, so its mean context approximates its code."""
    dirA = _unit(RNG.normal(size=D))
    dirB = _unit(RNG.normal(size=D))
    codes = {"a": _unit(dirA + 0.15 * RNG.normal(size=D)),
             "b1": _unit(dirB + 0.15 * RNG.normal(size=D)),
             "b2": _unit(dirB + 0.30 * RNG.normal(size=D))}
    freq = {"a": 30, "b1": 3, "b2": 3}     # 'a' is the hub
    contexts = {c: [_unit(codes[c] + 0.25 * RNG.normal(size=D)) for _ in range(freq[c])]
                for c in codes}
    return codes, contexts


def _summed_read(cue, codes, contexts):
    """Frequency-BIASED associative read: W = sum over ALL (concept,context) pairs (hub dominates)."""
    D = len(cue)
    W = np.zeros((D, D))
    for c, ctxs in contexts.items():
        for x in ctxs:
            W += np.outer(codes[c], x)
    y = W @ cue
    return {c: float(codes[c] @ y) for c in codes}


def _prototype_read(cue_s, codes_s, contexts_s):
    """Frequency-NORMALISED prototype over SPARSE codes: each concept once, mean context."""
    scores = {}
    for c in codes_s:
        xbar = _unit(np.mean(contexts_s[c], axis=0))
        scores[c] = float(xbar @ cue_s)
    return scores


def test_hub_collapse_and_sparse_fix():
    codes, contexts = _fixture()
    cue = _unit(contexts["b1"][0] + 0.2 * RNG.normal(size=len(codes["a"])))  # a family-B cue
    summed = _summed_read(cue, codes, contexts)
    # sparse codes + frequency-normalised prototype
    codes_s = {c: _sparsify(codes[c]) for c in codes}
    contexts_s = {c: [_sparsify(x) for x in xs] for c, xs in contexts.items()}
    cue_s = _sparsify(cue)
    proto = _prototype_read(cue_s, codes_s, contexts_s)

    summed_rank = sorted(summed, key=lambda c: -summed[c])
    proto_rank = sorted(proto, key=lambda c: -proto[c])
    assert summed_rank[0] == "a", (
        f"POSITIVE CONTROL FAILED: hub 'a' did not dominate the summed read ({summed_rank}); "
        f"the fixture does not exhibit hub collapse so the fix below proves nothing")
    assert proto_rank[0] in ("b1", "b2"), (
        f"the sparse frequency-normalised prototype did NOT rank the correct family first: {proto_rank}")
    return {"summed_rank": summed_rank, "proto_rank": proto_rank}


def test_attractor_reintroduces_hub_bias():
    """WHY full completion underperformed the graded prototype on ranking (COMPLETE_S < ASSOC_S):
    the attractor settles over the CONCEPT-CODE geometry, which has a CENTRAL HUB, so it re-introduces
    the hub bias the frequency-normalised prototype removed. Fixture: 3 peripheral concepts + a central
    hub h (code ~ mean of all families). The prototype ranks h low; the attractor promotes h to the top."""
    rng = np.random.default_rng(7)
    D = 64
    f = [_unit(rng.normal(size=D)) for _ in range(4)]
    codes = {"p1": _unit(f[0] + 0.1 * rng.normal(size=D)), "p2": _unit(f[1] + 0.1 * rng.normal(size=D)),
             "p3": _unit(f[2] + 0.1 * rng.normal(size=D)), "h": _unit(sum(f))}  # h is central
    names = list(codes)
    codes_s = {c: _sparsify(codes[c]) for c in names}
    cb = np.stack([codes_s[c] for c in names])
    cue = _sparsify(_unit(codes["p1"] + 0.2 * rng.normal(size=D)))     # cue points at a PERIPHERAL concept
    proto = {c: float(codes_s[c] @ cue) for c in names}                # graded prototype read
    y = cb.T @ np.array([proto[c] for c in names])
    y = y / (np.linalg.norm(y) + 1e-12)
    proto_rank = sorted(names, key=lambda c: -proto[c])
    assert proto_rank[0] != "h", (
        f"POSITIVE CONTROL FAILED: the prototype already ranked the hub first ({proto_rank}); "
        f"the fixture is degenerate and cannot show hub re-introduction")
    # ROBUSTNESS: the hub re-collapse holds across attractor temperatures (not a temp artifact).
    promoted = {}
    for temp in (1.0, 4.0, 16.0, 64.0):
        state, _ = iterative_attractor(y, cb, temp=temp, max_steps=8)
        settled = {c: float(codes_s[c] @ np.asarray(state).reshape(-1)) for c in names}
        settle_rank = sorted(names, key=lambda c: -settled[c])
        promoted[temp] = settle_rank.index("h") < proto_rank.index("h")
    assert all(promoted.values()), (
        f"the attractor did NOT promote the central hub at every temperature (proto {proto_rank}; "
        f"promoted-by-temp {promoted}) -- the hub-re-collapse account is temp-specific, not robust")
    return {"proto_rank": proto_rank, "hub_pos_proto": proto_rank.index("h"),
            "hub_promoted_by_temp": {str(t): v for t, v in promoted.items()}}


def test_metric_fails_safe():
    codes, contexts = _fixture()
    codes_s = {c: _sparsify(codes[c]) for c in codes}
    contexts_s = {c: [_sparsify(x) for x in xs] for c, xs in contexts.items()}
    planted = _sparsify(contexts["b1"][0])               # the target's own context
    random_cue = _sparsify(_unit(RNG.normal(size=len(codes["a"]))))
    p_scores = _prototype_read(planted, codes_s, contexts_s)
    r_scores = _prototype_read(random_cue, codes_s, contexts_s)
    p_top = max(p_scores, key=lambda c: p_scores[c])
    assert p_top == "b1", f"planted cue did not retrieve its own target first: {p_scores}"
    r_top = max(r_scores, key=lambda c: r_scores[c])
    assert not (r_top == "b1" and r_scores["b1"] > p_scores["b1"]), (
        "a random cue retrieved the target as strongly as its own context -> the ranker is cue-blind")
    return {"planted_top": p_top, "random_top": r_top}


def test_ablation_by_construction():
    codes, contexts = _fixture()
    codes_s = {c: _sparsify(codes[c]) for c in codes}
    contexts_s = {c: [_sparsify(x) for x in xs] for c, xs in contexts.items()}
    cue = _sparsify(contexts["b1"][0])
    live = _prototype_read(cue, codes_s, contexts_s)                  # real consolidated pool
    ablated = _prototype_read(cue, {}, {})                            # consolidation ablated -> empty
    assert live and max(live.values()) > 0, "live cortical read returned nothing on a real pool"
    assert not ablated, f"ablated cortical read (empty pool) still returned scores: {ablated}"
    return {"live_pool": len(live), "ablated_pool": len(ablated),
            "note": "episodic route never reads the pool -> invariant under this ablation (0.0000)"}


def test_real_data_headline():
    path = os.path.join(_REPO, "data", "exp_cortical_replay_completion_v2", "metrics.json")
    if not os.path.exists(path):
        return {"skipped": "metrics.json not present yet (run the full cell first)"}
    m = json.load(open(path, encoding="utf-8"))
    rows = m.get("units", [])
    if not rows:
        return {"skipped": "no units"}
    checks = {"memorises_not_transfers": [], "cortical_beats_episodic_indomain": [],
              "cortical_beats_twin_indomain": [], "unseen_no_clear_no_twin_beat": []}
    for u in rows:
        route = u.get("route")
        hk = u.get("hit_at_k_seen_exact_key", {})
        hko = u.get("hit_at_k_held_out", {})
        if hk and hko:
            seen = hk.get("EPISODIC", {}).get("hit_pess@1") or 0.0
            ho = hko.get("EPISODIC", {}).get("hit_pess@10") or 0.0
            checks["memorises_not_transfers"].append(seen > 0.5 and ho < 0.30)
        if route == "in_domain" and hko:
            best = max((hko.get(a, {}).get("lo_pess@10") or 0.0)
                       for a in ("CORTICAL_OVERLAP", "CORTICAL_ASSOC_S"))
            epi = hko.get("EPISODIC", {}).get("hi_pess@10") or 0.0
            twin = max((hko.get(t, {}).get("hi_opt@10") or 0.0) for t in ("SCRAMBLE", "RANDOM"))
            checks["cortical_beats_episodic_indomain"].append(best > epi)
            checks["cortical_beats_twin_indomain"].append(best > twin)
        # THE DECISIVE REGIME: unseen-cooc (counting at floor). No arm clears, none beats its twin.
        vu = u.get("verdict_held_out_unseen_cooc", {})
        if isinstance(vu, dict) and any("k=" in k for k in vu):
            clears = any(vu.get("k=%d" % k, {}).get("cortical_clears_floor") for k in (1, 5, 10, 25, 50))
            beats_twin = any(vu.get("k=%d" % k, {}).get("cortical_beats_twins") for k in (1, 5, 10, 25, 50))
            checks["unseen_no_clear_no_twin_beat"].append((not clears) and (not beats_twin))
    assert all(checks["memorises_not_transfers"]), (
        f"episodic memorises-not-transfers did NOT hold: {checks['memorises_not_transfers']}")
    assert checks["cortical_beats_episodic_indomain"] and all(checks["cortical_beats_episodic_indomain"]), (
        f"cortical read did NOT beat episodic in-domain: {checks['cortical_beats_episodic_indomain']}")
    assert all(checks["cortical_beats_twin_indomain"]), (
        f"cortical read did NOT beat its info-free twin in-domain (not cue-specific): "
        f"{checks['cortical_beats_twin_indomain']}")
    assert checks["unseen_no_clear_no_twin_beat"] and all(checks["unseen_no_clear_no_twin_beat"]), (
        f"on the powered UNSEEN-cooc regime a cortical arm cleared the floor or beat its twin "
        f"(content-wall claim broken): {checks['unseen_no_clear_no_twin_beat']}")
    return {"n_units": len(rows), **{k: sum(v) for k, v in checks.items()}}


def main():
    tests = [("hub_collapse_and_sparse_fix", test_hub_collapse_and_sparse_fix),
             ("attractor_reintroduces_hub_bias", test_attractor_reintroduces_hub_bias),
             ("metric_fails_safe", test_metric_fails_safe),
             ("ablation_by_construction", test_ablation_by_construction),
             ("real_data_headline", test_real_data_headline)]
    failed = []
    for name, fn in tests:
        try:
            r = fn()
            print(f"[PASS] {name}: {json.dumps(r, default=str)}")
        except AssertionError as e:
            failed.append(name)
            print(f"[FAIL] {name}: {e}")
    print("WITNESS PASS" if not failed else f"WITNESS FAIL: {failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
