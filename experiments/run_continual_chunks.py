"""Run Wave 3a continual learning in 12 independent chunks.

Each (substrate, condition) is a separate subprocess. If one crashes, the
others continue. Aggregates all chunk JSONs at the end.

This is the resilient version that survives mid-run CUDA failures.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

SUBSTRATES = ["FHRR", "BSC", "SBC"]
CONDITIONS = ["A_only", "B_only", "joint_AB", "sequential_AB"]


def main():
    repo = Path(__file__).resolve().parent.parent
    script = repo / "experiments" / "exp_continual_learning.py"
    out_dir = repo / "data" / "exp_continual_learning"
    out_dir.mkdir(parents=True, exist_ok=True)

    python_exe = sys.executable
    print(f"Python: {python_exe}", flush=True)
    print(f"Script: {script}", flush=True)
    print(f"Output: {out_dir}", flush=True)

    t_start = time.perf_counter()
    failures = []
    successes = []
    for substrate in SUBSTRATES:
        for condition in CONDITIONS:
            chunk_file = out_dir / f"chunk_{substrate}_{condition}.json"
            if chunk_file.exists():
                print(f"  [SKIP] {substrate}/{condition} (already exists)", flush=True)
                successes.append((substrate, condition))
                continue
            print(f"\n>>> {substrate} / {condition} <<<", flush=True)
            t0 = time.perf_counter()
            result = subprocess.run(
                [python_exe, "-u", str(script), "--substrate", substrate, "--condition", condition],
                cwd=str(repo),
                capture_output=False,
            )
            dt = time.perf_counter() - t0
            # Chunk file existence is the real success signal; exit code can be nonzero
            # for cosmetic reasons (e.g., partial-run summary failure) even when the
            # chunk JSON was successfully written.
            if chunk_file.exists():
                successes.append((substrate, condition))
                status = "DONE" if result.returncode == 0 else "DONE (exit nonzero, chunk saved)"
                print(f"  [{status}] {substrate}/{condition} in {dt:.1f}s", flush=True)
            else:
                failures.append((substrate, condition, result.returncode))
                print(f"  [FAIL] {substrate}/{condition} exit={result.returncode} after {dt:.1f}s (no chunk file)", flush=True)

    elapsed = time.perf_counter() - t_start
    print(f"\n========= CHUNK RUNNER SUMMARY =========", flush=True)
    print(f"  Successes: {len(successes)}/12", flush=True)
    print(f"  Failures:  {len(failures)}/12", flush=True)
    if failures:
        print(f"  Failed chunks: {failures}", flush=True)
    print(f"  Total wall: {elapsed:.1f}s", flush=True)

    # Aggregate all chunk JSONs into one
    aggregate = {"substrates": SUBSTRATES, "conditions": CONDITIONS, "chunks": []}
    for substrate in SUBSTRATES:
        for condition in CONDITIONS:
            f = out_dir / f"chunk_{substrate}_{condition}.json"
            if f.exists():
                aggregate["chunks"].append(json.loads(f.read_text()))
    agg_file = out_dir / "aggregated.json"
    agg_file.write_text(json.dumps(aggregate, indent=2, default=str))
    print(f"  Aggregated -> {agg_file}", flush=True)


if __name__ == "__main__":
    main()
