# exp_dev hand-off -- research: Phase 4 v1 production deployment roadmap

Filed-by: research sub-agent (2026-06-06)
Trigger: notes/research_drill_phase4_v1_production_deployment_roadmap_2026-06-06.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs the actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or check with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered)

### 1. CLOUD-1b Binding Test (HIGHEST PRIORITY -- in flight or next)
Anchor pointer: CLOUD-1b (name already in use; confirm status before re-dispatching)
Substrate-product reading: LM scale selection (1B vs 8B) determines Tier A vs Tier B production path; every downstream cell depends on this answer
Tier hint: GPU; ~30 min wall
Why-now: Architecture is confirmed; last remaining LM-selection gate; blocks Cell 2 (G16) and Cell 3 (hallucination stack on causal LM)

### 2. G16 Scale Confirmation (dim-expansion subsumes whitening at N=65536)
Anchor pointer: G16 (may be queued or in flight; confirm status)
Substrate-product reading: production rule from G7 (expansion subsumes whitening) needs scale confirmation; if G16 HARD-FAIL, whitening step must be added back
Tier hint: GPU; full-N sweep; ~1-2h wall
Why-now: Stage 2 deployment recipe is blocked on this answer; DIMSPARSE compound test depends on knowing G16 outcome first

### 3. DIMSPARSE Compound Test
Anchor pointer: DIMSPARSE (in flight today; check status before dispatching)
Substrate-product reading: determines whether sparse coding is included in default Stage 2 recipe; if HARD-PASS, mandatory; if HARD-FAIL, use dim-expansion alone
Tier hint: GPU or CPU depending on N; <2h wall
Why-now: Stage 2 mechanism selection is blocked; affects Cell 2 in critical path

### 4. PSE3 Codebook Monitoring Integration Test
Anchor pointer: PSE3-MONITOR (new anchor; not yet queued)
Substrate-product reading: HARD PRODUCTION DEPLOYMENT GATE; cannot ship v1 without confirming ETF Hadamard codebook stays stable (H_C > 0.8 * log(C_size)) under 10k insertions AND that alarm fires on injected collapse
Tier hint: CPU or GPU; moderate N; ~1-2h wall
Why-now: Operational gap; all physics is confirmed; this is pure monitoring-infrastructure validation; blocks Cell 4 in critical path

### 5. Hallucination Stack Integration (NEG1/G14 + HOC1)
Anchor pointer: NEG1/G14 (in flight); HOC1 (in flight, <2 min)
Substrate-product reading: 3-signal hallucination stack (substrate grounding + word bigrams + DeBERTa NLI) needs validation on causal LM outputs; KF-1 baseline is on MiniLM
Tier hint: CPU; HOC1 trivial; NEG1/G14 moderate
Why-now: Cell 3 in critical path; blocks Cell 5 (end-to-end demo)

---

## Context Pointers

Research note: d:/AI/hd-instrument/notes/research_drill_phase4_v1_production_deployment_roadmap_2026-06-06.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Prior handoffs: scan notes/exp_dev_handoff_*.md sorted by mtime for any conflicting dispatches

---

## Contract

exp_dev designs anchor names, sweep grids, pre-reg thresholds, timeout formulas, and queue assignments.
exp_dev does NOT re-derive the architecture or re-run the Stage 1-3 recipe above.
exp_dev verifies queue presence post-ship per [[feedback-ship-name-collision]] discipline.
exp_dev confirms no redundant dispatch if anchor is already in flight (check queue.json before ship).

## Autonomy Declaration

exp_dev has full autonomy over: anchor naming, N/seed/layer sweep parameters, timeout calculation, queue choice (GPU vs CPU vs remote), pre-reg HP/MID/HF numerical thresholds, and decision to batch vs serialize. The critical-path ordering above is a recommendation, not a constraint; exp_dev may reorder if queue state or runner availability argues for it.
