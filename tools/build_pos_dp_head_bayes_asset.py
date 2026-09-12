"""tools/build_pos_dp_head_bayes_asset.py -- build ONCE, offline, the two Bayesian terms the DP-head lexical-category
correction reads at inference (pri-7 upstream POS fix; SIGNAL_FLOW_MAP §1 requires a persisted asset, never a treebank read
at read-time).

  lexical prior   P(cat | word)            : per-word NOUN/ADJ counts over UD-EWT train (the mental lexicon's category
                                            frequency knowledge; only words with >=1 NOUN or ADJ count are stored)
  syntactic LR    P(DP-head|NOUN)/P(DP-head|ADJ) : over GOLD tags, how often a NOUN vs an ADJ heads a determiner phrase
                                            (a DET precedes, skipping ADJ/ADV; no nominal follows in the phrase)
Decision at inference (hdlab.pos_tagger.DPHeadCategoryCorrection): retag a DP-head ADJ -> NOUN iff
  prior_odds(word) * syn_lr > margin (margin 1.0 = Bayes-optimal under 0-1 loss; SWEPT in the solver's cell).
Source of the computation: experiments/exp_pos_bayesian_category_v1.py (owner-DONE pri-7 chain); this tool only persists.
Output: data/frontend_assets/pos_dp_head_bayes_ud_ewt.json
Run:    .venv/Scripts/python.exe tools/build_pos_dp_head_bayes_asset.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
UD_TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
OUT = os.path.join(REPO, "data", "frontend_assets", "pos_dp_head_bayes_ud_ewt.json")


def is_dp_head(upos, i) -> bool:
    """Same test as hdlab.pos_tagger.is_dp_head (and the solver's P0._is_dp_head)."""
    j = i - 1
    while j >= 0 and upos[j] in ("ADJ", "ADV"):
        j -= 1
    if j < 0 or upos[j] != "DET":
        return False
    k = i + 1
    while k < len(upos) and upos[k] in ("ADJ", "ADV"):
        k += 1
    return not (k < len(upos) and upos[k] in ("NOUN", "PROPN"))


def read_conllu(path):
    sents, cur = [], []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if not ln:
                if cur:
                    sents.append(cur); cur = []
                continue
            if ln.startswith("#"):
                continue
            cols = ln.split("\t")
            if "-" in cols[0] or "." in cols[0]:
                continue
            cur.append((cols[1], cols[3]))
    if cur:
        sents.append(cur)
    return sents


def build(train=UD_TRAIN, out=OUT) -> dict:
    sents = read_conllu(train)
    lex = defaultdict(lambda: [0, 0])          # word -> [NOUN count, ADJ count]
    dphead = {"NOUN": 0, "ADJ": 0}; total = {"NOUN": 0, "ADJ": 0}
    for s in sents:
        gold = [g for _, g in s]
        for i, (w, g) in enumerate(s):
            if g in ("NOUN", "ADJ"):
                lex[w.lower()][0 if g == "NOUN" else 1] += 1
                total[g] += 1
                if is_dp_head(gold, i):
                    dphead[g] += 1
    pN = dphead["NOUN"] / max(1, total["NOUN"]); pA = dphead["ADJ"] / max(1, total["ADJ"])
    asset = {"source": os.path.relpath(train, REPO), "n_sents": len(sents),
             "lex": {w: c for w, c in lex.items()},
             "p_dphead_noun": pN, "p_dphead_adj": pA, "syn_lr": (pN + 1e-9) / (pA + 1e-9),
             "margin": 1.0, "min_train_evidence": 3,
             "computation": "P(NOUN|word,DP-head)/P(ADJ|word,DP-head) = prior_odds(word) * P(DP-head|NOUN)/P(DP-head|ADJ); "
                            "retag iff > margin (MacDonald-Pearlmutter-Seidenberg constraint satisfaction; Trueswell-Tanenhaus)"}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(asset, f)
    print("[asset] %s: %d sents, %d lexical entries, syn_lr=%.3f (pN=%.4f pA=%.4f)" % (
        os.path.relpath(out, REPO), len(sents), len(asset["lex"]), asset["syn_lr"], pN, pA))
    return asset


if __name__ == "__main__":
    build()
