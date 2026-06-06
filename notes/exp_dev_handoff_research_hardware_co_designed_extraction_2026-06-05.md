# exp_dev hand-off -- research: hardware-co-designed extraction architecture

**Filed-by:** research sub-agent (2026-06-05)
**Trigger:** notes/research_drill_hardware_co_designed_extraction_2x_2026-06-05.md
**Per [[feedback-no-experiment-design-in-prompts]]:** this file hands off task + why + contract only.
  Exp_dev decides anchor names, sweep grids, thresholds, queue, and pre-reg bands.

---

## Pause state block

This hand-off is informational. Experiment dispatch requires pause-gate check
(data/orchestrator_paused.flag). Exp_dev scans this file on emergency-refill cycles.

---

## Anchor candidates (rank-ordered)

### Rank 1: Forward-pass prefill throughput scaling (M-series validation)
**Why now:** Roofline model predicts M4 Max achieves 13-16 tok/s for 70B Q4 decode
  and ~50-70 tok/s effective for batch=64 prefill (near compute-bound crossover).
  This prediction is falsifiable on available hardware with no cloud cost.
  If extraction runs in prefill-only mode (no generation), throughput may close the
  gap with H100 significantly. Needs empirical verification against roofline formula.
**Substrate-product reading:** Validates whether M-series is viable extraction backbone
  for Phase 0.5 and beyond; determines if cloud H100 budget can be redirected to hardware.
**Tier hint:** CPU/local experiment (M-series hardware required); no cloud needed.
**Anchor pointer:** research note section 8 (Cheap decisive test) + section 4d (prefill mode).

### Rank 2: Bipolar sign-compression storage verification
**Why now:** Research finding: bipolar 1-bit compression reduces vector storage from
  1.2 TB to 37.5 GB for Wikipedia-scale extraction (32x reduction). This is
  algebraically straightforward but needs a pipeline test to confirm no accuracy
  degradation in downstream retrieval tasks.
**Substrate-product reading:** If confirmed, eliminates storage as a bottleneck --
  entire Wikipedia bipolar embedding fits in M3 Ultra / M4 Max unified memory for
  in-memory retrieval. Changes product design significantly.
**Tier hint:** CPU smoke first; then GPU verification.
**Anchor pointer:** research note section 11c.

### Rank 3: vLLM prefill-only batch extraction mode
**Why now:** Standard vLLM usage extracts generated tokens; for substrate extraction
  we need final hidden states. Prefill-only extraction mode (batch hidden state output)
  is 3-5x faster than generation mode per roofline analysis. Needs implementation
  + throughput verification on available consumer hardware.
**Substrate-product reading:** Direct path to reducing extraction cost for Phase 0.5
  Wikipedia/PubMed corpus jobs. Could halve or reduce cloud budget.
**Tier hint:** Remote CPU queue for framework validation; GPU for throughput verification.
**Anchor pointer:** research note section 10d.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_hardware_co_designed_extraction_2x_2026-06-05.md
- Roofline algebra: research note section 1
- Cost model: research note sections 2 and 5
- Phase 0.5 extraction plan: notes/orchestrator_post_compaction_brief.md
- Hardware routing policy: memory/feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Cloud policy: memory/feedback_cloud_only_when_absolutely_necessary.md

---

## Contract

Exp_dev owns: anchor design, sweep parameters, pre-reg bands, queue routing, self-test.
Research handed off: (1) falsifiable predictions with HP/MID/HF thresholds in research note,
  (2) recommended hardware tier per anchor, (3) cost model to use for break-even verification.

Do NOT design experiments inline in this file or in orchestrator routing prompts.

## Autonomy declaration

Exp_dev has full autonomy over anchor naming, N/seed sweep, quantization choices,
framework selection (mlx vs llama.cpp vs vLLM), and pre-reg numerical bands.
The research note provides roofline predictions as theoretical targets only --
exp_dev is NOT bound to match them; discrepancies are the finding.
