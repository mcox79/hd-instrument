"""Generic cell-by-cell stdout parser that emits progress.json on the remote.

Runs ON THE LAMBDA INSTANCE (not locally). The generic launch_experiment
script SSHes this in instead of running the target experiment directly. Job:

  1. spawn the target experiment script as a subprocess with line-buffered
     stdio
  2. tee every line to our own stdout (so the launcher's existing
     remote-log tee still works unchanged)
  3. count lines matching the user-supplied --cell-regex
  4. emit progress.json via ProgressEmitter after each cell

Each experiment supplies its own cell-completion regex via CLI:
  --cell-regex '^\\s+seed=\\d+\\s+(?:ok=|acc=|FAILED:)'

A sensible default matches the common substrate-experiment cell shape:
  '^\\s+(?:M=\\d+\\s+d=\\d+\\s+)?seed=\\d+\\s+(?:ok=|acc=|FAILED:)'

Total cells must be supplied via --total-cells; experiments that compute
it dynamically can pass any int (ETA narrows as more cells complete).

The local-side launcher SCPs progress.json back every 30s and prints it.

Exits with the target's exit code (or signal mapped to 128+sig).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from hdlab_service.progress_emitter import ProgressEmitter  # noqa: E402


_DEFAULT_CELL_REGEX = (
    r"^\s+(?:M=\d+\s+d=\d+\s+)?seed=\d+\s+(?:ok=|acc=|FAILED:)"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generic Lambda experiment progress wrapper")
    parser.add_argument("--anchor", required=True,
                        help="Anchor name; progress.json written to "
                             "data/exp_<anchor>/progress.json")
    parser.add_argument("--script", required=True,
                        help="Path to experiment script (relative to repo "
                             "root or absolute)")
    parser.add_argument("--cell-regex", default=_DEFAULT_CELL_REGEX,
                        help="Regex matching one cell-completion line in the "
                             "target script's stdout. Default fits substrate "
                             "experiments that print 'seed=N ok=...' / "
                             "'M=N d=K seed=S acc=...' / 'seed=N FAILED:'")
    parser.add_argument("--total-cells", type=int, required=True,
                        help="Expected number of cell-completion lines "
                             "(used for ETA + percent-done display)")
    parser.add_argument("--initial-phase", default="starting",
                        help="Phase string before the first cell completes")
    parser.add_argument("--script-args", default="",
                        help="Single string of args passed through to the "
                             "target script (split via shlex). e.g. "
                             "--script-args '--dataset-dir data/foo --lr 1e-4'")
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.is_absolute():
        script_path = _REPO_ROOT / script_path
    if not script_path.is_file():
        print(f"[generic_progress_wrapper] script not found: {script_path}",
              file=sys.stderr, flush=True)
        return 2

    progress_path = _REPO_ROOT / "data" / f"exp_{args.anchor}" / "progress.json"
    try:
        cell_re = re.compile(args.cell_regex)
    except re.error as exc:
        print(f"[generic_progress_wrapper] invalid regex: {exc}",
              file=sys.stderr, flush=True)
        return 2

    emitter = ProgressEmitter(
        out_path=progress_path,
        total_cells=args.total_cells,
        phase=args.initial_phase,
    )
    print(f"[generic_progress_wrapper] target={script_path.name} "
          f"total_cells={args.total_cells} progress={progress_path}",
          flush=True)

    import shlex
    script_extra_args = shlex.split(args.script_args) if args.script_args else []
    if script_extra_args:
        print(f"[generic_progress_wrapper] script args: {script_extra_args}",
              flush=True)
    proc = subprocess.Popen(
        [sys.executable, "-u", str(script_path), *script_extra_args],
        cwd=str(_REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    cell_count = 0
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            if cell_re.match(line):
                cell_count += 1
                phase = line.strip()
                if len(phase) > 80:
                    phase = phase[:77] + "..."
                try:
                    emitter.update(cell=cell_count, phase=phase)
                except Exception as exc:
                    print(f"[generic_progress_wrapper] emitter.update "
                          f"failed: {exc}", flush=True)
    finally:
        rc = proc.wait()
        try:
            emitter.done(phase=f"exit={rc}")
        except Exception:
            pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
