#!/usr/bin/env python
"""THE PLAN, PARSED LIVE -- collector for the WHERE WE ARE panel of `tools/status_gui.py`.

WHY THIS EXISTS (owner, 2026-08-16): *"can you add your plan to that, and make sure you keep all
this updated? Also feel free to optimize all the content so it's better organized and actionable,
and easier to keep updated."*

THE DEFECT BEING FIXED IS TRANSCRIPTION. `notes/progress_ledger.json` carried a hand-copy of each
phase's state, gate and kill condition. A hand-copy of a living plan is stale the moment the plan
moves, and the plan moved three times on 2026-08-16 alone. So this module PARSES
`notes/LONG_TERM_PLAN.md` section 5 and `notes/PLAN.md` section 9 on EVERY REFRESH. Nothing here is
a stored copy of a sentence that exists in those files.

WHAT IT COLLECTS
  * the five (six, counting PHASE 0) phases: goal, GATE, STOP-IF, status, the work items
  * WHICH PHASE WE ARE IN, and THE SINGLE NEXT ACTION, both derived and both showing their basis
  * the owner's standing decisions: D1..Dn parsed live out of `notes/PLAN.md` section 9
  * a PARSER-CONTRACT CHECK -- see below, it is the whole point of job 2

THE PARSER CONTRACT, AND WHY IT IS CHECKED ON SCREEN
CLAUDE.md: *"a doc parsed by code is coupled to it -- mark both sides"*. On 2026-08-13 a reword of
two literals in `notes/STATUS.md` silently degraded EVERY compaction recovery for days, because the
parser substituted a placeholder that read like ordinary output. This module refuses to repeat that:
every literal it depends on is listed in `REQUIRED_*` below, checked against the file on every
refresh, and any absence is COUNTED and RENDERED as a contract violation with the literal named.
A phase with no `**Gate:**` line shows GATE: NOT STATED IN THE PLAN -- never a blank, never an
invented gate, and never a remembered one.
Doc-side record of the same coupling: `notes/LONG_TERM_PLAN_PARSER_CONTRACT.md`.
(`notes/LONG_TERM_PLAN.md` is Director-owned and was NOT edited by this module's author; the
contract note names the one line the Director should add to it. Until then the contract lives in one
file rather than two, and that gap is itself reported by `contract()` as OWNED_ELSEWHERE.)

THE CONVENTION THIS PARSER PREFERS, IN FULL (all of it OPTIONAL -- the parser degrades gracefully):

    ### PHASE <n> - <TITLE> *(<free text; may contain a status word>)*
    **Status:** DONE | IN PROGRESS | BLOCKED | NOT STARTED     <- wins over the aside if present
    **Goal:** one plain sentence                               <- wins over the first paragraph
    **Brain structure:** ...
    **The work:** ... (a numbered list; a ~~struck-through~~ item is read as RETRACTED and skipped)
    **Gate:** what would count as success
    **Kill condition:** what would make us stop

Precedence for STATUS: an explicit `**Status:**` line, else a keyword in the heading aside, else
NOT STATED. NOT STATED is reported as a gap, not guessed at.

  python tools/status_plan.py                # human-readable dump
  python tools/status_plan.py --json
  python tools/status_plan.py --self-test    # runs with every required file ABSENT
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# --- paths. Env-overridable so the self-test can point every one at nowhere. ------------------
LONG_PLAN_DOC = Path(os.environ.get("HD_LONG_PLAN_DOC")
                     or (REPO / "notes" / "LONG_TERM_PLAN.md"))
NEAR_PLAN_DOC = Path(os.environ.get("HD_PLAN_DOC") or (REPO / "notes" / "PLAN.md"))
OPERATOR_SPEC = Path(os.environ.get("HD_OPERATOR_SPEC")
                     or (REPO / "notes" / "operator_decisions.json"))
CONTRACT_DOC = Path(os.environ.get("HD_PLAN_CONTRACT")
                    or (REPO / "notes" / "LONG_TERM_PLAN_PARSER_CONTRACT.md"))
# The corpus a transcribed operator-decision row's `verify` literals are checked against.
AUTHORITY_DOCS = [
    Path(os.environ.get("HD_STATUS_DOC") or (REPO / "notes" / "STATUS.md")),
    Path(os.environ.get("HD_LESSONS_DOC") or (REPO / "notes" / "STATUS_LESSONS.md")),
    Path(os.environ.get("HD_STATUS_SPEC_DOC") or (REPO / "notes" / "STATUS_SPEC.md")),
    NEAR_PLAN_DOC,
    LONG_PLAN_DOC,
]

MAX_DOC_BYTES = 4_000_000

# --- THE CONTRACT. Every literal this parser depends on, named so a reword is visible. --------
#
# THE SECTION LITERALS ARE THE NUMBERS, NOT THE TITLES, and that is deliberate. The parser finds
# section 5 by `## 5.` and section 7 by `## 7.`, so the Director may reword either TITLE freely and
# nothing breaks -- a contract that fires on a harmless reword trains its reader to ignore it, which
# is worse than no contract. What the parser genuinely cannot survive is the section being
# RENUMBERED or removed, and that is exactly what these two literals catch.
REQUIRED_SECTIONS = ("## 5.", "## 7.")
EXPECTED_SECTION_TITLES = {"## 5.": "## 5. THE PLAN",
                           "## 7.": "## 7. HOW WE WILL KNOW IT IS WORKING"}
REQUIRED_PHASE_LABELS = ("Gate:", "Kill condition:")
OPTIONAL_PHASE_LABELS = ("Status:", "Goal:", "Brain structure:", "The work:",
                         "Where it stands:", "The problem in one line:")
DECISIONS_SECTION = "## 9. DECISIONS FOR THE OWNER"
DECISION_DEFAULT_LABEL = "Recommended default:"

# Status words looked for in the heading aside, most specific first. The mapping is stated here
# rather than buried in a branch so that it can be read, argued with, and changed in one place.
_STATUS_FROM_ASIDE = (
    ("blocked", "BLOCKED"),
    ("start here", "IN PROGRESS"),
    ("current", "IN PROGRESS"),
    ("in progress", "IN PROGRESS"),
    ("running", "IN PROGRESS"),
    ("not started", "NOT STARTED"),
    ("long horizon", "NOT STARTED"),
    ("done", "DONE"),
)
_STATUS_VALUES = ("DONE", "IN PROGRESS", "BLOCKED", "NOT STARTED", "NOT STATED")

_DASHES = ("‐", "‑", "‒", "–", "—", "―", "−")


def _norm_dashes(s: str) -> str:
    """Every dash-like character becomes '-'. Duplicated from status_state/status_organs on
    purpose: those modules import this one's siblings and a cross-import would be circular. It is
    a five-line text primitive, not a source of truth."""
    if not s:
        return ""
    for ch in _DASHES:
        s = s.replace(ch, "-")
    return s


def _norm_corpus(s: str) -> str:
    """Normalise a document (or a literal) for the drift check.

    Dashes to '-', markdown emphasis and code fences removed, ALL whitespace collapsed to single
    spaces. The last part is not cosmetic and it is why this differs from the sibling collectors'
    check: the sentence naming the four blocked cells is `**Blocked, and it is an operator
    decision:** 4` at the end of one line and `cells cannot be dispatched...` at the start of the
    next, so a literal quoting the COUNT can only be checked once the line break is collapsed.
    This loosens typography and nothing else -- a changed NUMBER still fails, which is the whole
    job."""
    s = _norm_dashes(s or "")
    s = s.replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


def _read_text(path: Path) -> str | None:
    """Read a document, or None. Never raises; never pulls an absurd file in whole."""
    try:
        if path.stat().st_size > MAX_DOC_BYTES:
            return path.read_text(encoding="utf-8", errors="replace")[:MAX_DOC_BYTES]
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _strip_md(s: str) -> str:
    """Plain text out of markdown, for a table cell.

    UNDERSCORES ARE NOT STRIPPED, and that is a bug fix, not an oversight: this document is full of
    arm keys and identifiers like `K1_OWN_NORMS` and `max(orthographic, frequency, scramble)`, and
    treating `_` as emphasis rendered that arm name as `K1OWNNORMS` on screen -- a mangled
    identifier the reader cannot look up. Underscore emphasis is not used in these documents;
    identifiers are."""
    s = re.sub(r"`([^`]*)`", r"\1", s or "")
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*~]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _first_sentence(s: str, cap: int = 240) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    m = re.search(r"(?<=[.!?])\s", s)
    out = s[: m.start() + 1] if m else s
    return out if len(out) <= cap else out[: cap - 3] + "..."


_PHASE_HEAD = re.compile(r"^###\s+(PHASE\s+\d+)\s*[-:]\s*(.+?)\s*$")
_LABEL = re.compile(r"^\*\*([A-Z][A-Za-z' ]{1,40}:)\*\*\s*(.*)$")
_SECTION_ANY = re.compile(r"^##\s+\d+\.\s")
_PLAN_SECTION5 = re.compile(r"^##\s+5\.\s")
_PLAN_SECTION7 = re.compile(r"^##\s+7\.\s")
_LIST_ITEM = re.compile(r"^\s*(\d+)\.\s+(.*)$")


def parse_success_ladder(text: str) -> list[dict]:
    """Section 7 -- the ordered list of things that would each count as this working.

    Rendered beside the phases because it is the only place the plan says, in order, what a WIN
    would look like, and it tags each rung with the phase that produces it. Parsed, not
    transcribed, for the same reason as everything else here."""
    out: list[dict] = []
    if not text:
        return out
    in7 = False
    for raw in _norm_dashes(text).splitlines():
        if _PLAN_SECTION7.match(raw):
            in7 = True
            continue
        if in7 and _SECTION_ANY.match(raw) and not _PLAN_SECTION7.match(raw):
            break
        if not in7:
            continue
        m = _LIST_ITEM.match(raw)
        if m:
            out.append({"n": m.group(1), "_raw": m.group(2)})
            continue
        # Continuation. Without this the fifth rung reads "passive, relative, coreference," and
        # stops mid-clause -- a truncated success criterion is worse than none.
        if out and raw.startswith((" ", "\t")) and raw.strip() and not raw.strip().startswith("#"):
            out[-1]["_raw"] += " " + raw.strip()
    for r in out:
        body = r.pop("_raw")
        ph = re.search(r"\*\(([^)]*Phase[^)]*)\)\*", body)
        r["text"] = _strip_md(re.sub(r"\*\([^)]*\)\*", "", body)).strip()
        r["phase"] = _strip_md(ph.group(1)) if ph else ""
    return out


# ---------------------------------------------------------------------------
# THE PHASES -- parsed live out of notes/LONG_TERM_PLAN.md section 5
# ---------------------------------------------------------------------------

def parse_phases(text: str) -> list[dict]:
    """Pull every phase out of section 5. Returns [] on anything unrecognised -- never a guess.

    The document's shape is stable and self-describing: `## 5.` opens the section, `### PHASE n -
    TITLE *(aside)*` opens a phase, `**Label:**` opens a field that runs until the next label, the
    next phase or the next section. Continuation lines are folded in so a gate wrapped over three
    lines is read whole.
    """
    out: list[dict] = []
    if not text:
        return out
    lines = _norm_dashes(text).splitlines()
    in5 = False
    cur: dict | None = None
    label: str | None = None

    def _close() -> None:
        nonlocal cur, label
        if cur is not None:
            for k, v in list(cur["fields"].items()):
                cur["fields"][k] = re.sub(r"\s+", " ", v).strip()
            out.append(cur)
        cur, label = None, None

    for raw in lines:
        if _PLAN_SECTION5.match(raw):
            in5 = True
            continue
        if in5 and _SECTION_ANY.match(raw) and not _PLAN_SECTION5.match(raw):
            break
        if not in5:
            continue
        h = _PHASE_HEAD.match(raw.strip())
        if h:
            _close()
            title = h.group(2).strip()
            aside = ""
            m = re.search(r"\*\(([^)]*)\)\*\s*$", title)
            if m:
                aside = m.group(1).strip()
                title = title[: m.start()].strip()
            cur = {"id": re.sub(r"\s+", " ", h.group(1)).upper(),
                   "title": _strip_md(title), "aside": _strip_md(aside),
                   "fields": {}, "field_order": [], "body": []}
            continue
        if cur is None:
            continue
        f = _LABEL.match(raw.strip())
        if f:
            label = f.group(1).strip()
            cur["fields"][label] = f.group(2).strip()
            cur["field_order"].append(label)
            continue
        if raw.strip():
            if label:
                cur["fields"][label] = cur["fields"].get(label, "") + " " + raw.strip()
            elif not re.fullmatch(r"[-*_\s]{3,}", raw.strip()):
                # A markdown horizontal rule is not prose. Without this guard PHASE 3 and PHASE 4,
                # whose first content is a labelled line, had their GOAL cell render as "---".
                cur["body"].append(raw.strip())
        else:
            # A blank line ends a labelled run. Without this, the paragraph AFTER a field is
            # silently appended to it and a two-line gate becomes a four-paragraph gate.
            label = None
    _close()

    for p in out:
        _derive_phase(p)
    return out


def _work_items(blob: str) -> list[dict]:
    """Split a `**The work:**` field into items, marking struck-through ones RETRACTED.

    THE STRIKETHROUGH IS LOAD-BEARING, not formatting. PHASE 1 item 3 is `~~Reduce the lift
    cost.~~ RETRACTED -- this item was wrong and it was mine.` Reading it as the next action would
    send the reader at a retracted instruction, which is the single worst thing this panel could
    do."""
    items: list[dict] = []
    if not blob:
        return items
    raw = _norm_dashes(blob)
    # Numbered items inside a folded field: split on ` <n>. ` boundaries, keeping the number.
    parts = re.split(r"(?:(?<=^)|(?<=\s))(\d+)\.\s+", " " + raw.strip())
    if len(parts) >= 3:
        pairs = [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    else:
        pairs = [("", raw)]
    for num, body in pairs:
        struck = bool(re.search(r"~~.+?~~", body)) or "RETRACTED" in body.upper()[:200]
        items.append({
            "n": num or None,
            "text": _first_sentence(_strip_md(body), 300),
            "full": _strip_md(body),
            "retracted": struck,
        })
    return items


def _derive_phase(p: dict) -> None:
    """Turn raw fields into the columns the panel shows. Every derivation states its basis."""
    f = p["fields"]
    get = lambda k: _strip_md(f.get(k, ""))  # noqa: E731

    p["gate"] = get("Gate:")
    p["kill"] = get("Kill condition:")
    p["brain_structure"] = get("Brain structure:")
    p["where_it_stands"] = get("Where it stands:")
    p["work_raw"] = f.get("The work:", "")
    p["work"] = _work_items(p["work_raw"])

    # GOAL: the explicit label wins; else the phase's own one-line problem statement; else the
    # first free paragraph under the heading. Never invented -- MISSING if there is none.
    goal = get("Goal:") or get("The problem in one line:")
    if not goal and p["body"]:
        goal = _strip_md(" ".join(p["body"]))
    p["goal"] = _first_sentence(goal) if goal else ""
    p["goal_basis"] = ("**Goal:** line" if f.get("Goal:") else
                       "**The problem in one line:** line" if f.get("The problem in one line:")
                       else "the first paragraph under the heading" if p["body"] else "MISSING")

    # STATUS: explicit line > keyword in the heading aside > NOT STATED.
    explicit = get("Status:").upper().strip().rstrip(".")
    if explicit in _STATUS_VALUES:
        p["status"], p["status_basis"] = explicit, "the plan's own **Status:** line"
    else:
        aside = (p.get("aside") or "").lower()
        hit = next((v for k, v in _STATUS_FROM_ASIDE if k in aside), None)
        if hit:
            p["status"] = hit
            p["status_basis"] = f"the word '{next(k for k, v in _STATUS_FROM_ASIDE if k in aside)}'" \
                                f" in the heading note '{p.get('aside')}'"
        else:
            p["status"] = "NOT STATED"
            p["status_basis"] = ("the plan states no status for this phase, in the heading note or "
                                 "anywhere else -- this is a gap in the document, not a guess "
                                 "declined")
    # A phase marked DONE whose body still lists remaining work is reported as BOTH, never
    # flattened. Same discipline as the organ map's floored-and-untested rows. PHASE 0 is the live
    # case: its heading says "substantially done" and its body says "Remaining, and it blocks Phase
    # 3" -- and the body is where it says so, which is why the search covers the body and not only
    # the parsed labels.
    _blob = " ".join(f.keys()) + " " + " ".join(f.values()) + " " + " ".join(p.get("body") or [])
    if p["status"] == "DONE" and re.search(r"\bRemaining\b", _blob, re.I):
        p["status"] = "MOSTLY DONE"
        p["status_basis"] += "; but the phase body still lists REMAINING work, so it is not DONE"

    missing = [lab for lab in REQUIRED_PHASE_LABELS if lab not in f]
    p["missing_labels"] = missing
    p["contract_ok"] = not missing
    if not p["gate"]:
        p["gate"] = ""
    if not p["kill"]:
        p["kill"] = ""


def _next_action(phase: dict | None) -> dict:
    """The single next thing to do, and where it came from. Never invented."""
    if phase is None:
        return {"text": "", "basis": "no current phase could be identified", "source": None}
    live = [w for w in phase.get("work") or [] if not w.get("retracted")]
    if live:
        w = live[0]
        return {"text": w["text"], "full": w.get("full"),
                "basis": f"the first item of {phase['id']}'s **The work:** list that is not "
                         f"struck through",
                "source": f"notes/LONG_TERM_PLAN.md {phase['id']}"}
    if phase.get("gate"):
        return {"text": f"Get to the gate: {phase['gate']}", "full": phase["gate"],
                "basis": f"{phase['id']} lists no un-retracted work item, so its GATE is shown "
                         f"instead",
                "source": f"notes/LONG_TERM_PLAN.md {phase['id']}"}
    return {"text": "", "basis": f"{phase['id']} states neither work items nor a gate",
            "source": None}


# ---------------------------------------------------------------------------
# THE OWNER'S STANDING DECISIONS -- parsed live out of notes/PLAN.md section 9
# ---------------------------------------------------------------------------

_DECISION_HEAD = re.compile(r"^\*\*(D\d+)\s*[-:]\s*(.+?)\*\*\s*$")


def parse_decisions(text: str) -> list[dict]:
    """Every `**Dn - question?**` block in section 9, with its recommended default.

    Section 9's own preamble is the reason this is worth rendering: *"Each has a recommended
    default, so silence is safe -- if no answer comes, the default is what happens."* That makes
    every one of them a live decision sitting on the owner, whether or not anybody has asked."""
    out: list[dict] = []
    if not text:
        return out
    lines = _norm_dashes(text).splitlines()
    in9 = False
    cur: dict | None = None
    in_default = False
    for raw in lines:
        s = raw.strip()
        if s.upper().startswith(DECISIONS_SECTION.upper()):
            in9 = True
            continue
        if in9 and _SECTION_ANY.match(raw) and not s.upper().startswith(
                DECISIONS_SECTION.upper()):
            break
        if not in9:
            continue
        h = _DECISION_HEAD.match(s)
        if h:
            if cur:
                out.append(cur)
            cur = {"id": h.group(1), "question": _strip_md(h.group(2)), "why_lines": [],
                   "default": ""}
            in_default = False
            continue
        if cur is None:
            continue
        m = re.match(r"^\*\*" + DECISION_DEFAULT_LABEL + r"\s*(.+)$", s)
        if m:
            cur["default"] = _strip_md(m.group(1))
            in_default = True
            continue
        if not s:
            in_default = False
            continue
        # The recommended default wraps over several lines. Reading only the first produced
        # "HOLD. Do it only when no concurrent session is running and a backup of the" -- a
        # recommendation that stops mid-sentence is a recommendation the owner cannot act on.
        if in_default:
            cur["default"] = (cur["default"] + " " + _strip_md(s)).strip()
        else:
            cur["why_lines"].append(s)
    if cur:
        out.append(cur)
    for d in out:
        d["why"] = _first_sentence(_strip_md(" ".join(d.pop("why_lines"))), 400)
        if not d["default"]:
            d["default"] = ""
    return out


# ---------------------------------------------------------------------------
# the transcribed standing decisions that live in no parseable section
# ---------------------------------------------------------------------------

def _authority_corpus() -> tuple[str, list[str]]:
    parts, missing = [], []
    for p in AUTHORITY_DOCS:
        t = _read_text(p)
        if t is None:
            missing.append(p.name)
        else:
            parts.append(t)
    return _norm_corpus("\n".join(parts)), missing


def load_operator_decisions() -> dict:
    """Standing operator decisions that exist only as prose in `notes/STATUS_LESSONS.md` and
    `notes/STATUS.md`, transcribed with `verify` literals re-checked on every refresh.

    WHY A TRANSCRIPTION AND NOT A PARSE, stated so it is not mistaken for laziness: those two
    documents state these four decisions inside running prose with no repeated heading shape, so
    there is no literal to anchor a parse to. The established alternative in this window is a
    structured transcription whose every number must still be findable in its source -- so a
    reword surfaces as CHECK-SOURCE rather than as a stale number. If those documents ever grow a
    heading shape for these, replace this with a parse."""
    txt = _read_text(OPERATOR_SPEC)
    if txt is None:
        return {"status": "MISSING", "detail": f"not found: {OPERATOR_SPEC}", "rows": []}
    try:
        spec = json.loads(txt)
    except (json.JSONDecodeError, ValueError) as exc:
        return {"status": "ERROR",
                "detail": f"{OPERATOR_SPEC.name} unreadable ({type(exc).__name__}: {exc})",
                "rows": []}
    if not isinstance(spec, dict):
        return {"status": "ERROR", "detail": "operator_decisions.json is not an object",
                "rows": []}
    corpus, missing_docs = _authority_corpus()
    can_verify = bool(corpus)
    rows = []
    for r in spec.get("decisions") or []:
        if not isinstance(r, dict):
            continue
        row = dict(r)
        strings = [s for s in (row.get("verify") or []) if isinstance(s, str) and s]
        if not can_verify:
            row["verify_status"], row["verify_missing"] = "CANNOT_VERIFY", []
        elif not strings:
            row["verify_status"], row["verify_missing"] = "NO_VERIFY_STRINGS", []
        else:
            gone = [s for s in strings if _norm_corpus(s) not in corpus]
            row["verify_missing"] = gone
            row["verify_status"] = "CHECK_SOURCE" if gone else "VERIFIED"
        rows.append(row)
    return {"status": "OK", "rows": rows, "path": str(OPERATOR_SPEC),
            "authority_missing": missing_docs,
            "drifted": [r.get("title") for r in rows
                        if r.get("verify_status") == "CHECK_SOURCE"]}


# ---------------------------------------------------------------------------
# the contract check -- job 2, made visible
# ---------------------------------------------------------------------------

def contract(text: str | None, phases: list[dict], decisions: list[dict],
             ops: dict) -> dict:
    """Every coupling this module has to a human-edited document, checked on this refresh.

    A violation is COUNTED and NAMED. It is never repaired here and never papered over: the
    2026-08-13 incident was caused precisely by a parser that substituted a plausible-looking
    placeholder for a literal that had been reworded."""
    violations: list[dict] = []
    if text is None:
        return {"status": "CANNOT_CHECK",
                "detail": f"{LONG_PLAN_DOC} is not readable, so no literal can be checked. "
                          f"CANNOT_CHECK is not the same as VERIFIED.",
                "violations": [], "n_violations": 0, "doc_side_recorded": CONTRACT_DOC.is_file()}
    corpus = _norm_dashes(text)
    for lit in REQUIRED_SECTIONS:
        if lit not in corpus:
            violations.append({
                "kind": "SECTION_HEADING_GONE", "literal": lit,
                "detail": f"tools/status_plan.py finds this section by the literal '{lit}' "
                          f"(expected heading: '{EXPECTED_SECTION_TITLES.get(lit, lit)}'). The "
                          f"number is gone from {LONG_PLAN_DOC.name}, so the section has been "
                          f"renumbered or removed. The TITLE may be reworded freely; the NUMBER "
                          f"is an API."})
    if not phases:
        violations.append({
            "kind": "NO_PHASES_PARSED", "literal": "### PHASE <n> - <TITLE>",
            "detail": f"section 5 of {LONG_PLAN_DOC.name} yielded no phase headings. Either the "
                      f"heading shape changed or the section moved."})
    for p in phases:
        for lab in p.get("missing_labels") or []:
            violations.append({
                "kind": "PHASE_LABEL_MISSING", "literal": f"**{lab}**", "phase": p["id"],
                "detail": f"{p['id']} has no '**{lab}**' line, so that cell shows NOT STATED "
                          f"rather than a value."})
        if p.get("status") == "NOT STATED":
            violations.append({
                "kind": "PHASE_STATUS_NOT_STATED", "literal": "**Status:**", "phase": p["id"],
                "detail": f"{p['id']} states no status. Add '**Status:** DONE | IN PROGRESS | "
                          f"BLOCKED | NOT STARTED' under its heading and this resolves."})
        if not p.get("goal"):
            violations.append({
                "kind": "PHASE_GOAL_MISSING", "literal": "**Goal:**", "phase": p["id"],
                "detail": f"{p['id']} has no one-line goal that can be read out of it -- its first "
                          f"content is a labelled line, so there is no opening sentence to take. "
                          f"Add '**Goal:** <one sentence>' under its heading and this resolves."})
    if not decisions:
        violations.append({
            "kind": "NO_DECISIONS_PARSED", "literal": DECISIONS_SECTION,
            "detail": f"no '**Dn - ...**' blocks were found under '{DECISIONS_SECTION}' in "
                      f"{NEAR_PLAN_DOC.name}."})
    for r in (ops.get("rows") or []):
        if r.get("verify_status") == "CHECK_SOURCE":
            violations.append({
                "kind": "TRANSCRIBED_NUMBER_GONE", "literal": ", ".join(r.get("verify_missing")
                                                                        or []),
                "phase": r.get("id"),
                "detail": f"'{r.get('title')}' quotes numbers that are no longer findable in the "
                          f"status documents. The documents are the authority; this row may be "
                          f"stale."})
    return {
        "status": "OK" if not violations else "VIOLATIONS",
        "violations": violations,
        "n_violations": len(violations),
        "checked_literals": list(REQUIRED_SECTIONS) + [f"**{x}**" for x in REQUIRED_PHASE_LABELS],
        "doc_side_recorded": CONTRACT_DOC.is_file(),
        "doc_side_path": str(CONTRACT_DOC),
        "doc_side_note": (
            "notes/LONG_TERM_PLAN.md is Director-owned and carries no pointer back to this parser "
            "yet. Until the Director adds one line naming tools/status_plan.py, the coupling is "
            "recorded on ONE side only -- see notes/LONG_TERM_PLAN_PARSER_CONTRACT.md."),
    }


# ---------------------------------------------------------------------------
# the panel
# ---------------------------------------------------------------------------

def collect_plan() -> dict:
    """WHERE WE ARE: the phases, which one we are in, and the single next action."""
    text = _read_text(LONG_PLAN_DOC)
    near = _read_text(NEAR_PLAN_DOC)
    phases = parse_phases(text or "")
    ladder = parse_success_ladder(text or "")
    decisions = parse_decisions(near or "")
    ops = load_operator_decisions()
    con = contract(text, phases, decisions, ops)

    if text is None:
        return {"status": "MISSING",
                "detail": f"the plan is not readable: {LONG_PLAN_DOC}. This panel has no data. "
                          f"A blank where the plan should be is the finding -- nothing here is "
                          f"reconstructed from memory.",
                "phases": [], "ladder": ladder, "decisions": decisions, "operator": ops,
                "contract": con, "current": None, "next_action": None}
    if not phases:
        return {"status": "ERROR",
                "detail": f"{LONG_PLAN_DOC.name} was read ({len(text)} bytes) but section 5 "
                          f"yielded no phases. The heading shape it is parsed by has changed. "
                          f"See notes/LONG_TERM_PLAN_PARSER_CONTRACT.md.",
                "phases": [], "ladder": ladder, "decisions": decisions, "operator": ops,
                "contract": con, "current": None, "next_action": None}

    # WHICH PHASE ARE WE IN. First an explicit IN PROGRESS; else the lowest-numbered phase that is
    # neither DONE nor MOSTLY DONE. The basis is carried so the reader can disagree with it.
    cur = next((p for p in phases if p["status"] == "IN PROGRESS"), None)
    basis = "the only phase the plan marks as in progress"
    if cur is None:
        cur = next((p for p in phases if p["status"] not in ("DONE", "MOSTLY DONE")), None)
        basis = ("no phase is marked in progress, so this is the lowest-numbered phase that is "
                 "not done")
    if cur is None:
        cur, basis = phases[-1], "every phase is marked done"

    nxt = _next_action(cur)
    return {
        "status": "OK",
        "doc": str(LONG_PLAN_DOC),
        "phases": phases,
        "ladder": ladder,
        "n_phases": len(phases),
        "current_id": cur["id"],
        "current": cur,
        "current_basis": basis,
        "next_action": nxt,
        "decisions": decisions,
        "n_decisions": len(decisions),
        "operator": ops,
        "contract": con,
        "n_contract_violations": con.get("n_violations", 0),
        "counts": {s: sum(1 for p in phases if p["status"] == s)
                   for s in ("DONE", "MOSTLY DONE", "IN PROGRESS", "BLOCKED", "NOT STARTED",
                             "NOT STATED")},
    }


# ---------------------------------------------------------------------------
# text dump + self-test
# ---------------------------------------------------------------------------

def render_text(s: dict) -> str:
    L: list[str] = []
    L.append("WHERE WE ARE -- the plan, parsed live, never transcribed")
    if s.get("status") != "OK":
        L.append(f"   {s.get('status')}: {s.get('detail')}")
        return "\n".join(L)
    L.append(f"   WE ARE IN {s['current_id']} -- {s['current'].get('title')}"
             f"   ({s.get('current_basis')})")
    na = s.get("next_action") or {}
    L.append(f"   NEXT ACTION: {na.get('text') or 'NOT STATED IN THE PLAN'}")
    L.append(f"                ({na.get('basis')})")
    for p in s["phases"]:
        L.append("")
        L.append(f"   {p['id']}  {p['title']}   [{p['status']}]")
        L.append(f"       goal:    {p.get('goal') or 'NOT STATED IN THE PLAN'}")
        L.append(f"       gate:    {p.get('gate') or 'NOT STATED IN THE PLAN'}")
        L.append(f"       stop-if: {p.get('kill') or 'NOT STATED IN THE PLAN'}")
    L.append("")
    L.append("   WHAT WOULD COUNT AS THIS WORKING, IN ORDER (section 7)")
    for r in s.get("ladder") or []:
        L.append(f"     {r['n']}. {r['text']}   {('[' + r['phase'] + ']') if r['phase'] else ''}")
    con = s.get("contract") or {}
    L.append("")
    L.append(f"   PARSER CONTRACT: {con.get('n_violations')} violation(s)")
    for v in (con.get("violations") or [])[:12]:
        L.append(f"     [{v.get('kind')}] {v.get('literal')} -- {v.get('detail')}")
    L.append("")
    L.append(f"   STANDING DECISIONS parsed from notes/PLAN.md: {s.get('n_decisions')}")
    for d in s.get("decisions") or []:
        L.append(f"     {d['id']}: {d['question']}")
        L.append(f"         default: {d.get('default') or 'NONE STATED'}")
    ops = s.get("operator") or {}
    L.append(f"   TRANSCRIBED STANDING DECISIONS: {ops.get('status')} "
             f"({len(ops.get('rows') or [])} row(s), drifted {ops.get('drifted')})")
    return "\n".join(L)


def collect() -> dict:
    return collect_plan()


def self_test() -> int:
    """Two properties, both against the real code path: it populates on the live repo, and it
    degrades to MISSING with every required file absent rather than inventing a plan."""
    import tempfile
    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    # ---- NORMAL ---------------------------------------------------------
    a = collect_plan()
    check(a.get("status") == "OK", f"normal: the panel populated ({a.get('status')}: "
                                   f"{str(a.get('detail'))[:120]})")
    ph = a.get("phases") or []
    check(len(ph) >= 5, f"normal: section 5 parsed (got {len(ph)} phases)")
    ids = [p["id"] for p in ph]
    check("PHASE 1" in ids and "PHASE 4" in ids,
          f"normal: the phases are identified by number (got {ids})")
    check(a.get("current_id") == "PHASE 1",
          f"normal: the current phase resolves to the one the plan says to start with "
          f"(got {a.get('current_id')!r})")
    na = a.get("next_action") or {}
    check(bool(na.get("text")), f"normal: a single next action is derived ({str(na.get('text'))[:70]})")
    check("RETRACT" not in str(na.get("text", "")).upper(),
          f"normal: the next action is NOT a struck-through item ({str(na.get('text'))[:70]})")
    p1 = next((p for p in ph if p["id"] == "PHASE 1"), {})
    check(bool(p1.get("gate")) and bool(p1.get("kill")),
          "normal: PHASE 1's gate and stop-if were both read out of the document")
    check(any(w.get("retracted") for w in (p1.get("work") or [])),
          "normal: a struck-through work item is marked RETRACTED, not shown as the next step")
    # The two documented gaps must be REPORTED, never filled in.
    p0 = next((p for p in ph if p["id"] == "PHASE 0"), {})
    p5 = next((p for p in ph if p["id"] == "PHASE 5"), {})
    check(p0.get("gate") == "" and "Gate:" in (p0.get("missing_labels") or []),
          f"normal: PHASE 0's absent gate is reported MISSING, not invented "
          f"(got {p0.get('gate')!r})")
    check(p5.get("kill") == "",
          f"normal: PHASE 5's absent stop-if is reported MISSING (got {p5.get('kill')!r})")
    con = a.get("contract") or {}
    check(con.get("status") in ("OK", "VIOLATIONS"), "normal: the contract check ran")
    check(isinstance(con.get("n_violations"), int),
          "normal: the contract violation count is a number the panel can render")
    check(con.get("n_violations", 0) > 0,
          "normal: the KNOWN gaps in the plan document are counted as violations rather than "
          "silently tolerated")
    check(con.get("doc_side_recorded") is True,
          f"normal: the doc-side record of this coupling exists "
          f"({con.get('doc_side_path')})")
    ds = a.get("decisions") or []
    check(len(ds) >= 5, f"normal: notes/PLAN.md section 9 decisions parsed (got {len(ds)})")
    check(all(d.get("default") for d in ds),
          f"normal: every parsed decision carries its recommended default "
          f"({[d['id'] for d in ds if not d.get('default')]})")
    ops = a.get("operator") or {}
    check(ops.get("status") == "OK",
          f"normal: the transcribed standing decisions loaded ({ops.get('status')}: "
          f"{str(ops.get('detail'))[:100]})")
    check(not ops.get("drifted"),
          f"normal: every transcribed standing-decision number is still findable in its source "
          f"(drifted: {ops.get('drifted')})")

    # ---- ABSENT ---------------------------------------------------------
    td = Path(tempfile.mkdtemp(prefix="status_plan_selftest_"))
    g = globals()
    keep = {k: g[k] for k in ("LONG_PLAN_DOC", "NEAR_PLAN_DOC", "OPERATOR_SPEC", "CONTRACT_DOC",
                              "AUTHORITY_DOCS")}
    try:
        g["LONG_PLAN_DOC"] = td / "nope_LONG_TERM_PLAN.md"
        g["NEAR_PLAN_DOC"] = td / "nope_PLAN.md"
        g["OPERATOR_SPEC"] = td / "nope_operator_decisions.json"
        g["CONTRACT_DOC"] = td / "nope_contract.md"
        g["AUTHORITY_DOCS"] = [td / "nope_STATUS.md"]
        b = collect_plan()
    finally:
        g.update(keep)
    check(b.get("status") == "MISSING",
          f"files-absent: the panel says MISSING (got {b.get('status')!r})")
    check(not b.get("phases"), "files-absent: no phase is invented")
    check(b.get("current") is None, "files-absent: no current phase is invented")
    check((b.get("contract") or {}).get("status") == "CANNOT_CHECK",
          "files-absent: the contract check says CANNOT_CHECK, never VERIFIED")
    check((b.get("operator") or {}).get("status") == "MISSING",
          "files-absent: the transcribed decisions say MISSING")
    check("MISSING" in render_text(b), "files-absent: the rendered view SAYS MISSING")

    check(len(a.get("ladder") or []) >= 4,
          f"normal: section 7's what-would-count-as-working ladder parsed "
          f"(got {len(a.get('ladder') or [])} rungs)")

    # ---- REWORDED (the 2026-08-13 failure, reproduced in both directions) -----
    # (a) TITLE reworded, number kept: the parser must keep working and must NOT cry wolf.
    retitled = ("## 5. THE ROADMAP\n\n### PHASE 1 - X *(current)*\n"
                "**Gate:** g\n**Kill condition:** k\n\n## 7. HOW WE KNOW\n\n1. a thing\n")
    ph_t = parse_phases(retitled)
    con_t = contract(retitled, ph_t, [{"id": "D1"}], {"rows": []})
    check(len(ph_t) == 1,
          f"retitled: rewording a section TITLE does not break parsing (got {len(ph_t)} phases)")
    check(not any(v["kind"] == "SECTION_HEADING_GONE" for v in con_t["violations"]),
          "retitled: rewording a section TITLE raises NO false contract violation")
    # (b) section RENUMBERED: that the parser cannot survive, and it must SAY SO, not degrade
    #     quietly into a plausible-looking empty panel.
    renumbered = ("## 6. THE PLAN\n\n### PHASE 1 - X *(current)*\n"
                  "**Gate:** g\n**Kill condition:** k\n")
    ph_r = parse_phases(renumbered)
    con_r = contract(renumbered, ph_r, [], {"rows": []})
    check(ph_r == [], "renumbered: a renumbered section yields NO phases, never partial ones")
    kinds = {v["kind"] for v in con_r["violations"]}
    check("SECTION_HEADING_GONE" in kinds and "NO_PHASES_PARSED" in kinds,
          f"renumbered: the window says WHICH literal went missing and that nothing parsed "
          f"(got {sorted(kinds)})")

    # ---- PARSER ---------------------------------------------------------
    tiny = ("## 5. THE PLAN\n\n### PHASE 7 - TEST PHASE *(blocked until something)*\n\n"
            "**Status:** IN PROGRESS\n"
            "**Goal:** do the thing.\n"
            "**The work:** 1. ~~old idea~~ RETRACTED, it was wrong. 2. the real next step.\n"
            "**Gate:** it clears the floor.\n"
            "**Kill condition:** it does not.\n\n## 6. NEXT\n")
    one = parse_phases(tiny)
    check(len(one) == 1 and one[0]["id"] == "PHASE 7", "parser: reads a well-formed phase")
    check(one[0]["status"] == "IN PROGRESS",
          f"parser: an explicit **Status:** line WINS over the heading note, which said 'blocked' "
          f"(got {one[0]['status']!r})")
    check(one[0]["goal"] == "do the thing.", f"parser: the goal line is read (got {one[0]['goal']!r})")
    check(len(one[0]["work"]) == 2 and one[0]["work"][0]["retracted"]
          and not one[0]["work"][1]["retracted"],
          f"parser: struck-through work items are marked retracted "
          f"(got {[(w['n'], w['retracted']) for w in one[0]['work']]})")
    check(_next_action(one[0])["text"].startswith("the real next step"),
          f"parser: the next action skips the retracted item "
          f"(got {_next_action(one[0])['text']!r})")
    no_status = parse_phases("## 5. THE PLAN\n\n### PHASE 8 - X *(some prose)*\n**Gate:** g\n")
    check(no_status and no_status[0]["status"] == "NOT STATED",
          "parser: a phase with no status word reports NOT STATED rather than guessing")
    check(no_status and "Kill condition:" in no_status[0]["missing_labels"],
          "parser: an absent required label is named")
    check(parse_phases("") == [], "parser: an empty document yields no phases, not a crash")
    check(parse_decisions("") == [], "parser: an empty document yields no decisions")

    print(f"[self-test] temp dir left in place by design: {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Live plan collector for the status window")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    s = collect_plan()
    print(json.dumps(s, indent=2, default=str) if args.json else render_text(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
