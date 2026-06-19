# Wave 14d — Competitive Landscape & Product Direction (Unbiased)

**Date:** 2026-05-19
**Framing:** "What exists, what doesn't, what's the wedge" — NOT "is HDC good?"
**Honesty contract:** if HDC has been a 30-year niche, say so and explain whether the
substrate's specific capabilities change the calculus.

---

## 1. TL;DR

**Strongest wedge:** *Editable, auditable on-device memory layer for personalized
assistants and regulated-domain copilots*, where the substrate exposes a per-fact
"who-said-what-when" provenance trail and lets an operator surgically delete or
patch knowledge in milliseconds — capabilities that LoRA/RAG/model-editing all
fail at, at the same time, on CPU. **Biggest threat:** Apple's Foundation Models
framework (on-device LoRA adapters, ~3B params, free to developers) already owns
the on-device personalization channel — if the wedge is just "personalize on
device", it's dead. The wedge has to be **auditability + edit-without-retrain
under regulatory pressure (EU AI Act Aug 2026, GDPR right-to-erasure)**, which
neither Apple nor RAG vendors currently solve. **Biggest risk:** HDC has been a
30-year niche because nobody could show it competes with backprop on the metrics
markets actually buy (loss, perplexity, downstream accuracy). The product MUST
sell *non-loss* metrics (editability, audit trail, latency floor) or it will
lose on the metric customers benchmark on.

---

## 2. Who's actually doing HDC/VSA today (and outcomes)

### 2.1 The companies that explicitly brand HDC/VSA

- **Simuli (Rachel St. Clair, COO Binoy Syed)** — only pure-play "Hyperdimensional
  AI" startup with public marketing. Pitched as "lossless data-agnostic compression
  + compute-on-compressed-data" + AGI gestures. Public traction as of early 2025:
  one Digital Trends contributor-content piece, podcast appearances, no disclosed
  funding round, no product GA, no enterprise logos.
  [Digital Trends: Simuli](https://www.digitaltrends.com/contributor-content/simuli/),
  [NewsBreak: Simuli + Human Mind](https://www.newsbreak.com/news/3643172973020-rachel-st-clair-and-simuli-combine-human-mind-with-hyperdimensional-computing-for-truly-intelligent-and-accessible-ai)
  **Honest read:** thought-leadership stage, not a commercial threat. No moat we
  can identify from public material.

- **BrainChip (Akida)** — *event-driven neuromorphic*, NOT primarily HDC, but
  positioned in the same "non-GPU, low-power, on-chip-learning" market the
  substrate would enter. Shipping AKD1500 co-processor (800 GOPS @ <300 mW), $25M
  raise Dec 2025, samples now, volume Q3 2026. Announcing a 1.2B-param on-device
  LLM at CES 2026.
  [BrainChip AKD1500 press](https://brainchip.com/brainchip-unveils-breakthrough-akd1500-edge-ai-co-processor-at-embedded-world-north-america/),
  [BrainChip $25M raise (SiliconAngle)](https://siliconangle.com/2025/12/10/brainchip-lands-25m-bring-neuromorphic-ai-edge/)
  **Honest read:** hardware company, not memory-substrate company. They're the
  rails our substrate could ride; not a head-on competitor.

- **Mythic AI** — analog compute-in-memory chip. Not HDC. Raised $125M end of
  2025, sells "Starlight" APU < 1 W, DoD + automotive design wins.
  [Bloomberg: Mythic $125M](https://www.bloomberg.com/news/articles/2025-12-17/ai-chip-startup-mythic-raises-125-million-in-bid-to-take-on-nvidia)
  **Relevance:** the substrate-on-Mythic story is plausible (low-precision XOR/
  majority maps to in-memory compute), but Mythic is selling neural-net inference,
  not symbolic memory.

- **Numenta** — *no longer an HTM company.* As of Jan 2025, foundational research
  spun out to nonprofit Thousand Brains Project; commercial Numenta is now a
  **CPU-LLM-acceleration vendor (NuPIC)** with Oracle Cloud deal June 2025. They
  pivoted *away* from the bio-inspired substrate story to "sparsity + pruning
  for transformer inference."
  [NeuromorphicCore on Numenta](https://www.neuromorphiccore.ai/insights/numenta/)
  **Lesson for us:** the only public "brain-inspired memory" company gave up the
  brain-inspired memory pitch and pivoted to LLM speed. That is the most
  important data point in this entire document. The market did not pay for HTM.

- **Vicarious** — folded into Alphabet, then into Intrinsic (Alphabet's robotics
  arm) June 2024. Active business is industrial robotics, not memory substrates.
  [Vicarious Wikipedia](https://en.wikipedia.org/wiki/Vicarious_(company))

- **IBM Research Zurich** — in-memory HDC papers continue (Sebastian, Rahimi,
  Karunaratne). Research, not productized.
  [IBM Research blog on in-memory HDC](https://research.ibm.com/blog/in-memory-hyperdimensional-computing)

- **Kanerva (Berkeley/Redwood)** — academic figurehead. 2025 work on residue
  number HDC. No company.

- **AUI (Augmented Intelligence Inc, Apollo-1)** — *neuro-symbolic*, not HDC,
  but worth knowing: $750M valuation cap, Fortune 500 closed beta, GA expected
  end 2025. They're the symbolic-AI flag-carrier that VCs are funding.
  [VentureBeat: AUI / Apollo-1](https://venturebeat.com/ai/the-beginning-of-the-end-of-the-transformer-era-neuro-symbolic-ai-startup)
  **Relevance:** customers ARE willing to fund non-transformer symbolic stacks
  when there's an enterprise pain point. AUI's pain point is "task reasoning
  separated from linguistic fluency" — adjacent to but distinct from ours.

- **Lemurian Labs** — *not HDC.* Software-portability layer (Tachyon) for
  heterogeneous hardware. $28M Series A Dec 2025. Mentioned because the name
  shows up in HDC searches as a false positive.
  [Lemurian $28M](https://www.lemurianlabs.com/press-releases/lemurian-labs-raises-28-million-series-a-to-liberate-ai-from-the-constraints-of-hardware)

- **Cerca.ai** — could not verify a company by that name doing HDC. Possibly
  defunct, possibly user mis-remembered. No public footprint.

### 2.2 Honest summary of "HDC commercial status as of May 2026"

- **30-year niche, still niche.** Pentti Kanerva published the foundational
  paper in 1988. As of 2026 there is *no* dominant HDC product, no IPO, no
  hyperscaler-acquired HDC team.
- The one company that bet the company on bio-inspired sparse memory (Numenta)
  visibly **pivoted away** in early 2025.
- The active commercial layer has shifted to (a) edge neuromorphic chips
  (BrainChip, Mythic) which are HDC-*compatible* not HDC-*native*, and (b)
  academic-industrial partnerships for biosignal classification.
- Energy-efficiency / one-shot-learning have not been enough to displace
  transformers + LoRA in any commercial category we can identify.

This is the part of the report most worth absorbing. The substrate's
capabilities have to be unusual on a *different* axis than HDC has historically
been pitched on, or the answer is "no product."

---

## 3. Adjacent technologies competing for the same product space

| Category | Leaders | What they DO well | What they CAN'T do |
|---|---|---|---|
| **Vector DB / RAG** | Pinecone, Qdrant ($50M Series B 2025), Weaviate, Milvus, Chroma | Retrieve passages by cosine sim; cheap; commodity | Cannot *decompose* a passage into its constituent facts; cannot edit a specific factual atom; no provenance per dimension; hallucination floor still 5%+ even with self-reflective RAG |
| **Knowledge Graph + GraphRAG** | Neo4j, Microsoft GraphRAG | Auditable subgraph retrieval; 90%+ on schema-bound queries vs. ~0% for vector RAG; explicit relations | Requires ontology engineering; not continual / Hebbian; expensive to build and maintain; doesn't bind to byte/token sub-symbols |
| **Model editing** | ROME, MEMIT, MEND, UnKE, LocFT-BF | Patch one fact in a transformer's weights | Sequential edits degrade and induce catastrophic forgetting after a few hundred patches; per-edit cost is non-trivial; no audit of "which edit caused this output"; unverified at production scale |
| **On-device LLM** | Apple Foundation Models (~3B + LoRA adapters), Google Gemini Nano 3.1B, Microsoft Phi | Free SDK, on-device latency, privacy story | LoRA adapters can't be edited at fact-granularity; cannot delete a *specific* user utterance from weights; one-LoRA-per-user scales linearly; no audit trail |
| **Continual learning frameworks** | Avalanche, ContinualAI; EWC, orthogonal subspace | Research-grade benchmarks for incremental learning; recent EWC cut forgetting 12.6%→6.9% on KG link prediction | Not memory substrates; integrate with neural nets that still require backprop; not deployed in real products |
| **Machine unlearning** | Academic + emerging "deletion-as-a-service" tools | Aim to satisfy GDPR Art. 17 | No verified production unlearning method exists; the legal "Goldilocks standard" papers (2025) explicitly say current techniques are inadequate |
| **Personalization on-device** | Apple Adapter Training Toolkit, Gemini Nano + LoRA | Swift / Kotlin API; PEFT; works today | Adapters are opaque; cannot point to a specific fact and edit/remove it; no per-user audit log |

### Critical observation

Every adjacent category has a **specific failure mode** the substrate's six
validated capabilities can attack:

- RAG fails on **decomposition + edit** — we have auditable decomposition.
- Model editing fails on **sequential edits → catastrophic forgetting** — we have
  random-replay continual learning with +0.66–0.73 BWT at K=4.
- LoRA adapters fail on **fact-granularity edit** — we can edit individual bindings.
- Machine unlearning fails on **verified deletion** — we can recover (byte, position)
  atoms, prove they're gone, and prove the rest is intact.

This is the wedge surface. It is narrow but it is real and it is unoccupied.

---

## 4. The substrate's unique value proposition (specific)

Be precise. The substrate's *real* USP is not "HDC is the future." It is the
following compound claim, which to our knowledge no other shipping system makes
all at once:

> **A memory layer where every stored fact has a provable, recoverable
> identity (the binding atoms), can be deleted or modified in O(1) without
> retraining, can be audited end-to-end for what it contains, can keep learning
> without forgetting at K=4, and runs on a CPU sub-100ms.**

Each adjacent technology beats us on one of those axes individually:
- A vector DB is faster to write to.
- A KG is more expressively related.
- ROME has been studied in more papers.
- LoRA has Apple's distribution.
- An Avalanche replay buffer can do continual learning if you don't mind
  retraining a net.

But none of them does **all of them on a CPU substrate that is itself the
memory** — which is the only configuration that satisfies the auditability
demands of EU AI Act Art. 13 (transparency) and GDPR Art. 17 (erasure) *while*
remaining personal-device-deployable *while* remaining continually updateable.

That compound claim is the wedge. Everything else is marketing noise.

---

## 5. Real-world product opportunities — 5 concrete examples, ranked by tractability

Ranking criteria: (a) is there a buyer with budget today, (b) is the regulatory
pressure binding, (c) does our substrate's specific weakness (compositional
generation quality, no perplexity-scaling) not matter, (d) can we ship in 3–6
months.

### Tier 1 — most tractable

**#1. EU AI Act compliance layer for high-risk LLM deployments (healthcare,
credit, HR, public safety)**
- *Buyer:* Enterprise compliance officer + ML Eng lead at banks, hospitals,
  HR-tech SaaS deploying LLM copilots.
- *Pain:* Aug 2, 2026 deadline. Article 13 requires "appropriate traceability
  and explainability." Article 17 GDPR right-to-erasure. Penalty: €15M or 3%
  global turnover. They have *no* technology that proves to an auditor *which
  facts contributed to an output and that a specific user's data was removed*.
- *Today:* Patchwork of audit logs + model cards + prayer. RAG + GraphRAG
  partially addresses retrieval-side, but they cannot prove deletion from the
  model's *internal* memory.
- *Our wedge:* the substrate sits as a sidecar to the LLM, stores user-derived
  knowledge, allows auditor-visible deletion in milliseconds, and shows the
  exact byte-position atoms that contributed to the answer.
- *Why this wins:* The buyer is not buying "intelligence" — they're buying
  "regulator off our back." Our weakness on perplexity is irrelevant.
- *Sources:* [EU AI Act 2026 (Legalnodes)](https://www.legalnodes.com/article/eu-ai-act-2026-updates-compliance-requirements-and-business-risks),
  [GDPR + LLM (PPC.land)](https://ppc.land/study-large-language-models-qualify-as-personal-data/),
  [Goldilocks standard unlearning](https://cep-project.org/wp-content/uploads/2025/11/Pratiksha-Ashok-THE-GOLDILOCKS-STANDARD-Machine-Unlearning-and-the-Right-to-be-Forgotten-Under-Emerging-Legal-Frameworks.pdf)

**#2. Healthcare AI decision-provenance / FDA GMLP audit trail**
- *Buyer:* AI/ML team at digital-health vendors with FDA-regulated SaMD or LDT.
- *Pain:* FDA GMLP requires "appropriate information about an AI system's logic
  — how outputs are reached" plus complete ALCOA+ audit trails. Postmarket
  surveillance requires real-world performance + drift tracking + traceable
  field updates.
- *Today:* Custom logging + opaque retraining cycles.
- *Our wedge:* Per-fact provenance + edit-without-retrain → demonstrable
  conformance to GMLP, faster postmarket update cycles, no full retraining for
  a single corrected guideline.
- *Sources:* [FDA AI guidance 2025 (USDM)](https://usdm.com/resources/blogs/fda-ai-guidance-2025-life-sciences-compliance),
  [Auditable RAG + provenance (PMC12913532)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12913532/)

### Tier 2 — tractable but more crowded

**#3. Personalized on-device assistant with editable user memory**
- *Buyer:* Consumer-AI product teams (third-party iOS/Android apps, automotive
  HMI vendors, smart-home OEMs) building on Apple Foundation Models / Gemini
  Nano but needing per-user persistent memory.
- *Pain:* Apple's LoRA adapters cannot remember user-specific facts between
  sessions in an editable, deletable way. "Hey Siri, forget what I told you
  about my dentist" doesn't work.
- *Today:* App-side JSON blobs + system prompts (brittle); LoRA-per-user
  (doesn't scale); cloud RAG (kills the privacy story).
- *Our wedge:* CPU-side memory bundle that holds personal facts, supports
  edit/delete by user gesture, exposes a clean Swift/Kotlin API.
- *Why threatened:* Apple and Google will plausibly ship a first-party version
  of this. Time-to-market is short.
- *Sources:* [Apple FM Adapters](https://developer.apple.com/apple-intelligence/foundation-models-adapter/),
  [Apple FM tech report 2025](https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025)

**#4. Customer-support knowledge correction tier ("hot-patch the bot")**
- *Buyer:* CX/support-ops at SaaS companies running RAG-backed support agents.
- *Pain:* Knowledge changes daily; vector DB re-embedding is expensive; fine-
  tuned LLMs require retrain cycles for material changes; RAG still hallucinates
  5%+ even at self-reflective tier.
- *Today:* RAG + LLM + prayer.
- *Our wedge:* Editable substrate as a "decision-grade" memory tier above
  vector DB. Specific facts that the bot must get exactly right (pricing,
  refund policy, SLA numbers) live in the substrate; auditor can show why the
  bot said $99 when the policy was $89.
- *Sources:* [RAG limits in support (AptEdge)](https://aptedge.io/artificial-intelligence/a-support-engineers-guide-to-rag-eliminating-llm-hallucinations-in-customer-support),
  [Enterprise LLM hallucination (Glean)](https://www.glean.com/perspectives/when-llms-hallucinate-in-enterprise-contexts-and-how-contextual-grounding)

### Tier 3 — less tractable

**#5. Real-time biosignal classification for wearables (the historical HDC
sweet spot)**
- *Buyer:* Wearable / medical-device OEM (EMG prosthetics, seizure detection,
  emotion recognition).
- *Pain:* On-device classification with one-shot learning, low power, robust
  to noise.
- *Today:* This is *the* application HDC has the most legitimate publication
  history in — Rahimi (ETH/Berkeley) papers on EMG/EEG, sub-10ms inference,
  256-channel scaling.
- *Our wedge:* The substrate is *not* differentiated here — we'd be competing
  with 10+ years of academic-industrial HDC for biosignal. This is "do what
  has already been done, possibly better."
- *Why ranked last:* Buyers are few, sales cycles are long (regulated medical
  device), and our substrate's special capabilities (decompose/edit/recompose)
  don't matter for a classifier.
- *Sources:* [HDC for biosignals (ETH)](https://iis-people.ee.ethz.ch/~arahimi/papers/PROC18.pdf),
  [HDC + EEG + seizure (arXiv 2205.07654)](https://arxiv.org/pdf/2205.07654)

---

## 6. Smallest credible wedge product (3–6 months)

**Working name: "ProvenanceBag"** — a CPU library + audit dashboard that wraps
any LLM call and stores every user-supplied fact in an HDC bundle with
auditable per-byte atoms, supports `edit(fact_id, new_value)`,
`delete(user_id)`, and `explain(answer_id) → [fact atoms used]`.

**v1 scope (small enough to actually ship):**
1. Python + Rust library; Swift / Kotlin shims if buyer pulls.
2. Wraps OpenAI / Anthropic / Apple FM / Gemini API as a "memory middleware."
3. Three exposed verbs: `remember`, `forget`, `explain`.
4. One audit UI: per-user fact list + provenance chain per LLM answer.
5. One vertical reference deployment, ideally healthcare or fintech, behind a
   binding regulatory deadline.

**Why this is the right v1:**
- Demonstrates one Tier-1 capability (auditable decomposition + edit) cleanly.
- Does **not** require us to ship a fusion-bundle K=512 capability — that's v2.
- Does **not** require Hebbian training to beat backprop on perplexity — we
  punt on that fight by sitting *next to* the LLM, not replacing it.
- Customer base exists (compliance-pressed AI deployers, regulated SaaS).
- Honest competitive moat: nobody else can show per-fact provenance + delete
  in O(1) on CPU.

**What v1 explicitly does not promise:**
- Replacing the LLM.
- Beating transformer accuracy on generative tasks.
- Mobile-grade footprint.
- "AGI."

---

## 7. Biggest credible product (full vision)

**"Hebbian Memory OS"** — a complete substrate-as-OS for on-device personalized
AI that ships the full Tier-1 capability set:

- Hebbian-only training (no backprop, neuromorphic-compatible)
- R10 concept fusion at K=512 for compressed long-term memory
- Random-replay continual learning across years of user lifetime data
- Sub-100ms CPU inference
- Per-fact audit + edit + delete
- Standard SDK on iOS / Android / Linux / Wear / automotive

This product *would* compete with Apple Foundation Models / Gemini Nano *if*
the Tier-1 killer (an LM driven by Hebbian-trained VSA representations rather
than backprop) is delivered. Until that killer is delivered the big vision is
speculative.

**Honest read on the big vision:** delivering this requires the "big bet" in
[project_two_bets](../../.claude/projects/d--AI/memory/project_two_bets.md) — a
Hebbian-trained VSA-LM that performs competitively with a small transformer.
If that bet fails, the big product collapses back to ProvenanceBag-scale.

---

## 8. Critical risks to product viability

| Risk | Severity | Mitigation |
|---|---|---|
| **Apple ships first-party editable on-device memory** in iOS 27 (June 2026 WWDC). Wedge #3 dies overnight; wedge #1 partially impacted. | High | Lead with the audit-trail / regulator-facing wedge (#1, #2), not the consumer wedge. Apple's incentive to expose raw provenance to enterprise auditors is weak. |
| **Throughput at scale.** Sub-100ms on CPU is great for one user; what does 10K QPS look like? Bundles are unitary objects — does fan-out break the model? | High | Benchmark early. The wedge sizes (compliance, healthcare) tolerate higher latency than consumer; honest about which use cases fit. |
| **Memory footprint of K=512 bundles.** Big bundles need RAM. On-device deployment may need K-tier negotiation. | Medium | The R10 monotone K=8→512 result lets us tune per-device; advertise that. |
| **Update latency for new facts at scale.** We've shown +0.66 BWT at K=4 — what's the deletion latency at K=512 across 10M facts? | Medium | Need to publish a real ops benchmark. Without it the audit-trail pitch is theater. |
| **Maintenance complexity / on-call burden** for a custom-data-structure deployment vs. a vector DB. | Medium | Wrap as a managed service; do not ship raw substrate to ops teams in v1. |
| **HDC's 30-year niche reputation** — buyers' first reaction will be "didn't that not work?" | High | Don't lead with "HDC." Lead with "auditable memory for regulated AI." HDC is the implementation detail. |
| **Talent moat is thin.** The substrate's core researchers are a small pool; if Apple or Google decides to enter, they can hire it. | Medium | File patents on the specific recovery + edit operations; build the product moat (audit UI, compliance integrations) faster than the algorithm moat. |
| **Backprop perplexity gap.** If the big-bet VSA-LM never closes the gap with a small transformer, the big product is capped. | High (long-term) | Big-bet is a research bet; small-bet (ProvenanceBag) doesn't depend on it. Separate funding/timing. |
| **Numenta lesson.** The only public bio-inspired-memory company gave up that pitch in Jan 2025. If we sell on bio-inspiration we will likely fail the same way. | High | Sell on regulatory + auditability outcomes. Bio-inspiration is internal motivation, not external messaging. |

---

## 9. Sources

### HDC / VSA companies and research

- [BrainChip AKD1500 (BrainChip)](https://brainchip.com/brainchip-unveils-breakthrough-akd1500-edge-ai-co-processor-at-embedded-world-north-america/)
- [BrainChip $25M raise (SiliconAngle)](https://siliconangle.com/2025/12/10/brainchip-lands-25m-bring-neuromorphic-ai-edge/)
- [Bloomberg: Mythic $125M](https://www.bloomberg.com/news/articles/2025-12-17/ai-chip-startup-mythic-raises-125-million-in-bid-to-take-on-nvidia)
- [Numenta pivot (NeuromorphicCore)](https://www.neuromorphiccore.ai/insights/numenta/)
- [Vicarious / Intrinsic (Wikipedia)](https://en.wikipedia.org/wiki/Vicarious_(company))
- [IBM in-memory HDC](https://research.ibm.com/blog/in-memory-hyperdimensional-computing)
- [Simuli (Digital Trends)](https://www.digitaltrends.com/contributor-content/simuli/)
- [Simuli (NewsBreak)](https://www.newsbreak.com/news/3643172973020-rachel-st-clair-and-simuli-combine-human-mind-with-hyperdimensional-computing-for-truly-intelligent-and-accessible-ai)
- [Lemurian Labs $28M](https://www.lemurianlabs.com/press-releases/lemurian-labs-raises-28-million-series-a-to-liberate-ai-from-the-constraints-of-hardware)
- [AUI / Apollo-1 neuro-symbolic (VentureBeat)](https://venturebeat.com/ai/the-beginning-of-the-end-of-the-transformer-era-neuro-symbolic-ai-startup)
- [HDC vs. NN comparison (arXiv 2207.12932)](https://arxiv.org/pdf/2207.12932)
- [HDC biomedical review (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12192801/)

### Adjacent tech — RAG / Vector DB / Knowledge Graph

- [Vector DB comparison 2025 (TensorBlue)](https://tensorblue.com/blog/vector-database-comparison-pinecone-weaviate-qdrant-milvus-2025)
- [Pinecone DRN (InfoQ)](https://www.infoq.com/news/2025/12/pinecone-drn-vector-workloads/)
- [Qdrant $50M Series B (TechTarget)](https://www.techtarget.com/searchdatamanagement/news/366640132/Qdrant-raises-50M-in-funding-to-fuel-vector-database-growth)
- [GraphRAG enterprise (Neo4j)](https://neo4j.com/labs/genai-ecosystem/graphrag/)
- [GraphRAG vs vector-only accuracy](https://medium.com/aingineer/enterprise-graphrag-building-production-grade-llm-applications-with-knowledge-graphs-b4d567c95cbf)
- [RAG limitations / hallucination (MEGA-RAG, PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12540348/)
- [RAG provenance & audit](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12913532/)

### Model editing / continual learning

- [The Mirage of Model Editing (arXiv 2502.11177)](https://arxiv.org/pdf/2502.11177)
- [Model editing methods (EmergentMind)](https://www.emergentmind.com/topics/model-editing-methods)
- [Avalanche framework (Medium)](https://medium.com/pytorch/avalanche-and-end-to-end-library-for-continual-learning-based-on-pytorch-a99cf5661a0d)
- [Continual learning + catastrophic forgetting 2026 (Zylos)](https://zylos.ai/research/2026-04-09-continual-learning-catastrophic-forgetting-ai-agents)

### On-device LLM

- [Apple FM adapter training](https://developer.apple.com/apple-intelligence/foundation-models-adapter/)
- [Apple FM tech report 2025](https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025)
- [Gemini Nano (Android Developers)](https://developer.android.com/ai/gemini-nano)
- [Apple FM analysis (GitHub)](https://github.com/fguzman82/apple-foundation-model-analysis)
- [LoRA personalization limits (arXiv 2511.20072 MTA)](https://arxiv.org/pdf/2511.20072)
- [LoRe low-rank reward (arXiv 2504.14439)](https://arxiv.org/pdf/2504.14439)

### Regulation / compliance

- [EU AI Act 2026 (Legalnodes)](https://www.legalnodes.com/article/eu-ai-act-2026-updates-compliance-requirements-and-business-risks)
- [EU AI Act timeline (Dataguard)](https://www.dataguard.com/eu-ai-act/timeline)
- [EU AI Act summary (SIG)](https://www.softwareimprovementgroup.com/blog/eu-ai-act-summary/)
- [The XAI Reckoning 2026 (Cogent)](https://cogentinfo.com/resources/the-xai-reckoning-turning-explainability-into-a-compliance-requirement-by-2026)
- [GDPR + LLMs as personal data (PPC.land)](https://ppc.land/study-large-language-models-qualify-as-personal-data/)
- [GDPR + LLMs technical & legal obstacles (MDPI)](https://www.mdpi.com/1999-5903/17/4/151)
- [The Goldilocks Standard (machine unlearning + RTBF)](https://cep-project.org/wp-content/uploads/2025/11/Pratiksha-Ashok-THE-GOLDILOCKS-STANDARD-Machine-Unlearning-and-the-Right-to-be-Forgotten-Under-Emerging-Legal-Frameworks.pdf)
- [Machine unlearning of PII (ACL 2025 NLLP)](https://aclanthology.org/2025.nllp-1.6.pdf)
- [FDA AI guidance 2025 (USDM)](https://usdm.com/resources/blogs/fda-ai-guidance-2025-life-sciences-compliance)
- [FDA AI guidance for medical devices (Jama)](https://www.jamasoftware.com/blog/navigating-fda-ai-guidance-for-medical-devices-a-practical-guide/)
- [Auditable framework for clinical AI (PMC12913532)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12913532/)
- [AI Product Passport (arXiv 2512.13702)](https://arxiv.org/pdf/2512.13702)

### Customer support / enterprise LLM

- [Glean: LLM hallucinations in enterprise](https://www.glean.com/perspectives/when-llms-hallucinate-in-enterprise-contexts-and-how-contextual-grounding)
- [AptEdge: RAG for support](https://aptedge.io/artificial-intelligence/a-support-engineers-guide-to-rag-eliminating-llm-hallucinations-in-customer-support)

### HDC biosignal applications

- [HDC for biosignals (ETH/Rahimi)](https://iis-people.ee.ethz.ch/~arahimi/papers/PROC18.pdf)
- [HDC + EEG seizure detection (arXiv 2205.07654)](https://arxiv.org/pdf/2205.07654)
- [HDC in biomedical sciences review (PeerJ CS)](https://peerj.com/articles/cs-2885.pdf)
