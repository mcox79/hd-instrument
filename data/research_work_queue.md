# Research (Director) Work Queue — durable anti-freeze queue

**Purpose:** mechanical anti-freeze infrastructure. Each cycle dequeues top item. Never end a cycle passive while queue is non-empty + USER hasn't directed standby. Per Fix #12 (freeze-pattern-harden discipline, 2026-06-22).

**How to use:**
- Each cycle: review queue; execute top 1-3 items in main thread or spawn background
- When item completes: mark DONE; remove or move to "Recently shipped"
- When new follow-up emerges: append to appropriate tier
- If queue depletes: refill from backlog / open loops / surfaced findings

**Anti-freeze checks (every cycle wake):**
- [ ] Did I ship at least ONE substantive thing this cycle? (spawn / edit / atom / commit / decision)
- [ ] If "standing by" — is the queue genuinely empty + USER directed standby? (If not, FREEZE pattern → execute top item)
- [ ] Did I update this queue with new follow-ups surfaced this cycle?

---

## TIER 1: In-flight (do not re-spawn; reactive on landing)

- [BG] n4 k-WTA-VQ cell (biological sparsity; brain-drill recommendation) — remote_cpu smoke + full
- [BG] Path A V_C=4096 frontier cell — remote_cpu full (~7.5h projected)
- [BG] WikiText-103 ingest cell (n6) — remote_cpu smoke
- [BG] arxiv abstracts ingest cell (n7) — remote_cpu smoke
- [BG] ConceptNet ingest cell (n8) — remote_cpu queued (OPEN-C unlock if 75x holds at full)
- [BG] text8 retry1 — accidental full on remote (~4.5h ETA)
- [BG] SMH (Sparse Modern Hopfield) cell — Path C revival #1; using pipeline-template first field-test
- [BG] HumanEval Anchor-1 cell — Qwen-1.5B stdlib-class split (substrate-as-LLM-tool pattern)
- [BG] SVAMP mechanism redesign research drill (selector-bias / multi-hop / synthetic WK training)
- [BG] Phase B chronological window 2 cert-trail enrichment (skunkworks Store-write; serialize-after)

## TIER 2: Queued (next bandwidth; ready to fire)

- [QUEUE-NEXT-CYCLE-FIRST] **c3 compressed sequence replay cell** — brain-drill #5 recommendation; substrate's missing sequence-binding primitive (S matrix via offline ordered-pair Hebbian k_{t-1}⊗k_t); 4 arms NONE/COMPRESSED/UNORDERED/ONLINE_NO_GAP; ~5min remote_cpu; **P=0.55 (NOT novel-synthesis-capped)** — direct extension of validated outer-product Hebbian; HARD_PASS depth-5 sequence_recall ≥0.80 + delta ≥0.50; SHIPS THE S MATRIX needed by g1 generation
- [QUEUE-NEXT-CYCLE-SECOND] **g1 substrate sequence generation cell** — brain-drill #4 recommendation; uses c3's S matrix as autoregressive engine; Karuvally-Sejnowski temporally-asymmetric Hebbian + Langevin sampling + HVC clock-binding; pre-reg HARD_PASS trajectory_coherence(T=8) ≥0.60 + novelty ≥1.5x + refuse_OOD ≥0.90; ~90min remote_cpu; P=0.45; gated on c3 land (c3 ships the substrate; g1 USES it)
- [QUEUE-NEXT-CYCLE-THIRD] **m1 modular K-macrocolumn W cell** — brain-drill #6 recommendation; replace single 4096x4096 W with K=8 OR K=32 modular W_k routed via Top-m k-WTA; HARD_PASS at α=0.3 recall ≥0.90 modular vs ≤0.5 K=1 anchor (capacity-cliff lift) + K=1 reproduces baseline ~327 substrate Hebbian-superposition; sqrt(K) capacity scaling at fixed parameter budget (analytic ~2.83x at K=8, ~5.66x at K=32); composes natively with k-WTA-VQ from drill #1 (k-WTA IS the router) + CLS-replay drill #2 + iterative-cleanup drill #3; P=0.45 novel-synthesis-capped; ~30-60min CPU
- [QUEUE-USER-DIRECTED 2026-06-22] **PHASE-DIAGRAM-ACTION + DATA-SURVIVES-TRANSFORM audit lane** — USER flagged latent capability ("substrate acts at any position in the phase diagram; data survives phase transformations"). 3 sub-items:
  - (a) **Phase-portrait v1 inventory atom:** scour Store for the ~47 cert-grade phase-diagram atoms identified in the 2026-06-18 phase-portrait note (capacity / α / κ / precision / encoder-decoder sweeps); build PHASE_PORTRAIT AtomKind v1 (NEW sibling of CAPABILITY_MAP; MEASURED points only, no extrapolation per cert-condition); regen-able; ~30-60min Director scour
  - (b) **Data-survives-phase-transform evidence audit:** explicit audit of candidates (transition-noise n_charngram HARDPASS / SimVQ n3 HONEST_NEGATIVE / whitening n10 eff-rank lift / CERT 591 KV-under-projection / substrate_durability_cron_v1 manifest-gap floor); classify each = chain-grade survives OR partial-survives OR untested; ~45min Skunkworks audit pass
  - (c) **p1 action-at-any-position cell pre-reg:** measure atom set A_0 stored at operating-point P_0 (V_C=1024 / N=16384 / α=0.3); transform substrate to P_1 (V_C=2048 / N=32768 / α=0.6); re-measure A_0 retrieval at P_1; HARD_PASS recall ≥0.80 of P_0 baseline; HARD_FAIL ≤0.20; ~60min remote_cpu; novel-synthesis-cap P=0.45
- [QUEUE] **Phase D cert_ledger extension** — FIRED this cycle (hdi_skunkworks; ~2-3hr in flight)
- [QUEUE] **Phase D cert_ledger extension** — FIRED this cycle (hdi_skunkworks; ~2-3hr in flight)
- [QUEUE] SVAMP Candidate D — joint pair+op training (~3-4hr cell-author + new training-data generation; rescue after Candidate A HARD_FAILed; SCHEMA-VET needed)
- [QUEUE] Back-port proper uniform-fallback to N1/N2 family cells (Fix #6 audit; non-urgent; old cells OK in full)
- [QUEUE] MEMORY.md curation (overweight 31.6KB+; CURRENT STATE block stale; compress + update)
- [QUEUE] Brain-drill #2: CLS continual learning (CLS theory + sleep replay + synaptic consolidation; ~30-60min research)
- [QUEUE] Brain-drill #3: multi-hop / working memory (prefrontal + entorhinal + planning circuits; informs U1 v2 extension to 3+ hops)
- [QUEUE] Phase A reconcile-cert-N mismatch audit (595 vs 583 chain_grade classification-logic; 12-atom delta)
- [QUEUE] Director cross-check on Path A V_C=4096 land (4-layer when it returns from remote)
- [QUEUE] Director cross-check on n4 / n6 / n7 / n8 lands (4-layer per cell)
- [QUEUE] U1 v2 with entity-name staging (FB15k-237 + entity2text.txt → unlock OPEN-C frozen-encoder baseline as planned pre-STANDSTILL; ConceptNet n8 partially handles)

## TIER 3: Composition cells (gated on Tier 1 outcomes)

- [GATED] n4 + MKN composition cell (if n4 lands HARD_PASS OR MIDDLE_BAND)
- [GATED] n4 + Path A V_C=4096 + MKN triple-composition (if both individual cells closure-direction-correct)
- [GATED] SMH + projection layer scaling (if SMH HARD_PASS; scale to higher M)
- [GATED] U1 v2 multi-hop 3+ chains (extend 2-hop chain-grade to longer chains; multi-hop ceiling test)

## TIER 4: Backlog (long-horizon; no immediate gating)

- [BACKLOG] Generation / sampling from substrate (substrate-only beyond next-token; ~brain-drill scope first)
- [BACKLOG] Continual-learning at scale validation (27x no-forget MM exists; full-scale test)
- [BACKLOG] Cross-corpus transfer cells (ingest WikiText → eval text8 perplexity; or ConceptNet → FB15k-237 transfer)
- [BACKLOG] Full Wikipedia ingest at scale (multi-million facts; tests substrate at scale)
- [BACKLOG] PubMed / arxiv full-papers / math-stack ingest (Tier 2+ ingest breadth)
- [BACKLOG] Math text-LM (after NL bigram-gap closure per math/code scope drill)
- [BACKLOG] Code text-LM (after NL + math; requires StarCoder/CodeBERT encoder swap)

## Recently shipped this autonomous arc (rolling; ≤10)

- 2026-06-22 Ferry-ask #1 RESOLVED (Orchestrator ferry response): pythia-160m local_cpu encoding rate-norm = **~67 ms/fact** (~893 facts/min) anchored to Path C wall=2798s/3seeds/12500facts; marsh@home INFERRED ~51ms/fact (1.3x faster; first-hand-measure pending); lookup table + decision rule (1.5x trust / >2x measure) operationalize Fix #17 wall-budget discipline; atom proposal `META_pythia160m_cpu_encoding_rate_norm_67ms_per_fact_local_cpu_anchor` routed to Skunkworks for SCHEMA-VET + atomization
- 2026-06-22 USER-DIRECTED PHASE-DIAGRAM lane OPENED: "substrate acts at any position in phase diagram + data survives phase transformations"; 3 sub-items queued (phase-portrait v1 inventory + data-survives audit + p1 action-at-any-position cell); ~47 cert-grade phase-diagram atom pool already in Store per 2026-06-18 phase-portrait note; memory saved (`project_phase_diagram_action_data_survives_phase_transformations_USER_2026-06-22.md`)
- 2026-06-22 Brain-drill #6 LANDED (cortical microcircuit + W-matrix architecture): substrate's W is single Hebbian sponge; cortex is K=1M macrocolumn modular store with WTA routing; 3 substrate-applicable primitives (modular K-macrocolumn W + Larkum two-stream context-binding + Bricken SDM-CL Top-K); novel synthesis composes all 3 forward-only Hebbian; m1 cell pre-reg HARD_PASS α=0.3 modular recall ≥0.90 vs K=1 ~0.5 (capacity-cliff lift via sqrt(K) at fixed parameter budget); P=0.45 novel-synthesis-cap; ~30-60min CPU
- 2026-06-22 Brain-drill #5 LANDED (hippocampal SWR + sleep replay): substrate's MISSING primitive is SEQUENCE-BINDING (not capacity); c3 cell pre-reg P=0.55 (~5min remote_cpu); compressed-time replay ~20x is the load-bearing novel finding; c3 ships S matrix needed by g1; c3+drill #1 kWTA may jointly close bigram gap
- 2026-06-22 Brain-drill #4 LANDED (cerebellar forward-prediction / generation): substrate-native generation feasible via Karuvally-Sejnowski Long-Sequence-Hopfield + Langevin sampling + HVC clock-binding; g1 cell pre-reg P=0.45; substrate L5 MOAT = generation without context window + refusal-gated per step; 4-drill convergence = substrate STRUCTURALLY aligned with biology at every brain-mechanism level
- 2026-06-22 Master plan SHIPPED (commit 08ac4e65; durable L1-L5 strategic plan; composes with work queue + plan.json + waiting_on)
- 2026-06-22 Fixes #14-19 banked + tools/queue_status.py infra + ferry-requests filed (Fix #15)
- 2026-06-22 c1 CLS replay PARTIAL (substrate-favorable surprise): NEVER FORGETS at α=0.5/J=10 (NONE baseline 1.000 vs drill prediction ≤0.40); cliff lives ABOVE α=0.5; codebook-NN argmax cleanup more robust than a8 Hopfield extrapolation; MOAT vs LLMs still holds (substrate continual-learns without replay at tested load); MM disposition predicted; 2x-revival queued (higher α / smaller codebook / overlapping-task)
- 2026-06-22 r1 multi-hop LANDED + RATIFIED MM (Skunkworks; commit ee4081e6): substrate-native chain-of-thought primitive (META atom; K=2 chain-grade + K=3,4 MM); cert_ledger row 59204e3e755136c3; r1b chain-grade promotion path in flight (margin-refuse + 7 seeds + verdict() band fix)
- 2026-06-22 SMH landed-VET RATIFIED HONEST_NEGATIVE (Skunkworks; commit 9ac12d79): META atom storage-chain-item3-eff-rank-limited-at-projection-step; cert_ledger 2caf2f8f6cf148ab; Fix #11 template patched +5 TODOs
- 2026-06-22 Whitening n10 DISPATCHED (3x route-negatives revival; smoke diagnostic FIRES eff_rank 16.7→230.3 = 13.8x; full ETA ~11:05Z; LOAD-BEARING for sparse-superposition family RE-OPEN)
- 2026-06-22 Brain-drill #3 multi-hop LANDED: iterative Hopfield cleanup per hop; r1 cell dispatched (~45min); K=3 HARD_PASS bar 0.20 + ratio ≥3x; P=0.45 deflated
- 2026-06-22 HumanEval Anchor-1 DISPATCHED full local_cpu (~3hr; smoke n=10 zero pass-flips; reclassifier tool shipped for broad n_A=35 vs narrow n=13 bucketing; substrate-retrieval hitting plausible snippets)
- 2026-06-22 Brain-drill #2 CLS LANDED: substrate has CLS stores latent (U1=hippocampus; W=cortex); c1 cell dispatched in flight; substrate's MOAT vs LLMs identified
- 2026-06-22 Phase B window 2 LANDED thin (9 enrichments; pre-CERT-NNN era cert events in portfolio_state; Phase D extension queued)
- 2026-06-22 MEMORY.md CURRENT STATE curated (13→5 lines; role-agnostic; commit 64f0f53)
- 2026-06-22 SVAMP-A HARD_FAIL (selector-bias deeper than scalar prior; Candidate D queued)
- 2026-06-22 Fix #12 freeze-pattern-harden infrastructure (durable work queue + discipline atom + memory pointer)
- 2026-06-22 Fix #6 zero-D-overlap audit (10 cells; new cells fixed; old N1/N2 family epsilon-floor smoke-vulnerable; commit 10790983)
- 2026-06-22 SMH cell dispatched via Fix #11 pipeline-template first field-test (Path C revival #1)
- 2026-06-22 HumanEval Anchor-1 cell-author bounded ~3hr (Qwen-1.5B integration)
- 2026-06-22 SVAMP mechanism redesign research drill (post WK-exhaustion)
- 2026-06-22 Phase B chronological window 2 dispatched
- 2026-06-22 ConceptNet n8 cell shipped (OPEN-C unlock candidate; smoke 75x substrate vs frozen-encoder)
- 2026-06-22 WikiText n6 + arxiv n7 ingest cells shipped (smoke dispatched)
- 2026-06-22 Path A V_C=4096 cell shipped (frontier; 7.5h projected wall)

— Research (Director). Queue maintained per Fix #12 freeze-pattern-harden discipline.
