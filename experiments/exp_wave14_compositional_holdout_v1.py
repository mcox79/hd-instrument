"""Compositional generalization hold-out probe — K6/U8 KILLER T2.

Per strategy_untested_rows_triage_2026-05-24.md Priority A #1.

Tests substrate ability to READ OUT novel (atom1, atom2) compositions that were
NOT seen at training. We build a synthetic compositional task:
  Vocabulary: 16 "objects" + 16 "attributes" = 32 atoms total
  Training set: 192 of 256 possible (obj, attr) compositions (75% coverage)
  Hold-out: 64 unseen (obj, attr) compositions (25%)

Train: bind obj * attr -> store in W via Hebbian rule with pos-encoding atom
Query: for each (obj, attr_query), read out predicted attr-byte from W @ obj
Compare hold-out accuracy vs train-set accuracy; if hold-out >> chance the
substrate compositionally generalizes.

Pre-reg falsifier statements:

  - HARD-PASS:  hold_out_acc >= 0.50 across 5 seeds (chance = 1/16 ~0.0625).
                Substrate compositionally generalizes; K6/U8 KILLER closed-PASS.
  - HARD-FAIL:  hold_out_acc <= 0.10 (within 2x chance). Substrate does NOT
                compositionally generalize at this readout setting; K6 closed-FAIL.
  - MIDDLE:     intermediate. Some compositional structure but partial.

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only.

Pre-reg: preregs/2026-05-24_wave14_compositional_holdout_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

N_OBJECTS = 16
N_ATTRS = 16
N_FULL = 4096
N_SMOKE = 512
TRAIN_FRAC_FULL = 0.75
TRAIN_FRAC_SMOKE = 0.75
EPOCHS_FULL = 30
EPOCHS_SMOKE = 5
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_HOLDOUT_ACC = 0.50
FAIL_HOLDOUT_ACC = 0.10


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return 2.0 * (raw > 0.5).float() - 1.0


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("COMPOSITIONAL_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    hold_acc = sum(s["hold_out_acc"] for s in seeds) / len(seeds)
    train_acc = sum(s["train_acc"] for s in seeds) / len(seeds)
    if hold_acc >= PASS_HOLDOUT_ACC:
        return ("COMPOSITIONAL_HARD_PASS",
                f"Substrate compositionally generalizes: hold_out_acc={hold_acc:.3f}>={PASS_HOLDOUT_ACC} "
                f"vs chance=1/{N_ATTRS}={1/N_ATTRS:.3f}. train_acc={train_acc:.3f}. K6/U8 closed-PASS.")
    if hold_acc <= FAIL_HOLDOUT_ACC:
        return ("COMPOSITIONAL_HARD_FAIL",
                f"No compositional generalization: hold_out_acc={hold_acc:.3f}<={FAIL_HOLDOUT_ACC} "
                f"(within 2x chance 1/{N_ATTRS}={1/N_ATTRS:.3f}). train_acc={train_acc:.3f}. K6 closed-FAIL.")
    return ("COMPOSITIONAL_MIDDLE_BAND",
            f"Partial compositional structure: hold_out_acc={hold_acc:.3f} in ({FAIL_HOLDOUT_ACC}, {PASS_HOLDOUT_ACC}); "
            f"train_acc={train_acc:.3f}.")


def self_test_verdict():
    def mk(ha, ta):
        return {"per_seed": {"17": {"hold_out_acc": ha, "train_acc": ta}}}
    cases = [
        (mk(0.65, 0.95), "COMPOSITIONAL_HARD_PASS"),
        (mk(0.50, 0.85), "COMPOSITIONAL_HARD_PASS"),
        (mk(0.30, 0.85), "COMPOSITIONAL_MIDDLE_BAND"),
        (mk(0.15, 0.70), "COMPOSITIONAL_MIDDLE_BAND"),
        (mk(0.10, 0.50), "COMPOSITIONAL_HARD_FAIL"),
        (mk(0.06, 0.30), "COMPOSITIONAL_HARD_FAIL"),
        ({}, "COMPOSITIONAL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config):
    N = config["N"]
    train_frac = config["train_frac"]
    n_epochs = config["epochs"]
    gen = torch.Generator().manual_seed(seed)
    device = torch.device("cpu")

    # Use a "subject + relation -> object" 2-argument structure to make the
    # compositional test well-posed. Each FACT is a triple (s, r, o) where s
    # in [0, N_OBJECTS), r in [0, N_ATTRS), and o is a deterministic function
    # of (s, r) — specifically o = (s + r) % N_ATTRS (a Latin-square fact set).
    # This creates 16*16=256 distinct facts; we hold out a structured 25% and
    # test whether the substrate can predict the held-out o given (s, r).
    obj_atoms = make_bsc_atoms(N_OBJECTS, N, gen).to(device)
    attr_atoms = make_bsc_atoms(N_ATTRS, N, gen).to(device)
    # 'value' atoms = the "object" of the fact (16 possible answer vectors).
    value_atoms = attr_atoms  # reuse attr-space as the answer space

    # All (s, r) -> o triples
    all_facts = [(s, r, (s + r) % N_ATTRS) for s in range(N_OBJECTS) for r in range(N_ATTRS)]
    perm = torch.randperm(len(all_facts), generator=gen).tolist()
    n_train = int(train_frac * len(all_facts))
    train_facts = [all_facts[i] for i in perm[:n_train]]
    holdout_facts = [all_facts[i] for i in perm[n_train:]]

    # Build a SINGLE bundle B = sum_i value_i * (s_i XOR r_i) using BSC sign-bind:
    #   bind(s, r) = s_v * r_v  (elementwise, sign vectors)
    # Then query for (s_q, r_q) attempts to recover value via B * bind(s_q, r_q):
    #   pred = B * bind(s_q, r_q)
    # which approximates value_correct + noise from other terms.
    # This is the canonical VSA bundle-bind-recover test.
    B = torch.zeros(N, dtype=torch.float32, device=device)
    for epoch in range(n_epochs):
        e_perm = torch.randperm(len(train_facts), generator=gen).tolist()
        for i in e_perm:
            s, r, o = train_facts[i]
            key = obj_atoms[s] * attr_atoms[r]   # bind by elementwise product (BSC)
            val = value_atoms[o]
            B = B + val * key  # accumulate bundle (value bound to key)

    def accuracy(facts):
        if not facts:
            return 0.0
        correct = 0
        for s, r, o in facts:
            key = obj_atoms[s] * attr_atoms[r]
            with torch.no_grad():
                pred = B * key  # unbind: B * key ~ value_correct + noise
                # Score against all value atoms via cosine
                sims = (value_atoms @ pred) / (value_atoms.norm(dim=1) * (pred.norm() + 1e-8) + 1e-8)
                o_pred = int(sims.argmax())
            if o_pred == o:
                correct += 1
        return correct / len(facts)

    train_acc = accuracy(train_facts)
    hold_out_acc = accuracy(holdout_facts)
    return {"train_acc": train_acc, "hold_out_acc": hold_out_acc,
             "n_train": len(train_facts), "n_holdout": len(holdout_facts)}


def run_experiment(smoke):
    t0 = time.monotonic()
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "train_frac": TRAIN_FRAC_SMOKE if smoke else TRAIN_FRAC_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "n_objects": N_OBJECTS, "n_attrs": N_ATTRS,
              "pass_holdout_acc": PASS_HOLDOUT_ACC,
              "fail_holdout_acc": FAIL_HOLDOUT_ACC}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: hold_out_acc={r['hold_out_acc']:.3f} train_acc={r['train_acc']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(metrics.keys()):
        raise ValueError("metrics missing required")
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
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_compositional_holdout_v1_smoke" if args.smoke
                          else "wave14_compositional_holdout_v1")
    out_dir = _canonical_get_output_dir(name)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("train_acc_smoke", r["train_acc"], 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
