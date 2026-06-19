"""Chunked runner for Wave 3a.5 forgetting mitigations.

3 substrates × 4 mitigations = 12 chunks; each independent subprocess.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

SUBSTRATES = ["FHRR", "BSC", "SBC"]
MITIGATIONS = ["baseline", "decay_off_P2", "W_frozen_P2", "dual_pool"]


def main():
    repo = Path(__file__).resolve().parent.parent
    script = repo / "experiments" / "exp_continual_mitigations.py"
    out_dir = repo / "data" / "exp_continual_mitigations"
    out_dir.mkdir(parents=True, exist_ok=True)

    python_exe = sys.executable
    print(f"Python: {python_exe}", flush=True)
    print(f"Script: {script}", flush=True)
    print(f"Output: {out_dir}", flush=True)

    t_start = time.perf_counter()
    failures = []
    successes = []
    for substrate in SUBSTRATES:
        for mitigation in MITIGATIONS:
            chunk_file = out_dir / f"chunk_{substrate}_{mitigation}.json"
            if chunk_file.exists():
                print(f"  [SKIP] {substrate}/{mitigation} (already exists)", flush=True)
                successes.append((substrate, mitigation))
                continue
            print(f"\n>>> {substrate} / {mitigation} <<<", flush=True)
            t0 = time.perf_counter()
            result = subprocess.run(
                [python_exe, "-u", str(script), "--substrate", substrate, "--mitigation", mitigation],
                cwd=str(repo),
                capture_output=False,
            )
            dt = time.perf_counter() - t0
            if chunk_file.exists():
                successes.append((substrate, mitigation))
                status = "DONE" if result.returncode == 0 else "DONE (exit nonzero, chunk saved)"
                print(f"  [{status}] {substrate}/{mitigation} in {dt:.1f}s", flush=True)
            else:
                failures.append((substrate, mitigation, result.returncode))
                print(f"  [FAIL] {substrate}/{mitigation} exit={result.returncode} after {dt:.1f}s", flush=True)

    elapsed = time.perf_counter() - t_start
    print(f"\n========= MITIGATION CHUNK RUNNER SUMMARY =========", flush=True)
    print(f"  Successes: {len(successes)}/12", flush=True)
    print(f"  Failures:  {len(failures)}/12", flush=True)
    if failures:
        print(f"  Failed chunks: {failures}", flush=True)
    print(f"  Total wall: {elapsed:.1f}s", flush=True)

    aggregate = {"substrates": SUBSTRATES, "mitigations": MITIGATIONS, "chunks": []}
    for substrate in SUBSTRATES:
        for mitigation in MITIGATIONS:
            f = out_dir / f"chunk_{substrate}_{mitigation}.json"
            if f.exists():
                aggregate["chunks"].append(json.loads(f.read_text()))
    agg_file = out_dir / "aggregated.json"
    agg_file.write_text(json.dumps(aggregate, indent=2, default=str))
    print(f"  Aggregated -> {agg_file}", flush=True)


if __name__ == "__main__":
    main()
