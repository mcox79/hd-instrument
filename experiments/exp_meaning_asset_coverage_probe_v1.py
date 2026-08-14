"""GROUND-TRUTH PROBE (read-only, no wiring): what is the LIVE meaning path of the C3
open-vocabulary grounding read-out, how big is the hand lexicon really, and what fraction of
the C3 read-out's own 5491 anchors is covered by each of the three "meaning assets" named as
the handoff's #1 open question (hdlab.lexical_similarity hand lexicon / the Lancaster+Brysbaert
grounding-norms island / the persisted 237.7M-token concept encoder)?

WHY THIS EXISTS. notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md 5.3 (MEH #1) and
10 Q1 assert that meaning in the live path is a ~380-word hand lexicon while a 39,707-word norms
island and a from-scratch concept encoder sit unused. That claim is the stated highest-value
move in the project. Before designing arms against it, this probe ESTABLISHES the premise by
counting on disk, per the exp_dev discipline that an absence/size claim requires an enumeration
rather than a recollection.

SCOPE: measurement only. This probe imports the live modules and counts; it wires nothing,
writes nothing outside its own output dir, and changes no default.

Run:  .venv/Scripts/python.exe experiments/exp_meaning_asset_coverage_probe_v1.py [--smoke]
"""
from __future__ import annotations

import os

# Thread pinning MUST precede numpy/torch import (PROT engineering rule).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

MIN_LEMMA_LEN = 3
MIN_LEMMA_COUNT = 3
SMOKE_SENT_LIMIT = 400


def _anchor_lemmas(smoke: bool) -> List[str]:
    """Rebuild the C3 cell's own anchor vocabulary: content lemmas of the definitional-grounding
    v5 corpus occurring >= MIN_LEMMA_COUNT times. Mirrors
    experiments/exp_grounding_readout_known_answer_v1.build_buckets' filter exactly (isalpha,
    len >= MIN_LEMMA_LEN, count >= MIN_LEMMA_COUNT) so the coverage denominator IS that cell's
    anchor set, not a lookalike."""
    from hdlab.reading_grounding_loop import content_lemmas
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5

    sents = [s for _seg, s in load_corpus_v5(None, lineaware=True)]
    if smoke:
        sents = sents[:SMOKE_SENT_LIMIT]
    counts: Counter = Counter()
    for s in sents:
        counts.update(sorted(set(l for l in content_lemmas(s)
                                 if l.isalpha() and len(l) >= MIN_LEMMA_LEN)))
    return sorted(w for w, c in counts.items() if c >= MIN_LEMMA_COUNT), len(sents)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    out_dir = os.path.join(_REPO, "data",
                           "exp_meaning_asset_coverage_probe_v1" + ("_smoke" if args.smoke else ""))
    os.makedirs(out_dir, exist_ok=True)

    rep: Dict[str, object] = {
        "anchor_name": "exp_meaning_asset_coverage_probe_v1",
        "run_mode": "smoke" if args.smoke else "full",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "scope": "MEASUREMENT_ONLY_NO_WIRING",
    }

    # ---------------------------------------------------------------- (1) the live meaning path
    import hdlab.reading_grounding_loop as rgl
    src = open(rgl.__file__, "r", encoding="utf-8", errors="replace").read()
    rep["live_path"] = {
        "c3_readout_imports_from_rgl": ["CTX_D", "GRADED_COMPARATOR", "ConceptSpace",
                                        "canonicalize_fast", "content_lemmas",
                                        "context_vector_masked", "normalize_lemma"],
        "rgl_imports_lexical_similarity": ("import hdlab.lexical_similarity" in src
                                           or "from hdlab.lexical_similarity" in src),
        "rgl_imports_grounded_similarity": ("import hdlab.grounded_similarity" in src
                                            or "from hdlab.grounded_similarity" in src),
        "rgl_imports_closed_class_lexicon": "from hdlab.closed_class_lexicon" in src,
        "ctx_d": int(rgl.CTX_D),
        "graded_comparator_default": bool(rgl.GRADED_COMPARATOR),
        "decision_variable": "cosine between context_vector_masked bags of nearby content-word "
                             "lemmas (hashed bipolar draws), compared in ConceptSpace",
    }

    # ---------------------------------------------------------------- (2) true asset sizes
    import hdlab.lexical_similarity as lx
    import hdlab.grounded_similarity as gs
    gcov = gs.coverage_stats()
    rep["asset_sizes"] = {
        "hand_lexicon_CONCEPT_FEATURES": len(lx.CONCEPT_FEATURES),
        "hand_lexicon_claimed_in_handoff": "~380",
        "grounded_norms_joined_vocab": int(gcov["n_words"]),
        "grounded_norms_claimed_in_handoff": 39707,
        "grounded_cap": float(gcov["grounded_cap"]),
        "grounded_n_dim": int(gcov["n_dim"]),
    }

    # ---------------------------------------------------------------- (3) anchors + coverage
    anchors, n_sents = _anchor_lemmas(args.smoke)
    rep["anchors"] = {"n_anchors": len(anchors), "n_corpus_sentences": n_sents,
                      "source": "definitional-grounding v5 corpus, C3 cell's own filter"}

    in_hand = [w for w in anchors if lx.in_lexicon(w)]
    in_norms = [w for w in anchors if gs.in_grounded_lexicon(w)]
    in_either = [w for w in anchors if lx.in_lexicon_or_grounded(w)]
    cov = {
        "hand_lexicon": {"n": len(in_hand), "frac": len(in_hand) / max(1, len(anchors))},
        "grounded_norms": {"n": len(in_norms), "frac": len(in_norms) / max(1, len(anchors))},
        "either_live_fallback_path": {"n": len(in_either),
                                      "frac": len(in_either) / max(1, len(anchors))},
    }

    # encoder: tokenizer-vocabulary coverage. The persisted encoder is consumed through its own
    # tokenizer; a word absent from that vocabulary has no encoder-native representation.
    enc_info: Dict[str, object] = {}
    try:
        from hdlab.encoder_retrain_persist import load_improved_encoder
        ext = load_improved_encoder(seed=7)
        vocab = ext.tok.get_vocab()
        vset = set(v.lower() for v in vocab.keys())
        whole = [w for w in anchors if w in vset]
        enc_info = {
            "loads": True,
            "class": type(ext).__name__,
            "d_model": int(ext.d),
            "tokenizer_vocab_size": len(vocab),
            "cues": dict(getattr(ext, "CUES", {})),
            "anchors_in_tokenizer_vocab": {"n": len(whole),
                                           "frac": len(whole) / max(1, len(anchors))},
            "has_word_embedding_api": bool(hasattr(ext, "embed") or hasattr(ext, "word_vector")),
            "public_api": sorted(a for a in dir(ext) if not a.startswith("_")),
        }
    except Exception as exc:  # loud, never silent
        enc_info = {"loads": False, "error": "%s: %s" % (type(exc).__name__, exc)}
    cov["encoder_tokenizer"] = enc_info
    rep["coverage_of_c3_anchors"] = cov

    rep["elapsed_s"] = round(time.time() - t0, 2)

    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(rep, fh, indent=2, sort_keys=False)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(json.dumps(rep, indent=2)[:4000], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
