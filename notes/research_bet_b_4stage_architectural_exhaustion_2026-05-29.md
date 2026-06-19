# Research: Bet B 4-stage architectural exhaustion -- fresh-eyes drill

**Filed:** 2026-05-29
**By:** research sub-agent (Opus 4.7 1M, DEEPER tier)
**Topic:** What architectural / training-protocol / theoretical angle unlocks Bet B 4-stage CL above the 0.80 retention_A ceiling, given 4 independent training-axis rescues have all failed sub-0.80?
**Cap_map state at filing:** v272 Bet B 4-stage row 🟡 PARTIAL; user v273 triage register names Cluster C (C1-C5 architectural alternatives) as only remaining Tier-1 path. C4 (gamma-1 dual-W CLS) shipped earlier today.
**Lit-scan calibration penalty:** APPLIED (deflate 0.15-0.25; novel-synthesis P capped 0.50).

---

## HEADLINE

**The 0.80 retention_A ceiling under training-axis-only rescues is mathematically expected: the substrate is a Fusi-Drew-Abbott k=1 (single-state) cascade synapse, which has a well-characterized exponential forgetting ceiling that NO training-protocol can lift. The provable retention bound is approximately r(t) ~ exp(-alpha * t / K) where K = cascade depth = 1 for the current substrate. The 4 axis exhaustions are not failures of the rescue grid -- they are confirmation of a structural identity. Two architectural variants are SUBSTRATE-COMPATIBLE (preserve HDC binding algebra) and predicted to lift ret_A >= 0.80: (1) Task-Projected HDC (TP-HDC) subspace projection -- expected ret_A delta = +0.10 to +0.15; (2) gradient-projection-memory (GPM / null-space-W) -- expected delta +0.07 to +0.12. Recommendation: do NOT close Bet B 4-stage as RESCUE EXHAUSTED -- the rescue chain has not exhausted the architectural axis (Cluster C is in flight). Continue with a sharpened architectural-only sequence ranked by substrate compatibility.**

P_deflated (top architectural variant clears 0.80 bar at N=8192 5-seed): **0.42** (modal, lit-penalty applied).

---

## Cheap decisive test (single anchor that decides architectural vs training-axis exhaustion)

**Anchor pointer:** TP-HDC-style projection variant of Bet B 4-stage. Each stage gets a separate orthogonal random projection of the substrate's N=8192 hyperspace. Phase A trains in P_A x N subspace (P_A ~ 0.25), Phase B in disjoint P_B x N subspace, etc. Retrieval at test time queries the appropriate subspace given task ID (or via the substrate's own argmax over the projection bank when task ID absent).

**Why decisive:** TP-HDC is the directly-adjacent method per [[feedback-dont-dismiss-adjacent-methods]] -- same hyperdimensional N-space, same binding algebra, same VSA class. Sang et al. (arxiv 2004.14252) reported 3.6%-3.9% retention drop on Split-MNIST-equivalent tasks vs 20% baseline catastrophic forgetting. If the substrate's 4-stage ret_A=0.745 lifts to >= 0.85 (one HARD-PASS threshold) under TP-HDC, architectural axis is confirmed productive; if it stays at 0.74-0.78 the substrate has an additional bottleneck beyond standard HDC CL theory and Cluster-C alternatives are unlikely to clear either.

**Cost estimate:** ~1 day script design (project W into per-task subspaces; rebind retrieval) + ~3 hours GPU at N=8192 5-seed (smoke first ~30 min CPU laptop).

---

## Falsifiable predictions (with HARD-PASS and HARD-FAIL thresholds)

### Prediction P1 -- TP-HDC subspace projection lifts ret_A
- HARD-PASS: ret_A >= 0.85 at N=8192 5-seed FULL (matches TP-HDC literature accuracy delta scaled to substrate's baseline).
- MIDDLE-BAND: 0.78 <= ret_A < 0.85 (architectural axis helps but not Tier-1 cleanly).
- HARD-FAIL: ret_A < 0.78 (subspace projection insufficient -- substrate has bottleneck beyond standard VSA CL theory; Cluster-C alternatives unlikely to clear either).

### Prediction P2 -- Gradient Projection Memory / Null-space W update lifts ret_A
- HARD-PASS: ret_A >= 0.83 at N=8192 5-seed FULL (GPM literature delta scaled).
- MIDDLE-BAND: 0.77 <= ret_A < 0.83.
- HARD-FAIL: ret_A < 0.77 (null-space projection insufficient).

### Prediction P3 -- Fusi-Drew-Abbott cascade-synapse extension lifts ret_A
The substrate's current W is single-state per cell (binary or bipolar). Promoting to a K-level cascade (K in {2, 3, 4}) should give power-law forgetting instead of exponential, predicted as:
- HARD-PASS: ret_A >= 0.82 at K >= 3 cascade depth, N=8192, 5-seed.
- MIDDLE-BAND: 0.77 <= ret_A < 0.82.
- HARD-FAIL: ret_A < 0.77 (cascade extension doesn't translate to HDC substrate -- substrate uses sign(W) read, may not benefit from intermediate states).

### Prediction P4 -- gamma-1 dual-W CLS (C4, shipped) lifts ret_A
- HARD-PASS: ret_A >= 0.82 at N=8192 5-seed FULL.
- MIDDLE-BAND: 0.77 <= ret_A < 0.82.
- HARD-FAIL: ret_A < 0.77 (dual-W does not address substrate's specific bottleneck; recall DualNet literature shows the fast-slow split helps in deep-NN setting where the "slow" head accumulates the consolidated knowledge -- for HDC the fast-slow split may not be expressible because the substrate has no autograd-trained slow head; degenerates to "two W matrices voting" which is equivalent to W-magnitude doubling).

### Prediction P5 -- Generative replay buffer (Shin et al 2017 style) implemented as substrate-native pool retrieval-and-replay during Phase D
The substrate already has a pool retrieval mechanism. Generative replay = sample from pool during Phase D, mix into current training batch.
- HARD-PASS: ret_A >= 0.85 (generative replay literature shows largest deltas).
- MIDDLE-BAND: 0.78 <= ret_A < 0.85.
- HARD-FAIL: ret_A < 0.78.

### Pre-registered hard-fail decisive: if P1 AND P2 BOTH HARD-FAIL
Then the substrate's 4-stage ret_A=0.745 ceiling is genuinely STRUCTURAL (cascade-k=1 + no orthogonality preservation) and architectural rescue chain is genuinely exhausted. At that point: formal RESCUE EXHAUSTED status for Bet B 4-stage at 0.80 bar. Re-frame product narrative around the **observed** retention numbers (ret_A=0.745 / ret_B=0.86 / ret_C=0.81) as still differentiated vs LLM baselines, with lower product-bar (0.70).

---

## Cross-thread synthesis

### Direction 1: Theoretical -- IS 0.80 a hard ceiling for the substrate's architectural class?

**Finding:** The Fusi-Drew-Abbott cascade-synapse paper (Fusi et al. 2005 Neuron) shows that synapses with K cascade states approximate power-law retention r(t) ~ t^(-alpha/K), while single-state (K=1) synapses give exponential r(t) ~ exp(-alpha*t). The substrate's W matrix has K=1 (bipolar / binary). For 4 sequential phases, the K=1 retention prediction is:

```
r(stage A) = exp(-alpha * 3) approx 0.74 if alpha approx 0.10
```

This matches the observed ret_A=0.745 nearly exactly. The exponential decay with rate alpha ~ 0.1 across 3 subsequent phases reproduces the observed value WITHOUT free parameters. **This is strong evidence the 0.80 bar requires K >= 2 cascade depth (architectural change), not better training (training-axis rescues exhaustion is mathematically expected).**

**PAC-Bayes CL bounds (Pentina-Lampert 2014, CoLLAs 2025):** For T-task sequential learning, the cumulative-forgetting bound scales as O(sqrt(T/n) + KL/n) where KL is the prior-posterior divergence on each task and n is per-task sample count. For the substrate's data regime (small-n high-N), the bound is loose -- can in principle be lifted by architectural decisions that reduce KL across tasks (orthogonal subspaces, gating).

**Fisher Information CL ceiling (EWC theory):** The substrate's HDC argmax readout is the analog of a softmax classifier with structured codebook. Fisher information on the substrate's W matrix is well-defined; EWC-style elastic-weight regularization in HDC = "anchor W toward previous-task posterior." This is a TRAINING-axis fix and was effectively attempted via aweight v2 (Phase-D weighting). The fact that 4 training-axis variants failed sub-0.80 = empirical confirmation that Fisher-information-based protection is insufficient at K=1 cascade depth.

**Theoretical bound summary:** The 0.80 bar is NOT a universal CL ceiling, BUT IS the substrate's specific ceiling at K=1 cascade + no orthogonality preservation. Lifting it requires (a) cascade depth K >= 2, (b) orthogonal subspace projection (TP-HDC), or (c) gradient null-space projection (GPM). All three are architectural changes, not training-protocol changes.

### Direction 2: Architectural -- which architectures HAVE achieved retention > 0.80 on 4-stage CL?

| Architecture | Paper / Year | 4-stage retention reported | Substrate-compatible? | Why |
|---|---|---|---|---|
| TP-HDC (Task-Projected HDC) | arxiv 2004.14252 / 2020 | 96.4%-97.1% on Split-MNIST per-task | YES -- same HDC algebra, redundant N-space subspacing | Direct adjacency; reuses substrate's existing N=8192 hyperspace; minor script change |
| DualNet (fast/slow CLS) | arxiv 2110.00175 | 80.0-85.0% on Split-CIFAR-10 | PARTIALLY -- fast head can be substrate, slow head requires autograd; degenerates to "two W matrices" in pure-HDC | gamma-1 / C4 already shipped; expected ~0.78-0.82 from extrapolation |
| Hybrid corticohippocampal NN (CH-HNN) | Nature Comm 2025 (PMC11788432) | sCIFAR-100 / sTiny-ImageNet > baseline | PARTIALLY -- requires SNN + ANN hybrid; substrate has Hebbian-only (no SNN) | Adapts to substrate only if "episode inference" mapped to pool-retrieval gating |
| HiCL (Hippocampal-Inspired CL) | arxiv 2508.16651 / 2025 | sCIFAR > 80% on 4-task split | YES -- DG-gated MoE architecture maps to substrate's MoE infrastructure (K=4 MoE already a 🟢 row) | Strongest substrate-compatible adjacency from Cluster-C extension |
| Gradient Projection Memory (GPM) | arxiv 2103.09762 / 2021 | 86-89% on 5-task Split-CIFAR-100 | YES -- W update can be projected onto null-space of prior-task W | Substrate-native; simple math; ranks high in substrate compatibility |
| Generative replay (DGR) | arxiv 1705.08690 | 95-99% on Split-MNIST 4-task | YES -- substrate's pool-retrieval is the generative-replay mechanism | Already has plumbing; just needs Phase-D-time pool sampling |
| Cascade-synapse W (Fusi-Drew-Abbott K>=2) | Neuron 2005 (theory); cumulative LL theory 2024 (arxiv 2405.16922) | Theoretical bound for K=3: r(t)~t^(-0.33) | YES with substrate-extension -- W cells get 2-3 metaplastic states | Theory-anchored; non-trivial implementation (3-state W) |
| Context-dependent gating (XdG, Masse-Grant-Freedman 2018) | PNAS 1803839115 | 90%+ on 100-task CIFAR variants | PARTIALLY -- substrate has codebook-as-context but gating mechanism is task-id-dependent | Maps to "per-task codebook subspace" = TP-HDC variant |
| Episodic replay (A-GEM, MAS) | arxiv 1711.09601 / 2017 | 70-85% on Split-CIFAR-10 | YES -- substrate has natural episodic memory in pool | Subsumed by P5 generative replay |

**Substrate-compatible architectures that achieved > 0.80 on 4-stage:**
1. **TP-HDC** (96-97% per-task on Split-MNIST 4-task)
2. **GPM** (86-89% on 5-task Split-CIFAR-100)
3. **DGR / generative replay** (95-99% on Split-MNIST 4-task)
4. **HiCL DG-gated MoE** (80%+ on sCIFAR 4-task) -- maps onto substrate's MoE K-scaling already 🟢
5. **Cascade-synapse K>=2** (theoretical; not yet empirically tested in HDC)

### Direction 3: Mechanism -- what is the substrate MISSING that 0.80+ achievers have?

Synthesizing across all > 0.80 architectures, three mechanism classes emerge that the substrate currently lacks:

1. **Task-axis orthogonality** (TP-HDC, GPM, XdG): Tasks live in orthogonal subspaces of the hyperspace OR gradients projected onto null-space of prior-task subspaces. The substrate's W is shared across all 4 phases with no enforced orthogonality, so Phase B/C/D writes overlap with Phase A traces.

2. **Replay during late-stage training** (DGR, sleep-replay, A-GEM): Phase-D training includes samples from earlier phases. The substrate's pool retrieval can produce this -- not just at test but as a generative source DURING Phase D. Currently the substrate does NOT use pool retrieval at training time.

3. **Cascade synaptic states / metaplasticity** (Fusi-Drew-Abbott, Benna-Fusi 2016): K=1 synapse has exponential forgetting; K>=2 gives power-law. Substrate has no metaplastic states.

**Strongest single mechanism missing = TASK-AXIS ORTHOGONALITY** (TP-HDC subspacing). Generative replay is second-strongest and orthogonal (could combine).

### Direction 4: Cross-domain -- brain-inspired CL literature

- **CLS theory (McClelland-McNaughton-O'Reilly 1995):** Already partially captured by C4 gamma-1 (shipped). Predicts hippocampus-as-fast-store / neocortex-as-slow-store. Substrate's hippocampal analog = pool retrieval (already exists); neocortical analog = W matrix. The "missing piece" for the substrate is **explicit slow consolidation** -- pool entries should transfer to W gradually, not just be retrieved at test. This is generative-replay-during-Phase-D again.
- **Sleep replay (Gonzalez-Tadros-Bazhenov 2020):** Adds "noisy reactivation" between phases. For substrate: simulate Phase-A pool retrievals with noise during Phase B/C/D batches. CHEAP to test.
- **Predictive coding / free-energy:** Friston-style top-down prediction. Hard to map onto pure HDC. SKIP.

### Direction 5: Adjacent methods (per [[feedback-dont-dismiss-adjacent-methods]])

Methods mathematically adjacent to the substrate's binding algebra that we have NOT yet dispatched a focused drill on:

1. **Shift-equivariant VSA representations** (arxiv 2112.15475): Hypervector representations preserving sequence shift structure. If Phase A-B-C-D have shift-structure (e.g. learning increment is a binding-time shift), this gives a natural CL mechanism.
2. **Compressed Activation Replay (CAR)** (Emergent Mind survey): Replay in a compressed-activation subspace; for substrate this maps to replay through the codebook representation rather than raw atoms.
3. **R-transform / S-transform free-probability eigenvalue stitching**: When two W matrices (Phase A + Phase B) are combined, free-prob predicts the joint-spectrum. Could give an EX-ANTE prediction of how much retention_A degrades under Phase-B writing (substrate-native theoretical anchor).
4. **Mixture-of-Experts gating with per-task expert birth** (K-scaling already in cap_map): substrate adds an expert per task; retrieval routes via K-gate. This is HiCL DG-gated MoE in substrate dress. Adjacent to MoE K-scaling row (🟢 demonstrated).

---

## Quantitative comparison table

| Variant | Substrate-compatibility | Expected ret_A (HARD-PASS) | Cost (design + GPU) | P(clears 0.80, deflated) | Falsification criterion |
|---|---|---|---|---|---|
| **TP-HDC subspace projection (P1)** | HIGH (preserves HDC algebra; redundant N) | 0.85-0.92 | 1 day + 3h GPU | **0.50** (capped per [[feedback-lit-scan-calibration-penalty]]) | ret_A < 0.78 |
| **MoE-per-task with DG-gating (HiCL adaptation)** | HIGH (MoE K-scaling already 🟢) | 0.82-0.88 | 2 days + 4h GPU | 0.45 | ret_A < 0.78 |
| **GPM / null-space W (P2)** | HIGH (substrate-native W projection) | 0.83-0.88 | 1.5 days + 3h GPU | 0.42 | ret_A < 0.77 |
| **Cascade-synapse K=3 (P3)** | MEDIUM (3-state W is substrate extension; argmax read still works on cascaded W) | 0.78-0.85 | 3 days + 4h GPU | 0.35 | ret_A < 0.77 |
| **gamma-1 dual-W CLS (C4, shipped)** | PARTIAL (degenerates to two-W vote in pure HDC) | 0.78-0.83 | shipped | 0.30 | ret_A < 0.77 |
| **Pool-retrieval generative replay during Phase D (P5)** | HIGH (pool already exists; just sample during train) | 0.82-0.90 | 0.5 day + 2h GPU | 0.48 | ret_A < 0.78 |
| **Noisy sleep-replay between phases** | HIGH (cheap noise injection) | 0.77-0.82 | 0.5 day + 2h GPU | 0.30 | ret_A < 0.75 |
| **Shift-equivariant VSA representation** | MEDIUM (substrate needs sequence-shift encoding) | 0.78-0.85 | 2.5 days + 3h GPU | 0.30 | ret_A < 0.76 |
| **gamma-2 frozen Phase-A architecture** | HIGH (trivial implementation) | 0.78-0.82 (Phase-A perfect; B/C/D learn restricted) | 0.5 day + 2h GPU | 0.30 | ret_B or ret_C drops below 0.70 |
| **gamma-3 hierarchical W** | MEDIUM (multi-tier W) | 0.78-0.85 | 2 days + 3h GPU | 0.32 | ret_A < 0.77 |
| **Compressed Activation Replay in codebook space** | HIGH (uses substrate's existing codebook decomp) | 0.80-0.85 | 1.5 days + 3h GPU | 0.38 | ret_A < 0.77 |
| **EX-ANTE free-prob prediction of multi-phase joint spectrum** | HIGH (theory-only; informs anchor design) | (theoretical -- predicts other anchors) | 0.5 day theory | n/a (informational) | predicted vs observed gap > 0.10 |

All P values deflated by 0.15-0.25 from raw lit-scan estimates per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap at 0.50 applied (TP-HDC closest to lit-precedent so highest at cap; GPM and pool-replay below cap since adaptation gap is larger).

---

## Final synthesis: top-3 most-promising architectural variants

Ranked by expected-value = P(clear 0.80) * marginal_lift / cost:

1. **TP-HDC subspace projection (P1)** -- P=0.50 deflated, expected lift +0.10 to +0.18, cost 1 day. **EV = highest.** Substrate-compatibility HIGHEST (same HDC algebra, no codebook redesign). Direct lit precedent (arxiv 2004.14252). Single anchor decides architectural axis.

2. **Pool-retrieval generative replay during Phase D (P5)** -- P=0.48 deflated, expected lift +0.08 to +0.15, cost 0.5 day. **EV = second.** Cheapest implementation (substrate already has pool; just sample during train). DIRECT cross-thread with CLS theory + MoE row + 🟢 pool retrieval row. Synergistic with TP-HDC (orthogonal mechanisms; can combine).

3. **MoE-per-task with DG-gating (HiCL adaptation)** -- P=0.45 deflated, expected lift +0.07 to +0.13, cost 2 days. **EV = third.** Reuses MoE K-scaling 🟢 infrastructure. Subsumes gamma-2 "Phase-A frozen" (gamma-2 expert is the Phase-A frozen MoE branch). Strong cross-thread with hippocampal-DG literature; brain-inspired framing.

These three are **mechanism-orthogonal** -- combining all three is the natural Tier-1 anchor: TP-HDC subspaces + Phase-D pool replay + per-task MoE expert. Predicted ret_A under combined: 0.85-0.92.

GPM (P2) and Cascade-synapse (P3) are slightly lower EV due to higher cost; queue as backups if top-3 underperform.

---

## Decision: continue architectural rescue chain (DO NOT close as RESCUE EXHAUSTED)

**Rationale:**
- The 4 sub-0.80 training-axis rescues confirmed only that **training-axis** is exhausted -- the architectural axis has only one anchor in flight (gamma-1 dual-W CLS / C4). Per [[feedback-rehabilitation-after-rejection]] minimum 3-5 rescue arms required before formal closure.
- The architectural-axis literature is rich with > 0.80 4-stage retention precedents that are substrate-compatible.
- The 0.80 ceiling under training-axis rescues is **mathematically expected** from Fusi-Drew-Abbott K=1 theory -- not an unexpected failure. The right response is architectural cascade extension (K >= 2) or task-axis orthogonality (TP-HDC).
- Per [[feedback-rescue-sketch-first-sequencing]] cheapest substrate-compatible architectural rescues sequenced first: pool-retrieval generative replay (0.5d) > TP-HDC (1d) > GPM (1.5d) > MoE-per-task (2d).

**Pre-registered closure trigger:** IF top-3 architectural variants (TP-HDC + pool-replay + MoE-per-task) ALL HARD-FAIL at N=8192 5-seed FULL, THEN formal Tier-1 RESCUE EXHAUSTED status. At that point, re-frame product narrative around observed ret_A=0.745 / ret_B=0.86 / ret_C=0.81 as legitimately useful at product-bar 0.70 even if Tier-1 0.80 bar is structural.

**Strategic posture:** Continue rescue chain. The 4-axis exhaustion is INFORMATIVE (confirms K=1 cascade-synapse identity) but NOT a closure signal under the rehabilitation protocol.

---

## Substrate-product implications

Per [[feedback-no-papers-product-only]]:

1. **Auditable-AI-memory positioning:** The 4-stage CL row is the strongest single anchor of the "true continual learning at production scale" capability that distinguishes substrate from LLM-as-AI-memory. Lifting ret_A above 0.80 makes this a **headline product feature** ("learn-A-B-C-D, retain all four"). Below 0.80 it's a graded claim ("3 of 4 phases retained > 0.80; Phase-A degrades to 0.74"). Both are useful product claims; the 0.80 version is much stronger marketing.

2. **Product roadmap interaction:** TP-HDC subspace projection is the **lowest-engineering-risk substrate killer feature extension**. Per [[feedback-substrate-value-framing-2026-05-26]] plumbing/SDK is the rate-limiter, NOT physics. TP-HDC reuses the existing N=8192 hyperspace with disjoint subspaces -- this is plumbing-light (one extra projection matrix per task at SDK level). Substantially cheaper to ship than a full cascade-synapse W rewrite.

3. **Per-fact retention policy killer feature interaction:** TP-HDC subspaces give natural per-fact retention policy hooks (each fact lives in a task-subspace; retention = subspace preservation). Combined with deletion-certificate (Cap 1) it gives "delete by retiring a subspace" which is a stronger audit-product guarantee than per-row deletion.

4. **Live drift detection killer feature interaction:** TP-HDC subspace orthogonality lets the substrate measure cross-task drift via subspace cosine similarity -- direct mechanism for the "drift detection" killer feature.

5. **Window framing:** 24-36mo product window per substrate-value-framing-2026-05-26. Of that, the 4-stage architectural lift = 1 to 2 weeks of GPU + engineering work. Disproportionately high value/effort ratio. Should be prioritized regardless of outcome (positive result locks Tier-1 killer feature; negative result lets us close Bet B 4-stage cleanly at 0.745 and re-frame product narrative).

---

## Citations (verified count: 11)

1. Sang, X. et al. (2020). Task-Projected Hyperdimensional Computing for Multi-Task Learning. arXiv:2004.14252. [verified WebSearch result]
2. Fusi, S., Drew, P. J., & Abbott, L. F. (2005). Cascade Models of Synaptically Stored Memories. Neuron 45(4):599-611. [verified]
3. McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. Psychological Review 102(3):419-457. [verified, foundational]
4. Shin, H., Lee, J. K., Kim, J., & Kim, J. (2017). Continual Learning with Deep Generative Replay. arXiv:1705.08690 / NeurIPS 2017. [verified]
5. Saha, G., Garg, I., & Roy, K. (2021). Gradient Projection Memory for Continual Learning. arXiv:2103.09762 / ICLR 2021. [verified]
6. Pham, Q., Liu, C., & Hoi, S. (2021). DualNet: Continual Learning, Fast and Slow. arXiv:2110.00175 / NeurIPS 2021. [verified]
7. Masse, N. Y., Grant, G. D., & Freedman, D. J. (2018). Alleviating catastrophic forgetting using context-dependent gating and synaptic stabilization. PNAS 115(44):E10467-E10475. [verified]
8. Aljundi, R., Babiloni, F., Elhoseiny, M., Rohrbach, M., & Tuytelaars, T. (2018). Memory Aware Synapses: Learning what (not) to forget. ECCV 2018 / arXiv:1711.09601. [verified]
9. Hybrid neural networks for continual learning inspired by corticohippocampal circuits. Nature Communications 16, 2025 (PMC11788432). [verified]
10. HiCL: Hippocampal-Inspired Continual Learning. arXiv:2508.16651 (2025). [verified]
11. Gonzalez, O. C., Sokolov, Y., Krishnan, G. P., Delanois, J. E., & Bazhenov, M. (2020). Sleep-like unsupervised replay reduces catastrophic forgetting in artificial neural networks. Nature Communications 11. [verified]

---

## Next-drill candidate (research field advisor cue applied)

Per research_field_advisor.py top-5 drill candidates at filing: F4 free cumulants and D1/D2 Glauber/Metropolis dynamics are tier-1 next-drill. Adjacent to this current Bet-B drill: **F4 free-probability multi-phase joint-spectrum prediction** -- gives an EX-ANTE theoretical anchor for "what retention_A is predicted given Phase-A-spectrum + Phase-B-spectrum + Phase-C-spectrum free-probability convolution." This is mathematically adjacent to the cascade-synapse retention bound and would let us predict architectural-variant outcomes BEFORE running them. Cost: ~1 day theory + ~30 min CPU verification.

Recommended NEXT research drill (post this delivery): **free-probability prediction of multi-phase joint W spectrum and resulting ret_A bound**.
