# Product options ranked — initial v0 (2026-05-22)

Owner: Session 7 (Product). Re-read every cycle per session_7_product.md
per-cycle protocol. Ranked by **(customer-value x likelihood-of-buy) /
user-effort**. Substrate state read against `substrate_capability_map.md`
v113 (after meta cycle 60 RS-phase certification + Lane D N-scaling
FULL + Lane D noise robust FULL).

**Lens**: `meta_strategic_direction_AI_memory_subsystem_2026-05-22.md` —
the four capability classes (1=verifiable erase, 2=editable memory,
3=provenance, 4=cognitive composition).

**Empirical anchors actually usable today** (`Tier-1` PROMOTED, multi-seed
or FULL where it matters):

- **Class 1 erase**: Bet 2 GDPR erase ✅ Tier-1; Lane C compliance
  smoke PERFECT (delete_leak=0, edit_acc=1.0, kept_acc=1.0,
  side_effect=0, ECE=0). Lane C compliance FULL still pending —
  flagged below where it matters.
- **Class 2 edit**: Bet A edit-then-query ✅ Tier-1 (M up to 16N at
  100-edit smoke; clean breakpoint at edit 8189). Bet B multi-task
  CL ✅ Tier-1 (5 FULL mechanisms).
- **Class 3 provenance**: `decompose_K_cliff` ✅ multi-seed; ACF
  resonator rescue past capacity cliff; pool retrieval ✅ Tier-1
  (Bet 1 ICL via pool).
- **Class 4 composition**: Lane D 4-primitive parallel composition
  ✅ FULL (S=0.983 / T=0.978 / U=1.0 / X=1.0); Lane D 3-stage e2e
  pipeline ✅ FULL (S->T->X = 1.0/1.0/1.0); Lane D noise robust ✅
  FULL (>99% composed_acc through 30% bit-flip); Lane D N-scaling
  ✅ FULL LINEAR c=0.073 (cycle 113 — overturns cycle 108 sublinear
  smoke).

**Empirical caveats**:
- Lane C compliance smoke is PERFECT; FULL still pending. Per the
  smoke-not-predictive precedent at 6 anchors (cycle 60), any demo
  anchored on Lane C compliance smoke is conditional. Bet S
  K-ceiling N=65536 FULL pending — affects agent-scale memory
  projections (class 2 + class 4 implication).
- Substrate is certified RS / paramagnet phase (cycle 60 v112) — no
  glassy attractor pathologies; predictable behavior. Substrate-product
  positive but supersedes prior Bet E RSB framing.

---

## Ranking table (8 candidates, ordered by composite score)

| Rank | Option | Buyer | Capability classes | Demo-readiness | User-effort | Likelihood-of-buy | Composite |
|---|---|---|---|---|---|---|---|
| 1 | **Lane D agent memory SDK + LangChain adapter** | AI agent platform engineer (Devin / Replit Agents / LangChain / Cursor team) | 2 + 3 + 4 (all 3 with multi-FULL anchors) | 🟢 ready (Lane D wedge is the most-anchored substrate axis) | 6-10 weeks | MEDIUM | **HIGHEST** |
| 2 | **Browser extension forensic-erase demo (substrate-as-service)** | Technical decision-maker / viral demo audience / Lane C buyer's eval lead | 1 + 3 | 🟡 demo-shell 2-3 weeks; substrate side ready | 2-4 weeks | INDIRECT (funnel to Lane C/D) | **HIGH** |
| 3 | **User-side observability tool (Hessian VDOS / P(h) + Mirage erase + decomposition GUI)** | User (substrate creator); secondary buyer = enterprise compliance auditor | all 4 + substrate-physics probes | 🟡 substrate-physics side smoke-ready (observability suite v1 smoke cycle 109; FULL pending); GUI 3-5 weeks | 3-5 weeks | N/A primary; HIGH user-side ROI | **HIGH (dual-purpose)** |
| 4 | **Open-standard publication — 5-probe Mirage erase protocol** | Industry (substrate as reference implementation) | 1 | 🟢 protocol spec writable today | 4-6 weeks | INDIRECT (long-tail inbound) | MEDIUM |
| 5 | **Lane C eDiscovery forensic-erase demo (Rule 26)** | Partner-track associate at AmLaw 100 doing eDiscovery, facing Rule 26 sanctions | 1 + 3 | 🟡 substrate + workflow integration | 8-12 weeks user-time + multi-month sales cycle | LOW (solo dev cant close AmLaw 100 procurement) | LOW for first MVP |
| 6 | **Lane C HIPAA right-to-deletion demo (healthcare)** | CTO at mid-size health system or AI-vendor selling to providers (Epic adjacents) | 1 + 3 | 🔬 substrate ready; HIPAA/BAA paperwork blocks | 12-16 weeks + 9-18mo sales cycle | LOW (BAA gating; solo dev unfit) | LOW for first MVP |
| 7 | **Lane C SOX financial-services retention demo** | AI/risk-tech team at BFSI vendor (Bloomberg / FIS / Fiserv) or investment-bank AI ops | 1 + 2 + 3 | 🔬 substrate ready; SOX evidence-chain integration | 12-16 weeks + multi-quarter sales | LOW for first MVP | LOW |
| 8 | **Lane A LLM-provider partnership pitch** | Memory team at Anthropic / OpenAI / Mistral | all 4 | 🔬 needs Lane C or Lane D reference customer first | 4-8 weeks pitch prep + 6-12mo BD | VERY LOW without prior reference customer | LOW until #1 or #5 lands |

---

## Per-option detail

### 1. Lane D agent memory SDK + LangChain adapter (RANK 1)

- **Buyer persona**: AI agent platform engineer at one of: Cognition
  (Devin), Replit Agents, LangChain ecosystem maintainer, Cursor team,
  early-stage agent startup (~Series A YC company building durable
  agents). Their current pain: persistent memory for long-running
  agents is either (a) vector DB with opaque retrieval, (b) Anthropic
  Memory API (locked to one model provider, no provenance), or (c)
  hand-rolled mess. Buying trigger: their agent fails a customer demo
  because it "remembered wrong" and they need provenance + correctable
  memory now.
- **Capability classes used**:
  - Class 4 cognitive composition (Lane D 4-primitive parallel FULL +
    3-stage sequential FULL + N-scaling LINEAR FULL + 30% noise FULL =
    4 independent FULL anchors)
  - Class 2 editable memory (Bet A edit-then-query ✅ Tier-1; scales
    M=16N)
  - Class 3 provenance (decomposition + pool retrieval = "this output
    came from these stored facts")
- **User-effort estimate** (realistic Marshall hours):
  - Python SDK (`hd_memory` package, async, REST-friendly): 2 weeks
  - LangChain `BaseMemory` adapter + minimal `BaseChatMemory`
    compatibility: 1 week
  - Substrate-as-service deployment (Docker + REST API around remote
    workstation): 1-2 weeks
  - Demo notebook: agent + memory roundtrip showing edit / provenance
    / replay: 1 week
  - Customer-conversation overhead (10-15 calls with target engineers
    to validate pain): 2-3 weeks parallel
  - **Total: 6-10 weeks**
- **Customer-value framing**: "Persistent agent memory where you can
  edit a fact in-place, query provenance for any answer, and prove a
  memory was forgotten — none of which Anthropic Memory API or vector
  DBs offer today. Substrate-level reason: bit-XOR / Hadamard binding
  commutes with edit + erase; pool retrieval gives mathematical
  decomposition not post-hoc interpretation."
- **Demo-readiness**: 🟢 — Lane D wedge is the most-anchored axis in
  the substrate. 4 independent FULL anchors. No 🔬-conditional gates.
- **Risk**:
  - Bet S K-ceiling N=65536 smoke KILL (cycle 60) — if FULL ratifies
    smoke KILL, agent-scale memory cap is K_crit ~200 not 2487; need
    to be honest about agent-scale (still useful for many agents but
    not for 100K-fact agents).
  - Agent-platform competition is fast-moving; SDK quality threshold
    is high. LangChain ecosystem fatigue is real.
  - Conversion: free SDK -> paid usage is not automatic. Need
    monetization plan (managed service, usage-based, or open-core).
- **Composite rank**: HIGHEST. Substrate is empirically ready;
  buyer is software-eng-flavor (faster eval than enterprise);
  value/effort ratio best of the 8.

### 2. Browser extension forensic-erase demo (substrate-as-service) (RANK 2)

- **Buyer persona**: Two audiences. (a) Technical decision-maker at a
  Lane C-adjacent shop who needs a 5-minute visceral demo to forward
  to their compliance officer / GC; (b) HN / Twitter viral audience
  who shares the demo and drives inbound. NOT a direct revenue play —
  this is a **funnel-top instrument** that feeds #1 (Lane D SDK eval)
  and #5-7 (Lane C enterprise).
- **Capability classes used**:
  - Class 1 verifiable erase (Bet 2 GDPR erase ✅ + Lane C compliance
    smoke PERFECT)
  - Class 3 provenance (decomposition shows what was stored before /
    after erase)
- **User-effort estimate**:
  - Substrate-as-service REST API around erase + decomposition: 1
    week (overlap with #1's substrate-as-service)
  - Minimal browser extension (Chrome Web Store) + web frontend with
    "store fact -> query -> erase -> verify all 5 Mirage probes" UX:
    1.5 weeks
  - Recording / demo asset production: 0.5 week
  - **Total: 2-4 weeks**
- **Customer-value framing**: "Watch a fact get algebraically erased
  and verified gone in 5 probes. Substrate-level reason: bit-XOR is
  commutative; the erase is mathematical inversion, not adversarial
  fine-tuning. LLM 'unlearning' has no such guarantee."
- **Demo-readiness**: 🟡 — substrate side ready; demo shell 2-3 weeks.
  Lane C compliance smoke is PERFECT but FULL pending. Either fine
  for funnel-top demo (smoke perfect = visceral demo works) OR
  conditional on FULL if we want to claim "production-ready erase."
  Recommend conditional framing.
- **Risk**:
  - Lane C compliance FULL could deviate from smoke (smoke-not-
    predictive precedent at 6 anchors). Demo claims should be smoke-
    qualified until FULL lands.
  - "Cool demo, no buyer" risk — needs paired CTA into Lane D SDK
    waitlist or Lane C consultation.
  - Browser extension review (Chrome Web Store) can add 1-2 weeks of
    bureaucratic overhead.
- **Composite rank**: HIGH. Cheap, visceral, dual-funnel. Justifies
  itself even with zero direct conversion if it generates inbound for
  #1.

### 3. User-side observability tool (Hessian VDOS / P(h) + Mirage erase + decomposition GUI) (RANK 3)

- **Buyer persona**: PRIMARY = the user (substrate creator), who
  needs an instrument-grade GUI to see substrate state, surface gaps,
  speed experiment design. SECONDARY = enterprise compliance auditor
  at a Lane C buyer who wants to inspect "what does the AI memory
  look like right now."
- **Capability classes used**:
  - All 4 classes (the GUI surfaces substrate-physics observables that
    map onto each class)
  - Plus substrate-physics probes (Hessian VDOS, P(h), C_ij, P(q)) —
    observability suite v1 smoke landed cycle 109
- **User-effort estimate**:
  - Read-only GUI over existing observability suite outputs: 2 weeks
  - Mirage 5-probe erase visualization (reuse demo from #2): 0.5 week
  - Decomposition K-cliff visualization: 1 week
  - Snapshot diff (state pre/post-edit, pre/post-erase): 0.5-1 week
  - **Total: 3-5 weeks**
- **Customer-value framing**:
  - **User-side**: see substrate state at a glance; surface
    invisible-gaps (e.g., decomposition near K-cliff; M_stored near
    capacity; Bet S K-ceiling proximity); speed up experiment
    triage; instrument the substrate as a substrate-physics product.
  - **Customer-side**: "compliance auditor view" — a buyer can
    inspect AI memory state the way a DBA inspects a database. No
    equivalent exists for transformer KV cache or vector DB.
- **Demo-readiness**: 🟡 — observability suite v1 SMOKE landed
  cycle 109; FULL still pending. Hessian VDOS not yet integrated.
  GUI itself is 3-5 weeks user work.
- **Risk**:
  - Observability suite v1 FULL deviates from smoke (smoke-not-
    predictive at 6 anchors). 4-family probe stack might show
    unexpected behavior at FULL.
  - Tool serves user primarily; treating it as buyer-facing requires
    polish + UX work beyond the user-side MVP.
- **Composite rank**: HIGH on dual-purpose grounds. Even if buyer-side
  conversion is zero, user-side ROI (faster discovery / better
  experiment design / surface substrate gaps before they bite) is
  load-bearing. This is the option where "what does the substrate
  let me see that I couldn't see before?" is the central thesis.

### 4. Open-standard publication — 5-probe Mirage erase protocol (RANK 4)

- **Buyer persona**: Industry as adopter. Direct beneficiaries:
  (a) regulators / standards bodies (NIST AI RMF, ISO/IEC 42001
  working groups, EU AI Act technical-standard committees);
  (b) AI vendors who need to demonstrate erase compliance; (c) buyers
  of AI who want a measurable spec.
- **Capability classes used**: Class 1 (the protocol IS class 1
  formalized).
- **User-effort estimate**:
  - Write protocol spec (Markdown + reference test vectors): 1 week
  - Reference implementation as Python library + CLI: 2 weeks
  - GitHub repo + documentation site + contribution guide: 1 week
  - Comms (HN post, NeurIPS-adjacent workshop submission, post to
    LessWrong / AI alignment): 1-2 weeks
  - **Total: 4-6 weeks**
- **Customer-value framing**: "Kubernetes became inevitable by
  framing the rules. SQL became inevitable by framing the rules.
  Substrate is the reference impl of the rules for verifiable AI
  memory erase. Substrate-level reason: bit-XOR / Hadamard commute
  with erase; protocol verifies behavior any candidate AI memory
  system can be tested against."
- **Demo-readiness**: 🟢 — protocol spec writable today; reference
  impl uses already-validated substrate.
- **Risk**:
  - Standards adoption is slow. Default outcome is "ignored."
  - Without flagship customer using the standard, hard to drive
    adoption.
  - High writing/documentation effort with deferred payoff.
- **Composite rank**: MEDIUM. Not first MVP. Reasonable to sequence
  AFTER #1 (Lane D SDK lands a reference customer using the protocol
  internally) — then publish the standard with paired case study.

### 5. Lane C eDiscovery forensic-erase demo (RANK 5)

- **Buyer persona**: Partner-track associate at AmLaw 100 firm
  handling eDiscovery for a securities case, whose firm just got hit
  with a Rule 26 sanctions motion for failure to produce documents
  the opposing side claims were stored in an AI assistant. Current
  pain: cant prove the AI assistant doesn't still "remember"
  privileged content. Buying trigger: court order to demonstrate
  forgetting.
- **Capability classes**: 1 + 3.
- **User-effort estimate**: 8-12 weeks user time + multi-month sales
  cycle. Substrate is the easy part (~2-3 weeks); legal workflow
  integration (Relativity / Everlaw / DISCO compatibility) is hard.
  Procurement at AmLaw 100 firms takes 3-9 months even with a
  champion.
- **Customer-value framing**: "Algebraic erase of privileged content
  with 5-probe forensic verification. Court-defensible. Substrate-
  level reason: Hadamard binding commutes with erase; LLM unlearning
  is adversarial fine-tuning that may not work."
- **Demo-readiness**: 🟡 — substrate ready; workflow integration is
  the lift.
- **Risk**:
  - Solo dev / unfunded substrate can't credibly close AmLaw 100
    procurement. Channel partner (a legal-tech AI vendor) is the
    realistic path. Without that channel, conversion = 0.
  - Lane C compliance FULL pending (smoke-not-predictive).
- **Composite rank**: LOW for **first** MVP; HIGH for **12-month
  flagship deployment** once Lane D SDK has revenue and a Lane D
  customer with a regulated-industry use case can be referenced.

### 6. Lane C HIPAA right-to-deletion demo (RANK 6)

- **Buyer persona**: CTO at mid-size hospital system / AI vendor
  selling AI scribes or clinical decision support (Hinge, Olive,
  Abridge, Nuance, athenahealth AI adjacents). Pain: HIPAA right-to-
  deletion + state-level (e.g., California CMIA) requires proving
  PHI removal; AI vendors currently say "we don't store PHI in the
  model" but can't prove the model didn't memorize. Trigger: OCR
  audit or class-action threat.
- **Capability classes**: 1 + 3.
- **User-effort estimate**: 12-16 weeks user time + 9-18 month sales
  cycle. BAA + HIPAA security rule compliance + SOC 2 Type II +
  HITRUST are gating; solo dev hits the BAA wall fast.
- **Customer-value framing**: "AI in a HIPAA workflow that proves
  PHI removal." Substrate-level reason same as #5.
- **Demo-readiness**: 🔬 — substrate ready but productionization
  blocks (BAA / SOC 2 / HITRUST) make standalone demo unconvincing.
- **Risk**: Same channel/procurement story as #5, plus HIPAA
  paperwork overhead.
- **Composite rank**: LOW for first MVP; possibly second-flagship
  after #5.

### 7. Lane C SOX financial-services retention demo (RANK 7)

- **Buyer persona**: AI/risk-tech team at BFSI vendor (Bloomberg /
  FIS / Fiserv) or AI/ML lead at investment bank's AI ops team.
  Pain: SOX 404 evidence chain + FINRA Rule 4511 retention; AI
  systems failing audit because retention/forgetting can't be
  evidenced. Trigger: SOX 404 audit finding or FINRA enforcement.
- **Capability classes**: 1 + 2 + 3.
- **User-effort estimate**: 12-16 weeks + multi-quarter sales.
- **Customer-value framing**: SOX 404-grade evidence chain for AI
  memory. Substrate-level reason same as #5/#6.
- **Demo-readiness**: 🔬 — same paperwork-overhead concern as #6.
- **Composite rank**: LOW for first MVP. Long-tail flagship.

### 8. Lane A LLM-provider partnership pitch (RANK 8)

- **Buyer persona**: Memory team at Anthropic / OpenAI / Mistral.
  Pain: their persistent memory products (Anthropic Memory API,
  OpenAI memory) leak context, can't be forensically erased, and
  enterprise buyers are asking for audit. Trigger: enterprise
  customer asks "can you prove deletion?"
- **Capability classes**: All 4.
- **User-effort estimate**: 4-8 weeks of pitch prep + working demo +
  6-12 month BD cycle. Substrate side trivial vs BD overhead.
- **Customer-value framing**: "Memory subsystem under your LLM API
  with database-grade audit properties." Substrate-level reason
  spans all 4 classes.
- **Demo-readiness**: 🔬 — without a Lane C or Lane D reference
  customer already shipping the substrate, the partnership pitch
  has no proof point.
- **Risk**: Partnership sales notoriously slow; vendor lock-in;
  buyer might absorb capability rather than partner. NIH effect at
  big-three labs is real.
- **Composite rank**: LOW for first MVP. Reasonable as 12-18 month
  goal AFTER #1 has revenue + reference customers.

---

## Top 2-3 by composite score (substantive next step)

**Tier A (build now)**:
1. Lane D agent memory SDK + LangChain adapter
2. Browser extension forensic-erase demo (substrate-as-service)
3. User-side observability tool (Hessian VDOS / P(h) + Mirage + decompose GUI)

These three share infrastructure (substrate-as-service REST API) and
build naturally in parallel. #1 is the conversion play; #2 is the
funnel-top instrument; #3 is the user-side discovery instrument that
doubles as enterprise audit view.

**Tier B (defer; sequence after Tier A traction)**:
4. Open-standard publication
5-7. Lane C eDiscovery / HIPAA / SOX (any one as flagship after #1
   has revenue)
8. Lane A LLM-provider pitch (after #5/#6/#7 flagship)

---

## Open conditions / substrate-validation gates

- **Bet S K-ceiling N=65536 FULL** (pending; cycle 60 smoke KILL).
  If FULL ratifies smoke KILL: Lane D agent memory positioning needs
  honest re-bound on agent-scale capacity (still useful for most
  agents but not for 100K-fact agents).
- **Lane C compliance FULL** (smoke PERFECT cycle 86; FULL pending).
  All Lane C-anchored claims (#2 + #5/6/7) are smoke-qualified
  until FULL lands.
- **Observability suite v1 FULL** (smoke cycle 109; FULL pending).
  Affects #3 user-side observability tool buyer-claims (user-side
  utility is unaffected; auditor-view positioning is conditional).

Filing two `product_request_to_<session>` items next cycle to push
these to top of substrate-validation queue. See decision log.

---

## What this v0 deliberately does NOT do

- TAM sizing (per feedback_value_creation_not_competition).
- "Killer" / "groundbreaking" without substrate-level reason in same
  sentence.
- Competitive marketing copy (Anthropic Memory API / OpenAI memory
  references are kept to honest capability-gap statements, not
  positioning sneers).
- Pretend Lane C enterprise sales are doable solo without a flagship
  channel. Lane C is correctly the strategic wedge but requires a
  preceding revenue + reference-customer flywheel from #1.

---

## Revision history

- v0 2026-05-22 — initial cold-start under PROT-001 (session 7
  bootstrap). Reads cap_map v113, meta cycle 60. Ranks 8 candidates
  per session_7_product.md INITIAL TASKS.
