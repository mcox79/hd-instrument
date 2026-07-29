# Comprehension frontier — situation-model scoping (living doc; updated as it develops)

Scoped 2026-07-28 (research drill) while the breadth run trained. The deep frontier after: readout fix (WIN, readout-limited), gated_fusion (WIN, island cashed), grounding (NULL, no transfer), objective axis (NULL). Comprehension = build a **situation model**, not a static S-R-O triple.

## Biology-first (the target)
Kintsch Construction-Integration + Zwaan/Radvansky Event-Indexing + Frankland-Greene 2015 (lmSTC AGENT/PATIENT slots) + Rabovsky Sentence-Gestalt (N400 = prediction-error-over-meaning-update). surface -> **textbase** (propositions = our current ceiling) -> **situation model** (integrated, updatable, tracks entity/space/time/causation/intention; measurable updating-cost at discontinuities; spatial is weakest -> deprioritize).
- **Binding is ROLE-GENERAL not positional** (brain lmSTC invariant to active/passive) — independently corroborates our 07-28 `probe_v5_bind_readout_derisk` (absolute-position bind 0.52 self-consistency vs mean-pool 0.95). Bind by content/role, not slot-position.
- Minimal brain-faithful mechanism: (a) small addressable entity slots (~4, Cowan) keyed by a LEARNED role-general identity; (b) write gated by prediction-error/surprise (update only when new input is inconsistent/extends); (c) the update decision + key are LEARNED by our own encoder, NOT asserted by rule.

## The line: supply STRUCTURE (allowed) vs supply MECHANISM (forbidden)
- **Allowed:** slot count/addressing scheme, which-dimensions schema (entity-state + time; skip spatial), training-signal shape (predict-next-slot-value / same-vs-changed), an existing bind/write primitive, construction-template ground-truth labels.
- **Forbidden:** any hand-coded rule that decides "did the referent change / which state is current" from surface cues (pronoun tables, recency/salience). `hdlab/state_of_mind.py` resolvers are exactly this — correctly registry-SHELVED for comprehension (rediscovered 3x; it's KG-store coref bookkeeping, not a comprehension organ).

## Candidate designs (A/C reuse existing stores + learned gate/key; B is escalation)
- **A. Entity-slot scaffold + learned write-gate** on the frozen encoder's OWN hidden states. At each clause boundary a TRAINED small head reads the hidden state for a mention vs the slot's content -> update-vs-keep + new value (learned decision). Write op reuses `hdlab/sequence_memory.SequenceMatrix` (WIRED, role-general Hebbian ordered-pair). **<- RECOMMENDED FIRST.**
- **C. Re-key the built DG/episodic store by entity-identity** (gap-map item 5: "reuse, no new component") — key episodic writes by a learned role-general signature, update=new write, read=pattern-completion. Nearly identical to A.
- **B. Event-schema template + forward state-prediction self-teacher** — supply a 2-dim schema, train the encoder to predict S2 slot values from S1 before seeing S2 (Rabovsky prediction-error, ground truth from construction). Changes the objective -> ESCALATION path if A/C's structure-only supply is insufficient.

## Measurement (calibration-first, non-negotiable)
Extend `experiments/diag_order_critical_comprehension_calib_v1.py` in place (keep its leak-proof split + scramble control + calibration gate). Add a genuine CROSS-BOUNDARY consistency arm (2-sentence consistent-vs-violated).
- **Calibration gate:** MiniLM/BGE (diagnostic-only) must clear >=0.70 AUC (or +0.15 acc over scrambled) on the new construction FIRST. A construction no known reader passes is broken.
- **HARD_PASS:** slot+gate readout beats matched plain readout >=+0.05 both seeds, controls at chance, AND an **untrained/random-init encoder through the identical slot+gate structure does NOT show the gain** (MANDATORY — this session random-init scored 0.704 > trained 0.592 on entity-state; structure-without-learning must be ruled out).
- **HARD_FAIL:** ties/loses both seeds OR untrained-gate matches (structure alone did it) -> escalate to design B.
- **MIDDLE:** +0.02-0.05 or single-seed -> do not bank; add auxiliary loss + re-probe.
- Real baseline = the measured RELOBJ_v3 MEAN_POOL on ENTITY_STATE (+0.283 seed7 / +0.130 seed13 — the non-replicated positive that must be beaten/replicated).

## Prior-work (reuse, don't reinvent)
- `sequence_binding`/`hdlab/sequence_memory.py` — WIRED, role-general Hebbian ordered-pair store = the write primitive for A/C.
- v6 extraction-head LESSON (role-general key beats absolute-position) — reuse the lesson, not the head.
- `cls_discrete_budget_consolidate` — possible surprise/write-gate signal source (VET_PENDING, don't lean on).
- `working_overlay_situation_reader` — SHELVED for this (non-fit); do NOT reach for it.
- No existing system does glass-box situation-model-as-mechanism+training-signal for text (closest: Dreamer/World-Models lineage cross-validates B's simulate-then-check framing).

## First can-fail experiment (ONE variable = mechanism only)
{matched mean-pool/plain readout} vs {entity-slot scaffold + learned write-gate on the SAME frozen encoder hiddens}. Encoder/data/seeds/construction FIXED (no retrain, no new data, no grounding). Same intervention class as the learned-readout fix that gave +0.067 for free; aimed at the one gap the brain-fidelity audit flagged UNMEASURED = cross-boundary persistence/update. Build: extend the calib instrument + a small `EntitySlotGate` in `hdlab/` reusing `sequence_memory.SequenceMatrix`. CPU-capable -> runs parallel to the GPU. Re-run on the breadth encoder later if breadth wins (mechanism is encoder-agnostic).
