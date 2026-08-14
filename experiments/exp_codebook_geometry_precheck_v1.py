#!/usr/bin/env python
"""PRE-CHECK (stage 0 of the composed-chain cell): what is the near-duplicate rate of OUR OWN
live 5491-anchor codebook, and does whitening change its geometry?

WHY THIS RUNS BEFORE THE CHAIN CELL IS BUILT
--------------------------------------------
`exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` found 22% of a 241-atom CURATED codebook
had a near-identical neighbour (top pair cos=1.0000, probability_space <-> measure_space). If OUR
live anchor set has the same pathology, then no write rule separates concepts that arrive
bit-identical, and the composed pool->expand->whiten->pinv->coarse-to-fine chain is dead on arrival
for a reason that has nothing to do with the write rule. That is a cheap, decisive, publishable
negative -- so it is measured FIRST.

THE CONTROL THAT MAKES THE NUMBER MEAN ANYTHING
----------------------------------------------
5491 anchors live in d=256. That is 21x OVERCOMPLETE. You CANNOT have 5491 near-orthogonal vectors
in 256 dimensions -- high nearest-neighbour cosines are partly GEOMETRICALLY FORCED, not evidence
of a defect. So every measured statistic is reported beside a RANDOM null of the SAME shape
(5491 x 256), and the only interpretable quantity is the EXCESS over that null. A raw
near-duplicate rate quoted without this null is uninterpretable.

Reports the same statistic under four codebook transforms so the whitening stage's contribution to
CODEBOOK GEOMETRY is separable before any read-out is run:
  RAW          -- the live graded accumulated sums (what canonicalize_fast actually scans)
  SIGNED       -- np.sign of them (the pre-2026-08-14 comparator)
  CENTERED     -- common-mode (mean anchor) removed
  ZCA_WHITEN   -- full covariance whitening (the ledger's "whiten" stage)

ASCII-only. Threads pinned before numpy import.
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json                                                                    # noqa: E402
import platform                                                                # noqa: E402
import sys                                                                     # noqa: E402
import time                                                                    # noqa: E402
from collections import Counter, defaultdict                                    # noqa: E402
from datetime import datetime, timezone                                        # noqa: E402
from typing import Dict, List, Tuple                                           # noqa: E402

import numpy as np                                                             # noqa: E402

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.reading_grounding_loop import (                                     # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, content_lemmas, context_vector_masked,
)

ANCHOR_NAME = "exp_codebook_geometry_precheck_v1"
MASTER_SEED = 20260814

# --- kept BYTE-IDENTICAL to exp_grounding_readout_known_answer_v1 so the anchor set is the SAME
MIN_LEMMA_COUNT = 8
MIN_LEMMA_LEN = 3
K_SENT_TOTAL = 90
PROFILE_FRAC = 0.8
SMOKE_LIMIT_PER_SEGMENT = 400

NN_THRESHOLDS = (0.99, 0.95, 0.90, 0.80, 0.70)
TOP_PAIRS = 25
BLOCK = 512


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _out_dir(run_mode: str) -> str:
    suffix = "" if run_mode == "full" else "_" + run_mode.upper()
    d = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _write_json(path: str, obj: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(json.dumps(obj, indent=2, sort_keys=False).encode("utf-8"))
    os.replace(tmp, path)


# ------------------------------------------------------------------ space construction
def build_corpus(run_mode: str) -> List[str]:
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode != "full" else None
    return [s for _seg, s in load_corpus_v5(limit, lineaware=True)]


def build_buckets(sents: List[str]) -> Tuple[Dict[str, List[int]], Counter]:
    lem_of: List[List[str]] = []
    counts: Counter = Counter()
    for s in sents:
        lems = sorted(set(l for l in content_lemmas(s)
                          if l.isalpha() and len(l) >= MIN_LEMMA_LEN))
        lem_of.append(lems)
        counts.update(lems)
    buckets: Dict[str, List[int]] = defaultdict(list)
    for i, lems in enumerate(lem_of):
        for l in lems:
            if counts[l] >= MIN_LEMMA_COUNT and len(buckets[l]) < K_SENT_TOTAL:
                buckets[l].append(i)
    return {k: v for k, v in buckets.items() if counts[k] >= MIN_LEMMA_COUNT}, counts


def _n_profile(k: int) -> int:
    if k < 2:
        return k
    return min(k - 1, max(1, int(k * PROFILE_FRAC)))


def build_space(sents: List[str], buckets: Dict[str, List[int]]) -> ConceptSpace:
    sp = ConceptSpace(d=CTX_D)
    t0 = time.time()
    lemmas = sorted(buckets)
    for k, w in enumerate(lemmas):
        for i in buckets[w][:_n_profile(len(buckets[w]))]:
            sp.observe(w, context_vector_masked(sents[i], w))
        if k % 1000 == 0 or k == len(lemmas) - 1:
            print("[space] %d/%d elapsed=%.1fs" % (k + 1, len(lemmas), time.time() - t0),
                  flush=True)
    return sp


# ------------------------------------------------------------------ geometry statistics
def _unit(mat: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(mat, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return mat / n


def nn_stats(mat: np.ndarray, labels: List[str], top_pairs: int = TOP_PAIRS) -> dict:
    """Nearest-neighbour cosine per row (self excluded), blocked so a 5491^2 matrix is never held.

    Also returns the highest-cosine PAIRS with their lemma names -- the only way to tell a
    forced-geometry high cosine from a genuine two-concepts-one-vector collision."""
    X = _unit(np.asarray(mat, dtype=np.float32))
    n = X.shape[0]
    best = np.full(n, -2.0, dtype=np.float32)
    best_j = np.full(n, -1, dtype=np.int64)
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        S = X[s:e] @ X.T                                  # (b, n)
        for r in range(e - s):
            S[r, s + r] = -2.0                            # exclude self
        j = np.argmax(S, axis=1)
        best[s:e] = S[np.arange(e - s), j]
        best_j[s:e] = j
    order = np.argsort(-best)
    seen = set()
    pairs = []
    for i in order:
        i = int(i)
        j = int(best_j[i])
        key = (min(i, j), max(i, j))
        if key in seen:
            continue
        seen.add(key)
        pairs.append({"a": labels[i], "b": labels[j], "cos": round(float(best[i]), 6)})
        if len(pairs) >= top_pairs:
            break
    return {
        "n": int(n),
        "d": int(X.shape[1]),
        "nn_cos_mean": round(float(best.mean()), 6),
        "nn_cos_median": round(float(np.median(best)), 6),
        "nn_cos_p95": round(float(np.percentile(best, 95)), 6),
        "nn_cos_max": round(float(best.max()), 6),
        "frac_nn_above": {str(t): round(float((best >= t).mean()), 6) for t in NN_THRESHOLDS},
        "n_nn_above": {str(t): int((best >= t).sum()) for t in NN_THRESHOLDS},
        "top_pairs": pairs,
    }


def zca_whiten(mat: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Full ZCA whitening of the anchor cloud: centre, then decorrelate+equalise every direction.
    This is the ledger's 'whiten' stage applied to the CODEBOOK (not to a read-out query)."""
    X = np.asarray(mat, dtype=np.float64)
    mu = X.mean(axis=0, keepdims=True)
    Xc = X - mu
    C = (Xc.T @ Xc) / max(1, Xc.shape[0] - 1)
    w, V = np.linalg.eigh(C)
    w = np.maximum(w, 0.0)
    W = V @ np.diag(1.0 / np.sqrt(w + eps)) @ V.T
    return Xc @ W


def spectrum_stats(mat: np.ndarray) -> dict:
    """How much of the anchor cloud's energy is COMMON MODE. If the top eigenvalue dominates, the
    codebook's high nearest-neighbour cosines are a shared backbone, which centering/whitening
    removes -- that is a DIFFERENT disease from bit-identical concept collisions."""
    X = np.asarray(mat, dtype=np.float64)
    Xu = _unit(X).astype(np.float64)
    mu = Xu.mean(axis=0)
    Xc = Xu - mu
    C = (Xc.T @ Xc) / max(1, Xc.shape[0] - 1)
    w = np.sort(np.linalg.eigvalsh(C))[::-1]
    tot = float(w.sum()) or 1.0
    mean_vec_norm = float(np.linalg.norm(mu))
    return {
        "mean_anchor_norm_of_unit_rows": round(mean_vec_norm, 6),
        "common_mode_energy_frac": round(float(mean_vec_norm ** 2), 6),
        "top1_eigen_frac_after_centering": round(float(w[0] / tot), 6),
        "top10_eigen_frac_after_centering": round(float(w[:10].sum() / tot), 6),
        "participation_ratio": round(float((w.sum() ** 2) / float((w ** 2).sum())), 4),
    }


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=["full", "smoke"])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        rng = np.random.default_rng(0)
        A = rng.standard_normal((60, 16))
        A[7] = A[3]                                        # planted exact duplicate
        st = nn_stats(A, ["w%d" % i for i in range(60)])
        assert st["nn_cos_max"] > 0.999, st["nn_cos_max"]
        assert st["n_nn_above"]["0.99"] >= 2, st
        names = {st["top_pairs"][0]["a"], st["top_pairs"][0]["b"]}
        assert names == {"w3", "w7"}, names
        Z = zca_whiten(A)
        C = np.cov(Z.T)
        off = C - np.diag(np.diag(C))
        assert float(np.abs(off).max()) < 0.15, float(np.abs(off).max())
        sp = spectrum_stats(A)
        assert 0.0 <= sp["top1_eigen_frac_after_centering"] <= 1.0
        # a whitened cloud must NOT lose a planted EXACT duplicate: identical rows stay identical
        stz = nn_stats(Z, ["w%d" % i for i in range(60)])
        assert stz["nn_cos_max"] > 0.999, stz["nn_cos_max"]
        print("SELF-TEST OK")
        return

    t0 = time.time()
    out = _out_dir(args.run_mode)
    print("[start] %s run_mode=%s out=%s" % (ANCHOR_NAME, args.run_mode, out), flush=True)
    sents = build_corpus(args.run_mode)
    print("[corpus] n_sentences=%d elapsed=%.1fs" % (len(sents), time.time() - t0), flush=True)
    buckets, _counts = build_buckets(sents)
    print("[corpus] n_candidate_lemmas=%d" % len(buckets), flush=True)
    space = build_space(sents, buckets)
    anchors, mat = space.anchor_matrix()
    print("[space] n_anchors=%d d=%d graded=%s" % (len(anchors), mat.shape[1], GRADED_COMPARATOR),
          flush=True)

    rng = np.random.default_rng(MASTER_SEED)
    variants = {
        "RAW_GRADED": np.asarray(mat, dtype=np.float64),
        "SIGNED": np.sign(np.asarray(mat, dtype=np.float64)),
        "CENTERED": np.asarray(mat, dtype=np.float64) - np.asarray(mat, dtype=np.float64).mean(axis=0, keepdims=True),
        "ZCA_WHITEN": zca_whiten(np.asarray(mat, dtype=np.float64)),
        "NULL_RANDOM": rng.standard_normal((len(anchors), mat.shape[1])),
    }
    res = {}
    for name, M in variants.items():
        ts = time.time()
        res[name] = nn_stats(M, anchors)
        print("[nn] %-12s nn_med=%.4f nn_max=%.4f frac>=0.99=%.4f (%.1fs)"
              % (name, res[name]["nn_cos_median"], res[name]["nn_cos_max"],
                 res[name]["frac_nn_above"]["0.99"], time.time() - ts), flush=True)

    spec = spectrum_stats(np.asarray(mat, dtype=np.float64))
    print("[spectrum] common_mode_energy=%.4f top1_after_centering=%.4f PR=%.1f"
          % (spec["common_mode_energy_frac"], spec["top1_eigen_frac_after_centering"],
             spec["participation_ratio"]), flush=True)

    raw = res["RAW_GRADED"]
    null = res["NULL_RANDOM"]
    excess_99 = raw["frac_nn_above"]["0.99"] - null["frac_nn_above"]["0.99"]
    excess_med = raw["nn_cos_median"] - null["nn_cos_median"]
    # DOOM band: our codebook has the 241-atom codebook's disease at comparable rate AND whitening
    # does not dissolve it -> write-rule changes cannot separate what arrives identical.
    doomed = (raw["frac_nn_above"]["0.99"] >= 0.10
              and res["ZCA_WHITEN"]["frac_nn_above"]["0.99"] >= 0.05)
    if doomed:
        verdict = "CODEBOOK_DOOMED_BY_NEAR_DUPLICATES"
    elif raw["frac_nn_above"]["0.99"] < 0.01:
        verdict = "NEAR_DUPLICATES_NOT_THE_DEFECT"
    else:
        verdict = "PARTIAL_NEAR_DUPLICATE_LOAD"
    msg = ("OUR live codebook n=%d d=%d: frac(NN>=0.99)=%.4f (null %.4f, excess %+.4f); "
           "median NN cos %.4f (null %.4f, excess %+.4f); max %.4f. After ZCA whitening "
           "frac(NN>=0.99)=%.4f median=%.4f. 241-atom curated codebook reference was 0.2241."
           % (raw["n"], raw["d"], raw["frac_nn_above"]["0.99"], null["frac_nn_above"]["0.99"],
              excess_99, raw["nn_cos_median"], null["nn_cos_median"], excess_med,
              raw["nn_cos_max"], res["ZCA_WHITEN"]["frac_nn_above"]["0.99"],
              res["ZCA_WHITEN"]["nn_cos_median"]))
    print("[verdict] %s | %s" % (verdict, msg), flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": args.run_mode,
        "ts_iso": _now(),
        "verdict": verdict,
        "verdict_msg": msg,
        "graded_comparator": bool(GRADED_COMPARATOR),
        "n_anchors": len(anchors),
        "d": int(mat.shape[1]),
        "n_sentences": len(sents),
        "overcompleteness_ratio": round(len(anchors) / float(mat.shape[1]), 3),
        "nn_by_variant": res,
        "spectrum": spec,
        "excess_over_null": {
            "frac_nn_ge_0.99": round(float(excess_99), 6),
            "nn_cos_median": round(float(excess_med), 6),
        },
        "reference_curated_codebook": {
            "cell": "exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1",
            "K": 241, "n_atoms_nn_above_0.99": 54, "rate": 0.2241,
            "top_pair_cos": 1.0, "top_pair": "math::T1/probability_space <-> math::T1/measure_space",
        },
        "elapsed_s": round(time.time() - t0, 1),
        "python": platform.python_version(),
    }
    _write_json(os.path.join(out, "metrics.json"), metrics)
    print("[done] %.1fs -> %s" % (time.time() - t0, os.path.join(out, "metrics.json")), flush=True)


if __name__ == "__main__":
    main()
