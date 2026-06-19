"""Binder cumulant g4 on P(q) for finite-size scaling (H2 observability probe).

From research_meta_map_and_adjacencies_2026-05-23.md H7:
  Binder ratio g4 on P(q): standard finite-size scaling probe for the
  cycle 162 PQ_OTHER_CARDINALITY structure; never run.

Binder cumulant: g4 = 1 - <q^4> / (3 * <q^2>^2)
  In a paramagnet: q -> 0 -> g4 -> 2/3
  In RS spin glass: g4 -> 0 at infinite N (q distribution is a delta at q_EA)
  In RSB phase: g4 -> value in (0, 2/3) that grows with N-scaling
  In finite-N: g4 crosses zero at a phase transition -> finite-size scaling

At FULL: compute g4 at N in {512, 1024, 2048, 4096, 8192} across 50+ seeds.
  If g4 decreases with N -> RS phase confirmed (self-averaging).
  If g4 increases with N -> RSB phase (non-self-averaging).
  If g4 collapses -> all N produce same g4 -> mean-field with finite-N corrections.

HARD PASS: g4 shows monotone decreasing trend with N (RS-cert confirmed via Binder).
HARD FAIL: g4 increases with N (RSB signal) OR non-monotone (inconclusive).

Verdict labels:
  BINDER_RS_CONFIRMED   -- g4 decreasing with N; RS phase confirmed
  BINDER_RSB_SIGNAL     -- g4 increasing with N; RSB candidate
  BINDER_NONMONOTONE    -- non-monotone; inconclusive
  BINDER_INCONCLUSIVE   -- not enough data

Pure CPU. No GPU required.
Memory budget: codebook N x K float32; N=8192, K=100 -> 3 MB. Peak ~50 MB.
Expected runtime: ~8-12 min CPU at FULL (50 seeds x 5 N values).
Smoke: ~1 min (10 seeds, N in {256, 512}).
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

MONOTONE_TOL = 0.01   # allow this much non-monotonicity before calling NONMONOTONE


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing keys: {set(d.keys())}")


def compute_verdict(summary):
    if "g4_by_N" not in summary:
        return ("BINDER_INCONCLUSIVE", "Missing g4_by_N.")
    g4s = summary["g4_by_N"]   # dict {str(N): g4_value}
    if len(g4s) < 2:
        return ("BINDER_INCONCLUSIVE", "Need >= 2 N values for trend.")
    Ns = sorted(g4s.keys(), key=int)
    vals = [g4s[n] for n in Ns]
    # Check monotone decreasing (RS) vs monotone increasing (RSB)
    diffs = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    all_dec = all(d < MONOTONE_TOL for d in diffs)
    all_inc = all(d > -MONOTONE_TOL for d in diffs)
    avg_slope = sum(diffs) / len(diffs)
    desc = f"g4={dict(zip(Ns, [round(v, 4) for v in vals]))}, slope={avg_slope:.4f}"
    if all_dec and avg_slope < -0.005:
        return ("BINDER_RS_CONFIRMED",
                f"g4 monotone decreasing with N (RS self-averaging confirmed). {desc}")
    if all_inc and avg_slope > 0.005:
        return ("BINDER_RSB_SIGNAL",
                f"g4 monotone increasing with N (RSB non-self-averaging signal). {desc}")
    return ("BINDER_NONMONOTONE",
            f"g4 non-monotone with N (inconclusive; may need larger N sweep or seeds). {desc}")


def self_test_verdict():
    cases = [
        ({"g4_by_N": {"512": 0.50, "1024": 0.40, "2048": 0.30, "4096": 0.20}}, "BINDER_RS_CONFIRMED"),
        ({"g4_by_N": {"512": 0.20, "1024": 0.30, "2048": 0.40, "4096": 0.50}}, "BINDER_RSB_SIGNAL"),
        ({"g4_by_N": {"512": 0.30, "1024": 0.20, "2048": 0.35, "4096": 0.25}}, "BINDER_NONMONOTONE"),
        ({}, "BINDER_INCONCLUSIVE"),
        ({"g4_by_N": {"512": 0.30}}, "BINDER_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"Expected {exp}, got {a} for input {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_codebook(K, N, gen, device):
    return (torch.randint(0, 2, (K, N), generator=gen, device=device).float() * 2 - 1)


def compute_q_overlap(codebook, K_store, n_seeds_inner, seed_base):
    """Compute q = (1/N) * <s_a * s_b> between two independent random starts."""
    N = codebook.shape[1]
    W = codebook[:K_store].T @ codebook[:K_store] / N
    q_samples = []
    gen = torch.Generator()
    for i in range(n_seeds_inner):
        # Two independent random starts, converge, measure overlap
        g1 = gen.manual_seed(seed_base + i * 2)
        g2 = gen.manual_seed(seed_base + i * 2 + 1)
        x1 = make_bsc_codebook(1, N, g1, codebook.device)[0]
        x2 = make_bsc_codebook(1, N, g2, codebook.device)[0]
        for _ in range(20):
            x1 = torch.sign(W @ x1)
            x1[x1 == 0] = 1.0
        for _ in range(20):
            x2 = torch.sign(W @ x2)
            x2[x2 == 0] = 1.0
        q = float((x1 * x2).mean())
        q_samples.append(q)
    return torch.tensor(q_samples)


def binder_g4(q_samples):
    """Binder cumulant g4 = 1 - <q^4> / (3 * <q^2>^2)."""
    q2 = float((q_samples ** 2).mean())
    q4 = float((q_samples ** 4).mean())
    if q2 < 1e-12:
        return float('nan')
    return 1.0 - q4 / (3.0 * q2 ** 2)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")
    cfg = {
        "mode": "smoke" if smoke else "full",
        "N_values": [256, 512] if smoke else [512, 1024, 2048, 4096, 8192],
        "K": 50,
        "K_store": 40,
        "n_codebook_seeds": 3 if smoke else 10,
        "n_overlap_pairs": 10 if smoke else 50,
    }

    g4_by_N = {}
    for N in cfg["N_values"]:
        g4_vals = []
        for cs in range(cfg["n_codebook_seeds"]):
            seed = 17 + cs * 101
            gen = torch.Generator(device=device).manual_seed(seed)
            codebook = make_bsc_codebook(cfg["K"], N, gen, device)
            q_samps = compute_q_overlap(codebook, cfg["K_store"], cfg["n_overlap_pairs"], seed + 50000)
            g4 = binder_g4(q_samps)
            g4_vals.append(g4)
        mean_g4 = sum(g4_vals) / len(g4_vals)
        g4_by_N[str(N)] = round(mean_g4, 5)
        print(f"  N={N}: g4={mean_g4:.4f} (across {cfg['n_codebook_seeds']} codebook seeds)", flush=True)

    summary = {"g4_by_N": g4_by_N}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_binder_ratio_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("n_N_values", float(len(summary["g4_by_N"])), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_binder_ratio_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
