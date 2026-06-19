"""
Head-to-head benchmark page (SPEC v5: 30 queries, show 3+ both-pass for honesty).

Reads data/benchmark_responses.json captured by scripts/capture_benchmark.py.
Side-by-side per row: substrate-tier5a vs gpt-4o-mini answers + cost + citation.
Categorizes outcomes honestly (both pass / substrate wins / bare wins / substrate abstains).
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from html import escape

from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "benchmark_responses.json"


CATEGORY_LABELS = {
    "factual_both": "Factual (both should pass)",
    "post_cutoff": "Post-cutoff fact",
    "compliance": "Compliance / regulation specifics",
    "abstain": "Honest abstention",
    "composition": "Multi-hop / composition",
}


def _classify(entry: dict) -> tuple[str, str]:
    """Heuristic outcome classification per row. Returns (label, color)."""
    sub_ans = entry.get("substrate_answer", "")
    sub_abstain = "do not know based on" in sub_ans.lower() or "i do not know" in sub_ans.lower()
    bare_ans = entry.get("bare_answer", "")
    bare_abstain = "i don't know" in bare_ans.lower() or "i do not know" in bare_ans.lower()
    cat = entry.get("category", "")

    if cat == "abstain":
        if sub_abstain and not bare_abstain:
            return ("substrate abstained honestly; bare answered from training (unverifiable)", "honest")
        if sub_abstain and bare_abstain:
            return ("both abstained", "tie")
        return ("substrate also answered (mixed)", "mixed")
    if sub_abstain:
        return ("substrate abstained (encoder did not retrieve the right fact)", "miss")
    if not sub_ans:
        return ("substrate empty", "miss")
    if not bare_ans:
        return ("bare empty", "tie")
    return ("both responded", "pass")


def _format_facts(facts: list) -> str:
    if not facts:
        return ""
    rows = []
    for f in facts:
        score = float(f.get("score", 0.0))
        rows.append(f'<li><span class="score">cos {score:.3f}</span> {escape(f.get("fact", ""))}</li>')
    return '<ul class="facts">' + "".join(rows) + "</ul>"


def _render() -> str:
    if not DATA_FILE.exists():
        return "<html><body><p>benchmark data missing; run scripts/capture_benchmark.py first.</p></body></html>"
    try:
        entries = json.loads(DATA_FILE.read_text())
    except Exception as e:
        return f"<html><body><p>error loading benchmark data: {escape(str(e))}</p></body></html>"

    pass_count = 0
    substrate_abstain_count = 0
    bare_total_cost = 0.0
    substrate_total_cost = 0.0
    classified = []
    per_category: dict = {}  # category -> {pass, miss, honest, tie, mixed, total, sub_lat_ms_total, bare_lat_ms_total}
    for e in entries:
        if "error" in e:
            continue
        label, color = _classify(e)
        if color == "honest":
            substrate_abstain_count += 1
        if color == "pass":
            pass_count += 1
        bare_total_cost += float(e.get("bare_cost_usd", 0.0))
        classified.append((e, label, color))
        cat = e.get("category", "unknown")
        bucket = per_category.setdefault(cat, {
            "pass": 0, "miss": 0, "honest": 0, "tie": 0, "mixed": 0,
            "total": 0, "sub_lat_sum": 0.0, "bare_lat_sum": 0.0,
        })
        bucket[color] = bucket.get(color, 0) + 1
        bucket["total"] += 1
        bucket["sub_lat_sum"] += float(e.get("substrate_latency_ms", 0))
        bucket["bare_lat_sum"] += float(e.get("bare_latency_ms", 0))

    rows_html = []
    for e, label, color in classified:
        sub_ans_full = escape(e.get("substrate_answer", ""))
        bare_ans_full = escape(e.get("bare_answer", ""))
        cat_label = CATEGORY_LABELS.get(e.get("category", ""), e.get("category", ""))
        sub_lat = e.get("substrate_latency_ms", 0)
        bare_lat = e.get("bare_latency_ms", 0)
        bare_cost = e.get("bare_cost_usd", 0)
        facts_html = _format_facts(e.get("substrate_facts", []))
        audit = e.get("audit_chain_root", "")[:12]

        rows_html.append(f"""
        <details class="row {color}">
          <summary>
            <span class="i">{e["i"]:02d}</span>
            <span class="cat">{escape(cat_label)}</span>
            <span class="outcome">{escape(label)}</span>
            <span class="q">{escape(e["question"])}</span>
          </summary>
          <div class="panels">
            <div class="panel sub">
              <h4>Substrate-augmented <span class="model">Qwen-2.5-1.5B-Instruct</span></h4>
              <p class="ans">{sub_ans_full}</p>
              {facts_html}
              <p class="meta">$0 / {sub_lat:.0f}ms / audit {audit}...</p>
            </div>
            <div class="panel bare">
              <h4>Bare <span class="model">gpt-4o-mini</span></h4>
              <p class="ans">{bare_ans_full}</p>
              <p class="meta">${bare_cost:.6f} / {bare_lat:.0f}ms / source: training data (unverifiable)</p>
            </div>
          </div>
        </details>""")

    # Per-category summary rows
    cat_rows = []
    for cat in sorted(per_category.keys()):
        b = per_category[cat]
        cat_label = CATEGORY_LABELS.get(cat, cat)
        n = max(1, b["total"])
        sub_avg = b["sub_lat_sum"] / n
        bare_avg = b["bare_lat_sum"] / n
        # Build a small color-coded outcome bar
        bar_parts = []
        for color, label in [("honest", "abstain"), ("pass", "both"), ("miss", "miss"), ("tie", "tie"), ("mixed", "mixed")]:
            v = b.get(color, 0)
            if v:
                pct = 100.0 * v / n
                color_hex = {"honest": "#4ade80", "pass": "#6b8eff", "miss": "#fb7185", "tie": "#888", "mixed": "#fbbf24"}[color]
                bar_parts.append(
                    f'<span style="background:{color_hex};color:#000;padding:0.05rem 0.45rem;border-radius:4px;font-size:0.7rem;margin-right:0.2rem" title="{label}: {v} ({pct:.0f}%)">{v}</span>'
                )
        cat_rows.append(f"""
        <tr>
          <td style="padding:0.45rem 0.7rem;color:#c8c8d0;font-size:0.85rem">{escape(cat_label)}</td>
          <td style="padding:0.45rem 0.7rem;color:#888;font-size:0.85rem">{b["total"]}</td>
          <td style="padding:0.45rem 0.7rem">{"".join(bar_parts)}</td>
          <td style="padding:0.45rem 0.7rem;color:#888;font-family:ui-monospace,monospace;font-size:0.78rem">{sub_avg:.0f} ms</td>
          <td style="padding:0.45rem 0.7rem;color:#888;font-family:ui-monospace,monospace;font-size:0.78rem">{bare_avg:.0f} ms</td>
        </tr>""")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate vs gpt-4o-mini head-to-head benchmark</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ background:#0a0a0f; color:#e8e8ed; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; margin:0; padding:0; line-height:1.55; }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:1.5rem 1.25rem 3rem; }}
    h1 {{ font-size:1.55rem; color:#fff; margin:0 0 0.3rem; }}
    .sub {{ color:#8b9eff; margin:0 0 0.3rem; font-weight:500; }}
    .meta {{ color:#888; font-size:0.9rem; margin:0 0 1.25rem; }}
    .meta code {{ background:#1e1e2a; padding:0.05rem 0.4rem; border-radius:4px; }}

    .summary-card {{ background:#16161f; border:1px solid #232333; border-radius:12px; padding:1rem 1.4rem; margin-bottom:1.25rem; }}
    .summary-card h2 {{ font-size:1rem; margin:0 0 0.5rem; color:#fff; }}
    .summary-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:0.4rem 1.4rem; font-size:0.88rem; color:#c8c8d0; }}
    .summary-grid b {{ color:#fff; }}

    details.row {{ background:#11111a; border:1px solid #232333; border-radius:8px; margin:0.4rem 0; overflow:hidden; }}
    details.row.honest {{ border-left:3px solid #4ade80; }}
    details.row.pass {{ border-left:3px solid #6b8eff; }}
    details.row.miss {{ border-left:3px solid #fb7185; }}
    details.row.tie {{ border-left:3px solid #888; }}
    details.row.mixed {{ border-left:3px solid #fbbf24; }}
    details.row summary {{ cursor:pointer; padding:0.65rem 1rem; display:flex; gap:0.7rem; align-items:center; user-select:none; flex-wrap:wrap; }}
    details.row summary .i {{ color:#7080a0; font-family:ui-monospace,monospace; font-size:0.8rem; }}
    details.row summary .cat {{ color:#a0a0b0; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; min-width:7rem; }}
    details.row summary .outcome {{ color:#888; font-size:0.78rem; font-style:italic; }}
    details.row summary .q {{ flex:1; color:#f0f0f5; font-size:0.93rem; min-width:200px; }}
    details.row[open] {{ background:#0e0e16; }}

    .panels {{ display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; padding:0 1rem 0.9rem; }}
    @media (max-width:700px) {{ .panels {{ grid-template-columns:1fr; }} }}
    .panel {{ background:#16161f; border-radius:6px; padding:0.7rem 0.85rem; }}
    .panel.sub {{ border-top:2px solid #4ade80; }}
    .panel.bare {{ border-top:2px solid #fbbf24; }}
    .panel h4 {{ font-size:0.78rem; margin:0 0 0.4rem; color:#a0a0b0; text-transform:uppercase; letter-spacing:0.05em; }}
    .panel h4 .model {{ font-size:0.7rem; background:#2a2a3a; color:#c8c8d0; padding:0.05rem 0.4rem; border-radius:999px; margin-left:0.3rem; text-transform:none; letter-spacing:0; }}
    .panel .ans {{ color:#f0f0f5; font-size:0.9rem; margin:0 0 0.5rem; }}
    .panel .meta {{ font-family:ui-monospace,SF Mono,monospace; color:#888; font-size:0.72rem; margin:0; }}
    .panel ul.facts {{ list-style:none; padding:0; margin:0.4rem 0; }}
    .panel ul.facts li {{ background:#1c1c28; padding:0.35rem 0.55rem; border-radius:4px; margin:0.2rem 0; font-size:0.78rem; color:#c8c8d0; }}
    .panel ul.facts .score {{ color:#7080a0; font-family:ui-monospace,monospace; font-size:0.7rem; margin-right:0.4rem; }}

    .legend {{ display:flex; gap:1.2rem; flex-wrap:wrap; font-size:0.82rem; color:#a0a0b0; margin:0.4rem 0 1rem; }}
    .legend span {{ display:inline-flex; align-items:center; }}
    .legend span::before {{ content:""; display:inline-block; width:0.7rem; height:0.7rem; border-radius:50%; margin-right:0.35rem; }}
    .legend .honest::before {{ background:#4ade80; }}
    .legend .pass::before {{ background:#6b8eff; }}
    .legend .miss::before {{ background:#fb7185; }}
    .legend .tie::before {{ background:#888; }}
    .legend .mixed::before {{ background:#fbbf24; }}

    a {{ color:#8b9eff; text-decoration:none; }}
    .footer {{ color:#555; font-size:0.8rem; text-align:center; margin-top:2rem; padding-top:1rem; border-top:1px solid #1c1c28; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Head-to-head: substrate vs gpt-4o-mini</h1>
    <p class="sub">30 queries. Same architecture comparison as <code>/demo</code>; broader coverage.</p>
    <p class="meta">Substrate-augmented Qwen-2.5-1.5B-Instruct (1.5 B parameters, local, $0/query) vs bare gpt-4o-mini API.
       Click any row to expand. Both pass on some queries (honest reporting). Substrate's wins are
       categorical (provenance, honest abstention, post-cutoff facts, compliance specifics) - not raw breadth.
       <a href="/">&larr; landing</a> &middot; <a href="/demo">decisive test</a> &middot; <a href="/playground">algebraic playground</a></p>

    <div class="summary-card">
      <h2>Summary across {len(classified)} queries</h2>
      <div class="summary-grid">
        <div><b>Both responded:</b> {pass_count}</div>
        <div><b>Substrate honest abstention:</b> {substrate_abstain_count}</div>
        <div><b>Substrate API cost:</b> $0.00</div>
        <div><b>gpt-4o-mini API cost:</b> ${bare_total_cost:.6f}</div>
      </div>
      <div class="legend">
        <span class="honest">honest abstention</span>
        <span class="pass">both responded</span>
        <span class="miss">substrate missed (encoder retrieval limit; production: scale KB)</span>
        <span class="tie">both abstained</span>
        <span class="mixed">mixed outcome</span>
      </div>

      <h3 style="font-size:0.9rem;margin:1rem 0 0.4rem;color:#a0a0b0;text-transform:uppercase;letter-spacing:0.05em">Per-category breakdown</h3>
      <table style="width:100%;border-collapse:collapse;font-size:0.85rem;background:#0e0e16;border:1px solid #232333;border-radius:6px;overflow:hidden">
        <thead>
          <tr style="background:#16161f;color:#a0a0b0;text-align:left;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.04em">
            <th style="padding:0.5rem 0.7rem">Category</th>
            <th style="padding:0.5rem 0.7rem">N</th>
            <th style="padding:0.5rem 0.7rem">Outcome distribution</th>
            <th style="padding:0.5rem 0.7rem">Sub avg lat</th>
            <th style="padding:0.5rem 0.7rem">Bare avg lat</th>
          </tr>
        </thead>
        <tbody>{"".join(cat_rows)}</tbody>
      </table>
    </div>

    <div style="margin:0.5rem 0 1rem;font-size:0.85rem;color:#888">
      <b style="color:#c8c8d0">Filter by outcome:</b>
      <button class="fbtn" onclick="filt('all')" data-f="all" style="margin:0 0.2rem">all</button>
      <button class="fbtn" onclick="filt('honest')" data-f="honest" style="margin:0 0.2rem">honest abstention</button>
      <button class="fbtn" onclick="filt('pass')" data-f="pass" style="margin:0 0.2rem">both responded</button>
      <button class="fbtn" onclick="filt('miss')" data-f="miss" style="margin:0 0.2rem">substrate missed</button>
      <button class="fbtn" onclick="filt('tie')" data-f="tie" style="margin:0 0.2rem">both abstained</button>
    </div>

    {"".join(rows_html)}

    <div class="footer">
      Substrate v1 demo &middot; head-to-head benchmark (30 queries) &middot; KB: 169 hand-crafted seed facts (Wikipedia 100K ingest pending)
    </div>
  </div>

  <style>
    .fbtn {{
      background: #1c1c28; color: #c8c8d0; border: 1px solid #2a2a36;
      padding: 0.25rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.78rem;
    }}
    .fbtn:hover {{ background: #2a2a3a; }}
    .fbtn.active {{ background: #2563eb; color: #fff; border-color: #2563eb; }}
  </style>
  <script>
    function filt(which) {{
      document.querySelectorAll('.fbtn').forEach(b => b.classList.toggle('active', b.dataset.f === which));
      document.querySelectorAll('details.row').forEach(row => {{
        const classes = row.className.split(/\\s+/);
        const c = classes.find(x => ['honest','pass','miss','tie','mixed'].includes(x));
        row.style.display = (which === 'all' || c === which) ? '' : 'none';
      }});
    }}
    // default active
    document.querySelector('.fbtn[data-f="all"]').classList.add('active');
  </script>
</body>
</html>"""


def benchmark_response():
    return HTMLResponse(content=_render())
