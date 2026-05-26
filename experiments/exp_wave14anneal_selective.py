"""Selective annealing: localized 'thermal noise' on ONE outer product.

wave14z showed global anneal (p=1.0) destroys EVERYTHING (factory reset).
Useful as upper bound but not selective. This tests LOCAL annealing:
apply targeted noise only to the (v_e ⊗ k_e^T) subspace via projector.

Method: project W onto k_e direction; add noise to that projection; reproject.
  P_e = (k_e k_e^T) / d
  W' = W - W @ P_e + noise * (random_vector outer k_e) / sqrt(d)

This is the substrate analog of laser annealing in semiconductor manufacturing:
heat ONE localized region without disturbing the surrounding crystal.

Multi-probe metrics. Sweep noise amplitude.

Pre-reg: preregs/2026-05-20_wave14anneal_selective.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_noise", [])
    if not rows:
        return ("SEL_ANNEAL_INCONCLUSIVE", "No data.")
    # GDPR-grade: erased facts have low retrieval, kept facts preserved
    target = [r for r in rows
              if r["leak_argmax"] <= 0.10 and r["mean_rank"] >= r["n_facts"] * 0.3
              and r["norm_ratio"] <= 0.30 and r["cosine"] <= 0.25
              and r["kept_recall"] >= 0.80
              and r["leak_paraphrase"] <= 0.20]
    if target:
        best = min(target, key=lambda r: r["leak_argmax"])
        return ("SEL_ANNEAL_GDPR",
                f"noise={best['noise']:.2f}: erased leak={best['leak_argmax']:.2%}, "
                f"kept_recall={best['kept_recall']:.2%}. Selective annealing achieves "
                f"GDPR-grade forgetting while preserving other facts. "
                f"Laser-annealing analog: localized 'heat' destroys target without "
                f"melting surrounding crystal.")
    # Partial: erased gone but kept also hurt
    erased_gone = [r for r in rows
                    if r["leak_argmax"] <= 0.10 and r["mean_rank"] >= r["n_facts"] * 0.3
                    and r["norm_ratio"] <= 0.30]
    if erased_gone:
        best = max(erased_gone, key=lambda r: r["kept_recall"])
        return ("SEL_ANNEAL_PARTIAL",
                f"noise={best['noise']:.2f}: erased leak={best['leak_argmax']:.2%} "
                f"but kept_recall={best['kept_recall']:.2%} < 80%. Selective anneal "
                f"erases but damages neighbors.")
    return ("SEL_ANNEAL_NO_FORGET",
            f"No noise level achieves leak<=10%. Best leak: "
            f"{min(r['leak_argmax'] for r in rows):.2%}.")


def self_test_verdict() -> None:
    base = {"n_facts": 100, "leak_argmax": 0.05, "mean_rank": 50,
            "norm_ratio": 0.15, "cosine": 0.10, "kept_recall": 0.92,
            "leak_paraphrase": 0.08}
    cases = [
        ({"per_noise": [{**base, "noise": 0.5}]}, "SEL_ANNEAL_GDPR"),
        ({"per_noise": [{**base, "noise": 0.5, "kept_recall": 0.5}]}, "SEL_ANNEAL_PARTIAL"),
        ({"per_noise": [{**base, "noise": 0.5, "leak_argmax": 0.5,
                          "mean_rank": 5, "norm_ratio": 0.8,
                          "kept_recall": 0.5}]}, "SEL_ANNEAL_NO_FORGET"),
        ({"per_noise": []}, "SEL_ANNEAL_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_correlated_keys(n_facts, N, rank_L, gen, device):
    factors = 2.0 * (torch.rand((rank_L, N), generator=gen) > 0.5).float() - 1.0
    weights = torch.rand((n_facts, rank_L), generator=gen)
    weights = weights * (weights > 0.6).float()
    noise = 0.3 * torch.randn((n_facts, N), generator=gen)
    keys = torch.sign(weights @ factors + noise + 1e-9)
    return keys.to(device)


def selective_anneal(W, key_vec, noise_amp, gen, device):
    """Project W along k_e, add noise in that direction, recombine.
    W' = W - (W @ k_e) k_e^T / d + noise_amp * eta * k_e^T / sqrt(d)
    where eta is a random N-vector.
    """
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    eta = torch.randn(W.size(0), generator=gen).to(device) * (d ** 0.5)
    update = (-torch.outer(Wk, key_vec) + noise_amp * torch.outer(eta, key_vec)) / d
    return W + update


def probe(W, keys, values, erase_idx, kept_idx, flip_frac, device, gen):
    if not erase_idx:
        return {}
    erase_t = torch.tensor(erase_idx, device=device)
    keys_e = keys[erase_idx]
    N = keys.size(-1)
    retrieved = keys_e @ W.T
    sims = retrieved @ values.T
    argmax_leak = (sims.argmax(dim=1) == erase_t).float().mean().item()
    sorted_idx = sims.argsort(dim=1, descending=True)
    ranks = [int((sorted_idx[r] == erase_t[r]).nonzero()[0].item()) + 1
             for r in range(len(erase_idx))]
    mean_rank = sum(ranks) / len(ranks)
    norm_ratio = (retrieved.norm(dim=1) / (N ** 0.5)).mean().item()
    cos = torch.nn.functional.cosine_similarity(retrieved, values[erase_idx], dim=1).mean().item()
    # Paraphrase
    flips = (torch.rand(keys_e.shape, generator=gen) < flip_frac).float().to(device)
    pq = keys_e * (1 - 2 * flips)
    psims = (pq @ W.T) @ values.T
    paraphrase_leak = (psims.argmax(dim=1) == erase_t).float().mean().item()
    # Kept recall
    if kept_idx:
        kept_t = torch.tensor(kept_idx, device=device)
        kr = (keys[kept_idx] @ W.T) @ values.T
        kept_recall = (kr.argmax(dim=1) == kept_t).float().mean().item()
    else:
        kept_recall = 1.0
    return {"leak_argmax": argmax_leak, "mean_rank": mean_rank,
            "norm_ratio": norm_ratio, "cosine": cos,
            "kept_recall": kept_recall, "leak_paraphrase": paraphrase_leak}


def run_one_noise(N, n_facts, n_erase, rank_L, noise_amp, flip_frac, seeds, device):
    rows = []
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        keys = make_correlated_keys(n_facts, N, rank_L, gen, device)
        values = 2.0 * (torch.rand((n_facts, N), generator=gen) > 0.5).float() - 1.0
        values = values.to(device)
        W = (values.T @ keys) / N
        erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
        erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())
        kept_idx = [i for i in range(n_facts) if i not in set(erase_idx)]
        W_edit = W.clone()
        for i in erase_idx:
            W_edit = selective_anneal(W_edit, keys[i], noise_amp, gen, device)
        m = probe(W_edit, keys, values, erase_idx, kept_idx, flip_frac, device, gen)
        rows.append({"seed": seed, **m})

    def avg(k):
        return sum(r[k] for r in rows) / len(rows)
    return {"noise": noise_amp, "n_facts": n_facts, "n_erase": n_erase,
            "leak_argmax": avg("leak_argmax"), "mean_rank": avg("mean_rank"),
            "norm_ratio": avg("norm_ratio"), "cosine": avg("cosine"),
            "kept_recall": avg("kept_recall"), "leak_paraphrase": avg("leak_paraphrase")}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "n_facts": 50, "n_erase": 10,
                  "rank_L": 12, "flip_frac": 0.10,
                  "noise_amps": [0.1, 0.5, 1.0], "seeds": [17]}
    else:
        # Substantial: many noise amps, many seeds, larger N
        config = {"mode": "full", "N": 4096, "n_facts": 400, "n_erase": 100,
                  "rank_L": 100, "flip_frac": 0.10,
                  "noise_amps": [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0],
                  "seeds": [17, 23, 31, 41, 53, 67, 79, 89, 101, 113]}
    print(f"wave14anneal_selective. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} n_facts={config['n_facts']} n_erase={config['n_erase']} "
          f"rank_L={config['rank_L']} noise_amps={config['noise_amps']}", flush=True)

    t0 = time.monotonic()
    per_noise = []
    for amp in config["noise_amps"]:
        r = run_one_noise(config["N"], config["n_facts"], config["n_erase"],
                          config["rank_L"], amp, config["flip_frac"],
                          config["seeds"], device)
        per_noise.append(r)
        print(f"  noise={amp:.2f}  leak_arg={r['leak_argmax']:.2%} "
              f"rank={r['mean_rank']:.1f}/{r['n_facts']} norm={r['norm_ratio']:.2f} "
              f"cos={r['cosine']:.2f}  kept={r['kept_recall']:.2%} "
              f"para={r['leak_paraphrase']:.2%}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_noise": per_noise}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_noise": per_noise, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14anneal_selective")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
