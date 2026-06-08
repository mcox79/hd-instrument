# Research -> Exp-Dev: NEW EXPERIMENTS batch (parallel to DEMO-SUPPORT; user "dig further")

**From:** Research  **Date:** 2026-06-08 ~14:00  **Re:** User mandate "dig further; fire
out drills and route experiments." 3 new research drills dispatched in parallel + 5 new
experiment anchors filed for substrate capability extension.

## 3 research drills NOW IN FLIGHT (sonnet bg)

1. **Substrate-LLM intrinsic language 5x** — Tier 5+ architecture; what does v3.0
   substrate-intrinsic LLM look like; per user's "most exciting direction" yesterday
2. **Substrate failure mode catalog 5x** — honest deep audit of where substrate fails
   structurally vs configurationally; 30+ failure modes anticipated
3. **Substrate composition operators 5x** — expressivity ceiling of substrate's algebra;
   higher-order reasoning patterns; new compositional operators

## 5 NEW experiment anchors (in addition to DEMO-SUPPORT batch)

### N1: Pythia-3B substrate-KV (D4; Tier 5 production-scale next step)
- Substrate-product reading: extend D2 Pythia-1.4B substrate-KV HP to Pythia-3B; tests
  whether Tier 5 substrate-as-attention-backbone scales to larger LLMs
- Tier: LOCAL GPU (~6-8 hr; Pythia-3B needs ~6GB VRAM)
- HARD-PASS: recall@1 >= 0.95 at M=2000 with Pythia-3B encoder
- HARD-FAIL: degrades below 0.85 (scale ceiling for Tier 5 at small models)
- Strategic: validates production Tier 5 path for v2.0+

### N2: Substrate latency profiling at 10M / 100M (extends PP-150)
- Substrate-product reading: cycle 188 PP-150 cascade router latency P95=0.21ms at 1M;
  test at 10M and 100M facts to confirm sub-ms latency holds at production extreme
- Tier: LOCAL CPU (~3-4 hr)
- HARD-PASS: P95 < 5ms at 10M; P95 < 50ms at 100M (still well under any reasonable SLA)
- Strategic: validates substrate scales for enterprise deployment

### N3: Self-improving routing at warm equilibrium (extends cycle 168)
- Substrate-product reading: cycle 168 HP at cold-start; test at warm equilibrium with
  ~10000 queries accumulated; verify routing accuracy holds + improves
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: warm-equilibrium routing accuracy >= cold-start +5pp

### N4: Highly cyclic graph K-hop test (failure-mode probe)
- Substrate-product reading: substrate K-hop assumes acyclic traversal; test on
  intentionally cyclic graphs (e.g., social network with mutual friendships);
  verify K-hop terminates correctly
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: K-hop on cyclic graphs returns correct result without infinite loop
- Strategic: characterizes structural limit; failure-mode catalog input

### N5: Type-confusion stress test (Apple-company vs apple-fruit)
- Substrate-product reading: build KB with many same-name-different-referent entities;
  test substrate's ability to disambiguate via context
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: substrate correctly disambiguates >= 90% of context-resolvable references
- Strategic: failure-mode catalog input; characterizes named-entity ambiguity handling

## Parallel work pipeline

| Lane | Current | Next |
|---|---|---|
| **Research drilling** | 3 new drills (intrinsic language + failure modes + composition operators) | Standing for returns; synthesize when landing |
| **Exp-Dev DEMO-SUPPORT batch** | A1 Wikipedia 5.84M ingest + A2 cascade latency profile + benchmarks | A3/A4/B1/B2/B3/B4/C1 in sequence |
| **Exp-Dev NEW experiments (this batch)** | N1-N5 as bandwidth allows after DEMO-SUPPORT | Could parallel-run smaller anchors |
| **Testbed AUDIT WEEK** | Day 1 complete (portability audit) → Day 2 (Cloudflare + Pythia-1.4B + Node + API keys) | Day 3-5 audit + Week 1 backend port |
| **Cycle 189+** | Standing | Synthesize as cycles land |

## Strategic intent

User wants drilling momentum to continue alongside demo build. v1 demo work doesn't
block research depth. The 3 new drills + 5 new anchors:
- Substrate-LLM intrinsic language: v3.0 architectural exploration; could surface
  surprising near-term wins
- Failure mode catalog: HONEST deep audit; substrate's PR claim requires knowing limits
- Composition operators: substrate-as-universal-reasoning-substrate pitch development
- N1-N5: extend substrate's capability map at the architectural frontier

## v2.0 deeper anchors still PARKED until v1 demo ships
- Sparse-VALUE coding (v3.0; modest 4.4x gain)
- Differentiable VSA (paused Tier 4)
- Inter-shard analogy detection (v2.5; needs role vocab normalization)

## Cross-references
- DEMO-SUPPORT batch: notes/research_to_exp_dev_DEMO_SUPPORT_batch_AUTHORIZE_2026-06-08.md
- Tier 5 MVE GREEN: notes/research_to_exp_dev_TIER5_MVE_GREEN_strategic_implications_2026-06-08.md
- v1.5 architecture INVARIANT: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md
- Cycle 188 KG-QA validation: notes/orchestrator_to_research_results_summary_2026-06-08_cycle188.md

---

**Exp-Dev:** authorize all 5 new experiment anchors; bandwidth permitting after the
DEMO-SUPPORT batch lane drains. N1 (Pythia-3B substrate-KV) is the highest-strategic
single anchor — validates Tier 5 path to larger LLMs.

**Research:** 3 drills in flight; standing for returns. v2.0/v3.0 architectural
exploration in parallel with v1 demo build.
