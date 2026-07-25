"""native_meaning_encoder_binder_grounded_v1 -- THE MECHANISM TEST (Director Option A, brain-native
fair test): can the substrate EARN a held-out concept's Binder-65 brain-grounded feature vector FROM
ITS RELATIONS + native-encoded CONTEXT (error-driven; native encoder input ONLY -- NOT GloVe/BERT/
Feature2Vec projection), and does that earned grounded meaning GENERALIZE to held-out concepts?

WHY THIS FRAMING (coverage finding, reported not hidden): Binder-2016 grounds 534 CONCRETE/embodied
common words on 65 human-rated brain-system feature dimensions (operationalized Barsalou grounding).
WorldTree is SCIENCE concepts + property-VALUES; the two are largely disjoint where the v2 cos-pick
task needs them -- 0 of 2264 v2 items are fully grounded, ~6% of candidate VALUES have Binder vectors.
Forcing the v2 task into Binder space would route ~94% of values through an earned native->Binder
readout = the Feature2Vec projection the redirect forbids. So we test the MECHANISM on Binder's OWN
clean brain gold (a fair test the data supports): earn -> retrieve against Binder's own grounded
neighborhoods. The SCIENCE-reasoning application (same earn-from-relations approach on WorldTree-PROP
features for ARC) is the FOLLOW-UP, not this cell.

THE KEY DISCRIMINATOR (grounded vs distributional -- the whole point): the SAME earn-and-retrieve
procedure is run with three input encoders on the SAME held-out split/metric:
  grounded_earned (PRIMARY): input = [native context vec (c) + native RELATION-structure vec (c)]
    -- WT typed relations (141 concepts) composed via the native encoder's E (values) + R (relation
    types) PLUS the native SGNS context vector. NO borrowed vectors: the native encoder is trained
    only by error-driven context(ARC)+relation(WT) prediction (exp_native_meaning_encoder_scale_v1).
  distributional_earned (BASELINE): input = native SGNS context vec (c) ONLY (no relation structure).
  glove_earned (BASELINE, borrowed reference): input = frozen GloVe vec (c). SMOKE-local; CITED if
    gensim absent (portable FULL is gensim-free).
Each learns the SAME ridge map input->Binder-65 (error-driven least-squares), trained on TRAIN
concepts, applied to HELD-OUT concepts (5-fold CV over the 141 relation-having concepts; no-leak:
held concepts' Binder vectors NEVER in the map's training). Then RETRIEVE.

METRICS (held-out generalization; gold = Binder-65 cosine neighborhoods derived from the ratings):
  A2 (PRIMARY generalization): for each held concept c, rank all OTHER 533 concepts by cosine
    (predicted_c, true_other) and compare to gold ranking cosine(true_c, true_other) -- precision@10
    (top-neighbor overlap) + Spearman rank corr. Does the earned vector land c in the right
    brain-grounded neighborhood WITHOUT ever seeing c's true vector?
  A1 (discriminative accuracy): 10-way -- predicted_c must pick c's TRUE 65-dim profile among 9 HARD
    distractors (c's nearest gold neighbors), gold at a randomized position. chance = 0.10.

CONTROLS (pre-registered): chance (random predicted vectors); shuffle (permute concept->Binder target
in the map's TRAIN -> held-out MUST collapse to chance = no-leak/anti-memorization proof);
untrained_input (map over the UNTRAINED native encoder's vectors -> input carries no earned meaning);
no-leak (held concepts never in map training, asserted).

VERDICT (a priori bands; gates apply to grounded_earned vs distributional_earned):
  GROUNDED-EARNS-AND-GENERALIZES = grounded_earned held-out BEATS distributional_earned by >= MARGIN
    (both A1 and A2 directionally) AND generalizes (grounded A2 p@10 CI-lower > chance AND >
    untrained_input) AND shuffle collapses to ~chance.
  NULL-grounded~=distributional (HONEST NULL, pre-registered, NOT buried) = grounded_earned <=
    distributional_earned + EPS on the primary metric -- relational grounding adds nothing over the
    distributional readout HERE (a real finding: grounding did not help on this slice/scale).
  MIDDLE = grounded generalizes + beats distributional by a positive but < MARGIN margin.
  INVALID = shuffle does NOT collapse (leak) OR held-out set < MIN_HELDOUT OR baselines out of band.

SECONDARY (cross-ref only, not headline): v2 cos-pick property-discrimination on the ~6% Binder-
grounded value slice (exp_native_meaning_encoder_scale_v1 items) -- reported as a sanity check.

SCALE/GPU: the only GPU-warranted part is training the native SGNS encoder over ARC (millions of
sentences -> quality native context vectors = a FAIR distributional baseline + grounded context
input). The map (ridge) + retrieval are CPU-trivial. SMOKE = small ARC (CPU). FULL = large ARC (GPU
overnight_queue) after smoke clears. If smoke already answers decisively at CPU-scale, GPU is optional
(idle GPU is fine per Director) -- reported.

CELL-TEMPLATE MANDATORY: except SystemExit before Exception (no BaseException/bare); tmp_replace
atomic metrics; start-marker + crash-diagnostic + heartbeat; arms_differ (per-arm metric hashes);
deterministic (fixed int seeds, numpy default_rng, sorted(set); no builtin-hash-seeded RNG); real
code path in self-test (loads REAL Binder csv + REAL WT parse + REAL encoder + REAL ridge CV at tiny
scale + planted separability + shuffle-collapse assertion); progress_logging print_flush_true; all
numbers MEASURED@ this metrics.json. NaN handling: verbs/adj miss Complexity/Practice/Caused ->
imputed with Binder-internal column mean (NOT borrowed), count logged (~0 on the noun intersection).

Contract: prereg + self-test + LOCAL SMOKE; FULL to overnight_queue (GPU) on smoke clearance; commit
cell+prereg+metrics by explicit path; NO atom banking (skunkworks owns VET); VET-PENDING. ASCII-only.
"""
from __future__ import annotations

import os
import csv
import sys
import json
import time
import hashlib
import argparse
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

import torch  # noqa: E402

# reuse the committed baseline cell's native-encoder machinery (portable: numpy/torch only at import)
from experiments.exp_native_meaning_encoder_scale_v1 import (  # noqa: E402
    parse_tables, normalize_phrase, wilson_ci, build_corpus, ContextSampler, NegSampler,
    RelationData, NativeEncoder, train_encoder, phrase_ids, _tok_words,
    CURATED_TABLES, COARSE_RELS, REL_IDX, NREL, N_DIM, UNIGRAM_POW, WINDOW)

ANCHOR_NAME = "native_meaning_encoder_binder_grounded_v1"

BINDER_CSV = os.path.join(_REPO, "data", "corpora", "binder", "binder2016_ratings.csv")
_FEAT_START = "Vision"
_N_FEAT = 65

SEED = 20260725
K_DISC = 9                 # 10-way discrimination (chance 0.10)
N_FOLDS = 5
RIDGE_LAMBDA = 10.0        # ridge regularization (n_train ~113 << not overfit)
MIN_HELDOUT = 40           # held-out retrieval evaluations floor
SEEDS_CV = (20260725, 13, 101)  # multi-seed fold shuffles (smoke uses 1)

# scale profiles for the native SGNS encoder (context vectors)
SMOKE_ENC = dict(max_sentences=70_000, steps=1_500, batch=512)
FULL_ENC = dict(max_sentences=6_000_000, steps=120_000, batch=4096)

# pre-registered bands
MARGIN = 0.02              # grounded must beat distributional by this on the primary metric (p@10)
EPS = 0.005               # null tie band
SHUFFLE_EPS = 0.03        # shuffle held-out must be <= chance-level + this
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_T0 = [0.0]


# ---------------------------------------------------------------------------
# markers / crash / heartbeat / atomic write
# ---------------------------------------------------------------------------
def _out_dir(suffix=""):
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(), "device": DEVICE}
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
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
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
# load Binder-65 grounded feature norms
# ---------------------------------------------------------------------------
def load_binder(path):
    """Return (concepts[list], X[Nc,65] float32 grounded vectors, feature_names[65], nan_imputed_count).
    NaN (verbs/adj miss Complexity/Practice/Caused) imputed with the Binder-INTERNAL column mean over
    rated words (NOT borrowed), count logged."""
    rows = list(csv.reader(open(path, encoding="utf-8")))
    hdr = rows[0]
    wi = hdr.index("Word")
    fs = hdr.index(_FEAT_START)
    feat_names = hdr[fs:fs + _N_FEAT]
    concepts = []
    raw = []
    seen = set()
    for r in rows[1:]:
        if len(r) < fs + _N_FEAT:
            continue
        nw = normalize_phrase(r[wi])
        if not nw or nw in seen:
            continue
        seen.add(nw)
        vec = []
        for j in range(fs, fs + _N_FEAT):
            s = r[j].strip()
            try:
                vec.append(float(s))
            except ValueError:
                vec.append(np.nan)
        concepts.append(nw)
        raw.append(vec)
    X = np.asarray(raw, dtype=np.float64)
    nan_mask = np.isnan(X)
    nan_count = int(nan_mask.sum())
    if nan_count:
        col_mean = np.nanmean(X, axis=0)
        idx = np.where(nan_mask)
        X[idx] = np.take(col_mean, idx[1])
    return concepts, X.astype(np.float32), feat_names, nan_count


# ---------------------------------------------------------------------------
# native representations for a concept: context vec (E) + relation-structure vec (E over values + R)
# ---------------------------------------------------------------------------
def native_context_vec(E, concept, word2id):
    ids = phrase_ids(concept, word2id)
    if not ids:
        return None
    v = E[np.asarray(ids)].mean(0)
    return v.astype(np.float32)


def native_relation_vec(E, R, concept, rels_of_concept, word2id):
    """Mean over the concept's WT relations of (nativeE(value) + R[rel_type]) -- native encoding of the
    concept's relational profile. None if the concept has no in-vocab relation."""
    accs = []
    for (r, v) in rels_of_concept:
        vids = phrase_ids(v, word2id)
        if not vids:
            continue
        accs.append(E[np.asarray(vids)].mean(0) + R[REL_IDX[r]])
    if not accs:
        return None
    return np.mean(accs, axis=0).astype(np.float32)


# ---------------------------------------------------------------------------
# ridge map input -> Binder-65 (error-driven least-squares; train-fold only, no leak)
# ---------------------------------------------------------------------------
def ridge_fit(Xtr, Ytr, lam):
    mu = Xtr.mean(0, keepdims=True)
    Xc = Xtr - mu
    n, d = Xc.shape
    A = Xc.T @ Xc + lam * np.eye(d, dtype=np.float64)
    W = np.linalg.solve(A.astype(np.float64), (Xc.T @ Ytr).astype(np.float64))
    b = Ytr.mean(0) - (mu @ W).ravel()
    return W.astype(np.float32), b.astype(np.float32), mu.astype(np.float32)


def ridge_pred(X, W, b, mu):
    return ((X - mu) @ W + b).astype(np.float32)


# ---------------------------------------------------------------------------
# retrieval + discrimination metrics vs Binder-65 gold (derived from the ratings)
# ---------------------------------------------------------------------------
def _cos_row(v, M):
    vn = v / (np.linalg.norm(v) + 1e-12)
    Mn = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return Mn @ vn


def _rankdata(a):
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=np.float64)
    ranks[order] = np.arange(len(a), dtype=np.float64)
    return ranks


def _spearman(x, y):
    rx = _rankdata(x)
    ry = _rankdata(y)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = (np.linalg.norm(rx) * np.linalg.norm(ry)) + 1e-12
    return float((rx @ ry) / denom)


def retrieval_metrics(pred_vecs, true_vecs, held_idx, topk=10):
    """For each held concept: rank the OTHER concepts by cos(pred_c, true_other) vs gold cos(true_c,
    true_other). Returns (mean_p@k, mean_spearman, per_concept_p@k array)."""
    Nc = true_vecs.shape[0]
    pks, sps = [], []
    for local, c in enumerate(held_idx):
        others = np.array([j for j in range(Nc) if j != c])
        gold = _cos_row(true_vecs[c], true_vecs[others])
        pred = _cos_row(pred_vecs[local], true_vecs[others])
        gtop = set(others[np.argsort(-gold)[:topk]].tolist())
        ptop = set(others[np.argsort(-pred)[:topk]].tolist())
        pks.append(len(gtop & ptop) / float(topk))
        sps.append(_spearman(pred, gold))
    return (round(float(np.mean(pks)), 4), round(float(np.mean(sps)), 4), np.asarray(pks))


def discrimination_acc(pred_vecs, true_vecs, held_idx, seed, k_distract=K_DISC):
    """10-way: predicted_c picks c's TRUE profile among k_distract HARD distractors (c's nearest gold
    neighbors), gold at a randomized position. chance = 1/(k+1)."""
    Nc = true_vecs.shape[0]
    correct = np.zeros(len(held_idx), dtype=bool)
    for local, c in enumerate(held_idx):
        others = np.array([j for j in range(Nc) if j != c])
        gold = _cos_row(true_vecs[c], true_vecs[others])
        hard = others[np.argsort(-gold)[:k_distract]]
        _h = hashlib.md5(f"{seed}|{c}".encode()).hexdigest()
        rng = np.random.default_rng(int(_h[:8], 16))
        gpos = int(rng.integers(0, k_distract + 1))
        cand = np.concatenate([hard[:gpos], [c], hard[gpos:]])
        sims = _cos_row(pred_vecs[local], true_vecs[cand])
        correct[local] = (int(np.argmax(sims)) == gpos)
    return round(float(np.mean(correct)), 4)


def _arm_hash(pk_array):
    q = np.round(pk_array * 1000).astype(np.int32)
    return hashlib.sha256(q.tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# earn-and-retrieve one arm (CV over test concepts; no-leak)
# ---------------------------------------------------------------------------
def earn_and_retrieve(inputs, X_true, test_local_idx, all_true_idx, seed, shuffle=False):
    """inputs: [Nc_test, d] input features for the TEST concept set (aligned to test_local_idx which
    index into X_true). X_true: [Nc_all, 65] gold. all_true_idx maps test rows -> row in X_true.
    5-fold CV: fit ridge on train folds' (input, gold), predict held fold, then retrieval + discrim vs
    gold over the FULL X_true pool. shuffle=True permutes the gold target within TRAIN (no-leak proof).
    Returns dict(p_at_10, spearman, disc_acc, n_held, pk_array)."""
    n = inputs.shape[0]
    rng = np.random.default_rng(seed)
    fold = rng.permutation(n) % N_FOLDS
    pred_full = np.zeros((n, _N_FEAT), dtype=np.float32)
    for f in range(N_FOLDS):
        tr = np.where(fold != f)[0]
        te = np.where(fold == f)[0]
        if len(tr) < 5 or len(te) == 0:
            continue
        Ytr = X_true[all_true_idx[tr]].copy()
        if shuffle:
            Ytr = Ytr[rng.permutation(len(Ytr))]
        W, b, mu = ridge_fit(inputs[tr].astype(np.float64), Ytr.astype(np.float64), RIDGE_LAMBDA)
        pred_full[te] = ridge_pred(inputs[te], W, b, mu)
    held_true_rows = all_true_idx  # every test concept is held out once (CV)
    p10, sp, pk = retrieval_metrics(pred_full, X_true, held_true_rows)
    disc = discrimination_acc(pred_full, X_true, held_true_rows, seed)
    return {"p_at_10": p10, "spearman": sp, "disc_acc": disc, "n_held": int(n), "_pk": pk}


def chance_retrieval(X_true, test_true_idx, seed):
    rng = np.random.default_rng(seed + 7)
    pred = rng.standard_normal((len(test_true_idx), _N_FEAT)).astype(np.float32)
    p10, sp, pk = retrieval_metrics(pred, X_true, test_true_idx)
    disc = discrimination_acc(pred, X_true, test_true_idx, seed + 7)
    return {"p_at_10": p10, "spearman": sp, "disc_acc": disc, "n_held": len(test_true_idx), "_pk": pk}


# ---------------------------------------------------------------------------
# run one mode
# ---------------------------------------------------------------------------
def run(mode, output_dir, try_glove=True):
    prof = SMOKE_ENC if mode == "smoke" else FULL_ENC
    seeds = (SEED,) if mode == "smoke" else SEEDS_CV

    # --- Binder grounded gold ---
    _heartbeat(output_dir, "load_binder")
    binder_concepts, X_true, feat_names, nan_count = load_binder(BINDER_CSV)
    cidx = {c: i for i, c in enumerate(binder_concepts)}
    Nb = len(binder_concepts)

    # --- WorldTree relations ---
    _heartbeat(output_dir, "parse_worldtree")
    triples, precision = parse_tables(CURATED_TABLES)
    rels_by_concept = defaultdict(list)
    for (c, r, v) in triples:
        rels_by_concept[c].append((r, v))

    # test concept set = Binder concepts WITH >=1 WT relation (grounded/distributional comparison set)
    rel_concepts = sorted([c for c in binder_concepts if len(rels_by_concept.get(c, [])) >= 1])
    rel_ge2 = [c for c in rel_concepts if len(set(r for (r, _) in rels_by_concept[c])) >= 2]
    _heartbeat(output_dir, "coverage", {"binder": Nb, "rel_ge1": len(rel_concepts),
               "rel_ge2": len(rel_ge2), "nan_imputed": nan_count})

    # --- train the native SGNS encoder over ARC context + WT relations (the ONLY heavy part) ---
    forced = set()
    for (c, r, v) in triples:
        forced.update(_tok_words(c))
        forced.update(_tok_words(v))
    for c in binder_concepts:
        forced.update(_tok_words(c))
    corpus, word2id, id_counts = build_corpus(prof["max_sentences"], forced, output_dir)
    _heartbeat(output_dir, "train_encoder", {"vocab": len(word2id), "steps": prof["steps"]})
    ctx = ContextSampler(corpus, WINDOW, SEED + 1)
    neg = NegSampler(id_counts, UNIGRAM_POW, SEED + 2)
    train_triples = [(c, r, v) for (c, r, v) in triples]  # relation channel trains on all WT (Binder
    #   held-out concepts are held out of the MAP, not the unsupervised encoder -- like GloVe seeing all text)
    rd = RelationData(train_triples, word2id, SEED + 3)
    enc = NativeEncoder(len(word2id), N_DIM, NREL, SEED)
    enc = train_encoder(enc, ctx, neg, rd, prof["steps"], prof["batch"], output_dir, use_relation=True)
    E = enc.E.detach().cpu().numpy().astype(np.float32)
    R = enc.R.detach().cpu().numpy().astype(np.float32)
    enc0 = NativeEncoder(len(word2id), N_DIM, NREL, SEED)   # untrained control
    E0 = enc0.E.detach().cpu().numpy().astype(np.float32)
    R0 = enc0.R.detach().cpu().numpy().astype(np.float32)

    # --- build per-arm input matrices over the rel_concepts test set (ISOLATE input source) ---
    _heartbeat(output_dir, "build_inputs")
    ctx_in, relonly_in, both_in, ctx0_in, keep = [], [], [], [], []
    for c in rel_concepts:
        cv = native_context_vec(E, c, word2id)
        rv = native_relation_vec(E, R, c, rels_by_concept[c], word2id)
        cv0 = native_context_vec(E0, c, word2id)
        if cv is None or rv is None or cv0 is None:
            continue
        ctx_in.append(cv)                              # CONTEXT-ONLY (distributional)
        relonly_in.append(rv)                          # RELATIONS-ONLY (brain-grounded relational signal)
        both_in.append(np.concatenate([cv, rv]))       # BOTH (context + relation structure)
        ctx0_in.append(cv0)
        keep.append(cidx[c])
    keep = np.asarray(keep)
    ctx_in = np.asarray(ctx_in, dtype=np.float32)
    relonly_in = np.asarray(relonly_in, dtype=np.float32)
    both_in = np.asarray(both_in, dtype=np.float32)
    ctx0_in = np.asarray(ctx0_in, dtype=np.float32)
    n_test = len(keep)
    _heartbeat(output_dir, "inputs_built", {"n_test": n_test})

    # --- GloVe baseline input (SMOKE-local; CITED if gensim absent) ---
    glove_in = None
    glove_note = "GloVe baseline CITED-only (gensim not staged to remote GPU / absent locally)"
    if try_glove:
        try:
            from experiments.exp_semantic_hd_encoder_meaning_match_v1 import _load_glove
            kv = _load_glove()

            def _gv(word):
                vs = [kv[w] for w in _tok_words(word) if w in kv]
                return np.sum(vs, axis=0).astype(np.float32) if vs else None
            gl = []
            gkeep = []
            for li, c in enumerate([binder_concepts[j] for j in keep]):
                g = _gv(c)
                if g is not None:
                    gl.append(g)
                    gkeep.append(li)
            if len(gkeep) >= MIN_HELDOUT:
                glove_in = (np.asarray(gl, dtype=np.float32), np.asarray(gkeep))
                glove_note = "MEASURED (frozen GloVe, SMOKE-local, same folds)"
        except Exception as e:
            glove_note = f"GloVe unavailable ({type(e).__name__}: {str(e)[:80]}); CITED-only"

    # --- earn-and-retrieve per arm (multi-seed CV) ---
    def _multiseed(fn):
        accs = defaultdict(list)
        pk_last = None
        for sd in seeds:
            r = fn(sd)
            for k in ("p_at_10", "spearman", "disc_acc"):
                accs[k].append(r[k])
            pk_last = r["_pk"]
        return {k: round(float(np.mean(v)), 4) for k, v in accs.items()} | {"n_held": n_test, "_pk": pk_last}

    _heartbeat(output_dir, "arm_chance")
    A_chance = _multiseed(lambda sd: chance_retrieval(X_true, keep, sd))
    _heartbeat(output_dir, "arm_untrained")
    A_unt = _multiseed(lambda sd: earn_and_retrieve(ctx0_in, X_true, np.arange(n_test), keep, sd))
    _heartbeat(output_dir, "arm_context_only")
    A_ctx = _multiseed(lambda sd: earn_and_retrieve(ctx_in, X_true, np.arange(n_test), keep, sd))
    _heartbeat(output_dir, "arm_relations_only")
    A_rel = _multiseed(lambda sd: earn_and_retrieve(relonly_in, X_true, np.arange(n_test), keep, sd))
    _heartbeat(output_dir, "arm_both")
    A_both = _multiseed(lambda sd: earn_and_retrieve(both_in, X_true, np.arange(n_test), keep, sd))
    _heartbeat(output_dir, "arm_shuffle")
    A_shuf = _multiseed(lambda sd: earn_and_retrieve(relonly_in, X_true, np.arange(n_test), keep, sd, shuffle=True))
    A_glove = None
    if glove_in is not None:
        gl, gkeep = glove_in
        A_glove = _multiseed(lambda sd: earn_and_retrieve(gl, X_true, np.arange(len(gkeep)), keep[gkeep], sd))

    def _p10_ci(a):
        pk = a["_pk"]
        return wilson_ci(int(round(float(np.sum(pk)) * 10)), int(len(pk) * 10)) if len(pk) else (0.0, 0.0)

    rel_ci = _p10_ci(A_rel)
    ctx_ci = _p10_ci(A_ctx)
    both_ci = _p10_ci(A_both)

    # gates
    arm_hashes = {"relations_only": _arm_hash(A_rel["_pk"]), "context_only": _arm_hash(A_ctx["_pk"]),
                  "both": _arm_hash(A_both["_pk"]), "untrained": _arm_hash(A_unt["_pk"]),
                  "shuffle": _arm_hash(A_shuf["_pk"])}
    arms_differ = len({A_rel["p_at_10"], A_ctx["p_at_10"], A_unt["p_at_10"], A_shuf["p_at_10"]}) > 1
    chance_p10 = A_chance["p_at_10"]
    shuffle_collapsed = (A_shuf["p_at_10"] <= chance_p10 + SHUFFLE_EPS)
    rel_generalizes = (rel_ci[0] > chance_p10 and A_rel["p_at_10"] > A_unt["p_at_10"])
    ctx_generalizes = (ctx_ci[0] > chance_p10 and A_ctx["p_at_10"] > A_unt["p_at_10"])
    rel_minus_ctx = round(A_rel["p_at_10"] - A_ctx["p_at_10"], 4)

    verdict, vmsg = _decide_source(A_rel, A_ctx, A_both, A_unt, A_chance, A_glove, A_shuf,
                                   rel_ci, ctx_ci, n_test, shuffle_collapsed, rel_generalizes,
                                   ctx_generalizes, rel_minus_ctx)

    def _clean(a):
        return {k: v for k, v in a.items() if not k.startswith("_")} if a else None

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": f"{verdict}: {vmsg}",
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "device": DEVICE, "seeds": list(seeds),
        "primary_metric": "held-out (5-fold CV, no-leak) retrieval p@10 vs Binder-65 gold neighborhoods; INPUT SOURCE ISOLATED: relations_only vs context_only vs both",
        "one_variable": "input SOURCE to the SAME ridge->Binder-65 map: relations_only (brain-grounded relational) vs context_only (distributional / native-Feature2Vec) vs both; same folds/metric",
        # headline arms (INPUT SOURCE ISOLATED per Director)
        "relations_only_earned": _clean(A_rel), "relations_only_p10_ci": list(rel_ci),
        "context_only_earned": _clean(A_ctx), "context_only_p10_ci": list(ctx_ci),
        "both_earned": _clean(A_both), "both_p10_ci": list(both_ci),
        "glove_earned": _clean(A_glove), "glove_note": glove_note,
        "untrained_input": _clean(A_unt), "shuffle_control": _clean(A_shuf), "chance": _clean(A_chance),
        "relations_only_minus_context_only_p10": rel_minus_ctx,
        "relations_only_generalizes": bool(rel_generalizes), "context_only_generalizes": bool(ctx_generalizes),
        "input_source_note": "relations_only = the brain-consistent test (earn grounded meaning from relational structure); context_only = distributional-to-grounded projection (native Feature2Vec, weaker/less-brain-consistent lever); verdict states which source carries any generalization signal",
        # coverage (headline finding)
        "coverage": {"binder_concepts": Nb, "binder_x_worldtree_ge1_rel": len(rel_concepts),
                     "ge2_rel": len(rel_ge2), "n_test_after_vocab_filter": n_test,
                     "nan_imputed_cells_binder_internal": nan_count,
                     "note": "test set = Binder concepts with >=1 WT relation AND in native vocab; CV over these; retrieval pool = all 534 true Binder-65"},
        # controls / gates
        "shuffle_collapsed": bool(shuffle_collapsed),
        "arms_differ_verified": bool(arms_differ), "arm_pk_hashes": arm_hashes,
        "no_leak": "held-out concepts' Binder vectors NEVER in ridge training (5-fold CV); shuffle-collapse verifies",
        "bands": {"MARGIN": MARGIN, "EPS": EPS, "SHUFFLE_EPS": SHUFFLE_EPS, "MIN_HELDOUT": MIN_HELDOUT,
                  "chance_p10": chance_p10, "K_DISC": K_DISC, "N_FOLDS": N_FOLDS},
        # config
        "config": {"N_DIM": N_DIM, "RIDGE_LAMBDA": RIDGE_LAMBDA, "encoder_profile": prof,
                   "vocab": len(word2id), "n_worldtree_triples": len(triples), "n_binder_features": _N_FEAT,
                   "feature_names_head": feat_names[:6]},
        "objective": "earn held-out concept's Binder-65 grounded vector from native (context+relations) via ridge; NO borrowed vectors in the native encoder (GloVe = eval baseline only)",
        "framing": "MECHANISM test on Binder brain gold (concrete/embodied grounding); WorldTree-PROP=science grounding is disjoint; the science-reasoning application is the FOLLOW-UP not this cell",
        "brain_fidelity": "Binder-65 = operationalized Barsalou brain-system grounding; earn-from-relations = Rogers-McClelland item->attribute; ridge = converged linear error-driven readout (MLP curriculum = follow-up)",
        "final_metrics_atomicity": "tmp_replace", "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True, "progress_logging": "print_flush_true",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_sorted_no_builtin_hash_seeded_rng",
        "storage": "no_composition_selfcontained", "gpu_justification":
        "only the native SGNS encoder over ARC is GPU-worthy (millions of sentences -> quality context vecs = fair distributional baseline); ridge+retrieval CPU-trivial",
        "contract": "SMOKE local; FULL GPU overnight_queue on smoke clearance; no push/remote-persist by exp_dev; no atom banking; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[headline] relations_only p@10={A_rel['p_at_10']} (ci {rel_ci}) disc={A_rel['disc_acc']} | "
          f"context_only p@10={A_ctx['p_at_10']} (ci {ctx_ci}) disc={A_ctx['disc_acc']} | "
          f"both p@10={A_both['p_at_10']} | glove={A_glove['p_at_10'] if A_glove else None} | "
          f"untrained={A_unt['p_at_10']} shuffle={A_shuf['p_at_10']} chance={chance_p10}", flush=True)
    print(f"[gates] n_test={n_test} relations_only-context_only={rel_minus_ctx} "
          f"rel_generalizes={rel_generalizes} ctx_generalizes={ctx_generalizes} "
          f"shuffle_collapsed={shuffle_collapsed} arms_differ={arms_differ}", flush=True)
    return metrics


def _decide_source(A_rel, A_ctx, A_both, A_unt, A_chance, A_glove, A_shuf, rel_ci, ctx_ci, n_test,
                   shuffle_collapsed, rel_gen, ctx_gen, rel_minus_ctx):
    """State WHICH input source carries the generalization signal (Director): relations_only
    (brain-grounded) vs context_only (distributional / native-Feature2Vec)."""
    chance = A_chance["p_at_10"]
    rp, cp = A_rel["p_at_10"], A_ctx["p_at_10"]
    tail = (f"[relations_only p@10={rp} ci{list(rel_ci)} | context_only p@10={cp} ci{list(ctx_ci)} | "
            f"both={A_both['p_at_10']} | untrained={A_unt['p_at_10']} | shuffle={A_shuf['p_at_10']} | "
            f"chance={chance} | glove={A_glove['p_at_10'] if A_glove else 'CITED'}]")
    if n_test < MIN_HELDOUT:
        return "INVALID", f"only {n_test} test concepts (< {MIN_HELDOUT}) -- coverage too thin for stable held-out CV; DATA-COVERAGE finding {tail}"
    if not shuffle_collapsed:
        return "INVALID", f"SHUFFLE did NOT collapse (shuffle p@10={A_shuf['p_at_10']} vs chance {chance}) -- leak/memorization; metric void {tail}"
    if not rel_gen and not ctx_gen:
        return ("NULL-neither-source-generalizes",
                f"NEITHER relations_only nor context_only earns generalizing grounded meaning above the floor "
                f"(chance {chance}, untrained {A_unt['p_at_10']}) -- honest null: no source earns grounded meaning here {tail}")
    # relations-only carries it, and is not beaten by context by more than MARGIN -> the brain-consistent win
    if rel_gen and rel_minus_ctx >= MARGIN:
        return ("GROUNDED-FROM-RELATIONS-CARRIES",
                f"RELATIONS-ONLY carries the signal: relations_only p@10={rp} (ci {list(rel_ci)}) generalizes AND "
                f"BEATS context_only {cp} by {rel_minus_ctx}>={MARGIN}; shuffle collapses -- brain-consistent grounding "
                f"earns generalizing meaning FROM RELATIONAL STRUCTURE {tail}")
    if rel_gen and abs(rel_minus_ctx) < MARGIN:
        return ("BOTH-SOURCES-EARN-relations-genuine",
                f"BOTH sources earn generalizing grounded meaning and are comparable (relations_only {rp} ~= context_only "
                f"{cp}, delta {rel_minus_ctx}); the relations_only arm is a GENUINE brain-grounded signal (not just "
                f"distributional) -- reported separately, not conflated {tail}")
    # context dominates (rel underperforms or does not generalize) -> distributional-to-grounded, NOT the brain result
    return ("CONTEXT-CARRIES-distributional-to-grounded",
            f"CONTEXT-ONLY carries the signal (context_only p@10={cp} > relations_only {rp} by {round(-rel_minus_ctx,4)}; "
            f"relations_only generalizes={rel_gen}). The generalization is DISTRIBUTIONAL-to-grounded projection "
            f"(native Feature2Vec) -- honest, but this is NOT the brain-grounded-from-relations result and is the "
            f"weaker/less-brain-consistent lever; do NOT sell as 'grounding-from-relations works' {tail}")


# ---------------------------------------------------------------------------
# self-test: real code path + planted separability + shuffle-collapse
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] load REAL Binder csv ...", flush=True)
    concepts, X, feats, nan_c = load_binder(BINDER_CSV)
    assert len(concepts) >= 500, f"binder load too few concepts ({len(concepts)})"
    assert X.shape[1] == 65, f"binder feature dim {X.shape[1]} != 65"
    assert not np.isnan(X).any(), "binder NaN not imputed"
    assert len(feats) == 65, "feature names != 65"
    print(f"[self-test]   binder: n={len(concepts)} feat={len(feats)} nan_imputed={nan_c} feats0={feats[:3]}", flush=True)

    print("[self-test] PLANTED separability: input = noisy copy of gold -> earn must generalize; SHUFFLE must collapse ...", flush=True)
    rng = np.random.default_rng(0)
    idx = np.arange(120)
    Xg = X[:120].astype(np.float32)
    # planted informative input = gold + noise (a learnable linear map exists)
    inp = (Xg @ rng.standard_normal((65, 40)).astype(np.float32)) + 0.15 * rng.standard_normal((120, 40)).astype(np.float32)
    keep = idx
    r_real = earn_and_retrieve(inp, X, np.arange(120), keep, SEED)
    r_shuf = earn_and_retrieve(inp, X, np.arange(120), keep, SEED, shuffle=True)
    r_chance = chance_retrieval(X, keep, SEED)
    print(f"[self-test]   planted: real p@10={r_real['p_at_10']} disc={r_real['disc_acc']} | "
          f"shuffle p@10={r_shuf['p_at_10']} | chance p@10={r_chance['p_at_10']}", flush=True)
    assert r_real["p_at_10"] > r_chance["p_at_10"] + 0.05, "planted: informative input did not generalize above chance"
    assert r_shuf["p_at_10"] <= r_chance["p_at_10"] + SHUFFLE_EPS + 0.05, "planted: shuffle did NOT collapse (leak)"
    assert _arm_hash(r_real["_pk"]) != _arm_hash(r_shuf["_pk"]), "real vs shuffle bit-identical"

    print("[self-test] REAL code path: WT parse + tiny ARC encoder + native inputs + ridge CV (both metrics) ...", flush=True)
    triples, prec = parse_tables((("KINDOF", 1, 4), ("HABITAT", 3, 5), ("PROP-MAGNETISM", 0, 3),
                                  ("XIVORE", 1, 4), ("MADEOF", 2, 6), ("PARTOF", 1, 5)))
    rels_by_concept = defaultdict(list)
    for (c, r, v) in triples:
        rels_by_concept[c].append((r, v))
    rel_concepts = [c for c in concepts if len(rels_by_concept.get(c, [])) >= 1]
    assert len(rel_concepts) >= 20, f"real: too few binder-x-WT concepts ({len(rel_concepts)})"
    forced = set()
    for (c, r, v) in triples:
        forced.update(_tok_words(c)); forced.update(_tok_words(v))
    for c in concepts:
        forced.update(_tok_words(c))
    od = _out_dir("_smoke")
    corpus, w2id, idc = build_corpus(4000, forced, od)
    ctx = ContextSampler(corpus, WINDOW, SEED + 1)
    neg = NegSampler(idc, UNIGRAM_POW, SEED + 2)
    rd = RelationData(triples, w2id, SEED + 3)
    enc = NativeEncoder(len(w2id), N_DIM, NREL, SEED)
    enc = train_encoder(enc, ctx, neg, rd, 40, 128, od, use_relation=True)
    E = enc.E.detach().cpu().numpy().astype(np.float32)
    R = enc.R.detach().cpu().numpy().astype(np.float32)
    cidx = {c: i for i, c in enumerate(concepts)}
    rin, keep2 = [], []
    for c in rel_concepts:
        cv = native_context_vec(E, c, w2id)
        rv = native_relation_vec(E, R, c, rels_by_concept[c], w2id)
        if cv is not None and rv is not None:
            rin.append(np.concatenate([cv, rv])); keep2.append(cidx[c])
    rin = np.asarray(rin, dtype=np.float32); keep2 = np.asarray(keep2)
    assert len(keep2) >= 20, f"real: too few usable inputs ({len(keep2)})"
    res = earn_and_retrieve(rin, X, np.arange(len(keep2)), keep2, SEED)
    assert res["p_at_10"] is not None and 0.0 <= res["p_at_10"] <= 1.0, "real: bad p@10"
    # determinism
    c2, X2, _, _ = load_binder(BINDER_CSV)
    assert c2 == concepts and np.allclose(X2, X, equal_nan=True), "real: binder load non-deterministic"
    print(f"[self-test]   real: n_test={len(keep2)} p@10={res['p_at_10']} disc={res['disc_acc']} vocab={len(w2id)}", flush=True)
    print("[self-test] PASS (binder load; planted generalizes + shuffle collapses; real WT+encoder+ridge CV; determinism)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--no-glove", action="store_true")
    args = ap.parse_args()
    _T0[0] = time.perf_counter()

    if args.self_test:
        output_dir = _out_dir("_smoke")
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    output_dir = _out_dir("_smoke") if mode == "smoke" else _out_dir()
    _write_start_marker(output_dir, mode)
    try_glove = (mode == "smoke") and (not args.no_glove)
    run(mode, output_dir, try_glove=try_glove)
    sys.exit(0)


if __name__ == "__main__":
    _od = _out_dir("_smoke") if ("--smoke" in sys.argv or "--self-test" in sys.argv) else _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
