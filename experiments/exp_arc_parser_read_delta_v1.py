"""End-to-end: how much a byte-identical parser speedup cuts a WARM SituationReader.read().

Problem: optimize_the_arc_parser_inner_loop_the_dominant_read_cost.

The parser is ~73% of a warm read, so a 3.5x parser speedup should cut the whole read materially
AND leave the reader's outputs byte-identical (same parses -> same events/roles/coref). This cell:
  1. times a warm stock read of a real LitBank doc (median of reps),
  2. monkeypatches ArcParser.parse to the fast v3 implementation (byte-identical),
  3. times the warm fast read,
  4. asserts the two reads produce an IDENTICAL SituationModel summary.

Writes only to its own dir. NO LLM. Deterministic. ASCII-only.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import time
import json

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, ParseResult
from hdlab.situation_reader import SituationReader
from experiments.exp_arc_parser_fastfeat_v1 import FeatCache
from experiments.exp_arc_parser_fastfeat_v3 import sentence_scores
from experiments.exp_arc_parser_fastfeat_v2 import decode_from_scores

_OUT = os.path.join(_REPO, "data/exp_arc_parser_read_delta_v1")
_DOC = os.path.join(_REPO, "data/litbank/coref_conll/1023_bleak_house_brat.conll")

_orig_parse = ArcParser.parse


def _fast_parse(self, tokens, pos_tags):
    if len(tokens) != len(pos_tags):
        raise ValueError("len mismatch")
    C = getattr(self, "_C", None)
    if C is None:
        C = self._C = FeatCache()
    sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
    Sc = sentence_scores(sent, self.avg, C)
    head, margin = decode_from_scores(Sc, len(sent))
    arcs = [(head[i], i) for i in range(1, len(sent) + 1)]
    return ParseResult(arcs=arcs, margins=margin, heads=head)


def _summ(sm):
    """A deterministic, parse-sensitive summary of the read (for output-identity)."""
    d = {}
    d["n_sentences"] = getattr(sm, "n_sentences", None)
    d["n_entities"] = len(getattr(sm, "entities", []) or [])
    d["n_targets"] = getattr(sm, "n_targets", None)
    d["coref_acc"] = getattr(sm, "coref_acc", None)
    evs = getattr(sm, "events", []) or []
    d["n_events"] = len(evs)
    # event fingerprints (predicate + sorted role fillers) -- highly parse-sensitive
    fp = []
    for e in evs:
        rf = getattr(e, "role_fillers", None) or getattr(e, "roles", None) or {}
        try:
            items = sorted((str(k), str(v)) for k, v in dict(rf).items())
        except Exception:
            items = []
        fp.append((str(getattr(e, "lemma", getattr(e, "predicate", ""))), tuple(items)))
    d["event_fp"] = sorted(fp)
    d["n_causal"] = len(getattr(sm, "causal_links", []) or [])
    d["n_timeline"] = len(getattr(sm, "timeline_frames", []) or [])
    return d


def _read(flags):
    return SituationReader(**flags).read(_DOC)


def time_read(flags, reps):
    _read(flags)  # warm caches (frontend load, etc.)
    xs = []
    sm = None
    for _ in range(reps):
        t0 = time.perf_counter()
        sm = _read(flags)
        xs.append(time.perf_counter() - t0)
    xs.sort()
    return xs[len(xs) // 2], sm


def main(reps=3, flags=None):
    os.makedirs(_OUT, exist_ok=True)
    flags = flags or {}

    # STOCK
    ArcParser.parse = _orig_parse
    t_stock, sm_stock = time_read(flags, reps)
    s_stock = _summ(sm_stock)
    print("STOCK read : %.3fs" % t_stock, flush=True)

    # FAST (patched, byte-identical)
    ArcParser.parse = _fast_parse
    t_fast, sm_fast = time_read(flags, reps)
    s_fast = _summ(sm_fast)
    print("FAST  read : %.3fs" % t_fast, flush=True)
    ArcParser.parse = _orig_parse  # restore

    identical = (s_stock == s_fast)
    print("READ SPEEDUP: %.2fx  (read cost cut %.0f%%)" % (t_stock / t_fast, 100 * (1 - t_fast / t_stock)), flush=True)
    print("READ OUTPUT identical: %s" % identical, flush=True)
    if not identical:
        for k in s_stock:
            if s_stock[k] != s_fast[k]:
                print("  DIFF %s: stock=%r fast=%r" % (k, s_stock.get(k), s_fast.get(k)), flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"reps": reps, "flags": flags, "stock_read_s": t_stock, "fast_read_s": t_fast,
                   "read_speedup": t_stock / t_fast, "output_identical": identical,
                   "summary_stock_keys": {k: s_stock[k] for k in s_stock if k != "event_fp"}}, f, indent=2)
    print("wrote", os.path.join(_OUT, "metrics.json"), flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        ArcParser.parse = _orig_parse
        _, sm = time_read({}, 1)
        s1 = _summ(sm)
        ArcParser.parse = _fast_parse
        _, sm2 = time_read({}, 1)
        s2 = _summ(sm2)
        ArcParser.parse = _orig_parse
        assert s1 == s2, "read output diverged under fast parser"
        print("SELF-TEST PASS: fast read output identical to stock")
    else:
        main(a.reps)
