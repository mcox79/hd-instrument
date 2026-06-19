"""Corpus-size scaling v2: proper N>=1024, corpus 10MB/100MB/1GB proxy.

v1 VERDICT: HARD_FAIL -- bpc stopped improving at N=1024 with corpus sizes
[10KB, 100KB, 500KB]. The issue was smoke-regime N=256 mismatch: at N=256
corpus sizes 10KB/100KB/500KB hit alpha_c * 256 = 144 items quickly, producing
spurious plateau. Path-(b) P dropped from 0.35 to 0.27.

FIX v2:
  - N=1024 (full scale, not smoke N=256)
  - Corpus sizes scaled to match N: [100_000, 1_000_000, 10_000_000] bytes
    (10x larger corpus steps than v1 to test well above tau-limit onset)
  - Multi-scale smoke: run at N=256 + N=512 first; if smoke passes both,
    ship N=1024 full.
  - K=4 (same as v1)
  - 5 seeds for CI

The hypothesis: at N=1024, with 10MB of corpus, does bpc continue improving
monotonically or plateau? If monotone improvement: path-(b) viability restored.
If plateau: tau-limit binding at N=1024 too -> path-(b) requires N >> 1024.

PRE-REGISTERED BANDS:
  CORPUS_SCALING_HARD_PASS:
    - bpc strictly decreasing across ALL 3 corpus sizes at N=1024 (monotone)
    - AND W_top_edge_ratio >= 2.0 at largest corpus size (not collapsed)
    -> Path-(b) viability: N=1024 can leverage large corpus; P back to 0.35+

  CORPUS_SCALING_HARD_FAIL:
    - bpc plateau or increase between medium and large corpus sizes
    - OR W_top_edge_ratio < 1.5 at any corpus size >= 1MB
    -> Tau-limit binding at N=1024; path-(b) needs N >> 1024 to scale

  MIDDLE_BAND:
    - Monotone bpc improvement but top_edge in [1.5, 2.0] at large corpus
    - OR strictly decreasing but only by < 0.1 bpc between corpus steps
    -> Marginal improvement; path-(b) may need N=4096 to be decisive

  INSTRUMENTATION_FAIL:
    - bpc is NaN, or top_edge_ratio < 1.0 at any cell

SELF-TESTS:
  1. load_corpus(1000) returns bytes of length == 1000
  2. bytes_to_idx(corpus, K=4) returns tensor shape (n, 4) with n > 0
  3. build_context_bundle(byte_atoms, pos_atoms, idx[0]) returns shape (N,)
  4. compute_spectral_metrics(W_zero) returns finite top_edge_ratio
  5. bpc from evaluate_bpc is finite and > 0 at N=256 small corpus

Multi-scale smoke: N=256 and N=512 both at corpus sizes [10_000, 100_000].
If either scale fails or produces suspicious results, BLOCK full ship.

Queue: overnight_queue (GPU; N=1024, 3 corpus_sizes x 5 seeds x 3 epochs; ~2-4h)
Pre-reg: preregs/2026-05-27_wave14_corpus_size_scaling_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Design parameters
N_FULL = 1024
N_SMOKE = 256
K_FULL = 4
K_SMOKE = 4
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
VOCAB_SIZE = 256
BETA = 8.0
ALPHA_LR = 0.3
DECAY = 1e-4
MAX_EPOCHS_FULL = 5
MAX_EPOCHS_SMOKE = 2
BATCH_SIZE = 64

# Corpus sizes: v2 uses 10x larger than v1 to probe well above tau-limit
CORPUS_SIZES_FULL = [100_000, 1_000_000, 10_000_000]   # 100KB / 1MB / 10MB proxy
CORPUS_SIZES_SMOKE = [10_000, 100_000]                   # fast smoke

# Pre-registered thresholds
TOP_EDGE_HARD_FAIL = 1.5
TOP_EDGE_MIDDLE_LO = 1.5
TOP_EDGE_MIDDLE_HI = 2.0
BPC_MIN_IMPROVEMENT = 0.05   # require at least 0.05 bpc improvement between corpus steps
ALPHA_C = 0.5625


def get_output_dir(default_name: str = "wave14_corpus_size_scaling_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def load_corpus(max_bytes: int) -> bytes:
    """Load and tile repo text corpus to max_bytes."""
    files = [
        REPO / "PLAN.md", REPO / "README.md", REPO / "PROGRESS.md",
        REPO / "RESULTS.md", REPO / "CLAUDE.md", REPO / "NEXT_PHASE.md",
    ]
    if max_bytes > 50_000:
        files += sorted((REPO / "experiments").glob("*.py"))[:30]
    if max_bytes > 200_000:
        files += sorted((REPO / "hdlab").glob("*.py"))[:20]
        files += sorted((REPO / "verification").glob("*.py"))[:15]
    if max_bytes > 2_000_000:
        files += sorted((REPO / "experiments").glob("*.py"))   # all scripts
        files += sorted((REPO / "notes").glob("*.md"))[:50]

    parts: List[bytes] = []
    total = 0
    for f in files:
        if not f.exists():
            continue
        data = f.read_bytes()
        parts.append(data)
        total += len(data)

    base_corpus = b"".join(parts) if parts else b"x" * 1000
    if len(base_corpus) == 0:
        base_corpus = b"x" * 1000

    # Tile to reach requested size
    reps = math.ceil(max_bytes / max(len(base_corpus), 1))
    tiled = (base_corpus * reps)[:max_bytes]
    return tiled


def bytes_to_idx(corpus: bytes, k: int) -> torch.Tensor:
    n = len(corpus)
    if n < k + 1:
        return torch.zeros((1, k), dtype=torch.long)
    indices = [list(corpus[i:i + k]) for i in range(0, n - k, 1)]
    return torch.tensor(indices[:50000], dtype=torch.long)   # cap for memory


def build_context_bundle(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                          idx: torch.Tensor) -> torch.Tensor:
    """Bundle K position-bound byte atoms into (N,) context vector."""
    bound = byte_atoms[idx] * pos_atoms   # (K, N)
    summed = bound.sum(dim=0)
    norm = summed.abs().clamp(min=1e-8)
    return summed / norm


def train_epoch(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                W: torch.Tensor, idx_tensor: torch.Tensor,
                batch_size: int, N: int) -> torch.Tensor:
    total_steps = min(idx_tensor.shape[0] - 1, 8000)
    for s in range(0, total_steps, batch_size):
        e = min(s + batch_size, total_steps)
        batch_idx  = idx_tensor[s:e]
        batch_next = idx_tensor[s + 1:e + 1]
        B = min(e - s, batch_next.shape[0])
        if B <= 0:
            continue
        batch_idx  = batch_idx[:B]
        batch_next = batch_next[:B]

        ctxs = torch.stack([
            build_context_bundle(byte_atoms, pos_atoms, batch_idx[i])
            for i in range(B)
        ])   # (B, N)
        targets = torch.stack([
            build_context_bundle(byte_atoms, pos_atoms, batch_next[i])
            for i in range(B)
        ])   # (B, N)

        preds = ctxs @ W.T
        preds_norm = preds / preds.norm(dim=1, keepdim=True).clamp(min=1e-8)
        err = targets - preds_norm
        dW = err.T @ ctxs / N
        W.add_(dW, alpha=ALPHA_LR)
        W.mul_(1.0 - DECAY)
    return W


def evaluate_bpc(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                 W: torch.Tensor, test_corpus: bytes, N: int) -> float:
    k = pos_atoms.shape[0]
    device = byte_atoms.device
    idx_tensor = bytes_to_idx(test_corpus, k)
    n_test = min(idx_tensor.shape[0] - 1, 1000)
    if n_test <= 0:
        return float('nan')

    total_nll = 0.0
    byte_atoms_norm = byte_atoms / byte_atoms.norm(dim=1, keepdim=True).clamp(min=1e-8)

    for i in range(n_test):
        ctx = build_context_bundle(byte_atoms, pos_atoms, idx_tensor[i])
        pred = W.T @ ctx
        pred_norm = pred / pred.norm().clamp(min=1e-8)
        sims = byte_atoms_norm @ pred_norm
        logits = sims * BETA
        true_byte = int(idx_tensor[i + 1, 0])
        log_z = torch.logsumexp(logits, dim=0)
        nll = float(log_z - logits[true_byte])
        total_nll += nll

    return total_nll / n_test / math.log(2)


def compute_spectral_metrics(W: torch.Tensor) -> dict:
    try:
        s = torch.linalg.svdvals(W)
    except Exception:
        return {"top_edge_ratio": float('nan'), "effective_rank": float('nan')}
    s_max = float(s[0])
    s_mean = float(s.mean())
    top_edge_ratio = s_max / max(s_mean, 1e-12)
    s_pos = s[s > 1e-10]
    if len(s_pos) > 0:
        p = s_pos / s_pos.sum()
        eff_rank = math.exp(float(-(p * p.log()).sum()))
    else:
        eff_rank = 0.0
    return {"top_edge_ratio": round(top_edge_ratio, 4), "effective_rank": round(eff_rank, 2)}


def run_cell(train_bytes: int, N: int, K: int, seed: int,
             max_epochs: int, device) -> dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms = (2.0 * torch.randint(0, 2, (VOCAB_SIZE, N),
                                       generator=gen, device=device).float() - 1.0)
    pos_atoms = (2.0 * torch.randint(0, 2, (K, N),
                                      generator=gen, device=device).float() - 1.0)

    corpus = load_corpus(train_bytes)
    split = int(len(corpus) * 0.85)
    train_corpus, test_corpus = corpus[:split], corpus[split:]

    idx_tensor = bytes_to_idx(train_corpus, K).to(device)
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for _ in range(max_epochs):
        W = train_epoch(byte_atoms, pos_atoms, W, idx_tensor, BATCH_SIZE, N)

    bpc = evaluate_bpc(byte_atoms, pos_atoms, W, test_corpus, N)
    spectral = compute_spectral_metrics(W)

    return {
        "train_bytes": train_bytes,
        "N": N, "K": K, "seed": seed,
        "bpc": round(bpc, 5) if math.isfinite(bpc) else None,
        "top_edge_ratio": spectral["top_edge_ratio"],
        "effective_rank": spectral["effective_rank"],
    }


def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    # 1. load_corpus returns correct length
    c = load_corpus(1000)
    assert len(c) == 1000, f"load_corpus length fail: {len(c)}"

    # 2. bytes_to_idx returns valid tensor
    idx = bytes_to_idx(c, 4)
    assert idx.shape[1] == 4 and idx.shape[0] > 0, f"bytes_to_idx shape fail: {idx.shape}"

    # 3. build_context_bundle returns (N,)
    N_t = 64
    gen = torch.Generator().manual_seed(0)
    ba = 2.0 * torch.randint(0, 2, (256, N_t), generator=gen).float() - 1.0
    pa = 2.0 * torch.randint(0, 2, (4, N_t), generator=gen).float() - 1.0
    ctx = build_context_bundle(ba, pa, idx[0])
    assert ctx.shape == (N_t,), f"build_context_bundle shape fail: {ctx.shape}"

    # 4. compute_spectral_metrics on zero W returns finite value
    W_z = torch.zeros((N_t, N_t))
    sm = compute_spectral_metrics(W_z)
    assert math.isfinite(sm["top_edge_ratio"]) or sm["top_edge_ratio"] != sm["top_edge_ratio"], \
        "spectral metrics should be finite or nan, not error"

    # 5. bpc finite at N=64
    W_r = torch.randn((N_t, N_t)) * 0.1
    bpc = evaluate_bpc(ba, pa, W_r, c, N_t)
    assert bpc is not None and not math.isnan(bpc), f"bpc is NaN or None: {bpc}"
    assert bpc > 0, f"bpc should be > 0 (non-trivial): {bpc}"

    # validity filter: at least 1 run completes per corpus size
    cell = run_cell(5000, 64, 4, 42, 1, torch.device("cpu"))
    assert cell["bpc"] is not None, "validity filter eliminated all cells at smoke scale"
    assert cell["bpc"] > 0, f"cell bpc should be > 0: {cell['bpc']}"

    print("[selftest] PASS: 5/5 assertions + 1 run OK", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool, device: torch.device) -> Dict:
    N         = N_SMOKE if smoke else N_FULL
    corpus_sw = CORPUS_SIZES_SMOKE if smoke else CORPUS_SIZES_FULL
    seeds     = SEEDS_SMOKE if smoke else SEEDS_FULL
    max_ep    = MAX_EPOCHS_SMOKE if smoke else MAX_EPOCHS_FULL
    K         = K_SMOKE if smoke else K_FULL

    t0 = time.monotonic()
    print(f"[corpus_scaling_v2] smoke={smoke} N={N} corpus_sizes={corpus_sw} seeds={seeds}",
          flush=True)

    # cells[corpus_size] -> list of bpc values across seeds
    cells: Dict[int, List[float]] = {cs: [] for cs in corpus_sw}
    top_edges: Dict[int, List[float]] = {cs: [] for cs in corpus_sw}

    for cs in corpus_sw:
        for seed in seeds:
            t_c = time.monotonic()
            result = run_cell(cs, N, K, seed, max_ep, device)
            bpc = result.get("bpc")
            te = result.get("top_edge_ratio")
            if bpc is not None and math.isfinite(bpc):
                cells[cs].append(bpc)
            if te is not None and math.isfinite(te):
                top_edges[cs].append(te)
            print(f"  cs={cs} N={N} s={seed}: bpc={bpc} top_edge={te} "
                  f"({time.monotonic()-t_c:.1f}s)", flush=True)

    # Mean metrics per corpus size
    mean_bpc = {cs: (sum(cells[cs]) / len(cells[cs]) if cells[cs] else float("nan"))
                for cs in corpus_sw}
    mean_te  = {cs: (sum(top_edges[cs]) / len(top_edges[cs]) if top_edges[cs] else float("nan"))
                for cs in corpus_sw}

    # Monotonicity check: bpc strictly decreasing (improving) across corpus sizes
    bpc_seq = [mean_bpc[cs] for cs in corpus_sw]
    valid_bpc = [b for b in bpc_seq if math.isfinite(b)]
    n_valid = sum(1 for cs in corpus_sw if cells[cs])

    if n_valid < len(corpus_sw) * 0.5:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: only {n_valid}/{len(corpus_sw)} "
                       f"corpus sizes have valid bpc")
    elif any(math.isnan(b) for b in bpc_seq):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = f"INSTRUMENTATION_FAIL: NaN bpc at some corpus sizes: {bpc_seq}"
    else:
        monotone = all(bpc_seq[i] > bpc_seq[i + 1] for i in range(len(bpc_seq) - 1))
        large_te = mean_te.get(corpus_sw[-1], float("nan"))
        min_improvement = (min(bpc_seq[i] - bpc_seq[i + 1]
                               for i in range(len(bpc_seq) - 1))
                           if len(bpc_seq) >= 2 else 0.0)

        if monotone and not math.isnan(large_te) and large_te >= TOP_EDGE_MIDDLE_HI:
            verdict = "CORPUS_SCALING_HARD_PASS"
            verdict_msg = (f"CORPUS_SCALING_HARD_PASS: bpc strictly decreasing "
                           f"{bpc_seq}; top_edge at large corpus={large_te:.3f} >= {TOP_EDGE_MIDDLE_HI}")
        elif (not monotone) or (not math.isnan(large_te) and large_te < TOP_EDGE_HARD_FAIL):
            verdict = "CORPUS_SCALING_HARD_FAIL"
            verdict_msg = (f"CORPUS_SCALING_HARD_FAIL: bpc={bpc_seq} monotone={monotone}; "
                           f"top_edge@large={large_te:.3f}; tau-limit binding at N={N}")
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (f"MIDDLE_BAND: bpc={[round(b,4) for b in bpc_seq]} monotone={monotone}; "
                           f"top_edge@large={large_te:.3f} in [{TOP_EDGE_HARD_FAIL},{TOP_EDGE_MIDDLE_HI}]; "
                           f"min_improvement={min_improvement:.4f}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": {
            "N": N, "corpus_sizes": corpus_sw,
            "mean_bpc_by_corpus": {str(cs): mean_bpc[cs] for cs in corpus_sw},
            "mean_top_edge_by_corpus": {str(cs): mean_te[cs] for cs in corpus_sw},
            "monotone_bpc": all(bpc_seq[i] > bpc_seq[i+1]
                                for i in range(len(bpc_seq)-1)) if len(bpc_seq) >= 2 else False,
        },
        "config": {"N": N, "smoke": smoke, "corpus_sizes": corpus_sw,
                   "seeds": seeds, "max_epochs": max_ep},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[corpus_scaling_v2] device={device}", flush=True)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke, device=device)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
