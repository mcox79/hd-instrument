"""The strategy/solver hand-off, enforced where it cannot be skipped: the certification suite.

WHAT THIS GUARDS, AND WHY IT IS A TEST RATHER THAN A HABIT

Two failure modes, both of which this project has already paid for in other costumes:

  1. A `SOLVED.md` that asserts success WITHOUT a floor or controls. The base rate here is 30 vetted
     HARD_PASS, 1 upheld -- so an unevidenced claim is the expected case, not the exceptional one.
     `tools/problem_ledger.py` refuses one; this test makes the refusal fire on `main`.

  2. A `PROBLEM.md` handed over MISSING its guard sections. The brief format is not decoration --
     "VERIFY BEFORE YOU START" is what stops a solver acting on a stale number, and "ALREADY TRIED"
     is what stops them re-running a landed negative. A brief without them looks complete and is
     the dangerous kind of incomplete. Measured cost of the second failure on this project: 7
     proposals in one night that were already answered on disk.

WHAT IT DELIBERATELY DOES *NOT* FAIL ON: a `SOLVED.md` that is well-formed but not yet integrated.
That is a normal state -- a solver finished and the strategy session has not folded it in yet -- and
failing `main` for it would train everyone to ignore this test. A guard that flags everything gets
ignored; that lesson is written into `rank_with_ties.py` and it applies here.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.problem_ledger import scan, parse_frontmatter  # noqa: E402

PROBLEMS_DIR = os.path.join(REPO_ROOT, "notes", "problems")

# The eight sections every brief carries, per notes/problems/README.md. These headings are an API
# between the README and this test: if the README's format changes, change this list in the same
# commit (a doc parsed by code is coupled to it).
REQUIRED_BRIEF_SECTIONS = (
    "THE PROBLEM IN PLAIN LANGUAGE",
    "WHY THIS ONE",
    "MEASURED vs INFERRED",
    "ALREADY TRIED",
    "VERIFY BEFORE YOU START",
    "THE BAR",
    "FILES AND ENTRY POINTS",
    "DO NOT QUOTE",
)


def test_no_solved_flag_is_malformed():
    """A claim of success must carry its bar, result, floor, controls and a reverify command."""
    bad = [r for r in scan() if r["state"] == "MALFORMED"]
    assert not bad, (
        "malformed SOLVED.md flag(s) -- a claim without evidence is not a flag:\n"
        + "\n".join(f"  {r['slug']}: {r['error']}" for r in bad))


def test_every_problem_folder_has_a_brief():
    bad = [r for r in scan() if r["state"] == "NO_BRIEF"]
    assert not bad, ("problem folder(s) with no PROBLEM.md: "
                     + ", ".join(r["slug"] for r in bad))


def test_every_brief_carries_its_guard_sections():
    """A brief missing VERIFY-BEFORE-YOU-START or ALREADY-TRIED looks complete and is not."""
    problems = [d for d in sorted(os.listdir(PROBLEMS_DIR))
                if os.path.isdir(os.path.join(PROBLEMS_DIR, d))]
    assert problems, "no problem folders found -- has the directory moved?"
    failures = []
    for slug in problems:
        path = os.path.join(PROBLEMS_DIR, slug, "PROBLEM.md")
        if not os.path.exists(path):
            continue  # covered by the test above
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        missing = [s for s in REQUIRED_BRIEF_SECTIONS if s not in text]
        if missing:
            failures.append(f"  {slug}: missing {missing}")
    assert not failures, (
        "brief(s) missing required guard sections (see notes/problems/README.md):\n"
        + "\n".join(failures))


def test_the_guard_can_actually_fire():
    """POSITIVE CONTROL. A guard nobody has seen fire is a guard nobody has tested.

    Builds the exact failure this exists to catch -- a confident SOLVED.md with NO FLOOR -- and
    asserts the scanner refuses it. Runs in a tempdir, so it cannot touch the real folders.
    """
    import tempfile

    claim = ("---\nproblem: demo\nstatus: SOLVED\nbar: beat the floor\n"
             "result: 0.91, n=500, held-out\n"
             "controls: scramble removed 40 of 500\n"
             "files_changed: hdlab/x.py\nreverify: python tools/x.py\n---\nlooks convincing\n")
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "demo")
        os.makedirs(d)
        open(os.path.join(d, "PROBLEM.md"), "w", encoding="utf-8").write("brief")
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(claim)
        row = scan(td)[0]
        assert row["state"] == "MALFORMED" and "floor" in (row["error"] or ""), (
            f"the guard did NOT fire on a SOLVED.md with no floor: {row}")

        # NEGATIVE CONTROL: a complete flag must NOT be flagged, or the guard cries wolf.
        ok = claim.replace("controls:", "floor: majority 0.6389\ncontrols:")
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(ok)
        assert scan(td)[0]["state"] == "SOLVED", "a complete flag was wrongly refused"


def test_frontmatter_parser_rejects_near_misses():
    """A nearly-right block is the dangerous one -- it reads as compliant at a glance."""
    _, err = parse_frontmatter("no fence at all\n")
    assert err and "fence" in err
    _, err = parse_frontmatter("---\nproblem: x\n")          # never closed
    assert err and "never closed" in err
    _, err = parse_frontmatter("---\nproblem x\n---\n")      # not key: value
    assert err and "key: value" in err


def test_every_open_problem_is_ranked():
    """The owner reads the problems tab to decide what to do next; an unranked row is a row that
    cannot be acted on.

    Owner, 2026-08-22: *"I also want a priority for what problems to tackle first, on the problem
    page"*. The priority lives in `PROBLEM.md` frontmatter because that is what
    `problem_ledger.scan()` reads and the GUI renders -- prose at the top of the brief was written
    first, and the owner saw none of it.
    """
    unranked = [r["slug"] for r in scan()
                if r["state"] == "OPEN" and r.get("priority") is None]
    assert not unranked, ("open problem(s) with no priority in PROBLEM.md frontmatter: "
                          + ", ".join(unranked))


def test_priorities_are_unique_and_the_ranking_is_readable():
    """Two problems sharing rank 3 is not a ranking. Also fails if the parse silently returns
    nothing, which would make the test above pass VACUOUSLY."""
    ranked = [(r["priority"], r["slug"]) for r in scan() if r.get("priority") is not None]
    assert len(ranked) >= 3, ("only %d ranked problems found -- if the frontmatter parse broke, "
                              "the unranked test above would pass on an empty set" % len(ranked))
    pris = [p for p, _ in ranked]
    dupes = {p for p in pris if pris.count(p) > 1}
    assert not dupes, "duplicate priorities %s in %s" % (sorted(dupes), sorted(ranked))


def test_no_brief_carries_a_broken_annotation():
    """A malformed priority must be reported, never silently dropped -- otherwise a typo removes a
    problem from the ranking and nothing says so."""
    bad = [(r["slug"], r["meta_error"]) for r in scan() if r.get("meta_error")]
    assert not bad, "brief frontmatter error(s): " + "; ".join("%s: %s" % b for b in bad)


if __name__ == "__main__":
    test_no_solved_flag_is_malformed()
    print("[CHECK flags] no malformed SOLVED.md")
    test_every_problem_folder_has_a_brief()
    print("[CHECK briefs] every problem folder has a PROBLEM.md")
    test_every_brief_carries_its_guard_sections()
    print("[CHECK sections] every brief carries its guard sections")
    test_the_guard_can_actually_fire()
    print("[CHECK positive_control] the guard fires on a no-floor claim and spares a complete one")
    test_frontmatter_parser_rejects_near_misses()
    print("[CHECK near_miss] near-miss frontmatter is rejected")
    print("[ALL CHECKS PASS] the strategy/solver hand-off is enforced on main.")
