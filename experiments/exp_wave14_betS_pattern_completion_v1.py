"""Bet S Pattern Completion — Plate 1995 HRR inversion for all 3 slot directions.

Substrate-native bidirectional recall: store facts as e = subj*rel*obj (BSC bind);
bundle M = sign(sum e_i); recover any slot from the other 2.

Per cap_map v75 + META Section 7 priority #1.

Pre-reg: preregs/2026-05-21_wave14_betS_pattern_completion_v1.md
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

PASS_SLOT = 0.85
PARTIAL_FLOOR = 0.65
SYMMETRY_TOL = 0.05


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
    by_K = summary.get("per_K")
    if not by_K:
        return ("BET_S_INCONCLUSIVE", "Missing per_K.")
    fails = []
    partials = []
    kills = []
    for K, slot_accs in by_K.items():
        Ki = int(K)
        slots = ["subject", "relation", "object"]
        accs = [slot_accs.get(s, 0.0) for s in slots]
        sub_a, rel_a, obj_a = accs
        max_a = max(accs)
        min_a = min(accs)
        symmetric = (max_a - min_a) <= SYMMETRY_TOL
        any_below_pass = any(a < PASS_SLOT for a in accs)
        any_kill = any(a < PARTIAL_FLOOR for a in accs)
        if any_kill and Ki <= 200:
            kills.append(K)
        elif any_below_pass:
            partials.append(K)
        elif not symmetric:
            fails.append((K, "asymmetric"))
    if kills:
        return ("BET_S_KILLED",
                f"Killed at K={kills}: some slot < {PARTIAL_FLOOR} at K<=200. "
                f"per_K: {by_K}")
    if not partials and not fails:
        return ("BET_S_PATTERN_COMPLETION_PASS",
                f"All K {list(by_K.keys())} pass all 3 slots >= {PASS_SLOT} "
                f"with symmetry. Bidirectional recall validated.")
    return ("BET_S_PARTIAL",
            f"Partial: K={partials} below {PASS_SLOT}, asymmetric={fails}. "
            f"per_K: {by_K}")


def self_test_verdict():
    def mk(*K_slot_accs):
        d = {}
        for K, (s, r, o) in K_slot_accs:
            d[K] = {"subject": s, "relation": r, "object": o}
        return {"per_K": d}
    cases = [
        (mk((8, (0.95, 0.94, 0.93)), (50, (0.90, 0.91, 0.92)),
             (200, (0.88, 0.87, 0.86)), (800, (0.86, 0.85, 0.87))),
         "BET_S_PATTERN_COMPLETION_PASS"),
        (mk((8, (0.95, 0.95, 0.95)), (50, (0.60, 0.90, 0.90)),
             (200, (0.50, 0.85, 0.85))),
         "BET_S_KILLED"),
        (mk((8, (0.80, 0.80, 0.80)), (50, (0.75, 0.75, 0.75))),
         "BET_S_PARTIAL"),
        ({}, "BET_S_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_K(K, num_entities, num_relations, N, n_trials, seed, device):
    """Build a fact-bundle from K triples; test 3 slot-direction queries."""
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)
    # Build K facts
    subj_idx = torch.randint(0, num_entities, (K,), generator=cpu_gen).to(device)
    rel_idx = torch.randint(0, num_relations, (K,), generator=cpu_gen).to(device)
    obj_idx = torch.randint(0, num_entities, (K,), generator=cpu_gen).to(device)
    # Bundle M = sign(sum subj * rel * obj)
    triples = entity_atoms[subj_idx] * relation_atoms[rel_idx] * entity_atoms[obj_idx]
    M = t.sign_quantize(triples.sum(dim=0))

    # Probe each slot direction for n_trials random facts (sampled from K stored)
    trial_idx = torch.randperm(K, generator=cpu_gen)[:min(n_trials, K)].to(device)
    n_trials_actual = trial_idx.shape[0]
    subj_correct = 0
    rel_correct = 0
    obj_correct = 0
    for i in range(n_trials_actual):
        ix = int(trial_idx[i])
        s_atom = entity_atoms[subj_idx[ix]]
        r_atom = relation_atoms[rel_idx[ix]]
        o_atom = entity_atoms[obj_idx[ix]]
        # Subject given (rel, obj)
        probe_s = M * r_atom * o_atom
        pred_s = int((entity_atoms @ probe_s).argmax().item())
        if pred_s == int(subj_idx[ix]): subj_correct += 1
        # Relation given (subj, obj)
        probe_r = M * s_atom * o_atom
        pred_r = int((relation_atoms @ probe_r).argmax().item())
        if pred_r == int(rel_idx[ix]): rel_correct += 1
        # Object given (subj, rel)
        probe_o = M * s_atom * r_atom
        pred_o = int((entity_atoms @ probe_o).argmax().item())
        if pred_o == int(obj_idx[ix]): obj_correct += 1
    return {"subject": subj_correct / n_trials_actual,
             "relation": rel_correct / n_trials_actual,
             "object": obj_correct / n_trials_actual,
             "K": K, "n_trials": n_trials_actual}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "num_entities": 200,
              "num_relations": 50,
              "K_sweep": [8, 50] if smoke else [8, 50, 200, 800],
              "n_trials_per_K": 20 if smoke else 100,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_K_seed = {K: [] for K in config["K_sweep"]}
    for seed in config["seeds"]:
        for K in config["K_sweep"]:
            r = run_one_K(K, config["num_entities"], config["num_relations"],
                            config["N"], config["n_trials_per_K"], seed, device)
            per_K_seed[K].append(r)
            print(f"  seed={seed} K={K}: subj={r['subject']:.3f} rel={r['relation']:.3f} "
                  f"obj={r['object']:.3f}", flush=True)
    # Mean across seeds
    per_K_mean = {}
    for K, seed_results in per_K_seed.items():
        per_K_mean[str(K)] = {
            "subject": sum(r["subject"] for r in seed_results) / len(seed_results),
            "relation": sum(r["relation"] for r in seed_results) / len(seed_results),
            "object": sum(r["object"] for r in seed_results) / len(seed_results),
        }
    summary = {"per_K": per_K_mean, "per_K_seed": {str(K): seed_results
                                                          for K, seed_results in per_K_seed.items()}}
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
    out_dir = get_output_dir("wave14_betS_pattern_completion_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_K = str(config["K_sweep"][0])
    sub_acc = summary["per_K"][first_K]["subject"]
    oracle.assert_baseline_high("K8_subject", sub_acc, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betS_pattern_completion_v1")
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
