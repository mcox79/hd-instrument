"""Run every `verification/test_*.py` through pytest in its OWN PROCESS, writing results incrementally.

WHY PER-FILE. `pytest verification/` cannot run at all: several files execute work at MODULE level
(one raises SystemExit -> INTERNALERROR aborting the session; two redirect the same module global to
different temp dirs and collide). They were written as STANDALONE witnesses. One process per file is
the only way to run them together today.

WHY NOT `python <file>` -- THE MISTAKE THIS REPLACES. 35 of the 64 files define `test_*` functions but
have NO `if __name__ == "__main__":` runner. Executed directly they import, define, and exit 0 HAVING
RUN NOTHING -- and a sweep counting exit code 0 scores them as passes. That is how "64/64 pass" was
reported twice for a sweep that actually exercised 29 files. A metric where "ran nothing" and "all
passed" both return 0 cannot fail safely.

WHY INCREMENTAL. The first attempt printed only a final summary, exceeded its timeout, and left a
ZERO-BYTE output file -- 10 minutes of work with nothing to show. Results are now appended and
flushed per file, so a kill at any point keeps everything already measured.

    python tools/per_file_pytest_sweep.py [--out PATH] [--timeout S] [--only SUBSTR]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIF = os.path.join(REPO, "verification")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "scratch", "per_file_pytest_sweep.jsonl"))
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    exe = os.path.join(REPO, ".venv", "Scripts", "python.exe")
    if not os.path.exists(exe):
        exe = sys.executable
    files = sorted(f for f in os.listdir(VERIF)
                   if f.startswith("test_") and f.endswith(".py") and args.only in f)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    done = set()
    if os.path.exists(args.out):                       # RESUMABLE: skip what is already measured
        for line in open(args.out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["file"])
            except Exception:
                pass
    print(f"{len(files)} files, {len(done)} already measured, timeout {args.timeout}s each",
          flush=True)

    fh = open(args.out, "a", encoding="utf-8", newline="\n")
    tp = tf = 0
    for i, f in enumerate(files, 1):
        if f in done:
            continue
        t0 = time.time()
        rec = {"file": f}
        try:
            r = subprocess.run([exe, "-m", "pytest", os.path.join("verification", f),
                                "-q", "--no-header", "-p", "no:cacheprovider"],
                               capture_output=True, text=True, timeout=args.timeout, cwd=REPO)
            out = r.stdout + r.stderr
            rec["rc"] = r.returncode
            rec["passed"] = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
            rec["failed"] = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
            rec["errors"] = int(m.group(1)) if (m := re.search(r"(\d+) error", out)) else 0
            rec["collected_none"] = ("no tests ran" in out)
            rec["tail"] = (out.strip().splitlines() or ["?"])[-1][:160]
        except subprocess.TimeoutExpired:
            rec.update(rc="TIMEOUT", passed=0, failed=0, errors=0, collected_none=False,
                       tail=f"exceeded {args.timeout}s")
        rec["elapsed_s"] = round(time.time() - t0, 1)
        tp += rec["passed"]
        tf += rec["failed"]
        fh.write(json.dumps(rec) + "\n")
        fh.flush()                                     # survive a kill
        os.fsync(fh.fileno())
        print(f"[{i}/{len(files)}] {f:52} rc={rec['rc']} "
              f"p={rec['passed']} f={rec['failed']} {rec['elapsed_s']}s", flush=True)
    fh.close()
    print(f"\nrunning total this session: {tp} passed, {tf} failed -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
