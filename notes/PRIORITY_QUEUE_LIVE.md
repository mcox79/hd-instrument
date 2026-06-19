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

### Slot 3 (DONE; HP at ~12x): ~~`substrate_sparse_pattern_coding_vs_dense_alpha_n4096_n16384_v1`~~
- **Status:** DONE 2026-06-06 09:40 -- sparse_alpha ~0.30 vs dense_alpha ~0.025 at N=1024 smoke = **~12x at f=0.10**
- **Confirmation:** sparse-Hopfield linear-noise regime rescue WORKS empirically (4x classical bound exceeded)
- **Key fix Exp-Dev caught:** single-step retrieval (iterating filled sparse zeros with +/-1 -> false 0)
- **Full run queued:** N=4096 + N=16384 to confirm at scale
- **Compound implication:** if Slot 8 ETF + sparse compound holds, total capacity gain ~100x+ at N=4096

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
- **2x rescue drill landed 2026-06-06 09:50:** norm-gate algebraically broken; **per-cluster stratified keep is the rescue** (100% coverage guaranteed, 100-1000x speedup; P_deflated=0.65); entropy-gate also biased (60-75%); random sampling adequate (>90% at large M; P_deflated=0.55)

### Slot 10 (SMOKE HARD_PASS; full queued): ~~`substrate_etf_hadamard_n_sweep_capacity_v1`~~ -- partial
- **Status:** SMOKE HP 2026-06-06 ~12:15 -- Hadamard/random ratio 8.02x@N1024, 8.03x@N2048 -- **lift is FLAT across N**
- **Architecture confirmed:** W-free Hopfield allows full sweep {4096, 16384, 32768, 65536}
- **Strategic CONTRAST with Slot 14:** synthetic-keys lift PERSISTS (8x flat across N) while real-encoder lift PLATEAUS at 1.29x. Confirms drill A's H2 hypothesis (Hadamard saturation is real-encoder specific; synthetic random-bipolar has no pre-structure for Hadamard to "rediscover")
- **If full holds >=5x at N=65536:** Phase 3 linear capacity gains ~10x lift -> ~26,000 facts/substrate (synthetic-style path)
- **Full queued:** CPU sweep across all 4 N-points

### Slot 12 (SMOKE MIDDLE; full queued): ~~`substrate_per_cluster_stratified_extraction_v1`~~ -- WORKING extraction rescue
- **Status:** SMOKE MIDDLE 2026-06-06 ~12:15 -- 100% coverage by construction; speedup bounded by N_tok/n_clusters (~21x at smoke; production target 100-1000x)
- **Confirms drill C prediction:** per-cluster stratified is the working extraction rescue (vs Slot 13 random which HFed)
- **Full queued:** N_tok=40k, v_c up to 4096 -- production-scale speedup measurement

### Slot 13 (SMOKE HARDFAIL): ~~`substrate_concept_uniform_random_extraction_v1`~~ -- random doesn't preserve coverage
- **Status:** SMOKE HARDFAIL 2026-06-06 ~12:15 -- Coverage 0.60 at 10x speedup; 0.16 at 100x speedup
- **Finding:** random sampling misses rare concepts (uneven concept distribution; random sampling has probability mass on common concepts)
- **Clean comparative:** norm gate (Slot 6 HF) drops 50% via low-norm bias; random (Slot 13 HF) misses 84% at 100x via probability; per-cluster stratified (Slot 12 MIDDLE-working) gives 100% by construction. The rescue is stratified.

### Slot 12-orig (NEW; from extraction gate rescue drill): `substrate_per_cluster_stratified_extraction_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke MIDDLE: 100% coverage, speedup~N/clusters); queued CPU
- **Wall:** ~30 min CPU
- **Source:** norm-gate HARDFAIL rescue drill (09:50)
- **Why:** RECOMMENDED rescue. Pre-compute VQ assignment (cheap); within each VQ cluster keep top-K tokens; guarantees 100% coverage by construction; 100-1000x speedup
- **Capability advanced:** PP-22 extraction sparse-gating (rescues the $333k -> $31 cost story)
- **HP threshold:** >=95% concept coverage AND >=100x speedup at production-class settings
- **Strategic value:** the "$333k -> $31" cost-reduction story now has a verified gating mechanism

### Slot 13 (NEW; secondary rescue): `substrate_concept_uniform_random_extraction_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_FAIL: random sampling loses coverage 0.60@10x; stratified is the rescue); queued CPU
- **Wall:** ~20 min CPU
- **Source:** norm-gate HARDFAIL rescue drill (09:50)
- **Why:** simplest rescue path; concept-uniform random sampling guarantees coverage by construction
- **Capability advanced:** PP-22 secondary
- **HP threshold:** >=90% coverage at 10-100x speedup
- **Strategic value:** floor case; cheap to validate as fallback

### Slot PSE1 (NEW; from drill C; sqrt-K allocation production architecture): `substrate_extraction_sqrt_K_allocation_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (un-parked; rebuilt with VQ-codebook-fidelity metric per Research spec; smoke MIDDLE sqrt_K 1.05x uniform); queued CPU
- **Wall:** ~30 min CPU
- **Source:** 2x drill C (per-cluster stratified operational depth) at 11:50
- **Architecture:** sqrt-K allocation K_c = M * sqrt(n_c) / sum(sqrt(n_c)) vs uniform-K baseline at production-scale settings (V_c=1M; M=10M)
- **Why:** Neyman-optimal proxy without needing per-cluster sigma_c. Avoids uniform-K over-sampling of small clusters and prop-K zeroing out rare clusters.
- **Capability advanced:** PP-22 production extraction architecture
- **HP threshold:** sqrt-K coverage >=99% AND quality matches uniform-K at half the budget
- **MID:** quality matches at 70-100% budget
- **HF:** sqrt-K fails to match uniform-K at full budget (mechanism doesn't work)

### Slot PSE2 (NEW; from drill C; online streaming stratification): `substrate_online_stratified_extraction_streaming_v1`
- **Wall:** ~45 min CPU
- **Source:** Drill C Sub-question (2) -- online vs offline architecture
- **Architecture:** Vitter stratified reservoir + IVF online VQ assignment (~50000x cheaper than naive) + sliding window for drift
- **Why:** production needs streaming; can't pre-compute full VQ assignment over corpus
- **Capability advanced:** PP-22 production streaming readiness
- **HP threshold:** online quality matches offline within 5% at 100x throughput speedup
- **MID:** within 10%
- **HF:** > 10% degradation (offline-only path needed)

### Slot PSE3 (NEW; CRITICAL from drill C; codebook collapse detection): `substrate_codebook_collapse_monitoring_recovery_v1`
- **Wall:** ~60 min CPU
- **Source:** Drill C Sub-question (6) -- DOMINANT FAILURE MODE
- **Architecture:** 6 monitoring metrics (M1-M6); detection trigger: n_c=0 for 3+ epochs; 3 recovery mechanisms (R1 EMA reinit, R2 OT regularization, R3 perturbation)
- **Why CRITICAL:** dominant production risk per drill C is dead VQ codes, NOT coverage loss. Without monitoring+recovery, extraction silently degrades.
- **Capability advanced:** PP-22 production reliability
- **HP threshold:** detection catches 95% of collapse events within 5 epochs; recovery restores cluster within 10 epochs
- **MID:** detection 70-95% OR recovery 10-20 epochs
- **HF:** detection < 70% OR recovery > 20 epochs
- **Strategic value:** production-deployment gate

### Slot DAMB1 (NEW; HIGHEST PRIORITY -- gating cell from drill A): `substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1`
- **Wall:** ~30 min CPU
- **Source:** 2x drill A (real-encoder cross-N attenuation disambiguation) at 12:00
- **Architecture:** sweep Q_real(N) vs Q_synthetic(N) at fixed alpha, Hadamard codebook; measure curve shape
- **Why CRITICAL:** Algebraic analysis shows H1 (N-dependent noise) predicts SUB-LINEAR decay; H2 (Hadamard N-saturation) predicts LINEAR decay. Different observed shapes pick between hypotheses. **All other real-encoder rescue investments depend on this answer.**
- **Capability advanced:** Phase 4B real-encoder noise-mechanism identification
- **HP threshold for H1:** Q_real / Q_synthetic decays SUB-linearly with N
- **HP threshold for H2:** Q_real / Q_synthetic decays LINEARLY with N
- **Strategic value:** routes ALL subsequent investments (LC2/LC3 vs SRHT vs other)

### Slot DAMB2 (NEW; extends LC1 with N-sweep -- attacks both hypotheses): `substrate_sparse_hadamard_mixture_N_sweep_v1`
- **Wall:** ~30 min CPU (extension to LC1)
- **Source:** Drill A Cell 2 -- SHM attacks BOTH H1 (anisotropy decorrelation) AND H2 (subspace saturation delay)
- **Architecture:** LC1 SHM at N in {384, 1024, 2048} to characterize Q(N) shape vs Hadamard
- **Why:** if Q(N) is FLAT under SHM, SHM ships as single highest-leverage training-free intervention for ALL downstream experiments. Combined H1+H2 attack.
- **Capability advanced:** Phase 4B + Phase 4a infra (training-free codebook)
- **HP threshold:** SHM Q(N) flat across N range AND >= 1.5x Hadamard at N=2048
- **Note:** can be merged with LC1 if Exp-Dev prefers (architecture compatible)

### Slot DAMB3 (NEW; conditional H2 rescue from drill A): `substrate_srht_codebook_N2048_v1`
- **Wall:** ~25 min CPU
- **Source:** Drill A Cell 3 -- SRHT (Subsampled Randomized Hadamard Transform) cheapest H2 rescue
- **Architecture:** SRHT codebook (random sign-flip diagonal + Hadamard); compare vs fixed Hadamard at N=2048 on real and synthetic keys
- **Why:** SRHT converts systematic M^2/N interference to random interference; one-line codebook construction change; zero retrieval changes
- **Capability advanced:** Phase 4B H2-saturation rescue
- **Condition:** Run if DAMB1 shows H2-dominant or mixed
- **HP threshold:** SRHT >= 1.5x Hadamard at N=2048 on REAL keys
- **Strategic value:** trivially ships; no training

### Slot G13 (NEW; from G5 HF -- contradiction detection on order-sensitive encoder): `substrate_kf1_contradiction_detection_order_sensitive_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_FAIL: Pythia negation AUC 0.111, even order-sensitive grounding fails -> needs NLI head); queued GPU
- **Wall:** ~75 min GPU
- **Source:** G5 HARDFAIL (negation AUC=0.034) + same encoder-limit class as G2/G11
- **Architecture:** KF-1 contradiction detection on Pythia/Llama-1b residuals OR with NLI head (e.g., BART-MNLI)
- **Why:** MiniLM negation-insensitive ("X increases Y" ~= "X decreases Y" in bag-of-words embedding); production needs to catch contradictions which are the highest-credibility-risk hallucination class
- **Capability advanced:** PP-3 contradiction detection (critical Phase 4 demo)
- **HP threshold:** negation AUC >= 0.85 with order-sensitive encoder OR NLI head
- **MID:** 0.60-0.85
- **HF:** < 0.60 (even order-sensitive encoders fail; need dedicated NLI)
- **Strategic value:** combined with HOC1+HOC2 (word-order), closes the two-encoder-limit class identified today

### Slot G14 / NEG1 (UPDATED with concrete spec from G5 negation 2x drill landing): `substrate_kf1_deberta_nli_contradiction_v1`
- **Wall:** ~2h CPU (no training required; CPU-eligible)
- **Source:** Slot G13 HF + G5 negation 2x drill (landed 14:00) -- Rank 1 cell (highest P_deflated 0.72)
- **Architecture:** Drop-in `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` cross-encoder; replace MiniLM cosine scorer in KF-1 with contradiction probability
- **Why:** NLI is the STRUCTURALLY CORRECT rescue (G13 confirmed embedding-grounding fundamentally cannot catch negation); DeBERTa-v3-large benchmarked at 91.2% MNLI / 70.2% ANLI
- **Capability advanced:** PP-3 contradiction detection via NLI
- **HP threshold:** AUC >= 0.85 on TruthfulQA-style; AUC >= 0.90 on easy negatives
- **MID:** 0.70-0.85 TruthfulQA-style; **HF:** < 0.60 TruthfulQA-style OR < 0.80 easy
- **P_deflated:** 0.72

### Slot NEG2 (NEW; from G5 drill Rank 2 -- antonym coverage): `substrate_kf1_polarity_adapter_v1`
- **Wall:** ~30 min CPU (training minutes; inference zero overhead)
- **Source:** G5 negation 2x drill Rank 2
- **Architecture:** diagonal re-weighting on 384 MiniLM dims using 200-1000 negation-flip contrastive pairs; frozen backbone
- **Why:** cue features cannot detect antonym-based negation (no "not" token); polarity adapter re-weights negation-sensitive dimensions
- **Cite:** arXiv:2504.00584 (+14.52% on SemAntoNeg with this approach)
- **Capability advanced:** PP-3 antonym coverage
- **HP threshold:** AUC >= 0.80 explicit+antonym combined; AUC >= 0.92 easy (regression check)
- **MID:** 0.65-0.80
- **HF:** < 0.55 antonym-only OR < 0.88 easy
- **P_deflated:** 0.55

### Slot NEG3 (NEW; from G5 drill Rank 3 -- explicit-token baseline): `substrate_kf1_negation_cue_features_v1`
- **Wall:** <30 min CPU (string matching + small MLP)
- **Source:** G5 negation 2x drill Rank 3 -- baseline / ablation
- **Architecture:** concat 20-dim negation cue vector (has_not / has_no / has_never / has_n't / etc.) + MLP head ~80k params
- **Why:** cheap ablation; explicit-token negation should be caught; ~60% structural ceiling
- **Capability advanced:** PP-3 explicit-token negation
- **HP threshold:** AUC >= 0.70 explicit subset
- **MID:** 0.55-0.70
- **HF:** < 0.45 (adds noise; discard if test set is mostly antonym)
- **P_deflated:** 0.48

### Slot NEG4 (NEW; from G5 drill Rank 4 -- PRODUCTION recipe): `substrate_kf1_hybrid_nli_bigram_pythia_v1`
- **Wall:** GPU preferred for DeBERTa throughput; CPU feasible at small N
- **Source:** G5 negation 2x drill Rank 4 -- integration test
- **Architecture:** late fusion of (a) DeBERTa NLI contradiction, (b) word-bigram TF-IDF miss (HOC1 signal), (c) Pythia residual perplexity delta; tune alpha/beta/gamma on held-out
- **Why:** negation + word-order have DIFFERENT dominant signals; weighted sum covers both adversarial classes + easy baseline
- **Cite:** AlignScore arXiv:2305.16739 (best AUC on 4/6 SummaC factual consistency with similar fusion)
- **Capability advanced:** PP-3 PRODUCTION hallucination scorer (Phase 4 v3)
- **HP threshold:** Combined adversarial AUC >= 0.88; TruthfulQA-style >= 0.85; word-order >= 0.88
- **MID:** HP1 [0.75, 0.85) AND word-order [0.78, 0.88)
- **HF:** Combined adversarial < 0.80 OR easy < 0.97
- **P_deflated:** 0.62
- **Condition:** Run after G14/NEG1 confirms NLI signal (AUC >= 0.70 min)

### Slot G15 (NEW; from G8 HP + CLOUD-1 connection): `substrate_last_token_vs_whitening_mean_pool_v1`
- **Wall:** ~45 min GPU
- **Source:** G8 + CLOUD-1 are SAME finding from different angles -- mean-pool causal LM is broken
- **Architecture:** compare 3 paths to usable causal-LM substrate: (a) last-token pool no whitening, (b) mean-pool with ETF whitening, (c) last-token + whitening (combined)
- **Why:** are last-token and whitening EQUIVALENT in effect (both fix anisotropy) or COMPLEMENTARY (combined gives more)?
- **Capability advanced:** Phase 4 production architecture clarity (causal-LM substrate recipe)
- **HP threshold:** (c) combined > max((a), (b)) by >=20% capacity (complementary mechanisms)
- **MID:** (c) approximately = max (equivalent mechanisms; pick whichever is cheaper)
- **HF:** (c) < max (interfering mechanisms)

### Slot G16 (NEW; from G7 HF subsumption -- explicit subsumption test at scale): `substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1`
- **Wall:** ~60 min GPU (full N_enc=10000; uncensored)
- **Source:** G7 HF smoke -- expansion saturates 4000 grid; whitening adds nothing; subsumption at small scale. Need full to confirm at scale.
- **Architecture:** 4 arms at N_enc=10000: (a) base raw, (b) whiten only, (c) expand only, (d) expand + whiten
- **Why CRITICAL:** if subsumption holds at scale, Phase 4 production rule simplifies to "expand". If full shows stacking, ~97x compound holds.
- **Capability advanced:** Phase 4 production architecture finalization
- **HP threshold:** (d) > (c) by >=15% (NO subsumption; ETF whitening still adds value)
- **MID:** (d) >= (c) but <15% better (marginal stacking)
- **HF:** (d) approximately = (c) (subsumption CONFIRMED at scale; whitening redundant once expanded)
- **Strategic value:** simplification vs complexity for Phase 4 production code

### Slot PP8R2 (NEW; from cycle 122 PP-8 cleanup): `substrate_pp8_cosine_variance_gate_v1`
- **Wall:** ~30 min CPU
- **Source:** Orchestrator cycle 122 -- PP-8 norm-gate closed; R2 cosine-variance is next rescue
- **Architecture:** gate token retention by variance of cosine similarity to VQ cluster centroid (high-variance = high-discriminability)
- **Capability advanced:** PP-8 cell-level discrimination
- **HP threshold:** cosine-variance gate preserves >=90% concept coverage at 10x speedup
- **MID:** 70-90% / **HF:** <70%

### Slot PP8R4 (NEW; from cycle 122 PP-8 cleanup): `substrate_pp8_learned_discriminability_probe_v1`
- **Wall:** ~60 min GPU
- **Source:** Orchestrator cycle 122 -- PP-8 R4 learned probe rescue
- **Architecture:** train small linear probe to predict which tokens contribute to retrieval quality
- **Capability advanced:** PP-8 learned routing
- **HP threshold:** >=95% concept coverage at 10-50x speedup
- **MID:** 80-95% / **HF:** <80%

### Slot G9-FIX (REVISED METRIC per Exp-Dev's methodology flag): `substrate_etf_minilm_M_star_cross_N_v1`
- **Wall:** ~30 min CPU (merges with DAMB1 if Exp-Dev prefers)
- **Source:** Exp-Dev G9 parking + methodology request for precise metric
- **Architecture (REVISED metric):** measure M_50(N_sub) = M at which raw recall first drops below 0.5; compute ratio whitened_M_50 / raw_M_50 across N_sub in {384, 768, 1536, 3072}
- **Why precise:** capacity-sweep ratio censors at grid max (false "shrinks"); M_50 threshold falls exactly where capacity breaks, no censoring; M_50 is natural inverse of capacity
- **Capability advanced:** Phase 4B cross-N attenuation profile (clean metric)
- **HP threshold:** ratio grows with N_sub (H2 saturation confirmed; matches drill A prediction that H2 is dominant)
- **MID:** ratio approximately constant (H1+H2 mixed)
- **HF:** ratio shrinks with N_sub (H1-dominant; matches drill A's secondary prediction)
- **Note to Exp-Dev:** can MERGE with DAMB1 (both measure cross-N Q-shape with clean metric); architecture compatible

### Slot DAMB4 (NEW; PARALLEL with DAMB1; attacks both hypotheses): `substrate_pca_prewhitening_codebook_v1`
- **Wall:** ~25 min CPU
- **Source:** Drill A Cell 4 -- PCA pre-whitening attacks BOTH H1 (anisotropy) AND H2 (isotropic-ization makes Hadamard near-optimal)
- **Architecture:** apply PCA whitening to encoder output BEFORE sign-projection; measure capacity vs unwhitened Hadamard at N=384 on real encoder keys
- **Why:** independent of DAMB1 result; cheapest encoder-architecture-aware intervention; one offline PCA + one O(d^2) multiply per query
- **Capability advanced:** Phase 4B + Phase 4a -- universal real-encoder rescue
- **HP threshold:** PCA-whitened Hadamard >= 2x unwhitened Hadamard at N=384
- **Strategic value:** if HP, ships as one-line preprocessing change to substrate VQ layer; multiplicative improvement across ALL downstream experiments

### Slot PSE4 (NEW; from drill C; adaptive K_c quality feedback): `substrate_adaptive_stratification_quality_feedback_v1`
- **Wall:** ~45 min CPU
- **Source:** Drill C Sub-question (4)
- **Architecture:** K_c(t+1) = K_c(t) * (1 + beta*(e_c - e_mean)/e_std), beta=0.1, normalized daily
- **Why:** rare-concept workloads benefit; <1% overhead
- **Capability advanced:** PP-22 adaptive production extraction
- **HP threshold:** quality on rare-concept queries >=10% better than static stratification
- **Strategic value:** production polish; runs after PSE1/PSE2/PSE3 establish baseline

### Slot 7 (UPDATED -- K-hop ceiling now K>=6 not K=3 per cycle 118): `substrate_native_reasoning_K10_K20_n16384_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HP; full tests K up to 20 at N=16384); queued CPU
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

### Slot DIMSPARSE (NEW; HIGHEST PRIORITY -- THE critical compound test from cycle 123): `substrate_dim_expansion_plus_sparse_pattern_compound_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (un-parked; Option iii + whitening; smoke HARD_FAIL gain_c=1.0 sparse-values no help, key-collision-limited; full queued GPU)
- **Wall:** ~45 min CPU
- **Source:** Cycle 123 cycle confirms 3 INDEPENDENT axes (Hadamard, dim-expansion, sparsity). Critical OPEN: do dim-expansion + sparsity stack?
- **Architecture:** 4 arms at N=4096 / N=16384: (a) baseline, (b) dim-expansion alone, (c) sparse pattern alone (alpha=0.20), (d) dim-expansion + sparse pattern combined
- **Why CRITICAL:** if (d) > (b) * (c) multiplicatively, causal-LM substrate compound = 6.68x x 6.7x = ~45x at N=16384. If they don't stack, each is independent ~7x ceiling.
- **Capability advanced:** Phase 3 capacity compound (THE remaining open question on capacity story)
- **HP threshold:** (d) combined >= 0.80 * (b)*(c) (multiplicative compound holds within 20%)
- **MID:** (d) > max((b),(c)) but < 0.80 * (b)*(c) (partial stack)
- **HF:** (d) approximately = max((b),(c)) (no stacking; pick one)
- **Strategic value:** SINGLE highest-value capacity test today. Gates Phase 3 compound math (~45x if HP; ~7x ceiling if HF).

### Slot 9 (DONE; MIDDLE 2.75x; real-encoder dim ceiling): ~~`substrate_etf_hadamard_phase4a_infra_eval_v1`~~
- **Status:** DONE 2026-06-06 ~10:15 -- raw_cap=307 vs whitened_cap=844 on MiniLM 384-dim = 2.75x
- **Root cause:** real-encoder dim ceiling -- MiniLM at 384-dim has limited orthogonalization headroom vs synthetic Hadamard at unrestricted N
- **Strategic NUANCE:** real-encoder compound is 2.75x x 12x = ~33x (NOT synthetic-keys 100x). Phase 3 linear-mode still meaningful but bounded
- **Rescue identified:** dim-expansion via random-feature lift -> Slot 14 below

### Slot 10 (NEW; CRITICAL Phase 3 confirmation gate): `substrate_etf_hadamard_n_sweep_capacity_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HP: lift persists 8.0x to N=2048; full sweeps to 65536); queued CPU
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

### Slot LC1 (NEW; learned-codebook drill Anchor 1; HIGHEST PRIORITY cheap test): `substrate_sparse_hadamard_mixture_codebook_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_FAIL: SHM cap 0 vs Hadamard 409, mixing destroys orthogonality -> informs LC2 learned); queued CPU
- **Wall:** ~30 min CPU
- **Source:** Learned-codebook research drill landed 2026-06-06 ~10:55
- **Architecture:** sparse Hadamard mixture codebook (k random Hadamard rows summed + sign); zero training cost
- **Why prioritize:** cheapest decisive test for encoder-anisotropy hypothesis. If HP, ships immediately in next infra update. If HF, informs whether LC2 (learned) is worth training cost.
- **Capability advanced:** Phase 4B real-encoder codebook-collision attack (encoder-decorrelation axis)
- **HP threshold:** SHM capacity >= 1.5x Hadamard at matched conditions
- **MID:** 1.1x-1.5x
- **HF:** <= 1.1x Hadamard
- **Cite:** Hu et al. 2024 (arXiv:2410.23126; spherical codes = optimal Hopfield memory)

### Slot LC2 (NEW; learned-codebook drill Anchor 2): `substrate_kmeans_learned_codebook_minilm_v1`
- **Wall:** ~90 min total CPU (~30 min k-means training + ~60 min substrate bench)
- **Source:** Learned-codebook research drill Anchor 2
- **Architecture:** k-means codebook initialization on real MiniLM embeddings; distribution-alignment hypothesis
- **Why:** larger potential gain than LC1 (targets distribution precisely) but requires training cost
- **Capability advanced:** Phase 4B real-encoder learned-codebook rescue
- **HP threshold:** learned capacity >= 2.0x Hadamard
- **MID:** 1.2x-2.0x
- **HF:** <= 1.2x Hadamard
- **Cite:** Achilli et al. 2025 (arXiv:2503.09518; manifold-aligned codebooks INCREASE capacity); Bielmeier-Friedland 2025 (arXiv:2508.01395; feature correlations reduce capacity prefactor)

### Slot LC3 (NEW; learned-codebook drill Anchor 3): `substrate_basis_pursuit_overcomplete_codebook_v1`
- **Wall:** ~45 min CPU
- **Source:** Learned-codebook research drill Anchor 3
- **Architecture:** 4x overcomplete dictionary with k=8 sparse codes; OMP retrieval
- **Why:** highest complexity, highest upside; tests whether Hopfield dynamics are compatible with sparse-support retrieval
- **Capability advanced:** Phase 4B sparse-support concept-address architecture
- **HP threshold:** sparse-code capacity >= 3.0x Hadamard
- **MID:** 1.5x-3.0x
- **HF:** <= 1.5x Hadamard
- **Cite:** Ganguli et al. (arXiv:1611.09621; expander decoding); informs V2 substrate architecture decision

---

## GPU LANE PRIORITIES (genuine GPU-appropriate cells; populated 2026-06-06 10:25 per Exp-Dev's request)

GPU lane must always have prioritized depth so it never idles. Pull from this section when GPU runner slot opens.

### Slot 14 (DONE; MIDDLE -- LVH catch #225): ~~`substrate_etf_minilm_dim_expansion_v1`~~
- **Status:** DONE 2026-06-06 ~11:00 -- D=384 2.75x; D=1024 1.29x; D=4096 1.29x. LVH catch #225 on >=3x mean-only claim.
- **Finding:** dim-expansion lift PLATEAUS (does not scale linearly with D as smoke suggested). At D=4096 the gain is only 1.29x.
- **Strategic impact:** real-encoder compound revised DOWN: ETF (2.75x) x dim-expansion (1.29x) x sparse (12x if real-encoder) = ~42x (not the optimistic 100x+ I projected from smoke)
- **Cross-N finding:** lift SHRINKS with N -- opposite of codebook-collision-as-sole-noise prediction. Either (a) real encoders have N-dependent additional noise, or (b) Hadamard gain is N-saturating because partial pre-structure dominates at large N. **Slot G9 N_sub sweep now CRITICAL to disambiguate.**
- **Honest-re-read discipline:** I over-extrapolated from smoke D=1024 result. LVH #225 caught it. Discipline working.

### Slot G1 (NEW; transferability test): `substrate_etf_dim_expansion_mpnet_768_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke MIDDLE 2.5x: expansion transfers to mpnet-768); queued GPU
- **Wall:** ~60 min GPU
- **Source:** Slot 14 dim-expansion result + Exp-Dev's recommendation
- **Why:** does dim-expansion rescue generalize across encoders? mpnet-768 has higher base dim than MiniLM; if expansion still helps, the rule is universal
- **Architecture:** load all-mpnet-base-v2; same random-feature lift + ETF; D in {768, 1536, 4096}
- **Capability advanced:** Phase 4a real-encoder rule generalization
- **HP threshold:** D=4096 whitened_cap >= 8x raw_cap (lower bar; mpnet starts higher dim)

### Slot G2 (DONE; HP under hard same-domain negatives): ~~`substrate_kf1_hallucination_robustness_sweep_v1`~~
- **Status:** DONE 2026-06-06 ~10:35 -- AUC easy=0.996, **AUC hard same-domain=0.975** (HP gate 0.90; exceeds by 0.075)
- **27th flagship anchor** -- production-grade KF-1 robustness validated
- **Honest side-finding (CAPABILITY BOUNDARY):** word-shuffled adversarial AUC=0.217. Root cause: MiniLM is bag-of-words; shuffling barely changes embedding. NOT substrate failure -- encoder bottleneck. Phase 4 word-order-sensitive detection needs order-sensitive encoder (Pythia/Llama residuals) or explicit n-gram/positional features.
- **Full run:** N_KB=4000 with 3 seeds queued GPU
- **Follow-ons added below:** Slot G10 (n-gram-augmented hallucination detection) + Slot G11 (KF-1 on order-sensitive encoder)

### Slot G3 (NEW; real-encoder capacity at production-class N): `substrate_real_encoder_capacity_n16384_dim_expanded_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke MIDDLE, capacity grid-lower-bound); full queued GPU
- **Wall:** ~75 min GPU
- **Source:** Slot 14 dim-expansion + capacity scaling story
- **Why:** combines dim-expansion result with substrate capacity narrative; tests whether dim-expanded MiniLM at N=16384 gives meaningful production capacity
- **Architecture:** dim-expanded MiniLM substrate (D_eff=4096); N=16384; sweep M; auto-assoc Hopfield + FLIP=0.05
- **Capability advanced:** Phase 4a production capacity claim
- **HP threshold:** whitened_cap at N=16384 >= 6,000 facts (10x raw MiniLM baseline)
- **Strategic value:** ties dim-expansion to production substrate sizing

### Slot G4 (NEW; continual KV scaling): `substrate_continual_kv_n32768_120_sessions_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_PASS 100% retention; W-free; full N=32768/120 sessions); queued CPU
- **Wall:** ~90 min GPU
- **Source:** Continual KV HP at N=8192 with 60 sessions (99.8% retention); scale test
- **Why:** production needs larger N + more sessions; current HP is mid-scale
- **Architecture:** Continual KV setup at N=32768; 120 sessions / 7,200 facts; same write rule as HP baseline
- **Capability advanced:** PP-19 continual learning scale
- **HP threshold:** retention >= 0.95 at session 120; zero contradictions
- **MID:** retention 0.85-0.95
- **HF:** retention < 0.85 (continual KV doesn't scale)

### Slot G5 (NEW; harder hallucination benchmark): `substrate_kf1_truthfulqa_style_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_FAIL: negation AUC=0.034, MiniLM negation-insensitive); full queued GPU
- **Wall:** ~60 min GPU
- **Source:** KF-1 flagship + Exp-Dev's note on harder benchmarks
- **Why:** KF-1's AUC=0.999 was on substrate-internal generated distractors; harder benchmark needed for production credibility
- **Architecture:** KF-1 setup applied to TruthfulQA-style adversarial questions (or curated subset); compare to LLM baselines (GPT-3.5 / Claude 3 / Llama-3-70B if available via API)
- **Capability advanced:** PP-3 hallucination detection generalization
- **HP threshold:** substrate KF-1 AUC >= 0.85 on adversarial benchmark
- **MID:** AUC 0.70-0.85
- **HF:** AUC < 0.70 (clean substrate signal didn't generalize)

### Slot G7 (NEW; combined defense): `substrate_hadamard_plus_whitening_combined_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_FAIL: expansion subsumes whitening, no stacking; data-censored); queued GPU
- **Wall:** ~45 min GPU
- **Source:** Orchestrator cycle 119 -- Phase 4B gates; currently Hadamard init and whitening are independent rescue mechanisms
- **Why:** Hadamard codebook init = orthogonal codebook by construction; whitening = transforms input space to isotropic. Different operations; could combine multiplicatively. Tests whether real-encoder headroom recovery scales further.
- **Architecture:** test substrate with (a) baseline random codebook, (b) Hadamard codebook init only, (c) whitening only, (d) Hadamard codebook + whitening (combined)
- **Capability advanced:** Phase 4B combined real-encoder rescue mechanism
- **HP threshold:** combined H+W > additive sum of individual mechanisms (multiplicative compound)
- **MID:** combined > max(individual) but < additive
- **HF:** combined approx max(individual) (mechanisms are redundant)

### Slot G8 (NEW; cross-encoder Pythia/Llama-1b dim-expansion): `substrate_dim_expansion_cross_encoder_pythia_llama_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_PASS: expansion scales 6.68x on Pythia; side-finding raw Pythia cap=0 -> LM embeddings need whitening); queued GPU
- **Wall:** ~90 min GPU (2 encoders)
- **Source:** Orchestrator cycle 119 -- Phase 4B cross-encoder test
- **Why:** Slot G1 tests mpnet (sentence-transformer family); orchestrator wants encoder-family-agnostic confirmation via Pythia-160m + Llama-1b (LM family). If dim-expansion works across encoder families, the rule is universal.
- **Architecture:** dim-expansion on Pythia-160m residuals (existing npz) AND Llama-1b residuals; ETF orthogonalize at D in {dim_native, 2*dim_native, 4096}
- **Capability advanced:** Phase 4B dim-expansion rule universality
- **HP threshold:** D=4096 whitened_cap >= 8x raw_cap on BOTH Pythia and Llama-1b
- **MID:** >= 8x on one but not both
- **HF:** < 8x on both (rule is encoder-specific)

### Slot G9 (NEW; lower-N dim sweep per orchestrator Phase 4B gate): `substrate_etf_minilm_n_sub_lower_sweep_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (un-parked; rebuilt with M_50-ratio metric per Research spec); queued GPU
- **Wall:** ~45 min GPU
- **Source:** Orchestrator cycle 119 -- "N-sweep across MiniLM N_sub in {384, 768, 1536, 3072}"
- **Why:** Slot G3 tests N=16384 production scale; orchestrator wants intermediate sweep to see whether 2.75x holds or GROWS as N_sub increases
- **Architecture:** ETF Hadamard whitening on MiniLM; sweep N_sub in {384, 768, 1536, 3072}; measure cap ratio vs raw
- **Capability advanced:** Phase 4B encoder-scale dependency curve
- **HP threshold:** ratio at N_sub=3072 >= 5x (growth from 2.75x at N=384)
- **MID:** plateau at 2.75-5x
- **HF:** ratio plateaus at 2.75x or declines

### Slot G10 (DONE; MIDDLE 0.702): ~~`substrate_kf1_hallucination_order_sensitive_encoder_v1`~~
- **Status:** DONE 2026-06-06 ~11:10 -- adv(word-shuffle) AUC easy=0.937 hard=0.893 ADV=0.702
- **Finding:** Pythia rescues word-order detection substantially (0.217 MiniLM -> 0.702) but short of 0.85 HP gate. Order-sensitive causal encoder IS the right architectural direction.
- **Full queued:** 3 seeds, N_KB=4000 GPU
- **2x rescue drill DISPATCHED 11:15:** how to close 0.702 -> 0.85+ gap (architecture choices, model size scale, fine-tune for hallucination)
- **Sibling HF Slot G11** below (char n-grams) shares root-cause topic; drill combines both

### Slot G10-orig (NEW; order-sensitive encoder for KF-1): `substrate_kf1_hallucination_order_sensitive_encoder_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke MIDDLE adv=0.702, rescues 0.217->0.702); full queued GPU
- **Wall:** ~75 min GPU
- **Source:** Slot G2 capability boundary finding -- MiniLM bag-of-words limits adversarial detection
- **Why:** if hallucination detection needs to be word-order-sensitive (e.g., catching "John gave Mary the book" vs "Mary gave John the book" as different facts), need an encoder that captures order
- **Architecture:** KF-1 setup with Pythia-160m residuals (already in npz; order-sensitive by construction) OR Llama-1b residuals -- compare to MiniLM baseline
- **Capability advanced:** PP-3 hallucination detection with order-sensitivity (production capability)
- **HP threshold:** word-shuffled adversarial AUC >= 0.85 on Pythia/Llama (vs 0.217 on MiniLM)
- **MID:** AUC 0.70-0.85
- **HF:** AUC < 0.70 (even order-sensitive encoders fail; need explicit n-gram features)

### Slot G11 (DONE; HARDFAIL 0.192 -- char n-grams cannot capture word order): ~~`substrate_kf1_ngram_augmented_v1`~~
- **Status:** DONE 2026-06-06 ~11:10 -- ADV=0.192 (worse than MiniLM-only 0.217)
- **ROOT CAUSE:** char n-grams live mostly WITHIN words; word-shuffle preserves them; ngram features barely change. CHAR n-grams cannot capture WORD order.
- **Strategic impact:** lightweight char-n-gram path BLOCKED. Word-LEVEL n-grams or order-sensitive encoder (G10) are the viable paths.
- **2x rescue drill DISPATCHED 11:15 (combined with G10):** word-level n-grams + positional embeddings + other lightweight order-sensitivity options
- **Follow-on hypothesis:** Slot G13 word-level n-gram MiniLM as lightweight alternative

### Slot G11-orig (NEW; n-gram-augmented hallucination detection): `substrate_kf1_ngram_augmented_v1`
- **Status:** LAUNCHED by exp_dev 2026-06-06 (smoke HARD_FAIL adv=0.192; char n-grams survive word-shuffle); full queued GPU
- **Wall:** ~60 min GPU
- **Source:** Slot G2 capability boundary -- alternative path to order-sensitivity
- **Why:** if order-sensitive encoder is too expensive, augment MiniLM with explicit n-gram features
- **Architecture:** MiniLM embedding concat character-level n-gram bag-of-features (n=2,3,4); standard KF-1 detection
- **Capability advanced:** PP-3 lightweight order-sensitivity
- **HP threshold:** word-shuffled adversarial AUC >= 0.80 (vs 0.217 baseline)
- **Strategic value:** if HP, MiniLM-class encoder gains order-sensitivity at minor cost

### Slot HOC1 (NEW; PRIORITY 1 from 2x drill B; CHEAPEST decisive): `substrate_kf1_minilm_word_bigram_concat_v1`
- **Wall:** <2 min CPU smoke
- **Source:** Drill B (11:30) Sub-question (2) cell
- **Architecture:** MiniLM embedding concat word-level bigram bag-of-features
- **Why first:** algebraically grounded; ~98% of word bigrams are destroyed by uniform word-shuffle, so detection is guaranteed in principle; zero training, no GPU
- **Capability advanced:** PP-3 hallucination detection lightweight order-sensitivity (G11 root-cause fix)
- **HP threshold:** word-shuffled adversarial AUC >= 0.65 (drill prediction)
- **MID:** AUC 0.50-0.65
- **HF:** AUC < 0.50 (redirects to positional embedding approach)
- **P_deflated:** 0.50

### Slot HOC2 (NEW; PRIORITY 2 from 2x drill B; algebraic AUC 0.88-0.92): `substrate_kf1_hybrid_pythia_bigram_fusion_v1`
- **Wall:** ~30 min CPU (logistic regression alpha sweep; no GPU fine-tune)
- **Source:** Drill B Sub-question (3) cell
- **Architecture:** Pythia frozen residuals (current 0.702) late-fused with word bigram features
- **Why:** error modes are NOT correlated (rho 0.2-0.4); algebraic prediction AUC in [0.88, 0.92] -- this is the path that CLOSES the 0.85+ gap
- **Capability advanced:** PP-3 production order-sensitive detection
- **HP threshold:** word-shuffled AUC >= 0.85 (closes the gap)
- **MID:** 0.75-0.85
- **HF:** < 0.75
- **Condition:** Run after HOC1 passes (smoke confirms bigram signal exists)
- **P_deflated:** 0.42

### Slot HOC3 (NEW; PRIORITY 3 from 2x drill B; ceiling option): `substrate_kf1_pythia_fine_tune_order_sensitive_v1`
- **Wall:** ~30 min GPU fine-tune; 5k-10k training pairs
- **Source:** Drill B Sub-question (1) Option C
- **Architecture:** Contrastive fine-tune Pythia-160m with word-shuffle as hard negative
- **Why:** highest-ceiling option; expected AUC [0.80, 0.88] alone; [0.90+] combined with bigram
- **Capability advanced:** PP-3 principled architecture for full adversarial robustness
- **HP threshold:** AUC >= 0.85 standalone OR >= 0.90 when combined with HOC1 bigrams
- **Condition:** Run only if HOC1+HOC2 stay in MID-BAND
- **P_deflated:** 0.38

### Slot HOC5 (NEW; orchestrator R3/R4 backup; size-scaling): `substrate_kf1_pythia_410m_1b_size_scaling_v1`
- **Wall:** ~60 min GPU (both 410M + 1B)
- **Source:** Orchestrator cycle 121 R3/R4 hypotheses
- **Why backup:** Drill B lit-scan predicts size-scaling alone gives only 0.702 -> ~0.72 (BERT-class 75-90% word-order invariant even at large scale per arXiv:2012.15180). KEEP in queue as falsification test of drill prediction.
- **Capability advanced:** PP-3 size-scaling falsification
- **HP threshold:** AUC >= 0.85 at Pythia-1B (would refute drill prediction; size DOES close gap)
- **MID:** 0.72-0.85 (drill prediction confirmed)
- **HF:** < 0.72 (size scaling actively unhelpful)
- **Strategic note:** lower priority than HOC1/HOC2/HOC3 per drill B; runs only if those cells fail or if user wants explicit falsification of size-scaling

### Slot HOC4 (NEW; PRIORITY 4 from 2x drill B; diagnostic): `substrate_kf1_adversarial_diversity_sweep_v1`
- **Wall:** Tier 2-3 (generates attack variants; small inference budget)
- **Source:** Drill B Sub-question (4)
- **Architecture:** Run detectors across 4 attack types: word shuffle, phrase shuffle, token reverse, paraphrase
- **Why:** required before production deployment to confirm no false-positive explosion on valid paraphrases
- **Capability advanced:** PP-3 production-readiness gate
- **HP threshold:** detector maintains AUC >= 0.85 across all 4 attack types; paraphrase AUC <= 0.30 (so it ISN'T flagging valid paraphrases as hallucinations)
- **Condition:** Run IN PARALLEL with HOC2+HOC3 to inform fine-tune training-negative selection
- **P_deflated:** 0.30

### Slot G12 (NEW; adversarial KF-1 a_query_sim defense): `substrate_kf1_a_query_sim_defense_v1`
- **Wall:** ~60 min GPU
- **Source:** Orchestrator cycle 120 -- KF-1 adversarial shuffled-KB AUC=0.206 remains open; orchestrator flagged `a_query_sim` defense path
- **Why:** the shuffled-KB attack remains the open KF-1 vulnerability after the hard-negative HP. a_query_sim is the query-layer defense (cosine similarity vs query distribution) that should detect this
- **Architecture:** KF-1 + a_query_sim query-layer defense (compute similarity of incoming query to KB query distribution; reject if too anomalous)
- **Capability advanced:** PP-3 hallucination detection adversarial robustness
- **HP threshold:** shuffled-KB adversarial AUC >= 0.80 (vs 0.206 baseline)
- **MID:** AUC 0.60-0.80
- **HF:** AUC < 0.60 (a_query_sim doesn't catch shuffled attacks)
- **Strategic value:** closes the last KF-1 adversarial vulnerability surfaced today

### Slot G6 (DEFERRED; Pythia end-to-end): `substrate_pythia_end_to_end_capability_v1`
- **Wall:** ~120 min GPU
- **Source:** Exp-Dev's note + Phase 4 capability validation
- **Status:** DEFERRED until Pythia weights confirmed available locally (similar to HotpotQA-1B gating)
- **Why valuable:** validates substrate-LLM coupling at non-MiniLM/non-Llama-1B encoder

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

### CLOUD-1 (KILLED 2026-06-06 13:40 -- mean-pool bug): ~~`substrate_extraction_quality_7B_vs_70B_v1`~~
- **Status:** KILLED after $0.50 cost; Testbed Pythia diagnostic found mean-pool over causal LM destroys retrieval signal
- **Infrastructure result:** GH200 + aarch64 + cu124 path PROVEN (valuable for Phase 4a work)
- **Replaced by CLOUD-1b** below

### CLOUD-1b (AUTHORIZED 2026-06-06 13:40): `substrate_extraction_quality_1B_8B_70B_last_token_pool_v1`
- **Cost:** ~$1.15 cloud GH200 (~30 min)
- **Architecture fixes from Testbed:**
  - Last-token pool (causal LM appropriate)
  - MiniLM-L6-v2 upper-bound baseline (60-80% top-5 sanity check)
  - Per-query gold-passage rank diagnostics (median, p25, p75, p95)
  - Shuffle gold_indices across full 1000 passages (removes 41-context concentration confound)
  - Llama-3.2-1B added as third model (1B / 8B / 70B size-scaling curve)
- **Gates:** ALL extraction infrastructure decisions
- **HP threshold:** 8B / 70B retrieval >= 0.80 (cheap CPU fleet path)
- **Plus secondary:** does 1B already give meaningful substrate (cheaper deployment)
- **Total binding test budget:** $0.50 sunk + $1.15 = $1.65 to definitive answer

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
- 2026-06-06 09:50 -- v7: TRIPLE LANDING. (a) Slot 3 sparse-PATTERN HP at ~12x (sparse_alpha 0.30 vs dense 0.025 at N=1024 smoke); compound with ETF could give ~100x. (b) Cycle 118 confirmed Matthiessen 100% codebook-collision + K-hop lossless to K>=6 (both labels conservative). (c) Slot 6 norm-gate HARDFAIL rescue drill landed: PER-CLUSTER STRATIFIED is the rescue (100% coverage + 100-1000x speedup; P_deflated 0.65). ADDED Slot 12: per_cluster_stratified_extraction. ADDED Slot 13: concept_uniform_random_extraction (floor case). Slot 7 expanded to K=10/K=20 sweep (K-hop ceiling unknown above 6). DIAGNOSTIC+RESCUE+REASONING TRIPLE NOW EMPIRICALLY ANCHORED.
- 2026-06-06 10:25 -- v8 (POST-COMPACTION + GPU LANE POPULATED): Slot 9 MIDDLE 2.75x on real MiniLM (real-encoder dim ceiling); compound revised to ~33x for real encoders. ADDED Slot 14 dim-expansion rescue (Exp-Dev's autonomous build; smoke linear scaling; full D=4096 in flight). ADDED GPU LANE PRIORITIES section with 6 cells (G1-G6): mpnet transferability, KF-1 robustness sweep, real-encoder capacity at N=16384 with expansion, continual KV at N=32768, KF-1 on TruthfulQA-style benchmark, Pythia end-to-end (deferred). Per Exp-Dev's note: GPU lane was thin; user flagged GPU-idle multiple times. Now GPU lane has prioritized depth.
- 2026-06-06 10:35 -- v9 (Phase 4B gates from orchestrator cycle 119): Orchestrator framed "remaining 73% real-encoder headroom is recoverable via deeper codebook-collision attacks." ADDED Slot G7 Hadamard+whitening combined defense (cheap architectural test); Slot G8 cross-encoder Pythia-160m + Llama-1b dim-expansion (encoder-family-agnostic confirmation); Slot G9 N_sub lower sweep {384, 768, 1536, 3072} on MiniLM. Plus research drill dispatched on learned codebooks / basis pursuit / sparse Hadamard mixtures (deeper rescue paths for the 73% headroom).
- 2026-06-06 10:45 -- v10: Slot G2 KF-1 robustness HP. AUC hard same-domain = 0.975 (27th flagship anchor). Honest side-finding: word-shuffled adversarial AUC=0.217 traced to MiniLM bag-of-words (capability boundary, NOT substrate failure). ADDED Slot G10 KF-1 on order-sensitive encoder (Pythia/Llama) + Slot G11 KF-1 n-gram-augmented MiniLM (lightweight rescue). Phase 4 order-sensitive hallucination detection now has 2 architectural paths.
- 2026-06-06 10:55 -- v11: Learned-codebook research drill landed. ADDED Slot LC1 sparse-Hadamard-mixture (CHEAPEST decisive ~30 min CPU; HP >=1.5x; zero training; ships in next infra update if HP); Slot LC2 k-means learned codebook on MiniLM (~90 min CPU; HP >=2x); Slot LC3 basis pursuit 4x overcomplete sparse codes (~45 min CPU; HP >=3x; highest upside). All 3 target the 73% real-encoder headroom orchestrator surfaced in cycle 119. If LC1 HPs, real-encoder Phase 4a substrate gains 1.5x on top of current 2.75x = ~4x effective; if LC2/3 HP, larger gains.
- 2026-06-06 11:05 -- v12 (cycle 120 -- 1 HP + 1 LVH catch): KF-1 hard-negative BAND-LIFT confirmed (AUC 0.968-0.975; KF-1 band 0.70-0.85 -> 0.72-0.87; 27th flagship). Slot 14 dim-expansion MIDDLE_BAND with LVH CATCH #225 (>=3x mean-only claim; honest floor 1.29x at D=4096; lift PLATEAUS not scales linearly). Real-encoder compound revised DOWN: 2.75x x 1.29x x 12x = ~42x (not earlier 100x projection). Phase 3 linear-mode: ~110k/substrate; D=8 = ~880k. ADDED Slot G12 KF-1 a_query_sim defense.
- 2026-06-06 11:30 -- v13: 2x drill B (hallucination order-sensitivity close-gap) landed. KEY INSIGHT: size scaling alone DOESN'T close the gap (BERT-class models are 75-90% word-order invariant even at large scale; Pythia 160m -> 1b only gives 0.702 -> ~0.72 AUC). Word-LEVEL bigram TF-IDF IS the algebraic fix (98% of bigrams destroyed by uniform word-shuffle of n=50; predicted AUC 0.85-0.92; zero GPU; zero training). ADDED Slot HOC1 MiniLM+word-bigram (<2 min CPU; cheapest); HOC2 hybrid Pythia+bigram (~30 min CPU; CLOSES gap if HP via uncorrelated error modes rho 0.2-0.4); HOC3 Pythia fine-tune (GPU; ceiling); HOC4 adversarial diversity sweep (production gate; paraphrase is separate capability row). Drill A + Drill C still in flight.
- 2026-06-06 11:45 -- v14 (cycle 121 -- 1 HF + 1 MID confirmed): cap_map v442 -> v443; HONEST 956 -> 958. G11 n-gram HARDFAIL (R1 rescue axis CLOSED per orchestrator); G10 Pythia MIDDLE confirmed (orchestrator's 0.746 vs Exp-Dev's 0.702; both 0.70-0.85). Orchestrator surfaces R3/R4/R5 paths. **TENSION FLAGGED:** drill B's lit-scan predicts R3/R4 (Pythia size scaling) will NOT close the gap (BERT-class word-order invariance at any scale); HOC1+HOC2 (word bigrams + hybrid late fusion) are algebraically more efficient. Added Slot HOC5 as size-scaling falsification backup (lower priority than HOC1/2/3). KF-1 band 0.72-0.87 unchanged.
- 2026-06-06 11:50 -- v15: 2x drill C (per-cluster stratified extraction operational depth) landed. KEY FINDING: dominant production risk is CODEBOOK COLLAPSE (dead VQ codes), NOT coverage loss. Coverage guaranteed by construction. Recommended production architecture: sqrt-K allocation (Neyman-optimal proxy without expensive sigma_c) + online Vitter reservoir + IVF VQ (~50000x cheaper) + sliding window + collapse monitoring (6 metrics) + recovery (EMA / OT / perturbation). ADDED Slot PSE1 sqrt-K allocation; PSE2 online streaming; PSE3 codebook collapse monitoring (CRITICAL production-deployment gate); PSE4 adaptive K_c feedback. Drill A real-encoder cross-N attenuation still in flight.
- 2026-06-06 12:00 -- v16: 2x drill A (real-encoder cross-N attenuation disambiguation) landed. KEY INSIGHT: H1 (N-dependent noise) and H2 (Hadamard N-saturation) predict DIFFERENT Q(N) curve shapes -- SUB-LINEAR vs LINEAR decay. ADDED Slot DAMB1 disambiguation N-sweep (HIGHEST PRIORITY ~30 min CPU; routes ALL subsequent rescue investments); Slot DAMB2 LC1 N-sweep extension (SHM attacks BOTH hypotheses); Slot DAMB3 SRHT codebook (conditional H2 rescue); Slot DAMB4 PCA pre-whitening (parallel with DAMB1; attacks BOTH hypotheses). ALL 3 of today's parallel 2x drills now landed (A+B+C). Today's drill output: 13 new cells (HOC1-5 + PSE1-4 + DAMB1-4) targeting all non-positive results with explicit algebraic rescue paths.
- 2026-06-06 12:15 -- v17: TRIPLE VERDICT batch. (a) Slot 10 SMOKE HP -- synthetic Hadamard lift FLAT 8x across N (CONTRASTS with Slot 14 real-encoder plateau; confirms drill A's H2 hypothesis is real-encoder-specific). Full sweep {4096-65536} queued. If holds, Phase 3 linear capacity ~10x lift -> 26k facts/substrate. (b) Slot 12 SMOKE MIDDLE -- per-cluster stratified WORKING; 100% coverage by construction; speedup ~21x smoke -> production 100-1000x. (c) Slot 13 SMOKE HARDFAIL -- random sampling 16% coverage at 100x. EXTRACTION RESCUE TREE RESOLVED: stratified is the only adequate path. G9 rebuilding with M_50 ratio spec; G5 full queued.
- 2026-06-06 12:30 -- v18 (cycle 122 nuance + 2 HF confirmed + PP-8 R2/R4 added + G5 NEGATION drill dispatched): cap_map v443 -> v444; HONEST 958 -> 961. **CRITICAL NUANCE: cross-N attenuation is PARTLY MEASUREMENT CEILING artifact** (N_sub=384 1.21x real; N_sub=512 ceiling-flat at 99% raw recall). N_sub=384 is the actionable real-encoder design point. Slot 6 norm-gate full HF confirmed; PP-8 norm-axis CLOSED; added Slot PP8R2 cosine-variance + Slot PP8R4 learned probe. G5 TruthfulQA HF confirmed (negation AUC 0.034); user flagged audit gap -- I had treated G5 as same-class as G11 word-order but NEGATION is a DISTINCT architectural axis (antonyms like "increases" vs "decreases" need polarity, not just order). **2x drill on negation detection dispatched (G5 dedicated rescue)** -- BART-MNLI / negation-cue features / polarity-aware embeddings / hybrid late fusion. ETA ~25 min sonnet.
- 2026-06-06 13:40 -- v19 (CLOUD-1 mean-pool bug + CLOUD-1b authorized): Testbed dispatched CLOUD-1 + diagnosed mean-pool bug on Pythia local in 3 min / $0. Mean-pool over causal LM destroys retrieval signal (Pythia: mean-pool top-5=0.000; last-token=0.130). CLOUD-1 killed at $0.50; CLOUD-1b authorized at ~$1.15 with 5 design fixes: last-token pool + MiniLM baseline + per-query rank + shuffled gold + Llama-1B added (1B/8B/70B trio). Total binding test cost $1.65 to definitive answer. **STANDING RULE codified:** causal LM = last-token pool; bidirectional encoder = mean-pool/CLS. Affects all future substrate-LLM extraction cell specs. Infrastructure proven: GH200 + aarch64 + cu124 path works (Phase 4a future asset).
- 2026-06-06 13:55 -- v20 (G13 HF + G8 HP = MAJOR STRATEGIC SHIFT for causal-LM substrate): **G13 contradiction HF** (Pythia AUC 0.111; embedding-grounding cannot catch negation regardless of encoder order-sensitivity); ADDED Slot G14 NLI-head BART-MNLI rescue. **G8 cross-encoder dim-expansion HP** at 6.68x for Pythia LM family with whitening NON-OPTIONAL (raw Pythia cap=0 cone-collapsed; mean-pooled causal LM is unusable raw). **MAJOR STRATEGIC INSIGHT: causal-LM substrate compound = 1.21x whitening x 6.68x expansion x 12x sparse = ~97x (vs MiniLM ~1.87x); causal LMs have MORE anisotropy to attack -> more headroom.** Phase 3 linear-mode revised UP: ~254k facts/substrate at N=65536; D=8 = ~2M facts (Wikipedia subset viable in linear mode!). G8 + CLOUD-1 are same finding from different angles (mean-pool causal LM broken; last-token AND whitening BOTH fix). ADDED Slot G15 last-token vs whitening vs combined comparison.
- 2026-06-06 14:00 -- v21: G5 negation 2x drill landed (4th + final 2x drill from today's audit-gap closure). REFINED Slot G14 with concrete spec: drop-in MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (91.2% MNLI / 70.2% ANLI; CPU-eligible; no training). ADDED Slot NEG2 polarity adapter (diagonal re-weighting on MiniLM dims; antonym coverage; +14.52% per arXiv:2504.00584); Slot NEG3 negation cue features (explicit-token baseline); Slot NEG4 hybrid NLI+bigram+Pythia fusion (production-grade Phase 4 v3 scorer; conditional on G14 NLI signal). **ALL 4 TODAY'S 2X DRILLS NOW LANDED** (A real-encoder + B order-sensitivity + C stratified extraction + D negation). Today's drills produced ~20 cells across all non-positive results with explicit algebraic rescue paths.
- 2026-06-06 14:15 -- v22 (G1 MID + G7 HF SIMPLIFICATION): G1 mpnet-768 dim-expansion MIDDLE (2.5x at D=768; rule transfers across encoder families; combined with G8's 6.68x on Pythia LM = UNIVERSAL dim-expansion rule). G7 Hadamard+whitening combined HARDFAIL but INFORMATIVE: expansion alone saturates 4000 grid; whitening adds nothing on top -> **EXPANSION SUBSUMES WHITENING** at data-limited scale. PRACTICAL: Phase 4 rule simplifies "expand AND whiten" -> "expand". Cleaner production architecture. CAVEAT: expand arms N_enc-censored at 4000; full N_enc=10000 needed. ADDED Slot G16 explicit subsumption test at scale. Compound math: if subsumption holds, causal-LM 80x (down from 97x); if stacking does occur at scale, 97x stable; either way Wikipedia subset viable in linear mode.
- 2026-06-06 15:00 -- v23 (cycle 123 -- 10-anchor batch + PP-11 BAND-LIFT + 3 INDEPENDENT capacity axes confirmed + LVH #226): cap_map v444 -> v445; HONEST 961 -> 970. 3 HP + 3 MID + 4 HF. **K-hop K=10 N=16384 100% accuracy = 29th flagship anchor**; PP-11 BAND-LIFT 0.40-0.55 -> 0.55-0.70. **3 INDEPENDENT capacity rescue axes confirmed**: Hadamard, dim-expansion, sparsity (Slot 3 full at 5.0-6.7x N=4096 + N=16384). Combined Hadamard+whitening doesn't stack (G7 HF; Phase 4B G7 axis CLOSED). **CRITICAL OPEN: do dim-expansion + sparsity stack?** ADDED Slot DIMSPARSE (HIGHEST PRIORITY; ~45 min CPU) -- THE single highest-value capacity test today. PSE1 LVH #226: speedup saturates at ~20x not 100x (3rd LVH over-claim by me today; discipline lesson: be more conservative on scaling extrapolations). KF-1 negation crisis convergent across 4 cycles; NLI head (NEG1/G14) is the structural fix.

---

**END.**

This file IS the queue priority. Exp-Dev pulls Slot 1 first; reports verdict; Research crosses off + updates; Exp-Dev pulls Slot 2; etc.
