"""Scaffold-free witness for `the_entity_store_is_a_dense_bundle_that_fans`.

Asserts the DECISIVE diagnosis + the brain-faithful fix, on synthetic fixtures and a small LitBank
slice (fast). Reproduces the headline without re-running the full landed cell. Run:
  .venv/Scripts/python.exe verification/test_entity_store_fan.py
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from experiments.exp_entity_store_sparse_fan_v1 import (  # noqa: E402
    part1_doc, part2_doc, part3_scaling, part3_residual, diagnose, self_test, binof,
)

PASS = []


def ok(name, cond, detail=""):
    if not cond:
        raise AssertionError(f"FAIL: {name} :: {detail}")
    PASS.append(name)
    print(f"  PASS {name} {detail}")


def test_cell_selftest():
    """The cell's own off-disk gate: batched DG matches organ; collision fixtures behave."""
    r = self_test()
    ok("cell_selftest_batched_dg", r["batched_dg_ok"])
    ok("cell_selftest_argmax_misses_collision", r["part1_syn"]["DENSE_ARGMAX"] < 0.7,
       f"argmax={r['part1_syn']['DENSE_ARGMAX']}")


def test_diagnosis_fan_is_collision_not_superposition():
    """On a small LitBank slice: the fan is an ADDRESSING COLLISION (unique-address decodes at ceiling
    at EVERY fan level; top-m set-return recovers the set) -- NOT superposition blur. Corrects the brief."""
    d = diagnose(docs=15)
    ok("collision_rate_material", d["collision_rate_pairs_with_multi_verb"] > 0.10,
       f"multi-verb-address rate={d['collision_rate_pairs_with_multi_verb']:.3f}")
    argmax = d["all_queries_argmax"]
    # the fan exists on argmax: 17+ is materially below 1-3
    ok("argmax_fans", argmax["17+"]["acc"] < argmax["1-3"]["acc"] - 0.10,
       f"1-3={argmax['1-3']['acc']:.3f} 17+={argmax['17+']['acc']:.3f}")
    # unique-address decodes at ceiling at EVERY fan level -> not superposition
    for b in ["1-3", "4-8", "9-16", "17+"]:
        u = d["unique_address_only"][b]
        if u["n"] > 0:
            ok(f"unique_address_ceiling_{b}", u["acc"] > 0.98, f"acc={u['acc']:.4f} n={u['n']}")
    # top-m set-return recovers the set at every level -> the dense bundle HOLDS the info
    for b in ["1-3", "17+"]:
        t = d["topm_setreturn"][b]
        ok(f"topm_recovers_set_{b}", t["acc"] > 0.98, f"acc={t['acc']:.4f} n={t['n']}")


def _fan_slope(per_doc):
    agg = {b: [0, 0] for b in ["1-3", "4-8", "9-16", "17+"]}
    for doc in per_doc:
        for ok_, n in doc:
            c = agg[binof(n)]; c[0] += ok_; c[1] += 1
    a = {b: (agg[b][0] / agg[b][1] if agg[b][1] else float("nan")) for b in agg}
    return a["1-3"] - a["17+"], a


def test_finer_context_and_setreturn_flatten_the_fan():
    """The brain-faithful fixes -- a FINER conjunctive temporal index (TCM) at store, or SET-RETURN
    (CA3 context-cued reactivation) at readout -- flatten the collision fan vs DENSE_ARGMAX."""
    from experiments.exp_entity_store_sparse_fan_v1 import load_events
    recs = load_events(docs=15)
    slopes = {}
    for arm in ["DENSE_ARGMAX", "DENSE_SETRETURN", "FINER_CTX", "POINTER_MULTIMAP"]:
        per_doc = [part1_doc(r, arm) for r in recs]
        slopes[arm], _ = _fan_slope(per_doc)
    ok("dense_argmax_has_a_fan", slopes["DENSE_ARGMAX"] > 0.10, f"slope={slopes['DENSE_ARGMAX']:.3f}")
    ok("setreturn_flattens", slopes["DENSE_SETRETURN"] < slopes["DENSE_ARGMAX"] - 0.05,
       f"argmax={slopes['DENSE_ARGMAX']:.3f} setreturn={slopes['DENSE_SETRETURN']:.3f}")
    ok("finer_ctx_flattens", slopes["FINER_CTX"] < slopes["DENSE_ARGMAX"] - 0.05,
       f"argmax={slopes['DENSE_ARGMAX']:.3f} finer={slopes['FINER_CTX']:.3f}")
    ok("pointer_flat", abs(slopes["POINTER_MULTIMAP"]) < 0.03, f"slope={slopes['POINTER_MULTIMAP']:.3f}")


def test_info_free_order_twin_loses_on_collisions():
    """The finer index carries INFORMATION: true within-sentence order recovers the specific action;
    a shuffled-order twin (info-free, matched shape) LOSES on colliding events."""
    from experiments.exp_entity_store_sparse_fan_v1 import load_events
    recs = load_events(docs=20)

    def collide_acc(arm):
        c = [0, 0]
        for r in recs:
            for okk, n, m in part2_doc(r, arm):
                if m > 1:
                    c[0] += okk; c[1] += 1
        return c[0] / c[1] if c[1] else float("nan")

    ft = collide_acc("FINER_TRUE")
    tw = collide_acc("RANDOM_ORDER_TWIN")
    ok("finer_true_recovers_specific", ft > 0.90, f"finer_true collide acc={ft:.3f}")
    ok("info_free_order_twin_loses", tw < ft - 0.15, f"true={ft:.3f} twin={tw:.3f}")


def test_sparse_wins_the_superposition_regime():
    """The brief's sparse mechanism is validated where it actually applies -- HIGH unique-event load:
    DENSE_flat fans, SPARSE_DG holds. (Not the measured LitBank fan, which is collision.)"""
    sc = part3_scaling(loads=(50, 400, 800))
    ok("dense_flat_fans_at_load", sc["N=800"]["DENSE_flat"] < 0.30, f"dense_flat@800={sc['N=800']['DENSE_flat']:.3f}")
    ok("sparse_holds_at_load", sc["N=800"]["SPARSE_DG"] > 0.95, f"sparse@800={sc['N=800']['SPARSE_DG']:.3f}")
    ok("sparse_beats_dense_flat", sc["N=400"]["SPARSE_DG"] > sc["N=400"]["DENSE_flat"] + 0.5)


def test_residual_tracks_similarity_not_count():
    """Brain-faithful signature (Leutgeb 2007; Yassa & Stark 2011): under a partial cue the sparse
    store's residual error tracks item-SIMILARITY (high-sim half errs more) far more than item-COUNT."""
    r = part3_residual(N=800, keep=0.7)
    s = r["similarity_arm_fixed_count"]
    ok("residual_tracks_similarity", s["err_high_similarity_half"] > s["err_low_similarity_half"] + 0.2,
       f"hi={s['err_high_similarity_half']:.3f} lo={s['err_low_similarity_half']:.3f}")
    c = r["count_arm_fixed_low_similarity"]
    # count effect is comparatively shallow: 16x more items -> < 3x the error, and stays modest
    ok("count_effect_shallow", c["N=1600"] < 3 * c["N=100"] and c["N=1600"] < 0.45,
       f"N100={c['N=100']:.3f} N1600={c['N=1600']:.3f}")


if __name__ == "__main__":
    test_cell_selftest()
    test_diagnosis_fan_is_collision_not_superposition()
    test_finer_context_and_setreturn_flatten_the_fan()
    test_info_free_order_twin_loses_on_collisions()
    test_sparse_wins_the_superposition_regime()
    test_residual_tracks_similarity_not_count()
    print(f"\nALL {len(PASS)} CHECKS PASSED")
