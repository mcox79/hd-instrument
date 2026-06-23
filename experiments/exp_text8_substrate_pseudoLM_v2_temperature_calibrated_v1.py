"""text8_substrate_pseudoLM_v2_temperature_calibrated_v1 -- REVIVAL of v1 HARD_FAIL.

REVIVAL of text8_substrate_pseudoLM_gpu_v1 (2026-06-22):
- v1 substrate BPC 9.371 vs unigram BPC 8.024 (substrate WORSE).
- BUT v1 substrate top-1 acc 0.198 ~ bigram acc 0.213 (competitive).
- Calibration problem, NOT mechanism failure: Hebbian outer-product produces
  single-spike distributions with low mass on the correct token when top-1 wrong.

Revival hypothesis (per `notes/research_2x_revival_overnight_negatives_2026-06-23.md`):
  Lit (Stolcke 1998 log-linear interp; Guo 2017 temperature scaling) gives
  standard calibration fixes. v1 backoff used HARD threshold (substrate prob < 0.05);
  log-linear interp is the standard.

DESIGN (3 arms x temperature/lambda sweeps x 3 seeds at N_DIM=4096, N_TRAIN=100k, V=4000):
  ARM SUBSTRATE_HEBBIAN_BPC_RAW    : control (= v1 SUBSTRATE_LM_HEBBIAN at this scale).
  ARM SUBSTRATE_HEBBIAN_TEMP_CALIBRATED:
       sweep T in {0.5, 1.0, 2.0, 5.0} on the substrate logits per-batch;
       report best-T BPC on held-out (calibration tuned on first 1/2 of held; eval on 2nd 1/2).
  ARM SUBSTRATE_LOG_LINEAR_UNIGRAM :
       p_combined = exp(lambda * log P_sub + (1-lambda) * log P_uni) / Z
       sweep lambda in {0.1, 0.3, 0.5, 0.7}; report best-lambda BPC (tuned on dev split).

PRE-REG HARD bands (verbatim from handoff):
  HARD_PASS: best calibrated arm BPC <= 7.5 AND cv across seeds <= 0.10.
  HARD_FAIL: best calibrated arm BPC >= 8.024 (no calibration arm beats unigram).
  MIDDLE_BAND: best calibrated arm BPC in (7.5, 8.024) (improvement but below target).

PROT-020 passes (imports torch).
Fix #24 GPU dispatch: uses torch.cuda + batched matmul + GPU encoder hoist.

ASCII-only. Per-seed checkpoint. atexit synthesizer.
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

ANCHOR_NAME = "text8_substrate_pseudoLM_v2_temperature_calibrated_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

_LLM_CALL_COUNTER = [0]
HARD_PASS_BPC = 7.5
HARD_FAIL_BPC = 8.024  # unigram baseline reported in v1 metrics
HARD_PASS_CV_MAX = 0.10
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

# Config per RUN_MODE
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 4096
    N_TRAIN = 100_000
    N_HELD = 5_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 8192
    RECALL_BATCH = 1024
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_TRAIN = 100_000
    N_HELD = 20_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 8192
    RECALL_BATCH = 1024

TEMP_GRID = [0.5, 1.0, 2.0, 5.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  # 1.0 = pure substrate (calibration check)

CONFIG_VERSION = (
    "text8-substrate-pseudoLM-v2-temperature-calibrated-v1: N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d INGEST_CHUNK=%d RECALL_BATCH=%d temp_grid=%s lambda_grid=%s run_mode=%s "
    "device=%s; bands HP_BPC<=%.2f HF_BPC>=%.3f cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, INGEST_CHUNK, RECALL_BATCH,
    TEMP_GRID, LAMBDA_GRID, RUN_MODE, str(DEVICE),
    HARD_PASS_BPC, HARD_FAIL_BPC, HARD_PASS_CV_MAX,
)


# ============================================================================
# Substrate primitives (mirror v1)
# ============================================================================

def char_trigram_encode_np(word: str, dim: int, seed: int = 0) -> np.ndarray:
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


def build_encoder_gpu(vocab: List[str], dim: int, seed: int, device) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode_np(w, dim, seed=seed) for w in vocab], 0).astype(np.float32)
    nrm = np.linalg.norm(E_np, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    E_np = E_np / nrm
    return torch.from_numpy(E_np).to(device=device, dtype=TORCH_DTYPE)


def build_hebbian_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
                         ingest_chunk: int) -> torch.Tensor:
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def softmax_with_temperature(logits, temperature):
    z = logits / max(temperature, 1e-6)
    z = z - z.max(dim=-1, keepdim=True).values
    e = torch.exp(z)
    return e / torch.clamp(e.sum(dim=-1, keepdim=True), min=1e-30)


# ============================================================================
# Unigram baseline (numpy; trivial)
# ============================================================================

def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


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
# Per-seed runner: substrate, temp-calibrated, log-linear interp arms
# ============================================================================

def run_seed(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading corpus + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[FATAL] corpus too small: need %d got %d" % (N_TRAIN + N_HELD, len(toks)), flush=True)
        sys.exit(1)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    unk = w2i["<unk>"]
    idx_train_np = tokens_to_idx(train_toks, w2i)
    idx_held_np = tokens_to_idx(held_toks, w2i)
    ctx_np = idx_held_np[:-1]
    nxt_np = idx_held_np[1:]
    mask = (ctx_np != unk)
    ctx_eval_np = ctx_np[mask]
    nxt_eval_np = nxt_np[mask]
    n_eval = len(ctx_eval_np)
    print("[seed=%d] V=%d train_tok=%d held_tok=%d eval_pos=%d device=%s" % (seed, V, N_TRAIN, N_HELD, n_eval, str(DEVICE)), flush=True)

    # Split held into dev (first half; for temp/lambda tuning) and test (second half)
    n_dev = n_eval // 2
    ctx_dev_np = ctx_eval_np[:n_dev]
    nxt_dev_np = nxt_eval_np[:n_dev]
    ctx_test_np = ctx_eval_np[n_dev:]
    nxt_test_np = nxt_eval_np[n_dev:]
    n_test = len(ctx_test_np)
    print("[seed=%d] split held: dev=%d test=%d" % (seed, n_dev, n_test), flush=True)

    # GPU encoder + W
    t0 = time.time()
    E = build_encoder_gpu(vocab, N_DIM, seed=seed, device=DEVICE)
    t_enc = time.time() - t0
    print("[seed=%d] encoder built V=%d N_DIM=%d on %s (%.1fs)" % (seed, V, N_DIM, str(DEVICE), t_enc), flush=True)

    idx_train = torch.from_numpy(idx_train_np).to(DEVICE)
    t0 = time.time()
    W = build_hebbian_W_gpu(idx_train, E, ingest_chunk=INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0
    print("[seed=%d] SUBSTRATE Hebbian W built n_pairs=%d chunk=%d (%.1fs)" % (seed, N_TRAIN - 1, INGEST_CHUNK, t_ingest), flush=True)

    # Unigram baseline
    U = build_unigram_np(idx_train_np, V=V, alpha=0.1)
    U_log = np.log(U.clip(1e-30, 1.0))

    # Compute per-position substrate logits (full vocab) on dev + test
    # We accumulate substrate log-probs at each (context_idx, vocab_idx) -- shape [n_eval, V]
    # That's memory-heavy: at V=4000, n_eval=10k -> 40M floats = 160MB; acceptable.
    # Then we apply temp/lambda combinations IN MEMORY (post-hoc; cheap).

    def compute_substrate_logits(ctx_np_local):
        n = len(ctx_np_local)
        logits_out = np.zeros((n, V), dtype=np.float32)
        ctx_t = torch.from_numpy(ctx_np_local).to(DEVICE)
        for b in range(0, n, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n)
            ctx_b = ctx_t[b:end]
            pred_vec = E[ctx_b] @ W.T
            pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
            pred_vec = pred_vec / pn
            logits_b = pred_vec @ E.T  # [b, V]
            logits_out[b:end] = logits_b.detach().cpu().numpy()
            if DEVICE.type == "cuda" and (b // RECALL_BATCH) % 16 == 0:
                torch.cuda.synchronize()
        return logits_out

    t0 = time.time()
    sub_logits_dev = compute_substrate_logits(ctx_dev_np)
    sub_logits_test = compute_substrate_logits(ctx_test_np)
    t_recall = time.time() - t0
    print("[seed=%d] substrate logits computed dev+test (%.1fs)" % (seed, t_recall), flush=True)

    # ARM 1: SUBSTRATE_HEBBIAN_BPC_RAW (= v1 reference at T=0.1; control)
    # Note v1 used T=0.1 hard-coded. We use T=1.0 here as the "raw" baseline (no temp scaling).
    def bpc_at_temp(logits, nxt, temp):
        # numpy softmax with temperature
        z = logits / max(temp, 1e-6)
        z = z - z.max(axis=1, keepdims=True)
        e = np.exp(z.astype(np.float64))
        probs = e / (e.sum(axis=1, keepdims=True) + 1e-30)
        p_true = np.clip(probs[np.arange(len(nxt)), nxt], 1e-12, 1.0)
        nll = float(-np.mean(np.log(p_true)))
        bpc = nll / math.log(2.0)
        argmax = probs.argmax(axis=1)
        acc = float((argmax == nxt).mean())
        return bpc, acc, probs

    raw_bpc, raw_acc, _ = bpc_at_temp(sub_logits_test, nxt_test_np, temp=1.0)
    print("[seed=%d] RAW (T=1.0) test bpc=%.3f acc=%.4f" % (seed, raw_bpc, raw_acc), flush=True)

    # ARM 2: SUBSTRATE_HEBBIAN_TEMP_CALIBRATED -- sweep T on dev, pick best, report test
    temp_dev = {}
    for T in TEMP_GRID:
        b, a, _ = bpc_at_temp(sub_logits_dev, nxt_dev_np, T)
        temp_dev[T] = b
    best_T = min(temp_dev, key=lambda t: temp_dev[t])
    temp_test_bpc, temp_test_acc, sub_probs_test_calibrated = bpc_at_temp(sub_logits_test, nxt_test_np, best_T)
    print("[seed=%d] TEMP_CALIBRATED best_T=%.2f (dev bpc=%.3f) -> test bpc=%.3f acc=%.4f" % (
        seed, best_T, temp_dev[best_T], temp_test_bpc, temp_test_acc), flush=True)

    # ARM 3: SUBSTRATE_LOG_LINEAR_UNIGRAM
    # p_combined(t) propto exp(lambda * log p_sub + (1-lambda) * log p_uni)
    # Renormalize per-position. Sweep lambda on dev, report test for best.
    def log_linear_bpc(sub_probs, nxt, lam, U_log_local):
        sub_logp = np.log(np.clip(sub_probs, 1e-30, 1.0))
        combined_logits = lam * sub_logp + (1.0 - lam) * U_log_local[None, :]
        z = combined_logits - combined_logits.max(axis=1, keepdims=True)
        e = np.exp(z.astype(np.float64))
        probs = e / (e.sum(axis=1, keepdims=True) + 1e-30)
        p_true = np.clip(probs[np.arange(len(nxt)), nxt], 1e-12, 1.0)
        nll = float(-np.mean(np.log(p_true)))
        bpc = nll / math.log(2.0)
        argmax = probs.argmax(axis=1)
        acc = float((argmax == nxt).mean())
        return bpc, acc

    # Substrate probs at T=1.0 for log-linear interp (separate from temp arm)
    _, _, sub_probs_dev_raw = bpc_at_temp(sub_logits_dev, nxt_dev_np, temp=1.0)
    _, _, sub_probs_test_raw = bpc_at_temp(sub_logits_test, nxt_test_np, temp=1.0)

    log_linear_dev = {}
    for lam in LAMBDA_GRID:
        b, _ = log_linear_bpc(sub_probs_dev_raw, nxt_dev_np, lam, U_log)
        log_linear_dev[lam] = b
    best_lam = min(log_linear_dev, key=lambda l: log_linear_dev[l])
    ll_test_bpc, ll_test_acc = log_linear_bpc(sub_probs_test_raw, nxt_test_np, best_lam, U_log)
    print("[seed=%d] LOG_LINEAR best_lambda=%.2f (dev bpc=%.3f) -> test bpc=%.3f acc=%.4f" % (
        seed, best_lam, log_linear_dev[best_lam], ll_test_bpc, ll_test_acc), flush=True)

    # Unigram-only baseline on test
    p_true_uni = U[nxt_test_np].clip(1e-12, 1.0)
    uni_nll = float(-np.mean(np.log(p_true_uni)))
    uni_bpc = uni_nll / math.log(2.0)
    uni_argmax = int(np.argmax(U))
    uni_acc = float((np.full(n_test, uni_argmax) == nxt_test_np).mean())
    print("[seed=%d] UNIGRAM test bpc=%.3f acc=%.4f" % (seed, uni_bpc, uni_acc), flush=True)

    # Free GPU
    del W, E, idx_train
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
        "n_dev": n_dev,
        "n_test": n_test,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "raw_bpc": raw_bpc,
        "raw_acc": raw_acc,
        "best_T": best_T,
        "temp_dev_bpc": temp_dev,
        "temp_test_bpc": temp_test_bpc,
        "temp_test_acc": temp_test_acc,
        "best_lambda": best_lam,
        "log_linear_dev_bpc": log_linear_dev,
        "log_linear_test_bpc": ll_test_bpc,
        "log_linear_test_acc": ll_test_acc,
        "unigram_test_bpc": uni_bpc,
        "unigram_test_acc": uni_acc,
        "per_unit": [
            {"arm": "SUBSTRATE_HEBBIAN_BPC_RAW",        "bpc": raw_bpc,        "acc": raw_acc},
            {"arm": "SUBSTRATE_HEBBIAN_TEMP_CALIBRATED", "bpc": temp_test_bpc,  "acc": temp_test_acc, "best_T": best_T},
            {"arm": "SUBSTRATE_LOG_LINEAR_UNIGRAM",     "bpc": ll_test_bpc,    "acc": ll_test_acc, "best_lambda": best_lam},
            {"arm": "UNIGRAM_BASELINE",                  "bpc": uni_bpc,        "acc": uni_acc},
        ],
        "elapsed_s": float(time.time() - t_seed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "wall_ingest_s": float(t_ingest),
        "wall_recall_s": float(t_recall),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(per_seed) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})
    raw_bpcs = [b.get("raw_bpc", float("nan")) for b in per_seed.values()]
    temp_bpcs = [b.get("temp_test_bpc", float("nan")) for b in per_seed.values()]
    ll_bpcs = [b.get("log_linear_test_bpc", float("nan")) for b in per_seed.values()]
    uni_bpcs = [b.get("unigram_test_bpc", float("nan")) for b in per_seed.values()]

    mean = lambda xs: float(np.mean(xs)) if xs else float("nan")
    std = lambda xs: float(np.std(xs)) if xs else float("nan")
    cv = lambda xs: (std(xs) / max(mean(xs), 1e-9)) if xs else float("inf")

    raw_m = mean(raw_bpcs)
    temp_m = mean(temp_bpcs)
    ll_m = mean(ll_bpcs)
    uni_m = mean(uni_bpcs)

    # Best calibrated arm = min(temp_m, ll_m)
    if temp_m <= ll_m:
        best_arm = "SUBSTRATE_HEBBIAN_TEMP_CALIBRATED"
        best_bpc = temp_m
        best_cv = cv(temp_bpcs)
    else:
        best_arm = "SUBSTRATE_LOG_LINEAR_UNIGRAM"
        best_bpc = ll_m
        best_cv = cv(ll_bpcs)

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "mean_raw_bpc": raw_m,
        "mean_temp_calibrated_bpc": temp_m,
        "mean_log_linear_bpc": ll_m,
        "mean_unigram_bpc": uni_m,
        "best_calibrated_arm": best_arm,
        "best_calibrated_bpc": best_bpc,
        "best_calibrated_cv": best_cv,
        "cv_raw": cv(raw_bpcs),
        "cv_temp": cv(temp_bpcs),
        "cv_log_linear": cv(ll_bpcs),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "Calibration REVIVAL of v1 HARD_FAIL. text8 N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
            "N_DIM=%d. 3 calibration arms vs unigram baseline. Held split into dev/test; "
            "best T and best lambda chosen on dev, BPC reported on test." % (
                N_TRAIN, N_HELD, VOCAB_CAP, N_DIM)),
    }

    summary = (
        "BPC raw=%.3f temp_calibrated=%.3f log_linear=%.3f unigram=%.3f | best=%s bpc=%.3f cv=%.3f n_llm=%d "
        "(n_seeds=%d V_DIM=%d N_TRAIN=%d)"
        % (raw_m, temp_m, ll_m, uni_m, best_arm, best_bpc, best_cv, n_llm,
           len(per_seed), N_DIM, N_TRAIN)
    )

    if not substrate_only_ok:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary), detail)

    cv_ok = (best_cv <= HARD_PASS_CV_MAX)

    if best_bpc <= HARD_PASS_BPC and cv_ok:
        return ("HARD_PASS",
                "HARD_PASS: calibrated substrate %s BPC %.3f <= %.2f bar; cv=%.3f. Calibration "
                "revival succeeded; substrate pseudo-LM viable. %s" % (
                    best_arm, best_bpc, HARD_PASS_BPC, best_cv, summary), detail)
    if best_bpc >= HARD_FAIL_BPC:
        return ("HARD_FAIL",
                "HARD_FAIL: best calibrated arm BPC %.3f >= unigram BPC %.3f; "
                "no calibration beats unigram. Mechanism truly rejected. %s" % (
                    best_bpc, HARD_FAIL_BPC, summary), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: best calibrated BPC %.3f in (%.2f, %.3f) -- improvement but below "
            "HARD_PASS bar. %s" % (best_bpc, HARD_PASS_BPC, HARD_FAIL_BPC, summary), detail)


# ============================================================================
# Self-tests (handoff: lambda=1.0 LOG_LINEAR reproduces HEBBIAN_RAW; lambda=0.0 reproduces UNIGRAM)
# ============================================================================

def _selftest():
    # 1. encoder deterministic
    a1 = char_trigram_encode_np("hello", 256, seed=42)
    a2 = char_trigram_encode_np("hello", 256, seed=42)
    assert np.allclose(a1, a2), "selftest 1: encoder not deterministic"
    # 2. encoder norm
    vocab_t = ["a", "b", "c", "d", "e"]
    E = build_encoder_gpu(vocab_t, 256, seed=0, device=torch.device("cpu"))
    assert E.shape == (5, 256)
    nrms = E.norm(dim=1).numpy()
    assert np.allclose(nrms, 1.0, atol=1e-5)
    # 3. Hebbian recall (cycle corpus)
    cycle_vocab = ["tok%d" % i for i in range(10)]
    Ec = build_encoder_gpu(cycle_vocab, 1024, seed=0, device=torch.device("cpu"))
    seq = np.tile(np.arange(10), 5).astype(np.int64)
    seq_t = torch.from_numpy(seq)
    Wc = build_hebbian_W_gpu(seq_t, Ec, ingest_chunk=8)
    ctx_t = seq_t[:-1]
    pred_vec = Ec[ctx_t] @ Wc.T
    pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
    pred_vec = pred_vec / pn
    logits = pred_vec @ Ec.T
    am = logits.argmax(dim=1).numpy()
    acc = float((am == seq[1:]).mean())
    assert acc >= 0.7, "selftest 3: cycle-recall acc=%.3f < 0.7" % acc
    # 4. log-linear endpoint check (handoff selftest):
    #    at lambda=1.0 LOG_LINEAR should reproduce substrate (HEBBIAN_RAW); at lambda=0.0 reproduce UNIGRAM
    V = 5
    n = 4
    sub_probs = np.array([
        [0.6, 0.1, 0.1, 0.1, 0.1],
        [0.1, 0.5, 0.2, 0.1, 0.1],
        [0.3, 0.3, 0.2, 0.1, 0.1],
        [0.1, 0.1, 0.1, 0.5, 0.2],
    ], dtype=np.float64)
    nxt = np.array([0, 1, 1, 3], dtype=np.int64)
    U_log = np.log(np.array([0.2, 0.3, 0.2, 0.2, 0.1]).clip(1e-30, 1.0))
    # lambda=1.0 -> log-linear should approx substrate (after renorm, identical)
    sub_logp = np.log(sub_probs.clip(1e-30, 1.0))
    combined_logits_lam1 = 1.0 * sub_logp + 0.0 * U_log[None, :]
    z = combined_logits_lam1 - combined_logits_lam1.max(axis=1, keepdims=True)
    e = np.exp(z)
    probs_lam1 = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    assert np.allclose(probs_lam1, sub_probs, atol=1e-6), "selftest 4: lambda=1.0 != substrate; got %s" % probs_lam1
    # lambda=0.0 -> should be uniform over vocab (because U_log * 1.0 -> softmax(U_log) = U)
    combined_logits_lam0 = 0.0 * sub_logp + 1.0 * U_log[None, :]
    z0 = combined_logits_lam0 - combined_logits_lam0.max(axis=1, keepdims=True)
    e0 = np.exp(z0)
    probs_lam0 = e0 / (e0.sum(axis=1, keepdims=True) + 1e-30)
    U_target = np.exp(U_log - U_log.max())
    U_target = U_target / U_target.sum()
    # each row should equal U
    for i in range(n):
        assert np.allclose(probs_lam0[i], U_target, atol=1e-6), "selftest 4: lambda=0.0 != unigram; row %d got %s" % (i, probs_lam0[i])
    # 5. unigram analytic max-class
    idx = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)
    U = build_unigram_np(idx, V=4, alpha=0.0)
    assert int(np.argmax(U)) == 2
    # 6. counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 6: LLM counter non-zero"
    print("[selftest] PASS: encoder, cycle-recall, log-linear-endpoints (lambda=1.0=substrate, lambda=0.0=unigram), unigram, llm=0", flush=True)


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
        v, vmsg, detail = compute_verdict(per_seed)
        vmsg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + vmsg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": v,
            "verdict_msg": vmsg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "config_version": CONFIG_VERSION,
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [{"seed": k, **{kk: vv for kk, vv in v_.items() if kk != "per_unit"},
                          "per_unit": v_.get("per_unit", [])} for k, v_ in per_seed.items()],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": vmsg[:200],
            "synthesized_at_exit": True,
            "elapsed_s": 0.0,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
    except Exception as e:
        print("[atexit] FAILED: %s" % e, flush=True)


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
print("[run] mode=%s N_DIM=%d N_TRAIN=%d VOCAB_CAP=%d device=%s seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, N_TRAIN, VOCAB_CAP, str(DEVICE), str(done), str(seeds_todo)), flush=True)
if DEVICE.type == "cuda":
    try:
        print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (DEVICE, torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
    except Exception as e:
        print("[gpu] info-fetch failed: %s" % e, flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
v, vmsg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "INGEST_CHUNK": INGEST_CHUNK,
    "RECALL_BATCH": RECALL_BATCH,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "arms": ["SUBSTRATE_HEBBIAN_BPC_RAW", "SUBSTRATE_HEBBIAN_TEMP_CALIBRATED", "SUBSTRATE_LOG_LINEAR_UNIGRAM", "UNIGRAM_BASELINE"],
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "config_version": CONFIG_VERSION,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [{"seed": k, **{kk: vv for kk, vv in vv_.items() if kk != "per_unit"},
                  "per_unit": vv_.get("per_unit", [])} for k, vv_ in per_seed.items()],
    "metrics_source": "measured_text8_substrate_pseudoLM_v2_calibrated",
    "elapsed_s": time.time() - t0_total,
    "summary": vmsg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % v, flush=True)
print("[VERDICT_MSG] %s" % vmsg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
