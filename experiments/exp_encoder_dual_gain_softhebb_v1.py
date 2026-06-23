"""encoder_dual_gain_softhebb_v1 -- Shannon-floor META branch-3 PIVOT 4-arm dual-gain cell.

Tests whether a substrate-native learned/structured encoder closes BOTH (a) cleanup
recall at sigma=1.5 production-regime AND (b) Path-A substrate-LM BPC gap to unigram,
SAME encoder producing both lifts. Branch #3 of Shannon-floor META (cert row 675) is
the only unclosed cell: prior 2 branches (N-INDEPENDENT, M-INDEPENDENT) chain-grade-
saturated; branch #3 = learned/structured encoder keys at production-regime.

DESIGN (4 arms x cleanup-sweep + path-A BPC x 3 seeds at N_DIM=4096):
  ARM_CHAR_TRIGRAM         existing substrate-native trigram bundling baseline.
                           Tests branch #3 "naive learned keys."
  ARM_SOFTHEBB_FORWARD     forward-only soft-WTA Hebbian layer over char-trigram;
                           streaming-Hebbian on text8 ingest; no backprop; k-WTA mask.
  ARM_FOLDIAK_ANTI_HEBB    lateral inhibition between codebook entries during write;
                           substrate auto-whitens its own codebook (Foldiak 1990).
  ARM_FPE_CONTRASTIVE      Forward-Forward (Hinton 2022) 2-phase Hebbian: positive
                           phase on real (x_t, x_{t+1}) pair, negative phase decrement
                           on unigram-sampled negative pair. Pure forward.

USER DIRECTIVE 2026-06-22 compliant: no MiniLM, no BGE, no proprietary embedding.
All 4 arms substrate-native or substrate-trainable.

PRE-REG bands (notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md):
  METRIC A (cleanup recall@1 @ sigma=1.5 per arm vs baseline 0.022):
    HARD_PASS:   recall >= 0.20 AND cv <= 0.30
    HARD_FAIL:   recall <= 0.05
    MIDDLE_BAND: 0.05 < recall < 0.20
  METRIC B (substrate-LM BPC vs unigram 7.738 per arm):
    HARD_PASS:   best_calibrated_bpc < 7.738 AND cv <= 0.05
    HARD_FAIL:   best_calibrated_bpc >= 7.864
    MIDDLE_BAND: 7.738 < bpc < 7.864
  CELL VERDICT:
    HARD_PASS  = ANY arm clears BOTH A AND B (dual-gain confluence)
    HARD_FAIL  = NO arm clears EITHER A or B  (Shannon-floor scope-wide saturated)
    MIDDLE_BAND= one arm clears A only OR B only (partial mechanism)

SANITY (CONFOUND_FAIL detector):
  sigma=0 across all 4 arms must yield recall@1 = 1.000.
  lambda=1.0 BPC = pure substrate raw BPC (interp sanity).

SUBSTRATE-ONLY: n_llm_calls = 0; numpy-only; no torch; remote_cpu_queue.

Cites:
  - notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md
  - notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md (parent ENC1 HARD_FAIL)
  - experiments/exp_enc1_structured_n_lift_v1.py (parent cell)
  - experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (Path-A 7.864 BPC ref)
  - Moraitis et al. 2107.05747 (SoftHebb)
  - Foldiak 1990 Biol Cybern (anti-Hebbian decorrelation)
  - Hinton 2022 Forward-Forward (no-backprop contrastive)
  - hdlab/char_trigram_encoder.py (substrate-native baseline)
  - Shannon-floor META cert row 675

Skunkworks structural blockers honored:
  #3 _LLM_CALL_COUNTER = [0] (substrate-only)
  #1 per_unit per seed
  #2 cv across seeds in compute_verdict
  #4 atexit synthesizer for timeout-resilience
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit, hashlib
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "encoder_dual_gain_softhebb_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]

# Reference baselines from prior cells (constants in the pre-reg bands)
UNIGRAM_BPC_REF = 7.738
PATH_A_CURRENT_BPC_REF = 7.864
CLEANUP_BASELINE_RECALL_REF = 0.022

# Pre-reg HARD bands (cleanup at sigma=1.5; bpc on held)
HP_CLEANUP_RECALL = 0.20
HF_CLEANUP_RECALL = 0.05
HP_CLEANUP_CV_MAX = 0.30
HP_BPC = UNIGRAM_BPC_REF       # < 7.738
HF_BPC = PATH_A_CURRENT_BPC_REF  # >= 7.864
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
M = 200
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
DISCRIMINATOR_SIGMA = 1.5
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
VOCAB_CAP = 4000
INGEST_CHUNK = 8192
K_WTA = 5

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

ARMS = ["ARM_CHAR_TRIGRAM", "ARM_SOFTHEBB_FORWARD", "ARM_FOLDIAK_ANTI_HEBB", "ARM_FPE_CONTRASTIVE"]

CONFIG_VERSION = (
    "encoder_dual_gain_softhebb_v1; N_DIM=%d M=%d N_EVAL=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d sigmas=%s arms=%s seeds=%s mode=%s K_WTA=%d INGEST_CHUNK=%d "
    "lambda_grid=%s; bands HP_recall>=%.2f HF_recall<=%.2f HP_bpc<%.3f HF_bpc>=%.3f"
) % (
    N_DIM, M, N_EVAL, N_TRAIN, N_HELD, VOCAB_CAP, SIGMA_SWEEP, ARMS, SEEDS, RUN_MODE,
    K_WTA, INGEST_CHUNK, LAMBDA_GRID, HP_CLEANUP_RECALL, HF_CLEANUP_RECALL, HP_BPC, HF_BPC,
)


# ============================================================================
# Substrate primitives
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Bag-of-trigrams sign-bundled bipolar HD vector. Substrate-native; deterministic."""
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


# ============================================================================
# Encoder ARMS -- each returns (codebook_M, encoder_state_for_path_A)
# encoder_state = E_matrix [V, N_DIM] usable for Path-A Hebbian LM
# ============================================================================

def encode_arm_char_trigram(vocab: List[str], M_atoms: int, n_dim: int, seed: int):
    """ARM 1: substrate-native baseline; pure trigram bundling. No training."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E = _l2_normalize(E)
    # Codebook = first M_atoms vocab entries' encodings
    codebook = E[:M_atoms].copy()
    return codebook, E


def encode_arm_softhebb_forward(vocab: List[str], M_atoms: int, n_dim: int, seed: int,
                                 idx_train: np.ndarray):
    """ARM 2: forward-only soft-WTA Hebbian layer over char-trigram input.

    Substrate-native upgrade per Moraitis 2021. Single linear layer W [n_dim, n_dim]
    initialized small; for each chunk of text8 token pairs (X [B, n_dim], X_next [B, n_dim])
    compute Z = X @ W.T, soft-WTA top-k mask (k=K_WTA) along output axis, Hebbian update:
        W += eta * Y.T @ X / B
    where Y masks all but top-k by absolute response. No backprop. Forward-only.
    Trained on N_TRAIN streaming text8 pairs in batched matmuls (no per-pair loop).
    After training, apply W as the encoder transformation: out = W @ char_trigram(word).
    """
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    rng = np.random.default_rng(seed * 31 + 1)
    # Init W as identity-ish + small noise: encourages stable forward + room to drift
    W = (np.eye(n_dim, dtype=np.float32) * 0.1 +
         rng.standard_normal((n_dim, n_dim)).astype(np.float32) * (0.005 / np.sqrt(n_dim)))
    eta = 0.001
    decay = 1e-6
    n_pairs = len(idx_train) - 1
    # Use up to 20k pairs at full, 2k at smoke; process in matmul-vectorized batches
    n_train_effective = min(n_pairs, 20_000 if RUN_MODE == "full" else 2_000)
    batch_size = 256
    if n_train_effective > 0:
        sub_idx = np.linspace(0, n_pairs - 1, n_train_effective).astype(np.int64)
        for chunk_start in range(0, n_train_effective, batch_size):
            chunk_end = min(chunk_start + batch_size, n_train_effective)
            js = sub_idx[chunk_start:chunk_end]
            X = E_in[idx_train[js]]               # [B, n_dim]
            Z = X @ W.T                            # [B, n_dim]
            k = K_WTA
            if k < n_dim:
                abs_Z = np.abs(Z)
                # row-wise top-k: threshold per row
                thresh = np.partition(abs_Z, -k, axis=1)[:, -k:].min(axis=1, keepdims=True)
                mask = (abs_Z >= thresh).astype(np.float32)
                Y = Z * mask
            else:
                Y = Z
            # Batched Hebbian: W += eta * Y.T @ X / B
            B_eff = max(X.shape[0], 1)
            W += (eta / B_eff) * (Y.T @ X)
            W *= (1.0 - decay)
    E_out = (E_in @ W.T).astype(np.float32)
    E_out = _l2_normalize(E_out)
    codebook = E_out[:M_atoms].copy()
    return codebook, E_out


def encode_arm_foldiak_anti_hebb(vocab: List[str], M_atoms: int, n_dim: int, seed: int,
                                  idx_train: np.ndarray):
    """ARM 3: Foldiak 1990 anti-Hebbian decorrelation.

    Maintain lateral W_lat [M, M] inhibitory weights. For codebook entries (first M vocab),
    iteratively apply lateral inhibition: codebook[i] -= sum_{j!=i} W_lat[i,j] * codebook[j].
    Update W_lat via anti-Hebb: W_lat[i,j] += eta * y_i * y_j - decay * W_lat[i,j]
    where y = activations on a stream of inputs. Substrate auto-whitens own codebook.
    Encoder output for non-codebook vocab: stay at char-trigram (only codebook itself
    is decorrelated; this isolates the lateral-inhibition mechanism on the M atoms).
    For Path-A BPC: use trigram encoder for E_out (anti-Hebb impact is on cleanup-codebook).
    """
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    codebook = E_in[:M_atoms].copy()
    # Lateral W_lat [M_atoms, M_atoms]; diagonal forced zero
    W_lat = np.zeros((M_atoms, M_atoms), dtype=np.float32)
    eta = 0.01
    decay = 1e-4
    n_iter = 30 if RUN_MODE == "full" else 5
    for _ in range(n_iter):
        # Forward: y = codebook @ random_input direction (use mean of trigram inputs as the canonical drive)
        # For decorrelation, we use the codebook entries themselves as activations
        # y_i = activation of codebook entry i (use self-similarity to the data stream)
        # Apply lateral inhibition: codebook[i] -= sum_{j!=i} W_lat[i,j] * codebook[j]
        np.fill_diagonal(W_lat, 0.0)
        inhibition = W_lat @ codebook  # [M, n_dim]
        codebook = codebook - inhibition
        codebook = _l2_normalize(codebook)
        # Update W_lat via anti-Hebb on correlation structure
        Y = codebook @ codebook.T  # [M, M] cross-correlation (target = identity)
        np.fill_diagonal(Y, 0.0)
        W_lat += eta * Y
        W_lat *= (1.0 - decay)
        W_lat = np.clip(W_lat, -1.0, 1.0)
    np.fill_diagonal(W_lat, 0.0)
    # For Path-A LM use base trigram encoding (anti-Hebb is codebook-local)
    E_out = E_in.copy()
    # But overwrite the first M entries with the decorrelated atoms
    E_out[:M_atoms] = codebook
    return codebook, E_out


def encode_arm_fpe_contrastive(vocab: List[str], M_atoms: int, n_dim: int, seed: int,
                                idx_train: np.ndarray):
    """ARM 4: Forward-Forward (Hinton 2022) 2-phase Hebbian contrastive.

    Pure forward; no backprop. Maintains W [n_dim, n_dim] encoder transform.
    Positive phase batched: W += (eta_pos / B) * X_next.T @ X_t.
    Negative phase batched: W -= (eta_neg / B) * X_neg.T @ X_t  where X_neg ~ unigram.
    Substrate-native (no labels; uses corpus structure as self-supervision).
    Batched matmul to avoid per-pair Python loop. Wall-bounded by batch count.
    """
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    rng = np.random.default_rng(seed * 41 + 2)
    W = (np.eye(n_dim, dtype=np.float32) * 0.1 +
         rng.standard_normal((n_dim, n_dim)).astype(np.float32) * (0.005 / np.sqrt(n_dim)))
    eta_pos = 0.001
    eta_neg = 0.001
    counts = np.bincount(idx_train, minlength=V).astype(np.float64) + 0.1
    p_uni = counts / counts.sum()
    n_pairs = len(idx_train) - 1
    n_train_effective = min(n_pairs, 20_000 if RUN_MODE == "full" else 2_000)
    batch_size = 256
    if n_train_effective > 0:
        sub_idx = np.linspace(0, n_pairs - 1, n_train_effective).astype(np.int64)
        neg_samples = rng.choice(V, size=n_train_effective, replace=True, p=p_uni)
        for chunk_start in range(0, n_train_effective, batch_size):
            chunk_end = min(chunk_start + batch_size, n_train_effective)
            js = sub_idx[chunk_start:chunk_end]
            X_t = E_in[idx_train[js]]                  # [B, n_dim]
            X_next = E_in[idx_train[js + 1]]           # [B, n_dim]
            X_neg = E_in[neg_samples[chunk_start:chunk_end]]  # [B, n_dim]
            B_eff = max(X_t.shape[0], 1)
            W += (eta_pos / B_eff) * (X_next.T @ X_t)
            W -= (eta_neg / B_eff) * (X_neg.T @ X_t)
    E_out = (E_in @ W.T).astype(np.float32)
    E_out = _l2_normalize(E_out)
    codebook = E_out[:M_atoms].copy()
    return codebook, E_out


# ============================================================================
# Metric A: cleanup recall over sigma sweep
# ============================================================================

def _argmax_cleanup_batch(cues, codebook):
    cb_n = _l2_normalize(codebook)
    cu_n = _l2_normalize(cues)
    scores = cu_n @ cb_n.T
    return np.argmax(scores, axis=1).astype(np.int64)


def cleanup_eval_arm(codebook: np.ndarray, n_eval: int, sigmas: list, seed: int) -> dict:
    """Cleanup recall@1 across sigma sweep on M-row codebook."""
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
    """Stable softmax along last axis."""
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
    # Eval positions: (ctx, nxt) pairs from held; mask out <unk> ctx
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
    # Substrate logits per held position
    # pred_vec[b] = W @ E[ctx[b]]; substrate_logits[b, v] = <pred_vec[b], E[v]>
    sub_logits = np.zeros((n_eval, V), dtype=np.float32)
    chunk = 1024
    for b in range(0, n_eval, chunk):
        end = min(b + chunk, n_eval)
        pred_vec = E[ctx[b:end]] @ W.T  # [chunk, n_dim]
        # L2-normalize pred_vec
        pn = np.linalg.norm(pred_vec, axis=1, keepdims=True)
        pn[pn < 1e-9] = 1e-9
        pred_vec = pred_vec / pn
        sub_logits[b:end] = pred_vec @ E.T
    # Unigram
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    # Per-pos substrate log-prob
    sub_logp = np.log(np.clip(softmax_safe(sub_logits, temperature=1.0), 1e-30, 1.0))
    # Tune lambda on dev half; eval on test half
    n_dev = n_eval // 2
    ctx_test = ctx[n_dev:]
    nxt_test = nxt[n_dev:]
    nxt_dev = nxt[:n_dev]
    sub_logp_dev = sub_logp[:n_dev]
    sub_logp_test = sub_logp[n_dev:]
    # Raw BPC (lambda=1.0, pure substrate)
    raw_logp_nxt_test = sub_logp_test[np.arange(len(nxt_test)), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt_test)) / np.log(2.0)
    # Lambda sweep on dev
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
    # Apply best_lambda on test
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
    encoders = {
        "ARM_CHAR_TRIGRAM":      encode_arm_char_trigram,
        "ARM_SOFTHEBB_FORWARD":  encode_arm_softhebb_forward,
        "ARM_FOLDIAK_ANTI_HEBB": encode_arm_foldiak_anti_hebb,
        "ARM_FPE_CONTRASTIVE":   encode_arm_fpe_contrastive,
    }
    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] encoding..." % (seed, arm_label), flush=True)
        fn = encoders[arm_label]
        if arm_label == "ARM_CHAR_TRIGRAM":
            codebook, E_full = fn(vocab, M_atoms, N_DIM, seed)
        else:
            codebook, E_full = fn(vocab, M_atoms, N_DIM, seed, idx_train)
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
        }
        a = by_arm[arm_label]
        print("    [seed=%d arm=%s] disc=%.3f basin_0=%.3f basin_1.5=%.3f bpc_raw=%.3f "
              "bpc_best=%.3f lam=%.2f (enc=%.1fs clean=%.1fs bpc=%.1fs)" % (
                  seed, arm_label, a["recall_discriminator"],
                  cleanup.get(0.0, 0.0), cleanup.get(1.5, 0.0),
                  a["bpc_raw"], a["bpc_best_calibrated"], a["best_lambda"],
                  t_enc, t_clean, t_bpc), flush=True)

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
        "K_WTA": K_WTA,
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
        # Cleanup basin agg
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

    # Cell-level verdict per pre-reg
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
            "HD-substrate-native encoder-side dual-gain drill; 4 arms x cleanup-sigma-sweep + "
            "Path-A BPC at N_DIM=%d M=%d N_TRAIN=%d N_HELD=%d V=%d K_WTA=%d; %d seeds; "
            "dual-gain HARD_PASS = ANY arm clears BOTH metric A (cleanup recall>=0.20 @ sigma=1.5) "
            "AND metric B (BPC<%.3f); HARD_FAIL = NO arm clears EITHER metric." % (
                N_DIM, M, N_TRAIN, N_HELD, VOCAB_CAP, K_WTA, len(units), HP_BPC)),
        "cites": [
            "notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md (source-of-truth)",
            "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md (parent ENC1 HARD_FAIL)",
            "experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (BPC ref 7.864)",
            "Moraitis_2107_05747_SoftHebb",
            "Foldiak_1990_anti_Hebbian_decorrelation",
            "Hinton_2022_Forward_Forward",
            "hdlab/char_trigram_encoder.py",
            "Shannon_floor_META_cert_row_675",
        ],
    }

    # Arm summary string
    parts = []
    for al in arm_labels:
        a = by_arm_agg[al]
        parts.append("%s=disc%.3f(%s)/bpc%.3f(%s)%s" % (
            al, a["recall_discriminator_mean"], a["cleanup_classification"],
            a["bpc_best_calibrated_mean"], a["bpc_classification"],
            "/DUAL" if a["dual_gain_HARD_PASS"] else ""))
    summary = "DUAL_GAIN @ sigma=%.2f: %s | sanity_ok=%s" % (
        DISCRIMINATOR_SIGMA, " | ".join(parts), sanity_ok)

    # CONFOUND check first
    if not sanity_ok:
        return ("CONFOUND_FAIL",
                ("CONFOUND_FAIL: sigma=0 recall < 1.000 for %d arm(s) (%s); implementation bug "
                 "suspected, NOT mechanism rejection. " % (len(sanity_failures), "; ".join(sanity_failures)))
                + summary,
                detail)

    # Cell-level HARD_PASS = any dual-gain
    if any_dual:
        any_dual.sort(key=lambda x: (-by_arm_agg[x]["recall_discriminator_mean"],
                                      by_arm_agg[x]["bpc_best_calibrated_mean"]))
        top = any_dual[0]
        t = by_arm_agg[top]
        return ("HARD_PASS",
                ("DUAL_GAIN HARD_PASS: arm %s clears BOTH cleanup (recall=%.3f cv=%.2f >= %.2f) AND "
                 "BPC (best=%.3f cv=%.2f < %.3f); branch #3 of Shannon-floor META FALSIFIED at production-"
                 "regime; encoder geometry IS the lever for cleanup AND closes BPC gap to unigram; "
                 "substrate-product unblock: chain-grade-tier candidate. dual_arms=%d total. " % (
                     top, t["recall_discriminator_mean"], t["recall_discriminator_cv"], HP_CLEANUP_RECALL,
                     t["bpc_best_calibrated_mean"], t["bpc_best_calibrated_cv"], HP_BPC,
                     len(any_dual))) + summary,
                detail)

    # Cell-level HARD_FAIL = no arm clears EITHER metric
    if cleanup_all_fail and bpc_all_fail:
        return ("HARD_FAIL",
                ("DUAL_GAIN HARD_FAIL: ALL %d arms HARD_FAIL on BOTH cleanup (max recall <= %.2f) "
                 "AND BPC (min BPC >= %.3f); Shannon-floor META branch #3 CLOSES; META promoted to "
                 "chain-grade scope-wide; substrate-as-LM structurally dead with current encoder "
                 "architectures; pivot: descope sigma>=1.5 permanently + char-LSTM backprop infra "
                 "(~1 week) is only remaining lever. " % (
                     len(arm_labels), HF_CLEANUP_RECALL, HF_BPC)) + summary,
                detail)
    # If at least one metric has at least one HARD_PASS or some MIDDLE coverage:
    # Cell-level HARD_FAIL also if NO arm clears EITHER (per the pre-reg spec)
    if len(cleanup_pass) == 0 and len(bpc_pass) == 0:
        return ("HARD_FAIL",
                ("DUAL_GAIN HARD_FAIL: NO arm clears EITHER metric A (cleanup HP) or metric B (BPC HP); "
                 "best cleanup arm in MIDDLE_BAND; best BPC arm in MIDDLE_BAND; no encoder lifts "
                 "substrate at production-regime to threshold. ") + summary,
                detail)

    # Otherwise MIDDLE_BAND: at least one metric A or B HARD_PASS but not dual on same arm
    msg_parts = []
    if cleanup_pass:
        msg_parts.append("cleanup HARD_PASS arms=%s" % cleanup_pass)
    if bpc_pass:
        msg_parts.append("bpc HARD_PASS arms=%s" % bpc_pass)
    return ("MIDDLE_BAND",
            ("DUAL_GAIN MIDDLE_BAND: at least one arm clears Metric A only OR Metric B only but "
             "NO arm clears BOTH on same seed-mean; partial mechanism characterization; route to "
             "second-tier follow-up. " + " ; ".join(msg_parts) + ". ") + summary,
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
            "metrics_source": "atexit_synthesize_partial_encoder_dual_gain_softhebb_v1",
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
    # T1: char-trigram encoder produces L2-normalized bipolar-derived sign vectors
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,), "T1 char_trigram shape: %s" % (v.shape,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 char_trigram not bipolar: %s" % uniq

    # T2: encoder ARM_CHAR_TRIGRAM produces M=8 codebook from 16-vocab; cleanup sigma=0 -> recall=1
    vocab_t = ["w%d" % i for i in range(16)]
    cb, E = encode_arm_char_trigram(vocab_t, 8, 64, seed=0)
    assert cb.shape == (8, 64), "T2 codebook shape: %s" % (cb.shape,)
    pred = _argmax_cleanup_batch(cb, cb)
    assert (pred == np.arange(8)).all(), "T2 sigma=0 identity failed: %s" % pred

    # T3: encoder ARM_SOFTHEBB_FORWARD produces shape (M, n_dim) post-training; sigma=0 ident
    idx_train_t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 0, 1] * 100, dtype=np.int64)
    cb_sh, E_sh = encode_arm_softhebb_forward(vocab_t, 8, 64, seed=0, idx_train=idx_train_t)
    assert cb_sh.shape == (8, 64), "T3 SoftHebb codebook shape: %s" % (cb_sh.shape,)
    pred_sh = _argmax_cleanup_batch(cb_sh, cb_sh)
    assert (pred_sh == np.arange(8)).all(), "T3 SoftHebb sigma=0 ident failed: %s" % pred_sh

    # T4: encoder ARM_FOLDIAK_ANTI_HEBB shape + sigma=0 ident
    cb_fl, E_fl = encode_arm_foldiak_anti_hebb(vocab_t, 8, 64, seed=0, idx_train=idx_train_t)
    assert cb_fl.shape == (8, 64), "T4 Foldiak codebook shape: %s" % (cb_fl.shape,)
    pred_fl = _argmax_cleanup_batch(cb_fl, cb_fl)
    assert (pred_fl == np.arange(8)).all(), "T4 Foldiak sigma=0 ident failed: %s" % pred_fl

    # T5: encoder ARM_FPE_CONTRASTIVE shape + sigma=0 ident
    cb_fp, E_fp = encode_arm_fpe_contrastive(vocab_t, 8, 64, seed=0, idx_train=idx_train_t)
    assert cb_fp.shape == (8, 64), "T5 FPE codebook shape: %s" % (cb_fp.shape,)
    pred_fp = _argmax_cleanup_batch(cb_fp, cb_fp)
    assert (pred_fp == np.arange(8)).all(), "T5 FPE sigma=0 ident failed: %s" % pred_fp

    # T6: cleanup_eval_arm returns dict keyed by sigma with float values; sigma=0 -> 1.0
    out = cleanup_eval_arm(cb, n_eval=4, sigmas=[0.0, 1.0], seed=0)
    assert 0.0 in out and out[0.0] == 1.0, "T6 sigma=0 cleanup not 1.0: %s" % out

    # T7: build_hebbian_W_np produces correct shape
    W = build_hebbian_W_np(idx_train_t, E, INGEST_CHUNK)
    assert W.shape == (64, 64), "T7 W shape: %s" % (W.shape,)

    # T8: softmax_safe + path_a_bpc_arm produces finite BPC on tiny data
    bpc_out = path_a_bpc_arm(E, vocab_t, idx_train_t, idx_train_t[:50],
                              lambda_grid=[0.5, 1.0], seed=0)
    assert np.isfinite(bpc_out["bpc_best_calibrated"]), "T8 BPC not finite: %s" % bpc_out

    # T9: lambda=1.0 in lambda_grid -> sanity: pure substrate dev BPC matches the path with lam=1.0
    # (substrate raw BPC == bpc_raw when held subset matches; weak structural check)
    assert bpc_out["bpc_raw"] > 0.0, "T9 raw BPC sane: %s" % bpc_out

    # T10: _classify_arm_cleanup bands
    assert _classify_arm_cleanup(0.25, 0.20) == "HARD_PASS", "T10 HP wrong"
    assert _classify_arm_cleanup(0.25, 0.35) == "MIDDLE_BAND", "T10 cv>0.30 should MIDDLE"
    assert _classify_arm_cleanup(0.10, 0.20) == "MIDDLE_BAND", "T10 mid recall MIDDLE"
    assert _classify_arm_cleanup(0.03, 0.10) == "HARD_FAIL", "T10 low recall HF"

    # T11: _classify_arm_bpc bands
    assert _classify_arm_bpc(7.5, 0.04) == "HARD_PASS", "T11 BPC HP"
    assert _classify_arm_bpc(7.5, 0.06) == "MIDDLE_BAND", "T11 BPC cv>0.05 should MIDDLE"
    assert _classify_arm_bpc(7.8, 0.04) == "MIDDLE_BAND", "T11 BPC mid"
    assert _classify_arm_bpc(7.9, 0.04) == "HARD_FAIL", "T11 BPC HF"

    # T12: compute_verdict CONFOUND_FAIL when sigma=0 not 1.0
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
            }
        return {
            "seed": 0, "by_arm": by_arm_local,
            "N": 64, "N_DIM": 64, "M": 8, "N_EVAL": 4,
            "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16, "K_WTA": 5,
            "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.01,
        }
    u_bad = _mk_unit([0.02, 0.25, 0.30, 0.32], [7.9, 7.6, 7.7, 7.6], basin0=0.85)
    v, m, _ = compute_verdict([u_bad, u_bad, u_bad])
    assert v == "CONFOUND_FAIL", "T12 expected CONFOUND_FAIL got %s" % v

    # T13: compute_verdict HARD_PASS when ANY arm dual-gain (clean+bpc HP same arm)
    u_dual = _mk_unit([0.02, 0.30, 0.10, 0.10], [7.9, 7.5, 7.8, 7.8])
    v, m, d = compute_verdict([u_dual, u_dual, u_dual])
    assert v == "HARD_PASS", "T13 expected HARD_PASS got %s msg=%s" % (v, m[:200])
    assert "ARM_SOFTHEBB_FORWARD" in d["any_dual_gain_pass"], "T13 dual arm wrong: %s" % d["any_dual_gain_pass"]

    # T14: compute_verdict HARD_FAIL when NO arm clears either metric A or B
    u_null = _mk_unit([0.02, 0.03, 0.04, 0.02], [7.95, 7.92, 7.90, 7.88])
    v, m, _ = compute_verdict([u_null, u_null, u_null])
    assert v == "HARD_FAIL", "T14 expected HARD_FAIL got %s msg=%s" % (v, m[:200])

    # T15: compute_verdict MIDDLE when cleanup HP on one arm but BPC HF on same arm (no dual)
    u_partial = _mk_unit([0.02, 0.30, 0.05, 0.05], [7.95, 7.85, 7.90, 7.90])
    v, m, _ = compute_verdict([u_partial, u_partial, u_partial])
    assert v == "MIDDLE_BAND", "T15 expected MIDDLE got %s msg=%s" % (v, m[:200])

    print("[selftest] PASS: T1 trigram + T2 char_trigram_arm + T3 softhebb + T4 foldiak + T5 fpe + "
          "T6 cleanup_eval + T7 W shape + T8 bpc finite + T9 raw bpc sane + T10 cleanup bands + "
          "T11 bpc bands + T12 CONFOUND_FAIL + T13 HARD_PASS dual + T14 HARD_FAIL + T15 MIDDLE_BAND OK",
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
               "schema": "encoder-dual-gain-softhebb-v1"}
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
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_encoder_dual_gain_softhebb_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native encoder-side dual-gain; no LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
