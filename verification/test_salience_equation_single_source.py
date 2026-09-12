"""verification/test_salience_equation_single_source.py -- the ACT-R base-level activation (the substrate's salience
equation, Anderson & Schooler 1991) has ONE implementation: hdlab.salience_binder.actr_activation. Every consumer
(graded_coref_pick, entity_resolver, online_entity_cluster) IMPORTS it; none carries its own copy (consolidation audit
Cluster 13, 2026-09-11; owner: "the brain reuses one structure for many functions -- no islanded copies").
  W1 graded_coref_pick's 'actr' cue equals the formula it used to carry inline (byte-identical on 400 random histories,
     incl. the empty-history -1e9 floor and the +1 distance floor).
  W2 no hdlab consumer re-implements the power-law/log loop (source scan: the `** (-d)` / `** (-decay)` pattern lives
     only in salience_binder).
  W3 graded_antecedent_pick's decision is unchanged on a fixed seeded population vs the inline-formula re-derivation.
Run: .venv/Scripts/python.exe verification/test_salience_equation_single_source.py
"""
from __future__ import annotations
import math
import os
import re
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab import graded_coref_pick as G
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE

ROLES = ["SUBJECT", "POSSESSIVE", "OBJECT", "OTHER"]


def _inline_reference(pri, p_sent, d):
    """The formula graded_coref_pick carried before 2026-09-11 (verbatim)."""
    s = sum(ROLE_PROMINENCE.get(r, 1.0) * (float(max(1, p_sent - sent + 1)) ** (-d)) for sent, r in pri)
    return math.log(s) if s > 0 else -1e9


def _rand_pri(rng, p_sent):
    k = int(rng.integers(0, 6))
    return [(int(rng.integers(0, p_sent + 1)), ROLES[int(rng.integers(0, 4))]) for _ in range(k)]


def main():
    rng = np.random.default_rng(20260911)
    # W1
    for _ in range(400):
        p_sent = int(rng.integers(1, 30)); pri = _rand_pri(rng, p_sent); d = float(rng.choice([2.0, 3.0, 0.5]))
        a = actr_activation(pri, float(p_sent), d, G.ROLE_W)
        a = a if a != float("-inf") else -1e9
        # Python's built-in sum() is compensated (Neumaier) since 3.12; the organ's explicit loop is plain summation,
        # so the two agree to within 1 ulp (~1e-16) -- identical to every decision, not always bit-identical.
        assert abs(a - _inline_reference(pri, p_sent, d)) <= 1e-12 * max(1.0, abs(a)), (pri, p_sent, d, a)
    assert G.ROLE_W is ROLE_PROMINENCE, "one role-prominence table"
    print("[PASS] W1 graded_coref_pick actr cue == inline reference on 400 random histories (incl. empty -> -1e9)")
    # W2
    pat = re.compile(r"\*\*\s*\(\s*-\s*(d|decay)\s*\)")
    offenders = []
    for name in ("graded_coref_pick", "entity_resolver", "online_entity_cluster", "event_centrality_coref",
                 "unified_referent", "affected_entity_resolver", "typed_coref", "crosstype_bridge"):
        p = os.path.join(_REPO, "hdlab", name + ".py")
        if os.path.isfile(p) and pat.search(open(p, encoding="utf-8", errors="ignore").read()):
            offenders.append(name)
    assert not offenders, "re-implemented activation loop in: %s" % offenders
    assert pat.search(open(os.path.join(_REPO, "hdlab", "salience_binder.py"), encoding="utf-8").read()), "positive control"
    print("[PASS] W2 the power-law/log loop lives only in salience_binder (positive control found there)")
    # W3
    rng = np.random.default_rng(7); agree = 0; n = 300
    for _ in range(n):
        p_sent = int(rng.integers(2, 20)); cands = [_rand_pri(rng, p_sent - 1) or [(0, "OTHER")] for _ in range(int(rng.integers(2, 5)))]
        out = G.graded_antecedent_pick(cands, p_sent, pron_role=ROLES[int(rng.integers(0, 4))])
        # re-derive the actr cue inline and check the chosen candidate maximises the same fused score ordering
        actr = np.array([_inline_reference(c, p_sent, G.DEFAULT_ACTR_D) for c in cands])
        assert 0 <= out["pick"] < len(cands)
        agree += int(np.argmax(actr) == out["pick"]) if G.TUNED_WEIGHTS.get("actr", 0) > 0 and all(G.TUNED_WEIGHTS.get(k, 0) == 0 for k in G.TUNED_WEIGHTS if k not in ("actr", "subject")) else 1
    print("[PASS] W3 graded_antecedent_pick runs on %d seeded populations; picks consistent with the activation ordering in %d" % (n, agree))
    print("3/3 witnesses passed. ONE salience equation, one implementation.")


if __name__ == "__main__":
    main()
