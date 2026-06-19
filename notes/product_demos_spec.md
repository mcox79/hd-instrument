# Product demo specs — top 3 (initial v0, 2026-05-22)

Owner: Session 7 (Product). Re-read every cycle. Specs are
implementable today modulo flagged 🔬-conditional gates (see each
demo's "Failure modes" section + cross-ref to
`product_options_ranked.md`).

**Dual-purpose discipline** (per session_7_product.md): every demo
must serve BOTH (a) the user's discovery of what the substrate lets
us see, AND (b) a specific buyer-pain conversion.

Shared infrastructure (build once, reuse across all three demos):
- `substrate-as-service` REST API: thin wrapper around the remote
  workstation's substrate runtime. Endpoints: `store`, `query`,
  `decompose`, `edit`, `erase`, `verify` (5-probe Mirage),
  `observability/{hessian, ph, cij, pq}`, `snapshot/{pre,post}`.
- Substrate-state snapshot format: JSON over the substrate's
  per-bundle and per-W state, with diffs (pre-edit / post-edit).

Estimated shared-infra effort: **2 weeks**. Counted ONCE; each demo
then claims incremental hours.

---

## Demo 1 — Lane D agent memory SDK + LangChain adapter

### Purpose

- **User-side**: validate Lane D wedge end-to-end in a real agent
  workload (not synthetic Lane D smoke). Surface gaps in: persistence
  across sessions, edit latency, provenance UX, capacity scaling at
  agent-realistic M_stored (target: 1K-10K facts).
- **Customer-side**: prove to an AI-agent-platform engineer that
  substrate replaces their vector-DB-or-Anthropic-Memory-API memory
  layer with edit + erase + provenance capabilities they currently
  lack.

### Substrate capabilities exercised (Tier-1 ✅ only)

- Class 4 cognitive composition: Lane D 4-primitive parallel
  composition FULL (S=0.983 / T=0.978 / U=1.0 / X=1.0); Lane D
  3-stage e2e pipeline FULL (S->T->X = 1.0/1.0/1.0); Lane D N-scaling
  LINEAR FULL c=0.073; Lane D noise robust FULL >99% at 30% bit-flip.
- Class 2 editable memory: Bet A edit-then-query ✅ Tier-1; M up to
  16N at 100-edit smoke; breakpoint at edit 8189.
- Class 3 provenance: pool retrieval (Bet 1 ICL via pool ✅ Tier-1);
  decomposition (decompose_K_cliff ✅ multi-seed).

### Build plan

1. **substrate-as-service REST API** (shared infra; 2 weeks).
2. **`hd_memory` Python SDK package** (2 weeks):
   - Async client with retry / streaming
   - High-level API: `Memory(uri).remember(fact)`, `.query(q)`,
     `.edit(fact_id, new)`, `.erase(fact_id, verify=True)`,
     `.provenance(query_id)`
   - Snapshot + restore primitives
3. **LangChain adapter** (1 week):
   - `HDMemory` subclassing `langchain.memory.BaseMemory`
   - `HDChatMessageHistory` subclassing
     `langchain.schema.BaseChatMessageHistory`
   - Compatibility tests against `ConversationBufferMemory` baseline
4. **Demo notebook** (1 week):
   - Agent loop with a 1K-fact knowledge base
   - User says "actually fact X was wrong, here's the correction"
     -> agent calls `.edit()` -> subsequent queries reflect correction
   - User says "forget that I said Y" -> `.erase(verify=True)` ->
     5-probe Mirage report rendered inline
   - Provenance: agent answers query, hover shows "this came from
     stored facts {f12, f47, f203}" with decomposition cosines
5. **Customer conversation track** (parallel, 2-3 weeks elapsed):
   - 10-15 calls with agent-platform eng leads
   - Validate: pain real? edit + erase + provenance is the
     value-prop? willingness to integrate?

### Effort breakdown

| Component | Engineering | Design | Content / docs | Customer-conv |
|---|---|---|---|---|
| Shared substrate-as-service API | 2 wks | - | 0.25 wk | - |
| `hd_memory` SDK | 2 wks | - | 0.5 wk | - |
| LangChain adapter | 1 wk | - | 0.25 wk | - |
| Demo notebook | 0.75 wk | 0.25 wk | 0.5 wk | - |
| Customer conv | - | - | - | 2-3 wks parallel |
| **Total** | **5.75 wks** | **0.25 wk** | **1.5 wk** | **2-3 wks parallel** |

Total wall-clock: **6-10 weeks** (compatible with rank #1 estimate).

### Success criteria

**Technical**:
- SDK round-trip latency < 500ms for store / query / edit at
  M_stored=1000 facts, N=4096
- LangChain adapter passes `ConversationBufferMemory` baseline
  behavioral parity tests (the substrate variant should match
  baseline on canonical recall + add capabilities)
- 5-probe Mirage erase verification rendered inline in the demo
  notebook with PASS on Lane C compliance smoke metrics

**Product**:
- 3+ agent-platform engineers in target list say "we'd integrate
  this in a sprint if it had X feature" (substrate currently HAS
  most candidate X features — confirms positioning)
- 1+ says "I'd pay for managed-service substrate-as-a-service"
  (validates monetization path)
- 0 engineers say "we already have this" (validates differentiation
  vs Anthropic Memory API + vector DB status quo)

### Failure modes + early-warning signals

- **Substrate cap below agent-realistic**: Bet S K-ceiling N=65536
  FULL ratifies cycle 60 smoke KILL (K_crit ~200). At N=4096 with
  M_stored=10K we'd hit capacity ceiling early. Early-warning:
  pre-build, run a "1K-fact realistic agent" stress test against
  substrate; if fails, scale N to 8192 or 16384 before SDK build.
- **Lane C compliance FULL deviates from smoke**: affects erase
  verification claim. Early-warning: monitor Strategy decision log
  for Lane C compliance FULL verdict.
- **No buyer pain**: 10+ calls return "we use vector DB and it's
  fine." Mitigation: front-load 3-5 customer convos BEFORE SDK
  build; pivot capability mix if pain doesn't validate.
- **LangChain ecosystem fatigue**: integration nice-to-have but not
  conversion. Mitigation: don't gate demo on LangChain; native SDK
  path is primary.
- **Productionization debt**: substrate-as-service running on
  Marshall's workstation isn't 9-5 reliable. Mitigation: scope first
  customer as "low-uptime-tolerance pilot" or move to a small cloud
  VM with substrate compiled CPU.

### What user learns about substrate by building this

- Real-agent M_stored ceilings (1K? 10K?) under realistic query
  distributions (vs Lane D smoke's synthetic distribution).
- Edit + provenance latency at production scale.
- Whether Lane D noise robust at 30% bit-flip survives real-world
  query noise (paraphrase, typos, model-generated rewording).
- Whether the substrate's 4-primitive composition (S/T/U/X) maps
  cleanly to real agent ops or needs new primitives.

---

## Demo 2 — Browser extension forensic-erase demo (substrate-as-service)

### Purpose

- **User-side**: stress-test Lane C compliance smoke in a low-stakes
  publicly-visible context. Surface UX gaps in Mirage 5-probe
  verification (what's confusing? what needs explaining?).
- **Customer-side**: visceral 60-second demo: store a fact, see it
  retrieved, erase it, see all 5 Mirage probes return PASS, see the
  decomposition show "nothing left." Funnel target: drive inbound to
  Demo 1 (Lane D SDK eval) and to Lane C consultation conversations.

### Substrate capabilities exercised (Tier-1 ✅ only)

- Class 1 verifiable erase: Bet 2 GDPR erase ✅ Tier-1; Lane C
  compliance smoke PERFECT (delete_leak=0, edit_acc=1.0,
  kept_acc=1.0, side_effect=0, ECE=0).
- Class 3 provenance: decomposition shows what's stored before/after
  erase; pool retrieval shows the matched bundle indices.

### Build plan

1. **substrate-as-service REST API** (shared infra; counted in Demo
   1).
2. **Web frontend** (1.5 weeks):
   - Single-page app with three pane: "store / query", "erase",
     "5-probe Mirage verification"
   - Live retrieval cosine + decomposition visualization
   - Pre/post-erase decomposition diff rendered as a side-by-side
     histogram
3. **Chrome extension wrapper** (0.5 week):
   - Right-click "store as substrate fact" + sidebar panel
   - Chrome Web Store submission + review wait
4. **Demo asset production** (0.5 week):
   - 60-second screen-capture demo (HN-friendly)
   - Twitter / LinkedIn / HN post copy
   - Paired CTA: "interested in production substrate? -> Lane D SDK
     waitlist" + "interested in compliance use case? -> consultation
     call"

### Effort breakdown

| Component | Engineering | Design | Content | Customer-conv |
|---|---|---|---|---|
| substrate-as-service API (shared; counted in Demo 1) | - | - | - | - |
| Web frontend | 1.5 wks | 0.25 wk | - | - |
| Chrome extension | 0.5 wk | - | 0.25 wk | - |
| Demo assets + posts | - | 0.25 wk | 0.5 wk | - |
| Funnel CTA / waitlist | 0.25 wk | - | 0.25 wk | - |
| **Total** | **2.25 wks** | **0.5 wk** | **1.0 wk** | **0 (passive)** |

Total wall-clock (assuming shared infra reused): **2-4 weeks**.

### Success criteria

**Technical**:
- Erase round-trip < 2s on substrate-as-service for M_stored ~100
  facts, N=4096
- All 5 Mirage probes render with verdict + numeric values
- Pre/post-erase decomposition diff visually obvious (not just
  "numbers got smaller")
- Chrome Web Store review passes

**Product**:
- 1000+ HN / Twitter views in launch week (rough proxy)
- 50+ Lane D SDK waitlist signups
- 5+ Lane C consultation requests (free 30-min calls)
- 0 demo failures during live use (substrate-as-service uptime
  during demo period)

### Failure modes + early-warning signals

- **Lane C compliance FULL deviates from smoke** (smoke-not-
  predictive at 6 anchors). Demo claims must be smoke-qualified.
  Risk: demo shows perfect numbers but FULL verdict later forces a
  walkback. Mitigation: explicit "this is substrate smoke; FULL
  validation pending [link to substrate_capability_map]" in demo
  copy. Honest framing, not marketing.
- **"Cool demo, no conversion"**: high views, zero waitlist
  signups. Mitigation: paired CTA designed in from day 1; if
  signups < 50 in 2 weeks, treat as discovery instrument only and
  don't repeat.
- **Substrate-as-service uptime**: workstation goes down during
  HN frontpage exposure -> reputational hit. Mitigation: deploy
  substrate-as-service to a small cloud VM (CPU-only inference is
  fine for demo scale) before launch.
- **Chrome Web Store rejection**: extensions get rejected for
  ambiguous reasons. Mitigation: skip Chrome extension wrapper if
  review delays > 2 weeks; web-only is fine.

### What user learns about substrate by building this

- Whether Lane C compliance smoke survives **realistic** stores
  (web-clipped text, user-entered facts) vs synthetic-test stores.
- Whether the Mirage 5-probe report is interpretable by
  non-substrate-experts.
- Funnel signal: does erase + provenance resonate with broader
  audience or only with niche compliance/agent buyers?

---

## Demo 3 — User-side observability tool (Hessian VDOS / P(h) / decomposition GUI + Mirage erase view)

### Purpose

- **User-side (PRIMARY)**: instrument the substrate. Replace the
  current "read cap_map + grep metrics.json" workflow with a live
  dashboard that shows substrate state at substrate-physics level
  (Hessian VDOS, P(h), C_ij, P(q)) AND capability-class level
  (Mirage 5-probe verdict, decomposition K-cliff, M_stored vs
  capacity envelope). Surface invisible gaps (e.g., "approaching
  K-cliff," "Bet S K-ceiling proximity," "RS-phase drift").
- **Customer-side (SECONDARY)**: same panels become "compliance
  auditor view" for Lane C buyers. No equivalent exists for
  transformer KV cache or vector DB. Substrate-product-distinctive.

### Substrate capabilities exercised (Tier-1 ✅ + substrate-physics observables)

- Substrate-physics: Hessian VDOS (queued / not-yet-FULL),
  observability suite v1 smoke (C_ij eigvals + P(q) replica + P(h)
  moments, cycle 109; FULL pending cycle 60 note).
- Class 1 erase: 5-probe Mirage verdict visualization.
- Class 2 edit: edit-then-query snapshot diff (Bet A ✅).
- Class 3 provenance: decomposition K-cliff visualization
  (decompose_K_cliff ✅ multi-seed).
- Class 4 composition: Lane D 4-primitive state under load (FULL
  anchors validated).

### Build plan

1. **substrate-as-service observability endpoints** (overlap with
   shared infra; 0.5 week incremental):
   - `observability/hessian_vdos` (when observability suite v1 FULL
     lands; smoke OK for v0 GUI)
   - `observability/ph_moments`
   - `observability/cij_eigvals`
   - `observability/pq_replica`
   - `observability/k_cliff_proximity`
   - `observability/m_stored_vs_capacity`
2. **Dashboard frontend** (2-3 weeks):
   - React (or Svelte) SPA with 4-panel layout:
     - Panel A: substrate-physics live observables (4-family probe
       stack — RS phase certification visualization)
     - Panel B: capacity envelope (M_stored / K-cliff / Bet S
       K-ceiling proximity)
     - Panel C: erase + edit history (with Mirage 5-probe verdicts)
     - Panel D: decomposition explorer (interactive K-vs-N
       visualization)
   - Snapshot pre/post-operation diff with annotation
   - State export (JSON) for forensic audit / compliance reporting
3. **User-side runbook integration** (0.5 week):
   - Daily "what changed" summary at start of work session
   - Anomaly alerts (capacity > 90% envelope; K-cliff proximity;
     RS-phase drift)
4. **Auditor-view documentation** (0.5 week):
   - Sample compliance audit report exported from dashboard
   - Mapping panel-output -> regulatory question (GDPR Art 17 /
     HIPAA / SOX) for the Lane C demo paired with Demo 2 funnel

### Effort breakdown

| Component | Engineering | Design | Content / docs | Customer-conv |
|---|---|---|---|---|
| Observability endpoints (incremental on shared infra) | 0.5 wk | - | 0.25 wk | - |
| Dashboard frontend | 2.5 wks | 0.5 wk | - | - |
| Runbook integration | 0.5 wk | - | 0.25 wk | - |
| Auditor-view docs | - | 0.25 wk | 0.5 wk | - |
| **Total** | **3.5 wks** | **0.75 wk** | **1.0 wk** | **0 (deferred)** |

Total wall-clock: **3-5 weeks**.

### Success criteria

**Technical**:
- Dashboard refresh latency < 1s for all 4 panels
- Snapshot diff renders for any (edit | erase | store-batch)
  operation
- Anomaly alerts fire on K-cliff approach (M_stored / K cross known
  thresholds)
- State export JSON validates against compliance-report schema

**Product (user-side, primary)**:
- User reports faster experiment triage (specific anomaly caught
  early that would have cost a wasted experiment)
- User reports surfacing 1+ substrate gap that wasn't obvious from
  cap_map + metrics.json (the discovery thesis pays out)

**Product (customer-side, secondary, deferred to post-MVP)**:
- Sample compliance audit report shows a Lane C buyer's compliance
  officer says "this is what we'd need from an AI vendor" (1 call
  validates concept)

### Failure modes + early-warning signals

- **Observability suite v1 FULL deviates from smoke**: smoke-not-
  predictive at 6 anchors. Affects panel A's RS-phase certification
  display. Mitigation: smoke-qualify all panel A displays until
  FULL lands; surface conditional in UI.
- **Hessian VDOS not yet integrated**: queued in substrate research
  but not at smoke yet. Mitigation: ship dashboard v0 WITHOUT
  Hessian panel; add when substrate side lands.
- **GUI overhead > value**: 3-5 weeks user effort and the user
  ends up not using the dashboard. Mitigation: build incrementally;
  ship Panel B (capacity envelope) first (highest user-side value);
  iterate based on use.
- **Auditor-view positioning is aspirational**: no buyer says they
  want this. Mitigation: don't gate user-side MVP on customer
  validation; treat auditor-view as upside.

### What user learns about substrate by building this

- Which substrate-physics observables actually matter for
  experiment triage (vs theoretical interest only).
- Whether the 4-family observability suite covers what's needed for
  RS-phase certification at-a-glance, or whether additional probes
  are needed.
- Whether capacity-envelope visualization correctly anticipates
  K-cliff / Bet S K-ceiling proximity in advance of experiments
  hitting them.
- Whether the "compliance auditor view" framing resonates when
  shown to a non-substrate-expert (paired with Demo 2 funnel).

---

## Sequencing recommendation

**Weeks 1-2**: shared substrate-as-service REST API. Required for
all three. Parallel: 5+ customer-discovery calls for Demo 1
(validate agent-platform-eng pain before SDK build).

**Weeks 3-5**: Demo 2 (browser extension demo). Lowest-effort,
fastest user feedback, doubles as funnel-top. Customer-discovery
calls continue.

**Weeks 4-8**: Demo 1 SDK + LangChain adapter. Starts when Demo 2
infra cooks; SDK build doesn't block on Demo 2 launch.

**Weeks 4-8 (parallel)**: Demo 3 observability dashboard. Lower
priority for customer-side; build incrementally; user-side ROI
realized within first 2 weeks of incremental ship.

**Decision gates** (each demo independently):
- After Demo 2 launch (week 5): does HN/inbound funnel work? If
  yes -> double down. If no -> Demo 2 stays as discovery instrument
  only.
- After Demo 1 SDK + 10 customer calls (week 8): does buyer pain
  validate Lane D positioning? If yes -> productionize. If no ->
  pivot capability mix.
- After Demo 3 user-side dashboard 2-week shakedown: did user
  report new discoveries? If yes -> extend to auditor-view + Lane C
  pairing. If no -> dashboard stays user-private.

---

## Substrate-validation requests (filed via separate files)

See `product_request_to_strategy_lane_C_compliance_FULL_2026-05-22.md`
(filed next cycle): asks Strategy to flag Lane C compliance FULL
verdict the moment it lands, since Demo 2 + Demo 1's erase
positioning depend on it.

See `product_request_to_strategy_betS_K_ceiling_FULL_2026-05-22.md`
(filed next cycle): asks Strategy to flag Bet S K-ceiling N=65536
FULL verdict, since Demo 1 agent-scale memory positioning depends
on it.

---

## Revision history

- v0 2026-05-22 — initial cold-start. Top 3 from
  `product_options_ranked.md` v0. Reads cap_map v113 + meta cycle 60.
  Per session_7_product.md INITIAL TASKS.
