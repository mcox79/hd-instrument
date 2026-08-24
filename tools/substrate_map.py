"""THE CENTRAL STORE: one joined view of brain requirement -> what we built -> gap -> who owns it.

OWNER, 2026-08-24: *"I want to understand exactly how the state of the substrate is - where the gaps
are, what the problems you've farmed out to the solver are supposed to shore up, where those
solutions have gotten us and how much progress we've made... You should have a VERY good
understanding of the brain foundational requirements... You should have a central store of this
information that you make available to solvers too."*

WHY THIS IS A JOIN AND NOT A TENTH FILE. Every piece already exists and none of them are connected:

    notes/ORGAN_MAP.md            50 organs: BRAIN'S MATH / OURS / FIDELITY / WIRED / EVIDENCE /
                                  BLOCKS. This IS the brain-foundational store -- 189 KB of prose,
                                  not queryable, not joined to anything.
    data/substrate_progress.json  10 pipeline stages: state, evidence, floor, gap, owning problem.
    notes/problems/<slug>/        the briefs we farm out, their priority, and what came back.
    data/capability_registry.jsonl what is BUILT and whether it is WIRED.

**A tenth hand-maintained file would drift within a day** -- this project has a documented history of
exactly that (`capability_map.md`, `capability_scorecard.md`, `promotion_backlog.md` all rotted
silently). So this DERIVES from the four sources on every run and stores no fact of its own.

WHAT IT ANSWERS, WHICH NOTHING CURRENTLY DOES IN ONE PLACE:
  * what does the BRAIN require here, and is that requirement PINNED or our invention?
  * what did we build, is it WIRED, and what did it MEASURE against what floor?
  * what is the GAP, in one sentence?
  * which BRIEF owns that gap, what did the solver find, and what did it BUY?

USAGE -- FOR ME AND FOR SOLVERS:
    python tools/substrate_map.py                 the whole map, one line per stage
    python tools/substrate_map.py --gaps          only what is broken or weak, worst first
    python tools/substrate_map.py --organ B3      one organ, brain requirement first
    python tools/substrate_map.py --brief <slug>  what a farmed-out problem was meant to shore up
    python tools/substrate_map.py --build         write data/substrate_map.json for the GUI
    python tools/substrate_map.py --self-test     controls both ways
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORGAN_MAP = os.path.join(REPO, "notes", "ORGAN_MAP.md")
STAGES = os.path.join(REPO, "data", "substrate_progress.json")
PROBLEMS = os.path.join(REPO, "notes", "problems")
REGISTRY = os.path.join(REPO, "data", "capability_registry.jsonl")
OUT = os.path.join(REPO, "data", "substrate_map.json")

# The field labels ORGAN_MAP uses. THIS IS A PARSER OF A HUMAN-EDITED DOC, so it is coupled to it:
# see the note at the top of notes/ORGAN_MAP.md. If a label is reworded there, this list must move
# with it -- and `--self-test` fails loudly rather than silently returning empty fields.
FIELDS = ("BRAIN'S MATH", "OURS", "FIDELITY", "WIRED", "EVIDENCE", "BLOCKS", "GAP", "STATUS")
# 🔴 THE `$` ANCHOR HERE WAS A REAL BUG, CAUGHT BY THIS FILE'S OWN COUNT CHECK (2026-08-24).
# The first version required the heading to END at the closing `**`, so it silently dropped every
# organ whose heading carries a trailing annotation -- `**C4 — Settling** *(EXPLICIT NEGATIVE
# RECOMMENDATION — do NOT build)*`, `**D8 — The cascade synapse** *(MISSING...)*`,
# `**D7 — ...** *(LABEL CORRECTED 2026-08-20: NOT MISSING...)*`. That is 18 of 50 organs, and they
# are precisely the ones carrying the strongest constraints. A parser that drops the annotated
# entries is worse than no parser: it reads as "unconstrained".
# The trailing text is CAPTURED, not discarded, and becomes a constraint line.
_ORGAN_HEAD = re.compile(r"^\*\*([A-Z]\d+)\s*[—-]\s*(.+?)\*\*\s*(.*)$")
# A line that constrains rather than describes. Deliberately broad: a false constraint costs one
# line of reading, a missed one costs a build. Same list as organ_map_cite.py, same reason.
_CONSTRAINT = re.compile(
    r"do not re-propose|do not\b|never\b|queue behind|not started|blocked behind|corrected|"
    r"retract|superseded|stale|does not count|must not|prohibition|no longer untested", re.I)


def _clean(s: str) -> str:
    """Strip markdown emphasis so a field reads as prose. Keeps the words, drops the decoration."""
    s = re.sub(r"[`*~]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_organs(path: str = ORGAN_MAP) -> dict:
    """ORGAN_MAP.md -> {id: {name, fields{}, constraints[], line}}.

    Parses by STRUCTURE (the bolded `**A1 — name**` heading and its `- **FIELD:**` bullets), never
    by keyword search over the whole file -- 'a mention is not a use', and this file names other
    organs inside an organ's own evidence paragraph constantly.
    """
    if not os.path.exists(path):
        return {}
    lines = io.open(path, encoding="utf-8", errors="replace").read().split("\n")
    organs, cur = {}, None
    for i, raw in enumerate(lines):
        m = _ORGAN_HEAD.match(raw.strip())
        if m:
            cur = m.group(1)
            trailing = _clean(m.group(3) or "")
            organs[cur] = {"id": cur, "name": _clean(m.group(2)), "fields": {},
                           "constraints": [], "line": i + 1, "heading_note": trailing}
            if trailing:            # MISSING / do NOT build / LABEL CORRECTED all arrive here
                organs[cur]["constraints"].append(trailing[:400])
            continue
        if cur is None:
            continue
        if raw.startswith("**") and not raw.startswith("- "):     # next section: this organ ended
            cur = None
            continue
        fm = re.match(r"\s*-\s*\*\*([A-Z][A-Z' /]+?)\s*[:—-]", raw)
        if fm:
            label = fm.group(1).strip()
            body = raw.split("**", 2)[-1].lstrip(":—- ")
            organs[cur]["fields"][label] = _clean(body)
            organs[cur]["_last"] = label
        elif organs[cur].get("_last") and raw.strip():
            organs[cur]["fields"][organs[cur]["_last"]] += " " + _clean(raw)
        if _CONSTRAINT.search(raw):
            organs[cur]["constraints"].append(_clean(raw)[:400])
    for o in organs.values():
        o.pop("_last", None)
    return organs


def load_stages(path: str = STAGES) -> list:
    if not os.path.exists(path):
        return []
    return json.load(io.open(path, encoding="utf-8")).get("stages", [])


def load_briefs(root: str = PROBLEMS) -> dict:
    """Every problem folder: priority, state, review, and what the solver's answer BOUGHT."""
    sys.path.insert(0, os.path.join(REPO, "tools"))
    try:
        import problem_ledger as PL
        rows = PL.scan(root) if root != PROBLEMS else PL.scan()
    except Exception:                                            # noqa: BLE001
        return {}
    out = {}
    for r in rows:
        f = r.get("fields", {}) or {}
        out[r["slug"]] = {
            "slug": r["slug"], "state": r.get("state"), "priority": r.get("priority"),
            "review": r.get("review", ""), "review_text": r.get("review_text", ""),
            "integrated": r.get("integrated", False),
            "result": str(f.get("result", ""))[:600],
            "floor": str(f.get("floor", ""))[:400],
            "reverify": str(f.get("reverify", ""))[:300],
        }
    return out


def load_registry(path: str = REGISTRY) -> dict:
    """capability_registry.jsonl -> counts only. The registry says what is BUILT, never what is
    ANSWERED -- that distinction cost this project a wasted build and is written into CLAUDE.md."""
    if not os.path.exists(path):
        return {}
    wired = shelved = total = 0
    for line in io.open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        total += 1
        st = str(r.get("integration_status") or r.get("status") or "").upper()
        if "WIRE" in st:
            wired += 1
        elif "SHELV" in st:
            shelved += 1
    return {"total": total, "wired": wired, "shelved": shelved}


def build() -> dict:
    organs, stages, briefs = parse_organs(), load_stages(), load_briefs()
    joined = []
    for s in stages:
        slugs = s.get("problems") or ([s["problem"]] if s.get("problem") else [])
        attached = [dict(briefs[x], slug=x) if x in briefs
                    else {"slug": x, "state": "NO SUCH BRIEF"} for x in slugs]
        joined.append({
            "id": s.get("id"), "name": s.get("name"), "plain": s.get("plain"),
            "state": s.get("state"), "evidence": s.get("evidence"), "floor": s.get("floor"),
            "gap": s.get("gap"), "goal": s.get("goal"), "reviewed_utc": s.get("reviewed_utc"),
            "briefs": attached,
        })
    linked = {x["slug"] for j in joined for x in j["briefs"]}
    unowned = [b for b in briefs.values() if b["state"] == "OPEN" and b["slug"] not in linked]
    return {
        "schema_version": 1,
        "_README": ("DERIVED -- do not hand-edit. Rebuild: python tools/substrate_map.py --build. "
                    "Sources: notes/ORGAN_MAP.md, data/substrate_progress.json, notes/problems/, "
                    "data/capability_registry.jsonl."),
        "organs": organs, "stages": joined, "briefs": briefs,
        "briefs_not_attached_to_a_stage": [b["slug"] for b in unowned],
        "registry": load_registry(),
    }


# ------------------------------------------------------------------ rendering
_ORDER = {"BROKEN": 0, "WEAK": 1, "UNKNOWN": 2, "UNTESTED": 3, "WORKS": 4}


def _brief_line(b):
    if not b:
        return "        (no brief owns this gap)"
    if b.get("state") == "NO SUCH BRIEF":
        return "        BRIEF %s -- NAMED BUT MISSING ON DISK" % b["slug"]
    bits = ["state=%s" % b.get("state")]
    if b.get("priority") is not None:
        bits.append("priority=%s" % b["priority"])
    if b.get("review"):
        bits.append("my review=%s" % b["review"])
    bits.append("integrated" if b.get("integrated") else "NOT integrated")
    out = ["        BRIEF %s  [%s]" % (b["slug"], ", ".join(bits))]
    if b.get("result"):
        out.append("          BOUGHT: %s" % b["result"][:200])
    return "\n".join(out)


def render(gaps_only=False):
    m = build()
    print("=" * 100)
    print("SUBSTRATE MAP -- brain requirement -> what we built -> gap -> who owns it")
    print("=" * 100)
    r = m["registry"]
    print("organs described: %d | pipeline stages: %d | briefs: %d | registry: %d built, %d wired"
          % (len(m["organs"]), len(m["stages"]), len(m["briefs"]), r.get("total", 0),
             r.get("wired", 0)))
    rows = sorted(m["stages"], key=lambda s: (_ORDER.get(s["state"], 9), s.get("id") or 0))
    for s in rows:
        if gaps_only and s["state"] in ("WORKS",):
            continue
        print()
        print("  [%-8s] %s" % (s["state"], s["name"]))
        print("        %s" % (s.get("plain") or "")[:150])
        if s.get("evidence"):
            print("        EVIDENCE: %s" % s["evidence"][:180])
        if s.get("floor"):
            print("        FLOOR   : %s" % s["floor"][:180])
        if s.get("gap"):
            print("        GAP     : %s" % s["gap"][:200])
        print(_brief_line(s.get("briefs")))
    if m["briefs_not_attached_to_a_stage"]:
        print()
        print("  OPEN BRIEFS NOT ATTACHED TO ANY STAGE (%d) -- a gap nobody is tracking, or a stage "
              "that needs one:" % len(m["briefs_not_attached_to_a_stage"]))
        for s in m["briefs_not_attached_to_a_stage"]:
            print("        %s" % s)
    return 0


def render_organ(oid):
    organs = parse_organs()
    oid = oid.upper()
    o = organs.get(oid)
    if not o:
        print("%s: NOT IN ORGAN_MAP. That is evidence the ID is wrong or the map does not cover it, "
              "NOT that the organ is unconstrained. Known IDs: %s"
              % (oid, ", ".join(sorted(organs)[:24])))
        return 1
    print("=" * 100)
    print("%s -- %s   (ORGAN_MAP.md:%d)" % (o["id"], o["name"], o["line"]))
    print("=" * 100)
    if o["constraints"]:
        print("*** %d CONSTRAINT/CORRECTION LINE(S). READ THESE FIRST. ***" % len(o["constraints"]))
        for c in o["constraints"]:
            print("   ! %s" % c[:220])
        print()
    for f in FIELDS:
        if f in o["fields"]:
            print("%-14s %s" % (f + ":", o["fields"][f][:700]))
    missing = [f for f in ("BRAIN'S MATH", "OURS") if f not in o["fields"]]
    if missing:
        print()
        print("!! this entry does not state: %s" % ", ".join(missing))
    return 0


def render_brief(slug):
    briefs = load_briefs()
    b = briefs.get(slug)
    if not b:
        print("no brief %r. known: %s" % (slug, ", ".join(sorted(briefs)[:20])))
        return 1
    stages = [s for s in build()["stages"]
              if any(x["slug"] == slug for x in (s.get("briefs") or []))]
    print("=" * 100)
    print("BRIEF %s" % slug)
    print("=" * 100)
    print("state=%s priority=%s review=%s integrated=%s"
          % (b["state"], b["priority"], b["review"] or "-", b["integrated"]))
    if stages:
        s = stages[0]
        print()
        print("MEANT TO SHORE UP: [%s] %s" % (s["state"], s["name"]))
        print("  THE GAP: %s" % (s.get("gap") or "")[:400])
    else:
        print()
        print("NOT ATTACHED TO A PIPELINE STAGE -- so what it shores up is not tracked in the map.")
    if b["result"]:
        print()
        print("WHAT CAME BACK: %s" % b["result"][:700])
    if b["floor"]:
        print("FLOOR         : %s" % b["floor"][:400])
    if b["review_text"]:
        print()
        print("MY REVIEW: %s" % b["review_text"][:500])
    if b["reverify"]:
        print()
        print("REVERIFY: %s" % b["reverify"])
    return 0


def self_test():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[self-test] %-64s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    organs = parse_organs()
    # 38, not 50. `grep -c '^\*\*[A-Z][0-9]'` reports 51 HEADINGS but only 38 UNIQUE IDs -- organs
    # appear in a summary section AND a detail section. My first threshold compared this unique
    # count against that with-duplicates count and failed a correct parser. Name the denominator.
    chk("ORGAN_MAP parses into all its organs", len(organs) >= 38, "%d unique organ ids" % len(organs))
    chk("ids are unique by construction", len(organs) == len(set(organs)))
    # POSITIVE CONTROL on a known entry -- if the doc's labels are reworded this fails loudly
    # instead of silently returning empty fields, which is the failure this repo has paid for.
    b3 = organs.get("B3")
    chk("known organ B3 is found", b3 is not None)
    if b3:
        chk("B3 carries its BRAIN'S MATH", "BRAIN'S MATH" in b3["fields"],
            "fields: %s" % ", ".join(sorted(b3["fields"]))[:110])
        chk("B3 carries OURS", "OURS" in b3["fields"])
        chk("B3's brain math mentions its pinned mechanism",
            "consolidation" in b3["fields"].get("BRAIN'S MATH", "").lower())
        chk("B3 surfaces at least one correction/constraint line", len(b3["constraints"]) > 0,
            "%d line(s)" % len(b3["constraints"]))
    # NEGATIVE CONTROL: an ID that does not exist must not be invented.
    chk("an unknown organ id returns nothing", organs.get("Z99") is None)
    # NEGATIVE CONTROL: a field label that is not in the doc must not appear.
    if b3:
        chk("a made-up field is absent", "SPARKLE" not in b3["fields"])

    m = build()
    chk("the map joins stages", len(m["stages"]) > 0, "%d stages" % len(m["stages"]))
    chk("every stage carries a state", all(s.get("state") for s in m["stages"]))
    attached = [s for s in m["stages"] if s.get("briefs")]
    chk("most stages name an owning brief", len(attached) >= 6,
        "%d of %d stages name at least one brief" % (len(attached), len(m["stages"])))
    needs_work = [s for s in m["stages"] if s.get("state") in ("BROKEN", "WEAK", "UNKNOWN", "UNTESTED")]
    unowned = [s["name"] for s in needs_work if not s.get("briefs")]
    chk("a stage that needs work and has NO brief is reported, not hidden", True,
        "%d of %d needing work are unowned: %s"
        % (len(unowned), len(needs_work), ", ".join(unowned) or "none"))
    dangling = [x["slug"] for s in m["stages"] for x in (s.get("briefs") or [])
                if x.get("state") == "NO SUCH BRIEF"]
    chk("no stage names a brief that is not on disk", not dangling, ", ".join(dangling))
    print("[self-test] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--build" in argv:
        m = build()
        tmp = OUT + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
            json.dump(m, fh, indent=1, ensure_ascii=False)
        os.replace(tmp, OUT)
        print("wrote %s (%d organs, %d stages, %d briefs)"
              % (OUT, len(m["organs"]), len(m["stages"]), len(m["briefs"])))
        return 0
    if "--organ" in argv:
        return render_organ(argv[argv.index("--organ") + 1])
    if "--brief" in argv:
        return render_brief(argv[argv.index("--brief") + 1])
    return render(gaps_only="--gaps" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
