"""K6 compositional generalization axis 2: hierarchical composition pre-binding.

Context: K6 compositional hold-out at 🟡 PARTIAL. hold_out_acc ranges from
0.116 (N=512, v190 V8) to 0.128 (N=8192, v193 V3). Dim-scaling axis is
exhausted. Axis 2 (hierarchical composition pre-binding) is the leading
remaining leverage path per v193 strategy narrative.

Axis 2 hypothesis: the K6 baseline (v190) uses simple bind(obj, attr) = obj * attr
(elementwise BSC product). Hierarchical pre-binding creates an intermediate
structural representation before storage:
  1. Pre-bind objects into GROUPS of N_GROUP objects (group prototype = mean/majority
     of group members).
  2. Bind (group_proto, individual_offset) -> object_slot.
  3. Store (object_slot, attr) -> value as before.
  4. At query time: resolve object_slot from (group_proto, individual_offset) first,
     then query (object_slot, attr) -> value.

This creates a TWO-LEVEL compositional hierarchy that allows the substrate to
use the group structure for generalization: novel (obj, attr) compositions can
be resolved via group_proto context even if the specific (obj, attr) pair was
unseen during training.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered before running.

Pre-reg:
    HARD-PASS: mean hold_out_acc >= 0.20 (3x chance; baseline v193 0.128=2x chance;
               clear improvement over axis-1-saturated baseline).
               -> K6 axis 2 hierarchical pre-binding PASSES; mechanism-class path
               unlocked; K6 🟡 PARTIAL rehab candidate.
    HARD-FAIL: mean hold_out_acc <= 0.08 (within 1.3x chance; no improvement
               over flat axis-1-N-scaling saturation baseline).
               -> K6 axis 2 REJECTED; sequence axis 3 (cleanup-iteration).
    MIDDLE: hold_out_acc in (0.08, 0.20); some improvement but below clear-pass.

Pre-reg self-test cells (per [[feedback-strategy-spec-formula-selftests]]):
    HARD-PASS: hold_out_acc=0.25 -> K6_HIER_HARD_PASS
    HARD-FAIL: hold_out_acc=0.07 -> K6_HIER_HARD_FAIL
    MIDDLE:    hold_out_acc=0.12 -> K6_HIER_MIDDLE_BAND

Queue: overnight_queue (GPU; pure-numpy similarity queries; multi-seed sweep;
>5 seeds x composite 2-level structure lookup).
ETA: ~60-90 min GPU.
Pre-reg file: preregs/2026-05-24_wave14_k6_axis2_hierprebin_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, os, time, math
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# ───── design parameters (exp_dev autonomy) ─────
N_OBJECTS = 16
N_ATTRS = 16
N_GROUP = 4          # objects per group: 16 objects -> 4 groups of 4
N_GROUPS = N_OBJECTS // N_GROUP  # = 4 groups
N_FULL = 4096
N_SMOKE = 512
TRAIN_FRAC_FULL = 0.75
TRAIN_FRAC_SMOKE = 0.75
EPOCHS_FULL = 30
EPOCHS_SMOKE = 5
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_HOLDOUT_ACC = 0.20   # 3x chance (chance = 1/16 = 0.0625)
FAIL_HOLDOUT_ACC = 0.08   # 1.3x chance
CHANCE = 1.0 / N_ATTRS   # = 0.0625


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


def make_bsc_atoms(k, n, gen):
    """BSC atoms: {-1,+1}^n, k atoms."""
    raw = torch.rand((k, n), generator=gen)
    return 2.0 * (raw > 0.5).float() - 1.0


def group_prototype(atoms: torch.Tensor, indices: list) -> torch.Tensor:
    """Majority-vote prototype of atoms at given indices."""
    stack = atoms[indices]   # [k, N]
    proto = stack.mean(dim=0).sign()
    proto[proto == 0] = 1.0  # resolve ties
    return proto


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("K6_HIER_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    hold_acc = sum(s["hold_out_acc"] for s in seeds) / len(seeds)
    train_acc = sum(s["train_acc"] for s in seeds) / len(seeds)
    detail = (f"hold_out_acc={hold_acc:.3f} train_acc={train_acc:.3f} "
              f"chance={CHANCE:.4f} "
              f"improvement_vs_chance={hold_acc/CHANCE:.1f}x")
    if hold_acc >= PASS_HOLDOUT_ACC:
        return ("K6_HIER_HARD_PASS",
                f"Hierarchical pre-binding UNLOCKS compositional generalization: {detail}. "
                f">={PASS_HOLDOUT_ACC:.2f} (3x chance). K6 axis 2 mechanism-class path.")
    if hold_acc <= FAIL_HOLDOUT_ACC:
        return ("K6_HIER_HARD_FAIL",
                f"Hierarchical pre-binding REJECTED: {detail}. "
                f"<={FAIL_HOLDOUT_ACC:.2f} (1.3x chance). K6 axis 3 cleanup-iter next.")
    return ("K6_HIER_MIDDLE_BAND",
            f"Partial improvement: {detail}. In ({FAIL_HOLDOUT_ACC:.2f}, {PASS_HOLDOUT_ACC:.2f}).")


def self_test_verdict():
    """Self-test cells (per [[feedback-strategy-spec-formula-selftests]]):
       Input hold_out_acc -> Expected verdict label.
    """
    def mk(ha, ta=0.90):
        return {"per_seed": {"17": {"hold_out_acc": ha, "train_acc": ta}}}

    # (input hold_out_acc -> expected verdict)
    cases = [
        # HARD-PASS: >= 0.20
        (mk(0.25), "K6_HIER_HARD_PASS"),   # 0.25 >= 0.20 -> PASS
        (mk(0.20), "K6_HIER_HARD_PASS"),   # exactly at boundary -> PASS
        (mk(0.50), "K6_HIER_HARD_PASS"),   # well above -> PASS
        # HARD-FAIL: <= 0.08
        (mk(0.07), "K6_HIER_HARD_FAIL"),   # 0.07 <= 0.08 -> FAIL
        (mk(0.08), "K6_HIER_HARD_FAIL"),   # exactly at boundary -> FAIL
        (mk(0.05), "K6_HIER_HARD_FAIL"),   # below chance -> FAIL
        # MIDDLE: (0.08, 0.20) exclusive
        (mk(0.12), "K6_HIER_MIDDLE_BAND"), # 0.12 in (0.08, 0.20) -> MIDDLE
        (mk(0.15), "K6_HIER_MIDDLE_BAND"), # 0.15 in (0.08, 0.20) -> MIDDLE
        (mk(0.19), "K6_HIER_MIDDLE_BAND"), # 0.19 in (0.08, 0.20) -> MIDDLE
        # INCONCLUSIVE: empty
        ({}, "K6_HIER_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        v, msg = compute_verdict(summary)
        if v != expected:
            raise AssertionError(f"Expected {expected}, got {v}: {msg}. summary={summary}")
    print(f"self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed: int, config: dict):
    N = config["N"]
    train_frac = config["train_frac"]
    n_epochs = config["epochs"]
    device = torch.device("cpu")  # pure vector ops; GPU not needed at this N

    gen = torch.Generator().manual_seed(seed)

    # Atoms for objects, groups, offsets, attributes, values
    obj_atoms = make_bsc_atoms(N_OBJECTS, N, gen).to(device)
    attr_atoms = make_bsc_atoms(N_ATTRS, N, gen).to(device)
    value_atoms = attr_atoms  # answer space = attribute space

    # M1 hierarchical structure: group prototypes + individual offset atoms
    # Objects 0..3 -> group 0, 4..7 -> group 1, 8..11 -> group 2, 12..15 -> group 3
    group_assignment = [i // N_GROUP for i in range(N_OBJECTS)]  # [0,0,0,0,1,1,1,1,...]
    group_protos = torch.stack([
        group_prototype(obj_atoms, list(range(g * N_GROUP, (g + 1) * N_GROUP)))
        for g in range(N_GROUPS)
    ]).to(device)  # [N_GROUPS, N]

    # Offset atoms: each object's role within its group (index 0..N_GROUP-1)
    offset_atoms = make_bsc_atoms(N_GROUP, N, gen).to(device)  # [N_GROUP, N]

    # Level-1 binding: object_slot = group_proto * offset_atom
    # This creates a unique N-dimensional vector for each object via two atoms.
    def object_slot(obj_id: int) -> torch.Tensor:
        g = group_assignment[obj_id]
        o = obj_id % N_GROUP
        return group_protos[g] * offset_atoms[o]  # [N]

    # All (s, r) -> o triples (same Latin-square structure as baseline)
    all_facts = [(s, r, (s + r) % N_ATTRS) for s in range(N_OBJECTS) for r in range(N_ATTRS)]
    perm = torch.randperm(len(all_facts), generator=gen).tolist()
    n_train = int(train_frac * len(all_facts))
    train_facts = [all_facts[i] for i in perm[:n_train]]
    holdout_facts = [all_facts[i] for i in perm[n_train:]]

    # Level-2 storage: B = sum_i value_i bound to (object_slot_i * attr_i)
    # The object_slot uses the hierarchical pre-binding; the attr dimension is unchanged.
    B = torch.zeros(N, dtype=torch.float32, device=device)
    for epoch in range(n_epochs):
        e_perm = torch.randperm(len(train_facts), generator=gen).tolist()
        for i in e_perm:
            s, r, o = train_facts[i]
            slot = object_slot(s)          # level-1 object representation
            key = slot * attr_atoms[r]     # level-2 bind slot * attribute
            val = value_atoms[o]
            B = B + val * key

    def query_acc(facts):
        if not facts:
            return 0.0
        correct = 0
        for s, r, o in facts:
            slot = object_slot(s)
            key = slot * attr_atoms[r]
            pred = B * key   # unbind
            sims = (value_atoms @ pred) / (value_atoms.norm(dim=1) * (pred.norm() + 1e-8) + 1e-8)
            if int(sims.argmax()) == o:
                correct += 1
        return correct / len(facts)

    train_acc = query_acc(train_facts)
    hold_out_acc = query_acc(holdout_facts)
    return {"train_acc": train_acc, "hold_out_acc": hold_out_acc,
            "n_train": len(train_facts), "n_holdout": len(holdout_facts),
            "n_groups": N_GROUPS, "n_group": N_GROUP}


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "train_frac": TRAIN_FRAC_SMOKE if smoke else TRAIN_FRAC_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "n_objects": N_OBJECTS, "n_attrs": N_ATTRS,
              "n_group": N_GROUP, "n_groups": N_GROUPS,
              "pass_holdout_acc": PASS_HOLDOUT_ACC,
              "fail_holdout_acc": FAIL_HOLDOUT_ACC}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: hold_out_acc={r['hold_out_acc']:.3f} "
              f"train_acc={r['train_acc']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    out_name = ("wave14_k6_axis2_hierprebin_v1_smoke" if args.smoke
                else "wave14_k6_axis2_hierprebin_v1")
    out_dir = get_output_dir(out_name)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("hold_out_acc_smoke_hier", r["hold_out_acc"], 0.04)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\n{'SMOKE' if args.smoke else 'DONE'}: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
