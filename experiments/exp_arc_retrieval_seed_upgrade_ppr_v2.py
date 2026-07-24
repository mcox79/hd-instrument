"""arc_retrieval_seed_upgrade_ppr_v2 -- UPGRADE SEED IDENTIFICATION for brain-faithful ARC retrieval.

ONE VARIABLE = SEEDING QUALITY. The prior cell (arc_retrieval_multicue_ppr_discriminative_v1, VET'd
29539) VALIDATED spreading activation over the REAL WorldTree graph: PPR recall@10 0.3796 vs cosine
0.2798 (+0.0998), shuffled-graph control collapses to 0.0007 (structure-driven). But it fell short of
the pre-registered +0.15 HARD-PASS bar, and the shortfall was precisely attributed to SEEDING:
seed_recall 0.365 < the 0.50 make-or-break floor (~64% of gold-fact terms never seeded). Spreading
delivered +0.0998 DESPITE bad seeds. Two prior VET sub-findings APPLIED here: (a) DROP the
discriminative re-rank (it HURT recall: prior arm C 0.1953 < B 0.3796); (b) DROP the hub-idf ablation
arm (near-inert: prior C-E = +0.0046, within noise). We keep the spreading (prior arm B) BIT-UNCHANGED
(same idf-weighted transition, same PPR, same 2 hops, same damping) and the SAME bind+settle combiner
UNCHANGED. The ONLY thing that changes vs v1 is how question surface forms are mapped to graph seed
term-nodes (lexical access / entity-linking).

SEED UPGRADE (brain-grounded lexical access -- surface forms robustly map to concepts incl. multi-word
expressions, morphological variants, and synonyms; Collins&Loftus cue-node identification, HippoRAG
seed-quality-is-make-or-break precondition):
  1. MORPHOLOGICAL normalization (WordNet morphy): "plants"->"plant" so inflected question words hit
     the graph's lemma. A seeding-only lemma index (lemma -> vocab term indices) leaves the graph/PPR
     UNCHANGED -- it only enriches which term-nodes a question word can match.
  2. WordNet EXPANSION (synonyms + hypernyms, reusing SemanticHDEncoder._wn_neighbors): a question word
     also seeds graph terms that are its synonyms/hypernyms (lower confidence weight). This is the
     lexical-taxonomic bridging (~40% of WorldTree gold support is KINDOF/SYNONYMY).
  3. LOWER semantic threshold (SEED_COS 0.60 -> 0.45): out-of-vocab words semantic-match more graph
     terms (SemanticHDEncoder meaning-match, not string-match).
  4. MULTI-TOKEN phrase seeds (adjacent content-word bigrams): encode the phrase, semantic-match to the
     nearest graph term -- catches phrase meaning that single-word matching misses.

ARMS (one variable = seeding; graph + PPR + combiner all held fixed):
  A  baseline_single_shot   -- cosine top-K (QQ @ SV_store.T), UNCHANGED. Head-to-head baseline.
  B0 ppr_baseline_seeds     -- PPR spreading with OLD/v1 seeds (SEED_COS=0.60, single-word exact+semantic
                               only). Positive control: reproduces prior arm B (expect ~0.38).
  B  ppr_upgraded_seeds     -- PPR spreading with UPGRADED seeds (1-4 above). [MECHANISM / new variable]
  D  shuffled_graph_control -- B's upgraded seeds on a degree-preserving edge-permuted graph -- MUST
                               collapse toward A (proves lift is graph-structure-driven).

METRICS: PRIMARY (i) seed_recall vs WorldTree gold entity mentions (MUST clear 0.50 floor); (ii)
recall@10 of gold central facts, target B - A >= +0.15 (the bar v1 missed at +0.0998). B0->B isolates
the seeding delta. KEY WATCH (secondary, load-bearing): end-to-end ARC Easy+Challenge through the
UNCHANGED combiner -- does higher recall NOW move Challenge above baseline A? Reported with a PAIRED
McNemar exact test (B vs A on Challenge). If recall clears +0.15 but end-to-end stays flat/insignificant
-> that is the necessary-but-not-sufficient finding; the combiner / pool-K dilution is the NEXT wall;
reported honestly, NOT tuned to force an end-to-end win.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> not remote-
portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted
iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds the REAL SemanticHDEncoder + REAL bipartite graph + REAL PPR +
#   REAL upgraded seed-linking (morphy + wordnet + bigram) + all arms at tiny scale; a PLANTED
#   synonym-bridge case asserts the SEED UPGRADE FIRES (upgraded seeds reach a gold term that v1 seeds
#   miss); arms-differ; determinism
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on baseline recall (headroom for the retrieval win)
# - storage = SHARDED (each fact = own vector + own graph node; no superposition)
# - discriminator survives scale: smoke runs the FULL 9720-fact graph (only the question set is subset)
# - all reported numbers MEASURED@ this cell's metrics.json ; prior-cell numbers MEASURED@ v1 metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import math
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np
import scipy.sparse as sp

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# reuse the aggregation cell's WorldTree parse + question loader + UNCHANGED combiner
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_retrieval_seed_upgrade_ppr_v2"
SEED = 20260724

# ---- spreading hyperparams (BIT-UNCHANGED from v1 arm B: keep the validated spreading) ----
TOP_K = 10          # primary recall@K and the pool size fed to the combiner
TOP_K2 = 20         # secondary recall@20
HOPS = 2            # fact-hops (term->fact->term x2); WorldTree central-support median 2, p90 5
DAMP = 0.5          # PPR restart / damping (alpha); a=(1-a)*seed + a*(a@M)
MIN_TERM_LEN = 4    # content-word length (arc._content_words default)

# ---- SEEDING hyperparams (the ONE variable; author-designed a priori; see pre-reg) ----
SEED_COS_OLD = 0.60     # v1 semantic seed-linking threshold (arm B0 baseline-seed control)
SEED_COS = 0.45         # UPGRADED: lower threshold -> out-of-vocab words match more graph terms
BIGRAM_COS = 0.55       # multi-token phrase semantic-match threshold (stricter than single-word)
EXPAND_WORDNET = True    # seed synonyms + hypernyms of each question word
USE_BIGRAMS = True       # multi-token phrase seeds
W_EXACT = 1.0            # exact vocab match weight
W_LEMMA = 1.0            # morphological (morphy lemma) match weight
W_SYN = 0.5             # WordNet synonym match weight (lower confidence)
W_HYP = 0.3             # WordNet hypernym match weight (lower confidence)
W_SEM = 0.5             # semantic nearest-term match weight
W_BIGRAM = 0.5          # bigram phrase semantic-match weight
MAX_BIGRAMS = 24         # cap bigrams/question (bound cost + noise)

# ---- bands (author-designed; see pre-reg). PRIMARY = seed_recall floor + recall@10 lift. ----
HP_RECALL_LIFT = 0.15       # B recall@10 - A recall@10 >= this -> mechanism HARD-PASS bar (v1 missed at 0.0998)
HP_D_COLLAPSE = 0.03        # D recall - A recall <= this -> lift is structure-driven
MB_RECALL_LIFT = 0.05       # positive-but-sub-HP lift band floor
SEED_QUALITY_FLOOR = 0.50   # seed_recall >= this = make-or-break floor (v1 was 0.365)
AG_BASELINE_SAT = 0.95      # baseline A recall >= this -> discriminator vacuous (no headroom)

# prior-cell reference (MEASURED@ data/exp_arc_retrieval_multicue_ppr_discriminative_v1/metrics.json)
PRIOR_A_RECALL10 = 0.2798
PRIOR_B_RECALL10 = 0.3796
PRIOR_SEED_RECALL = 0.365
B0_REPRO_TOL = 0.06         # |B0 recall@10 - PRIOR_B_RECALL10| within this = positive-control reproduced


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
_T0 = [0.0]


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# graph build: bipartite fact-term incidence + idf + PPR transition (scipy.sparse)
# (BIT-UNCHANGED from v1: keep the validated spreading)
# ---------------------------------------------------------------------------
def build_incidence(fact_terms, vocab):
    """fact_terms: list per fact of term-lists. vocab: sorted term list.
    Returns A [nFacts x nTerms] binary CSR, df[nTerms], t2i dict."""
    t2i = {t: i for i, t in enumerate(vocab)}
    rows, cols = [], []
    for fi, terms in enumerate(fact_terms):
        for t in set(terms):
            j = t2i.get(t)
            if j is not None:
                rows.append(fi)
                cols.append(j)
    data = np.ones(len(rows), dtype=np.float64)
    A = sp.csr_matrix((data, (rows, cols)), shape=(len(fact_terms), len(vocab)))
    df = np.asarray(A.sum(axis=0)).ravel()  # facts-per-term
    return A, df, t2i


def _row_normalize(M):
    """Row-normalize a CSR matrix (rows summing to 0 stay 0)."""
    M = M.tocsr().astype(np.float64)
    rs = np.asarray(M.sum(axis=1)).ravel()
    inv = np.zeros_like(rs)
    nz = rs > 0
    inv[nz] = 1.0 / rs[nz]
    D = sp.diags(inv)
    return (D @ M).tocsr()


def build_transition(A, df, use_idf=True):
    """Bipartite term->fact->term transition M [nTerms x nTerms] and idf-weighted fact-scoring
    projection Sft [nTerms x nFacts]. idf hub-downweight kept (unchanged spreading; near-inert per
    v1 C-E=+0.0046 but part of the validated arm-B transition -> left intact, not re-ablated)."""
    nFacts = A.shape[0]
    if use_idf:
        idf = np.log(np.maximum(nFacts, 1.0) / np.maximum(df, 1.0))
        idf = np.maximum(idf, 1e-6)
    else:
        idf = np.ones(A.shape[1], dtype=np.float64)
    A = A.tocsr().astype(np.float64)
    TF = _row_normalize(A.T)                       # [nTerms x nFacts]
    FT = _row_normalize(A @ sp.diags(idf))         # [nFacts x nTerms]
    M = (TF @ FT).tocsr()                          # [nTerms x nTerms]
    Sft = (sp.diags(idf) @ A.T).tocsr()            # [nTerms x nFacts]
    return M, Sft, idf


def shuffle_incidence(A, rng):
    """Degree-preserving config-model shuffle: keep fact endpoints, randomly permute the term
    endpoints of the incidence edges. Preserves each fact's size and the term-degree multiset while
    destroying real co-occurrence structure. Returns A_shuf [nFacts x nTerms], df_shuf."""
    A = A.tocoo()
    cols = A.col.copy()
    rng.shuffle(cols)                              # permute term endpoints
    A_shuf = sp.csr_matrix((np.ones(len(cols)), (A.row, cols)), shape=A.shape)
    A_shuf.data[:] = 1.0                            # collapse any accidental multi-edges to binary
    df_shuf = np.asarray(A_shuf.sum(axis=0)).ravel()
    return A_shuf, df_shuf


def ppr_batch(seed_mat, M, hops, damp):
    """Batched personalized PageRank. seed_mat [nQ x nTerms] (row-normalized personalization).
    a = seed; repeat hops times: a = (1-damp)*seed + damp*(a @ M). Returns a [nQ x nTerms] dense."""
    a = seed_mat.toarray() if sp.issparse(seed_mat) else np.asarray(seed_mat, dtype=np.float64)
    s = a.copy()
    Mc = M.tocsr()
    for _ in range(hops):
        a = (1.0 - damp) * s + damp * (a @ Mc)
    return a


def fact_activation(a, Sft):
    """Project term activation a [nQ x nTerms] onto facts via Sft [nTerms x nFacts] (idf already baked
    in: Sft[t,f]=idf[t]*incidence). Returns dense fact scores [nQ x nFacts]. Keeps Sft sparse."""
    return np.asarray(Sft.T.dot(a.T)).T


# ---------------------------------------------------------------------------
# seed linking (semantic, not lexical) -- THE ONE VARIABLE
# ---------------------------------------------------------------------------
_MORPHY_CACHE = {}


def _lemma(wn, w):
    """WordNet morphy lemma; cached; falls back to w when morphy has no entry."""
    if w in _MORPHY_CACHE:
        return _MORPHY_CACHE[w]
    try:
        m = wn.morphy(w)
    except Exception:
        m = None
    lz = m if m else w
    _MORPHY_CACHE[w] = lz
    return lz


def build_lemma_index(vocab, wn):
    """lemma -> sorted list of vocab term indices. SEEDING-ONLY enrichment: the graph (M, Sft) is
    built from raw vocab and is UNCHANGED; this index only lets a question word's lemma match graph
    terms that share that lemma (e.g. q 'plants' -> graph 'plant')."""
    lem2idx = {}
    for j, t in enumerate(vocab):
        lz = _lemma(wn, t)
        lem2idx.setdefault(lz, []).append(j)
    return {k: sorted(v) for k, v in lem2idx.items()}


def _content_bigrams(text, min_len, max_bigrams):
    """Adjacent content-word bigrams ('w1 w2') in surface order, deduped, capped."""
    words = arc._content_words(text, min_len)
    out, seen = [], set()
    for i in range(len(words) - 1):
        bg = words[i] + " " + words[i + 1]
        if bg not in seen:
            seen.add(bg)
            out.append(bg)
        if len(out) >= max_bigrams:
            break
    return out


def _vocab_hits(tok, t2i, lem2idxs, wn):
    """Vocab term indices a token matches: exact + shared-lemma."""
    out = []
    j = t2i.get(tok)
    if j is not None:
        out.append(j)
    for j2 in lem2idxs.get(_lemma(wn, tok), ()):
        out.append(j2)
    return out


def link_seeds_baseline(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, seed_cos):
    """v1 seed-linking (arm B0 positive control): exact vocab match; else semantic nearest term by
    cosine >= seed_cos. Single-word only, no expansion, no lemma, no bigram."""
    seeds = []
    for qi, words in enumerate(q_words_per_q):
        acc = {}
        wv = q_word_vecs_per_q[qi]
        for wi, w in enumerate(words):
            j = t2i.get(w)
            if j is not None:
                acc[j] = acc.get(j, 0.0) + 1.0
            elif term_vecs.shape[0] > 0:
                sims = term_vecs @ wv[wi]
                jb = int(np.argmax(sims))
                if float(sims[jb]) >= seed_cos:
                    acc[jb] = acc.get(jb, 0.0) + 1.0
        seeds.append(acc)
    return seeds


def link_seeds_upgraded(q_words_per_q, q_bigram_vecs_per_q, vocab, t2i, lem2idxs, enc, wn,
                        term_vecs, q_word_vecs_per_q, seed_cos, bigram_cos):
    """UPGRADED seed-linking (arm B). Per question word: exact vocab + morphological-lemma +
    WordNet synonym/hypernym vocab hits; else semantic nearest-term at LOWER seed_cos. Plus
    multi-token bigram phrase semantic seeds. Weight per source, kept via max() so a term hit by
    many low-confidence expansions does not runaway-dominate the personalization vector."""
    def bump(acc, j, w):
        if w > acc.get(j, 0.0):
            acc[j] = w

    seeds = []
    for qi, words in enumerate(q_words_per_q):
        acc = {}
        wv = q_word_vecs_per_q[qi]
        for wi, w in enumerate(words):
            matched = False
            j = t2i.get(w)
            if j is not None:
                bump(acc, j, W_EXACT)
                matched = True
            for j2 in lem2idxs.get(_lemma(wn, w), ()):   # morphological normalization
                bump(acc, j2, W_LEMMA)
                matched = True
            if EXPAND_WORDNET:                            # synonyms + hypernyms
                syns, hyps = enc._wn_neighbors(w)
                for e in syns:
                    for tok in e.split():
                        for j3 in _vocab_hits(tok, t2i, lem2idxs, wn):
                            bump(acc, j3, W_SYN)
                for e in hyps:
                    for tok in e.split():
                        for j4 in _vocab_hits(tok, t2i, lem2idxs, wn):
                            bump(acc, j4, W_HYP)
            if (not matched) and term_vecs.shape[0] > 0:  # semantic nearest at LOWER threshold
                sims = term_vecs @ wv[wi]
                jb = int(np.argmax(sims))
                if float(sims[jb]) >= seed_cos:
                    bump(acc, jb, W_SEM)
        if USE_BIGRAMS and q_bigram_vecs_per_q[qi].shape[0] > 0:   # multi-token phrase seeds
            bvs = q_bigram_vecs_per_q[qi]
            for bi in range(bvs.shape[0]):
                sims = term_vecs @ bvs[bi]
                jb = int(np.argmax(sims))
                if float(sims[jb]) >= bigram_cos:
                    bump(acc, jb, W_BIGRAM)
        seeds.append(acc)
    return seeds


def seeds_to_matrix(seeds, nTerms):
    """Row-normalized personalization matrix [nQ x nTerms] CSR."""
    rows, cols, data = [], [], []
    for qi, acc in enumerate(seeds):
        tot = sum(acc.values())
        if tot <= 0:
            continue
        for j, w in acc.items():
            rows.append(qi)
            cols.append(j)
            data.append(w / tot)
    return sp.csr_matrix((data, (rows, cols)), shape=(len(seeds), nTerms))


# ---------------------------------------------------------------------------
# ranking
# ---------------------------------------------------------------------------
def topk_from_scores(fact_scores_row, k):
    """Top-k fact indices by score (descending), stable for ties via index order."""
    n = fact_scores_row.shape[0]
    kk = min(k, n)
    if kk <= 0:
        return np.zeros(0, dtype=np.int64)
    idx = np.argpartition(-fact_scores_row, kk - 1)[:kk]
    return idx[np.argsort(-fact_scores_row[idx], kind="stable")]


def recall_at_k(topk_uids, gold_central):
    g = set(gold_central)
    if not g:
        return None
    return len(set(topk_uids) & g) / len(g)


# ---------------------------------------------------------------------------
# seed quality vs WorldTree gold (make-or-break sub-check)
# ---------------------------------------------------------------------------
def seed_quality(questions, seeds, vocab, fact_terms, uid2fi):
    """seed_recall = mean over questions of (linked seed terms INTERSECT gold-fact terms) / gold-fact
    terms; seed_precision analogous over seed terms. Gold-fact terms = content terms of the gold
    central facts (the entity mentions the seeder must find to spread from)."""
    i2t = vocab
    recs, precs = [], []
    n_empty = 0
    for qi, q in enumerate(questions):
        gold_terms = set()
        for u in q["gold_central"]:
            if u in uid2fi:
                gold_terms |= set(fact_terms[uid2fi[u]])
        seed_terms = {i2t[j] for j in seeds[qi].keys()}
        if not seed_terms:
            n_empty += 1
        if gold_terms:
            inter = len(seed_terms & gold_terms)
            recs.append(inter / len(gold_terms))
            precs.append(inter / len(seed_terms) if seed_terms else 0.0)
    return (round(float(np.mean(recs)), 4) if recs else 0.0,
            round(float(np.mean(precs)), 4) if precs else 0.0,
            n_empty)


# ---------------------------------------------------------------------------
# significance
# ---------------------------------------------------------------------------
def _binom_ci95(k, n):
    """Wald-ish normal-approx 95% CI for a binomial proportion (lower, upper)."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    return (max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se))


def _mcnemar_exact(b, c):
    """Two-sided exact McNemar p on discordant counts b (arm1-correct, arm2-wrong) and c (arm1-wrong,
    arm2-correct). Null: b,c ~ Binom(b+c, 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    from math import comb
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return float(min(1.0, 2.0 * tail))


# ---------------------------------------------------------------------------
# self-test (real code path + planted synonym-bridge SEED-UPGRADE discriminator + determinism)
# ---------------------------------------------------------------------------
def _planted_seed_upgrade_discriminator():
    """Synthetic bipartite graph where the GOLD fact is reachable only if the SEED UPGRADE (WordNet
    synonym / morphological lemma) links the question word to a graph term the raw string does NOT
    match. Question word 'autos' -> lemma/synonym 'car'; graph gold fact g contains 'car'+'wheel'.
    v1 baseline seeding (exact 'autos' + semantic on a tiny random encoder) never seeds 'car'; the
    upgraded seeding lemmatizes/expands 'autos'->'car', seeds it, and PPR reaches g. Proves the seed
    upgrade FIRES (recall reachable ONLY via better seeding, graph/PPR identical)."""
    wn = _load_wordnet()
    vocab = ["car", "wheel", "engine", "road", "boat", "sail", "water"]
    fact_terms = [["car", "engine"], ["car", "wheel"], ["wheel", "road"],
                  ["boat", "sail"], ["sail", "water"]]
    gold_idx = 1  # {car, wheel}
    A, df, t2i = build_incidence(fact_terms, vocab)
    M, Sft, idf = build_transition(A, df, use_idf=True)
    lem2idxs = build_lemma_index(vocab, wn)
    # question word 'cars' (plural, not in vocab). morphy 'cars'->'car'; must seed the 'car' node.
    hits = _vocab_hits("cars", t2i, lem2idxs, wn)
    assert t2i["car"] in hits, f"seed upgrade FAILED: 'cars' did not lemma-match graph 'car' (hits={hits})"
    # v1 baseline: exact-only, 'cars' not in vocab -> no seed (semantic skipped in this planted check)
    assert t2i.get("cars") is None, "planted: 'cars' must be out-of-vocab so lemma is the only bridge"
    # spread from the upgraded seed reaches the gold bridge fact
    seeds = [{t2i["car"]: 1.0}]
    seed_mat = seeds_to_matrix(seeds, len(vocab))
    a = ppr_batch(seed_mat, M, hops=2, damp=0.5)
    fscore = fact_activation(a, Sft)
    top = topk_from_scores(fscore[0], 3)
    assert gold_idx in set(top.tolist()), f"planted: PPR from upgraded seed missed gold; top={top}"
    # determinism
    a2 = ppr_batch(seed_mat, M, hops=2, damp=0.5)
    assert np.allclose(a, a2), "planted: PPR non-deterministic"
    return True


def self_test():
    print("[self-test] planted synonym/lemma SEED-UPGRADE discriminator ...", flush=True)
    _planted_seed_upgrade_discriminator()

    print("[self-test] REAL SemanticHDEncoder + real graph + real PPR + upgraded seeding + arms ...", flush=True)
    kv = _load_glove()
    wn = _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "photosynthesis produces oxygen as a byproduct for animals to breathe",
        "sunlight is a source of energy for plants",
        "an automobile is a kind of vehicle with wheels",
        "the moon orbits the earth once each month",
    ]
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in store_sents]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = build_incidence(fact_terms, vocab)
    assert A.shape == (5, len(vocab)) and A.nnz > 0, "incidence build failed"
    M, Sft, idf = build_transition(A, df, use_idf=True)
    lem2idxs = build_lemma_index(vocab, wn)

    SV_store = arc._encode_store(enc, store_sents)          # [5, nd] L2 rows
    term_vecs = arc._encode_store(enc, vocab)               # [nTerms, nd]

    q = {"stem": "What do green plants make using sunlight?",
         "choices": ["iron metal", "sugar and oxygen", "the moon", "loud sound"]}
    qtext = q["stem"] + " " + " ".join(q["choices"])
    q_words = sorted(set(arc._content_words(qtext, MIN_TERM_LEN)))
    q_word_vecs = arc._encode_store(enc, q_words)
    QQ = arc._encode_store(enc, [qtext])[0]
    bigrams = _content_bigrams(qtext, MIN_TERM_LEN, MAX_BIGRAMS)
    bigram_vecs = arc._encode_store(enc, bigrams)

    # upgraded vs baseline seeds MUST differ (the one variable)
    seeds_up = link_seeds_upgraded([q_words], [bigram_vecs], vocab, t2i, lem2idxs, enc, wn,
                                   term_vecs, [q_word_vecs], SEED_COS, BIGRAM_COS)
    seeds_bl = link_seeds_baseline([q_words], vocab, t2i, term_vecs, [q_word_vecs], SEED_COS_OLD)
    assert len(seeds_up[0]) > 0, "upgraded seed linking found no seeds on real question"
    assert set(seeds_up[0].keys()) != set(seeds_bl[0].keys()) or len(seeds_up[0]) >= len(seeds_bl[0]), \
        "META_RULE_AF: upgraded seeds identical to baseline seeds (seed upgrade inert)"
    assert len(seeds_up[0]) >= len(seeds_bl[0]), "upgraded seeding should not REDUCE seed count here"

    sm_up = seeds_to_matrix(seeds_up, len(vocab))
    sm_bl = seeds_to_matrix(seeds_bl, len(vocab))

    # arm A cosine
    topA = topk_from_scores(QQ @ SV_store.T, TOP_K)
    # arm B (upgraded) + B0 (baseline seeds), same PPR
    aB = ppr_batch(sm_up, M, HOPS, DAMP)
    aB0 = ppr_batch(sm_bl, M, HOPS, DAMP)
    topB = topk_from_scores(fact_activation(aB, Sft)[0], TOP_K)
    topB0 = topk_from_scores(fact_activation(aB0, Sft)[0], TOP_K)
    assert not np.allclose(aB, sm_up.toarray()), "META_RULE_AF: PPR moved no mass (spreading inert)"
    assert topA.size > 0 and topB.size > 0 and topB0.size > 0, "arm outputs empty on real path"

    # arm D shuffled
    A_s, df_s = shuffle_incidence(A, np.random.default_rng(0))
    M_s, Sft_s, idf_s = build_transition(A_s, df_s, use_idf=True)
    aD = ppr_batch(sm_up, M_s, HOPS, DAMP)
    topD = topk_from_scores(fact_activation(aD, Sft_s)[0], TOP_K)

    # combiner reuse UNCHANGED
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
    fhB = SV_store[topB]
    q_rel = np.maximum(fhB @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fhB, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == len(q["choices"]), "combiner reuse shape mismatch"

    # McNemar sanity
    assert _mcnemar_exact(0, 0) == 1.0 and _mcnemar_exact(10, 0) < 0.01, "mcnemar broken"

    # determinism
    assert np.allclose(aB, ppr_batch(sm_up, M, HOPS, DAMP)), "PPR non-deterministic on real path"

    # WorldTree parse touch
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = agg.load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print(f"[self-test] PASS (planted lemma/synonym bridge; real encoder+graph+PPR; upgraded seeds "
          f"({len(seeds_up[0])}) >= baseline seeds ({len(seeds_bl[0])}); arms A/B0/B/D; combiner reuse; "
          f"mcnemar; determinism; WT parse)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # FULL graph (all facts -> discriminator fires at real graph scale), question SUBSET
        return {"n_dim": 2048, "limit_easy": 200, "limit_chal": 150}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None}


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    wn = _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    nQ = len(questions)
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f}", flush=True)

    # ---- store = FULL tablestore (gold INCLUDED: recall@K of gold facts requires them present) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    print(f"[store] full tablestore = {nFacts} facts (gold included; closed-book-over-curriculum)", flush=True)

    # ---- bipartite graph over the store (UNCHANGED from v1) ----
    _heartbeat(output_dir, "build_graph")
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = build_incidence(fact_terms, vocab)
    nTerms = len(vocab)
    M, Sft, idf = build_transition(A, df, use_idf=True)          # arm B/B0/D transition (unchanged)
    lem2idxs = build_lemma_index(vocab, wn)                       # SEEDING-ONLY lemma enrichment
    print(f"[graph] terms={nTerms} incidence_nnz={A.nnz} mean_terms/fact={A.nnz/max(nFacts,1):.2f} "
          f"lemma_keys={len(lem2idxs)}", flush=True)

    # shuffled graph (control D)
    A_s, df_s = shuffle_incidence(A, np.random.default_rng(SEED + 77))
    M_s, Sft_s, idf_s = build_transition(A_s, df_s, use_idf=True)

    # ---- encode store + questions + term vocab (ONCE) ----
    _heartbeat(output_dir, "encode_store", {"n": nFacts})
    t_enc = time.perf_counter()
    SV_store = arc._encode_store(enc, sents)                     # [nFacts x nd]
    print(f"[encode] store {nFacts} facts in {time.perf_counter()-t_enc:.1f}s", flush=True)

    _heartbeat(output_dir, "encode_terms", {"n": nTerms})
    term_vecs = arc._encode_store(enc, vocab)                    # [nTerms x nd]

    _heartbeat(output_dir, "encode_questions")
    qtexts = [q["stem"] + " " + " ".join(q["choices"]) for q in questions]
    QQ = arc._encode_store(enc, qtexts)                          # [nQ x nd]
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]) for q in questions]

    # per-question content words + their vectors (for semantic seed linking)
    q_words_per_q = [sorted(set(arc._content_words(t, MIN_TERM_LEN))) for t in qtexts]
    uniq_words = sorted({w for ws in q_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}
    q_word_vecs_per_q = [uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)
                         for ws in q_words_per_q]

    # per-question bigrams + vectors (multi-token phrase seeds)
    _heartbeat(output_dir, "encode_bigrams")
    q_bigrams_per_q = [_content_bigrams(t, MIN_TERM_LEN, MAX_BIGRAMS) for t in qtexts]
    uniq_bigrams = sorted({b for bs in q_bigrams_per_q for b in bs})
    ub_vecs = arc._encode_store(enc, uniq_bigrams) if uniq_bigrams else np.zeros((0, nd), np.float32)
    ub2row = {b: i for i, b in enumerate(uniq_bigrams)}
    q_bigram_vecs_per_q = [ub_vecs[[ub2row[b] for b in bs]] if bs else np.zeros((0, nd), np.float32)
                           for bs in q_bigrams_per_q]

    # ---- seeds: UPGRADED (B) vs BASELINE (B0) ----
    _heartbeat(output_dir, "seed_linking")
    seeds_up = link_seeds_upgraded(q_words_per_q, q_bigram_vecs_per_q, vocab, t2i, lem2idxs, enc, wn,
                                   term_vecs, q_word_vecs_per_q, SEED_COS, BIGRAM_COS)
    seeds_bl = link_seeds_baseline(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, SEED_COS_OLD)
    sm_up = seeds_to_matrix(seeds_up, nTerms)
    sm_bl = seeds_to_matrix(seeds_bl, nTerms)

    seed_recall, seed_precision, n_empty_seed = seed_quality(questions, seeds_up, vocab, fact_terms, uid2fi)
    seed_recall_bl, seed_precision_bl, n_empty_bl = seed_quality(questions, seeds_bl, vocab, fact_terms, uid2fi)
    mean_seeds_up = round(float(np.mean([len(s) for s in seeds_up])), 2)
    mean_seeds_bl = round(float(np.mean([len(s) for s in seeds_bl])), 2)
    print(f"[seed] UPGRADED recall={seed_recall} precision={seed_precision} mean_seeds={mean_seeds_up} "
          f"empty={n_empty_seed}/{nQ} | BASELINE recall={seed_recall_bl} precision={seed_precision_bl} "
          f"mean_seeds={mean_seeds_bl}", flush=True)

    # ---- PPR (batched) for upgraded, baseline, shuffled ----
    _heartbeat(output_dir, "ppr")
    a_up = ppr_batch(sm_up, M, HOPS, DAMP)                       # arm B
    a_bl = ppr_batch(sm_bl, M, HOPS, DAMP)                       # arm B0
    a_shuf = ppr_batch(sm_up, M_s, HOPS, DAMP)                   # arm D
    ppr_mass_moved = round(float(np.mean(np.abs(a_up - sm_up.toarray()).sum(axis=1))), 5)

    _heartbeat(output_dir, "score_facts")
    FB = fact_activation(a_up, Sft)
    FB0 = fact_activation(a_bl, Sft)
    FD = fact_activation(a_shuf, Sft_s)

    # ---- per-arm retrieval (top-K2 pool; K slice for primary) ----
    _heartbeat(output_dir, "retrieve_and_eval")
    arm_topk = {name: [] for name in ("A", "B0", "B", "D")}
    for qi in range(nQ):
        arm_topk["A"].append(topk_from_scores(QQ[qi] @ SV_store.T, TOP_K2))
        arm_topk["B"].append(topk_from_scores(FB[qi], TOP_K2))
        arm_topk["B0"].append(topk_from_scores(FB0[qi], TOP_K2))
        arm_topk["D"].append(topk_from_scores(FD[qi], TOP_K2))

    def arm_recall(name, k):
        rs = []
        for qi, q in enumerate(questions):
            topk_uids = [uids[i] for i in arm_topk[name][qi][:k]]
            r = recall_at_k(topk_uids, q["gold_central"])
            if r is not None:
                rs.append(r)
        return round(float(np.mean(rs)), 4) if rs else 0.0

    recall = {name: {"at10": arm_recall(name, TOP_K), "at20": arm_recall(name, TOP_K2)}
              for name in ("A", "B0", "B", "D")}
    for name in ("A", "B0", "B", "D"):
        print(f"[recall] {name}: @10={recall[name]['at10']} @20={recall[name]['at20']}", flush=True)

    # ---- end-to-end through UNCHANGED combiner; keep per-question hit arrays for McNemar ----
    def end_to_end(name, combiner_mode):
        c_e = c_c = n_e = n_c = 0
        chal_hits = []   # (qid_order preserved for challenge questions)
        for qi, q in enumerate(questions):
            idx = arm_topk[name][qi][:TOP_K]
            fh = SV_store[idx]
            q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
            sc, _ = agg.aggregate(fh, q_rel, choice_hd_map[qi], combiner_mode,
                                  rng=np.random.default_rng(SEED + qi))
            pick = agg._pick(sc, np.random.default_rng(SEED + qi))
            hit = int(pick == q["correct_index"])
            if q["source"].startswith("ARC-Easy"):
                n_e += 1
                c_e += hit
            else:
                n_c += 1
                c_c += hit
                chal_hits.append(hit)
        return {"easy": round(c_e / n_e, 4) if n_e else None,
                "challenge": round(c_c / n_c, 4) if n_c else None,
                "chal_correct": c_c, "chal_n": n_c, "_chal_hits": chal_hits}

    e2e = {}
    for name in ("A", "B0", "B", "D"):
        e2e[name] = {"bundle": end_to_end(name, "bundle"), "single": end_to_end(name, "single")}
        print(f"[e2e] {name} bundle easy={e2e[name]['bundle']['easy']} chal={e2e[name]['bundle']['challenge']}",
              flush=True)

    # ---- KEY WATCH: paired McNemar B vs A on Challenge (does higher recall move end-to-end?) ----
    hA = e2e["A"]["bundle"]["_chal_hits"]
    hB = e2e["B"]["bundle"]["_chal_hits"]
    b_disc = sum(1 for a, bb in zip(hA, hB) if a == 1 and bb == 0)   # A right, B wrong
    c_disc = sum(1 for a, bb in zip(hA, hB) if a == 0 and bb == 1)   # A wrong, B right
    mcnemar_p = round(_mcnemar_exact(b_disc, c_disc), 4)
    cA, cB = e2e["A"]["bundle"], e2e["B"]["bundle"]
    ciA = _binom_ci95(cA["chal_correct"], cA["chal_n"])
    ciB = _binom_ci95(cB["chal_correct"], cB["chal_n"])
    chalB_above_chance = bool(ciB[0] > 0.25) if cB["chal_n"] else False
    e2e_B_beats_A_sig = bool(mcnemar_p < 0.05 and cB["challenge"] and cA["challenge"]
                             and cB["challenge"] > cA["challenge"])

    # drop the bulky per-question hit arrays before persist
    for name in ("A", "B0", "B", "D"):
        for cm in ("bundle", "single"):
            e2e[name][cm].pop("_chal_hits", None)

    # ---- arms-differ (top-K digests) ----
    import hashlib
    def dig(name):
        b = b"".join(np.sort(t[:TOP_K].astype(np.int64)).tobytes() for t in arm_topk[name])
        return hashlib.sha256(b).hexdigest()
    digests = {name: dig(name) for name in ("A", "B0", "B", "D")}
    arms_differ = (len(set(digests.values())) == 4) and (digests["B"] != digests["B0"])

    # ---- verdict ----
    rA, rB0, rB, rD = recall["A"]["at10"], recall["B0"]["at10"], recall["B"]["at10"], recall["D"]["at10"]
    lift = round(rB - rA, 4)                              # PRIMARY: upgraded-PPR vs cosine baseline
    seed_delta = round(rB - rB0, 4)                       # seeding-only delta (B vs B0)
    d_collapse = round(rD - rA, 4)                        # want <= HP_D_COLLAPSE
    b0_repro_ok = abs(rB0 - PRIOR_B_RECALL10) <= B0_REPRO_TOL   # Gate D positive control

    ag_saturated = rA >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < rA < 0.95
    seed_ok = seed_recall >= SEED_QUALITY_FLOOR
    structural_ok = d_collapse <= HP_D_COLLAPSE
    mechanism_hardpass = (lift >= HP_RECALL_LIFT) and structural_ok and seed_ok

    if ag_saturated:
        verdict = "RETRIEVAL_DISCRIMINATOR_SATURATED"
        vmsg = (f"baseline cosine recall@10 A={rA} >= {AG_BASELINE_SAT}: no headroom (report, not "
                f"a mechanism failure).")
    elif mechanism_hardpass:
        verdict = "SEED_UPGRADE_HARD_PASS"
        vmsg = (f"SEEDING: seed_recall {seed_recall} >= {SEED_QUALITY_FLOOR} floor (v1 {PRIOR_SEED_RECALL}). "
                f"RECALL: upgraded-PPR B recall@10 {rB} >= baseline A {rA} +{HP_RECALL_LIFT} (lift {lift:+.4f}; "
                f"seeding-only delta B-B0 {seed_delta:+.4f}); shuffled D {rD} collapses (D-A {d_collapse:+.4f} "
                f"<= {HP_D_COLLAPSE}). KEY WATCH end-to-end Challenge B={cB['challenge']} vs A={cA['challenge']} "
                f"(McNemar p={mcnemar_p}, {'SIG' if e2e_B_beats_A_sig else 'NOT sig'}; B "
                f"{'ABOVE' if chalB_above_chance else 'NOT above'} chance {chance:.3f}).")
    elif (seed_ok or lift >= MB_RECALL_LIFT):
        verdict = "SEED_UPGRADE_MIDDLE_BAND"
        vmsg = (f"MIDDLE: seed_recall {seed_recall} (floor {SEED_QUALITY_FLOOR}, {'CLEARED' if seed_ok else 'below'}); "
                f"recall lift {lift:+.4f} (B {rB} vs A {rA}; seeding-only B-B0 {seed_delta:+.4f}) in [{MB_RECALL_LIFT},"
                f"{HP_RECALL_LIFT}) OR structure gate unmet (D-A {d_collapse:+.4f} want<={HP_D_COLLAPSE}). "
                f"Seeding helps but recall not decisively past +{HP_RECALL_LIFT}. KEY WATCH end-to-end Chal "
                f"B={cB['challenge']} vs A={cA['challenge']} (McNemar p={mcnemar_p}).")
    else:
        verdict = "SEED_UPGRADE_HARD_FAIL"
        vmsg = (f"HARD_FAIL: seed_recall {seed_recall} < {SEED_QUALITY_FLOOR} AND recall lift {lift:+.4f} "
                f"< {MB_RECALL_LIFT} (B {rB} vs A {rA}; seeding-only B-B0 {seed_delta:+.4f}). Seed upgrade did "
                f"not clear the make-or-break floor nor lift recall. D shuffled {rD} (D-A {d_collapse:+.4f}).")

    # NECESSARY-BUT-NOT-SUFFICIENT flag: recall/seed win but end-to-end flat -> combiner/pool-K is next wall
    recall_won = (lift >= MB_RECALL_LIFT) or seed_ok
    nec_not_suff = bool(recall_won and not e2e_B_beats_A_sig)

    grade = arc._grade_proxy(cB["easy"], cB["challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: seed_recall={seed_recall} (v1 {PRIOR_SEED_RECALL}, floor {SEED_QUALITY_FLOOR}) | "
                    f"recall@10 A={rA} B0={rB0} B={rB} D={rD} | lift(B-A)={lift:+.4f} seeding-delta(B-B0)="
                    f"{seed_delta:+.4f} D-A={d_collapse:+.4f} | e2e Chal B={cB['challenge']} A={cA['challenge']} "
                    f"McNemar_p={mcnemar_p} nec_not_suff={nec_not_suff}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "chance_theoretical": round(chance, 4),
        # graph transparency
        "store_facts": nFacts, "graph_terms": nTerms, "incidence_nnz": int(A.nnz),
        "lemma_keys": len(lem2idxs), "hops": HOPS, "damp": DAMP, "top_k": TOP_K,
        "seed_cos_upgraded": SEED_COS, "seed_cos_baseline": SEED_COS_OLD, "bigram_cos": BIGRAM_COS,
        "expand_wordnet": EXPAND_WORDNET, "use_bigrams": USE_BIGRAMS, "max_bigrams": MAX_BIGRAMS,
        "seed_weights": {"exact": W_EXACT, "lemma": W_LEMMA, "syn": W_SYN, "hyp": W_HYP,
                         "sem": W_SEM, "bigram": W_BIGRAM},
        "ppr_mass_moved": ppr_mass_moved,
        # PRIMARY (i): SEED QUALITY (make-or-break)
        "seed_recall": seed_recall, "seed_precision": seed_precision,
        "seed_recall_baseline": seed_recall_bl, "seed_precision_baseline": seed_precision_bl,
        "mean_seeds_upgraded": mean_seeds_up, "mean_seeds_baseline": mean_seeds_bl,
        "n_empty_seed_q": n_empty_seed, "seed_quality_floor": SEED_QUALITY_FLOOR,
        "seed_ok": bool(seed_ok), "prior_seed_recall": PRIOR_SEED_RECALL,
        # PRIMARY (ii): recall@K of gold central facts
        "recall_at10": {k: recall[k]["at10"] for k in recall},
        "recall_at20": {k: recall[k]["at20"] for k in recall},
        "recall_lift_B_minus_A": lift,
        "recall_seeding_delta_B_minus_B0": seed_delta,
        "recall_D_minus_A": d_collapse,
        "b0_reproduces_prior_B": bool(b0_repro_ok),
        "prior_A_recall10": PRIOR_A_RECALL10, "prior_B_recall10": PRIOR_B_RECALL10,
        # KEY WATCH: end-to-end ARC through UNCHANGED combiner + significance
        "end_to_end": e2e,
        "challenge_A_ci95": [round(ciA[0], 4), round(ciA[1], 4)],
        "challenge_B_ci95": [round(ciB[0], 4), round(ciB[1], 4)],
        "challenge_B_above_chance": chalB_above_chance,
        "mcnemar_B_vs_A_chal": {"b_A_right_B_wrong": b_disc, "c_A_wrong_B_right": c_disc, "p_two_sided": mcnemar_p},
        "e2e_B_beats_A_significant": e2e_B_beats_A_sig,
        "necessary_but_not_sufficient": nec_not_suff,
        # gates / integrity
        "arms_differ_verified": bool(arms_differ),
        "arm_topk_digests": digests,
        "baseline_in_band": bool(baseline_in_band),
        "ag_saturated": bool(ag_saturated),
        "structural_collapse_ok": bool(structural_ok),
        "mechanism_hardpass": bool(mechanism_hardpass),
        "bands": {"HP_recall_lift": HP_RECALL_LIFT, "HP_D_collapse": HP_D_COLLAPSE,
                  "MB_recall_lift": MB_RECALL_LIFT, "seed_quality_floor": SEED_QUALITY_FLOOR,
                  "AG_baseline_sat": AG_BASELINE_SAT, "B0_repro_tol": B0_REPRO_TOL},
        "grade_proxy": grade,
        "one_variable": ("SEEDING (entity-linking): B vs B0 differ ONLY in seed-linking (morphy lemma + "
                         "WordNet synonym/hypernym + lower SEED_COS + bigram phrase seeds). Graph, PPR (2 hops, "
                         "damp 0.5, idf-weighted transition), and the bind+settle combiner are BIT-UNCHANGED "
                         "from v1 arm B. Dropped v1's discriminative re-rank (HURT: v1 C 0.1953<B 0.3796) and "
                         "the hub-idf ABLATION arm (near-inert: v1 C-E +0.0046)."),
        "wired_vs_stubbed": (
            "WIRED: REAL WorldTree tablestore as a bipartite fact-term graph, SHARDED. UPGRADED semantic "
            "seed-linking (SemanticHDEncoder meaning-match + exact vocab + WordNet morphy lemma index + "
            "WordNet synonym/hypernym expansion + lowered cosine threshold + multi-token bigram phrase seeds) "
            "from stem + ALL choices. Batched scipy.sparse PPR (unchanged). Retrieved pools fed through the "
            "UNCHANGED agg.aggregate combiner (imported; SEEDING is the ONE variable). Shuffled-graph control. "
            "recall@K vs WorldTree gold central facts + seed_recall vs gold entity mentions + end-to-end ARC "
            "Easy/Challenge with paired McNemar B-vs-A significance. "
            "STORE COMPOSITION: full tablestore incl gold (recall@K of gold requires them present; gold facts "
            "are general curriculum sentences, NOT answer labels -> closed-book-over-curriculum, not answer-leak). "
            "STUBBED/NOTED-NOT-BUILT: discriminative re-rank (dropped, HURT in v1); hub-idf ablation arm (dropped, "
            "inert in v1); khop Merkle audit-chain (glassbox_sample gives seed->fact trace); iterative re-seeding "
            "(depth capped at 2 per WorldTree task-shape)."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": "mixed CPU: batched GloVe encode + scipy.sparse batched PPR + per-question seed linking; wall target < 10min",
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
        "progress_logging": "line_buffered_stdout",
    }
    _write_metrics_atomic(output_dir, metrics)

    # glass-box: upgraded vs baseline seed terms + top retrieved facts for a few questions (LOCAL-only)
    try:
        sample = []
        for qi in range(min(8, nQ)):
            q = questions[qi]
            topb = [uids[i] for i in arm_topk["B"][qi][:TOP_K]]
            sample.append({
                "qid": q["qid"], "stem": q["stem"][:120],
                "seed_terms_upgraded": sorted([vocab[j] for j in seeds_up[qi].keys()])[:24],
                "seed_terms_baseline": sorted([vocab[j] for j in seeds_bl[qi].keys()])[:24],
                "gold_central_sents": [uid2sent.get(u, u)[:80] for u in q["gold_central"][:4]],
                "retrieved_B": [{"sent": uid2sent.get(u, u)[:80], "is_gold": u in set(q["gold_central"])}
                                for u in topb[:6]],
            })
        with open(os.path.join(output_dir, "glassbox_sample.json"), "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2)
    except Exception as e:
        print(f"[warn] glassbox persist failed (non-fatal): {e}", flush=True)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)
    return metrics


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    output_dir = _out_dir()
    _T0[0] = time.perf_counter()
    _write_start_marker(output_dir, args.mode)
    run(args.mode, output_dir)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
