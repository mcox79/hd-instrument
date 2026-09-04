"""Quantify the memoization opportunity in _arc_ids -- how redundant are the features?

Measures, over the SAME sentence set the profiler uses:
  - total feature-strings emitted vs DISTINCT strings  (sizes: crc32/string memo)
  - total arcs vs DISTINCT full feature-signatures      (sizes: whole-array memo)
  - distinct POS-only vs word-involving sub-signatures
This tells us which byte-identical optimization has the leverage. Writes only to its own dir.
"""
from __future__ import annotations
import os
import sys
import json
from collections import Counter

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_arc_parser_profile_v1 as P
import hdlab.arc_parser as A

_OUT = os.path.join(_REPO, "data/exp_arc_parser_feature_stats_v1")


def feat_strings(sent, i, h):
    """Replicate _arc_ids' feature-string list EXACTLY (order preserved), returning (F, sig_tuple)."""
    n = len(sent)
    dw, dp = sent[i - 1][1].lower(), sent[i - 1][2]
    if h == 0:
        hw, hp, d, dr = "<ROOT>", "ROOT", 0, "R"
    else:
        hw, hp = sent[h - 1][1].lower(), sent[h - 1][2]
        d = h - i
        dr = "L" if d < 0 else "R"
    db = A._dist(d)
    sdw, shw = A._suf(dw), A._suf(hw)
    F = ["b", "hp:" + hp, "dp:" + dp, "hp_dp:%s_%s" % (hp, dp), "hp_dp_dir:%s_%s_%s" % (hp, dp, dr),
         "hp_dp_dist:%s_%s_%s" % (hp, dp, db), "dw:" + dw, "hw:" + hw, "hw_dw:%s_%s" % (hw, dw),
         "hp_dw:%s_%s" % (hp, dw), "hw_dp:%s_%s" % (hw, dp), "dp_dir:%s_%s" % (dp, dr), "dp_dist:%s_%s" % (dp, db),
         "dsuf_hp:%s_%s" % (sdw, hp), "hsuf_dp:%s_%s" % (shw, dp), "dsuf_dp_dir:%s_%s_%s" % (sdw, dp, dr)]
    hp_l = sent[h - 2][2] if h >= 2 else "<S>"
    dp_l = sent[i - 2][2] if i >= 2 else "<S>"
    dp_r = sent[i][2] if i < n else "<E>"
    hp_r = sent[h][2] if 0 < h < n else "<E>"
    F += ["hpl_hp_dp:%s_%s_%s" % (hp_l, hp, dp), "dpl_dp_dir:%s_%s_%s" % (dp_l, dp, dr), "dpr_dp:%s_%s" % (dp_r, dp),
          "hpr_hp_dp:%s_%s_%s" % (hp_r, hp, dp)]
    hasV = hasP = False
    bn = ""
    if h != 0:
        lo, hi = min(i, h), max(i, h)
        between = [sent[k - 1][2] for k in range(lo + 1, hi)]
        hasV = "VERB" in between
        hasP = "PUNCT" in between
        if hasV:
            F.append("bV:%s_%s" % (hp, dp))
        if hasP:
            F.append("bP:%s_%s" % (hp, dp))
        bn = A._dist(len(between))
        F.append("dp_bn:%s_%s" % (dp, bn))
    # full signature (everything that determines the array), pos-part, word-part
    full = (hp, dp, dr, db, hp_l, dp_l, dp_r, hp_r, hasV, hasP, bn, dw, hw, sdw, shw)
    pos_sig = (hp, dp, dr, db, hp_l, dp_l, dp_r, hp_r, hasV, hasP, bn)
    word_sig = (dw, hw, dp, hp, dr)
    return F, full, pos_sig, word_sig


def main(n_sents: int = 250):
    os.makedirs(_OUT, exist_ok=True)
    sents_tp = P.load_sentences(n_sents)
    tot_str = distinct_str = 0
    tot_arc = 0
    S = set()
    full_set, pos_set, word_set = set(), set(), set()
    for toks, pos in sents_tp:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        n = len(sent)
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                F, full, ps, ws = feat_strings(sent, i, h)
                tot_arc += 1
                tot_str += len(F)
                for f in F:
                    S.add(f)
                full_set.add(full)
                pos_set.add(ps)
                word_set.add(ws)
    distinct_str = len(S)
    r = {
        "n_sents": len(sents_tp), "tot_arcs": tot_arc, "tot_feat_strings": tot_str,
        "distinct_feat_strings": distinct_str,
        "string_reuse_factor": round(tot_str / max(1, distinct_str), 2),
        "distinct_full_arc_sigs": len(full_set),
        "full_sig_reuse_factor": round(tot_arc / max(1, len(full_set)), 2),
        "distinct_pos_sigs": len(pos_set),
        "pos_sig_reuse_factor": round(tot_arc / max(1, len(pos_set)), 2),
        "distinct_word_sigs": len(word_set),
        "word_sig_reuse_factor": round(tot_arc / max(1, len(word_set)), 2),
    }
    print(json.dumps(r, indent=2), flush=True)
    with open(os.path.join(_OUT, "stats.json"), "w", encoding="ascii") as f:
        json.dump(r, f, indent=2)


if __name__ == "__main__":
    main()
