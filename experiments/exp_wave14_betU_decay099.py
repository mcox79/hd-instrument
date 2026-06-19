"""Bet U Working Memory + Decay — substrate items fade with explicit decay.

Per cap_map v78 Bet U: short-term working memory where stored items decay
exponentially. Test: store items in order; query at various time-offsets;
verify recent items recall well, old items fade.

Substrate analog: bundle accumulator B_t+1 = decay * B_t + new_fact.
At time t: bundle reflects weighted recent items.

Pre-reg: preregs/2026-05-22_wave14_betU_decay099.md
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


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "recent_acc" not in summary or "old_acc" not in summary:
        return ("BET_U_INCONCLUSIVE", "Missing accs.")
    recent = summary["recent_acc"]
    old = summary["old_acc"]
    ratio = recent / max(old, 1e-9) if old > 0 else float('inf')
    if recent >= 0.80 and old <= 0.30:
        return ("BET_U_PASS",
                f"Working memory decay validated: recent={recent:.3f}>=0.80, old={old:.3f}<=0.30. "
                f"Substrate shows expected recency gradient.")
    if recent < 0.50:
        return ("BET_U_KILLED",
                f"Even recent items not recalled: recent={recent:.3f}<0.50.")
    return ("BET_U_PARTIAL",
            f"Partial: recent={recent:.3f}, old={old:.3f}, ratio={ratio:.2f}.")


def self_test_verdict():
    cases = [
        ({"recent_acc": 0.95, "old_acc": 0.15}, "BET_U_PASS"),
        ({"recent_acc": 0.30, "old_acc": 0.10}, "BET_U_KILLED"),
        ({"recent_acc": 0.70, "old_acc": 0.50}, "BET_U_PARTIAL"),
        ({}, "BET_U_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
    N = config["N"]
    decay = config["decay"]
    n_items = config["n_items"]
    n_relations = config["n_relations"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(n_items + 50, N, gen, device)
    relation_atoms = t.make_bsc_codebook(n_relations, N, gen, device)

    # Sequential storage: B_t+1 = decay * B_t + new fact (as float bundle, then sign at end)
    B = torch.zeros(N, device=device)
    facts = []
    for i in range(n_items):
        s = int(torch.randint(0, n_items, (1,), generator=cpu_gen))
        r = int(torch.randint(0, n_relations, (1,), generator=cpu_gen))
        o = int(torch.randint(0, n_items, (1,), generator=cpu_gen))
        facts.append((s, r, o))
        triple = (entity_atoms[s] * relation_atoms[r] * entity_atoms[o]).float()
        B = decay * B + triple

    B_quant = t.sign_quantize(B)

    # Query: most recent n_recent items vs oldest n_old items
    n_recent = min(5, n_items // 4)
    n_old = min(5, n_items // 4)
    recent_correct = 0
    old_correct = 0
    for idx in range(n_items - n_recent, n_items):
        s, r, o = facts[idx]
        probe = B_quant * entity_atoms[s] * relation_atoms[r]
        if int((entity_atoms @ probe).argmax().item()) == o:
            recent_correct += 1
    for idx in range(n_old):
        s, r, o = facts[idx]
        probe = B_quant * entity_atoms[s] * relation_atoms[r]
        if int((entity_atoms @ probe).argmax().item()) == o:
            old_correct += 1
    return {"recent": recent_correct / n_recent, "old": old_correct / n_old}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "decay": 0.99,
              "n_items": 50 if smoke else 200,
              "n_relations": 5 if smoke else 20,
              "seeds": [17] if smoke else [17, 23, 31]}
    accs = []
    for s in config["seeds"]:
        r = run_one_seed(s, config, device)
        accs.append(r)
        print(f"  seed={s}: recent={r['recent']:.3f} old={r['old']:.3f}", flush=True)
    summary = {"recent_acc": sum(a["recent"] for a in accs) / len(accs),
                "old_acc": sum(a["old"] for a in accs) / len(accs),
                "per_seed": accs}
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
    out_dir = get_output_dir("wave14_betU_decay099_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("recent_acc", summary["recent_acc"], 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betU_decay099")
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
