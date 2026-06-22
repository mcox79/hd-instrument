# Research master plan (Director / strategic; durable across autonomous arcs)

**Updated:** 2026-06-22 (per USER directive post-overnight evaluation; CERT 584→585 ratified n8 ConceptNet HARD_PASS; PHASE_PORTRAIT v3 INVENTORY_NON_CERT atom written; SequenceMatrix substrate primitive shipped to hdlab/)
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
| Substrate-native chain-of-thought (multi-hop reasoning) | r1 MM LANDED (K=2 anchor + K=3,4 MM); META atom shipped | LIVE r1b chain-grade promotion |
| Continual learning without retraining | c1 partial (NEVER FORGETS at α=0.5; substrate-favorable); α=1.5 overload pending | LIVE c1 full + revival cell post-VET |
| Multi-value KG ingest + refuse-gate | U1 chain-grade (CERT 584) | LANDED |
| ConceptNet KG chain-grade #2 (OPEN-C unlock) | **LANDED HARD_PASS at full** (3 seeds; 36.5x vs frozen-encoder; setrecall=1.000 at every M 5k-100k; CERT 584→585 atomization pending) | CHAIN-GRADE |
| Substrate generation / sampling | UNKNOWN mechanism; brain-drill #4 in flight | DRILL → cell TBD |
| Cross-corpus transfer (text8 ↔ WikiText perplexity) | UNTESTED | DEFERRED |
| HumanEval Anchor-1 (substrate-augmented Qwen vs bare) | Full in flight ~3hr | LIVE |
| Math + code substrate-native LM | Sequenced after NL bigram-gap closure per scope drill | DEFERRED |
| **Phase-diagram-action + data-survives-transform (USER directive 2026-06-22)** | ~47 cert-grade phase-diagram atoms in pool; audit + p1 cell queued | LANE OPENED |

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
- #1 within-concept floor LANDED (k-WTA-VQ)
- #2 CLS continual learning LANDED (U1=hippocampus + W=cortex)
- #3 multi-hop reasoning LANDED (iterative-cleanup; r1 MM)
- #4 cerebellar forward-prediction / generation IN FLIGHT
- #5 hippocampal SWR + sleep replay QUEUED (firing this cycle per USER)
- #6 cortical microcircuit / W-matrix architecture QUEUED (firing this cycle per USER)
- #7+: materials science (memristive devices); information theory bounds; embodied cognition (TBD)

## Active cycle (2026-06-22 autonomous arc)

15+ background spawns in flight; 2 remote cells running; queue saturated at TIER 1. Multiple landings expected over next 1-7hr (HumanEval / c1 full / Path A / r1b / n10 / n4 / n6 / n7 / n8 / brain-drills #4/#5/#6 / Phase D).

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
  + c1 CLS-replay (continual learning; brain-drill #2)
  + ConceptNet n8 (OPEN-C unlock)
  + r1b chain-grade promotion (margin-refuse calibration)
  → L3 reasoning: substrate composes multi-hop refusal-bounded continual-learnable inference

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
