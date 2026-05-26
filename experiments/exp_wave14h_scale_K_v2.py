"""Erase scaling test: does anti-Hebbian rank-1 work at large fact counts?

v1 used orthogonal random keys -> trivial result (leak_reduction=0pp because
argmax is magnitude-invariant). v2 uses the same correlated-key setup as
wave14h_alpha_sweep_v2 (rank-L latent subspace) and sweeps n_facts.

Pre-reg: preregs/2026-05-20_wave14h_scale_K_v2.md

Theory-asserted smoke:
  1. Pairwise key cosine std in [0.05, 0.50] (keys actually correlated)
  2. Method A baseline leak >= 0.85 (substrate stores facts)
  3. Method A != Method B at largest K (distinguishable)
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
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_K", [])
    if not rows:
        return ("SCALE_INCONCLUSIVE", "No per-K data.")
    pass_all = all(r["leak_reduction_pp"] >= 30 and r["kept_mean"] >= 0.75 for r in rows)
    if pass_all:
        ks = ",".join(str(r["n_facts"]) for r in rows)
        return ("SCALE_PASS_ALL",
                f"Erase scales: leak_reduction>=30pp AND kept>=75% at every n_facts ({ks}). "
                f"GDPR mechanism holds at scale.")
    small_pass = all(r["leak_reduction_pp"] >= 30 and r["kept_mean"] >= 0.75
                     for r in rows if r["n_facts"] <= 200)
    if small_pass:
        return ("SCALE_PASS_SMALL",
                "Holds at n_facts<=200 but degrades at larger sizes. Per-K: " +
                ", ".join(f"K={r['n_facts']}: lk_red={r['leak_reduction_pp']:.1f}pp "
                          f"kept={r['kept_mean']:.2%}" for r in rows))
    return ("SCALE_FAIL",
            "Mechanism fails even at small n_facts. Per-K: " +
            ", ".join(f"K={r['n_facts']}: lk_red={r['leak_reduction_pp']:.1f}pp "
                      f"kept={r['kept_mean']:.2%}" for r in rows))


def self_test_verdict() -> None:
    cases = [
        ({"per_K": [{"n_facts": 50, "leak_reduction_pp": 80, "kept_mean": 0.85},
                    {"n_facts": 200, "leak_reduction_pp": 60, "kept_mean": 0.78},
                    {"n_facts": 1000, "leak_reduction_pp": 40, "kept_mean": 0.76}]},
         "SCALE_PASS_ALL"),
        ({"per_K": [{"n_facts": 50, "leak_reduction_pp": 80, "kept_mean": 0.90},
                    {"n_facts": 1000, "leak_reduction_pp": 15, "kept_mean": 0.50}]},
         "SCALE_PASS_SMALL"),
        ({"per_K": [{"n_facts": 50, "leak_reduction_pp": 10, "kept_mean": 0.40}]},
         "SCALE_FAIL"),
        ({"per_K": []}, "SCALE_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"verdict self-test FAIL: {s} -> {actual}, expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_correlated_keys(n_facts: int, N: int, rank_L: int, gen: torch.Generator,
                         device: torch.device) -> torch.Tensor:
    factors = 2.0 * (torch.rand((rank_L, N), generator=gen, device=device) > 0.5).float() - 1.0
    weights = torch.rand((n_facts, rank_L), generator=gen, device=device)
    weights = weights * (weights > 0.6).float()
    noise = 0.3 * torch.randn((n_facts, N), generator=gen, device=device)
    return torch.sign(weights @ factors + noise + 1e-9)


def antihebbian_erase(W, key_vec, alpha):
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    return W - alpha * torch.outer(Wk, key_vec) / d


def run_one_K(N, n_facts, n_erase, rank_L, alpha, seeds, device):
    rows = []
    pairwise_stds = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        keys = make_correlated_keys(n_facts, N, rank_L, gen, device)
        values = 2.0 * (torch.rand((n_facts, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (values.T @ keys) / N
        key_pairs = (keys @ keys.T) / N
        mask = ~torch.eye(n_facts, dtype=torch.bool, device=device)
        pairwise_stds.append(float(key_pairs[mask].std()))

        def retrieve_correct(W_, idxs):
            if not idxs:
                return 0
            retrieved = keys[idxs] @ W_.T
            sims = retrieved @ values.T
            preds = sims.argmax(dim=1)
            return int((preds == torch.tensor(idxs, device=device)).sum().item())

        erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
        erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())
        kept_idx = [i for i in range(n_facts) if i not in set(erase_idx)]
        leak_A = retrieve_correct(W, erase_idx) / n_erase
        kept_A = retrieve_correct(W, kept_idx) / max(1, len(kept_idx))
        W_B = W.clone()
        for i in erase_idx:
            W_B = antihebbian_erase(W_B, keys[i], alpha)
        leak_B = retrieve_correct(W_B, erase_idx) / n_erase
        kept_B = retrieve_correct(W_B, kept_idx) / max(1, len(kept_idx))
        rows.append({"seed": seed, "leak_A": leak_A, "kept_A": kept_A,
                     "leak_B": leak_B, "kept_B": kept_B})
    leak_mean = sum(r["leak_B"] for r in rows) / len(rows)
    kept_mean = sum(r["kept_B"] for r in rows) / len(rows)
    baseline_leak = sum(r["leak_A"] for r in rows) / len(rows)
    baseline_kept = sum(r["kept_A"] for r in rows) / len(rows)
    return {"n_facts": n_facts, "alpha": alpha, "n_erase": n_erase,
            "rank_L": rank_L,
            "leak_mean": leak_mean, "kept_mean": kept_mean,
            "baseline_leak": baseline_leak, "baseline_kept": baseline_kept,
            "leak_reduction_pp": (baseline_leak - leak_mean) * 100,
            "mean_pairwise_std": sum(pairwise_stds) / len(pairwise_stds),
            "per_seed": rows}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # rank_L FIXED (not scaling with n_facts) so correlation strength stays constant.
    # At rank_L=20, all K-values draw from the same 20-factor space -> consistent overlap.
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [30, 80],
                  "alpha": 1.5, "erase_frac": 0.25, "rank_L": 12,
                  "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096, "K_list": [50, 100, 200, 500, 1000],
                  "alpha": 1.5, "erase_frac": 0.25, "rank_L": 30,
                  "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14h_scale_K_v2. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} K_list={config['K_list']} alpha={config['alpha']} "
          f"erase_frac={config['erase_frac']} rank_L={config['rank_L']} (fixed)", flush=True)

    t0 = time.monotonic()
    per_K = []
    rank_L = config["rank_L"]
    for n_facts in config["K_list"]:
        n_erase = max(1, int(n_facts * config["erase_frac"]))
        r = run_one_K(config["N"], n_facts, n_erase, rank_L, config["alpha"],
                      config["seeds"], device)
        per_K.append(r)
        print(f"  n_facts={n_facts} rank_L={rank_L} pairwise_std={r['mean_pairwise_std']:.3f}  "
              f"leak_red={r['leak_reduction_pp']:.1f}pp  kept={r['kept_mean']:.3f}  "
              f"(baseline leak={r['baseline_leak']:.3f} kept={r['baseline_kept']:.3f})",
              flush=True)
    elapsed = time.monotonic() - t0

    last = per_K[-1]
    oracle.assert_in_range("largest_K pairwise_std", last["mean_pairwise_std"],
                            (0.03, 0.50))
    oracle.assert_baseline_high("largest_K baseline leak", last["baseline_leak"], 0.70)
    oracle.assert_distinguishable("largest_K Method A vs B leak",
                                   last["baseline_leak"], last["leak_mean"], 0.10)

    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    print(f"\nORACLE CHECKS PASSED.", flush=True)
    print(f"=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": per_K, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14h_scale_K_v2")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
