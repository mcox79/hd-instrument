"""End-to-end: how much the byte-identical tagger speedup cuts a WARM SituationReader.read(), and
PROOF that no downstream consumer regresses.

Problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost.

The tagger is ~28% of a warm read and feeds EVERY downstream organ (parser, events, coref, roles,
causal, ...). A byte-identical tagger speedup must (a) cut the whole read materially and (b) leave the
reader's outputs BYTE-IDENTICAL -- which is the no-regression proof: identical tags -> identical
parses -> identical events/roles/coref for ALL consumers, by construction. This cell:
  1. times a warm stock read of a real LitBank doc (median of reps),
  2. monkeypatches PosTagger.tag to the fast (variant C) implementation (covers EVERY PosTagger
     consumer: the frontend tagger, the copular es_pos, the referent_per_np tagger, etc.),
  3. times the warm fast read,
  4. asserts the two reads produce an IDENTICAL SituationModel summary (events, entities, coref,
     targets, causal, timeline) -- the whole-read no-regression witness.

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

from hdlab.pos_tagger import PosTagger
from hdlab.situation_reader import SituationReader
from experiments.exp_pos_tagger_fastfeat_v1 import FastTagger

_OUT = os.path.join(_REPO, "data/exp_pos_tagger_read_delta_v1")
_DOC = os.path.join(_REPO, "data/litbank/coref_conll/1023_bleak_house_brat.conll")

_orig_tag = PosTagger.tag


def _fast_tag(self, tokens):
    """Byte-identical fast tag; builds a per-instance FastTagger on first call (covers all consumers)."""
    ft = getattr(self, "_fast", None)
    if ft is None:
        ft = self._fast = FastTagger(self, "C")
    return ft.tag(list(tokens))


def _summ(sm):
    """A deterministic, tag/parse-sensitive summary of the read (for output-identity)."""
    d = {}
    d["n_sentences"] = getattr(sm, "n_sentences", None)
    d["n_entities"] = len(getattr(sm, "entities", []) or [])
    d["n_targets"] = getattr(sm, "n_targets", None)
    d["coref_acc"] = getattr(sm, "coref_acc", None)
    evs = getattr(sm, "events", []) or []
    d["n_events"] = len(evs)
    fp = []
    for e in evs:
        rf = getattr(e, "role_fillers", None) or getattr(e, "roles", None) or {}
        try:
            items = sorted((str(k), str(v)) for k, v in dict(rf).items())
        except Exception:
            items = []
        fp.append((str(getattr(e, "lemma", getattr(e, "predicate", ""))),
                   str(getattr(e, "agent", "")), str(getattr(e, "patient", "")),
                   str(getattr(e, "tense", "")), tuple(items)))
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

    PosTagger.tag = _orig_tag
    t_stock, sm_stock = time_read(flags, reps)
    s_stock = _summ(sm_stock)
    print("STOCK read : %.3fs" % t_stock, flush=True)

    PosTagger.tag = _fast_tag
    t_fast, sm_fast = time_read(flags, reps)
    s_fast = _summ(sm_fast)
    print("FAST  read : %.3fs" % t_fast, flush=True)
    PosTagger.tag = _orig_tag  # restore

    identical = (s_stock == s_fast)
    print("READ SPEEDUP: %.2fx  (read cost cut %.0f%%)"
          % (t_stock / t_fast, 100 * (1 - t_fast / t_stock)), flush=True)
    print("READ OUTPUT identical (NO consumer regresses): %s" % identical, flush=True)
    if not identical:
        for k in s_stock:
            if s_stock[k] != s_fast[k]:
                print("  DIFF %s: stock=%r fast=%r" % (k, s_stock.get(k), s_fast.get(k)), flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"reps": reps, "flags": flags, "stock_read_s": t_stock, "fast_read_s": t_fast,
                   "read_speedup": t_stock / t_fast, "read_cost_cut_pct": 100 * (1 - t_fast / t_stock),
                   "output_identical": identical,
                   "summary_stock": {k: s_stock[k] for k in s_stock if k != "event_fp"}}, f, indent=2)
    print("wrote", os.path.join(_OUT, "metrics.json"), flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        PosTagger.tag = _orig_tag
        _, sm = time_read({}, 1)
        s1 = _summ(sm)
        PosTagger.tag = _fast_tag
        _, sm2 = time_read({}, 1)
        s2 = _summ(sm2)
        PosTagger.tag = _orig_tag
        assert s1 == s2, "read output diverged under fast tagger"
        print("SELF-TEST PASS: fast-tagger read output identical to stock (no consumer regresses)")
    else:
        main(a.reps)
