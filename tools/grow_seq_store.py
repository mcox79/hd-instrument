"""tools/grow_seq_store.py -- GROW the parser-free SEQ identity channel by READING and PERSIST it.

The pri-5 landing (2026-09-11) made the reading-grounding loop rank over grounded-distinctive (+) SEQ (+) referent.
The SEQ channel is KNOWLEDGE GROWN BY READING (direction+distance-typed co-occurrence, accrued online -- Hebb; read
as rectified PMI -- Levy-Goldberg); measured: its increment over grounded on the loop's coverage-quality frontier
rises with exposure (+0.16 @250k -> +0.22 @500k -> +0.26 @1M modern Simple-Wikipedia lines, CI-sep, twin losing).
A fresh loop reads only its curriculum (~thousands of sentences), where SEQ is under-read. This tool reads modern
Simple-Wikipedia through the loop's OWN ingest operation (`content_words` -> `normalize_lemma` ->
`directional_context_lemmas` -> `ConceptSpace.observe_context_counts`; byte-identical to `process_sentence`'s
all-content path, witness A6 of the solver + test_fused_sense_ranker_live) and persists the grown store as the
ROUTE-B sidecar `data/foundation/seq_store_v1/concept_space_ctx_counts.npz`, which consumers MERGE into a live
loop (`foundation_persistence.load_ctx_counts_into`). The coverage-quality board arm loads it when present.

VOCABULARY (gold-blind, principled): the loop's base seed vocabulary (its anchors) plus every single-token word the
grounded ATL norms cover (the words the fused read can ever ground) -- NOT a benchmark's word list. Features
(typed neighbours) are unrestricted. Singleton features (seen once) are pruned at SAVE time only for memory
(cross-episode confirmation; W20 measured the confirmation gate as a tie with raw, never a loss).

Run (cap cores):  .venv/Scripts/python.exe tools/grow_seq_store.py --lines 250000 [--out data/foundation/seq_store_v1]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import argparse
import json
import sys
import time
from collections import Counter

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.reading_grounding_loop import (ConceptSpace, CTX_D, content_words, normalize_lemma,
                                          directional_context_lemmas)
from hdlab.foundation_persistence import save_concept_space, _ctx_sidecar_path

SIMPLEWIKI = os.path.join(_REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
OUT_DEFAULT = os.path.join(_REPO, "data", "foundation", "seq_store_v1")


def _vocab():
    import experiments.exp_reading_grounding_loop_cycle1_v1 as H
    from hdlab.grounded_similarity import _table
    v = set(normalize_lemma(w) for w in H.load_base_vocab_seed())
    v |= set(_table().keys())
    return v


def grow(lines: int, out_dir: str, vocab=None, prune_singletons: bool = True, log_every: int = 50000) -> dict:
    t0 = time.time()
    vocab = _vocab() if vocab is None else set(vocab)
    space = ConceptSpace(d=CTX_D)
    space.track_all_content_lemmas = True
    space.track_directional_context_counts = True
    n_read = 0
    with open(SIMPLEWIKI, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            if n_read >= lines:
                break
            n_read += 1
            sent = ln.strip()
            if not sent:
                continue
            multiset = [normalize_lemma(w) for w in content_words(sent)]
            for tgt in set(multiset):
                if tgt in vocab:
                    space.observe_context_counts(tgt, directional_context_lemmas(multiset, tgt))
            if n_read % log_every == 0:
                print("[grow] %d lines, %d lemmas, %d tokens, %.0fs" % (
                    n_read, len(space._ctx_counts), space._ctx_total, time.time() - t0), flush=True)
    n_pruned = 0
    if prune_singletons:
        for lem, ctr in list(space._ctx_counts.items()):
            kept = Counter({f: n for f, n in ctr.items() if n >= 2})
            n_pruned += len(ctr) - len(kept)
            if kept:
                space._ctx_counts[lem] = kept
            else:
                del space._ctx_counts[lem]
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "concept_space.npz")
    save_concept_space(space, path)
    manifest = {"source": os.path.relpath(SIMPLEWIKI, _REPO), "lines_read": n_read,
                "n_lemmas": len(space._ctx_counts), "ctx_total": int(space._ctx_total),
                "n_singleton_features_pruned": n_pruned, "vocab_size": len(vocab),
                "sidecar": os.path.relpath(_ctx_sidecar_path(path), _REPO),
                "ingest": "content_words -> normalize_lemma -> directional_context_lemmas -> observe_context_counts "
                          "(byte-identical to process_sentence's all-content directional path)",
                "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="ascii") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps(manifest, indent=1))
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=250000)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--keep-singletons", action="store_true")
    a = ap.parse_args(argv)
    grow(a.lines, a.out, prune_singletons=not a.keep_singletons)


if __name__ == "__main__":
    main()
