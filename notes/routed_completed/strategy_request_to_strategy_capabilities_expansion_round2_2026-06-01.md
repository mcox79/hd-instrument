# Strategy request: capabilities expansion Round 2 follow-on (9-drill consolidated routing)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` (full 9-drill synthesis)
**Trigger**: User-greenlit Round 2 expansion ("sonnet is cheap for us - dispatch for all of them") covering capability gaps not addressed in Round 1

## TL;DR

9-drill Round 2 produced a CONVERGENT strategic finding across 3 independent capability axes: **"physics-grade not policy-grade"** is the substrate's defensible moat. Multi-tenant isolation, differential privacy, AND disaster recovery all express this same architectural property in different domains. Bundling them as ONE positioning (audit-grade-memory-with-physics-grade-guarantees) is more defensible than 3 separate features.

Plus 6 secondary findings (workflow engine as audit layer not replacement, time-series as 2-tier with TimescaleDB, ensemble Config 5 cascading viable, long-tail is PP-10a sub-property, CF has K_crit~√N theory, streaming fits SMB-Enterprise on reads).

**4 NEW cap_map rows proposed**; **2 sub-properties to existing rows**; **2 directions explicitly close-recommended**.

## CONVERGENT FINDING: bundle physics-grade positioning

Three drills independently arrive at the same moat:

| Domain | Substrate property | Competitor offers | Substrate advantage |
|---|---|---|---|
| Multi-tenant isolation | Per-tenant W mathematical zero-leak | API-scoped policy isolation | Math vs policy |
| Differential privacy | Write-time algebraic noise; dual-cert (audit + ε,δ) | Query-time policy-enforced noise | Intrinsic vs bolt-on |
| Disaster recovery | Cert-chain replay cryptographic verifiability | Operationally-trusted pg_restore | Crypto-verifiable vs trust-required |

**Strategic recommendation**: bundle these into ONE killer-feature positioning, not three. Cap_map row LIFT proposed accordingly.

## TIER 1 dispatchable now (cheap diagnostics; high info gain)

| # | Item | Source | Cost | Pre-reg HARD-PASS |
|---|---|---|---|---|
| T1.1 | **Multi-tenant Arch 1 cross-tenant adversarial smoke** | Drill 1 | ~30 min CPU (essentially already validated via kf3_multisub) | contamination_rate = 0.000 across 5 seeds + Pattern-2 codebook-collision attack |
| T1.2 | **DP Mechanism 1 Gaussian write-noise smoke** | Drill 3 | <5 min CPU at N=512 | Unbinding accuracy ≥95% at σ corresponding to ε=1 |
| T1.3 | **DR Mechanism 4 Merkle + random-projection W verify** | Drill 4 | 1-2 eng-days | Random-projection detects W corruption >100 bit flips at N=4096 with P>0.95 |
| T1.4 | **Cascading ensemble Config 5 smoke** | Drill 9 | ~60s CPU at N=4096+N=16384 | <30% escalation at τ=0.7 + cascade accuracy within 3% of large-substrate |
| T1.5 | **Long-tail Zipfian PP-10a smoke** | Drill 5 | ~60s CPU at N=4096 M=512 α=1.5 | Head/tail accuracy within 2pp at fixed load m₀=0.8 |

**Tier 1 total wall: ~3-4 hours; each validates a distinct cap_map row**. Either PASS or FAIL outcome substantively narrows positioning.

## TIER 2 (medium info gain; 1-2 eng-week scope each)

| # | Item | Source | Cost |
|---|---|---|---|
| T2.1 | **Catastrophic forgetting Candidate 1 (K_crit~√N edit-threshold)** | Drill 6 | 24h workload at N=4096; 3 seeds. Validates free-probability K≈√N prediction empirically |
| T2.2 | **DR Mechanism 1 cert-chain replay implementation** | Drill 4 | 2-3 eng-days |
| T2.3 | **DP Mechanism 3 per-pattern budget tracking engineering layer** | Drill 3 | 1-2 eng-days (no physics; pure engineering) |
| T2.4 | **Time-series Mechanism 5 sparse-block 2-tier prototype** | Drill 8 | ~30 min smoke + 1 week eng |
| T2.5 | **PP-3 rotation V2-log decomposition analysis (SPECULATIVE high-upside)** | Drill 6 | 30 min analysis; if V2 0.911 L1 drift is rotational, PP-3 doubles as CF prevention |
| T2.6 | **Substrate ensemble Config 1 independent-seed smoke** | Drill 9 | ~60s CPU; 3-seed ensemble vs 1-seed baseline at moderate load |

## TIER 3 (multi-week engineering tracks; sequence after Tier 1 verdicts)

| # | Item | Source | Cost |
|---|---|---|---|
| T3.1 | Multi-tenant Arch 1 production SaaS service layer (tenant registry + router + tiered storage + factorized-W compression) | Drill 1 | 4-6 weeks |
| T3.2 | Workflow engine: Replay-from-cert smoke + Temporal integration | Drill 2 | 3-5 weeks |
| T3.3 | Streaming SLA Enterprise tier 3-gap engineering (P99.9 GC control + write-read scheduler + log-structured replication) | Drill 7 | 6-8 weeks |
| T3.4 | Multi-tenant Arch 3 sub-space N=16384+ scaling experiment | Drill 1 | ~4 weeks; depends on production N=16384 behavior |
| T3.5 | DP Mechanism 5 subsampled writes for analytics workloads | Drill 3 | 2-3 eng-days; only if analytics use case becomes commercial |

## CAP_MAP IMPLICATIONS

### NEW rows (4 proposed)

| Row | Initial state | Empirical anchor |
|---|---|---|
| **Multi-tenant isolation (per-tenant W)** | 🟢 0.75-0.90 | kf3_multisub_v4_n4096_codebook HARD_PASS max_leakage=0; factorized-W HARD_PASS v302 |
| **Differential privacy (dual-certificate)** | 🔬 0.40-0.55 | Pending T1.2 smoke |
| **Disaster recovery (cert-chain replay)** | 🔬 0.50-0.65 | Pending T1.3 + T2.2 smokes |
| **Workflow engine audit-layer-FOR-Temporal** | 🔬 0.45-0.60 | Pending T3.2 replay-from-cert smoke |
| **Substrate ensembling (Configs 5+1)** | 🔬 0.40-0.55 | Pending T1.4 + T2.6 smokes |

### Sub-properties (no new row)

| Sub-prop | Parent row | Description |
|---|---|---|
| PP-10a Uniform tail fidelity | PP-10 (Zipfian caching) | Head/tail accuracy uniform at fixed load (query-distribution agnostic) |
| PP-4a K_crit ~ √N edit-budget | PP-4 (drift detection) | Edit cadence before spectral drift detectable; ties to free-probability prediction |

### Recommended CLOSURE

| Direction | Rationale |
|---|---|
| **Multi-tenant Architecture 2 (shared W + binding)** | Probabilistic isolation; FAILS SOC 2 CC6.1 for regulated tenants; explicitly close to avoid wasted exploration |
| **Multi-tenant Architecture 4 (hierarchical)** | Higher eng cost than Arch 1; no isolation benefit; introduces new attack surfaces; explicitly close |
| **DP Mechanism 2 (randomized response)** + **DP Mechanism 4 (local DP atoms)** | Audit-moat veto: both REJECTED at useful ε values |
| **Ensemble Config 2 (diverse-codebook) + Config 3 (N-stratified)** | Config 2 has cert-fragmentation problem; Config 3 dominated by Config 5; explicitly close |
| **Time-series substrate as standalone product line** | P=0.25; better as feature of per-fact-retention-policy killer feature; NOT a new cap_map row |

## STRATEGIC NARRATIVE BUNDLING

After Round 1 + Round 2 (16 drills total today), the proposed unified narrative is:

> **"Audit-grade memory with physics-grade guarantees: substrate stores facts with intrinsic algebraic certificates for audit, privacy (DP), tenant isolation, edit-impact-prediction, deletion, and recovery — guarantees no logging-based system can produce because they are mathematical properties of the storage algebra, not policy enforcement at the API layer."**

Defensible against:
- Anthropic Memory (logical workspace isolation, policy-grade)
- AWS Clean Rooms / BigQuery DP (query-time noise, no individual-record audit)
- Temporal / LangGraph (durable execution, no cryptographic per-step proof)
- TimescaleDB / InfluxDB (raw throughput, no per-point deletion cert)
- Redis / Pinecone (latency, no audit/privacy cert)

Wedge: NARROW (compliance-driven regulated industries) but DEFENSIBLE (physics not policy).

## CONTRACT FOR STRATEGY

1. **Tier 1 dispatch sequencing**: all 5 in parallel? Or 1-2 first (cert FP and physics-isolation are highest-strategic-priority)?
2. **NEW cap_map rows authorized?** (4 new rows + 2 sub-properties proposed)
3. **CLOSURE authorizations** (5 directions recommended closed)
4. **Tier 3 multi-week engineering**: which to prioritize? Multi-tenant production SaaS (Arch 1) is highest-strategic-value but $$$. Streaming SLA gaps (3 items, 6-8 weeks) are also load-bearing for any enterprise pilot.
5. **Unified "physics-grade" positioning**: adopt as primary narrative or hold for further validation?

## METHOD NOTES

- 9 parallel Sonnet drills + main-thread synthesis ≈ ~180-220K tokens
- 16 total capability drills today across Round 1 + Round 2; research-direction breadth substantially closed
- Per [[feedback-no-padding-experiments]]: drills selected for distinct capability axes; no overlap
- Per [[feedback-aggressive-cross-domain-research]]: cross-domain probes (DP, RMT, workflow engines, TSDb landscape) covered
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated throughout
- Per [[feedback-query-privacy-decomposition]]: all drills generic terms only

## CLOSING

Move to `routed_completed/` when strategy:
1. Authorizes (or modifies) Tier 1 dispatch
2. Approves NEW cap_map rows + sub-properties
3. Confirms CLOSURE on the 5 directions
4. Decides on Tier 3 multi-week engineering priorities

**Research session recommendation**: PAUSE new capability-direction expansion after this round; let Tier 1 verdicts return before opening more breadth. Further drills would build routing-file inventory faster than orchestrator can process.


---
**ROUTED-COMPLETED**: Acted-on 2026-06-01: 4+ NEW cap_map rows + 5 closures + bundled physics-grade positioning ADOPTED in v314; Tier 1 dispatch routing filed for exp_dev (strategy_request_to_exp_dev_research_round1_tier1_dispatch_2026-06-01.md)
