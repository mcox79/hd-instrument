"""PROBE v16 (categories -> heads hand-off, lever b): the reading-learned attachment scorer (SelfSupEM, no prior, no gold) learns
from the SAME READING as the categories -- Simple-Wikipedia lines mapped to induced-category sequences -- instead of 8k
treebank sentences; UAS on UD-EWT test (gold used only as the reference). Sweeps the reading budget for the scorer and the
category inventory (k68 raw vs k17 coarse when present). Floors: adjacent-right; shuffled-cluster twin at the largest budget.
Run: .venv/Scripts/python.exe experiments/probe_scorer_learns_from_reading_v16.py [--smoke]
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
from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TEST
from experiments.exp_parser_selfsup_em_v1 import SelfSupEM, _adj_right_uas
from experiments.exp_reading_induced_categories_v1 import read_lines, SIMPLEWIKI

ASSETS = {"k68": os.path.join(_REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json"),
          "k17": os.path.join(_REPO, "data", "exp_reading_induced_categories_v1", "induced_categories_l1000000_k17.json")}


def scorer_from_reading(word2cat, n_lines, rounds, maxlen=40):
    seqs = []
    for toks in read_lines(SIMPLEWIKI, n_lines):
        if 3 <= len(toks) <= maxlen:
            seqs.append([(0, "x", word2cat.get(t, "UNK"), 0, "_") for t in toks])
    m = SelfSupEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(seqs)
    for _ in range(rounds):
        m.em_round(seqs)
    return m, len(seqs)


def main():
    smoke = "--smoke" in sys.argv
    test = load_ud(UD_TEST, cap=150 if smoke else 700)
    budgets = [5000] if smoke else [8000, 20000, 50000]
    rounds = 1 if smoke else 2
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_")
                             for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    out = {"adjacent_right_floor": round(floor, 4), "arms": []}
    for name, path in ASSETS.items():
        if not os.path.exists(path):
            print("skip", name, "(asset absent)"); continue
        w2c = {w: "C%d" % c for w, c in json.load(open(path, encoding="utf-8"))["word2cat"].items()}
        te = [C1._cat_seq([t[1] for t in s], w2c) for s in test]
        for b in budgets:
            t0 = time.time(); m, n = scorer_from_reading(w2c, b, rounds)
            uas = C1._uas(m, test, te)
            row = {"inventory": name, "lines_read": b, "sentences_used": n, "uas": round(uas, 4), "elapsed_s": round(time.time() - t0, 1)}
            out["arms"].append(row); print(row, flush=True)
        words = list(w2c); perm = np.random.default_rng(1).permutation(len(words))
        w2c_tw = {words[i]: w2c[words[perm[i]]] for i in range(len(words))}
        m_tw, _ = scorer_from_reading(w2c_tw, budgets[-1], rounds)
        tw = C1._uas(m_tw, test, [C1._cat_seq([t[1] for t in s], w2c_tw) for s in test])
        out["arms"].append({"inventory": name, "lines_read": budgets[-1], "twin_shuffled_clusters_uas": round(tw, 4)})
        print("twin", name, round(tw, 4), flush=True)
    from experiments._seed_checkpoint import get_output_dir   # Q115: canonical re-runnable output dir
    od = str(get_output_dir("probe_scorer_learns_from_reading_v16" + ("_smoke" if smoke else "")))
    os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
