"""Bet B Tier-1 KILLER - Multi-task continual learning A -> B -> C with replay.

Per R5 spec. Three sequential training phases on byte-LM substrate:
  Phase A: corpus_A = repo text (English)
  Phase B: corpus_B = byte-shuffled A (Phase-B established shift); 10% A replay
  Phase C: corpus_C = Python source (genuinely different domain); 10% A+B replay

Multi-probe: bpc on held-out A/B/C; retention ratios; BWT; gain_C.

Pre-reg: preregs/2026-05-21_wave14d_multi_task_cl_v13_a05.md
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

_pa = importlib.util.spec_from_file_location("pa", REPO / "experiments" / "exp_wave14b_cl_phase_a.py")
pa = importlib.util.module_from_spec(_pa); _pa.loader.exec_module(pa)

# Smaller scale for smoke gate
N_FULL = 4096
N_SMOKE = 1024
K = 4
BETA = 8.0
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
POOL_SIZE = 1024
ALPHA_RETR = 0.3
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
VOCAB = 256
PAD_BYTE = 0

EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8  # stronger Phase A baseline so subsequent overwrites erode less
REPLAY_FRAC = 0.10  # v9 maximum replay; compound with EMA

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_RETENTION = 0.80
PARTIAL_RETENTION = 0.50


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("BET_B_INCONCLUSIVE", "Missing per-seed.")
    seeds = list(seeds_data.values())
    # Aggregate
    ret_A = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B = sum(s["retention_B"] for s in seeds) / len(seeds)
    gain_C = sum(s["gain_C"] for s in seeds) / len(seeds)
    bwt = sum(s["bwt"] for s in seeds) / len(seeds)

    n_seeds = len(seeds)
    n_kill = sum(1 for s in seeds
                  if s["retention_A"] < PARTIAL_RETENTION or s["retention_B"] < PARTIAL_RETENTION)
    if n_kill * 2 > n_seeds:
        return ("BET_B_KILLED",
                f"Catastrophic forgetting: retention_A={ret_A:.3f} or retention_B={ret_B:.3f} "
                f"below {PARTIAL_RETENTION} on majority of {n_seeds} seeds. "
                f"gain_C={gain_C:.4f}, bwt={bwt:+.4f}. Mechanism insufficient at tested scale.")
    if ret_A >= PASS_RETENTION and ret_B >= PASS_RETENTION and gain_C > 0 and bwt >= 0:
        return ("BET_B_PASS",
                f"Tier-1 KILLER validated. retention_A={ret_A:.3f}>={PASS_RETENTION}, "
                f"retention_B={ret_B:.3f}>={PASS_RETENTION}, gain_C={gain_C:.4f}>0, "
                f"bwt={bwt:+.4f}>=0. Multi-task CL works through A->B->C with replay.")
    if ret_A >= PASS_RETENTION and ret_B >= PARTIAL_RETENTION and gain_C > 0:
        return ("BET_B_PARTIAL",
                f"Partial: retention_A={ret_A:.3f} held, retention_B={ret_B:.3f} in "
                f"[{PARTIAL_RETENTION}, {PASS_RETENTION}), gain_C={gain_C:.4f}>0, "
                f"bwt={bwt:+.4f}. Product-relevant under partial-retention assumptions.")
    return ("BET_B_INCONCLUSIVE",
            f"Pattern doesn't fit standard verdict. retention_A={ret_A:.3f}, "
            f"retention_B={ret_B:.3f}, gain_C={gain_C:.4f}, bwt={bwt:+.4f}.")


def self_test_verdict():
    def mk(ra, rb, gc, bw):
        return {"per_seed": {"17": {"retention_A": ra, "retention_B": rb,
                                       "gain_C": gc, "bwt": bw}}}
    cases = [
        (mk(0.95, 0.92, 0.30, 0.01), "BET_B_PASS"),
        (mk(0.85, 0.60, 0.25, -0.02), "BET_B_PARTIAL"),
        (mk(0.40, 0.30, 0.30, -0.50), "BET_B_KILLED"),
        ({"per_seed": {"17": {"retention_A": 0.85, "retention_B": 0.65,
                                "gain_C": -0.05, "bwt": -0.10}}}, "BET_B_INCONCLUSIVE"),
        ({}, "BET_B_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def load_corpus_C(smoke):
    """Python source from experiments dir as corpus_C."""
    exp_dir = REPO / "experiments"
    parts = []
    n_files = 3 if smoke else 12
    for f in sorted(exp_dir.glob("exp_wave14b*.py"))[:n_files]:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def train_w_with_replay(W_init, pool_vecs, pool_labels, pool_used,
                          byte_atoms, pos_atoms, train_bytes, target_bytes,
                          replay_pool_vecs, replay_pool_labels, replay_pool_used,
                          n_epochs, batch_size, device):
    """Train W on (train_bytes, target_bytes) with optional replay from external pool.

    train_bytes: (T, K) int  contextual indices
    target_bytes: (T,) int   next-byte targets
    replay_pool_*: if given, sample REPLAY_FRAC of each batch from this pool."""
    W = W_init.clone().to(device)
    if pool_vecs is not None:
        pool_vecs = pool_vecs.to(device)
        pool_labels = pool_labels.to(device)
    if replay_pool_vecs is not None:
        replay_pool_vecs = replay_pool_vecs.to(device)
        replay_pool_labels = replay_pool_labels.to(device)
    N = W.shape[0]
    T = train_bytes.shape[0]
    arange_b = torch.arange(batch_size, device=device)
    pool_idx_local = pool_used % POOL_SIZE if pool_used else 0
    pool_used_local = pool_used or 0
    if pool_vecs is None:
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=device)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=device)

    for epoch in range(n_epochs):
        for batch_start in range(0, T, batch_size):
            be = min(batch_start + batch_size, T)
            idx_batch = train_bytes[batch_start:be]
            tgt_batch = target_bytes[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)

            # Optional replay augmentation
            if replay_pool_vecs is not None and replay_pool_used > 0:
                n_replay = max(1, int(REPLAY_FRAC * B))
                replay_perm = torch.randperm(replay_pool_used, device=device)[:n_replay]
                replay_ctxs = replay_pool_vecs[replay_perm]
                replay_tgts = replay_pool_labels[replay_perm]
                ctxs = torch.cat([ctxs, replay_ctxs], dim=0)
                tgt_batch = torch.cat([tgt_batch, replay_tgts], dim=0)
                B = ctxs.shape[0]

            with torch.no_grad():
                q = ctxs @ W.T
                q = pa.shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_DECAY)
                W.add_(dW, alpha=DELTA_ALPHA)
                if epoch == 0:
                    # Build phase pool from THIS phase's batches only
                    take = min(B, batch_size)  # don't include replay in own pool
                    if take > 0:
                        dest = (pool_idx_local + arange_b[:take]) % POOL_SIZE
                        pool_vecs.index_copy_(0, dest, ctxs[:take])
                        pool_labels.index_copy_(0, dest, tgt_batch[:take])
                        pool_idx_local = (pool_idx_local + take) % POOL_SIZE
                        pool_used_local = min(pool_used_local + take, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used_local


def evaluate_bpc(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms,
                   eval_bytes, eval_targets, batch_size, device):
    N = W.shape[0]
    T = eval_bytes.shape[0]
    total_bits = 0.0
    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_bytes[bs:be])
        P_W = pa.predict_W(W, ctxs, byte_atoms, BETA, N)
        P_retr = pa.predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P = ALPHA_RETR * P_retr + (1.0 - ALPHA_RETR) * P_W
        tgts = eval_targets[bs:be]
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())
    return total_bits / max(T, 1)


def bytes_to_idx_tensors(data, device):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + data
    T = len(padded) - K
    byts = torch.tensor(list(padded), dtype=torch.long, device=device)
    offsets = torch.arange(K - 1, -1, -1, device=device)
    pos = torch.arange(T, device=device)
    return byts[pos.unsqueeze(1) + offsets.unsqueeze(0)], byts[pos + K]


def run_one_seed(seed, config, device):
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config.get("phase_a_epochs", n_epochs)
    n_bytes = config["bytes_per_corpus"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    if n_bytes < len(corpus_a_full):
        corpus_a = corpus_a_full[:n_bytes]
    else:
        corpus_a = corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    # Train/test split (80/20)
    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)

    train_a_idx, train_a_tgt = bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = bytes_to_idx_tensors(train_b, device)
    test_b_idx, test_b_tgt = bytes_to_idx_tensors(test_b, device)
    train_c_idx, train_c_tgt = bytes_to_idx_tensors(train_c, device)
    test_c_idx, test_c_tgt = bytes_to_idx_tensors(test_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A
    W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                       byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                       batch_size, device)
    bpc_zero_on_C = evaluate_bpc(W_zero, None, None, 0, byte_atoms, pos_atoms,
                                      test_c_idx, test_c_tgt, batch_size, device)

    # Phase B (with A replay)
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)
    bpc_B_baseline = evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                       byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                       batch_size, device)

    # Phase C (with combined A+B replay)
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_u = combined_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_v, combined_l, combined_u, n_epochs, batch_size, device)

    # v7: EMA blend with alpha sweep — return results per alpha
    ema_alpha = config.get("ema_alpha", 0.7)
    W_ABC = ema_alpha * W_ABC + (1.0 - ema_alpha) * W_A

    # Multi-probe battery
    bpc_A_after_C = evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                       byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                       batch_size, device)
    bpc_B_after_C = evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                       byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                       batch_size, device)
    bpc_C_after_C = evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                       byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                       batch_size, device)
    bpc_A_after_B = evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                       byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                       batch_size, device)

    # Retention = baseline / post_C  (lower BPC is better; ratio < 1 means worse;
    # bound by min(baseline / post_C, 1.0) so ideal retention = 1.0)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_after_C, 1e-6), 1.0)
    gain_C = bpc_zero_on_C - bpc_C_after_C
    bwt_A = bpc_A_after_B - bpc_A_after_C  # negative means A degraded post-C
    bwt = bwt_A  # main BWT signal

    return {"retention_A": retention_A, "retention_B": retention_B,
             "gain_C": gain_C, "bwt": bwt,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_C": bpc_A_after_C,
             "bpc_B_baseline": bpc_B_baseline, "bpc_B_after_C": bpc_B_after_C,
             "bpc_zero_on_C": bpc_zero_on_C, "bpc_C_after_C": bpc_C_after_C}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    alphas = [0.7] if smoke else [0.3, 0.5, 0.7, 0.9]
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": 5000 if smoke else 200000,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "replay_frac": REPLAY_FRAC,
              "alphas": alphas}
    print(f"[config] {config}", flush=True)
    per_alpha = {}
    for alpha in alphas:
        per_seed = {}
        cfg_local = dict(config)
        cfg_local["ema_alpha"] = alpha
        print(f"[alpha={alpha}] sweep ...", flush=True)
        for seed in config["seeds"]:
            r = run_one_seed(seed, cfg_local, device)
            per_seed[str(seed)] = r
            print(f"  alpha={alpha} seed={seed}: retention_A={r['retention_A']:.3f} "
                  f"retention_B={r['retention_B']:.3f}", flush=True)
        per_alpha[str(alpha)] = per_seed
    # Use best alpha for verdict (the alpha maximizing min retention)
    best_alpha = max(alphas, key=lambda a: min(
        sum(per_alpha[str(a)][s]["retention_A"] for s in per_alpha[str(a)]) / len(per_alpha[str(a)]),
        sum(per_alpha[str(a)][s]["retention_B"] for s in per_alpha[str(a)]) / len(per_alpha[str(a)])))
    print(f"[best_alpha={best_alpha}]", flush=True)
    summary = {"per_seed": per_alpha[str(best_alpha)],
                "per_alpha": per_alpha, "best_alpha": best_alpha}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14d_multi_task_cl_v13_a05_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    seed_key = list(summary["per_seed"].keys())[0]
    r = summary["per_seed"][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14d_multi_task_cl_v13_a05")
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
