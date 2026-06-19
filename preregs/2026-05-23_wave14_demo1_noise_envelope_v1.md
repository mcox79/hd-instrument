# Pre-registration: wave14_demo1_noise_envelope_v1

**Date**: 2026-05-23
**Queue**: overnight_queue (GPU required; N=65536)
**Axis probed**: Cap 1 (Demo 1 Lane D capstone) noise envelope — "4-primitive composition under noise"
**Trigger**: active_priorities.md Cap 1 next envelope axis; Strategy v161 substrate-product pipeline pacing; overnight_queue drained after pq_high_resolution FULL
**Script**: experiments/exp_wave14_demo1_noise_envelope_v1.py
**Peak VRAM**: ~260 MB (5 codebooks × 65536 × float32) — well under 8 GB
**Expected elapsed**: ~30-60 min at FULL (N=65536, 3 seeds, 5 noise levels × 40 trials each)

---

## Scientific question

Does the Cap 1 Demo 1 Lane D 4-primitive composition pipeline (Stage U EMA + Stage S VAMP-class + Stage T hypothesis tracking + Stage X skill decode) tolerate deployment-realistic observation noise at the demonstrated scale (N=65536)?

Cap 1 is ✅ FULL at clean observations (composed_acc=1.000, cycles 130+139). The next envelope axis is "4-primitive composition under noise" per active_priorities.md. This experiment characterizes the noise-tolerance boundary.

---

## Design

- **N**: 65536 (full scale at which Cap 1 was demonstrated)
- **Noise model**: independent bit-flip on each observation triple at rate p_flip before EMA accumulation. Same model as Cap 1 (Crooks-FT), Cap 3 (streaming NESS), Cap 5 (Online W).
- **Noise levels**: p in {0.0, 0.05, 0.10, 0.20, 0.30}
- **Trials per cell**: 40 (per seed) × 3 seeds = 120 total per noise level
- **Seeds**: [17, 23, 31]
- **Pipeline**: identical to exp_wave14_lane_D_end_to_end_N65536_vamp_v1.py with noise injection added at Stage U input

---

## Falsifiable predictions

### HARD PASS
- `composed_acc(p=0.10) >= 0.50` AND `composed_acc(p=0.00) >= 0.50`
- Verdict: `DEMO1_NOISE_ROBUST`

### HARD FAIL (either condition sufficient)
- `composed_acc(p=0.00) < 0.50` — regression from capstone FULL (Verdict: `DEMO1_NOISE_BROKEN`)
- `composed_acc(p=0.10) < 0.50` with clean >= 0.50 — noise brittle (Verdict: `DEMO1_NOISE_BRITTLE`)

### Pre-registered expectation
P(ROBUST) = 0.55 (moderate; Cap 1 at clean is 1.000, but composed accuracy can degrade quickly because all 4 stages must succeed simultaneously; each stage is independent so composed_acc degrades multiplicatively; at 10% flip each stage likely stays above 0.80 -> composed ~0.41; marginal case). P(BRITTLE) = 0.35. P(BROKEN) = 0.10.

---

## Memory budget audit

- entity_atoms: 200 × 65536 × 4 = 52.4 MB
- relation_atoms: 20 × 65536 × 4 = 5.2 MB
- hyp_atoms: 3 × 65536 × 4 = 0.8 MB
- position_atoms: 4 × 65536 × 4 = 1.0 MB
- skill_atoms: 5 × 65536 × 4 = 1.3 MB
- M_T joint matrix: 65536 × 4 = 0.3 MB
- B accumulator: 65536 × 4 = 0.3 MB
- sims vector: 200 × 4 = 0.8 KB
- Total peak: ~61 MB per trial on CUDA (all codebooks on device simultaneously)
- Well within 8 GB VRAM budget.

---

## Substrate-product positioning

If ROBUST: Cap 1 (Demo 1 Lane D) commercial envelope WIDENS to include moderate noise scenarios (realistic sensor noise, transmission errors). Product framing: "4-primitive cognitive pipeline survives up to 10% observation corruption."

If BRITTLE: Cap 1 envelope stays at clean observations; product note "pipeline requires clean input." Still ✅ FULL at clean.

If BROKEN: regression from capstone — very unlikely given the pipeline's physics at N=65536.

---

## PROT compliance

Not a closure; no PROT-004/006 required. PROT-001 (exp_dev_decisions log entry) paired.
