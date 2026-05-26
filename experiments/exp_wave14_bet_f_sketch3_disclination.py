"""Bet F Sketch 5 - Kerdock-coset topology probe.

Tests whether substrate's Kerdock 4-coset codebook geometry IS a topological-
protection primitive: store facts tagged by coset label; apply substrate noise;
check coset-label recovery rate.

Pre-reg: preregs/2026-05-21_wave14_bet_f_sketch3_disclination.md
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

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_zc = importlib.util.spec_from_file_location("zc", REPO / "experiments" / "exp_wave14zc_erase_kerdock_v7_32coset.py")
zc = importlib.util.module_from_spec(_zc); _zc.loader.exec_module(zc)

N_LABELS = 4  # Sketch 3 disclination pairs: 4 pair-core configurations

PASS_RECOVERY = 0.85
PARTIAL_FLOOR = 0.40


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def compute_verdict(summary):
    per_p = summary.get("recovery_by_p_kerdock")
    if not per_p:
        return ("BET_F_S3_INCONCLUSIVE", "Missing recovery data.")
    # Compare Kerdock to random control
    rate_at_p005 = per_p.get("0.05") or per_p.get(0.05) or 0.0
    ctrl = summary.get("recovery_by_p_random", {})
    ctrl_at_p005 = ctrl.get("0.05") or ctrl.get(0.05) or 0.5
    rate_at_p005 = float(rate_at_p005)
    ctrl_at_p005 = float(ctrl_at_p005)
    if rate_at_p005 >= PASS_RECOVERY and rate_at_p005 > ctrl_at_p005 + 0.15:
        return ("BET_F_S3_TOPOLOGY_PROTECTED",
                f"Kerdock coset recovery {rate_at_p005:.3f} at p=0.05 (>={PASS_RECOVERY}) "
                f"vs random control {ctrl_at_p005:.3f}. Codebook geometry IS a "
                f"topological-protection primitive.")
    if rate_at_p005 < PARTIAL_FLOOR:
        return ("BET_F_S3_KILLED",
                f"Kerdock coset recovery {rate_at_p005:.3f} at p=0.05 < {PARTIAL_FLOOR}. "
                f"Codebook geometry does not provide topological protection at this scale. "
                f"Closes another Bet F rescue axis.")
    return ("BET_F_S3_PARTIAL",
            f"Partial: Kerdock recovery={rate_at_p005:.3f}, control={ctrl_at_p005:.3f}. "
            f"Some protection signal but doesn't clear PASS threshold.")


def self_test_verdict():
    cases = [
        ({"recovery_by_p_kerdock": {"0.05": 0.92}, "recovery_by_p_random": {"0.05": 0.55}},
         "BET_F_S3_TOPOLOGY_PROTECTED"),
        ({"recovery_by_p_kerdock": {"0.05": 0.30}, "recovery_by_p_random": {"0.05": 0.30}},
         "BET_F_S3_KILLED"),
        ({"recovery_by_p_kerdock": {"0.05": 0.60}, "recovery_by_p_random": {"0.05": 0.50}},
         "BET_F_S3_PARTIAL"),
        ({}, "BET_F_S3_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed_kerdock(seed, N, M, p_sweep, device):
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    # Use 32-coset Kerdock for finer codebook granularity (Burgers 16-label needs more cosets)
    codebook, info = zc.make_kerdock_32coset_codebook(N, device)
    n_codewords_total = codebook.shape[0]
    n_cosets = N_LABELS  # 16 Burgers labels (interpret as 16 of the 32 cosets)
    n_per_coset = n_codewords_total // 32
    # Label atoms: one bipolar atom per Burgers label
    label_gen = torch.Generator(device=device).manual_seed(seed + 5003)
    coset_atoms = 2.0 * (torch.rand((n_cosets, N), generator=label_gen, device=device) > 0.5).float() - 1.0
    # Sample M facts, each is (codeword_idx, label_idx=codeword_idx//n_per_coset % N_LABELS)
    fact_idx = torch.randperm(n_codewords_total, generator=cpu_gen)[:M].to(device)
    fact_cosets = (fact_idx // n_per_coset) % n_cosets
    # Build W as Hebbian sum: W += outer(label_atom, codeword)
    keys = codebook[fact_idx]  # (M, N)
    labels = coset_atoms[fact_cosets]  # (M, N)
    W = (labels.T @ keys) / N  # (N, N)
    # Sweep noise
    recovery_by_p = {}
    for p in p_sweep:
        noise_gen = torch.Generator(device=device).manual_seed(seed * 31 + int(p * 1000))
        noise_mask = (torch.rand(W.shape, generator=noise_gen, device=device) < p).float()
        W_noisy = W * (1.0 - 2.0 * noise_mask)
        retrieved = keys @ W_noisy.T  # (M, N)
        sims = retrieved @ coset_atoms.T  # (M, n_cosets)
        predicted = sims.argmax(dim=1)
        recovery_by_p[p] = float((predicted == fact_cosets).float().mean())
    return recovery_by_p


def run_one_seed_random(seed, N, M, p_sweep, device):
    """Control: random ±1 keys with random coset labels (no codebook geometry)."""
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    gen = torch.Generator(device=device).manual_seed(seed + 2027)
    keys = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    n_cosets = N_LABELS
    label_gen = torch.Generator(device=device).manual_seed(seed + 5003)
    coset_atoms = 2.0 * (torch.rand((n_cosets, N), generator=label_gen, device=device) > 0.5).float() - 1.0
    fact_cosets = torch.randint(0, n_cosets, (M,), generator=cpu_gen).to(device)
    labels = coset_atoms[fact_cosets]
    W = (labels.T @ keys) / N
    recovery_by_p = {}
    for p in p_sweep:
        noise_gen = torch.Generator(device=device).manual_seed(seed * 31 + int(p * 1000))
        noise_mask = (torch.rand(W.shape, generator=noise_gen, device=device) < p).float()
        W_noisy = W * (1.0 - 2.0 * noise_mask)
        retrieved = keys @ W_noisy.T
        sims = retrieved @ coset_atoms.T
        predicted = sims.argmax(dim=1)
        recovery_by_p[p] = float((predicted == fact_cosets).float().mean())
    return recovery_by_p


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M": 256 if smoke else 1024,
              "p_sweep": [0.0, 0.05] if smoke else [0.0, 0.02, 0.05, 0.10, 0.20],
              "seeds": [17] if smoke else [17, 23, 31]}
    N = config["N"]
    M = config["M"]
    per_seed_k = []
    per_seed_r = []
    for seed in config["seeds"]:
        rk = run_one_seed_kerdock(seed, N, M, config["p_sweep"], device)
        rr = run_one_seed_random(seed, N, M, config["p_sweep"], device)
        per_seed_k.append(rk)
        per_seed_r.append(rr)
        print(f"  seed={seed}: kerdock " + ", ".join(f"p={p}:{rk[p]:.3f}" for p in config["p_sweep"]),
              flush=True)
        print(f"           random  " + ", ".join(f"p={p}:{rr[p]:.3f}" for p in config["p_sweep"]),
              flush=True)
    recovery_by_p_k = {str(p): sum(s[p] for s in per_seed_k) / len(per_seed_k) for p in config["p_sweep"]}
    recovery_by_p_r = {str(p): sum(s[p] for s in per_seed_r) / len(per_seed_r) for p in config["p_sweep"]}
    summary = {"recovery_by_p_kerdock": recovery_by_p_k,
                "recovery_by_p_random": recovery_by_p_r}
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
    out_dir = get_output_dir("wave14_bet_f_sketch3_disclination_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    rk = list(summary["recovery_by_p_kerdock"].values())[0]
    oracle.assert_baseline_high("kerdock_p0_recovery", rk, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_bet_f_sketch3_disclination")
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
