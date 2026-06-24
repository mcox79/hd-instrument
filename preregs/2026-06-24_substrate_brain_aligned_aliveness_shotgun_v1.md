# prereg: substrate_brain_aligned_aliveness_shotgun_v1

Date: 2026-06-24
Author: exp_dev
Cell: `experiments/exp_substrate_brain_aligned_aliveness_shotgun_v1.py`
Routing: local_cpu_queue (pure numpy; CPU only; ~20-30min wall)
Driver: USER directive 2026-06-24 "we need to find where the substrate is alive AND be sure we're testing for the RIGHT things."

## Strategic rationale

Current aliveness measurement leans on next-char-BPC over a unigram baseline. Substrate sits at +0.27 BPC / +61% top-1 there. But the brain does not do next-character prediction. The brain does:

1. Pattern completion (recover full memory from a partial cue).
2. Compositional generalization (substitute parts of learned structure).
3. Working memory (hold ~7 items, retrieve any).
4. Bidirectional prediction (fill missing element given before+after).

Brain achieves near-perfect on each of these trivially. Substrate's underlying machinery (HRR bind/unbind, sparse-bipolar codebook, superposition bank) is built for these. If substrate fails, that is a real aliveness gap. If substrate succeeds, substrate is MORE alive than current next-char metric implies and the substrate-as-LM struggle is task-mismatch, not aliveness-gap.

## Mechanism

Pure NumPy. No learning, no plasticity, no cf-RPE. N_DIM=8192, sparse-bipolar codebook with f=0.05 (~5% nonzero entries valued +/-1). HRR bind = circular convolution via FFT; unbind = circular correlation. Bank = superposition (sum) of bindings.

## Pre-reg bands (sacrosanct both directions per NEGATIVITY-BIAS rule)

### ARM 1 -- Pattern Completion (sanity floor)
- Codebook of M=500 sparse-bipolar patterns; each pattern is a "memory."
- Corrupt by zeroing half the nonzero coords of each pattern (the cue).
- Brain-aligned cleanup: nearest-codebook-entry by cosine (content-addressable retrieval).
- HARD_PASS: median post-cleanup cosine > 0.85 (equivalent to >85% top-1 codebook recovery).
- HARD_FAIL: median post-cleanup cosine < 0.50.
- Auxiliary metric reported: top1_recovery_rate AND median cue-only cosine (~sqrt(1-corrupt_frac) ~ 0.707 by construction; baseline for the lift via cleanup).
- **SANITY**: ARM 1 MUST HARD_PASS for any positive verdict. If ARM 1 fails the cell HARD_FAILS regardless of arms 2-4.

### ARM 2 -- Compositional Generalization
- 20 subjects x 20 objects = 400 pairs; 50% coverage (200 train, 200 heldout).
- For each heldout (A_i, B_j): unbind(bank, A_i), top-1 over OBJ codebook (20).
- HARD_PASS: holdout top-1 > 0.70 (brain-canonical high).
- HARD_FAIL: holdout top-1 < 0.20 (close to chance 1/20 = 0.05).

### ARM 3 -- Working Memory Capacity (Miller 7+/-2)
- For k in {1, 2, 4, 7, 10, 15}, bind k (slot, item) pairs into one bank.
- Retrieve each item via slot; argmax over item-pool codebook (ITEM_POOL = max(20, 2*K_MAX)).
- 60 trials per k. Accuracy at each k.
- k_capacity_at_90pct_accuracy = largest k with accuracy >= 0.90.
- HARD_PASS: min capacity across seeds >= 7 (Miller).
- HARD_FAIL: min capacity across seeds < 4.

### ARM 4 -- Bidirectional Prediction
- Sequence of 100 items drawn from vocab=50.
- For each interior t: bind key=bind(prev, next), value=curr; superpose into bank.
- Recover curr via unbind(bank, key); top-1 over vocab.
- HARD_PASS: top-1 > 0.50 (brain-canonical easy with context).
- HARD_FAIL: top-1 < 0.10 (chance 1/50 = 0.02).

## Cell-level verdict logic

- `BRAIN_ALIGNED_ALIVE`: all 4 arms HARD_PASS.
- `BRAIN_ALIGNED_PARTIAL`: 2-3 of 4 arms HARD_PASS.
- `BRAIN_ALIGNED_DEAD`: 0-1 arm HARD_PASS.
- `HARD_FAIL[sanity_floor]`: ARM 1 not HARD_PASS regardless of others.

## Seeds & config

- Full: seeds = [7, 17, 23] (n=3).
- Smoke: seed = [0] with reduced grid (ARM1_M=50, ARM2 8x8, ARM3 k in {1,2,4,7}, ARM4 seq=20 vocab=15).
- Per-seed checkpointed via `experiments/_seed_checkpoint.py`.
- CONFIG_VERSION includes every result-affecting param.

## Timeout estimation

Smoke target ~30s (1 seed, small grids). Full estimate: ~20-30min wall on CPU (3 seeds; ARM 2 holdout = 200 unbinds per seed; ARM 3 = 6 k-values x 60 trials x up-to-15 retrievals = ~5400 retrievals per seed; ARM 4 = 98 retrievals per seed; ARM 1 = 500 patterns per seed). Each retrieval is one FFT pair + one codebook matmul at N=8192. We budget timeout=1800s (30min) per USER directive.

## Pre-flight gates passed before dispatch

- [ ] `--self-test` exits 0 (HRR involutive + ARM tiny configs all pass).
- [ ] `--smoke` produces valid metrics.json with REQUIRED_FIELDS (verdict, verdict_msg, elapsed_s, summary).
- [ ] Cell file commit-first (this prereg + script).
- [ ] queue_add gate clears (no PROT-018 since anchor has no `_n<N>` suffix; PROT-021 N/A for timeout<14400s).

## WHAT_THIS_DOES_NOT_SHOW

These probes test brain-canonical aliveness dimensions on substrate primitives IN ISOLATION. They do NOT show:
- Language-task performance (no text corpus involved).
- Learning / plasticity (no cf-RPE, no gradient updates).
- Chain-grade integration with the rest of the substrate KG.
- That any specific downstream task will benefit.

A BRAIN_ALIGNED_ALIVE verdict is a MECHANISM characterization, not a cert of any downstream task.

By-construction notes:
- ARM 1 cue carries half the original bits at full sign-fidelity; cosine recovery directly reflects info preserved by the sparse-bipolar code (not by superposition cleanup).
- ARM 2-4 measure HRR bind/unbind crosstalk under superposition.
- Capacity in ARM 3 falls when M*f^2 crosstalk exceeds signal (theoretical scaling).

## Cites

- USER brain-aligned aliveness directive 2026-06-24.
- substrate-as-LM test harness rigged audit 2026-06-23.
- HRR involutive intuition + sparse-bipolar 20-300x bundle lift (operational findings 2026-06-23 late session).
- Miller 1956 seven plus minus two.
