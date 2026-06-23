# Director autonomous wake queue (USER away ~1hr; ScheduleWakeup every 15min)

**Purpose:** each wake, do maintenance THEN pick ONE substantive item from this queue (mark `[X]` when done). Persistent across wakes. Rotate across categories to deeply explore brain × HD × substrate world.

**Discipline:** Per Fix #28, verify metrics directly. Per USER 2026-06-22 "empowered to experiment where lit-dismissed". Per "deeply explore world taking cues from bio/brains/nature".

## Maintenance every wake (~1-2 min)

1. `cd /d/AI/hd-instrument && python tools/landing_notifier.py`
2. `ssh marsh@home` check both queues running/pending
3. For any new landings: pull metrics, read per-arm, classify, route negatives to research, positives to Skunkworks
4. If GPU empty: dispatch 1 GPU cell
5. Update todos

## Substantive exploration queue (pick ONE per wake; mark done)

### BRAIN/BIO/NATURE research drills (each: spawn hdi_research; ~5-10min)

- [ ] **R1: Gamma-synchronization binding** (Crick-Treisman; Singer): substrate-native temporal binding via HD phase coding. Cells we have are amplitude/spatial; this is temporal. P-deflated estimate first, then cell candidate.
- [ ] **R2: Neuromodulator HD state-control** (dopamine/serotonin/acetylcholine): scalar modulator vectors that gate substrate write-rate / refuse-threshold. Substrate analog of brain learning-rate modulation. Compose with pc1 predictive-coding gate.
- [ ] **R3: Cerebellar microzone forward-models**: 100k+ microzones each predicting one sensory dimension. Substrate analog = many small W matrices specialized to single dimensions. Composes with m1 modular (which is general modular; this is specialized).
- [ ] **R4: Thalamic relay routing**: substrate gate-matrix selects which W-submatrix activates per query (extends m1 modular into routing-based gating; brain-faithful version).
- [ ] **R5: Default-mode network spontaneous replay**: substrate idle-state mechanism that consolidates memory without input (composes with c2 cascade-STC-SWR which is replay-during-ingest; this is replay-during-idle).
- [ ] **R6: Sparse distributed memory (Kanerva) capacity at scale**: how does SDM compare to Hebbian-bind at high alpha? Substrate-mine prior + lit-survey.
- [ ] **R7: Cortical critical-state avalanches** (Beggs-Plenz 1/f scaling): substrate self-organized criticality; capacity at edge of stability.
- [ ] **R8: Hippocampal-cortical dialogue** (engram-to-permanent-storage): substrate analog of memory consolidation across sleep stages.

### LOCAL SMOKE SUITES (each: write+run smoke .py; ~3-5min total wall)

- [ ] **S1: Attractor variants** (different softmax temps, beta sweep, iter counts, basin sizes; fix the broken probe2 from suite v1 properly)
- [ ] **S2: Storage density v2** (rank-k SVD compression of W; tensor-train decomposition; semantic-hash quantization; bit-packing)
- [ ] **S3: Multi-encoder hybrid** (char_trigram + Random Indexing + entity-key all combined into single query vector; does each encoder add signal?)
- [ ] **S4: Substrate-native arithmetic** (does HD arithmetic preserve composition? cat+dog → "pets" cluster?)
- [ ] **S5: Refuse-gate calibration on real corpora** (use all 3 chat backends; calibrate per-backend τ; measure cross-backend transfer)
- [ ] **S6: Generation diversity** (g1b walk with different sampling temps + topk vs softmax sample; measure path diversity / entropy)

### SKUNKWORKS AUDITS (each: spawn hdi_skunkworks; ~5-10min)

- [ ] **A1: Audit hdlab/ primitives NEVER combined** — which pairs of the 10 primitives have NEVER been used together in a chain-grade cell? Surfaces composition gaps.
- [ ] **A2: Audit cert_ledger for HARD_FAIL atoms** — are any of them actually MEASURED_MECHANISM positives that didn't get the right scope? Re-scope candidates.
- [ ] **A3: Audit referent-validity** of recent atoms (per Fix #28 violation count) — find any atoms whose metrics.json doesn't actually support the verdict_msg framing.

### CELL-AUTHOR DISPATCHES (only if spawn budget allows — already 10+ active; do sparingly)

- [ ] **C1: r2e successor-W + cascade-W cross-thread** (drill #3 fallback cell if r2d HARD_FAILs)
- [ ] **C2: Grid-cell-VSA spatial substrate cell** (mechanism #3 from broad-exploration drill; novel)
- [ ] **C3: Engram-sparse-allocation cell** (mechanism #5+ from broad-exploration drill; sparse-ensemble write rules)
- [ ] **C4: substrate-as-MID-resolver cell** (FB15k MID→name lookup via char_trigram against ground-truth label corpus; chat-UX fix from probe6 finding)
- [ ] **C5: substrate-native semantic-hash storage cell** (compress W to semantic-hash codes; storage density)

### STRATEGIC DOCS (any wake; ~5min)

- [ ] **D1: Update master_plan.md** with today's substantial new direction (hybrid Path A+B, brain×HD broad-exploration top-3, 273-audit findings, ~10 new cells in flight, attractor/predictive-coding META primitives)
- [ ] **D2: Update fleet_waiting_on.md** with current blockers (sync push failing; chat needs MID-resolver; etc.)
- [ ] **D3: Director plan.json** update CERT-count + decision-point cadence per banked discipline

## Wake log (mark done; one line per wake)

- (21:09 wake N) — TBD
- (21:24 wake N+1) — TBD
- (21:39 wake N+2) — TBD
- (21:54 wake N+3) — TBD

## Stopping condition

USER returns → respond to their direction. Else continue rotating until next 5 wakes have all picked at least 1 item (~5 substantive explorations + maintenance).
