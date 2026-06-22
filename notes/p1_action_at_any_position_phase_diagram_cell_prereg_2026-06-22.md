# p1 — action-at-any-position-in-the-phase-diagram cell pre-reg (USER-directed lane sub-item c)

**Date:** 2026-06-22
**Lane:** USER-directed latent-capability (2026-06-22): "substrate acts at any position in the phase diagram + data survives phase transformations." Sub-items (a) phase-portrait v1 inventory + (b) data-survives-transform audit SHIPPED in [phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md](phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md). This is sub-item (c) — the new-evidence-generating cell.

## HEADLINE — plain English first (Fix #13)

**The existing chain-grade evidence shows the substrate is phase-diagram-portable across DIFFERENT atom sets measured at DIFFERENT operating points.** What no single chain-grade atom directly tests is whether **the SAME atom set, stored once at operating point P_0, can be retrieved after the substrate is transformed to P_1**. That's the literal "action-at-any-position" claim — operating-point-portability for a fixed payload.

The cell stores K=200 fact-atoms at one (V_C, N_DIM, α) corner, then re-builds the substrate at a DIFFERENT corner (same key encoder; different codebook/N_DIM/load), reuses the SAME key tokens to attempt retrieval, and measures recall delta vs the within-P_0 baseline.

**HARD-PASS** = recall(P_0 → P_1) ≥ 0.80 × recall(P_0 within) at the new operating point on three (P_0, P_1) pairs that span the phase diagram.
**HARD-FAIL** = recall(P_0 → P_1) ≤ 0.20 × baseline on any of the three pairs (data destroyed by the transform).
**MIDDLE_BAND** = 0.20 < ratio < 0.80 on ≥ one pair (partial survival; characterize the floor).

P estimate **0.45** (novel-synthesis cap; the chain-grade priors for transform-survival lift the floor above 0.30 but the operating-point-shift specifically has no direct chain-grade precedent).

## Mechanism (cell design)

For each pre-registered (P_0, P_1) pair:

1. **INGEST at P_0:** build substrate with `(V_C_0, N_DIM_0, α_0)`; ingest K=200 FB15k-237-style fact-atoms (or text8-derived key-value pairs). Pre-compute the codebook from P_0 corpus. Encode keys via frozen pythia-160m (held constant across arms per Fix #16 discriminator-isolation).
2. **STORE atom-set A_0:** capture (a) the key codebook indices for the K atoms, (b) the value HD-vectors, (c) the Hebbian-write log (which `(k_i, v_i)` outer-products fired). Treat `A_0` as the portable artifact.
3. **REBUILD at P_1:** create a NEW substrate with `(V_C_1, N_DIM_1, α_1)`. Recompute the codebook with the SAME corpus + same encoder; the codebook ALPHABET differs (different V_C) but the key encoder pipeline is held fixed. **The substrate-internal W matrix is BLANK at P_1 start.**
4. **REPLAY A_0 INTO P_1:** for each of the K atoms, re-encode its key with P_1's codebook (different indices, same encoder), write `(k_i^{P_1}, v_i)` via Hebbian outer-product into P_1's W. Note: `v_i` is preserved verbatim from P_0 (the value HD-vector is the portable payload).
5. **RETRIEVE at P_1:** for each test key, encode at P_1, retrieve via P_1's W, score against the original value HD-vector. Compute recall.
6. **BASELINE arms (REQUIRED — Fix #16 discriminator-regime check):**
   - **WITHIN_P_0:** retrieve all K atoms at P_0 itself (control; expected ≥ 0.90 baseline; below this the cell is invalid).
   - **P_0_TO_P_1_REPLAYED:** the main mechanism (steps 4-5).
   - **P_1_FRESH_INGEST:** ingest K atoms freshly at P_1 from the original corpus (no portability; tests whether P_1 alone supports the load).
   - **P_1_BLANK_RECALL:** retrieve test keys against an empty P_1 W (must collapse to chance; harness sanity-check; the floor reference for the substrate-survives delta).

## Three pre-registered (P_0, P_1) pairs (spanning the phase diagram)

| Pair | P_0 | P_1 | Transform class | Predicted ratio | HARD-PASS bound |
|------|-----|-----|------------------|------------------|------------------|
| **A: V_C lift** | V_C=1024, N=16384, α=0.012 | V_C=2048, N=16384, α=0.012 | codebook-resolution lift; same N, same load | ≥ 0.85 | ≥ 0.80 |
| **B: N_DIM lift** | V_C=1024, N=16384, α=0.012 | V_C=1024, N=32768, α=0.006 | N doubled; α halved (same K count, larger substrate) | ≥ 0.85 | ≥ 0.80 |
| **C: joint lift** | V_C=1024, N=16384, α=0.012 | V_C=2048, N=32768, α=0.006 | BOTH lifted; larger codebook + larger substrate | ≥ 0.80 (compounded uncertainty) | ≥ 0.80 |

The three pairs are the three independent orthogonal axes in the (V_C, N_DIM) corner of the phase diagram from the v1 inventory.

## Config

- **K=200 fact-atoms**, **N_seeds=3**, **N_DIM ∈ {16384, 32768}**, **V_C ∈ {1024, 2048}**, **3 (P_0, P_1) pairs × 4 arms = 12 arms**.
- **Encoder held fixed:** pythia-160m mean-pool, fp32, seq~64 (per Fix #17 rate-norm: ~67 ms/fact local_cpu / ~51 ms remote_cpu inferred; 200 facts × 51 ms ≈ 10 s per arm per seed × 12 arms × 3 seeds ≈ 6 min total encoding wall; W-build + recall adds modest overhead).
- **Substrate-only-decode gate:** zero LLM forward calls at retrieval. The pythia encoder runs ONCE per arm during ingest; retrieval uses only substrate ops (Hebbian inner products + codebook NN + value HD scoring).
- **Recall metric:** cosine-sim(retrieved, original_v_i) ≥ 0.5 = correct (sweeps over threshold reported as supplementary; the 0.5 is the pre-reg discriminator).
- **Dispatch target:** remote_cpu (matches the ~5-10 min wall estimate; fits Fix #17 budget; Path A V_C=4096 will be done long before this).

## HARD bands (sacrosanct per pre-reg)

- **HARD-PASS chain-grade:** ALL THREE pairs achieve ratio ≥ 0.80 (recall_P_0_TO_P_1 / recall_WITHIN_P_0) AND P_1_BLANK_RECALL collapses to ≤ 0.10 (sanity floor) AND substrate-only-decode gate preserved at every arm.
- **HARD-FAIL:** ANY pair drops to ratio ≤ 0.20 OR substrate-only-decode gate violated.
- **MIDDLE_BAND:** at least one pair in (0.20, 0.80); ledger as MEASURED_MECHANISM with the specific transform-class that drops the ratio characterized.
- **HONEST_NEGATIVE-eligible regime:** if pair A passes but pair B and C fail, the cell is honest-negative-at-N-DIM-shift (the V_C axis survives transforms but the N axis does not). This is information-positive even if not chain-grade.

## Discriminator-regime check (Fix #16)

The cell's 4-arm matrix has the structure: WITHIN_P_0 must succeed (else harness broken); P_1_BLANK_RECALL must fail (else recall is artifact of test-key encoding); P_1_FRESH_INGEST shows P_1's capacity independently; P_0_TO_P_1_REPLAYED is the mechanism. **If P_1_FRESH_INGEST ≈ P_0_TO_P_1_REPLAYED, that's the LOAD-BEARING evidence that the portability is real (data survived; not just "P_1 happens to support this load").** If P_1_FRESH_INGEST >> P_0_TO_P_1_REPLAYED, the data partially survived; if P_1_FRESH_INGEST << P_0_TO_P_1_REPLAYED, the portability mechanism is doing something fishy (HALT-and-investigate).

## Composes with

- **L2 substrate-native LM closure stack:** action-at-any-position lets the LM be reconfigured between (V_C, N_DIM) corners without losing prior writes — load-bearing for incremental scaling.
- **L3 continual-learning (c1):** data-survives-transform is the same mechanism class as "writes-survive-new-writes"; HARD-PASS here strengthens the c1-favorable surprise.
- **Brain-drill #6 modular K-macrocolumn:** modular stores DEFINE per-shard phase-diagrams; the m1 cell's K=8 vs K=1 contrast is a phase-diagram axis itself; p1 establishes the single-shard portability baseline that m1's modular contrast extends.
- **Phase-portrait v1 inventory:** p1 ADDS a new chain-grade axis (operating-point-portability) to the portrait if HARD-PASS.

## What this DOESN'T claim

- Does NOT claim portability across ENCODER swaps (`audit_core_C2_C3_whitened_pythia/llama1b` PASS-pair already covers that; orthogonal axis).
- Does NOT claim portability across PROJECTION transforms (`EXP_kv_learned_projection_v1` HARD_PASS already covers that; orthogonal axis).
- Does NOT claim cross-DOMAIN portability (text→code / text→math); explicitly out-of-scope for this cell.
- Does NOT claim long-horizon TEMPORAL persistence (durability_cron is the relevant existing tool; orthogonal).

This cell isolates **operating-point-shift portability** as one specific axis of the broader "data survives phase transformations" claim.

## SCHEMA-VET status

Pre-reg authored as cert-trail durable artifact. SCHEMA-VET (cert-owner authority) deferred to next cycle when spawn budget reopens (would dispatch hdi_skunkworks teammate for SCHEMA-VET + ratification before cell-author dispatch). Until SCHEMA-VET clears, this is a Director pre-reg DRAFT — load-bearing within the work queue but not gated for dispatch.

## Dispatch readiness (when SCHEMA-VET clears)

- Cell-author task: build `exp_p1_action_at_any_position_phase_diagram_v1.py`; smoke-VET; measure ONE seed at near-full (Fix #17); dispatch to remote_cpu_queue.
- Expected wall: 6-10 min total (per Fix #17 rate-norm); fits remote queue budget easily.
- Spawned via `hdi_exp_dev` agent with this artifact as the pre-reg pointer.

— Research (Director); p1 pre-reg DESIGN cert-trail artifact; no addressee.
