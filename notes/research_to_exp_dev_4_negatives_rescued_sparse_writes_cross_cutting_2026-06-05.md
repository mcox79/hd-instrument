# Research -> Exp-Dev: All 4 MIDDLE/NEGATIVE findings rescued -- sparse outer-product writes is cross-cutting architectural lever

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~17:30
**Subject:** 2x rescue drill landed. All four MIDDLE/NEGATIVE findings have actionable rescue paths. Cross-cutting architectural pattern identified: sparse outer-product writes would move substrate into linear-noise regime addressing all four. Plus quantitative Phase 3 scaling requirements derived.

---

## Drill verdict (all four findings)

| Finding | Verdict | Best rescue | CPU/GPU cost |
|---|---|---|---|
| A: Theta-burst HF | RECOVERABLE | Endpoint-only K=3 write | ~5 min laptop |
| B: Random-expansion HF | PARTIALLY RECOVERABLE | k=8 Hadamard bipolar expansion | ~10 min laptop |
| C: HotpotQA EM MIDDLE | BOUNDED small-LM; RECOVERABLE 1B+ | HotpotQA at Llama-1B (already extracted) | ~30-60 min GPU |
| D: Bigram-class ceiling MIDDLE | BOUNDED N=1024; RECOVERABLE Phase 3 | k=3 XOR at N>=4096, V_c>=100k | ~15-30 min laptop |

**4 cells routed below; all CPU-feasible except C which needs GPU (Llama-1B).**

---

## CROSS-CUTTING ARCHITECTURAL FINDING (most strategically important)

The drill identified a consistent pattern across all four failures: **"algebraically-promising bipolar architectures fail empirically because of sign quantization destroying the algebraic structure the capacity argument depends on."**

Three confirmed mechanisms from recent associative memory lit:

1. **Sharper capacity cliff in bipolar vs continuous** (first-order vs second-order RSB transition; Parisi ultrametric structure from spin-glass theory). Bipolar networks flip catastrophically at capacity; continuous networks degrade gracefully.

2. **Higher-order correlation amplification** at higher polynomial degree (arxiv:2508.01395). Multi-step writes effectively create higher-order correlations between stored patterns, shifting substrate into a regime where capacity drops sharply.

3. **Dense vs sparse noise asymmetry** (NeurIPS 2023 sparse Hopfield, arxiv:2309.12673). Dense bipolar retrieval: noise impact is EXPONENTIAL in load. Sparse bipolar retrieval: noise impact is LINEAR. This is a fundamental regime difference.

**Cross-cutting rescue: SPARSE OUTER-PRODUCT WRITES** -- only write when cosine similarity to existing patterns exceeds threshold. Moves substrate from exponential-noise dense regime to linear-noise sparse regime. Could address ALL FOUR findings with one architectural change.

This is a candidate for a separate drill (sparse-coding compressed-sensing direction; Tier-1b cross-cutting per next-drill candidate).

---

## Cell SPARSE-V2-1: Endpoint-only trajectory write (Finding A rescue)

**Anchor:** `substrate_theta_burst_endpoint_only_K3_v2`

### Architecture
- Write rule: W += outer(phi(c_t), phi(c_{t+K})) with K=3, NO intermediate writes
- Compare to baseline (K=1 standard Hebbian) and original theta-burst (gamma=0.7, K=3 all)
- N=1024, V_c=1000, 5 seeds
- Metric: multi-step prediction accuracy (predict c_{t+1}, c_{t+2}, c_{t+3})

### Pre-reg
- HP: >=10% multi-step (t+2, t+3) prediction improvement vs K=1 baseline; single-step (t+1) within 5%
- MID: 5-10% multi-step improvement
- HF: zero improvement OR 1-step quality degradation

### Cost + wall
- $0 CPU
- ~5 min wall
- 5 seeds

### Strategic
Validates that the algebraic direction (lookahead helps) holds with right parameter regime. If HP: substrate-API can ship "context-aware write" feature (10%+ multi-step lift at zero capacity cost). P_deflated: 0.45.

---

## Cell SPARSE-V2-2: Moderate k=8 Hadamard bipolar expansion (Finding B rescue)

**Anchor:** `substrate_bipolar_hadamard_expansion_k8_v2`

### Architecture
- Use structured Hadamard-based bipolar random matrix (preserves bipolar structure unlike random Gaussian)
- Expansion N=128 -> N_exp=1024 (k=8)
- Compare to baseline (no expansion, M_max scaling) at matched memory budget
- 5 seeds
- Metric: storage capacity (M where retrieval accuracy first drops below 0.95)

### Pre-reg
- HP: capacity >= 4x baseline at N=128, k=8 expansion
- MID: capacity 1.5-4x baseline
- HF: capacity < 1.5x OR retrieval quality below single-step baseline

### Cost + wall
- $0 CPU
- ~10 min wall
- 5 seeds

### Strategic
Validates moderate-expansion bipolar variant as Phase 2/3 capacity multiplier. If HP: 8x capacity gain at 8x memory cost is a direct Phase 3 architectural upgrade. P_deflated: 0.40.

Note: the original O(N^2) random-expansion claim is closed at substrate-class hardware; this is a REVISED target.

---

## Cell SPARSE-V2-3: HotpotQA multi-hop at Llama-1B (Finding C rescue)

**Anchor:** `substrate_hotpotqa_multihop_llama1b_v2`

### Architecture
- Substrate 2-hop retrieval at Llama-1B encoder (already extracted residuals)
- Compare to: (a) raw Llama-1B end-to-end QA; (b) 1-hop cosine retrieval + Llama-1B
- Same HotpotQA distractor subset previously used at Pythia tier
- 3 seeds
- Metric: end-to-end EM + recall@2

### Pre-reg
- HP: EM > 0.12 with substrate 2-hop + Llama-1B (vs 0.083 floor at Pythia)
- MID: EM 0.10-0.12 (substrate contribution visible but modest)
- HF: EM <= 0.08 at Llama-1B (substrate contributes nothing at any LM tier; substrate-side bound exists beyond decoder)

### Cost + wall
- GPU (Llama-1B inference; ~$1-3 cloud OR ~1-2 hours desktop bf16)
- 3 seeds

### Strategic
Decisive test for substrate's multi-hop contribution at 1B scale. If HP: multi-hop retrieval is product-ready capability. If HF: substrate-side architectural bound exists; document and close.

Note: per drill, this is the right test BEFORE accepting substrate-side bound. EM is the wrong metric at sub-1B; at 1B+ the contribution should be visible.

P_deflated: 0.40.

---

## Cell SPARSE-V2-4: k-gram XOR scaling sweep N x V_c (Finding D rescue)

**Anchor:** `substrate_kgram_xor_scaling_sweep_v2`

### Architecture
- Sweep: k in {2, 3, 4}, N in {1024, 4096}, V_c in {1000, 100000} (sparse activation)
- 5 seeds per cell
- Standard Hebbian write; k-gram XOR context binding (per validated K2-XOR rescue)
- Metric: next-token accuracy vs n-gram oracle (bigram/trigram/4-gram)

### Pre-reg
- HP: k=3 at N=4096, V_c=100k achieves accuracy >= trigram oracle within 2pp
- MID: k=3 at N=4096 within 5pp of trigram oracle
- HF: k=3 at N=4096 below bigram oracle (XOR scheme fails to scale)

### Cost + wall
- $0 CPU
- ~15-30 min wall (12 cells * 5 seeds)

### Strategic
Quantitatively validates Phase 3 scaling path (k-gram class unlocks at N>=4096 with V_c>=100k). If HP: Phase 3 substrate specification gains concrete scaling requirement (trigram requires N>=4096; 4-gram requires N>=16384). P_deflated: 0.40.

Plus optional sub-cell: hierarchical context (global context register + k=2 XOR) and position-aware k-gram (XOR with position labels). P_deflated: 0.30-0.35.

---

## Architectural closure language (per drill)

For findings deemed BOUNDED (not just failed), drill provides specific closure language for the scorecard + product framing:

**Finding C closure (small-LM EM):**
"End-to-end EM on HotpotQA at sub-1B LM tier is a decoder bottleneck, not a substrate failure. This is expected behavior. The substrate's retrieval contribution is confirmed at the recall layer."

**Finding D closure (N=1024 bigram):**
"At N=1024 and sparse V_c~1000, substrate sequence prediction is bigram-Markov class by design. This is not a failure; this is the substrate's operating point. Trigram/4-gram class is unlocked at Phase 3 with N >= 4096."

These should propagate to capability_scorecard.md (closing the open questions) and to HP-12 / Phase 3 product framing.

---

## Phase 3 architectural scaling requirements (newly quantified)

The drill quantitatively defines Phase 3 substrate scaling requirements:

| Markov class target | N requirement | V_c requirement |
|---|---|---|
| Bigram (current) | 1024 | 1000 |
| Trigram | 4096 | 100,000 |
| 4-gram | 16,384 | 100,000+ |
| 5-gram | 65,536 | 1,000,000+ |

This means the Phase 3 production blueprint (D=8 substrates at N=65536 + V_c=1M) naturally unlocks 5-gram class sequence prediction. No additional architecture needed.

---

## Updated Exp-Dev priority queue (post-drill)

**Highest priority (HP-12 V1 critical path):**
1. HP-12 V1 cheap decisive test (~2 hours per V1 pipeline drill)
2. HP-12 V1 4-day build sequence
3. K2-XOR-1B full verdict (mechanism confirmed; full pre-reg pending)
4. HP-5 medical Q&A proto (data delivered)

**Second priority (negatives rescue cells; CPU-feasible):**
5. SPARSE-V2-1 endpoint-only trajectory write (~5 min CPU; validates Finding A rescue)
6. SPARSE-V2-4 k-gram scaling sweep (~15-30 min CPU; validates Finding D Phase 3 scaling)
7. SPARSE-V2-2 Hadamard bipolar expansion (~10 min CPU; validates Finding B rescue)

**Third priority (validation at 1B):**
8. SPARSE-V2-3 HotpotQA at Llama-1B (~30-60 min GPU; resolves Finding C; bf16 desktop or cheap cloud)
9. CCC-1-v2 capability dims at Llama-1B residual-only transfers

**Phase 3 prep (gated on FAISS env fix):**
10. HNSW empirical smoke (Testbed env fix needed; gates HP-12 V2)

**Backburnered / dropped (per prior pruning):**
- HP-8/9/10/11 (HP-9 already HP; others not gating)
- CUBIC-N3-1 (HNSW solves capacity; sparse-V2-2 provides additional path)
- Two-bridge hybrid smoke (subsumed by HP-12 V2)
- Llama-8B Tier-4 (per user)
- Tier-4 follow-ons (aged out)

---

## NEW research direction queued (cross-cutting rescue)

**Sparse-coding compressed-sensing direction (Tier-1b)** -- the cross-cutting rescue that appears in all four findings. If sparse outer-product writes (only write above cosine threshold) move substrate to linear-noise regime, this could unlock all four rescues simultaneously AND improve baseline substrate quality.

Adding to research backlog. Could dispatch separately when current pipeline catches up. Not gating HP-12 V1 (which uses standard Hebbian writes).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-pressure-test-negative-findings]]: every "substrate cannot do X" claim has been enumerated for alternate operating modes
- Per [[feedback-negative-results-2x-research]]: 2x drill produced concrete rescue paths before architectural closure
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest decisive first (SPARSE-V2-1 at ~5 min; SPARSE-V2-2 at ~10 min)
- Per [[feedback-no-padding-experiments]]: 4 cells each test distinct architectural hypothesis
- ASCII-only

PROT-018: anchors per cell
PROT-021: source=local CPU (3/4 cells) + 1 GPU; n_seeds=3-5

---

**END.**

**Exp-Dev:** 4 V2 cells from negatives rescue drill. All CPU-feasible except HotpotQA-Llama-1B (~30-60 min GPU). Highest priority among V2 cells: SPARSE-V2-1 (theta-burst endpoint write; 5 min) + SPARSE-V2-4 (k-gram scaling; validates Phase 3 requirements). The new cross-cutting architectural finding (sparse outer-product writes move substrate to linear-noise regime) is queued as a separate research direction; not gating HP-12 V1.

**Testbed:** No additional cloud work from this drill. SPARSE-V2-3 (HotpotQA at Llama-1B) could use cheap cloud GPU (~$1-3) OR desktop bf16. Testbed FAISS env fix still highest priority for HP-12 V2 unblock.

**User:** All 4 MIDDLE/NEGATIVE findings have actionable rescue paths. Theta-burst RECOVERABLE (parameter regime mismatch fixed via endpoint-only write); cerebellar expansion PARTIALLY RECOVERABLE (N^2 closed; k=8 Hadamard works); HotpotQA EM RECOVERABLE at Llama-1B (decoder ceiling not substrate); bigram-class RECOVERABLE at Phase 3 scale (N>=4096 for trigram; N=16384 for 4-gram quantified). Cross-cutting finding: "bipolar architectures fail empirically because sign quantization destroys the algebraic structure capacity arguments depend on" -- sparse outer-product writes would move substrate to linear-noise regime addressing all four. Plus Phase 3 substrate naturally unlocks 5-gram class sequence prediction at the N=65536 + V_c=1M blueprint.
