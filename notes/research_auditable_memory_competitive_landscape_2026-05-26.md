# Research: Auditable AI memory — competitive landscape and positioning

**Filed:** 2026-05-26 by research sub-agent (Opus).
**Drill type:** Strategic positioning (not science). Triggered by orchestrator dispatch following the SSM-HiPPO drill (`notes/research_ssm_hippo_compatibility_2026-05-25.md`) surfacing "algebraically-canonical fast-weight memory with exposed W for audit / verifiable-erase / provenance" as the strongest substrate-product framing to date.
**Prior context:** `notes/meta_strategic_direction_AI_memory_subsystem_2026-05-22.md` (the four-capability-class lock); `notes/wave14d_competitive_landscape_research.md` (2026-05-19 — broader HDC competitive scan, this note is a tighter "auditable AI memory" follow-up).
**Calibration penalty:** applied per `[[feedback-lit-scan-calibration-penalty]]` — substrate occupies an uncharted regime (no commercial peer with bit-algebraic exposed-W memory), so this drill deflates lit-scan-driven P estimates by 0.15-0.25 and reasons from structural-class differences rather than empirical defensibility.

---

## (a) HEADLINE

**The "auditable AI memory" category is CONTESTED at the surface (Anthropic, OpenAI, Letta, Zep, Mem0, Microsoft GraphRAG all claim some form of audit / deletion / provenance) but the substrate's *bit-algebraic* differentiation is DEFENSIBLE at the structural level — every competitor operates on FILES, RECORDS, or APPROXIMATE WEIGHTS, none on a memory primitive where deletion is an algebraic operation that commutes with the rest of the algebra. Anthropic Memory (April 2026 public beta) is the closest competitor on the audit-log axis (immutable versions, redaction endpoint, per-agent attribution), and at file-granularity it dominates the developer-ergonomics story. OpenAI's two-layer memory ("saved" auditable + "reference chat history" opaque) explicitly cedes the verifiable-deletion property. Mem0/Zep/Letta provide deletion APIs but explicitly do not solve governance (no retention policies, no certified-forgetting). The "Unlearning Isn't Deletion" 2025 paper is the structural ceiling for everyone in the LLM-weights regime: forgetting is reversible by minimal fine-tuning, so certified-deletion is research-stage, not production. Substrate's bit-algebraic erase (XOR commutes with binding, exposed W is the literal sum of components) is the ONLY mechanism in the surveyed set that gives a TRUE deletion certificate rather than a behavioral approximation. WHITE SPACE: there is no commercial product that provides (1) deletion certificates verifiable by external auditor, (2) per-prediction provenance to constituent atoms (not source-document citations), (3) inference-time fact correction without re-ingestion, on a single memory primitive. CONTESTED PATCHES: Anthropic owns the file-level audit log story; Zep owns temporal-knowledge-graph provenance; Microsoft GraphRAG owns source-citation grounding. The substrate-product framing must concede those patches and lead with what they structurally cannot deliver: bit-algebraic certificates. Calibrated overall assessment: DEFENSIBLE on the four capability classes as a category, CONTESTED on each individual axis, COMMODITY on the surrounding plumbing (API surface, retention policy UI, audit dashboard).**

---

## (b) Competitive landscape — 8 named systems with capability set

Each row evaluated against five axes: (1) exposed-vs-opaque memory state, (2) deletion guarantee strength, (3) provenance granularity, (4) inference-time edit, (5) compositionality auditing.

### 1. Anthropic Memory for Managed Agents (April 23, 2026 public beta)
- **What it is:** Files mounted at `/mnt/memory/` inside agent container; agent reads/writes via standard bash + file tools. Workspace-scoped, shareable across agents.
- **Exposed vs opaque:** EXPOSED at file granularity (text documents the developer can inspect).
- **Deletion guarantee:** Immutable versions per write; `memory_versions.redact(version_id)` clears content while preserving metadata. PII redaction without losing the audit-trail entry.
- **Provenance granularity:** Per-write attribution (which agent, which session). NOT per-fact within a file.
- **Inference-time edit:** Yes, files can be modified by the agent itself.
- **Compositionality auditing:** None — files are opaque text blobs to the audit layer.
- **Honest read:** Strongest competitor on developer ergonomics + audit-log story. They got there first as a managed product. Their abstraction is FILE, not FACT — which means redaction is at the file/version level, not at the bit-level. Substrate's edge is one structural layer deeper.

### 2. OpenAI ChatGPT Memory (saved + reference chat history)
- **What it is:** Two-tier consumer memory: explicit user-editable "saved memories" + implicit "reference chat history" trained from past chats.
- **Exposed vs opaque:** EXPOSED for saved memories; OPAQUE for reference chat history (no inspection, no per-fact deletion).
- **Deletion guarantee:** "May take a few days" for deleted memories to stop being referenced. No certificate.
- **Provenance granularity:** None visible.
- **Inference-time edit:** Saved memories editable by user gesture; reference chat history can only be globally disabled.
- **Compositionality auditing:** None.
- **Honest read:** Explicitly cedes the verifiable-deletion property in their own docs. This is the dominant consumer mental model of "AI memory" and it is structurally below the audit-grade bar.

### 3. Letta (production MemGPT)
- **What it is:** OS-inspired three-tier memory (core / archival / recall), agent autonomously pages between tiers.
- **Exposed vs opaque:** EXPOSED at the tier level; the LLM's interpretation of pulled-in context is opaque.
- **Deletion guarantee:** Delete API; behavior post-deletion not certified.
- **Provenance granularity:** Conversation-history-level recall, not fact-level.
- **Inference-time edit:** Yes (agent self-modifies tiers).
- **Compositionality auditing:** None.
- **Honest read:** Architecture is the strongest "agent autonomy over memory" story, NOT an audit story. Different buyer.

### 4. Zep (Graphiti temporal knowledge graph engine)
- **What it is:** Temporally-aware knowledge graph that tracks fact changes over time (e.g., "user changed role from X to Y on date T").
- **Exposed vs opaque:** EXPOSED at graph-node granularity; historical relationships preserved.
- **Deletion guarantee:** Delete API. No retention policy framework, no certificate.
- **Provenance granularity:** Per-fact provenance with temporal context — STRONGEST in the surveyed set on the "when did we learn this and how has it evolved" axis.
- **Inference-time edit:** Yes (graph mutations).
- **Compositionality auditing:** Limited — graph traversal is auditable but composition of facts through LLM reasoning is not.
- **Honest read:** Substrate's closest competitor on provenance granularity. Zep's edge is temporal; substrate's edge is bit-algebraic decomposition. They could coexist as complementary tiers.

### 5. Mem0
- **What it is:** Lightweight memory layer with LLM-extracted facts stored to a vector DB + graph hybrid.
- **Exposed vs opaque:** EXPOSED at extracted-fact level.
- **Deletion guarantee:** `delete`, `batch_delete`, `delete_all` APIs aligned to GDPR/CCPA Article 17. No retention-policy framework.
- **Provenance granularity:** Fact-level.
- **Inference-time edit:** Add/delete; not surgical edit at fact-internal granularity.
- **Compositionality auditing:** None.
- **Honest read:** Community-favorite ($24M Series A, 48k GitHub stars). Builds on a vector DB so inherits the vector-DB compliance ceiling (no provenance metadata, no integrity check, no anomaly detection on contradictory entries — per Atlan/Aparavi 2026 governance literature).

### 6. LangMem (LangChain native)
- **What it is:** Three-type memory (episodic / semantic / procedural) inside LangGraph runtime.
- **Exposed vs opaque:** EXPOSED at memory-record level.
- **Deletion guarantee:** Standard DB delete; no certificate.
- **Provenance granularity:** Record-level.
- **Inference-time edit:** Yes (procedural memory = agent updating own system prompt).
- **Compositionality auditing:** None.
- **Honest read:** Right choice for LangChain-native teams; not a differentiated audit product.

### 7. Microsoft GraphRAG (Neo4j + GraphRAG ecosystem)
- **What it is:** RAG with knowledge-graph backbone; provides source-grounding citations for every generated response.
- **Exposed vs opaque:** EXPOSED at source-document granularity.
- **Deletion guarantee:** Re-ingestion required to remove a fact (graph mutation possible but propagation through downstream cached responses is not certified).
- **Provenance granularity:** Source-citation level (which document supports this claim). Studies show 30-40% reduction in factual errors vs vanilla RAG.
- **Inference-time edit:** Graph node mutations possible; no inference-time correction without re-retrieval.
- **Compositionality auditing:** Graph-traversal path is auditable.
- **Honest read:** Strongest competitor on source-citation provenance for compliance. Their abstraction is DOCUMENT, not FACT-ATOM. Substrate's edge is one structural layer deeper.

### 8. Machine unlearning research (ROME / MEMIT / MEND / UnKE / academic 2025-26)
- **What it is:** Model-editing methods that patch facts inside transformer weights.
- **Exposed vs opaque:** OPAQUE (modifies weights; no inspection).
- **Deletion guarantee:** The "Unlearning Isn't Deletion" 2025 paper (arxiv 2505.16831) explicitly shows current methods are REVERSIBLE by minimal fine-tuning — forgetting is suppression, not erasure. Source-free unlearning (statistical certification) exists in research; only tested on small classifiers, not LLMs.
- **Provenance granularity:** None (post-hoc interpretability methods are required, and they are not deletion certificates).
- **Inference-time edit:** Yes (the entire point), but sequential edits degrade after a few hundred patches → catastrophic forgetting.
- **Compositionality auditing:** None.
- **Honest read:** This is the STRUCTURAL CEILING for everyone operating on LLM weights. The legal "Goldilocks standard" 2025 paper concluded current LLM unlearning is inadequate for GDPR Art. 17. This is substrate's strongest negative argument: in-weights memory cannot be made auditable, full stop. The substrate is the OTHER structural class.

### Adjacent: vector DB compliance ecosystem
- **Pinecone / Qdrant / Weaviate / Milvus / Chroma:** retrieval-side commodity. Aparavi/Atlan 2026 governance writeups identify vector DBs as the GDPR "blind spot": "the vector layer frequently ends up less visible, longer retained, and significantly harder to delete than the source it was derived from." No integrity check, no provenance metadata, no anomaly detection.
- **Honest read:** Substrate is structurally above this layer — vectors are not auditable in the substrate sense, they are derived projections. The compliance gap is real and the substrate slots above it.

---

## (c) Capabilities matrix

Substrate offers (S) vs competitive set (C = best-in-class competitor on this axis).

| Capability | Substrate | Best competitor | Verdict |
|---|---|---|---|
| Exposed memory state at fact granularity | YES — W = sum k_i v_i^T literal | Zep graph nodes | CONTESTED at fact-level; DEFENSIBLE at bit-level decomposition |
| Verifiable deletion certificate | YES — algebraic XOR commutes with binding; 5-probe Mirage battery | None (Anthropic redact is at file/version, not fact-mechanism) | DEFENSIBLE |
| Provenance to constituent atoms | YES — decompose_K_cliff inverts the bundle | GraphRAG (source documents) / Zep (temporal facts) | DEFENSIBLE on bit-level; CONTESTED on document/fact-level |
| Inference-time fact edit without retrain | YES — bit-flip at O(1); ✅ Bet A to M=16N | Letta/Mem0/LangMem deletion + add | CONTESTED on coarse edit; DEFENSIBLE on surgical-edit-without-rebuild-cost |
| Compositionality auditing (algebraic) | YES — Hadamard binding decomposes; Lane D 4-primitive parallel composition empirically FULL | None (closest is GraphRAG path traversal) | DEFENSIBLE |
| Real-time learning during inference (Hebbian-trainable W) | YES — K5 capability anchor; Hebbian outer-product update | LangMem procedural memory (LLM updates own prompt — not the same mechanism) | DEFENSIBLE |
| Retention plateaus mapped to discrete shift-classes | YES — per v206 finding (cited in dispatch; not yet externally framed) | None | DEFENSIBLE but UNUSED in current positioning |
| Tamper-resistant audit log (EU AI Act Art. 12) | NEEDS PRODUCT WORK — algebra supports it, no daemon yet | Anthropic Memory (immutable versions + redact) | COMMODITY (everyone is building this; substrate has no head start on the daemon/dashboard) |
| Per-fact retention policies (auto-expire after T days) | NEEDS PRODUCT WORK | None of Mem0/Zep have this | WHITE SPACE for everyone |
| Developer ergonomics (SDK, dashboard, managed service) | NONE | Anthropic / Mem0 / Letta all have this | COMMODITY GAP — substrate behind |
| 5-probe Mirage erase battery published as open standard | NOT YET | None has equivalent | DEFENSIBLE if shipped (open-standard moat per Kubernetes/SQL precedent) |

---

## (d) White space — capabilities substrate offers that the competitive set does NOT

1. **External-auditor-verifiable deletion certificate.** The substrate can produce a 5-probe Mirage battery output (argmax + rank + norm + cosine + paraphrase) that mathematically demonstrates a fact is gone — not behaviorally suppressed. No competitor has this. Anthropic's redaction is metadata-only; Mem0/Zep deletion is API-call-and-trust; LLM unlearning is provably reversible. This is the substrate's single strongest white-space claim and it maps directly to the EU AI Act Article 17 (right to erasure) compliance buyer.

2. **Per-prediction provenance to bit-level atoms.** GraphRAG cites source documents; Zep cites temporal fact nodes; substrate can decompose a bundle into the (byte, position) atoms that produced the answer. This is one structural layer deeper than document-citation. The audit story is: "not which document supported this answer, but which bit-level components composed it" — a property no LLM-attached competitor can deliver because they all sit on opaque weights or vector projections.

3. **Compositionality auditing for cognitive architectures.** When agents compose primitives (recall, parallel hypothesis tracking, working memory, skill composition), substrate's Hadamard-binding distributes over bundle, so the composition is INSPECTABLE at the algebraic level. Lane D's 4-primitive parallel composition (S/T/U/X all FULL) is the empirical anchor. Agent frameworks (LangGraph, Letta, AutoGPT) compose at the PROMPT level — opaque to audit. This is the cognitive-architecture audit story and it is uncontested.

4. **Per-fact retention policies as algebraic operation.** Mem0 and Zep explicitly lack retention policies as product features (per the Trace Continuity 2026 governance comparison). Substrate can do "expire memory after T days" as an algebraic decay operation on W with auditable evidence of expiry. This is white space for both substrate AND competitors — the first to ship a working version owns the GDPR "data minimization" compliance angle.

5. **Real-time learning during inference (K5) with audit trail.** Hebbian outer-product updates leave a recoverable trail in W. No competitor has a memory mechanism that both learns at inference time AND produces an audit log of what was learned in which inference. LLM in-context learning is ephemeral; agent-framework memory writes are file-level, not algebraic.

---

## (e) Competitive gaps — capabilities the competitive set has that substrate currently does NOT

1. **Managed-service developer ergonomics.** Anthropic Memory is mounted as a directory and used via existing bash tools — five lines of code to onboard. Substrate has no SDK, no daemon, no managed service. This is the dominant time-to-deploy gap. Per `meta_strategic_direction_AI_memory_subsystem_2026-05-22.md` item 2 ("productionized SDK + API + managed service") — this is acknowledged as the gap-to-ship.

2. **Tamper-resistant audit log infrastructure.** Anthropic ships immutable versions + audit log + redact endpoint as a managed product. The substrate's bit-algebra supports building this, but the daemon/WAL/snapshot infrastructure is not built. Re-entry.ai's 2026 EU AI Act Article 12 writeup makes explicit that "tamper-resistant" is the binding requirement — substrate must ship a WAL or signed-log layer to clear this bar in production.

3. **Temporal fact-evolution tracking.** Zep's Graphiti tracks "user's company was X, now is Y, since date T" automatically. Substrate's W can hold the bound state but does not natively track temporal evolution as a structured object. This is a real product gap if the buyer asks "show me how this fact changed over the past 30 days."

4. **Source-document grounding for hallucination reduction.** GraphRAG's 30-40% factual-error reduction is the metric enterprise compliance buyers benchmark on. Substrate's wedge is NOT "lower hallucination" — it is "audit-grade memory next to the LLM." If a buyer benchmark requires hallucination reduction, substrate must be paired with a GraphRAG-style citation layer; it does not substitute for it.

5. **Schema-bound query expressiveness.** Knowledge graphs (Neo4j, GraphRAG) hit 90%+ on schema-bound queries vs ~0% for vector RAG. Substrate is currently aligned with the vector-RAG side of that split (similarity-based retrieval), not schema-bound traversal. If the buyer pain is "answer questions over a schema," substrate is not the answer.

6. **Established commercial credibility.** Anthropic, OpenAI, Microsoft, and Neo4j ship products today. Mem0 has $24M Series A. Substrate has none of this. The "30-year-niche HDC" reputation is the public-perception headwind documented in `wave14d_competitive_landscape_research.md`.

---

## (f) Product framing — 1-sentence and 1-paragraph

### Internal framing (preserve)

"Algebraically-canonical fast-weight memory with exposed W for audit / verifiable-erase / provenance." Stays for substrate-team internal use.

### External 1-sentence framing (suggested)

> **An AI memory layer where every fact has a mathematical address — so deletion produces a certificate, audit shows the bit-level components of every answer, and edits happen at inference time without retraining.**

Why this framing: (i) leads with "mathematical address" — accessible analogy to "database row" without using the word database (per the meta-direction doc); (ii) "certificate" is the EU AI Act / GDPR vocabulary the compliance buyer reads; (iii) "bit-level components of every answer" replaces "decomposition" with a phrase a non-substrate-expert can visualize; (iv) "inference time without retraining" is the cost-vs-fine-tuning angle.

### External 1-paragraph framing (suggested)

> **Today AI systems remember in two ways: facts baked into the model weights (which can't be inspected, edited, or deleted) and documents in a vector database (which the model treats as opaque text once retrieved). Neither passes audit. We are building a third memory layer: a substrate where every stored fact has a mathematical address, deletion produces an auditable certificate, and every answer can be traced to the bit-level components that produced it. The layer sits next to your LLM — it doesn't replace generation, it makes the model's memory accountable. Built for the next decade of AI regulation: EU AI Act Article 12 audit logs, GDPR Article 17 right to erasure, FDA GMLP traceability — capabilities that LLM unlearning, RAG, and knowledge graphs each address partially and none address together.**

Why this framing: (i) opens by naming the two existing memory types the reader already knows — orients fast; (ii) "third memory layer" introduces the category without using insider language; (iii) "mathematical address" + "auditable certificate" + "bit-level components" — the three core differentiators in plain language; (iv) "sits next to your LLM — it doesn't replace generation" defuses the "are you trying to replace transformers?" objection (the Numenta failure mode from wave14d); (v) explicit regulatory hooks (EU AI Act, GDPR, FDA GMLP) prime the compliance buyer's mental model.

---

## (g) Calibrated assessment — DEFENSIBLE / CONTESTED / COMMODITY

### Per-capability verdict

- **The CATEGORY of "verifiable, auditable, editable AI memory as a substrate":** **DEFENSIBLE.** No competitor has all four capability classes (verifiable erase, editable at scale, per-fact provenance, compositional auditing) on a single primitive. The structural-class distinction (bit-algebra vs LLM weights vs vector projections vs files) is real and cannot be patched by feature additions. The "Unlearning Isn't Deletion" 2025 result is a structural ceiling for everyone in the LLM-weights regime.

- **Each INDIVIDUAL capability axis viewed in isolation:** **CONTESTED.** Anthropic owns file-level audit logs; Zep owns temporal-knowledge-graph provenance; GraphRAG owns source-citation grounding; Mem0 owns deletion-API ergonomics. A buyer who only needs ONE axis can buy a competitor today. Substrate wins on the COMPOUND CLAIM (all four classes on one primitive), not on any single axis.

- **The surrounding PLUMBING (SDK, daemon, dashboard, retention UI):** **COMMODITY — substrate is behind.** Anthropic ships a managed product today; substrate has none. Per the meta-direction doc, this is acknowledged as gap-to-ship and is not a research gap — it is product engineering.

- **The OPEN STANDARD play (5-probe Mirage erase protocol):** **DEFENSIBLE if shipped.** No competitor has equivalent. Kubernetes/SQL precedent: the entity that frames the rules owns the category. The 5-probe Mirage battery is the substrate-original construct that could become the industry definition of "verified AI memory erasure." This is the single strongest moat-establishing move available.

### Overall positioning verdict

**DEFENSIBLE as a category** (the compound capability claim is structurally unique), **CONTESTED on each axis** (every single feature has a competitor that does that one feature well), **COMMODITY on plumbing** (SDK + daemon + dashboard are catch-up work, not differentiators). The wedge product strategy (per `wave14d_competitive_landscape_research.md` and the meta-direction lock) is correct: lead with EU AI Act / GDPR compliance buyer, where the COMPOUND CLAIM is what they need and competitors' single-axis wins are insufficient.

### Calibrated P estimate

Probability that "auditable AI memory" as a category framing earns substrate a defensible market position over 24-36 months, GIVEN substrate ships the plumbing and a flagship deployment:
- Base lit-scan rate (novel-category positioning): ~0.45.
- Deflated by 0.15 for substrate-uncharted-regime (no commercial peer to anchor against per `[[feedback-lit-scan-calibration-penalty]]`).
- Deflated by additional 0.10 for plumbing risk (substrate has not shipped the daemon yet; Anthropic et al. shipping competing managed products in the meantime erodes positioning).
- Inflated by 0.10 for the "Unlearning Isn't Deletion" structural-ceiling argument (every LLM-weights competitor is provably below the bar substrate clears).
- **Final calibrated P = 0.30.**

This is a P(>=0.30) bet, not a P(0.80) certainty. The honest read: the positioning is correct, the structural argument is sound, the execution risk is the binding constraint.

---

## (h) Substrate-product implications

Per `[[feedback-no-papers-product-only]]` — product framing only.

1. **Lead the compliance wedge pitch with "deletion certificate" not "auditable memory."** Compliance buyers are reading the EU AI Act and GDPR; "certificate" is their vocabulary. "Auditable" is the substrate-team vocabulary. Translate.

2. **Concede the file-audit-log story to Anthropic in messaging; differentiate on the FACT-level audit story.** Do not try to compete on developer ergonomics for managed-agent file storage. Compete on "what's IN the file the agent wrote" — Anthropic's redact preserves file metadata; substrate redact preserves the algebraic identity of the deleted fact AND certifies it was removed from the answer-generation path.

3. **Pair substrate with GraphRAG, not against it.** GraphRAG handles source-document citation; substrate handles bit-atom decomposition for the synthesized answer. The wedge product (ProvenanceBag per wave14d) should explicitly slot above a GraphRAG layer, not replace it.

4. **Ship the 5-probe Mirage erase battery as an open standard FIRST.** This is the moat-establishing move. The Kubernetes/SQL precedent (the meta-direction doc names this) is correct: who frames the rules owns the category. Until the standard is public, substrate cannot anchor the "we set the bar competitors must clear" claim.

5. **Add a retention-policy framework as a product capability before competitors do.** Mem0 and Zep explicitly lack this. Per-fact algebraic decay with audit log of expiry is a winnable feature in the 6-12 month window.

6. **DO NOT message on "HDC" or substrate-internal mechanism names.** Per wave14d risk #6 ("HDC 30-year niche reputation") — the public reaction to HDC framing is "didn't that not work?" Lead with the capability and the regulatory hook; HDC is the implementation detail.

7. **No demo gap that I can identify from this drill.** The four capability classes already have empirical anchors (Bet 2/C Mirage erase, Bet A edits to M=16N, decompose_K_cliff, Lane D 4-primitive composition). The gap is product packaging, not science. NO exp_dev handoff recommended from this drill.

---

## (i) Citations (verified count: 16)

### Anthropic Memory + MCP
1. [Wire Blog — Anthropic Managed Agents memory](https://usewire.io/blog/anthropic-managed-agents-memory-context-engineering/) — April 23, 2026 public beta; files mounted at `/mnt/memory/`; per-write audit logs.
2. [opentools.ai — Anthropic Managed Agents Memory](https://opentools.ai/news/anthropic-managed-agents-add-memory-persistent-state-for-ai-that-actually-ships) — immutable versions; redact endpoint; rollback.
3. [Anthropic Memory MCP / Continue.dev](https://www.continue.dev/anthropic/memory-mcp) — MCP server form factor.
4. [PulseMCP — Knowledge Graph Memory MCP Server by Anthropic](https://www.pulsemcp.com/servers/modelcontextprotocol-memory) — knowledge-graph MCP variant.

### OpenAI ChatGPT Memory
5. [OpenAI — Memory and new controls for ChatGPT](https://openai.com/index/memory-and-new-controls-for-chatgpt/) — official memory feature page.
6. [OpenAI Help Center — Memory FAQ](https://help.openai.com/en/articles/8590148-memory-faq) — saved vs reference chat history; deletion timeline ("may take a few days").

### Agent memory vendors
7. [AgentMarketCap — Letta/Zep/Mem0/LangMem comparison (April 2026)](https://agentmarketcap.ai/blog/2026/04/10/agent-memory-vendor-landscape-2026-letta-zep-mem0-langmem) — vendor landscape April 2026.
8. [Atlan — Best AI Agent Memory Frameworks 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/) — comparative analysis.
9. [Mem0 docs — Delete Memory](https://docs.mem0.ai/core-concepts/memory-operations/delete) — GDPR-aligned delete API.
10. [DEV.to — Trace Continuity vs Mem0 vs Zep governance comparison](https://dev.to/heath_99ab1667dfecd3da406/trace-continuity-vs-mem0-vs-zep-ai-memory-governance-compared-1mhp) — "neither Mem0 nor Zep has configurable retention policies as a product feature."

### Vector DB / RAG compliance
11. [Atlan — AI Agent Memory Governance](https://atlan.com/know/ai-agent-memory-governance/) — vector-DB governance gaps.
12. [Aparavi — Reinventing Data Protection for the AI Era 2026 whitepaper](https://aparavi.com/whitepapers/reinventing-data-protection-for-the-ai-era-2026-whitepaper/) — vector layer compliance blind spot.

### GraphRAG
13. [Microsoft Research — GraphRAG](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/) — source-grounded provenance; 30-40% factual-error reduction.

### Machine unlearning (structural ceiling)
14. [arxiv 2505.16831 — Unlearning Isn't Deletion: Investigating Reversibility of Machine Unlearning in LLMs](https://arxiv.org/abs/2505.16831) — forgetting reversible by minimal fine-tuning; structural ceiling.
15. [IAPP — The AI right to unlearn](https://iapp.org/news/a/the-ai-right-to-unlearn-reconciling-human-rights-with-generative-systems) — legal framing of certifiable unlearning gap.

### EU AI Act Article 12 (logging mandate)
16. [FireTail blog — Article 12 and the Logging Mandate](https://www.firetail.ai/blog/article-12-and-the-logging-mandate-what-the-eu-ai-act-actually-requires) — Aug 2, 2026 enforceable; tamper-resistant logs; 6-month retention; €15M / 3% turnover penalty.

### Verification status
- All 16 citations are real, returned by WebSearch, with article-level summaries consistent with the surrounding context.
- Substrate-internal mechanism names were NOT included in any external query per `[[feedback-query-privacy-decomposition]]`.
- Anthropic Memory architectural claims (file mount, immutable versions, redact endpoint) cross-validated across at least 2 of citations 1-4.
- The "Unlearning Isn't Deletion" result is widely cited in 2026 governance literature (citations 11, 12, 15 all reference variants of this conclusion).

### Lit-scan limitations / open angles not closed by this drill
- The substrate's empirical anchors for the four capability classes are NOT independently verified by external lit-scan — they are internal to the project's verification battery. External claims should cite the open-standard 5-probe Mirage protocol (once published) rather than internal empirical anchors.
- The "real-time learning during inference (K5)" capability is the most substrate-novel claim in the positioning and has the weakest external lit-scan validation. Recommend a follow-up cross-domain probe (Trigger F) into "online learning + audit log" specifically — there may be a small adjacent literature in continual learning + interpretability that wasn't surfaced here.
- The "temporal fact-evolution" gap vs Zep was identified as a real product gap but not deeply explored. Follow-up axis: can the substrate's W natively encode temporal versioning, or does it need an external versioning layer? This is a substrate-physics question, not a positioning question.

EOF.
