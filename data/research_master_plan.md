# Research master plan (Director / strategic; durable across autonomous arcs)

**Updated:** 2026-06-22 (per USER directive post-overnight evaluation; CERT 590 (n8 ConceptNet + c3 sequence-binding + g1b generation + h_hotpotqa + p1 phase-diagram + p1_v2 LLM-class all chain-grade-ratified today); PHASE_PORTRAIT v3 INVENTORY_NON_CERT atom; hdlab/ primitives: sequence_memory + kg_traversal + multi_hop + whitening + char_trigram_encoder + generation; substrate-native bidirectional conversation path chain-grade at every layer; portal v1 (KG REPL) + v2 (English MiniLM) + v3 (substrate-native char-trigram) + /walk graph-walk all live in dashboard chat)
**Cadence:** updated at decision points; composes with `data/research_work_queue.md` (tactical) + `data/director_plan.json` (per-priority state) + `data/fleet_waiting_on.md` (blocker registry)

## L1 — Program priority (USER-LOCKED 2026-06-19)

**Capability DEVELOPMENT is the goal; cert-grade is the INSTRUMENT, not the goal.** Sequence: certify the experiment backlog + prioritize the TRULY-ENABLING ("what builds on this?" → composition #1, then storage/KG/continual; refuse-gate + positioning are NOT enabling) → THEN new things. Halt substrate-vs-LLM head-to-head positioning. Glass-box-LLM CONTINUES (builds a trackable LLM on the substrate).

## L2 — MVP frontier: substrate-native glass-box LM that beats word-bigram on text8

**Current state:** N1 v3.1 substrate-native LM EXISTS (CERT 583→584 baseline post-STANDSTILL); beats unigram (5.00 vs 6.33 BPC); caps under word-bigram (4.96 vs 3.84 at V_C=1024 × N=16384); decode-side bottleneck diagnosed (substrate captures concept-layer structure; within-concept token-entropy floor swallows gains).

**Closure stack (decode-side intervention + storage rescue + ingest breadth):**

| Lever | Status | Path |
|---|---|---|
| MKN smoothing (Chen-Goodman modified Kneser-Ney) | LANDED MIDDLE_BAND (+0.068 bits) | LIVE |
| n4 k-WTA-VQ (biological sparsity; brain-drill #1) | In flight remote_cpu | LIVE |
| Path A V_C=4096 × N=32768 frontier | In flight remote_cpu ~7.5h | LIVE |
| Composition n4 + Path A + MKN | UNTESTED | GATED on individual lands |
| Storage rescue n10 whitening (eff-rank lift 13.8x on smoke) | Full in flight ~11:05Z | LIVE |
| Encoder upgrade pythia-1B/2.8B | Conditional on n10 | TIER 2 |

**MVP gate:** any cell at substrate_bpc ≤ 3.84 on text8 (or pythia residuals) chain-grades → L2 MVP complete.

## L3 — Capabilities tier (gated on MVP OR parallel-where-independent)

**The substrate's L3 differentiators vs LLMs:**

| Capability | Status | Path |
|---|---|---|
| Substrate-native chain-of-thought (multi-hop reasoning) | r1 MM LANDED chain-grade; r1b HARD_FAIL post-VET; **r2 successor-W + TEM compound HARD_FAIL 2026-06-22 with partial-positive**: TEM compound-margin = 1.13-1.17× per-hop refuse-gate consistent K=2,3,4,10 (target 2.0×); SR closure WORSE than anchor (noise compounds through W^k in 50k-triple KG); MEASURED_MECHANISM atom candidate. 2x revival drill in flight. | LIVE 2x REVIVAL — multi-hop chain-grade-promotion structurally hard |
| Continual learning without retraining | c1 partial chain-grade (NEVER FORGETS at α=0.5; substrate-favorable); c1 full HARD_FAIL post-VET; **c2 cascade-STC-SWR HARNESS_TIMEOUT 2026-06-22** (wall=9000s 2.5hr; mechanism too slow at N=4096 J=12 α=3.0; post-mortem + Option A+C re-author spec at `notes/c2_cascade_stc_swr_timeout_postmortem_and_reauthor_spec_2026-06-22.md`) | NEEDS c2-v2 re-author (N=2048 + drop NO_REPLAY arm; ~60-75min remote_cpu) |
| Multi-value KG ingest + refuse-gate | U1 chain-grade (CERT 584) | LANDED |
| ConceptNet KG chain-grade #2 (OPEN-C unlock) | **CERT 585 chain-grade** (n8; 36.5x vs frozen-encoder; setrecall=1.000) | CHAIN-GRADE |
| HotpotQA multi-hop Wikipedia KG chain-grade #3 | **CERT 588 chain-grade** (h_hotpotqa; 892× vs 1-hop, 24× vs frozen-encoder; cross-domain) | CHAIN-GRADE |
| Multi-domain KG portfolio (FB15k + ConceptNet + HotpotQA = 3 KG shapes at chain-grade) | **LANDED** | PORTFOLIO |
| Substrate generation / sampling | UNKNOWN mechanism; brain-drill #4 in flight | DRILL → cell TBD |
| Cross-corpus transfer (text8 ↔ WikiText perplexity) | UNTESTED | DEFERRED |
| HumanEval Anchor-1 (substrate-augmented Qwen vs bare) | HOLD per Research drill 2026-06-22: smoke gain=0 at 1.5B Qwen; CodeRAG-Bench lit shows library docs flat on HumanEval, canonical solutions +12.2pt only at 7B; redirect to substrate-native arc | DEFERRED — substrate-augmented LM at 1.5B has no path |
| Math + code substrate-native LM | Sequenced after NL bigram-gap closure per scope drill | DEFERRED |
| **Phase-diagram-action + data-survives-transform (USER directive 2026-06-22)** | p1 v1 CERT 589 (N=16384-32768 explicit-W) + p1 v2 CERT 590 (N up to 65536 implicit-W LLM-class); ~47 cert-grade phase-diagram atoms in pool | CHAIN-GRADE LLM-CLASS |

**L3 gate:** ≥3 capabilities chain-grade with cross-cell composition demonstrated → L3 complete; substrate is a fully functional brain-inspired memory + reasoning + LM system.

**USER-flagged latent-capability lane (2026-06-22):** substrate acts at ANY position in phase diagram + data SURVIVES phase transformations. Distinctive vs LLMs (LLM = single frozen operating-point + can't transfer config without retraining). 3 sub-items in work queue Tier 2: phase-portrait v1 inventory atom + data-survives evidence audit + p1 action-at-any-position cell pre-reg. Composes with the L2 closure stack (multi-α LM operation) + L3 continual-learning + modular K-macrocolumn W from drill #6 (modular stores = data-routing-invariance). Periodic visible progress beat to USER per "I haven't seen any work on that" flag.

## L4 — Infrastructure (background; non-blocking)

- **cert_ledger.jsonl OPERATIONAL** (Phase 3 migration; 646 rows queryable; live-write helper)
- **Pipeline-agent template** (Fix #11; 754 lines; 4 field-tests; ~53-100K per spawn vs 150K+ prior)
- **Work queue infrastructure** (Fix #12 durable anti-freeze)
- **Queue-status tool** (Fix #11 TODO #11; `tools/queue_status.py` shipped)
- **Phase D cert_ledger extension** — project portfolio_state PP-rows + HP-cells into cert_ledger (USER-authorized firing this cycle; ~3-4hr Skunkworks spawn)
- **Phase B windows 3-N** — chronological cert-trail enrichment (thin yield expected; non-urgent)
- **Phase A reconcile-cert-N 12-atom audit** — cert-headline-honesty; deferred
- **SVAMP Candidate D** — joint pair+op training (~3-4hr; queued; needs SCHEMA-VET)

## L5 — Process discipline (autonomous-arc operational; 19 fixes banked)

**Fixes #1-19** (see `feedback_*_2026-06-22.md` memory files; index in `MEMORY.md`):

- **#1-7:** ScheduleWakeup hygiene / bundle spawns / per-seed runtime / watchers don't auto-wake / pre-flight run_mode / zero-D-overlap audit / status-line
- **#8-10:** parallel-work-backlog / codify-patterns-into-tools / notes-framing under Agent Teams
- **#11:** pipeline-agent template (META infra; iterating via field-tests)
- **#12:** freeze-pattern-harden (work queue + mandatory-ship-one)
- **#13:** plain-English-first (strengthened to WHOLE-response per Fix #13a)
- **#14-19:** spawn-budget-per-cycle / ferry-execution / smoke-VET nuance / runtime measurement strict / Director cross-check strict / MEMORY.md curation cadence

**Brain-drill cadence:**
- #1 within-concept floor LANDED (k-WTA-VQ); n4 HARD_FAIL post-VET — revival route pending
- #2 CLS continual learning: c1 LANDED partial then HARD_FAIL; **5x DEEPER drill delivered 2026-06-22** (cascade-synapse + STC tag-and-capture + SWR-gated selective replay on expanding intervals); c2_cascade_stc_swr_continual_v1 DISPATCHED to remote_cpu (~90min; P_deflated=0.40)
- #3 multi-hop reasoning: r1 MM LANDED chain-grade; r1b chain-grade promotion HARD_FAIL post-VET; **5x DEEPER drill delivered 2026-06-22** (successor-W closure M=Σγᵏ Wᵏ + TEM structural-sensory factorization + theta-gamma compound margin); r2_successor_TEM_compound_v1 designed (~10-12hr remote_cpu; P_deflated=0.45)
- #4 cerebellar forward-prediction / generation: g1 substrate-native generation LANDED (CERT 587 chain-grade via g1b capacity-sweep)
- #5 hippocampal SWR + sleep replay: composed into #2 c2 design (SWR-gated selective replay arm)
- #6 cortical microcircuit / W-matrix architecture: m1 modular macrocolumn smoke MIDDLE_BAND — full needed
- #7+: materials science (memristive devices); information theory bounds; embodied cognition (TBD)

## Active cycle (2026-06-22 autonomous arc — post-CERT-590)

4 background cells in flight:
- p1 v3 capacity-sweep cell-author (GPU pre-dispatch; Skunkworks-recommended follow-up — sweep K across α=0.14·N=9175 to discriminate near saturation at LLM-class N=65536)
- HumanEval Anchor-1 revival cell-author (GPU pre-dispatch; substrate-augmented Qwen vs bare)
- c2 cascade-STC-SWR continual learning (remote_cpu; brain-drill #2 5x DEEPER mechanism)
- substrate_self_map_v2c full-Store ingest (remote_cpu; USER strategic vision Phase 1 — full ~28k atoms + ~200k relations ingest; cluster only chain-grade anchors but let them traverse the full substrate graph)

Recently LANDED (this cycle): CERT 589 p1 phase-diagram + CERT 590 p1 v2 LLM-class implicit-W + 8/8 hdlab/ primitives + v2b MIDDLE_BAND + modern_hopfield_xl HARD_FAIL (no-cliff finding; Skunkworks REJECTED Director's atomization framing — per-arm metrics show modern collapsed, classical didn't; 0.14·N wrong referent for high-SNR cleanup) + r2 HARD_FAIL with TEM compound partial-positive 1.13-1.17× (revival drill delivered + r2c conformal-Fisher cell dispatched) + c2 HARNESS_TIMEOUT (re-author spec ready).

Revival queue (route-negatives discipline; designed + ready to dispatch when capacity opens):
- **r2c conformal-Fisher LLR aggregator** (in flight remote_cpu; ~20-30min) — addresses calibration-stack gap from r2 1.13× → 2.0× target
- **c2-v2** (Option A+C: N=2048 + drop NO_REPLAY; ~60-75min remote_cpu) — re-author of timed-out c2
- **substrate_native_qa_hotpotqa_v1** (designed `notes/substrate_native_qa_hotpotqa_generation_v1_design_2026-06-22.md`; ~30-60min GPU) — composes g1b generation × h_hotpotqa KG into substrate-native QA on real benchmark
- **substrate_as_llm_scaling_million_facts_v1** (designed `notes/substrate_as_llm_scaling_million_facts_v1_design_2026-06-22.md`; ~20-30min GPU) — 10× lift over 600K @ N=2048 baseline toward USER 100M-facts target
- **Phase 2 autoatom** (designed `notes/substrate_self_improvement_phase_2_autoatom_design_2026-06-22.md`; gated on v2c HARD_PASS or MIDDLE_BAND)
- modern_hopfield N=2048 revival, Path A revival, n10 whitening revival, MedQA v2 — deferred per L1 capability-dev priority

## Decision-point cadence

- **Update master plan when:** L2 MVP gate hit (bigram-gap closed) OR L3 capability chain-grade landed OR USER directs replan OR major HONEST_NEGATIVE re-routes substantial chunk of strategy
- **Update work queue when:** cell lands / spawn fires / TIER 2 dequeues / new follow-up surfaces
- **Update plan.json when:** per-priority state changes (per existing Director discipline)
- **Update fleet_waiting_on when:** blocker starts / clears (per shared discipline)

## Composition map (where capabilities compose toward L3 frontier)

```
N1 substrate-LM (V_C codebook + Hebbian)
  + n4 k-WTA-VQ (concept sparsity; brain-drill #1)
  + Path A V_C=4096 (finer concepts)
  + MKN smoothing
  + n10 whitening (key separability)
  → L2 MVP: substrate-native LM beats word-bigram

U1 KG ingest (multi-value Hebbian + set-readout-top-k)
  + r1 iterative-cleanup (multi-hop chain-of-thought; brain-drill #3)
  + r2 successor-W TEM compound-margin (r1b revival; brain-drill #3 5x DEEPER mechanism)
  + c1 CLS-replay → c2 cascade-STC-SWR (continual learning; brain-drill #2 5x DEEPER mechanism)
  + ConceptNet n8 (OPEN-C unlock) + HotpotQA (multi-domain KG #3)
  + p1 v2 LLM-class phase-action portability (operating-point shifts preserved)
  → L3 reasoning: substrate composes multi-hop refusal-bounded continual-learnable inference at LLM-class scale

CERT 591 contrastive projection
  + n10 whitening OR encoder-upgrade pythia-1B/2.8B
  + storage chain item #3 rescue
  → L3 storage: high-M substrate-KV with separability + capacity

brain-drill #4 (generation)
  + brain-drill #5 (sleep-replay schedule)
  + brain-drill #6 (cortical microcircuit architecture)
  → L3 generation: substrate samples coherent sequences without context-window
```

— Research (Director / master plan owner). Composes with `feedback_*` discipline catalog + `data/research_work_queue.md` tactical queue.
