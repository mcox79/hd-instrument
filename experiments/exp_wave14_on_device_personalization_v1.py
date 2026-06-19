"""On-device personalization end-to-end — K3 KILLER T2.

Per strategy_untested_rows_triage_2026-05-24.md Priority A #3 K3 KILLER Tier 2.

Tests substrate ability to run the FULL pipeline (Hebbian add + retrieval from
bundle) at consumer-laptop scale on CPU-ONLY. The "on-device personalization"
product spec is: a user-laptop loads a base substrate, runs Hebbian updates on
user data (without GPU / autograd), and retrieves from the resulting bundle.

This is the DEPLOYMENT-TARGET match for the project: local_cpu_runner is
exactly the platform. We test:
  1. End-to-end latency (Hebbian add + retrieval) at N=2048 CPU-only
  2. Retention of base substrate after personalization (small-K user adapt)
  3. Throughput (items / second) for Hebbian add

Pre-reg falsifier statements:

  - HARD-PASS:  add_throughput >= 100 items/s AND retrieval_latency_ms <= 50
                AND retention_A >= 0.70 across 3 seeds. On-device deployment
                viable at consumer-laptop scale.
  - HARD-FAIL:  add_throughput <= 10 items/s OR retrieval_latency_ms >= 500
                OR retention_A <= 0.30. Substrate not viable for on-device
                deployment at this scale.
  - MIDDLE:     intermediate. Pipeline runs but doesn't meet product-grade
                throughput / latency targets.

Per [[feedback-no-smoke]]: falsifiable bands.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only.

Pre-reg: preregs/2026-05-24_wave14_on_device_personalization_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa

N_FULL = 2048
N_SMOKE = 1024
N_USER_ITEMS_FULL = 200
N_USER_ITEMS_SMOKE = 30
N_RETRIEVALS_FULL = 100
N_RETRIEVALS_SMOKE = 20
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

PASS_THROUGHPUT = 100.0  # items/s
PASS_RETRIEVAL_MS = 50.0  # ms per single retrieval
PASS_RET_A = 0.70
FAIL_THROUGHPUT = 10.0
FAIL_RETRIEVAL_MS = 500.0
FAIL_RET_A = 0.30


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("ON_DEVICE_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    thr = sum(s["add_throughput"] for s in seeds) / len(seeds)
    lat = sum(s["retrieval_latency_ms"] for s in seeds) / len(seeds)
    ret = sum(s["retention_A"] for s in seeds) / len(seeds)
    if thr <= FAIL_THROUGHPUT or lat >= FAIL_RETRIEVAL_MS or ret <= FAIL_RET_A:
        return ("ON_DEVICE_HARD_FAIL",
                f"Not viable: thr={thr:.1f} lat={lat:.1f}ms ret_A={ret:.3f}. "
                f"Bands: thr<={FAIL_THROUGHPUT} OR lat>={FAIL_RETRIEVAL_MS}ms OR ret_A<={FAIL_RET_A}.")
    if thr >= PASS_THROUGHPUT and lat <= PASS_RETRIEVAL_MS and ret >= PASS_RET_A:
        return ("ON_DEVICE_HARD_PASS",
                f"Viable for on-device deployment: thr={thr:.1f}>={PASS_THROUGHPUT} "
                f"AND lat={lat:.1f}ms<={PASS_RETRIEVAL_MS} AND ret_A={ret:.3f}>={PASS_RET_A}. K3 closed-PASS.")
    return ("ON_DEVICE_MIDDLE_BAND",
            f"Partial: thr={thr:.1f} lat={lat:.1f}ms ret_A={ret:.3f}. "
            f"Pipeline runs but does NOT meet all product-grade targets.")


def self_test_verdict():
    def mk(t, l, r):
        return {"per_seed": {"17": {"add_throughput": t, "retrieval_latency_ms": l, "retention_A": r}}}
    cases = [
        (mk(200.0, 30.0, 0.85), "ON_DEVICE_HARD_PASS"),
        (mk(100.0, 50.0, 0.70), "ON_DEVICE_HARD_PASS"),
        (mk(50.0, 100.0, 0.60), "ON_DEVICE_MIDDLE_BAND"),
        (mk(8.0, 200.0, 0.70), "ON_DEVICE_HARD_FAIL"),
        (mk(200.0, 600.0, 0.70), "ON_DEVICE_HARD_FAIL"),
        (mk(200.0, 30.0, 0.20), "ON_DEVICE_HARD_FAIL"),
        ({}, "ON_DEVICE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
    N = config["N"]
    n_user = config["n_user_items"]
    n_retrievals = config["n_retrievals"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    # Base substrate: train on corpus A (modest scale)
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:30000]
    train_a, test_a = corpus_a[:int(0.8*len(corpus_a))], corpus_a[int(0.8*len(corpus_a)):]
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    W_base, pool_v, pool_l, pool_u = base.train_w_with_replay(
        torch.zeros((N, N), dtype=torch.float32, device=device),
        None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        2, 16, device)
    bpc_A_baseline = base.evaluate_bpc(W_base, pool_v, pool_l, pool_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          16, device)

    # Personalization: small "user data" added via Hebbian outer-products.
    # Synthesize user-bundle items: random (byte_idx, pos_idx) pairs.
    user_byte_idx = torch.randint(0, base.VOCAB, (n_user,), generator=gen).to(device)
    user_pos_idx = torch.randint(0, base.K, (n_user,), generator=gen).to(device)
    user_bindings = byte_atoms[user_byte_idx] * pos_atoms[user_pos_idx]

    # ADD throughput: time how long to do Hebbian update on n_user items, batched.
    W_user = W_base.clone()
    t0 = time.monotonic()
    with torch.no_grad():
        for i in range(n_user):
            v = user_bindings[i]
            W_user.add_(torch.outer(v, v), alpha=1.0 / N)
    add_elapsed = time.monotonic() - t0
    add_throughput = n_user / max(add_elapsed, 1e-6)

    # RETRIEVAL latency: time n_retrievals single-query reads.
    query_idx_list = torch.randint(0, n_user, (n_retrievals,), generator=gen).tolist()
    t0 = time.monotonic()
    with torch.no_grad():
        for q in query_idx_list:
            v = user_bindings[q]
            result = W_user @ v
            sims = (byte_atoms @ result) / N
            _ = int(sims.argmax())
    retrieval_elapsed = time.monotonic() - t0
    retrieval_latency_ms = (retrieval_elapsed / max(n_retrievals, 1)) * 1000.0

    # Retention of base substrate after personalization
    bpc_A_after = base.evaluate_bpc(W_user, pool_v, pool_l, pool_u,
                                       byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                       16, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0)

    return {"add_throughput": add_throughput, "retrieval_latency_ms": retrieval_latency_ms,
             "retention_A": retention_A, "n_user_items": n_user, "n_retrievals": n_retrievals,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after": bpc_A_after,
             "add_elapsed_s": add_elapsed, "retrieval_elapsed_s": retrieval_elapsed}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # FORCED CPU-only per K3 product spec
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "n_user_items": N_USER_ITEMS_SMOKE if smoke else N_USER_ITEMS_FULL,
              "n_retrievals": N_RETRIEVALS_SMOKE if smoke else N_RETRIEVALS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_throughput": PASS_THROUGHPUT, "pass_retrieval_ms": PASS_RETRIEVAL_MS,
              "pass_ret_A": PASS_RET_A,
              "fail_throughput": FAIL_THROUGHPUT, "fail_retrieval_ms": FAIL_RETRIEVAL_MS,
              "fail_ret_A": FAIL_RET_A,
              "device": "cpu"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: thr={r['add_throughput']:.1f} lat={r['retrieval_latency_ms']:.1f}ms ret_A={r['retention_A']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    base.validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_on_device_personalization_v1_smoke" if args.smoke
                          else "wave14_on_device_personalization_v1")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("add_throughput_smoke", r["add_throughput"], 1.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
