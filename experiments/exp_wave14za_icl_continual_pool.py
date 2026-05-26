"""ICL with continual pool additions - real-time learning during inference.

Tests if substrate's pool retrieval improves as the pool grows from
streaming test queries. Cap_map Tier-2 KILLER 'Real-time learning during
inference'.

Pre-reg: preregs/2026-05-21_wave14za_icl_continual_pool.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14d_icl_via_pool_v3_scaling.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
ALPHA = 1.0
BETA = 8.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def stream_eval_with_continual_pool(W, byte_atoms, pos_atoms, test_bytes,
                                       pool_vecs, pool_labels, pool_used, batch_size,
                                       n_dim, pool_capacity):
    """Eval on test_bytes one BATCH at a time. After each batch, APPEND its (ctx, target)
    to the pool with FIFO eviction. Returns (initial_bpc, final_bpc, trajectory)."""
    pad = bytes([v3.PAD_BYTE]) * v3.K
    padded = pad + test_bytes
    T = len(padded) - v3.K
    bt = torch.tensor(list(padded), dtype=torch.long).to(W.device)
    offsets = torch.arange(v3.K - 1, -1, -1, device=W.device)
    pos = torch.arange(T, device=W.device)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + v3.K]

    pool_idx = pool_used % pool_capacity
    trajectory = []
    bpc_accum = 0.0
    n_pos_accum = 0
    snapshot_every = max(T // 20, 1)

    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = v3.build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = v3.shifted_relu(q, v3.RELU_B)
        sims = (byte_atoms @ q.T) / n_dim
        P_W = torch.softmax(BETA * sims, dim=0)
        if pool_used > 0 and ALPHA > 0:
            active = pool_vecs[:pool_used]
            labels = pool_labels[:pool_used]
            sims_p = (active @ ctxs.T) / n_dim
            weights_p = torch.softmax(BETA * sims_p, dim=0)
            P_retr = torch.zeros(v3.VOCAB_SIZE, B, device=W.device)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
            P = ALPHA * P_retr + (1 - ALPHA) * P_W
        else:
            P = P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bpc_batch = float(-torch.log2(p_true).sum())
        bpc_accum += bpc_batch
        n_pos_accum += B

        # Add this batch to pool (continual)
        arange_b = torch.arange(B, device=W.device)
        dest = (pool_idx + arange_b) % pool_capacity
        pool_vecs.index_copy_(0, dest, ctxs)
        pool_labels.index_copy_(0, dest, tgts)
        pool_idx = (pool_idx + B) % pool_capacity
        pool_used = min(pool_used + B, pool_capacity)

        if n_pos_accum >= snapshot_every * (len(trajectory) + 1):
            trajectory.append({"pos": n_pos_accum,
                                "bpc_so_far": bpc_accum / n_pos_accum,
                                "pool_used": pool_used})

    final_bpc = bpc_accum / n_pos_accum if n_pos_accum else float("inf")
    return final_bpc, trajectory


def compute_verdict(summary):
    static_bpc = summary.get("static_pool_bpc")
    continual_bpc = summary.get("continual_pool_final_bpc")
    if static_bpc is None or continual_bpc is None:
        return ("ICL_CONTINUAL_POOL_INCONCLUSIVE", "Missing.")
    improvement = static_bpc - continual_bpc
    if improvement > 0.10:
        return ("ICL_CONTINUAL_POOL_IMPROVES",
                f"Continual pool reduces bpc by {improvement:.3f} vs static "
                f"(static={static_bpc:.3f}, continual={continual_bpc:.3f}). "
                f"Substrate learns from its own queries: real-time learning works.")
    if improvement < -0.05:
        return ("ICL_CONTINUAL_POOL_HARMS",
                f"Continual pool INCREASES bpc by {-improvement:.3f}. The pool "
                f"additions degrade retrieval (likely cross-talk).")
    return ("ICL_CONTINUAL_POOL_FLAT",
            f"Continual pool gives ~same bpc as static (static={static_bpc:.3f}, "
            f"continual={continual_bpc:.3f}, delta={improvement:+.3f}). Substrate "
            f"doesn't measurably benefit from continual additions in this regime.")


def self_test_verdict():
    cases = [
        ({"static_pool_bpc": 4.5, "continual_pool_final_bpc": 4.2},
         "ICL_CONTINUAL_POOL_IMPROVES"),
        ({"static_pool_bpc": 4.5, "continual_pool_final_bpc": 4.7},
         "ICL_CONTINUAL_POOL_HARMS"),
        ({"static_pool_bpc": 4.5, "continual_pool_final_bpc": 4.48},
         "ICL_CONTINUAL_POOL_FLAT"),
        ({}, "ICL_CONTINUAL_POOL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_dim = N_SMOKE if smoke else N_FULL
    seed = 17
    max_epochs = 1 if smoke else 5
    batch_size = 64
    pool_capacity = 4096

    corpus_a = v3.load_corpus_a()
    corpus_b = v3.load_corpus_b_code(8000 if smoke else 200_000)
    train_a = corpus_a[:int(0.8 * len(corpus_a))]
    if smoke:
        train_a = train_a[:4000]
    test_b = corpus_b[int(0.7 * len(corpus_b)):int(0.7 * len(corpus_b)) + (4000 if smoke else 16000)]

    gen_rng = torch.Generator().manual_seed(seed)
    byte_atoms = v3.make_bsc_atoms(v3.VOCAB_SIZE, n_dim, gen_rng).to(device)
    pos_atoms = v3.make_bsc_atoms(v3.K, n_dim, gen_rng).to(device)

    W, pool_A, labels_A, used_A = v3.train_phase_a(
        byte_atoms, pos_atoms, train_a, n_dim, max_epochs, batch_size)

    # Static pool eval (baseline)
    static_bpc, _ = v3.eval_with_pool(W, byte_atoms, pos_atoms, test_b,
                                          pool_A, labels_A, used_A, ALPHA,
                                          batch_size, n_dim)

    # Continual pool eval: clone pool, then grow during eval
    pool_B = pool_A.clone()
    labels_B = labels_A.clone()
    final_bpc, trajectory = stream_eval_with_continual_pool(
        W, byte_atoms, pos_atoms, test_b, pool_B, labels_B, used_A, batch_size,
        n_dim, pool_capacity)

    summary = {"static_pool_bpc": static_bpc,
               "continual_pool_final_bpc": final_bpc,
               "trajectory": trajectory}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nstatic_pool_bpc = {static_bpc:.3f}", flush=True)
    print(f"continual_pool_final_bpc = {final_bpc:.3f}", flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, {"mode": "smoke" if smoke else "full",
                                                "N": n_dim, "max_epochs": max_epochs}


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14za_icl_continual_pool_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    static_bpc = summary["static_pool_bpc"]
    oracle.assert_in_range("static_bpc_smoke", static_bpc, (0.5, 8.0))
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14za_icl_continual_pool")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
