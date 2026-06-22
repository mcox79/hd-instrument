# Capability gap audit — chain-grade mechanisms vs `hdlab/` operational primitives (2026-06-22)

**Origin:** USER 2026-06-22 directive — "Are we keeping the substrate updated and operational? When clear improvements land, are they implemented in the substrate? ... Do we also evaluate what the missing or underperforming parts are?"

**Operationalizing:** the new results-to-application cadence (`feedback_results_to_application_cadence_same_cycle_atomize_and_hdlab_update_USER_2026-06-22.md`) — every cert-grade HARD_PASS should drive a hdlab/ code primitive update if the cell validated a reusable mechanism. First instance of the cadence's gap-evaluation step (every 5-7 cycles).

**Method:** scour `data/substrate_index/meta/cert_ledger.jsonl` (647 rows) for chain-grade atoms matched against a primitive-class lexicon, then check `hdlab/` for matching modules. Atoms vs modules are not 1:1 — many cells produce evidence without validating a NEW callable; the audit flags only the cases where a chain-grade mechanism could become a hdlab/ primitive.

## Inventory

| Mechanism | Chain-grade atoms | `hdlab/` status |
|-----------|------------------:|-----------------|
| codebook NN cleanup | 2 | ✓ `memory.py` (`Codebook`) |
| Hebbian W outer-product | 2 | ✓ `learning.py` (`HebbianAssociations`) |
| sequence-binding S matrix | (c3 HARD_PASS smoke+timing; 3-seed pending) | ✓ `sequence_memory.py` (`SequenceMatrix`) SHIPPED 2026-06-22 |
| **refuse-gate** | 1 (likely more under different atom-IDs) | ✗ MISSING — not in hdlab/ |
| **multi-hop iterative cleanup (r1)** | 2 | ✗ MISSING — chain-grade-validated mechanism not callable from hdlab/ |
| **continual writes (a8)** | 2 | ✗ MISSING — α=0.5 NEVER-FORGETS mechanism not in hdlab/ |
| **KV learned projection** | 2 (incl. HARD_PASS anchor `EXP_kv_learned_projection_v1`) | ✗ MISSING — strongest transform-survival evidence; primitive not implemented |
| **whitening projection** | **4** | ✗ MISSING — most-evidenced gap; only referenced in audit cells |
| **two-hop KG inference** | 1 (n8 ConceptNet CERT 585 2026-06-22) | ✗ MISSING — the L3 ConceptNet KG #2 mechanism is in the cell, not in hdlab/ |
| **modern Hopfield / SMH** | 1 | (HONEST_NEGATIVE; not a hdlab/ candidate) |
| **sparse distributed top-K kWTA** | 0 | (n4 cell never dispatched per audit; not yet chain-grade) |
| **conformal prediction (split-CP)** | 0 chain-grade visible (may exist under different atom-id) | ✗ Pending check |
| **MKN smoothing** | 0 chain-grade (MIDDLE_BAND); partial candidate | (deferred per cadence — MIDDLE_BAND not auto-atomized) |

## Substantial backlog: 7 chain-grade-validated primitives NOT in hdlab/

Ranked by leverage (chain-grade evidence × composability × current strategic priority):

1. **two-hop KG inference** (load-bearing for L3 KG capability tier; n8 just landed CERT 585; ConceptNet uses this internally but it's not a callable substrate primitive) — **HIGH priority**; would expose substrate-native multi-hop traversal as a public hdlab/ op.
2. **refuse-gate** (load-bearing for substrate-only-decode + KG safety; every ingest cell uses it; chain-grade-validated but currently re-implemented per-cell) — **HIGH priority**; would centralize the OOD-rejection mechanism.
3. **r1 iterative cleanup multi-hop** (substrate-native chain-of-thought primitive; META atom shipped) — **HIGH priority**; needed for any future multi-step reasoning composition.
4. **whitening projection** (4 chain-grade atoms — most-evidenced gap) — **MEDIUM-HIGH**; would expose the encoder-residual whitening as a substrate primitive callable before ingest.
5. **KV learned projection** (HARD_PASS anchor for transform-survival; load-bearing for the phase-diagram-action lane the USER opened) — **MEDIUM**; would expose the storage-chain-item-3 projection as callable.
6. **continual writes (a8 α=0.5 NEVER-FORGETS)** (substrate-vs-LLM MOAT mechanism) — **MEDIUM**; would expose the no-replay-needed continual ingest pattern.
7. **conformal prediction / split-CP** (auditable confidence intervals; possibly in cert_ledger under different atom-id family) — **LOWER**; supplementary calibration primitive.

## Next-cycle substrate-code-update queue (TIER 2 promotion)

Per the new cadence, these 7 backlog primitives become the per-cycle ship targets (one per cycle until backlog clears; bundle 2 per cycle if mechanism is small):

- **Next cycle:** `hdlab/kg_traversal.py` (two-hop + n-hop substrate-native KG traversal; uses U1 codebook + W; the n8 cert-class mechanism made callable)
- **Cycle +2:** `hdlab/refuse_gate.py` (OOD rejection primitive; standardized across all ingest cells)
- **Cycle +3:** `hdlab/iterative_cleanup.py` (r1 multi-hop chain-of-thought; iterative Codebook lookup with margin-refuse)
- **Cycle +4:** `hdlab/whitening.py` (encoder-residual whitening; 4 chain-grade evidence; pythia & llama1b)
- **Cycle +5:** `hdlab/learned_projection.py` (KV learned projection; transform-survival anchor)
- **Cycle +6:** `hdlab/continual_ingest.py` (a8 NEVER-FORGETS; α=0.5 baseline)
- **Cycle +7:** `hdlab/conformal.py` (split-CP confidence intervals)

By the end of the cycle window (7 cycles ~= 5-6 hr autonomous arc work + landed-VET turnarounds), the substrate's hdlab/ surface area would expose all chain-grade-validated primitives as callable substrate ops — bringing the operational substrate in line with the cert-grade evidence.

## Underperforming inventory (the other half of the user's question)

MIDDLE_BAND atoms = mechanisms that "almost worked" — promotion candidates if a discriminator-knob tweak gets them over the chain-grade bar:

- **N1 v3.1 substrate-LM** MIDDLE_BAND (4.96 BPC; bigram-gap 1.12 bits). Promotion path = composition with n4 k-WTA-VQ + n10 whitening + MKN — gated on n4 dispatch (still un-dispatched per TIER 1c audit).
- **n3 SimVQ** MIDDLE_BAND HONEST_NEGATIVE (PCA hurts ceiling). Demote to deferred.
- **n3 MKN smoothing** MIDDLE_BAND (+0.068 bits). Worth promoting if compose-with-n10-whitening + composes-with-Path-A (now HARD_FAIL — re-scope needed).
- **r1 K=3,4 MM (multi-hop)** — chain-grade at K=2; MIDDLE_BAND at K=3,4. r1b chain-grade promotion path HARD_FAILed today (cert-trail in queue). Promotion needs different angle.
- **HumanEval Anchor-1 variants** (3 MIDDLE_BAND + 2 HARD_FAIL today). Revival drill needed; rescope.
- **SVAMP role-asymmetry (3 variants)** all MIDDLE_BAND. Promotion path = synthetic-WK training (Candidate D) still queued.
- **n10 whitening** smoke fires eff_rank 16.7→230.3 = 13.8x; full status unclear (no metrics directory). Re-dispatch candidate.
- **capacity_sweet_spot_v2** MEASURED_MECHANISM (special verdict). Worth re-reading for whether the measured mechanism is promotable.

## Composes with

- The new results-to-application cadence (same-cycle hdlab/ updates) operationalized via the 7-cycle ship queue above.
- The phase-portrait v3 atom (just written) — the hdlab/ primitives become testable across the phase-diagram axes.
- Brain-drill cadence — the missing kWTA primitive will land when n4 cell finally dispatches.

— Research (Director); first capability-gap audit per the gap-evaluation discipline; cert-trail durable artifact; no addressee per the no-inter-session-routing rule.
