"""Unit test for PROT-018 anchor-name N-suffix binding check.

Tests the check_n_suffix_binding() function from tools/queue_add.py.

Run with:
    python tools/tests/test_prot018_n_suffix.py
"""
import sys
import os
import tempfile
from pathlib import Path

# Make queue_add importable
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

# We import only the check function; importing queue_add as a module also
# imports safe_queue which needs to be on the path (it is, via REPO/tools).
from queue_add import check_n_suffix_binding  # noqa: E402


def make_script(content: str) -> Path:
    """Write content to a temp .py file and return the path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def expect_exit6(anchor_name: str, script_content: str) -> None:
    """Assert that check_n_suffix_binding exits with code 6."""
    path = make_script(script_content)
    try:
        try:
            check_n_suffix_binding(anchor_name, path)
            raise AssertionError(
                f"Expected sys.exit(6) for anchor={anchor_name!r} but function returned normally"
            )
        except SystemExit as e:
            assert e.code == 6, (
                f"Expected exit code 6 for anchor={anchor_name!r}, got {e.code}"
            )
    finally:
        os.unlink(path)
    print(f"  PASS (exit-6 reject): {anchor_name!r}")


def expect_pass(anchor_name: str, script_content: str) -> None:
    """Assert that check_n_suffix_binding returns normally (no exit)."""
    path = make_script(script_content)
    try:
        try:
            check_n_suffix_binding(anchor_name, path)
        except SystemExit as e:
            raise AssertionError(
                f"Expected PASS for anchor={anchor_name!r} but got sys.exit({e.code})"
            )
    finally:
        os.unlink(path)
    print(f"  PASS (accepted): {anchor_name!r}")


def run_tests():
    print("PROT-018 N-suffix binding test suite")
    print("=" * 50)

    print("\n--- REJECT cases (expect exit-6) ---")

    # Core case from the bug report: anchor says _n4096, script has N=512
    expect_exit6(
        "wave14_saddle_cascade_plateau_v5_n4096",
        "N = 512\nresults = run(N)\n",
    )

    # N=512 buried in config dict
    expect_exit6(
        "exp_hebbian_storage_n8192",
        "config = {'N': 512, 'seeds': 5}\n",
    )

    # Production N is commented out, only a comment mentions 4096
    expect_exit6(
        "exp_betA_recall_n4096",
        "# N = 4096  (full run)\nN = 256  # smoke only\n",
    )

    # Anchor _n16384, script has N=4096 (close but wrong)
    expect_exit6(
        "exp_scale_sweep_n16384",
        "N = 4096\n",
    )

    print("\n--- PASS cases (expect no exit) ---")

    # Exact match: _n4096, script has N = 4096
    expect_pass(
        "wave14_saddle_cascade_plateau_v5_n4096",
        "import sys\nN = 4096\nresults = run(N)\n",
    )

    # Match with spaces around =
    expect_pass(
        "exp_betB_storage_n8192",
        "N  =  8192\n",
    )

    # Match via argparse default
    expect_pass(
        "exp_sweep_n16384",
        "parser.add_argument('--N', type=int, default=16384)\n",
    )

    # No _n<N> suffix at all — rule doesn't apply, must not reject
    expect_pass(
        "exp_wave14_betA_v3",
        "N = 512\n",
    )

    # _v<N> version suffix — must not be confused with _n<N>
    expect_pass(
        "exp_wave14_saddle_v5",
        "N = 512\n",
    )

    # Anchor has _n suffix at end (no trailing underscore), still parsed
    expect_pass(
        "exp_foo_n1024",
        "N = 1024\n",
    )

    print("\n" + "=" * 50)
    print("All tests PASSED.")


if __name__ == "__main__":
    run_tests()
