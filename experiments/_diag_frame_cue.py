"""DIAG (strategy 2026-09-13): the FREQUENT-FRAME cue in the category organ (lexical_categories.use_frame; Mintz 2003).
Builds a candidate counts asset WITH frame tables (same supply and flags as the live asset: order 2, shape, rare_max 2, cluster cue)
at data/hook_state/lexical_categories_counts_v1_frame.json, then on the FULL UD-EWT test (lag 2 = the live default):
  UPOS accuracy, unknown-word accuracy, and the two head-costly confusions (VERB->AUX, SCONJ->ADP) for FRAME_KAPPA in {0, 0.5, 1.0}
  and FRAME_F in {300, 1000}  (kappa 0 = the live organ), then heads UAS (live attachment asset, in-order decode) on test 700 under the
  organ's own tags for the live config vs the best frame config. Output: data/exp_diag_frame_cue_v1/metrics.json.
Run: python experiments/_diag_frame_cue.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json
import sys
import time
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
import hdlab.lexical_categories as LC

CAND = os.path.join(REPO, "data", "hook_state", "lexical_categories_counts_v1_frame.json")
TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")


def read_test():
    sents, cur = [], []
    with open(TEST, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            cur.append((c[1], c[3]))
    if cur:
        sents.append(cur)
    return sents


def evaluate(m, sents, lag=2):
    tot = ok = unk = unk_ok = 0; conf = Counter(); t0 = time.time()
    for s in sents:
        words = [w for w, _ in s]; gold = [g for _, g in s]
        post = m.posterior(words, lag=lag); pred = [m.tags[int(i)] for i in post.argmax(axis=1)]
        for w, g, p in zip(words, gold, pred):
            tot += 1; ok += int(g == p)
            if w.lower() not in m.vocab:
                unk += 1; unk_ok += int(g == p)
            if g != p:
                conf[(g, p)] += 1
    return {"acc": round(ok / tot, 4), "unknown_acc": round(unk_ok / max(1, unk), 4), "tokens": tot,
            "VERB->AUX": conf[("VERB", "AUX")], "AUX->VERB": conf[("AUX", "VERB")], "SCONJ->ADP": conf[("SCONJ", "ADP")],
            "ADP->SCONJ": conf[("ADP", "SCONJ")], "sec": round(time.time() - t0, 1)}


def main():
    if not os.path.exists(CAND):
        t0 = time.time()
        info = LC.build_asset(out=CAND, order=2, use_shape=True, rare_max=2, use_cluster=True, use_frame=True)
        print("built candidate asset", info, "%.0fs" % (time.time() - t0), flush=True)
    sents = read_test()
    m = LC.LexicalCategories.load(CAND)
    res = {"configs": []}
    best = None
    for F in (300, 1000):
        LC.FRAME_F = F; m.finalize()
        for kappa in ((0.0, 0.5, 1.0) if F == 300 else (0.5, 1.0)):
            LC.FRAME_KAPPA = kappa
            r = evaluate(m, sents); r.update({"FRAME_F": F, "FRAME_KAPPA": kappa}); res["configs"].append(r)
            print(json.dumps(r), flush=True)
            if kappa > 0 and (best is None or r["acc"] > best["acc"]):
                best = r
    res["best"] = best
    # heads under the organ's own tags: live config (kappa 0) vs best frame config
    import hdlab.attachment_arm as AA
    from tools.build_attachment_validities import sentences, TEST as T2, CORE_RELS
    test = sentences(T2, cap=700, maxlen=10**6); tab = AA.load_attachment_validities()

    def uas(tagger):
        c = t = 0; rt = Counter(); rh = Counter()
        for toks, gold_pos, gold_heads, rels in test:
            pred = tagger(list(toks)); hd = AA.heads(toks, pred, tab)
            for i, g in enumerate(gold_heads, start=1):
                if 0 <= g <= len(toks):
                    ok = int(hd.get(i, -1) == g); c += ok; t += 1
                    if rels[i - 1] in CORE_RELS:
                        rt[rels[i - 1]] += 1; rh[rels[i - 1]] += ok
        return {"uas": round(c / t, 4), "per_relation": {r: round(rh[r] / rt[r], 3) for r in CORE_RELS if rt[r]}}

    LC.FRAME_F = 300; m.finalize(); LC.FRAME_KAPPA = 0.0
    res["heads_live_tags"] = uas(lambda toks: m.tag(toks)); print("heads under live tags:", json.dumps(res["heads_live_tags"]), flush=True)
    LC.FRAME_F = best["FRAME_F"]; m.finalize(); LC.FRAME_KAPPA = best["FRAME_KAPPA"]
    res["heads_frame_tags"] = uas(lambda toks: m.tag(toks)); print("heads under frame tags:", json.dumps(res["heads_frame_tags"]), flush=True)
    od = str(get_output_dir("diag_frame_cue_v1")); os.makedirs(od, exist_ok=True)
    json.dump(res, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print("DONE best", json.dumps(best))


if __name__ == "__main__":
    main()
