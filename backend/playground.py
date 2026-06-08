"""
Algebraic playground UI page per SPEC v5.

Interactive playground showing substrate's categorical operations no vector DB has:
  - AND (set intersection over fact text)
  - NOT (set difference)
  - COUNT (cardinality)
  - counterfactual do() over a DAG

Each control hits the corresponding /query/tier5a/* endpoint and renders the result.
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse


PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate Algebraic Playground</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body {
      background: #0a0a0f;
      color: #e8e8ed;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 0;
      line-height: 1.55;
    }
    .wrap { max-width: 1000px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }
    h1 { font-size: 1.6rem; color: #fff; margin: 0 0 0.25rem; }
    .sub { color: #8b9eff; font-size: 1rem; margin: 0 0 0.4rem; font-weight: 500; }
    .meta { color: #888; font-size: 0.9rem; margin: 0 0 1.5rem; }

    .card {
      background: #14141c;
      border: 1px solid #2a2a36;
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1rem;
    }
    .card h2 { font-size: 1.05rem; margin: 0 0 0.35rem; color: #fff; }
    .card .info { color: #888; font-size: 0.85rem; margin: 0 0 0.85rem; }

    input, textarea {
      background: #1e1e2a;
      color: #fff;
      border: 1px solid #383848;
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      font-size: 0.92rem;
      font-family: inherit;
      width: 100%;
      margin-bottom: 0.5rem;
    }
    textarea { font-family: ui-monospace, SF Mono, monospace; font-size: 0.85rem; min-height: 6rem; resize: vertical; }
    button {
      background: #2563eb;
      color: #fff;
      border: none;
      padding: 0.55rem 1.1rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.92rem;
      font-weight: 500;
    }
    button:hover { background: #1e40af; }
    button.preset { background: #2a2a3a; color: #c8c8d0; font-size: 0.82rem; padding: 0.35rem 0.7rem; margin: 0 0.3rem 0.3rem 0; }
    button.preset:hover { background: #383848; }

    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
    @media (max-width: 600px) { .row { grid-template-columns: 1fr; } }

    .out {
      background: #1c1c28;
      padding: 0.75rem 1rem;
      border-radius: 6px;
      font-family: ui-monospace, SF Mono, monospace;
      font-size: 0.82rem;
      color: #c8c8d0;
      margin-top: 0.6rem;
      white-space: pre-wrap;
      min-height: 2rem;
      max-height: 24rem;
      overflow-y: auto;
    }
    .footer { color: #555; font-size: 0.8rem; text-align: center; margin-top: 2.5rem; padding-top: 1.25rem; border-top: 1px solid #1c1c28; }
    .footer a { color: #6b8eff; text-decoration: none; }
    a { color: #8b9eff; text-decoration: none; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Algebraic playground</h1>
    <p class="sub">Categorical operations no vector DB has.</p>
    <p class="meta">All ops run against the live substrate KB. Each result returns in
      sub-millisecond. The same operations compose to Datalog<sup>&not;</sup> (Datalog with
      negation as failure), which is what the substrate algebra extends.
      <a href="/">&larr; back to landing</a> | <a href="/demo">decisive test &rarr;</a></p>

    <!-- AND -->
    <div class="card">
      <h2>AND - set intersection</h2>
      <p class="info">Facts containing ALL listed terms (case-insensitive substring match). The substrate
      composes set operations natively. A pure-cosine vector DB cannot express this directly - it only
      does ranked top-K.</p>
      <input id="and-terms" placeholder="e.g. Anthropic, OpenAI" value="Anthropic, OpenAI">
      <div style="margin: 0.3rem 0 0.6rem">
        <button class="preset" onclick="document.getElementById('and-terms').value='Anthropic, OpenAI'">people bridging AI labs</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='Claude, 2025'">Claude 2025 family</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='Mistral, France'">Mistral France</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='founded, 2023'">things founded in 2023</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='EU AI Act, audit'">EU AI Act audit</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='Google, AI'">Google AI products</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='Pythia, substrate'">Pythia substrate</button>
        <button class="preset" onclick="document.getElementById('and-terms').value='CERN, 1989'">CERN 1989</button>
      </div>
      <button onclick="doAnd()">Run AND</button>
      <div id="and-out" class="out">Click "Run AND"...</div>
    </div>

    <!-- NOT -->
    <div class="card">
      <h2>NOT - set difference</h2>
      <p class="info">Facts containing ALL "include" terms but NONE of the "exclude" terms.
      Negation-as-failure - the core of Datalog<sup>&not;</sup> reasoning. No vector DB does this cleanly.</p>
      <div class="row">
        <div>
          <label style="color:#888; font-size:0.8rem">Include (AND):</label>
          <input id="not-include" placeholder="e.g. AI" value="founded">
        </div>
        <div>
          <label style="color:#888; font-size:0.8rem">Exclude (NONE):</label>
          <input id="not-exclude" placeholder="e.g. OpenAI" value="2023">
        </div>
      </div>
      <div style="margin: 0.3rem 0 0.6rem">
        <button class="preset" onclick="document.getElementById('not-include').value='founded'; document.getElementById('not-exclude').value='2023'">founded but NOT in 2023</button>
        <button class="preset" onclick="document.getElementById('not-include').value='AI'; document.getElementById('not-exclude').value='DeepMind'">AI NOT mentioning DeepMind</button>
        <button class="preset" onclick="document.getElementById('not-include').value='2024'; document.getElementById('not-exclude').value='OpenAI'">2024 events NOT OpenAI</button>
        <button class="preset" onclick="document.getElementById('not-include').value='Anthropic'; document.getElementById('not-exclude').value='Claude'">Anthropic facts that are NOT about Claude</button>
        <button class="preset" onclick="document.getElementById('not-include').value='cycle'; document.getElementById('not-exclude').value='multi-hop'">cycle facts NOT multi-hop</button>
        <button class="preset" onclick="document.getElementById('not-include').value='substrate'; document.getElementById('not-exclude').value='K-hop'">substrate NOT K-hop</button>
      </div>
      <button onclick="doNot()">Run NOT</button>
      <div id="not-out" class="out">Click "Run NOT"...</div>
    </div>

    <!-- COUNT -->
    <div class="card">
      <h2>COUNT - cardinality</h2>
      <p class="info">How many facts mention this term? Substrate exposes set sizes natively. Vector
      DBs only return top-K with no exact cardinality - "how many docs match X" needs a scan, not a search.</p>
      <input id="count-term" placeholder="e.g. EU AI Act" value="EU AI Act">
      <div style="margin: 0.3rem 0 0.6rem">
        <button class="preset" onclick="document.getElementById('count-term').value='EU AI Act'">EU AI Act</button>
        <button class="preset" onclick="document.getElementById('count-term').value='Anthropic'">Anthropic</button>
        <button class="preset" onclick="document.getElementById('count-term').value='OpenAI'">OpenAI</button>
        <button class="preset" onclick="document.getElementById('count-term').value='founded'">founded</button>
        <button class="preset" onclick="document.getElementById('count-term').value='Pythia'">Pythia</button>
        <button class="preset" onclick="document.getElementById('count-term').value='substrate'">substrate</button>
        <button class="preset" onclick="document.getElementById('count-term').value='2024'">2024</button>
        <button class="preset" onclick="document.getElementById('count-term').value='Claude'">Claude</button>
        <button class="preset" onclick="document.getElementById('count-term').value='CERN'">CERN</button>
        <button class="preset" onclick="document.getElementById('count-term').value='2021'">2021</button>
      </div>
      <button onclick="doCount()">Run COUNT</button>
      <div id="count-out" class="out">Click "Run COUNT"...</div>
    </div>

    <!-- Counterfactual -->
    <div class="card">
      <h2>Counterfactual do() - Pearl-style intervention</h2>
      <p class="info">Define base facts + a small DAG. Apply a do() intervention; substrate recomputes
      the derived values with a Merkle-committed audit chain. <em>No vector DB does this. No bare LLM offers verifiable provenance.</em>
      Drug interactions, compliance audits, financial scenarios - all collapse to do() on a DAG with
      provable answer.</p>

      <div style="margin: 0.3rem 0 0.6rem">
        <button class="preset" onclick="loadPreset('company')">Company age + founder still CEO</button>
        <button class="preset" onclick="loadPreset('drug')">Drug interaction risk</button>
        <button class="preset" onclick="loadPreset('compliance')">EU AI Act compliance check</button>
        <button class="preset" onclick="loadPreset('budget')">Budget allocation</button>
      </div>

      <textarea id="cf-body">{
  "base_facts": {"founded_year": 2015, "ceo_tenure_years": 8},
  "derived": [
    {"name": "company_age", "formula": "2026 - p['founded_year']", "parents": ["founded_year"]},
    {"name": "founder_still_ceo", "formula": "p['ceo_tenure_years'] >= p['company_age']", "parents": ["ceo_tenure_years", "company_age"]}
  ],
  "intervention": {"founded_year": 2020}
}</textarea>
      <div style="margin-bottom: 0.6rem; color: #888; font-size: 0.78rem">
        Try: change <code>founded_year</code> to 2010, 2015, 2020, 2023 - watch <code>founder_still_ceo</code> flip.
      </div>
      <button onclick="doCounterfactual()">Run counterfactual</button>
      <div id="cf-out" class="out">Click "Run counterfactual"...</div>
    </div>

    <div class="footer">
      Substrate v1 demo &middot; algebraic playground &middot; <a href="/">landing</a> &middot; <a href="/demo">decisive test</a>
    </div>
  </div>

  <script>
    function pre(j) { return JSON.stringify(j, null, 2); }

    async function postJSON(path, body, outId) {
      const out = document.getElementById(outId);
      out.textContent = 'POST ' + path + ' ...';
      try {
        const r = await fetch(path, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
        const j = await r.json();
        out.textContent = pre(j);
      } catch (e) { out.textContent = 'error: ' + e.message; }
    }

    function doAnd() {
      const terms = document.getElementById('and-terms').value.split(',').map(s => s.trim()).filter(Boolean);
      if (terms.length < 2) { document.getElementById('and-out').textContent = 'need >=2 terms'; return; }
      postJSON('/query/tier5a/and', { terms: terms, limit: 20 }, 'and-out');
    }
    function doNot() {
      const inc = document.getElementById('not-include').value.split(',').map(s => s.trim()).filter(Boolean);
      const exc = document.getElementById('not-exclude').value.split(',').map(s => s.trim()).filter(Boolean);
      postJSON('/query/tier5a/not', { include: inc, exclude: exc, limit: 12 }, 'not-out');
    }
    function doCount() {
      const t = document.getElementById('count-term').value.trim();
      postJSON('/query/tier5a/count', { term: t }, 'count-out');
    }
    function doCounterfactual() {
      const text = document.getElementById('cf-body').value;
      let body;
      try { body = JSON.parse(text); }
      catch (e) { document.getElementById('cf-out').textContent = 'JSON parse error: ' + e.message; return; }
      postJSON('/query/tier5a/counterfactual', body, 'cf-out');
    }

    const PRESETS = {
      company: {
        base_facts: { founded_year: 2015, ceo_tenure_years: 8 },
        derived: [
          { name: 'company_age', formula: "2026 - p['founded_year']", parents: ['founded_year'] },
          { name: 'founder_still_ceo', formula: "p['ceo_tenure_years'] >= p['company_age']", parents: ['ceo_tenure_years', 'company_age'] }
        ],
        intervention: { founded_year: 2020 }
      },
      drug: {
        base_facts: { drug_a_dose_mg: 50, drug_b_dose_mg: 30, patient_clearance: 0.7 },
        derived: [
          { name: 'effective_a', formula: "p['drug_a_dose_mg'] * p['patient_clearance']", parents: ['drug_a_dose_mg', 'patient_clearance'] },
          { name: 'effective_b', formula: "p['drug_b_dose_mg'] * p['patient_clearance']", parents: ['drug_b_dose_mg', 'patient_clearance'] },
          { name: 'interaction_index', formula: "p['effective_a'] + p['effective_b'] * 1.4", parents: ['effective_a', 'effective_b'] },
          { name: 'high_risk', formula: "p['interaction_index'] > 60", parents: ['interaction_index'] }
        ],
        intervention: { drug_b_dose_mg: 60 }
      },
      compliance: {
        base_facts: { eu_ai_act_date: 2026, deployment_year: 2025, has_audit_logs: false },
        derived: [
          { name: 'months_until_deadline', formula: "(p['eu_ai_act_date'] - p['deployment_year']) * 12", parents: ['eu_ai_act_date', 'deployment_year'] },
          { name: 'compliant', formula: "p['has_audit_logs'] or p['deployment_year'] >= p['eu_ai_act_date']", parents: ['has_audit_logs', 'deployment_year', 'eu_ai_act_date'] }
        ],
        intervention: { has_audit_logs: true }
      },
      budget: {
        base_facts: { revenue: 1000000, fixed_costs: 400000, hire_count: 5, salary_per_hire: 120000 },
        derived: [
          { name: 'variable_costs', formula: "p['hire_count'] * p['salary_per_hire']", parents: ['hire_count', 'salary_per_hire'] },
          { name: 'total_costs', formula: "p['fixed_costs'] + p['variable_costs']", parents: ['fixed_costs', 'variable_costs'] },
          { name: 'profit', formula: "p['revenue'] - p['total_costs']", parents: ['revenue', 'total_costs'] },
          { name: 'profitable', formula: "p['profit'] > 0", parents: ['profit'] }
        ],
        intervention: { hire_count: 8 }
      }
    };

    function loadPreset(name) {
      const p = PRESETS[name];
      if (!p) return;
      document.getElementById('cf-body').value = JSON.stringify(p, null, 2);
    }
  </script>
</body>
</html>"""


def playground_response():
    return HTMLResponse(content=PAGE_HTML)
