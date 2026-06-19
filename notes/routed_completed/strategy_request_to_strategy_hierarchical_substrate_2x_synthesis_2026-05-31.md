# Strategy request: hierarchical substrate architecture 2x synthesis (3 drills; substantially rescoped from doc's 6-experiment program)

## Trigger: research 2x deep drill 2026-05-31 (3 parallel Sonnet drills synthesized)

Origin: user 2026-05-31 -- shared hierarchical substrate proposal ("galaxy of substrates" architecture); meta-substrate stores leaf shards as facts; 6 proposed experiments (H-1 through H-6) over 3-4 months. Per [[feedback-2x-means-depth]] = operational depth on prerequisites. Full audit at `notes/research_continuous_embedding_storage_audit_v1_2026-05-31.md` (sibling for continuous-embedding).

## Finding (one paragraph)

The hierarchical substrate architecture is architecturally interesting but **not strategically superior to single-big-N within the 12-month horizon** (drill B P_def 0.18). The doc's 6-experiment program is overscoped for the strategic value it can deliver at this stage; honest re-scoping reduces to 1-2 lightweight smokes + a cheaper alternative path (BF16 single-substrate at N=32K-65K). Specific findings from 3 drills:

- **Drill A (meta-storage scheme)**: Scheme A (pointer atom) recommended; clean algebra, full moat preservation, 26-262x capacity advantage under CLEAN domain partition, 5-15x under messy partition. P_def 0.40 for ≥5x effective capacity advantage at equivalent engineering effort.
- **Drill B (latency + single-big-N comparison)**: hierarchy wins 1.5 of 4 matched-parameter criteria; HARD-PASS NOT MET. Modern hardware kills "too big to fit" argument (BF16 N=65K = 8.6GB fits H100). Hierarchy strategically superior only when (capacity >500K + per-token-latency ≤20ms + multi-tenancy) hold simultaneously -- a regime that's 24-36 months out per substrate-strategic-inversion window, NOT 12-month. P_def 0.18 for "hierarchy strategically superior in 12-month horizon."
- **Drill C (cross-shard composition)**: Mechanism 2 (sequential multi-hop with LLM bridge) is the only substrate-deployable cross-shard composition; v282 Op E second-order closure EXCLUDES Mechanisms 3 + 4. Mechanism 2 is structurally equivalent to substrate-LLM build's Rescue C extended across shard boundaries -- NOT a fundamentally new architecture. P_def 0.35-0.42 for Mechanism 2 within 15pp of single-shard baseline.

**The strongest hierarchy advantage that survived audit**: operational isolation (independent audit/delete per shard, multi-tenancy), NOT raw capacity (which depends on knowledge-partition cleanness AND degrades under messy real-domain partitioning).

## Recommended action

**1. Cap_map: ONE NEW row at narrower P-band than doc proposed.**

Row name: "Hierarchical substrate via Scheme A pointer routing (multi-tenant operational isolation)"

Initial P-band: 0.30-0.45 (range reflects capacity advantage of 5-15x messy-partition / 26-262x clean-partition + drill A P_def 0.40)

Caveats:
- Within 12-month horizon, single-big-N + BF16 is competitive on ALL strategic criteria except multi-tenancy / domain isolation
- Cross-shard composition reduces to Mechanism 2 (Rescue-C extended); not architecturally novel beyond Phase 1 build
- Capacity advantage real only under clean domain partition; degrades to 5-15x under messy real-domain knowledge
- v282 Op E closure rules out Mechanisms 3+4; first-order Scheme A/B viable

**2. Three experiments to dispatch (rescoped from doc's 6).**

### H-1-LITE: Meta-substrate Scheme A pointer routing smoke (~1 week NOT 2-3 weeks)

**Anchor**: `hierarchical_substrate_h1_scheme_a_routing_smoke_v1_n16384`

**Spec sketch**:
- Build minimal 2-level: meta-substrate at N=16384 + S=100 synthetic leaf shards (each at N=4096 storing K=1000 synthetic atoms)
- Leaf shard codebooks: drawn independently with quasi-orthogonal domain_descriptor codewords
- Meta-substrate stores (domain_descriptor, shard_id) bipolar pairs
- Query: 1000 queries per shard, uniformly drawn from leaf key distributions
- Measure: top-1 recall@1, top-5 recall@5, routing latency, audit-trace completeness

**Pre-reg HARD-PASS** (per drill A):
- Top-1 recall@1 ≥ 0.97 at S=100
- Top-5 recall@5 ≥ 0.999 at S=100
- Routing latency ≤ 2× single-leaf query latency
- Algebraic audit decomposition exact for 100% of stored entries

**Pre-reg HARD-FAIL**: top-1 < 0.90 at S=100 → Scheme A doesn't scale to modest shard counts; hierarchy direction substantially limited

**Pre-reg MIDDLE-BAND**: top-1 in [0.90, 0.97); triggers either Gram-Schmidt orthogonalization of domain codewords (rescue) or upgrade to Scheme B aggregate-embedding

**Cost**: ~1 week + ~30min CPU. Local 8GB sufficient. NO cloud spend.

### Alt-Experiment: BF16 single-substrate capacity probe at N=32K-65K (~1 week)

**Anchor**: `single_big_n_bf16_capacity_probe_v1_n32K_n65K`

**Spec sketch** (alternative to full hierarchy; tests the drill B finding that single-big-N may match hierarchy at 12-month horizon):
- Modern Hopfield activation regime at N=32K and N=65K at BF16 precision
- Measure: max_M sustained recall=1.0 at each N
- Compare to validated N=16K max_M=16N=262K envelope
- Predict whether single-big-N at N=65K can reach ~1M patterns (matching hierarchy's 100×10K leaf claim)

**Pre-reg HARD-PASS**:
- N=32K reaches max_M ≥ 16N = 524K
- N=65K reaches max_M ≥ 8N = 524K (more conservative scaling)
- BF16 retrieval accuracy within 2pp of fp32 baseline

**Pre-reg HARD-FAIL**: max_M at N=32K < 4N (Modern Hopfield activation regime doesn't extend); single-big-N capacity scaling story breaks

**Cost**: ~1 week + ~2-4h GPU. Local 8GB GPU sufficient with BF16 (~2GB for N=32K matrix, ~8GB for N=65K matrix; tight on 8GB at N=65K, easy on 24GB). NO cloud spend.

**Strategic value**: HIGHER than H-1-LITE because it tests the question of whether hierarchy is even necessary. If single-big-N at N=65K supports ~1M patterns at acceptable retrieval quality, the case for hierarchy collapses except for multi-tenancy.

### H-6 (multi-tenant pilot): defer to pilot deployment scoping

The doc's H-6 (multi-tenant hierarchy) tests the strongest unique-to-hierarchy advantage (operational isolation, per-customer audit/delete). This isn't a research experiment -- it's a pilot-deployment design question. Defer until a regulated-industry pilot customer is identified.

**3. REJECT 4 of 6 proposed experiments (with cross-refs).**

| Proposed | Why rejected |
|---|---|
| **H-2** cross-shard composition | Mechanism 2 = Rescue C extended across shards; structurally same pattern as substrate-LLM Phase 1 build + reasoning storage Phase 1 + Mechanism 2 from drill C. Test via existing infrastructure when Phase 1 evidence lands. |
| **H-3** domain specialization benefits | Cheaper version: BF16 single-substrate capacity probe (filed above) tests whether single-big-N matches multi-leaf-specialized capacity. If single-big-N suffices, specialization benefits are second-order. |
| **H-4** 3-level hierarchy scaling | Defer to Phase 3+ ambition. At 100×100×10K = 100M facts, GPU footprint = 4TB = multi-machine. Out of scope for 12-month horizon. |
| **H-5** edit isolation across hierarchy | T2 already validated edit isolation at bipolar atom level (45/45 cells unanimous v290 cap_map). Shard-level adds routing layer; if H-1-LITE routing passes, shard-level edit isolation inherits. No separate experiment needed. |

**4. Document explicit crossover criteria** for when hierarchy becomes worth revisiting:

Hierarchy is worth Phase 2+ investment when ALL THREE hold:
- (a) Capacity demand > 500K patterns (current product positioning is 100K-50K scale; not yet)
- (b) Per-token latency budget ≤ 20ms (substrate-LLM Phase 1 will measure this; pending Week 0 Missing 7 verdict)
- (c) Multi-tenancy / domain isolation is an explicit product requirement (depends on pilot deployment scoping)

Until at least 2 of 3 hold, single-big-N + amortized prefetch is the strategically right path.

**5. Honest product reframing for cap_map + go-to-market.**

REPLACE the doc's strategic framing:
- Doc said: "Galaxy of substrates with multiplicative capacity scaling" / "Approaching LLM-scale coverage"
- Honest: "**Single-big-N substrate is the 12-month strategic path. Hierarchical extension is a Phase 2+ ambition contingent on capacity demand >500K + multi-tenancy requirements; deferred with explicit crossover criteria.**"

The product moat that ACTUALLY differentiates substrate (across all the morning's research):
- Real-time learning during inference (validated v191 ✅; survives projection intact)
- Algebraic audit via element-wise unbinding (validated; degrades to projection layer with sha256 side-data mitigation)
- Edit isolation for semantically distinct keys (validated T2)
- Cryptographic deletion certificates (validated)
- ~10-20x retrieval speed vs FAISS via XOR-popcount
- 1.5x storage compactness vs FAISS fp32

These DON'T require hierarchy. They're already validated for single-substrate at N=16384.

## Confidence

P_deflated for each component:
- **Scheme A pointer routing PASSes at S=100 (H-1-LITE)**: 0.65-0.75 (drill A) -- routing math is clean; random bipolar codewords are quasi-orthogonal at N=16384
- **Single-big-N at N=32K BF16 reaches ≥16N capacity (alt-experiment)**: 0.55-0.70 -- Modern Hopfield activation regime validated to N=16384; extrapolation to N=32K is one envelope-jump
- **Hierarchy strategically superior to single-big-N within 12-month horizon**: 0.18 (drill B)
- **Hierarchy strategically superior at Phase 3+ horizon (24-36 months)**: 0.55-0.70 (capacity demand grows; multi-tenancy emerges; pilot deployment matures)
- **Mechanism 2 cross-shard composition works**: 0.35-0.42 (drill C; depends on inter-hop LLM reformulation reliability)
- **Joint: hierarchical-substrate as filed (H-1-LITE + alt-experiment + deferred H-6)**: 0.35-0.50 for at least one HARD-PASS that informs cap_map row movement; ~0.15-0.25 for HARD-FAIL across all bands

## Critical open empirical risks (carried forward; don't pretend resolved)

1. **Knowledge-partition cleanness in real domains**: drill A's 26-262x capacity advantage assumes clean partition. Real-domain knowledge (medical English vs medical French vs medical engineering) overlaps. Effective hierarchy gain in realistic deployments may be 5-15x not 100x.
2. **BF16 retrieval accuracy degradation**: drill B flagged BF16 as the key enabler for single-big-N viability but accuracy preservation at BF16 hasn't been measured. Alt-experiment tests this directly.
3. **Modern Hopfield extrapolation to N=32K and N=65K**: not validated; we've tested to N=16K. Extrapolation may be optimistic.
4. **Mechanism 2 inter-hop LLM reformulation reliability**: drill C's load-bearing fragility point. Same risk as substrate-LLM Phase 1 build's Rescue C reasoning chain construction.
5. **Routing error propagation in multi-level hierarchy**: drill A flagged that 3-level hierarchy compounds routing error multiplicatively. Even modest per-level error (5%) gives 14% top-level error at 3 levels; multi-level may not scale as cleanly as the doc claimed.

## Files of interest

- `notes/research_continuous_embedding_storage_audit_v1_2026-05-31.md` (sibling audit for continuous-embedding direction; same author + same drill pattern)
- Drill A return: Scheme A pointer atom recommended; Scheme B not closed by v282 (first-order vs second-order); Scheme C complement-not-replacement; P_def 0.40 for ≥5x effective capacity advantage
- Drill B return: HARD-PASS NOT MET at matched parameter count; modern hardware kills "too big to fit"; amortized prefetch alternative; P_def 0.18 for hierarchy strategically superior in 12-month
- Drill C return: Mechanism 2 = Rescue C extended; Mechanisms 3+4 excluded by v282; structurally not novel
- `notes/substrate_capability_map.md` v297 (Modern Hopfield N=16384 validated past 16N; capacity envelope for the single-big-N alt-experiment)
- `notes/substrate_capability_map.md` v282 Op E cross-shard pairwise correlation CLOSED (AUC=0.459)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (Rescue C autonomous Path D = same pattern as cross-shard Mechanism 2)
- `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` (Scheme B reasoning-storage; closely related substrate-physics question)
- Memory: [[feedback-2x-means-depth]], [[feedback-no-padding-experiments]], [[feedback-no-smoke]], [[feedback-substrate-value-framing-matured-2026-05-26]]

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to add the cap_map row at 0.30-0.45 P-band
- (b) Whether to dispatch H-1-LITE (~1 week) + Alt-experiment BF16 single-N (~1 week) in parallel
- (c) Whether to REJECT H-2/H-3/H-4/H-5 explicitly OR leave as documented-deferred
- (d) Whether to DEFER H-6 to pilot deployment scoping
- (e) Whether to ADOPT the honest reframing (single-big-N is 12-month strategic path; hierarchy deferred with crossover criteria)

No engineering work begins without orchestrator queueing.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
