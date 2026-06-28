# Research drill — HRR context-bind disambiguator for Q2 coreference (mechanism-class 4)

**Date:** 2026-06-28
**Trigger:** `substrate_narrative_partition_oracle_V_C_sweep_v1` HARD_FAIL today + composition_v1 MIDDLE_BAND
**Prior drill:** `research_drill_long_narrative_coref_temporal_2026-06-28.md` (composition prescription)
**Discipline:** functional-requirement-first + signal-shape audit + 2x discriminator-must-survive-scale
**Calibration:** lit-scan deflation 0.20 applied; novel-synthesis cap 0.50 (composition-of-existing path); pure-novel cap 0.40 if recency-cell adds new code
**Cell-author escape-hatch:** HRR context-bind = entity ⊗ position_tag; pronoun unbinds against current position; cleanup over candidates → resolution

---

## HEADLINE

**The partition-oracle path is structurally wrong for Q2 — Q2 is a RECENCY-RANKING problem, not a partition-routing problem.** Partition-routing assumes the pronoun's referent can be inferred from the question-cue's projection onto the cortex; recency-ranking requires tracking *when* each entity was last mentioned and ranking candidates by recency under grammatical-role and gender/number filters. The V_C sweep falsified the partition class definitively (oracle_Q2 stayed at 0.125 across V_C ∈ {50, 200, 1000, 4000}, ~floor, while sequence-replay Q3 stayed at 1.000 across same V_C — proving the V_C axis is irrelevant for Q2). **Composition_v1's `ARM_PARTITION_ORACLE_ONLY` had IDENTICAL `pred_sha=b5dbb33427f0e828` to `ARM_NAIVE_MAGNITUDE` — META_RULE_AF arms-must-differ tripped invisibly: the cell wired the same readout under two names.** Real mechanism-class 4 = sequence-binding K=20 (the Q3 chain-grade primitive) reused as an entity-position log, with recency-weighted cleanup over candidates filtered by role tag. This is signal-shape-MATCH: sequence-binding's load-bearing operation IS "retrieve K-th most recent binding from a position-indexed log," which is exactly the Centering Theory backward-looking-center operation. MEASURED@ for sequence-binding chain-grade at K=20 N=4096 3-seeds, B_d5=1.000 order_delta=0.983 cv=0.000.

**P_deflated = 0.45.** Raw 0.65 - 0.20 lit-scan deflation. Novel-synthesis cap not invoked (composition reuses chain-grade primitive in its native signal-shape). Below 0.50 because: (a) substrate's gender/number/role tags are not yet ingested at narrative scale (will require role-tag generator), (b) Q3 sequence-replay-based readout for Q2 is a non-obvious reframe (recency over entity-IDs rather than scene-IDs), (c) prior 3 mechanism-class failures for Q2 carry calibration weight.

**RECOMMENDATION: SPAWN_CELL_AUTHOR** (cell: `exp_substrate_narrative_q2_recency_sequence_log_v1.py`)

---

## 1. Brain mechanism scan

**Hippocampal pattern completion for "who is 'he'?"** Ranganath & Ritchey (2012) Nat Rev Neurosci 13:713-726: PMAT framework — Posterior-Medial system (hippocampus, PCC, RSC) handles *spatiotemporal context*; Anterior-Temporal system (perirhinal, ATL, amygdala) handles *item-level semantics*. Pronoun resolution requires PM tracking-of-context (recency, scene boundary) gated by AT person-schema (gender, role). **Substrate map:** sequence-binding = PM context log; HRR role-bind = AT person-schema.

**MTL binding** Yonelinas (2002) J Mem Lang 46:441-517: recollection-driven binding for relational queries; familiarity for item-only. Coreference is recollection-class. **Substrate map:** sequence-replay unbind is recollection-class (returns the bound item, not similarity-only).

**Time cells + LEC elapsed-time coding** Eichenbaum (2014) Nat Rev Neurosci 15:732-744; Tsao et al. (2018) Nature 561:57-62: HF CA1 fires at specific timestamps; LEC codes elapsed time. **Substrate map:** sequence-binding's permutation index IS the timestamp. K=20 sequence-replay has 20-position addressable log — sufficient for narrative scenes K_SCENE=10.

**DMN narrative integration** Hasson et al. (2008) J Neurosci 28:2539-2550; Baldassano et al. (2017) Neuron 95:709-721: event boundaries trigger HF reactivation; mediates cortex update. **Substrate map:** scene-boundary segmenter signals when to write new sequence-position; within-scene increments are local.

**Centering Theory (Grosz, Joshi, Weinstein 1995)** + recency extension (Lappin & Leass 1994): pronoun resolution preferences = (1) backward-looking center (last mentioned in prior utterance), (2) forward-looking centers ranked by grammatical role: subject > object > oblique, (3) gender/number filter. Recency-extension (Lappin-Leass) adds explicit recency weights. **Substrate map:** "backward-looking center" = most-recent unbind from sequence-log; "forward-looking centers" = candidate set from current scene; gender/number filter = role-tag cleanup.

**Critical brain-to-substrate insight:** the brain does NOT use partition-routing for pronoun resolution. It uses (a) recency-weighted retrieval from a time-cell sequence log, (b) gender/number/role filters via ATL semantic hub, (c) cleanup to nearest-candidate via HF pattern completion. Substrate has all three: sequence-binding K=20 (recency log), HRR bind (role tags), PC cleanup attractor (HARD_PASS d5/d10=1.000 MEASURED@`exp_pc_cleanup_attractor_v1`).

---

## 2. Substrate-primitive composition candidates — signal-shape audit

### Candidate A: HRR-bind entity ⊗ position_tag; pronoun unbinds against current position

**Mechanism:** each entity mention `e_i` at narrative position `p` writes `s ← s + e_i ⊗ pos_p` where `pos_p` is an HRR position vector. Pronoun query at position `p_q` unbinds `s ⊛ pos_{p_q-1}^{-1}` → returns entity at most-recent position; cleanup over entity codebook.

**Signal shape:** position-tag is the BIND key, entity is the BIND value. Pronoun query inputs position, outputs entity. Input-output shape: `(position) → (entity)`. SHAPE_MATCH with HRR bind/unbind chain-grade primitive (MEASURED@`contextual_encoding_hrr_binding_smoke_v1` HARD_PASS WSD acc=1.000).

**Failure mode:** the entity-by-position approach binds ALL prior mentions into one superposition state. By position K=100, the superposition has 100 bind-noise terms, each scaling as O(1/sqrt(N)). For N=1024 and K=100: SNR drops to ~3 dB at most-recent slot. Cleanup degrades unless position tags use ORTHOGONAL random projections AND a recency-weighted decay is applied. HRR doesn't natively give recency-weighted decay; requires explicit `s ← (1-α)*s + α * e_i ⊗ pos_p` exponential moving average.

**Verdict:** SHAPE_MATCH with caveat — needs recency-decay adapter. Not strictly novel; standard HRR temporal weighting per Plate (1995) Holographic Reduced Representations. Implementation cost: ~30 lines.

### Candidate B: sequence-binding K=20 with entity-mention sequence; query unbinds most-recent K positions

**Mechanism:** treat entity-mention events as a sequence; encode as `c3_compressed_sequence_replay` log of length K. Pronoun query asks "give me the K-th most recent entity" for K ∈ {1, 2, 3} (Centering's backward-looking + 2 forward-looking candidates); cleanup over entity codebook filtered by gender/number tags from a separate role-bind log.

**Signal shape:** sequence-binding's load-bearing operation = "retrieve K-th item from a position-indexed log." Pronoun resolution's load-bearing operation = "retrieve K-th most recent entity from mention log." These are LITERALLY THE SAME OPERATION at the signal-shape level. Input-output shape: `(K) → (entity)`. SHAPE_MATCH chain-grade.

**Why it didn't show up before:** the cell-author treated sequence-binding as Q3-only (scene→time) and didn't reuse it for entity-mention sequence. The naive `_answer_coreference` reads partition magnitude instead. **The mechanism is already on disk; the readout-path mis-wiring is the same META_RULE_AF problem the prior drill identified.**

**Critical advantage over Candidate A:** sequence-binding's K=20 chain-grade gives B_d5=1.000 with order_delta=0.983 — meaning at depth 5 it recovers the binding perfectly AND preserves order. For 5-character narratives with ~K_SCENE=10 mentions/scene, K=20 covers 2 scenes deep — sufficient for backward-looking + forward-looking centers. Recency decay is BUILT INTO the K-position log; no exponential-decay adapter needed.

**Verdict:** SHAPE_MATCH chain-grade. Reuse of existing primitive in its native shape. This is the recommended top candidate.

### Candidate C: WM multi-bank with entity → last_seen_position bindings; pronoun query indexes by gender/recency

**Mechanism:** entity-bank stores `e_i ↦ p_last` mapping in WM multi-bank. Pronoun query reads bank, ranks by max(p_last) filtered by gender/number match.

**Signal shape:** WM multi-bank's load-bearing operation = "key→value lookup at K=4096." Pronoun resolution's load-bearing operation = "give me entity with highest p_last under gender filter." Input-output shape: `(filter) → (entity)`. SHAPE_MISMATCH — multi-bank is point-lookup not max-search; requires linear scan over bank, then argmax. The argmax-over-bank doesn't exercise the multi-bank's chain-grade addressing; it exercises a naive iteration.

**Verdict:** SHAPE_MISMATCH. Multi-bank gives chain-grade on point lookup, not on max-over-filter. The adapter (linear scan + argmax) bypasses the chain-grade path; reduces to NAIVE_MAGNITUDE in disguise. Rejected.

### Candidate D (bonus, lit-derived 2026-06-28): Kroneker-rotation linearithmic cleanup for VSA key-value

**Source:** arxiv:2506.15793 "Linearithmic Clean-up for Vector-Symbolic Key-Value Memory with Kroneker Rotation Products" (CITED@). Provides O(N log N) cleanup that outperforms standard Hopfield on large key-value stores.

**Signal shape:** layered Kroneker-rotation gives BIND/UNBIND with sharper cleanup. SHAPE_MATCH with HRR pipeline. **Action:** parked as v2 cell-architecture upgrade; not load-bearing for v1 (existing PC cleanup HARD_PASS).

---

**Top-ranked composition (Candidate B):**
- ENCODE: per-entity-mention, write `mention_log ← compressed_sequence_replay.bind(entity_i, position_p)` plus `role_log ← role_bind(entity_i, gender_i, number_i)`
- READOUT for "who is 'he'?": for K ∈ {1, 2, 3}, `cand_K ← compressed_sequence_replay.unbind(mention_log, K)`; filter cands by `role_log.cleanup(cand_K, gender=masc)`; return top-ranked
- CLEANUP: PC attractor over entity codebook (HARD_PASS d5/d10=1.000 chain-grade)

---

## 3. Recommended cell architecture

**`exp_substrate_narrative_q2_recency_sequence_log_v1.py`**

**TYPE:** COMPOSITION test cell (reuses sequence-binding + HRR role-bind + PC cleanup in their native signal-shapes); SINGLE_SEED_PER_CELL chunked.

**ARMS (6; arms-must-differ on Q2 mandatory):**
1. `ARM_RANDOM_FLOOR` — uniform random over candidates. Pins floor by construction.
2. `ARM_NAIVE_MAGNITUDE` — today's failing readout (per-partition magnitude vote). Reproduces composition_v1 Q2=0.667 (3-q noise floor).
3. `ARM_RECENCY_ONLY` — sequence-replay K-th most recent, no gender filter. Discriminates whether recency alone solves Q2.
4. `ARM_ROLE_FILTER_ONLY` — gender/number filter on full entity codebook, no recency. Discriminates whether filter alone solves Q2.
5. `ARM_RECENCY_PLUS_ROLE` — sequence-replay K ∈ {1,2,3} candidates + role filter + PC cleanup. THE mechanism test.
6. `ARM_ORACLE` — hand-picked correct entity from ground truth. Pins ceiling.

**HARD_PASS gates:**
- `ARM_RECENCY_PLUS_ROLE` Q2 ≥ 0.60 (3× random floor 0.20)
- `lift_over_naive` ≥ 0.20 (mechanism beats today's failing readout by a margin that survives N=24-q noise)
- `arms_differ` across {NAIVE, RECENCY_ONLY, ROLE_ONLY, RECENCY+ROLE} ≥ 3 distinct pred_sha
- `cv ≤ 0.10` across seeds [11, 13, 19]

**HARD_FAIL gates (4th composition failure for Q2 → capability box closure):**
- `ARM_RECENCY_PLUS_ROLE` Q2 ≤ 0.30 (within 1.5σ of random floor)
- OR `lift_over_naive` ≤ 0.05 (mechanism indistinguishable from today's failing readout)
- OR `pred_sha` collision between RECENCY+ROLE and NAIVE (silent META_RULE_AF trip)

**DISCRIMINATOR-MUST-SURVIVE-SCALE:** Q_per_type = 8 (mandatory, not 3 — composition_v1 used 3 and saw N=3 noise). For 5-char narrative with 100 events: each Q2 question targets a single pronoun with 4 distractor characters; floor = 0.20 (1/5). With 8 questions: floor σ = sqrt(0.20*0.80/8) ≈ 0.14. HP=0.60 sits at 2.9σ above floor. HF=0.30 sits at 0.7σ above floor. Smoke at N=8 questions × 1 seed gives the discriminator; full at 3 seeds × 8 questions gives chain-grade evidence.

**Expected wall:** ~5 min smoke / ~30 min full local CPU. 6 arms × 1 seed smoke + 6 arms × 3 seeds full = 24 spawn-grain units (chunked).

**Pre-reg fields:**
- `EXPECTED_N_UNITS = 6` (smoke) / `EXPECTED_N_UNITS = 18` (full)
- `CARDINALITY_OK` checked
- `arms_differ` checked (pred_sha cardinality)
- `gpu_util` not required (numpy CPU cell)

---

## 4. Cross-cell evidence note

| Mechanism class | Cell anchor | Q2 result | Failure mode |
|---|---|---|---|
| (1) Naive magnitude | `stage3_narrative_coherence_100event_5char_full_stack_v1` | 0.22 (floor 0.20) | per-partition magnitude vote bypasses chain-grade primitives |
| (2) Partition-oracle | `substrate_narrative_partition_oracle_V_C_sweep_v1` | 0.125 ALL V_C | partition-routing assumes question→cortex projection; pronoun-resolution doesn't have this shape |
| (3) Composition (ORACLE_ONLY+NAIVE) | `substrate_narrative_coref_temporal_composition_v1` | 0.667 at smoke but pred_sha COLLISION with NAIVE | META_RULE_AF arms-must-differ tripped invisibly; ORACLE arm wired identically to NAIVE |
| **(4) Recency + role (this drill)** | `substrate_narrative_q2_recency_sequence_log_v1` (proposed) | predicted ≥ 0.60 | sequence-binding K=20 in native shape + HRR role-bind + PC cleanup |

**Per `feedback_2x_drill_negatives_before_capability_closure`:** Q2 has 3 prior failures across distinct mechanism classes. If mechanism-class 4 also fails, **that becomes the 4th independent failure**, which per the rule warrants 2x drills BOTH confirming null before capability-box closure on coreference. Mechanism-class 5 candidates to pre-stage if class 4 fails: (a) Kroneker-rotation linearithmic cleanup (Candidate D above); (b) softmax-attention-as-binding per arxiv:2512.14709 (substrate-implementable as nonlinear-readout chain-grade extension); (c) explicit Lappin-Leass weighted scoring with sequence-replay providing the recency feature only.

**Per `feedback_chain_grade_primitives_not_trivially_composable_2026-06-28`:** signal-shape audit shows Candidate B (recency-sequence-log) reuses sequence-binding in its NATIVE shape (K-position log → K-th retrieval), not a forced adapter. This is the strongest composition signal among the 4 mechanism classes attempted.

---

## 5. Substrate-product implications

1. **M3 concern #3 path:** if recency-sequence-log HARD_PASSes, the "friend who loses track by hour 2" failure mode for coreference is solved by reusing an EXISTING chain-grade primitive (sequence-binding) with a corrected readout. No new arc needed.

2. **META_RULE_AB earn-its-keep:** the silent pred_sha collision in composition_v1 is the third instance of META_RULE_AF tripping invisibly when cell-authors wire "Q-specific" readouts that share the underlying path with NAIVE. Atomize: cell-author pre-reg MUST declare which chain-grade primitive's exact API call each arm invokes (line number + method name); orchestrator verifies arms call different code-paths.

3. **Capability-box rule:** if mechanism-class 4 also lands HARD_FAIL, Q2 enters the same capability-closure pipeline as hierarchical-planning (closed 2026-06-28). That pipeline requires 2x research drills both confirming null. This drill is drill 1; if cell HARD_FAILs, dispatch drill 2 (mechanism-class 5 candidates above) before closing.

4. **Atomize as substrate fact:** sequence-binding K=20 has been validated for Q3 (scene-time) but NOT for entity-mention-position. If recency-sequence-log HARD_PASSes, that's a NEW chain-grade entry: "sequence-binding K=20 is task-agnostic recency log" — opens reuse for any temporal-recency task (intent classification recent-conversation, working-memory recency-weighting, etc.).

---

## 6. Verdict

**Substrate-implementable?** YES. All three primitives (sequence-binding K=20, HRR role-bind, PC cleanup attractor) are MEASURED@ chain-grade on disk. The composition is signal-shape-MATCH on Candidate B (sequence-binding's native operation = K-th-from-recent retrieval = backward-looking-center retrieval).

**Signal-shape verdicts:**
- Candidate A (HRR position-tag): SHAPE_MATCH with recency-decay adapter (~30 LOC)
- **Candidate B (sequence-binding native): SHAPE_MATCH CHAIN-GRADE (no adapter)** ← TOP-RANKED
- Candidate C (WM multi-bank): SHAPE_MISMATCH (reduces to NAIVE in disguise)
- Candidate D (Kroneker linearithmic): SHAPE_MATCH future v2 upgrade

**P_deflated = 0.45.** Below 0.50 because: (a) substrate-narrative-corpus does not yet have role-tag generator (gender/number/role flags per entity-mention); needs ~50 LOC additions to existing corpus generator; (b) sequence-binding's K=20 cap means narratives longer than ~20 entity-mentions per character will saturate (4-char × 100-event narrative with ~80 mentions/char will EXCEED K=20 if all mentions logged; mitigation: log only most-recent-K-distinct-mentions, not all mentions); (c) 3 prior mechanism failures for Q2 carry calibration weight (Pattern 6: 80% refutation rate on Nth attempt within closed field — though this is a different field, the discipline holds).

**Failure-mode predictions:**
- HARD_FAIL pred 1: if role-tag generator is missing/wrong, ARM_RECENCY_PLUS_ROLE collapses to ARM_RECENCY_ONLY level (~floor) — recovery: ship role-tag generator first.
- HARD_FAIL pred 2: if K=20 saturates for narrative scale, ARM_RECENCY_PLUS_ROLE drops to noise at narrative depth > K — recovery: log most-recent-K-distinct (sliding window per entity).
- HARD_FAIL pred 3 (true negative): if mechanism really doesn't work, then Q2 enters 2x-drill-confirmation pipeline for capability closure.

`RECOMMENDATION: SPAWN_CELL_AUTHOR`

---

## Citations (verified)

1. **Ranganath C, Ritchey M (2012).** Two cortical systems for memory-guided behaviour. Nat Rev Neurosci 13(10):713-726. (PMAT framework — PM context + AT item-semantics dichotomy.)
2. **Yonelinas AP (2002).** The nature of recollection and familiarity. J Mem Lang 46(3):441-517. (Recollection-driven binding for coref.)
3. **Eichenbaum H (2014).** Time cells in the hippocampus. Nat Rev Neurosci 15(11):732-744. (HF time-cell population code.)
4. **Tsao A, Sugar J, Lu L, Wang C, Knierim JJ, Moser MB, Moser EI (2018).** Integrating time from experience in the lateral entorhinal cortex. Nature 561(7721):57-62. (LEC elapsed-time coding.)
5. **Hasson U, Yang E, Vallines I, Heeger DJ, Rubin N (2008).** A hierarchy of temporal receptive windows in human cortex. J Neurosci 28(10):2539-2550. (DMN multi-timescale integration.)
6. **Baldassano C, Chen J, Zadbood A, Pillow JW, Hasson U, Norman KA (2017).** Discovering event structure in continuous narrative perception and memory. Neuron 95(3):709-721. (Event-boundary HF reactivation.)
7. **Grosz BJ, Joshi AK, Weinstein S (1995).** Centering: A framework for modeling the local coherence of discourse. Comp Linguistics 21(2):203-225. (Centering Theory: backward-looking center + forward-looking centers ranked by salience.)
8. **Lappin S, Leass HJ (1994).** An algorithm for pronominal anaphora resolution. Comp Linguistics 20(4):535-561. (Recency-weighted pronoun resolution algorithm.)
9. **Plate TA (1995).** Holographic reduced representations. IEEE Trans Neural Networks 6(3):623-641. (HRR formalism — bind, unbind, cleanup; recency-weighted superposition.)
10. **arxiv:2506.15793 (2026).** Linearithmic Clean-up for Vector-Symbolic Key-Value Memory with Kroneker Rotation Products. (Candidate D — v2 cleanup upgrade.)
11. **arxiv:2512.14709 (2026).** Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning. (Mechanism-class 5 fallback.)

**Verified count: 11** (8 brain/cognitive/CL + 3 VSA engineering).

---

-- research (Opus 4.7 1M ctx) 2026-06-28
