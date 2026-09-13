"""The CATEGORY organ's READING-ACQUISITION arm: accrue hdlab.lexical_categories counts (lexical + suffix + transition) over the
classes the READING-INDUCED inventory assigns (exp_reading_induced_categories_v1 asset: word type -> cluster, clusters NAMED by their
majority UPOS so consumers keep their convention), on raw simplewiki lines -- no tagged corpus anywhere in the loop.

WHY (overnight plan 1b, 2026-09-13): the live category organ's counts come from UD-EWT's tag column (offline labelled supply). The
brain's acquisition is distributional; the induced inventory IS that, but it is type-level (one class per word, unknown words
uncovered). Running the same count-based generative model over the induced labels adds what it lacks: SEQUENCE prediction
(transition counts), the morpho-orthographic cue for unknown words (suffix counts), and a token-level POSTERIOR. The result is a
category organ whose knowledge is grown from reading alone. Measured against the supervised-supply counts on UD-EWT test (agreement
with gold UPOS) and through the heads rung (tools/build_attachment_validities.py --categories hand-off).
Usage: python tools/build_lexical_categories_from_reading.py --lines 200000 [--skip 0] [--out data/frontend_assets/lexical_categories_counts_reading_v1.json]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse
import json
import re
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

CORPUS = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
INDUCED = os.path.join(REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json")
OUT = os.path.join(REPO, "data", "frontend_assets", "lexical_categories_counts_reading_v1.json")
_TOK = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+(?:[.,][0-9]+)*|[^\sA-Za-z0-9]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=200000); ap.add_argument("--skip", type=int, default=0)
    ap.add_argument("--induced", default=INDUCED); ap.add_argument("--out", default=OUT)
    ap.add_argument("--maxlen", type=int, default=40)
    a = ap.parse_args(argv)
    t0 = time.time()
    import hdlab.lexical_categories as LC
    with open(a.induced, encoding="utf-8") as f:
        d = json.load(f)
    w2c = d["word2cat"]; names = d.get("cluster_to_upos_name", {})
    def cat(tok):
        c = w2c.get(tok.lower())
        if c is None:
            if re.fullmatch(r"[^\w\s]+", tok):
                return "PUNCT"
            if re.fullmatch(r"[\d.,:/-]+", tok):
                return "NUM"
            return None                                     # unknown to the induced inventory: not a label source
        n = names.get(str(c), names.get(c))
        return n if isinstance(n, str) and n else None
    m = LC.LexicalCategories(); seen = used = toks_acc = 0; batch = []
    with open(CORPUS, encoding="utf-8") as f:
        for li, line in enumerate(f):
            if li < a.skip:
                continue
            if seen >= a.lines:
                break
            seen += 1
            toks = _TOK.findall(line.strip())
            if not (3 <= len(toks) <= a.maxlen):
                continue
            labels = [cat(t) for t in toks]
            if any(l is None for l in labels):              # only fully-covered sentences feed the TRANSITION counts honestly
                continue
            batch.append(list(zip(toks, labels))); used += 1; toks_acc += len(toks)
            if len(batch) >= 5000:
                m.accrue(batch); batch = []
    if batch:
        m.accrue(batch)
    m.finalize(); p = m.save(a.out)
    rep = {"lines_seen": seen, "sentences_used": used, "tokens": toks_acc, "n_categories": len(m.tags), "vocab": len(m.vocab),
           "asset": os.path.relpath(p, REPO), "elapsed_s": round(time.time() - t0, 1), "inventory": os.path.relpath(a.induced, REPO)}
    print(json.dumps(rep, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
