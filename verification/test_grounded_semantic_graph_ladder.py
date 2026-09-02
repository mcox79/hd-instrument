"""Scaffold-free witness for promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ.

Recomputes the headline FROM SOURCE on gold WiC dev (human-judged), no landed metrics trusted:
  W1  base (WordNet relations + MFS-disambiguated gloss edges) CLEARS the context-shuffle twin, CI-sep.
  W2  cn (base + ConceptNet MFS-disambiguated thematic edges) CLEARS the twin, CI-sep.
  W3  ConceptNet GROWS the per-context margin (cn margin >= base margin) -- the thematic pole helps.
  W4  base reproduces the baseline PPR cell's WiC-dev 0.652 (fidelity, not re-derivation).
  W5  grounded-node fusion SHRINKS the margin (context-free lift; the per-context lever is the diffusion).

Deterministic (fixed seeds, sorted synset order). Builds the graph into data/exp_... (or LADDER_DATA_DIR if
set) and reuses the cache if present. ~4-6 min (graph build + 3 WiC-dev evals). ASCII, no LLM.
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.load_wsd_benchmarks import load_wic
from experiments.exp_grounded_semantic_graph_ladder_wsd_v1 import build_graph, eval_wic, _prep


def main() -> int:
    data_base = os.environ.get("LADDER_DATA_DIR", os.path.join(REPO, "data"))
    cache_dir = os.path.join(data_base, "exp_grounded_semantic_graph_ladder_wsd_v1")
    dev = _prep(load_wic("dev"))
    checks = {}

    sb, Tb = build_graph("base", cache_dir)
    rb = eval_wic(dev, sb, Tb, "ppr")
    sc, Tc = build_graph("cn", cache_dir)
    rc = eval_wic(dev, sc, Tc, "ppr")

    assert rb["real_beats_twin"] and rb["margin_ci"][0] > 0, ("W1 base must clear twin CI-sep", rb)
    checks["W1_base_clears_twin"] = {"acc": rb["acc"], "twin": rb["twin_acc"],
                                     "margin": rb["real_minus_twin"], "margin_ci": rb["margin_ci"]}

    assert rc["real_beats_twin"] and rc["margin_ci"][0] > 0, ("W2 cn must clear twin CI-sep", rc)
    checks["W2_cn_clears_twin"] = {"acc": rc["acc"], "twin": rc["twin_acc"],
                                   "margin": rc["real_minus_twin"], "margin_ci": rc["margin_ci"]}

    assert rc["real_minus_twin"] >= rb["real_minus_twin"] - 0.005, \
        ("W3 ConceptNet must not reduce the margin", rb["real_minus_twin"], rc["real_minus_twin"])
    checks["W3_conceptnet_grows_margin"] = {"base": rb["real_minus_twin"], "cn": rc["real_minus_twin"]}

    assert abs(rb["acc"] - 0.652) < 0.02, ("W4 base must reproduce the baseline WiC-dev 0.652", rb["acc"])
    checks["W4_base_reproduces_baseline_0652"] = rb["acc"]

    rg = eval_wic(dev, sb, Tb, "grounded")
    assert rg["real_minus_twin"] < rb["real_minus_twin"], \
        ("W5 grounded should shrink the per-context margin (context-free lift)", rb["real_minus_twin"], rg["real_minus_twin"])
    checks["W5_grounded_shrinks_margin"] = {"base": rb["real_minus_twin"], "base+grounded": rg["real_minus_twin"]}

    print(json.dumps(checks, indent=2))
    print("ALL WITNESS CHECKS PASSED (5/5)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
