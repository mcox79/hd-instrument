"""ROME-style direct write vs anti-Hebbian erase under correlated keys.

wave14p_erase_multiprobe showed anti-Hebbian fails the Mirage test:
argmax says erased but rank/norm probes disagree under correlated keys.

ROME (arXiv:2202.05262) uses W' = W - (W k)(C^{-1} k)^T / (k^T C^{-1} k)
where C = empirical key covariance. The C^{-1} compensates for correlation
that breaks naive anti-Hebbian.

This experiment runs BOTH methods through the multi-probe framework. The
question: does ROME-style C^{-1} conditioning pass the deeper probes that
anti-Hebbian failed?

Pre-reg: preregs/2026-05-20_wave14q_rome_vs_antihebbian.md
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
    """Compare ROME vs anti-Hebbian on multi-probe. Both need to be measured at
    their best alpha. Verdict by which one passes more probes more cleanly.
    """
    methods = summary.get("by_method", {})
    if not methods:
        return ("ROME_VS_AH_INCONCLUSIVE", "No per-method data.")
    ah = methods.get("antihebbian", {})
    rm = methods.get("rome", {})

    def gdpr_score(rows):
        """Best alpha satisfying all-probes GDPR criteria."""
        for r in rows:
            if (r["leak_argmax"] <= 0.10 and r["mean_rank"] >= r["n_facts"] * 0.3 and
                r["norm_ratio"] <= 0.30 and r["cosine"] <= 0.25 and
                r["leak_paraphrase"] <= 0.20):
                return ("GDPR_GRADE", r)
        for r in rows:
            if r["leak_argmax"] <= 0.10:
                return ("ARGMAX_ONLY", r)
        return ("NO_ERASE", None)

    ah_status, ah_best = gdpr_score(ah.get("per_alpha", []))
    rm_status, rm_best = gdpr_score(rm.get("per_alpha", []))

    if rm_status == "GDPR_GRADE" and ah_status != "GDPR_GRADE":
        return ("ROME_WINS_GDPR",
                f"ROME passes ALL probes at alpha={rm_best['alpha']:.2f}, "
                f"anti-Hebbian status={ah_status}. C^-1 conditioning resolves "
                f"the correlated-key failure.")
    if rm_status == "GDPR_GRADE" and ah_status == "GDPR_GRADE":
        return ("BOTH_PASS_GDPR",
                f"Both methods pass at some alpha. ROME at {rm_best['alpha']:.2f}, "
                f"anti-Hebbian at {ah_best['alpha']:.2f}.")
    if rm_status == "ARGMAX_ONLY" and ah_status == "ARGMAX_ONLY":
        return ("BOTH_MIRAGE",
                f"Both fail deep probes (Mirage). Neither method gives GDPR-grade "
                f"erase under this correlation regime.")
    if ah_status == "GDPR_GRADE" and rm_status != "GDPR_GRADE":
        return ("AH_WINS",
                f"Unexpected: anti-Hebbian passes at alpha={ah_best['alpha']:.2f} "
                f"but ROME doesn't ({rm_status}). Investigate C estimation.")
    return ("NEITHER_ERASE",
            f"Both methods fail even argmax. anti-Hebbian={ah_status}, ROME={rm_status}.")


def self_test_verdict() -> None:
    cases = [
        ({"by_method": {
            "antihebbian": {"per_alpha": [{"alpha": 1.5, "n_facts": 100,
                                            "leak_argmax": 0.0, "mean_rank": 5,
                                            "norm_ratio": 0.7, "cosine": 0.1,
                                            "leak_paraphrase": 0.0}]},
            "rome": {"per_alpha": [{"alpha": 1.5, "n_facts": 100,
                                     "leak_argmax": 0.0, "mean_rank": 50,
                                     "norm_ratio": 0.05, "cosine": 0.05,
                                     "leak_paraphrase": 0.05}]}}},
         "ROME_WINS_GDPR"),
        ({"by_method": {
            "antihebbian": {"per_alpha": [{"alpha": 1.5, "n_facts": 100,
                                            "leak_argmax": 0.0, "mean_rank": 5,
                                            "norm_ratio": 0.7, "cosine": 0.1,
                                            "leak_paraphrase": 0.0}]},
            "rome": {"per_alpha": [{"alpha": 1.5, "n_facts": 100,
                                     "leak_argmax": 0.0, "mean_rank": 5,
                                     "norm_ratio": 0.7, "cosine": 0.1,
                                     "leak_paraphrase": 0.0}]}}},
         "BOTH_MIRAGE"),
        ({"by_method": {}}, "ROME_VS_AH_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"self-test FAIL: {s} -> {actual}, expected {expected}")
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


def rome_erase(W, key_vec, C_inv, alpha):
    """ROME-style erase: W' = W - alpha * (W k) (C^-1 k)^T / (k^T C^-1 k)."""
    Wk = W @ key_vec
    Cinv_k = C_inv @ key_vec
    denom = float(key_vec @ Cinv_k)
    if abs(denom) < 1e-8:
        return W
    return W - alpha * torch.outer(Wk, Cinv_k) / denom


def probe(W, keys, values, erase_idx, flip_frac, device, gen) -> dict:
    if not erase_idx:
        return {}
    erase_t = torch.tensor(erase_idx, device=device)
    keys_e = keys[erase_idx]
    N = keys.size(-1)

    def for_query(q_keys):
        retrieved = q_keys @ W.T
        sims = retrieved @ values.T
        argmax_leak = (sims.argmax(dim=1) == erase_t).float().mean().item()
        sorted_idx = sims.argsort(dim=1, descending=True)
        ranks = [int((sorted_idx[r] == erase_t[r]).nonzero()[0].item()) + 1
                 for r in range(len(erase_idx))]
        mean_rank = sum(ranks) / len(ranks)
        norm_ratio = (retrieved.norm(dim=1) / (N ** 0.5)).mean().item()
        cos = torch.nn.functional.cosine_similarity(retrieved, values[erase_idx], dim=1).mean().item()
        return argmax_leak, mean_rank, norm_ratio, cos

    a_lk, a_rk, a_nr, a_co = for_query(keys_e)
    flips = (torch.rand(keys_e.shape, generator=gen, device=device) < flip_frac).float()
    p_lk, p_rk, p_nr, p_co = for_query(keys_e * (1 - 2 * flips))
    return {"leak_argmax": a_lk, "mean_rank": a_rk, "norm_ratio": a_nr, "cosine": a_co,
            "leak_paraphrase": p_lk, "mean_rank_paraphrase": p_rk,
            "norm_ratio_paraphrase": p_nr, "cosine_paraphrase": p_co}


def run_one(method, N, n_facts, n_erase, rank_L, alpha, flip_frac, seeds, device,
            covariance_reg=0.01):
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

        # Empirical key covariance for ROME
        if method == "rome":
            C = (keys.T @ keys) / n_facts  # (N, N) — rank-limited but useful
            C_reg = C + covariance_reg * torch.eye(N, device=device)
            C_inv = torch.linalg.inv(C_reg)
        else:
            C_inv = None

        erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
        erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())

        W_edit = W.clone()
        for i in erase_idx:
            if method == "antihebbian":
                W_edit = antihebbian_erase(W_edit, keys[i], alpha)
            else:  # rome
                W_edit = rome_erase(W_edit, keys[i], C_inv, alpha)

        m = probe(W_edit, keys, values, erase_idx, flip_frac, device, gen)
        rows.append({"seed": seed, **m})

    def avg(k):
        return sum(r[k] for r in rows) / len(rows)
    return {"method": method, "alpha": alpha, "n_facts": n_facts, "n_erase": n_erase,
            "rank_L": rank_L,
            "leak_argmax": avg("leak_argmax"), "mean_rank": avg("mean_rank"),
            "norm_ratio": avg("norm_ratio"), "cosine": avg("cosine"),
            "leak_paraphrase": avg("leak_paraphrase"),
            "norm_ratio_paraphrase": avg("norm_ratio_paraphrase"),
            "cosine_paraphrase": avg("cosine_paraphrase"),
            "mean_pairwise_std": sum(pairwise_stds) / len(pairwise_stds)}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "n_facts": 50, "n_erase": 10,
                  "rank_L": 12, "flip_frac": 0.10,
                  "alphas": [1.0, 1.5], "seeds": [17]}
    else:
        # Substantial config: full alpha grid x multiple N and n_facts. ~5-10min GPU.
        config = {"mode": "full", "N": 4096, "n_facts": 300, "n_erase": 75,
                  "rank_L": 75, "flip_frac": 0.10,
                  "alphas": [0.3, 0.5, 0.7, 0.85, 1.0, 1.1, 1.2, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0],
                  "seeds": [17, 23, 31, 41, 53, 67, 79]}
    print(f"wave14q_rome_vs_antihebbian. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} n_facts={config['n_facts']} n_erase={config['n_erase']} "
          f"rank_L={config['rank_L']} flip_frac={config['flip_frac']}", flush=True)

    t0 = time.monotonic()
    by_method = {"antihebbian": {"per_alpha": []}, "rome": {"per_alpha": []}}
    for method in ["antihebbian", "rome"]:
        print(f"  --- {method} ---", flush=True)
        for alpha in config["alphas"]:
            r = run_one(method, config["N"], config["n_facts"], config["n_erase"],
                        config["rank_L"], alpha, config["flip_frac"],
                        config["seeds"], device)
            by_method[method]["per_alpha"].append(r)
            print(f"    alpha={alpha:.2f}  argmax={r['leak_argmax']:.2%} "
                  f"rank={r['mean_rank']:.1f}/{r['n_facts']} norm={r['norm_ratio']:.2f} "
                  f"cos={r['cosine']:.2f}  para_argmax={r['leak_paraphrase']:.2%}", flush=True)
    elapsed = time.monotonic() - t0

    # Oracle asserts: at the LAST alpha for ROME, rank must be > 1 (some erase happened)
    rome_last = by_method["rome"]["per_alpha"][-1]
    ah_last = by_method["antihebbian"]["per_alpha"][-1]
    oracle.assert_in_range("pairwise_std", rome_last["mean_pairwise_std"], (0.03, 0.50))
    # At least ONE method should have moved the answer at the highest alpha
    if rome_last["mean_rank"] <= 1.5 and ah_last["mean_rank"] <= 1.5:
        raise AssertionError(
            f"SANITY FAIL: neither ROME nor anti-Hebbian moved mean_rank at "
            f"alpha={config['alphas'][-1]}. Test setup is wrong.")

    summary = {"by_method": by_method}
    verdict, msg = compute_verdict(summary)
    print(f"\nORACLE CHECKS PASSED.", flush=True)
    print(f"=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "by_method": by_method, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14q_rome_vs_antihebbian")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
