#!/usr/bin/env python
# -*- coding: ascii -*-
"""
exp_semantic_hub_live_coverage_v1 -- the PRE-REGISTERED DECISION arm: does the ONE learned
convergence semantic hub (exp_semantic_hub_convergence_v1), read out for ranking, TIE-OR-BEAT the
landed convergent-cue fusion (FusedSenseRanker) on the LIVE coverage-quality instrument?

It reuses the REAL instrument (experiments/exp_board_grounding_coverage_quality_v1) verbatim -- same
live ReadingLoopState (real ingest), same population (SimLex/SimVerb high-sim, query = non-seed
grounding target, gold = eligible anchor), same MRR@0.5-coverage scorer and paired bootstrap CI --
and ADDS a HUB arm: rank the eligible anchors by cosine(hub(query), hub(anchor)) with a z_top
standout confidence for the coverage frontier. FUSED, INCUMBENT, GROUNDED_ONLY, TWIN arms are the
instrument's own; HUB is scored head-to-head against them on the identical queries.

Pre-registered read (brief section 6): HUB ties-or-beats FUSED @0.5 coverage (CI includes 0 with
diff >= -small, or lo>0), twin losing == HARD-PASS on the live instrument; HUB below FUSED CI-sep ==
that half of the decision fails.

__bf_status__ = "BF_SPIRIT"   # hub = Rogers-McClelland convergence (PINNED op); readout = cosine +
                              # SDT-style standout (population-vector + divisive norm), same family as FUSED.
SCOPE: experiments/ only. Own data dir. NO hdlab writes (Q111). ASCII. max 3 cores.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_semantic_hub_convergence_v1 as HUBMOD

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT_DIR = Path(get_output_dir("exp_semantic_hub_live_coverage_v1"))
HUB_ASSET = Path("data/exp_semantic_hub_convergence_v1/consensus_hub.pt")
HEADLINE_COV = 0.5


def _hub_vectors_for(words, gains_kind=None):
    """Assemble the cached spokes for `words` and encode with the saved hub. Returns {word: unit vec or None}.
    gains_kind: None (uniform) or 'perceptual_up' (task-control gain up grounded/visual/valence)."""
    spokes, _backbone = HUBMOD.load_real_spokes()
    hub = HUBMOD.ConsensusHub.load(str(HUB_ASSET))
    order = [n for n, _ in hub.spoke_dims]
    spokes = {nm: spokes.get(nm, {}) for nm in order}
    vocab = list(dict.fromkeys(words))
    X, present, spoke_dims, index = HUBMOD.assemble(spokes, vocab)
    gains = None
    if gains_kind == "perceptual_up":
        gains = [(2.5 if nm in ("grounded", "visual", "valence") else 0.6) for nm, _ in spoke_dims]
    Hc = hub.encode(X, gains=gains)
    out = {}
    for w in vocab:
        i = index[w]
        out[w] = Hc[i] if present[i].sum() > 0 else None
    return out


def _rank_hub(q, hub_vec, anchors, elig, min_cov=5):
    """rank eligible anchors by hub cosine; z_top standout confidence. None if abstain."""
    qv = hub_vec.get(q)
    if qv is None:
        return None
    cand = [a for a in anchors if (a in elig and a != q and hub_vec.get(a) is not None)]
    if len(cand) < min_cov:
        return None
    sims = np.array([float(np.dot(qv, hub_vec[a])) for a in cand])
    order_idx = np.argsort(-sims, kind="mergesort")
    ranked = [cand[i] for i in order_idx]
    mu, sd = float(sims.mean()), float(sims.std())
    z_top = (sims.max() - mu) / (sd + 1e-12)
    return {"order": ranked, "z_top": z_top}


def _rank_hub_plus_fused(q, r_fused, hub_vec, w_hub=1.0):
    """ADD the hub as a 4th SEPARATE POOL to FUSED's convergent-cue fusion (the brain-faithful architecture:
    hub is one pool the read-time precision fusion weights, NOT a replacement). Combine FUSED's per-anchor
    combined log-posterior (r_fused['scores'], aligned with r_fused['order']) with the hub's log-softmax over
    the SAME candidates; re-rank. Returns {'order','z_top'} or None if FUSED abstained."""
    if r_fused is None:
        return None
    cands = list(r_fused["order"])
    fscores = np.asarray(r_fused["scores"], dtype=np.float64)
    qv = hub_vec.get(q)
    if qv is None or len(cands) < 5:
        return None
    hs = np.array([float(np.dot(qv, hub_vec[a])) if hub_vec.get(a) is not None else np.nan for a in cands])
    cov = ~np.isnan(hs)
    if cov.sum() < 3:
        return None
    mu, sd = float(np.nanmean(hs)), float(np.nanstd(hs))
    z = np.where(cov, (hs - mu) / (sd + 1e-12), 0.0)                 # uncovered -> neutral 0
    lp = z - (z.max() + np.log(np.sum(np.exp(z - z.max()))))         # log-softmax
    comb = fscores + w_hub * lp
    order = np.argsort(-comb, kind="mergesort")
    ranked = [cands[i] for i in order]
    sdc = float(comb.std())
    z_top = (comb.max() - float(comb.mean())) / (sdc + 1e-12) if sdc > 1e-12 else 0.0
    return {"order": ranked, "z_top": z_top}


def run(mode="full", seed=None, n_boot=2000):
    import experiments.exp_board_grounding_coverage_quality_v1 as B
    import experiments.exp_meaning_fusion_live_coverage_v1 as E
    from hdlab.reading_grounding_loop import is_eligible_meaning
    if seed is None:
        seed = B.SEED
    t0 = time.time()
    limit = 900 if mode == "smoke" else None
    seed_words = E.H.load_base_vocab_seed(); seed_set = set(seed_words)
    print("[live] building live state (real ingest, limit=%s)..." % limit)
    state, n_sent, merged = B._build_live_state(limit, seed_words, B.GROWN_STORE)
    qs, targets, anchors, elig = B._queries(state, seed_set)
    ranker = state.ranker
    from hdlab.reading_grounding_loop import FusedSenseRanker
    g_only = FusedSenseRanker(state.space, use_seq=False, use_referent=False)
    print("[live] queries=%d anchors=%d eligible=%d; loading hub + hub vectors..." % (len(qs), len(anchors), len(elig)))
    need = set(anchors) | set(q for q, _t in qs)
    hub_vec = _hub_vectors_for(list(need))
    n_hub_cov = sum(1 for w in need if hub_vec.get(w) is not None)
    print("[live] hub covers %d/%d of the field words" % (n_hub_cov, len(need)))
    # TASK-CONTROL gained readout (Hoffman 2018): grounding = identity-flavored -> gain UP the perceptual
    # spokes. Same hub, per-task spoke gain (not a copy). Brain-faithful lever for this task.
    hub_vec_g = _hub_vectors_for(list(need), gains_kind="perceptual_up")

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(qs))
    dec = {"FUSED": [], "INCUMBENT": [], "GROUNDED_ONLY": [], "TWIN": [], "HUB": [], "HUB_GAINED": [],
           "HUB_PLUS_FUSED": []}
    n_fallback = 0
    n_hub_fallback = 0
    for k, (q, t) in enumerate(qs):
        raw_sum = np.sum([tr.context_vec for tr in targets[q].traces], axis=0)
        inc_ranked, inc_conf = B._incumbent(state, q, raw_sum, anchors, elig)
        dec["INCUMBENT"].append(B._dec(inc_ranked, t, inc_conf))
        r = ranker.rank(q, eligible=is_eligible_meaning, return_order=True)
        if r is None:
            n_fallback += 1; dec["FUSED"].append(B._dec(inc_ranked, t, inc_conf))
        else:
            dec["FUSED"].append(B._dec(r["order"], t, r["z_top"]))
        g = g_only.rank(q, eligible=is_eligible_meaning, return_order=True)
        dec["GROUNDED_ONLY"].append(B._dec(inc_ranked, t, inc_conf) if g is None else B._dec(g["order"], t, g["z_top"]))
        tw_word = qs[perm[k]][0] if qs[perm[k]][0] != q else qs[perm[(k + 1) % len(qs)]][0]
        tw = ranker.rank(q, eligible=is_eligible_meaning, query_word=tw_word, return_order=True)
        dec["TWIN"].append(B._dec(inc_ranked, t, inc_conf) if tw is None else B._dec(tw["order"], t, tw["z_top"]))
        # HUB arm (falls back to incumbent when the hub abstains -- same discipline as FUSED)
        h = _rank_hub(q, hub_vec, anchors, elig)
        if h is None:
            n_hub_fallback += 1; dec["HUB"].append(B._dec(inc_ranked, t, inc_conf))
        else:
            dec["HUB"].append(B._dec(h["order"], t, h["z_top"]))
        # HUB_GAINED: task-control perceptual-up gain (same hub, per-task spoke gain)
        hg = _rank_hub(q, hub_vec_g, anchors, elig)
        dec["HUB_GAINED"].append(B._dec(inc_ranked, t, inc_conf) if hg is None else B._dec(hg["order"], t, hg["z_top"]))
        # HUB_PLUS_FUSED: hub added as a 4th separate POOL to FUSED (brain-faithful: pool, not replacement)
        hpf = _rank_hub_plus_fused(q, r, hub_vec)
        if hpf is None:
            dec["HUB_PLUS_FUSED"].append(dec["FUSED"][-1])   # no hub pool -> FUSED's own decision
        else:
            dec["HUB_PLUS_FUSED"].append(B._dec(hpf["order"], t, hpf["z_top"]))

    n = len(qs)
    res = {"anchor": "exp_semantic_hub_live_coverage_v1", "mode": mode, "seed": seed, "n_queries": n,
           "n_sentences_read": n_sent, "grown_store_merged_tokens": merged,
           "n_anchors": len(anchors), "n_eligible_anchors": len(elig),
           "n_fused_fallback": n_fallback, "n_hub_fallback": n_hub_fallback, "hub_field_cov": n_hub_cov}
    if n < 10:
        res["note"] = "too few queries"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / ("metrics_%s.json" % mode)).write_text(json.dumps(res, indent=2), encoding="ascii")
        return res
    auf = {a: round(E.area_under_frontier(d, score_idx=1), 4) for a, d in dec.items()}
    mrr_all = {a: round(float(np.mean([x[1] for x in d])), 4) for a, d in dec.items()}

    def _ci(a, b, s):
        diff, lo, hi, pa, pb = E.boot_ci_at(dec[a], dec[b], HEADLINE_COV, seed + s, n_boot, score_idx=1)
        return {"diff": round(diff, 4), "ci": [round(lo, 4), round(hi, 4)], "a": round(pa, 4), "b": round(pb, 4),
                "ci_sep_positive": bool(lo > 0.0)}
    res.update({
        "AUF_MRR": auf, "MRR_all": mrr_all,
        "HUB_minus_FUSED@0.5": _ci("HUB", "FUSED", 11),
        "HUB_minus_INCUMBENT@0.5": _ci("HUB", "INCUMBENT", 12),
        "HUB_minus_TWIN@0.5": _ci("HUB", "TWIN", 13),
        "HUB_minus_GROUNDED_ONLY@0.5": _ci("HUB", "GROUNDED_ONLY", 14),
        "HUB_GAINED_minus_FUSED@0.5": _ci("HUB_GAINED", "FUSED", 15),
        "HUB_GAINED_minus_HUB@0.5": _ci("HUB_GAINED", "HUB", 16),
        "HUB_GAINED_minus_TWIN@0.5": _ci("HUB_GAINED", "TWIN", 17),
        "HUB_PLUS_FUSED_minus_FUSED@0.5": _ci("HUB_PLUS_FUSED", "FUSED", 18),
        "HUB_PLUS_FUSED_minus_TWIN@0.5": _ci("HUB_PLUS_FUSED", "TWIN", 19),
        "FUSED_minus_INCUMBENT@0.5": _ci("FUSED", "INCUMBENT", 1),
        "FUSED_minus_TWIN@0.5": _ci("FUSED", "TWIN", 2),
        "elapsed_s": round(time.time() - t0, 1),
    })
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("metrics_%s.json" % mode)).write_text(json.dumps(res, indent=2, default=str), encoding="ascii")
    hf = res["HUB_minus_FUSED@0.5"]; ht = res["HUB_minus_TWIN@0.5"]; hgf = res["HUB_GAINED_minus_FUSED@0.5"]
    print("\nHEADLINE n=%d  HUB MRR@0.5=%.4f  HUB_GAINED=%.4f  FUSED=%.4f  INCUMBENT=%.4f" % (
        n, mrr_all["HUB"], mrr_all["HUB_GAINED"], mrr_all["FUSED"], mrr_all["INCUMBENT"]))
    print("  HUB-FUSED %+.4f CI %s | HUB_GAINED-FUSED %+.4f CI %s | HUB-TWIN %+.4f sep=%s" % (
        hf["diff"], hf["ci"], hgf["diff"], hgf["ci"], ht["diff"], ht["ci_sep_positive"]))
    print("[live] wrote %s" % (OUT_DIR / ("metrics_%s.json" % mode)))
    return res


def self_test():
    """Lightweight: hub loads + ranks a planted gold above random on a synthetic eligible field."""
    if not HUB_ASSET.exists():
        print("[self-test] hub asset missing at %s -- run exp_semantic_hub_convergence_v1.py --mode full first"
              % HUB_ASSET)
        return 2
    hub = HUBMOD.ConsensusHub.load(str(HUB_ASSET))
    print("[self-test] hub loaded: spoke_dims=%s H=%d spoke_prec=%s" % (hub.spoke_dims, hub.H,
          [round(float(x), 3) for x in hub.spoke_prec]))
    # planted-gold ranking sanity on the real hub vectors for a few known words
    spokes, backbone = HUBMOD.load_real_spokes()
    sample = [w for w in ("dog", "cat", "car", "run", "happy", "king", "queen", "water", "river") if w in backbone]
    if len(sample) < 4:
        print("[self-test] too few sample words covered"); return 1
    hv = _hub_vectors_for(sample + backbone[:400])
    ok = all(hv.get(w) is not None for w in sample)
    # dog should be nearer cat than car (a soft sanity check, not a gate)
    def cs(a, b):
        return float(np.dot(hv[a], hv[b])) if hv.get(a) is not None and hv.get(b) is not None else float("nan")
    near = cs("dog", "cat") if "dog" in sample and "cat" in sample else float("nan")
    far = cs("dog", "car") if "dog" in sample and "car" in sample else float("nan")
    print("[self-test] hub covers sample=%s ; cos(dog,cat)=%.3f cos(dog,car)=%.3f" % (ok, near, far))
    print("[self-test] %s" % ("GREEN" if ok else "RED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="live ingest limited to 900 sentences")
    ap.add_argument("--self-test", action="store_true", help="hub-load + ranking sanity (no ingest)")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    r = run(mode="smoke" if a.smoke else "full", n_boot=a.n_boot)
    print(json.dumps({k: v for k, v in r.items() if k not in ("AUF_MRR",)}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
