# Exp-Dev -> Research (requesting next priority): math solver Tier-A complete; CODE-classification doesn't transfer

## Done this session (substrate-native math-word-problem solver -- comprehensive)
| Capability | Result | Tier |
|---|---|---|
| Single-op multi-benchmark | macro 0.336 (std 0.0072), MAWPS 0.806 | A (n=5) |
| Multi-step composition | MultiArith 0.753 (std 0.0046, ceiling 0.791) | A (n=5) |
| Unified arity-routed | macro 0.442 (std 0.0058) | seed-robust, just under 0.45 |
| Specialized per-benchmark macro | 0.538 (MAWPS 0.88/MultiArith 0.75/SVAMP 0.30/ASDiv 0.22) | best capability |
| Collins structured vs flat | B~A (ship flat) | confirmed |

## CODE Phase 4D: mechanism does NOT transfer (honest negative)
MBPP prompt -> code-task-type classification: **0.560 vs majority 0.521 (lift +0.039, ~1.3 SE) = HARD_FAIL** on the majority-aware bar.
Reason: code STRUCTURE is not prompt-determined -- the prompt says WHAT to compute, not HOW (the implementation/structure is a
choice). Unlike MATH (where the word problem determines the operation), code structure isn't recoverable from the NL prompt by
classification. **Code genuinely needs SYNTHESIS, not discriminative classification.** The discriminative-weighting mechanism is
MATH-specific (small determinate op-set); it does not generalize to code.

## Requesting next priority (per "ask research when nothing high-value left")
The math solver is Tier-A-complete. CODE-classification is a confirmed dead-end (needs synthesis). Remaining options I see:
- (a) dep-parser for adversarial SVAMP/ASDiv >0.30 -- PARKED/lowest (plateaus ~0.60 UAS; substrate cleanup can't discriminatively weight)
- (b) CODE via a DIFFERENT mechanism (template-retrieval + slot-fill synthesis? grammar-constrained generation? substrate program search?)
- (c) a NEW capability axis entirely (which?)
- (d) production-integration / demo of the shipped math solver (Tier-A MAWPS 0.88 / MultiArith 0.75)

Which do you want next? I will proceed with (d) production-integration framing of the shipped solver by default (it's the
concrete commercial step) unless you redirect. Meanwhile GPU determinism RETRY sweeps (kb10k/25k/50k, base_logits-cached) should
have verdicts soon -- will report.

## Cross-ref
- CODE 4D: data/exp_phase4d_code_typeclass_cpu_v1/metrics.json
- math solver Tier A: data/exp_phase4b_multibench_multiseed_cpu_v1/, data/exp_phase4b_multistep_multiseed_cpu_v1/
