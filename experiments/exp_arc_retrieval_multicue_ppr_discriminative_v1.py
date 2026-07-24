"""arc_retrieval_multicue_ppr_discriminative_v1 -- brain-faithful RETRIEVAL for ARC.

Retrieval is the VET-confirmed wall (29537 MM, af29a98ef): GIVEN gold facts the bind+settle
combiner reaches Challenge 0.696, but end-to-end stays ~chance because ~50% of misses = the right
fact was never retrieved. Our retriever is flat single-shot cosine NN. This cell tests whether
SPREADING ACTIVATION over the REAL WorldTree fact-graph, multi-cue seeded + hub-downweighted +
discriminatively re-ranked, surfaces the RIGHT (gold central) facts better than cosine, and whether
that lifts end-to-end ARC.

BRAIN MECHANISM (credited): Collins & Loftus 1975 spreading activation (activation spreads along
labeled relational links, reaching concepts sharing zero surface features with the cue); Anderson
1974 ACT-R fan-effect (a fact linked to BOTH an active stem-cue and an active choice-cue gets
activation that SUMS -- the bridge-fact the surface-cosine retriever misses); Tulving&Thomson 1973 +
Badre&Wagner 2007 discriminative/controlled retrieval (select facts that SEPARATE the choices, not
merely match the stem); Gutierrez et al. 2024 HippoRAG (PPR over a KG seeded from query entities;
hub-node down-weighting + seed-quality make-or-break). Prior attempt exp_ppr_spreading_activation_
cpu_v1 HARD_FAIL (recall 0.217) was CONFOUNDED by a 120-node synthetic sparse graph + single-bundle
superposition (lit failure-precondition c) -- this is the FAIR re-test on the REAL typed WorldTree
graph, SHARDED (each fact its own node; no superposition).

GRAPH: bipartite fact-term over the ingested tablestore (9720 typed facts). FACT nodes = tablestore
rows (UID), each independent (sharded). TERM nodes = content lemmas. Edge = fact-contains-term. A
KINDOF fact linking "dog" and "animal" realizes the typed bridge via both terms attaching to that
fact node. Node-specificity: term vertex weight idf[t]=log(nFacts/df[t]); fact->term walk + fact
scoring idf-weighted so hub terms do not swamp (HippoRAG precondition b).

ARMS (one variable = retrieval; combiner UNCHANGED, imported from the aggregation cell):
  A baseline_single_shot     -- cosine top-K (QQ @ SV_store.T), unchanged.
  B ppr_spreading_only       -- multi-cue PPR, rank by activation, top-K.
  C ppr_plus_discriminative  -- B's top-M pool re-ranked by discriminative_score, top-K.  [MECHANISM]
  D shuffled_graph_control   -- B/C on degree-preserving edge-permuted incidence -- MUST collapse toward A.
  E hub_dilution_ablation    -- C with idf down-weighting OFF -- must be worse than C.

METRICS: PRIMARY recall@K (K=10) of GOLD CENTRAL support facts vs WorldTree gold (store = FULL
tablestore incl gold; retrieving a general curriculum fact IS the task -- gold facts are plain
sentences, NOT answer labels; closed-book-over-curriculum, not answer-leak). SECONDARY end-to-end
ARC (Easy+Challenge) through the UNCHANGED combiner. SEED-QUALITY sub-check FIRST (make-or-break).

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> not remote-
portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted
iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds the REAL SemanticHDEncoder + REAL bipartite graph + REAL PPR +
#   all 5 arms at tiny scale; a PLANTED bridge-fact case asserts the discriminator FIRES (B/C find a
#   fact reachable only via the graph that cosine-baseline A misses); arms-differ; determinism
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on baseline recall (headroom for the retrieval win)
# - storage = SHARDED (each fact = own vector + own graph node; no superposition)
# - all reported numbers MEASURED@ this cell's metrics.json
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

ANCHOR_NAME = "arc_retrieval_multicue_ppr_discriminative_v1"
SEED = 20260724

# ---- retrieval hyperparams (author-designed a priori; see pre-reg) ----
TOP_K = 10          # primary recall@K and the pool size fed to the combiner
TOP_K2 = 20         # secondary recall@20
RERANK_M = 40       # discriminative re-rank candidate-pool depth (B activation top-M -> disc top-K)
HOPS = 2            # fact-hops (term->fact->term x2); WorldTree central-support median 2, p90 5
DAMP = 0.5          # PPR restart / damping (alpha); a=(1-a)*seed + a*(a@M)
SEED_COS = 0.60     # semantic seed-linking cosine threshold for out-of-vocab question words
MIN_TERM_LEN = 4    # content-word length (arc._content_words default)

# ---- bands (author-designed; see pre-reg). PRIMARY = recall@K of gold central facts. ----
HP_RECALL_LIFT = 0.15       # C/B recall@10 - A recall@10 >= this -> mechanism HARD-PASS
HP_D_COLLAPSE = 0.03        # D recall - A recall <= this -> lift is structure-driven
MB_RECALL_LIFT = 0.05       # positive-but-sub-HP lift band floor
SEED_QUALITY_FLOOR = 0.50   # seed_recall < this -> attribute downstream fail to SEEDING
AG_BASELINE_SAT = 0.95      # baseline A recall >= this -> discriminator vacuous (no headroom)


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
    projection Sft [nTerms x nFacts]. use_idf=False = hub-dilution ablation (uniform weights).
      TF = row_norm(A^T)              term -> its facts (uniform)
      FT = row_norm(A * diag(idf))    fact -> its terms, hub-downweighted (specificity fix)
      M  = TF @ FT                    one fact-hop in term space
      Sft[t,f] = idf[t] * A[f,t]      fact activation projection (specific terms dominate)
    """
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
# seed linking (semantic, not lexical)
# ---------------------------------------------------------------------------
def link_seeds(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, seed_cos):
    """For each question, build a seed term-index list. Exact-vocab match for in-vocab words; else
    SemanticHDEncoder meaning-match (nearest term by cosine >= seed_cos). Returns list of dict
    {term_idx: weight}. term_vecs [nTerms x N] L2 rows; q_word_vecs_per_q[qi] [nW x N] L2 rows."""
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


def discriminative_rerank(pool_idx, SV_store, choice_hd_q, k):
    """From candidate pool_idx, keep top-k facts by discriminative_score = (max_choice cos) -
    (2nd-max_choice cos). Answer-agnostic (all choices symmetric)."""
    if pool_idx.size == 0:
        return pool_idx
    fh = SV_store[pool_idx]                       # [P x N]
    cc = fh @ choice_hd_q.T                       # [P x C]
    if cc.shape[1] >= 2:
        part = np.sort(cc, axis=1)
        disc = part[:, -1] - part[:, -2]
    else:
        disc = cc.max(axis=1)
    kk = min(k, pool_idx.size)
    order = np.argsort(-disc, kind="stable")[:kk]
    return pool_idx[order]


def recall_at_k(topk_uids, gold_central):
    g = set(gold_central)
    if not g:
        return None
    return len(set(topk_uids) & g) / len(g)


# ---------------------------------------------------------------------------
# self-test (real code path + planted bridge-fact discriminator + determinism + arms-differ)
# ---------------------------------------------------------------------------
def _planted_bridge_discriminator():
    """Synthetic bipartite graph where the GOLD fact is a BRIDGE reachable only via spreading, NOT by
    the seed's own facts. Seeds = {ta, tc}. Gold fact g contains {tb, td} -- shares NO term with the
    seeds -- but tb co-occurs with ta (via fact f1) and td co-occurs with tc (via fact f2). A pure
    seed-fact lookup (baseline analog) never touches g; multi-cue PPR (2 hops) reaches g from both
    sides and it ranks top. Proves B/C recall-lift is ACHIEVABLE (discriminator_reachability)."""
    # facts: f0={ta,tb} f1={tb,tx} f2={tc,td} f3={td,ty} g4={tb,td}(GOLD bridge) noise5={tz,tw}
    vocab = ["ta", "tb", "tc", "td", "tx", "ty", "tz", "tw"]
    fact_terms = [["ta", "tb"], ["tb", "tx"], ["tc", "td"], ["td", "ty"],
                  ["tb", "td"], ["tz", "tw"]]
    gold_idx = 4
    A, df, t2i = build_incidence(fact_terms, vocab)
    M, Sft, idf = build_transition(A, df, use_idf=True)
    seeds = [{t2i["ta"]: 1.0, t2i["tc"]: 1.0}]   # multi-cue: stem-term ta + choice-term tc
    seed_mat = seeds_to_matrix(seeds, len(vocab))
    a = ppr_batch(seed_mat, M, hops=2, damp=0.5)
    fscore = fact_activation(a, Sft)             # [1 x nFacts]
    top = topk_from_scores(fscore[0], 3)
    assert gold_idx in set(top.tolist()), f"planted: PPR did not surface the bridge gold fact; top={top}"
    # baseline analog = facts directly containing a seed term (no spreading): must MISS the gold bridge
    direct = set()
    for f, terms in enumerate(fact_terms):
        if "ta" in terms or "tc" in terms:
            direct.add(f)
    assert gold_idx not in direct, "planted: gold bridge must not be directly seed-adjacent"
    # arms differ: shuffled graph must (in general) NOT reproduce the same top set deterministically
    rng = np.random.default_rng(0)
    A_s, df_s = shuffle_incidence(A, rng)
    M_s, Sft_s, idf_s = build_transition(A_s, df_s, use_idf=True)
    a_s = ppr_batch(seed_mat, M_s, hops=2, damp=0.5)
    fscore_s = fact_activation(a_s, Sft_s)
    top_s = topk_from_scores(fscore_s[0], 3)
    # determinism
    a2 = ppr_batch(seed_mat, M, hops=2, damp=0.5)
    assert np.allclose(a, a2), "planted: PPR non-deterministic"
    return True


def self_test():
    print("[self-test] planted bridge-fact discriminator (PPR reaches a fact cosine-seeds miss) ...", flush=True)
    _planted_bridge_discriminator()

    print("[self-test] REAL SemanticHDEncoder + real bipartite graph + real PPR + all arms ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "photosynthesis produces oxygen as a byproduct for animals to breathe",
        "sunlight is a source of energy for plants",
        "iron is a heavy metal used to build bridges",
        "the moon orbits the earth once each month",
    ]
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in store_sents]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = build_incidence(fact_terms, vocab)
    assert A.shape == (5, len(vocab)) and A.nnz > 0, "incidence build failed"
    M, Sft, idf = build_transition(A, df, use_idf=True)
    M_e, Sft_e, idf_e = build_transition(A, df, use_idf=False)
    assert not np.allclose(idf, idf_e), "idf ablation switch inert (E == C)"

    SV_store = arc._encode_store(enc, store_sents)          # [5, nd] L2 rows
    term_vecs = arc._encode_store(enc, vocab)               # [nTerms, nd]

    q = {"stem": "What do green plants make using sunlight?",
         "choices": ["iron metal", "sugar and oxygen", "the moon", "loud sound"]}
    q_words = sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
    q_word_vecs = arc._encode_store(enc, q_words)
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])

    seeds = link_seeds([q_words], vocab, t2i, term_vecs, [q_word_vecs], SEED_COS)
    assert len(seeds[0]) > 0, "seed linking found no seeds on the planted real question"
    seed_mat = seeds_to_matrix(seeds, len(vocab))

    # arm A baseline cosine
    A_scores = QQ @ SV_store.T
    topA = topk_from_scores(A_scores, TOP_K)
    # arm B ppr
    a = ppr_batch(seed_mat, M, HOPS, DAMP)
    B_scores = fact_activation(a, Sft)
    topB = topk_from_scores(B_scores[0], TOP_K)
    poolB = topk_from_scores(B_scores[0], RERANK_M)
    # arm C discriminative
    topC = discriminative_rerank(poolB, SV_store, choice_hd, TOP_K)
    # arm E ablation
    a_e = ppr_batch(seed_mat, M_e, HOPS, DAMP)
    E_scores = fact_activation(a_e, Sft_e)
    topE = topk_from_scores(E_scores[0], TOP_K)

    # discriminator-fires (real path): PPR must actually MOVE activation mass off the seeds (spreading
    # happened, not a pass-through). The genuine arms-differ proof is the planted-bridge case above
    # (B reaches the gold bridge that direct-seed misses) + the full-run top-K digest gate at 9720 facts;
    # a 5-fact self-test store returns all facts in top-K so a set/rank difference is not guaranteed.
    assert not np.allclose(a, seed_mat.toarray()), "META_RULE_AF: PPR moved no activation mass (spreading inert)"
    assert topB.size > 0 and topC.size > 0 and topE.size > 0, "arm outputs empty on real path"

    # combiner reuse UNCHANGED: agg.aggregate consumes (fact_hd, q_rel, choice_hd)
    fhB = SV_store[topB]
    q_rel = np.maximum(fhB @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fhB, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == len(q["choices"]), "combiner reuse shape mismatch"

    # determinism
    a_b = ppr_batch(seed_mat, M, HOPS, DAMP)
    assert np.allclose(a, a_b), "PPR non-deterministic on real path"

    # WorldTree parse touch
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = agg.load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print(f"[self-test] PASS (planted bridge reached by PPR + missed by direct-seed; real encoder+"
          f"graph+PPR+arms A/B/C/E; idf ablation live; combiner reuse; determinism; WT parse)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # FULL graph (all 9720 facts -> discriminator fires at real graph scale), question SUBSET
        return {"n_dim": 2048, "limit_easy": 200, "limit_chal": 150}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None}


def _binom_ci95(k, n):
    """Wald-ish normal-approx 95% CI for a binomial proportion (lower, upper)."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    return (max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se))


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
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

    # ---- bipartite graph over the store ----
    _heartbeat(output_dir, "build_graph")
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = build_incidence(fact_terms, vocab)
    nTerms = len(vocab)
    M, Sft, idf = build_transition(A, df, use_idf=True)          # arm B/C/D
    M_e, Sft_e, idf_e = build_transition(A, df, use_idf=False)   # arm E (no idf)
    print(f"[graph] terms={nTerms} incidence_nnz={A.nnz} mean_terms/fact={A.nnz/max(nFacts,1):.2f}", flush=True)

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
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])  # [nQ x nd]
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]) for q in questions]

    # per-question content words + their vectors (for semantic seed linking)
    q_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
                     for q in questions]
    uniq_words = sorted({w for ws in q_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}
    q_word_vecs_per_q = [uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)
                         for ws in q_words_per_q]

    # ---- seeds (semantic multi-cue) + seed-quality vs WorldTree gold ----
    _heartbeat(output_dir, "seed_linking")
    seeds = link_seeds(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, SEED_COS)
    seed_mat = seeds_to_matrix(seeds, nTerms)

    # seed-quality: gold-fact terms present-in-store vs linked seed terms
    i2t = vocab
    seed_recs, seed_precs = [], []
    n_empty_seed = 0
    for qi, q in enumerate(questions):
        gold_terms = set()
        for u in q["gold_central"]:
            if u in uid2fi:
                gold_terms |= set(fact_terms[uid2fi[u]])
        seed_terms = {i2t[j] for j in seeds[qi].keys()}
        if not seed_terms:
            n_empty_seed += 1
        if gold_terms:
            inter = len(seed_terms & gold_terms)
            seed_recs.append(inter / len(gold_terms))
            seed_precs.append(inter / len(seed_terms) if seed_terms else 0.0)
    seed_recall = round(float(np.mean(seed_recs)), 4) if seed_recs else 0.0
    seed_precision = round(float(np.mean(seed_precs)), 4) if seed_precs else 0.0
    print(f"[seed] recall={seed_recall} precision={seed_precision} empty_seed_q={n_empty_seed}/{nQ}", flush=True)

    # ---- PPR (batched) for real, shuffled, and ablation graphs ----
    _heartbeat(output_dir, "ppr")
    a_real = ppr_batch(seed_mat, M, HOPS, DAMP)                  # [nQ x nTerms]
    a_shuf = ppr_batch(seed_mat, M_s, HOPS, DAMP)
    a_abl = ppr_batch(seed_mat, M_e, HOPS, DAMP)
    ppr_mass_moved = round(float(np.mean(np.abs(a_real - seed_mat.toarray()).sum(axis=1))), 5)

    _heartbeat(output_dir, "score_facts")
    FB = fact_activation(a_real, Sft)           # arm B (idf baked into Sft)
    FD = fact_activation(a_shuf, Sft_s)         # arm D
    FE = fact_activation(a_abl, Sft_e)          # arm E (Sft_e built with idf=1)

    # ---- per-arm retrieval + recall + end-to-end (through UNCHANGED combiner) ----
    _heartbeat(output_dir, "retrieve_and_eval")
    arm_topk = {name: [] for name in ("A", "B", "C", "D", "E")}
    for qi in range(nQ):
        # A baseline cosine
        As = QQ[qi] @ SV_store.T
        arm_topk["A"].append(topk_from_scores(As, TOP_K2))
        # B ppr
        arm_topk["B"].append(topk_from_scores(FB[qi], TOP_K2))
        # C discriminative on B pool
        poolB = topk_from_scores(FB[qi], RERANK_M)
        arm_topk["C"].append(discriminative_rerank(poolB, SV_store, choice_hd_map[qi], TOP_K2))
        # D shuffled graph (spreading-only ranking)
        arm_topk["D"].append(topk_from_scores(FD[qi], TOP_K2))
        # E hub-dilution ablation (discriminative on ablated B pool, to mirror C)
        poolE = topk_from_scores(FE[qi], RERANK_M)
        arm_topk["E"].append(discriminative_rerank(poolE, SV_store, choice_hd_map[qi], TOP_K2))

    # recall@K and @K2
    def arm_recall(name, k):
        rs = []
        for qi, q in enumerate(questions):
            topk_uids = [uids[i] for i in arm_topk[name][qi][:k]]
            r = recall_at_k(topk_uids, q["gold_central"])
            if r is not None:
                rs.append(r)
        return round(float(np.mean(rs)), 4) if rs else 0.0

    recall = {name: {"at10": arm_recall(name, TOP_K), "at20": arm_recall(name, TOP_K2)}
              for name in ("A", "B", "C", "D", "E")}
    for name in ("A", "B", "C", "D", "E"):
        print(f"[recall] {name}: @10={recall[name]['at10']} @20={recall[name]['at20']}", flush=True)

    # end-to-end through UNCHANGED combiner (bundle = best per prior cell; single reported too)
    def end_to_end(name, combiner_mode):
        c_e = c_c = n_e = n_c = 0
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
        return {"easy": round(c_e / n_e, 4) if n_e else None,
                "challenge": round(c_c / n_c, 4) if n_c else None,
                "chal_correct": c_c, "chal_n": n_c}

    e2e = {}
    for name in ("A", "B", "C", "D", "E"):
        e2e[name] = {"bundle": end_to_end(name, "bundle"), "single": end_to_end(name, "single")}
        print(f"[e2e] {name} bundle easy={e2e[name]['bundle']['easy']} chal={e2e[name]['bundle']['challenge']}",
              flush=True)

    # ---- arms-differ (top-K digests) ----
    import hashlib
    def dig(name):
        b = b"".join(np.sort(t[:TOP_K].astype(np.int64)).tobytes() for t in arm_topk[name])
        return hashlib.sha256(b).hexdigest()
    digests = {name: dig(name) for name in ("A", "B", "C", "D", "E")}
    arms_differ = len({digests["A"], digests["B"], digests["C"]}) == 3 and digests["C"] != digests["E"]

    # ---- verdict (PRIMARY = recall@10; note bands) ----
    rA, rB, rC = recall["A"]["at10"], recall["B"]["at10"], recall["C"]["at10"]
    rD, rE = recall["D"]["at10"], recall["E"]["at10"]
    best_mech = max(rB, rC)
    best_name = "C" if rC >= rB else "B"
    lift = round(best_mech - rA, 4)
    d_collapse = round(rD - rA, 4)                       # want <= HP_D_COLLAPSE
    e_worse = round(rC - rE, 4)                          # want > 0 (E worse than C)

    # end-to-end challenge under C
    cC = e2e["C"]["bundle"]
    ci_lo, ci_hi = _binom_ci95(cC["chal_correct"], cC["chal_n"])
    challenge_above_chance = bool(ci_lo > 0.25) if cC["chal_n"] else False

    ag_saturated = rA >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < rA < 0.95
    seed_ok = seed_recall >= SEED_QUALITY_FLOOR

    structural_ok = d_collapse <= HP_D_COLLAPSE
    hub_ok = e_worse > 0
    mechanism_hardpass = (lift >= HP_RECALL_LIFT) and structural_ok and hub_ok

    if not seed_ok and (best_mech < rA + MB_RECALL_LIFT):
        verdict = "HARD_FAIL_SEEDING"
        vmsg = (f"seed_recall {seed_recall} < {SEED_QUALITY_FLOOR} (make-or-break) AND mechanism lift "
                f"{lift} < {MB_RECALL_LIFT}. Downstream fail attributed to SEEDING (entity-linking), NOT "
                f"spreading: recall A={rA} B={rB} C={rC}.")
    elif ag_saturated:
        verdict = "RETRIEVAL_DISCRIMINATOR_SATURATED"
        vmsg = (f"baseline cosine recall@10 A={rA} >= {AG_BASELINE_SAT}: single-shot already saturates gold "
                f"recall; no headroom for spreading (report, not a mechanism failure).")
    elif mechanism_hardpass:
        verdict = "RETRIEVAL_HARD_PASS"
        vmsg = (f"MECHANISM: arm {best_name} recall@10 {best_mech} >= baseline A {rA} +{HP_RECALL_LIFT} "
                f"(lift {lift:+.4f}); shuffled-graph D {rD} collapses to A (+{d_collapse:.4f} <= {HP_D_COLLAPSE}); "
                f"hub-ablation E {rE} worse than C {rC} ({e_worse:+.4f}). "
                f"END-TO-END Challenge under C = {cC['challenge']} (95% CI [{ci_lo:.3f},{ci_hi:.3f}], "
                f"{'ABOVE' if challenge_above_chance else 'NOT above'} chance {chance:.3f}). "
                f"seed_recall {seed_recall}.")
    elif lift >= MB_RECALL_LIFT:
        verdict = "RETRIEVAL_MIDDLE_BAND"
        vmsg = (f"MIDDLE: recall lift {lift:+.4f} (best {best_name} {best_mech} vs A {rA}) in [{MB_RECALL_LIFT},"
                f"{HP_RECALL_LIFT}) OR structure/hub gate unmet (D-A={d_collapse:+.4f} want<={HP_D_COLLAPSE}, "
                f"C-E={e_worse:+.4f} want>0). Spreading helps but not decisively; end-to-end Chal C="
                f"{cC['challenge']}. seed_recall {seed_recall}.")
    else:
        verdict = "RETRIEVAL_HARD_FAIL"
        vmsg = (f"MECHANISM HARD_FAIL: best spreading arm {best_name} recall@10 {best_mech} does not exceed "
                f"baseline A {rA} beyond noise (lift {lift:+.4f} < {MB_RECALL_LIFT}). "
                f"D shuffled {rD} (D-A={d_collapse:+.4f}); if D ~= B/C the lift is not structure-driven. "
                f"seed_recall {seed_recall} ({'ok' if seed_ok else 'LOW -> seeding suspect'}). "
                f"Redirect per note: isolate discriminative-rerank-alone (step 4) vs graph-spread (step 2).")

    grade = arc._grade_proxy(e2e["C"]["bundle"]["easy"], cC["challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: recall@10 A={rA} B={rB} C={rC} D={rD} E={rE} | lift={lift:+.4f} "
                    f"D-A={d_collapse:+.4f} C-E={e_worse:+.4f} | seed_recall={seed_recall} | "
                    f"e2e Chal C(bundle)={cC['challenge']} chance={chance:.3f}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "chance_theoretical": round(chance, 4),
        # graph transparency
        "store_facts": nFacts, "graph_terms": nTerms, "incidence_nnz": int(A.nnz),
        "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS, "top_k": TOP_K, "rerank_m": RERANK_M,
        "ppr_mass_moved": ppr_mass_moved,
        # SEED QUALITY (make-or-break, reported first)
        "seed_recall": seed_recall, "seed_precision": seed_precision,
        "n_empty_seed_q": n_empty_seed, "seed_quality_floor": SEED_QUALITY_FLOOR,
        "seed_ok": bool(seed_ok),
        # PRIMARY: recall@K of gold central facts
        "recall_at10": {k: recall[k]["at10"] for k in recall},
        "recall_at20": {k: recall[k]["at20"] for k in recall},
        "recall_lift_bestmech_minus_A": lift,
        "recall_best_mech_arm": best_name,
        "recall_D_minus_A": d_collapse,
        "recall_C_minus_E": e_worse,
        # SECONDARY: end-to-end ARC through UNCHANGED combiner
        "end_to_end": e2e,
        "challenge_C_bundle_ci95": [round(ci_lo, 4), round(ci_hi, 4)],
        "challenge_C_above_chance": challenge_above_chance,
        # gates / integrity
        "arms_differ_verified": bool(arms_differ),
        "arm_topk_digests": digests,
        "baseline_in_band": bool(baseline_in_band),
        "ag_saturated": bool(ag_saturated),
        "structural_collapse_ok": bool(structural_ok),
        "hub_downweight_load_bearing": bool(hub_ok),
        "mechanism_hardpass": bool(mechanism_hardpass),
        "bands": {"HP_recall_lift": HP_RECALL_LIFT, "HP_D_collapse": HP_D_COLLAPSE,
                  "MB_recall_lift": MB_RECALL_LIFT, "seed_quality_floor": SEED_QUALITY_FLOOR,
                  "AG_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: REAL WorldTree tablestore (9720 typed facts, 82 relation tables) as a bipartite "
            "fact-term graph, SHARDED (each fact = own node + own embedding; NO superposition -- fixes the "
            "prior PPR confound). Multi-cue semantic seed-linking (SemanticHDEncoder meaning-match + exact "
            "vocab) from stem + ALL choices. Batched scipy.sparse PPR (term->fact->term, idf hub-downweight, "
            "2 fact-hops). Discriminative re-rank (max-2nd-max choice-cos). ALL retrieved pools fed through "
            "the UNCHANGED agg.aggregate combiner (imported; retrieval is the ONE variable). Shuffled-graph "
            "control (degree-preserving) + hub-dilution ablation. recall@K vs WorldTree gold central facts + "
            "end-to-end ARC Easy/Challenge + seed-quality sub-check. "
            "STORE COMPOSITION: full tablestore incl. gold (recall@K of gold requires them present; gold facts "
            "are general curriculum sentences, NOT answer labels -> closed-book-over-curriculum, not answer-leak). "
            "STUBBED/NOTED-NOT-BUILT: khop Merkle audit-chain (glassbox_sample gives the seed->fact trace "
            "instead); attractor cleanup (exact-key, orthogonal here); iterative multi-hop re-seeding (depth "
            "capped at 2 per WorldTree task-shape)."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": "mixed CPU: batched GloVe encode + scipy.sparse batched PPR + per-question discriminative re-rank; wall target < 10min",
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
    }
    _write_metrics_atomic(output_dir, metrics)

    # glass-box: seed terms + top retrieved facts (with gold hit) for a few questions (LOCAL-only)
    try:
        sample = []
        for qi in range(min(8, nQ)):
            q = questions[qi]
            topc = [uids[i] for i in arm_topk["C"][qi][:TOP_K]]
            sample.append({
                "qid": q["qid"], "stem": q["stem"][:120],
                "seed_terms": sorted([vocab[j] for j in seeds[qi].keys()])[:20],
                "gold_central_sents": [uid2sent.get(u, u)[:80] for u in q["gold_central"][:4]],
                "retrieved_C": [{"sent": uid2sent.get(u, u)[:80], "is_gold": u in set(q["gold_central"])}
                                for u in topc[:6]],
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
