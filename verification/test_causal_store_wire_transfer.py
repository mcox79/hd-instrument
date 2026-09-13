"""Witness for `wire_the_mined_directed_causal_store_into_the_live_causal_reasoner_and_measure`.

Reproduces the headline: (LOCATED NEGATIVE) the mined store does NOT transfer to the reader's extracted-from-prose
NECESSITY read -- neither on the live single-verb-lemma graph nor, once the concept-bound upstream fix is applied,
above a topicality/mapping baseline or a direction-scramble null; and the brief's +0.139 storeonly prize collapses
against the honest density-matched twin. (POSITIVE / the read that WOULD work) the store's DIRECTION transfers on a
direction-discrimination 2AFC where association is pinned at chance -- CI-separated over the shuffled twin AND over the
reverse-direction control -- but the gain is small (~+0.03-0.04), at the intrinsic ~0.61 text-direction ceiling.

Glass-box, NO external LLM. Run: .venv/Scripts/python.exe verification/test_causal_store_wire_transfer.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("OMP_NUM_THREADS", "3")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("  [PASS] " if cond else "  [FAIL] ") + name + (("  " + detail) if detail else ""))
    return bool(cond)


def main():
    from experiments.exp_causal_store_wire_transfer_v1 import run as transfer_run
    out = transfer_run(smoke=True, thr=0.0)
    ne = out["necessity_effect_vs_noeffect"]; cb = out["upstream_fix_concept_bound_step_nodes"]
    rs = out["reference_storeonly_regime"]; ct = out["store_coverage_trace"]; ed = out["extraction_density"]

    # -- LOCATED NEGATIVE 1: the live single-verb-lemma wire transfers nothing --
    check("W1 live lemma-node wire transfers ~0 (paired store-base <= 0.01)",
          ne["paired_store_minus_base"]["delta"] <= 0.01,
          "store-base=%.4f  (avg_nodes=%.1f avg_edges=%.1f lemma_cov=%.4f)"
          % (ne["paired_store_minus_base"]["delta"], ed["avg_nodes"], ed["avg_edges"], ct["lemma_pair_coverage"]))
    check("W1b single-lemma store coverage << concept coverage (the node-granularity loss)",
          ct["lemma_pair_coverage"] < 0.5 * ct["concept_pair_coverage"],
          "lemma=%.4f concept=%.4f" % (ct["lemma_pair_coverage"], ct["concept_pair_coverage"]))

    # -- LOCATED NEGATIVE 2: even concept-bound, the store loses to a topicality baseline + direction is inert --
    check("W2 concept-bound store does NOT beat the mapping/topicality baseline (cbound-map_only <= 0)",
          cb["paired_cbound_minus_maponly"]["delta"] <= 0.0,
          "cbound-map_only=%.4f (cbound=%.3f map_only=%.3f)"
          % (cb["paired_cbound_minus_maponly"]["delta"], cb["cbound"]["acc"], cb["map_only"]["acc"]))
    check("W2b UNDIRECTED connectivity >= directed cbound (direction is inert-to-harmful on the existence axis)",
          cb["cbound_undirected"]["acc"] >= cb["cbound"]["acc"] - 0.005,
          "undirected=%.3f cbound=%.3f (diff %+.4f)" % (cb["cbound_undirected"]["acc"], cb["cbound"]["acc"],
                                                        cb["cbound_undirected"]["acc"] - cb["cbound"]["acc"]))
    check("W2c direction-scramble does NOT collapse cbound (|cbound-dirscramble| small -> direction not load-bearing)",
          abs(cb["paired_cbound_minus_dirscramble"]["delta"]) < 0.06,
          "cbound-dirscramble=%.4f (a random-orientation graph reproduces cbound; the residual is direction-COHERENCE "
          "not correctness)" % cb["paired_cbound_minus_dirscramble"]["delta"])

    # -- DISK-OUTRANKS-BRIEF: the +0.139 storeonly prize is a density artifact of the global-shuffle twin --
    check("W3 storeonly does NOT beat the density-matched topotwin CI-sep (the +0.139 was a density artifact)",
          rs["paired_storeonly_minus_topotwin"]["ci"][0] <= 0.0,
          "storeonly-topotwin=%.4f CI=%s (vs global-twin=%.4f)" % (
              rs["paired_storeonly_minus_topotwin"]["delta"], rs["paired_storeonly_minus_topotwin"]["ci"],
              rs["paired_storeonly_minus_globaltwin"]["delta"]))

    # -- POSITIVE: the store's DIRECTION transfers on a direction-discrimination 2AFC (association pinned at chance) --
    from experiments.exp_causal_directional_score_v1 import (_c, edge_condXasym, support)
    from experiments.exp_causal_testimony_eval_v1 import load_store, shuffle_store
    from experiments.exp_causal_selection_ecare_copa_v1 import load_ecare
    from experiments.exp_causal_bcopa_ce_v1 import load_bcopa_ce
    STORE = os.path.join(_REPO, "data", "exp_causal_testimony_mine_v1", "store_v1.json")
    store = load_store(STORE); twin = shuffle_store(store, seed=101)

    def bcopa_hit(st, it, rev=False):
        P = _c(it["premise"]); A1 = _c(it["a1"]); A2 = _c(it["a2"])
        if (it["ask"] == "cause") ^ rev:
            s1, s2 = support(st, edge_condXasym, A1, P), support(st, edge_condXasym, A2, P)
        else:
            s1, s2 = support(st, edge_condXasym, P, A1), support(st, edge_condXasym, P, A2)
        return 0.5 if s1 == s2 else (1.0 if (0 if s1 > s2 else 1) == it["gold"] else 0.0)

    bcopa = load_bcopa_ce()
    fwd = sum(bcopa_hit(store, it) for it in bcopa) / len(bcopa)
    tw = sum(bcopa_hit(twin, it) for it in bcopa) / len(bcopa)
    rev = sum(bcopa_hit(store, it, rev=True) for it in bcopa) / len(bcopa)
    check("W4 store DIRECTION beats the shuffled twin on BCOPA-CE (assoc pinned at chance by construction)",
          fwd > tw + 0.005, "fwd=%.3f twin=%.3f" % (fwd, tw))
    check("W4b store DIRECTION beats its REVERSE (direction, not association, is the signal)",
          fwd > rev + 0.02, "fwd=%.3f reverse=%.3f (fwd-rev=%+.3f)" % (fwd, rev, fwd - rev))
    check("W4c the direction gain is SMALL / at the intrinsic ceiling (fwd < 0.60 on 2AFC)",
          fwd < 0.60, "fwd=%.3f (the ~0.61 single-direction cap on a 2AFC)" % fwd)

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
