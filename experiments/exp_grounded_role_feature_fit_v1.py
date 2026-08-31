"""exp_grounded_role_feature_fit_v1 -- TEST (and, as measured, REFUTE for our quick feature set) the
hypothesis that thematic fit generalizes to NOVEL arguments better with a FEATURE-based fit vector than a
distributional one. problem: grounded_role_assignment_via_verb_keyed_thematic_fit.

CORRECTION FIRST (honesty -- caught by this very cell): an earlier probe reported that distributional
(GloVe) fit predicts role at ~0.51 (chance) on OOV nouns, i.e. "distributional cannot generalise role".
That was a MEASUREMENT ARTIFACT: the logistic ran WITHOUT class_weight on 22%-agent data, so it predicted
the majority class -> artificial 0.5 balanced accuracy. With a BALANCED classifier, GloVe verb-conditioned
generalises role to OOV nouns at ~0.65 balanced (noun-only ~0.59), beating its info-free twin (~0.48). So
distributional DOES carry generalising role signal (largely animacy/semantic-type, which GloVe encodes).

The brain-research drill (research_feature_based_role_generalization_2026-08-30.md) predicts a FEATURE space
should win (McRae feature norms; ATL = feature integration; LREC-2020 bag-of-words fit thematic fit weakly).
This cell TESTS that with a small no-LLM FEATURE vector for any noun (WordNet supersense + IS-A concreteness
+ animacy) and a VERB-CONDITIONED prototype. MEASURED OUTCOME: this quick WordNet feature vector does NOT
beat GloVe on OOV (0.57 vs 0.65) -- 300-d GloVe encodes animacy + more than a 17-d WordNet vector. So the
drill's STRONG claim (features > distributional) is NOT supported by our data with THIS feature set; the
open question is whether the RICHER norms the drill names (Lancaster sensorimotor 40k x 11; Binder 65-d)
would match/beat GloVe -- untested here. Both representations recover only a MODERATE noun-side signal
(0.57-0.65): most thematic-role information is in the verb-construction RELATION, not the argument alone --
which is why a good PARSER (spaCy 0.996) is the dominant fix.
Metric = BALANCED accuracy (chance 0.5), paired bootstrap. NO external LLM at inference.

Writes only to data/exp_grounded_role_feature_fit_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
from nltk.corpus import wordnet as wn

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_grounded_role_weak_parser_v1 as W
from hdlab.animacy_lexicon import lookup_animacy

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_feature_fit_v1")
GLOVE = os.path.join(REPO, "data/exp_grounded_role_protofit_generalize_v1/glove_noun_subset.npz")
GLOVE_V = os.path.join(REPO, "data/exp_grounded_role_knn_fit_v1/glove_verb_subset.npz")
SEED = 20260830
N_BOOT = 2000
MIN_PROTO = 3
_SS = ["noun.person", "noun.animal", "noun.group", "noun.artifact", "noun.substance", "noun.object",
       "noun.food", "noun.location", "noun.body", "noun.cognition", "noun.communication", "noun.state",
       "noun.act", "noun.event", "noun.attribute"]
_PHYS = wn.synset("physical_entity.n.01")
_ABS = wn.synset("abstraction.n.06")
_fcache = {}


def _concreteness(n):
    ss = wn.synsets(n, pos=wn.NOUN)[:5]
    if not ss:
        return 0.5
    out = []
    for s in ss:
        hyp = set()
        for p in s.hypernym_paths():
            hyp.update(p)
        out.append(1.0 if _PHYS in hyp else (0.0 if _ABS in hyp else 0.5))
    return float(np.mean(out))


def nfeat(n):
    """Brain-faithful, GENERALISING noun feature vector (any noun, no LLM): animacy + concreteness +
    WordNet supersense one-hots. Animacy is the dominant role-relevant feature (the drill's finding)."""
    if n in _fcache:
        return _fcache[n]
    ss = wn.synsets(n, pos=wn.NOUN)
    ln = ss[0].lexname() if ss else None
    a = lookup_animacy(n, "NOUN")
    av = {"animate": 1.0, "inanimate": -1.0}.get(a["animacy"] if a else "unk", 0.0)
    v = np.array([av, _concreteness(n)] + [1.0 if ln == s else 0.0 for s in _SS], float)
    _fcache[n] = v
    return v


def _items(rows):
    out = []
    for r in rows:
        vb = r["toks"][r["verb_idx"] - 1].lower()
        for role, span in (("agent", r.get("agent")), ("patient", r.get("patient"))):
            if not span:
                continue
            for i in W._span_set(span):
                j = i - 1
                if 0 <= j < len(r["pos"]) and r["pos"][j] in ("NOUN", "PROPN", "PRON"):
                    out.append((vb, r["toks"][j].lower(), 1 if role == "agent" else 0))
    return out


def _feature_predictor(tri, shuffle=False, seed=SEED):
    ys = [y for _, _, y in tri]
    if shuffle:
        r = np.random.default_rng(seed); ys = list(r.permutation(ys))
    va, vp, ga, gp = defaultdict(list), defaultdict(list), [], []
    for (v, n, _), y in zip(tri, ys):
        f = nfeat(n)
        (va[v] if y == 1 else vp[v]).append(f)
        (ga if y == 1 else gp).append(f)
    GA, GP = np.mean(ga, 0), np.mean(gp, 0)
    PA = {v: np.mean(x, 0) for v, x in va.items() if len(x) >= MIN_PROTO}
    PP = {v: np.mean(x, 0) for v, x in vp.items() if len(x) >= MIN_PROTO}

    def pred(v, n):
        f = nfeat(n); pa = PA.get(v, GA); pp = PP.get(v, GP)
        return 1 if np.linalg.norm(f - pa) < np.linalg.norm(f - pp) else 0
    return pred


def _glove_predictor(tri, gn, gv, shuffle=False, seed=SEED):
    from sklearn.linear_model import LogisticRegression
    X, Y = [], []
    for v, n, y in tri:
        a, b = gv.get(v), gn.get(n)
        if a is not None and b is not None:
            X.append(np.concatenate([a, b, a * b])); Y.append(y)
    X, Y = np.array(X), np.array(Y)
    if shuffle:
        Y = np.random.default_rng(seed).permutation(Y)
    clf = LogisticRegression(max_iter=2000, C=0.1, class_weight="balanced").fit(X, Y)

    def pred(v, n):
        a, b = gv.get(v), gn.get(n)
        if a is None or b is None:
            return 0
        return int(clf.predict([np.concatenate([a, b, a * b])])[0])
    return pred


def _bal(sub, fn):
    Y = np.array([y for _, _, y in sub]); P = np.array([fn(v, n) for v, n, _ in sub])
    accs = [(P[Y == c] == Y[Y == c]).mean() for c in (0, 1) if (Y == c).sum()]
    return float(np.mean(accs)) if accs else float("nan")


def _bal_boot(sub, fa, fb, seed=SEED):
    Ya = [(int(fa(v, n) == y), y) for v, n, y in sub]
    Yb = [(int(fb(v, n) == y), y) for v, n, y in sub]
    n = len(sub); rng = np.random.default_rng(seed)

    def bal(idx, arr):
        rec = {0: [0, 0], 1: [0, 0]}
        for i in idx:
            ok, y = arr[i]; rec[y][0] += ok; rec[y][1] += 1
        parts = [rec[c][0] / rec[c][1] for c in (0, 1) if rec[c][1]]
        return np.mean(parts) if len(parts) == 2 else np.nan
    ds = []
    for _ in range(N_BOOT):
        s = rng.integers(0, n, n); d = bal(s, Ya) - bal(s, Yb)
        if not np.isnan(d):
            ds.append(d)
    ds = np.array(ds)
    return round(float(_bal(sub, fa) - _bal(sub, fb)), 4), round(float(np.percentile(ds, 2.5)), 4), round(float(np.percentile(ds, 97.5)), 4)


def run():
    rows = W._load(); key = [tuple(r["toks"]) for r in rows]
    uniq = sorted(set(key)); rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(uniq)); tr = {uniq[i] for i in perm[: int(0.7 * len(uniq))]}
    train = [r for r, k in zip(rows, key) if k in tr]; test = [r for r, k in zip(rows, key) if k not in tr]
    tri, tei = _items(train), _items(test)
    seen_noun = {n for _, n, _ in tri}
    oov = [it for it in tei if it[1] not in seen_noun]

    feat = _feature_predictor(tri); feat_tw = _feature_predictor(tri, shuffle=True)
    out = {"n_test": len(tei), "n_oov": len(oov), "base_rate_agent": round(float(np.mean([y for _, _, y in tei])), 3)}
    have_glove = os.path.exists(GLOVE) and os.path.exists(GLOVE_V)
    glove = None
    if have_glove:
        gn = {k: np.load(GLOVE)[k] for k in np.load(GLOVE).files}
        gv = {k: np.load(GLOVE_V)[k] for k in np.load(GLOVE_V).files}
        glove = _glove_predictor(tri, gn, gv)

    for name, sub in (("ALL", tei), ("OOV_noun", oov)):
        row = {"feature_bal": round(_bal(sub, feat), 4), "feature_twin_bal": round(_bal(sub, feat_tw), 4),
               "feature_vs_twin": _bal_boot(sub, feat, feat_tw)}
        if glove is not None:
            row["glove_bal"] = round(_bal(sub, glove), 4)
            row["feature_vs_glove"] = _bal_boot(sub, feat, glove)
        out[name] = row

    O = out["OOV_noun"]
    out["verdict"] = {
        "feature_fit_generalises_to_OOV_over_twin": O["feature_vs_twin"][1] > 0,
        "feature_beats_distributional_on_OOV": (glove is not None and O["feature_vs_glove"][1] > 0),
        "distributional_is_at_chance_on_OOV": (glove is not None and abs(O["glove_bal"] - 0.5) < 0.03),
        "SUCCESS_feature_generalises_where_distributional_cannot":
            (glove is not None and O["feature_vs_twin"][1] > 0 and O["feature_vs_glove"][1] > 0),
    }
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); a = ap.parse_args()
    m = run()
    if a.self_test:
        assert m["n_oov"] > 100, m["n_oov"]
        print("self-test PASS", json.dumps(m["verdict"])); return
    os.makedirs(OUTDIR, exist_ok=True); m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 98)
    print("FEATURE-BASED vs DISTRIBUTIONAL thematic fit -- generalization to NOVEL (OOV) arguments (balanced acc, chance 0.5)")
    print("=" * 98)
    print(f"n_test={m['n_test']} n_oov={m['n_oov']} base_rate_agent={m['base_rate_agent']}")
    for name in ("ALL", "OOV_noun"):
        r = m[name]
        print(f"\n{name}: FEATURE={r['feature_bal']} (twin {r['feature_twin_bal']})  GloVe={r.get('glove_bal')}")
        print(f"   feature vs twin  {r['feature_vs_twin']}")
        if 'feature_vs_glove' in r:
            print(f"   feature vs GloVe {r['feature_vs_glove']}   (the RIGHT kind of representation generalizes)")
    print("\nVERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
