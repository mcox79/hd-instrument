"""exp_atl_hubspoke_full_chain_signal_trace_v1 -- the FULL brain-faithful meaning chain, assembled as ONE ladder,
tracing WHERE signal is lost stage by stage. Each rung adds one brain-faithful component; we read a_s on the
subordinate population AND the full (sub+dom) population (the consumer no-regression guard).

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

THE CHAIN (each stage = one pinned brain operation):
  R0  STATIC INPUT           raw frozen-w2v target vector -> gloss key (no context)         [dominant-biased substrate]
  R1  READ CONTEXT           flat context-mean query -> gloss key                           [the reader reads]
  R2  HUB-AND-SPOKE KEYS     + WordNet relations + SyntagNet in the sense key (rich atom)    [ATL knowledge]
  R3  CONTROLLED RETRIEVAL   + precision-weighted biased competition (LIFG/pMTG, Friston)    [the readout lever]
  R4  CONSOLIDATED EXPERIENCE + disambiguate-then-bind associates, GLASS-BOX resolver        [the online learner]
  R5  RESOLUTION CEILING     + disambiguate-then-bind associates, GOLD resolver              [perfect encoding]
  R6  READER RE-REP (mu)     + the gestalt reader's per-token mu re-representation fused     [the existing encoder]
Twins: shuffled-W on R4/R5. Consolidation W is EVEN-doc (train) only -> strictly inductive (no test-doc leakage).

Glass-box, frozen w2v, NO external LLM/transformer/training at inference. Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/_sglite_cache/sglite_syntagnet.pkl
# KB_REFERENT: data/corpora/binder/binder2016_ratings.csv
# KB_REFERENT: data/grounding_testbed/Ratings_Warriner_et_al.csv
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import pickle
import argparse
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF
import experiments.exp_atl_hubspoke_grounded_separability_v1 as A

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_full_chain_signal_trace_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _z(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    train = list(np.where(doc % 2 == 0)[0])
    test_sub = list(np.where((doc % 2 == 1) & sub)[0])
    test_all = list(np.where(doc % 2 == 1)[0])
    if smoke:
        train, test_sub, test_all = train[:3000], test_sub[:400], test_all[:800]
    cand = set()
    for i in train + test_all:
        cand.update(recs[i]["tn"])
    cand = sorted(cand)

    gloss_key = {s: G1._sigvec(mat, w2i, G1._seed_words(s, w2i)) for s in cand}
    rich_key = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in cand}
    gr = A.Grounded(add_affect=True)
    sg_white = A.build_sense_grounded(cand, gr, whiten=True, own_lemma_w=0.0)
    print("[setup] keys built (%.0fs)" % (time.time() - t0), flush=True)

    # ---- consolidated experience: disambiguate-then-bind associates from EVEN (train) docs, resolver in {gold,grounded}
    def build_W(resolver):
        cooc = defaultdict(Counter)
        for i in train:
            r = recs[i]; toks = set(x for x in r["ctx"] if x in w2i)
            if not toks:
                continue
            s = resolver(r)
            if s is None:
                continue
            cooc[s].update(toks)
        return {s: [w for w, _ in c.most_common(12)] for s, c in cooc.items()}

    def res_gold(r):
        return r["gold"]

    def res_grounded(r):
        tn = r["tn"]; rows = [gr.vec(x, True) for x in r["ctx"]]; rows = [v for v in rows if v is not None]
        keys = [sg_white.get(s) for s in tn]
        if not rows or all(k is None for k in keys):
            # fall back to precision-diagnostic in w2v
            rw = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
            if not rw:
                return None
            G = np.stack([rich_key[s] if (rich_key[s] is not None and np.any(rich_key[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
            if not np.any(G):
                return None
            from hdlab.diagnostic_context_wsd import diagnostic_context_scores
            return tn[int(np.argmax(diagnostic_context_scores(np.stack(rw), G)))]
        d = rows[0].shape[0]
        Gg = np.stack([k if k is not None else np.zeros(d) for k in keys])
        from hdlab.diagnostic_context_wsd import diagnostic_context_scores
        return tn[int(np.argmax(diagnostic_context_scores(np.stack(rows), Gg)))]

    W_gold = build_W(res_gold)
    W_grnd = build_W(res_grounded)

    def enrich(base_key, W, shuffle_map=None):
        out = {}
        for s in cand:
            words = list(BF.rich_atom_words(s, w2i, 3))
            src = shuffle_map[s] if (shuffle_map and s in shuffle_map) else s
            words += [w for w in W.get(src, []) if w in w2i]
            out[s] = G1._sigvec(mat, w2i, words)
        return out
    rich_W_gold = enrich(rich_key, W_gold)
    rich_W_grnd = enrich(rich_key, W_grnd)
    rng = np.random.default_rng(7); perm = list(cand); rng.shuffle(perm); shuf = dict(zip(cand, perm))
    rich_W_grnd_tw = enrich(rich_key, W_grnd, shuffle_map=shuf)

    # ---- readout primitives ----
    from hdlab.diagnostic_context_wsd import diagnostic_context_scores

    def score(r, keys, mode, mu_fuse=False):
        tn = r["tn"]
        G = np.stack([keys[s] if (keys[s] is not None and np.any(keys[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        if mode == "static":
            q = _unit(mat[w2i[r["lemma"]]]) if r["lemma"] in w2i else None
            if q is None:
                return None
            sc = G @ q
        else:
            rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
            if not rows:
                return None
            C = np.stack(rows)
            if mode == "ctxmean":
                sc = G @ _unit(C.mean(0))
            elif mode == "precision":
                sc = diagnostic_context_scores(C, G)                 # biased competition
                sim = C @ G.T; d = np.clip(sim.max(1) - sim.mean(1), 0, None)
                thr = np.sort(d)[-5] if len(d) > 5 else d.min()
                wq = np.where(d >= thr, d, 0.0) ** 3.0
                q = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))
                sc = G @ q
        if mu_fuse:
            mu = np.asarray(r["mu"], float)
            if mu.shape[0] == G.shape[1]:
                sc = _z(sc) + _z(G @ _unit(mu))
        return int(tn[int(np.argmax(sc))] == r["gold"])

    def a_s(idxs, keys, mode, mu_fuse=False):
        ok = [v for i in idxs if (v := score(recs[i], keys, mode, mu_fuse)) is not None]
        return np.asarray(ok, float)

    rungs = [
        ("R0_static_gloss",        gloss_key,   "static",    False),
        ("R1_readctx_gloss",       gloss_key,   "ctxmean",   False),
        ("R2_hubspoke_keys",       rich_key,    "ctxmean",   False),
        ("R3_controlled_precision", rich_key,   "precision", False),
        ("R4_consolidated_glassbox", rich_W_grnd, "precision", False),
        ("R5_resolution_ceiling_gold", rich_W_gold, "precision", False),
        ("R6_plus_reader_mu",      rich_W_gold, "precision", True),
    ]
    lad = {}; prev = None; trace = []
    for name, keys, mode, mu in rungs:
        v = a_s(test_sub, keys, mode, mu)
        vall = a_s(test_all, keys, mode, mu)
        lad[name] = {"a_s_sub": round(float(v.mean()), 4), "a_s_all": round(float(vall.mean()), 4)}
        d = None if prev is None else round(lad[name]["a_s_sub"] - prev, 4)
        trace.append((name, lad[name]["a_s_sub"], d, lad[name]["a_s_all"]))
        prev = lad[name]["a_s_sub"]
        print("[rung] %-28s a_s_sub=%.4f (delta %s) a_s_all=%.4f (%.0fs)"
              % (name, lad[name]["a_s_sub"], ("%+.4f" % d) if d is not None else "  base", lad[name]["a_s_all"],
                 time.time() - t0), flush=True)
    # twin: R4 with shuffled consolidation W (must not beat R4)
    tw = a_s(test_sub, rich_W_grnd_tw, "precision", False)

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)
    r3 = a_s(test_sub, rich_key, "precision"); r4 = a_s(test_sub, rich_W_grnd, "precision")
    r5 = a_s(test_sub, rich_W_gold, "precision")
    res = {
        "n_test_sub": len(test_sub), "n_test_all": len(test_all),
        "ladder": lad,
        "signal_loss_trace": [{"rung": n, "a_s_sub": s, "delta": d, "a_s_all": al} for (n, s, d, al) in trace],
        "consolidation_glassbox_vs_controlled": pair(r4, r3, 921),      # does the online learner add (glass-box)?
        "consolidation_gold_vs_controlled": pair(r5, r3, 922),          # the resolution-quality ceiling gain
        "consolidation_glassbox_vs_twin": pair(r4, tw, 923),
        "twin_shuffledW": round(float(tw.mean()), 4),
        "crosses_0.35_glassbox": bool(lad["R4_consolidated_glassbox"]["a_s_sub"] >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    # where is signal lost? the largest positive delta = biggest gain; the stall = where deltas go ~0 for glass-box
    deltas = [(n, d) for (n, s, d, al) in trace if d is not None]
    res["biggest_gain_stage"] = max(deltas, key=lambda kv: kv[1]) if deltas else None
    res["glassbox_consolidation_gain"] = round(lad["R4_consolidated_glassbox"]["a_s_sub"] - lad["R3_controlled_precision"]["a_s_sub"], 4)
    res["gold_consolidation_gain"] = round(lad["R5_resolution_ceiling_gold"]["a_s_sub"] - lad["R3_controlled_precision"]["a_s_sub"], 4)
    res["headline"] = ("FULL CHAIN SIGNAL TRACE | " + " -> ".join("%s=%.3f" % (n.split("_")[0], s) for (n, s, d, al) in trace)
                       + " | biggest gain=%s | glassbox-consolidation gain=%+.4f (gold ceiling %+.4f) | twin=%.3f | crosses0.35=%s"
                       % (res["biggest_gain_stage"], res["glassbox_consolidation_gain"], res["gold_consolidation_gain"],
                          res["twin_shuffledW"], res["crosses_0.35_glassbox"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_full_chain_signal_trace_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (full-chain signal-trace imports)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
