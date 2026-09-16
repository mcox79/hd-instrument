#!/usr/bin/env python
"""tools/desktop_run.py -- run a heavy job on the DESKTOP host (ssh alias `home`, repo C:\\AI\\hd-instrument,
same layout as this laptop repo) and bring the results back, so the laptop stops being the bottleneck.

    python tools/desktop_run.py --name <job> [--env KEY=VAL ...] [--pull data/<path> ...] \
        [--wait] [--timeout-min 240] [--no-sync] [--allow-dirty] [--force] [--dry-run] \
        -- <command line to run in the repo, on the desktop>

    python tools/desktop_run.py --pull-only --name <job> [--pull data/<path> ...] [--wait] [--force]

STEPS (see module docstrings on the functions below for the exact contract each implements):
  1. SYNC   -- match the desktop's git HEAD to the laptop's (bundle+fetch+reset), or copy dirty tracked
              files from hdlab/ and experiments/ if --allow-dirty. Refuses on dirty hdlab/experiments/
              without --allow-dirty.
  2. RUN    -- launch the given command on the desktop, DETACHED, with stdout+stderr going to
              data/hook_state/desktop_<name>.log and its pid to data/hook_state/desktop_<name>.pid.
  3. WAIT   -- (only with --wait) poll every 60s for the "exit=<code>" line the remote worker appends
              to the log when the command finishes, up to --timeout-min.
  4. PULL   -- scp back the log and every --pull path (skip a laptop path that's newer than the desktop
              copy, unless --force).

WHY NOT `start /b` ON THE REMOTE (see tools/start_desktop_runners.cmd's own history note): a
`start /b ... > log 2>&1` child launched from an ssh-driven cmd.exe inherits that cmd.exe's console, and
dies within seconds of the ssh session closing (CTRL_CLOSE_EVENT propagates to the whole console group).
Fix used here: the ssh-invoked process is a short-lived Python launcher that spawns the actual worker with
Win32 CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS (no console at all, so no CTRL_CLOSE_EVENT reaches it),
writes a tiny worker script to data/hook_state/desktop_<name>.run.py so no shell-quoting of the target
command line ever has to survive two hops of quoting, and returns the worker's pid before the ssh session
closes. The worker itself captures the target command's exit code in Python (subprocess.run().returncode)
rather than via cmd.exe's fragile %ERRORLEVEL% expansion, and appends "exit=<code>" to the log.

HARD LIMITS BAKED IN: --pull paths must be relative and under data/ (tools/desktop_run.py never reaches
outside data/ on either box). This tool never touches hdlab/, experiments/, notes/, preregs/, or arm_key*
on disk itself -- it only ever reads git plumbing (rev-parse/diff/merge-base) and data/hook_state/ paths.
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_STATE = os.path.join(REPO, "data", "hook_state")
SSH_HOST = "home"
REMOTE_REPO = r"C:\AI\hd-instrument"
REMOTE_PYEXE = r"C:\AI\hd-instrument\.venv\Scripts\python.exe"
DEFAULT_ENV = {
    "OMP_NUM_THREADS": "4",
    "OPENBLAS_NUM_THREADS": "4",
    "MKL_NUM_THREADS": "4",
    "PYTHONHASHSEED": "0",
}
DIRTY_CHECK_DIRS = ("hdlab", "experiments")
POLL_INTERVAL_S = 60
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0  # keep ssh/scp windowless


# --------------------------------------------------------------------------------------------------------
# PURE FUNCTIONS (no ssh/subprocess/filesystem side effects -- these are what verification/test_desktop_run.py
# unit-tests directly).
# --------------------------------------------------------------------------------------------------------

def split_argv_on_dashdash(argv: list[str]) -> tuple[list[str], list[str] | None]:
    """Split argv on the first literal '--' token. Returns (before, after) where `after` is None if no
    '--' was present at all (distinct from an empty command, which is `after == []`)."""
    for i, tok in enumerate(argv):
        if tok == "--":
            return argv[:i], argv[i + 1:]
    return argv, None


def parse_env_kv(items: list[str]) -> dict[str, str]:
    """Parse repeated --env KEY=VAL into a dict. Later entries win on duplicate keys. Raises ValueError
    on a malformed entry (no '=')."""
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--env expects KEY=VAL, got: {item!r}")
        k, v = item.split("=", 1)
        if not k:
            raise ValueError(f"--env key is empty: {item!r}")
        out[k] = v
    return out


def compose_env(overrides: dict[str, str]) -> dict[str, str]:
    """Merge the always-on defaults (thread caps + deterministic hashing) with caller overrides; an
    override for a default key wins ('unless overridden')."""
    merged = dict(DEFAULT_ENV)
    merged.update(overrides)
    return merged


def format_env_lines(env: dict[str, str]) -> list[str]:
    """Deterministic 'KEY=VAL' lines, sorted by key, for printing/logging (--dry-run plan, etc.)."""
    return [f"{k}={env[k]}" for k in sorted(env)]


def quote_cmd_arg(arg: str) -> str:
    """Quote one argv token for a Windows cmd.exe command line. Only quotes when necessary (a space,
    tab, or embedded double-quote); an embedded '=' alone does NOT need quoting under cmd.exe. An
    embedded '"' is escaped by doubling it, which is how a cmd.exe-quoted string is unquoted by a
    normal Win32 argv parser (python.exe included) inside a quoted span."""
    if arg == "":
        return '""'
    if re.search(r'[ \t"]', arg):
        return '"' + arg.replace('"', '""') + '"'
    return arg


def build_command_line(argv: list[str]) -> str:
    """Join argv tokens into one cmd.exe command line, quoting only where needed (spaces / embedded
    quotes). e.g. ['--env', 'K=V W'] -> '--env "K=V W"'; ['a=b'] -> 'a=b' (no quoting needed)."""
    return " ".join(quote_cmd_arg(a) for a in argv)


def validate_pull_path(path: str) -> str:
    """A --pull path must be relative and land under data/ on both boxes (never anywhere else). Returns
    the normalized forward-slash relative path (e.g. 'data/exp_foo/metrics.json'). Raises ValueError for
    an absolute path, a '..' component, or anything not rooted at data/."""
    p = path.replace("\\", "/").strip()
    if p.startswith("/") or (len(p) > 1 and p[1] == ":"):
        raise ValueError(f"--pull path must be relative, not absolute: {path!r}")
    parts = [seg for seg in p.split("/") if seg not in ("", ".")]
    if any(seg == ".." for seg in parts):
        raise ValueError(f"--pull path must not contain '..': {path!r}")
    if not parts or parts[0] != "data":
        raise ValueError(f"--pull path must be under data/: {path!r}")
    return "/".join(parts)


def decide_bundle_range(desktop_head: str, laptop_head: str, desktop_head_is_ancestor: bool) -> tuple[str | None, str | None]:
    """Decide the `git bundle create <out> <range>` range to bring the desktop to the laptop's HEAD.
    Returns (range_expr, note); range_expr is None when already in sync (nothing to bundle). If the
    desktop's HEAD is not an ancestor of the laptop's HEAD (diverged / desktop ahead / history rewritten),
    fall back to bundling the last 200 commits and say so via `note`."""
    if desktop_head == laptop_head:
        return None, "desktop already at laptop HEAD; no bundle needed"
    # The range must END IN A REF (HEAD), not a bare commit hash: `git bundle create` records refs, and a
    # range ending in a sha yields "Refusing to create empty bundle" (found on the first real run, 2026-09-15).
    if desktop_head_is_ancestor:
        return f"{desktop_head}..HEAD", None
    return (
        "HEAD~200..HEAD",
        f"desktop HEAD {desktop_head} is not an ancestor of laptop HEAD {laptop_head}; "
        "bundling the last 200 commits instead",
    )


def parse_dirty_tracked_files(git_diff_name_only_output: str) -> list[str]:
    """Parse `git diff --name-only -- hdlab experiments` output into a list of relative paths."""
    return [line.strip() for line in git_diff_name_only_output.splitlines() if line.strip()]


def is_dirty(git_status_porcelain_output: str) -> bool:
    """True if `git status --porcelain -- hdlab experiments` produced any line (modified, added,
    deleted, or untracked)."""
    return any(line.strip() for line in git_status_porcelain_output.splitlines())


def should_pull(local_mtime: float | None, remote_mtime: float, force: bool) -> bool:
    """Whether to pull a path back to the laptop: yes if it doesn't exist locally yet, or the remote
    copy is newer, or --force was passed. Never overwrite a laptop path that's strictly newer than the
    desktop copy unless forced."""
    if force or local_mtime is None:
        return True
    return remote_mtime > local_mtime


def parse_exit_line(log_text: str) -> int | None:
    """Find the last 'exit=<code>' line the remote worker appends when the target command finishes.
    Returns the exit code, or None if the job is still running (no such line yet)."""
    m = None
    for m in re.finditer(r"^exit=(-?\d+)\s*$", log_text, flags=re.MULTILINE):
        pass
    return int(m.group(1)) if m else None


def build_worker_script(cmdline: str, env_overrides: dict[str, str], log_path_remote: str, repo_remote: str) -> str:
    """The tiny Python source written to data/hook_state/desktop_<name>.run.py on the desktop and run
    DETACHED. It shells out to `cmdline` with the merged env, appending stdout+stderr to the log, then
    appends 'exit=<code>' captured from Python (subprocess.run().returncode) -- never from cmd.exe's
    %ERRORLEVEL%, which expands unreliably inside a single `cmd /c "..."` invocation."""
    return textwrap.dedent(f"""\
        import os, subprocess
        env = dict(os.environ)
        env.update({env_overrides!r})
        with open({log_path_remote!r}, "ab") as f:
            f.write(b"=== desktop_run worker start ===\\n")
            f.flush()
            proc = subprocess.run({cmdline!r}, shell=True, cwd={repo_remote!r}, env=env,
                                   stdout=f, stderr=subprocess.STDOUT)
        with open({log_path_remote!r}, "a") as f:
            f.write("exit={{}}\\n".format(proc.returncode))
        """)


def build_launcher_script(worker_path_remote: str, pid_path_remote: str) -> str:
    """The short-lived script run directly under ssh (attached to the ssh session): writes the worker
    script (already on disk by the time this runs -- see run_job), spawns it fully detached, records its
    pid, and prints it, then returns immediately so the ssh session can close without killing the worker."""
    return textwrap.dedent(f"""\
        import subprocess, sys
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        p = subprocess.Popen([sys.executable, {worker_path_remote!r}],
                              creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                              close_fds=True)
        with open({pid_path_remote!r}, "w") as f:
            f.write(str(p.pid))
        print("PID=" + str(p.pid))
        """)


def b64_exec_command(pyexe_remote: str, src: str) -> str:
    """A one-line cmd.exe command that runs `src` via `python -c "import base64;exec(...)"`. Base64
    sidesteps every quoting hazard of passing an arbitrary Python source string through ssh -> cmd.exe ->
    python's own argv parser in one hop."""
    b64 = base64.b64encode(src.encode("utf-8")).decode("ascii")
    return f'"{pyexe_remote}" -c "import base64;exec(base64.b64decode(\'{b64}\'))"'


# --------------------------------------------------------------------------------------------------------
# REMOTE I/O (thin wrappers around ssh/scp; kept separate from the pure logic above so the unit tests can
# exercise the logic without ever shelling out).
# --------------------------------------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(f"[desktop_run] {msg}")


def ssh_run(remote_cmd: str, timeout: int = 30) -> subprocess.CompletedProcess:
    argv = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", SSH_HOST, remote_cmd]
    _log("ssh: " + remote_cmd)
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, creationflags=_NO_WINDOW)


def scp_to(local_path: str, remote_path: str, recurse: bool = False, timeout: int = 600) -> subprocess.CompletedProcess:
    argv = ["scp", "-o", "BatchMode=yes"] + (["-r"] if recurse else []) + [local_path, f"{SSH_HOST}:{remote_path}"]
    _log("scp: " + " ".join(argv[1:]))
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, creationflags=_NO_WINDOW)


def scp_from(remote_path: str, local_path: str, recurse: bool = False, timeout: int = 600) -> subprocess.CompletedProcess:
    argv = ["scp", "-o", "BatchMode=yes"] + (["-r"] if recurse else []) + [f"{SSH_HOST}:{remote_path}", local_path]
    _log("scp: " + " ".join(argv[1:]))
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, creationflags=_NO_WINDOW)


def _run_local(argv: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=timeout, creationflags=_NO_WINDOW)


def remote_head() -> str | None:
    r = ssh_run(f'cmd /c "cd /d {REMOTE_REPO} && git rev-parse HEAD"')
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def laptop_head() -> str:
    return _run_local(["git", "rev-parse", "HEAD"]).stdout.strip()


def is_ancestor(candidate: str, of: str) -> bool:
    return _run_local(["git", "merge-base", "--is-ancestor", candidate, of]).returncode == 0


def dirty_status(dirs: tuple[str, ...] = DIRTY_CHECK_DIRS) -> str:
    return _run_local(["git", "status", "--porcelain", "--"] + list(dirs)).stdout


def dirty_tracked_files(dirs: tuple[str, ...] = DIRTY_CHECK_DIRS) -> list[str]:
    out = _run_local(["git", "diff", "--name-only", "--"] + list(dirs)).stdout
    return parse_dirty_tracked_files(out)


def remote_mtime_epoch(remote_path_bs: str) -> float | None:
    """Remote file/dir mtime (UTC epoch seconds) via PowerShell, or None if it doesn't exist."""
    ps = (f"if (Test-Path '{remote_path_bs}') {{ "
          f"(Get-Item '{remote_path_bs}').LastWriteTimeUtc.Subtract("
          f"[datetime]'1970-01-01').TotalSeconds }} else {{ 'MISSING' }}")
    r = ssh_run(f'powershell -NoProfile -Command "{ps}"')
    out = (r.stdout or "").strip()
    if r.returncode != 0 or out == "MISSING" or not out:
        return None
    try:
        return float(out)
    except ValueError:
        return None


# --------------------------------------------------------------------------------------------------------
# ORCHESTRATION
# --------------------------------------------------------------------------------------------------------

def do_sync(allow_dirty: bool, dry_run: bool) -> None:
    lh = laptop_head()
    _log(f"laptop HEAD  = {lh}")
    if is_dirty(dirty_status()):
        files = dirty_tracked_files()
        if not allow_dirty:
            raise SystemExit(
                "[desktop_run] REFUSING: uncommitted changes in hdlab/ or experiments/ "
                f"({len(files)} tracked file(s) modified; run `git status -- hdlab experiments` to see all). "
                "Pass --allow-dirty to copy the dirty tracked files across instead of refusing."
            )
        _log(f"--allow-dirty: {len(files)} dirty tracked file(s) will be copied over the bundle sync:")
        for f in files:
            _log(f"  dirty: {f}")
        if not dry_run:
            for f in files:
                local_abs = os.path.join(REPO, f)
                remote_abs = REMOTE_REPO + "\\" + f.replace("/", "\\")
                r = scp_to(local_abs, remote_abs)
                if r.returncode != 0:
                    _log(f"WARNING: scp of dirty file {f} failed: {r.stderr.strip()}")

    dh = remote_head()
    if dh is None:
        raise SystemExit("[desktop_run] could not read desktop git HEAD over ssh; is the desktop repo present?")
    _log(f"desktop HEAD = {dh}")
    rng, note = decide_bundle_range(dh, lh, is_ancestor(dh, lh) if dh != lh else True)
    if note:
        _log(note)
    if rng is None:
        _log("sync: desktop already at laptop HEAD")
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_local = os.path.join(tempfile.gettempdir(), f"desktop_run_delta_{stamp}.bundle")
    bundle_remote = f"C:/AI/desktop_run_delta_{stamp}.bundle"
    branch = f"delta_{stamp}"
    _log(f"bundle range: {rng}")
    if dry_run:
        _log(f"[dry-run] would: git bundle create {bundle_local} {rng}; scp to {bundle_remote}; "
             f"on desktop: git fetch {bundle_remote} HEAD:refs/heads/{branch} && "
             f"git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false reset --hard {branch}")
        return
    r = _run_local(["git", "bundle", "create", bundle_local, rng], timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"[desktop_run] git bundle create failed: {r.stderr.strip()}")
    r = scp_to(bundle_local, bundle_remote)
    if r.returncode != 0:
        raise SystemExit(f"[desktop_run] scp of bundle failed: {r.stderr.strip()}")
    remote_bundle_bs = bundle_remote.replace("/", "\\")
    fetch_cmd = (
        f'cmd /c "cd /d {REMOTE_REPO} && git fetch {remote_bundle_bs} HEAD:refs/heads/{branch} && '
        f'git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false reset --hard {branch}"'
    )
    r = ssh_run(fetch_cmd, timeout=180)
    if r.returncode != 0:
        raise SystemExit(f"[desktop_run] remote bundle apply failed: {r.stderr.strip()}\n{r.stdout.strip()}")
    _log(f"sync: desktop fast-forwarded to {lh} via {branch}")


def run_job(name: str, argv: list[str], env_overrides: dict[str, str], dry_run: bool) -> int | None:
    """Launch argv (already-split remote command tokens) detached on the desktop. Returns the worker
    pid on success, or None on --dry-run."""
    os.makedirs(HOOK_STATE, exist_ok=True)  # local mirror dir for humans tailing the same relative path
    cmdline = build_command_line(argv)
    env = compose_env(env_overrides)
    log_remote = f"{REMOTE_REPO}\\data\\hook_state\\desktop_{name}.log"
    pid_remote = f"{REMOTE_REPO}\\data\\hook_state\\desktop_{name}.pid"
    worker_remote = f"{REMOTE_REPO}\\data\\hook_state\\desktop_{name}.run.py"
    worker_src = build_worker_script(cmdline, env, log_remote, REMOTE_REPO)
    launcher_src = build_launcher_script(worker_remote, pid_remote)
    _log(f"job {name!r} command line: {cmdline}")
    _log("env: " + ", ".join(format_env_lines(env)))
    if dry_run:
        _log(f"[dry-run] would write worker script to {worker_remote}, launch it detached, "
             f"log -> {log_remote}, pid -> {pid_remote}")
        return None
    b64 = base64.b64encode(worker_src.encode("utf-8")).decode("ascii")
    write_worker_cmd = (
        f'cmd /c "mkdir {REMOTE_REPO}\\data\\hook_state 2>nul & '
        f'\"{REMOTE_PYEXE}\" -c \"import base64;open(r\'{worker_remote}\',\'w\').write('
        f'base64.b64decode(\'{b64}\').decode(\'utf-8\'))\""'
    )
    r = ssh_run(write_worker_cmd)
    if r.returncode != 0:
        raise SystemExit(f"[desktop_run] failed to write remote worker script: {r.stderr.strip()}\n{r.stdout.strip()}")
    launch_cmd = b64_exec_command(REMOTE_PYEXE, launcher_src)
    r = ssh_run(launch_cmd)
    if r.returncode != 0:
        raise SystemExit(f"[desktop_run] failed to launch job on desktop: {r.stderr.strip()}\n{r.stdout.strip()}")
    m = re.search(r"PID=(\d+)", r.stdout or "")
    if not m:
        raise SystemExit(f"[desktop_run] launcher ran but printed no PID: {r.stdout!r} {r.stderr!r}")
    pid = int(m.group(1))
    _log(f"job {name!r} launched detached on desktop, pid={pid}, log={log_remote}")
    return pid


def read_remote_log(name: str) -> str:
    r = ssh_run(f'cmd /c type "{REMOTE_REPO}\\data\\hook_state\\desktop_{name}.log" 2^>nul')
    return r.stdout or ""


def remote_pid_alive(pid: int) -> bool:
    r = ssh_run(f'cmd /c tasklist /FI "PID eq {pid}"')
    return str(pid) in (r.stdout or "")


def remote_pid(name: str) -> int | None:
    r = ssh_run(f'cmd /c type "{REMOTE_REPO}\\data\\hook_state\\desktop_{name}.pid" 2^>nul')
    out = (r.stdout or "").strip()
    return int(out) if out.isdigit() else None


def wait_for_completion(name: str, timeout_min: int) -> tuple[str, int | None]:
    """Poll every POLL_INTERVAL_S for an 'exit=<code>' line. Returns (status, exit_code):
    status is one of 'done', 'timeout', 'vanished' (pid gone, no exit= line -- crashed/killed)."""
    deadline = time.monotonic() + timeout_min * 60
    pid = remote_pid(name)
    while True:
        log_text = read_remote_log(name)
        code = parse_exit_line(log_text)
        if code is not None:
            return "done", code
        if pid is not None and not remote_pid_alive(pid):
            return "vanished", None
        if time.monotonic() >= deadline:
            return "timeout", None
        _log(f"job {name!r} still running (pid={pid}); polling again in {POLL_INTERVAL_S}s")
        time.sleep(POLL_INTERVAL_S)


def pull_results(name: str, pull_paths: list[str], force: bool) -> int:
    """Pull the log plus every validated --pull path. Skips a laptop path newer than its desktop copy
    unless --force. Returns the count of paths actually pulled."""
    pulled = 0
    log_remote = f"{REMOTE_REPO}\\data\\hook_state\\desktop_{name}.log"
    log_local = os.path.join(HOOK_STATE, f"desktop_{name}.log")
    remote_mt = remote_mtime_epoch(log_remote)
    local_mt = os.path.getmtime(log_local) if os.path.exists(log_local) else None
    if remote_mt is not None and should_pull(local_mt, remote_mt, force):
        r = scp_from(log_remote, log_local)
        if r.returncode == 0:
            pulled += 1
        else:
            _log(f"WARNING: could not pull log: {r.stderr.strip()}")
    for raw in pull_paths:
        rel = validate_pull_path(raw)
        remote_abs = REMOTE_REPO + "\\" + rel.replace("/", "\\")
        local_abs = os.path.join(REPO, rel.replace("/", os.sep))
        remote_mt = remote_mtime_epoch(remote_abs)
        if remote_mt is None:
            _log(f"WARNING: --pull path not found on desktop: {rel}")
            continue
        local_mt = os.path.getmtime(local_abs) if os.path.exists(local_abs) else None
        if not should_pull(local_mt, remote_mt, force):
            _log(f"skip (laptop copy newer, use --force to override): {rel}")
            continue
        os.makedirs(os.path.dirname(local_abs) or ".", exist_ok=True)
        recurse = os.path.isdir(local_abs) or "." not in os.path.basename(rel)
        r = scp_from(remote_abs, local_abs, recurse=True)
        if r.returncode != 0:
            # fall back to a non-recursive copy for a plain file
            r = scp_from(remote_abs, local_abs, recurse=False)
        if r.returncode == 0:
            pulled += 1
            _log(f"pulled: {rel}")
        else:
            _log(f"WARNING: could not pull {rel}: {r.stderr.strip()}")
    return pulled


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="job name; keys data/hook_state/desktop_<name>.{log,pid,run.py}")
    ap.add_argument("--env", action="append", default=[], metavar="KEY=VAL", help="repeatable env override")
    ap.add_argument("--pull", action="append", default=[], dest="pull_paths", metavar="data/PATH",
                     help="repeatable; a data/ path to copy back")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, touch nothing, exit 0")
    ap.add_argument("--no-sync", action="store_true", help="skip the git-HEAD sync step")
    ap.add_argument("--wait", action="store_true", help="poll every 60s for completion, then pull")
    ap.add_argument("--timeout-min", type=int, default=240, help="max minutes to poll with --wait (default 240)")
    ap.add_argument("--pull-only", action="store_true", help="skip sync+run; just check/pull an existing job by --name")
    ap.add_argument("--allow-dirty", action="store_true",
                     help="permit uncommitted changes in hdlab/ or experiments/ by copying the dirty tracked files")
    ap.add_argument("--force", action="store_true", help="overwrite a laptop path even if it's newer than the desktop copy")
    return ap


def main(argv: list[str] | None = None) -> int:
    raw = sys.argv[1:] if argv is None else argv
    opts_argv, cmd_after_dashdash = split_argv_on_dashdash(raw)
    ap = build_parser()
    args = ap.parse_args(opts_argv)

    if not args.pull_only and not cmd_after_dashdash:
        ap.error("a command is required after `--` (unless --pull-only is given)")

    try:
        env_overrides = parse_env_kv(args.env)
        for p in args.pull_paths:
            validate_pull_path(p)  # fail fast on a malformed --pull path before doing anything remote
    except ValueError as e:
        ap.error(str(e))
        return 2

    if args.pull_only:
        _log(f"--pull-only: checking job {args.name!r}")
        if args.wait:
            status, code = wait_for_completion(args.name, args.timeout_min)
        else:
            log_text = read_remote_log(args.name)
            code = parse_exit_line(log_text)
            status = "done" if code is not None else "running"
        pulled = pull_results(args.name, args.pull_paths, args.force)
        print(f"[desktop_run] {args.name}: {status}"
              f"{f' exit={code}' if code is not None else ''} "
              f"log={os.path.join(HOOK_STATE, f'desktop_{args.name}.log')} pulled={pulled} files")
        return 0 if status == "done" and code == 0 else (0 if status in ("running",) else 1)

    if not args.no_sync:
        do_sync(args.allow_dirty, args.dry_run)
    else:
        _log("--no-sync: skipping git-HEAD sync")

    pid = run_job(args.name, cmd_after_dashdash, env_overrides, args.dry_run)

    if args.dry_run:
        print(f"[desktop_run] {args.name}: dry-run log={os.path.join(HOOK_STATE, f'desktop_{args.name}.log')} pulled=0 files")
        return 0

    if not args.wait:
        pull_cmd = (f"python tools/desktop_run.py --pull-only --name {args.name} --wait "
                    + " ".join(f"--pull {p}" for p in args.pull_paths))
        _log(f"launched (pid={pid}); not waiting. Pull later with:\n    {pull_cmd}")
        print(f"[desktop_run] {args.name}: launched pid={pid} "
              f"log={os.path.join(HOOK_STATE, f'desktop_{args.name}.log')} pulled=0 files")
        return 0

    status, code = wait_for_completion(args.name, args.timeout_min)
    pulled = pull_results(args.name, args.pull_paths, args.force)
    print(f"[desktop_run] {args.name}: {status}"
          f"{f' exit={code}' if code is not None else ''} "
          f"log={os.path.join(HOOK_STATE, f'desktop_{args.name}.log')} pulled={pulled} files")
    return 0 if status == "done" and code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
