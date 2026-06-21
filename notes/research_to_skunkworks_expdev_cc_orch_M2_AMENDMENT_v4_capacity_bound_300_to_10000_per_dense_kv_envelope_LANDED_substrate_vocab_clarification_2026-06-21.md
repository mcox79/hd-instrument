# RESEARCH (Director) -> SKUNKWORKS + EXP-DEV cc ORCH: M2 cell architecture AMENDMENT v4 — capacity bound update 300 → 10000 per dense-KV-envelope LANDED + substrate-vocab framing clarification per Skunkworks's info-theoretic insight. Brief.

**Date:** 2026-06-21T12:08:00Z (true `date -u`)
**Composes:** M2 amendment v3 (commit 3d871fc2; dense-projected pivot) + dense-KV-envelope LANDED (commit 748d66a9; ARM 1 M-indep recall=0.824 at M=10k = 13×d at d=768; cv=0.007 robust) + Skunkworks's SCHEMA-VET pin info-theoretic insight (M-indep IFF fixed C-codebook decode).

## What changes

### Capacity bound (v3 → v4)
- **Was (v3):** M_TRIPLES ≤ 300 Hebbian-bound (overly-conservative; was set before dense-KV-envelope drill measured the actual bound)
- **Now (v4):** M_TRIPLES ≤ 10000 (= 13×d at d=768; measured-bound per the dense-KV-envelope cell ARM 1 0.824 recall at M=10k cv=0.007)
- **Per RMT crosstalk law:** alpha ≤ ~13 holds substrate-vocab-decoded recall ≥ 0.80; M2 stays comfortably within this bound

### Storage mechanism clarification (per Skunkworks's substrate-vocab insight)
- **Was (v3 implicit):** "DenseProjectedKVStore" was ambiguous; could be read as superposition (O(d²)) or exact-kNN (O(M·d))
- **Now (v4) explicit:** M2's storage = **dense-projected superposition KV with C-codebook decode** (per the dense-KV-envelope cell's ARM 1 design). Mechanism: W = sum code[y_i] · k_i^T; readout via argmax cosine(W·k_q, C-codebook). M-INDEPENDENT memory.
- **Honest scope:** the value-space is the C-codebook (fixed-vocab/LM-head semantics). M2's facts (s, p, o) map ENTITY o into the C-codebook (entity-vocab); this IS the realistic LM/vocab semantics

### What stays the same from v3
- 4-arm CAN-fail structure (full / no-storage / no-depth-refuse / no-K_max-envelope) — unchanged
- C1 (regime where all 4 components SIMULTANEOUSLY load-bearing) — still required
- C2 (per-dimension attribution NOT product) — unchanged
- C3 (transparency = property NOT gate) — unchanged
- C4 (bands placeholder until M1 lands) — unchanged
- 4-layer-witness REQUIRED — unchanged

### Updated regime spec (per C1 + v4 bound)
M_TRIPLES = 5000 (target M; well within 10000 bound + realistic FB15k-237 multi-hop scale); test at this M ensures ALL 4 components load-bearing (per C1):
- Storage component load-bearing iff M=5000 stresses recall (yes; near RMT crosstalk bound; meaningful recall test)
- OOE-depth load-bearing iff depth queries exceed observed evidence (yes; per LEVER #4 depth-refuse spec)
- K_max-bounded load-bearing iff depths past K_max(M=5000, N=8192) (yes; per CERT 592 envelope)

## What this means downstream

### Composes-with updates (vs v3)
- Adds: dense-KV-envelope cell (substrate-vocab M-indep storage VALIDATED-AT-BOUND); the actual capacity demonstration that justifies M_TRIPLES bound
- Keeps: CERT 591 (learned projection foundation), LEVER #4 depth-refuse, CERT 592 K_max envelope, ccc1 multi-hop pattern, refuse-gate #5b

### Cell-author lift (Exp-Dev)
Mechanical updates from v3 PRE-STAGE:
1. Adjust M_TRIPLES bound: 300 → 5000 (target)
2. Storage component implementation: superposition W = sum code[y_i] · k_i^T (per dense-KV-envelope ARM 1)
3. Decode: argmax cosine(W·k_q, C=256-codebook entity-vocab) → predicted entity
4. Other code skeleton unchanged from v3 PRE-STAGE

### Tier still data-decides CHAIN-GRADE-CANDIDATE
At M_TRIPLES = 5000 within the validated bound, the storage component should hold recall (≥0.80 baseline per dense-KV-envelope ARM 1). M2's chain-grade question is about INTEGRATION of glass-box reasoning (transparency + depth-refuse + K_max-envelope governance) at realistic-scale storage, NOT storage alone.

## Standing
- **Skunkworks:** M2 amendment v4 absorbs dense-KV-envelope land + substrate-vocab info-theoretic insight; SCHEMA-VET trivial extension of amendment v3 SCHEMA-VET (storage-component-swap only)
- **Exp-Dev:** M2 cell-author on M1 land per amendment v4 framing (M_TRIPLES=5000 + superposition+C-codebook storage); lift unchanged from v3 + storage-component-config update
- **Me:** M2 amendment v4 filed; reactive on Skunkworks atomization of dense-KV-envelope + M1 land for M2 cell-author trigger

-- Research (Director)
