"""
/chat - frontend page for the substrate-first /converse endpoint.

Per Research BUILD_SUBSTRATE_CONVERSE Phase 3:
  - Standard messaging UI
  - User message + substrate response sequence
  - Per-message metadata visible (source / latency / audit chain / confidence)
  - "Talk to substrate" framing as primary
  - Mobile responsive
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse


PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Talk to substrate</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body { background: #0a0a0f; color: #e8e8ed; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; line-height: 1.5; }
    .wrap { max-width: 820px; margin: 0 auto; padding: 1.25rem 1rem 1rem; min-height: 100vh; display: flex; flex-direction: column; }
    header { padding-bottom: 0.75rem; border-bottom: 1px solid #1c1c28; margin-bottom: 1rem; }
    h1 { font-size: 1.4rem; color: #fff; margin: 0 0 0.2rem; font-weight: 600; }
    .tagline { color: #8b9eff; font-size: 0.95rem; margin: 0 0 0.3rem; }
    .sub { color: #888; font-size: 0.82rem; margin: 0; }
    .sub a { color: #8b9eff; text-decoration: none; }
    #chat { flex: 1; overflow-y: auto; padding: 0.5rem 0 1rem; min-height: 280px; }
    .msg { margin-bottom: 1rem; }
    .msg-row { display: flex; gap: 0.5rem; align-items: flex-start; }
    .msg.user .msg-row { flex-direction: row-reverse; }
    .avatar { flex: 0 0 1.6rem; height: 1.6rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; }
    .msg.user .avatar { background: #2563eb; color: #fff; }
    .msg.bot .avatar { background: #14141c; color: #4ade80; border: 1px solid #4ade80; }
    .bubble { max-width: 76%; padding: 0.55rem 0.85rem; border-radius: 12px; font-size: 0.95rem; word-wrap: break-word; white-space: pre-wrap; }
    .msg.user .bubble { background: #2563eb; color: #fff; border-bottom-right-radius: 4px; }
    .msg.bot .bubble { background: #14141c; color: #e8e8ed; border: 1px solid #2a2a36; border-bottom-left-radius: 4px; }
    .meta { font-family: ui-monospace, SF Mono, monospace; font-size: 0.7rem; color: #888; margin-top: 0.3rem; padding-left: 2.1rem; display: flex; flex-wrap: wrap; gap: 0.25rem 0.4rem; }
    .meta-tag { background: #1c1c28; color: #c8c8d0; padding: 0.05rem 0.45rem; border-radius: 4px; }
    .meta-tag.substrate { background: #14401c; color: #4ade80; }
    .meta-tag.llm { background: #3a2a14; color: #fbbf24; }
    .meta-tag.audit { color: #8b9eff; }
    details.audit { margin: 0.35rem 0 0 2.1rem; background: #16161f; border-radius: 6px; border-left: 2px solid #8b9eff; padding: 0.3rem 0.6rem; font-size: 0.74rem; }
    details.audit summary { color: #8b9eff; cursor: pointer; user-select: none; font-size: 0.75rem; }
    details.audit .step { background: #1c1c28; padding: 0.3rem 0.5rem; border-radius: 4px; margin: 0.25rem 0; color: #c8c8d0; font-family: ui-monospace, monospace; font-size: 0.7rem; }
    .input-wrap { display: flex; gap: 0.4rem; padding: 0.5rem 0 0.25rem; border-top: 1px solid #1c1c28; }
    input.msg-input { flex: 1; background: #1c1c28; color: #fff; border: 1px solid #2a2a36; border-radius: 6px; padding: 0.6rem 0.85rem; font-size: 0.95rem; font-family: inherit; }
    input.msg-input:focus { outline: 1px solid #2563eb; }
    button.send { background: #2563eb; color: #fff; border: none; padding: 0.55rem 1.2rem; border-radius: 6px; cursor: pointer; font-size: 0.92rem; font-weight: 500; }
    button.send:hover { background: #1e40af; }
    button.send:disabled { background: #383848; cursor: not-allowed; }
    .quick { display: flex; flex-wrap: wrap; gap: 0.3rem; padding: 0.4rem 0; }
    .quick button { background: #1c1c28; color: #c8c8d0; border: 1px solid #2a2a36; padding: 0.25rem 0.65rem; border-radius: 999px; cursor: pointer; font-size: 0.78rem; }
    .quick button:hover { background: #2a2a3a; }
    .stats { background: #14141c; border: 1px solid #2a2a36; border-radius: 8px; padding: 0.45rem 0.85rem; margin-bottom: 0.5rem; font-family: ui-monospace, SF Mono, monospace; font-size: 0.78rem; color: #888; display: flex; gap: 0.4rem 1.5rem; flex-wrap: wrap; }
    .stats b { color: #c8c8d0; }
    .stats .green { color: #4ade80; }
    .stats .yellow { color: #fbbf24; }
    @media (max-width: 700px) { h1 { font-size: 1.2rem; } .bubble { max-width: 88%; font-size: 0.92rem; } .meta { padding-left: 1.8rem; } .stats { font-size: 0.72rem; gap: 0.3rem 0.9rem; } }
  </style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Talk to substrate</h1>
    <p class="tagline">Substrate IS the AI. The LLM is called only when language generation is genuinely needed.</p>
    <p class="sub"><a href="/">&larr; landing</a> &middot; <a href="/demo">decisive test</a> &middot; <a href="/playground">algebraic playground</a> &middot; <a href="/benchmark">benchmark</a></p>
  </header>
  <div class="stats" id="stats">
    <span><b>session</b>: <span id="stat-session">-</span></span>
    <span><b>turns</b>: <span id="stat-turns">0</span></span>
    <span><b>substrate-direct</b>: <span class="green" id="stat-direct">0</span></span>
    <span><b>llm-mediated</b>: <span class="yellow" id="stat-llm">0</span></span>
    <span><b>avg latency</b>: <span id="stat-avg">-</span></span>
    <span><b>cost saved</b>: <span class="green" id="stat-cost">$0.000</span></span>
  </div>
  <div id="chat"></div>
  <div class="quick">
    <button onclick="quick('Hello!')">Hello</button>
    <button onclick="quick('Who founded Anthropic and when?')">Anthropic founder</button>
    <button onclick="quick('What does the EU AI Act require?')">EU AI Act</button>
    <button onclick="quick('How many facts mention substrate?')">COUNT(substrate)</button>
    <button onclick="quick('Facts about Anthropic but not Claude')">Anthropic NOT Claude</button>
    <button onclick="quick('What is 1234 * 5678?')">Compute</button>
    <button onclick="quick('What if OpenAI had been founded in 2020?')">Counterfactual</button>
    <button onclick="quick('Write me a haiku about substrate')">Creative (calls LLM)</button>
    <button onclick="quick('Who is the current President of France?')">(Honest abstain)</button>
    <button onclick="quick('Thanks!')">Thanks</button>
    <button onclick="quick('Bye')">Bye</button>
  </div>
  <div class="input-wrap">
    <input id="input" class="msg-input" type="text" placeholder="Ask substrate anything..." autocomplete="off"/>
    <button class="send" id="send" onclick="send()">Send</button>
  </div>
</div>
<script>
function esc(s) { return String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
const SESSION_KEY = 'substrate_chat_session_id';
let sessionId = localStorage.getItem(SESSION_KEY);
if (!sessionId) { sessionId = 'sess_' + Math.random().toString(36).slice(2, 12); localStorage.setItem(SESSION_KEY, sessionId); }
document.getElementById('stat-session').textContent = sessionId.slice(-10);
let stats = { turns: 0, direct: 0, llm: 0, lat_total: 0, cost_saved: 0 };
const GPT_4O_COST_PER_TURN_APPROX = 0.0001;
function updateStats() {
  document.getElementById('stat-turns').textContent = stats.turns;
  document.getElementById('stat-direct').textContent = stats.direct;
  document.getElementById('stat-llm').textContent = stats.llm;
  const avg = stats.turns ? (stats.lat_total / stats.turns).toFixed(0) + 'ms' : '-';
  document.getElementById('stat-avg').textContent = avg;
  document.getElementById('stat-cost').textContent = '$' + stats.cost_saved.toFixed(4);
}
function addMessage(role, text, meta) {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  let html = '<div class="msg-row"><div class="avatar">' + (role === 'user' ? 'you' : '*') + '</div><div class="bubble">' + esc(text) + '</div></div>';
  if (role === 'bot' && meta) {
    const sourceClass = (meta.source && meta.source.includes('llm-mediated')) ? 'llm' : 'substrate';
    const sourceLabel = sourceClass === 'llm' ? 'llm-mediated' : 'substrate-direct';
    html += '<div class="meta">';
    html += '<span class="meta-tag ' + sourceClass + '">' + sourceLabel + '</span>';
    html += '<span class="meta-tag">intent: ' + esc(meta.intent || '?') + '</span>';
    html += '<span class="meta-tag">latency: ' + (meta.latency_ms !== undefined ? meta.latency_ms.toFixed(1) + 'ms' : '?') + '</span>';
    if (meta.confidence !== undefined) html += '<span class="meta-tag">conf: ' + meta.confidence.toFixed(2) + '</span>';
    if (meta.audit_chain_root) html += '<span class="meta-tag audit">root: ' + meta.audit_chain_root.slice(0, 10) + '...</span>';
    html += '</div>';
    if (meta.audit_chain && meta.audit_chain.steps) {
      html += '<details class="audit"><summary>Audit chain (' + meta.audit_chain.steps.length + ' steps; Merkle-committed)</summary>';
      for (const step of meta.audit_chain.steps) html += '<div class="step"><b>[' + step.seq + '] ' + esc(step.label) + '</b> &nbsp; ' + esc(JSON.stringify(step.payload).slice(0, 200)) + '</div>';
      html += '</details>';
    }
    if (meta.facts_used && meta.facts_used.length) {
      html += '<details class="audit" style="border-left-color:#4ade80"><summary>Substrate facts used (' + meta.facts_used.length + ')</summary>';
      for (const f of meta.facts_used) {
        const score = f.score !== null && f.score !== undefined ? f.score.toFixed(3) : '-';
        html += '<div class="step"><span style="color:#7080a0">' + score + '</span> &nbsp; ' + esc(f.fact || '') + '</div>';
      }
      html += '</details>';
    }
  }
  div.innerHTML = html;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
async function send() {
  const input = document.getElementById('input');
  const sendBtn = document.getElementById('send');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  addMessage('user', msg, null);
  sendBtn.disabled = true;
  sendBtn.textContent = 'sending...';
  try {
    const r = await fetch('/converse', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message: msg, session_id: sessionId }) });
    const j = await r.json();
    if (r.status !== 200) addMessage('bot', 'error: ' + (j.detail || JSON.stringify(j)), null);
    else {
      addMessage('bot', j.text, j);
      stats.turns += 1;
      stats.lat_total += j.latency_ms || 0;
      if ((j.source || '').includes('llm-mediated')) stats.llm += 1;
      else { stats.direct += 1; stats.cost_saved += GPT_4O_COST_PER_TURN_APPROX; }
      updateStats();
    }
  } catch (e) { addMessage('bot', 'fetch error: ' + e.message, null); }
  finally { sendBtn.disabled = false; sendBtn.textContent = 'Send'; input.focus(); }
}
function quick(t) { document.getElementById('input').value = t; send(); }
document.getElementById('input').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); send(); } });
window.addEventListener('load', () => document.getElementById('input').focus());
</script>
</body>
</html>"""

def chat_response():
    return HTMLResponse(content=PAGE_HTML)
