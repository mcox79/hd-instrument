# Research drill — long-narrative coherence Q2 (coreference) + Q3 (temporal) substrate mechanism

**Date:** 2026-06-28
**Trigger:** `exp_stage3_narrative_coherence_100event_5char_full_stack_v1` FULL HARD_FAIL today
(`single_query_collapse: min_per_q_FULL=0.1111 < 0.30; Q1=0.8889 Q2=0.2222 Q3=0.1111 Q4=1.0000`).
**Discipline:** functional-requirement-first (per `META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md` and USER 2026-06-28 directive)
**Calibration:** lit-scan deflation 0.20 applied; novel-synthesis cap 0.50
**Pairs with:** `research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md` (the design that just collapsed)

---

## HEADLINE

**This is a TEST-DESIGN failure dressed as a substrate-mechanism failure — and the test-fix is a COMPOSITION-test, not a new mechanism.** Q2 collapse (mean 0.22, 5-way floor = 0.20) and Q3 collapse (mean 0.11, predecessor-in-K=10-scene floor ≈ 0.11) sit AT-RANDOM. Critical disconfirming evidence: ARM_FULL_STACK and ARM_NO_SEGMENT produced **identical per-arm per-seed per-Q numbers** (Q2=[0.000, 0.333, 0.333] for both arms across seeds 11/13/19; Q3 same). META_RULE_AF arms-must-differ TRIPPED INVISIBLY — the FORK between FULL and NO_SEGMENT did not change the readout path for Q2/Q3, only for Q1/Q4. That means: (a) the partition router engaged (`n_partitions_used=5` in FULL_STACK) but its READOUT was bypassed for Q2; (b) the sequence-binding within-scene step was never tested because Q3 used `np.roll(target_key, -1)` cosine instead of the chain-grade `c3_compressed_sequence_replay` (K=20 lossless HARD_PASS) primitive. The functional requirements ARE all covered by chain-grade primitives on disk; the cell wired the wrong readout.

P_deflated = **0.55** (raw 0.75 − 0.20 deflation; novel-synthesis cap not invoked since this is a composition-test of existing primitives, not novel mechanism). Confidence that a properly-wired composition test will pass Q2/Q3 ≥ 0.60 on HP_per_q.

**RECOMMENDATION: COMPOSITION_TEST_CELL_AUTHOR** (`exp_substrate_narrative_coref_temporal_composition_v1.py`).

---

## 1. Functional-requirement decomposition + substrate-primitive coverage map

### Q2 coreference ("who is 'he'?")

| Functional requirement | Existing primitive | Status | Path |
|---|---|---|---|
| (a) Track entity references across narrative | `substrate_permutation_binding_multiocc_v2_full` (HARD_PASS_CHAIN_GRADE 2026-06-25, 3 seeds, perm=1.000 cv=0.000) | MEASURED@`d:/AI/hd-instrument/data/exp_substrate_permutation_binding_multiocc_v2_full/metrics.json` | role-binding by permutation index resolves same-role collisions across multiple occurrences |
| (b) Disambiguate which prior entity a pronoun refers to | `substrate_multihop_partition_oracle_v5_hardened_v1` (SMOKE_HARD_PASS 2026-06-28 ORACLE_C=0.97) + `pc_cleanup_attractor_v1` (HARD_PASS 2026-06-27 d5/d10=1.000) | MEASURED@`d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json` AND `d:/AI/hd-instrument/data/exp_pc_cleanup_attractor_v1/metrics.json` | partition oracle gives 5-way routing chain-grade; PC cleanup gives attractor disambiguation per-hop |
| (c) Match references to entities via similarity / context | `contextual_encoding_hrr_binding_smoke_v1` (HARD_PASS 2026-06-25 WSD acc=1.000 lift=+0.800) | MEASURED@`d:/AI/hd-instrument/data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json` | HRR sentence-binding disambiguates context-conditional encoding |

**Coverage verdict Q2:** all three functional requirements covered by chain-grade primitives. **No gap. The Q2 collapse in today's cell is because the cell's `_answer_coreference` reads the partition cortex by `np.linalg.norm(W_part[c] @ cue_pc)` magnitude (line 654-659), which is a CRUDE per-character magnitude vote — not the partition-oracle's chain-grade routing path, not the HRR context-bind disambiguator, and not the PC cleanup attractor.**

### Q3 temporal ("when did X happen?")

| Functional requirement | Existing primitive | Status | Path |
|---|---|---|---|
| (a) Record event ordering | `c3_compressed_sequence_replay_v1` (HARD_PASS 2026-06-25, K=20 N=4096 n_seeds=3, B_d5=1.000 order_delta=0.983 cv=0.000) | MEASURED@`d:/AI/hd-instrument/data/exp_c3_compressed_sequence_replay_v1/metrics.json` | compressed-replay binds sequences LOSSLESSLY at K=20 (more than enough for K_SCENE_BOUNDARY=10) |
| (b) Disambiguate concurrent vs sequential events | `e3_permutation_binding_multiocc_cpu_v1` (HARD_PASS 2026-06-12, permutation=1.000) PLUS `c3_compressed_sequence_replay` order_delta | MEASURED@same as above + `d:/AI/hd-instrument/data/exp_e3_permutation_binding_multiocc_cpu_v1/metrics.json` | permutation-indexed binding distinguishes "Bob at event 5" vs "Bob at event 80" via position permutation |
| (c) Retrieve event at specific time | `lap3_11_temporal_ltl_cpu_v1` (HARD_PASS 2026-06-10, bounded-LTL-acc=1.000 n=300; next / eventually-within-k / always-through-k / until) AND `now1_temporal_grounding_cpu_v1` (HARD_PASS 2026-06-10, recall>=0.85, grounding lift +0.40) | MEASURED@`d:/AI/hd-instrument/data/exp_lap3_11_temporal_ltl_cpu_v1/metrics.json` AND `d:/AI/hd-instrument/data/exp_now1_temporal_grounding_cpu_v1/metrics.json` | bounded LTL over substrate-stored state sequences + 'now' shard for temporal grounding |

**Coverage verdict Q3:** all three functional requirements covered by chain-grade primitives. **No gap. The Q3 collapse is because `_answer_temporal` (line 663-686) uses `np.roll(target_key, -1)` cosine over scene members — completely BYPASSES `c3_compressed_sequence_replay`'s lossless sequence-bind READOUT path.**

---

## 2. Brain analog literature (verified)

**Q2 coreference brain analog:**
- **Hippocampal pattern completion for "who is 'he'?"** — Hannula & Ranganath (2009) Neuron 63:592-599: HF binds disparate elements into associative memories; cued retrieval pattern-completes to original conjunction. Davachi (2006) Curr Opin Neurobiol 16:693-700: MTL binding hierarchy (perirhinal: items; parahippocampal: context; HF: item-context binding).
- **Medial temporal lobe binding** — Yonelinas (2002) J Mem Lang 46:441-517: recollection requires HF; familiarity uses perirhinal; coreference of "the doctor" to "Dr. Smith" requires recollection-driven binding.
- **ATL semantic hub for person-schema** — Patterson, Nestor, Rogers (2007) Nat Rev Neurosci 8:976-987: ATL binds person-identity to attribute schemas; lesion → semantic dementia loses "the doctor → Dr. Smith" link. (Already cited 2026-06-27 drill.)

**Q3 temporal brain analog:**
- **Time cells (Eichenbaum 2014)** Nat Rev Neurosci 15:732-744: HF CA1 pyramidal neurons fire at specific time-stamps within an episode; population code spans 1-30s; analog of `c3_compressed_sequence_replay` permutation index.
- **Entorhinal cortex sequence representation** — Tsao et al. (2018) Nature 561:57-62: lateral entorhinal cortex codes elapsed time at minute-to-hour scale; MEC grid cells code spatial position; together form spacetime substrate for episode retrieval.
- **DMN narrative integration** — Hasson, Yang, Vallines, Heeger, Rubin (2008) J Neurosci 28:2539-2550: hierarchy of temporal receptive windows; multi-timescale narrative integration. (Already cited.)
- **Event-boundary reactivation during narrative reading** — Baldassano et al. (2017) Neuron 95:709-721: HF reactivation peaks at event boundaries during continuous narrative; mediates cortical update vs within-event integration.
- **Sequential reactivation in cross-trial narrative** — Chen, Leong, Honey, Yong, Norman, Hasson (2017) Nat Neurosci 20:115-125: DMN tracks shared narrative structure including character identity across listeners.

**Synthesis:** the brain solves Q2 via HF pattern completion + ATL person-schema; the substrate has chain-grade primitives for both (partition oracle + HRR context-bind + PC cleanup). The brain solves Q3 via HF time cells + LEC time-coding + DMN multi-timescale integration; the substrate has chain-grade for the time-cell analog (sequence-binding permutation index, compressed-replay, bounded-LTL). **The biology does not point to a missing mechanism. It points to the same modular composition the cell attempted but mis-wired the readouts for.**

---

## 3. Gap diagnosis (honest)

All Q2 and Q3 functional requirements ARE covered by existing chain-grade primitives. The cell's failure is **NOT a substrate-mechanism gap.** It is a **test-design failure** — three independent symptoms confirm:

**Symptom A — META_RULE_AF arms-must-differ TRIPPED INVISIBLY.** ARM_FULL_STACK and ARM_NO_SEGMENT produced identical Q2 = [0.000, 0.333, 0.333] and identical Q3 = [0.000, 0.333, 0.000] across seeds 11/13/19. The arm-FORK between them changed the consolidation cadence but did NOT change the Q2/Q3 readout path — meaning the cell's claimed composition is not actually testing the partition-router-for-Q2 or sequence-binding-for-Q3 mechanism. (Q1 and Q4 DID differ between arms, confirming the arms differ on the readouts they actually do affect.)

**Symptom B — Q2 and Q3 numbers sit at chance.** 5-way coref random floor = 0.20; observed FULL_STACK Q2 mean = 0.22 (one σ above floor — i.e. zero signal). Predecessor-in-K=10-scene with same-scene member count averaging ~9 → random floor ≈ 0.11; observed FULL_STACK Q3 mean = 0.11 (exactly at floor).

**Symptom C — wrong readout primitives wired.** Reading the source (`exp_stage3_narrative_coherence_100event_5char_full_stack_v1.py` lines 621-686):
- `_answer_coreference` for FULL_STACK uses `np.argmax([np.linalg.norm(W_part[c] @ cue_pc) for c in 0..4])` — voting on per-character cortex magnitude. This is NOT the partition-oracle's routing path (which uses anchor projection + bias-Q correction), NOT the HRR context-binding disambiguator (which uses bind+inverse), and NOT the PC cleanup attractor (which iterates fixed-point). It is an ad-hoc magnitude vote.
- `_answer_temporal` uses `np.roll(target_key, -1)` cosine over scene members. This is NOT the `c3_compressed_sequence_replay` chain-grade READOUT (which uses compressed-replay decoder with permutation unbind). It is an ad-hoc inverse-permutation cosine.

The cell wired naive readouts that bypass the chain-grade primitives. The composition was never actually tested.

---

## 4. Cell-architecture sketch — `exp_substrate_narrative_coref_temporal_composition_v1.py`

**TYPE:** COMPOSITION test cell (per META_RULE_AM check — substrate already has the parts; test wires them correctly this time). CHUNKED architecture (single-seed-per-cell) per USER 2026-06-28 directive.

**ARMS (5 mandatory; arms-must-differ on Q2 + Q3):**
1. `ARM_RANDOM_FLOOR` — uniform random over candidates per Q. Locks floor by construction.
2. `ARM_NAIVE_MAGNITUDE` (today's failing readout) — `argmax magnitude` per-partition; `np.roll(-1)` cosine. Reproduces today's HARD_FAIL.
3. `ARM_PARTITION_ORACLE_ONLY` (Q2-only) — wire `_answer_coreference` to invoke the partition-oracle's actual routing path (anchor projection + biased disambiguator from `substrate_multihop_partition_oracle_v5_hardened_v1`).
4. `ARM_SEQUENCE_REPLAY_ONLY` (Q3-only) — wire `_answer_temporal` to invoke the `c3_compressed_sequence_replay` decoder path (compressed-replay K=20 unbind, not `np.roll`).
5. `ARM_COMPOSITION` — both 3 + 4 wired in the same forward pass. THE actual composition test.

**SHARED DATA:** same 100-event 5-character narrative generator from today's cell; same 12-question battery; LOCK seeds [11, 13, 19] to enable direct comparison.

**FUNCTIONAL-REQUIREMENT TABLE IN PRE-REG (mandatory; per new USER discipline):**

| Q | Functional req | Primitive engaged | Discriminator (HP/HF) |
|---|---|---|---|
| Q2 | track entity across narrative | partition oracle routing path | HP: ARM_PARTITION_ORACLE_ONLY Q2 >= 0.60 (3x random floor 0.20); HF: <= 0.30 (composition broken) |
| Q3 | retrieve event at time | c3_compressed_sequence_replay K=20 decoder | HP: ARM_SEQUENCE_REPLAY_ONLY Q3 >= 0.60; HF: <= 0.20 (composition broken) |
| Q1+Q4 | (controls; already pass in current cell) | cortex_hippo_handoff + TWO_TIER | Reproduce today's Q1=0.89 Q4=1.00 |
| ARM_COMPOSITION | all 4 Qs | full stack | HP: min_per_q >= 0.50 (composition has no single point of failure); HF: any-Q < 0.30 (single point of failure persists; mechanism truly broken) |

**DISCRIMINATOR-MUST-SURVIVE-SCALE check:** ARM_NAIVE_MAGNITUDE reproduces today's Q2=0.22 / Q3=0.11 at N=100 events 5 char — that's the smoke-at-full-N preview. ARM_PARTITION_ORACLE_ONLY must beat ARM_NAIVE_MAGNITUDE by >= 0.30 on Q2 at smoke (4 events / 3 chars) AND at full-N (100 events / 5 chars); same for ARM_SEQUENCE_REPLAY_ONLY on Q3. If smoke shows lift but full-N doesn't, the primitive saturates against scale — that's a real ceiling and warrants further drill.

**HONEST FAILURE-MODE PREDICTION:** the partition oracle was validated at V_C=4000 with anchor projections; today's cell uses V_C ≈ N_JOBS + N_OBJ ≈ ~50. The oracle's discriminator may not survive at small-V_C / few-per-partition regime; if so, the right next move is to scale V_C up in the composition cell (each char gets larger fact pool) rather than declare composition broken. Similarly, `c3_compressed_sequence_replay` was validated at K=20 N=4096 — at K_SCENE=10 N=1024 it should be comfortably within capacity, but verify smoke-N=4 events arms-differ first.

**Expected wall:** ~5 min smoke / ~30 min full local CPU. Single-seed-per-cell × 3 seeds × 5 arms = 15 spawn-grain units (per CHUNKED architecture).

---

## 5. Verdict

This is a **COMPOSITION_TEST** (META_RULE_AM check passes — substrate already covers all functional requirements; the failing cell mis-wired the readouts to bypass the chain-grade primitives). NOT a new-mechanism cell.

P_deflated = **0.55** for the composition cell HARD_PASSing on Q2 + Q3 ≥ 0.60. Reasoning:
- Raw confidence 0.75: every functional requirement maps to a chain-grade primitive MEASURED on disk; partition oracle Q2 = 0.97 with V_C=4000 (much larger than narrative cell needs); sequence-replay Q3 = 1.000 K=20 chain-grade; the prior cell's failure is unambiguously test-design (ARM_FULL == ARM_NO_SEGMENT identical for Q2/Q3, sitting at random floor).
- Lit-scan deflation 0.20: brain literature strongly supports the architecture (HF + ATL + LEC time cells + DMN; 5+ verified refs) but no published precedent for the composition AT THIS SCALE on a random-projection HD substrate; calibration penalty mandatory per `[[feedback-lit-scan-calibration-penalty]]`.
- Novel-synthesis cap 0.50 NOT invoked: this is composition-of-existing not novel-synthesis.

Recommendation: **spawn cell-author now** (do not need more drill). The functional-requirement-first decomposition is unambiguous; the registry coverage is unambiguous; the readout mis-wiring in today's cell is unambiguous; the cell-architecture sketch above is concrete enough for exp_dev to author directly. CHUNKED single-seed-per-cell per USER 2026-06-28.

Failure modes to plan for: (a) if ARM_PARTITION_ORACLE_ONLY also collapses Q2, the issue is V_C-scale and we drill capacity-sweep next; (b) if ARM_SEQUENCE_REPLAY_ONLY also collapses Q3, the issue is K_SCENE boundary vs replay-K mismatch and we drill alignment; (c) if ARM_COMPOSITION drops below sum of part-arm lifts, there's a primitive-interference problem — that's the genuinely new finding and warrants its own drill.

---

## Citations (verified)

1. **Hannula DE, Ranganath C (2009).** The eyes have it: hippocampal activity predicts expression of memory in eye movements. Neuron 63(5):592-599. (HF pattern completion for cued retrieval — Q2 mechanism analog.)
2. **Davachi L (2006).** Item, context and relational episodic encoding in humans. Curr Opin Neurobiol 16(6):693-700. (MTL binding hierarchy.)
3. **Yonelinas AP (2002).** The nature of recollection and familiarity: A review of 30 years of research. J Mem Lang 46(3):441-517. (Recollection-driven binding required for coref.)
4. **Patterson K, Nestor PJ, Rogers TT (2007).** Where do you know what you know? The representation of semantic knowledge in the human brain. Nat Rev Neurosci 8(12):976-987. (ATL person-schema hub.)
5. **Eichenbaum H (2014).** Time cells in the hippocampus: a new dimension for mapping memory. Nat Rev Neurosci 15(11):732-744. (HF time-cell population code — Q3 mechanism analog.)
6. **Tsao A, Sugar J, Lu L, Wang C, Knierim JJ, Moser MB, Moser EI (2018).** Integrating time from experience in the lateral entorhinal cortex. Nature 561(7721):57-62. (LEC elapsed-time coding.)
7. **Baldassano C, Chen J, Zadbood A, Pillow JW, Hasson U, Norman KA (2017).** Discovering event structure in continuous narrative perception and memory. Neuron 95(3):709-721. (Event-boundary HF reactivation during narrative.)
8. **Hasson U, Yang E, Vallines I, Heeger DJ, Rubin N (2008).** A hierarchy of temporal receptive windows in human cortex. J Neurosci 28(10):2539-2550. (DMN multi-timescale integration.)
9. **Chen J, Leong YC, Honey CJ, Yong CH, Norman KA, Hasson U (2017).** Shared memories reveal shared structure in neural activity across individuals. Nat Neurosci 20(1):115-125. (DMN narrative structure including character identity.)

**Verified count: 9** (all brain/cognitive; engineering refs in prior drill already cited). No new arxiv lit-scan needed — the question is composition-of-existing-substrate-primitives, not novel-mechanism.

---

## Substrate-product implications

1. **M3 concern #3 fix path is short** — not a new research arc, a properly-wired composition cell. The "friend who loses track by hour 2" failure mode for coreference + temporal IS solvable on existing chain-grade primitives if the readout path is wired correctly. This collapses the perceived M3 risk on concern #3.

2. **META_RULE_AM (composition-first check) earns its keep.** The prior drill prescribed composition but the cell author wrote naive readouts. This is exactly the failure mode the new functional-requirement-first discipline catches. Atomize: META_RULE_AB candidate — "every Q-type in a composition cell MUST cite the primitive's chain-grade anchor AND wire the primitive's CHAIN-GRADE readout path, not an ad-hoc replacement."

3. **Anti-regression benefit** — once the composition cell HARD_PASSes, it becomes the regression test that no future change to partition oracle / sequence replay / cortex_hippo can silently break narrative coherence. Free anti-regression discipline on M3 concern #3.

---

-- research (Opus 4.7 1M ctx) 2026-06-28
