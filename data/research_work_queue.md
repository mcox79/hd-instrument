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

## TIER 1: ACTIVELY RUNNING (verified via queue_status)

- [BG] **c3 compressed sequence replay cell** RUNNING on cpu_runner_0 remote_cpu (~4.5min wall; ~252s full-grid 3 seeds); cell commit a27939c5; cert-trail c6a2ac5e; **smoke + full-config single-seed timing-run BOTH HARD_PASS** at every depth [1,3,5,7,10]; Director cross-check (Fix #18) VERIFIED; honest-scope META proposal drafted; cert-grade verdict locks on 3-seed land (~08:25)

## TIER 1b: LANDED — landed-VET pending (Director cross-check 2026-06-22 audit; queue_status says 0/0/0 — cells already completed)

- [LANDED HARD_PASS] **n8 ConceptNet ingest_eval_v1** verified at full (3 seeds): setrecall@M=100000 all=1.000 / refuse-OOD=0.999 / 2-hop inference=0.426 vs 1-hop=0.000 vs frozen-encoder=0.012 → **36.5x ratio vs frozen-encoder baseline** (required ≥2.0x; CRUSHED); scale-curve 1.000 at every M (5k/10k/25k/50k/100k); OPEN-C UNLOCKED; **CERT 584→585 candidate** (atomization gated on hdi_skunkworks SCHEMA-VET spawn next cycle)
- [LANDED HARD_FAIL] **Path A V_C=4096 (n5_vc_4096_frontier_v1)** — V_C frontier scaling does NOT close bigram-gap; route-negatives-to-research per USER STANDING → revival drill candidate (5x DEEPER decode-side scope refresh or compose with n10 whitening + MKN)
- [LANDED HARD_FAIL] **HumanEval Anchor-1 stdlib-Qwen split** (`exp_humaneval_stdlib_split_qwen_v1`) — substrate-as-LLM-tool pattern HARD_FAIL on coding; revival drill candidate (rescope to non-coding OR different anchor-augmentation strategy)
- [LANDED HARD_FAIL] **r1b multi-hop refuse-calibration** — r1 chain-grade promotion path FAILED (smoke MIDDLE_BAND → full HARD_FAIL); r1 K=2 anchor + K=3,4 MM intact; chain-grade promotion needs different angle
- [LANDED MIDDLE_BAND] n3 SimVQ (alignment) + n3 MKN smoothing (decode-side leverage) — partial wins; already in cert-trail history
- [LANDED HARD_PASS] SMH (Sparse Modern Hopfield) honest-negative + a8 continual_writes (revival) + csp_first_ship + n8 ConceptNet (above)
- [LANDED MIDDLE_BAND] capacity_sweet_spot_v2 (MEASURED_MECHANISM) + svamp_role_asymmetry (3 variants all MIDDLE_BAND) + humaneval_full_coverage / humaneval_real_parse / humaneval_structural_lite

## TIER 1c: Never-dispatched OR dispatched-without-trace (audit)
- n4 k-WTA-VQ — no metrics.json; either never dispatched OR dispatched and cell-author crash
- n6 WikiText-103 ingest, n7 arxiv abstracts ingest — same status as n4 (queue_status clear; no metrics directory)
- text8 retry1 — same; no metrics
- Phase B window 2 / Phase D cert_ledger extension — Skunkworks-authored; no exp_* directory expected for these

## TIER 2: Queued (next bandwidth; ready to fire)

- [QUEUE-NEXT-CYCLE-FIRST] **c3 compressed sequence replay cell** — brain-drill #5 recommendation; substrate's missing sequence-binding primitive (S matrix via offline ordered-pair Hebbian k_{t-1}⊗k_t); 4 arms NONE/COMPRESSED/UNORDERED/ONLINE_NO_GAP; ~5min remote_cpu; **P=0.55 (NOT novel-synthesis-capped)** — direct extension of validated outer-product Hebbian; HARD_PASS depth-5 sequence_recall ≥0.80 + delta ≥0.50; SHIPS THE S MATRIX needed by g1 generation
- [QUEUE-NEXT-CYCLE-SECOND] **g1 substrate sequence generation cell** — brain-drill #4 recommendation; uses c3's S matrix as autoregressive engine; Karuvally-Sejnowski temporally-asymmetric Hebbian + Langevin sampling + HVC clock-binding; pre-reg HARD_PASS trajectory_coherence(T=8) ≥0.60 + novelty ≥1.5x + refuse_OOD ≥0.90; ~90min remote_cpu; P=0.45; gated on c3 land (c3 ships the substrate; g1 USES it)
- [QUEUE-NEXT-CYCLE-THIRD] **m1 modular K-macrocolumn W cell** — brain-drill #6 recommendation; replace single 4096x4096 W with K=8 OR K=32 modular W_k routed via Top-m k-WTA; HARD_PASS at α=0.3 recall ≥0.90 modular vs ≤0.5 K=1 anchor (capacity-cliff lift) + K=1 reproduces baseline ~327 substrate Hebbian-superposition; sqrt(K) capacity scaling at fixed parameter budget (analytic ~2.83x at K=8, ~5.66x at K=32); composes natively with k-WTA-VQ from drill #1 (k-WTA IS the router) + CLS-replay drill #2 + iterative-cleanup drill #3; P=0.45 novel-synthesis-capped; ~30-60min CPU
- [QUEUE-USER-DIRECTED 2026-06-22] **PHASE-DIAGRAM-ACTION + DATA-SURVIVES-TRANSFORM audit lane** — USER flagged latent capability ("substrate acts at any position in the phase diagram; data survives phase transformations"). 3 sub-items:
  - (a) ✅ **Phase-portrait v1 inventory atom SHIPPED 2026-06-22** (`notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md`) — 38-42 chain-grade phase-diagram atoms inventoried across capacity (9) / α (12) / κ (6) / sparsity (1) / multi-seed sweep (11) / envelope (2) / cliff (1) / hopfield (1); untested regions flagged (precision regime / V_C×N above (4096,32768) / cross-domain transfer / long-horizon temporal). v2 atomization queued (`hdi_skunkworks` spawn next cycle for SCHEMA-VET + PHASE_PORTRAIT AtomKind write)
  - (b) ✅ **Data-survives-phase-transform evidence audit SHIPPED 2026-06-22** (in same artifact) — 11 chain-grade atoms directly evidence atom-survival across transform classes (projection / whitening / PCA / encoder-swap pythia→llama1b / readout-swap / paraphrase MarianMT / multilang-chain / char-ngram-noise / dim-expansion / name-augmentation / adversarial-key). Strongest single = `EXP_kv_learned_projection_v1` HARD_PASS; cross-encoder = `audit_core_C2_C3_whitened_pythia+llama1b` PASS-pair
  - (c) ✅ **p1 action-at-any-position cell pre-reg DRAFT SHIPPED 2026-06-22** (`notes/p1_action_at_any_position_phase_diagram_cell_prereg_2026-06-22.md`) — 3 (P_0, P_1) pairs span V_C lift / N_DIM lift / joint lift axes; 4 arms (WITHIN_P_0 control + P_0_TO_P_1_REPLAYED main + P_1_FRESH_INGEST capacity-baseline + P_1_BLANK_RECALL sanity-floor); HARD_PASS ALL pairs ratio ≥0.80 AND blank-floor ≤0.10 AND substrate-only-decode gate; HARD_FAIL any pair ratio ≤0.20; K=200, 3 seeds, ~6-10min remote_cpu wall (Fix #17 rate-norm 51ms/fact × 200 × 12 arms × 3 seeds); P=0.45; SCHEMA-VET deferred to next-cycle hdi_skunkworks spawn; dispatch-ready post-SCHEMA-VET clearance via hdi_exp_dev
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

- 2026-06-22 TIER 1 AUDIT (Director cross-check; queue_status 0/0/0 trigger): **n8 ConceptNet ingest_eval_v1 LANDED HARD_PASS at full** (3 seeds; 36.5x vs frozen-encoder; scale-curve 1.000 at every M; CERT 584→585 candidate; OPEN-C UNLOCKED — chain-grade ConceptNet KG #2 per L3 master plan); **Path A V_C=4096 LANDED HARD_FAIL** (route to revival; decode-side scope re-open); **HumanEval Anchor-1 stdlib-Qwen LANDED HARD_FAIL**; **r1b LANDED HARD_FAIL**; SVAMP role-asymmetry 3 variants MIDDLE_BAND. Work queue TIER 1 reconciled to landed-VET-pending status; never-dispatched audit lane added for n4/n6/n7/text8-retry
- 2026-06-22 c3 cell DISPATCHED + smoke/timing HARD_PASS + Director cross-check (Fix #18) VERIFIED + honest-scope META proposal drafted: A=0.0/B=1.0/C=0.0/D=1.0 across all depths; delta=1.0, order_delta=1.0, W_unchanged_by_sleep=True, n_llm=0; the substrate-side architectural win is the SEPARATE S MATRIX (offline-pass + ordered-pair + W-vs-S separation); biological-compression-arm discriminator is NULL in software (D=B at full precision); META atom proposal `META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing` queued for next-cycle SCHEMA-VET. Cell commit a27939c5; cert-trail c6a2ac5e; 3-seed full-land in flight on cpu_runner_0 (~4.5min wall)
- 2026-06-22 p1 action-at-any-position phase-diagram cell pre-reg DRAFT SHIPPED (USER-directed lane sub-item (c)): 3 (P_0, P_1) pairs × 4 arms; HARD_PASS ratio ≥0.80 ALL pairs + blank-floor ≤0.10 + substrate-only-decode; K=200 / 3 seeds / ~6-10min remote_cpu; P=0.45; SCHEMA-VET + dispatch deferred to next cycle (Fix #14 budget already at 1 spawn this cycle)
- 2026-06-22 MEMORY.md curated mid-session (Fix #19): 29.4KB → 18.9KB (-36%); 58 → 15 lines over 250-char ceiling; CURRENT STATE block refreshed to 2026-06-22; Fix #15 marked DEPRECATED; phase-diagram lane pointer added under ACTIVE PROGRAM
- 2026-06-22 c3 cell-author spawn FIRED (Fix #14 spawn #1 of continuation cycle; brain-drill #5 recommendation; hdi_exp_dev agent a39b1a8c background; P=0.55, ~5min remote_cpu projected; pre-reg HARD_PASS depth-5 sequence_recall ≥0.80 + delta ≥0.50)
- 2026-06-22 tools/queue_status.py bug FIXED: queue.json shape is `{'experiments': [...]}` envelope not top-level list; added _normalize_entries() helper; all 3 queues now report correctly (0/0/0 pending — autonomous arc queues clear; "18+ in-flight" belief was stale)
- 2026-06-22 Phase-portrait v1 inventory + data-survives-phase-transform audit SHIPPED (USER-directed lane sub-items (a)+(b)): 38-42 chain-grade phase-diagram atoms + 11 chain-grade data-survives-transform atoms inventoried; HARD_PASS evidence anchor = `EXP_kv_learned_projection_v1`; cross-encoder portability evidence = whitened pythia-160m + llama1b PASS pair; untested regions flagged (precision regime / V_C×N joint frontier above (4096,32768) / cross-domain transfer); p1 action-at-any-position cell pre-reg = next-cycle active dispatch
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
