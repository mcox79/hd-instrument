# PRIORITY_QUEUE_LIVE -- Research-owned single-source-of-truth experiment queue

**Owner:** Research session
**Consumer:** Exp-Dev (pulls from top when runner slot opens)
**Inform:** Testbed + Orchestrator + User
**Last updated:** 2026-06-06 ~08:40 (v4 -- Exp-Dev reconciliation; Matthiessen + K-hop HP added; ETF Hadamard promoted)
**Version:** 4

---

## How this works

- Research keeps this list rank-ordered + current
- Exp-Dev pulls from the TOP whenever a runner slot opens
- Pull = build (if needed) + queue + run + report verdict
- After verdict reported: Research crosses off + adds new cells per latest strategic state
- Empty list = idle is correct (no padding)
- Re-runs are explicit additions by Research (varied-seed only, when CI/variance gates a decision)

---

## EXP-DEV OPERATIONAL PROTOCOL

### Pulling rules

1. **Pull from top of Tier-1 first.** If Tier-1 has BUILD-status cells (e.g., `n3_cubic_tensor_capacity` Slot 2), start engineering build in parallel while pulling next ready-to-queue cell.
2. **When Tier-1 empty -> Tier-2.** Pull in listed order.
3. **When Tier-2 empty -> idle is correct.** Do not pad with re-runs.
4. **TIER-3 cells stay parked** until their environment dependency clears (FAISS env, Llama weights, vLLM install). Research moves them up when unblocked.
5. **TIER-4 cells stay parked** as multi-day eng projects. Research promotes when ready for handoff.
6. **TIER-CLOUD cells stay parked** until user authorization signal in chat OR direct note. Then route to Testbed lane.

### CPU vs GPU routing

Exp-Dev decides routing based on cell needs:
- **Pure substrate smoke (N <= 16384, no LLM):** local CPU runner. Most Tier-1 + Tier-2 cells fit here.
- **Llama-1B residual-only cells (uses existing npz):** local CPU runner; no model load.
- **Llama-1B / larger model-load cells:** local GPU runner if fits 8GB at bf16; cloud H100 if OOM. Flag to Research if cloud needed and not already TIER-CLOUD.
- **BUILD-status cells (e.g., cubic-tensor n=3):** parallel engineering build first; smoke after build complete.
- **TIER-CLOUD cells:** route to Testbed lane (not Exp-Dev directly); user auth required.

### Verdict reporting

After every cell completes:
1. File a verdict note `notes/exp_dev_to_research_<short_anchor>_<verdict>_<date>.md` with: HP/MIDDLE/HF + per-seed metrics + any methodology flags
2. Update queue.json + standard dashboards as normal
3. Research reads via Monitor (real-time) -> crosses off LIVE queue + adds follow-ons within ~30 min
4. If verdict is MIDDLE/HF on a genuine architectural axis: Research auto-dispatches 2x rescue drill per standing rule

### Re-runs

Only run when Research adds a varied-seed entry under "TIER-1 VARIED-SEED RE-RUNS" with seed=N flag. Never re-run completed cells at fixed seed (byte-identical metrics = zero new info).

### Methodology flags

If a cell has metric / methodology / saturation issues, PARK and flag to Research (like yesterday's T1-6 sparse-write metric flag). Research specifies the fix and re-routes with V2 anchor.

---

## RESEARCH STANDING RESPONSIBILITIES (this is my job)

Per user directive 2026-06-06:

### Every Monitor event (real-time; ~30 sec lag)

1. Read the new note
2. If verdict: cross off LIVE queue + assess against latest priorities + add follow-ons if warranted
3. If MIDDLE/HF on architectural axis: dispatch 2x rescue drill
4. If infrastructure / coordination note: action or acknowledge per relevance
5. Update LIVE queue commit if state changed

### Every cadence wake (30-min fallback)

1. Verify Monitor caught everything (manual scan as backup)
2. Check `notes/capability_scorecard.md` for weak / incomplete capability axes
3. Cross-reference: are current Tier-1 cells the highest-leverage moves toward peak performance?
4. If queue is empty or thin: add new cells from drill outputs / capability gaps / strategic state
5. Commit any updates

### Every drill output landing

1. Synthesize headline + per-anchor candidates
2. Add highest-leverage anchors to LIVE queue (typically Tier-1 if binding, Tier-2 if interesting)
3. Update CHANGELOG at bottom of LIVE queue file
4. Direct note to recipient if action needed (Testbed for cloud cells; Exp-Dev for builds; Orchestrator for infra)

### Always-on rules

- **Queue must always be populated with high-quality cells** (or explicitly empty with reason logged in CHANGELOG)
- **No padding ever** -- if I can't justify a cell, it doesn't go in
- **Every cell tagged against the capability it advances**
- **Capability matrix checked against queue every cycle** -- if a high-value capability is stalled, queue cells must address it

---

## TIER-1 ACTIVE

### Slot 1: `n3_cubic_tensor_capacity_n4096_v1` (BUILD; multi-day) [WAS SLOT 2]
- **Wall:** ~1-2 days engineering (sparse cubic tensor impl) + smoke
- **Source:** today's 2x alpha drill -- Tier-1 BLOCKER
- **Gates:** Phase 3 Wikipedia-class capacity claim (~10^9 facts)
- **Capability advanced:** PP-23 cubic-tensor capacity (currently 0 evidence)
- **HP threshold:** C_3 prefactor > 0; M_max scales as N^2
- **Status:** needs engineering build; not yet started

### Slot 2: ~~`substrate_etf_hadamard_codebook_init_v1`~~ HP -- 8.02x capacity (26th flagship)
- **Status:** DONE 2026-06-06 08:55 -- random_cap=51 vs hadamard_cap=409 at N=1024 (8.02x)
- **Confirms:** Matthiessen diagnosis -> codebook-collision was binding constraint; orthogonalization removes it
- **Action item:** Phase 4a infrastructure to use ETF Hadamard codebook init by default
- **Follow-on candidate (NEW Slot 8):** ETF Hadamard at N=4096 + sparse compound test (queued below)

### Slot 3 (RESPEC; was sparse-write but mechanism was unclear): `substrate_sparse_pattern_coding_vs_dense_alpha_n4096_n16384_v1`
- **Wall:** ~15-20 min CPU
- **Source:** today's 2x alpha drill -- rescue path; spec clarified after Exp-Dev's Slot 3 first attempt found mechanism ambiguous
- **Architecture:** sparse PATTERN coding (k=f*N active components; f=0.10) vs dense (f=1.0); STANDARD Hebbian outer-product write for both
- **Capability advanced:** PP-21 sparse-Hopfield linear-noise regime rescue
- **HP threshold:** sparse_alpha / dense_alpha >= 3x at f=0.10 (per Tsodyks-Feigelman classical bound ~4.35x)
- **MID:** 2-3x
- **HF:** <2x (sparse pattern coding doesn't deliver linear-noise regime benefit)
- **Metric:** auto-associative Hopfield + FLIP=0.05 + unique patterns + 0.95 accuracy
- **Self-test:** dense N=1024 should give M_max ~140; sparse f=0.10 should give M_max ~600

### Slot 4: `substrate_sparse_outer_product_write_v2` (T1-6-V2)
- **Wall:** ~20 min CPU
- **Source:** Exp-Dev's metric-fix re-route from yesterday
- **Gates:** cross-cutting sparse-write rescue (10x base)
- **Capability advanced:** PP-21 sparse-write rescue
- **HP threshold:** 10x M_max at f=0.10
- **Metric:** auto-associative + flip-corrupted cue + unique patterns + 0.95 accuracy

### Slot 5: `substrate_sparse_plus_kgram_xor_compound_v2` (T1-7-V2)
- **Wall:** ~25 min CPU
- **Source:** Exp-Dev's metric-fix re-route from yesterday
- **Gates:** 30x multiplicative compound
- **Capability advanced:** PP-21 sparse-write rescue (compound)
- **HP threshold:** 30x M_max at N=4096

### Slot 6: ~~`substrate_embedding_norm_gate_discriminability_v1`~~ HARDFAIL (genuine; norm correlated with concept)
- **Status:** DONE 2026-06-06 09:30 -- top-30% norm gate preserves only 42% of VQ concepts at v_c=256
- **Finding:** L2-norm is strongly correlated with concept identity; norm-gating drops rare concepts systematically
- **Strategic impact:** norm-gating BLOCKED as Phase 4a extraction-speedup lever
- **2x rescue drill dispatched at 09:30:** entropy-gate vs per-cluster stratified vs concept-uniform random sampling
- **Follow-on cells coming** after drill lands (~25 min)

### Slot 7 (UPDATED -- K-hop ceiling now K>=6 not K=3 per cycle 118): `substrate_native_reasoning_K10_K20_n16384_v1`
- **Wall:** ~60 min CPU
- **Source:** Cycle 118 K-hop FULL run -- lossless to K=6 (test grid ceiling); actual ceiling unknown
- **Why now:** K-hop HP'd lossless at K=1..6 in cycle 118. Next questions: (1) does losslessness hold to K=10 at the same N? (2) does it scale to N=16384 production-class? (3) where is the actual K ceiling?
- **Architecture:** test K in {6, 8, 10, 15, 20} at N=4096 (find true ceiling) AND K in {3, 5, 10} at N=16384 (scale validation)
- **Capability advanced:** Idea 1 substrate-native reasoning -- ACTUAL ceiling identification + production-scale validation
- **HP threshold:** lossless (>= 0.95 accuracy) at K=10, N=4096 (extending the K=6 ceiling) OR lossless at K=5, N=16384 (scale validation)
- **Strategic value:** if K-hop is lossless to K=20+ at N=16384, substrate-native reasoning categorically dominates LLM-mediated multi-hop QA (100x-20000x speedup claim from yesterday's drill is empirically anchored)

### Slot 8 (NEW; follow-on from ETF Hadamard HP): `substrate_etf_hadamard_plus_sparse_compound_v1`
- **Wall:** ~25 min CPU
- **Source:** Slot 2 ETF Hadamard HP (8.02x) + Slot 4 T1-6-V2 sparse-write
- **Why new:** ETF Hadamard codebook init gave 8x. Sparse-write predicted 10x. **Test the multiplicative compound: does ETF + sparse give ~80x?**
- **Capability advanced:** combined capacity rescue (multi-axis architectural improvement)
- **HP threshold:** combined M_max ratio >= 40x vs random + dense baseline at N=4096
- **Metric:** auto-associative Hopfield + flip-corrupted cue (FLIP=0.05) + unique patterns + 0.95 accuracy

### Slot 9 (NEW; Phase 4a infrastructure adoption): `substrate_etf_hadamard_phase4a_infra_eval_v1`
- **Wall:** ~30 min CPU
- **Source:** Slot 2 ETF Hadamard HP + Phase 4a infrastructure plan
- **Why new:** Phase 4a infrastructure needs codebook init choice locked in. ETF Hadamard gives 10x at N=4096; should be the default. Test against current MiniLM-based substrate setups (used by overnight HPs: KF-1 hallucination, real-encoder, continual KV).
- **Capability advanced:** Phase 4a infrastructure quality
- **HP threshold:** ETF Hadamard codebook on MiniLM substrate >= 4x capacity vs random init at matched conditions

### Slot 10 (NEW; CRITICAL Phase 3 confirmation gate): `substrate_etf_hadamard_n_sweep_capacity_v1`
- **Wall:** ~60 min CPU (4 N-points x 3 seeds)
- **Source:** Orchestrator cycle 117 -- ETF Hadamard 10.04x at N=4096 confirmed; need N-sweep to verify scaling
- **Why CRITICAL:** Phase 3 production blueprint capacity revision depends on whether 10x lift persists from N=4096 to N=65536. If it does, Phase 3 linear capacity goes from ~2,621 facts to ~26,000 facts per substrate (D=8 = ~208k facts).
- **Architecture:** ETF Hadamard codebook init; sweep N in {4096, 16384, 32768, 65536}
- **Capability advanced:** Phase 3 capacity production claim
- **HP threshold:** ~10x ratio (Hadamard / random) holds across all N-points; or at minimum doesn't drop below 5x at N=65536
- **MID:** 5-10x at N=65536 (partial scaling)
- **HF:** <5x at N=65536 (10x lift was N=4096 artifact; Phase 3 capacity claim doesn't recover)
- **Metric:** auto-assoc Hopfield + FLIP=0.05 + unique patterns + 0.95 accuracy (per ETF Hadamard methodology)
- **Strategic value:** EITHER outcome dramatically clarifies Phase 3 trajectory. If HP: linear-mode Phase 3 is viable for Wikipedia subset; cubic-tensor still needed for full Wikipedia. If HF: cubic-tensor (Slot 1 BUILD) becomes the only Phase 3 capacity path.

### Slot 11 (NEW; architectural insight from Orchestrator): `substrate_u2_codebook_query_layer_stacked_defense_v1`
- **Wall:** ~45 min CPU
- **Source:** Orchestrator cycle 117 cross-thread synthesis
- **Why new:** Hadamard init provides codebook-layer hardening (codebook-collision defense at init-time); G8 a_query_sim provides query-layer defense at retrieval-time. Stacked-defense hypothesis: COMBINED defense is multiplicatively stronger.
- **Architecture:** test substrate with (a) no defense, (b) Hadamard only, (c) a_query_sim only, (d) both
- **Capability advanced:** U2 adversarial codebook-collision robustness
- **HP threshold:** stacked defense (Hadamard + a_query_sim) > additive sum of individual defenses

---

## TIER-1 VARIED-SEED RE-RUNS (Exp-Dev: please build seeds=10 copies)

### Slot V1: `substrate_capacity_scaling_sweep_xl_v1` at seeds=10
- **Action:** build seeds=10 variant
- **Why:** effective_n=2-3; need real CI for alpha=0.040 before Phase 3 commitment

### Slot V2: `exp_hp12_v2_crypto_2048_gmpy2_latency_v1` at seeds=10
- **Action:** build seeds=10 variant
- **Why:** n=2 measurements; spec-sheet CI for HP-12 V2

---

## TIER-2 (queue when Tier-1 drains)

Bio/materials + disparate-fields cells (lower priority given overnight HPs already validated several substrate axes):
- T2-2 Allosteric G-register write gate (~30 min)
- T2-3 Hadamard rotation cert channel (~30 min)
- T2-4 Corneal dense-pack cert codebook (~30 min)
- T2-5 Wright-Fisher write lifespan (~45 min)
- T2-6 Physarum-weighted retrieval (~60 min)
- T2-7 Immune cloud encoding (~90 min)
- T2-8 Landauer write-gate (~30 min)
- T2-9 k=4 XOR at N=16384 (~30 min)
- T2-10 K=8-10 hierarchical Rule 8 (~20 min)
- T2-11 Bipolar sign-compression storage (~30 min)
- T2-12 STREAM-V2 multi-layer hooks (~60 min)
- T2-13 STREAM-V3 confidence-gated (~45 min)

Pull from this list ONLY when Tier-1 is empty.

---

## TIER-CLOUD (2 cells; user authorization required)

### CLOUD-1: 7B vs 70B extraction quality binding test
- **Anchor:** `substrate_extraction_quality_7B_vs_70B_v1`
- **Cost:** ~$0.50-1.00 cloud H100 (prefill-only)
- **Wall:** ~15-20 min
- **Gates:** ALL extraction infrastructure decisions

### CLOUD-2: PHASE4A-2 distilled 22-26M student training
- **Anchor:** `substrate_distilled_22m_student_training_v1`
- **Cost:** ~$15 cloud H100
- **Wall:** ~2-4 hours
- **Gates:** V_c=1M production scale + 20-40x extraction speedup
- **Status:** awaits Exp-Dev handoff training script

---

## CLOUD-ROADMAP (future cells; not active queue; need additional gating)

- Cascade distillation FD smoke ($2; only matters if CLOUD-1 says we need bigger LLM)
- ~~Llama-8B Tier-4 replication~~ -- user DEPRIORITIZED 2026-06-05
- Wikipedia layer-10 cache ($30-400) -- need model selection first (CLOUD-1 outcome)
- HP-12 V2 build at 100K -- gated on FAISS env fix + cubic-tensor empirical
- Gemma-2-2B extraction -- Phase 3 production launch (weeks out)
- HP-12 V3 build at 1M -- gated on Gemma + cubic-tensor
- M4 Max volunteer fleet POC -- requires coordination infrastructure
- Full Wikipedia 7B chunked extraction ($31) -- gated on CLOUD-1 + chunking infra

---

## TIER-3 (gated on environment fixes; Testbed lane)

- T1-3 STREAM-V1 vLLM Hook smoke (needs vLLM install)
- HNSW empirical (gates HP-12 V2; needs FAISS env fix)
- IVF + RaBitQ smoke (needs FAISS env)
- Hierarchical VQ k-sweep (needs FAISS env)
- HotpotQA at Llama-1B (needs Llama-1B weights local download)

---

## TIER-4 (Phase 4 features; multi-day eng work; not queue-drainable cells)

- Working memory loop (Idea 2; partially anchored overnight)
- Continual learning via KV (Idea 17; anchored overnight)
- Hallucination detection (Idea 3; anchored overnight via KF-1 HP)
- CoT cache with cert (Idea 8)
- ~~K-hop native reasoning full scale~~ -- promoted to Slot 7 follow-on
- Substrate-native programs (Idea 7; depends on K-hop reasoning extension at scale)

---

## DONE (do not re-queue)

Crossed off per Exp-Dev reconciliation 08:15:
- `substrate_matthiessen_dominant_scatterer_v1` -- HP (codebook-collision dominant) -- 24th flagship anchor
- `substrate_native_reasoning_k_hop_v1` -- HP (perfect to K=5) -- 25th flagship anchor
- `substrate_hadamard_expansion_n256_v2` (T1-5 full) -- MIDDLE 3.0x; follow-up may need N=512 later
- Slot 1 capacity_sweep_n32768 -- QUEUED (awaiting verdict); cross off when verdict reported

Already done earlier:
- KF-1 hallucination detection at MiniLM (AUC=0.999) -- 21st flagship
- Real-encoder capability transfer (1.000 both encoders) -- 22nd flagship
- Continual KV injection at N=8192 (99.8%, zero contradictions) -- 23rd flagship
- HP-1/2/3/4/5/6/9/11 + audit-core + Tier-4-Llama -- earlier flagships
- HP-12 V1 deliverables -- 17th/18th flagships
- V2-1 theta-burst-endpoint HP, V2-4 kgram-XOR HP -- 19th/20th flagships

---

## DO NOT QUEUE (re-runs of completed cells with deterministic results)

- 25 flagship anchors with deterministic results -- STABLE
- Re-runs at fixed seeds produce ZERO new information

---

## CHANGELOG

- 2026-06-06 08:05 -- v1 created. 9 Tier-1 cells.
- 2026-06-06 08:15 -- v2: added TIER-CLOUD (10 cells).
- 2026-06-06 08:30 -- v3: PARED DOWN per user audit (Tier-1 9->5; Cloud 10->2 + roadmap).
- 2026-06-06 08:40 -- v4: Exp-Dev reconciliation. Crossed off Matthiessen HP (24th flagship; codebook-collision dominant), K-hop reasoning HP (25th flagship; perfect to K=5), Hadamard N=256 MIDDLE 3.0x. ADDED Slot 2 ETF Hadamard (promoted from Tier-2 because Matthiessen pointed to codebook-collision). ADDED Slot 7 K-hop at N=16384 K=10 (follow-on from Slot 5 HP). Added operational protocol + research standing responsibilities. 2 varied-seed re-runs flagged for Exp-Dev to build (capacity_xl seeds=10, hp12_v2_crypto seeds=10).
- 2026-06-06 08:55 -- v5: Slot 2 ETF Hadamard HP (26th flagship; 8.02x capacity at N=1024). ADDED Slot 8 ETF + sparse compound test (does ~80x compound hold?) + Slot 9 Phase 4a infrastructure ETF adoption eval. Matthiessen -> ETF chain is the day's biggest architectural win: 8x capacity for free via codebook init. Phase 4a infrastructure should adopt ETF Hadamard by default.
- 2026-06-06 09:20 -- v6: Orchestrator cycle 117 ETF Hadamard FULL RUN confirmed 10.04x at N=4096 (vs smoke 8.02x at N=1024). cap_map v438 -> v439. ADDED Slot 10: CRITICAL Phase 3 confirmation gate -- Hadamard N-sweep across {4096, 16384, 32768, 65536} to verify 10x lift persists. ADDED Slot 11: U2 codebook+query stacked-defense hypothesis (architectural insight from orchestrator). If Slot 10 HPs at N=65536, Phase 3 linear capacity goes from 2,621 facts to ~26,000 per substrate; D=8 production = ~208k facts.

---

**END.**

This file IS the queue priority. Exp-Dev pulls Slot 1 first; reports verdict; Research crosses off + updates; Exp-Dev pulls Slot 2; etc.
