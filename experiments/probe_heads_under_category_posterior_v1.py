"""PROBE: the categories -> heads hand-off on the LIVE organs. UAS of the attachment arm (live asset) on UD-EWT test 700 under
(a) gold categories, (b) the category organ's HARD tags (argmax posterior), (c) the GRADED mixture over the posterior
(attachment_arm.arc_scores_graded: second-best category kept alive for tokens with top mass < tau). Per relation too.
Run: python experiments/probe_heads_under_category_posterior_v1.py [--tau 0.8]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import json
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir  # Q115: route the output dir
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from tools.build_attachment_validities import sentences, TEST, CORE_RELS

tau = float(sys.argv[sys.argv.index("--tau") + 1]) if "--tau" in sys.argv else AA.TAG_GRADED_TAU
AA.TAG_GRADED_TAU = tau


def score(name, head_fn, test):
    c = t = 0; rt = {}; rh = {}; t0 = time.time()
    for toks, gold_pos, gold_heads, rels in test:
        hd = head_fn(toks, gold_pos)
        for i, g in enumerate(gold_heads, start=1):
            if 0 <= g <= len(toks):
                ok = int(hd.get(i, -1) == g); c += ok; t += 1
                r = rels[i - 1]
                if r in CORE_RELS:
                    rt[r] = rt.get(r, 0) + 1; rh[r] = rh.get(r, 0) + ok
    out = {"uas": round(c / max(1, t), 4), "per_relation": {r: round(rh[r] / rt[r], 3) for r in CORE_RELS if r in rt}, "ms_per_sent": round(1000 * (time.time() - t0) / len(test), 1)}
    print("%-18s UAS %.4f  %s  (%.0f ms/sent)" % (name, out["uas"], out["per_relation"], out["ms_per_sent"]), flush=True)
    return out


def main():
    test = sentences(TEST, cap=700, maxlen=10**6)
    tab = AA.load_attachment_validities(); lc = LC.get()
    tag_cache = {}
    def tagged(toks):
        k = tuple(toks)
        if k not in tag_cache:
            tag_cache[k] = lc.tag_with_posterior(list(toks))
        return tag_cache[k]
    agree = tot = 0
    for toks, gold_pos, _, _ in test:
        for x, y in zip(tagged(toks)[0], gold_pos):
            agree += int(x == y); tot += 1
    print("category organ agreement with gold UPOS on the test slice: %.4f (%d tokens)" % (agree / tot, tot), flush=True)
    res = {"tau": tau, "tag_agreement": round(agree / tot, 4)}
    res["gold_categories"] = score("gold categories", lambda toks, gp: AA.heads(toks, gp, tab), test)
    res["hard_predicted"] = score("hard predicted", lambda toks, gp: AA.heads(toks, tagged(toks)[0], tab), test)
    res["graded_predicted"] = score("graded predicted", lambda toks, gp: AA.heads_graded(toks, tagged(toks)[0], tagged(toks)[1], tab), test)
    od = str(get_output_dir("probe_heads_under_category_posterior_v1")); os.makedirs(od, exist_ok=True)
    json.dump(res, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: (v["uas"] if isinstance(v, dict) and "uas" in v else v) for k, v in res.items()}))


if __name__ == "__main__":
    main()
