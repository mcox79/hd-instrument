"""text8_substrate_pseudoLM_gpu_v1 -- Path A pseudo-LM at GPU-class scale.

Composes:
  - substrate_as_llm_scaling (1M facts at N=16384 perfect recall; sparse + multiplicative + Hebbian)
  - B2 TinyStories pseudo-LM mechanism (Hebbian-bind word-NEXT_TOKEN pairs; W += outer(E_next, E_prev))

Tests whether the substrate, given LLM-class N (16384) and a real natural-language corpus
(text8 5M token train + 100k held), can act as a pseudo-LM via pure Hebbian-bind word-NEXT_TOKEN
binding and beat / match the word-bigram bar (~3.84 BPC on text8 per L2 MVP frontier).

ARMS (Fix #16 discriminator; 4 arms):
  1. SUBSTRATE_LM_HEBBIAN          -- single NEXT_TOKEN bind W += sum outer(E[w_t+1], E[w_t])
  2. UNIGRAM_BASELINE              -- argmax unigram (CAN-FAIL floor)
  3. WORD_BIGRAM_BASELINE          -- Laplace-smoothed bigram (HARD bar)
  4. SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF -- substrate prediction with bigram-backoff when
                                         substrate confidence below threshold (HYBRID composition arm)

PRE-REG BANDS (preregs/2026-06-22_text8_substrate_pseudoLM_gpu_v1.md):
  HARD_PASS:   ppl(SUBSTRATE) <= ppl(BIGRAM) AND acc(SUBSTRATE) >= acc(BIGRAM)
               OR ppl(BACKOFF) < min(ppl(SUBSTRATE), ppl(BIGRAM)) (composition lift)
               cv across 3 seeds <= 0.10
               n_llm_calls == 0
  HARD_FAIL:   ppl(SUBSTRATE) >= ppl(UNIGRAM)  (fails to improve over unigram)
               OR n_llm_calls > 0
  MIDDLE_BAND: substrate beats unigram but doesn't match bigram (still informative)

ROUTING: overnight_queue (GPU); torch.cuda + batched matmul. PROT-020 passes (imports torch).

GPU MANDATE (Fix #24): nvidia-smi util >= 50% during ingest. W ingest is batched outer-product
accumulation on cuda; recall is one big matmul (Y = E_ctx @ W.T then E_vocab @ Y.T).

ASCII-only. Single-file. Resumable via _seed_checkpoint.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import hashlib
import math
import signal
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "text8_substrate_pseudoLM_gpu_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# Substrate-only-decode gate (asserted == 0 at exit)
_LLM_CALL_COUNTER = [0]

# Pre-reg bands (locked)
HARD_PASS_CV_MAX = 0.10
HARD_FAIL_NEED_BEAT_UNIGRAM = True

_METRICS_WRITTEN = [False]


def _detect_run_mode():
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 4096          # smaller to make smoke fit ~3min cap
    N_TRAIN = 100000      # 100k tokens
    N_HELD = 5000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 8192   # token pairs per outer-product chunk
    RECALL_BATCH = 1024   # held-out queries per substrate matmul batch
    BACKOFF_THRESH = 0.05 # substrate prob mass below this on argmax -> use bigram
else:
    SEEDS = [7, 17, 23]
    N_DIM = 16384
    N_TRAIN = 5_000_000   # 5M tokens
    N_HELD = 100_000
    VOCAB_CAP = 20000     # 20k cap fits 8GB GPU (E = 20k * 16384 * 4 = 1.3GB)
    # INGEST_CHUNK sized to 8GB GPU: W=1.07GB + E=1.31GB + 2*(chunk*N*4) activations
    # At chunk=8192: activations=1.07GB; total=3.5GB. Safe headroom on 8GB GPU.
    # At chunk=32768: activations=4.3GB; OOM observed on RTX 4060 Ti during bench.
    INGEST_CHUNK = 8192
    RECALL_BATCH = 1024   # vocab logits per recall batch (E [V,N] @ pred [b,N].T -> [V,b])
    BACKOFF_THRESH = 0.05

CONFIG_VERSION = (
    "text8-substrate-pseudoLM-gpu-v1: N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "INGEST_CHUNK=%d RECALL_BATCH=%d BACKOFF_THRESH=%.3f run_mode=%s device=%s; "
    "bands HP_cv=%.2f HF_need_beat_unigram=%s"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, INGEST_CHUNK, RECALL_BATCH, BACKOFF_THRESH,
    RUN_MODE, str(DEVICE),
    HARD_PASS_CV_MAX, str(HARD_FAIL_NEED_BEAT_UNIGRAM),
)


# ============================================================================
# Substrate primitives
# ============================================================================

def char_trigram_encode_np(word: str, dim: int, seed: int = 0) -> np.ndarray:
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


def build_encoder_gpu(vocab: List[str], dim: int, seed: int, device: torch.device) -> torch.Tensor:
    """Build (V, dim) row-normalized encoder, returned on `device`."""
    E_np = np.stack([char_trigram_encode_np(w, dim, seed=seed) for w in vocab], 0).astype(np.float32)
    nrm = np.linalg.norm(E_np, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    E_np = E_np / nrm
    return torch.from_numpy(E_np).to(device=device, dtype=TORCH_DTYPE)


def build_hebbian_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
                         ingest_chunk: int) -> torch.Tensor:
    """W = sum_t outer(E[idx[t+1]], E[idx[t]]) on GPU via batched matmul.

    Streams the corpus in chunks of `ingest_chunk` adjacent pairs to keep memory bounded.
    Each chunk: W += E_tgt^T @ E_src  where E_tgt, E_src are [chunk, dim].

    Returns W [dim, dim] on the same device as E.
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]   # [chunk, dim]
        E_tgt = E[tgt_idx]   # [chunk, dim]
        W.add_(E_tgt.T @ E_src)
        # Periodic sync to surface GPU work
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def substrate_predict_batched(W: torch.Tensor, E: torch.Tensor,
                               idx_ctx: torch.Tensor, batch: int
                               ) -> Tuple[torch.Tensor, torch.Tensor]:
    """For each context word, compute logits over the whole vocab.

    Returns:
      argmax_pred: [n_eval] int64 on CPU
      logp_true:   placeholder; per-eval log-probability computed by caller per batch
                   to avoid materializing the full [n_eval, V] logits matrix.

    Implementation streams ctx in batches; per batch computes:
        pred_vec = E[ctx_batch] @ W.T          # [b, dim]
        pred_vec = pred_vec / ||pred_vec||
        logits   = pred_vec @ E.T              # [b, V]
        probs    = softmax(logits / T)
        argmax_b = argmax(logits, dim=1)
    Memory: [batch, V] worst-case. At V=20000 and batch=2048: 160MB peak.
    """
    pass  # placeholder; we compute argmax + per-token logp together in run_seed


def softmax_temperature(logits: torch.Tensor, temperature: float = 0.1) -> torch.Tensor:
    z = logits / max(temperature, 1e-6)
    z = z - z.max(dim=-1, keepdim=True).values
    e = torch.exp(z)
    return e / torch.clamp(e.sum(dim=-1, keepdim=True), min=1e-30)


# ============================================================================
# Baselines: unigram + sparse bigram (CPU; trivial cost)
# ============================================================================

def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def build_sparse_bigram(idx_train: np.ndarray, V: int) -> Tuple[Dict[int, Dict[int, float]],
                                                                  np.ndarray]:
    """Sparse Laplace-smoothed bigram represented as dict-of-dicts + row totals.

    Returns:
      bg_rows:  dict src_idx -> dict tgt_idx -> count
      row_tot:  [V] float64 -- total count per src (excluding alpha smoothing)
    Laplace-smoothing is applied at query time: p(tgt|src) = (count + alpha) / (row_tot + alpha*V)
    """
    bg_rows: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
    row_tot = np.zeros(V, dtype=np.float64)
    src = idx_train[:-1]
    tgt = idx_train[1:]
    for s, t in zip(src, tgt):
        bg_rows[int(s)][int(t)] += 1.0
        row_tot[int(s)] += 1.0
    return bg_rows, row_tot


def bigram_predict_eval(bg_rows: Dict[int, Dict[int, float]], row_tot: np.ndarray,
                        ctx: np.ndarray, true_nxt: np.ndarray, V: int,
                        alpha: float = 0.1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate bigram: returns (argmax, p_true, top1_acc_mask) for each eval position.

    For prediction we need the argmax over V tokens. For a sparse row we still need to find
    the max over the *smoothed* distribution -- when row_tot[s] > 0, smoothing won't change
    the argmax (unless the row is empty). When row_tot[s] == 0, every token has equal smoothed
    prob; we predict 0 (the <unk> sentinel) but it's a tie. We return p_true (probability of the
    correct token) per-position for ppl/BPC.
    """
    n = ctx.shape[0]
    p_true = np.zeros(n, dtype=np.float64)
    argmax = np.zeros(n, dtype=np.int64)
    for i in range(n):
        s = int(ctx[i])
        t = int(true_nxt[i])
        rt = row_tot[s]
        if rt == 0.0:
            # Empty src row; uniform smoothed prob
            p_true[i] = (0.0 + alpha) / (0.0 + alpha * V)
            argmax[i] = 0  # arbitrary
        else:
            row = bg_rows.get(s, {})
            count_t = row.get(t, 0.0)
            denom = rt + alpha * V
            p_true[i] = (count_t + alpha) / denom
            # argmax: token in row with highest (count + alpha); since alpha is constant,
            # max count -> argmax. Fall back to any token if row empty (handled above).
            if row:
                # Find best key
                best_t, best_c = -1, -1.0
                for tt, cc in row.items():
                    if cc > best_c:
                        best_c, best_t = cc, tt
                argmax[i] = best_t
            else:
                argmax[i] = 0
    correct = (argmax == true_nxt).astype(np.int64)
    return argmax, p_true, correct


def bigram_p_target_for_substrate_pred(bg_rows: Dict[int, Dict[int, float]],
                                         row_tot: np.ndarray, ctx: np.ndarray,
                                         pred: np.ndarray, V: int, alpha: float = 0.1
                                         ) -> np.ndarray:
    """For each position, compute the bigram probability of the *predicted* token (used by backoff)."""
    n = ctx.shape[0]
    p = np.zeros(n, dtype=np.float64)
    for i in range(n):
        s = int(ctx[i])
        t = int(pred[i])
        rt = row_tot[s]
        if rt == 0.0:
            p[i] = (0.0 + alpha) / (0.0 + alpha * V)
        else:
            row = bg_rows.get(s, {})
            count_t = row.get(t, 0.0)
            p[i] = (count_t + alpha) / (rt + alpha * V)
    return p


# ============================================================================
# Corpus loader
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


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading corpus + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[FATAL] corpus too small: need %d got %d" % (N_TRAIN + N_HELD, len(toks)),
              flush=True)
        sys.exit(1)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    unk = w2i["<unk>"]
    idx_train_np = tokens_to_idx(train_toks, w2i)
    idx_held_np = tokens_to_idx(held_toks, w2i)

    # held-out eval positions: skip where ctx is unk (substrate has no info)
    ctx_np = idx_held_np[:-1]
    nxt_np = idx_held_np[1:]
    mask = (ctx_np != unk)
    ctx_eval_np = ctx_np[mask]
    nxt_eval_np = nxt_np[mask]
    n_eval = len(ctx_eval_np)
    print("[seed=%d] V=%d train_tok=%d held_tok=%d eval_pos=%d device=%s"
          % (seed, V, N_TRAIN, N_HELD, n_eval, str(DEVICE)), flush=True)

    # GPU encoder + W
    t0 = time.time()
    E = build_encoder_gpu(vocab, N_DIM, seed=seed, device=DEVICE)
    t_enc = time.time() - t0
    print("[seed=%d] encoder built V=%d N_DIM=%d on %s (%.1fs)"
          % (seed, V, N_DIM, str(DEVICE), t_enc), flush=True)

    # Train idx -> GPU
    idx_train = torch.from_numpy(idx_train_np).to(DEVICE)
    ctx_eval = torch.from_numpy(ctx_eval_np).to(DEVICE)

    # --- SUBSTRATE: Hebbian W ingest ---
    t0 = time.time()
    W = build_hebbian_W_gpu(idx_train, E, ingest_chunk=INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0
    print("[seed=%d] SUBSTRATE Hebbian W built n_pairs=%d chunk=%d (%.1fs)"
          % (seed, N_TRAIN - 1, INGEST_CHUNK, t_ingest), flush=True)

    # --- SUBSTRATE: batched recall ---
    t0 = time.time()
    sub_argmax = np.zeros(n_eval, dtype=np.int64)
    sub_logp_true = np.zeros(n_eval, dtype=np.float64)
    sub_p_argmax = np.zeros(n_eval, dtype=np.float64)
    nxt_eval = torch.from_numpy(nxt_eval_np).to(DEVICE)
    for b in range(0, n_eval, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_eval)
        ctx_b = ctx_eval[b:end]
        nxt_b = nxt_eval[b:end]
        pred_vec = E[ctx_b] @ W.T                       # [b, dim]
        pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
        pred_vec = pred_vec / pn
        logits = pred_vec @ E.T                          # [b, V]
        probs = softmax_temperature(logits, temperature=0.1)
        am = probs.argmax(dim=1)                         # [b]
        p_am = probs.gather(1, am.unsqueeze(1)).squeeze(1)
        p_true = probs.gather(1, nxt_b.unsqueeze(1)).squeeze(1).clamp(min=1e-12)
        sub_argmax[b:end] = am.detach().cpu().numpy()
        sub_p_argmax[b:end] = p_am.detach().cpu().numpy()
        sub_logp_true[b:end] = torch.log(p_true).detach().cpu().numpy()
        if DEVICE.type == "cuda" and (b // RECALL_BATCH) % 16 == 0:
            torch.cuda.synchronize()
    t_recall = time.time() - t0
    print("[seed=%d] SUBSTRATE recall done batch=%d (%.1fs)"
          % (seed, RECALL_BATCH, t_recall), flush=True)

    sub_acc = float((sub_argmax == nxt_eval_np).mean())
    sub_nll = float(-np.mean(sub_logp_true))
    sub_ppl = float(np.exp(sub_nll))
    sub_bpc = float(sub_nll / math.log(2.0))
    print("[seed=%d] SUBSTRATE_LM_HEBBIAN    ppl=%.2f bpc=%.3f acc=%.4f"
          % (seed, sub_ppl, sub_bpc, sub_acc), flush=True)

    # --- UNIGRAM (CPU; trivial) ---
    t0 = time.time()
    U = build_unigram_np(idx_train_np, V=V, alpha=0.1)
    uni_argmax_one = int(np.argmax(U))
    uni_argmax = np.full(n_eval, uni_argmax_one, dtype=np.int64)
    p_true_uni = U[nxt_eval_np].clip(1e-12, 1.0)
    uni_nll = float(-np.mean(np.log(p_true_uni)))
    uni_ppl = float(np.exp(uni_nll))
    uni_bpc = float(uni_nll / math.log(2.0))
    uni_acc = float((uni_argmax == nxt_eval_np).mean())
    t_uni = time.time() - t0
    print("[seed=%d] UNIGRAM_BASELINE         ppl=%.2f bpc=%.3f acc=%.4f (%.1fs)"
          % (seed, uni_ppl, uni_bpc, uni_acc, t_uni), flush=True)

    # --- WORD_BIGRAM (CPU; sparse) ---
    t0 = time.time()
    bg_rows, row_tot = build_sparse_bigram(idx_train_np, V=V)
    bg_argmax, bg_p_true, _ = bigram_predict_eval(bg_rows, row_tot, ctx_eval_np,
                                                    nxt_eval_np, V=V, alpha=0.1)
    bg_p_true = bg_p_true.clip(1e-12, 1.0)
    bg_nll = float(-np.mean(np.log(bg_p_true)))
    bg_ppl = float(np.exp(bg_nll))
    bg_bpc = float(bg_nll / math.log(2.0))
    bg_acc = float((bg_argmax == nxt_eval_np).mean())
    t_bg = time.time() - t0
    print("[seed=%d] WORD_BIGRAM_BASELINE     ppl=%.2f bpc=%.3f acc=%.4f (%.1fs)"
          % (seed, bg_ppl, bg_bpc, bg_acc, t_bg), flush=True)

    # --- BACKOFF: substrate prediction when sub_p_argmax >= BACKOFF_THRESH; else bigram ---
    t0 = time.time()
    use_substrate = (sub_p_argmax >= BACKOFF_THRESH)
    backoff_argmax = np.where(use_substrate, sub_argmax, bg_argmax)
    # For p_true under backoff: when substrate is confident, use substrate p_true; else bigram p_true
    backoff_p_true = np.where(use_substrate, np.exp(sub_logp_true), bg_p_true).clip(1e-12, 1.0)
    backoff_nll = float(-np.mean(np.log(backoff_p_true)))
    backoff_ppl = float(np.exp(backoff_nll))
    backoff_bpc = float(backoff_nll / math.log(2.0))
    backoff_acc = float((backoff_argmax == nxt_eval_np).mean())
    backoff_frac_substrate = float(use_substrate.mean())
    t_back = time.time() - t0
    print("[seed=%d] BACKOFF                  ppl=%.2f bpc=%.3f acc=%.4f frac_sub=%.3f (%.1fs)"
          % (seed, backoff_ppl, backoff_bpc, backoff_acc, backoff_frac_substrate, t_back),
          flush=True)

    # Per-unit: one entry per (seed, arm)
    per_unit = [
        {"arm": "SUBSTRATE_LM_HEBBIAN",          "ppl": sub_ppl,     "bpc": sub_bpc,
         "acc": sub_acc,      "wall_s": float(t_ingest + t_recall)},
        {"arm": "UNIGRAM_BASELINE",              "ppl": uni_ppl,     "bpc": uni_bpc,
         "acc": uni_acc,      "wall_s": float(t_uni)},
        {"arm": "WORD_BIGRAM_BASELINE",          "ppl": bg_ppl,      "bpc": bg_bpc,
         "acc": bg_acc,       "wall_s": float(t_bg)},
        {"arm": "SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF","ppl": backoff_ppl,"bpc": backoff_bpc,
         "acc": backoff_acc,  "wall_s": float(t_back), "frac_substrate": backoff_frac_substrate},
    ]

    # Free GPU memory
    del W, E, idx_train, ctx_eval, nxt_eval
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "V": V,
        "N": N_DIM,
        "M": N_TRAIN,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "n_eval": n_eval,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "ppl_substrate": sub_ppl,
        "ppl_unigram": uni_ppl,
        "ppl_bigram": bg_ppl,
        "ppl_backoff": backoff_ppl,
        "bpc_substrate": sub_bpc,
        "bpc_unigram": uni_bpc,
        "bpc_bigram": bg_bpc,
        "bpc_backoff": backoff_bpc,
        "acc_substrate": sub_acc,
        "acc_unigram": uni_acc,
        "acc_bigram": bg_acc,
        "acc_backoff": backoff_acc,
        "backoff_frac_substrate": backoff_frac_substrate,
        "elapsed_s": float(time.time() - t_seed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "wall_ingest_s": float(t_ingest),
        "wall_recall_s": float(t_recall),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    sub_bpcs = [b.get("bpc_substrate", float("nan")) for b in per_seed.values()]
    uni_bpcs = [b.get("bpc_unigram", float("nan")) for b in per_seed.values()]
    bg_bpcs = [b.get("bpc_bigram", float("nan")) for b in per_seed.values()]
    back_bpcs = [b.get("bpc_backoff", float("nan")) for b in per_seed.values()]

    sub_accs = [b.get("acc_substrate", 0.0) for b in per_seed.values()]
    bg_accs = [b.get("acc_bigram", 0.0) for b in per_seed.values()]

    mean = lambda xs: float(np.mean(xs)) if xs else float("nan")
    std = lambda xs: float(np.std(xs)) if xs else float("nan")
    cv = lambda xs: (std(xs) / max(mean(xs), 1e-9)) if xs else float("inf")

    sub_bpc_m, uni_bpc_m, bg_bpc_m, back_bpc_m = mean(sub_bpcs), mean(uni_bpcs), mean(bg_bpcs), mean(back_bpcs)
    sub_acc_m, bg_acc_m = mean(sub_accs), mean(bg_accs)
    sub_cv = cv(sub_bpcs)

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "mean_bpc_substrate": sub_bpc_m,
        "mean_bpc_unigram": uni_bpc_m,
        "mean_bpc_bigram": bg_bpc_m,
        "mean_bpc_backoff": back_bpc_m,
        "cv_bpc_substrate": sub_cv,
        "mean_acc_substrate": sub_acc_m,
        "mean_acc_bigram": bg_acc_m,
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "Path A pseudo-LM at GPU-class scale. text8 corpus, N_TRAIN=%d N_HELD=%d "
            "VOCAB_CAP=%d N_DIM=%d. 4-arm discriminator: SUBSTRATE_LM_HEBBIAN vs "
            "UNIGRAM_BASELINE (CAN-FAIL floor) vs WORD_BIGRAM_BASELINE (HARD bar) vs "
            "SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF (composition arm). Pure Hebbian W += "
            "sum outer(E[w_t+1], E[w_t]); single NEXT_TOKEN relation; substrate-only-decode "
            "(n_llm=%d). Composes substrate_as_llm_scaling capacity finding + B2 TinyStories "
            "mechanism. text8 word-bigram bar ~3.84 BPC (L2 MVP frontier reference)."
            % (N_TRAIN, N_HELD, VOCAB_CAP, N_DIM, n_llm)),
    }

    summary = (
        "BPC sub=%.3f uni=%.3f bigram=%.3f backoff=%.3f | acc sub=%.4f bigram=%.4f | "
        "cv_sub=%.3f n_llm=%d (n_seeds=%d, V_DIM=%d, N_TRAIN=%d, N_HELD=%d)"
        % (sub_bpc_m, uni_bpc_m, bg_bpc_m, back_bpc_m, sub_acc_m, bg_acc_m,
           sub_cv, n_llm, len(per_seed), N_DIM, N_TRAIN, N_HELD)
    )

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)

    # HARD_FAIL: substrate fails to beat unigram floor
    if HARD_FAIL_NEED_BEAT_UNIGRAM and (math.isnan(sub_bpc_m) or sub_bpc_m >= uni_bpc_m):
        return ("HARD_FAIL",
                "HARD_FAIL: substrate BPC %.3f >= unigram BPC %.3f; fails to improve over unigram. %s"
                % (sub_bpc_m, uni_bpc_m, summary), detail)

    # HARD_PASS check
    substrate_matches_bigram = (sub_bpc_m <= bg_bpc_m and sub_acc_m >= bg_acc_m)
    composition_lift = (back_bpc_m < min(sub_bpc_m, bg_bpc_m))
    cv_ok = (sub_cv <= HARD_PASS_CV_MAX)

    if cv_ok and (substrate_matches_bigram or composition_lift):
        if substrate_matches_bigram and composition_lift:
            note = "substrate matches bigram AND composition arm lifts further"
        elif substrate_matches_bigram:
            note = "substrate matches bigram via pure Hebbian-bind (L2 MVP frontier achieved)"
        else:
            note = "composition arm lifts above both parents (HYBRID composition demonstrated)"
        return ("HARD_PASS",
                "HARD_PASS: %s. cv=%.3f <= %.2f, n_llm=0. %s"
                % (note, sub_cv, HARD_PASS_CV_MAX, summary), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: substrate beats unigram (%.3f < %.3f bpc) but does not match bigram (%.3f); "
            "no composition lift (back=%.3f). %s"
            % (sub_bpc_m, uni_bpc_m, bg_bpc_m, back_bpc_m, summary), detail)


# ============================================================================
# Self-tests
# ============================================================================

def _selftest():
    # 1. encoder deterministic
    a1 = char_trigram_encode_np("hello", 256, seed=42)
    a2 = char_trigram_encode_np("hello", 256, seed=42)
    assert np.allclose(a1, a2), "selftest 1: encoder not deterministic"

    # 2. build_encoder_gpu shape + normalization
    vocab = ["a", "b", "c", "d", "e"]
    E = build_encoder_gpu(vocab, 256, seed=0, device=torch.device("cpu"))
    assert E.shape == (5, 256), "selftest 2: encoder shape %s != (5, 256)" % (E.shape,)
    nrms = E.norm(dim=1).numpy()
    assert np.allclose(nrms, 1.0, atol=1e-5), "selftest 2: rows not unit norm: %s" % nrms

    # 3. Hebbian W on tiny corpus + perfect-recall control
    cycle_vocab = ["tok%d" % i for i in range(10)]
    Ec = build_encoder_gpu(cycle_vocab, 1024, seed=0, device=torch.device("cpu"))
    seq = np.tile(np.arange(10), 5).astype(np.int64)  # 5 cycles
    seq_t = torch.from_numpy(seq)
    Wc = build_hebbian_W_gpu(seq_t, Ec, ingest_chunk=8)
    # Predict argmax for each ctx and verify high top-1 accuracy
    ctx_t = seq_t[:-1]
    pred_vec = Ec[ctx_t] @ Wc.T
    pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
    pred_vec = pred_vec / pn
    logits = pred_vec @ Ec.T
    am = logits.argmax(dim=1).numpy()
    acc = float((am == seq[1:]).mean())
    assert acc >= 0.7, "selftest 3: perfect-recall control acc=%.3f < 0.7" % acc

    # 4. order-sensitive: a->b vs b->a produce different W
    Ev = build_encoder_gpu(["a", "b", "c", "d"], 256, seed=0, device=torch.device("cpu"))
    idx_ab = torch.tensor([0, 1, 2, 3], dtype=torch.int64)
    idx_ba = torch.tensor([3, 2, 1, 0], dtype=torch.int64)
    W_ab = build_hebbian_W_gpu(idx_ab, Ev, ingest_chunk=8)
    W_ba = build_hebbian_W_gpu(idx_ba, Ev, ingest_chunk=8)
    diff = (W_ab - W_ba).norm().item()
    assert diff > 0.1, "selftest 4: bind not order-sensitive (diff=%.3f)" % diff

    # 5. unigram matches analytic max-class freq
    idx = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)  # max-class=2 freq=0.4
    U = build_unigram_np(idx, V=4, alpha=0.0)
    assert int(np.argmax(U)) == 2, "selftest 5: unigram argmax %d != 2" % int(np.argmax(U))

    # 6. sparse bigram: corpus "a b a b a b" -> P(b|a)=1, P(a|b)=1; ppl on held "a b a" ~ 1
    train = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    bg, rt = build_sparse_bigram(train, V=2)
    ctx_t = np.array([0, 1], dtype=np.int64)
    true_t = np.array([1, 0], dtype=np.int64)
    _, p_true, _ = bigram_predict_eval(bg, rt, ctx_t, true_t, V=2, alpha=1e-9)
    ppl = float(np.exp(-np.mean(np.log(np.clip(p_true, 1e-12, 1.0)))))
    assert abs(ppl - 1.0) < 0.01, "selftest 6: bigram ppl %.4f != 1.0" % ppl

    # 7. substrate-only-decode counter
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 7: LLM counter non-zero"

    print("[selftest] PASS: encoder gpu/det/norm, cycle-recall, order-sensitive, unigram, "
          "sparse-bigram, llm=0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- atexit synthesizer -----
def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        verdict, verdict_msg, detail = compute_verdict(per_seed)
        verdict_msg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + verdict_msg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "config_version": CONFIG_VERSION,
            "allow_synthetic": False,
            "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
                 "per_unit": v.get("per_unit", [])}
                for k, v in per_seed.items()
            ],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": verdict_msg[:200],
            "synthesized_at_exit": True,
            "elapsed_s": 0.0,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partials" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAILED to synthesize: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# ----- Main runner -----
out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_TRAIN=%d VOCAB_CAP=%d INGEST_CHUNK=%d device=%s seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, N_TRAIN, VOCAB_CAP, INGEST_CHUNK, str(DEVICE),
         str(done), str(seeds_todo)), flush=True)

if DEVICE.type == "cuda":
    try:
        print("[gpu] device=%s name=%s total_mem_gb=%.2f"
              % (DEVICE, torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
    except Exception as e:
        print("[gpu] info-fetch failed: %s" % e, flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "INGEST_CHUNK": INGEST_CHUNK,
    "RECALL_BATCH": RECALL_BATCH,
    "BACKOFF_THRESH": BACKOFF_THRESH,
    "arms": ["SUBSTRATE_LM_HEBBIAN", "UNIGRAM_BASELINE", "WORD_BIGRAM_BASELINE",
             "SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF"],
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "config_version": CONFIG_VERSION,
    "allow_synthetic": False,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_text8_substrate_pseudoLM_gpu_4arm",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
