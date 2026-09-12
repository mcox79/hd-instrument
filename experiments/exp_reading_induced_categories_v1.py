"""exp_reading_induced_categories_v1 -- the TOP RUNG of the upstream math-BF pass (owner 2026-09-12: "start at the top making
sure it's 100% brain foundational"): LEXICAL CATEGORIES INDUCED FROM READING, no labels, at the reading scale a child gets.

BRAIN COMPUTATION (PINNED at the computational level): a word's syntactic category is its SUBSTITUTION CLASS -- the words
that occur in the same immediate frames (Harris 1954; Mintz 2003 frequent frames, 91-98% accuracy on child-directed speech;
Redington, Chater & Finch 1998: immediate +-1/+-2 context vectors over the most frequent context words, clustered). The
acquisition is unsupervised and incremental; the brain's statistical-learning system accrues (target, left-neighbour) and
(target, right-neighbour) co-occurrence (the same Hebbian directional accrual the substrate's reading-grown SEQ store uses)
and categories emerge as clusters in that space. OUR-INVENTION (swept, never adopted): the number of clusters, the number of
context words, the reading budget, the SVD rank, the PPMI shift.

WHY THIS CELL: the prior fully-BF attempt (exp_parser_fully_bf_chain_v1, 2026-09-10) induced categories from 8,000 UD-EWT
training sentences -> many-to-one 0.323 -- a WEAK implementation (tiny reading budget, generic 2V-column PPMI), not a
ceiling (literature 0.75-0.94). This cell reads MODERN Simple-Wikipedia (up to 1M lines, ~20M tokens) -- the same corpus
the grown SEQ store reads -- and tests whether reading scale + the frequent-context computation reach usable accuracy.

ARMS (categories are TYPE-level here; the token-level graded readout is arm T):
  INDUCED(k, M, lines)   word x {L1, R1, L2, R2} x top-M context words -> PPMI -> SVD(r) -> k-means(k)  (swept)
  FRAMES                 Mintz frequent frames (prev, next) as categories, frame-overlap merge           (reference)
  MAJORITY floor         every word -> one category (= majority UPOS NOUN on the eval tokens)            (must beat, CI-sep)
  TWIN                   the INDUCED clustering with cluster ids SHUFFLED across words (structure destroyed)
  T: token readout       P(c | w, left, right) = P(c|w) * P(left | c) * P(right | c) (all from induced clusters, no labels)
EVAL (labels used for EVALUATION ONLY, never in acquisition): UD-EWT TEST gold UPOS; many-to-one accuracy over covered
tokens, coverage, V-measure (homogeneity/completeness), per-UPOS recall of the majority-mapped clusters; bootstrap CI over
sentences for INDUCED - MAJORITY and INDUCED - TWIN.
Glass-box, CPU, numpy/scipy only, NO LLM, NO external tagger, NO gold in acquisition. Threads capped. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_reading_induced_categories_v1.py --lines 200000 --k 34 --ctx 1000
     .venv/Scripts/python.exe experiments/exp_reading_induced_categories_v1.py --sweep     (lines x k grid, writes metrics)
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

__bf_status__ = "BF"   # label-free distributional category induction (Harris / Mintz / Redington-Chater-Finch); gold = eval only
__bf_verified__ = "2026-09-12 strategy (upstream pass, top rung)"
__bf_note__ = "reading-induced lexical categories at scale; k / context words / budget / rank are swept, never adopted"
__bf_corrections__ = []

SIMPLEWIKI = os.path.join(_REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
UD_TEST = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
ANCHOR_NAME = "reading_induced_categories_v1"
from experiments._seed_checkpoint import get_output_dir   # Q115: the canonical re-runnable output dir
OUT_DIR = str(get_output_dir(ANCHOR_NAME))
_TOK = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+(?:[.,][0-9]+)*|[^\sA-Za-z0-9]")
SEED = 20260912


def tokenize(line: str):
    """Glass-box orthographic tokenizer (letters/apostrophe clitics, numbers, single punctuation marks), lower-cased."""
    return [m.group(0).lower() for m in _TOK.finditer(line)]


def read_lines(path: str, n: int):
    k = 0
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield tokenize(line)
            k += 1
            if k >= n:
                break


def ud_test_tokens(path: str):
    sents = []
    cur = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); cur = []
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if "-" in cols[0] or "." in cols[0]:
                continue
            cur.append((cols[1].lower(), cols[3]))
    if cur:
        sents.append(cur)
    return sents


# ----------------------------------------------------------------------------------------------------------------------
# ACQUISITION (no labels): directional immediate-context counts -> PPMI -> SVD -> k-means
def accrue_counts(lines_iter, vocab_cap: int, ctx_cap: int, offsets=(-2, -1, 1, 2)):
    """Pass 1 counts word frequencies; pass 2 accrues word x (offset, context word) counts for the top-ctx_cap context words.
    Returns vocab, ctx vocab, dense count matrix (V, len(offsets)*M) float32, word frequencies."""
    lines = list(lines_iter)
    freq = Counter()
    for toks in lines:
        freq.update(toks)
    vocab = [w for w, _ in freq.most_common(vocab_cap)]
    w2i = {w: i for i, w in enumerate(vocab)}
    ctx = [w for w, _ in freq.most_common(ctx_cap)]
    c2i = {w: i for i, w in enumerate(ctx)}
    V, M, O = len(vocab), len(ctx), len(offsets)
    C = np.zeros((V, O * M), dtype=np.float32)
    for toks in lines:
        ids = np.array([w2i.get(t, -1) for t in toks], dtype=np.int64)
        cids = np.array([c2i.get(t, -1) for t in toks], dtype=np.int64)
        n = len(toks)
        for oi, off in enumerate(offsets):
            if off < 0:
                tgt = ids[-off:]; cx = cids[:n + off]
            else:
                tgt = ids[:n - off]; cx = cids[off:]
            m = (tgt >= 0) & (cx >= 0)
            if m.any():
                np.add.at(C, (tgt[m], oi * M + cx[m]), 1.0)
    return vocab, ctx, C, freq


def ppmi_svd(C: np.ndarray, rank: int, shift: float = 0.0):
    total = C.sum()
    row = C.sum(1, keepdims=True) + 1e-9
    col = C.sum(0, keepdims=True) + 1e-9
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((C * total) / (row * col) + 1e-30) - shift
    pmi[C <= 0] = 0.0
    pmi = np.maximum(pmi, 0.0).astype(np.float32)
    U, S, _ = np.linalg.svd(pmi, full_matrices=False)
    r = min(rank, len(S))
    X = U[:, :r] * np.sqrt(S[:r])
    X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    return X


def kmeans(X: np.ndarray, k: int, iters: int = 50, seed: int = 0, weights=None):
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    # k-means++ seeding
    cen = [X[rng.integers(n)]]
    d2 = ((X - cen[0]) ** 2).sum(1)
    for _ in range(1, k):
        p = d2 / d2.sum()
        cen.append(X[rng.choice(n, p=p)])
        d2 = np.minimum(d2, ((X - cen[-1]) ** 2).sum(1))
    cen = np.stack(cen)
    lab = np.zeros(n, dtype=int)
    w = np.ones(n) if weights is None else weights
    for _ in range(iters):
        d = ((X[:, None, :] - cen[None, :, :]) ** 2).sum(2)
        new = d.argmin(1)
        if np.array_equal(new, lab):
            break
        lab = new
        for c in range(k):
            m = lab == c
            if m.any():
                cen[c] = (X[m] * w[m, None]).sum(0) / w[m].sum()
    return lab


def frequent_frames(lines_iter, min_count: int = 3):
    frame_words = defaultdict(Counter)
    for toks in lines_iter:
        for i in range(1, len(toks) - 1):
            frame_words[(toks[i - 1], toks[i + 1])][toks[i]] += 1
    frames = [(fr, wc) for fr, wc in frame_words.items() if sum(wc.values()) >= min_count and len(wc) >= 2]
    frames.sort(key=lambda x: -sum(x[1].values()))
    word2frame = {}
    for idx, (fr, wc) in enumerate(frames):
        for w in wc:
            word2frame.setdefault(w, idx)        # a word's category = its most frequent frame
    return word2frame, len(frames)


# ----------------------------------------------------------------------------------------------------------------------
# EVALUATION (gold used ONLY here)
def many_to_one(test, word2cat):
    cg = defaultdict(Counter); tot = cov = 0
    for s in test:
        for w, g in s:
            tot += 1
            c = word2cat.get(w)
            if c is not None:
                cg[c][g] += 1; cov += 1
    cmap = {c: wc.most_common(1)[0][0] for c, wc in cg.items()}
    per_sent = []
    for s in test:
        hits = [int(cmap.get(word2cat.get(w)) == g) for w, g in s if word2cat.get(w) is not None]
        per_sent.append((sum(hits), len(hits)))
    hit = sum(h for h, _ in per_sent); n = sum(n for _, n in per_sent)
    # V-measure
    N = sum(sum(wc.values()) for wc in cg.values())
    gold_tot = Counter()
    for wc in cg.values():
        gold_tot.update(wc)
    def H(counter):
        p = np.array([v for v in counter.values()], dtype=float); p = p[p > 0] / p.sum()
        return float(-(p * np.log(p)).sum())
    H_gold = H(gold_tot); H_clu = H(Counter({c: sum(wc.values()) for c, wc in cg.items()}))
    H_gold_given_clu = sum(sum(wc.values()) / N * H(wc) for wc in cg.values())
    clu_given_gold = defaultdict(Counter)
    for c, wc in cg.items():
        for g, v in wc.items():
            clu_given_gold[g][c] += v
    H_clu_given_gold = sum(sum(wc.values()) / N * H(wc) for wc in clu_given_gold.values())
    hom = 1 - H_gold_given_clu / H_gold if H_gold else 1.0
    com = 1 - H_clu_given_gold / H_clu if H_clu else 1.0
    v = 2 * hom * com / (hom + com) if (hom + com) else 0.0
    per_upos = {}
    for g in gold_tot:
        r_hit = sum(wc[g] for c, wc in cg.items() if cmap[c] == g)
        per_upos[g] = round(r_hit / gold_tot[g], 3)
    return {"m2o": hit / max(1, n), "coverage": cov / max(1, tot), "v_measure": v, "homogeneity": hom, "completeness": com,
            "n_clusters_used": len(cg), "per_upos_recall": per_upos, "cmap": cmap}, per_sent


def boot_delta(a_sent, b_sent, rng, B=2000):
    """Paired sentence-level bootstrap of accuracy difference (arms may cover different token sets: compare per-sentence
    accuracies over the covered tokens of each arm)."""
    a = np.array([h / n if n else np.nan for h, n in a_sent]); b = np.array([h / n if n else np.nan for h, n in b_sent])
    m = ~np.isnan(a) & ~np.isnan(b); a = a[m]; b = b[m]; n = len(a)
    d = a - b
    boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(B)])
    return float(d.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def run(lines: int, k: int, ctx: int, vocab_cap: int, rank: int, seed: int, test, log):
    t0 = time.time()
    vocab, ctxw, C, freq = accrue_counts(read_lines(SIMPLEWIKI, lines), vocab_cap, ctx)
    n_tok = int(sum(freq.values()))
    X = ppmi_svd(C, rank)
    wts = np.log1p(np.array([freq[w] for w in vocab], dtype=float))
    lab = kmeans(X, k, seed=seed, weights=wts)
    word2cat = {w: int(lab[i]) for i, w in enumerate(vocab)}
    ind, ind_sent = many_to_one(test, word2cat)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(vocab))
    twin = {w: int(lab[perm[i]]) for i, w in enumerate(vocab)}
    tw, tw_sent = many_to_one(test, twin)
    maj = {w: 0 for w in vocab}
    mj, mj_sent = many_to_one(test, maj)
    d_maj = boot_delta(ind_sent, mj_sent, rng); d_tw = boot_delta(ind_sent, tw_sent, rng)
    res = {"lines": lines, "tokens_read": n_tok, "vocab": len(vocab), "ctx_words": len(ctxw), "k": k, "rank": rank,
           "induced": {kk: vv for kk, vv in ind.items() if kk != "cmap"},
           "majority_floor_m2o": mj["m2o"], "twin_m2o": tw["m2o"],
           "induced_minus_majority": d_maj, "induced_minus_twin": d_tw, "elapsed_s": round(time.time() - t0, 1)}
    log(f"lines={lines} k={k} ctx={ctx} rank={rank}: m2o={ind['m2o']:.4f} cov={ind['coverage']:.3f} V={ind['v_measure']:.3f} "
        f"| majority {mj['m2o']:.4f} twin {tw['m2o']:.4f} | ind-maj {d_maj[0]:+.4f} [{d_maj[1]:+.4f},{d_maj[2]:+.4f}] "
        f"| per-UPOS {ind['per_upos_recall']} | {res['elapsed_s']}s")
    return res, word2cat, ind["cmap"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=200000)
    ap.add_argument("--k", type=int, default=34)
    ap.add_argument("--ctx", type=int, default=1000)
    ap.add_argument("--vocab", type=int, default=20000)
    ap.add_argument("--rank", type=int, default=100)
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--frames", action="store_true", help="also run the Mintz frequent-frame reference")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    test = ud_test_tokens(UD_TEST)
    logf = open(os.path.join(OUT_DIR, "log.txt"), "a", encoding="utf-8")
    def log(s):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()
    results = []
    if a.sweep:
        grid = [(50000, 17), (50000, 34), (200000, 17), (200000, 34), (200000, 68), (1000000, 34), (1000000, 68)]
        for lines, k in grid:
            r, _, _ = run(lines, k, a.ctx, a.vocab, a.rank, SEED, test, log); results.append(r)
    else:
        r, word2cat, cmap = run(a.lines, a.k, a.ctx, a.vocab, a.rank, SEED, test, log); results.append(r)
        with open(os.path.join(OUT_DIR, f"induced_categories_l{a.lines}_k{a.k}.json"), "w", encoding="utf-8") as f:
            json.dump({"word2cat": word2cat, "cluster_to_upos_name": cmap, "note": "cmap uses gold ONLY to NAME clusters"}, f)
    if a.frames:
        w2f, nfr = frequent_frames(read_lines(SIMPLEWIKI, min(a.lines, 200000)))
        fr, _ = many_to_one(test, w2f)
        log(f"FRAMES (Mintz, {nfr} frames): m2o={fr['m2o']:.4f} cov={fr['coverage']:.3f} V={fr['v_measure']:.3f}")
        results.append({"frames": {kk: vv for kk, vv in fr.items() if kk != "cmap"}, "n_frames": nfr})
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results, "supervised_tagger_ref_ud_ewt_test": 0.944}, f, indent=1)
    log("wrote " + os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    main()
