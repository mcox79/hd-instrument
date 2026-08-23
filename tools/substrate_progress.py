"""Load, validate and age-check `data/substrate_progress.json` -- the SUBSTRATE tab's data.

WHY A VALIDATOR AND NOT JUST A JSON READ. The owner asked for a tab that is "a VERY clear and
maintained status of our progress". The hard word is MAINTAINED. A panel of curated sentences is
accurate on the day it is written and quietly wrong a week later, and nothing about looking at it
tells you which. This module makes the failure visible instead:

  * every row carries `reviewed_utc`, and `age_days()` turns that into a number the GUI colours
    (>3 days AMBER, >7 days RED). **The tab shows its own staleness.**
  * `validate()` refuses a row whose `evidence` states a number with no `floor` beside it. That is
    the repo's oldest rule -- a number without a floor is not evidence -- applied at the one place
    the owner actually reads numbers.
  * `validate()` refuses a `source` path that does not exist on disk. A citation nobody can open is
    a claim wearing a citation's clothes.
  * `validate()` refuses jargon in `plain`. The owner has said four times that they cannot act on
    text full of metric and organ names.

RUN:
    python tools/substrate_progress.py            # render the table as text
    python tools/substrate_progress.py --check    # validate; exit 1 on any error
    python tools/substrate_progress.py --self-test
"""
import argparse
import datetime as _dt
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data", "substrate_progress.json")

STATES = ("WORKS", "WEAK", "BROKEN", "UNTESTED", "UNKNOWN")
AMBER_DAYS = 3
RED_DAYS = 7

REQUIRED = ("id", "name", "plain", "state", "evidence", "floor", "gap", "goal", "source",
            "reviewed_utc")

# Words that mean nothing to the owner. Deliberately short: a long list would flag real prose and
# get switched off, and a control that gets switched off is worse than none.
JARGON = ("CI-separated", "p95", "PPMI", "cosine", "SimLex", "SimVerb", "HARD_PASS", "MIDDLE_BAND",
          "VSA", "hypervector", "n_dim", "arm_key", "prereg", "ablation", "hdlab/", "organ")

_NUM = re.compile(r"\d")


def load(path=DATA):
    """Read the file. Raises rather than returning a default -- an empty tab must not look healthy."""
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _parse_utc(s):
    return _dt.datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)


def age_days(reviewed_utc, now=None):
    """Whole days since the row was last actually re-checked. Negative clamps to 0."""
    now = now or _dt.datetime.now(_dt.timezone.utc)
    return max(0.0, (now - _parse_utc(reviewed_utc)).total_seconds() / 86400.0)


def freshness(reviewed_utc, now=None):
    """FRESH / AMBER / RED. The GUI colours on this, so the thresholds live here, not in the GUI."""
    d = age_days(reviewed_utc, now)
    if d > RED_DAYS:
        return "RED"
    if d > AMBER_DAYS:
        return "AMBER"
    return "FRESH"


def validate(doc, repo=REPO):
    """Return a list of human-readable problems. Empty list means the document is sound."""
    errs = []
    stages = doc.get("stages")
    if not stages:
        return ["no stages at all -- an empty SUBSTRATE tab would render as healthy"]

    head = doc.get("headline") or {}
    for k in ("the_wall", "plain", "reviewed_utc"):
        if not str(head.get(k) or "").strip():
            errs.append("headline is missing %r" % k)

    seen_ids = set()
    for st in stages:
        tag = "stage %s (%s)" % (st.get("id"), str(st.get("name"))[:34])
        for k in REQUIRED:
            if not str(st.get(k) or "").strip():
                errs.append("%s: missing %r" % (tag, k))
        if st.get("id") in seen_ids:
            errs.append("%s: duplicate id" % tag)
        seen_ids.add(st.get("id"))

        if st.get("state") not in STATES:
            errs.append("%s: state %r is not one of %s" % (tag, st.get("state"), list(STATES)))

        # THE LOAD-BEARING CHECK: a number with no floor beside it is not evidence.
        ev, fl = str(st.get("evidence") or ""), str(st.get("floor") or "")
        if _NUM.search(ev) and not fl.strip():
            errs.append("%s: evidence states a number and floor is empty -- "
                        "a number without a floor is not evidence" % tag)

        src = str(st.get("source") or "")
        if src and not os.path.exists(os.path.join(repo, src)):
            errs.append("%s: source %r does not exist on disk" % (tag, src))

        prob = str(st.get("problem") or "")
        if prob and not os.path.isdir(os.path.join(repo, "notes", "problems", prob)):
            errs.append("%s: problem %r has no folder" % (tag, prob))

        for j in JARGON:
            if j.lower() in str(st.get("plain") or "").lower():
                errs.append("%s: plain-language field contains %r" % (tag, j))

        try:
            _parse_utc(st.get("reviewed_utc"))
        except Exception:
            errs.append("%s: reviewed_utc %r is not YYYY-MM-DDTHH:MM:SSZ" % (tag, st.get("reviewed_utc")))
    return errs


def rows_for_display(doc, now=None):
    """One flat dict per stage, ready for the GUI table. Sorted by id so the order is the pipeline."""
    out = []
    for st in sorted(doc.get("stages", []), key=lambda s: s.get("id", 0)):
        out.append({
            "id": st.get("id"),
            "name": st.get("name", ""),
            "state": st.get("state", "UNKNOWN"),
            "plain": st.get("plain", ""),
            "evidence": st.get("evidence", ""),
            "floor": st.get("floor", ""),
            "gap": st.get("gap", ""),
            "goal": st.get("goal", ""),
            "problem": st.get("problem", ""),
            "source": st.get("source", ""),
            "reviewed_utc": st.get("reviewed_utc", ""),
            "age_days": age_days(st.get("reviewed_utc"), now),
            "freshness": freshness(st.get("reviewed_utc"), now),
        })
    return out


def _self_test():
    """Controls BOTH ways on every rule, so a rule that never fires cannot pass as enforcement."""
    ok = True

    def chk(label, cond):
        nonlocal ok
        print("[self-test] %-58s %s" % (label, "PASS" if cond else "FAIL"))
        ok = ok and bool(cond)

    good = {"headline": {"the_wall": "x", "plain": "y", "reviewed_utc": "2026-08-23T00:00:00Z"},
            "stages": [{"id": 1, "name": "N", "plain": "ordinary words", "state": "WORKS",
                        "evidence": "9 of 10", "floor": "must beat 5 of 10", "gap": "g",
                        "goal": "t", "source": "CLAUDE.md", "problem": "",
                        "reviewed_utc": "2026-08-23T00:00:00Z"}]}
    chk("a well-formed document validates clean", validate(good) == [])

    import copy
    bad = copy.deepcopy(good); bad["stages"][0]["floor"] = ""
    chk("a number with no floor is REFUSED", any("without a floor" in e for e in validate(bad)))

    # `floor` is REQUIRED on every row, number or not -- a stage that cannot say what it must beat
    # has not been thought about. So an empty floor is refused either way; what the number-specific
    # rule adds is the DIAGNOSIS, and this arm pins that the two messages stay distinguishable.
    bad = copy.deepcopy(good); bad["stages"][0]["evidence"] = "no digits here"; bad["stages"][0]["floor"] = ""
    e_prose = validate(bad)
    chk("an empty floor is refused even when evidence has no number",
        any("missing 'floor'" in x for x in e_prose))
    chk("...and it does NOT claim a number went unfloored",
        not any("without a floor" in x for x in e_prose))

    bad = copy.deepcopy(good); bad["stages"][0]["source"] = "does/not/exist.md"
    chk("a source that is not on disk is REFUSED", any("does not exist" in e for e in validate(bad)))

    bad = copy.deepcopy(good); bad["stages"][0]["state"] = "GOOD"
    chk("an invented state is REFUSED", any("is not one of" in e for e in validate(bad)))

    bad = copy.deepcopy(good); bad["stages"][0]["plain"] = "the PPMI cosine is fine"
    chk("jargon in the plain field is REFUSED", any("plain-language" in e for e in validate(bad)))

    bad = copy.deepcopy(good); bad["stages"] = []
    chk("an empty document does NOT render as healthy", validate(bad) != [])

    now = _dt.datetime(2026, 8, 23, tzinfo=_dt.timezone.utc)
    chk("today is FRESH", freshness("2026-08-23T00:00:00Z", now) == "FRESH")
    chk("5 days is AMBER", freshness("2026-08-18T00:00:00Z", now) == "AMBER")
    chk("30 days is RED", freshness("2026-07-24T00:00:00Z", now) == "RED")

    errs = validate(load())
    chk("THE REAL FILE ON DISK validates clean", errs == [])
    for e in errs:
        print("      -> %s" % e)

    print("[self-test] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="validate and exit non-zero on error")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)

    if a.self_test:
        return _self_test()

    doc = load()
    errs = validate(doc)
    if a.check:
        for e in errs:
            print("[substrate-progress] ERROR %s" % e)
        print("[substrate-progress] %d error(s)" % len(errs))
        return 1 if errs else 0

    h = doc.get("headline", {})
    print("THE WALL: %s" % h.get("the_wall", ""))
    print()
    print("  %-3s %-26s %-9s %-7s %s" % ("#", "STAGE", "STATE", "AGE", "GAP"))
    for r in rows_for_display(doc):
        print("  %-3s %-26s %-9s %-7s %s" % (
            r["id"], r["name"][:26], r["state"], "%.0fd" % r["age_days"], r["gap"][:60]))
    if errs:
        print()
        for e in errs:
            print("  ERROR %s" % e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
