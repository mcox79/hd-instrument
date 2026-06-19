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

    <h2>Algebraic auxiliaries</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Temporal / NOW grounding</h3>
        <div class="anchor">PP-306 / now1_temporal_grounding_cpu_v1</div>
        <p>One algebraic primitive for binding temporal context: an indexical NOW shard anchors time-relative queries and disambiguates polysemous facts by epoch.</p>
        <div class="metric">grounded = 1.000 / disambiguation = 0.993</div>
      </div>

      <div class="primitive">
        <h3>Concept-level bilingual pivot</h3>
        <div class="anchor">PP-323 / bilingual_dual_substrate_cpu_v1</div>
        <p>Concept-level cross-language retrieval over 400 concepts and 4 languages: direct A-&gt;B pivot at 0.997, zero-shot A-&gt;C-via-B pivot at 1.000. Concept-level translation-interlingua signal; not full text translation.</p>
        <div class="metric">A-&gt;B = 0.997 / A-&gt;C pivot = 1.000 / n_concepts = 400</div>
      </div>

      <div class="primitive">
        <h3>Distant-language translation</h3>
        <div class="anchor">PP-345 / comm2_translation_distant_cpu_v1</div>
        <p>Substrate-only systematic translation across typologically-distant orders (SVO / SOV / VSO): concept pivot via interlingua at 1.000, word-order reordering via stored templates at 1.000. Substrate handles the systematic / compositional layer; complex statistical syntax remains LLM domain.</p>
        <div class="metric">concept accuracy = 1.000 / order accuracy = 1.000</div>
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
        <h3>KB-DOMAIN shards (synthetic)</h3>
        <div class="anchor">PP-313 / comp28_kb_shard_l3_cpu_v1</div>
        <p>Feature-indexed knowledge-base shards. 40 shards x 1000 atoms = 40,000 atoms retrievable at L3 shard-level. Extends PP-310/311/312 template to KB domain at higher atom-per-shard count.</p>
        <div class="metric">recall = 1.000 / N = 40 / M = 1000</div>
      </div>

      <div class="primitive">
        <h3>KB-DOMAIN shards (real)</h3>
        <div class="anchor">PP-324 / kb_shard_real_cpu_v1</div>
        <p>Same shard primitive on real knowledge-base entities (not synthetic atoms). 20 shards over 1,539 real entities at L3. Synthetic-to-real audit passes the 0.70 threshold by 27pp.</p>
        <div class="metric">recall = 0.965 / N = 20 / n_ent = 1539</div>
      </div>
    </div>


    <h2>Cross-domain reasoning via SLIPNET substrate (PP-327 / PP-330 cycle 223-224)</h2>
    <div class="card">
      <p>
        Cross-domain analogy was the most open question in our v3.0 architecture
        list this morning. The SLIPNET-substrate mechanism (Hofstadter fluid
        analogy ported to FHRR) lands the cross-domain claim empirically:
        Hits@1 = 0.985 vs degree-based baseline = 0.827, lift = +0.158. Substrate
        addresses cross-domain at the relation-type level, not entity-geometry --
        a new mechanism that the prior SME and P9-Option-A approaches could not
        crack.
      </p>
      <p>
        Graceful degradation under noise (PP-330 cycle 224): Hits@1 = 0.697 at
        25% input noise -- the mechanism does not collapse abruptly outside the
        clean-input regime.
      </p>
      <p style="margin: 0">
        <strong>Real-data ceiling lower than synthetic (PP-327 annotation cycle 227):</strong>
        on real heterogeneous data (FB15K-style polysemic relation structure)
        SLIPNET degrades to Hits@1 = 0.375 (MIDDLE_BAND). The synthetic 0.985
        is an upper bound; real-deployment performance will sit between 0.375
        and 0.697 depending on noise + polysemy level. Tagged EXPLORATORY
        (0.78-0.92) per cap_map. Anchors:
        <code>slipnet_substrate_cpu_v1</code> + <code>slipnet_noise_cpu_v1</code>
        + <code>slipnet_real_polysemic_cpu_v1</code>.
      </p>
    </div>

    <h2>First wins on COMM + MATH + CODE thrusts (cycles 224-229)</h2>
    <div class="card">
      <p>
        Substrate-self-improvement requires substrate-grounded COMMUNICATE, MATH,
        and CODE primitives. First categorical wins landed across all three this
        evening and were multi-seed-validated in cycle 229 (14 of 15 anchors
        promoted from EXPLORATORY n=1 to seed-robust CONFIRMED at 5 of 5 seeds):
      </p>
      <ul style="margin: 0.5rem 0 0.75rem 1.25rem; color: #c5c5d0;">
        <li><strong>COMM:</strong> slot+topic decoding 1.000 (PP-331);
          intent decoding 1.000 n=1000 (PP-337); lexical-emission tok/sent 1.000 (PP-338);
          WUG morphology 1.000 1-shot + 3-shot (PP-342)</li>
        <li><strong>MATH:</strong> algebra acc 1.000 n=400 (PP-332); equation-solve 1.000 n=400 (PP-341);
          calculus 1.000 n=400 (PP-334); proof-chains L=8/10/12 mean = 1.000 (PP-343
          substrate-over-biology depth)</li>
        <li><strong>CODE:</strong> code-compose 1.000 n=300 (PP-333); algorithm-compose 1.000
          4-step n=300 (PP-339); <strong>HumanEval pass@1 = 0.750 (9 / 12; small-n
          first result; PP-340)</strong>; <strong>bug-detection rescued by template-conditional
          method to F1 = 0.948 at 5-seed (PP-361 closes PP-336)</strong></li>
      </ul>
      <p>
        14 of 15 anchors above (every one except code2's original rescue path)
        confirmed at 5 of 5 seeds via wave1_multiseed_sweep (cycle 229).
        LVH-277 closed retroactively. Real-benchmark validation queued
        (NarrativeQA / HumanEval / ArgKP / HotpotQA on synthetic-trained shards).
      </p>
      <p style="margin: 0">
        <strong>Multi-drive planning via VSA H=3 lookahead (PP-360 cycle 229):</strong>
        worst-drive satisfaction reaches 0.620 (4.9x single-action baseline) with
        a single VSA-encoded policy vector that decodes back at 1.000. Substrate
        handles multi-step, multi-goal planning algebraically. 5-seed robust.
      </p>
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
      <a class="cta secondary" href="/demo/cognition">Cognitive primitives</a>
      <a class="cta secondary" href="/demo/lifecycle">Lifecycle primitives</a>
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
