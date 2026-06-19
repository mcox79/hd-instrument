# exp_dev hand-off -- research: Path A cross-attention mechanism drill (5x)

**Filed-by.** research sub-agent, 2026-06-09.
**Trigger.** Research note d:/AI/hd-instrument/notes/research_drill_path_a_mechanism_5x_2026-06-09.md delivered 5x mechanism drill on empirically confirmed 15-17% perplexity improvement from Flamingo-style gated cross-attention adapter. Five ranked anchor candidates ready for empirical test.

**Pause state.** Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatch. If paused, hold until flag cleared.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and provides context pointers only. Exp-dev designs the actual experiment code, pre-reg bands, and dispatch config autonomously.

---

## Anchor candidates (rank-ordered)

### 1. Random-substrate baseline (mechanism discriminator -- highest priority)

**What it tests.** Replace past-token hidden states with random Gaussian vectors of the same shape. Same adapter architecture, same gate initialization, same training procedure. Discriminates regularization hypothesis (H3) from all signal-based hypotheses (H1, H2, H4, H5, H6).

**Substrate-product reading.** If random vectors provide less than 2% of the real-substrate improvement, substrate-attention is confirmed to be providing genuine non-redundant signal. This is the cheapest, most decisive gate before any frontier-scaling cloud spend.

**Tier hint.** CPU or local GPU. Short wall. No cloud required. Batch with layer-position ablation on same instance.

**Why now.** Cheapest discriminating experiment; should run before any layer-count or frontier scaling work. Result gates interpretation of all other anchors.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: random-substrate perplexity improvement < 2% of real-substrate improvement
- MID-BAND: 2-8%
- HARD-FAIL: > 8% (would require mechanism story revision)

---

### 2. Layer-position single-layer ablation

**What it tests.** Train four single-layer cross-attention adapters at L2, L5, L8, L11 of Pythia-160M (12 layers). Compare perplexity improvement at each position. Tests the semantic-band hypothesis (Tenney 2019 analog for causal decoders).

**Substrate-product reading.** If L4-L6 is best, the empirical choice of L4+L5 was mechanistically motivated, not coincidental. Validates layer-selection heuristic for future substrate-LLM coupling design.

**Tier hint.** Local GPU. Four independent runs; can batch on one instance. Medium wall.

**Why now.** Validates the most distinctive architectural claim (middle-layer injection is optimal). Low cost relative to discriminating power.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: L4-L6 range produces best single-layer result
- MID-BAND: L7-L9 is best (late-semantic, still consistent with hypothesis)
- HARD-FAIL: L2 or L11 is best (contradicts semantic-band hypothesis)

---

### 3. Sequence-length sweep

**What it tests.** Evaluate existing trained adapter (no new training) at sequence lengths 256, 512, 1024, 2048. Tests whether improvement is length-dependent (H1 context-extension) or length-flat (H3 regularization).

**Substrate-product reading.** Monotonic improvement with length confirms that substrate-attention provides context-extension benefit, which is the primary product claim for long-document use cases (compliance, audit logs, long-horizon reasoning).

**Tier hint.** CPU or local GPU. Inference-only (no new training). Very short wall if adapter is already trained.

**Why now.** Inference-only; uses existing trained checkpoint. Near-zero additional training cost.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: improvement at 2048 >= 2x improvement at 256
- MID-BAND: 1.3-2x
- HARD-FAIL: improvement within 20% across all lengths (flat = regularization-dominated)

---

### 4. Gate dynamics logging

**What it tests.** Log gate values (tanh(alpha)) per layer, per token, per document type during inference on held-out set stratified by: code (high repetition), formal text (structured), natural prose (low repetition), news (diverse). Tests whether gate is content-dependent (H1/H4/H5) or roughly constant (H3).

**Substrate-product reading.** Gate variance > 0.05 across document types establishes that the substrate-attention module is doing selective memory access, not uniform regularization. This is directly relevant to the audit trail product feature (gate value is a per-token memory-reliance score).

**Tier hint.** CPU or local GPU. Inference-only with logging hook. Short wall.

**Why now.** No new training required. Provides mechanism fingerprint that discriminates all hypotheses simultaneously. Gate logging is also a prerequisite for the audit trail product feature.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: gate variance across document types > 0.05
- MID-BAND: 0.01-0.05
- HARD-FAIL: gate variance < 0.01 (uniform = regularization-consistent)

---

### 5. Layer-count scaling (1 / 3 / 4 / 6 layers)

**What it tests.** Train adapters with 1, 3, 4, 6 cross-attention layers (in addition to existing 2-layer result). Tests saturation and interference predictions. Establishes cost-efficiency curve for production deployment.

**Substrate-product reading.** If improvement saturates by 4 layers, the production deployment should use 3-4 layers concentrated at the semantic-onset band, not the full KBLaM every-layer pattern. This has direct compute-cost implications for inference at scale.

**Tier hint.** Local GPU. Four independent training runs. Higher wall than anchors 1-4. Can batch on same instance if GPU memory allows.

**Why now.** Lower priority than anchors 1-4 because it requires new training and the mechanism question (H1 vs H3) should be resolved first (anchors 1-3) before investing in scaling experiments.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: saturation visible by 4 layers (< 5% additional gain at 6 vs 4)
- MID-BAND: gradual improvement through 6 without clear saturation
- HARD-FAIL: monotonic improvement through all 6 layers with no sign of saturation (suggests 2-layer is under-provisioned)

---

## Context pointers

- Research note (full mechanism analysis): d:/AI/hd-instrument/notes/research_drill_path_a_mechanism_5x_2026-06-09.md
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md (check Hopfield-retrieval and context-extension rows)
- Prior handoff template: d:/AI/hd-instrument/notes/exp_dev_handoff_cycle14_queue_refill_2026-06-02.md

---

## Contract

Exp-dev designs anchors with pre-regs per envelope-fail-bands. No inline experiment design in this file. Dispatch via queue_add.sh (GPU or CPU as appropriate per tier hints above). Post-ship REMOTE VERIFY per role contract.

## Autonomy declaration

Exp-dev has full autonomy to: sequence anchors 1-5 in any order, batch compatible anchors on one instance, skip any anchor that conflicts with an in-flight experiment, and adjust pre-reg band numbers based on current cap_map state at dispatch time. Escalate to orchestrator if: pause flag is set, cloud budget would exceed $5 for these anchors combined, or anchor 1 (random-substrate baseline) returns HARD-FAIL (mechanism story revision required before proceeding).
