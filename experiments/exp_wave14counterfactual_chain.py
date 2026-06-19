"""Counterfactual stress test: can we subtract MANY items without drift?

wave14soft_trace validated single-item counterfactual fidelity = 1.00.
This experiment stress-tests the capability: if we subtract 10, 100, or 1000
items from a soft bundle (m_tilde - sum_e v_e * c_e), does the result still
behave like a substrate trained without those items?

Pearl Level 3 capability: counterfactual queries as compound primitive.
Materials analog: rank-K perturbation of the storage matrix; stays exact
because soft bundle is in Z^N (no clipping).

Pre-reg: same family as wave14soft_trace.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_n_subtract", [])
    if not rows:
        return ("CF_CHAIN_INCONCLUSIVE", "No data.")
    fidelities = [r["fidelity"] for r in rows]
    min_fid = min(fidelities)
    if min_fid >= 0.99:
        return ("CF_CHAIN_PERFECT",
                f"All subtraction counts maintain fidelity >= 0.99 (min={min_fid:.4f}). "
                f"Counterfactual chain is EXACT - subtract any number of items, "
                f"result is provably identical to 'never stored those items'.")
    if min_fid >= 0.95:
        return ("CF_CHAIN_HIGH",
                f"Fidelity stays >= 0.95 across all subtraction counts. Min "
                f"fidelity at n_subtract={max(r['n_subtract'] for r in rows if r['fidelity']==min_fid)}: "
                f"{min_fid:.4f}. Capability holds with bounded drift.")
    return ("CF_CHAIN_DEGRADES",
            f"Fidelity drops to {min_fid:.4f} at some subtraction count. " +
            "Per-n: " + ", ".join(f"n={r['n_subtract']}: f={r['fidelity']:.3f}" for r in rows))


def self_test_verdict() -> None:
    cases = [
        ({"per_n_subtract": [{"n_subtract": 100, "fidelity": 1.0}]}, "CF_CHAIN_PERFECT"),
        ({"per_n_subtract": [{"n_subtract": 100, "fidelity": 0.97}]}, "CF_CHAIN_HIGH"),
        ({"per_n_subtract": [{"n_subtract": 100, "fidelity": 0.50}]}, "CF_CHAIN_DEGRADES"),
        ({"per_n_subtract": []}, "CF_CHAIN_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen):
    return 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0


def run_one_n_subtract(N, K, n_subtract, seed, device):
    """Build bundle with K items, subtract n_subtract of them, compare to bundle
    built without those n_subtract items."""
    gen = torch.Generator().manual_seed(seed)
    contents = make_bipolar((K, N), gen).to(device)
    cues = make_bipolar((K, N), gen).to(device)
    bound = contents * cues
    bundle_full = bound.sum(dim=0)  # soft trace
    # Pick n_subtract items to subtract
    sub_idx = torch.randperm(K, generator=gen)[:n_subtract].tolist()
    cf_bundle = bundle_full - bound[sub_idx].sum(dim=0)
    # Reference: bundle without those items
    mask = torch.ones(K, dtype=torch.bool, device=device)
    for i in sub_idx:
        mask[i] = False
    ref_bundle = bound[mask].sum(dim=0)
    fidelity = torch.nn.functional.cosine_similarity(cf_bundle.unsqueeze(0),
                                                       ref_bundle.unsqueeze(0)).item()
    return fidelity


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K": 100,
                  "n_subtract_list": [1, 10, 50],
                  "seeds": [17]}
    else:
        # K=2000 well past alpha_c (which is 627). Subtract varying fractions.
        config = {"mode": "full", "N": 4096, "K": 2000,
                  "n_subtract_list": [1, 10, 50, 100, 300, 500, 1000, 1500, 1900],
                  "seeds": [17, 23, 31, 41, 53, 67, 79]}
    print(f"wave14counterfactual_chain. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} K={config['K']} n_subtract_list={config['n_subtract_list']}",
          flush=True)

    t0 = time.monotonic()
    per_n_subtract = []
    for n_sub in config["n_subtract_list"]:
        fids = []
        for seed in config["seeds"]:
            f = run_one_n_subtract(config["N"], config["K"], n_sub, seed, device)
            fids.append(f)
        mean_fid = sum(fids) / len(fids)
        per_n_subtract.append({"n_subtract": n_sub,
                                "fidelity": mean_fid, "per_seed_fid": fids})
        print(f"  n_subtract={n_sub:5d} (frac={n_sub/config['K']:.2f})  "
              f"fidelity={mean_fid:.5f}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_n_subtract": per_n_subtract}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_n_subtract": per_n_subtract, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14counterfactual_chain")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
