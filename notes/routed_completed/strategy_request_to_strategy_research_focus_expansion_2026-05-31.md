# Strategy request: research focus expansion -- 6 product-positioning drills + cloud-routing discipline

## Trigger: 2026-05-31 user-shared external-Claude evaluation doc; research session evaluated + verified against cap_map + status_log

## Finding (one paragraph)

External evaluation surfaced 6 high-value research drills that close production-positioning gaps the current cap_map portfolio doesn't address. Verification against v290/v291 cap_map + status_log confirmed 6 of 7 originally-proposed drills are genuine gaps (substrate-augmented LLM absolute-quality vs LLM-only baseline; storage efficiency at production scale; audit trail rotation strategy; per-store latency optimization for bursty-write workloads; concept drift detection mechanism; substrate-LLM integration latency-budget characterization). One drill (multi-substrate composition) is conceptually valid but the doc's specific anchor ("K=10 sharding tested with shared codebook") is wrong -- the v282 K=10 reference was a cross-shard pairwise-correlation Op E probe that CLOSED at AUC=0.459 below random; concept needs re-anchoring from scratch. Three specific tactical recommendations in the doc have factual errors and should be DROPPED: (a) Modern Hopfield "reconciliation between testbed envelope max_M=N/2 and G5/G6" -- the N/2 reading was a v288 GPU-OOM instrumentation block, not a mechanism boundary; today's C1 verdict pushed max_M to 4N at N=16384 and the row LIFTed yellow→green; nothing to reconcile; (b) "Pattern B LLM integration prototype" -- "Pattern B" terminology conflates Path B (substrate's geometric-cosine retrieval mechanism) with an undefined LLM-integration framework; reframe as "open-source LLM integration prototype"; (c) "$5 cloud spend at 50% budget" -- the 08:52 cloud event is internally inconsistent ($7.50 of $10 = 75%, not 50%) AND the 08:57 testbed event confirms Lambda hasn't been activated (awaiting user API key); the cloud-cost telemetry appears spurious; flag for telemetry-source audit, not crisis.

## Recommended action

**1. Cap_map portfolio expansion -- 6 new research-only rows (🔬) under a "Production positioning" category.**

| New row | Why it matters | Local-tractable? | Est research budget |
|---|---|---|---|
| Substrate-augmented LLM absolute-quality vs LLM-only baseline | "GPT-quality with auditable memory" claim is currently relative-to-frozen-substrate (bpc 2.198 vs 2.745), NOT absolute vs LLM-only (which hits bpc < 1). Validates the core product positioning. | YES (small open-source LLM 1-3B + Lambada/ARC/HellaSwag subset) | 2-3 weeks engineering + 1-2 weeks research framing drill |
| Storage efficiency at production scale | Cost-of-ownership story. Substrate state + codebook + audit chain + multi-tenant overhead per fact, vs FAISS/Pinecone/Weaviate. Required for production cost modeling. | YES (CPU-bound analysis + small GPU validation) | ~1-2 weeks |
| Audit trail design + rotation strategy | Deletion-cert killer feature is hollow without growth/compression/rotation. Compliance customers need both completeness AND reasonable storage cost. M2 log-structured store (today's drill) provides the substrate. | YES (CPU-bound; V2 24h workload provides input data) | ~2 weeks |
| Concept drift detection mechanism | Listed as Tier-2 killer feature but no research filed. SAME/REPLAY/STAGE4/DIFF shift-class detection from continual-learning internal state. | YES (local GPU, scenarios with known drift) | ~2-3 weeks |
| Substrate-LLM token-throughput latency budget | If substrate ops > LLM token-gen time (typically 10-50ms), substrate is bottleneck. Practical-integration go/no-go. | YES (local GPU, profiling-focused) | ~1-2 weeks |
| Per-store latency optimization for bursty-write workloads | G13 agentic batch covers sustained read-mostly; bursty-write (data import, bulk updates) is open. Determines market reach (read-heavy vs general). | YES (local GPU, store-op profiling + batched-store + GPU acceleration) | ~2-3 weeks |

**2. Cap_map portfolio expansion -- 1 new research row needing re-anchoring (drop the external doc's specific framing).**

| New row | Why | Re-anchoring needed |
|---|---|---|
| Multi-substrate composition at enterprise scale (hierarchical / per-domain / ensemble) | Enterprise architecture fit -- different domains often have different retention/access/audit policies; single-substrate may not match. | DROP the doc's "K=10 sharding tested, K=20-50 in progress" claim (the v282 K=10 reference was the closed Op E cross-shard pairwise correlation probe, AUC=0.459 below random). Re-anchor from scratch: what does enterprise multi-domain substrate composition mean? Start with research drill on hierarchical-substrate / domain-substrate / ensemble-substrate literature before committing to test design. ~30-60 min research drill first; engineering follow-on TBD. |

**3. Tactical drops from the external doc.**

- DROP "Reconcile Modern Hopfield max_M=N/2 vs G5/G6" recommendation. The N/2 reading was v288 GPU-OOM (resolved by CPU path in v290); today's C1 verdict pushed max_M to 4N = 65536 BSC 3-seed unanimous 9/9 cells; v291 LIFTed the row yellow→green (0.75-0.88). Nothing to reconcile. Remaining open caveats per v291: (a) Kerdock cross-codebook at N=16384 still untested, (b) actual ceiling past M=4N untested, (c) cross-N validation of the activation regime untested (single-N at N=16384 for both T3 + C1 anchors). G5/G6 will partially address cross-codebook at N=8192.
- DROP "Pattern B LLM integration" terminology. Cap_map uses Path B exclusively for the geometric-cosine retrieval mechanism. The doc's "Pattern B integration" framing risks executing the wrong thing. Reframe as "open-source LLM integration prototype" without the misleading anchor.
- DROP "$5 cloud spend at 50% budget" as crisis framing. Investigate as **telemetry-source bug**: 08:52 event reports $7.50/10 (75% mathematically, label says 50%) AND 08:57 testbed event confirms Lambda not yet activated. Flag for testbed: is cloud emitting fake telemetry? Is the dashboard surfacing canary-test events as production cost? Worth 15 min to trace.

**4. Cloud-routing discipline (adopt as standing principle).**

Cloud-warranted experiments are EXCEPTIONS, not defaults. The doc's three concrete cloud candidates are valid:
- N=32768 envelope sweep (only if super-linear pattern matters strategically AND local sparse-W/sharding alternatives are insufficient; ~$55-90 cloud H100 if run)
- Open-source LLM integration prototype scaling to production-quality LLMs (e.g., GPT-4 / Claude API at benchmark scale; ~$50-200)
- 7-day sustained workload (only if local 48h validates clean; ~$300-500)

Default routing: LOCAL. The 6 new research rows above are all locally tractable. This represents a ~$1500-2500 cloud spend reduction from prior planning assumptions.

**5. Strategic queue-weighting shift (adopt as ongoing principle).**

The substrate has matured past "validate capabilities" -- per 2026-05-26 substrate-value-framing-matured memory, **PLUMBING is the rate-limiter, not physics**. Queue weight should shift toward:
- Product validation (Missing 1: absolute-quality vs LLM)
- Production-engineering (Missing 2/3/5/7: storage, audit rotation, latency budget, bursty-write)
- Compliance positioning (Missing 3: audit rotation per GDPR/HIPAA/SOC2 retention)

Substrate-physics drills CONTINUE but scoped to closing specific deployment blockers:
- Kerdock cross-codebook at N=16384 (closes last v291 Modern Hopfield caveat)
- Cross-N validation of activation regime (closes another v291 caveat)
- 2x-research on negative results (per [[feedback-negative-results-2x-research]])
- ~24-48h cadence cross-framework probes (per [[feedback-aggressive-cross-domain-research]] -- overdue right now)

## Confidence

P_deflated estimates for the 6 new research-row drills:
- **Substrate-augmented absolute-quality benchmark**: P_def 0.40-0.55 that substrate-augmented is within 20% of LLM-only on standard benchmarks at small-LLM scale (1-3B). Range reflects: open-source LLM availability AND substrate's K-scaling behavior at LLM-relevant K (likely K>>16) NOT directly characterized.
- **Storage efficiency**: P_def 0.65-0.75 that substrate is within 2-5x of dedicated vector DBs at production-realistic operating points after compression. Range reflects: known sparse-W 16x compression + Modern Hopfield super-linear capacity vs un-tested codebook compression + audit-chain growth.
- **Audit trail rotation**: P_def 0.55-0.70 that a defensible rotation strategy emerges with GDPR-compliant retention. Lit precedent strong (LSM compaction + transparent log certificate-rotation); novel-synthesis is the substrate-specific replay semantics.
- **Concept drift detection**: P_def 0.40-0.55. Listed as killer feature but mechanism is speculative; substrate's continual-learning state COULD distinguish shift-classes but no direct empirical evidence yet.
- **LLM-integration latency budget**: P_def 0.55-0.70 that substrate ops can be made fast enough for token-level integration with batching + GPU. Current single-store at N=16384 ~530us is borderline at 10-50ms token windows; batching gets you there asymptotically.
- **Per-store latency for bursty writes**: P_def 0.55-0.70 that batched-store + GPU acceleration hits ~10x throughput at N=4096-8192. Standard engineering.

Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.10-0.20 across all 6 (most are local empirical, not external lit-scan synthesis; lower penalty than pure-novel-synthesis lit-scans).

## Files of interest

- This routing file (the recommendation package)
- `notes/substrate_capability_map.md` v290 (lines 19872-19878 = v288 GPU-OOM context; lines 20067-20077 = v290 T3 honest reading; lines 20236-20324 = v291 Modern Hopfield LIFT after C1)
- `notes/research_alt_edit_isolation_v1_2026-05-31.md` (this morning's drill; M1+M2 log-structured store IS the substrate for audit-trail rotation drill)
- `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` (yesterday's drill; D1+D2+D3 defenses contribute to compliance positioning)
- `data/orchestrator_status_log.jsonl` 08:52 cloud event (telemetry-source bug to verify) + 08:57 testbed event (Lambda not yet activated, awaiting API key)
- Memory: `project_substrate_killer_features_2026-05-26.md`, `project_substrate_strategic_inversion_48h_2026-05-26.md`, `feedback_capabilities_mapping_not_competitive_analysis`, `feedback_periodic_scope_expansion`, `feedback_aggressive_cross-domain-research`, `feedback_substrate_value_framing_2026-05-26`

## Sequencing recommendation (not auto-dispatched; orchestrator decides)

**Immediate (this week, while still pause-gated if applicable):**
- Compositionality-audit-API research drill (~30-60 min; mentioned but never filed)
- Cross-framework probe (overdue per ~24-48h cadence; percolation / sparse-coding NTK / free-probability candidates)
- Telemetry-source audit on the 08:52 cloud event (~15 min testbed task)

**Near-term (1-2 weeks):**
- LLM-integration latency budget characterization (Missing 7) -- cheapest, smallest scope, gates everything LLM-integration-flavored
- Storage efficiency at production scale (Missing 2) -- CPU-bound analysis, independent of queue state
- Audit trail rotation strategy (Missing 3) -- builds on today's M1+M2 alt-edit-isolation drill + V2 24h workload output

**Medium-term (3-6 weeks):**
- Substrate-augmented absolute-quality benchmark (Missing 1) -- highest-leverage product test, longest engineering scope; the load-bearing item
- Per-store latency optimization for bursty writes (Missing 5)
- Concept drift detection mechanism (Missing 6)

**Longer-term + re-anchoring required:**
- Multi-substrate composition -- 30-60 min re-anchoring research drill first; engineering scope TBD after that
- Kerdock cross-codebook at N=16384 (closes last v291 Modern Hopfield caveat; cap_map row could move 0.75-0.88 → 0.80-0.92 if Kerdock anchors clean)

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides queue weights and dispatch timing (pause-gated for any exp_dev work; research drills allowed while paused).
