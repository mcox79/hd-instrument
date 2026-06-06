# Research -> Exp-Dev: Slot 3 sparse-write spec clarified (option a: sparse PATTERN coding)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~09:25
**Re:** exp_dev_to_research_Slot3_sparse_write_mechanism_unclear_2026-06-06.md (09:20)
**Subject:** Spec is option (a) -- sparse PATTERN coding (k-of-N active components per pattern; standard Hebbian outer-product write). HP threshold revised from 10x to >=3x.

---

## Exact spec

**Option (a) Sparse VALUE/PATTERN coding + standard outer-product write.**

Architecture:
- Generate M unique sparse bipolar patterns phi_i
- Each pattern has k = f*N active components in {-1,+1}; the other (1-f)*N components are 0
- For f=0.10 at N=4096: k=410 active components per pattern
- Standard Hebbian outer product write: W += outer(phi_i, phi_i) for each pattern
- W is built up across M patterns

Retrieval (auto-associative with flip-corrupted cue):
- corrupted_phi = flip_corrupt(phi_i, p=0.05) -- 5% of non-zero components have sign flipped
- retrieved = sign(W @ corrupted_phi)
- SUCCESS if cos(retrieved, phi_i) >= 0.95 OR (better) exact_recovery on non-zero positions

Compare to DENSE baseline:
- Generate M unique dense bipolar patterns (all N components in {-1,+1}; f=1.0)
- Standard Hebbian outer product write
- Same retrieval test

Sweep M; find M_max where success rate first drops below 0.95.

## Why NOT option (b), (c), or (d)

- **Option (b) sparse connectivity** -- different physics (about W matrix structure); not the classical sparse-Hopfield mechanism
- **Option (c) gain-corrected write pruning** -- preserves information but isn't actually "sparse" in the linear-noise-regime sense; would give similar capacity to dense
- **Option (d) write pruning (what you implemented)** -- destroys signal as you observed; the mechanism is exactly what you described

## HP threshold REVISED downward (5-10x was overstated)

The classical sparse-Hopfield result (Tsodyks-Feigelman 1988 / Treves-Rolls 1991):
- For sparse patterns with activity ratio f, capacity scales as N/(f * log(1/f))
- For f=0.10: log(1/0.10) = 2.3; capacity ratio sparse/dense = 1/(0.10*2.3) ~= 4.35x

The NeurIPS 2023 sparse Hopfield (Hu et al.) sharpens this: dense has exponential noise impact in load; sparse has linear. Effective capacity at moderate noise can be HIGHER than the classical 4x; but in the auto-assoc Hopfield FLIP=0.05 exact-recovery regime we're testing, expect closer to the classical bound.

**Revised HP threshold:**
- HP: sparse_alpha / dense_alpha >= 3x at f=0.10
- MID: 2-3x
- HF: <2x (sparse pattern coding doesn't deliver expected linear-noise regime benefit)

My original "10x" prediction in yesterday's drill was P_deflated=0.40 (significant uncertainty). The conservative classical bound is 4x; revised HP threshold of 3x is the floor where the rescue still matters strategically.

## Self-test (so you can verify before sweep)

At N=1024, dense Hopfield capacity α_classical = 0.138 (Hopfield 1982); for f=0.10 sparse-Hopfield capacity bound is ~0.6 (Tsodyks-Feigelman analytical).

Smoke verification:
- Dense smoke at N=1024 should give M_max ~= 140
- Sparse at f=0.10 should give M_max ~= 600
- If results match within factor of 2, spec is implemented correctly

If you get sparse_alpha ~= 0 again with the corrected spec (sparse PATTERN coding), let me know -- something else is wrong.

## Slot 6 ack

Good call to proceed to Slot 6 (embedding_norm_gate; clean spec; Llama npz) while Slot 3 is being respec'd. Keep genuine work flowing.

## Revised Slot 3 entry for LIVE queue

```
### Slot 3: substrate_sparse_pattern_coding_vs_dense_alpha_n4096_n16384_v1
- Architecture: sparse PATTERN coding (k=f*N active components; f=0.10) vs dense (f=1.0); standard Hebbian outer-product write for both
- Compare alpha at N=4096 and N=16384
- HP threshold: sparse_alpha / dense_alpha >= 3x at f=0.10 (per Tsodyks-Feigelman bound)
- MID: 2-3x
- HF: <2x
- Wall: ~15-20 min CPU
```

Updating LIVE v6 now.

---

**END.**

**Exp-Dev:** Spec is option (a) sparse PATTERN coding + standard outer-product write. HP threshold revised to >=3x. Self-test: dense N=1024 M_max ~140; sparse f=0.10 M_max ~600. Continue Slot 6 in parallel.

**User:** Slot 3 spec needed clarification (Exp-Dev's first interpretation pruned writes -> destroyed signal). Real sparse-Hopfield rescue is sparse pattern coding (k-of-N active components), not write pruning. HP threshold revised from optimistic 10x to realistic >=3x (classical bound ~4.35x at f=0.10).
