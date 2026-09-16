"""WITNESS: tools/desktop_run.py's pure logic (bundle-range decision, env composition, pull-path safety,
cmd-shell quoting, exit-line parsing, dirty-tree detection, should-pull mtime rule, argv splitting, and the
base64-wrapped remote launcher/worker source it builds) -- entirely WITHOUT ssh. Then, gated on
`ssh -o BatchMode=yes home echo ok` succeeding within 10s (skipped, not failed, if unreachable), one real
integration check: `--dry-run --allow-dirty --name ... -- echo hi` prints the plan and exits 0.
Run: python verification/test_desktop_run.py"""
import os
import subprocess
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import tools.desktop_run as DR


def _check_bundle_range_decision():
    # already in sync -> nothing to do
    rng, note = DR.decide_bundle_range("abc123", "abc123", True)
    assert rng is None and "no bundle needed" in note

    # clean ancestor case -> the documented <desktop_head>..<laptop_head> range, no note
    rng, note = DR.decide_bundle_range("d0d0d0", "l1l1l1", True)
    assert rng == "d0d0d0..HEAD", rng   # ends in a REF: a sha-ended range makes an empty bundle
    assert note is None

    # desktop HEAD is NOT an ancestor (diverged / rewritten history) -> fall back to last-200, and SAY SO
    rng, note = DR.decide_bundle_range("d0d0d0", "l1l1l1", False)
    assert rng == "HEAD~200..HEAD", rng
    assert note and "not an ancestor" in note and "d0d0d0" in note and "l1l1l1" in note


def _check_env_composition():
    env = DR.compose_env({})
    assert env["OMP_NUM_THREADS"] == "4" and env["PYTHONHASHSEED"] == "0"
    # an override wins over a default ("unless overridden")
    env2 = DR.compose_env({"OMP_NUM_THREADS": "8", "HDLAB_EXP_NAME": "pri131b"})
    assert env2["OMP_NUM_THREADS"] == "8"
    assert env2["HDLAB_EXP_NAME"] == "pri131b"
    assert env2["MKL_NUM_THREADS"] == "4"  # untouched default still present
    # deterministic, sorted KEY=VAL lines
    lines = DR.format_env_lines({"B": "2", "A": "1"})
    assert lines == ["A=1", "B=2"], lines
    # --env KEY=VAL parsing, including a value that itself contains '='
    parsed = DR.parse_env_kv(["A=B", "C=D=E"])
    assert parsed == {"A": "B", "C": "D=E"}, parsed
    try:
        DR.parse_env_kv(["NOEQUALSSIGN"])
        raise AssertionError("expected ValueError for a malformed --env entry")
    except ValueError:
        pass


def _check_pull_path_safety():
    assert DR.validate_pull_path("data/exp_foo/metrics.json") == "data/exp_foo/metrics.json"
    assert DR.validate_pull_path("data\\exp_foo\\metrics.json") == "data/exp_foo/metrics.json"
    for bad in ("../data/foo", "data/../../etc/passwd", "/data/foo", "C:/data/foo", "notdata/foo", "hdlab/coref.py"):
        try:
            DR.validate_pull_path(bad)
            raise AssertionError(f"expected ValueError for unsafe --pull path {bad!r}")
        except ValueError:
            pass


def _check_cmd_shell_quoting():
    # no space, no quote needed -- an '=' alone is NOT special to cmd.exe
    assert DR.quote_cmd_arg("HDLAB_EXP_NAME=situation_model_qa_modern_v1_pri131b") == \
        "HDLAB_EXP_NAME=situation_model_qa_modern_v1_pri131b"
    # a space forces quoting, '=' inside the quotes is preserved verbatim
    assert DR.quote_cmd_arg("KEY=hello world") == '"KEY=hello world"'
    # an embedded double-quote is escaped by doubling
    assert DR.quote_cmd_arg('say "hi"') == '"say ""hi"""'
    # a whole command line: mixed quoted/unquoted tokens, exact worked example from the brief
    line = DR.build_command_line([
        ".venv/Scripts/python.exe", "experiments/exp_situation_model_qa_modern_v1.py", "--run",
    ])
    assert line == ".venv/Scripts/python.exe experiments/exp_situation_model_qa_modern_v1.py --run", line
    line2 = DR.build_command_line(["--env", "HDLAB_EXP_NAME=a value with spaces"])
    assert line2 == '--env "HDLAB_EXP_NAME=a value with spaces"', line2


def _check_exit_line_parsing():
    assert DR.parse_exit_line("=== desktop_run worker start ===\nsome output\nexit=0\n") == 0
    assert DR.parse_exit_line("stuff\nexit=-1\n") == -1
    assert DR.parse_exit_line("still running, no exit line yet\n") is None
    # only the LAST exit= line counts (a job's own stdout could echo one)
    assert DR.parse_exit_line("exit=1\nmore log lines\nexit=0\n") == 0


def _check_dirty_tree_detection():
    assert DR.is_dirty(" M hdlab/coref.py\n?? experiments/_scratch.py\n") is True
    assert DR.is_dirty("") is False
    assert DR.is_dirty("\n\n") is False
    assert DR.parse_dirty_tracked_files(" M hdlab/coref.py\nhdlab/goal_register.py\n\n") == [
        "M hdlab/coref.py", "hdlab/goal_register.py"]
    # (git diff --name-only has no status letters -- exercise that exact shape)
    assert DR.parse_dirty_tracked_files("experiments/exp_board_rows_on_the_reader_v1.py\nhdlab/coref.py\n") == [
        "experiments/exp_board_rows_on_the_reader_v1.py", "hdlab/coref.py"]


def _check_should_pull():
    assert DR.should_pull(None, 100.0, False) is True          # nothing local yet -> always pull
    assert DR.should_pull(50.0, 100.0, False) is True           # remote newer -> pull
    assert DR.should_pull(150.0, 100.0, False) is False         # laptop copy newer -> DON'T clobber it
    assert DR.should_pull(150.0, 100.0, True) is True            # ...unless --force


def _check_argv_split():
    before, after = DR.split_argv_on_dashdash(["--name", "x", "--", "cmd", "--run"])
    assert before == ["--name", "x"] and after == ["cmd", "--run"]
    before, after = DR.split_argv_on_dashdash(["--pull-only", "--name", "x"])
    assert before == ["--pull-only", "--name", "x"] and after is None
    before, after = DR.split_argv_on_dashdash(["--name", "x", "--"])
    assert after == []  # an empty command after -- is distinct from "no -- at all"


def _check_remote_source_builders():
    # worker script embeds the exact command line + env via repr() (never raw string interpolation,
    # so an embedded quote or backslash in a Windows path can't break the generated .py file)
    src = DR.build_worker_script('echo "hi"', {"A": "B"}, r"C:\AI\hd-instrument\data\hook_state\desktop_x.log",
                                  r"C:\AI\hd-instrument")
    assert repr('echo "hi"') in src
    assert repr({"A": "B"}) in src
    assert "subprocess.run" in src and "exit={}" in src
    launcher = DR.build_launcher_script(r"C:\AI\hd-instrument\data\hook_state\desktop_x.run.py",
                                         r"C:\AI\hd-instrument\data\hook_state\desktop_x.pid")
    assert "DETACHED_PROCESS" in launcher and "CREATE_NEW_PROCESS_GROUP" in launcher and "PID=" in launcher
    # 2026-09-16: the worker must BREAK AWAY from sshd's session job object (else it dies when the session
    # closes -- the first two real runs), with the WMI Create as the fallback when breakaway is refused.
    assert "CREATE_BREAKAWAY_FROM_JOB" in launcher and "Win32_Process" in launcher
    compile(launcher, "<launcher>", "exec")   # the generated source must at least parse
    # the base64 wrapper round-trips exactly, and its only quoting is the outer double-quotes cmd.exe needs
    cmd = DR.b64_exec_command(r"C:\AI\hd-instrument\.venv\Scripts\python.exe", launcher)
    import base64
    import re as _re
    m = _re.search(r"b64decode\('([^']+)'\)", cmd)
    assert m, cmd
    assert base64.b64decode(m.group(1)).decode("utf-8") == launcher


def _check_argparse_requires_command_unless_pull_only():
    try:
        DR.main(["--name", "x"])  # no '--', not --pull-only -> must refuse, not silently no-op
        raise AssertionError("expected SystemExit for a missing command")
    except SystemExit as e:
        assert e.code == 2, e.code


def _gated_integration_dry_run_check():
    """Only runs when the desktop is actually reachable (ssh alias `home`); skipped, not failed,
    otherwise -- this witness must stay green on a laptop with no network to the desktop."""
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "home", "echo", "ok"],
                            capture_output=True, text=True, timeout=10)
    except Exception:
        r = None
    if r is None or r.returncode != 0 or "ok" not in (r.stdout or ""):
        print("SKIP: desktop (ssh alias 'home') not reachable within 10s -- integration check skipped")
        return
    # --allow-dirty so this is safe to run on a laptop with real in-progress edits (routes around the
    # refusal guard the same way a real dirty-tree run would); --dry-run means NOTHING is written or shipped.
    code = DR.main(["--dry-run", "--allow-dirty", "--name", "witness_dry_run_check", "--",
                     "echo", "hi"])
    assert code == 0, f"--dry-run exited {code}"


def main() -> int:
    _check_bundle_range_decision()
    _check_env_composition()
    _check_pull_path_safety()
    _check_cmd_shell_quoting()
    _check_exit_line_parsing()
    _check_dirty_tree_detection()
    _check_should_pull()
    _check_argv_split()
    _check_remote_source_builders()
    _check_argparse_requires_command_unless_pull_only()
    _gated_integration_dry_run_check()
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128 convention; see notes/problems/447_witness_files_define_no_test_function_.../PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
