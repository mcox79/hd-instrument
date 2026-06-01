"""Edit-impact DAG Reverse-Traversal smoke (A4).

SCIENTIFIC QUESTION (A4):
  Does DAG reverse-traversal correctly predict which stored facts are
  affected by editing a given atom? Precision >= 0.95 AND recall = 1.00.

PRE-REGISTERED BANDS:
  HARD-PASS: precision >= 0.95 AND recall = 1.00 in >= 3/5 seeds.
  HARD-FAIL: recall < 0.95 (misses affected facts) in majority of seeds.
  MIDDLE: recall=1.0 but precision < 0.95 (over-prediction), or
    precision>=0.95 but recall < 1.0 in minority.

DESIGN:
  Synthetic fact graph: M=50 facts, each fact uses ~K=3 atoms from
  atom registry of size A=100. Edit atom a_x; identify all facts
  that reference a_x via DAG edges. Compare to ground-truth affected set.
  Seeds: [7,17,23,31,41].

PROT-018: no _n suffix; graph-only, N not load-bearing.
PROT-021: seed-tagged checkpoint keys.

Anchor: edit_impact_dag_reverse_traversal_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_edit_impact_dag_reverse_traversal.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_dag", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_ATOMS  = 100   # atom registry size
M_FACTS  = 50    # facts in graph
K_ATOMS  = 3     # atoms per fact
N_EDITS  = 20    # atoms to test as edit targets (across seeds)

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_PREC  = 0.95
HP_REC   = 1.00
HF_REC   = 0.95  # recall < 0.95 = HF


class FactDAG:
    """Atom registry + fact membership graph.

    Edges: atom_id -> {fact_ids that reference it}.
    Reverse traversal: given atom_id, return all facts referencing it.
    """

    def __init__(self) -> None:
        self.fact_atoms: Dict[int, Set[int]] = {}   # fact_id -> set of atom_ids
        self.atom_facts: Dict[int, Set[int]] = {}   # atom_id -> set of fact_ids

    def add_fact(self, fact_id: int, atom_ids: Set[int]) -> None:
        self.fact_atoms[fact_id] = set(atom_ids)
        for a in atom_ids:
            if a not in self.atom_facts:
                self.atom_facts[a] = set()
            self.atom_facts[a].add(fact_id)

    def affected_by_edit(self, atom_id: int) -> Set[int]:
        """Return set of fact_ids affected by editing atom_id."""
        return set(self.atom_facts.get(atom_id, set()))


def measure_seed(n_atoms: int, m_facts: int, k_atoms: int,
                 n_edits: int, seed: int) -> Dict:
    """Build DAG, run reverse traversal, measure precision/recall."""
    rng = np.random.default_rng(seed)

    dag = FactDAG()
    fact_atom_map: Dict[int, Set[int]] = {}
    for fact_id in range(m_facts):
        atoms = set(int(a) for a in rng.choice(n_atoms, size=k_atoms, replace=False))
        fact_atom_map[fact_id] = atoms
        dag.add_fact(fact_id, atoms)

    # Test N_EDITS random atom targets
    edit_atoms = rng.choice(n_atoms, size=min(n_edits, n_atoms), replace=False)
    precisions: List[float] = []
    recalls: List[float] = []

    for atom_id in edit_atoms:
        # Ground truth: facts that reference atom_id
        gt = {fid for fid, atoms in fact_atom_map.items() if atom_id in atoms}
        # DAG prediction: reverse traversal
        pred = dag.affected_by_edit(int(atom_id))

        tp = len(gt & pred)
        fp = len(pred - gt)
        fn = len(gt - pred)

        # Skip if no ground-truth affected facts (nothing to detect)
        if len(gt) == 0:
            continue

        prec = tp / max(tp + fp, 1)
        rec  = tp / max(tp + fn, 1)
        precisions.append(prec)
        recalls.append(rec)

    if not recalls:
        return {"seed": seed, "ok": False, "error": "no atoms with affected facts"}

    mean_prec = float(np.mean(precisions))
    mean_rec  = float(np.mean(recalls))
    n_full_rec = sum(1 for r in recalls if r >= HP_REC - 1e-9)
    n_pass_hp  = sum(1 for p, r in zip(precisions, recalls)
                     if p >= HP_PREC and r >= HP_REC - 1e-9)

    return {
        "seed": seed,
        "n_atoms": n_atoms,
        "m_facts": m_facts,
        "k_atoms": k_atoms,
        "n_tested_atoms": len(recalls),
        "mean_precision": float(mean_prec),
        "mean_recall": float(mean_rec),
        "n_full_recall": int(n_full_rec),
        "n_pass_hp": int(n_pass_hp),
        "frac_pass_hp": float(n_pass_hp / len(recalls)),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("DAG_TRAVERSAL_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("DAG_TRAVERSAL_INCONCLUSIVE", "all cells failed")

    # HP: mean_recall == 1.0 and mean_precision >= 0.95 in >= 3/5 seeds
    n_hp = sum(1 for c in ok
               if c["mean_recall"] >= HP_REC - 1e-6 and
               c["mean_precision"] >= HP_PREC)
    n_hf = sum(1 for c in ok if c["mean_recall"] < HF_REC)
    majority = len(ok) // 2 + 1

    mean_prec = sum(c["mean_precision"] for c in ok) / len(ok)
    mean_rec  = sum(c["mean_recall"] for c in ok) / len(ok)
    detail = (
        f"mean_prec={mean_prec:.4f} mean_rec={mean_rec:.4f} "
        f"n_hp={n_hp}/{len(ok)} n_hf={n_hf}/{len(ok)}"
    )

    if n_hf >= majority:
        return ("DAG_TRAVERSAL_HARD_FAIL",
                f"RECALL_TOO_LOW: recall<{HF_REC} in {n_hf}/{len(ok)} seeds. "
                + detail)
    if n_hp >= majority:
        return ("DAG_TRAVERSAL_HARD_PASS",
                f"PRECISION_AND_RECALL_VALIDATED: n_hp={n_hp}/{len(ok)}. "
                + detail)
    return ("DAG_TRAVERSAL_MIDDLE_BAND",
            f"PARTIAL: " + detail)


def get_output_dir(default_name: str = "edit_impact_dag_reverse_traversal_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # Formula self-test 1: FactDAG basic operation
    dag = FactDAG()
    dag.add_fact(0, {1, 2, 3})
    dag.add_fact(1, {2, 4})
    affected = dag.affected_by_edit(2)
    assert affected == {0, 1}, f"affected_by_edit(2) should be {{0,1}}, got {affected}"
    not_affected = dag.affected_by_edit(99)
    assert not_affected == set(), f"atom 99 should affect no facts: {not_affected}"
    print(f"[selftest] formula-1 FactDAG.affected_by_edit PASS", flush=True)

    # Formula self-test 2: precision/recall computation
    gt = {0, 1, 2}
    pred = {0, 1, 3}  # tp=2, fp=1, fn=1
    tp = len(gt & pred); fp = len(pred - gt); fn = len(gt - pred)
    prec = tp / max(tp + fp, 1)
    rec  = tp / max(tp + fn, 1)
    assert abs(prec - 2/3) < 1e-9, f"prec={prec} expected 2/3"
    assert abs(rec  - 2/3) < 1e-9, f"rec={rec} expected 2/3"
    print(f"[selftest] formula-2 prec/rec computation PASS", flush=True)

    # Formula self-test 3: live smoke at small scale
    out = measure_seed(20, 10, 2, 10, 42)
    assert out["ok"], f"measure_seed failed: {out.get('error')}"
    assert 0.0 <= out["mean_precision"] <= 1.0, f"precision out of range"
    assert 0.0 <= out["mean_recall"] <= 1.0, f"recall out of range"
    assert out["n_tested_atoms"] >= 1, f"n_tested_atoms=0 (filter passed 0 items)"
    print(f"[selftest] formula-3 live smoke prec={out['mean_precision']:.4f} "
          f"rec={out['mean_recall']:.4f} n_atoms={out['n_tested_atoms']} PASS",
          flush=True)

    # Formula self-test 4: deterministic graph -> perfect precision AND recall
    dag2 = FactDAG()
    dag2.add_fact(0, {0})
    dag2.add_fact(1, {0, 1})
    dag2.add_fact(2, {2})
    affected_0 = dag2.affected_by_edit(0)
    assert affected_0 == {0, 1}, f"affected_0={affected_0}"
    print(f"[selftest] formula-4 deterministic graph perfect recall PASS", flush=True)

    # Formula self-test 5: verdict gates
    fake_hp = [{"ok": True, "mean_precision": 0.97, "mean_recall": 1.0,
                "n_tested_atoms": 20, "n_full_recall": 20, "n_pass_hp": 20,
                "frac_pass_hp": 1.0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "mean_precision": 0.99, "mean_recall": 0.90,
                "n_tested_atoms": 20, "n_full_recall": 0, "n_pass_hp": 0,
                "frac_pass_hp": 0.0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-5 verdict gates PASS", flush=True)

    print("[selftest] edit_impact_dag_reverse_traversal_v1 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke  = args.smoke
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_edits_cfg = N_EDITS // 2 if smoke else N_EDITS

    out_dir = get_output_dir()
    run_config = {"run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] edit_impact_dag_reverse_traversal_v1 smoke={smoke} "
          f"n_atoms={N_ATOMS} m_facts={M_FACTS} k_atoms={K_ATOMS} "
          f"seeds={seeds} done={len(done)}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded", flush=True)
                continue
        try:
            cell = measure_seed(N_ATOMS, M_FACTS, K_ATOMS, n_edits_cfg, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"prec={cell.get('mean_precision','n/a'):.4f} "
                  f"rec={cell.get('mean_recall','n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "edit_impact_dag_reverse_traversal_v1",
        "smoke": smoke, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
