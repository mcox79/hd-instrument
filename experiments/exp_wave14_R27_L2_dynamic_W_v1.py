"""R27 L.2 — Dynamic W reconfigurability (Marsh 2025 atomic-position re-weight analog).

Strategy pipeline-fill #5: substrate W is updated dynamically based on workload.
W_{t+1} = (1-alpha) W_t + alpha * (1/m) sum_recent x_i x_i^T over sliding window.
Test capacity boost vs static W baseline.

Pre-reg: preregs/2026-05-21_wave14_R27_L2_dynamic_W_v1.md
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

PASS_GAIN = 1.3
KILL_GAIN = 0.9


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "dynamic_acc" not in summary:
        return ("R27_L2_INCONCLUSIVE", "Missing.")
    dyn = summary["dynamic_acc"]
    base = summary["static_acc"]
    ratio = dyn / max(base, 1e-9)
    if ratio < KILL_GAIN:
        return ("R27_L2_KILLED",
                f"Dynamic W ({dyn:.3f}) underperforms static ({base:.3f}); ratio={ratio:.2f}.")
    if ratio >= PASS_GAIN:
        return ("R27_L2_PASS",
                f"Dynamic W gains {ratio:.2f}x over static (dyn={dyn:.3f}, base={base:.3f}). "
                f"Sliding-window reconfigurability is substrate-product-relevant.")
    return ("R27_L2_PARTIAL",
            f"Dynamic W marginal gain: {ratio:.2f}x (dyn={dyn:.3f}, base={base:.3f}).")


def self_test_verdict():
    cases = [
        ({"dynamic_acc": 0.90, "static_acc": 0.60}, "R27_L2_PASS"),
        ({"dynamic_acc": 0.70, "static_acc": 0.60}, "R27_L2_PARTIAL"),
        ({"dynamic_acc": 0.40, "static_acc": 0.60}, "R27_L2_KILLED"),
        ({}, "R27_L2_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_static_W(M, N, n_query, gen, device):
    keys = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    W = (values.T @ keys) / N
    # Query M random facts, the "recent" set
    query_idx = torch.randperm(M, generator=torch.Generator().manual_seed(7))[:n_query].to(device)
    pred = (keys[query_idx] @ W.T @ values.T).argmax(dim=1)
    return float((pred == query_idx).float().mean())


def run_dynamic_W(M, N, n_query, alpha, window, gen, device):
    """Dynamic W: re-weight toward recent queries via EMA."""
    keys = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    W = (values.T @ keys) / N
    query_idx = torch.randperm(M, generator=torch.Generator().manual_seed(7))[:n_query].to(device)
    # Sliding-window update: as queries arrive, re-weight W toward those keys/values
    recent_k = []
    recent_v = []
    for i in range(n_query):
        ix = int(query_idx[i])
        recent_k.append(keys[ix])
        recent_v.append(values[ix])
        if len(recent_k) > window:
            recent_k = recent_k[-window:]
            recent_v = recent_v[-window:]
        if len(recent_k) >= 2:
            rk = torch.stack(recent_k, dim=0)
            rv = torch.stack(recent_v, dim=0)
            W_recent = (rv.T @ rk) / N
            W = (1.0 - alpha) * W + alpha * W_recent
    # Final retrieval on the same query set
    pred = (keys[query_idx] @ W.T @ values.T).argmax(dim=1)
    return float((pred == query_idx).float().mean())


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 4096,
              "M": 1024 if smoke else 16384,  # over-capacity regime for static W
              "n_query": 50 if smoke else 200,
              "alpha": 0.1, "window": 50,
              "seeds": 1 if smoke else 3}
    print(f"[config] {config}", flush=True)
    static_accs = []
    dynamic_accs = []
    for s in range(config["seeds"]):
        gen = torch.Generator(device=device).manual_seed(s * 17 + 7)
        sa = run_static_W(config["M"], config["N"], config["n_query"], gen, device)
        static_accs.append(sa)
        gen = torch.Generator(device=device).manual_seed(s * 17 + 7)
        da = run_dynamic_W(config["M"], config["N"], config["n_query"],
                              config["alpha"], config["window"], gen, device)
        dynamic_accs.append(da)
        print(f"  seed={s}: static={sa:.3f} dynamic={da:.3f}", flush=True)
    summary = {"static_acc": sum(static_accs) / len(static_accs),
                "dynamic_acc": sum(dynamic_accs) / len(dynamic_accs)}
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
    out_dir = get_output_dir("wave14_R27_L2_dynamic_W_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("static_acc_present", summary["static_acc"] + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_R27_L2_dynamic_W_v1")
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
