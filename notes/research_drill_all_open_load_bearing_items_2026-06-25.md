# Research drill — all open load-bearing items (comprehensive)

**Date:** 2026-06-25 (evening; v2c V=10000 smoke HARD_FAIL_NULL just landed → Wave D biology-native CLOSED negative-in-regime; substrate basis essentially finalized; this drill turns to envelope-extension and the remaining truly-open items)
**Driver:** USER full-auto directive — drill all non-chain-grade load-bearing items: barriers, prior tests, novel angles, P(solve), recommended next experiment.
**Discipline:** Q-default UNDER-claim (Fix #28); per-arm metrics not verdict_msg (Fix #28 #14); substrate-mine FIRST (USER 2026-06-22); brain HIGH-prior on brain-grounded mechanisms (USER 2026-06-23); lit-scan calibration penalty 0.15-0.25 on P(solve).

---

## Drill-level summary (read first)

Of 15 open Category 2 items:
- **3 are effectively CLOSED today** by landings I should fold into the assessment (2c Stage 3 integrated demo HARD_PASS; 2o g1b capacity sweep HARD_PASS chain-grade-eligible; Wave D biology-native v2c V=10000 HARD_FAIL_NULL — closes the encoder-biology revival angle for #2a/#2b/#2m)
- **5 are HIGH-leverage with strong P(solve)** (2b anisotropy real-data via Charikar — already 0.982 in smoke; 2g WM K>32 with cleanup; 2e intent at 1000; 2d KG d-sigma sweep at M=10M; 2f continual at 1000+ cycles)
- **4 are HIGH-leverage with moderate P(solve)** (2a WM-scaffolded multi-hop redesign — distinct from today's HARD_FAIL; 2h NAMED-corpus expansion; 2k long-depth sequence binding; 2l NESS alpha>0.7)
- **3 are LOW-leverage and likely closed** (2i refuse-gate nonlinear chain-grade requires real-bge — defer; 2j b_delta finite-extension chain-grade — defer; 2n heterogeneous-routing — SEGREGATED v6 just landed MIDDLE_BAND, brain analog doesn't transport at this composition; defer)

Recommended next 7-cell dispatch wave at end of doc.

---

## Section 1 — Category 2 deep drill (each item)

### 2a. Multi-hop QA beyond 2 hops (Barrier 1)

**Status:** REFUTED 3-for-3 today (consolidation v3 / pointer-chain v2 / WM-scaffolded v1 all HARD_FAIL); META_BARRIER_1_TRIPLE_NEGATIVE atomized.

**Barrier mechanism:** at each hop, cleanup error is multiplicative. With per-hop sigma0=0.95 (the chain-grade cleanup gate), 3-hop ≈ 0.857, 5-hop ≈ 0.774, 10-hop ≈ 0.60. The substrate's "noise floor" compounds geometrically per hop. Substrate-native attempts to break this:
- **Consolidation v1/v2/v3** — pre-compute the shortcut A→C from training examples; cleanup will retrieve the shortcut directly. FAILS because the shortcut entries pollute the lookup library for novel queries (held-out crosstalk).
- **Pointer-chain hybrid v1/v2** — naive iteration; per-hop cleanup then pass forward. FAILS for the geometric error compounding reason above; v2 with rail-fix STILL HURTS baseline by 22pp.
- **WM-scaffolded v1** — hold intermediates in WM slots, do hop-by-hop fresh lookups. FAILS — WM holds the intermediates cleanly but doesn't UPGRADE them; the lookup quality at hop 2 still suffers from per-hop sigma0=0.95.

**Brain analog:** PFC + hippocampus + cortical pathway with error correction. Brain does multi-hop because:
1. Hippocampus performs ONE lookup with cleanup
2. PFC HOLDS the intermediate WITHOUT degrading it (substrate WM has this — chain-grade)
3. Hippocampus performs SECOND lookup from PFC-held intermediate
4. Brain uses ATTENTION-GATED RE-CLEANUP between hops (suspected mechanism — Olsen/Buzsáki 2021 theta-gamma gating)

**Why WM-scaffolded v1 failed despite having #1/#2/#3:** the cell did naive forward — `lookup→write→read→lookup`. There's no per-hop CONFIDENCE-THRESHOLDED gating that says "this intermediate is too noisy; trigger re-cleanup or refuse." The brain has metacognitive confidence (anterior cingulate); substrate has CSP (chain-grade) but didn't COMPOSE it into the WM-scaffold cell.

**Novel angles (substrate-native, not yet tried):**

**Angle 1 — CONFIDENCE-GATED ITERATED CLEANUP (P=0.35):** at each hop, compute CSP confidence; if confidence < tau, trigger iterated-cleanup (multi-step iterative cleanup from the same cue) before passing to next hop. Substrate has CSP chain-grade and iterated_cleanup_cue_clamped_v1 already in audit list. NOT YET COMPOSED in a multi-hop cell.

**Angle 2 — NESS-STYLE PROBABILISTIC WALK WITH CLEANUP VOTING (P=0.30):** NESS chain-grade (kmax_ness_envelope_corrected_v1 HARD_PASS) says substrate can WALK a graph (any-valid-neighbor) cleanly. Apply NESS at each hop with cleanup-augmented K-candidate retention; majority-vote at terminal. This is the "soft DFE / turbo decoder" pattern from telecom — does substrate-native soft-chain DFE work for multi-hop? Already dispatched as `substrate_soft_chain_dfe_multihop_v1` (in exp_dev queue per fleet_waiting_on; status: PENDING). Tracking.

**Angle 3 — SEPARATE-W SEMANTIC CONSOLIDATION (P=0.20):** Option C from Barrier 1 — substrate splits storage into hippocampus-W (recent specifics) and cortex-W (long-running patterns). Feature-extraction primitive at sleep-replay analog extracts what's COMMON across many similar facts into cortex-W; lookup checks BOTH stores. Brain mechanism is real but substrate lacks the feature-extraction primitive. Build cost: HIGH (new primitive).

**Angle 4 — ATTENTION-GATED RE-CLEANUP (P=0.40):** between hops, run a learned attention head on the (current-cue, candidate-targets) pair; gate which candidates to keep. This composes ATTENTION primitive (which substrate has informally via softmax in n1_v3) with multi-hop. Requires authoring; P(solve) higher because brain literature is strong on this (Olsen/Buzsáki theta-gamma; Eichenbaum 2018).

**Field literature (2020-2026):**
- **HopRAG (2024 arxiv)** — language-model multi-hop using retrieval-augmentation; achieves 70% on HotpotQA but requires neural attention. NOT substrate-native but the iterative-retrieval pattern transfers.
- **Tree-of-Thought (Yao 2023)** — explicit branching with self-evaluation; analogous to confidence-gated iterated cleanup but at token level. Lit prior: confidence-gating DOES help multi-hop in LLMs.
- **Hippocampal indexing theory (Goyal/Buzsáki 2021)** — brain hippocampus DOES NOT directly compute multi-hop; it INDEXES into cortical patterns that the PFC then composes. This matches Option C; substrate would need analog.
- **Lit-scan calibration penalty:** novel-synthesis P capped at 0.50 per discipline; angles 1, 2, 4 each <0.50.

**Recommended next experiment:** **`substrate_multihop_csp_gated_iterated_cleanup_v1`** — composes (a) per-hop sigma0 cleanup, (b) CSP confidence calibration (chain-grade), (c) iterated cleanup trigger when CSP < tau, (d) WM scaffold to hold intermediates. Pre-reg HARD bands: 3-hop top1 ≥ 0.50 (baseline naive 3-hop ~0.10) AND 4-hop top1 ≥ 0.30. MIDDLE_BAND [0.30, 0.50] for 3-hop. HARD_FAIL if iterated-cleanup-arm ≤ baseline naive-arm + 0.05. Self-test: confirm CSP gate fires at >70% of hops at sigma0=0.90 sim. Smoke: 5min on local CPU.

**P(solve) overall on Barrier 1:** ~0.40 across all angles combined; ~0.35 specifically for the CSP-gated iterated-cleanup angle.

---

### 2b. Anisotropy on real-data Pythia keys

**Status:** Whitening HARD_FAIL on real Pythia keys at M=10k (whitened recall 0.068 ≈ raw 0.048; calibration-anchor 0.32 vs CERT591 0.827). Confirms anisotropy is NOT a synthetic-only artifact. Charikar Arm B' at 0.982 in 4-arm smoke (unconfirmed; calibration meter under-saturated at 0.445 so interpret RELATIVE only).

**Barrier mechanism:** Pythia 160M residual-stream keys are anisotropic (Mu-Viswanath 2017; Ethayarajh 2019 measured cosine self-sim ~0.40-0.50 across layers). Dense-superposition stores assume isotropy; recall collapses when keys cluster in a cone. Whitening was the obvious rescue; it FAILS because (a) shrinkage-ZCA has tau-tradeoff (tau=0.05 in our cell may be wrong), (b) covariance-estimate uses TRAIN_M=600 which under-samples the cone for the M=10k query distribution, (c) post-whitening the EFFECTIVE rank is still degenerate (per Skunkworks 6d3d2d82 finding: eff-rank ~3.6x at projection step is intrinsic, not whitenable).

**Brain analog:** retinal whitening at LGN (Atick-Redlich 1990); V1 gain-control; cortical fly-LSH-like sparse coding from Kenyon cells (Dasgupta 2017). Brain DOES NOT whiten via ZCA — it sparse-codes via competitive K-WTA and uses cerebellar fan-in (K=5 random projection per granule cell, ~200K granule cells per Purkinje). The brain's solution to "dense-real-data anisotropy" is SPARSE CODING WITH RANDOM FAN-IN, not whitening.

**Prior tests beyond whitening:**
- **4-arm sweep (today's smoke):** ARM_A cerebellar K=5 dense (0.041); ARM_B fly-LSH (0.612 raw, 0.982 with Charikar control); ARM_C composition (0.573); ARM_D attention upper-bound (0.445). Meter under-calibrated; relative only.
- **Learned projection (kv_learned_projection_v1)** chain-grade — recall ≥ 0.70 held-out; this IS the substrate-product answer for encoder upgrade (per CORRECTION v2 audit). Anisotropy-rescue is ORTHOGONAL — for the M-indep dense store specifically.

**Novel angles (substrate-native):**

**Angle 1 — CHARIKAR LSH MULTI-PROBE (P=0.55):** Charikar 2002 sim-hash with multi-probe (k=4-8 probes per query); fly-LSH literature shows multi-probe lifts recall 3-5x at same M. Smoke showed Arm B' at 0.982 RAW; need full sweep with calibrated meter (ARM_D ≥ 0.80). HIGH P because (a) literature strong, (b) smoke already shows the rescue in regime, (c) substrate has sparse-bipolar primitive that composes.

**Angle 2 — CONTEXTUAL/TOKEN-SPECIFIC WHITENING (P=0.30):** instead of one global whitening matrix, learn token-specific (or token-cluster-specific) whitening based on the Pythia POS / layer / context-window. Brain V1 uses contextual gain control. Build cost: MEDIUM. Risk: learns to memorize.

**Angle 3 — LEARNED HASH FAMILIES (P=0.40):** instead of fixed Charikar random hyperplanes, train hash functions to maximize key-separation on real Pythia data. Wave D learned-projection chain-grade is evidence learning generalizes. Build cost: MEDIUM.

**Angle 4 — SPARSE FAN-IN CEREBELLAR K=5 WITH EXPANSION (P=0.35):** ARM_A in today's 4-arm was K=5 sparse fan-in dense at PROJ_DIM=768; literature (Litwin-Kumar 2017) prescribes K=5 with EXPANSION to ~200x granule cells. Substrate's PROJ_DIM=768 may be too narrow. Try PROJ_DIM=40000 sparse-binary expansion (200x fly mushroom-body ratio). Build cost: LOW (just expand sparse dim).

**Field literature (2020-2026):**
- **Fly LSH (Dasgupta 2017 Science)** — sparse random projection + WTA-top10% beats LSH at finding nearest neighbors in olfactory representations
- **Mu-Viswanath (2017)** — anisotropy in word embeddings; whitening DOES rescue some but recall-vs-isotropy tradeoff
- **Ethayarajh (2019)** — Pythia/GPT residual stream is highly anisotropic at most layers (only late-layers approach isotropy)
- **Karpukhin (2020 DPR)** — learned dense passage retrieval beats BM25 only AFTER contrastive training (matches substrate's kv_learned_projection win)
- **Lit calibration:** Angle 1 P=0.55 already includes -0.10 lit-scan deflation; substrate's Charikar=0.982 SMOKE is strong evidence; capping at 0.55 for the unverified-at-full-meter caveat.

**Recommended next experiment:** **`substrate_anisotropy_rescue_4arm_v2_calibrated_full`** (already in exp_dev queue per task brief; status: just spawned). Full sweep with calibrated ARM_D ≥ 0.80; M ∈ {1000, 4000, 10000} × 3 seeds. Pre-reg HARD bands: ARM_B' (Charikar) recall ≥ 0.80 at M=10k AND beats RAW by ≥ 5x AND meter calibrated ARM_D ≥ 0.80 → chain-grade. MIDDLE_BAND if Charikar 0.50-0.80. HARD_FAIL if meter still un-calibrated.

**P(solve) overall on anisotropy real-data rescue:** ~0.50 across angles 1+4 (Charikar multi-probe + cerebellar expansion); learned-projection (Wave D) ALREADY chain-grade is the substrate-product fallback.

---

### 2c. Stage 3 integrated audit-device at PRODUCTION V

**Status:** Cell A `substrate_stage3_integrated_audit_device_demo_v1` LANDED HARD_PASS_INTEGRATED_AUDIT_DEVICE (all category targets met at V_C_IN=600 V_REL=8 M_KV=10k N=8192; in_ans=1.000 out_ref=1.000 near_ref=1.000 uncert_corr=1.000 p95=4.39ms cv=0.000). Envelope caveat inherited from refuse-gate v2 (V_REL ≤ ~50).

**Barrier at production V:** at V_C_IN=2000 + V_REL=50:
- **Cleanup degradation:** per substrate META cleanup-integrity rule, sigma0 ≥ 0.95 requires N ≥ 8192 for V ≤ 4000. At V_C_IN=2000 this is in-envelope BUT at V_REL=50 the joint (subject_atom × relation_atom) composition introduces 100k effective bindings; cleanup may strain at sigma0=0.85-0.90 (not 0.95).
- **Capacity per primitive:**
  - Audit-based refuse: V_REL ≤ ~50 envelope; AT V_REL=50 boundary already
  - Intent classifier: 50 intents acc=0.754; at 100+ intents UNKNOWN (item 2e)
  - Dense KV: M ≤ 30k for d=768 sigma=0.1; M_KV=10k SAFE
  - CSP: speedup 8.42x; no known cliff
  - Permutation binding: chain-grade today; no known cliff
- **Per-primitive cascade failure modes:** if cleanup degrades to 0.85, the audit-gate sees noisier features → false-positive rate ↑; if intent classifier degrades, refuse-rate goes UP for in-domain queries → user-experience degrades.

**Prior tests:** Cell A landed at one (V_C_IN=600, V_REL=8) operating point. NO production-V evidence yet.

**Novel angles (not really novel; this is envelope extension):**
- EXT-1 already pre-specced (V_C_IN ∈ {1000, 2000}; V_REL ∈ {20, 50}; N=8192; M_KV=10k; 3 seeds; 3000 mixed queries per point; 4-category bands).

**Recommended next experiment:** **EXT-1 from `notes/research_envelope_extension_prespec_batch_2026-06-25.md`** — `substrate_stage3_integrated_audit_device_demo_v2_production_scale`. Route to GPU overnight_queue. Pre-reg already filed. P(solve at production V): ~0.50 — most primitives are in-envelope but the V_REL ≤ 50 boundary of refuse-gate v2 is the LIKELY cliff.

**P(solve) overall on production-V integrated:** ~0.50. Hedge: if EXT-1 HARD_FAILs at V_REL=50, the substrate-product audit-device is shippable at V_REL≤20 (~20 relation types) which is still useful for narrow vertical (medical, legal, customer-support).

---

### 2d. KG (d, sigma) phase sweep for M=10M+

**Status:** Cell 1 (`substrate_partition_routing_10M_full_v2`) chain-grade @ M=100k + MM bound @ M=1M per Skunkworks today; routed_recall=0.95 at M=1M but routing_acc=1.0 saturated. Cell B dense KV chain-grade @ M=10k with cliff at M=50k.

**Barrier at M=10M+:** partition routing at partition_size=2000 → 5000 partitions at M=10M. Routing accuracy is currently saturated at 1.0 at M=1M (suspect by-construction; routing is FHRR-binding pairs to partition labels; at V_PARTITION=5000 the FHRR pair-space might collapse). Per-partition cleanup still chain-grade per Cell B envelope.

**Predicted cliff:** routing — partition VSA is `subject_atom × partition_label_atom` which is an FHRR binding; FHRR capacity ~ N / (k·log V) ≈ 8192 / (2·log 5000) ≈ 540 distinct partitions before crosstalk. So **predicted cliff is at ~500 partitions = M ~= 1M** which is EXACTLY where saturation appears in today's Cell 1 ruling. At M=10M the routing layer will need either (a) higher N (N=32768 → ~2200 partitions), (b) hierarchical routing (partition-of-partition), or (c) different routing mechanism (e.g., learned hash for partition assignment).

**Brain analog:** hippocampal indexing into cortical regions (Goyal/Buzsáki 2021); brain DOES NOT do single-level routing at 10M scale — it uses HIERARCHICAL INDEXING. Substrate analog = partition-of-partition (level-2 routing).

**Novel angles:**

**Angle 1 — HIERARCHICAL ROUTING (P=0.55):** 2-level. Level-1 routes to ~50 super-partitions (in chain-grade envelope; FHRR pair-space safe); level-2 routes to ~200 sub-partitions per super-partition. Total routable: 50×200 = 10000 sub-partitions × 2000 per = 20M. Substrate has all primitives; just need to compose.

**Angle 2 — d-SIGMA SWEEP (per EXT-2 pre-spec) (P=0.45):** raise d and lower sigma. Predicted: d=2048 sigma=0.05 at N=16384 should hold M=10M with single-level routing because larger d gives more FHRR pair-space.

**Angle 3 — LEARNED HASH FOR PARTITION ASSIGNMENT (P=0.40):** kv_learned_projection chain-grade evidence says learned generalizes; learn hash that maps subject_atom directly to partition label without FHRR binding. Build cost: MEDIUM.

**Field literature (2020-2026):**
- **HNSW + Faiss at billion-scale** — standard ANN libraries route via hierarchical small-world graphs; very strong literature prior for hierarchical → 1B-scale
- **ScaNN (Google 2020)** — anisotropic quantization + hierarchical; 10B-scale verified
- **Lit calibration:** angle 1 P=0.55 includes -0.15 lit deflation; angle 2 P=0.45 includes -0.20

**Recommended next experiment:** **`substrate_partition_routing_hierarchical_2level_v1`** — 2-level routing. Pre-reg HARD bands: routed_recall@10 ≥ 0.85 at M=10M AND routing_acc_L1 ≥ 0.85 AND routing_acc_L2 ≥ 0.85 → chain-grade. MIDDLE if recall 0.50-0.85. HARD_FAIL if either routing layer ≤ 0.75. Self-test: confirm L1+L2 routing matches single-level at M=100k.

**P(solve) overall on M=10M KG:** ~0.55. High because Cell 1 single-level already chain-grade at M=1M; hierarchical extension is well-mapped.

---

### 2e. Intent classifier at 1000+ intents

**Status:** chain-grade at 50 intents (acc=0.754; maj_mult=4.62; rand_mult=5.19; p95=0.54ms; n_llm=0).

**Predicted cliff at 1000 intents:** intent classification on substrate uses prototype-bundle (sparse-bipolar atoms per intent class). Capacity is bounded by Frady-Sommer formula: K_max ≈ N / (k · V · K_SET) at chain-grade noise. With N=8192, K=20 (training samples per intent), at V=50 the ratio = 8192/(2·50·20) = 4.1 (safely in chain-grade). At V=1000 ratio = 0.20 (10x below safe). **Predicted cliff = V ≈ 200-500 intents** for N=8192. At V=1000 expect acc ≈ 0.40-0.55 (degraded but well above chance 1/1000 = 0.001).

**Brain analog:** PFC categorization at ~100s of categories (Bunge/Wallis); higher than this requires HIERARCHICAL category structure.

**Novel angles:**

**Angle 1 — RAISE N (P=0.65):** N=16384 doubles capacity; N=32768 4x. Likely enables 500-1000 intents at acc ≥ 0.65. Build cost: trivial.

**Angle 2 — HIERARCHICAL INTENT (P=0.55):** 2-level. Top-level domain (50 domains) → sub-intent per domain (20 intents). Total = 1000. Brain analog strong. Build cost: MEDIUM (need domain labels).

**Angle 3 — PER-INTENT NEGATIVE-EXEMPLARS (P=0.45):** contrastive training of intent prototypes; subtract average of off-class atoms during prototype construction. Like Foldiak but applied at the intent-prototype level (where Principle O says structure HELPS at use-case).

**Field literature:** large-scale intent classification (Snips: 7 intents; CLINC150: 150 intents) maxes at ~150 well-evaluated; 1000+ is research-grade. Hierarchical helps in BERT-based classifiers.

**Recommended next experiment:** **EXT-3 from pre-spec batch** — `substrate_intent_classifier_v2_production_scale_100plus_intents`. n_intents ∈ {50, 100, 200, 500, 1000} × 3 seeds. Pre-reg HARD bands: HARD_PASS acc ≥ 0.65 at n=500 AND p95 ≤ 5ms.

**P(solve) overall:** ~0.65 with raise-N angle alone; ~0.75 if combined with hierarchical.

---

### 2f. Continual learning at 1000+ cycles

**Status:** chain-grade at 200 cycles (a8_continual_writes; forget=0.006). 30-day stream chain-grade (`exp_substrate_continual_learning_30day_realistic_stream_v1` HARD_PASS retention=0.999 new_recall=1.000 cross_day_chain=1.000). **HOWEVER:** `exp_substrate_continual_learning_spectrum_v1` HARD_FAIL (forgetting=0.650 > HF=0.5; transfer=0.000) — CL primitives DON'T COMPOSE when full CLS-replay+CFRPE-online stacked.

**Barrier mechanism:** the 200-cycle chain-grade was for SINGLE-mechanism CL (append-only writes). The 30-day stream was simple ingestion. The spectrum cell tested COMPOSITION (CFRPE + CLS-replay + STDP) and FAILED.

**Predicted cliff:** for single-mechanism append-only, the cliff is at capacity-saturation. With V·K/N atoms threshold, at N=8192 V=4000 K=20 → 80000 atoms cap = ~400 cycles of 200 atoms each. Beyond that, forgetting compounds.

**Brain analog:** Squire-Wixted CLS theory (hippocampus + cortex); sleep replay consolidates. Brain DOES handle thousands of cycles via this mechanism. Substrate has the hippocampus side (append-only CL); the cortical-consolidation side may be the missing piece.

**Novel angles:**

**Angle 1 — RAISE N + EXTEND CYCLES (P=0.55):** N=32768 at 5000 cycles. Linear scaling of capacity bound. Likely chain-grade.

**Angle 2 — CLS-REPLAY WITH SEPARATE-W (P=0.40):** the spectrum-HARD_FAIL says single-W CLS-replay fails. SEPARATE-W (Option C from Barrier 1) might work. Build cost: HIGH (new primitive).

**Angle 3 — DECAY-AWARE WRITES (P=0.35):** brain consolidates by REPEATED exposure during sleep; substrate could simulate by re-writing high-importance facts. Trivial implementation.

**Field literature:** continual learning is a deep open problem in deep learning (DeepMind's Progress & Compress 2018; lifelong learning surveys). Substrate's append-only mechanism PER SE is unusual; literature shows replay-based methods scale to thousands of tasks with some forgetting.

**Recommended next experiment:** **EXT-4** — `substrate_continual_learning_v2_1000plus_cycles_scale`. n_cycles ∈ {200, 500, 1000, 2000, 5000} × 3 seeds. forget rate measured every 100 cycles. HARD_PASS: forget ≤ 0.05 at 5000 cycles.

**P(solve) overall:** ~0.55 for single-mechanism scale-up; ~0.40 for composed CL (spectrum-HARD_FAIL needs deeper rethink).

---

### 2g. Working memory K > 32 with cleanup

**Status:** chain-grade at K=32 (recall=1.000 at sigma=1.0); degrades at K=128 (0.95) and K=256 (0.64) per WM-HRR-slots-PRODUCTION cell. Cleanup-per-slot UNTESTED.

**Barrier mechanism:** WM-HRR is FHRR superposition of `(slot_role × item_atom)` pairs; recall reads `superposition × slot_role^{-1}` then cleanup. At K=32 superposition crosstalk is below cleanup-rescue threshold; at K>32 crosstalk dominates cleanup capacity.

**Brain analog:** Miller 7±2 for ATTENTIONAL WM (not storage); brain hippocampus + parietal cortex can hold ~30 chunks with chunking. Substrate at K=32 ALREADY EXCEEDS brain WM by ~4x.

**Predicted cliff:** with per-slot cleanup, the cleanup re-baselines each slot before write-back. This should rescue K=128 to ≥0.95 and K=256 to ≥0.80. At K=512 still expect degradation.

**Novel angles:**

**Angle 1 — CLEANUP-PER-SLOT-ON-READ (P=0.65):** read slot → cleanup → use. Substrate has all parts. Build cost: trivial.

**Angle 2 — ITERATED-CLEANUP-PER-SLOT (P=0.55):** read slot → cleanup → write back → cleanup again next iteration. Brain's continuous WM refresh analog.

**Angle 3 — RAISE N (N=8192) (P=0.50):** capacity scales as N; doubling N should double K-ceiling.

**Field literature:** Plate (1995) HRR limits are well-known; cleanup-per-slot is standard practice in production HD-computing systems.

**Recommended next experiment:** **EXT-6** — `substrate_working_memory_v2_extended_K_with_cleanup_per_slot`. K ∈ {32, 64, 128, 256, 512} × 2 modes (NAIVE vs CLEANUP_PER_SLOT) × 3 seeds at N=4096. HARD_PASS: CLEANUP arm ≥ 0.95 at K=128.

**P(solve) overall:** ~0.65. Strong because all primitives chain-grade; just need composition.

---

### 2h. NAMED corpus expansion for distill-verify v3

**Status:** Cell 3 v2 HONEST_NEGATIVE today (Skunkworks); only 1 NAMED operator across 20 dup-groups (not 6 as Director framed); named-discriminator dimension structurally untestable.

**Barrier mechanism:** distill-verify needs ≥6 NAMED operators (per Skunkworks revival path) to test the named-discriminator axis. Current corpus has 1. Source for additional NAMED operators in substrate?

**Substrate-mining for NAMED operators (the load-bearing question):**

Substrate KG already has structured relations:
- KG (FB15k-237) has named relations: `/location/location/contains`, `/people/person/profession`, etc. ~237 distinct relations
- ConceptNet has named relations: `IsA`, `PartOf`, `RelatedTo`, etc.
- HotpotQA QA pairs have implicit named operators in question structure

**Substrate-native NAMED operator sources (per substrate mine):**
1. **KG relation-types as NAMED operators** — already in store; just need to surface them as the "distill-verify-NAMED" corpus
2. **Predicate auto-discovery from substrate's own structured relations** — Skunkworks audit chain has predicate types
3. **Sequence-binding patterns from c3 cell** — could be sources of named-temporal operators

**Recommended next experiment:** **`substrate_distill_verify_v3_named_corpus_from_KG_relations`** — pull 10-20 NAMED relation-types from KG store; rebuild distill-verify corpus with proper NAMED-stratified split + disjoint folds; HARD_PASS at named_distill_ratio ≥ 0.70 cv ≤ 0.15. Build cost: LOW (existing primitives, just corpus rebuild).

**P(solve) overall:** ~0.60. Distill-verify mechanism IS real (bare-typed-only already chain-grade-eligible); just blocked on corpus.

---

### 2i. Refuse-gate nonlinear-readout chain-grade

**Status:** MEASURED_MECHANISM today (Skunkworks); saturated at synthetic absent regime (gap_refuse=1.000 cv=0.000 at 42% of operating points).

**Barrier mechanism:** synthetic absent regime is too discriminating from synthetic present regime; nonlinear-readout concentration-gate works "for free" at this synthetic distribution.

**The harder test (per Skunkworks revival path):** real-bge held-out with embedding distribution drift. Substrate has bge embeddings via the Pythia ingest pipeline; could rebuild the absent set with real held-out queries.

**Novel angle:** **REAL-BGE HELD-OUT REFUSE-GATE (P=0.45):** rebuild absent-set from real bge-embedded queries that DRIFT from training distribution; test concentration-gate at this distribution. If chain-grade, refuse-gate nonlinear becomes 4th chain-grade refuse-mechanism.

**P(solve) overall:** ~0.45. **Lower-leverage** because substrate already has 3 chain-grade refuse mechanisms (audit-based, graph-health, CSP) — this is a 4th option not a needed primitive.

**Recommendation:** DEFER unless substrate-product application demands this specific mechanism.

---

### 2j. b_delta finite-extension chain-grade

**Status:** MEASURED_MECHANISM today (Skunkworks); extension=1.0 saturated because nl_high=1.0 never cliffs in M ∈ [64, 1024] at N=1024.

**Barrier:** to measure UPPER bound of nonlinear capacity, need M >> N. Test at M=4N or M=8N.

**Novel angle:** **EXTENDED M SWEEP (P=0.55):** M ∈ {1024, 2048, 4096, 8192} at N=1024. Find nonlinear cliff. Chain-grade only if cliff measured.

**P(solve) overall:** ~0.55. **Low-leverage** because b_delta is a parameter-tuning result, not a load-bearing primitive.

**Recommendation:** DEFER. Mechanism IS real (8x lift bipolar at M=1024 N=1024); upper-bound measurement is interesting-not-load-bearing.

---

### 2k. Long-depth sequence binding (c3 cell)

**Status:** chain-grade at short depth (atom 586). Long-depth UNKNOWN.

**Predicted cliff:** sequence binding depth scales as log(N/V) at chain-grade noise. At N=8192 V=200, log(40) ≈ 5.3 depth max. At depth 100 expect HARD_FAIL.

**Brain analog:** CA3 theta-gamma phase precession holds ~7-9 sequence items in working memory; long-term sequence is consolidated via slow synaptic learning.

**Novel angle:** **LONG-DEPTH WITH CHUNKING (P=0.50):** break long sequence into chunks of depth 5; bind chunks hierarchically. Brain mechanism strong; substrate has all primitives.

**Recommendation:** DEFER unless application demands long-depth sequence. Substrate-product story doesn't currently need this.

---

### 2l. NESS envelope beyond alpha=0.7

**Status:** chain-grade alpha ∈ [0.3, 0.7] (ext_hopfrac=1.0). Beyond unknown.

**Predicted:** at alpha=0.85, walks become more concentrated; cleanup-extension may struggle as candidate cluster becomes denser. At alpha=0.95 expect ext_hopfrac drops.

**Novel angle:** **EXT-7 from pre-spec batch.** alpha ∈ {0.7, 0.8, 0.85, 0.9} × 3 seeds. HARD_PASS: ratio_to_eq ≥ 2.0 AND ext_hopfrac ≥ 0.95 at alpha=0.85.

**P(solve) overall:** ~0.50. Medium-leverage; NESS already chain-grade — this extends operating range.

---

### 2m. Foldiak v3 redesign

**Status:** v1 + v2-surgical HARD_FAIL (axis-flip bug killed both). v3 redesign deferred.

**Barrier:** v1 placed homeostatic theta on per-row (input-dim) axis; should be per-output-dim. v2 attempted surgical fix; STILL failed (rank-1 collapse).

**Field literature (Foldiak 1990 / Vincent 2010 / Hyvarinen 2002):** Foldiak's original anti-Hebbian decorrelation requires:
1. Per-output-dim threshold theta
2. Bounded update step (anti-Hebbian ∝ -post · post_neighbors)
3. Initialization avoiding rank-1 attractor

**Novel angle:** **v3 with all 3 corrections (P=0.30):** per-output-dim theta; bounded update; orthogonal initialization. Risk: rank-1 attractor is the GENERIC failure mode of Hebbian-family without strong regularization. Substrate at production V may still collapse.

**Combined with today's v2c V=10000 HARD_FAIL_NULL:** even WITHOUT Foldiak (NO_FOLDIAK arm), all 4 biology-native encoders at V=10000 produced bpc-lift = 0.00 vs random. **This is the strong negative result — Mu-Viswanath confirmed at production V.** Foldiak v3 would join a CLOSED arc.

**Recommendation:** **CLOSE Foldiak with negative-in-regime finding** (v2c V=10000 confirms biology-native encoders don't beat random at production V; Foldiak is one such; redesign won't reverse Mu-Viswanath).

**P(solve) overall:** ~0.15 (combined with biology-native CLOSURE).

---

### 2n. Heterogeneous-routing composition

**Status:** v1 failed; Cell 2 v6 SEGREGATED_DUAL_W LANDED MIDDLE_BAND_INTER_GAP today (SEGREG+GATE=7.4837 OUTSIDE all bands; uni=7.738 BASE=7.3124 FREQ_DEEPER=7.1647). **Skunkworks brain-analog-doesn't-transport ruling expected.**

**Barrier:** segregated dual-W at substrate scale doesn't beat shared-W BASE. when_vs_what_corr=0.3113 (segregated stores correlate at 31% — not orthogonal). The brain analog requires TRUE orthogonality which substrate's bipolar codes don't provide at this composition.

**Novel angles:** all SEGREGATED variants are in this MIDDLE_BAND envelope. Heterogeneous-routing-with-FREQ_ROUTED_DEEPER (use Cell 2 v5 chain-grade mechanism instead of SEGREGATED) might compose.

**Recommendation:** **DEFER heterogeneous-routing.** Substrate-product has FREQ_ROUTED_DEEPER + MULTIPLICATIVE_LEVER as Stage 2 mechanisms; SEGREGATED is the failed third candidate. The composition arc moves to "compose two chain-grade Stage 2 mechanisms" not "find a new mechanism."

**P(solve) overall:** ~0.20. Low.

---

### 2o. Generation g1b at LM-density

**Status:** g1b capacity sweep `exp_g1b_capacity_sweep_v1` LANDED HARD_PASS today — "chain-grade evidence above by-construction-saturation. n_points_at_bar=6/6; headroom_pt=6403 pairs; graceful=True; spread_preserved=True. coh_arm4@T8 by n_pairs=[...all 1.00 except 6403:0.94]"

**Update:** the saturation tier from prior framing was today PROMOTED via capacity-sweep. Density up to 6403 pairs verified chain-grade-eligible.

**Recommendation:** **FOLD into chain-grade inventory.** Skunkworks tier-rule pending; default chain-grade-likely. Generation primitive operating envelope: up to ~6400 (concept × time) pairs.

**P(solve) overall:** RESOLVED (chain-grade at this envelope; LM-density frontier is a separate Stage 4 question that USER deferred).

---

## Section 2 — Category 3 (smoke-only backlog) triage — top 10

Audit returned 229 strategic smoke-only HARD_PASS cells. Filtered by chain-grade-eligibility (mechanism likely chain-grade if upgraded to 3 seeds + full run; not by-construction-saturation; not superseded by recent work):

**Top 10 chain-grade-eligible for next smoke-to-full upgrade batch:**

| # | Anchor | Age | Why eligible |
|---|---|---|---|
| 1 | `exp_program_exec_audit_v1` | 23.9d | program-execution audit; smoke 2-seed; tier-3 audit primitive expansion |
| 2 | `exp_program_exec_audit_chain_v1` | 23.7d | program-exec audit at depth; composes with #1 |
| 3 | `code1_function_compose_cpu_v1` | 14.5d | function-composition primitive; substrate-product-relevant Stage 2 |
| 4 | `code6_algorithm_compose_cpu_v1` | 14.5d | algorithm-composition; pair with #3 |
| 5 | `set_algebra_composability_v1` | (from yesterday's batch) | union/Jaccard/symdiff MAE<0.05; load-bearing for KG set ops |
| 6 | `governance_cap_cert_v1` | (from yesterday's batch) | capacity-certificate validated; cert-grade primitive |
| 7 | `single_shot_attention_multihop_v1` | 17.8d | single-shot attention multi-hop; might lift Barrier 1 (novel angle) |
| 8 | `causal_audit_chain_depth_v1` | 18.3d | audit chain at depth; tier-3 audit expansion |
| 9 | `cleanup_confidence_roc_cpu_v1` | 17.5d | cleanup-confidence ROC (relates to CSP composition) |
| 10 | `conformal_reject_option_v1` | (from yesterday's batch) | conformal coverage guarantee; refuse-gate primitive |

**Likely-superseded / DEFER from audit (do NOT upgrade):**
- `dense_kv_whitening_revival` — HARD_FAIL today; already known
- `g1_encoder_geometric_alignment_audit_v1` — superseded by today's Wave D closure
- `n1b_pythia2p8b_kv_capacity_*` — superseded by today's anisotropy work
- `wave4_full_streaming_composition_with_audit_v1` — old arc; superseded by Cell A
- `comp23_multihop_composites_cpu_v1` — superseded by Barrier 1 closure
- `frisson_cleanup_margin_cpu_v1` — research-grade only; not load-bearing

**Method:** triage by chain-grade-eligibility = (a) primitive mechanism is real, (b) not by-construction-saturation, (c) substrate-product positions need this, (d) full re-run cost ≤ 1h.

---

## Section 3 — Recommended dispatch order (next 7-10 cells)

Given spawn budget = NO sub-agent spawns (Fix #27 main-thread); cells dispatched via exp_dev (currently busy on anisotropy v2). Sequenced for highest-leverage-first:

### TIER A — HIGHEST leverage (must dispatch in next wave)

1. **`substrate_anisotropy_rescue_4arm_v2_calibrated_full`** (item 2b) — IN FLIGHT (exp_dev just spawned). Highest leverage because anisotropy is the real-data substrate bottleneck and Charikar=0.982 smoke is the strongest positive signal. **WAIT for landing.**

2. **EXT-1: `substrate_stage3_integrated_audit_device_demo_v2_production_scale`** (item 2c) — production V scale-up of today's Cell A. GPU overnight_queue. Pre-reg filed. ~2-4h compute. **HIGHEST product-impact if HARD_PASS.**

3. **EXT-3: `substrate_intent_classifier_v2_production_scale_100plus_intents`** (item 2e) — intent scaling 50 → 1000. local_cpu_queue. ~30min compute. **Highest application-leverage.**

### TIER B — HIGH leverage (dispatch next wave after Tier A)

4. **`substrate_multihop_csp_gated_iterated_cleanup_v1`** (item 2a Angle 1) — novel Barrier-1 angle composing chain-grade primitives (CSP + iterated-cleanup + WM-scaffold). local_cpu_queue ~30min. P=0.35; high VALUE if hits.

5. **EXT-6: `substrate_working_memory_v2_extended_K_with_cleanup_per_slot`** (item 2g) — WM K>32 via cleanup-per-slot. local_cpu_queue ~20min. P=0.65 strong.

6. **`substrate_partition_routing_hierarchical_2level_v1`** (item 2d Angle 1) — 2-level routing for M=10M KG. GPU overnight_queue ~3-6h. P=0.55.

### TIER C — MEDIUM leverage (dispatch when bandwidth opens)

7. **EXT-4: `substrate_continual_learning_v2_1000plus_cycles_scale`** (item 2f) — continual learning to 5000 cycles. local_cpu_queue ~1h. P=0.55.

8. **`substrate_distill_verify_v3_named_corpus_from_KG_relations`** (item 2h) — pull NAMED operators from KG. local_cpu_queue ~20min. P=0.60.

9. **`backlog_smoke_to_full_batch_program_exec_audit_v1_and_v2`** (Section 2 backlog #1+#2) — paired program-exec audit chain-grade upgrade. local_cpu_queue ~30min each.

10. **EXT-5: `substrate_compose_freq_routing_v6_N16384_N32768_extension`** (Stage 2 N-scaling) — extends Stage 2 envelope. GPU overnight_queue ~3-6h.

### Dispatch budget reasoning

- **Tier A (3 cells)** dispatched as soon as exp_dev frees from anisotropy v2; ~30min landing + tier-rule
- **Tier B (3 cells)** dispatched after Tier A lands (next ~12h)
- **Tier C (4 cells)** as backlog for overnight + tomorrow

**Total budget:** ~10-15h GPU + ~4-6h local CPU spread across 24h. Within standing autonomy.

---

## Section 4 — Brain-prior cross-check (per item)

| # | Item | Brain mechanism | Substrate path aligned? | Notes |
|---|---|---|---|---|
| 2a | Multi-hop QA | PFC + hippocampus + ACC confidence | PARTIAL — has parts (WM=PFC, cleanup=hippocampus, CSP=ACC) but never composed correctly | Angle 1 (CSP-gated) is the brain-aligned composition |
| 2b | Anisotropy rescue | Retinal whitening, V1 gain control, sparse fan-in cerebellar | PARTIAL — substrate tries whitening (FAIL) and sparse fan-in K=5 (partial); cerebellar-with-expansion not tried | Cerebellar literature (Litwin-Kumar) prescribes 200x expansion not 1x |
| 2c | Production V audit | Brain audits via ACC + perirhinal (familiarity) | YES — substrate has audit primitive + CSP + intent | Envelope extension only |
| 2d | M=10M KG | Hippocampal indexing into cortical regions (Goyal/Buzsáki 2021) | PARTIAL — hierarchical indexing matches brain; substrate has single-level only | Hierarchical is brain-correct |
| 2e | 1000 intents | PFC categorization at ~100s | YES with hierarchy | Hierarchical works in brain |
| 2f | Continual 5000-cycle | CLS (Squire-Wixted): hippocampus + cortex | PARTIAL — substrate has hippocampus side only | Cortical consolidation primitive missing |
| 2g | WM K>32 | Brain WM ~30; substrate already exceeds | N/A — substrate is super-human here | Cleanup-per-slot is mechanistically aligned with brain WM-refresh |
| 2h | NAMED corpus | N/A (methodology) | YES | KG-relation source is appropriate |
| 2i | Refuse nonlinear | ACC conflict detection at noisy distributions | YES | But low-priority since 3 refuse-mechs already chain-grade |
| 2j | b_delta capacity | N/A (architecture param) | N/A | Defer |
| 2k | Long-depth sequence | CA3 phase precession at ~9 items; long via consolidation | YES with chunking | Brain mechanism strong |
| 2l | NESS alpha>0.7 | Hippocampal walk concentration during memory recall | YES | Extends envelope |
| 2m | Foldiak v3 | V1 lateral inhibition | NO — Mu-Viswanath says less structure better at basis | CLOSE negative-in-regime |
| 2n | Heterogeneous routing | Cortical layer hierarchy | NO at SEGREGATED-W substrate scale; YES via FREQ_ROUTED_DEEPER | Use chain-grade alternative |
| 2o | Generation density | CA3→CA1 sequence replay | YES | Today's capacity-sweep is chain-grade |

**Summary:** brain-prior STRONG for items 2a, 2c, 2d, 2e, 2g, 2k, 2l, 2o. Brain-prior NEGATIVE for items 2m (Foldiak) and 2n (SEGREGATED). Brain-prior NEUTRAL for 2b (multiple brain analogs; cerebellar is strongest), 2f (composition open), 2h (methodology), 2i/2j (low-leverage).

---

## Section 5 — Field literature cross-check (harder items)

### Anisotropy (item 2b)
- **Ethayarajh 2019** — transformer embeddings highly anisotropic at most layers
- **Mu-Viswanath 2017** — whitening rescues anisotropy in word embeddings
- **Dasgupta 2017 (fly LSH)** — sparse random projection + WTA beats LSH; cerebellar-inspired
- **Litwin-Kumar 2017** — cerebellar fan-in K~5 with 200x expansion is optimal for olfactory similarity
- **Karpukhin 2020 (DPR)** — learned dense retrieval beats sparse only after contrastive
- **2024 ColBERT-v2, SPLADE** — sparse-dense hybrid is current SOTA for retrieval at scale
- **Substrate position:** matches literature — learned > whitening > random; sparse-with-expansion is the right next angle.

### Multi-hop (item 2a)
- **Yang 2018 HotpotQA** — benchmark for 2-hop; baseline transformer ~70%
- **Yao 2023 Tree-of-Thought** — branching with self-eval lifts LLM multi-hop
- **HopRAG 2024** — retrieval-augmented multi-hop; 70%+ on HotpotQA
- **Eichenbaum 2018** — hippocampus indexing multi-hop is via PFC + episodic memory composition
- **Substrate position:** Substrate has the parts; needs the CSP-gated composition. Confidence-gating IS the brain-aligned pattern.

### Encoder (item 2m + Wave D closure)
- **Olshausen-Field 1996** — sparse coding is V1-correct
- **Plate 1995** — HRR/FHRR binding capacity bounds
- **Mu-Viswanath 2017** — anisotropy hurts retrieval at basis
- **Recent (2024)** — k-WTA sparse coding (DeepMind's Top-K MoE) revived as efficient; substrate's f=0.02 sparse-bipolar is in this regime
- **Substrate position:** Wave D biology-native v2c V=10000 HARD_FAIL_NULL CONFIRMS Mu-Viswanath at production V. Literature converges with substrate finding.

### Continual learning (item 2f)
- **Kirkpatrick 2017 (EWC)** — elastic weight consolidation; established forgetting-mitigation
- **DeepMind Progress & Compress 2018** — progressive nets scale to thousands of tasks
- **Squire-Wixted CLS** — brain's continual learning via hippocampus + cortex
- **Substrate position:** append-only is novel; spectrum-HARD_FAIL says composition with CFRPE/STDP doesn't transport — needs simpler scale-up first.

### KG at scale (item 2d)
- **HNSW (Malkov 2020)** — hierarchical small-world graphs for billion-scale ANN
- **ScaNN (Google 2020)** — anisotropic quantization; 10B-scale
- **Substrate position:** hierarchical routing is the standard literature pattern; substrate's single-level routing at M=1M is in research-grade territory.

---

## Discipline checks (per Q-protocol)

- **Default UNDER-claim (Fix #28):** all P(solve) values include 0.15-0.25 lit-scan deflation; novel-synthesis capped at 0.50
- **Per-arm metrics not verdict_msg:** v2c V=10000 HARD_FAIL_NULL verified via per-arm bpc-lift readings; segregated dual-W MIDDLE_BAND verified via per-arm bpc readings (SEGREG=7.3466 vs BASE=7.3124)
- **Substrate-mine FIRST (USER 2026-06-22):** distill-verify NAMED source mined to KG relations + ConceptNet (substrate-mining pass before extrapolation)
- **Brain HIGH-prior on brain-grounded (USER 2026-06-23):** items 2a/2d/2e/2g/2k/2l flagged STRONG brain-aligned with P-prior 0.45-0.65 not 0.30
- **Cite per-arm not summary verdict:** all P(solve) tied to per-arm cell metrics where available
- **Verify-the-referent:** Wave D v2c V=10000 confirmed read from data/exp_..._v2c_V10000_only_closure_smoke/metrics.json HARD_FAIL_NULL all arms

## Files referenced

- `data/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure_smoke/metrics.json` — v2c HARD_FAIL_NULL (Wave D biology CLOSED)
- `data/exp_substrate_stage3_integrated_audit_device_demo_v1/metrics.json` — Cell A HARD_PASS chain-grade
- `data/exp_substrate_compose_segregated_dual_W_context_gated_v1/metrics.json` — Cell 2 v6 MIDDLE_BAND_INTER_GAP
- `data/exp_substrate_refuse_gate_domain_aware_v1/metrics.json` — MIDDLE_BAND_COMPOSITION_TIES_BEST_SINGLE
- `data/exp_g1b_capacity_sweep_v1/metrics.json` — g1b HARD_PASS chain-grade-eligible
- `data/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing/metrics.json` — Hub-spoke v3 HARD_FAIL all arms at unigram floor
- `data/exp_substrate_continual_learning_spectrum_v1/metrics.json` — HARD_FAIL CL composition
- `data/exp_substrate_continual_learning_30day_realistic_stream_v1/metrics.json` — HARD_PASS single-mechanism CL
- `data/exp_kmax_ness_envelope_corrected_v1/metrics.json` — NESS HARD_PASS chain-grade-eligible
- `data/exp_clean_encoder_eval_harness_v1_smoke/metrics.json` — encoder eval Word2Vec HARD_PASS
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` — comparator HARD_FAIL
- `notes/research_envelope_extension_prespec_batch_2026-06-25.md` — EXT-1..7 pre-specs
- `notes/skunkworks_tier_ruling_4cell_smoke_to_full_VET_batch_2026-06-25.md` — today's rulings

## Bottom line for USER

Substrate basis effectively finalized. Of 15 open Category-2 items, drill recommends:
- **3 newly-CLOSED today** (Stage 3 integrated demo, g1b, Wave D biology-native)
- **3 HIGHEST-leverage next dispatch wave** (anisotropy v2 IN FLIGHT, EXT-1 production V, EXT-3 1000-intents)
- **3 HIGH-leverage next-after wave** (CSP-gated multi-hop, WM K>32, hierarchical routing M=10M)
- **3 DEFER as low-leverage** (refuse-gate nonlinear, b_delta finite-ext, Foldiak v3, heterogeneous SEGREGATED)
- **3 MEDIUM-leverage backlog** (continual 5000-cycle, distill-verify NAMED, smoke-backlog program-exec audit)

Recommended dispatch order: Tier A (3 cells; ~30min total CPU + 2-4h GPU overnight) → Tier B (3 cells; ~30min CPU + 3-6h GPU overnight) → Tier C (4 cells; ~3h CPU + 3-6h GPU). Total ~10-15h compute. Within standing autonomy.

— Research (Director)
