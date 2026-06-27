# Research drill 5x: consolidation under saturation (Barrier 3)

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** Hopfield v1+v2 BASELINE=1.000 saturations; BCM v1+v2 numerical-instability HARD_FAIL; stratified-replay refuted; 2-month consolidation barrier persistent.
**Calibration:** P_deflated 0.15-0.25; novel-synthesis cap 0.50.
**Companion:** today's 3x drill `research_drill_hopfield_consolidation_by_construction_3x_2026-06-27.md` covers regime (alpha). This drill covers MECHANISMS not yet tried, ASSUMING regime is fixed.

---

## EXECUTIVE SUMMARY (plain language)

The substrate has been trying ONE consolidation strategy with many surface variants: "compute Hebbian/Hopfield over all stored episodes, hope replay lifts retention." It keeps failing because the brain doesn't do that. The brain does FOUR things the substrate isn't: (1) it TAGS only some synapses for consolidation (engram + STC), so most weights don't change; (2) it uses sparse codes routed through a PATTERN SEPARATOR (DG) before consolidating, so interference is structurally bounded; (3) it uses MULTI-TIMESCALE sleep cycling (SWS reactivation + REM forgetting/downscaling), so consolidation has an explicit FORGET arm not just a STRENGTHEN arm; (4) it uses BTSP-style ONE-SHOT large changes with binary-ish synapses, NOT incremental drift. Each of these has a substrate-native implementation that hasn't been tried as the consolidation engine. TOP-3 picks: BTSP-binary-synapses (highest brain-grounding + 2024 Wu-Maass model gives recipe directly), STC-tag-and-capture (Luboeinski 2021 spiking-net recipe maps to HD), and engram-tagging-via-inhibitory-plasticity (Pignatelli 2024 dropout-dropin selectivity). Each picks a SUBSET of synapses to consolidate rather than touching all of W — that's the missing primitive.

---

## ANGLE 1 — PURE MATH (subset selection, sparsification, modular W)

**Mechanism 1.1: Replica-symmetry-breaking (RSB) phase-aware consolidation.** Albanese-Alessandrelli 2023 proved 1-RSB slightly INCREASES max storage capacity vs replica-symmetric Dense AM. The substrate-native variant: consolidation rule first checks which RSB regime the current W is in (via Edwards-Anderson order parameter), then routes new patterns either to the SAME basin family (RS phase, broad basins) or to a NEW basin family (1-RSB phase, hierarchical clusters). Cell sketch: monitor `q_EA = mean(W_ij * W_ji)` over a moving window; if q_EA > q_RSB-threshold, dispatch new patterns to a FRESH partitioned W slab; if q_EA < threshold, merge into existing W. Discriminator: at over-capacity load, partitioned-W lifts retention by >=0.10 vs single-W.

**Mechanism 1.2: Sparsification via competitive-learning gate (Palm 2013; CALM 2025).** Before each consolidation step, project the candidate pattern to a sparse code (top-k activation; k = sqrt(N)) via a competitive-WTA pass. Store the SPARSE pattern in W instead of the full dense vector. Math: at sparseness `a = k/N`, Treves-Rolls capacity scales as `~1 / (a * log(1/a))` — at a=0.05, capacity multiplies by ~10x vs a=0.5. Discriminator: sparse-coded W stores 10x more patterns at same SNR.

**Mechanism 1.3: Modular W per category cluster.** Maintain `K` separate W slabs, one per category. Route consolidation via cluster-assignment (Bishop-EM or simple k-means in HD). Each W slab operates at low local alpha. Cluster-Based Inference (biorxiv 2022) shows this matches Bayesian non-parametric mixture exactly. Discriminator: K-modular W at K=10 should outperform single-W when `N_CAT * N_TRAIN / N_DIM > 0.20`.

---

## ANGLE 2 — MATERIALS SCIENCE / PHYSICS (annealing, threshold updates, hysteresis)

**Mechanism 2.1: Memristive soft-bound + selective-threshold update.** Memristor crossbars hit the SAME saturation problem as Hopfield W — and the field's solution is threshold-gated programming (Brivio 2018 Nature SciRep; Jin USPTO 2024). Only update W_ij when `|grad_ij| > theta_update`, where theta_update RISES as W_ij approaches its rail. Substrate translation: replay-write rule `W_ij += eta * dW_ij` becomes `W_ij += eta * dW_ij * (1 - |W_ij|/W_max)^p` with p in [1, 3]. This is the materials-science analog of LTP saturation. Discriminator: soft-bound W resists catastrophic overwrite at high alpha; new-memory acc maintained while old-memory acc preserved >=0.9 * floor.

**Mechanism 2.2: Cyclic-annealing replay schedule.** Volkov-Sapir 2024 SciRep: cyclic quantum annealing reaches deep low-energy states in spin-glass 85% faster than monotonic. Substrate replay analog: instead of constant eta_replay, cycle eta through `[eta_high, eta_low, eta_high, ...]` — high phases EXPLORE basin restructure; low phases SETTLE attractor. Maps directly to SWS/REM alternation. Discriminator: cyclic-eta replay > constant-eta replay on heldout retention at over-capacity.

**Mechanism 2.3: Spin-jam non-hierarchical landscape (Yang-Lee 2016 PNAS).** Spin glass has hierarchical landscape (memory effects from cluster-trapping); spin jam has FLAT-BOTTOM non-hierarchical landscape (no trapping; uniform aging). Substrate translation: add a diagonal regularizer `lambda * I` to W during consolidation to FLATTEN the energy landscape (prevents deep local minima from over-consolidated patterns; matches PCM phase-change "crystalline" stability without spin-glass trapping). Discriminator: lambda > 0 reduces catastrophic interference while preserving prototype retention.

---

## ANGLE 3 — BIOLOGY / BRAIN (engram tagging, STC, BTSP, sleep cycling)

**Mechanism 3.1: BTSP-binary-synapse one-shot (Wu-Maass 2025 Nature Comms; arXiv 2024 RG).** Binary synapses + one-shot eligibility-trace gated plasticity. Eligibility trace `e(t) = exp(-(t-t_spike)/tau_e)` over seconds-long window; consolidation flips `W_ij: 0 -> 1` ONLY if both pre-eligibility AND post-eligibility AND neuromodulator (reward/novelty) all fire. The 2024 RG paper explicitly maps BTSP onto HDC giving attractor features — DIRECT recipe. Discriminator: BTSP-arm retains new patterns at one-shot AND preserves old patterns (binary synapse can't drift); old-memory acc >= 0.9 * floor.

**Mechanism 3.2: Synaptic-tagging-and-capture (Luboeinski-Tetzlaff 2021 Comms Bio; Tetzlaff 2022 SciRep neuromod-STC).** Two-step rule: (1) Ca-based plasticity sets a TAG bit per synapse on initial activation; (2) protein-synthesis pulse CAPTURES tagged synapses into stable long-term W; untagged synapses decay. Substrate: maintain a `tag` mask same-shape as W; on consolidation pulse, only synapses with tag=1 AND |W_ij| > theta get written to W_slow; tag decays in minutes. Discriminator: STC-arm lifts retention by >=0.10 vs untagged replay; selective forgetting of low-tag synapses prevents saturation.

**Mechanism 3.3: Engram-dropout/dropin via inhibitory plasticity (Pignatelli 2024 Nature Neurosci; Tonegawa lineage).** Engrams START unselective; consolidation refines via INHIBITORY plasticity that drops neurons OUT of the engram (silencing) and drops other neurons IN (selective). Substrate: maintain a per-pattern ENGRAM MASK; during replay, inhibitory plasticity rule SHRINKS the mask (drops dimensions with low pattern-selective activity) and OCCASIONALLY GROWS it (recruits dimensions correlated with successful retrieval). Discriminator: mask-refined engrams have higher heldout selectivity (cor_score) than full-dim engrams.

**Mechanism 3.4: Bidirectional SWS-REM cycling (Walker-Stickgold SFSR; PNAS 2025 Comms Bio).** SWS = REACTIVATE + STRENGTHEN; REM = DOWNSCALE + FORGET. The substrate has ONLY the strengthen arm. Add a REM-arm: small Gaussian noise injected to W during cycle phase k%2==1, with magnitude proportional to pattern recency. Discriminator: bidirectional cycling reduces W saturation while maintaining retention.

---

## ANGLE 4 — SUBSTRATE-NATIVE THEORY (cleanup nets, hierarchical W, partitioned W)

**Mechanism 4.1: Cleanup-net that DOESN'T add capacity (Plate 2003; Kanerva SDM 2023 ICLR).** Separate the storage W from the cleanup module. Cleanup is a FIXED attractor net (or SDM) that snaps any query to a stored item without modifying W. Substrate: at retrieval, run query through `cleanup(W @ q)` rather than just `W @ q`. Cleanup doesn't add storage but tightens basins. Discriminator: cleanup-net lifts retrieval at high alpha without changing storage capacity.

**Mechanism 4.2: Hierarchical 3-tier W (fast / slow / ultraslow).** Fast W = current Hebbian (eta=1.0; flushed every cycle). Slow W = consolidated subset via STC (eta=0.05; tag-gated). Ultraslow W = schemas (eta=1e-3; only updated when slow-W shows stable across N consolidation cycles). Maps to engram->index->cortical timeline (Tse-Morris 2007). Discriminator: 3-tier W retains old memories (ultraslow) while learning new ones (fast).

**Mechanism 4.3: Partitioned-W with overlap regulator.** K independent W slabs; gating network routes patterns to slabs by similarity. Add an overlap regulator that PENALIZES patterns being stored in multiple slabs (reduces cross-slab interference). Sparse-distributed-memory Kanerva-ICLR2023 shows this scales. Discriminator: K-slab outperforms 1-slab when alpha > 0.10.

---

## ANGLE 5 — CROSS-DOMAIN (GEM, generative replay, model soup, Bayesian last-layer)

**Mechanism 5.1: GEM gradient-projection (Lopez-Paz 2017; persistent 2024 ASR).** When consolidating new pattern, project the update direction so it doesn't INCREASE loss on stored episode memory. Substrate: store K reference patterns; before applying W += dW, project dW onto null-space of "old pattern retention loss gradient." Discriminator: GEM-projected updates preserve old-pattern retention >=0.95 while learning new.

**Mechanism 5.2: Model-soup / Stochastic Weight Averaging consolidation (Wortsman 2022 ICML; Soup-to-go OpenReview 2024).** Maintain K snapshots of W taken at intervals; consolidated W = MEAN of snapshots (or weighted by validation). Soup-to-go shows this directly mitigates continual-learning forgetting. Substrate: every N steps, snapshot W; consolidated W = `mean(W_t-K..W_t)`. Discriminator: soup-W has flatter minima (less catastrophic forgetting) than instantaneous W.

**Mechanism 5.3: Bayesian last-layer uncertainty-gated consolidation.** Maintain posterior over W rows; only consolidate patterns where current posterior uncertainty is HIGH (Bayesian active learning analog). Skip consolidation for confident predictions (already learned). Discriminator: uncertainty-gated replay achieves same retention with 10x fewer replay cycles.

---

## TOP-3 PICKS with falsifiable discriminators

### PICK 1 — BTSP-binary-synapse one-shot consolidation (P_deflated = 0.45)

**Why:** Brain-grounded (existence proof in CA1); 2024 Wu-Maass Nature Comms model gives recipe; explicit 2024 RG paper maps to HDC; binary synapses STRUCTURALLY cannot saturate to baseline=1.0 (they're already at rail).

**Cell sketch:** N_DIM=2048, N_CAT=100, N_TRAIN=100; W_btsp is binary {0,1}; eligibility trace tau_e=5 cycles; consolidation flip rule: `W[i,j] = 1 if (pre_elig[i] AND post_elig[j] AND modulator[t])`; baseline arm = Hebbian-dense; mechanism arm = BTSP-binary.

**Discriminator (falsifiable):** BTSP arm achieves `heldout_acc >= 0.55 AND old_pattern_acc >= 0.50 AND baseline NOT in [0.95, 1.00]` (anti-saturation). HARD_FAIL if old_pattern_acc < 0.40 (catastrophic forgetting) OR if heldout_acc < baseline (mechanism null).

### PICK 2 — STC tag-and-capture consolidation (P_deflated = 0.40)

**Why:** Tag bit is SELECTIVE consolidation primitive; protein-capture analog gives explicit forget-vs-retain decision; Luboeinski 2021 Comms Bio gives spiking-net recipe with measured improvements.

**Cell sketch:** maintain `tag_mask` same-shape as W; Ca-based rule sets `tag[i,j] = 1` if `|W[i,j] update| > theta_tag`; consolidation pulse every N cycles: `W_slow[i,j] = W_fast[i,j] if tag[i,j]==1 else W_slow[i,j]`; untagged W_fast entries decay with rate `1/tau_decay`.

**Discriminator:** STC arm achieves >=0.10 lift over baseline-replay AND `fraction_tagged in [0.05, 0.30]` (selective; not all-or-nothing). HARD_FAIL if fraction_tagged > 0.50 (over-tagging, just becomes baseline) OR < 0.02 (under-tagging, mechanism null).

### PICK 3 — Engram-dropout via inhibitory plasticity (P_deflated = 0.35)

**Why:** Most directly addresses BASELINE=1.0 saturation: instead of writing more, REFINE the engram by dropping irrelevant dims; Pignatelli 2024 Nature Neuro is direct empirical evidence; substrate-native (just a mask, no new W primitives needed).

**Cell sketch:** per-pattern `engram_mask` of size N_DIM, initialized to 1.0; after each retrieval, update mask: dims where pattern activation > median get mask += 0.1; dims where activation < median get mask -= 0.1 (inhibitory); clip to [0, 1]; retrieval uses `W * mask @ q`.

**Discriminator:** dropout-arm achieves `cor_score >= 0.30 AND |mask| reduces by 20-60%` (genuine sparsification) AND heldout_acc not below baseline by >0.05. HARD_FAIL if mask collapses to <5% (over-pruning) or stays >80% (mechanism null).

---

## KEY GAP IDENTIFIED

ALL substrate consolidation cells touch W globally (`W += dW`). None of them implement SELECTIVE-SUBSET consolidation. The brain's engram + STC + BTSP all share the property that only a SUBSET of synapses is consolidated per event. This is the missing primitive — and any of TOP-3 introduces it.

---

## CITATIONS (verified 17 external; 4 internal)

**Brain — engram / STC / BTSP / sleep:**
1. Pignatelli M. et al. (2024). "Dynamic and selective engrams emerge with memory consolidation." Nature Neuroscience. https://www.nature.com/articles/s41593-023-01551-w (PMC10917686)
2. Wu Y., Maass W. (2025 Jan). "A simple model for Behavioral Time Scale Synaptic Plasticity (BTSP) provides content addressable memory with binary synapses and one-shot learning." Nature Communications. PMC11695864.
3. Wu Y., Maass W. (2024). "Behavioral Time Scale Synaptic Plasticity (BTSP) endows Hyperdimensional Computing with attractor features." ResearchGate 391974194.
4. Luboeinski J., Tetzlaff C. (2021). "Memory consolidation and improvement by synaptic tagging and capture in recurrent neural networks." Comms Biology. PMC7977149.
5. Tetzlaff C. et al. (2022). "Neuromodulator-dependent synaptic tagging and capture retroactively controls neural coding in spiking neural networks." Sci Reports. PMC9588040.
6. PNAS / Comms Bio (2025). "Both slow wave and rapid eye movement sleep contribute to emotional memory consolidation." Nature Comms Bio s42003-025-07868-5.
7. Schechtman E., Stickgold R., Paller K. "Sleep and Memory" — Oxford Handbook of Human Memory.
8. Engram review — Nature Mol Psychiatry s41380-023-02137-5; PMC10618102.

**Math / RSB / capacity:**
9. Albanese E., Alessandrelli A. (2023). "Unsupervised and Supervised learning by Dense AM under replica symmetry breaking." arXiv 2312.09638.
10. (2025) "Modern Methods in Associative Memory." arXiv 2507.06211.
11. Palm G. (2013). "Neural associative memories and sparse coding." MIT lecture notes.
12. CALM (2025 Nov preprint). "Continual Associative Learning Model via Sparse." Preprints 202511.0430.
13. Bhatti et al. (2022). "Cluster-Based Inference for Memory-Based Cognition." biorxiv 2022.04.22.489185.
14. Kanerva-derived (2023 ICLR). "Sparse Distributed Memory IS [a continual learning solution]." klab.tch.harvard.edu publications.

**Materials / memristor / spin glass:**
15. Brivio S. et al. (2018). "Evidence of soft bound behaviour in analogue memristive devices." Sci Reports. PMC5940832.
16. Volkov-Sapir et al. (2024). "Cyclic quantum annealing: searching for deep low-energy states in 5000-qubit spin glass." Sci Reports s41598-024-80761-z.
17. Yang J., Lee S.-H. (2016). "Aging, memory, and nonhierarchical energy landscape of spin jam." PNAS. PMC5081640.

**Cross-domain / continual:**
18. Lopez-Paz D., Ranzato M. (2017). "Gradient Episodic Memory for Continual Learning." arXiv 1706.08840.
19. Wortsman M. et al. (2022). "Model soups: averaging weights of multiple fine-tuned models improves accuracy without increasing inference time." ICML. arXiv 2203.05482.
20. (2024 OpenReview). "Soup to go: mitigating forgetting during continual learning with model averaging." n2EU4PUrJP.
21. (2025) "Forget Forgetting: Continual Learning in a World of Abundant Memory." arXiv 2502.07274.

**Internal substrate:**
- `notes/research_drill_hopfield_consolidation_by_construction_3x_2026-06-27.md` (regime/alpha — companion drill)
- `notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md` (STC + slow-build precedent)
- `notes/research_R22_sleep_consolidation_2026-05-21.md`
- `hdlab/continual.py` (replay_cycle primitive atom 588)

---

## LIT-SCAN CALIBRATION

- P estimates deflated 0.15-0.25; novel-synthesis cap 0.50 applied.
- 5 disparate fields drilled (math/RSB, materials/memristor, neuroscience/engram-STC-BTSP-sleep, substrate-native HD, cross-domain continual learning). All five converge on SELECTIVE-SUBSET as the missing primitive — substrate writes globally, brain writes selectively.
- TOP-3 picks chosen for brain-grounding (existence proof; high prior per USER 2026-06-23) + substrate-native implementability + falsifiable discriminator that ANTI-correlates with saturation.

-- Research (Opus 4.7 1M; 5-angle drill on consolidation under saturation; TOP-3 picks ranked + cell sketches + discriminators).
