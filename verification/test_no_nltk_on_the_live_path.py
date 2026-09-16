#!/usr/bin/env python3
"""test_no_nltk_on_the_live_path -- the certification gate for priority 127.

THE CLAIM UNDER TEST: no external library is in the call chain of a read. Two halves, because either one
alone is cheatable:

  STATIC   every import statement under hdlab/ is parsed (AST, not a grep for the word "nltk": a mention in a
           comment is not an import, and a grep cannot tell them apart). The ONLY nltk import allowed in the
           package is the one inside `hdlab.lexicon_foundation.standin_nltk`, which is closed by default and
           exists so the two retired MODEL stand-ins (the NLTK perceptron tagger, the Porter stemmer) stay
           reproducible as deliberate baselines.
  DYNAMIC  a real read runs with `nltk` POISONED -- any import of it raises -- and must complete. This is the
           half that cannot be satisfied by tidy source: a surviving library call is a crash, not a warning.
           The CONTROL for it is in the cell (`--identity`): the SHIPPED tree under the same poison DOES crash,
           which is what proves the poison bites rather than the test being vacuous.

Plus the two properties that make the freeze honest rather than merely quiet:
  LOUD     a missing asset RAISES (LexiconAssetMissing). The defect this problem removes is a missing corpus
           silently degrading a read -- so the replacement must never silently degrade either.
  GATED    `standin_nltk` refuses by default; a stand-in can only be selected deliberately.

BEFORE THE PATCH LANDS this witness verifies the PROPOSED tree (the patched copy the cell builds under
data/exp_lexicon_foundation_parity_v1/patched_tree) and says so; after strategy applies
notes/problems/<slug>/lexicon_foundation_patch.diff the same file verifies hdlab/ itself with no edit. If
neither tree is clean it FAILS -- it never skips.

Run: .venv/Scripts/python.exe verification/test_no_nltk_on_the_live_path.py
"""
from __future__ import annotations
import ast
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

LIVE_HDLAB = os.path.join(_REPO, "hdlab")
PATCHED_HDLAB = os.path.join(_REPO, "data", "exp_lexicon_foundation_parity_v1", "patched_tree", "hdlab")
ALLOWED_FILE = "lexicon_foundation.py"          # the ONE gated route, and only inside standin_nltk()


def nltk_imports(tree_dir):
    """[(file, lineno, statement)] for every nltk import statement in a package directory, recursively."""
    hits = []
    for root, _dirs, files in os.walk(tree_dir):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            for node in ast.walk(ast.parse(src, filename=path)):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        if a.name == "nltk" or a.name.startswith("nltk."):
                            hits.append((os.path.relpath(path, tree_dir), node.lineno, "import " + a.name))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and (node.module == "nltk" or node.module.startswith("nltk.")):
                        hits.append((os.path.relpath(path, tree_dir), node.lineno,
                                     "from %s import ..." % node.module))
    return hits


def gated_only(hits):
    """True when every remaining import sits in lexicon_foundation.py (the gated stand-in route)."""
    return all(os.path.basename(f) == ALLOWED_FILE for f, _l, _s in hits)


def pick_tree():
    live = nltk_imports(LIVE_HDLAB)
    if gated_only(live):
        return LIVE_HDLAB, live, "LIVE hdlab/ (patch landed)"
    if os.path.isdir(PATCHED_HDLAB):
        pat = nltk_imports(PATCHED_HDLAB)
        return PATCHED_HDLAB, pat, ("PROPOSED tree (patch NOT landed: hdlab/ still has %d nltk import "
                                    "statements in %d files)" % (len(live), len({f for f, _l, _s in live})))
    return LIVE_HDLAB, live, "LIVE hdlab/ (no proposed tree on disk)"


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    # ---------------------------------------------------------------- STATIC
    tree, hits, provenance = pick_tree()
    print("[witness] tree under test: %s" % provenance)
    chk("no ungated nltk import statement in the package", gated_only(hits),
        "" if gated_only(hits) else str([h for h in hits if os.path.basename(h[0]) != ALLOWED_FILE][:8]))
    # the allowed ones must really be inside standin_nltk, not anywhere in that file
    lf = os.path.join(tree, ALLOWED_FILE)
    inside = True
    if os.path.exists(lf):
        src = open(lf, encoding="utf-8").read()
        fns = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)]
        allowed_ranges = [(n.lineno, max(getattr(c, "lineno", n.lineno) for c in ast.walk(n)))
                          for n in fns if n.name == "standin_nltk"]
        for f, line, _s in hits:
            if os.path.basename(f) != ALLOWED_FILE:
                continue
            inside = inside and any(a <= line <= b for a, b in allowed_ranges)
    chk("the gated imports sit inside standin_nltk() only", inside)

    # ---------------------------------------------------------------- the organ's own asset
    from hdlab import lexicon_foundation as LF
    m = LF.asset_meta()
    chk("frozen asset present and complete", int(m.get("n_synsets", 0)) == 117659
        and int(m.get("n_vn_classes", 0)) > 0 and int(m.get("n_fn_frames", 0)) > 0,
        "synsets=%s vn=%s fn=%s wordnet=%s" % (m.get("n_synsets"), m.get("n_vn_classes"),
                                               m.get("n_fn_frames"), m.get("wordnet_version")))
    chk("organ self-test (addresses, relations, frames, lists)", LF._self_test())

    # ---------------------------------------------------------------- LOUD, not silent
    loud = False
    try:
        LF._Store(os.path.join(_REPO, "data", "frontend_assets", "__absent_lexicon__.sqlite")).con()
    except LF.LexiconAssetMissing:
        loud = True
    chk("a MISSING asset raises instead of degrading", loud)

    gate_closed = False
    try:
        LF.standin_nltk("nltk.tag", "PerceptronTagger", reason="witness")
    except RuntimeError:
        gate_closed = True
    chk("the stand-in gate is closed by default", gate_closed and not LF.STANDIN_ALLOWED)

    # ---------------------------------------------------------------- DYNAMIC (poisoned read)
    n_docs = int(os.environ.get("HDLAB_WITNESS_DOCS", "1"))
    patched = None if tree == LIVE_HDLAB else os.path.dirname(tree)
    import experiments.exp_lexicon_foundation_parity_v1 as E
    docs = E._gum_docs(16)                                   # the modern 16-doc harness; take the cheapest
    prepared = E._prepare(docs, os.path.join(E.OUT_DIR, "conll"))
    order = sorted(prepared, key=lambda dp: os.path.getsize(dp[1]))
    paths = [p for (_d, p) in order[:n_docs]]
    run = E._run_subprocess(paths, patched=patched, poison=True, tag="witness_poisoned")
    got = run["result"] or []
    chk("a real read COMPLETES with every nltk import poisoned",
        run["rc"] == 0 and len(got) == len(paths),
        "rc=%s docs=%d%s" % (run["rc"], len(got), "" if run["rc"] == 0 else "\n" + run["tail"][-1500:]))
    chk("that read imported no nltk at all", "nltk imported: False" in (run["tail"] or ""),
        [l for l in (run["tail"] or "").split("\n") if "ORGAN IN USE" in l][:1])

    print("[witness] %s" % ("ALL CHECKS PASSED" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
