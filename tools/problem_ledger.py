"""The flag between the strategy session and the solver sessions. Refuses a claim without evidence.

WHY THIS IS CODE AND NOT A CONVENTION. This project's meta-rule is 5-for-5: a caution written as
prose gets violated; a control written as code catches something. "Write a SOLVED.md with a floor
and controls in it" is a caution. This is the control.

WHAT IT ENFORCES. A `notes/problems/<slug>/SOLVED.md` is only a flag if it carries a frontmatter
block naming the BAR it cleared, the RESULT with its scorer/n/population, the STRONGEST FLOOR
actually run, the CONTROLS and what each excluded, and a REVERIFY command. A file missing any of
those is reported MALFORMED and does not count as solved -- because the base rate for an unverified
claim here is 30 vetted HARD_PASS, 1 upheld.

IT DOES NOT JUDGE THE SCIENCE. It cannot tell a good floor from a bad one. It guarantees only that
the fields a reviewer needs are PRESENT and non-empty, so that "solved" can never mean "asserted".
The strategy session still re-verifies on disk before integrating.

Usage:
    python tools/problem_ledger.py             # table of every problem and its state
    python tools/problem_ledger.py --check     # exit 1 if anything is malformed or unintegrated
    python tools/problem_ledger.py --self-test
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(REPO_ROOT, "notes", "problems")

REQUIRED = ("problem", "status", "bar", "result", "floor", "controls", "files_changed", "reverify")
VALID_STATUS = ("SOLVED", "PARTIAL", "REFUTED")
# Written by the strategy session when it has re-verified and folded the result into the plan.
INTEGRATED_MARK = "INTEGRATED_BY_STRATEGY"


def parse_frontmatter(text):
    """Return (fields, error). Deliberately strict: a nearly-right block is the dangerous one."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "does not start with a '---' frontmatter fence"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, "frontmatter fence is never closed"
    fields = {}
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            return {}, f"frontmatter line is not 'key: value': {raw.strip()[:60]!r}"
        k, _, v = raw.partition(":")
        fields[k.strip()] = v.strip()
    missing = [k for k in REQUIRED if not fields.get(k)]
    if missing:
        return fields, f"missing or empty required field(s): {', '.join(missing)}"
    if fields["status"] not in VALID_STATUS:
        return fields, f"status {fields['status']!r} not one of {VALID_STATUS}"
    return fields, None


def scan(problems_dir=PROBLEMS_DIR):
    """Enumerate from the filesystem, then reconcile -- never the reverse."""
    rows = []
    if not os.path.isdir(problems_dir):
        return rows
    for slug in sorted(os.listdir(problems_dir)):
        d = os.path.join(problems_dir, slug)
        if not os.path.isdir(d):
            continue
        has_brief = os.path.exists(os.path.join(d, "PROBLEM.md"))
        solved_path = os.path.join(d, "SOLVED.md")
        row = {"slug": slug, "brief": has_brief, "state": "OPEN",
               "error": None, "fields": {}, "integrated": False}
        if not has_brief:
            row["state"], row["error"] = "NO_BRIEF", "folder has no PROBLEM.md"
        if os.path.exists(solved_path):
            with open(solved_path, "r", encoding="utf-8") as f:
                text = f.read()
            fields, err = parse_frontmatter(text)
            row["fields"] = fields
            row["integrated"] = INTEGRATED_MARK in text
            if err:
                row["state"], row["error"] = "MALFORMED", err
            else:
                row["state"] = fields["status"]
                if fields.get("problem") != slug:
                    row["state"] = "MALFORMED"
                    row["error"] = (f"frontmatter problem={fields.get('problem')!r} "
                                    f"does not match folder {slug!r}")
        rows.append(row)
    return rows


def report(rows):
    if not rows:
        return "no problem folders yet (notes/problems/<slug>/PROBLEM.md)"
    out = [f"{len(rows)} problem folder(s):"]
    for r in rows:
        mark = "  " if r["state"] == "OPEN" else ("OK" if r["integrated"] else "->")
        line = f"  {mark} {r['slug']:34s} {r['state']}"
        if r["state"] in VALID_STATUS and not r["integrated"]:
            line += "   <-- AWAITING STRATEGY RE-VERIFY + INTEGRATION"
        if r["error"]:
            line += f"\n        MALFORMED: {r['error']}"
        if r["fields"].get("result"):
            line += f"\n        result: {r['fields']['result'][:100]}"
            line += f"\n        floor : {r['fields'].get('floor','')[:100]}"
        out.append(line)
    awaiting = [r for r in rows if r["state"] in VALID_STATUS and not r["integrated"]]
    bad = [r for r in rows if r["state"] in ("MALFORMED", "NO_BRIEF")]
    out.append("")
    out.append(f"awaiting integration: {len(awaiting)} | malformed/incomplete: {len(bad)}")
    return "\n".join(out)


def self_test():
    import tempfile

    good = ("---\nproblem: demo\nstatus: SOLVED\nbar: beat the first_mention floor\n"
            "result: 0.83 hit@1, n=440, held-out prose\nfloor: first_mention 0.7955\n"
            "controls: scramble excluded 12 of 440; empty-arm scored 0.02\n"
            "files_changed: hdlab/demo.py\nreverify: python tools/demo_check.py\n---\nprose\n")
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "demo")
        os.makedirs(d)
        open(os.path.join(d, "PROBLEM.md"), "w", encoding="utf-8").write("brief")
        # 1. a well-formed flag is recognised
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(good)
        r = scan(td)[0]
        assert r["state"] == "SOLVED" and not r["integrated"], r
        print("[self-test] PASS a complete SOLVED.md is recognised and marked awaiting integration")

        # 2. THE LOAD-BEARING CASE: a confident claim with NO FLOOR must be refused.
        nofloor = good.replace("floor: first_mention 0.7955\n", "")
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(nofloor)
        r = scan(td)[0]
        assert r["state"] == "MALFORMED" and "floor" in r["error"], r
        print("[self-test] PASS a SOLVED.md with no FLOOR is refused (the whole point)")

        # 3. and with no CONTROLS.
        noctl = good.replace("controls: scramble excluded 12 of 440; empty-arm scored 0.02\n", "")
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(noctl)
        assert scan(td)[0]["state"] == "MALFORMED"
        print("[self-test] PASS a SOLVED.md with no CONTROLS is refused")

        # 4. NEGATIVE CONTROL -- a guard that flags everything gets ignored. REFUTED must pass.
        ref = good.replace("status: SOLVED", "status: REFUTED")
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(ref)
        assert scan(td)[0]["state"] == "REFUTED"
        print("[self-test] PASS REFUTED is a first-class accepted outcome, not an error")

        # 5. a slug mismatch is caught -- the copy-paste failure this format invites.
        mism = good.replace("problem: demo", "problem: something_else")
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(mism)
        r = scan(td)[0]
        assert r["state"] == "MALFORMED" and "does not match folder" in r["error"], r
        print("[self-test] PASS a frontmatter/folder slug mismatch is caught")

        # 6. integration mark clears the awaiting flag.
        open(os.path.join(d, "SOLVED.md"), "w", encoding="utf-8").write(good + INTEGRATED_MARK)
        assert scan(td)[0]["integrated"] is True
        print("[self-test] PASS the integration mark clears 'awaiting integration'")

        # 7. an OPEN problem with only a brief is not an error.
        os.remove(os.path.join(d, "SOLVED.md"))
        assert scan(td)[0]["state"] == "OPEN"
        print("[self-test] PASS an open problem is OPEN, not malformed")
    print("[self-test] RESULT: PASS")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    rows = scan()
    print(report(rows))
    if "--check" in sys.argv:
        bad = [r for r in rows if r["state"] in ("MALFORMED", "NO_BRIEF")]
        awaiting = [r for r in rows if r["state"] in VALID_STATUS and not r["integrated"]]
        return 1 if (bad or awaiting) else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
