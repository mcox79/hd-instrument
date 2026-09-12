"""tools/scorecard.py -- the ONE plain-language scorecard of the substrate: how well it performs and how
brain-faithful it is. Owner request 2026-09-11: "a clear idea of how well the substrate is performing, and its
capabilities ... kept updated, from a document that you keep updated ... capabilities, brain foundational fidelity,
etc. ... intuitive and jargon free."

SOURCES (all on disk; nothing is transcribed by hand except the plain-language sections of notes/SCORECARD.md):
  notes/BOARD_TREND.jsonl        one row per FULL board run (per-ability score vs simple-rule floor, twin, CI-sep)
  notes/bf_status_registry.jsonl  brain-foundational status of every organ (BF / BF_SPIRIT / NOT_BF)
  notes/scorecard_spec.json       plain name + group + organs behind each ability (hand-maintained by strategy)
  notes/problems/*/PROBLEM.md     what is being worked on (open / in review / waiting to be folded in)
  notes/BOARD.md                  questions waiting on the owner (via tools/board.py)
  notes/SCORECARD.md              the plain-language sections strategy keeps updated (THE SHORT VERSION etc.)
OUTPUT: data/scorecard.json (read by tools/scorecard_gui.py) and the AUTO table inside notes/SCORECARD.md.
Run:  .venv/Scripts/python.exe tools/scorecard.py          (prints the plain summary, writes both outputs)
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

TREND = REPO / "notes" / "BOARD_TREND.jsonl"
REGISTRY = REPO / "notes" / "bf_status_registry.jsonl"
SPEC = REPO / "notes" / "scorecard_spec.json"
DOC = REPO / "notes" / "SCORECARD.md"
OUT = REPO / "data" / "scorecard.json"
PROBLEMS = REPO / "notes" / "problems"
AUTO_BEGIN, AUTO_END = "<!-- AUTO:BEGIN (written by tools/scorecard.py; edit the sections ABOVE, not this) -->", "<!-- AUTO:END -->"

FIDELITY_WORDS = {
    "BF": "copies the brain's math (pinned)",
    "BF_SPIRIT": "brain model; some details still open",
    "NOT_BF": "uses a stand-in we are replacing",
    "MIXED": "brain model; one part is a stand-in we are replacing",
}


def _jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def registry_statuses() -> dict[str, str]:
    return {r["module"].split("/")[-1][:-3]: r.get("status", "?") for r in _jsonl(REGISTRY)
            if r.get("module") and not r.get("shim")}   # shims re-export a consolidated organ; not organs


def fidelity_for(organs: list[str], statuses: dict[str, str]) -> tuple[str, str, list[str]]:
    """(code, plain words, stand-in organs). NOT_BF anywhere -> stand-in; all BF -> pinned; else model."""
    st = [statuses.get(o, "?") for o in organs]
    bad = [o for o, s in zip(organs, st) if s == "NOT_BF"]
    if bad:
        code = "NOT_BF" if len(bad) == len(organs) else "MIXED"
    elif st and all(s == "BF" for s in st):
        code = "BF"
    else:
        code = "BF_SPIRIT"
    return code, FIDELITY_WORDS[code], bad


def _pct(x) -> str:
    return "-" if x is None else "%d in 100" % round(100 * float(x))


def _score_words(row: dict | None, metric: str) -> tuple[str, str]:
    """(how well, verdict vs the simple rule) in plain words."""
    if not row or row.get("model") is None:
        return "not scored in the last full check", "-"
    m, f = float(row["model"]), row.get("floor")
    if metric == "agreement":
        how = "agreement with people %.2f (out of 1)" % m
    elif metric == "rank":
        how = "right meaning ranked near the top %s" % _pct(m)
    else:
        how = "right %s" % _pct(m)
    if f is None:
        return how, "no simple-rule comparison"
    f = float(f)
    if row.get("sep"):
        verdict = "clearly better than the simple rule (%s)" % (("%.2f" % f) if metric == "agreement" else _pct(f))
    elif m > f:
        verdict = "a little better than the simple rule (%s), not yet convincingly" % (("%.2f" % f) if metric == "agreement" else _pct(f))
    else:
        verdict = "not better than the simple rule (%s) yet" % (("%.2f" % f) if metric == "agreement" else _pct(f))
    return how, verdict


def _trend_words(cur: dict | None, prev: dict | None) -> str:
    if not cur or cur.get("model") is None:
        return "-"
    if not prev or prev.get("model") is None:
        return "first full check on record"
    d = float(cur["model"]) - float(prev["model"])
    if abs(d) < 0.005:
        return "unchanged since the previous check"
    return ("up" if d > 0 else "DOWN") + " %.3f since the previous check" % abs(d)


def _frontmatter(p: Path) -> dict:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    fm = {}
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
    fm["_title"] = next((ln.lstrip("# ").strip() for ln in txt.splitlines() if ln.startswith("# ")), p.parent.name)
    return fm


def problems() -> dict:
    """Open (assignable), in review (SOLVED, awaiting owner), waiting to fold in (owner-DONE, not integrated)."""
    open_, review, fold = [], [], []
    if PROBLEMS.is_dir():
        for d in sorted(PROBLEMS.iterdir()):
            pm = d / "PROBLEM.md"
            if not pm.is_file():
                continue
            fm = _frontmatter(pm)
            solved = (d / "SOLVED.md")
            owner = (d / "OWNER_NOTES.md")
            title = re.sub(r"\s+", " ", fm.get("_title", d.name))[:160]
            pri = fm.get("priority") or ""
            if solved.is_file():
                s_txt = solved.read_text(encoding="utf-8", errors="ignore")
                done = owner.is_file() and "owner_verdict: DONE" in owner.read_text(encoding="utf-8", errors="ignore")
                if "INTEGRATED_BY_STRATEGY" in s_txt:
                    continue
                (fold if done else review).append({"slug": d.name, "title": title, "priority": pri})
            elif fm.get("status", "").upper() == "OPEN":
                open_.append({"slug": d.name, "title": title, "priority": pri})
    open_.sort(key=lambda r: (int(r["priority"]) if str(r["priority"]).isdigit() else 999))
    return {"open": open_, "in_review": review, "waiting_to_fold_in": fold}


def board_open() -> list[dict]:
    try:
        import board as B
        return [{"id": r.get("id"), "question": r.get("question"), "why": r.get("why"), "rec": r.get("rec")}
                for r in B.open_questions()]
    except Exception:
        return []


def hand_sections() -> dict[str, str]:
    """The plain-language sections strategy maintains in notes/SCORECARD.md (everything above the AUTO block)."""
    out: dict[str, str] = {}
    if not DOC.is_file():
        return out
    txt = DOC.read_text(encoding="utf-8")
    txt = txt.split(AUTO_BEGIN)[0]
    cur, buf = None, []
    for ln in txt.splitlines():
        if ln.startswith("## "):
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = ln[3:].strip(), []
        elif cur is not None:
            buf.append(ln)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def build() -> dict:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    trend = _jsonl(TREND)
    cur = trend[-1] if trend else {}
    prev = trend[-2] if len(trend) > 1 else {}
    statuses = registry_statuses()
    caps = []
    for key, c in spec["capabilities"].items():
        row = (cur.get("dims") or {}).get(key) or (cur.get("arms") or {}).get(key)
        prow = (prev.get("dims") or {}).get(key) or (prev.get("arms") or {}).get(key)
        how, verdict = _score_words(row, c.get("metric", "accuracy"))
        fcode, fwords, bad = fidelity_for(c["organs"], statuses)
        caps.append({"key": key, "name": c["name"], "group": c["group"], "headline": bool(c.get("headline")),
                     "n": (row or {}).get("n"), "model": (row or {}).get("model"), "floor": (row or {}).get("floor"),
                     "twin": (row or {}).get("twin"), "ci_sep": (row or {}).get("sep"),
                     "how_well": how, "verdict": verdict, "trend": _trend_words(row, prow),
                     "fidelity_code": fcode, "fidelity": fwords, "stand_ins": bad, "organs": c["organs"]})
    order = {g: i for i, g in enumerate(spec["groups_order"])}
    caps.sort(key=lambda r: (order.get(r["group"], 99), not r["headline"], r["name"]))
    scored = [r for r in caps if r["model"] is not None]
    n_sep = sum(1 for r in scored if r["ci_sep"])
    st_counts = {}
    for s in statuses.values():
        st_counts[s] = st_counts.get(s, 0) + 1
    agg = cur.get("agg") or {}
    pr = problems()
    out = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "last_full_check": cur.get("ts"), "previous_full_check": prev.get("ts"), "n_full_checks": len(trend),
        "overall": {"n_abilities_scored": len(scored), "n_clearly_better": n_sep,
                    "n_not_better": sum(1 for r in scored if r["floor"] is not None and r["model"] <= r["floor"]),
                    "headline_pooled": agg.get("model"), "headline_pooled_floor": agg.get("floor"),
                    "headline_n_items": agg.get("n")},
        "fidelity": {"organs_total": sum(st_counts.values()), "pinned": st_counts.get("BF", 0),
                     "brain_model": st_counts.get("BF_SPIRIT", 0), "stand_ins": st_counts.get("NOT_BF", 0),
                     "stand_in_organs": sorted(o for o, s in statuses.items() if s == "NOT_BF"),
                     "abilities_with_a_stand_in": [r["name"] for r in caps if r["stand_ins"]]},
        "capabilities": caps, "problems": pr, "questions_for_owner": board_open(), "sections": hand_sections(),
    }
    return out


def render_auto_table(sc: dict) -> str:
    lines = [AUTO_BEGIN, "", "Last full check: %s (%d on record). Generated %s." % (sc["last_full_check"], sc["n_full_checks"], sc["generated"]), "",
             "| Ability | Group | How well | Compared with a simple rule | Since the previous check | Brain-faithful? |", "|---|---|---|---|---|---|"]
    for r in sc["capabilities"]:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (r["name"], r["group"], r["how_well"], r["verdict"], r["trend"], r["fidelity"]))
    f = sc["fidelity"]
    lines += ["", "Brain-faithfulness of the %d building blocks: %d copy the brain's math exactly, %d are brain models with open details, %d are stand-ins being replaced (%s)."
              % (f["organs_total"], f["pinned"], f["brain_model"], f["stand_ins"], ", ".join(f["stand_in_organs"]) or "none"), "", AUTO_END]
    return "\n".join(lines)


def write_outputs(sc: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sc, indent=1, default=str), encoding="utf-8")
    if DOC.is_file():
        txt = DOC.read_text(encoding="utf-8")
        table = render_auto_table(sc)
        if AUTO_BEGIN in txt and AUTO_END in txt:
            pre = txt.split(AUTO_BEGIN)[0]
            post = txt.split(AUTO_END, 1)[1]
            txt = pre + table + post
        else:
            txt = txt.rstrip("\n") + "\n\n" + table + "\n"
        DOC.write_text(txt, encoding="utf-8", newline="\n")


def plain_summary(sc: dict) -> str:
    o, f = sc["overall"], sc["fidelity"]
    return ("%d abilities scored in the last full check; %d are clearly better than a simple rule, %d are not better yet. "
            "Pooled headline score %s (simple rule %s). Building blocks: %d copy the brain's math, %d are brain models, %d are stand-ins. "
            "%d problems open for the fleet, %d awaiting your review, %d waiting to be folded in, %d questions for you."
            % (o["n_abilities_scored"], o["n_clearly_better"], o["n_not_better"], o["headline_pooled"], o["headline_pooled_floor"],
               f["pinned"], f["brain_model"], f["stand_ins"], len(sc["problems"]["open"]), len(sc["problems"]["in_review"]),
               len(sc["problems"]["waiting_to_fold_in"]), len(sc["questions_for_owner"])))


def main(argv=None) -> int:
    sc = build()
    write_outputs(sc)
    print(plain_summary(sc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
