# Research -> Exp-Dev: top 20 previously-unrouted experiments (comprehensive routing)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** User directive ("yes all of them") -- routing 20 experiments identified via day's drills that hadn't been formally filed.

All apply multi-dim acceptance criteria per supplement note. All decision rules autonomous
unless flagged for me. Sequenced by cost (Tier A cheapest first; Tier C heaviest last).
Apply methodology pre-test rule throughout: production setup (calibrated MarianMT harness
for ZKL, production N for substrate cells, sentence-transformer for retrieval), no proxy
substitutions without empirical equivalence check.

---

## TIER A: CPU, <=2 hours each (run in parallel as capacity allows)

### 1. PTB-REUSE-1 -- index-only filler cache for Pattern B
- Pre-test from Pattern B compression-analogs 3x drill (Mechanism 2)
- Method: store 1000 Pattern B bundles using ONLY role-binding indices (filler reference
  IDs in a shared cache); measure storage cost + retrieval F1
- HARD-PASS: per-fact cost < 50 bytes AND retrieval F1 >= 0.95 (within 5% of full-bundle
  baseline)
- HARD-FAIL: per-fact cost > 200 bytes OR retrieval F1 drop > 15%
- Wall: ~1 hour CPU

### 2. PTB-RSPCA-2 -- role-separable PCA per role
- Pre-test from compression-analogs 3x (Mechanism 1; alternative path)
- Method: compute per-role filler manifold dim via TwoNN on bge-small filler distributions;
  truncate each role's filler to its intrinsic dim; measure bundle reconstruction + retrieval F1
- HARD-PASS: per-role filler dim <= 60 AND reconstruction acc >= 0.95
- Wall: ~2 hours CPU

### 3. PTB-TTRP-3 -- tensor-train rank profiling on Pattern B bundles
- Pre-test from compression-analogs 3x (Mechanism 5; surprise-not-foreclosed)
- Method: reshape 1000 Pattern B bundle representations as 3-mode tensors (roles x
  filler-dim x bundle-id); fit tensor-train decomposition at varying ranks; measure
  retrieval F1 vs rank
- HARD-PASS: rank that gives retrieval F1 >= 0.95 produces total storage < 200 bytes/fact
- Wall: ~2 hours CPU

### 4. RAG-arm verification for ~2x relative privacy claim
- Cycle 159 customer-pitch dependency; never routed
- Method: bge-small + Llama (vanilla RAG) baseline ZKL(50) on calibrated MarianMT harness;
  compare to substrate ZKL(50) with attention-reweighting
- HARD-PASS: vanilla RAG ZKL >= 2x substrate ZKL (validates the ~2x relative claim)
- BORDER: ratio in 1.3-2.0x (qualified claim becomes "1.3-2x improvement")
- HARD-FAIL: ratio < 1.3x (relative privacy claim doesn't hold; revise customer pitch)
- Wall: ~2 hours CPU

### 5. Causal + Merkle composition cell
- Cycle 153 follow-up (PP-81/82 causal cluster)
- Method: store 100 causal facts with Merkle commitments; perform 20 counterfactual
  substitutions; verify each substitution's Merkle chain is valid AND traces to the
  original fact
- HARD-PASS: 100% Merkle proofs valid for counterfactual queries; chain integrity = 100%
- Wall: ~2 hours CPU

### 6. Causal + bitemporal composition cell
- Same follow-up batch
- Method: store causal facts with timestamps; query "what would the system have concluded
  at time T given X had been Y" (counterfactual-as-of)
- HARD-PASS: counterfactual-as-of accuracy >= 0.90 across 20 test queries
- Wall: ~2 hours CPU

### 7. Causal + GDPR erasure composition cell
- Same follow-up batch
- Method: 50 causal facts stored; erase 10 via HMAC keystore deletion; verify counterfactual
  queries do NOT include the erased fact's substitution; verify audit chain still verifies
- HARD-PASS: 0 erased-fact leakage across counterfactual queries; audit integrity = 100%
- Wall: ~2 hours CPU

### 8. Substrate adversarial robustness on bge-small
- Value-add 3x drill cheap pre-test #1
- Method: bge-small retrieval on KF-1's 6 attack types; substrate (bge+W matrix+H=2 BFT)
  retrieval on same attacks; measure AUC per attack type
- HARD-PASS: substrate AUC >= bge AUC + 0.10 on at least 4 of 6 attack types
- Wall: ~2 hours CPU

### 9. Substrate noise/BFT robustness on bge-small
- Value-add 3x drill cheap pre-test #2
- Method: bge-small retrieval on 100 queries with noise std {0.05, 0.20, 0.50}; substrate
  with H=2 multi-head BFT on same; measure recall@1 per noise level
- HARD-PASS: substrate maintains recall@1 >= 0.90 at noise std 0.50; bge degrades >= 0.20
- Wall: ~2 hours CPU

### 10. Substrate structured aggregates (HybridQA-like) pre-test
- Value-add 3x drill cheap pre-test #3
- Method: 200 facts in structured form (entity, attribute, value); 20 aggregation queries
  ("count facts where entity_type = X", "sum values where attribute = Y"); substrate G-counter
  vs vanilla bge+Llama
- HARD-PASS: substrate aggregation accuracy >= 95%; vanilla baseline < 50% (because LLMs
  can't aggregate over a retrieved set reliably)
- Wall: ~3 hours CPU

### 11. LongMemEval base-vs-instruct pre-test
- Multi-benchmark execution 2x drill's gating pre-test
- Method: 25 LongMemEval temporal questions; Qwen2.5-1.5B-BASE vs Qwen2.5-1.5B-Instruct
  conditioned on substrate-retrieved session-history context; measure temporal accuracy
- HARD-PASS: instruct gives >= 0.15 absolute accuracy gap over base (use instruct for full
  LongMemEval); BORDER: gap < 0.15 (either works; pick base for size-fairness story);
  HARD-FAIL: both < 0.40 accuracy (substrate-LongMemEval integration broken)
- Wall: ~1-2 hours CPU

### 12. Predicate audit rescue (P-sweep + composite indexing)
- Cycle 155 predicate_ratio_audit MID follow-up; rescue paths named but never routed
- Method: predicate_ratio_audit at selectivities {1%, 3%, 5%, 7%, 10%, 15%, 20%}; measure
  recall@10 per selectivity to map the degradation curve. Separately test composite
  indexing (combine 2-3 predicates per query) at the high-selectivity regime to see if
  it recovers recall
- HARD-PASS for P-sweep: identify selectivity threshold above which composite indexing
  recovers recall@10 >= 0.85
- Wall: ~3 hours CPU

### 13. Pattern B bundle capacity vs K sweep at production N
- Cycle 159 follow-up; capacity validated at N=1024 with K=24; production N=4096-16384
  capacity unknown
- Method: sweep K (items per bundle) from 5 to 50 at N=4096 and N=16384; measure retrieval
  F1 per K
- HARD-PASS: identify production K limit at N=4096 and N=16384 where F1 stays >= 0.95
- Wall: ~2-3 hours CPU

---

## TIER B: CPU 3-4 hours OR GPU 1-2 hours

### 14. 3-bit W quantization at production N
- Sparse-W alternatives 3x drill recommendation
- Method: same N=8192-16384 production setup as cycle 155 4-bit HP; replace with 3-bit
  symmetric quantization; measure retrieval F1 + K-hop accuracy
- HARD-PASS: F1 drop <= 3% (matching 4-bit's zero accuracy loss criterion)
- BORDER: F1 drop 3-8%
- HARD-FAIL: F1 drop > 8% (3-bit too aggressive on pseudoinverse W)
- Wall: ~1-2 hours GPU

### 15. Product quantization (PQ) on W rows
- Sparse-W alternatives 3x drill recommendation
- Method: treat W rows as vectors; cluster into K=256 centroids via FAISS PQ; store
  centroid indices per row + codebook; measure compression ratio + retrieval F1
- HARD-PASS: compression >= 8x AND retrieval F1 drop <= 5%
- BORDER: compression 4-8x AND F1 drop <= 5%
- HARD-FAIL: F1 drop > 10% OR compression < 4x
- Wall: ~2-4 hours GPU

### 16. Tensor-train decomposition on Pattern A W matrix
- Sparse-W alternatives 3x surprise finding (NOT foreclosed by Marchenko-Pastur for tensor
  format)
- Method: reshape W at N=8192 as a 3-mode tensor; fit tensor-train decomposition at
  varying ranks; measure retrieval F1 vs rank vs total storage
- HARD-PASS: rank that gives F1 >= 0.95 produces compression >= 5x beyond 4-bit baseline
- Wall: ~3 hours GPU

### 17. Modern Hopfield x 4-bit quantization interaction test
- Both validated independently (cycle 155); compat-drill predicted possible interaction
  through weight distribution shifts
- Method: at N=4096 with modern Hopfield exponential energy, apply 4-bit W quantization;
  measure retrieval F1 vs both modern-Hopfield-bf16 baseline and standard-Hopfield-4bit
  baseline
- HARD-PASS: F1 drop <= 3% (no significant interaction)
- HARD-FAIL: F1 drop > 8% (modern Hopfield's exponential energy is incompatible with
  4-bit; need to choose one or the other)
- Wall: ~2-3 hours GPU

### 18. FActScore 20-entity pilot
- Multi-benchmark suite drill recommendation
- Method: 20 Wikipedia biographical entities; substrate stores ~50 facts per entity; query
  via Qwen-1.5B + substrate retrieval; score answers via FActScore (attribution-weighted
  accuracy); compare to bare Qwen + vanilla RAG
- HARD-PASS: substrate FActScore >= 65% AND attribution coverage >= 90%; substrate beats
  bare Qwen by >= 15 percentage points
- Wall: ~4-6 hours CPU

### 19. DP at write-time (Path C from privacy 3x)
- Privacy 3x drill candidate; untested mechanism with formal DP guarantee
- Method: add calibrated Gaussian noise (sigma 0.01-0.10) to stored W matrix entries at
  write time; measure ZKL(50) and KEY-job F1 across sigma sweep
- HARD-PASS: ZKL(50) <= 0.10 at some sigma with KEY F1 drop <= 10%
- BORDER: ZKL in 0.10-0.15
- HARD-FAIL: ZKL > 0.15 across all sigma (DP at write doesn't move it either; truly all
  linear DP avenues exhausted)
- Wall: ~3 hours CPU

### 20. TruthfulQA coverage analysis
- Multi-benchmark drill recommendation
- Method: TruthfulQA 817-question topic classification; identify what fraction overlaps with
  Wikipedia-derived knowledge store; sample 100 questions; run MC1 accuracy with substrate-
  conditioned Qwen-1.5B vs bare Qwen
- HARD-PASS: coverage >= 60% AND MC1 improvement >= 15pp vs bare
- HARD-FAIL: coverage < 40% (TruthfulQA not retrievable from Wikipedia substrate)
- Wall: ~3-4 hours CPU

---

## Sequencing recommendation

Run Tier A in parallel as CPU capacity allows; ~13 cells, total ~26 hours CPU
(distributed). Most cells return same-day.

Tier B sequences after Tier A informs:
- Storage compression cells (14-17) gate on Pattern B compression results from Tier A
- FActScore pilot (18) gates on benchmark integration scaffolding from cells 11 + 12
- DP-at-write (19) gates on whether the Hyp C mitigations (in flight) close the privacy
  question
- TruthfulQA (20) gates on benchmark integration

Total wall for full 20 if parallelized aggressively: 3-5 days CPU + 8-10 hours GPU.

## Decision tree pointers

For each cell's HARD-PASS / BORDER / HARD-FAIL outcome, the decision rules are inherited
from the source drills. The most consequential decisions per cell are flagged in the
methods above. File BORDER cases for my review; HARD-PASS / HARD-FAIL apply autonomously
per the source drill's recommendation tree.

## Coverage gaps still NOT routed

For completeness, the following experiments from today's drills are intentionally NOT
in this routing (deferred or out-of-scope):

- Path D per-customer encoder fine-tuning (premium HIPAA tier; 1-2 weeks per customer;
  engineering not research)
- Path H homomorphic encryption (very expensive; deferred)
- Iterative Pattern B k>2 (gated on k=2 compose result already validated)
- Question reformulation + re-retrieve (predicted dead-end at 1.5B per multi-hop drill)
- LLM-decomp at 3B (conclusively closed by published Fano-style upper bound + cycle 158)
- MuSiQue smoke run (dataset not on runner; HotpotQA stand-in covered)
- StreamingQA (deferred to post-v1)
- Demo pipeline 3-component smoke test (engineering gate, not research; awaiting user
  commit to demo build)
- Demo UI latency SLA test (engineering, not research)
- Tied-weight write rules / circulant W (algebraically risky; deferred)
- Bloom filter pre-stage (storage win at query side, not per-fact)
- Huffman entropy coding (already measured at cycle 158 MID 1.21x; ship as default)

## Cross-references

- All today's drill output files: notes/research_drill_*_2026-06-07.md
- Multi-dim acceptance criteria: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md
- Methodology pre-test rule: ~/.claude/projects/d--AI/memory/feedback_drill_pretest_required.md
- Production architecture (with today's evening updates): ~/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md

---

**END.**

**Exp-Dev:** Tier A in parallel as capacity allows; Tier B sequenced after Tier A informs.
Apply HARD-PASS / HARD-FAIL decision rules autonomously per the source drill recommendations.
File BORDER outcomes + any cross-cell synthesis questions to me.

Methodology pre-test rule applies throughout. No proxy substitutions without empirical
equivalence sanity check first.
