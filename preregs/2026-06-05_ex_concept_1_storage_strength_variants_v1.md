# Prereg: ex_concept_1_storage_strength_variants_v1
## Anchor
ex_concept_1_storage_strength_variants_v1
## Routing
substrate-MAX: attack introspection weak-storage barrier (retrieval_conf=0.01). Storage variants (multipass/highlr/count/hopfield) for next-concept. CPU $0.
## Bands
HARD-PASS best>=trigram AND conf>=5x. MIDDLE >=trigram OR conf>=2x. HARD-FAIL else.
Smoke: all storage variants=0.672 (accuracy unchanged; conf 2.9x) -> MIDDLE. Barrier is MODEL-ORDER (bigram) not storage strength.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
