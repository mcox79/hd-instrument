"""
exp_b2_substrate_only_tinystories_lm_v1 -- Substrate-only pseudo-LM (Path A; single NEXT_TOKEN relation).

ROUTING: Research B2 anchor (BATCH_HIERARCHICAL_LM_TIER5C 2026-06-08). Substrate-product
  reading: each word = char_trigram HD vector; Hebbian-bind (w_t, NEXT_TOKEN, w_t+1) into a
  single weight matrix W; next-token prediction = argmax_w' cosine(W @ enc(w_t), enc(w')).
  Compare to UNIGRAM (floor) + WORD_BIGRAM (standard NLP baseline).
PRE-REG: preregs/2026-06-22_b2_substrate_only_tinystories_lm_v1.md
  HARD_PASS: ppl(SUB) <= ppl(BIGRAM) AND acc(SUB) >= acc(BIGRAM).
  MIDDLE_BAND: ppl(UNI) > ppl(SUB) > ppl(BIGRAM).
  HARD_FAIL: ppl(SUB) >= ppl(UNI).
FORMULA SELF-TESTS (PROT-022): 1.encoder deterministic 2.bind order-sensitive 3.perfect-recall
  control on 10-cycle 4.unigram == analytic max-class freq 5.bigram ppl hand-crafted match.
CORPUS: data/text8_cache/text8.txt (substitute for TinyStories; ~370k stories not locally
  available; text8 is the proven locally-resident substrate-LM corpus).
ASCII-only. write_metrics. PROT-018: no _nN suffix.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import hashlib
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "b2_substrate_only_tinystories_lm_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]
    V_DIM = 1024
    N_TRAIN = 12000
    N_HELD = 1000
    VOCAB_CAP = 2000
else:
    SEEDS = [7, 17, 23]
    V_DIM = 2048
    N_TRAIN = 120000
    N_HELD = 10000
    VOCAB_CAP = 8000


# ============================================================================
# Substrate primitives
# ============================================================================

def char_trigram_encode(word: str, dim: int, seed: int = 0) -> np.ndarray:
    """Deterministic char-trigram HD vector encoder. Float32 unit-normalized."""
    v = np.zeros(dim, np.float32)
    w = "#" + word + "#"
    for i in range(len(w) - 2):
        tri = w[i:i + 3]
        h = int(hashlib.md5((tri + ":" + str(seed)).encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 32) & 1) else -1.0
        v[idx] += sign
    nrm = np.linalg.norm(v)
    return v / nrm if nrm > 0 else v


def build_encoder(vocab: List[str], dim: int, seed: int) -> np.ndarray:
    """Encode each vocab word -> (V, dim) float32 matrix."""
    E = np.stack([char_trigram_encode(w, dim, seed=seed) for w in vocab], 0).astype(np.float32)
    # row-normalize for safety
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    return E / nrm


def hebbian_bind_next_token(idx_train: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Build W = sum_t outer(E[idx[t+1]], E[idx[t]]) so that W @ enc(w_t) ~= enc(w_{t+1}).

    Returns (dim, dim) float32 matrix.
    """
    dim = E.shape[1]
    # Vectorized: W = E[idx[1:]].T @ E[idx[:-1]]
    src = E[idx_train[:-1]]
    tgt = E[idx_train[1:]]
    W = tgt.T @ src  # (dim, dim)
    return W.astype(np.float32)


# ============================================================================
# Arms
# ============================================================================

def predict_substrate(W: np.ndarray, E: np.ndarray, idx_ctx: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """For each context word idx_ctx[i], return (logits_over_vocab, argmax)."""
    src = E[idx_ctx]                   # (N, dim)
    pred_vec = src @ W.T               # (N, dim)
    # cosine vs every vocab embedding
    pred_norm = np.linalg.norm(pred_vec, axis=1, keepdims=True)
    pred_norm[pred_norm == 0] = 1.0
    pred_vec = pred_vec / pred_norm
    logits = pred_vec @ E.T            # (N, V) in [-1, 1]
    argmax = np.argmax(logits, axis=1)
    return logits, argmax


def softmax(x: np.ndarray, axis: int = -1, temperature: float = 1.0) -> np.ndarray:
    z = x / max(temperature, 1e-6)
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / np.maximum(e.sum(axis=axis, keepdims=True), 1e-30)


def perplexity_from_probs(probs: np.ndarray, idx_true: np.ndarray) -> float:
    p = probs[np.arange(len(idx_true)), idx_true]
    p = np.clip(p, 1e-12, 1.0)
    return float(np.exp(-np.mean(np.log(p))))


def build_bigram(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    """Laplace-smoothed bigram P(w_t+1 | w_t). Returns (V, V) row-stochastic."""
    P = np.full((V, V), alpha, dtype=np.float64)
    np.add.at(P, (idx_train[:-1], idx_train[1:]), 1.0)
    P /= P.sum(axis=1, keepdims=True)
    return P


def build_unigram(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Self-tests
# ============================================================================

def _selftest():
    # 1. encoder deterministic
    a1 = char_trigram_encode("hello", 256, seed=42)
    a2 = char_trigram_encode("hello", 256, seed=42)
    assert np.allclose(a1, a2), "encoder deterministic"
    # 2. bind order-sensitive: a-then-b vs b-then-a produce different W
    vocab = ["a", "b", "c", "d", "e"]
    E = build_encoder(vocab, 256, seed=0)
    idx_ab = np.array([0, 1, 2, 3], dtype=np.int64)
    idx_ba = np.array([3, 2, 1, 0], dtype=np.int64)
    W_ab = hebbian_bind_next_token(idx_ab, E)
    W_ba = hebbian_bind_next_token(idx_ba, E)
    assert np.linalg.norm(W_ab - W_ba) > 0.1, "bind order-sensitive"
    # 3. perfect-recall control: train on a 10-token cycle, expect high top-1 on train
    cycle_vocab = [f"tok{i}" for i in range(10)]
    Ec = build_encoder(cycle_vocab, 1024, seed=0)
    seq = np.tile(np.arange(10), 5).astype(np.int64)  # 5 cycles
    Wc = hebbian_bind_next_token(seq, Ec)
    _, am = predict_substrate(Wc, Ec, seq[:-1])
    acc = float((am == seq[1:]).mean())
    assert acc >= 0.7, f"perfect-recall control: acc={acc:.3f} < 0.7"
    # 4. unigram == analytic max-class freq
    idx = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)  # max-class=2 freq=0.4
    U = build_unigram(idx, V=4, alpha=0.0)
    am_uni = int(np.argmax(U))
    held = np.array([2, 2, 2, 1, 0], dtype=np.int64)
    pred = np.full_like(held, am_uni)
    acc_uni = float((pred == held).mean())  # 3/5 = 0.6
    assert abs(acc_uni - 0.6) < 1e-9, f"unigram analytic acc mismatch: {acc_uni}"
    # 5. bigram ppl: corpus "a b a b" -> P(b|a)=1, P(a|b)=1; held-out "a b a" ppl=1
    vocab5 = ["a", "b"]
    train5 = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    B = build_bigram(train5, V=2, alpha=1e-9)
    # held-out positions: ctx=[0, 1], true=[1, 0]; per-token prob ~ 1.0
    p = B[np.array([0, 1]), np.array([1, 0])]
    ppl5 = float(np.exp(-np.mean(np.log(np.clip(p, 1e-12, 1.0)))))
    assert abs(ppl5 - 1.0) < 0.01, f"bigram ppl hand-crafted mismatch: {ppl5}"
    print("[selftest] PASS: encoder bind cycle-recall unigram bigram", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Corpus loader
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    """Return first n_total whitespace-split tokens from text8."""
    if not TEXT8.exists():
        print(f"[FATAL] corpus missing at {TEXT8}", flush=True)
        sys.exit(1)
    out: List[str] = []
    # text8 is one long line; read in chunks
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n_total:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()  # may be incomplete
            out.extend(parts)
        if buf and len(out) < n_total:
            out.append(buf)
    return out[:n_total]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    """Cap-V most-frequent tokens + <unk>. Returns (vocab_list, word->idx)."""
    from collections import Counter
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int) -> Dict:
    t_seed = time.time()
    print(f"\n[seed={seed}] loading corpus + building vocab", flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    unk = w2i["<unk>"]

    # held-out eval positions: ctx in [0, N_HELD-1), exclude where ctx is unk
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    ctx_eval = ctx[mask]
    nxt_eval = nxt[mask]
    n_eval = len(ctx_eval)
    print(f"[seed={seed}] V={V} train_tok={N_TRAIN} held_tok={N_HELD} eval_pos={n_eval}", flush=True)

    # --- SUBSTRATE_LM ---
    t0 = time.time()
    E = build_encoder(vocab, V_DIM, seed=seed)
    W = hebbian_bind_next_token(idx_train, E)
    logits_sub, argmax_sub = predict_substrate(W, E, ctx_eval)
    probs_sub = softmax(logits_sub, axis=-1, temperature=0.1)
    ppl_sub = perplexity_from_probs(probs_sub, nxt_eval)
    acc_sub = float((argmax_sub == nxt_eval).mean())
    t_sub = time.time() - t0
    print(f"[seed={seed}] SUBSTRATE_LM   ppl={ppl_sub:.2f} acc={acc_sub:.4f} ({t_sub:.1f}s)", flush=True)

    # --- UNIGRAM_BASELINE ---
    t0 = time.time()
    U = build_unigram(idx_train, V=V, alpha=0.1)
    argmax_uni = np.full(n_eval, int(np.argmax(U)), dtype=np.int64)
    probs_uni = np.broadcast_to(U[None, :], (n_eval, V))
    ppl_uni = perplexity_from_probs(probs_uni, nxt_eval)
    acc_uni = float((argmax_uni == nxt_eval).mean())
    t_uni = time.time() - t0
    print(f"[seed={seed}] UNIGRAM        ppl={ppl_uni:.2f} acc={acc_uni:.4f} ({t_uni:.1f}s)", flush=True)

    # --- WORD_BIGRAM_BASELINE ---
    t0 = time.time()
    B = build_bigram(idx_train, V=V, alpha=0.1)
    rows = B[ctx_eval]                                # (n_eval, V)
    argmax_bg = np.argmax(rows, axis=1)
    p_bg = rows[np.arange(n_eval), nxt_eval]
    p_bg = np.clip(p_bg, 1e-12, 1.0)
    ppl_bg = float(np.exp(-np.mean(np.log(p_bg))))
    acc_bg = float((argmax_bg == nxt_eval).mean())
    t_bg = time.time() - t0
    print(f"[seed={seed}] WORD_BIGRAM    ppl={ppl_bg:.2f} acc={acc_bg:.4f} ({t_bg:.1f}s)", flush=True)

    return {
        "seed": seed,
        "V": V,
        "V_DIM": V_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "n_eval": n_eval,
        "ppl_substrate": ppl_sub,
        "ppl_unigram": ppl_uni,
        "ppl_bigram": ppl_bg,
        "acc_substrate": acc_sub,
        "acc_unigram": acc_uni,
        "acc_bigram": acc_bg,
        "elapsed_s": time.time() - t_seed,
    }


# ============================================================================
# Verdict
# ============================================================================

def verdict(ps: List[Dict]) -> Tuple[str, str]:
    ppl_sub = float(np.mean([p["ppl_substrate"] for p in ps]))
    ppl_uni = float(np.mean([p["ppl_unigram"] for p in ps]))
    ppl_bg = float(np.mean([p["ppl_bigram"] for p in ps]))
    acc_sub = float(np.mean([p["acc_substrate"] for p in ps]))
    acc_uni = float(np.mean([p["acc_unigram"] for p in ps]))
    acc_bg = float(np.mean([p["acc_bigram"] for p in ps]))
    summary = (
        "ppl SUB=%.2f UNI=%.2f BIGRAM=%.2f | acc SUB=%.4f UNI=%.4f BIGRAM=%.4f "
        "(n_seeds=%d, V_DIM=%d, N_TRAIN=%d, N_HELD=%d)"
        % (ppl_sub, ppl_uni, ppl_bg, acc_sub, acc_uni, acc_bg, len(ps), V_DIM, N_TRAIN, N_HELD)
    )
    if ppl_sub <= ppl_bg and acc_sub >= acc_bg:
        return ("HARD_PASS",
                "HARD_PASS: substrate-only LM matches OR beats word-bigram via single NEXT_TOKEN "
                "Hebbian bind (L2 MVP frontier). " + summary)
    if ppl_sub >= ppl_uni:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only LM fails to beat unigram floor; mechanism broken. "
                + summary)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: substrate beats unigram floor but not word-bigram (existing L2 state "
            "with simpler mechanism than VQ-codebook). " + summary)


# ============================================================================
# Main
# ============================================================================

print("[config] anchor=%s mode=%s seeds=%s V_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d"
      % (ANCHOR_NAME, RUN_MODE, SEEDS, V_DIM, N_TRAIN, N_HELD, VOCAB_CAP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
ps: List[Dict] = []
for seed in SEEDS:
    r = run_seed(seed)
    ps.append(r)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "config": {"V_DIM": V_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP},
    "per_seed": ps,
    "elapsed_s": time.time() - t0,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s/metrics.json" % out_dir, flush=True)
