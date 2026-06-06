# Research Drill: fact_checked_khop Optimization and Robustness
# Level-2 Operational Drill -- HP does NOT mean optimal
# Date: 2026-06-06
# Lit-scan penalty applied: P_raw deflated by 0.20; novel-synthesis capped at 0.50

---

## HEADLINE

Per-hop hallucination localization is structurally sound at K<=5 but faces four production gaps: (1) adversarial fabrication injected at intermediate hops degrades localization accuracy more than terminal-hop attacks; (2) confidence accumulation across hops is missing and is the single cheapest architectural lift; (3) latency scales O(K) synchronously but is embarrassingly parallelizable with minimal accuracy loss; (4) a per-hop Merkle-anchored audit chain (combining HP-12 V1 RSA accumulator with step-level hashes) can make the reasoning trace cryptographically verifiable end-to-end -- a capability gap no frontier system has.

---

## Cheap Decisive Test

Inject a fabricated fact at hop position h in a K-hop chain (h = 1, K/2, K-1) and measure:
  - Does the per-hop KF-1 flag activate at the correct hop h?
  - Does accuracy degrade differently for middle-hop vs terminal-hop injections?

Expected: middle-hop injection (h = K/2) causes error propagation that the current binary flag MISATTRIBUTES to later hops (because the downstream hops superficially look consistent with the fabricated premise). This is the key brittleness to confirm.

Cell recipe: 3 x K (K in {3, 5, 10}) x 3 injection positions x 10 seeds = 270 evaluation instances. CPU-only. Wall < 5 min at N=1024.

---

## Falsifiable Predictions

### HARD-PASS thresholds (claim is confirmed)

HP-1: Middle-hop injection localization accuracy >= 0.85 (per-hop flag correctly fires at the injected hop, not a later hop) for K in {3, 5}
HP-2: Confidence-weighted scoring (product of per-hop confidence scores) achieves AUC >= 0.990 on adversarial mixed chains vs AUC = 1.000 on clean -- maintaining near-ceiling with richer signal
HP-3: Parallelized per-hop verification (all K KF-1 calls dispatched simultaneously) achieves >= 0.95x accuracy of sequential verification (showing latency reduction is safe)
HP-4: Per-hop Merkle hash chain (hash of [hop_index || fact || KF1_score]) matches reconstructed root after tamper injection -- audit certifiability confirmed in < 2ms per chain

### MIDDLE-BAND (partial, needs follow-up)

MID-1: Middle-hop localization accuracy in [0.65, 0.85) -- degraded but salvageable with multi-pass
MID-2: Confidence-weighted AUC in [0.970, 0.990) -- marginal improvement; needs calibration tuning

### HARD-FAIL thresholds (claim is refuted or architecture is broken)

HF-1: Middle-hop localization accuracy < 0.65 at K=3 -- binary flag is fundamentally miscalibrated for propagation errors; requires redesign with backward chaining
HF-2: Parallelized verification achieves < 0.90x accuracy -- suggests KF-1 is hop-order-dependent and cannot be safely parallelized without re-sequencing
HF-3: Any K-hop chain with adversarial injection achieves AUC < 0.90 -- the composition as a whole is not robust to adversarial inputs and needs re-anchoring

---

## Sub-Question Analysis

### (1) TRUE CEILING AND WHAT BREAKS IT

AUC = 1.000 at K in {2,3,5} on clean data is consistent with the independently validated KF-1 AUC = 0.999 easy / 0.975 hard. The composition applies KF-1 per hop; the joint AUC is:

  AUC_joint >= 1 - K * (1 - AUC_per_hop)

At K=5 and AUC_per_hop = 0.975: AUC_joint >= 0.875 (lower bound). The observed 1.000 is consistent with easy-regime KB queries where AUC_per_hop is close to 1.000.

The ceiling is broken by:
(a) Hard-regime KB with same-domain plausible fabrications (AUC_per_hop -> 0.975): joint AUC degrades monotonically in K. At K=20 and AUC_per_hop = 0.975: floor at 0.60 -- below production-acceptable.
(b) Error propagation: a fabrication at hop h creates a plausible false premise for hop h+1. Hop h+1 KF-1 sees a locally consistent (but globally wrong) fact and may NOT flag. This is the primary structural weakness -- the per-hop check is LOCAL but errors are GLOBAL.
(c) Adversarial calibration: fabricated facts tuned to sit near the KF-1 decision boundary (confidence ~= 0.5) consistently evade binary flags. These are computationally cheap to construct by an adversary who knows the KF-1 surface.

P_deflated estimate that error-propagation is the dominant failure mode at K >= 5: 0.70 (raw 0.85, deflated by 0.15)

### (2) ARCHITECTURE TWEAKS

A. Multi-pass verification (backward chaining):
After the forward K-hop traversal, run a backward pass that checks each hop's fact against the FINAL answer. Backward chaining catches errors where a plausible middle-hop fabrication went undetected forward but contradicts the answer's support structure.
Algebraic cost: 2K KF-1 calls instead of K. Latency doubles synchronously but parallelizes to ~1.5K if forward and backward overlap.
P_deflated that backward chaining lifts middle-hop localization accuracy by >= 0.10: 0.45

B. Confidence accumulation (STRONGEST near-term lift):
Replace binary per-hop flag with confidence score c_h in [0,1] from KF-1. Two aggregates:
  - Chain confidence product: C_chain = prod(c_h, h=1..K)
  - Weakest-link: C_min = min(c_h)
C_min is more sensitive to single-hop failures; C_chain catches globally low-confidence chains.
Literature basis: ConfSpec (2025) shows that step-level confidence strongly correlates with correctness and enables efficient cascaded verification. Confidence-based stopping cuts compute by 66% (SpecExit) with no accuracy loss.
P_deflated that C_min gives >= 0.005 AUC lift over binary flag on adversarial chains: 0.50

C. Cross-hop consistency check:
For chains where hops share entities (e.g., entity X appears at hop 2 and hop 4), check that KF-1 confidence scores for X are consistent across hops. A score discrepancy > threshold flags a latent contradiction even when neither hop individually triggers a binary flag.
This requires entity-tracking across hops -- implementation complexity is moderate.
P_deflated that cross-hop consistency catches >= 30% of multi-hop adversarial attacks that single-hop flags miss: 0.35 (raw 0.50, deflated 0.15)

D. Selective verification (cheapest throughput lift):
First pass: low-cost retrieval + coarse plausibility check per hop. Only hops with plausibility < threshold (e.g., c_h < 0.85) get full KF-1 verification. Literature: ConfSpec shows most steps are verifiable by lightweight models; only a small fraction require full verification.
Cost: reduces KF-1 calls by 60-80% on clean chains. Risk: attacker learns the threshold and tunes fabrications to sit just above it.
P_deflated that selective verification preserves >= 0.98 AUC of full verification on clean chains: 0.50
P_deflated that selective verification is robust to a threshold-aware adversary: 0.20

E. Audit-cert per hop (HP-12 V1 composition -- HIGHEST product value):
Each hop emits: hash(hop_index || retrieved_fact || KF1_score || timestamp). Hashes are chained in a Merkle tree. The RSA accumulator (HP-12 V1, < 1ms) certifies the root.
This gives a cryptographically verifiable reasoning trace: any external party can prove that the stated reasoning chain was executed with those intermediate scores, without re-running inference.
No frontier LLM system offers this. RAG systems cannot localize WHICH hop failed, let alone certify it.
Merkle proof verification is O(log K) in chain length. For K=20, proof depth = 5 hashes. At modern crypto speeds (< 1 microsecond per hash), Merkle verification overhead is < 10 microseconds.
P_deflated that per-hop Merkle chain is implementable within HP-12 V1 < 1ms SLA at K <= 20: 0.50

### (3) FAILURE MODE CHARACTERIZATION

Failure mode taxonomy (ranked by empirical likelihood):

FM-1 (HIGH): Error propagation without localization
A fabrication at hop h creates a locally consistent premise that KF-1 at hop h+1 accepts. The error reaches the final answer but the localization points to hop h+1 or later (the hop where the chain "breaks open") rather than hop h where the fabrication was injected.
Structural cause: per-hop checks are CONDITIONED on the previous hop's output. If hop h output is wrong but internally consistent (the fabrication is plausible), hop h+1 KF-1 sees a reasonable claim.
Mitigation: backward chaining (architecture tweak B above) or hop-independent retrieval verification (re-retrieve each hop's evidence independently, not from the chain context).

FM-2 (MEDIUM): Multi-hop attribution ambiguity
When multiple hops contribute to an error (e.g., two individually plausible but jointly contradictory facts), neither hop flags at the binary threshold. Both c_h values are 0.6-0.8 (below binary flag threshold but above background). The chain fails but no single hop is clearly flagged.
Mitigation: C_chain product falls well below clean-chain baseline, enabling chain-level rejection even without per-hop localization.

FM-3 (MEDIUM): KB contradiction cascade
If the KB itself has a subtle contradiction (fact A and fact B are both stored but mutually inconsistent at a distant relation), a K-hop path may traverse both. KF-1 correctly flags each fact as "retrieved from KB" (high confidence) but the chain is contradictory. Binary flag: no alert. Cross-hop consistency check (tweak C): alert.
This is distinct from hallucination -- the substrate retrieved correctly but the KB is inconsistent. The current architecture cannot distinguish these.

FM-4 (LOW but HIGH IMPACT): Adversarial boundary attack
An adversary who can observe KF-1 confidence outputs (e.g., via API probing) can construct fabricated facts that consistently score c_h = 0.51 (just above binary flag threshold). These evade detection while being fabrications. Rate of success depends on KF-1 decision surface smoothness.
Mitigation: perturb the KF-1 decision threshold randomly per chain instance (randomized threshold) -- makes boundary attacks unreliable.

FM-5 (LOW): Unconventional reasoning path
Some correct multi-hop chains use non-canonical relation orderings. KF-1 may flag intermediate steps as "unsupported" because the retrieved evidence doesn't match the expected relational template, even though the reasoning is correct. This is a false positive, not a false negative.
Mitigation: evaluate recall (not just precision) of per-hop localization. A recall < 0.90 on correct chains indicates over-flagging.

### (4) PRODUCTION READINESS GAPS

Gap 1 -- Latency scaling (O(K) synchronous):
Current architecture: K sequential KF-1 calls. At K=20 with each call taking t_kf1 ms, total latency = 20 * t_kf1.
For a plausible t_kf1 = 5ms (fast embedding lookup + distance threshold), K=20 = 100ms. Acceptable for batch audit; borderline for real-time.
Parallelization path: all K KF-1 calls are INDEPENDENT if the retrieved facts are known. If retrieval is done in a single batched KB lookup, all K KF-1 calls dispatch simultaneously. Speedup: K/max_parallel_factor. With K=20 and 20-way parallelism, theoretical latency ~ t_kf1 + overhead.
P_deflated that parallelization is safe (no accuracy loss from batching): 0.45

Gap 2 -- Memory: KB lookup per hop:
Each hop requires KB lookup. At K=20 with KB of size M facts, total KB access = 20 lookups. If KB is in-memory (feasible for substrate-scale KBs), this is a cache-bandwidth problem, not a latency problem.
For production-scale KBs (M >> 10^6), each lookup requires approximate nearest-neighbor search, adding O(log M) cost per hop.

Gap 3 -- Throughput at batch scale:
Per-hop verification is parallelizable ACROSS chains, not just within a chain. A batch of B chains with K hops each = B*K KF-1 calls, all independent. GPU-batched KF-1 achieves throughput limited by the batch KF-1 implementation.
No identified fundamental throughput barrier. The bottleneck is KB bandwidth, not compute.

Gap 4 -- Confidence calibration on out-of-domain KB:
KF-1 was validated at AUC = 0.975 on hard same-domain. On cross-domain KB (e.g., legal domain knowledge applied to biomedical chain), calibration is unknown. Out-of-domain degradation is the leading production risk.
P_deflated that cross-domain AUC stays above 0.90: 0.30 (raw 0.45, deflated 0.15)

Gap 5 -- Audit cert integration (HP-12 V1):
Current HP-12 V1 certifies answers. Extension to certify per-hop intermediate steps requires: (a) capturing KF-1 score at each hop, (b) building Merkle chain over [hop_i, fact_i, score_i], (c) accumulating Merkle root in RSA accumulator. This is an engineering extension, not a research problem.
Estimated engineering effort: 1-2 days to retrofit existing HP-12 V1 pipeline.

### (5) SLIGHT ALTERNATIVES THAT MIGHT DO BETTER

Alternative A -- Confidence-weighted chain (RECOMMENDED FIRST):
Replace binary per-hop flag with C_min = min(c_h) threshold and C_chain = prod(c_h). Implement in a single day. Expected AUC gain: small on clean data (AUC near ceiling), measurable on adversarial. Cost: zero additional KF-1 calls.

Alternative B -- ConfSpec-style cascaded verification:
Low-cost first-pass (e.g., embedding cosine distance) gates which hops receive full KF-1. Reduces compute by ~60% on clean chains. Risk: threshold tuning required per domain.

Alternative C -- Backward chain verification pass:
After forward K-hop traversal, verify each hop against the final-answer support. Doubles KF-1 calls but catches error-propagation failures that forward-only misses. Highest accuracy lift for adversarial inputs. Recommended for high-stakes audit use cases.

Alternative D -- Hierarchical verification (groups of hops):
Verify hops in groups of g (e.g., g=3): if the group passes, skip individual hop verification. If the group fails, drill down. Reduces average KF-1 calls for clean chains. Analogous to hierarchical inspection sampling in manufacturing QA (Springer AOR cited below). P_deflated = 0.35 (raw 0.50, deflated 0.15).

Alternative E -- Cross-hop entity consistency:
Track entity mentions across hops. Require KF-1 confidence on the SAME entity to be consistent across hops (max c_h - min c_h < epsilon). Detects KB contradictions that single-hop checks miss. Adds one pass over the hop sequence -- O(K) cost, no additional KF-1 calls.

### (6) CROSS-DOMAIN ANALOGUES

Domain 1 -- Manufacturing in-line QA (optimal stopping):
Springer AOR (sequential quality control in batch manufacturing): optimal inspection policy is threshold-based on cumulative defect signal, not fixed-interval. Translated: per-hop KF-1 should use an ADAPTIVE stopping threshold -- early-exit if chain confidence C_chain drops below threshold before completing all K hops.
ScienceDirect (optimal inspection policies): dynamic programming gives the optimal trade-off between inspection cost and penalty for defective output. Directly applicable: cost of KF-1 call vs. penalty for passing a hallucinated chain.
Key insight: in-line QA at each station is CHEAPER than end-of-line inspection when defect rates are moderate. For chains with known high hallucination risk (long K, hard domain), per-hop checks are optimal. For short K on easy domains, end-of-chain check suffices.

Domain 2 -- Distributed consensus (PBFT fault localization):
PBFT requires 3f+1 nodes to handle f Byzantine failures. Translated: a K-hop chain with per-hop verification needs KF-1 precision >= (K-f)/K to correctly localize f faulty hops.
PBFT's two-phase prepare/commit directly maps to forward-pass/backward-pass verification. The key PBFT insight: a single Byzantine node cannot cause divergence because the majority vote overrides it. For reasoning chains: if K is large enough and most hops are clean, the minority of fabricated hops can be identified by their divergence from the consensus of the other hops.
This suggests a QUORUM-BASED localization strategy: a hop is flagged as fabricated only if its KF-1 score is an outlier relative to the other K-1 hops' score distribution. This is more robust than a fixed per-hop threshold.
P_deflated that quorum-based localization outperforms fixed-threshold on adversarial chains: 0.35

Domain 3 -- Formal verification / proof checking (per-step):
Lean 4 / Coq: every proof step is independently checkable in O(1) via type theory. A proof chain is valid iff every step is valid -- there is no error propagation in formal proof because each step's validity is defined solely by its local pre/post-conditions.
This is the IDEAL that per-hop KF-1 approximates but does not achieve. The gap is that KF-1 is probabilistic (not deterministic) and KB retrieval is approximate (not symbolic).
Key insight: the formal verification analogy identifies the EXACT failure mode of fact_checked_khop -- probabilistic verification admits error propagation that formal verification does not. The fix is backward chaining (post-hoc proof obligation discharge), which is the natural analog of "re-checking a proof step given the final theorem statement."

Domain 4 -- Medical differential diagnosis (sequential Bayesian updating):
Per-step differential diagnosis: at each step, the prior belief about the diagnosis is updated by the new test result. If a test result is inconsistent with ALL remaining hypotheses, the clinician flags an "unexpected finding" and re-evaluates earlier steps.
Translated: after each hop, update a chain-level belief P(chain correct | hops seen so far). If P drops below threshold, trigger backward re-verification. This is EXACTLY the Bayesian backward chaining described in alternative C.
Clinical literature shows that "anchoring bias" (sticking with an early hypothesis despite contradictory later evidence) is the leading diagnostic error. The analogous failure in fact_checked_khop is accepting a fabricated hop h because all subsequent hops "fit" the false premise.

### (7) ROBUSTNESS BENCHMARK DESIGN

Recommended test suite to reveal true performance ceiling:

Tier 1 -- Clean baseline:
  - K in {2, 3, 5, 10, 20}
  - KB sizes: small (100 facts), medium (10K facts), large (1M facts)
  - Expected: AUC near 1.000 for K <= 5, degrades at K >= 10 due to compounding

Tier 2 -- Adversarial injection:
  - Single-hop fabrication at position h in {1, K//2, K-1}
  - Fabrication types: (a) plausible but wrong [hardest], (b) confident but wrong [boundary attack], (c) unsupported [easiest]
  - Measure: localization accuracy (does flag fire at correct hop h?)

Tier 3 -- KB stress tests:
  - Cyclic KB: entity A -> entity B -> entity A (K-hop path loops)
  - Contradictory KB: two facts about same entity that cannot both be true
  - Under-specified: query has multiple valid K-hop paths giving different answers
  - Expected: cyclic KB causes infinite-loop risk in path traversal (needs path deduplication)

Tier 4 -- Compositional generalization:
  - Unseen relation combinations (relations appear individually in training but not this combination)
  - Cross-domain transfer (KB from different domain than KF-1 training)
  - Variable-arity relations (some hops involve 3-ary relations, not binary)

Tier 5 -- Production-scale:
  - K=20 with KB=10M facts
  - Batch size B=1000 chains simultaneously
  - Measure latency percentiles (p50, p95, p99) for sequential vs parallelized verification

Recommended first cell to implement: Tier 2 adversarial injection at K=3 with h in {1, 2} and fabrication type "plausible but wrong". This is the cheapest test that directly probes the middle-hop localization weakness. 90 instances, CPU-only, < 3 min wall.

---

## Cross-Thread Synthesis

1. PP-11 BAND-LIFT (K=20 perfect at N=16384): The K-hop traversal itself is validated at K=20. The CURRENT gap is not traversal accuracy but verification accuracy at K >= 10. The ceil is the per-hop KF-1 compounding, not the K-hop engine.

2. HP-12 V1 audit cert (< 1ms RSA accumulator): Extending HP-12 V1 to a per-hop Merkle chain is the highest-value near-term engineering lift. It transforms "this answer was verified" into "this specific reasoning chain was verified, step by step, with per-step confidence scores" -- a qualitatively different audit capability.

3. KF-1 (AUC 0.999 easy / 0.975 hard): The hard-domain degradation (0.975) is the primary ceiling for production chains with K >= 5. Addressing the hard-domain KF-1 calibration is a prerequisite for K >= 10 production deployment.

4. Field adjacency -- mesoscopic-transport: The "K-hop cliff at d=25" (PP-11) maps to a transport problem in the field advisor's Tier-1b. Multi-hop hallucination verification may benefit from Landauer-Buttiker formalism analysis: model each hop as a transmission channel, and the chain AUC as a total transmission coefficient. This maps AUC degradation to a physics framework with known phase transition behavior.

---

## Substrate-Product Implications

1. MOAT: The per-hop localization capability (WHICH hop failed, not just whether the answer is wrong) is not available in any RAG system or frontier LLM. It is a categorical differentiator for KF-1 audit use cases. The HP-12 V1 per-hop Merkle extension makes this cryptographically verifiable -- a second-order moat.

2. PRODUCTION GATE: Before K >= 10 deployment, must validate:
  (a) Hard-domain KF-1 AUC -- is 0.975 sufficient at K=10?
  (b) Middle-hop localization accuracy -- does error propagation break localization?
  (c) Latency model -- parallelization or sequential-with-early-exit?

3. QUICKEST WIN: Confidence-weighted aggregation (C_min / C_chain) costs zero additional compute, adds meaningful adversarial robustness signal, and is a 1-day implementation. Ship this before adversarial benchmark validation.

4. ROADMAP ORDERING:
  Step 1 (1 day): Add confidence-weighted aggregation to existing fact_checked_khop
  Step 2 (1 day): Build per-hop Merkle hash chain + HP-12 V1 root composition
  Step 3 (2 days): Run Tier 2 adversarial injection benchmark to characterize middle-hop localization
  Step 4 (2 days): Implement backward chaining if Step 3 reveals HF-1 (localization accuracy < 0.65)
  Step 5 (1 day): Parallelize per-hop KF-1 calls; validate accuracy parity

---

## Citations (verified count: 12 primary)

1. Chain-of-Verification (CoVe) -- ResearchGate / ACL 2025: hallucination reduction via self-verification
2. Verifying Chain-of-Thought via Computational Graph -- arXiv 2510.09312
3. ConfSpec: Confidence-Gated Step-Level Verification -- arXiv 2602.18447
4. Early Stopping via Confidence Dynamics -- arXiv 2604.04930
5. Conformal Thinking: Risk Control on Compute Budget -- arXiv 2602.03814
6. Sequential quality control in batch manufacturing -- Springer Annals of Operations Research
7. Optimal inspection policies for manufacturing station -- ScienceDirect 1992
8. The Critical Horizon: Inspection Design for Multi-Stage Operations -- arXiv 2602.09394
9. StepChain GraphRAG: Multi-Hop Reasoning over KGs -- arXiv 2510.02827
10. Reasoning Chain Based Adversarial Attack for Multi-hop QA -- arXiv 2112.09658
11. PBFT + Raft combination (Springer Physics of Particles and Nuclei 2024)
12. Merkle tree verifiable data structures -- transparency.dev / Register Dynamics

---

## Experimental Cell Recipes (4-6 cells for empirical validation)

CELL-1: Middle-hop adversarial injection (cheapest decisive test)
  K in {3, 5}, injection at h=K//2, fabrication type "plausible but wrong"
  Metric: localization accuracy (flag at h vs flag at h+1..K)
  HP: >= 0.85 at K=3, MID: [0.65, 0.85), HF: < 0.65
  Cost: CPU, < 3 min, ~90 instances

CELL-2: Confidence-weighted aggregation AUC lift
  Add C_min and C_chain as features alongside binary flag
  Compare AUC on clean vs adversarial chains
  HP: C_min AUC >= 0.990 on adversarial; binary >= 0.985
  Cost: CPU, < 5 min, no new KF-1 calls

CELL-3: K-scaling latency model
  K in {5, 10, 20}, sequential vs parallelized (all K calls in one batch)
  Metric: latency (ms) + accuracy parity check (within 0.005 AUC)
  HP: parallelized latency = t_kf1 + overhead (vs K * t_kf1 sequential)
  Cost: CPU/GPU, < 10 min

CELL-4: Per-hop Merkle chain + HP-12 V1 composition
  Emit hash(hop_i || fact_i || score_i) at each hop; build Merkle tree; accumulate root in HP-12 V1
  Metric: end-to-end latency < 1ms overhead; tamper injection detected (hash mismatch)
  HP: latency overhead < 1ms at K <= 20; tamper detection 100%
  Cost: CPU, < 2 min

CELL-5: Backward chaining accuracy lift
  Run full backward pass after forward chain; combine forward + backward localization
  Metric: localization accuracy delta vs forward-only
  HP: >= +0.05 accuracy lift on middle-hop injection (CELL-1 regime)
  Cost: CPU, 2x CELL-1 compute (doubles KF-1 calls)

CELL-6: KB contradiction robustness
  Inject contradictory facts (A=X and A=not-X at different hops in the same chain)
  Metric: cross-hop consistency check detects contradiction; localization points to BOTH conflicting hops
  HP: detection rate >= 0.90 on injected contradictions; false positive rate < 0.10 on clean chains
  Cost: CPU, < 5 min

---

## Production Readiness Checklist

[ ] Validate hard-domain KF-1 AUC >= 0.95 for target KB domain (not just same-domain)
[ ] Run CELL-1 middle-hop localization test -- pass HP-1 before K >= 5 production deployment
[ ] Add confidence-weighted aggregation (C_min / C_chain) -- 1 day, zero compute overhead
[ ] Build per-hop Merkle chain + HP-12 V1 root (CELL-4) -- 1-2 days engineering
[ ] Profile latency at K=20 sequential; implement parallelization if p95 > 100ms
[ ] Characterize false positive rate on correct-but-unconventional reasoning paths (FM-5)
[ ] Define cross-domain deployment protocol (re-calibrate KF-1 or validate AUC on target domain KB)

---

P_deflated overall: 0.50 (novel synthesis; adversarial middle-hop brittleness claim has highest confidence; parallelization safety has moderate confidence; cross-domain AUC retention has lowest confidence)

Next-drill candidate: mesoscopic-transport (Landauer-Buttiker formalism for multi-hop AUC as transmission coefficient; field advisor Tier-1b; maps K-hop cliff directly to physics framework with known universality class)
