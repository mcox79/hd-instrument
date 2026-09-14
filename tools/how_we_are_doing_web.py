"""tools/how_we_are_doing_web.py -- the "how we're doing" view as a plain web page, and the ONE parser
both views share.

WHY THIS FILE EXISTS (two jobs, deliberately in one file so there is no third module to keep in step):

  1. THE PARSER.  `parse_doc()` turns notes/HOW_WE_ARE_DOING.md into a small section model
     (goal, position, plan stages, what moved, what is running, next, risks).  `tools/scorecard_gui.py`
     imports it -- the Tkinter window and this web page therefore always show the same thing.
  2. THE REMOTE PATH.  The owner's window is Tkinter, so over Tailscale it only exists inside an RDP
     session on the machine that runs it.  This serves the same content as ONE self-contained HTML
     page (standard library only, no external assets, no fonts, no CDN) so it can be read from a phone
     or a laptop on the tailnet without a remote desktop.

Run it:
    .venv/Scripts/python.exe tools/how_we_are_doing_web.py                 # http://127.0.0.1:8787
    .venv/Scripts/python.exe tools/how_we_are_doing_web.py --bind 100.x.y.z   # the Tailscale address
    .venv/Scripts/python.exe tools/how_we_are_doing_web.py --self-test     # renders the page, no socket

Every path is resolved from this file's own location, so the repo can sit anywhere (it moved from
D: to C: once already, and moves to the desktop next).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC_PATH = REPO / "notes" / "HOW_WE_ARE_DOING.md"
TREND_PATH = REPO / "notes" / "BOARD_TREND.jsonl"

# The eight headings the two views render. Anything else in the file is ignored, so the strategy
# session can leave notes in it without breaking either view.
SECTION_ORDER = [
    "GOAL",
    "POSITION",
    "WHERE WE ARE ON THE PLAN",
    "WHAT MOVED THIS WEEK",
    "WHAT IS RUNNING",
    "NEXT",
    "RISKS AND CORRECTIONS",
]

# The status vocabulary of column 2 of the plan table -> (colour for the window, colour for the page,
# how urgent it is). Order matters: the longest phrases are matched first.
STATUS_STYLES = [
    ("NOT STARTED", "#9a9a9a", "#8b8b8b"),
    ("NEXT FRONT", "#8ab4f8", "#1f6feb"),
    ("IMPROVING", "#8ab4f8", "#1f6feb"),
    ("AT RISK", "#ef6e6e", "#c62828"),
    ("SOLID", "#7ccf8a", "#1e7c38"),
    ("WEAK", "#f0b35b", "#b26a00"),
]
DEFAULT_STATUS = ("#e8e8e8", "#333333")


# ---------------------------------------------------------------------------- parsing
def status_style(status: str) -> tuple[str, str, str]:
    """(keyword, dark-theme colour, light-theme colour) for a plan-table status cell."""
    up = (status or "").strip().upper()
    for key, dark, light in STATUS_STYLES:
        if up.startswith(key):
            return key, dark, light
    return up.split()[0] if up else "", DEFAULT_STATUS[0], DEFAULT_STATUS[1]


def _split_sections(text: str) -> dict[str, str]:
    """Split on '## ' headings. Comments and the '# ' title are dropped."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out: dict[str, str] = {}
    name, buf = None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if name is not None:
                out[name] = "\n".join(buf).strip()
            name, buf = m.group(1).strip().upper(), []
        elif name is not None:
            buf.append(line)
    if name is not None:
        out[name] = "\n".join(buf).strip()
    return out


def _bullets(block: str) -> list[str]:
    """'- ' items, with indented continuation lines folded into the item they belong to."""
    items: list[str] = []
    for line in (block or "").splitlines():
        if re.match(r"^\s*[-*]\s+", line):
            items.append(re.sub(r"^\s*[-*]\s+", "", line).strip())
        elif line.strip() and items:
            items[-1] += " " + line.strip()
    return items


def _dated(items: list[str]) -> list[dict]:
    """'2026-09-14 -- text' -> {'date': ..., 'text': ...}; undated items keep an empty date."""
    out = []
    for it in items:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\s*(?:--|—|-|:)\s*(.*)$", it)
        out.append({"date": m.group(1), "text": m.group(2).strip()} if m else {"date": "", "text": it})
    return out


def _table(block: str) -> list[dict]:
    """The plan table: | Stage | Status | How well | What it means |."""
    rows: list[dict] = []
    for line in (block or "").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if set("".join(cells)) <= set("-: "):          # the markdown rule row
            continue
        if cells[0].lower() in ("stage", "step"):      # the header row
            continue
        key, dark, light = status_style(cells[1])
        rows.append({"stage": cells[0], "status": cells[1], "status_key": key,
                     "colour_dark": dark, "colour_light": light,
                     "number": cells[2], "detail": cells[3]})
    return rows


def parse_doc(path: Path | str | None = None) -> dict:
    """The section model both views render. Missing file -> a model that still renders, with a note."""
    p = Path(path) if path else DOC_PATH
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc), "path": str(p),
                "goal": "", "position": "", "stages": [], "moved": [], "running": [], "next": [],
                "risks": [], "sections": {}, "mtime": None}
    secs = _split_sections(raw)
    try:
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    except OSError:
        mtime = None
    return {
        "ok": True,
        "path": str(p),
        "mtime": mtime,
        "sections": secs,
        "goal": " ".join(secs.get("GOAL", "").split()),
        "position": " ".join(secs.get("POSITION", "").split()),
        "stages": _table(secs.get("WHERE WE ARE ON THE PLAN", "")),
        "moved": _dated(_bullets(secs.get("WHAT MOVED THIS WEEK", ""))),
        "running": _bullets(secs.get("WHAT IS RUNNING", "")),
        "next": _bullets(secs.get("NEXT", "")),
        "risks": _bullets(secs.get("RISKS AND CORRECTIONS", "")),
    }


# ---------------------------------------------------------------------------- the board trend
def load_trend(path: Path | str | None = None, keep: int = 24) -> dict:
    """Board history.

    MEASUREMENT HONESTY: runs made on a different number of test questions are NOT comparable, and
    the file contains both (11,218-question runs and 9,300-question ones). So every point carries
    `comparable` = "was this run on the same set of questions as the most recent run?", and only
    comparable points are joined by the line. The rest are drawn hollow and disconnected.
    """
    p = Path(path) if path else TREND_PATH
    points: list[dict] = []
    try:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                agg = row.get("agg") or {}
                if agg.get("model") is None:
                    continue
                points.append({"ts": (row.get("ts") or "")[:16].replace("T", " "),
                               "commit": (row.get("commit") or "")[:9],
                               "n": agg.get("n"), "model": agg.get("model"),
                               "floor": agg.get("floor"), "twin": agg.get("twin"),
                               "n_sep": agg.get("n_sep"), "n_dims": agg.get("n_dims"),
                               "dims": row.get("dims") or {}})
    except OSError:
        return {"ok": False, "points": [], "path": str(p)}
    points = points[-keep:]
    latest_n = points[-1]["n"] if points else None
    for pt in points:
        pt["comparable"] = (pt["n"] == latest_n)
    return {"ok": bool(points), "points": points, "path": str(p), "latest_n": latest_n,
            "latest": points[-1] if points else None}


def trend_delta(trend: dict) -> tuple[float | None, str]:
    """Change in the board since the previous COMPARABLE run, in words."""
    pts = [p for p in trend.get("points", []) if p.get("comparable")]
    if len(pts) < 2:
        return None, "no earlier run on the same questions"
    d = pts[-1]["model"] - pts[-2]["model"]
    if abs(d) < 0.0005:
        return d, "unchanged since the previous run on the same questions"
    return d, "%s %.1f of a point since the previous run on the same questions" % (
        "up" if d > 0 else "down", abs(d) * 100)


# ---------------------------------------------------------------------------- HTML rendering
def _e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _sparkline_svg(trend: dict, width: int = 920, height: int = 170) -> str:
    """Inline SVG. First and last values are labelled (Few's rule: a trend line needs magnitude)."""
    pts = trend.get("points") or []
    if len(pts) < 2:
        return '<p class="dim">Not enough full checks on record to draw a trend yet.</p>'
    pad_l, pad_r, pad_t, pad_b = 52, 168, 16, 34   # right margin holds the "simple rules NN in 100" label
    vals = [p["model"] for p in pts] + [p["floor"] for p in pts if p["floor"] is not None]
    lo, hi = min(vals), max(vals)
    span = max(hi - lo, 0.02)
    lo, hi = lo - span * 0.25, hi + span * 0.25
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b

    def x(i):
        return pad_l + (iw * i / max(len(pts) - 1, 1))

    def y(v):
        return pad_t + ih - ih * (v - lo) / (hi - lo)

    parts = ['<svg viewBox="0 0 %d %d" width="100%%" height="%d" role="img" '
             'aria-label="board score over the last %d full checks">' % (width, height, height, len(pts))]
    # the floor: a grey band baseline, drawn first so the model line reads as "distance above it"
    fl = [(x(i), y(p["floor"])) for i, p in enumerate(pts) if p["floor"] is not None]
    if len(fl) > 1:
        parts.append('<polyline fill="none" stroke="#b9b9b9" stroke-width="1.5" stroke-dasharray="4 3" points="%s"/>'
                     % " ".join("%.1f,%.1f" % q for q in fl))
        parts.append('<text x="%.1f" y="%.1f" class="lbl dim">simple rules %.0f in 100</text>'
                     % (fl[-1][0] + 6, fl[-1][1] + 4, pts[-1]["floor"] * 100))
    # the model: only comparable points are connected
    run: list[tuple[float, float]] = []
    for i, p in enumerate(pts):
        if p["comparable"]:
            run.append((x(i), y(p["model"])))
        else:
            if len(run) > 1:
                parts.append('<polyline fill="none" stroke="#2f7d4f" stroke-width="2.5" points="%s"/>'
                             % " ".join("%.1f,%.1f" % q for q in run))
            run = []
    if len(run) > 1:
        parts.append('<polyline fill="none" stroke="#2f7d4f" stroke-width="2.5" points="%s"/>'
                     % " ".join("%.1f,%.1f" % q for q in run))
    for i, p in enumerate(pts):
        cx, cy = x(i), y(p["model"])
        if p["comparable"]:
            parts.append('<circle cx="%.1f" cy="%.1f" r="3" fill="#2f7d4f"><title>%s  %.0f in 100  '
                         '(%s questions, commit %s)</title></circle>'
                         % (cx, cy, _e(p["ts"]), p["model"] * 100, "{:,}".format(p["n"] or 0), _e(p["commit"])))
        else:
            parts.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="#ffffff" stroke="#9a9a9a" stroke-width="1.5">'
                         '<title>%s  %.0f in 100 -- a DIFFERENT set of %s questions, not comparable</title></circle>'
                         % (cx, cy, _e(p["ts"]), p["model"] * 100, "{:,}".format(p["n"] or 0)))
    first, last = pts[0], pts[-1]
    parts.append('<text x="%.1f" y="%.1f" class="lbl" text-anchor="end">%.0f</text>'
                 % (x(0) - 8, y(first["model"]) + 4, first["model"] * 100))
    parts.append('<text x="%.1f" y="%.1f" class="lbl strong">%.0f in 100</text>'
                 % (x(len(pts) - 1) + 8, y(last["model"]) + 4, last["model"] * 100))
    parts.append('<text x="%.1f" y="%d" class="lbl dim">%s</text>' % (pad_l, height - 8, _e(first["ts"])))
    parts.append('<text x="%.1f" y="%d" class="lbl dim" text-anchor="end">%s</text>'
                 % (x(len(pts) - 1), height - 8, _e(last["ts"])))
    parts.append("</svg>")
    return "".join(parts)


def _details(summary: str, items, count_note: str = "", open_first: int = 0) -> str:
    """Progressive disclosure: the first `open_first` items are visible, the rest fold away."""
    items = list(items)
    if not items:
        return '<section class="card"><h2>%s</h2><p class="dim">Nothing recorded.</p></section>' % _e(summary)
    head, tail = items[:open_first], items[open_first:]
    out = ['<section class="card"><h2>%s%s</h2>' % (_e(summary), (' <span class="dim">%s</span>' % _e(count_note)) if count_note else "")]
    if head:
        out.append('<ul class="items">%s</ul>' % "".join("<li>%s</li>" % _e(i) for i in head))
    if tail:
        out.append('<details><summary>%d more</summary><ul class="items">%s</ul></details>'
                   % (len(tail), "".join("<li>%s</li>" % _e(i) for i in tail)))
    out.append("</section>")
    return "".join(out)


CSS = """
:root{color-scheme:light dark}
*{box-sizing:border-box}
body{margin:0;padding:0 16px 48px;font:16px/1.5 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
     background:#f6f6f4;color:#1b1b1b}
.wrap{max-width:1000px;margin:0 auto}
header.band{padding:24px 0 12px}
.goal{font-size:14px;color:#5c5c5c;max-width:78ch}
.position{font-size:23px;line-height:1.35;font-weight:600;margin:12px 0 0;max-width:44ch}
@media(min-width:700px){.position{max-width:70ch}}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 0}
.chip{background:#fff;border:1px solid #e0e0dc;border-radius:10px;padding:8px 14px}
.chip b{display:block;font-size:22px;line-height:1.1}
.chip span{font-size:12px;color:#5c5c5c}
.card{background:#fff;border:1px solid #e0e0dc;border-radius:12px;padding:16px 18px;margin:16px 0}
h2{font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#5c5c5c;margin:0 0 12px}
.stages{display:grid;gap:10px;grid-template-columns:1fr}
@media(min-width:760px){.stages{grid-template-columns:repeat(7,1fr)}}
.stage{border:1px solid #e4e4e0;border-radius:10px;padding:10px;background:#fcfcfb;
       border-top:4px solid var(--c)}
.stage .nm{font-weight:600;font-size:13px;line-height:1.25;min-height:2.4em}
.stage .st{font-size:11px;font-weight:700;letter-spacing:.05em;color:var(--c);margin-top:6px}
.stage .no{font-size:13px;margin-top:4px;color:#333}
.stage details{margin-top:8px}
.stage summary{font-size:12px;color:#1f6feb;cursor:pointer}
.stage details p{font-size:13px;color:#3a3a3a;margin:6px 0 0}
.items{margin:0;padding-left:20px}
.items li{margin:0 0 8px}
.moved li b{font-variant-numeric:tabular-nums;color:#5c5c5c;font-weight:600;margin-right:6px}
details>summary{cursor:pointer;color:#1f6feb;font-size:14px;margin-top:8px}
.lbl{font:12px -apple-system,"Segoe UI",Roboto,sans-serif;fill:#1b1b1b}
.lbl.dim{fill:#7a7a7a}
.lbl.strong{font-weight:700;fill:#2f7d4f}
.dim{color:#6a6a6a}
footer{color:#7a7a7a;font-size:12px;padding:16px 0 0}
.err{background:#fff2f2;border:1px solid #f0c0c0;color:#9b1c1c}
@media(prefers-color-scheme:dark){
 body{background:#191919;color:#e8e8e8}
 .card,.chip{background:#232323;border-color:#343434}
 .stage{background:#1f1f1f;border-color:#343434}
 .stage .no{color:#d4d4d4}.stage details p{color:#c6c6c6}
 .goal,.chip span,h2,.dim,footer{color:#a0a0a0}
 .lbl{fill:#e8e8e8}.lbl.dim{fill:#9a9a9a}.lbl.strong{fill:#7ccf8a}
 details>summary,.stage summary{color:#8ab4f8}
 .err{background:#3a1f1f;border-color:#6a3030;color:#f0a0a0}
}
"""


def render_html(doc: dict | None = None, trend: dict | None = None) -> str:
    """The whole page, as one self-contained string. No external requests of any kind."""
    doc = doc if doc is not None else parse_doc()
    trend = trend if trend is not None else load_trend()
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           "<title>How we are doing</title><style>%s</style></head><body><div class='wrap'>" % CSS]

    if not doc.get("ok"):
        out.append('<section class="card err"><h2>The live document could not be read</h2><p>%s</p>'
                   "<p>Expected at: %s</p></section>" % (_e(doc.get("error")), _e(doc.get("path"))))

    # --- BAND: goal (small, standing) then position (large, the one thing to read)
    out.append('<header class="band"><div class="goal">%s</div><p class="position">%s</p>'
               % (_e(doc.get("goal")), _e(doc.get("position"))))
    latest = (trend or {}).get("latest")
    if latest:
        d, words = trend_delta(trend)
        arrow = "" if d is None or abs(d) < 0.0005 else (" ▲" if d > 0 else " ▼")
        out.append('<div class="chips">')
        out.append('<div class="chip"><b>%.0f in 100%s</b><span>the board overall &middot; %s</span></div>'
                   % (latest["model"] * 100, arrow, _e(words)))
        if latest.get("floor") is not None:
            out.append('<div class="chip"><b>%.0f in 100</b><span>what simple rules get on the same questions</span></div>'
                       % (latest["floor"] * 100))
        if latest.get("n_sep") is not None:
            out.append('<div class="chip"><b>%s of %s</b><span>parts of the board clearly better than simple rules</span></div>'
                       % (latest["n_sep"], latest.get("n_dims", "?")))
        out.append('<div class="chip"><b>%s</b><span>test questions in the last full check</span></div>'
                   % "{:,}".format(latest.get("n") or 0))
        out.append("</div>")
    out.append("</header>")

    # --- THE PLAN: the chain as a strip, each stage a colour, a number, and detail on demand
    stages = doc.get("stages") or []
    if stages:
        out.append('<section class="card"><h2>Where we are on the plan &mdash; a passage of text goes '
                   "left to right through these</h2><div class='stages'>")
        for s in stages:
            out.append('<div class="stage" style="--c:%s"><div class="nm">%s</div>'
                       '<div class="st">%s</div><div class="no">%s</div>'
                       "<details><summary>what this is</summary><p>%s</p></details></div>"
                       % (_e(s["colour_light"]), _e(s["stage"]), _e(s["status"]), _e(s["number"]), _e(s["detail"])))
        out.append("</div></section>")

    # --- TREND
    out.append('<section class="card"><h2>The board over the last %d full checks</h2>%s'
               '<p class="dim">Hollow marks were measured on a different set of questions and are not '
               "joined to the line &mdash; they are not a rise or a fall.</p></section>"
               % (len(trend.get("points") or []), _sparkline_svg(trend)))

    # --- MOVEMENTS, RUNNING, NEXT, RISKS (progressive disclosure on each)
    moved = doc.get("moved") or []
    if moved:
        head, tail = moved[:3], moved[3:]
        out.append('<section class="card"><h2>What moved</h2><ul class="items moved">%s</ul>'
                   % "".join("<li><b>%s</b>%s</li>" % (_e(m["date"]), _e(m["text"])) for m in head))
        if tail:
            out.append('<details><summary>%d earlier</summary><ul class="items moved">%s</ul></details>'
                       % (len(tail), "".join("<li><b>%s</b>%s</li>" % (_e(m["date"]), _e(m["text"])) for m in tail)))
        out.append("</section>")
    out.append(_details("What is running right now", doc.get("running") or [], open_first=99))
    out.append(_details("What is next", doc.get("next") or [], open_first=3))
    out.append(_details("Risks and corrections", doc.get("risks") or [], open_first=2))

    out.append('<footer>Written by the strategy session in notes/HOW_WE_ARE_DOING.md%s. '
               "Page built %s. Reload for the current version.</footer>"
               % ((" (last edited %s)" % _e(doc["mtime"])) if doc.get("mtime") else "",
                  datetime.now().strftime("%Y-%m-%d %H:%M")))
    out.append("</div></body></html>")
    return "".join(out)


# ---------------------------------------------------------------------------- the server
class Handler(BaseHTTPRequestHandler):
    server_version = "how-we-are-doing/1.0"

    def do_GET(self):  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            body = render_html().encode("utf-8")
            ctype = "text/html; charset=utf-8"
        elif path == "/doc.json":
            body = json.dumps({"doc": {k: v for k, v in parse_doc().items() if k != "sections"},
                               "trend": load_trend()}, indent=1).encode("utf-8")
            ctype = "application/json; charset=utf-8"
        elif path == "/healthz":
            body, ctype = b"ok", "text/plain; charset=utf-8"
        else:
            self.send_error(404, "nothing here but / and /doc.json")
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (datetime.now(timezone.utc).strftime("%H:%M:%S"), fmt % args))


def self_test() -> int:
    doc = parse_doc()
    assert doc["ok"], "notes/HOW_WE_ARE_DOING.md must be readable: %s" % doc.get("error")
    missing = [s for s in SECTION_ORDER if s not in doc["sections"]]
    assert not missing, "missing sections: %s" % missing
    assert doc["goal"] and doc["position"], "GOAL and POSITION must both carry text"
    assert len(doc["position"].split(".")) <= 3, "POSITION should be one sentence"
    assert len(doc["stages"]) >= 5, "the plan needs its stages: %d" % len(doc["stages"])
    for s in doc["stages"]:
        assert s["status_key"] in [k for k, _, _ in STATUS_STYLES], \
            "stage %r has an unknown status %r (allowed: %s)" % (
                s["stage"], s["status"], ", ".join(k for k, _, _ in STATUS_STYLES))
        assert s["number"], "stage %r has no number" % s["stage"]
    assert doc["moved"] and doc["moved"][0]["date"], "WHAT MOVED needs dated entries, newest first"
    assert doc["running"] and doc["next"] and doc["risks"], "running / next / risks must not be empty"

    trend = load_trend()
    assert trend["ok"], "notes/BOARD_TREND.jsonl should be readable"
    assert any(p["comparable"] for p in trend["points"]), "no comparable board runs found"
    assert any(not p["comparable"] for p in trend["points"]) or True  # mixed populations are allowed

    page = render_html(doc, trend)
    assert page.startswith("<!doctype html>") and page.rstrip().endswith("</html>")
    for needle in ("Where we are on the plan", "What moved", "What is running", "What is next",
                   "Risks and corrections", "<svg", doc["stages"][0]["stage"]):
        assert needle in page, "the page must render %r" % needle
    assert "http://" not in page and "https://" not in page, "the page must load no external asset"
    assert "<script" not in page.lower(), "the page must carry no script"
    print("[how_we_are_doing_web self-test] PASS: %d sections, %d stages, %d movements, "
          "%d board runs (%d comparable), page %.1f KB, zero external assets"
          % (len(doc["sections"]), len(doc["stages"]), len(doc["moved"]), len(trend["points"]),
             sum(1 for p in trend["points"] if p["comparable"]), len(page) / 1024))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="serve notes/HOW_WE_ARE_DOING.md as one HTML page")
    ap.add_argument("--bind", default="127.0.0.1",
                    help="address to listen on (default 127.0.0.1; pass the machine's Tailscale "
                         "address, e.g. 100.x.y.z, to read it from another device on the tailnet)")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    srv = HTTPServer((a.bind, a.port), Handler)
    print("how we are doing -> http://%s:%d/   (reading %s)" % (a.bind, a.port, DOC_PATH))
    if a.bind == "127.0.0.1":
        print("  this machine only. For another device on the tailnet: --bind <this machine's 100.x.y.z>")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
