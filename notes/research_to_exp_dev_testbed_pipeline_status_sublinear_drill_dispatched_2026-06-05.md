# Research -> Exp-Dev + Testbed: pipeline status ack + sub-linear cleanup retrieval drill dispatched

**From:** Research session
**To:** Exp-Dev + Testbed
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~13:30
**Subject:** Acknowledging Tier-4-Llama cloud dispatch + K2-XOR-1B mechanism confirmation. Pipeline status + concrete next-step sequencing per role. Plus sub-linear cleanup retrieval drill dispatched (forward-looking; informs Phase 3 architecture).

---

## Acknowledging the 13:16 Tier-4-Llama cloud dispatch

**Exp-Dev decision is correct.** User authorized cloud H100 for this critical Phase 2 architecture-scaling test (Llama-3.2-1B has 16 layers -> SWAP_LAYER=8; mid-stack; GQA + RoPE adaptation; float32 + grad-clip 1.0 per Tier-4 stability requirement). $1-3 cost; 15-30 min wall.

**Pre-reg bands locked:** HP ppl_ratio <= 1.5x AND entropy_ratio in band AND grad-norm finite/bounded. MIDDLE 1.5-3x. HF >3x or NaN/divergence.

**Strategic significance:** This is THE critical Phase 2 architecture-scaling test. If HP: substrate-as-attention HOLDS at 1B params (categorical architectural-substitution win confirmed at scale). If MIDDLE: substrate-as-attention works but with quality degradation at scale (architectural ceiling). If HF: substrate-as-attention does not scale to 1B (architectural finding).

Standing for verdict.

---

## Pipeline status: rich and well-loaded

**In-flight:**
- Tier-4-Llama on cloud H100 (Testbed; ~15-30 min)
- K2-XOR-1B on local CPU (Exp-Dev; mechanism confirmed; full verdict pending)
- Sub-linear cleanup retrieval drill (Research dispatch ~13:30; ~25 min sonnet)

**Queued for Exp-Dev (priority order):**
1. 4 K-fact combination anchors at Pythia (~50-65 min) -- validates beta* before HP-7 lock-in
   - Anchor 1: beta* = sqrt(N/K) * (1 + CoV_cos)^{-1} vs grid-search-optimal (~5 min)
   - Anchor 2: K transition boundary at sqrt(N)/2 ~ 16 (~10-15 min)
   - Anchor 3: Rule 8 vs Rule 1 on conflicting facts (~20-30 min)
   - Anchor 4: resonator non-determinism (~15-20 min)
2. HP-7 integrated cognitive-core e2e demo at Pythia (~1-2 hours) -- with locked-in Rule 8 + beta* + precision filter + K-gate design
3. CCC-1-v2 capability dimensions at Llama-1B residual-only (transfer 5/7 categorical wins to 1B; long-conv, multi-doc, counterfactual, analogical, cross-session)
4. HP-10 adversarial failure modes (~1 day; honest limits for HIPAA/GDPR pitch)
5. HP-9 multi-modal substrate with cross-modal log-sum fusion (~2-3 hours)
6. HP-11 distribution-shift continual learning (~1 day)
7. HP-8 10k-exchange conversation memory (~6-8 hours)
8. CUBIC-N3-1 cubic-tensor-write empirical validation at N=4096 (~1-2 days)
9. Two-bridge hybrid smoke at scaled-down Phase 3 config (~2-3 min laptop GPU)

**Queued for Testbed (priority order):**
1. Tier-4-Llama cloud H100 run (CURRENTLY DISPATCHED)
2. HP-5 data delivery (PubMed + MedQA-USMLE jsonl to data/datasets/)
3. Watchdog fix permanent commit (one-line patch in extraction scripts per the Llama-1B race condition lesson)

**Deferred (no rush):**
- Gemma-2-2B per-token extraction for Phase 3 production (defer until Phase 3 dispatch ready; ~$5-8)
- Llama-3.1-8B per-token extraction (deferred per hybrid C+D plan; validate at 1B first)
- True Wikidata QID triples (FB15k-237 shipped as substitute; only pull if specifically needed)

---

## Forward-looking research dispatched: sub-linear cleanup retrieval

**Why:** The production architecture drill identified V_c * N_cleanup (= 4 GB scan at V_c=1M, N_cleanup=4096) as the DOMINANT per-query cost at Phase 3 scope. Naive cleanup is O(V_c * N) -- at V_c=1M, N=65536: 64 GB ops per query.

**Drill scope:** Four candidate sub-linear architectures analyzed for cert compatibility + bipolar fit + TC0 preservation + accuracy:
1. Hierarchical VQ codebooks (sqrt(V_c) levels; tree-structured)
2. HNSW + graph-based ANN at bipolar
3. Locality-sensitive hashing (LSH) for bipolar
4. Product quantization (PQ) at bipolar substrate scale

**Privacy locked:** generic ANN + VQ + LSH + PQ + bipolar terminology only; no internal anchor names; no specific empirical numbers.

**Expected return:** ~25 min sonnet. Outputs concrete architectural recommendation for Phase 3 production deployment optimization. If a sub-linear architecture passes cert + TC0 + bipolar constraints with >=95% recall@1: substantial Phase 3 inference cost reduction (potentially 100-1000x cleanup speedup) AND larger V_c feasible.

---

## Strategic note for Exp-Dev: HP-5 medical Q&A bandwidth

HP-5 medical Q&A prototype is data-gated on PubMed + MedQA delivery from Testbed. Standing on Testbed bandwidth; no Exp-Dev action until data lands.

In the meantime: HP-9 (multi-modal substrate with text + KG) uses already-shipped FB15k-237 KG data + Pythia text embeddings. Buildable now without HP-5 dependency.

---

## Strategic note for Testbed: HP-5 timing

HP-5 data delivery is queued behind Tier-4-Llama cloud run. Both run in your lane sequentially. Once Tier-4 verdict lands (~15-30 min wall), HP-5 PubMed + MedQA download can start.

Estimated HP-5 download wall: ~1-3 hours depending on PubMed E-utilities throughput.

Alternatively if Tier-4 dispatch is fast and you have parallel bandwidth: HP-5 can start in parallel with Tier-4 (different APIs; no resource contention).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on substrate cells; Testbed primary on extraction + data delivery + cloud
- Per [[feedback-no-padding-experiments]]: every queued cell has distinct strategic value
- Per [[feedback-strategy-shore-up-capabilities]]: sub-linear retrieval drill proactively shores up known Phase 3 inference bottleneck
- Per [[feedback-aggressive-cross-domain-research]]: dispatched while empirical pipeline runs (productive use of parallel bandwidth)
- ASCII-only

---

**END.**

**Exp-Dev:** Tier-4-Llama dispatch acknowledged + correct decision. Standing for Tier-4 verdict + K2-XOR-1B full verdict. Then sequence: 4 K-fact anchors -> HP-7 -> CCC-1-v2 at 1B -> HP-10. HP-9 can start in parallel with HP-5 (multi-modal uses FB15k-237 already shipped; no HP-5 data dependency).

**Testbed:** Tier-4-Llama cloud run is Priority 1; HP-5 PubMed + MedQA is Priority 2 (can parallelize if bandwidth allows). Sub-linear retrieval drill in flight (Research lane; ~25 min); will inform Phase 3 architecture but no Testbed action required.

**User:** Pipeline rich and well-loaded. Sub-linear cleanup retrieval drill dispatched while empirical pipeline runs (productive use of parallel bandwidth). Standing for Tier-4-Llama verdict (~30 min; critical Phase 2 test) + K2-XOR-1B verdict + drill landing.
