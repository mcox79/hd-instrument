# Research -> Exp-Dev: 2-HOUR HIGH-PRIORITY BATTERY (parallel CPU + GPU)

**From:** Research session
**To:** Exp-Dev (primary)
**Date:** 2026-06-07
**Re:** User directive: "we need a strong body of high priority experiments to run for
the next 2 hours - please route"

8 cells across CPU + GPU lanes, parallel runnable, all return within 2 hours, all
inform major strategic decisions. Apply HARD-PASS / HARD-FAIL decision rules autonomously.

---

## GPU LANE (~2 hours total)

### G1. zkl_hypC_entropy_max REAL-ENCODER validation (URGENT)
HIGHEST STRATEGIC PRIORITY. Synthetic showed α=1.00 → ZKL=0.030 with F1 unchanged
(below HIPAA absolute 0.10), but sanity_ok=False. If Llama+MarianMT real-encoder
validates, ZKL story reverses to absolute HIPAA on shared encoder — eliminates Path D
premium-tier requirement. CRITICAL customer pitch upgrade.

Method: cycle 151 calibrated Llama+MarianMT harness; α=1.00 entropy-max; measure ZKL
+ F1 + sanity_ok.

HARD-PASS: ZKL ≤ 0.10 AND F1 within 3% baseline AND sanity_ok=True.
BORDER: ZKL 0.10-0.20.
HARD-FAIL: ZKL > 0.20 OR F1 drops > 5% OR sanity remains False.

Wall: ~2-3 hr GPU local (MarianMT dominates).

### G2. hotpot_fullwiki 3-baseline (replaces distractor 3-baseline)
Cycle 164 showed hotpot distractor 3-baseline at substrate=96% RAG quality. Fullwiki is
HARDER (full Wikipedia universe to retrieve from); the better-grounded headline number
for v1 demo.

Method: bare Qwen vs vanilla RAG vs substrate-augmented Qwen on hotpot_fullwiki at n=200+.

HARD-PASS: substrate matches RAG at >= 90% quality AND beats bare LLM by >= 0.15 F1.
HARD-FAIL: substrate drops below 70% RAG quality (fullwiki passages are too noisy for
substrate's whitening + K-hop).

Wall: ~45-90 min GPU local (depending on n).

---

## CPU LANE (~1.5-2 hours parallel)

### C1. K-hop audit replay (highest demo value)
30 min CPU. Demo asset for regulated industries. 20 multi-hop questions; substrate K-hop
produces auditable chain with Merkle proofs per step; replay each chain to verify
determinism; cryptographic verification of each step; compare to LLM chain-of-thought
non-determinism.

HARD-PASS: 100% deterministic chain replay; 100% Merkle verification; LLM CoT shows
divergence between runs (confirming "superficially plausible narrative" claim from
legal/clinical literature).

The categorical-win demo for the customer pitch. Run early so the asset is available.

### C2. ZKL T1 INLP nullspace projection feasibility (20 min)
From ZKL alternatives 3x drill. Gates T5 (combination test). Tests whether Llama L15
signal is linearly accessible for nullspace projection.

HARD-PASS: ZKL drops by >= 0.05 with F1 cost <= 3% via INLP alone.

### C3. ZKL T3 VIB sigma sweep (20 min)
Variational Information Bottleneck on KEY representations. Sigma sweep identifies the
operating regime where leakage drops without F1 loss.

HARD-PASS: any sigma achieves ZKL drop >= 0.05 at F1 cost <= 3%.

### C4. ZKL T4 GRL Pythia-160M rung-2 pre-test (60 min)
Gradient reversal layer for ZKL features on Pythia-160M (rung-2 scale). Gates the
adversarial fine-tuning path (highest ceiling but expensive at full scale).

HARD-PASS: ZKL drops by >= 0.10 with F1 cost <= 3% on Pythia-160M (rung-2 validation).

### C5. Sleep defrag pre-test (1-2 hr CPU)
Tests the 50-60% domain-specific implicit-generalization closure claim. 100 synthetic
fever-case Pattern B facts; co-occurrence aggregator; substrate aggregator output vs
LLM closed-book on the same aggregated regularity.

HARD-PASS: cosine sim >= 0.65 AND correct filler ranks #1 (per drill's recipe).

Validates a major customer-pitch axis (continual learning + implicit generalization).

### C6. Pattern B chain-k234 HF diagnostic (45 min)
Cycle 161 chain-k234 HF; Exp-Dev noted payload-bound chains interfere. Diagnose:
- Is it K-depth dependent? (sweep K=2, 3, 4 with smaller payload)
- Is it payload-magnitude dependent? (fix K, sweep payload size)
- Is it bundle-saturation dependent? (smaller N test)

HARD-PASS: identify specific failure mode → routes a future fix.
This is a follow-up diagnostic to convert the HF into a future MIDDLE-band rescue.

---

## Sequencing

Parallel start: G1 (URGENT GPU) + G2 (GPU after G1 starts) + C1 + C2 + C3 + C5 + C6 all
fire immediately. C4 (60 min) starts after C2/C3 to avoid CPU contention.

Wall time when parallelized: ~2 hours.

Total cells: 8 (2 GPU + 6 CPU).

## What this battery resolves at the end of 2 hours

- ZKL story unlocks (entropy-max real-encoder) OR remains locked qualified (Path D)
- HotpotQA fullwiki headline number for v1 demo (harder benchmark)
- K-hop audit replay categorical-win demo asset confirmed (or not)
- Three ZKL defense-in-depth candidates evaluated (T1 INLP + T3 VIB + T4 GRL)
- Sleep defrag 50-60% closure claim validated
- Pattern B chain-k234 HF diagnosed for future rescue

After this battery, the customer pitch can be confidently corrected for cycle 164 +
the next round of empirical results.

## Cross-references

- Cycle 164: notes/orchestrator_to_research_results_summary_2026-06-07_cycle164.md
- ZKL entropy-max URGENT validation: notes/research_to_exp_dev_zkl_entropy_max_real_encoder_validation_URGENT_2026-06-07.md
- ZKL alternatives 3x: notes/research_drill_zkl_alternatives_crazy_ideas_3x_2026-06-07.md
- Reasoning-code 3 pretests (K-hop audit replay): notes/research_to_exp_dev_reasoning_code_3_pretests_2026-06-07.md
- Sleep defrag pre-test: notes/research_to_exp_dev_sleep_defrag_pretest_authorize_2026-06-07.md
- Hotpot fullwiki routing: notes/research_to_exp_dev_hotpot_fullwiki_authorize_plus_composition_filter_dead_2026-06-07.md
- Post-compaction afternoon brief: notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

**END.**

**Exp-Dev:** 8 cells parallel-runnable, ~2 hours wall. G1 entropy-max real-encoder
validation is highest strategic priority (potential ZKL absolute-HIPAA unlock). C1
K-hop audit replay is highest demo-asset priority. Run all in parallel as capacity
allows. File synthesis as each batch completes.
