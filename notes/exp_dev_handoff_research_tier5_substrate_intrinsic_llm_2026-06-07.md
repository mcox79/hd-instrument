# exp_dev hand-off -- research: Tier 5 Substrate-Intrinsic LLM Architecture

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: d:/AI/hd-instrument/notes/research_drill_tier5_substrate_intrinsic_llm_3x_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
WHY they matter. exp_dev designs the actual experiment (sweep grid, thresholds, queue
choice, timeout). No numerical grids or threshold formulas are pre-committed here.

---

## Pause state block

This handoff was written during an active research session. exp_dev MUST check
data/orchestrator_paused.flag before dispatching any anchors. These anchors target
Pythia-160M scale and are designed to be CPU/cheap-GPU workloads ($30-200 each).

---

## Anchor candidates (rank-ordered by urgency + cheapness)

### Anchor 1 (TIER: CHEAP GPU SMOKE -- highest priority gate for all Tier 5 paths)

NAME SUGGESTION: tier5_arch8_kv_cache_hopfield_fidelity

WHY NOW: Arch 8 (substrate as KV-cache replacement) is the ONLY Tier 5 architecture that
works on a FROZEN pre-trained LLM with NO new training. It tests whether substrate's modern
Hopfield retrieval is precise enough to replace fp16 KV cache in transformer attention without
degrading generation quality. This is the cheapest empirical gate for the ENTIRE Tier 5
design space. If it hard-fails, we learn critical information about Hopfield retrieval precision
before spending any money on training experiments.

ANCHOR POINTER: Intercept KV cache of the final N attention layers of Pythia-160M using
PyTorch forward hooks. Write K/V pairs to a substrate bipolar store. On attention read, retrieve
via modern Hopfield energy function. Evaluate on wikitext-103 subset (500-1000 samples,
512-token context). Compare perplexity vs unmodified Pythia-160M-base as reference.

SUBSTRATE-PRODUCT READING:
- PASS: substrate Hopfield retrieval is precise enough for attention computation. Authorize
  Arch 8 production path. This becomes "GDPR-compliant persistent context window" product
  capability.
- FAIL: substrate KV fidelity is insufficient at current N. Root cause likely: N must be
  higher (8192-16384) for adequate attention precision. Either raise N or scope Arch 8 to
  final 2 layers only as a soft-memory augmentation.

TIER HINT: GPU smoke on Lambda H100 or local RTX4060. No training. Just inference with
modified KV cache. Cost $30-80. Wall time 1-2 hours. Run after 8-point preflight checklist.

---

### Anchor 2 (TIER: CHEAP GPU SMOKE -- parallel path; tests bipolar input projection viability)

NAME SUGGESTION: tier5_arch7_bipolar_input_projection_smoke

WHY NOW: Arch 7 (dual-mode LLM: text + substrate input) is the #1 actionable Tier 5
architecture. The first empirical gate is whether a linear projection from bipolar HD vectors
(N=4096) to Pythia-160M hidden dim (512) can produce useful representations with minimal
fine-tuning. A 5K-pair synthetic dataset tests whether bipolar input projection is
structurally viable before committing to $200 training runs.

ANCHOR POINTER: Construct a small synthetic evaluation set: (bipolar query vector from a
substrate KB of 100 facts) -> (text answer from that fact). Freeze all Pythia-160M weights.
Add a single linear projection layer: R^N_bipolar -> R^512. Train ONLY this projection on
the 5K pairs via AdamW with small LR. Evaluate exact-match accuracy on 500 held-out pairs.
Compare to a baseline that uses standard text tokens (Tier 4 text interface path).

SUBSTRATE-PRODUCT READING:
- PASS: bipolar input projection reaches >= 80% of text-interface accuracy at 5K pairs.
  Authorize Arch 7 full training run (500M tokens, $100-200).
- FAIL: accuracy < 50% of text-interface baseline at 5K pairs. Root cause: either (A) N
  is too small (N=4096 bipolar not expressive enough for projection to 512 dims), or (B)
  5K pairs is insufficient (scale to 50K before abandoning). Do NOT abandon Arch 7 on a
  single FAIL at 5K -- follow rehabilitation per feedback-rehabilitation-after-rejection.

TIER HINT: GPU smoke. Training only the projection layer = fast. 5K pairs * modest LR sweep.
$30-80 on Lambda H100 or local RTX4060. Wall time 1-2 hours.

---

### Anchor 3 (TIER: GPU PROBE -- validates bipolar semantic coverage at generation quality)

NAME SUGGESTION: tier5_arch1_bipolar_input_wikitext_perplexity_probe

WHY NOW: Arch 1 (input layer replacement alone) is the cheapest single-architecture test.
Trains Pythia-160M's input projection on 500M tokens of wikitext-103 passages encoded via
Pattern B bipolar encoding. Measures whether Pattern B bipolar encoding preserves enough
semantic structure to guide LLM generation. This is the foundational question for ALL
architectures that consume bipolar input.

ANCHOR POINTER: Encode wikitext-103 passages into bipolar HD vectors using Pattern B
(existing substrate implementation). Replace Pythia-160M embedding table with linear
projection from R^N -> R^512. Freeze all transformer weights. Train projection on 500M tokens
of encoded passages. Evaluate perplexity on wikitext-103 test set vs Pythia-160M-base
reference.

SUBSTRATE-PRODUCT READING:
- PASS (perplexity within 1.5x baseline): Pattern B encoding preserves sufficient semantic
  structure. Authorize Arch 7 full training with dual-mode input.
- FAIL (perplexity >= 3x baseline or training diverges): Pattern B encoding is semantically
  lossy for generation tasks. Root cause to investigate: (A) N too small, (B) Pattern B
  binding scheme doesn't cover morphological variants, (C) need pretrained semantic encoder
  to produce bipolar input (not raw Pattern B bind).

TIER HINT: GPU probe. 500M tokens training. Projection-only fine-tuning is cheap vs full
retraining. $100-200 on Lambda H100. Wall time 3-4 hours. Lower priority than Anchors 1-2
(depends on Anchor 2 gate logic).

---

### Anchor 4 (TIER: CPU SMOKE -- architecture compatibility verification, free)

NAME SUGGESTION: tier5_arch8_kv_partition_design_validation

WHY NOW: Arch 8 requires partitioning a single substrate W matrix by attention layer and
head. Pythia-160M has 12 layers x 12 heads = 144 "slots." At N=4096 per slot, this is a
144x4096 partition requirement. This is a software design question with a cheap CPU
correctness test: does substrate support 144-slot partitioned KV store with correct retrieval
isolation between slots?

ANCHOR POINTER: Instantiate a substrate instance with 144 partitioned KV slots. Write 100
random K/V pairs to each slot. Retrieve from each slot independently. Verify zero cross-slot
contamination (retrieval from slot 7 does not return content from slot 23). Measure retrieval
accuracy per slot vs single-slot baseline.

SUBSTRATE-PRODUCT READING:
- PASS: multi-slot partitioned KV store works with zero cross-slot contamination. Arch 8
  is architecturally feasible on the current substrate implementation.
- FAIL: cross-slot contamination detected. Root cause: either (A) substrate's W matrix
  needs explicit row-slicing for partition isolation, or (B) Hopfield energy function
  is not partition-aware. Engineering fix before Anchor 1 GPU test.

TIER HINT: CPU smoke. Pure substrate operation test. No LLM. No GPU. < 5 min wall.
Should run BEFORE Anchor 1 GPU test to validate the partition scheme.

---

## Context pointers

Research note (primary):
  d:/AI/hd-instrument/notes/research_drill_tier5_substrate_intrinsic_llm_3x_2026-06-07.md

Afternoon brief (Tier 4 context + substrate validation baseline):
  d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

Substrate codebase:
  d:/AI/hd-instrument/hdlab/

Tier 4 v1.1 anchor reference (existing pre-tests gating Tier 4):
  d:/AI/hd-instrument/notes/active_priorities.md

Key published references (from lit-scan):
  arXiv:2512.14709 -- Attention as Binding (VSA-transformer equivalence; Dec 2025)
  arXiv:2407.07093 -- FBI-LLM (fully binarized LLM training; Jul 2024)
  arXiv:2509.24425 -- BiHDTrans (binary HD transformer; Sep 2025)
  arXiv:2604.07466 -- Cross-tokenizer distillation via byte interface (Apr 2026)

---

## Contract

exp_dev designs the experiment (sweep grid, thresholds, queue choice, timeout formula,
anchor name with _n suffix). This file provides WHY + ANCHOR POINTER + TIER HINT only.

## Autonomy declaration

exp_dev has full autonomy to:
  - Set sweep ranges and step sizes within tier constraints
  - Choose between overnight_queue and remote_cpu_queue / remote_gpu_queue based on wall-time
  - Set HARD-PASS / HARD-FAIL / middle-band thresholds per envelope-fail-bands feedback
  - Batch Anchor 4 (CPU) with other CPU anchors if queue depth permits
  - Run Anchor 1 and Anchor 2 in parallel (independent codepaths)
  - Skip Anchor 3 if Anchor 2 HARD-FAIL (Arch 7 not viable -- revisit before training)
  - Deprioritize these anchors if Tier 4 v1.1 pre-tests are still running (Tier 4 gates first)
