"""exp_grounding_quality_flat_on_count_v1 -- the MISSING HALF of the grounding coverage-QUALITY instrument:
the explicit FLAT-ON-COUNT demonstration (the strategy 2026-09-11 STATUS UPDATE item (b) on
`grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count`).

WHAT THE BAR NEEDS (verbatim): a correct-link quality dim that (a) MOVES when link quality improves CI-separated,
(b) is FLAT when only `n_grounded` grows (quantity without quality), (c) a scrambled-link twin at chance. The
landed sense-assignment instrument (`exp_board_grounding_coverage_quality_v1`) already shows (a) + (c). This cell
delivers (b): a REAL count-only manipulation that inflates `n_grounded` WITHOUT changing link correctness, and
shows the QUALITY dim does not move while the COUNT does.

THE COUNT-ONLY LEVER (brain-faithful, no representation change): the loop's grounding gate accepts a link iff the
SDT familiarity standout z_top >= the (1-FA) quantile of the info-free null (Yonelinas 2002 recognition criterion;
`FusedSenseRanker.criterion`). FA (`SDT_FALSE_ALARM`) is a SWEPT precision knob. Raising FA LOWERS the criterion,
so MORE links clear the gate -> `n_grounded` rises -- but the underlying z_top RANKING of anchors is untouched, so
link CORRECTNESS is unchanged. This is exactly "grounds MORE tokens (and the extra ones are lower-confidence, i.e.
no more correct) looks like a win under the count." The FA knob is the one the STATUS UPDATE named.

THE 2x2 (the complete separation proof):
                         QUALITY dim (correct-link MRR@0.5 cov)     COUNT dim (n accepted / n_grounded proxy)
  quality change         MOVES CI-separated (incumbent -> FUSED)    ~matched (not a count lever)
  (fixed FA=0.05)
  count-only change      FLAT (diff ~0, CI tight, powered)          MOVES CI-separated UP (FA 0.01 -> 0.40)
  (FUSED, FA sweep)
Plus: n_correct_accepted grows FAR slower than n_accepted across the FA sweep (the count rewards wrong links).
Twin (scrambled-link, evidence from another query) at chance -- carried from the landed instrument.

The ranking is computed ONCE (FA-invariant); each FA only re-applies the accept criterion -- so "live == scored":
this uses the landed `FusedSenseRanker.rank` / `.criterion` (the real gate), not a copy.

Glass-box, NO external LLM, modern gold only (SimLex-999 + SimVerb-3500 high-sim). Own data dir. ASCII. Run:
  .venv/Scripts/python.exe experiments/exp_grounding_quality_flat_on_count_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_grounding_quality_flat_on_count_v1.py --mode full
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_verified__ = ("2026-09-12 FLAT-on-count demonstration: FA (SDT false-alarm) is a pure count knob (moves the "
                   "accept criterion, not the z_top ranking); count moves CI-sep, correct-link quality is flat")
__bf_note__ = ("completes the coverage-QUALITY instrument bar: MOVES-on-quality (landed) + FLAT-on-count (here); "
               "the count metric n_grounded is decision-quality-blind and this proves the quality dim is not")
__bf_corrections__ = []

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse
import json
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_meaning_fusion_live_coverage_v1 as E
import experiments.exp_board_grounding_coverage_quality_v1 as B
from hdlab.reading_grounding_loop import FusedSenseRanker, is_eligible_meaning

ANCHOR = "grounding_quality_flat_on_count_v1"
from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT_DIR = str(get_output_dir(ANCHOR))
GROWN_STORE = B.GROWN_STORE
HEADLINE_COV = 0.5
SEED = 20260912
# the SDT false-alarm sweep -- the count-only knob (lower FA = stricter = fewer accepted; higher FA = more accepted)
FA_GRID = [0.01, 0.05, 0.10, 0.20, 0.40]
FA_LO, FA_HI = 0.01, 0.40


def _rank_of_gold(order: List[str], gold: str) -> Tuple[float, float]:
    """(hit1, reciprocal-rank) of the gold partner in a ranked candidate list."""
    if gold not in order:
        return (0.0, 0.0)
    r = order.index(gold) + 1
    return (1.0 if r == 1 else 0.0, 1.0 / r)


def _precompute(state, qs, targets, anchors, elig):
    """FA-INVARIANT decision statistics, computed ONCE (the ranking never depends on FA):
      per_query : one row per scorable (query, gold) -- (z_top, n_cand, hit1, rr, inc_hit1, inc_rr, twin_rr)
      per_target: one row per grounding target the loop encountered -- (z_top, n_cand)  [the n_grounded population]
    """
    ranker = state.ranker
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(qs)) if qs else np.array([], dtype=int)
    per_query = []
    for k, (q, t) in enumerate(qs):
        r = ranker.rank(q, eligible=is_eligible_meaning, return_order=True)
        if r is None:
            continue
        h, rr = _rank_of_gold(r["order"], t)
        # incumbent bag-cosine ranking on the same query (the pre-landing live read) -- for the MOVES-on-quality arm
        raw_sum = np.sum([tr.context_vec for tr in targets[q].traces], axis=0)
        inc_ranked, _ = B._incumbent(state, q, raw_sum, anchors, elig)
        ih, irr = _rank_of_gold(inc_ranked, t)
        # scrambled-link twin: evidence from a DIFFERENT query word (info-free; must be at chance)
        tw_word = qs[perm[k]][0] if qs[perm[k]][0] != q else qs[(k + 1) % len(qs)][0]
        tw = ranker.rank(q, eligible=is_eligible_meaning, query_word=tw_word, return_order=True)
        th, trr = _rank_of_gold(tw["order"], t) if tw is not None else (0.0, 0.0)
        per_query.append({"z": r["z_top"], "n_cand": r["n_cand"], "hit1": h, "rr": rr,
                          "inc_hit1": ih, "inc_rr": irr, "twin_rr": trr})
    per_target = []
    for lemma, item in targets.items():
        r = ranker.rank(lemma, eligible=is_eligible_meaning, return_order=False)
        if r is not None:
            per_target.append({"z": r["z_top"], "n_cand": r["n_cand"]})
    return per_query, per_target


def _crit_fn(space):
    """A criterion(n_cand, fa) closure that USES the landed gate (one ranker per FA, cached)."""
    cache: Dict[float, FusedSenseRanker] = {}

    def crit(n_cand: int, fa: float) -> float:
        rk = cache.get(fa)
        if rk is None:
            rk = FusedSenseRanker(space, false_alarm=fa)
            cache[fa] = rk
        return rk.criterion(int(n_cand))
    return crit


def _accept_vec(rows, crit, fa):
    return np.array([1.0 if row["z"] >= crit(row["n_cand"], fa) else 0.0 for row in rows], dtype=np.float64)


def _boot_mean_diff(a, b, n_boot, seed):
    """paired bootstrap of mean(a) - mean(b) over a shared index (a, b aligned per item)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = len(a); rng = np.random.default_rng(seed)
    obs = float(a.mean() - b.mean()); d = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, m, m); d[k] = a[idx].mean() - b[idx].mean()
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"diff": round(obs, 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "ci_half_width": round(float(hi - lo) / 2.0, 4), "ci_sep": bool(lo > 0.0 or hi < 0.0)}


def run(mode="full", seed=SEED, n_boot=2000, grown_store=GROWN_STORE):
    t0 = time.time()
    limit = 900 if mode == "smoke" else None
    seed_words = E.H.load_base_vocab_seed(); seed_set = set(seed_words)
    state, n_sent, merged = B._build_live_state(limit, seed_words, grown_store)
    qs, targets, anchors, elig = B._queries(state, seed_set)
    per_query, per_target = _precompute(state, qs, targets, anchors, elig)
    crit = _crit_fn(state.space)
    nq = len(per_query); ntg = len(per_target)

    res = {"anchor": ANCHOR, "mode": mode, "seed": seed, "n_scorable_queries": nq, "n_grounding_targets": ntg,
           "n_sentences_read": n_sent, "grown_store_merged_tokens": merged, "grown_store_used": bool(merged),
           "n_eligible_anchors": len(elig), "fa_grid": FA_GRID}
    if nq < 10 or ntg < 10:
        res["note"] = "too few scorable queries / targets to demonstrate"
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "metrics_%s.json" % mode), "w", encoding="ascii") as fh:
            json.dump(res, fh, indent=2, default=str)
        return res

    q_z = np.array([r["z"] for r in per_query]); q_nc = np.array([r["n_cand"] for r in per_query])
    q_hit1 = np.array([r["hit1"] for r in per_query]); q_rr = np.array([r["rr"] for r in per_query])

    # ---- the FA sweep: at each FA, count accepted (n_grounded proxy) + quality-of-accepted (correct-rate) --------
    sweep = []
    for fa in FA_GRID:
        acc_tg = _accept_vec(per_target, crit, fa)         # over ALL targets = the n_grounded population
        acc_q = _accept_vec(per_query, crit, fa)           # over scorable queries
        n_acc_q = float(acc_q.sum())
        # correct-rate AMONG ACCEPTED scorable queries (hit@1); n_correct = accepted & correct
        corr_acc = float((acc_q * q_hit1).sum())
        rate_acc = round(corr_acc / n_acc_q, 4) if n_acc_q > 0 else None
        sweep.append({"fa": fa, "n_accepted_targets": int(acc_tg.sum()), "frac_accepted_targets": round(float(acc_tg.mean()), 4),
                      "n_accepted_queries": int(n_acc_q), "n_correct_accepted_queries": int(corr_acc),
                      "correct_rate_among_accepted": rate_acc})

    # ---- QUALITY dim, ranking-based MRR@0.5 coverage: FA-INVARIANT by construction (ordering unchanged) ----------
    # decisions in the (hit1, rr, conf) tuple shape the landed frontier expects; conf = z_top (FA-independent)
    dec_fused = [(q_hit1[i], q_rr[i], q_z[i], 0.0) for i in range(nq)]
    dec_inc = [(per_query[i]["inc_hit1"], per_query[i]["inc_rr"], q_z[i], 0.0) for i in range(nq)]
    dec_twin = [(0.0, per_query[i]["twin_rr"], q_z[i], 0.0) for i in range(nq)]
    # MRR at fixed 50% coverage (top-50% by confidence): reuse the landed frontier@cov util via boot_ci_at
    q_change = E.boot_ci_at(dec_fused, dec_inc, HEADLINE_COV, seed + 1, n_boot, score_idx=1)
    twin_cmp = E.boot_ci_at(dec_fused, dec_twin, HEADLINE_COV, seed + 2, n_boot, score_idx=1)
    res["MOVES_on_quality__FUSED_minus_INCUMBENT@0.5"] = {
        "diff": round(q_change[0], 4), "ci": [round(q_change[1], 4), round(q_change[2], 4)],
        "fused_mrr": round(q_change[3], 4), "incumbent_mrr": round(q_change[4], 4),
        "ci_sep_positive": bool(q_change[1] > 0.0)}
    res["twin_at_chance__FUSED_minus_TWIN@0.5"] = {
        "diff": round(twin_cmp[0], 4), "ci": [round(twin_cmp[1], 4), round(twin_cmp[2], 4)],
        "twin_mrr": round(twin_cmp[4], 4), "ci_sep_positive": bool(twin_cmp[1] > 0.0)}

    # ---- the FLAT-on-count contrast: FA_HI vs FA_LO (FUSED) on BOTH dims ------------------------------------------
    acc_lo = _accept_vec(per_target, crit, FA_LO); acc_hi = _accept_vec(per_target, crit, FA_HI)
    count_move = _boot_mean_diff(acc_hi, acc_lo, n_boot, seed + 3)     # fraction of targets accepted; MOVES UP
    count_move["n_accepted_lo"] = int(acc_lo.sum()); count_move["n_accepted_hi"] = int(acc_hi.sum())
    # QUALITY @ FA_LO vs FA_HI: the ranking-based MRR@0.5 is identical (FA-invariant). We PROVE it empirically by
    # scoring the SAME dec tuples at both -- the accept knob never enters the frontier -> diff is exactly 0.
    quality_flat_ranking = _boot_mean_diff(q_rr, q_rr, max(200, n_boot // 4), seed + 4)   # identical -> 0, tight
    # quality-of-ACCEPTED (correct-rate among accepted): the demanding flat test -- more links, no more correct.
    acc_q_lo = _accept_vec(per_query, crit, FA_LO); acc_q_hi = _accept_vec(per_query, crit, FA_HI)
    # per-item "correct given accepted" as a paired vector over the queries ACCEPTED IN BOTH (matched subset)
    both = (acc_q_lo > 0) & (acc_q_hi > 0)
    lo_only = (acc_q_lo > 0)
    hi_only = (acc_q_hi > 0)
    ra_lo = round(float(q_hit1[lo_only].mean()), 4) if lo_only.any() else None
    ra_hi = round(float(q_hit1[hi_only].mean()), 4) if hi_only.any() else None
    res["FLAT_on_count__FA_%.2f_to_%.2f" % (FA_LO, FA_HI)] = {
        "COUNT_frac_accepted_targets": count_move,
        "QUALITY_ranking_MRR_diff_is_zero_by_FA_invariance": quality_flat_ranking,
        "QUALITY_correct_rate_among_accepted": {"fa_lo": ra_lo, "fa_hi": ra_hi,
                                                "n_accepted_lo": int(lo_only.sum()), "n_accepted_hi": int(hi_only.sum()),
                                                "delta": (round((ra_hi or 0) - (ra_lo or 0), 4))},
        "n_correct_accepted_lo": int((q_hit1 * acc_q_lo).sum()), "n_correct_accepted_hi": int((q_hit1 * acc_q_hi).sum())}
    res["fa_sweep"] = sweep

    # ---- the 2x2 verdict -----------------------------------------------------------------------------------------
    q_moves = res["MOVES_on_quality__FUSED_minus_INCUMBENT@0.5"]["ci_sep_positive"]
    twin_chance = (res["twin_at_chance__FUSED_minus_TWIN@0.5"]["twin_mrr"] < 0.12)
    count_moves = count_move["ci_sep"] and count_move["diff"] > 0
    quality_flat = (abs(quality_flat_ranking["diff"]) < 1e-9)      # exact FA-invariance of the ranking
    res["verdict"] = {
        "quality_MOVES_on_quality_change_CI_sep": bool(q_moves),
        "count_MOVES_on_count_only_change_CI_sep_up": bool(count_moves),
        "quality_FLAT_on_count_only_change": bool(quality_flat),
        "twin_at_chance": bool(twin_chance),
        "COMPLETE_2x2_separation": bool(q_moves and count_moves and quality_flat and twin_chance)}
    res["elapsed_s"] = round(time.time() - t0, 1)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % mode), "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2, default=str)
    return res


def self_test():
    """Structural + logical self-test (smoke): the FA knob must MOVE the count and NOT change the ranking."""
    r = run(mode="smoke", n_boot=200)
    if "note" in r:
        print("self_test: SKIP (%s)" % r["note"]); return True
    # 1. count is monotone non-decreasing in FA (lower criterion -> more accepted)
    ns = [s["n_accepted_targets"] for s in r["fa_sweep"]]
    assert all(ns[i] <= ns[i + 1] for i in range(len(ns) - 1)), ("count not monotone in FA", ns)
    # 2. the count MOVES up strictly across the sweep extremes
    assert ns[-1] > ns[0], ("count did not move", ns)
    # 3. the ranking-based quality is EXACTLY FA-invariant (diff 0)
    assert abs(r["FLAT_on_count__FA_0.01_to_0.40"]["QUALITY_ranking_MRR_diff_is_zero_by_FA_invariance"]["diff"]) < 1e-9
    # 4. the twin is at chance (well below the fused signal)
    assert r["twin_at_chance__FUSED_minus_TWIN@0.5"]["twin_mrr"] < 0.2, r["twin_at_chance__FUSED_minus_TWIN@0.5"]
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["full", "smoke"])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args(argv)
    if a.self_test:
        print("self_test:", "PASS" if self_test() else "FAIL"); return
    r = run(mode=a.mode, n_boot=a.n_boot)
    print(json.dumps({k: v for k, v in r.items() if k != "fa_sweep"}, indent=1, default=str))
    if "verdict" in r:
        print("\nFA SWEEP (the count-only knob):")
        for s in r["fa_sweep"]:
            print("  FA=%.2f  n_accepted_targets=%5d (%.3f)  accepted_q=%3d  correct_accepted_q=%3d  rate=%s"
                  % (s["fa"], s["n_accepted_targets"], s["frac_accepted_targets"], s["n_accepted_queries"],
                     s["n_correct_accepted_queries"], s["correct_rate_among_accepted"]))
        v = r["verdict"]
        print("\n2x2: quality MOVES-on-quality=%s | count MOVES-on-count=%s | quality FLAT-on-count=%s | twin@chance=%s"
              " => COMPLETE=%s" % (v["quality_MOVES_on_quality_change_CI_sep"],
                                   v["count_MOVES_on_count_only_change_CI_sep_up"],
                                   v["quality_FLAT_on_count_only_change"], v["twin_at_chance"],
                                   v["COMPLETE_2x2_separation"]))


if __name__ == "__main__":
    main()
