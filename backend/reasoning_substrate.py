"""
/demo/reasoning page surfacing substrate-as-reasoning-substrate empirical wins.

Per cycle 220 visibility_decisions 2026-06-10: substrate-native reasoning primitives
all hold at L3 compositional depth (do-calculus / Bayesian / analogical, all gap=0.000)
+ confidence calibration + temporal NOW + multi-hop over composites + shard types at
production scale.

All results tagged EXPLORATORY (0.78-0.92 per cap_map cycles 219-220): n=1 seed each
but ceiling-consistent. Multi-seed validation queued.

Honesty audit (OVERCLAIM_CORRECTIONS 2026-06-10): this page exhibits algebraic
reasoning primitives at depth. It does NOT claim multi-agent game theory, embodied
cognition, end-to-end generation, or LLM aesthetic parity. Those remain open
architectural questions per Research's revised v3.0 position.
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate-as-reasoning-substrate - Substrate v1</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Substrate algebraic reasoning primitives at L3 composition: do-calculus, Bayesian MAP, analogy, confidence, temporal grounding, multi-hop over composites.">
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
    .breadcrumb { font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; }
    .breadcrumb a { color: #8b9eff; text-decoration: none; }
    h1 { font-size: 2.1rem; color: #fff; margin: 0 0 0.4rem; font-weight: 600; letter-spacing: -0.02em; }
    .tagline { color: #4ade80; font-size: 1.1rem; margin: 0 0 1.5rem; font-weight: 500; }
    h2 { font-size: 1.25rem; color: #fff; margin: 1.75rem 0 0.75rem; font-weight: 600; }
    p { color: #d0d0d8; margin: 0 0 1rem; }
    .pill {
      display: inline-block; padding: 0.2rem 0.7rem; border-radius: 999px;
      font-size: 0.8rem; font-weight: 500; border: 1px solid;
      color: #4ade80; border-color: #4ade80; margin-right: 0.4rem;
    }
    .card {
      background: #11111a; border: 1px solid #232333; border-radius: 12px;
      padding: 1.1rem 1.25rem; margin-bottom: 1rem;
    }
    .primitive-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.8rem; margin: 1.5rem 0;
    }
    @media (max-width: 700px) {
      .primitive-grid { grid-template-columns: 1fr; }
    }
    .primitive {
      background: #11111a; border: 1px solid #232333; border-radius: 10px;
      padding: 0.95rem 1.1rem;
    }
    .primitive h3 {
      color: #4ade80; font-size: 1rem; margin: 0 0 0.25rem; font-weight: 600;
    }
    .primitive .anchor { color: #888; font-size: 0.78rem; margin-bottom: 0.5rem; font-family: monospace; }
    .primitive p { font-size: 0.92rem; margin: 0 0 0.45rem; color: #c5c5d0; }
    .primitive .metric { color: #8bff8b; font-size: 0.88rem; font-family: monospace; }
    .footnote { color: #888; font-size: 0.85rem; margin-top: 1rem; }
    .cta-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 1.5rem; }
    .cta {
      display: inline-block; padding: 0.65rem 1.1rem; border-radius: 8px;
      font-weight: 500; text-decoration: none; font-size: 0.95rem;
    }
    .cta.primary { background: #4ade80; color: #0a0a0f; }
    .cta.secondary { background: transparent; color: #e8e8ed; border: 1px solid #444; }
    .footer { color: #888; font-size: 0.85rem; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid #232333; }
    .footer a { color: #8b9eff; text-decoration: none; }
    code { background: #1e1e2a; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.88rem; color: #c5c5d0; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="breadcrumb"><a href="/">v1 demo</a> / reasoning</div>
    <h1>Substrate as reasoning substrate</h1>
    <p class="tagline">Algebraic primitives for do-calculus, Bayesian MAP, analogy, multi-hop, temporal grounding, and confidence -- all at L3 compositional depth</p>
    <span class="pill">PP-303 - PP-312 cycle 220</span>
    <span class="pill">EXPLORATORY 0.78-0.92</span>

    <h2>What this is</h2>
    <div class="card">
      <p>
        Cycle 219 established that substrate compositional recall holds at ceiling
        through L=8 with cascading per-level cleanup. Cycle 220 extends specific
        reasoning primitives into that deep-composition regime. Each primitive is
        an algebraic operation over bound substrate vectors -- not a learned model
        and not an LLM call.
      </p>
      <p style="margin: 0">
        All results below are tagged EXPLORATORY (0.78-0.92 per cap_map cycle 220):
        n = 1 seed each but ceiling-consistent. Multi-seed validation is the next
        gate before claiming production-grade.
      </p>
    </div>

    <h2>Reasoning primitives at L=3 composition</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Multi-hop over composite nodes</h3>
        <div class="anchor">PP-305 / comp23_multihop_composites_cpu_v1</div>
        <p>3-hop K-hop traversal where every node is itself an L=3 composite bound vector. Multi-hop graph traversal and compositional binding compose without interference.</p>
        <div class="metric">recall_cleanup = 1.000 (vs 0.033 no-cleanup) / hops = 3 / NN = 40</div>
      </div>

      <div class="primitive">
        <h3>Do-calculus (Pearl interventional)</h3>
        <div class="anchor">PP-307 / comp22_causal_at_l3_cpu_v1</div>
        <p>Pearl do() operator over L3 composite causal graphs. Intervention semantics preserved through deep composition.</p>
        <div class="metric">recall_l3 = 1.000 / gap_to_flat = 0.000</div>
      </div>

      <div class="primitive">
        <h3>Bayesian MAP</h3>
        <div class="anchor">PP-308 / comp21_bayesian_at_l3_cpu_v1</div>
        <p>Bayesian maximum-a-posteriori inference over L3 composite posteriors. Probabilistic reasoning composes with structural depth at ceiling.</p>
        <div class="metric">recall_l3 = 1.000 / gap_to_flat = 0.000</div>
      </div>

      <div class="primitive">
        <h3>Within-domain analogy</h3>
        <div class="anchor">PP-309 / comp24_analogical_at_l3_cpu_v1</div>
        <p>Proportional analogy A : B :: C : ? via complex-phasor rotation, over L3 composite entities. Extends PP-275 (RotatE-style) into the deep-composition regime.</p>
        <div class="metric">Hits@1 = 1.000 / gap_to_flat = 0.000</div>
      </div>
    </div>

    <h2>Meta-reasoning primitives</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Confidence calibration</h3>
        <div class="anchor">PP-304 / negres_confidence_head_cpu_v1</div>
        <p>Trained logistic head over substrate retrieval features. Predicts answer confidence; ECE measures calibration vs ground-truth accuracy. Resolves LAP4-3.</p>
        <div class="metric">corr = 0.479 / ECE = 0.021</div>
      </div>

      <div class="primitive">
        <h3>Temporal / NOW grounding</h3>
        <div class="anchor">PP-306 / now1_temporal_grounding_cpu_v1</div>
        <p>One algebraic primitive for binding temporal context: an indexical NOW shard anchors time-relative queries and disambiguates polysemous facts by epoch.</p>
        <div class="metric">grounded = 1.000 / disambiguation = 0.993</div>
      </div>
    </div>

    <h2>Domain-specific compositional shards at production scale</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>STORY shards</h3>
        <div class="anchor">PP-310 / comp25_story_shard_l3_cpu_v1</div>
        <p>Narrative-structured shards (setting / character / event hierarchies). 100 shards x 500 atoms = 50,000 narrative atoms retrievable at L3.</p>
        <div class="metric">recall = 1.000 / N = 100 / M = 500</div>
      </div>

      <div class="primitive">
        <h3>PROGRAM shards</h3>
        <div class="anchor">PP-311 / comp26_program_shard_l3_cpu_v1</div>
        <p>Code-AST-structured shards (function / call / argument hierarchies). 50 shards x 100 atoms compose at L3 ceiling.</p>
        <div class="metric">recall = 1.000 / N = 50 / M = 100</div>
      </div>

      <div class="primitive">
        <h3>ARGUMENT shards</h3>
        <div class="anchor">PP-312 / comp27_argument_shard_l3_cpu_v1</div>
        <p>Argumentation-structured shards (claim / evidence / warrant). 50 shards x 20 atoms compose at L3 ceiling. Extends PP-255.</p>
        <div class="metric">recall = 1.000 / N = 50 / M = 20</div>
      </div>

      <div class="primitive">
        <h3>KB-DOMAIN shards</h3>
        <div class="anchor">PP-313 / comp28_kb_shard_l3_cpu_v1</div>
        <p>Feature-indexed knowledge-base shards. 40 shards x 1000 atoms = 40,000 atoms retrievable at L3 shard-level. Extends PP-310/311/312 template to KB domain at higher atom-per-shard count.</p>
        <div class="metric">recall = 1.000 / N = 40 / M = 1000</div>
      </div>
    </div>

    <h2>Composition is genuine, not an artifact (PP-314 cycle 221)</h2>
    <div class="card">
      <p>
        Gap analysis: at story scale (50,000 atoms), a flat bundle index returns
        recall = 0.000 -- complete failure -- while the compositional STORY shard
        (PP-310) returns recall = 1.000. Same domain, same atoms, same N. The only
        difference is the binding structure.
      </p>
      <p>
        Per-domain gaps (cycle 221):
        STORY flat=0.000 vs shard=1.000;
        PROGRAM flat=0.017 vs shard=1.000;
        ARGUMENT flat=0.694 vs shard=1.000.
      </p>
      <p style="margin: 0">
        Confirms that the cycle-220 shard recall results are not artifacts of
        favorable N -- composition delivers a measurable lift over flat indexing.
        Tagged EXPLORATORY (0.82-0.92).
      </p>
    </div>

    <h2>Honest open question (cycle 220 negative result)</h2>
    <div class="card">
      <p>
        <strong>PP-303 / negres_struct_align_cpu_v1 (LVH-274):</strong> structural-phase
        projection was hypothesized to lift cross-domain analogy Hits@1 from 0.400
        baseline to &gt;= 0.40 with a meaningful margin. Empirical result: Hits@1 = 0.402,
        lift = 0.001 -- within binomial noise. The method clears the absolute threshold
        but the lift is essentially zero.
      </p>
      <p style="margin: 0">
        Documented as a negative finding (LVH-274 in cap_map): structural-phase projection
        does NOT meaningfully improve cross-domain analogy. Cross-domain analogy at L3
        remains open; within-domain analogy (PP-309) does succeed at ceiling.
      </p>
    </div>

    <h2>What this enables and what stays open</h2>
    <div class="card">
      <p>
        <strong>Enables:</strong> deep-compositional reasoning over structured KBs
        (parse trees, ontologies, causal graphs, narrative arcs, AST). All primitives
        are sub-millisecond inner-product retrieval over bound substrate vectors. No
        learned-model inference required for the core operations; trained primitives
        (confidence head, structural alignment) supplement.
      </p>
      <p style="margin: 0">
        <strong>Open architectural questions</strong> (per Research's revised v3.0
        position, 2026-06-10): cross-domain analogy via multi-tier abstraction (decisive
        GPU test pending); end-to-end generation algorithm (primitive assembly is itself
        research); lexical fluency at LLM-tier (substrate+LLM hybrid is the answer);
        continual learning at production scale (needs cortical-analog alongside the
        substrate fast-store). These are not exhibited on this page.
      </p>
    </div>

    <h2>Reproducibility</h2>
    <div class="card">
      <p>
        All anchor scripts at <code>exp/comp*_*_cpu_v1/</code> and
        <code>exp/now1_*_cpu_v1/</code>; metrics at <code>data/exp_&lt;name&gt;/metrics.json</code>.
        cap_map cycle 220 commit references PP-303 through PP-312. n = 1 seed each;
        multi-seed validation queued.
      </p>
    </div>

    <div class="cta-row">
      <a class="cta primary" href="/benchmark/fb15k-237">FB15K-237 benchmark</a>
      <a class="cta secondary" href="/chat">Try in /chat</a>
      <a class="cta secondary" href="/">Back to overview</a>
    </div>

    <div class="footer">
      Substrate v1 demo / observable hyperdimensional computing /
      <a href="/api">API</a> /
      <a href="/playground">Playground</a>
    </div>
  </div>
</body>
</html>
"""


def reasoning_response() -> HTMLResponse:
    return HTMLResponse(content=HTML)
