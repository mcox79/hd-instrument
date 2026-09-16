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
LEDGER = REPO / "notes" / "INTEGRATION_LEDGER.md"
STATUS_MD = REPO / "notes" / "STATUS.md"
BOARD_METRICS_GLOB = "data/exp_situation_model_qa_modern_v1*/metrics.json"
AUTO_BEGIN, AUTO_END = "<!-- AUTO:BEGIN (written by tools/scorecard.py; edit the sections ABOVE, not this) -->", "<!-- AUTO:END -->"

# ---------------------------------------------------------------------------------------------------------
# RESOLUTION EXPANSION (owner 2026-09-15: "more resolution on which parts are performing well and which
# aren't; it's very hard to understand what you're working on"). Three extra sections built straight from
# disk (the same sources named above), degrading gracefully whenever a field is missing:
#   1. THE PRODUCT, QUESTION BY QUESTION  -- one row per board question, the READER'S OWN read of plain text.
#   2. THE READING CHAIN, RUNG BY RUNG    -- one row per stage a passage passes through, in order.
#   3. WHAT STRATEGY IS DOING NOW         -- a plain digest of notes/STATUS.md's live front.
# ---------------------------------------------------------------------------------------------------------

PRODUCT_DIMS = ["coref", "common_noun_coref", "salience", "who_did_what_agent", "who_did_what_patient", "state", "wic"]
PRODUCT_FLAVOR = "reader_textonly"   # "the reader's own read of the raw text alone" -- the headline provenance

# plain phrase(s) a PROBLEM.md or ledger line uses when it is working on this board question (owner-given map)
DIM_KEYWORDS = {
    "coref": ["pronoun"], "common_noun_coref": ["common noun", "commonnoun", "common-noun"],
    "salience": ["main character", "salience"], "who_did_what_agent": ["who did it", "who-did-what", "agent"],
    "who_did_what_patient": ["acted on", "patient", "undergoer"],
    "state": ["what things are like", "copular", "predicational", "state read"],
    "wic": ["word sense", "wic", "sense selection"],
}

FLOOR_WORDS = {
    "first_introduced_entity": "whichever character showed up first", "string_identity": "the same exact word as before",
    "recency": "whichever thing was mentioned most recently", "positional_nearest_preverbal": "the nearest word before the verb",
    "positional_nearest_postverbal": "the nearest word after the verb", "most_recent_noun": "the most recently mentioned noun",
    "majority": "always guessing the most common answer", "sense_blind_reader_majority": "always guessing the most common word sense",
    "deployed_position_readout": "the word's position in the sentence", "separate": "treating every mention as a brand-new thing",
}

# the 13 rungs a passage passes through, in order, each with the one organ file that does the work
CHAIN_RUNGS = [
    {"name": "Tokens & case", "what": "splits the raw text into words and keeps capital letters",
     "organ": "hdlab/scene_segment.py", "keys": ["scene_segment", "keeps capital letters"]},
    {"name": "Word categories", "what": "settles each word's part of speech (noun, verb, name...) as it is read",
     "organ": "hdlab/lexical_categories.py", "keys": ["lexical_categories", "categories rung", "category organ", "word-category organ"]},
    {"name": "Word attachment (heads)", "what": "decides which word each word depends on (the sentence's structure)",
     "organ": "hdlab/attachment_arm.py", "keys": ["attachment_arm", "heads rung", "word-attachment organ", "the governor", "word-governor"]},
    {"name": "Grammatical roles", "what": "decides who is the subject, object or agent of each clause",
     "organ": "hdlab/graded_role_assigner.py", "keys": ["graded_role_assigner", "roles rung", "role competition", "who-was-acted-on organ"]},
    {"name": "Mention discovery", "what": "finds pronouns and noun phrases and opens a target for each one",
     "organ": "hdlab/coref.py", "keys": ["coref.py", "pronoun-picker", "pronoun targets"]},
    {"name": "Entity files (who is who)", "what": "keeps one running file per person or thing in the story",
     "organ": "hdlab/online_entity_cluster.py", "keys": ["online_entity_cluster", "entity layer", "entity clusters", "entity files"]},
    {"name": "Events", "what": "records who did what to whom as a structured event",
     "organ": "hdlab/event_bundle.py", "keys": ["event_bundle", "predicate_detector", "predicate rescue", "event recall"]},
    {"name": "States", "what": "tracks what things are like, and when that stops being true",
     "organ": "hdlab/state_register.py", "keys": ["state_register", "entity_states", "copular", "state read"]},
    {"name": "Time", "what": "works out the order events happened in",
     "organ": "hdlab/temporal_model.py", "keys": ["temporal_model", "temporal_ordering", "tense tagger", "time-ordering"]},
    {"name": "Goals", "what": "tracks what a character is trying to do and whether events help or block it",
     "organ": "hdlab/goal_achievement.py", "keys": ["goal_achievement", "goal_hierarchy_graph", "goal register"]},
    {"name": "Belief", "what": "tracks what a character believes, even when it is false",
     "organ": "hdlab/belief_reader.py", "keys": ["belief_reader", "belief_timeline", "belief_partition"]},
    {"name": "Causes", "what": "works out why something happened and what it led to",
     "organ": "hdlab/causation_typing.py", "keys": ["causation_typing", "causal_reasoner", "force_dynamics", "force-dynamic"]},
    {"name": "Word senses", "what": "picks which meaning of a word is meant from the sentence it is in",
     "organ": "hdlab/grounded_semantic_graph.py", "keys": ["grounded_semantic_graph", "select_sense", "word-sense", "sense selection"]},
]

CHAIN_FIDELITY_WORDS = {"BF": "BF (copies the brain's math)", "BF_SPIRIT": "in the brain's spirit; some details still open",
                        "NOT_BF": "NOT yet -- a stand-in we are replacing", "MIXED": "in the brain's spirit; one part is a stand-in"}

_DATE_RE = re.compile(r"20\d\d-\d\d-\d\d(?:[ T]\d\d:\d\d(?::\d\d)?)?")
_PRI_RE = re.compile(r"\bpri[- ]?(\d+)\b", re.I)
_FIGURE_RE = re.compile(r"\d+\.\d+\s*(?:->|\u2192)\s*\d+\.\d+|\d+\s*(?:->|\u2192)\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*in\s*100")
_LOSS_WORDS = ("loss", "gap", "wall", "collapsed", "regress", "dip", "down", "deficit", "residual", "refuted", "blind", "silent")

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


_LEDGER_LINES: list[str] | None = None
_PROBLEM_BODIES: list[tuple[str, str, str, str]] | None = None


def _ledger_lines() -> list[str]:
    global _LEDGER_LINES
    if _LEDGER_LINES is None:
        _LEDGER_LINES = [ln for ln in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()] \
            if LEDGER.is_file() else []
    return _LEDGER_LINES


def _find_all(haystack: str, needle: str) -> list[int]:
    out, i = [], haystack.find(needle)
    while i != -1:
        out.append(i)
        i = haystack.find(needle, i + 1)
    return out


def organ_ledger_row(keys: list[str]) -> dict | None:
    """The ledger's most-recent line mentioning any of `keys` (case-insensitive substrings), or None if never
    mentioned. 'Most recent' = the latest YYYY-MM-DD[ HH:MM] date found anywhere in a matching line. Ledger
    lines can be very long and cover several organs at once, so the figure/pri are read from a WINDOW around
    the keyword hit (not the whole line) to avoid attributing a neighbour's number to this organ."""
    best: tuple[str, str, list[int]] | None = None
    for ln in _ledger_lines():
        low = ln.lower()
        hits = sorted(set(i for k in keys for i in _find_all(low, k.lower())))
        if not hits:
            continue
        m = _DATE_RE.search(ln)
        date = m.group(0) if m else ""
        if best is None or date > best[0]:
            best = (date, ln, hits)
    if best is None:
        return None
    date, ln, hits = best
    # the organ's own number must be NEAR one of its keyword mentions -- a huge ledger line often names several
    # organs, so a whole-line search would misattribute a neighbour's figure; try each mention in order.
    window = ""
    for hit in hits:
        w = ln[max(0, hit - 80):hit + 350]
        if _FIGURE_RE.search(w):
            window = w
            break
    pri_m = _PRI_RE.search(window) or _PRI_RE.search(ln)
    figs = _FIGURE_RE.findall(window)
    return {"date": date or None, "pri": pri_m.group(1) if pri_m else None, "line": ln.strip(" |"),
            "figure": figs[-1] if figs else None, "ci_sep": "CI-sep" in window,
            "loss": any(w in window.lower() for w in _LOSS_WORDS)}


def organ_health(row: dict | None) -> str:
    """strong / improving / weak / unmeasured -- see the module docstring's build() spec for the rule."""
    if row is None:
        return "unmeasured"
    if row.get("ci_sep"):
        return "strong"
    d = row.get("date") or ""
    try:
        dt = datetime.fromisoformat(d[:10])
        if (datetime.now() - dt).days <= 7:
            return "improving"
    except Exception:
        pass
    if row.get("loss"):
        return "weak"
    return "unmeasured"


def _problem_bodies() -> list[tuple[str, str, str, str]]:
    """[(slug, priority, title, lowercased full text)] for OPEN problems only (mirrors problems()'s own filter)."""
    global _PROBLEM_BODIES
    if _PROBLEM_BODIES is not None:
        return _PROBLEM_BODIES
    out = []
    if PROBLEMS.is_dir():
        for d in sorted(PROBLEMS.iterdir()):
            pm = d / "PROBLEM.md"
            if not pm.is_file() or (d / "SOLVED.md").is_file():
                continue
            fm = _frontmatter(pm)
            if fm.get("status", "").upper() != "OPEN":
                continue
            try:
                txt = pm.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                txt = ""
            title = re.sub(r"\s+", " ", fm.get("_title", d.name))[:160]
            out.append((d.name, fm.get("priority") or "", title, txt.lower()))
    _PROBLEM_BODIES = out
    return out


def _short_title(title: str, n: int = 60) -> str:
    title = title.split(":", 1)[-1].strip() if title.upper().startswith("PROBLEM:") else title
    title = title.replace("`", "'").replace("|", "/")
    return title[:n].rsplit(" ", 1)[0] + "..." if len(title) > n else title


def open_problems_matching(keys: list[str]) -> list[dict]:
    keys = [k.lower() for k in keys]
    out = [{"slug": slug, "priority": pri, "title": title} for slug, pri, title, low in _problem_bodies()
           if any(k in low for k in keys)]
    out.sort(key=lambda r: int(r["priority"]) if str(r["priority"]).isdigit() else 999)
    return out


def _all_board_metrics_files() -> list[Path]:
    return sorted(REPO.glob(BOARD_METRICS_GLOB))


def load_product_metrics(trend_rows: list[dict] | None = None) -> tuple[dict | None, str | None]:
    """(metrics dict, ts) for the newest FULL board run whose per_dimension_reader_driven is populated -- found
    by matching BOARD_TREND's dims_reader (one row per full run) back to its source metrics.json by ts_iso.
    A run can fail to build reader-driven rows (fallback to the component number); this skips those and falls
    back to the last run that succeeded, so the product section stays populated even when the newest run didn't."""
    trend_rows = _jsonl(TREND) if trend_rows is None else trend_rows
    files = _all_board_metrics_files()
    for row in reversed(trend_rows):
        dr = row.get("dims_reader") or {}
        if not any(dr.values()):
            continue
        ts = row.get("ts")
        for f in files:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if d.get("ts_iso") == ts and (d.get("per_dimension_reader_driven") or {}).get(PRODUCT_FLAVOR):
                return d, ts
    return None, None


def _reason_not_measured(row: dict | None, metrics: dict | None) -> str:
    if row is None:
        return "no reader-driven run recorded yet"
    n = row.get("n") or 0
    if n:
        return ""
    try:
        gd = ((metrics or {}).get("reader_driven_detail") or {}).get("gum_detail") or {}
        per_doc = (gd.get("per_doc") or {}).get(PRODUCT_FLAVOR) or (gd.get("per_doc") or {}).get("reader_annotated") or []
        if any(doc.get("coref_aligned") is False for doc in per_doc):
            return "0 items scored this run -- the scorer's own matching does not yet line up with the reader's own column"
    except Exception:
        pass
    return "0 items scored this run in the reader's own population"


def _verdict_reader(model_acc, floor) -> str:
    if model_acc is None or floor is None:
        return "not measured"
    if model_acc >= floor:
        return "WINS clearly" if abs(model_acc - floor) > 0.02 else "roughly level"
    return "LOSES to the rule" if abs(model_acc - floor) > 0.02 else "roughly level"


def build_product_rows(metrics: dict | None, product_ts: str | None, trend_rows: list[dict]) -> list[dict]:
    """THE PRODUCT, QUESTION BY QUESTION -- one row per board question, the reader's own read of plain text."""
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    prow_idx = next((i for i, r in enumerate(trend_rows) if r.get("ts") == product_ts), None)
    rows = []
    for key in PRODUCT_DIMS:
        cap = spec["capabilities"].get(key, {})
        question = cap.get("name", key)
        organs = cap.get("organs", [])
        row = ((metrics or {}).get("per_dimension_reader_driven") or {}).get(PRODUCT_FLAVOR, {}).get(key)
        component = ((metrics or {}).get("per_dimension") or {}).get(key)
        n = (row or {}).get("n") or 0
        model_acc = (row or {}).get("model_acc")
        if row is None or n == 0 or model_acc is None:
            verdict, reason = "NOT MEASURED YET", _reason_not_measured(row, metrics)
            reader_txt, rule_txt, twin_txt = "not measured on this run", "-", "-"
        else:
            floor = row.get("strongest_floor")
            reason = ""
            verdict = _verdict_reader(model_acc, floor)
            reader_txt = "right %s (%d item%s tested)" % (_pct(model_acc), n, "" if n == 1 else "s")
            ar = row.get("answered_rate")
            if ar is not None:
                reader_txt += "; of the %d asked, %d answered" % (n, round(n * float(ar)))
            fname = row.get("strongest_floor_name")
            rule_txt = "%s (%s)" % (_pct(floor), FLOOR_WORDS.get(fname, (fname or "-").replace("_", " "))) if floor is not None else "-"
            twin_txt = _pct(row.get("twin_acc"))
        # trend vs the previous full run that scored this same reader flavor+dim
        trend_txt = "first measurement"
        if prow_idx is not None:
            dkey = "%s.%s" % (PRODUCT_FLAVOR, key)
            cur_t = (trend_rows[prow_idx].get("dims_reader") or {}).get(dkey)
            prev_t = None
            for j in range(prow_idx - 1, -1, -1):
                prev_t = (trend_rows[j].get("dims_reader") or {}).get(dkey)
                if prev_t:
                    break
            trend_txt = _trend_words(cur_t, prev_t) if cur_t else ("-" if row is not None else "first measurement")
        comp_txt = "parts given answer-key spans: %s" % _pct(component.get("model_acc")) if component and component.get("model_acc") is not None else "not available"
        landed = organ_ledger_row(DIM_KEYWORDS.get(key, []) + organs)
        matches = open_problems_matching(DIM_KEYWORDS.get(key, []) + organs)
        worked = ["pri %s (%s)" % (p["priority"], _short_title(p["title"])) for p in matches[:5]]
        if len(matches) > 5:
            worked.append("+%d more open" % (len(matches) - 5))
        if landed and landed.get("pri"):
            worked.append("pri %s landed %s" % (landed["pri"], (landed.get("date") or "-")[:10]))
        rows.append({"key": key, "question": question, "reader": reader_txt, "rule": rule_txt, "twin": twin_txt,
                     "verdict": verdict, "reason": reason, "trend": trend_txt, "component": comp_txt,
                     "worked_on_by": worked or ["nothing open on record"]})
    return rows


def build_chain_rows() -> list[dict]:
    """THE READING CHAIN, RUNG BY RUNG -- one row per stage a passage passes through, in order."""
    statuses = registry_statuses()
    rows = []
    for rung in CHAIN_RUNGS:
        organ_key = rung["organ"].split("/")[-1][:-3]
        fcode, _, _ = fidelity_for([organ_key], statuses)
        landed = organ_ledger_row(rung["keys"])
        matches = open_problems_matching(rung["keys"] + [organ_key])
        open_pri = sorted({int(p["priority"]) for p in matches if str(p["priority"]).isdigit()})
        open_txt = ", ".join("pri %d" % p for p in open_pri[:8]) + ("; +%d more" % (len(open_pri) - 8) if len(open_pri) > 8 else "") if open_pri else "none open"
        rows.append({
            "name": rung["name"], "what": rung["what"], "organ": rung["organ"],
            "bf_status": CHAIN_FIDELITY_WORDS.get(fcode, "not yet checked"),
            "instrument": (landed.get("figure") if landed else None) or "no instrument on record",
            "last_landing": ("%s (pri %s)" % (landed["date"][:10], landed["pri"]) if landed and landed.get("date") and landed.get("pri")
                              else (landed["date"][:10] if landed and landed.get("date") else "no landing on record")),
            "open_problems": open_txt,
            "health": organ_health(landed),
        })
    return rows


def _split_top_level(text: str, sep: str) -> list[str]:
    """Split on `sep`, but never inside ( ) -- a ledger clause like 'diff (463 files; discovery gate)' must
    stay one item."""
    parts, buf, depth = [], [], 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            parts.append("".join(buf)); buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return parts


def strategy_now() -> dict:
    """WHAT STRATEGY IS DOING NOW -- a plain digest of notes/STATUS.md's live front."""
    out = {"summary": "", "running": [], "queue": []}
    if not STATUS_MD.is_file():
        return out
    try:
        txt = STATUS_MD.read_text(encoding="utf-8", errors="ignore")
        blocks = [b.strip() for b in re.split(r"\n\s*\n", txt) if b.strip()]
        body = [b for b in blocks if not b.startswith("# STATUS") and not b.startswith("**LOCATED")]
        first = body[0] if body else (blocks[0] if blocks else "")
        out["summary"] = re.sub(r"\s+", " ", first)[:600]
        scan = " ".join(body[:3])
        out["running"] = sorted(set(re.findall(r"solver_pri\d+", scan)))
        qmatches = re.findall(r"QUEUE[^:]{0,40}:([^.]{5,240})\.", scan, re.I)
        items: list[str] = []
        for q in qmatches:
            for part in _split_top_level(q, ";"):
                part = part.strip(" .")
                if part:
                    items.append(part)
        mapped = []
        for it in items[:3]:
            low = it.lower()
            target = next((dk for dk, kws in DIM_KEYWORDS.items() if any(k in low for k in kws)), None)
            if target is None:
                target = next((r["name"] for r in CHAIN_RUNGS if any(k.lower() in low for k in r["keys"])), "-")
            mapped.append({"item": it, "targets": target})
        out["queue"] = mapped
    except Exception as e:
        out["summary"] = "(could not read notes/STATUS.md: %s)" % e
    return out


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
    product_metrics, product_ts = load_product_metrics(trend)
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
        "product_rows": build_product_rows(product_metrics, product_ts, trend),
        "chain_rows": build_chain_rows(), "strategy_now": strategy_now(),
    }
    return out


def render_product_section(rows: list[dict]) -> list[str]:
    out = ["### THE PRODUCT, QUESTION BY QUESTION", "",
           "The reader's own read of plain text (no answer key), one row per board question.", "",
           "| Question | Reader on plain text | Best simple rule | Random twin | Verdict | Since last check | Parts given answer-key spans | Worked on by |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        verdict = r["verdict"] + (" (%s)" % r["reason"] if r["reason"] else "")
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["question"], r["reader"], r["rule"], r["twin"], verdict, r["trend"], r["component"], "; ".join(r["worked_on_by"])))
    out.append("")
    return out


def render_chain_section(rows: list[dict]) -> list[str]:
    out = ["### THE READING CHAIN, RUNG BY RUNG", "",
           "One row per stage a passage passes through, in order.", "",
           "| Stage | What it does | Module | Brain-faithful? | Its own instrument | Last landing | Open problems | Health |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append("| %s | %s | *%s* | %s | %s | %s | %s | %s |" % (
            r["name"], r["what"], r["organ"], r["bf_status"], r["instrument"], r["last_landing"], r["open_problems"], r["health"]))
    out.append("")
    return out


def render_strategy_section(strat: dict) -> list[str]:
    out = ["### WHAT STRATEGY IS DOING NOW", ""]
    out.append(strat.get("summary") or "(nothing recorded)")
    out.append("")
    running = strat.get("running") or []
    out.append("**Running now:** " + (", ".join(running) if running else "nothing recorded as running"))
    q = strat.get("queue") or []
    if q:
        out.append("")
        out.append("**Next in the queue:**")
        for item in q:
            out.append("- %s -- targets: %s" % (item["item"], item["targets"]))
    out.append("")
    return out


def render_auto_table(sc: dict) -> str:
    lines = [AUTO_BEGIN, "", "Last full check: %s (%d on record). Generated %s." % (sc["last_full_check"], sc["n_full_checks"], sc["generated"]), ""]
    lines += render_product_section(sc.get("product_rows") or [])
    lines += render_chain_section(sc.get("chain_rows") or [])
    lines += render_strategy_section(sc.get("strategy_now") or {})
    lines += ["### EVERY ABILITY, MEASURED", "",
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
