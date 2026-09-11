"""exp_board_grounding_coverage_quality_v1 -- the COVERAGE-QUALITY instrument arm for the reading-grounding loop
(landed 2026-09-11 by strategy from owner-DONE pri-5 `measure_end_to_end_whether_the_meaning_fusion_lifts_live_
grounding_coverage`, SOLVED "hdlab proposal" item 3 + W20: the loop's coverage COUNT `n_grounded` is decision-
quality-blind, so a sense-assignment quality gain is BOARD-INVISIBLE without its own instrument).

WHAT IT SCORES: the LIVE sense-assignment read as it actually runs -- `hdlab.reading_grounding_loop.FusedSenseRanker`
on a `ReadingLoopState` fed by the loop's REAL ingest (`process_sentence` over the curriculum the loop reads, seed
vocabulary = the loop's anchors) -- against the INCUMBENT bag-cosine read (canonicalize's representation) on the
same field, same queries. "live == scored": the arm calls the landed organ, not a copy.

POPULATION: SimLex-999 + SimVerb-3500 HIGH-similarity pairs (modern human gold, non-circular), restricted to the
loop's own decision: the gold partner must be an ELIGIBLE ANCHOR (seed-known, profiled) and the query a NON-SEED word
the loop actually encountered (a grounding target with traces) -- the exact shape of canonicalize's live decision.
QUALITY = reciprocal rank of the gold partner among the eligible anchors; HEADLINE = MRR at 50% coverage (each arm
ordered by its OWN confidence: z_top for the fused read, best cosine for the incumbent), area-under-frontier reported.
  model    FUSED         grounded-distinctive (+) grown-SEQ (+) referent (the landed live read)
  floor    INCUMBENT     bag-of-context cosine (what the loop ranked over before)
  ablation GROUNDED_ONLY the fused read with SEQ + referent OFF (isolates the reading-grown + referent increment)
  twin     TWIN          FUSED with the query's evidence taken from a DIFFERENT query word (info-free; must lose)
GROWN STORE: if data/foundation/seq_store_v1/concept_space_ctx_counts.npz exists (tools/grow_seq_store.py), its
directional counts are MERGED into the field before scoring (the W20 exposure lever); the row says which.

Glass-box, NO external LLM. Own data dir. ASCII. Run:
  .venv/Scripts/python.exe experiments/exp_board_grounding_coverage_quality_v1.py --smoke | (full)
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_verified__ = ("2026-09-11 instrument: scores the landed FusedSenseRanker on the loop's own live field (real "
                   "ingest) vs the incumbent bag-cosine; twin + ablation; SimLex/SimVerb modern gold")
__bf_note__ = ("coverage-QUALITY instrument (correct-link MRR at matched coverage) for the reading-grounding loop; "
               "the count metric is quality-blind")
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
from experiments.exp_ppc_second_gold_powerup_v1 import _load_simverb_high
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (ReadingLoopState, FusedSenseRanker, seed_known_words, process_sentence,
                                          is_eligible_meaning, KNOWN_RELATION, MEANING_RELATION)

ANCHOR = "board_grounding_coverage_quality_v1"
OUT_DIR = os.path.join(_REPO, "data", ANCHOR)
GROWN_STORE = os.path.join(_REPO, "data", "foundation", "seq_store_v1", "concept_space_ctx_counts.npz")
HEADLINE_COV = 0.5
SEED = 20260911


def _build_live_state(limit: Optional[int], seed_words, grown_store: Optional[str]):
    st = HDFactStore(n_dim=2048, seed=1, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                                               MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    state = ReadingLoopState(store=st)          # LIVE default: fused ranking ON, directional tracking ON
    assert state.fused_ranking and state.ranker is not None
    seed_known_words(state, seed_words, "seed")
    pool = E.H.build_curriculum_pool(limit_sentences=limit)
    for i, (_t, sent) in enumerate(pool):
        process_sentence(state, sent, "e%d" % i, pass_idx=0)
    merged = 0
    if grown_store and os.path.isfile(grown_store):
        from hdlab.foundation_persistence import load_ctx_counts_into
        merged = load_ctx_counts_into(state.space, grown_store)
    return state, len(pool), merged


def _queries(state, seed_set):
    anchors, _ = state.space.anchor_matrix()
    elig = {a for a in anchors if is_eligible_meaning(a)}
    # a grounding TARGET = a non-seed word the loop encountered (has Library traces -> a distributional bundle)
    targets = {l: it for l, it in state.library.items.items() if it.traces and l not in seed_set}
    pairs = [(a, b) for (a, b, _s) in E._load_simlex_high()] + [(a, b) for (a, b, _s) in _load_simverb_high()]
    qs, seen = [], set()
    for a, b in pairs:
        for q, t in ((a, b), (b, a)):
            if q != t and q in targets and t in elig and (q, t) not in seen:
                seen.add((q, t)); qs.append((q, t))
    return qs, targets, anchors, elig


def _incumbent(state, q, raw_sum, anchors, elig):
    _a, mat = state.space.anchor_matrix()
    nb = np.asarray(raw_sum, dtype=np.float64); nn = float(np.linalg.norm(nb))
    norms = np.linalg.norm(mat, axis=1)
    keep = np.array([(a in elig and a != q and n >= 1e-9) for a, n in zip(anchors, norms)], dtype=bool)
    sims = np.full(len(anchors), -np.inf)
    sims[keep] = (mat[keep] @ nb) / (norms[keep] * nn + 1e-12)
    order = np.argsort(-sims, kind="mergesort")
    ranked = [anchors[i] for i in order if keep[i]]
    return ranked, float(sims[order[0]])


def _dec(ranked: List[str], gold: str, conf: float):
    if gold not in ranked:
        return (0.0, 0.0, conf, 0.0)
    r = ranked.index(gold) + 1
    return (1.0 if r == 1 else 0.0, 1.0 / r, conf, 0.0)


def run(mode="full", seed=SEED, n_boot=2000, grown_store=GROWN_STORE):
    t0 = time.time()
    limit = 900 if mode == "smoke" else None
    seed_words = E.H.load_base_vocab_seed(); seed_set = set(seed_words)
    state, n_sent, merged = _build_live_state(limit, seed_words, grown_store)
    qs, targets, anchors, elig = _queries(state, seed_set)
    ranker = state.ranker
    g_only = FusedSenseRanker(state.space, use_seq=False, use_referent=False)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(qs))
    dec = {"FUSED": [], "INCUMBENT": [], "GROUNDED_ONLY": [], "TWIN": []}
    n_fallback = 0
    for k, (q, t) in enumerate(qs):
        raw_sum = np.sum([tr.context_vec for tr in targets[q].traces], axis=0)
        inc_ranked, inc_conf = _incumbent(state, q, raw_sum, anchors, elig)
        dec["INCUMBENT"].append(_dec(inc_ranked, t, inc_conf))
        r = ranker.rank(q, eligible=is_eligible_meaning, return_order=True)
        if r is None:                                        # live fallback: the incumbent decides
            n_fallback += 1; dec["FUSED"].append(_dec(inc_ranked, t, inc_conf))
        else:
            dec["FUSED"].append(_dec(r["order"], t, r["z_top"]))
        g = g_only.rank(q, eligible=is_eligible_meaning, return_order=True)
        dec["GROUNDED_ONLY"].append(_dec(inc_ranked, t, inc_conf) if g is None else _dec(g["order"], t, g["z_top"]))
        tw_word = qs[perm[k]][0] if qs[perm[k]][0] != q else qs[perm[(k + 1) % len(qs)]][0]
        tw = ranker.rank(q, eligible=is_eligible_meaning, query_word=tw_word, return_order=True)
        dec["TWIN"].append(_dec(inc_ranked, t, inc_conf) if tw is None else _dec(tw["order"], t, tw["z_top"]))
    n = len(qs)
    res = {"anchor": ANCHOR, "mode": mode, "seed": seed, "n_queries": n, "n_sentences_read": n_sent,
           "grown_store_merged_tokens": merged, "grown_store_used": bool(merged),
           "n_anchors": len(anchors), "n_eligible_anchors": len(elig), "n_targets": len(targets),
           "n_fused_fallback_to_incumbent": n_fallback, "ranker_stats": dict(ranker.stats),
           "sdt_criterion_example": ranker.criterion(len(elig))}
    if n < 10:
        res["note"] = "too few anchor-pool queries to score"
        return res
    auf = {a: round(E.area_under_frontier(d, score_idx=1), 4) for a, d in dec.items()}
    mrr_all = {a: round(float(np.mean([x[1] for x in d])), 4) for a, d in dec.items()}
    hit_all = {a: round(float(np.mean([x[0] for x in d])), 4) for a, d in dec.items()}

    def _ci(a, b, s):
        diff, lo, hi, pa, pb = E.boot_ci_at(dec[a], dec[b], HEADLINE_COV, seed + s, n_boot, score_idx=1)
        return {"diff": round(diff, 4), "ci": [round(lo, 4), round(hi, 4)], "a": round(pa, 4), "b": round(pb, 4),
                "ci_sep_positive": bool(lo > 0.0)}
    res.update({"AUF_MRR": auf, "MRR_all": mrr_all, "hit1_all": hit_all,
                "FUSED_minus_INCUMBENT@0.5": _ci("FUSED", "INCUMBENT", 1),
                "FUSED_minus_TWIN@0.5": _ci("FUSED", "TWIN", 2),
                "FUSED_minus_GROUNDED_ONLY@0.5": _ci("FUSED", "GROUNDED_ONLY", 3),
                "GROUNDED_ONLY_minus_INCUMBENT@0.5": _ci("GROUNDED_ONLY", "INCUMBENT", 4),
                "elapsed_s": round(time.time() - t0, 1)})
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % mode), "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2, default=str)
    return res


def board_grounding_coverage_quality_dimension(smoke=False, n_boot=2000):
    """Board row (schema-matched): model = FUSED MRR@0.5 coverage; floor = INCUMBENT (the pre-landing live read);
    ablation GROUNDED_ONLY in floor_accs; twin = info-free evidence swap. OUT of the headline aggregate."""
    try:
        r = run(mode="smoke" if smoke else "full", n_boot=n_boot)
        if "note" in r:
            return {"n": r["n_queries"], "model_acc": None, "informational": True, "population": r["note"]}, r
        fi = r["FUSED_minus_INCUMBENT@0.5"]; ft = r["FUSED_minus_TWIN@0.5"]; fg = r["FUSED_minus_GROUNDED_ONLY@0.5"]
        floors = {"incumbent_bag_cosine": fi["b"], "grounded_only_ablation": fg["b"]}
        strongest = max(floors, key=floors.get)
        vs = fi if strongest == "incumbent_bag_cosine" else fg
        row = {"n": r["n_queries"], "model_acc": fi["a"], "overlap_floor": fi["b"], "floor_accs": floors,
               "strongest_floor_name": strongest, "strongest_floor": floors[strongest], "twin_acc": ft["b"],
               "model_minus_strongest": [vs["diff"]] + vs["ci"],
               "model_minus_twin": [ft["diff"]] + ft["ci"],
               "ci_sep_over_strongest": bool(vs["ci_sep_positive"]),
               "ci_sep_over_twin": bool(ft["ci_sep_positive"]),
               "population": ("reading-grounding loop LIVE sense-assignment decision (real ingest, %d sentences%s): "
                              "SimLex/SimVerb high-sim queries whose gold partner is an eligible anchor and whose "
                              "query is a non-seed grounding target (n=%d); quality = MRR of the gold partner at 50%% "
                              "coverage; model = FUSED (grounded-distinctive + grown-SEQ + referent, SDT criterion); "
                              "floor = the incumbent bag-cosine read; ablation = grounded-only; twin = evidence from "
                              "another query word." % (r["n_sentences_read"],
                                                       ", + grown SEQ store" if r["grown_store_used"] else "",
                                                       r["n_queries"]))}
        return row, r
    except Exception as e:  # never crash the board
        return {"n": 0, "model_acc": None, "informational": True,
                "error": "%s: %s" % (type(e).__name__, e)}, {}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args(argv)
    r = run(mode="smoke" if a.smoke else "full", n_boot=a.n_boot)
    print(json.dumps({k: v for k, v in r.items() if k != "ranker_stats"}, indent=1, default=str))
    if "AUF_MRR" in r:
        fi = r["FUSED_minus_INCUMBENT@0.5"]; ft = r["FUSED_minus_TWIN@0.5"]; fg = r["FUSED_minus_GROUNDED_ONLY@0.5"]
        print("HEADLINE n=%d FUSED MRR@0.5=%.4f vs INCUMBENT %.4f (diff %+.4f CI %s sep=%s) | vs TWIN %+.4f sep=%s"
              " | vs GROUNDED_ONLY %+.4f sep=%s | grown_store=%s"
              % (r["n_queries"], fi["a"], fi["b"], fi["diff"], fi["ci"], fi["ci_sep_positive"], ft["diff"],
                 ft["ci_sep_positive"], fg["diff"], fg["ci_sep_positive"], r["grown_store_used"]))


if __name__ == "__main__":
    main()
