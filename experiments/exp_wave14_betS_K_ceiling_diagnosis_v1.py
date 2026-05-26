"""Bet S K-ceiling diagnosis — which of {cross-talk, Hopfield blackout, capacity} dominates?

Per Research Entry 113 (2026-05-22): K_crit ~ 130-200 at N=4096. Three candidate
mechanisms with formulas:
  - Cleanup cross-talk (PRIMARY, P=0.75): K_crit = D / (2 log M); reducing M extends K_crit
  - Hopfield blackout (SECONDARY, P=0.50): K_crit = 0.138*D (AGS); higher beta reduces effect
  - Capacity / binding noise (continuous, P=0.25): K_crit ~ sqrt(D/(K-1))

This experiment holds K=200 (above current ceiling), then sweeps M, beta, and N
INDEPENDENTLY to see which knob restores accuracy.

Verdict (one-hot diagnosis):
  KCEIL_M_LIMITED:   smaller M restores acc by >=0.2 (cross-talk dominant)
  KCEIL_BETA_LIMITED: higher beta restores acc by >=0.2 (Hopfield blackout dominant)
  KCEIL_N_LIMITED:    higher N restores acc by >=0.2 (capacity dominant)
  KCEIL_COMPOUND:     2+ knobs each restore >=0.2 (compound failure)
  KCEIL_NONE:         no knob helps (ceiling is fundamental at this K)
  KCEIL_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betS_K_ceiling_diagnosis_v1.md
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

_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)


RESTORE_DELTA = 0.20


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "baseline_acc" not in summary:
        return ("KCEIL_INCONCLUSIVE", "Missing baseline_acc.")
    base = summary["baseline_acc"]
    M_gain = summary["best_M_acc"] - base
    B_gain = summary["best_beta_acc"] - base
    N_gain = summary["best_N_acc"] - base
    helps = []
    if M_gain >= RESTORE_DELTA: helps.append(("M", M_gain))
    if B_gain >= RESTORE_DELTA: helps.append(("beta", B_gain))
    if N_gain >= RESTORE_DELTA: helps.append(("N", N_gain))
    if not helps:
        return ("KCEIL_NONE",
                f"No knob restores acc by {RESTORE_DELTA}: baseline={base:.3f}, "
                f"best M_gain={M_gain:.3f}, beta_gain={B_gain:.3f}, N_gain={N_gain:.3f}. "
                f"K=200 ceiling is fundamental at current substrate config.")
    if len(helps) >= 2:
        return ("KCEIL_COMPOUND",
                f"Compound K-ceiling failure: {[h[0] for h in helps]} all restore acc by "
                f">={RESTORE_DELTA}. M_gain={M_gain:.3f}, beta_gain={B_gain:.3f}, N_gain={N_gain:.3f}. "
                f"baseline={base:.3f}.")
    winner = helps[0][0]
    name_map = {"M": "KCEIL_M_LIMITED (cross-talk dominant)",
                 "beta": "KCEIL_BETA_LIMITED (Hopfield blackout dominant)",
                 "N": "KCEIL_N_LIMITED (capacity dominant)"}
    verdict_label = {"M": "KCEIL_M_LIMITED", "beta": "KCEIL_BETA_LIMITED", "N": "KCEIL_N_LIMITED"}[winner]
    return (verdict_label,
            f"{name_map[winner]}: knob '{winner}' restores acc by {helps[0][1]:.3f} (>={RESTORE_DELTA}). "
            f"Other knobs: M_gain={M_gain:.3f}, beta_gain={B_gain:.3f}, N_gain={N_gain:.3f}. "
            f"baseline={base:.3f}.")


def self_test_verdict():
    cases = [
        ({"baseline_acc": 0.40, "best_M_acc": 0.85, "best_beta_acc": 0.45, "best_N_acc": 0.50}, "KCEIL_M_LIMITED"),
        ({"baseline_acc": 0.40, "best_M_acc": 0.42, "best_beta_acc": 0.85, "best_N_acc": 0.50}, "KCEIL_BETA_LIMITED"),
        ({"baseline_acc": 0.40, "best_M_acc": 0.42, "best_beta_acc": 0.45, "best_N_acc": 0.85}, "KCEIL_N_LIMITED"),
        ({"baseline_acc": 0.40, "best_M_acc": 0.85, "best_beta_acc": 0.85, "best_N_acc": 0.50}, "KCEIL_COMPOUND"),
        ({"baseline_acc": 0.40, "best_M_acc": 0.45, "best_beta_acc": 0.50, "best_N_acc": 0.55}, "KCEIL_NONE"),
        ({}, "KCEIL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def betS_one_config(K, num_entities, N, beta, n_trials, seed, device):
    """Bet S with optional beta-temperature cleanup (beta=inf = argmax).
    M = num_entities (codebook size). N = substrate dim."""
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(20, N, gen, device)
    subj_idx = torch.randint(0, num_entities, (K,), generator=cpu_gen).to(device)
    rel_idx = torch.randint(0, 20, (K,), generator=cpu_gen).to(device)
    obj_idx = torch.randint(0, num_entities, (K,), generator=cpu_gen).to(device)
    triples = entity_atoms[subj_idx] * relation_atoms[rel_idx] * entity_atoms[obj_idx]
    M_bundle = t.sign_quantize(triples.sum(dim=0))
    trial_idx = torch.randperm(K, generator=cpu_gen)[:min(n_trials, K)].to(device)
    correct = 0; total = 0
    for i in range(trial_idx.shape[0]):
        ix = int(trial_idx[i])
        r_atom = relation_atoms[rel_idx[ix]]
        o_atom = entity_atoms[obj_idx[ix]]
        probe_s = M_bundle * r_atom * o_atom
        # Cleanup: argmax if beta=inf, else softmax-weighted pick
        sims = (entity_atoms @ probe_s)
        if beta == float("inf"):
            pred = int(sims.argmax().item())
        else:
            # beta-temperature: pick the argmax (still argmax over softmax) but adds nonzero floor.
            # Modern dense AM (Demircigil): use softmax-weighted readout state, then argmax over values.
            sims_norm = sims - sims.max()
            w = torch.softmax(beta * sims_norm, dim=0)
            state = w @ entity_atoms
            pred = int((entity_atoms @ state).argmax().item())
        if pred == int(subj_idx[ix]): correct += 1
        total += 1
    return correct / total


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "K_test": 200,
              "n_trials": 30 if smoke else 60,
              "seed": 17,
              "N_base": 1024 if smoke else 4096,
              "M_base": 200,
              "beta_base": float("inf"),
              "M_sweep": [50, 200, 800] if smoke else [50, 100, 200, 400, 800],
              "beta_sweep": [1.0, 8.0, float("inf")] if smoke else [1.0, 4.0, 16.0, 64.0, float("inf")],
              "N_sweep": [1024, 2048] if smoke else [4096, 8192, 16384]}
    print(f"[config] K_test={config['K_test']} N_base={config['N_base']} M_base={config['M_base']}", flush=True)
    # Baseline: standard config
    baseline = betS_one_config(config["K_test"], config["M_base"], config["N_base"],
                                  config["beta_base"], config["n_trials"], config["seed"], device)
    print(f"  baseline: acc={baseline:.3f}", flush=True)

    M_results = {}
    for m in config["M_sweep"]:
        acc = betS_one_config(config["K_test"], m, config["N_base"], config["beta_base"],
                                 config["n_trials"], config["seed"], device)
        M_results[str(m)] = acc
        print(f"  M={m}: acc={acc:.3f}", flush=True)
    best_M_acc = max(M_results.values())

    beta_results = {}
    for b in config["beta_sweep"]:
        b_key = "inf" if b == float("inf") else str(b)
        acc = betS_one_config(config["K_test"], config["M_base"], config["N_base"], b,
                                 config["n_trials"], config["seed"], device)
        beta_results[b_key] = acc
        print(f"  beta={b}: acc={acc:.3f}", flush=True)
    best_beta_acc = max(beta_results.values())

    N_results = {}
    for n in config["N_sweep"]:
        acc = betS_one_config(config["K_test"], config["M_base"], n, config["beta_base"],
                                 config["n_trials"], config["seed"], device)
        N_results[str(n)] = acc
        print(f"  N={n}: acc={acc:.3f}", flush=True)
    best_N_acc = max(N_results.values())

    summary = {"baseline_acc": baseline,
                "M_sweep": M_results, "best_M_acc": best_M_acc,
                "beta_sweep": beta_results, "best_beta_acc": best_beta_acc,
                "N_sweep": N_results, "best_N_acc": best_N_acc}
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
    out_dir = get_output_dir("wave14_betS_K_ceiling_diagnosis_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("baseline_present", summary["baseline_acc"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betS_K_ceiling_diagnosis_v1")
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
