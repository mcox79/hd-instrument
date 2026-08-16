"""exp_meaning_asset_norms_coverage_gap_v1 -- how wide the grounded norms actually reach, and how
much wider a norm set would have to be to matter.

WHY THIS IS THE ACTIONABLE CELL. The grounded sensorimotor norms are the ONLY meaning asset whose
SimLex signal survives leaving the corpus's frequent vocabulary (0.2701 on the frequent 322 pairs,
0.2289 [+0.1517,+0.3014] on the disjoint rarer 677, drop NOT_SEPARATED), while every learned
encoder collapses CI-separated. That makes "widen the norms" a concrete build rather than a hope.
A build needs a target, and a target needs the coverage gap measured rather than guessed.

TWO COVERAGE NUMBERS, AND THEY ANSWER DIFFERENT QUESTIONS.
  TYPE coverage  -- what fraction of the DISTINCT words we could meet have norms. This is the
                    honest breadth number and it is the low one.
  TOKEN coverage -- what fraction of word OCCURRENCES in running text have norms. This is what
                    determines how often the asset can say anything while actually reading, and
                    it is much higher, because the words we meet most often are the ones covered.
Reporting only one of them misleads in one direction or the other, so both are reported, banded by
frequency rank, and neither is averaged with the other.

THE BUILD TARGET is then stated the only way that is meaningful: how many ADDITIONAL words, taken
in frequency order, a norm set would need in order to reach stated token-coverage marks.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import re
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "meaning_asset_norms_coverage_gap_v1"
BANDS = [(0, 1000), (1000, 4096), (4096, 16384), (16384, 65536), (65536, 10 ** 9)]
TOKEN_MARKS = (0.90, 0.95, 0.98, 0.99)


def main() -> int:
    t0 = time.time()
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    norm_words = set(tab)

    # the SAME tokenisation the instrument uses, over the SAME corpus and byte budget
    with open(INS.CORPUS, "rb") as f:
        raw = f.read(INS.CORPUS_BYTES)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    text = raw.decode("utf-8", errors="ignore").lower()
    counts = {}
    for tok in re.findall(r"[a-z]+", text):
        if len(tok) >= INS.MIN_LEN:
            counts[tok] = counts.get(tok, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ranked = ordered[INS.TOP_DROP:]
    words = [w for w, _ in ranked]
    cnt = np.array([c for _, c in ranked], dtype=np.float64)
    covered = np.array([w in norm_words for w in words])

    # ---- self-test: reproduce the instrument's own vocabulary and the landed miss count
    inst_words = words[:INS.V]
    ref, _ = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    assert inst_words == list(ref), "recomputed vocabulary differs from the instrument's"
    landed = json.loads((REPO / "data/exp_meaning_asset_fair_test_v1/metrics.json").read_text())
    miss_inst = int((~covered[:INS.V]).sum())
    assert miss_inst == landed["norms_missing_in_vocab"], (
        f"instrument-vocab miss {miss_inst} != landed {landed['norms_missing_in_vocab']}")
    assert len(norm_words) == 36810, f"norm table is {len(norm_words)} words, expected 36810"
    print(f"[selftest] OK  {len(words)} corpus types, norms {len(norm_words)}, "
          f"instrument-vocab miss {miss_inst}", flush=True)
    if "--self-test" in sys.argv:
        print("SELFTEST_ONLY_OK")
        return 0

    tot_tok = float(cnt.sum())
    bands = {}
    for lo, hi in BANDS:
        sl = slice(lo, min(hi, len(words)))
        c, k = covered[sl], cnt[sl]
        if len(k) == 0:
            continue
        bands[f"rank_{lo}_{min(hi, len(words))}"] = {
            "n_types": int(len(k)),
            "types_covered": int(c.sum()),
            "type_coverage": round(float(c.mean()), 4),
            "token_coverage_within_band": round(float(k[c].sum() / max(k.sum(), 1)), 4),
            "share_of_all_tokens": round(float(k.sum() / tot_tok), 4),
        }

    # how many words, in frequency order, to reach each token-coverage mark IF all were covered
    cum = np.cumsum(cnt) / tot_tok
    need = {}
    for m in TOKEN_MARKS:
        idx = int(np.searchsorted(cum, m)) + 1
        already = int(covered[:idx].sum())
        need[f"token_coverage_{int(m*100)}pct"] = {
            "words_needed_in_frequency_order": idx,
            "of_those_already_in_the_norms": already,
            "ADDITIONAL_WORDS_TO_NORM": idx - already,
        }

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": "full",
        "why": ("the norms are the only asset whose meaning signal survives leaving the frequent "
                "vocabulary, so widening them is the concrete next build; this cell sizes it"),
        "norm_table": {"words": len(norm_words),
                       "source": "hdlab/grounded_similarity.py _table(): Lancaster sensorimotor "
                                 "JOIN Brysbaert concreteness, lower-cased, single-token, z-scored",
                       "NOT_39707": "39,707 is the Lancaster CSV filename, not the usable asset"},
        "corpus": {"path": str(INS.CORPUS).replace("\\", "/"), "bytes": INS.CORPUS_BYTES,
                   "distinct_types": len(words), "total_tokens": int(tot_tok),
                   "tokenisation": "the instrument's own: [a-z]+ lower-cased, min length "
                                   f"{INS.MIN_LEN}, top {INS.TOP_DROP} dropped"},
        "HEADLINE_COVERAGE": {
            "instrument_vocab_4096_types_covered": int(covered[:INS.V].sum()),
            "instrument_vocab_type_coverage": round(float(covered[:INS.V].mean()), 4),
            "whole_corpus_type_coverage": round(float(covered.mean()), 4),
            "whole_corpus_TOKEN_coverage": round(float(cnt[covered].sum() / tot_tok), 4),
            "simlex999_pair_coverage": 1.0,
            "reading_rule": ("type coverage is the breadth number and is LOW; token coverage is "
                             "what determines how often the asset speaks while reading and is "
                             "HIGH. Both are real; neither alone is the answer."),
        },
        "coverage_by_frequency_band": bands,
        "BUILD_TARGET_how_many_more_words_to_norm": need,
        "what_would_make_the_widening_worth_it": (
            "the widened set must hold the SAME signal on the words it adds. The rarer-677 result "
            "(0.2289 [+0.1517,+0.3014]) is evidence the norms do NOT degrade off the frequent "
            "vocabulary, but it is evidence about words that ALREADY have norms. A widened set "
            "must be re-scored on ITS OWN new words against the same floors before any of this "
            "coverage arithmetic converts into capability."),
    }
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["verdict"] = "COVERAGE_GAP_SIZED"
    out["summary"] = (f"norms cover {out['HEADLINE_COVERAGE']['whole_corpus_type_coverage']:.1%} of "
                      f"corpus types but {out['HEADLINE_COVERAGE']['whole_corpus_TOKEN_coverage']:.1%} "
                      f"of tokens; {need['token_coverage_95pct']['ADDITIONAL_WORDS_TO_NORM']} more "
                      f"words would reach 95% token coverage")
    write_metrics(out_dir, out)
    print(json.dumps(out["HEADLINE_COVERAGE"], indent=1))
    print(json.dumps(bands, indent=1))
    print(json.dumps(need, indent=1))
    print("VERDICT:", out["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
