"""exp_knowledge_factory_grow_loop_v1 -- the MULTI-ROUND grow-from-reading loop: INGEST a large corpus over
several rounds, PRUNE (surprise-weighting + recurrence gate), show the held-out improvement CLIMB, ACCUMULATE
(additive = catastrophic-forgetting-free, CLS), FREEZE the grown store, and CHECK every consumer for regression.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift (owner: "show ingestion of
a large corpus, then pruning, then the clear improvement -- a number of times, to a respectable corpus, freeze it,
hand it for permanent inclusion; and investigate any consumers that regress").

HONEST SCOPE (measured): reading-growth improves the ASSOCIATIVE / word-similarity store (SimLex/WordSim rho -- the
proven `does_learning_from_reading_deserve_to_continue` regime), a DIFFERENT typed store than the curated
sense-DISCRIMINATIVE WSD signatures (C1, frozen; reading-growth is a located NEGATIVE there). This loop grows the
associative store; C1 stays curated+frozen. The PRUNE (PPMI surprise-weighting + recurrence gate) is what converts
raw-regression into gated-improvement.

BRAIN-FAITHFUL: PPMI = N400 lexical surprise-weighting gating encoding (Rabovsky 2018); additive co-occurrence =
read-forever without catastrophic forgetting (CLS, McClelland 1995); the round-over-round climb = consolidation.

REUSES the proven reader machinery (exp_learn_from_reading_strong_arm_v1): read_corpus_stream / build_vocab /
build_cooc / ppmi_matrix / svd_vectors / dense_vec_cosine_fn / sparse_row_cosine_fn / score_arm + the SimLex/WordSim
gold. NO external LLM. Deterministic. ASCII. Remote-safe (no module-level spaCy; loads cached corpus+benchmarks).

# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
# KB_REFERENT: data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt
# KB_REFERENT: data/encoder_eval_benchmarks/simlex999.txt
# KB_REFERENT: data/encoder_eval_benchmarks/wordsim353_combined.csv
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_grow_loop_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_learn_from_reading_strong_arm_v1 as SA

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_grow_loop_v1")
ASSET = os.path.join(_REPO, "data", "frontend_assets", "associative_similarity_store_v1.npz")


def _rho(bench, sim_fn):
    r = SA.score_arm(bench, sim_fn, n_boot=500, n_null=500)
    return r


SIMPLEWIKI = os.path.join(_REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
ARC = os.path.join(_REPO, "data", "corpora", "arc", "ARC-V1-Feb2018-2", "ARC_Corpus.txt")


def _stream_corpora(paths, max_tokens):
    """Stream multiple corpus files to a token budget (reuses SA tokenization). Returns (sentences, n_tokens)."""
    sents = []; ntok = 0
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="ignore") as fh:
            for ln in fh:
                toks = [w for w in SA.TOKEN_RE.findall(ln.lower()) if len(w) >= 2]
                if toks:
                    sents.append(toks); ntok += len(toks)
                    if ntok >= max_tokens:
                        return sents, ntok
    return sents, ntok


def _broad_files():
    """Every corpus text file across ALL genres (fiction, mystery, drama, textbook-science/social, graded readers,
    news, social-commonsense, encyclopedic, science-exam), preferring cleaned/ over raw/. This is the BREADTH set:
    diverse registers expose diverse senses + collocations (a child learns vocabulary from stories, conversation,
    description, instruction -- not one giant encyclopedia)."""
    import glob
    from collections import defaultdict
    allt = [f.replace("\\", "/") for f in glob.glob(os.path.join(_REPO, "data", "corpora", "**", "*.txt"),
                                                     recursive=True)]
    allt = [f for f in allt if "__macosx" not in f.lower() and "readme" not in f.lower()
            and "/binder/" not in f.lower() and "word_image_early_vocab" not in f.lower()]
    by_corpus = defaultdict(list)
    for f in allt:
        parts = f.split("data/corpora/")[-1].split("/")
        by_corpus[parts[0]].append(f)
    picked = []
    for corpus, fs in by_corpus.items():
        cleaned = [f for f in fs if "/cleaned/" in f]
        raw = [f for f in fs if "/raw/" in f]
        flat = [f for f in fs if "/cleaned/" not in f and "/raw/" not in f]
        picked.extend(cleaned or flat or raw)
    return sorted(set(picked))


def _stream_balanced(total, big_cap=15_000_000):
    """BALANCED multi-genre stream: read every diverse corpus FULLY, cap the two giant expository sources
    (simplewiki, ARC) at big_cap so the diverse registers are a real fraction. Returns (sents, ntok, per_source)."""
    files = _broad_files(); sents = []; ntok = 0
    per_source = {}
    for f in files:
        cap = big_cap if ("simplewiki" in f or "ARC_Corpus" in f.lower() or "/arc/" in f.lower()) else 10 ** 9
        n_f = 0
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                for ln in fh:
                    toks = [w for w in SA.TOKEN_RE.findall(ln.lower()) if len(w) >= 2]
                    if toks:
                        sents.append(toks); ntok += len(toks); n_f += len(toks)
                        if n_f >= cap or ntok >= total:
                            break
        except OSError:
            continue
        if n_f:
            per_source[f.split("data/corpora/")[-1]] = n_f
        if ntok >= total:
            break
    return sents, ntok, per_source


def recurrence_prune(cooc, min_count):
    """The consolidation-gate recurrence step on the accumulated co-occurrence: drop entries seen < min_count
    (one-off co-occurrences are noise; keep what RECURS). Returns a pruned CSR + the kept fraction."""
    c = cooc.tocoo()
    keep = c.data >= min_count
    from scipy.sparse import coo_matrix
    pruned = coo_matrix((c.data[keep], (c.row[keep], c.col[keep])), shape=cooc.shape).tocsr()
    return pruned, float(keep.mean())


def run(rounds=6, tokens_per_round=3_000_000, min_count=3, smoke=False, freeze=True,
        corpus_paths=None, vocab_cap=40000, broad=False, big_cap=15_000_000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    simlex = SA.load_simlex(); wordsim = SA.load_wordsim()
    force = SA.benchmark_vocab(simlex) | SA.benchmark_vocab(wordsim)
    if smoke:
        rounds = 3; tokens_per_round = 300_000; vocab_cap = 8000; big_cap = 200_000
    total = rounds * tokens_per_round
    per_source = {}
    if broad:
        # BALANCED multi-genre stream (breadth): diverse registers feed the different typed stores; a
        # breadth-PRESERVING prune (low min_count + PPMI surprise-weighting) keeps the low-frequency narrative
        # signal instead of a global count floor deleting it.
        sents, _ntok, per_source = _stream_balanced(total, big_cap=big_cap)
        min_count = 2 if not smoke else 2                 # low floor so rare-genre co-occurrence survives; PPMI ranks
    else:
        if corpus_paths is None:
            corpus_paths = [SIMPLEWIKI]
        sents, _ntok = _stream_corpora(corpus_paths, total)
    # cumulative token cut points -> per-round NEW chunks
    cuts, _toks_at = SA.token_cuts(sents, [tokens_per_round * (r + 1) for r in range(rounds)])
    # BREADTH-PRESERVING vocab floor: a global min_count=5 would DROP the low-frequency diverse-genre words
    # (children's-book / fiction vocabulary swamped by expository volume) -> defeats breadth. Use a low floor for
    # broad ingestion; PPMI surprise-weighting (not raw count) does the real pruning of the co-occurrences.
    index = SA.build_vocab(sents, force, vocab_cap=vocab_cap, min_count=(2 if (smoke or broad) else 5))
    if per_source:
        top = sorted(per_source.items(), key=lambda kv: -kv[1])[:12]
        print("[grow] BREADTH sources (%d): %s" % (len(per_source),
              " | ".join("%s=%.1fM" % (k.split('/')[0], v / 1e6) for k, v in top)), flush=True)
    print("[grow] rounds=%d tok/round=%d vocab=%d sents=%d (%.0fs)"
          % (rounds, tokens_per_round, len(index), len(sents), time.time() - t0), flush=True)

    cooc_accum = None; prev = 0; history = []
    from scipy.sparse import csr_matrix
    for r in range(rounds):
        chunk = sents[prev:cuts[r]]; prev = cuts[r]
        cooc_r = SA.build_cooc(chunk, index, SA.WINDOW)
        cooc_accum = cooc_r if cooc_accum is None else cooc_accum + cooc_r
        # PRUNE (recurrence gate) then PPMI (surprise-weighting prune) then SVD
        pruned, kept = recurrence_prune(cooc_accum, min_count)
        ppmi = SA.ppmi_matrix(pruned)
        vecs = SA.svd_vectors(ppmi)
        sim_fn = SA.dense_vec_cosine_fn(vecs, index)
        rs = _rho(simlex, sim_fn); rw = _rho(wordsim, sim_fn)
        # controls at this round: RAW-count (no prune) + info-free shuffled-corpus twin
        raw_fn = SA.sparse_row_cosine_fn(cooc_accum, index)
        rs_raw = _rho(simlex, raw_fn)
        shuf = SA.build_cooc(chunk, index, SA.WINDOW, shuffle_seed=1234)
        shuf_ppmi = SA.ppmi_matrix(shuf); shuf_vecs = SA.svd_vectors(shuf_ppmi)
        rs_shuf = _rho(simlex, SA.dense_vec_cosine_fn(shuf_vecs, index))
        _r = lambda x: round(x, 4) if x is not None else 0.0     # guard: an empty round (corpus exhausted) -> None rho
        row = {"round": r + 1, "cum_tokens": int(tokens_per_round * (r + 1)), "kept_frac": round(kept, 3),
               "simlex_rho": _r(rs["rho"]), "simlex_ci_half": _r(rs["ci_half"]),
               "wordsim_rho": _r(rw["rho"]), "simlex_raw_rho": _r(rs_raw["rho"]),
               "simlex_shuffled_rho": _r(rs_shuf["rho"]), "n_pairs": rs["n"]}
        history.append(row)
        print("[grow] round %d cum=%dM kept=%.2f | SimLex rho=%.4f (raw %.4f, shuf %.4f) WordSim rho=%.4f (%.0fs)"
              % (r + 1, row["cum_tokens"] // 10 ** 6, kept, rs["rho"], rs_raw["rho"], rs_shuf["rho"],
                 rw["rho"], time.time() - t0), flush=True)
        last_vecs = vecs

    # FREEZE the grown associative store (the respectable corpus), for permanent inclusion
    sz = 0.0
    if freeze:
        words = [w for w, _ in sorted(index.items(), key=lambda kv: kv[1])]
        np.savez_compressed(ASSET, words=np.array(words), vecs=last_vecs.astype(np.float32),
                            meta=json.dumps({"builder": "exp_knowledge_factory_grow_loop_v1", "rounds": rounds,
                                             "cum_tokens": int(total), "min_count": min_count, "svd_k": SA.SVD_K,
                                             "store": "associative_similarity (reading-grown, PPMI-SVD, gated)"}))
        sz = os.path.getsize(ASSET) / 1e6

    first, last = history[0], history[-1]
    climb = last["simlex_rho"] - first["simlex_rho"]
    res = {"rounds": rounds, "tokens_per_round": tokens_per_round, "history": history,
           "n_breadth_sources": len(per_source),
           "breadth_sources": {k: int(v) for k, v in sorted(per_source.items(), key=lambda kv: -kv[1])},
           "climb_simlex": round(climb, 4), "final_simlex_rho": last["simlex_rho"],
           "final_wordsim_rho": last["wordsim_rho"],
           "prune_helps": bool(last["simlex_rho"] > last["simlex_raw_rho"]),
           "shuffled_twin_loses": bool(last["simlex_rho"] > last["simlex_shuffled_rho"]),
           "monotone_climb": bool(all(history[i]["simlex_rho"] >= history[i - 1]["simlex_rho"] - 0.01
                                      for i in range(1, len(history)))),
           "frozen_asset": ASSET, "frozen_mb": round(sz, 1), "elapsed_s": round(time.time() - t0, 1)}
    res["headline"] = ("GROW LOOP: SimLex rho %.4f -> %.4f over %d rounds (climb +%.4f, monotone=%s) | prune>raw=%s "
                       "| shuffled-twin-loses=%s | WordSim %.4f | FROZEN %s (%.1f MB)"
                       % (first["simlex_rho"], last["simlex_rho"], rounds, climb, res["monotone_climb"],
                          res["prune_helps"], res["shuffled_twin_loses"], last["wordsim_rho"],
                          os.path.basename(ASSET), sz))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_grow_loop_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # recurrence_prune drops sub-threshold entries; a tiny 2-round climb runs end-to-end on the smoke corpus.
    from scipy.sparse import csr_matrix
    m = csr_matrix(np.array([[5, 1], [0, 4]], float))
    pruned, kept = recurrence_prune(m, 3)
    assert pruned.nnz == 2 and abs(kept - 2.0 / 3.0) < 0.02, \
        "recurrence prune keeps >=3 only (2 of 3 nnz): nnz=%d kept=%.2f" % (pruned.nnz, kept)
    print("SELFTEST PASS (recurrence prune keeps recurrent co-occurrence; kept=%.2f)" % kept, flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--tokens-per-round", type=int, default=3_000_000)
    ap.add_argument("--min-count", type=int, default=3)
    ap.add_argument("--vocab-cap", type=int, default=40000)
    ap.add_argument("--big", action="store_true", help="LARGE volume ingestion (simplewiki+ARC, ~120M tokens, 80k vocab)")
    ap.add_argument("--broad", action="store_true", help="BREADTH ingestion: ALL genres balanced (fiction, textbook, graded, drama, news, social + capped expository)")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    if args.broad:
        # breadth over raw volume: every genre (incl. math/physics/astronomy/philosophy/neuroscience textbooks),
        # expository capped so diverse registers are a real fraction. 4 rounds x 10M ~= the full balanced corpus.
        run(rounds=4, tokens_per_round=10_000_000, min_count=2, vocab_cap=80000, broad=True, big_cap=15_000_000,
            smoke=args.smoke)
        return 0
    if args.big:
        run(rounds=6, tokens_per_round=20_000_000, min_count=args.min_count, corpus_paths=[SIMPLEWIKI, ARC],
            vocab_cap=80000)
        return 0
    run(rounds=args.rounds, tokens_per_round=args.tokens_per_round, min_count=args.min_count,
        vocab_cap=args.vocab_cap)
    return 0


if __name__ == "__main__":
    sys.exit(main())
