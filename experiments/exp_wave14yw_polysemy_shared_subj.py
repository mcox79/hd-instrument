"""Polysemy test: does substrate disambiguate two facts with same (subj, rel)?

Store (A, R, B) and (A, R, C) for same A, R. Query (A, R): what does
substrate return? If it cleanly returns one (typically the most-recent
or one chosen by alignment), single-value retrieval works. If it returns
noise, the substrate naturally averages and can't distinguish.

Tests substrate handling of conflicting facts in M.

Pre-reg: preregs/2026-05-21_wave14yw_polysemy_shared_subj.md
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    m = summary.get("metrics")
    if not m:
        return ("POLYSEMY_INCONCLUSIVE", "Missing.")
    one_of_pair = m.get("returns_one_of_pair", 0.0)
    consistent = m.get("consistent_choice", 0.0)
    other_entity = m.get("returns_other_entity", 0.0)
    if one_of_pair >= 0.85:
        if consistent >= 0.85:
            return ("POLYSEMY_PICKS_ONE_CONSISTENTLY",
                    f"Substrate returns one of the conflict pair {one_of_pair:.3f} of the "
                    f"time, AND consistently the same one {consistent:.3f}. Polysemy "
                    f"resolved by deterministic choice.")
        return ("POLYSEMY_PICKS_ONE_NONDET",
                f"Substrate returns one of the conflict pair {one_of_pair:.3f} of the "
                f"time, but inconsistently (consistency={consistent:.3f}). Substrate "
                f"can't deterministically disambiguate; picks one based on noise alignment.")
    if other_entity >= 0.50:
        return ("POLYSEMY_RETURNS_NOISE",
                f"Substrate returns NEITHER pair member {other_entity:.3f} of the time. "
                f"Conflict creates noise that overwhelms cleanup; substrate can't store "
                f"polysemous (A, R) -> {{B, C}} cleanly.")
    return ("POLYSEMY_INCONCLUSIVE",
            f"one_of_pair={one_of_pair:.3f}, consistent={consistent:.3f}, "
            f"other={other_entity:.3f}.")


def self_test_verdict():
    cases = [
        ({"metrics": {"returns_one_of_pair": 0.95, "consistent_choice": 0.95,
                        "returns_other_entity": 0.05}},
         "POLYSEMY_PICKS_ONE_CONSISTENTLY"),
        ({"metrics": {"returns_one_of_pair": 0.90, "consistent_choice": 0.50,
                        "returns_other_entity": 0.10}},
         "POLYSEMY_PICKS_ONE_NONDET"),
        ({"metrics": {"returns_one_of_pair": 0.30, "consistent_choice": 0.30,
                        "returns_other_entity": 0.70}},
         "POLYSEMY_RETURNS_NOISE"),
        ({}, "POLYSEMY_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 4096,
              "num_entities": 50 if smoke else 200,
              "num_relations": 5 if smoke else 20,
              "num_polysemous_pairs": 5 if smoke else 30,
              "num_distractor_facts": 10 if smoke else 70,
              "n_trials": 20 if smoke else 100,
              "seeds": [17] if smoke else [17, 23, 31]}
    print(f"[config] {config}", flush=True)

    one_of_pair_counts = []
    consistent_counts = []
    other_entity_counts = []

    for seed in config["seeds"]:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)
        entity_atoms = v3.make_bsc_codebook(config["num_entities"], config["N"],
                                              gen, device)
        relation_atoms = v3.make_bsc_codebook(config["num_relations"], config["N"],
                                                gen, device)

        for trial in range(config["n_trials"]):
            # Build M with polysemous pairs + distractors
            triples = []
            polysemous_records = []  # (subj_idx, rel_idx, obj_b_idx, obj_c_idx)
            used_subj_rel = set()
            for _ in range(config["num_polysemous_pairs"]):
                # Pick subj, rel that haven't been used as polysemous pair
                attempts = 0
                while True:
                    s = int(torch.randint(0, config["num_entities"], (1,), generator=cpu_gen).item())
                    r = int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                    if (s, r) not in used_subj_rel:
                        used_subj_rel.add((s, r))
                        break
                    attempts += 1
                    if attempts > 100: break
                # Pick two distinct objects
                while True:
                    o_b = int(torch.randint(0, config["num_entities"], (1,), generator=cpu_gen).item())
                    o_c = int(torch.randint(0, config["num_entities"], (1,), generator=cpu_gen).item())
                    if o_b != o_c and o_b != s and o_c != s:
                        break
                polysemous_records.append((s, r, o_b, o_c))
                # Add both triples
                t1 = v3.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o_b])
                t2 = v3.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o_c])
                triples.append(t1)
                triples.append(t2)

            # Distractor triples
            for _ in range(config["num_distractor_facts"]):
                ds = int(torch.randint(0, config["num_entities"], (1,), generator=cpu_gen).item())
                dr = int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                do = int(torch.randint(0, config["num_entities"], (1,), generator=cpu_gen).item())
                triples.append(v3.sign_quantize(entity_atoms[ds] * relation_atoms[dr] *
                                                  entity_atoms[do]))

            M = v3.sign_quantize(torch.stack(triples, dim=0).sum(dim=0))

            # Query each polysemous pair
            for (s, r, o_b, o_c) in polysemous_records:
                probe = M * (entity_atoms[s] * relation_atoms[r])
                pred = v3.cleanup_argmax(probe, entity_atoms)
                returns_one_of_pair = (pred == o_b or pred == o_c)
                consistent = (pred == o_b)  # convention: count "consistent" = picks first
                returns_other = not returns_one_of_pair
                one_of_pair_counts.append(1.0 if returns_one_of_pair else 0.0)
                consistent_counts.append(1.0 if (returns_one_of_pair and consistent) else 0.0)
                other_entity_counts.append(1.0 if returns_other else 0.0)

    n = len(one_of_pair_counts)
    summary = {"metrics": {
        "returns_one_of_pair": sum(one_of_pair_counts) / n if n else 0.0,
        "consistent_choice": sum(consistent_counts) / sum(one_of_pair_counts)
                                  if sum(one_of_pair_counts) > 0 else 0.0,
        "returns_other_entity": sum(other_entity_counts) / n if n else 0.0,
        "n_polysemous_queries": n,
    }}
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
    out_dir = get_output_dir("wave14yw_polysemy_shared_subj_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    n = summary["metrics"]["n_polysemous_queries"]
    if n < 5:
        raise AssertionError(f"SANITY FAIL: only {n} polysemous queries collected.")
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yw_polysemy_shared_subj")
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
