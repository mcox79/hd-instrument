"""Bet F v3 - SSH-BSC topological with R10 Option 2 W-construction.

v2 used Option 3 (tridiagonal hopping) which R10 REJECTED as non-substrate.
v3 implements Option 2 per R10 addendum:
  W = (1/N_facts) sum_mu k_mu outer k_mu
where k_mu = sign(a_A + h_q^mu * a_B) over N_facts distinct (q, seed) pairs.

Pre-reg: preregs/2026-05-21_wave14_ssh_bsc_v3_protected.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_v2 = importlib.util.spec_from_file_location("v2", REPO / "experiments" / "exp_wave14_ssh_bsc_v2_protected.py")
v2 = importlib.util.module_from_spec(_v2); _v2.loader.exec_module(v2)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def build_W_option2(N, N_facts, q_distribution, seed_base, device):
    """W = (1/N_facts) sum_mu k_mu outer k_mu where k_mu encodes q_mu domain walls."""
    gen = torch.Generator().manual_seed(seed_base)
    a_A = torch.zeros(N)
    a_B = torch.zeros(N)
    # Sublattice partition: A on even, B on odd
    a_A_raw = 2.0 * (torch.rand(N // 2, generator=gen) > 0.5).float() - 1.0
    a_B_raw = 2.0 * (torch.rand(N // 2, generator=gen) > 0.5).float() - 1.0
    a_A[::2] = a_A_raw
    a_B[1::2] = a_B_raw
    a_A = a_A.to(device)
    a_B = a_B.to(device)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for mu in range(N_facts):
        q_mu = int(q_distribution[mu % len(q_distribution)])
        gen_mu = torch.Generator().manual_seed(seed_base + mu * 1009 + 7)
        h_q_mu = v2.make_modulation(N, q_mu, gen_mu).to(device)
        raw = a_A + h_q_mu * a_B
        k_mu = torch.sign(raw)
        k_mu = torch.where(k_mu == 0, torch.ones_like(k_mu), k_mu)
        W += torch.outer(k_mu, k_mu)
    W /= N_facts
    return W, a_A, a_B


def apply_substrate_noise(W, p, gen, device):
    """Apply Bernoulli(p) bit-flip noise by perturbing W with random ±1 sign-flips."""
    if p == 0.0:
        return W.clone()
    noise_mask = (torch.rand(W.shape, generator=gen, device=device) < p).float()
    return W * (1.0 - 2.0 * noise_mask)


def chiral_violation(H, device):
    return v2.chiral_violation(H, device)


def mondragon_shem_winding(H, device):
    return v2.mondragon_shem_winding(H, device)


def compute_verdict(summary):
    return v2.compute_verdict(summary)


def self_test_verdict():
    v2.self_test_verdict()
    print(f"v3 inherits v2 verdict tree", flush=True)


def run_one_cell(q, p, seed, N, N_facts, q_distribution, device):
    W, a_A, a_B = build_W_option2(N, N_facts, q_distribution, seed * 31 + 7, device)
    noise_gen = torch.Generator(device=device).manual_seed(seed * 7 + 1009)
    W_noisy = apply_substrate_noise(W, p, noise_gen, device)
    H_raw = W_noisy  # already symmetric (sum of symmetric outer-products)
    # Per R10 addendum: project to off-diagonal sublattice block to enforce chiral AIII.
    # Gamma = diag(+1 on A=even, -1 on B=odd); chiral-AIII requires Gamma H Gamma = -H.
    # H_chiral = (H_raw - Gamma H_raw Gamma) / 2 keeps only AB+BA blocks.
    gamma = torch.ones(N, device=device)
    gamma[1::2] = -1.0
    GHG = gamma.unsqueeze(1) * H_raw * gamma.unsqueeze(0)
    H = (H_raw - GHG) / 2.0
    cv = chiral_violation(H, device)
    if cv > 0.05:
        return {"q": q, "p": p, "seed": seed, "chiral_violation": cv,
                 "nu_MS": None, "bott": None}
    nu_MS = mondragon_shem_winding(H, device)
    return {"q": q, "p": p, "seed": seed, "chiral_violation": cv,
             "nu_MS": nu_MS, "bott": None}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "N_facts": 100 if smoke else 500,
              "q_sweep": [2] if smoke else [2, 5, 10],
              "q_distribution": [2, 5, 10],  # facts span these q values
              "p_sweep": [0.0, 0.10] if smoke else [0.0, 0.02, 0.05, 0.10, 0.20],
              "seeds": [17] if smoke else [17, 23, 31]}
    print(f"[config] {config}", flush=True)
    per_cell = {}
    for q in config["q_sweep"]:
        for p in config["p_sweep"]:
            for seed in config["seeds"]:
                key = f"{q}_{p}_{seed}"
                print(f"[cell] {key} ...", flush=True)
                per_cell[key] = run_one_cell(q, p, seed, config["N"],
                                                  config["N_facts"],
                                                  config["q_distribution"], device)
                cv = per_cell[key]["chiral_violation"]
                nu = per_cell[key]["nu_MS"]
                print(f"  chiral_viol={cv:.4f} nu_MS={nu}", flush=True)
    summary = {"per_cell": per_cell}
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
    out_dir = get_output_dir("wave14_ssh_bsc_v3_protected_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["per_cell"].values())[0]
    oracle.assert_baseline_high("chiral_inv_present",
                                    1.0 - first["chiral_violation"], 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_ssh_bsc_v3_protected")
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
