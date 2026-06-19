# Prereg: substrate_stdp_x_b2_sparse_sequence_storage_v1_n8192
## Anchor
substrate_stdp_x_b2_sparse_sequence_storage_v1_n8192
## Routing
overnight (I) P5: STDP-transition x B2 sparse sequence storage. Contrasts P4 (posbind x B2 = 1x). CPU numpy $0.
## Bands
HARD-PASS sparse>=5x dense. MIDDLE 2-5x. HARD-FAIL <2x. Smoke: 2.0x -> MIDDLE (sparse helps transitions, not bundles).
## Queue
remote_cpu_queue timeout 21600s (_n8192). PROT-022 PASS.
