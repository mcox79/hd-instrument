"""Multi-hop HMM geometric scaling — Test 2 from Research 20:23 falsifiability list.

Per Research framework: acc_argmax(L) ≈ p_hop^L where p_hop ≈ 0.97 per cycle 127 data
(0.97^50 ≈ 0.22 matches observed acc_50hop).

Test: vary chain depth L ∈ {5, 10, 20, 50, 100} at N=65536 K=100; fit empirical
acc vs L to geometric model.

Verdict thresholds:
  GEOMETRIC_CONFIRMED:  log-linear fit r^2 >= 0.85 AND fitted p in [0.94, 0.99]
  GEOMETRIC_PARTIAL:    fit r^2 in [0.60, 0.85] OR p outside [0.94, 0.99] but within [0.85, 0.999]
  GEOMETRIC_FALSIFIED:  fit r^2 < 0.60 (non-geometric scaling)
  GEOMETRIC_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_hmm_geometric_scaling_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "fitted_p" not in summary:
        return ("GEOMETRIC_INCONCLUSIVE", "Missing fitted_p.")
    p = summary["fitted_p"]; r2 = summary["fit_r2"]
    per_L = summary["acc_per_L"]
    if r2 >= 0.85 and 0.94 <= p <= 0.99:
        return ("GEOMETRIC_CONFIRMED",
                f"Geometric decay confirmed: fitted p={p:.4f} in [0.94, 0.99], r2={r2:.3f}>=0.85. "
                f"acc_per_L={per_L}. HMM cascade-error theory validated.")
    if r2 >= 0.60 and 0.85 <= p <= 0.999:
        return ("GEOMETRIC_PARTIAL",
                f"Partial geometric: p={p:.4f}, r2={r2:.3f}. acc_per_L={per_L}.")
    return ("GEOMETRIC_FALSIFIED",
            f"Non-geometric scaling: p={p:.4f}, r2={r2:.3f}<0.60. "
            f"acc_per_L={per_L}. HMM cascade-error theory wrong.")


def self_test_verdict():
    cases = [
        ({"fitted_p": 0.97, "fit_r2": 0.90, "acc_per_L": {}}, "GEOMETRIC_CONFIRMED"),
        ({"fitted_p": 0.90, "fit_r2": 0.70, "acc_per_L": {}}, "GEOMETRIC_PARTIAL"),
        ({"fitted_p": 0.50, "fit_r2": 0.30, "acc_per_L": {}}, "GEOMETRIC_FALSIFIED"),
        ({}, "GEOMETRIC_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def fit_geometric(Ls, accs):
    """Fit acc(L) = p^L via log-linear regression on log(acc) vs L. Skip acc=0."""
    pairs = [(L, a) for L, a in zip(Ls, accs) if a > 0.01]
    if len(pairs) < 3:
        return 0.0, 0.0
    xs = [L for L, _ in pairs]
    ys = [math.log(a) for _, a in pairs]
    n = len(xs)
    sx = sum(xs); sy = sum(ys); sxx = sum(x * x for x in xs); sxy = sum(xs[i] * ys[i] for i in range(n))
    slope = (n * sxy - sx * sy) / max(n * sxx - sx * sx, 1e-9)
    intercept = (sy - slope * sx) / n
    p = math.exp(slope)
    mean_y = sy / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((ys[i] - (slope * xs[i] + intercept)) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return p, r2


def run_one_seed(seed, L_grid, n_trials, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    accs = {}
    for L in L_grid:
        if L > num_entities - 1 or L > num_facts:
            accs[L] = 0.0
            continue
        correct = 0
        for trial in range(n_trials):
            perm = torch.randperm(num_entities, generator=cpu_gen)[:L + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                          for _ in range(L)]
            n_distractors = max(0, num_facts - L)
            M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                    num_entities, num_relations,
                                    entity_atoms, relation_atoms, cpu_gen, device)
            if mh.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                              entity_atoms, relation_atoms):
                correct += 1
        accs[L] = correct / n_trials
    return accs


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "L_grid": [5, 10, 20] if smoke else [5, 10, 20, 50, 100],
              "n_trials": 10 if smoke else 30,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} K={config['num_facts']} L_grid={config['L_grid']}", flush=True)
    per_seed_accs = {L: [] for L in config["L_grid"]}
    for seed in config["seeds"]:
        accs = run_one_seed(seed, config["L_grid"], config["n_trials"], config, device)
        for L, a in accs.items():
            per_seed_accs[L].append(a)
        a_str = " ".join(f"L{L}={accs[L]:.3f}" for L in config["L_grid"])
        print(f"  seed={seed}: {a_str}", flush=True)
    acc_per_L = {L: sum(per_seed_accs[L]) / len(per_seed_accs[L]) for L in config["L_grid"]}
    p, r2 = fit_geometric(list(acc_per_L.keys()), list(acc_per_L.values()))
    summary = {"acc_per_L": {str(L): acc_per_L[L] for L in config["L_grid"]},
                "fitted_p": p,
                "fit_r2": r2,
                "predicted_p_per_hop": 0.97}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nfitted p={p:.4f} r2={r2:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14_multihop_hmm_geometric_scaling_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_L_acc_present",
                                 max(summary["acc_per_L"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_hmm_geometric_scaling_v1")
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
