"""Bet V Self-Reflective Memory — substrate queries return calibrated confidence.

Per cap_map v78 Bet V: substrate can answer "do I know X?" without committing
to a value, via confidence based on retrieval magnitude / spectrum.

Substrate analog: cleanup probe returns sim_max and sim_2nd; ratio is
confidence. Stored facts -> high confidence; unstored -> low.

Pre-reg: preregs/2026-05-22_wave14_betV_largeN.md
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

_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "stored_confidence" not in summary or "unstored_confidence" not in summary:
        return ("BET_V_INCONCLUSIVE", "Missing.")
    stored = summary["stored_confidence"]
    unstored = summary["unstored_confidence"]
    gap = stored - unstored
    if gap >= 0.30 and stored >= 0.70:
        return ("BET_V_PASS",
                f"Self-reflective confidence separates stored ({stored:.3f}) from unstored "
                f"({unstored:.3f}); gap={gap:.3f}. Substrate can introspect knowledge.")
    if gap < 0.05:
        return ("BET_V_KILLED",
                f"Stored vs unstored confidence indistinguishable: {stored:.3f} vs {unstored:.3f}. "
                f"Substrate cannot self-report knowledge.")
    return ("BET_V_PARTIAL",
            f"Some separation: stored={stored:.3f}, unstored={unstored:.3f}, gap={gap:.3f}.")


def self_test_verdict():
    cases = [
        ({"stored_confidence": 0.85, "unstored_confidence": 0.40}, "BET_V_PASS"),
        ({"stored_confidence": 0.50, "unstored_confidence": 0.48}, "BET_V_KILLED"),
        ({"stored_confidence": 0.60, "unstored_confidence": 0.40}, "BET_V_PARTIAL"),
        ({}, "BET_V_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def confidence(probe, codebook):
    """sim_max - sim_2nd; normalized to [0, 1]. High = confident retrieval."""
    sims = codebook @ probe
    top2 = sims.topk(2).values
    raw_gap = float(top2[0] - top2[1])
    norm = float(sims.abs().max())
    return raw_gap / max(norm, 1e-9)


def run_one_seed(seed, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    n_probes = config["n_probes"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)

    # Store num_facts
    facts = []
    triples = []
    for _ in range(num_facts):
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        facts.append((s, r, o))
        triples.append(t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o]))
    M = t.sign_quantize(torch.stack(triples, dim=0).sum(dim=0))

    # Stored facts: query each and measure confidence
    stored_confs = []
    for s, r, o in facts[:n_probes]:
        probe = M * entity_atoms[s] * relation_atoms[r]
        stored_confs.append(confidence(probe, entity_atoms))

    # Unstored: random (s, r) NOT in facts
    fact_set = {(s, r): o for s, r, o in facts}
    unstored_confs = []
    attempts = 0
    while len(unstored_confs) < n_probes and attempts < n_probes * 10:
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        if (s, r) not in fact_set:
            probe = M * entity_atoms[s] * relation_atoms[r]
            unstored_confs.append(confidence(probe, entity_atoms))
        attempts += 1
    return {"stored": sum(stored_confs) / max(len(stored_confs), 1),
             "unstored": sum(unstored_confs) / max(len(unstored_confs), 1)}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 8192,
              "num_entities": 50 if smoke else 200,
              "num_relations": 5 if smoke else 20,
              "num_facts": 30 if smoke else 100,
              "n_probes": 20 if smoke else 50,
              "seeds": [17] if smoke else [17, 23, 31]}
    accs = []
    for s in config["seeds"]:
        r = run_one_seed(s, config, device)
        accs.append(r)
        print(f"  seed={s}: stored_conf={r['stored']:.3f} unstored_conf={r['unstored']:.3f}", flush=True)
    summary = {"stored_confidence": sum(a["stored"] for a in accs) / len(accs),
                "unstored_confidence": sum(a["unstored"] for a in accs) / len(accs),
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
    out_dir = get_output_dir("wave14_betV_largeN_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("stored_conf", summary["stored_confidence"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betV_largeN")
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
