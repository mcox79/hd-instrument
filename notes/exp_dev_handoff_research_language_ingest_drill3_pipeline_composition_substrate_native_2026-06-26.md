# exp_dev hand-off -- research: language ingest drill 3 (pipeline + composition + new infrastructure)

**Filed by:** research (Opus)
**Filed at:** 2026-06-26
**Trigger:** USER directive to formalize Path C + start substrate-native language ingest. Companion to research note `notes/research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next emergency cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and lit-evidence + chain-grade primitive backing. Cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, cheapest decisive, ships immediately)

- **Pointer:** `lang_ingest_vocab_bigram_meta_m7_v1`
- **Substrate-product reading:** Phase-1 substrate-native language ingest: build deterministic-hash bipolar token codebook on text8 top-V_TOK=8192 tokens; ingest text8 stream as bigram ordered-pairs via SequenceMatrix S; route by token-hash to N_PARTITIONS=64 partitioned S matrices; cleanup via Codebook nearest-neighbor; eval next-token prediction via META_M7-compliant top1+top5+T-calibrated BPC harness. 4-arm comparison: ARM_A_NULL_UNIGRAM / ARM_B_BIGRAM_HRR / ARM_C_TRIGRAM_HRR / ARM_D_CHAR_TRIGRAM_BIGRAM. The decisive question: does substrate-native Path C ingest reproduce the n1_v3 bigram-gap-closure signal (top1=0.4455 vs unigram 0.2757; +61.6% relative lift) on text8 with NO Pythia/MiniLM/word2vec encoder? 8 of 9 pipeline stages have chain-grade primitive backing (char_trigram_encoder + binding + bundling + SequenceMatrix + Codebook + refuse_gate + continual + multi_hop); the 9th is the NEW META_M7 LM eval harness which is THE measurement methodology fix from 2026-06-23.
- **Tier hint:** likely MIDDLE_BAND at first land (novel-on-substrate Path C composition); chain-grade-eligible if HARD_PASS replicates with cv <= 0.05 and ARM_A_NULL_UNIGRAM HARD_FAILS (discriminator visible).
- **Why now:** L2-vision-critical (glass-box LM is the unlock); 8 of 9 primitives already chain-grade; compute cheap (~3-4 CPU-hr remote_cpu_queue); decisive single-cell test against the n1_v3 anchor.
- **P_deflated:** 0.30 (cap on novel-synthesis applied; bigram architecture itself is chain-grade-validated; the question is whether Path C encoder reproduces the lift).
- **Pre-flight requirement:** ship the 3 new infrastructure pieces FIRST -- `hdlab/lm_eval_harness.py` (META_M7-compliant), `hdlab/token_vocab.py`, `hdlab/bigram_gap_measurement.py`. Each is ~3hr-1day build; verification tests in `verification/`. Cell cannot ship without these.
- **Reference for design context:** Section "Cheap decisive test" + Section 7 Cell 1 of the parent research note.

### ANCHOR_2 (rank-2, depth extension; CONTINGENT on Gap 3 landing)

- **Pointer:** `lang_ingest_trigram_modern_hopfield_attractor_v1`
- **Substrate-product reading:** Trigram-depth ingest using Modern Hopfield (Ramsauer 2021 dense Hopfield = beta-softmax attention) for cleanup. The HRR crosstalk floor at N_DIM=4096 / V_TOK=8192 / depth=3 EXCEEDS Plate's per-position capacity bound; vanilla cosine-floor cleanup degrades. Modern Hopfield basin-sharpening is the canonical fix (matched to Gap 3 ANCHOR_1 mechanism). 3-arm: ARM_TRIGRAM_VANILLA_CLEANUP / ARM_TRIGRAM_MODERN_HOPFIELD / ARM_TRIGRAM_K_SET_BUNDLE.
- **Tier hint:** MEASURED_MECHANISM expected; chain-grade-eligible if HP and beats ARM_VANILLA_CLEANUP by >= 0.05 absolute on top1.
- **Why now:** ONLY-IF Gap 3 `gap3_modern_hopfield_prototype_attractor_v1` lands chain-grade FIRST (currently in queue per status_log 2026-06-26 08:13). Compose immediately after.
- **P_deflated:** 0.35.

### ANCHOR_3 (rank-3, generation eval; ships parallel to ANCHOR_1)

- **Pointer:** `lang_ingest_autoregressive_generation_eval_v1`
- **Substrate-product reading:** End-to-end generation quality on text8: substrate generates 50-token sequences from a held-out prompt; measure diversity_5gram, repetition_rate, trigram_chrf, perplexity-on-truncation. Uses g1 SubstrateGenerator + ANCHOR_1's S matrices. 3-arm: ARM_GREEDY_TOPK1 / ARM_NUCLEUS_TOPP_0p9 / ARM_LANGEVIN_SIGMA_0p1 (sigma_scale sweep [0.0, 0.05, 0.1, 0.2]).
- **Tier hint:** MEASURED_MECHANISM; demonstrates substrate IS a viable autoregressive generator at vocab=8192.
- **Why now:** depends on ANCHOR_1 completing (needs S matrices); ships ~30min after ANCHOR_1 lands.
- **P_deflated:** 0.40.

### ANCHOR_4 (rank-4, refuse-gate calibration; ships parallel to ANCHOR_3)

- **Pointer:** `lang_ingest_refuse_gate_calibration_text8_heldout_v1`
- **Substrate-product reading:** Apply hdlab/refuse_gate.py:calibrate_refuse_threshold to LM next-token scores; calibrate tau on heldout in-dist/ood split; demonstrate substrate-LM-with-confidence. 2-arm: ARM_NO_GATE_BASELINE / ARM_REFUSE_GATE_TAU_CALIBRATED.
- **Tier hint:** MEASURED_MECHANISM; provides glass-box LM with substrate-native "I don't know".
- **Why now:** depends on ANCHOR_1; cheap (~30min); HIGH product-narrative value (glass-box + calibrated-refuse).
- **P_deflated:** 0.50 (refuse_gate primitive already chain-grade at V_REL=256; transferring to LM scope is incremental).

### ANCHOR_5 (rank-5, continual extension; CONTINGENT on Gap 4 landing)

- **Pointer:** `lang_ingest_continual_nrem_replay_v1`
- **Substrate-product reading:** Demonstrate substrate ingests text8 + wikitext-103 SEQUENTIALLY without forgetting text8 bigram-gap. Uses nrem_replay_decorator from hdlab/continual.py (proven-bound +0.57 drift_reduction). 3-arm: ARM_SEQUENTIAL_NO_REPLAY / ARM_NREM_REPLAY_FRAC_0p2 / ARM_INTERLEAVED_BASELINE. If Gap 4 TWO_TIER_GENERATIONAL lands chain-grade, compose with TWO_TIER for dual-mechanism continual.
- **Tier hint:** MEASURED_MECHANISM if HP; chain-grade-eligible only with TWO_TIER composition.
- **Why now:** ONLY-IF Gap 4 `gap4_two_tier_generational_W_v1` lands AND ANCHOR_1 lands chain-grade. Lower priority unless decade-scale ingest is sequence-critical.
- **P_deflated:** 0.40.

---

## NEW INFRASTRUCTURE REQUIRED PRE-CELL (mandatory before ANCHOR_1)

Three new hdlab/ files must land BEFORE ANCHOR_1 ships:

### INFRA_1 (BLOCKING): `hdlab/lm_eval_harness.py`

- **Purpose:** META_M7-compliant LM eval harness. Returns top1, top5, T-calibrated BPC, bigram_gap, sanity_top1_at_random, regime_check_passed.
- **Why load-bearing:** the 2026-06-23 RIGGED-HARNESS finding (cert ledger row 698) showed 7+ HARD_FAILs on substrate-as-LM were methodology-confound. Without this, every LM cell will reproduce the trap.
- **Build cost:** ~1 day; ~150 lines; verification test in `verification/test_lm_eval_harness.py`.
- **Reference spec:** Section 3.1 of parent research note.

### INFRA_2 (BLOCKING): `hdlab/token_vocab.py`

- **Purpose:** Deterministic-hash vocabulary management; persists to `data/substrate_index/lang/tokens.jsonl`; codebook caching; OOV / UNK handling.
- **Build cost:** ~1 day; ~120 lines.
- **Reference spec:** Section 3.2 of parent research note.

### INFRA_3 (NON-BLOCKING for ANCHOR_1; BLOCKING for chain-grade reporting): `hdlab/bigram_gap_measurement.py`

- **Purpose:** Standardized bigram_gap = substrate_top1 - word_bigram_top1 with consistent baseline computation.
- **Build cost:** ~3 hours; ~80 lines.
- **Reference spec:** Section 3.3 of parent research note.

**Total infrastructure build:** ~2.5 days of cell-author time before ANCHOR_1 ships. This is the load-bearing investment; without it, ANCHOR_1 will reproduce the METHODOLOGY-CONFOUND class.

---

## Context pointers (file paths only, not summaries)

- Primary research note (this drill): `notes/research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
- n1_v3 provenance audit (the cert anchor): `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md`
- Path C 5x universal encoder drill (sister composition): `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
- META_HARNESS_RIGGED methodology audit: `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md`
- Brain-to-LM relevance: `notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md`
- Decode-side LM improvements: `notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md`
- Gap 3 Modern Hopfield (in queue; composition dep for ANCHOR_2): `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md`
- Gap 4 TWO_TIER (running; composition dep for ANCHOR_5): `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- Gap 1 routing (running; composition dep for autonomous routing): `notes/research_gap1_routing_bidirectional_as_router_2026-06-26.md`
- Prior text8 cells (substrate-mine first per [[feedback-substrate-mine-capacity-before-extrapolating]]): `data/exp_n3_text8_ingest_cert_v1_smoke2/`, `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/`, `data/exp_substrate_pc_hierarchy_text8_lm_v2/`
- chain-grade primitives backing the pipeline: hdlab/{char_trigram_encoder, sequence_memory, generation, binding, bundling, memory, refuse_gate, continual, multi_hop}.py
- Cell-author smoke + Fix #17 measurement reference: per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]]; route heavy matmul cells via hdi_orchestrator to remote_cpu (not laptop CPU)

---

## Contract section

This hand-off is informational. Cell-author retains:
- experiment design authority (envelope-fail-bands, smoke design, harness wiring)
- pre-reg HARD-PASS / HARD-FAIL threshold authorship
- skip-smoke / smoke-yes decision per substrate-native vet
- dispatch queue selection (remote_cpu_queue recommended for matmul-bound; overnight_queue if GPU available per Fix #24)
- predispatch_check.py verify-the-referent gate (Fix #26)
- mandatory schema-vet + atexit partial-results + per-seed checkpoint for multi-million pair ingest (D1/D2 from timeout drill)
- decision authority on whether to build INFRA_1/2/3 inline vs hand-off to testbed
- decision authority on V_TOK = 8192 vs V_TOK = 4096 vs V_TOK = 50087 (n1_v3 matched regime)
- decision authority on N_PARTITIONS = 16 vs 64 vs 256 vs 1024 per Section R5 capacity analysis

Research role: literature provided; substrate-mapping articulated; ranked priority surfaced; 8 of 9 chain-grade primitive citations verified line-by-line; 3 NEW infrastructure pieces specified with interface contract. Cell-author may RE-RANK based on substrate-state at pickup (queue depth, recent verdicts, Gap 3/4 status).

---

## Autonomy declaration

Cell-author has FULL autonomy to:
- pick which of the 5 anchors to ship first (or alternate order)
- defer / skip any anchor that conflicts with current fleet priorities
- batch INFRA_1/2/3 with ANCHOR_1 in single multi-day cycle vs separate cells
- choose V_TOK regime (recommended: V_TOK=8192 for vocabulary scale balance; smoke at V_TOK=2048 first per Section R3)
- choose N_PARTITIONS (recommended: N_PARTITIONS=64 with sparse-S threshold per Section R5)
- compose anchors differently than this hand-off suggests (e.g., merge ANCHOR_3 + ANCHOR_4 into single eval cell)
- substitute encoder choice (char_trigram_encoder vs deterministic-hash bipolar; this IS what ARM_B vs ARM_D in ANCHOR_1 measures)
- defer ANCHOR_2/5 indefinitely if Gap 3/4 don't land soon
- re-rank against fleet priorities at pickup time (e.g., if substrate is mid-bigram-gap-closure on a different track, defer this drill entirely)

The hand-off is the entry point; cell-author is the authority on cell execution.

---

## Fleet-state pointers for ranking decisions

- Recent gap drills landed today (2026-06-26): Gap 1 routing in flight; Gap 2 CLOSED RED->GREEN; Gap 3 Modern Hopfield queued; Gap 4 TWO_TIER running.
- Last research_delivery: gap1 bidirectional-collide-as-router (P_deflated=0.45; single 6-arm cell ~5500s local_cpu).
- Pipeline state per orchestrator status log (last entry 15:37 UTC): local_cpu_queue=455 atoms (1 running); remote_cpu_queue=1134 atoms (1 running); 4 cells moved local->remote per USER directive.
- Active program priority: USER-directed substrate-native language ingest start per Path C 81% compliance audit.
- Pause flag: check at exp_dev pickup; ANCHOR_1 ship is pause-gated per orchestrator-routing skill.
