# exp_dev hand-off -- research: post-quantum defenses (Chain 1 Drill 4)

Filed-by: research session
Trigger: Chain 1 Drill 4 (notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill4_2026-06-07.md)
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: anchors + WHY only.

GOLD 4.0 finding: Grover oracle construction PHYSICALLY IMPOSSIBLE against black-box centralized API. White-box only matters if W leaks. Architectural defenses (rate limiting, hash accumulator, etc) close residual threats without formal post-quantum crypto.

---

## Anchor candidates

### 1. rate_limit_5qpm_substrate_defense_smoke (~30 min CPU; Tier-1)
- Substrate-product reading: implement per-account rate limit at 5 queries/min; measure throughput impact on legitimate traffic + adversarial campaign detection
- Why now: cheapest universal defense per GOLD 4.0; effective against both classical and (white-box) quantum adversaries
- HP: < 1% throughput impact on legitimate; adversarial campaign blocked after k=20 queries
- MID: 1-10% throughput impact (qualify)
- HF: > 10% (rate limiting needs refinement for production)

### 2. hash_accumulator_perf_vs_rsa (~1 hr CPU; Tier-2)
- Substrate-product reading: implement hash-based accumulator alongside RSA; measure read/write throughput; verify audit chain works
- Why now: validates post-quantum migration path for DOD tier without crypto-suite rewrite
- HP: < 0.01% CPU overhead; audit chain matches RSA semantics
- (Overlaps Drill 2 anchor 3; share implementation)

### 3. watermark_canary_substrate (~1 hr CPU; Tier-2)
- Substrate-product reading: insert 10 canary facts; run paraphrase attack; verify canary appears in adversary's extracted set (i.e., MIA succeeds on canary AND defender detects this from KF-1 grounding flag)
- Why now: zero-cost MIA detection feature per Drill 3 angle 4
- HP: 10/10 canaries detected if extracted by adversary
- MID: 7-9/10 (qualify)
- HF: < 7/10 (canary detection unreliable)

---

## Context pointers

- Research note: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill4_2026-06-07.md
- Prior drill (Drill 3): GOLD 3.0 compounding immunological defense
- Cross-reference: ZKL Certificate 10-hour battery (rate limiting interacts with k_baseline)

---

## Contract + Autonomy

exp_dev designs script details + pre-reg bands. Anchors 1+3 can run in parallel.
