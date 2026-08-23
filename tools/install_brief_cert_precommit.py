#!/usr/bin/env python
"""Install a pre-commit hook that refuses a commit touching notes/problems/ while its cert is red.

WHY THIS EXISTS, AND IT IS THE THIRD ESCALATION OF THE SAME LESSON. On 2026-08-23 I committed a
problem brief while `verification/test_problem_briefs_and_flags.py` was FAILING on it -- the brief
was missing a required guard section. The cert had already told me. I chained the commit after a
PIPED pytest:

    pytest ... 2>&1 | tail -3 && git add ... && git commit

**A pipeline's exit status is the LAST command's**, so the chain saw `tail` succeed and proceeded on
a red suite. That was the SECOND time that night the same pipe pattern hid a failing gate, and I had
written the lesson down after the first.

**A CAUTION WRITTEN AS PROSE GETS VIOLATED; A CONTROL WRITTEN AS CODE CATCHES SOMETHING.** This repo
has that rule five times over (`rank_with_ties.py`, `replication_gate.py`, `organ_map_cite.py` ...),
each added after a prose rule failed to stop its own author. This is the same move for the same
reason: I do not need another note telling me to check exit codes, I need the unsafe commit to be
unrepresentable.

WHAT IT GUARDS, DELIBERATELY NARROW: only commits that stage something under `notes/problems/`, and
only the brief cert, which runs in about half a second. A hook that runs the full suite on every
commit gets uninstalled within a day, and an uninstalled hook guards nothing.

    python tools/install_brief_cert_precommit.py            # install
    python tools/install_brief_cert_precommit.py --check    # report status, change nothing
    python tools/install_brief_cert_precommit.py --self-test

NOT VERSION-CONTROLLED, AND THAT IS A REAL LIMIT, STATED RATHER THAN HIDDEN. `.git/hooks/` is not in
the repository, so this protects THIS checkout only and a fresh clone starts unguarded. That is why
this ships as an installer script that IS tracked, rather than as a hook file that is not -- the
tracked thing is the ability to reinstate it.
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO, ".git", "hooks", "pre-commit")
MARKER = "hd-instrument brief-cert pre-commit"

BODY = '''#!/bin/sh
# ''' + MARKER + '''
# Installed by tools/install_brief_cert_precommit.py. See that file for why.
# Refuses a commit that stages anything under notes/problems/ while the brief cert is failing.
# Bypass deliberately with: git commit --no-verify   (and say so in the commit message)

if git diff --cached --name-only | grep -q '^notes/problems/'; then
    PY="$(git rev-parse --show-toplevel)/.venv/Scripts/python.exe"
    [ -x "$PY" ] || PY=python
    "$PY" -X utf8 -m pytest verification/test_problem_briefs_and_flags.py -q
    rc=$?
    if [ $rc -ne 0 ]; then
        echo ""
        echo "COMMIT REFUSED: notes/problems/ is staged and its cert is FAILING (exit $rc)."
        echo "  A brief missing a guard section looks complete and is not."
        echo "  Fix it, or bypass with --no-verify and say so in the message."
        exit 1
    fi
fi

# --- Q115 (owner ruling 2026-08-23): a NEW experiment must be genuinely re-runnable. -------------
# "I think you should def make it a requirement for new experiments, but I would go back through the
#  275 older ones one at a time." So this fires ONLY on ADDED files (diff-filter=A), never on the
#  existing backlog -- a rule that fired on 1,413 old cells would be switched off within a day, and
#  a switched-off rule protects nothing.
ADDED="$(git diff --cached --name-only --diff-filter=A | grep '^experiments/.*\\.py$')"
if [ -n "$ADDED" ]; then
    PY="$(git rev-parse --show-toplevel)/.venv/Scripts/python.exe"
    [ -x "$PY" ] || PY=python
    # shellcheck disable=SC2086
    "$PY" -X utf8 -W ignore tools/reproducibility_inventory.py --check-new $ADDED || exit 1
fi
exit 0
'''


def status():
    if not os.path.isfile(HOOK):
        return "ABSENT"
    try:
        t = open(HOOK, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return "UNREADABLE (%s)" % e
    return "INSTALLED" if MARKER in t else "PRESENT BUT NOT MINE -- refusing to overwrite"


def install() -> int:
    st = status()
    if st.startswith("PRESENT BUT NOT MINE"):
        print("[precommit] %s" % st)
        print("            A hook already exists that this script did not write. Not touching it.")
        print("            Merge by hand if you want both.")
        return 1
    os.makedirs(os.path.dirname(HOOK), exist_ok=True)
    with open(HOOK, "wb") as fh:          # binary: an sh script must not gain CRLF here
        fh.write(BODY.encode("utf-8"))
    try:
        os.chmod(HOOK, 0o755)
    except OSError:
        pass                              # Windows; git for windows runs it via sh regardless
    print("[precommit] installed at .git/hooks/pre-commit")
    print("            guards 1: commits staging notes/problems/ -- brief cert (~0.5s)")
    print("            guards 2: NEW experiments/*.py that write a result -- must call the shared")
    print("                      save-location helper, so a re-run recomputes (owner ruling Q115)")
    print("            NOT version-controlled -- a fresh clone starts unguarded; re-run this to arm it")
    return 0


def self_test() -> int:
    ok = True

    # The guard must actually be able to FIRE. Run the cert the hook runs and check it returns a
    # real exit code -- a hook whose gate cannot fail is decoration.
    p = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest",
                        "verification/test_problem_briefs_and_flags.py", "-q"],
                       cwd=REPO, capture_output=True, encoding="utf-8", errors="replace")
    if p.returncode == 0:
        print("[self-test] PASS the guarded cert runs and currently passes (exit 0)")
    else:
        print("[self-test] FAIL the guarded cert is RED right now -- fix that before installing")
        ok = False

    # The hook body must key on the right path, or it guards nothing.
    if "notes/problems/" in BODY and "--no-verify" in BODY:
        print("[self-test] PASS the hook keys on notes/problems/ and documents its bypass")
    else:
        print("[self-test] FAIL hook body is wrong")
        ok = False

    # NEGATIVE CONTROL: neither guard may fire on a commit that touches neither area. Checked
    # structurally -- every guarded action sits inside its own `if`, and the body ends at exit 0.
    if BODY.count("\nif ") == 2 and BODY.strip().endswith("exit 0"):
        print("[self-test] PASS both guards are conditional; an unrelated commit exits 0 immediately")
    else:
        print("[self-test] FAIL a guard is not conditional -- it would run on every commit")
        ok = False

    # 🔻 THE DRIFT CHECK, ADDED BECAUSE IT ALREADY HAPPENED (2026-08-23). The Q115 gate was added to
    # the INSTALLED hook and lost from this file within the hour, so the two disagreed and the next
    # re-install would have silently DISARMED the gate while printing "installed". A guard that can
    # be removed by running its own installer is worse than none, because it reports success.
    if "diff-filter=A" in BODY and "reproducibility_inventory.py --check-new" in BODY:
        print("[self-test] PASS the Q115 new-cell gate is present in the body this script installs")
    else:
        print("[self-test] FAIL the Q115 gate is MISSING -- installing would disarm it")
        ok = False

    if os.path.isfile(HOOK):
        live = open(HOOK, encoding="utf-8", errors="replace").read()
        same = ("diff-filter=A" in live) == ("diff-filter=A" in BODY)
        print("[self-test] %s the installed hook and this script agree about the Q115 gate"
              % ("PASS" if same else "FAIL"))
        ok = ok and same

    print("[self-test] " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        print("[precommit] status: %s" % status())
        return 0
    return install()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
