"""VAMP-on-chain N-sweep — at what N does the VAMP advantage emerge over argmax?

Cycle 127 VAMP-on-chain PERFECT at N=65536 but argmax also PERFECT at N=4096 cycle 96.
The "VAMP rescues failure" only matters at large N. At what N does the failure mode
appear / VAMP advantage emerge?

Test depth=50 K=100 across N in {4096, 8192, 16384, 32768, 65536}; compare argmax
vs VAMP-on-chain.

Verdict thresholds:
  N_SWEEP_CLEAN_TRANSITION: argmax decays smoothly with N AND VAMP stays >= 0.9 throughout
  N_SWEEP_DISTINCT_CLIFF:   argmax drops sharply at specific N (cliff localized)
  N_SWEEP_BOTH_DECAY:      both methods decay (VAMP advantage diminishes at large N)
  N_SWEEP_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_vamp_chain_N_sweep_v1.md
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

_v = importlib.util.spec_from_file_location("v",
    REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
v = importlib.util.module_from_spec(_v); _v.loader.exec_module(v)
_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "argmax_per_N" not in summary:
        return ("N_SWEEP_INCONCLUSIVE", "Missing argmax_per_N.")
    arg = summary["argmax_per_N"]; vmp = summary["vamp_per_N"]
    arg_vals = list(arg.values()); vmp_vals = list(vmp.values())
    vamp_min = min(vmp_vals)
    arg_max = max(arg_vals); arg_min = min(arg_vals)
    # If VAMP stays >=0.9 and argmax shows monotone or substantial decay
    if vamp_min < 0.5:
        return ("N_SWEEP_BOTH_DECAY",
                f"VAMP also decays: min={vamp_min:.3f}. argmax_per_N={arg}, vamp_per_N={vmp}.")
    # CLIFF: penultimate N has high acc, last has low (clean step-down)
    Ns_sorted = sorted(int(N) for N in arg.keys())
    last_step_drop = arg[str(Ns_sorted[-2])] - arg[str(Ns_sorted[-1])] if len(Ns_sorted) >= 2 else 0.0
    penult_acc = arg[str(Ns_sorted[-2])] if len(Ns_sorted) >= 2 else 0.0
    if vamp_min >= 0.9 and last_step_drop >= 0.30 and penult_acc >= 0.70:
        return ("N_SWEEP_DISTINCT_CLIFF",
                f"argmax cliff at N={Ns_sorted[-1]}: drop from {penult_acc:.3f} to "
                f"{arg[str(Ns_sorted[-1])]:.3f}. argmax_per_N={arg}, vamp_per_N={vmp}.")
    if vamp_min >= 0.9 and (arg_max - arg_min) >= 0.4:
        return ("N_SWEEP_CLEAN_TRANSITION",
                f"VAMP stays >=0.9 throughout; argmax decays from {arg_max:.3f} to {arg_min:.3f}. "
                f"argmax_per_N={arg}, vamp_per_N={vmp}.")
    return ("N_SWEEP_INCONCLUSIVE",
            f"No clear pattern. argmax_per_N={arg}, vamp_per_N={vmp}.")


def self_test_verdict():
    cases = [
        ({"argmax_per_N": {"4096": 0.8, "8192": 0.6, "65536": 0.2},
          "vamp_per_N": {"4096": 1.0, "8192": 1.0, "65536": 1.0}}, "N_SWEEP_CLEAN_TRANSITION"),
        ({"argmax_per_N": {"4096": 0.9, "8192": 0.9, "65536": 0.3},
          "vamp_per_N": {"4096": 1.0, "8192": 1.0, "65536": 1.0}}, "N_SWEEP_DISTINCT_CLIFF"),
        ({"argmax_per_N": {"4096": 0.8, "65536": 0.3},
          "vamp_per_N": {"4096": 0.4, "65536": 0.2}}, "N_SWEEP_BOTH_DECAY"),
        ({}, "N_SWEEP_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_N(N, depth, n_trials, num_relations, num_facts, num_entities, seed, device):
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    c_arg = 0; c_vmp = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
        chain_entities = perm.tolist()
        chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                      for _ in range(depth)]
        n_distractors = max(0, num_facts - depth)
        Mb = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if mh.run_chain(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                          entity_atoms, relation_atoms):
            c_arg += 1
        if v.vamp_chain_forward_backward(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                                            entity_atoms, relation_atoms):
            c_vmp += 1
    return c_arg / n_trials, c_vmp / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_grid": [4096, 8192] if smoke else [4096, 8192, 16384, 32768, 65536],
              "depth": 50,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "n_trials": 5 if smoke else 15,
              "seed": 17}
    print(f"[config] depth={config['depth']} N_grid={config['N_grid']}", flush=True)
    arg_per_N = {}; vmp_per_N = {}
    for N in config["N_grid"]:
        arg_acc, vmp_acc = run_one_N(N, config["depth"], config["n_trials"],
                                          config["num_relations"], config["num_facts"],
                                          config["num_entities"], config["seed"], device)
        arg_per_N[str(N)] = arg_acc
        vmp_per_N[str(N)] = vmp_acc
        print(f"  N={N}: argmax={arg_acc:.3f}, vamp={vmp_acc:.3f}, gap={vmp_acc-arg_acc:+.3f}", flush=True)
    summary = {"argmax_per_N": arg_per_N, "vamp_per_N": vmp_per_N,
                "depth": config["depth"]}
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
    out_dir = get_output_dir("wave14_vamp_chain_N_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_vamp_present", max(summary["vamp_per_N"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_vamp_chain_N_sweep_v1")
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
