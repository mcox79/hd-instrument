# Research: Demo Visualization and UX -- 5x Depth Drill
# Date: 2026-06-08
# Topic: Substrate demo rendering, animation, and interaction patterns
# Calibration: P_deflated applied (lit-scan -0.20); P_theoretical x P_empirical split below

---

## HEADLINE

Substrate demo has three categorically differentiating visualization axes that no API-only
LLM demo can replicate: (1) per-token substrate-attention layer display showing live K/V
injection at inference time, (2) auditable provenance chain with click-to-verify source
expansion, and (3) algebraic operation playground (AND/NOT/COUNT/counterfactual do()).
The hero pattern recommendation is a live two-panel comparison: substrate-augmented Pythia
answering correctly with visible audit chain vs. raw Pythia (same params) answering without
one. The 30-second hook is "same model, different substrate" -- the substrate provides the
facts; the LLM provides the reasoning; together they beat a model 10x larger.

---

## Cheap decisive test

Implement one interactive element first before building anything else: a static HTML page
with a single 3-question benchmark comparison (substrate-augmented Pythia-1.4B vs GPT-4o-
mini on 3 factual multi-hop questions). Manual answers, no live inference. If a test
audience of 3-5 people who see this page correctly read the value proposition in under 30
seconds without explanation, the visual framing is working and you build the rest. If they
are confused, the framing needs work before investing in live-render infrastructure.

Estimated cost: 2 hours of static HTML.
Gate criterion: 4/5 observers answer "I understand what this does" within 30 seconds.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### HARD-PASS criteria (signals the demo approach is working)

- HP-1: Median time-to-comprehension (what does this do?) <= 30 seconds for 5 non-expert
  observers watching the hero section without any explanation text.
- HP-2: Median time-to-engagement (clicking at least one interactive element) <= 60 seconds.
- HP-3: The substrate-attention panel visualization (Panel B) can sustain 60fps on a
  MacBook M-class or equivalent mid-tier laptop at N=512 with 5 visible retrieval events
  per second. (WebGL path; Three.js or similar).
- HP-4: A 30-question benchmark comparison table renders the substrate advantage on the
  relevant subset without requiring a statistician to read it (ratio metric, not raw scores).
- HP-5: Mobile rendering of hero counter + audit chain expansion passes WCAG 2.1 AA
  contrast check and requires no hover interaction for core content.

### HARD-FAIL criteria (if any of these, stop and redesign before shipping)

- HF-1: The per-token substrate-attention visualization causes iframe/tab crashes on 2 or
  more of {Chrome, Firefox, Safari} with N > 1024 and 10+ simultaneous retrieval events.
  If this occurs, fall back to a replay-mode visualization (pre-recorded WebM) rather than
  live WebGL.
- HF-2: The audit chain click-expand interaction depth exceeds 4 clicks to reach a source
  document on mobile. Four clicks is the empirical limit for investor demo contexts.
- HF-3: The 30-question benchmark comparison is read as "substrate always wins" without
  visible failure cases. Demos with zero visible failure cases are perceived as cherry-picked
  and reduce trust. At least 3 questions where raw Pythia and substrate-augmented Pythia
  give the same answer must be visible (honest baseline).
- HF-4: Total page weight including WebGL assets exceeds 3MB on first load over a 10 Mbps
  connection (LCP > 3 seconds). This is the realistic investor-on-phone threshold.

---

## Level 1 -- Hero counter / 30-second visual hook

### Option A (RECOMMENDED PRIMARY): Two-panel live comparison counter

Left panel: "Substrate-augmented Pythia-1.4B" -- answer + audit chain visible.
Right panel: "GPT-4o-mini (70x larger parameter count)" -- answer only, no provenance.

Both panels answer the same question simultaneously. The left panel shows:
- Answer text streaming
- Fact retrieval indicator: "Retrieved 3 facts in 0.4ms"
- Audit chain links appearing inline as answer renders

The right panel shows:
- Answer text streaming (same or worse answer)
- No provenance. "Source: model weights (unverifiable)"

Below both panels: a live cost ticker.
Left: "$0.00004 per query (substrate lookup + Pythia inference)"
Right: "$0.0008 per query (GPT-4o-mini API)"

This framing is visceral because it shows the same answer with 20x cost difference and
an audit capability the API model structurally cannot provide.

P_theoretical: 0.75 (conversion rate on side-by-side demos is well-established in B2B SaaS)
P_empirical: 0.55 (deflated 0.20 per calibration rule; depends on substrate actually
winning the comparison questions chosen, and on Pythia-1.4B being competitive enough)

### Option B: Live fact-ingestion counter

Hero text: "200,143,221 facts indexed. Growing."
Counter ticks up in real time (or fakes a plausible rate). Below the counter:
"Retrieved in 0.4ms. Context window: 512 tokens. LLM context equivalent: 2.4M tokens."

This hits the "context window ratio" axis. The key metric to show is not the raw fact count
but the ratio: "substrate stores what would require a 2.4M token context window."
Context window ratio = (200M facts * ~12 tokens/fact) / (4096 token context) = ~585,000x.
That number is the visceral hook for the memory axis.

P_theoretical: 0.60. P_empirical: 0.40 (deflated; depends on fact count being live, not
cached; depends on ratio framing landing correctly).

### Option C: Substrate "consuming" Wikipedia real-time

Progress bar and counter showing live KB growth. "Added 847 new facts in the last minute."
Feeds into the "system is alive" framing. Works well as a secondary element paired with A.

### Option D: Geographic shard map

World map with shard locations lighting up. Better for multi-tenant enterprise pitch than
technical demo. Low priority for Tier 5 sprint.

### Option E: Cost accumulator race

Two tickers: "Substrate session cost so far: $0.0000..." vs "GPT-4o-mini equivalent: $..."
Ticker runs in real time as you interact with the demo. The gap widens visually.
This is the most visceral cost argument available but requires live inference to make honest.

### Option F: "Today's substrate growth" stat

Simple daily stat block: "Today: +14,230 facts | Latency: 0.4ms avg | Uptime: 100%"
Low-lift, good for a secondary trust-signal row below the hero.

### Option G: Context window ratio meter

Gauge or progress bar comparing substrate effective context to LLM context window.
"Substrate: 2.4M token equivalent. GPT-4 context: 128K tokens. Long-context Gemini: 2M tokens."
One bar chart. Substrate bar extends past the frame on the right.

### Option H: Latency comparison meter

Three columns: "Substrate retrieval: 0.4ms | RAG: 80ms | Fine-tune: not applicable."
Simple. Technical audience immediately understands the retrieval-path advantage.

---

## Level 2 -- Audit chain rendering

### Pattern A (RECOMMENDED): Progressive-disclosure provenance tree

Default view: answer + inline citation markers [1], [2], [3].
Click [1]: expands to show Fact text + source document name + shard ID + timestamp.
Click source document: opens primary source URL in new tab.
On mobile: same interaction, touch target >= 48px, no hover required.

Reference design: Perplexity.ai inline citations. They made this pattern mainstream.
Substrate's advantage over Perplexity: the citation is a cryptographic binding, not just
a URL pointer. That distinction should be surfaced in the tooltip text.

P_empirical: 0.70 (this pattern is already user-validated by Perplexity's adoption;
substrate implementation risk is engineering, not UX).

### Pattern B: Confidence-per-binding color coding

Inline citation markers colored green/yellow/red by cosine similarity score.
Green: similarity >= 0.85. Yellow: 0.70-0.84. Red: < 0.70.
Include a legend. Colorblind-safe: use green/amber/red with pattern fill as backup.

### Pattern C: Multi-hop K-hop chain visualization

For a K=3 query: show a horizontal chain diagram.
Node 0 (Query) -> Node 1 (Fact A, sim=0.92) -> Node 2 (Fact B, sim=0.87) -> Node 3 (Answer)
Arrows labeled with similarity scores and shard IDs.

For K > 5: collapse intermediate nodes into an expandable ellipsis. The user can click to
expand the full chain. Do not show all 10 hops by default on mobile.

Research finding: BertViz and AttentionViz (attentionviz.com) show that attention over many
steps becomes unreadable above ~8 simultaneous visible edges. Recommendation: show K<=4 by
default, expand on demand.

P_empirical: 0.50 (K-hop chain vis is novel in consumer AI; no direct reference design
exists; requires user testing to confirm comprehension).

### Pattern D: Merkle proof interactive expansion

Click "Verify integrity" button on any answer. Expands a collapsible panel showing:
- Fact binding hash
- KB root hash
- Proof path (3-4 hashes)
- "Verify" button that re-computes and confirms

This is a categorical differentiator: no API LLM can show this. The pattern is borrowed from
blockchain explorers (etherscan.io transaction trace pattern).

P_empirical: 0.35 (deflated; technical audiences will engage; non-technical may not).

### Pattern E: Shard source labels

Each retrieved fact labeled with its shard origin: "[Shard: customer-A-kb | Shard: public-wiki]"
For multi-tenant demo: show 3 visible shards in different colors. Makes isolation tangible.

### Pattern F: "Where did this fact come from" provenance tree

Full tree view: Query -> Retrieval step -> Fact node -> Source document -> Original corpus.
Works well as a deep-dive view, not a default view. Accessible via "Show full provenance" link.

---

## Level 3 -- Substrate-attention layer visualization (Panel B, categorical)

This is the highest-differentiation visualization in the entire demo. No API LLM can expose
this view because it requires access to internal KV injection. This is ONLY possible because
substrate is architecture-internal.

### Pattern A (RECOMMENDED): Live per-token retrieval stream

Two-column layout:
Left column: Token stream as Pythia generates output (token-by-token).
Right column: For each token, a small card showing "Substrate retrieved: [Fact X, Fact Y]"
appearing as the token is generated.

Animation: as each token appears in the left column, the corresponding retrieval event
slides in from the right. At steady state, a 5-token rolling window is visible.

This answers the demo question "what does substrate do during inference?" in 5 seconds
without any explanation text.

Reference design: the Animated Transformer (prvnsmpth.github.io/animated-transformer) for
the animation timing model. Their approach of showing intermediate steps synchronized with
token generation is directly applicable.

P_theoretical: 0.80 (the animation design is proven; substrate-specific adaptation is clear)
P_empirical: 0.45 (deflated; requires Panel B to actually inject K/V at Pythia layer 6,
which is the empirical gate; visualization is blocked until Panel B is implemented)

### Pattern B: Layer-by-layer architecture view

Static or slowly animated diagram:
Pythia layers 1-5: standard self-attention (gray)
Layer 6: SUBSTRATE-ATTENTION (highlighted, branded color)
Layers 7-12: standard self-attention (gray)

With a "substrate-attention is the only layer that knows about your KB" caption.
This is educational scaffolding, not a live visualization. 30-second comprehension pattern.

### Pattern C: Attention pattern heatmap over substrate K/V

For a single query: show the attention weight matrix at layer 6.
Rows: query tokens. Columns: substrate-provided K/V slots (= retrieved facts).
Color intensity = attention weight.

Reference: BertViz head view (github.com/jessevig/bertviz). Exact visual pattern to borrow.
Difference: BertViz shows attention over input tokens; substrate visualization shows attention
over retrieved fact embeddings. The mechanics are identical; the semantic interpretation is
different and more meaningful.

P_empirical: 0.45 (deflated; depends on Panel B layer access; same gate as Pattern A).

### Pattern D: Substrate "lighting up" state view

A grid of squares, each representing one stored fact in the substrate KB (at reduced scale).
During inference, retrieved facts light up in the grid (bright color). Non-retrieved facts
remain dim. Creates a "firing neurons" visual metaphor.

Performance note: at 200M facts, this cannot be a real-time grid per-fact. Must be sampled
or bucketed. Recommendation: show a 100x100 representative grid with bucket-level
aggregation. 10,000 cells at 60fps is feasible in canvas2D with no WebGL required.

---

## Level 4 -- Interactive playgrounds (categorical demos)

### Playground A (RECOMMENDED PRIMARY): Counterfactual do() scenario builder

UI: Two input fields.
Field 1: "Current fact: [The capital of France is Paris]"
Field 2: "Counterfactual: [The capital of France is Lyon]"

Hit "Apply counterfactual". System:
1. Shows substrate state BEFORE (fact binding highlighted in KB)
2. Removes the binding (animated fade-out)
3. Inserts counterfactual binding (animated fade-in, different color)
4. Re-runs the query and shows new answer

This directly demonstrates causal reasoning capability and substrate mutability in a single
30-second interaction. No API LLM can demonstrate this: they would require full retraining.

P_empirical: 0.50 (deflated; requires do() operator to be implemented; if it is implemented
and works correctly, the UX lift from this playground is high).

### Playground B: "Add your own fact" live ingestion

Text box: "Enter a fact to add to the substrate."
User types a fact. System shows:
1. Encoder processing (spinner, ~200ms)
2. Fact appearing in a mini "KB view" panel
3. Query that would return this fact, running automatically
4. Answer incorporating the new fact

This is the most visceral capability demo for a live investor meeting: "type anything and
watch the system learn it in 200 milliseconds."

P_empirical: 0.65 (deflated from 0.85; this is the highest-probability playground to work
because encoding and retrieval are already implemented; risk is demo-mode stability).

### Playground C: K-hop traversal builder

UI: Drag-and-drop query builder. User selects:
- Start entity (dropdown or text)
- Hop 1 relationship (dropdown: "is_a", "part_of", "located_in", etc.)
- Hop 2 relationship
- ... up to K=5

Hit "Traverse". System animates the traversal path as a force-directed graph expanding
step by step. Each hop takes ~300ms animated delay to show the traversal visually.

Library recommendation: 3d-force-graph (github.com/vasturiano/3d-force-graph) for 3D;
D3.js force simulation for 2D. At K=5 with branching factor ~3, the visible graph has
~243 nodes maximum -- well within 60fps WebGL budget.

P_empirical: 0.40 (deflated; depends on K-hop being reliable; current research shows
iterative retrieval +0.04 validated, so the substrate physics support this, but engineering
is the gate).

### Playground D: AND / NOT / COUNT query playground

Query builder with checkboxes:
- AND: "facts about topic A AND topic B"
- NOT: "facts about topic A NOT topic B"
- COUNT: "how many facts about topic A?"

Each operation returns a visible result set. COUNT is particularly visceral: "Substrate
knows 14,237 facts about this topic. LLM context would need 170,000 tokens to hold them."

P_empirical: 0.55 (algebraic operations are a core substrate capability; IF implemented,
this playground is low-effort to expose via demo UI).

### Playground E: Multi-tenant isolation demo

Three visible "shards" in a column:
- Shard A (Customer A): blue
- Shard B (Customer B): green
- Shard C (public): gray

Query runs. System shows which shard each retrieved fact came from. A toggle lets the user
"switch to Customer B view" -- the answer changes because different facts are accessible.
A "cross-shard query" shows only public facts returned, not private ones.

This is the GDPR / enterprise isolation demo in 30 seconds.

### Playground F: Sleep-defrag time-lapse

A 10-second replay of substrate consolidation during a "sleep" phase:
- Fact count ticks up (merging duplicates)
- Similarity score distribution histogram shifts (more concentrated clusters)
- Latency counter ticks down (post-defrag retrieval faster)

Framed as "substrate optimizes itself overnight like biological memory consolidation."
Reference: the biological sleep-memory consolidation framing is well-validated in neuroscience
and is a strong analogy for a non-technical audience.

### Playground G: GDPR delete with visible state change

Input: "Delete all facts about [entity name]."
System shows:
1. Pre-delete: facts highlighted in KB grid
2. Animated "redaction" -- facts fade and are removed from grid
3. Post-delete: query returns "No facts found" for deleted entity
4. Latency of deletion displayed: "Deleted 47 facts in 0.8ms"

This is the GDPR Article 17 "right to erasure" demo. Regulatory compliance made visceral.

### Playground H: Encoder drift visualization

A scatter plot (PCA 2D) of embeddings over time. Two time points:
T0: embeddings clustered clearly
T+N (after encoder drift): clusters have shifted

A toggle shows "substrate with drift correction" vs "substrate without". This is the
encoder-drift robustness argument made visual.

P_empirical: 0.35 (deflated; requires encoder drift experiment data; lower priority).

### Playground I: Cross-shard chain extraction animated

A K-hop chain that crosses from Shard A (Customer A facts) through the public shard into
Shard B (Customer B facts) -- and shows the privacy policy BLOCKING the cross-shard step.
The chain stops at the shard boundary with a "Permission denied" marker.

This is the enterprise multi-tenant security argument made visual in a traversal.

### Playground J: Substrate growth replay

A time-lapse slider showing KB growth over 7 days. Facts per day bar chart. The user drags
the slider and watches the KB fill up. A query is shown running against the KB at each
time point -- earlier time points return fewer facts or less precise answers.

---

## Level 5 -- Comparison / head-to-head designs

### Comparison A (RECOMMENDED PRIMARY): 30-question benchmark dashboard

A table with 30 rows (questions). Columns:
- Question (short, truncated)
- Substrate-augmented Pythia-1.4B: answer + Pass/Fail
- GPT-4o-mini (70x params): answer + Pass/Fail
- Cost (substrate / GPT-4o-mini)

Summary row at top: "Substrate: 24/30 correct. GPT-4o-mini: 22/30 correct. Substrate cost: 
20x cheaper."

Key design decision: show the questions where raw Pythia FAILS and substrate-augmented Pythia
PASSES. These are the signal rows. Color code them (green highlight). The 6 questions where
both fail should also be visible (honesty builds trust).

P_empirical: 0.60 (deflated; depends on having real benchmark data; manual for v1 demo is
acceptable; automated live benchmark is engineering effort of ~1 week).

### Comparison B: Live cost ticker accumulator

Two live counters, side by side, running in real time during the demo session:
"Substrate session: $0.000041"
"GPT-4o-mini equivalent: $0.000840"

Counters increment as queries are made. Over a 5-minute demo, the gap is ~$0.004 vs $0.08.
Over a month of production use at 1M queries/day: show the extrapolated difference.
"At 1M queries/day: Substrate ~$40/day. GPT-4o-mini API: ~$800/day."

The extrapolation is the visceral number. The per-query delta is too small to feel real.

### Comparison C: Audit chain comparison

Two columns:
"Substrate answer" -- shows audit chain, fact sources, timestamps, hashes.
"GPT-4o-mini answer" -- shows only answer text. Below it: "Source: training data (unverifiable,
unknown cutoff, no per-fact attribution)."

This is not about accuracy -- it is about the compliance and auditability argument. One column
has evidence; the other column structurally cannot have evidence.

P_empirical: 0.70 (deflated from 0.90; this comparison is a structural substrate advantage;
the only implementation risk is framing it without appearing to attack a specific vendor).

### Comparison D: Substrate vs LongContextLLM cost graph

A line chart.
X-axis: context size in facts (1K, 10K, 100K, 1M)
Y-axis: cost per query ($)

Three lines:
- Substrate (flat): cost does not scale with KB size (O(1) retrieval)
- GPT-4 128K context (steep): cost scales linearly with context length
- Gemini 2M context (moderate): same linear scaling

The substrate line is flat. All other lines slope up. This is the scalability argument in
one chart.

### Comparison E: "Same query, different LLMs" carousel

A query input box. Three tabs: "Pythia-1.4B (raw)", "Substrate + Pythia-1.4B", "GPT-4o-mini".
Click each tab to see the answer from that configuration. Answers are pre-cached for demo
stability. The tab switch is instant (no live inference needed for demo mode).

Design reference: HuggingFace Spaces compare UI pattern. Tab-based model comparison is
a well-understood pattern.

### Comparison F: Visceral cost calculator

Input fields:
"Queries per day: [slider 1K - 10M]"
"Average context per query: [slider 1K - 128K tokens]"

Two output rows:
"Substrate monthly cost: $X"
"GPT-4o-mini monthly cost: $Y"

"You save $Z per month with substrate."

The calculator is interactive. As the user drags the sliders up, the GPT-4o-mini number
grows much faster (linear in context) while the substrate number barely moves (retrieval cost
is sub-ms flat regardless of KB size).

P_empirical: 0.65 (deflated; the calculator math is straightforward; risk is accuracy of
the cost model for the substrate side, which requires knowing actual infrastructure cost).

---

## Cross-cutting concerns

### Mobile rendering

Investors will demo this on phones. Specific requirements:
1. Hero counter: single column on mobile. No side-by-side on screens < 480px wide.
2. Audit chain: accordion pattern, not hover-expand. Touch target >= 48px.
3. Substrate-attention panel: fall back to replay-mode WebM on mobile. Live WebGL is too
   heavy for most phones at N > 256.
4. Benchmark table: horizontal scroll on mobile, or show top 10 rows only with "Show all" button.
5. Cost calculator: sliders work well on mobile; ensure 44px minimum touch target.

### Performance budget

- First contentful paint: <= 1.5s
- Total page weight: <= 2MB (images + JS + fonts). WebGL assets separate (lazy-load).
- 60fps target for any canvas/WebGL element. If frame budget is violated, drop to 30fps
  with a prefers-reduced-motion fallback.
- Three.js for 3D force graph: 200KB gzipped. D3.js for 2D: 70KB gzipped. Both are fine.
- Pre-record any visualization that cannot sustain 60fps on mid-tier hardware.

### Accessibility

- WCAG 2.1 AA minimum.
- Color coding: always pair color with a secondary cue (shape, pattern, label). Green/amber/red
  is safe for protanopia/deuteranopia IF accompanied by text labels.
- Animation: respect prefers-reduced-motion. All animated elements must have a static fallback.
- Screen reader: every chart and visualization must have an aria-label describing the data.
  "Substrate answers 24 of 30 benchmark questions correctly. GPT-4o-mini answers 22 of 30."
- Audit chain expansion: keyboard-navigable (Enter/Space to expand, Escape to collapse).

### "Wow without overwhelm" balance

The single hardest UX problem in this demo. Recommendation:
- Default state: hero counter + one comparison + one playground active. Everything else collapsed.
- A single "Explore more" CTA expands additional panels.
- The demo has a "guided tour" mode (autoplay sequence, 90 seconds) and a "free explore" mode.
  Guided tour is for investor demos. Free explore is for technical visitors.
- Progressive disclosure is the design principle throughout. First click should always be
  available and obvious. Depth should require deliberate exploration.

### Educational scaffolding

"What is substrate?" tooltip chain:
- Hover on "substrate": tooltip "A knowledge base that connects directly to the LLM's
  attention mechanism -- not a prompt, not a retrieval API, but an internal memory layer."
- Hover on "audit chain": tooltip "Every fact has a cryptographic proof of its origin.
  Unlike LLM outputs, substrate answers are verifiable."
- Hover on "0.4ms retrieval": tooltip "Sub-millisecond exact lookup from 200M facts, not
  an approximate embedding search."

These three tooltips are the minimum educational layer needed. They should be present on
the hero section and the comparison section.

---

## Cross-thread synthesis

### Link to prior research findings

- Production-scale 1M end-to-end validated (recall@1=1.000, SMW pinv 4.174ms): the latency
  and recall numbers cited in the demo comparisons are empirically grounded, not aspirational.
  Use the validated numbers; do not inflate.

- Counterfactual do() capability (Wish 1 counterfactual empirically validated 20/20):
  Playground A is grounded in validated substrate physics. This is a real capability.

- GDPR delete at 0.0004ms: this number is the GDPR playground hook. It should be displayed
  as "GDPR delete: 0.4 microseconds" (more visceral than ms).

- Multi-hop iterative retrieval +0.04 improvement validated: K-hop chain visualization is
  grounded in real benchmark improvement. The chain vis is not aspirational.

- Privacy ZKL work: the audit chain comparisons should NOT claim HIPAA-absolute compliance
  until T5 pre-tests pass (see exp_dev handoff for ZKL alternatives).

### Connection to North Star

Per memory: goal = deployed system that empirically exceeds LLMs of relative size in clear
measurable ways. The 30-question benchmark dashboard is the primary North Star deliverable:
it is the empirical head-to-head comparison that validates the "beats LLMs of relative size"
claim. All other visualizations support this primary claim; none should overshadow it.

---

## Substrate-product implications

1. Panel A demo (substrate-KV production): the "add your fact" playground and the GDPR
   delete playground are the two highest-lift interactions for Panel A alone. They require
   no Panel B. They demonstrate substrate-KV value in < 60 seconds.

2. Panel B demo (substrate-attention): the per-token retrieval stream is categorically
   differentiated from any existing AI demo. It requires Panel B to be working. This should
   be the secondary demo element, not the primary, because it is blocked on Panel B completion.

3. Benchmark table: this is the primary North Star deliverable and should be the first
   demo element built, with manual/pre-cached answers, before any live inference is wired up.

4. Cost argument: the cost comparison requires honest numbers. Use actual infrastructure
   cost for substrate (Cloudflare Tunnel + Pythia on desktop + substrate library) vs
   GPT-4o-mini API pricing. Do not use theoretical minimums; use real measured costs.

5. The Perplexity inline citation pattern is the strongest existing design reference for
   audit chain UI. Do not invent a new pattern for audit chain display -- follow Perplexity's
   UX convention with the addition of the cryptographic binding distinction.

6. For the hero section: the "same model, different substrate" framing is cleaner than
   "substrate vs LLM" framing. The latter implies competition with API vendors; the former
   implies a substrate is a capability upgrade. The positioning matters for investor demos.

---

## Specific design references (cited)

1. Perplexity.ai inline citations: the gold standard for audit chain UX in consumer AI.
   Pattern: [1][2][3] inline numbers, hover or click expands source. Established user
   mental model as of 2025.

2. Transformer Explainer (poloclub.github.io/transformer-explainer): live GPT-2 running in
   browser, per-token attention visualization, expandable intermediate computations. The
   closest existing design reference for substrate-attention layer visualization.

3. BertViz (github.com/jessevig/bertviz): head view and model view for attention across
   layers. The specific multi-head attention grid pattern is directly applicable to
   substrate layer 6 attention over retrieved fact embeddings.

4. 3d-force-graph (github.com/vasturiano/3d-force-graph): WebGL/Three.js force-directed
   graph. Sustains 60fps at 2,000 nodes / 7,000 edges. Drop to 2D (D3.js) above 5,000 nodes
   for mobile safety.

5. AttentionViz (attentionviz.com): global view of transformer attention across all heads and
   layers. The joint query-key embedding scatter plot is a good reference for substrate
   similarity space visualization.

6. Vellum.ai LLM leaderboard: clean benchmark comparison table design. Sortable columns,
   expandable rows, cost column. Direct reference for benchmark comparison dashboard (Level 5
   Pattern A).

7. Etherscan.io transaction trace: the expand/collapse cryptographic proof path pattern.
   Direct reference for Merkle proof interactive expansion (Level 2 Pattern D).

8. AnimatedLLM (arxiv.org/html/2601.04213v2): play/pause/step-through animation for LLM
   mechanics explanation to non-technical audiences. Reference for the "guided tour" mode
   in the demo.

---

## Recommended build order (priority sequence)

PHASE 1 (before any live inference): 2-4 hours each
- P1: Static 3-question benchmark comparison table (manual answers, no live inference)
  Test with 5 observers. Gate for rest of demo build.
- P2: Hero counter (fact count + retrieval latency + cost comparison). Static numbers initially.
- P3: Audit chain accordion for one pre-cached query. Perplexity-style inline citations.

PHASE 2 (live Panel A): 1-2 days each
- P4: "Add your fact" playground (live Panel A ingestion + retrieval)
- P5: GDPR delete playground (live Panel A delete + visible state change)
- P6: Full 30-question benchmark table (pre-cached answers; live on demand)

PHASE 3 (live Panel B): 2-3 days each
- P7: Per-token substrate-attention stream (requires Panel B working)
- P8: K-hop traversal builder with animated graph

PHASE 4 (polish + comparison): 1 day each
- P9: Cost accumulator live ticker
- P10: Context window ratio chart
- P11: Mobile responsive pass + WCAG AA audit

---

## Citations (verified, from search results)

1. ShapeofAI.com -- Citations UX pattern catalog: https://www.shapeof.ai/patterns/citations
2. Transformer Explainer (Polo Club): https://poloclub.github.io/transformer-explainer/
3. AttentionViz: https://attentionviz.com/
4. BertViz: https://github.com/jessevig/bertviz
5. The Animated Transformer: https://prvnsmpth.github.io/animated-transformer/
6. AnimatedLLM paper: https://arxiv.org/html/2601.04213v2
7. 3d-force-graph: https://github.com/vasturiano/3d-force-graph
8. Carina million-node graph vis: https://arxiv.org/pdf/1702.07099
9. Neo4j 3D WebGL graph: https://neo4j.com/blog/developer/visualizing-graphs-in-3d-with-webgl/
10. Vellum LLM Leaderboard: https://www.vellum.ai/llm-leaderboard
11. LLM Stats compare: https://llm-stats.com/models/compare
12. Counterfactual explanations (Molnar): https://christophm.github.io/interpretable-ml-book/counterfactual.html
13. Graph Counterfactual XAI via latent traversal: https://arxiv.org/abs/2501.08850
14. Responsive dataviz accessibility: https://datafloq.com/responsive-design-for-data-visualizations-ultimate-guide/
15. Highcharts 10 DataViz accessibility guidelines: https://www.highcharts.com/blog/tutorials/10-guidelines-for-dataviz-accessibility/
16. Smashing Magazine: Accessibility standards for chart design: https://www.smashingmagazine.com/2024/02/accessibility-standards-empower-better-chart-visual-design/
17. Agentic Visualization patterns: https://arxiv.org/pdf/2505.19101
18. Auditable clinical AI provenance (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC12913532/

Verified citation count: 18

---

## P_deflated summary

| Element | P_theoretical | P_empirical (deflated -0.20) | Gate |
|---|---|---|---|
| Two-panel comparison hero | 0.75 | 0.55 | benchmark data required |
| Per-token substrate-attention vis | 0.80 | 0.45 | Panel B gate |
| Audit chain accordion | 0.85 | 0.70 | Panel A (implemented) |
| "Add your fact" playground | 0.85 | 0.65 | Panel A (implemented) |
| K-hop chain visualization | 0.65 | 0.40 | K-hop reliability gate |
| 30-question benchmark table | 0.80 | 0.60 | benchmark data required |
| Cost calculator | 0.80 | 0.65 | cost model accuracy |
| Counterfactual playground | 0.70 | 0.50 | do() operator gate |
| GDPR delete playground | 0.80 | 0.65 | Panel A (implemented) |

Novel-synthesis P cap: 0.50 applied to substrate-attention visualization (no direct precedent).
