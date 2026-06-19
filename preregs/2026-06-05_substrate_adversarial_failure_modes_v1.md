# Prereg: substrate_adversarial_failure_modes_v1
## Anchor
substrate_adversarial_failure_modes_v1
## Routing
HP-10 honest-limits: 4 adversarial failure modes (contradiction/OOD/overflow/adversarial-keys). Required for regulated-AI honesty. CPU $0.
## Bands
HARD-PASS all 4 predictable. MIDDLE 3/4. HARD-FAIL catastrophic mode.
Smoke: contradiction->latest 1.0, overflow graceful, OOD separable, BUT adversarial similar-key confusion 0.53 (>0.3 limit) -> MIDDLE (honest limit found).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
