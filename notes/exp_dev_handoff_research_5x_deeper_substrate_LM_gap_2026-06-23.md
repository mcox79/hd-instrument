# exp_dev hand-off -- research: 5x DEEPER substrate-as-LM gap (Path A pseudo-LM bigram-gap closure)

**Filed by:** Research (Opus 4.7) 2026-06-23
**Trigger:** Research delivery `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` -- 5x deeper drill on the substrate-as-LM gap after Path A v2 calibrated landed MIDDLE_BAND BPC=7.864 (lambda=0.1 log-linear interp with unigram). Substrate is 0.126 bits BEHIND unigram standalone and 1.26 bits behind word-bigram. Best calibrated arm reads as "90% unigram, 10% substrate" — substrate contribution is at most 0.05-0.10 bits. Fix is NOT more calibration; fix is moving from rank-1 Hebbian outer product to a HIGHER-ORDER predictive operator that contributes well-calibrated mass across second-and-lower-rank candidates.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; if present, defer cell dispatch but keep hand-off filed for resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** exp_dev owns the actual cell design (smoke, gates, prereg). This hand-off provides anchor candidates + context pointers + autonomy declaration only.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP): `text8_substrate_pseudoLM_v3_hierarchical_bigram_v1`
**Pointer:** research note section "L3.1 — PC1: hierarchical-bigram + renormalization-group tokenizer" and "Cheap decisive test (pre-registered)".
**Substrate-product reading:** if HARD_PASSES at BPC <= 7.500, substrate-as-LM closes unigram gap forward-only-Hebbian on text8 V=4000 N_DIM=4096 (first substrate-native LM that beats minimum LM bar). New `hdlab/` primitive `hierarchical_ngram_substrate_lm(V, N_DIM, max_n=3, epsilon=4)` ships substrate-flat same cycle. Path A v3 unblocks bigram-gap closure attempt at GPU full scale (~6hr); next milestone BPC <= 7.0 = within 0.4 bits of word-bigram.
**Tier hint:** chain-grade-eligible if discriminating control (LAYER123_HIERARCHICAL BPC vs LAYER12_LOG_LINEAR BPC=7.864) cleanly shows layer-3 adds >=0.30 bits AND beats unigram BPC=7.738 by >=0.2 bits.
**Why now:** reuses entire v2 infrastructure (text8 ingest, GPU pipeline, per-seed sweep, log-linear interp); adds only one new code path (L3 token construction = pairs of (bigram, char) above co-occurrence threshold epsilon_2); Eugenio smoothness constraint guarantees d_n bounded (no memory blowup); 1hr GPU smoke + 6hr GPU full = ~7hr total compute fits in one overnight slot; tests a structurally-different mechanism class (rank-stacking vs rank-1-with-calibration) — the FIRST cell that directly addresses the v2-calibrated-MIDDLE_BAND finding's root cause.
**Pre-flight sanity (mandatory):** LAYER2_HEBBIAN_BIGRAM standalone BPC should be within 0.3 of v2's measured LAYER12_LOG_LINEAR BPC=7.864 at 10x-reduced N_TRAIN=10000 smoke (sanity-check rank-1 Hebbian is reproducible from existing pipeline). If LAYER2 deviates by >0.3, implementation bug. **Also:** coverage of L3 context on test set (fraction of test tokens with valid L3 context after smoothness constraint) must be reported per-seed; if <0.10, smoothness bottleneck dominates and the cell verdict needs to discriminate "L3 is empty" from "L3 doesn't help" — exp_dev to design this discriminator.

### Anchor 2 (CONDITIONAL on Anchor 1 verdict): `text8_substrate_pseudoLM_v3_CA3_hetero_autoassoc_v1`
**Pointer:** research note section "L3.2 — PC2: CA3-style heteroassoc + autoassoc cleanup composition".
**Substrate-product reading:** tests CA3-style composition (heteroassociative prediction + autoassociative cleanup of output distribution). If HARD_PASSES at BPC <= 7.500, an ORTHOGONAL substrate-as-LM mechanism is validated; substrate gains a second forward-only-Hebbian LM family.
**Tier hint:** measured-mechanism if positive; chain-grade requires verification at scale.
**Why now:**
- If Anchor 1 HARD_FAILS: Anchor 2 tests the orthogonal cleanup-side fix (mass spread via autoassoc cleanup of p_next distribution) — different mechanism class, may rescue where Anchor 1 cannot.
- If Anchor 1 HARD_PASSES: Anchor 2 tests additive lift (does cleanup of p_next add on top of hierarchical composition?).
- Either way, Anchor 2 is informative AFTER Anchor 1 verdict, NOT before.
**Risk:** uses `hdlab/iterative_attractor.py` which is in att1-HARD_FAIL family for noisy-cue cleanup. PC2 applies cleanup to OUTPUT DISTRIBUTION not cue, but the risk that cleanup primitive is broken for this regime too is real. Mitigation: run PC2 with N_DIM=16384 (larger; M/N=0.24 in finite-T retrieval regime); also include `PC2_HETERO_ONLY` arm (no cleanup) so cleanup contribution is measured isolated.

### Anchor 3 (CONDITIONAL on Anchor 1 HARD_PASS): `text8_substrate_pseudoLM_v3_HYBRID_path_a_path_b_v1`
**Pointer:** research note section "L5: Cross-substrate composition (Path A + Path B HYBRID)".
**Substrate-product reading:** USER directive to compose Path A (next-token LM) + Path B (KG storage) in same matrix W. If HARD_PASSES at BPC <= PC1_BPC - 0.30, substrate gets in-matrix LM + KG composition; product-grade for auditable-AI-memory subsystem positioning. Composes with continual-learning CLS-replay (each replayed atom contributes to W's per-layer rank-stack AND its KG triple).
**Tier hint:** chain-grade-eligible if HARD_PASS + 3 seeds + held-out.
**Why now:** **ONLY** if Anchor 1 HARD_PASSes — HYBRID without working hierarchical LM is structurally vacuous. Path B is already chain-grade at 1M facts (`exp_substrate_as_llm_scaling_million_facts_v1_resume`); HYBRID composes the two existing wins.
**Risk:** zero published precedent for in-matrix forward-only-Hebbian LM+KG composition; novel-synthesis; deflation factor 0.30 applied. The two contributions may interfere destructively.

### Anchor 4 (TERTIARY conditional on Anchor 1 HARD_PASS): PC1 + ENC1 sparse-fan-in composition test
**Pointer:** research note section "Cross-thread synthesis — With ENC1 cell".
**Substrate-product reading:** if ENC1 (in flight) HARD_PASSES sparse-fan-in encoder AND Anchor 1 HARD_PASSES PC1, rerun PC1 with sparse-fan-in codebook (K=5 sparse rows replacing dense bipolar). Expected additional lift: ~0.2 bits BPC reduction (encoder dimension + structural lift compose with hierarchical-bigram).
**Tier hint:** measured-mechanism; chain-grade requires PC1 + ENC1 both HARD_PASS independently first.
**Why now:** double-conditional. Defer until both predicate cells land.

### Anchor 5 (DEFERRED to PC1 HARD_PASS): sigma=1.0 input regime test
**Pointer:** research note section "L5 — Encoder-side composition: does PC1 break encoder Shannon-floor too?".
**Substrate-product reading:** tests whether PC1 simultaneously breaks V2 (BPC gap) and V3 (encoder Shannon-floor at sigma=1.0). Falsifier: PC1 layer-123 HARD_PASS in clean-input but degrade to BPC > 8.0 at sigma=1.0.
**Tier hint:** measured-mechanism characterization, not chain-grade target.
**Why now:** only meaningful if PC1 HARD_PASSes primary test in clean-input regime.

---

## Context pointers (paths, not summaries)

- Parent research drill (this drill): `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md`
- Parent v2 calibrated metrics (MIDDLE_BAND BPC=7.864): `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json`
- v1 HARD_FAIL metrics (substrate BPC=9.371 vs unigram 8.024): `data/exp_text8_substrate_pseudoLM_gpu_v1_smoke_remote/metrics.json`
- Path B chain-grade at 1M (HYBRID composition target): `data/exp_substrate_as_llm_scaling_million_facts_v1_resume/metrics.json`
- 2x revival overnight context: `notes/research_2x_revival_overnight_negatives_2026-06-23.md`
- att1 HARD_FAIL context (PC2 cleanup risk): `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md`
- Encoder-side cleanup fix (ENC1 in flight; Anchor 4 predicate): `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md`
- META atom Shannon-floor (cert ledger row 675): `T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026-06-23`
- Existing substrate primitives:
  - `hdlab/predictive_coding.py` (PC1 base — confirmed in tree)
  - `hdlab/sequence_memory.py` (PC2 hetero base)
  - `hdlab/iterative_attractor.py` (PC2 autoassoc base; in HARD_FAIL family per att1)
  - `hdlab/char_trigram_encoder.py` (PC1 layer-1 base)
  - `hdlab/whitening.py` (composition with ENC1 candidate)
  - `hdlab/generation.py` (downstream LM sampling)
- text8 corpus + pipeline: `data/text8_cache/text8.txt` + the v2 cell's ingest/recall/calibration scripts (clone for v3)

---

## Contract (exp_dev autonomy declaration)

- **exp_dev OWNS:**
  - cell file authoring (`text8_substrate_pseudoLM_v3_hierarchical_bigram_v1.py`, smoke + full; clone from v2 calibrated cell)
  - prereg file (`preregs/2026-06-23_text8_substrate_pseudoLM_v3_hierarchical_bigram.md`) with HARD_PASS / HARD_FAIL / MIDDLE_BAND thresholds per arm (research note "Falsifiable predictions" section is the source-of-truth for proposed thresholds; exp_dev may adjust within research-pre-reg bounds with justification)
  - smoke-gate cell at 10x-reduced N_TRAIN=10000 (LAYER2 standalone within 0.3 of v2 baseline)
  - full-cell dispatch via queue_add to overnight_queue (GPU; ~7hr per Anchor 1)
  - per-arm metrics.json emission with per-layer-BPC, per-layer-coverage, alpha-mixing-weights, cv-across-seeds — all REQUIRED_FIELDS per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]
  - REMOTE VERIFY post-ship per [[reference-remote-dispatch-cell-readiness-checklist]]
- **Research OWNS:**
  - mechanism interpretation post-verdict
  - cap_map row updates (`text8_substrate_pseudoLM_v3_hierarchical`: PENDING -> MEASURED_MECHANISM or REFUTED based on verdict)
  - follow-up drill design:
    - Anchor 2 dispatch if Anchor 1 HARD_FAIL (CA3-style orthogonal mechanism) OR HARD_PASS (additive lift test)
    - Anchor 3 dispatch ONLY if Anchor 1 HARD_PASS (HYBRID composition)
    - Anchor 4 dispatch if Anchor 1 HARD_PASS AND ENC1 HARD_PASS
    - Anchor 5 dispatch if Anchor 1 HARD_PASS
- **Orchestrator/Director OWNS:**
  - prioritization vs other queue items
  - pause-flag gating
  - Anchor 2/3/4/5 follow-up dispatch trigger after Anchor 1 verdict

---

## Cost / runtime

- **Anchor 1:** ~1hr GPU smoke (N_TRAIN=10000, V=4000, N_DIM=4096, 3 seeds, 5 arms); ~6hr GPU full (N_TRAIN=100000, V=4000, N_DIM=4096, 3 seeds, 5 arms). Total ~7hr GPU compute. Route to `overnight_queue` on `marsh@home`. **GPU usage discipline per [[feedback-fix24-gpu-dispatch-must-actually-use-gpu]]:** verify torch.cuda batched ops, encoder-hoisted, concurrent seeds, smoke GPU-util profiling >=50%.
- **Anchor 2:** ~1.5hr GPU smoke; ~8hr GPU full at N_DIM=16384 (larger codebook for cleanup capacity).
- **Anchor 3:** ~2hr GPU smoke (Path A + Path B in-matrix; Path B KG seeded from WordNet on text8 vocab); ~10hr GPU full.
- **Anchor 4:** ~7hr GPU full (PC1 with sparse-fan-in encoder; reuses Anchor 1 pipeline + ENC1 encoder).
- **Anchor 5:** ~6hr GPU full (PC1 at sigma=1.0 input; reuses Anchor 1 pipeline + noise injection at encoder stage).

---

## Cross-thread composition pointers

- Composes with `feedback-empowered-to-experiment-where-lit-says-dismissed`: Eugenio 2025 (closest published precedent) reported NO BPC, NO baseline comparison, only Alice in Wonderland — lit-scan says substrate is in uncharted regime for "forward-only Hebbian LM beats unigram on text8 V=4000". This is INFORMATION not STOP signal. Substrate-native variant (hierarchical-bigram + smoothness constraint + Hebbian rank-1 layers stacked) is principled and tests a structural escape from rank-1 limit; dispatch is correct default.
- Composes with `feedback-results-to-application-cadence-same-cycle`: if Anchor 1 HARD_PASSES, atomize `hierarchical_ngram_substrate_lm` to Store AND ship to `hdlab/` same cycle.
- Composes with `feedback-substrate-mine-capacity-before-extrapolating`: scour Store FIRST for existing chain-grade hierarchical-bigram primitives before declaring this novel. `predictive_coding.py` already exists in hdlab/; Research did NOT verify whether the existing primitive implements Eugenio-style hierarchical n-gram. **exp_dev to verify the existing predictive_coding.py contents and decide reuse vs new file.**
- Composes with `feedback-verify-the-referent`: pre-flight LAYER2_HEBBIAN_BIGRAM standalone BPC must match v2 calibrated baseline within 0.3 — if not, implementation bug NOT mechanism rejection. The referent (v2 baseline) must arrive as expected.
- Composes with `feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text`: cross-cell convergence claims (e.g., "PC1 + PC2 both HARD_PASS") must verify per-arm metrics.json, NOT verdict_msg framing. Per-layer-BPC + per-layer-coverage required fields in metrics.json.
- Composes with `feedback-fix26-predispatch-verify-the-referent-gate`: run `tools/predispatch_check.py text8_substrate_pseudoLM_v3_hierarchical_bigram_v1` before dispatch to check recent_landings.jsonl + atoms.jsonl for prior evidence (no duplicates; no recent HARD_FAIL re-dispatches).

---

## Operational note

This hand-off is filed alongside the research note for auto-discovery by exp_dev emergency-refill cycles (scans `notes/exp_dev_handoff_*.md` sorted by mtime). The Anchor 1 cell is the recommended dispatch on next exp_dev refill cycle; Anchors 2-5 are conditional follow-ups awaiting Anchor 1 verdict.

Research-to-experiment feed is structural: this handoff exists so exp_dev pulls from filesystem, not from main-thread memory.
