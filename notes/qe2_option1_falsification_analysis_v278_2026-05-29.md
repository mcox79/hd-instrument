# QE-2 Option-1 falsification analysis (user-delivered, v278)

## Failure mode localized: softmax saturation = argmax-bottleneck one layer deeper

User's analysis: at high SNR on BSC readout, softmax becomes effectively argmax. The top-K soft mixture collapses to a delta function. The "soft propagation" reverts to hard propagation. **Option-1 doesn't avoid the argmax bottleneck; it defers it one layer.**

This is a clean falsification, not an ambiguous result.

## Theoretical strengthening of operational-layer-invariance pattern

The argmax-readout-decoupling isn't a bug you can route around by softening the readout. It's a STRUCTURAL feature of how Kerdock codebooks interact with retrieval at meaningful SNR.

**Substrate wants to be discrete at the operational layer.** This is now a 5-witness pattern (PB-3, Axis-4, KF-5, BE-1, QE-2 Option-1) — adds Option-1 falsification as 5th witness.

## Probability adjustment

| Path | Pre-Option-1 estimate | Post-Option-1 estimate |
|---|---|---|
| Option 1 (top-K soft mixture) | P=0.30-0.35 | CLOSED (HARD_FAIL) |
| Option 2 (direct distribution) | P=0.34 | (unchanged; not yet tested) |
| Option 3 (spectral propagation) | P=0.30 | P=0.25-0.35 (carries Option-1's remaining mass) |
| Coherent multi-hop overall (d=50+ rescue) | P=0.50-0.60 | **P=0.25-0.35** |

## Why Option-3 is the structurally right next test

Option 3 propagates substrate's **internal continuous structure** (spectral information, eigenstructure) which **doesn't saturate the way softmax does**. If multi-hop happens at the internal layer (not the operational layer), it's theoretically more consistent with where substrate's continuous dynamics actually live.

This is also the user's two-layer architecture framing applied: Direction B (internal-layer) work, not Direction A (operational).

## Fallback narrative if Option-3 also fails

User: "If Option 3 also fails, coherent multi-hop closes as a research direction and the multi-hop story locks at current depth 25-50 at 22-40% accuracy. **That's not catastrophic** -- the substrate-as-memory-layer positioning doesn't require deep multi-hop because LLMs handle that. But it does close the 'substrate does its own reasoning' framing more definitively."

Strategic implication: the substrate's product positioning is robust to coherent multi-hop's outcome. If it works, substrate gains a category-defining capability. If it doesn't, substrate's compliance-grade-auditable-memory positioning is unchanged.

## Concrete next-test design (Option-3 spectral propagation)

Propagate substrate's pre-argmax spectral signature (W applied to the query, NOT softmax) across multiple hops. At depth d, project final spectral state back to codebook via argmax. No intermediate softmax = no saturation.

Specific design:
- s_1 = W * q (full N-dim spectral state)
- s_{t+1} = W * (s_t / ||s_t||) -- propagate normalized spectral state (no softmax)
- Final readout: argmax over codebook similarity at depth d
- Depth sweep: d in {5, 10, 25, 50, 100}
- 3 seeds, single-batch CPU smoke
- Baseline: chained-argmax-cleanup at same depths

Expected runtime: ~1hr CPU (similar to Option-1 smoke).

HARD_PASS criterion: d=50 acc >= 0.65 (same as Option-1)
HARD_FAIL: d=50 acc <= 0.35

If HARD_PASS: ship FULL multi-seed + write up as substrate-novel multi-hop mechanism.
If HARD_FAIL: coherent multi-hop closes; substrate's multi-hop story locks at d=25-50 22-40% (LLMs handle deeper reasoning anyway per user).

## Companion exp_dev dispatch required

Scaffold experiments/exp_qe2_spectral_propagation_v1_n4096.py (Option-3 implementation). Ship to CPU queue. ~1hr smoke. If HARD_PASS, dispatch FULL multi-seed + Tier-1 promotion verdict_handler.
