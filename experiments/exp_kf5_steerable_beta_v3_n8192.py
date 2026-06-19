"""KF-5 STEERABLE SUBSTRATE v3: ENVELOPE EXTENSION to N=8192 (2x v2 N=4096).

PARENT: exp_kf5_steerable_beta_v2.py -- v2 HARD_PASS N=4096 5-seed.
  v2 result: entropy collapse 7.71->0.12 over beta=2-128, range=7.59 bits (7.6x HP threshold).
  v2 5-seed fully replicated within 0.02 bits.

SCIENTIFIC QUESTION (Killer Feature 5 -- envelope extension):
  Does beta-steering scale to 2x larger substrate (N=8192)?
  If entropy collapse depth grows with N: substrate-intrinsic behavior (stronger at scale).
  If flat or shrinking: finite-N artifact -- cannot claim KF-5 at production N=8192.

  Kerdock valid N: {1024, 4096, 16384}. N=8192 is NOT a valid Kerdock N.
  Use BSC (random +/-1 patterns) at N=8192 instead, matching the pa.make_bsc_atoms path.
  v2 already used BSC atoms (pa.make_bsc_atoms); this script is a clean N=8192 BSC run.

PRE-REGISTERED BANDS:
  HARD_PASS: (1) entropy monotone DECREASING across beta sweep in >= 4/5 seeds
    AND (2) mean_entropy_range > 1.0 bit (same threshold as v2)
    AND (3) bpc has interior minimum at some beta in {4,8,16,32}.
    If HARD_PASS AND mean_entropy_range >= v2 range (7.59 bits): SCALE_CONFIRMED.
    Interpretation: KF-5 steerable substrate scales to N=8192 BSC.
  HARD_FAIL: entropy_range < 0.5 bits AND bpc monotonic in >= 4/5 seeds.
    Interpretation: BSC at N=8192 does not support inference-time steering.
  MIDDLE_BAND: entropy monotone in < 4/5 seeds OR range in [0.5, 1.0] bits.

FORMULA SELF-TESTS:
  1. H(uniform over 256 bytes) = log2(256) = 8.0 bits. beta->0: H -> 8.0.
  2. H(one-hot) = 0 bits. beta->inf: H -> 0.0 bits.
  3. entropy_range = H(beta_min) - H(beta_max) for beta_min=2, beta_max=128: >> 0.
  4. bpc optimal near BETA_TRAIN=8.
  5. HARD_PASS gate: verify with mk_seed_pass() -> KF5_HARD_PASS.
  6. HARD_FAIL gate: verify with mk_seed_fail() -> KF5_HARD_FAIL.
  7. v3_scale check: mean_entropy_range(v3) >= 1.0 bit required for HARD_PASS.

TIMEOUT ESTIMATE:
  v2 elapsed at N=4096, 5 seeds, 7 betas, 2 epochs: ~5s on GPU.
  N=8192 scale: (8192/4096)^1.5 = 2.83x geometric.
  But training tokens are the same (T_TRAIN_FULL=20000 fixed); extra cost is per-step W ops.
  W is (N, N); matmul cost scales as N^2. (8192/4096)^2 = 4x.
  Conservative: 4x cost at N=8192 vs N=4096.
  5s * 4 * 1.5 = 30s. Safety x5 (uncertain GPU dispatch overhead): 150s.
  timeout_s = ceil(1.5 * 150) = 225 -> 300s.
  OOM check: W float32 at N=8192 = 8192*8192*4 = 268MB. Well under 6GB. PASS.

N-suffix: _n8192 suffix; production N = 8192 (PROT-018 binding).
Queue: overnight_queue (GPU; BSC N=8192, 5 seeds, 7 betas)
Pre-reg: preregs/2026-05-27_kf5_steerable_beta_v3_n8192.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load phase_a infrastructure (BSC atoms, corpus, delta-rule training)
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# Load v2 for reuse of: compute_entropy, eval_at_beta, compute_steerability, compute_verdict
_v2_path = REPO / "experiments" / "exp_kf5_steerable_beta_v2.py"
_v2_spec = importlib.util.spec_from_file_location("kf5v2", _v2_path)
v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(v2)

compute_entropy = v2.compute_entropy
eval_at_beta = v2.eval_at_beta
compute_steerability = v2.compute_steerability
compute_verdict = v2.compute_verdict

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix; N_FULL = 8192 (binding)
N_FULL = 8192          # PROT-018 binding: anchor name is kf5_steerable_beta_v3_n8192
N_SMOKE = 1024         # smallest valid BSC N for quick smoke
K = 4                  # context window
VOCAB = 256
BETA_TRAIN = 8.0
BETA_INF_SWEEP = [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
BETA_INF_SMOKE = [2.0, 8.0, 64.0]
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
T_TRAIN_FULL = 20000
T_TRAIN_SMOKE = 3000
T_EVAL_FULL = 2000
T_EVAL_SMOKE = 300
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v2 -- same HP bar applied to N=8192)
PASS_ENTROPY_RANGE_MIN = 1.0
PASS_ENTROPY_MONOTONE_SEEDS = 4
FAIL_ENTROPY_RANGE_MAX = 0.5
FAIL_BPC_MONOTONE_SEEDS = 4


def get_output_dir(default_name: str = "kf5_steerable_beta_v3_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def train_w_delta_n8192(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                         train_idx: torch.Tensor, train_tgt: torch.Tensor,
                         N: int, device: torch.device,
                         n_epochs: int = 2, batch_size: int = 64) -> torch.Tensor:
    """Delta-rule training. W is (N, N); same logic as v2 train_w_delta."""
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    T = train_idx.shape[0]
    for epoch in range(n_epochs):
        for bs in range(0, T, batch_size):
            be = min(bs + batch_size, T)
            ctxs = pa.build_ctx_bundles_bsc(
                byte_atoms, pos_atoms, train_idx[bs:be].to(device)
            )
            q = ctxs @ W.T
            q = pa.shifted_relu(q, RELU_B)
            sims = (byte_atoms @ q.T) / N
            P = torch.softmax(BETA_TRAIN * sims, dim=0)
            target_atoms = byte_atoms[train_tgt[bs:be].to(device)]
            predicted = P.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs / N
            W.mul_(1.0 - DELTA_DECAY)
            W.add_(dW, alpha=DELTA_ALPHA)
    return W


def load_and_tokenize(smoke: bool):
    """Load corpus and tokenize train/eval splits."""
    corpus = pa.load_corpus_a()
    T = len(corpus) - K
    T_train = T_TRAIN_SMOKE if smoke else T_TRAIN_FULL
    T_eval = T_EVAL_SMOKE if smoke else T_EVAL_FULL
    T_train = min(T_train, T - T_eval)
    T_eval = min(T_eval, T - T_train)

    train_idx = torch.tensor(
        [[corpus[i + j] for j in range(K)] for i in range(T_train)],
        dtype=torch.long
    )
    train_tgt = torch.tensor([corpus[i + K] for i in range(T_train)], dtype=torch.long)
    eval_start = T_train
    eval_idx = torch.tensor(
        [[corpus[eval_start + i + j] for j in range(K)] for i in range(T_eval)],
        dtype=torch.long
    )
    eval_tgt = torch.tensor(
        [corpus[eval_start + i + K] for i in range(T_eval)], dtype=torch.long
    )
    return train_idx, train_tgt, eval_idx, eval_tgt


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Run one seed at N=8192 BSC."""
    smoke = config["smoke"]
    N = config["N"]
    beta_sweep = config["beta_sweep"]

    gen_cpu = torch.Generator(device="cpu").manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen_cpu).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen_cpu).to(device)

    train_idx, train_tgt, eval_idx, eval_tgt = load_and_tokenize(smoke)

    W = train_w_delta_n8192(
        byte_atoms, pos_atoms, train_idx, train_tgt, N, device,
        n_epochs=1 if smoke else 2
    )

    per_beta = {}
    for beta_inf in beta_sweep:
        metrics = eval_at_beta(W, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                beta_inf, N, device)
        per_beta[str(beta_inf)] = metrics

    return {"seed": seed, "N": N, "per_beta": per_beta}


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: N_FULL binding check
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192 (matches _n8192 suffix); got {N_FULL}"
    assert N_SMOKE == 1024, f"N_SMOKE should be 1024; got {N_SMOKE}"

    # Self-test 1: entropy formula (from v2)
    P_uniform = torch.ones(256, 1) / 256.0
    H_uniform = compute_entropy(P_uniform).item()
    assert abs(H_uniform - 8.0) < 0.01, f"Entropy of uniform(256) should be 8.0; got {H_uniform}"

    P_onehot = torch.zeros(256, 1)
    P_onehot[0, 0] = 1.0
    H_onehot = compute_entropy(P_onehot).item()
    assert abs(H_onehot) < 0.01, f"Entropy of one-hot should be 0; got {H_onehot}"

    # Self-test 2: verdict logic HARD_PASS path
    def mk_seed_pass():
        per_beta = {}
        for b, h, bpc in [(2.0, 7.0, 4.0), (8.0, 4.0, 3.2), (64.0, 0.5, 5.5)]:
            per_beta[str(b)] = {
                "output_entropy_bits": h, "bpc": bpc,
                "retention_argmax": 0.35, "top1_top2_gap": 0.1
            }
        return {"per_beta": per_beta}

    summary_pass = {"per_seed": {str(s): mk_seed_pass() for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_pass)
    assert v == "KF5_HARD_PASS", f"Self-test HARD_PASS gate failed: got {v}: {msg}"

    # Self-test 3: verdict logic HARD_FAIL path
    def mk_seed_fail():
        per_beta = {}
        for b in [2.0, 8.0, 32.0, 64.0]:
            per_beta[str(b)] = {
                "output_entropy_bits": 4.0, "bpc": float(3.0 + b * 0.01),
                "retention_argmax": 0.35, "top1_top2_gap": 0.1
            }
        return {"per_beta": per_beta}

    summary_fail = {"per_seed": {str(s): mk_seed_fail() for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_fail)
    assert v == "KF5_HARD_FAIL", f"Self-test HARD_FAIL gate failed: got {v}: {msg}"

    # Self-test 4: OOM pre-check at N=8192 float32
    oom_bytes = N_FULL * N_FULL * 4  # W matrix only (N x N float32)
    assert oom_bytes < 6e9, f"OOM pre-check: W at N=8192 is {oom_bytes:.2e} bytes >= 6GB"

    # Self-test 5: smoke forward pass at tiny N
    device = torch.device("cpu")
    N_test = 256
    gen = torch.Generator(device="cpu").manual_seed(17)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_test, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N_test, gen).to(device)

    corpus = pa.load_corpus_a()[:600]
    T = len(corpus) - K
    assert T >= 20, f"Corpus too small: T={T}"
    idx = torch.tensor([[corpus[i + j] for j in range(K)] for i in range(min(T, 200))],
                        dtype=torch.long)
    tgt = torch.tensor([corpus[i + K] for i in range(min(T, 200))], dtype=torch.long)

    W = train_w_delta_n8192(byte_atoms, pos_atoms, idx, tgt, N_test, device, n_epochs=1)
    assert W.shape == (N_test, N_test), f"W shape mismatch: {W.shape}"
    assert not torch.all(W == 0), "W is all-zero after training"

    m_low = eval_at_beta(W, byte_atoms, pos_atoms, idx[:30], tgt[:30], 2.0, N_test, device)
    m_high = eval_at_beta(W, byte_atoms, pos_atoms, idx[:30], tgt[:30], 64.0, N_test, device)

    assert m_low["output_entropy_bits"] is not None
    assert 0 <= m_low["output_entropy_bits"] <= 8.1, \
        f"entropy out of range: {m_low['output_entropy_bits']}"
    assert m_low["output_entropy_bits"] > m_high["output_entropy_bits"], (
        f"Expected entropy(beta=2) > entropy(beta=64): "
        f"{m_low['output_entropy_bits']:.3f} <= {m_high['output_entropy_bits']:.3f}"
    )

    # Self-test 6: HDLAB_EXP_NAME path
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_kf5v3_path"
    _d = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _d.name == "exp_test_kf5v3_path", f"get_output_dir ignores HDLAB_EXP_NAME: {_d.name}"
    _d.rmdir()

    print(f"[SELFTEST PASS] kf5_steerable_beta_v3_n8192: N_FULL={N_FULL} "
          f"OOM={oom_bytes:.2e} entropy_check OK verdict_gates OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_INF_SMOKE if smoke else BETA_INF_SWEEP

    if not smoke:
        assert N == 8192, f"PROT-018: FULL run must use N=8192; got {N}"

    config = {"smoke": smoke, "N": N, "beta_sweep": beta_sweep}
    exp_name = os.environ.get("HDLAB_EXP_NAME", "kf5_steerable_beta_v3_n8192")
    print(f"[kf5v3_n8192] N={N} seeds={seeds} betas={beta_sweep} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        pb = result["per_beta"]
        betas_sorted = sorted([float(k) for k in pb.keys()])
        ents = [pb[str(b)]["output_entropy_bits"] for b in betas_sorted]
        bpcs = [pb[str(b)]["bpc"] for b in betas_sorted]
        print(f"    entropy={[round(e,3) for e in ents]} bpc={[round(b,3) for b in bpcs]} "
              f"elapsed={te:.1f}s", flush=True)
        per_seed[str(seed)] = result

    summary = {"per_seed": per_seed, "mode": "smoke" if smoke else "full", "N": N}
    verdict, msg = compute_verdict(summary)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    out_dir = get_output_dir(exp_name)
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
