"""Corpus-size scaling probe v1: bpc monotonicity + W spectral top-edge ratio.

CONTEXT: R26 path-(b) feasibility; P(path-b)=0.35 after tau-limit finding.
Research note: notes/research_corpus_size_scaling_2026-05-27.md
Handoff: notes/exp_dev_handoff_corpus_size_scaling_probe_2026-05-27.md

HYPOTHESIS: if substrate Hebbian W accumulates interference when M_stored > alpha_c * N,
then at small N bpc may plateau or degrade at large corpus sizes. Tau-limit onset is
flagged by W spectral top-edge ratio collapsing toward 1.0.

DESIGN:
  - N = 1024 (CPU-feasible; tight tau-limit onset expected here)
  - Corpus sizes: 3 levels spanning ~2 decades
      small:  ~10MB  (10000 tokens * avg ~10 bytes/token -> 100KB raw; scale by batch)
      medium: ~100KB bytes (train_bytes = 100_000)
      large:  ~500KB bytes (train_bytes = 500_000)
  NOTE: actual corpus is streamed from enwik8/enwiki or repo text; sizes in bytes.
  - K = 4 position atoms
  - 2 seeds (variance estimate at low cost)
  - Metrics per cell: bpc (bits per character), W_top_edge_ratio, W_effective_rank

Pre-registered bands (from handoff):
  HARD-PASS: bpc strictly decreasing across all corpus-size cells AND
             W_top_edge_ratio NOT collapsing (>= 1.5 at all cells)
  HARD-FAIL: bpc stops improving or increases at largest cell OR
             W_top_edge_ratio < 1.5 at largest cell
  MIDDLE:    monotone bpc improvement but top-edge in [1.5, 2.0] at largest cell

Queue: remote_cpu_queue (no GPU; N=1024; < 30 min total)
Pre-reg: preregs/2026-05-27_wave14_corpus_size_scaling_v1.md
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
from typing import List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Design parameters
N_FULL = 1024
N_SMOKE = 256
K_FULL = 4
K_SMOKE = 4
SEEDS_FULL = [7, 17]
SEEDS_SMOKE = [17]
VOCAB_SIZE = 256
BETA = 8.0
ALPHA = 0.3
DECAY = 1e-4
MAX_EPOCHS = 3          # 3 epochs per corpus size to avoid N*epochs memory OOM
BATCH_SIZE = 64

# Corpus sizes in bytes (training bytes)
CORPUS_SIZES_FULL = [10_000, 100_000, 500_000]    # small / medium / large
CORPUS_SIZES_SMOKE = [3_000, 20_000]               # fast smoke

# Pre-registered thresholds
TOP_EDGE_HARD_FAIL = 1.5   # ratio below this = whitening onset
TOP_EDGE_MIDDLE_LO = 1.5
TOP_EDGE_MIDDLE_HI = 2.0

ALPHA_C = 0.5625   # empirical alpha_c; conservative for N=1024


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def load_corpus(max_bytes: int) -> bytes:
    """Load text corpus from repo docs, up to max_bytes."""
    files = [
        REPO / "PLAN.md", REPO / "README.md", REPO / "PROGRESS.md",
        REPO / "RESULTS.md", REPO / "CLAUDE.md", REPO / "NEXT_PHASE.md",
    ]
    # Supplement with experiment scripts if needed for larger sizes
    if max_bytes > 50_000:
        files += sorted((REPO / "experiments").glob("*.py"))[:20]
    if max_bytes > 200_000:
        files += sorted((REPO / "hdlab").glob("*.py"))[:15]
        files += sorted((REPO / "verification").glob("*.py"))[:10]

    parts = []
    total = 0
    for f in files:
        if not f.exists():
            continue
        data = f.read_bytes()
        remaining = max_bytes - total
        if remaining <= 0:
            break
        chunk = data[:remaining]
        parts.append(chunk)
        total += len(chunk)
        if total >= max_bytes:
            break

    result = b"".join(parts)
    if len(result) < max_bytes:
        # Tile to reach requested size
        reps = math.ceil(max_bytes / max(len(result), 1))
        result = (result * reps)[:max_bytes]
    return result[:max_bytes]


def bytes_to_idx(corpus: bytes, k: int) -> torch.Tensor:
    """Convert corpus bytes to K-gram index tensor. Shape: (L, K)."""
    n = len(corpus)
    indices = []
    for i in range(0, n - k, 1):
        indices.append(list(corpus[i:i + k]))
    if not indices:
        return torch.zeros((1, k), dtype=torch.long)
    return torch.tensor(indices, dtype=torch.long)


def build_context_bundle(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                         idx: torch.Tensor) -> torch.Tensor:
    """Bundle K position-bound byte atoms. Shape: (N,)."""
    bound = byte_atoms[idx] * pos_atoms   # (K, N)
    summed = bound.sum(dim=0)
    norm = summed.abs().clamp(min=1e-8)
    return summed / norm


def init_weight_matrix(N: int, device) -> torch.Tensor:
    return torch.zeros((N, N), dtype=torch.float32, device=device)


def train_epoch(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                W: torch.Tensor, corpus: bytes, N: int) -> torch.Tensor:
    """One epoch of Hebbian outer-product learning. Returns updated W."""
    k = pos_atoms.shape[0]
    device = byte_atoms.device
    idx_tensor = bytes_to_idx(corpus, k)
    total_steps = min(idx_tensor.shape[0] - 1, 5000)   # cap per-epoch steps for speed

    for s in range(0, total_steps, BATCH_SIZE):
        e = min(s + BATCH_SIZE, total_steps)
        batch_idx = idx_tensor[s:e]  # (B, K)
        batch_next = idx_tensor[s + 1:e + 1]  # (B, K) target positions

        # Build context and target bundles
        ctxs = torch.stack([
            build_context_bundle(byte_atoms, pos_atoms, batch_idx[i])
            for i in range(e - s)
        ])  # (B, N)
        targets = torch.stack([
            build_context_bundle(byte_atoms, pos_atoms, batch_next[i])
            for i in range(e - s)
        ])  # (B, N)

        # Prediction and error
        preds = ctxs @ W.T  # (B, N)
        preds_norm = preds / preds.norm(dim=1, keepdim=True).clamp(min=1e-8)
        err = targets - preds_norm  # (B, N)

        # Outer-product update with decay
        dW = err.T @ ctxs / N
        W.add_(dW, alpha=ALPHA)
        W.mul_(1.0 - DECAY)

    return W


def evaluate_bpc(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                 W: torch.Tensor, test_corpus: bytes, N: int) -> float:
    """Estimate bpc via cosine-similarity scoring on held-out corpus."""
    k = pos_atoms.shape[0]
    device = byte_atoms.device
    idx_tensor = bytes_to_idx(test_corpus, k)
    n_test = min(idx_tensor.shape[0] - 1, 500)
    if n_test <= 0:
        return float('nan')

    total_nll = 0.0
    total_chars = 0
    byte_atoms_norm = byte_atoms / byte_atoms.norm(dim=1, keepdim=True).clamp(min=1e-8)

    for i in range(n_test):
        ctx = build_context_bundle(byte_atoms, pos_atoms, idx_tensor[i])  # (N,)
        pred = W.T @ ctx  # (N,)
        pred_norm = pred / pred.norm().clamp(min=1e-8)
        # Similarity scores against all byte atoms (vocab)
        sims = byte_atoms_norm @ pred_norm  # (V,)
        logits = sims * BETA
        # Softmax NLL for true next byte
        true_byte = int(idx_tensor[i + 1, 0])
        log_z = torch.logsumexp(logits, dim=0)
        nll = float(log_z - logits[true_byte])
        total_nll += nll
        total_chars += 1

    if total_chars == 0:
        return float('nan')
    return total_nll / total_chars / math.log(2)  # convert nats to bits


def compute_spectral_metrics(W: torch.Tensor) -> dict:
    """Compute spectral top-edge ratio and effective rank of W."""
    # SVD (economy)
    try:
        s = torch.linalg.svdvals(W)
    except Exception:
        return {"top_edge_ratio": float('nan'), "effective_rank": float('nan'), "s_max": float('nan'), "s_mean": float('nan')}

    s_max = float(s[0])
    s_mean = float(s.mean())
    top_edge_ratio = s_max / max(s_mean, 1e-12)

    # Effective rank = exp(H(singular values))
    s_pos = s[s > 1e-10]
    if len(s_pos) == 0:
        eff_rank = 0.0
    else:
        p = s_pos / s_pos.sum()
        entropy = float(-(p * p.log()).sum())
        eff_rank = math.exp(float(entropy))

    return {
        "top_edge_ratio": round(top_edge_ratio, 4),
        "effective_rank": round(eff_rank, 2),
        "s_max": round(s_max, 6),
        "s_mean": round(s_mean, 6),
    }


def run_cell(train_bytes: int, N: int, K: int, seed: int, device) -> dict:
    """One cell: train on corpus_size bytes, evaluate bpc + spectral metrics."""
    gen = torch.Generator(device=device).manual_seed(seed)

    byte_atoms = 2.0 * torch.randint(0, 2, (VOCAB_SIZE, N), generator=gen, device=device).float() - 1.0
    pos_atoms = 2.0 * torch.randint(0, 2, (K, N), generator=gen, device=device).float() - 1.0

    corpus = load_corpus(train_bytes)
    split = int(len(corpus) * 0.85)
    train_corpus, test_corpus = corpus[:split], corpus[split:]

    W = init_weight_matrix(N, device)
    for epoch in range(MAX_EPOCHS):
        W = train_epoch(byte_atoms, pos_atoms, W, train_corpus, N)

    bpc = evaluate_bpc(byte_atoms, pos_atoms, W, test_corpus, N)
    spectral = compute_spectral_metrics(W)

    # Effective M_stored estimate (Heaps' law approximation for vocab growth)
    # rough: M_stored ~ train_bytes / K (one pattern per K-gram)
    m_stored_est = min(train_bytes // K, ALPHA_C * N * 0.9)
    capacity_fraction = m_stored_est / max(ALPHA_C * N, 1)

    return {
        "train_bytes": train_bytes,
        "N": N, "K": K, "seed": seed,
        "bpc": round(bpc, 5) if math.isfinite(bpc) else None,
        "top_edge_ratio": spectral["top_edge_ratio"],
        "effective_rank": spectral["effective_rank"],
        "s_max": spectral["s_max"],
        "s_mean": spectral["s_mean"],
        "capacity_fraction_est": round(capacity_fraction, 4),
        "m_stored_est": int(m_stored_est),
    }


# ── instrumentation self-test ──

def _instrumentation_selftest() -> None:
    print("[selftest] starting instrumentation self-test...", flush=True)
    device = torch.device("cpu")

    # 1. load_corpus returns correct length
    c = load_corpus(5000)
    assert len(c) == 5000, f"Selftest 1 FAIL: load_corpus returned {len(c)} bytes"
    print("[selftest] 1/5 load_corpus length OK")

    # 2. bytes_to_idx returns correct shape
    idx = bytes_to_idx(b"hello world", 4)
    assert idx.shape[1] == 4, f"Selftest 2 FAIL: wrong idx shape {idx.shape}"
    print("[selftest] 2/5 bytes_to_idx shape OK")

    # 3. context bundle produces finite non-NaN output (elementwise div by abs, not vector-norm)
    gen = torch.Generator(device=device).manual_seed(42)
    batoms = 2.0 * torch.randint(0, 2, (256, 64), generator=gen, device=device).float() - 1.0
    patoms = 2.0 * torch.randint(0, 2, (4, 64), generator=gen, device=device).float() - 1.0
    idx_s = torch.tensor([0, 1, 2, 3], dtype=torch.long)
    ctx = build_context_bundle(batoms, patoms, idx_s)
    assert ctx.shape == (64,), f"Selftest 3 FAIL: wrong shape {ctx.shape}"
    assert not ctx.isnan().any(), "Selftest 3 FAIL: NaN in context bundle"
    assert ctx.abs().max() <= 1.01, f"Selftest 3 FAIL: max abs > 1 (got {ctx.abs().max():.4f})"
    print(f"[selftest] 3/5 context bundle: shape={ctx.shape}, finite, max_abs={ctx.abs().max():.4f}")

    # 4. compute_spectral_metrics returns finite values
    W_test = torch.randn(32, 32)
    spec = compute_spectral_metrics(W_test)
    assert math.isfinite(spec["top_edge_ratio"]), f"Selftest 4a FAIL: top_edge_ratio not finite"
    assert spec["effective_rank"] > 0, f"Selftest 4b FAIL: effective_rank <= 0"
    print(f"[selftest] 4/5 spectral metrics OK: top_edge={spec['top_edge_ratio']:.3f} eff_rank={spec['effective_rank']:.1f}")

    # 5. run_cell at smoke scale produces non-null bpc and spectral metrics
    cell = run_cell(3000, 128, 4, 7, device)
    assert cell["bpc"] is not None, "Selftest 5a FAIL: bpc is None"
    assert math.isfinite(cell["bpc"]), f"Selftest 5b FAIL: bpc not finite: {cell['bpc']}"
    assert cell["top_edge_ratio"] is not None, "Selftest 5c FAIL: top_edge_ratio is None"
    assert cell["effective_rank"] > 0, f"Selftest 5d FAIL: effective_rank={cell['effective_rank']}"
    print(f"[selftest] 5/5 run_cell smoke: bpc={cell['bpc']:.4f} top_edge={cell['top_edge_ratio']:.3f}")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool = False) -> tuple[dict, Path]:
    device = torch.device("cpu")
    N = N_SMOKE if smoke else N_FULL
    K = K_SMOKE if smoke else K_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    corpus_sizes = CORPUS_SIZES_SMOKE if smoke else CORPUS_SIZES_FULL
    out_dir = get_output_dir("wave14_corpus_size_scaling_v1")

    results_per_size: dict[int, dict] = {}
    for train_bytes in corpus_sizes:
        print(f"\n[run] train_bytes={train_bytes} N={N} K={K}", flush=True)
        cells = []
        for seed in seeds:
            c = run_cell(train_bytes, N, K, seed, device)
            cells.append(c)
            bpc_str = f"{c['bpc']:.4f}" if c["bpc"] is not None else "NaN"
            print(f"  seed={seed}: bpc={bpc_str} top_edge={c['top_edge_ratio']:.3f} "
                  f"eff_rank={c['effective_rank']:.1f} cap_frac={c['capacity_fraction_est']:.3f}",
                  flush=True)

        valid_bpc = [c["bpc"] for c in cells if c["bpc"] is not None and math.isfinite(c["bpc"])]
        mu_bpc = sum(valid_bpc) / max(len(valid_bpc), 1) if valid_bpc else float('nan')
        std_bpc = math.sqrt(
            sum((x - mu_bpc) ** 2 for x in valid_bpc) / max(len(valid_bpc) - 1, 1)
        ) if len(valid_bpc) > 1 else 0.0
        mu_top_edge = sum(c["top_edge_ratio"] for c in cells if math.isfinite(c["top_edge_ratio"])) / len(cells)
        mu_eff_rank = sum(c["effective_rank"] for c in cells if c["effective_rank"] > 0) / len(cells)

        results_per_size[train_bytes] = {
            "train_bytes": train_bytes,
            "mean_bpc": round(mu_bpc, 5) if math.isfinite(mu_bpc) else None,
            "std_bpc": round(std_bpc, 5),
            "mean_top_edge_ratio": round(mu_top_edge, 4),
            "mean_effective_rank": round(mu_eff_rank, 2),
            "n_seeds": len(cells),
        }
        print(f"  -> bpc={mu_bpc:.4f}+/-{std_bpc:.4f} top_edge={mu_top_edge:.3f} eff_rank={mu_eff_rank:.1f}", flush=True)

    return results_per_size, out_dir


def compute_verdict(results_per_size: dict) -> tuple[str, str, dict]:
    sorted_sizes = sorted(results_per_size.keys())
    bpcs = [results_per_size[s]["mean_bpc"] for s in sorted_sizes]
    top_edges = [results_per_size[s]["mean_top_edge_ratio"] for s in sorted_sizes]

    valid_bpcs = [(s, b) for s, b in zip(sorted_sizes, bpcs) if b is not None and math.isfinite(b)]
    valid_top_edges = [(s, t) for s, t in zip(sorted_sizes, top_edges) if math.isfinite(t)]

    summary = {
        "corpus_sizes": sorted_sizes,
        "per_size": results_per_size,
        "bpc_sequence": [b for _, b in valid_bpcs],
        "top_edge_sequence": [t for _, t in valid_top_edges],
        "top_edge_hard_fail_thresh": TOP_EDGE_HARD_FAIL,
        "top_edge_middle_band": [TOP_EDGE_MIDDLE_LO, TOP_EDGE_MIDDLE_HI],
    }

    if len(valid_bpcs) < 2:
        return ("INSTRUMENTATION_FAIL", "Fewer than 2 valid bpc measurements.", summary)

    # Monotonicity check
    bpc_vals = [b for _, b in valid_bpcs]
    monotone = all(bpc_vals[i] >= bpc_vals[i + 1] for i in range(len(bpc_vals) - 1))

    # Top-edge ratio at largest corpus
    largest_size = sorted_sizes[-1]
    top_edge_large = results_per_size[largest_size]["mean_top_edge_ratio"]

    # Whitening onset
    whitening_onset = math.isfinite(top_edge_large) and top_edge_large < TOP_EDGE_HARD_FAIL

    summary["monotone_bpc"] = monotone
    summary["top_edge_at_largest"] = top_edge_large
    summary["whitening_onset"] = whitening_onset

    if monotone and not whitening_onset and top_edge_large >= TOP_EDGE_MIDDLE_HI:
        verdict = "CORPUS_SCALING_HARD_PASS"
        verdict_msg = (
            f"CORPUS_SCALING_HARD_PASS: bpc strictly decreasing across {len(bpc_vals)} corpus sizes "
            f"({bpc_vals[0]:.4f} -> {bpc_vals[-1]:.4f}) AND W top-edge ratio stable at largest corpus "
            f"(top_edge={top_edge_large:.3f} >= {TOP_EDGE_MIDDLE_HI}). "
            f"Tau-limit not binding in tested range. Path-(b) corpus-size axis is safe to extrapolate."
        )
    elif not monotone or whitening_onset:
        reasons = []
        if not monotone:
            reasons.append(f"bpc non-monotone: {[round(b, 4) for b in bpc_vals]}")
        if whitening_onset:
            reasons.append(f"top_edge at largest={top_edge_large:.3f} < {TOP_EDGE_HARD_FAIL} (whitening onset)")
        verdict = "CORPUS_SCALING_HARD_FAIL"
        verdict_msg = (
            f"CORPUS_SCALING_HARD_FAIL: tau-limit binding in tested range. "
            + "; ".join(reasons) + ". "
            f"N-scaling required before corpus-size scaling extrapolation is safe for path-(b)."
        )
    else:
        verdict = "CORPUS_SCALING_MIDDLE"
        verdict_msg = (
            f"CORPUS_SCALING_MIDDLE: bpc monotone but top-edge in ambiguous band at largest corpus "
            f"(top_edge={top_edge_large:.3f} in [{TOP_EDGE_MIDDLE_LO}, {TOP_EDGE_MIDDLE_HI}]). "
            f"Further probe needed at larger N (N=4096 or N=8192) before path-(b) extrapolation."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False) -> None:
    t0 = time.time()
    print(f"[exp] wave14_corpus_size_scaling_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results_per_size, out_dir = run_sweep(smoke)

    # Multi-scale smoke: also run at N_smoke * 2 for the smallest corpus size
    if smoke:
        print("\n[multi-scale smoke] N_smoke * 2 check...", flush=True)
        device = torch.device("cpu")
        c2 = run_cell(CORPUS_SIZES_SMOKE[0], N_SMOKE * 2, K_SMOKE, 17, device)
        assert c2["bpc"] is not None and math.isfinite(c2["bpc"]), \
            f"Multi-scale smoke FAIL: bpc={c2['bpc']}"
        assert c2["top_edge_ratio"] is not None and math.isfinite(c2["top_edge_ratio"]), \
            "Multi-scale smoke FAIL: top_edge_ratio not finite"
        print(f"  N={N_SMOKE * 2}: bpc={c2['bpc']:.4f} top_edge={c2['top_edge_ratio']:.3f}", flush=True)
        print("[multi-scale smoke] PASS", flush=True)

    verdict, verdict_msg, summary = compute_verdict(results_per_size)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "K": K_SMOKE if smoke else K_FULL,
            "corpus_sizes": CORPUS_SIZES_SMOKE if smoke else CORPUS_SIZES_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "max_epochs": MAX_EPOCHS,
            "mode": "smoke" if smoke else "full",
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit (used by queue gate)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)  # selftests already ran at module scope above
    run(smoke=args.smoke)
