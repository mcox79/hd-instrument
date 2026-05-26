"""Bet B rehab probe: EWC (Elastic Weight Consolidation) smoke for the byte-LM substrate.

Mechanism: after Phase A, compute a Fisher-information diagonal F on W
(estimated as E[(d log p / d W_ij)^2] over Phase-A retrieval samples).
During Phase B and Phase C, add a quadratic penalty
  L_ewc = (lambda/2) * sum_{ij} F_ij * (W_ij - W_A_ij)^2
to the W update step. We implement this by augmenting the delta-rule update
with a pull-back term toward W_A weighted by F:

  W <- W + alpha * dW - lambda * F * (W - W_A)

This is the canonical Kirkpatrick 2017 EWC formulation, adapted from
gradient-descent W to delta-rule W.

Hypothesis: EWC lifts retention_A from the current ~0.73 baseline toward >=0.80,
without harming gain_C significantly. Hard-fail: retention_A <= 0.70 with EWC
on at lambda > 0 (worse than no-EWC); hard-pass: retention_A >= 0.80 at any
tested lambda with gain_C > 0.

Smoke scale: N=512, single seed, 2 epochs, 4000 bytes per corpus, single
lambda value to verify the mechanism works in <60s; full scale is N=4096, 5
seeds, 5 epochs, 200k bytes.

Pre-reg: preregs/2026-05-24_wave14e_betB_ewc_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

VOCAB = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
RELU_B = 0.5
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4

# Smoke-vs-full split
N_FULL = 4096
N_SMOKE = 512
EPOCHS_FULL = 5
EPOCHS_SMOKE = 2
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 2
BYTES_FULL = 200_000
BYTES_SMOKE = 4_000
BATCH_FULL = 64
BATCH_SMOKE = 32
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_RETR = 0.3
POOL_SIZE = 1024
REPLAY_FRAC = 0.50

# EWC sweep
LAMBDAS_FULL = [0.0, 0.001, 0.01, 0.1]
LAMBDAS_SMOKE = [0.0, 0.01]

PASS_RETENTION_A = 0.80
HARD_FAIL_RETENTION_A = 0.70  # EWC ON should not be worse than this
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


def bytes_to_idx_tensors(data, device):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + data
    T = len(padded) - K
    byts = torch.tensor(list(padded), dtype=torch.long, device=device)
    offsets = torch.arange(K - 1, -1, -1, device=device)
    pos = torch.arange(T, device=device)
    return byts[pos.unsqueeze(1) + offsets.unsqueeze(0)], byts[pos + K]


def fisher_diagonal_W(W, byte_atoms, pos_atoms, train_idx, train_tgt,
                       batch_size, device, n_samples=256):
    """Estimate Fisher diagonal F_ij = E[(d log p(target | ctx) / d W_ij)^2].

    For the substrate, log p(target | ctx) involves softmax(BETA * sims)
    where sims = (byte_atoms @ q.T)/N and q = shifted_relu(ctxs @ W.T - RELU_B).
    The gradient w.r.t. W_ij is:
      d log p_t / d W_ij = (1/N) * (byte_atoms[t,i] - sum_b p_b * byte_atoms[b,i]) * mask_i * ctxs[j]
    where mask_i = (q_i > 0). We estimate F by averaging squared gradient over
    n_samples random batches.

    Returns F: (N, N) Fisher diagonal tensor.
    """
    N = W.shape[0]
    F = torch.zeros((N, N), dtype=torch.float32, device=device)
    T = train_idx.shape[0]
    n_batches = max(1, n_samples // batch_size)
    perm = torch.randperm(T, device=device)[:n_samples]
    for bi in range(n_batches):
        start = bi * batch_size
        end = min(start + batch_size, n_samples)
        idx_batch = train_idx[perm[start:end]]
        tgt_batch = train_tgt[perm[start:end]]
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
        with torch.no_grad():
            q_pre = ctxs @ W.T
            q = pa.shifted_relu(q_pre, RELU_B)
            mask = (q_pre - RELU_B > 0).float()  # (B, N)
            sims = (byte_atoms @ q.T) / N
            P = torch.softmax(BETA * sims, dim=0)  # (V, B)
            # residual_i for each batch element b: byte_atoms[tgt_b, i] - sum_v P[v,b] * byte_atoms[v, i]
            target_atoms = byte_atoms[tgt_batch]  # (B, N)
            predicted = (P.T @ byte_atoms)  # (B, N)
            residual = (target_atoms - predicted) / N  # (B, N)
            # Effective gradient_ij = residual[b, i] * mask[b, i] * ctxs[b, j]
            eff = residual * mask  # (B, N)
            # F_ij accumulates over batch: sum_b (eff[b,i] * ctxs[b,j])^2
            # = sum_b eff[b,i]^2 * ctxs[b,j]^2 + cross terms (which average to zero)
            # We compute it directly as outer-product squared, accumulated.
            for b in range(eff.shape[0]):
                grad_b = torch.outer(eff[b], ctxs[b])
                F.add_(grad_b * grad_b)
    F.div_(max(n_samples, 1))
    return F


def train_w_with_replay_ewc(W_init, W_anchor, F_diag, lam, pool_vecs,
                              pool_labels, pool_used, byte_atoms, pos_atoms,
                              train_bytes, target_bytes, replay_pool_vecs,
                              replay_pool_labels, replay_pool_used, n_epochs,
                              batch_size, device):
    """Same as pa.train_w_with_replay, plus EWC pull-back."""
    W = W_init.clone().to(device)
    if pool_vecs is None:
        N_local = W.shape[0]
        pool_vecs = torch.zeros((POOL_SIZE, N_local), dtype=torch.float32, device=device)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=device)
    else:
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
    for epoch in range(n_epochs):
        for batch_start in range(0, T, batch_size):
            be = min(batch_start + batch_size, T)
            idx_batch = train_bytes[batch_start:be]
            tgt_batch = target_bytes[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)

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
                # EWC pull-back toward W_anchor weighted by F
                if W_anchor is not None and F_diag is not None and lam > 0:
                    ewc_pull = F_diag * (W - W_anchor)
                    W.add_(ewc_pull, alpha=-lam)
                W.mul_(1.0 - DELTA_DECAY)
                W.add_(dW, alpha=DELTA_ALPHA)
                if epoch == 0:
                    take = min(B, batch_size)
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


def load_corpus_C(smoke):
    exp_dir = REPO / "experiments"
    parts = []
    n_files = 3 if smoke else 12
    for f in sorted(exp_dir.glob("exp_wave14b*.py"))[:n_files]:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def run_one_seed(seed, config, device):
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    lambdas = config["lambdas"]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]
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

    # Phase A (shared across lambdas)
    W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_replay_ewc(
        W_zero, None, None, 0.0, None, None, 0,
        byte_atoms, pos_atoms, train_a_idx, train_a_tgt,
        None, None, 0, phase_a_epochs, batch_size, device)
    bpc_A_baseline = evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                    byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                    batch_size, device)
    bpc_zero_on_C = evaluate_bpc(W_zero, None, None, 0, byte_atoms, pos_atoms,
                                  test_c_idx, test_c_tgt, batch_size, device)

    # Fisher diagonal (computed once on Phase A; reused across lambdas)
    F = fisher_diagonal_W(W_A, byte_atoms, pos_atoms, train_a_idx, train_a_tgt,
                            batch_size, device,
                            n_samples=128 if config["mode"] == "smoke" else 512)
    F_max = float(F.max())
    F_mean = float(F.mean())

    results_by_lambda = {}
    for lam in lambdas:
        # Phase B with EWC pull toward W_A
        W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_replay_ewc(
            W_A, W_A, F, lam, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
            byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
            pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)
        bpc_B_baseline = evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                        byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                        batch_size, device)
        # Phase C with EWC pull toward W_A (still)
        combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
        combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
        W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_replay_ewc(
            W_AB, W_A, F, lam, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
            byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
            combined_v, combined_l, combined_v.shape[0], n_epochs, batch_size, device)
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
        retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
        retention_B = min(bpc_B_baseline / max(bpc_B_after_C, 1e-6), 1.0)
        gain_C = bpc_zero_on_C - bpc_C_after_C
        bwt = bpc_A_after_B - bpc_A_after_C
        results_by_lambda[str(lam)] = {
            "lambda": lam,
            "retention_A": retention_A,
            "retention_B": retention_B,
            "gain_C": gain_C,
            "bwt": bwt,
            "bpc_A_baseline": bpc_A_baseline,
            "bpc_A_after_C": bpc_A_after_C,
            "bpc_B_baseline": bpc_B_baseline,
            "bpc_B_after_C": bpc_B_after_C,
            "bpc_zero_on_C": bpc_zero_on_C,
            "bpc_C_after_C": bpc_C_after_C,
        }
    return {
        "by_lambda": results_by_lambda,
        "fisher_max": F_max,
        "fisher_mean": F_mean,
    }


def compute_verdict(summary):
    """Verdict: best lambda with retention_A >= PASS_RETENTION_A and gain_C > 0
    is a PASS. EWC ON below HARD_FAIL is a kill (worse than no-EWC).
    """
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("BET_B_EWC_INCONCLUSIVE", "Missing per-seed.")
    # Aggregate per-lambda retention_A across seeds
    seeds = list(per_seed.values())
    lambdas = list(seeds[0]["by_lambda"].keys())
    agg = {}
    for lam in lambdas:
        rA = sum(s["by_lambda"][lam]["retention_A"] for s in seeds) / len(seeds)
        rB = sum(s["by_lambda"][lam]["retention_B"] for s in seeds) / len(seeds)
        gC = sum(s["by_lambda"][lam]["gain_C"] for s in seeds) / len(seeds)
        bwt = sum(s["by_lambda"][lam]["bwt"] for s in seeds) / len(seeds)
        agg[lam] = {"retention_A": rA, "retention_B": rB, "gain_C": gC, "bwt": bwt}
    # Best non-zero lambda by retention_A
    nonzero = [lam for lam in lambdas if float(lam) > 0]
    if not nonzero:
        return ("BET_B_EWC_INCONCLUSIVE", "No nonzero lambda tested.")
    best_lam = max(nonzero, key=lambda lam: agg[lam]["retention_A"])
    best = agg[best_lam]
    # Hard-fail
    if best["retention_A"] < HARD_FAIL_RETENTION_A:
        return ("BET_B_EWC_KILLED",
                f"EWC at best lambda {best_lam}: retention_A={best['retention_A']:.3f} "
                f"< HARD_FAIL {HARD_FAIL_RETENTION_A}. Worse than no-EWC baseline ~0.73.")
    # Hard-pass
    if best["retention_A"] >= PASS_RETENTION_A and best["gain_C"] > 0:
        return ("BET_B_EWC_PASS",
                f"EWC LIFTS Bet B. best lambda={best_lam}: retention_A={best['retention_A']:.3f} "
                f">= {PASS_RETENTION_A}, retention_B={best['retention_B']:.3f}, "
                f"gain_C={best['gain_C']:.4f}>0, bwt={best['bwt']:+.4f}.")
    # Middle band: improves over zero lambda but not to pass
    zero = agg["0.0"] if "0.0" in agg else None
    if zero is not None and best["retention_A"] > zero["retention_A"] + 0.02:
        return ("BET_B_EWC_PARTIAL",
                f"EWC improves but does not clear {PASS_RETENTION_A}. "
                f"best lambda={best_lam}: retention_A={best['retention_A']:.3f} "
                f"(vs lambda=0: {zero['retention_A']:.3f}), gain_C={best['gain_C']:.4f}.")
    return ("BET_B_EWC_INCONCLUSIVE",
            f"EWC ON: retention_A={best['retention_A']:.3f}, gain_C={best['gain_C']:.4f}, "
            f"bwt={best['bwt']:+.4f}. No clear lift over lambda=0.")


def self_test_verdict():
    def mk(by_lam):
        return {"per_seed": {"17": {"by_lambda": by_lam}}}
    cases = [
        # PASS
        (mk({"0.0": {"retention_A": 0.72, "retention_B": 0.70, "gain_C": 0.3, "bwt": -0.01},
              "0.01": {"retention_A": 0.85, "retention_B": 0.82, "gain_C": 0.25, "bwt": 0.01}}),
         "BET_B_EWC_PASS"),
        # KILLED (best lambda worse than 0.70)
        (mk({"0.0": {"retention_A": 0.72, "retention_B": 0.70, "gain_C": 0.3, "bwt": -0.01},
              "0.01": {"retention_A": 0.60, "retention_B": 0.50, "gain_C": 0.20, "bwt": -0.10}}),
         "BET_B_EWC_KILLED"),
        # PARTIAL
        (mk({"0.0": {"retention_A": 0.72, "retention_B": 0.70, "gain_C": 0.3, "bwt": -0.01},
              "0.01": {"retention_A": 0.78, "retention_B": 0.75, "gain_C": 0.22, "bwt": -0.005}}),
         "BET_B_EWC_PARTIAL"),
        # INCONCLUSIVE
        (mk({"0.0": {"retention_A": 0.72, "retention_B": 0.70, "gain_C": 0.3, "bwt": -0.01},
              "0.01": {"retention_A": 0.73, "retention_B": 0.70, "gain_C": 0.30, "bwt": -0.005}}),
         "BET_B_EWC_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SMOKE if smoke else BATCH_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "lambdas": LAMBDAS_SMOKE if smoke else LAMBDAS_FULL,
        "replay_frac": REPLAY_FRAC,
    }
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: fisher_mean={r['fisher_mean']:.2e} "
              f"fisher_max={r['fisher_max']:.2e}", flush=True)
        for lam, ed in r["by_lambda"].items():
            print(f"    lambda={lam}: retA={ed['retention_A']:.3f} "
                  f"retB={ed['retention_B']:.3f} gainC={ed['gain_C']:.4f}", flush=True)
    summary = {"per_seed": per_seed}
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
    out_dir = get_output_dir("wave14e_betB_ewc_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Basic sanity assertion: at least one lambda produced a non-NaN retention
    seed_key = list(summary["per_seed"].keys())[0]
    by_lam = summary["per_seed"][seed_key]["by_lambda"]
    assert any(ed["retention_A"] > 0.0 for ed in by_lam.values()), \
        "all retention_A == 0 -- mechanism failed catastrophically"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14e_betB_ewc_smoke_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
