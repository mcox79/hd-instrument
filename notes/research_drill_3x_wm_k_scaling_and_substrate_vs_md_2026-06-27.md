# Research drill 3x — Gap 1: WM K-scaling beyond K=30 / Gap 2: Substrate-vs-MD A/B

**Date:** 2026-06-27 ~22:00 UTC
**Author:** research (Opus 4.7 1M)
**Trigger:** USER 2026-06-27 ~18:00 PDT — drill all high-priority gaps 3x; consider testability; build experiments.
**Calibration discipline:** lit-scan deflation -0.15 to -0.25; novel-synthesis cap 0.50; brain-existence-proof prior bump +0.10; generic-terms-only per query-privacy.
**Builds-on (load-bearing prior anchors):**
- `hdlab/working_memory.py` — WM-multi-bank primitive chain-grade at K_total<=4096, k_per_bank=64 (HARD_PASS commit 6e2ff698)
- `data/exp_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1/metrics.json` — K=8192 CHAIN_GRADE single-arm (rec=1.0 cv=0 adv 0.9999); K=16384 single-seed PASS; K=32768 v3 = HARD_FAIL_UNIT_EXCEPTION (cardinality breach surfaced)
- `data/exp_substrate_multihop_wm_scaffolded_v1/metrics.json` — **HARD_FAIL_WM_DOESNT_HELP**: WM-2hop=0.425 vs baseline=0.65; WM-5hop=0.12; WM-10hop=0.035 (WM-as-scaffold actively HURTS multi-hop)
- `notes/research_drill_substrate_vs_md_head_to_head_proof_gate_design_2026-06-27.md` — design doc for Gap 2 cell; 4-axis envelope, 20-query corpus, 5 arms; GATED on Wave 4 v2 tripwire-surfaced cell chain-grade + 1M-atom KB built + 24h continuous-ingest proven

---

## GAP 1: WM K-SCALING BEYOND K=30 (scope-corrected: K=4096->K=??)

### STALE FRAMING CORRECTION (load-bearing)
The prompt frames "substrate WM cap=30 CHAIN_GRADE; longer chains need K=100+". This is wrong. Skunkworks landed-VET 2026-06-26 on `exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1` ratified K_total=4096 / n_banks=64 / k_per_bank=64 as CHAIN_GRADE; K=8192 single-arm chain-grade landed too. The REAL frontier gap is one of:
- **(a) K scaling beyond 16384** at preserved k_per_bank=64 (v3 cell hit cardinality breach at K=32768 — root-cause needed before re-dispatch)
- **(b) k_per_bank scaling** at fixed K_total (i.e., reducing n_banks; the discriminating-regime threshold is k_per_bank>=64 per `assert_k_per_bank_in_discriminating_regime` gate — what happens at k_per_bank=128, 256, 512?)
- **(c) WM-as-scaffold for multi-hop** (the multihop_wm_scaffolded HARD_FAIL is the OPEN bleeding wound: WM works for storage but DOESN'T HELP intermediate-state binding in multi-hop chains)

### 3x angle synthesis

**ANGLE A — MATH (HD interference scaling at high K):**
Plate (2003) HRR capacity bound: clean-recall at N-dim approximately scales as K ~ N / (4 log(K/p_fail)). For N=8192 and p_fail=0.01: K_predicted ~= 1820 single-bank — substrate hits 4096 in single-bank-equivalent measurement at k_per_bank=64 because the multi-bank routing partitions interference. The math says k_per_bank scaling is bounded by per-bank cross-talk at ~N/(4 log K_per_bank) which at N=8192, K_per_bank=64 has 100x slack. **Prediction**: k_per_bank scaling up to 128-256 should hold rand_rec>=0.95; k_per_bank=512 starts to bite. K_total scaling at fixed k_per_bank=64 is bounded ONLY by routing-hash collision (deterministic bank-id from key hash mod n_banks) and n_banks compute overhead — should scale to K=65536 if cardinality breach root-caused.

**ANGLE B — BRAIN (PFC chunking + dlPFC capacity):**
Cowan (2001) embedded-process model: working memory capacity is 4±1 CHUNKS, not items; Miller's 7±2 was item-counting in chunked contexts. Ericsson-Kintzich long-term-WM (1995): chess grandmasters hold ~100k+ positions retrievably because their LTM-WM uses retrieval structures (chunked schemas). dlPFC neurons (Funahashi 1989 oculomotor delayed-response) show sustained activity during delay periods; capacity is ~4 items per dlPFC subnetwork. CRITICAL BRAIN INSIGHT: brain doesn't scale flat-K — it scales by CHUNKING (cluster K items into groups of ~4-7) and DELEGATING (LTM-WM through schema scaffolds). The substrate's multi-bank architecture IS already chunking (k_per_bank=64 is "one chunk"); flat K=200 in a single bank would replicate Cowan's failure mode. **Prediction**: chunking-based scaffold (route K items into clusters-of-7 via ultrametric-clustering, then WM-bind each cluster centroid) should outperform flat K at K>=50, because flat-K substrate hits the same per-bank interference ceiling brain hits at ~4 items.

**ANGLE C — CROSS-DOMAIN (transformer attention KV-cache scaling):**
Transformer KV-cache at sequence-length L stores 2*L*d_model values per layer; KV-cache memory is O(L*d*layers). At L=100k+ (Claude/GPT context), KV-cache scaling techniques include: (1) sliding-window attention (Mistral) — only attend to last W tokens, O(W) not O(L); (2) KV-cache quantization (AWQ, GPTQ-style int4) — 4-8x compression with <1% perplexity loss; (3) attention-sink architectures (StreamingLLM, Xiao 2023) — preserve first-K tokens as "sinks" plus sliding window; (4) hierarchical KV-compression (MInference 2024) — different attention patterns per head, sparse-1.2k from dense-100k. CRITICAL CROSS-DOMAIN INSIGHT: transformers solve long-context NOT by raw K-scaling but by structural hierarchy (sinks + sliding + compression). The substrate's multi-bank routing is the analog of attention-head partitioning; per-bank capacity is the analog of per-head context budget. **Prediction**: hierarchical WM (chunk-of-chunks; 2-level multi-bank with chunk-centroids at level-2) should provide effectively-K=4096*chunks-per-level lift, mirroring how StreamingLLM achieves effective-100k context with O(W) compute.

### TOP-1 CELL PROPOSAL: `exp_substrate_wm_chunked_vs_flat_K_scaling_v1`

**Hypothesis (falsifiable):** chunking-based scaffold (ultrametric-cluster K items into groups of 5-7, store cluster-centroid in WM bank-0 + per-cluster bank slot) outperforms flat-K-into-multi-bank at K in {50, 100, 200, 500, 1000} on a recall task where items must be retrieved AFTER a 200-step intervening distractor stream.

**Arms (5):**
1. `FLAT_K_RAND` — K items routed deterministically into n_banks=K/64 banks, rand_query (item-id given, return item-vec)
2. `FLAT_K_ADV` — same but adversarial overlap 0.20 (per current cell's discriminating regime)
3. `CHUNK_K_CENTROID` — ultrametric-cluster K items into c=K/6 clusters; bank-0 stores cluster centroids (recall: first probe cluster centroid via partial-cue, then probe item-within-cluster via second cleanup)
4. `CHUNK_K_CENTROID_ADV` — same with overlap 0.20
5. `HIERARCHICAL_2LEVEL` — chunk of chunks: K items -> 64 level-1 clusters -> 8 level-2 clusters; 3-step probe (level-2 -> level-1 -> item)

**Discriminator (falsifiable):**
- Define `chunking_lift(K) = CHUNK_K_CENTROID_recall(K) - FLAT_K_RAND_recall(K)`
- Prediction: chunking_lift(K=50) >= 0; chunking_lift(K=200) >= 0.10; chunking_lift(K=500) >= 0.20
- Anti-prediction (cell-FAIL): chunking_lift < 0 at any K (chunking actively hurts) OR flat_K_RAND already >=0.95 at K=500 (no headroom — by-construction-saturated, ratify k_per_bank instead).
- HARD_PASS: chunking_lift(K=500) >= 0.20 AND HIERARCHICAL_2LEVEL >= 0.85 at K=1000 AND adv_within=adv-rand <= 0.05.
- HARD_FAIL: flat-K-RAND already saturated at K=500 (=no test) OR chunking arm degrades vs flat (=mechanism broken).

**Testability status:** FULLY BUILDABLE NOW
- WM-multi-bank primitive: chain-grade (`hdlab/working_memory.py`)
- Ultrametric clustering primitive: chain-grade (`hdlab/ultrametric_clustering.py`)
- N_DIM=8192, K up to 1000 single-laptop ~6-8 CPU-hr (CPU-eligible per prompt)
- Smoke variant (K in {50, 200}, 3 seeds, single arm): <15min
- Routing: remote_cpu_queue (USER NO LOCAL directive)
- Cell-author smoke MUST fire discriminator at full-K=500 preview per "discriminator-must-survive-scale" rule (caught 3 prior cells)

**Dependencies:** none external. Builds on chain-grade primitives only. Smoke gates dispatch; full ~6-8 CPU-hr.

**Cross-link to multihop-WM-scaffold HARD_FAIL:** if this cell HARD_PASSES, the multi-hop failure is NOT a WM-capacity issue — it's a binding-fidelity issue (intermediate-state representation drift during chain traversal). That re-frames the multi-hop barrier toward decoder-side mechanisms (Belief Propagation / LDPC / RTS — see `notes/research_gap1_multihop_5x_drill_2026-06-26.md`) rather than WM-capacity rescues.

### P-estimate (Gap 1 top-1 HARD_PASS)
- Raw P(chunked >= flat at K=500) = 0.70 (math + brain + cross-domain all converge; substrate primitives chain-grade)
- Lit-scan deflation: -0.15 (substrate-native composition is novel; per-bank-capacity META rule may surface saturations)
- Brain-existence bump: +0.10 (Cowan + Ericsson chunking is THE brain solution to K scaling)
- **Deflated: P = 0.55**

---

## GAP 2: SUBSTRATE-VS-MD A/B HEAD-TO-HEAD

### PRIOR-ART CHECK
Full design doc already filed: `notes/research_drill_substrate_vs_md_head_to_head_proof_gate_design_2026-06-27.md`. 5 arms, 20-query corpus, 4-axis envelope (latency / completeness / freshness / robustness), ARM 5 SCALE_PROBE diagnostic. GATED on Wave 4 v2 tripwire-surfaced cell landing chain-grade + 1M-atom content-chunk KB built (not just 152-file smoke) + 24h continuous-ingest cadence proven.

This 3x drill EXTENDS the design with three angles the original doc didn't deeply explore.

### 3x angle synthesis

**ANGLE A — MATH (retrieval metrics: recall@k / precision@k / latency):**
BEIR benchmark (Thakur 2021) standardizes information-retrieval evaluation across 18 datasets: recall@10, nDCG@10, MRR. MTEB (Muennighoff 2022) extends to 56 tasks across 8 categories. Best-in-class dense retrievers (E5-large, BGE-large) hit nDCG@10 ~0.55 average MTEB; sparse-BM25 baselines hit ~0.42. Critical retrieval-eval insight: **per-query precision/recall has high variance** — single-query comparisons are MEANINGLESS; need N>=100 queries with macro-averaging + bootstrap CI. The existing 20-query corpus is UNDERPOWERED for tight bounds; either widen to 100 queries OR ship with explicit "indicative-only / N=20" caveat. Latency target: substrate <=2x MD is generous; competitive vector-DB latencies (Pinecone, Weaviate) hit p99<100ms at 1M vectors; MD-grep on 1M-tokens corpus runs ~1-3s on commodity SSD — substrate at <2s p99 is realistic but NOT guaranteed without quantization.

**ANGLE B — BRAIN (declarative-vs-procedural memory):**
Tulving (1972, 1985) declarative (episodic + semantic) vs procedural memory dissociation. Squire 1992 review: hippocampus-MTL for declarative; basal-ganglia/cerebellum/motor-cortex for procedural; double-dissociation in amnesic patients (HM episodic-impaired but procedurally intact). Critical brain insight for substrate-vs-MD: **the brain uses BOTH simultaneously** — fast cortical schema lookup (procedural, ~50-100ms automatic) + slow hippocampal episodic re-construction (declarative, ~500-1000ms effortful). Brain doesn't have to PICK one; it uses both for the same query type because they answer DIFFERENT subparts. Implication for cell: should NOT frame as "substrate REPLACES MD" — should frame as "substrate ADDS retrieval-modes MD cannot provide" (e.g., semantic-similarity / partial-cue / refuse-gate on unknowns). The verdict gate should test substrate-UNIQUE-VALUE not just substrate-PARITY.

**ANGLE C — CROSS-DOMAIN (vector-DB benchmarks: BEIR / MTEB / ANN-benchmarks):**
ANN-benchmarks.com tracks ~30 algorithms (HNSW, IVF, Faiss-Flat, ScaNN, Annoy) across recall-vs-QPS Pareto frontiers; HNSW dominates for recall>=0.95 with ~100k QPS at 1M-vectors-1024d. Production-scale vector-DB lessons: (1) **char-trigram cosine at 1M atoms gets noisy** — this is exactly what ARM 5 SCALE_PROBE catches; char-trigram encoders aren't trained on domain semantics, so cosine sim at high atom count surfaces too many false positives; (2) hybrid retrieval (BM25 + dense + reranker) consistently beats either alone by 5-15% nDCG; (3) chunking strategy matters more than embedding choice — overlap+sliding-window beats per-document. Implication for substrate-KB Wave 4: current content-chunk size and overlap settings are unverified; need ablation arm.

### TOP-1 CELL PROPOSAL: PER PRIOR DESIGN DOC + 3 EXTENSIONS

The design doc cell `exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1` is the TOP-1. Three EXTENSIONS this drill adds:

**Extension E1 — Widen query corpus (math angle):**
Current 20 queries underpowered for tight CI. Add 80 more queries (5 per existing bucket, plus 6 new buckets: cell-name lookup / atom-state / cert-headline / disagreement-arc / cross-cell-convergence / tool-name). Total 100; macro-avg + 1000-bootstrap 95% CI per arm. Time cost: +30min cell-author for query authoring; +20min cell wall for 5x more queries on full arm.

**Extension E2 — Add 6th arm `ARM_SUBSTRATE_UNIQUE_VALUE` (brain angle):**
Test 10 queries that MD cannot answer at all — e.g., "find notes semantically similar to X but NOT mentioning X by name"; "find atoms with concept-property Y even if Y-name absent"; "refuse-gate on totally-unknown query Z, return UNKNOWN not garbage". Substrate must hit semantic-similarity recall@5 >= 0.70 AND refuse-correctly on Z queries. If substrate provides retrieval-modes MD cannot, the cell's verdict graduates from "parity-with-MD" to "substrate-strictly-additive". This is the right framing per brain double-system rule.

**Extension E3 — Add chunk-ablation diagnostic arm `ARM_CHUNK_CONFIG_SWEEP` (cross-domain angle):**
Sweep chunk-size in {200, 500, 1000} tokens × overlap in {0, 50, 200} = 9 configs; for each, recompute content-completeness on 20-query base corpus. Picks Pareto-optimal config; flags whether current Wave 4 v2 default (chunk-size? overlap?) is on the frontier. If not, this surfaces a cheap re-ingest opportunity that lifts substrate scores BEFORE ritual-flip is even debated.

### Discriminator (falsifiable; per design doc + extensions)
- **HARD_PASS for ritual flip:** ALL 4 axes hit `hp_*` thresholds (latency <=2x MD; content-match >=0.95; freshness <=10min lag; robustness 100% fallback) AND ARM_SUBSTRATE_UNIQUE_VALUE recall>=0.70 with refuse-correct=1.0 AND ARM 5 SCALE_PROBE not degraded.
- **HARD_FAIL keeps MD canonical:** any `hf_*` axis tripped OR substrate-unique-value <=0.5 (no additive value over MD) OR ARM 5 catastrophic 1M-atom degradation (>50% completeness drop vs smoke-scale).
- **MIDDLE_BAND:** 3/4 axes + substrate-unique-value pass; file remediation route (E3 chunk-sweep usually unblocks).

### Testability status: PARTIALLY BUILDABLE
- **READY NOW:** design doc + 20-query corpus + ground-truth-build instructions exist; chunk-ablation primitive (Extension E3) can be authored as standalone cell against current 152-file content-chunk-KB
- **BLOCKED on Wave 4 v2 full ingest:** main cell needs 1M-atom KB built (not just smoke); per CRITICAL_CONTEXT the v2 tripwire-surfaced cell still in queue. UNTIL that lands, only smoke-scale arms can run.
- **PROPOSAL:** dispatch Extension E3 (chunk-config sweep) NOW as standalone diagnostic — it doesn't need 1M-atom KB; runs against current 152-file content-chunk KB; output informs whether current Wave 4 v2 default settings are Pareto-optimal BEFORE full ingest commits to a config. ~2 CPU-hr.

### Dependencies (Gap 2 main cell)
1. Wave 4 v2 tripwire-surfaced cell landed chain-grade by Skunkworks
2. Full 1M-atom content-chunk KB built (verify via `ls data/substrate_director_kb_chunk_v1/` shows expected atom count)
3. Scheduled task `hd_director_kb_continuous_ingest` proven cadence >=24h (5-min cadence stable; no atomic-swap races; verified post commit 5de28ea1)
4. Extension E3 (chunk-config sweep) PRECEDES main cell (informs config choice for full ingest)

### P-estimate (Gap 2 main cell HARD_PASS for ritual flip)
- Raw P(substrate-KB hits all 4 axes + substrate-unique-value on 100 queries at 1M-atom scale) = 0.45 (char-trigram encoder is the weak link; scale degradation is real risk)
- Lit-scan deflation: -0.15 (vector-DB benchmarks show char-trigram is sub-SOTA; production needs trained embeddings)
- **Deflated: P = 0.35**
- HARD_FAIL probability ~0.30; MIDDLE_BAND ~0.35; **honest framing for USER: substrate is more likely to be additive-not-replacement than to win head-to-head — Extension E2 framing protects the cell's value-claim regardless of head-to-head outcome.**

---

## SUMMARY TABLE

| Gap | Top-1 cell | Testability | Dependencies | P(HARD_PASS) | Wall |
|---|---|---|---|---|---|
| 1 (WM K-scaling) | `exp_substrate_wm_chunked_vs_flat_K_scaling_v1` | FULLY BUILDABLE NOW | none external; chain-grade primitives | 0.55 | ~6-8 CPU-hr full / <15min smoke |
| 2 (substrate-vs-MD) | `exp_substrate_vs_md_head_to_head_v1` (per prior design doc + 3 extensions) | PARTIALLY (Extension E3 ships now; main cell GATED) | Wave 4 v2 full ingest + 24h continuous-ingest + E3 chunk-config sweep | 0.35 main / 0.65 E3 alone | ~30-60min main / ~2-hr E3 |

---

## NEXT ACTIONS (Director, immediate)

1. Dispatch `hdi_exp_dev` for Extension E3 chunk-config sweep against current 152-file content-chunk KB (~2 CPU-hr; unblocks Wave 4 v2 config choice).
2. Dispatch `hdi_exp_dev` for `exp_substrate_wm_chunked_vs_flat_K_scaling_v1` smoke (uses chain-grade primitives only; <15min smoke; if HARD_PASS, full ~6-8 CPU-hr on remote_cpu_queue).
3. Director cross-link this drill to `data/director_plan.json` per anti-drift discipline (update at decision points).
4. Wait for Wave 4 v2 tripwire-surfaced cell landing before dispatching Gap 2 main cell.

---

**End of 3x drill.** Both top-1 cells have falsifiable discriminators + testability classification + dependency lists. Gap 1 is ship-ready NOW; Gap 2 main is gated but Extension E3 is ship-ready NOW.
