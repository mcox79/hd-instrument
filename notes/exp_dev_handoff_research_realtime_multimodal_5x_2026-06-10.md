# exp_dev hand-off -- research: real-time multimodal substrate architecture

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_realtime_multimodal_5x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are research
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

PP-257 (one-shot cross-modal binding) is validated. The open question is whether
substrate-native real-time multimodal binding (video 30Hz + audio 44.1kHz + sensorimotor
1kHz simultaneously) is achievable with the existing substrate architecture.

Research identified two convergent paths:

PATH 1 (P_deflated=0.40): PER-MODALITY-SUBSTRATE + role-vector binding (HDC/VSA
  bundling). Three substrate instances, each updated at native rate. Binding step runs
  at 30Hz. Substrate-native; reuses existing FHRR operations.

PATH 2 (P_deflated=0.42): WAVE-INTERFERENCE-HOLOGRAPHIC (HRR complex binding).
  B = S_A * conj(S_V) * conj(S_M). Substrate already uses FHRR; most direct extension.

Both paths converge in a COMBINED architecture: B_total = alpha * (S_A * r_A + S_V *
r_V + S_M * r_M) + (1-alpha) * S_A * conj(S_V).

Supporting architecture: ASYNC-EVENT-DRIVEN updates (P_deflated=0.38) reduce CPU cost
10-100x for real-world sparse signals. Prerequisite: T-BIND-1 passes.

All 5 tests (T-BIND-1 through T-BIND-5) are CPU laptop tier, 20-30 min each. No cloud
dispatch needed for pre-tests.

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. T-BIND-1 -- Per-modality substrate binding capacity (HIGHEST PRIORITY, GATE TEST)

Anchor pointer: MMOD-BIND-1 (new; not yet queued)
Substrate-product reading: Validates whether role-vector binding (VSA bundling) achieves
  recall@10 >= 0.80 with K=3 modalities at N=10000, M=100 patterns per modality. This
  is the gate test for PATH 1 (PER-MODALITY-SUBSTRATE). If it passes, multimodal binding
  is substrate-native and no new architecture is needed beyond 3 substrate instances.
  If it fails at N=10000, the capacity bound is hit and N must be increased or PATH 2
  must be used exclusively.
Tier hint: CPU laptop; ~30 min wall; numpy/torch only; no model load
Why-now: Gate for all downstream multimodal binding tests. Cheapest pre-test. Runs first.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: recall@10 >= 0.80 at N=10000, M=100, K=3 modalities (all 3 modalities pass)
  HARD-FAIL: recall@10 < 0.50 at N=10000, M=100 for any modality
  MID-BAND: recall@10 in [0.50, 0.80] -- increase N to 50000 and retest before declaring fail

Setup: generate 3 sets of M=100 random FHRR unit vectors (S_A^i, S_V^i, S_M^i for
  i=1..M). Generate 3 random role vectors (r_A, r_V, r_M) of the same dimension.
  Compute B^i = S_A^i * r_A + S_V^i * r_V + S_M^i * r_M for each pattern i.
  Store all B^i. For query: given B^i, compute S_A^i_approx = B^i * r_A. Measure
  recall@10: what fraction of queries retrieve the correct S_A^i in the top 10 by cosine
  similarity against the M=100 stored S_A vectors.
  Repeat for r_V, r_M. Report mean recall@10 across 3 modalities.

Note: the * operation is element-wise product for FHRR (bipolar/complex vectors).
  The + is element-wise sum. The retrieval is cosine similarity on the real part.

### 2. T-BIND-2 -- Async temporal offset degradation

Anchor pointer: MMOD-BIND-2 (new; not yet queued)
Substrate-product reading: Measures how much binding quality degrades when S_A and S_V
  are sampled at different moments (temporal offset delta_t). If binding holds at
  delta_t = 33ms (one video frame), async per-modality updates are safe. If not,
  synchronous polling within the frame is required, which increases implementation
  complexity but does not change the architecture.
Tier hint: CPU laptop; ~20 min wall
Why-now: Determines whether the async architecture (F2.3) is viable at frame timescales.
  Should run immediately after T-BIND-1 pass.

Pre-reg bands:
  HARD-PASS: recall@10 >= 0.75 at delta_t = 33ms (one video frame period)
  HARD-FAIL: recall@10 < 0.60 at delta_t = 33ms
  MID-BAND: recall@10 in [0.60, 0.75] -- async is marginal; may need sub-frame polling

Setup: use the binding setup from T-BIND-1. Simulate temporal offset by adding Gaussian
  noise to S_A^i with magnitude proportional to delta_t (or equivalently, replacing
  S_A^i with a slightly corrupted version S_A^i + epsilon * N(0,I) where epsilon =
  delta_t * noise_rate). Sweep delta_t in {0, 10ms, 33ms, 100ms, 333ms}. Report
  recall@10 vs delta_t curve.

Prerequisite: T-BIND-1 HARD-PASS.

### 3. T-BIND-3 -- Event-driven update rate vs binding quality

Anchor pointer: MMOD-BIND-3 (new; not yet queued)
Substrate-product reading: Validates that event-driven threshold gating (update S_k only
  when input changes by > delta_k in cosine distance) achieves 10x+ CPU reduction at
  negligible binding quality cost. This is the key to making 44.1kHz audio practical
  without running the substrate at audio sample rates.
Tier hint: CPU laptop; ~20 min wall
Why-now: Independent of T-BIND-2. Can run in parallel after T-BIND-1 pass.

Pre-reg bands:
  HARD-PASS: delta_k = 0.05 achieves >= 10x update rate reduction at < 0.05 recall@10 drop
  HARD-FAIL: Any delta_k achieving >= 10x reduction causes > 0.15 recall@10 drop
  MID-BAND: 10x reduction achieved but with 0.05-0.15 recall@10 drop -- acceptable if
            recall@10 absolute value is still >= 0.75

Setup: simulate an audio stream at 44.1kHz as a sequence of random vectors with slow
  drift (each step adds N(0, sigma^2*I) noise; sigma = drift rate). Apply threshold
  gating: only update the substrate when |x[t] - x[t-1]|_cos > delta_k. Sweep delta_k
  in {0.01, 0.05, 0.10, 0.20}. For each delta_k, measure effective update rate (fraction
  of time steps where update fires) and recall@10 on the final binding.

Prerequisite: T-BIND-1 HARD-PASS.

### 4. T-BIND-4 -- Kuramoto phase-lock convergence

Anchor pointer: MMOD-BIND-4 (new; not yet queued)
Substrate-product reading: Tests whether Kuramoto oscillator coupling between K=3
  modalities with heterogeneous natural frequencies (proportional to their update rates)
  achieves phase lock in < 100 simulation steps at a coupling K <= 2.0. This validates
  the phase-based binding architecture (F2.2) and informs the phase parameter for T-BIND-5.
Tier hint: CPU laptop; ~30 min wall; numpy only
Why-now: Independent of T-BIND-1. Can run immediately.

Pre-reg bands:
  HARD-PASS: Phase lock achieved in < 100 simulation steps at K_Kuramoto <= 2.0
  HARD-FAIL: Phase lock requires K_Kuramoto > 5.0
  MID-BAND: Phase lock at K_Kuramoto in [2.0, 5.0] -- marginal; use fixed phase encoding instead

Setup: K=3 Kuramoto oscillators with natural frequencies omega = [1.0, 0.023, 0.00068]
  (proportional to 44.1kHz, 1kHz, 30Hz, normalized to [0,1] range). Initial phases
  random uniform in [0, 2*pi]. Coupling K swept in {0.1, 0.5, 1.0, 2.0, 5.0}.
  Phase lock criterion: max(|phi_i - phi_j|) < 0.1 radians for all pairs i,j.
  Run 1000 steps at each K. Report: lock achieved (bool), steps to lock, K required.

Note: if the extreme frequency ratio 44100:30 prevents lock-in for any practical K,
  use compressed (event-driven) rates instead: the effective audio rate after event
  gating may be ~100-500Hz, making the ratio more favorable.

### 5. T-BIND-5 -- Holographic cross-modal retrieval with phase encoding

Anchor pointer: MMOD-BIND-5 (new; not yet queued)
Substrate-product reading: Tests whether FHRR complex-conjugate product binding
  (PATH 2 wave-interference-holographic) achieves recall@10 >= 0.80 at K=3 modalities
  with N=10000. This validates the substrate-native holographic path and determines
  whether phase encoding from T-BIND-4 improves binding quality.
Tier hint: CPU laptop; ~30 min wall
Why-now: Depends on T-BIND-1 and T-BIND-4 results.

Pre-reg bands:
  HARD-PASS: recall@10 >= 0.80 with phase-encoded holographic binding;
             improvement over no-phase baseline >= 0.05 in recall@10
  HARD-FAIL: recall@10 < 0.50 (holographic capacity insufficient at K=3, N=10000)
  MID-BAND: recall@10 in [0.50, 0.80] -- increase N to 50000 before declaring fail

Setup: same M=100 patterns per modality as T-BIND-1. Compute binding using complex
  product: B^i = S_A^i * conj(S_V^i) (pairwise A-V binding). Also compute extended:
  B^i_3 = S_A^i * conj(S_V^i) * conj(S_M^i). Retrieve: S_A^i_approx = B^i * S_V^i.
  Measure recall@10 for pairwise and 3-way binding. Compare to T-BIND-1 role-vector
  baseline.
  Phase-encoded variant: multiply each B^i by exp(i * phi_AB) where phi_AB is the
  phase-lock angle from T-BIND-4. Report whether phase encoding improves recall@10.

Prerequisite: T-BIND-1 HARD-PASS. T-BIND-4 results used for phase parameterization.

---

## Strategic context for exp_dev

T-BIND-1 is the gate test. Run it first.

If T-BIND-1 HARD-PASS and T-BIND-5 HARD-PASS: the combined PATH 1 + PATH 2 architecture
is validated. The combined binding B_total = alpha * B_roles + (1-alpha) * B_holographic
is ready for production-scale implementation. Escalate to orchestrator for cap_map update.

If T-BIND-1 HARD-PASS but T-BIND-5 HARD-FAIL: use PATH 1 (role-vector bundling) only.
The holographic path has capacity issues at K=3; either increase N or use sequential
pairwise binding (bind A-V, then (A-V)-M).

If T-BIND-1 HARD-FAIL at N=10000: rerun at N=50000 before declaring path blocked.
VSA capacity at N=50000 with K=3 should exceed M=500 patterns. If N=50000 also fails,
the role-vector approach is blocked and PATH 2 is the only substrate-native path.

T-BIND-3 (event-driven) is critical for implementation feasibility. If it passes,
the system can handle 44.1kHz audio at low CPU cost. If it fails, audio integration
requires a dedicated compression pipeline (F2.5) rather than event gating.

Test dispatch order:
  Immediate (independent): T-BIND-1, T-BIND-4 in parallel
  After T-BIND-1 PASS: T-BIND-2, T-BIND-3 in parallel
  After T-BIND-4: T-BIND-5 (uses phi_AB from T-BIND-4)

---

## Context pointers

- Research note (full analysis):
  d:/AI/hd-instrument/notes/research_drill_realtime_multimodal_5x_2026-06-10.md
- PP-257 cross-modal binding validation (prior validated anchor):
  Check data/exp_PP-257/metrics.json or equivalent
- Substrate cap_map (multimodal rows):
  d:/AI/hd-instrument/data/substrate_capability_map.md
- v3.0 compositional cliff (most recent substrate milestone):
  See memory index: substrate_v3_compositional_cliff_crossed.md
- HDC/VSA survey (theoretical framework):
  https://dl.acm.org/doi/10.1145/3538531

---

## Contract section

This hand-off is research-to-experiment. The 5 test specs (T-BIND-1 through T-BIND-5)
are provided as pre-reg recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs from
  research estimates)
- Implementing the test scripts (FHRR role-vector binding, temporal offset sweep,
  event-driven threshold sweep, Kuramoto simulation, holographic binding)
- Assigning to correct queue (all are CPU laptop tier)
- Writing verdict notes for each test per standard protocol
- Escalating any HARD-PASS combination to orchestrator for cap_map update

## Autonomy declaration

Exp_dev may dispatch T-BIND-1 and T-BIND-4 immediately and in parallel without
orchestrator approval (independent, CPU pre-tests, low cost). T-BIND-2 and T-BIND-3
require T-BIND-1 HARD-PASS first. T-BIND-5 requires T-BIND-1 HARD-PASS and T-BIND-4
completion. A combined T-BIND-1 + T-BIND-5 HARD-PASS that validates the multimodal
binding architecture MUST be escalated to orchestrator before any product specification
or cap_map row is updated.
