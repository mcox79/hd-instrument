"""verify_ppmi_svd_oracle_group_disjoint_cv -- supplementary robustness check for C1_FITTED_ORACLE.

exp_corpus_capacity_ppmi_svd_ceiling_v1's C1_FITTED_ORACLE held-out figure (0.9606) uses a
pair-level 5-fold StratifiedKFold, NOT word-disjoint: 232/617 (37.6%) of the words appearing in
the 484 matched pairs (242 P + 242 S) appear in MORE THAN ONE pair (max reuse count 7), so the
same word's SVD embedding can appear in both a training pair and a test pair, letting the fitted
model partly exploit per-word identity rather than a genuinely unseen-pair signal.

This script re-derives the SAME k=100 PPMI-SVD feature space (reusing
exp_corpus_capacity_ppmi_svd_ceiling_v1.build_matrix / ppmi_of / l2n_dense verbatim, same seed
convention) and re-scores C1 under a GROUP-DISJOINT split: union-find over the 617 words (grouping
by shared pair membership) yields 148 connected components (largest holds 7.1% of words), and
GroupKFold splits by COMPONENT so no word ever appears in both train and test.

MEASURED 2026-08-18 (this script, deterministic given the pinned seeds):
  GROUP-DISJOINT (word-level, no leakage) 5-fold CV AUC = 0.8629
  PAIR-LEVEL (word-sharing allowed, matches the landed cell's convention) 5-fold CV AUC = 0.9587
The group-disjoint estimate is markedly lower than the pair-level one (confirming the leakage
concern is real, not hypothetical) but STILL clears 0.5 by a wide margin -- the fitted-oracle
finding (information present in first-order counts, reachable by supervised fit, not reached by
any unsupervised transform) holds up under the stricter test. Cited in
notes/corpus_capacity_ppmi_svd_ceiling_2026-08-18.md.

Not part of exp_corpus_capacity_ppmi_svd_ceiling_v1's own landed metrics.json / regression gate --
this is a standalone supplementary verification, run manually, not dispatched via queue_add.
ASCII-only. NO LLM anywhere. Classical linear algebra + sklearn logistic regression only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import time
from collections import Counter

import numpy as np
from scipy.sparse.linalg import svds
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedKFold

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_corpus_capacity_ppmi_svd_ceiling_v1 as CC   # noqa: E402  READ ONLY
import experiments.exp_dissociation_score_instrument_v1 as DSI     # noqa: E402  READ ONLY
from tools.exp_checkpoint import unit_key, load_units              # noqa: E402


def union_find_components(pairs):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for w1, w2, _ in pairs:
        union(w1, w2)
    return {w: find(w) for w1, w2, _ in pairs for w in (w1, w2)}


def main() -> int:
    units = load_units(os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1"))
    pop = units[unit_key("POPULATION", "v1.7", "full")]
    matchedP = [tuple(x) for x in pop["matchedP"]]
    matchedS = [tuple(x) for x in pop["matchedS"]]
    pairs = matchedP + matchedS

    comp_of = union_find_components(pairs)
    comp_sizes = Counter(comp_of.values())
    print("n_words=%d n_components=%d largest_component_frac_words=%.4f" %
         (len(comp_of), len(comp_sizes), max(comp_sizes.values()) / len(comp_of)))

    pair_comp = [comp_of[w1] for w1, w2, _ in pairs]
    for (w1, w2, _), c in zip(pairs, pair_comp):
        assert comp_of[w2] == c, "a pair spans two components -- union-find bug"

    t0 = time.time()
    C = CC.CTS.load_cache()
    anchor_words_full = [a for a, ok in zip(C["anchors"], np.asarray(C["mat_ok"], dtype=bool)) if ok]
    M, row_idx, _diag = CC.build_matrix(anchor_words_full)
    Mppmi = CC.ppmi_of(M)
    print("matrix+ppmi built in %.1fs" % (time.time() - t0))

    t1 = time.time()
    U, S, Vt = svds(Mppmi.asfptype(), k=100, random_state=CC.MASTER_SEED + 7100)
    order = np.argsort(-S)
    U, S = U[:, order], S[order]
    vecs = CC.l2n_dense(U * np.sqrt(np.maximum(S, 0.0))[None, :])
    print("svd k=100 done in %.1fs" % (time.time() - t1))

    y = np.array([1] * len(matchedP) + [0] * len(matchedS))
    X = np.zeros((len(pairs), vecs.shape[1]))
    comp_id_map = {c: i for i, c in enumerate(sorted(set(pair_comp)))}
    groups = np.array([comp_id_map[c] for c in pair_comp])
    for i, (w1, w2, _p) in enumerate(pairs):
        X[i] = vecs[row_idx[w1]] * vecs[row_idx[w2]]

    n_splits = min(5, len(set(groups)))
    gkf = GroupKFold(n_splits=n_splits)
    oof_group = np.zeros(len(y))
    for tr, te in gkf.split(X, y, groups):
        clf = LogisticRegression(C=1.0, max_iter=2000, random_state=0)
        clf.fit(X[tr], y[tr])
        oof_group[te] = clf.decision_function(X[te])
    auc_group = DSI.auc_of(oof_group[y == 1], oof_group[y == 0])
    print("GROUP-DISJOINT (word-level, no leakage) %d-fold CV AUC = %.4f" % (n_splits, auc_group))

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=CC.MASTER_SEED + 5153)
    oof_pair = np.zeros(len(y))
    for tr, te in skf.split(X, y):
        clf = LogisticRegression(C=1.0, max_iter=2000, random_state=0)
        clf.fit(X[tr], y[tr])
        oof_pair[te] = clf.decision_function(X[te])
    auc_pair = DSI.auc_of(oof_pair[y == 1], oof_pair[y == 0])
    print("PAIR-LEVEL (word-sharing allowed across folds) 5-fold CV AUC = %.4f" % auc_pair)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
