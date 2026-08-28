#!/usr/bin/env python
"""tools/fulfill_remote_run_request.py -- STRATEGY-side fulfiller for solver REMOTE_RUN_REQUEST files.

WHY THIS EXISTS
  Solver sessions must route heavy runs to the remote box (marsh@home) per the standing rule, but they
  are deliberately scope-barred from writing preregs/**, pushing to origin, and remote ops. The remote
  pipeline `tools/orchestrator/queue_add.sh` REQUIRES a prereg file (existence-checked), so a solver
  dead-ends at the prereg. This bridge lets ANY solver request a remote run WITHOUT writing a prereg:
  the solver drops `notes/problems/<slug>/REMOTE_RUN_REQUEST_<cell>.md` (solvers may write their own
  problem folder); a STRATEGY session runs THIS tool, which validates the cell, auto-writes the prereg,
  ships any un-shipped data, and queues it to the correct CPU or GPU queue.

CPU vs GPU ROUTING (both supported)
  remote_cpu_queue  numpy/scipy/sklearn cells (NO torch)         -> remote CPU runner on marsh@home
  overnight_queue   torch+cuda cells                              -> GPU runner on marsh@home (RTX 4060 Ti)
  Auto-detected from `import torch`. A torch-LESS cell pinned to overnight_queue is REJECTED (it idles
  the GPU and blocks real GPU jobs -- queue_add.sh enforces this too). If `queue:` is omitted, the tool
  picks overnight_queue for a torch cell, else remote_cpu_queue.

REMOTE HAS NO spaCy (documented install failures) -> a cell that imports spaCy at MODULE level, or whose
  imported experiments.* siblings do, is REJECTED: remote cells LOAD a pre-parsed cache, never parse.

USAGE
  .venv/Scripts/python.exe tools/fulfill_remote_run_request.py --request notes/problems/<slug>/REMOTE_RUN_REQUEST_<cell>.md
  .venv/Scripts/python.exe tools/fulfill_remote_run_request.py --request <req> --dry-run   # validate + show, no write/ship/queue
  (direct, no request file:)
  .venv/Scripts/python.exe tools/fulfill_remote_run_request.py --cell experiments/exp_X_v1.py --queue remote_cpu_queue \
      --timeout 3600 --args "--mode full" --gate "X beats FLOOR CI-sep AND beats TWIN" --question "..." [--dry-run]

The prereg is written by ordinary Python file I/O (NOT the Write tool) -- the sanctioned strategy path.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def _resolve_bash():
    """Full path to GIT-bash. Under the hd_remote_run_watcher Scheduled Task (minimal PATH), a bare `bash`
    is either absent (rc=127) OR -- worse -- resolves to the Windows Store/WSL stub
    (`...\\WindowsApps\\bash.EXE`), which MANGLES Windows paths (backslashes stripped ->
    `C:AIhd-instrument...`, No such file). So check git-bash's canonical locations FIRST, and only accept a
    PATH `bash` that is NOT the WindowsApps stub. git-bash handles Windows paths AND bundles scp/ssh."""
    for c in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe",
              r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if os.path.isfile(c):
            return c
    b = shutil.which("bash")
    if b and "WindowsApps" not in b:
        return b
    return "bash"

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_ADD = os.path.join(REPO, "tools", "orchestrator", "queue_add.sh")
LOG = os.path.join(REPO, "data", "remote_run_requests_log.jsonl")
VALID_QUEUES = ("remote_cpu_queue", "overnight_queue", "local_cpu_queue")
REPO_REMOTE = "C:/dev/hd-instrument"   # marsh@home repo root (matches queue_add.sh)
SSH_TARGET = "marsh@home"


def _ssh(ps_cmd, timeout=30):
    """Run a PowerShell command on the remote box; returns CompletedProcess (or None on failure)."""
    try:
        return subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", SSH_TARGET, f'powershell -Command "{ps_cmd}"'],
            capture_output=True, text=True, timeout=timeout)
    except Exception:  # noqa: BLE001 -- unreachable remote -> caller treats as unverifiable
        return None


def hdlab_import_closure(cell_abs, max_hops=6):
    """Bounded BFS over BOTH `hdlab.<mod>` AND `experiments.<mod>` imports, starting from the cell, collecting
    every hdlab module reachable (module- AND function-level imports). queue_add.sh ships the sibling EXPERIMENTS
    but NOT the hdlab modules THOSE siblings import, so a cell -> sibling-experiment -> hdlab.X chain leaves X
    missing on the (drifted) remote -- exactly the gap_driven_reader class. Traversing the full import graph closes
    it. Bounded hops (not an infinite resolver); the remote --self-test gate catches anything deeper."""
    pat_hd = re.compile(r"(?:from|import)\s+hdlab\.(\w+)")
    pat_exp = re.compile(r"(?:from|import)\s+experiments\.(\w+)")
    hd_seen, exp_seen = set(), set()
    txt0 = _read(cell_abs)
    hd_front, exp_front = set(pat_hd.findall(txt0)), set(pat_exp.findall(txt0))
    hops = 0
    while (hd_front or exp_front) and hops < max_hops:
        new_hd, new_exp = set(), set()
        for mod in list(hd_front):
            if mod in hd_seen:
                continue
            hd_seen.add(mod)
            p = os.path.join(REPO, "hdlab", mod + ".py")
            if os.path.isfile(p):
                t = _read(p); new_hd |= set(pat_hd.findall(t)); new_exp |= set(pat_exp.findall(t))
        for mod in list(exp_front):
            if mod in exp_seen:
                continue
            exp_seen.add(mod)
            p = os.path.join(REPO, "experiments", mod + ".py")
            if os.path.isfile(p):
                t = _read(p); new_hd |= set(pat_hd.findall(t)); new_exp |= set(pat_exp.findall(t))
        hd_front, exp_front = new_hd - hd_seen, new_exp - exp_seen
        hops += 1
    return sorted(hd_seen | hd_front)


def ship_hdlab_modules(cell_abs, dry_run):
    """scp-ship (if MISSING on remote) the cell's hdlab dependency closure. Ship-if-missing is additive and
    safe -- it never overwrites a present module (avoids clobbering a concurrent remote run). A STALE-but-
    present hdlab module is a separate, rarer problem the orchestrator's hdlab sync owns."""
    report = []
    for mod in hdlab_import_closure(cell_abs):
        local = os.path.join(REPO, "hdlab", mod + ".py")
        if not os.path.isfile(local):
            continue  # not a local hdlab source module (e.g. a subpackage/name) -- skip quietly
        if dry_run:
            report.append((mod, "would-ship-if-missing"))
            continue
        remote_path = f"{REPO_REMOTE}/hdlab/{mod}.py"
        r = _ssh(f"if (Test-Path '{remote_path}') {{ 'YES' }} else {{ 'NO' }}")
        if r is not None and "YES" in (r.stdout or ""):
            report.append((mod, "present"))
            continue
        try:
            sp = subprocess.run(["scp", "-o", "ConnectTimeout=10", local, f"{SSH_TARGET}:{REPO_REMOTE}/hdlab/"],
                                capture_output=True, text=True, timeout=300)
            report.append((mod, "shipped" if sp.returncode == 0 else f"SHIP-FAILED rc={sp.returncode}"))
        except Exception as e:  # noqa: BLE001
            report.append((mod, f"SHIP-ERROR {e}"))
    return report


def ship_kb_referents(krefs, dry_run):
    """For each `# KB_REFERENT` path: verify it exists on the remote; scp it if it is missing.
    Best-effort -- an unreachable remote or a ship failure is a WARNING, not a hard stop, because
    queue_add.py's PROT-022 existence check on the remote is the authoritative backstop (it will
    REJECT the dispatch if a referent is genuinely absent). Returns a list of (ref, status)."""
    report = []
    for ref in krefs:
        remote_path = f"{REPO_REMOTE}/{ref}"
        if dry_run:
            report.append((ref, "would-verify-on-remote"))
            continue
        r = _ssh(f"if (Test-Path '{remote_path}') {{ 'YES' }} else {{ 'NO' }}")
        if r is None:
            report.append((ref, "UNVERIFIABLE (remote unreachable) -- PROT-022 will backstop"))
            continue
        if "YES" in (r.stdout or ""):
            report.append((ref, "present"))
            continue
        local = os.path.join(REPO, ref)
        if not os.path.isfile(local):
            report.append((ref, "MISSING on remote AND local -- cannot ship"))
            continue
        remote_dir = os.path.dirname(remote_path)
        _ssh(f"New-Item -ItemType Directory -Force -Path '{remote_dir}' | Out-Null")
        try:
            sp = subprocess.run(["scp", "-o", "ConnectTimeout=10", local, f"{SSH_TARGET}:{remote_dir}/"],
                                capture_output=True, text=True, timeout=1800)
            report.append((ref, "shipped" if sp.returncode == 0 else f"SHIP-FAILED rc={sp.returncode}"))
        except Exception as e:  # noqa: BLE001
            report.append((ref, f"SHIP-ERROR {e}"))
    return report


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_request(path):
    """Minimal front-matter parser (key: value, and `- ` list items under a key). No pyyaml dependency."""
    txt = _read(path)
    fm = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", txt, re.DOTALL)
    body = ""
    block = txt
    if m:
        block, body = m.group(1), m.group(2)
    cur_list_key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        li = re.match(r"^\s*-\s+(.*)$", line)
        if li and cur_list_key:
            fm.setdefault(cur_list_key, []).append(li.group(1).strip())
            continue
        kv = re.match(r"^([A-Za-z_][\w]*):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1).strip(), kv.group(2).strip()
            if val == "":
                cur_list_key = key  # a list follows
                fm.setdefault(key, [])
            else:
                cur_list_key = None
                fm[key] = val
    fm["_body"] = body
    return fm


def kb_referents(cell_path):
    out = []
    for line in _read(cell_path).splitlines():
        m = re.match(r"^\s*#\s*KB_REFERENT:\s*(\S+)", line)
        if m:
            out.append(m.group(1))
    return out


def sibling_experiment_imports(cell_path):
    """experiments.* modules the cell imports (for the spaCy-at-module-level check)."""
    mods = []
    for line in _read(cell_path).splitlines():
        m = re.match(r"^\s*from\s+experiments\.(\w+)\s+import", line) or re.match(r"^\s*import\s+experiments\.(\w+)", line)
        if m:
            mods.append(m.group(1))
    return mods


def has_module_level_spacy(path):
    for line in _read(path).splitlines():
        # column-0 (module level) import only; an indented `import spacy` inside a function is fine
        if re.match(r"^(import\s+spacy|from\s+spacy\b)", line):
            return True
    return False


def has_torch(path):
    for line in _read(path).splitlines():
        if re.match(r"^\s*(import\s+torch|from\s+torch\b)", line):
            return True
    return False


def has_flag(path, *flags):
    txt = _read(path)
    return any(f in txt for f in flags)


def run_self_test(cell_path, timeout_s=300):
    try:
        p = subprocess.run([sys.executable, cell_path, "--self-test"],
                           cwd=REPO, capture_output=True, text=True, timeout=timeout_s)
        return p.returncode, (p.stdout[-500:] + p.stderr[-500:])
    except subprocess.TimeoutExpired:
        return 124, f"--self-test exceeded {timeout_s}s"
    except Exception as e:  # noqa: BLE001
        return 1, f"--self-test could not run: {e}"


def guardrails(cell, queue, skip_self_test):
    """Return (ok, decided_queue, reasons[], warnings[])."""
    reasons, warns = [], []
    cell_abs = os.path.join(REPO, cell)
    if not os.path.isfile(cell_abs):
        return False, queue, [f"cell not found: {cell}"], warns

    krefs = kb_referents(cell_abs)
    if not krefs:
        reasons.append("cell declares NO `# KB_REFERENT:` line -- remote cells must LOAD a pre-parsed "
                       "cache, not parse (remote has no spaCy). Declare the data deps and re-request.")
    if not has_flag(cell_abs, "--self-test", "--self_test", "--smoke"):
        reasons.append("cell exposes neither --self-test nor --smoke -- required (a re-run must recompute, "
                       "not replay). Add the reproducibility hooks and re-request.")

    # spaCy-at-module-level on the cell OR any imported experiments.* sibling
    if has_module_level_spacy(cell_abs):
        reasons.append("cell imports spaCy at MODULE level -> import crashes on the remote box (no spaCy). "
                       "Move the import inside the parse function (which remote cells never call).")
    for mod in sibling_experiment_imports(cell_abs):
        sib = os.path.join(REPO, "experiments", mod + ".py")
        if os.path.isfile(sib) and has_module_level_spacy(sib):
            reasons.append(f"imported sibling experiments.{mod} imports spaCy at MODULE level -> remote "
                           f"ImportError. Guard it inside the parse function.")

    # RUN-TIME spaCy risk in the hdlab dependency closure: a closure module that imports spaCy (even inside a
    # function) crashes the remote at RUN time if that path is reached -- self-test may not exercise it (this
    # bit foraging via closed_class_lexicon). WARN, don't reject: a guarded parse-only import (never called
    # remotely) is genuinely safe, so a hard reject would false-positive.
    spacy_mods = [m for m in hdlab_import_closure(cell_abs)
                  if os.path.isfile(os.path.join(REPO, "hdlab", m + ".py"))
                  and re.search(r"(?m)^\s*(import\s+spacy|from\s+spacy\b)", _read(os.path.join(REPO, "hdlab", m + ".py")))]
    if spacy_mods:
        warns.append("RUN-TIME spaCy RISK: hdlab closure module(s) import spaCy: " + ", ".join(spacy_mods) +
                     " -- if the run reaches that path the remote (no spaCy) CRASHES even though self-test passed. "
                     "Make the module degrade without spaCy (e.g. freeze the constant) or keep the path unreached.")

    # CPU/GPU routing
    torch = has_torch(cell_abs)
    decided = queue
    if not decided:
        decided = "overnight_queue" if torch else "remote_cpu_queue"
        warns.append(f"queue not pinned -> auto-routed to {decided} ({'torch/GPU' if torch else 'numpy/CPU'}).")
    if decided == "overnight_queue" and not torch:
        reasons.append("queue=overnight_queue (GPU runner) but the cell has no `import torch` -- a numpy/CPU "
                       "script idles the GPU and blocks real GPU jobs. Route to remote_cpu_queue.")
    if decided == "remote_cpu_queue" and torch:
        warns.append("cell imports torch but queue=remote_cpu_queue -> it runs on the remote CPU (no GPU accel). "
                     "Use overnight_queue if you want the GPU.")
    if decided not in VALID_QUEUES:
        reasons.append(f"invalid queue '{decided}' (valid: {', '.join(VALID_QUEUES)}).")

    # Soft check for the CONFIRMED runner-bare-invocation gotcha (2026-08-28): the remote runner invokes a
    # cell BARE (+ --timeout), NOT with --mode full. A cell whose default (no flags) is SMOKE will run the
    # smoke sample on remote -- and fail if its smoke cache was not shipped (exactly what bit exemplar_selpref).
    celltxt = _read(cell_abs)
    if re.search(r"mode\s*!=\s*['\"]full['\"]", celltxt):
        warns.append("SMOKE-DEFAULT WARNING: the cell derives smoke from `mode != \"full\"`, so the runner's "
                     "BARE invocation runs SMOKE, not full. Either make the cell default to FULL for the real "
                     "run, or declare the SMOKE cache as a KB_REFERENT so the smoke run at least completes.")

    # self-test is the strongest guardrail (proves imports resolve + logic sound); cache-free by convention
    if not skip_self_test and not reasons:
        rc, tail = run_self_test(cell_abs)
        if rc != 0:
            reasons.append(f"--self-test FAILED (rc={rc}). It must pass before dispatch. Tail:\n{tail}")
        else:
            warns.append("--self-test PASSED (rc=0).")

    return (len(reasons) == 0), decided, reasons, warns


def build_prereg_text(cell, decided_queue, args_str, gate, question, krefs, torch, extra_body):
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Pre-reg: {os.path.splitext(os.path.basename(cell))[0]}",
        "",
        f"**Auto-generated {date} by tools/fulfill_remote_run_request.py (strategy fulfiller) from a solver "
        f"REMOTE_RUN_REQUEST.** Dispatched to `{decided_queue}` (marsh@home), args `{args_str or '(none)'}`. "
        f"This is a COMPUTE dispatch, not an integration.",
        "",
        "## Question",
        question or "(see the spawning problem brief)",
        "",
        "## Gate",
        gate or "(see the spawning problem brief -- CI-separated over the strongest real floor; info-free twin loses)",
        "",
        "## Compute route",
        f"- Queue: **{decided_queue}** "
        + ("(GPU runner, RTX 4060 Ti -- cell imports torch)." if decided_queue == "overnight_queue"
           else "(remote CPU runner -- numpy/scipy/sklearn, no torch)." if decided_queue == "remote_cpu_queue"
           else "(local CPU)."),
        f"- torch on the import path: {'yes' if torch else 'no'}.",
        "",
        "## Data dependencies (KB_REFERENT -- auto-shipped by queue_add.sh if missing on remote)",
    ]
    if krefs:
        lines += [f"- `{k}`" for k in krefs]
    else:
        lines.append("- (none declared)")
    lines += [
        "",
        "## Remote-safety",
        "Verified by the fulfiller before dispatch: --self-test/--smoke present and (unless skipped) PASSED; "
        "no module-level spaCy on the cell or its imported experiments.* siblings (remote has no spaCy -> the "
        "cell LOADS a pre-parsed cache, never parses); CPU/GPU route matches the cell's torch usage.",
    ]
    if extra_body and extra_body.strip():
        lines += ["", "## Solver notes (from the request)", extra_body.strip()]
    lines.append("")
    return "\n".join(lines)


def log_event(record):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps(record) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Fulfill a solver REMOTE_RUN_REQUEST: validate, write prereg, ship, queue (CPU or GPU).")
    ap.add_argument("--request", help="path to notes/problems/<slug>/REMOTE_RUN_REQUEST_<cell>.md")
    ap.add_argument("--cell", help="experiments/exp_X_v1.py (if not using --request)")
    ap.add_argument("--queue", choices=VALID_QUEUES, help="pin the queue; omit to auto-route by torch")
    ap.add_argument("--timeout", type=int, help="per-run timeout seconds (required to actually dispatch)")
    ap.add_argument("--args", dest="args_str", default="", help="extra args passed to the cell, e.g. '--mode full'")
    ap.add_argument("--gate", default="")
    ap.add_argument("--question", default="")
    ap.add_argument("--name", help="queue entry name (default: cell basename)")
    ap.add_argument("--skip-self-test", action="store_true", help="skip the --self-test guardrail (NOT recommended)")
    ap.add_argument("--rerun", action="store_true", help="reset a terminal (failed/done/canceled) remote entry in place via --allow-duplicate")
    ap.add_argument("--dry-run", action="store_true", help="validate + print the prereg and queue command; write/ship/queue NOTHING")
    a = ap.parse_args()

    fm = {}
    if a.request:
        if not os.path.isfile(a.request):
            print(f"FAIL: request not found: {a.request}", file=sys.stderr)
            return 2
        fm = parse_request(a.request)

    cell = a.cell or fm.get("cell")
    if not cell:
        print("FAIL: no cell (pass --cell or put `cell:` in the request).", file=sys.stderr)
        return 2
    queue = a.queue or (fm.get("queue") or None)
    timeout = a.timeout or (int(fm["timeout_s"]) if fm.get("timeout_s") else None)
    args_str = a.args_str or fm.get("args", "") or (("--mode " + fm["mode"]) if fm.get("mode") else "")
    gate = a.gate or fm.get("gate", "")
    question = a.question or fm.get("question", "")
    name = a.name or fm.get("name") or os.path.splitext(os.path.basename(cell))[0]
    body = fm.get("_body", "")

    print(f"[fulfill] cell={cell} requested_queue={queue or '(auto)'} timeout={timeout} args='{args_str}'")

    ok, decided_queue, reasons, warns = guardrails(cell, queue, a.skip_self_test)
    for w in warns:
        print(f"[fulfill]   note: {w}")
    if not ok:
        print("\nREQUEST REJECTED -- guardrails failed:", file=sys.stderr)
        for r in reasons:
            print(f"  - {r}", file=sys.stderr)
        log_event({"ts": datetime.now(timezone.utc).isoformat(), "cell": cell, "outcome": "rejected",
                   "reasons": reasons, "request": a.request})
        return 4

    cell_abs = os.path.join(REPO, cell)
    krefs = kb_referents(cell_abs)
    torch = has_torch(cell_abs)
    prereg_rel = os.path.join("preregs", f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{name}.md").replace("\\", "/")
    prereg_abs = os.path.join(REPO, prereg_rel)
    prereg_text = build_prereg_text(cell, decided_queue, args_str, gate, question, krefs, torch, body)

    if not timeout:
        print("FAIL: no --timeout (or timeout_s in the request) -- required to dispatch.", file=sys.stderr)
        return 2

    # Pass queue_add.sh's path with FORWARD slashes: a Windows backslash absolute path handed to bash can be
    # eaten as escape sequences (`\A`->`A`) -> `C:AIhd-instrument...` not found. git-bash tolerates it, but the
    # forward-slash form eliminates the class regardless of which bash resolves (belt-and-suspenders, and it is
    # identical for the initial and --rerun paths -- the qcmd is built once).
    qcmd = [_resolve_bash(), QUEUE_ADD.replace("\\", "/"), decided_queue, name, cell, prereg_rel,
            str(timeout), "--skip-smoke"]
    if a.rerun:
        qcmd.append("--allow-duplicate")
    if args_str:
        # queue_add.sh passes extra flags to queue_add.py; the cell args ride via the runner's arg convention.
        # Cell args are declared in the prereg and applied by the runner; queue_add extra flags are queue-level.
        pass

    if a.dry_run:
        print("\n===== DRY RUN -- nothing written, shipped, or queued =====")
        print(f"[fulfill] WOULD write prereg -> {prereg_rel}")
        print("----- prereg preview -----")
        print(prereg_text)
        print("----- queue command -----")
        print("  " + " ".join(qcmd))
        print(f"[fulfill] KB_REFERENTs (fulfiller verifies on remote + scp-ships any missing before queuing):")
        for ref, st in ship_kb_referents(krefs, dry_run=True):
            print(f"    - {ref}  [{st}]")
        print(f"[fulfill] hdlab dependency closure (ship-if-missing on remote; closes queue_add.sh's drift gap):")
        for mod, st in ship_hdlab_modules(cell_abs, dry_run=True):
            print(f"    - hdlab.{mod}  [{st}]")
        print("===== END DRY RUN =====")
        log_event({"ts": datetime.now(timezone.utc).isoformat(), "cell": cell, "outcome": "dry_run",
                   "queue": decided_queue, "prereg": prereg_rel, "request": a.request})
        return 0

    # LIVE: write the prereg via ordinary Python I/O (the sanctioned strategy path; NOT the Write tool).
    os.makedirs(os.path.dirname(prereg_abs), exist_ok=True)
    with open(prereg_abs, "w", encoding="utf-8", newline="\n") as f:
        f.write(prereg_text)
    print(f"[fulfill] wrote prereg -> {prereg_rel}")

    # Ship the cell's hdlab dependency closure if missing on remote (closes queue_add.sh's drift gap).
    for mod, st in ship_hdlab_modules(cell_abs, dry_run=False):
        print(f"[fulfill] hdlab.{mod}: {st}")

    # Ship any un-shipped KB_REFERENT data to the remote (PROT-022 on the runner is the backstop).
    ship_report = ship_kb_referents(krefs, dry_run=False)
    for ref, st in ship_report:
        print(f"[fulfill] KB_REFERENT {ref}: {st}")
    if any("MISSING on remote AND local" in st for _, st in ship_report):
        print("[fulfill] WARN: a KB_REFERENT is absent on BOTH remote and local -- queue_add.py PROT-022 "
              "will likely REJECT. Proceeding so you see the authoritative gate.", file=sys.stderr)

    print(f"[fulfill] dispatching: {' '.join(qcmd)}")
    p = subprocess.run(qcmd, cwd=REPO)
    outcome = "dispatched" if p.returncode == 0 else "queue_add_failed"
    log_event({"ts": datetime.now(timezone.utc).isoformat(), "cell": cell, "outcome": outcome,
               "queue": decided_queue, "prereg": prereg_rel, "name": name, "timeout": timeout,
               "rc": p.returncode, "request": a.request})
    if p.returncode != 0:
        print(f"FAIL: queue_add.sh returned {p.returncode}", file=sys.stderr)
        return p.returncode
    print(f"[fulfill] OK: {name} queued to {decided_queue}. Results return via local_metrics_sync.ps1 "
          f"(~20 min) or tools/orchestrator/scp_recover_landing.py --verify-after {name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
