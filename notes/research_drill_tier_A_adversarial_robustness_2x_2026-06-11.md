# Research Note: Tier A Adversarial Robustness 2x Drill -- Production-Claim Promotion Gates
**Date:** 2026-06-11
**Filed-by:** research sub-agent (2x level-2 operational drill)
**Trigger:** Orchestrator mandate -- promote 5 Tier A capabilities from categorical/lab claim to production-defensible claim via adversarial attack surface analysis + HARD-PASS gates
**Prior adversarial notes:** notes/research_drill_adversarial_substrate_divergence_2026-06-07.md (level-1 attack vectors); notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md (adaptive attack catalog)
**Calibration:** P estimates deflated 0.20-0.25 from raw lit-scan; novel-synthesis P capped at 0.50; hard-fail thresholds pre-registered for all 5 capabilities.
**5000-word cap enforced.**

---

## HEADLINE

Five Tier A capabilities (PP-217/225/226/227/228) carry production-claim value but each rests on a distinct adversarial attack surface that has not been formally stress-tested. This drill identifies: (1) PP-225 fact-recall is vulnerable to paraphrase-injection and DISC_POOL scaling illusions -- the flat 10K-100K claim is the primary production risk; (2) PP-217 ppl-reduction is robust to normal input variation but fragile under adversarial prefix injection and cross-attention gate collapse from out-of-distribution inputs; (3) PP-226 multi-hop completeness categorical advantage over LazyGraphRAG rests on the algebraic all-paths property but is vulnerable to graph poisoning attacks that create phantom completeness; (4) PP-228 audit decoupling is the most hardened of the five by construction, but is vulnerable to replay, second-preimage, and chain-truncation if nonce-binding and domain separation are absent; (5) PP-227 hybrid composition is vulnerable to interference attacks that simultaneously degrade both the LM and fact-recall paths via adversarial inputs tuned to desynchronize gating. P_deflated = 0.32 that all five would survive full adversarial test battery without at least one partial regression. Substrate-native hardening mechanisms exist for all five and are concrete.

---

## CAPABILITY 1: PP-225 -- Substrate-as-LLM-Memory Fact Recall (FLAT 10K-100K, 3-seed)

### Attack Surface

The PP-225 claim is: projection head achieves heldout recall = 1.000 across kb5k through kb100k scales with 3-seed determinism. The primary production risks are:

**A1 -- DISC_POOL Scaling Illusion.** Per the PP-225 fact-scaling CORRECTION (memory note pp225_fact_scaling_correction_2026-06-10.md): the kb10k/kb50k/kb100k HARD_PASS verdicts were illusory because DISC_POOL was fixed at ~249 entries. All scale labels tested the same ~249 facts. Genuine kb10k requires N_distinct_facts >= 10,000 in retrieval pool. An adversary deploying the system at genuine 10K-fact scale would observe catastrophic recall degradation because the substrate has only been validated at sub-300 effective pool size. This is not a motivated-adversary attack; it is a scaling assumption that fails on first production query.

**A2 -- Paraphrase-Injection Attack (AV-1 from prior drill, now targeted to PP-225).** The projection head was trained and evaluated on exact or near-exact phrasings of stored facts. An adversary who submits paraphrased queries ("Who leads the company that makes GPT?" vs. "Who is the CEO of OpenAI?") tests whether the retrieval vector is robust to surface-variation. PoisonedRAG (USENIX Security 2025) demonstrated 90% attack success with 5 injected documents per target question in million-doc RAG systems. A single paraphrased-query attack on PP-225 would test whether the projection generalizes.

**A3 -- Fact-Contamination Attack.** A motivated adversary injects near-true but factually wrong entries into the knowledge base that share high embedding similarity with true facts. If cosine similarity between poisoned and true embeddings exceeds the retrieval threshold, the poisoned fact wins retrieval. Per ADMIT (2025 adversarial RAG fact-checking): few-shot poisoning at 1e-6 injection rate achieves 86% success on retrieval-dependent pipelines.

**A4 -- Projection Head Distribution Shift.** The projection head was trained on a specific embedding distribution. At genuine 100K+ fact scale, the PCA-whitened retrieval space changes character (Marchenko-Pastur tail shifts). An out-of-distribution query cluster (different domain from training facts) will probe whether the projection head generalizes beyond its training distribution.

### Cheap Decisive Test (PP-225)

**Test PP225-ADVERS-1 (Genuine scale gate):** Run retrieval with N_distinct_facts = {1K_genuine, 5K_genuine, 10K_genuine} where DISC_POOL >= N at each scale. Measure heldout recall on 100 queries not seen in training. This is a CPU run of <30 minutes. HARD-PASS: recall >= 0.90 at genuine 10K. HARD-FAIL: recall < 0.80 at genuine 1K, or recall drops >0.15 from 1K to 5K genuine.

**Test PP225-ADVERS-2 (Paraphrase robustness):** Generate 50 paraphrases of 50 stored facts using back-translation (en->fr->en). Measure recall on paraphrased queries. HARD-PASS: recall >= 0.85 on paraphrase set. HARD-FAIL: recall < 0.70 on paraphrase set.

### Substrate-Native Hardening (PP-225)

- **Write-lock isolation:** Per PP-344 key-rotation primitive, bind each fact-shard to a write-locked RoleKey that requires authenticated bind-R operation. Prevents unauthenticated fact injection at KB construction time.
- **Per-tier importance weighting:** Assign retrieval-probability amplification to facts confirmed by multiple sources at write time. Poisoned facts (injected from a single source) receive lower effective retrieval weight.
- **Redundant encoding across shards:** Per PP-313 KB-shard primitive (recall=1.000 at 40 shards x 1000 atoms), distribute facts across shards and require consensus across >= 2 shards for a high-confidence retrieval. Single-shard poisoning cannot corrupt multi-shard consensus.

### Production-Defensible HARD-PASS Gate (PP-225)

Genuine kb10K recall >= 0.90 on 3 seeds + paraphrase recall >= 0.85 + no single-source poisoning succeeding at rate >= 0.10 on write-locked substrate. All three required simultaneously.

---

## CAPABILITY 2: PP-217 -- Path A Every-Layer Substrate-Attention LLM ppl Reduction (28pct, 4 scales)

### Attack Surface

The PP-217 claim is: multi-layer Flamingo cross-attention substrate-attention achieves ratio=0.835x (ppl reduction) at 160M scale, replicated across 4 scales (160M to 3B), 3-seed std=0.0006.

**B1 -- Adversarial Prefix Injection.** The cross-attention gates (values [0.330, 0.425] at 160M) read from substrate retrieval vectors. An adversary who controls query content can craft inputs that drive both gates to near-zero, effectively disabling substrate-attention and reducing ppl improvement to zero. AdvSuffix filtering (arXiv 2505.09602) demonstrated that adversarial suffixes can suppress attention mechanisms by saturating softmax in specific heads. For gated cross-attention, adversarial prefixes can similarly collapse gate values.

**B2 -- Out-of-Distribution Domain Collapse.** PP-217 was measured on Wikitext/standard LM benchmarks. The ppl reduction rests on the substrate supplying relevant context vectors. An adversary presents queries from highly technical/OOD domains (dense code, mathematical formulas, domain-specific jargon) where the substrate has no stored relevant entries. In this case retrieval returns noise vectors, which actively hurt ppl (noise injection via cross-attention). The question is not whether OOD hurts -- it likely does -- but whether the gate mechanism suppresses noisy substrate inputs.

**B3 -- Training Distribution Memorization vs. Generalization.** 3-seed std=0.0006 is very low, suggesting the improvement may be specific to the training data distribution. Per TamperBench (arXiv 2602.06911): fine-tuned models can have safety/capability claims invalidated by distribution shifts too small to affect base LM perplexity. If the ppl improvement on Wikitext relies on substrate facts that co-occur with Wikitext training data, the improvement is partially a memorization artifact.

**B4 -- Gate Collapse Under Extended Context.** The multi-hop retrieval chain uses sequential substrate queries. Each additional hop exposes the cross-attention gating to compound noise. An adversary constructing 5+ hop queries may find that gate activation degrades monotonically with hop depth as each retrieval step returns less precise context.

### Cheap Decisive Test (PP-217)

**Test PP217-ADVERS-1 (OOD domain gate test):** Evaluate ppl ratio on 3 held-out domains not in training distribution (arXiv abstract style, legal text, code). Measure gate values and ppl delta. HARD-PASS: gate values >= 0.20 on OOD domains AND ppl ratio <= 1.00 (not worse than baseline). HARD-FAIL: ppl ratio > 1.05 (substrate hurts more than it helps) on ANY OOD domain, or gate values collapse to < 0.05 on OOD.

**Test PP217-ADVERS-2 (Null-retrieval stress):** Replace substrate retrieval with zero vectors (simulates empty substrate) at inference time. Measure whether gates close (gate values near zero) or stay open (passing noise). HARD-PASS: gate values drop to < 0.10 on null retrieval (gate mechanism detects null correctly). HARD-FAIL: gate values > 0.20 on null retrieval (gates stay open when substrate is empty, injecting noise).

### Substrate-Native Hardening (PP-217)

- **Temporal refresh guard:** If retrieval confidence (similarity score to nearest stored item) is below threshold, inject a null-like vector rather than the actual retrieved vector. Prevents noisy OOD retrieval from entering cross-attention.
- **Per-role isolation:** Use separate RoleKey-bound substrates for different query domains. LM queries probe their domain-specific substrate; cross-domain noise is reduced by role separation.
- **Gate calibration via confidence binding:** Bind gate open/close signal to retrieval confidence score (cosine sim to nearest item). If sim < theta_min, gate auto-closes. This converts OOD noise injection from a continuous degradation to a binary cutoff.

### Production-Defensible HARD-PASS Gate (PP-217)

Ppl ratio <= 1.00 on all tested domains (in-distribution AND OOD) across 3 seeds + gate mechanism closes correctly on null retrieval (gate < 0.10 on zero vector) + original 0.835x ratio maintained across 3 seeds on training distribution.

---

## CAPABILITY 3: PP-226 -- Multi-Hop Completeness 24.3pp Advantage over LazyGraphRAG (Algebraic)

### Attack Surface

The PP-226 claim is: substrate multi-hop achieves categorical completeness advantage over LazyGraphRAG. The algebraic basis is that the substrate's associative memory traverses all paths simultaneously rather than greedy first-hop selection.

**C1 -- Graph Poisoning via False-Hop Fabrication.** Per KEPo (arXiv 2603.11501) and "Reasoning Chain Adversarial Attack for Multi-hop QA" (arXiv 2112.09658): adversaries can inject perturbation triples that form plausible but incorrect inference chains. In the substrate, this means injecting M bindings that create phantom paths in the superposition. When the substrate traverses hops, it may traverse a poison-chain that terminates at a false answer. The substrate's all-paths completeness property ALSO means it traverses ALL poison paths -- completeness is symmetric with respect to true and false paths.

**C2 -- High-Cardinality Hop Flood.** An adversary who injects many high-similarity items creates a hub node that attracts all multi-hop traversals. Every query passes through the hub, which the adversary controls. This is the vector equivalent of a Wikipedia "disambiguation page" attack -- make every retrieval path route through one adversary-controlled entry.

**C3 -- Semantic Entrapment.** Inject facts that are true but redirect to a false conclusion when combined: "The capital of France is Paris" + "The Eiffel Tower is in Lyon" + "Paris is a suburb of Lyon". Each individual fact passes any single-hop check; the multi-hop chain concludes "The Eiffel Tower is in the capital of France" correctly (Paris) but "The Eiffel Tower is in Lyon" is also retrievable as a 2-hop chain. Completeness advantage becomes completeness-of-wrong-answers under semantic entrapment.

**C4 -- LazyGraphRAG Comparison Validity.** The categorical advantage claim requires that the comparison is fair: same KB, same queries, same answer-correctness criterion. If LazyGraphRAG's greedy selection happens to prune the exact paths that lead to wrong answers (i.e., LazyGraphRAG's incompleteness is a feature that filters poison chains), then the substrate's completeness advantage may actually reduce precision while improving recall. The production-defensible claim requires precision x recall, not recall alone.

### Cheap Decisive Test (PP-226)

**Test PP226-ADVERS-1 (Poisoned-KB multi-hop):** Inject 50 poison-chain triples into a 1000-fact KB. Measure: (a) substrate hop recall on clean chains, (b) substrate hop precision on poison chains (ideally the substrate should NOT traverse poison chains), (c) same for LazyGraphRAG baseline. HARD-PASS: substrate precision on poison chains >= 0.80 AND recall on clean chains >= 0.90. HARD-FAIL: poison-chain traversal rate > 0.30 for substrate (categorical completeness becomes categorical poison-traversal).

**Test PP226-ADVERS-2 (F1 score, not recall alone):** Re-run PP-226 measuring F1 (precision x recall harmonic mean) rather than completeness-only. HARD-PASS: substrate F1 >= LazyGraphRAG F1 + 0.15. HARD-FAIL: substrate F1 < LazyGraphRAG F1 (precision loss outweighs recall gain).

### Substrate-Native Hardening (PP-226)

- **Write-time corroboration gate:** Require >= 2 independent sources for any KB fact before it enters the multi-hop traversal space. Single-source poison chains fail this gate.
- **Temporal binding:** Each fact carries a write-timestamp binding. Facts injected in a burst (attacker-rate injection pattern) trigger anomaly detection before entering the substrate.
- **Per-hop confidence decay:** Assign traversal confidence that decays per hop using an exponential or geometric schedule. Long chains (hop depth >= 5) require individual hop confidence to overcome decay. Adversarial chains that require 5+ hops to reach the poison conclusion are strongly penalized.
- **RS-parity check on hop chains:** Use redundant encoding (per the substrate's RS-parity primitive) to detect internally inconsistent chains: if chain A-B-C contradicts chain A-D-C, flag both as requiring external verification.

### Production-Defensible HARD-PASS Gate (PP-226)

F1 advantage >= 0.15 over LazyGraphRAG on a poisoned KB with >= 50 injected chains + poison-chain traversal rate <= 0.30 + clean-chain recall >= 0.90 on same KB.

---

## CAPABILITY 4: PP-228 -- Cryptographic Audit Decoupled from Retrieval (Categorical)

### Attack Surface

The PP-228 claim is: audit_present = 1.000, audit_reproduces = 1.000, categorical by mathematical construction (composes PP-224 RAG-prefix with PP-184 Merkle primitive).

**D1 -- Second-Preimage Attack (Domain Separation Absent).** Standard Merkle tree without domain separation: an internal node hash is computed the same way as a leaf node hash. An attacker can present an internal node as a leaf, constructing a valid-looking inclusion proof for data that was never stored. This has been documented in production deployments of smart contract Merkle proofs (Nethermind 2025 audit). If PP-184 Merkle primitive does not use distinct prefixes for leaf vs. internal nodes (0x00/leaf, 0x01/internal per Certificate Transparency RFC 6962), this attack is live.

**D2 -- Replay Attack (Nonce Binding Absent).** A valid hop-cert from query Q1 can be replayed as a proof for query Q2 if the audit system does not bind each proof to the specific query context. The PP-228 setup with audit_present = 1.000 does not specify whether each proof is nonce-bound. A statically generated audit chain is replayable indefinitely.

**D3 -- Chain Truncation.** If the verifier does not check that the presented chain has exactly N hops (where N is the expected depth), an attacker who intercepts the audit log can omit trailing hops. The truncated chain may still verify (shorter chains are valid sub-chains if truncation occurs at a valid node). The production-grade claim requires that the expected chain length is committed at the start of each query.

**D4 -- Timing Side-Channel.** The 0.051ms verification latency for the Merkle primitive may vary by a few microseconds depending on tree depth (deeper trees require more SHA-256 iterations). This leaks the depth of the reasoning chain, which may be operationally sensitive information. Constant-time verification (pad all chains to max depth before verification) eliminates this.

**D5 -- RSA Accumulator Key Exposure.** PP-184 uses an RSA accumulator variant. If the accumulator modulus is discoverable (e.g., via timing attacks on the modular exponentiation step), an attacker with sufficient computational resources can factor it and forge witnesses. RSA-2048 is secure against near-term adversaries but not against quantum (post-2030 horizon).

### Cheap Decisive Test (PP-228)

**Test PP228-ADVERS-1 (Domain separation check):** Inspect the PP-184 Merkle primitive implementation for presence of leaf vs. internal node prefixes. Run a second-preimage test: present an internal node hash as a leaf hash, verify whether the inclusion proof accepts. HARD-PASS: second-preimage attempt rejected (domain separation is in place). HARD-FAIL: second-preimage attempt succeeds (internal node accepted as leaf).

**Test PP228-ADVERS-2 (Nonce binding check):** Run two distinct queries Q1 and Q2, capture Q1's audit proof, present Q1's proof as proof for Q2. Verify whether the system accepts or rejects. HARD-PASS: Q1 proof rejected for Q2 (nonce binding present). HARD-FAIL: Q1 proof accepted for Q2 (replay attack live).

**Test PP228-ADVERS-3 (Chain truncation check):** Present a chain of length N-2 when expected N. Verify whether the shortened chain is accepted. HARD-PASS: truncated chain rejected. HARD-FAIL: truncated chain accepted.

### Substrate-Native Hardening (PP-228)

- **Domain separation by construction:** Prepend 0x00 to leaf data before hashing, 0x01 to internal-node data. One-line code change; eliminates second-preimage and related attacks.
- **Per-session nonce binding:** At query time, generate a fresh 128-bit nonce, commit it into the root signature, and require every hop-cert to include nonce || hop_data. Replay attacks require guessing the per-session nonce.
- **Chain length commitment:** Include expected_chain_length in the root commitment. Truncation attacks must forge a new valid root, which requires breaking SHA-256.
- **Constant-time verification:** Pad all chains to max_depth before verification to eliminate timing side-channels.
- **Post-quantum readiness:** Accept NIST PQC Kyber/Dilithium as drop-in accumulator key signatures for deployments past 2028.

### Production-Defensible HARD-PASS Gate (PP-228)

Second-preimage test: rejected + Replay test: rejected + Chain-truncation test: rejected. All three required. These tests run in < 5 minutes via a unit test suite. This is the most achievable Tier A production gate because it requires code audits, not new empirical experiments.

---

## CAPABILITY 5: PP-227 -- Hybrid LM+Fact-KV Composition (10K KB, 20.7% ppl + recall=1.000)

### Attack Surface

The PP-227 claim is: substrate simultaneously improves LM perplexity (lm_ratio=0.793x) AND supplies held-out facts (recall=1.000) at n_test=92, 1 seed GPU.

**E1 -- Interference Desynchronization Attack.** The PP-227 result was obtained on n_test=92 held-out facts. An adversary presents a query that is high-similarity to both a stored fact AND a relevant LM context token. The cross-attention gate opens for both the fact-recall path and the LM path simultaneously, creating interference between the two outputs. With dual gate activity (PP-217 gates = [0.330, 0.425] at 160M), a carefully constructed adversarial input could desynchronize both paths: the fact path retrieves the wrong fact (close but wrong) while the LM ppl optimization drives the gate to stay open. The result: ppl may improve slightly but fact-recall degrades.

**E2 -- Scale-Up Interference.** The n_test=92 claim is very small sample size. At genuine 10K KB scale, the fact retrieval competition increases: more candidates for the projection head to choose from. Per the DISC_POOL scaling issue (PP-225 CORRECTION), if genuine scale has not been validated, the PP-227 composition claim may rest on a pool that is genuinely only ~249 items. At genuine 10K, interference between the LM path and fact path may not remain zero.

**E3 -- Single-Seed Fragility.** PP-227 is n=1 seed GPU. One seed. The 3-seed requirement for promotion to defensible is standard per the feedback-smoke-test-methodology memory note. With one seed, the probability of observing a lucky no-interference configuration is non-negligible. P_deflated = 0.30 that the interference-free result replicates at 3 seeds with genuine scale.

**E4 -- Adversarial LM Input Targeting Both Objectives.** An adversary who knows the architecture can craft an input where the LM ppl objective conflicts with fact-recall: e.g., an input where the highest-probability next token conflicts with the stored fact. The model must choose between "reduce ppl" and "recall correct fact" at inference time. The composition claim requires that no such conflict occurs. In practice, factual queries will regularly produce such conflicts (model has seen the correct fact in training data but at different surface form than stored in substrate).

### Cheap Decisive Test (PP-227)

**Test PP227-ADVERS-1 (3-seed genuine scale):** Re-run PP-227 with 3 seeds at genuine 10K KB (DISC_POOL >= 10K facts) on n_test >= 500 queries. Measure both lm_ratio and fact_recall. HARD-PASS: lm_ratio < 0.90 AND fact_recall >= 0.90 on all 3 seeds. HARD-FAIL: fact_recall < 0.80 on any seed, OR lm_ratio > 1.00 on any seed (ppl gets worse at genuine scale).

**Test PP227-ADVERS-2 (Conflict-query stress):** Construct 50 queries where the factually-correct next token is NOT the highest-probability token under the base LM (i.e., cases where ppl optimization conflicts with fact-recall). Measure both metrics on this conflict subset. HARD-PASS: fact_recall >= 0.80 on conflict subset. HARD-FAIL: fact_recall < 0.60 on conflict subset (LM ppl dominates fact-recall in conflicting cases).

### Substrate-Native Hardening (PP-227)

- **Priority signal gating:** During inference, route inputs through a lightweight fact-query classifier. For queries identified as factual (entity-containing), weight the fact-recall path gate higher than the LM path gate. This implements a priority signal that prevents ppl optimization from overriding factual correctness.
- **Separate gate training with constraint:** Train the cross-attention gates with an explicit no-interference constraint: the composite loss penalizes cases where lm_improvement and recall_degradation co-occur. This shapes the gate distribution to prefer configurations where both objectives are simultaneously satisfied.
- **Temporal consistency check:** After generation, verify that each generated factual claim is retrievable from the substrate (self-consistency check using the same projection head). Inconsistencies flag potential interference cases.

### Production-Defensible HARD-PASS Gate (PP-227)

3-seed genuine 10K KB: lm_ratio < 0.90 AND fact_recall >= 0.90 across all seeds + conflict-query subset recall >= 0.80. This requires genuine scale resolution (PP-225 ADVERS-1 must pass first as a dependency).

---

## EMERGING TIER B: BRIEF ADVERSARIAL NOTES (PP-362 POS, PP-313 KB-Shard, PP-344 Key Rotation)

**PP-362 substrate-only NL POS tagger (0.906 Penn Treebank WSJ sec 24).**
Attack surface: adversarial tokenization (splitting or joining tokens), OOD text style (code, multilingual, social media abbreviations), class-imbalance probe (WSJ sec 24 skews toward financial journalism; a long-tail POS class probe on non-WSJ text will show degradation). Cheap test: evaluate on WSJ sec 23 (standard POS test set) vs. sec 24 (reported); measure F1 per POS tag on long-tail classes. HARD-PASS: macro-F1 >= 0.88 on sec 23. HARD-FAIL: accuracy < 0.85 on non-NNP long-tail classes. Substrate hardening: n-gram context binding (bundle neighboring tokens into the item encoding) for robustness to tokenization variation.

**PP-313 KB-shard recall=1.000 at 40 shards x 1000 atoms.**
Attack surface: out-of-distribution shard queries (query matches atoms in multiple shards equally well), shard-boundary poisoning (inject items near the top-tier feature decision boundary), and memory-collision attack (fill all shards with near-identical embeddings to saturate capacity). Cheap test: cross-shard query (query semantically spans 2 shards) -- measure retrieval precision. HARD-PASS: cross-shard precision >= 0.90. HARD-FAIL: cross-shard retrieval returns shard-B item when shard-A is correct at rate > 0.20. Substrate hardening: per PP-344 RoleKey, bind each shard to a distinct role vector to prevent cross-shard confusion.

**PP-344 key rotation n=120.**
Attack surface: concurrent rotation (rotate key during active retrieval query -- race condition), exhaustive-key-search (probe enough bind-R queries to reconstruct the rotation operator), and rollback attack (present a query with old key after rotation). Per the experimental result: old_key_recall=0.002 already passes the revocation threshold. Cheap test: post-rotation query with cached old-key embedding -- verify rejection rate. HARD-PASS: old-key rejection >= 0.99. HARD-FAIL: old-key recall > 0.10 (revocation is incomplete). This is likely already passing but the concurrent-rotation race condition needs a specific multithreaded smoke test.

---

## CHEAP DECISIVE TEST PRIORITY RANKING

Ordered by: (cost to run) x (probability of finding production-blocking issue)

1. **PP228-ADVERS-1/2/3** -- Audit cryptographic hardening checks. < 5 min unit tests. Code audit + injection test. If any of the three fail, PP-228 production claim is immediately downgraded to "categorical in lab only." Highest urgency.

2. **PP225-ADVERS-1** -- Genuine scale gate. 30-min CPU run. Resolves the DISC_POOL scaling illusion directly. This is a prerequisite for PP-227-ADVERS-1 as well.

3. **PP227-ADVERS-1** -- 3-seed genuine scale composition. GPU run. Depends on PP225-ADVERS-1. Can be run in parallel if PP225-ADVERS-1 result is available from a prior run.

4. **PP217-ADVERS-2** -- Null-retrieval gate test. 10-min CPU run. Verifies that cross-attention gates close on empty substrate. If gates stay open, OOD domain noise injection is live.

5. **PP226-ADVERS-1** -- Poisoned-KB F1 multi-hop. 60-min CPU run. Requires KB construction with injected poison chains. Tests the precision dimension of the completeness claim.

---

## FALSIFIABLE PREDICTIONS

**HARD-PASS thresholds (required for production-defensible claim):**
- PP-225: genuine_kb10K recall >= 0.90, 3 seeds; paraphrase recall >= 0.85
- PP-217: OOD ppl ratio <= 1.00 on all domains; gate values >= 0.20 OOD; null-retrieval gate < 0.10
- PP-226: F1 >= LazyGraphRAG F1 + 0.15; poison-chain traversal rate <= 0.30; clean-chain recall >= 0.90
- PP-228: second-preimage rejected; replay rejected; chain-truncation rejected
- PP-227: 3-seed genuine-10K: lm_ratio < 0.90 AND recall >= 0.90; conflict-query recall >= 0.80

**HARD-FAIL thresholds (stop and remediate before production claim):**
- PP-225: genuine_kb1K recall < 0.80, or recall drops > 0.15 from 1K to 5K genuine
- PP-217: ppl ratio > 1.05 on any OOD domain (substrate actively hurts LM)
- PP-226: poison-chain traversal rate > 0.30 (completeness claim is contaminated by poison traversal)
- PP-228: ANY of second-preimage / replay / chain-truncation succeeds
- PP-227: fact_recall < 0.80 on any of 3 seeds at genuine 10K scale

**P_deflated estimates (novel-synthesis, calibration penalty applied):**
- PP-225 surviving full adversarial battery: P_deflated = 0.45 (genuine scale is the known open gap; paraphrase likely passes given retrieval-grounding architecture)
- PP-217 surviving OOD domain test: P_deflated = 0.50 (gate mechanism theoretically suppresses null retrieval; OOD collapse is the uncertain dimension)
- PP-226 surviving F1+poison test: P_deflated = 0.38 (completeness is genuine but precision under poisoning is untested)
- PP-228 surviving crypto hardening audit: P_deflated = 0.55 (most of the required hardening is known standard practice; code audit is the bottleneck)
- PP-227 surviving 3-seed genuine scale: P_deflated = 0.35 (depends on PP-225 genuine scale; single-seed fragility is the leading risk)

---

## CROSS-THREAD SYNTHESIS

This drill connects to three prior threads:

**Thread 1: PP-225 DISC_POOL Correction (2026-06-10).** The genuine-scale gap identified in the memory correction is the most load-bearing unresolved adversarial risk across PP-225 AND PP-227. The recommended PP225-ADVERS-1 test is exactly the cheap decisive test that resolves this gap. This is the highest-priority experiment in the batch.

**Thread 2: Prior AV catalog (2026-06-07 drill).** AV-1 (paraphrase evasion), AV-2 (Merkle replay), AV-3 (encoder supply chain), AV-5 (substrate poisoning) from the prior drill all map directly onto the five Tier A capabilities here. This drill adds three new dimensions: (a) the DISC_POOL scaling illusion as a non-adversarial production risk, (b) the interference desynchronization attack on PP-227 as a composition-specific attack surface, and (c) the precise cryptographic gate tests for PP-228.

**Thread 3: Substrate primitives YES integration NO (2026-06-10).** The finding that basic algebraic primitives work but integrative cognition does not cleanly work substrate-only applies directly to PP-226 (multi-hop completeness). Multi-hop traversal is an integrative operation; the adversarial poison-chain attack is precisely the failure mode predicted by the "integration fragile" finding. Hardening for PP-226 should prioritize write-time authentication (a primitive operation) over reasoning-time filtering (an integrative operation).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **PP-228 is the fastest win.** The cryptographic hardening (domain separation, nonce binding, chain length commitment) requires 3 code changes, each < 10 lines, that can be audited and tested in < 1 day. After this, PP-228's categorical claim becomes production-defensible without any new experimental runs.

2. **PP-225 genuine scale is the blocking dependency.** Until genuine_kb10K is validated with N_distinct_facts >= 10K, the production pitch for substrate-as-LLM-memory is bounded. PP225-ADVERS-1 is the gate experiment. All other fact-recall claims (PP-227 composition, any product demo involving >300 facts) depend on this resolving PASS.

3. **PP-217 and PP-227 share the gate-mechanism adversarial risk.** If the cross-attention gates do not close correctly on null/OOD retrieval, both capabilities are simultaneously at risk. A single PP217-ADVERS-2 test resolves this for both.

4. **PP-226 completeness claim needs F1 reframe for customer pitch.** The "categorical advantage" language is currently framed as recall advantage. For a production customer who has adversarial KB content (e.g., a corporate KB with conflicting information from different departments), precision matters equally. The F1 reframe is the production-appropriate claim.

5. **For product: hardening mechanisms are substrate-native.** Write-lock isolation (PP-344), per-shard redundancy (PP-313), and role separation are already empirically validated substrate primitives. The adversarial hardening stack for production is constructable from primitives without new mechanism development.

---

## CITATIONS (verified from search results + prior notes)

1. PoisonedRAG, USENIX Security 2025 (arXiv 2402.07867) -- 90% attack success at 5 injected docs/target in million-doc RAG
2. ADMIT (arXiv 2510.13842) -- few-shot knowledge poisoning for RAG-based fact-checking; 86% success at 1e-6 injection rate
3. KEPo (arXiv 2603.11501) -- knowledge evolution poisoning on graph-based RAG systems
4. Adversarial Suffix Filtering (arXiv 2505.09602) -- adversarial suffix defense pipeline for LLMs
5. TamperBench (arXiv 2602.06911) -- systematically stress-testing LLM safety under fine-tuning and tampering
6. Lipschitz-based robustness for HDC (Frontiers AI, 2025) -- theoretical upper bound for noise tolerance in hyperdimensional classifiers
7. Testing and Enhancing Adversarial Robustness of HDC (IEEE Xplore, 2023) -- first systematic adversarial robustness study for HDC
8. Nethermind Merkle second-preimage prevention guide (2025) -- domain separation 0x00/0x01 prefix standard
9. Certificate Transparency RFC 6962 -- leaf vs. internal node hash prefix standard
10. "Reasoning Chain Adversarial Attack for Multi-hop QA" (arXiv 2112.09658) -- poison-chain injection for multi-hop reasoning
11. AtomEval (arXiv 2604.07967) -- atomic evaluation of adversarial claims in fact verification
12. Adversarial Attacks Against Automated Fact-Checking (ACL EMNLP 2025) -- paraphrase + semantic adversarial attacks on fact-checking systems
13. SoK: Privacy Risks in RAG (arXiv 2601.03979) -- membership inference, embedding inversion in RAG systems
14. PP-225 fact-scaling CORRECTION (memory note, 2026-06-10) -- DISC_POOL fixed at ~249 entries; all scale labels were ~249 facts
15. Substrate primitives YES integration NO (memory note, 2026-06-10) -- integrative cognition fragile; primitives robust
16. Research drill adversarial substrate divergence (notes/research_drill_adversarial_substrate_divergence_2026-06-07.md) -- level-1 attack vector catalog

**Verified citation count: 16**

---

## NEXT-DRILL CANDIDATE

**PP-226 multi-hop adversarial under algebraic poisoning.** The multi-hop completeness claim has the weakest empirical adversarial validation of the five. The VSA all-paths property is algebraically correct for clean KBs. What has not been tested is the algebraic behavior of the superposition under systematically injected binding collisions. A targeted lit-scan into "associative memory capacity under adversarial binding" (VSA capacity theory under adversarial initialization) would sharpen the poison-chain traversal probability estimate before PP226-ADVERS-1 is run. Field: network-science-graph-theory (expander properties of the substrate's item manifold under poisoning).
