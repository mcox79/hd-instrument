"""PROBE v15 (upstream pass, top rung -> heads rung): does a BETTER top rung pass MORE signal down?
Re-runs the fully brain-foundational acquisition chain of exp_parser_fully_bf_chain_v1 (induced categories -> reading-learned
arc scorer SelfSupEM, no prior -> exact graded CLE decode; ZERO gold anywhere in acquisition) with the categories swapped:
  v1 (2026-09-10): categories induced from 8k UD-EWT sentences, k=17 -> many-to-one 0.323 -> chain UAS 0.034 (twin ~0.03)
  HERE          : categories induced from 1M Simple-Wikipedia lines, k=68+2 (exp_reading_induced_categories_v1, m2o 0.745)
Arms (UD-EWT test UAS, gold used only as the reference): READING-CATS chain; gold-POS no-prior reference; shuffled-cluster twin;
adjacent-right strong floor. Also reports how many test tokens are covered by the reading vocabulary (UNK -> 'UNK' category).
Run: .venv/Scripts/python.exe experiments/probe_fully_bf_chain_with_reading_categories_v15.py [--smoke]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import json
import sys
import time

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_parser_fully_bf_chain_v1 as C1
from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TRAIN, UD_TEST
from experiments.exp_parser_selfsup_em_v1 import _adj_right_uas

ASSET = os.path.join(_REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json")


def main():
    smoke = "--smoke" in sys.argv
    t0 = time.time()
    train = load_ud(UD_TRAIN, cap=2500 if smoke else 8000, maxlen=40)
    test = load_ud(UD_TEST, cap=150 if smoke else 700)
    rounds = 1 if smoke else 2
    word2cat = {w: "C%d" % c for w, c in json.load(open(ASSET, encoding="utf-8"))["word2cat"].items()}
    m2o, cov, cmap = C1.many_to_one(test, word2cat)
    tr_ind = [C1._cat_seq([t[1] for t in s], word2cat) for s in train]
    te_ind = [C1._cat_seq([t[1] for t in s], word2cat) for s in test]
    tr_gold = [[t[2] for t in s] for s in train]
    te_gold = [[t[2] for t in s] for s in test]
    unk = sum(c == "UNK" for cs in te_ind for c in cs) / max(1, sum(len(cs) for cs in te_ind))
    m_bf = C1._train_scorer(tr_ind, rounds, prior_weight=0.0)
    uas_bf = C1._uas(m_bf, test, te_ind)
    m_gold = C1._train_scorer(tr_gold, rounds, prior_weight=0.0)
    uas_gold = C1._uas(m_gold, test, te_gold)
    words = list(word2cat); perm = np.random.default_rng(1).permutation(len(words))
    w2c_tw = {words[i]: word2cat[words[perm[i]]] for i in range(len(words))}
    m_tw = C1._train_scorer([C1._cat_seq([t[1] for t in s], w2c_tw) for s in train], rounds, prior_weight=0.0)
    uas_tw = C1._uas(m_tw, test, [C1._cat_seq([t[1] for t in s], w2c_tw) for s in test])
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_")
                             for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    out = {"categories": {"source": os.path.basename(ASSET), "many_to_one_on_ud_test": round(m2o, 4), "coverage": cov,
                          "unk_token_share": round(unk, 4)},
           "uas": {"READING_CATS_chain_no_prior": round(uas_bf, 4), "gold_pos_no_prior_ref": round(uas_gold, 4),
                   "shuffled_cluster_twin": round(uas_tw, 4), "adjacent_right_floor": round(floor, 4),
                   "v1_reference_induced_8k_k17": 0.0342, "supervised_ceiling": 0.782},
           "elapsed_s": round(time.time() - t0, 1), "smoke": smoke}
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir   # Q115: canonical re-runnable output dir
    od = str(get_output_dir("probe_fully_bf_chain_with_reading_categories_v15" + ("_smoke" if smoke else "")))
    os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
