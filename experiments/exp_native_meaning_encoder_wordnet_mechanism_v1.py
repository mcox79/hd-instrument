"""native_meaning_encoder_wordnet_mechanism_v1 -- CAN MECHANISM RESCUE RELATIONAL GROUNDING?

REFRAME (VET seq 29564, commit e45e89f0e): "densify relations" is NOT the lever. Per-concept
corr(n_relations, relations p@10) ~= -0.007 (~zero); dense strata ANTI-scale (k>=4 collapses to
0.121). The predecessor's weak relations-arm (p@10 0.139 vs context 0.243) and the "relations DILUTE
context" artifact (both=0.204 < context=0.243) are almost certainly MECHANISM artifacts, not a data
wall:
  (1) DENSE-CODE SUPERPOSITION CROSSTALK: mean-bundling many dense R^300 relation vectors blurs the
      centroid (the density-collapse-at-high-k IS the crosstalk signature). FIX = SPARSE codes (many
      relations compose with low crosstalk; cortical). Reuse the certified GSBC graded-sparse-block
      code (_gsbc_code_from_z).
  (2) NAIVE CONCAT + SINGLE GLOBAL RIDGE LAMBDA: noisy relation dims add variance under one lambda so
      relations "hurt" when concatenated with context. FIX = WEIGHTED / PER-BLOCK FUSION (block-diag
      ridge lambda; relation block regularized separately, multiplier chosen by inner-CV on TRAIN
      only) -- a learned/weighted readout, not one global lambda.

THE VARIABLE IS THE MECHANISM, not the relation count. WordNet supplies a RICHER structural relation
set (mean ~30-70 rels/concept vs WorldTree ~2.4) = more raw material for the mechanism to work with;
density is INSTRUMENTED (crosstalk recovery margin), not the hypothesis under test.

MATRIX (same held-out split / metric / concept set; ONE variable = the mechanism):
  relations-alone x {DENSE, SPARSE} : does sparse coding rescue the relations-only signal past 0.139?
  fused (context + relations) x {naive-concat-single-lambda, weighted-block-diag-fusion} x {DENSE,
    SPARSE relation code} : does better fusion stop relations from diluting context (both>context)?
  secondary encoding lever: typed-BIND (circular-conv bind of a role key with E[value]) vs the
    predecessor's additive mean-of-(E[value]+R[reltype]).
  cross-density check: run the SPARSE relations-alone arm on the WorldTree-SPARSE set too -- does the
    mechanism fix help REGARDLESS of density?

FIXED BASELINES / CONTROLS (reproduce predecessor = Gate D positive controls):
  context_only (~0.2426), relations_worldtree_dense_naive (~0.139), both_dense_naiveconcat (~0.204),
  untrained_input (~0.033), chance (~0.026), shuffle (permute relation->Binder target in TRAIN; MUST
  collapse to ~chance = no-leak proof).

BRAIN-CONSISTENCY: WordNet structural relations = SUPPLIED clean vetted structure (PIVOT; same KIND as
WorldTree typed relations, just broader) -- NOT a borrowed distributional embedding. Sparse codes =
cortical low-crosstalk composition. The native encoder is trained ONLY by error-driven context(ARC) +
relation(WorldTree) prediction; NO GloVe/BGE in the learned rep. WordNet was earlier "supply-semantic"
for SIMILARITY (29533) but that augmented GloVe for similarity; HERE WordNet is the structural
relational INPUT to earn grounding + the mechanism levers operate on the SUBSTRATE's own codes -- a
different + fair use. Polysemy handled honestly: FIRST (most-frequent) noun synset per concept.

DECISIVE READ (a priori bands; gates apply to the relations / fused arms vs the fixed baselines):
  MECHANISM-RESCUED (real path) = a SPARSE and/or WEIGHTED-FUSION (and/or typed-BIND) arm lifts the
    relational contribution MEANINGFULLY past 0.139 toward/above context 0.243 -- EITHER relations-
    alone >= 0.139 + LIFT and generalizes (S1), OR a WEIGHTED-fusion arm > context_only + FUSE_EPS AND
    beats its own naive-concat sibling (S2, fusion fixed the dilution) -- with shuffle-collapse + no-
    leak. Report WHICH lever rescued.
  HONEST-WALL (structure alone insufficient) = NONE of {sparse, weighted-fusion, typed-bind} lifts
    relations past ~0.139 (all within FLAT_EPS of 0.139) AND no fused arm beats context -> relational
    grounding is genuinely mechanism+data limited even after the nearest fixes; grounding needs more
    than taxonomy (sensorimotor/Barsalou) -- the honest deep finding.
  MIDDLE = some lift (> 0.139 + LIFT) but below context and fusion does not beat context.
  INVALID = shuffle does NOT collapse (leak) OR n_test < MIN_HELDOUT OR positive controls do not
    reproduce (context out of [0.20,0.29] or relations_worldtree out of [0.10,0.18]) = Gate D fail.

CROSSTALK INSTRUMENTATION (confirm/refute the crosstalk hypothesis directly): per-concept constituent-
recovery margin (mean cos(bundle, own constituent) - mean cos(bundle, other concepts' constituents))
for the DENSE-summed vs SPARSE-summed WordNet relation bundle. If sparse margin >> dense margin AND
sparse arm >> dense arm -> crosstalk WAS the limiter. If sparse margin >> dense but both arms flat ->
NOT crosstalk; structure genuinely insufficient.

CELL-TEMPLATE MANDATORY: except SystemExit before Exception (no BaseException/bare); tmp_replace atomic
metrics; start-marker + crash-diagnostic + heartbeat; arms_differ (per-arm metric hashes); determin-
istic (fixed int seeds, numpy default_rng, sorted(set)); real code path in self-test (REAL Binder csv +
REAL WT parse + REAL WordNet extract + REAL encoder + REAL GSBC sparse code + REAL ridge/fusion CV at
tiny scale + planted separability + shuffle-collapse + sparse-lowers-crosstalk assertion); progress
print_flush_true; all numbers MEASURED@ this metrics.json.

Contract: prereg + self-test + INLINE-LOCAL CPU FOREGROUND (Binder+WordNet local, small scale ~139
matched concepts, SGNS at SMOKE_ENC ~70k sentences = predecessor's 147s regime); metrics.json; commit
cell+prereg by explicit path; NO atom banking (skunkworks owns VET); VET-PENDING. ASCII-only.
"""
from __future__ import annotations

import os
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

# reuse the committed baseline cell's native-encoder machinery + the predecessor grounded-cell helpers
from experiments.exp_native_meaning_encoder_scale_v1 import (  # noqa: E402
    parse_tables, normalize_phrase, wilson_ci, build_corpus, ContextSampler, NegSampler,
    RelationData, NativeEncoder, train_encoder, phrase_ids, _tok_words,
    CURATED_TABLES, REL_IDX, NREL, N_DIM, UNIGRAM_POW, WINDOW)
from experiments.exp_native_meaning_encoder_binder_grounded_v1 import (  # noqa: E402
    load_binder, native_context_vec, ridge_pred, retrieval_metrics, discrimination_acc,
    _cos_row, BINDER_CSV, _N_FEAT)
# reuse the certified GSBC graded-sparse-block code (existing sparse machinery)
from experiments.exp_encoder_v11_gsbc_graded_sparse_v1_core import _gsbc_code_from_z  # noqa: E402

ANCHOR_NAME = "native_meaning_encoder_wordnet_mechanism_v1"

SEED = 20260725
N_FOLDS = 5
RIDGE_LAMBDA = 10.0                 # 300-dim faithful arms (matches predecessor)
RIDGE_LAMBDA_HD = 10.0 * (4096.0 / 300.0)  # dim-scaled for 4096-dim sparse arms (declared, NOT tuned-for-PASS)
FUSION_REL_MULT_GRID = (1.0, 10.0, 30.0)   # weighted-fusion: relation-block lambda multiplier (inner-CV select)
INNER_FOLDS = 3
MIN_HELDOUT = 40

# GSBC sparse-block geometry (g0-class certified operating point): kb*blk_l=4096, m=3 -> ~4.7% active
GSBC_KB, GSBC_BLK, GSBC_M, GSBC_TAU = 64, 64, 3, 0.1
SPARSE_DIM = GSBC_KB * GSBC_BLK

# WordNet relation extraction caps (bound the noisy co-hyponym / SIMILAR tail)
CAP_SIMILAR = 20                    # deterministic first-N sisters (sorted lemma) to avoid 900-relation blur
CAP_TOTAL = 60                      # total relations/concept cap (hypernym+meronym first, then similar)

SMOKE_ENC = dict(max_sentences=70_000, steps=1_500, batch=512)
FULL_ENC = dict(max_sentences=6_000_000, steps=120_000, batch=4096)

# pre-registered bands
LIFT = 0.05                        # relations-alone must beat 0.139 by this to count as a rescue
FLAT_EPS = 0.03                    # within 0.139 +/- this = FLAT (no rescue)
FUSE_EPS = 0.01                    # fused arm must beat context by this to count as fusion-rescue
SHUFFLE_EPS = 0.03
CTX_LO, CTX_HI = 0.20, 0.29        # Gate D: context positive-control band
WT_LO, WT_HI = 0.10, 0.18          # Gate D: relations_worldtree positive-control band

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
# WordNet structural relation extraction (SUPPLIED clean structure; first noun synset = honest polysemy)
# ---------------------------------------------------------------------------
def wordnet_rels(concept, wn):
    """Return sorted list of (COARSE_REL, value_str) for the concept's FIRST (most-frequent) noun synset.
    hypernym CLOSURE -> KINDOF; part meronyms -> PARTOF; substance meronyms -> MADEOF; member holonyms ->
    PARTOF; co-hyponyms (sisters) -> SIMILAR (capped). None if no noun synset. Deterministic."""
    w = concept.replace(" ", "_")
    syns = wn.synsets(w, pos=wn.NOUN)
    if not syns:
        toks = _tok_words(concept)
        if len(toks) == 1:
            syns = wn.synsets(toks[0], pos=wn.NOUN)
    if not syns:
        return None
    s = syns[0]
    core, sim = [], []
    for h in s.closure(lambda x: x.hypernyms()):
        for l in h.lemmas():
            core.append(("KINDOF", l.name()))
    for m in s.part_meronyms():
        for l in m.lemmas():
            core.append(("PARTOF", l.name()))
    for m in s.substance_meronyms():
        for l in m.lemmas():
            core.append(("MADEOF", l.name()))
    for m in s.member_holonyms():
        for l in m.lemmas():
            core.append(("PARTOF", l.name()))
    for hyp in s.hypernyms():
        for co in hyp.hyponyms():
            if co != s:
                for l in co.lemmas():
                    sim.append(("SIMILAR", l.name()))
    core = sorted(set(core))
    sim = sorted(set(sim))[:CAP_SIMILAR]
    out = (core + sim)[:CAP_TOTAL]
    return out


# ---------------------------------------------------------------------------
# relation encoders (native): additive-mean (predecessor) / typed-bind / per-relation vectors
# ---------------------------------------------------------------------------
def _rel_offset(R, rel):
    """Learned relation-type offset if the coarse rel exists in the encoder's R table, else zero (SIMILAR
    has no trained slot -> carried by the value embedding only; declared/conservative)."""
    if rel in REL_IDX and REL_IDX[rel] < R.shape[0]:
        return R[REL_IDX[rel]]
    return np.zeros(R.shape[1], dtype=np.float32)


def per_relation_vecs(E, R, rels, word2id):
    """List of native per-relation vectors E[value].mean + R[reltype] (R^300). Skips OOV values."""
    out = []
    for (r, v) in rels:
        vids = phrase_ids(v.replace("_", " "), word2id)
        if not vids:
            continue
        out.append((E[np.asarray(vids)].mean(0) + _rel_offset(R, r)).astype(np.float32))
    return out


def rel_dense_mean(E, R, rels, word2id):
    """Predecessor-faithful DENSE bundle: mean over relations of (E[value]+R[reltype]) in R^300."""
    accs = per_relation_vecs(E, R, rels, word2id)
    if not accs:
        return None
    return np.mean(accs, axis=0).astype(np.float32)


def _cconv(a, b):
    """Circular convolution (HRR bind) via FFT."""
    return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=len(a)).astype(np.float32)


def _role_key(rel):
    """Deterministic bipolar role key per relation type (typed-BIND encoding)."""
    h = int(hashlib.md5(("ROLE|" + rel).encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(h)
    return rng.standard_normal(N_DIM).astype(np.float32) / np.sqrt(N_DIM)


def rel_typed_bind(E, R, rels, word2id):
    """Typed-BIND bundle: mean over relations of cconv(role_key[reltype], E[value]) in R^300."""
    accs = []
    for (r, v) in rels:
        vids = phrase_ids(v.replace("_", " "), word2id)
        if not vids:
            continue
        accs.append(_cconv(_role_key(r), E[np.asarray(vids)].mean(0)))
    if not accs:
        return None
    return np.mean(accs, axis=0).astype(np.float32)


def _lift_matrix(seed=SEED + 99):
    rng = np.random.default_rng(seed)
    return (rng.standard_normal((N_DIM, SPARSE_DIM)).astype(np.float32) / np.sqrt(N_DIM))


def rel_sparse_bundle(E, R, rels, word2id, W_lift, return_constituents=False):
    """SPARSE bundle: each per-relation R^300 vec lifted (fixed random proj -> R^4096), GSBC-sparsified
    (top-m per block, ~4.7% active), then SUMMED (low-crosstalk composition). L2-normalized. Optionally
    returns the per-relation sparse constituents (for crosstalk instrumentation)."""
    dv = per_relation_vecs(E, R, rels, word2id)
    if not dv:
        return (None, None) if return_constituents else None
    z = np.stack(dv, axis=0) @ W_lift                       # [n_rel, 4096]
    zt = torch.from_numpy(z.astype(np.float32))
    with torch.no_grad():
        s = _gsbc_code_from_z(zt, GSBC_KB, GSBC_BLK, GSBC_M, GSBC_TAU).cpu().numpy().astype(np.float32)
    bundle = s.sum(axis=0)
    nb = bundle / (np.linalg.norm(bundle) + 1e-12)
    if return_constituents:
        return nb.astype(np.float32), s
    return nb.astype(np.float32)


KWTA_K = 45                        # sign-preserving top-K per per-relation code (15% of N_DIM=300)


def rel_sparse_kwta(E, R, rels, word2id, return_constituents=False):
    """FAITHFUL sparse bundle (no random-projection loss): each per-relation R^300 code is sparsified by
    sign-preserving k-WTA (keep the top-KWTA_K |.| dims of the LEARNED code, zero the rest), then SUMMED
    (sparse codes occupy different dims -> low-crosstalk composition, unlike the dense MEAN which blurs).
    Preserves the trained-encoder geometry (contrast: the GSBC random-lift arm is lossy)."""
    dv = per_relation_vecs(E, R, rels, word2id)
    if not dv:
        return (None, None) if return_constituents else None
    cons = []
    for v in dv:
        s = np.zeros_like(v)
        idx = np.argsort(-np.abs(v))[:KWTA_K]
        s[idx] = v[idx]
        s = s / (np.linalg.norm(s) + 1e-12)
        cons.append(s.astype(np.float32))
    bundle = np.sum(cons, axis=0)
    nb = (bundle / (np.linalg.norm(bundle) + 1e-12)).astype(np.float32)
    if return_constituents:
        return nb, np.stack(cons, axis=0)
    return nb


def rel_dense_lifted(E, R, rels, word2id, W_lift, return_constituents=False):
    """DENSE-lifted control: same lift to R^4096 and SUM but NO sparsify (dense high-dim sum). Isolates
    the sparsify step (SPARSE vs this = pure coding-regime delta at matched dim + op)."""
    dv = per_relation_vecs(E, R, rels, word2id)
    if not dv:
        return (None, None) if return_constituents else None
    d = np.stack(dv, axis=0) @ W_lift                       # [n_rel, 4096] dense
    dn = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-12)
    bundle = dn.sum(axis=0)
    nb = bundle / (np.linalg.norm(bundle) + 1e-12)
    if return_constituents:
        return nb.astype(np.float32), dn.astype(np.float32)
    return nb.astype(np.float32)


# ---------------------------------------------------------------------------
# ridge (scalar OR per-dim diagonal lambda) + fusion + earn-and-retrieve
# ---------------------------------------------------------------------------
def ridge_fit_diag(Xtr, Ytr, lam):
    """Ridge with lam scalar OR per-dim vector (block-diagonal regularization = weighted fusion)."""
    mu = Xtr.mean(0, keepdims=True)
    Xc = (Xtr - mu).astype(np.float64)
    d = Xc.shape[1]
    lam_vec = np.full(d, float(lam), dtype=np.float64) if np.isscalar(lam) else np.asarray(lam, dtype=np.float64)
    A = Xc.T @ Xc + np.diag(lam_vec)
    W = np.linalg.solve(A, Xc.T @ Ytr.astype(np.float64))
    b = Ytr.mean(0) - (mu.astype(np.float64) @ W).ravel()
    return W.astype(np.float32), b.astype(np.float32), mu.astype(np.float32)


def _select_rel_mult(Xtr, Ytr, d_ctx, base_lam, grid, seed):
    """Inner-CV (TRAIN-only, no leak) select the relation-block lambda multiplier minimizing held-inner
    prediction MSE. d_ctx = number of leading context dims (lambda=base_lam); remaining = relation dims
    (lambda=base_lam*mult)."""
    n, d = Xtr.shape
    rng = np.random.default_rng(seed + 555)
    fold = rng.permutation(n) % INNER_FOLDS
    best_mult, best_mse = grid[0], np.inf
    for mult in grid:
        lam_vec = np.concatenate([np.full(d_ctx, base_lam), np.full(d - d_ctx, base_lam * mult)])
        mse = 0.0
        cnt = 0
        for f in range(INNER_FOLDS):
            tr = np.where(fold != f)[0]
            te = np.where(fold == f)[0]
            if len(tr) < 5 or len(te) == 0:
                continue
            W, b, mu = ridge_fit_diag(Xtr[tr], Ytr[tr], lam_vec)
            pred = ridge_pred(Xtr[te], W, b, mu)
            mse += float(np.mean((pred - Ytr[te]) ** 2)) * len(te)
            cnt += len(te)
        mse = mse / max(cnt, 1)
        if mse < best_mse:
            best_mse, best_mult = mse, mult
    return best_mult


def earn(inputs, X_true, keep, seeds, fit_builder, shuffle=False):
    """5-fold CV earn-and-retrieve (no-leak). fit_builder(Xtr,Ytr,seed)->predict(Xte). shuffle permutes the
    gold target within TRAIN (no-leak proof). Returns dict with mean p@10 / spearman / disc / _pk."""
    n = inputs.shape[0]
    accs = defaultdict(list)
    pk_last = None
    for sd in seeds:
        rng = np.random.default_rng(sd)
        fold = rng.permutation(n) % N_FOLDS
        pred_full = np.zeros((n, _N_FEAT), dtype=np.float32)
        for f in range(N_FOLDS):
            tr = np.where(fold != f)[0]
            te = np.where(fold == f)[0]
            if len(tr) < 5 or len(te) == 0:
                continue
            Ytr = X_true[keep[tr]].copy()
            if shuffle:
                Ytr = Ytr[rng.permutation(len(Ytr))]
            predict = fit_builder(inputs[tr].astype(np.float64), Ytr.astype(np.float64), sd)
            pred_full[te] = predict(inputs[te])
        p10, sp, pk = retrieval_metrics(pred_full, X_true, keep)
        disc = discrimination_acc(pred_full, X_true, keep, sd)
        accs["p_at_10"].append(p10)
        accs["spearman"].append(sp)
        accs["disc_acc"].append(disc)
        pk_last = pk
    return {k: round(float(np.mean(v)), 4) for k, v in accs.items()} | {"n_held": int(n), "_pk": pk_last}


def _ridge_builder(lam):
    def bld(Xtr, Ytr, sd):
        W, b, mu = ridge_fit_diag(Xtr, Ytr, lam)
        return lambda Xte: ridge_pred(Xte, W, b, mu)
    return bld


def _weighted_fusion_builder(d_ctx, base_lam, grid):
    def bld(Xtr, Ytr, sd):
        mult = _select_rel_mult(Xtr, Ytr, d_ctx, base_lam, grid, sd)
        d = Xtr.shape[1]
        lam_vec = np.concatenate([np.full(d_ctx, base_lam), np.full(d - d_ctx, base_lam * mult)])
        W, b, mu = ridge_fit_diag(Xtr, Ytr, lam_vec)
        return lambda Xte: ridge_pred(Xte, W, b, mu)
    return bld


def chance_retrieval(X_true, keep, seed):
    rng = np.random.default_rng(seed + 7)
    pred = rng.standard_normal((len(keep), _N_FEAT)).astype(np.float32)
    p10, sp, pk = retrieval_metrics(pred, X_true, keep)
    disc = discrimination_acc(pred, X_true, keep, seed + 7)
    return {"p_at_10": p10, "spearman": sp, "disc_acc": disc, "n_held": len(keep), "_pk": pk}


def _arm_hash(pk_array):
    q = np.round(pk_array * 1000).astype(np.int32)
    return hashlib.sha256(q.tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# crosstalk instrumentation: constituent-recovery margin (dense-sum vs sparse-sum bundle)
# ---------------------------------------------------------------------------
def crosstalk_stats(bundles, constituents, seed=SEED):
    """Crosstalk instrumentation for a SUM bundle b = sum_r constituent_r.
    own      = mean cos(bundle_c, own constituent_r) -- how recoverable each relation is from its bundle.
    cross    = mean cos(bundle_c, OTHER concepts' constituents) -- baseline overlap (biased UP for the
               non-negative GSBC code, so report separately; interpret own-vs-cross margin with that caveat).
    margin   = own - cross.
    pairwise = mean cos between a concept's OWN constituents (within-bundle interference; LOWER = the
               relation codes are more orthogonal = compose with LESS crosstalk). This is the fairest
               regime-comparison (independent of the sum + non-negativity offset).
    Returns {own, cross, margin, pairwise_overlap}."""
    rng = np.random.default_rng(seed + 321)
    idxs = [i for i in range(len(bundles)) if constituents[i] is not None and len(constituents[i]) >= 2]
    owns, crosses, pairs = [], [], []
    for i in idxs:
        b = bundles[i]
        C = constituents[i]
        owns.append(float(np.mean(_cos_row(b, C))))
        others = [j for j in idxs if j != i]
        if others:
            picks = rng.choice(others, size=min(8, len(others)), replace=False)
            crosses.append(float(np.mean([np.mean(_cos_row(b, constituents[j])) for j in picks])))
        Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
        G = Cn @ Cn.T
        n = G.shape[0]
        pairs.append(float((G.sum() - np.trace(G)) / (n * (n - 1))))
    own = round(float(np.mean(owns)), 4) if owns else 0.0
    cross = round(float(np.mean(crosses)), 4) if crosses else 0.0
    return {"own": own, "cross": cross, "margin": round(own - cross, 4),
            "pairwise_overlap": round(float(np.mean(pairs)), 4) if pairs else 0.0}


# ---------------------------------------------------------------------------
# run one mode
# ---------------------------------------------------------------------------
def run(mode, output_dir):
    from nltk.corpus import wordnet as wn
    prof = SMOKE_ENC if mode == "smoke" else FULL_ENC
    seeds = (SEED,) if mode == "smoke" else (SEED, 13, 101)

    _heartbeat(output_dir, "load_binder")
    binder_concepts, X_true, feat_names, nan_count = load_binder(BINDER_CSV)
    cidx = {c: i for i, c in enumerate(binder_concepts)}
    Nb = len(binder_concepts)

    _heartbeat(output_dir, "parse_worldtree")
    triples, precision = parse_tables(CURATED_TABLES)
    wt_by_concept = defaultdict(list)
    for (c, r, v) in triples:
        wt_by_concept[c].append((r, v))

    _heartbeat(output_dir, "extract_wordnet")
    wn_by_concept = {}
    for c in binder_concepts:
        rs = wordnet_rels(c, wn)
        if rs:
            wn_by_concept[c] = rs
    n_binder_wn_broad = len(wn_by_concept)

    # matched set = Binder concepts with a WorldTree relation AND a WordNet noun synset (clean ONE-variable
    # cross-arm comparison; reproduces the predecessor's 0.139/0.243 on the same concepts)
    matched = sorted([c for c in binder_concepts
                      if len(wt_by_concept.get(c, [])) >= 1 and c in wn_by_concept])
    _heartbeat(output_dir, "coverage", {"binder": Nb, "matched": len(matched),
               "binder_wn_broad": n_binder_wn_broad, "nan_imputed": nan_count})

    # --- train the native SGNS encoder over ARC context + WT relations (identical to predecessor) ---
    forced = set()
    for (c, r, v) in triples:
        forced.update(_tok_words(c)); forced.update(_tok_words(v))
    for c in binder_concepts:
        forced.update(_tok_words(c))
    for c, rs in wn_by_concept.items():
        for (r, v) in rs:
            forced.update(_tok_words(v.replace("_", " ")))
    corpus, word2id, id_counts = build_corpus(prof["max_sentences"], forced, output_dir)
    _heartbeat(output_dir, "train_encoder", {"vocab": len(word2id), "steps": prof["steps"]})
    ctx = ContextSampler(corpus, WINDOW, SEED + 1)
    neg = NegSampler(id_counts, UNIGRAM_POW, SEED + 2)
    rd = RelationData(list(triples), word2id, SEED + 3)
    enc = NativeEncoder(len(word2id), N_DIM, NREL, SEED)
    enc = train_encoder(enc, ctx, neg, rd, prof["steps"], prof["batch"], output_dir, use_relation=True)
    E = enc.E.detach().cpu().numpy().astype(np.float32)
    R = enc.R.detach().cpu().numpy().astype(np.float32)
    enc0 = NativeEncoder(len(word2id), N_DIM, NREL, SEED)
    E0 = enc0.E.detach().cpu().numpy().astype(np.float32)

    W_lift = _lift_matrix()

    # --- build per-concept inputs on the matched set (isolate every arm's source/coding) ---
    _heartbeat(output_dir, "build_inputs")
    keep, ctx_in, ctx0_in = [], [], []
    rel_wt_d, rel_wn_d, rel_wn_bind = [], [], []
    rel_wn_sp, rel_wn_dl, rel_wt_sp = [], [], []
    rel_wn_kw, rel_wt_kw = [], []
    wn_sp_const, wn_dl_const, wn_kw_const = [], [], []
    wt_counts, wn_counts = [], []
    for c in matched:
        cv = native_context_vec(E, c, word2id)
        cv0 = native_context_vec(E0, c, word2id)
        rwt = rel_dense_mean(E, R, wt_by_concept[c], word2id)
        rwn = rel_dense_mean(E, R, wn_by_concept[c], word2id)
        rbn = rel_typed_bind(E, R, wn_by_concept[c], word2id)
        rsp, sp_const = rel_sparse_bundle(E, R, wn_by_concept[c], word2id, W_lift, return_constituents=True)
        rdl, dl_const = rel_dense_lifted(E, R, wn_by_concept[c], word2id, W_lift, return_constituents=True)
        rwtsp = rel_sparse_bundle(E, R, wt_by_concept[c], word2id, W_lift)
        rkw, kw_const = rel_sparse_kwta(E, R, wn_by_concept[c], word2id, return_constituents=True)
        rwtkw = rel_sparse_kwta(E, R, wt_by_concept[c], word2id)
        if any(x is None for x in (cv, cv0, rwt, rwn, rbn, rsp, rdl, rwtsp, rkw, rwtkw)):
            continue
        keep.append(cidx[c]); ctx_in.append(cv); ctx0_in.append(cv0)
        rel_wt_d.append(rwt); rel_wn_d.append(rwn); rel_wn_bind.append(rbn)
        rel_wn_sp.append(rsp); rel_wn_dl.append(rdl); rel_wt_sp.append(rwtsp)
        rel_wn_kw.append(rkw); rel_wt_kw.append(rwtkw)
        wn_sp_const.append(sp_const); wn_dl_const.append(dl_const); wn_kw_const.append(kw_const)
        wt_counts.append(len(wt_by_concept[c])); wn_counts.append(len(wn_by_concept[c]))
    keep = np.asarray(keep)
    ctx_in = np.asarray(ctx_in, np.float32); ctx0_in = np.asarray(ctx0_in, np.float32)
    rel_wt_d = np.asarray(rel_wt_d, np.float32); rel_wn_d = np.asarray(rel_wn_d, np.float32)
    rel_wn_bind = np.asarray(rel_wn_bind, np.float32)
    rel_wn_sp = np.asarray(rel_wn_sp, np.float32); rel_wn_dl = np.asarray(rel_wn_dl, np.float32)
    rel_wt_sp = np.asarray(rel_wt_sp, np.float32)
    rel_wn_kw = np.asarray(rel_wn_kw, np.float32); rel_wt_kw = np.asarray(rel_wt_kw, np.float32)
    n_test = len(keep)
    _heartbeat(output_dir, "inputs_built", {"n_test": n_test,
               "mean_wt_rels": round(float(np.mean(wt_counts)), 2),
               "mean_wn_rels": round(float(np.mean(wn_counts)), 2)})

    # fused inputs (context ++ relation code)
    both_wn_d = np.concatenate([ctx_in, rel_wn_d], axis=1)
    both_wn_sp = np.concatenate([ctx_in, rel_wn_sp], axis=1)
    both_wn_kw = np.concatenate([ctx_in, rel_wn_kw], axis=1)

    R_L = _ridge_builder(RIDGE_LAMBDA)
    R_HD = _ridge_builder(RIDGE_LAMBDA_HD)

    # ---- arms ----
    _heartbeat(output_dir, "arm_chance")
    A = {}
    A["chance"] = chance_retrieval(X_true, keep, SEED)
    _heartbeat(output_dir, "arm_context_only")
    A["context_only"] = earn(ctx_in, X_true, keep, seeds, R_L)
    _heartbeat(output_dir, "arm_untrained")
    A["untrained_input"] = earn(ctx0_in, X_true, keep, seeds, R_L)
    # relations-alone x {DENSE, SPARSE} (+ typed-bind, + dense-lifted control, + WT cross-density)
    _heartbeat(output_dir, "arm_rel_wt_dense")
    A["relations_worldtree_dense_naive"] = earn(rel_wt_d, X_true, keep, seeds, R_L)     # ~0.139 control
    _heartbeat(output_dir, "arm_rel_wn_dense")
    A["relations_wordnet_dense_naive"] = earn(rel_wn_d, X_true, keep, seeds, R_L)
    _heartbeat(output_dir, "arm_rel_wn_denselifted")
    A["relations_wordnet_dense_lifted"] = earn(rel_wn_dl, X_true, keep, seeds, R_HD)
    _heartbeat(output_dir, "arm_rel_wn_sparse_gsbc")
    A["relations_wordnet_sparse_gsbc_naive"] = earn(rel_wn_sp, X_true, keep, seeds, R_HD)   # SPARSE lever (GSBC lift)
    _heartbeat(output_dir, "arm_rel_wn_sparse_kwta")
    A["relations_wordnet_sparse_kwta_naive"] = earn(rel_wn_kw, X_true, keep, seeds, R_L)    # SPARSE lever (faithful kWTA)
    _heartbeat(output_dir, "arm_rel_wn_bind")
    A["relations_wordnet_typedbind_naive"] = earn(rel_wn_bind, X_true, keep, seeds, R_L)  # encoding lever
    _heartbeat(output_dir, "arm_rel_wt_sparse_gsbc")
    A["relations_worldtree_sparse_gsbc_naive"] = earn(rel_wt_sp, X_true, keep, seeds, R_HD)  # GSBC-lossy validity check
    _heartbeat(output_dir, "arm_rel_wt_sparse_kwta")
    A["relations_worldtree_sparse_kwta_naive"] = earn(rel_wt_kw, X_true, keep, seeds, R_L)   # kWTA non-lossy validity check
    # fused x {naive-concat-single-lambda, weighted-block-diag-fusion} x {DENSE, SPARSE}
    _heartbeat(output_dir, "arm_both_wn_dense_naive")
    A["both_wordnet_dense_naiveconcat"] = earn(both_wn_d, X_true, keep, seeds, R_L)      # ~0.204 control
    _heartbeat(output_dir, "arm_both_wn_dense_weighted")
    A["both_wordnet_dense_weighted"] = earn(both_wn_d, X_true, keep, seeds,
                                            _weighted_fusion_builder(N_DIM, RIDGE_LAMBDA, FUSION_REL_MULT_GRID))
    _heartbeat(output_dir, "arm_both_wn_sparse_naive")
    A["both_wordnet_sparse_naiveconcat"] = earn(both_wn_sp, X_true, keep, seeds, R_L)
    _heartbeat(output_dir, "arm_both_wn_sparse_weighted")
    A["both_wordnet_sparse_weighted"] = earn(both_wn_sp, X_true, keep, seeds,
                                             _weighted_fusion_builder(N_DIM, RIDGE_LAMBDA, FUSION_REL_MULT_GRID))
    _heartbeat(output_dir, "arm_both_wn_kwta_weighted")
    A["both_wordnet_kwta_weighted"] = earn(both_wn_kw, X_true, keep, seeds,
                                           _weighted_fusion_builder(N_DIM, RIDGE_LAMBDA, FUSION_REL_MULT_GRID))
    # shuffle control on a best-shot relation arm (faithful kWTA sparse)
    _heartbeat(output_dir, "arm_shuffle")
    A["shuffle_wordnet_kwta"] = earn(rel_wn_kw, X_true, keep, seeds, R_L, shuffle=True)

    # crosstalk instrumentation
    _heartbeat(output_dir, "crosstalk")
    dense_ct = crosstalk_stats(list(rel_wn_dl), wn_dl_const)
    sparse_ct = crosstalk_stats(list(rel_wn_sp), wn_sp_const)
    kwta_ct = crosstalk_stats(list(rel_wn_kw), wn_kw_const)

    # CIs
    def _ci(a):
        pk = a["_pk"]
        return wilson_ci(int(round(float(np.sum(pk)) * 10)), int(len(pk) * 10)) if pk is not None and len(pk) else (0.0, 0.0)

    p = {k: A[k]["p_at_10"] for k in A}
    chance = p["chance"]
    ctx = p["context_only"]
    wt_dense = p["relations_worldtree_dense_naive"]
    both_naive_d = p["both_wordnet_dense_naiveconcat"]

    # rescue signals
    rel_alone_arms = {k: p[k] for k in ("relations_wordnet_dense_naive", "relations_wordnet_sparse_gsbc_naive",
                                        "relations_wordnet_sparse_kwta_naive", "relations_wordnet_typedbind_naive",
                                        "relations_worldtree_sparse_kwta_naive")}
    best_rel_alone_arm = max(rel_alone_arms, key=rel_alone_arms.get)
    best_rel_alone = rel_alone_arms[best_rel_alone_arm]
    best_rel_ci = _ci(A[best_rel_alone_arm])
    rel_generalizes = (best_rel_ci[0] > chance and best_rel_alone > p["untrained_input"])
    S1 = (best_rel_alone >= wt_dense + LIFT) and rel_generalizes

    fused_weighted = {"both_wordnet_dense_weighted": p["both_wordnet_dense_weighted"],
                      "both_wordnet_sparse_weighted": p["both_wordnet_sparse_weighted"],
                      "both_wordnet_kwta_weighted": p["both_wordnet_kwta_weighted"]}
    best_fused_arm = max(fused_weighted, key=fused_weighted.get)
    best_fused = fused_weighted[best_fused_arm]
    if "dense" in best_fused_arm:
        naive_sibling = "both_wordnet_dense_naiveconcat"
    elif "kwta" in best_fused_arm:
        naive_sibling = "both_wordnet_dense_naiveconcat"   # kWTA has no naive-concat sibling; compare to dense-naive dilution
    else:
        naive_sibling = "both_wordnet_sparse_naiveconcat"
    S2 = (best_fused > ctx + FUSE_EPS) and (best_fused > p[naive_sibling])

    shuffle_collapsed = (p["shuffle_wordnet_kwta"] <= chance + SHUFFLE_EPS)
    controls_reproduce = (CTX_LO <= ctx <= CTX_HI) and (WT_LO <= wt_dense <= WT_HI)
    arms_differ = len(set(round(v, 4) for v in p.values())) > 3

    # sparse-lever validity: does kWTA (faithful) PRESERVE the WorldTree dense signal that GSBC (lossy) destroys?
    wt_kwta_preserves = round(p["relations_worldtree_sparse_kwta_naive"] - wt_dense, 4)
    wt_gsbc_lossy = round(p["relations_worldtree_sparse_gsbc_naive"] - wt_dense, 4)
    kwta_vs_dense_wn = round(p["relations_wordnet_sparse_kwta_naive"] - p["relations_wordnet_dense_naive"], 4)
    gsbc_vs_denselifted_wn = round(p["relations_wordnet_sparse_gsbc_naive"] - p["relations_wordnet_dense_lifted"], 4)
    fusion_gain_dense = round(p["both_wordnet_dense_weighted"] - both_naive_d, 4)
    fused_minus_context = round(best_fused - ctx, 4)

    verdict, vmsg = _decide(p, chance, ctx, wt_dense, best_rel_alone, best_rel_alone_arm, best_rel_ci,
                            best_fused, best_fused_arm, S1, S2, shuffle_collapsed, controls_reproduce,
                            n_test, rel_generalizes)

    def _clean(a):
        return {k: v for k, v in a.items() if not k.startswith("_")}

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": f"{verdict}: {vmsg}",
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "device": DEVICE, "seeds": list(seeds),
        "primary_metric": "held-out (5-fold CV, no-leak) retrieval p@10 vs Binder-65 gold neighborhoods",
        "one_variable": "the MECHANISM: relation coding {DENSE, SPARSE-GSBC} x fusion/readout {naive-concat-single-lambda, weighted-block-diag} (+ typed-bind encoding lever); relation SOURCE=WordNet richer set; density is INSTRUMENTED not the hypothesis",
        "arms_p_at_10": p,
        "arms_full": {k: _clean(A[k]) for k in A},
        "best_relation_alone_arm": best_rel_alone_arm, "best_relation_alone_p10": best_rel_alone,
        "best_relation_alone_p10_ci": list(best_rel_ci),
        "best_fused_weighted_arm": best_fused_arm, "best_fused_weighted_p10": best_fused,
        "rescue_signals": {"S1_relations_alone_rescued": bool(S1), "S2_fusion_rescued": bool(S2),
                           "relations_generalize": bool(rel_generalizes)},
        "lever_deltas": {
            "kwta_minus_dense_relations_alone_wordnet": kwta_vs_dense_wn,
            "gsbc_minus_denselifted_wordnet_pure_regime": gsbc_vs_denselifted_wn,
            "worldtree_kwta_minus_dense_SPARSE_VALIDITY": wt_kwta_preserves,
            "worldtree_gsbc_minus_dense_LOSSY_CHECK": wt_gsbc_lossy,
            "weighted_minus_naive_fusion_dense": fusion_gain_dense,
            "best_fused_minus_context": fused_minus_context,
            "typedbind_minus_dense_relations": round(p["relations_wordnet_typedbind_naive"] - p["relations_wordnet_dense_naive"], 4),
            "note": "worldtree_kwta_minus_dense ~0 => faithful sparse code PRESERVES signal (valid sparse test); worldtree_gsbc_minus_dense <<0 => GSBC random-lift is LOSSY (its null result is confounded, not a fair sparse test)"},
        "crosstalk": {"dense_lifted": dense_ct, "sparse_gsbc": sparse_ct, "sparse_kwta": kwta_ct,
                      "note": "pairwise_overlap = within-bundle constituent interference (LOWER=less crosstalk, fairest regime cmp). own/cross = bundle recoverability (cross biased UP by non-negativity). Crosstalk-limited iff sparse pairwise_overlap << dense AND the FAITHFUL (kWTA) sparse arm >> dense arm; NOT crosstalk if sparse composes cleaner but the faithful arm stays flat"},
        "density": {"mean_worldtree_rels_per_concept": round(float(np.mean(wt_counts)), 2),
                    "mean_wordnet_rels_per_concept": round(float(np.mean(wn_counts)), 2),
                    "density_ratio_wn_over_wt": round(float(np.mean(wn_counts)) / max(float(np.mean(wt_counts)), 1e-9), 1),
                    "note": "VET seq29564: density is NOT the lever (corr n_rel vs p10 ~= -0.007); reported as instrumentation only"},
        "coverage": {"binder_concepts": Nb, "matched_binder_x_worldtree_x_wordnet_noun": len(matched),
                     "n_test_after_vocab_filter": n_test, "binder_with_wordnet_noun_rels_broad": n_binder_wn_broad,
                     "nan_imputed_cells_binder_internal": nan_count},
        "positive_controls_gate_D": {"context_only": ctx, "context_band": [CTX_LO, CTX_HI],
                                     "relations_worldtree_dense_naive": wt_dense, "worldtree_band": [WT_LO, WT_HI],
                                     "both_dense_naiveconcat": both_naive_d, "reproduce_ok": bool(controls_reproduce),
                                     "reference_predecessor": {"context": 0.2426, "relations_worldtree": 0.139, "both": 0.2043,
                                                               "source": "MEASURED@data/exp_native_meaning_encoder_binder_grounded_v1_smoke/metrics.json"}},
        "shuffle_collapsed": bool(shuffle_collapsed), "shuffle_wordnet_kwta_p10": p["shuffle_wordnet_kwta"],
        "arms_differ_verified": bool(arms_differ),
        "arm_pk_hashes": {k: _arm_hash(A[k]["_pk"]) for k in A if A[k]["_pk"] is not None},
        "no_leak": "held concepts' Binder vectors NEVER in ridge/fusion training (5-fold CV; inner-CV lambda select is TRAIN-only); shuffle-collapse verifies",
        "bands": {"LIFT": LIFT, "FLAT_EPS": FLAT_EPS, "FUSE_EPS": FUSE_EPS, "SHUFFLE_EPS": SHUFFLE_EPS,
                  "MIN_HELDOUT": MIN_HELDOUT, "chance_p10": chance, "N_FOLDS": N_FOLDS},
        "config": {"N_DIM": N_DIM, "SPARSE_DIM": SPARSE_DIM, "gsbc": {"kb": GSBC_KB, "blk_l": GSBC_BLK, "m": GSBC_M, "tau": GSBC_TAU},
                   "RIDGE_LAMBDA": RIDGE_LAMBDA, "RIDGE_LAMBDA_HD": round(RIDGE_LAMBDA_HD, 2),
                   "fusion_rel_mult_grid": list(FUSION_REL_MULT_GRID), "inner_folds": INNER_FOLDS,
                   "cap_similar": CAP_SIMILAR, "cap_total": CAP_TOTAL,
                   "encoder_profile": prof, "vocab": len(word2id), "n_worldtree_triples": len(triples),
                   "wordnet_sense_policy": "first_most_frequent_noun_synset"},
        "brain_fidelity": "WordNet structural relations = SUPPLIED clean vetted structure (not a borrowed distributional encoder); sparse GSBC codes = cortical low-crosstalk composition; weighted fusion = learned readout; native encoder trained only by error-driven context(ARC)+relation(WT) prediction",
        "calibration_check": "adaptive_with_discriminator_gate: fusion relation-block lambda multiplier selected by inner-CV MSE on TRAIN folds only (no leak); RIDGE_LAMBDA_HD dim-scaled (4096/300) not tuned-for-PASS; shuffle-collapse still gates",
        "crlb_n/a": "retrieval p@10 vs Binder gold neighborhoods has no closed-form estimator noise floor; empirical chance floor measured (~0.026) + shuffle-collapse is the discriminator gate",
        "cardinality_ok": True, "sweep_axis": "none_fixed_arm_matrix",
        "final_metrics_atomicity": "tmp_replace", "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True, "progress_logging": "print_flush_true",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_sorted_no_builtin_hash_seeded_rng",
        "storage": "no_composition_selfcontained",
        "contract": "INLINE-LOCAL CPU foreground; no push/remote-persist by exp_dev; no atom banking; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[matrix] context={ctx} | wt_dense={wt_dense} both_naive_d={both_naive_d} | "
          f"REL-ALONE wn_dense={p['relations_wordnet_dense_naive']} wn_gsbc={p['relations_wordnet_sparse_gsbc_naive']} "
          f"wn_kwta={p['relations_wordnet_sparse_kwta_naive']} wn_bind={p['relations_wordnet_typedbind_naive']} | "
          f"VALIDITY wt_kwta={p['relations_worldtree_sparse_kwta_naive']} wt_gsbc={p['relations_worldtree_sparse_gsbc_naive']} | "
          f"FUSED d_naive={both_naive_d} d_weighted={p['both_wordnet_dense_weighted']} "
          f"kwta_weighted={p['both_wordnet_kwta_weighted']} sp_weighted={p['both_wordnet_sparse_weighted']} | "
          f"shuffle={p['shuffle_wordnet_kwta']} chance={chance}", flush=True)
    print(f"[levers] kwta-dense(alone)={kwta_vs_dense_wn} gsbc-denselifted={gsbc_vs_denselifted_wn} "
          f"VALID wt_kwta-dense={wt_kwta_preserves} wt_gsbc-dense={wt_gsbc_lossy} weighted-naive(fuse)={fusion_gain_dense} "
          f"fused-context={fused_minus_context} | crosstalk pairwise dense={dense_ct['pairwise_overlap']} "
          f"gsbc={sparse_ct['pairwise_overlap']} kwta={kwta_ct['pairwise_overlap']}", flush=True)
    print(f"[gates] n_test={n_test} S1={S1} S2={S2} controls_reproduce={controls_reproduce} "
          f"shuffle_collapsed={shuffle_collapsed} arms_differ={arms_differ} "
          f"mean_wn_rels={round(float(np.mean(wn_counts)),1)} mean_wt_rels={round(float(np.mean(wt_counts)),1)}", flush=True)
    return metrics


def _decide(p, chance, ctx, wt_dense, best_rel_alone, best_rel_arm, best_rel_ci, best_fused, best_fused_arm,
            S1, S2, shuffle_collapsed, controls_reproduce, n_test, rel_gen):
    tail = (f"[best_rel_alone={best_rel_arm} p@10={best_rel_alone} ci{list(best_rel_ci)} | "
            f"best_fused={best_fused_arm} p@10={best_fused} | context={ctx} | wt_dense={wt_dense} | "
            f"shuffle={p['shuffle_wordnet_kwta']} chance={chance}]")
    if n_test < MIN_HELDOUT:
        return "INVALID", f"only {n_test} matched test concepts (< {MIN_HELDOUT}); coverage too thin {tail}"
    if not shuffle_collapsed:
        return "INVALID", f"SHUFFLE did NOT collapse (shuffle p@10={p['shuffle_wordnet_kwta']} vs chance {chance}) -- leak; metric void {tail}"
    if not controls_reproduce:
        return "INVALID", (f"GATE-D positive controls did NOT reproduce (context={ctx} band[{CTX_LO},{CTX_HI}]; "
                           f"relations_worldtree={wt_dense} band[{WT_LO},{WT_HI}]) -- invocation/regime mismatch; downstream arms suspect {tail}")
    if S1 or S2:
        lever = []
        if S1:
            lever.append(f"RELATIONS-ALONE rescued ({best_rel_arm} p@10={best_rel_alone} >= 0.139+{LIFT}, generalizes)")
        if S2:
            lever.append(f"WEIGHTED-FUSION rescued ({best_fused_arm} p@10={best_fused} > context {ctx}+{FUSE_EPS} AND > its naive sibling)")
        return ("MECHANISM-RESCUED",
                f"relational grounding was MECHANISM-limited, now rescued: {'; '.join(lever)}. shuffle collapses, no-leak. "
                f"WordNet supplied the structure; the SUBSTRATE mechanism (sparse coding / weighted fusion) carried it {tail}")
    # nothing rescued
    if (best_rel_alone <= wt_dense + FLAT_EPS) and (best_fused <= ctx + FUSE_EPS):
        return ("HONEST-WALL-structure-insufficient",
                f"NONE of {{sparse-kWTA, sparse-GSBC, weighted-fusion, typed-bind}} lifts relations past ~0.139 (best_rel_alone "
                f"{best_rel_alone} ~= wt_dense {wt_dense}) AND best weighted-fusion ({best_fused}) does not beat context {ctx} "
                f"by >= FUSE_EPS ({FUSE_EPS}) -- weighted fusion may FIX the naive-concat dilution but relations add ~0 NET; "
                f"relational grounding is mechanism+data limited even after the nearest fixes; grounding needs MORE than "
                f"taxonomy (sensorimotor/Barsalou) {tail}")
    return ("MIDDLE-partial-lift",
            f"some lift (best_rel_alone {best_rel_alone} > 0.139+{LIFT}) but below context {ctx} and weighted-fusion does "
            f"not beat context -- mechanism helps partially; not a full rescue {tail}")


# ---------------------------------------------------------------------------
# self-test: real code path + planted separability + shuffle-collapse + sparse-lowers-crosstalk
# ---------------------------------------------------------------------------
def self_test():
    from nltk.corpus import wordnet as wn
    print("[self-test] load REAL Binder csv ...", flush=True)
    concepts, X, feats, nan_c = load_binder(BINDER_CSV)
    assert len(concepts) >= 500 and X.shape[1] == 65 and not np.isnan(X).any(), "binder load bad"
    print(f"[self-test]   binder n={len(concepts)} nan_imputed={nan_c}", flush=True)

    print("[self-test] REAL WordNet extract (first noun synset) ...", flush=True)
    rs = wordnet_rels("dog", wn)
    assert rs is not None and len(rs) >= 5, f"wordnet dog rels too few ({rs})"
    kinds = set(r for (r, _) in rs)
    assert "KINDOF" in kinds, f"no KINDOF hypernym for dog ({kinds})"
    print(f"[self-test]   dog: {len(rs)} rels, types={sorted(kinds)}", flush=True)

    print("[self-test] PLANTED separability (custom ridge builder): informative input generalizes, shuffle collapses ...", flush=True)
    rng = np.random.default_rng(0)
    Xg = X[:120].astype(np.float32)
    inp = (Xg @ rng.standard_normal((65, 40)).astype(np.float32)) + 0.15 * rng.standard_normal((120, 40)).astype(np.float32)
    keep = np.arange(120)
    R_L = _ridge_builder(RIDGE_LAMBDA)
    r_real = earn(inp, X, keep, (SEED,), R_L)
    r_shuf = earn(inp, X, keep, (SEED,), R_L, shuffle=True)
    r_ch = chance_retrieval(X, keep, SEED)
    print(f"[self-test]   planted real p@10={r_real['p_at_10']} shuffle={r_shuf['p_at_10']} chance={r_ch['p_at_10']}", flush=True)
    assert r_real["p_at_10"] > r_ch["p_at_10"] + 0.05, "planted informative input did not generalize"
    assert r_shuf["p_at_10"] <= r_ch["p_at_10"] + SHUFFLE_EPS + 0.05, "planted shuffle did NOT collapse (leak)"
    assert _arm_hash(r_real["_pk"]) != _arm_hash(r_shuf["_pk"]), "real vs shuffle bit-identical"

    print("[self-test] weighted-fusion builder runs (block-diag + inner-CV) ...", flush=True)
    fus = _weighted_fusion_builder(20, RIDGE_LAMBDA, FUSION_REL_MULT_GRID)
    r_fus = earn(np.concatenate([inp[:, :20], inp[:, 20:]], axis=1), X, keep, (SEED,), fus)
    assert 0.0 <= r_fus["p_at_10"] <= 1.0, "fusion arm bad p@10"

    print("[self-test] REAL code path: WT parse + tiny ARC encoder + WordNet + GSBC sparse + crosstalk ...", flush=True)
    triples, prec = parse_tables((("KINDOF", 1, 4), ("HABITAT", 3, 5), ("MADEOF", 2, 6), ("PARTOF", 1, 5)))
    wt_by = defaultdict(list)
    for (c, r, v) in triples:
        wt_by[c].append((r, v))
    wn_by = {}
    for c in concepts:
        rr = wordnet_rels(c, wn)
        if rr:
            wn_by[c] = rr
    matched = [c for c in concepts if len(wt_by.get(c, [])) >= 1 and c in wn_by]
    assert len(matched) >= 20, f"too few matched concepts ({len(matched)})"
    forced = set()
    for (c, r, v) in triples:
        forced.update(_tok_words(c)); forced.update(_tok_words(v))
    for c in matched:
        forced.update(_tok_words(c))
        for (r, v) in wn_by[c]:
            forced.update(_tok_words(v.replace("_", " ")))
    od = _out_dir("_selftest")
    corpus, w2id, idc = build_corpus(4000, forced, od)
    ctx = ContextSampler(corpus, WINDOW, SEED + 1)
    neg = NegSampler(idc, UNIGRAM_POW, SEED + 2)
    rd = RelationData(triples, w2id, SEED + 3)
    enc = NativeEncoder(len(w2id), N_DIM, NREL, SEED)
    enc = train_encoder(enc, ctx, neg, rd, 40, 128, od, use_relation=True)
    E = enc.E.detach().cpu().numpy().astype(np.float32)
    R = enc.R.detach().cpu().numpy().astype(np.float32)
    W_lift = _lift_matrix()
    cidx = {c: i for i, c in enumerate(concepts)}
    keep2, rsp_list, rkw_list, rdl_list, sp_c, kw_c, dl_c = [], [], [], [], [], [], []
    for c in matched:
        rwn = rel_dense_mean(E, R, wn_by[c], w2id)
        rsp, spc = rel_sparse_bundle(E, R, wn_by[c], w2id, W_lift, return_constituents=True)
        rkw, kwc = rel_sparse_kwta(E, R, wn_by[c], w2id, return_constituents=True)
        rdl, dlc = rel_dense_lifted(E, R, wn_by[c], w2id, W_lift, return_constituents=True)
        if rwn is None or rsp is None or rkw is None or rdl is None:
            continue
        keep2.append(cidx[c]); rsp_list.append(rsp); rkw_list.append(rkw); rdl_list.append(rdl)
        sp_c.append(spc); kw_c.append(kwc); dl_c.append(dlc)
    keep2 = np.asarray(keep2)
    assert len(keep2) >= 20, f"too few usable ({len(keep2)})"
    res_sp = earn(np.asarray(rsp_list, np.float32), X, keep2, (SEED,), _ridge_builder(RIDGE_LAMBDA_HD))
    res_kw = earn(np.asarray(rkw_list, np.float32), X, keep2, (SEED,), _ridge_builder(RIDGE_LAMBDA))
    assert 0.0 <= res_sp["p_at_10"] <= 1.0 and 0.0 <= res_kw["p_at_10"] <= 1.0, "sparse arm bad p@10"
    dct = crosstalk_stats(list(np.asarray(rdl_list, np.float32)), dl_c)
    sct = crosstalk_stats(list(np.asarray(rsp_list, np.float32)), sp_c)
    kct = crosstalk_stats(list(np.asarray(rkw_list, np.float32)), kw_c)
    print(f"[self-test]   n_test={len(keep2)} gsbc p@10={res_sp['p_at_10']} kwta p@10={res_kw['p_at_10']} | "
          f"pairwise dense={dct['pairwise_overlap']} gsbc={sct['pairwise_overlap']} kwta={kct['pairwise_overlap']}", flush=True)
    assert all(np.isfinite([dct["pairwise_overlap"], sct["pairwise_overlap"], kct["pairwise_overlap"]])), "crosstalk stats not finite"
    # faithful signed-sparse kWTA composes with LOWER within-bundle crosstalk than dense-mean (near-orthogonal
    # constituents); own/cross cosine is confounded by GSBC non-negativity so pairwise_overlap is the fair test
    assert kct["pairwise_overlap"] <= dct["pairwise_overlap"] + 0.05, \
        f"kWTA pairwise_overlap ({kct['pairwise_overlap']}) not <= dense ({dct['pairwise_overlap']}) -- sparse should compose with less crosstalk"
    # determinism
    c2, X2, _, _ = load_binder(BINDER_CSV)
    assert c2 == concepts and np.allclose(X2, X, equal_nan=True), "binder load non-deterministic"
    print("[self-test] PASS (binder+wordnet load; planted generalizes+shuffle collapses; fusion builder; real "
          "WT+ARC+WordNet+GSBC sparse+ridge/fusion CV; sparse-lowers-crosstalk; determinism)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    _T0[0] = time.perf_counter()

    if args.self_test:
        output_dir = _out_dir("_selftest")
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    output_dir = _out_dir("_smoke") if mode == "smoke" else _out_dir()
    _write_start_marker(output_dir, mode)
    run(mode, output_dir)
    sys.exit(0)


if __name__ == "__main__":
    _od = (_out_dir("_selftest") if "--self-test" in sys.argv else
           (_out_dir("_smoke") if "--smoke" in sys.argv else _out_dir()))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
