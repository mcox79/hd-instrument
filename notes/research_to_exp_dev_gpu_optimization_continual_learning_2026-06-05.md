# Research -> Exp-Dev: GPU-optimized Tier 6 variant + continual learning empirical test (user pushback on training-speed framing)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~08:30
**Subject:** User pushed back on "GPU can't be optimized" framing -- correctly. Tier 6 GPU MIDDLE was naive PyTorch on both sides. Substrate-specific GPU optimizations haven't been tested. Plus continual learning empirical test hasn't been done at production scale. Two new high-value CPU/GPU cells.

---

## Why this routing

User feedback on training-speed framing was correct:
- I said "GPU can't be optimized for substrate" -- that was lazy
- We measured PyTorch-naive substrate vs PyTorch-naive gradient baseline on GPU
- Substrate-specific GPU optimizations were NOT tested
- And critically: continual learning empirical test (the 10^9x advantage) was NOT empirically validated at scale

Two new cells address this directly.

---

## Cell GPU-OPT-1: Substrate-specific GPU optimization sweep

**Anchor:** `substrate_tier6_phase_d_gpu_optimized_kernels_v1`

### Architecture

Same Tier 6 Phase D architecture (4-layer char-LM; substrate-Hebbian attention) but with substrate-specific GPU optimizations:

```
Optimization 1: Bipolar arithmetic kernel
  Substrate W is bipolar {-1,+1}; multiplications become XOR-popcount
  Theoretical: 4-8x throughput vs float32 PyTorch general ops
  Implementation: custom kernel (Triton or CUDA)

Optimization 2: Fused Hebbian write kernel
  Standard PyTorch: x_outer = torch.outer(x, x); W += x_outer (2 kernel launches)
  Fused: single kernel does outer product + accumulation in-place
  Theoretical: 1.5-2x latency reduction (eliminates intermediate memory traffic)

Optimization 3: Batched substrate writes
  Standard: write patterns one at a time per training step
  Batched: write 64-128 patterns in single kernel call
  Theoretical: 5-10x throughput on Hebbian write phase

Optimization 4: Compiled gradient baseline (apples-to-apples)
  Baseline gradient transformer uses torch.compile (or Triton) for fair comparison
  Without this, substrate is compared against unoptimized baseline (unfair to substrate)

Conservative target: 1-2 of these 4 optimizations implemented in v1
```

### Pre-reg

- HP: substrate-hybrid GPU speedup vs torch.compile'd baseline >= 2.0x (matches CPU 2x; recovers training-speed claim on GPU)
- MID: speedup 1.5-2.0x (substrate-specific optimization helps but doesn't fully recover)
- HF: <1.5x (even optimized substrate doesn't show meaningful speedup on GPU; would honestly accept "substrate speedup is CPU/edge-specific")

### Cost + wall

- $0 GPU (remote 4060 Ti)
- ~30-60 min wall per variant; 3 seeds
- Engineering: ~4-8h (custom kernels take time)

### Strategic significance

Either way is informative:
- If HP: substrate GPU speedup recovers; product can claim "fast on GPU AND CPU"
- If HF: honest negative; product narrative pivots to CPU/edge + 10^9x continual learning advantage (which is hardware-independent)

User pushback was correct; this is the honest test.

---

## Cell CONT-LRN-1: Continual learning empirical test (10^9x claim validation)

**Anchor:** `substrate_continual_learning_empirical_10e9x_speedup_validation_v1`

### Why this matters

The 10^9x continual learning advantage is the BIGGEST claim in the training-speed narrative. Currently it's algebraic (substrate Hebbian write microseconds vs LLM fine-tune hours = ~10^6-10^9x ratio). We haven't empirically tested at production scale.

### Architecture

Two scenarios at substrate cognitive-core configuration (Pythia-160M-tier substrate; N=8192; 20 domains):

**Scenario A: Substrate adds 10,000 new facts**
- Starting state: substrate trained on some baseline corpus (~100k patterns)
- Action: write 10,000 NEW facts via Hebbian outer-product writes
- Measure: wall time + final accuracy on (a) old facts (no catastrophic forgetting) and (b) new facts

**Scenario B: Equivalent LLM fine-tune adds same 10,000 facts**
- Starting state: Pythia-160M base
- Action: fine-tune on 10,000 new facts (e.g., 1 epoch on small fine-tune corpus)
- Measure: wall time + final accuracy on old facts and new facts

### Pre-reg

- HP: substrate scenario A is >= 1000x faster than scenario B for matched final accuracy
  AND substrate retains >= 95% of old facts (no catastrophic forgetting)
  AND LLM fine-tune loses some old facts (typical catastrophic forgetting)
- MID: 100-1000x speedup
- HF: <100x speedup (substrate continual learning advantage is much smaller than algebraic claim)

### Cost + wall

- Substrate scenario: $0 CPU; ~minutes wall (substrate writes are microseconds)
- LLM fine-tune scenario: ~$5-20 cloud H100; ~30-60 min wall
- Total: ~$5-20 + 1 day engineering

### Strategic significance

This is the BIGGEST training-speed claim in our narrative. If HP: substrate's continual learning advantage is empirically anchored. If HF: we have to soften the claim.

User explicitly flagged training speed as strategic-critical. This test is the load-bearing empirical anchor.

---

## Priority

**Cell CONT-LRN-1 (continual learning empirical)** is the higher-strategic-value of the two:
- The 10^9x continual learning claim is the biggest unique substrate advantage
- Currently completely unvalidated empirically
- Cheap ($5-20) and fast (1 day)

**Cell GPU-OPT-1 (GPU optimization)** is more engineering-heavy but addresses user pushback directly:
- 4-8h engineering for substrate-specific kernels
- Either outcome is informative

Recommend: build CONT-LRN-1 first (cheaper + higher strategic value). Then GPU-OPT-1 when GPU runner inspection is done (Action 3 from Testbed routing).

---

## Honest framing

Both cells test specific user-flagged concerns:
- "Training can't be optimized for GPU?" -- GPU-OPT-1 tests this directly
- "Did we test continual learning?" -- CONT-LRN-1 tests this empirically

These are not padding -- they're addressing genuine empirical gaps the user surfaced.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each cell tests a specific user-flagged empirical gap
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF + WHY-DRILL paths per cell
- Per [[feedback-pressure-test-negative-findings]]: HF outcomes have clear product-narrative implications
- ASCII-only

PROT-018: anchors with `_gpu_optimized_kernels_v1` and `_continual_learning_empirical_10e9x_v1`
PROT-021: source=remote 4060 Ti + Lambda cloud; n_seeds=3

---

**END.**

**Exp-Dev:** two new cells addressing user pushback on training-speed framing. CONT-LRN-1 (continual learning empirical) is higher priority -- $5-20 + 1 day, validates the 10^9x claim that's load-bearing in the product narrative. GPU-OPT-1 follows when GPU runner is inspected (Testbed Action 3).

**Standing for: CONT-LRN-1 + GPU-OPT-1 verdicts.**
