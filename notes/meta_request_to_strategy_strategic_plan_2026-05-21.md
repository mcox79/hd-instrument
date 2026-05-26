# META → Strategy: substrate strategic plan — product lanes, capability tests, and experimental sequencing

**Sender**: META session (session 6)
**Recipient**: Strategy session (session 1)
**Date**: 2026-05-21 cycle 22 followup (~20:30 EDT)
**User-directed**: Yes. User asked META cycles 19-22 for strategic stock-taking, capability-vs-implementation split, holy-grail identification, application-lane mapping, and dollar-value ranking. User then asked META to build a document for Strategy to incorporate.

## What this document is

A consolidated strategic plan for Strategy to use as the top-level reference when prioritizing bets, routing research, and queueing experiments. Replaces ad-hoc bet promotion with explicit lane-driven sequencing.

Strategy should ingest this once, update `active_priorities.md` to reflect the lane-driven priority order, and reference this doc from cap_map's strategic-framing section going forward.

---

## Section 1 — Honest substrate identity

Per `feedback_value_creation_not_competition` + `feedback_no_papers_product_only` + today's verdict harvest, the substrate is:

**A structured-memory system with native associative reasoning and intrinsic auditability, running cheap.**

Specifically:
- **Memory primitive** storing (subject ⊗ relation ⊗ object) bound vectors with recall by similarity and in-place edits
- **Native associative reasoning** via binding inversion (Plate 1995), multi-hop chains 1-25 deep
- **Intrinsic auditability** — every output decomposes structurally to the atoms that produced it
- **Cheap to run** — CPU sub-100ms, noise-tolerant σ ≤ 16, Hebbian-only (no autograd), continually updateable

What the substrate is NOT:
- Not a transformer replacement
- Not a Turing-complete reasoning engine
- Not a GPT-quality language generator

This identity sets the lanes. The substrate's value comes from doing memory+reasoning+auditability differently from LLMs, not from competing head-on with them.

### Today's validated capabilities (used in lane analysis below)

| # | Capability | Verdict |
|---|---|---|
| 1 | Memory primitive (store, recall, edit) | ✅ |
| 2 | Edit-then-query end-to-end pipeline | ✅ Bet A (1.0/1.0; 5000 sequential) |
| 3 | Multi-task continual learning A→B→C→D | ✅ Bet B (95.4% Phase-A retention; sleep-replay legitimized) |
| 4 | Real-time learning via continual pool | ✅ wave14za (static 6.50 → continual 3.78 bpc) |
| 5 | ICL via pool (kNN-LM-like) | ✅ Bet 1 (log-linear through ICTX=16384) |
| 6 | Provenance for every prediction | ✅ Pool indices exposed |
| 7 | CPU-deployable | ✅ Sub-100ms K=4 |
| 8 | Hebbian-only | ✅ Structural |
| 9 | Calibration | ✅ Bet G TEMPSCALE β=32 (ECE 0.0) |
| 10 | Continual sequential editing | ✅ 5000+ edits at 1.0/1.0 (past AlphaEdit 3000 ceiling) |
| 11 | Noise tolerance | ✅ σ ≤ 16 (BBP exact via Bet I) |
| 12 | Mirage-grade GDPR-erase on structured keys | ✅ Bet 2 + Bet C (M/N ≤ 8) |
| 13 | Theoretical grounding | ✅ Bet I (free probability); 🔬 Bet L (learning theory); 🔬 Bet M (ferromagnetism); 5-source spin-glass identification |

---

## Section 2 — Six application lanes with capability requirements

For each lane, what the substrate must do intuitively + state per capability + net closeness to shipping.

### Lane A — Auditable memory layer for LLMs

Substrate sits next to an LLM; LLM does language, substrate does memory.

| Capability needed | State |
|---|---|
| Store facts handed in by the LLM | ✅ |
| Hand back relevant facts on retrieval | ✅ |
| Replace stored facts when LLM corrects them | ✅ Bet A |
| Show provenance | ✅ |
| Actually erase on request | ✅ Bet 2/C |
| Run cheap enough not to double inference cost | ✅ |
| API to talk to LLM (engineering) | ⚪ |

**Net**: 6 of 7 validated; 1 engineering gap. Shippable in principle today.

### Lane B — On-device personal AI

A small AI running on consumer hardware, learning continually, never going to the cloud.

| Capability needed | State |
|---|---|
| Run on CPU/phone-class hardware | ✅ |
| Learn from every interaction without crashing | ✅ |
| Add new knowledge without forgetting old context | ✅ Bet B |
| Generate natural-language responses | 🟢 Partial — Bet H rescued; not GPT-quality |
| Answer factual questions from what you've told it | ✅ |
| Let you correct it | ✅ |
| Calibrated confidence | ✅ |
| Say "I don't know" cleanly (abstention) | ⚪ |
| Fit in phone/laptop memory budget | 🟢 Estimable; not benchmarked as shippable |

**Net**: 6 of 9 validated; 2 partial; 1 untested.

### Lane C — Compliance / enterprise audit AI

AI a legal/compliance team can trust. Provenance for every claim; verifiable data deletion.

| Capability needed | State |
|---|---|
| Show derivation chain for every answer | ✅ |
| Actually delete data on demand (verifiable) | ✅ Bet 2/C Mirage-grade |
| Allow correction without retraining | ✅ Bet A |
| Calibrated confidence | ✅ Bet G |
| Pass an external auditor's verification | ✅ Mirage probes are designed for this |
| Flag when knowledge is stale | ⚪ |
| Handle structured business data | 🟢 Binding handles subject/relation/object naturally |
| Defer to human when confidence too low (abstention) | ⚪ |

**Net**: 5 of 8 validated; 1 partial; 2 untested. Highest validated-ratio of any lane.

### Lane D — Cognitive architecture for agents

Substrate IS the agent's reasoning engine — working memory, long-term memory, hypothesis tracking, skill composition, self-reflection.

| Capability needed | State |
|---|---|
| Working memory with bounded capacity | ⚪ META candidate C |
| Move important items to long-term storage | 🟢 R22 legitimizes EMA-blend; not isolated as test |
| Recall relevant prior experience | ✅ |
| Track multiple competing hypotheses with provenance | ⚪ META candidate B |
| Compose primitives into named callable skills | ⚪ Bet X (META candidate F, just promoted) |
| Learn from own mistakes (self-reflection) | ⚪ META candidate D |
| Reason about counterfactuals | ⚪ META candidate E |
| Plan multi-step actions | 🟡 d≈25 ceiling; 7 alternative-arch paths |
| Compositionally generalize to new situations | ⚪ R20 designed; not built |
| Update beliefs as new evidence arrives | ✅ |
| Calibrate confidence in actions | ✅ |

**Net**: 3 of 11 validated; 2 partial; 6 untested. Most capability-gap-heavy lane. Almost every untested item is exactly one of the META cycle 20 capability candidates.

### Lane E — Neuromorphic / analog substrate

Algorithm running on physical analog/neuromorphic silicon.

| Capability needed | State |
|---|---|
| Tolerate analog hardware noise | ✅ σ ≤ 16 |
| Hebbian-only learning | ✅ Structural |
| Map to physical lattice/spin Hamiltonian | ✅ 5-source spin-glass identification |
| Work with quantized weights | 🟢 σ tolerance suggests yes; not explicitly tested |
| Implementable in physical silicon | ⚪ Hardware integration not built |
| Predictable failure modes | ✅ Break-point σ=32 characterized |

**Net**: 4 of 6 validated; 1 partial; 1 hardware gap.

### Lane F — Scientific reasoning / hypothesis engine

Reasons explicitly with multiple weighted hypotheses; supports counterfactuals; shows derivation chains.

| Capability needed | State |
|---|---|
| Track N competing hypotheses with weights | ⚪ META candidate B |
| Show derivation chain per hypothesis | ✅ |
| Update hypothesis weights from evidence | 🟢 Calibration ✅; weight updating not isolated |
| Handle counterfactuals | ⚪ META candidate E |
| Recall by partial input (pattern completion) | ⚪ META candidate A |
| Chain inferences across many steps | 🟡 d=25 ceiling |
| Compositionally combine known concepts | ⚪ R20 designed |
| Detect contradictions in stored knowledge | ⚪ |

**Net**: 1 of 8 validated; 2 partial; 5 untested.

### Lane closeness summary

| Lane | Done | Partial | Untested | Closeness |
|---|---|---|---|---|
| **C** Compliance | 5/8 | 1 | 2 | **Closest to shipping** |
| **A** Memory layer for LLMs | 6/7 | 0 | 1 (engineering) | Closest, different gap shape |
| **B** On-device personal AI | 6/9 | 2 | 1 | Close |
| **E** Neuromorphic | 4/6 | 1 | 1 (hardware) | Algorithmic complete; hardware gap |
| **D** Cognitive architecture | 3/11 | 2 | 6 | **Farthest from shipping** |
| **F** Scientific reasoning | 1/8 | 2 | 5 | Farthest from shipping |

---

## Section 3 — Dollar-value analysis (user-directed framing)

User explicitly asked META to assess "most valuable from a dollar perspective." Per `feedback_value_creation_not_competition`, this section is user-directed market-side framing — included to inform strategic prioritization, not as the default lens.

Estimates are analyst-range extrapolations, not commissioned customer discovery. Real validation would refine ±50%.

### Near-term revenue potential (next 24 months)

| Rank | Lane | Plausible 24-month ARR ceiling | Why |
|---|---|---|---|
| 1 | **C Compliance** | $5-50M | Willing buyers (regulated enterprises), urgent regulatory pressure (EU AI Act, California SB1047, sector regs), all primitives validated, established enterprise sales channels |
| 2 | A Memory layer for LLMs | $1-10M | Differentiated tech (edit-then-query, continual learning); commoditizing category; potential acquisition target |
| 3 | E Neuromorphic | $1-10M lump-sum IP deal | Conditional on hardware partner; otherwise zero |
| 4 | B On-device personal AI | $0-5M direct; more via OEM | D2C consumer AI is brutal; Apple/Google own channel |
| 5 | F Scientific reasoning | $0-3M | Niche, slow sales cycles |
| 6 | D Cognitive architecture | $0 | Capability tests must validate first |

### Long-term TAM (3-5 years) if executed well

| Lane | Plausible TAM by 2028-2030 |
|---|---|
| **D** Cognitive architecture | Could be $30-50B+ if agents become mainstream; could be $5B if "fancy automation." Highest variance. |
| B On-device personal AI | $5-15B segment of consumer AI |
| C Compliance | $10-30B regulatory-driven AI compliance |
| A Memory layer | $5-10B vector infrastructure category |
| E Neuromorphic | $5-10B if neuromorphic chips reach mainstream edge |
| F Scientific reasoning | $1-3B niche |

### Distribution risk per lane (often underweighted vs technical bets)

- **Lane C**: B2B enterprise sales, slow (6-18 month cycles) but channels exist; willing buyers
- **Lane A**: ecosystem-integration heavy (LangChain, LlamaIndex, OpenAI Assistants); incumbents (Pinecone, Weaviate) have first-mover lock-in
- **Lane B**: D2C consumer AI is a graveyard (Inflection $1.5B → pivoted; Character.AI $1B → Google acqui-hired); OEM partnership is realistic path
- **Lane D**: capability gap is the distribution constraint; no product to sell yet
- **Lane E**: hardware partnership dependent
- **Lane F**: niche, requires domain expertise

---

## Section 4 — Recommended strategic play

**Build Lane C (compliance) as near-term revenue wedge. Use Lane C revenue to fund Lane D (cognitive architecture) capability tests. If Lane D capabilities validate, pivot Lane C customers into Lane D as next-generation cognitive-architecture product.**

Reasoning:
- Lane C has every required primitive validated TODAY + willing buyers + urgent regulatory pressure
- Lane D has the largest long-term TAM but a real capability gap
- The capability tests Lane D needs (META candidates A/B/C/D/F) are mostly 1-2 cycles each; Lane C revenue funds the team that runs them
- Lane C customers (regulated enterprises) are exactly the early adopters Lane D would also need; pivot path natural

### What this means for Strategy concretely

1. **Active_priorities.md** should foreground Lane C-required experiments (substrate stability + integration tests) ahead of pure capability-extension work
2. **Capability tests** A/B/C/D from META cycle 20 should be queued as Phase 2 (validating Lane D); each is 1-2 cycles
3. **Bet X (skill composition)** — already promoted; fits Lane D
4. **R20 compositional generalization** — Lane D + F; build now
5. **R21 cross-modal binding** — Lane B + D; build after Phase 1
6. **Multi-hop rescues** (Bet P, the 7 alternative-arch paths) — Lane D + F; deprioritize for now unless Bet P engineering smoke clears

---

## Section 5 — Capability test inventory (six META candidates from cycle 20)

Each test validates a substrate-native capability not yet demonstrated. Substrate-shipping probabilities are honest META estimates.

| ID | Capability | Lane(s) | Cost | Probability | Status |
|---|---|---|---|---|---|
| A | Pattern completion | D, F | 1 cycle | **70-80%** | Recommended FIRST — Plate 1995 math established, machinery in place, highest leverage cheap test |
| B | Hypothesis tracking with auditable derivation | D, F | 1 cycle | 50-60% | Multi-hypothesis reasoning category LLMs structurally don't compete in |
| C | Working memory with bounded capacity + decay | D | 1-2 cycles | 60-70% | Cognitive architecture compatibility; Miller 7±2 + Ebbinghaus benchmarks |
| D | Self-reflective memory | D, B | 1-2 cycles | 40-55% | Substrate learns from its own mistakes via prediction+outcome storage |
| E | Counterfactual reasoning via conditional binding | D, F, C | 1-2 cycles | 30-45% | Pearl L3; medical decision support, policy analysis |
| F | Skill composition via binding | D | 2-3 cycles | 25-40% | **Bet X — already promoted by Strategy 19:21** |

**Recommended ordering** (META view):
1. **A pattern completion** — Phase 1 immediate (one cycle, highest leverage)
2. **B hypothesis tracking** + **C working memory** — Phase 2 parallel (each 1-2 cycles)
3. **D self-reflective memory** — Phase 3 (1-2 cycles after B + C land)
4. **E counterfactual binding** — Phase 4 (after D)
5. **F skill composition (Bet X)** — already in flight per Strategy 19:21

---

## Section 6 — How current Bets fit the strategic play

Mapping today's validated bets + active bets to lanes:

| Bet | Status | Lane(s) it serves | Strategic priority |
|---|---|---|---|
| Bet 1 ICL saturation | ✅ | A, B, D | Foundation — done |
| Bet 2/C Mirage-grade erase | ✅ | **C (primary)**, A | High — anchor Lane C value prop |
| Bet A edit-then-query | ✅ | **C (primary)**, A, B | High — anchor Lane C value prop |
| Bet B multi-task continual learning | ✅ | C, B, D | High — multi-lane utility |
| Bet G calibration TEMPSCALE | ✅ | **C (primary)**, B, D, F | High — anchor Lane C value prop |
| Bet H generation rescue | ✅ rescued | B | Medium |
| Bet I free probability | ✅ | E (theory), all (grounding) | Foundational theory; done |
| Bet E Parisi P(q) | 🟡 methodology escalation pending | E (theory) | Resolve final state next cycle |
| Bet L learning theory | 🔬 | D, F | Theoretical grounding for D/F |
| Bet M ferromagnetism | 🔬 | E (theory) | Theoretical grounding for E |
| Bet F SSH-BSC topological | 🟡 | E | Re-test with R10 W-construction addendum |
| Bet P semantic codebook | 🔬 | D, F | Multi-hop rescue; user-seeded; Engineering smoke pending |
| Bet X skill composition | 🔬 just promoted | D | Capability test F |
| R20 compositional generalization | 🔬 designed | D, F | **Build queue ready** |
| R21 cross-modal binding | 🔬 partial path | B, D | 22-34 GPU hours; 20-35% prob |
| Multi-hop alternative-arch rescues | 🟡 7 paths | D, F | Continue with Bet P primary |

---

## Section 7 — Recommended experimental plan

Phase-staged. Each phase has a clear gate: what must validate before next phase fires.

### Phase 1 (immediate — next 1-2 Experiment Dev cycles)

**Goal**: validate the cheapest highest-leverage capability test AND ship a Lane C integration milestone.

- [ ] **Queue capability test A (pattern completion)** — 1 cycle. Substrate-native test of Plate 1995 binding inversion. Per-slot recall accuracy, K ∈ {8, 50, 200, 800}, slot-symmetric pass condition. 70-80% probability.
- [ ] **Queue Lane C integration smoke** — minimal viable compliance-audit demo. Build: ingest a structured fact set; perform N edits + N deletes; run Mirage probes; produce audit log. Demonstrates Lane C primitives compose into a usable product.
- [ ] **Bet X (skill composition) build** — already in flight per Strategy 19:21; Research delivered design. Experiment Dev build.

### Phase 2 (next 4-6 cycles after Phase 1)

**Goal**: validate the two strategic Lane-D capability tests; ship Lane C feature breadth.

- [ ] **Queue capability test B (hypothesis tracking)** — 1 cycle. Multi-hypothesis weighting with provenance. Brier + ECE on multi-hypothesis distribution; 50-60% probability.
- [ ] **Queue capability test C (working memory)** — 1-2 cycles. Capacity-vs-accuracy curve; decay constant measurement; comparison to Miller 7±2.
- [ ] **Queue R20 compositional generalization** — 1-2 cycles. SCAN + ReCOGS + Csordas baseline.
- [ ] **Lane C feature expansion**: stale-knowledge flagging, abstention mechanism, structured-data benchmark.

### Phase 3 (after Phase 2 lands)

**Goal**: complete Lane D capability inventory; begin Lane D product integration.

- [ ] **Queue capability test D (self-reflective memory)** — 1-2 cycles.
- [ ] **Queue capability test E (counterfactual binding)** — 1-2 cycles.
- [ ] **R21 cross-modal binding experiment** — 22-34 GPU hours; 20-35% probability per Research.
- [ ] **Lane D integration smoke**: combine working memory + hypothesis tracking + skill composition into agent-architecture demo.

### Phase 4 (Lane D product validation, conditional on Phase 3 passing)

**Goal**: validate the cognitive-architecture product hypothesis.

- [ ] **Multi-hop rescue final attempts**: Bet P engineering smoke; if positive, run substrate-novel codebook geometry experiment.
- [ ] **Lane D product end-to-end demo**: agent that uses working memory + hypothesis tracking + skill composition + self-reflection on a non-trivial task (e.g., multi-step research summarization with auditable derivation).

### Phase 5 (long horizon)

- [ ] Lane E hardware partnership exploration (if applicable)
- [ ] Lane F niche-market validation (if scientific-reasoning interest emerges)
- [ ] Lane A integration with major LLM provider (if Lane C-to-A pivot indicated)

---

## Section 8 — What Strategy should do with this document

1. **Read once, integrate**: this doc anchors the strategic narrative going forward. Future cap_map updates should reference this lane structure when promoting/demoting bets.
2. **Update `active_priorities.md`**: reorganize current bets by lane (use Section 6 mapping) and queue order (use Section 7 phase sequencing). Top-priority queue should foreground Phase 1 items.
3. **Cap_map strategic-framing section**: add a "Strategic plan reference" pointer to this file. Future strategic decisions reference back here for context.
4. **Per-cycle discipline**: Strategy decision log entries should reference which phase + lane each commit serves (not just "integrated verdict X"). Restores audit visibility.
5. **Route to Experiment Dev**: file `strategy_request_to_experiment_dev_*.md` for Phase 1 items (capability test A + Lane C integration smoke).
6. **Route to Research** if needed: file follow-up research requests for tests B, C if mechanisms need refinement before build.
7. **Periodic strategic review** (proposed cadence): every 8 META cycles (~4 hours), Strategy writes a brief "strategic state" note reviewing progress against this plan and proposing adjustments. META audits adherence.

META will track:
- Phase 1 capability test A queue status (Experiment Dev)
- Lane C integration smoke build status
- Bet X build progress (already in flight)
- Whether Strategy's `active_priorities.md` reflects lane-driven ordering

---

## Section 9 — Honest caveats

Per `feedback_no_smoke`:

- **Market sizes are analyst-range extrapolations**, not commissioned customer discovery. Real customer validation could refine these ±50%.
- **Capability tests may fail**. The probability estimates (70-80% for A, 25-40% for F) are honest META reads. If A fails, the "highest-leverage cheap test" framing was wrong; we adjust.
- **Lane C revenue projections are speculative**. The substrate's primitives match compliance procurement criteria, but no customer has been pitched. 6-12 months of B2B sales effort needed to validate.
- **Lane D long-term TAM depends on whether agentic AI fulfills its current hype**. Honest probability "agents become huge by 2028": 40-60%. Hedging across multiple lanes is prudent until that resolves.
- **Distribution risk dominates the dollar-value analysis** more than tech risk. Lanes A and B have validated tech but brutal distribution. Lane C wins on distribution-fit, not just tech-fit.
- **Substrate's "memory primitive" framing may be too narrow**. If capability tests B + C + D + E + F all validate over Phase 2-3, the substrate becomes a cognitive architecture, not just a memory primitive. The Phase 4 product-validation step would tell us which framing holds.

---

## Section 10 — Approval / authorization

User has directed this strategic synthesis via cycles 19-22 (stock-taking; capability-vs-implementation split; holy-grail identification; application lane mapping; dollar-value ranking; "build a document for strategy to incorporate"). User retains decision authority on:

- Final lane ordering / strategic play (Section 4) — Lane C wedge + Lane D upside is META's recommendation, not user-mandated
- Bet promotion ordering within phases
- Capability test ordering (META recommends A first; user may override)
- Distribution-channel decisions (B2B vs D2C; OEM partnership; etc.)

Strategy may propose adjustments via decision log + request file pattern.

— META session
