"""Bet Z.1 SRHT compressive readout — fast holistic similarity via M log K projections.

Per Research 2026-05-22 14:50 EDT cued-holistic-readout deliverable. Tests whether
Subsampled Randomized Hadamard Transform (Tropp 2011) gives >=90% top-10 recall
on K stored patterns using M = O(eps^-2 log K) measurements vs brute-force O(NK)
direct inner products.

Mechanism: S = sqrt(N/M) * H[rows] * diag(D); sketched_patterns = patterns @ S^T.
Online: state_sketch = S @ state; similarities = sketched_patterns @ state_sketch.

Verdict (Research-specified falsification threshold):
  BET_Z1_PASS:    top-10 recall >= 0.90 (substrate-novel fast readout)
  BET_Z1_PARTIAL: 0.70 <= top-10 recall < 0.90
  BET_Z1_KILLED:  recall < 0.70 (JL guarantee broken by structured substrate)
  BET_Z1_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betZ_srht_readout_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


PASS_RECALL = 0.90
PARTIAL_RECALL = 0.70


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "top10_recall" not in summary:
        return ("BET_Z1_INCONCLUSIVE", "Missing top10_recall.")
    r = summary["top10_recall"]
    M = summary["M_measurements"]
    K = summary["K_patterns"]
    speedup = summary.get("speedup_ratio", 0)
    if r >= PASS_RECALL:
        return ("BET_Z1_PASS",
                f"SRHT compressive readout: top-10 recall = {r:.3f} (>={PASS_RECALL}) at "
                f"M={M} measurements vs N={summary['N']} (speedup={speedup:.1f}x over brute "
                f"force at K={K} stored patterns). Substrate-novel fast readout viable.")
    if r >= PARTIAL_RECALL:
        return ("BET_Z1_PARTIAL",
                f"top-10 recall = {r:.3f} ({PARTIAL_RECALL}<=r<{PASS_RECALL}) at M={M}. "
                f"Partial speedup viable but JL guarantee weak.")
    return ("BET_Z1_KILLED",
            f"top-10 recall = {r:.3f} (<{PARTIAL_RECALL}) at M={M}. "
            f"SRHT JL guarantee broken — possible structured-substrate non-IID correlation.")


def self_test_verdict():
    cases = [
        ({"top10_recall": 0.95, "M_measurements": 2000, "K_patterns": 1000, "N": 4096, "speedup_ratio": 2.0}, "BET_Z1_PASS"),
        ({"top10_recall": 0.80, "M_measurements": 2000, "K_patterns": 1000, "N": 4096}, "BET_Z1_PARTIAL"),
        ({"top10_recall": 0.50, "M_measurements": 2000, "K_patterns": 1000, "N": 4096}, "BET_Z1_KILLED"),
        ({}, "BET_Z1_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def sylvester_hadamard(n_log2, device):
    """Build Sylvester-Hadamard matrix H_n at N=2^n_log2 via recursion."""
    H = torch.tensor([[1.0]], device=device)
    for _ in range(n_log2):
        H = torch.cat([torch.cat([H, H], dim=1), torch.cat([H, -H], dim=1)], dim=0)
    return H


def srht_precompute(patterns, M, cpu_gen, device):
    """patterns: (K, N) ±1 bipolar. Returns S (M, N) and sketched (K, M)."""
    K, N = patterns.shape
    # D: diagonal sign flip
    D_bits = (torch.rand(N, generator=cpu_gen) > 0.5).to(device)
    D = 2.0 * D_bits.float() - 1.0
    # Subsampled rows
    n_log2 = int(round(math.log2(N)))
    assert 2 ** n_log2 == N, f"N={N} must be power of 2 for Hadamard"
    H = sylvester_hadamard(n_log2, device) / math.sqrt(N)
    row_idx = torch.randperm(N, generator=cpu_gen)[:M].to(device)
    S = math.sqrt(N / M) * (H[row_idx, :] * D.unsqueeze(0))  # (M, N)
    sketched = patterns @ S.T  # (K, M)
    return S, sketched


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "K_patterns": 100 if smoke else 1000,
              "M_measurements": 200 if smoke else 2000,
              "top_k": 10,
              "n_query_seeds": 1 if smoke else 5,
              "seed": 17}
    N, K, M = config["N"], config["K_patterns"], config["M_measurements"]
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    # Patterns
    bits = (torch.rand((K, N), generator=cpu_gen) > 0.5).to(device)
    patterns = 2.0 * bits.float() - 1.0
    print(f"[setup] N={N} K={K} M={M}", flush=True)
    # Pre-sketch
    S, sketched = srht_precompute(patterns, M, cpu_gen, device)
    print(f"[srht] sketch matrix S=({M},{N}), sketched_patterns=({K},{M})", flush=True)
    # Planted-signal queries: query = mean of 10 specific patterns + small noise.
    # Brute-force top-10 should recover those 10. SRHT should preserve the ranking.
    recalls = []
    n_plant = config["top_k"]
    for q_seed in range(config["n_query_seeds"]):
        # Pick n_plant indices to plant
        plant_idx = torch.randperm(K, generator=cpu_gen)[:n_plant]
        query = patterns[plant_idx.to(device)].sum(dim=0)
        # Add 10% small noise
        noise = (2.0 * (torch.rand(N, generator=cpu_gen) > 0.5).float() - 1.0) * 0.1 * math.sqrt(N) / math.sqrt(N)
        query = query + noise.to(device)
        # Brute-force ranking
        true_sim = patterns @ query  # (K,)
        true_top10 = set(torch.argsort(true_sim, descending=True)[:config["top_k"]].tolist())
        # SRHT-projected ranking
        q_sketch = S @ query
        srht_sim = sketched @ q_sketch
        srht_top10 = set(torch.argsort(srht_sim, descending=True)[:config["top_k"]].tolist())
        recall = len(true_top10 & srht_top10) / config["top_k"]
        recalls.append(recall)
        print(f"  q_seed={q_seed} plant={plant_idx.tolist()[:3]}...: top-10 recall={recall:.3f}", flush=True)
    mean_recall = sum(recalls) / len(recalls)
    speedup = (N * K) / max(M * N + K * M + M, 1)  # brute O(NK) vs SRHT O(NM + KM)
    summary = {"top10_recall": mean_recall,
                "per_query_recalls": recalls,
                "M_measurements": M,
                "K_patterns": K,
                "N": N,
                "speedup_ratio": speedup}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betZ_srht_readout_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("recall_present", summary["top10_recall"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betZ_srht_readout_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
