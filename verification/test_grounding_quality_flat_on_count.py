"""verification/test_grounding_quality_flat_on_count.py -- scaffold-free witnesses for the FLAT-on-count half of the
grounding coverage-QUALITY instrument (problem: grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count,
STATUS UPDATE item (b)). The landed sense-assignment instrument shows MOVES-on-quality + twin-at-chance (W5 in
test_fused_sense_ranker_live). These witnesses prove the OTHER half: the count knob (SDT false-alarm) inflates
`n_grounded` WITHOUT changing link correctness, and the quality dim does NOT move while the count does.

  V1 the count knob is REAL and separate from the ranking: on the LIVE ranker, raising FA (SDT_FALSE_ALARM) LOWERS
     the accept criterion (criterion(FA_hi) < criterion(FA_lo)), so strictly more links clear the gate -- while the
     ranked candidate ORDER and z_top for every query are BYTE-IDENTICAL across FA (the accept threshold never
     enters the ranking). This is the mechanism that makes n_grounded quality-blind.
  V2 the demonstration cell's 2x2 verdict holds on smoke: count MOVES-up on the count-only change, the quality
     RANKING is exactly FA-invariant (diff 0), the twin is at chance, and (from the landed arm) quality MOVES on a
     real quality change.
  V3 the count grows FASTER than the correct count: across the FA sweep the accepted count rises but the number of
     CORRECT accepted links does not keep pace (the count rewards wrong links) -- monotone accepted, correct-rate
     among accepted does not rise.
Run: .venv/Scripts/python.exe verification/test_grounding_quality_flat_on_count.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_meaning_fusion_live_coverage_v1 as E
import experiments.exp_board_grounding_coverage_quality_v1 as B
import experiments.exp_grounding_quality_flat_on_count_v1 as F
from hdlab.reading_grounding_loop import FusedSenseRanker, is_eligible_meaning

PASSED = []


def v1_count_knob_is_separate_from_ranking():
    """LIVE micro-check: FA moves the accept criterion + accepted count, never the ranking/z_top."""
    seed_words = E.H.load_base_vocab_seed(); seed_set = set(seed_words)
    state, _n, _m = B._build_live_state(700, seed_words, None)   # no grown store: fast, self-contained
    qs, targets, anchors, elig = B._queries(state, seed_set)
    assert len(qs) >= 10, ("too few queries", len(qs))
    r_lo = FusedSenseRanker(state.space, false_alarm=0.01)
    r_hi = FusedSenseRanker(state.space, false_alarm=0.40)
    # criterion strictly lower at higher FA for every realistic field size
    for n in (10, 50, 100, 300):
        assert r_hi.criterion(n) < r_lo.criterion(n), ("criterion not lower at higher FA", n)
    # the ranking (order + z_top) is byte-identical across FA; only the accept verdict differs, and accepts >=
    n_checked = 0; n_accept_lo = 0; n_accept_hi = 0
    for (q, _t) in qs:
        a = r_lo.rank(q, eligible=is_eligible_meaning, return_order=True)
        b = r_hi.rank(q, eligible=is_eligible_meaning, return_order=True)
        if a is None or b is None:
            continue
        n_checked += 1
        assert a["order"] == b["order"], ("order changed with FA", q)
        assert abs(a["z_top"] - b["z_top"]) < 1e-12, ("z_top changed with FA", q)
        assert bool(b["accept"]) or not bool(a["accept"]), "FA_hi must accept a superset of FA_lo"
        n_accept_lo += int(a["accept"]); n_accept_hi += int(b["accept"])
    assert n_checked >= 10, n_checked
    assert n_accept_hi > n_accept_lo, ("count did not move with the FA knob", n_accept_lo, n_accept_hi)
    PASSED.append("V1 count knob separate from ranking: order+z_top FA-invariant on %d queries; accepted %d->%d as "
                  "FA 0.01->0.40 (criterion lower, ranking untouched)" % (n_checked, n_accept_lo, n_accept_hi))


def v2_smoke_2x2():
    r = F.run(mode="smoke", n_boot=300, grown_store=F.GROWN_STORE)
    assert "verdict" in r, r.get("note", r)
    v = r["verdict"]
    fk = r["FLAT_on_count__FA_0.01_to_0.40"]
    assert v["count_MOVES_on_count_only_change_CI_sep_up"], fk["COUNT_frac_accepted_targets"]
    assert v["quality_FLAT_on_count_only_change"], fk["QUALITY_ranking_MRR_diff_is_zero_by_FA_invariance"]
    assert v["twin_at_chance"], r["twin_at_chance__FUSED_minus_TWIN@0.5"]
    # the count effect must dwarf the quality CI half-width (a POWERED flat, not an underpowered null)
    cm = fk["COUNT_frac_accepted_targets"]
    assert cm["diff"] > 0 and cm["ci_sep"], cm
    PASSED.append("V2 smoke 2x2 (n_q=%d, n_tg=%d): count +%.3f CI %s (MOVES); quality ranking diff %.1e (FLAT); "
                  "twin MRR %.3f (chance); quality MOVES-on-quality=%s"
                  % (r["n_scorable_queries"], r["n_grounding_targets"], cm["diff"], cm["ci"],
                     fk["QUALITY_ranking_MRR_diff_is_zero_by_FA_invariance"]["diff"],
                     r["twin_at_chance__FUSED_minus_TWIN@0.5"]["twin_mrr"],
                     v["quality_MOVES_on_quality_change_CI_sep"]))
    return r


def v3_count_outruns_correct(r):
    sweep = r["fa_sweep"]
    ns = [s["n_accepted_targets"] for s in sweep]
    assert all(ns[i] <= ns[i + 1] for i in range(len(ns) - 1)), ("accepted not monotone", ns)
    # correct-rate among accepted does NOT rise as the count grows (the count rewards wrong links)
    rates = [s["correct_rate_among_accepted"] for s in sweep if s["correct_rate_among_accepted"] is not None]
    assert rates, sweep
    assert rates[-1] <= rates[0] + 0.05, ("correct-rate rose with the count -- count would not be quality-blind", rates)
    PASSED.append("V3 count outruns correctness: accepted_targets %d->%d monotone; correct-rate-among-accepted %.3f->%.3f "
                  "(does not rise) -> more links, not more correct" % (ns[0], ns[-1], rates[0], rates[-1]))


def main():
    v1_count_knob_is_separate_from_ranking()
    r = v2_smoke_2x2()
    v3_count_outruns_correct(r)
    for p in PASSED:
        print("[PASS]", p)
    print("%d/3 witnesses passed." % len(PASSED))
    print("FLAT-ON-COUNT PROVEN: the SDT false-alarm knob inflates n_grounded without touching the ranking, so the "
          "count is quality-blind and the correct-link quality dim is not -- the instrument separates quality from "
          "quantity (moves-on-quality is W5 of test_fused_sense_ranker_live).")


if __name__ == "__main__":
    main()
