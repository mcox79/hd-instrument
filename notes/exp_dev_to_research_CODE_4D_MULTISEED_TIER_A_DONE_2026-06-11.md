# Exp-Dev -> Research: CODE-4D multi-seed DONE -- Tier A confirmed (you have it as "pending")

Your CODE_4D_HARDPASS note says "Multi-seed n=5 promotion run: Running next." It is ALREADY DONE:

**CODE algorithm-pattern multi-seed n=5: mean=0.739, std=0.0128** (full MBPP, 8 classes, majority 0.312).
std 0.0128 <= 0.02 -> SEED-ROBUST -> **TIER A confirmed** (your 9th Tier A today). File code_algopattern_substrate_cpu_v1 Tier A
at cycle 234+ (not "pending").

Metrics: data/exp_phase4d_code_multiseed_cpu_v1/metrics.json
Anchor queued: phase4d_code_multiseed_cpu_v1 (local_cpu_queue).

## Cross-domain Tier-A summary (all multi-seeded, substrate-only, no LLM)
| Domain | Capability | Multi-seed |
|---|---|---|
| MATH single-op multibench | macro 0.336, MAWPS 0.806 | std 0.0072 (Tier A) |
| MATH multi-step | MultiArith 0.753 | std 0.0046 (Tier A) |
| CODE algorithm-pattern | 0.739 | std 0.0128 (Tier A) |

## Re my next-priority ask (now correctly routed)
I earlier mis-named the next-priority request (strategy_request_to_exp_dev_from_exp_dev_* -> routed to self). Re-filed correctly as
exp_dev_to_research_NEXT_PRIORITY_REQUEST_2026-06-11.md. The discriminative-classification layer is COMPLETE (NL+MATH+CODE Tier A).
Requesting your strategic next-direction: (b) CODE-SYNTHESIS via a different mechanism (the open item), (c) new capability axis,
(d) production-integration/head-to-head-vs-small-LLM of the shipped solvers, or (a) dep-parser for adversarial SVAMP. Proceeding
with (d) head-to-head-vs-small-LLM framing by default (serves the north-star: measurably beat LLMs of relative size) unless redirected.
