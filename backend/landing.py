"""
Minimal HTML landing page so the root URL renders something meaningful in a browser.

Full Next.js frontend lands Week 3. This is just so the demo URL doesn't look broken
when someone visits it during dev.
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse

LANDING_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate v1 Demo</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      background: #0a0a0f;
      color: #e8e8ed;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 2rem;
      max-width: 880px;
      margin: 0 auto;
    }
    h1 { color: #fff; font-size: 2rem; margin-bottom: 0.25rem; }
    .sub { color: #888; font-size: 1rem; margin-bottom: 2rem; }
    .card {
      background: #14141c;
      border: 1px solid #2a2a36;
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1rem;
    }
    .ok { color: #4ade80; }
    .warn { color: #fbbf24; }
    .pill {
      display: inline-block;
      padding: 0.15rem 0.65rem;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 500;
      border: 1px solid;
    }
    .pill.ok { color: #4ade80; border-color: #4ade80; }
    .pill.pending { color: #888; border-color: #444; }
    .pill.work { color: #fbbf24; border-color: #fbbf24; }
    code { background: #1e1e2a; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.9rem; }
    h2 { font-size: 1.1rem; margin-top: 0; }
    ul { line-height: 1.7; }
    a { color: #8b9eff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    button {
      background: #2563eb;
      color: #fff;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      margin-right: 0.5rem;
      font-size: 0.9rem;
    }
    button:hover { background: #1e40af; }
    button.toggle-off { background: #404050; }
    #status {
      background: #1e1e2a;
      padding: 0.75rem;
      border-radius: 6px;
      font-family: ui-monospace, SF Mono, monospace;
      font-size: 0.85rem;
      margin-top: 0.5rem;
      white-space: pre-wrap;
    }
    .footer {
      color: #555;
      font-size: 0.8rem;
      text-align: center;
      margin-top: 3rem;
    }
  </style>
</head>
<body>
  <h1>Substrate v1 Demo <span class="pill ok">ONLINE</span></h1>
  <p class="sub">Substrate IS knowledge. LLM IS interface. Full UI lands Week 3.</p>

  <div class="card">
    <h2>What you're hitting right now</h2>
    <p>This is the FastAPI backend running on a desktop with an RTX 4060 Ti.
    It's reachable from anywhere via Cloudflare Tunnel for $0 hosting cost.
    The next 5 weeks add the substrate engine + 3 LLM endpoints + Next.js frontend
    with side-by-side panels and 5 wow moments.</p>
    <p style="color:#888;font-size:0.9rem;margin-top:1rem">Architecture: substrate is a
    sharded FHRR knowledge store providing K-hop traversal with audit chains, GDPR exact
    erasure, bitemporal as-of queries, counterfactual do() operator. The LLM (gpt-4o-mini
    or Claude Haiku) reads from the substrate as external memory beyond its context window.</p>
  </div>

  <div class="card">
    <h2>Tier 5 Sprint architecture (locked 2026-06-08)</h2>
    <p style="margin-bottom:1rem">Two panels, same Pythia, two architectural tiers of substrate integration.
    Substrate IS knowledge. LLM IS interface.</p>
    <ul>
      <li><span class="pill work">PANEL A</span> <strong>Tier 5a substrate-KV</strong> (production-ready):
        Pythia-1.4B + 200M-fact substrate. Substrate provides external persistent memory.
        Retrieval BEFORE forward pass. <em>D2 empirically HP at M=10K (156x context).</em></li>
      <li><span class="pill pending">PANEL B</span> <strong>Tier 5b substrate-attention-layer</strong> (PoC):
        Pythia-160M layer-6 attention modified. K/V come from substrate retrieval, not learned
        projections. Standard softmax(QK^T)V math. <em>Architectural proof for v2.0.</em></li>
    </ul>
  </div>

  <div class="card">
    <h2>Build progress</h2>
    <ul>
      <li><span class="pill ok">DONE</span> Substrate library (13 modules: K-hop with audit chain, cascade router, GDPR exact erase, bitemporal, confidence, FHRR primitives, Merkle audit, persistence, sharding with dynamic SNR threshold, counterfactual do(), two-stage disambig, Mechanism B inverted, Mechanism C cross-shard scatter-gather)</li>
      <li><span class="pill ok">DONE</span> Backend skeleton (FastAPI, 15 routes including <code>/query/tier5a</code>)</li>
      <li><span class="pill ok">DONE</span> Demo-mode experiment-pause toggle (verified live: suspends 8 real experiment procs)</li>
      <li><span class="pill ok">DONE</span> Pythia-1.4B Tier 5a substrate-KV (2.6 GB VRAM on 4060 Ti; 5.5 GB headroom)</li>
      <li><span class="pill ok">DONE</span> Cloudflare Tunnel public URL (this one)</li>
      <li><span class="pill ok">DONE</span> 50-fact seed KB (AI labs + papers + benchmarks; <code>/query/tier5a</code> end-to-end live)</li>
      <li><span class="pill work">NEXT</span> Substrate KB ingest: Wikidata 100M + Wikipedia 5.84M + ConceptNet + arXiv + PubMed</li>
      <li><span class="pill work">NEXT</span> Panel B Pythia-160M layer-6 substrate-attention modification</li>
      <li><span class="pill work">NEXT</span> Two-panel frontend with audit chain expansion</li>
    </ul>
  </div>

  <div class="card">
    <h2>Demo-mode toggle (live test)</h2>
    <p>This pauses all CPU/GPU experiment dispatches while the demo is active. Watchdog
    re-suspends new procs every 30 sec; fail-open after 10 min stale heartbeat.</p>
    <button onclick="hit('/admin/demo-mode-on', 'POST')">Demo mode ON</button>
    <button class="toggle-off" onclick="hit('/admin/demo-mode-off', 'POST')">Demo mode OFF</button>
    <button class="toggle-off" onclick="hit('/admin/demo-mode-status', 'GET')">Check status</button>
    <div id="status">Click a button to see the response.</div>
  </div>

  <div class="card">
    <h2>Substrate-side benchmark numbers (validated public data, cycles 187 + 188)</h2>
    <ul>
      <li><strong>WebQSP</strong> real KG-QA (PP-148): <strong>97.6%</strong> accuracy</li>
      <li><strong>CWQ</strong> complex multi-hop (PP-149): <strong>92.6%</strong></li>
      <li><strong>MuSiQue</strong> harder multi-hop (PP-151): <strong>r@10 = 0.784</strong></li>
      <li><strong>FB15K-237</strong> sharded K-hop: <strong>r@5 = 1.000</strong> (1-hop), 0.705 (2-hop); monolithic collapses to 0.007 = <strong>140x recall gap</strong></li>
      <li><strong>Wikipedia ingest</strong>: 155 articles/sec; r@1 = 0.971; 5.84M projected ~10-12 hr</li>
      <li><strong>Cascade router P95 latency</strong> (PP-150): <strong>0.21 ms at 1M</strong>, <strong>0.36 ms at 10M</strong> facts — scale-invariant</li>
      <li><strong>Cleanup confidence</strong> (PP-107): AUC = 1.0 — substrate abstains honestly when it doesn't know</li>
      <li><strong>Tier-5 substrate-KV</strong> (PP-135): size-agnostic (Pythia 160M / 1.4B / 2.8B all HP) + family-agnostic (Pythia + Qwen 1.5B both HP) — 156x context expansion at M=10K</li>
    </ul>
  </div>

  <div class="card">
    <h2>Raw API</h2>
    <p>Backend endpoints (JSON):</p>
    <ul>
      <li><code>GET <a href="/admin/demo-mode-status">/admin/demo-mode-status</a></code></li>
      <li><code>POST /admin/demo-mode-on</code> / <code>POST /admin/demo-mode-off</code></li>
      <li><code>POST /query</code> (W1 stub; LLM clients land this week)</li>
      <li><code>POST /add_fact</code>, <code>POST /delete_facts</code>, <code>GET /scale_stats</code> (W1 stubs)</li>
    </ul>
  </div>

  <div class="footer">
    v1 demo backend &middot; 0.1.0 &middot; hosted on desktop via Cloudflare Tunnel &middot; $0 infrastructure
  </div>

  <script>
    async function hit(path, method) {
      const status = document.getElementById('status');
      status.textContent = method + ' ' + path + '...';
      try {
        const r = await fetch(path, { method });
        const text = await r.text();
        try {
          const j = JSON.parse(text);
          status.textContent = method + ' ' + path + ' -> ' + r.status + '\\n' + JSON.stringify(j, null, 2);
        } catch (e) {
          status.textContent = method + ' ' + path + ' -> ' + r.status + '\\n' + text;
        }
      } catch (e) {
        status.textContent = 'error: ' + e.message;
      }
    }
  </script>
</body>
</html>"""


def landing_response():
    return HTMLResponse(content=LANDING_HTML)
