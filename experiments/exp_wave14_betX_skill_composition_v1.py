"""Bet X Skill Composition - position-indexed binding for multi-step skill programs.

Per Research cycle 61: substrate stores program pointer + audit trace via
s = sum_i (skill_i * position_i). HYBRID executor: substrate stores trace;
external Python dispatches primitives.

Tests:
- Level 1: flat program of L=8 skills bound at L positions
- Level 2: meta-skill program — each meta = bundle of K base skills with own positions

Pre-reg: preregs/2026-05-21_wave14_betX_skill_composition_v1.md
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

PASS_SKILL_ACC = 0.80
PASS_AUDIT = 0.90
KILL_SKILL = 0.50
KILL_AUDIT = 0.50


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
    if "level1_skill_acc" not in summary:
        return ("BET_X_INCONCLUSIVE", "Missing metrics.")
    l1_acc = summary["level1_skill_acc"]
    l1_audit = summary["level1_audit_decomposable"]
    l2_acc = summary.get("level2_skill_acc", 0.0)
    l2_audit = summary.get("level2_audit_decomposable", 0.0)
    if l1_acc < KILL_SKILL or l1_audit < KILL_AUDIT:
        return ("BET_X_KILLED",
                f"Level 1 fails: skill_acc={l1_acc:.3f}<{KILL_SKILL} or "
                f"audit={l1_audit:.3f}<{KILL_AUDIT}. Bet X mechanism doesn't compose.")
    l1_pass = l1_acc >= PASS_SKILL_ACC and l1_audit >= PASS_AUDIT
    l2_pass = l2_acc >= PASS_SKILL_ACC and l2_audit >= PASS_AUDIT
    if l1_pass and l2_pass:
        return ("BET_X_COMPOSITION_PASS",
                f"Both levels pass: L1 skill={l1_acc:.3f}/audit={l1_audit:.3f}; "
                f"L2 skill={l2_acc:.3f}/audit={l2_audit:.3f}. Position-indexed binding "
                f"works at 2-level hierarchy.")
    if l1_pass:
        return ("BET_X_FLAT_PASS",
                f"Level 1 PASS but Level 2 fails: L1 acc={l1_acc:.3f}, "
                f"L2 acc={l2_acc:.3f} (<{PASS_SKILL_ACC}). Single-level works; "
                f"hierarchy breaks at depth 2.")
    return ("BET_X_INCONCLUSIVE",
            f"Pattern unclear: L1 skill={l1_acc:.3f} audit={l1_audit:.3f}, "
            f"L2 skill={l2_acc:.3f} audit={l2_audit:.3f}.")


def self_test_verdict():
    cases = [
        ({"level1_skill_acc": 0.95, "level1_audit_decomposable": 0.92,
          "level2_skill_acc": 0.85, "level2_audit_decomposable": 0.90},
         "BET_X_COMPOSITION_PASS"),
        ({"level1_skill_acc": 0.95, "level1_audit_decomposable": 0.92,
          "level2_skill_acc": 0.40, "level2_audit_decomposable": 0.45},
         "BET_X_FLAT_PASS"),
        ({"level1_skill_acc": 0.30, "level1_audit_decomposable": 0.40,
          "level2_skill_acc": 0.20, "level2_audit_decomposable": 0.20},
         "BET_X_KILLED"),
        ({}, "BET_X_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_atoms(k, n, gen, device):
    return 2.0 * (torch.rand((k, n), generator=gen, device=device) > 0.5).float() - 1.0


def encode_program(skill_indices, skill_atoms, position_atoms):
    """s = sum_i (skill_atoms[skill_indices[i]] * position_atoms[i]). Sign-quantize."""
    bound = skill_atoms[skill_indices] * position_atoms[:len(skill_indices)]
    summed = bound.sum(dim=0)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def decode_program(prog_atom, position_atoms, skill_atoms, L):
    """For each position 0..L-1: probe = prog * position_i, argmax against skill codebook."""
    predictions = []
    for i in range(L):
        probe = prog_atom * position_atoms[i]
        sims = skill_atoms @ probe
        predictions.append(int(sims.argmax().item()))
    return predictions


def run_one_seed(seed, config, device):
    N = config["N"]
    n_skills = config["n_skills"]
    max_L = config["max_program_length"]
    n_trials = config["n_trials_per_level"]
    n_meta = config["n_meta_skills"]
    L_meta = config["meta_program_length"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    skill_atoms = make_atoms(n_skills, N, gen, device)
    position_atoms = make_atoms(max_L, N, gen, device)

    # Level 1: flat program of L=max_L skills
    l1_correct = 0
    l1_total = 0
    l1_audit = []
    for _ in range(n_trials):
        skill_indices = torch.randint(0, n_skills, (max_L,), generator=cpu_gen).to(device)
        prog = encode_program(skill_indices, skill_atoms, position_atoms)
        decoded = decode_program(prog, position_atoms, skill_atoms, max_L)
        target = skill_indices.tolist()
        per_pos_correct = [int(decoded[i] == target[i]) for i in range(max_L)]
        l1_correct += sum(per_pos_correct)
        l1_total += max_L
        # Audit decomposable: count fraction of correctly decoded positions
        l1_audit.append(sum(per_pos_correct) / max_L)
    level1_skill_acc = l1_correct / l1_total
    level1_audit = sum(l1_audit) / len(l1_audit)

    # Level 2: meta-skill program
    # Build n_meta meta-skill atoms, each = bundle of skills with its own positions
    meta_position_atoms = make_atoms(L_meta, N, gen, device)
    meta_atoms_list = []
    meta_compositions = []  # for each meta: skill_indices it contains
    for j in range(n_meta):
        skill_indices = torch.randint(0, n_skills, (L_meta,), generator=cpu_gen).to(device)
        meta_atom = encode_program(skill_indices, skill_atoms, meta_position_atoms)
        meta_atoms_list.append(meta_atom)
        meta_compositions.append(skill_indices.tolist())
    meta_atoms = torch.stack(meta_atoms_list, dim=0)

    # Level 2 outer program: bundle of meta-skills at positions
    l2_correct = 0
    l2_total = 0
    l2_audit = []
    for _ in range(n_trials):
        meta_indices = torch.randperm(n_meta, generator=cpu_gen)[:max_L].to(device)
        outer_prog = encode_program(meta_indices, meta_atoms, position_atoms)
        # First decode meta indices at outer positions
        decoded_meta = decode_program(outer_prog, position_atoms, meta_atoms, max_L)
        # Then decode each meta's inner skill program
        per_meta_correct = []
        for pos in range(max_L):
            true_meta = int(meta_indices[pos])
            if decoded_meta[pos] != true_meta:
                # Outer-level decode wrong; inner can't recover
                per_meta_correct.append(0.0)
                continue
            inner_skills = decode_program(meta_atoms[true_meta], meta_position_atoms,
                                             skill_atoms, L_meta)
            inner_correct = sum(1 for k in range(L_meta) if inner_skills[k] == meta_compositions[true_meta][k])
            per_meta_correct.append(inner_correct / L_meta)
        avg = sum(per_meta_correct) / max_L
        l2_correct += sum(per_meta_correct)
        l2_total += max_L
        l2_audit.append(avg)
    level2_skill_acc = l2_correct / l2_total
    level2_audit = sum(l2_audit) / len(l2_audit)

    return {"level1_skill_acc": level1_skill_acc,
             "level1_audit_decomposable": level1_audit,
             "level2_skill_acc": level2_skill_acc,
             "level2_audit_decomposable": level2_audit}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "n_skills": 5,
              "max_program_length": 4 if smoke else 8,
              "n_meta_skills": 5,
              "meta_program_length": 4 if smoke else 6,
              "n_trials_per_level": 10 if smoke else 50,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: L1 skill={r['level1_skill_acc']:.3f} "
              f"audit={r['level1_audit_decomposable']:.3f}; "
              f"L2 skill={r['level2_skill_acc']:.3f} "
              f"audit={r['level2_audit_decomposable']:.3f}", flush=True)
    # Mean across seeds
    summary = {
        "level1_skill_acc": sum(r["level1_skill_acc"] for r in per_seed.values()) / len(per_seed),
        "level1_audit_decomposable": sum(r["level1_audit_decomposable"] for r in per_seed.values()) / len(per_seed),
        "level2_skill_acc": sum(r["level2_skill_acc"] for r in per_seed.values()) / len(per_seed),
        "level2_audit_decomposable": sum(r["level2_audit_decomposable"] for r in per_seed.values()) / len(per_seed),
        "per_seed": per_seed,
    }
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
    out_dir = get_output_dir("wave14_betX_skill_composition_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("L1_skill_acc", summary["level1_skill_acc"], 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betX_skill_composition_v1")
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
