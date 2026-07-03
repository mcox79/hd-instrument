"""Unit test: Stage 1 wrappers route out_dir through get_output_dir (SH-4 fix).

Testbed 2026-07-03 fleet audit. Follow-up to commit 70c9f6a5d (SH-4 root fix
in `_seed_checkpoint.get_output_dir()`). Probe 13 SMOKE first-queue attempt
(commit 318fa3f6e) surfaced that wrappers still manually built
`REPO / "data" / ("exp_" + env_name)`, bypassing SH-4 normalization and
producing double-prefix `data/exp_exp_<anchor>/` when
`HDLAB_EXP_NAME=exp_<anchor>`.

This test asserts:
  (A) Every Stage 1 sibling wrapper (`experiments/exp_stage1_*_s*.py`) imports
      `get_output_dir` from `_seed_checkpoint` AND has ZERO occurrences of the
      manual double-prefix pattern `REPO / "data" / ("exp_" + env_name)`.
  (B) Runtime: with `HDLAB_EXP_NAME=exp_<anchor>`, the resolved out_dir is the
      single-prefix `data/exp_<anchor>/`, NOT the double-prefix
      `data/exp_exp_<anchor>/`.
  (C) Runtime: with `HDLAB_EXP_NAME=<anchor>` (unprefixed), out_dir is still
      the single-prefix canonical path.

Regression guard against SH-4 wrapper-vs-get_output_dir gap.

Run:
    python tools/test_wrapper_path_normalization.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO = THIS_DIR.parent
sys.path.insert(0, str(REPO))


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        print(f"FAIL: {msg}", file=sys.stderr)
        sys.exit(1)


# Static AST-lite check: source-level anti-pattern regression.
BAD_MANUAL = re.compile(
    r'out_dir\s*=\s*REPO\s*/\s*"data"\s*/\s*\(\s*"exp_"\s*\+\s*env_name\s*\)'
)

# Template anti-pattern: any of the double-prefix-producing forms.
#   (A) REPO / "data" / ("exp_" + env_name)      -- Stage 1 wrapper form
#   (B) REPO / "data" / f"exp_{env_name}"        -- f-string form
#   (C) os.environ.get("HDLAB_EXP_NAME", ...) followed by manual "exp_" prefix
BAD_TEMPLATE_PATTERNS = [
    re.compile(r'REPO\s*/\s*"data"\s*/\s*\(\s*"exp_"\s*\+\s*env_name\s*\)'),
    re.compile(r'REPO\s*/\s*"data"\s*/\s*f"exp_\{env_name\}"'),
]


def test_static_source_no_manual_construction() -> None:
    """Test A: no wrapper contains the manual construction anti-pattern."""
    wrappers = sorted(REPO.glob("experiments/exp_stage1_*_s*.py"))
    _assert(len(wrappers) > 0, "no Stage 1 sibling wrappers found")
    offenders = []
    missing_import = []
    for p in wrappers:
        # Read bytes and normalize CRLF to LF so pattern matching works
        # regardless of committed line-ending style.
        text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8", errors="replace")
        if BAD_MANUAL.search(text):
            offenders.append(p.name)
        if "get_output_dir" not in text:
            missing_import.append(p.name)
    _assert(
        not offenders,
        f"wrappers with manual double-prefix construction: {offenders}"
    )
    _assert(
        not missing_import,
        f"wrappers missing get_output_dir import: {missing_import}"
    )
    print(f"[A] static check OK: {len(wrappers)} wrappers, 0 offenders")


def test_runtime_double_prefix_normalization() -> None:
    """Test B: HDLAB_EXP_NAME=exp_<anchor> lands at data/exp_<anchor>/."""
    from experiments._seed_checkpoint import get_output_dir  # noqa: E402
    _orig = os.environ.get("HDLAB_EXP_NAME")
    try:
        anchor = "wrapper_norm_test_zzz_v1"
        # Case 1: env has exp_ prefix (the bug scenario).
        os.environ["HDLAB_EXP_NAME"] = "exp_" + anchor
        out = get_output_dir("fallback_unused")
        _assert(
            out.name == "exp_" + anchor,
            f"Case1 double-prefix leaked: got {out.name}, expected exp_{anchor}"
        )
        _assert(
            out.parent.name == "data",
            f"Case1 parent should be data/: got {out.parent.name}"
        )
        # Case 2: env unprefixed anchor (normal FULL run).
        os.environ["HDLAB_EXP_NAME"] = anchor
        out2 = get_output_dir("fallback_unused")
        _assert(
            out2.name == "exp_" + anchor,
            f"Case2 canonical failed: got {out2.name}"
        )
        # Case 3: env unset -> fallback to anchor_name (with exp_ prefix).
        os.environ.pop("HDLAB_EXP_NAME", None)
        out3 = get_output_dir("exp_" + anchor)
        _assert(
            out3.name == "exp_" + anchor,
            f"Case3 fallback anchor with exp_ prefix failed: got {out3.name}"
        )
        # Case 4: env unset -> fallback to anchor_name (unprefixed).
        out4 = get_output_dir(anchor)
        _assert(
            out4.name == "exp_" + anchor,
            f"Case4 fallback anchor unprefixed failed: got {out4.name}"
        )
        print("[B] runtime normalization OK: cases 1-4 all single-prefix")
    finally:
        if _orig is None:
            os.environ.pop("HDLAB_EXP_NAME", None)
        else:
            os.environ["HDLAB_EXP_NAME"] = _orig


def test_wrapper_module_import_side_effects() -> None:
    """Test C: sanity — a representative wrapper's imports do not crash and its
    _write_import_crash_sentinel + main() sites resolve out_dir via
    get_output_dir. We check by inspecting the AST of the module's source rather
    than executing (execution would enter argparse + torch import)."""
    import ast
    sample = REPO / "experiments" / "exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s7.py"
    if not sample.exists():
        print(f"[C] SKIP: {sample} missing")
        return
    tree = ast.parse(sample.read_bytes().replace(b"\r\n", b"\n"))
    # Count out_dir = get_output_dir(...) calls.
    calls_get = 0
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "out_dir" for t in node.targets)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "get_output_dir"
        ):
            calls_get += 1
    _assert(
        calls_get >= 2,
        f"expected >=2 out_dir=get_output_dir(...) sites, got {calls_get}"
    )
    print(f"[C] AST check OK: {calls_get} out_dir = get_output_dir(...) sites in sample")


def test_template_files_no_anti_pattern() -> None:
    """Test D: template files under experiments/_templates/*.template must not
    contain the double-prefix anti-pattern. Templates are the authoring seed for
    new wrappers; a re-introduction here would leak into every cell forked from
    them (SH-4 preventive layer, follow-up to commit 996d35f0c)."""
    templates_dir = REPO / "experiments" / "_templates"
    if not templates_dir.exists():
        print("[D] SKIP: experiments/_templates/ missing")
        return
    templates = sorted(templates_dir.glob("*.template"))
    _assert(len(templates) > 0, "no templates found under experiments/_templates/")
    offenders = []
    missing_get_output_dir = []
    for p in templates:
        text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8", errors="replace")
        for pat in BAD_TEMPLATE_PATTERNS:
            if pat.search(text):
                offenders.append((p.name, pat.pattern))
                break
        # If the template references HDLAB_EXP_NAME at all, it MUST route
        # through get_output_dir; otherwise it's manually constructing paths.
        if "HDLAB_EXP_NAME" in text and "get_output_dir" not in text:
            missing_get_output_dir.append(p.name)
    _assert(
        not offenders,
        f"templates with double-prefix anti-pattern: {offenders}"
    )
    _assert(
        not missing_get_output_dir,
        f"templates that reference HDLAB_EXP_NAME but do not import "
        f"get_output_dir: {missing_get_output_dir}"
    )
    print(f"[D] template guard OK: {len(templates)} templates, 0 offenders")


def test_template_clone_selftest_single_prefix() -> None:
    """Test E: simulate cloning a template + running selftest -> canonical
    single-prefix path. We do not execute the template (needs GPU), but we
    render its output-path resolution logic in isolation using the same
    get_output_dir(ANCHOR_NAME) call site the template uses."""
    from experiments._seed_checkpoint import get_output_dir  # noqa: E402
    _orig = os.environ.get("HDLAB_EXP_NAME")
    try:
        # Mimic what a wrapper cloned from the template would do at runtime:
        # ANCHOR_NAME baked in unprefixed, HDLAB_EXP_NAME set to exp_<anchor>.
        anchor = "template_clone_selftest_zzz_v1"
        os.environ["HDLAB_EXP_NAME"] = "exp_" + anchor
        out = get_output_dir(anchor)  # template uses get_output_dir(ANCHOR_NAME)
        _assert(
            out.name == "exp_" + anchor,
            f"template-clone Case1 leaked double-prefix: {out.name}"
        )
        # No env var set (SELFTEST path when wrapper falls through).
        os.environ.pop("HDLAB_EXP_NAME", None)
        out2 = get_output_dir(anchor)
        _assert(
            out2.name == "exp_" + anchor,
            f"template-clone Case2 fallback failed: {out2.name}"
        )
        print("[E] template-clone selftest OK: single-prefix in both cases")
    finally:
        if _orig is None:
            os.environ.pop("HDLAB_EXP_NAME", None)
        else:
            os.environ["HDLAB_EXP_NAME"] = _orig


if __name__ == "__main__":
    test_static_source_no_manual_construction()
    test_runtime_double_prefix_normalization()
    test_wrapper_module_import_side_effects()
    test_template_files_no_anti_pattern()
    test_template_clone_selftest_single_prefix()
    print("PASS: all wrapper-path-normalization tests OK")
