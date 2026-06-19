# exp_dev hand-off -- research: QS DEEPER 3x cheater dynamics + biofilm phase transitions

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_natural_analog_QS_DEEPER_3x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by actionability + cheap test criteria)

### 1. Cell QS-C1 -- Cheater equilibrium replicator dynamics (HIGHEST PRIORITY)
Anchor pointer: QS-CHEATER-REPLICATOR-C1 (new; not yet queued)
Substrate-product reading: validates that a federation with contribution scoring converges to a stable predictable cheater fraction f_c* controlled by penalty tuning; if f_c* does NOT decrease monotonically with increasing penalty, the public goods game model is mis-specified for the substrate context and the federation design must be revisited
Tier hint: CPU; ~1 hr wall; pure numerical simulation (no encoder, no GPU required); minimal Python (scipy or numpy only)
Why-now: directly tests the mathematical foundation of the federated contribution scoring claim -- the equilibrium formula f_c* = c/b is the core guarantee; cheap to verify before engineering any policing layer
Pre-reg bands: HARD-PASS = f_c* decreases monotonically with increasing penalty c across 5 values of c/b in [0.1, 0.9]; stable interior equilibrium forms within 50 generations; HARD-FAIL = f_c* does NOT converge or increases with increasing penalty; MID-BAND = monotone decrease but no stable interior equilibrium (limit cycle behavior instead)

### 2. Cell QS-C2 -- Bistable federation gate no-chattering smoke (HIGH PRIORITY)
Anchor pointer: QS-BISTABLE-GATE-C2 (new; not yet queued)
Substrate-product reading: validates that the no-oscillation federation activation condition (n=4 Hill function, h_OFF = 0.2 * h_ON) actually prevents chattering under realistic query load variation; this is a direct spec for the federation activation layer
Tier hint: CPU; <30 min wall; pure signal processing simulation; use existing EMA machinery from QS cycle 175 adversarial signal logic
Why-now: the bistable gate design is ready to implement; this is the smoke test that verifies the hysteresis bound before it is committed to the activation code path
Pre-reg bands: HARD-PASS = zero chattering events (oscillations) when input signal S fluctuates with CV=0.3 around h_ON; gate activates at h_ON and does NOT deactivate until signal drops to h_OFF = 0.2 * h_ON; HARD-FAIL = oscillations persist at CV=0.3 with n=4; MID-BAND = no oscillations at CV=0.3 but oscillations appear at CV=0.5

### 3. Cell QS-C3 -- Policing cost ratio sweep (MEDIUM PRIORITY)
Anchor pointer: QS-POLICING-COST-SWEEP-C3 (new; not yet queued)
Substrate-product reading: empirically verifies the Wechsler 2019 threshold condition (c_pg/(c_tox + c_res) >= 1.5) for the substrate analog; determines what contribution-score-to-penalty ratio is needed for the policing strategy to dominate cheaters within 10 generations
Tier hint: CPU; <1 hr wall; replicator dynamics extension of QS-C1 to include the policer strategy; moderate complexity (4-strategy model vs 2-strategy in C1)
Why-now: the 1.5 threshold is from a biological model; substrate analog parameters may be different; empirical verification prevents over- or under-engineering the policing layer
Pre-reg bands: HARD-PASS = policers achieve >50% frequency within 10 generations when cost ratio >= 1.5; HARD-FAIL = policing collapses to zero regardless of cost ratio (second-order public goods problem dominates); MID-BAND = policing viable only at narrow cost ratio window (sensitive to parameter tuning)

### 4. Cell QS-C4 -- Persister / Poisson hibernation vs deterministic threshold (LOWER PRIORITY)
Anchor pointer: QS-PERSISTER-HIBERNATION-C4 (new; not yet queued)
Substrate-product reading: compares Poisson-distributed hibernation transitions (Lewis 2010 TA-bistability analog) vs deterministic threshold hibernation for substrate cold-storage mode; verifies that Poisson jitter prevents synchronized wake/sleep spikes in query latency
Tier hint: CPU; <30 min wall; queueing simulation with exponential service time; no GPU required
Why-now: hibernation mode is not yet implemented; this test determines which activation pattern to use BEFORE implementation commits to a design; prevents synchronized latency spikes at production scale
Pre-reg bands: HARD-PASS = Poisson-distributed hibernation shows no synchronized latency spikes (max latency percentile p99 < 2x median); deterministic threshold shows visible synchronized spikes; HARD-FAIL = both methods produce identical latency distributions (no benefit to Poisson jitter); MID-BAND = Poisson reduces spike amplitude but doesn't eliminate them

---

## Context pointers (file paths, not summaries)

- Primary research note: d:/AI/hd-instrument/notes/research_drill_natural_analog_QS_DEEPER_3x_2026-06-07.md
- Prior QS 5x note: d:/AI/hd-instrument/notes/research_drill_natural_analog_quorum_sensing_5x_2026-06-07.md
- Related: differential privacy 5x (contribution scoring + DP policing coupling): d:/AI/hd-instrument/notes/research_drill_field_differential_privacy_5x_2026-06-07.md
- Related: streaming algorithms 5x (Count-Min Sketch for contribution frequency): d:/AI/hd-instrument/notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md
- Related: modern Hopfield 5x (sparse activation / persister analog): d:/AI/hd-instrument/notes/research_drill_field_modern_hopfield_5x_2026-06-07.md
- Adversarial QS signal EMA prior result (cycle 175, 10/10 adversarial, 0 FP): referenced in QS 5x note above

---

## Contract section

These anchors are CPU-runnable smoke tests (C1, C2, C4) and one medium-complexity replicator dynamics test (C3). All are local-first per [[feedback-small-scale-first-methodology]]. None requires cloud GPU. All can run on the local runner or laptop (background, no nohup per [[feedback-laptop-run-no-nohup-use-timeout]]).

C1 and C2 should be dispatched first (sequential or parallel) -- they test the mathematical foundations that C3 and C4 build on. If C1 HARD-FAILs (f_c* does not respond to penalty), C3 is moot.

## Autonomy declaration

exp_dev decides: exact sweep grid for c/b values in C1; exact noise model (Gaussian vs Poisson vs realistic query traces) for C2; 4-strategy model specifics (group size, mixing coefficient) for C3; access-frequency distribution model for C4. Orchestrator does not pre-specify these; exp_dev owns experimental design per role contract.
