# Full-Night Dispatch Plan — 2026-07-02

**Filed:** 2026-07-02 (UTC) — post-2026-07-01 late session
**Trigger:** USER authorized full-night push — finalize Stage 1, open Stage 2, chain-grade Stage 3. Liberal Sonnet 2x-drill authorized, especially on load-bearing negatives.
**Predecessor drill:** `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` (3 top-priority Dim H/I/S already in flight or bounded)
**Substrate-KB grounding:** 8 concept-queries run pre-write (temporal decay, adversarial, learned encoding, failure taxonomy, INT8 quant, latency percentile, batch throughput, nested composition). Prior work exists on ALL 8; plan builds ON not INSTEAD OF.

Lit-scan calibration penalty applied: all novel-synthesis P_deflated capped at 0.50; base deflation 0.15-0.25 vs raw intuition.

---

## Task 1 — Remaining 8 Hidden-Dim Probes

### Dim A — Temporal dynamics / forgetting timescales
- **P_deflated: 0.32** (raw 0.55 minus 0.23 lit-scan penalty; existing "stretched-exponential novelty decay" atom + Dim 3 catalog entry indicate substrate has SOME temporal characterization; question is whether forgetting curve matches biological/hippocampal timescales for M3 conversational memory)
- **Cheapest decisive experiment:** CPU, N=8192, M=10k stored items, sweep interval-since-write t ∈ {1, 10, 100, 1000, 10000} store-events; discriminator = recall vs t curve shape (power-law α∈[0.3,0.7] = biological; exponential = non-biological; flat = infinite; steep-cliff = unusable). Cost ≈ 90 min CPU. Reuse `hdlab/continual.py` + `hdlab/sequence_memory.py`.
- **Stage:** Stage 1 base characterization (belongs to closure of Stage 1 — retention curve is a base property, NOT an optimization).
- **Sonnet-drill priority:** MEDIUM. Prior substrate atom (stretched-exp decay) covers some ground; drill would extend to "which biological timescale operators does substrate reproduce?"

### Dim C — Retrieval latency percentiles vs accuracy
- **P_deflated: 0.22** (raw 0.40 minus 0.18; prior atoms "P99 tail latency problem", "DEMO-RETRIEVAL-LATENCY at 200M-fact scale", "FM-4: Retrieval latency at 1M ACCEPTABLE" already characterize means; question is whether tail latency has an accuracy penalty when we cut off)
- **Cheapest decisive experiment:** GPU (Testbed streaming_attention primitive), N=8192, M=100k, budget=1M query-response pairs; measure (p50, p95, p99, p99.9) wall-clock AND recall@1 AS FUNCTION of latency-truncation-budget. Discriminator = does aggressive truncation (p50 budget on all queries) collapse recall by >20%? If yes, substrate has a latency-accuracy tradeoff that M3 must respect. Cost ≈ 3-4 hr GPU.
- **Stage:** Stage 2 optimization (this IS an optimization question — where's the latency-accuracy Pareto frontier?).
- **Sonnet-drill priority:** LOW. Prior work is thick here; more experiment than drill.

### Dim E — Adversarial robustness / key-collision attacks
- **P_deflated: 0.48** (raw 0.65 minus 0.17; prior atoms "ADVERSARIAL ROBUSTNESS" in BATCH 3 anchor + "Adaptive Adversarial Robustness" rank-2 + Axis 1 in strong-encoders drill establish it's been NAMED; but I don't see landed adversarial-attack cells in preregs — most atoms are in RESEARCH docs not empirical results. This is a load-bearing gap for M3 threat model.)
- **Cheapest decisive experiment:** CPU, N=8192, M=10k, 3 attack modes: (1) craft key k' with cosine 0.85-0.95 to legitimate k, measure whether store(k,v) then retrieve(k') returns v (unauthorized read); (2) craft v' to poison retrieve(k) to return v' (write attack); (3) craft dense-adversarial-set that saturates capacity ~10x faster than random. Discriminator = attack success rate vs random baseline. Cost ≈ 2 hr CPU.
- **Stage:** Stage 1 base characterization (robustness IS a base property, not an optimization; M3 threat model needs this before optimize).
- **Sonnet-drill priority:** **HIGHEST.** Load-bearing M3 threat model + drill_count<3 on adversarial-empirical (all prior atoms are research not landed). Recommend 2x drill: broad (VSA/HDC adversarial literature; DNN adversarial-transfer; associative-memory poisoning; cryptographic-collision-attack analogs) + narrow (operational attack construction protocol for the 3 modes above).

### Dim F — Batch throughput scaling
- **P_deflated: 0.18** (raw 0.35 minus 0.17; prior atoms "EXP-SCALE-9: GPU throughput scaling with N", "Anchor C: Encoder batching throughput" already have operational protocols filed; substrate-KB confidence 0.38 with 3 direct hits)
- **Cheapest decisive experiment:** GPU, N=8192, M=100k, batch sizes {1, 4, 16, 64, 256, 1024}; measure throughput (queries/sec) AND effective per-query latency. Discriminator = is scaling super-linear (good), linear (fine), sub-linear (bottleneck), or falls off cliff at some batch? Cost ≈ 2 hr GPU.
- **Stage:** Stage 2 optimization (throughput IS optimization).
- **Sonnet-drill priority:** LOW. Well-scoped experiment; no drill needed.

### Dim L — Learned encoding vs random-init
- **P_deflated: 0.44** (raw 0.60 minus 0.16; prior atoms cover "HDC for Online Learning" + "Improved Cleanup and Decoding of Fractional Power Encodings" + "Optimal Hyperdimensional Representation" — but substrate uses `char_trigram_v1` random-ish encoder as CANONICAL for all Director-KB + upstream. Question: would a task-learned encoder unlock more capacity? Load-bearing for M3 conversational: language codeword geometry matters.)
- **Cheapest decisive experiment:** CPU (small model can go on laptop), N=1024 (smaller to allow training), toy compositional-recall task, 3 arms: (a) random-init encoder frozen; (b) random-init + PCA-whitening (Mu-Viswanath); (c) contrastive-learned encoder trained 1k steps. Discriminator = recall@1 gap between (a) and (c). Threshold: if (c) - (a) > 0.15 recall points → learned encoding is load-bearing for M3; queue larger-scale cell. If < 0.05 → random is enough. Cost ≈ 3-4 hr CPU (training is the expensive part).
- **Stage:** Stage 2 optimization (choice of encoder IS an optimization decision; and it's a load-bearing one for M3).
- **Sonnet-drill priority:** **HIGH.** Load-bearing for M3 (glass-box LLM = substrate-native language) + prior work is theoretical/tangential. 2x drill: broad (contrastive encoder learning / representation learning for VSA / codebook learning) + narrow (which contrastive objective fits HDC codeword geometry).

### Dim P — 4/5/6-primitive compositions
- **P_deflated: 0.42** (raw 0.60 minus 0.18; prior atoms establish 3-primitive compositions HARD_PASS + Composition depth L=10,000 cell in training-speed drill + Cell P4 position-binding × B2. Question: does substrate degrade at 4/5/6-way? Dim I nesting drill filed for pairs; this is FLAT n-way compositions.)
- **Cheapest decisive experiment:** CPU, N=8192, sweep composition arity k ∈ {2, 3, 4, 5, 6, 7, 8}, at each k measure recall of full binding `bind(a1,a2,...,ak)` given partial cue (k-1 factors). Discriminator = recall-vs-k slope. Analytical prediction: recall ~ exp(-k·noise_per_binding); observed slope steeper than analytical → super-linear-degradation. Cost ≈ 45 min CPU. **Cheap — can bundle into overnight batch.**
- **Stage:** Stage 1 base (arity IS a base characterization).
- **Sonnet-drill priority:** MEDIUM. Adjacent to Dim I nesting-depth already in flight; probably rides that drill's coattails.

### Dim R — Failure mode taxonomy (silent/loud/hallucination/refuse)
- **P_deflated: 0.36** (raw 0.55 minus 0.19; prior atoms 6-mode named + PRF failure-modes drill + gating cross-family + Hallucination-resistance. Named ≠ operationally characterized; question: for each of {silent-miss, loud-error, hallucination, refuse}, what fraction of substrate errors falls in each? This is M3 UX-critical.)
- **Cheapest decisive experiment:** No new cell — REPROCESS existing landed metrics. Take 5 recent Stage-1-close CG cells; for each error case in per_arm_rows, classify as (silent: query returned wrong item silently; loud: threshold-breach + refuse; hallucination: returned item never stored; refuse: below-threshold refuse). Discriminator = distribution shape. If mostly refuse → substrate is HONEST (great for M3); if mostly silent → dangerous for M3 (fabricate confidently). Cost ≈ 30 min analysis, NO new compute.
- **Stage:** Stage 1 base (understanding failure modes is base characterization).
- **Sonnet-drill priority:** LOW. Reprocessing existing data; small drill on M3-UX literature (calibration, honesty, refusal patterns) at most.

### Dim T — Regime-shift transitions
- **P_deflated: 0.28** (raw 0.45 minus 0.17; NREM replay + generation cell + phase-diagram atoms already touch regime transitions; question is CROSSING the phase boundary — does substrate handle regime shifts within one session or does it need re-init?)
- **Cheapest decisive experiment:** CPU, N=8192, M swept in-session from M=100 → M=5000 → M=100 → M=8000, measure recall throughout. Discriminator = does substrate recover after transient overload, or does it stay degraded? Cost ≈ 1 hr CPU.
- **Stage:** Stage 1 base characterization (regime dynamics are a base property).
- **Sonnet-drill priority:** LOW. Adjacent to existing NREM/replay work.

### Dim-priority summary (for Sonnet 2x-drill queue)
| Dim | P_def | Stage | Sonnet priority | Rationale |
|-----|-------|-------|-----------------|-----------|
| E — adversarial | 0.48 | Stage 1 | **HIGHEST** | Load-bearing M3 threat model; drill_count low on empirical |
| L — learned encoding | 0.44 | Stage 2 | **HIGH** | Load-bearing M3 language geometry |
| P — n-way composition | 0.42 | Stage 1 | MEDIUM | Rides Dim I drill |
| R — failure taxonomy | 0.36 | Stage 1 | LOW | Reprocess existing |
| A — temporal | 0.32 | Stage 1 | MEDIUM | Extends existing stretched-exp atom |
| T — regime shift | 0.28 | Stage 1 | LOW | Adjacent to NREM |
| C — latency-accuracy | 0.22 | Stage 2 | LOW | Prior work thick |
| F — batch throughput | 0.18 | Stage 2 | LOW | Well-scoped |

---

## Task 2 — Stage 2 (Optimize) Opening — Top-5 Cells Ranked

Stage 2 definition for THIS substrate: given Stage 1 base behavior, WHAT knobs give the best price-performance for M3 conversational glass-box LLM? Not a random optimize-everything; the load-bearing pareto axes are LATENCY / MEMORY / CAPACITY-DENSITY / SEMANTIC-QUALITY.

Ranking columns: **M3-load** (does M3 need this to work?), **cost-to-decisive** (hr of CPU/GPU), **new-primitive** (does cell-author need to invent hdlab code?).

### Rank 1 — INT8 dense-Hopfield end-to-end recall
- **M3-load:** HIGH. Memory-bound is a real M3 constraint (glass-box LLM on consumer hardware).
- **Cost-to-decisive:** LOW (~2 hr GPU). Testbed shipped `hdlab/int8_dense.py` today; smoke should be trivial.
- **New-primitive:** NO. Primitive already exists; cell is USE not BUILD.
- **Discriminator:** INT8 vs FP32 recall gap at M near capacity edge. If gap < 3% recall points and memory savings > 3x → CG lever for M3. Prior work (2026-07-01 INT8 rediscovery via preregs/2026-05-29_kf2_be1_n8192) establishes theoretical baseline.
- **Load-bearing rationale:** M3 wants substrate on laptop; INT8 quantization is table-stakes.

### Rank 2 — Learned-encoder vs random-encoder (Dim L above)
- **M3-load:** HIGH. Glass-box LLM = substrate-native language (USER 2026-07-01 correction); language geometry is load-bearing.
- **Cost-to-decisive:** MEDIUM (~3-4 hr CPU). Toy compositional task; training the contrastive encoder is the expensive part.
- **New-primitive:** YES. Cell-author needs `hdlab/contrastive_encoder.py` — new module for training a task-conditioned encoder. Estimate 1-2 days build.
- **Discriminator:** recall@1 delta at fixed capacity. See Dim L above.
- **Load-bearing rationale:** if random encoders are near-optimal, Stage 2 language work simpler; if learned wins big, M3 needs the whole encoder-training loop.

### Rank 3 — Adaptive-β schedule for refuse-gate
- **M3-load:** MEDIUM-HIGH. Refuse-gate CG portfolio (V_REL=256, sqrt(2·log V_REL / N) law) + Atom 15 v8 conformal are all fixed-β. Question: adaptive β conditional on cue-quality gives Pareto lift.
- **Cost-to-decisive:** LOW (~1.5 hr CPU). Reuse `hdlab/refuse_gate.py` + `hdlab/conformal.py`; new arm just swaps β schedule.
- **New-primitive:** NO. Both primitives exist; cell adds schedule logic inline.
- **Discriminator:** Pareto frontier on (recall, refuse-rate) — does adaptive dominate fixed-β at same average β?
- **Load-bearing rationale:** M3 UX needs "know when to shut up"; better refuse-gate = better honesty.

### Rank 4 — Streaming/chunked attention capacity vs latency
- **M3-load:** HIGH. M3 conversational context is streaming; Testbed shipped `chunked_attention.py` + `streaming_attention.py` today. Need to characterize the capacity-latency tradeoff.
- **Cost-to-decisive:** MEDIUM (~2 hr GPU). Sweep chunk-size and context-window.
- **New-primitive:** NO. Primitives shipped; cell uses them.
- **Discriminator:** at what chunk-size does capacity match dense-attention, and how much latency does that cost?
- **Load-bearing rationale:** streaming is M3's default operating mode for dialog.

### Rank 5 — Sparse-activation acceleration (analytical + empirical)
- **M3-load:** MEDIUM. If sparse activation preserves recall at 10-30% activity, memory bandwidth and speed both improve.
- **Cost-to-decisive:** MEDIUM (~2 hr CPU + 1 hr GPU). Existing `hdlab/binding.py` + `hdlab/cleanup_family.py`; sparse arm needs activity gating.
- **New-primitive:** MAYBE. Small helper in hdlab (`sparse_gate.py`); Testbed can likely ship in ~1 session.
- **Discriminator:** recall @ activity-level ∈ {1.0, 0.5, 0.3, 0.1, 0.05}. Threshold: activity=0.3 with recall gap < 5% → sparse-CG lever.
- **Load-bearing rationale:** M3 laptop-compute — sparse is a memory-bandwidth win.

### Deferred to later Stage 2
- Latency percentile Pareto (Dim C above) — bundle after INT8 lands
- Batch throughput scaling (Dim F above) — bundle after streaming attention lands
- INT4 aggressive quantization — smoke only until INT8 CG

---

## Task 3 — Load-Bearing Negatives for Sonnet 2x-Drill

Ranked by (load-bearing-for-M3 × drill-payoff × novelty-of-negative):

### Rank 1 — "Can substrate be adversarial-robust?" (USER's candidate b + Dim E)
- **Why load-bearing:** M3 threat model. If substrate breaks on adversarial keys → any glass-box LLM built on it is unsafe. Prior atoms establish concept NAMED, not empirical characterization.
- **2x drill scope:** broad (VSA/HDC adversarial + DNN adversarial-transfer + associative-memory poisoning + cryptographic-collision-attack analogs) + narrow (operational protocol for the 3 attack modes in Dim E — cosine-close key, poisoning write, dense saturation).
- **Deliverable:** attack construction protocol + expected defense mechanisms + literature-derived baseline attack-success rates.

### Rank 2 — "Why does dense-Hopfield saturate underloaded regime universally?" (USER's candidate a)
- **Why load-bearing:** Twin HF findings (Dim H distributional-shape + Dim S metric-dependence) both fell over here. This is a MECHANISM question, not a scaling question. Substrate discriminator "must survive scale" rule caught it, but WHY is theoretical.
- **2x drill scope:** broad (dense associative memory theoretical bounds — Krotov-Hopfield energy; Ramsauer capacity; Amit-Gutfreund wall; sample complexity bounds; underparameterized-regime rescue) + narrow (does our specific dense-Hopfield READ-REPLACE + M3 architecture have a testable prediction at what load fraction saturation kicks in?).
- **Deliverable:** theoretical prediction curve + Amit-Gutfreund-wall-crossing test protocol + go/no-go on whether every dense-HF cell needs a super-wall arm.

### Rank 3 — "Is there a systematic gap between HDC recall metric and semantic-utility?" (Dim S extension)
- **Why load-bearing:** M3 conversational quality is not top-1 recall; it's semantic similarity + utility to downstream turn. Substrate closed cells on top-1; question: is there a task where top-1 says PASS but semantic-utility says FAIL?
- **2x drill scope:** broad (retrieval-eval literature: BEIR / MTEB / cross-encoder vs bi-encoder; semantic-similarity vs task-utility gap; Goodhart on retrieval metrics; conversational-quality evaluation) + narrow (which specific downstream utility metric would we adopt for M3 conversational evaluation).
- **Deliverable:** metric-selection recommendation for Stage 2/3.

### Rank 4 — "Does substrate hallucinate confidently under load?" (Dim R extension)
- **Why load-bearing:** If distribution is silent-fail-heavy, M3 becomes untrustworthy. This is Dim R turned into a negative-drill: "why WOULD substrate hallucinate?"
- **2x drill scope:** broad (calibration literature for retrieval; confidence-under-load; hallucination taxonomy in LLM/RAG; honest-refusal design patterns) + narrow (which existing refuse-gate configurations minimize hallucination-rate).
- **Deliverable:** hallucination-rate prediction + gate-configuration recommendation.

### Rank 5 — "What happens at 100M+ M scale — is the M3 KB fundamentally viable?" (scaling-negative)
- **Why load-bearing:** M3 conversational needs LARGE KB. Prior atom "FM-4: Retrieval latency at 1M ACCEPTABLE" only goes to 1M; M3 needs 10M-100M facts probably.
- **2x drill scope:** broad (production-scale associative memory; billion-scale ANN; disk-backed VSA store; distributed HDC) + narrow (analytical model of substrate at 100M scale + which of our 30+ hdlab primitives break there).
- **Deliverable:** scaling-analytical model + break-mode taxonomy at 100M.

---

## Cross-References

- Predecessor drill: `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md`
- BACKUP: `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-01_LATE.md`
- Stage-progression rule: `feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md`
- Substrate-doesn't-know-anything: `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- Discriminator-must-survive-scale: `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md`
- M3 architecture: `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md`
- Glass-box LLM: `project_glass_box_LLM_substrate_native_language_no_external_LLM_USER_LOCKED_2026-07-01.md`
- Testbed shipped 2026-07-01: `hdlab/int8_dense.py`, `hdlab/k_cliff_scaling.py`, `hdlab/schema_exemplar_bayes.py`, `hdlab/chunked_attention.py`, `hdlab/streaming_attention.py`
- Related HF twin findings: Dim H distributional-shape drill + Dim S metric-dependence drill (both in flight per predecessor)

## Recommended Immediate Dispatch (next 8-12 hr)

1. **Spawn Sonnet 2x-drill on Dim E adversarial** (Rank 1 negative) — deepest load-bearing gap.
2. **Spawn hdi_exp_dev to author Rank-1 Stage-2 cell (INT8 end-to-end)** — cheap, uses shipped primitive, closes Stage 2 opening.
3. **Spawn Sonnet 2x-drill on dense-Hopfield underloaded-saturation** (Rank 2 negative) — theoretical, unblocks discriminator-design going forward.
4. **Spawn hdi_exp_dev to author Dim R failure-taxonomy reprocess** — no compute, quick close of a Stage 1 base characterization.
5. **Bundle Dim A/P/T into single overnight CPU cell if queue capacity** — all Stage 1 cheap and adjacent.

Budget: 2 Sonnet drills + 2 hdi_exp_dev spawns = 4 in flight; within default ≤3-in-flight cap only if serialized. Recommend Sonnet drills first (they don't count against experiment queue), then hdi_exp_dev sequential.
