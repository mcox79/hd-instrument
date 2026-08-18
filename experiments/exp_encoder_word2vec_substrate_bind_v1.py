"""encoder_word2vec_substrate_bind_v1 -- Path A ideal-encoder PRETRAINED-SEMANTIC test.

Tests whether ANY pretrained semantic encoder (word2vec / GloVe / fastText) breaks the
Shannon-floor (encoder_dual_gain_softhebb_v1 HARD_FAIL 2026-06-23: all 4 forward-only
substrate-native arms produced recall=0.020-0.023 at sigma=1.5 + BPC=7.866-7.874).

USER directive 2026-06-23: "we need to find the right -- ideal -- encoding as soon as
possible. what is required here? I'm open to being wrong here."
USER directive 2026-06-22: NO MiniLM, NO BGE. word2vec / GloVe / fastText are open-weights
+ scientifically-published training; permitted.

Information-decisive design:
  if ANY pretrained-semantic arm clears BOTH Metric A AND Metric B
     -> encoder choice IS the lever; question becomes "which pretrained encoder is best"
  if NO pretrained-semantic arm clears EITHER A or B
     -> substrate W-matrix itself is the bottleneck regardless of encoder
     -> Shannon-floor is encoder-INVARIANT
     -> pivot to refuse-aware product strategy + sigma<=1.0 envelope

DESIGN (4 arms x cleanup-sigma-sweep + Path-A BPC x 3 seeds at N_DIM=4096):
  ARM_CHAR_TRIGRAM_BASELINE -- existing substrate; reproduces Shannon-floor + BPC fail.
  ARM_WORD2VEC_300D         -- Google word2vec 300d pretrained on Google News.
  ARM_GLOVE_300D            -- Stanford GloVe 300d pretrained on Common Crawl/wiki.
  ARM_FASTTEXT_300D         -- Facebook fastText 300d pretrained (OOV char-ngram backoff).

All 3 pretrained 300d -> 4096d via same random Gaussian projection (one matrix per seed).

PRE-REG bands (preregs/2026-06-23_encoder_word2vec_substrate_bind_v1.md):
  METRIC A (cleanup recall@1 @ sigma=1.5 per arm vs trigram-baseline 0.020):
    HARD_PASS:   recall >= 0.20 AND cv <= 0.30
    HARD_FAIL:   recall <= 0.05
    MIDDLE_BAND: 0.05 < recall < 0.20
  METRIC B (substrate-LM BPC vs unigram 7.738 per arm):
    HARD_PASS:   best_calibrated_bpc < 7.738 AND cv <= 0.05
    HARD_FAIL:   best_calibrated_bpc >= 7.864
    MIDDLE_BAND: 7.738 < bpc < 7.864
  CELL VERDICT:
    HARD_PASS  = ANY arm clears BOTH A AND B (encoder IS the lever -> product unblock)
    HARD_FAIL  = NO arm clears EITHER A or B  (W-matrix is bottleneck -> Shannon-floor invariant)
    MIDDLE_BAND= one arm clears A only OR B only (partial)

SANITY:
  sigma=0 across all 4 arms must yield recall@1 = 1.000.
  Cross-corpus alignment (BONUS metric C): cosine(emb[w], emb[w]) = 1.0 across encoders for
  same string -- trivial; validates pretrained encoders solve cross-corpus problem by
  construction (same string -> same vector).

SUBSTRATE-ONLY: n_llm_calls = 0; numpy-only + gensim downloader (open-weight bundles).

Cites:
  - preregs/2026-06-23_encoder_word2vec_substrate_bind_v1.md
  - experiments/exp_encoder_dual_gain_softhebb_v1.py (parent HARD_FAIL 4-arm forward-only)
  - experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (BPC 7.864 ref)
  - Mikolov 2013 word2vec / Pennington 2014 GloVe / Bojanowski 2017 fastText
  - hdlab/char_trigram_encoder.py (substrate-native baseline)
  - Shannon-floor META cert row 675

Skunkworks structural blockers honored:
  #3 _LLM_CALL_COUNTER = [0] (substrate-only)
  #1 per_unit per seed via _seed_checkpoint
  #2 cv across seeds in compute_verdict
  #4 atexit synthesizer for timeout-resilience
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit, hashlib
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "encoder_word2vec_substrate_bind_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Reference baselines from prior cells
UNIGRAM_BPC_REF = 7.738
PATH_A_CURRENT_BPC_REF = 7.864
CLEANUP_BASELINE_RECALL_REF = 0.020

# Pre-reg HARD bands
HP_CLEANUP_RECALL = 0.20
HF_CLEANUP_RECALL = 0.05
HP_CLEANUP_CV_MAX = 0.30
HP_BPC = UNIGRAM_BPC_REF
HF_BPC = PATH_A_CURRENT_BPC_REF
HP_BPC_CV_MAX = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
PRETRAIN_DIM = 300
M = 200
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
DISCRIMINATOR_SIGMA = 1.5
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
VOCAB_CAP = 4000
INGEST_CHUNK = 8192

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_EVAL = 200
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    SEEDS = [0]
    N_EVAL = 50
    N_TRAIN = 10_000
    N_HELD = 2_000
    VOCAB_CAP = 1000

ARMS = ["ARM_CHAR_TRIGRAM_BASELINE", "ARM_WORD2VEC_300D", "ARM_GLOVE_300D", "ARM_FASTTEXT_300D"]
PRETRAINED_ARMS = {"ARM_WORD2VEC_300D", "ARM_GLOVE_300D", "ARM_FASTTEXT_300D"}
GENSIM_MODEL_FOR = {
    "ARM_WORD2VEC_300D":   "word2vec-google-news-300",
    "ARM_GLOVE_300D":      "glove-wiki-gigaword-300",
    "ARM_FASTTEXT_300D":   "fasttext-wiki-news-subwords-300",
}

CONFIG_VERSION = (
    "encoder_word2vec_substrate_bind_v1; N_DIM=%d PRETRAIN_DIM=%d M=%d N_EVAL=%d "
    "N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d sigmas=%s arms=%s seeds=%s mode=%s INGEST_CHUNK=%d "
    "lambda_grid=%s; bands HP_recall>=%.2f HF_recall<=%.2f HP_bpc<%.3f HF_bpc>=%.3f"
) % (
    N_DIM, PRETRAIN_DIM, M, N_EVAL, N_TRAIN, N_HELD, VOCAB_CAP, SIGMA_SWEEP, ARMS, SEEDS,
    RUN_MODE, INGEST_CHUNK, LAMBDA_GRID, HP_CLEANUP_RECALL, HF_CLEANUP_RECALL, HP_BPC, HF_BPC,
)


# ============================================================================
# Substrate primitives (char-trigram baseline; matches dual_gain encoder)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Bag-of-trigrams sign-bundled bipolar HD vector. Deterministic; substrate-native."""
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    """Random Gaussian projection matrix P [out_dim, in_dim] with 1/sqrt(in_dim) scale.

    Johnson-Lindenstrauss style; preserves pairwise distances in expectation.
    Same scale for all 3 pretrained arms; same seed -> same projection structure.
    """
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# ============================================================================
# Pretrained-model loader (gensim downloader)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    """Load a gensim KeyedVectors model; cache in-process for cross-seed reuse."""
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    import gensim.downloader as gd
    # gensim 4.x respects GENSIM_DATA_DIR env (we set it above) AND has base_dir attr
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(model_name)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def _embed_vocab_via_gensim(vocab: List[str], kv) -> np.ndarray:
    """Look up each vocab word in gensim KeyedVectors; fallback strategies:

      1. exact word
      2. lowercase
      3. zero-vector (OOV explicit; will L2-normalize to zero -> handled downstream)

    Returns [V, PRETRAIN_DIM] float32 (un-normalized).
    """
    dim = kv.vector_size
    V = len(vocab)
    out = np.zeros((V, dim), dtype=np.float32)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        # Direct lookup
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        else:
            # fastText handles OOV; word2vec/glove return KeyError. Try fastText's
            # get_vector path explicitly only if supported.
            try:
                v = kv.get_vector(w, norm=False)
            except Exception:
                v = None
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            out[i] = v.astype(np.float32)
    return out, n_hit, n_miss


# ============================================================================
# Encoder ARMS -- each returns (codebook_M, E_full_for_path_A)
# ============================================================================

def encode_arm_char_trigram_baseline(vocab: List[str], M_atoms: int, n_dim: int, seed: int):
    """ARM 1: substrate-native baseline; trigram bundling. No training."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E = _l2_normalize(E)
    codebook = E[:M_atoms].copy()
    return codebook, E


def encode_arm_pretrained_projected(vocab: List[str], M_atoms: int, n_dim: int, seed: int,
                                     model_name: str):
    """ARMS 2-4: pretrained-semantic encoder; 300d -> n_dim via random Gaussian projection.

    Same projection matrix structure per seed across all 3 pretrained arms (one Gaussian
    matrix per seed; isolates encoder semantic content vs projection noise).

    For OOV words: char_trigram encoding scaled to match L2 norm structure (fallback so
    cleanup recall@1 at sigma=0 stays 1.000 by construction).
    """
    kv = _load_gensim_kv(model_name)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    # Project 300d -> n_dim (L2-normalize input first to control geometry)
    E_pre_n = _l2_normalize(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)  # [V, n_dim]
    # OOV mask: rows where original was all-zero get char-trigram fallback so sigma=0 ident still works
    norms_before_proj = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before_proj < 1e-9
    if oov_mask.any():
        n_oov = int(oov_mask.sum())
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize(E_proj)
    codebook = E_proj[:M_atoms].copy()
    # Stash hit/miss in a side-channel by attaching to array (ignored by downstream;
    # logged via global at caller)
    return codebook, E_proj, {"n_hit": int(n_hit), "n_miss": int(n_miss),
                              "n_vocab": int(len(vocab)),
                              "pretrain_dim": int(kv.vector_size)}


# ============================================================================
# Metric A: cleanup recall over sigma sweep
# ============================================================================

def _argmax_cleanup_batch(cues, codebook):
    cb_n = _l2_normalize(codebook)
    cu_n = _l2_normalize(cues)
    scores = cu_n @ cb_n.T
    return np.argmax(scores, axis=1).astype(np.int64)


def cleanup_eval_arm(codebook: np.ndarray, n_eval: int, sigmas: list, seed: int) -> dict:
    g = np.random.default_rng(seed * 7919 + 11)
    M_loc = codebook.shape[0]
    D_loc = codebook.shape[1]
    query_idx = g.choice(M_loc, size=min(n_eval, M_loc), replace=False)
    out = {}
    for sig in sigmas:
        noise = sig * g.standard_normal((len(query_idx), D_loc)).astype(np.float32)
        cues = codebook[query_idx] + noise
        pred = _argmax_cleanup_batch(cues, codebook)
        out[float(sig)] = float((pred == query_idx).sum()) / max(len(query_idx), 1)
    return out


# ============================================================================
# Metric B: substrate-LM BPC on text8 (per arm)
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing at %s" % TEXT8, flush=True)
        sys.exit(1)
    out: List[str] = []
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n_total:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()
            out.extend(parts)
        if buf and len(out) < n_total:
            out.append(buf)
    return out[:n_total]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_hebbian_W_np(idx_train: np.ndarray, E: np.ndarray, ingest_chunk: int) -> np.ndarray:
    """Hebbian outer-product LM W [N_DIM, N_DIM] = sum over training pairs of E[t+1] outer E[t]."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = idx_train.shape[0] - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src = idx_train[b:end]
        tgt = idx_train[b + 1:end + 1]
        E_src = E[src]
        E_tgt = E[tgt]
        W += E_tgt.T @ E_src
    return W


def softmax_safe(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = logits / max(temperature, 1e-6)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def path_a_bpc_arm(E: np.ndarray, vocab: List[str], idx_train: np.ndarray,
                    idx_held: np.ndarray, lambda_grid: list, seed: int) -> dict:
    """Train Hebbian W on idx_train; eval BPC on idx_held; log-linear interp w/ unigram."""
    V = len(vocab)
    W = build_hebbian_W_np(idx_train, E, INGEST_CHUNK)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    ctx = ctx[mask]
    nxt = nxt[mask]
    n_eval = len(ctx)
    if n_eval == 0:
        return {"bpc_raw": float("inf"), "bpc_best_calibrated": float("inf"),
                "best_lambda": 1.0, "n_eval": 0}
    sub_logits = np.zeros((n_eval, V), dtype=np.float32)
    chunk = 1024
    for b in range(0, n_eval, chunk):
        end = min(b + chunk, n_eval)
        pred_vec = E[ctx[b:end]] @ W.T
        pn = np.linalg.norm(pred_vec, axis=1, keepdims=True)
        pn[pn < 1e-9] = 1e-9
        pred_vec = pred_vec / pn
        sub_logits[b:end] = pred_vec @ E.T
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    sub_logp = np.log(np.clip(softmax_safe(sub_logits, temperature=1.0), 1e-30, 1.0))
    n_dev = n_eval // 2
    ctx_test = ctx[n_dev:]
    nxt_test = nxt[n_dev:]
    nxt_dev = nxt[:n_dev]
    sub_logp_dev = sub_logp[:n_dev]
    sub_logp_test = sub_logp[n_dev:]
    raw_logp_nxt_test = sub_logp_test[np.arange(len(nxt_test)), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt_test)) / np.log(2.0)
    best_lambda = 1.0
    best_dev_bpc = float("inf")
    for lam in lambda_grid:
        combined = lam * sub_logp_dev + (1.0 - lam) * U_log[None, :]
        combined = combined - combined.max(axis=1, keepdims=True)
        Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
        logp = combined - Z[:, None]
        logp_nxt = logp[np.arange(n_dev), nxt_dev]
        dev_bpc = -float(np.mean(logp_nxt)) / np.log(2.0)
        if dev_bpc < best_dev_bpc:
            best_dev_bpc = dev_bpc
            best_lambda = lam
    combined_t = best_lambda * sub_logp_test + (1.0 - best_lambda) * U_log[None, :]
    combined_t = combined_t - combined_t.max(axis=1, keepdims=True)
    Z_t = np.log(np.clip(np.exp(combined_t).sum(axis=1), 1e-30, None))
    logp_t = combined_t - Z_t[:, None]
    logp_nxt_t = logp_t[np.arange(len(nxt_test)), nxt_test]
    bpc_best = -float(np.mean(logp_nxt_t)) / np.log(2.0)
    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best_calibrated": round(bpc_best, 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4),
        "n_eval": int(len(nxt_test)),
    }


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] loading corpus + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus too small: %d vs %d; truncating" % (len(toks), N_TRAIN + N_HELD), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d M=%d" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, M), flush=True)

    M_atoms = min(M, V)
    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] encoding..." % (seed, arm_label), flush=True)
        meta = {}
        if arm_label == "ARM_CHAR_TRIGRAM_BASELINE":
            codebook, E_full = encode_arm_char_trigram_baseline(vocab, M_atoms, N_DIM, seed)
        else:
            model_name = GENSIM_MODEL_FOR[arm_label]
            codebook, E_full, meta = encode_arm_pretrained_projected(
                vocab, M_atoms, N_DIM, seed, model_name)
        t_enc = time.time() - t_arm
        # Metric A: cleanup
        t_a = time.time()
        cleanup = cleanup_eval_arm(codebook, N_EVAL, SIGMA_SWEEP, seed)
        t_clean = time.time() - t_a
        # Metric B: BPC
        t_b = time.time()
        bpc = path_a_bpc_arm(E_full, vocab, idx_train, idx_held, LAMBDA_GRID, seed)
        t_bpc = time.time() - t_b
        by_arm[arm_label] = {
            "cleanup": {str(k): round(v, 4) for k, v in cleanup.items()},
            "recall_discriminator": round(cleanup.get(DISCRIMINATOR_SIGMA, 0.0), 4),
            "bpc_raw": bpc["bpc_raw"],
            "bpc_best_calibrated": bpc["bpc_best_calibrated"],
            "best_lambda": bpc["best_lambda"],
            "best_dev_bpc": bpc["best_dev_bpc"],
            "bpc_n_eval": bpc["n_eval"],
            "wall_encode_s": round(t_enc, 2),
            "wall_cleanup_s": round(t_clean, 2),
            "wall_bpc_s": round(t_bpc, 2),
            "encoder_meta": meta,
        }
        a = by_arm[arm_label]
        oov_info = ""
        if meta:
            oov_info = " hit/miss=%d/%d" % (meta.get("n_hit", 0), meta.get("n_miss", 0))
        print("    [seed=%d arm=%s] disc=%.3f basin_0=%.3f basin_1.5=%.3f bpc_raw=%.3f "
              "bpc_best=%.3f lam=%.2f%s (enc=%.1fs clean=%.1fs bpc=%.1fs)" % (
                  seed, arm_label, a["recall_discriminator"],
                  cleanup.get(0.0, 0.0), cleanup.get(1.5, 0.0),
                  a["bpc_raw"], a["bpc_best_calibrated"], a["best_lambda"],
                  oov_info, t_enc, t_clean, t_bpc), flush=True)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "M": M,
        "N_EVAL": N_EVAL,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def _classify_arm_cleanup(recall: float, cv: float) -> str:
    if recall >= HP_CLEANUP_RECALL and cv <= HP_CLEANUP_CV_MAX:
        return "HARD_PASS"
    if recall <= HF_CLEANUP_RECALL:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def _classify_arm_bpc(bpc: float, cv: float) -> str:
    if bpc < HP_BPC and cv <= HP_BPC_CV_MAX:
        return "HARD_PASS"
    if bpc >= HF_BPC:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())
    by_arm_agg = {}
    for arm_label in arm_labels:
        disc_vals = [u["by_arm"][arm_label]["recall_discriminator"] for u in units]
        bpc_vals = [u["by_arm"][arm_label]["bpc_best_calibrated"] for u in units]
        basin_keys = list(units[0]["by_arm"][arm_label]["cleanup"].keys())
        basin_agg = {}
        for sk in basin_keys:
            vals = [u["by_arm"][arm_label]["cleanup"].get(sk, 0.0) for u in units]
            basin_agg[sk] = round(float(np.mean(vals)), 4)
        d_mean = float(np.mean(disc_vals))
        d_std = float(np.std(disc_vals))
        d_cv = d_std / max(abs(d_mean), 1e-6)
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        cleanup_class = _classify_arm_cleanup(d_mean, d_cv)
        bpc_class = _classify_arm_bpc(b_mean, b_cv)
        dual_gain = (cleanup_class == "HARD_PASS" and bpc_class == "HARD_PASS")
        by_arm_agg[arm_label] = {
            "recall_discriminator_mean": round(d_mean, 4),
            "recall_discriminator_std": round(d_std, 4),
            "recall_discriminator_cv": round(d_cv, 4),
            "bpc_best_calibrated_mean": round(b_mean, 4),
            "bpc_best_calibrated_std": round(b_std, 4),
            "bpc_best_calibrated_cv": round(b_cv, 4),
            "basin_robustness_mean": basin_agg,
            "cleanup_classification": cleanup_class,
            "bpc_classification": bpc_class,
            "dual_gain_HARD_PASS": dual_gain,
        }

    # Sanity sigma=0 check
    sanity_failures = []
    for arm_label in arm_labels:
        basin_0 = by_arm_agg[arm_label]["basin_robustness_mean"].get("0.0", -1.0)
        if basin_0 < 0.999:
            sanity_failures.append("%s basin_0=%.4f" % (arm_label, basin_0))
    sanity_ok = len(sanity_failures) == 0

    any_dual = [al for al in arm_labels if by_arm_agg[al]["dual_gain_HARD_PASS"]]
    cleanup_pass = [al for al in arm_labels if by_arm_agg[al]["cleanup_classification"] == "HARD_PASS"]
    bpc_pass = [al for al in arm_labels if by_arm_agg[al]["bpc_classification"] == "HARD_PASS"]
    cleanup_all_fail = all(by_arm_agg[al]["cleanup_classification"] == "HARD_FAIL" for al in arm_labels)
    bpc_all_fail = all(by_arm_agg[al]["bpc_classification"] == "HARD_FAIL" for al in arm_labels)

    detail = {
        "by_arm_agg": by_arm_agg,
        "any_dual_gain_pass": list(any_dual),
        "cleanup_pass_arms": list(cleanup_pass),
        "bpc_pass_arms": list(bpc_pass),
        "cleanup_all_fail": bool(cleanup_all_fail),
        "bpc_all_fail": bool(bpc_all_fail),
        "sanity_sigma0_ok": sanity_ok,
        "sanity_sigma0_failures": sanity_failures,
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "path_a_current_bpc_ref": PATH_A_CURRENT_BPC_REF,
        "cleanup_baseline_recall_ref": CLEANUP_BASELINE_RECALL_REF,
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "HD-substrate ideal-encoder PRETRAINED-SEMANTIC dual-gain test; 4 arms (1 substrate "
            "baseline + 3 open-weight pretrained) x cleanup-sigma-sweep + Path-A BPC at "
            "N_DIM=%d M=%d N_TRAIN=%d N_HELD=%d V=%d PRETRAIN_DIM=%d; %d seeds; HARD_PASS = "
            "ANY arm clears BOTH cleanup>=0.20@sigma=1.5 AND BPC<%.3f; HARD_FAIL = NO arm "
            "clears EITHER metric -> substrate W-matrix is bottleneck (encoder-invariant)." % (
                N_DIM, M, N_TRAIN, N_HELD, VOCAB_CAP, PRETRAIN_DIM, len(units), HP_BPC)),
        "cites": [
            "preregs/2026-06-23_encoder_word2vec_substrate_bind_v1.md",
            "experiments/exp_encoder_dual_gain_softhebb_v1.py (parent 4-arm HARD_FAIL)",
            "experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (BPC 7.864 ref)",
            "Mikolov_2013_word2vec",
            "Pennington_2014_GloVe",
            "Bojanowski_2017_fastText",
            "hdlab/char_trigram_encoder.py",
            "Shannon_floor_META_cert_row_675",
            "USER_2026-06-23_ideal_encoder_directive",
            "USER_2026-06-22_no_minilm_no_bge",
        ],
    }

    parts = []
    for al in arm_labels:
        a = by_arm_agg[al]
        parts.append("%s=disc%.3f(%s)/bpc%.3f(%s)%s" % (
            al, a["recall_discriminator_mean"], a["cleanup_classification"],
            a["bpc_best_calibrated_mean"], a["bpc_classification"],
            "/DUAL" if a["dual_gain_HARD_PASS"] else ""))
    summary = "PRETRAINED_BIND @ sigma=%.2f: %s | sanity_ok=%s" % (
        DISCRIMINATOR_SIGMA, " | ".join(parts), sanity_ok)

    if not sanity_ok:
        return ("CONFOUND_FAIL",
                ("CONFOUND_FAIL: sigma=0 recall < 1.000 for %d arm(s) (%s); implementation bug "
                 "suspected, NOT mechanism rejection. " % (len(sanity_failures), "; ".join(sanity_failures)))
                + summary,
                detail)

    if any_dual:
        any_dual.sort(key=lambda x: (-by_arm_agg[x]["recall_discriminator_mean"],
                                      by_arm_agg[x]["bpc_best_calibrated_mean"]))
        top = any_dual[0]
        t = by_arm_agg[top]
        return ("HARD_PASS",
                ("PRETRAINED_BIND HARD_PASS: arm %s clears BOTH cleanup (recall=%.3f cv=%.2f >= %.2f) AND "
                 "BPC (best=%.3f cv=%.2f < %.3f); encoder choice IS the lever for cleanup AND BPC; "
                 "Shannon-floor FALSIFIED with open-weight pretrained semantic encoder; "
                 "substrate-product unblock: pretrained encoder route open; chain-grade-tier candidate. "
                 "dual_arms=%d total. " % (
                     top, t["recall_discriminator_mean"], t["recall_discriminator_cv"], HP_CLEANUP_RECALL,
                     t["bpc_best_calibrated_mean"], t["bpc_best_calibrated_cv"], HP_BPC,
                     len(any_dual))) + summary,
                detail)

    if cleanup_all_fail and bpc_all_fail:
        return ("HARD_FAIL",
                ("PRETRAINED_BIND HARD_FAIL: ALL %d arms (substrate-baseline + 3 pretrained-semantic) "
                 "HARD_FAIL on BOTH cleanup (max recall <= %.2f) AND BPC (min BPC >= %.3f); "
                 "Shannon-floor is ENCODER-INVARIANT; substrate W-matrix itself is the bottleneck "
                 "regardless of encoder semantic quality; pivot: refuse-aware product strategy + "
                 "sigma<=1.0 envelope ONLY. " % (
                     len(arm_labels), HF_CLEANUP_RECALL, HF_BPC)) + summary,
                detail)
    if len(cleanup_pass) == 0 and len(bpc_pass) == 0:
        return ("HARD_FAIL",
                ("PRETRAINED_BIND HARD_FAIL: NO arm clears EITHER metric A (cleanup HP) or metric B "
                 "(BPC HP); best cleanup in MIDDLE; best BPC in MIDDLE; pretrained encoders do not "
                 "lift substrate at production-regime to HP threshold. ") + summary,
                detail)

    msg_parts = []
    if cleanup_pass:
        msg_parts.append("cleanup HARD_PASS arms=%s" % cleanup_pass)
    if bpc_pass:
        msg_parts.append("bpc HARD_PASS arms=%s" % bpc_pass)
    return ("MIDDLE_BAND",
            ("PRETRAINED_BIND MIDDLE_BAND: at least one arm clears Metric A OR B but NO arm clears "
             "BOTH on same seed-mean; partial mechanism characterization; route to second-tier follow-up. "
             + " ; ".join(msg_parts) + ". ") + summary,
            detail)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "M": M,
            "N_EVAL": N_EVAL,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_encoder_word2vec_substrate_bind_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test (mechanism + sanity + verdict-shape)
# ============================================================================

def _selftest():
    # T1: char-trigram encoder produces L2-normalizable bipolar sign vectors
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,), "T1 char_trigram shape: %s" % (v.shape,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 char_trigram not bipolar: %s" % uniq

    # T2: char-trigram baseline arm produces M=8 codebook from 16-vocab; sigma=0 -> recall=1
    vocab_t = ["w%d" % i for i in range(16)]
    cb, E = encode_arm_char_trigram_baseline(vocab_t, 8, 64, seed=0)
    assert cb.shape == (8, 64), "T2 codebook shape: %s" % (cb.shape,)
    pred = _argmax_cleanup_batch(cb, cb)
    assert (pred == np.arange(8)).all(), "T2 sigma=0 ident failed: %s" % pred

    # T3: Gaussian projection produces correct shape + JL-style scale
    P = _gaussian_projection(in_dim=300, out_dim=64, seed=0)
    assert P.shape == (64, 300), "T3 P shape: %s" % (P.shape,)
    # Expected std ~ 1/sqrt(300) ~ 0.0577
    std_P = float(P.std())
    assert 0.04 < std_P < 0.08, "T3 P std out of expected JL range: %.4f" % std_P

    # T4: cleanup_eval_arm returns dict with sigma=0 -> 1.0
    out = cleanup_eval_arm(cb, n_eval=4, sigmas=[0.0, 1.0], seed=0)
    assert 0.0 in out and out[0.0] == 1.0, "T4 sigma=0 cleanup not 1.0: %s" % out

    # T5: build_hebbian_W_np produces correct shape
    idx_train_t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 0, 1] * 100, dtype=np.int64)
    W = build_hebbian_W_np(idx_train_t, E, INGEST_CHUNK)
    assert W.shape == (64, 64), "T5 W shape: %s" % (W.shape,)

    # T6: path_a_bpc_arm produces finite BPC
    bpc_out = path_a_bpc_arm(E, vocab_t, idx_train_t, idx_train_t[:50],
                              lambda_grid=[0.5, 1.0], seed=0)
    assert np.isfinite(bpc_out["bpc_best_calibrated"]), "T6 BPC not finite: %s" % bpc_out
    assert bpc_out["bpc_raw"] > 0.0, "T6 raw BPC sane: %s" % bpc_out

    # T7: pretrained arm with TINY synthetic KV (no network) -- mock gensim KV
    class _MockKV:
        def __init__(self, dim=10):
            self.vector_size = dim
            self.key_to_index = {"w0": 0, "w1": 1, "w2": 2}
            self._vecs = np.random.default_rng(0).standard_normal((3, dim)).astype(np.float32)
        def __contains__(self, key):
            return key in self.key_to_index
        def __getitem__(self, key):
            return self._vecs[self.key_to_index[key]]
        def get_vector(self, key, norm=False):
            if key in self.key_to_index:
                return self._vecs[self.key_to_index[key]]
            raise KeyError(key)
    mock = _MockKV(dim=10)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(["w0", "w1", "w2", "OOV"], mock)
    assert E_pre.shape == (4, 10), "T7 pretrained shape: %s" % (E_pre.shape,)
    assert n_hit == 3 and n_miss == 1, "T7 hit/miss mismatch: %d/%d" % (n_hit, n_miss)
    # OOV row is zero
    assert float(np.linalg.norm(E_pre[3])) < 1e-9, "T7 OOV not zero: %s" % E_pre[3]

    # T8: simulate full pretrained-projected pipeline with mock KV: shape + sigma=0 ident
    _GENSIM_KV_CACHE["__mock__"] = mock
    # Patch in the mock for one call path: call the inner projection directly
    vocab_p = ["w0", "w1", "w2", "OOV"]
    E_pre_n = _l2_normalize(E_pre)  # OOV row stays zero
    P = _gaussian_projection(in_dim=10, out_dim=64, seed=0)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    # OOV fallback to char-trigram
    E_proj[3] = char_trigram_encode("OOV", 64, seed=0)
    E_proj = _l2_normalize(E_proj)
    cb_p = E_proj[:3].copy()
    pred_p = _argmax_cleanup_batch(cb_p, cb_p)
    assert (pred_p == np.arange(3)).all(), "T8 pretrained sigma=0 ident failed: %s" % pred_p

    # T9: _classify_arm_cleanup bands
    assert _classify_arm_cleanup(0.25, 0.20) == "HARD_PASS", "T9 HP wrong"
    assert _classify_arm_cleanup(0.25, 0.35) == "MIDDLE_BAND", "T9 cv>0.30 should MIDDLE"
    assert _classify_arm_cleanup(0.10, 0.20) == "MIDDLE_BAND", "T9 mid recall MIDDLE"
    assert _classify_arm_cleanup(0.03, 0.10) == "HARD_FAIL", "T9 low recall HF"

    # T10: _classify_arm_bpc bands
    assert _classify_arm_bpc(7.5, 0.04) == "HARD_PASS", "T10 BPC HP"
    assert _classify_arm_bpc(7.5, 0.06) == "MIDDLE_BAND", "T10 BPC cv>0.05 should MIDDLE"
    assert _classify_arm_bpc(7.8, 0.04) == "MIDDLE_BAND", "T10 BPC mid"
    assert _classify_arm_bpc(7.9, 0.04) == "HARD_FAIL", "T10 BPC HF"

    def _mk_unit(rd_per_arm, bpc_per_arm, basin0=1.0):
        by_arm_local = {}
        for al, rd, bp in zip(ARMS, rd_per_arm, bpc_per_arm):
            by_arm_local[al] = {
                "cleanup": {"0.0": basin0, "0.5": rd + 0.05, "1.0": rd + 0.02,
                            "1.5": rd, "2.0": rd - 0.02},
                "recall_discriminator": rd,
                "bpc_raw": bp + 1.0,
                "bpc_best_calibrated": bp,
                "best_lambda": 0.5,
                "best_dev_bpc": bp,
                "bpc_n_eval": 100,
                "wall_encode_s": 0.0, "wall_cleanup_s": 0.0, "wall_bpc_s": 0.0,
                "encoder_meta": {},
            }
        return {
            "seed": 0, "by_arm": by_arm_local,
            "N": 64, "N_DIM": 64, "M": 8, "N_EVAL": 4,
            "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16, "PRETRAIN_DIM": 10,
            "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.01,
        }
    # T11: CONFOUND_FAIL when basin_0 < 1
    u_bad = _mk_unit([0.02, 0.25, 0.30, 0.32], [7.9, 7.6, 7.7, 7.6], basin0=0.85)
    v, m, _ = compute_verdict([u_bad, u_bad, u_bad])
    assert v == "CONFOUND_FAIL", "T11 expected CONFOUND_FAIL got %s" % v

    # T12: HARD_PASS when any arm dual-gain
    u_dual = _mk_unit([0.02, 0.30, 0.10, 0.10], [7.9, 7.5, 7.8, 7.8])
    v, m, d = compute_verdict([u_dual, u_dual, u_dual])
    assert v == "HARD_PASS", "T12 expected HARD_PASS got %s msg=%s" % (v, m[:200])
    assert "ARM_WORD2VEC_300D" in d["any_dual_gain_pass"], "T12 dual arm wrong: %s" % d["any_dual_gain_pass"]

    # T13: HARD_FAIL when no arm clears either
    u_null = _mk_unit([0.02, 0.03, 0.04, 0.02], [7.95, 7.92, 7.90, 7.88])
    v, m, _ = compute_verdict([u_null, u_null, u_null])
    assert v == "HARD_FAIL", "T13 expected HARD_FAIL got %s msg=%s" % (v, m[:200])

    # T14: MIDDLE_BAND when partial (one arm clears A only)
    u_partial = _mk_unit([0.02, 0.30, 0.05, 0.05], [7.95, 7.85, 7.90, 7.90])
    v, m, _ = compute_verdict([u_partial, u_partial, u_partial])
    assert v == "MIDDLE_BAND", "T14 expected MIDDLE got %s msg=%s" % (v, m[:200])

    print("[selftest] PASS: T1 trigram + T2 baseline arm + T3 projection + T4 cleanup + "
          "T5 W shape + T6 bpc finite + T7 mock-KV lookup + T8 pretrained sigma=0 ident + "
          "T9 cleanup bands + T10 bpc bands + T11 CONFOUND + T12 HARD_PASS + "
          "T13 HARD_FAIL + T14 MIDDLE OK",
          flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d M=%d N_EVAL=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
          "seeds=%s arms=%s | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, M, N_EVAL, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "M": M,
               "schema": "encoder-word2vec-substrate-bind-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "M": M,
        "N_EVAL": N_EVAL,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_encoder_word2vec_substrate_bind_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (substrate-native cleanup + Path-A LM; pretrained encoders are open-weight static lookups; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
