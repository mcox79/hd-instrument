"""
/demo/lifecycle page surfacing substrate continual-learning primitives.

Per Research PRIORITY_RESPONSE 2026-06-10: split lifecycle / continual-learning
primitives out of /demo/reasoning into a dedicated page. Research labeled
this "continual learning 4/4 substrate-native" as a defensible commercial claim.

Primitives:
- PP-319 frequency-selective decay (AUC=0.886; hi-freq retained=0.929 vs
  lo-freq=0.051) -- partially addresses an OVERCLAIM_CORRECTIONS continual-
  learning gap noted earlier today (frequency selectivity was flagged absent)
- PP-320 intentional forgetting (retained=1.000, forgotten=0.004; zero
  collateral) -- foundation for selective unlearning, compliance / GDPR
- PP-322 neurogenesis (recall=1.000, 8 of 8 shards discovered; 8x over
  single-shard baseline) -- online capacity expansion
- d2_1 dual-CLS (MIDDLE_BAND): fast-store + slow-store synergy, +4pp lift over
  slow alone. Annotation reference (not a top-level PP row).

Honesty footer per OVERCLAIM_CORRECTIONS: substrate has hippocampal fast-store
analog; full Complementary Learning Systems equivalence remains open (cortical
slow-generalizer + frequency-selectivity-as-architecture not yet substrate-only).
"""
from __future__ import annotations
from fastapi.responses import HTMLResponse


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Substrate lifecycle primitives - Substrate v1</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Substrate continual-learning primitives: frequency-selective decay, intentional forgetting, neurogenesis, dual-CLS.">
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
    <div class="breadcrumb"><a href="/">v1 demo</a> / lifecycle</div>
    <h1>Substrate lifecycle primitives</h1>
    <p class="tagline">Continual learning suite: frequency-selective decay, intentional forgetting, neurogenesis, complementary stores</p>
    <span class="pill">PP-319 / 320 / 322 + d2_1</span>
    <span class="pill">EXPLORATORY 0.78-0.92</span>

    <h2>What this is</h2>
    <div class="card">
      <p>
        How a substrate-grounded system handles knowledge over time:
        what stays, what fades, what gets added on the fly, what gets
        forcibly removed. Each primitive is one algebraic operation against
        substrate state; no replay buffer, no retraining loop.
      </p>
      <p style="margin: 0">
        All results tagged EXPLORATORY (0.78-0.92 per cap_map cycle 222):
        n = 1 seed but ceiling-consistent. Multi-seed validation is the next
        gate before claiming production-grade.
      </p>
    </div>

    <h2>Continual learning suite (cycle 222)</h2>
    <div class="primitive-grid">
      <div class="primitive">
        <h3>Intentional forgetting</h3>
        <div class="anchor">PP-320 / d2_7_intentional_forgetting_cpu_v1</div>
        <p>Targeted deletion of a marked subset of atoms, with zero collateral damage on retained atoms. Foundation for selective unlearning (compliance / GDPR-adjacent), consolidation policies, and trauma-cleared retraining.</p>
        <div class="metric">retained recall = 1.000 / forgotten recall = 0.004</div>
      </div>

      <div class="primitive" style="border: 1px dashed #f59e0b;">
        <h3 style="color: #f59e0b;">Frequency-selective decay (HOLD)</h3>
        <div class="anchor">PP-319 / d2_2_frequency_decay_cpu_v1</div>
        <p>Synthetic claim (AUC = 0.886 on independent inputs) does NOT survive real-data audit. Real-data audit (cycle 224 LVH-276): AUC = 0.590 on correlated Zipfian inputs -- below the 0.85 threshold. Customer-facing claim withdrawn until a context-bound rescue validates.</p>
        <div class="metric" style="color: #f59e0b;">real-data AUC = 0.590 (FAIL) / synthetic = 0.886 / status = HOLD</div>
      </div>

      <div class="primitive">
        <h3>Neurogenesis (online shard creation)</h3>
        <div class="anchor">PP-322 / d2_4_neurogenesis_cpu_v1 + hiermerge rescue</div>
        <p>Synthetic 8-shard discovery hits recall = 1.000 at cluster purity 1.000; 8x capacity vs single shard. Real-data online over-fragments correlated inputs (cycle 224: 54 shards vs 18 truth at purity 0.603). RESCUE-1 hierarchical merge (cycle 227 partial PASS): post-hoc cosine-similarity merge restores purity to 1.000 with count 13 vs K=12 (off-by-one). Online discovery + post-hoc merge is the deploying recipe.</p>
        <div class="metric">synthetic = 1.000 (full) / online + hiermerge real-data: purity 1.000, count 13 vs K=12</div>
      </div>

      <div class="primitive">
        <h3>Dual-substrate CLS (rescued)</h3>
        <div class="anchor">PP-359 / cls_rescue4_plus_rescue2_cpu_v1</div>
        <p>The naive two-substrate architecture fails at both axes (recent=0.689 / old=0.378; stable across 5 seeds). The cycle-229 rescue closes it: asymmetric capacity (fast N=2048, slow N=8192) combined with offline consolidation passes brings BOTH axes to 1.000, seed-robust across 5 seeds. Substrate supports the full CLS pattern: fast recency buffer + slow durable store + offline consolidation policy.</p>
        <div class="metric">recent recall = 1.000 / old consolidated = 1.000 / 5-seed-robust / N_fast=2048 N_slow=8192</div>
      </div>
    </div>

    <h2>Why this matters</h2>
    <div class="card">
      <p>
        LLMs without external memory rewrite every weight on every fine-tune.
        Vector databases have no native concept of forgetting or decay -- you
        either keep everything or rebuild indexes. Substrate has 4 in-algebra
        operations for the actual lifecycle of knowledge.
      </p>
      <p style="margin: 0">
        Combined with the GDPR exact-erasure primitive (PP-229; 0.058 ms;
        deletion-certificate verifiable) and the per-token audit chain
        (PP-261), substrate is the only system in our stack that handles
        the full data lifecycle algebraically: add, decay, forget, expand,
        and prove deletion.
      </p>
    </div>

    <h2>What this does not claim</h2>
    <div class="card">
      <p>
        Per Research's revised v3.0 position (OVERCLAIM_CORRECTIONS 2026-06-10):
        substrate has the hippocampal fast-store analog and avoids McCloskey-Cohen
        catastrophic forgetting. <strong>Full Complementary Learning Systems
        equivalence (McClelland 1995) is not yet substrate-only solved</strong> -- the
        cortical slow-generalizer alongside the fast store is an open architectural
        question. Dual-CLS above is a first step at MIDDLE_BAND, not a final answer.
      </p>
      <p style="margin: 0">
        Schema preservation under correlated real-encoder outputs is empirically
        unconfirmed at production scale. Multi-seed validation across PP-319 / 320 / 322
        is the next gate.
      </p>
    </div>

    <h2>v3.2 wrapper-layer primitives (cycle 228)</h2>
    <div class="card">
      <p>
        Sprint-4 added an engineered wrapper layer over the FHRR algebra. No
        algebra changes -- each primitive is a routing / policy choice composed
        on top of the substrate. Demonstrates that several "missing features"
        were engineering choices, not algebraic limits.
      </p>
    </div>

    <div class="primitive-grid">
      <div class="primitive">
        <h3>Write-lock immutable regions</h3>
        <div class="anchor">PP-353 / write_lock_threshold_cpu_v1</div>
        <p>Wrapper routing refuses writes to locked shards. Locked memory survives 4000 subsequent writes at recall = 1.000 vs baseline collapse (0.000). Foundation for protected reference facts, constitutional constraints, compliance anchors. Seed-robust at n = 5 (std = 0.0).</p>
        <div class="metric">locked recall = 1.000 / baseline = 0.000 / writes survived = 4000 / 5-seed std = 0.0</div>
      </div>

      <div class="primitive">
        <h3>Reed-Solomon erasure coding</h3>
        <div class="anchor">PP-354 / fhrr_rs_parity_cpu_v1</div>
        <p>FHRR additive bundles support exact phase-domain erasure coding. R = 2 parity shards via Vandermonde matrix recover lost data shards at recall = 1.000. Standard Reed-Solomon coding applies directly in phase space -- data-center-grade fault tolerance intrinsic to the algebra.</p>
        <div class="metric">recovered recall = 1.000 / K = 6 / R = 2 parity / threshold = 0.95</div>
      </div>

      <div class="primitive">
        <h3>Per-tier importance policy</h3>
        <div class="anchor">PP-355 / per_tier_importance_cpu_v1</div>
        <p>Three-way differential refresh policy by access tier: Tier-1 always protected (1.000), Tier-3 accessed retained via refresh (1.000), Tier-3 unaccessed faded (0.004). Importance-weighted memory retention mimicking cognitive salience.</p>
        <div class="metric">tier-1 = 1.000 / tier-3 accessed = 1.000 / tier-3 unaccessed = 0.004</div>
      </div>

      <div class="primitive">
        <h3>Per-role domain isolation</h3>
        <div class="anchor">PP-356 / per_role_substrate_cpu_v1</div>
        <p>Per-domain substrates prevent compositional crosstalk -- each role gets its own substrate; routing wrapper enforces isolation. +22.6pp recall over shared substrate. Multi-tenant isolation at role level (agent roles, application contexts, data domains). Seed-robust at n = 5.</p>
        <div class="metric">per-role = 1.000 / shared = 0.774 / isolation delta = +0.226 / 5-seed std = 0.0</div>
      </div>

      <div class="primitive">
        <h3>v3.2 unified wrapper composition</h3>
        <div class="anchor">PP-357 / v32_unified_wrapper_cpu_v1</div>
        <p>Per-role isolation + write-lock + RS-parity composing in ONE wrapper on FHRR algebra. Demonstrates that the wrapper-layer primitives are not interfering: all three operational gates pass simultaneously. Multi-seed full validation queued (n = 1 currently).</p>
        <div class="metric">per_role = 1.000 / write_lock = 0.999 / rs_parity = 1.000</div>
      </div>

      <div class="primitive">
        <h3>3x soft redundancy</h3>
        <div class="anchor">PP-358 / 3x_redundant_substrate_FULL_cpu_v1</div>
        <p>3x mirrored copies with averaging recovers recall from 0.706 to 0.987 under corruption. Complementary to hard RS-parity. Full run (cycle 229) confirms smoke result; LVH-279 closed.</p>
        <div class="metric">3x recall = 0.987 / single-copy = 0.706 / status = full validated</div>
      </div>
    </div>

    <div class="cta-row">
      <a class="cta primary" href="/demo/reasoning">Reasoning primitives</a>
      <a class="cta secondary" href="/demo/cognition">Cognitive primitives</a>
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


def lifecycle_response() -> HTMLResponse:
    return HTMLResponse(content=HTML)
