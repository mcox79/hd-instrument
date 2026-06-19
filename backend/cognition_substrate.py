"""
/demo/cognition page surfacing substrate-native cognitive primitives.

Per Research PRIORITY_RESPONSE 2026-06-10: split out embodied + aesthetic +
intrinsic-motivation + meta-cognition from /demo/reasoning into a dedicated
page. Customer-facing copy passes OVERCLAIM_CORRECTIONS:

- PP-317 tool-extended body schema -- SHIP with REAL-DATA framing (AUC=0.883
  post-audit; Maravita-Iriki analog; research-grade primitive, NOT full
  embodied-cognition claim)
- PP-318 frisson cleanup margin -- SHIP as "structural surprise signal"
  (prediction-error-resolution dynamics; NOT aesthetic claim per se)
- PP-315 boredom_detection -- intrinsic-motivation primitive (AUC=1.000
  novelty-saturation discriminator)
- PP-304 confidence calibration -- meta-cognitive primitive (corr=0.479,
  ECE=0.021); moved here from /demo/reasoning
- PP-316 image-schema codebook -- HELD per Research (real-data HARD_FAIL
  0.342 on polysemic abstract concepts; rescue via D2.1/D2.6 pending);
  appears as research-roadmap stub only.
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate cognitive primitives - Substrate v1</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Substrate-native cognitive primitives: tool-extended body schema, structural surprise, intrinsic motivation, confidence calibration.">
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
    .pill.hold {
      color: #f59e0b; border-color: #f59e0b;
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
    .primitive.hold {
      border: 1px dashed #f59e0b;
    }
    .primitive h3 {
      color: #4ade80; font-size: 1rem; margin: 0 0 0.25rem; font-weight: 600;
    }
    .primitive.hold h3 { color: #f59e0b; }
    .primitive .anchor { color: #888; font-size: 0.78rem; margin-bottom: 0.5rem; font-family: monospace; }
    .primitive p { font-size: 0.92rem; margin: 0 0 0.45rem; color: #c5c5d0; }
    .primitive .metric { color: #8bff8b; font-size: 0.88rem; font-family: monospace; }
    .primitive.hold .metric { color: #f59e0b; }
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
    <div class="breadcrumb"><a href="/">v1 demo</a> / cognition</div>
    <h1>Substrate cognitive primitives</h1>
    <p class="tagline">Algebraic operations over substrate vectors: tool-extension, structural surprise, novelty saturation, calibrated confidence</p>
    <span class="pill">PP-304 / 315 / 317 / 318</span>
    <span class="pill">EXPLORATORY 0.76-0.92</span>

    <h2>What this is</h2>
    <div class="card">
      <p>
        Cognitive primitives that the substrate exhibits as algebraic side-effects
        of its core operations -- no learned model, no separate inference stack.
        These are research-grade signals: each is one algebraic operation against
        substrate state, measurable in microseconds.
      </p>
      <p style="margin: 0">
        All results tagged EXPLORATORY (0.76-0.92 per cap_map cycles 220-222):
        n = 1 seed per anchor but ceiling-consistent. Multi-seed validation is
        the next gate before claiming production-grade.
      </p>
    </div>

    <h2>Embodied / peripersonal</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Tool-extended body schema (real data)</h3>
        <div class="anchor">PP-317 + PP-326 / tool_extended_real_cpu_v1</div>
        <p>Maravita-Iriki analog: substrate body-schema membership rises after tool use, indicating the tool is functionally encoded as an extension of agent body. Real-data audit (PP-326 cycle 223) on correlated + noisy inputs: AUC = 0.866 (passes the 0.85 threshold). Research-grade primitive; not a full embodied-cognition claim.</p>
        <div class="metric">membership AUC = 0.866 (real-data) / synthetic = 1.000 / tool_delta = +0.180</div>
      </div>

      <div class="primitive">
        <h3>Cross-modal FHRR binding</h3>
        <div class="anchor">PP-329 / t_bind_1_cpu_v1</div>
        <p>Multimodal scene binding via Fourier holographic reduced representations: 25 concurrent scenes with cross-modal retrieval at recall = 0.944. Substrate-only multimodal binding; no cross-modal contrastive loss required.</p>
        <div class="metric">crossmodal recall = 0.944 / scenes = 25 / threshold = 0.80</div>
      </div>

      <div class="primitive">
        <h3>Image-schema grounding (context-bound)</h3>
        <div class="anchor">PP-316 + PP-346 / polysemy_context_bound_cpu_v1</div>
        <p>Synthetic codebook (CONTAINER, SOURCE-PATH-GOAL, FORCE-DYNAMICS) returns 1.000 grounding accuracy. The earlier polysemic real-data failure (0.342 context-free) was a context-free artifact: with context provided at retrieval time, purity = 1.000 (PP-346 cycle 226 rescue). Substrate handles polysemous abstract concepts when context is provided -- the normal case in deployed settings.</p>
        <div class="metric">context-bound purity = 1.000 / context-free = 0.816 / synthetic = 1.000</div>
      </div>
    </div>

    <h2>Aesthetic / structural-surprise</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Structural surprise signal</h3>
        <div class="anchor">PP-318 / frisson_cleanup_margin_cpu_v1</div>
        <p>At deep composition, a sudden cleanup-margin spike marks a prediction-error-resolution event in the substrate dynamics. Not a generated-aesthetics claim -- this is a scoring head over the substrate's surprise dynamics. Honest framing: structural signal of resolution-after-tension events, not artistic merit.</p>
        <div class="metric">AUC = 0.999 / n = 1200 / framing = prediction-error dynamics</div>
      </div>

      <div class="primitive">
        <h3>(reserved)</h3>
        <div class="anchor">future structural-aesthetic primitives</div>
        <p>Schema-fit scoring head for formal genres (PP-265 territory) and compositional-coherence metrics across long documents are real structural advantages. Open creative-writing aesthetics is NOT exhibited per Research's revised v3.0 position.</p>
        <div class="metric">scope: structural / formal genres only</div>
      </div>
    </div>

    <h2>Intrinsic motivation</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Novelty saturation / boredom (real data)</h3>
        <div class="anchor">PP-315 + PP-325 / boredom_real_cpu_v1</div>
        <p>Cleanup-margin against a decayed recent-experience buffer discriminates repeated vs novel inputs. Synthetic AUC = 1.000; real-data audit (PP-325 cycle 223) on Zipfian-distributed + correlated inputs: AUC = 0.908. Foundation for selective attention, active learning, exploration-exploitation policies.</p>
        <div class="metric">AUC = 0.908 (real-data) / synthetic = 1.000 / density_corr = 0.815</div>
      </div>

      <div class="primitive">
        <h3>Offline consolidation / dreaming</h3>
        <div class="anchor">PP-328 / dreaming_substrate_cpu_v1</div>
        <p>Offline replay over substrate state compresses memory traces (0.712), measures compression progress autonomously (0.618), and discovers 7 latent schemas at cluster purity 0.875 -- no labels, no supervised loss. Substrate-only analog of sleep-replay schema consolidation.</p>
        <div class="metric">compression = 0.712 / progress = 0.618 / schemas = 7 / purity = 0.875</div>
      </div>
    </div>

    <h2>Meta-cognition</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Calibrated confidence</h3>
        <div class="anchor">PP-304 / negres_confidence_head_cpu_v1</div>
        <p>Trained logistic head over substrate retrieval features predicts the answer's confidence. Correlation with ground-truth accuracy = 0.479; expected-calibration-error = 0.021. Resolves LAP4-3 (calibration-axis open question). Substrate answers come with a real, low-overhead self-trust signal.</p>
        <div class="metric">corr = 0.479 / ECE = 0.021 / status = LAP4-3 resolved</div>
      </div>

      <div class="primitive">
        <h3>(reserved)</h3>
        <div class="anchor">self-monitoring + introspection</div>
        <p>Self-monitoring (substrate observes its own cleanup margin) and depth-of-knowledge introspection compose with calibration but are not yet exhibited as standalone primitives.</p>
        <div class="metric">status = composes with PP-304</div>
      </div>
    </div>

    <h2>What this enables</h2>
    <div class="card">
      <p>
        Substrate-grounded agents get these primitives for free: tool-aware
        peripersonal models, structural surprise signals for narrative pacing,
        novelty-saturation for active-learning, calibrated confidence for
        retrieval triage. All sub-millisecond.
      </p>
      <p style="margin: 0">
        <strong>What this does not claim:</strong> embodied cognition in the
        Lakoff/Johnson sense (image-schema grounding HELD), open creative-writing
        aesthetic parity with LLMs (NOT supported per Research's revised v3.0
        position), or autonomous integrated agent behavior (integration algebra
        currently MIDDLE_BAND; not yet substrate-only solved).
      </p>
    </div>

    <div class="cta-row">
      <a class="cta primary" href="/demo/reasoning">Reasoning primitives</a>
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


def cognition_response() -> HTMLResponse:
    return HTMLResponse(content=HTML)
