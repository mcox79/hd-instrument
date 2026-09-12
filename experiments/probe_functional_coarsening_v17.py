"""PROBE v17 (categories -> heads hand-off): CONSUMER-GUIDED, LABEL-FREE COARSENING of the reading-induced categories.
The attachment learner (SelfSupEM) needs a small set of the RIGHT functional classes (v15/v16: fine 70-way 0.012-0.036,
gold-named 17-way 0.208, label-free k=17 clustering 0.126 = twin). Here the coarse classes are defined by the fine clusters'
SYNTACTIC BEHAVIOUR as the learner itself sees it: each fine cluster's profile = its directional head/dependent co-occurrence
distribution from the learner's first pass (P(head cat | dep=c, dir) ++ P(dep cat | head=c, dir)); clusters with the same
profile are merged (agglomerative, cosine) down to K functional classes; the learner is re-run on the merged inventory.
PLUS the form-class constraint (punctuation / numerals never head or root -- a mark is not a word).
Arms: K in {12, 17, 25, 34}; fine 70 with the constraint; gold-POS reference with/without the constraint; twin = shuffled merge map.
Run: .venv/Scripts/python.exe experiments/probe_functional_coarsening_v17.py [--smoke]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import json
import sys
import time
from collections import defaultdict

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_parser_fully_bf_chain_v1 as C1
from experiments.exp_parser_selfsup_em_v1 import SelfSupEM, _adj_right_uas
from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TRAIN, UD_TEST

ASSET = os.path.join(_REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json")
FORM = {"C68", "C69"}          # the two orthographic form classes of the k68 asset (punctuation, numerals)


class FormAwareEM(SelfSupEM):
    NONHEAD: set = set()

    def _score_matrix(self, toks, pos):
        A, n = SelfSupEM._score_matrix(self, toks, pos)
        words = [j for j in range(1, n + 1) if pos[j - 1] not in self.NONHEAD]
        for i in range(1, n + 1):
            if pos[i - 1] in self.NONHEAD:
                A[i, :] = -np.inf
                if words:
                    A[0][i] = -np.inf
        return A, n


def train_scorer(catseqs, rounds, nonhead):
    tr = [[(0, "x", c, 0, "_") for c in cs] for cs in catseqs]
    FormAwareEM.NONHEAD = set(nonhead)
    m = FormAwareEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(tr)
    for _ in range(rounds):
        m.em_round(tr)
        m2 = FormAwareEM(lam=0.3, prior_weight=0.0, lex_weight=0.0)
        m2.cpair, m2.cdep, m2.lpair, m2.ldep, m2.crootpos, m2.rootden = m.cpair, m.cdep, m.lpair, m.ldep, m.crootpos, m.rootden
        m = m2
    return m


def behaviour_profiles(m, cats):
    """Per fine category: its directional attachment behaviour as the learner sees it (normalised head|dep and dep|head rows)."""
    ix = {c: k for k, c in enumerate(cats)}; K = len(cats)
    P = np.zeros((K, 4 * K))
    for (ph, pd, dr), c in m.cpair.items():
        if ph in ix and pd in ix:
            d = 0 if dr == "L" else 1
            P[ix[pd], d * K + ix[ph]] += c           # as dependent: who heads me (by direction)
            P[ix[ph], (2 + d) * K + ix[pd]] += c     # as head: whom I head
    for blk in range(4):
        sl = slice(blk * K, (blk + 1) * K); s = P[:, sl].sum(1, keepdims=True) + 1e-9; P[:, sl] /= s
    return P


def merge_by_behaviour(P, cats, K_out, mass):
    """Agglomerative (average-link, cosine) merging of fine categories by behaviour profile, mass-weighted centroids."""
    groups = [[k] for k in range(len(cats))]
    cen = [P[k].copy() for k in range(len(cats))]; w = [float(mass[k]) for k in range(len(cats))]
    def cos(a, b):
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    while len(groups) > K_out:
        best, bi, bj = -2.0, -1, -1
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                s = cos(cen[i], cen[j])
                if s > best:
                    best, bi, bj = s, i, j
        cen[bi] = (cen[bi] * w[bi] + cen[bj] * w[bj]) / (w[bi] + w[bj]); w[bi] += w[bj]
        groups[bi] += groups.pop(bj); cen.pop(bj); w.pop(bj)
    return {cats[k]: "F%d" % g for g, grp in enumerate(groups) for k in grp}


def main():
    smoke = "--smoke" in sys.argv
    t0 = time.time()
    train = load_ud(UD_TRAIN, cap=2500 if smoke else 8000, maxlen=40)
    test = load_ud(UD_TEST, cap=150 if smoke else 700)
    rounds = 1 if smoke else 2
    w2c = {w: "C%d" % c for w, c in json.load(open(ASSET, encoding="utf-8"))["word2cat"].items()}
    tr_f = [C1._cat_seq([t[1] for t in s], w2c) for s in train]; te_f = [C1._cat_seq([t[1] for t in s], w2c) for s in test]
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_")
                             for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    out = {"adjacent_right_floor": round(floor, 4), "arms": {}}
    # fine inventory with the form constraint (the profile source)
    m_f = train_scorer(tr_f, rounds, FORM)
    out["arms"]["fine70_formaware"] = round(C1._uas(m_f, test, te_f), 4)
    print("fine70 form-aware:", out["arms"]["fine70_formaware"], flush=True)
    cats = sorted({c for cs in tr_f for c in cs if c not in FORM and c != "UNK"})
    mass = {c: 0.0 for c in cats}
    for cs in tr_f:
        for c in cs:
            if c in mass:
                mass[c] += 1
    P = behaviour_profiles(m_f, cats)
    rng = np.random.default_rng(7)
    for K in ([17] if smoke else [12, 17, 25, 34]):
        merge = merge_by_behaviour(P, cats, K, [mass[c] for c in cats])
        merge.update({c: c for c in FORM}); merge["UNK"] = "UNK"
        tr_m = [[merge.get(c, "UNK") for c in cs] for cs in tr_f]; te_m = [[merge.get(c, "UNK") for c in cs] for cs in te_f]
        m = train_scorer(tr_m, rounds, FORM)
        uas = C1._uas(m, test, te_m)
        # twin: same group SIZES, random assignment of fine clusters to groups
        vals = [merge[c] for c in cats]; rng.shuffle(vals); tw_map = dict(zip(cats, vals)); tw_map.update({c: c for c in FORM}); tw_map["UNK"] = "UNK"
        m_tw = train_scorer([[tw_map.get(c, "UNK") for c in cs] for cs in tr_f], rounds, FORM)
        tw = C1._uas(m_tw, test, [[tw_map.get(c, "UNK") for c in cs] for cs in te_f])
        groups = defaultdict(list)
        for c, g in merge.items():
            groups[g].append(c)
        out["arms"]["functional_K%d" % K] = {"uas": round(uas, 4), "twin_shuffled_merge": round(tw, 4),
                                             "group_sizes": sorted([len(v) for v in groups.values()], reverse=True)}
        print("functional K=%d: UAS=%.4f twin=%.4f" % (K, uas, tw), flush=True)
    tr_g = [[t[2] for t in s] for s in train]; te_g = [[t[2] for t in s] for s in test]
    out["arms"]["goldPOS_formaware"] = round(C1._uas(train_scorer(tr_g, rounds, {"PUNCT", "NUM", "SYM"}), test, te_g), 4)
    out["arms"]["goldPOS_plain_ref"] = round(C1._uas(C1._train_scorer(tr_g, rounds, prior_weight=0.0), test, te_g), 4)
    out["elapsed_s"] = round(time.time() - t0, 1); out["smoke"] = smoke
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir   # Q115: canonical re-runnable output dir
    od = str(get_output_dir("probe_functional_coarsening_v17" + ("_smoke" if smoke else "")))
    os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
