"""K5 real-time learning during inference -- v1 INSTRUMENTATION REPAIR rerun.

Per v190 cap_map V10 LABEL-OVER-CLAIM detection:
  - v1 FULL reported bpc_online=0.000 / bpc_frozen=0.000 / delta=0.000
  - Root cause: pretrain_bytes=50000 + T_infer=4000 = 54000 needed but
    corpus_a length is only 48512 -> infer_corpus is empty -> n_predictions=0
    -> bpc = 0.0 / max(0,1) = 0.0 across all 3 seeds; metric collapse not
    a substrate-capability reading.

This rerun caps pretrain_bytes so the held-out stream is genuinely populated.
Also adds a hard assertion that infer_idx is non-empty before running, so the
instrumentation-bug class fails LOUDLY (assertion) instead of silently (zero
metric) in any future similar misconfig.

Mechanism unchanged from v1: offline pre-train W on a slice of corpus A,
then run inference on a held-out slice with two W variants (frozen vs online
delta-rule update per batch). Compare mean BPC.

Pre-reg falsifier statements (unchanged from v1):

  - HARD-PASS:  mean (bpc_online - bpc_frozen) <= -0.05 bits/char across 3 seeds.
                Online learning LIFTS capability; K5 substrate-compatible.
  - HARD-FAIL:  mean (bpc_online - bpc_frozen) >= +0.05 bits/char.
                Online updates DEGRADE prediction; K5 incompatible.
  - MIDDLE:     intermediate. Pipeline viable but no capability uplift.

Per [[feedback-no-smoke]]: bands falsifiable BEFORE running.
Per [[feedback-verdict-msg-honest-reread]]: v190 V10 labeled-vs-honest entry
flagged this instrumentation bug; this rerun resolves it. K5 row STAYS ⚪
until this rerun produces a real reading.

Pre-reg: preregs/2026-05-24_wave14_realtime_inference_learning_v1_rerun.md
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

# Load v1 module to reuse run_inference_stream, compute_verdict, write_metrics.
_v1_path = REPO / "experiments" / "exp_wave14_realtime_inference_learning_v1.py"
_spec = importlib.util.spec_from_file_location("k5base", _v1_path)
k5base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(k5base)
base = k5base.base
pa = k5base.pa

# v1 had pretrain_bytes=50000 + T_infer=4000 -> 54000 needed; corpus is 48512.
# Repair: cap pretrain to leave room for T_infer + safety margin (200 bytes).
N_FULL = 2048
N_SMOKE = 512
T_INFER_FULL = 4000
T_INFER_SMOKE = 400
ONLINE_ALPHA_FULL = 0.05
ONLINE_ALPHA_SMOKE = 0.05
ONLINE_DECAY_FULL = 1e-4
ONLINE_DECAY_SMOKE = 1e-4
PRETRAIN_EPOCHS_FULL = 3
PRETRAIN_EPOCHS_SMOKE = 1
# CAPPED pretrain_bytes -- determined from corpus length at runtime to GUARANTEE
# infer_corpus is non-empty. Fallback if corpus is shorter than expected:
# pretrain_bytes = len(corpus) - T_infer - 200.
PRETRAIN_BYTES_FULL_TARGET = 40000   # was 50000 in v1; explicit cap
PRETRAIN_BYTES_SMOKE_TARGET = 2000
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

PASS_BPC_DELTA = k5base.PASS_BPC_DELTA
FAIL_BPC_DELTA = k5base.FAIL_BPC_DELTA


def _compute_safe_pretrain_bytes(corpus_len, requested_pretrain, t_infer, safety=200):
    """Cap pretrain_bytes so corpus_len - pretrain_bytes >= t_infer + safety."""
    max_pretrain = corpus_len - t_infer - safety
    if max_pretrain <= 0:
        raise AssertionError(
            f"corpus_len={corpus_len} too small for t_infer={t_infer} + safety={safety}; "
            f"need len > {t_infer + safety}")
    return min(requested_pretrain, max_pretrain)


def run_one_seed(seed, config, device):
    """Same as v1 base.run_one_seed but with hard assertion on infer corpus."""
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
    # HARD ASSERT (instrumentation guard): corpus must have enough bytes for
    # both phases. This is the bug v1 silently hit -> v190 V10 LABEL-OVER-CLAIM.
    needed = n_pretrain_bytes + T_infer
    assert len(corpus) >= needed, (
        f"corpus length {len(corpus)} insufficient for pretrain={n_pretrain_bytes} + "
        f"T_infer={T_infer} = {needed}. Cap pretrain_bytes below.")
    pretrain_corpus = corpus[:n_pretrain_bytes]
    infer_corpus = corpus[n_pretrain_bytes:n_pretrain_bytes + T_infer]
    assert len(infer_corpus) == T_infer, (
        f"infer_corpus has {len(infer_corpus)} bytes, expected {T_infer}; "
        f"slicing bug between pretrain and inference phases.")

    pretrain_idx, pretrain_tgt = base.bytes_to_idx_tensors(pretrain_corpus, device)
    infer_idx, infer_tgt = base.bytes_to_idx_tensors(infer_corpus, device)
    assert infer_idx.shape[0] > 0, "infer_idx is empty after bytes_to_idx_tensors"

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_pretrained, _, _, _ = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        pretrain_idx, pretrain_tgt, None, None, 0,
        n_pretrain_epochs, batch_size, device)

    bpc_frozen, _ = k5base.run_inference_stream(
        W_pretrained, byte_atoms, pos_atoms, infer_idx, infer_tgt, batch_size,
        online_alpha, online_decay, do_online_update=False, device=device)
    bpc_online, _ = k5base.run_inference_stream(
        W_pretrained, byte_atoms, pos_atoms, infer_idx, infer_tgt, batch_size,
        online_alpha, online_decay, do_online_update=True, device=device)
    # Sanity: both BPCs must be finite and positive (bug guard for v190 V10).
    assert 0.0 < bpc_frozen < 9.0, f"bpc_frozen={bpc_frozen} out of sane range"
    assert 0.0 < bpc_online < 9.0, f"bpc_online={bpc_online} out of sane range"
    delta = bpc_online - bpc_frozen
    return {"bpc_frozen": bpc_frozen, "bpc_online": bpc_online, "delta": delta}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Resolve actual pretrain_bytes against the live corpus to guarantee we
    # do not hit the v1 instrumentation bug a second time.
    corpus_len = len(pa.load_corpus_a())
    requested_pretrain = PRETRAIN_BYTES_SMOKE_TARGET if smoke else PRETRAIN_BYTES_FULL_TARGET
    t_infer = T_INFER_SMOKE if smoke else T_INFER_FULL
    safe_pretrain = _compute_safe_pretrain_bytes(corpus_len, requested_pretrain, t_infer)

    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "T_infer": t_infer,
              "online_alpha": ONLINE_ALPHA_SMOKE if smoke else ONLINE_ALPHA_FULL,
              "online_decay": ONLINE_DECAY_SMOKE if smoke else ONLINE_DECAY_FULL,
              "pretrain_bytes": safe_pretrain,
              "pretrain_bytes_requested": requested_pretrain,
              "corpus_len": corpus_len,
              "pretrain_epochs": PRETRAIN_EPOCHS_SMOKE if smoke else PRETRAIN_EPOCHS_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_bpc_delta": PASS_BPC_DELTA,
              "fail_bpc_delta": FAIL_BPC_DELTA,
              "rerun_reason": "v190 V10 LABEL-OVER-CLAIM instrumentation repair"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: bpc_frozen={r['bpc_frozen']:.3f} bpc_online={r['bpc_online']:.3f} "
              f"delta={r['delta']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = k5base.compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        k5base.self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_realtime_inference_learning_v1_rerun_smoke" if args.smoke
                          else "wave14_realtime_inference_learning_v1_rerun")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    k5base.write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
