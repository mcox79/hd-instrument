# Pre-registration: phase05_v1_llama32_1b_residual_extract_v1

**Date:** 2026-06-04
**Anchor:** phase05_v1_llama32_1b_residual_extract_v1
**Queue:** overnight_queue
**N:** n/a (anchor is residual-extraction, not a substrate N sweep), **Seeds:** 1 (deterministic), **n_docs:** 100000

## Scientific question
Does Llama-3.2-1B's residual stream at the Algorithm 1 layer band (`hidden_states[8:17]` = 9 effective layer outputs, final-token position, BF16 cast to FP32) produce non-NaN, distinct, all-finite features sufficient to feed Exp-Dev's substrate-side Algorithm 1 + Hyperprobe MLP + audit primitive pipeline for Phase 0.5 v1 Rung A? This anchor is the Testbed-side handoff: it exists to deliver clean residuals + VSA target encodings to Exp-Dev; downstream val_sim measurement happens in Exp-Dev's pipeline.

## Pre-registered bands

**HARD-PASS:**
- All target docs (>=95% of parsed-analogy target = 95000+ of 100000) processed without exception
- residuals (n_docs, 9, 2048) float32 contains zero NaN/Inf
- target_vsa (n_docs, 4096) float32 bipolar (values in {-1, +1}) contains zero NaN
- npz + sidecar JSONs written and openable; aggregate-from-partials succeeds

**MIDDLE:** 80-95% docs processed without exception; per-doc failures isolated and logged; npz still openable.

**HARD-FAIL:** <80% docs processed OR any NaN/Inf in residuals OR target_vsa shape/dtype/bipolar invariants violated OR npz fails to open OR no partial recovery possible.

## Calibration rationale
This anchor is a deterministic forward-pass extraction (no training, no stochastic seeds beyond doc-id split-hash). The HP gate is engineering correctness: "did the pipeline run end-to-end and produce well-formed artifacts." Downstream val_sim measurement (Hyperprobe MLP) is Exp-Dev's responsibility on the consumed artifacts. The 95% completeness floor accounts for token-edge-case parser failures that would silently drop a small fraction of malformed analogy strings; >5% would indicate a parser bug or HF dataset schema drift.

## N-suffix section
Anchor has NO `_n<N>` suffix per PROT-018 because it is not a substrate-N sweep. The "N" of relevance is the LLM hidden dim (2048, model-specific not sweep parameter) and the substrate VSA dim (4096, paper-matched default; Exp-Dev may flag 2048 to match Algorithm-1 sum-pool dim). Neither is being swept; both are fixed config.

## Timeout estimate
Smoke (synthetic-residual mode; no model load): 5.5s wall at 50 docs / VSA_D=512.
Real-load smoke (2 docs CPU forward of Llama-3.2-1B BF16): 6.2s wall.
FULL: 100000 docs / VSA_D=4096 / 4060 Ti BF16 GPU.

Per-doc wall budget (4060 Ti, batch=1, SEQ_LEN<=64 short-analogy prompts, Llama-3.2-1B BF16 inference, no KV cache, no backward): ~30-100ms/doc empirically (1B-class BF16 forward on 4060 Ti is bandwidth-bound; 4060 Ti has 288 GB/s mem bandwidth; 2.5GB model weights => ~9ms theoretical mem-read floor; practical ~30-80ms with kernel launches + tokenization + transfer + CPU-side aggregation).

formula: ceil(1.5 * 50_s_per_doc * 100000_docs / 1000) = 7500s (1.5x safety on midpoint estimate)
Adding model-load (~30s) + codebook build (~60s) + npz write (~120s) + safety buffer = **timeout_s = 10800** (3 hours; well under PROT-019 cap of 14400).

Resume capability: per-doc partial JSON via `_seed_checkpoint.write_partial_key`; if killed mid-run, restart picks up at last completed doc index. So the timeout is per-attempt; a HARD_FAIL on timeout doesn't lose progress.

# -----------------------------------------------------------------------------
# Handoff to Exp-Dev (post-completion)
# -----------------------------------------------------------------------------
# On HARD_PASS, the following artifacts are delivered for Exp-Dev's substrate-side pipeline:
#   F:\hd_data\exp_phase05_v1_llama32_1b_residual_extract_v1\
#     llama32_1b_residuals.npz                # residuals + doc_ids + split + target_vsa + vsa_dim
#     llama32_1b_residuals_meta.json          # model_id + layer_band + n_train/val/test + extracted_at
#     doc_id_to_doc_str.json                  # traceability sidecar
#     metrics.json                            # this anchor's HP/MID/HF verdict
#
# Heartbeat watchdog SCP-pulls these back to D:\AI\hd-instrument\data\... within 30s of write.
# Exp-Dev's substrate-side harness reads the npz, runs Algorithm 1 (k-means k=5 + sum-pool + sign) on
# the residuals + trains Hyperprobe MLP (val_sim >= 0.80 HP gate at 1B) + runs 3 audit primitives.
