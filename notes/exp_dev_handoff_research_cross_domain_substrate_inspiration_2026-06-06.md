# exp_dev hand-off -- research: cross-domain substrate inspiration

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_cross_domain_substrate_inspiration_2026-06-06.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA. Do NOT re-specify what is already specified here.

---

## Anchor Candidates (rank-ordered)

### Rank 1: Donoho-Tanner phase boundary verification (CS-1)
- Anchor pointer: Cross-domain research note CS-1 cell
- Substrate-product reading: Unifies all capacity rescue axes under a single phase-boundary framework; algebraic-only test confirms or refutes whether substrate retrieval is a compressed-sensing-class problem
- Tier hint: CPU-local theory computation (~1h), no GPU required
- Why now: Highest score (0.66) in ranking; algebraic-only means no experiment blocking; result directly audits the 45x compound capacity claim's operating-point geometry

### Rank 2: Polyphony ceiling SNR formula (SIG-1)
- Anchor pointer: Cross-domain research note SIG-1 cell
- Substrate-product reading: Gives a closed-form production spec "simultaneous concept capacity = N/10 at 95% fidelity"; directly useful for API design + customer communication
- Tier hint: CPU-local smoke (~1h), sweep N=1024,4096,16384
- Why now: Score 0.66 tied with CS-1; SNR formula is a direct product-spec deliverable with zero ambiguity in success criterion; cheap to verify

### Rank 3: Chain-binding K-hop protocol (NRO-1)
- Anchor pointer: Cross-domain research note NRO-1 cell, hippocampus theta-sequence analogy
- Substrate-product reading: Extends lossless K-hop reasoning depth from K~10 to K~15 without N-scaling cost; directly extends the multi-step reasoning capability class
- Tier hint: CPU smoke 2h; GPU overnight for full K/N grid
- Why now: Score 0.62; extends an existing HARD-PASS capability; hippocampal chain-binding mechanism has no prior substrate test

### Rank 4: Percolation universality exponent (PERC-1)
- Anchor pointer: Cross-domain research note PERC-1 cell
- Substrate-product reading: Establishes capacity degradation curve (1 - M/M_c)^beta; enables predictive production monitoring of memory load headroom
- Tier hint: CPU sweep 3h, scipy curve_fit
- Why now: Score 0.55; percolation is a tier-1b field per field advisor (unfilled adjacency); beta exponent is a production monitoring parameter

### Rank 5: p-spin ternary interaction terms (SG-1)
- Anchor pointer: Cross-domain research note SG-1 cell, spin-glass field
- Substrate-product reading: +25-35% additional capacity via ternary interaction terms layered on top of existing rescue axes; directly relevant to cap_map capacity rows
- Tier hint: CPU 2h smoke; GPU overnight for full grid
- Why now: Score 0.54; adjacent to ongoing spin-glass drill track (Plefka expansion tier-1)

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_cross_domain_substrate_inspiration_2026-06-06.md
- Field advisor output: run `python tools/orchestrator/research_field_advisor.py` for current tier rankings
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check current state of capacity rescue axes before SG-1 dispatch)
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

exp_dev owns: anchor naming, sweep grid design, pre-reg bands, queue selection, ETA estimate, formula self-tests.
exp_dev does NOT own: cap_map decisions, verdict interpretation, strategy priority ordering (those go to verdict_handler / orchestrator).

## Autonomy Declaration

exp_dev has full autonomy on implementation details for all 5 candidates above. Dispatch in priority order unless queue/pause constraints apply. CS-1 and SIG-1 are algebraic-only and can be dispatched immediately regardless of pause flag (no GPU, no runner slot needed).
