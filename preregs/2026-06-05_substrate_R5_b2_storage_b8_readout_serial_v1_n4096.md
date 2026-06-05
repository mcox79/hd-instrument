# Prereg: substrate_R5_b2_storage_b8_readout_serial_v1_n4096
## Anchor
substrate_R5_b2_storage_b8_readout_serial_v1_n4096
## Routing
R5 reframed (serial stack): B2 sparse-storage + B8 sparse-readout. Post-R6 question: does B2 storage corrupt B8 readout? CPU numpy $0.
## Bands
HARD-PASS M_crit(B2)>=1.5x dense AND B8 readout functional (corr-with-target r>=0.25). MIDDLE one. HARD-FAIL both fail.
Smoke: B2 M_crit 50x dense, b8_r=0.41 -> HARD_PASS (storage does NOT corrupt readout).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
