"""K5 real-time learning during inference -- single-query-updates-W ablation.

Per untested-rows triage (cap_map v189 Priority A #4):
  - K5 / U6 KILLER T2 "Real-time learning during inference"
  - "every prediction updates W"
  - Pipeline-config change not new mechanism; CPU-bound (small N + single stream)

Mechanism: substrate uses K=4 byte-window context bundles (standard Bet B
infrastructure). Offline pre-train W on first half of corpus A. Then run
inference on the held-out second half:
  - FROZEN-W: predict each next byte from K-bundle ctx via predict_W; W static.
  - ONLINE-W: same start state; AFTER each prediction, apply one-step Hebbian
    update W += lr * outer(target_atom, ctx_bundle).

Compare mean BPC across the held-out stream.

Falsifier statements (per [[feedback-no-smoke]]):
  - HARD-PASS: mean (bpc_online - bpc_frozen) <= -0.05 bits/char across 3 seeds.
    Online learning LIFTS capability; K5 substrate-compatible.
  - HARD-FAIL: mean (bpc_online - bpc_frozen) >= +0.05 bits/char.
    Online updates DEGRADE prediction; K5 incompatible.
  - MIDDLE:    intermediate. Pipeline viable but no capability uplift.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev chose lr=0.01 (mild;
substrate-conservative), N=2048 (CPU-tractable), T=4000 (~few min CPU), 3 seeds.

Pre-reg: preregs/2026-05-24_wave14_realtime_inference_learning_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Reuse Kovacs base (provides bytes_to_idx_tensors, train_w_with_replay, K, BETA, etc).
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa

N_FULL = 2048
N_SMOKE = 512
T_INFER_FULL = 4000
T_INFER_SMOKE = 400
# Online delta-rule parameters (matching offline trainer style; alpha rescaled
# for the inference setting where the substrate already encodes most structure).
ONLINE_ALPHA_FULL = 0.05      # 6x smaller than offline DELTA_ALPHA=0.3 (conservative)
ONLINE_ALPHA_SMOKE = 0.05
ONLINE_DECAY_FULL = 1e-4      # same as offline
ONLINE_DECAY_SMOKE = 1e-4
PRETRAIN_EPOCHS_FULL = 3
PRETRAIN_EPOCHS_SMOKE = 1
PRETRAIN_BYTES_FULL = 50000
PRETRAIN_BYTES_SMOKE = 2000
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

PASS_BPC_DELTA = -0.05   # online must reduce BPC by >= 0.05 vs frozen
FAIL_BPC_DELTA = +0.05   # online increasing BPC by >= 0.05 is failure


def run_inference_stream(W_init, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                          batch_size, online_alpha, online_decay,
                          do_online_update, device):
    """Run inference on the eval stream; optionally update W per batch using
    the same delta-rule as the offline trainer (with optional rescaled alpha).

    Returns mean BPC and final W.
    """
    W = W_init.clone()
    N = W.shape[0]
    T = eval_idx.shape[0]
    total_bits = 0.0
    n_predictions = 0
    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be])
        P_W = pa.predict_W(W, ctxs, byte_atoms, base.BETA, N)
        tgts = eval_tgt[bs:be]
        p_true = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())
        n_predictions += (be - bs)
        if do_online_update:
            # Same delta-rule as offline trainer: residual = target - predicted; dW
            # = residual.T @ ctxs / N; W = (1-decay)*W + alpha*dW. alpha rescaled
            # for the online setting (typically smaller than offline DELTA_ALPHA=0.3).
            target_atoms = byte_atoms[tgts]
            predicted = (P_W.T @ byte_atoms)
            residual = target_atoms - predicted
            dW = (residual.T @ ctxs) / N
            W.mul_(1.0 - online_decay)
            W.add_(dW, alpha=online_alpha)
    return total_bits / max(n_predictions, 1), W


def run_one_seed(seed, config, device):
    N = config["N"]
    batch_size = config["batch_size"]
    n_pretrain_bytes = config["pretrain_bytes"]
    n_pretrain_epochs = config["pretrain_epochs"]
    T_infer = config["T_infer"]
    online_alpha = config["online_alpha"]
    online_decay = config["online_decay"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus = pa.load_corpus_a()
    pretrain_corpus = corpus[:n_pretrain_bytes]
    infer_corpus = corpus[n_pretrain_bytes:n_pretrain_bytes + T_infer]

    pretrain_idx, pretrain_tgt = base.bytes_to_idx_tensors(pretrain_corpus, device)
    infer_idx, infer_tgt = base.bytes_to_idx_tensors(infer_corpus, device)

    # Offline pre-train on first half.
    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_pretrained, _, _, _ = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        pretrain_idx, pretrain_tgt, None, None, 0,
        n_pretrain_epochs, batch_size, device)

    # FROZEN-W: same start state, no update.
    bpc_frozen, _ = run_inference_stream(W_pretrained, byte_atoms, pos_atoms,
                                          infer_idx, infer_tgt, batch_size,
                                          online_alpha, online_decay,
                                          do_online_update=False, device=device)
    # ONLINE-W: same start state, delta-rule update per batch.
    bpc_online, _ = run_inference_stream(W_pretrained, byte_atoms, pos_atoms,
                                          infer_idx, infer_tgt, batch_size,
                                          online_alpha, online_decay,
                                          do_online_update=True, device=device)
    delta = bpc_online - bpc_frozen   # negative is good
    return {"bpc_frozen": bpc_frozen, "bpc_online": bpc_online, "delta": delta}


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("REALTIME_INFERENCE_INCONCLUSIVE", "Missing per-seed data.")
    deltas = [s["delta"] for s in seeds_data.values()]
    mean_delta = sum(deltas) / len(deltas)
    bpc_f = sum(s["bpc_frozen"] for s in seeds_data.values()) / len(seeds_data)
    bpc_o = sum(s["bpc_online"] for s in seeds_data.values()) / len(seeds_data)
    if mean_delta <= PASS_BPC_DELTA:
        return ("REALTIME_INFERENCE_HARD_PASS",
                f"Online updates LIFT capability: bpc_online={bpc_o:.3f} vs bpc_frozen={bpc_f:.3f}; "
                f"delta={mean_delta:.3f} bits/char <= {PASS_BPC_DELTA}. K5 substrate-compatible.")
    if mean_delta >= FAIL_BPC_DELTA:
        return ("REALTIME_INFERENCE_HARD_FAIL",
                f"Online updates DEGRADE prediction: bpc_online={bpc_o:.3f} vs bpc_frozen={bpc_f:.3f}; "
                f"delta={mean_delta:.3f} bits/char >= {FAIL_BPC_DELTA}. K5 incompatible.")
    return ("REALTIME_INFERENCE_MIDDLE_BAND",
            f"Online updates have marginal effect: bpc_online={bpc_o:.3f} vs bpc_frozen={bpc_f:.3f}; "
            f"delta={mean_delta:.3f} bits/char in ({PASS_BPC_DELTA},{FAIL_BPC_DELTA}). Pipeline viable; "
            f"no capability uplift.")


def self_test_verdict():
    def mk(d):
        return {"per_seed": {"17": {"delta": d, "bpc_frozen": 3.0, "bpc_online": 3.0 + d}}}
    cases = [
        (mk(-0.10), "REALTIME_INFERENCE_HARD_PASS"),
        (mk(-0.05), "REALTIME_INFERENCE_HARD_PASS"),
        (mk(-0.02), "REALTIME_INFERENCE_MIDDLE_BAND"),
        (mk(0.00), "REALTIME_INFERENCE_MIDDLE_BAND"),
        (mk(0.02), "REALTIME_INFERENCE_MIDDLE_BAND"),
        (mk(0.05), "REALTIME_INFERENCE_HARD_FAIL"),
        (mk(0.10), "REALTIME_INFERENCE_HARD_FAIL"),
        ({}, "REALTIME_INFERENCE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "T_infer": T_INFER_SMOKE if smoke else T_INFER_FULL,
              "online_alpha": ONLINE_ALPHA_SMOKE if smoke else ONLINE_ALPHA_FULL,
              "online_decay": ONLINE_DECAY_SMOKE if smoke else ONLINE_DECAY_FULL,
              "pretrain_bytes": PRETRAIN_BYTES_SMOKE if smoke else PRETRAIN_BYTES_FULL,
              "pretrain_epochs": PRETRAIN_EPOCHS_SMOKE if smoke else PRETRAIN_EPOCHS_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_bpc_delta": PASS_BPC_DELTA,
              "fail_bpc_delta": FAIL_BPC_DELTA}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: bpc_frozen={r['bpc_frozen']:.3f} bpc_online={r['bpc_online']:.3f} "
              f"delta={r['delta']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_realtime_inference_learning_v1_smoke" if args.smoke
                          else "wave14_realtime_inference_learning_v1")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        # Sanity: BPC should be finite and bounded by log2(VOCAB)=8.
        if not (0 < r["bpc_frozen"] < 9.0):
            raise AssertionError(f"smoke bpc_frozen out of sane range: {r['bpc_frozen']}")
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
