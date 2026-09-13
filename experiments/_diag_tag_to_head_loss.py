"""DIAG: WHICH category errors cost the heads rung its 1.5 points (0.6125 gold tags -> 0.598 organ tags, UD-EWT test 700)?
For every sentence where the category organ's hard tags differ from gold, decode heads under both tag sequences (live asset, live
decode) and attribute each head FLIP (right under gold tags, wrong under organ tags; and the reverse = repairs) to the mis-tagged
tokens in that sentence: the flipped word itself, its gold head, or another token. Report confusion pairs (gold -> predicted) ranked by
net head loss, and the relation of the flipped arcs. Read-only; cores capped. Output: data/exp_diag_tag_to_head_loss_v1/metrics.json.
Run: python experiments/_diag_tag_to_head_loss.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from tools.build_attachment_validities import sentences, TEST, CORE_RELS


def main():
    test = sentences(TEST, cap=700, maxlen=10**6)
    tab = AA.load_attachment_validities(); lc = LC.get()
    conf_loss = Counter(); conf_gain = Counter(); conf_tokens = Counter()
    where = Counter(); rel_loss = Counter(); rel_gain = Counter()
    n_sent_err = n_flip_loss = n_flip_gain = n_tok = n_tag_err = 0
    examples = defaultdict(list)
    for toks, gold_pos, gold_heads, rels in test:
        pred_pos = lc.tag_with_posterior(list(toks))[0]
        n_tok += len(toks)
        errs = {i + 1: (gold_pos[i], pred_pos[i]) for i in range(len(toks)) if pred_pos[i] != gold_pos[i]}
        n_tag_err += len(errs)
        for g, p in errs.values():
            conf_tokens[(g, p)] += 1
        if not errs:
            continue
        n_sent_err += 1
        hg = AA.heads(toks, gold_pos, tab); hp = AA.heads(toks, list(pred_pos), tab)
        for i, g in enumerate(gold_heads, start=1):
            if not (0 <= g <= len(toks)):
                continue
            okg = hg.get(i, -1) == g; okp = hp.get(i, -1) == g
            if okg == okp:
                continue
            r = rels[i - 1]
            # attribute to the mis-tagged tokens: the word itself, its gold head, else the nearest other error
            if i in errs:
                site = "self"; pair = errs[i]
            elif g in errs:
                site = "gold_head"; pair = errs[g]
            else:
                j = min(errs, key=lambda k: abs(k - i)); site = "other"; pair = errs[j]
            if okg and not okp:
                n_flip_loss += 1; conf_loss[pair] += 1; where[("loss", site)] += 1; rel_loss[r] += 1
                if len(examples[pair]) < 3:
                    examples[pair].append(" ".join(toks) + "  | word=%s rel=%s site=%s" % (toks[i - 1], r, site))
            else:
                n_flip_gain += 1; conf_gain[pair] += 1; where[("gain", site)] += 1; rel_gain[r] += 1
    net = Counter({k: conf_loss[k] - conf_gain.get(k, 0) for k in set(conf_loss) | set(conf_gain)})
    rows = []
    for pair, n in net.most_common():
        rows.append({"gold": pair[0], "pred": pair[1], "tag_errors": conf_tokens[pair], "head_loss": conf_loss[pair],
                     "head_gain": conf_gain.get(pair, 0), "net": n, "loss_per_error": round(conf_loss[pair] / max(1, conf_tokens[pair]), 2)})
    out = {"tokens": n_tok, "tag_errors": n_tag_err, "tag_agreement": round(1 - n_tag_err / n_tok, 4), "sentences_with_tag_error": n_sent_err,
           "head_flips_lost": n_flip_loss, "head_flips_gained": n_flip_gain, "net_head_loss": n_flip_loss - n_flip_gain,
           "net_uas_points": round(100 * (n_flip_loss - n_flip_gain) / n_tok, 2),
           "attribution_site": {"%s_%s" % k: v for k, v in where.items()},
           "loss_by_relation": dict(rel_loss.most_common()), "gain_by_relation": dict(rel_gain.most_common()),
           "confusions_by_net_loss": rows[:25], "examples": {"%s->%s" % k: v for k, v in list(examples.items())[:12]}}
    od = str(get_output_dir("diag_tag_to_head_loss_v1")); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print("tag agreement %.4f (%d errors / %d tokens); sentences with an error %d" % (out["tag_agreement"], n_tag_err, n_tok, n_sent_err))
    print("head flips: lost %d, gained %d, net %d = %.2f UAS points" % (n_flip_loss, n_flip_gain, out["net_head_loss"], out["net_uas_points"]))
    print("attribution:", out["attribution_site"])
    print("loss by relation:", dict(rel_loss.most_common(10)))
    print("%-6s %-6s %6s %6s %6s %5s %s" % ("gold", "pred", "tagerr", "loss", "gain", "net", "loss/err"))
    for r in rows[:15]:
        print("%-6s %-6s %6d %6d %6d %5d %.2f" % (r["gold"], r["pred"], r["tag_errors"], r["head_loss"], r["head_gain"], r["net"], r["loss_per_error"]))


if __name__ == "__main__":
    main()
