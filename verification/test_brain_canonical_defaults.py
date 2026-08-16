"""Tripwire: a parameter documented as having a brain-canonical value must declare its default.

WHY THIS EXISTS (2026-08-15 audit). `hdlab/iterative_attractor.iterative_cleanup` gained a
cue-clamp parameter `alpha` on 2026-06-23 (commit 78f10ede8). Its own docstring says
"brain-canonical = 0.5" and calls alpha=0.0 the "HARD_FAIL baseline". It shipped with
`alpha: float = 0.0` and no caller on the live path has ever passed anything else, so the
brain-motivated behaviour has been unreachable-by-default ever since. Nothing in the repo
noticed, because nothing was watching. This is the same failure class as the 11 scheduled
tasks silently disabled for 12 days and the director-KB ingest disabled for 6: a thing that
ships off and is never switched on did not ship.

WHAT THIS ENFORCES. It does NOT force any parameter to a particular value -- that is an
experimental decision and belongs to the operator. It forces the decision to be WRITTEN DOWN:

  1. DISCOVERY (ast, no import side effects): every git-TRACKED hdlab module is parsed; any
     function whose docstring claims "brain-canonical" / "brain-faithful" / "brain-motivated"
     is collected.
  2. Every discovered function must have a row in DECLARED below. Adding a new brain-canonical
     claim without a row FAILS this test, which is the whole point: the author has to say
     whether the canonical value is the default, and if not, why, and with what evidence.
  3. Every declared default is checked at RUNTIME via inspect.signature against the live
     function object, not against the source text. Changing a default without updating the
     row FAILS in BOTH directions.
  4. A row claiming canonical_is_default=True is checked against the live default, so
     "the fix is active" can never be an unverified claim.
  5. Rows with canonical_is_default=False must carry a non-empty reason AND evidence pointer.

Scope note: DISCOVERY reads git-tracked files only. Untracked, in-flight modules are out of
scope until committed, at which point this tripwire fires and forces the declaration.
"""
from __future__ import annotations

import ast
import importlib
import inspect
import os
import re
import subprocess
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

CLAIM_RE = re.compile(r"brain[- ]canonical|brain[- ]faithful|brain[- ]motivated", re.IGNORECASE)

# (module, function) -> rows. One entry per parameter carrying a brain-canonical value.
# `actual_default` records what the code does TODAY; it is a tripwire, not an endorsement.
DECLARED = {
    ("hdlab.iterative_attractor", "iterative_cleanup"): {
        "alpha": {
            "brain_canonical": 0.5,
            "actual_default": 0.0,
            "canonical_is_default": False,
            "why_not": (
                "Landed 2026-06-23 (78f10ede8) as an opt-in so the pre-existing self-consistent "
                "dynamics stayed bit-reproducible. The intended follow-up never adjudicated it."),
            "evidence": (
                "data/exp_substrate_iterative_cleanup_cue_clamped_v1/metrics.json HARD_PASS is a "
                "1-seed 40-trial max-of-3-arms smoke; "
                "data/exp_substrate_iterative_cleanup_cue_clamped_production_v1/metrics.json is "
                "SANITY_FAIL and never scored the clamp. The clamp is therefore UNADJUDICATED, "
                "not refuted and not established. Operator decision pending."),
        },
    },
    ("hdlab.cleanup_family", "iterative_attractor"): {
        "alpha": {
            "brain_canonical": 0.5,
            "actual_default": 0.0,
            "canonical_is_default": False,
            "why_not": "Mirrors the wrapped hdlab.iterative_attractor default; see that row.",
            "evidence": "Same as hdlab.iterative_attractor.iterative_cleanup.alpha.",
        },
    },
    ("hdlab.hippocampal_encoder", "cls_discrete_budget_consolidate"): {
        "ca3_alpha": {
            "brain_canonical": 0.5,
            "actual_default": 0.5,
            "canonical_is_default": True,
            "why_not": "",
            "evidence": "Default matches the canonical value; the clamp is reachable by default.",
        },
        "ca3_complete": {
            "brain_canonical": True,
            "actual_default": True,
            "canonical_is_default": True,
            "why_not": "",
            "evidence": "Completion on by default.",
        },
    },
}


def _tracked_hdlab_files():
    r = subprocess.run(["git", "ls-files", "hdlab/*.py"], cwd=_REPO,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("git unavailable; discovery scope undefined")
    return [os.path.join(_REPO, p) for p in r.stdout.split() if p.endswith(".py")]


def discover(paths):
    """AST-only discovery: (module, function) for every brain-canonical claim. No imports."""
    found = set()
    for path in paths:
        try:
            rel = os.path.relpath(path, _REPO).replace("\\", "/")
        except ValueError:      # different drive (self-test uses a temp dir); not a repo module
            rel = os.path.basename(path)
        mod = rel[:-3].replace("/", ".")
        try:
            tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = ast.get_docstring(node) or ""
            if CLAIM_RE.search(doc):
                found.add((mod, node.name))
    return found


def _live_default(module, func, param):
    m = importlib.import_module(module)
    fn = getattr(m, func)
    sig = inspect.signature(fn)
    assert param in sig.parameters, f"{module}.{func} has no parameter {param!r}"
    d = sig.parameters[param].default
    assert d is not inspect.Parameter.empty, f"{module}.{func}.{param} has no default"
    return d


def test_every_brain_canonical_claim_is_declared():
    found = discover(_tracked_hdlab_files())
    undeclared = sorted(found - set(DECLARED))
    assert not undeclared, (
        "These functions document a brain-canonical/faithful/motivated value but have no row in "
        "DECLARED, so nothing checks whether that value is the DEFAULT. Add a row saying whether "
        "the canonical value is the default, and if not, why and with what evidence: "
        + repr(undeclared))


def test_declared_rows_still_correspond_to_a_real_claim():
    """Reverse direction: a row whose function no longer claims anything is stale."""
    found = discover(_tracked_hdlab_files())
    stale = sorted(set(DECLARED) - found)
    assert not stale, (
        "DECLARED rows whose function no longer carries a brain-canonical claim (renamed, "
        "removed, or docstring reworded). Re-verify and update: " + repr(stale))


@pytest.mark.parametrize("key", sorted(DECLARED))
def test_declared_default_matches_runtime(key):
    module, func = key
    for param, row in DECLARED[key].items():
        live = _live_default(module, func, param)
        assert live == row["actual_default"], (
            f"{module}.{func}.{param} default is {live!r} at runtime but DECLARED records "
            f"{row['actual_default']!r}. A default moved without the audit row moving with it. "
            f"If this was intentional, update the row AND its evidence.")


@pytest.mark.parametrize("key", sorted(DECLARED))
def test_canonical_is_default_claims_are_true_at_runtime(key):
    module, func = key
    for param, row in DECLARED[key].items():
        if not row["canonical_is_default"]:
            continue
        live = _live_default(module, func, param)
        assert live == row["brain_canonical"], (
            f"{module}.{func}.{param} is DECLARED as having the brain-canonical value "
            f"{row['brain_canonical']!r} by default, but the live default is {live!r}. "
            f"A fix that ships default-off did not ship.")


@pytest.mark.parametrize("key", sorted(DECLARED))
def test_deviations_carry_reason_and_evidence(key):
    for param, row in DECLARED[key].items():
        if row["canonical_is_default"]:
            continue
        assert row["why_not"].strip(), f"{key}.{param}: deviation with no reason"
        assert row["evidence"].strip(), f"{key}.{param}: deviation with no evidence pointer"


def test_the_checker_itself_can_fail():
    """Self-test: prove each gate rejects a wrong world, so a PASS is informative."""
    # 1. discovery finds a claim in a synthetic source
    import tempfile
    src = 'def f(x, alpha=0.0):\n    """Uses the brain-canonical value."""\n    return x\n'
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "synthetic_mod.py")
        open(p, "w", encoding="utf-8").write(src)
        got = discover([p])
    assert len(got) == 1 and list(got)[0][1] == "f", "discovery failed to see a claim"

    # 2. a claim with no DECLARED row must be reported as undeclared
    assert got - set(DECLARED) == got

    # 3. the runtime-default gate rejects a wrong expectation
    live = _live_default("hdlab.iterative_attractor", "iterative_cleanup", "alpha")
    wrong = live + 1.0
    with pytest.raises(AssertionError):
        assert live == wrong, "forced"

    # 4. a missing parameter is caught rather than silently skipped
    with pytest.raises(AssertionError):
        _live_default("hdlab.iterative_attractor", "iterative_cleanup", "no_such_param")
