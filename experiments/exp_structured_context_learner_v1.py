"""exp_structured_context_learner_v1 -- the brain-faithful learner's OPEN lever is CONTEXT SHAPE,
not the update rule. Hold everything constant except the definition of "context" and ask whether
grammatical-relation-typed (dependency) contexts beat the linear-window baseline on the SIMILARITY
axis (SimLex/SimVerb) where the baseline is weak.

WHY (see notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/
DESIGN_brain_analysis.md): the update-rule route is CLOSED on disk -- SGNS == shifted-PPMI
factorisation (Levy & Goldberg 2014), online == batch on a stationary corpus, confirmed 3x on this
substrate. The brain organises meaning by grammatical ROLE (ATL hub + pMTG/LIFG syntax; Harris 1954
= substitutability within grammatical environments), not linear nearness. So the lever is WHAT the
learner learns over. Dependency-typed contexts -> paradigmatic/functional similarity (SimLex/SimVerb);
window contexts -> topical relatedness (WordSim, already strong).

ONE VARIABLE: the word x context matrix's COLUMNS. Same corpus subset, same target-word vocab, same
PPMI(alpha)+SVD(k) pipeline (REUSED VERBATIM from exp_learn_from_reading_strong_arm_v1), same scorer
(score_arm: Spearman rho of pairwise cosine vs human ratings on the common-coverage intersection,
bootstrap CI half-width + label-permutation null p95).

ARMS (all batch PPMI-SVD unless noted; differ only in context columns):
  WIN2         symmetric +/-2 window (the incumbent context shape).
  WIN1         symmetric +/-1 window (the STRONGEST pure-window structural floor -- the honest floor).
  DEP_TYPED    columns = (directed deprel, filler) typed contexts -- the brain-faithful arm.
  DEP_UNTYPED  columns = syntactic-neighbour filler words WITHOUT the relation label (ablation).
  SELPREF      verbs only: each verb = PPMI dist over its typed argument-slot fillers (nsubj/dobj) --
               the McRae selectional-preference vector; scored on SimVerb.
INFO-FREE TWINS (must LOSE, CI-separated):
  DEP_LABELSHUF  dependency-typed with relation labels globally permuted -- keeps parse+filler+sparsity,
                 destroys only the grammatical-relation TYPE. The KILLER twin.
  RAND_TREE      typed contexts from a random spanning tree per sentence (same count, random structure).
  SHUF_CORPUS    global token shuffle (same unigram marginals).
  RANDOM         random dense vectors.

Parse: spaCy en_core_web_sm (a small CNN parser, NOT an LLM; offline foundation-build). Parsed
(token, head, deprel, upos) cached once to JSONL. ASCII-only. Writes only to its own data dir.
hdlab/ NOT modified. data/foundation/** never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from array import array as _arr

import numpy as np
import scipy.sparse as sp
from scipy.stats import spearmanr

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# REUSE the baseline's math + scoring VERBATIM (single-variable discipline: same pipeline, diff cols)
from experiments.exp_learn_from_reading_strong_arm_v1 import (
    ppmi_matrix, svd_vectors, sparse_row_cosine_fn, dense_vec_cosine_fn, random_vec_cosine_fn,
    ortho_sim_fn, load_simlex, load_simverb, load_wordsim, score_arm, covered_pairs,
    benchmark_vocab, build_vocab, build_cooc, PPMI_ALPHA, SVD_K, SVD_P,
)

ANCHOR = "structured_context_learner_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_" + ANCHOR)
CORPUS_PATH = os.path.join(_REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
CACHE_DIR = os.path.join(_REPO, "data", "exp_" + ANCHOR)
SEED = 13
CTX_MIN_COUNT = 5          # min occurrences for a typed-context COLUMN to be kept
ARG_SLOTS = {"nsubj", "nsubjpass", "dobj", "obj", "iobj", "obl", "nmod", "amod", "acomp", "attr"}
CONTENT_UPOS = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}


# --------------------------------------------------------------------------- parse + cache
def parse_and_cache(max_tokens, cache_path, batch_lines=2000):
    """Stream simplewiki, spaCy-parse, cache per-sentence [tok_lower, head_idx, deprel, upos] JSONL.
    Resumable: if the cache already holds >= max_tokens, reuse it. spaCy parser+tagger only."""
    if os.path.exists(cache_path):
        ntok = 0
        with open(cache_path, encoding="utf-8") as fh:
            for ln in fh:
                ntok += len(json.loads(ln))
                if ntok >= max_tokens:
                    print("[parse] cache HIT %s (>=%d tokens)" % (cache_path, max_tokens), flush=True)
                    return cache_path
        print("[parse] cache has only %d tokens < %d; re-parsing" % (ntok, max_tokens), flush=True)
    import spacy
    # keep tagger + attribute_ruler: attribute_ruler populates token.pos_ (UPOS); disabling it
    # leaves pos_ EMPTY, which silently broke the SELPREF verb arm (upos never == "VERB").
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    nlp.max_length = 2_000_000
    t0 = time.time()
    ntok = 0
    n_sent = 0
    tmp = cache_path + ".tmp"
    with open(CORPUS_PATH, encoding="utf-8") as fin, open(tmp, "w", encoding="utf-8") as fout:
        buf = []
        def flush_buf():
            nonlocal ntok, n_sent
            for doc in nlp.pipe(buf, batch_size=64):
                for sent in doc.sents:
                    start = sent[0].i
                    rec = []
                    for t in sent:
                        if not t.text.strip():
                            continue
                        rec.append([t.text.lower(), t.head.i - start, t.dep_, t.pos_])
                    if len(rec) >= 2:
                        fout.write(json.dumps(rec) + "\n")
                        ntok += len(rec); n_sent += 1
            buf.clear()
        for ln in fin:
            ln = ln.strip()
            if ln:
                buf.append(ln)
            if len(buf) >= batch_lines:
                flush_buf()
                if ntok >= max_tokens:
                    break
                if n_sent and n_sent % 20000 < batch_lines:
                    print("[parse] %d sent / %d tok / %.0fs" % (n_sent, ntok, time.time() - t0), flush=True)
        if buf and ntok < max_tokens:
            flush_buf()
    os.replace(tmp, cache_path)
    print("[parse] DONE %d sent / %d tok / %.0fs -> %s" % (n_sent, ntok, time.time() - t0, cache_path), flush=True)
    return cache_path


def load_parsed(cache_path, max_tokens):
    """List of sentences; each = list of (tok, head_idx, deprel, upos). Truncated at max_tokens."""
    sents = []
    ntok = 0
    with open(cache_path, encoding="utf-8") as fh:
        for ln in fh:
            rec = json.loads(ln)
            sents.append([(r[0], int(r[1]), r[2], r[3]) for r in rec])
            ntok += len(rec)
            if ntok >= max_tokens:
                break
    return sents, ntok


# --------------------------------------------------------------------------- context builders
def token_sents(parsed):
    """Plain token-lists for window arms + vocab (surface lowercased, matches the baseline)."""
    return [[tok for (tok, _h, _r, _u) in s] for s in parsed]


def _edges(parsed):
    """Yield (i_tok, deprel, j_tok, direction) undirected pairs from each sentence's dependency tree.
    direction '+' = child->head, '-' = head->child. Skips root self-links and punctuation deprels."""
    for s in parsed:
        for i, (tok, head, rel, _u) in enumerate(s):
            if head == i or rel in ("punct", "ROOT", "root", "dep"):
                continue
            if head < 0 or head >= len(s):
                continue
            htok = s[head][0]
            yield tok, rel, htok, "+"      # child sees (rel, head)
            yield htok, rel, tok, "-"       # head sees (rel_inv, child)


def _build_from_edges(edge_iter, n_rows, min_count):
    """Memory-efficient CSR builder: consume (row_id:int, colname:str) edges, map colnames to int ids
    on the fly (no giant list of (int,str) tuples), drop columns below min_count. Scales to tens of
    millions of edges (int32 arrays + one string->id dict, vectorised remap)."""
    col_id = {}
    col_count = []
    rows = _arr("i"); cols = _arr("i")
    for ri, cn in edge_iter:
        j = col_id.get(cn)
        if j is None:
            j = len(col_id); col_id[cn] = j; col_count.append(0)
        col_count[j] += 1
        rows.append(ri); cols.append(j)
    if not col_id:
        return sp.csr_matrix((n_rows, 1), dtype=np.float64), 0
    rows_np = np.frombuffer(rows, dtype=np.int32).astype(np.int64)
    cols_np = np.frombuffer(cols, dtype=np.int32).astype(np.int64)
    cc = np.asarray(col_count, dtype=np.int64)
    keepmask = cc >= min_count
    n_keep = int(keepmask.sum())
    if n_keep == 0:
        return sp.csr_matrix((n_rows, 1), dtype=np.float64), 0
    remap = np.full(len(cc), -1, dtype=np.int64)
    remap[keepmask] = np.arange(n_keep)
    nc = remap[cols_np]
    sel = nc >= 0
    M = sp.coo_matrix((np.ones(int(sel.sum())), (rows_np[sel], nc[sel])),
                      shape=(n_rows, n_keep), dtype=np.float64).tocsr()
    M.sum_duplicates()
    return M, n_keep


def build_typed_cooc(parsed, word_index, typed=True, min_count=CTX_MIN_COUNT):
    """word x context CSR. Column = (direction+deprel, filler) if typed else filler word (untyped
    ablation). Columns below min_count dropped."""
    def it():
        for tok, rel, filler, direction in _edges(parsed):
            if tok in word_index and filler in word_index:
                yield word_index[tok], ((direction + rel + "\t" + filler) if typed else filler)
    return _build_from_edges(it(), len(word_index), min_count)


def build_labelshuffle_cooc(parsed, word_index, rng, min_count=CTX_MIN_COUNT):
    """The KILLER info-free twin. Materialise every directed edge and SHUFFLE the deprel labels ACROSS
    edges -- preserving the label multiset, the edge count, the fillers and the directions, but
    destroying the edge<->label CORRESPONDENCE (which filler occupies which role). NOT a global
    bijection (that only permutes columns and is SVD-invariant); two true `nsubj:x` edges get DIFFERENT
    labels. If DEP_TYPED beats this, the win is the CORRECT grammar, not context sparsity.
    Memory-light: labels stored as an int16 id array, exactly shuffled (multiset preserved), streamed
    in the same deterministic _edges order for pass 2."""
    lab2id = {}
    ids = _arr("h")
    for tok, rel, filler, direction in _edges(parsed):
        if tok in word_index and filler in word_index:
            j = lab2id.get(rel)
            if j is None:
                j = len(lab2id); lab2id[rel] = j
            ids.append(j)
    id2lab = sorted(lab2id, key=lab2id.get)
    arr = np.frombuffer(ids, dtype=np.int16).copy()
    rng.shuffle(arr)
    def it():
        k = 0
        for tok, rel, filler, direction in _edges(parsed):
            if tok in word_index and filler in word_index:
                yield word_index[tok], direction + id2lab[arr[k]] + "\t" + filler
                k += 1
    return _build_from_edges(it(), len(word_index), min_count)


def build_random_tree_cooc(parsed, word_index, rng, min_count=CTX_MIN_COUNT):
    """Info-free twin: replace each sentence's tree with a random-parent tree + random deprel labels,
    same edge count. Uses the REAL deprel alphabet so column cardinality is comparable."""
    deprels = sorted({rel for s in parsed for (_t, _h, rel, _u) in s if rel not in ("punct", "ROOT", "root")})
    nd = len(deprels)
    def it():
        for s in parsed:
            n = len(s); toks = [t[0] for t in s]
            for i in range(n):
                parent = int(rng.integers(0, n))
                if parent == i:
                    continue
                rel = deprels[int(rng.integers(0, nd))]
                for a, b, d in ((i, parent, "+"), (parent, i, "-")):
                    if toks[a] in word_index and toks[b] in word_index:
                        yield word_index[toks[a]], d + rel + "\t" + toks[b]
    return _build_from_edges(it(), len(word_index), min_count)


def build_selpref_cooc(parsed, word_index, min_count=CTX_MIN_COUNT):
    """Verb selectional-preference: verb row x (arg-slot, filler) column, restricted to argument slots
    whose HEAD is a verb. The McRae event-schema / selectional-preference representation of verbs."""
    def it():
        for s in parsed:
            for tok, head, rel, _upos in s:
                base = rel.split(":")[0]
                if base in ARG_SLOTS and 0 <= head < len(s) and s[head][3] == "VERB":
                    verb = s[head][0]
                    if verb in word_index and tok in word_index:
                        yield word_index[verb], base + "\t" + tok
    return _build_from_edges(it(), len(word_index), min_count)


# --------------------------------------------------------------------------- online SGNS (BAR #2)
def sgns_window(sents, word_index, dim=SVD_K, window=2, neg=5, epochs=2, lr=0.025, seed=0):
    """Online skip-gram negative-sampling over the +/-window context. Demonstrates Levy-Goldberg:
    the online delta-rule predictor CONVERGES TO (ties, not beats) the batch PPMI-SVD on the SAME
    context. Operation: predict context word c from target t; error = label - sigmoid(u_t . v_c);
    update u_t, v_c by the gradient. Unigram^0.75 negative sampling, linear lr decay."""
    V = len(word_index)
    rng = np.random.default_rng(seed)
    U = (rng.standard_normal((V, dim)) * 0.01)
    Vv = np.zeros((V, dim))
    ids_sents = [[word_index[t] for t in s if t in word_index] for s in sents]
    freq = np.zeros(V)
    for s in ids_sents:
        for i in s:
            freq[i] += 1
    negp = np.power(freq, 0.75); negp = negp / max(negp.sum(), 1e-9)
    ntok = sum(len(s) for s in ids_sents)
    step = 0; total = max(epochs * ntok, 1)
    for _ep in range(epochs):
        for s in ids_sents:
            for pos, t in enumerate(s):
                a = lr * max(1.0 - step / total, 1e-4); step += 1
                lo = max(0, pos - window); hi = min(len(s), pos + window + 1)
                for cpos in range(lo, hi):
                    if cpos == pos:
                        continue
                    c = s[cpos]
                    negs = rng.choice(V, size=neg, p=negp)
                    targets = np.concatenate(([c], negs))
                    labels = np.zeros(neg + 1); labels[0] = 1.0
                    ut = U[t]
                    scores = Vv[targets] @ ut
                    g = (labels - 1.0 / (1.0 + np.exp(-scores)))
                    U[t] = ut + a * (g @ Vv[targets])
                    Vv[targets] = Vv[targets] + a * np.outer(g, ut)
    return U


# --------------------------------------------------------------------------- scoring
def score_arms(benches, arms, gate_floor_name, n_boot, n_null, seed, exclude_from_common=()):
    """Score every arm on each benchmark, on BOTH own-coverage and the common intersection across
    the CORE arms (excluding any arm named in exclude_from_common). Returns nested dict.
    BUGFIX (smoke, see report): SELPREF is a verb-only, argument-slot-restricted arm (by design,
    scored on SimVerb via its own coverage per the pre-reg). Including it in the cross-arm coverage
    AND collapses n_common to 0 for EVERY arm on EVERY benchmark whenever SELPREF's coverage is thin
    or empty (as at this smoke scale: 0 columns, 0 covered pairs) -- one restricted-domain arm was
    silently gating the whole comparison. exclude_from_common keeps SELPREF's own scoring intact
    while computing the shared common-coverage population from the arms that are meant to share it."""
    out = {}
    core = [nm for nm in arms if nm not in exclude_from_common]
    for bn, rows in benches.items():
        common = None
        for nm in core:
            cov = covered_pairs(rows, arms[nm])
            common = cov if common is None else (common & cov)
        common = common or set()
        res = {"n_common": len(common), "common_pairs": sorted(common), "arms": {}}
        for nm, fn in arms.items():
            res["arms"][nm] = {
                "common": score_arm(rows, fn, restrict_pairs=common, n_boot=n_boot, n_null=n_null, seed=seed),
                "own": score_arm(rows, fn, restrict_pairs=None, n_boot=n_boot, n_null=n_null, seed=seed),
            }
        out[bn] = res
    return out


def paired_delta(rows, common, fn_a, fn_b, n_boot, seed):
    """Paired bootstrap of Spearman rho(a) - rho(b) on the SAME common pairs. The CORRECT,
    higher-power test for a matched-population margin (cancels the shared variance) -- identical
    method to the baseline's own score_fusion. Comparing two arms' INDEPENDENT bootstrap CIs is
    far too conservative for a ~0.05 effect at n~1000. Returns delta, CI, and separated_above (CI
    lower bound > 0). Only pairs both arms cover are used."""
    A, B, G = [], [], []
    for k in common:
        w1, w2, g = rows[k][0], rows[k][1], rows[k][2]
        a = fn_a(w1, w2); b = fn_b(w1, w2)
        if a is None or b is None:
            continue
        A.append(a); B.append(b); G.append(g)
    if len(G) < 10:
        return None
    A, B, G = np.asarray(A), np.asarray(B), np.asarray(G)
    d0 = float(spearmanr(A, G).correlation - spearmanr(B, G).correlation)
    rng = np.random.default_rng(seed)
    n = len(G)
    ds = np.array([spearmanr(A[s], G[s]).correlation - spearmanr(B[s], G[s]).correlation
                   for s in (rng.integers(0, n, n) for _ in range(n_boot))])
    lo, hi = float(np.nanpercentile(ds, 2.5)), float(np.nanpercentile(ds, 97.5))
    return {"delta": round(d0, 4), "ci": [round(lo, 4), round(hi, 4)], "ci_half": round((hi - lo) / 2, 4),
            "n": int(n), "separated_above": bool(lo > 0), "separated_below": bool(hi < 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--tokens", type=int, default=None, help="override token budget")
    ap.add_argument("--sgns", action="store_true", help="also run the (slow) online SGNS BAR#2 arm")
    args = ap.parse_args()
    if args.mode == "smoke":
        max_tokens = args.tokens or 400_000
        vocab_cap, min_count, n_boot, n_null = 15_000, 3, 200, 200
    else:
        max_tokens = args.tokens or 10_000_000
        vocab_cap, min_count, n_boot, n_null = 60_000, 8, 500, 500
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, "parsed_simplewiki_%dtok.jsonl" % max_tokens)
    rng = np.random.default_rng(SEED)

    t0 = time.time()
    parse_and_cache(max_tokens, cache_path)
    parsed, ntok = load_parsed(cache_path, max_tokens)
    print("[load] %d sentences / %d tokens" % (len(parsed), ntok), flush=True)

    benches = {"simlex": load_simlex(), "simverb": load_simverb(), "wordsim": load_wordsim()}
    force = set().union(*(benchmark_vocab(r) for r in benches.values()))
    toks = token_sents(parsed)
    index = build_vocab(toks, force, vocab_cap, min_count)
    print("[vocab] %d words" % len(index), flush=True)

    # ---- build the context matrices (ONE variable: columns) ----
    def svd_of(M):
        return dense_vec_cosine_fn(svd_vectors(ppmi_matrix(M), seed=SEED), index)

    print("[build] window arms...", flush=True)
    cw2 = build_cooc(toks, index, 2)
    cw1 = build_cooc(toks, index, 1)
    print("[build] dependency arms...", flush=True)
    dep_typed, n_typed = build_typed_cooc(parsed, index, typed=True)
    dep_untyped, n_unt = build_typed_cooc(parsed, index, typed=False)
    # label-shuffle twin: reassign deprel labels ACROSS edges (breaks edge<->label correspondence,
    # preserves label multiset + edge count + fillers; NOT a global bijection, which is SVD-invariant)
    dep_shuf, n_shuf = build_labelshuffle_cooc(parsed, index, np.random.default_rng(SEED + 3))
    rand_tree, n_rt = build_random_tree_cooc(parsed, index, np.random.default_rng(SEED + 1))
    selpref, n_sp = build_selpref_cooc(parsed, index)
    print("[build] cols: typed=%d untyped=%d labelshuf=%d randtree=%d selpref=%d"
          % (n_typed, n_unt, n_shuf, n_rt, n_sp), flush=True)
    shuf_cooc = build_cooc(toks, index, 2, shuffle_seed=SEED + 7)

    arms = {
        "WIN2": svd_of(cw2),
        "WIN1": svd_of(cw1),
        "DEP_TYPED": svd_of(dep_typed),
        "DEP_UNTYPED": svd_of(dep_untyped),
        "SELPREF": svd_of(selpref),
        "DEP_LABELSHUF": svd_of(dep_shuf),
        "RAND_TREE": svd_of(rand_tree),
        "SHUF_CORPUS": svd_of(shuf_cooc),
        "RANDOM": random_vec_cosine_fn(index, seed=SEED),
        "ORTHO": ortho_sim_fn(),
    }
    if args.sgns:
        print("[build] online SGNS (BAR#2)...", flush=True)
        arms["ONLINE_SGNS_WIN2"] = dense_vec_cosine_fn(
            sgns_window(toks, index, window=2, epochs=2, seed=SEED), index)

    print("[score] scoring %d arms x 3 benches..." % len(arms), flush=True)
    scored = score_arms(benches, arms, "WIN1", n_boot, n_null, SEED, exclude_from_common={"SELPREF"})

    # ---- verdict: PAIRED-difference gate (the correct, higher-power test -- Delta-rho on the SAME
    # pairs, cancels the shared variance; comparing independent bootstrap CIs is far too conservative
    # for a ~0.05 effect at n~1000, and is what the incumbent's own score_fusion avoids) ----
    def rho(bn, nm):
        return scored[bn]["arms"].get(nm, {}).get("common", {}).get("rho")

    def pd(bn, a, b):
        return paired_delta(benches[bn], scored[bn]["common_pairs"], arms[a], arms[b], n_boot, SEED + 42)

    paired = {}
    verdict_bits = {}
    for bn in benches:
        r2, r1 = rho(bn, "WIN2") or -9, rho(bn, "WIN1") or -9
        strong_win = "WIN2" if r2 >= r1 else "WIN1"      # gate against the STRONGER window floor
        d = {"vs_WIN2": pd(bn, "DEP_TYPED", "WIN2"), "vs_WIN1": pd(bn, "DEP_TYPED", "WIN1"),
             "vs_DEP_UNTYPED": pd(bn, "DEP_TYPED", "DEP_UNTYPED"),
             "vs_DEP_LABELSHUF": pd(bn, "DEP_TYPED", "DEP_LABELSHUF"),
             "vs_RAND_TREE": pd(bn, "DEP_TYPED", "RAND_TREE"),
             "strongest_window_floor": strong_win}
        paired[bn] = d
        def _sep(key):
            return bool(d[key] and d[key]["separated_above"])
        vb = {"DEP_TYPED_beats_strongest_window(%s)" % strong_win: _sep("vs_" + strong_win),
              "DEP_TYPED_beats_LABELSHUF": _sep("vs_DEP_LABELSHUF"),
              "DEP_TYPED_beats_RANDTREE": _sep("vs_RAND_TREE"),
              "DEP_TYPED_beats_UNTYPED": _sep("vs_DEP_UNTYPED")}
        vb["pass"] = bool(_sep("vs_" + strong_win) and _sep("vs_DEP_LABELSHUF") and _sep("vs_RAND_TREE"))
        verdict_bits[bn] = vb
    n_pass = sum(1 for bn in benches if verdict_bits[bn]["pass"])
    passes = n_pass >= 2
    verdict = ("STRUCTURED_CONTEXT_BEATS_WINDOW_ON_SIMILARITY_AXIS_TWINS_LOSE_CISEP"
               if passes else "STRUCTURED_CONTEXT_DOES_NOT_BEAT_WINDOW_CISEP__SEE_PAIRED_DELTAS")

    for bn in benches:
        line = " ".join("%s=%s" % (nm, ("%.4f" % rho(bn, nm)) if rho(bn, nm) is not None else "NA")
                        for nm in arms)
        print("[%s] n_common=%d | %s" % (bn, scored[bn]["n_common"], line), flush=True)
        d = paired[bn]
        print("     paired vs %s: %s | vs LABELSHUF: %s | vs RANDTREE: %s | vs UNTYPED: %s | pass=%s"
              % (d["strongest_window_floor"], d["vs_" + d["strongest_window_floor"]],
                 d["vs_DEP_LABELSHUF"], d["vs_RAND_TREE"], d["vs_DEP_UNTYPED"], verdict_bits[bn]["pass"]), flush=True)

    # ---- BAR #2: the online rule CONVERGES TO (ties, not beats) batch on the SAME context. A TIE =
    # paired Delta-rho(SGNS - batch WIN2) CI INCLUDES 0. Empirically confirms Levy-Goldberg on our
    # corpus: the update rule (online vs batch) is not the lever; the context shape is. ----
    bar2 = None
    if "ONLINE_SGNS_WIN2" in arms:
        bar2 = {}
        for bn in benches:
            dd = pd(bn, "ONLINE_SGNS_WIN2", "WIN2")
            bar2[bn] = dd
            tie = bool(dd and not dd["separated_above"] and not dd["separated_below"])
            print("[BAR2 online==batch] %s: SGNS_rho=%.4f WIN2_rho=%.4f delta=%s TIE=%s"
                  % (bn, rho(bn, "ONLINE_SGNS_WIN2") or -9, rho(bn, "WIN2") or -9, dd, tie), flush=True)

    metrics = {
        "anchor_name": ANCHOR, "mode": args.mode, "n_tokens": ntok, "vocab": len(index),
        "verdict": verdict, "n_pops_pass": n_pass,
        "context_cols": {"typed": n_typed, "untyped": n_unt, "labelshuf": n_shuf,
                         "randtree": n_rt, "selpref": n_sp},
        "config": {"ppmi_alpha": PPMI_ALPHA, "svd_k": SVD_K, "svd_p": SVD_P, "ctx_min_count": CTX_MIN_COUNT,
                   "vocab_cap": vocab_cap, "min_count": min_count, "n_boot": n_boot, "n_null": n_null,
                   "seed": SEED, "parser": "spacy_en_core_web_sm"},
        "scored": scored, "paired_deltas": paired, "verdict_bits": verdict_bits,
        "bar2_sgns_vs_batch": bar2, "elapsed_s": round(time.time() - t0, 1),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print("[verdict] %s (DEP_TYPED passes strict gate on %d/3 pops) | %.0fs"
          % (verdict, n_pass, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
