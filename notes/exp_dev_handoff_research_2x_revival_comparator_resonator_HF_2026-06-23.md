# exp_dev hand-off — research: 2x revival comparator_resonator_primitive_smoke_v1 HARD_FAIL

**Filed-by:** Research (Director)
**Date (UTC):** 2026-06-23
**Trigger:** USER directive "understand WHY it failed" on comparator_resonator_primitive_smoke_v1 HF1 (ARM_COMPARATOR mean=0.856 vs ARM_RAW_W_LOOKUP mean=0.894). Research diagnosis: smoke-regime-too-easy + wrong-test-corpus; math is sound; revival path is v3 wiring + optional capacity-sweep backstop.
**Trigger note:** `notes/research_2x_revival_comparator_resonator_HF_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If paused, queue and surface to USER.

**Per [[feedback-no-experiment-design-in-prompts]]:** anchors + bands below; exp_dev owns cell-author + smoke + dispatch + REMOTE VERIFY.

---

## Anchor candidates (rank-ordered)

### 1. PRIMARY: lift comparator primitive into `hdlab/comparator.py` and unblock v3 (NO NEW CELL)

**Anchor pointer:** `hdlab/comparator.py` primitive ship — sources from `experiments/exp_comparator_resonator_primitive_smoke_v1.py` `arm_comparator`, `scalar_value_vec`, `fractional_power_encode`, `basis_direction` functions.
**Substrate-product reading:** the smoke validated the math (sanity 5/5, FPE monotone, projection-sign 5/5). The primitive is ready to ship into hdlab/ per the v3 handoff specification at `notes/exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md` Section "New primitive to author". This is a primitive-ship + ~6 lines of v3 cell wiring, not a new experiment.
**Tier hint:** PRIMITIVE-SHIP (not a cell; hdlab/ code update + import in v3 cell).
**Why-now:** the v3 cell is already filed and waiting on this primitive. The smoke HF does NOT block the v3 dispatch — it CONFIRMS the math is sound; the smoke's failure mode is diagnostically uninformative for the production target (HotpotQA comparison-em=0.07 is upstream encoder failure, not comparator failure). v3 Arm 3 + Arm 4 are designed to test the comparator at the regime where it actually matters.

**Spec (per parent research note L3):**

```python
# hdlab/comparator.py
import numpy as np

def fractional_power_encode(base: np.ndarray, t: float) -> np.ndarray:
    """Substrate-native FPE for scalar value encoding.
    Phase scaling on FFT; returns unit-norm real vector.
    """
    fb = np.fft.fft(base)
    mag = np.abs(fb); phase = np.angle(fb)
    fb_t = mag * np.exp(1j * phase * t)
    out = np.fft.ifft(fb_t).real
    n = np.linalg.norm(out)
    return out / n if n > 1e-12 else out

def scalar_value_vec(base, v, v_min, v_max):
    v_norm = max(0.0, min(1.0, (v - v_min) / max(1e-12, (v_max - v_min))))
    return fractional_power_encode(base, v_norm)

def basis_direction(base):
    hi = fractional_power_encode(base, 1.0)
    lo = fractional_power_encode(base, 0.0)
    d = hi - lo
    n = np.linalg.norm(d)
    return d / n if n > 1e-12 else d

def compare(W, E_X, E_Y, R_attr, direction):
    """Substrate-native 2-argument relational comparator.
    Returns +1 if X attr > Y attr, -1 if Y > X.
    """
    k_X = bind(E_X, R_attr); k_Y = bind(E_Y, R_attr)
    diff = W @ k_X - W @ k_Y
    score = float(np.dot(diff, direction))
    return 1 if score > 0 else -1
```

**Action contract:** exp_dev lifts the math from `exp_comparator_resonator_primitive_smoke_v1.py` (which has the validated implementations) into `hdlab/comparator.py`, runs `pytest verification/` to confirm no regressions, then unblocks the v3 dispatch.

---

### 2. SECONDARY (optional defense-in-depth): `comparator_resonator_capacity_sweep_v1` smoke

**Anchor pointer:** new anchor `comparator_resonator_capacity_sweep_v1`
**Substrate-product reading:** demonstrate empirically the M-regime where ARM_COMPARATOR strictly beats ARM_RAW_W_LOOKUP. Validates that the smoke HF1 is regime-bound, not mechanism-null. Useful for confidence before v3 dispatch but NOT load-bearing.
**Tier hint:** SMOKE (~30 min local CPU; 5 M-values × 3 seeds × ~2 min each)
**Why-now:** ONLY if exp_dev wants pre-dispatch confidence that the comparator primitive has a regime where it adds value. Skip if v3 dispatch proceeds based on math-soundness alone.

**Pre-reg HARD bands:**

**HARD_PASS:**
- There EXISTS some M ∈ {500, 1000, 2000} where ARM_COMPARATOR mean ≥ ARM_RAW_W_LOOKUP mean + 0.05
- AND sanity selftests still 5/5 at that M
- AND ARM_COMPARATOR > ARM_FREQ_BIAS by ≥ 0.20 at that M (lift over majority-class control)

**HARD_FAIL:**
- ARM_COMPARATOR ≤ ARM_RAW_W_LOOKUP for ALL M ∈ {50, 200, 500, 1000, 2000}
- → comparator primitive is strictly dominated; the v3 cell should drop the comparator arms

**MIDDLE_BAND:**
- ARM_COMPARATOR ≥ ARM_RAW_W_LOOKUP but lift < 0.05 at all M
- → marginal mechanism; not a chain-grade primitive on its own

**Sweep:**
- M ∈ {50, 200, 500, 1000, 2000} at N_DIM=4096
- α = M·n_attrs / N_DIM ∈ {0.061, 0.244, 0.610, 1.221, 2.441}
- 5 attrs, 3 seeds {7, 17, 23}, same selftest gate as v1
- Use the smoke cell's existing arm implementations; ONLY change is M-loop

**Resources:** local_cpu_queue; ~30 min wall

---

### 3. TERTIARY (conditional; queue only if v3 HARD_FAIL on Arm 3): comparator + alternative encoder smoke

**Anchor pointer:** `comparator_with_minilm_encoder_smoke_v1`
**Substrate-product reading:** isolates comparator math from encoder noise; tests if MiniLM-L6 retrieval + comparator could rescue comparison-QA even if v3 Arm 4 fails
**Tier hint:** SMOKE (~1 hr CPU + GPU encoding)
**Why-now:** ONLY if v3 HARD_FAIL on Arm 3 (comparison-em < 0.10) → indicates char_trigram encoder is the dominant noise source AND comparator alone cannot recover

---

## Context pointers (file paths, not summaries)

**Required reads (exp_dev primitive-ship phase):**
- `experiments/exp_comparator_resonator_primitive_smoke_v1.py` (source for `arm_comparator`, FPE, scalar_value_vec, basis_direction)
- `notes/research_2x_revival_comparator_resonator_HF_2026-06-23.md` (this drill; math soundness analysis)
- `notes/exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md` (downstream v3 cell that needs this primitive)
- `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` L3 (the comparator-primitive specification)
- `hdlab/kg_traversal.py` (KGStore where W, E, R live for production use)

**Existing related primitives in hdlab/:**
- `hdlab/multi_hop.py` (chain composition; comparator complements this)
- `hdlab/generation.py` (g1b; downstream consumer if comparator output is generated into text)
- `hdlab/whitening.py` (encoder-side; orthogonal to comparator)

---

## Contract

Per spawn_templates/experiment_pipeline_agent_template.md:

**For PRIMARY anchor (primitive ship):**
1. **Code-ship phase:** copy `arm_comparator`, `scalar_value_vec`, `fractional_power_encode`, `basis_direction` from `experiments/exp_comparator_resonator_primitive_smoke_v1.py` into a new `hdlab/comparator.py`. Use the v3-handoff `compare(kg, X, Y, attr, pred, ...)` signature as the public API.
2. **Verification phase:** add a `verification/test_comparator.py` test that runs the same 4 selftests the smoke cell ran (bind/unbind round-trip, FPE monotonicity, projection-sign 5/5, sanity holdout 5/5). Must pass with `tracing=False`.
3. **No dispatch:** this is a code-ship, not an experiment. Status_log emit on landing per [[feedback-results-to-application-cadence-same-cycle]].

**For SECONDARY anchor (capacity-sweep smoke):**
1. **Cell-author phase:** extend smoke cell with M-loop. Output per-M arm-accuracies in metrics.json.
2. **Smoke gate (Fix #17 measurement strict):** sanity selftests still pass at each M.
3. **Pre-dispatch verify-the-referent (Fix #26):** run `tools/predispatch_check.py comparator_resonator_capacity_sweep_v1`; verify no prior dispatch.
4. **Dispatch via local_cpu_queue.**
5. **REMOTE VERIFY post-dispatch:** verify metrics.json contains per-M arm breakdowns.

**Pause-gate:** check `data/orchestrator_paused.flag` before dispatch. If paused, queue + surface; do NOT ship.

---

## Autonomy declaration

exp_dev owns:
- Primitive code-ship implementation details (within the API signature specified above)
- Whether to ship the SECONDARY capacity-sweep cell (defense-in-depth; not load-bearing — math is already validated)
- Whether to ship the TERTIARY conditional cell (only triggers on v3 HARD_FAIL)
- Cell-author smoke regime (M-sweep range; current spec is {50, 200, 500, 1000, 2000})
- Routing decision (local_cpu_queue for SECONDARY is the recommendation)

Research owns:
- Pre-reg bands (above; do not negotiate)
- HARD_PASS / HARD_FAIL / MIDDLE_BAND classification
- Verdict-handler routing on completion
- The diagnostic narrative (smoke-regime-too-easy + wrong-test-corpus; the comparator math is SOUND)

---

*Research (Director) hand-off complete 2026-06-23. The smoke HF1 is informative-negative: math validated; revival lives in v3 (already filed). PRIMARY action is the hdlab/ primitive lift; SECONDARY capacity-sweep is optional confidence-builder.*
