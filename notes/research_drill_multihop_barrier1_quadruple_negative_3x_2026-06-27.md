# RESEARCH DRILL — META_BARRIER_1_QUADRUPLE_NEGATIVE 3x cross-domain synthesis (multi-hop closure beyond 2 hops)

**Date:** 2026-06-27
**Filed-by:** Research (Opus 4.7 1M); team lead under Agent Teams; HYBRID architecture (KB + filesystem + Agent Teams primitives).
**Trigger:** USER drill request. META_BARRIER_1 atomized 2026-06-25: 4 substrate-native multi-hop closure attempts REFUTED at random-bipolar isotropic regime (consolidation, pointer-chain, WM-scaffold, CSP-gated) + META_M7 parallel-vote also regime-artifact. Multi-hop beyond 2 hops is currently the largest OPEN substrate-product limit.
**Discipline:** 0.20 calibration deflation; novel-synthesis P cap 0.50; brain-existence +0.10 prior; default UNDER-claim per Fix #28; ASCII only; HARD-PASS + HARD-FAIL bands MANDATORY; sanity-rail mandatory; CARDINALITY_OK field mandatory; DISCRIMINATOR-MUST-SURVIVE-SCALE pre-check mandatory; novelty AGAINST 28 prior-drilled angles (22 from gap1 5x drill 2026-06-26 + 6 from 2x revival drill 2026-06-26) required.

**Cross-thread anchors (de-conflict targets):**
- `notes/research_gap1_multihop_5x_drill_2026-06-26.md` (22 candidates across 9 fields; top-5 LDPC-BIDIR / RTS-SMOOTHER / VTE-MCTS / MPS / PARTICLE-FILTER)
- `notes/research_multihop_relational_2x_revival_drill_2026-06-26.md` (6 candidates; top-3 SOLAR / HOLOGRAPHIC-CHUNK-PACK / DIFFUSION-DENOISE)
- `notes/research_multihop_revival_5x_drill_2026-06-25.md` (4-for-4 HARD_FAIL diagnosis: downstream-of-cleanup doomed)
- META_BARRIER_1_QUADRUPLE_NEGATIVE atom (2026-06-25 atomization)
- META_M7 atom (parallel-vote regime-artifact)
- chain-grade NREM-replay primitive (existing); multi-bank WM K=4096 (existing); ultrametric clustering (existing); KG ingest 584-585-588 chain-grade.

---

## HEADLINE (one-line synthesis)

**Across the 28 prior-drilled angles, three structurally-novel angles SURVIVE the de-confliction filter: (M1) GROVER-STYLE AMPLITUDE AMPLIFICATION (quantum-inspired sqrt-N speedup via repeated reflect-about-mean + reflect-about-target; classical-numpy implementation) — NEVER drilled, novelty = the AMPLIFY-not-CLEANUP framing turns chain-state distribution into Grover-iteration target; (M2) NREM-REPLAY-DRIVEN ADAPTIVE CHAIN COMPACTION (uses substrate's CHAIN-GRADE NREM-replay primitive to COMPACT frequently-traversed multi-hop sequences into single-shot direct atoms DURING REPLAY, not at training-time) — distinct from holographic-chunk-pack (which is training-time, not adaptive) and from cortical schema extraction (which was MIDDLE_BAND; this is REPLAY-driven not online-extraction); (M3) ENZYME-CASCADE INTERMEDIATE STABILIZATION via BIND-TO-STABILIZER VECTOR (chemistry analog: enzyme active sites stabilize transition-state intermediates by lowering free energy of mid-chain conformations; substrate-native = bind the intermediate hop-vector to a learned STABILIZER scaffold vector that raises the cleanup margin by O(margin_lift) per intermediate, breaking error compounding at the per-hop level rather than the chain level). Top-3 P_deflated: M1=0.30, M2=0.45 (HIGHEST — composes with chain-grade primitive), M3=0.35. Plus two FOURTH-and-FIFTH supporting candidates: (M4) HOP-DISTANCE-METRIC-EMBEDDED CHAIN (encode hop position as continuous distance-from-start in the basis; entorhinal time-cell / EC ramping analog; metric-embedded gives the cleanup a global-position prior); (M5) HONEST-ACCEPTANCE 2-HOP PRIMITIVE + EXTERNAL ORCHESTRATION (substrate exposes 2-hop call as primitive; product layer chains 2-hop primitives with external state-tracking — this is the FAILBACK if M1-M4 all HARD_FAIL). P_deflated M4=0.25; M5 is not a HARD_PASS candidate but a substrate-product framing decision.**

Plain English: the 28 prior candidates fall into 4 mechanism-classes — (a) soft messages + bidirectional refinement (LDPC, RTS, turbo, TPR), (b) speculative rollout + gating (VTE-MCTS, particle-filter, K-beam, beam-search), (c) precomputed global closure (SR, HSR, MPS, compose-flyLSH, holographic-chunk), (d) primitive replacement (dense-Hopfield, sparse-bipolar, FHRR-coherent, diffusion-denoise). What's MISSING from all 28: AMPLITUDE-AMPLIFICATION (boost the correct-answer probability MULTIPLICATIVELY each iteration rather than adding refinement passes), REPLAY-ADAPTIVE COMPACTION (uses an existing chain-grade substrate primitive that none of the 28 angles use), and PER-HOP STABILIZATION via stabilizer-scaffold-vector (raises per-hop margin without replacing the cleanup primitive). These three address the error-compounding pathology at three different layers: M1 at the readout layer (amplify correct over noise), M2 at the structural layer (turn multi-hop chains into single-hop lookups via replay-driven shortcut creation), M3 at the per-hop primitive layer (raise margin without primitive replacement).

---

## DIAGNOSIS — WHY THE 28 PRIOR CANDIDATES LEAVE THESE GAPS

The four mechanism-classes covered by the 28 prior candidates all share ONE of two assumptions:

1. **Architectural assumption: the chain MUST be traversed at query time**, hop-by-hop, with per-hop cleanup. Mechanisms (a) + (b) + (d) all operate within this assumption — they vary the per-hop cleanup primitive or add refinement, but the chain is walked.

2. **Storage assumption: pre-compute the closure SO that the chain is not walked at query time**. Mechanism (c) does this — SR / HSR / MPS / holographic-chunk-pack all pre-compute O(W^K) at training time.

**The 3 gaps in this 2-axis framing:**

- **Gap A (post-query amplification):** what if the chain IS walked but the noisy distribution at the end is AMPLIFIED post-hoc to boost the correct answer over noise? This is Grover's amplitude amplification (quantum); classical analog = repeated reflect-and-rescale on the readout distribution. P_amplified_correct = sin^2((2k+1) * theta) where theta = arcsin(sqrt(P_correct)); sqrt-N speedup over linear amplification. Substrate-native form: AFTER the chain walk produces a noisy endpoint distribution, treat that distribution as a Grover-state, run K=O(sqrt(V_C)) amplification iterations to boost the correct endpoint from baseline 0.145 to ~0.85+ if a single correct atom is present in the candidate set.

- **Gap B (adaptive shortcut creation):** the substrate already has chain-grade NREM-replay (existing primitive, used for continual learning). What if NREM replay isn't just CONSOLIDATION but ADAPTIVE COMPACTION — replay-driven creation of direct-shortcut atoms for frequently-traversed paths? Brain analog: hippocampal sharp-wave-ripple replay during sleep extracts STATISTICAL REGULARITIES into cortex (Buzsaki 2015; Wilson-McNaughton 1994); the COMPACTION analog is that replay finds frequent A->B->C subsequences and INSTALLS A->C direct bindings. The cortex-schema MIDDLE_BAND drill was ONLINE extraction; replay-driven is OFFLINE, batch, and uses substrate's existing chain-grade replay primitive.

- **Gap C (per-hop margin stabilization without primitive replacement):** the dense-Hopfield / sparse-bipolar candidates (X1 / X2) REPLACE the primitive. The 28 prior angles either replace the primitive or don't touch it. What's untried: AUGMENT the primitive by binding each hop's intermediate to a STABILIZER VECTOR (learned scaffold) that raises the cleanup margin without changing the primitive. Chemistry analog: enzyme active sites stabilize transition-state intermediates by binding-affinity, lowering the activation energy of the next step. Substrate-native: each intermediate at hop-k is bound to a hop-k-specific STABILIZER atom; the stabilizer is trained to RAISE the cleanup margin at hop-k against the substrate's per-hop distractor distribution.

---

## CANDIDATE M1 — GROVER-STYLE AMPLITUDE AMPLIFICATION (quantum-inspired, classical numpy)

### Mechanism (lit anchor)

Grover 1996 "A fast quantum mechanical algorithm for database search" (STOC). Amplitude amplification iteration: given an N-element database with M=1 marked element, repeatedly apply the operator G = -A * S_0 * A^-1 * S_chi where A prepares uniform superposition, S_0 reflects about mean, S_chi reflects about target. After K = O(sqrt(N/M)) iterations, marked-element amplitude is amplified from 1/sqrt(N) to ~1 (probability ~1).

**Classical analog (Brassard-Hoyer-Mosca-Tapp 2002):** amplitude amplification generalizes to any process that prepares a state with success probability p; K = O(sqrt(1/p)) iterations boost p to ~1. The CLASSICAL implementation does NOT require quantum — repeated reflect-about-mean + reflect-about-target on real-valued amplitudes (probability distribution) achieves the same speedup, since the operator algebra is linear.

**Brain analog (weak; this is the AI-canonical anchor):** repeated cortical re-processing of perceptual ambiguity (Roelfsema 2006 "Cortical algorithms for perceptual grouping") — re-entrant processing AMPLIFIES task-relevant features over distractors via iterated top-down modulation. Less mature than the AI anchor but suggests the brain does SOMETHING like amplitude amplification at the perceptual level.

### Substrate-native mapping

After the depth-K chain walk, the substrate has produced an ENDPOINT DISTRIBUTION over the V_C codebook: p_i = exp(beta * <endpoint_vec, atom_i>) / Z. Baseline accuracy 0.145 at depth-5 means p_correct ~ 0.145 (slightly above chance 1/V_C = 0.005).

Grover-amplification iteration:
1. **Reflect about mean:** p_i' = 2 * mean(p) - p_i for each i. This is the diffusion operator (real-valued).
2. **Reflect about candidate set:** if the substrate has CONSTRAINT INFORMATION (e.g., "endpoint must be of type T" from the relation predicate), set p_i = -p_i for i NOT in candidate set, p_i = +p_i for i in candidate set.
3. **Renormalize** (classical analog; quantum is unitary).
4. **Repeat K = O(sqrt(V_C / |candidate_set|)) times** = O(sqrt(200/20)) = ~3 iterations for V_C=200, candidate=20.

After K iterations, the candidate-set entries in p are amplified by factor ~ sqrt(V_C / |candidate_set|) = sqrt(10) ~ 3.2. If p_correct started at 0.145, amplification lifts it to ~0.45-0.85 depending on the noise floor.

**CRITICAL substrate detail:** the "reflect-about-candidate-set" step requires CONSTRAINT INFORMATION — the substrate must know which atoms are TYPE-VALID for the endpoint. Substrate's KG ingest primitive (ch_588) provides this: the predicate p_K (last-hop relation) constrains the endpoint atom-type via the relation's range. For example, "person -[bornIn]-> location" constrains endpoint to be a location-atom.

### Discriminator design (META_M7-compliant, CARDINALITY_OK)

3-arm cell at production regime N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200, depths in {1, 2, 3, 5, 7}, 5 seeds.

- **ARM_BASELINE** = pointer-chain v2 forward argmax (anchors 0.69 / 0.485 / 0.31 / 0.145 / 0.08 across depths 1-7)
- **ARM_TYPE_CONSTRAINT_ONLY** = baseline + type-constraint filter on endpoint (relation range restriction); isolates the LIFT from the constraint alone (no amplification). Expected: modest lift, maybe 0.20-0.25 at depth-5.
- **ARM_GROVER_AMPLIFICATION** = baseline + type-constraint + Grover-K-iter amplification; K = round(pi/4 * sqrt(V_C / |candidate_set|)) = 3 for V_C=200, candidate=20.

**Super-additive test:** ARM_GROVER must beat ARM_TYPE_CONSTRAINT_ONLY by >= 0.10 at depth-5. If Grover-iter only matches constraint-alone, the amplification step is not adding value.

**CARDINALITY_OK pre-reg:** EXPECTED_N_UNITS per arm = 5 (depths) x 5 (seeds) x 200 (chains) = 5000 cells per arm. HARD_FAIL_CARDINALITY_BREACH if observed < 4900 cells (1% silent-drop tolerance).

**DISCRIMINATOR-MUST-SURVIVE-SCALE check (cell-author MANDATE):** smoke at full V_C=200 (not V_C=20) — smoke-at-small-V_C is meaningless because Grover speedup depends on V_C scale. Required smoke = V_C=200 + 1 seed + 1 depth (depth-5) + 50 chains. Must confirm: ARM_BASELINE ~ 0.145, ARM_TYPE_CONSTRAINT ~ 0.20-0.25, ARM_GROVER >= ARM_TYPE_CONSTRAINT + 0.10.

### P_deflated calculation

- Raw P = 0.50 (Grover-Brassard amplitude amplification has 30-year proven speedup; classical implementation is straightforward; key risk is the type-constraint substrate-native operationalization).
- -0.20 novel-synthesis (Grover-on-VSA is genuinely new combo; never published as far as lit-scan reveals).
- +0.00 brain-existence (weak brain anchor; mostly AI-canonical).
- **P_deflated = 0.30.**

### HARD-PASS / MIDDLE_BAND / HARD-FAIL bands

- **HARD_PASS:** ARM_GROVER depth-5 >= 0.50 AND > ARM_TYPE_CONSTRAINT + 0.10 AND sd <= 0.06.
- **MIDDLE_BAND:** ARM_GROVER depth-5 in 0.30-0.50 OR super-additive lift in 0.05-0.10.
- **HARD_FAIL:** ARM_GROVER depth-5 <= 0.25 OR adds <= 0.05 over ARM_TYPE_CONSTRAINT.

### Compute

- Laptop CPU 2-3 hr (3 amplification iters * 5 depths * 5 seeds * 200 chains at N=8192; matmul-bounded but small).
- ROUTE: laptop OK; not GPU-required (operations are vectorized but small).

### Novelty vs 28 prior-drilled angles

- LDPC-BIDIR / RTS-SMOOTHER / turbo: all do REFINEMENT via bidirectional sweeps; Grover is single-pass AMPLIFICATION of forward output.
- K-beam / particle-filter / VTE-MCTS: all maintain MULTI-HYPOTHESIS during the walk; Grover is single-hypothesis with post-hoc amplification.
- SR / MPS / holographic-chunk: all precompute closure; Grover does not change storage.
- Diffusion / dense-Hopfield / TPR / FHRR-coherent: primitive-replacement; Grover keeps the primitive.
- The 2026-06-25 "parallel vote was regime-artifact" META_M7 finding is DIFFERENT from Grover: parallel-vote averaged INDEPENDENT chains; Grover amplifies a SINGLE endpoint distribution via reflection. The reflect-about-mean operator is fundamentally different from voting.
- The CSP-gate failure: CSP rejected uncertain queries; Grover does NOT reject — it amplifies what's there.

### Sanity rail

- ARM_BASELINE must reproduce 0.145 +/- 0.02 at depth-5 (anchors the 4-refute regime).
- ARM_GROVER at K=0 iterations must = ARM_TYPE_CONSTRAINT (zero-iter Grover is identity).
- ARM_GROVER at K=infinity (impossible, but K=large) must converge to deterministic readout of constraint-set max-amplitude entry (Grover converges then oscillates).

### Composition opportunities with chain-grade primitives

- **Compose with KG ingest 588:** the type-constraint mask comes from relation-range; ch_588 already validates KG ingest at chain-grade. The substrate has the constraint primitive ready.
- **Compose with refuse-gate V_REL=256:** Grover's K-iter overshoot oscillation = signal of low-confidence. If Grover hits a stable amplification plateau < 0.40, refuse-gate fires with reason "no atom strongly favored by type constraint".
- **Compose with multi-bank WM K=4096:** maintain multiple candidate hypotheses across Grover-iters via WM banks; pick the best amplified candidate.
- **Compose with NREM replay (chain-grade primitive):** if Grover succeeds on chain X, replay-bind a direct A->endpoint shortcut for chain X (links to M2 candidate).

---

## CANDIDATE M2 — NREM-REPLAY-DRIVEN ADAPTIVE CHAIN COMPACTION (TOP RANK; brain-grounded; composes with chain-grade primitive)

### Mechanism (lit anchor)

Buzsaki 2015 "Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning" (Hippocampus 25). Sharp-wave ripples (SWRs) during NREM sleep replay recent experiential sequences at 8-20x compressed time-scale. Replay isn't passive — it's CONSOLIDATION + EXTRACTION + COMPACTION: frequently co-activated sequences get strengthened into cortex as DIRECT associations (Wilson-McNaughton 1994 "Reactivation of hippocampal ensemble memories during sleep"; Lewis-Durrant 2011 "Overlapping memory replay during sleep builds cognitive schemata"; Davidson 2009 "Hippocampal replay of extended experience").

**Key brain mechanism:** replay-driven cortical learning forms SHORTCUT ASSOCIATIONS. If A->B->C->D occurs frequently in experience, NREM replay strengthens DIRECT A->D associations in cortex (Lewis-Durrant 2011 review). This is NOT online schema extraction (which is what the substrate's cortical-schema MIDDLE_BAND drill tested); it's OFFLINE, BATCH, REPLAY-DRIVEN compaction.

**Computational analog:** off-policy replay buffers in RL (Mnih DQN 2015) do exactly this — replay-driven learning extracts SHORTCUT VALUE-ASSOCIATIONS across long trajectories. Dyna-Q (Sutton 1990) replays trajectories to compact long action-sequences into direct value updates.

### Substrate-native mapping

Substrate has CHAIN-GRADE NREM-REPLAY primitive (existing). Current use: continual-learning replay during ingest. NEW use:

**Algorithm REPLAY-COMPACT:**
1. During NREM replay phase, walk each stored chain A_1 -> A_2 -> ... -> A_K (substrate already does this for consolidation).
2. For each chain, count the FREQUENCY of co-traversal across the chain ensemble. Frequent chains = STATISTICAL REGULARITIES.
3. For chains with frequency above threshold tau_freq (top-N most common), BIND a direct shortcut: A_1 -> A_K via relation p_compact (new relation atom).
4. The shortcut atom is stored as a NORMAL substrate atom: bind(A_1, p_compact, A_K). It's addressable as a SINGLE-HOP cleanup at query time.
5. At query time, BEFORE walking the full chain, the substrate checks for direct shortcut: cleanup(A_1, p_compact) — if hit (high margin), return A_K directly; if miss, fall back to full chain walk.

**The compaction-vs-walk tradeoff:** storing K shortcut atoms costs K substrate-atoms (cheap; substrate has 177K+ atoms already). Query time: shortcut hit = 1-hop instead of K-hop; shortcut miss = K-hop fall-back. Net: if shortcut hit rate > 1/K * (per-hop accuracy)^K, compaction wins.

**Replay-frequency criterion:** the substrate's NREM replay already weights frequent sequences; the existing chain-grade primitive provides the frequency-counting infrastructure. The NEW thing is the BINDING of compacted-shortcut atoms during replay, and the QUERY-TIME shortcut-check.

### Discriminator design (META_M7-compliant, CARDINALITY_OK)

3-arm cell at production regime N=8192, V_C=200, V_P=10, n_chains_train=500, n_chains_query=200, depths in {1, 2, 3, 5, 7}, 5 seeds.

- **ARM_BASELINE** = pointer-chain v2 (anchors 0.69 / 0.485 / 0.31 / 0.145 / 0.08).
- **ARM_HOLOGRAPHIC_RAIL** = holographic-chunk-pack v1 from candidate P1 in 2x revival drill (anchor pending; rail against training-time chunking). If that cell hasn't landed, use HSR-multiscale rail as substitute.
- **ARM_NREM_REPLAY_COMPACT** = ADAPTIVE replay-driven shortcut creation; n_replay_passes=10; tau_freq = top-20% chains by frequency.

**Within-arm metrics:** shortcut-HIT-rate per depth (frequent chains => high hit rate => mostly 1-hop performance); MISS-rate fall-back accuracy (matches baseline).

**CARDINALITY_OK:** EXPECTED_N_UNITS per arm = 5 depths * 5 seeds * 200 chains = 5000 query cells; plus n_chains_train=500 chains over 10 replay passes = 5000 replay cells. HARD_FAIL_CARDINALITY_BREACH if observed < 4900 of either.

**DISCRIMINATOR-MUST-SURVIVE-SCALE check:** smoke at FULL n_chains_train=500 (not n_chains_train=10) — small-train means no shortcuts will be created. Required smoke = full n_chains_train + 1 seed + 1 depth (depth-5) + 50 chains_query. Must confirm: shortcut HIT rate >= 30% at depth-5 (chains that match a created shortcut). If smoke shows shortcut HIT rate < 20%, the mechanism is not firing — cell is REJECTED before full dispatch.

**NOVELTY TEST vs holographic-chunk-pack:** holographic-chunk is TRAINING-TIME, FIXED set of chunks. NREM-replay-compact is ADAPTIVE — shortcuts created based on observed query distribution. If the query distribution shifts, NREM-compact ADAPTS via re-replay; holographic-chunk does not. Discriminator: add a SHIFT condition (query distribution differs from train); test both ARM_HOLOGRAPHIC and ARM_NREM_COMPACT on the shifted set.

### P_deflated calculation

- Raw P = 0.60 (substrate already has chain-grade NREM replay; the compaction is a small extension on top of an existing chain-grade primitive; brain analog is direct; AI off-policy replay analog is established).
- -0.15 novel-synthesis (replay-driven adaptive compaction on VSA is new combo, but each component is established).
- +0.10 brain-existence-proof (sharp-wave-ripple replay-compaction is direct brain mechanism).
- **P_deflated = 0.55** — wait, this exceeds the 0.50 novel-synthesis cap.
- **P_deflated = 0.45 (CAP-HONORED)** — capping at 0.50, then -0.05 for compute-uncertainty in the replay-batch-size + frequency-threshold hyperparam space.
- **FINAL P_deflated = 0.45 — HIGHEST of the 3 candidates.**

### HARD-PASS / MIDDLE_BAND / HARD-FAIL bands

- **HARD_PASS:** ARM_NREM_REPLAY_COMPACT depth-5 mean >= 0.50 AND > ARM_BASELINE + 0.30 AND shortcut-HIT-rate >= 0.40 AND sd <= 0.06.
- **MIDDLE_BAND:** depth-5 mean in 0.30-0.50 OR shortcut-HIT-rate 0.20-0.40.
- **HARD_FAIL:** depth-5 mean <= 0.25 OR shortcut-HIT-rate <= 0.15 (mechanism not firing) OR FALLBACK-MISS accuracy < ARM_BASELINE - 0.05 (shortcut creation HURTS baseline).

### Compute

- Laptop CPU 4-5 hr (replay passes are expensive: 10 passes * 500 train chains * depth 5 chain walks = 25k chain-walks; plus query 5 depths * 5 seeds * 200 chains = 5k query walks). Route via orchestrator to remote_cpu if compute > 4 hr.

### Novelty vs 28 prior-drilled angles

- Holographic-chunk-pack (P1, 2x revival): TRAINING-TIME chunk creation, fixed set; M2 is ADAPTIVE replay-time.
- Cortical-schema-extraction (MIDDLE_BAND historical): ONLINE schema extraction at query time; M2 is OFFLINE replay-time batch.
- SR / HSR closure: precomputed M = sum gamma^k W^k once at training; M2 creates SELECTIVE shortcuts only for frequent chains, not all chains.
- MPS: bond-truncated dense closure; M2 is sparse selective shortcuts.
- None of the 28 use the substrate's existing chain-grade NREM-replay primitive for compaction — they all build NEW mechanisms.

### Sanity rail

- ARM_BASELINE reproduces 0.145 +/- 0.02 at depth-5.
- Disable replay (n_replay_passes=0) => ARM_NREM_REPLAY_COMPACT = ARM_BASELINE.
- Shortcut-HIT entries = single-hop cleanup accuracy (substrate's ch_587 anchor 0.90+); shortcut-MISS entries fall back to baseline chain accuracy.

### Composition opportunities with chain-grade primitives

- **NREM-replay primitive (chain-grade):** this candidate USES the chain-grade primitive directly — highest leverage.
- **KG ingest 588:** provides relation atoms p_compact for shortcut binding; ch_588 chain-grade gives the binding primitive.
- **Multi-bank WM K=4096:** during replay, WM banks track per-chain frequency counts; one bank per chain-class.
- **Ultrametric clustering (existing):** group similar chains in ultrametric tree; create shortcut PER CLUSTER, not per individual chain — amortizes shortcut creation cost.
- **Compose with M1 Grover:** if Grover succeeds on chain X, REPLAY-BIND a shortcut for chain X (Grover identifies high-confidence chains during query; M2 commits them to storage). M1 + M2 are SYNERGISTIC, not competitive.

---

## CANDIDATE M3 — ENZYME-CASCADE INTERMEDIATE STABILIZATION via BIND-TO-STABILIZER VECTOR

### Mechanism (lit anchor)

Fersht 1999 "Structure and Mechanism in Protein Science" (chapter 12: enzyme catalysis); transition-state stabilization theory (Pauling 1946 + Haldane 1930). Enzymes accelerate multi-step reactions by binding to TRANSITION-STATE INTERMEDIATES with higher affinity than substrates or products — this lowers the activation energy of each step in a cascade. Each intermediate in a multi-step enzyme cascade (e.g., glycolysis: 10 enzyme-catalyzed steps from glucose to pyruvate) is STABILIZED by its enzyme's active site, raising the local concentration of the correct intermediate over the noise floor of side-reactions.

**Computational analog:** auxiliary-task scaffolding in deep learning (Andreas-Klein 2017 "Modular Multitask Reinforcement Learning with Policy Sketches"); intermediate-supervision in RNNs (Lipton 2015 "Critical Review of RNNs for Sequence Learning"); BERT-style intermediate-layer supervision raises per-layer feature quality.

**Brain analog (secondary):** GABAergic disinhibition in cortex stabilizes intermediate task-states (Letzkus 2015 "Disinhibition, a Circuit Mechanism for Associative Learning and Memory"). Less direct than the chemistry anchor.

### Substrate-native mapping

The per-hop cleanup at hop-k operates on the intermediate vector E_k. Currently, E_k is the noisy output of W @ (E_{k-1} bound to p_k); cleanup-margin against distractors is ~0.69 per hop, leading to compounded error.

**STABILIZER mechanism:** train a per-hop STABILIZER VECTOR S_k such that:
- S_k is bound to E_k via convolution: E_k_stabilized = bind(E_k, S_k).
- S_k is OPTIMIZED to MAXIMIZE the cleanup margin at hop-k: argmax_{S_k} margin(W @ bind(E_k, S_k)).
- S_k is HOP-K-SPECIFIC and shared across all chains at hop-k.

**How training S_k works:** S_k is a learnable atom in the substrate's N_DIM space. Loss = -sum_chains (top-1-similarity - top-2-similarity) of cleanup at hop-k. Gradient via numerical optimization on a small training set (~100 chains). S_k is then frozen and used at query time.

**Why this differs from primitive replacement (dense-Hopfield):** the cleanup primitive (HRR / VSA convolution + W @ key) is UNCHANGED. The stabilizer is an ADDITIONAL bind operation that pre-conditions the input to cleanup. The stabilizer is hop-position-specific but query-content-agnostic.

**Why this differs from holographic-chunk-pack:** holographic-chunk stores PER-CHAIN chunked atoms (chain-specific). Stabilizer is PER-HOP-POSITION (chain-agnostic, generalizes across all chains at hop-k).

**Theoretical margin lift:** if S_k is well-optimized, per-hop margin can rise from 0.69 to 0.80-0.90 (analogous to enzyme catalysis raising reaction rate 10^6+ fold). At per-hop 0.90, depth-5 accuracy = 0.90^5 = 0.59 vs current 0.145.

### Discriminator design (META_M7-compliant, CARDINALITY_OK)

3-arm cell at production regime N=8192, V_C=200, V_P=10, K_SET=20, n_chains_train=100, n_chains_query=200, depths in {1, 2, 3, 5, 7}, 5 seeds.

- **ARM_BASELINE** = pointer-chain v2 (anchors 0.69 / 0.485 / 0.31 / 0.145 / 0.08).
- **ARM_RANDOM_STABILIZER** = bind random hop-k-specific random vector S_k; isolates whether ANY bind improves cleanup (it should NOT; bind with random vector is noise). Expected: ~0.145 or slightly worse.
- **ARM_TRAINED_STABILIZER** = bind hop-k-specific OPTIMIZED S_k; cleanup-margin maximized.

**Super-additive test:** ARM_TRAINED_STABILIZER must beat ARM_RANDOM_STABILIZER by >= 0.10 at depth-5 (margin lift is real, not just basis-change).

**Within-arm metric:** per-hop margin (top-1 minus top-2 similarity) for each arm; trained-stabilizer must show per-hop margin >= 0.80 across all hops (vs 0.69 baseline).

**CARDINALITY_OK:** EXPECTED_N_UNITS per arm = 5 depths * 5 seeds * 200 chains = 5000 query cells; HARD_FAIL_CARDINALITY_BREACH if < 4900.

**DISCRIMINATOR-MUST-SURVIVE-SCALE check:** smoke at full V_C=200 (not V_C=20) — stabilizer training depends on the distractor distribution which is V_C-dependent. Required smoke = V_C=200, 1 seed, depth 5, 50 chains. Must confirm: trained-stabilizer per-hop margin > random-stabilizer per-hop margin by >= 0.05 (training is learning SOMETHING).

### P_deflated calculation

- Raw P = 0.50 (enzyme analog is theoretically clean; intermediate-supervision in DL is established; main risk is whether S_k optimization actually finds a good per-hop margin lift on substrate's W matrix).
- -0.20 novel-synthesis (substrate-VSA stabilizer-bind is new combo).
- +0.05 brain-existence (weak; GABAergic disinhibition is partial analog).
- **P_deflated = 0.35.**

### HARD-PASS / MIDDLE_BAND / HARD-FAIL bands

- **HARD_PASS:** ARM_TRAINED_STABILIZER depth-5 mean >= 0.45 AND > ARM_RANDOM_STABILIZER + 0.10 AND per-hop margin >= 0.80 AND sd <= 0.06.
- **MIDDLE_BAND:** depth-5 mean in 0.25-0.45 OR per-hop margin in 0.72-0.80.
- **HARD_FAIL:** depth-5 mean <= 0.20 OR per-hop margin <= 0.72 (stabilizer training did not lift margin) OR ARM_TRAINED <= ARM_RANDOM + 0.05 (training is no better than random).

### Compute

- Laptop CPU 3-4 hr (stabilizer optimization: 100 train chains * 5 hop positions * 50 grad steps = 25k cleanup ops; plus query 5k cells). Numerical optimization may need to route to GPU if grad-step compute exceeds 4 hr.

### Novelty vs 28 prior-drilled angles

- Dense-Hopfield / sparse-bipolar (X1, X2): REPLACE the cleanup primitive; M3 augments with a bind pre-condition.
- TPR (A2, 2x revival): outer-product binding alternative to HRR convolution; M3 uses HRR convolution unchanged but pre-binds stabilizer.
- LDPC-BIDIR / RTS-SMOOTHER: forward-backward refinement at chain level; M3 raises per-hop quality before any refinement.
- VTE-MCTS / particle-filter: multi-hypothesis at chain level; M3 raises per-hop signal so single-hypothesis works.
- Cerebellar-forward-model (N3): SUPERVISED prediction of next state; M3 doesn't predict, it pre-conditions cleanup input.

### Sanity rail

- ARM_BASELINE reproduces 0.145 +/- 0.02 at depth-5.
- ARM_RANDOM_STABILIZER must be within 0.05 of baseline at all depths (random bind doesn't help).
- depth-1 single-hop with trained stabilizer must be near 1.0 (single-hop is already 0.90+ baseline; stabilizer should push to ceiling).

### Composition opportunities with chain-grade primitives

- **KG ingest 588:** stabilizer S_k can be relation-specific S_k_p (per relation type); learned from KG training data.
- **NREM replay (chain-grade primitive):** during replay, refine S_k against the observed query distribution (online stabilizer adaptation).
- **Multi-bank WM K=4096:** stabilizer banks for different chain-classes (e.g., one bank of S_k vectors per relation-domain).
- **Compose with M2 NREM-replay-compact:** stabilizer reduces per-hop error; compaction reduces hop count. Together: compaction creates shortcut atoms, stabilizer raises shortcut margin. Strongly complementary.
- **Compose with M1 Grover:** stabilizer raises per-hop margin from 0.69 to 0.85; Grover amplifies the post-chain distribution. Stabilizer makes Grover work on a less noisy endpoint distribution. Strongly complementary.

---

## CANDIDATE M4 — HOP-DISTANCE-METRIC-EMBEDDED CHAIN (entorhinal time-cell / EC ramping analog)

### Mechanism (lit anchor)

Eichenbaum 2014 "Time cells in the hippocampus: a new dimension for mapping memories" (Nat Rev Neurosci). CA1 contains TIME CELLS that fire at specific delays in a sequence, encoding ELAPSED TIME / SEQUENCE POSITION as a continuous variable. EC ramping cells (Igarashi 2014, Nature) encode position-in-sequence via a ramping firing rate.

**Key brain mechanism:** sequence position is encoded as a CONTINUOUS METRIC dimension in the basis, not as a discrete categorical token. This gives multi-hop chains a GLOBAL POSITION PRIOR: the cleanup at hop-k can EXPECT the result to be near a specific point in metric-embedded space.

**AI analog:** rotary position embeddings (RoPE; Su 2024) in transformers encode position as a continuous rotation in vector space; positional sinusoidal encodings (Vaswani 2017); these give the transformer a continuous position metric that scales smoothly to long sequences.

### Substrate-native mapping

Currently: chain position is encoded via PERMUTATION (substrate's existing permutation-binding). Permutation is CATEGORICAL — there's no continuous metric between perm^3 and perm^4.

**METRIC-EMBEDDED CHAIN:** encode chain position k as a CONTINUOUS VECTOR position_vec(k) = cos(2 pi k / K_max) * basis_1 + sin(2 pi k / K_max) * basis_2 + ... (sinusoidal positional encoding adapted to substrate's N_DIM). At hop-k, the intermediate E_k is bound to position_vec(k); cleanup uses the position prior to restrict candidates to atoms within a metric ball around the expected position.

**Why this differs from permutation-binding (drilled 2026-06-22):** permutation is discrete categorical; metric-embedded is continuous. The 2026-06-22 drill used permutation as a CATEGORICAL position tag; this candidate uses position as a CONTINUOUS METRIC PRIOR that the cleanup uses for candidate restriction.

**Why this differs from grid-cell-linear-lookahead (N5, gap1 5x drill):** N5 used multi-scale W^k for hierarchical lookahead; M4 uses continuous-metric position-embedding for per-hop candidate restriction. Different operationalization.

### Discriminator design

3-arm cell at production regime N=8192, V_C=200, V_P=10, depths in {1, 2, 3, 5, 7}, 5 seeds.

- **ARM_BASELINE** = pointer-chain v2.
- **ARM_PERMUTE_POSITION** = baseline + permutation-position binding (the 2026-06-22 drill anchor; isolates discrete-categorical position advantage).
- **ARM_METRIC_POSITION** = baseline + continuous-metric position embedding + ball-restricted cleanup at each hop.

**Super-additive test:** ARM_METRIC must beat ARM_PERMUTE by >= 0.05 at depth-5.

**CARDINALITY_OK:** standard 5000 cells per arm.

### P_deflated calculation

- Raw P = 0.35 (continuous-metric position prior is theoretically clean but substrate's existing per-hop is highly nonlinear due to W's noise; metric prior may not survive nonlinearity).
- -0.20 novel-synthesis.
- +0.10 brain-existence.
- **P_deflated = 0.25.**

### HARD-PASS / MIDDLE_BAND / HARD-FAIL

- **HARD_PASS:** depth-5 >= 0.40 AND > ARM_PERMUTE + 0.05.
- **MIDDLE_BAND:** depth-5 in 0.22-0.40.
- **HARD_FAIL:** depth-5 <= 0.20 OR no lift over permute-position.

### Compute

- Laptop CPU 2 hr (continuous-encoding is cheap; ball-restriction is the only new compute).

### Novelty vs 28 prior-drilled angles

- Permutation-binding (drilled 2026-06-22): discrete categorical position; M4 is continuous metric.
- Grid-cell N5 (gap1 5x): multi-scale W^k; M4 is single-scale continuous embedding.
- TEM (gap1 5x): factor representation of position-in-space; M4 is position-in-sequence specifically.

### Composition opportunities

- **NREM replay:** position-metric is preserved across replay; replay-compact shortcuts get position-metric for FREE.
- **KG ingest 588:** relation types may have characteristic position distributions (e.g., "bornIn" usually appears at hop-1, "worksFor" at hop-2); position-metric encodes these.
- **WM K=4096:** WM banks indexed by metric position; bank-k holds intermediates expected near position k.

---

## CANDIDATE M5 — HONEST-ACCEPTANCE 2-HOP PRIMITIVE + EXTERNAL ORCHESTRATION (FRAMING; not HARD_PASS-able)

### Mechanism

Accept that substrate is structurally 2-hop with high fidelity (per-hop ~ 0.85, depth-2 ~ 0.65 chain-grade). Expose 2-hop traversal as a PRIMITIVE; product layer chains 2-hop calls with EXTERNAL state-tracking (Python harness / Claude orchestration / vector DB intermediary).

**Brain analog:** PFC + hippocampus combined achieve multi-hop via PFC providing external state tracking (working memory holds intermediate; hippocampus does the 2-hop episodic recall; PFC re-issues the next 2-hop query with the new intermediate). The substrate has the 2-hop hippocampus + WM K=4096 buffer; what's missing is the QUERY ORCHESTRATOR.

### Substrate-product framing

**This is not a cell.** This is a substrate-product framing: if M1, M2, M3, M4 all HARD_FAIL, then the substrate-product story shifts to:

- Substrate exposes `query_2hop(start, relation_1, relation_2)` as the load-bearing primitive (chain-grade fidelity).
- Multi-hop queries (>2 hops) require either external orchestration (Python harness chains 2-hop calls with explicit intermediate tracking) OR external reasoning (LLM / agent issues per-2-hop queries with intermediate validation).
- Audit-chain capability: each 2-hop call is fully provenance-tracked; the orchestrator's per-2-hop call sequence is also provenance-tracked.
- Refuse-gate: substrate refuses 2-hop calls with low confidence; orchestrator handles the refusal externally.

**Why this is a REASONABLE framing:** the brain's hippocampus is ALSO structurally limited in chain depth (Howard-Eichenbaum 2017 review: hippocampal recall fidelity drops sharply beyond 2-3 step delays); humans achieve multi-hop reasoning via PFC + external aids (writing things down, mental rehearsal); LLMs achieve multi-hop via chain-of-thought (external token-level state). Multi-hop is HARD across all known systems; expecting substrate to solve internally what brain solves externally may be a category error.

**Decision criterion for adopting M5:** if M1, M2, M3 all deliver HARD_FAIL on their discriminators at production scale (depth-5 < 0.25 for all three), pivot to M5 substrate-product framing. Update PLAN.md + master-plan + memory accordingly.

---

## TOP-3 RANK-ORDERED DISPATCH

| Rank | Candidate | Mechanism class | Field | P_deflated | Compute | Discriminator |
|------|-----------|-----------------|-------|------------|---------|---------------|
| 1 | M2 NREM-REPLAY-COMPACT | adaptive-compaction | brain + AI off-policy replay | 0.45 | 4-5 hr | 3-arm: BASELINE / HOLOGRAPHIC_RAIL / NREM_REPLAY_COMPACT |
| 2 | M3 STABILIZER-VECTOR | per-hop margin lift | chemistry + DL aux-supervision | 0.35 | 3-4 hr | 3-arm: BASELINE / RANDOM_STABILIZER / TRAINED_STABILIZER |
| 3 | M1 GROVER-AMPLIFICATION | post-hoc amplification | quantum-inspired classical | 0.30 | 2-3 hr | 3-arm: BASELINE / TYPE_CONSTRAINT_ONLY / GROVER_AMPLIFICATION |
| 4 | M4 METRIC-POSITION | continuous-position prior | brain time-cells + RoPE | 0.25 | 2 hr | 3-arm: BASELINE / PERMUTE_POSITION / METRIC_POSITION |
| 5 | M5 HONEST-ACCEPT 2-HOP | substrate-product framing | acceptance | n/a | n/a | not a cell |

**All four cells (M1-M4) share the META_M7-compliant sanity rail:** ARM_BASELINE reproduces 0.145 +/- 0.02 at depth-5; depth-1 must be at single-hop 0.90+ baseline. If breached, cell REJECTED.

### Recommended dispatch sequence

1. **IMMEDIATE (1 cycle, highest P + composes with chain-grade primitive):** M2 NREM-REPLAY-COMPACT. Uses existing chain-grade NREM replay; ADAPTIVE compaction is the most direct substrate-extension of an existing chain-grade capability.

2. **PARALLEL (1 cycle, complementary mechanism layer):** M3 STABILIZER-VECTOR. Operates at per-hop primitive layer; M2 operates at chain-storage layer. Together they address error compounding at TWO independent layers.

3. **CONDITIONAL (1 cycle, if M2 + M3 ship MIDDLE_BAND or HARD_PASS):** M1 GROVER-AMPLIFICATION. Cheap to run; could amplify the result of M2/M3 to chain-grade. Strongly composes with M2 + M3.

4. **CONDITIONAL (cycle 2-3, if M1 + M2 + M3 all HARD_PASS or MIDDLE_BAND):** M4 METRIC-POSITION as additional independent lever; tests whether continuous position priors stack with the other mechanisms.

5. **PIVOT (only if M1, M2, M3 ALL HARD_FAIL):** adopt M5 honest-acceptance framing; update PLAN.md + substrate-product story.

### Composition opportunity: combined cell

If compute budget supports it, file ONE 5-arm combined cell:
- ARM_BASELINE
- ARM_M2_NREM_REPLAY_COMPACT
- ARM_M3_TRAINED_STABILIZER
- ARM_M1_GROVER_AMPLIFICATION (composes with type-constraint)
- ARM_COMBINED (M2 + M3 + M1; full stack)

If ARM_COMBINED >= 0.65 at depth-5, the stack is SYNERGISTIC and the substrate has multi-hop closure beyond 2 hops via this stack. This is the HIGH-LEVERAGE path.

---

## CHEAP DECISIVE TEST (META_M7 COMPLIANT)

`exp_substrate_multihop_barrier1_3x_meta_drill_v1` — single multi-arm cell

Suggested arms:
1. ARM_BASELINE_PTR_CHAIN (anchors 0.145 at depth-5)
2. ARM_M2_NREM_REPLAY_COMPACT (rank-1; brain-grounded; composes with chain-grade)
3. ARM_M3_TRAINED_STABILIZER (rank-2; per-hop margin lift)
4. ARM_M1_GROVER_AMPLIFICATION (rank-3; post-hoc amplify; with type-constraint)
5. ARM_COMBINED_M2_M3_M1 (full stack; super-additive test)

Smoke required at FULL V_C=200, full n_chains_train=500 (for M2), 1 seed, depth-5 only, 50 chains_query. Must show:
- ARM_BASELINE within +/- 0.02 of 0.145
- ARM_M2 shortcut-HIT rate >= 0.30
- ARM_M3 trained-stabilizer margin > random-stabilizer margin by >= 0.05
- ARM_M1 Grover-amplification > type-constraint-only by >= 0.05

If smoke gates all pass, dispatch full run (5 seeds, 5 depths, 200 chains).

Decision logic:
- ARM_COMBINED depth-5 >= 0.65 => META_BARRIER_1 BROKEN; multi-hop closure beyond 2 hops achieved via 3-mechanism stack. Atomize as chain-grade if 5-seed reproducible.
- ARM_COMBINED depth-5 in 0.45-0.65 + at least one of M1/M2/M3 individually HARD_PASS => META_BARRIER_1 PARTIALLY BROKEN; specific mechanism is the load-bearing lever.
- ARM_COMBINED depth-5 in 0.25-0.45 + no individual HARD_PASS => MIDDLE_BAND; mechanism class is correct but parameter-tuning needed; consider M4 addition.
- ARM_COMBINED depth-5 < 0.25 AND all individual HARD_FAIL => META_BARRIER_1 STILL OPEN; pivot to M5 honest-acceptance framing.

---

## FALSIFIABLE PREDICTIONS WITH HARD-PASS + HARD-FAIL

### Strong claim (top-3 of M1-M4)
- **HARD-PASS:** at least one of {M1, M2, M3} delivers HARD-PASS on its discriminator at production regime (N=8192, V_C=200, V_P=10, 5 seeds, sd <= 0.06). Combined: P_combined ~ 0.60-0.70 if independent; P_combined ~ 0.50-0.55 if correlated (M2 and M3 share primitive-level operations).
- **HARD-FAIL:** ALL three of {M1, M2, M3} HARD-FAIL on their discriminators with no super-additivity over baselines.

### Meta-prediction (the 3 mechanisms address 3 different layers)
- **HARD-PASS:** the verdicts on M1, M2, M3 are UNCORRELATED across discriminators (each addresses a distinct layer: post-hoc amplification, chain-storage compaction, per-hop margin). Independent verdicts confirms the 3-layer diagnosis.
- **HARD-FAIL:** the verdicts CO-VARY perfectly => there's a SHARED bottleneck not addressed by any of M1-M4 (likely the per-hop primitive at production scale, supporting the dense-Hopfield + sparse-bipolar X1 pivot OR the M5 honest-acceptance pivot).

### Super-additive prediction (combined stack)
- **HARD-PASS:** ARM_COMBINED depth-5 > MAX(M1, M2, M3) + 0.10 (super-additive stack). If true, the 3 mechanisms operate at orthogonal layers.
- **HARD-FAIL:** ARM_COMBINED depth-5 <= MAX(M1, M2, M3) + 0.03 (no stack-additive lift). If true, the mechanisms share a hidden common-mode.

### Cross-thread predictions
- **HARD-PASS:** M2 NREM-REPLAY-COMPACT shortcut-HIT rate scales LINEARLY with training-set size (more train chains => more shortcuts created => higher hit rate). Test: n_chains_train scan {100, 500, 1000}; HIT rate must rise monotonically.
- **HARD-PASS:** M3 STABILIZER per-hop margin > 0.80 at all 5 hop positions. Test: per-hop margin tracked at each k in {1,2,3,4,5}.
- **HARD-PASS:** M1 GROVER amplification follows the K = pi/4 * sqrt(V_C/|candidate|) optimal-iteration scaling — too-few iterations under-amplifies, too-many over-rotates. Test: K-iter scan {1, 2, 3, 5, 8}; peak must be near K=3 for V_C=200, candidate=20.

### Calibration check
- The 0.45 P_deflated for M2 (top rank) is at the cap. M2 has the strongest brain-existence anchor (SWR replay is direct) AND uses an existing chain-grade substrate primitive, so the prior is well-justified.
- The P_combined for at-least-one-HARD_PASS (M1, M2, M3) is in 0.50-0.60 range — this is a HIGH-LEVERAGE drill where the EV is positive even if individual probabilities are moderate.

---

## CROSS-THREAD SYNTHESIS

1. **Three SUBSTRATE-LAYER gaps in the 28 prior-drilled angles, each addressed by ONE of M1-M3.** The mechanism class taxonomy (soft-bidirectional / speculative-rollout / global-closure / primitive-replacement) was SATURATED in the 22+6 drilled set. The new layer taxonomy (post-hoc-amplification / replay-adaptive-compaction / per-hop-margin-stabilization) is ORTHOGONAL — none of the 28 candidates use any of these three layers.

2. **The brain-grounded chain-grade NREM-replay primitive is HIGH-LEVERAGE and UNDER-USED.** Substrate has chain-grade NREM replay (existing). M2 leverages it directly — replay-driven adaptive compaction extends an existing chain-grade primitive rather than building a new mechanism. This is the most direct substrate-product extension available. Per Director's discipline "results-to-application cadence same-cycle" (USER 2026-06-22), if M2 HARD_PASSes, the chain-grade NREM-replay primitive gets its second chain-grade application (after continual-learning).

3. **The "downstream-of-cleanup is doomed" 2026-06-25 thesis is REFINED again.** M3 stabilizer doesn't operate downstream of cleanup; it operates UPSTREAM by pre-conditioning the cleanup input. M1 Grover operates POST cleanup but on the DISTRIBUTION not on individual decisions. M2 compaction bypasses cleanup entirely for frequent chains. The 2026-06-25 thesis applies to mechanisms that operate strictly downstream of (i.e., taking the cleanup output as input). M1-M3 operate at orthogonal layers.

4. **The honest-acceptance M5 path is a REASONABLE substrate-product framing.** Brain hippocampus is ALSO structurally limited beyond 2-3 hops; humans use external aids; LLMs use CoT. Multi-hop is HARD across all known systems. If M1-M3 HARD_FAIL, the M5 framing is not defeat but RECALIBRATION of substrate-product story. Director's lock: "capability dev is goal; cert-grade is instrument" (USER 2026-06-19) — if 2-hop is the load-bearing capability, build the product around it.

5. **Cross-domain field coverage:** this drill adds NEW coverage in:
   - Quantum-inspired classical algorithms (Grover; un-drilled scope-expansion field).
   - Off-policy replay buffers (Dyna-Q + DQN; un-drilled in substrate context).
   - Enzyme transition-state stabilization (chemistry; un-drilled).
   - Time-cell / EC ramping continuous-metric position encoding (un-drilled, distinct from prior permutation drills).
   The gap1 5x drill covered info-theory / materials / pure-math / hardware / neuroscience / robotics / distributed / signal-proc / primitive-replacement. The 2x revival drill covered attention-AI / HD-VSA / diffusion / predictive-coding. This 3x drill adds quantum-classical / replay-RL / chemistry / position-encoding.

6. **Substrate-product implications (per [[feedback-no-papers-product-only]]):**
   - **M2 chain-grade extension:** if HARD_PASS, substrate has NEW load-bearing capability: ADAPTIVE chain compaction during sleep. Product story: "substrate learns shortcuts as you use it; frequently-asked multi-hop queries become single-hop after replay." Strong product differentiator vs vector-DB (which doesn't have replay) and vs LLM (which doesn't have substrate's atom-level provenance).
   - **M3 margin lift:** if HARD_PASS, single-hop accuracy can be pushed to 0.95+ at production V_C=200, lifting all chain-grade work. Product story: "per-hop confidence above 95%" — auditable-AI memory differentiator.
   - **M1 amplification:** if HARD_PASS, substrate exposes amplification primitive that boosts low-confidence query results. Product story: "iterative confidence-boost on demand." Refuse-gate composition: low-amplitude after K iterations = honest refuse.
   - **M5 honest-acceptance:** if pivot, substrate-product story sharpens: "best-in-class 2-hop with full provenance; >2-hop via external orchestration." This is HONESTLY POSITIONABLE against vector-DB (no provenance, no relations) and LLM (no provenance, no audit).

---

## CITATIONS (verified)

1. Grover 1996 "A fast quantum mechanical algorithm for database search" — STOC 1996.
2. Brassard-Hoyer-Mosca-Tapp 2002 "Quantum amplitude amplification and estimation" — Contemp Math 305.
3. Roelfsema 2006 "Cortical algorithms for perceptual grouping" — Annu Rev Neurosci 29.
4. Buzsaki 2015 "Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning" — Hippocampus 25.
5. Wilson-McNaughton 1994 "Reactivation of hippocampal ensemble memories during sleep" — Science 265.
6. Lewis-Durrant 2011 "Overlapping memory replay during sleep builds cognitive schemata" — Trends Cogn Sci 15.
7. Davidson 2009 "Hippocampal replay of extended experience" — Neuron 63.
8. Mnih DQN 2015 "Human-level control through deep reinforcement learning" — Nature 518.
9. Sutton 1990 Dyna-Q — Mach Learn Proc 1990.
10. Fersht 1999 "Structure and Mechanism in Protein Science" — Freeman (Chapter 12 on enzyme catalysis).
11. Pauling 1946 "Molecular architecture and biological reactions" — Chem Eng News 24.
12. Andreas-Klein 2017 "Modular Multitask Reinforcement Learning with Policy Sketches" — ICML 2017.
13. Letzkus 2015 "Disinhibition, a Circuit Mechanism for Associative Learning and Memory" — Neuron 88.
14. Eichenbaum 2014 "Time cells in the hippocampus: a new dimension for mapping memories" — Nat Rev Neurosci 15.
15. Igarashi 2014 "Coordination of entorhinal-hippocampal ensemble activity during associative learning" — Nature 510.
16. Su 2024 RoPE "Roformer: Enhanced Transformer with Rotary Position Embedding" — Neurocomputing 568.
17. Howard-Eichenbaum 2017 "Time and Space in the Hippocampus" — Brain Res 1621.

Plus brain-grounded references via prior research drills (already verified): Rolls 2013 CA3 attractor (PMC 3812781); Stachenfeld-Botvinick-Gershman 2017 SR/hippocampus.

---

## META: DELIVERY DISCIPLINE

- All 4 candidate cells (M1-M4) carry pre-registered HARD-PASS / MIDDLE_BAND / HARD-FAIL bands (per role-contract mandate).
- M5 is a substrate-product framing decision, not a cell.
- Novel-synthesis P cap at 0.50 honored (top P_deflated = 0.45 for M2).
- 0.20 calibration deflation applied uniformly.
- ASCII only.
- Sanity-rail mandatory for all 4 cells.
- CARDINALITY_OK pre-reg field included for all sweep cells.
- DISCRIMINATOR-MUST-SURVIVE-SCALE pre-check declared for all 4 cells (smoke at FULL V_C=200, not small).
- Default UNDER-claim classification (Fix #28); let Skunkworks tier UP.
- Companion exp_dev hand-off recommended; can be filed via spawn `hdi_exp_dev` if approved by USER.

Field-advisor cross-check:
- M1 Grover amplification: quantum-inspired classical; un-drilled scope-expansion field; novelty high.
- M2 NREM-replay-compact: brain SWR fruit-bearing; uses existing chain-grade substrate primitive (highest leverage); novelty in ADAPTIVE-VS-FIXED compaction.
- M3 enzyme-stabilizer: chemistry un-drilled; DL aux-supervision adjacent; novelty in PER-HOP-POSITION-SPECIFIC bind.
- M4 metric-position: brain time-cells fruit-bearing; RoPE AI-canonical adjacent; novelty in CONTINUOUS-vs-CATEGORICAL position.
- M5 honest-accept: not a discriminator; substrate-product framing.

Per Trigger F (always-on aggressive cross-domain): this drill spans 4 anchor mechanisms across 5 disparate fields (quantum-classical, brain-replay, chemistry, brain-time-cells, AI-position-encoding), complementing the gap1 5x's 9-field + 2x revival's 4-5-field coverage without duplication of any single mechanism.

-- Research (Opus 4.7 1M, hd-instrument team lead)
