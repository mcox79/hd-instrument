---
owner_verdict: DONE
---

SOLVED: the_register_bundle_renorm_breaks_the_serial_readout (SOLVER, opus 4.8)

The brief's suspect is confirmed and the fix is built. The situation register bundles superposed traces and rescales them by dividing each channel by its own magnitude (S_i/|S_i|, hdlab/bundling.py default) — a non-invertible per-component distortion that destroys the linear structure the theta-gamma serial readout needs. The brain instead controls a summed population's magnitude by pooled divisive normalization (Carandini & Heeger 2012) — one shared scalar over the pool — which preserves the linear structure exactly.

Result (D=256 FIXED, V=100, per-slot filler-recovery, bootstrap CI over entities). Swapping per-component renorm for a pooled/scalar divisive norm + a gain-matched serial readout: serial 0.325 → 1.000 @M=64, +0.675 CI-sep [+0.646,+0.703] hw0.028; ties the raw-sum ceiling at every load; argmax path improves 0.512→0.644 (no regression); info-free twin loses (0.029); parameter-flat (serial=1.000 across every C-H sigma and homeostatic target → it's the operation, not a tuned number). One normalization serves BOTH readouts — no raw-sum shadow copy needed (the brief's fidelity question, answered positively). Positive control: even the best gain-matched readout can't rescue the per-component store (isolates the STORE norm, not the readout). Measured on the DEFAULT backend in the compose regime (multibank, M=384/8 banks, k_per_bank≈60): serial 0.733→1.000 (+0.293), argmax 0.654→0.765 — the p2 store lever and this norm fix COMPOSE.

Research-verified (2 adversarial literature drills). Pooled divisive normalization is confirmed in sensory/decision cortex and extended by analogy to a memory register (labeled OUR-EXTENSION-UNDER-TEST, closest precedent Eliasmith near-unit-radius / Frady 2018) — NOT a recorded hippocampal fact. Per-component instantaneous magnitude-erasure has no fast biological analogue (Turrigiano scaling is slow/weight-level/structure-preserving). The M≥96 divergence is the brain's own working-memory → episodic boundary (normalize a bounded bundle vs sparse-pattern-separate a large one) — a positive architecture result, and the p2 lever, not a fidelity failure.

Files: experiments/exp_register_divisive_norm_v1.py, verification/test_register_divisive_norm.py (8/8 PASS), SOLVED.md, ADJACENT_COMPONENTS_brain_fidelity_map.md. Reverify: .venv/Scripts/python.exe verification/test_register_divisive_norm.py

Proposed hdlab diff (Q111 — you land it): add norm="divnorm" (pooled Carandini-Heeger) to bundling.bundle + a bundle_norm opt-in on AccumulateRegister/situation_model_multibank (default "percomp", so nothing changes until opted in) + the gain-matched decode_serial_pooled. Land the store option and the gain-matched readout together — the store option alone breaks any serial caller assuming raw scale.

AUDIT UPDATE (§2b): the flagged per-component bundle-renorm wall is RESOLVED (mechanism identified + built); the per-component-normaliser's correct scope narrows to re-bound atoms only; record the WM↔episodic subsystem boundary (this norm lever + the p2 sparse store = the two halves of CLS, they compose).

Adjacent tools flagged (mapped, ranked): every enumerated bundling.bundle caller is read-terminal → the per-component default is sub-optimal substrate-wide; the sign()-on-a-bundle sites are the same wrong-op (already audit-flagged with graded>sign measured); the cosine-readout consumers (lexical_similarity, quality_relation) need their own probe (distinct readout). Candidate follow-ons ranked in the map.
