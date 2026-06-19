# Prereg: substrate_max_for_reasoning_tasks_not_lm_v1
## Anchor
substrate_max_for_reasoning_tasks_not_lm_v1
## Routing
HP-4: substrate-MAX (cleanup-iterate) helps REASONING not LM. K-hop chain depth: plain vs cleanup; + LM no-op contrast. CPU $0.
## Bands
HARD-PASS cleanup K_max>=2x plain AND LM gain<0.05. MIDDLE ratio 1.3-2x. HARD-FAIL <1.3x.
Smoke: REASONING K_plain=0 K_cleanup=13.5 (13.5x); LM single=cleanup=0.912 (no-op) -> HARD_PASS. Reframes LM-negative.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
