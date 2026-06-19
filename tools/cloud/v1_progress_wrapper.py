"""V1 cell-by-cell stdout parser that emits progress.json on the remote.

Runs ON THE LAMBDA INSTANCE (not locally). The launch_v1_canary script
SSHes this in instead of running V1 directly. Job:

  1. spawn V1 (`exp_modern_hopfield_pipeline_validation_v1_n2048_n4096.py`)
     as a subprocess with line-buffered stdio
  2. tee every line to our own stdout (so launch_v1_canary's existing
     remote-log tee still works unchanged)
  3. count lines matching the V1 cell-completion pattern
     `N=NNNN M=MMM s=SS success=...`
  4. emit progress.json via ProgressEmitter after each cell

V1 has 39 cells (21 for N=2048 + 18 for N=4096; per_N derived from the
verdict_msg of a known good run). Hard-coded here because V1's script
doesn't expose that count up front.

The local-side launch_v1_canary script SCPs progress.json back every 30s
and prints it.

This wrapper is V1-specific because V1's stdout format is well-defined.
A more generic wrapper (one for any experiment that uses ProgressEmitter
directly) is the right shape long-term; this serves as the worked
example showing the dispatch pattern.

Exits with V1's exit code (or its signal mapped to 128+sig).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

# Make hdlab_service importable when invoked from the repo root on the remote.
_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from hdlab_service.progress_emitter import ProgressEmitter  # noqa: E402


_V1_ANCHOR = "modern_hopfield_pipeline_validation_v1_n2048_n4096"
_V1_SCRIPT = f"experiments/exp_{_V1_ANCHOR}.py"
_PROGRESS_PATH = f"data/exp_{_V1_ANCHOR}/progress.json"

# Total cells per the V1 verdict_msg from a known good run:
# per_N={2048: 21, 4096: 18} -> 39 total.
_V1_TOTAL_CELLS = 39

# V1 prints one line per cell completion matching:
#   N=2048 M=512 s=7 success=True recall=1.0 kf1=0.0 ... cert=True (2.0s)
_CELL_RE = re.compile(
    r"^\s*N=(?P<n>\d+)\s+M=(?P<m>\d+)\s+s=(?P<s>\d+)\s+success=",
)


def main() -> int:
    py = sys.executable
    script = str(_REPO_ROOT / _V1_SCRIPT)
    cwd = str(_REPO_ROOT)
    progress_path = _REPO_ROOT / _PROGRESS_PATH

    emitter = ProgressEmitter(
        out_path=progress_path,
        total_cells=_V1_TOTAL_CELLS,
        phase="V1 starting",
    )

    # Spawn V1 unbuffered + line-buffered so cell lines reach us promptly.
    proc = subprocess.Popen(
        [py, "-u", script],
        cwd=cwd,
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
            m = _CELL_RE.match(line)
            if m:
                cell_count += 1
                phase = f"N={m.group('n')} M={m.group('m')} s={m.group('s')}"
                try:
                    emitter.update(cell=cell_count, phase=phase)
                except Exception as exc:
                    # Progress writes must never kill the experiment.
                    print(f"[progress_wrapper] emitter.update failed: {exc}",
                          flush=True)
    finally:
        rc = proc.wait()
        try:
            emitter.done(phase=f"V1 exit={rc}")
        except Exception:
            pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
