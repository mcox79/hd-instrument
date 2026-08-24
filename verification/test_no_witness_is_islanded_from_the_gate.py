"""A file named test_*.py that defines no test_ function is INVISIBLE to the certification gate.

WHY THIS EXISTS. On 2026-08-23 I wrote four witnesses, ran each by hand, saw them pass, and
committed them. Then I ran the certification suite and found pytest collects ZERO tests from any of
them: they were named `test_*.py` and sat in `verification/`, so they LOOKED certified, but they
define only `main()` and are executed by nothing.

Enumerating the whole directory rather than stopping at my own four:

    94 test_*.py files in verification/
    73 the gate collects tests from
    21 define no test function -- of which:
        3 still ASSERT AT IMPORT, so a failure surfaces as a collection ERROR (covered, loudly)
       18 are TRULY SILENT: every check sits in a main() nothing calls

🔴 CORRECTED WITHIN THE HOUR: I first wrote all 21 as "the gate runs NOTHING from them". That
over-stated by three, and I found it by MEASURING rather than reasoning -- two temp files, one
failing at module level and one failing only inside main():

    module-level assert fails  ->  pytest exit 2, "1 error"      the gate CATCHES it
    failure only inside main() ->  pytest exit 5, "no tests ran"  completely SILENT

That is the difference that matters, and it is why the baseline below is split in two.

**AND THIS REACHES THE RE-VERIFY WITNESSES FOR FIVE SOLVER SUBMISSIONS -- but not all the same way,
so state it exactly:** `..._reader_sense_selection_bayesian_hub`,
`..._recognition_store_calibrated_familiarity_recollection` and `..._grow_by_reading_trivial_floor`
assert at import, so the gate WOULD catch a failure (as an error, not a test).
🔻 **`..._c3_bundling_is_not_the_bottleneck` and `..._learn_from_reading_strong_arm` are TRULY
SILENT** -- two solver submissions whose re-verify the gate does not run at all. Both pass by hand;
neither is certified. *A witness the gate does not run is a witness nobody runs.*

This is the SILENT twin of a hazard `run_certification.py` already documents in its own comment: a
script-style file under a `test_` name that raises SystemExit at import ABORTS the whole suite,
loudly, and once cost this project two days of a false PASS. The version here does the opposite --
it is skipped without a word.

WHAT THIS TEST DOES, AND WHY IT IS A RATCHET RATHER THAN A CLEANUP. Failing outright on all 21
would turn the gate red for a pre-existing condition, which is how a useful check gets disabled.
Instead it pins the KNOWN set: any NEW islanded file fails immediately, and removing one from the
baseline is a one-line edit that can only ever make the suite stricter.

**TO FIX AN ISLANDED WITNESS: give it a `def test_<name>()` that calls its `main()` and asserts the
exit code is 0.** For a witness too slow for the gate (real corpus reads, minutes), say so in the
file and leave it in the baseline below with `# SLOW` -- an absence that is a decision must read as
one, and this list is where that decision is recorded.

    .venv/Scripts/python.exe -m pytest verification/test_no_witness_is_islanded_from_the_gate.py -q
"""
import ast
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Files with NO test function whose checks DO run at import (module-level asserts). A failure in
# these surfaces as a pytest collection ERROR, so the gate does catch them -- they simply contribute
# 0 to the test count. Listed separately because calling them "islanded" was wrong.
CHECKED_AT_IMPORT = {
    "test_grow_by_reading_trivial_floor.py",
    "test_reader_sense_selection_bayesian_hub.py",
    "test_recognition_store_calibrated_familiarity_recollection.py",
}

# TRULY SILENT as measured 2026-08-23: no test function AND no import-time assert, so pytest reports
# "no tests ran" and the gate is none the wiser. THIS LIST MAY SHRINK, NEVER GROW.
# SLOW = real corpus reads / long computation, deliberately kept out while run_certification.py is
# itself timing out (see the certification_gate_hangs brief).
KNOWN_ISLANDED = {
    "test_board_archive_and_reading_pane.py",
    "test_c3_bundling_is_not_the_bottleneck.py",                    # SLOW ~13 min
    "test_definiens_head_light_nouns.py",
    "test_does_an_addressed_slot_survive_bundling.py",
    "test_does_our_format_survive_the_meaning_signal.py",
    "test_does_sparsity_fix_the_bundling_loss.py",
    "test_gui_does_not_freeze_the_ui_thread.py",
    "test_gui_stale_banner.py",
    "test_hypernym_matcher_positive_control.py",
    "test_learn_from_reading_strong_arm.py",                        # SLOW, builds a PPMI model
    "test_segregated_beats_superposed_at_equal_budget.py",
    "test_sensorimotor_covers_the_verb_hole.py",
    "test_source_trust_vet_has_a_trivial_floor.py",
    "test_the_100k_noise_sweep_bites_and_the_system_survives_it.py",
    "test_the_channel_cannot_gate_links_alone.py",
    "test_the_familiarity_gate_refuses_most_of_english.py",         # SLOW, 14 corpus reads
    "test_which_number_is_the_meaning_asset.py",
    "test_wordnet_advantage_is_selection_not_meaning.py",
}


def _defines_a_test(path):
    """True if pytest would collect at least one test from this file.

    Parsed with ast, NOT matched with a regex: 'a mention is not a use', and a file that merely
    contains the string 'def test_' in a docstring or comment must not count as covered.
    """
    try:
        tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            return True
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and sub.name.startswith("test"):
                    return True
    return False


def _asserts_at_import(tree):
    """Only an ASSERT counts as a check that runs at import. A top-level sys.path.insert() or
    print() is NOT a check -- counting those was a false positive in my first pass and inflated
    the 'covered' set from 3 to 15."""
    for n in tree.body:
        if isinstance(n, ast.Assert):
            return True
        if isinstance(n, (ast.For, ast.While, ast.With, ast.Try)):
            if any(isinstance(s, ast.Assert) for s in ast.walk(n)):
                return True
        if isinstance(n, ast.If):
            guard = isinstance(n.test, ast.Compare) and getattr(n.test.left, "id", "") == "__name__"
            if not guard and any(isinstance(s, ast.Assert) for s in ast.walk(n)):
                return True
    return False


def _islanded_now():
    """Files the gate would run NOTHING from: no test function AND no import-time assert."""
    out = set()
    for f in os.listdir(HERE):
        if not (f.startswith("test_") and f.endswith(".py")):
            continue
        path = os.path.join(HERE, f)
        try:
            tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
        except SyntaxError:
            continue
        if _defines_a_test(path) or _asserts_at_import(tree):
            continue
        out.add(f)
    return out


def test_no_new_witness_is_islanded():
    """A NEW test_*.py with no test function is a witness the gate silently skips."""
    new = sorted(_islanded_now() - KNOWN_ISLANDED)
    assert not new, (
        "these test_*.py files define no test function, so the certification gate runs NOTHING "
        "from them:\n  " + "\n  ".join(new) +
        "\nGive each a `def test_<name>(): ...` calling its main(), or add it to KNOWN_ISLANDED "
        "with a comment saying why (e.g. too slow for the gate).")


def test_the_baseline_does_not_list_files_that_are_fine_now():
    """The ratchet must tighten. A file that has been fixed has to leave the baseline, or the list
    rots into a permanent excuse and stops meaning anything."""
    stale = sorted(KNOWN_ISLANDED - _islanded_now() - {f for f in KNOWN_ISLANDED
                                                       if not os.path.exists(os.path.join(HERE, f))})
    assert not stale, (
        "these are listed as islanded but now define tests -- remove them from KNOWN_ISLANDED:\n  "
        + "\n  ".join(stale))


def test_the_detector_can_actually_fire():
    """POSITIVE CONTROL. A checker that has never been seen to fire is untested -- and this repo has
    a documented case of a detector whose verification shared its own blind spot."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        good = os.path.join(td, "test_good.py")
        bad = os.path.join(td, "test_bad.py")
        io.open(good, "w", encoding="utf-8").write("def test_x():\n    assert True\n")
        io.open(bad, "w", encoding="utf-8").write(
            '"""def test_looks_like_one_but_is_a_docstring"""\ndef main():\n    pass\n')
        assert _defines_a_test(good) is True, "failed to see a real test function"
        assert _defines_a_test(bad) is False, \
            "counted a 'def test_' inside a docstring as a real test -- a mention is not a use"
