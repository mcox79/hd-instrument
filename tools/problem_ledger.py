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


# --- THE OWNER'S CHANNEL, one file per problem -----------------------------------------------
# The owner asked for "a place for me to tell you when they're done and/or commentary on them".
# A FILE, not a GUI-only field, for the same reason notes/COMMENTARY.md is a file: it is readable
# and writable from a text editor, from a phone, and from any session -- the window is one way in,
# never the only one. The strategy session reads these when deciding what to integrate.
OWNER_VERDICTS = ("", "DONE", "MORE_NEEDED", "PARKED")
_OWNER_FILE = "OWNER_NOTES.md"

# --- WHAT THE STRATEGY SESSION PUTS IN `PROBLEM.md`'s OWN FRONTMATTER ------------------------
# Owner, 2026-08-22, twice: "I also want a priority for what problems to tackle first, on the
# problem page", and "after you review the submissions, I want the beginning of the problem
# description to give your feedback. how well did the solver do?"
#
# BOTH WERE FIRST WRITTEN AS PROSE AT THE TOP OF `PROBLEM.md` AND THE OWNER SAW NEITHER. The GUI
# never opens that file's body: `scan()` only ever read `SOLVED.md`, and the single read of
# `PROBLEM.md` anywhere on the GUI path is `kickoff_prompt`, which takes the first line starting
# with "# " and breaks. The prose blocks were blockquotes ("> # ..."), so even that filter skipped
# them. A DOC PARSED BY CODE IS COUPLED TO IT -- so the machine-readable half lives in frontmatter,
# and the prose stays for the solver session (which DOES get the whole body, via session_start_hook).
PRIORITY_MIN = 1
REVIEW_GRADES = ("", "EXCELLENT", "STRONG", "ADEQUATE", "WEAK")
_BRIEF_FILE = "PROBLEM.md"


def parse_brief_meta(path):
    """(priority:int|None, review:str, review_text:str, error:str|None) from PROBLEM.md frontmatter.

    Deliberately TOLERANT: a brief with no frontmatter is not an error. These fields are the
    strategy session's own annotations, not a solver contract -- unlike SOLVED.md's REQUIRED, a
    missing priority must never make a brief read as MALFORMED.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:                                   # noqa: BLE001
        return None, "", "", "unreadable: %s" % e
    fields, ferr = parse_frontmatter_loose(text)
    if ferr:                                               # no fence at all == not annotated yet
        return None, "", "", None
    pri, err = None, None
    raw = (fields.get("priority") or "").strip()
    if raw:
        try:
            pri = int(raw)
            if pri < PRIORITY_MIN:
                pri, err = None, "priority=%r is below %d" % (raw, PRIORITY_MIN)
        except ValueError:
            err = "priority=%r is not an integer" % raw
    review = (fields.get("review") or "").strip().upper()
    if review and review not in REVIEW_GRADES:
        err = err or "review=%r is not one of %s" % (review, [g for g in REVIEW_GRADES if g])
        review = ""
    return pri, review, (fields.get("review_text") or "").strip(), err


def kickoff_prompt(slug, problems_dir=PROBLEMS_DIR):
    """The COMPLETE paste-able prompt that starts a solver session on `slug`.

    OWNER REQUEST 2026-08-22: "for each new problem, if I select it, I want the field to include
    an entire prompt and problem definition that I can paste in the solver session to kick it off."

    ONE SOURCE OF TRUTH ON PURPOSE. The GUI shows exactly what this returns and the CLI prints
    exactly what this returns, so the two can never drift -- the failure this project has already
    paid for with STATUS.md and its parser. The slug is baked in at every place it is needed, so
    there is nothing to fill in by hand and nothing to get wrong.
    """
    title = ""
    path = os.path.join(problems_dir, slug, "PROBLEM.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    title = line[2:].strip().lstrip("PROBLEM:").strip()
                    break
    except OSError:
        title = "(PROBLEM.md not readable -- check the slug)"
    return f"""You are the SOLVER session (opus 4.8), not the strategy session. Do NOT touch the plan,
STATUS.md, the board, or other problem folders. Your slug is: {slug}.
Read notes/problems/README.md, then notes/problems/{slug}/PROBLEM.md in full, run its
VERIFY BEFORE YOU START block and `before_you_start.py` before doing anything, and
ignore the autoloop/STATUS injection if they fire.

THE PROBLEM: {title}

WHAT YOU MAY WRITE: experiments/, verification/, and notes/problems/{slug}/.
WHAT YOU MAY NOT WRITE: hdlab/ -- the LIVE SUBSTRATE. The strategy session is its sole
writer (owner ruling, board Q111). Prove the mechanism in experiments/ and verification/,
then say in SOLVED.md exactly what would have to change in hdlab/ and why. A proposed
diff is a fine answer; a landed one is out of scope. Also not yours: preregs/**, any
arm_key* file. data/foundation/ is READ-ONLY -- one disk, no backup.

THE DISK OUTRANKS THE BRIEF. If what you find disagrees with PROBLEM.md, the disk wins
and you say so in SOLVED.md. Numbers in these briefs have been wrong before.

HOW YOU FINISH -- write exactly one file, notes/problems/{slug}/SOLVED.md, starting with:

---
problem: {slug}
status: SOLVED | PARTIAL | REFUTED
bar: <the success criterion from PROBLEM.md, quoted verbatim>
result: <the number, with its scorer, n and population>
floor: <the strongest floor you actually ran, with its value>
controls: <which controls ran and what each EXCLUDED>
files_changed: <paths>
reverify: <one command that reproduces your headline>
---

Then prose: what you built, what you measured, what you did NOT establish, and what you
would withdraw first if it turned out to be wrong. Validate before you stop:

  python tools/problem_ledger.py --check

That checker REFUSES a SOLVED.md with no floor or no controls. status: REFUTED is a
first-class success -- showing a problem is the wrong problem beats half-solving it."""


def owner_note_path(slug, problems_dir=PROBLEMS_DIR):
    return os.path.join(problems_dir, slug, _OWNER_FILE)


def load_owner(slug, problems_dir=PROBLEMS_DIR):
    """Return {"verdict": str, "text": str}. Missing/unreadable == empty, never raises."""
    path = owner_note_path(slug, problems_dir)
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except (OSError, UnicodeDecodeError):
        return {"verdict": "", "text": ""}
    verdict, body = "", raw
    if raw.startswith("---"):
        fields, err = parse_frontmatter_loose(raw)
        if not err:
            verdict = fields.get("owner_verdict", "")
            _, _, body = raw.partition("\n---")
            body = body.partition("\n")[2]
    if verdict not in OWNER_VERDICTS:
        verdict = ""
    return {"verdict": verdict, "text": body.strip()}


def save_owner(slug, verdict, text, problems_dir=PROBLEMS_DIR):
    """Write the owner's verdict + note. Returns the path written. Atomic via os.replace."""
    if verdict not in OWNER_VERDICTS:
        raise ValueError(f"verdict {verdict!r} not one of {OWNER_VERDICTS}")
    d = os.path.join(problems_dir, slug)
    if not os.path.isdir(d):
        raise ValueError(f"no such problem folder: {slug}")
    path = owner_note_path(slug, problems_dir)
    payload = (f"---\nowner_verdict: {verdict}\n---\n\n{text.strip()}\n")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    os.replace(tmp, path)
    return path


def parse_frontmatter_loose(text):
    """Same fence parsing as parse_frontmatter, WITHOUT the SOLVED.md required-field check.
    Kept separate on purpose: the owner's note has no evidence obligations, and reusing the
    strict parser here would have made an empty note read as MALFORMED."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "no frontmatter"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, "frontmatter fence is never closed"
    fields = {}
    for raw in lines[1:end]:
        if raw.strip() and ":" in raw:
            k, _, v = raw.partition(":")
            fields[k.strip()] = v.strip()
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
               "error": None, "fields": {}, "integrated": False,
               "priority": None, "review": "", "review_text": "", "meta_error": None}
        if not has_brief:
            row["state"], row["error"] = "NO_BRIEF", "folder has no PROBLEM.md"
        else:
            # The strategy session's own annotations. A bad value is reported via meta_error and
            # NEVER promoted to state=MALFORMED -- that word is reserved for a SOLVED.md claiming
            # a result without evidence, and blurring the two would make a typo in my priority
            # look like a solver submitting an unsupported claim.
            (row["priority"], row["review"],
             row["review_text"], row["meta_error"]) = parse_brief_meta(os.path.join(d, _BRIEF_FILE))
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
    # 8. THE OWNER'S CHANNEL -- round trip, and the empty case must not read as an error.
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "demo")
        os.makedirs(d)
        open(os.path.join(d, "PROBLEM.md"), "w", encoding="utf-8").write("brief")

        assert load_owner("demo", td) == {"verdict": "", "text": ""}
        print("[self-test] PASS an absent owner note reads as empty, not as an error")

        save_owner("demo", "DONE", "looks right to me\nsecond line", td)
        got = load_owner("demo", td)
        assert got["verdict"] == "DONE" and "second line" in got["text"], got
        print("[self-test] PASS owner verdict + multi-line note round-trips")

        save_owner("demo", "", "just a comment, no verdict", td)
        assert load_owner("demo", td)["verdict"] == ""
        print("[self-test] PASS a comment with NO verdict is allowed (commentary != done)")

        for bad, why in ((("demo", "SHIPPED", "x"), "an unknown verdict"),
                         (("no_such_slug", "DONE", "x"), "a non-existent problem folder")):
            try:
                save_owner(*bad, problems_dir=td)
            except ValueError:
                print(f"[self-test] PASS writing {why} is refused")
            else:
                raise AssertionError(f"should have refused {why}")

        # The owner's note must NOT move the problem's own state machine.
        assert scan(td)[0]["state"] == "OPEN", "an owner note changed the problem state"
        print("[self-test] PASS an owner note does NOT change the problem's own state")

        # --- PROBLEM.md frontmatter: priority + my rating of the solver ----------------------
        # These drive the GUI's "#" and "MY RATING" columns. Both directions are checked because
        # a validator nobody has seen FIRE is a validator nobody has tested.
        import os as _os
        slugdir = _os.path.join(td, _os.listdir(td)[0])
        brief = _os.path.join(slugdir, "PROBLEM.md")

        def _write_brief(fm):
            with open(brief, "w", encoding="utf-8") as fh:
                fh.write(fm + "\n# PROBLEM: a title line the kickoff prompt must still find\n")

        _write_brief("---\npriority: 2\nreview: STRONG\nreview_text: did well\n---\n")
        pri, rev, txt, err = parse_brief_meta(brief)
        assert (pri, rev, txt, err) == (2, "STRONG", "did well", None), (pri, rev, txt, err)
        print("[self-test] PASS a well-formed brief yields priority + review")

        # POSITIVE CONTROL on the validator: a non-integer priority must be REPORTED, not ignored.
        _write_brief("---\npriority: soon\n---\n")
        pri, _rev, _txt, err = parse_brief_meta(brief)
        assert pri is None and err and "not an integer" in err, (pri, err)
        print("[self-test] PASS a non-integer priority is caught and named")

        # ...and an unknown grade must not silently become a rating.
        _write_brief("---\nreview: BRILLIANT\n---\n")
        _pri, rev, _txt, err = parse_brief_meta(brief)
        assert rev == "" and err, (rev, err)
        print("[self-test] PASS an unknown review grade is refused")

        # NEGATIVE CONTROL: a brief with NO frontmatter is not an error. Most briefs start that
        # way, and treating "unannotated" as "malformed" would flag the whole folder.
        _write_brief("")
        pri, rev, txt, err = parse_brief_meta(brief)
        assert (pri, rev, txt, err) == (None, "", "", None), (pri, rev, txt, err)
        print("[self-test] PASS an un-annotated brief is NOT an error")

        # And a bad annotation must never be promoted to state=MALFORMED -- that word is reserved
        # for a SOLVED.md claiming a result without evidence.
        _write_brief("---\npriority: soon\n---\n")
        row = scan(td)[0]
        assert row["state"] == "OPEN" and row["meta_error"], row
        print("[self-test] PASS a bad priority reports meta_error, NOT state=MALFORMED")

    print("[self-test] RESULT: PASS")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()

    # OWNER VERDICT FROM THE COMMAND LINE.
    # Added 2026-08-22 because the owner was BLOCKED: `save_owner` existed but the GUI was the
    # ONLY way to reach it, so a stale or empty window meant the verdict could not be recorded at
    # all. A second, independent path to the same file removes the single point of failure --
    # same lesson as "disarm is a write, never a delete": the escape hatch must not depend on the
    # thing that is broken.
    #   python tools/problem_ledger.py note <slug> <DONE|MORE_NEEDED|PARKED> "free text"
    #   python tools/problem_ledger.py kickoff <slug>    -> the paste-able solver prompt
    if len(sys.argv) >= 3 and sys.argv[1] == "kickoff":
        slug = sys.argv[2]
        known = [r["slug"] for r in scan()]
        if slug not in known:
            print(f"no such problem folder: {slug}\nknown slugs: {', '.join(known)}",
                  file=sys.stderr)
            return 2
        print(kickoff_prompt(slug))
        return 0

    if len(sys.argv) >= 4 and sys.argv[1] == "note":
        slug, verdict = sys.argv[2], sys.argv[3].upper()
        text = " ".join(sys.argv[4:])
        if verdict not in OWNER_VERDICTS or not verdict:
            print(f"verdict must be one of {[v for v in OWNER_VERDICTS if v]}", file=sys.stderr)
            return 2
        try:
            path = save_owner(slug, verdict, text)
        except ValueError as exc:
            print(f"refused: {exc}", file=sys.stderr)
            print(f"known slugs: {', '.join(r['slug'] for r in scan())}", file=sys.stderr)
            return 2
        print(f"wrote {path}\n  verdict: {verdict}\n  note: {text or '(none)'}")
        return 0

    rows = scan()
    print(report(rows))
    if "--check" in sys.argv:
        bad = [r for r in rows if r["state"] in ("MALFORMED", "NO_BRIEF")]
        awaiting = [r for r in rows if r["state"] in VALID_STATUS and not r["integrated"]]
        return 1 if (bad or awaiting) else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
