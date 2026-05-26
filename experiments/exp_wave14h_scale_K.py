"""Does anti-Hebbian rank-1 erase scale to large fact stores?

wave14h_alpha_sweep tests alpha at n_facts=100. This script holds alpha fixed
(0.5 = a sensible mid-range default) and sweeps n_facts in {30, 100, 300, 1000}
to test whether the erase mechanism still works at scale.

Pre-reg: preregs/2026-05-20_wave14h_scale_K.md

Same retrieval test as alpha_sweep (random keys + values, sign-cosine argmax
over value codebook). Always erases 30% of facts.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("verdict or verdict_msg empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_K", [])
    if not rows:
        return ("SCALE_INCONCLUSIVE", "No per-K data.")
    # PASS: leak reduction >=50pp at all K AND kept_recall >=80% at all K
    all_pass = all(r["leak_reduction_pp"] >= 50 and r["kept_mean"] >= 0.80 for r in rows)
    if all_pass:
        ks = ",".join(str(r["n_facts"]) for r in rows)
        return ("SCALE_PASS_ALL",
                f"Erase mechanism holds at all tested n_facts ({ks}): "
                f"leak reduction >=50pp AND kept_recall >=80% everywhere. "
                f"GDPR mechanism scales.")
    # PARTIAL: pass at K<=100 but degrades at K=300+
    small_pass = all(r["leak_reduction_pp"] >= 50 and r["kept_mean"] >= 0.80
                     for r in rows if r["n_facts"] <= 100)
    if small_pass:
        return ("SCALE_PASS_SMALL",
                f"Mechanism works at n_facts<=100 but degrades at larger sizes. "
                f"Per-K: " + ", ".join(
                    f"K={r['n_facts']}: lk_red={r['leak_reduction_pp']:.1f}pp "
                    f"kept={r['kept_mean']:.2%}" for r in rows))
    return ("SCALE_FAIL",
            "Mechanism fails even at small n_facts. Per-K: " + ", ".join(
                f"K={r['n_facts']}: lk_red={r['leak_reduction_pp']:.1f}pp "
                f"kept={r['kept_mean']:.2%}" for r in rows))


def self_test_verdict() -> None:
    cases = [
        ({"per_K": [{"n_facts": 30, "leak_reduction_pp": 70, "kept_mean": 0.85},
                    {"n_facts": 100, "leak_reduction_pp": 65, "kept_mean": 0.82},
                    {"n_facts": 300, "leak_reduction_pp": 55, "kept_mean": 0.81}]},
         "SCALE_PASS_ALL"),
        ({"per_K": [{"n_facts": 30, "leak_reduction_pp": 70, "kept_mean": 0.85},
                    {"n_facts": 300, "leak_reduction_pp": 30, "kept_mean": 0.60}]},
         "SCALE_PASS_SMALL"),
        ({"per_K": [{"n_facts": 30, "leak_reduction_pp": 20, "kept_mean": 0.55}]},
         "SCALE_FAIL"),
        ({"per_K": []}, "SCALE_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"self-test FAIL: {s} -> {actual}, expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen, device):
    return 2.0 * (torch.rand(shape, generator=gen, device=device) > 0.5).float() - 1.0


def antihebbian_erase(W, key_vec, alpha):
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    return W - alpha * torch.outer(Wk, key_vec) / d


def run_one_K(N, n_facts, alpha, erase_frac, seeds, device):
    """For a given (N, n_facts), measure leak_reduction and kept-recall averaged over seeds."""
    rows = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        keys = make_bipolar((n_facts, N), gen, device)
        values = make_bipolar((n_facts, N), gen, device)
        W = (values.T @ keys) / N
        n_erase = max(1, int(n_facts * erase_frac))
        erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
        erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())
        kept_idx = [i for i in range(n_facts) if i not in set(erase_idx)]

        def retrieve_correct(W_, idxs):
            if not idxs:
                return 0
            keys_sub = keys[idxs]
            retrieved = keys_sub @ W_.T
            sims = retrieved @ values.T
            preds = sims.argmax(dim=1)
            return int((preds == torch.tensor(idxs, device=device)).sum().item())

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
            "leak_mean": leak_mean, "kept_mean": kept_mean,
            "baseline_leak": baseline_leak, "baseline_kept": baseline_kept,
            "leak_reduction_pp": (baseline_leak - leak_mean) * 100,
            "per_seed": rows}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [20, 50],
                  "alpha": 0.5, "erase_frac": 0.3, "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096, "K_list": [30, 100, 300, 1000],
                  "alpha": 0.5, "erase_frac": 0.3, "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14h scale_K. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} K_list={config['K_list']} alpha={config['alpha']} "
          f"erase_frac={config['erase_frac']} seeds={config['seeds']}", flush=True)

    t0 = time.monotonic()
    per_K = []
    for n_facts in config["K_list"]:
        r = run_one_K(config["N"], n_facts, config["alpha"], config["erase_frac"],
                      config["seeds"], device)
        per_K.append(r)
        print(f"  n_facts={n_facts}  leak_red={r['leak_reduction_pp']:.1f}pp  "
              f"kept_recall={r['kept_mean']:.3f}  (baseline_leak={r['baseline_leak']:.3f}, "
              f"baseline_kept={r['baseline_kept']:.3f})", flush=True)
    elapsed = time.monotonic() - t0
    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": per_K, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14h_scale_K")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
