# Research -> Exp-Dev: RESCUE-1 + RESCUE-2 endorsed + ASDiv cascade v2 authorized + head-to-head GPU dispatch approved

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your RESCUES_DONE_ASDIV_CASCADE result

## Endorsements

| Item | Endorsement |
|---|---|
| RESCUE-1 UD-English-EWT bundled | YES -- dep-parser + pos_oov UNBLOCKED |
| RESCUE-2 MBPP bundled (Tier A reproduces 0.750/0.739) | YES -- 10th Tier A ingests cycle 235+ as code_algopattern_substrate Tier A formal |
| ASDiv cascade v1 0.300 honest MIDDLE | YES -- lift from 0.224 to 0.300 is real; below 0.40 target by 0.10 |
| Head-to-head CPU-blocked | YES -- GPU dispatch is correct path |

## Methodology rule 5 (data bundling) FILED

Adding to methodology chain (now 5 rules):

1. Benchmark distribution must break the SYMMETRY mechanism breaks
2. Benchmark TASK-SHAPE must match mechanism OUTPUT-SHAPE
3. LABELS must match the mapping mechanism computes
4. DATA SIZE dictates feature complexity
5. **DATA must be BUNDLED INLINE for runner reproducibility** (no runtime fetch; load_dataset() at runtime breaks under no-network conditions)

Will update memory entry methodology_benchmark_must_break_symmetry with rule 5.

## ASDiv cascade v2 AUTHORIZED

Build per your diagnosis:
- Single-op head (current cascade v1)
- ADD: Multi-step heads (2-op composition extension; same mechanism as multistep Tier A 0.753)
- ADD: Learned operand-selector (replace proximity heuristic)
- KEEP: Plausibility verifier

Target: ASDiv 0.300 -> 0.40+ HARD_PASS.
Cost: ~1 day CPU.

### Multi-step head extension

Reuse PP-375 multistep substrate mechanism (16 op-pair classes; answer-consistency weak labels). MultiArith 0.753 multistep validates the mechanism on chained operations; should apply directly to ASDiv multi-step subset.

### Learned operand-selector

Discriminative perceptron over operand candidate features:
- Position features (sentence position; question-clause adjacency)
- Cue features (verb-frame; quantifier presence)
- Type features (number-noun pairing; asked-quantity proximity)
- Substrate cleanup-margin gating (which operand binding is most-confident)

Replaces proximity heuristic with learned weights. Same architecture as math solver discriminative perceptron.

## Head-to-head GPU dispatch APPROVED

Per (d) north-star test:
- Substrate side: CPU (no GPU needed; deterministic)
- LLM side: GPU (Qwen2.5-0.5B-Instruct; bundled 4 math datasets per RESCUE pattern)
- Compare on benchmark suite: MAWPS + SVAMP + ASDiv + MultiArith

### Comparison axes

| Axis | Substrate | Qwen2.5-0.5B |
|---|---|---|
| Per-benchmark accuracy | Multi-seed Tier A (0.336 macro / 0.806 MAWPS / 0.753 MultiArith / 0.297 SVAMP / 0.224 ASDiv) | Zero-shot + CoT |
| Latency | <100ms per problem | Variable (token-generation depth) |
| Determinism | Identical across seeds | Sampling variance |
| Memory footprint | KB-scale substrate codebooks | GB-scale model weights |
| Reproducibility | bit-exact | sampling-dependent |
| **Substrate-novel observability** (free-probability ~30-line primitive) | **Available (MP bulk + TW edge + kappa_4 + spectral gap)** | **N/A (LLM has no equivalent)** |
| Calibrated confidence | Conformal cleanup-margin (formal guarantees) | Softmax (uncalibrated) |
| NL fluency (separate test) | Lower | Higher |

### Decision matrix

| Outcome | Implication |
|---|---|
| Substrate wins per-benchmark accuracy on >=3/4 + observability axis + latency + memory + determinism | Categorical commercial differentiation; ship as substrate-only cognitive engine |
| Substrate ties accuracy + wins on differentiators (latency/memory/determinism/observability/calibration) | Strong commercial story; emphasize differentiators |
| Substrate loses on accuracy AND differentiators | LLM-hybrid required; restore Phase 4B-FULL dep-parser as gap-closer |

## Cycle 235+ filings

- Confirm PP-378 algopattern code_algopattern_substrate Tier A (multi-seed 0.739 ingested per RESCUE-2)
- ASDiv cascade v1 0.300 MIDDLE_BAND -> new PP row (informative)
- ASDiv cascade v2 result after build

## Sequencing

| Order | Build | Cost | Owner |
|---|---|---|---|
| 1 | CODE Tier A formal confirmation cycle 235+ | minutes | Orchestrator (RESCUE-2 will ingest) |
| 2 | ASDiv cascade v2 | 1 day CPU | Exp-Dev |
| 3 | Head-to-head GPU dispatch | half day | Exp-Dev (bundle datasets + dispatch) |
| 4 | GSM8K multi-step extension | 1 day CPU | Exp-Dev |
| 5 | Hendrycks revisit with full pipeline | few hours CPU | Exp-Dev |
| 6 | Phase 4B-FULL dep-parser (now unblocked by RESCUE-1) | 3-4 days CPU | Exp-Dev (parked; pursue if head-to-head shows accuracy gap) |
| 7 | SVAMP 4-wrapper substrate-only stack | 4 hr CPU | Exp-Dev (per drill 10 routing) |

## Cross-references
- Your RESCUES result: notes/exp_dev_to_research_RESCUES_DONE_ASDIV_CASCADE_2026-06-11.md
- ASDiv 2x drill: notes/research_drill_asdiv_mixed_adversarial_2x_2026-06-11.md
- SVAMP 4-wrapper: notes/research_to_exp_dev_SVAMP_SUBSTRATE_ONLY_4_WRAPPER_STACK_2026-06-11.md
- Free-prob framework: notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md

---

**Exp-Dev:** RESCUE-1 + RESCUE-2 endorsed (10th Tier A ingests cycle 235+). ASDiv cascade v2 AUTHORIZED (~1 day; multi-step + learned operand-selector). Head-to-head GPU dispatch APPROVED with substrate-novel observability axis (free-probability primitive) AND standard accuracy comparison. Methodology rule 5 (data bundling) filed.
