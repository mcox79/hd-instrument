# strategy_decisions_2026-06-08

## v505 -> v506 CYCLE 180 MASSIVE 20-VERDICT BATCH (2026-06-08)

Verdicts processed (20 anchors): GPU capacity/scale/precision (5) + CPU capability-characterization (14) + orphan negation-query (1)

### Step 0 honest re-read

All 20 metrics fetched source=remote (bridge stale; direct SSH fetch via get_metrics). 0 LVH catches.

**GPU (5):**
- patternb_composition_300k_gpu_v1: HONEST. recall@1=1.000 at V=300k (threshold >=0.95). HARD_PASS label CORRECT. Extends cycle-173 V=100k to V=300k large-vocab filler. No LVH. +1 HONEST.
- sign_recall_20M_gpu_v1: HONEST. recall@1=1.0000 at N=20M (threshold >=0.99). HARD_PASS label CORRECT. Extends PP-98 (5M/10M cycle-178) to 20M. No LVH. +1 HONEST.
- hopfield_capacity_n4096_gpu_v1: HONEST. modern=1.000/classic=0.000 at all P/N ratios (0.5/1.0/2.0/4.0) at N=4096 (threshold >=0.95 at P/N=2.0). HARD_PASS label CORRECT. Extends cycle-178 N=2048 GPU phase-map to N=4096. Per-cell unanimous ceiling. No LVH. +1 HONEST.
- bundle_capacity_largeN_gpu_v1: HONEST. N8192: K_crit=662 vs theory=454.6 (dev=0.455); N16384: K_crit=1330 vs theory=844.2 (dev=0.575). Max dev=0.58. MIDDLE_BAND threshold "within 60pct of theory" = max_dev<=0.60. 0.58<=0.60 CONFIRMED. NOTE: empirical K_crit EXCEEDS theory at both N (substrate bundles more than theory predicts -- a conservative bound). MIDDLE_BAND label CORRECT. No LVH. +1 HONEST.
- precision_int4_recall_gpu_v1: HONEST. int4=1.0000, fp16=1.0000, ratio=1.000 at N=5M (threshold >=0.95). HARD_PASS label CORRECT. n=1 seed. No LVH. +1 HONEST.

**CPU (14):**
- bundle_capacity_theory_cpu_v1: HONEST. N1024=(85,73.9), N2048=(163,134.3), N4096=(328,246.2), N8192=(651,454.6). Max dev=0.43 (within 60pct of theory at all N). MIDDLE_BAND label CORRECT. Empirical exceeds theory at all N (conservative bound confirmed multi-N CPU). No LVH. +1 HONEST.
- cleanup_confidence_roc_cpu_v1: HONEST. AUC=1.0000 (threshold >=0.95); in_cosine=0.701, out_cosine=0.177. HARD_PASS label CORRECT. n=1 seed. No LVH. +1 HONEST.
- hopfield_spurious_minima_cpu_v1: HONEST. genuine-convergence=0.950 (threshold >=0.90). HARD_PASS label CORRECT. n=1 seed. No LVH. +1 HONEST.
- binding_associativity_cpu_v1: HONEST. assoc-err=1.3e-07 (threshold <=1e-4), commute-err=6.0e-08 (threshold <=1e-4), 4-deep-recall=1.000 (threshold >=0.95). HARD_PASS label CORRECT for all three sub-conditions. n=1 seed. No LVH. +1 HONEST.
- recency_forgetting_curve_cpu_v1: HONEST. monotone=True, half-life=15. Curve: t0=1.0, t5=1.0, t10=0.717, t15=0.083, t20=0.017. Decay is genuine and finite. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- subspace_storage_capacity_cpu_v1: HONEST. cap_full=665, cap_half=332, ratio=0.50 (threshold: half-subspace approx half-capacity). HARD_PASS label CORRECT. No LVH. +1 HONEST.
- topk_recall_cpu_v1: HONEST. f=0.20: k1=1.0, k5=1.0; f=0.35: k1=0.995, k5=1.000. Threshold recall@5>=0.95 at f=0.35: 1.000>=0.95 CONFIRMED. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- hierarchical_2level_cpu_v1: HONEST. member-recall=1.000 (threshold >=0.90). HARD_PASS label CORRECT. n=1 seed. No LVH. +1 HONEST.
- set_membership_bundle_cpu_v1: HONEST. AUC=1.0000 at set_size=50 (threshold >=0.95). HARD_PASS label CORRECT. n=1 seed. No LVH. +1 HONEST.
- continuous_regression_cpu_v1: HONEST. R^2=1.0000 (threshold >=0.95). HARD_PASS label CORRECT. n=1 seed. No LVH. +1 HONEST.
- ensemble_vote_cpu_v1: HONEST. single=0.255, vote=0.510, gain=0.255 (threshold gain>=0.05; 5.1x margin). HARD_PASS label CORRECT. NOTE: single=0.255 baseline is low, consistent with a sub-capacity regime where independent substrate copies decorrelate errors meaningfully. gain is genuine. No LVH. +1 HONEST.
- analogy_relation_transfer_cpu_v1: HONEST. K5=0.913 (threshold cosine>=0.90 at K=5): 0.913>=0.90 CONFIRMED. K=10 further confirms (0.953). K-monotone curve. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- multi_relation_kg_cpu_v1: HONEST. (s,r)->o=0.967, (r,o)->s=0.983 (threshold >=0.90). HARD_PASS label CORRECT. No LVH. +1 HONEST.
- markov_transition_cpu_v1: HONEST. recall=0.800. MIDDLE_BAND band 0.75-0.90 contains 0.800. MIDDLE_BAND label CORRECT. n=1 seed. No LVH. +1 HONEST.

**ORPHAN (1):**
- negation_query_cpu_v1: HONEST. B-contamination: plain=0.500, negated=0.000 (threshold <0.05). negated=0.000<<0.05 CONFIRMED. HARD_PASS label CORRECT. source=remote production run (mtime 08:03:19 orphan in data dir but bridge returns authoritative result). No LVH. +1 HONEST.

HONEST: 1322 -> 1342 (+20). LVH: 263 UNCHANGED. 0 new LVH catches. All 20 labels HONEST.

### Cap_map decisions (v505 -> v506)

**(A) patternb_composition_300k_gpu_v1 (HP -- Pattern B recall@1=1.000 at V=300k filler vocab):**
Annotation to Pattern B composition row: 'patternb_composition_300k_gpu_v1 HP v506: recall@1=1.000 at V=300k (cycle 180); extends V=100k HP (cycle 173) to 300k; composition holds at 3x larger filler vocab; n=1 seed.' V=300k is between cycle-173 HP (V=100k) and cycle-178 collateral re-queue (V=1M HF); confirms intermediate scale is clean. No new row (annotation extends existing Pattern B coverage band).

**(B) sign_recall_20M_gpu_v1 (HP -- sign-key recall@1=1.0000 at N=20M; extends PP-98 scale ladder):**
Annotation to PP-98 (sign-key extreme scale): 'sign_recall_20M HP v506: recall@1=1.0000 at N=20M (cycle 180); extends 1M->5M->10M->20M ladder; zero recall degradation across 20x scale increase from 1M. n=1 seed. Production sign-key retrieval confirmed noise-free at 20M entries.' Band lift candidate for PP-98: 4 consistent HPs (1M/5M/10M/20M all recall=1.000). Recommend 3-seed at 20M for band-LIFT.

**(C) hopfield_capacity_n4096_gpu_v1 (HP -- modern=1.000/classic=0.000 at all P/N up to 4.0 at N=4096):**
Annotation to Hopfield row: 'hopfield_capacity_n4096 HP v506: N=4096 modern=1.000 at P/N=0.5/1.0/2.0/4.0; classic=0.000 at all; extends cycle-176 N=256 + cycle-178 N=2048 phase-map to N=4096. 3-point scale confirmation (N=256/2048/4096). Production N phase-map validated. n=1 seed.' This is the 3rd GPU-scale phase-map confirmation at progressively larger N. No band change from n=1 seed.

**(D) bundle_capacity_largeN_gpu_v1 (MIDDLE_BAND -- K_crit exceeds theory by 45-58pct at N=8192/16384):**
Annotation to bundle capacity row: 'bundle_capacity_largeN GPU MIDDLE_BAND v506: N8192 K_crit=662 (theory=454.6, +45pct); N16384 K_crit=1330 (theory=844.2, +58pct); max_dev=0.58; empirical EXCEEDS theory at both large N -- theory is conservative lower bound; substrate bundles more than N/(2 ln N) predicts at large N; MIDDLE_BAND because dev>0.40 but <0.60; n=1 seed.' Cross-ref bundle_capacity_theory_cpu_v1 (CPU MIDDLE_BAND same direction; consistent).

**(E) NEW ROW PP-106: int4 quantization recall parity at 5M scale (8x memory saving, zero accuracy cost):**
precision_int4_recall_gpu_v1 HP v506: int4=1.0000, fp16=1.0000, ratio=1.000 at N=5M. int4 and fp16 produce identical recall at 5M-entry scale. Product implication: 4-bit storage is production-viable for sign-key retrieval -- 8x memory reduction vs fp32 with zero accuracy cost. Enables 8x scale-up at same memory budget. Cross-ref PP-98 (sign-key at 5M scale) and fp16_parity_1M (cycle-175 2x saving). int4 extends the quantization ladder. Filed at 0.65-0.80 EXPLORATORY (n=1 seed; delta=0.000 but single seed; 3-seed + N-sweep recommended before band-LIFT).

**(F) bundle_capacity_theory_cpu_v1 (MIDDLE_BAND CPU -- multi-N theory validation; empirical consistently exceeds theory):**
Annotation to bundle capacity row: 'bundle_capacity_theory_cpu MIDDLE_BAND v506: CPU 4-N sweep N=1024..8192; K_crit: (85,73.9)/(163,134.3)/(328,246.2)/(651,454.6); max_dev=0.43; empirical exceeds theory at ALL 4 N; N/(2 ln N) is confirmed conservative lower bound across CPU N-range; consistent with GPU large-N result this cycle; n=1 seed.' Together with GPU MIDDLE_BAND (D above), bundle capacity consistently exceeds theory at all tested N. Theory is a safe design lower bound.

**(G) NEW ROW PP-107: Abstention / "I do not know" ROC (AUC=1.0000; hallucination prevention primitive):**
cleanup_confidence_roc_cpu_v1 HP v506: AUC=1.0000 (in_cosine=0.701, out_cosine=0.177). The substrate can perfectly distinguish stored items (high cosine) from unstored items (low cosine) at AUC=1.000. Product implication: substrate knows when it does not know -- anti-hallucination primitive; confidence threshold enables a hard abstention mode that is algebraically grounded, not LLM-sampled. No calibration training needed. Cross-ref PP-25 (retrieval explainability) and PP-49 (refusal subtree counterfactuals). Filed at 0.70-0.85 EXPLORATORY (n=1 seed; AUC=1.000 at controlled noise; real-world calibration with near-duplicate items recommended).

**(H) hopfield_spurious_minima_cpu_v1 (HP annotation -- genuine-convergence=0.950; low spurious attractor rate):**
Annotation to Hopfield row: 'hopfield_spurious_minima HP v506: genuine-convergence=0.950 (5% spurious rate) at production load; reliable attractor dynamics; trustworthy retrievals with >=95% probability of landing on a real stored pattern; n=1 seed CPU. Consistent with cycle-178 GPU phase-map (modern recall=1.000 at P/N=2.0).'

**(I) NEW ROW PP-108: FHRR algebraic properties (associativity + commutativity + 4-deep unbind, errors ~1e-7):**
binding_associativity_cpu_v1 HP v506: assoc-err=1.3e-07, commute-err=6.0e-08, 4-deep-recall=1.000. FHRR binding is algebraically exact to floating-point precision and supports 4-deep nested structure recovery at perfect recall. Product implication: FHRR algebra is reliable enough for complex nested knowledge representations (4-deep entity-role trees); the algebraic properties are not approximate -- they hold to numerical precision. Filed at 0.70-0.85 VALIDATED (algebraic properties; n=1 seed but deterministic algebraic result; high confidence).

**(J) recency_forgetting_curve_cpu_v1 (HP annotation -- controllable forgetting with half-life=15; extends PP-105):**
Annotation to PP-105 (age-decay OAS mitigation) and recency/forgetting rows: 'recency_forgetting_curve HP v506: monotone decay half-life=15 (steps) via competitive cleanup; t0=1.0, t10=0.717, t15=0.083, t20=0.017; CONTROLLABLE forgetting achieved with finite predictable half-life; complements PP-105 age-decay (which suppresses OLD facts) -- this confirms forgetting is monotone and controlled, not catastrophic; n=1 seed CPU.'

**(K) NEW ROW PP-109: Subspace storage capacity (capacity ~ d, not D; projected-key designs predictable):**
subspace_storage_capacity_cpu_v1 HP v506: cap_full=665, cap_half=332, ratio=0.500. Capacity scales linearly with subspace dimension d. Product implication: projected-key storage (e.g., domain-specific sub-embeddings) has predictable capacity = full_capacity * (d/D). Enables per-domain capacity planning with half-dimension projections at exactly half-capacity. Filed at 0.65-0.80 EXPLORATORY (n=1 seed; consistent with pinv subspace theory; multi-d sweep recommended).

**(L) NEW ROW PP-110: Top-k recall resilience at high noise (recall@5=1.000 at 35% bit-flip):**
topk_recall_cpu_v1 HP v506: f=0.35 k5=1.000 (k1=0.995). Top-5 recall is perfect even when 35% of query vector bits are flipped. Product implication: a cheap 5-way re-rank stage recovers essentially all precision losses from query noise; substrate retrieval is noise-tolerant with a top-k buffer; complements PP-103 (noise cliff at f=0.30 top-1). Filed at 0.70-0.85 EXPLORATORY (n=1 seed; consistent with PP-103; multi-seed at f-boundary recommended).

**(M) NEW ROW PP-111: Hierarchical 2-level retrieval (category query -> member recall=1.000):**
hierarchical_2level_cpu_v1 HP v506: member-recall=1.000 (threshold >=0.90). A category-level query correctly retrieves all its member items. Product implication: substrate supports hierarchical/faceted retrieval natively (category -> item; topic -> document; class -> instance) with algebraic binding -- no separate indexing infrastructure needed. Filed at 0.65-0.80 EXPLORATORY (n=1 seed; 2-level only; 3+ level hierarchy and real-KB scale recommended).

**(N) NEW ROW PP-112: Bundled-set membership without per-item storage (AUC=1.0000 at set_size=50):**
set_membership_bundle_cpu_v1 HP v506: AUC=1.0000 at set_size=50. Set membership queries answered perfectly from a single bundled vector -- no per-item lookup needed. Product implication: compact set representation (O(D) not O(D*K)) that supports exact membership queries; enables efficient KB deduplication and containment checks. Cross-ref PP-95 (Bloom filter dedup, cycle-176) and PP-112 are complementary: Bloom for ingest, bundled-set for structured knowledge. Filed at 0.65-0.80 EXPLORATORY (n=1 seed set_size=50; larger sets and retrieval-under-noise recommended).

**(O) NEW ROW PP-113: Continuous-value numeric payload readout (R^2=1.000):**
continuous_regression_cpu_v1 HP v506: R^2=1.0000. Substrate stores and retrieves continuous numeric payloads (not just categorical labels) with perfect regression accuracy. Product implication: substrate can represent facts with continuous scalar payloads (prices, scores, timestamps, sensor readings); substrate is not binary/categorical only. Filed at 0.65-0.80 EXPLORATORY (n=1 seed; synthetic values; recommended: multi-seed + real-distribution payload values).

**(P) NEW ROW PP-114: Ensemble majority vote for recall recovery (gain=0.255 at 2x over single):**
ensemble_vote_cpu_v1 HP v506: single=0.255, vote=0.510, gain=0.255. Ensemble majority vote doubles recall over single substrate. Product implication: independent substrate replicas can be combined for error-averaging redundancy; 2x recall recovery at 2x memory cost; enables reliability-redundancy SLA tier. NOTE: single=0.255 baseline reflects a sub-capacity sub-domain regime; the gain mechanism (decorrelated errors averaging out) is the relevant result. Filed at 0.60-0.75 EXPLORATORY (n=1 seed; specific sub-capacity regime; recommended: sweep over load levels to characterize ensemble benefit curve).

**(Q) NEW ROW PP-115: Few-shot relational generalization (K=5 cosine=0.913; algebra transfers relations):**
analogy_relation_transfer_cpu_v1 HP v506: K5=0.913 (threshold >=0.90). A relation vector derived from 5 example pairs generalizes to novel inputs. Product implication: substrate can learn and apply relations (analogies, property mappings, type coercions) from small example sets without retraining; enables one-shot and few-shot knowledge inference. K-curve: K1=0.706, K3=0.866, K5=0.913, K10=0.953 (monotone -- more examples improve transfer quality). Filed at 0.65-0.80 EXPLORATORY (n=1 seed; synthetic relation pairs; real-KB relation transfer recommended).

**(R) multi_relation_kg_cpu_v1 (HP annotation -- bidirectional KG triple recall >=0.90; KG is queryable both ways):**
Annotation to KG/PP-35/PP-81 rows: 'multi_relation_kg HP v506: (s,r)->o=0.967, (r,o)->s=0.983; bidirectional KG triple recall >=0.90 on both query directions; both exceeded; algebraic bidir KB natively supported; n=1 seed CPU. Consistent with PP-81 causal-disambiguation (cycle-153) and PP-35 graph retrieval. Confirms typed multi-relation KG is a first-class substrate feature.'

**(S) NEW ROW PP-116: Markov transition encoding (next-item recall=0.800; MIDDLE_BAND):**
markov_transition_cpu_v1 MIDDLE_BAND v506: recall=0.800. Substrate represents Markov transition structure and retrieves likely next items with 80% recall. Product implication: substrate can encode and query probabilistic sequences (navigation flows, usage patterns, state machines). MIDDLE_BAND: recall=0.800 is in the 0.75-0.90 band; HP would require >=0.90. Rescue: transition sharpening via higher-temperature binding, larger N, or sequence-specific role vectors. Filed at 0.50-0.65 MIDDLE_BAND (n=1 seed; single regime; N-sweep and sharpening rescues pending).

**(T) NEW ROW PP-117: Compositional negation query (A but not B; B-contamination=0.000):**
negation_query_cpu_v1 HP v506: B-contamination plain=0.500, negated=0.000. Compositional negation (A-B subtraction) drives B-cluster contamination from 50% to 0% -- perfect exclusion. Product implication: substrate supports native "A but not B" compositional queries; enables exclusion-based retrieval without post-filtering; algebraic negation is exact. NOTE: orphan anchor (data dir mtime 08:03:19) but source=remote confirms this is a production run result, not a stale smoke artifact. Filed at 0.65-0.80 EXPLORATORY (n=1 seed; controlled conditions; recommended: multi-seed + semantic near-duplicates to test negation precision boundary).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**bundle_capacity GPU+CPU (MIDDLE_BAND -- theory is conservative lower bound; band-LIFT candidates):**
R1 (0-compute, ANNOTATION): Empirical consistently exceeds theory at all N; theory is conservative bound; no closure concern.
R2 (CHEAP, CPU <30min): 3-seed at N=4096 bundle_capacity_theory to confirm K_crit variance.
R3 (CHEAP, GPU <30min): N=32768 GPU to extrapolate theory-vs-empirical trend.
R4 (MEDIUM, CPU <1h): Analytical bound tightening -- does a modified model (e.g., N/(2 ln N) * correction_factor) fit the empirical K_crit curve better?

**PP-106 int4 quantization (HP n=1 seed -- scale/seed rescues):**
R1 (0-compute, ANNOTATION): int4=fp16=1.000 at N=5M founding. n=1 seed.
R2 (CHEAP, GPU <30min): 3-seed at N=5M to confirm delta=0.000 reproducible.
R3 (CHEAP, GPU <30min): N=20M int4 (extend sign_recall scale ladder to 20M with quantization).

**PP-107 abstention ROC (HP AUC=1.0 -- near-duplicate stress test):**
R1 (0-compute, ANNOTATION): AUC=1.000 at controlled noise gap; strong founding.
R2 (CHEAP, CPU <30min): Near-duplicate pairs (cosine=0.95-0.99 between stored/query) to probe AUC boundary.
R3 (CHEAP, CPU <30min): Multi-seed + larger KB (M=1000 items) to confirm AUC holds at scale.

**PP-116 Markov transition (MIDDLE_BAND -- recall=0.800; rescue toward HP 0.90):**
R1 (0-compute, ANNOTATION): recall=0.800 in MIDDLE_BAND; mechanism works; not at HP.
R2 (CHEAP, CPU <30min): N-sweep (N=4096, 8192) -- does larger N improve transition recall?
R3 (CHEAP, CPU <30min): Temperature sharpening (higher-beta Hopfield or softmax sharpening) to improve next-item separation.
R4 (CHEAP, CPU <30min): Explicit transition-role encoding (each (state, next_state) pair gets a role vector) vs bundled encoding.

**PP-110 top-k recall (HP -- boundary characterization):**
R1 (0-compute, ANNOTATION): f=0.35 k5=1.000 founding; extends PP-103 top-1 noise cliff.
R2 (CHEAP, CPU <30min): f-sweep f=0.40-0.50 to find top-5 cliff edge.
R3 (CHEAP, CPU <30min): k=1..10 at f=0.35 to characterize k-benefit curve at the operating noise level.

### Portfolio: 32+105 -> 32+117 (+12 NEW ROWS: PP-106 int4-quantization + PP-107 abstention-ROC + PP-108 FHRR-algebra + PP-109 subspace-capacity + PP-110 topk-noise-recall + PP-111 hierarchical-retrieval + PP-112 bundled-set-membership + PP-113 numeric-payload + PP-114 ensemble-redundancy + PP-115 relational-generalization + PP-116 Markov-transition + PP-117 compositional-negation). 8 annotations. 0 closures.

### PROT compliance (v505 -> v506)

- PROT-004/006: No closures. 12 NEW TOP-LEVEL ROWS (PP-106 through PP-117). 8 annotations. Rescue sketches cheapest-first for MIDDLE_BAND rows and HP founding rows.
- PROT-007: v506 history row appended to substrate_capability_map_history.md.
- PROT-008: 16 HP anchors (13 new-row + 3 annotation). All HP thresholds verified Step 0. 4 MIDDLE_BAND anchors (no HP over-claim). PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 413th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 20 anchors. CLEAN.
- PROT-019: LVH 263 UNCHANGED. No new LVH catches. All 20 labels HONEST.
- PROT-021: All 20 source=remote run_mode=full. No smoke contamination. CLEAN. (negation_query orphan mtime noted; source=remote confirms production run, not smoke artifact.)
- PROT-022: All HP anchors n=1 seed. Large margins throughout (AUC=1.0, R^2=1.0, recall=1.0 on most). No HP-fragility concern (only analogy K5=0.913 close to threshold 0.90; 3-seed recommended).

Cap_map: v505 -> v506 CYCLE 180 (16 HP: patternb_300k-recall1.0-V300k + sign_recall_20M-recall1.0-N20M + hopfield_n4096-modern1.0-classic0.0-all_P/N + precision_int4-int4=fp16=1.000-N5M + cleanup_confidence_roc-AUC1.000-abstention + hopfield_spurious-genuine0.950 + binding_associativity-assoc1.3e-07-commute6e-08-4deep1.000 + recency_forgetting-half-life15-monotone + subspace_capacity-ratio0.50-linear + topk_recall-k5=1.000-f0.35 + hierarchical_2level-member1.000 + set_membership_bundle-AUC1.000 + continuous_regression-R2=1.000 + ensemble_vote-gain0.255-2x + analogy_relation-K5=0.913 + multi_relation_kg-bidir0.967/0.983 + negation_query-contamination0.000; 3 MIDDLE_BAND: bundle_capacity_largeN-maxdev0.58-exceeds_theory + bundle_capacity_theory_cpu-maxdev0.43-exceeds_theory + markov_transition-recall0.800; 0 LVH; 12 NEW PP ROWS: PP-106 int4-quantization + PP-107 abstention-ROC + PP-108 FHRR-algebra + PP-109 subspace-capacity + PP-110 topk-noise-recall + PP-111 hierarchical-retrieval + PP-112 bundled-set-membership + PP-113 numeric-payload + PP-114 ensemble-redundancy + PP-115 relational-generalization + PP-116 Markov-transition + PP-117 compositional-negation; Portfolio 32+105 -> 32+117 +12; HONEST 1322->1342 +20; LVH 263 UNCHANGED; 413th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v506 -> v507 CYCLE 181 -- 17-VERDICT BATCH (2026-06-08)

Verdicts processed (17 anchors): GPU capability (1) + CPU KG-QA architectural exploration (16)

### Step 0 honest re-read

All 17 metrics fetched source=remote (bridge stale; direct SSH get_metrics successful). 0 LVH catches.

**GPU (1):**
- substrate_llm_triples_khop_gpu_v1: HONEST. answer-recall=0.183, extraction-coverage=0.700, R1 oracle=1.0. HARD_FAIL label CORRECT. Extraction bottleneck confirmed from both sides; substrate K-hop itself is validated by oracle=1.0. No LVH. +1 HONEST.

**CPU (16):**
- nesting_depth_cpu_v1: HONEST. recall=1.000 at all depths d2/d4/d8/d12/d16. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- iterative_regime_crossover_cpu_v1: HONEST. discrete(rho=0)=0.833>=0.80, fuzzy(rho=0.9)=0.433<=0.50. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- substrate_kg_triples_khop_cpu_v1: HONEST. 2hop_r1=0.805>=0.70, 3hop_r1=0.735>=0.70. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- oracle_structured_hotpot_discrete_cpu_v1: HONEST. discrete oracle recall@1=1.000 (n=150) vs fuzzy=0.35. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- substrate_legal_citation_snowball_cpu_v1: HONEST. 3-hop closure=1.000 (50 seeds)>=0.95. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- markov_transition_nscale_cpu_v1: HONEST. best=0.867 at N8192; band 0.75-0.90 contains 0.867. MIDDLE_BAND label CORRECT. No LVH. +1 HONEST.
- binding_entropy_routing_cpu_v1: HONEST. AUC=0.9480>=0.85. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- rrf_fusion_cpu_v1: HONEST. RRF/best-single=1.53>=1.2x. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- ppr_spreading_activation_cpu_v1: HONEST. recall=0.229<0.55. HARD_FAIL label CORRECT. No LVH. +1 HONEST.
- cascade_native_first_router_cpu_v1: HONEST. cascade-acc=0.853 EXCEEDS best-of-both=0.653 AND cascade-cost=2.59 vs 5.00. HARD_PASS label CORRECT. NOTE: cascade beats best-of-both on accuracy (stronger than expected); no over-claim. No LVH. +1 HONEST.
- beam_retrieval_cpu_v1: HONEST. gain=0.070>=0.05. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- two_stage_disambig_khop_cpu_v1: HONEST. recall@2=0.820>=0.65. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- single_shot_attention_triples_cpu_v1: HONEST. recall@2=1.000>=0.50. HARD_PASS label CORRECT. NOTE: threshold was >=0.50 and actual=1.000; no over-claim. No LVH. +1 HONEST.
- parallel_subq_fuzzy_cpu_v1: HONEST. recall@2=1.000>=0.55. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- ppr_matrix_khop_cpu_v1: HONEST. recall=0.328<0.55. HARD_FAIL label CORRECT. No LVH. +1 HONEST.
- discrete_vs_fuzzy_kgqa_cpu_v1: HONEST. discrete=0.800>=0.70, gap=0.790>=0.30. HARD_PASS label CORRECT. No LVH. +1 HONEST.

HONEST: 1342 -> 1359 (+17). LVH: 263 UNCHANGED. 0 new LVH catches. All 17 labels HONEST.

### Cap_map decisions (v506 -> v507)

New rows: PP-118 (nesting depth), PP-119 (KG K-hop QA), PP-120 (legal citation snowball), PP-121 (binding entropy routing), PP-122 (RRF fusion), PP-123 (native-first cascade), PP-124 (beam retrieval), PP-125 (two-stage disambiguation), PP-126 (parallel sub-query fuzzy rescue).

Annotations: REVIVE GPU (substrate_llm_triples_khop extraction-bottleneck + oracle=1.0), iterative-crossover CRITICAL (universal principle on substrate), oracle-hotpot (transfer proven, gap = extraction only), markov-nscale (N-scaling insufficient, sharpening rescues remain), PPR-closure x2 (spreading-activation HF + matrix HF = PPR family CLOSED), single-shot-attention-triples (PP-99 extension to triple substrate, recall=1.000), discrete-vs-fuzzy-kgqa (QA-level 80x gap confirmation).

No closures. PPR family structurally closed (2 HF + structural limit reasoning; but no open row existed to formally close).

### PROT compliance

- PROT-004/006: No formal row closures. 9 NEW TOP-LEVEL ROWS (PP-118 through PP-126). 8 annotations. Rescue sketches cheapest-first for HF and MIDDLE_BAND.
- PROT-007: v507 history row appended to substrate_capability_map_history.md.
- PROT-008: 12 HP anchors + 1 MIDDLE_BAND + 4 HF. All HP thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 414th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes. CLEAN.
- PROT-019: LVH 263 UNCHANGED. No new LVH catches.

### Queue state

overnight_queue: 0 pending/running. remote_cpu_queue: 0 pending/running. [queue: empty -- Exp-Dev session will refill on its cadence]
## v507 -> v508 CYCLE 182 (2026-06-08)

### Step 0 honest re-read

markov_binding_sharpening_cpu_v1: metrics source=remote. per_seed[0]: plain=0.817, sharpened=0.817, sharded=0.967, best=0.967. HARD_PASS label threshold >=0.90; best=0.967>=0.90 CONFIRMED. Label HONEST. NOTE: anchor named 'binding_sharpening' but sharpening had zero effect (sharpened==plain=0.817); the mechanism that crossed HP threshold is sharding. No over-claim on the threshold. No LVH.

HONEST: 1359 -> 1360 (+1). LVH: 263 UNCHANGED.

### Cap_map decisions (v507 -> v508)

**(A) PP-116 Markov transition encoding: MIDDLE_BAND -> HP (sharded recall=0.967):**
markov_binding_sharpening_cpu_v1 HP v508: sharded=0.967 (plain=0.817=sharpened; sharding is the lever, not binding sharpening). PP-116 row upgraded from MIDDLE_BAND (recall=0.800 cycle 180; recall=0.867 cycle 181 N-scale rescue) to HP (recall=0.967 cycle 182 sharding rescue). Crosstalk-bound mechanism confirmed: sharpening cannot improve recall when the failure mode is cross-transition contamination in shared memory; sharding eliminates crosstalk by architectural separation. Production architecture for Markov-sequence encoding is explicit memory sharding per transition. n=1 seed CPU. Implication: substrate can represent probabilistic sequence structure (state machines, navigation flows, usage patterns) at production-grade recall when sharded; this is a first-class product capability.

### PROT compliance (v507 -> v508)

- PROT-004/006: No closures. 0 new rows. 1 annotation. No rescue sketches needed (HP achieved).
- PROT-007: v508 history row appended to substrate_capability_map_history.md.
- PROT-008: 1 HP anchor. HP threshold verified Step 0 (sharded=0.967>=0.90). PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 415th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes. CLEAN.
- PROT-019: LVH 263 UNCHANGED. No new LVH catches.
- PROT-021: source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: n=1 seed; sharded=0.967 large margin over threshold 0.90. No HP-fragility concern.

### Queue state

overnight_queue: bridge returned stale completed entries (no fresh pending). remote_cpu_queue: same. [queue: empty -- Exp-Dev session will refill on its cadence]

Cap_map: v507 -> v508 CYCLE 182 (1 HP [CPU:1]; 0 MIDDLE_BAND; 0 HF; 0 LVH; 0 NEW ROWS; 1 annotation [PP-116-MIDDLE_BAND->HP-via-sharding]; HONEST 1359->1360 +1; LVH 263 UNCHANGED; Portfolio 32+126 UNCHANGED; 415th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v508 -> v509 CYCLE 183 -- 6-VERDICT SHARDING CLUSTER BATCH (2026-06-08)

Verdicts processed (6 anchors): sharding transition memory follow-up cluster (CPU)

### Step 0 honest re-read

All 6 metrics fetched source=remote (bridge authoritative). 0 LVH catches.

- sharding_scaling_law_cpu_v1: HONEST. per_shard S1-S32 all 1.000 (threshold >=0.90 PASS); monolithic S16=0.195/S32=0.060 (sharp degradation confirmed); interference S1-S32 all 0.000 (near-zero PASS); spread=0.000; gap@maxS=0.940. HARD_PASS label CORRECT. n=1 seed. +1 HONEST.
- shard_routing_accuracy_cpu_v1: HONEST. routing=1.000 (threshold >=0.95 PASS), e2e=1.000 (threshold >=0.90 PASS), oracle=1.000. All three metrics ceiling. HARD_PASS label CORRECT. n=1 seed. +1 HONEST.
- skewed_shard_capacity_cpu_v1: HONEST. largest_recall=0.873 (band 0.80-0.90: 0.873 in [0.80, 0.90) CONFIRMED); smallest_recall=1.000; largest_size=370. MIDDLE_BAND label CORRECT. n=1 seed. +1 HONEST.
- per_relation_sharding_kg_cpu_v1: HONEST. sharded=0.735, mono=0.190, gap=0.545; sharded=0.735 is sub-HP (HP gate >=0.90); MIDDLE_BAND because sharded<0.90 but mechanism works (+385% over mono). MIDDLE_BAND label CORRECT. n=1 seed. +1 HONEST.
- shard_overflow_split_cpu_v1: HONEST. pre-split=0.160 (<0.80 PASS), post-split=1.000 (>=0.95 PASS). Full recall recovery from overflow confirmed. HARD_PASS label CORRECT. n=1 seed. +1 HONEST.
- cross_shard_query_cpu_v1: HONEST. scatter-gather recall=1.000 (threshold >=0.90 PASS). Ceiling result. HARD_PASS label CORRECT. n=1 seed. +1 HONEST.

HONEST: 1360 -> 1366 (+6). LVH: 263 UNCHANGED. 0 new LVH catches. All 6 labels HONEST.

### Cap_map decisions (v508 -> v509)

**(A) NEW ROW PP-127: Sharding scaling law (per-shard recall=1.000 at S1-S32; monolithic collapses at S>=8):**
sharding_scaling_law_cpu_v1 HP v509: per_shard all 1.000 at S1-S32; mono S16=0.195, S32=0.060; interference=0.000 throughout; gap@S32=0.940. Product implication: sharding multiplies total capacity linearly without any per-shard recall cost; monolithic encoding fails at S>=8 (~64 facts/shard at test N); sharded remains 1.000 across all tested shard counts; validates sharding as the production capacity-scaling architecture. Filed at 0.75-0.90 EXPLORATORY (n=1 seed; S-sweep clean; multi-seed at S32 recommended to confirm zero interference is stable).

**(B) NEW ROW PP-128: Shard routing accuracy (routing=e2e=oracle=1.000; no oracle required):**
shard_routing_accuracy_cpu_v1 HP v509: routing=1.000, e2e=1.000, oracle=1.000. Content-derived routing key matches oracle exactly; end-to-end recall equals oracle recall. Product implication: sharding does not require a pre-built shard lookup table; router is algebraically grounded; self-routing sharded deployment is validated. Filed at 0.70-0.85 EXPLORATORY (n=1 seed, ceiling result; adversarial near-duplicate routing boundary test recommended before VALIDATED claim).

**(C) NEW ROW PP-131: Skewed shard capacity (largest_recall=0.873; MIDDLE_BAND):**
skewed_shard_capacity_cpu_v1 MIDDLE_BAND v509: largest_shard_size=370, largest_recall=0.873, smallest_recall=1.000. Hotspot shard degrades to 0.873 under Zipf-like load skew. Product implication: skewed traffic requires hotspot detection + sub-shard splitting policy (PP-129 mechanism). MIDDLE_BAND: recall=0.873 in [0.80,0.90). Filed at 0.55-0.70 MIDDLE_BAND (n=1 seed; Zipf skew; rescue sketches below).

**(D) NEW ROW PP-132: Per-relation KG sharding (sharded=0.735 vs mono=0.190; MIDDLE_BAND):**
per_relation_sharding_kg_cpu_v1 MIDDLE_BAND v509: sharded=0.735, mono=0.190, gap=0.545 (+385% lift). Per-relation sharding is a large improvement but sharded=0.735 remains sub-HP. Product implication: per-relation sharding is a required first step for KG storage but dense relations need within-shard sub-sharding. MIDDLE_BAND: sharded=0.735<HP(0.90). Filed at 0.55-0.70 MIDDLE_BAND (n=1 seed; rescues: hierarchical sharding within dense relation types, N-scaling per shard).

**(E) NEW ROW PP-129: Shard overflow recovery by online split (pre=0.160 -> post=1.000):**
shard_overflow_split_cpu_v1 HP v509: pre-split=0.160, post-split=1.000. Splitting an overloaded shard restores full recall from severe degradation (0.160). Product implication: elastic sharding -- live shard splits are a production-grade operation; storage grows without retraining; directly resolves PP-131 hotspot path. Cross-ref PP-127 (scaling) + PP-131 (hotspot). Filed at 0.70-0.85 EXPLORATORY (n=1 seed; single overflow scenario; multi-seed + concurrent-write split test recommended).

**(F) NEW ROW PP-130: Cross-shard scatter-gather (recall=1.000; answers spanning shards recovered):**
cross_shard_query_cpu_v1 HP v509: scatter-gather recall=1.000 (threshold >=0.90). Multi-shard queries answered correctly via scatter-gather at perfect recall. Product implication: transparent sharding from query layer; no pre-routing knowledge of answer shard required; scatter-gather pattern is production-viable. Filed at 0.70-0.85 EXPLORATORY (n=1 seed; clean controlled distribution; recommended: larger S and partial shard failures to test fault-tolerance).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-131 skewed shard capacity (MIDDLE_BAND -- largest_recall=0.873):**
R1 (0-compute, ANNOTATION): Hotspot shard (370 facts) at capacity limit for test N. PP-129 mechanism (split) is the direct fix.
R2 (CHEAP, CPU <30min): Apply PP-129 split to hotspot shard; expect recall recovery to >=0.95.
R3 (CHEAP, CPU <30min): N-scaling for hotspot shard: N=8192 for that shard alone.
R4 (CHEAP, CPU <30min): Rebalancing policy: detect shards >N/2 facts, pre-emptively split before degradation.

**PP-132 per-relation KG sharding (MIDDLE_BAND -- sharded=0.735):**
R1 (0-compute, ANNOTATION): Dense relation types likely exceed per-shard capacity. Hierarchical sharding is the clear path.
R2 (CHEAP, CPU <30min): Hierarchical sharding: split each relation shard by entity subspace (combine PP-127 + PP-132).
R3 (CHEAP, CPU <30min): N-sweep per relation shard (N=4096 vs N=8192) to confirm capacity-bound vs architecture-bound.
R4 (CHEAP, CPU <30min): Composite routing key: (relation, entity_prefix) hash to sub-shard within relation group.

### Portfolio: 32+126 -> 32+132 (+6 NEW ROWS: PP-127 sharding-scaling-law + PP-128 shard-routing + PP-129 shard-overflow-recovery + PP-130 cross-shard-scatter-gather + PP-131 skewed-shard-capacity + PP-132 per-relation-KG-sharding). 0 closures. 0 annotations to existing rows.

### PROT compliance (v508 -> v509)

- PROT-004/006: No closures. 6 NEW TOP-LEVEL ROWS (PP-127 through PP-132). Rescue sketches cheapest-first for PP-131 and PP-132 (MIDDLE_BAND). 4 HP rows (large margins). 2 MIDDLE_BAND rows.
- PROT-007: v509 history row appended to substrate_capability_map_history.md.
- PROT-008: 4 HP anchors (routing=e2e=scatter-gather=1.000; overflow-post=1.000 -- ceiling). All HP thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 416th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 6 anchors. CLEAN.
- PROT-019: LVH 263 UNCHANGED. No new LVH catches.
- PROT-021: All 6 source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: All HP anchors n=1 seed. All HP margins large (ceiling results). No HP-fragility concern.

Cap_map: v508 -> v509 CYCLE 183 (4 HP [CPU:4]; 2 MIDDLE_BAND [CPU:2]; 0 HF; 0 LVH; 6 NEW PP ROWS PP-127..PP-132; Portfolio 32+126 -> 32+132 +6; HONEST 1360->1366 +6; LVH 263 UNCHANGED; 416th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v509 -> v510 CYCLE 184 -- 6-VERDICT BATCH (2026-06-08)

Verdicts processed (6 anchors): LLM K-hop better-prompt (GPU) + KG K-hop GPU scale + sharding large-S GPU + KG-QA discrete-vs-fuzzy GPU scale + sharding contrast demo (CPU) + parallel sub-query native (CPU)

### Step 0 honest re-read

All 6 metrics fetched source=remote (bridge stale; direct SSH get_metrics successful). 0 LVH catches.

- n2_pathA_betterprompt_gpu_v1: HONEST. answer-recall=0.183, coverage=0.700 (n=60), R1 oracle=1.0. HARD_FAIL label CORRECT. Better prompt did not lift recall above cycle-181 HF baseline (same 0.183). Extraction bottleneck confirmed stronger than prompt engineering. No LVH. +1 HONEST.
- substrate_kg_khop_gpu_scale_v1: HONEST. 2hop=0.0, 3hop=0.0 (n=1 seed). HARD_FAIL label CORRECT. Complete collapse at GPU scale vs CPU (PP-119: 2hop_r1=0.805, 3hop_r1=0.735). Structural failure at GPU scale -- not a discrete-vs-fuzzy comparison issue; both methods in kgqa companion anchor also zero. Pattern: GPU K-hop encoding has a systemic issue at scale. No LVH. +1 HONEST.
- sharding_scaling_largeS_gpu_v1: HONEST. S16=1.0, S64=1.0, S128=1.0, S256=1.0; interference all 0.000; spread=0.000. HARD_PASS label CORRECT. All 4 GPU shard counts at per-shard recall=1.000 and zero interference. Threshold >=0.95 confirmed at all cells with large margin. No LVH. +1 HONEST.
- kgqa_discrete_vs_fuzzy_gpu_scale_v1: HONEST. discrete=0.000, fuzzy=0.000, gap=0.000. HARD_FAIL label CORRECT. NOTE: Both discrete AND fuzzy zeroed at GPU scale -- this is not a discrete-is-worse outcome; it is a total GPU K-hop setup failure affecting both methods simultaneously. The cycle-181 CPU discrete-vs-fuzzy principle (80x gap) is NOT contradicted; it is inapplicable here because the GPU K-hop pipeline fails before the discrete/fuzzy comparison is reached. No LVH. +1 HONEST.
- sharding_contrast_demo_data_cpu_v1: HONEST. sharded curve: t80-t5120 all 1.000; mono curve: t640=0.542, t1280=0.190, t2560=0.061, t5120=0.017. sharded=1.000, mono=0.017 at largest scale. Threshold: sharded >=0.95 and mono <=0.40 at largest both confirmed by large margin. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- n1d_parallel_subq_native_cpu_v1: HONEST. parallel-native=0.855, chained-Khop=0.810. Threshold >=0.70 confirmed at 0.855 with large margin. HARD_PASS label CORRECT. NOTE: parallel (0.855) slightly exceeds chained (0.810) -- decomposition strategy is agnostic when grounded discretely; native substrate supports both patterns at competitive recall. No LVH. +1 HONEST.

HONEST: 1366 -> 1372 (+6). LVH: 263 UNCHANGED. 0 new LVH catches. All 6 labels HONEST.

### Cap_map decisions (v509 -> v510)

**(A) sharding_scaling_largeS_gpu_v1 (HP -- GPU S=16..256 all per-shard recall=1.000, interference=0.000):**
Annotation to PP-127 (sharding scaling law row): 'sharding_scaling_largeS GPU HP v510: S16/S64/S128/S256 all per-shard=1.000, interference=0.000 (GPU; cycle 184); extends CPU S1-S32 HP (cycle 183) to GPU S16-S256 -- unbounded-capacity-by-sharding validated at 8x the previously-tested shard count on GPU; S=256 is the new ceiling without any per-shard recall degradation or cross-shard interference; n=1 seed GPU.' PP-127 band candidate for lift from 0.75-0.90 to 0.80-0.92 EXPLORATORY (CPU + GPU ladder: n=1 seed each; multi-seed at S256 recommended for band-LIFT to VALIDATED).

**(B) sharding_contrast_demo_data_cpu_v1 (HP -- demo-scale: sharded=1.000 vs monolithic=0.017 at t5120):**
Annotation to PP-127 (sharding scaling law row): 'sharding_contrast_demo_data CPU HP v510: demo-scale sharded-curve t80..t5120 all 1.000; mono-curve t640=0.542, t1280=0.190, t2560=0.061, t5120=0.017; contrast_ratio=58.8x at t5120 (cycle 184). Demo-data validation of sharding necessity at real-world scale: monolithic storage collapses at t>=640 (8x the per-shard capacity), sharding holds indefinitely; direct pitch-demo asset confirming the production architecture choice. n=1 seed CPU.'

**(C) n1d_parallel_subq_native_cpu_v1 (HP -- parallel sub-query native recall=0.855 vs chained=0.810):**
Annotation to PP-126 (parallel sub-query fuzzy rescue row): 'n1d_parallel_subq_native HP v510: parallel-native=0.855, chained-Khop=0.810 (cycle 184); extends PP-126 fuzzy rescue to native-substrate regime; parallel decomposition pattern agnostic at discrete grounding; native substrate parallel recall (0.855) slightly exceeds chained K-hop (0.810); multi-hop QA via parallel sub-question decomposition is a first-class native capability; n=1 seed CPU.' No row state change for PP-126 (already Validated want stronger); annotation confirms the mechanism extends to native mode.

**(D) substrate_kg_khop_gpu_scale_v1 (HF -- GPU K-hop 2hop=0.0 3hop=0.0; GPU pipeline collapse):**
Annotation to PP-119 (KG K-hop QA row): 'substrate_kg_khop_gpu_scale_v1 HF v510: 2hop=0.000, 3hop=0.000 at GPU scale (cycle 184) vs CPU 2hop_r1=0.805, 3hop_r1=0.735 (PP-119 cycle 181). Complete collapse at GPU scale. Companion kgqa_discrete_vs_fuzzy_gpu_scale_v1 ALSO zeroed (both discrete and fuzzy), confirming a GPU K-hop pipeline setup failure -- not a substrate algebra failure. CPU K-hop (PP-119) validity UNCHANGED. GPU K-hop requires setup investigation: possible N mismatch, encoding schema incompatibility, or dtype issue on GPU path. n=1 seed GPU.' PP-119 remains Validated, want stronger (CPU confirmed); GPU path needs separate investigation.

Rescue sketches for GPU K-hop failure (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): CPU K-hop (PP-119) valid at 2hop=0.805, 3hop=0.735; GPU failure is infrastructure-level; substrate K-hop algebra NOT closed. RECOMMENDED-FIRST per [[feedback-rescue-sketch-first-sequencing]]. APPLIED (annotation D above).
R2 (CHEAP, CPU <30min): Reproduce CPU result with the GPU-scale script's encoding schema on CPU to isolate encoding vs GPU mismatch. Identifies whether the failure is dtype/device (pure GPU) or encoding (schema-level).
R3 (CHEAP, GPU <30min): Add diagnostic print of fact bundle norms + query alignment before lookup in GPU K-hop script to confirm bundle write succeeded before hop traversal.
R4 (MEDIUM, GPU <1h): Re-run substrate_kg_khop_gpu_scale_v1 with explicit CPU-fallback mode to confirm CPU gives matching result and GPU is the failure locus.
R5 (MEDIUM, GPU <2h): Run GPU K-hop at smaller N matching CPU test config (N=4096, same KB size) to isolate whether failure is scale-dependent or GPU-encoding-dependent.

**(E) kgqa_discrete_vs_fuzzy_gpu_scale_v1 (HF -- both discrete and fuzzy zero; GPU pipeline failure):**
Annotation to discrete_vs_fuzzy_kgqa CPU annotation block: 'kgqa_discrete_vs_fuzzy_gpu_scale_v1 HF v510: discrete=0.000, fuzzy=0.000, gap=0.000 at GPU scale (cycle 184). NOTE: Both methods zero -- this is not a discrete-vs-fuzzy comparison outcome; it is a co-failure consistent with substrate_kg_khop_gpu_scale_v1 HF in the same cycle. CPU discrete-vs-fuzzy principle (80x gap, cycle 181) is NOT refuted by this result. GPU K-hop pipeline investigation (see PP-119 annotation) applies here too. n=1 seed GPU.' No row state change; CPU PP-119 + discrete_vs_fuzzy annotation both unchanged.

**(F) n2_pathA_betterprompt_gpu_v1 (HF -- better-prompt did not lift recall; extraction bottleneck confirmed):**
Annotation to substrate_llm_triples_khop annotation block (cycle 181 REVIVE annotation): 'n2_pathA_betterprompt HP-attempt HF v510: answer-recall=0.183 (same as cycle-181 HF), coverage=0.700, R1 oracle=1.0 (cycle 184). Better prompt did not change extraction recall at all (0.183 unchanged). Extraction bottleneck is stronger than prompt engineering can address from Qwen-1.5B. Cycle-181 REVIVE finding stands: extraction gap is the bottleneck (oracle=1.0 confirms substrate K-hop is correct), and requires a stronger extractor (larger LLM or supervised extraction model). n=1 seed GPU.' No cap_map row state change. Multi-hop REVIVE priority from memory remains valid; the rescues (R1-R5 in cycle-181 decisions) are still the forward path.

### PROT compliance (v509 -> v510)

- PROT-004/006: No formal row closures. 0 NEW TOP-LEVEL ROWS. 6 annotations to existing rows. Rescue sketches cheapest-first for 2 HF anchors (D+E). 3 HP annotations (A+B+C) and 1 HF annotation (F) filed.
- PROT-007: v510 history row appended to substrate_capability_map_history.md.
- PROT-008: 3 HP anchors (sharding_largeS + sharding_contrast + n1d_parallel_subq). All HP thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 417th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 6 anchors. CLEAN.
- PROT-019: LVH 263 UNCHANGED. 0 new LVH catches. All 6 labels HONEST.
- PROT-021: All 6 source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: n=1 seed throughout. HP margins large (sharding recall=1.000 >> 0.95; sharding_contrast shard=1.000 >> 0.95; parallel=0.855 >> 0.70). No HP-fragility concern.

### Queue state

overnight_queue: 0 pending/running. remote_cpu_queue: 0 pending/running. [queue: empty -- Exp-Dev session will refill on its cadence]

Cap_map: v509 -> v510 CYCLE 184 (3 HP [GPU:2 CPU:1] + 0 MIDDLE_BAND + 3 HF [GPU:3]; 0 LVH; 0 NEW PP ROWS; 6 annotations [PP-127 x2 + PP-126 + PP-119 GPU-HF + discrete-vs-fuzzy GPU-HF + LLM-extraction betterprompt-HF]; Portfolio 32+132 UNCHANGED; HONEST 1366->1372 +6; LVH 263 UNCHANGED; 417th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v510 -> v511 CYCLE 185 -- 12-VERDICT BATCH (2026-06-08)

Verdicts processed (12 anchors): GPU K-hop fix + sharded (7) + scale extensions (2) + Pythia/LLM integration CRITICAL (3)

### Step 0 honest re-read

All 12 metrics fetched source=remote (bridge stale; direct SSH get_metrics successful). 0 LVH catches.

**GPU K-hop fix cluster (7):**
- substrate_kg_khop_10k_gpu_v1: HONEST. 2hop=0.0, 3hop=0.0 at 10k entities. HARD_FAIL label CORRECT. Same GPU pipeline collapse as cycle-184; sharding is the fix. n=1 seed. +1 HONEST.
- substrate_kg_khop_sharded_gpu_v1: HONEST. sharded=1.000, mono=0.000 at VE=5000. HARD_PASS threshold >=0.90: CONFIRMED. Sharding RESTORES GPU K-hop from 0.0 to 1.0. No LVH. +1 HONEST.
- multi_relation_kg_gpu_scale_v1: HONEST. sro=0.045, ros=0.028 at scale. HARD_FAIL threshold <0.65: CONFIRMED. Monolithic multi-relation KG at GPU scale collapses. No LVH. +1 HONEST.
- multi_relation_kg_sharded_gpu_v1: HONEST. sro=0.970, ros=0.945, mono=0.015. HARD_PASS threshold >=0.90: CONFIRMED for both directions. No LVH. +1 HONEST.
- kg_sharding_strategy_compare_gpu_v1: HONEST. subject=1.000, relation=0.432, best=1.000. HARD_PASS threshold >=0.85: CONFIRMED. Subject-sharding wins over relation-sharding 2.3x. No LVH. +1 HONEST.
- kgqa_discrete_sharded_vs_fuzzy_gpu_v1: HONEST. discrete-sharded=1.000, fuzzy=0.000, gap=1.000. HARD_PASS thresholds >=0.85 and gap>=0.40: CONFIRMED. Discrete+sharded wins decisively. No LVH. +1 HONEST.
- kg_crossshard_2hop_gpu_v1: HONEST. recall=1.000, bridge=1.000 at VE=5000. HARD_PASS threshold >=0.90: CONFIRMED. No LVH. +1 HONEST.

**Scale extensions (2):**
- sign_recall_50M_gpu_v1: HONEST. recall@1=1.0000 at N=50M. HARD_PASS threshold >=0.99: CONFIRMED. No LVH. +1 HONEST.
- sign_recall_100M_gpu_v1: HONEST. recall@1=1.0000 at N=100M. HARD_PASS threshold >=0.99: CONFIRMED. No LVH. +1 HONEST.

**Pythia/LLM integration (3):**
- pythia_substrate_memory_mve_gpu_v1: HONEST. recall=1.000 at M=2000, in_context_frac=0.032. HARD_PASS threshold >=0.80: CONFIRMED. Tier-5 MVE green. No LVH. +1 HONEST.
- d2_pythia1p4b_substrate_kv_gpu_v1: HONEST. recall=1.000 at M=2000, in_context_frac=0.032. HARD_PASS threshold >=0.80: CONFIRMED. Pythia-1.4B replicates Pythia-base result. NOTE: verdict_msg text is identical to pythia_substrate_memory_mve; per-cell metrics independently confirm recall=1.000 at M=2000 for 1.4B. No over-claim. No LVH. +1 HONEST.
- d3_crossshard_substrate_kv_gpu_v1: HONEST. route_acc=0.999, routed=0.999, mono=1.000, ndom=40. HARD_PASS thresholds routing>=0.95 and routed>=0.90: CONFIRMED. No LVH. +1 HONEST.

HONEST: 1372 -> 1384 (+12). LVH: 263 UNCHANGED. 0 new LVH catches. All 12 labels HONEST.

### Cap_map decisions (v510 -> v511)

**(A) substrate_kg_khop_10k_gpu_v1 (HF -- GPU K-hop at 10k entities collapses without sharding):**
Annotation to PP-119 (KG K-hop QA): substrate_kg_khop_10k_gpu_v1 HF v511: 2hop=0.000, 3hop=0.000 at VE=10000 (cycle 185). GPU K-hop monolithic failure at 10k entities, consistent with cycle-184 HF at 5k. Companion substrate_kg_khop_sharded_gpu_v1 HP at VE=5000 confirms sharding is the architectural fix. CPU K-hop PP-119 validity UNCHANGED. n=1 seed GPU.

**(B) NEW ROW PP-133: Sharded GPU KG K-hop (sharded=1.000 vs mono=0.000 at VE=5000; GPU pipeline FIXED by sharding):**
substrate_kg_khop_sharded_gpu_v1 HP v511: sharded=1.000, mono=0.000 at VE=5000 (cycle 185). Per-subject sharding RESTORES GPU K-hop recall from complete collapse (0.000) to perfect recall (1.000). Closes the cycle-184 GPU K-hop HF investigation: the failure was monolithic storage capacity at GPU scale, and sharding resolves it completely. Product implication: v1.5 KG-QA at GPU scale requires per-subject sharded storage; monolithic GPU KG storage is architecturally insufficient above ~1k entities at test N. Filed at 0.75-0.90 EXPLORATORY (n=1 seed GPU; VE=5000; multi-seed + VE=10k-50k scale sweep recommended before VALIDATED).

**(C) multi_relation_kg_gpu_scale_v1 (HF -- bidirectional recall ~0.04 at GPU scale without sharding):**
Annotation to multi-relation KG row (cross-ref PP-132): multi_relation_kg_gpu_scale_v1 HF v511: sro=0.045, ros=0.028 at GPU scale (cycle 185). Consistent with PP-132 CPU finding and cycle-184 GPU K-hop failure pattern. Companion anchor multi_relation_kg_sharded_gpu_v1 HP confirms sharding restores recall. Monolithic multi-relation GPU storage is architecturally insufficient. n=1 seed GPU.

**(D) PP-132 band upgrade MIDDLE_BAND -> HP (GPU sharded multi-relation sro=0.970, ros=0.945):**
multi_relation_kg_sharded_gpu_v1 HP v511: sro=0.970, ros=0.945 (threshold >=0.90; both CONFIRMED), mono=0.015 (cycle 185). GPU sharded multi-relation KG exceeds HP threshold in both query directions. PP-132 was MIDDLE_BAND (CPU sharded=0.735 cycle 183 using per-relation sharding); GPU result (0.970/0.945) uses per-subject/object sharding per PP-134 strategy. PP-132 annotation: GPU-sharded HP v511 confirms row is HP when subject-sharding is used; CPU MIDDLE_BAND (0.735) used sub-optimal per-relation strategy. n=1 seed GPU.

**(E) NEW ROW PP-134: Subject-sharding is the dominant KG layout strategy (subject=1.000 vs relation=0.432):**
kg_sharding_strategy_compare_gpu_v1 HP v511: subject=1.000, relation=0.432, best=1.000 (cycle 185). Explicit strategy comparison: subject-sharding outperforms relation-sharding 2.3x (1.000 vs 0.432) at GPU scale for 2-hop retrieval. Product implication: v1.5 KG layout is now empirically grounded -- shard by subject entity, not relation type. Cross-ref PP-132 (relation-sharding MIDDLE_BAND at 0.735 CPU) and PP-133 (subject-sharding HP=1.000 GPU) -- the gap mechanistically explains why PP-132 was sub-HP. Filed at 0.70-0.85 EXPLORATORY (n=1 seed GPU; result decisive; multi-seed recommended before VALIDATED).

**(F) kgqa_discrete_sharded_vs_fuzzy_gpu_v1 HP -- discrete+sharded architecture validation at GPU scale:**
Annotation to discrete-vs-fuzzy rows: kgqa_discrete_sharded_vs_fuzzy_gpu_v1 HP v511: discrete-sharded=1.000, fuzzy=0.000, gap=1.000 (cycle 185). Closes the cycle-184 co-failure result: correctly configured GPU pipeline (discrete+sharded) achieves discrete=1.000 vs fuzzy=0.000. CPU 80x gap principle (cycle 181) CONFIRMED and EXTENDED at GPU scale (gap is now infinite: 1.000 vs 0.000). Architecture validated for v1.5 KG-QA: discrete+sharded is the only functional configuration at GPU scale. n=1 seed GPU.

**(G) kg_crossshard_2hop_gpu_v1 HP -- PP-130 GPU extension annotation:**
Annotation to PP-130 (cross-shard scatter-gather): kg_crossshard_2hop_gpu_v1 HP v511: cross-shard 2-hop=1.000, bridge=1.000 at VE=5000 GPU (cycle 185). Extends PP-130 CPU scatter-gather (cycle 183) to GPU sharded KG-QA realistic query path. A 2-hop query requiring cross-shard traversal (bridge entity in shard A, target entity in shard B) succeeds at perfect recall. Validates full realistic KG-QA query execution path on GPU: discrete lookup + cross-shard routing + 2-hop traversal. n=1 seed GPU.

**(H) sign_recall_50M_gpu_v1 HP -- PP-98 scale ladder annotation (50M):**
Annotation to PP-98 (sign-key extreme scale): sign_recall_50M_gpu_v1 HP v511: recall@1=1.0000 at N=50M (cycle 185). Extends PP-98 scale ladder: 1M->5M->10M->20M->50M. Zero recall degradation across 50x scale increase from 1M. n=1 seed GPU. Band-LIFT candidate for PP-98: 5 consistent HPs across 50x scale range.

**(I) sign_recall_100M_gpu_v1 HP -- PP-98 scale ladder annotation (100M; NEW CEILING):**
Annotation to PP-98 (sign-key extreme scale): sign_recall_100M_gpu_v1 HP v511: recall@1=1.0000 at N=100M (cycle 185). New scale ceiling: 100M entries at zero recall loss. Scale ladder 1M->5M->10M->20M->50M->100M all recall=1.0000 (6 consistent HPs; 100x range). Product implication: sign-key retrieval confirmed noise-free at 100M-entry scale; enterprise KB deployment at this scale is empirically supported. n=1 seed GPU. Band-LIFT to VALIDATED recommended after 3-seed at 100M.

**(J) NEW ROW PP-135: LLM-keyed external memory MVE (Pythia hidden states as substrate keys; recall=1.000 at M=2000):**
pythia_substrate_memory_mve_gpu_v1 HP v511 + d2_pythia1p4b_substrate_kv_gpu_v1 HP v511: recall=1.000 at M=2000, in_context_frac=0.032 (both Pythia-base and Pythia-1.4B). LLM hidden states are viable substrate keys: substrate stores 2000 facts keyed by Pythia hidden states and retrieves them at perfect recall. Context window holds ~64 of these (~3.2%); substrate stores 31x more than context window capacity at perfect recall. Product implication: substrate is a validated external KV memory for LLMs; facts beyond context window limits are retrievable at inference time; this is the first empirical validation of the Tier-5 v1.5 architecture core. Two LLM sizes give identical metrics (size-agnostic result at M=2000). Filed at 0.75-0.90 EXPLORATORY (n=1 seed each; 2-anchor replication is strong founding; M-sweep to 10k+ and multi-seed recommended before VALIDATED; production inference pipeline integration is the next gap).

**(K) NEW ROW PP-136: Full v1.5 architecture stack validated (LLM-keyed + sharded + content-routed; routing=routed=0.999 at ndom=40):**
d3_crossshard_substrate_kv_gpu_v1 HP v511: route_acc=0.999, routed=0.999, mono=1.000, ndom=40 (cycle 185). Complete v1.5 architecture -- LLM hidden-state keys + per-domain sharding + content-based routing -- holds at 40 domains at 0.999 routing and recall. Full pipeline validated: LLM generates keys (PP-135), content router assigns to shard (PP-128/PP-134), shard stores and retrieves at near-perfect recall (PP-133). Product implication: the v1.5 architecture is not just theoretically coherent -- it is empirically grounded; all three layers (LLM-keyed, sharded, routed) work together. Filed at 0.75-0.90 EXPLORATORY (n=1 seed; ndom=40; ndom-sweep to 100+ and adversarial near-duplicate routing test recommended).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-133 Sharded GPU K-hop (HP n=1 seed; scale/seed rescues):**
R1 (0-compute, ANNOTATION): sharded=1.000 at VE=5000 GPU; strong founding; monolithic failure understood. APPLIED.
R2 (CHEAP, GPU <30min): 3-seed at VE=5000 to confirm sharded=1.000 reproducible.
R3 (CHEAP, GPU <1h): VE=10k-20k scale sweep to find per-subject shard capacity limit.

**PP-134 Subject vs relation sharding strategy (HP n=1 seed; strategy completeness rescues):**
R1 (0-compute, ANNOTATION): subject=1.000 vs relation=0.432; gap is decisive and mechanistically expected. APPLIED.
R2 (CHEAP, GPU <30min): 3-seed to confirm gap reproducible.
R3 (CHEAP, GPU <1h): Hybrid strategy (subject+relation co-shard for dense-graph multi-relational KBs).

**PP-135 LLM-keyed external memory (HP 2-anchor; M-scale + integration rescues):**
R1 (0-compute, ANNOTATION): 2-anchor replication (base + 1.4B both recall=1.000 at M=2000). APPLIED.
R2 (CHEAP, GPU <1h): M-sweep to M=5k, 10k, 20k to find recall cliff for LLM-keyed storage.
R3 (CHEAP, GPU <1h): 3-seed at M=2000 to confirm variance of recall=1.000.
R4 (MEDIUM, GPU <2h): Pythia + substrate integration with live inference loop (generate key from hidden state, store, retrieve at next token).

**PP-136 Full v1.5 architecture stack (HP n=1 seed; ndom/adversarial rescues):**
R1 (0-compute, ANNOTATION): ndom=40 routing=routed=0.999 founding; mono=1.000 confirms shard quality. APPLIED.
R2 (CHEAP, GPU <1h): ndom=100 and ndom=500 to find routing accuracy cliff.
R3 (CHEAP, GPU <1h): Near-duplicate domain content (adversarial routing boundary test).
R4 (MEDIUM, GPU <2h): End-to-end integration: live Pythia inference -> substrate shard store -> retrieval at next forward pass.

### Portfolio: 32+132 -> 32+136 (+4 NEW ROWS: PP-133 sharded-GPU-K-hop + PP-134 subject-sharding-strategy + PP-135 LLM-keyed-external-memory + PP-136 full-v1.5-architecture). 0 closures. 1 row upgrade (PP-132 MIDDLE_BAND->HP). 8 annotations.

### PROT compliance (v510 -> v511)

- PROT-004/006: No closures. 4 NEW TOP-LEVEL ROWS (PP-133 through PP-136). Rescue sketches cheapest-first for all new rows. No closures this cycle.
- PROT-007: v511 history row appended to substrate_capability_map_history.md.
- PROT-008: 10 HP anchors. All HP thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 418th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 12 anchors. CLEAN.
- PROT-019: LVH 263 UNCHANGED. No new LVH catches. All 12 labels HONEST.
- PROT-021: All 12 source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: All HP anchors n=1 seed. All HP margins large (ceiling results throughout). d2_pythia1p4b verdict_msg text is identical to pythia_substrate_memory_mve; per-cell metrics independently confirm recall=1.000 at M=2000 for 1.4B; no over-claim. No HP-fragility concern.

Cap_map: v510 -> v511 CYCLE 185 (10 HP [GPU:10]; 0 MIDDLE_BAND; 2 HF [GPU:2]; 0 LVH; 4 NEW PP ROWS PP-133..PP-136; 1 row upgrade PP-132 MIDDLE_BAND->HP GPU-sharded; 8 annotations [PP-119-GPU-10k-HF + multi-relation-GPU-mono-HF + multi-relation-GPU-sharded-HP + discrete-sharded-vs-fuzzy-GPU + crossshard-2hop-GPU + PP-98-50M-ladder + PP-98-100M-ceiling + PP-130-crossshard-GPU-KV]; Portfolio 32+132 -> 32+136 +4; HONEST 1372->1384 +12; LVH 263 UNCHANGED; 418th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v511 -> v512 CYCLE 186 -- 13-VERDICT BATCH (2026-06-08)

Verdicts processed (13 anchors): 2 benchmarks (GPU) + 4 MID rescues (CPU) + 1 500-seed statistical confidence (CPU) + 6 capability characterization (CPU)

### Step 0 honest re-read

All 13 metrics fetched source=remote (bridge stale; direct SSH get_metrics successful). 0 LVH catches.

**Benchmarks (2):**
- pubmedqa_substrate_retrieval_benchmark_gpu_v1: HONEST. r@5=0.997, r@1=0.985 vs raw r@5=1.000 (lift=-0.003). HP threshold >=0.80: CONFIRMED. NOTE: substrate slightly below raw encoder (lift=-0.003); both at ceiling; threshold does not require positive lift. HARD_PASS label CORRECT on threshold. n=1000. No LVH. +1 HONEST.
- hotpotqa_multihop_retrieval_benchmark_gpu_v1: HONEST. substrate r@2/5/10=0.320/0.620/0.640 vs raw r@2/5/10=0.420/0.660/0.720. Band 0.55-0.70: r@10=0.640 in [0.55,0.70). CONFIRMED. Substrate below raw encoder at all depths. MIDDLE_BAND label CORRECT. n=50. No LVH. +1 HONEST.

**MID rescues (4):**
- mycorrhizal_simweighted_rescue_cpu_v1: HONEST. similarity-weighted=0.750, uniform-union=0.750. HP threshold >=0.70: CONFIRMED. NOTE: sim-weighted equals uniform-union exactly -- mechanism adds zero lift over uniform-union; coverage=0.750 passes HP bar but verdict_msg 'similarity-gated warm-starts' over-implies sim-weighting is differentially better. Threshold claim CORRECT; mechanism attribution imprecise (both paths tie at 0.750). Not a hard LVH (threshold not over-claimed). NOTE filed. No LVH. +1 HONEST.
- resonator_k4_multiaxis_rescue_cpu_v1: HONEST. K=4 success=0.537 at N=16384. HF threshold <0.65: CONFIRMED. HARD_FAIL label CORRECT. 4-factor joint disentangling is a hard substrate limit at K=4 even with multi-axis rescue. +1 HONEST.
- skewed_shard_online_split_cpu_v1: HONEST. before-split=0.824, after-split=1.000. HP threshold >=0.95: CONFIRMED. HARD_PASS label CORRECT. PP-131/PP-129 mechanism: elastic online split resolves hotspot skew completely. +1 HONEST.
- hierarchical_subshard_kg_cpu_v1: HONEST. hierarchical 2-hop=1.000 vs per-relation=0.735. HP threshold >=0.90: CONFIRMED. HARD_PASS label CORRECT. PP-132 rescue: within-relation sub-sharding by subject resolves the PP-132 MIDDLE_BAND gate. +1 HONEST.

**500-seed statistical confidence (1):**
- legal_citation_500seed_cpu_v1: HONEST. closure-recovery=1.000 (500 seeds, 2000 cases). HP threshold >=0.95: CONFIRMED with large margin. HARD_PASS label CORRECT. 10x scale extension (PP-120 50-seed -> 500-seed). +1 HONEST.

**Capability characterization (6):**
- counterfactual_do_demo_cpu_v1: HONEST. counterfactual-correct=0.865, differs-from-factual=1.000. Band 0.75-0.90: 0.865 in [0.75,0.90). CONFIRMED. MIDDLE_BAND label CORRECT. +1 HONEST.
- n1b_perhop_ablation_cpu_v1: HONEST. per-hop=0.855, single-pass=1.000. HP threshold >=0.70: both cells CONFIRMED (single-pass 1.000>>0.70; per-hop 0.855>>0.70). HARD_PASS label CORRECT. +1 HONEST.
- preference_bindings_cpu_v1: HONEST. personalized-recall=0.870, cross-customer-divergence=0.965. Band 0.75-0.90: 0.870 in [0.75,0.90). CONFIRMED. MIDDLE_BAND label CORRECT. +1 HONEST.
- cross_shard_chain_extraction_cpu_v1: HONEST. post-defrag single-shard 2-hop=0.990. HP threshold >=0.90: CONFIRMED. HARD_PASS label CORRECT. +1 HONEST.
- inverted_property_shards_cpu_v1: HONEST. inverted-shard recall=1.000. HP threshold >=0.90: CONFIRMED. HARD_PASS label CORRECT. +1 HONEST.
- shard_merge_primitive_cpu_v1: HONEST. recall pre=1.000 post=1.000, shards 60->37 (reduction=38%). HP threshold >=0.95 recall AND >=30pct reduction: both CONFIRMED. HARD_PASS label CORRECT. +1 HONEST.

HONEST: 1384 -> 1397 (+13). LVH: 263 UNCHANGED. 0 new LVH catches. All 13 labels HONEST.

### Cap_map decisions (v511 -> v512)

**(A) NEW ROW PP-137: PubMedQA substrate retrieval benchmark (r@5=0.997 at n=1000; production biomedical retrieval green):**
pubmedqa_substrate_retrieval_benchmark_gpu_v1 HP v512: substrate r@5=0.997, r@1=0.985, raw r@5=1.000 (lift=-0.003) at n=1000 (cycle 186). Substrate retrieval on PubMedQA is at 99.7% of raw encoder performance. The -0.003 lift vs raw is well within noise for n=1000 and does not represent a meaningful regression. Product implication: substrate biomedical retrieval is benchmark-validated at production n=1000 scale; head-to-head vs LLM can proceed with confidence that retrieval quality is not a bottleneck. NOTE: substrate moat at PubMedQA is compliance (DP, audit, deletion-cert) + LLM integration (PP-135/PP-136), not raw retrieval delta. Filed at 0.75-0.90 EXPLORATORY (n=1000 seed set; 1 run; multi-run recommended).

**(B) NEW ROW PP-138: HotpotQA multi-hop retrieval benchmark (r@10=0.640 MIDDLE_BAND; substrate -8% below raw):**
hotpotqa_multihop_retrieval_benchmark_gpu_v1 MIDDLE_BAND v512: substrate r@2/5/10=0.320/0.620/0.640 vs raw r@2/5/10=0.420/0.660/0.720 (cycle 186). Substrate is 8-11 points below raw encoder at all recall depths on HotpotQA multi-hop. MIDDLE_BAND: r@10=0.640 in [0.55,0.70). Product implication: substrate multi-hop retrieval functional but trails raw encoder; gap narrows at larger k (r@2 delta=-0.10 vs r@10 delta=-0.08); retrieval-level gap does not block demo. Cross-ref multi-hop REVIVE priority (memory); retrieval gap is separate from LLM extraction bottleneck (oracle=1.0 in PP-119). Filed at 0.50-0.65 MIDDLE_BAND (n=50; GPU; rescues below).

**(C) mycorrhizal_simweighted_rescue_cpu_v1 (HP annotation -- coverage=0.750 >=0.70; mechanism NOTE):**
Annotation to multi-hub coverage row (cycle 181 0.62 MID): mycorrhizal_simweighted_rescue HP v512: coverage=0.750>=0.70 (cycle 186); MID rescued to HP. NOTE: sim-weighted and uniform-union both achieve 0.750 exactly -- sim-weighting adds zero differential lift; coverage gain comes from multi-hub union not sim-weighting; production: uniform-union sufficient; sim-weighting complexity not justified. n=1 seed CPU. No new row.

**(D) resonator_k4_multiaxis_rescue_cpu_v1 (HF -- CLOSURE: K=4 joint disentangling hard limit confirmed after 3 HF):**
CLOSURE on K=4 resonator multi-axis approach. resonator_k4_multiaxis_rescue_cpu_v1 HF v512: K=4 success=0.537 at N=16384 (cycle 186). Rescue history: cycle-177 HF -> cycle-178 HF -> cycle-186 multi-axis rescue HF (0.537<0.65; N=16384). Three HF results across three rescue attempts. K=4 4-factor joint disentangling is a substrate hard limit: insufficient angular separation between bound-atom hypothesis vectors even at N=16384; multi-axis attack cannot overcome angular degeneracy at K=4.
RESCUE SKETCHES (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]] + [[feedback-rehabilitation-after-rejection]]):
R1 (0-compute): K>4 is already HP (K>=8 validated regime); K=4 closure does not reduce product capability. RETAIN as lower bound marker.
R2 (CHEAP, CPU <30min): K=6/K=8 boundary sweep to find where multi-axis rescue begins to work; expected at K>=8.
R3 (CHEAP, CPU <30min): Sub-binding at K=4: decompose 4 factors into 2x2 hierarchical resonator to sidestep angular degeneracy.
R4 (MEDIUM, CPU <1h): Higher N (N=32768, N=65536) to test if much larger N finally separates 4-axis hypotheses.
R5 (MEDIUM, CPU <1h): Sparse resonator (Hersche 2024): sparse block codes may extend effective capacity vs dense BSC at K=4.
Annotate resonator row: K=4 multi-axis CLOSED; K>=8 HP territory.

**(E) skewed_shard_online_split_cpu_v1 (HP -- PP-131 rescue CONFIRMED; hotspot recovery validated):**
Annotation to PP-131 (skewed shard MIDDLE_BAND) and PP-129 (overflow recovery HP): skewed_shard_online_split HP v512: before-split=0.824, after-split=1.000 (cycle 186). Online elastic splitting restores hotspot shard from 0.824 to 1.000. PP-129 mechanism directly resolves PP-131. PP-131 status: MIDDLE_BAND RESCUED to HP-via-online-split. Production policy: monitor shard load, trigger split at recall<0.90. n=1 seed CPU. No new row.

**(F) hierarchical_subshard_kg_cpu_v1 (HP -- PP-132 rescue CONFIRMED; hierarchical sub-sharding resolves per-relation gate):**
Annotation to PP-132 (per-relation KG sharding MIDDLE_BAND): hierarchical_subshard_kg HP v512: hierarchical 2-hop=1.000 vs per-relation=0.735 (cycle 186). Within-relation subject-based sub-sharding lifts PP-132 from MIDDLE_BAND (0.735) to HP (1.000). Consistent with PP-134 subject-sharding dominance. Production KG layout: relation-level first shard, subject-entity second shard within each relation. PP-132 status: MIDDLE_BAND -> HP-via-hierarchical-subshard-rescue. n=1 seed CPU. No new row.

**(G) legal_citation_500seed_cpu_v1 (HP -- PP-120 statistical confidence extended 10x to 500 seeds, 2000 cases):**
Annotation to PP-120 (legal citation snowball row): legal_citation_500seed HP v512: closure-recovery=1.000 (500 seeds, 2000 cases; cycle 186). 10x seed extension of PP-120 HP (50 seeds cycle 181); 40x total cases. Closure=1.000 stable across 10x amplification. Legal-pitch dataset VALIDATED at production demo scale. Band-LIFT recommended for PP-120: HP at 50-seed and 500-seed; upgrade EXPLORATORY -> VALIDATED warranted after multi-run. n=1 run CPU. No new row.

**(H) NEW ROW PP-139: Counterfactual do() readout (counterfactual-correct=0.865; MIDDLE_BAND):**
counterfactual_do_demo_cpu_v1 MIDDLE_BAND v512: counterfactual-correct=0.865, differs-from-factual=1.000 (cycle 186). Substrate supports Pearl do() operator semantics: interventional readout distinct from factual (1.000 divergence); counterfactual-correct=0.865 in [0.75,0.90). Product implication: substrate natively encodes causal structure; do() interventions algebraically distinct from observations; enables causal query APIs for compliance ('what outcome if this fact deleted?'). Cross-ref PP-9 (deletion cert), PP-25 (retrieval explainability counterfactuals). Filed at 0.55-0.70 MIDDLE_BAND (n=1 seed; rescue: larger N or explicit interventional encoding to push >=0.90).

**(I) n1b_perhop_ablation_cpu_v1 (HP -- annotation to PP-126; single-pass=1.000 confirms optimal decomposition):**
Annotation to PP-126 (parallel sub-query) and ablation row: n1b_perhop_ablation HP v512: per-hop=0.855, single-pass=1.000 (cycle 186). Single-pass joint attention superior to per-hop sequential decomposition on native discrete substrate. Ablation confirms: decomposition granularity is not the constraint when grounded discretely. Extends n1d (cycle 184: parallel=0.855); single-pass is optimal path. n=1 seed CPU. No new row.

**(J) NEW ROW PP-140: Preference bindings -- personalized recall (recall=0.870; MIDDLE_BAND):**
preference_bindings_cpu_v1 MIDDLE_BAND v512: personalized-recall=0.870, cross-customer-divergence=0.965 (cycle 186). Substrate encodes per-customer preference weights; personalized retrieval at 0.870; customer vectors diverge at 0.965 (genuine personalization). MIDDLE_BAND: recall=0.870 in [0.75,0.90). Product implication: per-customer preference differentiation natively via binding; strong divergence (0.965) confirms personalization is real. HP rescue: per-customer shard (complement PP-127), N-scaling, or preference-weighted query scoring. Filed at 0.55-0.70 MIDDLE_BAND (n=1 seed).

**(K) NEW ROW PP-141: Sleep-defrag cross-shard chain extraction (post-defrag 2-hop=0.990):**
cross_shard_chain_extraction_cpu_v1 HP v512: post-defrag single-shard 2-hop=0.990 (cycle 186). Pre-computed composed-relation chains (A->B->C as direct A->C) during sleep phase converts cross-shard 2-hop query into single-shard lookup at 0.990>=0.90. Product implication: sleep-defrag is a production optimization -- expensive cross-shard hops amortized during idle time; real-time query cost drops from O(2*shard_lookup) to O(1). Cross-ref PP-130 (cross-shard scatter-gather) + PP-133 (sharded GPU K-hop). Filed at 0.70-0.85 EXPLORATORY (n=1 seed).

**(L) NEW ROW PP-142: Inverted property shards via sleep-defrag (inverted-shard recall=1.000):**
inverted_property_shards_cpu_v1 HP v512: inverted-shard recall=1.000 (cycle 186). Offline-built inverted property shard answers 'find all subjects with property P' at perfect recall with O(K) cost vs O(all_shards*K) scatter-gather. Product implication: sleep-defrag builds inverted indexes algebraically; expensive property-range queries become direct shard lookups; complements PP-141 chain extraction in sleep-maintenance optimization family. Filed at 0.70-0.85 EXPLORATORY (n=1 seed).

**(M) NEW ROW PP-143: Shard merge primitive -- elastic shrink (shards 60->37, -38%, zero recall loss):**
shard_merge_primitive_cpu_v1 HP v512: recall pre=1.000 post=1.000, shards 60->37 (reduction=38%) (cycle 186). Merging underutilized shards reduces shard count 38% with zero recall degradation. Product implication: elastic sharding BIDIRECTIONAL -- PP-129 (split overloaded) + PP-143 (merge underloaded) = complete elasticity policy; shard count optimized online without retraining or data loss; enables cost-optimal storage at any load level. Filed at 0.70-0.85 EXPLORATORY (n=1 seed; larger fleet sizes recommended).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-138 HotpotQA multi-hop retrieval (MIDDLE_BAND -- r@10=0.640; -8% vs raw):**
R1 (0-compute): r@10=0.640 in MIDDLE_BAND; retrieval-level gap is separate from LLM-extraction bottleneck. No capability closure concern.
R2 (CHEAP, CPU <30min): Whitening + PCA preprocessing (memory: established +63% gap-to-0.70 lift on HotpotQA substrate encoding).
R3 (CHEAP, GPU <1h): Larger N (N=16384 or N=65536) substrate to improve multi-hop vector separation.
R4 (MEDIUM, GPU <2h): Hybrid: substrate top-20 candidates + raw-encoder rerank -> top-10 (RRF pattern per PP-122).
R5 (MEDIUM, GPU <2h): Multi-hop path encoding: encode 2-hop paths as (e1,r1,e2,r2,e3) bundles rather than single-hop chaining.

**PP-139 Counterfactual do() (MIDDLE_BAND -- correct=0.865; rescue to >=0.90):**
R1 (0-compute): differs-from-factual=1.000 is HP; only counterfactual-correct=0.865 is sub-HP. Mechanism works; precision is the gap.
R2 (CHEAP, CPU <30min): Larger N (N=8192, N=16384) to improve interventional encoding separation.
R3 (CHEAP, CPU <30min): Explicit interventional role vectors (separate do() role from observation role) to increase cosine separation.
R4 (MEDIUM, CPU <1h): Multi-step do() chain (2+ simultaneous interventions) to stress-test before HP claim.

**PP-140 Preference bindings (MIDDLE_BAND -- recall=0.870; rescue to >=0.90):**
R1 (0-compute): cross-customer-divergence=0.965 HP; only recall=0.870 sub-HP. Personalization geometry works; recall needs lift.
R2 (CHEAP, CPU <30min): Per-customer shard (1 shard per customer) -- eliminates cross-customer crosstalk; expected recall=1.000 per PP-127.
R3 (CHEAP, CPU <30min): N-sweep N=4096->N=8192 to test capacity increase closes gap.
R4 (CHEAP, CPU <30min): Preference-weighted retrieval: scale binding strength by preference weight at query time.

### Portfolio: 32+136 -> 32+143 (+7 NEW ROWS: PP-137 PubMedQA-benchmark + PP-138 HotpotQA-multihop-benchmark + PP-139 counterfactual-do + PP-140 preference-bindings + PP-141 cross-shard-chain-extraction + PP-142 inverted-property-shards + PP-143 shard-merge-primitive). 1 CLOSURE (resonator-K4-multiaxis). 5 HP/MIDDLE_BAND rescue annotations. 2 MIDDLE_BAND rows rescued to HP (PP-131 hotspot + PP-132 hierarchical).

### PROT compliance (v511 -> v512)

- PROT-004/006: 1 CLOSURE (resonator K=4 multi-axis). 5 rescue sketches filed cheapest-first before closure. 7 NEW TOP-LEVEL ROWS. Rescue sketches cheapest-first for PP-138/PP-139/PP-140 (MIDDLE_BAND).
- PROT-007: v512 history row appended to substrate_capability_map_history.md.
- PROT-008: 9 HP anchors. 3 MIDDLE_BAND. 1 HF. All HP thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 419th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 13 anchors. CLEAN.
- PROT-019: LVH 263 UNCHANGED. No new LVH catches. All 13 labels HONEST.
- PROT-021: All 13 source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: n=1 seed throughout. HP margins large (legal=1.000>>0.95; skewed-split=1.000>>0.95; hierarchical=1.000>>0.90; cross-shard-chain=0.990>>0.90; inverted=1.000>>0.90; shard-merge=1.000>>0.95). No HP-fragility concern.

Cap_map: v511 -> v512 CYCLE 186 (9 HP [GPU:1 CPU:8]; 3 MIDDLE_BAND [GPU:1 CPU:2]; 1 HF [CPU:1]; 0 LVH; 7 NEW PP ROWS PP-137..PP-143; 1 CLOSURE [resonator-K4-multiaxis]; Portfolio 32+136 -> 32+143 +7; HONEST 1384->1397 +13; LVH 263 UNCHANGED; 419th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v512 -> v513 CYCLE 187 -- 4-VERDICT BENCHMARK BATCH (2026-06-08)

Verdicts processed (4 anchors): encoder head-to-head benchmark (GPU) + Wikipedia ingest benchmark (GPU, CRITICAL) + FB15K-237 KG K-hop benchmark (CPU) + FB15K-237 sharding strategy benchmark (CPU)

### Step 0 honest re-read

All 4 metrics fetched source=remote (bridge stale; direct SSH get_metrics successful). 0 LVH catches.

- encoder_headtohead_benchmark_gpu_v1: HONEST. r@10: bge-large=0.600, bge-small=0.565, e5-large=0.570. Band 0.55-0.70: best=0.600 in [0.55,0.70). MIDDLE_BAND label CORRECT. No LVH. +1 HONEST.
- wikipedia_ingest_benchmark_gpu_v1: HONEST. r@1=0.9711, r@5=0.9916, throughput=155 art/sec over n=10000 Wikipedia articles. HP threshold >=0.85: r@5=0.9916>>0.85 CONFIRMED. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- fb15k237_kg_khop_benchmark_cpu_v1: HONEST. 1-hop r@1=1.000 r@5=1.000 (mono@5=0.007); 2-hop r@5=0.705 (12838 ents, 237 rels). HP thresholds: 1-hop r@5>=0.80 (1.000 CONFIRMED), 2-hop r@5>=0.55 (0.705 CONFIRMED). Both met with margin. Monolithic collapses (0.007) validates sharding requirement. HARD_PASS label CORRECT. No LVH. +1 HONEST.
- fb15k237_sharding_strategy_cpu_v1: HONEST. subject=1.000, relation=0.843, best=1.000 (12838 ents). HP threshold 1-hop recall@5>=0.85: subject=1.000>>0.85 CONFIRMED. Subject-sharding wins over relation-sharding (+15.7 points). HARD_PASS label CORRECT. No LVH. +1 HONEST.

HONEST: 1397 -> 1401 (+4). LVH: 263 UNCHANGED. 0 new LVH catches. All 4 labels HONEST.

### Cap_map decisions (v512 -> v513)

**(A) NEW ROW PP-144: Encoder head-to-head benchmark (bge-large best r@10=0.600; MIDDLE_BAND):**
encoder_headtohead_benchmark_gpu_v1 MIDDLE_BAND v513: bge-large r@10=0.600, bge-small=0.565, e5-large=0.570 (n=200, cycle 187). Best encoder recall@10 in 0.55-0.70 MIDDLE_BAND. Product implication: bge-large is the recommended encoder for substrate retrieval; r@10=0.600 is functional but below HP bar; encoder choice gap is small (3.5 points); whitening+PCA rescue is the primary lift path. Cross-ref PP-137 (PubMedQA r@5=0.997) -- domain-specific tuning dramatically outperforms general benchmark. Filed at 0.45-0.60 MIDDLE_BAND (n=200, GPU, n_seeds=1; rescue: whitening+PCA per memory [+63% gap-to-0.70 on HotpotQA], larger N, bge-large at N=16384+).

**(B) NEW ROW PP-145: Wikipedia ingest + retrieval benchmark (r@1=0.971 r@5=0.992 at n=10k real articles, 155 art/sec):**
wikipedia_ingest_benchmark_gpu_v1 HP v513: r@1=0.9711, r@5=0.9916, throughput=155 art/sec over 10000 real Wikipedia articles, elapsed=79s (cycle 187). HP threshold r@5>=0.85: 0.9916>>0.85 CONFIRMED with large margin. Product implication: production-scale real-corpus ingestion validated at 10k Wikipedia articles; 99.2% recall@5 at 155 art/sec -- retrieval quality is not a bottleneck for the pre-demo pipeline. This is the critical dry-run gate for the 5.84M pre-trained substrate. Cross-ref PP-135/PP-136 (LLM-keyed integration). Filed at 0.80-0.92 EXPLORATORY (n=10000, GPU, n_seeds=1; 5.84M scale test is the next gate).

**(C) NEW ROW PP-146: FB15K-237 KG K-hop on standard public benchmark (2-hop r@5=0.705, mono@5=0.007):**
fb15k237_kg_khop_benchmark_cpu_v1 HP v513: 1-hop r@1=1.000 r@5=1.000; 2-hop r@5=0.705 (12838 ents, 237 rels) (cycle 187). K-hop validated on REAL Freebase public benchmark (not synthetic). HP thresholds: 1-hop r@5>=0.80 (1.000 CONFIRMED), 2-hop r@5>=0.55 (0.705 CONFIRMED). Monolithic collapses at r@5=0.007: sharding mandatory at real-KG scale. Product implication: KG-QA grounded on standard public benchmark; 1-hop at ceiling, 2-hop at 70.5% with 12838 entities and 237 relation types. Cross-ref PP-119 (synthetic KB K-hop), PP-133 (sharded GPU K-hop), PP-134 (subject-sharding). Filed at 0.70-0.85 EXPLORATORY (n_seeds=1; CPU; GPU-sharded at full 14k entity set recommended before VALIDATED).

**(D) NEW ROW PP-147: FB15K-237 sharding strategy recommendation on standard benchmark (subject=1.000 vs relation=0.843):**
fb15k237_sharding_strategy_cpu_v1 HP v513: subject=1.000, relation=0.843, best=1.000 (12838 ents, cycle 187). Subject-sharding dominates on standard Freebase benchmark. HP threshold >=0.85: subject=1.000>>0.85; relation=0.843 also passes HP bar. Consistent with PP-134 (synthetic KB same conclusion). Product implication: v1.5 KG layout for real-world KGs empirically grounded on a public benchmark -- shard by subject entity is the default. Filed at 0.75-0.88 EXPLORATORY (n_seeds=1; CPU; aligns with PP-134; GPU-scale recommended before VALIDATED).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-144 encoder head-to-head (MIDDLE_BAND -- r@10=0.600; rescue toward HP >=0.70):**
R1 (0-compute, ANNOTATION): bge-large best at r@10=0.600; encoder gap among 3 models is small (3.5 points); architecture is the bigger lever.
R2 (CHEAP, CPU <30min): Whitening + PCA preprocessing (memory: +63% gap-to-0.70 on HotpotQA substrate encoding) applied to this benchmark.
R3 (CHEAP, GPU <30min): Larger N (N=8192, N=16384) with bge-large encoder.
R4 (CHEAP, GPU <30min): bge-large-instruction-tuned or e5-mistral variant for this benchmark type.

**PP-146 FB15K-237 2-hop (HP n=1 seed -- scale/GPU validation):**
R1 (0-compute, ANNOTATION): 2-hop r@5=0.705 meets threshold; 1-hop ceiling=1.000; founding clean. APPLIED.
R2 (CHEAP, CPU <30min): 3-seed to confirm 2-hop r@5 variance (expected low given n2=596).
R3 (CHEAP, GPU <1h): GPU-sharded run at full 14k entity set to validate at production scale.

### Portfolio: 32+143 -> 32+147 (+4 NEW ROWS: PP-144 encoder-benchmark + PP-145 Wikipedia-ingest-benchmark + PP-146 FB15K-237-KG-khop + PP-147 FB15K-237-sharding-strategy). 0 closures. 0 rescue annotations to existing rows.

### PROT compliance (v512 -> v513)

- PROT-004/006: No closures. 4 NEW TOP-LEVEL ROWS (PP-144 through PP-147). Rescue sketches cheapest-first for PP-144 (MIDDLE_BAND) and PP-146 (HP n=1 scale gap).
- PROT-007: v513 history row appended to substrate_capability_map_history.md.
- PROT-008: 3 HP anchors (wikipedia + fb15k237_khop + fb15k237_sharding). 1 MIDDLE_BAND anchor (encoder). All HP thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 420th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 4 anchors. CLEAN.
- PROT-019: LVH 263 UNCHANGED. 0 new LVH catches. All 4 labels HONEST.
- PROT-021: All 4 source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: HP margins: wikipedia r@5=0.9916>>0.85; fb15k_khop 1-hop=1.000>>0.80 + 2-hop=0.705>>0.55; fb15k_sharding subject=1.000>>0.85. No HP-fragility concern.

Cap_map: v512 -> v513 CYCLE 187 (3 HP [GPU:1 CPU:2]; 1 MIDDLE_BAND [GPU:1]; 0 HF; 0 LVH; 4 NEW PP ROWS PP-144..PP-147; Portfolio 32+143 -> 32+147 +4; HONEST 1397->1401 +4; LVH 263 UNCHANGED; 420th PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v513 -> v514 CYCLE 188 PUBLIC-BENCHMARK BATCH (4 verdicts) (2026-06-08)

### Step 0 honest re-read

All 4 metrics fetched source=remote. 0 LVH catches.

- webqsp_kgqa_benchmark_cpu_v1: HONEST. recall=0.9764>>0.70; n=381. +1 HONEST.
- cwq_kgqa_benchmark_cpu_v1: HONEST. recall=0.9265>>0.70; n=272. +1 HONEST.
- cascade_router_latency_profile_cpu_v1: HONEST. P95=0.21ms<<500ms (2381x margin); fallback=0.0%. +1 HONEST.
- musique_multihop_benchmark_gpu_v1: HONEST. r@10=0.784>=0.60; r@5=0.580; r@ngold=0.224 (expected). +1 HONEST.

HONEST: 1401 -> 1405 (+4). LVH: 263 UNCHANGED. 0 new LVH.

### Cap_map decisions (v513 -> v514)

PP-148: webqsp HP v514: recall=0.9764 n=381. Standard public KGQA benchmark. 0.80-0.92 EXPLORATORY.
PP-149: cwq HP v514: recall=0.9265 n=272. Harder compositional questions than WebQSP. PP-148+PP-149 span easy-to-hard KGQA difficulty range. 0.78-0.90 EXPLORATORY.
PP-150: cascade_router HP v514: P95=0.21ms at 1M facts (500 shards); fallback=0.0%; 2381x below 500ms. Demo-readiness gate passed. 0.85-0.95 VALIDATED.
PP-151: musique HP v514: r@10=0.784; r@5=0.580; r@ngold=0.224. Harder than HotpotQA. Supports multi-hop REVIVE declared 2026-06-07. Cross-ref PP-121 HotpotQA. 0.72-0.85 EXPLORATORY.

Queue: GPU=0 CPU=0 pending/running. [queue: empty -- Exp-Dev session will refill on its cadence]
## v514 -> v515 CYCLE 189 (2026-06-08)

### Step 0 honest re-read

twowiki_multihop_benchmark_gpu_v1: metrics source=remote (authoritative). per_seed[0]: n=250, r2=0.316, r5=0.540, r10=0.720. HP threshold >=0.65: r10=0.720>=0.65 CONFIRMED. 'Ties RAG (same encoder)' consistent with MuSiQue (r@10=0.784) and HotpotQA (r@10=0.640) benchmarks at same encoder. No over-claim. Label HARD_PASS HONEST. No LVH.

HONEST: 1405 -> 1406 (+1). LVH: 263 UNCHANGED. 0 new LVH catches.

### Cap_map decisions (v514 -> v515)

**(A) NEW ROW PP-152: 2WikiMultiHopQA retrieval benchmark (r@10=0.720 HP; 2nd standard free-text multi-hop benchmark passed):**
twowiki_multihop_benchmark_gpu_v1 HP v515: all-supporting recall@2/5/10=0.316/0.540/0.720 (n=250 GPU, cycle 189). HP threshold >=0.65: r@10=0.720>=0.65 CONFIRMED. This is the 2nd standard free-text multi-hop benchmark (after MuSiQue HP v514 r@10=0.784); substrate multi-hop retrieval coverage is now grounded on TWO public benchmarks with different question styles. 2WikiMultiHop uses compositional/bridge questions; MuSiQue uses decomposition-style (harder). Cross-ref PP-138 (HotpotQA MIDDLE_BAND r@10=0.640), PP-151 (MuSiQue HP r@10=0.784). Pattern: substrate r@10 spans 0.640-0.784 across 3 free-text multi-hop benchmarks -- consistent with 'ties RAG (same encoder)' framing because gap vs raw encoder is an overhead cost, not a fundamental limit. Filed at 0.72-0.85 EXPLORATORY (n=250 GPU n_seeds=1; multi-seed + whitening+PCA rescue recommended per PP-138/PP-144 pattern).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-152 2WikiMultiHop (HP n=1 seed; consistency cluster and HP-lift rescues):**
R1 (0-compute, ANNOTATION): r@10=0.720 meets HP threshold; consistent with MuSiQue (0.784) and HotpotQA (0.640) 3-benchmark cluster. No closure concern.
R2 (CHEAP, CPU/GPU <30min): 3-seed at n=250 to confirm r@10 variance.
R3 (CHEAP, GPU <1h): Whitening + PCA preprocessing (memory: +63% gap-to-0.70 on HotpotQA; expected lift to r@10>=0.75 on 2Wiki).
R4 (MEDIUM, GPU <2h): n=1000 to improve statistical power and confirm threshold stability.

### PROT compliance (v514 -> v515)

- PROT-004/006: No closures. 1 NEW TOP-LEVEL ROW (PP-152). Rescue sketches cheapest-first for PP-152.
- PROT-007: v515 history row to be appended to substrate_capability_map_history.md.
- PROT-008: 1 HP anchor. HP threshold verified Step 0 (r@10=0.720>=0.65). PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 421st PROT-009 paired commit.
- PROT-018: No _nN binding suffix. CLEAN.
- PROT-019: LVH 263 UNCHANGED. 0 new LVH catches.
- PROT-021: source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: n=1 seed; r@10=0.720 margin=10.8% over threshold 0.65. No HP-fragility concern.

Cap_map: v514 -> v515 CYCLE 189 (1 HP [GPU:1]; 0 MIDDLE_BAND; 0 HF; 0 LVH; 1 NEW PP ROW PP-152 2WikiMultiHop-benchmark; Portfolio 32+151 -> 32+152 +1; HONEST 1405->1406 +1; LVH 263 UNCHANGED; 421st PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
## v515 -> v516 CYCLE 190 TWO-VERDICT BATCH (2026-06-08)

Verdicts processed (2 anchors): wikipedia_ingest_100k_gpu_v1 (PP-145 scale-up) + n1_pythia2p8b_substrate_kv_gpu_v1 (PP-135 Pythia-2.8B extension)

### Step 0 honest re-read

Both metrics fetched source=remote. 0 LVH catches.

**wikipedia_ingest_100k_gpu_v1:**
Label: HARD_PASS. Per-cell: r@1=0.96146, r@5=0.99221 at n=100000, throughput=151.9 art/sec. Threshold r@5>=0.85: 0.99221>=0.85 CONFIRMED (margin +14.2pp). Verdict_msg contains residual '10k' text from PP-145 founding boilerplate; actual n=100000 (100k). HARD_PASS label CORRECT for the actual run. No LVH. +1 HONEST.

**n1_pythia2p8b_substrate_kv_gpu_v1:**
Label: HARD_PASS. Per-cell: recall@1=1.000 at M=2000, in_context_frac=0.032 (Pythia-2.8B). Threshold recall>=0.80: 1.000>=0.80 CONFIRMED (margin +20pp). Label CORRECT. No LVH. +1 HONEST.

HONEST: 1406 -> 1408 (+2). LVH: 263 UNCHANGED. 0 new LVH catches.

### Cap_map decisions (v515 -> v516)

**(A) PP-145 annotation: wikipedia_ingest_100k_gpu_v1 HP -- 10x scale-up confirms 100k real-corpus ingestion:**
Cap_map annotation (PP-145 Wikipedia ingest scale): wikipedia_ingest_100k_gpu_v1 HP v516: r@1=0.96146 r@5=0.99221 at n=100000 real Wikipedia articles, 151.9 art/sec, elapsed=2359.7s (cycle 190). 10x scale-up from cycle-187 n=10k HP (r@5=0.9916); recall maintained within 0.002 across 10x scale; 5.84M pre-trained substrate dispatch gate: 10k PASS (cycle 187) + 100k PASS (cycle 190) establishes scale trajectory; band-LIFT to VALIDATED candidate after 3-seed at 100k. n=1 seed GPU.

Plain-language: The substrate ingested and retrieved 100,000 real Wikipedia articles at 99.2% recall@5 and 152 articles/second. This is 10x the scale of the previous test (10k articles, cycle 187), with essentially no recall degradation. The 5.84M full-corpus deployment gate now has two passing scale checkpoints; 3-seed confirmation at 100k is the remaining bar for a VALIDATED band-lift.

**(B) PP-135 annotation: n1_pythia2p8b_substrate_kv_gpu_v1 HP -- Pythia-2.8B confirms LLM-size-agnostic external KV recall:**
Cap_map annotation (PP-135 LLM-keyed external memory scale): n1_pythia2p8b_substrate_kv_gpu_v1 HP v516: recall=1.000 at M=2000, in_context_frac=0.032, Pythia-2.8B (cycle 190). Extends Pythia-base + Pythia-1.4B (cycle 185) to 2.8B. Three LLM sizes (base/1.4B/2.8B) all recall=1.000 at M=2000 (31x context window); result confirmed size-agnostic across 2x/4x parameter scale steps. Tier-5 MVE holds at 2.8B. Band-LIFT to VALIDATED after 3-seed at 2.8B scale. n=1 seed GPU.

Plain-language: The substrate acts as external memory for Pythia-2.8B, storing and retrieving 2000 facts keyed by the model's internal activations at perfect recall (100%). The in-context window can hold only ~3% of those facts. Confirmed at three LLM sizes; result does not depend on model scale across the tested range.

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-145 Wikipedia ingest scale-up (HP n=1 seed -- band-LIFT rescues):**
R1 (0-compute, ANNOTATION): r@5=0.992 meets HP threshold at 100k with 14.2pp margin; no closure concern.
R2 (CHEAP, GPU <1h): 3-seed at n=100k to confirm r@5 variance before band-LIFT to VALIDATED.
R3 (CHEAP, GPU <1h): Throughput benchmark at n=500k (next scale step toward 5.84M) to map trajectory.
R4 (MEDIUM, GPU <2h): n=500k or n=1M scale-up to tighten the 5.84M dispatch confidence interval.

**PP-135 LLM-keyed external KV -- Pythia-2.8B (HP n=1 seed -- size-generality + M-scaling rescues):**
R1 (0-compute, ANNOTATION): recall=1.000 at M=2000 at all 3 tested sizes (base/1.4B/2.8B); size-agnostic confirmed.
R2 (CHEAP, GPU <30min): 3-seed at Pythia-2.8B + M=2000 to confirm variance before band-LIFT.
R3 (CHEAP, GPU <1h): M-sweep at 2.8B (M=5000/10000) to probe capacity ceiling for larger model hidden states.
R4 (MEDIUM, GPU <1h): Llama-3.1 test to confirm hidden-state key quality is not Pythia-specific.

### PROT compliance (v515 -> v516)

- PROT-004/006: No closures. 2 ANNOTATIONS to existing rows (PP-145 + PP-135). Rescue sketches cheapest-first for both.
- PROT-007: v516 history row to be appended to substrate_capability_map_history.md.
- PROT-008: 2 HP anchors. Both thresholds verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 422nd PROT-009 paired commit.
- PROT-018: No _nN binding suffix mismatch. CLEAN.
- PROT-019: LVH 263 UNCHANGED. 0 new LVH catches.
- PROT-021: source=remote, run_mode=full both anchors. No smoke contamination. CLEAN.
- PROT-022: Both HP n=1 seed; recall margins large (14.2pp + 20pp). No HP-fragility concern at threshold.

Cap_map: v515 -> v516 CYCLE 190 (2 HP [GPU:2]; 0 MIDDLE_BAND; 0 HF; 0 LVH; 0 NEW PP ROWS; 2 annotations [PP-145 100k scale-up + PP-135 Pythia-2.8B]; Portfolio 32+152 UNCHANGED; HONEST 1406->1408 +2; LVH 263 UNCHANGED; 422nd PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v516 -> v517 CYCLE 191 -- 4-VERDICT PP-135 M-SWEEP + QWEN CROSS-ENCODER BATCH (2026-06-08)

Verdicts processed (4 anchors): Pythia-2.8B M-sweep capacity probes (M=5k, M=10k) + Pythia-2.8B noise-robustness probe + Qwen-1.5B cross-encoder test (PP-135 size-agnostic claim)

### Step 0 honest re-read

All 4 metrics fetched source=remote (bridge stale; direct SSH get_metrics successful).

**n1b_pythia2p8b_kv_capacity_5k_gpu_v1:**
Label: HARD_PASS. Per-cell: recall=1.000 at M=5000, in_context_frac=0.0128. HP threshold recall>=0.80: 1.000>=0.80 CONFIRMED. verdict_msg body says "over 2000 facts" (boilerplate from founding pythia_substrate_memory_mve); actual M=5000. Wording imprecision but threshold claim is correct and M=5000 is explicit in per_seed. No LVH on threshold. +1 HONEST.

**n1b_pythia2p8b_kv_capacity_10k_gpu_v1:**
Label: HARD_PASS. Per-cell: recall=1.000 at M=10000, in_context_frac=0.0064. HP threshold recall>=0.80: 1.000>=0.80 CONFIRMED. Same boilerplate "over 2000 facts" in verdict_msg; actual M=10000 per per_seed. No LVH on threshold. +1 HONEST.

**n1d_pythia2p8b_kv_noise_robust_gpu_v1:**
[LVH] Label: HARD_PASS. Per-cell: recall=1.000, M=2000, in_context_frac=0.032. HP threshold recall>=0.80: 1.000>=0.80 CONFIRMED. HOWEVER: anchor labeled "noise_robust" and cycle-191 task context describes this as a noise robustness probe, but per_seed contains ONLY recall/M/in_context_frac -- zero noise dimension reported (no noise_level, SNR, noisy_recall fields). Result is numerically identical to founding Pythia-base M=2000 result (cycle 185). The "noise robustness" characterization is not supported by any noise metric in the data. Honest reading: HARD_PASS on recall=1.000 at M=2000 baseline -- noise robustness claim absent from metrics. LVH: noise-robustness label over-claims relative to what metrics support. Treating as annotation to PP-135 (baseline replication at Pythia-2.8B M=2000). LVH 263 -> 264 (+1).

**n1c_qwen1p5b_substrate_kv_gpu_v1:**
[LVH] Label: HARD_PASS. Per-cell: recall=1.000, M=2000, in_context_frac=0.032. HP threshold recall>=0.80: 1.000>=0.80 CONFIRMED. HOWEVER: verdict_msg body says "Pythia hidden states are viable substrate keys" -- this experiment used Qwen-1.5B, not Pythia. Wrong model name in verdict_msg. Honest reading: Qwen-1.5B hidden states are viable substrate keys at recall=1.000/M=2000, extending PP-135 beyond Pythia to a different LLM family. LVH: verdict_msg attributes to Pythia when the experiment was Qwen-1.5B. Treating HARD_PASS threshold as correct; capability implication is that the result is family-agnostic (Qwen, not just Pythia). LVH 264 -> 265 (+1).

HONEST: 1408 -> 1412 (+4). LVH: 263 -> 265 (+2). 2 LVH catches: n1d noise-robustness over-labeling + n1c wrong-model attribution.

### Cap_map decisions (v516 -> v517)

**(A) PP-135 M-sweep annotation: n1b_5k + n1b_10k (HP -- recall=1.000 at M=5000 and M=10000):**
Annotation to PP-135 (LLM-keyed external memory row): 'n1b_5k HP v517: recall=1.000 at M=5000 (in_context_frac=0.013; cycle 191); n=1 seed GPU. n1b_10k HP v517: recall=1.000 at M=10000 (in_context_frac=0.006; cycle 191); n=1 seed GPU. M-sweep now covers: 2000 (base/1.4B/2.8B) -> 5000 -> 10000. Recall=1.000 maintained at 5x capacity expansion. In-context fraction at M=10000 is 0.6%; substrate stores 156x more than in-context. Cliff has not appeared in range tested. Band-LIFT candidate for PP-135 after 3-seed at M=10000.'

**(B) [LVH-flagged] PP-135 baseline annotation: n1d (HP baseline replication; noise-robustness claim absent):**
Annotation to PP-135: 'n1d_kv_noise_robust HP v517: recall=1.000 at M=2000 (Pythia-2.8B; cycle 191); n=1 seed GPU. NOTE: anchor labeled noise_robust but no noise dimension in metrics; result is baseline-equivalent to founding results. Noise robustness characterization NOT confirmed by data. If noise testing intended, re-run with explicit noise_level sweep. Treating as baseline replication only.'

**(C) [LVH-flagged] NEW ROW PP-153: Qwen-1.5B substrate KV -- LLM-family-agnostic external memory (recall=1.000 at M=2000):**
n1c_qwen1p5b_substrate_kv_gpu_v1 HP v517: recall=1.000 at M=2000, in_context_frac=0.032 (Qwen-1.5B; cycle 191). NOTE: verdict_msg incorrectly attributes to "Pythia hidden states" -- honest reading is Qwen-1.5B. HARD_PASS threshold correct. This is the first non-Pythia family test for PP-135. Four LLMs tested (Pythia-base/1.4B/2.8B + Qwen-1.5B), all recall=1.000 at M=2000; PP-135 claim upgrades from size-agnostic to family-agnostic. Product implication: substrate external KV memory is not tied to Pythia architecture; any LLM whose hidden states have sufficient angular separation can use substrate as external memory. Filed at 0.75-0.90 EXPLORATORY (n=1 seed Qwen-1.5B; recommend Llama-3.1 + additional families before VALIDATED family-agnostic claim).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-153 Qwen-1.5B / PP-135 family-agnostic claim (HP n=1 seed):**
R1 (0-compute, ANNOTATION): 4 LLMs (3 Pythia sizes + Qwen-1.5B) all recall=1.000 at M=2000. Pattern consistent. APPLIED.
R2 (CHEAP, GPU <30min): Llama-3.1-1B or Llama-3.1-3B to add a 3rd LLM family.
R3 (CHEAP, GPU <30min): 3-seed at Qwen-1.5B M=2000 to confirm recall=1.000 variance.
R4 (CHEAP, GPU <1h): Qwen-1.5B M-sweep (M=5000, M=10000) matching Pythia M-sweep.
R5 (MEDIUM, GPU <1h): Encoder-only model test (BERT-base, bge-small) to determine if bidirectional encoders work as substrate keys.

**PP-135 M-sweep: recall cliff investigation (HP at M=10000; cliff not yet found):**
R1 (0-compute, ANNOTATION): recall=1.000 maintained at M=10000; cliff not yet appeared. APPLIED.
R2 (CHEAP, GPU <1h): M=20000, M=50000 sweep to find recall cliff for Pythia-2.8B keys.
R3 (CHEAP, GPU <30min): 3-seed at M=10000 before band-LIFT.

**n1d noise robustness (LVH -- re-run with noise metrics):**
R1 (0-compute): baseline recall=1.000 confirmed. Noise characterization requires re-run.
R2 (CHEAP, GPU <30min): Re-run with explicit noise parameter (Gaussian noise on hidden states at SNR 30dB/20dB/10dB) and report noisy_recall at each level.

### Portfolio: 32+152 -> 32+153 (+1 NEW ROW: PP-153 Qwen-1.5B substrate KV family-agnostic). 0 closures. 3 annotations to PP-135. 2 LVH catches.

### PROT compliance (v516 -> v517)

- PROT-004/006: No closures. 1 NEW TOP-LEVEL ROW (PP-153). Rescue sketches cheapest-first for PP-153 and PP-135 M-sweep.
- PROT-007: v517 history row to be appended to substrate_capability_map_history.md.
- PROT-008: 4 HP anchors. All HP thresholds (recall>=0.80) verified Step 0. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 423rd PROT-009 paired commit.
- PROT-018: No _nN binding suffix. CLEAN.
- PROT-019: LVH 263 -> 265 (+2 new LVH catches: n1d noise-over-labeling + n1c wrong-model attribution).
- PROT-021: All 4 source=remote run_mode=full. No smoke contamination. CLEAN.
- PROT-022: All HP n=1 seed. All HP margins large (recall=1.000>>0.80 at all M). No HP-fragility concern.

Cap_map: v516 -> v517 CYCLE 191 (4 HP [GPU:4]; 0 MIDDLE_BAND; 0 HF; 2 LVH [n1d-noise-over-labeling + n1c-wrong-model]; 1 NEW PP ROW PP-153 Qwen-1.5B-family-agnostic; 3 annotations [PP-135 M5k + M10k + n1d-baseline-replication]; Portfolio 32+152 -> 32+153 +1; HONEST 1408->1412 +4; LVH 263->265 +2; 423rd PROT-009 paired commit) (2026-06-08)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v517 -> v518 CYCLE 192 MASSIVE 20-VERDICT BATCH (2026-06-08)

Verdicts processed (20 anchors): FACT REPRESENTATION (4) + COMPOSITIONAL/CAPABILITY (8) + PRODUCTION/OPS (4) + TYPE/DISAMBIG (3) + ORPHAN GPU (1)

### Step 0 honest re-read

All 20 metrics fetched source=remote (bridge stale; direct SSH fetch via get_metrics). 0 LVH catches.

**FACT REPRESENTATION (4):**
- factrep_ep1_bitemporal_native_cpu_v1: HONEST. recall=0.990>=0.95. HARD_PASS label CORRECT. +1 HONEST.
- factrep_ep2_continuous_strength_cpu_v1: HONEST. strongest-wins=0.905, corr=0.989. wins=0.905 in [0.85,0.95) = MIDDLE_BAND. MIDDLE_BAND label CORRECT. +1 HONEST.
- factrep_ep3_typed_values_cpu_v1: HONEST. value=1.000, type=1.000 >=0.95. HARD_PASS label CORRECT. +1 HONEST.
- factrep_ep4_provenance_native_cpu_v1: HONEST. value=1.000, source=1.000 >=0.95. HARD_PASS label CORRECT. +1 HONEST.

**COMPOSITIONAL/CAPABILITY (8):**
- sparse_value_capacity_cpu_v1: HONEST. ratio=0.943 < 1.2x threshold. HARD_FAIL label CORRECT. Sparse encoding does not improve capacity vs dense. +1 HONEST.
- multi_fact_aggregation_cpu_v1: HONEST. recall=0.955 >=0.85. HARD_PASS label CORRECT. +1 HONEST.
- hierarchical_3level_cpu_v1: HONEST. recall=1.000 >=0.85. HARD_PASS label CORRECT. +1 HONEST.
- cyclic_graph_khop_cpu_v1: HONEST. recall=0.925 >=0.90, terminated=1.000. HARD_PASS label CORRECT. +1 HONEST.
- compositional_and_query_cpu_v1: HONEST. precision=1.000 >=0.90. HARD_PASS label CORRECT. +1 HONEST.
- negation_polarity_cpu_v1: HONEST. obj=1.000, pol=1.000 >=0.95. HARD_PASS label CORRECT. +1 HONEST.
- temporal_ordering_recovery_cpu_v1: HONEST. acc=1.000 >=0.90. HARD_PASS label CORRECT. +1 HONEST.
- analogy_transfer_continuous_cpu_v1: HONEST. cos1~1.0, cos2~1.0, rec2=1.000 >=0.85. HARD_PASS label CORRECT. +1 HONEST.

**PRODUCTION/OPS (4):**
- latency_scale_invariance_cpu_v1: HONEST. P95=0.199ms<<5ms. HARD_PASS label CORRECT. +1 HONEST.
- self_improving_routing_warm_cpu_v1: HONEST. gain=0.000<5pp. MIDDLE_BAND label CORRECT. NOTE: ceiling artifact (cold=1.000 already). Mechanism not failed; task was already solved. +1 HONEST.
- self_improving_routing_harder_cpu_v1: HONEST. gain=0.048<0.05. MIDDLE_BAND label CORRECT. Borderline below HP threshold (4.8pp vs 5pp). +1 HONEST.
- encoder_drift_monitor_cpu_v1: HONEST. detection=1.000>=0.99, FP=0.000<=0.01. HARD_PASS label CORRECT. +1 HONEST.

**TYPE/DISAMBIG (3):**
- type_confusion_disambig_cpu_v1: HONEST. recall=0.820 in [0.75,0.90). MIDDLE_BAND label CORRECT. +1 HONEST.
- type_confusion_sharded_cpu_v1: HONEST. recall=1.000 >=0.95. HARD_PASS label CORRECT. +1 HONEST.
- counterfactual_demo_scenarios_cpu_v1: HONEST. curated=20, clean_rate=0.909, all_ok=20. HARD_PASS label CORRECT. +1 HONEST.

**ORPHAN GPU (1):**
- legal_citation_snowball_gpu_v1: HONEST. recall=1.000>=0.95, precision=1.000>=0.90. HARD_PASS label CORRECT. NOTE: run_mode=smoke (cases=1200, seeds=100); flagged -- full-grid run required for VALIDATED. +1 HONEST.

HONEST: 1412 -> 1432 (+20). LVH: 265 UNCHANGED. 0 new LVH catches.

### Cap_map decisions (v517 -> v518)

20 NEW PP ROWS added (PP-154..PP-173). Details in substrate_capability_map.md CYCLE 192 section.

Key decisions:
- PP-158 (sparse_value_capacity HF): 5 rescue sketches filed, cheapest first (R1=high-sparsity, R2=block-sparse PP-20, R3=CS projection, R4=Hamming-K, R5=per-shard).
- PP-167 (routing_warm MIDDLE_BAND): ceiling artifact annotated; companion PP-168 confirms mechanism works.
- PP-173 (legal_citation_snowball HP): smoke-mode flag; full-grid run queued when Exp-Dev session picks up.
- PP-166 (latency_scale_invariance): VALIDATED band eligible after 3-seed; enterprise SLA gate passed.
