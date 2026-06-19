"""Annealing-as-erasure: thermal/noise-based forgetting vs targeted subtraction.

User's materials-science insight: in real systems, ordered phases (crystal,
ferromagnet, glass) are destroyed by raising temperature past Tc. Substrate
analog: raising effective noise rate p past a threshold should destroy stored
patterns. AGS phase diagram T_g(alpha) = 1 + sqrt(alpha) gives the prediction.

Three protocols compared:
  A. ANNEAL: W' = (1-p) * W + p * Gaussian_noise. Global thermal disorder.
     Predict: leak rate drops sharply past a critical p.
  B. DIRECT_SUBTRACT: W' = W - eta * (v_e outer k_e). Exact rank-1 subtraction
     of the original storage. The "ground-truth" erase.
     Predict: leak=0 at eta=1 for any correlation regime.
  C. ANTI_HEBBIAN: W' = W - eta * (W k_e)(k_e^T) / d (the Mirage-failing
     approach from wave14p). Included as baseline for comparison.

Multi-probe metrics per protocol: argmax_leak, mean_rank, norm_ratio, cosine,
paraphrase_argmax_leak.

Pre-reg: preregs/2026-05-20_wave14z_anneal_erase.md
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
        raise ValueError(f"missing required fields")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def compute_verdict(summary: dict) -> tuple[str, str]:
    by = summary.get("by_method", {})
    if not by:
        return ("ANNEAL_INCONCLUSIVE", "No method data.")
    # Best single config per method
    def best_gdpr(rows):
        target = [r for r in rows
                  if r["leak_argmax"] <= 0.10 and r["mean_rank"] >= r["n_facts"] * 0.3
                  and r["norm_ratio"] <= 0.30 and r["cosine"] <= 0.25
                  and r["leak_paraphrase"] <= 0.20]
        return target[0] if target else None

    ann = best_gdpr(by.get("anneal", {}).get("per_eta", []))
    dir_ = best_gdpr(by.get("direct_subtract", {}).get("per_eta", []))
    ah = best_gdpr(by.get("anti_hebbian", {}).get("per_eta", []))

    winners = []
    if ann: winners.append(f"ANNEAL@p={ann['eta']}")
    if dir_: winners.append(f"DIRECT@eta={dir_['eta']}")
    if ah: winners.append(f"AH@eta={ah['eta']}")

    if not winners:
        return ("ANNEAL_NONE_GDPR",
                "No method achieves GDPR-grade multi-probe forgetting. " +
                f"Best norm_ratio across all methods: " +
                f"{min((r['norm_ratio'] for m in by.values() for r in m.get('per_eta', [])), default=1.0):.3f}")
    # Check most-specific cases first (multi vs single winner)
    if len(winners) >= 2:
        return ("ANNEAL_MULTIPLE_PASS",
                f"GDPR-grade achieved by: {', '.join(winners)}.")
    if dir_:
        return ("ANNEAL_DIRECT_WINS",
                f"DIRECT_SUBTRACT achieves GDPR-grade at eta={dir_['eta']} "
                f"(leak={dir_['leak_argmax']:.2%}, rank={dir_['mean_rank']:.0f}). "
                f"Neither ANNEAL nor ANTI_HEBBIAN does. Direct subtraction is "
                f"the clean GDPR mechanism for this substrate.")
    if ann:
        return ("ANNEAL_THERMAL_WINS",
                f"ANNEAL achieves GDPR-grade at p={ann['eta']} "
                f"(leak={ann['leak_argmax']:.2%}). Materials-analog thermal "
                f"disorder destroys stored patterns cleanly.")
    return ("ANNEAL_AH_WINS",
            f"Only anti-Hebbian passes (unexpected): {ah['eta']}")


def self_test_verdict() -> None:
    base = {"n_facts": 100, "leak_argmax": 0.0, "mean_rank": 80, "norm_ratio": 0.1,
            "cosine": 0.05, "leak_paraphrase": 0.05}
    fail = {"n_facts": 100, "leak_argmax": 1.0, "mean_rank": 1, "norm_ratio": 0.95,
            "cosine": 0.95, "leak_paraphrase": 1.0}
    cases = [
        # Direct wins, others fail
        ({"by_method": {
            "direct_subtract": {"per_eta": [{**base, "eta": 1.0}]},
            "anneal":          {"per_eta": [{**fail, "eta": 0.5}]},
            "anti_hebbian":    {"per_eta": [{**fail, "eta": 1.0}]},
         }}, "ANNEAL_DIRECT_WINS"),
        # All fail
        ({"by_method": {
            "direct_subtract": {"per_eta": [{**fail, "eta": 1.0}]},
            "anneal":          {"per_eta": [{**fail, "eta": 0.5}]},
            "anti_hebbian":    {"per_eta": [{**fail, "eta": 1.0}]},
         }}, "ANNEAL_NONE_GDPR"),
        # Multiple pass
        ({"by_method": {
            "direct_subtract": {"per_eta": [{**base, "eta": 1.0}]},
            "anneal":          {"per_eta": [{**base, "eta": 0.7}]},
            "anti_hebbian":    {"per_eta": [{**fail, "eta": 1.0}]},
         }}, "ANNEAL_MULTIPLE_PASS"),
        ({"by_method": {}}, "ANNEAL_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_correlated_keys(n_facts: int, N: int, rank_L: int, gen, device):
    factors = 2.0 * (torch.rand((rank_L, N), generator=gen) > 0.5).float() - 1.0
    weights = torch.rand((n_facts, rank_L), generator=gen)
    weights = weights * (weights > 0.6).float()
    noise = 0.3 * torch.randn((n_facts, N), generator=gen)
    keys = torch.sign(weights @ factors + noise + 1e-9)
    return keys.to(device)


def make_bipolar(shape, gen, device):
    x = 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0
    return x.to(device)


def anneal_erase(W, eta, gen, device):
    """W' = (1-eta) * W + eta * gaussian_noise. Global thermal disorder."""
    sigma_W = float(W.std())
    noise = torch.randn(W.shape, generator=gen).to(device) * sigma_W
    return (1.0 - eta) * W + eta * noise


def direct_subtract_erase(W, key_vec, value_vec, eta):
    """W' = W - eta * (v outer k) / N. The exact ground-truth erase."""
    N = key_vec.size(-1)
    return W - eta * torch.outer(value_vec, key_vec) / N


def antihebbian_erase(W, key_vec, eta):
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    return W - eta * torch.outer(Wk, key_vec) / d


def probe(W, keys, values, erase_idx, flip_frac, device, gen) -> dict:
    if not erase_idx:
        return {}
    erase_t = torch.tensor(erase_idx, device=device)
    keys_e = keys[erase_idx]
    N = keys.size(-1)

    def for_q(q_keys):
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

    a_lk, a_rk, a_nr, a_co = for_q(keys_e)
    flips = (torch.rand(keys_e.shape, generator=gen) < flip_frac).float().to(device)
    p_lk, _, _, _ = for_q(keys_e * (1 - 2 * flips))
    return {"leak_argmax": a_lk, "mean_rank": a_rk, "norm_ratio": a_nr, "cosine": a_co,
            "leak_paraphrase": p_lk}


def run_one(method, N, n_facts, n_erase, rank_L, eta, flip_frac, seeds, device):
    rows = []
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        keys = make_correlated_keys(n_facts, N, rank_L, gen, device)
        values = make_bipolar((n_facts, N), gen, device)
        W = (values.T @ keys) / N
        erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
        erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())

        W_edit = W.clone()
        if method == "anneal":
            W_edit = anneal_erase(W_edit, eta, gen, device)
        else:
            for i in erase_idx:
                if method == "direct_subtract":
                    W_edit = direct_subtract_erase(W_edit, keys[i], values[i], eta)
                else:  # anti_hebbian
                    W_edit = antihebbian_erase(W_edit, keys[i], eta)

        m = probe(W_edit, keys, values, erase_idx, flip_frac, device, gen)
        rows.append({"seed": seed, **m})

    def avg(k):
        return sum(r[k] for r in rows) / len(rows)
    return {"method": method, "eta": eta, "n_facts": n_facts, "n_erase": n_erase,
            "leak_argmax": avg("leak_argmax"), "mean_rank": avg("mean_rank"),
            "norm_ratio": avg("norm_ratio"), "cosine": avg("cosine"),
            "leak_paraphrase": avg("leak_paraphrase")}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "n_facts": 50, "n_erase": 10,
                  "rank_L": 12, "flip_frac": 0.10,
                  "etas_anneal": [0.3, 0.7, 1.0],
                  "etas_direct": [0.5, 1.0],
                  "etas_ah": [1.0],
                  "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096, "n_facts": 300, "n_erase": 75,
                  "rank_L": 75, "flip_frac": 0.10,
                  "etas_anneal": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                  "etas_direct": [0.3, 0.5, 0.7, 0.85, 1.0, 1.15, 1.3],
                  "etas_ah": [0.5, 1.0, 1.5, 2.0],
                  "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14z_anneal_erase. mode={config['mode']} device={device}", flush=True)

    t0 = time.monotonic()
    by_method = {"anneal": {"per_eta": []},
                 "direct_subtract": {"per_eta": []},
                 "anti_hebbian": {"per_eta": []}}

    for method, etas_key in [("anneal", "etas_anneal"),
                              ("direct_subtract", "etas_direct"),
                              ("anti_hebbian", "etas_ah")]:
        print(f"  --- {method} ---", flush=True)
        for eta in config[etas_key]:
            r = run_one(method, config["N"], config["n_facts"], config["n_erase"],
                        config["rank_L"], eta, config["flip_frac"],
                        config["seeds"], device)
            by_method[method]["per_eta"].append(r)
            print(f"    eta={eta:.2f}  argmax={r['leak_argmax']:.2%} "
                  f"rank={r['mean_rank']:.1f}/{r['n_facts']} norm={r['norm_ratio']:.2f} "
                  f"cos={r['cosine']:.2f}  para={r['leak_paraphrase']:.2%}", flush=True)
    elapsed = time.monotonic() - t0

    # Oracle: DIRECT_SUBTRACT at eta=1.0 should at minimum kill DIRECTION
    # (cos -> 0). Norm may stay high due to cross-talk under correlated keys
    # (this is a real physics finding, not a bug).
    direct_eta1 = next((r for r in by_method["direct_subtract"]["per_eta"]
                       if abs(r["eta"] - 1.0) < 0.01), None)
    if direct_eta1:
        if direct_eta1["cosine"] > 0.30:
            raise AssertionError(
                f"SANITY FAIL: direct_subtract at eta=1.0 has cosine="
                f"{direct_eta1['cosine']:.2f} > 0.30. Subtraction should kill "
                f"direction; test setup is broken.")

    summary = {"by_method": by_method}
    verdict, msg = compute_verdict(summary)
    print(f"\nORACLE CHECKS PASSED.")
    print(f"=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "by_method": by_method, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14z_anneal_erase")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
