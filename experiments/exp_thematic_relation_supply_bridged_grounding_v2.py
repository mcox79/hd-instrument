"""exp_thematic_relation_supply_bridged_grounding_v2 -- does a word grounded ONLY by bridging carry
meaning ONCE THE BRAIN'S SECOND RELATIONAL HUB IS SUPPLIED?

PRE-REG: preregs/2026-08-16_thematic_relation_supply_bridged_grounding_v2.md
         (all thresholds fixed BEFORE any run; this file never edits them)
SIBLING: experiments/exp_bridged_grounding_from_core_v1.py -- IMPORTED AS A LIBRARY, NEVER EDITED.
         It is landed with verdict POWER_INSUFFICIENT_ON_THE_PRIMARY_STRATUM and that verdict is
         CORRECT: it is the record of what a TAXONOMIC-ONLY relation graph supports (n=47,
         mean in-CORE bridge degree 1.216, V=0).
SUPPLY:  .claude/scan-out/relation-supply.json -- the scan that made this testable.

WHAT CHANGED, AND IT IS A BRAIN-FIDELITY CHANGE, NOT A TUNING CHANGE:
  TAXONOMIC relations (anterior temporal lobe) and THEMATIC relations (a SEPARATE temporo-parietal
  system: posterior middle temporal gyrus + angular gyrus) are distinct organising principles of
  semantic memory with a clean lesion double dissociation [PINNED: Schwartz et al. 2011 PNAS;
  Mirman, Landrigan & Britt 2017 Psych Bull 143:499], and thematic organisation is developmentally
  PRIOR [PINNED: Nelson/Lucariello slot-filler]. Every one of our 5,799 extracted relations was
  taxonomic. WE HAD BUILT ONE OF THE TWO HUBS. This cell supplies the other, from our OWN organs,
  on the IDENTICAL 64,000,000-byte simplewiki budget the frequency floor is computed on.
  Measured supply effect: mean in-CORE bridge degree 1.216 -> 3.573, primary stratum 47 -> 394,
  both-endpoints 4 -> 138, VERBS 0 -> 86 (the Hills-2009 noun-specific falsifier becomes runnable
  on our own graph for the first time).

  THE EDGE RULE IS OURS -- INVENTION UNDER TEST. The literature pins that thematic relations exist,
  are carried separately, and are action/location-flavoured. It pins NO extraction rule and NO
  combination equation. FIVE additive transformations are tested here and ALL FIVE ARE OURS.

  PRE-REGISTERED HONESTY LINE (prereg section 8, must travel with any number this cell produces):
  the thematic channel is DISTRIBUTIONALLY DERIVED from our own corpus. That is brain-real
  (language transports relational structure into a modality the learner cannot experience --
  Kim, Elli & Bedny, blind colour) and it is OURS, not a pretrained table. But this arm tests
  "can our own event-co-participation relations TRANSPORT GROUNDING", which is a HYBRID
  distributional + grounded claim and is labelled as such, never as pure relational inheritance.

TRAPS GUARDED, re-verified by RUNTIME in selftest() every run, never inherited:
  hdlab.grounded_similarity.grounded_similarity() SATURATES >70% of SimLex pairs onto two values.
  It is NEVER the scorer. The scorer is the raw 12-dim vector, L2-normalised, plain cosine.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. No pretrained embedding or co-occurrence
table in any arm. The CSKG arm is CEILING REFERENCE ONLY, on the same footing as GloVe, and a pass
on it is never a wiring recommendation.

ASCII-only. CPU. No network. data/foundation/** is opened READ-ONLY and never written.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS          # THE INSTRUMENT, IMPORTED, NEVER EDITED
import exp_meaning_asset_fair_test_v1 as FT               # the Phase-1 verdict machinery, unchanged
import exp_bridged_grounding_from_core_v1 as CELL         # THE SIBLING CELL, IMPORTED, NEVER EDITED
import thematic_relation_extractor_v1 as THEM             # promoted out of scratch/ this pass
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "thematic_relation_supply_bridged_grounding_v2"
CODE_VERSION = "v2.0"
PREREG = "preregs/2026-08-16_thematic_relation_supply_bridged_grounding_v2.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = bool(_ARGS.smoke) or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
RUN_MODE = "smoke" if SMOKE else "full"

# ------------------------------------------------------------------------------------------
# PRE-REGISTERED CONSTANTS -- prereg section 6. NOT EDITED AFTER A RUN.
# ------------------------------------------------------------------------------------------
AOA_CORE_MAX = CELL.AOA_CORE_MAX                 # 6.0, identical to the sibling
THEMATIC_MIN_COUNT = 5
THEMATIC_MIN_PMI = 2.0
THEMATIC_TOPK = 24
T_MARGIN_MIN = FT.T_MARGIN_MIN                   # 0.05
N_BOOT = 2000 if SMOKE else 10000
N_PERM = 400 if SMOKE else 2000
NULL_SEEDS = (7, 13, 17, 23, 29)
HUB_INDEGREE_MAX = CELL.HUB_INDEGREE_MAX         # 10
POS_MIN_N = CELL.POS_MIN_N                       # 25
COOC_MIN_COUNT = 2
BOOT_SEED = 20260816
ORTHO_DIMS = CELL.ORTHO_DIMS
MIDDLE_BAND_FRAC = CELL.MIDDLE_BAND_FRAC

FLOOR_ORTHO = "F_ORTHOGRAPHIC"                   # names chosen so tools/c3_gate.py can READ them
FLOOR_FREQ = "F_FREQUENCY_HARDENED"
FLOOR_SCRAM = "F_SCRAMBLE_PERM_P95"

BRIDGE_ARMS = ("B1_BRIDGE_MEAN", "B2_BRIDGE_PMI_WEIGHTED", "B3_BRIDGE_UNIT_MEAN",
               "B4_BRIDGE_MEDIAN", "B5_BRIDGE_TOP3_PMI")
PRIMARY_ARM = "B1_BRIDGE_MEAN"
NULL_TAGS = ("N1_NULL_ARM_MATCHED_REWIRE", "N2_NULL_ARM_RANDOM_TARGET")
POS_ARMS = ("K1_OWN_NORMS", "K2_ORACLE_BRIDGE", "B1_BRIDGE_MEAN")

_ORTHO_CACHE: Dict[int, np.ndarray] = {}


# ------------------------------------------------------------------------------------------
# graph construction -- the ONE genuinely new component
# ------------------------------------------------------------------------------------------
def undirected(rows: Sequence[Tuple[str, str, float]]) -> Dict[str, Dict[str, float]]:
    g: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
    for a, b, w in rows:
        if a == b:
            continue
        g[a][b] = max(g[a].get(b, -1e9), w)
        g[b][a] = max(g[b].get(a, -1e9), w)
    return dict(g)


def merge(*graphs: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    g: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
    for gg in graphs:
        for a, nb in gg.items():
            for b, w in nb.items():
                g[a][b] = max(g[a].get(b, -1e9), w)
    return dict(g)


def cap_topk(g: Dict[str, Dict[str, float]], k: int = THEMATIC_TOPK) -> Dict[str, Dict[str, float]]:
    """Cap neighbours per word, highest PMI first. A hub cannot buy a degree statistic."""
    out = {}
    for a, nb in g.items():
        if len(nb) <= k:
            out[a] = dict(nb)
        else:
            out[a] = dict(sorted(nb.items(), key=lambda kv: (-kv[1], kv[0]))[:k])
    return out


def build_thematic_graph(edges: Dict) -> Tuple[Dict[str, Dict[str, float]], Dict]:
    """EVENT CO-PARTICIPATION edges at the pre-registered gates. OURS -- INVENTION UNDER TEST."""
    ev = [(a, b, p) for a, b, c, p, _v in edges["event"]
          if c >= THEMATIC_MIN_COUNT and p >= THEMATIC_MIN_PMI]
    g = cap_topk(undirected(ev))
    info = {"gate": {"min_count": THEMATIC_MIN_COUNT, "min_pmi": THEMATIC_MIN_PMI,
                     "topk": THEMATIC_TOPK},
            "n_event_edges_before_gate": len(edges["event"]),
            "n_event_edges_after_gate": len(ev),
            "n_nodes_after_topk": len(g),
            "STATUS": "OURS -- INVENTION UNDER TEST (the literature pins no extraction rule)"}
    return g, info


def partner_context_filter(graph: Dict[str, Dict[str, float]], held_out: Set[str],
                           partners: Dict[str, Set[str]]) -> Tuple[Dict[str, Dict[str, float]], int, int]:
    """CONTROL C6a -- PARTNER-CONTEXT EXCLUSION.

    Delete every bridge edge (w, n) where n is ALSO a graph neighbour of w's SimLex PARTNER. The
    confound this closes, measured on the primary graph by the supply scan: a held-out word and its
    partner share neighbours at 2.34% vs 0.09% at random, CI-separated (+0.0225 [+0.0147,+0.0310]).
    Neither morphology blocking nor the degree-and-frequency-matched shuffle touches this channel:
    it is SECOND ORDER, through shared neighbours, and partner EXCLUSION alone does not close it.
    """
    out = dict(graph)
    before = after = 0
    for w in held_out:
        nb = graph.get(w)
        if not nb:
            continue
        ctx: Set[str] = set()
        for p in partners.get(w, ()):
            ctx |= set(graph.get(p) or ())
        before += len(nb)
        keep = {n: wt for n, wt in nb.items() if n not in ctx}
        after += len(keep)
        out[w] = keep
    return out, before, after


# ------------------------------------------------------------------------------------------
# floors -- ALL THREE RECOMPUTED ON EVERY STRATUM AND EVERY POS SUB-STRATUM
# ------------------------------------------------------------------------------------------
def _ortho_codes(vocab: List[str], d: int) -> np.ndarray:
    X = _ORTHO_CACHE.get(d)
    if X is None:
        X = INS._l2n(INS.enc_orthographic(vocab, d, 7))
        _ORTHO_CACHE[d] = X
    return X


def build_floors(vocab: List[str], ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
                 counts: Dict[str, int]) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    best = None
    per_d = {}
    for d in ORTHO_DIMS:
        c = CELL.pair_cos(_ortho_codes(vocab, d), ia, ib)
        r = INS._spearman(c, gold)
        per_d[f"d{d}"] = float(r)
        if best is None or r > best[0]:
            best = (r, c, d)
    out[FLOOR_ORTHO] = {"rho": float(best[0]), "per_dim": per_d, "argmax_d": int(best[2]),
                        "_partner": best[1],
                        "what_it_is": "SPELLING CHOOSES THE CODE -- the floor that has beaten this "
                                      "project before (8.70% vs 4.80% on the hit@1 instrument)"}
    lf = np.array([np.log(counts.get(w, 0) + 1.0) for w in vocab], dtype=np.float64)
    la, lb = lf[ia], lf[ib]
    ch = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
          "FREQ_MIN": np.minimum(la, lb),
          "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    rh = {k: float(INS._spearman(v, gold)) for k, v in ch.items()}
    bk = max(rh, key=lambda k: rh[k])
    out[FLOOR_FREQ] = {"rho": rh[bk], "per_channel": rh, "argmax_channel": bk, "_partner": ch[bk]}
    return out


def scramble_floor(X: np.ndarray, ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
                   seed: int) -> Dict:
    """PERMUTATION-CALIBRATED: p95 of the null from permuting the CODE TABLE'S ROWS. Explicitly NOT
    a max of observed draws -- a prior scramble floor was one lucky draw at the 98.6th percentile of
    its own null. The gold-permutation null is computed too and the HIGHER p95 is taken."""
    n = X.shape[0]
    rhos = np.empty(N_PERM)
    for i in range(N_PERM):
        p = np.random.default_rng(seed + i).permutation(n)
        rhos[i] = INS._spearman(CELL.pair_cos(X[p], ia, ib), gold)
    rhos = rhos[np.isfinite(rhos)]
    p95_row = float(np.percentile(rhos, 95))
    obs = CELL.pair_cos(X, ia, ib)
    g_rng = np.random.default_rng(seed ^ 0xBEEF)
    gn = np.array([INS._spearman(obs, gold[g_rng.permutation(len(gold))]) for _ in range(N_PERM)])
    gn = gn[np.isfinite(gn)]
    p95_gold = float(np.percentile(gn, 95))
    p95 = max(p95_row, p95_gold)
    near_i = int(np.argmin(np.abs(rhos - p95)))
    near = CELL.pair_cos(X[np.random.default_rng(seed + near_i).permutation(n)], ia, ib)
    return {"p95": p95, "p95_row_permutation": p95_row, "p95_gold_permutation": p95_gold,
            "row_null_mean": float(rhos.mean()), "row_null_sd": float(rhos.std(ddof=1)),
            "n_perm": int(len(rhos)),
            "permutation_p_value": float((np.sum(rhos >= INS._spearman(obs, gold)) + 1)
                                         / (len(rhos) + 1)),
            "_partner": near}


def score_arm(name: str, X: np.ndarray, ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
              floors: Dict[str, Dict], seed: int, light: bool = False) -> Dict:
    """light=True -> rho only (used for NULL SEED draws; the null FLOOR is the MAX draw and only
    the max draw needs the full treatment). Pre-registered as deviation G; no verdict quantity
    depends on a non-max null draw."""
    obs = CELL.pair_cos(X, ia, ib)
    if light:
        return {"arm": name, "rho": FT.boot_rho(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED),
                "scoring": "LIGHT (rho only; not a verdict-bearing arm)", "_cos": obs}
    sc = scramble_floor(X, ia, ib, gold, seed)
    cands = {FLOOR_ORTHO: (floors[FLOOR_ORTHO]["rho"], floors[FLOOR_ORTHO]["_partner"]),
             FLOOR_FREQ: (floors[FLOOR_FREQ]["rho"], floors[FLOOR_FREQ]["_partner"]),
             FLOOR_SCRAM: (sc["p95"], sc["_partner"])}
    bf = max(cands, key=lambda k: cands[k][0])
    diff = FT.boot_rho_diff(obs, cands[bf][1], gold, n_boot=N_BOOT, seed=BOOT_SEED)
    b = FT.band(diff["ci95"])
    per_floor = {}
    for k, (r, p) in cands.items():
        dd = FT.boot_rho_diff(obs, p, gold, n_boot=N_BOOT, seed=BOOT_SEED)
        per_floor[k] = {"floor_rho": float(r), "margin": dd, "band": FT.band(dd["ci95"])}
    min_ci_lo = min(per_floor[k]["margin"]["ci95"][0] for k in per_floor)
    clears = bool(b == "ABOVE" and diff["point"] >= T_MARGIN_MIN)
    clears_all = bool(clears and min_ci_lo > 0.0)
    middle = bool(clears and (diff["point"] - T_MARGIN_MIN)
                  < MIDDLE_BAND_FRAC * max(abs(diff["ci95"][1] - diff["ci95"][0]), 1e-12))
    return {"arm": name, "rho": FT.boot_rho(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED),
            "strongest_floor": bf, "floor_rho_by_arm": {k: round(v[0], 4) for k, v in cands.items()},
            "margin_over_strongest_floor": diff, "band": b, "clears_floor": clears,
            "clears_ALL_THREE_floors_ci_separated": clears_all,
            "min_ci_lo_over_all_floors": float(min_ci_lo),
            "middle_band": middle,
            "scramble_null": {k: v for k, v in sc.items() if not k.startswith("_")},
            "DECOMPOSED_per_floor": per_floor, "_cos": obs}


# ------------------------------------------------------------------------------------------
# the FIVE additive transformations -- PINNED that combination is additive (Baron & Osherson 2011);
# the transformation itself is UNPINNED, so ALL FIVE ARE OURS-INVENTION-UNDER-TEST
# ------------------------------------------------------------------------------------------
def combine(br: "CELL.Bridger", nbrs: Sequence[Tuple[str, float]], form: str) -> np.ndarray:
    M = np.stack([br.hidden[n] for n, _ in nbrs]).astype(np.float64)
    w = np.array([max(wt, 0.0) for _, wt in nbrs], dtype=np.float64)
    if form == "B1_BRIDGE_MEAN":
        return M.mean(axis=0)
    if form == "B2_BRIDGE_PMI_WEIGHTED":
        return M.mean(axis=0) if w.sum() <= 0 else (M * w[:, None]).sum(axis=0) / w.sum()
    if form == "B3_BRIDGE_UNIT_MEAN":
        nrm = np.linalg.norm(M, axis=1, keepdims=True)
        nrm[nrm <= 0] = 1.0
        return (M / nrm).mean(axis=0)
    if form == "B4_BRIDGE_MEDIAN":
        return np.median(M, axis=0)
    if form == "B5_BRIDGE_TOP3_PMI":
        order = np.argsort(-w, kind="stable")[:3]
        return M[order].mean(axis=0)
    raise ValueError(form)


# ------------------------------------------------------------------------------------------
def _pos_stratified(name: str, cos: np.ndarray, gold: np.ndarray, pos_of: np.ndarray,
                    vocab: List[str], ia: np.ndarray, ib: np.ndarray, counts: Dict[str, int],
                    seed: int, X: np.ndarray) -> Dict:
    """POS strata with their OWN FLOORS recomputed on the sub-stratum. THE FALSIFIER LIVES HERE.

    Hills et al. 2009: 'lure of the associates' predicts NOUN acquisition; a different mechanism
    predicts verbs. IF BRIDGING WORKS EQUALLY WELL ON VERBS AS ON NOUNS WE ARE NOT SEEING THE
    MECHANISM WE THINK WE ARE -- reported as a MECHANISM FAILURE even with a positive headline.
    """
    out: Dict[str, Dict] = {}
    for tag in ("N", "V", "A"):
        m = pos_of == tag
        k = int(m.sum())
        if k < POS_MIN_N:
            out[tag] = {"n": k, "status": "NOT_CONSTRUCTIBLE", "rule":
                        f"n < POS_MIN_N={POS_MIN_N}; this is NOT a null and NOT a passed falsifier"}
            continue
        fl = build_floors(vocab, ia[m], ib[m], gold[m], counts)
        sc = scramble_floor(X, ia[m], ib[m], gold[m], seed + 101)
        cands = {FLOOR_ORTHO: (fl[FLOOR_ORTHO]["rho"], fl[FLOOR_ORTHO]["_partner"]),
                 FLOOR_FREQ: (fl[FLOOR_FREQ]["rho"], fl[FLOOR_FREQ]["_partner"]),
                 FLOOR_SCRAM: (sc["p95"], sc["_partner"])}
        bf = max(cands, key=lambda kk: cands[kk][0])
        dd = FT.boot_rho_diff(cos[m], cands[bf][1], gold[m], n_boot=N_BOOT, seed=BOOT_SEED)
        per_floor = {}
        for kk, (r, p) in cands.items():
            d2 = FT.boot_rho_diff(cos[m], p, gold[m], n_boot=N_BOOT, seed=BOOT_SEED)
            per_floor[kk] = {"floor_rho": float(r), "margin": d2, "band": FT.band(d2["ci95"])}
        out[tag] = {"n": k, "rho": FT.boot_rho(cos[m], gold[m], n_boot=N_BOOT, seed=BOOT_SEED),
                    "strongest_floor": bf,
                    "floor_rho_by_arm": {kk: round(v[0], 4) for kk, v in cands.items()},
                    "margin_over_strongest_floor": dd, "band": FT.band(dd["ci95"]),
                    "clears_floor": bool(FT.band(dd["ci95"]) == "ABOVE"
                                         and dd["point"] >= T_MARGIN_MIN),
                    "DECOMPOSED_per_floor": per_floor}
    return out


def run_config(cfg_name: str, graph: Optional[Dict[str, Dict[str, float]]], sources: Set[str],
               morph_block: bool, hub_censor: bool, ctx: Dict, *,
               restrict_words: Optional[Set[str]] = None,
               pair_filter: Optional[str] = None,
               arm_graphs: Optional[Dict[str, Dict[str, Dict[str, float]]]] = None,
               do_pos: bool = False) -> Dict:
    t0 = time.time()
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, held_out = ctx["idx"], ctx["held_out"]
    partners, counts = ctx["partners"], ctx["counts"]
    br = CELL.Bridger(raw, held_out, partners)

    indeg = None
    if hub_censor and graph is not None:
        c: collections.Counter = collections.Counter()
        for w in held_out:
            for n in (graph.get(w) or {}):
                if n in sources:
                    c[n] += 1
        indeg = dict(c)

    nbrs: Dict[str, List[Tuple[str, float]]] = {}
    edges_before = edges_after = 0
    if graph is not None:
        for w in sorted(held_out):
            if restrict_words is not None and w not in restrict_words:
                continue
            allnb = [(n, wt) for n, wt in (graph.get(w) or {}).items()
                     if br.eligible(w, n, sources, False)]
            edges_before += len(allnb)
            keep = br.neighbours(w, graph, sources, morph_block, indeg)
            edges_after += len(keep)
            if keep:
                nbrs[w] = keep
    else:                                   # ORACLE config: every held-out word is bridgeable
        for w in sorted(held_out):
            nbrs[w] = []
    bridged_words = sorted(nbrs)

    S = set(bridged_words)
    strat = [p for p in pairs if (p[0] in S) != (p[1] in S)]
    n_before_pair_filter = len(strat)
    if pair_filter == "NEVER_COOCCUR":
        cooc = ctx["cooc"]
        strat = [p for p in strat if cooc.get(tuple(sorted((p[0], p[1]))), 0) < COOC_MIN_COUNT]
    n = len(strat)

    res = {"config": cfg_name, "n_stratum": n, "n_stratum_before_pair_filter": n_before_pair_filter,
           "pair_filter": pair_filter, "n_bridged_words": len(bridged_words),
           "morph_block": morph_block, "hub_censor": hub_censor,
           "restricted_word_set": bool(restrict_words is not None),
           "edges_before_control": edges_before, "edges_after_control": edges_after,
           "edges_deleted_by_control": edges_before - edges_after,
           "pos_counts": dict(collections.Counter(p[2] for p in strat)),
           "spearman_ci_halfwidth_approx": (round(1.96 / max(n - 3, 1) ** 0.5, 4) if n > 3 else None),
           "elapsed_s": None}
    if graph is not None and bridged_words:
        deg = [len(nbrs[w]) for w in bridged_words]
        tg = collections.Counter(nn for w in bridged_words for nn, _ in nbrs[w])
        res["bridge_degree"] = {"mean": round(float(np.mean(deg)), 3),
                                "median": int(np.median(deg)), "max": int(max(deg)),
                                "frac_degree_1": round(float(np.mean(np.array(deg) == 1)), 4),
                                "frac_degree_ge3": round(float(np.mean(np.array(deg) >= 3)), 4),
                                "frac_degree_ge5": round(float(np.mean(np.array(deg) >= 5)), 4)}
        res["distinct_bridge_targets"] = len(tg)
        res["top_bridge_targets"] = tg.most_common(8)
        res["ADDITIVITY_EXERCISED"] = bool(np.median(deg) >= 2)
        if np.median(deg) <= 1:
            res["ADDITIVITY_NOT_EXERCISED"] = (
                "median in-source degree <= 1: 'mean over d=1 neighbours' is a SINGLE-NEIGHBOUR "
                "SUBSTITUTION here, so Baron & Osherson additivity is essentially untested")
    if n < 10:
        res["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        res["elapsed_s"] = round(time.time() - t0, 1)
        return res

    ia = np.array([idx[p[0]] for p in strat]); ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)
    floors = build_floors(vocab, ia, ib, gold, counts)
    res["floors"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                     for k, v in floors.items()}

    core_src = sorted(w for w in sources if w in raw and w not in held_out)
    CM = INS._l2n(np.stack([raw[w] for w in core_src]).astype(np.float32))

    def oracle_nbrs(w: str, k: int) -> List[Tuple[str, float]]:
        v = INS._l2n(raw[w][None, :].astype(np.float32))[0]
        s = CM @ v
        out = []
        for j in np.argsort(-s):
            cw = core_src[j]
            if cw == w or cw in partners.get(w, ()):
                continue
            out.append((cw, float(s[j])))
            if len(out) >= k:
                break
        return out

    # ---- arms
    arms: Dict[str, Dict[str, np.ndarray]] = {"K1_OWN_NORMS": {}}
    arms["K2_ORACLE_BRIDGE"] = {w: combine(br, oracle_nbrs(w, 1), "B1_BRIDGE_MEAN")
                                for w in bridged_words}
    arms["K2b_ORACLE_BRIDGE_MEAN3"] = {w: combine(br, oracle_nbrs(w, 3), "B1_BRIDGE_MEAN")
                                       for w in bridged_words}
    if graph is not None:
        for form in BRIDGE_ARMS:
            arms[form] = {w: combine(br, nbrs[w], form) for w in bridged_words}
        if arm_graphs:
            for lbl, g2 in arm_graphs.items():
                tbl = {}
                for w in bridged_words:
                    kk = br.neighbours(w, g2, sources, morph_block, indeg)
                    if kk:
                        tbl[w] = combine(br, kk, "B1_BRIDGE_MEAN")
                arms[lbl] = tbl

        pool = core_src
        lf = np.array([np.log(counts.get(w, 0) + 1.0) for w in pool])
        dec = np.digitize(lf, np.percentile(lf, np.arange(10, 100, 10)))
        by_dec: Dict[int, List[str]] = collections.defaultdict(list)
        for w, dd in zip(pool, dec):
            by_dec[int(dd)].append(w)
        dec_of = {w: int(dd) for w, dd in zip(pool, dec)}
        for tag in NULL_TAGS:
            for s in NULL_SEEDS:
                rng = np.random.default_rng(s ^ 0x51F7)
                tbl = {}
                for w in bridged_words:
                    picks = []
                    for nn, _ in nbrs[w]:
                        cand = by_dec[dec_of.get(nn, 0)] if tag.startswith("N1") else pool
                        for _ in range(64):
                            c2 = cand[int(rng.integers(len(cand)))]
                            if br.eligible(w, c2, sources, False):
                                picks.append((c2, 1.0))
                                break
                    if picks:
                        tbl[w] = combine(br, picks, "B1_BRIDGE_MEAN")
                arms[f"{tag}|s{s}"] = tbl
    else:
        rng = np.random.default_rng(7 ^ 0x51F7)
        tbl = {}
        for w in bridged_words:
            for _ in range(64):
                c2 = core_src[int(rng.integers(len(core_src)))]
                if br.eligible(w, c2, sources, False):
                    tbl[w] = combine(br, [(c2, 1.0)], "B1_BRIDGE_MEAN")
                    break
        arms["N2_NULL_ARM_RANDOM_TARGET|s7"] = tbl

    # ---- G3 arms-must-differ (and the five transformations must not all collapse)
    k1 = CELL.code_matrix(vocab, raw, {})
    gate_g3 = []
    for a in sorted(arms):
        if a == "K1_OWN_NORMS" or not arms[a]:
            continue
        Xa = CELL.code_matrix(vocab, raw, arms[a])
        gate_g3.append({"arm": a, "differs_from_K1": bool(not np.allclose(Xa, k1))})
    res["G3_arms_must_differ"] = gate_g3
    forms_present = [f for f in BRIDGE_ARMS if arms.get(f)]
    sig = set()
    for f in forms_present:
        sig.add(hash(np.round(np.stack([arms[f][w] for w in bridged_words]), 9).tobytes()))
    res["G3_distinct_additive_transformations"] = len(sig)
    res["G3_passed"] = bool(gate_g3 and all(g["differs_from_K1"] for g in gate_g3)
                            and (not forms_present or len(sig) >= 2))

    # ---- score
    rows: Dict[str, Dict] = {}
    cos_by_arm: Dict[str, np.ndarray] = {}
    for a in sorted(arms):
        if a != "K1_OWN_NORMS" and not arms[a]:
            rows[a] = {"arm": a, "status": "NO_BRIDGE_PRODUCED"}
            continue
        Xa = CELL.code_matrix(vocab, raw, arms[a])
        light = a.startswith(NULL_TAGS)
        r = score_arm(a, Xa, ia, ib, gold, floors,
                      seed=int(abs(hash(cfg_name + a)) % 100000) + 11, light=light)
        cos_by_arm[a] = r.pop("_cos")
        r["IDENTITY"] = (CELL.identity_axis(arms[a]) if arms[a]
                         else CELL.identity_axis({w: raw[w] for w in bridged_words}))
        rows[a] = r

    # ---- null floors: the MAX draw, never the mean; the max draw is then FULLY scored
    for tag in NULL_TAGS:
        ks = [k for k in rows if k.startswith(tag + "|") and "rho" in rows[k]]
        if not ks:
            continue
        best = max(ks, key=lambda k: rows[k]["rho"]["point"])
        Xb = CELL.code_matrix(vocab, raw, arms[best])
        rb = score_arm(best, Xb, ia, ib, gold, floors,
                       seed=int(abs(hash(cfg_name + best)) % 100000) + 11, light=False)
        rb.pop("_cos")
        rb["IDENTITY"] = rows[best].get("IDENTITY")
        rb["note"] = "MAX DRAW of this null family -- fully scored; the other seeds are LIGHT"
        rows[best] = rb
        res.setdefault("null_floors", {})[tag] = {
            "n_draws": len(ks), "max_draw_arm": best, "rho_max": rows[best]["rho"]["point"],
            "rho_mean": float(np.mean([rows[k]["rho"]["point"] for k in ks])),
            "policy": "the NULL FLOOR IS THE MAX DRAW, never the mean"}
        for a in list(rows):
            if (a.startswith(("K", "B")) and "rho" in rows[a]):
                dd = FT.boot_rho_diff(cos_by_arm[a], cos_by_arm[best], gold,
                                      n_boot=N_BOOT, seed=BOOT_SEED)
                rows[a].setdefault("vs_nulls", {})[tag] = {"margin": dd, "band": FT.band(dd["ci95"])}

    # ---- retention fraction
    k1c = cos_by_arm.get("K1_OWN_NORMS")
    rho_k1 = rows["K1_OWN_NORMS"]["rho"]["point"] if "K1_OWN_NORMS" in rows else float("nan")
    for a in list(rows):
        if "rho" not in rows[a] or a == "K1_OWN_NORMS":
            continue
        dd = FT.boot_rho_diff(cos_by_arm[a], k1c, gold, n_boot=N_BOOT, seed=BOOT_SEED)
        rows[a]["RETENTION_vs_K1"] = {
            "rho_arm": rows[a]["rho"]["point"], "rho_K1": rho_k1,
            "retention_fraction": (rows[a]["rho"]["point"] / rho_k1
                                   if rho_k1 == rho_k1 and rho_k1 != 0.0 else None),
            "paired_difference": dd, "band": FT.band(dd["ci95"])}

    # ---- POS strata WITH THEIR OWN FLOORS -- the Hills 2009 falsifier
    pos_of = np.array([p[2] for p in strat])
    res["pos_stratified_note"] = (
        "Hills et al. 2009: lure-of-the-associates is NOUN-SPECIFIC. If bridging works EQUALLY "
        "WELL on verbs as on nouns we are NOT seeing that mechanism. K2_ORACLE_BRIDGE uses NO "
        "graph, so if it shows the SAME POS profile the asymmetry belongs to the 12-dim "
        "CONCRETE-SPOKE TARGET SPACE and no ordering claim may be made either way.")
    if do_pos:
        for a in POS_ARMS:
            if a not in rows or "rho" not in rows[a]:
                continue
            Xa = CELL.code_matrix(vocab, raw, arms[a])
            rows[a]["POS_STRATA_WITH_OWN_FLOORS"] = _pos_stratified(
                a, cos_by_arm[a], gold, pos_of, vocab, ia, ib, counts,
                int(abs(hash(cfg_name + a)) % 100000) + 11, Xa)
    for a in list(rows):
        if "rho" not in rows[a]:
            continue
        ps = {}
        for tag in ("N", "V", "A"):
            m = pos_of == tag
            k = int(m.sum())
            ps[tag] = ({"n": k, "status": "NOT_CONSTRUCTIBLE"} if k < POS_MIN_N else
                       {"n": k, "rho": FT.boot_rho(cos_by_arm[a][m], gold[m],
                                                   n_boot=N_BOOT, seed=BOOT_SEED)})
        rows[a]["POS_RHO_ONLY"] = ps

    # ---- G0 POWER GATE, decided BEFORE any treatment number is read
    k1row = rows.get("K1_OWN_NORMS", {})
    res["G0_power_gate"] = {
        "K1_clears_floor": bool(k1row.get("clears_floor")),
        "K1_rho": k1row.get("rho", {}).get("point"),
        "K1_margin": k1row.get("margin_over_strongest_floor", {}).get("point"),
        "K1_band": k1row.get("band"),
        "rule": ("if the KNOWN-ANSWER arm does not clear this stratum's floor, the instrument "
                 "cannot resolve meaning at this n and every bridge arm here is POWER_INSUFFICIENT, "
                 "NEVER FAIL. A bigger n is not a licence to read a null as a refutation.")}
    for a in rows:
        if a.startswith(("B", "K2")) and "rho" in rows[a]:
            if not res["G0_power_gate"]["K1_clears_floor"]:
                rows[a]["verdict_for_this_arm"] = "POWER_INSUFFICIENT"
            else:
                rows[a]["verdict_for_this_arm"] = (
                    "MIDDLE_BAND" if rows[a].get("middle_band")
                    else ("CLEARS_FLOOR" if rows[a]["clears_floor"] else "DOES_NOT_CLEAR_FLOOR"))

    # ---- the ATL-vs-AG decomposition, when this config carries it
    if arm_graphs and "BT_BRIDGE_THEMATIC_ONLY" in cos_by_arm and "BD_BRIDGE_TAXONOMIC_ONLY" in cos_by_arm:
        dd = FT.boot_rho_diff(cos_by_arm["BT_BRIDGE_THEMATIC_ONLY"],
                              cos_by_arm["BD_BRIDGE_TAXONOMIC_ONLY"], gold,
                              n_boot=N_BOOT, seed=BOOT_SEED)
        res["THEMATIC_minus_TAXONOMIC_same_stratum"] = {
            "margin": dd, "band": FT.band(dd["ci95"]),
            "what_it_is": ("ONE-VARIABLE contrast on the IDENTICAL stratum, identical words, "
                           "identical gold: only the RELATION TYPE changes. This is the "
                           "temporo-parietal-vs-anterior-temporal contrast the sibling prereg "
                           "declared NOT CONSTRUCTIBLE (its DEVIATION 4), which was true of the "
                           "FACT FILES and false of the SUBSTRATE.")}

    res["arms"] = rows
    res["elapsed_s"] = round(time.time() - t0, 1)
    print(f"[cfg] {cfg_name:<44} n={n:<4} bridged={len(bridged_words):<4} "
          f"G0={'PASS' if res['G0_power_gate']['K1_clears_floor'] else 'FAIL'} "
          f"({res['elapsed_s']}s)", flush=True)
    return res


# ------------------------------------------------------------------------------------------
def run_order_effects(graph: Dict[str, Dict[str, float]], sources: Set[str], ctx: Dict,
                      tag: str) -> Dict:
    """A5 -- nearest-frontier ordering. O1 frozen core one pass | O2 iterative nearest-frontier,
    AoA earliest-first | O3 identical iteration, randomised order. Scored on the SAME words, so the
    only variable is the ORDER in which codes become available as bridge sources."""
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, held_out, counts = ctx["idx"], ctx["held_out"], ctx["counts"]
    partners, aoa = ctx["partners"], ctx["aoa"]
    br = CELL.Bridger(raw, held_out, partners)
    d1 = sorted(w for w in held_out if br.neighbours(w, graph, sources, False))
    frontier = set(sources) | set(d1)
    rounds = [len(d1)]
    admitted = list(d1)
    for _ in range(6):
        new = sorted(w for w in held_out if w not in frontier and any(
            n in frontier and br.eligible(w, n, frontier, False) for n in (graph.get(w) or {})))
        if not new:
            break
        rounds.append(len(new))
        frontier |= set(new)
        admitted.extend(new)

    def bridge_ordered(order: Sequence[str]) -> Dict[str, np.ndarray]:
        avail = set(sources)
        codes: Dict[str, np.ndarray] = {}
        live = dict(br.hidden)
        b2 = CELL.Bridger(raw, held_out, partners)
        b2.hidden = live
        for w in order:
            nb = [(n, wt) for n, wt in (graph.get(w) or {}).items()
                  if n in avail and n in live and n != w and n not in partners.get(w, ())]
            if not nb:
                continue
            codes[w] = combine(b2, sorted(nb), "B1_BRIDGE_MEAN")
            live[w] = codes[w]
            avail.add(w)
        return codes

    o1 = {w: combine(br, br.neighbours(w, graph, sources, False), "B1_BRIDGE_MEAN") for w in d1}
    o2 = bridge_ordered(sorted(d1, key=lambda w: (aoa.get(w, 99.0), w)))
    o3s = {}
    for s in NULL_SEEDS:
        rng = np.random.default_rng(s ^ 0x1234)
        perm = list(d1)
        rng.shuffle(perm)
        o3s[s] = bridge_ordered(perm)
    common = sorted(set(o1) & set(o2) & set.intersection(*[set(v) for v in o3s.values()]))
    S = set(common)
    strat = [p for p in pairs if (p[0] in S) != (p[1] in S)]
    out = {"graph": tag, "d1_count": len(d1), "admissions_per_round": rounds,
           "closure_size": len(admitted), "n_common_words": len(common), "n_stratum": len(strat),
           "note": ("O1 and O2 differ ONLY where a d1 word can bridge from an EARLIER-admitted d1 "
                    "word; if the graph has no such edge the arms are identical BY CONSTRUCTION")}
    if len(strat) < 10:
        out["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        return out
    ia = np.array([idx[p[0]] for p in strat]); ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)
    floors = build_floors(vocab, ia, ib, gold, counts)
    tables = {"O1_ONESHOT_D1": {w: o1[w] for w in common},
              "O2_ITER_NEAREST": {w: o2[w] for w in common}}
    for s, t in o3s.items():
        tables[f"O3_ITER_ARBITRARY|s{s}"] = {w: t[w] for w in common}
    rows, cs = {}, {}
    for a, tb in sorted(tables.items()):
        X = CELL.code_matrix(vocab, raw, tb)
        r = score_arm(a, X, ia, ib, gold, floors, seed=int(abs(hash(tag + a)) % 100000) + 3,
                      light=a.startswith("O3_"))
        cs[a] = r.pop("_cos")
        r["IDENTITY"] = CELL.identity_axis(tb)
        rows[a] = r
    o3k = [k for k in rows if k.startswith("O3_")]
    best3 = max(o3k, key=lambda k: rows[k]["rho"]["point"])
    for a in ("O2_ITER_NEAREST", "O1_ONESHOT_D1"):
        dd = FT.boot_rho_diff(cs[a], cs[best3], gold, n_boot=N_BOOT, seed=BOOT_SEED)
        rows[a]["vs_O3_max_draw"] = {"vs": best3, "margin": dd, "band": FT.band(dd["ci95"])}
    d21 = FT.boot_rho_diff(cs["O2_ITER_NEAREST"], cs["O1_ONESHOT_D1"], gold,
                           n_boot=N_BOOT, seed=BOOT_SEED)
    out["O2_vs_O1"] = {"margin": d21, "band": FT.band(d21["ci95"])}
    out["O1_equals_O2_bitwise"] = bool(all(
        np.allclose(tables["O1_ONESHOT_D1"][w], tables["O2_ITER_NEAREST"][w]) for w in common))
    out["arms"] = rows
    out["floors"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                     for k, v in floors.items()}
    return out


# ------------------------------------------------------------------------------------------
# self-tests -- run BEFORE anything else, every run
# ------------------------------------------------------------------------------------------
def selftest() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    from hdlab import grounded_similarity as GS

    tab = GS._table()
    assert len(tab) == 36810, f"norms table {len(tab)} != 36810"
    assert len(next(iter(tab.values()))) == 12, "norms are not 12-dim"
    ev["norms_table"] = {"n_words": len(tab), "n_dim": 12}

    # TRAP RE-VERIFIED BY RUNTIME, NEVER INHERITED: grounded_similarity() is SATURATED.
    pairs = CELL.load_simlex_pos()
    vals = [GS.grounded_similarity(a, b) for a, b, _, _ in pairs]
    c = collections.Counter(round(v, 6) for v in vals if v is not None)
    frac2 = sum(n for _, n in c.most_common(2)) / len(vals)
    assert frac2 > 0.70, f"expected grounded_similarity saturated; top-2 mass {frac2:.4f}"
    ev["TRAP_grounded_similarity_saturation"] = {
        "n_pairs": len(vals), "n_distinct": len(c), "top2": c.most_common(2),
        "fraction_on_two_values": round(frac2, 4),
        "consequence": "NEVER used as a scorer here; the scorer is raw 12-dim + plain cosine"}

    # G1: the scorer reproduces an INDEPENDENT per-pair recompute on the full 999
    vocab = sorted({w for p in pairs for w in p[:2]})
    raw = {w: np.asarray(tab[w], dtype=np.float64) for w in vocab}
    idx = {w: i for i, w in enumerate(vocab)}
    ia = np.array([idx[p[0]] for p in pairs]); ib = np.array([idx[p[1]] for p in pairs])
    gold = np.array([p[3] for p in pairs], dtype=np.float64)
    X = CELL.code_matrix(vocab, raw, {})
    rho_fast = INS._spearman(CELL.pair_cos(X, ia, ib), gold)
    ref = []
    for a, b, _, _ in pairs:
        va = np.asarray(tab[a], np.float64); vb = np.asarray(tab[b], np.float64)
        ref.append(float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb))))
    rho_ref = INS._spearman(np.array(ref), gold)
    assert abs(rho_fast - rho_ref) < 1e-6, f"scorer {rho_fast} != recompute {rho_ref}"
    ev["G1_norms_rho_simlex999"] = {"vectorised": round(float(rho_fast), 6),
                                    "independent_recompute": round(float(rho_ref), 6)}

    # G2 + the FIVE additive transformations really are five different functions
    br = CELL.Bridger({"a": np.ones(12), "b": np.full(12, 3.0), "c": np.full(12, 11.0),
                       "d": np.full(12, 2.0), "x": np.full(12, 99.0)}, {"x"}, {"x": {"a"}})
    assert "x" not in br.hidden, "held-out row survived into the hidden table"
    nb = br.neighbours("x", {"x": {"a": 1.0, "b": 1.0}}, {"a", "b"}, False)
    assert [n for n, _ in nb] == ["b"], f"SimLex-partner exclusion failed: {nb}"
    fx = [("b", 1.0), ("c", 3.0), ("d", 2.0), ("a", 0.5)]
    got = {f: combine(br, fx, f) for f in BRIDGE_ARMS}
    assert np.allclose(got["B1_BRIDGE_MEAN"], (3 + 11 + 2 + 1) / 4.0), got["B1_BRIDGE_MEAN"][0]
    assert np.allclose(got["B2_BRIDGE_PMI_WEIGHTED"],
                       (3 * 1 + 11 * 3 + 2 * 2 + 1 * 0.5) / 6.5), got["B2_BRIDGE_PMI_WEIGHTED"][0]
    assert np.allclose(got["B3_BRIDGE_UNIT_MEAN"], 1.0 / np.sqrt(12)), "unit-mean wrong"
    assert np.allclose(got["B4_BRIDGE_MEDIAN"], 2.5), got["B4_BRIDGE_MEDIAN"][0]
    assert np.allclose(got["B5_BRIDGE_TOP3_PMI"], (11 + 2 + 3) / 3.0), got["B5_BRIDGE_TOP3_PMI"][0]
    sigs = {tuple(np.round(v, 9)) for v in got.values()}
    assert len(sigs) == 5, f"the five additive transformations collapse to {len(sigs)}"
    ev["five_additive_transformations"] = {
        "checked": {f: round(float(got[f][0]), 6) for f in BRIDGE_ARMS},
        "n_distinct_on_fixture": len(sigs),
        "STATUS": "ALL FIVE ARE OURS -- INVENTION UNDER TEST. Additivity is PINNED (Baron & "
                  "Osherson 2011); the transformation is NOT."}

    # the morphology blocker (the sibling's own, reused)
    for a, b in (("biology", "biological"), ("reproduction", "production"),
                 ("photosynthesis", "synthesis"), ("cell", "cells")):
        assert CELL.morph_related(a, b), f"morphology blocker missed {a}/{b}"
    for a, b in (("dog", "cat"), ("tissue", "organ"), ("heart", "pump")):
        assert not CELL.morph_related(a, b), f"morphology blocker over-fired on {a}/{b}"

    # the orthographic floor is a function of SPELLING ONLY and is not degenerate
    ws = [f"word{i}" for i in range(64)]
    O1 = INS.enc_orthographic(ws, 64, 7)
    assert np.allclose(O1, INS.enc_orthographic(ws, 64, 999)), "ortho floor depends on the seed"
    assert len({tuple(np.round(r, 6)) for r in INS._l2n(O1)}) == 64, "ortho floor degenerate"

    # the bootstrap can fail and can fire
    g = np.random.default_rng(1)
    gg = g.random(200)
    good = gg + 0.05 * g.standard_normal(200)
    noise = g.standard_normal(200)
    assert FT.band(FT.boot_rho_diff(good, good.copy(), gg, n_boot=400)["ci95"]) == "NOT_SEPARATED"
    assert FT.band(FT.boot_rho_diff(good, noise, gg, n_boot=400)["ci95"]) == "ABOVE"

    # the calibrated scramble floor sits ABOVE its own null centre
    sc = scramble_floor(X, ia[:200], ib[:200], gold[:200], 7)
    assert sc["p95"] > sc["row_null_mean"], "calibrated scramble floor below its null centre"
    ev["scramble_floor_selftest"] = {k: round(v, 4) for k, v in sc.items()
                                     if isinstance(v, float)}

    # the floor NAMES are the ones tools/c3_gate.py can classify (deviation H)
    from tools.c3_gate import classify_arm_role
    roles = {FLOOR_ORTHO: "orthographic", FLOOR_FREQ: "frequency", FLOOR_SCRAM: "scramble",
             "K2_ORACLE_BRIDGE": "known_answer", "N1_NULL_ARM_MATCHED_REWIRE": "null_control",
             "N2_NULL_ARM_RANDOM_TARGET": "null_control"}
    for k, want in roles.items():
        got_role = classify_arm_role(k)
        assert got_role == want, f"c3_gate reads {k} as {got_role}, not {want}"
    for k in BRIDGE_ARMS + ("K1_OWN_NORMS",):
        assert classify_arm_role(k) is None, f"treatment arm {k} misreads as {classify_arm_role(k)}"
    ev["standing_bar_arm_roles"] = {k: classify_arm_role(k) for k in
                                    list(roles) + list(BRIDGE_ARMS) + ["K1_OWN_NORMS"]}

    print("[selftest] ALL PASS", flush=True)
    return ev


# ------------------------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    ev = selftest()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK")
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_PERM={N_PERM} out={out_dir}", flush=True)

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    pairs = CELL.load_simlex_pos()
    vocab = sorted({w for p in pairs for w in p[:2]})
    for w in vocab:
        if w not in tab:
            raise SystemExit(f"[fatal] SimLex word {w} has no norms")
    raw = {w: np.asarray(v, dtype=np.float64) for w, v in tab.items()}
    idx = {w: i for i, w in enumerate(vocab)}
    partners: Dict[str, Set[str]] = collections.defaultdict(set)
    for a, b, _, _ in pairs:
        partners[a].add(b)
        partners[b].add(a)

    aoa = CELL.load_aoa()
    core = {w for w, v in aoa.items() if v <= AOA_CORE_MAX and w in tab}
    held_out = {w for w in vocab if w not in core}

    def_graph, pat_census, def_rows = CELL.load_def_graph()
    cskg_all, cskg_nolex = CELL.load_cskg_graphs(set(vocab))
    counts = CELL.corpus_counts()

    edges = THEM.build_or_load()
    them_graph, them_info = build_thematic_graph(edges)
    cooc = edges["cooccurrence"]
    enriched = merge(def_graph, them_graph)
    print(f"[assets] core={len(core)} held_out={len(held_out)} def_nodes={len(def_graph)} "
          f"def_rows={def_rows} them_nodes={len(them_graph)} enriched_nodes={len(enriched)}",
          flush=True)

    # G4: the thematic channel must actually exist and must supply verbs
    from hdlab import definitional_extraction as DE
    them_verbs = sorted({b for a, nb in them_graph.items() for b in nb
                         if DE.is_verbal_lemma(b) and not DE.is_nominal_lemma(b)})
    g4 = {"thematic_graph_nonempty": bool(them_graph),
          "n_thematic_nodes": len(them_graph),
          "n_verb_lemmas_in_thematic_graph": len(them_verbs),
          "example_verb_lemmas": them_verbs[:12],
          "passed": bool(them_graph and len(them_graph) > 100)}
    if not g4["passed"]:
        raise SystemExit("[fatal] G4: the thematic channel is empty -- nothing to test")

    ctx = {"vocab": vocab, "raw": raw, "pairs": pairs, "idx": idx, "held_out": held_out,
           "core": core, "partners": partners, "counts": counts, "aoa": aoa, "cooc": cooc}

    c6_graph, c6_before, c6_after = partner_context_filter(enriched, held_out, partners)
    def_bridgeable = {w for w in held_out
                      if CELL.Bridger(raw, held_out, partners).neighbours(w, def_graph, core, False)}
    them_bridgeable = {w for w in held_out
                       if CELL.Bridger(raw, held_out, partners).neighbours(w, them_graph, core, False)}
    common_words = def_bridgeable & them_bridgeable

    CONFIGS = [
        # (name, graph, sources, morph_block, hub_censor, kwargs)
        ("PRIMARY_DEF_THEMATIC_CORE", enriched, core, False, False, {"do_pos": True}),
        ("PRIMARY_MORPHBLOCK", enriched, core, True, False, {"do_pos": True}),
        ("PRIMARY_C6a_PARTNER_CONTEXT_EXCLUDED", c6_graph, core, False, False, {"do_pos": True}),
        ("PRIMARY_C6b_NEVER_COOCCUR_SUBSTRATUM", enriched, core, False, False,
         {"pair_filter": "NEVER_COOCCUR"}),
        ("PRIMARY_HUBCENSOR", enriched, core, False, True, {}),
        ("THEMATIC_ONLY_CORE", them_graph, core, False, False, {}),
        ("DEF_ONLY_CORE_reproduces_sibling", def_graph, core, False, False, {}),
        ("DECOMP_COMMON_STRATUM_TAXONOMIC_VS_THEMATIC", enriched, core, False, False,
         {"restrict_words": common_words,
          "arm_graphs": {"BD_BRIDGE_TAXONOMIC_ONLY": def_graph,
                         "BT_BRIDGE_THEMATIC_ONLY": them_graph}}),
        ("CEILING_CSKG_NOLEXREL_CORE_EXTERNAL_REFERENCE", cskg_nolex, core, False, False,
         {"do_pos": True}),
        ("ORACLE_ALL_HELDOUT", None, core, False, False, {"do_pos": True}),
    ]

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    results: Dict[str, Dict] = {}
    for name, g, src, mb, hc, kw in CONFIGS:
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, name)
        if key in done and key in units:
            results[name] = units[key]
            print(f"[cfg] {name} RESUMED", flush=True)
            continue
        r = run_config(name, g, set(src), mb, hc, ctx, **kw)
        record_unit(str(out_dir), key, r)
        results[name] = r

    order = {}
    for tag, g in (("ENRICHED_DEF_THEMATIC_CORE", enriched),):
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "ORDER_" + tag)
        if key in done and key in units:
            order[tag] = units[key]
            continue
        o = run_order_effects(g, set(core), ctx, tag)
        record_unit(str(out_dir), key, o)
        order[tag] = o
        print(f"[order] {tag} rounds={o.get('admissions_per_round')} n={o.get('n_stratum')} "
              f"O1==O2 {o.get('O1_equals_O2_bitwise')}", flush=True)

    # ---------------- verdict ----------------
    P = results["PRIMARY_DEF_THEMATIC_CORE"]
    parm = P.get("arms", {}).get(PRIMARY_ARM, {})
    pmb = results["PRIMARY_MORPHBLOCK"].get("arms", {}).get(PRIMARY_ARM, {})
    pc6 = results["PRIMARY_C6a_PARTNER_CONTEXT_EXCLUDED"].get("arms", {}).get(PRIMARY_ARM, {})
    g0 = bool(P.get("G0_power_gate", {}).get("K1_clears_floor"))
    g3 = bool(P.get("G3_passed"))
    vs_n1 = parm.get("vs_nulls", {}).get("N1_NULL_ARM_MATCHED_REWIRE", {}).get("band")
    if not g3:
        verdict = "INVALID_VALIDITY_GATE_FAILED"
    elif not g0:
        verdict = "POWER_INSUFFICIENT_ON_THE_PRIMARY_STRATUM"
    elif (parm.get("clears_floor") and pmb.get("clears_floor") and pc6.get("clears_floor")
          and vs_n1 == "ABOVE" and not parm.get("middle_band")):
        verdict = "BRIDGED_CODES_CARRY_MEANING_CLEARS_THE_FLOOR_ON_OUR_OWN_ENRICHED_GRAPH"
    elif parm.get("clears_floor"):
        verdict = "MIDDLE_BAND_CLEARS_UNBLOCKED_ONLY"
    else:
        verdict = "BRIDGED_CODES_DO_NOT_CLEAR_THE_FLOOR_ON_OUR_GRAPH"

    ceil = results["CEILING_CSKG_NOLEXREL_CORE_EXTERNAL_REFERENCE"].get("arms", {}).get(
        PRIMARY_ARM, {})
    orc = results["ORACLE_ALL_HELDOUT"].get("arms", {}).get("K2_ORACLE_BRIDGE", {})
    dissociation = {
        "our_enriched_graph_" + PRIMARY_ARM: parm.get("verdict_for_this_arm"),
        "ceiling_cskg_nolexrel_EXTERNAL": ceil.get("verdict_for_this_arm"),
        "oracle_neighbour_choice": orc.get("verdict_for_this_arm"), "reading": None}
    if orc.get("clears_floor") and not parm.get("clears_floor"):
        dissociation["reading"] = (
            "OUR RELATIONS ARE STILL THE LIMITER, NOT THE BRIDGING IDEA. The next fidelity step is "
            "EDGE TYPING -- role-structured thematic relations via extract_predicates_v62, an organ "
            "we own and have never run at scale -- then the TARGET SPACE. NOT a different operator "
            "and NOT a conclusion about bridging.")
    elif not orc.get("clears_floor") and not parm.get("clears_floor"):
        dissociation["reading"] = (
            "additive single-hop bridging does not carry meaning in the 12-dim CONCRETE-SPOKE space "
            "even with a PERFECT neighbour. Next step is the TARGET SPACE (add the Warriner "
            "emotion/interoception spoke) or the operator, NOT the graph.")
    elif parm.get("clears_floor"):
        dissociation["reading"] = (
            "bridged codes clear the floor on our OWN enriched graph; see the PASS band and the "
            "morphology / C6a survival flags before quoting it.")

    # ---- the falsifier, read out explicitly
    def _pos_block(cfg: str, arm: str) -> Dict:
        a = results.get(cfg, {}).get("arms", {}).get(arm, {})
        return a.get("POS_STRATA_WITH_OWN_FLOORS", a.get("POS_RHO_ONLY", {}))

    fals = {"WHAT_IT_TESTS": (
        "Hills et al. 2009: the lure-of-the-associates growth mechanism is NOUN-SPECIFIC. If "
        "bridging works EQUALLY WELL on verbs as on nouns, we are NOT seeing that mechanism, and "
        "that is a MECHANISM FAILURE even if the headline margin is positive."),
        "primary_" + PRIMARY_ARM: _pos_block("PRIMARY_DEF_THEMATIC_CORE", PRIMARY_ARM),
        "oracle_K2_uses_NO_graph": _pos_block("ORACLE_ALL_HELDOUT", "K2_ORACLE_BRIDGE"),
        "known_answer_K1": _pos_block("PRIMARY_DEF_THEMATIC_CORE", "K1_OWN_NORMS"),
        "HOW_TO_READ": (
            "If the ORACLE arm (which uses NO relation graph at all) shows the SAME POS profile as "
            "a graph arm, the asymmetry belongs to the 12-dim CONCRETE-SPOKE TARGET SPACE and NOT "
            "to the ordering mechanism -- and NO ordering claim may be made in either direction.")}
    pn = _pos_block("PRIMARY_DEF_THEMATIC_CORE", PRIMARY_ARM)
    if isinstance(pn, dict) and "N" in pn and "V" in pn:
        nn, vv = pn["N"], pn["V"]
        if "rho" in nn and "rho" in vv:
            fals["noun_rho"] = nn["rho"]["point"]
            fals["verb_rho"] = vv["rho"]["point"]
            fals["noun_minus_verb_rho_point"] = round(nn["rho"]["point"] - vv["rho"]["point"], 4)
            fals["noun_ci_vs_verb_ci_overlap"] = bool(
                nn["rho"]["ci95"][0] <= vv["rho"]["ci95"][1]
                and vv["rho"]["ci95"][0] <= nn["rho"]["ci95"][1])
        else:
            fals["status"] = "NOT_CONSTRUCTIBLE on one or both POS sub-strata"

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "prereg": PREREG, "verdict": verdict,
        "verdict_msg": (
            "Does a word grounded ONLY by bridging from an already-grounded core carry measurable "
            "meaning once the brain's SECOND relational hub (the temporo-parietal THEMATIC system) "
            "is supplied from our own corpus, against floors recomputed on the identical stratum? "
            "-> " + verdict),
        "summary": verdict,
        "HOW_TO_READ_A_NULL": (
            "The brain does this, so the capability is DEMONSTRATED. A null here is a fact about "
            "OUR IMPLEMENTATION, never about the capability. See prereg section 8 and "
            "named_divergences_from_the_biology below. Deflate claims, never ambition."),
        "PRE_REGISTERED_HONESTY_LINE": (
            "The thematic channel is DISTRIBUTIONALLY DERIVED from OUR OWN corpus. That is "
            "brain-real (language transports relational structure into a modality the learner "
            "cannot experience -- Kim, Elli & Bedny, congenitally blind colour structure) and it is "
            "OURS, not a pretrained table. But this arm tests 'can our own event-co-participation "
            "relations TRANSPORT GROUNDING', which is a HYBRID distributional + grounded claim and "
            "must never be reported as pure relational inheritance."),
        "config": {"AOA_CORE_MAX": AOA_CORE_MAX, "THEMATIC_MIN_COUNT": THEMATIC_MIN_COUNT,
                   "THEMATIC_MIN_PMI": THEMATIC_MIN_PMI, "THEMATIC_TOPK": THEMATIC_TOPK,
                   "T_MARGIN_MIN": T_MARGIN_MIN, "N_BOOT": N_BOOT, "N_PERM": N_PERM,
                   "NULL_SEEDS": list(NULL_SEEDS), "HUB_INDEGREE_MAX": HUB_INDEGREE_MAX,
                   "POS_MIN_N": POS_MIN_N, "COOC_MIN_COUNT": COOC_MIN_COUNT,
                   "ORTHO_DIMS": list(ORTHO_DIMS), "BOOT_SEED": BOOT_SEED,
                   "MORPH_PREFIX_MIN": CELL.MORPH_PREFIX_MIN,
                   "MORPH_TRIGRAM_COS_MAX": CELL.MORPH_TRIGRAM_COS_MAX},
        "assets": {"simlex": "data/encoder_eval_benchmarks/simlex999.txt",
                   "norms": "hdlab/grounded_similarity.py (36,810 words x 12 dims)",
                   "aoa": "data/grounding_testbed/AoA_51715_words.csv (AoA_Kup_lem)",
                   "definitional_graph_TAXONOMIC": list(CELL.FACT_FILES),
                   "thematic_graph_THEMATIC": "data/thematic_relations_v1/thematic_edges_v1.pkl "
                                              "(experiments/thematic_relation_extractor_v1.py)",
                   "cskg_cache": "data/_cache_cskg_simlex_canonical_v1.pkl (CEILING REFERENCE ONLY)",
                   "corpus_for_frequency_and_for_thematic_edges":
                       str(INS.CORPUS.relative_to(REPO)).replace("\\", "/"),
                   "corpus_bytes": INS.CORPUS_BYTES,
                   "NOTE": "the thematic edges and the FREQUENCY FLOOR are computed on the "
                           "IDENTICAL corpus and the IDENTICAL byte budget, deliberately, so the "
                           "frequency-matched null is drawn from the same distribution the edges "
                           "came from"},
        "population": {"n_simlex_pairs": len(pairs), "n_distinct_words": len(vocab),
                       "n_core_AoA_le_6": len(core), "n_held_out_simlex": len(held_out),
                       "definitional_graph_nodes": len(def_graph),
                       "definitional_graph_rows": def_rows,
                       "relation_pattern_census_TAXONOMIC_ONLY": pat_census,
                       "thematic_graph_nodes": len(them_graph),
                       "enriched_graph_nodes": len(enriched),
                       "n_def_bridgeable": len(def_bridgeable),
                       "n_thematic_bridgeable": len(them_bridgeable),
                       "n_common_bridgeable": len(common_words)},
        "thematic_extraction": {**edges["report"], **them_info},
        "G4_thematic_channel_exists": g4,
        "C6a_partner_context_exclusion": {
            "edges_before": c6_before, "edges_after": c6_after,
            "edges_deleted": c6_before - c6_after,
            "why": ("the enrichment INTRODUCES this confound: an event edge comes from corpus "
                    "co-occurrence, so a held-out word and its SimLex partner can bridge from the "
                    "SAME neighbours. Measured shared-neighbour rate 0.0234 vs 0.0009 at random, "
                    "+0.0225 [+0.0147,+0.0310] ABOVE. Partner exclusion does NOT close it; it is "
                    "second-order through shared neighbours.")},
        "selftest_evidence": ev,
        "brain_fidelity_block": {
            "a_structures": {
                "taxonomic channel (COPULA/APPOSITIVE/CALLED/GLOSSARY_COLON/REFERS_TO)":
                    "anterior temporal lobe, entity features -- PINNED as a structure",
                "thematic channel (event co-participation) ADDED BY THIS CELL":
                    "temporo-parietal cortex: posterior middle temporal gyrus + angular gyrus, "
                    "event/action/location knowledge -- STRUCTURE PINNED (Schwartz 2011 PNAS "
                    "lesion double dissociation; Mirman 2017 dual-hub review); EXTRACTION RULE OURS",
                "the additive bridge operator":
                    "LATL conceptual combination -- additivity PINNED (Baron & Osherson 2011), the "
                    "TRANSFORMATION UNPINNED, which is why five are tested and all five are OURS",
                "nearest-frontier ordering":
                    "mPFC schema congruency x MTL (Tse 2007); noun-specific growth effect "
                    "(Hills 2009) -- PINNED as a prediction WITH the falsifier",
                "the developmental CORE cut (AoA <= 6.0)":
                    "early sensorimotor spokes; slot-filler evidence (Nelson/Lucariello) says the "
                    "pre-7 child organises THEMATICALLY, a second independent reason a thematic "
                    "channel belongs in a CORE-sourced bridge"},
            "b_organ_reuse": (
                "Enumerated from disk by RUNTIME (imported and called), then reconciled read-only "
                "to data/capability_registry.jsonl, never registry-first. REUSED, not "
                "reimplemented: the sibling cell (Bridger, every eligibility rule, morph_related, "
                "code_matrix, identity_axis, the stratum definition), the Phase-1 instrument "
                "(_spearman, _l2n, enc_orthographic, recoverability), the Phase-1 verdict "
                "machinery (boot_rho, boot_rho_diff, band, T_MARGIN_MIN), "
                "hdlab.definitional_extraction.clause_main_verb (the event detector), "
                "hdlab.reading_grounding_loop.normalize_lemma (the SAME lemmatiser the "
                "definitional graph uses). The one genuinely new component is the EDGE "
                "DEFINITION -- the hub the brain has and we did not. This cell WRITES NOTHING to "
                "the capability registry; WIRE-or-SHELVE is a separate act at land time."),
            "c_pinned_vs_ours": (
                "PINNED: the existence and separateness of the thematic system and its neural "
                "substrate; its action/location feature basis; its developmental priority; the "
                "taxonomic constraint on label extension (Markman & Hutchinson 1984); additivity. "
                "OURS -- INVENTION UNDER TEST: the edge rule, the count/PMI gates, the top-k cap, "
                "ALL FIVE additive transformations, the AoA cut, and the C6a exclusion rule."),
            "d_shelve_revival_criterion_BRAIN_FRAMED": (
                "If the bridge does not clear, the direction is NOT shelved and the NUMBER is not "
                "the reason to move. Revival is triggered by closing a named biological "
                "divergence, in this order: (1) our thematic edge is UNTYPED co-participation "
                "whereas the brain's thematic relations are ROLE-STRUCTURED (agent/patient/"
                "location/instrument) -- we own hdlab/thematic_role_labeler.py and "
                "extract_predicates_v62 (221 facts banked, CALLED BY NOBODY) and have never fed "
                "either into a bridging graph at scale; (2) the TARGET SPACE is a concrete-spoke "
                "12-dim code with no emotion/interoception dimensions (Warriner is on disk, "
                "unused); (3) there is no informative-encounter selector and ~90% of natural "
                "exposures are uninformative (Medina et al. 2011); (4) no consolidation -- a "
                "bridged code is treated as immediately durable (Dumay & Gaskell 2007).")},
        "named_divergences_from_the_biology": [
            "EDGE TYPING: our thematic edge is UNTYPED event co-participation; the brain's "
            "thematic relations are ROLE-STRUCTURED. This is the FIRST revival move and the organ "
            "already exists (extract_predicates_v62, 221 facts, no callers).",
            "TARGET SPACE: the 12-dim code is a CONCRETE-SPOKE code with no emotion / "
            "interoception / social spokes. Ratings_Warriner_et_al.csv is on disk and unused.",
            "NO INFORMATIVE-ENCOUNTER SELECTOR: every sentence is treated as equally informative; "
            "~90% of natural exposures are uninformative (Medina et al. 2011).",
            "NO CONSOLIDATION: a bridged code is treated as immediately durable. Lexical "
            "integration requires an interval containing sleep (Dumay & Gaskell 2007). Phase 5.",
            "PRECISION UNMEASURED: no thematic edge has been hand-scored. The verb-detection rate "
            "is a YIELD number, not an accuracy number.",
        ],
        "HILLS_2009_NOUN_VERB_FALSIFIER": fals,
        "dissociation": dissociation,
        "results": results,
        "order_effects": order,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)

    print("\n===== RESULTS")
    for cfg in [c[0] for c in CONFIGS]:
        r = results.get(cfg)
        if not r or "arms" not in r:
            continue
        print(f"\n--- {cfg}  n={r['n_stratum']}  POS={r['pos_counts']}  "
              f"deg={r.get('bridge_degree', {}).get('median')}  "
              f"G0={'PASS' if r['G0_power_gate']['K1_clears_floor'] else 'FAIL'}")
        for a, v in sorted(r["arms"].items()):
            if "rho" not in v or "margin_over_strongest_floor" not in v:
                continue
            m = v["margin_over_strongest_floor"]
            print(f"  {a:<34} rho={v['rho']['point']:+.4f} "
                  f"[{v['rho']['ci95'][0]:+.4f},{v['rho']['ci95'][1]:+.4f}]  "
                  f"floor={v['strongest_floor']:<22}"
                  f"({v['floor_rho_by_arm'][v['strongest_floor']]:+.4f})  "
                  f"margin={m['point']:+.4f} [{m['ci95'][0]:+.4f},{m['ci95'][1]:+.4f}] "
                  f"{v['band']:<14} {v.get('verdict_for_this_arm', '')}")
    print("\nFALSIFIER:", json.dumps({k: v for k, v in fals.items()
                                      if k in ("noun_rho", "verb_rho",
                                               "noun_minus_verb_rho_point",
                                               "noun_ci_vs_verb_ci_overlap", "status")}, indent=1))
    print("\nVERDICT:", verdict)
    print("DISSOCIATION:", json.dumps(dissociation, indent=1))
    print(f"[done] {out_dir}/metrics.json ({metrics['elapsed_s']}s)", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:                                     # noqa: BLE001 -- printed, never hidden
        import traceback
        traceback.print_exc()
        sys.exit(2)
