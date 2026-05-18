"""Autonomous sequential runner for the prioritized experiment queue.

Runs each experiment one at a time on whatever GPU is available, saves
metrics to its own data/ directory, continues on failures. Designed to
run unattended for hours.

Priority order (highest payoff/cost first per master plan):
1. Wave 12 qFHRR (quick, low risk)
2. Wave 8 Clifford G(2,0) (top substrate-audit pick)
3. Wave 10A RG-flow Phase A (depth question)
4. Wave 9 MPS-shape (low-rank tensor network)
5. Wave 4.5 gradient W frozen atoms (cheapest backprop test)
6. Wave 4.6 gradient W + learnable offsets
7. Wave 3b induction-head ICL (capability test)

Each gets ~5-45 min; total queue is ~3 hours.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

EXPERIMENTS = [
    ("exp_wave12_qfhrr.py", "Wave 12: qFHRR phase quantization"),
    ("exp_wave8_clifford_g20.py", "Wave 8: Clifford G(2,0) geometric algebra"),
    ("exp_wave10_rgflow_phaseA.py", "Wave 10A: 2-layer Hebbian feedforward"),
    ("exp_wave9_mps_prototype.py", "Wave 9: MPS-shape substrate"),
    ("exp_wave45_gradient_w_frozen_atoms.py", "Wave 4.5: gradient W frozen atoms"),
    ("exp_wave46_learnable_offsets.py", "Wave 4.6: gradient W + learnable offsets"),
    ("exp_induction_head.py", "Wave 3b: induction-head ICL"),
]


def main():
    repo = Path(__file__).resolve().parent.parent
    python_exe = sys.executable
    print(f"Python: {python_exe}", flush=True)
    print(f"Repo:   {repo}", flush=True)
    print(f"Queue:  {len(EXPERIMENTS)} experiments", flush=True)

    t_start = time.perf_counter()
    successes = []
    failures = []
    for script_name, description in EXPERIMENTS:
        script_path = repo / "experiments" / script_name
        if not script_path.exists():
            print(f"\n  [MISSING] {script_name} not found", flush=True)
            failures.append((script_name, "missing"))
            continue
        print(f"\n{'='*70}", flush=True)
        print(f">>> {description}", flush=True)
        print(f"    {script_name}", flush=True)
        print(f"{'='*70}", flush=True)
        t0 = time.perf_counter()
        result = subprocess.run(
            [python_exe, "-u", str(script_path)],
            cwd=str(repo),
            capture_output=False,
        )
        dt = time.perf_counter() - t0
        if result.returncode == 0:
            successes.append((script_name, dt))
            print(f"\n  [DONE] {script_name} in {dt:.1f}s", flush=True)
        else:
            failures.append((script_name, f"exit {result.returncode}"))
            print(f"\n  [FAIL] {script_name} exit={result.returncode} after {dt:.1f}s", flush=True)
        print(f"  Elapsed total: {(time.perf_counter()-t_start)/60:.1f} min", flush=True)

    print(f"\n{'='*70}", flush=True)
    print(f"AUTONOMOUS QUEUE SUMMARY", flush=True)
    print(f"  Successes: {len(successes)}/{len(EXPERIMENTS)}", flush=True)
    print(f"  Failures:  {len(failures)}/{len(EXPERIMENTS)}", flush=True)
    print(f"  Total wall: {(time.perf_counter()-t_start)/60:.1f} min", flush=True)
    if failures:
        print(f"  Failed:", flush=True)
        for s, reason in failures:
            print(f"    - {s}: {reason}", flush=True)


if __name__ == "__main__":
    main()
