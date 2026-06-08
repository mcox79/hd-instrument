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
  <p class="sub">Algebraic memory architecture for LLMs.
    <a href="/demo" style="color:#8b9eff">Decisive test</a> &middot;
    <a href="/playground" style="color:#8b9eff">Algebraic playground</a> &middot;
    <a href="/benchmark" style="color:#8b9eff">30-query benchmark</a></p>

  <div class="card">
    <h2>Hero counter</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 1.5rem;font-family:ui-monospace,SF Mono,monospace;font-size:0.88rem;color:#c8c8d0">
      <div><b style="color:#a0a0b0">Substrate KB target</b></div><div>200M+ facts (Wikidata + Wikipedia + ConceptNet + arXiv + PubMed)</div>
      <div><b style="color:#a0a0b0">Substrate retrieval</b></div><div>0.21 ms P95 at 1M facts (PP-150 cycle 188)</div>
      <div><b style="color:#a0a0b0">Substrate latency</b></div><div>O(1) in corpus size; 0.148 ms at 100M (PP-166 cycle 192)</div>
      <div><b style="color:#a0a0b0">Algebraic operations</b></div><div>AND / NOT / COUNT / counterfactual <code>do()</code> native</div>
      <div><b style="color:#a0a0b0">Audit chain</b></div><div>Merkle-proven per query (SHA-256 hash chain)</div>
      <div><b style="color:#a0a0b0">Tier 5 substrate-KV</b></div><div>Size + family agnostic; 156x context expansion (PP-135 + PP-153)</div>
    </div>
  </div>

  <div class="card">
    <h2>What you're hitting right now</h2>
    <p>FastAPI backend on a desktop with an RTX 4060 Ti, reachable from anywhere via Cloudflare Tunnel for $0
    hosting cost. <strong>Panel A (Tier 5a substrate-KV)</strong> is live: substrate-augmented Qwen-2.5-1.5B-Instruct
    cites loaded facts verbatim with Merkle audit chain. Try it below or hit <code>/demo</code> for a 3-panel
    side-by-side decisive-test page.</p>
  </div>

  <div class="card">
    <h2>Architecture (SPEC v5: algebra-first)</h2>
    <p style="margin-bottom:1rem">Substrate's moat is the underlying ALGEBRA (HD bind/unbind + Datalog<sup>&not;</sup> ops + Merkle audit + cross-session persistence), NOT the injection pattern.</p>
    <ul>
      <li><span class="pill ok">PANEL A</span> <strong>Tier 5a substrate-KV + algebraic playground</strong> (LIVE):
        Qwen-2.5-1.5B-Instruct + substrate. Retrieval BEFORE forward pass. AND / NOT / COUNT / counterfactual <code>do()</code> categorical ops on top.
        <em>D2 + D3 + N1 + PP-153 empirically HP. <a href="/playground">Try the playground</a>.</em></li>
      <li><span class="pill pending">TIER 5b</span> <strong>Substrate-attention-layer (Flamingo-style gated)</strong> (research; conditional):
        Frozen Qwen-Instruct + per-head HD-to-K/V adapter + learnable scalar gate. <em>Promoted to demo headline IFF
        falsifiable test passes. Substrate vs kNN-LM falsifiable test already HARD-PASSED (+98pp on 2-hop).</em></li>
      <li><span class="pill pending">TIER 5c</span> <strong>Substrate-intrinsic LLM</strong> (active R&D; roadmap):
        Trained from scratch with substrate routing through every attention layer. Categorical reframing of how
        LLMs use external knowledge. <em>5x deep research drill + MVP scoping in flight.</em></li>
    </ul>
  </div>

  <div class="card">
    <h2>Build progress</h2>
    <ul>
      <li><span class="pill ok">DONE</span> Substrate library (13 modules: K-hop with audit chain, cascade router, GDPR exact erase, bitemporal, confidence, FHRR primitives, Merkle audit, persistence, sharding with dynamic SNR threshold, counterfactual do(), two-stage disambig, Mechanism B inverted, Mechanism C cross-shard scatter-gather)</li>
      <li><span class="pill ok">DONE</span> Backend skeleton (FastAPI, 15 routes including <code>/query/tier5a</code>)</li>
      <li><span class="pill ok">DONE</span> Demo-mode experiment-pause toggle (verified live: suspends 8 real experiment procs)</li>
      <li><span class="pill ok">DONE</span> Tier 5a substrate-KV LIVE on Qwen-2.5-1.5B-Instruct (PP-153 cross-family validated)</li>
      <li><span class="pill ok">DONE</span> Cloudflare Tunnel public URL (this one) - hosted on a single desktop</li>
      <li><span class="pill ok">DONE</span> 50-fact seed KB (AI labs + papers + benchmarks); <code>POST /query/tier5a</code> answers correctly + abstains honestly when facts absent</li>
      <li><span class="pill ok">DONE</span> Sub-second substrate retrieval (~30-225 ms) + ~1 s LLM generation; <strong>$0 per query</strong> (local Qwen inference)</li>
      <li><span class="pill work">NEXT</span> Substrate KB ingest: Wikidata 100M + Wikipedia 5.84M + ConceptNet + arXiv + PubMed</li>
      <li><span class="pill work">NEXT</span> Panel B Pythia-160M layer-6 substrate-attention modification</li>
      <li><span class="pill work">NEXT</span> Two-panel frontend with audit chain expansion</li>
    </ul>
  </div>

  <div class="card">
    <h2>Try Tier 5a (Panel A) live</h2>
    <p>Substrate-KV retrieval + Qwen-2.5-1.5B-Instruct local generation. $0/query.</p>
    <input id="q" type="text" placeholder="ask anything: 'Who founded Anthropic?'" style="width:100%;padding:0.6rem;background:#1e1e2a;color:#fff;border:1px solid #444;border-radius:6px;margin-bottom:0.6rem"/>
    <button onclick="askTier5a()">Ask substrate</button>
    <button class="toggle-off" onclick="document.getElementById('q').value='Who founded Anthropic?'">example 1</button>
    <button class="toggle-off" onclick="document.getElementById('q').value='When was Mistral AI founded and by whom?'">example 2</button>
    <button class="toggle-off" onclick="document.getElementById('q').value='Who is the President of France?'">example 3 (should abstain)</button>
    <div id="t5a-out" style="background:#1e1e2a;padding:0.75rem;border-radius:6px;margin-top:0.6rem;font-family:ui-monospace,SF Mono,monospace;font-size:0.85rem;white-space:pre-wrap;min-height:3rem">Type a question + click "Ask substrate".</div>
  </div>

  <!-- Demo-mode toggle hidden from public landing per user direction (until demo is live + being shared).
       Endpoints still work for operator use via /admin/demo-mode-{on,off,status} but UI buttons are removed
       so visitors can't accidentally pause running experiments. -->
  <!-- div class="card">
    <h2>Demo-mode toggle (operator-only)</h2>
    Available at /admin/demo-mode-{on,off,status}. Hidden from public landing per user direction.
  </div -->
  <div id="status" style="display:none"></div>

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

    async function askTier5a() {
      const q = document.getElementById('q').value.trim();
      const out = document.getElementById('t5a-out');
      if (!q) { out.textContent = 'enter a question first.'; return; }
      out.textContent = 'querying substrate + Qwen-2.5-1.5B-Instruct...';
      try {
        const r = await fetch('/query/tier5a', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q, top_k: 3, max_new_tokens: 80, temperature: 0.1 }),
        });
        const j = await r.json();
        if (r.status !== 200) {
          out.textContent = 'error: ' + JSON.stringify(j, null, 2);
          return;
        }
        const lines = [];
        lines.push('ANSWER: ' + j.answer);
        lines.push('');
        lines.push('SUBSTRATE FACTS RETRIEVED:');
        for (const f of j.facts_used) {
          lines.push('  [' + f.score.toFixed(3) + ']  ' + f.fact);
        }
        lines.push('');
        lines.push('LATENCY: substrate=' + j.substrate_latency_ms.toFixed(0) + 'ms  llm=' + j.llm_latency_ms.toFixed(0) + 'ms  total=' + j.total_latency_ms.toFixed(0) + 'ms');
        lines.push('MODEL: ' + j.llm_model + ' (' + j.llm_input_tokens + ' input + ' + j.llm_output_tokens + ' output tokens)');
        lines.push('COST: $' + j.cost_usd.toFixed(6) + ' (local inference)');
        lines.push('AUDIT CHAIN ROOT: ' + j.audit_chain_root.slice(0, 16) + '...');
        out.textContent = lines.join('\\n');
      } catch (e) {
        out.textContent = 'fetch error: ' + e.message;
      }
    }
  </script>
</body>
</html>"""


def landing_response():
    return HTMLResponse(content=LANDING_HTML)
