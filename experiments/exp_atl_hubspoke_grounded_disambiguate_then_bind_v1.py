"""exp_atl_hubspoke_grounded_disambiguate_then_bind_v1 -- THE UPSTREAM brain-foundational component, built as a
MONOTONIC BRAIN-FIDELITY LADDER: does the sense-discriminative connection matrix W get MORE discriminative as the
ENCODING disambiguation becomes more brain-foundational?

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

THE WALL (proven by two parents + this problem's located negative): the readout is fine (precision-weighted biased
competition), the sense KEYS separate; what is missing at coverage is the SENSE-DISCRIMINATIVE W -- for each sense,
which context words signal IT over its dominant twin. An ORACLE W -> a_s 0.995 (parent break_the_contextual...);
the only bottleneck is building W without gold. Prior attempts failed for a DIAGNOSABLE reason:
  * parent consolidation-gate READBIND resolved each encounter's sense with DISTRIBUTION (topical) -> W reinforced
    the DOMINANT sense -> a_s ~= gloss 0.251 (topical failure).
  * the reading-derived learner grew W on the ambiguous FORM -> same topical failure.
  * a GOLD-resolved W is sense-discriminative (+0.059 on covered senses) but gold is not brain-foundational.

THE BRAIN-FOUNDATIONAL UPSTREAM FIX (this cell): resolve each encounter's sense at ENCODING with the GROUNDED
hub-and-spoke (the ATL non-distributional anchor -- Cell A grounded keys separate senses cos 0.22 where the
distributional gloss keys sit at 0.80), THEN Hebbian-bind context to the RESOLVED sense, THEN cross-situationally
consolidate. Grounding breaks the bootstrap circularity that trapped the distributional readbind. Every component
is the brain's actual computation: LIFG/pMTG controlled retrieval settles the sense (Jefferies 2013), ATL grounding
supplies the non-distributional resolution cue (Patterson-2007), CLS keeps-what-recurs (McClelland 1995), and the
readout is precision-weighted biased competition (Friston / this problem's Cell B).

THE LADDER (each rung makes ENCODING more brain-foundational; W built document-disjoint from even-doc SemCor
contexts, tested on odd-doc subordinate; readout combines the launch-pad diagnostic prior + the W signal):
  R0  launch-pad diagnostic only (no W)                                    -- the 0.313 floor
  R1  + DISTRIBUTIONAL-resolved W  (parent readbind; expected topical ~gloss)
  R2  + GROUNDED-resolved W        (the brain-foundational upstream fix -- hypothesis: climbs)
  R3  + precision-weighted readout over the grounded W
  REF + GOLD-resolved W            (perfect encoding disambiguation -- parent's learned-W ceiling reference)

Glass-box, frozen w2v, NO external LLM / transformer / training, NO gold used to build the R1/R2/R3 W (gold only in
the REF reference arm and as the eval scorer). Strict document-disjoint. Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
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
import math
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
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_grounded_disambiguate_then_bind_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _z(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    train_idx = list(np.where(doc % 2 == 0)[0])           # even docs -> build W (ALL senses, doc-disjoint)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])    # odd docs, subordinate -> eval (n=2676)
    if smoke:
        train_idx = train_idx[:2000]; test_idx = test_idx[:400]

    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    train_cand = set()
    for i in train_idx:
        train_cand.update(recs[i]["tn"])
    allsyn = sorted(cand | train_cand)

    # keys: launch-pad rich w2v atom (the 0.313 prior) + grounded hub (Cell A) for grounded resolution
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in allsyn}
    gr = A.Grounded(add_affect=True)
    sg_white = A.build_sense_grounded(allsyn, gr, whiten=True, own_lemma_w=0.0)
    print("[setup] train=%d test=%d cand=%d grounded_cov=%.3f (%.0fs)"
          % (len(train_idx), len(test_idx), len(cand), np.mean([sg_white[s] is not None for s in allsyn]),
             time.time() - t0), flush=True)

    # ---- ENCODING: resolve each training encounter's sense 3 ways, bind context to the RESOLVED sense ----
    def resolve_distributional(r):
        tn = r["tn"]
        rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if not rows:
            return None
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        return tn[int(np.argmax(diagnostic_context_scores(np.stack(rows), G)))]

    def resolve_grounded(r):
        tn = r["tn"]
        rows = [gr.vec(x, True) for x in r["ctx"]]
        rows = [v for v in rows if v is not None]
        keys = [sg_white.get(s) for s in tn]
        if not rows or all(k is None for k in keys):
            return resolve_distributional(r)     # fall back where grounding is silent (brain: use what cue exists)
        d = rows[0].shape[0]
        G = np.stack([k if k is not None else np.zeros(d) for k in keys])
        return tn[int(np.argmax(diagnostic_context_scores(np.stack(rows), G)))]

    def resolve_gold(r):
        return r["gold"]

    def build_W(resolver):
        cooc = defaultdict(Counter); sel = Counter(); uni = Counter(); N = 0
        for i in train_idx:
            r = recs[i]
            toks = [x for x in r["ctx"] if x in w2i]
            if not toks:
                continue
            s = resolver(r)
            if s is None:
                continue
            N += 1
            seen = set(toks)
            for w in seen:
                uni[w] += 1
            sel[s] += 1
            cooc[s].update(seen)
        return {"cooc": cooc, "sel": sel, "uni": uni, "N": N}

    def ppmi(store, s, w):
        c = store["cooc"].get(s, {}).get(w, 0)
        if c == 0:
            return 0.0
        ns = store["sel"].get(s, 0); nw = store["uni"].get(w, 0); N = max(1, store["N"])
        p = (c / N) / max(1e-9, (ns / N) * (nw / N))
        return max(0.0, math.log(p + 1e-12))

    def ppmi(store, s, w):
        c = store["cooc"].get(s, {}).get(w, 0)
        if c == 0:
            return 0.0
        ns = store["sel"].get(s, 0); nw = store["uni"].get(w, 0); N = max(1, store["N"])
        p = (c / N) / max(1e-9, (ns / N) * (nw / N))
        return max(0.0, math.log(p + 1e-12))

    W_dist = build_W(resolve_distributional)
    W_grnd = build_W(resolve_grounded)
    W_gold = build_W(resolve_gold)

    # PROPOSE-AND-VERIFY BOOTSTRAP (Trueswell 2013; Yu-Smith cross-situational): re-resolve each encounter with the
    # combined evidence launch-pad + grounding + the pass-0 grounded W0 (the sense-discriminative signal grounding
    # seeded), then REBUILD W. The brain's circularity-breaker -- grounding anchors the confident cases, whose W then
    # helps resolve the rest. Bind only CONFIDENT resolutions (top1-top2 margin) = the "verify" half.
    def resolve_with_W(r, W0, wlam=1.0, verify_margin=0.0):
        tn = r["tn"]; ctxw = [x for x in r["ctx"] if x in w2i]
        rows_d = [_unit(mat[w2i[x]]) for x in ctxw]
        if not rows_d:
            return None
        Gd = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        base = diagnostic_context_scores(np.stack(rows_d), Gd) if np.any(Gd) else np.zeros(len(tn))
        rows_g = [gr.vec(x, True) for x in ctxw]; rows_g = [v for v in rows_g if v is not None]
        keys = [sg_white.get(s) for s in tn]
        gsc = np.zeros(len(tn))
        if rows_g and not all(k is None for k in keys):
            d = rows_g[0].shape[0]; Gg = np.stack([k if k is not None else np.zeros(d) for k in keys])
            gsc = diagnostic_context_scores(np.stack(rows_g), Gg)
        wsc = np.array([sum(ppmi(W0, s, w) for w in ctxw) for s in tn])
        comb = _z(base) + _z(gsc) + (wlam * _z(wsc) if np.any(wsc) else 0.0)
        order = np.argsort(-comb)
        if verify_margin > 0 and len(order) > 1 and (comb[order[0]] - comb[order[1]]) < verify_margin:
            return None                     # VERIFY: skip low-confidence bindings (propose-and-verify)
        return tn[int(order[0])]

    W_boot = build_W(lambda r: resolve_with_W(r, W_grnd, wlam=1.0, verify_margin=0.5))
    print("[encode] W built: dist=%d grounded=%d gold=%d BOOTSTRAP=%d senses (%.0fs)"
          % (len(W_dist["cooc"]), len(W_grnd["cooc"]), len(W_gold["cooc"]), len(W_boot["cooc"]), time.time() - t0),
          flush=True)

    # ---- READOUT. Two signals per test item: (a) BASE = launch-pad diagnostic; (b) WSC = the sense-discriminative
    # W score, score_s = sum_c precision_wq[c] * ppmi(W, s, c) (parent 2's winning headroom readout). We isolate the
    # MECHANISM from the coverage drag by reporting, per W: coverage, the COVERED-SUBSET a_s ranked by WSC vs by BASE
    # on the SAME items, and the GATED overall (WSC where the item is W-covered, else BASE fallback -- no scale-mixing).
    def item_scores(r, store, gamma=1.0, topk=None, shuffle_map=None):
        tn = r["tn"]; rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        ctxw = [x for x in r["ctx"] if x in w2i]
        if not rows:
            return None
        C = np.stack(rows)
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        sim = C @ G.T
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        if topk is not None and topk < len(diag):
            thr = np.sort(diag)[-topk]; diag = np.where(diag >= thr, diag, 0.0)
        wq = diag ** gamma
        q = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))
        base = G @ q
        wsc = np.zeros(len(tn))
        if store is not None:
            wqn = wq if wq.sum() > 1e-9 else np.ones(len(ctxw))
            for si, s in enumerate(tn):
                skey = shuffle_map[s] if (shuffle_map is not None and s in shuffle_map) else s
                wsc[si] = sum(wqn[wi] * ppmi(store, skey, w) for wi, w in enumerate(ctxw))
        return tn, base, wsc, int(np.argmax([1 if x == r["gold"] else 0 for x in tn]))

    def eval_W(store, gamma=1.0, topk=None, shuffle_map=None):
        # ATT = GOLD-sense-attested subset (the parent's coverage definition: the rare/gold sense itself has a W
        # profile). This isolates "does W help where the subordinate sense is attested" from the Zipf drag.
        gated, cov_W, cov_base, uncov_base, cov_flag = [], [], [], [], []
        att_W, att_base, att_flag = [], [], []
        for i in test_idx:
            r = recs[i]
            sc = item_scores(r, store, gamma=gamma, topk=topk, shuffle_map=shuffle_map)
            if sc is None:
                continue
            tn, base, wsc, gi = sc
            covered = bool(store is not None and float(wsc.max()) > 0.0)
            hit_base = int(tn[int(np.argmax(base))] == r["gold"])
            hit_W = int(tn[int(np.argmax(wsc))] == r["gold"]) if covered else hit_base
            gated.append(hit_W if covered else hit_base)
            cov_flag.append(covered)
            if covered:
                cov_W.append(hit_W); cov_base.append(hit_base)
            else:
                uncov_base.append(hit_base)
            gkey = shuffle_map[r["gold"]] if (shuffle_map is not None and r["gold"] in shuffle_map) else r["gold"]
            attested = bool(store is not None and store["sel"].get(gkey, 0) > 0)
            att_flag.append(1.0 if attested else 0.0)
            if attested:
                att_W.append(hit_W if covered else hit_base); att_base.append(hit_base)
        return {"gated": np.asarray(gated, float), "cov_W": np.asarray(cov_W, float),
                "cov_base": np.asarray(cov_base, float), "cov_flag": np.asarray(cov_flag, float),
                "att_W": np.asarray(att_W, float), "att_base": np.asarray(att_base, float),
                "att_flag": np.asarray(att_flag, float)}

    def m(x):
        return round(float(x.mean()), 4) if len(x) else None

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed) if n else None

    E0 = eval_W(None)
    Ed = eval_W(W_dist, gamma=1.0)
    Eg = eval_W(W_grnd, gamma=1.0)
    Egp = eval_W(W_grnd, gamma=3.0, topk=5)
    Egold = eval_W(W_gold, gamma=3.0, topk=5)
    Eboot = eval_W(W_boot, gamma=3.0, topk=5)
    rng = np.random.default_rng(20260904)
    perm = list(cand); rng.shuffle(perm); shuf = dict(zip(sorted(cand), perm))
    Etw = eval_W(W_grnd, gamma=3.0, topk=5, shuffle_map=shuf)

    def mech(E, seed, subset="cov"):
        W, B = (E["cov_W"], E["cov_base"]) if subset == "cov" else (E["att_W"], E["att_base"])
        d = pair(W, B, seed)
        return {"n": len(W), "a_s_W": m(W), "a_s_base_same_items": m(B),
                "W_minus_base": round((m(W) or 0) - (m(B) or 0), 4) if len(W) else None,
                "sep": d["sep"] if d else None, "ci": d["ci"] if d else None}

    ladder = {"R0_launchpad_overall": m(E0["gated"]),
              "R1_distributional_W_gated": m(Ed["gated"]), "R2_grounded_W_gated": m(Eg["gated"]),
              "R3_grounded_W_precision_gated": m(Egp["gated"]), "R4_bootstrap_W_gated": m(Eboot["gated"]),
              "REF_gold_W_gated": m(Egold["gated"]), "TWIN_shuffled_grounded_W_gated": m(Etw["gated"])}
    # MECHANISM on the GOLD-SENSE-ATTESTED subset (parent 2's coverage definition): does W beat base where the rare
    # sense is actually attested? -- isolates the mechanism from the Zipf coverage drag.
    attested = {
        "attested_frac_grounded": round(float(Eg["att_flag"].mean()), 3),
        "attested_frac_gold": round(float(Egold["att_flag"].mean()), 3),
        "distributional_W": mech(Ed, 331, "att"), "grounded_W": mech(Eg, 332, "att"),
        "grounded_W_precision": mech(Egp, 333, "att"), "bootstrap_W": mech(Eboot, 336, "att"),
        "gold_W_reference": mech(Egold, 334, "att"), "shuffled_twin": mech(Etw, 335, "att"),
    }
    res = {
        "n_train": len(train_idx), "n_test": len(test_idx),
        "ladder_gated_overall": ladder,
        "MECHANISM_on_covered_subset": {"coverage_frac": round(float(Eg["cov_flag"].mean()), 3),
                                        "distributional_W": mech(Ed, 311), "grounded_W": mech(Eg, 312),
                                        "grounded_W_precision": mech(Egp, 313), "gold_W_reference": mech(Egold, 314),
                                        "shuffled_twin": mech(Etw, 315)},
        "MECHANISM_on_gold_attested_subset": attested,
        "R3_gated_vs_R0": pair(Egp["gated"], E0["gated"], 303),
        "crosses_0.35_overall": bool((m(Egp["gated"]) or 0) >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("GROUNDED DISAMBIG-THEN-BIND | GATED overall: R0=%.4f dist=%.4f grnd=%.4f grnd+prec=%.4f "
                       "gold=%.4f twin=%.4f | ATTESTED-subset(gold-sense seen) W-minus-base: dist=%s grnd=%s gold=%s "
                       "(att_frac=%.2f) | crosses0.35=%s"
                       % (ladder["R0_launchpad_overall"], ladder["R1_distributional_W_gated"],
                          ladder["R2_grounded_W_gated"], ladder["R3_grounded_W_precision_gated"],
                          ladder["REF_gold_W_gated"], ladder["TWIN_shuffled_grounded_W_gated"],
                          attested["distributional_W"]["W_minus_base"], attested["grounded_W"]["W_minus_base"],
                          attested["gold_W_reference"]["W_minus_base"], attested["attested_frac_gold"],
                          res["crosses_0.35_overall"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_grounded_disambiguate_then_bind_v1", "verdict": "MEASURED",
                   "result": res}, f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    import numpy as np
    # ppmi monotonicity sanity via a tiny store
    store = {"cooc": {"s1": {"river": 5, "the": 5}}, "sel": {"s1": 5}, "uni": {"river": 5, "the": 100}, "N": 100}

    def ppmi(store, s, w):
        c = store["cooc"].get(s, {}).get(w, 0)
        if c == 0:
            return 0.0
        ns = store["sel"].get(s, 0); nw = store["uni"].get(w, 0); N = max(1, store["N"])
        import math
        p = (c / N) / max(1e-9, (ns / N) * (nw / N)); return max(0.0, math.log(p + 1e-12))
    assert ppmi(store, "s1", "river") > ppmi(store, "s1", "the"), "ppmi ranks the discriminative word above the frequent one"
    print("SELFTEST PASS (ppmi ranks sense-discriminative 'river' above frequent 'the')", flush=True)
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
