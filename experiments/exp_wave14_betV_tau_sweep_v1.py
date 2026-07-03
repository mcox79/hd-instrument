"""Bet V post-hoc tau-sweep (Rescue 1, research_betV_rescue_sketches_2026-05-23.md).

Bet V status: PARTIAL gap=0.424 at cycle 103, N=4096.
Research Rescue 1: there may exist a threshold tau* in [0.60, 0.80] such that
queries with stored_confidence >= tau* achieve acc_above_tau >= 0.85.

This experiment sweeps tau in [0.50, 0.90] step=0.05 and measures:
  - fraction_above_tau: fraction of probes that meet the confidence gate
  - acc_above_tau: argmax accuracy among gated probes

HARD PASS: exists tau* in [0.60, 0.80] with acc_above_tau >= 0.85 AND
           fraction_above_tau >= 0.30 (non-trivial gate, >=30% pass).
HARD FAIL: no tau in [0.60, 0.80] achieves acc >= 0.85 OR fraction >= 0.30.

Verdict labels:
  BET_V_TAU_PASS     -- HARD PASS criteria met; tau* found
  BET_V_TAU_PARTIAL  -- acc >= 0.85 found but fraction < 0.30 (too restrictive gate)
  BET_V_TAU_KILL     -- no tau achieves acc >= 0.85 in [0.60, 0.80]
  BET_V_TAU_INCONCLUSIVE

Pure CPU. No GPU required.
Memory budget: W = N x N float32; N=4096 -> 64 MB. Peak ~200 MB.
Expected runtime: ~5-10 min CPU at FULL.
Smoke: ~1 min (N=1024, small config).
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
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

TAU_RANGE = [round(0.50 + 0.05 * i, 2) for i in range(9)]   # 0.50 .. 0.90
TAU_TARGET_LOW = 0.60
TAU_TARGET_HIGH = 0.80
ACC_THRESHOLD = 0.85
FRAC_THRESHOLD = 0.30   # gate must pass >= 30% of probes to count


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing keys: {set(d.keys())}")


def compute_verdict(summary):
    if "tau_sweep" not in summary:
        return ("BET_V_TAU_INCONCLUSIVE", "Missing tau_sweep.")
    sweep = summary["tau_sweep"]
    # Find best tau in target range
    target = {tau: v for tau, v in sweep.items()
               if TAU_TARGET_LOW <= float(tau) <= TAU_TARGET_HIGH}
    if not target:
        return ("BET_V_TAU_INCONCLUSIVE", "No tau in target range.")
    best_tau = max(target, key=lambda t: target[t]["acc"])
    best = target[best_tau]
    acc = best["acc"]
    frac = best["frac"]
    if acc >= ACC_THRESHOLD and frac >= FRAC_THRESHOLD:
        return ("BET_V_TAU_PASS",
                f"HARD PASS: tau*={best_tau} -> acc={acc:.3f} >= {ACC_THRESHOLD}, "
                f"frac={frac:.3f} >= {FRAC_THRESHOLD}. "
                "Confidence-gating rescues Bet V accuracy.")
    if acc >= ACC_THRESHOLD and frac < FRAC_THRESHOLD:
        return ("BET_V_TAU_PARTIAL",
                f"acc={acc:.3f} >= {ACC_THRESHOLD} at tau*={best_tau} but "
                f"frac={frac:.3f} < {FRAC_THRESHOLD}. Gate too restrictive: "
                "abstains on too many queries to be a useful rescue.")
    return ("BET_V_TAU_KILL",
            f"No tau in [{TAU_TARGET_LOW}, {TAU_TARGET_HIGH}] achieves acc >= {ACC_THRESHOLD}. "
            f"Best: tau={best_tau} -> acc={acc:.3f}, frac={frac:.3f}. "
            "Confidence-gating cannot rescue Bet V.")


def self_test_verdict():
    cases = [
        # tau_sweep dict with some tau achieving pass
        ({"tau_sweep": {"0.70": {"acc": 0.90, "frac": 0.50}}}, "BET_V_TAU_PASS"),
        ({"tau_sweep": {"0.70": {"acc": 0.90, "frac": 0.15}}}, "BET_V_TAU_PARTIAL"),
        ({"tau_sweep": {"0.70": {"acc": 0.70, "frac": 0.50}}}, "BET_V_TAU_KILL"),
        ({}, "BET_V_TAU_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"Expected {exp}, got {a} for input {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_codebook(K, N, gen, device):
    return (torch.randint(0, 2, (K, N), generator=gen, device=device).float() * 2 - 1)


def confidence(probe, codebook):
    """Confidence = (sim_max - sim_2nd) / max(|sim|). Range [0, 1]."""
    sims = codebook @ probe
    top2 = sims.topk(2).values
    norm = float(sims.abs().max())
    if norm < 1e-9:
        return 0.0
    return float(top2[0] - top2[1]) / norm


def run_one_seed(seed, cfg, device):
    N = cfg["N"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = make_bsc_codebook(cfg["num_entities"], N, gen, device)
    relation_atoms = make_bsc_codebook(cfg["num_relations"], N, gen, device)

    # Build W from stored facts
    triples = []
    fact_set = {}
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    for _ in range(cfg["num_facts"]):
        s = int(torch.randint(0, cfg["num_entities"], (1,), generator=cpu_gen))
        r = int(torch.randint(0, cfg["num_relations"], (1,), generator=cpu_gen))
        o = int(torch.randint(0, cfg["num_entities"], (1,), generator=cpu_gen))
        if (s, r) not in fact_set:
            fact_set[(s, r)] = o
            atom = entity_atoms[s] * relation_atoms[r] * entity_atoms[o]
            triples.append(torch.sign(atom))
    if not triples:
        return {}
    W_vec = torch.sign(torch.stack(triples, 0).sum(0))
    W = W_vec.unsqueeze(0) * W_vec.unsqueeze(1) / N  # rank-1 Hebbian approx

    # Full Hebbian W (sum of outer products / N)
    W_full = torch.stack(triples, 0)  # (K_facts, N)
    W = W_full.T @ W_full / N  # (N, N)

    # Probe: for each stored (s, r) pair, compute confidence and check retrieval
    results = []  # (confidence, correct)
    for (s, r), o_true in list(fact_set.items())[:cfg["n_probes"]]:
        probe = W @ (entity_atoms[s] * relation_atoms[r])
        conf = confidence(probe, entity_atoms)
        pred = int((entity_atoms @ probe).argmax().item())
        correct = (pred == o_true)
        results.append((conf, correct))

    return results


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")
    cfg = {
        "mode": "smoke" if smoke else "full",
        "N": 1024 if smoke else 4096,
        "num_entities": 100 if smoke else 300,
        "num_relations": 5 if smoke else 20,
        "num_facts": 30 if smoke else 100,
        "n_probes": 30 if smoke else 100,
        "seeds": [17] if smoke else [17, 23, 31, 42, 57],
    }

    all_results = []  # list of (conf, correct) across seeds
    for seed in cfg["seeds"]:
        results = run_one_seed(seed, cfg, device)
        all_results.extend(results)
        if results:
            confs = [r[0] for r in results]
            accs = [r[1] for r in results]
            print(f"  seed={seed}: n={len(results)}, mean_conf={sum(confs)/len(confs):.3f}, "
                  f"acc={sum(accs)/len(accs):.3f}", flush=True)

    if not all_results:
        return {"tau_sweep": {}}, "BET_V_TAU_INCONCLUSIVE", "No results.", time.monotonic() - t0, cfg

    # Tau sweep
    tau_sweep = {}
    for tau in TAU_RANGE:
        gated = [(c, ok) for c, ok in all_results if c >= tau]
        if len(gated) == 0:
            tau_sweep[str(tau)] = {"acc": 0.0, "frac": 0.0, "n": 0}
        else:
            acc = sum(ok for _, ok in gated) / len(gated)
            frac = len(gated) / len(all_results)
            tau_sweep[str(tau)] = {"acc": round(acc, 4), "frac": round(frac, 4), "n": len(gated)}
            print(f"  tau={tau:.2f}: n_gated={len(gated)}/{len(all_results)} ({frac:.2f}), "
                  f"acc={acc:.3f}", flush=True)

    summary = {"tau_sweep": tau_sweep, "total_probes": len(all_results)}
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
    out_dir = get_output_dir("wave14_betV_tau_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("total_probes", float(summary.get("total_probes", 0)), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betV_tau_sweep_v1")
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
