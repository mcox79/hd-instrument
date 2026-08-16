"""exp_meaning_asset_handlexicon_scorability_v1 -- can the HAND-AUTHORED concept lexicon be
scored on the encoding-quality instrument at all?

`hdlab/lexical_similarity.py` carries CONCEPT_FEATURES, a hand-authored DOM/ROLE feature lexicon,
and is the live path's concept-similarity organ. It is a MEANING asset (human-authored features),
so it belongs in the enumeration. This cell answers the SCORABILITY question honestly instead of
producing a number the item count cannot support: it measures coverage, and only then reports.

THE RULE BEING OBEYED: if an asset cannot be scored, say why, do not adjust the ruler. A rho on a
handful of pairs is exactly the underpowered readout the v1 instrument's own smoke gate refused to
certify (26 SimLex pairs, Spearman SE ~0.20).

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "meaning_asset_handlexicon_scorability_v1"
MIN_PAIRS_TO_SCORE = 100      # pre-declared: below this the readout is not reported as a result


def main() -> int:
    from hdlab import lexical_similarity as LS
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = INS.load_simlex(INS.SIMLEX)
    cf = LS.CONCEPT_FEATURES

    n_concepts = len(cf)
    in_vocab = [w for w in words if w in cf]
    both_all = [(a, b, s) for a, b, s in pairs if a in cf and b in cf]
    both_vocab = [(a, b, s) for a, b, s in pairs if a in w2i and b in w2i and a in cf and b in cf]

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": "full",
        "asset": {"module": "hdlab/lexical_similarity.py", "symbol": "CONCEPT_FEATURES",
                  "kind": "hand-authored DOM/ROLE feature lexicon (not learned, not distributional)",
                  "n_concepts": n_concepts},
        "coverage": {
            "instrument_vocabulary_size": len(words),
            "instrument_words_covered": len(in_vocab),
            "instrument_coverage_fraction": round(len(in_vocab) / float(len(words)), 4),
            "simlex_pairs_covered_by_the_instrument": 322,
            "simlex_pairs_both_words_in_lexicon_whole_simlex": len(both_all),
            "simlex_pairs_both_words_in_lexicon_AND_in_instrument_vocab": len(both_vocab),
        },
        "min_pairs_to_score_predeclared": MIN_PAIRS_TO_SCORE,
    }

    if len(both_vocab) < MIN_PAIRS_TO_SCORE:
        out["verdict"] = "NOT_SCORABLE_ON_THE_SEMANTIC_GOLD"
        out["verdict_msg"] = (
            "The hand lexicon covers %d of the instrument's %d vocabulary words (%.1f%%) and only "
            "%d SimLex pairs have BOTH words in it, against a pre-declared floor of %d. At that n "
            "the readout cannot separate any arm from any other, so NO rho is reported. This is a "
            "coverage fact about the asset, not a failure of the asset: the instrument's "
            "vocabulary is the 4,096 most frequent corpus surface forms and the lexicon is a "
            "hand-built inventory of ~%d concepts. Scoring it would require either a different "
            "item population (a decomposition, not a like-for-like arm) or extending the lexicon "
            "(construction, not measurement)."
            % (len(in_vocab), len(words), 100.0 * len(in_vocab) / len(words), len(both_vocab),
               MIN_PAIRS_TO_SCORE, n_concepts))
        out["what_would_make_it_scorable"] = (
            "a semantic gold whose pairs are drawn FROM the lexicon's own inventory, scored "
            "against floors on that same population -- a different, legitimate cell, not this one")
    else:
        # only reached if coverage ever improves; kept so the cell is not a dead end
        X = np.zeros((len(words), 8192), dtype=np.float32)
        cov = np.zeros(len(words), dtype=bool)
        for i, w in enumerate(words):
            v = LS.concept_vector(w) if hasattr(LS, "concept_vector") else None
            if v is not None:
                cov[i] = True
                a = np.asarray(v)
                X[i, :len(a)] = np.real(a) if np.iscomplexobj(a) else a
        cs, gs, _ = FT.simlex_perpair(INS._l2n(X), w2i, both_vocab)
        out["verdict"] = "SCORED"
        out["simlex_rho"] = FT.boot_rho(cs, gs)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(out_dir, out)
    print(json.dumps({k: out[k] for k in ("verdict", "coverage")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
