#!/usr/bin/env python
"""Collectors for panels A, B and C of the owner-facing status window.

WHY THIS FILE EXISTS (owner request, 2026-08-16): *"in the dash I'd like to see some info on
progress made (more info), and a brain organ map and fidelity measure with detail too"*.

THIS IS NOT A SECOND SOURCE OF TRUTH. `tools/status_state.py` remains the one collector and the
one entry point; it imports this module and runs each function through its existing
`_panel(name, fn, budget)` wrapper, so a failure here degrades ONE panel and the window stays up.
`tools/status_gui.py` remains a renderer. Nothing here writes anything, ever.

THE THREE PANELS

  A. PROGRESS MADE      what a thing scored BEFORE, what it scores NOW, and the floor beside both.
  B. BRAIN ORGAN MAP    per organ: the brain structure, what it does in one plain sentence,
                        whether we built it, whether it is switched on, and what it measures.
  C. FIDELITY           how closely we copy the brain -- explicitly NOT how well it works.

FIVE RULES, EACH ONE PAID FOR ELSEWHERE IN THIS REPO

  1. A SCORE WITHOUT ITS FLOOR IS FORBIDDEN. Panel A refuses to render a `now` score whose row
     carries no floor: it prints the floor as MISSING beside it. The whole "we beat scramble" era
     was this error, and on 2026-08-16 a CONSTANT ranking that uses zero information about the
     query was measured ABOVE both our read-out and the spelling channel.
  2. NEGATIVES AND RETRACTIONS ARE AS LOUD AS GAINS. Panel A has a RETRACTED class rendered in the
     same red as a loss, and the panel header counts them. Three headline numbers were retracted on
     2026-08-16 alone. A progress panel that only showed gains would reproduce the exact failure
     this project keeps having to unpick.
  3. NEVER INVENT A BRAIN STRUCTURE. Panel B takes the brain structure from
     `notes/ORGAN_MAP.md` section 4 or from a `brain_structure` field in
     `data/capability_registry.jsonl`. Where neither exists the cell says NOT NAMED and the panel
     header reports how many registry rows are deliberately empty. Retro-filling that field is
     banned (`3e70c3ba4`); this panel shows the backlog instead of hiding it.
  4. THE FIDELITY SCORE IS NOT A PREDICTION. `tools/brain_fidelity_score.py` (`3e355e16d`) is
     UNVALIDATED as a predictor -- one positive in six points, p ~ 0.17 -- and it scores the
     REFUTED CA3 arm well ABOVE the incumbent flat bag that beats it in practice. Panel C carries
     that verdict ON SCREEN, read from the tool's own `VALIDATION_VERDICT` string rather than
     paraphrased here. Showing a fidelity number as though it predicted performance would be
     exactly the laundering the fidelity gate exists to prevent.
  5. MISSING IS INFORMATION. Every artifact is optional. A missing file degrades its panel to
     MISSING with the path named. No panel ever substitutes a stale or invented value.

WHERE THE NUMBERS COME FROM, AND HOW DRIFT IS CAUGHT

Panels B and C read their structure LIVE: `notes/ORGAN_MAP.md` is parsed on every refresh,
`data/capability_registry.jsonl` is read on every refresh, and `tools/brain_fidelity_score.py` is
imported and run IN PROCESS (measured at 16 ms -- no subprocess, no multi-minute audit inline).

Panel A cannot work that way, because the plan documents state their numbers in prose. So it uses
the mechanism `notes/component_health.json` already established for panel 1: a structured
transcription (`notes/progress_ledger.json`) in which EVERY row carries a `verify` list of literal
strings that must still be findable in its authority document. The strings are re-checked on every
refresh and a row whose literal has gone missing renders CHECK-SOURCE -- so an edit that moves a
number surfaces as a mismatch instead of the window quietly showing yesterday's figure. Dashes are
normalised before comparison so typography cannot trip the check.

A row may name its own authority with `verify_source` (a repo-relative path). That exists because
some of tonight's numbers live only in a scan fragment under `.claude/scan-out/` and not in any
notes document -- the sparse-coding participation ratio is the live example. Naming the fragment is
honest; silently dropping the check is not.

  python tools/status_organs.py                # human-readable dump
  python tools/status_organs.py --json
  python tools/status_organs.py --self-test    # runs with every required file ABSENT
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# --- paths. Every one is env-overridable so the self-test can point at absent files. ---------
ORGAN_MAP_DOC = Path(os.environ.get("HD_ORGAN_MAP") or (REPO / "notes" / "ORGAN_MAP.md"))
PROGRESS_SPEC = Path(os.environ.get("HD_PROGRESS_SPEC")
                     or (REPO / "notes" / "progress_ledger.json"))
ORGAN_SPEC = Path(os.environ.get("HD_ORGAN_SPEC") or (REPO / "notes" / "organ_panel.json"))
REGISTRY = Path(os.environ.get("HD_REGISTRY")
                or (REPO / "data" / "capability_registry.jsonl"))
# The authority corpus the `verify` literals are checked against.
AUTHORITY_DOCS = [
    Path(os.environ.get("HD_STATUS_DOC") or (REPO / "notes" / "STATUS.md")),
    Path(os.environ.get("HD_LONG_PLAN_DOC") or (REPO / "notes" / "LONG_TERM_PLAN.md")),
    Path(os.environ.get("HD_PLAN_DOC") or (REPO / "notes" / "PLAN.md")),
    ORGAN_MAP_DOC,
]

MAX_DOC_BYTES = 4_000_000      # a runaway doc must not be pulled into memory whole
MAX_REGISTRY_ROWS = 5_000

# Fidelity vocabulary in notes/ORGAN_MAP.md, mapped to the three axes the owner asked for:
# does our SHAPE match, is it in the right POSITION in the pipeline, is it judged on the brain's
# METRIC. The mapping is the map's own vocabulary, not a new judgement -- see ORGAN_MAP section 1,
# which reports RIGHT-OP-WRONG-METRIC and RIGHT-OP-WRONG-PLACE as different populations precisely
# because collapsing them destroys this information.
_FIDELITY_AXES = {
    "SAME": ("matches", "matches", "matches",
             "Our operation IS the brain's, in the right place, judged the brain's way."),
    "RIGHT-OP-WRONG-METRIC": ("matches", "matches", "DIVERGES",
                              "Right operation, wrong yardstick."),
    "RIGHT-OP-WRONG-PLACE": ("matches", "DIVERGES", "unknown",
                             "Right operation, wrong point in the pipeline."),
    "WRONG-OP": ("DIVERGES", "unknown", "unknown",
                 "We are not doing the brain's operation at all."),
    "MISSING": ("NOT BUILT", "NOT BUILT", "NOT BUILT",
                "The organ does not exist here."),
    "UNSCORABLE": ("unknown", "unknown", "unknown",
                   "The brain's equation is UNPINNED, so fidelity cannot be scored at all."),
}
_FIDELITY_ORDER = ("RIGHT-OP-WRONG-METRIC", "RIGHT-OP-WRONG-PLACE", "UNSCORABLE",
                   "WRONG-OP", "MISSING", "SAME")


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def _norm_dashes(s: str) -> str:
    """Normalise every dash-like character to '-'.

    Deliberately duplicated from `status_state._norm_dashes` rather than imported: status_state
    imports THIS module, so importing back would be circular. This is a six-line text primitive,
    not a source of truth, and duplicating it is cheaper than a lazy cross-import that fails at
    the worst moment."""
    if not s:
        return ""
    for ch in ("‐", "‑", "‒", "–", "—", "―", "−"):
        s = s.replace(ch, "-")
    return s


def _read_text(path: Path) -> str | None:
    """Read a text file, or None. Never raises, never loads an absurd file whole."""
    try:
        if path.stat().st_size > MAX_DOC_BYTES:
            return path.read_text(encoding="utf-8", errors="replace")[:MAX_DOC_BYTES]
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


_cache: dict = {}


def _cached(path: Path, build):
    """Cache a parse keyed on (path, mtime, size) so a 20-second refresh does not re-parse a
    167 KB document every tick. A changed file invalidates itself; a deleted file falls straight
    through to the MISSING path."""
    try:
        st = path.stat()
        key = (str(path), st.st_mtime_ns, st.st_size)
    except OSError:
        return None
    hit = _cache.get(str(path))
    if hit is not None and hit[0] == key:
        return hit[1]
    val = build()
    _cache[str(path)] = (key, val)
    return val


def _load_json(path: Path) -> tuple[dict | None, str]:
    txt = _read_text(path)
    if txt is None:
        return None, f"not found: {path}"
    try:
        obj = json.loads(txt)
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"unreadable ({type(exc).__name__}: {exc})"
    if not isinstance(obj, dict):
        return None, f"expected an object, got {type(obj).__name__}"
    return obj, ""


# ---------------------------------------------------------------------------
# the drift check -- the mechanism that stops a stale number being shown as current
# ---------------------------------------------------------------------------

def _authority_corpus() -> tuple[str, list[str]]:
    """Concatenate the authority documents. Returns (corpus, names_of_missing_docs).

    An ABSENT authority means CANNOT_VERIFY, never VERIFIED. That distinction is the whole point:
    a check that silently passes when its input is missing is not a check."""
    parts, missing = [], []
    for p in AUTHORITY_DOCS:
        t = _read_text(p)
        if t is None:
            missing.append(p.name)
        else:
            parts.append(t)
    return _norm_dashes("\n".join(parts)), missing


def _verify_row(row: dict, corpus: str, can_verify: bool) -> dict:
    """Attach verify_status / verify_missing to one transcribed row.

    VERIFIED           every literal still findable in the authority
    CHECK_SOURCE       at least one literal has gone missing -- the row may be stale
    NO_VERIFY_STRINGS  the row quotes no number, so there is nothing to drift
    CANNOT_VERIFY      the authority document itself was unreadable
    """
    strings = [s for s in (row.get("verify") or []) if isinstance(s, str) and s]
    extra = row.get("verify_source")
    local = corpus
    if extra:
        # A row may name its own authority (a scan fragment). Read it bounded, and if it is gone
        # say so rather than quietly falling back to the shared corpus.
        t = _read_text(REPO / str(extra))
        if t is None:
            row["verify_status"] = "CANNOT_VERIFY"
            row["verify_missing"] = []
            row["verify_detail"] = f"named source not found: {extra}"
            return row
        local = corpus + "\n" + _norm_dashes(t)
    if not can_verify and not extra:
        row["verify_status"] = "CANNOT_VERIFY"
        row["verify_missing"] = []
        row["verify_detail"] = "authority documents unreadable"
        return row
    if not strings:
        row["verify_status"] = "NO_VERIFY_STRINGS"
        row["verify_missing"] = []
        return row
    missing = [s for s in strings if _norm_dashes(s) not in local]
    row["verify_missing"] = missing
    row["verify_status"] = "CHECK_SOURCE" if missing else "VERIFIED"
    return row


# ---------------------------------------------------------------------------
# notes/ORGAN_MAP.md section 4 -- parsed live, never transcribed
# ---------------------------------------------------------------------------

_ORGAN_HEAD = re.compile(r"^\*\*([A-H]\d+[a-z]?)\s*[-‐-―−]\s*(.+?)\*\*\s*(.*)$")
_GROUP_HEAD = re.compile(r"^###\s+([A-H])\.\s+(.+?)\s*$")
_FIELD = re.compile(r"^-\s+\*\*([A-Z][A-Z0-9'’ /()-]*?):\*\*\s*(.*)$")
_SECTION4 = re.compile(r"^##\s+4\.\s")
_SECTION_ANY = re.compile(r"^##\s+\d+\.\s")


def parse_organ_map(text: str) -> list[dict]:
    """Pull every organ out of section 4 of notes/ORGAN_MAP.md.

    The document's shape is stable and self-describing: `### <LETTER>. <group>` opens a group,
    `**<ID> - <title>**` opens an organ, and `- **FIELD:**` opens a field that runs until the next
    field, the next organ or the next group. Continuation lines are folded in, so a fidelity
    verdict wrapped over three lines is read whole.

    Parsing rather than transcribing is deliberate: the map is a LIVING doc updated in place, and
    a transcription of it would go stale in exactly the way this panel exists to prevent."""
    organs: list[dict] = []
    if not text:
        return organs
    lines = _norm_dashes(text).splitlines()
    in4 = False
    group = ""
    cur: dict | None = None
    field: str | None = None

    def _close():
        nonlocal cur, field
        if cur is not None:
            for k, v in list(cur.get("fields", {}).items()):
                cur["fields"][k] = re.sub(r"\s+", " ", v).strip()
            organs.append(cur)
        cur, field = None, None

    for raw in lines:
        if _SECTION4.match(raw):
            in4 = True
            continue
        if in4 and _SECTION_ANY.match(raw) and not _SECTION4.match(raw):
            break
        if not in4:
            continue
        g = _GROUP_HEAD.match(raw)
        if g:
            _close()
            group = f"{g.group(1)}. {g.group(2)}"
            continue
        h = _ORGAN_HEAD.match(raw.strip())
        if h:
            _close()
            cur = {"id": h.group(1), "title": h.group(2).strip(), "group": group,
                   "aside": h.group(3).strip().strip("*"), "fields": {}}
            continue
        if cur is None:
            continue
        f = _FIELD.match(raw.strip())
        if f:
            field = f.group(1).strip().upper()
            cur["fields"][field] = f.group(2).strip()
            continue
        if field and raw.strip():
            cur["fields"][field] = (cur["fields"].get(field, "") + " " + raw.strip())
    _close()

    for o in organs:
        _derive_organ(o)
    return organs


def _strip_md(s: str) -> str:
    """Plain text out of markdown emphasis and code fences, for a table cell."""
    s = re.sub(r"[*`~]", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def _derive_organ(o: dict) -> None:
    """Turn the raw fields into the columns the panel shows. Every derivation is from the map's
    own vocabulary -- nothing here is a fresh judgement about biology."""
    f = o.get("fields", {})
    math = f.get("BRAIN'S MATH", "") or f.get("BRAINS MATH", "")
    fid = f.get("FIDELITY", "")
    wired = f.get("WIRED", "")
    ev = f.get("EVIDENCE", "")
    o["brain_math"] = _strip_md(math)
    o["ours"] = _strip_md(f.get("OURS", ""))
    o["fidelity_raw"] = _strip_md(fid)
    o["wired_raw"] = _strip_md(wired)
    o["evidence_raw"] = _strip_md(ev)
    o["blocks"] = _strip_md(f.get("BLOCKS", ""))

    # fidelity class: first vocabulary term that appears in the FIDELITY line, else in the aside
    blob = (fid + " " + o.get("aside", "")).upper()
    cls = next((k for k in _FIDELITY_ORDER if k in blob), None)
    if cls is None and "MISSING" in (o.get("aside") or "").upper():
        cls = "MISSING"
    o["fidelity_class"] = cls or "NOT STATED"
    shape, pos, metric, plain = _FIDELITY_AXES.get(
        o["fidelity_class"], ("unknown", "unknown", "unknown",
                              "The map states no fidelity verdict for this organ."))
    o["axis_shape"], o["axis_position"], o["axis_metric"] = shape, pos, metric
    o["fidelity_plain"] = plain

    # is the brain's equation pinned?
    o["brain_math_pinned"] = "UNPINNED" not in math.upper() if math else None

    # built / switched on. The map states WIRED as YES / NO / mixed prose; DEFAULT-OFF is stated
    # in the OURS or WIRED text ("default OFF" / "DEFAULT FALSE" / "switched OFF by default").
    wu = wired.upper()
    ou = (f.get("OURS", "") + " " + wired).upper()
    default_off = bool(re.search(r"DEFAULT\s*(-|\s)?\s*(OFF|FALSE)|SWITCHED OFF BY DEFAULT", ou))
    if o["fidelity_class"] == "MISSING":
        o["built"] = "NO"
        o["state"] = "MISSING"
    elif wu.startswith("NO") or re.search(r"\bZERO\b.*IMPORTERS|ORPHAN", wu):
        o["built"] = "YES"
        o["state"] = "BUILT BUT NOT SWITCHED ON"
    elif "YES" in wu:
        o["built"] = "YES"
        o["state"] = "DEFAULT-OFF" if default_off else "SWITCHED ON"
    else:
        o["built"] = "YES" if o.get("ours") else "UNKNOWN"
        o["state"] = "NOT STATED"

    # what it measures, and -- the point -- whether the measurement had a floor.
    #
    # THE FALLBACK IS LOAD-BEARING, not tidying. Several organs (B1, D2, A1) carry no separate
    # `- **EVIDENCE:**` line: their evidence sits in a re-audit note folded into the WIRED field
    # ("SEE section 10.1 - NO LONGER UNTESTED: ..."). Reading only the EVIDENCE field renders those
    # organs as NOTHING RECORDED, which is false and is precisely the "we looked and did not find
    # it" error -- an absence claim that is really a parsing gap. So when EVIDENCE is empty we read
    # the WIRED continuation, and we say which field the text came from.
    ev_from = "EVIDENCE"
    if not ev:
        tail = re.sub(r"^\s*(YES|NO)\b[.,;:]?", "", wired, flags=re.I).strip()
        if len(tail) > 30:
            ev = tail
            ev_from = "WIRED note"
    o["evidence_raw"] = _strip_md(ev)
    o["evidence_field"] = ev_from
    o["reaudited"] = bool(re.search(r"SEE\s*.{0,3}\s*10(\.1)?\b|NO LONGER UNTESTED", ev, re.I))
    # Three signals, read SEPARATELY and never collapsed, because the map genuinely says
    # contradictory things about several organs and flattening that would be a fabrication in
    # whichever direction the code happened to pick:
    #   * "NO LONGER UNTESTED" is stripped first -- it CONTAINS the word UNTESTED and a naive
    #     substring match reads a re-audit that FOUND evidence as an absence of evidence.
    #   * "NO FLOOR" / "no floored number" is stripped before looking for floor words, or the
    #     phrase that DENIES a floor is itself counted as one.
    #   * an organ whose row says BOTH (A1: a floored trigram comparison AND a stale UNTESTED
    #     marker) is reported as saying both. That is the honest cell, and the detail box carries
    #     the raw sentence so the reader can adjudicate it rather than trusting this classifier.
    evu = ev.upper()
    ev_clean = evu.replace("NO LONGER UNTESTED", "")
    says_no_floor = "NO FLOOR" in ev_clean
    ev_noneg = ev_clean.replace("NO FLOORED", "").replace("NO FLOOR", "")
    says_untested = "UNTESTED" in ev_noneg
    has_floor = bool(re.search(r"FLOOR|BASELINE|CHANCE|SCRAMBLE", ev_noneg))
    if not ev:
        o["measured"], o["floor_named"] = "NOTHING RECORDED IN THE MAP", False
    elif has_floor and (says_untested or says_no_floor):
        o["measured"] = ("the map says BOTH -- a floored comparison AND still untested in part; "
                         "read the detail")
        o["floor_named"] = None
    elif says_no_floor:
        o["measured"], o["floor_named"] = "measured, NO FLOOR beside it", False
    elif says_untested:
        o["measured"], o["floor_named"] = "UNTESTED against anything that could fail", False
    elif has_floor:
        o["measured"], o["floor_named"] = "measured WITH a floor", True
    else:
        o["measured"], o["floor_named"] = "measured, floor not stated in this row", False


# ---------------------------------------------------------------------------
# data/capability_registry.jsonl -- read live
# ---------------------------------------------------------------------------

def load_registry() -> dict:
    """Read the registry, and -- the number the owner asked for -- count how many rows carry a
    named brain structure versus how many are deliberately empty.

    Retro-filling `brain_structure` on the backlog is BANNED (`3e70c3ba4`), so an empty field is a
    correct state, not a defect. The panel shows the backlog count rather than hiding it."""
    txt = _read_text(REGISTRY)
    if txt is None:
        return {"status": "MISSING", "detail": f"registry not found: {REGISTRY}",
                "rows": [], "by_module": {}}
    rows, bad = [], 0
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(rows) >= MAX_REGISTRY_ROWS:
            break
        try:
            r = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            bad += 1
            continue
        if isinstance(r, dict):
            rows.append(r)
    by_module: dict[str, dict] = {}
    for r in rows:
        p = r.get("path")
        for x in (p if isinstance(p, list) else [p]):
            if isinstance(x, str) and x:
                by_module.setdefault(Path(x).name, r)
                by_module.setdefault(x, r)
    with_bs = [r for r in rows if r.get("brain_structure")]
    return {
        "status": "OK",
        "path": str(REGISTRY),
        "rows": rows,
        "by_module": by_module,
        "n_rows": len(rows),
        "n_unparseable": bad,
        "n_brain_structure": len(with_bs),
        "n_no_brain_structure": len(rows) - len(with_bs),
        "n_fidelity_basis": sum(1 for r in rows if r.get("fidelity_basis")),
        "with_brain_structure": [
            {"id": r.get("id"), "name": r.get("name"),
             "path": r.get("path"),
             "gate_decision": r.get("gate_decision"),
             "integration_status": r.get("integration_status"),
             "pipeline_status": r.get("pipeline_status"),
             "brain_structure": r.get("brain_structure"),
             "fidelity_basis": r.get("fidelity_basis"),
             "fidelity_basis_note": r.get("fidelity_basis_note"),
             "revival_criteria": r.get("revival_criteria")}
            for r in with_bs],
    }


def _registry_state(reg_row: dict | None, module: str | None) -> tuple[str, str]:
    """(state, detail) for one module, in the owner's vocabulary."""
    if reg_row is None:
        return ("NO REGISTRY ROW",
                f"{module or 'this module'} has no row in data/capability_registry.jsonl at all, "
                f"so the wire-or-shelve gate has never been applied to it.")
    gate = (reg_row.get("gate_decision") or "").upper()
    pipe = (reg_row.get("pipeline_status") or "").upper()
    if gate.startswith("SHELVE"):
        state = "SHELVED"
    elif gate.startswith("WIRE_CANDIDATE"):
        state = "CANDIDATE, NOT WIRED"
    elif "NOT_PIPELINE_REACHABLE" in pipe:
        state = "BUILT BUT NOT ON THE LIVE PATH"
    elif "PIPELINE_USED" in pipe:
        state = "SWITCHED ON"
    elif gate.startswith("WIRE") or gate.startswith("ALREADY_WIRED"):
        state = "WIRED"
    else:
        state = gate or "NOT STATED"
    return state, f"registry: gate {reg_row.get('gate_decision')}, pipeline {reg_row.get('pipeline_status')}"


# ---------------------------------------------------------------------------
# PANEL A -- PROGRESS MADE
# ---------------------------------------------------------------------------

def collect_progress() -> dict:
    spec, err = _load_json(PROGRESS_SPEC)
    if spec is None:
        return {"status": "MISSING",
                "detail": f"progress ledger {err}. Panel A has no data. This is a MISSING panel, "
                          f"not an empty one -- a blank where a measurement should be is the "
                          f"finding.",
                "components": [], "phases": [], "retractions": [], "governing_floor": None}
    corpus, missing_docs = _authority_corpus()
    can_verify = bool(corpus)

    def prep(items, kind):
        out = []
        for r in items if isinstance(items, list) else []:
            if not isinstance(r, dict):
                continue
            row = dict(r)
            row["kind"] = kind
            _verify_row(row, corpus, can_verify)
            # THE RULE: a score is never shown without its floor. If the row states a score and
            # no floor, we do not hide it -- we mark it, because a score with no floor beside it
            # cannot be graded and saying so is the useful output.
            for side in ("before", "now"):
                s = row.get(side)
                if isinstance(s, dict):
                    if s.get("score") and not s.get("floor"):
                        s.setdefault("floor", None)
                        s["floor_name"] = s.get("floor_name") or "NO FLOOR STATED"
                        row["floor_gap"] = True
            out.append(row)
        return out

    comps = prep(spec.get("components"), "COMPONENT")
    phases = prep(spec.get("phases"), "PLAN PHASE")
    retr = prep(spec.get("retractions"), "RETRACTED")
    gov = spec.get("governing_floor")
    if isinstance(gov, dict):
        gov = _verify_row(dict(gov), corpus, can_verify)
    else:
        gov = None

    rows = comps + phases + retr
    drifted = [r.get("title") for r in rows if r.get("verify_status") == "CHECK_SOURCE"]
    return {
        "status": "OK",
        "as_of": spec.get("as_of"),
        "spec_path": str(PROGRESS_SPEC),
        "authority_docs": [str(p) for p in AUTHORITY_DOCS],
        "authority_missing": missing_docs,
        "can_verify": can_verify,
        "governing_floor": gov,
        "components": comps,
        "phases": phases,
        "retractions": retr,
        "n_retracted": len(retr),
        "n_down": sum(1 for r in rows if (r.get("direction") or "").upper()
                      in ("DOWN", "WORSE", "NULL", "NEGATIVE")),
        "n_up": sum(1 for r in rows if (r.get("direction") or "").upper() in ("UP", "BETTER")),
        "n_no_floor": sum(1 for r in rows if r.get("floor_gap")),
        "drifted": drifted,
    }


# ---------------------------------------------------------------------------
# PANEL B -- THE BRAIN ORGAN MAP
# ---------------------------------------------------------------------------

def collect_organs() -> dict:
    """Every organ, from the map and the registry, with the overlay rows for organs that post-date
    the map. Plain-language glosses come from `notes/organ_panel.json`; a gloss the file does not
    carry renders as "no plain-language summary written yet" rather than as invented biology."""
    text = _read_text(ORGAN_MAP_DOC)
    parsed = _cached(ORGAN_MAP_DOC, lambda: parse_organ_map(text or "")) if text else None
    if parsed is None:
        parsed = parse_organ_map(text or "")
    reg = load_registry()
    overlay_spec, ov_err = _load_json(ORGAN_SPEC)
    glosses = (overlay_spec or {}).get("glosses") or {}
    overlays = (overlay_spec or {}).get("overlay_organs") or []
    required = (overlay_spec or {}).get("required_organs") or []

    corpus, missing_docs = _authority_corpus()
    can_verify = bool(corpus)

    rows: list[dict] = []

    # 1. the organs the map itself enumerates
    for o in parsed:
        g = glosses.get(o["id"]) if isinstance(glosses, dict) else None
        g = g if isinstance(g, dict) else {}
        module = None
        m = re.search(r"hdlab/([A-Za-z0-9_]+)\.py", o.get("ours", ""))
        if m:
            module = m.group(1) + ".py"
        reg_row = reg.get("by_module", {}).get(module) if module else None
        state, state_detail = (o["state"], "from notes/ORGAN_MAP.md WIRED line")
        rows.append({
            "source": "ORGAN_MAP",
            "id": o["id"],
            "title": o["title"],
            "group": o["group"],
            "plain_name": g.get("plain_name") or o["title"],
            "brain_structure": g.get("brain_structure") or o["title"],
            "brain_plain": g.get("brain_plain"),
            "brain_math": o["brain_math"],
            "brain_math_pinned": o["brain_math_pinned"],
            "ours": o["ours"],
            "module": module,
            "built": o["built"],
            "state": state,
            "state_detail": state_detail,
            "measured": o["measured"],
            "floor_named": o["floor_named"],
            "evidence": o["evidence_raw"],
            "evidence_field": o.get("evidence_field"),
            "reaudited": o.get("reaudited"),
            "blocks": o["blocks"],
            "fidelity_class": o["fidelity_class"],
            "fidelity_plain": o["fidelity_plain"],
            "axis_shape": o["axis_shape"],
            "axis_position": o["axis_position"],
            "axis_metric": o["axis_metric"],
            "registry_gate": (reg_row or {}).get("gate_decision"),
            "registry_pipeline": (reg_row or {}).get("pipeline_status"),
            "fidelity_basis": (reg_row or {}).get("fidelity_basis"),
            "verify_status": "LIVE_PARSE",
        })

    # 2. the organs that post-date the map, or that have no map row at all
    for r in overlays if isinstance(overlays, list) else []:
        if not isinstance(r, dict):
            continue
        row = dict(r)
        row["source"] = "OVERLAY"
        module = row.get("module")
        reg_row = reg.get("by_module", {}).get(module) if module else None
        st, detail = _registry_state(reg_row, module)
        # A registry row that carries the brain_structure field is the AUTHORITY for it; the
        # overlay never overrides one that exists on disk.
        if reg_row and reg_row.get("brain_structure"):
            row["brain_structure"] = reg_row["brain_structure"]
            row["brain_structure_source"] = "data/capability_registry.jsonl"
        else:
            row.setdefault("brain_structure", None)
            row.setdefault("brain_structure_source", "notes/organ_panel.json")
        if reg_row and reg_row.get("fidelity_basis"):
            row["fidelity_basis"] = reg_row["fidelity_basis"]
            row["fidelity_basis_note"] = reg_row.get("fidelity_basis_note")
            row["revival_criteria"] = reg_row.get("revival_criteria")
        row["registry_gate"] = (reg_row or {}).get("gate_decision")
        row["registry_pipeline"] = (reg_row or {}).get("pipeline_status")
        row["has_registry_row"] = reg_row is not None
        if not row.get("state"):
            row["state"] = st
        row["state_detail"] = detail
        _verify_row(row, corpus, can_verify)
        rows.append(row)

    if not rows:
        return {"status": "MISSING",
                "detail": f"no organs could be read. map: {ORGAN_MAP_DOC} "
                          f"({'present' if text else 'MISSING'}); overlay: {ov_err or 'ok'}; "
                          f"registry: {reg.get('status')}.",
                "rows": [], "registry": reg}

    # A short BUILT? flag for the table column. The long form stays in `built` for the detail box:
    # an overlay row's `built` is a sentence ("NO -- WE HAVE AN OPERATOR THAT DOES THE OPPOSITE")
    # and that sentence is the point, but it does not belong in a 60-pixel column.
    for r in rows:
        head = str(r.get("built") or "").strip().upper()
        r["built_short"] = "YES" if head.startswith("YES") else (
            "NO" if head.startswith("NO") else "UNKNOWN")

    by_id = {r["id"]: r for r in rows if r.get("id")}
    ordered = [by_id[i] for i in required if i in by_id]
    ordered += [r for r in rows if r.get("id") not in set(required)]
    missing_required = [i for i in required if i not in by_id]

    n_missing = sum(1 for r in rows if (r.get("state") or "").upper().startswith("MISSING")
                    or (r.get("built") or "").upper() == "NO")
    return {
        "status": "OK",
        "rows": ordered,
        "n_organs": len(rows),
        "n_from_map": sum(1 for r in rows if r["source"] == "ORGAN_MAP"),
        "n_overlay": sum(1 for r in rows if r["source"] == "OVERLAY"),
        "n_missing": n_missing,
        "n_no_floor": sum(1 for r in rows if r.get("floor_named") is False),
        "missing_required": missing_required,
        "map_path": str(ORGAN_MAP_DOC),
        "overlay_path": str(ORGAN_SPEC),
        "overlay_error": ov_err,
        "authority_missing": missing_docs,
        "registry": {k: v for k, v in reg.items() if k not in ("rows", "by_module")},
        "drifted": [r.get("title") for r in rows if r.get("verify_status") == "CHECK_SOURCE"],
    }


# ---------------------------------------------------------------------------
# PANEL C -- FIDELITY, WITH ITS OWN HONESTY BUILT IN
# ---------------------------------------------------------------------------

def collect_fidelity() -> dict:
    """How closely we copy the brain -- and, on screen, the fact that this number does NOT predict
    whether the thing works.

    The scoring tool is imported and run IN PROCESS. Measured at 16 ms, so this is nowhere near a
    multi-minute audit; but it is still wrapped by the caller's budget, and an import failure
    degrades this panel alone."""
    out: dict = {"status": "OK", "tool": "tools/brain_fidelity_score.py"}
    try:
        import brain_fidelity_score as _bfs
    except Exception as exc:
        return {"status": "MISSING",
                "detail": f"tools/brain_fidelity_score.py could not be imported "
                          f"({type(exc).__name__}: {exc}). The fidelity score is UNAVAILABLE. "
                          f"Showing nothing is correct here -- there is no cached number to fall "
                          f"back on and inventing one would be the exact failure this panel "
                          f"warns about.",
                "rows": [], "components": [], "warning": None}
    t0 = time.time()
    try:
        retro = _bfs.run_retrodiction()
    except Exception as exc:
        retro = {"_error": f"{type(exc).__name__}: {exc}"}
    try:
        table = _bfs.run_component_table()
    except Exception as exc:
        table = {"_error": f"{type(exc).__name__}: {exc}"}
    out["took_s"] = round(time.time() - t0, 3)

    rows = []
    for r in (retro.get("rows") or []) if isinstance(retro, dict) else []:
        if not isinstance(r, dict):
            continue
        blind = r.get("design_time_blind") or {}
        outcome = str(r.get("outcome") or "")
        held = "HELD" in outcome.upper()[:8]
        rows.append({
            "component": r.get("component"),
            "pct": blind.get("pct"),
            "points": blind.get("points"),
            "max": blind.get("max"),
            "n_scorable": blind.get("n_scorable"),
            "outcome": outcome,
            "outcome_source": r.get("outcome_source"),
            "held": held,
            "dimensions": r.get("dimensions_blind"),
            "regime_or_pairing_zero": r.get("regime_or_pairing_zero"),
        })
    rows.sort(key=lambda r: (r.get("pct") is None, -(r.get("pct") or 0)))

    comps = []
    for r in (table.get("rows") or []) if isinstance(table, dict) else []:
        if not isinstance(r, dict):
            continue
        comps.append({
            "component": r.get("component"),
            "plan_status": r.get("plan_status"),
            "pct": r.get("pct"),
            "points": r.get("points"),
            "max_points": r.get("max_points"),
            "not_scored": r.get("NOT_SCORED"),
            "dimensions": r.get("dimensions"),
        })

    # THE WARNING. Read from the tool, never paraphrased here: if the tool's own verdict ever
    # changes, this panel changes with it instead of repeating a sentence somebody typed once.
    verdict = retro.get("VALIDATION_VERDICT") if isinstance(retro, dict) else None
    out.update({
        "rows": rows,
        "components": comps,
        "n_held": retro.get("n_held") if isinstance(retro, dict) else None,
        "n_failed_or_null": retro.get("n_failed_or_null") if isinstance(retro, dict) else None,
        "validation_verdict": verdict,
        "was_anything_tuned": retro.get("WAS_ANYTHING_TUNED") if isinstance(retro, dict) else None,
        "unscored_is_the_finding": (table.get("UNSCORED_IS_THE_FINDING")
                                    if isinstance(table, dict) else None),
        "retro_error": retro.get("_error") if isinstance(retro, dict) else None,
        "table_error": table.get("_error") if isinstance(table, dict) else None,
        "headline": ("HOW CLOSELY WE COPY THE BRAIN. This is NOT a measure of how well anything "
                     "works, and it has NOT been shown to predict that."),
    })
    if verdict is None:
        out["validation_verdict"] = (
            "THE TOOL DID NOT STATE ITS OWN VALIDATION VERDICT. Treat every number in this panel "
            "as unvalidated until it does.")
        out["status"] = "PARTIAL"

    # The divergence table, straight out of the map's own fidelity vocabulary -- but labelled with
    # the PLAIN name, not the map's own title. The map is written for us; this panel is not.
    text = _read_text(ORGAN_MAP_DOC)
    organs = parse_organ_map(text or "") if text else []
    ospec, _ = _load_json(ORGAN_SPEC)
    gl = (ospec or {}).get("glosses") or {}
    counts: dict[str, int] = {}
    div = []
    for o in organs:
        counts[o["fidelity_class"]] = counts.get(o["fidelity_class"], 0) + 1
        gname = (gl.get(o["id"]) or {}).get("plain_name") if isinstance(gl, dict) else None
        div.append({"id": o["id"], "title": gname or o["title"],
                    "map_title": o["title"], "class": o["fidelity_class"],
                    "shape": o["axis_shape"], "position": o["axis_position"],
                    "metric": o["axis_metric"], "plain": o["fidelity_plain"],
                    "pinned": o["brain_math_pinned"]})
    out["divergence"] = div
    out["divergence_counts"] = counts
    out["n_unscorable"] = counts.get("UNSCORABLE", 0)
    if not organs:
        out["divergence_detail"] = (f"notes/ORGAN_MAP.md is not readable ({ORGAN_MAP_DOC}), so the "
                                    f"per-organ divergence table is MISSING.")

    reg = load_registry()
    out["registry_basis"] = [
        {"id": r.get("id"), "fidelity_basis": r.get("fidelity_basis"),
         "note": r.get("fidelity_basis_note"), "brain_structure": r.get("brain_structure")}
        for r in reg.get("with_brain_structure", [])]
    out["n_registry_rows"] = reg.get("n_rows")
    out["n_registry_with_basis"] = reg.get("n_fidelity_basis")
    out["n_registry_backlog"] = reg.get("n_no_brain_structure")
    return out


# ---------------------------------------------------------------------------
# text dump + self-test
# ---------------------------------------------------------------------------

def collect() -> dict:
    return {"progress": collect_progress(), "organs": collect_organs(),
            "fidelity": collect_fidelity()}


def render_text(s: dict) -> str:
    L: list[str] = []
    p = s.get("progress") or {}
    L.append("A. PROGRESS MADE -- what moved, and the floor beside every number")
    if p.get("status") != "OK":
        L.append(f"   {p.get('status')}: {p.get('detail')}")
    else:
        gov = p.get("governing_floor") or {}
        if gov:
            L.append(f"   GOVERNING FLOOR: {gov.get('title')} -- {gov.get('plain')}")
        for r in (p.get("components") or []) + (p.get("phases") or []) + \
                 (p.get("retractions") or []):
            b, n = r.get("before") or {}, r.get("now") or {}
            L.append(f"   [{r.get('kind')}] {r.get('title')}  ->  {r.get('direction')}"
                     f"{'' if r.get('verify_status') == 'VERIFIED' else '  [' + str(r.get('verify_status')) + ']'}")
            L.append(f"       before: {b.get('score', '-')} vs floor {b.get('floor', '-')} "
                     f"({b.get('floor_name', '-')})")
            L.append(f"       now:    {n.get('score', '-')} vs floor {n.get('floor', '-')} "
                     f"({n.get('floor_name', '-')})")
        L.append(f"   retractions: {p.get('n_retracted')}   rows drifted: {p.get('drifted')}")

    o = s.get("organs") or {}
    L.append("")
    L.append("B. BRAIN ORGAN MAP")
    if o.get("status") != "OK":
        L.append(f"   {o.get('status')}: {o.get('detail')}")
    else:
        reg = o.get("registry") or {}
        L.append(f"   {o.get('n_organs')} organs ({o.get('n_from_map')} from the map, "
                 f"{o.get('n_overlay')} newer than it). {o.get('n_missing')} not built. "
                 f"{reg.get('n_brain_structure')} of {reg.get('n_rows')} registry rows name a "
                 f"brain structure; {reg.get('n_no_brain_structure')} deliberately do not.")
        for r in (o.get("rows") or [])[:14]:
            L.append(f"   {r.get('id', '?'):<6} {str(r.get('plain_name'))[:44]:<46} "
                     f"built {str(r.get('built')):<8} {str(r.get('state'))[:30]:<32} "
                     f"{r.get('measured') or ''}")

    fd = s.get("fidelity") or {}
    L.append("")
    L.append("C. HOW CLOSELY WE COPY THE BRAIN (not how well it works)")
    if fd.get("status") == "MISSING":
        L.append(f"   MISSING: {fd.get('detail')}")
    else:
        L.append(f"   !! {str(fd.get('validation_verdict'))[:300]}")
        for r in fd.get("rows") or []:
            pct = r.get("pct")
            L.append(f"   {('%.0f%%' % (pct * 100)) if isinstance(pct, (int, float)) else '  ?':>5}"
                     f"  {str(r.get('component'))[:44]:<46} {str(r.get('outcome'))[:70]}")
        L.append(f"   organ divergence: {fd.get('divergence_counts')}")
    return "\n".join(L)


def self_test() -> int:
    """Two properties, both proven against the real code path.

      NORMAL   -- against the live repo, so the panels are shown to populate at all.
      ABSENT   -- every required file pointed at a path that does not exist. All three panels must
                  still return, must say MISSING, must invent nothing, and must not raise.

    The degraded case is the one that matters: a collector that only works on healthy data is a
    collector that goes blank at 3am, which is exactly when the data is not healthy."""
    import tempfile
    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    # ---- NORMAL ---------------------------------------------------------
    t0 = time.time()
    a = collect()
    took = time.time() - t0
    check(took < 10.0, f"normal: collected in {took:.2f}s (must stay cheap enough for a refresh)")
    check(a["progress"].get("status") == "OK",
          f"normal: panel A populated ({a['progress'].get('status')}: "
          f"{str(a['progress'].get('detail'))[:120]})")
    check(a["organs"].get("status") == "OK",
          f"normal: panel B populated ({a['organs'].get('status')})")
    check(a["organs"].get("n_from_map", 0) >= 30,
          f"normal: the organ map parsed (got {a['organs'].get('n_from_map')} organs from it)")
    check(not a["organs"].get("missing_required"),
          f"normal: every organ the owner named is present "
          f"(missing: {a['organs'].get('missing_required')})")
    check(a["fidelity"].get("status") in ("OK", "PARTIAL"),
          f"normal: panel C populated ({a['fidelity'].get('status')})")

    # THE RULE. No progress row may show a `now` score with no floor and no explicit marker.
    bad = [r.get("title") for r in (a["progress"].get("components") or [])
           + (a["progress"].get("phases") or [])
           if isinstance(r.get("now"), dict) and r["now"].get("score")
           and not r["now"].get("floor") and r["now"].get("floor_name") in (None, "")]
    check(not bad, f"normal: no row shows a score without a floor or an explicit marker ({bad})")

    # THE OTHER RULE. Panel C must state on screen that the score is not a prediction.
    v = str(a["fidelity"].get("validation_verdict") or "")
    check("UNVALIDATED" in v.upper(),
          f"normal: panel C carries the UNVALIDATED verdict on screen (got {v[:80]!r})")
    check("NOT a measure of how well" in str(a["fidelity"].get("headline")),
          "normal: panel C's headline separates fidelity from performance")

    # Drift: every transcribed literal must still be findable in its authority.
    check(not a["progress"].get("drifted"),
          f"normal: every quoted number is still findable in its source doc "
          f"(drifted: {a['progress'].get('drifted')})")
    check(not a["organs"].get("drifted"),
          f"normal: every overlay organ's quoted number still found "
          f"(drifted: {a['organs'].get('drifted')})")

    # The backlog count is REPORTED, not hidden.
    reg = a["organs"].get("registry") or {}
    check(isinstance(reg.get("n_no_brain_structure"), int)
          and reg["n_no_brain_structure"] > 0,
          f"normal: the empty-brain_structure backlog is reported, not hidden "
          f"(got {reg.get('n_no_brain_structure')})")

    # ---- ABSENT ---------------------------------------------------------
    td = Path(tempfile.mkdtemp(prefix="status_organs_selftest_"))
    g = globals()
    keep = {k: g[k] for k in ("ORGAN_MAP_DOC", "PROGRESS_SPEC", "ORGAN_SPEC", "REGISTRY",
                              "AUTHORITY_DOCS")}
    try:
        g["ORGAN_MAP_DOC"] = td / "nope_ORGAN_MAP.md"
        g["PROGRESS_SPEC"] = td / "nope_progress.json"
        g["ORGAN_SPEC"] = td / "nope_organs.json"
        g["REGISTRY"] = td / "nope_registry.jsonl"
        g["AUTHORITY_DOCS"] = [td / "nope_STATUS.md", td / "nope_PLAN.md"]
        _cache.clear()
        t0 = time.time()
        b = collect()
        took_b = time.time() - t0
    finally:
        g.update(keep)
        _cache.clear()
    check(took_b < 10.0, f"files-absent: returned in {took_b:.2f}s, did not hang")
    check(b["progress"].get("status") == "MISSING",
          f"files-absent: panel A says MISSING (got {b['progress'].get('status')!r})")
    check(not b["progress"].get("components"),
          "files-absent: panel A invents no component rows")
    check(b["organs"].get("status") == "MISSING",
          f"files-absent: panel B says MISSING (got {b['organs'].get('status')!r})")
    check(not b["organs"].get("rows"), "files-absent: panel B invents no organ rows")
    check(b["fidelity"].get("status") in ("OK", "PARTIAL", "MISSING"),
          "files-absent: panel C resolves without raising")
    # Panel C's tool is a MODULE, so it survives the documents vanishing -- but its per-organ
    # divergence table comes from the map and MUST go MISSING with it.
    check(not b["fidelity"].get("divergence"),
          "files-absent: panel C's per-organ table empties instead of showing a stale one")
    txt = render_text(b)
    check("MISSING" in txt, "files-absent: the rendered view SAYS MISSING to the reader")

    # ---- GARBAGE --------------------------------------------------------
    # A structurally wrong spec must not be rendered as data.
    gd = td / "garbage.json"
    try:
        gd.write_text('{"components": "not a list", "phases": 42, "retractions": null}',
                      encoding="utf-8")
        g["PROGRESS_SPEC"] = gd
        _cache.clear()
        c = collect_progress()
    finally:
        g.update(keep)
        _cache.clear()
    check(c.get("status") == "OK" and c.get("components") == [] and c.get("phases") == [],
          f"garbage-spec: wrong types render as EMPTY, never as rows "
          f"(components={c.get('components')!r})")

    # ---- PARSER ---------------------------------------------------------
    # The parser must not silently return nothing on a document it does not recognise.
    fake = "## 4. THE ORGAN MAP\n\n### Z. GROUP\n\nnot an organ header\n"
    check(parse_organ_map(fake) == [], "parser: an unrecognised document yields no organs")
    tiny = ("## 4. THE ORGAN MAP\n\n### A. G\n\n**A1 - Test organ**\n"
            "- **BRAIN'S MATH:** UNPINNED entirely\n"
            "- **OURS:** `hdlab/nope.py` something\n"
            "- **FIDELITY:** WRONG-OP, badly\n- **WIRED:** YES\n"
            "- **EVIDENCE:** self-test PASS. NO FLOOR - UNTESTED.\n\n## 5. NEXT\n")
    one = parse_organ_map(tiny)
    check(len(one) == 1 and one[0]["id"] == "A1", "parser: reads a well-formed organ")
    check(one[0]["fidelity_class"] == "WRONG-OP" and one[0]["axis_shape"] == "DIVERGES",
          "parser: fidelity class maps onto the shape/position/metric axes")
    check(one[0]["brain_math_pinned"] is False,
          "parser: UNPINNED brain math is recorded as unpinned, not scored")
    check(one[0]["floor_named"] is False and "NO FLOOR" in one[0]["measured"].upper(),
          f"parser: a NO-FLOOR evidence line is reported as such "
          f"(got {one[0]['measured']!r})")
    check(parse_organ_map("") == [], "parser: an empty document yields no organs, not a crash")

    print(f"[self-test] temp dir left in place by design: {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Progress / organ-map / fidelity collectors")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    s = collect()
    print(json.dumps(s, indent=2, default=str) if args.json else render_text(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
