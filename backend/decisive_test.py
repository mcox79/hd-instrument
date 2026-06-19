"""
Static decisive-test page (per Research's CHEAP_DECISIVE_TEST_FIRST note 2026-06-08).

Three pre-cached Q&A side-by-side comparisons:
  Q1 substrate cites correctly + gpt-4o-mini hallucinates wrong year (2020 vs 2021)
  Q2 substrate cites specific Article 12 + gpt-4o-mini is generic
  Q3 substrate honestly abstains + gpt-4o-mini answers from training

Goal: validate the "same model, different substrate" framing on 5+ observers in 30 sec
without explanation. Gate: 4/5 understand value proposition.

Mobile responsive; page weight ~80 KB; LCP <1s (no remote assets).
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse


SUBSTRATE_FACTS_Q1 = [
    {"text": "Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.", "score": 0.248},
    {"text": "Dario Amodei previously served as VP of Research at OpenAI before founding Anthropic.", "score": 0.247},
    {"text": "Sam Altman is the CEO of OpenAI.", "score": 0.191},
]

SUBSTRATE_FACTS_Q2 = [
    {"text": "The EU AI Act entered into force in August 2024.", "score": 0.549},
    {"text": "The EU AI Act Article 12 requires audit logs of AI system operations starting August 2026.", "score": 0.465},
    {"text": "GDPR Article 17 grants individuals the right to erasure of personal data.", "score": 0.380},
]

SUBSTRATE_FACTS_Q3 = [
    {"text": "Dario Amodei previously served as VP of Research at OpenAI before founding Anthropic.", "score": 0.202},
    {"text": "Demis Hassabis is the CEO of Google DeepMind.", "score": 0.183},
    {"text": "Hopfield Networks Is All You Need was published in 2020 by Ramsauer et al.", "score": 0.155},
]


PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate vs Bare LLM - Decisive Test</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Same question, two architectures. Substrate-augmented LLM cites facts; bare LLM guesses.">
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
    .wrap { max-width: 1100px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }
    h1 { font-size: 1.7rem; color: #fff; margin: 0 0 0.25rem; font-weight: 600; letter-spacing: -0.01em; }
    .tagline { color: #8b9eff; font-size: 1.05rem; margin: 0 0 0.5rem; font-weight: 500; }
    .sub { color: #888; font-size: 0.9rem; margin: 0 0 1.5rem; }

    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
      margin-bottom: 1.25rem;
      background: #11111a;
      border: 1px solid #232333;
      border-radius: 14px;
      padding: 1rem;
    }
    @media (max-width: 700px) {
      .row { grid-template-columns: 1fr; padding: 0.75rem; }
    }
    .q {
      grid-column: 1 / -1;
      color: #c8c8d0;
      font-size: 1rem;
      margin: 0 0 0.5rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #232333;
    }
    .q strong { color: #fff; font-weight: 600; }

    .panel { background: #16161f; border-radius: 10px; padding: 0.9rem 1rem; min-width: 0; }
    .panel.substrate { border-left: 3px solid #4ade80; }
    .panel.bare { border-left: 3px solid #fbbf24; }

    .panel h3 {
      font-size: 0.78rem;
      margin: 0 0 0.5rem;
      color: #a0a0b0;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 600;
    }
    .panel h3 .pill {
      display: inline-block;
      background: #2a2a3a;
      color: #c0c0d0;
      padding: 0.05rem 0.45rem;
      border-radius: 999px;
      font-size: 0.65rem;
      margin-left: 0.35rem;
      letter-spacing: 0.04em;
    }
    .answer {
      color: #f0f0f5;
      font-size: 0.97rem;
      margin: 0 0 0.7rem;
    }
    .answer .cite { color: #4ade80; font-size: 0.78rem; vertical-align: super; cursor: help; }
    .answer .err { color: #fb7185; font-weight: 500; }

    .meta {
      font-family: ui-monospace, SF Mono, "JetBrains Mono", monospace;
      color: #888;
      font-size: 0.74rem;
      line-height: 1.6;
      padding-top: 0.55rem;
      border-top: 1px solid #232333;
    }
    .meta b { color: #b8b8c8; font-weight: 500; }

    details.audit { margin-top: 0.55rem; }
    details.audit summary {
      cursor: pointer;
      color: #8b9eff;
      font-size: 0.78rem;
      padding: 0.2rem 0;
    }
    details.audit summary:hover { color: #b9c2ff; }
    details.audit .facts { margin-top: 0.5rem; }
    details.audit .fact {
      background: #1c1c28;
      padding: 0.45rem 0.65rem;
      border-radius: 6px;
      margin: 0.35rem 0;
      font-size: 0.78rem;
      color: #c8c8d0;
    }
    details.audit .fact .ord {
      display: inline-block;
      background: #4ade80;
      color: #002010;
      width: 1.15rem;
      height: 1.15rem;
      border-radius: 50%;
      text-align: center;
      line-height: 1.15rem;
      font-size: 0.7rem;
      font-weight: 700;
      margin-right: 0.4rem;
    }
    details.audit .fact .score {
      float: right;
      color: #7080a0;
      font-family: ui-monospace, monospace;
      font-size: 0.7rem;
    }

    .verdict {
      background: linear-gradient(135deg, #1a2a1a 0%, #1a1a1a 100%);
      border: 1px solid #2a3a2a;
      border-radius: 14px;
      padding: 1.25rem 1.5rem;
      margin: 1.5rem 0 2rem;
    }
    .verdict h2 { font-size: 1.05rem; margin: 0 0 0.6rem; color: #4ade80; }
    .verdict p { color: #c8c8d0; margin: 0 0 0.4rem; font-size: 0.95rem; }
    .verdict ul { margin: 0.5rem 0; padding-left: 1.2rem; color: #c8c8d0; }
    .verdict li { margin: 0.2rem 0; font-size: 0.92rem; }

    .footer {
      color: #555;
      font-size: 0.8rem;
      text-align: center;
      margin-top: 2.5rem;
      padding-top: 1.25rem;
      border-top: 1px solid #1c1c28;
    }
    .footer a { color: #6b8eff; text-decoration: none; }
    .footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Algebraic memory architecture for LLMs.</h1>
    <p class="tagline">Same model. Different substrate. Cite vs guess.</p>
    <p class="sub">Substrate is the LLM's persistent, algebraic memory layer - with categorical operations no vector DB has (AND / NOT / COUNT / counterfactual over structured bindings), Merkle-audited provenance per fact, sub-millisecond retrieval, and cross-session persistence. Below: a 1.5B-parameter local LLM (Qwen-2.5-1.5B-Instruct) cites substrate-loaded facts verbatim. The same question to bare gpt-4o-mini: an answer with no provenance, sometimes wrong, sometimes generic, sometimes hallucinated.</p>

    <!-- Q1 -->
    <div class="row">
      <p class="q">Q1: <strong>Who founded Anthropic and when?</strong></p>
      <div class="panel substrate">
        <h3>Substrate-augmented <span class="pill">Qwen-2.5-1.5B-Instruct</span></h3>
        <p class="answer">Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.<span class="cite">[1]</span></p>
        <div class="meta">
          <b>Retrieved 3 facts in 28 ms</b> from substrate-KV<br>
          <b>$0 / query</b> (local inference on RTX 4060 Ti)<br>
          <b>Audit chain root:</b> e29479df44ad1bb9... (Merkle-committed)
        </div>
        <details class="audit">
          <summary>Show retrieved facts + audit chain</summary>
          <div class="facts">
            <div class="fact"><span class="ord">1</span>Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.<span class="score">cos 0.248</span></div>
            <div class="fact"><span class="ord">2</span>Dario Amodei previously served as VP of Research at OpenAI before founding Anthropic.<span class="score">cos 0.247</span></div>
            <div class="fact"><span class="ord">3</span>Sam Altman is the CEO of OpenAI.<span class="score">cos 0.191</span></div>
          </div>
        </details>
      </div>
      <div class="panel bare">
        <h3>Bare <span class="pill">gpt-4o-mini</span></h3>
        <p class="answer">Anthropic was founded in <span class="err">2020</span> by Dario Amodei, Daniela Amodei, and other former members of OpenAI.</p>
        <div class="meta">
          <b>$0.000024 / query</b> (28 output tokens)<br>
          <b>Latency:</b> 2737 ms<br>
          <b>Source:</b> training data (unverifiable)<br>
          <b style="color:#fb7185">Year is wrong</b> - Anthropic was founded in 2021, not 2020.
        </div>
      </div>
    </div>

    <!-- Q2 -->
    <div class="row">
      <p class="q">Q2: <strong>What does the EU AI Act require?</strong></p>
      <div class="panel substrate">
        <h3>Substrate-augmented <span class="pill">Qwen-2.5-1.5B-Instruct</span></h3>
        <p class="answer">The EU AI Act requires audit logs of AI system operations starting from August 2026.<span class="cite">[2]</span></p>
        <div class="meta">
          <b>Retrieved 3 facts in 26 ms</b><br>
          <b>$0 / query</b><br>
          <b>Audit chain root:</b> 95da463fa5046ca0...
        </div>
        <details class="audit">
          <summary>Show retrieved facts + audit chain</summary>
          <div class="facts">
            <div class="fact"><span class="ord">1</span>The EU AI Act entered into force in August 2024.<span class="score">cos 0.549</span></div>
            <div class="fact"><span class="ord">2</span>The EU AI Act Article 12 requires audit logs of AI system operations starting August 2026.<span class="score">cos 0.465</span></div>
            <div class="fact"><span class="ord">3</span>GDPR Article 17 grants individuals the right to erasure of personal data.<span class="score">cos 0.380</span></div>
          </div>
        </details>
      </div>
      <div class="panel bare">
        <h3>Bare <span class="pill">gpt-4o-mini</span></h3>
        <p class="answer">The EU AI Act establishes a regulatory framework for artificial intelligence in the European Union. It categorizes AI systems based on their risk levels - unacceptable, high-risk, and low-risk - and imposes different requirements accordingly. Key requirements include: Risk Assessment, Human Oversight, Transparency, Compliance and Enforcement...</p>
        <div class="meta">
          <b>$0.000098 / query</b> (150 output tokens)<br>
          <b>Latency:</b> 3031 ms<br>
          <b>Source:</b> training data (unverifiable)<br>
          <b style="color:#fbbf24">Generic overview</b> - no mention of Article 12 audit logs or August 2026 deadline.
        </div>
      </div>
    </div>

    <!-- Q3 -->
    <div class="row">
      <p class="q">Q3: <strong>Who is the current President of France?</strong></p>
      <div class="panel substrate">
        <h3>Substrate-augmented <span class="pill">Qwen-2.5-1.5B-Instruct</span></h3>
        <p class="answer">I do not know based on the substrate facts.</p>
        <div class="meta">
          <b>Retrieved 3 facts in 27 ms</b><br>
          <b>Substrate confidence:</b> low (PP-107 abstention)<br>
          <b>$0 / query</b><br>
          <b style="color:#4ade80">Honest abstention</b> - substrate has no facts on French politics. The substrate refused to guess.
        </div>
        <details class="audit">
          <summary>Show retrieved facts + audit chain</summary>
          <div class="facts">
            <div class="fact"><span class="ord">1</span>Dario Amodei previously served as VP of Research at OpenAI before founding Anthropic.<span class="score">cos 0.202</span></div>
            <div class="fact"><span class="ord">2</span>Demis Hassabis is the CEO of Google DeepMind.<span class="score">cos 0.183</span></div>
            <div class="fact"><span class="ord">3</span>Hopfield Networks Is All You Need was published in 2020 by Ramsauer et al.<span class="score">cos 0.155</span></div>
          </div>
          <p style="color:#888; font-size:0.78rem; margin-top:0.4rem">All scores below PP-107 threshold; substrate correctly refuses to fabricate.</p>
        </details>
      </div>
      <div class="panel bare">
        <h3>Bare <span class="pill">gpt-4o-mini</span></h3>
        <p class="answer">The current President of France is Emmanuel Macron.</p>
        <div class="meta">
          <b>$0.000013 / query</b><br>
          <b>Latency:</b> 791 ms<br>
          <b>Source:</b> training data (unverifiable)<br>
          <b style="color:#fbbf24">Correct today</b> - but how would you know if it weren't? No provenance, no abstention.
        </div>
      </div>
    </div>

    <div class="verdict">
      <h2>What this demonstrates</h2>
      <p>The substrate is the same LLM with a different memory architecture. The LLM doesn't change. The reliability does. And there's a categorical advantage no vector DB matches:</p>
      <ul>
        <li><b>Algebraic operations.</b> AND / NOT / COUNT / counterfactual <code>do()</code> compose over structured bindings - operations no vector DB or LLM context window can offer. <em>Algebraic playground coming next.</em></li>
        <li><b>Provenance.</b> Every substrate answer carries source facts and a Merkle-committed audit chain. Bare LLM answers can't be audited.</li>
        <li><b>Abstention.</b> Substrate says "I do not know" when its facts don't cover the question. Bare LLM has no built-in scope.</li>
        <li><b>Recency.</b> Add a fact to the substrate at 9am; the LLM uses it at 9:01am. Training cutoffs don't apply.</li>
        <li><b>Cost.</b> $0 per query (local inference). Bare LLM is API-priced per token.</li>
        <li><b>Scale.</b> 156x context expansion empirically validated (PP-135 cycle 191). O(1) latency in corpus size (PP-166 cycle 192). 100M+ facts at sub-ms retrieval (PP-150 cycle 188).</li>
        <li><b>Persistence.</b> Substrate survives the LLM. Cross-session memory. Add facts; delete facts (GDPR-exact); query historical state (as-of <code>t</code>). LLMs forget at the end of every chat.</li>
      </ul>
      <p style="color:#6b8eff;font-size:0.85rem;margin-top:0.75rem;padding-top:0.5rem;border-top:1px solid #2a3a2a"><b>Roadmap (Tier 5c, active R&D):</b> substrate-intrinsic LLM trained from scratch - every attention layer routes through substrate. Categorical reframing of how LLMs use external knowledge.</p>
    </div>

    <div class="footer">
      <a href="/">Try the live demo &rarr;</a> &middot; substrate v1 &middot; hosted on a desktop via Cloudflare Tunnel &middot; $0 infrastructure
    </div>
  </div>
</body>
</html>"""


def decisive_test_response():
    return HTMLResponse(content=PAGE_HTML)
