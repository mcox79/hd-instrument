#!/usr/bin/env python
"""Re-run a landed cell so that it CAN come out different, and say plainly whether it did.

WHY THIS EXISTS. Re-running a finished cell here does not redo it. `completed_units()` finds every
unit already in `units.jsonl`, the cell skips all of them, and the SAME verdict comes back in ~0.0s
having computed nothing. Measured: 403 of 7,875 landed cells replay. So "I re-ran it and it matched"
is currently not evidence of anything -- it is the harness handing back a stored answer.

SH-7 (`experiments/_seed_checkpoint.get_output_dir`) added the switch: `HDI_FRESH_RUN=<tag>` points
the cell at an EMPTY sibling directory, so it recomputes every unit, and the landed directory is
never opened for writing. This is the driver for it, so an operator gets a falsifiable re-run in one
command instead of needing to know an environment variable exists.

    python tools/reproduce.py exp_cortical_read_consolidated_v1 --check   # safe, no run
    python tools/reproduce.py exp_cortical_read_consolidated_v1
    python tools/reproduce.py exp_foo --tag nightly --timeout 7200

THE REFUSAL IS THE POINT, NOT A LIMITATION. SH-7 only covers cells that route their output through
`get_output_dir`. A cell holding a bare module-level `OUTPUT_DIR` IGNORES the env var: it would run
and write straight into the LANDED directory, overwriting `metrics.json` with a new timestamp while
this tool cheerfully reported a "reproduction". **That is worse than the bug being fixed**, so a
cell that cannot be redirected is REFUSED, loudly, with the one-line migration that fixes it.
`--force` exists and prints what it is risking.

COVERAGE, AND THE TWO NUMBERS ARE ON DIFFERENT POPULATIONS -- DO NOT CROSS THEM:
  * Of the 423 cells carrying a `units.jsonl` -- the REPLAY-PRONE population, the one SH-7 exists
    for -- a STRING match says 87 (~21%) and a strict IMPORT match says **43 (~10%)**. The string
    number is PROVEN to overcount: one cell containing `get_output_dir` DEFINES ITS OWN and the
    redirect was inert when run. **Treat 10-21% as the range and never quote the 87 alone.** The
    deciding test is not a grep at all -- run the cell and check the fresh sibling was created,
    which this tool now does.
  * Of ALL 5,897 files in `experiments/`, **69% route through it.** Most of those never produced a
    `units.jsonl` and so are not in the replay population at all.
  **So ~21% is a property of the CHECKPOINTING archive, not of the codebase**, and quoting the 69%
  as this tool's coverage would overstate it by more than 3x.

  MEASURED PROPERLY 2026-08-22, AND COVERAGE SHRINKS: the share of NEW primary cells routing
  through `get_output_dir` fell 90.8% (June) -> 47.3% (July) -> 27.2% (August), n=707-2,869 per
  month. Not a file-generation artifact -- variant-suffix files are n<=2 per month. **So this
  tool reaches fewer cells over time, not more**, and clearing the 275-cell backlog while new bare
  cells keep arriving does not close the gap. *An underpowered 25-per-class sample the night before
  called this direction correctly; that is a reason to run the powered version, not to trust the
  sample.*

  AND THE ONE-HOOK SHORTCUT IS REFUTED, RECORDED SO IT IS NOT RE-PROPOSED: redirecting inside
  `tools/exp_checkpoint.write_metrics` instead of migrating cells would reach **85 of 1,584 bare
  cells (5%)** -- 849 write `metrics.json` with a raw `json.dump`. The units side IS shared (208
  call `record_unit`), which is exactly what makes a units-only redirect tempting and wrong: it
  would force a recompute while leaving the landed `metrics.json` to be overwritten.
  `notes/THE_REPRODUCIBILITY_HOLE_IS_GROWING_AND_THE_ONE_HOOK_SHORTCUT_IS_REFUTED_2026-08-22.md`

WHAT IT REPORTS, and the three outcomes are genuinely different:
  REPRODUCED  -- fresh recompute, verdict matches the landed one. The only one that is evidence.
  DIVERGED    -- fresh recompute, verdict differs. The landed record is not reproducible AS RECORDED.
  REPLAYED    -- no work was done. Says NOTHING about the result, and is reported as such.

It never prints "PASS".
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from tools import reproduction_check as rc  # noqa: E402

DATA = os.path.join(REPO, "data")
EXPERIMENTS = os.path.join(REPO, "experiments")
PYTHON = os.path.join(REPO, ".venv", "Scripts", "python.exe")


def _cell_source(cell: str) -> str | None:
    """The experiment source for a cell name, trying the usual spellings. None if not located."""
    stem = cell[4:] if cell.startswith("exp_") else cell
    for cand in (cell, stem, "exp_" + stem):
        p = os.path.join(EXPERIMENTS, cand + ".py")
        if os.path.isfile(p):
            return p
    return None


def _landed_dir(cell: str) -> str | None:
    """The landed data directory, trying BOTH spellings. None if it does not exist.

    NOT `data/exp_<cell>` UNCONDITIONALLY, which is what this did until 2026-08-23. Asked to check
    `solverB_cortical_scored_path_v1`, it built `data/exp_solverB_...`, found nothing, printed
    "(MISSING)" as one line among several -- and then gave confident advice about redirectability
    based on a directory that does not exist. **19 of 423 landed directories do not carry the `exp_`
    prefix**, mostly solver-authored and `writerule_*` cells, so the tool was structurally blind to
    them while sounding certain.

    Found by using the tool on a real solver result rather than on the cells it was written against.
    """
    for cand in (cell, "exp_" + cell) if not cell.startswith("exp_") else (cell, cell[4:]):
        p = os.path.join(DATA, cand)
        if os.path.isdir(p):
            return p
    return None


def routes_through_get_output_dir(src: str) -> bool:
    """Does this cell's output path come from `get_output_dir` (i.e. is SH-7 able to redirect it)?

    A SOURCE GREP, AND ITS LIMITS ARE STATED RATHER THAN HIDDEN: an aliased import or an unusual
    path construction could be missed in either direction. It is used only to decide whether to
    REFUSE, and the refusal is the safe side -- a false refusal costs a message, a false acceptance
    overwrites a landed record.
    """
    try:
        text = open(src, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    return "get_output_dir" in text


def _verdict_of(output_dir: str):
    """The cell's own verdict string from metrics.json, or None. Never raises."""
    p = os.path.join(output_dir, "metrics.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for key in ("verdict", "final_verdict", "verdict_msg", "status"):
        v = d.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _dir_fingerprint(output_dir: str):
    """(size, mtime) per file, so an unexpected write to the LANDED dir is detectable afterwards."""
    out = {}
    for name in ("units.jsonl", "metrics.json"):
        p = os.path.join(output_dir, name)
        try:
            st = os.stat(p)
            out[name] = (st.st_size, st.st_mtime_ns)
        except OSError:
            out[name] = None
    return out


def check(cell: str) -> int:
    """Report whether this cell can be reproduced at all, WITHOUT running anything."""
    src = _cell_source(cell)
    landed = _landed_dir(cell)
    if landed is None:
        print("cell            :", cell)
        print("REFUSING: no landed data directory found under data/ for that name.")
        print("  tried: data/%s and data/exp_%s" % (cell, cell))
        print("  A missing landed directory means there is nothing to reproduce AGAINST, so any")
        print("  answer about redirectability would be advice about a directory that does not")
        print("  exist. Check the name with: ls data/ | grep <fragment>")
        return 2
    units = rc.unit_count(landed)

    print("cell            :", cell)
    print("source          :", os.path.relpath(src, REPO).replace("\\", "/") if src else "NOT LOCATED")
    print("landed dir      :", os.path.relpath(landed, REPO).replace("\\", "/"),
          "(exists)" if os.path.isdir(landed) else "(MISSING)")
    print("recorded units  :", units)
    print("landed verdict  :", _verdict_of(landed))

    if units > 0:
        print("re-running AS-IS:", rc.REPLAYED, "-- it would skip every unit and prove nothing")
    else:
        print("re-running AS-IS: no recorded units, so a plain re-run would already recompute")

    if src is None:
        print("REPRODUCIBLE    : UNKNOWN -- source not located, so the redirect cannot be checked")
        return 2
    if routes_through_get_output_dir(src):
        print("REPRODUCIBLE    : YES -- routes through get_output_dir, SH-7 can redirect it")
        return 0
    print("REPRODUCIBLE    : NO -- bare OUTPUT_DIR; setting HDI_FRESH_RUN would do NOTHING and the")
    print("                  run would write into the LANDED directory. Migrate it first:")
    print("                    from experiments.fresh_recompute import fresh_run_output_dir")
    print("                    OUTPUT_DIR = fresh_run_output_dir(<the existing expression>)")
    return 1


def reproduce(cell: str, tag: str, timeout: int, force: bool, extra: list) -> int:
    src = _cell_source(cell)
    if src is None:
        print(f"[reproduce] REFUSED: no source located for {cell!r}. Run --check for detail.")
        return 2

    if not routes_through_get_output_dir(src) and not force:
        print("[reproduce] REFUSED, and the refusal is the point.")
        print(f"  {os.path.relpath(src, REPO)} does not route through get_output_dir, so")
        print("  HDI_FRESH_RUN would be IGNORED and the run would write into the LANDED directory,")
        print("  overwriting metrics.json while this tool reported a 'reproduction'.")
        print("  Migrate the cell (one line) or pass --force and read what it prints.")
        return 1
    if not routes_through_get_output_dir(src) and force:
        print("[reproduce] --force ON A CELL THAT CANNOT BE REDIRECTED.")
        print("  The landed directory WILL be written to. Any 'reproduction' this prints is not one.")

    base = _landed_dir(cell)
    if base is None:
        print(f"[reproduce] REFUSED: no landed data directory for {cell!r} (tried data/{cell} and")
        print(f"            data/exp_{cell}). Nothing to reproduce against.")
        return 2
    fresh = base + f"__fresh_{tag}"
    landed_before = _dir_fingerprint(base)
    landed_verdict = _verdict_of(base)

    units_before = rc.unit_count(fresh)
    print(f"[reproduce] cell {cell} -> fresh sibling {os.path.basename(fresh)}")
    print(f"[reproduce] landed verdict: {landed_verdict}")
    print(f"[reproduce] fresh dir units before: {units_before}")

    env = dict(os.environ)
    env["HDI_FRESH_RUN"] = tag
    env.setdefault("PYTHONIOENCODING", "utf-8")
    cmd = [PYTHON if os.path.isfile(PYTHON) else sys.executable, src] + list(extra)
    print("[reproduce] running:", " ".join(cmd), f"(HDI_FRESH_RUN={tag}, timeout {timeout}s)")

    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=REPO, env=env, timeout=timeout,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              encoding="utf-8", errors="replace")
        rcode, tail = proc.returncode, (proc.stdout or "")[-2000:]
    except subprocess.TimeoutExpired:
        print(f"[reproduce] TIMEOUT after {timeout}s -- INCONCLUSIVE, not a failure of the cell.")
        return 3
    elapsed = time.time() - t0

    units_after = rc.unit_count(fresh)
    verdict = rc.classify_run(units_before, units_after, elapsed)
    fresh_verdict = _verdict_of(fresh)

    print(f"[reproduce] exit {rcode} in {elapsed:.1f}s | units {units_before} -> {units_after}")
    print(f"[reproduce] classify_run: {verdict.status}")

    # DID THE REDIRECT ACTUALLY TAKE? Ask the filesystem, do not infer it from the source.
    # Measured 2026-08-23 on the first real end-to-end run: a cell whose source CONTAINS
    # `get_output_dir` defines its OWN copy rather than importing the harness one, so SH-7 was inert.
    # It ran to exit 0 and the sibling was never created. The static check said redirectable and the
    # runtime truth said otherwise -- which is this repo's standing rule that static search locates
    # candidates and runtime observation decides.
    if not os.path.isdir(fresh):
        print("[reproduce] *** THE REDIRECT DID NOT TAKE. The fresh sibling was never created:")
        print("             %s" % fresh)
        print("            The cell ran but wrote nowhere this tool can see, so NOTHING here is")
        print("            evidence about the landed result. Most likely it defines its own")
        print("            get_output_dir, or builds its output path some other way, so setting")
        print("            HDI_FRESH_RUN cannot move it. The source check that accepted this cell")
        print("            tested for the STRING, not the IMPORT.")

    landed_after = _dir_fingerprint(base)
    if landed_after != landed_before:
        print("[reproduce] *** THE LANDED DIRECTORY CHANGED. The isolation did not hold, so nothing")
        print("            below is evidence about the landed record. Investigate before trusting it.")
        for k in landed_before:
            if landed_before[k] != landed_after[k]:
                print(f"              {k}: {landed_before[k]} -> {landed_after[k]}")
    else:
        print("[reproduce] landed directory unchanged (size+mtime on units.jsonl and metrics.json)")

    if not verdict.is_evidence_of_reproduction():
        print(f"[reproduce] OUTCOME: REPLAYED -- no work was done, so this says NOTHING about the")
        print(f"            result. Fresh dir already held {units_before} units; delete nothing,")
        print(f"            pick a new --tag instead.")
        return 4
    if fresh_verdict is None:
        print("[reproduce] OUTCOME: RECOMPUTED but the fresh run wrote no readable verdict.")
        return 5
    if landed_verdict is None:
        print(f"[reproduce] OUTCOME: RECOMPUTED, fresh verdict {fresh_verdict!r}, but the landed")
        print("            record has no readable verdict to compare against.")
        return 5
    if fresh_verdict == landed_verdict:
        print(f"[reproduce] OUTCOME: REPRODUCED -- recomputed from scratch and got {fresh_verdict!r}")
        print("            again. This is the only outcome that is evidence.")
        return 0
    print(f"[reproduce] OUTCOME: DIVERGED -- landed {landed_verdict!r}, fresh {fresh_verdict!r}.")
    print("            The landed record is not reproducible as recorded. Neither is automatically")
    print("            wrong; the fresh run is at HEAD and the landed one may not be.")
    return 6


def self_test() -> int:
    ok = True

    # POSITIVE CONTROL on the refusal, using REAL cells rather than fixtures: at least one cell in
    # the archive must route through get_output_dir and at least one must not. If either side is
    # empty the detector cannot be doing its job.
    import glob
    routed = bare = 0
    for p in glob.glob(os.path.join(EXPERIMENTS, "*.py"))[:400]:
        if routes_through_get_output_dir(p):
            routed += 1
        else:
            bare += 1
    if routed > 0 and bare > 0:
        print(f"[self-test] PASS: the redirect detector separates real cells ({routed} routed, {bare} bare)")
    else:
        print(f"[self-test] FAIL: detector returned one class only ({routed} routed, {bare} bare)")
        ok = False

    # NEGATIVE CONTROL: a file that does not exist is not silently 'routed'.
    if not routes_through_get_output_dir(os.path.join(EXPERIMENTS, "__no_such_cell_zzqq.py")):
        print("[self-test] PASS: a missing source is not reported as redirectable")
    else:
        print("[self-test] FAIL: a missing source read as redirectable")
        ok = False

    # A REPLAY MUST NOT BE CALLED A REPRODUCTION -- the whole reason this driver exists.
    v = rc.classify_run(10, 10, 0.0)
    if not v.is_evidence_of_reproduction():
        print("[self-test] PASS: a 0-unit re-run is NOT evidence of reproduction")
    else:
        print("[self-test] FAIL: a replay classified as a reproduction")
        ok = False
    v2 = rc.classify_run(0, 10, 5.0)
    if v2.is_evidence_of_reproduction():
        print("[self-test] PASS: a genuine recompute IS evidence")
    else:
        print("[self-test] FAIL: a real recompute rejected")
        ok = False

    # _verdict_of must not invent a verdict for a directory that has none.
    if _verdict_of(os.path.join(DATA, "__no_such_dir_zzqq")) is None:
        print("[self-test] PASS: a missing metrics.json yields no verdict (no fabrication)")
    else:
        print("[self-test] FAIL: invented a verdict")
        ok = False

    print("[self-test] " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cell", nargs="?", help="cell name, with or without the exp_ prefix")
    ap.add_argument("--check", action="store_true", help="report reproducibility, run nothing")
    ap.add_argument("--tag", default="repro", help="fresh-sibling tag (default: repro)")
    ap.add_argument("--timeout", type=int, default=3600, help="seconds (default 3600)")
    ap.add_argument("--force", action="store_true", help="run even if the cell cannot be redirected")
    ap.add_argument("--self-test", action="store_true")
    args, extra = ap.parse_known_args(argv[1:])

    if args.self_test:
        return self_test()
    if not args.cell:
        print(__doc__)
        return 2
    if args.check:
        return check(args.cell)
    return reproduce(args.cell, args.tag, args.timeout, args.force, extra)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
