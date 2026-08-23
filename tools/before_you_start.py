"""BEFORE YOU START: run the prior-work check on what you are ABOUT TO DO, in one command.

WHY THIS EXISTS. On 2026-08-21 I proposed SEVEN pieces of work that were already answered on disk:
build the foraging organ (built, PINNED, run at 10k sentences); improve coreference that way
(HARD_FAIL on that exact mechanism); turn on the graded switches (already default-ON, and already
floored); hand-score 100 facts (a BLIND 100-row score already existed, done and written up); gate
writes by prediction error (already dissociated -- a random gate at the same rate ties it); sweep the
write rate (already swept, four thresholds); wire the sensorimotor spoke (already scored, 3 seeds,
40k sentences each).

**EACH WAS ONE `experiment_index` QUERY AWAY, AND I RAN THAT TOOL FAITHFULLY -- ON THE THING I WAS
*BUILDING*, NEVER ON THE THING I WAS *DOING*.** The standing rule says "before building OR wiring
anything, query BOTH archives". Hand-scoring is neither building nor wiring, so the rule never fired.

**SO THIS TAKES A PLAIN-ENGLISH DESCRIPTION OF THE INTENDED WORK AND QUERIES THE VERBS AS WELL AS THE
NOUNS.** "I am going to hand-score the grounding output" queries `hand-score`, `score`, `grounding`,
`quality` -- not just the organ name.

**IT CANNOT RETURN SILENTLY.** Every run prints what it searched and how many rows it scanned, because
`substrate_query.sh` returning zero bytes and exiting 0 is the failure this whole archive line exists
to prevent, and `experiment_index` itself once shipped a variant of it.

USAGE
  python tools/before_you_start.py "hand-score the definitional grounding output"
  python tools/before_you_start.py --self-test
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = str(REPO / ".venv" / "Scripts" / "python.exe")
INDEX = REPO / "tools" / "experiment_index.py"
REGISTRY = REPO / "data" / "capability_registry.jsonl"

# ACTIVITY VERBS -- the half that was never queried. Each maps to the words the archive actually
# uses, because a cell is named for what it MEASURED, not for what its author was doing that day.
ACTIVITY = {
    "hand-score": ["handscore", "blind", "quality"],
    "handscore": ["handscore", "blind", "quality"],
    "score": ["quality", "handscore"],
    "grade": ["quality", "handscore"],
    "sweep": ["sweep", "gating rate"],
    "gate": ["ingest gate", "write gate", "quality gate"],
    "wire": ["wire", "wiring"],
    "audit": ["audit", "coverage"],
    "measure": ["instrument", "quality"],
    "evaluate": ["evaluation", "quality"],
    "build": ["build"],
    "read": ["reading", "read grow"],
    "extract": ["extraction", "extractor"],
    "encode": ["encoder", "encoding quality"],
    "select": ["selection"],
    "rank": ["ranking", "rank"],
    "place": ["cold placement", "placement"],
    "forage": ["information foraging", "gap driven"],
    "predict": ["predictive coding", "surprise"],
}
STOP = set("the a an of to for on in and or i we you it that this is are be will would should our my "
           "am going next then with from by at as it's its into out up".split())


def terms_from(text: str):
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z\-']+", text.lower()) if w not in STOP]
    nouns, acts = [], []
    for w in words:
        base = w.rstrip("s") if len(w) > 4 else w
        for key in (w, base):
            if key in ACTIVITY:
                acts.extend(ACTIVITY[key])
                break
        else:
            if len(w) > 3:
                nouns.append(w)
    seen, out = set(), []
    for t in acts + nouns:                       # ACTIVITIES FIRST -- they are the ones that get missed
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:10]


def run_query(term: str):
    try:
        r = subprocess.run([PY, str(INDEX), "query", term], capture_output=True, text=True,
                           timeout=180, cwd=str(REPO))
    except Exception as e:
        return None, "ERROR %s" % type(e).__name__
    out = r.stdout or ""
    m = re.search(r"\[query\] (\d[\d,]*) matching cells \((\d[\d,]*) landed\)", out)
    if not m:
        return None, "no count line -- TOOL PROBLEM, not an absence"
    n = int(m.group(1).replace(",", ""))
    landed = int(m.group(2).replace(",", ""))
    corr = out.count("!! CORRECTION ON THIS CELL")
    verdicts = re.findall(r"verdict: (\S+)", out)
    return (n, landed, corr, verdicts[:4]), None


def main():
    if "--self-test" in sys.argv:
        return _self_test()
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[-3])
        return 2
    text = " ".join(a for a in sys.argv[1:] if not a.startswith("--"))
    terms = terms_from(text)
    print("=" * 78)
    print("BEFORE YOU START:  %s" % text)
    print("=" * 78)
    print("querying %d terms (ACTIVITIES FIRST -- those are the ones that get missed): %s\n"
          % (len(terms), ", ".join(terms)))
    total = 0
    for t in terms:
        res, err = run_query(t)
        if err:
            print("  %-26s !! %s" % (t, err))
            continue
        n, landed, corr, verdicts = res
        total += n
        flag = "   " if n == 0 else ">> "
        print("%s%-26s %3d cells (%d landed)%s" % (flag, t, n, landed,
              ("   [%d CELL(S) CARRY A CORRECTION]" % corr) if corr else ""))
        for v in verdicts:
            print("       %s" % v[:96])
    print()
    if total == 0:
        print("NO PRIOR WORK FOUND ON ANY TERM. That is a real absence ONLY because every query above")
        print("printed its scan count. If a term errored, treat it as UNKNOWN, not as absent.")
    else:
        print("!! %d total matches. READ EVERY ROW A QUERY RETURNED BEFORE QUOTING ANY OF THEM --" % total)
        print("   on 2026-08-21 a 4-row result was read at row 1, and row 4 reversed row 1.")
    concurrent_work(terms)
    slot_status(terms)
    print("\nSTILL TO DO BY HAND: `python tools/organ_map_cite.py <ORGAN_ID>` if an organ is involved,")
    print("and grep data/capability_registry.jsonl for the capability name.")
    return 0


def slot_status(terms):
    """IS THE ORGAN YOU ARE ABOUT TO IMPROVE ACTUALLY CONNECTED?

    Measured 2026-08-22: four autoloop continuations went into the case for repairing the
    sensorimotor norms lookup -- coverage gain, verb signal, word-class enrichment -- before anyone
    checked whether `read()` calls it. It does not. **That was already written in `substrate.py`'s
    own slot table** (`B5`: *"read() does not consult it, so it is NEEDS_ADAPTER and not FILLED"*),
    and none of the five standing prior-work reads searches that file.
    """
    try:
        from tools.slot_status import find, slots
        rows = slots()
    except Exception as e:                                # noqa: BLE001
        print("-" * 78)
        print("  !! slot table UNREADABLE (%s: %s) -- wiring status UNKNOWN, not clear"
              % (type(e).__name__, e))
        return
    hits = []
    seen = set()
    for t in terms:
        for r in find(t, rows):
            if r[0] not in seen:
                seen.add(r[0])
                hits.append(r)
    print("-" * 78)
    print("IS IT EVEN WIRED?  (%d slots; NEEDS_ADAPTER = built but NOT on the live path, so"
          " improving it moves no downstream number)" % len(rows))
    if not hits:
        print("  no slot matches your terms. NOT evidence it is wired -- it may not be in the table.")
        return
    for sid, need, organ, status, _ in hits[:8]:
        flag = "   " if status == "FILLED" else ">> "
        print("  %s%-4s %-14s %-30s %s" % (flag, sid, status, organ[:30], need[:36]))
    if any(h[3] != "FILLED" for h in hits):
        print("  ^^ python tools/slot_status.py <term>   for the rationale, which says WHY not.")


def recent_commits(hours: int = 72):
    """(subjects, error) for the last `hours` of git log. Never returns a bare empty on failure."""
    import subprocess
    try:
        # `text=True` decodes with the ANSI codepage (cp1252 here), NOT utf-8. Measured 2026-08-22:
        # one undecodable byte in a commit subject kills subprocess's reader thread, and the call
        # then returns **stdout=None with returncode 0 and an EMPTY stderr** -- so the failure is
        # indistinguishable from a clean empty log. This tool would have printed "nobody else is on
        # it", its single most dangerous output. Same class as the repo's PowerShell text-mode rule.
        out = subprocess.run(["git", "log", "--since=%d.hours" % hours, "--format=%h\t%s"],
                             cwd=str(REPO), capture_output=True, timeout=20,
                             encoding="utf-8", errors="replace")
        if out.returncode != 0:
            return [], (out.stderr or "git log failed").strip().splitlines()[0][:70]
        if out.stdout is None:
            return [], "git log returned rc=0 but no stdout (decode failure) -- NOT an empty log"
        return [l for l in out.stdout.splitlines() if l.strip()], None
    except Exception as e:                                    # noqa: BLE001
        return [], "%s: %s" % (type(e).__name__, e)


def open_claims():
    """(rows, error) for queue items currently CLAIMED by somebody."""
    try:
        import json
        p = REPO / "data" / "dispatch_queue.jsonl"
        if not p.exists():
            return [], "no data/dispatch_queue.jsonl on disk"
        rows = []
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if d.get("status") == "claimed":
                    rows.append(d)
        return rows, None
    except Exception as e:                                    # noqa: BLE001
        return [], "%s: %s" % (type(e).__name__, e)


def concurrent_work(terms):
    """IS SOMEBODY ELSE DOING THIS RIGHT NOW? The three archives answer 'was it done'; none of them
    can see work that is IN FLIGHT.

    Measured 2026-08-22, two strategy sessions on one repo in one afternoon: a permissions audit was
    answered twice 44 minutes apart, and the SAME tool file was written twice simultaneously -- the
    second copy landed on disk before the first author staged it, so a commit shipped the other
    session's code under its own message. **A lost update with no error, no conflict and no
    warning.** The git-log half would have caught the first; only a CLAIM can catch the second.
    """
    print("-" * 78)
    print("IS SOMEONE ELSE ALREADY ON IT?  (the archives answer 'was it DONE', never 'is it BEING")
    print("done' -- on 2026-08-22 that gap cost two duplicated audits and one lost file)")

    commits, err = recent_commits()
    if err:
        print("  !! recent commits UNKNOWN (%s) -- absence NOT established" % err)
    else:
        # Rank by HOW MANY DISTINCT TERMS a subject matches, not by recency. A single generic term
        # ("fix", "queue") matches ~11% of a 700-commit window, and a guard that flags one commit in
        # nine is one nobody reads. Sorting by term-overlap puts the genuine collision on line 1.
        scored = []
        for c in commits:
            k = sum(1 for t in terms if t.lower() in c.lower())
            if k:
                scored.append((k, c))
        scored.sort(key=lambda kc: -kc[0])
        print("  scanned %d commits from the last 72h; %d mention your terms (best overlap first)"
              % (len(commits), len(scored)))
        for k, c in scored[:8]:
            print("     >> [%d terms] %s" % (k, c[:88]))

    claims, err = open_claims()
    if err:
        print("  !! open claims UNKNOWN (%s) -- absence NOT established" % err)
    else:
        hit = [c for c in claims
               if any(t.lower() in (c.get("title", "") + " " + c.get("brief", "")).lower()
                      for t in terms)]
        print("  %d item(s) currently CLAIMED in the queue; %d match your terms" % (len(claims), len(hit)))
        for c in hit[:8]:
            print("     >> [%s] %s" % (c.get("claimed_by"), str(c.get("title"))[:70]))
        if hit:
            print("  ^^ TALK TO THAT OWNER BEFORE STARTING. If it is you, carry on.")
    print("  ANNOUNCE YOURS:  python tools/dispatch_queue.py announce '<what you are starting>' --by <session>")


def _self_test():
    """A prior-work tool that has never been shown to return NON-zero cannot establish absence."""
    t = terms_from("hand-score the definitional grounding output")
    assert "handscore" in t, "activity verb not extracted: %r" % t
    assert t.index("handscore") < t.index("definitional"), "activities must be queried FIRST: %r" % t
    t2 = terms_from("sweep the write rate")
    assert any(x in t2 for x in ("sweep", "gating rate")), t2
    # POSITIVE CONTROL against the live index -- a known-present term must return rows.
    res, err = run_query("quality")
    assert err is None, "query failed: %s" % err
    assert res[0] > 50, "known-present term 'quality' returned %r -- the index is broken" % (res,)
    # NEGATIVE CONTROL -- a nonsense term must return zero, proving non-zero means something.
    res2, err2 = run_query("zzqqxx_not_a_real_term")
    assert err2 is None and res2[0] == 0, "known-absent term returned %r" % (res2,)
    # POSITIVE CONTROL ON THE CONCURRENT-WORK HALF. A `git log` that silently returns nothing reads
    # exactly like "nobody else is on it" -- the most dangerous output this tool can produce, and
    # the same defect that made `director_kb_query.py` useless while reporting success.
    commits, cerr = recent_commits(hours=24 * 3650)
    assert cerr is None, "git log failed: %s" % cerr
    assert len(commits) > 100, "recent_commits returned %d -- it CANNOT establish absence" % len(commits)
    claims, qerr = open_claims()
    assert qerr is None, "queue unreadable: %s" % qerr
    assert all("id" in c for c in claims), "a claimed row is missing its id"
    print("self-test PASS (verb extraction, activities-first ordering, "
          "known-present control %d cells, known-absent control 0)" % res[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
